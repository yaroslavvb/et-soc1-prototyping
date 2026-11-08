#!/usr/bin/env bash
# E183 (Q155, the kit): the runbook's desk test with a FAKE ssh and rsync (E182's rb/selftest_rb_e182_v4.sh, ported). Stand-in ssh and rsync
# sit first on PATH and serve a stand-in box (a local directory laid out like aifoundry3's ~/aifoundry); they refuse any other host, and no
# lab box is reached. Everything runs in <scratch dir> (never the lab clone). rb_run.py's own bounds hold (60 s a read): this test sets no
# RB_<CLS>_S; it sets RB_WAIT_LOOP_S=20 so a wait on a long job says 17 and is called again, as on the card day. The cases:
#   A   the dry listing: every step exits 0, the look listed before the post, and the stand-ins see no ssh or rsync call;
#   K   step 2 with no window in RB_OUT refuses (10), and no call is made;
#   P1  step 2 on a scratch repository that holds the lab's files (with an origin, so the pull runs): 0 at the pins (20 and the kit's);
#   S1  step 5 on a clean stand-in box, then step 6 start and wait with the fast stand-in cmake (the patched host compiled against the mock
#       runtime): 0; the four checks each in its own 60 s read; one build counted, its "ended" line and its own log kept on the box;
#   S2  step 8 on the box step 6 left: job a3-dry-e183 ends rc 0 (block 18310, the smoke, the stop test, the start gate 8);
#   X3  a second start after that good build: refused (10), no job, the host unchanged, the count unchanged; wait reads the checks again (0);
#   X2  a build input off its pin on the box: step 6's read before the build says TRAIN-HOST-INPUTS-DIFFER (16) with step 5's words, no job,
#       no build counted; then step 5 sends it back and step 6 builds (0);
#   V   the 90 s stand-in cmake: one job (a second start refused while it runs, 10), waits that say 17, then the checks: 0; no call past a bound;
#   O   a card session of ours on the box (the stand-in pgrep reports one): start refused (10), and wait's first check refused (10);
#   R1-R3  the re-run rule (the stand-in build fails): one re-run asked for (16); the second names the fallback, SKIP (16); a third start is
#       refused (16) with the same words;
#   T   the build past its own bound (E183_BUILD_S=5 with RB_DESKTEST=1, the 90 s cmake): TRAIN-HOST-BUILD-OVERRAN, one re-run (16);
#       E183_BUILD_S without RB_DESKTEST refused (10, no call);
#   W   (N1, critic-q154's nit 2) a wait call that fails before it reads the job (the network cut on the wait's call): 14, "no reading of
#       the build job: run this step's wait again", never a failed build; the next wait reads the build (0);
#   N2  (E182 note 4's fault 1, verify-q154k's) the first build fails (16, one re-run); the re-run runs; its wait call is cut: 14 "no
#       reading", the fallback NOT named; wait then reads the good build (0); a start after it is refused (10); two builds counted;
#   N6  (E182 note 4's fix 3, fix-q154k's case) the first check's read after a good build is cut: 14, "no reading of inputs" (never "a
#       dated amendment first"); wait then reads all four checks (0);
#   L   a lost job (its processes killed on the stand-in box mid-build, the 90 s cmake): JOB-LOST is still a build's failure: one re-run
#       asked for (16), one build counted;
#   C1  step 11 on a stand-in session's files (T0-named) on the box: the copies, the box's manifest against them, COPY EXACT, the collector
#       (a stand-in, RB_DESKTEST=1), the desk-path gate and the login scrub: 0; C2 step 11 again into the same raw tree: refused (10);
#       C3 a file of the copy changed afterwards: copycheck_e183.py reads COPY NOT EXACT (9);
#   Z   no process of this test is left running.
# THE NETWORK CUT (E182 note 4's desk test, rb/selftest_rb_e182_v5.sh): while <scratch>/ssh-fail-at holds k, the k-th remote script call
# from now fails as a dropped connection does (ssh's exit 255, nothing on stdout; its script is read and dropped first); the probe never
# counts.
#   bash tools/claims-v3/e183/rb/selftest_rb_e183.sh <scratch dir> > <log>
# SPDX-License-Identifier: Apache-2.0
set -u
SRC=$(cd "$(dirname "${BASH_SOURCE[0]}")/../../../.." && pwd)
S=${1:?a scratch directory outside the repository}
case "$S" in "$SRC"|"$SRC"/*) echo "the scratch directory must be outside the repository"; exit 2 ;; esac
for v in RB_PROBE_S RB_READ_S RB_COPY_S RB_WAIT_S RB_LAUNCH_S RB_DESK_S E183_BUILD_S RB_DESKTEST E183_COLLECT; do
  [ -z "${!v:-}" ] || { echo "$v is set: this test runs with rb_run.py's own bounds and no desk-test override in its environment"; exit 2; }
done
for c in gdate timeout sha256sum; do command -v "$c" > /dev/null || { echo "no $c on PATH"; exit 2; }; done
REAL_TIMEOUT=$(command -v timeout)
mkdir -p "$S"
S=$(cd "$S" && pwd)
rm -rf "${S:?}/tree" "${S:?}/box" "${S:?}/bin" "${S:?}/boxbin" "${S:?}/origin.git" "${S:?}/out-k" "${S:?}/out-p" "${S:?}/out-b" "${S:?}/out-a"
T=$S/tree; B=$S/box; BIN=$S/bin
mkdir -p "$T/tools/claims-v3" "$T/workloads" "$B/aifoundry3/aifoundry" "$BIN" "$S/boxbin"
for p in e183 e180 e182 e178 e184 e128 e164 q141k-runbook/k6 q141k-runbook/v3.1 p8-600; do
  mkdir -p "$T/tools/claims-v3/$p"; rsync -a --exclude __pycache__ "$SRC/tools/claims-v3/$p/" "$T/tools/claims-v3/$p/"
done
cp -p "$SRC/tools/claims-v3/lib.sh" "$SRC/tools/claims-v3/dmcmd_audit.py" "$SRC/tools/claims-v3/dmcmd_table.json" "$T/tools/claims-v3/"
( cd "$SRC" && git ls-files workloads/enercat docs/reports/data/2026-11-06-e180-vector-add-aifoundry3 ) |
  while IFS= read -r f; do mkdir -p "$T/$(dirname "$f")"; cp -p "$SRC/$f" "$T/$f"; done
# P1's stand-ins: the kit's list (written after this test's log) is replaced by a stand-in list of the scratch's e183 files, at the pin
# step 2 reads, and the desk tests' logs step 2 greps for by their own committed stand-in lines
KITPIN=$(sed -n 's/.*SHA256SUMS-e183-kit:\([0-9]*\)".*/\1/p' "$T/tools/claims-v3/e183/rb/s03_desk_e183.sh")
HN=$(sed -n 's/^HARNESS_N=\([0-9]*\)$/\1/p' "$T/tools/claims-v3/e183/rb/s03_desk_e183.sh")
for spec in "desktest-host-e183.txt DESKTEST-HOST-E183 PASS" "selftest-score-e183.txt SELFTEST-SCORE-E183 1 of 1 PASS" \
            "selftest-rb-e183.txt SELFTEST-RB-E183 0 of 0 PASS" "dry-intel-e183.txt DRY-INTEL-E183 PASS"; do
  set -- $spec; f=$1; shift
  [ -s "$T/tools/claims-v3/e183/logs/$f" ] || printf '%s (a stand-in written by the runbook desk test for its case P1)\n' "$*" > "$T/tools/claims-v3/e183/logs/$f"
