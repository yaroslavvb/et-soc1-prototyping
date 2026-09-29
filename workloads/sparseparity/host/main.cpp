// sparseparity_host: the noisy sparse-parity correlation scan on the ET-SoC-1 (see ../sparseparity_args.h and
// docs/research/sparse-parity/DESIGN.md). One process: build or load an instance, build the work list, open the
// device, copy in, launch, read the per-hart records back after every launch, close the device, then check
// everything on the CPU and print one JSON line on stdout (progress goes to stderr).
//
//   sparseparity_host [--sysemu [--sim-args "-vpurf_warn ..."]]
//       instance:  --n N --k K --eta E --m M --seed S   (spbits' generator; default C0 = 32 3 0.1 128 1)
//                  | --instance FILE (SPI1) [--save-instance FILE]
//       mode:      --mode tensor|scalar [--two-hart] [--dump] [--nowait-a]
//       work list: --shires MASK --per-shire P [--rounds R] [--slice I/N]
//                  | --plan FILE: M0's binary work list (tools/planner.py plan; its shire mask and minions per shire
//                    replace --shires and --per-shire), or text lines "shire minion tile0 ntiles"
//                  | --probe narrow:N: N consecutive one-column-tile row tiles per minion (the hand-off race probe:
//                    hart 0 consumes every tile right after hart 1 publishes it; run it with --oracle on)
//                  [--perturb drop|dup|mask]   (negative controls: the checksums must fail)
//       staging:   --nbuf auto|1|2 --stage auto|scp|dram   (auto: scratchpad with 2 buffers, else scratchpad with
//                  1, else DRAM with 2) [--scp-kb KB] (the scratchpad per shire the layout may use; default 2560,
//                  and the device's own size is read after opening: a layout past it is refused)
//       limits:    --reps R --budget SECONDS --max-kernel-s SECONDS --poll-limit N
//       checks:    --oracle auto|on|sample|off [--oracle-work U]   (the per-minion CPU oracle, below)
//       output:    --records-out FILE --dump-out FILE
//                  --out FILE: M0's output file (tensor mode), for tools/sptest.py card and tools/planner.py merge.
//                    The kernel keeps no top list: plan with --topm 0, or the comparison flags the empty lists
//       --verify-records FILE   no device: load a --records-out file of an earlier run with the same arguments
//                  and run every check on it, with the full oracle (the offline value check of a large run)
//       --dry      plan and model only: print the JSON line and exit without opening any device
//       --timing-only  tensor mode without the epilogue: cycles per op alone (no scores; status TIMING)
//       M4 (tensor mode; tools/cycle_model.py's analysis of the 29 September card runs):
//                  --variant m4|m1   m4 (default): the kernel's incremental row generation and its epilogue in pieces
//                                    (SPP_F_GEN_INC | SPP_F_EPI_HIDE) and the plan balanced by the fitted pipeline
//                                    model; m1: the M1 kernel and M1's planner, exactly as run on 29 September
//                  --gen m1|inc  --epi m1|hide  --abuf 2|3  --cost m1|fit  --slice-cost m1|fit
//                                    one change at a time, over the variant's defaults (--abuf 3: SPP_F_ABUF3, streamed
//                                    A only; --slice-cost: the cost --slice I/N cuts by, default --cost's; an A/B passes
//                                    --slice-cost m1 so that every configuration scans the same tiles)
//                  --pipe-set K=V,..  override the fitted model's constants (a recalibration; spp_common.h PipeConst)
//                  --gen-probe nostore  (with --timing-only, --gen inc) hart 1 expands every row but stores it in its
//                                    own L1: the staged stores' share of the generation time
//       The modelled kernel time (model_s) is the fitted model's prediction for the kernel that runs, whatever the
//       plan was balanced by; est_s adds a margin (x1.15 for M1's kernel, which the fit reproduces within 8%; x1.3
//       once an M4 change is on, which only the card can check). The --max-kernel-s guard (guard_s) is the largest
//       of est_s, M1's own model and, while an M4 change runs on predicted constants (no --pipe-set), the same plan
//       simulated with M1's fitted constants x1.15 (model_fallback_s: what the launch takes if the M4 changes gain
//       nothing; review of M4, finding 1).
//                  --trust-model  guard on est_s alone, not on model_fallback_s: only once a launch of the same
//                                    kernel has run within x1.3 of its model (card_run.sh m4 gates it so)
//
// Value checks. The count, the ops and the rescoring of the best come from every run. The two closed-form checksums
// apply when the plan covers all C(n,k) candidates. The oracle rescores whole minions on the CPU and compares each
// hart-0 record field by field: `on` every minion; `auto` every minion if that fits the time left, else a random
// sample (seeded by the launch's epoch) that fits; `sample` a sample of about --oracle-work cost units (default
// 1e9: about a second); `off` none, which on silicon is refused unless the closed forms apply and --nowait-a is off.
//
// Card etiquette. The device is held only between opening the runtime and tearing it down; the instance, the plan
// and every check run with it closed. On silicon: the host refuses a work list whose modelled kernel time is over
// --max-kernel-s (default 4 s); it launches only while the launch's timeout still ends by --budget (default 9 s,
// counted from the process's start, at most 9.5 s); each launch's timeout is min(8, 2 x the model + 1.5 s, the time
// left); after a timed-out launch it aborts the stream and reads nothing back; the harts give up waiting for each
// other well inside the timeout. Run it as `flock -n /run/lock/etsoc-shire<N>.lock timeout 10 sparseparity_host ...`.
#include <g3log/loglevels.hpp>
#include <runtime/IRuntime.h>
#include <runtime/Types.h>
#include <device-layer/IDeviceLayer.h>
#include <sw-sysemu/SysEmuOptions.h>

#include <algorithm>
#include <chrono>
#include <cmath>
#include <cstdint>
#include <cstdlib>
#include <cstring>
#include <filesystem>
#include <fstream>
#include <iostream>
#include <limits>
#include <random>
#include <sstream>
#include <string>
#include <vector>

#include "Constants.h"
#include "cpu/sp.h"  // M0's formats: the work list (sp_wl_*) and the output file (sp_out_hdr_t, sp_rec_t, sp_top_t)
#include "spp_common.h"

using namespace spp;

// libetrt's thread-pool workers log at the custom levels VERBOSE_HIGH/MID/LOW, which only logging::LoggerDefault
// registers with g3log; registering them first removes the race behind aifoundry3's 1.08 s host crash
// (docs/findings/14-card-behaviour.md, "Traps").
static void registerRuntimeLogLevels() {
  const LEVELS levels[] = {LEVELS(g3::kDebugValue - 100, "VERBOSE_HIGH"), LEVELS(g3::kDebugValue - 99, "VERBOSE_MID"),
                           LEVELS(g3::kDebugValue - 98, "VERBOSE_LOW")};
  for (const auto& l : levels) g3::only_change_at_initialization::addLogLevel(l, false);
}

namespace fs = std::filesystem;
using Clock = std::chrono::steady_clock;
static double secondsSince(Clock::time_point t0) { return std::chrono::duration<double>(Clock::now() - t0).count(); }

// The single-thread oracle's cost, used to fit it into the time left: (S + 12) units per scored entry (S popcounts
// plus the entry's own work), at 1.45e9 units per second measured with -mpopcnt on aifoundry3's i7-11700K
// (spp_selftest --bench-oracle, 29 September: 1.03e9 words/s at S = 29, 2.8e8 at S = 3); 8e8 leaves a margin.
static constexpr double kOracleUnitsPerS = 8e8;
static constexpr double kDeadlineMax = 9.5;     // the host's own cap under `timeout 10`
static constexpr double kChecksDeadline = 9.7;  // on silicon the in-process checks stop here (sampled oracle)

static std::vector<std::byte> readFile(const std::string& path) {
  std::ifstream file(path, std::ios::binary);
  if (!file) return {};
  std::vector<std::byte> data(fs::file_size(path));
  file.read(reinterpret_cast<char*>(data.data()), static_cast<std::streamsize>(data.size()));
  return data;
}

static std::unique_ptr<dev::IDeviceLayer> makeDeviceLayer(bool sysemu, const std::string& simArgs) {
  if (!sysemu) return dev::IDeviceLayer::createPcieDeviceLayer(true, true);
  emu::SysEmuOptions o;
  o.bootromTrampolineToBL2ElfPath = BOOTROM_TRAMPOLINE_TO_BL2_ELF;
  o.spBL2ElfPath = BL2_ELF;
  o.masterMinionElfPath = MASTER_MINION_ELF;
  o.machineMinionElfPath = MACHINE_MINION_ELF;
  o.workerMinionElfPath = WORKER_MINION_ELF;
  o.executablePath = fs::path(SYSEMU_INSTALL_DIR) / "sys_emu";
  o.runDir = fs::current_path();
  o.maxCycles = std::numeric_limits<uint64_t>::max();
  o.minionShiresMask = 0x1FFFFFFFFu;
  o.puUart0Path = o.runDir + "/pu_uart0_tx.log";
  o.puUart1Path = o.runDir + "/pu_uart1_tx.log";
  o.spUart0Path = o.runDir + "/spio_uart0_tx.log";
  o.spUart1Path = o.runDir + "/spio_uart1_tx.log";
  o.startGdb = false;
  std::istringstream extra(simArgs);
  for (std::string arg; extra >> arg;) o.additionalOptions.push_back(arg);
  return dev::IDeviceLayer::createSysEmuDeviceLayer(o, 1);
}

