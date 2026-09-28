// ettelem: power, temperature and voltage telemetry from an ET-SoC-1 card, through the management library.
//
//   ettelem sample [--seconds T] [--every-ms M] [--reset-ms R]
//                                                   JSON lines: board power, SP stats (rails), temperatures,
//                                                   regulator set-points, on-die voltages, clock frequencies.
//                                                   The SP's rail figures are [avg, min, max]: avg is the PMIC's
//                                                   own running average (roughly first-order, tau ~ 1 s); min and
//                                                   max run since the last stats reset. --reset-ms R resets the
//                                                   stats (and sends the PMIC its stats reset) every R ms and tags
//                                                   each sample with its window; whether that makes avg a window
//                                                   mean is untested.
//   ettelem config                                 static governor inputs: TDP (W), SW temperature
//                                                   threshold (C), power state, current minion clock and voltage
//   ettelem loglevel critical|error|warning|info|debug
//                                                   SP log level (DM_CMD_SET_DM_TRACE_CONFIG), trace_string_event 0-4
//                                                   (et-trace/include/et-trace/encoder.h:208-214). At debug the SP logs
//                                                   one line per shire per pass with its on-die voltages; at warning
//                                                   (the boot default) the ring keeps only CRITICAL, ERROR and WARNING
//                                                   lines, which include the governor's event lines.
//
// ettelem-hp (tools/claims-v3/hp/ettelem-hp/): a copy of tools/ettelem/ettelem.cpp whose only change is the loglevel
// argument. The original maps every word but "debug" to INFO (3), so "loglevel warning" set INFO; here each of the five
// words sets its own level and any other word is refused. Built into build/ettelem-hp/ only, never over build/ettelem.
//   ettelem sptrace <out.bin>                       raw SP trace buffer (the log strings)
//
// ettelem-dv2 (tools/claims-v3/dv2/ettelem-dv2/, DV2 DESIGN §9 T2): ettelem-hp plus four reads and one sampler option.
//   ettelem residency <raw state> [...]             DM_CMD_GET_MODULE_RESIDENCY_THROTTLE_STATES (29), one JSON line per
//                                                   state: {cumulative, average, maximum, minimum} in SP microseconds.
//                                                   The RAW firmware number is sent (0.20.0 and 0.18.0: 2 POWER_UP,
//                                                   3 POWER_DOWN, 4 THERMAL_DOWN, 5 POWER_SAFE, 6 THERMAL_SAFE; the host
//                                                   header's enum differs). Only 2-6 are accepted.
//   ettelem uptime                                  DM_CMD_GET_MODULE_UPTIME (30): {day, hours, mins} (minute resolution)
//   ettelem threshold get                           the software thermal threshold (DM 21), as config reads it
//   ettelem threshold set N                         NOT BUILT: refused always (DV2's D1 needs the owner's yes; no set
//                                                   path exists in this binary, so none can be taken by mistake)
//   ettelem sample ... --reset-once-file F          no statistics reset at start; ONE reset (the same request as
//                                                   --reset-ms) after the first sample read while F exists, never
//                                                   another. since_reset_ms is -1 before it and the time since it
//                                                   after; every line carries "resets" (0 or 1), the line after which
//                                                   the reset was sent carries "reset_rc". Excludes --reset-ms.
// There is no DM 36 marker and no set of any kind here besides loglevel.
//
// Everything here is a read, except loglevel, which only changes what the SP writes into its own log buffer, and the
// statistics reset, which restarts the SP's min/max windows (as every --reset-ms sampler of V3 and HP did).
// The management node allows one opener: quit et-powertop and scripts/et-power-log.sh first.
#include <csignal>
#include <device-layer/IDeviceLayer.h>
#include <deviceManagement/DeviceManagement.h>
#include <esperanto/device-apis/management-api/device_mgmt_api_rpc_types.h>
#include <esperanto/device-apis/management-api/device_mgmt_api_spec.h>

#include <dlfcn.h>
#include <unistd.h>
#include <chrono>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <fstream>
#include <string>
#include <thread>
#include <vector>

using namespace device_management;
using namespace device_mgmt_api;
using Clock = std::chrono::steady_clock;

