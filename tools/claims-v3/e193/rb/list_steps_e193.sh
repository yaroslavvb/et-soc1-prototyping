#!/usr/bin/env bash
# E193 (Q177, lane kit-e193, Sat 14 Nov 2026, before any E193 datum): the dry listing of E193's runbook on aifoundry3, BOTH SITTINGS, E189's
# form (rb/list_steps_e189.sh): every step in order with RB_DRY=1, so each prints its exact commands (every remote script in full) and
# nothing runs: no ssh, no rsync, no scp, no device, no file in the repo. Stand-ins for ssh, rsync and scp go first on PATH and each
# counts a call it should never get, so the last line says "0 box calls" only when nothing reached for a box. Each sitting lists in its
# own RB_OUT (one RB_OUT per sitting); the windows are SAMPLES. Steps 4 and 7 are the k6 runbook's own, unchanged; step 0 and the post
# are the card lane's, named only.
#   bash tools/claims-v3/e193/rb/list_steps_e193.sh <an empty scratch dir> [<sample day>] > listing.txt
# SPDX-License-Identifier: Apache-2.0
set -u
D=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
K6=$(cd "$D/../../q141k-runbook/k6" && pwd)
REPO=$(cd "$D/../../../.." && pwd)
O=${1:?usage: list_steps_e193.sh <an empty scratch dir> [<sample day>]}
day=${2:-2026-11-16}
mkdir -p "$O/standin" "$O/A" "$O/B" || exit 10
O=$(cd "$O" && pwd)
for c in ssh rsync scp; do printf '#!/bin/sh\necho "%s $*" >> "%s/box-calls.txt"\nexit 99\n' "$c" "$O" > "$O/standin/$c"; chmod +x "$O/standin/$c"; done
: > "$O/box-calls.txt"
export PATH="$O/standin:$PATH" RB_DRY=1 RB_LOCK="$O/lock-dry.txt"
fails=0; n=0
s() { echo; echo "################ [sitting $SIT] ${1#$REPO/} ${*:2}"; RB_OUT="$O/$SIT" bash "$1" "${@:2}" 2>&1 | sed "s#$O#<RB_OUT>#g; s#$REPO#<lab clone>#g"; r=${PIPESTATUS[0]}; echo "(exit $r)"; n=$((n + 1)); [ "$r" -eq 0 ] || fails=$((fails + 1)); }
echo "E193 runbook (aifoundry3 card 0, both sittings), dry listing (nothing below was run). Sample windows: $day, sitting A last start 10:30, last end 12:30; sitting B last start 13:30, last end 15:00 (Pacific)."
echo; echo "---- the runbook's prelude for aifoundry3: every remote script on aifoundry3 starts with these lines"
( . "$D/rb_e193.sh"; rb_prelude aifoundry3 ) | sed 's/^/    | /'
for SIT in A B; do
  if [ "$SIT" = A ]; then ls=10:30; le=12:30; else ls=13:30; le=15:00; fi
  echo; echo "======================================== SITTING $SIT (its own RB_OUT) ========================================"
  echo; echo "################ step 0, by hand (the card lane's): uptime (the load rule), the anchor lines of E193's LAND.md (registration and kit), GitHub main read"
  s "$D/s02_window_e193.sh" "$SIT" "$day" "$ls" "$le"
  s "$D/s03_desk_e193.sh"
  s "$K6/s05_look_k6.sh" aifoundry3
  echo; echo "################ the day's post, made AFTER the look above reads FREE, or his waiver of it for the day (the card lane's): not scripted"
  s "$D/s07_a3_sync_e193.sh"
  if [ "$SIT" = A ]; then s "$D/s08_a3_build_e193.sh" start; fi
  s "$D/s08_a3_build_e193.sh" wait
  echo; echo "################ step 6's rule: at most two starts a Pacific day (the third: NO-THIRD-BUILD, 16); a second start only when the first did not end X04-BUILT; sitting B on the same day runs only the wait; a 14 on wait is no reading, wait again"
  s "$K6/s09_a3_reads_k6.sh"
  s "$D/s10_a3_dry_e193.sh" start
  s "$D/s10_a3_dry_e193.sh" wait
  s "$D/s11_a3_session_e193.sh" "$SIT"
  echo; echo "################ inside the sitting (session_e193.sh $SIT, detached on the box): the harness at the launch's sha256, the preflight, the binaries against today's build record; the first card command (its time stamped as it starts; the two ps rules, et-who --check); the one ops node (exactly /dev/et0_ops); the start config read (ET_DEVICES=0; TDP 0 W / 65 C / 600 MHz); the runner's deadline (first command + cap - 120 s); the smoke (run_x04.py --smoke --blocks S,D,W,T,C) and the kit's smoke gate; the main run (run_x04.py --blocks $([ "$SIT" = A ] && echo S,D,W,T || echo C)); a crash of it (a non-zero exit, no stop recorded) written apart from a registered stop (exit 4); the closing config read; session end; the manifest last"
  s "$D/s20_wait_e193.sh" "$SIT"
  s "$D/s22_collect_e193.sh" "$SIT"
  echo; echo "################ the README in the lab's form (DATA-README-FORM-e193.md) and the data commit (commit_lab.sh, new files only): not scripted; a sitting that ended at a gate is a gate stop's record instead (docs/reports/gate-stops/, committed the same way, never reduced); then the reduction on the committed data:"
  s "$D/s24_reduce_e193.sh" "$SIT"
done
nb=$(grep -c . "$O/box-calls.txt")
echo; echo "dry listing: $n steps listed, $fails exited non-zero, $nb box calls"
[ "$fails" -eq 0 ] && [ "$nb" -eq 0 ]
