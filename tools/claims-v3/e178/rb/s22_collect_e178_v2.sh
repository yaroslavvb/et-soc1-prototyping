#!/usr/bin/env bash
# E178 (Q146; the kit's dated note 1, ../KIT.md.dated-note-1.md sections 3 and 4), step 22, v2: collect and score at the desk, on the Intel,
# at nice 10 with at most 2 jobs, every copy bounded, after the run has ended (s20_wait_e178.sh read the session end). It replaces
# s22_collect_e178.sh (v1, which stays as committed) in the runbook. v1's copies, its C-session gate and its desk-path gate are unchanged.
# Three changes:
#   1. the collector is ../collect_e178_v2.sh: an arm that fails is dropped, with one line in arms-dropped.txt, and the session scored again
#      without it, so a failed arm's traceback (this Mac's paths) never reaches the output (the kit verifier's fault 4);
#   2. the login scrub's check reads EVERY directory of the output with ../scrub_tree_e178.py --check (E164's patterns, unchanged, and
#      run_e78.py's own "another user on this card: [...]" stop line, which E164's --check does not read), where v1 read logs/ only with
#      E164's (the kit verifier's fault 3; the day critic's kit v4 item 2). Without a recorded box login every login counts as another's;
#   3. that check runs LAST, after the desk-path gate, so a stop there leaves one remedy, named in its message: scrub_tree_e178.py without
#      --check (it rewrites the lines in place), then its --check again; every other gate has already passed.
# The desk test's stand-in for the collector (K6E178_COLLECT) is read only with RB_DESKTEST=1; set without it, the step refuses (10).
# This step commits nothing.
#
#   bash tools/claims-v3/e178/rb/s22_collect_e178_v2.sh
# SPDX-License-Identifier: Apache-2.0
. "$(dirname "${BASH_SOURCE[0]}")/rb_e178.sh"
rb_init s22_collect_v2
rb_window
DAY=$RB_DAY
OUT=build/e178-out/$DAY-e178-one-number-aifoundry3
if [ "${RB_DESKTEST:-}" != 1 ] && [ -n "${K6E178_COLLECT:-}" ]; then
  rb_die $RB_E_USAGE "K6E178_COLLECT is a desk-test stand-in and is read only with RB_DESKTEST=1: unset it (the card day never sets it)"
fi
COL=${K6E178_COLLECT:-tools/claims-v3/e178/collect_e178_v2.sh}
cc_gate() {  # v1's: cc_gate <since, epoch s> <raw copy> <ccheck --out json>: every listed session checked to its end, else 14
  local since=$1 raw=$2 cc=$3
  rb_local read local "E178's sessions that must carry a C log, each checked to its end (ccsessions_e178.py)" \
    "$RB_PY" -B tools/claims-v3/e178/ccsessions_e178.py --run E178 --raw "$raw" --ccheck "$cc" --since "$since"
  [ "$RB_RC" -eq 0 ] || rb_die $RB_E_FAIL "E178: a session that must carry a C log has no finished check of C (the CCSESSION-, CCHECK- and STOPTEST- lines above): nothing is scored as registered. Read the collector's output, remove what it wrote, then collect again"
}
scrub_tree() {  # v2: scrub_tree <output dir> <box>: every directory of the output, --check only (it rewrites nothing)
  local d=$1 box=$2 own
  own=$(cat "$RB_OUT/box-login-$box.txt" 2>/dev/null)
  [ -n "${RB_DRY:-}" ] && own=${own:-LOGIN}
  [ -n "$own" ] || rb_say "no box login recorded by s05_look_k6.sh: every login in $d counts as another account's"
  rb_local read local "another account's login or uid in any directory of $d (scrub_tree_e178.py --check)" \
    "$RB_PY" -B tools/claims-v3/e178/scrub_tree_e178.py --check "$d" ${own:+--owner "$own"}
  [ "$RB_RC" -eq 0 ] || rb_die $RB_E_GATE "another account's login or uid is left in $d (the scrub-tree lines above). Every other gate has passed. Before any commit: python3 -B tools/claims-v3/e178/scrub_tree_e178.py $d${own:+ --owner $own} (it rewrites those lines in place), then the same with --check (0 left), and name it in the data README"
}
RAW=build/e178-raw
[ -n "${RB_DRY:-}" ] || mkdir -p "$RAW/logs"
rb_probe aifoundry3
rb_local copy aifoundry3 "copy back E178's passes, smoke and stop test (KIT.md box step 11)" \
  rsync -a -e "$RB_RSH" aifoundry3:aifoundry/build/claims-v3/aifoundry3/e178 \
  aifoundry3:aifoundry/build/claims-v3/aifoundry3/e178-smoke aifoundry3:aifoundry/build/claims-v3/aifoundry3/e178-stoptest "$RAW/"
[ "$RB_RC" -eq 0 ] || rb_die $RB_E_FAIL "the copy back exited non-zero"
rb_local copy aifoundry3 "copy back E178's session logs" rsync -a -e "$RB_RSH" aifoundry3:aifoundry/build/e178/ "$RAW/logs/"
[ "$RB_RC" -eq 0 ] || rb_die $RB_E_FAIL "the logs' copy exited non-zero"
t_cc=$(date +%s)
rb_local desk local "collect_e178_v2.sh (the check of C over every listed session, the primary and its arms, score_e178.py; a failed arm dropped)" \
  env PY=/usr/bin/python3 E178_DATE="$DAY" nice -n 10 bash "$COL" "$RAW"
res=0; rb_has '^results\.md written' && res=1
cc_gate "$t_cc" "$RAW" "$OUT/ccheck/ccheck-all.json"
[ "$res" -eq 1 ] || [ -n "${RB_DRY:-}" ] || rb_die $RB_E_FAIL "score_e178 did not write results.md: read the collector's output above"
rb_nopath "$OUT"
scrub_tree "$OUT" aifoundry3
dr=0; [ -z "${RB_DRY:-}" ] && [ -s "$OUT/arms-dropped.txt" ] && dr=$(($(grep -c . "$OUT/arms-dropped.txt") - 1))
rb_say "E178 collected and scored: $OUT (the data directory is docs/reports/data/$DAY-e178-one-number-aifoundry3/); arms dropped: $dr$([ "$dr" -gt 0 ] && echo " (arms-dropped.txt: name them in the data README, as KIT.md.dated-note-1.md section 4 registers)")"
