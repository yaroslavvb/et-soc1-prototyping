#!/usr/bin/env bash
# E182 (Q155, the kit's dated note 4): the desk test of note 4's steps with a FAKE ssh and rsync, on note 1's stand-in box (its setup is note 3's
# desk test's, rb/selftest_rb_e182_v4.sh, which stays as committed, with five changes: the stand-ins for note 4's list and log instead of note
# 3's; every file of note 3's committed list copied into the scratch repository; the stand-in ssh's network cut; v5, netcut, jobend and
# stopline). Stand-in ssh and rsync sit first on PATH and serve a stand-in box (a local directory laid out like aifoundry3's ~/aifoundry); they
# refuse any other host, and no lab box is reached. Everything runs in <scratch dir> (never the lab clone). The bounds are rb_run.py's own:
# this test sets no RB_<CLS>_S (it refuses to start if one is set). THE NETWORK CUT: while <scratch>/ssh-fail-at holds k, the k-th remote
# script call from now fails as a dropped connection does (ssh's exit 255, nothing on stdout); the probe never counts. It is verify-q154k's
# fail-once stand-in (its jobs/j2_e182_netfault.sh) with a count. Each fault note 3's verifier found is shown under step 6 v4 (a case ending
# in v), then its fix under step 6 v5. The cases:
#   A   the dry listing v5 (both paths, the look before the post): every step exits 0, the stand-ins see no ssh or rsync call;
#   K   step 2 v5 with no window in RB_OUT refuses (10), and no call is made;
#   P1  step 2 v5 on a scratch repository that holds every file the six lists name (with an origin, so the pull runs): 0, at the pins
#       32, 79, 50, 49, 89 and 19 (a stand-in note-4 list of 19 of the scratch's files: note 4's own list is written after this test's log);
#   P2  note 4's list one line short: step 2 v5 refuses (16) naming it against its pin 19; step 2 v4 passes the same tree (0);
#   S1  step 5 v2 on a clean stand-in box, its stand-in binaries and pins, then step 6 v5 start and wait (the fast stand-in cmake): 0, five
#       60 s reads, one build counted;
#   X3  a second start after that good build: refused (10), as in v4;
#   N1  (critic-q154's nit 2) the wait call cut while the first build runs: 14, "no reading of the build job", nothing counted, no re-run
#       or fallback named; then wait reads the good build (0), and a start after it is refused (10);
#   N1b the wait call cut after the first build ended good: 14 "no reading"; wait then reads it (0); a start is refused (10);
#   N2  (verify-q154k's fault 1) the first build fails (16, one re-run); the re-run runs; its wait call is cut: 14 "no reading", the fallback
#       NOT named; --no-trains refused while the job runs (10), and refused again after the re-run's good build (10, the good-build
#       refusal); wait reads the good build (0); N2v, the fault shown: step 6 v4 on the same sequence names the fallback (16) on the cut
#       wait, and its --no-trains passes (0) beside the good host;
#   N4  the same with the re-run already ended good when its wait call is cut: 14, --no-trains refused (10), wait 0; N4v: v4 names the
#       fallback (16) and its --no-trains passes at once (0);
#   N6  (found by fix-q154k, the same kind) the first check's read after a good build is cut: 14, "no reading of inputs", then wait 0;
#       N6v: v4 reads the cut read as a failed check, 16, "a binary or file differs: a dated amendment first";
#   O   a card session of ours on the box (the stand-in pgrep reports one): start, the fallback and wait each refused (10);
#   R1-R4  the re-run rule with two REAL failed builds (the stand-in build fails): one re-run asked for (16); the second names the fallback
#       (16, step 6 v5 --no-trains); a third start refused (16); the fallback: --no-trains with its first read cut (14, no reading), then
#       --no-trains (0, HARNESS OK 70) and step 8 v2 --no-trains (job a3-dry-e182-nt rc 0);
#   L   a lost job (its processes killed mid-build): JOB-LOST is still a build's failure: one re-run asked for (16), one build counted;
#   Z   no process of this test is left running.
#
#   bash tools/claims-v3/e182/rb/selftest_rb_e182_v5.sh <scratch dir> > <log>
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
# every file the five committed lists name (the kit's and note 3's lists name a few outside these directories), so step 2 can check them here
for l in SHA256SUMS-e182-registration SHA256SUMS-e182-kit SHA256SUMS-e182-note1 SHA256SUMS-e182-note2 SHA256SUMS-e182-note3; do
  awk '{print $2}' "$SRC/tools/claims-v3/e182/$l" | while IFS= read -r f; do
    [ -e "$T/$f" ] || { mkdir -p "$T/$(dirname "$f")"; cp -p "$SRC/$f" "$T/$f"; }
  done
