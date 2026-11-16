#!/usr/bin/env bash
# E197 (Q185, lane kit-e197, Sun 15 Nov 2026, before any E197 datum): the dry listing of E197's runbook on aifoundry3, BOTH SITTINGS, E193's
# form (rb/list_steps_e193.sh): every step in order with RB_DRY=1, so each prints its exact commands (every remote script in full) and
# nothing runs: no ssh, no rsync, no scp, no device, no file in the repo. Stand-ins for ssh, rsync and scp go first on PATH and each
# counts a call it should never get, so the last line says "0 box calls" only when nothing reached for a box. Each sitting lists in its
# own RB_OUT (one RB_OUT per sitting); the windows are SAMPLES. Step 4 is the k6 runbook's own, unchanged, and step 7 is k6's reads
# behind the kit's wrapper; step 0 and the post are the card lane's, named only. THE ORDER (CARD-LANE-BRIEF.md 2): 5 the sync, 6 the
# build, 8 the dry pass, then, once the rest has opened, 7 the reads (the sitting's first card command) and 9 the launch at once.
#   bash tools/claims-v3/e197/rb/list_steps_e197.sh <an empty scratch dir> [<sample day>] > listing.txt
# SPDX-License-Identifier: Apache-2.0
set -u
D=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
K6=$(cd "$D/../../q141k-runbook/k6" && pwd)
REPO=$(cd "$D/../../../.." && pwd)
O=${1:?usage: list_steps_e197.sh <an empty scratch dir> [<sample day>]}
day=${2:-2026-11-16}
mkdir -p "$O/standin" "$O/1" "$O/2" || exit 10
O=$(cd "$O" && pwd)
for c in ssh rsync scp; do printf '#!/bin/sh\necho "%s $*" >> "%s/box-calls.txt"\nexit 99\n' "$c" "$O" > "$O/standin/$c"; chmod +x "$O/standin/$c"; done
: > "$O/box-calls.txt"
export PATH="$O/standin:$PATH" RB_DRY=1 RB_LOCK="$O/lock-dry.txt"
fails=0; n=0
s() { echo; echo "################ [sitting $SIT] ${1#$REPO/} ${*:2}"; RB_OUT="$O/$SIT" bash "$1" "${@:2}" 2>&1 | sed "s#$O#<RB_OUT>#g; s#$REPO#<lab clone>#g"; r=${PIPESTATUS[0]}; echo "(exit $r)"; n=$((n + 1)); [ "$r" -eq 0 ] || fails=$((fails + 1)); }
echo "E197 runbook (aifoundry3 card 0, both sittings), dry listing (nothing below was run). Sample windows: $day, sitting 1 last start 10:30, last end 12:00; sitting 2 last start 13:30, last end 15:00 (Pacific)."
echo; echo "---- the runbook's prelude for aifoundry3: every remote script on aifoundry3 starts with these lines"
( . "$D/rb_e197.sh"; rb_prelude aifoundry3 ) | sed 's/^/    | /'
for SIT in 1 2; do
  if [ "$SIT" = 1 ]; then ls=10:30; le=12:00; else ls=13:30; le=15:00; fi
  echo; echo "======================================== SITTING $SIT (its own RB_OUT) ========================================"
  echo; echo "################ step B and step 0, by hand (the card lane's): the booking; uptime (the load rule), the go's anchor lines, GitHub main read; step H, the quiet hold"
  s "$D/s02_window_e197.sh" "$SIT" "$day" "$ls" "$le"
  s "$D/s03_desk_e197.sh"
  s "$K6/s05_look_k6.sh" aifoundry3
  echo; echo "################ the day's post, AFTER the look above reads FREE, or the owner's standing waiver of it (his words, Sun 15 Nov 2026 10:22:36 PST): not scripted"
  s "$D/s07_a3_sync_e197.sh"
  if [ "$SIT" = 1 ]; then s "$D/s08_a3_build_e197.sh" start; fi
  s "$D/s08_a3_build_e197.sh" wait
  echo; echo "################ step 6's rule: at most two starts a Pacific day (the third: NO-THIRD-BUILD, 16); a second start only when the first did not end REGFILE-BUILT; sitting 2 on the same day runs only the wait; a 14 on wait is no reading, wait again"
  s "$D/s10_a3_dry_e197.sh" start
  s "$D/s10_a3_dry_e197.sh" wait
  echo; echo "################ WAIT until the rest has opened (40 minutes after our last session's end on aifoundry3; for sitting 2, sitting 1's end): nothing is sent to the card before it; then step 7 and step 9 back to back"
  s "$D/s09_a3_reads_e197.sh" "$SIT"
  s "$D/s11_a3_session_e197.sh" "$SIT"
  echo; echo "################ inside the sitting (session_e197.sh, detached on the box): the refusals (the host's name, USER, the harness at the launch's sha256, the registration's list, the host of today's build, E128's guard, the box's sampler, dmcmd_audit GO, exactly /dev/et0_ops and /dev/et0_mgmt, ref/'s four files at the registration's sha256, the first card command today and at most 10 minutes ago, the cap before the last end); the free check (et-who --check, other users' device processes, the lock probe); CAP_S = the cap - 60 s - (now - the first card command): the runner's deadline at the first card command + the cap - 120 s; the kit's watch beside (its live stops, its smoke check, the end-stop at the cap - 30 s, the hang watch: a STOP and a report, never a kill); run_session.sh $([ "$SIT" = 1 ] && echo 'full (or short)' || echo ext) with ETTELEM = E128's guard; SESSION_DONE by the wrapper if run_session.sh exits before its own; the summary (the smoke, the blocks, the stop and whether it names the card, SITTING-RESULT, GATE-STOP); a crash written apart (exit 9); session end; the manifest last"
  s "$D/s20_wait_e197.sh" "$SIT"
  s "$D/s22_collect_e197.sh" "$SIT"
  echo; echo "################ the README in the lab's form (DATA-README-FORM-e197.md) and the data commit (commit_lab.sh, new files only): not scripted; a sitting that ended at a gate is a gate stop's record instead (docs/reports/gate-stops/, committed the same way, never reduced); then the reduction on the committed data:"
  s "$D/s24_reduce_e197.sh" "$SIT"
done
nb=$(grep -c . "$O/box-calls.txt")
echo; echo "dry listing: $n steps listed, $fails exited non-zero, $nb box calls"
[ "$fails" -eq 0 ] && [ "$nb" -eq 0 ]
