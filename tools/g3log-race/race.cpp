// Reproduces aifoundry3's host crash mechanism without a card: several threads make the first g3::logLevel() call for
// a custom level at once, as libetrt's thread-pool workers do with VLOG_MID when nothing registered it.
// Usage: race <trials> <threads> [register]   ("register" adds the level first, as logging::LoggerDefault does)
#include <g3log/loglevels.hpp>
#include <atomic>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <thread>
#include <vector>
static const LEVELS VLOG_MID{g3::kDebugValue - 99, {"VERBOSE_MID"}};
int main(int argc, char** argv) {
  int trials = std::atoi(argv[1]), nth = std::atoi(argv[2]);
  bool reg = argc > 3 && !std::strcmp(argv[3], "register");
  std::atomic<int> gen{0}, done{0};
  std::vector<std::thread> th;
  for (int t = 0; t < nth; ++t)
    th.emplace_back([&] {
      for (int g = 1; g <= trials; ++g) {
        while (gen.load(std::memory_order_acquire) < g) {}
        (void)g3::logLevel(VLOG_MID);
        done.fetch_add(1, std::memory_order_acq_rel);
      }
    });
  size_t expect = 0; long bad = 0;
  for (int g = 1; g <= trials; ++g) {
    g3::only_change_at_initialization::reset();
    if (reg) g3::only_change_at_initialization::addLogLevel(VLOG_MID, false);
    if (g == 1) expect = g3::log_levels::getAll().size() + (reg ? 0 : 1);
    done.store(0); gen.store(g, std::memory_order_release);
    while (done.load(std::memory_order_acquire) < nth) {}
    if (g3::log_levels::getAll().size() != expect) ++bad;
  }
  for (auto& t : th) t.join();
  std::printf("%s: %d trials x %d threads, %ld with a corrupted level map (expected %zu levels)\n",
              reg ? "registered first" : "unregistered", trials, nth, bad, expect);
  return 0;
}