namespace {

long long epochMs() {
  return std::chrono::duration_cast<std::chrono::milliseconds>(std::chrono::system_clock::now().time_since_epoch()).count();
}

struct Dm {
  std::shared_ptr<dev::IDeviceLayer> dl;
  DeviceManagement* dm = nullptr;
  Dm() {
    void* h = dlopen("libDM.so", RTLD_LAZY);
    if (!h) throw std::runtime_error(std::string("dlopen libDM.so: ") + dlerror());
    using getDM_t = DeviceManagement& (*)(dev::IDeviceLayer*);
    auto get = reinterpret_cast<getDM_t>(dlsym(h, "getInstance"));
    if (!get) throw std::runtime_error("no getInstance in libDM.so");
    dl = dev::IDeviceLayer::createPcieDeviceLayer(false, true);  // management node only
    dm = &get(dl.get());
  }
  // The service processor's per-rail figures are [avg, min, max]: avg is the PMIC's own running average (roughly
  // first-order, tau ~ 1 s), min and max run since the last reset. This resets the SP's stats and sends the PMIC its
  // stats reset (0x47); what that does to the running average is untested.
  bool resetStats() {
    const uint32_t in[2] = {1u /* SP stats */, 2u /* STATS_CONTROL_RESET_COUNTER */};
    char out[8] = {0};
    uint32_t hl = 0;
    uint64_t dlat = 0;
    return dm->serviceRequest(0, DM_CMD_SET_STATS_RUN_CONTROL, reinterpret_cast<const char*>(in), sizeof(in), out, 1,
                              &hl, &dlat, 2000) == 0;
  }
  template <class T> bool get(uint32_t cmd, T& out) {
    uint32_t hl = 0;
    uint64_t dlat = 0;
    std::memset(&out, 0, sizeof(out));
    return dm->serviceRequest(0, cmd, nullptr, 0, reinterpret_cast<char*>(&out), sizeof(out), &hl, &dlat, 2000) == 0;
  }
  // a read with a one-byte input (the residency state), as devicemanagement/tests/TestDevMgmtApiSyncCmds.cpp sends it
  template <class T> int getWith1(uint32_t cmd, uint8_t arg, T& out) {
    uint32_t hl = 0;
    uint64_t dlat = 0;
    std::memset(&out, 0, sizeof(out));
    const char in[1] = {static_cast<char>(arg)};
    return dm->serviceRequest(0, cmd, in, 1, reinterpret_cast<char*>(&out), sizeof(out), &hl, &dlat, 2000);
  }
};

// DV2 Z2: throttle residency by raw firmware state (2-6 only), one JSON line each
int residency(Dm& d, const std::vector<int>& states) {
  int bad = 0;
  for (int s : states) {
    residency_t r{};
    const int rc = d.getWith1(DM_CMD_GET_MODULE_RESIDENCY_THROTTLE_STATES, static_cast<uint8_t>(s), r);
    std::printf("{\"t_ms\":%lld,\"state\":%d,\"rc\":%d", epochMs(), s, rc);
    if (rc == 0)
      std::printf(",\"cumulative_us\":%llu,\"average_us\":%llu,\"maximum_us\":%llu,\"minimum_us\":%llu",
                  (unsigned long long)r.cumulative, (unsigned long long)r.average, (unsigned long long)r.maximum,
                  (unsigned long long)r.minimum);
    std::printf("}\n");
    std::fflush(stdout);
    if (rc != 0) bad = 1;
  }
  return bad;
}

int uptime(Dm& d) {
  module_uptime_t u{};
  const bool ok = d.get(DM_CMD_GET_MODULE_UPTIME, u);
  std::printf("{\"t_ms\":%lld,\"rc\":%d", epochMs(), ok ? 0 : 1);
  if (ok) std::printf(",\"day\":%u,\"hours\":%u,\"mins\":%u", (unsigned)u.day, (unsigned)u.hours, (unsigned)u.mins);
  std::printf("}\n");
  return ok ? 0 : 1;
}

int thresholdGet(Dm& d) {
  struct U8 { uint8_t v; uint8_t pad[7]; } thr{};
  const bool ok = d.get(DM_CMD_GET_MODULE_TEMPERATURE_THRESHOLDS, thr);
  std::printf("{\"t_ms\":%lld,\"temp_threshold_c\":%s}\n", epochMs(), ok ? std::to_string(thr.v).c_str() : "null");
  return ok ? 0 : 1;
}

int bin2mv(int reg, int base, int mul, int div) { return base + reg * mul / div; }

// The static configuration the service processor's governor compares against: the static TDP in watts, the
// software temperature threshold, and the current power state. check_power_throttle_conditions() in
// ServiceProcessorBL2/services/thermal_pwr_mgmt.c throttles down whenever measured SoC power exceeds the TDP
// and steps up only when it is below, so these three numbers decide whether a card can ever leave its boot
// clock. All three are reads.
int config(Dm& d) {
  struct U8 { uint8_t v; uint8_t pad[7]; } tdp{}, thr{}, st{};
  asic_frequencies_t f{};
  asic_voltage_t av{};
  const bool okD = d.get(DM_CMD_GET_MODULE_STATIC_TDP_LEVEL, tdp),
             okT = d.get(DM_CMD_GET_MODULE_TEMPERATURE_THRESHOLDS, thr),
             okS = d.get(DM_CMD_GET_MODULE_POWER_STATE, st), okF = d.get(DM_CMD_GET_ASIC_FREQUENCIES, f),
             okV = d.get(DM_CMD_GET_ASIC_VOLTAGE, av);
  static const char* names[] = {"max_power", "managed_power", "safe_power", "low_power", "invalid"};
  std::printf("{\"tdp_w\":%s,\"temp_threshold_c\":%s,\"power_state\":%s,\"power_state_name\":\"%s\"",
              okD ? std::to_string(tdp.v).c_str() : "null", okT ? std::to_string(thr.v).c_str() : "null",
              okS ? std::to_string(st.v).c_str() : "null", okS && st.v < 5 ? names[st.v] : "?");
  if (okF) std::printf(",\"minion_mhz\":%u", (unsigned)f.minion_shire_mhz);
  if (okV) std::printf(",\"minion_mv\":%u", (unsigned)av.minion);
  std::printf("}\n");
  return (okD && okT && okS) ? 0 : 1;
}

// A sampler killed in the middle of a request leaves that request's reply in the management queue, and the next
// process to open the node receives it with no handler registered and dies of std::bad_function_call; so does every
// retry, each leaving its own reply behind (24 Sep 2026: both cards). So SIGTERM and SIGINT only ask the loop to
// stop, and the sample in flight completes. A queue already poisoned is drained by one call of the vendor tool:
//   dev_mngt_service -m DM_CMD_GET_MODULE_POWER -n 0 -u 5000   (it crashes on the stale reply and clears it)
static volatile std::sig_atomic_t g_stop = 0;
static void onStop(int) { g_stop = 1; }

int sample(Dm& d, double seconds, int everyMs, int resetMs, const std::string& resetOnceFile) {
  struct sigaction sa {};
  sa.sa_handler = onStop;
  sa.sa_flags = SA_RESTART;   // the device layer's blocking calls resume instead of failing with EINTR
  sigemptyset(&sa.sa_mask);
  sigaction(SIGTERM, &sa, nullptr);
  sigaction(SIGINT, &sa, nullptr);
  const auto t0 = Clock::now();
  auto lastReset = Clock::now();
  if (resetMs > 0) d.resetStats();
  int resetsDone = 0;  // --reset-once-file: 0 until the one reset, then 1 for good
  while (!g_stop && std::chrono::duration<double>(Clock::now() - t0).count() < seconds) {
    const auto tick = Clock::now();
    module_power_t p;
    get_sp_stats_t s;
    current_temperature_t t;
    asic_voltage_t av;
    module_voltage_t mv;
    asic_frequencies_t f;
    const long long ms = epochMs();
    // With --reset-ms, the rail minima and maxima in this sample cover the window since the last reset (whether the
    // PMIC's running average restarts with it is untested); the sample carries that window's length.
    long long sinceResetMs = -1;
    if (resetMs > 0 || resetsDone > 0) {
      sinceResetMs = std::chrono::duration_cast<std::chrono::milliseconds>(tick - lastReset).count();
    }
    const bool okP = d.get(DM_CMD_GET_MODULE_POWER, p), okS = d.get(DM_CMD_GET_SP_STATS, s),
               okT = d.get(DM_CMD_GET_MODULE_CURRENT_TEMPERATURE, t), okA = d.get(DM_CMD_GET_ASIC_VOLTAGE, av),
               okM = d.get(DM_CMD_GET_MODULE_VOLTAGE, mv), okF = d.get(DM_CMD_GET_ASIC_FREQUENCIES, f);
    std::printf("{\"t_ms\":%lld,\"took_ms\":%lld,\"since_reset_ms\":%lld", ms, epochMs() - ms, sinceResetMs);
    if (!resetOnceFile.empty()) std::printf(",\"resets\":%d", resetsDone);
    if (okP) std::printf(",\"board_w\":%.2f", p.power / 100.0);
    // Reset after reading, so this sample closed the window and the next one opens a fresh one.
    if (resetMs > 0 && sinceResetMs >= resetMs) {
      d.resetStats();
      lastReset = Clock::now();
    }
    // The one-shot reset: once, after this sample was read, if the file exists (DV2 DESIGN §5.1 step 3)
    if (!resetOnceFile.empty() && resetsDone == 0 && ::access(resetOnceFile.c_str(), F_OK) == 0) {
      const bool okR = d.resetStats();
      lastReset = Clock::now();
      resetsDone = 1;
      std::printf(",\"reset_rc\":%d", okR ? 0 : 1);
    }
    if (okS)
      std::printf(",\"sp\":{\"board_avg_w\":%.2f,\"board_min_w\":%.2f,\"board_max_w\":%.2f,"
                  "\"minion_w\":[%.3f,%.3f,%.3f],\"sram_w\":[%.3f,%.3f,%.3f],\"noc_w\":[%.3f,%.3f,%.3f],"
                  "\"minion_mv\":[%u,%u,%u],\"sram_mv\":[%u,%u,%u],\"noc_mv\":[%u,%u,%u],"
                  "\"minion_c\":[%u,%u,%u],\"system_c\":[%u,%u,%u],\"minion_mhz\":[%u,%u,%u],\"noc_mhz\":[%u,%u,%u]}",
                  s.system_power_avg / 100.0, s.system_power_min / 100.0, s.system_power_max / 100.0,
                  s.minion_power_avg / 1000.0, s.minion_power_min / 1000.0, s.minion_power_max / 1000.0,
                  s.sram_power_avg / 1000.0, s.sram_power_min / 1000.0, s.sram_power_max / 1000.0,
                  s.noc_power_avg / 1000.0, s.noc_power_min / 1000.0, s.noc_power_max / 1000.0, s.minion_voltage_avg,
                  s.minion_voltage_min, s.minion_voltage_max, s.sram_voltage_avg, s.sram_voltage_min,
                  s.sram_voltage_max, s.noc_voltage_avg, s.noc_voltage_min, s.noc_voltage_max, s.minion_temperature_avg,
                  s.minion_temperature_min, s.minion_temperature_max, s.system_temperature_avg,
                  s.system_temperature_min, s.system_temperature_max, s.minion_freq_avg, s.minion_freq_min,
                  s.minion_freq_max, s.noc_freq_avg, s.noc_freq_min, s.noc_freq_max);
    if (okT)
      std::printf(",\"temp_c\":{\"pmic\":%u,\"ioshire\":[%d,%d,%d],\"minshire\":[%d,%d,%d]}", t.pmic_sys, t.ioshire_current,
                  t.ioshire_low, t.ioshire_high, t.minshire_avg, t.minshire_low, t.minshire_high);
    if (okA)  // on-die voltage monitors (PVT), mV
      std::printf(",\"die_mv\":{\"ddr\":%u,\"sram\":%u,\"maxion\":%u,\"minion\":%u,\"pshire\":%u,\"noc\":%u,\"ioshire\":%u}",
                  av.ddr, av.l2_cache, av.maxion, av.minion, av.pshire_0p75, av.noc, av.ioshire_0p75);
    if (okM)  // regulator set-points as the PMIC reports them, mV
      std::printf(",\"reg_mv\":{\"ddr\":%d,\"sram\":%d,\"maxion\":%d,\"minion\":%d,\"noc\":%d,\"pcie_logic\":%d,\"vddq\":%d,\"vddqlp\":%d}",
                  bin2mv(mv.ddr, 250, 5, 1), bin2mv(mv.l2_cache, 250, 5, 1), bin2mv(mv.maxion, 250, 5, 1),
                  bin2mv(mv.minion, 250, 5, 1), bin2mv(mv.noc, 250, 5, 1), bin2mv(mv.pcie_logic, 600, 625, 100),
                  bin2mv(mv.vddq, 250, 10, 1), bin2mv(mv.vddqlp, 250, 10, 1));
    if (okF) std::printf(",\"mhz\":{\"minion\":%u,\"noc\":%u,\"ddr\":%u}", f.minion_shire_mhz, f.noc_mhz, f.ddr_mhz);
    std::printf("}\n");
    std::fflush(stdout);
    std::this_thread::sleep_until(tick + std::chrono::milliseconds(everyMs));
  }
  return 0;
}

}  // namespace

