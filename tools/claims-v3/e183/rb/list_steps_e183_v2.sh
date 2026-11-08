#!/usr/bin/env bash
# E183 (Q155, the kit's dated note 1): the dry listing v2 of the runbook (RB_DRY=1: every step prints what it would call and calls
# nothing), in KIT.md's order as note 1 runs it: step 2 is s03 v2 and step 11 is s22 v2; every other step is v1's. It is
# rb/list_steps_e183.sh (v1, which stays as committed) with those two lines changed.
#   bash tools/claims-v3/e183/rb/list_steps_e183_v2.sh <an empty scratch dir> [<sample day> <last start HH:MM> <last end HH:MM>]
# v1's words follow:
# E183 (Q155, the kit): the dry listing of the runbook (RB_DRY=1: every step prints what it would call and calls nothing), in KIT.md's order,
# the look before the post (E182's list_steps_e182_v4.sh, ported). Its last line counts the steps and the ones that exited non-zero.
#   bash tools/claims-v3/e183/rb/list_steps_e183.sh <an empty scratch dir> [<sample day> <last start HH:MM> <last end HH:MM>]
# SPDX-License-Identifier: Apache-2.0
set -u
D=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
K6=$(cd "$D/../../q141k-runbook/k6" && pwd)
REPO=$(cd "$D/../../../.." && pwd)
O=${1:?usage: list_steps_e183.sh <an empty scratch dir> [<sample day> <last start HH:MM> <last end HH:MM>]}
day=${2:-2026-11-09}; ls=${3:-15:30}; le=${4:-17:30}
mkdir -p "$O" || exit 10
export RB_DRY=1 RB_OUT="$O" RB_LOCK="$O/lock-dry.txt"
fails=0; n=0
s() { echo; echo "################ ${1#$REPO/} ${*:2}"; bash "$1" "${@:2}"; r=$?; echo "(exit $r)"; n=$((n + 1)); [ "$r" -eq 0 ] || fails=$((fails + 1)); }
echo "E183 runbook (aifoundry3), dry listing v2 (note 1: step 2 v2, step 11 v2; nothing below was run). Sample window: $day, last start $ls, last end $le (Pacific)."
echo; echo "---- the runbook's prelude for aifoundry3: every remote script on aifoundry3 starts with these lines"
( . "$D/rb_e183.sh"; rb_prelude aifoundry3 ) | sed 's/^/    | /'
echo; echo "==================== FULL (or SHORT at step 9)"
s "$D/s02_window_e183.sh" "$day" "$ls" "$le"
s "$D/s03_desk_e183_v2.sh"
s "$K6/s05_look_k6.sh" aifoundry3
echo; echo "################ KIT.md box step 3, the day's one post, made AFTER the look above reads FREE (the card lane's, under the post's lock): not scripted"
s "$D/s07_a3_sync_e183.sh"
s "$D/s08_a3_build_e183.sh" start
s "$D/s08_a3_build_e183.sh" wait
echo; echo "################ step 6's re-run rule: after a build that failed, overran or was lost, start then wait ONCE more; after a second, the fallback (SKIP: no E183 session today; drop E183's clause from the post); after TRAIN-HOST-INPUTS-DIFFER, step 5 once more, then start; after 11-14 on start or wait, wait before any second start"
s "$K6/s09_a3_reads_k6.sh"
s "$D/s10_a3_dry_e183.sh" start
s "$D/s10_a3_dry_e183.sh" wait
s "$D/s11_a3_session_e183.sh" FULL
s "$D/s20_wait_e183.sh"
echo; echo "################ step 11's release (a rewrite of the day's post): not scripted"
s "$D/s22_collect_e183_v2.sh"
echo; echo "dry listing: $n steps listed, $fails exited non-zero"
exit "$fails"
