#!/usr/bin/env bash
# sparseparity on a card: the M1, M2, M4 and M5 steps (README.md, "M1 on a card", "M2 on a card", "M4 on a card" and
# "M5 on a card"), one process per step.
#
#   bash workloads/sparseparity/card_run.sh <m1|probe|m2|m4|m4gen|m5|list> [--dry] [--build DIR] [--out DIR] [--from STEP]
#
# m5 (the two-stage screen: stage 1 on the card with variant b's kernel, planner and generation, stage 2 on the host)
# needs a build of the M5 sources with R4's fixes (default build/sparseparity-t): its host knows --m1 and --tau1,
# --perturb tau|lostlog, and poisons the survivor logs before each launch.
# m4 and m4gen need a build of the M4 sources (default build/sparseparity-h): the host's --variant m1 runs M1's kernel
# and planner on that build, so every A/B pair runs one binary. --build and --out may be absolute, or relative to the
# tree's root (the directory two levels above this script).
#
# Run it from the tree's root on the card's host (~/nekko on aifoundry1 and aifoundry3; never on aifoundry2, whose
# card is out of service since 2 October 2026), only with the owner's go-ahead for that card. Every step is one host
# process run as
#     flock -n /run/lock/etsoc-shire<N>.lock timeout 10 sparseparity_host ... --records-out <step>.rec
# so the lock is held for one process at a time and released between steps, and no process holds the device for
# more than 10 s (the host itself launches only while its timeout ends by 9 s). Before every step the script checks
# `et-who --check` and waits up to 5 minutes for a free card (on aifoundry1 the check counts both cards, so it waits
# while either is held). On aifoundry1 it uses card 1 (ET_DEVICES=1, etsoc-shire1.lock); card 0 is not used here.
# It stops at the first step whose result is not the expected one (a negative control must FAIL on its checksums and
# pass everything else), so a person can look before going on.
# After a step whose plan does not cover every candidate, the full per-minion oracle runs offline on the saved
# records (--verify-records: no device, no lock, no timeout); stage m4 also runs it, at the end, on its full-coverage
# M4 steps (the closed forms do not check the lane maxima, the best or the tie flag the new epilogue computes).
# Every step's line shows its launch time over the host's model (xR); in stage m4 a step whose guard trusts M4's
# predicted model (--trust-model: the whole (256,5), 2.25 s modelled, 3.66 s at M1's fitted speed) runs only after
# its gate steps, the same instance's halves with the same kernel, ran within x1.3 of their model in this --out
# directory; otherwise it is skipped (not a stop) and says why.
#
# --dry: every step with the host's --dry (plan and model only; the device is never opened, no lock is taken).
# --from STEP: skip the steps before STEP (after a stop). Output: --out DIR (default
# build/sparseparity-card/<host>-<time>/): <step>.json (the host's JSON line), .err, .rec, .verify.json, summary.txt,
# manifest.txt (et-lab-manifest).
set -u
cd "$(dirname "${BASH_SOURCE[0]}")/../.." || exit 2
WHAT=${1:-}; shift || true
DRY=; BUILD=; OUT=; FROM=
while [ $# -gt 0 ]; do
  case "$1" in
    --dry) DRY=1 ;;
    --build) BUILD=$2; shift ;;
    --out) OUT=$2; shift ;;
    --from) FROM=$2; shift ;;
    *) echo "unknown option $1" >&2; exit 2 ;;
  esac
  shift
