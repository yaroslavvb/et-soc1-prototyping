#!/usr/bin/env bash
# E178 (Q146, the kit), step 22: collect and score at the desk, on the Intel (it needs this Mac's tree and its ssh to the box; section 28 lets
# that stay here), at nice 10 with at most 2 jobs, every copy bounded, after the run has ended (s20_wait_e178.sh read the session end). A port
# of ../../q141k-runbook/k6/s22_collect_k6_v3.sh's e171 route: the copies back into build/e178-raw (repo-relative), collect_e178.sh (the
# check of C over every listed session, the primary and its arms, score_e178.py), cc_gate over every session that must carry a C log
# (ccsessions_e178.py: ccsessions_p8.py's check, unchanged, on E178's layout), E164's login scrub in --check form, and the desk-path gate.
# The desk test's stand-in for the collector (K6E178_COLLECT) is read only with RB_DESKTEST=1; set without it, the step refuses (10).
# This step commits nothing.
#
#   bash tools/claims-v3/e178/rb/s22_collect_e178.sh
# SPDX-License-Identifier: Apache-2.0
. "$(dirname "${BASH_SOURCE[0]}")/rb_e178.sh"
rb_init s22_collect
rb_window
DAY=$RB_DAY
OUT=build/e178-out/$DAY-e178-one-number-aifoundry3
if [ "${RB_DESKTEST:-}" != 1 ] && [ -n "${K6E178_COLLECT:-}" ]; then
  rb_die $RB_E_USAGE "K6E178_COLLECT is a desk-test stand-in and is read only with RB_DESKTEST=1: unset it (the card day never sets it)"
fi
COL=${K6E178_COLLECT:-tools/claims-v3/e178/collect_e178.sh}
scrub_check() {  # k6's: scrub_check <logs dir> <box>: E164's scrub, --check only (it rewrites nothing)
  local d=$1 box=$2 own
  own=$(cat "$RB_OUT/box-login-$box.txt" 2>/dev/null)
  [ -n "${RB_DRY:-}" ] && own=${own:-LOGIN}
  if [ -z "$own" ]; then rb_say "logs/ in $d: read them by eye for et-who lines before the data commit (no box login recorded by s05_look_k6.sh)"; return 0; fi
  rb_local read local "et-who lines in $d (E164's scrub, --check)" "$RB_PY" -B tools/claims-v3/e164/scrub_etwho_e164.py --check "$d" --owner "$own"
  [ "$RB_RC" -eq 0 ] || rb_die $RB_E_GATE "another login is in $d: scrub it (scrub_etwho_e164.py without --check) before any commit"
}
cc_gate() {  # cc_gate <since, epoch s> <raw copy> <ccheck --out json>: every listed session checked to its end, else 14
  local since=$1 raw=$2 cc=$3
  rb_local read local "E178's sessions that must carry a C log, each checked to its end (ccsessions_e178.py)" \
    "$RB_PY" -B tools/claims-v3/e178/ccsessions_e178.py --run E178 --raw "$raw" --ccheck "$cc" --since "$since"
  [ "$RB_RC" -eq 0 ] || rb_die $RB_E_FAIL "E178: a session that must carry a C log has no finished check of C (the CCSESSION-, CCHECK- and STOPTEST- lines above): nothing is scored as registered. Read the collector's output, remove what it wrote, then collect again"
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
rb_local desk local "collect_e178.sh (the check of C over every listed session, the primary and its arms, score_e178.py)" \
  env PY=/usr/bin/python3 E178_DATE="$DAY" nice -n 10 bash "$COL" "$RAW"
res=0; rb_has '^results\.md written' && res=1
cc_gate "$t_cc" "$RAW" "$OUT/ccheck/ccheck-all.json"
[ "$res" -eq 1 ] || [ -n "${RB_DRY:-}" ] || rb_die $RB_E_FAIL "score_e178 did not write results.md: read the collector's output above"
scrub_check "$OUT/logs" aifoundry3
rb_nopath "$OUT"
rb_say "E178 collected and scored: $OUT (the data directory is docs/reports/data/$DAY-e178-one-number-aifoundry3/)"
