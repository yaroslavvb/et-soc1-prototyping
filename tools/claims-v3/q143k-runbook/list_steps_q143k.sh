#!/usr/bin/env bash
# Q143(k): the dry listing of the runbook for M11's E176 session, every step in order with RB_DRY=1, so each prints its exact commands (every
# remote script in full) and nothing runs: no ssh, no rsync, no device, no file in the repo. The window is a SAMPLE (s02 sets the real one).
#
#   bash tools/claims-v3/q143k-runbook/list_steps_q143k.sh <an empty scratch dir> [<sample day> <last start> <last end>] > listing.txt
# SPDX-License-Identifier: Apache-2.0
set -u
D=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
O=${1:?usage: list_steps_q143k.sh <an empty scratch dir> [<sample day> <last start HH:MM> <last end HH:MM>]}
day=${2:-2026-11-05}; ls=${3:-18:30}; le=${4:-20:30}
mkdir -p "$O" || exit 10
export RB_DRY=1 RB_OUT="$O" RB_LOCK="$O/lock-dry.txt"
fails=0
s() { echo; echo "################ $*"; bash "$D/$1" "${@:2}"; r=$?; echo "(exit $r)"; [ "$r" -eq 0 ] || fails=$((fails + 1)); }
echo "Q143(k) runbook for E176, dry listing (nothing below was run). Sample window: $day, last start $ls, last end $le (Pacific)."
echo; echo "---- the runbook's prelude for aifoundry3: every remote script on aifoundry3 starts with these lines"
( . "$D/rb_common.sh"; rb_prelude aifoundry3 ) | sed 's/^/    | /'
s s02_window_q143k.sh "$day" "$ls" "$le"
s s03_desk_q143k.sh
s s05_look_q143k.sh aifoundry3
echo; echo "################ step 6: the day's one post (the card lane's, under the post's lock): not scripted"
s s07_a3_sync_q143k.sh
s s08_a3_preflight_q143k.sh
s s09_a3_reads_q143k.sh
s s10_a3_dry_q143k.sh start
s s10_a3_dry_q143k.sh wait
s s11_a3_session_q143k.sh
s s11_a3_session_q143k.sh --later-try
s s20_wait_q143k.sh
echo; echo "################ step 21: the release (a rewrite of the day's post): not scripted"
s s22_collect_q143k.sh
echo; echo "dry listing: $fails step(s) exited non-zero"
exit "$fails"