done
rm -f "$T/tools/claims-v3/e183/SHA256SUMS-e183-kit"
( cd "$T" && find tools/claims-v3/e183 -type f ! -name 'SHA256SUMS-e183-kit' ! -path '*/logs/*' | LC_ALL=C sort | head -n "${KITPIN:-1}" |
  while IFS= read -r f; do sha256sum "$f"; done ) > "$S/kit-standin.txt"
cp "$S/kit-standin.txt" "$T/tools/claims-v3/e183/SHA256SUMS-e183-kit"
G="git -C $T -c user.name=e183-desktest -c user.email=desktest@localhost -c core.hooksPath=/dev/null -c commit.gpgsign=false"
$G init -q && $G add -A && $G commit -q -m "E183 runbook desk test: the lab files the steps read" || { echo "the scratch repository failed"; exit 2; }
git clone -q --bare "$T" "$S/origin.git" && $G remote add origin "$S/origin.git" && $G fetch -q origin &&
  $G branch -q -u "origin/$($G rev-parse --abbrev-ref HEAD)" || { echo "the scratch repository's origin failed"; exit 2; }
BASE0=$($G rev-list --max-parents=0 HEAD)
echo "scratch repository: $($G ls-files | wc -l | tr -d ' ') files committed, with an origin; the kit's pin $KITPIN, the harness's $HN"
REAL_RSYNC=$(command -v rsync)
cat > "$BIN/ssh" <<EOF
#!/bin/bash
echo "ssh \$*" >> "$S/calls.log"
host=""; cmd=""
while [ \$# -gt 0 ]; do case "\$1" in -o) shift 2 ;; -*) shift ;; *) if [ -z "\$host" ]; then host=\$1; shift; else cmd="\$*"; break; fi ;; esac; done
case "\$host" in aifoundry3) ;; *) echo "STAND-IN SSH: refusing host \$host" >&2; exit 97 ;; esac
[ "\$cmd" = true ] && exit 0
if [ -s "$S/ssh-fail-at" ]; then k=\$(cat "$S/ssh-fail-at"); if [ "\$k" -le 1 ]; then rm -f "$S/ssh-fail-at"; cat > /dev/null; echo "ssh: connection to \$host closed (desk-test stand-in)" >&2; exit 255; fi; echo \$((k - 1)) > "$S/ssh-fail-at"; fi
cat | HOME="$B/\$host" PATH="$S/boxbin:\$PATH" bash -c "cd ~ && \$cmd"
EOF
cat > "$BIN/rsync" <<EOF
#!/bin/bash
echo "rsync \$*" >> "$S/calls.log"
a=()
while [ \$# -gt 0 ]; do case "\$1" in -e) shift 2 ;; *:*) h=\${1%%:*}; p=\${1#*:}; case "\$h" in aifoundry3) ;; *) echo "STAND-IN RSYNC: refusing \$h" >&2; exit 97 ;; esac; a+=("$B/\$h/\$p"); shift ;; *) a+=("\$1"); shift ;; esac; done
exec "$REAL_RSYNC" "\${a[@]}"
EOF
R=$T/tools/claims-v3/e183/rb
BOXT=$B/aifoundry3/aifoundry
J=$BOXT/build/q141k/jobs
printf '#!/bin/sh\necho aifoundry3\n' > "$S/boxbin/hostname"
printf '#!/bin/sh\nexec gdate "$@"\n' > "$S/boxbin/date"
# the stand-in ssh sets HOME to the stand-in box, so the box's python3 keeps the Intel's own user site (numpy, which the block's preflight
# asks for, as aifoundry3's python3 has it): its user base is read here, before any HOME changes
printf '#!/bin/sh\nPYTHONUSERBASE="%s" exec /usr/bin/python3 "$@"\n' "$(/usr/bin/python3 -m site --user-base)" > "$S/boxbin/python3"
printf '#!/bin/sh\necho "(desk test: no et-who here)"\n' > "$S/boxbin/et-who"
printf '#!/bin/sh\n[ -e "%s" ] && { echo 4242; exit 0; }\nexit 1\n' "$S/ours-live.flag" > "$S/boxbin/pgrep"
printf '#!/bin/sh\nexec "$@"\n' > "$S/boxbin/setsid"
for n in ssh scp; do printf '#!/bin/sh\necho "%s $*" >> "%s"\necho "NETWORK STAND-IN: %s refused" >&2\nexit 97\n' "$n" "$S/box-network.log" "$n" > "$S/boxbin/$n"; done
cp -p "$SRC/tools/claims-v3/e183/rb/fake_cmake_slow_e183.sh" "$S/boxbin/cmake"
cp -p "$SRC/tools/claims-v3/e183/rb/fake_cmake_e183.sh" "$S/boxbin/fake_cmake_e183.sh"
chmod +x "$BIN/ssh" "$BIN/rsync" "$S/boxbin"/*
export PATH="$BIN:$PATH" RB_REPO="$T" RB_LOCK="$S/lock.txt" RB_WAIT_LOOP_S=20 FAKE_CMAKE_SLEEP_S=0 \
  FAKE_CMAKE_STUBS="$T/tools/claims-v3/e184/desk/stubs" FAKE_CMAKE_MOCK="$T/tools/claims-v3/e183/desk/mock_runtime_e183.cpp"
: > "$S/calls.log"; : > "$RB_LOCK"; : > "$S/box-network.log"; rm -f "$S/ours-live.flag" "$S/ssh-fail-at"
fail=0; npass=0; ncase=0
ok() { ncase=$((ncase + 1)); if [ "$1" = "$2" ]; then npass=$((npass + 1)); echo "-> PASS ($3)"; else echo "-> FAIL ($3: got $1, want $2)"; fail=1; fi; }
step() { echo; echo "== $*"; }
san() { sed -e "s#$S#<scratch>#g"; }
nlog() { if [ -f "$RB_OUT/runbook.log" ]; then grep -c . "$RB_OUT/runbook.log"; else echo 0; fi; }
since() { tail -n +"$(( $1 + 1 ))" "$RB_OUT/runbook.log" 2>/dev/null; }
TODAY=$(TZ=America/Los_Angeles gdate +%F)
AT=$BOXT/build/e183-build-attempts.txt
builds() { if [ -f "$AT" ]; then echo $(( $(grep -c "^$TODAY .* a3-build-e183 started\$" "$AT") - $(grep -c "^$TODAY .* a3-build-e183 ended rc=[0-9]*: TRAIN-HOST-INPUTS-DIFFER" "$AT") )); else echo 0; fi; }
fresh_day() {  # as on a new day: no count file, no build logs, the last job's status from an earlier day
  rm -f "$AT"; rm -rf "${BOXT:?}/build/e183-build-logs"
  for x in rc out sh; do [ -e "$J/a3-build-e183.$x" ] && touch -t "$(gdate -d '-2 day' +%Y%m%d%H%M)" "$J/a3-build-e183.$x"; done
  return 0
}
hostsha() { if [ -f "$BOXT/build/enercat-e183/host/enercat_host" ]; then sha256sum "$BOXT/build/enercat-e183/host/enercat_host" | cut -c1-16; else echo none; fi; }
leftovers() { pgrep -f "$S/boxbin/cmake|bash build/q141k/jobs/a3-build-e183[.]sh|tools/claims-v3/e183/build_host_e183[.]sh" 2>/dev/null | grep -c .; }
b6() { bash "$R/s08_a3_build_e183.sh" "$@"; }
waitb() {  # waitb <out> [<max calls>]: step 6's wait, again while it says 17; prints "<rc> <number of 17s>"
  local o=$1 m=${2:-12} k r n17=0
  : > "$o"
  for k in $(seq 1 "$m"); do b6 wait >> "$o" 2>&1; r=$?; [ "$r" -eq 17 ] || break; n17=$((n17 + 1)); done
  echo "$r $n17"
}
wait10() { local o=$1 k r; for k in 1 2 3 4 5 6 7 8 9 10; do bash "$R/s10_a3_dry_e183.sh" wait > "$o" 2>&1; r=$?; [ "$r" -eq 17 ] || break; done; return "$r"; }
has() { grep -aq -- "$1" "$2" && echo 1 || echo 0; }
netcut() { echo "${1:-1}" > "$S/ssh-fail-at"; }   # the ${1:-1}-th remote script call from now is cut (exit 255, no output)
killtree() {  # freeze the parent first (so the job never writes its exit status), then its children, then kill them all (E182 v5's)
  local p=$1 c kids; kids=$(pgrep -P "$p" 2>/dev/null); kill -STOP "$p" 2>/dev/null
  for c in $kids; do killtree "$c"; done; kill -KILL "$p" 2>/dev/null
}
cd "$T" || exit 2

step "A. the dry listing: every step exits 0, the look before the post, no ssh or rsync call"
: > "$S/calls.log"
bash "$R/list_steps_e183.sh" "$S/out-a" > "$S/dry-listing.txt" 2>&1; rc=$?
n=$(grep -c . "$S/calls.log"); tail -n 1 "$S/dry-listing.txt"
lp=$(awk '/s05_look_k6.sh aifoundry3$/ {l=NR} /the day.s one post, made AFTER the look/ {p=NR} END {print (l > 0 && p > l) ? 1 : 0}' "$S/dry-listing.txt")
ok "$rc.$n.$lp" "0.0.1" "A the dry listing: 0 steps failing, no call, the look listed before the post"

step "K. step 2 with no window in RB_OUT (step 1 not run)"
: > "$S/calls.log"
RB_OUT="$S/out-k" bash "$R/s03_desk_e183.sh" > "$S/k.txt" 2>&1; rc=$?
grep -m1 -i 'no window' "$S/k.txt" | cut -c1-200; n=$(grep -c . "$S/calls.log")
ok "$rc.$n" "10.0" "K step 2 refuses without step 1's window"

step "P1. step 2 on the scratch repository (the lab's files, an origin, the stand-in kit list at its pin)"
mkdir -p "$S/out-p"; RB_OUT="$S/out-p" bash "$R/s02_window_e183.sh" "$(gdate +%F)" 23:00 23:30 > /dev/null 2>&1
RB_OUT="$S/out-p" RB_E183_BASE=$BASE0 bash "$R/s03_desk_e183.sh" > "$S/p1.txt" 2>&1; rc=$?
grep -E 'desk check:|STOP' "$S/p1.txt" | cut -c1-330
ok "$rc" "0" "P1 step 2 passes the intact tree at its pins"

export RB_OUT="$S/out-b"; mkdir -p "$RB_OUT"
ls_=$(gdate -d '+5 min' +%H:%M); le_=23:59      # a window inside today's calendar day (step 1 refuses one that crosses midnight)
[ "$(gdate +%H%M)" -lt 2350 ] || { echo "run this desk test before 23:50 (its window must end by 23:59 the same day)"; exit 2; }
bash "$R/s02_window_e183.sh" "$(gdate +%F)" "$ls_" "$le_" > "$S/b-window.txt" 2>&1 || { echo "the window failed: $(tail -2 "$S/b-window.txt")"; fail=1; }

step "S1. step 5 on a clean stand-in box, then step 6 start and wait (the fast stand-in cmake)"
rm -rf "${B:?}/aifoundry3/aifoundry"; mkdir -p "$BOXT"
bash "$R/s07_a3_sync_e183.sh" > "$S/s1-sync.txt" 2>&1; rs=$?
grep -E 'synced to|STOP' "$S/s1-sync.txt" | san | cut -c1-220
mkdir -p "$BOXT/build/ettelem"
printf '#!/bin/sh\necho "STUB EXECUTED: ettelem $*" >&2\nexit 97\n' > "$BOXT/build/ettelem/ettelem"; chmod +x "$BOXT/build/ettelem/ettelem"
n0=$(nlog)
b6 start > "$S/s1-start.txt" 2>&1; ra=$?
grep -E 'STOP|REFUSED|runs on aifoundry3' "$S/s1-start.txt" | san | cut -c1-220
read -r rw n17 <<EOF2
$(waitb "$S/s1-wait.txt")
EOF2
grep -aE '^E183-BUILD-ATTEMPT|^TRAIN-HOST-BUILT|^BUILD INPUTS OK|^HARNESS|^check_e183 rc|^preflight_e183 rc|^e183_common rc|STOP|aifoundry3: the train host built' "$S/s1-wait.txt" | sort -u | san | cut -c1-220
nreads=$(since "$n0" | grep -c 'step=s08_a3_build_e183 class=read host=aifoundry3 bound=60s')
n13=$(since "$n0" | grep -c ' rc=13 ')
th=$([ -x "$BOXT/build/enercat-e183/host/enercat_host" ] && echo 1 || echo 0)
el=$(grep -c "^$TODAY .* a3-build-e183 ended rc=0: TRAIN-HOST-BUILT rc=0\$" "$AT" 2>/dev/null)
lg=$(grep -c '^BUILD OK' "$BOXT/build/e183-build-logs/$TODAY/e183-build-host-start1.txt" 2>/dev/null)
ok "$rs.$ra.$rw.$nreads.$n13.$th.$(builds).$el.$lg" "0.0.0.5.0.1.1.1.1" "S1 step 6 on the synced box: the build job, then the four checks, each in its own 60 s read (5 reads with the one before the build); one build counted, its ended line and its own log kept"

step "S2. step 8 (the dry pass) on the box step 6 left"
: > "$S/box-network.log"
bash "$R/s10_a3_dry_e183.sh" start > "$S/s2-start.txt" 2>&1; r1=$?
wait10 "$S/s2-wait.txt"; r2=$?
grep -aE '^E183 dry|^E183 start gate' "$S/s2-wait.txt" | sort -u | cut -c1-200
k1=$(has '^E183 dry 18310 rc=0' "$S/s2-wait.txt"); k3=$(has '^E183 dry 18301 --smoke rc=0' "$S/s2-wait.txt"); k4=$(has '^E183 start gate rc=8' "$S/s2-wait.txt")
nw=$(grep -c . "$S/box-network.log")
ok "$r1.$r2.$k1.$k3.$k4.$nw" "0.0.1.1.1.0" "S2 job a3-dry-e183 rc 0: 18310 0, the smoke 0, the start gate 8; no network call from the box"

step "X3. a second start after the good build: refused; wait reads the checks again"
hs0=$(hostsha); b0=$(builds)
b6 start > "$S/x3-start.txt" 2>&1; ra=$?
q=$(has 'REFUSED: the train host was built on aifoundry3 today' "$S/x3-start.txt")
read -r rw n17 <<EOF2
$(waitb "$S/x3-wait.txt")
EOF2
ok "$ra.$q.$([ "$(hostsha)" = "$hs0" ] && echo same).$(builds).$rw" "10.1.same.$b0.0" "X3 a second start after a good build refused (10): no job, the host unchanged; wait reads its checks again (0)"

step "X2. a build input off its pin on the box: no job, no build counted, step 5's words; then step 5, then step 6 builds"
fresh_day
printf '// changed on the box (desk test)\n' >> "$BOXT/workloads/enercat/host/main.cpp"
b6 start > "$S/x2-start.txt" 2>&1; ra=$?
grep -m1 'STOP' "$S/x2-start.txt" | cut -c1-260
q=$(has 'TRAIN-HOST-INPUTS-DIFFER' "$S/x2-start.txt"); w5=$(has 'run step 5 (rb/s07_a3_sync_e183.sh) once more' "$S/x2-start.txt")
nb=$(builds); jb=$([ -e "$J/a3-build-e183.rc" ] && [ "$(gdate -r "$J/a3-build-e183.rc" +%F)" = "$(gdate +%F)" ] && echo today || echo none)
bash "$R/s07_a3_sync_e183.sh" > "$S/x2-sync.txt" 2>&1; rs=$?
b6 start > "$S/x2-start2.txt" 2>&1; rb=$?
read -r rw n17 <<EOF2
$(waitb "$S/x2-wait.txt")
EOF2
ok "$ra.$q.$w5.$nb.$jb.$rs.$rb.$rw" "16.1.1.0.none.0.0.0" "X2 an input off its pin: 16 with step 5's words, no job, no build counted; step 5 then step 6: built (0)"

step "V. the 90 s stand-in cmake: one job, a second start refused while it runs, waits that say 17, then the checks"
fresh_day
n0=$(nlog); t0=$(gdate +%s)
FAKE_CMAKE_SLEEP_S=90 b6 start > "$S/v-start.txt" 2>&1; ra=$?
FAKE_CMAKE_SLEEP_S=90 b6 start > "$S/v-start2.txt" 2>&1; rb=$?
q=$(has 'REFUSED: 1 runbook job(s) still run on aifoundry3' "$S/v-start2.txt")
read -r rw n17 <<EOF2
$(waitb "$S/v-wait.txt" 20)
EOF2
dt=$(( $(gdate +%s) - t0 ))
n13=$(since "$n0" | grep -c ' rc=13 ')
ok "$ra.$rb.$q.$rw.$([ "$n17" -ge 2 ] && echo many17).$n13.$(builds)" "0.10.1.0.many17.0.1" "V a 90 s build as one detached job (the call ${dt} s in all; $n17 waits said 17): a second start refused while it ran (10), no call past a bound, one build counted"

step "O. a card session of ours on the box: start refused, and wait's first check refused"
: > "$S/ours-live.flag"
b6 start > "$S/o-start.txt" 2>&1; ra=$?
b6 wait > "$S/o-wait.txt" 2>&1; rw=$?
rm -f "$S/ours-live.flag"
qa=$(has 'REFUSED: a card session of ours runs on aifoundry3' "$S/o-start.txt"); qw=$(has 'REFUSED: a card session of ours runs on aifoundry3' "$S/o-wait.txt")
ok "$ra/$qa/$rw/$qw" "10/1/10/1" "O beside a session of ours: start refused (10), wait's checks refused (10)"

step "R1-R3. the re-run rule (the stand-in build fails): one re-run, then the fallback named, then a third start refused"
fresh_day
FAKE_CMAKE_FAIL=build b6 start > "$S/r1-start.txt" 2>&1
read -r r1 n17 <<EOF2
$(FAKE_CMAKE_FAIL=build waitb "$S/r1-wait.txt")
EOF2
q1=$(has 'build 1 of at most 2 today' "$S/r1-wait.txt")
FAKE_CMAKE_FAIL=build b6 start > "$S/r2-start.txt" 2>&1
read -r r2 n17 <<EOF2
$(FAKE_CMAKE_FAIL=build waitb "$S/r2-wait.txt")
EOF2
q2=$(has 'registered fallback, SKIP' "$S/r2-wait.txt")
b6 start > "$S/r3-start.txt" 2>&1; r3=$?
q3=$(has 'no third. E183 does not run today' "$S/r3-start.txt")
ok "$r1.$q1.$r2.$q2.$r3.$q3.$(builds)" "16.1.16.1.16.1.2" "R1-R3 the re-run rule: 16 asking one re-run; 16 naming the fallback SKIP; a third start refused (16); two builds counted"

step "T. the build past its own bound (E183_BUILD_S=5, RB_DESKTEST=1, the 90 s cmake): OVERRAN, one re-run; the bound without RB_DESKTEST refused"
fresh_day
E183_BUILD_S=5 RB_DESKTEST=1 FAKE_CMAKE_SLEEP_S=90 b6 start > "$S/t-start.txt" 2>&1; ra=$?
read -r rw n17 <<EOF2
$(waitb "$S/t-wait.txt")
EOF2
q=$(has 'TRAIN-HOST-BUILD-OVERRAN' "$S/t-wait.txt"); q2=$(has 'build 1 of at most 2 today' "$S/t-wait.txt")
: > "$S/calls.log"
E183_BUILD_S=5 b6 start > "$S/t-bad.txt" 2>&1; rb=$?
nc=$(grep -c . "$S/calls.log")
ok "$ra.$rw.$q.$q2.$rb.$nc" "0.16.1.1.10.0" "T a build past its own 5 s bound: OVERRAN, one re-run asked (16); E183_BUILD_S without RB_DESKTEST refused (10) with no call"

step "W. (N1) a wait call that fails before it reads the job (the network cut on the wait's call): 14, run wait again, never a failed build"
fresh_day
b6 start > "$S/w-start.txt" 2>&1
netcut 1
b6 wait > "$S/w-wait.txt" 2>&1; rw=$?
q=$(has 'no reading of the build job' "$S/w-wait.txt"); nf=$(has 'build failed' "$S/w-wait.txt")
read -r r2 n17 <<EOF2
$(waitb "$S/w-wait2.txt")
EOF2
ok "$rw.$q.$nf.$r2" "14.1.0.0" "W a dropped wait call: 14 with 'no reading of the build job', no build named failed; the next wait reads the build (0)"

step "N2. the first build fails; the re-run runs; its wait call is cut (the day's build 2)"
fresh_day
FAKE_CMAKE_FAIL=build b6 start > "$S/n2-s1.txt" 2>&1; r1=$?
read -r w1 n17 <<EOF2
$(FAKE_CMAKE_FAIL=build waitb "$S/n2-w1.txt")
EOF2
b6 start > "$S/n2-s2.txt" 2>&1; r2=$?
netcut 1
b6 wait > "$S/n2-w2.txt" 2>&1; w2=$?
stopline=$(grep -a 'STOP' "$S/n2-w2.txt" | tail -n 1 | cut -c1-260); echo "$stopline"
nr=$(has 'no reading of the build job' "$S/n2-w2.txt"); fb=$(has 'registered fallback, SKIP' "$S/n2-w2.txt")
read -r w3 n17 <<EOF2
$(waitb "$S/n2-w3.txt")
EOF2
b6 start > "$S/n2-s3.txt" 2>&1; r3=$?
fb3=$(cat "$S/n2-w3.txt" "$S/n2-s3.txt" | grep -c 'registered fallback, SKIP')
ok "$r1.$w1.$r2.$w2.$nr.$fb.$w3.$r3.$fb3.$(builds)" "0.16.0.14.1.0.0.10.0.2" "N2 the cut wait of the re-run reads 14 'no reading' and does NOT name the fallback; wait then reads the good build (0), and a start after it is refused (10); two builds counted"

step "N6. the first check's read after a good build is cut"
fresh_day
b6 start > "$S/n6-s.txt" 2>&1; ra=$?
sleep 6
netcut 2
b6 wait > "$S/n6-w.txt" 2>&1; rw=$?
grep -a 'STOP' "$S/n6-w.txt" | tail -n 1 | cut -c1-260
nr=$(has 'no reading of inputs' "$S/n6-w.txt"); am=$(has 'a dated amendment first' "$S/n6-w.txt")
read -r rw2 n17 <<EOF2
$(waitb "$S/n6-w2.txt")
EOF2
ok "$ra.$rw.$nr.$am.$rw2" "0.14.1.0.0" "N6 a cut check read is 14 'no reading of inputs' (never 'a dated amendment first'); wait then reads all four checks (0)"

step "L. a lost job: a fresh day, the 90 s stand-in cmake, the job's processes killed on the stand-in box mid-build"
fresh_day
FAKE_CMAKE_SLEEP_S=90 b6 start > "$S/l1.txt" 2>&1; ra=$?
sleep 3
jp=$(cat "$J/a3-build-e183.pid" 2>/dev/null)
[ -n "$jp" ] && killtree "$jp"
sleep 1
read -r rw n17 <<EOF2
$(waitb "$S/l1-wait.txt" 5)
EOF2
grep -aE '^JOB-LOST' "$S/l1-wait.txt" | head -n 1 | cut -c1-200
lo=$(has '^JOB-LOST a3-build-e183' "$S/l1-wait.txt")
m1=$(has "the train host's build job was lost (no process and no exit status) on aifoundry3 (the lines above; build 1 of at most 2 today)" "$S/l1-wait.txt")
ok "$ra.$rw.$lo.$m1.$(builds)" "0.16.1.1.1" "L the lost job: JOB-LOST is still a build's failure: one re-run asked for (16), one build counted"

step "C1-C3. step 11: the exact copy-back of a stand-in session's T0-named files, the collector (a stand-in), then a second run and a changed copy"
T0S=$(gdate +%s)
for d in e183/p18310 e183-smoke/p18301 e183-stoptest/p18302; do
  mkdir -p "$BOXT/build/claims-v3/aifoundry3/$d"
  printf '{"status":"ok","note":"desk test"}\n' > "$BOXT/build/claims-v3/aifoundry3/$d/block.json"
  printf 'desk test\n' > "$BOXT/build/claims-v3/aifoundry3/$d/run.log"
done
mkdir -p "$BOXT/build/e183"
printf '%s session start (T0 %s = 00:00:00 PST), kit v1; plan FULL\n%s session end (T0 %s)\n' "$(gdate '+%F %T %Z')" "$T0S" "$(gdate '+%F %T %Z')" "$T0S" > "$BOXT/build/e183/session-t$T0S.log"
for f in session-t$T0S.out queue-t$T0S.out dmcmd-preflight-t$T0S.txt config-t$T0S-start.json config-t$T0S-end.json; do echo "desk test" > "$BOXT/build/e183/$f"; done
echo "$T0S" > "$RB_OUT/t0-e183.txt"
cat > "$S/collect-standin.sh" <<'EOF2'
#!/usr/bin/env bash
# the desk test's stand-in collector: it writes the collector's output directory and its last line, nothing else
set -u
OUT=build/e183-out/$E183_DATE-e183-vector-add-r2-aifoundry3
mkdir -p "$OUT"; echo "a stand-in scored file (desk test)" > "$OUT/scored-e183.md"
echo "scored-e183.md written: $OUT"
EOF2
chmod +x "$S/collect-standin.sh"
rm -rf "${T:?}/build/e183-raw" "${T:?}/build/e183-out"
RB_DESKTEST=1 E183_COLLECT="$S/collect-standin.sh" bash "$R/s22_collect_e183.sh" > "$S/c1.txt" 2>&1; r1=$?
grep -E 'COPY EXACT|COPY NOT|STOP|collected and scored' "$S/c1.txt" | san | cut -c1-240
e1=$(has 'COPY EXACT' "$S/c1.txt")
RB_DESKTEST=1 E183_COLLECT="$S/collect-standin.sh" bash "$R/s22_collect_e183.sh" > "$S/c2.txt" 2>&1; r2=$?
echo "changed after the copy" >> "$T/build/e183-raw/e183/p18310/run.log"
/usr/bin/python3 -B "$T/tools/claims-v3/e183/copycheck_e183.py" "$T/build/e183-raw/logs/box-manifest.txt" "$T/build/e183-raw" "$(gdate +%F)" > "$S/c3.txt" 2>&1; r3=$?
head -n 2 "$S/c3.txt" | san | cut -c1-200
ok "$r1.$e1.$r2.$r3" "0.1.10.9" "C1 step 11: COPY EXACT and the collector ran (0); C2 the same step again into the same raw tree refused (10); C3 a changed copy reads COPY NOT EXACT (9)"

step "Z. no process of this test is left running"
sleep 1
z=$(leftovers); echo "leftovers: $z"
ok "$z" "0" "Z nothing left running"
echo
echo "SELFTEST-RB-E183 $npass of $ncase $([ "$fail" -eq 0 ] && echo PASS || echo FAIL)"
exit "$fail"
