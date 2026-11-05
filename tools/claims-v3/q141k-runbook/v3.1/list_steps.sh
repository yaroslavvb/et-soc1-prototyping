#!/usr/bin/env bash
# Q141(k): the dry listing. Every step of the runbook in the go checklist's order with RB_DRY=1, so each prints its exact commands,
# local and remote (every remote script in full; a kit file sent as it is, by its path), and nothing runs: no ssh, no rsync, no
# device, no file in the repo. The window is a SAMPLE (his go sets the real one with s02_window.sh); the times in it show where
# the gates go.
#
#   bash tools/claims-v3/q141k-runbook/list_steps.sh <an empty scratch dir> [<sample day> <last start> <last end>] > listing.txt
# SPDX-License-Identifier: Apache-2.0
set -u
D=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
O=${1:?usage: list_steps.sh <an empty scratch dir> [<sample day> <last start HH:MM> <last end HH:MM>]}
day=${2:-2026-11-05}; ls=${3:-15:30}; le=${4:-16:30}
mkdir -p "$O" || exit 10
export RB_DRY=1 RB_OUT="$O" RB_LOCK="$O/lock-dry.txt"
s() { echo; echo "################ $*"; bash "$D/$1" "${@:2}"; echo "(exit $?)"; }
echo "Q141(k) runbook, dry listing (nothing below was run). Sample window: $day, last start $ls, last end $le (Pacific)."
for b in aifoundry3 aifoundry1 aifoundry2; do
  echo; echo "---- the runbook's prelude for $b: every remote script on $b starts with these lines"
  ( . "$D/rb_common.sh"; rb_prelude "$b" ) | sed 's/^/    | /'
done
s s01_probe.sh
s s02_window.sh "$day" "$ls" "$le" full
s s03_desk.sh
s s05_look.sh aifoundry3
s s05_look.sh aifoundry1
s s05_look.sh aifoundry2 --wait
echo; echo "################ go checklist step 6: the day's one post (the main session's, under the Discord lock): not scripted"
s s07_a3_sync.sh
s s08_a3_preflight.sh
s s09_a3_reads.sh
s s10_a3_dry.sh start
s s10_a3_dry.sh wait
s s11_a3_session.sh e166
s s11_a3_session.sh e166 --later-try
s s11_a3_session.sh e163 FULL
s s12_a1_check.sh sync
s s12_a1_check.sh start
s s12_a1_check.sh wait
s s13_a1_launch.sh
s s13_a1_launch.sh --drop-p2
s s14_a2_tree.sh
for r in e165 e167 e168 e169; do s s15_a2_dry.sh "$r" start; s s15_a2_dry.sh "$r" wait; done
s s16_a2_e165.sh full
s s16_a2_e165.sh subset
s s17_a2_e167.sh latch
s s17_a2_e167.sh config
s s17_a2_e167.sh go 13:10 14:30 "$ls" "$le"
s s18_a2_e168.sh
s s19_a2_e169.sh
for r in e166 e163 e164 e165 e167 e168 e169; do s s20_wait.sh "$r"; done
echo; echo "################ go checklist step 21: the releases (rewrites of the day's post): not scripted"
for r in e163 e166 e164 e165 e167 e168 e169 pair; do s s22_collect.sh "$r"; done
