#!/usr/bin/env bash
# E180 (Q146(f); the kit's dated note 1, ../KIT.md.dated-note-1.md sections 2 and 3), step 22, v2: collect and score at the desk, on the Intel
# (it needs this Mac's tree and its ssh to the box), at nice 10, every copy bounded, after the run has ended (s20_wait_e180_v2.sh read the
# session end). It replaces s22_collect_e180.sh (v1, which stays as committed) in the runbook. v1's copies, its stop-path test check and its
# desk-path gate are unchanged. Two changes:
#   1. the collector is ../collect_e180_v2.sh: reduce_e180_v2.py and score_e180_v2.py (every registered rule by v1's code; the registration's
#      dated note A1's rules A1-1, A1-5 and A1-7 and its reported arms), given the box's disassembly check, logs/elfcheck-e180.txt, which the
#      logs' copy brings back from build/e180/ with the session's logs;
#   2. the login check reads EVERY directory of the output with ../../e178/scrub_tree_e178.py --check, unchanged (E164's patterns over the
#      whole tree, the others-present lists of lib.sh and of D1 among them; run_e78's stop list, which E180 never writes, as well), where v1
#      read logs/ only with E164's scrub (the adversarial verifier's fault 5; E178's kit verifier's class, fixed there in 763307e7). The runner
#      writes "others present: ... procs=[uid:pid:comm] holders=[login:pid]" into a pass directory's run.log when D1 stops a pass, which v1
#      never read. It runs LAST, after the desk-path gate, so a stop there leaves one remedy, named in its message: scrub_tree_e178.py
#      without --check (it rewrites the lines in place), then its --check again; every other gate has already passed.
# The desk test's stand-in for the collector (K6E180_COLLECT) is read only with RB_DESKTEST=1; set without it, the step refuses (10). This
# step commits nothing.
#
#   bash tools/claims-v3/e180/rb/s22_collect_e180_v2.sh
# SPDX-License-Identifier: Apache-2.0
. "$(dirname "${BASH_SOURCE[0]}")/rb_e180.sh"
rb_init s22_collect_v2
rb_window
DAY=$RB_DAY
OUT=build/e180-out/$DAY-e180-vector-add-aifoundry3
if [ "${RB_DESKTEST:-}" != 1 ] && [ -n "${K6E180_COLLECT:-}" ]; then
  rb_die $RB_E_USAGE "K6E180_COLLECT is a desk-test stand-in and is read only with RB_DESKTEST=1: unset it (the card day never sets it)"
fi
COL=${K6E180_COLLECT:-tools/claims-v3/e180/collect_e180_v2.sh}
scrub_tree() {  # v2: scrub_tree <output dir> <box>: every directory of the output, --check only (it rewrites nothing)
  local d=$1 box=$2 own
  own=$(cat "$RB_OUT/box-login-$box.txt" 2>/dev/null)
  [ -n "${RB_DRY:-}" ] && own=${own:-LOGIN}
  [ -n "$own" ] || rb_say "no box login recorded by s05_look_k6.sh: every login in $d counts as another account's"
  rb_local read local "another account's login or uid in any directory of $d (scrub_tree_e178.py --check)" \
    "$RB_PY" -B tools/claims-v3/e178/scrub_tree_e178.py --check "$d" ${own:+--owner "$own"}
  [ "$RB_RC" -eq 0 ] || rb_die $RB_E_GATE "another account's login or uid is left in $d (the scrub-tree lines above). Every other gate has passed. Before any commit: python3 -B tools/claims-v3/e178/scrub_tree_e178.py $d${own:+ --owner $own} (it rewrites those lines in place), then the same with --check (0 left), and name it in the data README"
}
RAW=build/e180-raw
[ -n "${RB_DRY:-}" ] || mkdir -p "$RAW/logs"
rb_probe aifoundry3
rb_local copy aifoundry3 "copy back E180's passes, smoke and stop-path test (KIT.md box step 11)" \
  rsync -a -e "$RB_RSH" aifoundry3:aifoundry/build/claims-v3/aifoundry3/e180 \
  aifoundry3:aifoundry/build/claims-v3/aifoundry3/e180-smoke aifoundry3:aifoundry/build/claims-v3/aifoundry3/e180-stoptest "$RAW/"
[ "$RB_RC" -eq 0 ] || rb_die $RB_E_FAIL "the copy back exited non-zero"
rb_local copy aifoundry3 "copy back E180's session logs and the build step's disassembly check" rsync -a -e "$RB_RSH" aifoundry3:aifoundry/build/e180/ "$RAW/logs/"
[ "$RB_RC" -eq 0 ] || rb_die $RB_E_FAIL "the logs' copy exited non-zero"
if [ -z "${RB_DRY:-}" ]; then
  for f in "$RAW"/e180-stoptest/p18002/runs.jsonl "$RAW"/e180-stoptest/p18002/runs.jsonl.gz; do
    [ -s "$f" ] && rb_die $RB_E_FAIL "STOPTEST-LAUNCHED: the stop-path test recorded a launch ($f): nothing is scored as registered"
  done
fi
rb_local desk local "collect_e180_v2.sh (reduce_e180_v2.py, score_e180_v2.py)" env PY=/usr/bin/python3 E180_DATE="$DAY" nice -n 10 bash "$COL" "$RAW"
rb_has '^scored-e180\.md written' || [ -n "${RB_DRY:-}" ] || rb_die $RB_E_FAIL "score_e180_v2 did not write scored-e180.md: read the collector's output above"
rb_nopath "$OUT"
scrub_tree "$OUT" aifoundry3
rb_say "E180 collected and scored (kit v2): $OUT (the data directory is docs/reports/data/$DAY-e180-vector-add-aifoundry3/)"
