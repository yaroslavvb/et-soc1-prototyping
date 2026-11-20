#!/usr/bin/env bash
# E220's arm A in E213's Amendment A2 form (Q233, lane kit-e220, Fri 20 Nov 2026, before any E220 datum; E213's A2 by Q219's lane a2-e213, landed 8b675547, run by card-e213b2 on Wed 18 Nov 2026): the dry listing of ARM A's runbook AS AMENDED BY A2,
# in the kit's listing form (tools/claims-v3/e220/rb/list_steps_e220a.sh, unchanged beside it): every box step in order with RB_DRY=1, so each prints
# its exact commands (every remote script in full) and nothing runs: no ssh, no rsync, no scp, no device, no file in the repo. A2's three steps
# (4, 9 and 12) stand where the kit's stand; every other step is the kit's own file. Stand-ins for ssh, rsync and scp go first on PATH and count a
# call they should never get, so the last line says "0 box calls" only when nothing reached for a box. The window is a SAMPLE. The card lane's
# own lines (B, 0, H, 3, E and the spans) are the kit's listing's notes, unchanged: see list_steps_e220a.sh A.
#   bash tools/claims-v3/e220/a2/rb/list_steps_e220a_a2.sh <an empty scratch dir> [<sample day> <last start> <last end>] > listing.txt
# SPDX-License-Identifier: Apache-2.0
set -u
D=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
K=$(cd "$D/../../rb" && pwd)
K6=$(cd "$D/../../../q141k-runbook/k6" && pwd)
REPO=$(cd "$D/../../../../.." && pwd)
O=${1:?usage: list_steps_e220a_a2.sh <an empty scratch dir> [<sample day> <last start HH:MM> <last end HH:MM>]}
day=${2:-2026-11-20}; ls=${3:-09:20}; le=${4:-11:20}
mkdir -p "$O/standin" || exit 10
O=$(cd "$O" && pwd)
for cc in ssh rsync scp; do printf '#!/bin/sh\necho "%s $*" >> "%s/box-calls.txt"\nexit 99\n' "$cc" "$O" > "$O/standin/$cc"; chmod +x "$O/standin/$cc"; done
: > "$O/box-calls.txt"
export PATH="$O/standin:$PATH" RB_DRY=1 RB_OUT="$O" RB_LOCK="$O/lock-dry.txt"
fails=0; n=0
s() { echo; echo "################ ${1#$REPO/} ${*:2}"; bash "$1" "${@:2}" 2>&1 | sed "s#$O#<RB_OUT>#g; s#$REPO#<lab clone>#g"; r=${PIPESTATUS[0]}; echo "(exit $r)"; n=$((n + 1)); [ "$r" -eq 0 ] || fails=$((fails + 1)); }
note() { echo; echo "################ $*"; }
echo "E220 runbook, ARM A (aifoundry1 card 1) AS AMENDED BY A2, dry listing (nothing below was run). Sample window: $day, last start $ls, last end $le (Pacific)."
echo "A2's steps: 4 (tools/claims-v3/e220/a2/rb/s05_look_e220a_a2.sh A), 9 (tools/claims-v3/e220/a2/rb/s11_session_e220a_a2.sh A), 12 (tools/claims-v3/e220/a2/rb/s23_data_e220a_a2.sh A); every other step is the kit's."
note "B, 0, H (the card lane's): as the kit's listing (list_steps_e220a.sh A) names them"
s "$K/s02_window_e220a.sh" A "$day" "$ls" "$le"
s "$K/s03_desk_e220a.sh" A
note "after step 2 (the card lane's): 'bash W/onelab.sh undesk <lane>'"
note "4 (A2): THE PINS at the desk; THE HOLDER RULE by k6's look with --wait (no identity by continuity); A2's box files synced and checked on the box; fwgate's look (no device); on NEEDS-READ ONLY: THE REST RULE, then ONE fwgate read with --both-nodes-ok (the owner's word, A2), EQUAL or the day ends; the read's folder copied back exact and its scrub checked"
s "$D/s05_look_e220a_a2.sh" A
note "3: the post: none, by the owner's standing waiver of Sun 15 Nov 2026 10:22:36 PST (the kit's listing quotes his words)"
s "$K/s07_sync_e220a.sh" A
s "$K/s08_build_e220a.sh" A start
s "$K/s08_build_e220a.sh" A wait
s "$K/s06n_neverrun_e220a.sh" A
s "$K/s09_reads_e220a.sh" A
s "$K/s10_dry_e220a.sh" A start
s "$K/s10_dry_e220a.sh" A wait
note "9 (A2): the kit's step 9 with A2's launch guard in place of k6's: fwgate's guard on this boot (this boot's EQUAL read of today, or continuity), else IDENTITY-STOP and nothing launched"
s "$D/s11_session_e220a_a2.sh" A
s "$K/s20_wait_e220a.sh" A
note "11 (the card lane's first): 'bash W/onelab.sh collect <lane>'"
s "$K/s22_collect_e220a.sh" A
note "12 (A2): the kit's step 12, then the read's folder into the directory as fwgate/ after the kit's scrub, SHA256SUMS made again; then the README (fwgate/ and A2 among the dated departures) and the data commit"
s "$D/s23_data_e220a_a2.sh" A
s "$K/s24_score_e220a.sh" A
note "E (every path ends here): as the kit's listing names it"
nb=$(grep -c . "$O/box-calls.txt")
echo; echo "dry listing (A2, arm A): $n steps listed, $fails exited non-zero, $nb box calls"
[ "$fails" -eq 0 ] && [ "$nb" -eq 0 ]
