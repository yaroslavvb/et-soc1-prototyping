#!/usr/bin/env bash
# E186 (Q158, the kit): the desk test of E186's runbook with a FAKE ssh and rsync on a stand-in box. Its setup is E182's runbook desk test's
# (tools/claims-v3/e182/rb/selftest_rb_e182_v5.sh: a scratch git repository with an origin holding the lab files the steps read; a
# stand-in box laid out like aifoundry3's ~/aifoundry; stand-in ssh and rsync first on PATH that serve it and refuse any other host; the
# stand-in cmakes E182's notes 1 and 2 made, unchanged; the network cut), with E186's steps and cases. No lab box is reached; everything
# runs in <scratch dir> (never the lab clone); the bounds are rb_run.py's own (the test refuses to start if any RB_<CLS>_S is set). Cases:
#   A   the dry listing (FULL and the fallback, the look before the post): every step exits 0, the stand-ins see no ssh or rsync call;
#   K   step 2 with no window in RB_OUT refuses (10), and no call is made;
#   W1  a window written yesterday: step 2 refuses (10); W2 a window written for another runbook (RB_PLAN e182): 10; W3 step 1 with a
#       day that is not today: 10 (THE WINDOW RULE);
#   G   step 2 with no RB_GITLOCK: 10 (THE LAB-GIT LOCK);
#   P1  step 2 on the scratch repository (every file the pinned lists name, an origin so the pull runs, the kit's list a stand-in of the
#       scratch's files at its pinned count, stand-ins for the kit's desk-test logs): 0, the eleven lists at their counts and bytes, and
#       the history check's HISTORY OK (its anchor the scratch's root);
#   P2  the registration's list one line short: 16, named against its pin; P3 a file and its line rewritten together (the count kept,
#       every entry OK): 16, "its own bytes differ from the pin"; P4 the kit's list one line short: 16;
#   H1  a committed edit of a kit file no list pins at its bytes (score_e186.py): 16 by the history check alone, naming the file (its
#       cases on the lab's own history are rb/selftest_history_e186.sh's);
#   S1  step 5 on a clean stand-in box, its stand-in binaries and pins, then step 6 start and wait (the fast stand-in cmake): 0, the
#       build counted once, HARNESS OK 78 on the box, five 60 s reads, no call past a bound;
#   X3  a second start after the good build: refused (10);
#   N1  the wait call cut (ssh's 255, nothing printed): 14 "no reading of the build job", nothing counted; then wait reads the good build;
#   O   a card session of ours on the box (the stand-in pgrep reports one): step 6's start, step 8's start and step 9's launch refused (10);
#   D   step 8 (the trains' dry job) on the box step 6 left: rc 0, with the fp16 train 18610, 18611, 18612, the pass 18620, the smoke
#       and the start gate's 8;
#   R   the re-run rule with REAL failed builds (a fresh day; the stand-in build fails): 16 with one re-run; 16 naming the fallback; a
#       third start 16; then the fallback: step 6 --no-trains 0 (HARNESS OK 75), step 8 --no-trains rc 0;
#   V   THE BOX BUILD UNDER ITS BOUND (E182 note 2's V3S): a stand-in cmake that sleeps 90 s, past the 60 s a read gets: the detached job
#       runs past it, the waits say 17 (one wait loop 30 s here), no call runs past a bound, then the four checks (HARNESS OK 78);
#   N6  (E182 note 4's) the first check's read after the good build cut: 14 "no reading of inputs", never 16; wait then reads 0;
#   LJ  (E182 note 3's L) a lost job (its processes killed mid-build): JOB-LOST is a build's failure: one re-run asked for (16);
#   L   step 9 FULL yes launches the session on the stand-in box with the committed binaries' pins put back by step 5: the session stops
#       at its own harness check ("no device opened", exit 9) and writes its MANIFEST.sha256 (the manifest on an early path); step 10
#       reads it ended at a gate (16) with the manifest written;
#   C   step 11 on a session staged on the box (two block directories and the session's own files, the manifest made as the session makes
#       it): the copies by name, COPY-BACK EXACT, the history check (HISTORY OK), then the C-session gate stops it (14) because the staged session holds no C log, by
#       design (E182 note 1's F4: the copies are what is tested); C2 a second collection into the used output: refused (10); C3 one
#       byte of a box file changed after the manifest (the output moved aside first): COPY-BACK DIFFERS (16); C4 the window's last end
#       5 minutes away: refused (16) before any call;
#   Z   no process of this test is left running.
#
#   bash tools/claims-v3/e186/rb/selftest_rb_e186.sh <scratch dir> > <log>
# SPDX-License-Identifier: Apache-2.0
set -u
SRC=$(cd "$(dirname "${BASH_SOURCE[0]}")/../../../.." && pwd)
S=${1:?a scratch directory outside the repository}
case "$S" in "$SRC"|"$SRC"/*) echo "the scratch directory must be outside the repository"; exit 2 ;; esac
for v in RB_PROBE_S RB_READ_S RB_COPY_S RB_WAIT_S RB_LAUNCH_S RB_DESK_S E186_BUILD_S RB_DESKTEST RB_GITLOCK; do
  [ -z "${!v:-}" ] || { echo "$v is set: this test runs with rb_run.py's own bounds and no desk-test override in its environment"; exit 2; }
done
command -v gdate > /dev/null || { echo "no gdate (GNU date) on PATH"; exit 2; }
command -v timeout > /dev/null || { echo "no timeout on PATH"; exit 2; }
command -v sha256sum > /dev/null || { echo "no sha256sum on PATH"; exit 2; }
REAL_TIMEOUT=$(command -v timeout)
mkdir -p "$S"
S=$(cd "$S" && pwd)
rm -rf "${S:?}/tree" "${S:?}/box" "${S:?}/bin" "${S:?}/out" "${S:?}/boxbin" "${S:?}/origin.git" "${S:?}/out-k" "${S:?}/out-w" "${S:?}/out-p" "${S:?}/out-b"
T=$S/tree; B=$S/box; BIN=$S/bin
mkdir -p "$T/tools/claims-v3" "$T/workloads" "$B/aifoundry3/aifoundry" "$BIN" "$S/out" "$S/boxbin"
for p in e186 e182 m12 kinds hpl ccheck e128 e178 p8-600 q141k-runbook/k6 q141k-runbook/v3.1; do
  mkdir -p "$T/tools/claims-v3/$p"; rsync -a --exclude __pycache__ "$SRC/tools/claims-v3/$p/" "$T/tools/claims-v3/$p/"
done
cp -p "$SRC/tools/claims-v3/lib.sh" "$SRC/tools/claims-v3/dmcmd_audit.py" "$SRC/tools/claims-v3/dmcmd_table.json" "$T/tools/claims-v3/"
( cd "$SRC" && git ls-files workloads/sparsity ) | while IFS= read -r f; do mkdir -p "$T/$(dirname "$f")"; cp -p "$SRC/$f" "$T/$f"; done
# every file the pinned lists name (E186's registration and E182's six name a few outside these directories), and E182's committed train
# and block files that plan_e186.py --check and forecast_e186.py --check read
for l in tools/claims-v3/e186/SHA256SUMS-e186-registration tools/claims-v3/e182/SHA256SUMS-e182-registration tools/claims-v3/e182/SHA256SUMS-e182-kit \
         tools/claims-v3/e182/SHA256SUMS-e182-note1 tools/claims-v3/e182/SHA256SUMS-e182-note2 tools/claims-v3/e182/SHA256SUMS-e182-note3 \
         tools/claims-v3/e182/SHA256SUMS-e182-note4 tools/claims-v3/e186/SHA256SUMS-e186-m1; do
  awk '{print $2}' "$SRC/$l" | while IFS= read -r f; do f=${f#\*}; [ -e "$T/$f" ] || { mkdir -p "$T/$(dirname "$f")"; cp -p "$SRC/$f" "$T/$f"; }; done
done
E182D=docs/reports/data/2026-11-08-e182-one-number-r2-aifoundry3
mkdir -p "$T/$E182D"; cp -p "$SRC/$E182D/trains-e182.json" "$T/$E182D/"
for b in "$SRC/$E182D"/aifoundry3/e182/p182*; do mkdir -p "$T/$E182D/aifoundry3/e182/$(basename "$b")"; cp -p "$b/block.json" "$T/$E182D/aifoundry3/e182/$(basename "$b")/"; done
# P1's stand-ins, written before the scratch commit: the kit's desk-test logs (this test's own log is being written now) and the kit's
# list, a stand-in of KITPIN files of the scratch at their sha256 (the kit's own list is made after this test and holds its log)
KITN=$(sed -n 's/^KITPIN=tools\/claims-v3\/e186\/SHA256SUMS-e186-kit:\([0-9]*\).*/\1/p' "$SRC/tools/claims-v3/e186/rb/s03_desk_e186.sh")
case "$KITN" in ''|*[!0-9]*) echo "s03_desk_e186.sh pins no count for the kit's list ($KITN)"; exit 2 ;; esac
mkdir -p "$T/tools/claims-v3/e186/logs"
for spec in "desktest-host-e186.txt DESKTEST-HOST-E186 0 of 0 PASS" "selftest-score-e186.txt SELFTEST-SCORE-E186 0 of 0 PASS" \
            "selftest-stops-e186t.txt SELFTEST-STOPS-E186T 0 of 0 PASS" "dry-intel-e186.txt DRY-INTEL-E186 PASS" "selftest-rb-e186.txt SELFTEST-RB-E186 0 of 0 PASS" \
            "selftest-history-e186.txt SELFTEST-HISTORY-E186 0 of 0 PASS"; do
  f=${spec%% *}; [ -f "$T/tools/claims-v3/e186/logs/$f" ] || printf '%s (a stand-in written by the runbook desk test for its case P1)\n' "${spec#* }" > "$T/tools/claims-v3/e186/logs/$f"
