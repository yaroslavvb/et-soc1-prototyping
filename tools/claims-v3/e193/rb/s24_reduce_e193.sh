#!/usr/bin/env bash
# E193 (Q177, the kit), the box step "the reduction, after the data commit" (this file is s24), one sitting a call, on the desk only:
# THE REGISTERED REDUCER, proposal/src/reduce_x04.py at its sha256 (98bbc174..., E193.md 7), UNCHANGED, in its registered form
# (`python3 reduce_x04.py OUT --out x04.json`: no --pvt, no --keep-warmup), on the COMMITTED data directory, never before: the directory
# is in HEAD, clean, its SHA256SUMS reads every entry OK, and the history check holds. Its x04/ (runs.jsonl and the unpacked
# telemetry.jsonl) is copied into RB_OUT/e193-reduce-<sitting>/x04/, each checked first against the box's own manifest
# (session/MANIFEST.sha256: the bytes the box wrote), then reduced; then the kit's checker reads E193.md 8's nine checks (check_e193.py
# checks: 1-7 from x04.json, 8's dip count by the reducer's own windows, 9 by section 8's reading). Its outputs go to RB_OUT
# (x04-e193-<sitting>.json, checks-e193-<sitting>.json, the reducer's printed table); the records lane commits them beside the data in a
# later commit. Nothing here scores anything against the sealed forecasts (E193.md 0): the model session does that, privately.
#   bash tools/claims-v3/e193/rb/s24_reduce_e193.sh A|B
# SPDX-License-Identifier: Apache-2.0
. "$(dirname "${BASH_SOURCE[0]}")/rb_e193.sh"
rb_init s24_reduce
sit=${1:-}
e193_cap_s "$sit" > /dev/null || rb_die $RB_E_USAGE "usage: s24_reduce_e193.sh A|B"
rb_window
low=$(echo "$sit" | tr 'AB' 'ab')
DATA=docs/reports/data/${RB_DAY:-DAY}-e193-x04-clock-sitting-$low-aifoundry3
E=tools/claims-v3/e193
rb_local read local "the data directory committed (a commit names it)" git -C "$RB_REPO" log --oneline -1 -- "$DATA"
[ -n "${RB_DRY:-}" ] || [ -s "$RB_CAP" ] || rb_die $RB_E_USAGE "$DATA is not committed: commit it first (the reduction runs after the data commit)"
rb_local read local "the data directory clean" git -C "$RB_REPO" status --short --untracked-files=all -- "$DATA"
[ -z "${RB_DRY:-}" ] && [ -s "$RB_CAP" ] && rb_die $RB_E_GATE "$DATA has uncommitted changes: the reduction reads the committed data only"
RB_CWD="$RB_REPO/$DATA" rb_local read local "the data's SHA256SUMS, every entry" shasum -a 256 -c SHA256SUMS
[ -n "${RB_DRY:-}" ] || { [ "$RB_RC" -eq 0 ] && ! grep -qv ': OK$' "$RB_CAP"; } || rb_die $RB_E_GATE "the data's SHA256SUMS does not read every entry OK"
rb_local read local "the history check" /usr/bin/python3 -I -B $E/rb/check_history_e193.py tree
[ -n "${RB_DRY:-}" ] || rb_has '^HISTORY OK: ' || rb_die $RB_E_GATE "the history check failed"
rb_local read local "the registered reducer at its sha256 (98bbc174...)" shasum -a 256 $E/proposal/src/reduce_x04.py
[ -n "${RB_DRY:-}" ] || rb_has '^98bbc174db714667748c8d27436c7205e7d52be9d83f2614b4346aafc9630511 ' || rb_die $RB_E_GATE "reduce_x04.py is not at its registered sha256"
X=$RB_OUT/e193-reduce-$sit/x04
if [ -n "${RB_DRY:-}" ]; then
  echo "--- desk: copy $DATA/x04/runs.jsonl and unpack $DATA/x04/telemetry.jsonl.gz into <RB_OUT>/e193-reduce-$sit/x04/, each against session/MANIFEST.sha256's x04/ entries"
else
  [ ! -e "$RB_OUT/e193-reduce-$sit" ] || rb_die $RB_E_USAGE "RB_OUT/e193-reduce-$sit exists already: a new RB_OUT, or move it aside"
  mkdir -p "$X" || rb_die $RB_E_USAGE "cannot make $X"
  cp "$RB_REPO/$DATA/x04/runs.jsonl" "$X/runs.jsonl" || rb_die $RB_E_GATE "no x04/runs.jsonl in $DATA (a sitting stopped before its main run has nothing to reduce)"
  gzip -dc "$RB_REPO/$DATA/x04/telemetry.jsonl.gz" > "$X/telemetry.jsonl" || rb_die $RB_E_GATE "x04/telemetry.jsonl.gz does not unpack"
  for p in runs.jsonl telemetry.jsonl; do
    w=$(awk -v p="x04/$p" '$2 == p {print $1}' "$RB_REPO/$DATA/session/MANIFEST.sha256")
    h=$(shasum -a 256 "$X/$p" | cut -d' ' -f1)
    [ -n "$w" ] && [ "$w" = "$h" ] || rb_die $RB_E_GATE "x04/$p as committed is not the box's bytes (its manifest says ${w:-nothing}, the copy reads $h)"
  done
  rb_say "x04/runs.jsonl and the unpacked x04/telemetry.jsonl equal the box's manifest's sha256"
fi
rb_local desk local "THE REGISTERED REDUCER, unchanged, on the committed data (reduce_x04.py OUT --out x04.json)" \
  /usr/bin/python3 -I -B $E/proposal/src/reduce_x04.py "$X" --out "$RB_OUT/x04-e193-$sit.json"
[ -n "${RB_DRY:-}" ] || [ "$RB_RC" -eq 0 ] || rb_die $RB_E_FAIL "the reducer exited $RB_RC (its output above)"
[ -n "${RB_DRY:-}" ] || cp "$RB_CAP" "$RB_OUT/x04-e193-$sit.txt"
rb_local desk local "the kit's checker: E193.md 8's nine checks (check_e193.py checks)" \
  /usr/bin/python3 -I -B $E/check_e193.py checks "$RB_OUT/x04-e193-$sit.json" "$X" --out "$RB_OUT/checks-e193-$sit.json"
[ -n "${RB_DRY:-}" ] && exit 0
rb_has '^CHECKS READ: ' || rb_die $RB_E_FAIL "the checker gave no reading (its output above)"
rb_say "reduced sitting $sit: RB_OUT/x04-e193-$sit.json and checks-e193-$sit.json ($(grep -m1 '^CHECKS READ: ' "$RB_CAP" | cut -c1-160)); the records lane commits them beside the data"
