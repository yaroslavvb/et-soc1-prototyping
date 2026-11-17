#!/usr/bin/env bash
# E211 (Q204, lane kit-e211, Tue 17 Nov 2026, before any E211 datum), the step "the never-run search, repeated" (this file is s06n; STEP 6n, the
# last step before step 7's config read, the day's first card command): E211.md section 4's "The card lane re-checks the never-run list right
# before its first card command (E207's twins will have run by then: E211 books no card before E207's data commit)". E207's kit's step 6n form
# (Q199), with the registration's judgement (desk/neverrun_card_e211.py says how): E206's scanner, unchanged, over the registration's roots and
# aifoundry3's box tree, E211's own folders, its two design lanes and the model session's folders left out by name:
#   1. at the desk: the lab clone at HEAD (but tools/claims-v3/e211 and sealed-e211), the round's lane folders (E211_ROUND_OUT: the card lane sets
#      it to the round's OUT; but every <role>-e211[<suffix>], mm-kernel2 and critic-kernel2) and HOME/claude/work (but ee-*) (one 5,400 s desk
#      call; about two minutes);
#   2. on aifoundry3, one bounded read (the wait class, 600 s; reads only, nice 19 and idle IO, nothing written there): E206's scanner sent on
#      stdin over every folder of HOME/aifoundry/build but e211 and e211rgm (E211's own), every folder of HOME/claude/work but ee-*, and
#      HOME/claude/et-soc1-prototyping/build where it exists; `A --desk-only` leaves this part out and the words say "aifoundry3 NOT SEARCHED"
#      (only after three failed tries of the full form: CARD-LANE-BRIEF.md 2);
#   3. the report: RB_OUT/neverrun-<time>/ (the scans, neverrun-e211-card.json, neverrun-e211-card.txt), and RB_OUT/e211-neverrun.txt (its
#      NEVER-RUN-E211 line), whose time step 7 reads: step 7 refuses (10) unless this step ended rc 0 within the last 30 minutes. rgm211 found
#      on a card before E211 is REPORTED, never a gate (a dated note before the data commit, and the orchestrator told); E207's twins are
#      expected there.
# Exits: 0 the search done (its words on the last line); 10 refused (no window, no E211_ROUND_OUT); 14 a scan or the report failed (run it
# again); the k6 codes for the box call (11, 12, 13).
#   E211_ROUND_OUT=<the round's OUT> bash tools/claims-v3/e211/rb/s06n_neverrun_e211.sh A [--desk-only]
# SPDX-License-Identifier: Apache-2.0
. "$(dirname "${BASH_SOURCE[0]}")/rb_e211.sh"
rb_init s06n_neverrun
e211_arm "${1:-}"
form=${2:-}
case "$form" in ""|--desk-only) ;; *) rb_die $RB_E_USAGE "usage: s06n_neverrun_e211.sh A [--desk-only]" ;; esac
e211_window
E=tools/claims-v3/e211
if [ -z "${RB_DRY:-}" ]; then
  [ -n "${E211_ROUND_OUT:-}" ] && [ -d "${E211_ROUND_OUT:-}" ] || rb_die $RB_E_USAGE "E211_ROUND_OUT does not name the round's lane folders (set it to the round's OUT)"
  case "$(cd "$E211_ROUND_OUT" && pwd -P)/" in "$(cd "$RB_REPO" && pwd -P)/"*) rb_die $RB_E_USAGE "E211_ROUND_OUT is inside the lab repo: refused" ;; esac
fi
N="$RB_OUT/neverrun-$(date +%Y%m%dT%H%M%S)-$$"         # a new folder for each call (never a folder an earlier call wrote: its scans would be read)
[ -n "${RB_DRY:-}" ] || mkdir "$N" || rb_die $RB_E_USAGE "cannot make a new $N"
export E211_ROUND_OUT
rb_local desk local "the never-run search at the desk: E206's scanner (unchanged) over the lab at HEAD, the round's lane folders and HOME/claude/work, E211's own folders and the model session's left out by name" \
  /usr/bin/python3 -I -B $E/desk/neverrun_card_e211.py desk "$N"
[ -n "${RB_DRY:-}" ] || rb_has '^SCANNED-DESK ' || rb_die $RB_E_FAIL "the desk's scans did not end (rc $RB_RC; the lines above): run this step again"
a3args=(--a3-not-searched "the --desk-only form, after three failed tries of the full form (CARD-LANE-BRIEF.md 2)")
if [ "$form" != --desk-only ]; then
  rb_probe "$BOX"
  f=$(rb_file a3scan)
  { rb_prelude "$BOX"
    echo 'tops=""; for d in "$PWD"/build/*/; do d=${d%/}; case "${d##*/}" in e211|e211rgm) ;; *) tops="$tops $d" ;; esac; done'
    echo 'for d in "$HOME"/claude/work/*/; do d=${d%/}; case "${d##*/}" in ee-*) ;; *) tops="$tops $d" ;; esac; done'
    echo '[ -d "$HOME/claude/et-soc1-prototyping/build" ] && tops="$tops $HOME/claude/et-soc1-prototyping/build"'
    echo 'echo "A3SCAN-RAW-BEGIN"'
    echo 'nice -n 19 ionice -c 3 python3 -I -B - scan aifoundry3-box aifoundry3 $tops 2>/dev/null <<'"'"'RB_NR_EOF'"'"''
    cat "$RB_REPO/tools/claims-v3/e206/desk/neverrun_e206.py"
    echo 'RB_NR_EOF'
    echo 'echo "A3SCAN-RAW-END rc $?"'
  } > "$f"
  rb_remote wait "$BOX" "the never-run search on aifoundry3: E206's scanner (unchanged, on stdin) over its run folders but E211's own, reads only" "$f"
  if [ -z "${RB_DRY:-}" ]; then
    [ "$RB_RC" -eq 0 ] && rb_has '^A3SCAN-RAW-END rc 0$' || rb_die $RB_E_FAIL "aifoundry3's scan did not end rc 0 (rc $RB_RC): run this step again (after three failed tries: A --desk-only)"
    sed -n '/^A3SCAN-RAW-BEGIN$/,/^A3SCAN-RAW-END rc /p' "$RB_CAP" | sed '1d;$d' > "$N/found-aifoundry3-box.json"
    "$RB_PY" -I -B -c 'import json, sys; [json.load(open(p)) for p in sys.argv[1:]]' "$N/found-aifoundry3-box.json" 2> /dev/null ||
      rb_die $RB_E_FAIL "aifoundry3's scan output is not whole JSON: run this step again"
  fi
  a3args=()
fi
rb_local desk local "the report: rgm211's arms on a card, and the twins (E211's judgement on the scanner's outputs)" \
  /usr/bin/python3 -I -B $E/desk/neverrun_card_e211.py report "$N" "${a3args[@]}"
[ -n "${RB_DRY:-}" ] && exit 0
rb_has '^NEVER-RUN-E211 ' || rb_die $RB_E_FAIL "the report gave no NEVER-RUN-E211 line (rc $RB_RC; the lines above): run this step again"
line=$(grep -m1 '^NEVER-RUN-E211 ' "$RB_CAP")
echo "$N" > "$RB_OUT/e211-neverrun-dir.txt"
echo "$(date '+%F %T %Z') $line" > "$RB_OUT/e211-neverrun.txt"
echo "$(date '+%F %T %Z') step=$RB_STEP arm=$ARM $line" >> "$RB_LOG"
rb_say "the never-run search, repeated: $line (the report in $(basename "$N")/; step 7 follows within 30 minutes, else this step again)"
exit 0
