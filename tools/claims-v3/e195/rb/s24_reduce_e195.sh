#!/usr/bin/env bash
# E195 (Q185, lane kit-e195, Sun 15 Nov 2026, before any E195 datum), the box step "the reduction, after the data commit" (this file is
# s24): THE REGISTERED REDUCER (proposal/src/reduce_x09.py, sha256 999232f2..., E195.md section 7), run UNCHANGED at the desk on the
# COMMITTED data only, then the kit's checker for what the reducer leaves (check_e195.py leftover: the floor's and the closure's terms the
# code takes as zero, pass by pass; the rails' measured volts beside its fixed ones; the session's peaks against the stops). It refuses
# (10) unless the data directory is tracked at HEAD and clean, and the reducer is at its registered sha256. THE MAIN PASSES ONLY (E195.md
# 7): the pass directories p910-p917 whose block.json reads "status":"ok", never the smoke p901 and never a moved-aside .attempt-*
# folder; a pass that did not end ok is reported, not reduced. Each main pass's runs.jsonl, marks.jsonl and telemetry.jsonl.gz is copied
# into RB_OUT/reduce-e195/<pass>/ and checked against the session's own MANIFEST.sha256 (the box's bytes) before the reducer reads it, and
# every pass's gen.sha256 must name the kit's gen-e195-noms/ files (the generator output the session ran). The call, as registered:
#   reduce_x09.py <main passes> --gen tools/claims-v3/e195/gen-e195-noms --out x09-e195.json --warmup 910
# (the leakage slope `auto` and the 5-pass minimum its defaults; NEVER --forecast: the forecast is sealed, E195.md section 0). Outputs:
# RB_OUT/x09-e195.json (the reducer's), x09-e195.txt (its printout), leftover-e195.json and .txt (the checker's), with the interpreter
# named; the records lane commits them in a dated note. NO SCORING: the model session scores its sealed forecast privately.
#   bash tools/claims-v3/e195/rb/s24_reduce_e195.sh docs/reports/data/<day>-e195-x09-dramtoggle-aifoundry3
# SPDX-License-Identifier: Apache-2.0
. "$(dirname "${BASH_SOURCE[0]}")/rb_e195.sh"
rb_init s24_reduce
D=${1:-}
case "$D" in docs/reports/data/*-e195-x09-dramtoggle-aifoundry3) ;; *) rb_die $RB_E_USAGE "usage: s24_reduce_e195.sh docs/reports/data/<day>-e195-x09-dramtoggle-aifoundry3" ;; esac
RED=tools/claims-v3/e195/proposal/src/reduce_x09.py
GEN=tools/claims-v3/e195/gen-e195-noms
rb_local read local "the data directory tracked at HEAD" git -C "$RB_REPO" ls-files -- "$D/session/MANIFEST.sha256" "$D/facts-e195.json" "$D/SHA256SUMS"
[ -n "${RB_DRY:-}" ] || [ "$(grep -c . "$RB_CAP")" = 3 ] || rb_die $RB_E_USAGE "$D is not committed (the reducer runs after the data commit only)"
rb_local read local "the data directory clean" git -C "$RB_REPO" status --porcelain --untracked-files=all -- "$D"
[ -z "${RB_DRY:-}" ] && [ -s "$RB_CAP" ] && rb_die $RB_E_USAGE "$D has uncommitted changes: reduce only the committed data"
RB_CWD="$RB_REPO/$D" rb_local read local "the data directory's own SHA256SUMS holds" sha256sum -c --quiet SHA256SUMS
[ -z "${RB_DRY:-}" ] && [ "$RB_RC" -ne 0 ] && rb_die $RB_E_USAGE "$D's SHA256SUMS does not hold"
rb_local read local "the reducer at its registered sha256" sha256sum "$RED"
[ -n "${RB_DRY:-}" ] || rb_has '^999232f2c1c95439b3ba4dc8135aba8d31eec32fec7df8bbbec3b8cdffbb3b64 ' || rb_die $RB_E_USAGE "the reducer is not at its registered sha256 (999232f2...)"
IN=$RB_OUT/reduce-e195
MAIN=()
if [ -z "${RB_DRY:-}" ]; then
  [ -e "$IN" ] && rb_die $RB_E_USAGE "$IN exists: move it aside first"
  mkdir -p "$IN"
  T0=$("$RB_PY" -I -c 'import json,sys; print(json.load(open(sys.argv[1]))["T0"])' "$D/facts-e195.json") || rb_die $RB_E_FAIL "facts-e195.json unreadable"
  MF=$D/session/MANIFEST.sha256
  gh=$( (cd "$GEN" && sha256sum manifest.json counts.json) )
  for pd in "$D"/passes/p91[0-7]; do
    [ -d "$pd" ] || continue
    p=$(basename "$pd")
    grep -q '"status":"ok"' "$pd/block.json" 2>/dev/null || { echo "$p: block.json is not ok: reported, not reduced (E195.md 7)" | tee -a "$RB_OUT/reduce-e195.notes"; continue; }
    [ "$(cat "$pd/gen.sha256")" = "$gh" ] || rb_die $RB_E_GATE "$p ran a generator output other than gen-e195-noms/ (its gen.sha256): reduce nothing; read why"
    mkdir -p "$IN/$p"
    for f in runs.jsonl marks.jsonl telemetry.jsonl.gz; do
      cp "$pd/$f" "$IN/$p/$f" || rb_die $RB_E_FAIL "$p/$f is missing"
      want=$(grep -E "  build/claims-v3/aifoundry3/e195/build/claims-v3/aifoundry3/x09-T$T0/$p/$f\$" "$MF" | cut -d' ' -f1)
      [ -n "$want" ] && [ "$(sha256sum "$IN/$p/$f" | cut -d' ' -f1)" = "$want" ] || rb_die $RB_E_GATE "$p/$f is not the box's bytes (the session's MANIFEST.sha256): reduce nothing; read why"
    done
    MAIN+=("$IN/$p")
  done
  [ "${#MAIN[@]}" -ge 1 ] || rb_die $RB_E_GATE "no main pass ended ok: nothing to reduce (every scored verdict reads UNRESOLVED: report it)"
else
  MAIN=("<RB_OUT>/reduce-e195/p910" "..." "<RB_OUT>/reduce-e195/p917 (each whose block.json reads ok)")
fi
RB_STDOUT="$RB_OUT/x09-e195.txt" rb_local desk local "the registered reducer, unchanged, on the main passes (/usr/bin/python3 -I -B; never --forecast)" \
  /usr/bin/python3 -I -B "$RED" "${MAIN[@]}" --gen "$GEN" --out "$RB_OUT/x09-e195.json" --warmup 910
[ "$RB_RC" -eq 0 ] || rb_die $RB_E_FAIL "the reducer exited $RB_RC: read its output above"
RB_STDOUT="$RB_OUT/leftover-e195.txt" rb_local desk local "what the reducer leaves (check_e195.py leftover)" /usr/bin/python3 -I -B tools/claims-v3/e195/check_e195.py leftover \
  "$RED" "$GEN" "${MAIN[@]}" --warmup 910 --json "$RB_OUT/leftover-e195.json"
rb_has '^LEFTOVER-E195: ' || [ -n "${RB_DRY:-}" ] || rb_die $RB_E_FAIL "the checker did not run (the lines above)"
rb_say "reduced (the registered reducer, Python $(/usr/bin/python3 -V 2>&1 | cut -d' ' -f2), on ${#MAIN[@]} main passes, --warmup 910): RB_OUT/x09-e195.json and .txt; what it leaves: RB_OUT/leftover-e195.json and .txt; commit them in a dated note with the records, no score"
exit 0
