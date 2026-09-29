#!/usr/bin/env bash
# Board energy per solve: one card, one instance, variant b (README "Energy per solve").
#
#   bash workloads/sparseparity/energy.sh <l1|l2|f5h0|f5h1> [--build DIR] [--out DIR] [--reps N] [--target-s S]
#        [--budget S] [--idle-before S] [--idle-after S] [--every-ms M] [--ettelem PATH]
#        [--dry [--real-plan] [--stub-card base|alt]]
#
# Presets (variant b = `--variant m1 --cost fit --gen inc` on 32 shires x 32 minions, the 29 September card runs'
# best): l1 = L1 (512,4,0.3,448), l2 = L2 (512,4,0.4,1850), f5h0 / f5h1 = (256,5,0.4,1925) slice 0/2 / 1/2 (sliced by
# M1's cost, as card_run.sh m4 and data/2026-09-29-aifoundry3-card-m4/f5-b); a whole (256,5) solve is f5h0 + f5h1
# (tools/energy_reduce.py combine, which refuses anything but one instance's slices 0..N-1). Run it from the tree's
# root on the card's host, only with the owner's go-ahead. It refuses aifoundry2 (its DV2 validation treats a
# sampler or a *_host process as foreign) unless SPP_ALLOW_AIFOUNDRY2=1; there only the stubs' --dry runs.
# These are the first card runs with --reps > 1 (L1: 44 launches at 7.3 per second): run l2 (14 launches, or a smoke
# run of `l2 --reps 3`) before l1.
#
# What it does, as the tools/claims-v3 blocks do (lib.sh: the card lock held by the script for the whole run, the
# sampler started with retries and stopped with SIGTERM only, every device process under timeout 10):
#   1. no device: the host's --dry (the plan, its model and guard) and, from its time and the preset's measured launch
#      time, the number of launches that fills --target-s (6 s) and that the host's own --budget rule (9 s from the
#      process's start; each launch needs its whole timeout left) will let it start;
#   2. waits (<= 5 min) until `et-who --check` shows the card free and no other user's device process runs, then takes
#      /run/lock/etsoc-shire<N>.lock on fd 9 (flock -n) and keeps it to the end;
#   3. starts `ettelem sample --every-ms 100` (10 Hz, as lib.sh and the energy catalogue: board_w is held for one SP
#      pass, which a 20 Hz sampler only lengthens, 0.255 -> 0.296 s, E58; the management node, which the rebuilt host
#      no longer opens);
#   4. --idle-before (8 s) of idle; then ONE host process, `timeout 10 sparseparity_host <preset> --reps R`, which runs
#      the solve R times back to back (each launch read back and checked; the last one's records are value-checked:
#      closed forms at full coverage, a sampled oracle), its CPU time measured (bash `times`: every thread, the whole
#      process; the host also reports its own over the burst); then --idle-after (10 s: the rails' 1 s filter needs 6 s);
#   5. stops the sampler (SIGTERM), releases the lock, runs tools/energy_reduce.py: J per solve over idle for the
#      board (the headline: the SP's board average less the leakage law on the measured die temperature, +-3%; the
#      catalogue's method beside it) and each rail, the board total, the host's share (assumed package watts x its CPU
#      time), the CPU ratios (the card's board alone; with the host's package), solves per second, die temperature.
# The host must be a build with the ops-node-only device layer and launch_epoch_ms (host/main.cpp, 29 September):
# the build that ran M4 (build/sparseparity-h) also opens the management node, which the driver lets one process hold
# (EBUSY), so it cannot run under the sampler. Default --build build/sparseparity-t (R4's: the host also reports its
# CPU time over the burst, host_cpu_s); build/sparseparity-i (the kernel that ran M4) runs too, its host's share then
# bounded by the whole process's CPU time.
#
# --dry (or V3_DRY=1): no device, no lock, no et-who wait: the host and the sampler are tools/energy_stub.py's doubles
# (a simulated card in real time), and the reducer checks its result against the energies the doubles injected
# (TRUTH PASS/FAIL). --stub-card base (default) simulates a card with the reducer's own laws: a PLUMBING test;
# --stub-card alt breaks them (another leakage law, 11-thermal-model.md's thermal chain, filter taus and gain, board_w a
# pass late, the idle die on the other side of a half degree, the card's edges off the host's marks): the test of the
# method. The plan also uses the double unless --real-plan (the real host's --dry,
# niced: CPU only, never a device; refused on aifoundry2). Output: --out DIR (default
# build/sparseparity-energy/<host>-<preset>-<time>[-dry]/): run.json (marks), plan.json, host.json, host.err,
# host.rec, host.times, telemetry.jsonl.gz, energy.json, energy.txt, manifest.txt, etwho-{before,after}.txt.
set -u
cd "$(dirname "${BASH_SOURCE[0]}")/../.." || exit 2
ROOT=$PWD
HERE=workloads/sparseparity
WHAT=${1:-}; shift || true
DRY=${V3_DRY:+1}; REAL_PLAN=; BUILD=; OUT=; REPS=; TARGET=6; BUDGET=9; IB=8; IA=10; EVERY=100; ETT=; STUB_CARD=base
while [ $# -gt 0 ]; do
  case "$1" in
    --dry) DRY=1 ;;
    --real-plan) REAL_PLAN=1 ;;
    --build) BUILD=$2; shift ;;
    --out) OUT=$2; shift ;;
    --reps) REPS=$2; shift ;;
    --target-s) TARGET=$2; shift ;;
    --budget) BUDGET=$2; shift ;;
    --idle-before) IB=$2; shift ;;
    --idle-after) IA=$2; shift ;;
    --every-ms) EVERY=$2; shift ;;
    --ettelem) ETT=$2; shift ;;
    --stub-card) STUB_CARD=$2; shift ;;
    *) echo "unknown option $1" >&2; exit 2 ;;
  esac
  shift
