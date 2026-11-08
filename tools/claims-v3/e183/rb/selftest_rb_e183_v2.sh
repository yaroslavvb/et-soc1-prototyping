#!/usr/bin/env bash
# E183 (Q155, the kit's dated note 1): the runbook v2's desk test with a FAKE ssh and rsync, for the two steps note 1 changes: step 2 v2
# (rb/s03_desk_e183_v2.sh) and step 11 v2 (rb/s22_collect_e183_v2.sh, which runs collect_e183_v2.sh). The stand-ins, the scratch
# repository and the stand-in box are the v1 test's (rb/selftest_rb_e183.sh, which stays as committed and is not re-run here: steps 5-10
# are unchanged); everything runs in <scratch dir>, never the lab clone, and no lab box is reached. rb_run.py's own bounds hold. The cases:
#   A   the dry listing v2: every step exits 0, the look listed before the post, step 2 v2 and step 11 v2 named, no ssh or rsync call;
#   K   step 2 v2 with no window in RB_OUT refuses (10), and no call is made;
#   P1  step 2 v2 on a scratch repository holding the lab's files (with an origin, so the pull runs): 0 at the three pins (20, 46, 46);
#   P2  note 1's list one line short: step 2 v2 refuses (16, "SHA256SUMS-e183-note1(45 OK of 45; pinned 46)"); step 2 v1 passes the same
#       tree (0), since it never read that list;
#   C1  step 11 v2 on a synthetic session on the stand-in box (fake_card_e183_v2.py: the RESULT world at a quarter of sigma_q, every
#       block.json with its t0_ms after the session's T0, but T5's block left from an earlier session, its t0_ms two hours before T0), with
#       the session's T0-named files: the copies, COPY EXACT, then the REAL collector v2: the frozen inputs at their pins, the reduction v2
#       with T0 (T5's block set aside as from before the session's T0, the five others reduced), the scorer (E183-MECH RESULT, E183-HT NOT
#       SCORED), the desk-path gate and the login scrub: 0;
#   C2  step 11 v2 again into the same raw tree: refused (10);
#   C3  the collector v2 with one registration file changed in the scratch tree (plan-e183.json, one byte appended): exit 1, "not at their
#       pins", no reduced or scored file written; the file is put back after;
#   Z   no process of this test is left running.
# THE STAND-INS for P1 (note 1's list and two of its logs are written after this test's log, as in v1's P1): the scratch tree's
# SHA256SUMS-e183-note1 is a stand-in of 46 real entries (the scratch's E183 files, sorted, lists and logs left out), and a log the tree
# lacks gets one stand-in line that its grep reads.
#   bash tools/claims-v3/e183/rb/selftest_rb_e183_v2.sh <scratch dir> > <log>
# SPDX-License-Identifier: Apache-2.0
set -u
SRC=$(cd "$(dirname "${BASH_SOURCE[0]}")/../../../.." && pwd)
S=${1:?a scratch directory outside the repository}
case "$S" in "$SRC"|"$SRC"/*) echo "the scratch directory must be outside the repository"; exit 2 ;; esac
for v in RB_PROBE_S RB_READ_S RB_COPY_S RB_WAIT_S RB_LAUNCH_S RB_DESK_S E183_BUILD_S RB_DESKTEST E183_COLLECT; do
  [ -z "${!v:-}" ] || { echo "$v is set: this test runs with rb_run.py's own bounds and no desk-test override in its environment"; exit 2; }
done
for c in gdate timeout sha256sum; do command -v "$c" > /dev/null || { echo "no $c on PATH"; exit 2; }; done
mkdir -p "$S"
S=$(cd "$S" && pwd)
rm -rf "${S:?}/tree" "${S:?}/box" "${S:?}/bin" "${S:?}/boxbin" "${S:?}/origin.git" "${S:?}/out-k" "${S:?}/out-p" "${S:?}/out-c" "${S:?}/out-a"
T=$S/tree; B=$S/box; BIN=$S/bin
mkdir -p "$T/tools/claims-v3" "$T/workloads" "$B/aifoundry3/aifoundry" "$BIN" "$S/boxbin"
for p in e183 e180 e182 e178 e184 e128 e164 q141k-runbook/k6 q141k-runbook/v3.1 p8-600; do
  mkdir -p "$T/tools/claims-v3/$p"; rsync -a --exclude __pycache__ "$SRC/tools/claims-v3/$p/" "$T/tools/claims-v3/$p/"
done
cp -p "$SRC/tools/claims-v3/lib.sh" "$SRC/tools/claims-v3/dmcmd_audit.py" "$SRC/tools/claims-v3/dmcmd_table.json" "$T/tools/claims-v3/"
( cd "$SRC" && git ls-files workloads/enercat docs/reports/data/2026-11-06-e180-vector-add-aifoundry3 ) |
  while IFS= read -r f; do mkdir -p "$T/$(dirname "$f")"; cp -p "$SRC/$f" "$T/$f"; done
E3=$T/tools/claims-v3/e183
NPIN=$(sed -n 's/.*SHA256SUMS-e183-note1:\([0-9]*\)".*/\1/p' "$E3/rb/s03_desk_e183_v2.sh")
for spec in "selftest-score-e183-v2.txt SELFTEST-SCORE-E183-V2 1 of 1 PASS" "selftest-rb-e183-v2.txt SELFTEST-RB-E183-V2 0 of 0 PASS"; do
  set -- $spec; f=$1; shift
  [ -s "$E3/logs/$f" ] || printf '%s (a stand-in written by the runbook v2 desk test for its case P1)\n' "$*" > "$E3/logs/$f"