done
# P1's stand-ins, written before the scratch commit: note 4's desk-test log (this test's own log is being written now) and a note-4 list
# of 19 of the scratch's files at their sha256 (note 4's own list is made after this test and holds its log)
rm -f "$T/tools/claims-v3/e182/SHA256SUMS-e182-note4"
printf 'SELFTEST-RB-E182-V5 0 of 0 PASS (a stand-in written by the v5 desk test for its case P1: this log is being written)\n' > "$T/tools/claims-v3/e182/logs/selftest-rb-e182-v5.txt"
( cd "$T" && find tools/claims-v3/e182 -type f ! -name 'SHA256SUMS-e182-note4' | LC_ALL=C sort | head -n 19 | while IFS= read -r f; do sha256sum "$f"; done ) > "$S/note4-standin.txt"
cp "$S/note4-standin.txt" "$T/tools/claims-v3/e182/SHA256SUMS-e182-note4"
G="git -C $T -c user.name=e182-desktest -c user.email=desktest@localhost -c core.hooksPath=/dev/null -c commit.gpgsign=false"
$G init -q && $G add -A && $G commit -q -m "E182 runbook v5 desk test: the lab files the steps read" || { echo "the scratch repository failed"; exit 2; }
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
# v5's cases: while <scratch>/ssh-fail-at holds k, the k-th remote script call from now fails as a dropped connection does: exit 255,
# nothing printed on stdout (its script is read and dropped first); the counter counts every other script call down
if [ -s "$S/ssh-fail-at" ]; then k=\$(cat "$S/ssh-fail-at"); if [ "\$k" -le 1 ]; then rm -f "$S/ssh-fail-at"; cat > /dev/null; echo "ssh: connection to \$host closed (desk-test stand-in)" >&2; exit 255; fi; echo \$((k - 1)) > "$S/ssh-fail-at"; fi
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
: > "$S/calls.log"; : > "$RB_LOCK"; : > "$S/dry-network.log"; rm -f "$S/ours-live.flag" "$S/race.flag" "$S/ssh-fail-at"
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
v5() { bash "$R/s08_a3_preflight_e182_v5.sh" "$@"; }
netcut() { echo "${1:-1}" > "$S/ssh-fail-at"; }   # the ${1:-1}-th remote script call from now is cut (exit 255, no output)
jobend() {  # wait (bounded, 150 s) for the stand-in box's build job to write its exit status, without calling the runbook
  local k; for k in $(seq 1 150); do [ -e "$J/a3-build-e182.rc" ] && return 0; sleep 1; done; echo "the build job did not end in 150 s"; return 1
}
stopline() { grep -a 'STOP' "$1" | tail -n 1 | cut -c1-330; }
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

step "A. the dry listing v5 (FULL and the fallback, the look before the post): every step exits 0, no ssh or rsync call"
: > "$S/calls.log"
bash "$R/list_steps_e182_v5.sh" "$S/dry-out" > "$S/dry-listing.txt" 2>&1; rc=$?
n=$(grep -c . "$S/calls.log"); tail -n 1 "$S/dry-listing.txt"
lp=$(awk '/s05_look_k6.sh aifoundry3$/ {l=NR} /the day.s one post, made AFTER the look/ {p=NR} END {print (l > 0 && p > l) ? 1 : 0}' "$S/dry-listing.txt")
v5n=$(grep -c '^################ tools/claims-v3/e182/rb/s08_a3_preflight_e182_v5.sh' "$S/dry-listing.txt"); s5=$(grep -c '^################ tools/claims-v3/e182/rb/s03_desk_e182_v5.sh' "$S/dry-listing.txt")
ok "$rc.$n.$lp.$v5n.$s5" "0.0.1.3.1" "A dry listing v5: 0 failing, no call, the look listed before the post, step 6 v5 three times and step 2 v5 once"

