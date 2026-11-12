#!/usr/bin/env bash
# E183 (the kit's dated note 4, KIT.md.dated-note-4.md, Thu 12 Nov 2026, before any E183 datum): the runbook's desk test v3, for note 4's
# steps, with a FAKE ssh and rsync (rb/selftest_rb_e183.sh's stand-ins, cc597bf2: they serve a stand-in box, a local directory laid out like
# aifoundry3's ~/aifoundry, refuse any other host, and log every call; no lab box is reached). rb_run.py's own bounds hold. The cases:
#   A   the dry listing v5: every step exits 0; the look before the post; step 5a (the records' copy) before step 5 (the sync) and step 6;
#       the stand-ins see no ssh or rsync call;
#   K   step 2 v5 with no window in RB_OUT: refused (10), no call;
#   R0  step 6 v2's start before step 5a: refused (10), no call;
#   R1  step 5a on a stand-in box holding Thursday's records: one probe and ONE rsync, all 11 files copied with the box's own bytes, the
#       compiler line printed, RECORDS-COPIED written, and the box's build/ unchanged (its manifest before and after);
#   R2  two of the records absent on the box: COPIED WITH GAPS (0), the two named in the marker;
#   R3  a login link on the probe: 11, one line appended to RB_LOCK, no rsync call;
#   R4  the rsync failing otherwise (a protocol error): 14, no marker;
#   R5-R11 (added before the land, after verify-kit183's fault 1): the REAL rsync in remote mode, its server run on the stand-in box by the
#       stand-in ssh (R1-R4's stand-in rsync rewrote host:path to local paths, and local rsync did not print the broken pipe below):
#       R5 all 11 records, one probe and one transport, the box unchanged (0); R6 two absent, each named by the box's own rsync, COPIED WITH
#       GAPS (0); R7 EVERY record absent, rsync's 23 with its receiver's "write error: Broken pipe (32)": COPIED WITH GAPS, 0 files, the
#       marker written (0); R8 a record present but unreadable: 14, no marker; R9 the box's tree missing (rsync's change_dir line): 14, no
#       marker; R10 step 5a again where RECORDS-COPIED is already written: 16, no call, the marker unchanged; R11 a login link during the
#       transport: 11, the lock file appended, no marker; then the stand-in box's build/ as before R5;
#   B1  step 5 (s07 v1) syncs E183's directory, note 4's files with it; then step 6 V1 with a stand-in cmake that builds the patched host by
#       GCC at -O2 (rb/fake_cmake_gcc_e183.sh): TRAIN-HOST-BUILD-FAILED, "the host lacks the train change", 16 (Thu 12 Nov's defect);
#   B2  the same day, step 6 v2 (the re-run): TRAIN-HOST-BUILT, the job's log reads TRAIN-CHANGE OK, then the four checks (inputs 40,
#       harness v2 with the binaries, preflight v2 GO, the registration): 0; two builds counted;
#   B3  a third start: refused (10), a good build today;
#   D   step 8 v2 (the dry pass) on that box: job a3-dry-e183 rc 0 (block v2's 18310, the smoke, the stop test on the GCC host; the start
#       gate of session v2 reads 8);
#   S1-S3  step 9 v2's rest rule on the box: E185's T<T0>/session.log ending 10 minutes ago, E186's 15 minutes ago, E184's
#       session-S-t<T0>.log 20 minutes ago: each REFUSED (10), naming the run; nothing launched;
#   S4  all three ended 41 or more minutes ago: the rest line ("rest: 41 minutes since E185's ..."), then the next gate's refusal (the dry
#       pass's job made yesterday's for this case: 10), so nothing is launched by the test;
#   P1-P7  step 2 v5's own checks, on a scratch repository holding E183's files and those its checks read, with step 2 v4 replaced there by
#       a stand-in (the real v4 runs on the lab clone in the note's checks) and a stand-in note 4 list pinned in the scratch copy of v5:
#       P1 at its pins (0); P2 a changed entry in note 4's list (16); P3 note 4's list one line short (16); P4 kit note 3's list one line
#       short (16); P5 a list with SHA256SUMS in the middle of its name, unknown (reported, 0); P6 note M1's list changed (reported, 0);
#       P7 step 2 v4 exiting 16 (v5 exits 16, its own checks not run);
#   Z   no process of this test left running; the recording mock's device record empty through every case.
#   bash tools/claims-v3/e183/rb/selftest_rb_e183_v3.sh <scratch dir> > <log>
# SPDX-License-Identifier: Apache-2.0
set -u
SRC=$(cd "$(dirname "${BASH_SOURCE[0]}")/../../../.." && pwd)
S=${1:?a scratch directory outside the repository}
case "$S" in "$SRC"|"$SRC"/*) echo "the scratch directory must be outside the repository"; exit 2 ;; esac
for v in RB_PROBE_S RB_READ_S RB_COPY_S RB_WAIT_S RB_LAUNCH_S RB_DESK_S E183_BUILD_S RB_DESKTEST E183_COLLECT; do
  [ -z "${!v:-}" ] || { echo "$v is set: this test runs with rb_run.py's own bounds and no desk-test override in its environment"; exit 2; }
done
for c in gdate timeout sha256sum g++-13; do command -v "$c" > /dev/null || { echo "no $c on PATH"; exit 2; }; done
mkdir -p "$S"; S=$(cd "$S" && pwd)
main() {
rm -rf "${S:?}/tree" "${S:?}/box" "${S:?}/bin" "${S:?}/boxbin" "${S:?}/origin.git" "${S:?}/out-"* "${S:?}/prepo"
T=$S/tree; B=$S/box; BIN=$S/bin
mkdir -p "$T/tools/claims-v3" "$T/workloads" "$B/aifoundry3/aifoundry" "$BIN" "$S/boxbin"
for p in e183 e180 e182 e178 e184 e185 e128 q141k-runbook/k6 q141k-runbook/v3.1 p8-600; do
  mkdir -p "$T/tools/claims-v3/$p"; rsync -a --exclude __pycache__ "$SRC/tools/claims-v3/$p/" "$T/tools/claims-v3/$p/"
done
cp -p "$SRC/tools/claims-v3/lib.sh" "$SRC/tools/claims-v3/dmcmd_audit.py" "$SRC/tools/claims-v3/dmcmd_table.json" "$T/tools/claims-v3/"
( cd "$SRC" && git ls-files workloads/enercat ) | while IFS= read -r f; do mkdir -p "$T/$(dirname "$f")"; cp -p "$SRC/$f" "$T/$f"; done
for f in "$SRC"/tools/claims-v3/e183/*_v2.* "$SRC"/tools/claims-v3/e183/train_check_e183.sh "$SRC"/tools/claims-v3/e183/harness-e183-v2.json \
         "$SRC"/tools/claims-v3/e183/rb/*; do
  [ -f "$f" ] && cp -p "$f" "$T/${f#$SRC/}"
done
G="git -C $T -c user.name=e183-desktest -c user.email=desktest@localhost -c core.hooksPath=/dev/null -c commit.gpgsign=false"
$G init -q && $G add -A && $G commit -q -m "E183 runbook desk test v3: the lab files the steps read" || { echo "the scratch repository failed"; return 2; }
echo "scratch repository: $($G ls-files | wc -l | tr -d ' ') files committed"
REAL_RSYNC=$(command -v rsync)
cat > "$BIN/ssh" <<EOF
#!/bin/bash
echo "ssh \$*" >> "$S/calls.log"
host=""; cmd=""
while [ \$# -gt 0 ]; do case "\$1" in -o) shift 2 ;; -*) shift ;; *) if [ -z "\$host" ]; then host=\$1; shift; else cmd="\$*"; break; fi ;; esac; done
case "\$host" in aifoundry3) ;; *) echo "STAND-IN SSH: refusing host \$host" >&2; exit 97 ;; esac
if [ -e "$S/link-at-probe" ] && [ "\$cmd" = true ]; then echo "To authenticate, visit: https://login.tailscale.com/a/desk-test-stand-in" >&2; sleep 30; exit 1; fi
[ "\$cmd" = true ] && exit 0
case "\$cmd" in "rsync --server "*)   # cases R5-R11: the copy's transport in REMOTE mode; the box's rsync server runs in the stand-in home, as sshd would run it
  if [ -e "$S/link-at-rsync" ]; then echo "To authenticate, visit: https://login.tailscale.com/a/desk-test-stand-in" >&2; sleep 30; exit 1; fi
  cd "$B/\$host" && exec \$cmd ;;
esac
cat | HOME="$B/\$host" PATH="$S/boxbin:\$PATH" bash -c "cd ~ && \$cmd"
EOF
cat > "$BIN/rsync" <<EOF
#!/bin/bash
echo "rsync \$*" >> "$S/calls.log"
if [ -e "$S/rsync-protocol-error" ]; then echo "rsync error: error in rsync protocol data stream (code 12) at io.c(232) [desk stand-in]" >&2; exit 12; fi
[ -e "$S/rsync-remote-mode" ] && exec "$REAL_RSYNC" "\$@"   # cases R5-R11: the real rsync, unchanged words, in remote mode through the stand-in ssh
a=()
while [ \$# -gt 0 ]; do case "\$1" in -e) shift 2 ;; *:*) h=\${1%%:*}; p=\${1#*:}; case "\$h" in aifoundry3) ;; *) echo "STAND-IN RSYNC: refusing \$h" >&2; exit 97 ;; esac; a+=("$B/\$h/\$p"); shift ;; *) a+=("\$1"); shift ;; esac; done
exec "$REAL_RSYNC" "\${a[@]}"
EOF
R=$T/tools/claims-v3/e183/rb
BOXT=$B/aifoundry3/aifoundry
J=$BOXT/build/q141k/jobs
printf '#!/bin/sh\necho aifoundry3\n' > "$S/boxbin/hostname"
printf '#!/bin/sh\nexec gdate "$@"\n' > "$S/boxbin/date"
printf '#!/bin/sh\nPYTHONUSERBASE="%s" exec /usr/bin/python3 "$@"\n' "$(/usr/bin/python3 -m site --user-base)" > "$S/boxbin/python3"
printf '#!/bin/sh\necho "No process holds an ET-SoC-1 device node or card lock. (desk stand-in)"\n' > "$S/boxbin/et-who"
printf '#!/bin/sh\nexit 1\n' > "$S/boxbin/pgrep"
printf '#!/bin/sh\nexec "$@"\n' > "$S/boxbin/setsid"
for n in ssh scp; do printf '#!/bin/sh\necho "%s $*" >> "%s"\necho "NETWORK STAND-IN: %s refused" >&2\nexit 97\n' "$n" "$S/box-network.log" "$n" > "$S/boxbin/$n"; done
cp -p "$SRC/tools/claims-v3/e183/rb/fake_cmake_gcc_e183.sh" "$S/boxbin/cmake"
chmod +x "$BIN/ssh" "$BIN/rsync" "$S/boxbin"/*
export PATH="$BIN:$PATH" RB_REPO="$T" RB_LOCK="$S/lock.txt" RB_WAIT_LOOP_S=20 E183_DEVICE_RECORD="$S/box-device-record.txt" \
  FAKE_CMAKE_STUBS="$T/tools/claims-v3/e184/desk/stubs" FAKE_CMAKE_MOCK="$T/tools/claims-v3/e183/desk/mock_runtime_e183_v2.cpp"
: > "$S/calls.log"; : > "$RB_LOCK"; : > "$S/box-network.log"; rm -f "$S/link-at-probe" "$S/rsync-protocol-error" "$E183_DEVICE_RECORD"
fail=0; npass=0; ncase=0
ok() { ncase=$((ncase + 1)); if [ "$1" = "$2" ]; then npass=$((npass + 1)); echo "-> PASS ($3)"; else echo "-> FAIL ($3: got $1, want $2)"; fail=1; fi; }
step() { echo; echo "== $*"; }
ncalls() { grep -c "^$1 " "$S/calls.log" 2>/dev/null; }
has() { grep -aq -- "$1" "$2" && echo 1 || echo 0; }
nrec() { if [ -f "$E183_DEVICE_RECORD" ]; then grep -c . "$E183_DEVICE_RECORD"; else echo 0; fi; }
TODAY=$(TZ=America/Los_Angeles gdate +%F)
AT=$BOXT/build/e183-build-attempts.txt
builds() { if [ -f "$AT" ]; then echo $(( $(grep -c "^$TODAY .* a3-build-e183 started\$" "$AT") - $(grep -c "^$TODAY .* a3-build-e183 ended rc=[0-9]*: TRAIN-HOST-INPUTS-DIFFER" "$AT") )); else echo 0; fi; }
b6v1() { bash "$R/s08_a3_build_e183.sh" "$@"; }
b6() { bash "$R/s08_a3_build_e183_v2.sh" "$@"; }
waitb() {  # waitb <step file> <out>: step 6's wait, again while it says 17; prints its last exit status
  local f=$1 o=$2 k r
  : > "$o"
  for k in 1 2 3 4 5 6 7 8 9 10 11 12; do bash "$f" wait >> "$o" 2>&1; r=$?; [ "$r" -eq 17 ] || break; done
  echo "$r"
}
wait10() { local o=$1 k r; for k in 1 2 3 4 5 6 7 8 9 10; do bash "$R/s10_a3_dry_e183_v2.sh" wait > "$o" 2>&1; r=$?; [ "$r" -eq 17 ] || break; done; return "$r"; }
boxman() { ( cd "$BOXT" && find build -type f | LC_ALL=C sort | while IFS= read -r f; do sha256sum "$f"; done ) | sha256sum | cut -c1-16; }
cd "$T" || return 2

step "A. the dry listing v5: every step exits 0; the look before the post; step 5a before step 5 and step 6; no ssh or rsync call"
: > "$S/calls.log"
bash "$R/list_steps_e183_v5.sh" "$S/out-a" > "$S/dry-listing.txt" 2>&1; rc=$?
n=$(grep -c . "$S/calls.log"); tail -n 1 "$S/dry-listing.txt"
lp=$(awk '/s05_look_k6.sh aifoundry3$/ {l=NR} /the day.s one post, made AFTER the look/ {p=NR} /s06_a3_records_e183.sh $/ {c=NR} /s07_a3_sync_e183.sh $/ {y=NR} /s08_a3_build_e183_v2.sh start$/ {b=NR} END {print (l > 0 && p > l && c > p && y > c && b > y) ? 1 : 0}' "$S/dry-listing.txt")
ok "$rc.$n.$lp" "0.0.1" "A the dry listing v5: 0 steps failing, no call; the look, the post, step 5a, step 5, step 6 in that order"

step "K. step 2 v5 with no window in RB_OUT"
: > "$S/calls.log"
RB_OUT="$S/out-k" bash "$R/s03_desk_e183_v5.sh" > "$S/k.txt" 2>&1; rc=$?
grep -m1 -i 'no window' "$S/k.txt" | cut -c1-200
ok "$rc.$(grep -c . "$S/calls.log")" "10.0" "K step 2 v5 refuses without step 1's window"

export RB_OUT="$S/out-b"; mkdir -p "$RB_OUT"
[ "$(gdate +%H%M)" -lt 2250 ] || { echo "run this desk test before 22:50 (its window must leave FULL's 65 minutes before 23:59)"; return 2; }
bash "$R/s02_window_e183.sh" "$TODAY" "$(gdate -d '+30 min' +%H:%M)" 23:59 > "$S/b-window.txt" 2>&1 || { echo "the window failed: $(tail -2 "$S/b-window.txt")"; fail=1; }

step "R0. step 6 v2's start before step 5a: refused, no call"
: > "$S/calls.log"
b6 start > "$S/r0.txt" 2>&1; rc=$?
grep -m1 'STOP' "$S/r0.txt" | cut -c1-200
ok "$rc.$(grep -c . "$S/calls.log")" "10.0" "R0 no build before the records' copy"

# Thursday's records on the stand-in box (their words stand in for the box's; the cmake log names a compiler as cmake writes it)
mkdir -p "$BOXT/build/e183-build-logs/2026-11-12" "$J"
for k in 1 2; do printf 'E183-BUILD-ATTEMPT %s today (the day'"'"'s start %s)\nthe host lacks the train change\nTRAIN-HOST-BUILD-FAILED rc=1\n' "$k" "$k" > "$BOXT/build/e183-build-logs/2026-11-12/e183-build-host-start$k.txt"; done
printf '2026-11-12 06:36:51 PST a3-build-e183 started\n2026-11-12 06:36:55 PST a3-build-e183 ended rc=1: TRAIN-HOST-BUILD-FAILED rc=1\n2026-11-12 06:38:41 PST a3-build-e183 started\n2026-11-12 06:38:45 PST a3-build-e183 ended rc=1: TRAIN-HOST-BUILD-FAILED rc=1\n' > "$BOXT/build/e183-build-attempts.txt"
printf -- '-- The C compiler identification is GNU 11.4.0\n-- The CXX compiler identification is GNU 11.4.0\n-- Configuring done\n' > "$BOXT/build/enercat-e183-cmake.log"
for f in e183-inputs.txt e183-inputs-build.txt e183-tree-check.txt; do echo "BUILD INPUTS OK: 40 files (desk stand-in of $f)" > "$BOXT/build/$f"; done
for x in sh out pid rc; do echo "desk stand-in of a3-build-e183.$x" > "$J/a3-build-e183.$x"; done
step "R1. step 5a on the stand-in box: one probe, ONE rsync, all 11 records, the compiler line, the box unchanged"
: > "$S/calls.log"; m0=$(boxman)
bash "$R/s06_a3_records_e183.sh" > "$S/r1.txt" 2>&1; rc=$?
grep -E 'compiler|RECORDS|STOP' "$S/r1.txt" | sed "s#$S#<scratch>#g" | cut -c1-240
m1=$(boxman)
nc=$(grep -c -v '^#' "$RB_OUT/box-records-e183/RECORDS-COPIED" 2>/dev/null)
same=0; ( cd "$RB_OUT/box-records-e183" && grep -v '^#' RECORDS-COPIED | while read -r h p; do [ "$(sha256sum "$BOXT/$p" | cut -d' ' -f1)" = "$h" ] || echo bad; done ) | grep -q bad && same=1
gc=$(has 'GNU 11.4.0' "$S/r1.txt")
ok "$rc.$(ncalls ssh).$(ncalls rsync).$nc.$same.$gc.$([ "$m0" = "$m1" ] && echo unchanged)" "0.1.1.11.0.1.unchanged" "R1 the records copied read-only (11 files at the box's own bytes), the compiler named, the box's build/ unchanged"
step "R2. two records absent on the box: COPIED WITH GAPS, the two named"
mkdir -p "$S/aside"; mv "$BOXT/build/e183-inputs.txt" "$J/a3-build-e183.pid" "$S/aside/"
RB_OUT="$S/out-r2" bash "$R/s06_a3_records_e183.sh" > "$S/r2.txt" 2>&1; rc=$?
grep -E 'COPIED|STOP' "$S/r2.txt" | cut -c1-260
gm=$(grep -c 'not on aifoundry3:.*build/e183-inputs.txt.*a3-build-e183.pid' "$S/out-r2/box-records-e183/RECORDS-COPIED" 2>/dev/null)
ok "$rc.$(has 'COPIED WITH GAPS' "$S/r2.txt").$gm" "0.1.1" "R2 a partial copy names its gaps and writes the marker"
mv "$S/aside/e183-inputs.txt" "$BOXT/build/"; mv "$S/aside/a3-build-e183.pid" "$J/"
step "R3. a login link at the probe: 11, the lock file appended, no rsync"
: > "$S/calls.log"; touch "$S/link-at-probe"; l0=$(grep -c . "$RB_LOCK")
RB_OUT="$S/out-r3" bash "$R/s06_a3_records_e183.sh" > "$S/r3.txt" 2>&1; rc=$?
rm -f "$S/link-at-probe"
grep -m1 'STOP' "$S/r3.txt" | cut -c1-200
ok "$rc.$(( $(grep -c . "$RB_LOCK") - l0 )).$(ncalls rsync).$([ -e "$S/out-r3/box-records-e183/RECORDS-COPIED" ] && echo marker || echo none)" "11.1.0.none" "R3 a login link stops the copy before it starts"
step "R4. the rsync failing otherwise: 14, no marker"
touch "$S/rsync-protocol-error"
RB_OUT="$S/out-r4" bash "$R/s06_a3_records_e183.sh" > "$S/r4.txt" 2>&1; rc=$?
rm -f "$S/rsync-protocol-error"
grep -m1 'STOP' "$S/r4.txt" | cut -c1-200
ok "$rc.$([ -e "$S/out-r4/box-records-e183/RECORDS-COPIED" ] && echo marker || echo none)" "14.none" "R4 a failed copy writes no marker"

# R5-R11 (fix-kit183, before the land; verify-kit183's fault 1): the real rsync in REMOTE mode, client here and "rsync --server --sender" on
# the stand-in box through the stand-in ssh, as on the day (R1-R4's stand-in rsync rewrote host:path into local paths, and local rsync did not
# print the receiver's broken pipe that remote rsync printed when every source was missing).
recs="build/e183-build-logs build/e183-build-attempts.txt build/enercat-e183-cmake.log build/e183-inputs.txt build/e183-inputs-build.txt build/e183-tree-check.txt build/q141k/jobs/a3-build-e183.sh build/q141k/jobs/a3-build-e183.out build/q141k/jobs/a3-build-e183.pid build/q141k/jobs/a3-build-e183.rc"
aside_all() { mkdir -p "$S/aside-all"; for r in $recs; do mv "$BOXT/$r" "$S/aside-all/$(basename "$r")"; done; }
back_all() { for r in $recs; do mv "$S/aside-all/$(basename "$r")" "$BOXT/$r"; done; }
marker() { [ -e "$S/$1/box-records-e183/RECORDS-COPIED" ] && echo marker || echo none; }
touch "$S/rsync-remote-mode"; mr0=$(boxman)
step "R5. remote mode, all 11 records on the box: one probe, one transport, 11 files at the box's bytes, the box unchanged"
: > "$S/calls.log"
RB_OUT="$S/out-r5" bash "$R/s06_a3_records_e183.sh" > "$S/r5.txt" 2>&1; rc=$?
grep -E 'RECORDS|STOP' "$S/r5.txt" | cut -c1-200
nc=$(grep -c -v '^#' "$S/out-r5/box-records-e183/RECORDS-COPIED" 2>/dev/null)
same=0; ( cd "$S/out-r5/box-records-e183" && grep -v '^#' RECORDS-COPIED | while read -r h p; do [ "$(sha256sum "$BOXT/$p" | cut -d' ' -f1)" = "$h" ] || echo bad; done ) | grep -q bad && same=1
ok "$rc.$(grep -c '^ssh .* aifoundry3 true$' "$S/calls.log").$(grep -c '^ssh .* aifoundry3 rsync --server --sender ' "$S/calls.log").$nc.$same.$([ "$mr0" = "$(boxman)" ] && echo unchanged)" "0.1.1.11.0.unchanged" "R5 remote mode: the whole copy, read-only"
step "R6. remote mode, two records absent: rsync's 23, each named missing by the box's own rsync: COPIED WITH GAPS"
mkdir -p "$S/aside"; mv "$BOXT/build/e183-inputs.txt" "$J/a3-build-e183.pid" "$S/aside/"
RB_OUT="$S/out-r6" bash "$R/s06_a3_records_e183.sh" > "$S/r6.txt" 2>&1; rc=$?
mv "$S/aside/e183-inputs.txt" "$BOXT/build/"; mv "$S/aside/a3-build-e183.pid" "$J/"
grep -E 'link_stat|COPIED|STOP' "$S/r6.txt" | sed "s#$B#<box>#g" | cut -c1-200
gm=$(grep -c 'not on aifoundry3:.*build/e183-inputs.txt.*a3-build-e183.pid' "$S/out-r6/box-records-e183/RECORDS-COPIED" 2>/dev/null)
ok "$rc.$(has 'COPIED WITH GAPS: 9 files' "$S/r6.txt").$gm.$(grep -c 'link_stat ".*/build/e183-inputs.txt" failed: No such file' "$S/r6.txt").$(grep -c 'link_stat ".*/build/q141k/jobs/a3-build-e183.pid" failed: No such file' "$S/r6.txt")" "0.1.1.1.1" "R6 a partial copy, its gaps proven by the box's rsync"
step "R7. remote mode, EVERY record absent (verify-kit183's MR4): COPIED WITH GAPS, 0 files, the marker written"
aside_all
RB_OUT="$S/out-r7" bash "$R/s06_a3_records_e183.sh" > "$S/r7.txt" 2>&1; rc=$?
back_all
grep -E 'Broken pipe|code 23|COPIED|STOP' "$S/r7.txt" | cut -c1-200
echo "   (reported) rsync's own lines: receiver's 'write error: Broken pipe' $(grep -c '^rsync: .*write error: Broken pipe' "$S/r7.txt"); sender's link_stat $(grep -c '^rsync: .*link_stat ".*" failed: No such file' "$S/r7.txt")"
ok "$rc.$(has 'COPIED WITH GAPS: 0 files' "$S/r7.txt").$(grep -c -v '^#' "$S/out-r7/box-records-e183/RECORDS-COPIED" 2>/dev/null).$(grep -c '^rsync: .*link_stat ".*" failed: No such file' "$S/r7.txt").$([ "$mr0" = "$(boxman)" ] && echo unchanged)" "0.1.0.10.unchanged" "R7 nothing on the box: COPIED WITH GAPS (0 files), the marker written, so step 6 v2 can build"
step "R8. remote mode, a record on the box that cannot be read: 14, no marker (a gap the box's rsync did not name missing)"
chmod 000 "$BOXT/build/e183-tree-check.txt"
RB_OUT="$S/out-r8" bash "$R/s06_a3_records_e183.sh" > "$S/r8.txt" 2>&1; rc=$?
chmod 644 "$BOXT/build/e183-tree-check.txt"
grep -E 'STOP' "$S/r8.txt" | sed "s#$S#<scratch>#g" | cut -c1-240
ok "$rc.$(marker out-r8).$(has 'not named missing by the box' "$S/r8.txt")" "14.none.1" "R8 a record present but not copied is never read as a gap"
step "R9. remote mode, the box's whole tree missing: 14, no marker (rsync's change_dir line, no record named missing)"
mv "$BOXT" "$BOXT-away"
RB_OUT="$S/out-r9" bash "$R/s06_a3_records_e183.sh" > "$S/r9.txt" 2>&1; rc=$?
mv "$BOXT-away" "$BOXT"
grep -E 'STOP' "$S/r9.txt" | sed "s#$S#<scratch>#g" | cut -c1-240
ok "$rc.$(marker out-r9)" "14.none" "R9 no tree on the box: a failed copy, never COPIED WITH GAPS"
step "R10. step 5a again in an RB_OUT that already holds RECORDS-COPIED: 16, no call, the marker unchanged"
: > "$S/calls.log"; h0=$(sha256sum "$S/out-r5/box-records-e183/RECORDS-COPIED" | cut -d' ' -f1)
RB_OUT="$S/out-r5" bash "$R/s06_a3_records_e183.sh" > "$S/r10.txt" 2>&1; rc=$?
grep -m1 'STOP' "$S/r10.txt" | cut -c1-240
ok "$rc.$(grep -c . "$S/calls.log").$([ "$h0" = "$(sha256sum "$S/out-r5/box-records-e183/RECORDS-COPIED" | cut -d' ' -f1)" ] && echo same)" "16.0.same" "R10 a second run never overwrites the day's copy"
step "R11. remote mode, a login link during the copy's transport (not at the probe): 11, the lock file appended, no marker"
touch "$S/link-at-rsync"; l0=$(grep -c . "$RB_LOCK")
RB_OUT="$S/out-r11" bash "$R/s06_a3_records_e183.sh" > "$S/r11.txt" 2>&1; rc=$?
rm -f "$S/link-at-rsync"
grep -m1 'STOP' "$S/r11.txt" | cut -c1-200
ok "$rc.$(( $(grep -c . "$RB_LOCK") - l0 )).$(marker out-r11)" "11.1.none" "R11 a link mid-copy stops it"
rm -f "$S/rsync-remote-mode"
ok "$([ "$mr0" = "$(boxman)" ] && echo unchanged)" "unchanged" "R5-R11 the stand-in box's build/ as before them"

