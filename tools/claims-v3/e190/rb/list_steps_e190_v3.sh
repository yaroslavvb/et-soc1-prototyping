#!/usr/bin/env bash
# E190 (Q177, the kit's dated note 2, lane note2-e190, Sat 14 Nov 2026, after E190's first card day and before any later E190 day): the
# dry listing of E190's runbook v3 for both arms, rb/list_steps_e190_v2.sh's form (note 1's, unchanged beside it): every step in order
# with RB_DRY=1, so each prints its exact commands (every remote script in full) and nothing runs: no ssh, no rsync, no scp, no device, no
# file in the repo. Stand-ins for ssh, rsync and scp go first on PATH and each counts a call it should never get, so the last line says
# "0 box calls" only when nothing reached for a box. The window is a SAMPLE. It is note 1's listing with note 2's two steps in place of
# note 1's: step 2 v3 (rb/s03_desk_e190_v3.sh: step 2 v2 inside it, then note 2's list and logs) and step 10 v3 (rb/s20_wait_e190_v3.sh,
# whose GATE-STOPPED pattern no longer holds the identity gate's pass line). Steps 1, 12 and 13 are the kit's (unchanged); 5, 6, 8, 9 and
# 11 are note 1's v2; step 4 (the look) is the k6 runbook's own; s25 (note 1's report) follows step 13. Step 0 (the anchor lines), THE
# QUIET HOLD (W/hold.sh add/remove, one owner a line) and the data commit are the card lane's, named only. The post and its release on a
# later E190 day are the owner's call for that day (he waived the post of Fri 13 Nov 2026: his words, about 11:30 PST): named only.
#   bash tools/claims-v3/e190/rb/list_steps_e190_v3.sh <an empty scratch dir> [<sample day> <last start> <last end>] > listing.txt
# SPDX-License-Identifier: Apache-2.0
set -u
D=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
K6=$(cd "$D/../../q141k-runbook/k6" && pwd)
REPO=$(cd "$D/../../../.." && pwd)
O=${1:?usage: list_steps_e190_v3.sh <an empty scratch dir> [<sample day> <last start HH:MM> <last end HH:MM>]}
day=${2:-2026-11-13}; ls=${3:-15:00}; le=${4:-17:30}
mkdir -p "$O/standin" || exit 10
O=$(cd "$O" && pwd)
for c in ssh rsync scp; do printf '#!/bin/sh\necho "%s $*" >> "%s/box-calls.txt"\nexit 99\n' "$c" "$O" > "$O/standin/$c"; chmod +x "$O/standin/$c"; done
: > "$O/box-calls.txt"
export PATH="$O/standin:$PATH" RB_DRY=1 RB_OUT="$O" RB_LOCK="$O/lock-dry.txt"
fails=0; n=0
s() { echo; echo "################ ${1#$REPO/} ${*:2}"; bash "$1" "${@:2}" 2>&1 | sed "s#$O#<RB_OUT>#g; s#$REPO#<lab clone>#g"; r=${PIPESTATUS[0]}; echo "(exit $r)"; n=$((n + 1)); [ "$r" -eq 0 ] || fails=$((fails + 1)); }
echo "E190 runbook v3 (kit dated notes 1 and 2; arm A: aifoundry2 card 0; arm B: aifoundry1 card 1), dry listing (nothing below was run). Sample window: $day, last start $ls, last end $le (Pacific)."
for b in aifoundry2 aifoundry1; do
  echo; echo "---- the runbook's prelude for $b: every remote script on $b starts with these lines"
  ( . "$D/rb_e190_v2.sh"; rb_prelude "$b" ) | sed 's/^/    | /'
done
echo; echo "################ step 0, by hand (the card lane's): E190's anchor lines (note 1's and note 2's); 'bash W/hold.sh add <lane>' before step 2 (one owner a line; never over or in place of another lane's line); the bookings (W/book.sh take aifoundry2 / aifoundry1 <lane>); the quiet desk on aifoundry2 from step 4 to the copy-back"
s "$D/s02_window_e190.sh" "$day" "$ls" "$le"
s "$D/s03_desk_e190_v3.sh"
for a in A B; do
  b=$([ "$a" = A ] && echo aifoundry2 || echo aifoundry1)
  echo; echo "======================== arm $a ($b) ========================"
  s "$K6/s05_look_k6.sh" "$b"
  echo; echo "################ the post: on a later E190 day the owner's call for that day (he waived the post of Fri 13 Nov 2026: his words, ~11:30 PST); every other etiquette check stays"
  s "$D/s07_sync_e190_v2.sh" "$a"
  s "$D/s08_build_e190_v2.sh" "$a" start
  s "$D/s08_build_e190_v2.sh" "$a" wait
  echo; echo "################ step 6's rule: at most two starts a Pacific day on a box, v1 and v2 counted together (the third: NO-THIRD-BUILD, 16, no session of that arm); a 14 on wait is no reading, wait again"
  s "$D/s10_dry_e190_v2.sh" "$a" start
  s "$D/s10_dry_e190_v2.sh" "$a" wait
  s "$D/s11_session_e190_v2.sh" "$a"
  echo; echo "################ inside the session (session_e190_v2.sh, detached on $b): the box and the build v2, the harness v2 and the preflight v2 (GO), the lock, the holders, the start config and THE IDENTITY GATE, the sampler, the stop-path test, THE IDENTITY READ, the smoke (the host's card watched; the board's rise), P1 S1 P2 S2 P3 S3 P4 S4 S5 S6 (the host watched, a live sampler before every process), the closing config, session end, the manifest last"
  s "$D/s20_wait_e190_v3.sh" "$a"
  s "$D/s22_collect_e190_v2.sh" "$a"
done
echo; echo "################ the release, if that day's post was made. The data directory once every arm that ran is copied back:"
s "$D/s23_data_e190.sh"
echo; echo "################ the data commit (commit_lab.sh, new files only, with LAB_QUIET_HOLD_OWNER=<the lane>, its line on the hold): not scripted; then 'bash W/hold.sh remove <lane>' (the card lane's; on every stop path too), then the scorer on the committed data, then note 1's report:"
s "$D/s24_score_e190.sh"
s "$D/s25_report_e190_n1.sh"
nb=$(grep -c . "$O/box-calls.txt")
echo; echo "dry listing: $n steps listed, $fails exited non-zero, $nb box calls"
[ "$fails" -eq 0 ] && [ "$nb" -eq 0 ]