struct Opts {
  bool sysemu = false;
  std::string simArgs;
  int n = 32, k = 3, m = 128;
  double eta = 0.1;
  uint64_t seed = 1;
  std::string instPath, saveInst;
  std::string mode = "tensor";
  bool dump = false, twoHart = false, nowaitA = false;
  uint64_t shires = 0x1;
  int perShire = 1, rounds = 4;
  std::string planPath, perturb;
  int probeTiles = 0;
  int sliceI = 0, sliceN = 1;
  int nbuf = 0;  // 0 = auto
  std::string stage = "auto";
  uint64_t scpKB = 2560;
  int reps = 1;
  double budget = -1, maxKernelS = 4.0;
  uint64_t pollLimit = 0;
  std::string oracle = "auto";
  double oracleWork = 1e9;
  std::string kernel = KERNEL_ELF;
  std::string recordsOut, dumpOut, outPath, verifyRecords;
  bool dry = false, timingOnly = false;
  // M4
  std::string variant = "m4", gen, epi, cost, sliceCost, pipeSet, genProbe;
  int abuf = 0;
  bool genInc = true, epiHide = true, costFit = true, sliceFit = true;
  bool trustModel = false;
};

[[noreturn]] static void usage(const char* argv0, const std::string& why = "") {
  if (!why.empty()) std::cerr << argv0 << ": " << why << "\n";
  std::cerr << "usage: " << argv0
            << " [--sysemu [--sim-args ARGS]] [--n N --k K --eta E --m M --seed S | --instance FILE]"
               " [--save-instance FILE] [--mode tensor|scalar] [--two-hart] [--dump] [--nowait-a]"
               " [--shires MASK] [--per-shire P] [--rounds R] [--slice I/N] [--plan FILE] [--probe narrow:N]"
               " [--perturb drop|dup|mask] [--nbuf auto|1|2] [--stage auto|scp|dram] [--scp-kb KB] [--reps R]"
               " [--budget S] [--max-kernel-s S] [--poll-limit N] [--oracle auto|on|sample|off] [--oracle-work W]"
               " [--kernel ELF] [--records-out FILE] [--dump-out FILE] [--out FILE] [--verify-records FILE] [--dry]"
               " [--timing-only] [--variant m4|m1] [--gen m1|inc] [--epi m1|hide] [--abuf 2|3] [--cost m1|fit]"
               " [--slice-cost m1|fit] [--pipe-set K=V,..] [--gen-probe nostore] [--trust-model]\n";
  std::exit(2);
}

static Opts parse(int argc, char** argv) {
  Opts o;
  for (int i = 1; i < argc; ++i) {
    const std::string a = argv[i];
    auto next = [&]() -> std::string {
      if (i + 1 >= argc) usage(argv[0], a + " needs a value");
      return argv[++i];
    };
    if (a == "--sysemu") o.sysemu = true;
    else if (a == "--sim-args") o.simArgs = next();
    else if (a == "--n") o.n = std::stoi(next());
    else if (a == "--k") o.k = std::stoi(next());
    else if (a == "--eta") o.eta = std::stod(next());
    else if (a == "--m") o.m = std::stoi(next());
    else if (a == "--seed") o.seed = std::stoull(next(), nullptr, 0);
    else if (a == "--instance") o.instPath = next();
    else if (a == "--save-instance") o.saveInst = next();
    else if (a == "--mode") o.mode = next();
    else if (a == "--two-hart") o.twoHart = true;
    else if (a == "--dump") o.dump = true;
    else if (a == "--nowait-a") o.nowaitA = true;
    else if (a == "--shires") o.shires = std::stoull(next(), nullptr, 0);
    else if (a == "--per-shire") o.perShire = std::stoi(next());
    else if (a == "--rounds") o.rounds = std::stoi(next());
    else if (a == "--plan") o.planPath = next();
    else if (a == "--perturb") o.perturb = next();
    else if (a == "--probe") {
      const std::string s = next();
      if (s.rfind("narrow:", 0) != 0) usage(argv[0], "--probe narrow:N");
      o.probeTiles = std::stoi(s.substr(7));
    } else if (a == "--slice") {
      const std::string s = next();
      const auto slash = s.find('/');
      if (slash == std::string::npos) usage(argv[0], "--slice I/N");
      o.sliceI = std::stoi(s.substr(0, slash));
      o.sliceN = std::stoi(s.substr(slash + 1));
    } else if (a == "--nbuf") {
      const std::string s = next();
      o.nbuf = s == "auto" ? 0 : std::stoi(s);
    } else if (a == "--stage") o.stage = next();
    else if (a == "--scp-kb") o.scpKB = std::stoull(next());
    else if (a == "--reps") o.reps = std::max(1, std::stoi(next()));
    else if (a == "--budget") o.budget = std::stod(next());
    else if (a == "--max-kernel-s") o.maxKernelS = std::stod(next());
    else if (a == "--poll-limit") o.pollLimit = std::stoull(next());
    else if (a == "--oracle") o.oracle = next();
    else if (a == "--oracle-work") o.oracleWork = std::stod(next());
    else if (a == "--kernel") o.kernel = next();
    else if (a == "--records-out") o.recordsOut = next();
    else if (a == "--dump-out") o.dumpOut = next();
    else if (a == "--out") o.outPath = next();
    else if (a == "--verify-records") o.verifyRecords = next();
    else if (a == "--dry") o.dry = true;
    else if (a == "--timing-only") o.timingOnly = true;
    else if (a == "--variant") o.variant = next();
    else if (a == "--gen") o.gen = next();
    else if (a == "--epi") o.epi = next();
    else if (a == "--abuf") o.abuf = std::stoi(next());
    else if (a == "--cost") o.cost = next();
    else if (a == "--slice-cost") o.sliceCost = next();
    else if (a == "--pipe-set") o.pipeSet = next();
    else if (a == "--gen-probe") o.genProbe = next();
    else if (a == "--trust-model") o.trustModel = true;
    else usage(argv[0], "unknown option " + a);
  }
  if (o.variant != "m4" && o.variant != "m1") usage(argv[0], "--variant m4|m1");
  const bool m4 = o.variant == "m4";
  if (!o.gen.empty() && o.gen != "m1" && o.gen != "inc") usage(argv[0], "--gen m1|inc");
  if (!o.epi.empty() && o.epi != "m1" && o.epi != "hide") usage(argv[0], "--epi m1|hide");
  if (!o.cost.empty() && o.cost != "m1" && o.cost != "fit") usage(argv[0], "--cost m1|fit");
  if (!o.sliceCost.empty() && o.sliceCost != "m1" && o.sliceCost != "fit") usage(argv[0], "--slice-cost m1|fit");
  if (o.abuf != 0 && o.abuf != 2 && o.abuf != 3) usage(argv[0], "--abuf 2|3");
  if (!o.genProbe.empty() && o.genProbe != "nostore") usage(argv[0], "--gen-probe nostore");
  o.genInc = o.gen.empty() ? m4 : o.gen == "inc";
  o.epiHide = o.epi.empty() ? m4 : o.epi == "hide";
  o.costFit = o.cost.empty() ? m4 : o.cost == "fit";
  o.sliceFit = o.sliceCost.empty() ? o.costFit : o.sliceCost == "fit";
  if (o.abuf == 0) o.abuf = 2;
  if (o.abuf == 3 && o.nowaitA) usage(argv[0], "--abuf 3 excludes --nowait-a");
  if (!o.genProbe.empty() && (!o.timingOnly || !o.genInc)) usage(argv[0], "--gen-probe needs --timing-only and --gen inc");
  if (o.mode != "tensor" && o.mode != "scalar") usage(argv[0], "--mode tensor|scalar");
  if (o.timingOnly && (o.mode != "tensor" || o.dump || !o.perturb.empty())) usage(argv[0], "--timing-only: tensor, no dump, no perturb");
  if (!o.outPath.empty() && o.mode != "tensor") usage(argv[0], "--out needs tensor mode");
  if (o.nbuf != 0 && o.nbuf != 1 && o.nbuf != 2) usage(argv[0], "--nbuf auto|1|2");
  if (o.sliceN < 1 || o.sliceI < 0 || o.sliceI >= o.sliceN) usage(argv[0], "--slice I/N with 0 <= I < N");
  if (!o.perturb.empty() && o.perturb != "drop" && o.perturb != "dup" && o.perturb != "mask") usage(argv[0], "--perturb drop|dup|mask");
  if (o.perturb == "mask" && o.mode != "tensor") usage(argv[0], "--perturb mask is a tensor-mode control");
  if (o.stage != "auto" && o.stage != "scp" && o.stage != "dram") usage(argv[0], "--stage auto|scp|dram");
  if (o.oracle != "auto" && o.oracle != "on" && o.oracle != "sample" && o.oracle != "off") usage(argv[0], "--oracle auto|on|sample|off");
  if (o.perShire < 1 || o.perShire > 32 || (o.shires & ~0xFFFFFFFFull) || !o.shires) usage(argv[0], "--shires / --per-shire out of range");
  if (o.probeTiles < 0 || (o.probeTiles && (!o.planPath.empty() || o.sliceN > 1))) usage(argv[0], "--probe excludes --plan and --slice");
  if (o.scpKB < 512 || o.scpKB > 4096) usage(argv[0], "--scp-kb 512..4096");
  if (o.budget < 0) o.budget = o.sysemu ? 1e9 : 9.0;  // the simulator is private; a real card is shared
  if (!o.sysemu && o.budget > kDeadlineMax) usage(argv[0], "--budget is at most 9.5 s on a card (the run is under timeout 10)");
  return o;
}

// sliceRange (host-side slices, cut by position) is in spp_common.h.

// The race probe: N consecutive row tiles with one column tile each (the last run, J0 = nJ - 1) per active minion,
// disjoint across minions; the run before it is used when the last one is too short.
static Plan probePlan(const Geometry& G, uint64_t shireMask, int perShire, int N) {
  Plan plan;
  plan.shireMask = shireMask;
  plan.perShire = perShire;
  const std::vector<int> act = plan.activeSlots();
  const uint64_t need = uint64_t(N) * act.size();
  if (need > G.workTiles) throw std::runtime_error("--probe: " + std::to_string(need) + " tiles needed, the instance has " + std::to_string(G.workTiles));
  const uint64_t base = G.workTiles - need;  // the narrowest tiles are last in colex order
  for (size_t i = 0; i < act.size(); ++i) plan.slots[act[i]].push_back({base + i * uint64_t(N), uint64_t(N)});
  return plan;
}

