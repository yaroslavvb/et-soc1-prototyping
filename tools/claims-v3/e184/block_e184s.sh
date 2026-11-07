#!/usr/bin/env bash
# E184 (Q153, the kit): one pass of arm S, the staircase, on aifoundry3 card 0 (KIT.md). tools/claims-v3/e180/block_e180_v2.sh's form with
# E184's files: lib.sh's look, D1's other-user test (E180's others_d1_e180.sh, sourced unchanged), the preflight (files only), block_begin's
# card lock, the 10 Hz sampler through E128's telemetry guard with no --reset-ms, the runner (run_e184.py: quads, the calibration), the
# post-block check, gzip, block_end. lib.sh's drain_mgmt is replaced by a refusal, so dev_mngt_service never runs. Nothing is set: no
# governor, TDP, threshold or clock set, no reset, no statistics reset.
#
#   bash tools/claims-v3/e184/block_e184s.sh <P>             # P = 18410-18418, a planned pass of arm S
#   bash tools/claims-v3/e184/block_e184s.sh 18401 --smoke   # the smoke: four quads
#   bash tools/claims-v3/e184/block_e184s.sh 18402 --stoptest   # the stop-path test: no launch
#   V3_DRY=1 bash tools/claims-v3/e184/block_e184s.sh <P>    # print every device call, touch nothing
#
# Data: $DATA_ROOT/e184/p<P>/ (runs, telemetry and marks gzipped; configs.json, check.json, block.json, run.log, code.sha256, sched/).
# Exit: 0 ok; 1 the block failed; 2 preflight or plan refused; 3 another user or device process; 5 a stop fired.
# SPDX-License-Identifier: Apache-2.0
. "$(dirname "${BASH_SOURCE[0]}")/../lib.sh"      # cd's to the tree root; CARD, DATA_ROOT
ETTELEM=tools/claims-v3/e128/ettelem_guard.sh
drain_mgmt() { log "E184: drain refused: dev_mngt_service is not in E184's classified command list"; return 0; }
. tools/claims-v3/e180/others_d1_e180.sh
[ "$CARD" = aifoundry3 ] || { echo "arm S runs on aifoundry3 card 0 only (this is $CARD)" >&2; exit 2; }
others_present && exit 3
if ours_running; then log "one of our own device processes on this card is still running"; exit 3; fi

ARG=${1:?usage: block_e184s.sh <pass> [--smoke | --stoptest]}
SMOKE=; [ "${2:-}" = --smoke ] && SMOKE=1
STOPTEST=; [ "${2:-}" = --stoptest ] && STOPTEST=1
case "$ARG" in ''|*[!0-9]*) echo "pass must be a number" >&2; exit 2 ;; esac
HERE=tools/claims-v3/e184
RUNNER=$HERE/run_e184.py
HOST_BIN=build/enercat-e184/host/enercat_host
EXPN=e184; [ -n "$SMOKE" ] && EXPN=e184-smoke; [ -n "$STOPTEST" ] && EXPN=e184-stoptest
case "$ARG" in
  18402) [ -n "$STOPTEST" ] || { echo "18402 is the stop-path test: --stoptest" >&2; exit 2; } ;;
  18401) [ -n "$SMOKE" ] || { echo "18401 is the smoke: --smoke" >&2; exit 2; } ;;
  1841[0-8]) [ -z "$SMOKE$STOPTEST" ] || { echo "$ARG is a measured pass" >&2; exit 2; } ;;
  *) echo "pass $ARG is not arm S's" >&2; exit 2 ;;
esac

# ---- preflight: files only, no device --------------------------------------------------------------------------
pf=()
[ -x "$HOST_BIN" ] || pf+=("missing $HOST_BIN (the E184 build: build_e184.sh)")
[ -x "$ETTELEM" ] || pf+=("missing $ETTELEM")
[ -x build/ettelem/ettelem ] || pf+=("missing build/ettelem/ettelem (the reader $ETTELEM execs)")
if [ -x "$HOST_BIN" ]; then
  grep -a -q -- '--schedule' "$HOST_BIN" && grep -a -q -- '--stop-file' "$HOST_BIN" || pf+=("$HOST_BIN lacks E184's --schedule and --stop-file")
  kelf=$(grep -a -o '/[[:alnum:]/._-]*/enercat\.elf' "$HOST_BIN" | head -1)
  [ -n "$kelf" ] && [ ! -f "$kelf" ] && pf+=("kernel $kelf (compiled into $HOST_BIN) not found")
