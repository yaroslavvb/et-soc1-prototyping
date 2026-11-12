#!/usr/bin/env bash
# E183 (the kit's dated note 4, KIT.md.dated-note-4.md, Thu 12 Nov 2026, before any E183 datum): KIT.md box step 5a, NEW, before any E183
# build: the read-only copy of the train host's build records that Thu 12 Nov 2026's two failed builds left on aifoundry3 (card-e183's list),
# so that the next build (step 6, which rewrites the cmake log, the inputs and tree checks and the job's files) cannot lose them. ONE bounded
# read-only rsync from aifoundry3:aifoundry/ into this day's RB_OUT (k6's copy class: the 15 s probe first, 600 s for the copy; a printed
# login link stops it with 11 and appends "<HH:MM:SS> aifoundry3 needs a check" to RB_LOCK), relative paths kept under
# $RB_OUT/box-records-e183/:
#   build/e183-build-logs/          every day's build logs (2026-11-12/: e183-build-host-start1.txt and -start2.txt)
#   build/e183-build-attempts.txt   the box's count of builds (two started, two ended rc=1 on Thu 12 Nov)
#   build/enercat-e183-cmake.log    the last build's cmake log, which names the box's compiler
#   build/e183-inputs.txt, build/e183-inputs-build.txt, build/e183-tree-check.txt   the inputs' and the tree's checks
#   build/q141k/jobs/a3-build-e183.sh, .out, .pid, .rc                              the build job's files
# The rsync sends from the box and writes only here: nothing on the box is written, moved or removed. Then, at the desk, it prints the
# cmake log's compiler lines ("The C/CXX compiler identification is ...") and writes RECORDS-COPIED (the copied files and their sha256),
# which step 6 v2 (rb/s08_a3_build_e183_v2.sh start) requires before it builds.
# A record not on the box is a GAP, not a failure, only when the box's own rsync says so: rsync exits 23 (rb_run.py's 14, its child_rc in
# the runbook log) and every record not copied has its own sender line 'link_stat "<...>/<record>" failed: No such file or directory'.
# The only other lines allowed are rsync's code-23 summary and, when not one record is on the box, any rsync line naming a broken pipe
# ('rsync: [Receiver] write error: Broken pipe (32)': with every source missing, the remote sender ends at once and the receiver prints it;
# safe to pass then, since the box's own rsync has named every record missing and nothing was there to lose; real rsync
# 3.5.1 in remote mode, verify-kit183's MR4/MR6; local mode did not print it on the desk). The copy then reads COPIED WITH GAPS (0 files when none is
# there) and the marker names the gaps. Anything else (another exit code, an error line, a record missing from the copy that the box's
# rsync did not name missing) is 14 and no marker: run this step again before step 6.
# It runs ONCE a day, before step 6: with RECORDS-COPIED already in this RB_OUT it refuses (16) before any call, so a second run after step 6
# cannot overwrite Thursday's records with the new day's (verify-kit183's nit). These records stay in RB_OUT, outside the repo: a records
# round that commits any of them scrubs them first (E178's scrub_tree_e178.py: they may hold the box account's home path).
# Exit codes k6's: 0 copied; 10 usage; 11 a login link; 12 no answer; 13 past the bound; 14 the copy failed (no marker: run it again);
# 16 the marker is already here (the same day: go on to step 5; a new day: a new RB_OUT).
#   bash tools/claims-v3/e183/rb/s06_a3_records_e183.sh
# SPDX-License-Identifier: Apache-2.0
. "$(dirname "${BASH_SOURCE[0]}")/rb_e183.sh"
rb_init s06_a3_records
DEST=$RB_OUT/box-records-e183
RECS="build/e183-build-logs build/e183-build-attempts.txt build/enercat-e183-cmake.log build/e183-inputs.txt build/e183-inputs-build.txt build/e183-tree-check.txt build/q141k/jobs/a3-build-e183.sh build/q141k/jobs/a3-build-e183.out build/q141k/jobs/a3-build-e183.pid build/q141k/jobs/a3-build-e183.rc"
if [ -z "${RB_DRY:-}" ] && [ -f "$DEST/RECORDS-COPIED" ]; then
  rb_die $RB_E_GATE "RB_OUT/box-records-e183/RECORDS-COPIED is already here ($(head -n 1 "$DEST/RECORDS-COPIED" | sed 's/^# //' | cut -c1-160)): step 5a copies once a day, before step 6, and a second copy after step 6 would overwrite Thursday's records with the new day's. Nothing was called. The same day: go on to step 5 (step 6 v2 reads this marker); a new day: a new RB_OUT"
fi
SRCS=()
for r in $RECS; do SRCS+=("aifoundry3:aifoundry/./$r"); done
[ -n "${RB_DRY:-}" ] || mkdir -p "$DEST"
rb_probe aifoundry3
rb_local copy aifoundry3 "aifoundry3's E183 build records, one read-only rsync (the box only sends; nothing there is written, moved or removed)" \
  rsync -a -R -e "$RB_RSH" "${SRCS[@]}" "$DEST/"