done
rm -f "$T/tools/claims-v3/e186/SHA256SUMS-e186-kit"
( cd "$T" && find tools/claims-v3/e186 tools/claims-v3/e182 -type f ! -name 'SHA256SUMS-e186-kit' | LC_ALL=C sort | head -n "$KITN" | while IFS= read -r f; do sha256sum "$f"; done ) > "$S/kit-standin.txt"
[ "$(grep -c . "$S/kit-standin.txt")" -eq "$KITN" ] || { echo "the kit list's stand-in holds fewer than $KITN files"; exit 2; }
cp "$S/kit-standin.txt" "$T/tools/claims-v3/e186/SHA256SUMS-e186-kit"
G="git -C $T -c user.name=e186-desktest -c user.email=desktest@localhost -c core.hooksPath=/dev/null -c commit.gpgsign=false"
$G init -q && $G add -A && $G commit -q -m "E186 runbook desk test: the lab files the steps read" || { echo "the scratch repository failed"; exit 2; }
git clone -q --bare "$T" "$S/origin.git" && $G remote add origin "$S/origin.git" && $G fetch -q origin &&
  $G branch -q -u "origin/$($G rev-parse --abbrev-ref HEAD)" || { echo "the scratch repository's origin failed"; exit 2; }
BASE0=$($G rev-list --max-parents=0 HEAD)
echo "scratch repository: $($G ls-files | wc -l | tr -d ' ') files committed ($($G ls-files workloads/sparsity | wc -l | tr -d ' ') of them the workload's), with an origin; the kit list's stand-in $KITN files"
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
R=$T/tools/claims-v3/e186/rb
BOXT=$B/aifoundry3/aifoundry
J=$BOXT/build/q141k/jobs
printf '#!/bin/sh\necho aifoundry3\n' > "$S/boxbin/hostname"
printf '#!/bin/sh\nexec gdate "$@"\n' > "$S/boxbin/date"
printf '#!/bin/sh\nexec /usr/bin/python3 "$@"\n' > "$S/boxbin/python3"
printf '#!/bin/sh\necho "(desk test: no et-who here)"\n' > "$S/boxbin/et-who"
printf '#!/bin/sh\n[ -e "%s" ] && { echo 4242; exit 0; }\nexit 1\n' "$S/ours-live.flag" > "$S/boxbin/pgrep"
for n in ssh rsync scp sudo flock; do printf '#!/bin/sh\necho "%s $*" >> "%s"\necho "BOX STAND-IN: %s refused" >&2\nexit 97\n' "$n" "$S/dry-network.log" "$n" > "$S/boxbin/$n"; done
printf '#!/bin/sh\nexec "$@"\n' > "$S/boxbin/setsid"
printf '#!/bin/sh\nexec "%s" "$@"\n' "$REAL_TIMEOUT" > "$S/boxbin/timeout"
cp -p "$SRC/tools/claims-v3/e182/rb/fake_cmake_slow_e182.sh" "$S/boxbin/cmake"
cp -p "$SRC/tools/claims-v3/e182/rb/fake_cmake_e182.sh" "$S/boxbin/fake_cmake_e182.sh"
chmod +x "$BIN/ssh" "$BIN/rsync" "$S/boxbin"/*
export PATH="$BIN:$PATH" RB_REPO="$T" RB_OUT="$S/out" RB_LOCK="$S/lock.txt" FAKE_CMAKE_MOCKRT="$T/tools/claims-v3/ccheck/mockrt" FAKE_CMAKE_SLEEP_S=0
export RB_E186_BASE=$BASE0 RB_E186_MERGED=$BASE0 RB_E186_M1=$BASE0
: > "$S/calls.log"; : > "$RB_LOCK"; : > "$S/dry-network.log"; : > "$S/gitlock"; rm -f "$S/ours-live.flag" "$S/ssh-fail-at"
fail=0; npass=0; ncase=0
ok() { ncase=$((ncase + 1)); if [ "$1" = "$2" ]; then npass=$((npass + 1)); echo "-> PASS ($3)"; else echo "-> FAIL ($3: got $1, want $2)"; fail=1; fi; }
step() { echo; echo "== $*"; }
san() { sed -e "s#$S#<scratch>#g"; }
nlog() { if [ -f "$RB_OUT/runbook.log" ]; then grep -c . "$RB_OUT/runbook.log"; else echo 0; fi; }
since() { tail -n +"$(( $1 + 1 ))" "$RB_OUT/runbook.log" 2>/dev/null; }
TODAY=$(TZ=America/Los_Angeles gdate +%F)
AT=$BOXT/build/e186-build-attempts.txt
builds() { if [ -f "$AT" ]; then echo $(( $(grep -c "^$TODAY .* a3-build-e186 started\$" "$AT") - $(grep -c "^$TODAY .* a3-build-e186 ended rc=[0-9]*: TRAIN-HOST-INPUTS-DIFFER" "$AT") )); else echo 0; fi; }
fresh_day() {
  rm -f "$AT"; rm -rf "${BOXT:?}/build/e186-build-logs"
  for x in rc out; do [ -e "$J/a3-build-e186.$x" ] && touch -t "$(gdate -d '-2 day' +%Y%m%d%H%M)" "$J/a3-build-e186.$x"; done
  return 0
}
pin_standins() {
  /usr/bin/python3 -B - "$BOXT" <<'PY'
import hashlib, json, os, sys
t = sys.argv[1]
p = os.path.join(t, "tools/claims-v3/e186/harness-e186.json")
h = json.load(open(p))
for rel in h["box_binaries_sha256"]:
    h["box_binaries_sha256"][rel] = hashlib.sha256(open(os.path.join(t, rel), "rb").read()).hexdigest()
open(p, "w").write(json.dumps(h, indent=1) + "\n")
print("the stand-in box's harness-e186.json now pins its 4 stand-in binaries")
PY
}
leftovers() { pgrep -f "$S/boxbin/cmake|bash build/q141k/jobs/a3-build-e186[.]sh|tools/claims-v3/e186/build_host_e186[.]sh|session_e186[.]sh" 2>/dev/null | grep -c .; }
b6() { bash "$R/s08_a3_build_e186.sh" "$@"; }
netcut() { echo "${1:-1}" > "$S/ssh-fail-at"; }
jobend() { local k; for k in $(seq 1 150); do [ -e "$J/a3-build-e186.rc" ] && return 0; sleep 1; done; echo "the build job did not end in 150 s"; return 1; }
stopline() { grep -a 'STOP' "$1" | tail -n 1 | cut -c1-330; }
waitb() {  # waitb <out> [<max calls>]: step 6's wait, again while it says 17; prints "<rc> <number of 17s>"
  local o=$1 m=${2:-12} k r n17=0
  : > "$o"
  for k in $(seq 1 "$m"); do b6 wait >> "$o" 2>&1; r=$?; [ "$r" -eq 17 ] || break; n17=$((n17 + 1)); done
  echo "$r $n17"
}
wait10() { local o=$1 x=${2:-} k r; for k in 1 2 3 4 5 6 7 8; do bash "$R/s10_a3_dry_e186.sh" wait $x > "$o" 2>&1; r=$?; [ "$r" -eq 17 ] || break; done; return "$r"; }
has() { grep -aq -- "$1" "$2" && echo 1 || echo 0; }
killtree() {  # E182's: freeze the parent first (so the job never writes its exit status), then its children, then kill them all
  local p=$1 c kids; kids=$(pgrep -P "$p" 2>/dev/null); kill -STOP "$p" 2>/dev/null
  for c in $kids; do killtree "$c"; done; kill -KILL "$p" 2>/dev/null
}
cd "$T" || exit 2

step "A. the dry listing (FULL and the fallback, the look before the post): every step exits 0, no ssh or rsync call"
: > "$S/calls.log"
bash "$R/list_steps_e186.sh" "$S/dry-out" > "$S/dry-listing.txt" 2>&1; rc=$?
n=$(grep -c . "$S/calls.log"); tail -n 1 "$S/dry-listing.txt"
lp=$(awk '/s05_look_k6.sh aifoundry3$/ {l=NR} /the day.s one post, made AFTER the look/ {p=NR} END {print (l > 0 && p > l) ? 1 : 0}' "$S/dry-listing.txt")
n6=$(grep -c '^################ tools/claims-v3/e186/rb/s08_a3_build_e186.sh' "$S/dry-listing.txt"); n2=$(grep -c '^################ tools/claims-v3/e186/rb/s03_desk_e186.sh' "$S/dry-listing.txt")
n11=$(grep -c '^################ tools/claims-v3/e186/rb/s22_collect_e186.sh' "$S/dry-listing.txt"); cb=$(grep -c 'COPY-BACK EXACT against the session' "$S/dry-listing.txt")
ok "$rc.$n.$lp.$n6.$n2.$n11.$cb" "0.0.1.3.1.2.2" "A the dry listing: 0 failing, no call, the look before the post, step 6 three times, step 2 once, step 11 twice with its exact copy-back"

step "K. step 2 with no window in RB_OUT (step 1 not run)"
: > "$S/calls.log"
RB_OUT="$S/out-k" RB_GITLOCK="$S/gitlock" bash "$R/s03_desk_e186.sh" > "$S/k.txt" 2>&1; rc=$?
stopline "$S/k.txt" | san; n=$(grep -c . "$S/calls.log")
ok "$rc.$n.$(has 'no window in RB_OUT' "$S/k.txt")" "10.0.1" "K step 2 refuses without step 1's window, before any call"

step "W1-W3. the window rule: a window written yesterday, one written for another runbook, and step 1 with a day not today"
mkdir -p "$S/out-w"
RB_OUT="$S/out-w" bash "$R/s02_window_e186.sh" "$TODAY" 23:50 23:55 > /dev/null 2>&1
touch -t "$(gdate -d '-1 day' +%Y%m%d%H%M)" "$S/out-w/window.env"
RB_OUT="$S/out-w" RB_GITLOCK="$S/gitlock" bash "$R/s03_desk_e186.sh" > "$S/w1.txt" 2>&1; w1=$?; stopline "$S/w1.txt" | san
RB_OUT="$S/out-w" bash "$R/s02_window_e186.sh" "$TODAY" 23:50 23:55 > /dev/null 2>&1
sed -i '' -e 's/^RB_PLAN=e186$/RB_PLAN=e182/' "$S/out-w/window.env"
RB_OUT="$S/out-w" RB_GITLOCK="$S/gitlock" bash "$R/s03_desk_e186.sh" > "$S/w2.txt" 2>&1; w2=$?; stopline "$S/w2.txt" | san
RB_OUT="$S/out-w" bash "$R/s02_window_e186.sh" "$(gdate -d '+1 day' +%F)" 10:00 12:00 > "$S/w3.txt" 2>&1; w3=$?; stopline "$S/w3.txt" | san
ok "$w1.$(has 'was not written today' "$S/w1.txt").$w2.$(has 'written for e182' "$S/w2.txt").$w3.$(has 'is not today' "$S/w3.txt")" "10.1.10.1.10.1" \
  "W1-W3 a window not written today, one for another runbook, and a window for another day are each refused (10)"

step "G. step 2 with no RB_GITLOCK (the lab-git lock)"
mkdir -p "$S/out-p"; RB_OUT="$S/out-p" bash "$R/s02_window_e186.sh" "$TODAY" 23:50 23:55 > /dev/null 2>&1
RB_OUT="$S/out-p" bash "$R/s03_desk_e186.sh" > "$S/g.txt" 2>&1; rc=$?; stopline "$S/g.txt" | san
ok "$rc.$(has 'RB_GITLOCK is not set' "$S/g.txt")" "10.1" "G step 2 refuses a pull without the lab-git lock"

step "P1. step 2 on the scratch repository (every listed file, an origin, the kit list's stand-in of $KITN, the logs' stand-ins)"
RB_OUT="$S/out-p" RB_GITLOCK="$S/gitlock" bash "$R/s03_desk_e186.sh" > "$S/p1.txt" 2>&1; rc=$?
grep -E 'desk check:|STOP' "$S/p1.txt" | san | cut -c1-400
pins=$(grep -c 'the eleven lists at their pinned counts and bytes (10; 37, 24, 1, 9; 32, 79, 50, 49, 89, 19)' "$S/p1.txt")
lk=$(grep -c 'lockf -k -t 600' "$S/out-p/runbook.log" 2>/dev/null)
ok "$rc.$pins.$([ "$lk" -ge 1 ] && echo 1 || echo 0)" "0.1.1" "P1 step 2 passes the intact tree at every pin, its pull under the lab-git lock"

step "P2-P4. a pinned list one line short; a file and its line rewritten together; the kit's list one line short"
sed -i '' -e '$d' "$T/tools/claims-v3/e186/SHA256SUMS-e186-registration"
$G commit -q -am "desk test: the registration's list one line short" || echo "the scratch commit failed"
RB_OUT="$S/out-p" RB_GITLOCK="$S/gitlock" bash "$R/s03_desk_e186.sh" > "$S/p2.txt" 2>&1; p2=$?; stopline "$S/p2.txt" | san | cut -c1-300
k2=$(grep -c 'SHA256SUMS-e186-registration(9 OK of 9; pinned 10; its own bytes differ from the pin)' "$S/p2.txt")
$G reset -q --hard HEAD~1
printf ' \n' >> "$T/tools/claims-v3/e186/forecast-e186.txt"
h=$(sha256sum "$T/tools/claims-v3/e186/forecast-e186.txt" | cut -d' ' -f1)
sed -i '' -e "s#^[0-9a-f]*  tools/claims-v3/e186/forecast-e186.txt\$#$h  tools/claims-v3/e186/forecast-e186.txt#" "$T/tools/claims-v3/e186/SHA256SUMS-e186-registration"
$G commit -q -am "desk test: a file and its line rewritten together" || echo "the scratch commit failed"
RB_OUT="$S/out-p" RB_GITLOCK="$S/gitlock" bash "$R/s03_desk_e186.sh" > "$S/p3.txt" 2>&1; p3=$?; stopline "$S/p3.txt" | san | cut -c1-300
k3=$(grep -c 'SHA256SUMS-e186-registration(10 OK of 10; pinned 10; its own bytes differ from the pin)' "$S/p3.txt")
$G reset -q --hard HEAD~1
sed -i '' -e '$d' "$T/tools/claims-v3/e186/SHA256SUMS-e186-kit"
$G commit -q -am "desk test: the kit's list one line short" || echo "the scratch commit failed"
RB_OUT="$S/out-p" RB_GITLOCK="$S/gitlock" bash "$R/s03_desk_e186.sh" > "$S/p4.txt" 2>&1; p4=$?; stopline "$S/p4.txt" | san | cut -c1-300
k4=$(grep -c "SHA256SUMS-e186-kit($((KITN - 1)) OK of $((KITN - 1)); pinned $KITN)" "$S/p4.txt")
$G reset -q --hard HEAD~1
ok "$p2.$k2.$p3.$k3.$p4.$k4" "16.1.16.1.16.1" "P2-P4 each refused (16) and named against its pin: a short list, a rewritten list (count kept, bytes not), the kit's short list"

step "H1. a committed edit of a kit file no list pins at its bytes (score_e186.py): the history check refuses it"
printf '\n# a desk-test edit\n' >> "$T/tools/claims-v3/e186/score_e186.py"
$G commit -q -am "desk test: a kit file edited" || echo "the scratch commit failed"
RB_OUT="$S/out-p" RB_GITLOCK="$S/gitlock" bash "$R/s03_desk_e186.sh" > "$S/h1.txt" 2>&1; h1=$?; stopline "$S/h1.txt" | san | cut -c1-300
kh=$(grep -c 'the desk check failed: history$' "$S/h1.txt"); kf=$(has 'M tools/claims-v3/e186/score_e186.py' "$S/h1.txt")
$G reset -q --hard HEAD~1
ok "$h1.$kh.$kf.$(has 'HISTORY OK: ' "$S/p1.txt")" "16.1.1.1" "H1 refused (16) by the history check alone, naming the file (P1's intact tree read HISTORY OK)"

# ---- the box's side, through the fake ssh
export RB_OUT="$S/out-b"; mkdir -p "$RB_OUT"
wd=$(TZ=America/Los_Angeles gdate -d '+3 hour' +%F); le_=$(TZ=America/Los_Angeles gdate -d '+3 hour' +%H:%M)
if [ "$wd" = "$TODAY" ]; then
  if [ "$(TZ=America/Los_Angeles gdate -d '+30 min' +%F)" = "$wd" ]; then ls_=$(TZ=America/Los_Angeles gdate -d '+30 min' +%H:%M); else ls_=23:58; fi
else le_=23:59; ls_=$(TZ=America/Los_Angeles gdate -d '+30 min' +%H:%M); wd=$TODAY; fi
bash "$R/s02_window_e186.sh" "$wd" "$ls_" "$le_" > "$S/b-window.txt" 2>&1 || { echo "the window failed: $(tail -2 "$S/b-window.txt")"; fail=1; }

step "S1. step 5 on a clean stand-in box, its stand-in binaries and pins, then step 6 start and wait (the fast stand-in cmake)"
rm -rf "${B:?}/aifoundry3/aifoundry"; mkdir -p "$BOXT"
bash "$R/s07_a3_sync_e186.sh" > "$S/s1-sync.txt" 2>&1; rs=$?
grep -E 'synced to|STOP' "$S/s1-sync.txt" | san | cut -c1-220
for f in build/sparsity/host/sparsity_host build/ccheck/b/host/sparsity_host build/ettelem/ettelem; do
  mkdir -p "$BOXT/$(dirname "$f")"
  printf '#!/bin/sh\n# options the preflight looks for: file: int8 fp16 --dump-tiles --stop-file --c-log --c-poison --values-b --abba --launches\necho "STUB EXECUTED: %s $*" >&2\nexit 97\n' "$f" > "$BOXT/$f"
  chmod +x "$BOXT/$f"
done
mkdir -p "$BOXT/build/sparsity/kernel"; echo "stub kernel (desk test)" > "$BOXT/build/sparsity/kernel/sparsity.elf"
pin_standins
n0=$(nlog)
b6 start > "$S/s1-start.txt" 2>&1; ra=$?
grep -E 'STOP|REFUSED|JOB-STARTED|runs on aifoundry3' "$S/s1-start.txt" | san | cut -c1-220
read -r rw n17 <<EOF2
$(waitb "$S/s1-wait.txt")
EOF2
grep -aE '^E186-BUILD-ATTEMPT|^TRAIN-HOST-BUILT|^NOTE1 FILES OK|^HARNESS|^check_e186 rc|^preflight_e186 rc|^e186_common rc|STOP|aifoundry3: the train host built' "$S/s1-wait.txt" | sort -u | san | cut -c1-220
nreads=$(since "$n0" | grep -c 'step=s08_a3_build_e186 class=read host=aifoundry3 bound=60s')
n13=$(since "$n0" | grep -c ' rc=13 ')
th=$([ -x "$BOXT/build/e186host/b/host/sparsity_host" ] && echo 1 || echo 0)
ok "$rs.$ra.$rw.$(has '^HARNESS OK: 78 files' "$S/s1-wait.txt").$nreads.$n13.$th.$(builds)" "0.0.0.1.5.0.1.1" "S1 the sync, the build job, then the four checks, each in its own 60 s read (5 with the one before the build); HARNESS OK 78; one build counted"

step "X3. a second start after the good build: refused"
b6 start > "$S/x3.txt" 2>&1; ra=$?; stopline "$S/x3.txt" | san
ok "$ra.$(has 'REFUSED: the train host was built on aifoundry3 today' "$S/x3.txt").$(builds)" "10.1.1" "X3 step 6 refuses a second start after a good build (10), the count unchanged"

step "N1. the wait call cut (exit 255) after the good build"
netcut 1
b6 wait > "$S/n1.txt" 2>&1; rw=$?; stopline "$S/n1.txt" | san
nr=$(has 'no reading of the build job on aifoundry3' "$S/n1.txt")
read -r rw2 n17 <<EOF2
$(waitb "$S/n1-2.txt")
EOF2
ok "$rw.$nr.$rw2.$(builds)" "14.1.0.1" "N1 a cut wait reads 14 'no reading', nothing counted; wait then reads the good build (0)"

step "D. step 8, the trains' dry job, on the box step 6 left"
: > "$S/dry-network.log"
bash "$R/s10_a3_dry_e186.sh" start > "$S/d-start.txt" 2>&1; ds=$?
wait10 "$S/d-wait.txt"; dw=$?
grep -aE '^E186 dry|^E186 start gate' "$S/d-wait.txt" | cut -c1-120
k=0; for x in 'E186 dry 18610 rc=0' 'E186 dry 18611 rc=0' 'E186 dry 18612 rc=0' 'E186 dry 18620 rc=0' 'E186 dry 18601 --smoke rc=0' 'E186 start gate rc=8'; do k=$((k + $(has "^$x" "$S/d-wait.txt"))); done
nw=$(grep -c . "$S/dry-network.log")
ok "$ds.$dw.$k.$nw" "0.0.6.0" "D the dry job rc 0: the fp16 train 18610, 18611, 18612, the pass 18620, the smoke, the start gate's 8; no network or device-tool call on the box"

step "O. a card session of ours on the box: step 6's start, step 8's start and step 9's launch each refused"
touch "$S/ours-live.flag"
b6 start > "$S/o6.txt" 2>&1; o6=$?
bash "$R/s10_a3_dry_e186.sh" start > "$S/o8.txt" 2>&1; o8=$?
bash "$R/s11_a3_session_e186.sh" FULL yes > "$S/o9.txt" 2>&1; o9=$?
rm -f "$S/ours-live.flag"
stopline "$S/o9.txt" | san
ok "$o6.$(has 'a card session of ours runs on aifoundry3' "$S/o6.txt").$o8.$o9.$(grep -aqE 'a card session of ours already runs|card session of ours' "$S/o9.txt" && echo 1 || echo 0)" "10.1.14.10.1" \
  "O beside a session of ours: step 6 refused (10), step 8's job refused on the box (14, JOB-REFUSED), step 9 refused (10)"

step "R. the re-run rule with REAL failed builds, then the fallback"
fresh_day
env FAKE_CMAKE_FAIL=build bash "$R/s08_a3_build_e186.sh" start > "$S/r1s.txt" 2>&1; r1s=$?
read -r r1w n17 <<EOF2
$(waitb "$S/r1w.txt")
EOF2
m1=$(has "build 1 of at most 2 today): run this step's start once more (the one re-run)" "$S/r1w.txt")
env FAKE_CMAKE_FAIL=build bash "$R/s08_a3_build_e186.sh" start > "$S/r2s.txt" 2>&1; r2s=$?
read -r r2w n17 <<EOF2
$(waitb "$S/r2w.txt")
EOF2
m2=$(has "no train runs today: run step 6 with --no-trains (rb/s08_a3_build_e186.sh --no-trains)" "$S/r2w.txt")
b6 start > "$S/r3.txt" 2>&1; r3=$?
m3=$(has 'no third' "$S/r3.txt")
b6 --no-trains > "$S/r4.txt" 2>&1; r4=$?
grep -aE '^HARNESS|^preflight_e186 rc|^e186_common rc|STOP|the trains off' "$S/r4.txt" | sort -u | san | cut -c1-200
h75=$(has '^HARNESS OK: 75 files' "$S/r4.txt")
: > "$S/dry-network.log"
bash "$R/s10_a3_dry_e186.sh" start --no-trains > "$S/r5s.txt" 2>&1; r5s=$?
wait10 "$S/r5w.txt" --no-trains; r5w=$?
k=0; for x in 'E186 dry 18620 rc=0' 'E186 dry 18601 --smoke trains=no rc=0' 'E186 start gate rc=8'; do k=$((k + $(has "^$x" "$S/r5w.txt"))); done
ok "$r1s.$r1w.$m1.$r2s.$r2w.$m2.$r3.$m3.$(builds).$r4.$h75.$r5s.$r5w.$k" "0.16.1.0.16.1.16.1.2.0.1.0.0.3" \
  "R one re-run asked for (16); the second failure names the fallback (16); no third (16); two builds counted; the fallback: --no-trains 0 (HARNESS OK 75), step 8 --no-trains rc 0"

step "V. the box build under its bound: a fresh day, a stand-in cmake that sleeps 90 s (past the 60 s a read gets); the detached job, waited on"
fresh_day
n0=$(nlog)
env FAKE_CMAKE_SLEEP_S=90 bash "$R/s08_a3_build_e186.sh" start > "$S/v-start.txt" 2>&1; vs=$?
t0v=$(date +%s)
read -r vw n17 <<EOF2
$(RB_WAIT_LOOP_S=30 waitb "$S/v-wait.txt" 12)
EOF2
dv=$(( $(date +%s) - t0v ))
grep -aE '^build_host_e186 rc=|^TRAIN-HOST-BUILT|^HARNESS|STOP|aifoundry3: the train host built' "$S/v-wait.txt" | sort -u | san | cut -c1-200
n13=$(since "$n0" | grep -c ' rc=13 ')
ok "$vs.$vw.$([ "$n17" -ge 2 ] && echo 1 || echo 0).$([ "$dv" -ge 60 ] && echo 1 || echo 0).$n13.$(has '^HARNESS OK: 78 files' "$S/v-wait.txt").$(builds)" "0.0.1.1.0.1.1" \
  "V a 90 s build: the job ran past one read's 60 s ($dv s of waits, $n17 of them 17), no call past a bound, then the checks (HARNESS OK 78); one build counted"

step "N6. the first check's read after the good build cut: no reading of a check, never a failed check"
netcut 2
b6 wait > "$S/n6.txt" 2>&1; n6=$?; stopline "$S/n6.txt" | san
q6=$(has 'no reading of inputs' "$S/n6.txt"); f6=$(has 'a dated amendment first' "$S/n6.txt")
read -r n6b n17 <<EOF2
$(waitb "$S/n6-2.txt")
EOF2
ok "$n6.$q6.$f6.$n6b.$(builds)" "14.1.0.0.1" "N6 a cut check read is 14 'no reading of inputs' (never 16 'a dated amendment first'); wait then reads all four checks (0)"

step "LJ. a lost job: a fresh day, the 90 s stand-in cmake, the job's processes killed on the stand-in box mid-build"
fresh_day
env FAKE_CMAKE_SLEEP_S=90 bash "$R/s08_a3_build_e186.sh" start > "$S/lj-start.txt" 2>&1; ljs=$?
sleep 3
jp=$(cat "$J/a3-build-e186.pid" 2>/dev/null)
[ -n "$jp" ] && killtree "$jp"
sleep 1
read -r ljw n17 <<EOF2
$(waitb "$S/lj-wait.txt")
EOF2
stopline "$S/lj-wait.txt" | san
lo=$(has '^JOB-LOST a3-build-e186' "$S/lj-wait.txt"); m1=$(has "the train host's build job was lost (no process and no exit status) on aifoundry3 (the lines above; build 1 of at most 2 today)" "$S/lj-wait.txt")
sleep 1
ok "$ljs.$ljw.$lo.$m1.$(builds)" "0.16.1.1.1" "LJ the lost job: JOB-LOST is a build's failure: one re-run asked for (16), one build counted"

step "L. step 9 FULL yes on the box with the committed binaries' pins put back (step 5 again): the session stops at its own harness check"
fresh_day
b6 start > "$S/l0s.txt" 2>&1
read -r l0w n17 <<EOF2
$(waitb "$S/l0w.txt")
EOF2
bash "$R/s07_a3_sync_e186.sh" > "$S/l-sync.txt" 2>&1; ls_rc=$?
bash "$R/s11_a3_session_e186.sh" FULL yes > "$S/l9.txt" 2>&1; l9=$?
grep -aE 'LAUNCHED|STOP|launched on' "$S/l9.txt" | san | cut -c1-200
T0=$(cat "$RB_OUT/e186-T0.txt" 2>/dev/null)
for k in $(seq 1 30); do [ -s "$BOXT/build/e186/T$T0/MANIFEST.sha256" ] && break; sleep 1; done
bash "$R/s20_wait_e186.sh" > "$S/l20.txt" 2>&1; l20=$?; stopline "$S/l20.txt" | san
hc=$(has 'harness check failed: no device opened' "$BOXT/build/e186/T$T0/session.log")
mf=$([ -s "$BOXT/build/e186/T$T0/MANIFEST.sha256" ] && echo 1 || echo 0)
ok "$l0w.$ls_rc.$l9.$hc.$mf.$l20.$(has '^MANIFEST-WRITTEN' "$RB_OUT"/calls/*wait-e186*.out 2>/dev/null)" "0.0.0.1.1.16.1" \
  "L the launch (0); the session stops at its harness check, no device opened, its manifest written; step 10 reads a gate stop (16) with the manifest"

step "C. step 11 on a session staged on the box: the copies by name, COPY-BACK EXACT, then the C gate (14, by design)"
SD=$BOXT/build/e186/T$T0
mkdir -p "$BOXT/build/claims-v3/aifoundry3/e186-stoptest/p18602" "$BOXT/build/claims-v3/aifoundry3/e186/p18610/a0"
echo '{"status":"ok"}' > "$BOXT/build/claims-v3/aifoundry3/e186-stoptest/p18602/block.json"
echo 'rc=6' > "$BOXT/build/claims-v3/aifoundry3/e186-stoptest/p18602/stoptest.rc"
echo '{"process": 0}' > "$BOXT/build/claims-v3/aifoundry3/e186/p18610/train.jsonl"
echo '{"item": "fp16.zeros"}' > "$BOXT/build/claims-v3/aifoundry3/e186/p18610/a0/runs.jsonl"
printf 'build/claims-v3/aifoundry3/e186-stoptest/p18602\nbuild/claims-v3/aifoundry3/e186/p18610\n' > "$SD/blocks.txt"
( cd "$BOXT" && { find "build/e186/T$T0" -type f ! -name 'MANIFEST.sha256*'; while IFS= read -r b; do find "$b" -type f ! -name telemetry.jsonl.raw; done < "$SD/blocks.txt"; } |
  LC_ALL=C sort -u | while read -r f; do sha256sum "$f"; done > "build/e186/T$T0/MANIFEST.sha256" )
nm=$(grep -c . "$SD/MANIFEST.sha256")
printf '#!/bin/sh\necho "the desk-test stand-in collector (RB_DESKTEST=1): nothing reduced"\n' > "$S/standin-collect.sh"
RB_DESKTEST=1 K6E186_COLLECT="$S/standin-collect.sh" bash "$R/s22_collect_e186.sh" > "$S/c1.txt" 2>&1; c1=$?
grep -aE '^COPY-BACK|STOP' "$S/c1.txt" | san | cut -c1-200
cx=$(has "^COPY-BACK EXACT $nm files" "$S/c1.txt"); cg=$(has 'has no finished check of C' "$S/c1.txt"); ch=$(has 'HISTORY OK: ' "$S/c1.txt")
RB_DESKTEST=1 K6E186_COLLECT="$S/standin-collect.sh" bash "$R/s22_collect_e186.sh" > "$S/c2.txt" 2>&1; c2=$?; stopline "$S/c2.txt" | san
mv "$T/build/e186-raw" "$S/raw-c1"
echo '{"process": 1}' > "$BOXT/build/claims-v3/aifoundry3/e186/p18610/train.jsonl"
RB_DESKTEST=1 K6E186_COLLECT="$S/standin-collect.sh" bash "$R/s22_collect_e186.sh" > "$S/c3.txt" 2>&1; c3=$?; stopline "$S/c3.txt" | san
mv "$T/build/e186-raw" "$S/raw-c3"
cp "$RB_OUT/window.env" "$S/window-keep.env"
bash "$R/s02_window_e186.sh" "$TODAY" "$(TZ=America/Los_Angeles gdate -d '-1 min' +%H:%M)" "$(TZ=America/Los_Angeles gdate -d '+5 min' +%H:%M)" > /dev/null 2>&1
: > "$S/calls.log"
bash "$R/s22_collect_e186.sh" > "$S/c4.txt" 2>&1; c4=$?; stopline "$S/c4.txt" | san; nc4=$(grep -c . "$S/calls.log")
cp "$S/window-keep.env" "$RB_OUT/window.env"
ok "$c1.$cx.$cg.$ch.$c2.$(has 'already holds files' "$S/c2.txt").$c3.$(has 'COPY-BACK DIFFERS' "$S/c3.txt").$c4.$nc4" "14.1.1.1.10.1.16.1.16.0" \
  "C COPY-BACK EXACT ($nm files), the history check OK before any scoring, then the C gate (14, by design); C2 a used output refused (10); C3 a changed box file: COPY-BACK DIFFERS (16); C4 the last end 5 minutes away: refused (16) before any call"

step "Z. no process of this test left running"
sleep 2
zs=$(leftovers)
ok "$zs" "0" "Z nothing left running"

echo
echo "SELFTEST-RB-E186 $npass of $ncase $([ "$fail" -eq 0 ] && echo PASS || echo FAIL)"
exit "$fail"
