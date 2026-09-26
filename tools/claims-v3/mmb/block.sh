#!/usr/bin/env bash
# V3-MMB, one pass on the local card (docs/reports/data/2026-09-25-claims-v3/PLAN3.md, section V3-MMB):
#   bash tools/claims-v3/mmb/block.sh <pass> [--smoke]
# A pass, in order: smoke checks (the four mmbench-check launches, it_test_code_loading); E1 (the four mmbench
# workloads, one invocation each in the pass's registered order, each inside its own ettelem sampler); ridge-X1
# (private and shared tile pools per mode, in the pass's registered mode order); pt X1 (the E5 load step).
# A governor-free card (lib.sh GOV_FREE: aifoundry2, aifoundry1-c0, aifoundry1-c1) heats the die to >= HEAT_C before
# each E1 workload, before ridge-X1 and before the load step; the pinned card (aifoundry3) sleeps 60 s before the load
# step. On aifoundry1 set V3_DEVICE=0|1 (lib.sh). Everything is in tools/claims-v3/mmb/README.md ("Four cards").
# --smoke: the smallest real check of every component (about 45 s of card time), into mmb-smoke/p<pass>.
set -u
. "$(dirname "${BASH_SOURCE[0]}")/../lib.sh"      # cd's to the tree root; CARD, DATA_ROOT, binaries, helpers
others_present && exit 3

PASS=${1:?usage: block.sh <pass> [--smoke]}
SMOKE=; [ "${2:-}" = --smoke ] && SMOKE=1
case "$PASS" in ''|*[!0-9]*|0) echo "pass must be a positive integer" >&2; exit 2 ;; esac
HERE=$V3_ROOT/tools/claims-v3/mmb
MMB_LAUNCHER=$MMBENCH_DIR/build/launchers/mmbench_launcher
MMB_KERNEL=$MMBENCH_DIR/build/kernels/nekko/mmbench.elf
DRAM_TBL=$V3_ROOT/build/memprobe-data/dram_seq.tbl
IT_TEST=/opt/et/bin/it_test_code_loading
MEMPROBE_ABS=$V3_ROOT/$MEMPROBE
# Per-card parameters (README "Four cards"). The heat target is aifoundry2's registered 76 C on every governor-free
# card: aifoundry1's cards have the same software threshold (65 C) and TDP (65 W), so the same margin above it applies.
HEAT_C=76
if [ -n "$GOV_FREE" ]; then GF01=1; else GF01=0; fi

# The registered orders (PLAN3 V3-MMB "Order"); a pass number above 4 (a re-run numbered anew) reuses them cyclically.
case $(( (PASS - 1) % 4 + 1 )) in
  1) E1_ORDER="fp32-tensor-L2 fp16-tensor-L2 int8-tensor-L2 fp32-tensor-DRAM"; X1_ORDER="fp32 fp16 int8" ;;
  2) E1_ORDER="fp32-tensor-DRAM int8-tensor-L2 fp16-tensor-L2 fp32-tensor-L2"; X1_ORDER="int8 fp16 fp32" ;;
  3) E1_ORDER="int8-tensor-L2 fp32-tensor-L2 fp32-tensor-DRAM fp16-tensor-L2"; X1_ORDER="fp16 int8 fp32" ;;
  4) E1_ORDER="fp16-tensor-L2 fp32-tensor-DRAM fp32-tensor-L2 int8-tensor-L2"; X1_ORDER="fp32 int8 fp16" ;;
esac
if [ -n "$SMOKE" ]; then E1_ORDER="fp32-tensor-L2"; X1_ORDER="int8"; fi

# Everything the pass needs must exist before the card is touched (no block.json is written: the queue re-runs it).
missing=
for f in "$MMB_LAUNCHER" "$MMB_KERNEL" "$MEMPROBE_ABS" "$DRAM_TBL" "$ETTELEM" scripts/mmbench-report-data.py; do
  [ -e "$f" ] || missing="$missing $f"
done
[ -n "$GOV_FREE" ] && { [ -e "$HEATER" ] || missing="$missing $HEATER"; }
if [ -n "$missing" ]; then
  if [ -n "${V3_DRY:-}" ]; then log "DRY: missing (a real run would stop here):$missing"
  else log "mmb: missing:$missing"; exit 2; fi
