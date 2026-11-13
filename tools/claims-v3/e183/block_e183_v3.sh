#!/usr/bin/env bash
# E183 (the kit's dated note 6, KIT.md.dated-note-6.md, Fri 13 Nov 2026, before any E183 train datum): one block, v3. It is block_e183_v2.sh
# (24b9b99e, which stays as committed) with TWO changes, each marked "note 6":
#   (1) THE POST-BLOCK CHECK RUNS ON A TRAIN BLOCK ONLY. v2 ran check_e183.py block on every real block that reached its end, the smoke
#       included (the stop-path test ends at its own lines before it). check_e183.py's block() reads a train block of the plan (its record
#       names the block's train, its anchors and its processes, through e183_common.train_of_block) and raises for any other block, so on
#       aifoundry3 on Fri 13 Nov 2026 the smoke 18301 ended "fail post-block check crashed: KeyError: 'block 18301 is not a planned train
#       block (18310-18315)'" after its own gate had read SMOKE GO, and the session stopped at its smoke gate. Under V3_DRY the check is
#       skipped, so no dry pass could see it. v3 runs the check on a train block exactly as v2 does; on the smoke it runs none and writes
#       the runner's status with a note naming the smoke's registered gate (check_e183.py smoke, E183.md section 7), which the session runs
#       right after the block. Every stop, refusal and exit code is v2's;
#   (2) the harness check is harness_e183_v3.py (v2's check, then note 6's box files at their pins). pass.json's "kit" reads "note6".
# Everything else is v2's, line for line. Run by session_e183_v3.sh and queue_e183_v3.sh, and by rb/s10_a3_dry_e183_v3.sh under V3_DRY.
# v2's words follow:
# E183 (the kit's dated note 4, KIT.md.dated-note-4.md, Thu 12 Nov 2026, before any E183 datum): one block, v2. It is block_e183.sh
# (cc597bf2, which stays as committed) with TWO changes in its preflight (files only, no device): (1) v1's line 48 grepped the train host
# for '--operands-b' and 'train_kind', which a correctly patched host built by GCC at -O2 fails (the literal is built from immediates), so
# it would have refused every block; v2 runs train_check_e183.sh on the host instead (the host's own behaviour: --list, and the three train
# options with an empty --kernel; neither run reaches a device call); (2) the harness check is harness_e183_v2.py (v1's 80 files and note
# 4's box files at their pins) in place of check_e183.py harness. pass.json's "kit" reads "note4". Everything else is v1's, line for line.
# Run by session_e183_v2.sh and queue_e183_v2.sh, and by rb/s10_a3_dry_e183_v2.sh under V3_DRY.
# v1's words follow:
# E183 (Q155, the kit): one block of E183 on the local card - a train block (18310-18315), the smoke (18301) or the stop-path test (18302).
# E180's block v2 (tools/claims-v3/e180/block_e180_v2.sh, which ran on aifoundry3 on 6 Nov 2026), ported: the same lib.sh, the same D1
# other-user rule (others_d1_e180.sh, sourced after lib.sh), every telemetry call through E128's guard and lib.sh's drain refused, the
# preflight on files only, block_begin's card lock, `timeout 10` on every device process (the runner), the 10 Hz sampler with no
# --reset-ms, the stop-path test, the post-block check, gzip, block_end. What differs, for E183: the runner is run_e183.py (a train block's
# anchors and processes, or the smoke), the host is the train host (build/enercat-e183, build_host_e183.sh), the harness check is
# check_e183.py's, and train.jsonl is gzipped beside runs.jsonl and telemetry.jsonl. Nothing is set: no governor, TDP, threshold or clock
# set, no reset, no statistics reset.
#
#   bash tools/claims-v3/e183/block_e183.sh <block>            # 18310-18315, a train block of the plan
#   bash tools/claims-v3/e183/block_e183.sh 18301 --smoke      # the smoke: four 1 s bursts, then two train processes of T5
#   bash tools/claims-v3/e183/block_e183.sh 18302 --stoptest   # the stop-path test: no launch, the stops on live samples
#   V3_DRY=1 bash tools/claims-v3/e183/block_e183.sh <block>   # print every device call, touch nothing
#   E183_PROCESSES=<n> runs only a train block's first n processes (the dry pass's short form; never set by the session)
#
# Data: $DATA_ROOT/e183/p<block>/ (runs, train, telemetry gzipped; configs.json, marks.jsonl, pass.json, check.json, run.log, code.sha256).
# Exit: 0 ok; 1 the block failed; 2 preflight or plan refused; 3 another user or device process; 5 a stop fired.
# SPDX-License-Identifier: Apache-2.0
. "$(dirname "${BASH_SOURCE[0]}")/../lib.sh"      # cd's to the tree root; CARD, GOV_FREE, DATA_ROOT, ET_DEVICES
ETTELEM=tools/claims-v3/e128/ettelem_guard.sh
drain_mgmt() { log "E183: drain refused: dev_mngt_service is not in E183's classified command list"; return 0; }
. tools/claims-v3/e180/others_d1_e180.sh
[ "${V3_DEVICE:-}" = 0 ] && { echo "E183 never runs on aifoundry1 card 0" >&2; exit 2; }
[ -n "${V3_DEVICE:-}" ] && { echo "E183 is kitted for aifoundry3 card 0 alone" >&2; exit 2; }
others_present && exit 3
if ours_running; then log "one of our own device processes on this card is still running"; exit 3; fi

