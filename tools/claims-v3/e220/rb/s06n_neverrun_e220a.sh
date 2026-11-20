#!/usr/bin/env bash
# E220 ARM A (Q233, lane kit-e220, Fri 20 Nov 2026, before any E220 datum), the step "the never-run search, repeated" (this file is s06n; STEP
# 6n, the last step before step 7's config read, the day's first card command): E220.md section 4's "The card lanes repeat the scan right before
# their first card command (step 6n): a point found run then is labelled 'ran before' and leaves every rule, said", with the kit's judgement
# (desk/neverrun_card_e220.py says how). E218's step 6n (tools/claims-v3/e218/rb/s06n_neverrun_e218.sh, landed in 5582edfc) for E220's scanner:
#   1. at the desk, one 5,400 s desk call (about a minute, single-threaded, inside the round's slot): the registration's scanner and report
#      UNCHANGED (desk/neverrun_e220.py and desk/neverrun_report_e220.py at their registered sha256) over the lab clone at HEAD (after step 2's
#      pull: GitHub main) and the round's lane folders (E220A_ROUND_OUT: the card lane sets it to the round's OUT; E220's own folders - W/out/
#      card-e220* and any path holding '-e220-' - are subtracted, so the card lanes must be named exactly card-e220a and card-e220b), then THE
#      JUDGEMENT of arm A's 84 registered points: every one the report now reads not never run on aifoundry1 card 1, under its family's reading
#      (the token for XG, XGt, XF, L3, Y2, G2, G2t; the configuration for XY), labelled 'ran before' (leaves every rule), the labels written in the
#      scorer's form and checked against points-e220.json;
#   2. the report: RB_OUT/neverrun-A-<time>/ (scan-e220-reg.json, neverrun-e220.json and .txt, judge-e220-A.json and .txt, labels-e220-A.json),
#      RB_OUT/e220a-neverrun-dir-A.txt naming it, and RB_OUT/e220a-neverrun-A.txt (its NEVER-RUN-E220 line), whose time step 7 reads: step 7
#      refuses (10) unless this step ended rc 0 within the last 30 minutes. A labelled point is REPORTED, never a gate: a dated note before the
#      data commit, the labels passed to the scorer at step 13, and the orchestrator told.
# NOT SEARCHED, as registered: the box's own disk and the model session's uncommitted folders.
# Exits: 0 the search done (its words on the last line); 10 refused (no window, no E220A_ROUND_OUT); 14 a scan, the report or the judgement failed
# (run it again).
#   E220A_ROUND_OUT=<the round's OUT> bash tools/claims-v3/e220/rb/s06n_neverrun_e220a.sh A
# SPDX-License-Identifier: Apache-2.0
. "$(dirname "${BASH_SOURCE[0]}")/rb_e220a.sh"
rb_init s06n_neverrun
e220a_arm "${1:-}"
e220a_window
E=tools/claims-v3/e220
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1    # THE CPU RULE (the scan reads MM1-v3.2's data loader)
if [ -z "${RB_DRY:-}" ]; then
  [ -n "${E220A_ROUND_OUT:-}" ] && [ -d "${E220A_ROUND_OUT:-}" ] || rb_die $RB_E_USAGE "E220A_ROUND_OUT does not name the round's lane folders (set it to the round's OUT)"
  case "$(cd "$E220A_ROUND_OUT" && pwd -P)/" in "$(cd "$RB_REPO" && pwd -P)/"*) rb_die $RB_E_USAGE "E220A_ROUND_OUT is inside the lab repo: refused" ;; esac
fi
N="$RB_OUT/neverrun-$ARM-$(date +%Y%m%dT%H%M%S)-$$"     # a new folder for each call (never a folder an earlier call wrote)
[ -n "${RB_DRY:-}" ] || mkdir "$N" || rb_die $RB_E_USAGE "cannot make a new $N"
rb_local desk local "the never-run search at the desk: the registration's scanner and report (unchanged) over the lab at HEAD and the round's lane folders, and the judgement of arm A's 84 registered points" \
  /usr/bin/python3 -I -B $E/desk/neverrun_card_e220.py run "$N" --arm "$ARM" --lab "$RB_REPO" --lanes "${E220A_ROUND_OUT:-ROUND_OUT}"
[ -n "${RB_DRY:-}" ] && exit 0
[ "$RB_RC" -eq 0 ] && rb_has "^NEVER-RUN-E220 arm $ARM: " || rb_die $RB_E_FAIL "the never-run search did not end with its NEVER-RUN-E220 line (rc $RB_RC; the lines above): run this step again"
line=$(grep -m1 "^NEVER-RUN-E220 arm $ARM: " "$RB_CAP")
echo "$N" > "$RB_OUT/e220a-neverrun-dir-$ARM.txt"
echo "$(date '+%F %T %Z') $line" > "$RB_OUT/e220a-neverrun-$ARM.txt"
echo "$(date '+%F %T %Z') step=$RB_STEP arm=$ARM $line" >> "$RB_LOG"
rb_say "the never-run search, repeated: $line (the report in $(basename "$N")/; step 7 follows within 30 minutes, else this step again)"
exit 0
