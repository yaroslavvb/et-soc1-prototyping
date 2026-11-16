#!/usr/bin/env bash
# E200 (Q192, lane kit-e200, Mon 16 Nov 2026, before any E200 datum): the dry listing of E200's runbook on aifoundry2 itself, BOTH SITTINGS,
# E197's form (tools/claims-v3/e197/rb/list_steps_e197.sh, unchanged beside it): every step in order with RB_DRY=1, so each prints its exact
# commands (every remote script in full) and nothing runs: no ssh, no rsync, no scp, no device, no file in the repo. Stand-ins for ssh,
# rsync and scp go first on PATH and each counts a call it should never get, so the last line says "0 box calls beyond aifoundry2" only
# when nothing reached for a box and every printed call names aifoundry2 alone (the desk is the box: k6's drivers reach it by ssh to
# itself). Each sitting lists in its own RB_OUT (one RB_OUT per sitting); the windows are SAMPLES (G = the booking at 10:00 for sitting 1,
# sitting 2's G its rest's opening). THE ONE-LAB RULE helper (W/onelab.sh), the booking (W/book.sh), the quiet hold (W/hold.sh) and the
# data commit are the card lane's and are named here in their places, not run. THE ORDER (CARD-LANE-BRIEF.md 2): B, 0, H, 1, 2, then Q (the
# quiet desk flag) and 4 the look, 5 the sync, 6 the build, 8 the dry pass, then, once the rest has opened, 7 the reads (the sitting's first
# card command) and 9 the launch at once, 10 the wait, 11 the collection, Q lowered, 12 the data commit, 13 the reduction.
#   bash tools/claims-v3/e200/rb/list_steps_e200.sh <an empty scratch dir> [<sample day>] > listing.txt
# SPDX-License-Identifier: Apache-2.0
set -u
D=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
REPO=$(cd "$D/../../../.." && pwd)
O=${1:?usage: list_steps_e200.sh <an empty scratch dir> [<sample day>]}
day=${2:-2026-11-16}
mkdir -p "$O/standin" "$O/1" "$O/2" || exit 10
O=$(cd "$O" && pwd)
for c in ssh rsync scp; do printf '#!/bin/sh\necho "%s $*" >> "%s/box-calls.txt"\nexit 99\n' "$c" "$O" > "$O/standin/$c"; chmod +x "$O/standin/$c"; done
: > "$O/box-calls.txt"
export PATH="$O/standin:$PATH" RB_DRY=1 RB_LOCK="$O/lock-dry.txt"
fails=0; n=0
: > "$O/listing.tmp"
s() { echo; echo "################ [sitting $SIT] ${1#$REPO/} ${*:2}"; RB_OUT="$O/$SIT" bash "$1" "${@:2}" 2>&1 | sed "s#$O#<RB_OUT>#g; s#$REPO#<lab clone>#g" | tee -a "$O/listing.tmp"; r=${PIPESTATUS[0]}; echo "(exit $r)"; n=$((n + 1)); [ "$r" -eq 0 ] || fails=$((fails + 1)); }
echo "E200 runbook (aifoundry2 card 0, run from aifoundry2 itself, both sittings), dry listing (nothing below was run). Sample windows: $day, sitting 1 from a booking at 10:00 (last start 11:30, last end 13:30); sitting 2 from its rest's opening at 11:30 (last start 13:00, last end 15:00) (Pacific)."
echo; echo "---- the runbook's prelude for aifoundry2: every remote script on aifoundry2 starts with these lines"
( . "$D/rb_e200.sh"; rb_prelude aifoundry2 ) | sed 's/^/    | /'
for SIT in 1 2; do
  if [ "$SIT" = 1 ]; then ls=11:30; le=13:30; else ls=13:00; le=15:00; fi
  echo; echo "======================================== SITTING $SIT (its own RB_OUT) ========================================"
  echo; echo "################ step B (the card lane's): bash W/book.sh take aifoundry2 <lane> (G = the time its owner file records; a booking held for both sittings serves sitting 2 too)"
  echo "################ step 0 (the card lane's): bash W/onelab.sh desk <lane> FIRST (THE ONE-LAB RULE: undesk on every stop path from here to step 2); uptime (THE LOAD RULE); the go's anchor lines; GitHub main read"
  echo "################ step H (the card lane's): bash W/hold.sh add <lane> (THE QUIET HOLD: removed after the data commit's push, and on every stop path)"
  s "$D/s02_window_e200.sh" "$SIT" "$day" "$ls" "$le"
  s "$D/s03_desk_e200.sh"
  echo; echo "################ right after step 2 (the card lane's): bash W/onelab.sh undesk <lane>"
  echo "################ step Q (the card lane's): RB_QUIET=W/locks/quiet-desk-aifoundry2 bash tools/claims-v3/e200/rb/quiet_e200.sh raise <lane>, then quiet_e200.sh count --wait (THE P2 COUNT 0); lowered after step 11's COPY-BACK EXACT and on every stop path after the raise"
  s "$D/s05_look_e200.sh"
  echo; echo "################ the day's post: none, the owner's standing waiver (his words, Sun 15 Nov 2026 10:22:36 PST): not scripted"
  s "$D/s07_sync_e200.sh"
  if [ "$SIT" = 1 ]; then s "$D/s08_build_e200.sh" start; fi
  s "$D/s08_build_e200.sh" wait
  echo; echo "################ step 6's rule: at most two starts a Pacific day (the third: NO-THIRD-BUILD, 16); a second start only when the first did not end REGFILE-BUILT; sitting 2 on the same day runs only the wait; a 14 on wait is no reading, wait again"
  s "$D/s10_dry_e200.sh" start
  s "$D/s10_dry_e200.sh" wait
  echo; echo "################ WAIT until the rest has opened (40 minutes after our last session's end on aifoundry2: E194's, or for sitting 2 sitting 1's end): nothing is sent to the card before it; then step 7 and step 9 back to back"
  s "$D/s09_reads_e200.sh" "$SIT"
  s "$D/s11_session_e200.sh" "$SIT"
  echo; echo "################ inside the sitting (session_e200.sh, detached on the box): the refusals (the box tree's layout, the host's name aifoundry2, USER, the harness at the launch's sha256, E197's registration list, the host of today's build, E200's guard, the reader at its pin, dmcmd_audit_v2 GO, exactly /dev/et0_ops and /dev/et0_mgmt, ref/'s three E197 files at E197's registration's sha256 and E200's runner made by W1 at 8774027b..., step 7's folder and the firmware identity, the first card command today and at most 120 s ago, the cap before the last end); the free check (et-who --check, re-read for a reader of ours on the management node; other users' device processes; the lock probe); THE DIE GATE (minshire[0] at or below 57 C, every 20 s for up to 10 minutes, counted in the cap); CAP_S = the cap - 60 s - (now - the first card command): the runner's deadline at the first card command + the cap - 120 s; the kit's watch beside (65 W, 70 C and aifoundry2's 85 W and 80 C lines, C3, the smoke check with the smoke's clock, the end-stop at the cap - 30 s, the hang watch: a STOP and a report, never a kill); run_session.sh $([ "$SIT" = 1 ] && echo 'full (or short)' || echo ext) with ETTELEM = E200's guard; SESSION_DONE by the wrapper if run_session.sh exits before its own; the configuration at the end (reported); the summary (the smoke, the clock, the blocks, the stop and whether it names the card, SITTING-RESULT, GATE-STOP); a crash written apart (exit 9); session end; the manifest last"
  s "$D/s20_wait_e200.sh" "$SIT"
  echo; echo "################ right before step 11 (the card lane's): bash W/onelab.sh collect <lane> (uncollect after the data commit's push, and on every stop path after it)"
  s "$D/s22_collect_e200.sh" "$SIT"
  echo; echo "################ after step 11's COPY-BACK EXACT (the card lane's): quiet_e200.sh lower <lane>; the README in the lab's form (DATA-README-FORM-e200.md) and the data commit (commit_lab.sh with LAB_QUIET_HOLD_OWNER=<lane>, new files only); then onelab.sh uncollect <lane>, hold.sh remove <lane> (and book.sh release aifoundry2 <lane> once no sitting of this booking is left); a sitting that ended at a gate is a gate stop's record instead (docs/reports/gate-stops/, committed the same way, never reduced); then the reduction on the committed data:"
  s "$D/s24_reduce_e200.sh" "$SIT"
done
nb=$(grep -c . "$O/box-calls.txt")
calls=$(grep -cE '^--- (probe [a-z0-9]+,|[a-z]+ on [a-z0-9]+ \()' "$O/listing.tmp")
to2=$(grep -cE '^--- (probe aifoundry2,|[a-z]+ on aifoundry2 \()' "$O/listing.tmp")
cp2=$(grep -E '^--- copy, run on the Intel' "$O/listing.tmp" | grep -c 'aifoundry2:')
other=$(grep -E '^--- ' "$O/listing.tmp" | grep -cE "(ConnectTimeout=10 aifoundry[13]( |'|\$)|[ '\"]aifoundry[13]:)")
beyond=$((nb + calls - to2 + other))
echo; echo "box calls printed: $calls ssh calls and probes ($to2 of them to aifoundry2) and $cp2 rsync copies to or from aifoundry2; calls to aifoundry1 or aifoundry3 (an ssh or rsync target): $other; calls that reached a stand-in ssh, rsync or scp: $nb"
echo "dry listing: $n steps listed, $fails exited non-zero, $beyond box calls beyond aifoundry2"
[ "$fails" -eq 0 ] && [ "$beyond" -eq 0 ]
