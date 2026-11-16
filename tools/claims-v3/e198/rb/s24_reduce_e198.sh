#!/usr/bin/env bash
# E198 (Q191, lane kit-e198, Sun 15 Nov 2026, before any E198 datum; ported from E193's file of the same step, unchanged in logic but the names below), the box step "the reduction, after the data commit" (this file is s24), one sitting a call, on the desk only:
# THE REGISTERED REDUCER, proposal/src/reduce_x04.py at its sha256 (98bbc174..., E198.md 7), UNCHANGED, in its registered form
# (`python3 reduce_x04.py OUT --out x04.json`: no --pvt, no --keep-warmup), on the COMMITTED data directory, never before: the directory
# is in HEAD, clean, its SHA256SUMS reads every entry OK, and the history check holds. Its x04/ (runs.jsonl and the unpacked
# telemetry.jsonl) is copied into RB_OUT/e198-reduce-<sitting>/x04/, each checked first against the box's own manifest
# (session/MANIFEST.sha256: the bytes the box wrote), then reduced; then the kit's checker reads E193.md 8's nine checks (E198.md 7: REPORTED) (check_e193.py
# checks: 1-7 from x04.json, 8's dip count by the reducer's own windows, 9 by section 8's reading). Its outputs go to RB_OUT
# (x04-e198-<sitting>.json, checks-e198-<sitting>.json, the reducer's printed table); the records lane commits them beside the data in a
# later commit. Nothing here scores anything against the sealed forecasts (E198.md 0): the model session does that, privately.
#   bash tools/claims-v3/e198/rb/s24_reduce_e198.sh A|B           (one sitting: the reducer, then E193's checker)
#   bash tools/claims-v3/e198/rb/s24_reduce_e198.sh score <x04-e198-A.json> [<x04-e198-B.json>]   (THE TRANSPORT SCORER, after both, or A alone)
# SPDX-License-Identifier: Apache-2.0
. "$(dirname "${BASH_SOURCE[0]}")/rb_e198.sh"
rb_init s24_reduce
if [ "${1:-}" = score ]; then   # THE TRANSPORT SCORER (E198.md 5), after the data commits: the reducer's outputs of A (and B), unchanged
  A=${2:-}; B=${3:-}
  [ -n "${RB_DRY:-}" ] || [ -f "$A" ] || [ -f "$B" ] || rb_die $RB_E_USAGE "usage: s24_reduce_e198.sh score <x04-e198-A.json> [<x04-e198-B.json>] (either may be '-')"
  args=(); [ -n "$A" ] && [ "$A" != - ] && args+=(--a "$A"); [ -n "$B" ] && [ "$B" != - ] && args+=(--b "$B")
  rb_local read local "the scorer at its sha256 (1d2b211e...)" sha256sum tools/claims-v3/e198/score_e198.py
  [ -n "${RB_DRY:-}" ] || rb_has '^1d2b211ea95ca1a7566daf612ab5133d5713ff1e647632adfc4128c7acb56e8b ' || rb_die $RB_E_GATE "score_e198.py is not at its registered sha256"
  rb_local desk local "THE TRANSPORT RULES' scorer, unchanged (score_e198.py score)" \
    /usr/bin/python3 -I -B tools/claims-v3/e198/score_e198.py score "${args[@]}" --out "$RB_OUT/scores-e198.json"
  [ -n "${RB_DRY:-}" ] && exit 0
  [ "$RB_RC" -eq 0 ] || rb_die $RB_E_FAIL "the scorer exited $RB_RC (its output above)"
  cp "$RB_CAP" "$RB_OUT/scores-e198.txt"
  rb_say "scored: RB_OUT/scores-e198.json and scores-e198.txt (the records lane commits them beside the data)"
  exit 0
fi
sit=${1:-}
e198_cap_s "$sit" > /dev/null || rb_die $RB_E_USAGE "usage: s24_reduce_e198.sh A|B"
rb_window
low=$(echo "$sit" | tr 'AB' 'ab')
DATA=docs/reports/data/${RB_DAY:-DAY}-e198-x04-clock-sitting-$low-aifoundry1-c1
E=tools/claims-v3/e198
rb_local read local "the data directory committed (a commit names it)" git -C "$RB_REPO" log --oneline -1 -- "$DATA"
[ -n "${RB_DRY:-}" ] || [ -s "$RB_CAP" ] || rb_die $RB_E_USAGE "$DATA is not committed: commit it first (the reduction runs after the data commit)"
rb_local read local "the data directory clean" git -C "$RB_REPO" status --short --untracked-files=all -- "$DATA"
[ -z "${RB_DRY:-}" ] && [ -s "$RB_CAP" ] && rb_die $RB_E_GATE "$DATA has uncommitted changes: the reduction reads the committed data only"
RB_CWD="$RB_REPO/$DATA" rb_local read local "the data's SHA256SUMS, every entry" shasum -a 256 -c SHA256SUMS
[ -n "${RB_DRY:-}" ] || { [ "$RB_RC" -eq 0 ] && ! grep -qv ': OK$' "$RB_CAP"; } || rb_die $RB_E_GATE "the data's SHA256SUMS does not read every entry OK"
rb_local read local "the history check" /usr/bin/python3 -I -B $E/rb/check_history_e198.py tree
[ -n "${RB_DRY:-}" ] || rb_has '^HISTORY OK: ' || rb_die $RB_E_GATE "the history check failed"
rb_local read local "the registered reducer at its sha256 (98bbc174...)" sha256sum tools/claims-v3/e193/proposal/src/reduce_x04.py
[ -n "${RB_DRY:-}" ] || rb_has '^98bbc174db714667748c8d27436c7205e7d52be9d83f2614b4346aafc9630511 ' || rb_die $RB_E_GATE "reduce_x04.py is not at its registered sha256"
X=$RB_OUT/e198-reduce-$sit/x04
if [ -n "${RB_DRY:-}" ]; then
  echo "--- desk: copy $DATA/x04/runs.jsonl and unpack $DATA/x04/telemetry.jsonl.gz into <RB_OUT>/e198-reduce-$sit/x04/, each against session/MANIFEST.sha256's x04/ entries"
else
  [ ! -e "$RB_OUT/e198-reduce-$sit" ] || rb_die $RB_E_USAGE "RB_OUT/e198-reduce-$sit exists already: a new RB_OUT, or move it aside"
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
  /usr/bin/python3 -I -B tools/claims-v3/e193/proposal/src/reduce_x04.py "$X" --out "$RB_OUT/x04-e198-$sit.json"
[ -n "${RB_DRY:-}" ] || [ "$RB_RC" -eq 0 ] || rb_die $RB_E_FAIL "the reducer exited $RB_RC (its output above)"
[ -n "${RB_DRY:-}" ] || cp "$RB_CAP" "$RB_OUT/x04-e198-$sit.txt"
rb_local desk local "the kit's checker: E193.md 8's nine checks (E198.md 7: REPORTED) (check_e193.py checks)" \
  /usr/bin/python3 -I -B tools/claims-v3/e193/check_e193.py checks "$RB_OUT/x04-e198-$sit.json" "$X" --out "$RB_OUT/checks-e198-$sit.json"
[ -n "${RB_DRY:-}" ] && exit 0
rb_has '^CHECKS READ: ' || rb_die $RB_E_FAIL "the checker gave no reading (its output above)"
rb_say "reduced sitting $sit: RB_OUT/x04-e198-$sit.json and checks-e198-$sit.json ($(grep -m1 '^CHECKS READ: ' "$RB_CAP" | cut -c1-160)); the records lane commits them beside the data"
