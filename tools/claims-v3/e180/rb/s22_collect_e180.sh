#!/usr/bin/env bash
# E180 (Q146(f), the kit), step 22: collect and score at the desk, on the Intel (it needs this Mac's tree and its ssh to the box), at nice 10,
# every copy bounded, after the run has ended (s20_wait_e180.sh read the session end): the copies back into build/e180-raw (repo-relative),
# the stop-path test checked to have launched nothing, collect_e180.sh (reduce_e180.py and score_e180.py), E164's login scrub in --check
# form, and the desk-path gate. The desk test's stand-in for the collector (K6E180_COLLECT) is read only with RB_DESKTEST=1; set without
# it, the step refuses (10). This step commits nothing. tools/claims-v3/e178/rb/s22_collect_e178.sh's form, without its check of C (the
# energy catalogue's host keeps no C log).
#
#   bash tools/claims-v3/e180/rb/s22_collect_e180.sh
# SPDX-License-Identifier: Apache-2.0
. "$(dirname "${BASH_SOURCE[0]}")/rb_e180.sh"
rb_init s22_collect
rb_window
DAY=$RB_DAY
OUT=build/e180-out/$DAY-e180-vector-add-aifoundry3
if [ "${RB_DESKTEST:-}" != 1 ] && [ -n "${K6E180_COLLECT:-}" ]; then
  rb_die $RB_E_USAGE "K6E180_COLLECT is a desk-test stand-in and is read only with RB_DESKTEST=1: unset it (the card day never sets it)"
fi
COL=${K6E180_COLLECT:-tools/claims-v3/e180/collect_e180.sh}
scrub_check() {  # k6's: scrub_check <logs dir> <box>: E164's scrub, --check only (it rewrites nothing)
  local d=$1 box=$2 own
  own=$(cat "$RB_OUT/box-login-$box.txt" 2>/dev/null)
  [ -n "${RB_DRY:-}" ] && own=${own:-LOGIN}
  if [ -z "$own" ]; then rb_say "logs/ in $d: read them by eye for et-who lines before the data commit (no box login recorded by s05_look_k6.sh)"; return 0; fi
  rb_local read local "et-who lines in $d (E164's scrub, --check)" "$RB_PY" -B tools/claims-v3/e164/scrub_etwho_e164.py --check "$d" --owner "$own"
  [ "$RB_RC" -eq 0 ] || rb_die $RB_E_GATE "another login is in $d: scrub it (scrub_etwho_e164.py without --check) before any commit"
}
RAW=build/e180-raw
[ -n "${RB_DRY:-}" ] || mkdir -p "$RAW/logs"
rb_probe aifoundry3
rb_local copy aifoundry3 "copy back E180's passes, smoke and stop-path test (KIT.md box step 11)" \
  rsync -a -e "$RB_RSH" aifoundry3:aifoundry/build/claims-v3/aifoundry3/e180 \
  aifoundry3:aifoundry/build/claims-v3/aifoundry3/e180-smoke aifoundry3:aifoundry/build/claims-v3/aifoundry3/e180-stoptest "$RAW/"
[ "$RB_RC" -eq 0 ] || rb_die $RB_E_FAIL "the copy back exited non-zero"
rb_local copy aifoundry3 "copy back E180's session logs" rsync -a -e "$RB_RSH" aifoundry3:aifoundry/build/e180/ "$RAW/logs/"
[ "$RB_RC" -eq 0 ] || rb_die $RB_E_FAIL "the logs' copy exited non-zero"
if [ -z "${RB_DRY:-}" ]; then
  for f in "$RAW"/e180-stoptest/p18002/runs.jsonl "$RAW"/e180-stoptest/p18002/runs.jsonl.gz; do
    [ -s "$f" ] && rb_die $RB_E_FAIL "STOPTEST-LAUNCHED: the stop-path test recorded a launch ($f): nothing is scored as registered"
  done
fi
rb_local desk local "collect_e180.sh (reduce_e180.py, score_e180.py)" env PY=/usr/bin/python3 E180_DATE="$DAY" nice -n 10 bash "$COL" "$RAW"
rb_has '^scored-e180\.md written' || [ -n "${RB_DRY:-}" ] || rb_die $RB_E_FAIL "score_e180 did not write scored-e180.md: read the collector's output above"
scrub_check "$OUT/logs" aifoundry3
rb_nopath "$OUT"
rb_say "E180 collected and scored: $OUT (the data directory is docs/reports/data/$DAY-e180-vector-add-aifoundry3/)"
