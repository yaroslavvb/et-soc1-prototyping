#!/usr/bin/env bash
# E215 (Q224, lane kit-e215, Thu 19 Nov 2026, before any E215 datum), the step "the never-run search, repeated" (this file is s06n; STEP 6n, the
# last step before step 7's config read, the day's first card command): E215.md section 4's "The card lanes repeat this scan right before their
# first card command (desk/neverrun_e215.py scan, then report with desk/candidates-e215.json, on the lab at GitHub main then and the folders then,
# E215's own folders subtracted)", with the kit's judgement of the arm's points (desk/neverrun_card_e215.py says how):
#   1. at the desk, one 5,400 s desk call (about one minute, single-threaded, inside the round's slot): the registration's scanner UNCHANGED (its pinned sha256) over the lab clone at HEAD
#      (after step 2's pull: GitHub main) and the round's lane folders (E215_ROUND_OUT: the card lane sets it to the round's OUT), then its report
#      with the registration's candidates, then THE JUDGEMENT for this arm: every scored point whose verdict now reads ran, each hit file dated
#      (a lab file by the commit that added it, a lane file by its modification time) against the arm's freeze line (arm A MM1-v3.1's land 2c971828;
#      arm B the registration commit), 'ran before' (labelled, leaves every rule) or REPORTED (kept), the labels written in the scorer's form and
#      checked against points-e215.json;
#   2. the report: RB_OUT/neverrun-<arm>-<time>/ (scan-e215.json, neverrun-e215.json and .txt, judge-e215-<arm>.json and .txt, labels-e215-<arm>.json),
#      RB_OUT/e215-neverrun-dir-<arm>.txt naming it, and RB_OUT/e215-neverrun-<arm>.txt (its NEVER-RUN-E215 line), whose time step 7 reads: step 7
#      refuses (10) unless this step ended rc 0 within the last 30 minutes. A point that ran before its freeze line is REPORTED, never a gate: a
#      dated note before the data commit, the labels passed to the scorer at step 13, and the orchestrator told.
# NOT SEARCHED, as registered: the boxes' own disks and the model session's uncommitted folders.
# Exits: 0 the search done (its words on the last line); 10 refused (no window, no E215_ROUND_OUT); 14 a scan, the report or the judgement failed
# (run it again).
#   E215_ROUND_OUT=<the round's OUT> bash tools/claims-v3/e215/rb/s06n_neverrun_e215.sh A|B
# SPDX-License-Identifier: Apache-2.0
. "$(dirname "${BASH_SOURCE[0]}")/rb_e215.sh"
rb_init s06n_neverrun
e215_arm "${1:-}"
e215_window
E=tools/claims-v3/e215
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1    # THE CPU RULE (the scan reads MM1-v3.1's data loader)
if [ -z "${RB_DRY:-}" ]; then
  [ -n "${E215_ROUND_OUT:-}" ] && [ -d "${E215_ROUND_OUT:-}" ] || rb_die $RB_E_USAGE "E215_ROUND_OUT does not name the round's lane folders (set it to the round's OUT)"
  case "$(cd "$E215_ROUND_OUT" && pwd -P)/" in "$(cd "$RB_REPO" && pwd -P)/"*) rb_die $RB_E_USAGE "E215_ROUND_OUT is inside the lab repo: refused" ;; esac
fi
N="$RB_OUT/neverrun-$ARM-$(date +%Y%m%dT%H%M%S)-$$"     # a new folder for each call (never a folder an earlier call wrote)
[ -n "${RB_DRY:-}" ] || mkdir "$N" || rb_die $RB_E_USAGE "cannot make a new $N"
rb_local desk local "the never-run search at the desk: the registration's scanner (unchanged) over the lab at HEAD and the round's lane folders, its report, and the judgement of arm $ARM's points against its freeze line" \
  /usr/bin/python3 -I -B $E/desk/neverrun_card_e215.py run "$N" --arm "$ARM" --lab "$RB_REPO" --lanes "${E215_ROUND_OUT:-ROUND_OUT}"
[ -n "${RB_DRY:-}" ] && exit 0
[ "$RB_RC" -eq 0 ] && rb_has "^NEVER-RUN-E215 arm $ARM: " || rb_die $RB_E_FAIL "the never-run search did not end with its NEVER-RUN-E215 line (rc $RB_RC; the lines above): run this step again"
line=$(grep -m1 "^NEVER-RUN-E215 arm $ARM: " "$RB_CAP")
echo "$N" > "$RB_OUT/e215-neverrun-dir-$ARM.txt"
echo "$(date '+%F %T %Z') $line" > "$RB_OUT/e215-neverrun-$ARM.txt"
echo "$(date '+%F %T %Z') step=$RB_STEP arm=$ARM $line" >> "$RB_LOG"
rb_say "the never-run search, repeated: $line (the report in $(basename "$N")/; step 7 follows within 30 minutes, else this step again)"
exit 0
