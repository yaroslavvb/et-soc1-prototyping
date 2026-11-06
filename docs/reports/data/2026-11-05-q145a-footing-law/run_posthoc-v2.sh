#!/bin/bash
# Q145(a), the footing law's post hoc study end to end (README.md.dated-note-1.md, item N7): run_posthoc.sh; then rederive_e97.py,
# which run_posthoc.sh leaves out though the README says it re-runs everything; then the note's fix_note1.py; then every output is
# compared byte for byte with its committed copy (E172's three scored files after the README's label for the one scratch path).
#   bash docs/reports/data/2026-11-05-q145a-footing-law/run_posthoc-v2.sh <a scratch directory outside the repository>
# From the lab clone's top, with a python that has numpy (PY=...). It reads committed files only and writes only to the scratch
# directory. Exit 0 if every output matches.
# SPDX-License-Identifier: Apache-2.0
set -u
OUT=${1:?usage: run_posthoc-v2.sh <scratch dir>}
PY=${PY:-/usr/bin/python3}
export PY
D=docs/reports/data/2026-11-05-q145a-footing-law
NOTE=${NOTE:-$D/fix_note1.py}
LABEL='<a gunzipped copy of the committed ccheck/ccheck-session.json.gz>'
bash $D/run_posthoc.sh "$OUT" > "$OUT.run_posthoc.log" 2>&1
$PY -B $D/rederive_e97.py . "$OUT/e97-law.json" > "$OUT.rederive_e97.log" 2>&1
$PY -B "$NOTE" . "$OUT/fix-note1.json" > "$OUT/fix-note1.txt" 2>&1
rc=0
for f in idle.json e97-law.json inrun.json profile.json law.json sim.json fix-note1.json fix-note1.txt; do
  if cmp -s "$OUT/$f" "$D/$f"; then echo "SAME $f"; else echo "DIFF $f"; rc=1; fi
done
for f in $(cd $D/fl7 && ls); do
  if [ ! -f "$OUT/fl7/$f" ]; then echo "MISSING fl7/$f"; rc=1; continue; fi
  if cmp -s "$OUT/fl7/$f" "$D/fl7/$f"; then echo "SAME fl7/$f"; continue; fi
  if sed "s#$OUT/fl7/e172-ccheck-session.json#$LABEL#g" "$OUT/fl7/$f" | cmp -s - "$D/fl7/$f"; then echo "SAME-AFTER-LABEL fl7/$f"
  else echo "DIFF fl7/$f"; rc=1; fi
done
echo "run_posthoc-v2: rc $rc"
exit $rc
