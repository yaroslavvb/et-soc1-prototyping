#!/usr/bin/env bash
# E218 (Q230, lane kit-e218, Thu 19 Nov 2026, before any E218 datum), the step "the never-run search, repeated" (this file is s06n; STEP 6n, the
# last step before step 7's config read, the day's first card command): E218.md section 4's "The card lane repeats this scan right before its
# first card command (E215's step 6n form; a point it finds run then is labelled 'ran before' and leaves every rule, said)", with the kit's
# judgement (desk/neverrun_card_e218.py says how). E215 arm A's step 6n (tools/claims-v3/e215/rb/s06n_neverrun_e215.sh, landed in 8bde0182)
# for E218's scanner and readings:
#   1. at the desk, one 5,400 s desk call (about fifteen seconds, single-threaded, inside the round's slot): the registration's scanner UNCHANGED
#      (desk/neverrun_e218.py at its pinned sha256) over the lab clone at HEAD (after step 2's pull: GitHub main) and the round's lane folders
#      (E218_ROUND_OUT: the card lane sets it to the round's OUT; E218's own folders - W/out/card-e218* and data folders holding '-e218-' - are
#      subtracted, so the card lane must be named exactly card-e218), then its report on MM1-v3.2's 54 landed points (as the registration ran it),
#      then THE JUDGEMENT of the 52 registered points: every one the report now reads not never run, under its family's reading (F the token on any
#      card; G and Gt the token on aifoundry3 card 0; Y the configuration on aifoundry3 card 0), labelled 'ran before' (leaves every rule), each
#      hit's files dated against MM1-v3.2's land 4e386f75 (REPORTED), the labels written in the scorer's form and checked against points-e218.json;
#   2. the report: RB_OUT/neverrun-A-<time>/ (scan-e218-reg.json, neverrun-e218.json and .txt, judge-e218-A.json and .txt, labels-e218-A.json),
#      RB_OUT/e218-neverrun-dir-A.txt naming it, and RB_OUT/e218-neverrun-A.txt (its NEVER-RUN-E218 line), whose time step 7 reads: step 7
#      refuses (10) unless this step ended rc 0 within the last 30 minutes. A labelled point is REPORTED, never a gate: a dated note before the
#      data commit, the labels passed to the scorer at step 13, and the orchestrator told.
# NOT SEARCHED, as registered: the box's own disk and the model session's uncommitted folders.
# Exits: 0 the search done (its words on the last line); 10 refused (no window, no E218_ROUND_OUT); 14 a scan, the report or the judgement failed
# (run it again).
#   E218_ROUND_OUT=<the round's OUT> bash tools/claims-v3/e218/rb/s06n_neverrun_e218.sh A
# SPDX-License-Identifier: Apache-2.0
. "$(dirname "${BASH_SOURCE[0]}")/rb_e218.sh"
rb_init s06n_neverrun
e218_arm "${1:-}"
e218_window
E=tools/claims-v3/e218
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1    # THE CPU RULE (the scan reads MM1-v3.2's data loader)
if [ -z "${RB_DRY:-}" ]; then
  [ -n "${E218_ROUND_OUT:-}" ] && [ -d "${E218_ROUND_OUT:-}" ] || rb_die $RB_E_USAGE "E218_ROUND_OUT does not name the round's lane folders (set it to the round's OUT)"
  case "$(cd "$E218_ROUND_OUT" && pwd -P)/" in "$(cd "$RB_REPO" && pwd -P)/"*) rb_die $RB_E_USAGE "E218_ROUND_OUT is inside the lab repo: refused" ;; esac
fi
N="$RB_OUT/neverrun-$ARM-$(date +%Y%m%dT%H%M%S)-$$"     # a new folder for each call (never a folder an earlier call wrote)
[ -n "${RB_DRY:-}" ] || mkdir "$N" || rb_die $RB_E_USAGE "cannot make a new $N"
rb_local desk local "the never-run search at the desk: the registration's scanner (unchanged) over the lab at HEAD and the round's lane folders, its report, and the judgement of E218's 52 registered points" \
  /usr/bin/python3 -I -B $E/desk/neverrun_card_e218.py run "$N" --arm "$ARM" --lab "$RB_REPO" --lanes "${E218_ROUND_OUT:-ROUND_OUT}"
[ -n "${RB_DRY:-}" ] && exit 0
[ "$RB_RC" -eq 0 ] && rb_has "^NEVER-RUN-E218 arm $ARM: " || rb_die $RB_E_FAIL "the never-run search did not end with its NEVER-RUN-E218 line (rc $RB_RC; the lines above): run this step again"
line=$(grep -m1 "^NEVER-RUN-E218 arm $ARM: " "$RB_CAP")
echo "$N" > "$RB_OUT/e218-neverrun-dir-$ARM.txt"
echo "$(date '+%F %T %Z') $line" > "$RB_OUT/e218-neverrun-$ARM.txt"
echo "$(date '+%F %T %Z') step=$RB_STEP arm=$ARM $line" >> "$RB_LOG"
rb_say "the never-run search, repeated: $line (the report in $(basename "$N")/; step 7 follows within 30 minutes, else this step again)"
exit 0
