// ettelem-e77: E77's telemetry, the NO-PMIC-READ profile (Q133, Sun 1 Nov 2026).
//
// A copy of tools/claims-v3/dv2/ettelem-dv2/ettelem.cpp with every request that reaches the card's PMIC REMOVED, so no
// call of this binary can send one. At et-platform 836a4ab (BL2 0.22.0, the build aifoundry2 reports):
//   * DM_CMD_GET_ASIC_VOLTAGE reads the on-die PVT monitors AND two PMIC voltage registers (VDDQLP, VDDQ):
//     services/thermal_pwr_mgmt.c:1212-1216 -> pmic_get_voltage -> get_pmic_reg (driver/pmic_controller.c:1473-1500).
//     The stock sampler sent it with every sample and `config` with every call. REMOVED: die_mv and config's minion_mv
//     are gone.
//   * DM_CMD_GET_MODULE_VOLTAGE makes nine PMIC register reads (thermal_pwr_mgmt.c:1010-1120). The stock sampler sent it
//     with every sample. REMOVED: reg_mv is gone.
//   * DM_CMD_SET_STATS_RUN_CONTROL (the statistics reset, --reset-ms / --reset-once-file) is forwarded to the PMIC
//     (E85 C1). REMOVED.
//   * DM_CMD_SET_DM_TRACE_CONFIG (loglevel) is a set. REMOVED.
// What is left, and what each request touches on the card (the same source):
//   sample    DM_CMD_GET_MODULE_POWER (get_module_soc_power, a RAM copy, thermal_pwr_mgmt.c:984-988), DM_CMD_GET_SP_STATS
//             (RAM, services/performance.c:420-466: the rails E77 reads, sp.minion_w / sram_w / noc_w and sp.minion_mv,
//             which the service processor keeps from its own periodic reads), DM_CMD_GET_MODULE_CURRENT_TEMPERATURE (on-die
//             PVT, thermal_pwr_mgmt.c:732-773), DM_CMD_GET_ASIC_FREQUENCIES (PLL registers, services/perf_mgmt.c:276-)
//   config    DM_CMD_GET_MODULE_STATIC_TDP_LEVEL and DM_CMD_GET_MODULE_TEMPERATURE_THRESHOLDS (the two RAM GETs that read
//             the governor's two fields, thermal_pwr_mgmt.c:143-144), DM_CMD_GET_MODULE_POWER_STATE (RAM),
//             DM_CMD_GET_ASIC_FREQUENCIES (PLL)
//   uptime    DM_CMD_GET_MODULE_UPTIME (RAM, thermal_pwr_mgmt.c:1451-1455)
//   residency DM_CMD_GET_MODULE_RESIDENCY_THROTTLE_STATES (RAM)
//   sptrace   no DM command: two driver ioctls (ETSOC1_IOCTL_GET_TRACE_BUFFER_SIZE, ETSOC1_IOCTL_EXTRACT_TRACE_BUFFER), a copy
//             of the service processor's trace region by MMIO (et-driver/et-soc1-pcie.c:719-720, 1021-)
//   profile   prints this list; opens nothing
// There is no set of any kind in this binary. The management node allows one opener.
//
// Build into its own directory, never over another ettelem:
//   cmake -S tools/claims-v3/e77/ettelem-e77 -B build/ettelem-e77 -DCMAKE_PREFIX_PATH=/opt/et -Wno-dev \
//     && nice cmake --build build/ettelem-e77 -j2
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
  // Only these five reads can be sent (allowed() below); anything else is refused before it is built.
  static bool allowed(uint32_t cmd) {
    return cmd == DM_CMD_GET_MODULE_POWER || cmd == DM_CMD_GET_SP_STATS || cmd == DM_CMD_GET_MODULE_CURRENT_TEMPERATURE ||
           cmd == DM_CMD_GET_ASIC_FREQUENCIES || cmd == DM_CMD_GET_MODULE_STATIC_TDP_LEVEL ||
           cmd == DM_CMD_GET_MODULE_TEMPERATURE_THRESHOLDS || cmd == DM_CMD_GET_MODULE_POWER_STATE ||
           cmd == DM_CMD_GET_MODULE_UPTIME;
  }
  template <class T> bool get(uint32_t cmd, T& out) {
    std::memset(&out, 0, sizeof(out));
    if (!allowed(cmd)) return false;
    uint32_t hl = 0;
    uint64_t dlat = 0;
    return dm->serviceRequest(0, cmd, nullptr, 0, reinterpret_cast<char*>(&out), sizeof(out), &hl, &dlat, 2000) == 0;
  }
  // a read with a one-byte input (the residency state), as devicemanagement/tests/TestDevMgmtApiSyncCmds.cpp sends it
  template <class T> int residencyGet(uint8_t arg, T& out) {
    uint32_t hl = 0;
    uint64_t dlat = 0;
    std::memset(&out, 0, sizeof(out));
    const char in[1] = {static_cast<char>(arg)};
    return dm->serviceRequest(0, DM_CMD_GET_MODULE_RESIDENCY_THROTTLE_STATES, in, 1, reinterpret_cast<char*>(&out),
                              sizeof(out), &hl, &dlat, 2000);
  }
};

