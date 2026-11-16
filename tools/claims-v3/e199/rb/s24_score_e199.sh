#!/usr/bin/env bash
# E199 (Q191, lane kit-e199, Sun 15 Nov 2026, before any E199 datum), the desk step "the reduction and the transport scorer" (this file is
# s24; the card lane's step 13), AFTER THE DATA COMMIT ONLY. E192's step 13 (tools/claims-v3/e192/rb/s24_reduce_e192.sh, unchanged beside
# it) with E199.md sections 6.5 and 16's pipeline, every program at its registered sha256, unchanged:
#   1. the data directory committed and clean at HEAD; its run/ files unpacked and checked against the session's own MANIFEST.sha256
#      (runs.jsonl, marks.jsonl, telemetry.jsonl: the box's bytes);
#   2. E151's rail filter (prefilter_e199.py, which imports tools/claims-v3/e151/railfilter_e151.py at 87bffb5f...): the filtered run dir;
#   3. E192's registered reducer (proposal/src/reduce_intbits.py, 715fddaa...) on the filtered dir: intbits-e199.json;
#   4. E192's section 7 checker (check_e192.py, unchanged at E192's kit pin ceb99e7c...) on card 1's raw run dir and that reduction:
#      checks-e199.json, set beside E192's checks (REPORTED, never a transport verdict);
#   5. THE TRANSPORT SCORER (score_e199.py score intbits-e199.json --out scores-e199.json --checks checks-e199.json): E199-T1, E199-T2
#      (the headline, family A) and the other families' T1/T2 by E199.md section 6's registered rules; a FAIL is reported as FAIL;
#   6. the unfiltered reduction beside it (reduce_intbits.py on the unfiltered dir: intbits-e199-unfiltered.json, REPORTED).
# Every output goes to RB_OUT (a records lane commits them); no lab file here holds a forecast number of any sealed forecast. Python is
# /usr/bin/python3 -I -B (3.12.3 with the system's numpy 1.26.4 for the reducer); run it in the round's CPU slot and a private /dev.
#   bash tools/claims-v3/e199/rb/s24_score_e199.sh docs/reports/data/<day>-e199-intbits-aifoundry1-c1
# SPDX-License-Identifier: Apache-2.0
. "$(dirname "${BASH_SOURCE[0]}")/rb_e199.sh"
rb_init s24_score
D=${1:-}
case "$D" in docs/reports/data/*-e199-intbits-aifoundry1-c1) ;; *) rb_die $RB_E_USAGE "usage: s24_score_e199.sh docs/reports/data/<day>-e199-intbits-aifoundry1-c1" ;; esac
RED=tools/claims-v3/e192/proposal/src/reduce_intbits.py
CHK=tools/claims-v3/e192/check_e192.py
E=tools/claims-v3/e199
rb_local read local "the data directory tracked at HEAD" git -C "$RB_REPO" ls-files -- "$D/run/runs.jsonl" "$D/run/telemetry.jsonl.gz" "$D/session/MANIFEST.sha256"
[ -n "${RB_DRY:-}" ] || [ "$(grep -c . "$RB_CAP")" = 3 ] || rb_die $RB_E_USAGE "$D is not committed (the reduction runs after the data commit only)"
rb_local read local "the data directory clean" git -C "$RB_REPO" status --porcelain --untracked-files=all -- "$D"
[ -z "${RB_DRY:-}" ] && [ -s "$RB_CAP" ] && rb_die $RB_E_USAGE "$D has uncommitted changes: reduce only the committed data"
rb_local read local "the reducer, the checker, the filter and the scorer at their registered sha256" sha256sum "$RED" "$CHK" "$E/prefilter_e199.py" "$E/score_e199.py" tools/claims-v3/e151/railfilter_e151.py
if [ -z "${RB_DRY:-}" ]; then
  rb_has '^715fddaa36c1ca81889b20f39a649254479cb1db68d797c8a9876e0c0677d0b7 ' || rb_die $RB_E_USAGE "the reducer is not at its registered sha256 (715fddaa...)"
  rb_has "^$(grep -E "  $CHK\$" tools/claims-v3/e192/SHA256SUMS-e192-kit | cut -d' ' -f1) " || rb_die $RB_E_USAGE "check_e192.py is not at E192's kit pin"
  rb_has "^$(grep -E "  $E/prefilter_e199.py\$" $E/SHA256SUMS-e199-registration | cut -d' ' -f1) " || rb_die $RB_E_USAGE "prefilter_e199.py is not at E199's registration pin"
  rb_has "^$(grep -E "  $E/score_e199.py\$" $E/SHA256SUMS-e199-registration | cut -d' ' -f1) " || rb_die $RB_E_USAGE "score_e199.py is not at E199's registration pin"
  rb_has '^87bffb5f' || rb_die $RB_E_USAGE "railfilter_e151.py is not at 87bffb5f..."
fi
IN=$RB_OUT/score-e199/run; FL=$RB_OUT/score-e199/filtered
if [ -z "${RB_DRY:-}" ]; then
  [ -e "$RB_OUT/score-e199" ] && rb_die $RB_E_USAGE "$RB_OUT/score-e199 exists: move it aside first"
  mkdir -p "$IN"
  gzip -dc "$D/run/telemetry.jsonl.gz" > "$IN/telemetry.jsonl" || rb_die $RB_E_FAIL "the telemetry could not be unpacked"
  cp "$D/run/runs.jsonl" "$D/run/marks.jsonl" "$IN/"
  for f in telemetry.jsonl runs.jsonl marks.jsonl; do
    want=$(grep -E "  \./run/$f\$" "$D/session/MANIFEST.sha256" | cut -d' ' -f1)
    [ -n "$want" ] && [ "$(sha256sum "$IN/$f" | cut -d' ' -f1)" = "$want" ] || rb_die $RB_E_GATE "run/$f is not the box's bytes (the session's MANIFEST.sha256): reduce nothing; read why"
  done
fi
rb_local desk local "E151's rail filter (prefilter_e199.py), unchanged" /usr/bin/python3 -I -B $E/prefilter_e199.py "$IN" "$FL"
[ "$RB_RC" -eq 0 ] || rb_die $RB_E_FAIL "the rail filter exited $RB_RC: read its output above"
rb_local desk local "E192's registered reducer on the filtered run, unchanged" /usr/bin/python3 -I -B "$RED" "$FL" --out "$RB_OUT/intbits-e199.json"
[ "$RB_RC" -eq 0 ] || rb_die $RB_E_FAIL "the reducer exited $RB_RC: read its output above"
rb_local desk local "E192's section 7 checker on card 1's data (check_e192.py, unchanged)" /usr/bin/python3 -I -B "$CHK" "$IN" "$RB_OUT/intbits-e199.json" --out "$RB_OUT/checks-e199.json"
rb_has '^CHECKS-E192: ' || [ -n "${RB_DRY:-}" ] || rb_die $RB_E_FAIL "the checker did not run (the lines above)"
rb_local desk local "THE TRANSPORT SCORER (score_e199.py, registered)" /usr/bin/python3 -I -B $E/score_e199.py score "$RB_OUT/intbits-e199.json" --out "$RB_OUT/scores-e199.json" --checks "$RB_OUT/checks-e199.json"
[ "$RB_RC" -eq 0 ] || rb_die $RB_E_FAIL "the scorer exited $RB_RC: read its output above"
rb_local desk local "the unfiltered reduction beside it (REPORTED)" /usr/bin/python3 -I -B "$RED" "$IN" --out "$RB_OUT/intbits-e199-unfiltered.json"
rb_say "scored (Python $(/usr/bin/python3 -V 2>&1 | cut -d' ' -f2)): RB_OUT/intbits-e199.json (filtered, E151's rule), checks-e199.json (E192's section 7 checker, REPORTED beside E192's), scores-e199.json ($(grep -m1 -oE 'E199-T1[^;]*' "$RB_CAP" 2>/dev/null | head -c 80)); the unfiltered reduction beside it; a records lane commits them"
exit 0