step "K. step 2 v5 with no window in RB_OUT (s02 not run)"
: > "$S/calls.log"
RB_OUT="$S/out-nowindow" bash "$R/s03_desk_e182_v5.sh" > "$S/k.txt" 2>&1; rc=$?
grep -m1 -i 'no window' "$S/k.txt" | cut -c1-200; n=$(grep -c . "$S/calls.log")
ok "$rc.$n" "10.0" "K step 2 v5 refuses without step 1's window"

step "P1. step 2 v5 on the scratch repository (every listed file there, an origin, the stand-in note-4 list of 19)"
mkdir -p "$S/out-p"; RB_OUT="$S/out-p" bash "$R/s02_window_e182.sh" "$(gdate +%F)" 23:50 23:55 > /dev/null 2>&1
RB_OUT="$S/out-p" RB_E182_BASE=$BASE0 bash "$R/s03_desk_e182_v5.sh" > "$S/p1.txt" 2>&1; rc=$?
grep -E 'desk check v5|STOP' "$S/p1.txt" | cut -c1-330
pins=$(grep -c 'the six hash lists at their pinned counts (32, 79, 50, 49, 89 and 19)' "$S/p1.txt")
ok "$rc.$pins" "0.1" "P1 step 2 v5 passes the intact tree at the pins 32, 79, 50, 49, 89 and 19"

step "P2. note 4's list one line short (committed): step 2 v5, then step 2 v4, on the same tree"
sed -i '' -e '$d' "$T/tools/claims-v3/e182/SHA256SUMS-e182-note4"
$G commit -q -am "desk test: note 4's list one line short" || echo "the scratch commit failed"
RB_OUT="$S/out-p" RB_E182_BASE=$BASE0 bash "$R/s03_desk_e182_v5.sh" > "$S/p2-v5.txt" 2>&1; r5=$?
grep -m1 'STOP' "$S/p2-v5.txt" | cut -c1-260
k5=$(grep -c 'SHA256SUMS-e182-note4(18 OK of 18; pinned 19)' "$S/p2-v5.txt")
RB_OUT="$S/out-p" RB_E182_BASE=$BASE0 bash "$R/s03_desk_e182_v4.sh" > "$S/p2-v4.txt" 2>&1; r4=$?
grep -E 'desk check v4|STOP' "$S/p2-v4.txt" | cut -c1-260
k4=$(grep -c 'the five hash lists at their pinned counts (32, 79, 50, 49 and 89)' "$S/p2-v4.txt")
$G reset -q --hard HEAD~1
ok "$r5.$k5.$r4.$k4" "16.1.0.1" "P2 step 2 v5 refuses note 4's short list against its pin (16); step 2 v4, which reads no note-4 list, passes it (0)"

# ---- the box's side, through the fake ssh
export RB_OUT="$S/out-b"; mkdir -p "$RB_OUT"
# the window: the last start 30 minutes from now and the last end 3 hours from now, on one Pacific day (after 21:00 the day is tomorrow's,
# and its last start 00:00 if the two times would straddle midnight: s02 takes one day)
wd=$(gdate -d '+3 hour' +%F); le_=$(gdate -d '+3 hour' +%H:%M)
if [ "$(gdate -d '+30 min' +%F)" = "$wd" ]; then ls_=$(gdate -d '+30 min' +%H:%M); else ls_=00:00; fi
bash "$R/s02_window_e182.sh" "$wd" "$ls_" "$le_" > "$S/b-window.txt" 2>&1 || { echo "the window failed: $(tail -2 "$S/b-window.txt")"; fail=1; }