int profile() {
  std::printf("{\"binary\":\"ettelem-e77\",\"profile\":\"no-PMIC-read\",\"requests\":[\"DM_CMD_GET_MODULE_POWER\","
              "\"DM_CMD_GET_SP_STATS\",\"DM_CMD_GET_MODULE_CURRENT_TEMPERATURE\",\"DM_CMD_GET_ASIC_FREQUENCIES\","
              "\"DM_CMD_GET_MODULE_STATIC_TDP_LEVEL\",\"DM_CMD_GET_MODULE_TEMPERATURE_THRESHOLDS\","
              "\"DM_CMD_GET_MODULE_POWER_STATE\",\"DM_CMD_GET_MODULE_UPTIME\","
              "\"DM_CMD_GET_MODULE_RESIDENCY_THROTTLE_STATES\",\"ioctl:GET_TRACE_BUFFER_SIZE\","
              "\"ioctl:EXTRACT_TRACE_BUFFER\"],\"removed\":[\"DM_CMD_GET_ASIC_VOLTAGE\",\"DM_CMD_GET_MODULE_VOLTAGE\","
              "\"DM_CMD_SET_STATS_RUN_CONTROL\",\"DM_CMD_SET_DM_TRACE_CONFIG\"]}\n");
  return 0;
}

