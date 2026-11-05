#!/usr/bin/env bash
# Q142(v2) fix pass, Thu 5 Nov 2026: the dry listing of the pool-8 card day's kg steps (E173 on aifoundry2, E174 on aifoundry1 card 0) through
# the v3 drivers (tools/claims-v3/e173/box/step_e173_v3.sh and tools/claims-v3/e174/box/step_e174_v3.sh), every step in order with RB_DRY=1, so
# each prints its exact commands (every remote script in full; a kit file sent as it is, by its path), and nothing runs: no ssh, no rsync, no
# device, no file in the repo. The window is a SAMPLE (his go sets the real one with s02_window_q142kg.sh).
#
# Why it exists (the first verifier of v2's fault 5): the v2 listing (logs/dry-listing-v2.txt, 34436d68) and v1's say on 13 lines that each
# box's 58-line prelude is "printed once at the top of the listing", but neither file prints it, so neither records the remote ours_live,
# jobs_live and hold_read that E174's gates rest on. This listing prints the prelude for aifoundry2 and for aifoundry1 once, at the top, as
# k6's list_steps_k6_v2.sh does; every later remote script that opens with it shows the same one-line marker.
#
#   bash tools/claims-v3/q142kg-runbook/list_steps_q142kg_v3.sh <an empty scratch dir> [<sample day> <last start> <last end>] > listing.txt
# SPDX-License-Identifier: Apache-2.0
set -u
D=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
REPO=$(cd "$D/../../.." && pwd)
O=${1:?usage: list_steps_q142kg_v3.sh <an empty scratch dir> [<sample day> <last start HH:MM> <last end HH:MM>]}
day=${2:-2026-11-05}; ls=${3:-15:30}; le=${4:-16:30}
mkdir -p "$O" || exit 10
export RB_DRY=1 RB_OUT="$O" RB_LOCK="$O/lock-dry.txt"
fails=0
s() { echo; echo "################ $*"; bash "$REPO/$1" "${@:2}"; r=$?; echo "(exit $r)"; [ "$r" -eq 0 ] || fails=$((fails + 1)); }
echo "Q142(kg) steps through the v3 drivers, dry listing (nothing below was run). Sample window: $day, last start $ls, last end $le (Pacific)."
for b in aifoundry2 aifoundry1; do
  echo; echo "---- the runbook's prelude for $b: every remote script on $b starts with these lines"
  ( . "$D/rb_common_v3.sh"; rb_prelude "$b" ) | sed 's/^/    | /'
done
s tools/claims-v3/q142kg-runbook/s02_window_q142kg.sh "$day" "$ls" "$le"
for st in look tree "dry start" "dry wait" launch "launch subset" wait collect; do
  # shellcheck disable=SC2086
  s tools/claims-v3/e173/box/step_e173_v3.sh $st
done
for st in look sync "check start" "check wait" launch "launch subset" wait pull collect; do
  # shellcheck disable=SC2086
  s tools/claims-v3/e174/box/step_e174_v3.sh $st
done
echo; echo "dry listing: $fails step(s) exited non-zero"
exit "$fails"