if [ -n "${RB_DRY:-}" ]; then
  rb_say "the records copied into RB_OUT/box-records-e183/, the compiler line printed, RECORDS-COPIED written (step 6 v2 requires it)"
  exit 0
fi
gaps=""; have=""
for r in $RECS; do if [ -e "$DEST/$r" ]; then have="$have $r"; else gaps="$gaps $r"; fi; done
if [ "$RB_RC" -ne 0 ]; then    # rb_run.py's 14 for any non-zero exit; rsync's own status is the log line's child_rc
  crc=$(grep " step=$RB_STEP class=copy " "$RB_LOG" 2>/dev/null | tail -n 1 | sed -nE 's/.* child_rc=([0-9]+) .*/\1/p')
  unproven=""
  for r in $gaps; do   # the sender's path ends ".../<record>" (shell mode prints it whole) or is the record itself
    grep -qF "/$r\" failed: No such file or directory" "$RB_CAP" 2>/dev/null || grep -qF "\"$r\" failed: No such file or directory" "$RB_CAP" 2>/dev/null || unproven="$unproven $r"
  done
  other=$(grep -E 'rsync|failed|error' "$RB_CAP" 2>/dev/null | grep -v -E 'link_stat ".*" failed: No such file or directory|some files/attrs were not transferred')
  pipe=$(printf '%s\n' "$other" | grep -c -E '^rsync.*Broken pipe')   # 3.5.1's receiver: 'rsync: [Receiver] write error: Broken pipe (32)'
  [ -z "$have" ] && other=$(printf '%s\n' "$other" | grep -v -E '^rsync.*Broken pipe')
  if [ "${crc:-}" = 23 ] && [ -n "$gaps" ] && [ -z "$unproven" ] && [ -z "$other" ]; then
    rb_say "rsync's code 23: the box's own rsync names each of these records missing (one 'link_stat ... No such file or directory' line each):$gaps"
    [ -z "$have" ] && [ "$pipe" -gt 0 ] && rb_say "not one record is on aifoundry3, so rsync also printed its receiver's broken pipe (its sender ended at once): read as part of that case"
  else
    why=""
    [ "${crc:-}" = 23 ] || why="$why rsync exited ${crc:-(not read)}, and only its 23 (a partial transfer) can mean records not on the box;"
    [ -n "$gaps" ] || why="$why every record is here, yet rsync failed;"
    [ -n "$unproven" ] && why="$why not copied, and not named missing by the box's rsync:$unproven;"
    [ -n "$other" ] && why="$why other lines: $(printf '%s\n' "$other" | head -n 3 | sed -E 's#/home/[^/ ]+/#/home/<box account>/#g' | tr '\n' '|' | cut -c1-300);"
    rb_die $RB_E_FAIL "the records' copy exited $RB_RC:$why no marker written; run this step again before step 6"
  fi
fi
n=0
{ echo "# E183's build records copied from aifoundry3:aifoundry/ by s06_a3_records_e183.sh, $(date '+%F %T %Z'); rsync rc $RB_RC"
  for r in $RECS; do
    if [ -d "$DEST/$r" ]; then find "$DEST/$r" -type f | LC_ALL=C sort | while IFS= read -r f; do echo "$(shasum -a 256 "$f" | cut -d' ' -f1)  ${f#$DEST/}"; done
    elif [ -f "$DEST/$r" ]; then echo "$(shasum -a 256 "$DEST/$r" | cut -d' ' -f1)  $r"; fi
  done
  [ -n "$gaps" ] && echo "# not on aifoundry3:$gaps"
} > "$DEST/RECORDS-COPIED.tmp"
n=$(grep -c -v '^#' "$DEST/RECORDS-COPIED.tmp")
mv "$DEST/RECORDS-COPIED.tmp" "$DEST/RECORDS-COPIED"
cl="(no cmake log copied)"
[ -f "$DEST/build/enercat-e183-cmake.log" ] && cl=$(grep -E 'compiler identification is' "$DEST/build/enercat-e183-cmake.log" | sed -E 's#/home/[^/ ]+/#/home/<box account>/#g' | head -n 2 | tr '\n' ';')
echo "[$RB_STEP] the box's compiler, from build/enercat-e183-cmake.log: ${cl:-no 'compiler identification' line in it}"
echo "$(date '+%F %T %Z') step=$RB_STEP compiler: ${cl:-none read}" >> "$RB_LOG"
if [ -n "$gaps" ]; then
  rb_say "COPIED WITH GAPS: $n files of E183's build records into RB_OUT/box-records-e183/ (RECORDS-COPIED lists them and their sha256); not on the box:$gaps"
else
  rb_say "RECORDS COPIED: $n files of E183's build records into RB_OUT/box-records-e183/ (RECORDS-COPIED lists them and their sha256); nothing on the box was written or moved"
fi
