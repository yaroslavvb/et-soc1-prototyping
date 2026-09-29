#!/usr/bin/env bash
# memp2 (hub rungs 33, 36, 43 and energy-manual-102): one block on the local card, from the tree's root.
#
#   bash tools/claims-v3/memp2/block.sh <pass>              aifoundry1: V3_DEVICE=1 (card 1; card 0 is never used)
#   V3_DRY=1 bash tools/claims-v3/memp2/block.sh <pass>     no device access: every device call printed, synthetic
#                                                           results (MEMP2_DRY_WORLD=predicted|alt|lockstep|alt2)
#   bash tools/claims-v3/memp2/block.sh --binhash           the binaries a block would run, with sha256 (no device)
#   Several blocks in a row: tools/claims-v3/memp2/series.sh (queue.sh works too, but reads the die between blocks
#   outside the card lock and with a 20 s cap; see README.md).
#
# pass: 901-999 smoke (any memp2 card); 101-109 PROBE and 201-209 ENERGY development blocks (aifoundry1 card 1 only);
# 111-119 PROBE and 211-219 ENERGY validation blocks (aifoundry3; aifoundry2 only after DV2, with MEMP2_AFTER_DV2=1).
# Every pass on a validation card, its smoke included, needs MEMP2_LOCK_SHA256 = the sha256 of LOCK.sha256 that
# `memp2lib.py freeze` printed, and a LOCK.sha256 whose every entry verifies (the kernel's .text included). A PROBE or
# ENERGY pass needs an ok smoke on the same card that ran the same kernel file (`memp2lib.py smokegate`).
# SMOKE: a ladder, stopped at the first stage with any failure: (1) one minion of shire 0 streams every stride,
# spread and source for 200 loads; (2) the four op programs (one hart; treload's timed TensorLoads); (3) one whole
# shire; (4) the chip; then one energy replicate of two configurations.
# PROBE: the memprobe2 programs rowalt, rrd, refphase (R33) and treload (R36), then the R43 TensorLoad sweep.
# ENERGY: three passes of the catalogue runner over scpline/* and spin/zeros/h1 with build/enercat (E102).
# Data: build/claims-v3/<card>/memp2/p<pass>/ (build/claims-v3-dry/... under V3_DRY).
# Exit: 0 ok, 1 fail, 2 refused before anything touched a card, 3 someone else on the card (the queue retries).
#
# Card rules (AGENT.md 5, 14-card-behaviour.md): et-who --check and lib's others_present / ours_running before the
# block; the card lock (lib block_begin: flock -n on /run/lock/etsoc-shire<N>.lock, fd 9) held across every device
# process and closed in each child; every launch under timeout 10; nobody else and no STOP file between launches; the
# die's minshire mean read between launches (and at 2 Hz from the live telemetry during an energy pass): no start
# above 80 C, stop at a mean of 86 C (the hottest sensor has run at most 4 C above the mean, E53, so no sensor passes
# 90 C) and write build/claims-v3/STOP; a launch that does not finish (the host's 6 s timeout, rc 124/137, a stream
# error, "HPSQ") writes STOP and ends the block at once: nothing more is launched on that card; never card 0 on
# aifoundry1 and never the stock dev_mngt_service there (it opens card 0's management node too), so on aifoundry1 a
# management-node failure (no die temperature, a sampler that will not start or ignores SIGTERM) also writes STOP;
# on aifoundry2 nothing runs while any DV2 queue or block process exists; no reset, no clock, TDP or firmware command.
set -u
. "$(dirname "${BASH_SOURCE[0]}")/../lib.sh"            # cd's to the tree root: CARD, ETTELEM, ENERCAT, HEATER, ...
HERE=tools/claims-v3/memp2
PY=(python3 "$HERE/memp2lib.py")
MP2=build/memprobe2/host/memprobe_host                  # an MEMPROBE_EXT build; never build/memprobe(-v3)
MP2_KERNEL=build/memprobe2/kernel/memprobe.elf
ENERCAT_FIXED=$ENERCAT                                   # build/enercat: the g3log-fixed build, never enercat_v2
RUNNER=tools/claims-v3/cat/run_catalogue_t10.py
START_MAX_C=80
STOP_C=86
STOPFILE=build/claims-v3/STOP
dry() { [ -n "${V3_DRY:-}" ]; }
dry && STOPFILE=build/claims-v3-dry/STOP