int main(int argc, char** argv) {
  if (argc < 2 || !std::strcmp(argv[1], "--help")) {
    std::fprintf(stderr, "usage: ettelem sample [--seconds T] [--every-ms M] [--reset-ms R | --reset-once-file F] | config"
                         " | loglevel critical|error|warning|info|debug | sptrace <out.bin> | residency <2-6>... | uptime"
                         " | threshold get\n");
    return argc < 2 ? 2 : 0;
  }
  const std::string cmd = argv[1];
  // Every argument is checked before the management node is opened (a typo never touches the card).
  if (cmd == "threshold") {
    if (argc == 3 && !std::strcmp(argv[2], "get")) {
      // fall through to the device below
    } else if (argc >= 3 && !std::strcmp(argv[2], "set")) {
      std::fprintf(stderr, "threshold set: refused: not built into this binary (DV2 D1 needs the owner's explicit yes;"
                           " DESIGN §4.3)\n");
      return 2;
    } else {
      std::fprintf(stderr, "threshold: expected get\n");
      return 2;
    }
  }
  std::vector<int> states;
  if (cmd == "residency") {
    for (int i = 2; i < argc; ++i) {
      char* e = nullptr;
      const long v = std::strtol(argv[i], &e, 10);
      if (!e || *e || v < 2 || v > 6) {
        std::fprintf(stderr, "residency: raw states 2-6 only (got '%s')\n", argv[i]);
        return 2;
      }
      states.push_back(static_cast<int>(v));
    }
    if (states.empty()) {
      std::fprintf(stderr, "residency: give one or more raw states 2-6\n");
      return 2;
    }
  }
  if (cmd == "uptime" && argc != 2) {
    std::fprintf(stderr, "uptime: no arguments\n");
    return 2;
  }
  double seconds = 10;
  int everyMs = 100, resetMs = 0;
  std::string resetOnceFile;
  if (cmd == "sample") {
    for (int i = 2; i < argc; i += 2) {
      if (i + 1 >= argc) {
        std::fprintf(stderr, "sample: %s needs a value\n", argv[i]);
        return 2;
      }
      if (!std::strcmp(argv[i], "--seconds")) seconds = std::atof(argv[i + 1]);
      else if (!std::strcmp(argv[i], "--every-ms")) everyMs = std::atoi(argv[i + 1]);
      else if (!std::strcmp(argv[i], "--reset-ms")) resetMs = std::atoi(argv[i + 1]);
      else if (!std::strcmp(argv[i], "--reset-once-file")) resetOnceFile = argv[i + 1];
      else {
        std::fprintf(stderr, "sample: unknown option %s\n", argv[i]);
        return 2;
      }
    }
    if (resetMs > 0 && !resetOnceFile.empty()) {
      std::fprintf(stderr, "sample: --reset-ms and --reset-once-file exclude each other\n");
      return 2;
    }
    if (everyMs < 50) {
      std::fprintf(stderr, "sample: --every-ms >= 50\n");
      return 2;
    }
  }
  // loglevel: the word is checked before the management node is opened (a typo never touches the card)
  int loglevelWord = -1;
  if (cmd == "loglevel") {
    static const char* words[] = {"critical", "error", "warning", "info", "debug"};  // trace_string_event 0-4
    for (int i = 0; argc == 3 && i < 5; ++i) {
      if (!std::strcmp(argv[2], words[i])) loglevelWord = i;
    }
    if (loglevelWord < 0) {
      std::fprintf(stderr, "loglevel: expected critical|error|warning|info|debug\n");
      return 2;
    }
  }
  try {
    Dm d;
    if (cmd == "sample") return sample(d, seconds, everyMs, resetMs, resetOnceFile);
    if (cmd == "config") return config(d);
    if (cmd == "residency") return residency(d, states);
    if (cmd == "uptime") return uptime(d);
    if (cmd == "threshold") return thresholdGet(d);
    if (cmd == "loglevel" && argc == 3) {
      // trace_string_event: CRITICAL 0, ERROR 1, WARNING 2, INFO 3, DEBUG 4 (encoder.h:208-214)
      const uint32_t level = static_cast<uint32_t>(loglevelWord);
      const uint32_t in[2] = {1u /* TRACE_EVENT_STRING */, level};
      char out[8] = {0};
      uint32_t hl = 0;
      uint64_t dlat = 0;
      const int rc = d.dm->serviceRequest(0, DM_CMD_SET_DM_TRACE_CONFIG, reinterpret_cast<const char*>(in), sizeof(in), out,
                                          1, &hl, &dlat, 2000);
      std::printf("loglevel %s: rc %d status %d\n", argv[2], rc, out[0]);
      return rc;
    }
    if (cmd == "sptrace" && argc == 3) {
      std::vector<std::byte> buf;
      const int rc = d.dm->getTraceBufferServiceProcessor(0, TraceBufferType::TraceBufferSP, buf);
      std::ofstream(argv[2], std::ios::binary).write(reinterpret_cast<const char*>(buf.data()), (std::streamsize)buf.size());
      std::printf("sptrace: rc %d, %zu bytes\n", rc, buf.size());
      return rc;
    }
  } catch (const std::exception& e) {
    std::fprintf(stderr, "FAIL: %s\n", e.what());
    return 1;
  }
  std::fprintf(stderr, "bad arguments\n");
  return 2;
}