fi

if [ -n "$SMOKE" ]; then block_begin mmb-smoke "$PASS"; else block_begin mmb "$PASS"; fi
# V3_DRY: print every device command on the block's own stderr (fd 8), also from calls whose output goes to files.
# A local override of lib.sh's dry hold10 (which prints to the redirected stderr); the real hold10 is untouched.
# Not fd 9: block_begin holds the machine's card lock (/run/lock/etsoc-shire<n>.lock) on fd 9 until the block exits,
# and redirecting fd 9 would close it and release the lock for the rest of the block.
exec 8>&2
if [ -n "${V3_DRY:-}" ]; then hold10() { echo "DRY hold10: $* (cwd $PWD)" >&8; }; fi
RUN=$OUT/run; mkdir -p "$RUN"
REASONS=
note() { log "$*"; REASONS="$REASONS${REASONS:+; }$*"; }
nap() { if [ -n "${V3_DRY:-}" ]; then echo "DRY sleep $1" >&2; else sleep "$1"; fi; }
mark() { echo "{\"t_ms\":$(now_ms),\"phase\":\"$1\"}" >> "$2"; }
# a launcher process in the run directory (it writes an 8 MB trace dump into its working directory)
mmb() { ( cd "$RUN" && hold10 "$MMB_LAUNCHER" -k "$MMB_KERNEL" -d silicon "$@" ); }
json_list() { printf '"%s",' "$@" | sed 's/,$//'; }
clock_json() {  # die temperature and minion clock, 1 s sample each (only while no sampler runs)
  local c m; c=$(die_c); m=$(clock_mhz)
  echo "{\"t_ms\":$(now_ms),\"at\":\"$1\",\"die_c\":${c:-null},\"mhz_minion\":${m:-null}}"
}
# The card's idle state (four cards: aifoundry1-c0 idles at 300 MHz in a low_power state): the firmware's view from
# `ettelem config` (one read-only query: TDP, threshold, power_state, minion MHz and mV) plus clock_json's readings.
# Only while no sampler runs. Under V3_DRY nothing is queried.
state_json() {
  local cfg c m
  if [ -n "${V3_DRY:-}" ]; then cfg='{"dry":true}'; echo "DRY ettelem config" >&8
  else cfg=$(timeout 20 "$ETTELEM" config 2>/dev/null < /dev/null | grep '^{' | tail -1); fi
  c=$(die_c); m=$(clock_mhz)
  echo "{\"t_ms\":$(now_ms),\"at\":\"$1\",\"config\":${cfg:-null},\"die_c\":${c:-null},\"mhz_minion\":${m:-null}}"
}
SMOKE_JSON=false; [ -n "$SMOKE" ] && SMOKE_JSON=true
# shellcheck disable=SC2086
printf '{"pass":%s,"smoke":%s,"card":"%s","gov_free":%s,"device":"%s","heat_c":%s,"e1":[%s],"x1":[%s],"mmbench":"%s","memprobe":"%s"}\n' \
  "$PASS" "$SMOKE_JSON" "$CARD" "$([ "$GF01" = 1 ] && echo true || echo false)" "${V3_DEVICE:-}" "$HEAT_C" \
  "$(json_list $E1_ORDER)" "$(json_list $X1_ORDER)" "$MMB_LAUNCHER" "$MEMPROBE" > "$OUT/order.json"
