#!/usr/bin/env bash
# E189 (Q167, the kit, Thu 12 Nov 2026, before any E189 datum): the dry listing of E189's runbook on aifoundry3, E188's form
# (rb/list_steps_e188_v2.sh): every step in order with RB_DRY=1, so each prints its exact commands (every remote script in full) and nothing
# runs: no ssh, no rsync, no scp, no device, no file in the repo. Stand-ins for ssh, rsync and scp go first on PATH and each counts a call it
# should never get, so the last line says "0 box calls" only when nothing reached for a box. The window is a SAMPLE. Steps 4 and 7 are
# the k6 runbook's own, unchanged; step 0 (the check v2 and E189's anchor lines) and the post are the card lane's, named only.
#   bash tools/claims-v3/e189/rb/list_steps_e189.sh <an empty scratch dir> [<sample day> <last start> <last end>] > listing.txt
# SPDX-License-Identifier: Apache-2.0
set -u
D=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
K6=$(cd "$D/../../q141k-runbook/k6" && pwd)
REPO=$(cd "$D/../../../.." && pwd)
O=${1:?usage: list_steps_e189.sh <an empty scratch dir> [<sample day> <last start HH:MM> <last end HH:MM>]}
day=${2:-2026-11-13}; ls=${3:-10:30}; le=${4:-12:30}
mkdir -p "$O/standin" || exit 10
O=$(cd "$O" && pwd)
for c in ssh rsync scp; do printf '#!/bin/sh\necho "%s $*" >> "%s/box-calls.txt"\nexit 99\n' "$c" "$O" > "$O/standin/$c"; chmod +x "$O/standin/$c"; done
: > "$O/box-calls.txt"
export PATH="$O/standin:$PATH" RB_DRY=1 RB_OUT="$O" RB_LOCK="$O/lock-dry.txt"
fails=0; n=0
s() { echo; echo "################ ${1#$REPO/} ${*:2}"; bash "$1" "${@:2}" 2>&1 | sed "s#$O#<RB_OUT>#g; s#$REPO#<lab clone>#g"; r=${PIPESTATUS[0]}; echo "(exit $r)"; n=$((n + 1)); [ "$r" -eq 0 ] || fails=$((fails + 1)); }
echo "E189 runbook (aifoundry3), dry listing (nothing below was run). Sample window: $day, last start $ls, last end $le (Pacific)."
echo; echo "---- the runbook's prelude for aifoundry3: every remote script on aifoundry3 starts with these lines"
( . "$D/rb_e189.sh"; rb_prelude aifoundry3 ) | sed 's/^/    | /'
echo; echo "################ step 0, by hand (the card lane's), under the lab-git lock: /usr/bin/python3 -I -B tools/claims-v3/e185/rb/check_day2_v2.py tree --pull; then E189's anchor lines (LAND.md); load_guard --status calm or warm"
s "$D/s02_window_e189.sh" "$day" "$ls" "$le"
s "$D/s03_desk_e189.sh"
s "$K6/s05_look_k6.sh" aifoundry3
echo; echo "################ the day's ONE post, made AFTER the look above reads FREE (the card lane's, under the post's lock): 'for 2 h' alone, 'for 4 h' after E183: not scripted"
s "$D/s07_a3_sync_e189.sh"
s "$D/s08_a3_build_e189.sh" start
s "$D/s08_a3_build_e189.sh" wait
echo; echo "################ step 6's rule: at most two starts a Pacific day (the third: NO-THIRD-BUILD, 16; the programs not built are SKIPPED); a second start only when the first built fewer than both; a 14 on wait is no reading, wait again"
s "$K6/s09_a3_reads_k6.sh"
s "$D/s10_a3_dry_e189.sh" start
s "$D/s10_a3_dry_e189.sh" wait
s "$D/s11_a3_session_e189.sh" FULL
echo; echo "################ inside the session (session_e189.sh, detached on the box): the lock, the holders, the start config (TDP 0 W / 65 C / 600 MHz), the sampler, the stop-path test, the ramped smoke, anchor 1, rounds 1-2, anchor 2, rounds 3-4, anchor 3 (the counters arm DROPPED), the closing config, session end, the manifest last"
s "$D/s20_wait_e189.sh"
echo; echo "################ the release (a rewrite of the day's post, ' — released'): not scripted"
s "$D/s22_collect_e189.sh"
echo; echo "################ the data commit (commit_lab.sh, new files only): not scripted; then the scorer on the committed data:"
s "$D/s24_score_e189.sh"
nb=$(grep -c . "$O/box-calls.txt")
echo; echo "dry listing: $n steps listed, $fails exited non-zero, $nb box calls"
[ "$fails" -eq 0 ] && [ "$nb" -eq 0 ]