step "B1. step 5 (v1, unchanged) syncs E183's directory with note 4's files; step 6 V1 with GCC -O2: the host lacks the train change"
rm -f "$AT"; rm -rf "${BOXT:?}/build/e183-build-logs" "${J:?}"/a3-build-e183.*
bash "$R/s07_a3_sync_e183.sh" > "$S/b1-sync.txt" 2>&1; rs=$?
grep -E 'synced to|STOP' "$S/b1-sync.txt" | sed "s#$S#<scratch>#g" | cut -c1-200
n4=0; for f in train_check_e183.sh build_host_e183_v2.sh block_e183_v2.sh queue_e183_v2.sh session_e183_v2.sh preflight_e183_v2.sh harness_e183_v2.py harness-e183-v2.json; do
  cmp -s "$T/tools/claims-v3/e183/$f" "$BOXT/tools/claims-v3/e183/$f" && n4=$((n4 + 1)); done
mkdir -p "$BOXT/build/ettelem"
printf '#!/bin/sh\necho "STUB EXECUTED: ettelem $*" >&2\nexit 97\n' > "$BOXT/build/ettelem/ettelem"; chmod +x "$BOXT/build/ettelem/ettelem"
b6v1 start > "$S/b1-start.txt" 2>&1; ra=$?
rw=$(waitb "$R/s08_a3_build_e183.sh" "$S/b1-wait.txt")
grep -aE '^E183-BUILD-ATTEMPT|lacks the train change|^TRAIN-HOST-BUILD|STOP' "$S/b1-wait.txt" | sort -u | cut -c1-220
ok "$rs.$n4.$ra.$rw.$(has 'the host lacks the train change' "$S/b1-wait.txt").$(builds)" "0.8.0.16.1.1" "B1 the sync carries note 4's 8 files; v1's build of a GCC -O2 host fails its own grep (one re-run asked)"
step "B2. the re-run, by step 6 v2: TRAIN-CHANGE OK, then the four checks"
b6 start > "$S/b2-start.txt" 2>&1; ra=$?
rw=$(waitb "$R/s08_a3_build_e183_v2.sh" "$S/b2-wait.txt")
grep -aE '^E183-BUILD-ATTEMPT|^TRAIN-CHANGE|^TRAIN-HOST-BUILT|^BUILD INPUTS OK|^HARNESS|^harness_e183_v2 rc|^preflight_e183_v2 rc|^e183_common rc|STOP|aifoundry3: the train host built' "$S/b2-wait.txt" | sort -u | sed "s#$S#<scratch>#g" | cut -c1-220
tc=$(grep -c '^TRAIN-CHANGE OK' "$BOXT/build/e183-build-logs/$TODAY/e183-build-host-start2.txt" 2>/dev/null)
ok "$ra.$rw.$tc.$(has '^HARNESS OK: 127 files' "$S/b2-wait.txt").$(has '^preflight_e183_v2 rc=0 dmcmd_audit: GO' "$S/b2-wait.txt").$(builds).$(nrec)" "0.0.1.1.1.2.0" "B2 build v2 of the same GCC -O2 host passes (TRAIN-CHANGE OK in its log), HARNESS OK 127, preflight v2 GO; two builds; no device record"
step "B3. a third start: refused (a good build today)"
b6 start > "$S/b3.txt" 2>&1; ra=$?
ok "$ra.$(has 'REFUSED: the train host was built on aifoundry3 today' "$S/b3.txt").$(builds)" "10.1.2" "B3 no second build after a good one"