state_json start >> "$OUT/idle-state.jsonl"   # the idle state before anything runs (before any heating)
sha256sum "$HERE"/*.sh "$HERE"/*.py "$MMB_LAUNCHER" "$MMB_KERNEL" "$MEMPROBE_ABS" "$DRAM_TBL" > "$OUT/code-mmb.sha256" 2>/dev/null

# ---- 1. smoke checks: make mmbench-check DEVICE=silicon's four launches (without its build step) and it_test_code_loading
S=$OUT/smoke; mkdir -p "$S"
# t0_ms/t_ms give each process's wall time: "-n 64 -p" builds the same 256 MB private pools as E1's DRAM workload
for args in "-m fp32" "-m fp16" "-m int8" "-m fp32 -n 64 -i 2 -p"; do
  tag=$(echo "$args" | tr -d ' -'); t0=$(now_ms)
  # shellcheck disable=SC2086
  mmb -s 0xffffffff $args > "$S/check-$tag.out" 2> "$S/check-$tag.err"; rc=$?
  echo "{\"test\":\"mmbench-check\",\"args\":\"$args\",\"rc\":$rc,\"t0_ms\":$t0,\"t_ms\":$(now_ms)}" >> "$S/smoke.jsonl"
done
t0=$(now_ms)
if [ -x "$IT_TEST" ] || [ -n "${V3_DRY:-}" ]; then
  ( cd "$RUN" && hold10 "$IT_TEST" --mode=pcie ) > "$S/it_test_code_loading.log" 2>&1; rc=$?
else
  echo "$IT_TEST not found" > "$S/it_test_code_loading.log"; rc=127
fi
echo "{\"test\":\"it_test_code_loading\",\"args\":\"--mode=pcie\",\"rc\":$rc,\"t0_ms\":$t0,\"t_ms\":$(now_ms)}" >> "$S/smoke.jsonl"
if [ -n "$SMOKE" ] && [ -n "$GOV_FREE" ]; then   # the heater binary itself, one 1 s launch
  hold10 "$HEATER" --test fma --type fp32 --pattern none --values randn --shires 0xffffffff --per-shire 32 \
    --seconds 1 --seed 1 > "$S/heater.out" 2>&1; echo "{\"test\":\"heater\",\"rc\":$?,\"t_ms\":$(now_ms)}" >> "$S/smoke.jsonl"
fi

# ---- 2. E1: one mmbench_power_v3.py invocation per workload, each inside its own sampler
if [ -n "$SMOKE" ]; then E1_ARGS="--idle 2 --seconds 1 --gap 1"; else E1_ARGS="--seconds 6"; fi
for w in $E1_ORDER; do
  d=$OUT/e1/$w; mkdir -p "$d"
  if [ -n "$GOV_FREE" ] && [ -z "$SMOKE" ]; then heat_to $HEAT_C "$d/heat.jsonl" || note "heat_to $HEAT_C gave up before $w"; fi
  if ! start_sampler "$d/telemetry.jsonl" 90; then note "sampler did not start: e1 $w skipped"; continue; fi
  # shellcheck disable=SC2086
  e1run() { python3 "$HERE/mmbench_power_v3.py" run --root "$V3_ROOT" --launcher "$MMB_LAUNCHER" \
              --kernel "$MMB_KERNEL" --only "$w" $E1_ARGS --out "$d" --rundir "$RUN"; }
  if [ -n "${V3_DRY:-}" ]; then e1run > "$d/run.log" 2>&8   # dry: the runner's DRY lines on the block's stderr
  else e1run > "$d/run.log" 2>&1; fi || note "e1 $w: runner failed"
  stop_sampler
  python3 "$HERE/mmbench_power_v3.py" finish --out "$d" --telemetry "$d/telemetry.jsonl" --card "$CARD" \
    --gov-free $GF01 >> "$d/run.log" 2>&1
  [ -s "$d/results.json" ] && python3 scripts/mmbench-report-data.py "$d" > "$d/report.txt" 2>&1
  [ -s "$d/telemetry.jsonl" ] && gzip -f "$d/telemetry.jsonl"
done

# ---- 3. ridge-X1: private tile pools (-p -n 4) and the shared 16-tile control, per mode; cycle counters only
X=$OUT/x1; mkdir -p "$X"
if [ -n "$GOV_FREE" ] && [ -z "$SMOKE" ]; then heat_to $HEAT_C "$X/heat.jsonl" || note "heat_to $HEAT_C gave up before x1"; fi
clock_json before >> "$X/clock.jsonl"
for m in $X1_ORDER; do
  case $m in int8) it=250000 ;; *) it=280000 ;; esac
  r=3; gap=3; [ -n "$SMOKE" ] && { it=$((it / 10)); r=1; gap=1; }
  # the launcher exits 1 when a check fails; the cycle counts stand, so rc is recorded (passcheck: a note) not a re-run
  mmb -m "$m" -n 4 -p -i "$it" -r "$r" -t 4 > "$X/private-$m.out" 2> "$X/private-$m.err"
  echo "{\"kind\":\"private\",\"mode\":\"$m\",\"rc\":$?}" >> "$X/rc.jsonl"
  nap $gap
  mmb -m "$m" -n 16 -i $((it / 4)) -r "$r" -t 4 > "$X/shared-$m.out" 2> "$X/shared-$m.err"
  echo "{\"kind\":\"shared\",\"mode\":\"$m\",\"rc\":$?}" >> "$X/rc.jsonl"
  nap $gap
done
clock_json after >> "$X/clock.jsonl"

# ---- 4. pt X1: the E5 load step of tools/ettelem/run_thermal.sh (same phases, loads and flags), with lib.sh's sampler
T=$OUT/thermal; mkdir -p "$T"
if [ -n "$GOV_FREE" ]; then   # governor free: heat (aifoundry2's registered step); pinned (aifoundry3): sleep 60 s
  [ -z "$SMOKE" ] && { heat_to $HEAT_C "$T/heat.jsonl" || note "heat_to $HEAT_C gave up before the load step"; }
else
  [ -z "$SMOKE" ] && nap 60
fi
if [ -n "$SMOKE" ]; then NMM=1; NDR=1; MMI=20000; MMR=1; DRS=1; I0=2; C1=2; C2=2
else NMM=8; NDR=4; MMI=100000; MMR=5; DRS=6; I0=20; C1=40; C2=22; fi
: > "$T/thermal-phases.jsonl"; : > "$T/thermal-loads.log"
if start_sampler "$T/thermal-telemetry.jsonl" 240; then
  mark idle0 "$T/thermal-phases.jsonl"; nap $I0
  mark matmul "$T/thermal-phases.jsonl"
  for i in $(seq 1 $NMM); do
    mmb -s 0xffffffff -m fp32 -n 16 -i $MMI -r $MMR -t 120 > "$T/mm-$i.out" 2> "$T/mm-$i.err"
    grep '^MMBENCH' "$T/mm-$i.out" | tail -1 >> "$T/thermal-loads.log"
  done
  mark cool1 "$T/thermal-phases.jsonl"; nap $C1
  mark dram "$T/thermal-phases.jsonl"
  for i in $(seq 1 $NDR); do
    hold10 "$MEMPROBE_ABS" --loop --table "$DRAM_TBL" --level 4 --stride 64 --lines 1024 --seconds $DRS \
      > "$T/dram-$i.out" 2> "$T/dram-$i.err"
    grep '^MEMPROBE' "$T/dram-$i.out" | tail -1 >> "$T/thermal-loads.log"
  done
  mark cool2 "$T/thermal-phases.jsonl"; nap $C2
  mark end "$T/thermal-phases.jsonl"
  nap 1
  stop_sampler
  [ -s "$T/thermal-telemetry.jsonl" ] && gzip -f "$T/thermal-telemetry.jsonl"
else
  note "sampler did not start: load step skipped"
fi

# ---- end: completeness and drop rules, tidy, block.json
state_json end >> "$OUT/idle-state.jsonl"      # the idle state after the load step (its sampler has stopped)
python3 "$HERE/passcheck.py" "$OUT" --card "$CARD" --gov-free $GF01 ${SMOKE:+--smoke} > "$OUT/passcheck.json" 2> "$OUT/passcheck.err"
pc=$?
rm -f "$RUN"/traceKernels_*.bin
if [ -n "${V3_DRY:-}" ]; then
  block_end ok "dry run${REASONS:+: $REASONS}"; exit 0
fi
if [ $pc -ne 0 ]; then
  note "rerun: $(grep -c '^RERUN' "$OUT/passcheck.err") reasons in passcheck.err"
fi
if [ -n "$REASONS" ]; then block_end fail "$REASONS"; exit 1; fi
block_end ok "$(grep -c '^NOTE' "$OUT/passcheck.err") notes"
exit 0
