#!/usr/bin/env bash
# V3-WIRE (PLAN3 §2 "V3-WIRE": heat per millimetre, third run, plus the byte-for-byte fill check), one pass per block:
#   bash tools/claims-v3/wire/block.sh <pass> [--smoke]          (passes 1-6 on each card; 7, 8 ... only as re-runs)
#   V3_DRY=1 bash tools/claims-v3/wire/block.sh 1                (no device access: prints every device call)
# A pass is run_wire.py's pass loop (--set v2, the 28 configurations of configs.json) done in bash so that every
# device call goes through lib.sh (hold10, start_sampler/stop_sampler, heat_to):
#   [pass 1 only] the 12 --dump-slice launches of WIRE-FILL (before the sampler, before heating);
#   [aifoundry2] heat_to 76;  the 10 Hz sampler;  8 s settle;
#   per configuration, in the pass's shuffled order (seed 31+pass-1 on aifoundry2, 41+pass-1 on aifoundry3):
#     check the sampler (restart it with SIGTERM + start_sampler if it died or stalled);
#     [aifoundry2] a 2 s heater launch if the die (read from the sampler's own output) is below 69 C, marked;
#     tstore_uniq prefill of every scratchpad (marked);  5 s idle;  3 s burst of 1 KB tensor loads;  4 s idle;
#   8 s idle; stop the sampler; quick check (wire_check.py); gzip the telemetry.
# Every enercat launch is under hold10 (timeout 10) and --budget 8. Exit: 0 ok, 1 failed (block.json says why),
# 3 another user on the card (at the start, or a foreign device process mid-pass) or one of our own device processes
# already running at the start (the queue retries later). Deviations from the plan's commands: README.md.
. "$(dirname "${BASH_SOURCE[0]}")/../lib.sh"
others_present && exit 3
# queue.sh's wait_free checks this before every block; a manual run (the smoke) must not start a second sampler next to
# a running block's, nor set its directory aside (below)
ours_running && { log "one of our own device processes is running (another block?): not starting"; exit 3; }

PASS=${1:-}
SMOKE=; [ "${2:-}" = --smoke ] && SMOKE=1
case "$PASS" in ''|*[!0-9]*|0) echo "usage: block.sh <pass >= 1> [--smoke]" >&2; exit 2 ;; esac
WD=tools/claims-v3/wire                        # this experiment's directory, relative to the tree root (lib.sh cd'd there)
if [ "$CARD" = aifoundry2 ]; then SEED0=31; WARM_C=69; else SEED0=41; WARM_C=0; fi
SEED=$((SEED0 + PASS - 1))
GAP=5; AFTER=4; BURST=3; SETTLE=8; TAIL=8      # run_wire.py: --gap 5 --after 4 --burst 3, 8 s after the sampler starts, gap + 3 at the end
ONLY=; EXP=wire; FORCE_HEAT=
if [ -n "$SMOKE" ]; then
  EXP=wire-smoke; SETTLE=2; TAIL=1
  ONLY=wu/p0.5/hop4,wsep/p0/hop5               # the two argument shapes: --hop-distance + --uniq-regions, and --pairs
  [ "$CARD" = aifoundry2 ] && FORCE_HEAT=1     # run the mid-pass heater once whatever the die reads
fi

nap() { if [ -n "${V3_DRY:-}" ]; then echo "DRY sleep $1" >&2; else sleep "$1"; fi; }
# hold10 with stdout to $1 and stderr appended to $2; in a dry run the command line is also shown on the terminal.
run10() {
  local o=$1 e=$2; shift 2
  [ -n "${V3_DRY:-}" ] && echo "DRY hold10: $* > ${o#"$V3_ROOT"/}" >&2
  hold10 "$@" > "$o" 2>> "$e"
}
mark() { printf '{"kind":"%s","cfg":"%s","pass":%s,"t_start_ms":%s,"t_end_ms":%s}\n' "$1" "$2" "$PASS" "$3" "$4" >> "$OUT/marks.jsonl"; }
# the die from the running sampler's last line (die_c would open the management node, which the sampler holds)
tel_die() {
  if [ -n "${V3_DRY:-}" ]; then echo 80; return; fi
  tail -c 4000 "$OUT/telemetry.jsonl.raw" 2>/dev/null | grep '^{' | tail -1 | sed -n 's/.*"minshire":\[\([0-9]*\),.*/\1/p'
}
# another user's device process appeared mid-block (logins alone do not stop a running pass)
foreign_device() {
  [ -n "${V3_DRY:-}" ] && return 1
  ps -eo uid=,comm= | awk -v me="$(id -u)" -v re="$DEV_COMM" '$1 != me && $2 ~ re {f=1} END {exit !f}'
}
LAST_SZ=0; LAST_T=0
check_sampler() {  # run_wire.py's check_sampler, with SIGTERM (stop_sampler) instead of kill
  [ -n "${V3_DRY:-}" ] && return 0
  local sz now alive=1
  sz=$(stat -c %s "$OUT/telemetry.jsonl.raw" 2>/dev/null || echo 0); now=$(date +%s)
  kill -0 "${SAMPLER_PID:-0}" 2>/dev/null || alive=0
  if [ "$alive" = 0 ] || { [ "$LAST_T" -gt 0 ] && [ $((now - LAST_T)) -gt 2 ] && [ "$sz" -le "$LAST_SZ" ]; }; then
    echo "sampler $([ "$alive" = 0 ] && echo exited || echo stalled); restarting" >> "$OUT/run.log"
    stop_sampler; sleep 2
    start_sampler "$OUT/telemetry.jsonl" "$SAMPLER_S" || return 1
    sleep 4
    sz=$(stat -c %s "$OUT/telemetry.jsonl.raw" 2>/dev/null || echo 0)
  fi
  LAST_SZ=$sz; LAST_T=$(date +%s)
}

