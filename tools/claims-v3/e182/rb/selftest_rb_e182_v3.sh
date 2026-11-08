#!/usr/bin/env bash
# E182 (Q154, the kit's dated note 2): the desk test of note 2's two v3 steps with a FAKE ssh and rsync, on note 1's stand-in box (its setup
# is rb/selftest_rb_e182_v2.sh's, which stays as committed and is re-run unchanged beside this test for every v2 case). Stand-in ssh and
# rsync sit first on PATH and serve a stand-in box (a local directory laid out like aifoundry3's ~/aifoundry); they refuse any other host,
# and no lab box is reached. Everything runs in <scratch dir> (never the lab clone). The bounds are rb_run.py's own: this test sets no
# RB_<CLS>_S, so every read is killed at 60 s as on the card day (it refuses to start if one is set). The cases:
#   A   the dry listing v3 (both paths, the look before the post): every step exits 0, and the stand-ins see no ssh or rsync call;
#   K   step 2 v3 with no window in RB_OUT refuses (10), and no call is made;
#   P1  step 2 v3 on a scratch repository that holds every file the four lists name (with an origin, so the pull runs): 0, at the pins
#       32, 79, 50 and 49 (a stand-in note-2 list of 49 of the scratch's files: note 2's own list is written after this test's log);
#   P2  the kit's list one line short: step 2 v3 refuses (16) naming it against its pin 79; step 2 v2 passes the same tree (0): the fault;
#   S1  step 5 v2 on a clean stand-in box, the box's four stand-in binaries with their stand-in pins (the desk has no real binaries; on
#       aifoundry3 the committed pins are E178's), then step 6 v3 start and wait with the fast stand-in cmake (rb/fake_cmake_e182.sh, which
#       compiles the copy's patched main.cpp against Q139(k)'s mock runtime): 0, every check in its own 60 s read;
#   S2  step 8 v2 (the trains' dry pass) on the box step 6 v3 left: job a3-dry-e182 ends rc 0 (18220, 18215, the smoke, the start gate 8);
#   V2O THE FAULT, SHOWN: the stand-in cmake sleeps 90 s (rb/fake_cmake_slow_e182.sh), past the 60 s read bound: step 6 v2 is killed at its
#       bound (13, "run this step again"), the box holds no train host and no record, and run again it rebuilds from scratch and is killed
#       again (13); neither message names the fallback. The two runs' words and log lines are kept in <scratch>/step6-v2-overrun.txt;
#   V3S THE SAME 90 s CMAKE under step 6 v3: start (a second start while the job runs is refused, 10), then wait (17 while it runs, with
#       30 s waits), then done: 0, no call past a bound, every read bounded at 60 s, the job longer than 90 s;
#   O   a card session of ours on the box (the stand-in pgrep reports one): start, the fallback and wait's checks each refused (10) before
#       any build or check, no build counted;
#   R1-R4  the re-run rule (the stand-in build fails): the first failure asks for one re-run (16); the second names the fallback (16); a
#       third start is refused naming the fallback (16), no job started; the fallback then runs: step 6 v3 --no-trains (0, HARNESS OK 70)
#       and step 8 v2 --no-trains (job a3-dry-e182-nt rc 0);
#   T   the build past its own bound (E182_BUILD_S=5 with RB_DESKTEST=1, the 90 s cmake): TRAIN-HOST-BUILD-OVERRAN rc 124, one re-run asked
#       for (16); E182_BUILD_S without RB_DESKTEST refused (10, no call);
#   L   a lost job (its processes killed on the stand-in box mid-build): JOB-LOST, one re-run asked for (16);
#   Z   no process of this test is left running.
#
#   bash tools/claims-v3/e182/rb/selftest_rb_e182_v3.sh <scratch dir> > <log>
# SPDX-License-Identifier: Apache-2.0
set -u
SRC=$(cd "$(dirname "${BASH_SOURCE[0]}")/../../../.." && pwd)
S=${1:?a scratch directory outside the repository}
case "$S" in "$SRC"|"$SRC"/*) echo "the scratch directory must be outside the repository"; exit 2 ;; esac
for v in RB_PROBE_S RB_READ_S RB_COPY_S RB_WAIT_S RB_LAUNCH_S RB_DESK_S E182_BUILD_S RB_DESKTEST; do
  [ -z "${!v:-}" ] || { echo "$v is set: this test runs with rb_run.py's own bounds and no desk-test override in its environment"; exit 2; }
done
command -v gdate > /dev/null || { echo "no gdate (GNU date) on PATH"; exit 2; }
command -v timeout > /dev/null || { echo "no timeout on PATH"; exit 2; }
command -v sha256sum > /dev/null || { echo "no sha256sum on PATH"; exit 2; }
mkdir -p "$S"
S=$(cd "$S" && pwd)
rm -rf "${S:?}/tree" "${S:?}/box" "${S:?}/bin" "${S:?}/out" "${S:?}/boxbin" "${S:?}/drybin" "${S:?}/origin.git" "${S:?}/out-nowindow" "${S:?}/out-p" "${S:?}/out-b"
T=$S/tree; B=$S/box; BIN=$S/bin
mkdir -p "$T/tools/claims-v3" "$T/workloads" "$B/aifoundry3/aifoundry" "$BIN" "$S/out" "$S/drybin" "$S/boxbin"
for p in e182 e178 kinds hpl ccheck e128 e164 p8-600 q141k-runbook/k6 q141k-runbook/v3.1; do
  mkdir -p "$T/tools/claims-v3/$p"; rsync -a --exclude __pycache__ "$SRC/tools/claims-v3/$p/" "$T/tools/claims-v3/$p/"
done
cp -p "$SRC/tools/claims-v3/lib.sh" "$SRC/tools/claims-v3/dmcmd_audit.py" "$SRC/tools/claims-v3/dmcmd_table.json" "$T/tools/claims-v3/"
mkdir -p "$T/workloads/sparsity"
( cd "$SRC" && git ls-files workloads/sparsity ) | while IFS= read -r f; do mkdir -p "$T/$(dirname "$f")"; cp -p "$SRC/$f" "$T/$f"; done
# every file the three committed lists name (the kit's list names a few outside these directories), so step 2 can check them here
for l in SHA256SUMS-e182-registration SHA256SUMS-e182-kit SHA256SUMS-e182-note1; do
  awk '{print $2}' "$SRC/tools/claims-v3/e182/$l" | while IFS= read -r f; do
    [ -e "$T/$f" ] || { mkdir -p "$T/$(dirname "$f")"; cp -p "$SRC/$f" "$T/$f"; }
  done
done
# P1's stand-ins, written before the scratch commit: note 2's two desk-test logs (this test's own log is being written now) and a
# note-2 list of 49 of the scratch's files at their sha256 (note 2's own list is made after this test and holds its log)
rm -f "$T/tools/claims-v3/e182/SHA256SUMS-e182-note2"
printf 'SELFTEST-RB-E182-V3 0 of 0 PASS (a stand-in written by the v3 desk test for its case P1: this log is being written)\n' > "$T/tools/claims-v3/e182/logs/selftest-rb-e182-v3.txt"
printf 'SELFTEST-RB-E182-V2 0 of 0 PASS (a stand-in written by the v3 desk test for its case P1)\n' > "$T/tools/claims-v3/e182/logs/selftest-rb-e182-v2-note2.txt"
( cd "$T" && find tools/claims-v3/e182 -type f ! -name 'SHA256SUMS-e182-note2' | LC_ALL=C sort | head -n 49 | while IFS= read -r f; do sha256sum "$f"; done ) > "$S/note2-standin.txt"
cp "$S/note2-standin.txt" "$T/tools/claims-v3/e182/SHA256SUMS-e182-note2"
G="git -C $T -c user.name=e182-desktest -c user.email=desktest@localhost -c core.hooksPath=/dev/null -c commit.gpgsign=false"
$G init -q && $G add -A && $G commit -q -m "E182 runbook v3 desk test: the lab files the steps read" || { echo "the scratch repository failed"; exit 2; }
git clone -q --bare "$T" "$S/origin.git" && $G remote add origin "$S/origin.git" && $G fetch -q origin &&
  $G branch -q -u "origin/$($G rev-parse --abbrev-ref HEAD)" || { echo "the scratch repository's origin failed"; exit 2; }
BASE0=$($G rev-list --max-parents=0 HEAD)
echo "scratch repository: $($G ls-files | wc -l | tr -d ' ') files committed ($($G ls-files workloads/sparsity | wc -l | tr -d ' ') of them the workload's), with an origin"
REAL_RSYNC=$(command -v rsync)
cat > "$BIN/ssh" <<EOF
#!/bin/bash
echo "ssh \$*" >> "$S/calls.log"
host=""; cmd=""
while [ \$# -gt 0 ]; do case "\$1" in -o) shift 2 ;; -*) shift ;; *) if [ -z "\$host" ]; then host=\$1; shift; else cmd="\$*"; break; fi ;; esac; done
case "\$host" in aifoundry3) ;; *) echo "STAND-IN SSH: refusing host \$host" >&2; exit 97 ;; esac
[ "\$cmd" = true ] && exit 0
# the remote script reaches bash -s through a pipe, as over ssh (note 1's lesson: a seekable stdin lets a detached child rewind it)
cat | HOME="$B/\$host" PATH="$S/boxbin:\$PATH" bash -c "cd ~ && \$cmd"
EOF
cat > "$BIN/rsync" <<EOF
#!/bin/bash
echo "rsync \$*" >> "$S/calls.log"
a=()
while [ \$# -gt 0 ]; do case "\$1" in -e) shift 2 ;; *:*) h=\${1%%:*}; p=\${1#*:}; case "\$h" in aifoundry3) ;; *) echo "STAND-IN RSYNC: refusing \$h" >&2; exit 97 ;; esac; a+=("$B/\$h/\$p"); shift ;; *) a+=("\$1"); shift ;; esac; done
exec "$REAL_RSYNC" "\${a[@]}"
EOF
# the stand-in box's own commands (first on its PATH): v2's, except pgrep, which reports one card session of ours while
# <scratch>/ours-live.flag exists (case O) and none otherwise, and cmake, the slow stand-in (FAKE_CMAKE_SLEEP_S, 0 unless a case sets it)
for d in "$S/boxbin" "$S/drybin"; do
  printf '#!/bin/sh\necho aifoundry3\n' > "$d/hostname"
  printf '#!/bin/sh\nexec gdate "$@"\n' > "$d/date"
  printf '#!/bin/sh\nexec /usr/bin/python3 "$@"\n' > "$d/python3"
  printf '#!/bin/sh\necho "(desk test: no et-who here)"\n' > "$d/et-who"
  printf '#!/bin/sh\n[ -e "%s" ] && { echo 4242; exit 0; }\nexit 1\n' "$S/ours-live.flag" > "$d/pgrep"
  for n in ssh rsync scp; do printf '#!/bin/sh\necho "%s $*" >> "%s"\necho "NETWORK STAND-IN: %s refused" >&2\nexit 97\n' "$n" "$S/dry-network.log" "$n" > "$d/$n"; done
done
printf '#!/bin/sh\nexec "$@"\n' > "$S/boxbin/setsid"
cp -p "$SRC/tools/claims-v3/e182/rb/fake_cmake_slow_e182.sh" "$S/boxbin/cmake"
cp -p "$SRC/tools/claims-v3/e182/rb/fake_cmake_e182.sh" "$S/boxbin/fake_cmake_e182.sh"
chmod +x "$BIN/ssh" "$BIN/rsync" "$S/boxbin"/* "$S/drybin"/*
export PATH="$BIN:$PATH" RB_REPO="$T" RB_OUT="$S/out" RB_LOCK="$S/lock.txt" FAKE_CMAKE_MOCKRT="$T/tools/claims-v3/ccheck/mockrt" FAKE_CMAKE_SLEEP_S=0
: > "$S/calls.log"; : > "$RB_LOCK"; : > "$S/dry-network.log"; rm -f "$S/ours-live.flag"
R=$T/tools/claims-v3/e182/rb
BOXT=$B/aifoundry3/aifoundry
J=$BOXT/build/q141k/jobs
fail=0; npass=0; ncase=0
ok() { ncase=$((ncase + 1)); if [ "$1" = "$2" ]; then npass=$((npass + 1)); echo "-> PASS ($3)"; else echo "-> FAIL ($3: got $1, want $2)"; fail=1; fi; }
step() { echo; echo "== $*"; }
san() { sed -e "s#$S#<scratch>#g"; }
nlog() { if [ -f "$RB_OUT/runbook.log" ]; then grep -c . "$RB_OUT/runbook.log"; else echo 0; fi; }
since() { tail -n +"$(( $1 + 1 ))" "$RB_OUT/runbook.log" 2>/dev/null; }   # the runbook log's lines after line $1
builds() { if [ -f "$BOXT/build/e182-build-attempts.txt" ]; then grep -c "^$(TZ=America/Los_Angeles gdate +%F) " "$BOXT/build/e182-build-attempts.txt"; else echo 0; fi; }
leftovers() { pgrep -f "$S/boxbin/cmake|bash build/q141k/jobs/a3-build-e182[.]sh|tools/claims-v3/e182/build_host_e182_v2[.]sh|^sleep 90$" 2>/dev/null | grep -c .; }
v3() { bash "$R/s08_a3_preflight_e182_v3.sh" "$@"; }
wait3() {  # wait3 <out> [<max calls>]: step 6 v3's wait, again while it says 17; prints "<rc> <number of 17s>"
  local o=$1 m=${2:-12} k r n17=0
  : > "$o"
  for k in $(seq 1 "$m"); do v3 wait >> "$o" 2>&1; r=$?; [ "$r" -eq 17 ] || break; n17=$((n17 + 1)); done
  echo "$r $n17"
}
wait10() {  # wait10 <out> [--no-trains]: step 8 v2's wait, again while it says 17
  local o=$1 x=${2:-} k r
  for k in 1 2 3 4 5 6; do bash "$R/s10_a3_dry_e182_v2.sh" wait $x > "$o" 2>&1; r=$?; [ "$r" -eq 17 ] || break; done
  return "$r"
}
has() { grep -aq "$1" "$2" && echo 1 || echo 0; }
killtree() {  # freeze the parent first (so the job never writes its exit status), then its children, then kill them all
  local p=$1 c kids; kids=$(pgrep -P "$p" 2>/dev/null); kill -STOP "$p" 2>/dev/null
  for c in $kids; do killtree "$c"; done; kill -KILL "$p" 2>/dev/null
}
cd "$T" || exit 2

step "A. the dry listing v3 (FULL and the fallback, the look before the post): every step exits 0, no ssh or rsync call"
: > "$S/calls.log"
bash "$R/list_steps_e182_v3.sh" "$S/dry-out" > "$S/dry-listing.txt" 2>&1; rc=$?
n=$(grep -c . "$S/calls.log"); tail -n 1 "$S/dry-listing.txt"
lp=$(awk '/s05_look_k6.sh aifoundry3$/ {l=NR} /the day.s one post, made AFTER the look/ {p=NR} END {print (l > 0 && p > l) ? 1 : 0}' "$S/dry-listing.txt")
ok "$rc.$n.$lp" "0.0.1" "A dry listing v3: 0 failing, no call, the look listed before the post"

step "K. step 2 v3 with no window in RB_OUT (s02 not run)"
: > "$S/calls.log"
RB_OUT="$S/out-nowindow" bash "$R/s03_desk_e182_v3.sh" > "$S/k.txt" 2>&1; rc=$?
grep -m1 -i 'no window' "$S/k.txt" | cut -c1-200; n=$(grep -c . "$S/calls.log")
ok "$rc.$n" "10.0" "K step 2 v3 refuses without step 1's window"

step "P1. step 2 v3 on the scratch repository (every listed file there, an origin, the stand-in note-2 list of 49)"
mkdir -p "$S/out-p"; RB_OUT="$S/out-p" bash "$R/s02_window_e182.sh" "$(gdate +%F)" 23:00 23:30 > /dev/null 2>&1
RB_OUT="$S/out-p" RB_E182_BASE=$BASE0 bash "$R/s03_desk_e182_v3.sh" > "$S/p1.txt" 2>&1; rc=$?
grep -E 'desk check v3|STOP' "$S/p1.txt" | cut -c1-330
pins=$(grep -c 'the four hash lists at their pinned counts (32, 79, 50 and 49)' "$S/p1.txt")
ok "$rc.$pins" "0.1" "P1 step 2 v3 passes the intact tree at the pins 32, 79, 50 and 49"

step "P2. the kit's list one line short (committed): step 2 v3, then step 2 v2, on the same tree"
sed -i '' -e '$d' "$T/tools/claims-v3/e182/SHA256SUMS-e182-kit"
$G commit -q -am "desk test: the kit's list one line short" || echo "the scratch commit failed"
RB_OUT="$S/out-p" RB_E182_BASE=$BASE0 bash "$R/s03_desk_e182_v3.sh" > "$S/p2-v3.txt" 2>&1; r3=$?
grep -m1 'STOP' "$S/p2-v3.txt" | cut -c1-260
k3=$(grep -c 'SHA256SUMS-e182-kit(78 OK of 78; pinned 79)' "$S/p2-v3.txt")
RB_OUT="$S/out-p" RB_E182_BASE=$BASE0 bash "$R/s03_desk_e182_v2.sh" > "$S/p2-v2.txt" 2>&1; r2=$?
grep -E 'desk check v2|STOP' "$S/p2-v2.txt" | cut -c1-260
k2=$(grep -c 'the three hash lists (32, 78 and 50)' "$S/p2-v2.txt")
$G reset -q --hard HEAD~1
ok "$r3.$k3.$r2.$k2" "16.1.0.1" "P2 step 2 v3 refuses the short list against its pin (16); step 2 v2 passes it, counting the list against itself (0)"

# ---- the box's side, through the fake ssh
export RB_OUT="$S/out-b"; mkdir -p "$RB_OUT"
ls_=$(gdate -d '+4 min' +%H:%M); le_=$(gdate -d '+2 hour' +%H:%M)
bash "$R/s02_window_e182.sh" "$(gdate +%F)" "$ls_" "$le_" > "$S/b-window.txt" 2>&1 || { echo "the window failed: $(tail -2 "$S/b-window.txt")"; fail=1; }

step "S1. step 5 v2 on a clean stand-in box, its stand-in binaries and pins, then step 6 v3 start and wait (the fast stand-in cmake)"
rm -rf "${B:?}/aifoundry3/aifoundry"; mkdir -p "$BOXT"
: > "$S/calls.log"
bash "$R/s07_a3_sync_e182_v2.sh" > "$S/s1-sync.txt" 2>&1; rs=$?
grep -E 'synced to|STOP' "$S/s1-sync.txt" | san | cut -c1-220
for f in build/sparsity/host/sparsity_host build/ccheck/b/host/sparsity_host build/ettelem/ettelem; do
  mkdir -p "$BOXT/$(dirname "$f")"
  printf '#!/bin/sh\n# options the preflight looks for: file: int8 fp16 --dump-tiles --stop-file --c-log --c-poison --values-b --abba --launches\necho "STUB EXECUTED: %s $*" >&2\nexit 97\n' "$f" > "$BOXT/$f"
  chmod +x "$BOXT/$f"
done
mkdir -p "$BOXT/build/sparsity/kernel"; echo "stub kernel (desk test)" > "$BOXT/build/sparsity/kernel/sparsity.elf"
/usr/bin/python3 -B - "$BOXT" <<'PY'
import hashlib, json, os, sys
t = sys.argv[1]
p = os.path.join(t, "tools/claims-v3/e182/harness-e182.json")
h = json.load(open(p))
for rel in h["box_binaries_sha256"]:
    h["box_binaries_sha256"][rel] = hashlib.sha256(open(os.path.join(t, rel), "rb").read()).hexdigest()
open(p, "w").write(json.dumps(h, indent=1) + "\n")
print("the stand-in box's harness-e182.json now pins its 4 stand-in binaries (the desk's stand-in for E178's binaries on aifoundry3)")
PY
n0=$(nlog)
v3 start > "$S/s1-start.txt" 2>&1; ra=$?
grep -E 'STOP|REFUSED|JOB-STARTED|runs on aifoundry3' "$S/s1-start.txt" | san | cut -c1-220
read -r rw n17 <<EOF2
$(wait3 "$S/s1-wait.txt")
EOF2
grep -aE '^TRAIN-HOST-BUILT|^NOTE1 FILES OK|^HARNESS|^check_e182 rc|^preflight_e182 rc|^e182_common rc|STOP|aifoundry3: the train host built' "$S/s1-wait.txt" | sort -u | san | cut -c1-220
nreads=$(since "$n0" | grep -c 'step=s08_a3_preflight_v3_e182 class=read host=aifoundry3 bound=60s')
nany=$(since "$n0" | grep -c 'step=s08_a3_preflight_v3_e182 class=read ')
n13=$(since "$n0" | grep -c ' rc=13 ')
th=$([ -x "$BOXT/build/e182host/b/host/sparsity_host" ] && echo 1 || echo 0)
ok "$rs.$ra.$rw.$nreads.$nany.$n13.$th.$(builds)" "0.0.0.5.5.0.1.1" "S1 step 6 v3 on the synced box: the build job, then NOTE1 FILES OK 10, HARNESS OK 73, GO and the verify, each in its own 60 s read (5 reads with the one before the build); no call past a bound; one build counted"

step "S2. step 8 v2 (the trains' dry pass) on the box step 6 v3 left"
: > "$S/dry-network.log"
bash "$R/s10_a3_dry_e182_v2.sh" start > "$S/s2-start.txt" 2>&1; r1=$?
wait10 "$S/s2-wait.txt"; r2=$?
grep -aE '^E182 dry|^E182 start gate' "$S/s2-wait.txt" | sort -u | cut -c1-200
k1=$(has '^E182 dry 18220 rc=0' "$S/s2-wait.txt"); k2=$(has '^E182 dry 18215 rc=0' "$S/s2-wait.txt")
k3=$(has '^E182 dry 18201 --smoke rc=0' "$S/s2-wait.txt"); k4=$(has '^E182 start gate rc=8' "$S/s2-wait.txt")
nw=$(grep -c . "$S/dry-network.log")
ok "$r1.$r2.$k1.$k2.$k3.$k4.$nw" "0.0.1.1.1.1.0" "S2 job a3-dry-e182 rc 0 with the host step 6 v3 built: 18220 0, 18215 0, the smoke 0, the start gate 8; no network call from the box"

step "V2O. the fault, shown: the stand-in cmake sleeps 90 s, past the 60 s read bound: step 6 v2, twice"
EV=$S/step6-v2-overrun.txt
{ echo "E182 kit note 2: step 6 v2 (rb/s08_a3_preflight_e182_v2.sh, as committed) against a stand-in cmake that sleeps 90 s in its build phase"
  echo "(rb/fake_cmake_slow_e182.sh), on the desk test's stand-in box, with rb_run.py's own bounds (no RB_<CLS>_S set): $(gdate '+%F %T %Z')"; } > "$EV"
for k in 1 2; do
  n0=$(nlog); t0=$(gdate +%s)
  env FAKE_CMAKE_SLEEP_S=90 bash "$R/s08_a3_preflight_e182_v2.sh" > "$S/v2o-$k.txt" 2>&1; r=$?
  dt=$(( $(gdate +%s) - t0 ))
  eval "rv$k=$r"
  eval "st$k=$(grep -c 'ran past its bound and was killed: run this step again' "$S/v2o-$k.txt")"
  eval "fb$k=$(grep -c 'no train runs today' "$S/v2o-$k.txt")"
  eval "lg$k=$(since "$n0" | grep -c 'step=s08_a3_preflight_v2_e182 class=read host=aifoundry3 bound=60s .* rc=13 .*status=timeout')"
  eval "th$k=$([ -e "$BOXT/build/e182host/b/host/sparsity_host" ] || [ -e "$BOXT/build/e182host/SHA256" ] && echo 1 || echo 0)"
  eval "cm$k=$(stat -f %m "$BOXT/build/e182host/configure.log" 2>/dev/null || echo 0)"
  { echo; echo "---- run $k: exit $r after $dt s"
    sed "s#$S#<scratch>#g" "$S/v2o-$k.txt" | cut -c1-300
    echo "  the runbook log's lines for this run:"
    since "$n0" | sed -e "s#$S#<scratch>#g" -e 's/^/    /' | cut -c1-300
    echo "  the box after it: train host $([ -e "$BOXT/build/e182host/b/host/sparsity_host" ] && echo present || echo absent), build record $([ -e "$BOXT/build/e182host/SHA256" ] && echo present || echo absent); the build's configure log written $(gdate -d "@$(stat -f %m "$BOXT/build/e182host/configure.log" 2>/dev/null || echo 0)" '+%T %Z') (a fresh configure: the build started from scratch)"; } >> "$EV"
  echo "run $k: exit $r after $dt s"
done
sleep 2
left=$(leftovers)
{ echo; echo "---- what it shows: each run of step 6 v2 is killed at its 60 s read bound (13) and says 'run this step again'; the build"
  echo "started from scratch each time (build_host_e182_v2.sh removes src/, b/ and the record first), so a re-run is killed the same way;"
  echo "neither message names the registered fallback (PASSES). Processes of the killed builds left running: $left."; } >> "$EV"
fresh=$([ "$cm2" -gt "$cm1" ] && echo 1 || echo 0)
ok "$rv1.$st1.$fb1.$lg1.$th1.$rv2.$st2.$fb2.$lg2.$th2.$fresh.$left" "13.1.0.1.0.13.1.0.1.0.1.0" "V2O step 6 v2 killed at the 60 s read bound twice (13 'run this step again'), the box left with no train host or record each time, the second run configured afresh (a rebuild from scratch), the fallback never named; no build left running"

step "V3S. the same 90 s stand-in cmake under step 6 v3: start, a second start while it runs, then wait (30 s waits, 17 while it runs)"
rm -f "$BOXT/build/e182-build-attempts.txt"
n0=$(nlog)
env FAKE_CMAKE_SLEEP_S=90 bash "$R/s08_a3_preflight_e182_v3.sh" start > "$S/v3s-start.txt" 2>&1; ra=$?
grep -E 'STOP|JOB-STARTED|runs on aifoundry3' "$S/v3s-start.txt" | san | cut -c1-200
v3 start > "$S/v3s-start2.txt" 2>&1; rb2=$?
grep -m1 'STOP' "$S/v3s-start2.txt" | cut -c1-220
rj=$(has 'runbook job(s) still run on aifoundry3' "$S/v3s-start2.txt"); b1=$(builds)
read -r rw n17 <<EOF2
$(export RB_WAIT_LOOP_S=30; wait3 "$S/v3s-wait.txt" 12)
EOF2
grep -aE '^E182-BUILD-ATTEMPT|^build_host_e182_v2 rc|^fake cmake \(slow\)|^TRAIN-HOST-BUILT|^HARNESS|^preflight_e182 rc|^e182_common rc|STOP|the dry pass a3-build-e182 still runs|aifoundry3: the train host built' "$S/v3s-wait.txt" | sort | uniq -c | san | cut -c1-220
grep -a 'fake cmake (slow)' "$BOXT/build/e182-build-host.txt" | head -n 1
span=$(/usr/bin/python3 -B - "$J/a3-build-e182.out" <<'PY'
import re, sys, datetime
s = open(sys.argv[1]).read()
b = re.search(r"JOB-BEGIN \S+ (\S+ \S+)", s); e = re.search(r"JOB-END \S+ rc=\d+ (\S+ \S+)", s)
f = "%Y-%m-%d %H:%M:%S"
print(int((datetime.datetime.strptime(e.group(1), f) - datetime.datetime.strptime(b.group(1), f)).total_seconds()) if b and e else -1)
PY
)
nreads=$(since "$n0" | grep -c 'step=s08_a3_preflight_v3_e182 class=read host=aifoundry3 bound=60s')
nany=$(since "$n0" | grep -c 'step=s08_a3_preflight_v3_e182 class=read ')
nwait=$(since "$n0" | grep -c 'step=s08_a3_preflight_v3_e182 class=wait host=aifoundry3 bound=600s')
n13=$(since "$n0" | grep -c ' rc=13 ')
long=$([ "$span" -ge 90 ] && echo 1 || echo 0); some17=$([ "$n17" -ge 1 ] && echo 1 || echo 0)
echo "the job took $span s; step 6 v3's waits: $nwait ($n17 said 17); its reads: $nany, $nreads of them bounded at 60 s (the two starts' and the four checks'); calls past a bound: $n13"
ok "$ra.$rb2.$rj.$b1.$rw.$some17.$long.$nreads.$nany.$n13.$(builds)" "0.10.1.1.0.1.1.6.6.0.1" "V3S step 6 v3 passes the 90 s build: one job (a second start refused while it runs), waits that say 17, then the four checks in 60 s reads; nothing past a bound"

step "O. a card session of ours on the box (the stand-in pgrep reports one): start, the fallback, then wait's checks"
touch "$S/ours-live.flag"
b0=$(builds); js0=$(gdate -r "$J/a3-build-e182.sh" +%s 2>/dev/null)
: > "$S/calls.log"
v3 start > "$S/o1.txt" 2>&1; r1=$?; c1=$(grep -c '^ssh ' "$S/calls.log")
v3 --no-trains > "$S/o2.txt" 2>&1; r2=$?
v3 wait > "$S/o3.txt" 2>&1; r3=$?
rm -f "$S/ours-live.flag"
for f in o1 o2 o3; do grep -m1 'STOP' "$S/$f.txt" | cut -c1-200; done
q1=$(has 'REFUSED: a card session of ours runs on aifoundry3' "$S/o1.txt"); q2=$(has 'REFUSED: a card session of ours runs on aifoundry3' "$S/o2.txt"); q3=$(has 'REFUSED: a card session of ours runs on aifoundry3' "$S/o3.txt")
js1=$(gdate -r "$J/a3-build-e182.sh" +%s 2>/dev/null)
ok "$r1.$q1.$c1.$r2.$q2.$r3.$q3.$([ "$(builds)" = "$b0" ] && echo same).$([ "$js1" = "$js0" ] && echo same)" "10.1.2.10.1.10.1.same.same" "O each refused (10) beside a session of ours, the start after its probe and one read, no build started or counted"

step "R1. the re-run rule: a fresh day, the stand-in build fails (FAKE_CMAKE_FAIL=build): the first failure"
rm -f "$BOXT/build/e182-build-attempts.txt"
env FAKE_CMAKE_FAIL=build bash "$R/s08_a3_preflight_e182_v3.sh" start > "$S/r1-start.txt" 2>&1; ra=$?
read -r rw n17 <<EOF2
$(wait3 "$S/r1-wait.txt")
EOF2
grep -a 'STOP' "$S/r1-wait.txt" | tail -n 1 | cut -c1-260
m1=$(has 'build 1 of at most 2 today): run this step.s start once more (the one re-run)' "$S/r1-wait.txt")
f1=$(has '^TRAIN-HOST-BUILD-FAILED' "$S/r1-wait.txt")
th=$([ -e "$BOXT/build/e182host/b/host/sparsity_host" ] || [ -e "$BOXT/build/e182host/SHA256" ] && echo 1 || echo 0)
ok "$ra.$rw.$f1.$m1.$th.$(builds)" "0.16.1.1.0.1" "R1 the first failed build: 16, one re-run asked for, no train host or record left, one build counted"
step "R2. the one re-run fails too"
env FAKE_CMAKE_FAIL=build bash "$R/s08_a3_preflight_e182_v3.sh" start > "$S/r2-start.txt" 2>&1; ra=$?
read -r rw n17 <<EOF2
$(wait3 "$S/r2-wait.txt")
EOF2
grep -a 'STOP' "$S/r2-wait.txt" | tail -n 1 | cut -c1-330
m2=$(has "it was the day's build 2 (the first and its one re-run are spent): no train runs today: run step 6 v3 with --no-trains (rb/s08_a3_preflight_e182_v3.sh --no-trains), then step 8 v2 with --no-trains (rb/s10_a3_dry_e182_v2.sh start --no-trains, then wait --no-trains), then step 9 v2 PASSES no (rb/s11_a3_session_e182_v2.sh PASSES no)" "$S/r2-wait.txt")
ok "$ra.$rw.$m2.$(builds)" "0.16.1.2" "R2 the second failed build: 16, the fallback's three steps named, two builds counted"
step "R3. a third start"
js0=$(gdate -r "$J/a3-build-e182.sh" +%s 2>/dev/null)
v3 start > "$S/r3.txt" 2>&1; r3=$?
grep -m1 'STOP' "$S/r3.txt" | cut -c1-330
m3=$(has "two train-host builds were started on aifoundry3 today (the first and its one re-run): no third. no train runs today: run step 6 v3 with --no-trains" "$S/r3.txt")
js1=$(gdate -r "$J/a3-build-e182.sh" +%s 2>/dev/null)
ok "$r3.$m3.$(builds).$([ "$js1" = "$js0" ] && echo same)" "16.1.2.same" "R3 no third build: 16, the fallback named, no job started"
step "R4. the fallback runs: step 6 v3 --no-trains, then step 8 v2 --no-trains"
v3 --no-trains > "$S/r4a.txt" 2>&1; ra=$?
grep -aE '^HARNESS|^preflight_e182 rc|^e182_common rc|STOP|the trains off' "$S/r4a.txt" | sort -u | cut -c1-200
h70=$(has '^HARNESS OK: 70 files' "$S/r4a.txt")
: > "$S/dry-network.log"
bash "$R/s10_a3_dry_e182_v2.sh" start --no-trains > "$S/r4b.txt" 2>&1; rb_=$?
wait10 "$S/r4c.txt" --no-trains; rc_=$?
grep -aE '^E182 dry|^E182 start gate' "$S/r4c.txt" | sort -u | cut -c1-200
k1=$(has '^E182 dry 18220 rc=0' "$S/r4c.txt"); k2=$(has '^E182 dry 18201 --smoke trains=no rc=0' "$S/r4c.txt"); k3=$(has '^E182 start gate rc=8' "$S/r4c.txt")
nw=$(grep -c . "$S/dry-network.log")
ok "$ra.$h70.$rb_.$rc_.$k1.$k2.$k3.$nw" "0.1.0.0.1.1.1.0" "R4 the fallback: step 6 v3 --no-trains 0 (HARNESS OK 70, GO, verify), step 8 v2 --no-trains job rc 0 (18220 0, the smoke trains=no 0, the gate 8); no network call"

step "T. the build past its own bound: E182_BUILD_S=5 (RB_DESKTEST=1), the 90 s stand-in cmake, a fresh day"
rm -f "$BOXT/build/e182-build-attempts.txt"
: > "$S/calls.log"
env E182_BUILD_S=5 bash "$R/s08_a3_preflight_e182_v3.sh" start > "$S/t0.txt" 2>&1; r0=$?; c0=$(grep -c . "$S/calls.log")
grep -m1 'STOP' "$S/t0.txt" | cut -c1-200
env RB_DESKTEST=1 E182_BUILD_S=5 FAKE_CMAKE_SLEEP_S=90 bash "$R/s08_a3_preflight_e182_v3.sh" start > "$S/t1.txt" 2>&1; ra=$?
read -r rw n17 <<EOF2
$(wait3 "$S/t1-wait.txt")
EOF2
grep -aE '^TRAIN-HOST-BUILD-OVERRAN|^build_host_e182_v2 rc' "$S/t1-wait.txt" | sort -u | cut -c1-200; grep -a 'STOP' "$S/t1-wait.txt" | tail -n 1 | cut -c1-260
o1=$(has '^TRAIN-HOST-BUILD-OVERRAN rc=124' "$S/t1-wait.txt"); m1=$(has 'ran past its own 5 s bound on aifoundry3 (the lines above; build 1 of at most 2 today)' "$S/t1-wait.txt")
sleep 1; lt=$(leftovers)
ok "$r0.$c0.$ra.$rw.$o1.$m1.$(builds).$lt" "10.0.0.16.1.1.1.0" "T E182_BUILD_S without RB_DESKTEST refused (10, no call); the build past its own bound reads OVERRAN rc 124 and asks for one re-run (16); nothing left running"

step "L. a lost job: a fresh day, the 90 s stand-in cmake, the job's processes killed on the stand-in box mid-build"
rm -f "$BOXT/build/e182-build-attempts.txt"
env FAKE_CMAKE_SLEEP_S=90 bash "$R/s08_a3_preflight_e182_v3.sh" start > "$S/l1.txt" 2>&1; ra=$?
sleep 3
jp=$(cat "$J/a3-build-e182.pid" 2>/dev/null)
[ -n "$jp" ] && killtree "$jp"
sleep 1
read -r rw n17 <<EOF2
$(wait3 "$S/l1-wait.txt")
EOF2
grep -aE '^JOB-LOST' "$S/l1-wait.txt" | head -n 1 | cut -c1-200; grep -a 'STOP' "$S/l1-wait.txt" | tail -n 1 | cut -c1-260
lo=$(has '^JOB-LOST a3-build-e182' "$S/l1-wait.txt"); m1=$(has 'job was lost (no process and no exit status) on aifoundry3 (the lines above; build 1 of at most 2 today)' "$S/l1-wait.txt")
sleep 1
ok "$ra.$rw.$lo.$m1.$(builds)" "0.16.1.1.1" "L the lost job: JOB-LOST, one re-run asked for (16), one build counted"

step "Z. no process of this test left running"
sleep 1
z=$(pgrep -f "$S/" 2>/dev/null | grep -v "^$$\$" | grep -c .)
zs=$(leftovers)
ok "$z.$zs" "0.0" "Z nothing of this test's stand-in box or builds left running"

echo
echo "SELFTEST-RB-E182-V3 $npass of $ncase $([ "$fail" -eq 0 ] && echo PASS || echo FAIL)"
exit "$fail"
