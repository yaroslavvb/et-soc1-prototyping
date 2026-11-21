#!/usr/bin/env bash
# E222 (Q236, lane kit-e222, Fri 20 Nov 2026, before any E222 datum; E218's landed kit 5582edfc ported, the kit that ran E218 FULL on aifoundry3 card 0 at 03:11-03:56 PST that day), the step "the never-run search, repeated" (this file is s06n; STEP 6n, the
# last step before step 7's config read, the day's first card command): E222.md section 4's "The card lane repeats the scan right before its
# first card command (step 6n, the same reading): a point found run then is labelled 'ran before' and leaves every rule, said", with the kit's
# judgement (desk/neverrun_card_e222.py says how). E218's step 6n (tools/claims-v3/e218/rb/s06n_neverrun_e218.sh, kit 5582edfc) with E220's
# judgement form (dated note 1: tools/claims-v3/e220/desk/neverrun_card_e220.py, kit 2f0ab9cd) for E222's scanner and readings:
#   1. at the desk, one 5,400 s desk call (about twenty seconds, single-threaded, inside the round's slot): the registration's scanner UNCHANGED
#      (desk/neverrun_e222.py at its pinned sha256, its scan then its report) over the lab clone at HEAD (after step 2's pull: GitHub main) and
#      the round's lane folders (E222_ROUND_OUT: the card lane sets it to the round's OUT; every lane or data folder whose name holds 'e222' is
#      never opened - W/out/card-e222 among them, so the card lane must be named exactly card-e222 - nor any holding 'e220', as registered),
#      then THE JUDGEMENT of the 70 registered points by session records on aifoundry3 card 0 (dated note 1's reading, the registration's): every
#      non-R point the report reads not never run labelled 'ran before' (leaves every rule); FAMILY R (ry01a, ry01b, rg01, rg01t) exempt by its
#      family name only and printed "RAN (exempt by family name: same-card repeats, REPORTED only)"; THE POSITIVE CONTROL (the orchestrator's
#      answer 1 of 14:21 PST Fri 20 Nov 2026): R's exemption lifted, all four must read RAN from E218's committed session on this card, else the
#      scan cannot see this card's sessions: 16, the day stops before step 7 (no card command) and the orchestrator is told; the literal reading
#      REPORTED beside; the labels written in the frozen scorer's form ({"ran_before_points": {"A": [...]}}) and checked against points-e222.json;
#   2. the report: RB_OUT/neverrun-A-<time>/ (scan-e222-reg.json, neverrun-e222.json and .txt, judge-e222-A.json and .txt, labels-e222-A.json),
#      RB_OUT/e222-neverrun-dir-A.txt naming it, and RB_OUT/e222-neverrun-A.txt (its NEVER-RUN-E222 line), whose time step 7 reads: step 7
#      refuses (10) unless this step ended rc 0 within the last 30 minutes. A labelled point is REPORTED, never a gate: a dated note before the
#      data commit, the labels passed to the scorer at step 13, and the orchestrator told.
# NOT SEARCHED, as registered: the box's own disk and the model session's uncommitted folders.
# Exits: 0 the search done (its words on the last line); 10 refused (no window, no E222_ROUND_OUT); 14 a scan, the report or the judgement failed
# (run it again); 16 the positive control failed (no card command today without the orchestrator's word): read by the tool's own line
# "POSITIVE CONTROL FAILED: ...", since k6's runner reports the tool's exit 15, as every non-zero exit of a desk call, as 14.
#   E222_ROUND_OUT=<the round's OUT> bash tools/claims-v3/e222/rb/s06n_neverrun_e222.sh A
# SPDX-License-Identifier: Apache-2.0
. "$(dirname "${BASH_SOURCE[0]}")/rb_e222.sh"
rb_init s06n_neverrun
e222_arm "${1:-}"
e222_window
E=tools/claims-v3/e222
export OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 MKL_NUM_THREADS=1 NUMEXPR_NUM_THREADS=1    # THE CPU RULE (the scan reads MM1-v3.2's data loader)
if [ -z "${RB_DRY:-}" ]; then
  [ -n "${E222_ROUND_OUT:-}" ] && [ -d "${E222_ROUND_OUT:-}" ] || rb_die $RB_E_USAGE "E222_ROUND_OUT does not name the round's lane folders (set it to the round's OUT)"
  case "$(cd "$E222_ROUND_OUT" && pwd -P)/" in "$(cd "$RB_REPO" && pwd -P)/"*) rb_die $RB_E_USAGE "E222_ROUND_OUT is inside the lab repo: refused" ;; esac
fi
N="$RB_OUT/neverrun-$ARM-$(date +%Y%m%dT%H%M%S)-$$"     # a new folder for each call (never a folder an earlier call wrote)
[ -n "${RB_DRY:-}" ] || mkdir "$N" || rb_die $RB_E_USAGE "cannot make a new $N"
rb_local desk local "the never-run search at the desk: the registration's scanner (unchanged) over the lab at HEAD and the round's lane folders, its report, and the judgement of E222's 70 registered points (family R exempt by name, the positive control)" \
  /usr/bin/python3 -I -B $E/desk/neverrun_card_e222.py run "$N" --arm "$ARM" --lab "$RB_REPO" --lanes "${E222_ROUND_OUT:-ROUND_OUT}"
[ -n "${RB_DRY:-}" ] && exit 0
# k6's runner reports every non-zero exit of a desk call as 14 (the tool's own 15 is in its log line), so the tool's printed line decides
if [ "$RB_RC" -ne 0 ] && rb_has '^POSITIVE CONTROL FAILED: '; then
  echo "$(date '+%F %T %Z') step=$RB_STEP arm=$ARM POSITIVE CONTROL FAILED ($N)" >> "$RB_LOG"
  rb_die $RB_E_GATE "the never-run search's POSITIVE CONTROL FAILED: the scan does not read family R's four as run on aifoundry3 card 0 (E218 ran them there), so it cannot see this card's sessions: no card command today; tell the orchestrator (its answer 1: a re-scan with a reader that does)"
fi
[ "$RB_RC" -eq 0 ] && rb_has "^NEVER-RUN-E222 arm $ARM: " || rb_die $RB_E_FAIL "the never-run search did not end with its NEVER-RUN-E222 line (rc $RB_RC; the lines above): run this step again"
line=$(grep -m1 "^NEVER-RUN-E222 arm $ARM: " "$RB_CAP")
echo "$N" > "$RB_OUT/e222-neverrun-dir-$ARM.txt"
echo "$(date '+%F %T %Z') $line" > "$RB_OUT/e222-neverrun-$ARM.txt"
echo "$(date '+%F %T %Z') step=$RB_STEP arm=$ARM $line" >> "$RB_LOG"
rb_say "the never-run search, repeated: $line (the report in $(basename "$N")/; step 7 follows within 30 minutes, else this step again)"
exit 0
