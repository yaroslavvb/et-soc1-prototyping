# E190 (Q169, the kit's dated note 1, lane fix-e190, Fri 13 Nov 2026, before any E190 datum): the part every v2 runbook step sources.
# It sources rb_e190.sh (the kit, unchanged: k6's library, E190's ours_live by each process's own script, the arms, the window rule, the
# lab-git lock, the kit commit by content) and adds only:
#   - THE NOTE COMMIT, found by its content: the commit that added tools/claims-v3/e190/KIT.md.dated-note-1.md (it lands after this file
#     is written); a box tree must hold it (step 5 v2), and step 2 v2 reads it an ancestor of HEAD;
#   - the v2 job names: a2-build-e190v2 / a1-build-e190v2 (the build v2), a2-dry-e190v2 / a1-dry-e190v2 (the dry pass v2); the day's build
#     count (NO-THIRD-BUILD) counts the v1 and the v2 build jobs' starts together;
#   - e190_built_v2 <arm>: "rgm-v2" when step 6 v2's wait recorded today's build v2 for that arm (RB_OUT/e190-built-v2-<arm>.txt).
# The v2 steps: s03_desk_e190_v2.sh (step 2), s07_sync_e190_v2.sh (5), s08_build_e190_v2.sh (6), s10_dry_e190_v2.sh (8),
# s11_session_e190_v2.sh (9), s20_wait_e190_v2.sh (10), s22_collect_e190_v2.sh (11); steps 1, 12 and 13 are the kit's unchanged
# (s02_window_e190.sh, s23_data_e190.sh, s24_score_e190.sh), step 4 is k6's look, and s25_report_e190_n1.sh follows step 13.
# SPDX-License-Identifier: Apache-2.0
. "$(dirname "${BASH_SOURCE[0]}")/rb_e190.sh"
RB_E190_V2_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)

e190_note1_commit() {  # the note commit, by its content (the commit that added tools/claims-v3/e190/KIT.md.dated-note-1.md); empty if none
  git -C "$RB_REPO" log --diff-filter=A --format=%H -- tools/claims-v3/e190/KIT.md.dated-note-1.md 2>/dev/null | tail -n 1
}

e190_jobs_v2() {  # e190_jobs_v2 <arm>: sets J (a2 or a1), JOB_BUILD and JOB_DRY (the v2 job names)
  J=$([ "$1" = A ] && echo a2 || echo a1)
  JOB_BUILD=$J-build-e190v2
  JOB_DRY=$J-dry-e190v2
}

e190_built_v2() {  # e190_built_v2 <arm>: "rgm-v2" if step 6 v2's wait recorded today's build v2 for that arm, else nothing
  local f="$RB_OUT/e190-built-v2-$1.txt"
  if [ -f "$f" ] && [ "$(TZ=America/Los_Angeles date -r "$f" +%F)" = "$(TZ=America/Los_Angeles date +%F)" ]; then cat "$f"; fi
}
