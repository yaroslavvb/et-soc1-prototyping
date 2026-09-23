// ettelem: power, temperature and voltage telemetry from an ET-SoC-1 card, through the management library.
//
//   ettelem sample [--seconds T] [--every-ms M] [--reset-ms R]
//                                                   JSON lines: board power, SP stats (rails), temperatures,
//                                                   regulator set-points, on-die voltages, clock frequencies.
//                                                   The SP's rail figures are [avg, min, max] SINCE THEIR LAST
//                                                   RESET; with --reset-ms R they are reset every R ms and each
//                                                   sample says how long its window has been open.
//   ettelem config                                 static governor inputs: flashed TDP (W), SW temperature
//                                                   threshold (C), power state, current minion clock and voltage
//   ettelem loglevel debug|info                     SP log level (DM_CMD_SET_DM_TRACE_CONFIG). At debug the SP logs one
//                                                   line per shire per pass with its on-die voltages (current/low/high).
//   ettelem sptrace <out.bin>                       raw SP trace buffer (the log strings)
//
// Everything here is a read, except loglevel, which only changes what the SP writes into its own log buffer.
// The management node allows one opener: quit et-powertop and scripts/et-power-log.sh first.
#include <device-layer/IDeviceLayer.h>
#include <deviceManagement/DeviceManagement.h>
#include <esperanto/device-apis/management-api/device_mgmt_api_rpc_types.h>
#include <esperanto/device-apis/management-api/device_mgmt_api_spec.h>

#include <dlfcn.h>
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
  // The service processor's per-rail figures are averages, minima and maxima SINCE THEIR LAST RESET, not
  // instantaneous power. Reset them and the average from then on is the mean over the window that follows.
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
};

int bin2mv(int reg, int base, int mul, int div) { return base + reg * mul / div; }

// The static configuration the service processor's governor compares against: the flashed TDP in watts, the
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

int sample(Dm& d, double seconds, int everyMs, int resetMs) {
  const auto t0 = Clock::now();
  auto lastReset = Clock::now();
  if (resetMs > 0) d.resetStats();
  while (std::chrono::duration<double>(Clock::now() - t0).count() < seconds) {
    const auto tick = Clock::now();
    module_power_t p;
    get_sp_stats_t s;
    current_temperature_t t;
    asic_voltage_t av;
    module_voltage_t mv;
    asic_frequencies_t f;
    const long long ms = epochMs();
    // With --reset-ms, the rail averages in this sample cover the window since the last reset; the sample
    // carries that window's length so the reader can pick the one that closes each window.
    long long sinceResetMs = -1;
    if (resetMs > 0) {
      sinceResetMs = std::chrono::duration_cast<std::chrono::milliseconds>(tick - lastReset).count();
    }
    const bool okP = d.get(DM_CMD_GET_MODULE_POWER, p), okS = d.get(DM_CMD_GET_SP_STATS, s),
               okT = d.get(DM_CMD_GET_MODULE_CURRENT_TEMPERATURE, t), okA = d.get(DM_CMD_GET_ASIC_VOLTAGE, av),
               okM = d.get(DM_CMD_GET_MODULE_VOLTAGE, mv), okF = d.get(DM_CMD_GET_ASIC_FREQUENCIES, f);
    std::printf("{\"t_ms\":%lld,\"took_ms\":%lld,\"since_reset_ms\":%lld", ms, epochMs() - ms, sinceResetMs);
    if (okP) std::printf(",\"board_w\":%.2f", p.power / 100.0);
    // Reset after reading, so this sample closed the window and the next one opens a fresh one.
    if (resetMs > 0 && sinceResetMs >= resetMs) {
      d.resetStats();
      lastReset = Clock::now();
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
  if (argc < 2) {
    std::fprintf(stderr, "usage: ettelem sample [--seconds T] [--every-ms M] | loglevel debug|info | sptrace <out.bin>\n");
    return 2;
  }
  const std::string cmd = argv[1];
  try {
    Dm d;
    if (cmd == "sample") {
      double seconds = 10;
      int everyMs = 100, resetMs = 0;
      for (int i = 2; i + 1 < argc; i += 2) {
        if (!std::strcmp(argv[i], "--seconds")) seconds = std::atof(argv[i + 1]);
        if (!std::strcmp(argv[i], "--every-ms")) everyMs = std::atoi(argv[i + 1]);
        if (!std::strcmp(argv[i], "--reset-ms")) resetMs = std::atoi(argv[i + 1]);
      }
      return sample(d, seconds, everyMs, resetMs);
    }
    if (cmd == "config") return config(d);
    if (cmd == "loglevel" && argc == 3) {
      const uint32_t level = !std::strcmp(argv[2], "debug") ? 4 : 3;  // trace_string_event: INFO 3, DEBUG 4
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
