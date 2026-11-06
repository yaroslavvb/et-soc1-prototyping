#!/usr/bin/env bash
# E180 (Q146(g); the kit's dated note 2, ../KIT.md.dated-note-2.md sections 1-3 and 6), step 22, v3: collect and score at the desk, on the
# Intel (it needs this Mac's tree and its ssh to the box), at nice 10, every copy bounded, after the run has ended (s20_wait_e180_v2.sh read
# the session end). It replaces s22_collect_e180_v2.sh (v2, which stays as committed) in the runbook. No box file changes. Two changes:
#   1. after v2's two copies, a third: the build record, build/enercat-e180/BUILD-E180.json (the kernel's and the host's sha256, which no
#      collected file held), and the box's kernel listing, build/e180-kernel-dis.txt (step 6 v2's objdump, A1-7's evidence), into
#      build/e180-raw/build-record/ (the kit verifier's fault 3). The listing is not asked for when the box's own walk line, copied back
#      with the logs, says step 6 found no objdump or no kernel (then it was never written), or when that line is not there at all (step
#      6 v2 never ran its walk). A copy that exits non-zero stops the step (14): call it again;
#   2. the collector is ../collect_e180_v3.sh: the build record into logs/, A1-7 read at the desk by check_elf_e180_v2.py on that listing
#      (faults 1 and 2), reduce_e180_v3.py (fault 4) and score_e180_v3.py (faults 5 and 6).
# Everything else is v2's, line for line: the passes' and the logs' copies, the stop-path test check, the desk-path gate, and the login
# check over every directory of the output with ../../e178/scrub_tree_e178.py --check, run LAST. The desk test's stand-in for the
# collector (K6E180_COLLECT) is read only with RB_DESKTEST=1; set without it, the step refuses (10). This step commits nothing.
#
#   bash tools/claims-v3/e180/rb/s22_collect_e180_v3.sh
# SPDX-License-Identifier: Apache-2.0
. "$(dirname "${BASH_SOURCE[0]}")/rb_e180.sh"
rb_init s22_collect_v3
rb_window
DAY=$RB_DAY
OUT=build/e180-out/$DAY-e180-vector-add-aifoundry3
if [ "${RB_DESKTEST:-}" != 1 ] && [ -n "${K6E180_COLLECT:-}" ]; then
  rb_die $RB_E_USAGE "K6E180_COLLECT is a desk-test stand-in and is read only with RB_DESKTEST=1: unset it (the card day never sets it)"
fi
COL=${K6E180_COLLECT:-tools/claims-v3/e180/collect_e180_v3.sh}
scrub_tree() {  # v2's: scrub_tree <output dir> <box>: every directory of the output, --check only (it rewrites nothing)
  local d=$1 box=$2 own
  own=$(cat "$RB_OUT/box-login-$box.txt" 2>/dev/null)
  [ -n "${RB_DRY:-}" ] && own=${own:-LOGIN}
  [ -n "$own" ] || rb_say "no box login recorded by s05_look_k6.sh: every login in $d counts as another account's"
  rb_local read local "another account's login or uid in any directory of $d (scrub_tree_e178.py --check)" \
    "$RB_PY" -B tools/claims-v3/e178/scrub_tree_e178.py --check "$d" ${own:+--owner "$own"}
  [ "$RB_RC" -eq 0 ] || rb_die $RB_E_GATE "another account's login or uid is left in $d (the scrub-tree lines above). Every other gate has passed. Before any commit: python3 -B tools/claims-v3/e178/scrub_tree_e178.py $d${own:+ --owner $own} (it rewrites those lines in place), then the same with --check (0 left), and name it in the data README"
}
RAW=build/e180-raw
[ -n "${RB_DRY:-}" ] || mkdir -p "$RAW/logs" "$RAW/build-record"
rb_probe aifoundry3
rb_local copy aifoundry3 "copy back E180's passes, smoke and stop-path test (KIT.md box step 11)" \
  rsync -a -e "$RB_RSH" aifoundry3:aifoundry/build/claims-v3/aifoundry3/e180 \
  aifoundry3:aifoundry/build/claims-v3/aifoundry3/e180-smoke aifoundry3:aifoundry/build/claims-v3/aifoundry3/e180-stoptest "$RAW/"
[ "$RB_RC" -eq 0 ] || rb_die $RB_E_FAIL "the copy back exited non-zero"
rb_local copy aifoundry3 "copy back E180's session logs and the build step's disassembly check" rsync -a -e "$RB_RSH" aifoundry3:aifoundry/build/e180/ "$RAW/logs/"
[ "$RB_RC" -eq 0 ] || rb_die $RB_E_FAIL "the logs' copy exited non-zero"
# v3 change 1: the build record and the box's kernel listing (an earlier collection's copies are removed first, so a listing the box
# did not write this time can never be read from an older copy)
[ -n "${RB_DRY:-}" ] || rm -f "${RAW:?}/build-record/BUILD-E180.json" "${RAW:?}/build-record/e180-kernel-dis.txt"
src=(aifoundry3:aifoundry/build/enercat-e180/BUILD-E180.json)
if [ -n "${RB_DRY:-}" ]; then
  src+=(aifoundry3:aifoundry/build/e180-kernel-dis.txt)
  rb_disp "--- (the listing is asked for unless the box's walk line, $RAW/logs/elfcheck-e180.txt, is absent or says 'no objdump at')"
elif [ ! -f "$RAW/logs/elfcheck-e180.txt" ]; then
  rb_say "no walk line from step 6 v2 in the logs: the box's kernel listing is not asked for (A1-7 reads UNREAD, no objdump)"
elif grep -q 'no objdump at' "$RAW/logs/elfcheck-e180.txt"; then
  rb_say "the box's walk line says step 6 found no objdump or no kernel: the listing was never written and is not asked for (A1-7 reads UNREAD, no objdump)"
else
  src+=(aifoundry3:aifoundry/build/e180-kernel-dis.txt)
fi
rb_local copy aifoundry3 "copy back the build record and the box's kernel listing (KIT.md.dated-note-2.md section 2)" \
  rsync -a -e "$RB_RSH" "${src[@]}" "$RAW/build-record/"
[ "$RB_RC" -eq 0 ] || rb_die $RB_E_FAIL "the build record's copy exited non-zero (BUILD-E180.json, or the listing step 6 v2 wrote, did not come back): run this step again; both are A1-7's and the build's evidence"
if [ -z "${RB_DRY:-}" ]; then
  for f in "$RAW"/e180-stoptest/p18002/runs.jsonl "$RAW"/e180-stoptest/p18002/runs.jsonl.gz; do
    [ -s "$f" ] && rb_die $RB_E_FAIL "STOPTEST-LAUNCHED: the stop-path test recorded a launch ($f): nothing is scored as registered"
  done
fi
rb_local desk local "collect_e180_v3.sh (the build record, check_elf_e180_v2.py, reduce_e180_v3.py, score_e180_v3.py)" \
  env PY=/usr/bin/python3 E180_DATE="$DAY" nice -n 10 bash "$COL" "$RAW"
rb_has '^scored-e180\.md written' || [ -n "${RB_DRY:-}" ] || rb_die $RB_E_FAIL "score_e180_v3 did not write scored-e180.md: read the collector's output above"
rb_nopath "$OUT"
scrub_tree "$OUT" aifoundry3
rb_say "E180 collected and scored (kit v3): $OUT (the data directory is docs/reports/data/$DAY-e180-vector-add-aifoundry3/)"