int residency(Dm& d, const std::vector<int>& states) {
  int bad = 0;
  for (int s : states) {
    residency_t r{};
    const int rc = d.residencyGet(static_cast<uint8_t>(s), r);
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

// The governor's two fields by their own GETs, the power state, and the clock. No voltage: that read reaches the PMIC.
int config(Dm& d) {
  struct U8 { uint8_t v; uint8_t pad[7]; } tdp{}, thr{}, st{};
  asic_frequencies_t f{};
  const bool okD = d.get(DM_CMD_GET_MODULE_STATIC_TDP_LEVEL, tdp),
             okT = d.get(DM_CMD_GET_MODULE_TEMPERATURE_THRESHOLDS, thr),
             okS = d.get(DM_CMD_GET_MODULE_POWER_STATE, st), okF = d.get(DM_CMD_GET_ASIC_FREQUENCIES, f);
  static const char* names[] = {"max_power", "managed_power", "safe_power", "low_power", "invalid"};
  std::printf("{\"t_ms\":%lld,\"tdp_w\":%s,\"temp_threshold_c\":%s,\"power_state\":%s,\"power_state_name\":\"%s\"",
              epochMs(), okD ? std::to_string(tdp.v).c_str() : "null", okT ? std::to_string(thr.v).c_str() : "null",
              okS ? std::to_string(st.v).c_str() : "null", okS && st.v < 5 ? names[st.v] : "?");
  if (okF) std::printf(",\"minion_mhz\":%u", (unsigned)f.minion_shire_mhz);
  std::printf(",\"profile\":\"no-PMIC-read\"}\n");
  return (okD && okT && okS) ? 0 : 1;
}

// A sampler killed in the middle of a request leaves that request's reply in the management queue (24 Sep 2026), so
// SIGTERM and SIGINT only ask the loop to stop, and the sample in flight completes.
static volatile std::sig_atomic_t g_stop = 0;
static void onStop(int) { g_stop = 1; }

int sample(Dm& d, double seconds, int everyMs) {
  struct sigaction sa {};
  sa.sa_handler = onStop;
  sa.sa_flags = SA_RESTART;
  sigemptyset(&sa.sa_mask);
  sigaction(SIGTERM, &sa, nullptr);
  sigaction(SIGINT, &sa, nullptr);
  const auto t0 = Clock::now();
  while (!g_stop && std::chrono::duration<double>(Clock::now() - t0).count() < seconds) {
    const auto tick = Clock::now();
    module_power_t p;
    get_sp_stats_t s;
    current_temperature_t t;
    asic_frequencies_t f;
    const long long ms = epochMs();
    const bool okP = d.get(DM_CMD_GET_MODULE_POWER, p), okS = d.get(DM_CMD_GET_SP_STATS, s),
               okT = d.get(DM_CMD_GET_MODULE_CURRENT_TEMPERATURE, t), okF = d.get(DM_CMD_GET_ASIC_FREQUENCIES, f);
    std::printf("{\"t_ms\":%lld,\"took_ms\":%lld,\"since_reset_ms\":-1", ms, epochMs() - ms);
    if (okP) std::printf(",\"board_w\":%.2f", p.power / 100.0);
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
    if (okF) std::printf(",\"mhz\":{\"minion\":%u,\"noc\":%u,\"ddr\":%u}", f.minion_shire_mhz, f.noc_mhz, f.ddr_mhz);
    std::printf(",\"profile\":\"no-PMIC-read\"}\n");
    std::fflush(stdout);
    std::this_thread::sleep_until(tick + std::chrono::milliseconds(everyMs));
  }
  return 0;
}

}  // namespace

int main(int argc, char** argv) {
  if (argc < 2 || !std::strcmp(argv[1], "--help")) {
    std::fprintf(stderr, "usage: ettelem-e77 sample [--seconds T] [--every-ms M] | config | uptime | residency <2-6>... |"
                         " sptrace <out.bin> | profile\n");
    return argc < 2 ? 2 : 0;
  }
  const std::string cmd = argv[1];
  if (cmd == "profile") return profile();
  // Every argument is checked before the management node is opened (a typo never touches the card).
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
  } else if ((cmd == "uptime" || cmd == "config") && argc != 2) {
    std::fprintf(stderr, "%s: no arguments\n", cmd.c_str());
    return 2;
  } else if (cmd == "sptrace" && argc != 3) {
    std::fprintf(stderr, "sptrace: one output file\n");
    return 2;
  } else if (cmd != "sample" && cmd != "uptime" && cmd != "config" && cmd != "sptrace") {
    std::fprintf(stderr, "unknown command %s (this binary has no set and no PMIC read)\n", cmd.c_str());
    return 2;
  }
  double seconds = 10;
  int everyMs = 100;
  if (cmd == "sample") {
    for (int i = 2; i < argc; i += 2) {
      if (i + 1 >= argc) {
        std::fprintf(stderr, "sample: %s needs a value\n", argv[i]);
        return 2;
      }
      if (!std::strcmp(argv[i], "--seconds")) seconds = std::atof(argv[i + 1]);
      else if (!std::strcmp(argv[i], "--every-ms")) everyMs = std::atoi(argv[i + 1]);
      else {
        std::fprintf(stderr, "sample: unknown option %s (no statistics reset in this binary)\n", argv[i]);
        return 2;
      }
    }
    if (everyMs < 50) {
      std::fprintf(stderr, "sample: --every-ms >= 50\n");
      return 2;
    }
  }
  try {
    Dm d;
    if (cmd == "sample") return sample(d, seconds, everyMs);
    if (cmd == "config") return config(d);
    if (cmd == "residency") return residency(d, states);
    if (cmd == "uptime") return uptime(d);
    if (cmd == "sptrace") {
      std::vector<std::byte> buf;
      const int rc = d.dm->getTraceBufferServiceProcessor(0, TraceBufferType::TraceBufferSP, buf);  // as ettelem-dv2
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