// M0's binary work list (cpu/sp.h section 6). Logical minion q = shire_index * mps + minion_in_shire, with
// shire_index the rank of the physical shire among the mask's set bits. Fills the plan (physical slots) and
// logical[q] = slot. Two-stage lists are refused: M1 has no survivor log.
struct M0Plan {
  sp_wl_hdr_t hdr{};
  std::vector<int> logical;  // q -> physical slot shire * 32 + minion
};

static bool isM0Plan(const std::string& path) {
  std::ifstream f(path, std::ios::binary);
  uint32_t magic = 0;
  f.read(reinterpret_cast<char*>(&magic), 4);
  return f && magic == SP_WL_MAGIC;
}

static Plan readM0Plan(const std::string& path, const Geometry& G, M0Plan& m0) {
  std::ifstream f(path, std::ios::binary);
  sp_wl_hdr_t& h = m0.hdr;
  f.read(reinterpret_cast<char*>(&h), sizeof h);
  if (!f || h.magic != SP_WL_MAGIC || h.version != SP_WL_VERSION) throw std::runtime_error(path + ": not an SPWL v1 work list");
  if (int(h.n) != G.n || int(h.k) != G.k || int(h.m) != G.m || int(h.S) != G.S)
    throw std::runtime_error(path + ": the work list is for another (n, k, m, S)");
  if (h.flags & SP_WL_TWOSTAGE) throw std::runtime_error(path + ": two-stage work lists need the survivor log (M3/M4)");
  if (h.NT != G.ntiles) throw std::runtime_error(path + ": the work list has " + std::to_string(h.NT) + " row tiles, the host " + std::to_string(G.ntiles));
  std::vector<int> shires;
  for (int s = 0; s < 32; ++s)
    if ((h.shire_mask >> s) & 1) shires.push_back(s);
  if (h.shire_mask >> 32 || shires.size() != h.nshires || h.mps < 1 || h.mps > 32 || h.nminions != h.nshires * h.mps)
    throw std::runtime_error(path + ": shire mask, shires and minions per shire disagree");
  std::vector<sp_wl_minion_t> mins(h.nminions);
  std::vector<sp_wl_range_t> rg(h.nranges);
  f.read(reinterpret_cast<char*>(mins.data()), std::streamsize(mins.size() * sizeof(sp_wl_minion_t)));
  f.read(reinterpret_cast<char*>(rg.data()), std::streamsize(rg.size() * sizeof(sp_wl_range_t)));
  if (!f) throw std::runtime_error(path + ": truncated");
  Plan plan;
  plan.shireMask = h.shire_mask;
  plan.perShire = int(h.mps);
  m0.logical.assign(h.nminions, -1);
  for (uint32_t q = 0; q < h.nminions; ++q) {
    const sp_wl_minion_t& mi = mins[q];
    if (mi.shire >= h.nshires || mi.minion >= h.mps || mi.first_range + uint64_t(mi.nranges) > h.nranges)
      throw std::runtime_error(path + ": minion entry out of range");
    const int slot = shires[mi.shire] * 32 + int(mi.minion);
    m0.logical[q] = slot;
    for (uint32_t i = 0; i < mi.nranges; ++i) {
      const sp_wl_range_t& r = rg[mi.first_range + i];
      if (r.tile_end <= r.tile_begin || r.tile_end > G.ntiles || r.tile_end - r.tile_begin > 0xFFFFFFFFull)
        throw std::runtime_error(path + ": range out of range");
      plan.slots[slot].push_back({r.tile_begin, r.tile_end - r.tile_begin});
    }
  }
  return plan;
}

static bool recTie(const SppRecord& r) { return (r.status & SPP_INFO_TIE) != 0; }

// M0's output file: header, then records (index q * 2 + hart), then q * topm empty top entries (the kernel keeps
// the best only). Hart 0 holds the scores and tensor ops; hart 1 the row tiles generated.
static void writeM0Out(const std::string& path, const Instance& I, const Geometry& G, const M0Plan* m0,
                       const Plan& plan, const std::vector<SppRecord>& records, uint32_t epoch) {
  std::vector<int> logical;
  uint32_t topm = 0;
  uint64_t nranges = 0, totalOps = 0, totalCands = 0;
  if (m0) {
    logical = m0->logical;
    topm = m0->hdr.topm;
    nranges = m0->hdr.nranges;
    totalOps = m0->hdr.total_ops;
    totalCands = m0->hdr.total_cands;
  } else {
    logical = plan.activeSlots();
    for (int g : logical) {
      nranges += plan.slots[g].size();
      totalOps += countOps(G, plan.slots[g]);
      totalCands += countCandidates(G, plan.slots[g]);
    }
  }
  std::ofstream f(path, std::ios::binary);
  if (!f) throw std::runtime_error("cannot write " + path);
  sp_out_hdr_t oh{};
  oh.magic = SP_OUT_MAGIC;
  oh.version = 1;
  oh.nminions = uint32_t(logical.size());
  oh.harts = 2;
  oh.topm = topm;
  oh.n = uint32_t(I.n);
  oh.k = uint32_t(I.k);
  oh.m = uint32_t(I.m);
  oh.nranges = nranges;
  oh.total_ops = totalOps;
  oh.total_cands = totalCands;
  f.write(reinterpret_cast<const char*>(&oh), sizeof oh);
  for (uint32_t q = 0; q < logical.size(); ++q) {
    const int g = logical[q];
    for (int th = 0; th < 2; ++th) {
      const SppRecord& r = records[size_t(2 * g + th)];
      const bool valid = (r.status >> 16) == (epoch & 0xFFFF);
      const bool err = !valid || (r.status & SPP_STATUS_BAD) != 0;
      sp_rec_t o{};
      o.magic = SP_REC_MAGIC;
      o.hart = uint16_t(th);
      o.minion = q;
      o.best_c = INT32_MIN;
      if (th == 0) {
        const bool has = r.count > 0 && r.best_c != INT32_MIN && r.best_rank < G.ncand;
        if (has) {
          const std::vector<int> T = unrank(r.best_rank, I.k);
          o.best_c = r.best_c;
          o.best_j = uint32_t(T.back());
          o.best_row = r.best_rank - binom64(T.back(), I.k);
        }
        o.flags = uint16_t((valid ? SP_REC_VALID : 0) | (has ? SP_REC_HAS_BEST : 0) | (err ? SP_REC_ERROR : 0) |
                           (has && recTie(r) ? SP_REC_TIE : 0));
        o.ops = r.work;
        o.sum_c = r.sum_c;
        o.sum_c2 = r.sum_c2;
        o.cands = r.count;
        o.cycles = r.cycles;
      } else {
        o.flags = uint16_t((valid ? SP_REC_VALID : 0) | (err ? SP_REC_ERROR : 0));
        o.ops = uint32_t(r.count);  // row tiles generated
      }
      f.write(reinterpret_cast<const char*>(&o), sizeof o);
    }
  }
  for (uint64_t i = 0; i < uint64_t(logical.size()) * topm; ++i) {
    sp_top_t e{};
    e.c = INT32_MIN;
    f.write(reinterpret_cast<const char*>(&e), sizeof e);
  }
}

struct JsonOut {
  std::ostringstream s;
  bool first = true;
  void key(const std::string& k) {
    s << (first ? "" : ",") << "\"" << k << "\":";
    first = false;
  }
  template <class T> void kv(const std::string& k, const T& v) {
    key(k);
    s << v;
  }
  void ks(const std::string& k, const std::string& v) {
    key(k);
    s << "\"" << v << "\"";
  }
  void raw(const std::string& k, const std::string& v) {
    key(k);
    s << v;
  }
};

template <class T> static std::string jarr(const std::vector<T>& v) {
  std::ostringstream s;
  s << "[";
  for (size_t i = 0; i < v.size(); ++i) s << (i ? "," : "") << v[i];
  s << "]";
  return s.str();
}

static std::string hex(uint64_t v) {
  std::ostringstream s;
  s << "0x" << std::hex << v;
  return s.str();
}

static const char* tf(bool b) { return b ? "true" : "false"; }

// A hart-0 record (plus hart 1's in two-hart scalar mode) as an Acc.
static Acc accOf(const std::vector<SppRecord>& records, int g, bool withHart1) {
  Acc a;
  for (int th = 0; th < (withHart1 ? 2 : 1); ++th) {
    const SppRecord& r = records[size_t(2 * g + th)];
    Acc b;
    b.sum = r.sum_c;
    b.sq = r.sum_c2;
    b.count = r.count;
    b.best = r.best_c;
    b.bestRank = r.best_rank;
    b.tie = recTie(r);
    if (th == 0) a = b;
    else a.merge(b);
  }
  return a;
}

