#!/usr/bin/env bash
# E180 (Q146(f); the kit's dated note 1, KIT.md.dated-note-1.md sections 1 and 3): one pass of E180's one-number vector adds on the local
# card, v2. block_e180.sh (v1, which stays as committed) with these changes, each marked v2:
#   1. D1's other-user test (others_d1_e180.sh, E178's and E171's verbatim, sourced after lib.sh): an idle login does not block on aifoundry3
#      or aifoundry1; another user on this card, or any other user's device process, does; it fails closed when et-holders is unreadable.
#      v1 used lib.sh's stock test, which counts every login `who` lists (the adversarial verifier's fault 1);
#   2. the runner is run_e180_v2.py, whose check before every run applies the same D1 rule (v1's ran lib.sh's stock test in a fresh shell);
#   3. E153's change 5, as E171's and E178's change 6 (the verifier's fault 6): every telemetry call goes through
#      tools/claims-v3/e128/ettelem_guard.sh (`ettelem config` and `ettelem sample --seconds --every-ms` only), and lib.sh's drain_mgmt is
#      replaced by a refusal, so the vendor tool dev_mngt_service is never run (v1 left it live); the preflight also checks the real reader
#      the guard execs (build/ettelem/ettelem);
#   4. the harness check is check_e180_v2.py's (harness-e180-v2.json, the v2 file set).
# Everything else is v1's, line for line: the preflight (files only), block_begin's card lock, timeout 10 on every device process, the
# 10 Hz sampler with no --reset-ms, the stop-path test, the post-block check, gzip, block_end. Nothing is set: no governor, TDP, threshold
# or clock set, no reset, no statistics reset.
#
#   bash tools/claims-v3/e180/block_e180_v2.sh <P>            # P = a planned pass (18010-18015)
#   bash tools/claims-v3/e180/block_e180_v2.sh 18001 --smoke  # the smoke: four runs, 1 s bursts, a 3 s lead
#   bash tools/claims-v3/e180/block_e180_v2.sh 18002 --stoptest   # the stop-path test: no launch, the stops on live samples
#   V3_DRY=1 bash tools/claims-v3/e180/block_e180_v2.sh <P>   # print every device call, touch nothing
#   aifoundry1: V3_DEVICE=1 selects card 1 (lib.sh); never card 0
#
# Data: $DATA_ROOT/e180/p<P>/ (runs, telemetry gzipped; configs.json, pass.json, check.json, run.log, code.sha256).
# Exit: 0 ok; 1 the block failed; 2 preflight or plan refused; 3 another user or device process; 5 a stop fired.
# SPDX-License-Identifier: Apache-2.0
. "$(dirname "${BASH_SOURCE[0]}")/../lib.sh"      # cd's to the tree root; CARD, GOV_FREE, DATA_ROOT, ET_DEVICES
ETTELEM=tools/claims-v3/e128/ettelem_guard.sh                                                          # v2 change 3
drain_mgmt() { log "E180: drain refused: dev_mngt_service is not in E180's classified command list"; return 0; }   # v2 change 3
. tools/claims-v3/e180/others_d1_e180.sh                                                               # v2 change 1
[ "${V3_DEVICE:-}" = 0 ] && { echo "E180 never runs on aifoundry1 card 0" >&2; exit 2; }
[ -n "${V3_DEVICE:-}" ] && export V3_DEVICE
others_present && exit 3
if ours_running; then log "one of our own device processes on this card is still running"; exit 3; fi

ARG=${1:?usage: block_e180_v2.sh <pass> [--smoke | --stoptest]}
SMOKE=; [ "${2:-}" = --smoke ] && SMOKE=1
STOPTEST=; [ "${2:-}" = --stoptest ] && STOPTEST=1
case "$ARG" in ''|*[!0-9]*) echo "pass must be a number" >&2; exit 2 ;; esac
HERE=tools/claims-v3/e180
RUNNER=$HERE/run_e180_v2.py                                                                           # v2 change 2
HOST_BIN=build/enercat-e180/host/enercat_host
EXPN=e180; [ -n "$SMOKE" ] && EXPN=e180-smoke; [ -n "$STOPTEST" ] && EXPN=e180-stoptest
SMOKE_ARGS=(); [ -n "$SMOKE" ] && SMOKE_ARGS=(--smoke)

# ---- preflight: files only, no device --------------------------------------------------------------------------
pf=()
python3 -c 'import numpy' 2>/dev/null || pf+=("python3 has no numpy (analyze_catalogue.py needs it)")
[ -f workloads/enercat/analyze_catalogue.py ] || pf+=("missing workloads/enercat/analyze_catalogue.py (post-block check)")
[ -x "$HOST_BIN" ] || pf+=("missing $HOST_BIN (the E180 build: build_e180.sh)")
[ -x "$ETTELEM" ] || pf+=("missing $ETTELEM")
[ -x build/ettelem/ettelem ] || pf+=("missing build/ettelem/ettelem (the reader $ETTELEM execs)")                 # v2 change 3
if [ -x "$HOST_BIN" ]; then
  grep -a -q 'fadd.ps.acc' "$HOST_BIN" && grep -a -q 'fadd.pi.acc' "$HOST_BIN" || pf+=("$HOST_BIN lacks E180's two accumulating modes")
  grep -a -q -- 'file:' "$HOST_BIN" || pf+=("$HOST_BIN has no --operands file:")
  kelf=$(grep -a -o '/[[:alnum:]/._-]*/enercat\.elf' "$HOST_BIN" | head -1)
  [ -n "$kelf" ] && [ ! -f "$kelf" ] && pf+=("kernel $kelf (compiled into $HOST_BIN) not found")