# An earlier attempt of this pass left without block.json (interrupted), or any earlier attempt when V3_FORCE is set:
# this block appends to runs.jsonl, marks.jsonl and telemetry.jsonl, and analyze_wire would merge two attempts' launches
# into one burst. queue.sh moves such a directory aside before a retry; a manual run (the smoke) does the same here.
OUT0=$DATA_ROOT/$EXP/p$PASS
if [ -d "$OUT0" ] && { [ ! -e "$OUT0/block.json" ] || [ -n "${V3_FORCE:-}" ]; }; then
  case "$OUT0" in
    "$V3_ROOT"/build/claims-v3-dry/*) rm -rf "$OUT0" ;;                  # dry-run output only
    *) mv "$OUT0" "$OUT0.attempt-$(date +%s)"; log "earlier attempt of $EXP p$PASS set aside as $OUT0.attempt-*" ;;
  esac
fi
block_begin "$EXP" "$PASS"
if [ -n "$SMOKE" ]; then sha256sum "$WD"/*.sh "$WD"/*.py "$WD"/*.json "$WD"/registered/*.py; else sha256sum "$WD"/registered/*.py; fi \
  >> "$OUT/code.sha256" 2>/dev/null
echo "$CARD $EXP pass $PASS seed $SEED warm_c $WARM_C $(date +%FT%T)" >> "$OUT/run.log"

# ---- pre-flight (no device access) ----
miss=
for f in "$ENERCAT2" "$ETTELEM"; do [ -x "$f" ] || miss="$miss $f"; done
[ "$CARD" = aifoundry2 ] && { [ -x "$HEATER" ] || miss="$miss $HEATER"; }
[ -n "$miss" ] && { block_end fail "missing:$miss"; exit 1; }
python3 "$WD/wire_cfgs.py" --root "$V3_ROOT" --seed "$SEED" ${ONLY:+--only "$ONLY"} --json "$OUT/order.json" > "$OUT/order.tsv" \
  || { block_end fail "wire_cfgs.py failed"; exit 1; }
python3 "$WD/wire_cfgs.py" --root "$V3_ROOT" --check-runner >> "$OUT/run.log" 2>&1 \
  || log "note: configs.json and this tree's run_wire.py differ (configs.json is what runs; see run.log)"
NC=$(wc -l < "$OUT/order.tsv")
SAMPLER_S=$((NC * 18 + 300))                   # run_wire.py's total_s for one pass; the sampler is stopped at the end anyway

# ---- WIRE-FILL: the --dump-slice launches (pass 1: 4 fills x 3 separate launches; smoke: one of each) ----
# WIRE_DUMPS=1 repeats them in another pass (only if pass 1's were incomplete; the reduction reads every ok pass's dumps).
FILL_NOTE=; FILL_RC=0
if [ -n "$SMOKE" ] || [ "$PASS" = 1 ] || [ -n "${WIRE_DUMPS:-}" ]; then
  mkdir -p "$OUT/dump"; reps="1 2 3"; [ -n "$SMOKE" ] && reps=1
  for op in "tstore_raw bern:0.25" "tstore_raw alt:64" "tstore_raw frz" "tstore_uniq uq:0.25"; do
    set -- $op
    for r in $reps; do
      f="$OUT/dump/dump_${2//:/_}_$r"; t0=$(now_ms)
      run10 "$f.txt" "$f.err" "$ENERCAT2" --pattern "$1" --operands "$2" --slice-bytes 32K --seconds 0.3 --window 60000000 \
        --dump-slice 1024 --budget 8
      rc=$?
      echo "{\"pattern\":\"$1\",\"operands\":\"$2\",\"rep\":$r,\"rc\":$rc,\"t_start_ms\":$t0,\"t_end_ms\":$(now_ms)}" >> "$OUT/dump/launches.jsonl"
    done
  done
  FILL_NOTE=$(python3 "$WD/wire_check.py" dump "$OUT/dump" ${V3_DRY:+--dry}); FILL_RC=$?
  log "WIRE-FILL: $FILL_NOTE"
fi

# ---- heat (aifoundry2 power work starts on a die >= 76 C), then the sampler ----
if [ "$CARD" = aifoundry2 ] && [ -z "$SMOKE" ]; then
  heat_to 76 "$OUT/heat.jsonl" || { block_end fail "heat_to 76 gave up"; exit 1; }
fi
start_sampler "$OUT/telemetry.jsonl" "$SAMPLER_S" || { block_end fail "sampler would not start"; exit 1; }
LAST_T=$(date +%s)
nap "$SETTLE"

# ---- the configurations ----
i=0; HEAT_RC=0
while IFS=$'\t' read -r -u 9 cfg fpat fops args; do
  i=$((i + 1))
  if foreign_device; then block_end fail "another user started a device process before configuration $i"; exit 3; fi
  check_sampler || { block_end fail "sampler would not restart before configuration $i"; exit 1; }
  if [ "$WARM_C" != 0 ]; then
    t=$(tel_die)
    if [ -n "$FORCE_HEAT" ] || { [ -n "$t" ] && [ "$t" -lt "$WARM_C" ]; }; then
      h0=$(now_ms)
      run10 /dev/null "$OUT/heater.err" "$HEATER" --test fma --type fp32 --pattern none --values randn \
        --shires 0xffffffff --per-shire 32 --seconds 2 --seed 1
      HEAT_RC=$?
      mark heater "$cfg" "$h0" "$(now_ms)"
      echo "heater at ${t:-?} C (rc $HEAT_RC)" >> "$OUT/run.log"; FORCE_HEAT=
    fi
  fi
  f0=$(now_ms)
  run10 /dev/null "$OUT/host.err" "$ENERCAT2" --pattern "$fpat" --operands "$fops" --slice-bytes 32K --scp \
    --seconds 0.3 --window 60000000 --budget 8
  frc=$?
  mark fill "$cfg" "$f0" "$(now_ms)"
  nap "$GAP"
  # shellcheck disable=SC2086  # args is a list of simple tokens (configs.json)
  run10 "$OUT/burst.out" "$OUT/host.err" "$ENERCAT2" $args --seconds "$BURST" --window 240000000 --budget 8
  brc=$?
  n=$(grep -c '^ENERCAT {' "$OUT/burst.out")
  sed -n "s|^ENERCAT {|{\"host\":\"$CARD\",\"pass\":$PASS,\"cfg\":\"$cfg\",|p" "$OUT/burst.out" >> "$OUT/runs.jsonl"   # cfg has /
  nap "$AFTER"
  echo "pass $PASS $cfg: $n launches (fill rc $frc, burst rc $brc)" >> "$OUT/run.log"
done 9< "$OUT/order.tsv"
nap "$TAIL"
stop_sampler
rm -f "$OUT/burst.out"

# ---- quick check and compression ----
touch "$OUT/runs.jsonl" "$OUT/marks.jsonl"
NOTE=$(python3 "$WD/wire_check.py" pass "$OUT" --card "$CARD" --pass "$PASS" --expect "$NC" ${SMOKE:+--smoke} ${V3_DRY:+--dry})
PASS_RC=$?
[ -s "$OUT/telemetry.jsonl" ] && gzip -f "$OUT/telemetry.jsonl"
[ -n "$FILL_NOTE" ] && NOTE="$NOTE; $FILL_NOTE"
[ -n "${V3_DRY:-}" ] && NOTE="dry run: $NOTE"
if [ -n "$SMOKE" ] && [ -z "${V3_DRY:-}" ]; then
  [ "$FILL_RC" = 0 ] || PASS_RC=1
  [ "$HEAT_RC" = 0 ] || { PASS_RC=1; NOTE="$NOTE; heater rc $HEAT_RC"; }
fi
if [ "$PASS_RC" = 0 ]; then block_end ok "$NOTE"; else block_end fail "$NOTE"; exit 1; fi