step "D. step 8 v2 (the dry pass) on that box: block v2 on the GCC -O2 host, the start gate of session v2"
: > "$S/box-network.log"
bash "$R/s10_a3_dry_e183_v2.sh" start > "$S/d-start.txt" 2>&1; r1=$?
wait10 "$S/d-wait.txt"; r2=$?
grep -aE '^E183 dry|^E183 start gate' "$S/d-wait.txt" | sort -u | cut -c1-200
k1=$(has '^E183 dry 18310 rc=0' "$S/d-wait.txt"); k3=$(has '^E183 dry 18301 --smoke rc=0' "$S/d-wait.txt"); k4=$(has '^E183 start gate rc=8' "$S/d-wait.txt")
ok "$r1.$r2.$k1.$k3.$k4.$(grep -c . "$S/box-network.log").$(nrec)" "0.0.1.1.1.0.0" "D job a3-dry-e183 rc 0: 18310 0, the smoke 0, the start gate 8; no network call from the box; no device record"

slog() {  # slog <box path> <minutes ago> <end form>: a real session log of ours ending that long ago
  local p=$BOXT/$1 e s0
  e=$(TZ=America/Los_Angeles gdate -d "-$2 min" '+%F %T %Z'); s0=$(TZ=America/Los_Angeles gdate -d "-$(( $2 + 30 )) min" '+%F %T %Z')
  mkdir -p "$(dirname "$p")"; printf '%s session start (desk stand-in)\n%s smoke gate passed\n%s %s\n' "$s0" "$s0" "$e" "$3" > "$p"
}
launched() { ls "$BOXT"/build/e183/session-t*.log 2>/dev/null | grep -c .; }
for spec in "S1 build/e185/T1794600000/session.log 10 E185" "S2 build/e186/T1794600100/session.log 15 E186" "S3 build/e184/session-S-t1794600200.log 20 E184"; do
  set -- $spec
  step "$1. step 9 v2's rest rule: $4's form ($2) ending $3 minutes ago"
  rm -rf "${BOXT:?}/build/e184" "${BOXT:?}/build/e185" "${BOXT:?}/build/e186"
  end="session end"; [ "$4" = E184 ] && end="session end (T0 1794600200)"
  slog "$2" "$3" "$end"
  bash "$R/s11_a3_session_e183_v2.sh" FULL > "$S/$1.txt" 2>&1; rc=$?
  grep -m1 -E 'REFUSED|STOP' "$S/$1.txt" | cut -c1-220
  ok "$rc.$(has "REFUSED: $3 minutes since $4's session end" "$S/$1.txt").$(launched)" "10.1.0" "$1 under 40 minutes after $4's end: refused, nothing launched"