enercat_kernel() { grep -a -o '/[[:alnum:]/._-]*/enercat\.elf' "$ENERCAT_FIXED" 2>/dev/null | head -1; }
binhash() {
  local pairs=("memprobe2=$MP2" "memprobe2_kernel=$MP2_KERNEL" "enercat=$ENERCAT_FIXED" "ettelem=$ETTELEM")
  local k; k=$(enercat_kernel); [ -n "$k" ] && pairs+=("enercat_kernel=$k")
  [ "$CARD" = aifoundry2 ] && pairs+=("heater=$HEATER")
  "${PY[@]}" binhash "${pairs[@]}"
}
if [ "${1:-}" = --binhash ]; then binhash; exit 0; fi

PASS=${1:?usage: block.sh <pass> | --binhash}
case "$PASS" in ''|*[!0-9]*) echo "pass must be a number" >&2; exit 2 ;; esac
PASS=$(( 10#$PASS ))

# ---- refusals: nothing below has touched a device yet
case "$CARD" in
  aifoundry1-c0) log "memp2: aifoundry1 card 0 is never used: refused"; exit 2 ;;
  aifoundry1-c1) [ "${ET_DEVICES:-}" = 1 ] || { log "memp2: aifoundry1 card 1 needs ET_DEVICES=1 (got '${ET_DEVICES:-}')"; exit 2; } ;;
esac
if [ "$CARD" = aifoundry2 ]; then   # DV2's own gate ends its pass on any other framework process: never beside it
  if dry; then dv2p=${MEMP2_DRY_DV2:+dry-hook-dv2-queue}
  else dv2p=$(pgrep -af '[s]chedule-dv2|[t]ools/claims-v3/dv2v?/' 2>/dev/null | cut -c1-160 | tr '\n' ';'); fi
  [ -n "$dv2p" ] && { log "memp2: DV2 processes on aifoundry2 ($dv2p): refused"; exit 2; }
fi
[ -n "${V3_FORCE:-}" ] && ! dry && { log "memp2: V3_FORCE is honoured only under V3_DRY=1"; exit 2; }
PLAN=$("${PY[@]}" plan --pass "$PASS" --card "$CARD") || { log "memp2: pass $PASS on $CARD refused: $PLAN"; exit 2; }
KIND=$(sed -n 's/^KIND=//p' <<< "$PLAN"); ROLE=$(sed -n 's/^ROLE=//p' <<< "$PLAN")
SEED=$(sed -n 's/^SEED=//p' <<< "$PLAN"); EPASSES=$(sed -n 's/^PASSES=//p' <<< "$PLAN")
NEEDLOCK=$(sed -n 's/^NEEDLOCK=//p' <<< "$PLAN")
if [ -n "${MEMP2_PREREG_SHA256:-}" ] && [ -z "${MEMP2_LOCK_SHA256:-}" ]; then
  log "memp2: MEMP2_PREREG_SHA256 is no longer read: set MEMP2_LOCK_SHA256 (the sha256 of LOCK.sha256 the freeze printed)"; exit 2
fi
if [ "$NEEDLOCK" = 1 ]; then       # every pass on a validation card, the smoke included
  why=$("${PY[@]}" preregcheck --lock-sha "${MEMP2_LOCK_SHA256:-}") || { log "memp2: pass $PASS on $CARD refused: $why"; exit 2; }
  log "memp2: $why"
fi
[ -e "$STOPFILE" ] && { log "memp2: $STOPFILE present: not starting"; exit 2; }
[ -n "${V3_DEVICE:-}" ] && export V3_DEVICE           # the runner's own others_present check sources lib.sh again