done
rm -f "$E3/SHA256SUMS-e183-note1"
( cd "$T" && find tools/claims-v3/e183 -type f ! -name 'SHA256SUMS-*' ! -path '*/logs/*' | LC_ALL=C sort | head -n "${NPIN:-1}" |
  while IFS= read -r f; do sha256sum "$f"; done ) > "$E3/SHA256SUMS-e183-note1"
G="git -C $T -c user.name=e183-desktest -c user.email=desktest@localhost -c core.hooksPath=/dev/null -c commit.gpgsign=false"
$G init -q && $G add -A && $G commit -q -m "E183 runbook v2 desk test: the lab files the steps read" || { echo "the scratch repository failed"; exit 2; }
git clone -q --bare "$T" "$S/origin.git" && $G remote add origin "$S/origin.git" && $G fetch -q origin &&
  $G branch -q -u "origin/$($G rev-parse --abbrev-ref HEAD)" || { echo "the scratch repository's origin failed"; exit 2; }
BASE0=$($G rev-list --max-parents=0 HEAD)
echo "scratch repository: $($G ls-files | wc -l | tr -d ' ') files committed, with an origin; note 1's stand-in list $(grep -c . "$E3/SHA256SUMS-e183-note1") entries (pin $NPIN)"
REAL_RSYNC=$(command -v rsync)
cat > "$BIN/ssh" <<EOF
#!/bin/bash
echo "ssh \$*" >> "$S/calls.log"
host=""; cmd=""
while [ \$# -gt 0 ]; do case "\$1" in -o) shift 2 ;; -*) shift ;; *) if [ -z "\$host" ]; then host=\$1; shift; else cmd="\$*"; break; fi ;; esac; done
case "\$host" in aifoundry3) ;; *) echo "STAND-IN SSH: refusing host \$host" >&2; exit 97 ;; esac
[ "\$cmd" = true ] && exit 0
cat | HOME="$B/\$host" PATH="$S/boxbin:\$PATH" bash -c "cd ~ && \$cmd"
EOF
cat > "$BIN/rsync" <<EOF
#!/bin/bash
echo "rsync \$*" >> "$S/calls.log"
a=()
while [ \$# -gt 0 ]; do case "\$1" in -e) shift 2 ;; *:*) h=\${1%%:*}; p=\${1#*:}; case "\$h" in aifoundry3) ;; *) echo "STAND-IN RSYNC: refusing \$h" >&2; exit 97 ;; esac; a+=("$B/\$h/\$p"); shift ;; *) a+=("\$1"); shift ;; esac; done
exec "$REAL_RSYNC" "\${a[@]}"
EOF
R=$E3/rb
BOXT=$B/aifoundry3/aifoundry
printf '#!/bin/sh\necho aifoundry3\n' > "$S/boxbin/hostname"
printf '#!/bin/sh\nexec gdate "$@"\n' > "$S/boxbin/date"
printf '#!/bin/sh\nPYTHONUSERBASE="%s" exec /usr/bin/python3 "$@"\n' "$(/usr/bin/python3 -m site --user-base)" > "$S/boxbin/python3"
printf '#!/bin/sh\necho "(desk test: no et-who here)"\n' > "$S/boxbin/et-who"
printf '#!/bin/sh\nexit 1\n' > "$S/boxbin/pgrep"
for n in ssh scp; do printf '#!/bin/sh\necho "%s $*" >> "%s"\necho "NETWORK STAND-IN: %s refused" >&2\nexit 97\n' "$n" "$S/box-network.log" "$n" > "$S/boxbin/$n"; done
chmod +x "$BIN/ssh" "$BIN/rsync" "$S/boxbin"/*
export PATH="$BIN:$PATH" RB_REPO="$T" RB_LOCK="$S/lock.txt"
: > "$S/calls.log"; : > "$RB_LOCK"; : > "$S/box-network.log"
fail=0; npass=0; ncase=0
ok() { ncase=$((ncase + 1)); if [ "$1" = "$2" ]; then npass=$((npass + 1)); echo "-> PASS ($3)"; else echo "-> FAIL ($3: got $1, want $2)"; fail=1; fi; }
step() { echo; echo "== $*"; }
san() { sed -e "s#$S#<scratch>#g"; }
has() { grep -aq -- "$1" "$2" && echo 1 || echo 0; }
leftovers() { pgrep -f "$S/(tree|box)/" 2>/dev/null | grep -c .; }
cd "$T" || exit 2

step "A. the dry listing v2: every step exits 0, the look before the post, steps 2 v2 and 11 v2 named, no ssh or rsync call"
: > "$S/calls.log"
bash "$R/list_steps_e183_v2.sh" "$S/out-a" > "$S/dry-listing.txt" 2>&1; rc=$?
n=$(grep -c . "$S/calls.log"); tail -n 1 "$S/dry-listing.txt"
lp=$(awk '/s05_look_k6.sh aifoundry3$/ {l=NR} /the day.s one post, made AFTER the look/ {p=NR} END {print (l > 0 && p > l) ? 1 : 0}' "$S/dry-listing.txt")
v2=$(( $(has 's03_desk_e183_v2.sh' "$S/dry-listing.txt") + $(has 's22_collect_e183_v2.sh' "$S/dry-listing.txt") ))
ok "$rc.$n.$lp.$v2" "0.0.1.2" "A the dry listing v2: 0 steps failing, no call, the look listed before the post, step 2 v2 and step 11 v2 listed"

step "K. step 2 v2 with no window in RB_OUT (step 1 not run)"
: > "$S/calls.log"
RB_OUT="$S/out-k" bash "$R/s03_desk_e183_v2.sh" > "$S/k.txt" 2>&1; rc=$?
grep -m1 -i 'no window' "$S/k.txt" | cut -c1-200; n=$(grep -c . "$S/calls.log")
ok "$rc.$n" "10.0" "K step 2 v2 refuses without step 1's window"

step "P1. step 2 v2 on the scratch repository (the lab's files, an origin, note 1's stand-in list at its pin)"
mkdir -p "$S/out-p"; RB_OUT="$S/out-p" bash "$R/s02_window_e183.sh" "$(gdate +%F)" 00:00 23:59 > /dev/null 2>&1
RB_OUT="$S/out-p" RB_E183_BASE=$BASE0 bash "$R/s03_desk_e183_v2.sh" > "$S/p1.txt" 2>&1; rc=$?
grep -E 'desk check v2:|STOP' "$S/p1.txt" | cut -c1-330
ok "$rc.$(has 'the three hash lists at their pinned counts (20, 46 and 46)' "$S/p1.txt")" "0.1" "P1 step 2 v2 passes the intact tree at its three pins"

step "P2. note 1's list one line short: step 2 v2 refuses, step 2 v1 passes the same tree"
cp -p "$E3/SHA256SUMS-e183-note1" "$S/note1-full.txt"
sed -i '' '$d' "$E3/SHA256SUMS-e183-note1"
$G commit -q -am "P2: note 1's list one line short" && $G push -q origin HEAD 2>/dev/null
RB_OUT="$S/out-p" RB_E183_BASE=$BASE0 bash "$R/s03_desk_e183_v2.sh" > "$S/p2.txt" 2>&1; r2=$?
grep -m1 'STOP' "$S/p2.txt" | cut -c1-260
q=$(has "SHA256SUMS-e183-note1($((NPIN - 1)) OK of $((NPIN - 1)); pinned $NPIN)" "$S/p2.txt")
RB_OUT="$S/out-p" RB_E183_BASE=$BASE0 bash "$R/s03_desk_e183.sh" > "$S/p2-v1.txt" 2>&1; r1=$?
grep -m1 -E 'desk check:|STOP' "$S/p2-v1.txt" | cut -c1-200
cp -p "$S/note1-full.txt" "$E3/SHA256SUMS-e183-note1"
$G commit -q -am "P2: note 1's list restored" && $G push -q origin HEAD 2>/dev/null
ok "$r2.$q.$r1" "16.1.0" "P2 the note-1 list one line short: refused by step 2 v2 (16, its count named), passed by step 2 v1 (0)"

step "C1. step 11 v2 on a synthetic session on the stand-in box: COPY EXACT, then the real collector v2 (the pins, the reduction v2 with T0, the scorer)"
export RB_OUT="$S/out-c"; mkdir -p "$RB_OUT"
bash "$R/s02_window_e183.sh" "$(gdate +%F)" 00:00 23:59 > "$S/c-window.txt" 2>&1 || { echo "the window failed: $(tail -2 "$S/c-window.txt")"; fail=1; }
T0S=$(gdate +%s)
BD=$BOXT/build/claims-v3/aifoundry3
mkdir -p "$BD"
/usr/bin/python3 -B "$E3/fake_card_e183_v2.py" "$BD" --b 0.009692712164197832 --c 0 --sigma 0.015622 --seed 41 \
  --t0-ms $(( (T0S + 90) * 1000 )) --stale "T5:$(( (T0S - 7200) * 1000 ))" | san
for d in e183-smoke/p18301 e183-stoptest/p18302; do
  mkdir -p "$BD/$d"
  printf '{"status":"ok","note":"desk test","t0_ms":%s}\n' "$(( (T0S + 30) * 1000 ))" > "$BD/$d/block.json"
  printf 'desk test\n' > "$BD/$d/run.log"
done
mkdir -p "$BOXT/build/e183"
printf '%s session start (T0 %s = 00:00:00 PST), kit v1; plan FULL\n%s session end (T0 %s)\n' "$(gdate '+%F %T %Z')" "$T0S" "$(gdate '+%F %T %Z')" "$T0S" > "$BOXT/build/e183/session-t$T0S.log"
for f in session-t$T0S.out queue-t$T0S.out dmcmd-preflight-t$T0S.txt config-t$T0S-start.json config-t$T0S-end.json; do echo "desk test" > "$BOXT/build/e183/$f"; done
echo "$T0S" > "$RB_OUT/t0-e183.txt"
rm -rf "${T:?}/build/e183-raw" "${T:?}/build/e183-out"
: > "$S/calls.log"
bash "$R/s22_collect_e183_v2.sh" > "$S/c1.txt" 2>&1; r1=$?
grep -aE 'COPY EXACT|COPY NOT|frozen inputs|block 183|set aside|scored-e183.md written|STOP|collected and scored' "$S/c1.txt" | san | cut -c1-240
OUTD=$T/build/e183-out/$(gdate +%F)-e183-vector-add-r2-aifoundry3
mech=$(/usr/bin/python3 -c 'import json,sys; s=json.load(open(sys.argv[1])); print(s["rules"]["E183-MECH"]["verdict"], s["rules"]["E183-HT"]["sign"])' "$OUTD/scored-e183.json" 2>/dev/null | tr ' ' '_')
sa=$(/usr/bin/python3 -c 'import json,sys; r=json.load(open(sys.argv[1])); print("before the session" in r["set_aside"].get("18315",""), len(r["blocks"]), r.get("t0"))' "$OUTD/reduced-e183.json" 2>/dev/null | tr ' ' '_')
ok "$r1.$(has 'COPY EXACT' "$S/c1.txt").$(has 'the frozen inputs at their pins' "$S/c1.txt").$mech.$sa" "0.1.1.RESULT_NOT_SCORED.True_5_$T0S" \
  "C1 step 11 v2: COPY EXACT, the pins checked, the reduction v2 with T0 (T5's stale block set aside, five reduced), MECH RESULT, HT NOT SCORED, the desk-path gate and the scrub passed (0)"

step "C2. step 11 v2 again into the same raw tree: refused"
bash "$R/s22_collect_e183_v2.sh" > "$S/c2.txt" 2>&1; r2=$?
grep -m1 'already exists' "$S/c2.txt" | san | cut -c1-200
ok "$r2" "10" "C2 the same step again into the same raw tree refused (10)"

step "C3. the collector v2 with a registration file changed: nothing reduced or scored"
cp -p "$E3/plan-e183.json" "$S/plan-keep.json"
printf ' ' >> "$E3/plan-e183.json"
rm -rf "${T:?}/build/e183-out"
( cd "$T" && E183_DATE="$(gdate +%F)" E183_T0="$T0S" PY=/usr/bin/python3 bash tools/claims-v3/e183/collect_e183_v2.sh build/e183-raw ) > "$S/c3.txt" 2>&1; r3=$?
cp -p "$S/plan-keep.json" "$E3/plan-e183.json"
head -n 2 "$S/c3.txt" | cut -c1-240
nf=$(find "$T/build" -name 'reduced-e183.json' -newer "$S/plan-keep.json" 2>/dev/null | grep -c .)
ok "$r3.$(has 'not at their pins: SHA256SUMS-e183-registration(19 OK of 20; pinned 20)' "$S/c3.txt").$nf" "1.1.0" "C3 a registration file off its pin: the collector v2 stops (1) and names the list, with no reduced or scored file"

step "Z. no process of this test is left running"
sleep 1
z=$(leftovers); echo "leftovers: $z"; nw=$(grep -c . "$S/box-network.log")
ok "$z.$nw" "0.0" "Z nothing left running; the stand-in box made no network call"
echo
echo "SELFTEST-RB-E183-V2 $npass of $ncase $([ "$fail" -eq 0 ] && echo PASS || echo FAIL)"
exit "$fail"