fi
CHK=$(python3 -B "$HERE/check_e184.py" harness 2>&1) || pf+=("harness: $CHK")
LIST=
if [ ${#pf[@]} -eq 0 ] && [ -z "$STOPTEST" ]; then
  LIST=$(python3 -B "$RUNNER" /dev/null --root "$V3_ROOT" --pass "$ARG" --card "$CARD" --list 2>&1) || pf+=("runner --list: $LIST")
fi
if [ ${#pf[@]} -gt 0 ]; then printf 'preflight: %s\n' "${pf[@]}" >&2; exit 2; fi
if [ -n "$STOPTEST" ]; then NRUN=0; MAXS=30
else
  NRUN=$(python3 -c 'import json,sys; print(json.loads(sys.argv[1])["n"])' "$LIST")
  MAXS=$(python3 -c 'import json,sys; print(json.loads(sys.argv[1])["max_s"])' "$LIST")
fi

# ---- the block ---------------------------------------------------------------------------------------------------
eval "lib_die_c() $(declare -f die_c | tail -n +2)"
finish() {  # finish <status> <note>
  if [ "$1" = others ]; then die_c() { echo null; }; else die_c() { local t; t=$(lib_die_c); echo "${t:-null}"; }; fi
  block_end "$1" "$2"
}
gz_out() { local f; for f in telemetry.jsonl runs.jsonl marks.jsonl; do [ -s "$OUT/$f" ] && gzip -f "$OUT/$f"; done; return 0; }
d=$DATA_ROOT/$EXPN/p$ARG
if [ -d "$d" ] && { [ -n "$SMOKE" ] || [ ! -e "$d/block.json" ] || [ -n "${V3_FORCE:-}" ]; }; then
  mv "$d" "$d.attempt-$(date +%s)"     # never append to an earlier attempt's runs.jsonl
fi
{ [ -n "$SMOKE" ] || [ -n "$STOPTEST" ]; } && export V3_FORCE=1
block_begin "$EXPN" "$ARG"
{ sha256sum tools/claims-v3/lib.sh $(find "$HERE" -maxdepth 1 -type f | sort) "$HOST_BIN" 2>/dev/null; } > "$OUT/code.sha256"
IDLE_MHZ0=$(clock_mhz || true)
case "$IDLE_MHZ0" in ''|*[!0-9]*) IDLE_MHZ0= ;; esac
log "$EXPN p$ARG: $NRUN items, <= $((MAXS / 60 + 1)) min; idle ${IDLE_MHZ0:-?} MHz (E184 arm S)"
others_present && { finish others "others present before the sampler"; exit 3; }
start_sampler "$OUT/telemetry.jsonl" $((MAXS + 300)) || { finish fail "sampler would not start"; exit 1; }
if [ -n "$STOPTEST" ]; then
  s1=0; s2=0
  python3 -B "$RUNNER" "$OUT/board" --root "$V3_ROOT" --pass "$ARG" --card "$CARD" --stop-path-test --tel-live "$OUT/telemetry.jsonl.raw" \
    --stop-w 1 --stop-c 999 > "$OUT/stoptest-board.out" 2>&1 || s1=$?
  python3 -B "$RUNNER" "$OUT/die" --root "$V3_ROOT" --pass "$ARG" --card "$CARD" --stop-path-test --tel-live "$OUT/telemetry.jsonl.raw" \
    --stop-w 999 --stop-c 1 > "$OUT/stoptest-die.out" 2>&1 || s2=$?
  stop_sampler
  gz_out
  if [ "$s1" = 5 ] && [ "$s2" = 5 ]; then finish ok "stop-path test: board and die stops fired before a run and in the watcher"; exit 0; fi
  finish fail "stop-path test: board rc $s1, die rc $s2 (5 = fired)"; exit 1
fi
rargs=(--root "$V3_ROOT" --pass "$ARG" --tel-live "$OUT/telemetry.jsonl.raw" --card "$CARD")
if [ -n "${V3_DRY:-}" ]; then
  python3 -B "$RUNNER" "$OUT" "${rargs[@]}" --dry; rc=$?
else
  python3 -B "$RUNNER" "$OUT" "${rargs[@]}" > "$OUT/runner.out" 2>&1; rc=$?
fi
stop_sampler
[ "$rc" = 3 ] && { gz_out; finish others "another user or device process appeared during the pass (runner stopped)"; exit 3; }
if [ -n "${V3_DRY:-}" ]; then
  st=ok; note="dry run (runner rc $rc)"
  [ "$rc" != 0 ] && st=fail
else
  res=$(python3 -B "$HERE/check_e184.py" block "$OUT" 2> "$OUT/check.err") || res="fail post-block check crashed: $(tail -1 "$OUT/check.err")"
  res=$(printf '%s\n' "$res" | tail -1); [ -s "$OUT/check.err" ] || rm -f "$OUT/check.err"
  case "${res%% *}" in ok|partial|fail) ;; *) res="fail post-block check printed no status: $res" ;; esac
  st=${res%% *}; note=${res#* }
  [ "$rc" = 5 ] && { st=stop; note="a live stop fired: $(cat "$OUT/stop.json" 2>/dev/null); $note"; }
  [ "$rc" = 4 ] && { st=fail; note="the sampler stopped writing: runner stopped the pass; $note"; }
  [ "$rc" != 0 ] && [ "$rc" != 5 ] && [ "$st" != fail ] && { st=fail; note="runner rc $rc; $note"; }
fi
gz_out
finish "$st" "${note//\"/\'}"
[ "$st" = ok ] && exit 0
[ "$st" = stop ] && exit 5
exit 1
