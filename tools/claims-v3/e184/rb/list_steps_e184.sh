#!/usr/bin/env bash
# E184 (Q153), kit note 1 (../KIT.md.dated-note-1.md section 3): the dry listing of E184's runbook, both arms, every step in order with RB_DRY=1,
# so each prints its exact commands (every remote script in full; a kit file sent as it is, by its path), and nothing runs: no ssh, no
# rsync, no device, no file in the repo. The window is a SAMPLE (his go sets the real one with s02_window_e184.sh). Steps 4 (the look) is the
# k6 runbook's own, unchanged; the day's post and its release are the card lane's, not scripted.
#
#   bash tools/claims-v3/e184/rb/list_steps_e184.sh <an empty scratch dir> [<sample day> <last start> <last end>] > listing.txt
# SPDX-License-Identifier: Apache-2.0
set -u
D=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
K6=$(cd "$D/../../q141k-runbook/k6" && pwd)
REPO=$(cd "$D/../../../.." && pwd)
O=${1:?usage: list_steps_e184.sh <an empty scratch dir> [<sample day> <last start HH:MM> <last end HH:MM>]}
day=${2:-2026-11-08}; ls=${3:-12:30}; le=${4:-16:30}
mkdir -p "$O" || exit 10
export RB_DRY=1 RB_OUT="$O" RB_LOCK="$O/lock-dry.txt"
fails=0
s() { echo; echo "################ ${1#$REPO/} ${*:2}"; bash "$1" "${@:2}"; r=$?; echo "(exit $r)"; [ "$r" -eq 0 ] || fails=$((fails + 1)); }
echo "E184 runbook (kit note 1), both arms, dry listing (nothing below was run). Sample window: $day, last start $ls, last end $le (Pacific)."
for box in aifoundry3 aifoundry1; do
  echo; echo "---- the runbook's prelude for $box: every remote script on $box starts with these lines"
  ( . "$D/rb_e184.sh"; rb_prelude "$box" ) | sed 's/^/    | /'
done
s "$D/s02_window_e184.sh" "$day" "$ls" "$le"
s "$D/s03_desk_e184.sh"
for arm in S B; do
  box=aifoundry3; [ "$arm" = B ] && box=aifoundry1
  echo; echo "================ arm $arm on $box"
  s "$K6/s05_look_k6.sh" "$box"
  echo; echo "################ the day's one post names $box (the card lane's, under the post's lock): not scripted"
  s "$D/s07_sync_e184.sh" "$arm"
  s "$D/s08_build_e184.sh" "$arm" start
  s "$D/s08_build_e184.sh" "$arm" wait
  s "$D/s09_reads_e184.sh" "$arm"
  s "$D/s10_dry_e184.sh" "$arm" start
  s "$D/s10_dry_e184.sh" "$arm" wait
  s "$D/s11_session_e184.sh" "$arm"
  s "$D/s20_wait_e184.sh" "$arm"
  echo; echo "################ the release (a rewrite of the day's post): not scripted"
  s "$D/s22_collect_e184.sh" "$arm"
done
echo; echo "dry listing: $fails step(s) exited non-zero"
exit "$fails"
