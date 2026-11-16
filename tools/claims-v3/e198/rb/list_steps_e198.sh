#!/usr/bin/env bash
# E198 (Q191, lane kit-e198, Sun 15 Nov 2026, before any E198 datum; ported from E193's file of the same step, unchanged in logic but the names below): the dry listing of E198's runbook on aifoundry1, BOTH SITTINGS, E189's
# form (rb/list_steps_e189.sh): every step in order with RB_DRY=1, so each prints its exact commands (every remote script in full) and
# nothing runs: no ssh, no rsync, no scp, no device, no file in the repo. Stand-ins for ssh, rsync and scp go first on PATH and each
# counts a call it should never get, so the last line says "0 box calls" only when nothing reached for a box. Each sitting lists in its
# own RB_OUT (one RB_OUT per sitting); the windows are SAMPLES (G, the booking, written as a sample). Step 0, the post (waived), THE
# ONE-LAB RULE's calls (W/onelab.sh, the round's helper) and the data commit are the card lane's, named only.
#   bash tools/claims-v3/e198/rb/list_steps_e198.sh <an empty scratch dir> [<sample day>] > listing.txt
# SPDX-License-Identifier: Apache-2.0
set -u
D=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
K6=$(cd "$D/../../q141k-runbook/k6" && pwd)
REPO=$(cd "$D/../../../.." && pwd)
O=${1:?usage: list_steps_e198.sh <an empty scratch dir> [<sample day>]}
day=${2:-2026-11-16}
mkdir -p "$O/standin" "$O/A" "$O/B" || exit 10
O=$(cd "$O" && pwd)
for c in ssh rsync scp; do printf '#!/bin/sh\necho "%s $*" >> "%s/box-calls.txt"\nexit 99\n' "$c" "$O" > "$O/standin/$c"; chmod +x "$O/standin/$c"; done
: > "$O/box-calls.txt"
export PATH="$O/standin:$PATH" RB_DRY=1 RB_LOCK="$O/lock-dry.txt"
fails=0; n=0
s() { echo; echo "################ [sitting $SIT] ${1#$REPO/} ${*:2}"; RB_OUT="$O/$SIT" bash "$1" "${@:2}" 2>&1 | sed "s#$O#<RB_OUT>#g; s#$REPO#<lab clone>#g"; r=${PIPESTATUS[0]}; echo "(exit $r)"; n=$((n + 1)); [ "$r" -eq 0 ] || fails=$((fails + 1)); }
echo "E198 runbook (aifoundry1 card 1, both sittings), dry listing (nothing below was run). Sample G (the card lane's booking): $day 09:00:00 for sitting A (last start 10:30, last end 12:30) and 11:40:00 for sitting B (last start 13:10, last end 15:10) (Pacific)."
echo; echo "---- the runbook's prelude for aifoundry1: every remote script on aifoundry1 starts with these lines"
( . "$D/rb_e198.sh"; rb_prelude aifoundry1 ) | sed 's/^/    | /'
for SIT in A B; do
  if [ "$SIT" = A ]; then g=09:00:00; else g=11:40:00; fi
  echo; echo "======================================== SITTING $SIT (its own RB_OUT) ========================================"
  echo; echo "################ step 0, by hand (the card lane's): uptime (the load rule), the anchor lines of E198's LAND.md (registration and kit), GitHub main read; the booking (book.sh take aifoundry1 <lane>: G); THE ONE-LAB RULE: bash W/onelab.sh desk <lane> right before step 0 (and undesk on every stop path from here to step 2)"
  s "$D/s02_window_e198.sh" "$SIT" "$day" "$g"
  s "$D/s03_desk_e198.sh"
  echo; echo "################ THE ONE-LAB RULE: bash W/onelab.sh undesk <lane> right after step 2 (the card lane's)"
  s "$D/s05_look_e198.sh"
  echo; echo "################ the day's post: waived by the owner's standing words (Sun 15 Nov 2026, 10:22:36 PST): not made, recorded as waived"
  s "$D/s07_a1_sync_e198.sh"
  if [ "$SIT" = A ]; then s "$D/s08_a1_build_e198.sh" start; fi
  s "$D/s08_a1_build_e198.sh" wait
  echo; echo "################ step 6's rule: at most two starts a Pacific day (the third: NO-THIRD-BUILD, 16); a second start only when the first did not end X04-BUILT; sitting B on the same day runs only the wait; a 14 on wait is no reading, wait again"
  s "$D/s09_a1_reads_e198.sh"
  echo; echo "################ step 7 reads THE REST RULE first: before the 40-minute rest on aifoundry1 opens it stops with 17 (call again) and opens nothing"
  s "$D/s10_a1_dry_e198.sh" start
  s "$D/s10_a1_dry_e198.sh" wait
  s "$D/s11_a1_session_e198.sh" "$SIT"
  echo; echo "################ inside the sitting (session_e198.sh $SIT, detached on the box): the harness at the launch's sha256, the preflight, the binaries against today's build record, the tree's files at their pins; the first card command (stamped as it starts; the two ps rules, et-who --check on both cards); the two-card box (/dev/et0_ops /dev/et1_ops); THE PRIVATE /dev shown (card 1's two nodes only); the start config read inside it (ET_DEVICES=1, card 1's lock): IDENTITY (a); the warden; IDENTITY (b) with the identity sampler; the runner's deadline (first command + cap - 120 s); the smoke (run_x04.py --smoke --blocks S,D,W,T,C --device 1 in the private /dev) and E193's smoke gate and the watch; the main run (--blocks $([ "$SIT" = A ] && echo S,D,W,T || echo C)); a crash written apart from a registered stop (exit 4); the closing config read; the warden's summary; session end; the manifest last"
  s "$D/s20_wait_e198.sh" "$SIT"
  echo; echo "################ THE ONE-LAB RULE: bash W/onelab.sh collect <lane> right before step 11 (and uncollect on every stop path from here to the data commit's push)"
  s "$D/s22_collect_e198.sh" "$SIT"
  echo; echo "################ the README in DATA-README-FORM-e198.md's form and the data commit (commit_lab.sh, new files only), its push; THE ONE-LAB RULE: bash W/onelab.sh uncollect <lane> right after the push; a sitting that ended at a gate is a gate stop's record instead (docs/reports/gate-stops/, committed the same way, never reduced); then the reduction on the committed data:"
  s "$D/s24_reduce_e198.sh" "$SIT"
done
echo; echo "======================================== AFTER THE DATA COMMITS (both sittings, or A alone) ========================================"
SIT=B
s "$D/s24_reduce_e198.sh" score "<RB_OUT of A>/x04-e198-A.json" "<RB_OUT of B>/x04-e198-B.json"
nb=$(grep -c . "$O/box-calls.txt")
echo; echo "dry listing: $n steps listed, $fails exited non-zero, $nb box calls"
[ "$fails" -eq 0 ] && [ "$nb" -eq 0 ]
