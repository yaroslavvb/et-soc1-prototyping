#!/usr/bin/env bash
# Q142(k6), step 22: collect and score at the desk, on the Intel (it needs this Mac's tree and its ssh to the boxes; section 28 lets that
# stay here), at nice 10 with at most 2 jobs, every copy bounded, after the run has ended (s20_wait_k6.sh read the session end). A port of
# ../v3.1/s22_collect.sh's e163 and e164 routes to E171's and E172's kits, with one change (k6) for the Q142 critic's fault 3:
#   cc_gate reads, with tools/claims-v3/p8-600/ccsessions_p8.py, EVERY session that must carry a C log (E171.md and E172.md: the smoke
#   and every pass with a launch record, ok or not, listed from the raw copy by the registered rule), not only the checks that ran: a
#   listed session with no C log, a check that did not finish, a check written before this collection, or a check that judged fewer
#   launches from a session's log than the log holds, stops the step (14) before it says "collected". v3.1's cc_gate read each --out
#   file the collector named, so a pass whose C log was missing was never checked and never missed. A genuine C FAIL is a finished
#   check: it reaches P8-KC, as registered. The C gate's message comes first when the scorer refused for it (exit 4).
# Kept from v3.1: the raw copy repo-relative (build/e171-raw, build/e172-raw), so no desk path enters a data directory; the collector's
# own success line read before anything else; the login scrub's check (E164's scrub_etwho_e164.py, --check, for E171's logs; inside
# collect_e172.sh for E172's, its exit 7 = commit nothing); the desk-path gate (v3.1's nopath_q142s.py) over what the step wrote.
#   e171  two bounded rsyncs from aifoundry3 into build/e171-raw (e171/, e171-smoke/, e171-stoptest/, logs/), then
#         PY=/usr/bin/python3 nice -n 10 bash tools/claims-v3/e171/collect_e171.sh build/e171-raw
#   e172  box/pull_e172.sh (into build/e172-raw), then collect_e172.sh build/e172-raw (E172_OWNER from s05's box login of record)
#   ka    after both: score_p8_600.py ka-pooled <E171 scored.json> <E172 scored.json> -> <E172's out>/ka-pooled.json (P8-KA pooled)
# This step commits nothing. K6_COLLECT_E171 and K6_COLLECT_E172 exist only for the desk test (selftest_runbook_k6.sh): a stand-in
# collector; the card day never sets them.
#
#   bash tools/claims-v3/q141k-runbook/k6/s22_collect_k6.sh e171 | e172 | ka
# SPDX-License-Identifier: Apache-2.0
. "$(dirname "${BASH_SOURCE[0]}")/rb_common.sh"
rb_init s22_collect
run=${1:-}
rb_window
DAY=$RB_DAY
E171OUT=build/e171-out/$DAY-e171-blind8-aifoundry3
E172OUT=build/e172-out/$DAY-e172-blind8-card1
C171=${K6_COLLECT_E171:-tools/claims-v3/e171/collect_e171.sh}
C172=${K6_COLLECT_E172:-tools/claims-v3/e172/collect_e172.sh}

scrub_check() {  # scrub_check <logs dir> <box>: E164's scrub, --check only (it rewrites nothing); v3.1's backstop
  local d=$1 box=$2 own
  own=$(cat "$RB_OUT/box-login-$box.txt" 2>/dev/null)
  [ -n "${RB_DRY:-}" ] && own=${own:-LOGIN}
  if [ -z "$own" ]; then rb_say "logs/ in $d: read them by eye for et-who lines before the data commit (no box login recorded by s05_look_k6.sh)"; return 0; fi
  rb_local read local "et-who lines in $d (E164's scrub, --check)" "$RB_PY" -B tools/claims-v3/e164/scrub_etwho_e164.py --check "$d" --owner "$own"
  [ "$RB_RC" -eq 0 ] || rb_die $RB_E_GATE "another login is in $d: scrub it (scrub_etwho_e164.py without --check) before any commit"
}
cc_gate() {  # k6: cc_gate <run> <since, epoch s> <raw copy> <ccheck --out json>: every listed session checked to its end, else 14
  local r=$1 since=$2 raw=$3 cc=$4
  rb_local read local "$r's sessions that must carry a C log, each checked to its end (ccsessions_p8.py)" \
    "$RB_PY" -B "$RB_P8/ccsessions_p8.py" --run "$r" --raw "$raw" --ccheck "$cc" --since "$since"
  [ "$RB_RC" -eq 0 ] || rb_die $RB_E_FAIL "$r: a session that must carry a C log has no finished check of C (the CCSESSION-, CCHECK- and STOPTEST- lines above): nothing is scored as registered. Read the collector's output, remove what it wrote, then collect again"
}