ARG=${1:?usage: block_e183.sh <block> [--smoke | --stoptest]}
SMOKE=; [ "${2:-}" = --smoke ] && SMOKE=1
STOPTEST=; [ "${2:-}" = --stoptest ] && STOPTEST=1
case "$ARG" in ''|*[!0-9]*) echo "block must be a number" >&2; exit 2 ;; esac
HERE=tools/claims-v3/e183
RUNNER=$HERE/run_e183.py
HOST_BIN=build/enercat-e183/host/enercat_host
EXPN=e183; [ -n "$SMOKE" ] && EXPN=e183-smoke; [ -n "$STOPTEST" ] && EXPN=e183-stoptest
MODE=(--block "$ARG"); [ -n "$SMOKE" ] && MODE=(--smoke)
PROC=(); [ -n "${E183_PROCESSES:-}" ] && PROC=(--processes "$E183_PROCESSES")

# ---- preflight: files only, no device --------------------------------------------------------------------------
pf=()
python3 -c 'import numpy' 2>/dev/null || pf+=("python3 has no numpy (analyze_catalogue.py needs it)")
[ -f workloads/enercat/analyze_catalogue.py ] || pf+=("missing workloads/enercat/analyze_catalogue.py (post-block check)")
[ -x "$HOST_BIN" ] || pf+=("missing $HOST_BIN (the train host: build_host_e183.sh)")
[ -x "$ETTELEM" ] || pf+=("missing $ETTELEM")
[ -x build/ettelem/ettelem ] || pf+=("missing build/ettelem/ettelem (the reader $ETTELEM execs)")
if [ -x "$HOST_BIN" ]; then
  tc=$(bash "$HERE/train_check_e183.sh" "$HOST_BIN" 2>&1) || pf+=("$HOST_BIN lacks the train change: $(printf '%s\n' "$tc" | tail -n 1 | cut -c1-240)")   # note 4: v1's line 48
  grep -a -q -- 'file:' "$HOST_BIN" || pf+=("$HOST_BIN has no --operands file:")
  kelf=$(grep -a -o '/[[:alnum:]/._-]*/enercat\.elf' "$HOST_BIN" | head -1)
  [ -n "$kelf" ] && [ ! -f "$kelf" ] && pf+=("kernel $kelf (compiled into $HOST_BIN) not found")