done
ALL="--mode tensor --shires 0xffffffff --per-shire 32"
CB="--variant m1 --cost fit --gen inc"                 # variant b (card_run.sh CB)
case "$WHAT" in
  l1)   INST="--n 512 --k 4 --eta 0.3 --m 448 --seed 1";  SLICE=;                             EST=0.130 ;;
  l2)   INST="--n 512 --k 4 --eta 0.4 --m 1850 --seed 1"; SLICE=;                             EST=0.429 ;;
  f5h0) INST="--n 256 --k 5 --eta 0.4 --m 1925 --seed 1"; SLICE="--slice 0/2 --slice-cost m1"; EST=0.958 ;;
  f5h1) INST="--n 256 --k 5 --eta 0.4 --m 1925 --seed 1"; SLICE="--slice 1/2 --slice-cost m1"; EST=1.589 ;;
  *) echo "usage: $0 <l1|l2|f5h0|f5h1> [--build DIR] [--out DIR] [--reps N] [--target-s S] [--budget S]" \
          "[--idle-before S] [--idle-after S] [--every-ms M] [--ettelem PATH] [--dry [--real-plan] [--stub-card base|alt]]" >&2; exit 2 ;;
esac
case "$STUB_CARD" in base|alt) ;; *) echo "--stub-card base|alt" >&2; exit 2 ;; esac
# aifoundry2: its DV2 validation treats ettelem, a *_host process or a device node held as foreign; only the stubs run
if [ "$(hostname)" = aifoundry2 ] && [ "${SPP_ALLOW_AIFOUNDRY2:-}" != 1 ] && { [ -z "$DRY" ] || [ -n "$REAL_PLAN" ]; }; then
  echo "aifoundry2: refused (DV2 validation; only --dry with the stubs runs here, or set SPP_ALLOW_AIFOUNDRY2=1 with the owner's go-ahead)" >&2
  exit 2