fi
CHK=$(python3 -B "$HERE/check_e180_v2.py" harness 2>&1) || pf+=("harness: $CHK")                         # v2 change 4
LIST=
if [ ${#pf[@]} -eq 0 ] && [ -z "$STOPTEST" ]; then
  LIST=$(python3 -B "$RUNNER" /dev/null --root "$V3_ROOT" --pass "$ARG" ${SMOKE_ARGS[@]+"${SMOKE_ARGS[@]}"} --list 2>&1) || pf+=("runner --list: $LIST")
fi
[ -n "$STOPTEST" ] && [ "$ARG" != 18002 ] && pf+=("the stop-path test is pass 18002")
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
gz_out() { local f; for f in telemetry.jsonl runs.jsonl; do [ -s "$OUT/$f" ] && gzip -f "$OUT/$f"; done; return 0; }
d=$DATA_ROOT/$EXPN/p$ARG
if [ -d "$d" ] && { [ -n "$SMOKE" ] || [ ! -e "$d/block.json" ] || [ -n "${V3_FORCE:-}" ]; }; then
  mv "$d" "$d.attempt-$(date +%s)"     # never append to an earlier attempt's runs.jsonl
fi
{ [ -n "$SMOKE" ] || [ -n "$STOPTEST" ]; } && export V3_FORCE=1
block_begin "$EXPN" "$ARG"
{ sha256sum tools/claims-v3/lib.sh $(find "$HERE" -maxdepth 1 -type f | sort) workloads/enercat/analyze_catalogue.py \
    "$HOST_BIN" 2>/dev/null; } > "$OUT/code.sha256"
IDLE_MHZ0=$(clock_mhz || true)
[ -z "$IDLE_MHZ0" ] && { sleep 2; IDLE_MHZ0=$(clock_mhz || true); }
case "$IDLE_MHZ0" in ''|*[!0-9]*) IDLE_MHZ0= ;; esac
python3 - "$OUT/pass.json" <<EOF
import json, sys
json.dump({"exp": "e180", "kit": "v2", "card": "$CARD", "pass": $ARG, "smoke": bool("$SMOKE"), "gov_free": bool("$GOV_FREE"),
           "v3_device": "${V3_DEVICE:-}" or None, "et_devices": "${ET_DEVICES:-}" or None, "n_runs": $NRUN,
           "host_bin": "$HOST_BIN", "runner": "$RUNNER", "idle_mhz_start": ${IDLE_MHZ0:-None}, "max_s": $MAXS},
          open(sys.argv[1], "w"), indent=1)
EOF
log "$EXPN p$ARG: $NRUN runs, <= $((MAXS / 60 + 1)) min; idle ${IDLE_MHZ0:-?} MHz (kit v2)"
others_present && { finish others "others present before the sampler"; exit 3; }
start_sampler "$OUT/telemetry.jsonl" $((MAXS + 300)) || { finish fail "sampler would not start"; exit 1; }
if [ -n "$STOPTEST" ]; then
  # the stop path on live samples, no launch: a board line of 1 W (the card idles near 26 W), then a die line of 1 C;
  # each must fire before a run and in the in-run watcher (run_e180_v2.py --stop-path-test exits 5 only when both fired)
  s1=0; s2=0
  python3 -B "$RUNNER" "$OUT/board" --root "$V3_ROOT" --pass "$ARG" --stop-path-test --tel-live "$OUT/telemetry.jsonl.raw" \
    --stop-w 1 --stop-c 999 > "$OUT/stoptest-board.out" 2>&1 || s1=$?
  python3 -B "$RUNNER" "$OUT/die" --root "$V3_ROOT" --pass "$ARG" --stop-path-test --tel-live "$OUT/telemetry.jsonl.raw" \
    --stop-w 999 --stop-c 1 > "$OUT/stoptest-die.out" 2>&1 || s2=$?
  stop_sampler
  gz_out
  if [ "$s1" = 5 ] && [ "$s2" = 5 ]; then finish ok "stop-path test: board and die stops fired before a run and in the watcher"; exit 0; fi
  finish fail "stop-path test: board rc $s1, die rc $s2 (5 = fired)"; exit 1
fi
rargs=(--root "$V3_ROOT" --pass "$ARG" ${SMOKE_ARGS[@]+"${SMOKE_ARGS[@]}"} --tel-live "$OUT/telemetry.jsonl.raw" --card "$CARD")
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
  res=$(python3 -B "$HERE/check_e180_v2.py" block "$OUT" --card "$CARD" --root "$V3_ROOT" 2> "$OUT/check.err") ||
    res="fail post-block check crashed: $(tail -1 "$OUT/check.err")"
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