step "S1. step 5 v2 on a clean stand-in box, its stand-in binaries and pins, then step 6 v5 start and wait (the fast stand-in cmake)"
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
v5 start > "$S/s1-start.txt" 2>&1; ra=$?
grep -E 'STOP|REFUSED|JOB-STARTED|runs on aifoundry3' "$S/s1-start.txt" | san | cut -c1-220
read -r rw n17 <<EOF2
$(waitv 5 "$S/s1-wait.txt")
EOF2
grep -aE '^E182-BUILD-ATTEMPT|^TRAIN-HOST-BUILT|^NOTE1 FILES OK|^HARNESS|^check_e182 rc|^preflight_e182 rc|^e182_common rc|STOP|aifoundry3: the train host built' "$S/s1-wait.txt" | sort -u | san | cut -c1-220
nreads=$(since "$n0" | grep -c 'step=s08_a3_preflight_v5_e182 class=read host=aifoundry3 bound=60s')
n13=$(since "$n0" | grep -c ' rc=13 ')
th=$([ -x "$BOXT/build/e182host/b/host/sparsity_host" ] && echo 1 || echo 0)
ok "$rs.$ra.$rw.$nreads.$n13.$th.$(builds)" "0.0.0.5.0.1.1" "S1 step 6 v5 on the synced box: the build job, then the four checks, each in its own 60 s read (5 reads with the one before the build); no call past a bound; one build counted"

step "X3. a second start after the good build: refused (v4's refusal, kept)"
hs0=$(hostsha)
v5 start > "$S/x3.txt" 2>&1; ra=$?; stopline "$S/x3.txt"
q=$(has 'REFUSED: the train host was built on aifoundry3 today' "$S/x3.txt")
ok "$ra.$q.$([ "$(hostsha)" = "$hs0" ] && echo same).$(builds)" "10.1.same.1" "X3 step 6 v5 refuses a second start after a good build (10), the host unchanged, the count unchanged"

step "N1. (critic-q154's nit 2) the wait call cut (exit 255) while the first build runs"
fresh_day
env FAKE_CMAKE_SLEEP_S=25 bash "$R/s08_a3_preflight_e182_v5.sh" start > "$S/n1-start.txt" 2>&1; ra=$?
netcut 1
v5 wait > "$S/n1-wait.txt" 2>&1; rw=$?; stopline "$S/n1-wait.txt"
nr=$(has 'no reading of the build job on aifoundry3' "$S/n1-wait.txt"); bf=$(grep -aqE 'build failed|no train runs today|start once more' "$S/n1-wait.txt" && echo 1 || echo 0); b1=$(builds)
read -r rw2 n17 <<EOF2
$(waitv 5 "$S/n1-wait2.txt")
EOF2
v5 start > "$S/n1-start2.txt" 2>&1; rs2=$?; stopline "$S/n1-start2.txt"
ok "$ra.$rw.$nr.$bf.$b1.$rw2.$rs2.$(builds)" "0.14.1.0.1.0.10.1" "N1 the cut wait reads 14 'no reading of the build job' and names neither a failed build nor a re-run; wait then reads the good build (0); a start after it is refused (10); one build counted"

step "N1b. the wait call cut after the first build ended good"
fresh_day
v5 start > "$S/n1b-start.txt" 2>&1; ra=$?
jobend
netcut 1
v5 wait > "$S/n1b-wait.txt" 2>&1; rw=$?; stopline "$S/n1b-wait.txt"
nr=$(has 'no reading of the build job on aifoundry3' "$S/n1b-wait.txt")
read -r rw2 n17 <<EOF2
$(waitv 5 "$S/n1b-wait2.txt")
EOF2
v5 start > "$S/n1b-start2.txt" 2>&1; rs2=$?
ok "$ra.$rw.$nr.$rw2.$rs2.$(builds)" "0.14.1.0.10.1" "N1b the cut wait after a good build reads 14 'no reading'; wait then reads it (0); a start is refused (10)"