done
case "$WHAT" in m1|probe|m2|m4|m4gen|m5|list) ;; *) echo "usage: $0 <m1|probe|m2|m4|m4gen|m5|list> [--dry] [--build DIR] [--out DIR] [--from STEP]" >&2; exit 2 ;; esac
case "$WHAT" in m4|m4gen) BUILD=${BUILD:-build/sparseparity-h} ;; m5) BUILD=${BUILD:-build/sparseparity-t} ;; *) BUILD=${BUILD:-build/sparseparity-f} ;; esac
case "$BUILD" in /*) ;; *) BUILD=$PWD/$BUILD ;; esac
HOST_BIN=$BUILD/host/sparseparity_host
SELFTEST=$BUILD/host/spp_selftest
[ -x "$HOST_BIN" ] && [ -x "$SELFTEST" ] || { echo "build first: $HOST_BIN" >&2; exit 2; }
if [ "$WHAT" = m4 ] || [ "$WHAT" = m4gen ]; then   # the usage text only: nothing is opened
  u=$("$HOST_BIN" --no-such-option 2>&1)
  grep -q -- '--variant m4|m1' <<< "$u" && grep -q -- '--trust-model' <<< "$u" || \
    { echo "$HOST_BIN has no --variant or no --trust-model: build these M4 sources" >&2; exit 2; }
fi
if [ "$WHAT" = m5 ]; then
  u=$("$HOST_BIN" --no-such-option 2>&1)
  grep -q -- '--m1 M1 --tau1 T' <<< "$u" || { echo "$HOST_BIN has no --m1/--tau1: build the M5 sources" >&2; exit 2; }
  grep -q -- 'lostlog' <<< "$u" || { echo "$HOST_BIN has no --perturb tau|lostlog (nor the logs' poisoning): build R4's sources (build/sparseparity-t)" >&2; exit 2; }
fi
H=$(hostname)
LOCK=/run/lock/etsoc-shire0.lock
if [ "$H" = aifoundry1 ]; then export ET_DEVICES=1; LOCK=/run/lock/etsoc-shire1.lock; fi
OUT=${OUT:-build/sparseparity-card/$H-$(date +%Y%m%d-%H%M%S)$([ -n "$DRY" ] && echo -dry)}

L2="--n 512 --k 4 --eta 0.4 --m 1850 --seed 1"
L1="--n 512 --k 4 --eta 0.3 --m 448 --seed 1"
C1="--n 128 --k 4 --eta 0.2 --m 192"
F5="--n 256 --k 5 --eta 0.4 --m 1925 --seed 1"
L5="--n 512 --k 5 --eta 0.4 --m 2151 --seed 1"
# name|expect|model kernel time|args   (expect: PASS, TIMING, NEG (drop/dup: a closed form fails, nothing else),
# NEGM (the mask: both closed forms and the oracle fail, the count holds), TIE (PASS, the answer not unique))
M1=(
  "m1-c0-scalar|PASS|1 ms|--mode scalar --dump"
  "m1-c0-tensor|PASS|0.1 ms|--mode tensor --dump"
  "m1-neg-drop|NEG|0.1 ms|--mode tensor --perturb drop"
  "m1-neg-dup|NEG|0.1 ms|--mode tensor --perturb dup"
  "m1-neg-mask|NEGM|0.1 ms|--mode tensor --perturb mask"
  "m1-tie|TIE|0.1 ms|--mode tensor --instance $OUT/tie.spi"
  "m1-c1-timing|TIMING|0.14 s|--mode tensor $C1 --seed 1 --timing-only"
  "m1-c1|PASS|0.14 s|--mode tensor $C1 --seed 1"
  "m1-l1-timing|TIMING|1.2 s|--mode tensor $L1 --slice 0/64 --timing-only"
  "m1-l1|PASS|1.2 s|--mode tensor $L1 --slice 0/64"
  "m1-l2-timing|TIMING|1.5 s|--mode tensor $L2 --slice 0/200 --timing-only"
  "m1-l2|PASS|1.5 s|--mode tensor $L2 --slice 0/200"
)
for s in $(seq 1 20); do M1+=("m1-c1-32-seed$s|PASS|4 ms|--mode tensor $C1 --seed $s --per-shire 32"); done
# The hand-off race probe (review R1, finding 3): 32 minions, each consuming one-column-tile row tiles right after
# hart 1 publishes them, with the full oracle; the streamed path (L2's m) and the resident one (C1's m), every staging.
PROBE=(
  "probe-l2-scp1|PASS|77 ms|--mode tensor $L2 --per-shire 32 --probe narrow:2000 --oracle on --stage scp --nbuf 1"
  "probe-l2-scp2|PASS|77 ms|--mode tensor $L2 --per-shire 16 --probe narrow:2000 --oracle on --stage scp --nbuf 2"
  "probe-l2-dram1|PASS|77 ms|--mode tensor $L2 --per-shire 32 --probe narrow:2000 --oracle on --stage dram --nbuf 1"
  "probe-l2-dram2|PASS|77 ms|--mode tensor $L2 --per-shire 32 --probe narrow:2000 --oracle on --stage dram --nbuf 2"
  "probe-c1-scp2|PASS|1 ms|--mode tensor $C1 --seed 1 --per-shire 32 --probe narrow:200 --oracle on --stage scp --nbuf 2"
  "probe-c1-scp1|PASS|1 ms|--mode tensor $C1 --seed 1 --per-shire 32 --probe narrow:200 --oracle on --stage scp --nbuf 1"
  "probe-c1-dram2|PASS|1 ms|--mode tensor $C1 --seed 1 --per-shire 32 --probe narrow:200 --oracle on --stage dram --nbuf 2"
  "probe-c1-dram1|PASS|1 ms|--mode tensor $C1 --seed 1 --per-shire 32 --probe narrow:200 --oracle on --stage dram --nbuf 1"
)
M2=("m2-c1-32|PASS|4 ms|--mode tensor $C1 --seed 1 --per-shire 32")
for P in 1 2 4 8 16 32; do   # the shire-bandwidth knee: the same work per minion (L1, S = 7, A streamed)
  M2+=("m2-knee-p$P-timing|TIMING|1.2 s|--mode tensor $L1 --per-shire $P --slice 0/$((64 / P)) --timing-only")
  M2+=("m2-knee-p$P|PASS|1.2 s|--mode tensor $L1 --per-shire $P --slice 0/$((64 / P))")
done
M2+=(
  "m2-l1-full|PASS|2.3 s|--mode tensor $L1 --per-shire 32"
  "m2-l2-q0|PASS|2.4 s|--mode tensor $L2 --per-shire 32 --slice 0/4"
  "m2-l2-q0-dram2|PASS|2.4 s|--mode tensor $L2 --per-shire 32 --slice 0/4 --stage dram --nbuf 2"
  "m2-l2-q0-dram1|PASS|2.4 s|--mode tensor $L2 --per-shire 32 --slice 0/4 --stage dram --nbuf 1"
  "m2-l2-q0-timing|TIMING|2.4 s|--mode tensor $L2 --per-shire 32 --slice 0/4 --timing-only"
  "m2-f5-s0|PASS|2.3 s|--mode tensor $F5 --per-shire 32 --slice 0/16"
  "m2-l5-s0|PASS|2.3 s|--mode tensor $L5 --per-shire 32 --slice 0/512"
  # last: skips the PRM's TensorWait before an A buffer is reloaded (sys_emu's checker rejects it); silicon only
  "m2-l2-q0-nowait|PASS|2.4 s|--mode tensor $L2 --per-shire 32 --slice 0/4 --nowait-a"
)
# M4 (README.md, "M4 on a card"): A/B of M1's kernel and planner against each change, on one build. Configurations:
# m1 = --variant m1 (M1 exactly: kernel and planner as on 29 September); a = M1's kernel, the plan cut by the fitted
# model; b, c = a with the incremental generation or the epilogue in pieces alone; m4 = both (the default); m4d = m4
# with 3 A buffers. A sliced step cuts its slice by M1's cost (--slice-cost m1), so its configurations scan the same
# tiles. "model" is tools/cycle_model.py m4's prediction (the host's --dry prints the same model_s): M1's kernel is
# fitted (M3 within +1.4%/+3.6%), M4's changes are predictions; the host refuses a launch whose model x1.3 (x1.15 for
# M1's kernel) is over 4 s.
ONE="--mode tensor --shires 0x1 --per-shire 32"
ALL="--mode tensor --shires 0xffffffff --per-shire 32"
CM1="--variant m1"; CA="--variant m1 --cost fit"; CB="--variant m1 --cost fit --gen inc"
CC="--variant m1 --cost fit --epi hide"; CM4="--variant m4"; CM4D="--variant m4 --abuf 3"
# m4a = M4's kernel on the plan cut by M1's fitted constants (--pipe-set changes only the plan and the model): the
# kernel's gain apart from the plan's balance (review of M4, finding 2)
CM4A="--variant m4 --pipe-set HIDDEN=0,G_TILE=2081,G_SLICE=2108,G_K=570.3"
M4=(
  # first, the hand-off race probe with M4's faster (incremental) generation, which the probe stage ran only with M1's;
  # the DRAM staging (fswl.ps) runs nowhere else in this stage (review of M4, finding 3)
  "m4-probe-l2-scp1|PASS|0.29 s|--mode tensor $L2 --per-shire 32 --probe narrow:2000 --oracle on --stage scp --nbuf 1 $CM4"
  "m4-probe-l2-dram1|PASS|0.49 s|--mode tensor $L2 --per-shire 32 --probe narrow:2000 --oracle on --stage dram --nbuf 1 $CM4"
  "m4-probe-l2-dram2|PASS|0.45 s|--mode tensor $L2 --per-shire 32 --probe narrow:2000 --oracle on --stage dram --nbuf 2 $CM4"
  "m4-probe-l2-scp1-abuf3|PASS|0.28 s|--mode tensor $L2 --per-shire 32 --probe narrow:2000 --oracle on --stage scp --nbuf 1 $CM4D"
  "m4-probe-c1-scp1|PASS|5 ms|--mode tensor $C1 --seed 1 --per-shire 32 --probe narrow:200 --oracle on --stage scp --nbuf 1 $CM4"
  "m4-probe-c1-dram1|PASS|7 ms|--mode tensor $C1 --seed 1 --per-shire 32 --probe narrow:200 --oracle on --stage dram --nbuf 1 $CM4"
  "m4-1s-l1-w-m1|PASS|1.12 s|$ONE $L1 --slice 0/3 --slice-cost m1 $CM1"
  "m4-1s-l1-w-a|PASS|1.11 s|$ONE $L1 --slice 0/3 --slice-cost m1 $CA"
  "m4-1s-l1-w-m4|PASS|0.69 s|$ONE $L1 --slice 0/3 --slice-cost m1 $CM4"
  "m4-1s-l1-w-m4d|PASS|0.59 s|$ONE $L1 --slice 0/3 --slice-cost m1 $CM4D"
  "m4-1s-l1-n-m1|PASS|2.48 s|$ONE $L1 --slice 2/3 --slice-cost m1 $CM1"
  "m4-1s-l1-n-a|PASS|1.92 s|$ONE $L1 --slice 2/3 --slice-cost m1 $CA"
  "m4-1s-l1-n-m4|PASS|1.25 s|$ONE $L1 --slice 2/3 --slice-cost m1 $CM4"
  "m4-1s-l1-n-m4d|PASS|1.20 s|$ONE $L1 --slice 2/3 --slice-cost m1 $CM4D"
  "m4-1s-l2-w-m1|PASS|1.50 s|$ONE $L2 --slice 0/8 --slice-cost m1 $CM1"
  "m4-1s-l2-w-a|PASS|1.48 s|$ONE $L2 --slice 0/8 --slice-cost m1 $CA"
  "m4-1s-l2-w-m4|PASS|1.18 s|$ONE $L2 --slice 0/8 --slice-cost m1 $CM4"
  "m4-1s-l2-w-m4d|PASS|1.01 s|$ONE $L2 --slice 0/8 --slice-cost m1 $CM4D"
  "m4-1s-l2-n-m1|PASS|2.71 s|$ONE $L2 --slice 15/16 --slice-cost m1 $CM1"
  "m4-1s-l2-n-a|PASS|2.52 s|$ONE $L2 --slice 15/16 --slice-cost m1 $CA"
  "m4-1s-l2-n-m4|PASS|1.66 s|$ONE $L2 --slice 15/16 --slice-cost m1 $CM4"
  "m4-1s-l2-n-m4d|PASS|1.59 s|$ONE $L2 --slice 15/16 --slice-cost m1 $CM4D"
  "m4-32s-l1-m1|PASS|207 ms|$ALL $L1 $CM1"
  "m4-32s-l1-a|PASS|134 ms|$ALL $L1 $CA"
  "m4-32s-l1-b|PASS|113 ms|$ALL $L1 $CB"
  "m4-32s-l1-c|PASS|110 ms|$ALL $L1 $CC"
  "m4-32s-l1-m4|PASS|86 ms|$ALL $L1 $CM4"
  "m4-32s-l1-m4d|PASS|78 ms|$ALL $L1 $CM4D"
  "m4-32s-l2-m1|PASS|835 ms|$ALL $L2 $CM1"
  "m4-32s-l2-a|PASS|545 ms|$ALL $L2 $CA"
  "m4-32s-l2-b|PASS|427 ms|$ALL $L2 $CB"
  "m4-32s-l2-c|PASS|520 ms|$ALL $L2 $CC"
  "m4-32s-l2-m4|PASS|403 ms|$ALL $L2 $CM4"
  "m4-32s-l2-m4d|PASS|362 ms|$ALL $L2 $CM4D"
  "m4-32s-l2-m4a|PASS|545 ms|$ALL $L2 $CM4A"
  "m4-32s-f5-h0-m1|PASS|1.30 s|$ALL $F5 --slice 0/2 --slice-cost m1 $CM1"
  "m4-32s-f5-h0-m4|PASS|0.83 s|$ALL $F5 --slice 0/2 --slice-cost m1 $CM4"
  "m4-32s-f5-h0-m4d|PASS|0.76 s|$ALL $F5 --slice 0/2 --slice-cost m1 $CM4D"
  "m4-32s-f5-h1-m1|PASS|2.55 s|$ALL $F5 --slice 1/2 --slice-cost m1 $CM1"
  "m4-32s-f5-h1-m4|PASS|1.41 s|$ALL $F5 --slice 1/2 --slice-cost m1 $CM4"
  "m4-32s-f5-h1-m4d|PASS|1.34 s|$ALL $F5 --slice 1/2 --slice-cost m1 $CM4D"
  "m4-32s-f5-m4|PASS|2.25 s|$ALL $F5 $CM4 --trust-model"
)
# The gates of a step that runs with --trust-model: each must have run in this --out directory within x1.3 of its
# model (review of M4, finding 1: M4's constants are predictions until the card measures them).
declare -A GATE=([m4-32s-f5-m4]="m4-32s-f5-h0-m4 m4-32s-f5-h1-m4")
# Full-coverage M4 steps that also get the full oracle offline, at the end of the stage (review of M4, finding 4).
VERIFY_FULL=" m4-32s-l1-m4 m4-32s-l1-m4d m4-32s-l2-m4 m4-32s-l2-m4d m4-32s-f5-m4 "
# The generation probe (the analysis' open question): 32 minions x 400 one-column-tile row tiles, timing only, so the
# pipeline runs at hart 1's pace; M1's generation, the incremental one, and the incremental one with its staged stores
# sent to hart 1's own L1 instead (hart 0 then multiplies stale rows: timing only). Cycles per row tile =
# kernel.cycles_max / 400; at k = 4 (L1, L2) and k = 5 (F5).
GP="--mode tensor --shires 0x1 --per-shire 32 --probe narrow:400 --timing-only --variant m1"
M4GEN=(
  "m4gen-l1-m1|TIMING|23 ms|$GP $L1"
  "m4gen-l1-inc|TIMING|14 ms|$GP $L1 --gen inc"
  "m4gen-l1-nostore|TIMING|14 ms|$GP $L1 --gen inc --gen-probe nostore"
  "m4gen-l2-m1|TIMING|92 ms|$GP $L2"
  "m4gen-l2-inc|TIMING|57 ms|$GP $L2 --gen inc"
  "m4gen-l2-nostore|TIMING|57 ms|$GP $L2 --gen inc --gen-probe nostore"
  "m4gen-f5-m1|TIMING|111 ms|$GP $F5"
  "m4gen-f5-inc|TIMING|61 ms|$GP $F5 --gen inc"
  "m4gen-f5-nostore|TIMING|61 ms|$GP $F5 --gen inc --gen-probe nostore"
)
# M5 (README.md, "M5: the two-stage screen"): stage 1 on the first m1 samples with variant b (M4 on a card: the best),
# whose epilogue logs every candidate with c1 >= tau1; the host reads the logs back in one copy and rescores the
# survivors on all m samples with 6 threads (stage 2). (m1, tau1) keep the secret with P(loss) < 1e-4 (exact binomial
# tails, design_model.py screen_at) at the fewest modelled seconds: L1 320/66 (P(loss) 8.8e-5, 3.8e5 survivors), L2
# and (256,5) 1152/106 (8.9e-5; 2.8e6 and 8.7e6). m1 <= 192 (A resident) cannot reach 1e-4 at eta = 0.4 with fewer
# survivors than candidates (tau1 = -12 keeps 83% of them), so its step is L1's, as a measurement of the resident
# regime at P(loss) 1.8e-3. Expect S2 = PASS and stage 2's answer the secret, unique; OVF = the survivor logs overflow
# (--surv-cap 8): flagged, the run fails, every other check passes; NEGT = --perturb tau, the kernel screens at
# tau1 + 2 while the host checks tau1: it misses survivors, and the survivor oracle (on every minion, --oracle on) must
# say MISMATCH while stage 1's checks and stage 2 pass (the proof that the survivor checks catch a missed survivor);
# LOST = --perturb lostlog, the kernel logs into a spare area and the host reads the log area it poisoned (all-ones)
# before the launch, as if no log line reached DRAM: the entries, their oracle and stage 2 must fail (the proof that
# the poisoning works on the card). An S2 step on 1,024 minions checks its survivors in-process on a sample of
# minions only: its S2 is provisional until the full oracle offline (at the end of the stage) confirms it.
# "model" is the host's model_solve_s: stage 1's kernel (variant b's fitted model with the screen's assumed cost) +
# the log's readback + stage 2 (--dry prints it).
M5=(
  "m5-1s-small|S2|70 ms|$ONE --n 128 --k 4 --eta 0.4 --m 1850 --seed 1 --m1 1152 --tau1 60 --oracle on $CB"
  "m5-ovf|OVF|0.16 s|$ONE $L1 --slice 0/16 --slice-cost m1 --m1 320 --tau1 66 --surv-cap 8 $CB"
  "m5-negmask|NEGM|15 ms|$ONE $C1 --seed 1 --m1 128 --tau1 24 --perturb mask $CB"
  "m5-negtau|NEGT|70 ms|$ONE --n 128 --k 4 --eta 0.4 --m 1850 --seed 1 --m1 1152 --tau1 60 --oracle on --perturb tau $CB"
  "m5-lostlog|LOST|70 ms|$ONE --n 128 --k 4 --eta 0.4 --m 1850 --seed 1 --m1 1152 --tau1 60 --oracle on --perturb lostlog $CB"
  "m5-l1-b|PASS|113 ms|$ALL $L1 $CB"
  "m5-l1-s320|S2|101 ms|$ALL $L1 --m1 320 --tau1 66 $CB"
  "m5-l1-res192|S2|127 ms|$ALL $L1 --m1 192 --tau1 40 $CB"
  "m5-l2-b|PASS|427 ms|$ALL $L2 $CB"
  "m5-l2-s1152|S2|262 ms|$ALL $L2 --m1 1152 --tau1 106 $CB"
  "m5-f5-s1152|S2|1.22 s|$ALL $F5 --m1 1152 --tau1 106 $CB"
)
# Full-coverage M5 steps that also get the full oracle offline (every minion's survivor list, entry by entry), at
# the end of the stage (no device).
VERIFY_FULL5=" m5-l1-s320 m5-l1-res192 m5-l2-s1152 m5-f5-s1152 "
case "$WHAT" in m1) STEPS=("${M1[@]}") ;; probe) STEPS=("${PROBE[@]}") ;; m2) STEPS=("${M2[@]}") ;; m4) STEPS=("${M4[@]}") ;;
  m4gen) STEPS=("${M4GEN[@]}") ;; m5) STEPS=("${M5[@]}"); VERIFY_FULL=$VERIFY_FULL5 ;;
  list) STEPS=("${M1[@]}" "${PROBE[@]}" "${M2[@]}" "${M4[@]}" "${M4GEN[@]}" "${M5[@]}") ;; esac
if [ "$WHAT" = list ]; then
  for c in "${STEPS[@]}"; do IFS='|' read -r n e t a <<< "$c"; printf '%-22s %-6s %-7s %s\n' "$n" "$e" "$t" "$a"; done
  exit 0
fi
mkdir -p "$OUT"
"$SELFTEST" --tie-instance "$OUT/tie.spi" > /dev/null || { echo "cannot write the tie instance" >&2; exit 2; }

say() { echo "$(date +%T) $*" | tee -a "$OUT/summary.txt"; }
card_free() {   # 0 when nobody holds a card node or lock (et-who --check: 0 free, 1 held, 2 failed)
  command -v et-who > /dev/null || return 0
  et-who --check > /dev/null 2>&1
}
[ -z "$DRY" ] && command -v et-lab-manifest > /dev/null && et-lab-manifest > "$OUT/manifest.txt" 2>&1
say "sparseparity card_run $WHAT on $H ($([ -n "$DRY" ] && echo 'DRY: no device' || echo "lock $LOCK${ET_DEVICES:+, ET_DEVICES=$ET_DEVICES}")), out $OUT"
OBJCOPY=objcopy; [ -x /opt/et/bin/riscv64-unknown-elf-objcopy ] && OBJCOPY=/opt/et/bin/riscv64-unknown-elf-objcopy
$OBJCOPY -O binary -j .text "$BUILD/kernel/sparseparity.elf" "$OUT/kernel.text" 2> /dev/null
say "kernel $BUILD/kernel/sparseparity.elf: .text sha256 $(sha256sum < "$OUT/kernel.text" | cut -c1-64)"
started=${FROM:+0}; started=${started:-1}
DEFER=(); SKIPPED=()
for c in "${STEPS[@]}"; do
  IFS='|' read -r name expect model args <<< "$c"
  [ "$started" = 0 ] && { [ "$name" = "$FROM" ] && started=1 || continue; }
  rm -f "$OUT/$name.fast"
  if [ -z "$DRY" ] && [ -n "${GATE[$name]:-}" ]; then
    missing=
    for g in ${GATE[$name]}; do [ -f "$OUT/$g.fast" ] || missing="$missing $g"; done
    if [ -n "$missing" ]; then
      say "SKIP $name: its guard trusts M4's predicted model (--trust-model), and not every gate ran within x1.3 of its model in $OUT:$missing (run the gates with --out $OUT first, or refit the constants and pass --pipe-set)"
      SKIPPED+=("$name")
      continue
    fi
  fi
  if [ -z "$DRY" ]; then
    waited=0
    until card_free; do
      [ $waited -ge 300 ] && { say "STOP: the card is held (et-who) for 5 minutes before $name"; exit 3; }
      sleep 10; waited=$((waited + 10))
    done
    # shellcheck disable=SC2086
    flock -n "$LOCK" timeout 10 "$HOST_BIN" $args --records-out "$OUT/$name.rec" > "$OUT/$name.json" 2> "$OUT/$name.err" < /dev/null
    rc=$?
  else
    # shellcheck disable=SC2086
    "$HOST_BIN" --dry $args > "$OUT/$name.json" 2> "$OUT/$name.err" < /dev/null
    rc=$?
  fi
  grep -v '^I20' "$OUT/$name.err" > "$OUT/$name.err.txt" 2> /dev/null; mv -f "$OUT/$name.err.txt" "$OUT/$name.err"
  verdict=$(python3 - "$OUT/$name.json" "$expect" "$rc" "${DRY:-0}" "$OUT/$name.fast" <<'EOF'
import json, sys
path, expect, rc, dry, fast = sys.argv[1], sys.argv[2], int(sys.argv[3]), sys.argv[4] == "1", sys.argv[5]
try:
    j = json.loads(open(path).read().strip().splitlines()[-1])
except Exception:
    print("BAD no JSON line (rc %d)" % rc); sys.exit()
st = j.get("status", "NONE")
if dry:
    ok = st == "DRY" and not j.get("refused_on_silicon")
    ts = j.get("two_stage") or {}
    tss = (f" two-stage m1 {ts.get('m1')} tau1 {ts.get('tau1')} P(loss) {ts.get('p_loss', 0):.2g} survivors "
           f"{ts.get('expected_survivors', 0):.3g} log {ts.get('log_mb', 0):.0f} MB readback {ts.get('readback_est_s', 0):.3f} s "
           f"stage2 {ts.get('stage2_est_s', 0):.3f} s solve {ts.get('model_solve_s', 0):.3g} s") if ts else ""
    print(("OK " if ok else "BAD ") + f"DRY model {j.get('model_s', 0):.3g} s est {j.get('est_s', 0):.3g} s "
          f"fallback {j.get('model_fallback_s', 0):.3g} s guard {j.get('guard_s', 0):.3g} s "
          f"stage {j.get('stage')} nbuf {j.get('nbuf')} scp {j.get('scp_layout_kb')} KB coverage {j.get('coverage')}{tss}")
    sys.exit()
c, res, k, pl = j.get("checks", {}), j.get("result", {}), j.get("kernel", {}), j.get("plan", {})
# the launch against the host's model: x1.3 is the margin the guard gives an M4 change (x1.15 M1's kernel)
ls = j.get("launch_s") or [0]
ratio = ls[0] / pl["model_s"] if pl.get("model_s") else 0.0
margin = 1.15 if j.get("m4", {}).get("kernel") == "m1" else 1.3
speed = f"x{ratio:.2f} of model{' SLOW' if ratio > margin else ''}"
ts = j.get("two_stage") or {}
if expect in ("PASS", "TIMING"):
    ok = rc == 0 and st == expect
elif expect == "S2":  # M5: PASS (survivors, their oracle, stage 2) and stage 2's answer the secret, unique
    ok = (rc == 0 and st == "PASS" and ts.get("solved") is True and c.get("survivors", "").startswith("ok")
          and c.get("stage2", "").startswith("ok"))
elif expect == "NEGT":  # M5: the kernel screened at tau1 + 2: the survivor oracle catches the missed survivors,
    # everything else holds (the per-minion count check may also fire: COUNT)
    ok = (st == "FAIL" and c.get("survivors_oracle", "").startswith("MISMATCH") and c.get("records") == "ok"
          and c.get("launch") == "ok" and c.get("count") == "ok" and c.get("sum_c") == "ok" and c.get("sum_c2") == "ok"
          and c.get("oracle", "").startswith("exact") and c.get("stage2", "").startswith("ok")
          and c.get("survivors", "").split(" ")[0].rstrip(",") in ("ok", "COUNT"))
elif expect == "LOST":  # M5: the log area read back holds only the poison: entries, their oracle and stage 2 fail
    ok = (st == "FAIL" and c.get("survivors", "").startswith("MISMATCH") and c.get("survivors_oracle", "").startswith("MISMATCH")
          and c.get("stage2", "").startswith("MISMATCH") and c.get("records") == "ok" and c.get("launch") == "ok"
          and c.get("count") == "ok" and c.get("sum_c") == "ok" and c.get("sum_c2") == "ok"
          and c.get("oracle", "").startswith("exact"))
elif expect == "OVF":  # M5: the logs overflow: flagged and failed, every other check passes
    ok = (st == "FAIL" and c.get("survivors", "").startswith("OVERFLOW") and c.get("records") == "ok"
          and c.get("launch") == "ok" and c.get("count") == "ok" and "MISMATCH" not in c.get("oracle", "")
          and "MISMATCH" not in c.get("survivors_oracle", ""))
elif expect == "TIE":
    ok = rc == 0 and st == "PASS" and res.get("unique") is False
elif expect == "NEGM":
    ok = (st == "FAIL" and c.get("count") == "ok" and c.get("sum_c") == "MISMATCH" and c.get("sum_c2") == "MISMATCH"
          and c.get("records") == "ok" and c.get("launch") == "ok")
else:  # NEG
    ok = (st == "FAIL" and c.get("count") == "ok" and "MISMATCH" in c.get("sum_c", "") + c.get("sum_c2", "")
          and c.get("records") == "ok" and c.get("launch") == "ok")
if ok and expect == "PASS" and 0 < ratio <= 1.3:
    open(fast, "w").write(f"{ratio:.4f}\n")   # a gate for a step that trusts the model
s2note = ""
if ok and expect == "S2":  # the survivor oracle on every minion in-process, or only on a sample (provisional)
    s2note = (" [S2 confirmed in-process: the survivor oracle covered every minion]" if "all " in c.get("oracle", "")
              else " [S2 PROVISIONAL: the survivor oracle sampled minions; the full oracle offline decides]")
print(("OK " if ok else "BAD ") + f"{st} launch_s {j.get('launch_s')} {speed} open_s {j.get('open_s', 0):.2f} "
      f"cyc/op {k.get('cycles_per_op_busiest', 0):.1f} MHz {k.get('clock_mhz_est', 0):.0f} "
      f"cyc max/med {k.get('cycles_max', 0)}/{k.get('cycles_median', 0):.0f} wait {k.get('wait_cycles_max')} "
      f"solved {res.get('solved')} unique {res.get('unique')} sum_c {c.get('sum_c')} sum_c2 {c.get('sum_c2')} "
      f"oracle '{c.get('oracle')}' coverage {j.get('plan', {}).get('coverage')} "
      f"stage {j.get('plan', {}).get('stage')}/{j.get('plan', {}).get('nbuf')} scp_kb_device "
      f"{j.get('plan', {}).get('scp_kb_device')} problems {j.get('problems')}"
      + (f" | two-stage found {ts.get('found')} (x{ts.get('found_over_expected', 0):.3f} of expected) overflow "
         f"{ts.get('overflow_minions')} readback {ts.get('readback_s', 0):.4f} s stage2 {ts.get('stage2_s', 0):.4f} s "
         f"solve {ts.get('solve_s', 0):.4f} s (model {ts.get('model_solve_s', 0):.4f}) answer {ts.get('answer')} "
         f"solved {ts.get('solved')} secret survived {ts.get('secret_survived')} survivors '{c.get('survivors')}' "
         f"oracle '{c.get('survivors_oracle')}' stage2 '{c.get('stage2')}' poison {ts.get('poison_s', 0):.4f} s" if ts else "")
      + s2note)
EOF
)
  say "$name [$expect, model $model] $verdict"
  if [ "${verdict%% *}" != OK ]; then
    say "STOP at $name: not the expected result; see $OUT/$name.json and $OUT/$name.err (resume: --from $name)"
    exit 1
  fi
  # the offline value check of a partial plan: the full oracle on the saved records (no device)
  if [ -z "$DRY" ] && [ "$expect" = PASS ] && grep -q '"coverage":"partial"' "$OUT/$name.json" && \
     ! grep -q '"oracle":"exact, all' "$OUT/$name.json"; then
    # shellcheck disable=SC2086
    nice -n 10 "$HOST_BIN" $args --verify-records "$OUT/$name.rec" > "$OUT/$name.verify.json" 2> /dev/null
    v=$(python3 -c 'import json,sys; j=json.loads(open(sys.argv[1]).read().splitlines()[-1]); print(j["status"], j["checks"]["oracle"])' "$OUT/$name.verify.json" 2> /dev/null)
    say "  $name offline verify: $v"
    [ "${v%% *}" = PASS ] || { say "STOP at $name: the offline oracle disagrees (resume: --from $name)"; exit 1; }
  fi
  [ -z "$DRY" ] && { [ "$expect" = PASS ] || [ "$expect" = S2 ]; } && [[ "$VERIFY_FULL" == *" $name "* ]] && DEFER+=("$name|$args")
done
# The full oracle offline on the full-coverage M4 steps (no device; about 1 s per 1.4e9 units of oracle work, one
# thread: L1 ~40 s, L2 ~85 s, (256,5) ~5 min).
vbad=0
for d in "${DEFER[@]}"; do
  IFS='|' read -r name args <<< "$d"
  # shellcheck disable=SC2086
  nice -n 10 "$HOST_BIN" $args --verify-records "$OUT/$name.rec" > "$OUT/$name.verify.json" 2> /dev/null
  v=$(python3 -c 'import json,sys; j=json.loads(open(sys.argv[1]).read().splitlines()[-1]); c=j["checks"]; print(j["status"], c["oracle"], ("survivors: " + c["survivors_oracle"]) if c.get("survivors_oracle", "n/a") != "n/a" else "")' "$OUT/$name.verify.json" 2> /dev/null)
  say "  $name offline verify (full oracle): $v"
  [ "${v%% *}" = PASS ] || vbad=1
done
# M5's survivor logs (<step>.rec.surv: 64 KB of headers, then the stored entries: 20-70 MB per step), once the offline
# oracle has read them: each kept gzipped (gunzip -k before another --verify-records), with its sha256 and its headers
# alone (<step>.rec.surv.hdr.gz, a few KB), which are what goes into the repository, never the log itself.
for f in "$OUT"/*.rec.surv; do
  [ -f "$f" ] || continue
  (cd "$OUT" && sha256sum "$(basename "$f")") > "$f.sha256"
  head -c 65536 "$f" | gzip -9 > "$f.hdr.gz"
  nice -n 19 gzip -f -1 "$f"
done
[ $vbad = 0 ] || { say "STOP: an offline oracle disagrees with a full-coverage step (see its .verify.json)"; exit 1; }
[ ${#DEFER[@]} -gt 0 ] && [ "$WHAT" = m5 ] && say "S2 confirmed by the full oracle offline: $(for d in "${DEFER[@]}"; do printf '%s ' "${d%%|*}"; done)"
if [ ${#SKIPPED[@]} -gt 0 ]; then say "DONE $WHAT: every step run as expected; skipped (gates): ${SKIPPED[*]}"; exit 0; fi
say "DONE $WHAT: every step as expected"
