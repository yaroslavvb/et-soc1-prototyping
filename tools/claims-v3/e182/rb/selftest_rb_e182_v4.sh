#!/usr/bin/env bash
# E182 (Q154, the kit's dated note 3): the desk test of note 3's steps with a FAKE ssh and rsync, on note 1's stand-in box (its setup is
# note 2's desk test's, rb/selftest_rb_e182_v3.sh, which stays as committed). Stand-in ssh and rsync sit first on PATH and serve a stand-in
# box (a local directory laid out like aifoundry3's ~/aifoundry); they refuse any other host, and no lab box is reached. Everything runs in
# <scratch dir> (never the lab clone). The bounds are rb_run.py's own: this test sets no RB_<CLS>_S, so every read is killed at 60 s as on
# the card day (it refuses to start if one is set). Each fault note 2's verifier found is shown under step 6 v3 or step 11 v2, then its fix
# under step 6 v4 or step 11 v3. The cases:
#   A   the dry listing v4 (both paths, the look before the post): every step exits 0, and the stand-ins see no ssh or rsync call;
#   K   step 2 v4 with no window in RB_OUT refuses (10), and no call is made;
#   P1  step 2 v4 on a scratch repository that holds every file the five lists name (with an origin, so the pull runs): 0, at the pins
#       32, 79, 50, 49 and 89 (a stand-in note-3 list of 89 of the scratch's files: note 3's own list is written after this test's log);
#   P2  note 3's list one line short: step 2 v4 refuses (16) naming it against its pin 89; step 2 v3 passes the same tree (0);
#   S1  step 5 v2 on a clean stand-in box, its four stand-in binaries with their stand-in pins, then step 6 v4 start and wait with the fast
#       stand-in cmake: 0, five 60 s reads, one build counted, its "ended" line and its own log kept on the box;
#   S2  step 8 v2 (the trains' dry pass) on the box step 6 v4 left: job a3-dry-e182 ends rc 0;
#   X3  (the verifier's minor 2) a second start after that good build: step 6 v4 refuses it (10), no job, the host's sha256 unchanged, and
#       wait reads the checks again (0); X3v, the fault shown: step 6 v3 starts a build after a good one, and when it fails the good host
#       is gone and the fallback is named;
#   X2  (the verifier's minor 1) main.cpp off its pin on the box: step 6 v4's read before the build says TRAIN-HOST-INPUTS-DIFFER (16) with
#       note 1's words (step 5 v2 once more), no job, no build counted; X2v, the fault shown: step 6 v3 builds, counts a build and asks for
#       a re-run with no word of step 5; X2r: step 5 v2 sends main.cpp back, and step 6 v4 builds (0);
#   X2b the race: main.cpp changes after the read and before the job copies it (a stand-in timeout on the box changes it once): the job
#       reads TRAIN-HOST-INPUTS-DIFFER, wait says note 1's words (16), and no build is counted; step 5 v2, then step 6 v4 builds (0);
#   V4S the 90 s stand-in cmake under step 6 v4: one job (a second start refused while it runs, 10), waits that say 17, the four checks:
#       0, six 60 s reads, no call past a bound;
#   O   a card session of ours on the box (the stand-in pgrep reports one): start, the fallback and wait's checks each refused (10);
#   R1-R4  the re-run rule (the stand-in build fails): one re-run asked for (16); the second names the fallback (16); a third start is
#       refused (16); the fallback runs: step 6 v4 --no-trains (0, HARNESS OK 70) and step 8 v2 --no-trains (job a3-dry-e182-nt rc 0);
#   C   (the verifier's nit 5) step 11 v3 on that fallback day's box: the count file and both builds' own logs copied into the raw tree's
#       logs/ (14 at the C-session gate, by design: the stand-in tree holds no C log); Cv, the nit shown: step 11 v2 copies neither;
#   T   the build past its own bound (E182_BUILD_S=5 with RB_DESKTEST=1, the 90 s cmake): TRAIN-HOST-BUILD-OVERRAN rc 124, one re-run (16);
#       E182_BUILD_S without RB_DESKTEST refused (10, no call);
#   L   a lost job (its processes killed mid-build): JOB-LOST, one re-run (16), and the lost build's own log kept on the box;
#   Z   no process of this test is left running.
#
#   bash tools/claims-v3/e182/rb/selftest_rb_e182_v4.sh <scratch dir> > <log>
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
REAL_TIMEOUT=$(command -v timeout)
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
# every file the four committed lists name (the kit's list names a few outside these directories), so step 2 can check them here
for l in SHA256SUMS-e182-registration SHA256SUMS-e182-kit SHA256SUMS-e182-note1 SHA256SUMS-e182-note2; do
  awk '{print $2}' "$SRC/tools/claims-v3/e182/$l" | while IFS= read -r f; do
    [ -e "$T/$f" ] || { mkdir -p "$T/$(dirname "$f")"; cp -p "$SRC/$f" "$T/$f"; }
  done