int main(int argc, char** argv) {
  registerRuntimeLogLevels();  // first, before any library starts a thread
  const auto tProc = Clock::now();
  Opts o = parse(argc, argv);
  const bool verify = !o.verifyRecords.empty();

  // ---------------------------------------------------------------- instance, geometry, plan (no device)
  Instance I;
  try {
    I = o.instPath.empty() ? generate(o.n, o.k, o.eta, o.m, o.seed) : loadInstance(o.instPath);
    if (!o.saveInst.empty()) saveInstance(o.saveInst, I);
  } catch (const std::exception& e) {
    std::cerr << "instance: " << e.what() << "\n";
    return 2;
  }
  const Geometry G(I);
  if (G.ntiles >= (1ull << 32)) {  // SppBlock.tile0 and the per-minion counts are 32-bit (review R1, finding 14)
    std::cerr << "refused: " << G.ntiles << " row tiles; the kernel's work list indexes at most 2^32\n";
    return 2;
  }
  const bool tensor = o.mode == "tensor";
  uint64_t t0 = 0, t1 = G.workTiles;
  Plan plan;
  M0Plan m0;
  bool fromM0 = false;
  bool fullCoverage = false;
  std::string planSource = "built-in";
  const bool filePlan = !o.planPath.empty() || o.probeTiles;
  try {
    if (filePlan) {
      if (o.probeTiles) {
        plan = probePlan(G, o.shires, o.perShire, o.probeTiles);
        planSource = "probe narrow:" + std::to_string(o.probeTiles);
      } else if ((fromM0 = isM0Plan(o.planPath))) {
        plan = readM0Plan(o.planPath, G, m0);
        o.shires = plan.shireMask;
        o.perShire = plan.perShire;
        o.sliceI = int(m0.hdr.slice);
        o.sliceN = int(m0.hdr.nslices);
        planSource = "m0:" + o.planPath;
      } else {
        plan = readPlan(o.planPath, o.shires, o.perShire, G);
        planSource = "text:" + o.planPath;
      }
      std::vector<uint32_t> seen(G.workTiles, 0);
      bool ok = true;
      for (int g : plan.activeSlots())
        for (const Block& b : plan.slots[g])
          for (uint64_t t = b.tile0; t < b.tile0 + b.ntiles; ++t) {
            if (t < G.workTiles) ++seen[t];
          }
      for (uint32_t v : seen) ok &= v == 1;
      fullCoverage = ok;
      t0 = ~0ull;
      t1 = 0;
      for (int g : plan.activeSlots())
        for (const Block& b : plan.slots[g]) {
          t0 = std::min(t0, b.tile0);
          t1 = std::max(t1, b.tile0 + b.ntiles);
        }
      if (t1 == 0) t0 = 0;
    }
  } catch (const std::exception& e) {
    std::cerr << "plan: " << e.what() << "\n";
    return 2;
  }

  // Scratchpad layout (tensor): X_B at 256 KB, then the staging buffers of minions 0..P-1 (or staging in DRAM).
  // auto: the scratchpad with 2 buffers, else with 1, else DRAM with 2 (review R1, finding 5). Decided before the
  // built-in plan, whose fitted costs depend on the buffers.
  const uint64_t scpBytes = o.scpKB * 1024;
  const uint64_t xbBytes = uint64_t(G.nJ) * G.S * SPP_TILE_BYTES;
  const uint64_t stageBytes = 16ull * G.S * 64;
  const uint64_t stageOff = SPP_SCP_MIN_OFFSET + xbBytes;
  bool stageScp = false;
  int nbuf = o.nbuf ? o.nbuf : 2;
  uint64_t layoutEnd = stageOff;
  if (tensor) {
    if (SPP_SCP_MIN_OFFSET + xbBytes > scpBytes) {
      std::cerr << "refused: X_B (" << xbBytes << " B) does not fit a shire's scratchpad (n * m too large; the"
                << " column-sharded layout is not written yet)\n";
      return 2;
    }
    auto fits = [&](int nb) { return stageOff + uint64_t(o.perShire) * nb * stageBytes <= scpBytes; };
    if (o.stage == "dram") {
      stageScp = false;
    } else if (o.nbuf) {
      stageScp = fits(o.nbuf);
    } else if (fits(2)) {
      stageScp = true, nbuf = 2;
    } else if (fits(1)) {
      stageScp = true, nbuf = 1;
    } else {
      stageScp = false, nbuf = 2;
    }
    if (o.stage == "scp" && !stageScp) {
      std::cerr << "refused: staging with " << nbuf << " buffer(s) per minion does not fit the scratchpad ("
                << o.scpKB << " KB); use --stage dram or --nbuf 1\n";
      return 2;
    }
    if (stageScp) layoutEnd = stageOff + uint64_t(o.perShire) * nbuf * stageBytes;
  }
  const uint64_t stride = uint64_t(nbuf) * stageBytes;

  // The fitted pipeline model of the kernel that runs (M4 changes as flags), and the costs the plan is cut by.
  const bool m1Kernel = !(tensor && (o.genInc || o.epiHide || o.abuf == 3));
  PipeConst pipe = pipeVariant(tensor && o.genInc, tensor && o.epiHide, tensor && o.abuf == 3 && G.S > 3);
  {
    std::string bad;
    if (!pipeSet(pipe, o.pipeSet, bad)) {
      std::cerr << "--pipe-set: unknown or malformed '" << bad << "'\n";
      return 2;
    }
  }
  const int epiOn = o.timingOnly ? 0 : 1;
  TileCost fitCost;
  try {
    if (tensor && (o.costFit || o.sliceFit)) fitCost = pipeTileCost(G, pipe, nbuf, !stageScp, pipePlanU(o.perShire), epiOn);
  } catch (const std::exception& e) {
    std::cerr << "model: " << e.what() << "\n";
    return 2;
  }
  const TileCost planCost = tensor && o.costFit ? fitCost : TileCost{};
  if (!filePlan) {
    try {
      sliceRange(G, o.sliceI, o.sliceN, t0, t1, tensor && o.sliceFit ? fitCost : TileCost{});
      plan = makePlan(G, o.shires, o.perShire, o.rounds, t0, t1, planCost);
      fullCoverage = o.sliceN == 1;
    } catch (const std::exception& e) {
      std::cerr << "plan: " << e.what() << "\n";
      return 2;
    }
  }
  const std::vector<int> slots = plan.activeSlots();
  int perturbSlot = -1;
  if (!o.perturb.empty()) {  // negative controls: drop one tile, scan one twice, or shift one staircase mask
    for (int g : slots)
      if (!plan.slots[g].empty()) {
        perturbSlot = g;
        break;
      }
    if (perturbSlot >= 0) {
      auto& bl = plan.slots[perturbSlot];
      if (o.perturb == "drop") {
        if (--bl.front().ntiles == 0) bl.erase(bl.begin());
      } else if (o.perturb == "dup") {
        bl.push_back({bl.front().tile0, 1});
      }
    }
  }

  // Device images of the plan.
  std::vector<SppMinion> minions(SPP_MINION_SLOTS);
  std::vector<SppBlock> blocks;
  std::vector<uint64_t> tilesPerSlot(SPP_MINION_SLOTS, 0), rowTilesPerSlot(SPP_MINION_SLOTS, 0);
  uint64_t dumpTiles = 0, planCand = 0, planOps = 0, maxOps = 0;
  double maxModel = 0, sumModel = 0, maxEst = 0, maxM1 = 0;
  int busy = 0;
  for (int g : slots) {
    SppMinion& mp = minions[g];
    mp.first_block = uint32_t(blocks.size());
    mp.nblocks = uint32_t(plan.slots[g].size());
    mp.dump_base = dumpTiles;
    for (const Block& b : plan.slots[g]) {
      SppBlock sb{};
      sb.tile0 = uint32_t(b.tile0);
      sb.ntiles = uint32_t(b.ntiles);
      const std::vector<int> sub = unrank(16 * b.tile0, I.k - 1);
      for (int e = 0; e < I.k - 1; ++e) sb.sub[e] = uint16_t(sub[e]);
      blocks.push_back(sb);
      rowTilesPerSlot[g] += b.ntiles;
    }
    const uint64_t ot = countOutputTiles(G, plan.slots[g]);
    tilesPerSlot[g] = ot;
    dumpTiles += ot;
    planCand += countCandidates(G, plan.slots[g]);
    const uint64_t ops = ot * uint64_t(G.S);
    planOps += ops;
    maxOps = std::max(maxOps, ops);
    const double mc = modelCycles(G, plan.slots[g], planCost);
    maxModel = std::max(maxModel, mc);
    maxM1 = std::max(maxM1, modelCycles(G, plan.slots[g], TileCost{}));  // M1's model, whatever cut the plan
    maxEst = std::max(maxEst, estCycles(G, plan.slots[g]));
    sumModel += mc;
    busy += plan.slots[g].empty() ? 0 : 1;
  }
  if (blocks.empty()) blocks.push_back(SppBlock{});
  for (int g : slots)
    if (rowTilesPerSlot[g] >= 0xFFFFFFFFull) {
      std::cerr << "refused: minion slot " << g << " has " << rowTilesPerSlot[g] << " row tiles (32-bit counts)\n";
      return 2;
    }
  // Modelled kernel time at 600 MHz. Tensor: the fitted pipeline model of the kernel that runs, every minion's row
  // tiles simulated in order (pipeSimMinion) at the shire's L2 demand U, iterated on the sum of the steady costs.
  // Kept alongside for the guard: M1's model (modelCycles / estCycles with M1's cost, which M3 showed 2.7x low;
  // model_m1_s), the plan's own cost summed (model_plan_s: the fitted steady costs under --cost fit) and, while an
  // M4 change runs on predicted constants, the same plan simulated with M1's fitted constants (model_fallback_s:
  // the launch if the M4 changes gain nothing; review of M4, finding 1). Scalar: about 12 instructions per
  // 64-sample word per candidate at 0.5 instructions per cycle (one hart; two harts halve it).
  const double modelPlanS = maxModel / 600e6, modelM1S = maxM1 / 600e6, estM1S = maxEst / 600e6;
  double modelS = modelM1S, estS = estM1S, fitImbalance = 0, fitU = 0, fallbackS = 0;
  if (tensor) {
    const bool res = G.S <= 3;
    const int k1 = I.k - 1;
    const double copy = 5000.0 + 200.0 * double((uint64_t(G.nJ) * G.S + o.perShire - 1) / o.perShire);
    std::vector<std::vector<std::pair<int, uint64_t>>> rles;
    for (int g : slots) rles.push_back(blocksRle(G, plan.slots[g]));
    // The busiest minion's cycles under constants P; U and the max/mean imbalance on the side.
    auto simulate = [&](const PipeConst& P, double& Uout, double& imb) -> double {
      double U = pipePlanU(o.perShire);
      for (int it = 0; it < 3; ++it) {  // U from the steady costs (cheap), then one full simulation
        const TileCost tc = pipeTileCost(G, P, nbuf, !stageScp, U, epiOn);
        std::vector<double> est;
        std::vector<double> sb(32, 0.0);
        std::vector<int> sn(32, 0);
        for (size_t i = 0; i < slots.size(); ++i) {
          if (rles[i].empty()) continue;
          est.push_back(copy + modelCycles(G, plan.slots[slots[i]], tc));
          sb[slots[i] / 32] += pipeShireBytes(rles[i], G.S, res);
          sn[slots[i] / 32] = 1;
        }
        if (est.empty()) break;
        std::sort(est.begin(), est.end());
        double bsum = 0;
        int ns = 0;
        for (int sh = 0; sh < 32; ++sh)
          if (sn[sh]) bsum += sb[sh], ++ns;
        U = (bsum / ns) / (est[est.size() / 2] * 128.0);
      }
      Uout = U;
      double mx = 0, sum = 0;
      int nb = 0;
      for (size_t i = 0; i < slots.size(); ++i) {
        if (rles[i].empty()) continue;
        const double c = pipeSimMinion(rles[i], G.S, k1, res, nbuf, epiOn, !stageScp, U, copy, P).cycles;
        mx = std::max(mx, c);
        sum += c;
        ++nb;
      }
      imb = nb ? mx / (sum / nb) : 0;
      return mx;
    };
    try {
      modelS = simulate(pipe, fitU, fitImbalance) / 600e6;
      if (!m1Kernel && o.pipeSet.empty()) {
        double u = 0, imb = 0;
        fallbackS = simulate(pipeVariant(false, false, false), u, imb) / 600e6;
      }
    } catch (const std::exception& e) {
      std::cerr << "model: " << e.what() << "\n";
      return 2;
    }
    estS = modelS * (m1Kernel ? 1.15 : 1.3);
  } else {
    double mx = 0;
    for (int g : slots) mx = std::max(mx, double(countCandidates(G, plan.slots[g])) * (24.0 * G.S + 40.0));
    modelS = estS = mx / 600e6 / (o.twoHart ? 2.0 : 1.0);
  }
  const double guardS = tensor ? std::max({modelS, estS, modelM1S, estM1S, modelPlanS,
                                           o.trustModel ? 0.0 : 1.15 * fallbackS})
                               : std::max(modelS, estS);
  const bool onCard = !o.sysemu && !o.dry && !verify;
  if (onCard && guardS > o.maxKernelS) {
    std::cerr << "refused: the modelled kernel time " << guardS << " s is over --max-kernel-s " << o.maxKernelS
              << " s (use more shires, or --slice I/N"
              << (!o.trustModel && 1.15 * fallbackS >= guardS
                      ? "; the M4 kernel's model x1.3 is " + std::to_string(estS) +
                            " s, but the plan at M1's fitted speed x1.15 is " + std::to_string(1.15 * fallbackS) +
                            " s: --trust-model once the same kernel ran within x1.3 of its model"
                      : std::string())
              << ")\n";
    return 2;
  }
  if (o.dump && dumpTiles * SPP_TILE_BYTES > (512ull << 20)) {
    std::cerr << "refused: the dump would be " << (dumpTiles >> 10) << " MB\n";
    return 2;
  }
  // A value check is required on a card whenever the closed forms cannot catch a wrong value (review R1, finding 1).
  if (onCard && !o.timingOnly && o.oracle == "off" && (!fullCoverage || o.nowaitA)) {
    std::cerr << "refused: --oracle off on a card needs a plan that covers every candidate (closed forms) and no "
                 "--nowait-a; use --oracle auto|sample|on, and --records-out for an offline --verify-records\n";
    return 2;
  }

  // Host images.
  std::vector<uint64_t> binomK(I.n);
  for (int j = 0; j < I.n; ++j) binomK[j] = binom64(j, I.k);
  const std::vector<uint8_t> xb = tensor ? makeXB(I) : std::vector<uint8_t>(SPP_TILE_BYTES, 0);
  const std::vector<uint64_t> xt = tensor ? makeXT(I) : std::vector<uint64_t>(8, 0);  // slice-major X (GEN_INC)
  std::vector<SppRecord> records(SPP_HARTS), zeroRecords(SPP_HARTS);
  std::memset(zeroRecords.data(), 0, zeroRecords.size() * sizeof(SppRecord));
  std::memset(records.data(), 0, records.size() * sizeof(SppRecord));
  std::vector<uint8_t> sync(size_t(SPP_MINION_SLOTS) * SPP_SYNC_BYTES, 0);
  const size_t dumpBytes = std::max<size_t>(SPP_TILE_BYTES, size_t(dumpTiles) * SPP_TILE_BYTES * (o.dump ? 1 : 0));
  std::vector<int32_t> dumpHost(dumpBytes / 4, 0x7F7F7F7F);  // unwritten entries stay 0x7F7F7F7F
  int maxSlot = 0;
  for (int g : slots) maxSlot = std::max(maxSlot, g);
  const size_t stageDramBytes = (tensor && !stageScp) ? size_t(maxSlot + 1) * stride : 64;

  const uint64_t flags = (o.dump ? SPP_F_DUMP : 0) | (o.twoHart ? SPP_F_TWOHART : 0) |
                         (o.nowaitA ? SPP_F_NOWAIT_A : 0) | (o.timingOnly ? SPP_F_NOEPI : 0) |
                         (o.perturb == "mask" && perturbSlot >= 0 ? (SPP_F_PERTURB_MASK | (uint64_t(perturbSlot) << 32)) : 0) |
                         (tensor && o.genInc ? SPP_F_GEN_INC : 0) | (tensor && o.epiHide ? SPP_F_EPI_HIDE : 0) |
                         (tensor && o.abuf == 3 ? SPP_F_ABUF3 : 0) | (tensor && !o.genProbe.empty() ? SPP_F_GEN_NOSTORE : 0);
  // What runs, for the JSON line: the kernel's changes (3 A buffers apply to streamed A only, and bring the
  // epilogue in pieces with them), the plan's cost, and the fitted model's constants overridden.
  std::string m4json;
  {
    std::ostringstream m;
    const bool ab3 = tensor && o.abuf == 3 && G.S > 3;
    m << "{\"variant\":\"" << o.variant << "\",\"kernel\":\"" << (m1Kernel ? "m1" : "m4") << "\",\"gen\":\""
      << (tensor && o.genInc ? "inc" : "m1") << "\",\"epi\":\"" << (tensor && (o.epiHide || ab3) ? "hide" : "m1")
      << "\",\"abuf\":" << (ab3 ? 3 : 2) << ",\"cost\":\"" << (tensor && o.costFit ? "fit" : "m1")
      << "\",\"slice_cost\":\"" << (tensor && o.sliceFit ? "fit" : "m1") << "\",\"pipe_set\":\"" << o.pipeSet
      << "\",\"gen_probe\":\"" << o.genProbe << "\",\"trust_model\":" << tf(o.trustModel) << ",\"flags\":\""
      << hex(flags & 0xFFFFFFFFull) << "\"}";
    m4json = m.str();
  }
  std::mt19937_64 rng(uint64_t(std::chrono::high_resolution_clock::now().time_since_epoch().count()) ^ 0x5eed);
  const uint32_t epochBase = uint32_t(rng());

  // The launch's timeout and the harts' poll limit (each poll is an L2 atomic plus a 70-330 cycle pause, under
  // ~420 cycles: a hart gives up within 0.4 of the timeout at 600 MHz). The simulator runs one hart at a time, so
  // there a hart may wait for millions of the other's instructions.
  const double timeoutPlan = o.sysemu ? 3600.0 : std::clamp(std::ceil(2.0 * guardS + 1.5), 2.0, 8.0);
  const uint64_t pollLimit = o.pollLimit ? o.pollLimit
                             : o.sysemu  ? (1ull << 30)
                                         : std::clamp<uint64_t>(uint64_t(0.4 * timeoutPlan * 600e6 / 420.0), 1ull << 20, 1ull << 23);

  std::cerr << "sparseparity " << o.mode << " n=" << I.n << " k=" << I.k << " eta=" << I.eta << " m=" << I.m
            << " seed=" << I.seed << " S=" << G.S << " candidates=" << G.ncand << " tiles=" << G.workTiles
            << " plan: " << planSource << " shires=" << hex(o.shires) << " per_shire=" << o.perShire << " slice="
            << o.sliceI << "/" << o.sliceN << " [" << t0 << "," << t1 << ") ops=" << planOps << " model=" << modelS
            << " s est=" << estS << " s"
            << (tensor ? (stageScp ? " stage=scp" : " stage=dram") : "") << (tensor ? " nbuf=" + std::to_string(nbuf) : "")
            << " device=" << (verify ? "none (verify)" : o.sysemu ? "sysemu" : "silicon") << "\n";

  if (o.dry) {
    std::ostringstream s;
    s << "{\"workload\":\"sparseparity\",\"device\":\"none\",\"mode\":\"" << o.mode << "\",\"n\":" << I.n
      << ",\"k\":" << I.k << ",\"eta\":" << I.eta << ",\"m\":" << I.m << ",\"seed\":" << I.seed << ",\"S\":" << G.S
      << ",\"candidates\":" << G.ncand << ",\"work_tiles\":" << G.workTiles << ",\"shires\":\"" << hex(o.shires)
      << "\",\"per_shire\":" << o.perShire << ",\"slice\":\"" << o.sliceI << "/" << o.sliceN << "\",\"plan_source\":\""
      << planSource << "\",\"tiles\":[" << t0 << "," << t1 << "],\"coverage\":\"" << (fullCoverage ? "full" : "partial")
      << "\",\"plan_candidates\":" << planCand << ",\"ops\":" << planOps << ",\"ops_max\":" << maxOps
      << ",\"model_s\":" << modelS << ",\"est_s\":" << estS << ",\"model_imbalance\":"
      << (tensor ? fitImbalance : busy ? maxModel / (sumModel / busy) : 0) << ",\"model_m1_s\":" << modelM1S
      << ",\"est_m1_s\":" << estM1S << ",\"model_plan_s\":" << modelPlanS << ",\"model_fallback_s\":" << fallbackS
      << ",\"guard_s\":" << guardS << ",\"plan_imbalance\":" << (busy ? maxModel / (sumModel / busy) : 0)
      << ",\"model_U\":" << fitU << ",\"m4\":" << m4json << ",\"stage\":\""
      << (tensor ? (stageScp ? "scp" : "dram") : "none") << "\",\"nbuf\":" << nbuf << ",\"scp_layout_kb\":"
      << (layoutEnd + 1023) / 1024 << ",\"dump_tiles\":" << dumpTiles << ",\"timeout_s\":" << timeoutPlan
      << ",\"poll_limit\":" << pollLimit << ",\"refused_on_silicon\":" << tf(guardS > o.maxKernelS)
      << ",\"status\":\"DRY\"}";
    std::cout << s.str() << std::endl;
    return 0;
  }

  // ---------------------------------------------------------------- the device (held only in this block)
  std::vector<double> launchS;
  std::vector<uint32_t> epochs;
  double openS = 0, setupS = 0, heldS = 0;
  bool launchOk = true, repsConsistent = true;
  int repsDone = 0;
  std::string launchErr, stopReason;
  uint64_t scpKBDevice = 0;
  std::vector<std::string> problems;
  // per-rep checks: every active hart's record carries this launch's epoch and no error; hart 0's results equal
  // the first rep's (review R1, finding 10)
  std::vector<Acc> firstRep;
  auto repCheck = [&](uint32_t ep, int r) {
    int bad = 0;
    for (int g : slots) {
      const bool h1 = tensor || o.twoHart;
      for (int th = 0; th < (h1 ? 2 : 1); ++th) {
        const SppRecord& x = records[size_t(2 * g + th)];
        if ((x.status >> 16) != (ep & 0xFFFF) || (x.status & SPP_STATUS_BAD)) ++bad;
      }
    }
    if (bad && problems.size() < 8) problems.push_back("rep " + std::to_string(r) + ": " + std::to_string(bad) + " bad records");
    std::vector<Acc> cur;
    for (int g : slots) cur.push_back(accOf(records, g, !tensor && o.twoHart));
    if (r == 0) {
      firstRep = cur;
    } else {
      for (size_t i = 0; i < cur.size(); ++i) {
        const Acc &a = firstRep[i], &b = cur[i];
        if (a.sum != b.sum || a.sq != b.sq || a.count != b.count || a.best != b.best || a.bestRank != b.bestRank || a.tie != b.tie) {
          if (repsConsistent && problems.size() < 8)
            problems.push_back("rep " + std::to_string(r) + ": minion slot " + std::to_string(slots[i]) + " differs from rep 0");
          repsConsistent = false;
        }
      }
    }
  };
  if (verify) {
    std::ifstream f(o.verifyRecords, std::ios::binary);
    f.read(reinterpret_cast<char*>(records.data()), std::streamsize(records.size() * sizeof(SppRecord)));
    if (!f) {
      std::cerr << "cannot read " << SPP_HARTS << " records from " << o.verifyRecords << "\n";
      return 2;
    }
    const uint32_t ep = slots.empty() ? 0 : (records[size_t(2 * slots[0])].status >> 16);
    epochs.push_back(ep);
    repCheck(ep, 0);
    repsDone = 1;
  } else {
    const auto elf = readFile(o.kernel);
    if (elf.empty()) {
      std::cerr << "cannot read kernel " << o.kernel << "\n";
      return 1;
    }
    const auto tOpen = Clock::now();
    std::shared_ptr<dev::IDeviceLayer> deviceLayer = makeDeviceLayer(o.sysemu, o.simArgs);
    auto runtime = rt::IRuntime::create(deviceLayer);
    const auto devices = runtime->getDevices();
    if (devices.empty()) {
      std::cerr << "no ET devices found\n";
      return 1;
    }
    const auto device = devices[0];
    // The scratchpad the layout may use: the device reports the whole chip's in MB (runtime RuntimeImp.cpp:
    // totalScratchPadSize_ / 1024) over its compute shires (review R1, finding 11).
    {
      const auto props = runtime->getDeviceProperties(device);
      const int nsh = __builtin_popcount(props.computeMinionShireMask_ & 0xFFFFFFFFu);
      if (props.l2scratchpadSize_ && nsh) scpKBDevice = uint64_t(props.l2scratchpadSize_) * 1024 / uint64_t(nsh);
    }
    if (tensor && scpKBDevice && layoutEnd > scpKBDevice * 1024) {
      std::cerr << "refused: the scratchpad layout ends at " << (layoutEnd + 1023) / 1024 << " KB, the device reports "
                << scpKBDevice << " KB per shire (TensorLoadL2Scp would wrap): rerun with --scp-kb " << scpKBDevice << "\n";
      return 2;
    }
    const auto stream = runtime->createStream(device);
    openS = secondsSince(tOpen);
    const auto load = runtime->loadCode(stream, elf.data(), elf.size());
    if (!runtime->waitForEvent(load.event_, std::chrono::seconds(o.sysemu ? 3600 : 5))) {
      std::cerr << "loading the kernel timed out\n";
      launchOk = false;
    }
    auto alloc = [&](size_t bytes) { return runtime->mallocDevice(device, std::max<size_t>(bytes, 64), 1024); };
    auto put = [&](std::byte* d, const void* h, size_t bytes) {
      runtime->memcpyHostToDevice(stream, reinterpret_cast<const std::byte*>(h), d, bytes);
    };
    const auto wait = std::chrono::seconds(o.sysemu ? 3600 : 3);
    std::byte* dX = alloc(I.X.size() * 8);
    std::byte* dY = alloc(I.y.size() * 8);
    std::byte* dXB = alloc(xb.size());
    std::byte* dBin = alloc(binomK.size() * 8);
    std::byte* dMin = alloc(minions.size() * sizeof(SppMinion));
    std::byte* dBlk = alloc(blocks.size() * sizeof(SppBlock));
    std::byte* dRec = alloc(records.size() * sizeof(SppRecord));
    std::byte* dDump = alloc(dumpBytes);
    std::byte* dSync = alloc(sync.size());
    std::byte* dStage = alloc(stageDramBytes);
    std::byte* dXT = alloc(xt.size() * 8);
    if (launchOk) {
      put(dX, I.X.data(), I.X.size() * 8);
      put(dY, I.y.data(), I.y.size() * 8);
      put(dXB, xb.data(), xb.size());
      put(dBin, binomK.data(), binomK.size() * 8);
      put(dMin, minions.data(), minions.size() * sizeof(SppMinion));
      put(dBlk, blocks.data(), blocks.size() * sizeof(SppBlock));
      put(dDump, dumpHost.data(), dumpBytes);
      put(dSync, sync.data(), sync.size());
      put(dXT, xt.data(), xt.size() * 8);
      if (!runtime->waitForStream(stream, wait)) {
        launchErr = "copy-in did not finish";
        launchOk = false;
      }
    }
    setupS = secondsSince(tOpen) - openS;

    SppArgs args{};
    args.mode = tensor ? SPP_TENSOR : SPP_SCALAR;
    args.flags = flags;
    args.shire_mask = o.shires;
    args.per_shire = uint64_t(o.perShire);
    args.n = uint64_t(I.n);
    args.k = uint64_t(I.k);
    args.m = uint64_t(I.m);
    args.S = uint64_t(G.S);
    args.nJ = uint64_t(G.nJ);
    args.nrows = G.nrows;
    args.xbits = reinterpret_cast<uint64_t>(dX);
    args.ybits = reinterpret_cast<uint64_t>(dY);
    args.xb = reinterpret_cast<uint64_t>(dXB);
    args.binom_k = reinterpret_cast<uint64_t>(dBin);
    args.minions = reinterpret_cast<uint64_t>(dMin);
    args.blocks = reinterpret_cast<uint64_t>(dBlk);
    args.records = reinterpret_cast<uint64_t>(dRec);
    args.dump = reinterpret_cast<uint64_t>(dDump);
    args.sync = reinterpret_cast<uint64_t>(dSync);
    args.xb_line = SPP_SCP_MIN_OFFSET / 64;
    args.stage = stageScp ? stageOff : reinterpret_cast<uint64_t>(dStage);
    args.stage_stride = stride;
    args.stage_global = stageScp ? 0 : 1;
    args.nbuf = uint64_t(nbuf);
    args.poll_limit = pollLimit;
    args.xt = reinterpret_cast<uint64_t>(dXT);

    rt::KernelLaunchOptions lo;
    lo.setShireMask(o.shires);
    lo.setBarrier(true);
    for (int r = 0; r < o.reps && launchOk; ++r) {
      // Launch only if the launch's whole timeout, plus a readback, still ends by the budget (review R1, finding 2).
      const double elapsed = secondsSince(tProc);
      // whole seconds (the runtime's wait takes std::chrono::seconds), rounded down so the launch ends in time
      const int toS = int(std::floor(o.sysemu ? timeoutPlan : std::min(timeoutPlan, o.budget - elapsed - 0.5)));
      if (!o.sysemu && (toS < 1 || toS < 1.25 * guardS + 0.5)) {
        stopReason = "stopped after " + std::to_string(r) + " launch(es): " + std::to_string(o.budget - elapsed) +
                     " s left before --budget, a launch needs " + std::to_string(1.25 * guardS + 1.0) +
                     " s (its timeout, rounded down to whole seconds, and a readback)";
        std::cerr << stopReason << "\n";
        break;
      }
      uint32_t ep = epochBase + uint32_t(r) * 0x10001u;
      if ((ep & 0xFFFF) == 0) ep |= 1;
      args.epoch = ep;
      put(dRec, zeroRecords.data(), zeroRecords.size() * sizeof(SppRecord));
      if (!runtime->waitForStream(stream, wait)) {
        launchErr = "clearing the records did not finish";
        launchOk = false;
        break;
      }
      epochs.push_back(ep);
      const auto tl = Clock::now();
      runtime->kernelLaunch(stream, load.kernel_, reinterpret_cast<const std::byte*>(&args), sizeof(args), lo);
      launchOk = runtime->waitForStream(stream, std::chrono::seconds(toS));
      launchS.push_back(secondsSince(tl));
      if (!launchOk) {
        launchErr = "kernel did not finish within " + std::to_string(toS) + " s; stream aborted, nothing read back";
        std::cerr << launchErr << "\n";
        runtime->waitForEvent(runtime->abortStream(stream), std::chrono::seconds(2));
      }
      for (const auto& e : runtime->retrieveStreamErrors(stream)) {
        launchErr += (launchErr.empty() ? "" : "; ") + e.getString();
        std::cerr << "stream error: " << e.getString() << "\n";
        launchOk = false;
      }
      if (!launchOk) break;
      runtime->memcpyDeviceToHost(stream, dRec, reinterpret_cast<std::byte*>(records.data()),
                                  records.size() * sizeof(SppRecord));
      if (!runtime->waitForStream(stream, wait)) {
        launchErr = "reading the records back did not finish";
        launchOk = false;
        break;
      }
      ++repsDone;
      repCheck(ep, r);
    }
    if (o.dump && launchOk && repsDone > 0) {
      runtime->memcpyDeviceToHost(stream, dDump, reinterpret_cast<std::byte*>(dumpHost.data()), dumpBytes);
      if (!runtime->waitForStream(stream, wait)) launchErr += (launchErr.empty() ? "" : "; ") + std::string("dump readback did not finish");
    }
    for (std::byte* p : {dX, dY, dXB, dBin, dMin, dBlk, dRec, dDump, dSync, dStage, dXT}) runtime->freeDevice(device, p);
    runtime->unloadCode(load.kernel_);
    runtime->destroyStream(stream);
    heldS = secondsSince(tOpen);
  }  // runtime and device layer destroyed here: the device is released
  if (!verify) std::cerr << "device open " << openS << " s, load+copy-in " << setupS << " s, held " << heldS << " s\n";

  if (!o.recordsOut.empty() && !verify) {
    std::ofstream f(o.recordsOut, std::ios::binary);
    f.write(reinterpret_cast<const char*>(records.data()), std::streamsize(records.size() * sizeof(SppRecord)));
  }
  const uint32_t ep = epochs.empty() ? 0 : epochs.back();
  if (!o.outPath.empty()) {
    try {
      writeM0Out(o.outPath, I, G, fromM0 ? &m0 : nullptr, plan, records, ep);
    } catch (const std::exception& e) {
      std::cerr << e.what() << "\n";
    }
  }
  if (!o.dumpOut.empty() && o.dump) {
    std::ofstream f(o.dumpOut, std::ios::binary);
    f.write(reinterpret_cast<const char*>(dumpHost.data()), std::streamsize(dumpBytes));
  }

  // ---------------------------------------------------------------- checks (device closed)
  int badRecords = 0;
  Acc dev;
  uint64_t cyclesMax = 0, copyMax = 0, waitMax = 0, genPollsMax = 0, opsBusiest = 0;
  std::vector<double> cyc;
  auto recOf = [&](int g, int thread) -> const SppRecord& { return records[size_t(2 * g + thread)]; };
  auto recOk = [&](const SppRecord& r) { return (r.status >> 16) == (ep & 0xFFFF) && (r.status & SPP_STATUS_BAD) == 0; };
  const bool haveRecords = repsDone > 0;
  std::vector<int32_t> slotBest;
  for (int g : slots) {
    const bool h1 = tensor || o.twoHart;
    for (int th = 0; th < (h1 ? 2 : 1); ++th) {
      const SppRecord& r = recOf(g, th);
      if (haveRecords && !recOk(r)) {
        if (badRecords < 5) {
          std::ostringstream s;
          s << "hart " << 2 * g + th << " record status " << hex(r.status) << " (epoch " << hex(ep & 0xFFFF) << ")";
          problems.push_back(s.str());
        }
        ++badRecords;
      }
    }
    const Acc a = accOf(records, g, !tensor && o.twoHart);
    dev.merge(a);
    slotBest.push_back(a.count ? a.best : INT32_MIN);
    const SppRecord& r0 = recOf(g, 0);
    cyclesMax = std::max(cyclesMax, r0.cycles);
    if (r0.cycles == cyclesMax) opsBusiest = r0.work;
    cyc.push_back(double(r0.cycles));
    copyMax = std::max<uint64_t>(copyMax, r0.copy_cycles);
    if (tensor && haveRecords) {
      waitMax = std::max(waitMax, r0.wait);
      genPollsMax = std::max(genPollsMax, recOf(g, 1).wait);
      if (recOf(g, 1).count != rowTilesPerSlot[g] && problems.size() < 8)
        problems.push_back("hart " + std::to_string(2 * g + 1) + " generated " + std::to_string(recOf(g, 1).count) +
                           " tiles, plan " + std::to_string(rowTilesPerSlot[g]));
      if (r0.work != tilesPerSlot[g] * uint64_t(G.S) && problems.size() < 8)
        problems.push_back("hart " + std::to_string(2 * g) + " ran " + std::to_string(r0.work) + " ops, plan " +
                           std::to_string(tilesPerSlot[g] * uint64_t(G.S)));
    }
  }
  std::sort(cyc.begin(), cyc.end());
  const double cycMed = cyc.empty() ? 0 : cyc[cyc.size() / 2];

  // Totals against the plan and the closed forms (timing-only runs score nothing).
  const bool countOk = o.timingOnly ? dev.count == 0 : dev.count == planCand;
  std::string sumCheck = "partial", sqCheck = "partial";
  __int128 cfSum = 0;
  unsigned __int128 cfSq = 0;
  if (o.timingOnly) {
    sumCheck = sqCheck = "timing-only";
  } else if (fullCoverage) {
    closedForms(I, cfSum, cfSq);
    sumCheck = dev.sum == cfSum ? "ok" : "MISMATCH";
    sqCheck = uint64_t(dev.sq) == uint64_t(cfSq) ? "ok" : "MISMATCH";  // the card's sum is mod 2^64
  }
  // The reported best, rescored on the CPU; a tie is two harts at the best, or one hart that flags one.
  std::vector<int> answer;
  int32_t rescored = INT32_MIN;
  if (dev.count && dev.bestRank < G.ncand) {
    answer = unrank(dev.bestRank, I.k);
    rescored = scoreSubset(I, answer);
  }
  const bool rescoreOk = o.timingOnly || dev.count == 0 || rescored == dev.best;
  int hartsAtBest = 0, hartsTie = 0;
  for (size_t i = 0; i < slots.size(); ++i)
    if (dev.count && slotBest[i] == dev.best) {
      ++hartsAtBest;
      hartsTie += recTie(recOf(slots[i], 0)) || (!tensor && o.twoHart && recTie(recOf(slots[i], 1)));
    }
  const bool unique = dev.count > 0 && !dev.tie;
  const bool solved = !I.secret.empty() && answer == I.secret && unique;

  // The per-minion oracle and the dump.
  auto slotWords = [&](int g) { return double(tilesPerSlot[g]) * 256.0 * (G.S + 12) + double(rowTilesPerSlot[g]) * 16 * G.S * I.k; };
  double oracleWork = 0;
  for (int g : slots) oracleWork += slotWords(g);
  std::vector<int> busySlots;
  for (int g : slots)
    if (!plan.slots[g].empty()) busySlots.push_back(g);
  std::string oracleMode = o.timingOnly ? "off" : o.oracle;
  if (o.dump && !o.timingOnly) oracleMode = "on";  // the dump is compared tile by tile against the full oracle
  if (verify && o.oracle == "auto") oracleMode = "on";
  const bool deadlined = !o.sysemu && !verify;
  const double checksDeadline = deadlined ? kChecksDeadline : 1e18;
  if (oracleMode == "auto") {
    const double fullS = oracleWork / kOracleUnitsPerS;
    oracleMode = (secondsSince(tProc) + fullS <= checksDeadline) ? "on" : "sample";
  }
  std::vector<int> oracleSlots;
  if (oracleMode == "on") {
    oracleSlots = busySlots;
  } else if (oracleMode == "sample") {
    // a random order (seeded by the epoch, so every launch samples other minions), taken while it fits
    std::vector<int> order = busySlots;
    std::mt19937_64 srng(uint64_t(ep) * 0x9E3779B97F4A7C15ull + 7);
    std::shuffle(order.begin(), order.end(), srng);
    double work = 0;
    for (int g : order) {
      const double w = slotWords(g);
      const bool first = oracleSlots.empty();
      if (!first && (work + w > o.oracleWork || secondsSince(tProc) + (work + w) / kOracleUnitsPerS > checksDeadline)) break;
      oracleSlots.push_back(g);
      work += w;
    }
  }
  std::string oracleCheck = "skipped", dumpCheck = "n/a";
  uint64_t oracleBad = 0, dumpBad = 0, oracleDone = 0;
  if (!oracleSlots.empty() && haveRecords) {
    std::vector<int32_t> expect;
    std::vector<char> inSample(SPP_MINION_SLOTS, 0);
    for (int g : oracleSlots) inSample[g] = 1;
    // In slot order (the dump's order) when the dump is checked; otherwise the sampled order.
    const std::vector<int>& seq = o.dump ? slots : oracleSlots;
    for (int g : seq) {
      if (!inSample[g] && !o.dump) continue;
      if (deadlined && oracleMode == "sample" && oracleDone > 0 && secondsSince(tProc) > checksDeadline) break;
      Acc a;
      scoreBlocks(I, G, plan.slots[g], a, o.dump ? &expect : nullptr, !tensor);
      if (!plan.slots[g].empty()) ++oracleDone;
      const Acc d = accOf(records, g, !tensor && o.twoHart);
      const bool same = d.count == a.count && d.sum == a.sum && uint64_t(d.sq) == uint64_t(a.sq) &&
                        (a.count == 0 || (d.best == a.best && d.bestRank == a.bestRank && d.tie == a.tie));
      if (!same) {
        if (oracleBad < 4) {
          std::ostringstream s;
          s << "minion slot " << g << ": card count " << d.count << " sum " << i128(d.sum) << " sq "
            << uint64_t(d.sq) << " best " << d.best << "@" << d.bestRank << (d.tie ? " tie" : "") << ", oracle count "
            << a.count << " sum " << i128(a.sum) << " sq " << uint64_t(a.sq) << " best " << a.best << "@" << a.bestRank
            << (a.tie ? " tie" : "");
          problems.push_back(s.str());
        }
        ++oracleBad;
      }
    }
    const std::string scope = oracleDone == busySlots.size() ? "all " + std::to_string(oracleDone) + " minions"
                                                              : std::to_string(oracleDone) + " of " + std::to_string(busySlots.size()) + " minions (sampled)";
    oracleCheck = oracleBad ? "MISMATCH " + std::to_string(oracleBad) + " of " + scope : "exact, " + scope;
    if (o.dump) {
      if (expect.size() != dumpHost.size()) {
        dumpCheck = "SIZE " + std::to_string(expect.size()) + " vs " + std::to_string(dumpHost.size());
      } else {
        for (size_t i = 0; i < expect.size(); ++i) {
          if (expect[i] != dumpHost[i]) {
            if (dumpBad < 4) {
              std::ostringstream s;
              s << "dump tile " << i / 256 << " row " << (i % 256) / 16 << " col " << i % 16 << ": card "
                << dumpHost[i] << ", CPU " << expect[i];
              problems.push_back(s.str());
            }
            ++dumpBad;
          }
        }
        dumpCheck = dumpBad ? "MISMATCH " + std::to_string(dumpBad) + " of " + std::to_string(expect.size())
                            : "exact " + std::to_string(expect.size()) + " entries";
      }
    }
  }
  // Every value check that ran; on silicon a run without one fails (review R1, finding 1).
  const bool valueChecked = o.timingOnly || (fullCoverage && sumCheck == "ok" && sqCheck == "ok") || oracleDone > 0;
  if (!valueChecked && !o.sysemu) problems.push_back("no value check ran (partial coverage and no oracle)");
  const bool repsOk = repsDone == o.reps || verify;
  if (!repsOk) problems.push_back("reps: " + std::to_string(repsDone) + " of " + std::to_string(o.reps) + " done");

  const bool pass = launchOk && haveRecords && repsOk && repsConsistent && badRecords == 0 && countOk && rescoreOk &&
                    sumCheck != "MISMATCH" && sqCheck != "MISMATCH" && oracleBad == 0 && dumpBad == 0 &&
                    dumpCheck.rfind("SIZE", 0) != 0 && (valueChecked || o.sysemu) && problems.empty();
  if (!countOk) problems.push_back("count " + std::to_string(dev.count) + " != plan " + std::to_string(planCand));
  if (!rescoreOk) problems.push_back("best c " + std::to_string(dev.best) + " rescored " + std::to_string(rescored));

  // ---------------------------------------------------------------- one JSON line
  JsonOut j;
  j.s << "{";
  j.ks("workload", "sparseparity");
  j.ks("device", verify ? "none (verify-records)" : o.sysemu ? "sysemu" : "silicon");
  j.ks("mode", o.mode);
  j.raw("flags", std::string("{\"dump\":") + tf(o.dump) + ",\"two_hart\":" + tf(o.twoHart) + ",\"nowait_a\":" +
                     tf(o.nowaitA) + ",\"timing_only\":" + tf(o.timingOnly) + "}");
  j.raw("m4", m4json);
  {
    std::ostringstream s;
    s << "{\"n\":" << I.n << ",\"k\":" << I.k << ",\"eta\":" << I.eta << ",\"m\":" << I.m << ",\"seed\":" << I.seed
      << ",\"hash\":\"" << std::hex << instHash(I) << std::dec << "\",\"secret\":" << jarr(I.secret)
      << ",\"source\":\"" << (o.instPath.empty() ? "generated" : o.instPath) << "\"}";
    j.raw("instance", s.str());
  }
  {
    std::ostringstream s;
    s << "{\"S\":" << G.S << ",\"nJ\":" << G.nJ << ",\"rows\":" << G.nrows << ",\"row_tiles\":" << G.ntiles
      << ",\"work_tiles\":" << G.workTiles << ",\"candidates\":" << G.ncand << "}";
    j.raw("geometry", s.str());
  }
  {
    std::ostringstream s;
    s << "{\"shires\":\"" << hex(o.shires) << "\",\"per_shire\":" << o.perShire << ",\"minions\":" << slots.size()
      << ",\"busy_minions\":" << busy << ",\"rounds\":" << o.rounds << ",\"slice\":\"" << o.sliceI << "/"
      << o.sliceN << "\",\"tiles\":[" << t0 << "," << t1 << "],\"blocks\":" << blocks.size() << ",\"source\":\""
      << planSource << "\",\"coverage\":\"" << (fullCoverage ? "full" : "partial") << "\",\"perturb\":\"" << o.perturb
      << "\",\"candidates\":" << planCand << ",\"ops\":" << planOps << ",\"ops_max\":" << maxOps << ",\"model_s\":"
      << modelS << ",\"est_s\":" << estS << ",\"model_imbalance\":"
      << (tensor ? fitImbalance : busy ? maxModel / (sumModel / busy) : 0) << ",\"model_m1_s\":" << modelM1S
      << ",\"est_m1_s\":" << estM1S << ",\"model_plan_s\":" << modelPlanS << ",\"model_fallback_s\":" << fallbackS
      << ",\"guard_s\":" << guardS << ",\"plan_imbalance\":" << (busy ? maxModel / (sumModel / busy) : 0)
      << ",\"model_U\":" << fitU
      << ",\"stage\":\"" << (tensor ? (stageScp ? "scp" : "dram") : "none") << "\",\"nbuf\":" << nbuf
      << ",\"scp_layout_kb\":" << (layoutEnd + 1023) / 1024 << ",\"scp_kb_assumed\":" << o.scpKB
      << ",\"scp_kb_device\":" << scpKBDevice << ",\"timeout_s\":" << timeoutPlan << ",\"poll_limit\":" << pollLimit
      << "}";
    j.raw("plan", s.str());
  }
  j.kv("open_s", openS);
  j.kv("setup_s", setupS);
  j.raw("launch_s", jarr(launchS));
  j.kv("reps_requested", o.reps);
  j.kv("reps_done", repsDone);
  j.ks("reps_consistent", repsConsistent ? "ok" : "MISMATCH");
  j.ks("stop_reason", stopReason);
  j.kv("device_held_s", heldS);
  {
    std::ostringstream s;
    s << "{\"cycles_max\":" << cyclesMax << ",\"cycles_median\":" << cycMed << ",\"copy_cycles_max\":" << copyMax
      << ",\"wait_cycles_max\":" << waitMax << ",\"gen_polls_max\":" << genPollsMax << ",\"ops_busiest\":"
      << opsBusiest << ",\"cycles_per_op_busiest\":" << (opsBusiest ? double(cyclesMax) / double(opsBusiest) : 0)
      << ",\"clock_mhz_est\":"
      << (launchS.empty() || launchS.back() <= 0 || o.sysemu ? 0 : double(cyclesMax) / launchS.back() / 1e6) << "}";
    j.raw("kernel", s.str());
  }
  {
    std::ostringstream s;
    s << "{\"best_c\":" << dev.best << ",\"best_rank\":" << dev.bestRank << ",\"answer\":" << jarr(answer)
      << ",\"unique\":" << tf(unique) << ",\"harts_at_best\":" << hartsAtBest << ",\"harts_flagging_tie\":" << hartsTie
      << ",\"solved\":" << tf(solved) << ",\"rescored_c\":" << rescored << ",\"sum_c\":\"" << i128(dev.sum)
      << "\",\"sum_c2_mod64\":\"" << uint64_t(dev.sq) << "\",\"count\":" << dev.count << "}";
    j.raw("result", s.str());
  }
  {
    std::ostringstream s;
    s << "{\"records\":\"" << (badRecords ? std::to_string(badRecords) + " bad" : haveRecords ? "ok" : "none")
      << "\",\"count\":\"" << (countOk ? "ok" : "MISMATCH") << "\",\"sum_c\":\"" << sumCheck << "\",\"sum_c2\":\""
      << sqCheck << "\",\"closed_form_sum_c\":\"" << (fullCoverage ? i128(cfSum) : "")
      << "\",\"closed_form_sum_c2\":\"" << (fullCoverage ? i128(__int128(cfSq)) : "") << "\",\"best_rescore\":\""
      << (rescoreOk ? "ok" : "MISMATCH") << "\",\"oracle\":\"" << oracleCheck << "\",\"oracle_mode\":\"" << oracleMode
      << "\",\"value_checked\":" << tf(valueChecked) << ",\"dump\":\"" << dumpCheck << "\",\"launch\":\""
      << (launchOk ? "ok" : "FAILED") << "\"}";
    j.raw("checks", s.str());
  }
  {
    std::ostringstream s;
    s << "[";
    for (size_t i = 0; i < problems.size(); ++i) {
      std::string p = problems[i];
      std::replace(p.begin(), p.end(), '"', '\'');
      s << (i ? "," : "") << "\"" << p << "\"";
    }
    s << "]";
    j.raw("problems", s.str());
  }
  j.ks("launch_error", launchErr);
  j.kv("process_s", secondsSince(tProc));
  j.ks("status", pass ? (o.timingOnly ? "TIMING" : "PASS") : "FAIL");
  j.s << "}";
  std::cout << j.s.str() << std::endl;
  return pass ? 0 : 1;
}
