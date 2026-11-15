#!/usr/bin/env bash
# E192 (Q176, lane kit-e192, Sat 14 Nov 2026, before any E192 datum), the box step "the reduction, after the data commit" (this file is
# s24): THE REGISTERED REDUCER (proposal/src/reduce_intbits.py, sha256 715fddaa..., E192.md section 6), run UNCHANGED at the desk on the
# COMMITTED data only, then the kit's checker for E192.md section 7 (check_e192.py). It refuses (10) unless the data directory is tracked
# at HEAD and clean, and the reducer is at its registered sha256. The reducer reads run/telemetry.jsonl, which the data directory keeps
# gzipped: it is unpacked into RB_OUT/reduce-e192/run/ beside run/runs.jsonl and run/marks.jsonl, and each of the three is checked
# against the session's own MANIFEST.sha256 (the box's bytes) before the reducer reads it. Outputs: RB_OUT/intbits-e192.json (the
# reducer's), RB_OUT/checks-e192.json (the checker's), with the interpreter named; the records lane commits them. NO SCORING: the sealed
# forecasts are the model session's, who scores them privately against these published prices (E192.md section 0).
#   bash tools/claims-v3/e192/rb/s24_reduce_e192.sh docs/reports/data/<day>-e192-intbits-aifoundry3
# SPDX-License-Identifier: Apache-2.0
. "$(dirname "${BASH_SOURCE[0]}")/rb_e192.sh"
rb_init s24_reduce
D=${1:-}
case "$D" in docs/reports/data/*-e192-intbits-aifoundry3) ;; *) rb_die $RB_E_USAGE "usage: s24_reduce_e192.sh docs/reports/data/<day>-e192-intbits-aifoundry3" ;; esac
RED=tools/claims-v3/e192/proposal/src/reduce_intbits.py
rb_local read local "the data directory tracked at HEAD" git -C "$RB_REPO" ls-files -- "$D/run/runs.jsonl" "$D/run/telemetry.jsonl.gz" "$D/session/MANIFEST.sha256"
[ -n "${RB_DRY:-}" ] || [ "$(grep -c . "$RB_CAP")" = 3 ] || rb_die $RB_E_USAGE "$D is not committed (the reducer runs after the data commit only)"
rb_local read local "the data directory clean" git -C "$RB_REPO" status --porcelain --untracked-files=all -- "$D"
[ -z "${RB_DRY:-}" ] && [ -s "$RB_CAP" ] && rb_die $RB_E_USAGE "$D has uncommitted changes: reduce only the committed data"
rb_local read local "the reducer at its registered sha256" sha256sum "$RED"
[ -n "${RB_DRY:-}" ] || rb_has '^715fddaa36c1ca81889b20f39a649254479cb1db68d797c8a9876e0c0677d0b7 ' || rb_die $RB_E_USAGE "the reducer is not at its registered sha256 (715fddaa...)"
IN=$RB_OUT/reduce-e192/run
if [ -z "${RB_DRY:-}" ]; then
  [ -e "$RB_OUT/reduce-e192" ] && rb_die $RB_E_USAGE "$RB_OUT/reduce-e192 exists: move it aside first"
  mkdir -p "$IN"
  gzip -dc "$D/run/telemetry.jsonl.gz" > "$IN/telemetry.jsonl" || rb_die $RB_E_FAIL "the telemetry could not be unpacked"
  cp "$D/run/runs.jsonl" "$D/run/marks.jsonl" "$IN/"
  for f in telemetry.jsonl runs.jsonl marks.jsonl; do
    want=$(grep -E "  \./run/$f\$" "$D/session/MANIFEST.sha256" | cut -d' ' -f1)
    [ -n "$want" ] && [ "$(sha256sum "$IN/$f" | cut -d' ' -f1)" = "$want" ] || rb_die $RB_E_GATE "run/$f is not the box's bytes (the session's MANIFEST.sha256): reduce nothing; read why"
  done
fi
rb_local desk local "the registered reducer, unchanged (/usr/bin/python3 -I -B)" /usr/bin/python3 -I -B "$RED" "$IN" --out "$RB_OUT/intbits-e192.json"
[ "$RB_RC" -eq 0 ] || rb_die $RB_E_FAIL "the reducer exited $RB_RC: read its output above"
rb_local desk local "the section 7 checker (check_e192.py)" /usr/bin/python3 -I -B tools/claims-v3/e192/check_e192.py "$IN" "$RB_OUT/intbits-e192.json" --out "$RB_OUT/checks-e192.json"
rb_has '^CHECKS-E192: ' || [ -n "${RB_DRY:-}" ] || rb_die $RB_E_FAIL "the checker did not run (the lines above)"
rb_say "reduced (the registered reducer, Python $(/usr/bin/python3 -V 2>&1 | cut -d' ' -f2)): RB_OUT/intbits-e192.json; the section 7 checks: $(grep -m1 '^CHECKS-E192: ' "$RB_CAP" 2>/dev/null | cut -c14-200); commit both with the records, no score"
exit 0