done
# P1's stand-ins, written before the scratch commit: note 3's desk-test log (this test's own log is being written now) and a note-3 list
# of 89 of the scratch's files at their sha256 (note 3's own list is made after this test and holds its log)
rm -f "$T/tools/claims-v3/e182/SHA256SUMS-e182-note3"
printf 'SELFTEST-RB-E182-V4 0 of 0 PASS (a stand-in written by the v4 desk test for its case P1: this log is being written)\n' > "$T/tools/claims-v3/e182/logs/selftest-rb-e182-v4.txt"
( cd "$T" && find tools/claims-v3/e182 -type f ! -name 'SHA256SUMS-e182-note3' | LC_ALL=C sort | head -n 89 | while IFS= read -r f; do sha256sum "$f"; done ) > "$S/note3-standin.txt"
cp "$S/note3-standin.txt" "$T/tools/claims-v3/e182/SHA256SUMS-e182-note3"
G="git -C $T -c user.name=e182-desktest -c user.email=desktest@localhost -c core.hooksPath=/dev/null -c commit.gpgsign=false"
$G init -q && $G add -A && $G commit -q -m "E182 runbook v4 desk test: the lab files the steps read" || { echo "the scratch repository failed"; exit 2; }
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
R=$T/tools/claims-v3/e182/rb
BOXT=$B/aifoundry3/aifoundry
J=$BOXT/build/q141k/jobs
# the stand-in box's own commands (first on its PATH): note 2's test's, plus a timeout that, while <scratch>/race.flag exists, first changes
# the box's main.cpp once (case X2b: an input that changes after step 6 v4's read and before the build job copies it), then runs the real one
for d in "$S/boxbin" "$S/drybin"; do
  printf '#!/bin/sh\necho aifoundry3\n' > "$d/hostname"
  printf '#!/bin/sh\nexec gdate "$@"\n' > "$d/date"
  printf '#!/bin/sh\nexec /usr/bin/python3 "$@"\n' > "$d/python3"
  printf '#!/bin/sh\necho "(desk test: no et-who here)"\n' > "$d/et-who"
  printf '#!/bin/sh\n[ -e "%s" ] && { echo 4242; exit 0; }\nexit 1\n' "$S/ours-live.flag" > "$d/pgrep"
  for n in ssh rsync scp; do printf '#!/bin/sh\necho "%s $*" >> "%s"\necho "NETWORK STAND-IN: %s refused" >&2\nexit 97\n' "$n" "$S/dry-network.log" "$n" > "$d/$n"; done
done
printf '#!/bin/sh\nexec "$@"\n' > "$S/boxbin/setsid"
printf '#!/bin/sh\nif [ -e "%s" ]; then rm -f "%s"; printf "// changed on the box after the read before the build (desk test)\\n" >> "%s"; fi\nexec "%s" "$@"\n' \
  "$S/race.flag" "$S/race.flag" "$BOXT/workloads/sparsity/host/main.cpp" "$REAL_TIMEOUT" > "$S/boxbin/timeout"
