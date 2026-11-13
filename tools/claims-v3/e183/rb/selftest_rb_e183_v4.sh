#!/usr/bin/env bash
# E183 (the kit's dated note 6, KIT.md.dated-note-6.md, Fri 13 Nov 2026, before any E183 train datum): the runbook's desk test v4, for note
# 6's step 8 v3 (rb/s10_a3_dry_e183_v3.sh) and step 9 v3 (rb/s11_a3_session_e183_v3.sh), and the dry listing v7, with the stand-ins of
# rb/selftest_rb_e183_v3.sh (24b9b99e, unchanged): a FAKE ssh that runs each remote script with `bash -s` in a local directory laid out
# as aifoundry3's ~/aifoundry and refuses any other host or command, a FAKE rsync that copies host:path to that directory, a stand-in cmake
# (rb/fake_cmake_gcc_e183.sh) that builds the patched host by g++-13 at -O2 on the recording mock. It runs in a private PID namespace of its
# own (bubblewrap, re-executing itself; no /dev/et*, refused if one is visible), so k6's ours_live and jobs_live read only its own
# processes, less this test's desk-side steps (a stand-in pgrep: on the real box they run on the desk, and step 9's own name matches k6's
# session pattern). No lab box is reached. Every case of step 9 v3 but L ends at a refusal; in L (verify-n6's case, carried into this test
# before the land by the lane fix-n6: step 9 v3's launch tail was run by no committed desk test) every gate passes and step 9 v3 launches
# session v3 on the stand-in box with a USER that is not the login, so the session stops at its USER gate before any device is opened.
#   V   the dry listing v7: every step exits 0; the look before the post's line; step 5a, then step 5b, then step 5; step 6's "NOT RUN" line;
#       step 8 v3, step 9 v3, step 10 v2 and step 11 v3 in that order; no ssh or rsync call;
#   B   the stand-in box made ready as a day's box steps make it: the window, step 5 (the sync carries note 6's files), step 5a, step 6 v2
#       (TRAIN-HOST-BUILT; its wait's checks);
#   D   step 8 v3: job a3-dry-e183-v3 rc 0 (block v3's dry 18310, the smoke and the stop-path test on the GCC -O2 host; session v3's start
#       gate 8); the job a3-dry-e183 (step 8 v2's) not written;
#   G1  step 9 v3 with the first session's smoke and stop test in the data root: REFUSED (10), naming step 5b; nothing launched;
#   G2  the same after an aside, but step 8 v3's job not ended today (only step 8 v2's): REFUSED (10), "dry pass v3"; nothing launched;
#   G3  every note 6 gate passing, the build's job made yesterday's for this case: REFUSED (10) at the build's gate (so the data root and
#       the dry pass v3 passed); nothing launched;
#   G4  the rest rule kept (v2's): a session log of ours ending 10 minutes ago: REFUSED (10); nothing launched;
#   G5  (fix-n6) an operator's stop left on the box, build/e183/STOP, then build/claims-v3/STOP, every other gate passing (the rest line
#       read): REFUSED (10) naming the file; nothing launched;
#   L   (verify-n6's, carried by fix-n6) the launch path end to end, every gate passing, the launch's USER not the login: rc 0, LAUNCHED with
#       a T0, t0-e183.txt in RB_OUT; the box's session log reads "kit note 6; plan FULL", the USER gate's line ("no device opened") and
#       "session end (T0 ...)"; step 10 v2 then reads RUN-ENDED and GATE-STOPPED (16); one session log more; no device record;
#   G6  (fix-n6) step 9 v3 again from the same RB_OUT, which now holds L's T0: REFUSED (10) at the desk before any call; nothing launched;
#   Z   no process of this test left; the recording mock's device record empty.
#   bash tools/claims-v3/e183/rb/selftest_rb_e183_v4.sh <scratch dir outside the repository> > <log>
# Prints SELFTEST-RB-E183-V4 PASS or FAIL (<n> of <m>). A few minutes (one GCC -O2 build, one dry pass of block 18310's 52 processes).
# SPDX-License-Identifier: Apache-2.0
set -u
SRC=$(cd "$(dirname "${BASH_SOURCE[0]}")/../../../.." && pwd)
S=${1:?a scratch directory outside the repository}
case "$S" in "$SRC"|"$SRC"/*) echo "the scratch directory must be outside the repository"; exit 2 ;; esac
case "$S" in *session_e*|*queue_e*) echo "the scratch directory's path must not name a session or a queue"; exit 2 ;; esac
ls /dev/et* > /dev/null 2>&1 && { echo "REFUSED: a /dev/et* node is visible here: run this test only inside a no-device sandbox"; exit 2; }
if [ "${E183RB4_INNER:-}" != 1 ]; then
  [ -x /usr/bin/bwrap ] || { echo "no /usr/bin/bwrap (bubblewrap)"; exit 2; }
  mkdir -p "$S" || exit 2
  SELF=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/$(basename "${BASH_SOURCE[0]}")
  E183RB4_INNER=1 exec /usr/bin/bwrap --dev-bind / / --dev /dev --tmpfs /run/lock --unshare-pid --proc /proc --die-with-parent -- \
    /bin/bash "$SELF" "$S"
fi
for v in RB_DRY RB_PROBE_S RB_READ_S RB_COPY_S RB_WAIT_S RB_LAUNCH_S RB_DESK_S E183_BUILD_S RB_DESKTEST E183_COLLECT V3_DRY; do
  [ -z "${!v:-}" ] || { echo "$v is set: this test runs with rb_run.py's own bounds and no desk-test override in its environment"; exit 2; }
done
for c in timeout sha256sum g++-13 rsync; do command -v "$c" > /dev/null || { echo "no $c on PATH"; exit 2; }; done
S=$(cd "$S" && pwd)
ME=$(id -un)
main() {
rm -rf "${S:?}/tree" "${S:?}/box" "${S:?}/bin" "${S:?}/boxbin" "${S:?}/out-"*
T=$S/tree; B=$S/box; BIN=$S/bin
mkdir -p "$T/tools/claims-v3" "$T/workloads" "$B/aifoundry3/aifoundry" "$BIN" "$S/boxbin"
for p in e183 e180 e182 e178 e184 e185 e128 q141k-runbook/k6 q141k-runbook/v3.1 p8-600; do
  mkdir -p "$T/tools/claims-v3/$p"; rsync -a --exclude __pycache__ "$SRC/tools/claims-v3/$p/" "$T/tools/claims-v3/$p/"
done
cp -p "$SRC/tools/claims-v3/lib.sh" "$SRC/tools/claims-v3/dmcmd_audit.py" "$SRC/tools/claims-v3/dmcmd_table.json" "$T/tools/claims-v3/"
( cd "$SRC" && git ls-files workloads/enercat ) | while IFS= read -r f; do mkdir -p "$T/$(dirname "$f")"; cp -p "$SRC/$f" "$T/$f"; done
G="git -C $T -c user.name=e183-desktest -c user.email=desktest@localhost -c core.hooksPath=/dev/null -c commit.gpgsign=false"
$G init -q && $G add -A && $G commit -q -m "E183 runbook desk test v4: the lab files the steps read" || { echo "the scratch repository failed"; return 2; }
echo "scratch repository: $($G ls-files | wc -l | tr -d ' ') files committed"
REAL_RSYNC=$(command -v rsync)
cat > "$BIN/ssh" <<EOF
#!/bin/bash
echo "ssh \$*" >> "$S/calls.log"
host=""; cmd=""
while [ \$# -gt 0 ]; do case "\$1" in -o) shift 2 ;; -*) shift ;; *) if [ -z "\$host" ]; then host=\$1; shift; else cmd="\$*"; break; fi ;; esac; done
[ "\$host" = aifoundry3 ] || { echo "STAND-IN SSH: refusing host \$host" >&2; exit 97; }
[ "\$cmd" = true ] && exit 0
[ "\$cmd" = "bash -s" ] || { echo "STAND-IN SSH: refusing the command \$cmd" >&2; exit 97; }
cd "$B/\$host" && HOME="$B/\$host" PATH="$S/boxbin:\$PATH" exec bash -s
EOF
cat > "$BIN/rsync" <<EOF
#!/bin/bash
echo "rsync \$*" >> "$S/calls.log"
a=()
while [ \$# -gt 0 ]; do case "\$1" in -e) shift 2 ;; *:*) h=\${1%%:*}; p=\${1#*:}; case "\$h" in aifoundry3) ;; *) echo "STAND-IN RSYNC: refusing \$h" >&2; exit 97 ;; esac; a+=("$B/\$h/\$p"); shift ;; *) a+=("\$1"); shift ;; esac; done
exec "$REAL_RSYNC" "\${a[@]}"
EOF
command -v gdate > /dev/null || printf '#!/bin/sh\nexec date "$@"\n' > "$BIN/gdate"
printf '#!/bin/sh\necho aifoundry3\n' > "$S/boxbin/hostname"
printf '#!/bin/sh\nexec /usr/bin/python3 "$@"\n' > "$S/boxbin/python3"
printf '#!/bin/sh\necho "No process holds an ET-SoC-1 device node or card lock. (desk stand-in)"\n' > "$S/boxbin/et-who"
cat > "$S/boxbin/pgrep" <<'PGREP_EOF'
#!/bin/bash
# desk stand-in: the box's own pgrep, less this test's desk-side runbook steps (on the real box they run on the desk, never there: step 9's
# own name, s11_a3_session_e183_v3.sh, matches k6's session pattern)
n=0
for p in $(/usr/bin/pgrep "$@"); do
  case "$(tr '\0' ' ' < "/proc/$p/cmdline" 2> /dev/null)" in *"/claims-v3/e183/rb/s"[0-9]*) continue ;; esac
  echo "$p"; n=$((n + 1))
done
[ "$n" -gt 0 ]
PGREP_EOF
for n in ssh scp; do printf '#!/bin/sh\necho "%s $*" >> "%s"\necho "NETWORK STAND-IN: %s refused" >&2\nexit 97\n' "$n" "$S/box-network.log" "$n" > "$S/boxbin/$n"; done
cp -p "$SRC/tools/claims-v3/e183/rb/fake_cmake_gcc_e183.sh" "$S/boxbin/cmake"
chmod +x "$BIN"/* "$S/boxbin"/*
R=$T/tools/claims-v3/e183/rb
BOXT=$B/aifoundry3/aifoundry
J=$BOXT/build/q141k/jobs
export PATH="$BIN:$PATH" RB_REPO="$T" RB_LOCK="$S/lock.txt" RB_WAIT_LOOP_S=20 E183_DEVICE_RECORD="$S/box-device-record.txt" USER="$ME" \
  FAKE_CMAKE_STUBS="$T/tools/claims-v3/e184/desk/stubs" FAKE_CMAKE_MOCK="$T/tools/claims-v3/e183/desk/mock_runtime_e183_v2.cpp" FAKE_CMAKE_CXX=g++-13
: > "$S/calls.log"; : > "$RB_LOCK"; : > "$S/box-network.log"; rm -f "$E183_DEVICE_RECORD"
fail=0; npass=0; ncase=0
ok() { ncase=$((ncase + 1)); if [ "$1" = "$2" ]; then npass=$((npass + 1)); echo "-> PASS ($3)"; else echo "-> FAIL ($3: got $1, want $2)"; fail=1; fi; }
step() { echo; echo "== $*"; }
has() { grep -aq -- "$1" "$2" && echo 1 || echo 0; }
nrec() { if [ -f "$E183_DEVICE_RECORD" ]; then grep -c . "$E183_DEVICE_RECORD"; else echo 0; fi; }
TODAY=$(TZ=America/Los_Angeles date +%F)
waitj() {  # waitj <step file> <out>: a step's wait, again while it says 17; its last exit status
  local f=$1 o=$2 k r
  : > "$o"
  for k in 1 2 3 4 5 6 7 8 9 10 11 12; do bash "$f" wait >> "$o" 2>&1; r=$?; [ "$r" -eq 17 ] || break; done
  echo "$r"
}
launched() { ls "$BOXT"/build/e183/session-t*.log 2> /dev/null | grep -c .; }
cd "$T" || return 2

step "V. the dry listing v7: every step exits 0, in note 6's order; no ssh or rsync call"
: > "$S/calls.log"
bash "$R/list_steps_e183_v7.sh" "$S/out-v" > "$S/dry-listing-v7.txt" 2>&1; rc=$?
tail -n 1 "$S/dry-listing-v7.txt"
ord=$(awk '/s05_look_k6.sh aifoundry3$/ {l=NR} /the day.s one post: WAIVED/ {p=NR} /s06_a3_records_e183.sh $/ {a=NR} /s06b_a3_aside_e183.sh / {b=NR}
  /s07_a3_sync_e183.sh $/ {y=NR} /box step 6, the build: NOT RUN/ {x=NR} /s10_a3_dry_e183_v3.sh start$/ {d=NR} /s11_a3_session_e183_v3.sh FULL$/ {s=NR}
  /s20_wait_e183_v2.sh $/ {w=NR} /s22_collect_e183_v3.sh $/ {c=NR}
  END {print (l > 0 && p > l && a > p && b > a && y > b && x > y && d > x && s > d && w > s && c > w) ? 1 : 0}' "$S/dry-listing-v7.txt")
ok "$rc.$(grep -c . "$S/calls.log").$ord" "0.0.1" "V the dry listing v7: 0 failing, no call; the look, the post's line, 5a, 5b, 5, step 6 not run, 8 v3, 9 v3, 10 v2, 11 v3"

export RB_OUT="$S/out-b"; mkdir -p "$RB_OUT"
step "B. the stand-in box made ready: the window, step 5 (the sync), step 5a, step 6 v2"
bash "$R/s02_window_e183.sh" "$TODAY" "$(date -d '+30 min' +%H:%M)" 23:59 > "$S/b-window.txt" 2>&1; r0=$?
bash "$R/s07_a3_sync_e183.sh" > "$S/b-sync.txt" 2>&1; rs=$?
n6=0; for f in block_e183_v3.sh queue_e183_v3.sh session_e183_v3.sh preflight_e183_v3.sh harness_e183_v3.py harness-e183-v3.json rb/s10_a3_dry_e183_v3.sh; do
  cmp -s "$T/tools/claims-v3/e183/$f" "$BOXT/tools/claims-v3/e183/$f" && n6=$((n6 + 1)); done
mkdir -p "$BOXT/build/ettelem"
printf '#!/bin/sh\necho "STUB EXECUTED: ettelem $*" >&2\nexit 97\n' > "$BOXT/build/ettelem/ettelem"; chmod +x "$BOXT/build/ettelem/ettelem"
bash "$R/s06_a3_records_e183.sh" > "$S/b-records.txt" 2>&1; rr=$?
bash "$R/s08_a3_build_e183_v2.sh" start > "$S/b-start.txt" 2>&1; ra=$?
rw=$(waitj "$R/s08_a3_build_e183_v2.sh" "$S/b-wait.txt")
grep -aE '^TRAIN-HOST-BUILT|^HARNESS OK|^preflight_e183_v2 rc|STOP' "$S/b-wait.txt" | sort -u | sed "s#$S#<scratch>#g" | cut -c1-200
ok "$r0.$rs.$n6.$rr.$ra.$rw.$(has '^TRAIN-HOST-BUILT rc=0' "$J/a3-build-e183.out")" "0.0.7.0.0.0.1" "B the sync carries note 6's files; step 5a; step 6 v2 builds the host"

step "D. step 8 v3 (the dry pass of note 6's files) on that box"
: > "$S/box-network.log"
bash "$R/s10_a3_dry_e183_v3.sh" start > "$S/d-start.txt" 2>&1; r1=$?
r2=$(waitj "$R/s10_a3_dry_e183_v3.sh" "$S/d-wait.txt")
grep -aE '^E183 dry|^E183 start gate' "$S/d-wait.txt" | sort -u | cut -c1-200
k1=$(has '^E183 dry 18310 rc=0' "$S/d-wait.txt"); k2=$(has '^E183 dry 18301 --smoke rc=0' "$S/d-wait.txt"); k3=$(has '^E183 dry 18302 --stoptest rc=0' "$S/d-wait.txt")
k4=$(has '^E183 start gate rc=8' "$S/d-wait.txt"); kv=$([ -e "$J/a3-dry-e183-v3.rc" ] && [ ! -e "$J/a3-dry-e183.rc" ] && echo 1 || echo 0)
ok "$r1.$r2.$k1.$k2.$k3.$k4.$kv.$(grep -c . "$S/box-network.log").$(nrec)" "0.0.1.1.1.1.1.0.0" "D job a3-dry-e183-v3 rc 0 (18310, the smoke, the stop test, the start gate 8); no a3-dry-e183; no network; no device record"

DRR=$BOXT/build/claims-v3/aifoundry3
step "G1. step 9 v3 with the first session's smoke and stop test in the data root"
mkdir -p "$DRR/e183-smoke/p18301" "$DRR/e183-stoptest/p18302"
echo '{"status":"fail","note":"desk stand-in of the first smoke"}' > "$DRR/e183-smoke/p18301/block.json"
echo '{"status":"ok","note":"desk stand-in of the first stop test"}' > "$DRR/e183-stoptest/p18302/block.json"
bash "$R/s11_a3_session_e183_v3.sh" FULL > "$S/g1.txt" 2>&1; rc=$?
grep -m1 -E 'REFUSED|STOP' "$S/g1.txt" | cut -c1-220
ok "$rc.$(has 'move them aside first (step 5b' "$S/g1.txt").$(launched)" "10.1.0" "G1 refused while the data root holds the first session's directories; nothing launched"
step "G2. after an aside, but step 8 v3's job not ended today (step 8 v2's job only)"
A=$DRR/e183-aside-$TODAY-t1794604458
mkdir -p "$A/e183-smoke" "$A/e183-stoptest" && mv -T "$DRR/e183-smoke/p18301" "$A/e183-smoke/p18301" && mv -T "$DRR/e183-stoptest/p18302" "$A/e183-stoptest/p18302"
cp -p "$J/a3-dry-e183-v3.rc" "$J/a3-dry-e183.rc"; touch -d '-2 day' "$J/a3-dry-e183-v3.rc"
bash "$R/s11_a3_session_e183_v3.sh" FULL > "$S/g2.txt" 2>&1; rc=$?
grep -m1 -E 'REFUSED|STOP' "$S/g2.txt" | cut -c1-220
ok "$rc.$(has 'dry pass v3' "$S/g2.txt").$(launched)" "10.1.0" "G2 refused without today's dry pass v3 (v2's does not count); nothing launched"
step "G3. every note 6 gate passing; the build's job made yesterday's for this case"
touch "$J/a3-dry-e183-v3.rc"; rm -f "$J/a3-dry-e183.rc"; touch -d '-2 day' "$J/a3-build-e183.rc"
bash "$R/s11_a3_session_e183_v3.sh" FULL > "$S/g3.txt" 2>&1; rc=$?
grep -m1 -E 'REFUSED|STOP' "$S/g3.txt" | cut -c1-220
ok "$rc.$(has 'was not built today' "$S/g3.txt").$(has 'earlier entr' "$S/g3.txt").$(launched)" "10.1.0.0" "G3 the data root and the dry pass v3 pass; refused at the build's gate; nothing launched"
step "G4. the rest rule kept: a session log of ours ending 10 minutes ago"
touch "$J/a3-build-e183.rc"
mkdir -p "$BOXT/build/e185/T1794600000"
printf '%s session start (desk stand-in)\n%s session end\n' "$(date -d '-40 min' '+%F %T %Z')" "$(date -d '-10 min' '+%F %T %Z')" > "$BOXT/build/e185/T1794600000/session.log"
bash "$R/s11_a3_session_e183_v3.sh" FULL > "$S/g4.txt" 2>&1; rc=$?
grep -m1 -E 'REFUSED|STOP' "$S/g4.txt" | cut -c1-220
ok "$rc.$(has "REFUSED: 10 minutes since E185's session end" "$S/g4.txt").$(launched)" "10.1.0" "G4 refused under 40 minutes; nothing launched"
step "G5 (fix-n6). an operator's stop left on the box: build/e183/STOP, then build/claims-v3/STOP; every other gate passing"
printf '%s session start (desk stand-in)\n%s session end\n' "$(date -d '-90 min' '+%F %T %Z')" "$(date -d '-50 min' '+%F %T %Z')" > "$BOXT/build/e185/T1794600000/session.log"
mkdir -p "$BOXT/build/e183" "$BOXT/build/claims-v3"
: > "$BOXT/build/e183/STOP"
bash "$R/s11_a3_session_e183_v3.sh" FULL > "$S/g5a.txt" 2>&1; ra=$?
grep -m1 -E 'REFUSED|STOP:' "$S/g5a.txt" | cut -c1-220
rm -f "${BOXT:?}/build/e183/STOP"
: > "$BOXT/build/claims-v3/STOP"
bash "$R/s11_a3_session_e183_v3.sh" FULL > "$S/g5b.txt" 2>&1; rb=$?
grep -m1 -E 'REFUSED|STOP:' "$S/g5b.txt" | cut -c1-220
rm -f "${BOXT:?}/build/claims-v3/STOP"
ok "$ra.$(has 'rest: [0-9]* minutes since' "$S/g5a.txt").$(has 'REFUSED: build/e183/STOP exists on the box' "$S/g5a.txt").$rb.$(has 'REFUSED: build/claims-v3/STOP exists on the box' "$S/g5b.txt").$(launched)" "10.1.1.10.1.0" "G5 refused while either operator's stop exists (the rest rule read and passed first); nothing launched"
step "L (verify-n6's case, carried by fix-n6). step 9 v3's launch path end to end, every gate passing; the launch's USER is not the login, so session v3 stops at its USER gate before any device; then step 10 v2"
n0=$(launched)
USER=desk-not-the-login bash "$R/s11_a3_session_e183_v3.sh" FULL > "$S/l1.txt" 2>&1; rc=$?
grep -aE 'LAUNCHED|REFUSED|STOP|rest:|launched' "$S/l1.txt" | cut -c1-220
t0=$(cat "$RB_OUT/t0-e183.txt" 2> /dev/null)
LG=$BOXT/build/e183/session-t$t0.log
echo "-- the stand-in box's session log for T0 $t0:"; cut -d' ' -f4- "$LG" 2> /dev/null | cut -c1-220
USER=desk-not-the-login bash "$R/s20_wait_e183_v2.sh" > "$S/l2.txt" 2>&1; rw=$?
grep -aE 'RUN-|GATE-|STOP|no device' "$S/l2.txt" | cut -c1-220
ok "$rc.$(has 'LAUNCHED e183 T0=' "$S/l1.txt").$(has "LAUNCHED e183 T0=$t0 " "$S/l1.txt").$(has 'kit note 6; plan FULL' "$LG").$(has "USER is 'desk-not-the-login', not this login" "$LG").$(has "session end (T0 $t0)" "$LG").$rw.$(has '^RUN-ENDED e183' "$S/l2.txt").$(has '^GATE-STOPPED e183' "$S/l2.txt").$(( $(launched) - n0 )).$(nrec)" \
  "0.1.1.1.1.1.16.1.1.1.0" "L step 9 v3 launches session v3 (LAUNCHED, its T0 in RB_OUT), the session stops at its USER gate (no device), step 10 v2 reads RUN-ENDED and GATE-STOPPED (16)"
step "G6 (fix-n6). step 9 v3 again from the same RB_OUT, which now holds L's T0: one RB_OUT, one session"
c1=$(grep -c . "$S/calls.log"); n1=$(launched)
bash "$R/s11_a3_session_e183_v3.sh" FULL > "$S/g6.txt" 2>&1; rc=$?
grep -m1 -E 'STOP' "$S/g6.txt" | cut -c1-220
ok "$rc.$(has "this RB_OUT already holds a session's T0 (t0-e183.txt: $t0)" "$S/g6.txt").$(( $(grep -c . "$S/calls.log") - c1 )).$(( $(launched) - n1 ))" "10.1.0.0" "G6 refused at the desk before any call; nothing launched"
step "Z. no process of this test left; no network call from the box; the device record"
left=$(pgrep -c -f 'session_e18|queue_e18|block_e18|run_e18|ettelem|enercat_host')
echo "processes left: $left; box network calls: $(grep -c . "$S/box-network.log"); device record lines: $(nrec)"
ok "$left.$(grep -c . "$S/box-network.log").$(nrec)" "0.0.0" "Z"
echo
echo "SELFTEST-RB-E183-V4 $([ "$fail" -eq 0 ] && echo PASS || echo FAIL) ($npass of $ncase): step 8 v3 and step 9 v3 on a stand-in aifoundry3, its launch path included, and the dry listing v7"
return "$fail"
}
main 2>&1 | sed "s#$S#<scratch>#g; s#$SRC#<repo>#g; s#$HOME#<home>#g; s#\\b$ME\\b#<login>#g"
exit "${PIPESTATUS[0]}"