case "$run" in
  e171)
    RAW=build/e171-raw
    [ -n "${RB_DRY:-}" ] || mkdir -p "$RAW/logs"
    rb_probe aifoundry3
    rb_local copy aifoundry3 "copy back E171's passes, smoke and stop test (README step 11)" \
      rsync -a -e "$RB_RSH" aifoundry3:aifoundry/build/claims-v3/aifoundry3/e171 \
      aifoundry3:aifoundry/build/claims-v3/aifoundry3/e171-smoke aifoundry3:aifoundry/build/claims-v3/aifoundry3/e171-stoptest "$RAW/"
    [ "$RB_RC" -eq 0 ] || rb_die $RB_E_FAIL "the copy back exited non-zero"
    rb_local copy aifoundry3 "copy back E171's session logs" rsync -a -e "$RB_RSH" aifoundry3:aifoundry/build/e171/ "$RAW/logs/"
    [ "$RB_RC" -eq 0 ] || rb_die $RB_E_FAIL "the logs' copy exited non-zero"
    t_cc=$(date +%s)
    rb_local desk local "collect_e171.sh (the check of C over every listed session, the primary and its arms, the P8 scorer)" \
      env PY=/usr/bin/python3 E171_DATE="$DAY" nice -n 10 bash "$C171" "$RAW"
    res=0; rb_has '^results\.md written' && res=1
    cc_gate E171 "$t_cc" "$RAW" "$E171OUT/ccheck/ccheck-all.json"
    [ "$res" -eq 1 ] || [ -n "${RB_DRY:-}" ] || rb_die $RB_E_FAIL "score_p8_600 did not write results.md: read the collector's output above"
    scrub_check "$E171OUT/logs" aifoundry3
    rb_nopath "$E171OUT"
    rb_say "E171 collected and scored: $E171OUT (the data directory is docs/reports/data/$DAY-e171-blind8-aifoundry3/)"
    ;;
  e172)
    rb_probe aifoundry1
    rb_local copy aifoundry1 "box/pull_e172.sh (E172 box step 7)" bash tools/claims-v3/e172/box/pull_e172.sh
    { [ "$RB_RC" -eq 0 ] && ! rb_has '^rsync .* failed$'; } || [ -n "${RB_DRY:-}" ] || rb_die $RB_E_FAIL "pull_e172.sh did not copy everything: run this step again"
    own=$(cat "$RB_OUT/box-login-aifoundry1.txt" 2>/dev/null)
    t_cc=$(date +%s)
    rb_local desk local "collect_e172.sh (the check of C over every listed session, the primary and its arms, the P8 scorer, the scrub)" \
      env PY=/usr/bin/python3 E172_DATE="$DAY" ${own:+E172_OWNER=$own} nice -n 10 bash "$C172" build/e172-raw
    if [ -n "${RB_DRY:-}" ]; then cc_gate E172 "$t_cc" build/e172-raw "$E172OUT/ccheck/ccheck-session.json"; rb_nopath "$E172OUT"; exit 0; fi
    rb_has '^scrub (check )?failed' && rb_die $RB_E_GATE "collect_e172.sh's scrub failed: commit nothing (its exit 7)"
    res=0; rb_has '^results\.md written' && res=1
    cc_gate E172 "$t_cc" build/e172-raw "$E172OUT/ccheck/ccheck-session.json"
    [ "$res" -eq 1 ] || rb_die $RB_E_FAIL "score_p8_600 did not write results.md: read the collector's output above"
    rb_nopath "$E172OUT"
    rb_say "E172 collected and scored: $E172OUT (the data directory is docs/reports/data/$DAY-e172-blind8-card1/)"
    ;;
  ka)
    if [ -z "${RB_DRY:-}" ]; then
      [ -s "$E171OUT/scored.json" ] && [ -s "$E172OUT/scored.json" ] || rb_die $RB_E_USAGE "collect E171 and E172 first (s22_collect_k6.sh e171, then e172)"
    fi
    rb_local read local "P8-KA pooled over E171 and E172 (score_p8_600.py ka-pooled)" \
      "$RB_PY" -B "$RB_P8/score_p8_600.py" ka-pooled "$E171OUT/scored.json" "$E172OUT/scored.json" --json "$E172OUT/ka-pooled.json"
    [ "$RB_RC" -eq 0 ] || rb_die $RB_E_FAIL "ka-pooled exited $RB_RC"
    rb_nopath "$E172OUT/ka-pooled.json"
    rb_say "P8-KA pooled read: $(rb_val '"verdict": "([A-Z ]+)"')"
    ;;
  *) rb_die $RB_E_USAGE "usage: s22_collect_k6.sh e171 | e172 | ka" ;;
esac