fi
BIN=--binaries; [ -n "${V3_DRY:-}" ] && BIN=
CHK=$(python3 -B "$HERE/harness_e183_v3.py" $BIN 2>&1) || pf+=("harness: $CHK")      # note 6: v2's check, then note 6's box files
LIST=
if [ ${#pf[@]} -eq 0 ] && [ -z "$STOPTEST" ]; then
  LIST=$(python3 -B "$RUNNER" /dev/null --root "$V3_ROOT" "${MODE[@]}" ${PROC[@]+"${PROC[@]}"} --list 2>&1) || pf+=("runner --list: $LIST")
fi
[ -n "$STOPTEST" ] && [ "$ARG" != 18302 ] && pf+=("the stop-path test is block 18302")
[ -n "$SMOKE" ] && [ "$ARG" != 18301 ] && pf+=("the smoke is block 18301")
if [ ${#pf[@]} -gt 0 ]; then printf 'preflight: %s\n' "${pf[@]}" >&2; exit 2; fi
if [ -n "$STOPTEST" ]; then NB=0; NP=0; MAXS=30
else
  NB=$(python3 -c 'import json,sys; print(json.loads(sys.argv[1])["n_bursts"])' "$LIST")
  NP=$(python3 -c 'import json,sys; print(json.loads(sys.argv[1])["n_processes"])' "$LIST")
  MAXS=$(python3 -c 'import json,sys; print(json.loads(sys.argv[1])["max_s"])' "$LIST")
fi

# ---- the block ---------------------------------------------------------------------------------------------------
eval "lib_die_c() $(declare -f die_c | tail -n +2)"
finish() {  # finish <status> <note>
  if [ "$1" = others ]; then die_c() { echo null; }; else die_c() { local t; t=$(lib_die_c); echo "${t:-null}"; }; fi
  block_end "$1" "$2"
}
gz_out() { local f; for f in telemetry.jsonl runs.jsonl train.jsonl; do [ -s "$OUT/$f" ] && gzip -f "$OUT/$f"; done; return 0; }
d=$DATA_ROOT/$EXPN/p$ARG
if [ -d "$d" ] && { [ -n "$SMOKE" ] || [ ! -e "$d/block.json" ] || [ -n "${V3_FORCE:-}" ]; }; then
  mv "$d" "$d.attempt-$(date +%s)"     # never append to an earlier attempt's records
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
json.dump({"exp": "e183", "kit": "note6", "card": "$CARD", "pass": $ARG, "smoke": bool("$SMOKE"), "stoptest": bool("$STOPTEST"),
           "gov_free": bool("$GOV_FREE"), "n_bursts": $NB, "n_processes": $NP, "host_bin": "$HOST_BIN", "runner": "$RUNNER",
           "idle_mhz_start": ${IDLE_MHZ0:-None}, "max_s": $MAXS, "processes_cap": "${E183_PROCESSES:-}" or None},
          open(sys.argv[1], "w"), indent=1)
EOF
log "$EXPN p$ARG: $NB bursts, $NP train processes, <= $((MAXS / 60 + 1)) min; idle ${IDLE_MHZ0:-?} MHz"
others_present && { finish others "others present before the sampler"; exit 3; }
start_sampler "$OUT/telemetry.jsonl" $((MAXS + 300)) || { finish fail "sampler would not start"; exit 1; }
if [ -n "$STOPTEST" ]; then
  s1=0; s2=0
  python3 -B "$RUNNER" "$OUT/board" --root "$V3_ROOT" --stop-path-test --tel-live "$OUT/telemetry.jsonl.raw" \
    --stop-w 1 --stop-c 999 > "$OUT/stoptest-board.out" 2>&1 || s1=$?
  python3 -B "$RUNNER" "$OUT/die" --root "$V3_ROOT" --stop-path-test --tel-live "$OUT/telemetry.jsonl.raw" \
    --stop-w 999 --stop-c 1 > "$OUT/stoptest-die.out" 2>&1 || s2=$?
  stop_sampler
  gz_out
  if [ "$s1" = 5 ] && [ "$s2" = 5 ]; then finish ok "stop-path test: board and die stops fired before a run and in the watcher"; exit 0; fi
  finish fail "stop-path test: board rc $s1, die rc $s2 (5 = fired)"; exit 1
fi
rargs=(--root "$V3_ROOT" "${MODE[@]}" ${PROC[@]+"${PROC[@]}"} --tel-live "$OUT/telemetry.jsonl.raw" --card "$CARD")
if [ -n "${V3_DRY:-}" ]; then
  python3 -B "$RUNNER" "$OUT" "${rargs[@]}" --dry; rc=$?
else
  python3 -B "$RUNNER" "$OUT" "${rargs[@]}" > "$OUT/runner.out" 2>&1; rc=$?
fi
stop_sampler
[ "$rc" = 3 ] && { gz_out; finish others "another user or device process appeared during the block (runner stopped)"; exit 3; }
if [ -n "${V3_DRY:-}" ]; then
  st=ok; note="dry run (runner rc $rc)"
  [ "$rc" != 0 ] && st=fail
else
  if [ -n "$SMOKE" ]; then     # note 6: the post-block check reads a train block of the plan only; the smoke's check is its gate
    res="ok smoke: no post-block check (check_e183.py block reads a train block only, note 6); its gate is check_e183.py smoke, run by the session next"
  else
    res=$(python3 -B "$HERE/check_e183.py" block "$OUT" --card "$CARD" --root "$V3_ROOT" 2> "$OUT/check.err") ||
      res="fail post-block check crashed: $(tail -1 "$OUT/check.err")"
    res=$(printf '%s\n' "$res" | tail -1); [ -s "$OUT/check.err" ] || rm -f "$OUT/check.err"
  fi
  case "${res%% *}" in ok|partial|fail) ;; *) res="fail post-block check printed no status: $res" ;; esac
  st=${res%% *}; note=${res#* }
  [ "$rc" = 5 ] && { st=stop; note="a live stop fired: $(cat "$OUT/stop.json" 2>/dev/null); $note"; }
  [ "$rc" = 4 ] && { st=fail; note="the sampler stopped writing: runner stopped the block; $note"; }
  [ "$rc" = 7 ] && { st=fail; note="three train processes in a row gave no record; $note"; }
  [ "$rc" != 0 ] && [ "$rc" != 5 ] && [ "$st" != fail ] && { st=fail; note="runner rc $rc; $note"; }
fi
gz_out
finish "$st" "${note//\"/\'}"
[ "$st" = ok ] && exit 0
[ "$st" = stop ] && exit 5
exit 1