nseq() {  # nseq <4|5> <tag> <re-run's stand-in sleep, s> <wait before the cut: 0|1>: a failed first build, its wait, the re-run's start; then
  #        (if asked) its end; then the cut wait call; prints "<start 1> <wait 1> <start 2> <cut wait>"
  local v=$1 t=$2 sl=$3 we=$4 r1 w1 n r2 w2
  fresh_day
  env FAKE_CMAKE_FAIL=build bash "$R/s08_a3_preflight_e182_v$v.sh" start > "$S/$t-start1.txt" 2>&1; r1=$?
  read -r w1 n <<EOF3
$(waitv "$v" "$S/$t-wait1.txt")
EOF3
  env FAKE_CMAKE_SLEEP_S="$sl" bash "$R/s08_a3_preflight_e182_v$v.sh" start > "$S/$t-start2.txt" 2>&1; r2=$?
  [ "$we" = 1 ] && jobend
  netcut 1
  bash "$R/s08_a3_preflight_e182_v$v.sh" wait > "$S/$t-wait2.txt" 2>&1; w2=$?
  echo "$r1 $w1 $r2 $w2"
}
step "N2. (verify-q154k's fault 1) the first build fails; the re-run runs; its wait call is cut (the day's build 2)"
read -r r1 w1 r2 w2 <<EOF2
$(nseq 5 n2 25 0)
EOF2
stopline "$S/n2-wait2.txt"
nr=$(has 'no reading of the build job on aifoundry3' "$S/n2-wait2.txt"); fb=$(has 'no train runs today' "$S/n2-wait2.txt")
v5 --no-trains > "$S/n2-nt1.txt" 2>&1; nt1=$?; stopline "$S/n2-nt1.txt"
jobend
v5 --no-trains > "$S/n2-nt2.txt" 2>&1; nt2=$?; stopline "$S/n2-nt2.txt"
q2=$(has 'the registered fallback is for a failed build' "$S/n2-nt2.txt"); h70=$(has '^HARNESS OK: 70 files' "$S/n2-nt2.txt")
read -r w3 n17 <<EOF2
$(waitv 5 "$S/n2-wait3.txt")
EOF2
ok "$r1.$w1.$r2.$w2.$nr.$fb.$nt1.$nt2.$q2.$h70.$w3.$(builds)" "0.16.0.14.1.0.10.10.1.0.0.2" "N2 the cut wait of the re-run reads 14 'no reading' and does NOT name the fallback; --no-trains is refused while the job runs (10) and after the good build (10, the good-build refusal), never reaching its checks; wait reads the good build (0); two builds counted"
step "N2v. the fault shown: step 6 v4 on the same sequence"
read -r r1 w1 r2 w2 <<EOF2
$(nseq 4 n2v 25 0)
EOF2
stopline "$S/n2v-wait2.txt"
fb=$(has "it was the day's build 2 (the first and its one re-run are spent): no train runs today: run step 6 v4 with --no-trains" "$S/n2v-wait2.txt")
jobend
v4 --no-trains > "$S/n2v-nt.txt" 2>&1; nt=$?
grep -aE '^HARNESS|the trains off' "$S/n2v-nt.txt" | sort -u | cut -c1-200
ok "$r1.$w1.$r2.$w2.$fb.$nt" "0.16.0.16.1.0" "N2v step 6 v4 names the FALLBACK on the cut wait (16), and its --no-trains passes (0) beside the good host: a network fault would lose the trains"

step "N4. the same, the re-run already ended good when its wait call is cut"
read -r r1 w1 r2 w2 <<EOF2
$(nseq 5 n4 0 1)
EOF2
stopline "$S/n4-wait2.txt"
nr=$(has 'no reading of the build job on aifoundry3' "$S/n4-wait2.txt"); fb=$(has 'no train runs today' "$S/n4-wait2.txt")
v5 --no-trains > "$S/n4-nt.txt" 2>&1; nt=$?; stopline "$S/n4-nt.txt"
q2=$(has 'the registered fallback is for a failed build' "$S/n4-nt.txt")
read -r w3 n17 <<EOF2
$(waitv 5 "$S/n4-wait3.txt")
EOF2
ok "$r1.$w1.$r2.$w2.$nr.$fb.$nt.$q2.$w3.$(builds)" "0.16.0.14.1.0.10.1.0.2" "N4 the cut wait reads 14 'no reading', the fallback not named; --no-trains refused beside the good host (10); wait reads it (0)"
step "N4v. the fault shown: step 6 v4 on the same sequence"
read -r r1 w1 r2 w2 <<EOF2
$(nseq 4 n4v 0 1)
EOF2
stopline "$S/n4v-wait2.txt"
fb=$(has "it was the day's build 2 (the first and its one re-run are spent): no train runs today" "$S/n4v-wait2.txt")
v4 --no-trains > "$S/n4v-nt.txt" 2>&1; nt=$?
ok "$r1.$w1.$r2.$w2.$fb.$nt" "0.16.0.16.1.0" "N4v step 6 v4 names the FALLBACK (16) and its --no-trains passes at once (0)"

