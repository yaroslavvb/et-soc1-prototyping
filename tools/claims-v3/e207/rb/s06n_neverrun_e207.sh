#!/usr/bin/env bash
# E207 (Q199, lane kit-e207, Mon 16 Nov 2026, before any E207 datum), the step "the never-run search, repeated" (this file is s06n; STEP 6n, the
# last step before step 7's config read, the day's first card command): E207.md section 4's "The card lane repeats this search right before its
# first card command (... any new E208 session included); a point found run then stays in E207 but is labelled 'ran before' and leaves every
# head-to-head and every rule (a dated note before the data commit)". E206's scanner, unchanged, over the registered roots and more, E207's own
# folders subtracted by the scanner's own counts, then the registration's matching, unchanged (desk/neverrun_card_e207.py says how).
# FIXED by fix-e207 (Tue 17 Nov 2026, before any E207 datum; E207.md amendment A1 items 1-4, verify-e207's findings 1-4 and note 13): every
# folder is scanned on its own and COUNTED only where a record is a card run (the lab's data directories; the card and data lanes' folders in OUT;
# HOME/claude/work but the model session's ee-* folders, which are NOT READ; aifoundry3's run folders); a record in any other folder (another
# experiment's desk test, a kit's log) is DISMISSED and listed with its paths; every counted record of an E207 point is DATED against MM1-v1's
# freeze (21:14:57 PST Mon 16 Nov 2026): RAN BEFORE, TO DATE (the card lane reads its session's start for the dated note) or AFTER THE FREEZE
# (REPORTED, kept in every rule); the dating and the labels it proposes go to <the step's folder>/ranbefore-e207.json:
#   1. at the desk: the lab clone at HEAD, the round's lane folders (E207_ROUND_OUT: the card lane sets it to the round's OUT) and HOME/claude/work,
#      each folder on its own, E207's own folders (every top-level folder named <role>-e207[<suffix>], tools/claims-v3/e207) subtracted (one
#      5,400 s desk call; about a minute or two);
#   2. on aifoundry3, one bounded read (the wait class, 600 s; reads only, nice 19 and idle IO, nothing written there): E206's scanner sent on
#      stdin over HOME/aifoundry/build, HOME/claude/work and HOME/claude/et-soc1-prototyping/build (those that exist), and over build/e207 alone
#      (E207's own: subtracted); `A --desk-only` leaves this part out and the words say "aifoundry3 NOT SEARCHED" (only after three failed tries
#      of the full form: CARD-LANE-BRIEF.md 2);
#   3. the report: the registration's neverrun_e207.py from a copy, on the counted records and E208's planned arms, then the dating:
#      RB_OUT/neverrun-<time>/ (the scans, reg/desk/neverrun-e207.json, neverrun-e207-card.txt, ranbefore-e207.json), and RB_OUT/e207-neverrun.txt
#      (its NEVER-RUN line), whose time step 7 reads: step 7 refuses (10) unless this step ended rc 0 within the last 30 minutes. A point found run
#      is REPORTED, never a gate (its label goes into the card lane's dated note before the data commit; CARD-LANE-BRIEF.md row 12).
# Exits: 0 the search done (its words on the last line); 10 refused (no window today in this RB_OUT: steps 0-2 were not run in it today, start the
# day again from step 0; or no E207_ROUND_OUT: set it to the round's OUT and run this step again); 14 a scan or the matching failed (run it
# again); the k6 codes for the box call (11, 12, 13).
#   E207_ROUND_OUT=<the round's OUT> bash tools/claims-v3/e207/rb/s06n_neverrun_e207.sh A [--desk-only]
# SPDX-License-Identifier: Apache-2.0
. "$(dirname "${BASH_SOURCE[0]}")/rb_e207.sh"
rb_init s06n_neverrun
e207_arm "${1:-}"
form=${2:-}
case "$form" in ""|--desk-only) ;; *) rb_die $RB_E_USAGE "usage: s06n_neverrun_e207.sh A [--desk-only]" ;; esac
e207_window
E=tools/claims-v3/e207
if [ -z "${RB_DRY:-}" ]; then
  [ -n "${E207_ROUND_OUT:-}" ] && [ -d "${E207_ROUND_OUT:-}" ] || rb_die $RB_E_USAGE "E207_ROUND_OUT does not name the round's lane folders (set it to the round's OUT)"
  case "$(cd "$E207_ROUND_OUT" && pwd -P)/" in "$(cd "$RB_REPO" && pwd -P)/"*) rb_die $RB_E_USAGE "E207_ROUND_OUT is inside the lab repo: refused" ;; esac