fi
ARGS="$ALL $INST $SLICE $CB"
CHECKS="--oracle sample --oracle-work 3e8"             # a value check on the last launch, ~0.2-0.4 s of one core
BUILD=${BUILD:-build/sparseparity-t}
case "$BUILD" in /*) ;; *) BUILD=$ROOT/$BUILD ;; esac
HOST_BIN=$BUILD/host/sparseparity_host
H=$(hostname)
LOCK=/run/lock/etsoc-shire0.lock
if [ "$H" = aifoundry1 ]; then export ET_DEVICES=1; LOCK=/run/lock/etsoc-shire1.lock; fi   # card 0 overheats
OUT=${OUT:-build/sparseparity-energy/$H-$WHAT-$(date +%Y%m%d-%H%M%S)${DRY:+-dry}}
case "$OUT" in /*) ;; *) OUT=$ROOT/$OUT ;; esac
PY=python3; [ -x "$HOME/nekko/.venv/bin/python3" ] && PY=$HOME/nekko/.venv/bin/python3       # numpy (lib.sh's venv)
STUB=("$PY" "$HERE/tools/energy_stub.py")
now_ms() { date +%s%3N; }
say() { echo "$(date +%T) $*" | tee -a "$OUT/energy.log"; }
nap() { sleep "$1"; }

# ---- preflight (files only) ----------------------------------------------------------------------------------------
pf=()
"$PY" -c 'import numpy' 2> /dev/null || pf+=("$PY has no numpy (the reducer)")
if [ -z "$DRY" ]; then
  if [ -z "$ETT" ]; then
    for c in "$ROOT/build/ettelem/ettelem" "$HOME/nekko/build/ettelem/ettelem" "$HOME/claude/et-soc1-prototyping/build/ettelem/ettelem"; do
      [ -x "$c" ] && { ETT=$c; break; }
    done
  fi
  [ -n "$ETT" ] && [ -x "$ETT" ] || pf+=("no ettelem (build/ettelem/ettelem here or in ~/nekko; --ettelem PATH)")
  if [ ! -x "$HOST_BIN" ]; then pf+=("build first: $HOST_BIN")
  else
    if ! grep -a -q 'launch_epoch_ms' "$HOST_BIN"; then
      pf+=("$HOST_BIN predates the ops-node-only host (it opens the management node, which the sampler holds): build these sources into a new directory")
    else
      u=$("$HOST_BIN" --no-such-option 2>&1)       # the usage text only: nothing is opened
      grep -q -- '--variant m4|m1' <<< "$u" || pf+=("$HOST_BIN has no --variant")
    fi
  fi
  command -v et-who > /dev/null || pf+=("no et-who on this host")
fi
if [ ${#pf[@]} -gt 0 ]; then printf 'preflight: %s\n' "${pf[@]}" >&2; exit 2; fi
mkdir -p "$OUT"
if [ -n "$DRY" ]; then
  RUN_HOST=("${STUB[@]}" host --sched "$OUT/stub_sched.jsonl")
  RUN_SAMPLER=("${STUB[@]}" sample --sched "$OUT/stub_sched.jsonl" --truth "$OUT/stub_truth.json" --card "$STUB_CARD")
  if [ -n "$REAL_PLAN" ] && [ -x "$HOST_BIN" ]; then PLAN_HOST=("$HOST_BIN"); else PLAN_HOST=("${STUB[@]}" host); fi
  : > "$OUT/stub_sched.jsonl"
else
  # the host runs in card_run.sh's environment; ettelem (and dev_mngt_service) with /opt/et/lib, as lib.sh gives them
  RUN_HOST=("$HOST_BIN"); RUN_SAMPLER=(env "LD_LIBRARY_PATH=/opt/et/lib" "$ETT" sample); PLAN_HOST=("$HOST_BIN")
fi
say "sparseparity energy $WHAT on $H ($([ -n "$DRY" ] && echo "DRY: test doubles (card $STUB_CARD), no device" || echo "lock $LOCK${ET_DEVICES:+, ET_DEVICES=$ET_DEVICES}")), out $OUT"
KHASH=
if [ -f "$BUILD/kernel/sparseparity.elf" ]; then
  OBJCOPY=objcopy; [ -x /opt/et/bin/riscv64-unknown-elf-objcopy ] && OBJCOPY=/opt/et/bin/riscv64-unknown-elf-objcopy
  KHASH=$($OBJCOPY -O binary -j .text "$BUILD/kernel/sparseparity.elf" /dev/stdout 2> /dev/null | sha256sum | cut -c1-64)
  say "kernel $BUILD/kernel/sparseparity.elf: .text sha256 $KHASH"
fi

# ---- 1. the plan (no device) and the number of launches ------------------------------------------------------------
t0=$(date +%s%N)
# shellcheck disable=SC2086
nice -n 19 "${PLAN_HOST[@]}" --dry $ARGS --budget "$BUDGET" > "$OUT/plan.json" 2> "$OUT/plan.err" < /dev/null
prc=$?; t1=$(date +%s%N)
PLAN=$("$PY" - "$OUT/plan.json" "$(( (t1 - t0) / 1000000 ))" "$EST" "$TARGET" "$BUDGET" "${REPS:-0}" "$prc" <<'EOF'
import json, math, sys
path, dry_ms, est, target, budget, reps_req, rc = sys.argv[1], int(sys.argv[2]), float(sys.argv[3]), \
    float(sys.argv[4]), float(sys.argv[5]), int(sys.argv[6]), int(sys.argv[7])
try:
    j = json.loads([l for l in open(path).read().splitlines() if l.startswith("{")][-1])
except Exception:
    print(f"BAD the host's --dry printed no JSON (rc {rc})"); sys.exit()
if j.get("status") != "DRY" or j.get("refused_on_silicon"):
    print(f"BAD the plan: status {j.get('status')}, refused_on_silicon {j.get('refused_on_silicon')}"); sys.exit()
guard, tmo = float(j["guard_s"]), float(j["timeout_s"])
# the host launches rep r only if floor(min(timeout, budget - elapsed - 0.5)) >= max(1, 1.25 guard + 0.5)
need = math.ceil(max(1.0, 1.25 * guard + 0.5) - 1e-9)
if need > tmo:
    print(f"BAD a launch needs {need} s of timeout, the plan's is {tmo} s"); sys.exit()
last_start = budget - 0.5 - need            # the latest process time at which the host still starts a launch
first = dry_ms / 1000.0 + 0.15 + 0.20        # the plan (as --dry took), a margin, the device open and copy-in
per = est + 0.006                            # a launch and its record clear and readback
fit = max(0, math.floor((last_start - 0.15 - first) / per) + 1)
want = max(1, round(target / per))
reps = reps_req or min(fit, want)
note = "" if reps <= fit else f"; {reps} is over the {fit} the budget allows: the host will stop short"
print(f"OK {reps} {fit} {want} {reps * per:.2f} {first:.2f} {last_start:.2f} {j['model_s']:.4f} {guard:.4f} {tmo:g}|{note}")
EOF
)
case "$PLAN" in OK*) ;; *) say "STOP: $PLAN (see $OUT/plan.json, plan.err)"; exit 2 ;; esac
read -r _ R FIT WANT BURST FIRST LAST MODEL GUARD TMO <<< "${PLAN%%|*}"
say "plan: $R launches of ~${EST} s (budget allows $FIT, target $WANT): burst ~${BURST} s from ~${FIRST} s of the process; the host starts no launch after ${LAST} s (model ${MODEL} s, guard ${GUARD} s, timeout ${TMO} s)${PLAN#*|}"
[ "$R" -ge 1 ] || { say "STOP: no launch fits the budget"; exit 2; }

# ---- 2. the card: free, then locked for the whole run ---------------------------------------------------------------
DEV_COMM='_host$|^sparseparity_ho|^ettelem$|^dev_mngt_servi|^et-powertop$|^mmbench_launch|^sys_emu$|^Runner.Worker$'
foreign() {     # another user's device process, or a node or lock held by another user (et-holders, as lib.sh)
  [ -n "$DRY" ] && return 0
  local p hl=
  p=$(ps -eo uid=,pid=,comm= | awk -v me="$(id -u)" -v re="$DEV_COMM" '$1 != me && $3 ~ re {print $1":"$2":"$3}' | tr '\n' ' ')
  [ -x /usr/local/sbin/et-holders ] && hl=$(sudo -n /usr/local/sbin/et-holders 9>&- 2> /dev/null | grep -v et-holders |
    awk -v me="$USER" '($1 ~ /^\/dev\/et/ || $1 ~ /^lock:/) && $2 != me && $2 != "" {print $1":"$2":"$3}' | tr '\n' ' ')
  printf '%s' "$p$hl" | sed 's/ *$//'
}
ours() {       # our own device processes, except $1 (the sampler)
  ps -eo uid=,pid=,comm= | awk -v me="$(id -u)" -v re="$DEV_COMM" -v skip="${1:-}" '$1 == me && $3 ~ re && $2 != skip {print $2":"$3}' | tr '\n' ' '
}
RAPL_F=/sys/class/powercap/intel-rapl:0/energy_uj
if [ -r "$RAPL_F" ] && cat "$RAPL_F" > /dev/null 2>&1; then RAPL="readable"
elif [ -e "$RAPL_F" ]; then RAPL="root-only ($(stat -c '%a %U' "$RAPL_F"))"; else RAPL="absent"; fi
rapl_uj() { [ "$RAPL" = readable ] && cat "$RAPL_F" 2> /dev/null || echo None; }   # printed into Python below
FOREIGN=
if [ -z "$DRY" ]; then
  o=$(ours); [ -n "$o" ] && { say "STOP: one of our own device processes runs: $o"; exit 3; }
  waited=0
  until et-who --check > "$OUT/etwho-before.txt" 2>&1 && [ -z "$(foreign)" ]; do
    [ $waited -ge 300 ] && { say "STOP: the card is held (et-who) or another user's device process runs, for 5 minutes"; exit 3; }
    sleep 10; waited=$((waited + 10))
  done
  exec 9<> "$LOCK" || { say "STOP: cannot open $LOCK"; exit 3; }
  flock -n 9 || { say "STOP: the card lock $LOCK is held"; exit 3; }
  { echo "--- who"; who; echo "--- uptime"; uptime; } >> "$OUT/etwho-before.txt" 2>&1
  command -v et-lab-manifest > /dev/null && et-lab-manifest > "$OUT/manifest.txt" 2>&1
else
  echo "DRY: et-who --check, flock -n $LOCK (fd 9), et-lab-manifest skipped" > "$OUT/etwho-before.txt"
fi

# ---- 3. the sampler (lib.sh start_sampler / stop_sampler, at --every-ms) --------------------------------------------
SPID=
drain_mgmt() {  # a sampler killed mid-request leaves a reply queued (14-card-behaviour.md); dev_mngt_service ignores ET_DEVICES
  [ -n "$DRY" ] && return 0
  [ -n "${ET_DEVICES:-}" ] && { say "drain skipped (ET_DEVICES=$ET_DEVICES)"; return 0; }
  LD_LIBRARY_PATH=/opt/et/lib timeout 20 /opt/et/bin/dev_mngt_service -m DM_CMD_GET_MODULE_POWER -n 0 -u 5000 > /dev/null 2>&1 || true
}
stop_sampler() {  # SIGTERM only; after 30 s stuck in a request: SIGKILL and drain, as lib.sh
  [ -n "$SPID" ] || return 0
  kill -TERM "$SPID" 2> /dev/null
  local i; for i in $(seq 1 300); do kill -0 "$SPID" 2> /dev/null || break; sleep 0.1; done
  if kill -0 "$SPID" 2> /dev/null; then
    say "sampler $SPID ignored SIGTERM for 30 s: SIGKILL and drain"; kill -KILL "$SPID" 2> /dev/null; sleep 1; drain_mgmt
  fi
  wait "$SPID" 2> /dev/null
  grep '^{.*}$' "$OUT/telemetry.jsonl.raw" >> "$OUT/telemetry.jsonl" 2> /dev/null; rm -f "$OUT/telemetry.jsonl.raw"
  SPID=
}
start_sampler() {
  local attempt i secs=$((IB + IA + 45))
  for attempt in 1 2 3 4 5 6; do
    "${RUN_SAMPLER[@]}" --seconds "$secs" --every-ms "$EVERY" > "$OUT/telemetry.jsonl.raw" 2>> "$OUT/sampler.err" < /dev/null &
    SPID=$!
    for i in $(seq 1 40); do
      sleep 0.25; grep -q '^{' "$OUT/telemetry.jsonl.raw" 2> /dev/null && return 0
      kill -0 "$SPID" 2> /dev/null || break
    done
    stop_sampler; rm -f "$OUT/telemetry.jsonl"
    [ "$attempt" = 2 ] && drain_mgmt
    sleep 2
  done
  return 1
}
cleanup() { stop_sampler; exec 9>&- 2> /dev/null; }
trap cleanup EXIT
trap 'say "interrupted"; exit 130' INT TERM
: > "$OUT/telemetry.jsonl"
start_sampler || { say "STOP: the sampler would not start (see $OUT/sampler.err)"; exit 1; }
T_SAMPLER=$(now_ms)
say "sampler $SPID at $((1000 / EVERY)) Hz; idle ${IB} s"

# ---- 4. idle, ONE host process, idle -------------------------------------------------------------------------------
nap "$IB"
f=$(foreign); [ -n "$f" ] && { say "STOP: another user's device process or node appeared during the idle: $f"; exit 3; }
o=$(ours "$SPID"); [ -n "${o// /}" ] && [ -z "$DRY" ] && { say "STOP: another of our device processes runs: $o"; exit 3; }
RAPL0=$(rapl_uj)
T_HOST0=$(now_ms)
# the host in a subshell, whose `times` then gives the CPU time of everything it waited for (timeout and the host,
# every thread): the host's share of the energy for a host that does not report its own
# shellcheck disable=SC2086
( timeout 10 "${RUN_HOST[@]}" $ARGS --reps "$R" --budget "$BUDGET" $CHECKS --records-out "$OUT/host.rec" \
    > "$OUT/host.json" 2> "$OUT/host.err" < /dev/null
  rc=$?; times > "$OUT/host.times"; exit $rc )
HRC=$?
HCPU=$(tail -1 "$OUT/host.times" 2> /dev/null | awk '{ for (i = 1; i <= 2; ++i) { split($i, a, "m"); sub("s", "", a[2]); v[i] = a[1] * 60 + a[2] } printf "[%.3f, %.3f]", v[1], v[2] }')
[ -n "$HCPU" ] || HCPU=None
T_HOST1=$(now_ms)
RAPL1=$(rapl_uj)
grep -v '^I20' "$OUT/host.err" > "$OUT/host.err.txt" 2> /dev/null; mv -f "$OUT/host.err.txt" "$OUT/host.err"
say "host rc $HRC in $(( (T_HOST1 - T_HOST0) )) ms: $(tail -1 "$OUT/host.json" | "$PY" -c 'import json,sys
try:
    j = json.loads(sys.stdin.read()); print(j.get("status"), "reps", j.get("reps_done"), "of", j.get("reps_requested"),
        "launch_s mean", round(sum(j["launch_s"]) / max(1, len(j["launch_s"])), 4), "solved", j.get("result", {}).get("solved"))
except Exception as e: print("no JSON line")')"
nap "$IA"
f=$(foreign); [ -n "$f" ] && FOREIGN="$FOREIGN after the host: $f;"
stop_sampler
T_END=$(now_ms)
exec 9>&- 2> /dev/null
if [ -z "$DRY" ]; then et-who > "$OUT/etwho-after.txt" 2>&1; else echo "DRY" > "$OUT/etwho-after.txt"; fi
[ -s "$OUT/telemetry.jsonl" ] || { say "STOP: no telemetry"; exit 1; }

# ---- 5. marks, then the reduction (no device) ----------------------------------------------------------------------
"$PY" - "$OUT/run.json" <<EOF
import json, sys
json.dump({"preset": "$WHAT", "card": "$H", "dry": bool("$DRY"), "lock": "$LOCK", "et_devices": "${ET_DEVICES:-}" or None,
           "build": "$BUILD", "kernel_text_sha256": "$KHASH" or None, "host_args": "$ARGS $CHECKS",
           "reps_planned": $R, "reps_fit": $FIT, "target_s": $TARGET, "budget_s": $BUDGET, "launch_est_s": $EST,
           "idle_before_s": $IB, "idle_after_s": $IA, "every_ms": $EVERY, "sampler": "${RUN_SAMPLER[*]}",
           "sampler_t0_ms": $T_SAMPLER, "host_t0_ms": $T_HOST0, "host_t1_ms": $T_HOST1, "end_ms": $T_END, "host_rc": $HRC,
           "foreign": "${FOREIGN}".strip() or None, "rapl": "$RAPL", "rapl_uj": [$RAPL0, $RAPL1],
           "host_cpu_ext_s": $HCPU, "stub_card": "$STUB_CARD" if bool("$DRY") else None},
          open(sys.argv[1], "w"), indent=1)
EOF
gzip -f "$OUT/telemetry.jsonl"
TR=(); [ -n "$DRY" ] && [ -s "$OUT/stub_truth.json" ] && TR=(--truth "$OUT/stub_truth.json")
nice -n 19 "$PY" "$HERE/tools/energy_reduce.py" "$OUT" "${TR[@]}" > "$OUT/energy.txt" 2>&1
rc=$?
tee -a "$OUT/energy.log" < "$OUT/energy.txt"
say "DONE $WHAT: $([ $rc = 0 ] && echo ok || echo "NOT OK (rc $rc)"); $OUT/energy.json"
exit $rc