step "N6. (fix-q154k) the first check's read after a good build is cut"
fresh_day
v5 start > "$S/n6-start.txt" 2>&1; ra=$?
jobend
netcut 2
v5 wait > "$S/n6-wait.txt" 2>&1; rw=$?; stopline "$S/n6-wait.txt"
nr=$(has 'no reading of inputs (rc 14) on aifoundry3' "$S/n6-wait.txt"); am=$(has 'a dated amendment first' "$S/n6-wait.txt")
read -r rw2 n17 <<EOF2
$(waitv 5 "$S/n6-wait2.txt")
EOF2
ok "$ra.$rw.$nr.$am.$rw2" "0.14.1.0.0" "N6 a cut check read is 14 'no reading of inputs' (never 'a dated amendment first'); wait then reads all four checks (0)"
step "N6v. the same under step 6 v4"
fresh_day
v4 start > "$S/n6v-start.txt" 2>&1; ra=$?
jobend
netcut 2
v4 wait > "$S/n6v-wait.txt" 2>&1; rw=$?; stopline "$S/n6v-wait.txt"
am=$(has "aifoundry3's checks after the build failed: inputs check_inputs_e182 (a binary or file differs: a dated amendment first)" "$S/n6v-wait.txt")
ok "$ra.$rw.$am" "0.16.1" "N6v step 6 v4 reads the cut read as a failed check: 16, 'a binary or file differs: a dated amendment first'"

step "O. a card session of ours on the box (the stand-in pgrep reports one): start, the fallback, then wait's checks"
touch "$S/ours-live.flag"
b0=$(builds)
v5 start > "$S/o1.txt" 2>&1; r1=$?
v5 --no-trains > "$S/o2.txt" 2>&1; r2=$?
v5 wait > "$S/o3.txt" 2>&1; r3=$?
rm -f "$S/ours-live.flag"
q1=$(has 'REFUSED: a card session of ours runs on aifoundry3' "$S/o1.txt"); q2=$(has 'REFUSED: a card session of ours runs on aifoundry3' "$S/o2.txt"); q3=$(has 'REFUSED: a card session of ours runs on aifoundry3' "$S/o3.txt")
ok "$r1.$q1.$r2.$q2.$r3.$q3.$([ "$(builds)" = "$b0" ] && echo same)" "10.1.10.1.10.1.same" "O each refused (10) beside a session of ours, no build started or counted"