done
step "S4. all three ended 41 minutes ago or more: the rest line, then the next gate (the dry pass made yesterday's for this case)"
rm -rf "${BOXT:?}/build/e184" "${BOXT:?}/build/e185" "${BOXT:?}/build/e186"
slog build/e185/T1794600000/session.log 41 "session end"; slog build/e186/T1794600100/session.log 90 "session end"; slog build/e184/session-S-t1794600200.log 120 "session end (T0 1794600200)"
touch -t "$(gdate -d '-2 day' +%Y%m%d%H%M)" "$J/a3-dry-e183.rc"
bash "$R/s11_a3_session_e183_v2.sh" FULL > "$S/S4.txt" 2>&1; rc=$?
grep -E '^rest: |REFUSED' "$S/S4.txt" | cut -c1-200
ok "$rc.$(has "^rest: 41 minutes since E185's session end" "$S/S4.txt").$(has "REFUSED: E183's dry pass" "$S/S4.txt").$(launched)" "10.1.1.0" "S4 the rest rule passes (41 minutes) and the launch's next gate refuses: nothing launched"

step "P. step 2 v5's own checks on a scratch repository (step 2 v4 a stand-in there; a stand-in note 4 list pinned in v5's copy)"
P=$S/prepo; mkdir -p "$P/tools/claims-v3" "$P/workloads"
for p in e183 e180 e128; do mkdir -p "$P/tools/claims-v3/$p"; rsync -a --exclude __pycache__ "$T/tools/claims-v3/$p/" "$P/tools/claims-v3/$p/"; done
cp -p "$T/tools/claims-v3/lib.sh" "$T/tools/claims-v3/dmcmd_audit.py" "$T/tools/claims-v3/dmcmd_table.json" "$P/tools/claims-v3/"
rsync -a "$T/workloads/" "$P/workloads/"
PE=$P/tools/claims-v3/e183
for l in "$PE"/SHA256SUMS-e183-*; do   # every file E183's lists name, so their entries read as on the lab clone
  awk '{print $2}' "$l" | while IFS= read -r f; do
    f=${f#\*}; [ -e "$P/$f" ] || { [ -f "$SRC/$f" ] && mkdir -p "$P/$(dirname "$f")" && cp -p "$SRC/$f" "$P/$f"; }
  done
done
printf '#!/usr/bin/env bash\n# desk stand-in for step 2 v4 (selftest_rb_e183_v3.sh case P): exits as $PREPO_V4_RC says\necho "[s03_desk_v4_e183] (desk stand-in) rc ${PREPO_V4_RC:-0}"\nexit "${PREPO_V4_RC:-0}"\n' > "$PE/rb/s03_desk_e183_v4.sh"
v4s=$(sha256sum "$PE/rb/s03_desk_e183_v4.sh" | cut -d' ' -f1)   # kit note 3's list pins v4: in P's copy it pins the stand-in, and v5's copy pins that list
sed -i.bak "s#^[0-9a-f]\{64\}  tools/claims-v3/e183/rb/s03_desk_e183_v4.sh\$#$v4s  tools/claims-v3/e183/rb/s03_desk_e183_v4.sh#" "$PE/SHA256SUMS-e183-kit-note3" && rm -f "$PE/SHA256SUMS-e183-kit-note3.bak"
k3=$(sha256sum "$PE/SHA256SUMS-e183-kit-note3" | cut -d' ' -f1)
sed -i.bak "s#^SHA256SUMS-e183-kit-note3:19:[0-9a-f]\{64\}:gate\$#SHA256SUMS-e183-kit-note3:19:$k3:gate#" "$PE/rb/s03_desk_e183_v5.sh" && rm -f "$PE/rb/s03_desk_e183_v5.sh.bak"
[ -s "$PE/logs/selftest-rb-e183-v3.txt" ] || echo "SELFTEST-RB-E183-V3 PASS (a stand-in line written by the runbook desk test v3 for its case P)" > "$PE/logs/selftest-rb-e183-v3.txt"
for f in desktest-train-check-e183.txt selftest-rest-e183.txt dry-intel-e183-v2.txt; do
  [ -s "$PE/logs/$f" ] || echo "$(echo "$f" | sed 's/\.txt$//; s/-/ /g' | tr 'a-z ' 'A-Z-') PASS (a stand-in line)" > "$PE/logs/$f"
done
N4="train_check_e183.sh build_host_e183_v2.sh block_e183_v2.sh queue_e183_v2.sh session_e183_v2.sh preflight_e183_v2.sh harness_e183_v2.py
harness-e183-v2.json make_harness_e183_v2.py dry_intel_e183_v2.sh desk/desktest_train_check_e183.sh desk/mock_runtime_e183_v2.cpp
rb/s06_a3_records_e183.sh rb/s08_a3_build_e183_v2.sh rb/s10_a3_dry_e183_v2.sh rb/s11_a3_session_e183_v2.sh rb/rest_rule_e183.sh
rb/list_steps_e183_v5.sh rb/selftest_rest_e183.sh rb/selftest_rb_e183_v3.sh rb/fake_cmake_gcc_e183.sh logs/selftest-rb-e183-v3.txt
logs/desktest-train-check-e183.txt logs/selftest-rest-e183.txt logs/dry-intel-e183-v2.txt"     # a stand-in of note 4's list (the real one is made last)
( cd "$P" && for f in $N4; do [ -f "tools/claims-v3/e183/$f" ] && sha256sum "tools/claims-v3/e183/$f"; done ) > "$PE/SHA256SUMS-e183-kit-note4"
pn=$(grep -c . "$PE/SHA256SUMS-e183-kit-note4"); ps=$(sha256sum "$PE/SHA256SUMS-e183-kit-note4" | cut -d' ' -f1)
sed -i.bak "s/^NOTE4_N=.*/NOTE4_N=$pn/; s/^NOTE4_SHA=.*/NOTE4_SHA=$ps/" "$PE/rb/s03_desk_e183_v5.sh" && rm -f "$PE/rb/s03_desk_e183_v5.sh.bak"
GP="git -C $P -c user.name=e183-desktest -c user.email=desktest@localhost -c core.hooksPath=/dev/null -c commit.gpgsign=false"
$GP init -q && $GP add -A && $GP commit -q -m "desk: step 2 v5's scratch repository" || { echo "the P repository failed"; return 2; }
echo "P's repository: $($GP ls-files | wc -l | tr -d ' ') files; the stand-in note 4 list: $pn entries"
mkdir -p "$S/out-p"; RB_OUT="$S/out-p" bash "$R/s02_window_e183.sh" "$TODAY" 23:00 23:30 > /dev/null 2>&1
p5() {  # p5 <case>: v5 on P, its exit status
  RB_REPO="$P" RB_OUT="$S/out-p" bash "$PE/rb/s03_desk_e183_v5.sh" > "$S/$1.txt" 2>&1; local r=$?
  grep -E 'STOP|desk check v5|reported' "$S/$1.txt" | sed "s#$S#<scratch>#g" | cut -c1-260; return "$r"
}
reset_p() { $GP reset -q --hard HEAD~"$1"; }
p5 P1; ok "$?" "0" "P1 step 2 v5 passes at its pins"
sed -i.bak '1s/^[0-9a-f]\{64\}/0000000000000000000000000000000000000000000000000000000000000000/' "$PE/SHA256SUMS-e183-kit-note4"; rm -f "$PE/SHA256SUMS-e183-kit-note4.bak"; $GP commit -q -am "desk: a changed entry"
p5 P2; r=$?; ok "$r.$(has 'SHA256SUMS-e183-kit-note4' "$S/P2.txt")" "16.1" "P2 a changed entry in note 4's list: refused"; reset_p 1
sed -i.bak '$d' "$PE/SHA256SUMS-e183-kit-note4"; rm -f "$PE/SHA256SUMS-e183-kit-note4.bak"; $GP commit -q -am "desk: one line short"
p5 P3; r=$?; ok "$r.$(has 'SHA256SUMS-e183-kit-note4' "$S/P3.txt")" "16.1" "P3 note 4's list one line short: refused"; reset_p 1
sed -i.bak '$d' "$PE/SHA256SUMS-e183-kit-note3"; rm -f "$PE/SHA256SUMS-e183-kit-note3.bak"; $GP commit -q -am "desk: kit note 3's list short"
p5 P4; r=$?; ok "$r.$(has 'SHA256SUMS-e183-kit-note3' "$S/P4.txt")" "16.1" "P4 kit note 3's list one line short: refused"; reset_p 1
head -n 2 "$PE/SHA256SUMS-e183-kit" > "$PE/logs/extra-SHA256SUMS-x"; $GP add -A; $GP commit -q -m "desk: an unknown list"
p5 P5; r=$?; ok "$r.$(has 'extra-SHA256SUMS-x: a list this step does not know' "$S/P5.txt")" "0.1" "P5 SHA256SUMS in the middle of a name is found; unknown, reported, never a gate"; reset_p 1
sed -i.bak '$d' "$PE/SHA256SUMS-e183-m1"; rm -f "$PE/SHA256SUMS-e183-m1.bak"; $GP commit -q -am "desk: note M1's list changed"
p5 P6; r=$?; ok "$r.$(has 'SHA256SUMS-e183-m1 24 OK of 24 (pinned 25), own bytes NOT as pinned (reported)' "$S/P6.txt")" "0.1" "P6 note M1's list changed: reported, never a gate"; reset_p 1
PREPO_V4_RC=16 p5 P7; r=$?; ok "$r.$(has 'desk check v5' "$S/P7.txt")" "16.0" "P7 step 2 v4's 16 stops v5 before its own checks"

step "Z. no process of this test left running; the device record"
left=$(pgrep -f "$S/boxbin/cmake|build/q141k/jobs/a3-(build|dry)-e183[.]sh" 2>/dev/null | grep -c .)
ok "$left.$(nrec)" "0.0" "Z nothing left running; no device record in any case"
echo
echo "SELFTEST-RB-E183-V3 $([ "$fail" -eq 0 ] && echo PASS || echo FAIL) ($npass of $ncase)"
return "$fail"
}
main 2>&1 | sed "s#$S#<scratch>#g; s#$SRC#<repo>#g"
exit "${PIPESTATUS[0]}"