fi
N="$RB_OUT/neverrun-$(date +%Y%m%dT%H%M%S)"
[ -n "${RB_DRY:-}" ] || mkdir -p "$N" || rb_die $RB_E_USAGE "cannot make $N"
export E207_ROUND_OUT
rb_local desk local "the never-run search at the desk: E206's scanner (unchanged) over the lab at HEAD, the round's lane folders and HOME/claude/work; E207's own lanes scanned apart" \
  /usr/bin/python3 -I -B $E/desk/neverrun_card_e207.py desk "$N"
[ -n "${RB_DRY:-}" ] || rb_has '^SCANNED-DESK ' || rb_die $RB_E_FAIL "the desk's scans did not end (rc $RB_RC; the lines above): run this step again"
a3args=(--a3-not-searched "the --desk-only form, after three failed tries of the full form (CARD-LANE-BRIEF.md 2)")
if [ "$form" != --desk-only ]; then
  rb_probe "$BOX"
  f=$(rb_file a3scan)
  { rb_prelude "$BOX"
    echo 'tops=""; for d in "$PWD/build" "$HOME/claude/work" "$HOME/claude/et-soc1-prototyping/build"; do [ -d "$d" ] && tops="$tops $d"; done'
    echo 'echo "A3SCAN-RAW-BEGIN"'
    echo 'nice -n 19 ionice -c 3 python3 -I -B - scan aifoundry3-ours aifoundry3 $tops 2>/dev/null <<'"'"'RB_NR_EOF'"'"''
    cat "$RB_REPO/tools/claims-v3/e206/desk/neverrun_e206.py"
    echo 'RB_NR_EOF'
    echo 'echo "A3SCAN-RAW-END rc $?"'
    echo 'if [ -d build/e207 ]; then'
    echo '  echo "A3SCAN-EXCL-BEGIN"'
    echo '  nice -n 19 ionice -c 3 python3 -I -B - scan aifoundry3-e207-own aifoundry3 "$PWD/build/e207" 2>/dev/null <<'"'"'RB_NR_EOF'"'"''
    cat "$RB_REPO/tools/claims-v3/e206/desk/neverrun_e206.py"
    echo 'RB_NR_EOF'
    echo '  echo "A3SCAN-EXCL-END rc $?"'
    echo 'else echo "A3SCAN-EXCL-NONE: no build/e207 on the box"; fi'
  } > "$f"
  rb_remote wait "$BOX" "the never-run search on aifoundry3: E206's scanner (unchanged, on stdin) over its run folders, reads only" "$f"
  if [ -z "${RB_DRY:-}" ]; then
    [ "$RB_RC" -eq 0 ] && rb_has '^A3SCAN-RAW-END rc 0$' || rb_die $RB_E_FAIL "aifoundry3's scan did not end rc 0 (rc $RB_RC): run this step again (after three failed tries: A --desk-only)"
    sed -n '/^A3SCAN-RAW-BEGIN$/,/^A3SCAN-RAW-END rc /p' "$RB_CAP" | sed '1d;$d' > "$N/found-a3-raw.json"
    if rb_has '^A3SCAN-EXCL-END rc 0$'; then
      sed -n '/^A3SCAN-EXCL-BEGIN$/,/^A3SCAN-EXCL-END rc /p' "$RB_CAP" | sed '1d;$d' > "$N/found-a3-excluded.json"
    elif rb_has '^A3SCAN-EXCL-NONE'; then
      echo '{}' > "$N/found-a3-excluded.json"
    else
      rb_die $RB_E_FAIL "aifoundry3's scan of build/e207 did not end rc 0: run this step again"
    fi
    "$RB_PY" -I -B -c 'import json, sys; [json.load(open(p)) for p in sys.argv[1:]]' "$N/found-a3-raw.json" "$N/found-a3-excluded.json" 2> /dev/null ||
      rb_die $RB_E_FAIL "aifoundry3's scan output is not whole JSON: run this step again"
  fi
  a3args=(--a3 "$N/found-a3-raw.json" --a3-excluded "$N/found-a3-excluded.json")
fi
rb_local desk local "the report: the net counts and the registration's matching (neverrun_e207.py, from a copy), with E208's planned arms" \
  /usr/bin/python3 -I -B $E/desk/neverrun_card_e207.py report "$N" "${a3args[@]}"
[ -n "${RB_DRY:-}" ] && exit 0
rb_has '^NEVER-RUN ' || rb_die $RB_E_FAIL "the report gave no NEVER-RUN line (rc $RB_RC; the lines above): run this step again"
line=$(grep -m1 '^NEVER-RUN ' "$RB_CAP")
echo "$N" > "$RB_OUT/e207-neverrun-dir.txt"
echo "$(date '+%F %T %Z') $line" > "$RB_OUT/e207-neverrun.txt"
echo "$(date '+%F %T %Z') step=$RB_STEP arm=$ARM $line" >> "$RB_LOG"
rb_say "the never-run search, repeated: $line (the report in $(basename "$N")/; step 7 follows within 30 minutes, else this step again)"
exit 0
