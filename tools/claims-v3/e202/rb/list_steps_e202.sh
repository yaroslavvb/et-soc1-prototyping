#!/usr/bin/env bash
# E202 (Q193, lane kit-e202, Mon 16 Nov 2026, before any E202 datum): THE DRY LISTING of E202's runbook on aifoundry3, E189's form
# (tools/claims-v3/e189/rb/list_steps_e189.sh): every step in order with RB_DRY=1, so each prints its exact commands (every remote script in
# full) and nothing runs: no ssh, no rsync, no scp, no device, no file in the repo. Stand-ins for ssh, rsync and scp go first on PATH and
# each counts a call it should never get, so the last line says "0 box calls" only when nothing reached for a box. The window is a SAMPLE
# on the listing's own day (step 1 refuses a window not for today). Steps 4 and 7's reads are the k6 runbook's own, unchanged; the card
# lane's by-hand steps (B, 0, H, THE ONE-LAB RULE's calls, the commit, E) are named only. Its lines "run on the Intel" are k6's rb_local
# wording, unchanged: they mean the desk (aifoundry2).
#   bash tools/claims-v3/e202/rb/list_steps_e202.sh <an empty scratch dir> [<last start HH:MM> <last end HH:MM>] > listing.txt
# SPDX-License-Identifier: Apache-2.0
set -u
D=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
K6=$(cd "$D/../../q141k-runbook/k6" && pwd)
REPO=$(cd "$D/../../../.." && pwd)
O=${1:?usage: list_steps_e202.sh <an empty scratch dir> [<last start HH:MM> <last end HH:MM>]}
day=$(TZ=America/Los_Angeles date +%F); ls=${2:-22:00}; le=${3:-23:59}
mkdir -p "$O/standin" || exit 10
O=$(cd "$O" && pwd)
for c in ssh rsync scp; do printf '#!/bin/sh\necho "%s $*" >> "%s/box-calls.txt"\nexit 99\n' "$c" "$O" > "$O/standin/$c"; chmod +x "$O/standin/$c"; done
: > "$O/box-calls.txt"
export PATH="$O/standin:$PATH" RB_DRY=1 RB_OUT="$O" RB_LOCK="$O/lock-dry.txt" RB_GITLOCK="$O/gitlock-dry"
fails=0; n=0
s() { echo; echo "################ ${1#$REPO/} ${*:2}"; bash "$1" "${@:2}" 2>&1 | sed "s#$O#<RB_OUT>#g; s#$REPO#<lab clone>#g"; r=${PIPESTATUS[0]}; echo "(exit $r)"; n=$((n + 1)); [ "$r" -eq 0 ] || fails=$((fails + 1)); }
h() { echo; echo "################ by hand (the card lane's): $*"; }
echo "E202 runbook (aifoundry3 card 0, from aifoundry2), dry listing (nothing below was run). Sample window: $day, last start $ls, last end $le (Pacific)."
echo; echo "---- the runbook's prelude for aifoundry3: every remote script on aifoundry3 starts with these lines"
( . "$D/rb_e202.sh"; rb_prelude aifoundry3 ) | sed 's/^/    | /'
h "B: bash W/book.sh take aifoundry3 <lane> (G = this moment; 1: another lane holds it: no ssh call to aifoundry3 at all)"
h "0: bash W/onelab.sh desk <lane> (THE ONE-LAB RULE); uptime (THE LOAD RULE); GitHub main read; E202's anchor lines (the land files)"
h "H: bash W/hold.sh add <lane> (THE QUIET HOLD, until the data commit); the lab clone's status reads 0 lines"
s "$D/s02_window_e202.sh" "$day" "$ls" "$le"
s "$D/s03_desk_e202.sh"
h "bash W/onelab.sh undesk <lane> (right after step 2; and on every stop path inside steps 0-2, before E)"
s "$K6/s05_look_k6.sh" aifoundry3
h "3: the post: none (the owner's standing waiver of Sun 15 Nov 2026 10:22:36 PST)"
s "$D/s07_a3_sync_e202.sh"
s "$D/s08_a3_build_e202.sh" start
s "$D/s08_a3_build_e202.sh" wait
h "step 6's rule: at most two starts a Pacific day (the third: NO-THIRD-BUILD, 16, no session that day); a 14 on wait is no reading, wait again"
s "$D/s09_a3_reads_e202.sh"
s "$D/s10_a3_dry_e202.sh" start
s "$D/s10_a3_dry_e202.sh" wait
s "$D/s11_a3_session_e202.sh"
h "inside the session (session_e202.sh, detached on the box): the refusals, the lock, et-who, the first card command (config), the sampler, the stop-path test, anchor 1, the smoke (T-scp Z-scp T-dram Z-dram ACC) and its gate, the R rule, the bursts T Z Z T T Z Z T (+ dram T Z Z T REPORTED), anchor 2, et-who and the closing config, session end, the manifest last"
s "$D/s20_wait_e202.sh"
h "bash W/onelab.sh collect <lane> (before step 11)"
s "$D/s22_collect_e202.sh"
h "12: the data README (DATA-README-FORM-e202.md), the public-text scan, LAB_QUIET_HOLD_OWNER=<lane> bash W/commit_lab.sh ... (new files only); then bash W/onelab.sh uncollect <lane>"
s "$D/s24_score_e202.sh"
h "E: bash W/hold.sh remove <lane>; bash W/book.sh release aifoundry3 <lane> (on every stop path too, with undesk or uncollect if held)"
nb=$(grep -c . "$O/box-calls.txt")
echo; echo "dry listing: $n steps listed, $fails exited non-zero, $nb box calls"
[ "$fails" -eq 0 ] && [ "$nb" -eq 0 ]