# on aifoundry1 lib's drain (the stock dev_mngt_service) would open card 0's management node too: never run it
case "$CARD" in aifoundry1-*) drain_mgmt() { log "memp2: queue drain skipped on aifoundry1 (the stock dev_mngt_service opens card 0 too)"; } ;; esac
stop_a1() {   # on aifoundry1 a management-node failure cannot be drained: write STOP so no queue runs into it again
  case "$CARD" in aifoundry1-*) touch "$STOPFILE"; echo " (aifoundry1, no drain possible: STOP written)" ;; esac
}
# the die's minshire mean: ettelem under timeout 10 (lib's die_c uses 20), the lock fds closed in the child
if dry; then   # MEMP2_DRY_DIE=a,b,c...: the successive dry readings (the last repeats; 'x' = unreadable)
  DRYDIE=$DATA_ROOT/.memp2-drydie; mkdir -p "$DATA_ROOT"; echo 0 > "$DRYDIE"
  die_c_num() { local n v r; n=$(cat "$DRYDIE"); echo $((n + 1)) > "$DRYDIE"; IFS=, read -ra v <<< "${MEMP2_DRY_DIE:-80}"
                r=${v[$(( n < ${#v[@]} ? n : ${#v[@]} - 1 ))]}; [ "$r" = x ] || echo "$r"; }
else   # ettelem sample fails to start about one time in three right after another instance: up to three tries
  die_c_num() { local i t=; for i in 1 2 3; do
      t=$(timeout 10 "$ETTELEM" sample --seconds 1 --every-ms 500 2>/dev/null < /dev/null 8>&- 9>&- |
          grep '^{' | tail -1 | sed -n 's/.*"minshire":\[\([0-9]*\),.*/\1/p')
      [ -n "$t" ] && break; sleep 2; done; echo "$t"; }
fi
die_c() { local t; t=$(die_c_num); echo "${t:-null}"; }  # block_begin / block_end record it (null, not empty)
if dry; then  # MEMP2_DRY_INTRUDE_AT=n: the n-th others_present check (1 = before the block) finds someone
  DRYOTH=$DATA_ROOT/.memp2-dryothers; echo 0 > "$DRYOTH"
  others_present() { local n; n=$(( $(cat "$DRYOTH") + 1 )); echo "$n" > "$DRYOTH"
                     [ "$n" = "${MEMP2_DRY_INTRUDE_AT:-0}" ] && { log "others present (dry hook, check $n)"; return 0; }; return 1; }
fi
# every device launch: timeout 10, stdin closed, the card-lock fds (8, 9) closed in the child
dev10() { if dry; then echo "DRY hold10: $*" >&2; return 0; fi; timeout 10 "$@" < /dev/null 8>&- 9>&-; }
eval "memp2_lib_start_sampler() $(declare -f start_sampler | tail -n +2)"
start_sampler() { memp2_lib_start_sampler "$@" 8>&- 9>&-; }
# lib's stop_sampler SIGKILLs a sampler that ignores SIGTERM for 30 s and then drains, which is skipped on aifoundry1:
# notice that case first (SIGTERM only here) and write STOP there
eval "memp2_lib_stop_sampler() $(declare -f stop_sampler | tail -n +2)"
SAMPLER_STUCK=
stop_sampler() {
  local pid=${SAMPLER_PID:-} i
  if [ -n "$pid" ] && ! dry; then
    kill -TERM "$pid" 2>/dev/null
    for i in $(seq 1 300); do kill -0 "$pid" 2>/dev/null || break; sleep 0.1; done
    if kill -0 "$pid" 2>/dev/null; then
      SAMPLER_STUCK=1
      case "$CARD" in aifoundry1-*) touch "$STOPFILE"; log "memp2: the sampler ignored SIGTERM for 30 s on aifoundry1: STOP written" ;; esac
    fi
  fi
  memp2_lib_stop_sampler
}

# ---- preflight: files only
pf=()
if ! dry; then
  SRC_TAG="memp2-src:$(sha256sum workloads/memprobe/host/main.cpp | cut -c1-64):$(sha256sum workloads/memprobe/memprobe_args.h | cut -c1-64)"
  [ -x "$MP2" ] || pf+=("missing $MP2 (cmake -S workloads/memprobe -B build/memprobe2 -DMEMPROBE_EXT=ON)")
  [ -f "$MP2_KERNEL" ] || pf+=("missing $MP2_KERNEL")
  [ -x "$MP2" ] && ! grep -a -q -- '--tloop' "$MP2" && pf+=("$MP2 is not an MEMPROBE_EXT build (no --tloop)")
  [ -x "$MP2" ] && ! grep -a -q -- "$SRC_TAG" "$MP2" && pf+=("$MP2 was not built from this tree's host/main.cpp and memprobe_args.h (stale build: rebuild build/memprobe2)")
  [ -f "$MP2_KERNEL" ] && [ -x "$MP2" ] && [ "$MP2_KERNEL" -ot workloads/memprobe/kernel/memprobe.c ] &&
    pf+=("$MP2_KERNEL is older than kernel/memprobe.c (rebuild build/memprobe2 with --clean-first)")
  [ -x "$ETTELEM" ] || pf+=("missing $ETTELEM")
  if [ "$KIND" != PROBE ]; then
    [ -x "$ENERCAT_FIXED" ] || pf+=("missing $ENERCAT_FIXED")
    grep -a -q 'VERBOSE_MID' "$ENERCAT_FIXED" 2>/dev/null || pf+=("$ENERCAT_FIXED lacks the g3log fix (registerRuntimeLogLevels)")
    grep -a -q -- '--access-bytes' "$ENERCAT_FIXED" 2>/dev/null || pf+=("$ENERCAT_FIXED lacks --access-bytes (scpline)")
    k=$(enercat_kernel); { [ -n "$k" ] && [ -f "$k" ]; } || pf+=("the kernel compiled into $ENERCAT_FIXED ('$k') is missing")
  fi
  [ "$CARD" = aifoundry2 ] && [ ! -x "$HEATER" ] && pf+=("missing heater $HEATER")
  [ -e "/run/lock/etsoc-shire${V3_DEVICE:-0}.lock" ] || pf+=("no card lock file /run/lock/etsoc-shire${V3_DEVICE:-0}.lock")
  command -v et-who > /dev/null || pf+=("no et-who on this host")
fi
python3 -c 'import numpy' 2>/dev/null || pf+=("python3 has no numpy (the post-block check)")
[ ${#pf[@]} -gt 0 ] && { printf 'memp2 preflight: %s\n' "${pf[@]}" >&2; exit 2; }
if [ "$KIND" != SMOKE ]; then      # the smoke's ladder must have run this kernel on this card first
  why=$("${PY[@]}" smokegate --data "$DATA_ROOT/memp2" --kernel "$MP2_KERNEL" ${V3_DRY:+--dry}) ||
    { log "memp2: pass $PASS on $CARD refused: $why"; exit 2; }
  log "memp2: $why"
fi

# ---- the card must be free
if ! dry; then
  held=$(et-who --check 2>&1); rc=$?
  [ $rc -ne 0 ] && { log "memp2: et-who --check exit $rc: ${held//$'\n'/; }"; exit 3; }
fi
others_present && exit 3
ours_running && { log "memp2: a device process of this user is running on this card: not starting"; exit 3; }

# ---- begin (block_begin takes the card lock on fd 9, flock -n, for the whole block)
d0=$DATA_ROOT/memp2/p$PASS           # an earlier unfinished (or, with V3_FORCE, any) attempt is set aside, never mixed in
if [ -d "$d0" ] && { [ ! -e "$d0/block.json" ] || [ -n "${V3_FORCE:-}" ]; }; then mv "$d0" "$d0.attempt-$(date +%s)"; fi
block_begin memp2 "$PASS"
WATCH_PID=; RUNNER_PID=
cleanup() {   # SIGTERM only: the runner's current launch ends by itself (timeout 10); then the sampler
  [ -n "${RUNNER_PID:-}" ] && kill "$RUNNER_PID" 2>/dev/null
  [ -n "${WATCH_PID:-}" ] && kill "$WATCH_PID" 2>/dev/null
  if [ -n "${RUNNER_PID:-}" ] && ! dry; then
    local i; for i in $(seq 1 30); do pgrep -u "$(id -u)" -x enercat_host > /dev/null || break; sleep 0.5; done
  fi
  RUNNER_PID=; WATCH_PID=
  stop_sampler
}
trap cleanup EXIT
mkdir -p "$OUT"
: > "$OUT/launches.jsonl"; : > "$OUT/marks.jsonl"
mark() { echo "{\"t_ms\":$(now_ms),\"ev\":\"$1\"${2:+,$2}}" >> "$OUT/marks.jsonl"; }
sha256sum "$HERE"/*.py "$HERE"/*.sh "$HERE"/*.txt "$HERE"/prereg/* workloads/memprobe/gen_ops.py workloads/memprobe/gen_ops2.py \
  workloads/memprobe/memprobe_args.h workloads/memprobe/kernel/memprobe.c workloads/memprobe/host/main.cpp \
  "$RUNNER" tools/claims-v3/cat/catlib.py workloads/enercat/run_catalogue.py workloads/enercat/analyze_catalogue.py \
  tools/claims-v3/queue.sh >> "$OUT/code.sha256" 2>/dev/null
[ -e "$HERE/LOCK.sha256" ] && sha256sum "$HERE/LOCK.sha256" >> "$OUT/code.sha256"
binhash > "$OUT/binaries.json"
python3 - "$OUT/pass.json" <<EOF
import json, sys
json.dump({"exp": "memp2", "card": "$CARD", "pass": $PASS, "kind": "$KIND", "role": "$ROLE", "seed": $SEED,
           "dry": bool("${V3_DRY:-}"), "dry_world": "${MEMP2_DRY_WORLD:-predicted}" if "${V3_DRY:-}" else None,
           "lock_sha256": "${MEMP2_LOCK_SHA256:-}" or None, "needlock": "$NEEDLOCK" == "1",
           "device": "${V3_DEVICE:-}" or None, "stop_c": $STOP_C, "start_max_c": $START_MAX_C},
          open(sys.argv[1], "w"), indent=1)
EOF
command -v et-lab-manifest > /dev/null && ! dry && timeout 30 et-lab-manifest > "$OUT/manifest.txt" 2>&1
mark block_begin "\"kind\":\"$KIND\",\"role\":\"$ROLE\",\"die_c\":${BLOCK_C0:-null}"

finish() {   # finish <status> <note> [exit code]
  cleanup
  [ "$1" = others ] && die_c() { echo null; }         # someone else is on the card: do not open it again
  block_end "$1" "$2"
  exit "${3:-0}"
}
hang_stop() {   # hang_stop <label> <why>: a launch did not finish; nothing more on this card until someone looks
  touch "$STOPFILE"
  mark hang "\"label\":\"$1\",\"why\":\"${2//\"/\'}\""
  finish fail "launch $1 did not finish ($2): STOP written, nothing more launched on this card" 1
}
NULLS=0
between() {   # between <what>: nobody else, no STOP file, the die below STOP_C (two unreadable dies in a row: stop)
  [ -e "$STOPFILE" ] && { mark stop "\"why\":\"STOP file\""; finish fail "STOP file present ($1)" 1; }
  others_present && { mark others "\"at\":\"$1\""; finish others "another user or device process present ($1)" 3; }
  local t; t=$(die_c_num)
  if [ -z "$t" ]; then
    NULLS=$((NULLS + 1)); [ $NULLS -ge 2 ] && finish fail "no die temperature twice in a row ($1)$(stop_a1)" 1
    return 0
  fi
  NULLS=0; LAST_C=$t
  if [ "$t" -ge "$STOP_C" ]; then touch "$STOPFILE"; mark thermal_stop "\"die_c\":$t"; finish fail "die mean $t C >= $STOP_C C ($1): STOP written" 1; fi
  return 0
}
launch() {   # launch <label> <out file> <cmd...>: one device process, its rc in launches.jsonl; a hung launch stops all
  local label=$1 out=$2 t0 rc h=; shift 2
  local err=${out%.*}.err
  t0=$(now_ms)
  if dry; then   # MEMP2_DRY_FAIL_AT / MEMP2_DRY_HANG_AT=label,...: that launch fails (rc 1) / does not finish (rc 3)
    echo "DRY hold10: $*" >&2; : > "$out"; : > "$err"; rc=0
    case ",${MEMP2_DRY_FAIL_AT:-}," in *",$label,"*) rc=1 ;; esac
    case ",${MEMP2_DRY_HANG_AT:-}," in *",$label,"*) echo "kernel did not finish within 6 s, aborting the stream (dry hook)" > "$err"; rc=3 ;; esac
  else dev10 "$@" > "$out" 2> "$err"; rc=$?; fi
  echo "{\"label\":\"$label\",\"t0_ms\":$t0,\"t1_ms\":$(now_ms),\"rc\":$rc}" >> "$OUT/launches.jsonl"
  case "$rc" in 124|137) h="rc $rc (the 10 s cap)" ;; esac
  [ "$rc" = 3 ] && [ "$1" = "$MP2" ] && h="rc 3 (memprobe: a launch did not finish or a stream error)"
  [ -z "$h" ] && h=$("${PY[@]}" hang "$err" "$out" 2>/dev/null)
  [ -n "$h" ] && hang_stop "$label" "$h"
  return $rc
}

# ---- the start temperature (no launch while waiting)
t=$(die_c_num); w=0
while [ -n "$t" ] && [ "$t" -gt "$START_MAX_C" ] && [ $w -lt 300 ]; do dry || sleep 20; w=$((w + 20)); t=$(die_c_num); done
[ -z "$t" ] && finish fail "no die temperature at the start$(stop_a1)" 1
[ "$t" -gt "$START_MAX_C" ] && finish fail "die $t C > $START_MAX_C C after 300 s" 1
mark start "\"die_c\":$t,\"waited_s\":$w"
if [ "$CARD" = aifoundry2 ]; then   # its governor lifts the clock off 600 MHz on a cool die: heat to 76 C first
  for i in $(seq 1 60); do
    t=$(die_c_num); [ -n "$t" ] && [ "$t" -ge 76 ] && break
    between "heat $i"
    launch heat "$OUT/heat.out" "$HEATER" --test fma --type fp32 --pattern none --values randn \
      --shires 0xffffffff --per-shire 32 --seconds 2 --seed 1
  done
  mark heated "\"die_c\":${t:-null}"
fi

FAILS=0
# ---------------------------------------------------------------- PROBE: R33, R36 (programs) and R43 (sweep)
run_programs() {
  local grp progs p
  for grp in "rowalt rrd" "refphase treload"; do
    between "programs $grp"
    progs=(); for p in $grp; do progs+=(--program "$OUT/mp/$p.ops"); done
    launch "programs:${grp// /+}" "$OUT/mp/run-${grp%% *}.out" "$MP2" --arena 1G --out-dir "$OUT/mp" "${progs[@]}" ||
      { FAILS=$((FAILS + 1)); log "memp2: programs $grp failed"; }
  done
}
run_tloops() {   # run_tloops [--smoke --stage S]: the pass's R43 launches (or one stage of the smoke's ladder)
  local name args
  while IFS=$'\t' read -r name args; do
    between "tloop $name"
    # shellcheck disable=SC2086
    launch "tloop:$name" "$OUT/tl/$name.out" "$MP2" $args || { FAILS=$((FAILS + 1)); log "memp2: tloop $name failed"; }
  done < <("${PY[@]}" tloop-configs --pass "$SEED" "$@" --args)
}
gate() {   # the smoke goes up a stage only if nothing has failed so far
  [ "$FAILS" -eq 0 ] && return 0
  mark smoke_stop "\"after\":\"$1\",\"fails\":$FAILS"
  finish fail "smoke: $FAILS failure(s) by the end of $1: not going further" 1
}
probe() {   # probe [--smoke]
  local sm=${1:-}
  mkdir -p "$OUT/mp" "$OUT/tl"
  echo "python3 workloads/memprobe/gen_ops2.py all --out <mp> --seed $SEED $sm" > "$OUT/mp/gen.log"
  python3 workloads/memprobe/gen_ops2.py all --out "$OUT/mp" --seed "$SEED" $sm >> "$OUT/mp/gen.log" 2>&1 ||
    finish fail "gen_ops2.py failed" 1
  "${PY[@]}" tloop-configs --pass "$SEED" ${sm:+--smoke} > "$OUT/tl/plan.jsonl"
  if [ -n "$sm" ]; then
    run_tloops --smoke --stage 1; gate "stage 1 (one minion of shire 0)"
    run_programs;                 gate "stage 2 (the op programs)"
    run_tloops --smoke --stage 3; gate "stage 3 (one shire)"
    run_tloops --smoke --stage 4; gate "stage 4 (the chip)"
  else
    run_programs
    run_tloops
  fi
  dry && "${PY[@]}" dry-probe "$OUT" > "$OUT/mp/dry-probe.out"
  rm -f "$OUT"/mp/*.ops                          # regenerated by gen.log's command
  mark probe_done "\"fails\":$FAILS"
}

# ---------------------------------------------------------------- ENERGY: E102 (scratchpad strides) with build/enercat
energy() {   # energy <replicates> [--smoke]
  local n=$1 sm=${2:-} r d only timing list maxs rc st note h
  only="scpline/,spin/zeros/h1"; timing=(--burst 3 --gap 4.5)
  [ -n "$sm" ] && { only="scpline/stride64/random,spin/zeros/h1"; timing=(--burst 1 --gap 4.5 --lead 3); }
  for r in $(seq 1 "$n"); do
    between "energy $r"
    d=$OUT/e$r; mkdir -p "$d"
    list=$(python3 "$RUNNER" /dev/null --root "$V3_ROOT" --only "$only" --passes 1 "${timing[@]}" --seed "$((SEED * 10 + r))" \
           --host-bin "$ENERCAT_FIXED" --list 2>&1) || finish fail "runner --list: $list" 1
    maxs=$(python3 -c 'import json,sys; print(json.loads(sys.argv[1])["max_s"])' "$list")
    start_sampler "$d/telemetry.jsonl" $((maxs + 120)) || finish fail "the sampler would not start (energy $r)$(stop_a1)" 1
    local rargs=("$d" --root "$V3_ROOT" --only "$only" --passes 1 "${timing[@]}" --seed "$((SEED * 10 + r))"
                 --host-bin "$ENERCAT_FIXED" --tel-live "$d/telemetry.jsonl.raw" --card "$CARD")
    mark energy_begin "\"rep\":$r,\"max_s\":$maxs"
    if dry; then
      python3 "$RUNNER" "${rargs[@]}" --dry 2> "$d/runner.dry"; rc=$?
      "${PY[@]}" dry-energy "$d" --seed "$((SEED * 10 + r))"
      [ -n "${MEMP2_DRY_HANG_ENERGY:-}" ] && echo "pass 0 scpline/stride256/random: 0 launches rc=124 'dry hook'" >> "$d/run.log"
    else
      python3 "$RUNNER" "${rargs[@]}" > "$d/runner.out" 2>&1 8>&- 9>&- &
      RUNNER_PID=$!
      "${PY[@]}" watch --tel "$d/telemetry.jsonl.raw" --stop-c "$STOP_C" --pid "$RUNNER_PID" --flag "$OUT/thermal_stop.json" \
        --log "$d/run.log" --hang-flag "$OUT/hang.json" 8>&- 9>&- &
      WATCH_PID=$!
      wait "$RUNNER_PID"; rc=$?; RUNNER_PID=
      kill "$WATCH_PID" 2>/dev/null; wait "$WATCH_PID" 2>/dev/null; WATCH_PID=
      # a runner stopped by the watcher leaves its current launch (<= 10 s) running: let it end before the sampler
      for i in $(seq 1 30); do pgrep -u "$(id -u)" -x enercat_host > /dev/null || break; sleep 0.5; done
    fi
    stop_sampler
    mark energy_end "\"rep\":$r,\"rc\":$rc"
    if [ -e "$OUT/thermal_stop.json" ]; then touch "$STOPFILE"; finish fail "thermal stop during energy $r (mean >= $STOP_C C): STOP written" 1; fi
    h=$("${PY[@]}" hang "$d/run.log" "$d/runner.out" 2>/dev/null)
    [ -e "$OUT/hang.json" ] || [ -n "$h" ] && hang_stop "energy:$r" "${h:-the watcher saw a hung launch}"
    [ -n "$SAMPLER_STUCK" ] && finish fail "the sampler ignored SIGTERM for 30 s (energy $r)$(stop_a1)" 1
    [ "$rc" = 3 ] && finish others "another user or device process appeared during energy $r" 3
    [ "$rc" = 4 ] && { FAILS=$((FAILS + 1)); log "memp2: energy $r: the sampler stopped writing"; }
    res=$(python3 tools/claims-v3/cat/catlib.py check "$d" --card "$CARD" --root "$V3_ROOT" 2>&1) || res="fail check crashed"
    st=${res%% *}; note=${res#* }
    log "memp2: energy $r: $st $note"
    [ "$st" = ok ] || FAILS=$((FAILS + 1))
    for f in telemetry.jsonl runs.jsonl marks.jsonl; do [ -s "$d/$f" ] && gzip -f -n "$d/$f"; done
  done
}

case "$KIND" in
  PROBE) probe ;;
  ENERGY) energy "$EPASSES" ;;
  SMOKE) probe --smoke; energy 1 --smoke ;;
esac

res=$(python3 "$HERE/reduce.py" --check-pass "$OUT" 2>&1); crc=$?
for f in "$OUT"/mp/*.json "$OUT"/mp/*.u32; do [ -f "$f" ] && gzip -f -n "$f"; done
if [ $crc -eq 0 ] && [ $FAILS -eq 0 ]; then finish ok "$KIND ($ROLE) done: ${res#* }"
else finish fail "$KIND ($ROLE): $FAILS failed step(s); check: ${res//\"/\'}" 1; fi
