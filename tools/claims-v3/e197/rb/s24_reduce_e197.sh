#!/usr/bin/env bash
# E197 (Q185, the kit), the box step "the reduction, after the data commit" (this file is s24), one sitting a call, on the desk only:
# THE REGISTERED REDUCER, proposal/src/reduce_regfile.py at its sha256 (f325bd0e..., E197.md 7), UNCHANGED, in its registered form
# (`python3 reduce_regfile.py OUT [OUT] --out <json>`: never --prediction; --participants at its default, 1,024), on the COMMITTED data
# directories, never before: each in HEAD, clean, its SHA256SUMS reading every entry OK, and the history check holding. Each sitting's
# run/ (runs.jsonl, marks.jsonl, STOP when there, and the unpacked telemetry.jsonl) is copied into RB_OUT/e197-reduce-<n>/sitting-<k>/,
# each file checked first against the box's own manifest (session/MANIFEST.sha256: the bytes the box wrote), then reduced:
#   sitting 1:  reduce_regfile.py sitting-1 --out regfile-e197-s1.json             (sitting 1's own result)
#   sitting 2:  reduce_regfile.py sitting-1 sitting-2 --out regfile-e197.json      (the pooled reduction: E197's registered result, by
#                                                                                  unit; sitting 1's own stays committed beside it)
# then the kit's checker reads E197.md 8's rows (check_e197.py checks). Its outputs go to RB_OUT (the json, its printed table, the
# checks); the records lane commits them beside the data in a later commit. Nothing here scores anything against the sealed forecast
# (E197.md 0): the model session does that, privately.
#   bash tools/claims-v3/e197/rb/s24_reduce_e197.sh 1|2
# SPDX-License-Identifier: Apache-2.0
. "$(dirname "${BASH_SOURCE[0]}")/rb_e197.sh"
rb_init s24_reduce
sit=${1:-}
e197_sit_ok "$sit" || rb_die $RB_E_USAGE "usage: s24_reduce_e197.sh 1|2"
rb_window
E=tools/claims-v3/e197
D1=$(ls -d "$RB_REPO"/docs/reports/data/*-e197-regfile-sitting-1-aifoundry3 2>/dev/null | head -n 1); D1=${D1#$RB_REPO/}
D2=""; [ "$sit" = 2 ] && { D2=$(ls -d "$RB_REPO"/docs/reports/data/*-e197-regfile-sitting-2-aifoundry3 2>/dev/null | head -n 1); D2=${D2#$RB_REPO/}; }
[ -n "${RB_DRY:-}" ] && { D1=${D1:-docs/reports/data/DAY-e197-regfile-sitting-1-aifoundry3}; [ "$sit" = 2 ] && D2=${D2:-docs/reports/data/DAY-e197-regfile-sitting-2-aifoundry3}; }
[ -n "$D1" ] || rb_die $RB_E_USAGE "no committed sitting-1 data directory (docs/reports/data/*-e197-regfile-sitting-1-aifoundry3): commit it first"
[ "$sit" = 1 ] || [ -n "$D2" ] || rb_die $RB_E_USAGE "no committed sitting-2 data directory: commit it first"
for DATA in $D1 $D2; do
  rb_local read local "the data directory committed (a commit names it): $DATA" git -C "$RB_REPO" log --oneline -1 -- "$DATA"
  [ -n "${RB_DRY:-}" ] || [ -s "$RB_CAP" ] || rb_die $RB_E_USAGE "$DATA is not committed: commit it first (the reduction runs after the data commit)"
  rb_local read local "the data directory clean" git -C "$RB_REPO" status --short --untracked-files=all -- "$DATA"
  [ -z "${RB_DRY:-}" ] && [ -s "$RB_CAP" ] && rb_die $RB_E_GATE "$DATA has uncommitted changes: the reduction reads the committed data only"
  RB_CWD="$RB_REPO/$DATA" rb_local read local "the data's SHA256SUMS, every entry" shasum -a 256 -c SHA256SUMS
  [ -n "${RB_DRY:-}" ] || { [ "$RB_RC" -eq 0 ] && ! grep -qv ': OK$' "$RB_CAP"; } || rb_die $RB_E_GATE "$DATA's SHA256SUMS does not read every entry OK"
done
unset RB_CWD
rb_local read local "the history check" /usr/bin/python3 -I -B $E/rb/check_history_e197.py tree
[ -n "${RB_DRY:-}" ] || rb_has '^HISTORY OK: ' || rb_die $RB_E_GATE "the history check failed"
rb_local read local "the registered reducer at its sha256 (f325bd0e...)" shasum -a 256 $E/proposal/src/reduce_regfile.py
[ -n "${RB_DRY:-}" ] || rb_has '^f325bd0e3e916b81ee12304db7b47d79ad6daa5172ded19952f0ef1b0565eb87 ' || rb_die $RB_E_GATE "reduce_regfile.py is not at its registered sha256"
X=$RB_OUT/e197-reduce-$sit
if [ -n "${RB_DRY:-}" ]; then
  echo "--- desk: for each committed sitting, copy run/runs.jsonl, run/marks.jsonl and run/STOP (when there) and unpack run/telemetry.jsonl.gz into <RB_OUT>/e197-reduce-$sit/sitting-<k>/, each against session/MANIFEST.sha256's ./run/ entries"
else
  [ ! -e "$X" ] || rb_die $RB_E_USAGE "RB_OUT/e197-reduce-$sit exists already: a new RB_OUT, or move it aside"
  k=0
  for DATA in $D1 $D2; do
    k=$((k + 1)); S=$X/sitting-$k
    mkdir -p "$S" || rb_die $RB_E_USAGE "cannot make $S"
    cp "$RB_REPO/$DATA/run/runs.jsonl" "$S/runs.jsonl" && cp "$RB_REPO/$DATA/run/marks.jsonl" "$S/marks.jsonl" ||
      rb_die $RB_E_GATE "no run/runs.jsonl or run/marks.jsonl in $DATA (a sitting with no train data has nothing to reduce)"
    gzip -dc "$RB_REPO/$DATA/run/telemetry.jsonl.gz" > "$S/telemetry.jsonl" || rb_die $RB_E_GATE "run/telemetry.jsonl.gz in $DATA does not unpack"
    [ -f "$RB_REPO/$DATA/run/STOP" ] && cp "$RB_REPO/$DATA/run/STOP" "$S/STOP"
    for p in runs.jsonl marks.jsonl telemetry.jsonl $([ -f "$S/STOP" ] && echo STOP); do
      w=$(awk -v p="./run/$p" '$2 == p {print $1}' "$RB_REPO/$DATA/session/MANIFEST.sha256")
      h=$(shasum -a 256 "$S/$p" | cut -d' ' -f1)
      [ -n "$w" ] && [ "$w" = "$h" ] || rb_die $RB_E_GATE "run/$p of $DATA as committed is not the box's bytes (its manifest says ${w:-nothing}, the copy reads $h)"
    done
  done
  rb_say "each sitting's run/ files (the telemetry unpacked) equal the box's manifest's sha256"
fi
if [ "$sit" = 1 ]; then OUTJ=$RB_OUT/regfile-e197-s1.json; ARGS="$X/sitting-1"; else OUTJ=$RB_OUT/regfile-e197.json; ARGS="$X/sitting-1 $X/sitting-2"; fi
# shellcheck disable=SC2086
rb_local desk local "THE REGISTERED REDUCER, unchanged, on the committed data (reduce_regfile.py $( [ "$sit" = 1 ] && echo 'sitting-1' || echo 'sitting-1 sitting-2: the pooled reduction') --out ...; never --prediction)" \
  /usr/bin/python3 -I -B $E/proposal/src/reduce_regfile.py $ARGS --out "$OUTJ"
[ -n "${RB_DRY:-}" ] || [ "$RB_RC" -eq 0 ] || rb_die $RB_E_FAIL "the reducer exited $RB_RC (its output above)"
[ -n "${RB_DRY:-}" ] || cp "$RB_CAP" "${OUTJ%.json}.txt"
rb_local desk local "the kit's checker: E197.md 8's rows (check_e197.py checks)" \
  /usr/bin/python3 -I -B $E/check_e197.py checks "$OUTJ" --out "$RB_OUT/checks-e197-$sit.json"
[ -n "${RB_DRY:-}" ] && exit 0
rb_has '^CHECKS READ: ' || rb_die $RB_E_FAIL "the checker gave no reading (its output above)"
rb_say "reduced after sitting $sit: $(basename "$OUTJ") and checks-e197-$sit.json in RB_OUT ($(grep -m1 '^CHECKS READ: ' "$RB_CAP" | cut -c1-160)); the records lane commits them beside the data"
