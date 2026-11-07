#!/usr/bin/env bash
# E182 (Q153, the kit), step 22: collect and score at the desk, on the Intel, at nice 10 with at most 2 jobs, every copy bounded, after the
# run has ended (s20_wait_e182.sh read the session end). A port of E178's step 22 v2 (tools/claims-v3/e178/rb/s22_collect_e178_v2.sh):
# the copies back (E182's blocks, smoke and stop test, and the session logs), the collector ../collect_e182.sh (the check of C over every
# listed session, each C log once; the kinds reductions with E178's arms; the trains; score_e182.py), the C-session gate
# (ccsessions_e182.py), the desk-path gate, and last the login scrub over every directory (E178's scrub_tree_e178.py, unchanged). This step
# commits nothing; the data commit's message goes through the public-text scan with the files (kit v5's lesson).
# The desk test's stand-in for the collector (K6E182_COLLECT) is read only with RB_DESKTEST=1; set without it, the step refuses (10).
#
#   bash tools/claims-v3/e182/rb/s22_collect_e182.sh
# SPDX-License-Identifier: Apache-2.0
. "$(dirname "${BASH_SOURCE[0]}")/rb_e182.sh"
rb_init s22_collect
rb_window
DAY=$RB_DAY
OUT=build/e182-out/$DAY-e182-one-number-r2-aifoundry3
if [ "${RB_DESKTEST:-}" != 1 ] && [ -n "${K6E182_COLLECT:-}" ]; then
  rb_die $RB_E_USAGE "K6E182_COLLECT is a desk-test stand-in and is read only with RB_DESKTEST=1: unset it (the card day never sets it)"
fi
COL=${K6E182_COLLECT:-tools/claims-v3/e182/collect_e182.sh}
cc_gate() {  # cc_gate <since, epoch s> <raw copy> <ccheck --out json>: every listed session checked to its end, else 14
  local since=$1 raw=$2 cc=$3
  rb_local read local "E182's sessions that must carry a C log, each checked to its end (ccsessions_e182.py)" \
    /usr/bin/python3 -B tools/claims-v3/e182/ccsessions_e182.py --run E182 --raw "$raw" --ccheck "$cc" --since "$since"
  [ "$RB_RC" -eq 0 ] || rb_die $RB_E_FAIL "E182: a session that must carry a C log has no finished check of C (the lines above): nothing is scored as registered. Read the collector's output, remove what it wrote, then collect again"
}
scrub_tree() {  # scrub_tree <output dir> <box>: every directory of the output, --check only (it rewrites nothing)
  local d=$1 box=$2 own
  own=$(cat "$RB_OUT/box-login-$box.txt" 2>/dev/null)
  [ -n "${RB_DRY:-}" ] && own=${own:-LOGIN}
  [ -n "$own" ] || rb_say "no box login recorded by s05_look_k6.sh: every login in $d counts as another account's"
  rb_local read local "another account's login or uid in any directory of $d (scrub_tree_e178.py --check, E178's, unchanged)" \
    /usr/bin/python3 -B tools/claims-v3/e178/scrub_tree_e178.py --check "$d" ${own:+--owner "$own"}
  [ "$RB_RC" -eq 0 ] || rb_die $RB_E_GATE "another account's login or uid is left in $d (the lines above). Every other gate has passed. Before any commit: python3 -B tools/claims-v3/e178/scrub_tree_e178.py $d${own:+ --owner $own} (it rewrites those lines in place), then the same with --check (0 left), and name it in the data README"
}
RAW=build/e182-raw
[ -n "${RB_DRY:-}" ] || mkdir -p "$RAW/logs"
rb_probe aifoundry3
rb_local copy aifoundry3 "copy back E182's blocks, smoke and stop test (KIT.md box step 11)" \
  rsync -a -e "$RB_RSH" aifoundry3:aifoundry/build/claims-v3/aifoundry3/e182 \
  aifoundry3:aifoundry/build/claims-v3/aifoundry3/e182-smoke aifoundry3:aifoundry/build/claims-v3/aifoundry3/e182-stoptest "$RAW/"
[ "$RB_RC" -eq 0 ] || rb_die $RB_E_FAIL "the copy back exited non-zero"
rb_local copy aifoundry3 "copy back E182's session logs and the train host's build record" rsync -a -e "$RB_RSH" aifoundry3:aifoundry/build/e182/ \
  aifoundry3:aifoundry/build/e182host/SHA256 aifoundry3:aifoundry/build/e182-build-host.txt "$RAW/logs/"
[ "$RB_RC" -eq 0 ] || rb_die $RB_E_FAIL "the logs' copy exited non-zero"
t_cc=$(date +%s)
rb_local desk local "collect_e182.sh (the check of C over every listed session, the kinds passes and their arms, the trains, score_e182.py)" \
  env PY=/usr/bin/python3 E182_DATE="$DAY" nice -n 10 bash "$COL" "$RAW"
res=0; rb_has '^results\.md written' && res=1
cc_gate "$t_cc" "$RAW" "$OUT/ccheck/ccheck-all.json"
[ "$res" -eq 1 ] || [ -n "${RB_DRY:-}" ] || rb_die $RB_E_FAIL "score_e182 did not write results.md: read the collector's output above"
rb_nopath "$OUT"
scrub_tree "$OUT" aifoundry3
dr=0; [ -z "${RB_DRY:-}" ] && [ -s "$OUT/arms-dropped.txt" ] && dr=$(($(grep -c . "$OUT/arms-dropped.txt") - 1))
rb_say "E182 collected and scored: $OUT (the data directory is docs/reports/data/$DAY-e182-one-number-r2-aifoundry3/); arms dropped: $dr; before the data commit, scan its message with the files"
