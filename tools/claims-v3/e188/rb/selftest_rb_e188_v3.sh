#!/usr/bin/env bash
# E188 (Q182, the kit's dated note 2, KIT.md.dated-note-2.md, Sun 15 Nov 2026, before any E188 datum): the runbook desk test v3, with a FAKE
# ssh and rsync on a stand-in box, on either desk: the Intel (macOS) or aifoundry2 (Linux). It is v2's (rb/selftest_rb_e188_v2.sh, 16b41cf2,
# which stays as committed; on aifoundry2 it reads 12 of 16: BSD sed's `sed -i ''` in its setup and cases, step 2 v1's /usr/bin/lockf
# and its forecast byte check under 3.12, and S1's grep for Homebrew's GCC), with these changes, each marked "note 2":
#   - PORTED: GNU date as gdate (the Intel's Homebrew name) or as date when it is GNU's (Linux); the lab-git lock's nested case N with
#     /usr/bin/lockf where it exists, else /usr/bin/flock (-n outside, the step's own short wait and exit 75 inside: the same 16); every
#     in-place edit through sedi (a copy written back: GNU and BSD sed differ on -i); S1 reads the stand-in build's compiler line as
#     "with g++-13 (", whatever its vendor (Homebrew's on the Intel, Ubuntu's here);
#   - the steps note 2 changes: STEP 2 v3 (rb/s03_desk_e188_v3.sh) in K, W1-W3, G, N, P1-P9, F1 and H1; STEP 11 v2 (rb/s22_collect_e188_v2.sh)
#     in C, C0 and C5; the dry listing v3 (rb/list_steps_e188_v3.sh) in A; step 9 v2 and step 10 unchanged (RS, RS3, L, O);
#   - the committed lists stay real in the scratch tree (the registration's 20, the kit's 106, note 1's 2 and 10, A2's 1; the kit list
#     names rtl-sim/fma_toggle_v2/accum.c, copied in), with no stand-in for any log they hold: only note 2's own list and its logs get
#     stand-ins (the tests, this one among them, write those logs, and the list holds them), and the scratch copy of step 2 v3 pins the
#     stand-in list's count and bytes in its N2PINS line, the one line this test changes in a copy;
#   - new cases: D2 step 2 v3 is v1's code with exactly note 2's lines, and step 11 v2 and the dry listing v3 likewise against theirs; N a
#     step 2 v3 inside the lab-git lock stops with 16 naming its pull; P1 also reads the pull's lock tool in the runbook log and
#     FORECAST-TOL-E188 PASS; P6-P7 read note 1's real lists; P8 A2's list one line short; P9 note 2's list one line short; F1 the
#     forecast's last digit and its registration line rewritten together (16 at the registration's pin and at the forecast check); C0 step 11
#     v2 with HOME set but empty: 10 before any copy; C5 the desk-path gate end to end on this desk: a session whose scored output names
#     aifoundry3's own tree under the desk's home, step 11 v1 stops at k6's rb_nopath (16) and step 11 v2 collects it (0), and a desk path
#     beside it stops step 11 v2 (16);
#   - added by fix-port188 (Sun 15 Nov 2026, on verify-port188's finding 1, before the land): T a module _strptime.py committed at the
#     lab's top runs in step 1 and passes the history check, and rb/check_top_e188.py alone and step 2 v3 refuse it (16); an untracked
#     json.py there stops step 2 v3 (16) unread; so does an untracked re.py in tools/claims-v3/e183/rb/ (16), which the history check
#     reads OK; the dry listing names the check three times; T11 step 11 v2 on C5's staged session with an
#     untracked json.py at the top stops (16) after the copy-back and the history check, before any scoring, the module unread; D2's
#     counts follow (step 2 v3 25 lines in; step 11 v2 5 out and 11 in);
#   - v2's X3, N1, U, R, V, N6 and LJ (steps 6 and 8, unchanged by notes 1 and 2) stay v1's committed log's, as v2 left them.
# On a box with a card (aifoundry2) run it only inside a sandbox with no /dev/et* and an empty /run/lock: case L launches the real
# session_e188.sh on the stand-in box (it stops at its harness check, no device opened).
#   bash tools/claims-v3/e188/rb/selftest_rb_e188_v3.sh <scratch dir> > <log>      (SELFTEST-RB-E188-V3 <n> of <m> PASS or FAIL; exit 0 or 1)
# v2's words follow:
# E188 (Q165, the kit's dated note 1, KIT.md.dated-note-1.md, Thu 12 Nov 2026, before any E188 datum): the runbook desk test v2, with a FAKE
# ssh and rsync on a stand-in box. It is v1's (rb/selftest_rb_e188.sh, 726a6b64, which stays as committed): its setup (the scratch repository
# with an origin, the closure trace, the stand-in box, the GCC -O2 stand-in cmake, the stand-in ssh and rsync) and every case that runs
# step 2 or step 9, run on STEP 2 v2 (rb/s03_desk_e188_v2.sh) and STEP 9 v2 (rb/s11_a3_session_e188_v2.sh, THE REST RULE v2), with these
# changes, each marked "note 1":
#   - the setup also writes stand-ins of note 1's two lists (SHA256SUMS-e188-a1 and SHA256SUMS-e188-kit-note1, from the scratch tree's own
#     note 1 files) and of note 1's three logs, and pins the two lists' counts and bytes in the scratch copy of step 2 v2 (the line this
#     test changes in a copy, as v1 changes KITPIN in step 2 v1's); the kit list's stand-in leaves note 1's files out, as the real kit list
#     (made before note 1) does;
#   - A runs the dry listing v2 (rb/list_steps_e188_v2.sh): step 2 v2 once, and the rest rule v2's lines in step 9 v2 on both paths;
#   - P5's unknown list is read among the lists step 2 v1 reports (note 1's two are reported by v1 too; v2 pins them);
#   - P6 (new) note 1's kit list one line short, committed and then taken as the anchor (so the history check, which reads changes after
#     it, cannot see it): step 2 v1 passes and step 2 v2 refuses (16), naming the list against its pin; P7 (new) a file of the registration's
#     dated amendment A1 and its line in SHA256SUMS-e188-a1 rewritten together, the same way: 16, "own" bytes against the pin;
#   - RS3 (new) THE REST RULE v2 THROUGH STEP 9 v2 (verify-e188's fault 3 on the stand-in box): an E188-form session on the box cut
#     mid-queue (its session.log silent since "queue starts" 95 minutes ago; its queue.out and a train block's telemetry written 10 minutes
#     ago): step 9 v2 refused (10), naming E188, nothing launched; its files are then moved aside for L;
#   - the cases that run neither step 2 nor step 9 (X3, N1, U, R, V, N6, LJ: steps 6 and 8, unchanged by note 1) are not run here: v1's
#     committed log (logs/selftest-rb-e188.txt, 21 of 21) holds them. S1 and D stay (step 9's launch needs today's build and dry pass).
#   bash tools/claims-v3/e188/rb/selftest_rb_e188_v2.sh <scratch dir> > <log>
# v1's header follows:
# E188 (Q165, the kit): the desk test of E188's runbook with a FAKE ssh and rsync on a stand-in box. Its setup is E186's runbook desk test's
# (tools/claims-v3/e186/rb/selftest_rb_e186.sh, itself E182's: a scratch git repository with an origin holding the lab files the steps
# read; a stand-in box laid out like aifoundry3's ~/aifoundry; stand-in ssh and rsync first on PATH that serve it and refuse any other host;
# the network cut) with E188's steps and cases, and two changes: the scratch repository holds tools/claims-v3, the workload and the files
# E188's step 2 reads by a run-time trace (rb/closure_e188.py), so step 2 runs there as committed; and the stand-in box's cmake is
# rb/fake_cmake_gcc_e188.sh, which builds the patched host with g++-13 at -O2 (the box's compiler family and the host's own flag) against the
# recording mock, so step 6 reads the train change from a real GCC -O2 binary's BEHAVIOUR (E183's kit note 4's lesson). No lab box is
# reached; everything runs in <scratch dir> (never the lab clone); the bounds are rb_run.py's own (the test refuses to start if any
# RB_<CLS>_S is set). The kit's own list is made after this test (it holds this test's log), so the scratch copy of step 2 pins a stand-in
# list's count and bytes in its KITPIN line, the one line this test changes in a copy (E183's step 2 v5 desk test did the same). Cases:
#   A   the dry listing (FULL and the fallback, the look before the post): every step exits 0, the stand-ins see no ssh or rsync call;
#   K   step 2 with no window in RB_OUT refuses (10), and no call is made;
#   W1  a window written yesterday: 10; W2 one written for another runbook (RB_PLAN e186): 10; W3 step 1 with a day not today: 10;
#   G   step 2 with no RB_GITLOCK: 10 (THE LAB-GIT LOCK);
#   P1  step 2 on the scratch repository: 0, every list at its count and bytes, HISTORY OK, the plan and forecast re-made;
#   P2  the registration's list one line short: 16, named against its pin; P3 a file and its line rewritten together (the count kept, every
#       entry OK): 16, "its own bytes differ from the pin"; P4 the kit's list one line short: 16; P5 a list with SHA256SUMS in the middle of
#       its name (notes-SHA256SUMS-x): reported, never a gate (0);
#   H1  a committed edit of a kit file (score_e188.py): 16 by the history check, naming the file;
#   S1  step 5 on a clean stand-in box, its stand-in binaries and pins, then step 6 start and wait (the GCC -O2 stand-in cmake): 0, the build
#       counted once, TRAIN-CHANGE OK read on the box from the built host's behaviour, HARNESS OK 79, six 60 s reads, no call past a bound;
#   X3  a second start after the good build: refused (10);
#   N1  the wait call cut (ssh's 255, nothing printed): 14 "no reading of the build job", nothing counted; then wait reads the good build;
#   D   step 8 (the trains' dry job) on the box step 6 left: rc 0, with 18810, 18811, 18820, the smoke and the start gate's 8;
#   O   a card session of ours on the box (the stand-in pgrep reports one): step 5, step 6's start, step 8's start and step 9's launch refused;
#   U   THE NEGATIVE CONTROL THROUGH THE RUNBOOK: a fresh day, the stand-in cmake building E78's unpatched host (FAKE_CMAKE_UNPATCHED=1): the
#       build's own behavioural check reads TRAIN-CHANGE MISSING, the build counts as failed, no build record is left, one re-run asked (16);
#   R   the re-run rule with REAL failed builds (a fresh day; the stand-in build fails): 16 with one re-run; 16 naming the fallback; a
#       third start 16; then the fallback: step 6 --no-trains 0 (HARNESS OK 76), step 8 --no-trains rc 0;
#   V   the box build under its bound: a stand-in cmake that sleeps 90 s (past the 60 s a read gets): the detached job, waited on;
#   N6  the first check's read after the good build cut: 14 "no reading of inputs", never 16; wait then reads 0;
#   LJ  a lost job (its processes killed mid-build): JOB-LOST is a build's failure: one re-run asked for (16);
#   RS  THE REST RULE THROUGH STEP 9: a real E185-form session log on the box ended 10 minutes ago: step 9 refused (10) naming E185, nothing
#       launched; RS2 an E183-form session log (as its kit note 4 writes it) ended 45 minutes ago: step 9 launches (L);
#   L   step 9 FULL yes on the box with the committed binaries' pins put back (step 5 again): the session stops at its own harness check
#       (exit 9, no device opened) and writes its MANIFEST.sha256; step 10 reads it ended at a gate (16) with the manifest written;
#   C   step 11 on a session staged on the box: the copies by name, COPY-BACK EXACT, the history check (HISTORY OK), then the C-session gate
#       stops it (14) because the staged session holds no C log, by design; C2 a second collection into the used output: 10; C3 one byte of
#       a box file changed after the manifest: COPY-BACK DIFFERS (16); C4 the window's last end 5 minutes away: 16 before any call;
#   Z   no process of this test is left running.
#
#   bash tools/claims-v3/e188/rb/selftest_rb_e188.sh <scratch dir> > <log>
# SPDX-License-Identifier: Apache-2.0
set -u
SRC=$(cd "$(dirname "${BASH_SOURCE[0]}")/../../../.." && pwd)
S=${1:?a scratch directory outside the repository}
case "$S" in "$SRC"|"$SRC"/*) echo "the scratch directory must be outside the repository"; exit 2 ;; esac
for v in RB_PROBE_S RB_READ_S RB_COPY_S RB_WAIT_S RB_LAUNCH_S RB_DESK_S E188_BUILD_S RB_DESKTEST RB_GITLOCK; do
  [ -z "${!v:-}" ] || { echo "$v is set: this test runs with rb_run.py's own bounds and no desk-test override in its environment"; exit 2; }
done
for c in timeout sha256sum g++-13; do command -v "$c" > /dev/null || { echo "no $c on PATH"; exit 2; }; done     # note 2: gdate below
GDATE=$(command -v gdate 2> /dev/null) || GDATE=""                                                                # note 2: GNU date, either name
if [ -z "$GDATE" ] && date --version 2> /dev/null | grep -q 'GNU coreutils'; then GDATE=$(command -v date); fi
[ -n "$GDATE" ] || { echo "no GNU date on PATH (neither gdate nor a GNU date)"; exit 2; }
if [ -x /usr/bin/lockf ]; then LOCKTOOL=lockf; elif [ -x /usr/bin/flock ]; then LOCKTOOL=flock; else echo "neither /usr/bin/lockf nor /usr/bin/flock"; exit 2; fi
sedi() {  # note 2: sedi <sed arguments> <file>: sed in place, the same on GNU and BSD sed (the output written back over the file)
  local f=${!#} tf; tf=$(mktemp "${TMPDIR:-/tmp}/sedi.XXXXXX") || return 2
  sed "${@:1:$(($# - 1))}" "$f" > "$tf" && cat "$tf" > "$f"; local r=$?; rm -f "${tf:?}"; return "$r"
}
REAL_TIMEOUT=$(command -v timeout)
mkdir -p "$S"
S=$(cd "$S" && pwd)
for d in tree box bin out boxbin origin.git out-k out-w out-p out-b dry-out out-n; do [ -e "$S/$d" ] && { echo "$S/$d exists: give an empty scratch directory"; exit 2; }; done
T=$S/tree; B=$S/box; BIN=$S/bin
mkdir -p "$T/tools/claims-v3" "$T/workloads" "$B/aifoundry3/aifoundry" "$BIN" "$S/out" "$S/boxbin"
rsync -a --exclude __pycache__ "$SRC/tools/claims-v3/" "$T/tools/claims-v3/"
( cd "$SRC" && git ls-files workloads/sparsity ) | while IFS= read -r f; do mkdir -p "$T/$(dirname "$f")"; cp -p "$SRC/$f" "$T/$f"; done
/usr/bin/python3 -B "$SRC/tools/claims-v3/e188/rb/closure_e188.py" "$SRC" > "$S/closure.txt" || { echo "the closure trace failed"; exit 2; }
n0=0; while IFS= read -r f; do [ -e "$T/$f" ] || { mkdir -p "$T/$(dirname "$f")"; cp -p "$SRC/$f" "$T/$f"; n0=$((n0 + 1)); }; done < "$S/closure.txt"
# note 2: the committed lists stay real (every file they name is in the scratch tree; the kit list names rtl-sim/fma_toggle_v2/accum.c);
# only note 2's own list and its logs get stand-ins, and the scratch copy of step 2 v3 pins the stand-in list in its N2PINS line
mkdir -p "$T/rtl-sim/fma_toggle_v2"; cp -p "$SRC/rtl-sim/fma_toggle_v2/accum.c" "$T/rtl-sim/fma_toggle_v2/accum.c"
KITN=$(grep -c . "$T/tools/claims-v3/e188/SHA256SUMS-e188-kit")
N1N=$(grep -c . "$T/tools/claims-v3/e188/SHA256SUMS-e188-kit-note1"); A1N=$(grep -c . "$T/tools/claims-v3/e188/SHA256SUMS-e188-a1")
N2_FILES="KIT.md.dated-note-2.md CARD-LANE-BRIEF.md.dated-note-2.md forecast_tol_e188.py selftest_forecast_tol_e188.py desk/gnudate_e188.sh
desk/desktest_realpath_e188.sh desk/mock_rt_e188_clock.cpp desk/reruns_note2_e188.sh rb/rb_e188_n2.sh rb/s22_collect_e188_v2.sh rb/list_steps_e188_v3.sh rb/selftest_rb_e188_v3.sh
rb/selftest_wait_e188.sh rb/check_top_e188.py logs/selftest-forecast-tol-e188.txt logs/selftest-rb-e188-v3.txt logs/selftest-wait-e188.txt logs/desktest-realpath-e188.txt
logs/dry-listing-e188-v3.txt logs/reruns-note2-e188.txt logs/port-aifoundry2-e188.txt"
for spec in "selftest-forecast-tol-e188.txt SELFTEST-FORECAST-TOL-E188 PASS (0 of 0)" "selftest-rb-e188-v3.txt SELFTEST-RB-E188-V3 0 of 0 PASS" \
            "selftest-wait-e188.txt SELFTEST-WAIT-E188 PASS (0 of 0)" "desktest-realpath-e188.txt DESKTEST-REALPATH-E188 PASS (0 of 0)" \
            "dry-listing-e188-v3.txt dry listing: 19 steps listed, 0 exited non-zero, 0 box calls" "reruns-note2-e188.txt RERUNS-NOTE2-E188 PASS (0 of 0)" \
            "port-aifoundry2-e188.txt (the port's record)"; do
  f=${spec%% *}
  [ -f "$T/tools/claims-v3/e188/logs/$f" ] || printf '(a stand-in written by the runbook desk test v3 for its case P1)\n%s\n' "${spec#* }" > "$T/tools/claims-v3/e188/logs/$f"
done
( cd "$T" && for f in $N2_FILES; do [ -f "tools/claims-v3/e188/$f" ] && sha256sum "tools/claims-v3/e188/$f"; done
  for f in tools/claims-v3/e183/rb/nopath_desk_e183.sh tools/claims-v3/e183/rb/nopath_spell_e183.py; do sha256sum "$f"; done ) > "$T/tools/claims-v3/e188/SHA256SUMS-e188-kit-note2"
N2N=$(grep -c . "$T/tools/claims-v3/e188/SHA256SUMS-e188-kit-note2"); N2H=$(sha256sum "$T/tools/claims-v3/e188/SHA256SUMS-e188-kit-note2" | cut -d' ' -f1)
sedi -e "s#^tools/claims-v3/e188/SHA256SUMS-e188-kit-note2:[0-9]*:[0-9a-f]*\"\$#tools/claims-v3/e188/SHA256SUMS-e188-kit-note2:$N2N:$N2H\"#" "$T/tools/claims-v3/e188/rb/s03_desk_e188_v3.sh"
grep -q "^tools/claims-v3/e188/SHA256SUMS-e188-kit-note2:$N2N:$N2H\"\$" "$T/tools/claims-v3/e188/rb/s03_desk_e188_v3.sh" || { echo "the scratch step 2 v3's note 2 pin was not set"; exit 2; }
echo "note 2's stand-ins: SHA256SUMS-e188-kit-note2 $N2N entries, pinned in the scratch copy of step 2 v3; the kit list ($KITN), note 1's ($A1N, $N1N) and A2's real"
G="git -C $T -c user.name=e188-desktest -c user.email=desktest@localhost -c core.hooksPath=/dev/null -c commit.gpgsign=false"
$G init -q && $G add -A && $G commit -q -m "E188 runbook desk test: the lab files the steps read" || { echo "the scratch repository failed"; exit 2; }
git clone -q --bare "$T" "$S/origin.git" && $G remote add origin "$S/origin.git" && $G fetch -q origin &&
  $G branch -q -u "origin/$($G rev-parse --abbrev-ref HEAD)" || { echo "the scratch repository's origin failed"; exit 2; }
BASE0=$($G rev-list --max-parents=0 HEAD)
echo "scratch repository: $($G ls-files | wc -l | tr -d ' ') files committed ($n0 of them by the closure trace beside tools/claims-v3 and the workload), with an origin; the kit list real ($KITN files); note 2's list a stand-in ($N2N)"     # note 2
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
R=$T/tools/claims-v3/e188/rb
BOXT=$B/aifoundry3/aifoundry
J=$BOXT/build/q141k/jobs
printf '#!/bin/sh\necho aifoundry3\n' > "$S/boxbin/hostname"
printf '#!/bin/sh\nexec "%s" "$@"\n' "$GDATE" > "$S/boxbin/date"     # note 2
printf '#!/bin/sh\nexec /usr/bin/python3 "$@"\n' > "$S/boxbin/python3"
printf '#!/bin/sh\necho "(desk test: no et-who here)"\n' > "$S/boxbin/et-who"
printf '#!/bin/sh\n[ -e "%s" ] && { echo 4242; exit 0; }\nexit 1\n' "$S/ours-live.flag" > "$S/boxbin/pgrep"
for n in ssh rsync scp sudo flock; do printf '#!/bin/sh\necho "%s $*" >> "%s"\necho "BOX STAND-IN: %s refused" >&2\nexit 97\n' "$n" "$S/dry-network.log" "$n" > "$S/boxbin/$n"; done
printf '#!/bin/sh\nexec "$@"\n' > "$S/boxbin/setsid"
printf '#!/bin/sh\nexec "%s" "$@"\n' "$REAL_TIMEOUT" > "$S/boxbin/timeout"
cp -p "$SRC/tools/claims-v3/e188/rb/fake_cmake_gcc_e188.sh" "$S/boxbin/cmake"
chmod +x "$BIN/ssh" "$BIN/rsync" "$S/boxbin"/*
export PATH="$BIN:$PATH" RB_REPO="$T" RB_OUT="$S/out" RB_LOCK="$S/lock.txt" FAKE_CMAKE_MOCKRT="$T/tools/claims-v3/ccheck/mockrt"
export FAKE_CMAKE_MOCK="$T/tools/claims-v3/e188/desk/mock_rt_e188.cpp" FAKE_CMAKE_UNPATCHED_SRC="$T/workloads/sparsity/host/main.cpp" FAKE_CMAKE_SLEEP_S=0
export RB_E188_BASE=$BASE0
: > "$S/calls.log"; : > "$RB_LOCK"; : > "$S/dry-network.log"; : > "$S/gitlock"; rm -f "$S/ours-live.flag" "$S/ssh-fail-at"
fail=0; npass=0; ncase=0
ok() { ncase=$((ncase + 1)); if [ "$1" = "$2" ]; then npass=$((npass + 1)); echo "-> PASS ($3)"; else echo "-> FAIL ($3: got $1, want $2)"; fail=1; fi; }
step() { echo; echo "== $*"; }
san() { sed -e "s#$S#<scratch>#g"; }
nlog() { if [ -f "$RB_OUT/runbook.log" ]; then grep -c . "$RB_OUT/runbook.log"; else echo 0; fi; }
since() { tail -n +"$(( $1 + 1 ))" "$RB_OUT/runbook.log" 2>/dev/null; }
TODAY=$(TZ=America/Los_Angeles "$GDATE" +%F)
AT=$BOXT/build/e188-build-attempts.txt
builds() { if [ -f "$AT" ]; then echo $(( $(grep -c "^$TODAY .* a3-build-e188 started\$" "$AT") - $(grep -c "^$TODAY .* a3-build-e188 ended rc=[0-9]*: TRAIN-HOST-INPUTS-DIFFER" "$AT") )); else echo 0; fi; }
fresh_day() {
  rm -f "${AT:?}"; rm -rf "${BOXT:?}/build/e188-build-logs"
  for x in rc out; do [ -e "$J/a3-build-e188.$x" ] && touch -t "$("$GDATE" -d '-2 day' +%Y%m%d%H%M)" "$J/a3-build-e188.$x"; done
  return 0
}
pin_standins() {
  /usr/bin/python3 -B - "$BOXT" <<'PY'
import hashlib, json, os, sys
t = sys.argv[1]
p = os.path.join(t, "tools/claims-v3/e188/harness-e188.json")
h = json.load(open(p))
for rel in h["box_binaries_sha256"]:
    h["box_binaries_sha256"][rel] = hashlib.sha256(open(os.path.join(t, rel), "rb").read()).hexdigest()
open(p, "w").write(json.dumps(h, indent=1) + "\n")
print("the stand-in box's harness-e188.json now pins its 4 stand-in binaries")
PY
}
leftovers() { pgrep -f "$S/boxbin/cmake|bash build/q141k/jobs/a3-build-e188[.]sh|tools/claims-v3/e188/build_host_e188[.]sh|session_e188[.]sh" 2>/dev/null | grep -c .; }
b6() { bash "$R/s08_a3_build_e188.sh" "$@"; }
netcut() { echo "${1:-1}" > "$S/ssh-fail-at"; }
stopline() { grep -a 'STOP' "$1" | tail -n 1 | cut -c1-330; }
waitb() {  # waitb <out> [<max calls>]: step 6's wait, again while it says 17; prints "<rc> <number of 17s>"
  local o=$1 m=${2:-12} k r n17=0
  : > "$o"
  for k in $(seq 1 "$m"); do b6 wait >> "$o" 2>&1; r=$?; [ "$r" -eq 17 ] || break; n17=$((n17 + 1)); done
  echo "$r $n17"
}
wait10() { local o=$1 x=${2:-} k r; for k in 1 2 3 4 5 6 7 8; do bash "$R/s10_a3_dry_e188.sh" wait $x > "$o" 2>&1; r=$?; [ "$r" -eq 17 ] || break; done; return "$r"; }
has() { grep -aq -- "$1" "$2" && echo 1 || echo 0; }
killtree() {
  local p=$1 c kids; kids=$(pgrep -P "$p" 2>/dev/null); kill -STOP "$p" 2>/dev/null
  for c in $kids; do killtree "$c"; done; kill -KILL "$p" 2>/dev/null
}
cd "$T" || exit 2

step "A. the dry listing v3 (FULL and the fallback, the look before the post): every step exits 0, no ssh or rsync call"
: > "$S/calls.log"
bash "$R/list_steps_e188_v3.sh" "$S/dry-out" > "$S/dry-listing.txt" 2>&1; rc=$?
n=$(grep -c . "$S/calls.log"); tail -n 1 "$S/dry-listing.txt"
lp=$(awk '/s05_look_k6.sh aifoundry3$/ {l=NR} /the day.s one post, made AFTER the look/ {p=NR} END {print (l > 0 && p > l) ? 1 : 0}' "$S/dry-listing.txt")
n6=$(grep -c '^################ tools/claims-v3/e188/rb/s08_a3_build_e188.sh' "$S/dry-listing.txt"); n2=$(grep -c '^################ tools/claims-v3/e188/rb/s03_desk_e188_v3[.]sh' "$S/dry-listing.txt")
n11=$(grep -c '^################ tools/claims-v3/e188/rb/s22_collect_e188_v2[.]sh' "$S/dry-listing.txt"); cb=$(grep -c 'COPY-BACK EXACT against the session' "$S/dry-listing.txt")
rr=$(grep -c 'E188 starts on a rested card' "$S/dry-listing.txt")
r2=$(grep -c '^    | latest_write() {  # note 1' "$S/dry-listing.txt"); r1=$(grep -c '^################ tools/claims-v3/e188/rb/s11_a3_session_e188_v2[.]sh' "$S/dry-listing.txt")
ec=$(grep -c "^--- check (note 5), before any copy: HOME resolves to this account's home" "$S/dry-listing.txt"); gl=$(grep -c '^--- gate (note 5): no desk path' "$S/dry-listing.txt")     # note 2
lk=$(grep -cE 'run on the desk \(git pull --ff-only under the lab-git lock\): /usr/bin/(lockf -k -t 600|flock -w 600 -E 75) <RB_GITLOCK>' "$S/dry-listing.txt")       # note 2
bc=$(grep -c ', 0 exited non-zero, 0 box calls$' "$S/dry-listing.txt")                                                                                           # note 2
ok "$rc.$n.$lp.$n6.$n2.$n11.$cb.$([ "$rr" -ge 2 ] && echo 1 || echo 0).$r2.$r1.$ec.$gl.$lk.$bc" "0.0.1.3.1.2.2.1.2.2.2.2.1.1" "A the dry listing v3: 0 failing, no call (0 box calls), the look before the post, step 6 three times, step 2 v3 once with its pull's lock tool, step 11 v2 twice with its exact copy-back, its early check and its gate, step 9 v2 on both paths with the rest rule v2's lines"

step "D2 (note 2). step 2 v3, step 11 v2 and the dry listing v3 against the committed versions they come from (their code lines, comments aside)"
dl() { diff <(grep -v '^#' "$1") <(grep -v '^#' "$2") | grep -c "^$3"; }
E8=$T/tools/claims-v3/e188/rb
d2a=$(dl "$E8/s03_desk_e188.sh" "$SRC/tools/claims-v3/e188/rb/s03_desk_e188_v3.sh" '<'); d2b=$(dl "$E8/s03_desk_e188.sh" "$SRC/tools/claims-v3/e188/rb/s03_desk_e188_v3.sh" '>')
d11a=$(dl "$E8/s22_collect_e188.sh" "$E8/s22_collect_e188_v2.sh" '<'); d11b=$(dl "$E8/s22_collect_e188.sh" "$E8/s22_collect_e188_v2.sh" '>')
dla=$(dl "$E8/list_steps_e188_v2.sh" "$E8/list_steps_e188_v3.sh" '<'); dlb=$(dl "$E8/list_steps_e188_v2.sh" "$E8/list_steps_e188_v3.sh" '>')
nm=$(diff <(grep -v '^#' "$E8/s03_desk_e188.sh") <(grep -v '^#' "$SRC/tools/claims-v3/e188/rb/s03_desk_e188_v3.sh") | grep '^>' | grep -vc 'note 2\|^> tools/claims-v3/e188/SHA256SUMS-e188-\|^> N2PINS=\|^> for spec in\|^>             "logs/\|^>   set -- \|^>   rb_local read local "a desk\|^>   rb_has .\^1\$. || bad\|^> done$\|^> pyv=\|^> rb_say "desk check v3')
echo "step 2 v3 against v1: $d2a lines out, $d2b in ($nm in that neither carry 'note 2' nor belong to note 2's two added blocks); step 11 v2 against v1: $d11a out, $d11b in; the dry listing v3 against v2: $dla out, $dlb in"
ok "$d2a.$d2b.$nm.$d11a.$d11b.$dla.$dlb" "7.25.0.5.11.5.10" "D2 step 2 v3 is v1's code but 7 lines out and 25 in, every one note 2's; step 11 v2 is v1's but 5 out and 11 in; the dry listing v3 is v2's but 5 out and 10 in"     # fix-port188: 22 -> 25, 3/6 -> 5/11 (the top's check)

step "K. step 2 with no window in RB_OUT (step 1 not run)"
: > "$S/calls.log"
RB_OUT="$S/out-k" RB_GITLOCK="$S/gitlock" bash "$R/s03_desk_e188_v3.sh" > "$S/k.txt" 2>&1; rc=$?
stopline "$S/k.txt" | san; n=$(grep -c . "$S/calls.log")
ok "$rc.$n.$(has 'no window in RB_OUT' "$S/k.txt")" "10.0.1" "K step 2 refuses without step 1's window, before any call"

step "W1-W3. the window rule: a window written yesterday, one written for another runbook, and step 1 with a day not today"
mkdir -p "$S/out-w"
RB_OUT="$S/out-w" bash "$R/s02_window_e188.sh" "$TODAY" 23:50 23:55 > /dev/null 2>&1
touch -t "$("$GDATE" -d '-1 day' +%Y%m%d%H%M)" "$S/out-w/window.env"
RB_OUT="$S/out-w" RB_GITLOCK="$S/gitlock" bash "$R/s03_desk_e188_v3.sh" > "$S/w1.txt" 2>&1; w1=$?; stopline "$S/w1.txt" | san
RB_OUT="$S/out-w" bash "$R/s02_window_e188.sh" "$TODAY" 23:50 23:55 > /dev/null 2>&1
sedi -e 's/^RB_PLAN=e188$/RB_PLAN=e186/' "$S/out-w/window.env"
RB_OUT="$S/out-w" RB_GITLOCK="$S/gitlock" bash "$R/s03_desk_e188_v3.sh" > "$S/w2.txt" 2>&1; w2=$?; stopline "$S/w2.txt" | san
RB_OUT="$S/out-w" bash "$R/s02_window_e188.sh" "$("$GDATE" -d '+1 day' +%F)" 10:00 12:00 > "$S/w3.txt" 2>&1; w3=$?; stopline "$S/w3.txt" | san
ok "$w1.$(has 'was not written today' "$S/w1.txt").$w2.$(has 'written for e186' "$S/w2.txt").$w3.$(has 'is not today' "$S/w3.txt")" "10.1.10.1.10.1" \
  "W1-W3 a window not written today, one for another runbook, and a window for another day are each refused (10)"

step "G. step 2 with no RB_GITLOCK (the lab-git lock)"
mkdir -p "$S/out-p"; RB_OUT="$S/out-p" bash "$R/s02_window_e188.sh" "$TODAY" 23:50 23:55 > /dev/null 2>&1
RB_OUT="$S/out-p" bash "$R/s03_desk_e188_v3.sh" > "$S/g.txt" 2>&1; rc=$?; stopline "$S/g.txt" | san
ok "$rc.$(has 'RB_GITLOCK is not set' "$S/g.txt")" "10.1" "G step 2 refuses a pull without the lab-git lock"

step "N (note 2). step 2 v3 run inside the lab-git lock (nested): its pull cannot take the lock"
mkdir -p "$S/out-n"; RB_OUT="$S/out-n" bash "$R/s02_window_e188.sh" "$TODAY" 23:50 23:55 > /dev/null 2>&1
if [ "$LOCKTOOL" = lockf ]; then
  /usr/bin/lockf -k -t 0 "$S/gitlock" env RB_DESKTEST=1 RB_GITLOCK_T=2 RB_OUT="$S/out-n" RB_GITLOCK="$S/gitlock" bash "$R/s03_desk_e188_v3.sh" > "$S/n.txt" 2>&1; nn=$?
else
  /usr/bin/flock -n -E 75 "$S/gitlock" env RB_DESKTEST=1 RB_GITLOCK_T=2 RB_OUT="$S/out-n" RB_GITLOCK="$S/gitlock" bash "$R/s03_desk_e188_v3.sh" > "$S/n.txt" 2>&1; nn=$?
fi
echo "   (the outer lock taken with $LOCKTOOL; the step's own pull waits 2 s for it with $LOCKTOOL, then exits 75)"
stopline "$S/n.txt" | san | cut -c1-300
n75=$(grep -c ' child_rc=75 status=exit 75 ' "$S/out-n/runbook.log" 2>/dev/null)
ok "$nn.$(has 'the desk check failed: pull' "$S/n.txt").$([ "$n75" -ge 1 ] && echo 1 || echo 0)" "16.1.1" "N a nested step 2 v3 stops with 16 naming its pull, the lock tool's exit 75 in the runbook log (never run step 2 inside the lock; outer lock by $LOCKTOOL)"

step "P1. step 2 v3 on the scratch repository (every listed file, an origin, the kit list real at $KITN, note 2's list a stand-in at $N2N)"
RB_OUT="$S/out-p" RB_GITLOCK="$S/gitlock" bash "$R/s03_desk_e188_v3.sh" > "$S/p1.txt" 2>&1; rc=$?
grep -E 'desk check:|STOP' "$S/p1.txt" | san | cut -c1-500
pins=$(grep -c 'the lists at their pinned counts and bytes (20; 37, 24, 1, 9; 32, 79, 50, 49, 89, 19; 10; 376, 6; 209, 16, 9, 68, 10, 160)' "$S/p1.txt")
lk=$(grep -cE "cmd=/usr/bin/$LOCKTOOL (-k -t 600|-w 600 -E 75) .*pull --ff-only" "$S/out-p/runbook.log" 2>/dev/null)     # note 2: the desk's lock tool
n2p=$(grep -c "note 1's ($A1N, $N1N), A2's (1) and note 2's ($N2N)" "$S/p1.txt")
ok "$rc.$pins.$([ "$lk" -ge 1 ] && echo 1 || echo 0).$(has 'HISTORY OK: ' "$S/p1.txt").$(has 'desk check v3 (note 2):' "$S/p1.txt").$(has '^FORECAST-TOL-E188 PASS' "$S/p1.txt").$n2p" "0.1.1.1.1.1.1" \
  "P1 step 2 v3 passes the intact tree: v1's pins and the kit's, its pull under the lab-git lock by $LOCKTOOL, HISTORY OK, the forecast within its tolerance (FORECAST-TOL-E188 PASS), note 1's, A2's and note 2's lists at their pins"

step "P2-P5. a pinned list one line short; a file and its line rewritten together; the kit's list one line short; an unknown list"
sedi -e '$d' "$T/tools/claims-v3/e188/SHA256SUMS-e188-registration"
$G commit -q -am "desk test: the registration's list one line short" || echo "the scratch commit failed"
RB_OUT="$S/out-p" RB_GITLOCK="$S/gitlock" bash "$R/s03_desk_e188_v3.sh" > "$S/p2.txt" 2>&1; p2=$?; stopline "$S/p2.txt" | san | cut -c1-300
k2=$(grep -c 'SHA256SUMS-e188-registration(19 OK of 19; pinned 20; its own bytes differ from the pin)' "$S/p2.txt")
$G reset -q --hard HEAD~1
printf ' \n' >> "$T/tools/claims-v3/e188/forecast-e188.txt"
h=$(sha256sum "$T/tools/claims-v3/e188/forecast-e188.txt" | cut -d' ' -f1)
sedi -e "s#^[0-9a-f]*  tools/claims-v3/e188/forecast-e188.txt\$#$h  tools/claims-v3/e188/forecast-e188.txt#" "$T/tools/claims-v3/e188/SHA256SUMS-e188-registration"
$G commit -q -am "desk test: a file and its line rewritten together" || echo "the scratch commit failed"
RB_OUT="$S/out-p" RB_GITLOCK="$S/gitlock" bash "$R/s03_desk_e188_v3.sh" > "$S/p3.txt" 2>&1; p3=$?; stopline "$S/p3.txt" | san | cut -c1-300
k3=$(grep -c 'SHA256SUMS-e188-registration(20 OK of 20; pinned 20; its own bytes differ from the pin)' "$S/p3.txt")
$G reset -q --hard HEAD~1
sedi -e '$d' "$T/tools/claims-v3/e188/SHA256SUMS-e188-kit"
$G commit -q -am "desk test: the kit's list one line short" || echo "the scratch commit failed"
RB_OUT="$S/out-p" RB_GITLOCK="$S/gitlock" bash "$R/s03_desk_e188_v3.sh" > "$S/p4.txt" 2>&1; p4=$?; stopline "$S/p4.txt" | san | cut -c1-300
k4=$(grep -c "SHA256SUMS-e188-kit($((KITN - 1)) OK of $((KITN - 1)); pinned $KITN; its own bytes differ from the pin)" "$S/p4.txt")
$G reset -q --hard HEAD~1
( cd "$T" && sha256sum tools/claims-v3/e188/E188.md > tools/claims-v3/e188/notes-SHA256SUMS-x )
$G add tools/claims-v3/e188/notes-SHA256SUMS-x && $G commit -q -m "desk test: an unknown list" || echo "the scratch commit failed"
RB_OUT="$S/out-p" RB_GITLOCK="$S/gitlock" bash "$R/s03_desk_e188_v3.sh" > "$S/p5.txt" 2>&1; p5=$?; stopline "$S/p5.txt" | san | cut -c1-300
k5=$(grep -c 'lists not pinned (reported):.* tools/claims-v3/e188/notes-SHA256SUMS-x' "$S/p5.txt")     # note 1: v1 reports note 1's two lists beside it
$G reset -q --hard HEAD~1
ok "$p2.$k2.$p3.$k3.$p4.$k4.$p5.$k5" "16.1.16.1.16.1.0.1" "P2-P5 each pin refused (16) and named: a short list, a rewritten list (count kept, bytes not), the kit's short list; an unknown list reported (0)"

step "P6-P7 (note 1, on step 2 v3). note 1's pins: note 1's kit list one line short; a file of the amendment A1 and its line rewritten together (each committed, then taken as the anchor, so the history check cannot see it)"
sedi -e '$d' "$T/tools/claims-v3/e188/SHA256SUMS-e188-kit-note1"
$G commit -q -am "desk test: note 1's kit list one line short" || echo "the scratch commit failed"
RB_E188_BASE=$($G rev-parse HEAD) RB_OUT="$S/out-p" RB_GITLOCK="$S/gitlock" bash "$R/s03_desk_e188_v3.sh" > "$S/p6.txt" 2>&1; p6=$?; stopline "$S/p6.txt" | san | cut -c1-300
k6v1=$(has 'HISTORY OK: ' "$S/p6.txt"); k6=$(grep -c "SHA256SUMS-e188-kit-note1($((N1N - 1)) OK of $((N1N - 1)); pinned $N1N; its own bytes differ from the pin)" "$S/p6.txt")     # note 2: v1's loop's words
$G reset -q --hard HEAD~1
printf ' \n' >> "$T/tools/claims-v3/e188/E188.md.dated-amendment-A1.md"
h=$(sha256sum "$T/tools/claims-v3/e188/E188.md.dated-amendment-A1.md" | cut -d' ' -f1)
sedi -e "s#^[0-9a-f]*  tools/claims-v3/e188/E188.md.dated-amendment-A1.md\$#$h  tools/claims-v3/e188/E188.md.dated-amendment-A1.md#" "$T/tools/claims-v3/e188/SHA256SUMS-e188-a1"
$G commit -q -am "desk test: a file of A1 and its line rewritten together" || echo "the scratch commit failed"
RB_E188_BASE=$($G rev-parse HEAD) RB_OUT="$S/out-p" RB_GITLOCK="$S/gitlock" bash "$R/s03_desk_e188_v3.sh" > "$S/p7.txt" 2>&1; p7=$?; stopline "$S/p7.txt" | san | cut -c1-300
k7v1=$(has 'HISTORY OK: ' "$S/p7.txt"); k7=$(grep -c "SHA256SUMS-e188-a1($A1N OK of $A1N; pinned $A1N; its own bytes differ from the pin)" "$S/p7.txt")     # note 2: v1's loop's words
$G reset -q --hard HEAD~1
ok "$p6.$k6v1.$k6.$p7.$k7v1.$k7" "16.1.1.16.1.1" "P6-P7 the history check passes (the change lies before the anchor), and step 2 v3 refuses (16) at note 1's pins, naming the list"

step "P8-P9, F1 (note 2). A2's list one line short; note 2's list one line short; the forecast's last digit and its registration line rewritten together (each committed, then taken as the anchor)"
sedi -e '$d' "$T/tools/claims-v3/e188/SHA256SUMS-e188-a2"
$G commit -q -am "desk test: A2's list one line short" || echo "the scratch commit failed"
RB_E188_BASE=$($G rev-parse HEAD) RB_OUT="$S/out-p" RB_GITLOCK="$S/gitlock" bash "$R/s03_desk_e188_v3.sh" > "$S/p8.txt" 2>&1; p8=$?; stopline "$S/p8.txt" | san | cut -c1-300
k8=$(grep -c 'SHA256SUMS-e188-a2(0 OK of 0; pinned 1; its own bytes differ from the pin)' "$S/p8.txt")
$G reset -q --hard HEAD~1
sedi -e '$d' "$T/tools/claims-v3/e188/SHA256SUMS-e188-kit-note2"
$G commit -q -am "desk test: note 2's list one line short" || echo "the scratch commit failed"
RB_E188_BASE=$($G rev-parse HEAD) RB_OUT="$S/out-p" RB_GITLOCK="$S/gitlock" bash "$R/s03_desk_e188_v3.sh" > "$S/p9.txt" 2>&1; p9=$?; stopline "$S/p9.txt" | san | cut -c1-300
k9=$(grep -c "SHA256SUMS-e188-kit-note2($((N2N - 1)) OK of $((N2N - 1)); pinned $N2N; its own bytes differ from the pin)" "$S/p9.txt")
$G reset -q --hard HEAD~1
FJ=$T/tools/claims-v3/e188/forecast-e188.json
grep -q '"M10_w": 8.233099847174708,' "$FJ" || echo "F1: the committed line is not where the test expects it"
sedi -e 's/"M10_w": 8.233099847174708,/"M10_w": 8.233099847174709,/' "$FJ"
h=$(sha256sum "$FJ" | cut -d' ' -f1)
sedi -e "s#^[0-9a-f]*  tools/claims-v3/e188/forecast-e188.json\$#$h  tools/claims-v3/e188/forecast-e188.json#" "$T/tools/claims-v3/e188/SHA256SUMS-e188-registration"
$G commit -q -am "desk test: the forecast's last digit and its registration line rewritten together" || echo "the scratch commit failed"
RB_E188_BASE=$($G rev-parse HEAD) RB_OUT="$S/out-p" RB_GITLOCK="$S/gitlock" bash "$R/s03_desk_e188_v3.sh" > "$S/f1.txt" 2>&1; f1=$?; stopline "$S/f1.txt" | san | cut -c1-300
kf1=$(grep -c 'SHA256SUMS-e188-registration(20 OK of 20; pinned 20; its own bytes differ from the pin)' "$S/f1.txt"); kf2=$(grep -c 'STOP: the desk check failed:.* forecast' "$S/f1.txt")
kf3=$(grep -c "^pins: .*FAIL: tools/claims-v3/e188/SHA256SUMS-e188-registration: 20 entries" "$S/f1.txt")
$G reset -q --hard HEAD~1
ok "$p8.$k8.$p9.$k9.$f1.$kf1.$kf2.$kf3" "16.1.16.1.16.1.1.1" "P8-P9, F1 step 2 v3 refuses (16): A2's short list and note 2's short list, each named against its pin; a forecast edited in its last digit with its list line rewritten, at the registration's pin and at the forecast check's own pins (the float comparison alone would admit a last-digit edit: the bytes are pinned)"

step "H1. a committed edit of a kit file (score_e188.py): the history check refuses it"
printf '\n# a desk-test edit\n' >> "$T/tools/claims-v3/e188/score_e188.py"
$G commit -q -am "desk test: a kit file edited" || echo "the scratch commit failed"
RB_OUT="$S/out-p" RB_GITLOCK="$S/gitlock" bash "$R/s03_desk_e188_v3.sh" > "$S/h1.txt" 2>&1; h1=$?; stopline "$S/h1.txt" | san | cut -c1-300
kh=$(grep -c 'history' "$S/h1.txt"); kf=$(has 'M tools/claims-v3/e188/score_e188.py' "$S/h1.txt")
$G reset -q --hard HEAD~1
ok "$h1.$([ "$kh" -ge 1 ] && echo 1 || echo 0).$kf" "16.1.1" "H1 refused (16) by the history check, naming the file"

step "T (fix-port188, on verify-port188's finding 1). the lab's top: a module _strptime.py committed there (a working copy of the standard library's, which writes a marker when imported): step 1 runs it, the history check passes it, the top's check alone and step 2 v3 refuse it; then an untracked json.py there: step 2 v3 refuses it, and nothing in step 2 v3 imports it"
cat > "$T/_strptime.py" <<EOF
# a desk-test shadow (case T): it writes a marker when imported, then runs the standard library's own _strptime, so step 1 still works
import os as _os, sysconfig as _sc
open("$S/shadow-strptime-ran", "a").write("_strptime shadow ran\n")
_p = _os.path.join(_sc.get_paths()["stdlib"], "_strptime.py")
exec(compile(open(_p).read(), _p, "exec"))
EOF
$G add _strptime.py && $G commit -q -m "desk test: a module _strptime.py at the lab's top (case T)" || echo "the scratch commit failed"
mkdir -p "$S/out-t"; rm -f "$S/shadow-strptime-ran" "$S/shadow-json-ran"
RB_OUT="$S/out-t" bash "$R/s02_window_e188.sh" "$TODAY" 23:50 23:55 > "$S/t1w.txt" 2>&1; t1s=$?
t1m=$([ -s "$S/shadow-strptime-ran" ] && echo 1 || echo 0)
echo "   step 1 on that tree: rc $t1s; the shadow's marker written: $t1m (why the brief reads the top's check right before step 1)"
( cd "$T" && /usr/bin/python3 -I -B "$R/check_top_e188.py" ) > "$S/t1d.txt" 2>&1; t1d=$?; cut -c1-200 "$S/t1d.txt" | san
RB_OUT="$S/out-t" RB_GITLOCK="$S/gitlock" bash "$R/s03_desk_e188_v3.sh" > "$S/t1.txt" 2>&1; t1=$?; stopline "$S/t1.txt" | san | cut -c1-300
t1h=$(has 'HISTORY OK: ' "$S/t1.txt"); t1k=$(grep -c 'the desk check failed:.* top' "$S/t1.txt")
$G reset -q --hard HEAD~1
cat > "$T/json.py" <<EOF
open("$S/shadow-json-ran", "a").write("json shadow ran\n")
EOF
RB_OUT="$S/out-t" RB_GITLOCK="$S/gitlock" bash "$R/s03_desk_e188_v3.sh" > "$S/t2.txt" 2>&1; t2=$?; stopline "$S/t2.txt" | san | cut -c1-300
t2k=$(has 'TOP REFUSED: .*json.py' "$S/t2.txt"); t2m=$([ -e "$S/shadow-json-ran" ] && echo 1 || echo 0)
rm -f "${T:?}/json.py"
printf '# a desk-test shadow (case T3): an untracked module beside nopath_spell_e183.py\n' > "$T/tools/claims-v3/e183/rb/re.py"
RB_OUT="$S/out-t" RB_GITLOCK="$S/gitlock" bash "$R/s03_desk_e188_v3.sh" > "$S/t3.txt" 2>&1; t3=$?; stopline "$S/t3.txt" | san | cut -c1-300
t3k=$(has 'TOP REFUSED: tools/claims-v3/e183/rb/re.py' "$S/t3.txt"); t3h=$(has 'HISTORY OK: ' "$S/t3.txt")
rm -f "${T:?}/tools/claims-v3/e183/rb/re.py"
tl=$(grep -c 'check_top_e188[.]py' "$S/dry-listing.txt")
ok "$t1s.$t1m.$t1d.$t1h.$t1.$t1k.$t2.$t2k.$t2m.$t3.$t3k.$t3h.$tl" "0.1.16.1.16.1.16.1.0.16.1.1.3" \
  "T a committed _strptime.py at the top runs in step 1 (rc 0, its marker written) and passes the history check (HISTORY OK); check_top_e188.py alone refuses it (16) and step 2 v3 stops (16, 'top'); an untracked json.py there: step 2 v3 stops (16, TOP REFUSED naming it) and no step-2 process imported it; an untracked re.py in tools/claims-v3/e183/rb/ (step 11 v2's nopath_spell_e183.py runs there): HISTORY OK, and step 2 v3 stops (16, TOP REFUSED naming it); the dry listing names the check 3 times (step 2 v3 once, step 11 v2 on both paths)"

# ---- the box's side, through the fake ssh
export RB_OUT="$S/out-b"; mkdir -p "$RB_OUT"
wd=$(TZ=America/Los_Angeles "$GDATE" -d '+3 hour' +%F); le_=$(TZ=America/Los_Angeles "$GDATE" -d '+3 hour' +%H:%M)
if [ "$wd" = "$TODAY" ]; then
  if [ "$(TZ=America/Los_Angeles "$GDATE" -d '+30 min' +%F)" = "$wd" ]; then ls_=$(TZ=America/Los_Angeles "$GDATE" -d '+30 min' +%H:%M); else ls_=23:58; fi
else le_=23:59; ls_=$(TZ=America/Los_Angeles "$GDATE" -d '+30 min' +%H:%M); wd=$TODAY; fi
bash "$R/s02_window_e188.sh" "$wd" "$ls_" "$le_" > "$S/b-window.txt" 2>&1 || { echo "the window failed: $(tail -2 "$S/b-window.txt")"; fail=1; }

step "S1. step 5 on a clean stand-in box, its stand-in binaries and pins, then step 6 start and wait (the GCC -O2 stand-in cmake)"
mkdir -p "$BOXT"
bash "$R/s07_a3_sync_e188.sh" > "$S/s1-sync.txt" 2>&1; rs=$?
grep -E 'synced to|STOP' "$S/s1-sync.txt" | san | cut -c1-220
for f in build/sparsity/host/sparsity_host build/ccheck/b/host/sparsity_host build/ettelem/ettelem; do
  mkdir -p "$BOXT/$(dirname "$f")"
  printf '#!/bin/sh\necho "STUB EXECUTED: %s $*" >&2\nexit 97\n' "$f" > "$BOXT/$f"
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
grep -aE '^E188-BUILD-ATTEMPT|^TRAIN-HOST-BUILT|^TRAIN-CHANGE|^NOTE1 FILES OK|^HARNESS|^check_e188 rc|^train_check_e188 rc|^preflight_e188 rc|^e188_common rc|STOP|aifoundry3: the train host built' "$S/s1-wait.txt" | sort -u | san | cut -c1-220
nreads=$(since "$n0" | grep -c 'step=s08_a3_build_e188 class=read host=aifoundry3 bound=60s')
n13=$(since "$n0" | grep -c ' rc=13 ')
th=$([ -x "$BOXT/build/e188host/b/host/sparsity_host" ] && echo 1 || echo 0)
gc=$(grep -cF 'with g++-13 (' "$BOXT/build/e188host/build.log" 2>/dev/null)     # note 2: Homebrew's on the Intel, Ubuntu's here
ok "$rs.$ra.$rw.$(has '^TRAIN-CHANGE OK: ' "$S/s1-wait.txt").$(has '^HARNESS OK: 79 files' "$S/s1-wait.txt").$nreads.$n13.$th.$gc.$(builds)" "0.0.0.1.1.6.0.1.1.1" \
  "S1 the sync, the build job (g++-13 -O2), then the five checks, each in its own 60 s read (6 with the one before the build); TRAIN-CHANGE OK from the host's behaviour; HARNESS OK 79; one build counted"

# note 1: X3 and N1 (step 6, unchanged) are v1's committed log's

step "D. step 8, the trains' dry job, on the box step 6 left"
: > "$S/dry-network.log"
bash "$R/s10_a3_dry_e188.sh" start > "$S/d-start.txt" 2>&1; ds=$?
wait10 "$S/d-wait.txt"; dw=$?
grep -aE '^E188 dry|^E188 start gate' "$S/d-wait.txt" | cut -c1-120
k=0; for x in 'E188 dry 18810 rc=0' 'E188 dry 18811 rc=0' 'E188 dry 18820 rc=0' 'E188 dry 18801 --smoke rc=0' 'E188 start gate rc=8'; do k=$((k + $(has "^$x" "$S/d-wait.txt"))); done
nw=$(grep -c . "$S/dry-network.log")
ok "$ds.$dw.$k.$nw" "0.0.5.0" "D the dry job rc 0: 18810, 18811, the kinds pass 18820, the smoke, the start gate's 8; no network or device-tool call on the box"

step "O. a card session of ours on the box: step 5, step 6's start, step 8's start and step 9's launch each refused"
touch "$S/ours-live.flag"
bash "$R/s07_a3_sync_e188.sh" > "$S/o5.txt" 2>&1; o5=$?
b6 start > "$S/o6.txt" 2>&1; o6=$?
bash "$R/s10_a3_dry_e188.sh" start > "$S/o8.txt" 2>&1; o8=$?
bash "$R/s11_a3_session_e188_v2.sh" FULL yes > "$S/o9.txt" 2>&1; o9=$?
rm -f "$S/ours-live.flag"
stopline "$S/o9.txt" | san
ok "$o5.$o6.$(has 'a card session of ours runs on aifoundry3' "$S/o6.txt").$o8.$o9" "10.10.1.14.10" \
  "O beside a session of ours: step 5 refused (10), step 6 refused (10), step 8's job refused on the box (14, JOB-REFUSED), step 9 refused (10)"

# note 1: U, R, V, N6 and LJ (steps 6 and 8, unchanged) are v1's committed log's

step "RS. the rest rule through step 9: a real E185-form session log ended 10 minutes ago, then only an E183-form log ended 45 minutes ago"
fresh_day
b6 start > "$S/rs0s.txt" 2>&1
read -r rs0w n17 <<EOF2
$(waitb "$S/rs0w.txt")
EOF2
bash "$R/s07_a3_sync_e188.sh" > "$S/rs-sync.txt" 2>&1; rss=$?
mkdir -p "$BOXT/build/e185/T1794480000"
printf '%s session start (T0 1794480000)\n%s smoke gate passed\n%s session end\n' "$("$GDATE" -d '-70 min' '+%F %T %Z')" "$("$GDATE" -d '-65 min' '+%F %T %Z')" "$("$GDATE" -d '-10 min' '+%F %T %Z')" > "$BOXT/build/e185/T1794480000/session.log"
bash "$R/s11_a3_session_e188_v2.sh" FULL yes > "$S/rs1.txt" 2>&1; rs1=$?
stopline "$S/rs1.txt" | san
nl1=$([ -f "$RB_OUT/e188-T0.txt" ] && echo 1 || echo 0)
mv "$BOXT/build/e185" "$S/e185-moved"
mkdir -p "$BOXT/build/e183"
printf '%s session start (T0 1794480100 = %s), kit note 4; plan FULL\n%s session end (T0 1794480100)\n' "$("$GDATE" -d '-100 min' '+%F %T %Z')" "x" "$("$GDATE" -d '-45 min' '+%F %T %Z')" > "$BOXT/build/e183/session-t1794480100.log"
ok "$rs0w.$rss.$rs1.$(has 'REFUSED: 10 minutes since E185' "$S/rs1.txt").$nl1" "0.0.10.1.0" "RS step 9 v2 refused (10) 10 minutes after an E185-form session's end, naming E185, nothing launched"

step "RS3 (note 1). THE REST RULE v2 through step 9 v2: an E188-form session on the box cut mid-queue (its log silent since 'queue starts' 95 minutes ago; its queue and a train block written 10 minutes ago)"
CS=$BOXT/build/e188/T1794470000
mkdir -p "$CS" "$BOXT/build/claims-v3/aifoundry3/e188/p18813"
printf '%s session start (budget anchor T0 x; plan FULL; trains yes; its files in build/e188/T1794470000)\n%s smoke gate passed: queue starts (plan FULL)\n' "$("$GDATE" -d '-100 min' '+%F %T %Z')" "$("$GDATE" -d '-95 min' '+%F %T %Z')" > "$CS/session.log"
touch -t "$("$GDATE" -d '-95 min' +%Y%m%d%H%M.%S)" "$CS/session.log"
echo "the queue's output, written until the shell died" > "$CS/queue.out"; touch -t "$("$GDATE" -d '-10 min' +%Y%m%d%H%M.%S)" "$CS/queue.out"
echo '{"t_ms": 0}' > "$BOXT/build/claims-v3/aifoundry3/e188/p18813/telemetry.jsonl.raw"; touch -t "$("$GDATE" -d '-10 min' +%Y%m%d%H%M.%S)" "$BOXT/build/claims-v3/aifoundry3/e188/p18813/telemetry.jsonl.raw"
rm -f "${RB_OUT:?}/e188-T0.txt"
bash "$R/s11_a3_session_e188_v2.sh" FULL yes > "$S/rs3.txt" 2>&1; rs3=$?
stopline "$S/rs3.txt" | san
nl3=$([ -f "$RB_OUT/e188-T0.txt" ] && echo 1 || echo 0); nt3=$(ls "$BOXT/build/e188" | grep -c '^T[0-9]*$')
mkdir -p "$S/rs3-moved"; mv "$CS" "$S/rs3-moved/"; mv "$BOXT/build/claims-v3/aifoundry3/e188/p18813" "$S/rs3-moved/"
nc3=$(grep -l "^note: E188's last real session block has no 'session end': counted as ended at .* (the latest write of E188's files" "$RB_OUT"/calls/*s11_a3_session_v2_e188* 2>/dev/null | grep -c .)
ok "$rs3.$(has 'REFUSED: 10 minutes since E188' "$S/rs3.txt").$([ "$nc3" -ge 1 ] && echo 1 || echo 0).$nl3.$nt3" "10.1.1.0.1" "RS3 step 9 v2 refused (10) 10 minutes after the cut E188 session's last write (not 95 minutes after its last log line), naming E188, nothing launched"

step "L. step 9 FULL yes (an E183-form session ended 45 minutes ago; the committed binaries' pins put back by step 5): the session stops at its own harness check"
bash "$R/s11_a3_session_e188_v2.sh" FULL yes > "$S/l9.txt" 2>&1; l9=$?
grep -aE 'LAUNCHED|STOP|launched on|^rest: ' "$S/l9.txt" | san | cut -c1-200
T0=$(cat "$RB_OUT/e188-T0.txt" 2>/dev/null)
for k in $(seq 1 30); do [ -s "$BOXT/build/e188/T$T0/MANIFEST.sha256" ] && break; sleep 1; done
bash "$R/s20_wait_e188.sh" > "$S/l20.txt" 2>&1; l20=$?; stopline "$S/l20.txt" | san
hc=$(has 'harness check failed: no device opened' "$BOXT/build/e188/T$T0/session.log")
mf=$([ -s "$BOXT/build/e188/T$T0/MANIFEST.sha256" ] && echo 1 || echo 0)
rl=$(grep -c "rest: 4[5-9] minutes since E183's session end" "$RB_OUT/runbook.log")
ok "$l9.$([ "$rl" -ge 1 ] && echo 1 || echo 0).$hc.$mf.$l20.$(has '^MANIFEST-WRITTEN' "$RB_OUT"/calls/*wait-e188*.out 2>/dev/null)" "0.1.1.1.16.1" \
  "L the launch (0) with the rest rule's line naming E183's end; the session stops at its harness check, no device opened, its manifest written; step 10 reads a gate stop (16) with the manifest"

step "C. step 11 v2 on a session staged on the box: the copies by name, COPY-BACK EXACT, then the C gate (14, by design)"
SD=$BOXT/build/e188/T$T0
mkdir -p "$BOXT/build/claims-v3/aifoundry3/e188-stoptest/p18802" "$BOXT/build/claims-v3/aifoundry3/e188/p18810/a0"
echo '{"status":"ok"}' > "$BOXT/build/claims-v3/aifoundry3/e188-stoptest/p18802/block.json"
echo 'rc=6' > "$BOXT/build/claims-v3/aifoundry3/e188-stoptest/p18802/stoptest.rc"
echo '{"process": 0}' > "$BOXT/build/claims-v3/aifoundry3/e188/p18810/train.jsonl"
echo '{"item": "fp32.zeros"}' > "$BOXT/build/claims-v3/aifoundry3/e188/p18810/a0/runs.jsonl"
printf 'build/claims-v3/aifoundry3/e188-stoptest/p18802\nbuild/claims-v3/aifoundry3/e188/p18810\n' > "$SD/blocks.txt"
( cd "$BOXT" && { find "build/e188/T$T0" -type f ! -name 'MANIFEST.sha256*'; while IFS= read -r b; do find "$b" -type f ! -name telemetry.jsonl.raw; done < "$SD/blocks.txt"; } |
  LC_ALL=C sort -u | while read -r f; do sha256sum "$f"; done > "build/e188/T$T0/MANIFEST.sha256" )
nm=$(grep -c . "$SD/MANIFEST.sha256")
printf '#!/bin/sh\necho "the desk-test stand-in collector (RB_DESKTEST=1): nothing reduced"\n' > "$S/standin-collect.sh"
RB_DESKTEST=1 K6E188_COLLECT="$S/standin-collect.sh" bash "$R/s22_collect_e188_v2.sh" > "$S/c1.txt" 2>&1; c1=$?
grep -aE '^COPY-BACK|STOP' "$S/c1.txt" | san | cut -c1-200
cx=$(has "^COPY-BACK EXACT $nm files" "$S/c1.txt"); cg=$(has 'has no finished check of C' "$S/c1.txt"); ch=$(has 'HISTORY OK: ' "$S/c1.txt")
c6=$(ls "$T/build/e188-raw/logs/step6/" 2>/dev/null | grep -c .)
RB_DESKTEST=1 K6E188_COLLECT="$S/standin-collect.sh" bash "$R/s22_collect_e188_v2.sh" > "$S/c2.txt" 2>&1; c2=$?; stopline "$S/c2.txt" | san
mv "$T/build/e188-raw" "$S/raw-c1"
echo '{"process": 1}' > "$BOXT/build/claims-v3/aifoundry3/e188/p18810/train.jsonl"
RB_DESKTEST=1 K6E188_COLLECT="$S/standin-collect.sh" bash "$R/s22_collect_e188_v2.sh" > "$S/c3.txt" 2>&1; c3=$?; stopline "$S/c3.txt" | san
mv "$T/build/e188-raw" "$S/raw-c3"
cp "$RB_OUT/window.env" "$S/window-keep.env"
bash "$R/s02_window_e188.sh" "$TODAY" "$(TZ=America/Los_Angeles "$GDATE" -d '-1 min' +%H:%M)" "$(TZ=America/Los_Angeles "$GDATE" -d '+5 min' +%H:%M)" > /dev/null 2>&1
: > "$S/calls.log"
bash "$R/s22_collect_e188_v2.sh" > "$S/c4.txt" 2>&1; c4=$?; stopline "$S/c4.txt" | san; nc4=$(grep -c . "$S/calls.log")
cp "$S/window-keep.env" "$RB_OUT/window.env"
ok "$c1.$cx.$cg.$ch.$([ "$c6" -ge 4 ] && echo 1 || echo 0).$c2.$(has 'already holds files' "$S/c2.txt").$c3.$(has 'COPY-BACK DIFFERS' "$S/c3.txt").$c4.$nc4" "14.1.1.1.1.10.1.16.1.16.0" \
  "C COPY-BACK EXACT ($nm files), the history check OK before any scoring, the day's step-6 record copied ($c6 entries), then the C gate (14, by design); C2 a used output refused (10); C3 a changed box file: COPY-BACK DIFFERS (16); C4 the last end 5 minutes away: refused (16) before any call"

step "C0 (note 2). step 11 v2 with HOME set but empty: refused (10) before any copy"
: > "$S/calls.log"
HOME= bash "$R/s22_collect_e188_v2.sh" > "$S/c0.txt" 2>&1; c0=$?; stopline "$S/c0.txt" | san
nc0=$(grep -c '^rsync ' "$S/calls.log"); rw0=$([ -e "$T/build/e188-raw" ] && echo 1 || echo 0)
ok "$c0.$(has 'HOME is set but empty' "$S/c0.txt").$nc0.$rw0" "10.1.0.0" "C0 step 11 v2 refuses an empty HOME (10) before any copy: no rsync, no raw copy"

step "C5 (note 2). the desk-path gate end to end on this desk's shape: a scored output naming aifoundry3's own tree under the desk's home"
echo '{"process": 0}' > "$BOXT/build/claims-v3/aifoundry3/e188/p18810/train.jsonl"      # C3's change undone: the staged manifest holds again
AH=$(/usr/bin/python3 -I -B -c 'import os, pwd; print(pwd.getpwuid(os.getuid()).pw_dir)')
case "$AH" in /home/?*) shape=home ;; *) shape=other ;; esac
printf '#!/usr/bin/env python3\n"""a desk-test stand-in for the C-session reader (case C5 only): every listed session read as checked"""\nprint("CCSESSION-OK (the runbook desk test v3 stand-in, case C5)")\n' > "$T/tools/claims-v3/e188/ccsessions_e188.py"
$G commit -q -am "desk test: a stand-in C-session reader (case C5)" || echo "the scratch commit failed"
ANCH=$($G rev-parse HEAD)
cat > "$S/standin-collect-c5.sh" <<EOF
#!/bin/bash
# the desk-test stand-in collector of case C5 (RB_DESKTEST=1): a scored output whose files name aifoundry3's own tree, as a real one does
O=build/e188-out/\${E188_DATE:?}-e188-one-number-r4-aifoundry3
mkdir -p "\$O/ccheck"
printf '# E188 results (stand-in)\nsession log line: %s/aifoundry/build/claims-v3/aifoundry3/e188/p18810/runs.jsonl written\n' "$AH" > "\$O/results-e188.md"
[ -n "\${C5_DESKPATH:-}" ] && printf 'a desk path beside it: %s/.ssh/known_hosts\n' "$AH" >> "\$O/results-e188.md"
printf '{"verdicts": {"E188-SCHED": "PASS"}, "pairing": {"trains_failed": []}}\n' > "\$O/scored-e188.json"
printf '{"sessions": []}\n' > "\$O/ccheck/ccheck-all.json"
echo '"E188-SCHED": "PASS"'
echo "results-e188.md written (stand-in)"
EOF
id -un > "$RB_OUT/box-login-aifoundry3.txt"
mvaside() { local k=$1; [ -d "$T/build/e188-raw" ] && mv "$T/build/e188-raw" "$S/raw-$k"; [ -d "$T/build/e188-out" ] && mv "$T/build/e188-out" "$S/out-$k"; return 0; }
mvaside c5pre
RB_E188_BASE=$ANCH RB_DESKTEST=1 K6E188_COLLECT="$S/standin-collect-c5.sh" bash "$R/s22_collect_e188.sh" > "$S/c5v1.txt" 2>&1; c5v1=$?; stopline "$S/c5v1.txt" | san | cut -c1-240
v1hit=$(grep -c "this user's home\|HIT" "$S/c5v1.txt"); mvaside c5v1
RB_E188_BASE=$ANCH RB_DESKTEST=1 K6E188_COLLECT="$S/standin-collect-c5.sh" bash "$R/s22_collect_e188_v2.sh" > "$S/c5v2.txt" 2>&1; c5v2=$?
grep -aE 'collected and scored|STOP' "$S/c5v2.txt" | san | cut -c1-160; mvaside c5v2
RB_E188_BASE=$ANCH RB_DESKTEST=1 C5_DESKPATH=1 K6E188_COLLECT="$S/standin-collect-c5.sh" bash "$R/s22_collect_e188_v2.sh" > "$S/c5v2d.txt" 2>&1; c5v2d=$?; stopline "$S/c5v2d.txt" | san | cut -c1-240
mvaside c5v2d
# fix-port188, case T11 (read out after C5): the same staged session, an untracked json.py at the lab's top that writes a marker if imported
rm -f "$S/shadow-json-ran"
cat > "$T/json.py" <<EOF
open("$S/shadow-json-ran", "a").write("json shadow ran\n")
EOF
RB_E188_BASE=$ANCH RB_DESKTEST=1 K6E188_COLLECT="$S/standin-collect-c5.sh" bash "$R/s22_collect_e188_v2.sh" > "$S/t11.txt" 2>&1; t11=$?
t11s=$(stopline "$S/t11.txt" | san | cut -c1-260); t11x=$(has '^COPY-BACK EXACT ' "$S/t11.txt"); t11h=$(has 'HISTORY OK: ' "$S/t11.txt")
t11c=$([ -d "$T/build/e188-out" ] && echo 1 || echo 0); mvaside t11; rm -f "${T:?}/json.py"
t11m=$([ -e "$S/shadow-json-ran" ] && echo 1 || echo 0)
$G reset -q --hard HEAD~1; rm -f "${RB_OUT:?}/box-login-aifoundry3.txt"
if [ "$shape" = home ]; then
  ok "$c5v1.$([ "$v1hit" -ge 1 ] && echo 1 || echo 0).$c5v2.$(has 'E188 collected and scored' "$S/c5v2.txt").$c5v2d.$(has 'a desk path reached what this step wrote' "$S/c5v2d.txt")" "16.1.0.1.16.1" \
    "C5 on a desk whose home has the box account's shape: step 11 v1 stops at k6's gate (16, this user's home); step 11 v2 collects the same session (0, E183's gate, the box's tree left out); a desk path beside it stops step 11 v2 (16)"
else
  ok "$c5v1.$c5v2.$c5v2d" "16.16.16" "C5 on a desk whose home is not under /home/ (the Intel): step 11 v2's gate is k6's own, so both versions stop alike (here the home is $shape)"
fi

step "T11 (fix-port188, on verify-port188's finding 1). step 11 v2 on C5's staged session with an untracked json.py at the lab's top (the collector's scripts on stdin read the top first)"
echo "$t11s"
ok "$t11.$t11x.$t11h.$(has 'TOP REFUSED: .*json.py' "$S/t11.txt").$(has 'nothing is scored' "$S/t11.txt").$t11m.$t11c" "16.1.1.1.1.0.0" \
  "T11 step 11 v2 copies back (COPY-BACK EXACT) and reads HISTORY OK, then stops (16) at the top's check naming json.py, before any scoring: no collector output, and no process of the step imported the module"

step "Z. no process of this test left running"
sleep 2
zs=$(leftovers)
ok "$zs" "0" "Z nothing left running"

echo
echo "SELFTEST-RB-E188-V3 $npass of $ncase $([ "$fail" -eq 0 ] && echo PASS || echo FAIL)"
exit "$fail"