cp -p "$SRC/tools/claims-v3/e182/rb/fake_cmake_slow_e182.sh" "$S/boxbin/cmake"
cp -p "$SRC/tools/claims-v3/e182/rb/fake_cmake_e182.sh" "$S/boxbin/fake_cmake_e182.sh"
chmod +x "$BIN/ssh" "$BIN/rsync" "$S/boxbin"/* "$S/drybin"/*
export PATH="$BIN:$PATH" RB_REPO="$T" RB_OUT="$S/out" RB_LOCK="$S/lock.txt" FAKE_CMAKE_MOCKRT="$T/tools/claims-v3/ccheck/mockrt" FAKE_CMAKE_SLEEP_S=0
: > "$S/calls.log"; : > "$RB_LOCK"; : > "$S/dry-network.log"; rm -f "$S/ours-live.flag" "$S/race.flag"
fail=0; npass=0; ncase=0
ok() { ncase=$((ncase + 1)); if [ "$1" = "$2" ]; then npass=$((npass + 1)); echo "-> PASS ($3)"; else echo "-> FAIL ($3: got $1, want $2)"; fail=1; fi; }
step() { echo; echo "== $*"; }
san() { sed -e "s#$S#<scratch>#g"; }
nlog() { if [ -f "$RB_OUT/runbook.log" ]; then grep -c . "$RB_OUT/runbook.log"; else echo 0; fi; }
since() { tail -n +"$(( $1 + 1 ))" "$RB_OUT/runbook.log" 2>/dev/null; }   # the runbook log's lines after line $1
TODAY=$(TZ=America/Los_Angeles gdate +%F)
AT=$BOXT/build/e182-build-attempts.txt
builds() {  # step 6 v4's count: the day's starts less the jobs that read TRAIN-HOST-INPUTS-DIFFER
  if [ -f "$AT" ]; then echo $(( $(grep -c "^$TODAY .* a3-build-e182 started\$" "$AT") - $(grep -c "^$TODAY .* a3-build-e182 ended rc=[0-9]*: TRAIN-HOST-INPUTS-DIFFER" "$AT") )); else echo 0; fi
}
v3builds() { if [ -f "$AT" ]; then grep -c "^$TODAY " "$AT"; else echo 0; fi; }   # step 6 v3's count: every line of the day
fresh_day() {  # as on a new day: no count file, no build logs, the last job's status from an earlier day
  rm -f "$AT"; rm -rf "${BOXT:?}/build/e182-build-logs"
  for x in rc out; do [ -e "$J/a3-build-e182.$x" ] && touch -t "$(gdate -d '-2 day' +%Y%m%d%H%M)" "$J/a3-build-e182.$x"; done
  return 0
}
hostsha() { if [ -f "$BOXT/build/e182host/b/host/sparsity_host" ]; then sha256sum "$BOXT/build/e182host/b/host/sparsity_host" | cut -c1-16; else echo none; fi; }
pin_standins() {  # the stand-in box's harness-e182.json pins its 4 stand-in binaries (a sync puts the committed pins back)
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
}
leftovers() { pgrep -f "$S/boxbin/cmake|bash build/q141k/jobs/a3-build-e182[.]sh|tools/claims-v3/e182/build_host_e182_v2[.]sh|^sleep 90$" 2>/dev/null | grep -c .; }
v4() { bash "$R/s08_a3_preflight_e182_v4.sh" "$@"; }
v3() { bash "$R/s08_a3_preflight_e182_v3.sh" "$@"; }
waitv() {  # waitv <3|4> <out> [<max calls>]: step 6 v3's or v4's wait, again while it says 17; prints "<rc> <number of 17s>"
  local v=$1 o=$2 m=${3:-12} k r n17=0
  : > "$o"
  for k in $(seq 1 "$m"); do bash "$R/s08_a3_preflight_e182_v$v.sh" wait >> "$o" 2>&1; r=$?; [ "$r" -eq 17 ] || break; n17=$((n17 + 1)); done
  echo "$r $n17"
}
wait10() {  # wait10 <out> [--no-trains]: step 8 v2's wait, again while it says 17
  local o=$1 x=${2:-} k r
  for k in 1 2 3 4 5 6; do bash "$R/s10_a3_dry_e182_v2.sh" wait $x > "$o" 2>&1; r=$?; [ "$r" -eq 17 ] || break; done
  return "$r"
}
has() { grep -aq -- "$1" "$2" && echo 1 || echo 0; }
mtime() { gdate -r "$1" +%s 2>/dev/null || echo 0; }
killtree() {  # freeze the parent first (so the job never writes its exit status), then its children, then kill them all
  local p=$1 c kids; kids=$(pgrep -P "$p" 2>/dev/null); kill -STOP "$p" 2>/dev/null
  for c in $kids; do killtree "$c"; done; kill -KILL "$p" 2>/dev/null
}
cd "$T" || exit 2

step "A. the dry listing v4 (FULL and the fallback, the look before the post): every step exits 0, no ssh or rsync call"
: > "$S/calls.log"
bash "$R/list_steps_e182_v4.sh" "$S/dry-out" > "$S/dry-listing.txt" 2>&1; rc=$?
n=$(grep -c . "$S/calls.log"); tail -n 1 "$S/dry-listing.txt"
lp=$(awk '/s05_look_k6.sh aifoundry3$/ {l=NR} /the day.s one post, made AFTER the look/ {p=NR} END {print (l > 0 && p > l) ? 1 : 0}' "$S/dry-listing.txt")
v4n=$(grep -c '^################ tools/claims-v3/e182/rb/s08_a3_preflight_e182_v4.sh' "$S/dry-listing.txt"); c3=$(grep -c '^################ tools/claims-v3/e182/rb/s22_collect_e182_v3.sh' "$S/dry-listing.txt")
ok "$rc.$n.$lp.$v4n.$c3" "0.0.1.3.2" "A dry listing v4: 0 failing, no call, the look listed before the post, step 6 v4 three times and step 11 v3 twice"

step "K. step 2 v4 with no window in RB_OUT (s02 not run)"
: > "$S/calls.log"
RB_OUT="$S/out-nowindow" bash "$R/s03_desk_e182_v4.sh" > "$S/k.txt" 2>&1; rc=$?
grep -m1 -i 'no window' "$S/k.txt" | cut -c1-200; n=$(grep -c . "$S/calls.log")
ok "$rc.$n" "10.0" "K step 2 v4 refuses without step 1's window"

step "P1. step 2 v4 on the scratch repository (every listed file there, an origin, the stand-in note-3 list of 89)"
mkdir -p "$S/out-p"; RB_OUT="$S/out-p" bash "$R/s02_window_e182.sh" "$(gdate +%F)" 23:00 23:30 > /dev/null 2>&1
RB_OUT="$S/out-p" RB_E182_BASE=$BASE0 bash "$R/s03_desk_e182_v4.sh" > "$S/p1.txt" 2>&1; rc=$?
grep -E 'desk check v4|STOP' "$S/p1.txt" | cut -c1-330
pins=$(grep -c 'the five hash lists at their pinned counts (32, 79, 50, 49 and 89)' "$S/p1.txt")
ok "$rc.$pins" "0.1" "P1 step 2 v4 passes the intact tree at the pins 32, 79, 50, 49 and 89"

step "P2. note 3's list one line short (committed): step 2 v4, then step 2 v3, on the same tree"
sed -i '' -e '$d' "$T/tools/claims-v3/e182/SHA256SUMS-e182-note3"
$G commit -q -am "desk test: note 3's list one line short" || echo "the scratch commit failed"
RB_OUT="$S/out-p" RB_E182_BASE=$BASE0 bash "$R/s03_desk_e182_v4.sh" > "$S/p2-v4.txt" 2>&1; r4=$?
grep -m1 'STOP' "$S/p2-v4.txt" | cut -c1-260
k4=$(grep -c 'SHA256SUMS-e182-note3(88 OK of 88; pinned 89)' "$S/p2-v4.txt")
RB_OUT="$S/out-p" RB_E182_BASE=$BASE0 bash "$R/s03_desk_e182_v3.sh" > "$S/p2-v3.txt" 2>&1; r3=$?
grep -E 'desk check v3|STOP' "$S/p2-v3.txt" | cut -c1-260
k3=$(grep -c 'the four hash lists at their pinned counts (32, 79, 50 and 49)' "$S/p2-v3.txt")
$G reset -q --hard HEAD~1
ok "$r4.$k4.$r3.$k3" "16.1.0.1" "P2 step 2 v4 refuses note 3's short list against its pin (16); step 2 v3, which reads no note-3 list, passes it (0)"

# ---- the box's side, through the fake ssh
export RB_OUT="$S/out-b"; mkdir -p "$RB_OUT"
ls_=$(gdate -d '+30 min' +%H:%M); le_=$(gdate -d '+3 hour' +%H:%M)
bash "$R/s02_window_e182.sh" "$(gdate +%F)" "$ls_" "$le_" > "$S/b-window.txt" 2>&1 || { echo "the window failed: $(tail -2 "$S/b-window.txt")"; fail=1; }

step "S1. step 5 v2 on a clean stand-in box, its stand-in binaries and pins, then step 6 v4 start and wait (the fast stand-in cmake)"
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
pin_standins
n0=$(nlog)
v4 start > "$S/s1-start.txt" 2>&1; ra=$?
grep -E 'STOP|REFUSED|JOB-STARTED|runs on aifoundry3' "$S/s1-start.txt" | san | cut -c1-220
read -r rw n17 <<EOF2
$(waitv 4 "$S/s1-wait.txt")
EOF2
grep -aE '^E182-BUILD-ATTEMPT|^TRAIN-HOST-BUILT|^NOTE1 FILES OK|^HARNESS|^check_e182 rc|^preflight_e182 rc|^e182_common rc|STOP|aifoundry3: the train host built' "$S/s1-wait.txt" | sort -u | san | cut -c1-220
nreads=$(since "$n0" | grep -c 'step=s08_a3_preflight_v4_e182 class=read host=aifoundry3 bound=60s')
nany=$(since "$n0" | grep -c 'step=s08_a3_preflight_v4_e182 class=read ')
n13=$(since "$n0" | grep -c ' rc=13 ')
th=$([ -x "$BOXT/build/e182host/b/host/sparsity_host" ] && echo 1 || echo 0)
el=$(grep -c "^$TODAY .* a3-build-e182 ended rc=0: TRAIN-HOST-BUILT rc=0\$" "$AT" 2>/dev/null)
lg=$(grep -c '^BUILD OK' "$BOXT/build/e182-build-logs/$TODAY/e182-build-host-start1.txt" 2>/dev/null)
sed -e "s/^$TODAY /<today> /" "$AT" 2>/dev/null | sed 's/^/    count file: /'
ok "$rs.$ra.$rw.$nreads.$nany.$n13.$th.$(builds).$el.$lg" "0.0.0.5.5.0.1.1.1.1" "S1 step 6 v4 on the synced box: the build job, then the four checks, each in its own 60 s read (5 reads with the one before the build); no call past a bound; one build counted, its ended line and its own log kept"

step "S2. step 8 v2 (the trains' dry pass) on the box step 6 v4 left"
: > "$S/dry-network.log"
bash "$R/s10_a3_dry_e182_v2.sh" start > "$S/s2-start.txt" 2>&1; r1=$?
wait10 "$S/s2-wait.txt"; r2=$?
grep -aE '^E182 dry|^E182 start gate' "$S/s2-wait.txt" | sort -u | cut -c1-200
k1=$(has '^E182 dry 18220 rc=0' "$S/s2-wait.txt"); k2=$(has '^E182 dry 18215 rc=0' "$S/s2-wait.txt")
k3=$(has '^E182 dry 18201 --smoke rc=0' "$S/s2-wait.txt"); k4=$(has '^E182 start gate rc=8' "$S/s2-wait.txt")
nw=$(grep -c . "$S/dry-network.log")
ok "$r1.$r2.$k1.$k2.$k3.$k4.$nw" "0.0.1.1.1.1.0" "S2 job a3-dry-e182 rc 0 with the host step 6 v4 built: 18220 0, 18215 0, the smoke 0, the start gate 8; no network call from the box"

step "X3. (minor 2) a second start after the good build: step 6 v4 refuses it; wait reads the checks again"
hs0=$(hostsha); js0=$(mtime "$J/a3-build-e182.sh"); b0=$(builds)
v4 start > "$S/x3-start.txt" 2>&1; ra=$?
grep -m1 'STOP' "$S/x3-start.txt" | cut -c1-260
q=$(has 'REFUSED: the train host was built on aifoundry3 today' "$S/x3-start.txt")
read -r rw n17 <<EOF2
$(waitv 4 "$S/x3-wait.txt")
EOF2
grep -a 'aifoundry3: the train host built' "$S/x3-wait.txt" | head -n 1 | cut -c1-200
ok "$ra.$q.$([ "$(hostsha)" = "$hs0" ] && echo same).$([ "$(mtime "$J/a3-build-e182.sh")" = "$js0" ] && echo same).$(builds).$rw" "10.1.same.same.$b0.0" "X3 step 6 v4 refuses a second start after a good build (10): no job, the host unchanged, the count unchanged; wait reads its checks again (0)"
step "X3v. the fault shown: step 6 v3 after a good build of its own (its count from a fresh file), then a second start whose build fails"
rm -f "$AT"
v3 start > "$S/x3v-1.txt" 2>&1; r1=$?
read -r w1 n17 <<EOF2
$(waitv 3 "$S/x3v-1w.txt")
EOF2
hs1=$(hostsha)
env FAKE_CMAKE_FAIL=build bash "$R/s08_a3_preflight_e182_v3.sh" start > "$S/x3v-2.txt" 2>&1; r2=$?
read -r w2 n17 <<EOF2
$(waitv 3 "$S/x3v-2w.txt")
EOF2
grep -a 'STOP' "$S/x3v-2w.txt" | tail -n 1 | cut -c1-260
fb=$(has "it was the day's build 2 (the first and its one re-run are spent): no train runs today" "$S/x3v-2w.txt")
ok "$r1.$w1.$([ "$hs1" != none ] && echo built).$r2.$w2.$fb.$(hostsha)" "0.0.built.0.16.1.none" "X3v step 6 v3 starts a second build after a good one (0, not refused); when it fails the good host is gone and the fallback is named (16)"

step "X2. (minor 1) main.cpp off its pin on the box: step 6 v4's read before the build"
fresh_day
printf '// changed on the box (desk test)\n' >> "$BOXT/workloads/sparsity/host/main.cpp"
js0=$(mtime "$J/a3-build-e182.sh")
v4 start > "$S/x2.txt" 2>&1; ra=$?
grep -aE '^BUILD INPUTS|host/main.cpp|STOP' "$S/x2.txt" | san | cut -c1-260
m=$(has "are not the pinned ones (the lines above), so nothing was built and no build is counted: run step 5 v2 (rb/s07_a3_sync_e182_v2.sh) once more, then this step's start" "$S/x2.txt")
d=$(has 'BUILD INPUTS DIFFER' "$S/x2.txt"); nl=$(grep -c "^$TODAY .* a3-build-e182 not started: TRAIN-HOST-INPUTS-DIFFER" "$AT" 2>/dev/null)
ok "$ra.$m.$d.$([ "$(mtime "$J/a3-build-e182.sh")" = "$js0" ] && echo same).$(builds).$nl" "16.1.1.same.0.1" "X2 step 6 v4 reads TRAIN-HOST-INPUTS-DIFFER before any job (16) with note 1's words: no job, no build counted, the event in the count file"
step "X2v. the fault shown: step 6 v3 on the same box (its count from a fresh file)"
rm -f "$AT"
v3 start > "$S/x2v-1.txt" 2>&1; r1=$?
read -r w1 n17 <<EOF2
$(waitv 3 "$S/x2v-1w.txt")
EOF2
grep -a 'STOP' "$S/x2v-1w.txt" | tail -n 1 | cut -c1-260
rr=$(has 'build 1 of at most 2 today): run this step.s start once more (the one re-run)' "$S/x2v-1w.txt"); s5=$(grep -c 'step 5' "$S/x2v-1w.txt")
ok "$r1.$w1.$rr.$s5.$(v3builds)" "0.16.1.0.1" "X2v step 6 v3 passes its read, builds, reads the copy's main.cpp as a failed build (16), spends the day's first build and names no step 5"
step "X2r. step 5 v2 sends main.cpp back; step 6 v4 then builds"
fresh_day
bash "$R/s07_a3_sync_e182_v2.sh" > "$S/x2r-sync.txt" 2>&1; rs=$?
grep -E 'synced to' "$S/x2r-sync.txt" | san | cut -c1-200
sw=$(has ', 1 of them under workloads/sparsity/' "$S/x2r-sync.txt")
pin_standins > /dev/null
v4 start > "$S/x2r-start.txt" 2>&1; ra=$?
read -r rw n17 <<EOF2
$(waitv 4 "$S/x2r-wait.txt")
EOF2
ok "$rs.$sw.$ra.$rw.$(builds).$([ "$(hostsha)" != none ] && echo built)" "0.1.0.0.1.built" "X2r step 5 v2 sends the one workload file back, then step 6 v4 builds (0), one build counted"

step "X2b. the race: main.cpp changes after the read before the build and before the job copies it (the stand-in timeout, once)"
fresh_day
touch "$S/race.flag"
v4 start > "$S/x2b-start.txt" 2>&1; ra=$?
read -r rw n17 <<EOF2
$(waitv 4 "$S/x2b-wait.txt")
EOF2
grep -aE '^TRAIN-HOST-INPUTS-DIFFER|STOP' "$S/x2b-wait.txt" | san | cut -c1-260
m=$(has "were not the pinned ones when the build job copied them (the lines above), so nothing was built and no build is counted: run step 5 v2 (rb/s07_a3_sync_e182_v2.sh) once more, then this step's start" "$S/x2b-wait.txt")
ne=$(grep -c "^$TODAY .* a3-build-e182 ended rc=1: TRAIN-HOST-INPUTS-DIFFER" "$AT" 2>/dev/null); b1=$(builds); fl=$([ -e "$S/race.flag" ] && echo left || echo used)
bash "$R/s07_a3_sync_e182_v2.sh" > "$S/x2b-sync.txt" 2>&1; rs=$?
pin_standins > /dev/null
v4 start > "$S/x2b-start2.txt" 2>&1; ra2=$?
read -r rw2 n17 <<EOF2
$(waitv 4 "$S/x2b-wait2.txt")
EOF2
ok "$ra.$rw.$m.$ne.$b1.$fl.$rs.$ra2.$rw2.$(builds)" "0.16.1.1.0.used.0.0.0.1" "X2b the job's own check finds the change: TRAIN-HOST-INPUTS-DIFFER, note 1's words (16), not counted (0 builds); step 5 v2, then step 6 v4 builds, one build counted"

step "V4S. the 90 s stand-in cmake under step 6 v4: start, a second start while it runs, then wait (30 s waits, 17 while it runs)"
fresh_day
n0=$(nlog)
env FAKE_CMAKE_SLEEP_S=90 bash "$R/s08_a3_preflight_e182_v4.sh" start > "$S/v4s-start.txt" 2>&1; ra=$?
grep -E 'STOP|JOB-STARTED|runs on aifoundry3' "$S/v4s-start.txt" | san | cut -c1-200
v4 start > "$S/v4s-start2.txt" 2>&1; rb2=$?
grep -m1 'STOP' "$S/v4s-start2.txt" | cut -c1-220
rj=$(has 'runbook job(s) still run on aifoundry3' "$S/v4s-start2.txt"); b1=$(builds)
read -r rw n17 <<EOF2
$(export RB_WAIT_LOOP_S=30; waitv 4 "$S/v4s-wait.txt" 12)
EOF2
grep -aE '^E182-BUILD-ATTEMPT|^build_host_e182_v2 rc|^TRAIN-HOST-BUILT|^HARNESS|^preflight_e182 rc|^e182_common rc|STOP|the dry pass a3-build-e182 still runs|aifoundry3: the train host built' "$S/v4s-wait.txt" | sed -e 's/after [0-9]* s/after <n> s/' -e "s#$TODAY#<today>#" | sort | uniq -c | san | cut -c1-220
span=$(/usr/bin/python3 -B - "$J/a3-build-e182.out" <<'PY'
import re, sys, datetime
s = open(sys.argv[1]).read()
b = re.search(r"JOB-BEGIN \S+ (\S+ \S+)", s); e = re.search(r"JOB-END \S+ rc=\d+ (\S+ \S+)", s)
f = "%Y-%m-%d %H:%M:%S"
print(int((datetime.datetime.strptime(e.group(1), f) - datetime.datetime.strptime(b.group(1), f)).total_seconds()) if b and e else -1)
PY
)
nreads=$(since "$n0" | grep -c 'step=s08_a3_preflight_v4_e182 class=read host=aifoundry3 bound=60s')
nany=$(since "$n0" | grep -c 'step=s08_a3_preflight_v4_e182 class=read ')
nwait=$(since "$n0" | grep -c 'step=s08_a3_preflight_v4_e182 class=wait host=aifoundry3 bound=600s')
n13=$(since "$n0" | grep -c ' rc=13 ')
long=$([ "$span" -ge 90 ] && echo 1 || echo 0); some17=$([ "$n17" -ge 1 ] && echo 1 || echo 0)
echo "the job took $span s; step 6 v4's waits: $nwait ($n17 said 17); its reads: $nany, $nreads of them bounded at 60 s (the two starts' and the four checks'); calls past a bound: $n13"
ok "$ra.$rb2.$rj.$b1.$rw.$some17.$long.$nreads.$nany.$n13.$(builds)" "0.10.1.1.0.1.1.6.6.0.1" "V4S step 6 v4 passes the 90 s build: one job (a second start refused while it runs), waits that say 17, then the four checks in 60 s reads; nothing past a bound"

step "O. a card session of ours on the box (the stand-in pgrep reports one): start, the fallback, then wait's checks"
touch "$S/ours-live.flag"
b0=$(builds); js0=$(mtime "$J/a3-build-e182.sh")
: > "$S/calls.log"
v4 start > "$S/o1.txt" 2>&1; r1=$?; c1=$(grep -c '^ssh ' "$S/calls.log")
v4 --no-trains > "$S/o2.txt" 2>&1; r2=$?
v4 wait > "$S/o3.txt" 2>&1; r3=$?
rm -f "$S/ours-live.flag"
for f in o1 o2 o3; do grep -m1 'STOP' "$S/$f.txt" | cut -c1-200; done
q1=$(has 'REFUSED: a card session of ours runs on aifoundry3' "$S/o1.txt"); q2=$(has 'REFUSED: a card session of ours runs on aifoundry3' "$S/o2.txt"); q3=$(has 'REFUSED: a card session of ours runs on aifoundry3' "$S/o3.txt")
ok "$r1.$q1.$c1.$r2.$q2.$r3.$q3.$([ "$(builds)" = "$b0" ] && echo same).$([ "$(mtime "$J/a3-build-e182.sh")" = "$js0" ] && echo same)" "10.1.2.10.1.10.1.same.same" "O each refused (10) beside a session of ours, the start after its probe and one read, no build started or counted"

step "R1. the re-run rule: a fresh day, the stand-in build fails (FAKE_CMAKE_FAIL=build): the first failure"
fresh_day
env FAKE_CMAKE_FAIL=build bash "$R/s08_a3_preflight_e182_v4.sh" start > "$S/r1-start.txt" 2>&1; ra=$?
read -r rw n17 <<EOF2
$(waitv 4 "$S/r1-wait.txt")
EOF2
grep -a 'STOP' "$S/r1-wait.txt" | tail -n 1 | cut -c1-260
m1=$(has "the train host's build failed on aifoundry3 (the lines above; build 1 of at most 2 today): run this step's start once more (the one re-run)" "$S/r1-wait.txt")
f1=$(has '^TRAIN-HOST-BUILD-FAILED' "$S/r1-wait.txt")
th=$([ -e "$BOXT/build/e182host/b/host/sparsity_host" ] || [ -e "$BOXT/build/e182host/SHA256" ] && echo 1 || echo 0)
ok "$ra.$rw.$f1.$m1.$th.$(builds)" "0.16.1.1.0.1" "R1 the first failed build: 16, one re-run asked for, no train host or record left, one build counted"
step "R2. the one re-run fails too"
env FAKE_CMAKE_FAIL=build bash "$R/s08_a3_preflight_e182_v4.sh" start > "$S/r2-start.txt" 2>&1; ra=$?
read -r rw n17 <<EOF2
$(waitv 4 "$S/r2-wait.txt")
EOF2
grep -a 'STOP' "$S/r2-wait.txt" | tail -n 1 | cut -c1-330
m2=$(has "it was the day's build 2 (the first and its one re-run are spent): no train runs today: run step 6 v4 with --no-trains (rb/s08_a3_preflight_e182_v4.sh --no-trains), then step 8 v2 with --no-trains (rb/s10_a3_dry_e182_v2.sh start --no-trains, then wait --no-trains), then step 9 v2 PASSES no (rb/s11_a3_session_e182_v2.sh PASSES no)" "$S/r2-wait.txt")
ok "$ra.$rw.$m2.$(builds)" "0.16.1.2" "R2 the second failed build: 16, the fallback's three steps named, two builds counted"
step "R3. a third start"
js0=$(mtime "$J/a3-build-e182.sh")
v4 start > "$S/r3.txt" 2>&1; r3=$?
grep -m1 'STOP' "$S/r3.txt" | cut -c1-330
m3=$(has "two train-host builds were started on aifoundry3 today (the first and its one re-run): no third. no train runs today: run step 6 v4 with --no-trains" "$S/r3.txt")
ok "$r3.$m3.$(builds).$([ "$(mtime "$J/a3-build-e182.sh")" = "$js0" ] && echo same)" "16.1.2.same" "R3 no third build: 16, the fallback named, no job started"
step "R4. the fallback runs: step 6 v4 --no-trains, then step 8 v2 --no-trains"
v4 --no-trains > "$S/r4a.txt" 2>&1; ra=$?
grep -aE '^HARNESS|^preflight_e182 rc|^e182_common rc|STOP|the trains off' "$S/r4a.txt" | sort -u | cut -c1-200
h70=$(has '^HARNESS OK: 70 files' "$S/r4a.txt")
: > "$S/dry-network.log"
bash "$R/s10_a3_dry_e182_v2.sh" start --no-trains > "$S/r4b.txt" 2>&1; rb_=$?
wait10 "$S/r4c.txt" --no-trains; rc_=$?
grep -aE '^E182 dry|^E182 start gate' "$S/r4c.txt" | sort -u | cut -c1-200
k1=$(has '^E182 dry 18220 rc=0' "$S/r4c.txt"); k2=$(has '^E182 dry 18201 --smoke trains=no rc=0' "$S/r4c.txt"); k3=$(has '^E182 start gate rc=8' "$S/r4c.txt")
nw=$(grep -c . "$S/dry-network.log")
ok "$ra.$h70.$rb_.$rc_.$k1.$k2.$k3.$nw" "0.1.0.0.1.1.1.0" "R4 the fallback: step 6 v4 --no-trains 0 (HARNESS OK 70, GO, verify), step 8 v2 --no-trains job rc 0 (18220 0, the smoke trains=no 0, the gate 8); no network call"

step "C. (nit 5) step 11 v3 on the fallback day's box (two failed builds): the day's step-6 record copied back"
for d in e182/p18220 e182-smoke/p18201 e182-stoptest/p18202; do mkdir -p "$BOXT/build/claims-v3/aifoundry3/$d"; echo '{"status":"desk test"}' > "$BOXT/build/claims-v3/aifoundry3/$d/block.json"; done
mkdir -p "$BOXT/build/e182"; echo "a stand-in session log (desk test)" > "$BOXT/build/e182/session.log"
printf '#!/bin/bash\n# desk-test stand-in for collect_e182.sh: the output directory only\nmkdir -p "build/e182-out/${E182_DATE}-e182-one-number-r2-aifoundry3/ccheck"\necho "results.md written (desk-test stand-in)"\n' > "$S/collect-standin.sh"
chmod +x "$S/collect-standin.sh"
RL=$T/build/e182-raw/logs
rm -rf "$T/build/e182-raw" "$T/build/e182-out"
RB_DESKTEST=1 K6E182_COLLECT="$S/collect-standin.sh" bash "$R/s22_collect_e182_v3.sh" > "$S/c.txt" 2>&1; rc=$?
grep -E 'absent on the box|STOP' "$S/c.txt" | san | cut -c1-240
at=$([ -f "$RL/e182-build-attempts.txt" ] && echo "$(grep -c "^$TODAY .* a3-build-e182 started\$" "$RL/e182-build-attempts.txt")s$(grep -c "^$TODAY .* a3-build-e182 ended rc=1: TRAIN-HOST-BUILD-FAILED" "$RL/e182-build-attempts.txt")f" || echo none)
l1=$(has 'fake cmake: the build fails' "$RL/e182-build-host-start1.txt"); l2=$(has 'fake cmake: the build fails' "$RL/e182-build-host-start2.txt")
ab=$(grep -c 'absent on aifoundry3 at collection: aifoundry/build/e182host/SHA256' "$RL/absent-on-box.txt" 2>/dev/null)
sl=$([ -s "$RL/session.log" ] && echo 1 || echo 0); gl=$(grep -c 'a session that must carry a C log' "$S/c.txt")
ls "$RL" | sed 's/^/    raw logs: /'
ok "$rc.$at.$l1.$l2.$ab.$sl.$gl" "14.2s2f.1.1.1.1.1" "C step 11 v3 copies the count file (2 starts, 2 failed builds) and both builds' own logs into the raw logs, names the absent record, copies the session log, and goes on to the C-session gate (14 here by design)"
step "Cv. the nit shown: step 11 v2 on the same box"
rm -rf "$T/build/e182-raw" "$T/build/e182-out"
RB_DESKTEST=1 K6E182_COLLECT="$S/collect-standin.sh" bash "$R/s22_collect_e182_v2.sh" > "$S/cv.txt" 2>&1; rv=$?
av=$([ -f "$RL/e182-build-attempts.txt" ] && echo 1 || echo 0); lv=$(ls "$RL" 2>/dev/null | grep -c '^e182-build-host-start'); bv=$([ -s "$RL/e182-build-host.txt" ] && echo 1 || echo 0)
ok "$rv.$av.$lv.$bv" "14.0.0.1" "Cv step 11 v2 copies neither the count file nor the first build's log: only the last build's log (build/e182-build-host.txt)"
rm -rf "${BOXT:?}/build/claims-v3/aifoundry3" "$T/build/e182-raw" "$T/build/e182-out"

step "T. the build past its own bound: E182_BUILD_S=5 (RB_DESKTEST=1), the 90 s stand-in cmake, a fresh day"
fresh_day
: > "$S/calls.log"
env E182_BUILD_S=5 bash "$R/s08_a3_preflight_e182_v4.sh" start > "$S/t0.txt" 2>&1; r0=$?; c0=$(grep -c . "$S/calls.log")
grep -m1 'STOP' "$S/t0.txt" | cut -c1-200
env RB_DESKTEST=1 E182_BUILD_S=5 FAKE_CMAKE_SLEEP_S=90 bash "$R/s08_a3_preflight_e182_v4.sh" start > "$S/t1.txt" 2>&1; ra=$?
read -r rw n17 <<EOF2
$(waitv 4 "$S/t1-wait.txt")
EOF2
grep -aE '^TRAIN-HOST-BUILD-OVERRAN|^build_host_e182_v2 rc' "$S/t1-wait.txt" | sed 's#its log on the box: .*#its log on the box: <...>#' | sort -u | cut -c1-200; grep -a 'STOP' "$S/t1-wait.txt" | tail -n 1 | cut -c1-260
o1=$(has '^TRAIN-HOST-BUILD-OVERRAN rc=124' "$S/t1-wait.txt"); m1=$(has "the train host's build ran past its own 5 s bound on aifoundry3 (the lines above; build 1 of at most 2 today)" "$S/t1-wait.txt")
sleep 1; lt=$(leftovers)
ok "$r0.$c0.$ra.$rw.$o1.$m1.$(builds).$lt" "10.0.0.16.1.1.1.0" "T E182_BUILD_S without RB_DESKTEST refused (10, no call); the build past its own bound reads OVERRAN rc 124 and asks for one re-run (16); nothing left running"

step "L. a lost job: a fresh day, the 90 s stand-in cmake, the job's processes killed on the stand-in box mid-build"
fresh_day
env FAKE_CMAKE_SLEEP_S=90 bash "$R/s08_a3_preflight_e182_v4.sh" start > "$S/l1.txt" 2>&1; ra=$?
sleep 3
jp=$(cat "$J/a3-build-e182.pid" 2>/dev/null)
[ -n "$jp" ] && killtree "$jp"
sleep 1
read -r rw n17 <<EOF2
$(waitv 4 "$S/l1-wait.txt")
EOF2
grep -aE '^JOB-LOST' "$S/l1-wait.txt" | head -n 1 | cut -c1-200; grep -a 'STOP' "$S/l1-wait.txt" | tail -n 1 | cut -c1-260
lo=$(has '^JOB-LOST a3-build-e182' "$S/l1-wait.txt"); m1=$(has "the train host's build job was lost (no process and no exit status) on aifoundry3 (the lines above; build 1 of at most 2 today)" "$S/l1-wait.txt")
kl=$(has '^BUILD INPUTS OK: 9 files' "$BOXT/build/e182-build-logs/$TODAY/e182-build-host-start1.txt")   # how far the lost build got: its copy checked
sleep 1
ok "$ra.$rw.$lo.$m1.$(builds).$kl" "0.16.1.1.1.1" "L the lost job: JOB-LOST, one re-run asked for (16), one build counted, the lost build's own log kept on the box"

step "Z. no process of this test left running"
sleep 1
z=$(pgrep -f "$S/" 2>/dev/null | grep -v "^$$\$" | grep -c .)
zs=$(leftovers)
ok "$z.$zs" "0.0" "Z nothing of this test's stand-in box or builds left running"

echo
echo "SELFTEST-RB-E182-V4 $npass of $ncase $([ "$fail" -eq 0 ] && echo PASS || echo FAIL)"
exit "$fail"
