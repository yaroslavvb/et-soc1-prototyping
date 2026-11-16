#!/usr/bin/env bash
# E196 (Q185, lane kit-e196, Sun 15 Nov 2026, PST, before any E196 datum), the box step "the reduction, after the data commit" (this file
# is s24): THE REGISTERED REDUCTION (reduce_e196.py, sha256 c58c6690..., E196.md section 7), run UNCHANGED at the desk on the COMMITTED data
# only, as E196.md 7 writes it: `reduce_e196.py OUT --readback-none-ok --json x14-e196.json`, its defaults otherwise (leakage slope 0.1994
# W/C; rail tau 1.05 s and delay 0.26 s; --min-passes 5; no --drop-pass0), OUT/gen/arms.json the session's regenerated table; then the
# kit's checker for E196.md section 8 (check_e196.py). It refuses (10) unless the data directory is tracked at HEAD and clean, the reducer
# is at its registered sha256 and the session's arms.json is the registered one byte for byte. The reduction reads run/telemetry.jsonl,
# which the data directory keeps gzipped: it is unpacked into RB_OUT/reduce-e196/run/ beside run/runs.jsonl, train.jsonl, checks.jsonl and
# marks.jsonl, and each is checked against the session's own MANIFEST.sha256 (the box's bytes) before the reduction reads it (16 if not).
# Outputs: RB_OUT/x14-e196.json (the reduction's) and its printed lines, RB_OUT/checks-e196.json (the checker's) and its lines, with the
# interpreter named; the records lane commits them beside the data. NO SCORING: the sealed forecast is the model session's, who scores
# it privately against these published prices (E196.md section 0). Never on a gate stop's record; after a crash only once a dated note
# says its blocks are reduced.
#   bash tools/claims-v3/e196/rb/s24_reduce_e196.sh docs/reports/data/<day>-e196-zeroshare-aifoundry3
# SPDX-License-Identifier: Apache-2.0
. "$(dirname "${BASH_SOURCE[0]}")/rb_e196.sh"
rb_init s24_reduce
D=${1:-}
case "$D" in docs/reports/data/*-e196-zeroshare-aifoundry3) ;; *) rb_die $RB_E_USAGE "usage: s24_reduce_e196.sh docs/reports/data/<day>-e196-zeroshare-aifoundry3 (never a gate stop's record)" ;; esac
RED=tools/claims-v3/e196/reduce_e196.py
REDSHA=c58c6690016f18e5dac62ba620086f3cefda812cab9e93d2a929cb1aa207f3f7
rb_local read local "the data directory tracked at HEAD" git -C "$RB_REPO" ls-files -- "$D/run/runs.jsonl" "$D/run/telemetry.jsonl.gz" "$D/session/MANIFEST.sha256" "$D/run/gen/arms.json"
[ -n "${RB_DRY:-}" ] || [ "$(grep -c . "$RB_CAP")" = 4 ] || rb_die $RB_E_USAGE "$D is not committed (the reduction runs after the data commit only)"
rb_local read local "the data directory clean" git -C "$RB_REPO" status --porcelain --untracked-files=all -- "$D"
[ -z "${RB_DRY:-}" ] && [ -s "$RB_CAP" ] && rb_die $RB_E_USAGE "$D has uncommitted changes: reduce only the committed data"
RB_CWD="$RB_REPO/$D" rb_local read local "the data directory's SHA256SUMS, every entry" sha256sum -c --quiet SHA256SUMS
[ -n "${RB_DRY:-}" ] || [ "$RB_RC" -eq 0 ] || rb_die $RB_E_GATE "$D's SHA256SUMS does not hold: reduce nothing; read why"
rb_local read local "the reduction at its registered sha256" sha256sum "$RED"
[ -n "${RB_DRY:-}" ] || rb_has "^$REDSHA " || rb_die $RB_E_USAGE "the reduction is not at its registered sha256 (c58c6690...)"
rb_local read local "the session's arms.json is the registered one (proposal/src/arms.json), byte for byte" cmp "$D/run/gen/arms.json" tools/claims-v3/e196/proposal/src/arms.json
[ -n "${RB_DRY:-}" ] || [ "$RB_RC" -eq 0 ] || rb_die $RB_E_GATE "the session's arms.json is not the registered one: reduce nothing"
IN=$RB_OUT/reduce-e196/run
if [ -z "${RB_DRY:-}" ]; then
  [ -e "$RB_OUT/reduce-e196" ] && rb_die $RB_E_USAGE "$RB_OUT/reduce-e196 exists: move it aside first"
  mkdir -p "$IN/gen"
  gzip -dc "$D/run/telemetry.jsonl.gz" > "$IN/telemetry.jsonl" || rb_die $RB_E_FAIL "the telemetry could not be unpacked"
  for f in runs.jsonl train.jsonl checks.jsonl marks.jsonl STOP; do [ -f "$D/run/$f" ] && cp "$D/run/$f" "$IN/"; done
  cp "$D/run/gen/arms.json" "$IN/gen/"
  for f in telemetry.jsonl runs.jsonl train.jsonl checks.jsonl marks.jsonl; do
    want=$(grep -E "  (\./)?run/$f\$" "$D/session/MANIFEST.sha256" | cut -d' ' -f1)
    [ -n "$want" ] || { [ ! -e "$IN/$f" ] && continue; }
    [ -n "$want" ] && [ "$(sha256sum "$IN/$f" | cut -d' ' -f1)" = "$want" ] || rb_die $RB_E_GATE "run/$f is not the box's bytes (the session's MANIFEST.sha256): reduce nothing; read why"
  done
fi
rb_local desk local "the registered reduction, unchanged (/usr/bin/python3 -I -B): reduce_e196.py OUT --readback-none-ok --json x14-e196.json" \
  /usr/bin/python3 -I -B "$RED" "$IN" --readback-none-ok --json "$RB_OUT/x14-e196.json"
[ "$RB_RC" -eq 0 ] || rb_die $RB_E_FAIL "the reduction exited $RB_RC: read its output above"
cp "$RB_CAP" "$RB_OUT/x14-e196.txt" 2>/dev/null
rb_local desk local "the section 8 checker (check_e196.py)" /usr/bin/python3 -I -B tools/claims-v3/e196/check_e196.py "$IN" "$RB_OUT/x14-e196.json" --out "$RB_OUT/checks-e196.json"
rb_has '^CHECKS-E196: ' || [ -n "${RB_DRY:-}" ] || rb_die $RB_E_FAIL "the checker did not run (the lines above)"
cp "$RB_CAP" "$RB_OUT/checks-e196.txt" 2>/dev/null
rb_say "reduced (the registered reduction, Python $(/usr/bin/python3 -V 2>&1 | cut -d' ' -f2)): RB_OUT/x14-e196.json; the section 8 checks: $(grep -m1 '^CHECKS-E196: ' "$RB_CAP" 2>/dev/null | cut -c14-220); commit both with the records, no score"
exit 0
