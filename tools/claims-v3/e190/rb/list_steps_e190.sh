#!/usr/bin/env bash
# E190 (Q169, the kit, Fri 13 Nov 2026, before any E190 datum): the dry listing of E190's runbook for both arms, E189's form
# (rb/list_steps_e189.sh): every step in order with RB_DRY=1, so each prints its exact commands (every remote script in full) and nothing
# runs: no ssh, no rsync, no scp, no device, no file in the repo. Stand-ins for ssh, rsync and scp go first on PATH and each counts a call it
# should never get, so the last line says "0 box calls" only when nothing reached for a box. The window is a SAMPLE. Step 4 (the look) is
# the k6 runbook's own, unchanged; step 0 (the anchor lines), THE QUIET HOLD and the data commit are the card lane's, named only. NO post
# and NO release: the owner waived the day's Discord post (his words, Fri 13 Nov 2026 about 11:30 PST).
#   bash tools/claims-v3/e190/rb/list_steps_e190.sh <an empty scratch dir> [<sample day> <last start> <last end>] > listing.txt
# SPDX-License-Identifier: Apache-2.0
set -u
D=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
K6=$(cd "$D/../../q141k-runbook/k6" && pwd)
REPO=$(cd "$D/../../../.." && pwd)
O=${1:?usage: list_steps_e190.sh <an empty scratch dir> [<sample day> <last start HH:MM> <last end HH:MM>]}
day=${2:-2026-11-13}; ls=${3:-15:00}; le=${4:-17:30}
mkdir -p "$O/standin" || exit 10
O=$(cd "$O" && pwd)
for c in ssh rsync scp; do printf '#!/bin/sh\necho "%s $*" >> "%s/box-calls.txt"\nexit 99\n' "$c" "$O" > "$O/standin/$c"; chmod +x "$O/standin/$c"; done
: > "$O/box-calls.txt"
export PATH="$O/standin:$PATH" RB_DRY=1 RB_OUT="$O" RB_LOCK="$O/lock-dry.txt"
fails=0; n=0
s() { echo; echo "################ ${1#$REPO/} ${*:2}"; bash "$1" "${@:2}" 2>&1 | sed "s#$O#<RB_OUT>#g; s#$REPO#<lab clone>#g"; r=${PIPESTATUS[0]}; echo "(exit $r)"; n=$((n + 1)); [ "$r" -eq 0 ] || fails=$((fails + 1)); }
echo "E190 runbook (arm A: aifoundry2 card 0; arm B: aifoundry1 card 1), dry listing (nothing below was run). Sample window: $day, last start $ls, last end $le (Pacific)."
for b in aifoundry2 aifoundry1; do
  echo; echo "---- the runbook's prelude for $b: every remote script on $b starts with these lines"
  ( . "$D/rb_e190.sh"; rb_prelude "$b" ) | sed 's/^/    | /'
done
echo; echo "################ step 0, by hand (the card lane's): E190's anchor lines (ANCHOR-LINES.md); THE QUIET HOLD created before step 2 (its first line the card lane's name; never over another lane's hold)"
s "$D/s02_window_e190.sh" "$day" "$ls" "$le"
s "$D/s03_desk_e190.sh"
for a in A B; do
  b=$([ "$a" = A ] && echo aifoundry2 || echo aifoundry1)
  echo; echo "======================== arm $a ($b) ========================"
  s "$K6/s05_look_k6.sh" "$b"
  echo; echo "################ NO post: the owner waived the day's Discord post (his words, Fri 13 Nov 2026 ~11:30 PST); every other etiquette check stays"
  s "$D/s07_sync_e190.sh" "$a"
  s "$D/s08_build_e190.sh" "$a" start
  s "$D/s08_build_e190.sh" "$a" wait
  echo; echo "################ step 6's rule: at most two starts a Pacific day on a box (the third: NO-THIRD-BUILD, 16, no session of that arm); a 14 on wait is no reading, wait again"
  s "$D/s10_dry_e190.sh" "$a" start
  s "$D/s10_dry_e190.sh" "$a" wait
  s "$D/s11_session_e190.sh" "$a"
  echo; echo "################ inside the session (session_e190.sh, detached on $b): the box and the build, the harness and the preflight (GO), the lock, the holders, the start config, the sampler, the stop-path test, the smoke, P1 S1 P2 S2 P3 S3 P4 S4 S5 S6, the closing config, session end, the manifest last"
  s "$D/s20_wait_e190.sh" "$a"
  s "$D/s22_collect_e190.sh" "$a"
done
echo; echo "################ NO release (no post was made). The data directory once every arm that ran is copied back:"
s "$D/s23_data_e190.sh"
echo; echo "################ the data commit (commit_lab.sh, new files only, with LAB_QUIET_HOLD_OWNER set to the hold's first line): not scripted; then THE QUIET HOLD removed (the card lane's), then the scorer on the committed data:"
s "$D/s24_score_e190.sh"
nb=$(grep -c . "$O/box-calls.txt")
echo; echo "dry listing: $n steps listed, $fails exited non-zero, $nb box calls"
[ "$fails" -eq 0 ] && [ "$nb" -eq 0 ]