step "R1. the re-run rule with REAL failed builds: a fresh day, the stand-in build fails (FAKE_CMAKE_FAIL=build): the first failure"
fresh_day
env FAKE_CMAKE_FAIL=build bash "$R/s08_a3_preflight_e182_v5.sh" start > "$S/r1-start.txt" 2>&1; ra=$?
read -r rw n17 <<EOF2
$(waitv 5 "$S/r1-wait.txt")
EOF2
stopline "$S/r1-wait.txt"
m1=$(has "the train host's build failed on aifoundry3 (the lines above; build 1 of at most 2 today): run this step's start once more (the one re-run)" "$S/r1-wait.txt")
ok "$ra.$rw.$m1.$(builds)" "0.16.1.1" "R1 the first failed build (JOB-DONE rc 1): 16, one re-run asked for, one build counted"
step "R2. the one re-run fails too"
env FAKE_CMAKE_FAIL=build bash "$R/s08_a3_preflight_e182_v5.sh" start > "$S/r2-start.txt" 2>&1; ra=$?
read -r rw n17 <<EOF2
$(waitv 5 "$S/r2-wait.txt")
EOF2
stopline "$S/r2-wait.txt"
m2=$(has "it was the day's build 2 (the first and its one re-run are spent): no train runs today: run step 6 v5 with --no-trains (rb/s08_a3_preflight_e182_v5.sh --no-trains), then step 8 v2 with --no-trains" "$S/r2-wait.txt")
ok "$ra.$rw.$m2.$(builds)" "0.16.1.2" "R2 the second failed build: 16, the fallback named (step 6 v5 --no-trains), two builds counted"
step "R3. a third start"
v5 start > "$S/r3.txt" 2>&1; r3=$?; stopline "$S/r3.txt"
m3=$(has "two train-host builds were started on aifoundry3 today (the first and its one re-run): no third. no train runs today: run step 6 v5 with --no-trains" "$S/r3.txt")
ok "$r3.$m3.$(builds)" "16.1.2" "R3 no third build: 16, the fallback named, no job started"
step "R4. the fallback: step 6 v5 --no-trains with its first read cut, then again; then step 8 v2 --no-trains"
netcut 1
v5 --no-trains > "$S/r4a.txt" 2>&1; rn=$?; stopline "$S/r4a.txt"
nr=$(has 'no reading of harness (rc 14) on aifoundry3' "$S/r4a.txt")
v5 --no-trains > "$S/r4b.txt" 2>&1; ra=$?
grep -aE '^HARNESS|^preflight_e182 rc|^e182_common rc|STOP|the trains off' "$S/r4b.txt" | sort -u | cut -c1-200
h70=$(has '^HARNESS OK: 70 files' "$S/r4b.txt")
: > "$S/dry-network.log"
bash "$R/s10_a3_dry_e182_v2.sh" start --no-trains > "$S/r4c.txt" 2>&1; rb_=$?
wait10 "$S/r4d.txt" --no-trains; rc_=$?
k1=$(has '^E182 dry 18220 rc=0' "$S/r4d.txt"); k2=$(has '^E182 dry 18201 --smoke trains=no rc=0' "$S/r4d.txt"); k3=$(has '^E182 start gate rc=8' "$S/r4d.txt")
nw=$(grep -c . "$S/dry-network.log")
ok "$rn.$nr.$ra.$h70.$rb_.$rc_.$k1.$k2.$k3.$nw" "14.1.0.1.0.0.1.1.1.0" "R4 a cut fallback read is 14 'no reading of harness'; then the fallback runs: --no-trains 0 (HARNESS OK 70, GO, verify), step 8 v2 --no-trains job rc 0; no network call"

step "L. a lost job: a fresh day, the 90 s stand-in cmake, the job's processes killed on the stand-in box mid-build"
fresh_day
env FAKE_CMAKE_SLEEP_S=90 bash "$R/s08_a3_preflight_e182_v5.sh" start > "$S/l1.txt" 2>&1; ra=$?
sleep 3
jp=$(cat "$J/a3-build-e182.pid" 2>/dev/null)
[ -n "$jp" ] && killtree "$jp"
sleep 1
read -r rw n17 <<EOF2
$(waitv 5 "$S/l1-wait.txt")
EOF2
grep -aE '^JOB-LOST' "$S/l1-wait.txt" | head -n 1 | cut -c1-200; stopline "$S/l1-wait.txt"
lo=$(has '^JOB-LOST a3-build-e182' "$S/l1-wait.txt"); m1=$(has "the train host's build job was lost (no process and no exit status) on aifoundry3 (the lines above; build 1 of at most 2 today)" "$S/l1-wait.txt")
sleep 1
ok "$ra.$rw.$lo.$m1.$(builds)" "0.16.1.1.1" "L the lost job: JOB-LOST is still a build's failure under v5: one re-run asked for (16), one build counted"

step "Z. no process of this test left running"
sleep 1
z=$(pgrep -f "$S/" 2>/dev/null | grep -v "^$$\$" | grep -c .)
zs=$(leftovers)
ok "$z.$zs" "0.0" "Z nothing of this test's stand-in box or builds left running"

echo
echo "SELFTEST-RB-E182-V5 $npass of $ncase $([ "$fail" -eq 0 ] && echo PASS || echo FAIL)"
exit "$fail"
