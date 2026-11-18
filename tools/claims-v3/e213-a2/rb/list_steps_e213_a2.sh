#!/usr/bin/env bash
# E213 Amendment A2 (Q219, lane a2-e213, Wed 18 Nov 2026, before any datum of E213's arm B): the dry listing of ARM B's runbook AS AMENDED BY A2,
# in the kit's listing form (tools/claims-v3/e213/rb/list_steps_e213.sh, unchanged beside it): every box step in order with RB_DRY=1, so each prints
# its exact commands (every remote script in full) and nothing runs: no ssh, no rsync, no scp, no device, no file in the repo. A2's three steps
# (4, 9 and 12) stand where the kit's stand; every other step is the kit's own file. Stand-ins for ssh, rsync and scp go first on PATH and count a
# call they should never get, so the last line says "0 box calls" only when nothing reached for a box. The window is a SAMPLE. The card lane's
# own lines (B, 0, H, 3, E and the spans) are the kit's listing's notes, unchanged: see list_steps_e213.sh B.
#   bash tools/claims-v3/e213-a2/rb/list_steps_e213_a2.sh <an empty scratch dir> [<sample day> <last start> <last end>] > listing.txt
# SPDX-License-Identifier: Apache-2.0
set -u
D=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
K=$(cd "$D/../../e213/rb" && pwd)
K6=$(cd "$D/../../q141k-runbook/k6" && pwd)
REPO=$(cd "$D/../../../.." && pwd)
O=${1:?usage: list_steps_e213_a2.sh <an empty scratch dir> [<sample day> <last start HH:MM> <last end HH:MM>]}
day=${2:-2026-11-18}; ls=${3:-08:44}; le=${4:-10:44}
mkdir -p "$O/standin" || exit 10
O=$(cd "$O" && pwd)
for cc in ssh rsync scp; do printf '#!/bin/sh\necho "%s $*" >> "%s/box-calls.txt"\nexit 99\n' "$cc" "$O" > "$O/standin/$cc"; chmod +x "$O/standin/$cc"; done
: > "$O/box-calls.txt"
export PATH="$O/standin:$PATH" RB_DRY=1 RB_OUT="$O" RB_LOCK="$O/lock-dry.txt"
fails=0; n=0
s() { echo; echo "################ ${1#$REPO/} ${*:2}"; bash "$1" "${@:2}" 2>&1 | sed "s#$O#<RB_OUT>#g; s#$REPO#<lab clone>#g"; r=${PIPESTATUS[0]}; echo "(exit $r)"; n=$((n + 1)); [ "$r" -eq 0 ] || fails=$((fails + 1)); }
note() { echo; echo "################ $*"; }
echo "E213 runbook, ARM B (aifoundry1 card 1) AS AMENDED BY A2, dry listing (nothing below was run). Sample window: $day, last start $ls, last end $le (Pacific)."
echo "A2's steps: 4 (tools/claims-v3/e213-a2/rb/s05_look_e213_a2.sh B), 9 (tools/claims-v3/e213-a2/rb/s11_session_e213_a2.sh B), 12 (tools/claims-v3/e213-a2/rb/s23_data_e213_a2.sh B); every other step is the kit's."
note "B, 0, H (the card lane's): as the kit's listing (list_steps_e213.sh B) names them"
s "$K/s02_window_e213.sh" B "$day" "$ls" "$le"
s "$K/s03_desk_e213.sh" B
note "after step 2 (the card lane's): 'bash W/onelab.sh undesk <lane>'"
note "4 (A2): THE PINS at the desk; THE HOLDER RULE by k6's look with --wait (no identity by continuity); A2's box files synced and checked on the box; fwgate's look (no device); on NEEDS-READ ONLY: THE REST RULE, then ONE fwgate read with --both-nodes-ok (the owner's word, A2), EQUAL or the day ends; the read's folder copied back exact and its scrub checked"
s "$D/s05_look_e213_a2.sh" B
note "3: the post: none, by the owner's standing waiver of Sun 15 Nov 2026 10:22:36 PST (the kit's listing quotes his words)"
s "$K/s07_sync_e213.sh" B
s "$K/s08_build_e213.sh" B start
s "$K/s08_build_e213.sh" B wait
s "$K/s06n_neverrun_e213.sh" B
s "$K/s09_reads_e213.sh" B
s "$K/s10_dry_e213.sh" B start
s "$K/s10_dry_e213.sh" B wait
note "9 (A2): the kit's step 9 with A2's launch guard in place of k6's: fwgate's guard on this boot (this boot's EQUAL read of today, or continuity), else IDENTITY-STOP and nothing launched"
s "$D/s11_session_e213_a2.sh" B
s "$K/s20_wait_e213.sh" B
note "11 (the card lane's first): 'bash W/onelab.sh collect <lane>'"
s "$K/s22_collect_e213.sh" B
note "12 (A2): the kit's step 12, then the read's folder into the directory as fwgate/ after the kit's scrub, SHA256SUMS made again; then the README (fwgate/ and A2 among the dated departures) and the data commit"
s "$D/s23_data_e213_a2.sh" B
s "$K/s24_score_e213.sh" B
note "E (every path ends here): as the kit's listing names it"
nb=$(grep -c . "$O/box-calls.txt")
echo; echo "dry listing (A2, arm B): $n steps listed, $fails exited non-zero, $nb box calls"
[ "$fails" -eq 0 ] && [ "$nb" -eq 0 ]
