#!/usr/bin/env bash
# E181 (M11's session 2): the desk test of E181's runbook as the kit's dated note 1 (README.md.dated-note-1.md) orders it: selftest_rb_e181.sh
# (33cdccf6, which stays as committed) on the note's steps (s11 v2, s12, s22 v2 with the collector v2 and M11's scorer v4), with a case for
# each of the E181 kit verifier's faults the note fixes, each also run on the v1 step where that shows the fault. Stand-in ssh and rsync sit
# first on PATH and serve a stand-in box (a local directory laid out like aifoundry3's ~/aifoundry); no lab box is reached. A date shim runs
# GNU date. Every tree is a scratch copy under <scratch dir>, never the lab clone. The cases:
#   A    the dry listing v2: every step exits 0, no ssh or rsync call;
#   P1, L1-L4, W1-W5    v1's, unchanged (the steps they call are v1's: s08, s20);
#   S1-S6   v1's, on s11 v2 (the same answers);
#   S7   FAULT 7: a real session block with no "session end" 25 minutes ago (it was killed), after a real end 3 h ago: s11 v2 refuses (10,
#        "counted as ended at its last line"); s11 v1 launches on the end 3 h ago (0: the fault);
#   S8   a block that ended at a session gate ("no device opened") 10 minutes ago, after a real end 3 h ago: skipped, launched (0, 180 min);
#   H1   step 12's start window on a stand-in hwmon tree: 0, the NVMe composite and coretemp 2-9 read, host-start.out on the box;
#   H2   step 12's end window: host-end.out;  H3  the stand-in tree named without RB_DESKTEST=1: ignored (the box's own /sys read);
#   C1-C20 v1's collection cases on s22 v2 with stand-in collector and scorer (C3's words are v2's; C7 and C16 now also checked for no
#        scored file; C1, C4, C6 and C11 leave the STAND-IN scorer's files by design: E6 shows the real scorer v4 leaves none);
#   C21  SMOKE-STOPPED (the session's last block: the smoke or its gate failed, no measured pass): 16, no scored file;
#   C22  STOP-FILE: 16;  C23  NO-DEVICE (a session gate, no device opened): 16;  C24  no session log collected: 16;
#   U1, U2  v1's: E166's and E154's committed sessions through the launch gate (COUNT-OK);
#   E1   the real collector v2 and M11's scorer v4 end to end on a stand-in box holding E154's committed passes: 0, the scorer's six stages,
#        A9's arm SCORED (H_E's shift as A9's post hoc reads E154's H_M), no staging file;
#   E2   the measured pass's C log absent on the box: 14, MISSING-CLOG p18120, no scored file;
#   E3   FAULT 2: A6-1 as the real box leaves it (no e181/ directory, the A6-1 session log, step 10's dry smoke-gate.json in build/e181/): s22 v2
#        16 F0-STOPPED, "absent on the box", the dry smoke gate set aside in logs/not-this-session/, no scored file; E3v1: s22 v1 on the same
#        box, 14 on "rsync e181 rc=23" (the fault);
#   E4   G0-REFUSED with the real collector v2: 16;
#   E5   FAULT 5: another login's holder line in the measured pass's run.log: s22 v2 16 (LOGIN-LEFT in that directory), no scored file;
#        E5v1: s22 v1 reads logs/ only and scores (0: the fault);
#   E6   FAULT 4: a start_gate mark that lies (passed true, numbers that refuse) gets past the marks' gate to the score: v4 refuses before any
#        file (14, no scored file left); E6v1: s22 v1 with v3 refuses too, but leaves scored-m11-lines.jsonl (the fault);
#   O1   ours_live names E181's, E178's and E180's processes, and none of the note's new step or helper names.
#
#   bash tools/claims-v3/e181/rb/selftest_rb_e181_v2.sh <scratch dir> > <log>
# SPDX-License-Identifier: Apache-2.0
set -u
SRC=$(cd "$(dirname "${BASH_SOURCE[0]}")/../../../.." && pwd)
S=${1:?a scratch directory outside the repository}
case "$S" in "$SRC"|"$SRC"/*) echo "the scratch directory must be outside the repository"; exit 2 ;; esac
mkdir -p "$S"
S=$(cd "$S" && pwd -P)
rm -rf "${S:?}/tree" "${S:?}/tree2" "${S:?}/box" "${S:?}/box2" "${S:?}/bin" "${S:?}/out" "${S:?}/out2" "${S:?}/dry-out" "${S:?}/u" "${S:?}/cache" "${S:?}/hwmon"
DATA=$SRC/tools/claims-v3/e181/rb/selftest_data_e181.py
E166=$SRC/docs/reports/data/2026-11-04-e166-heat-replicate-aifoundry3
E154=$SRC/docs/reports/data/2026-11-03-e154-heat-e2e-aifoundry3
fail=0
ok() { if [ "$1" = "$2" ]; then echo "-> PASS ($3)"; else echo "-> FAIL ($3: rc $1, want $2)"; fail=1; fi; }
step() { echo; echo "== $*"; }
show() { grep -m2 -E "$2|STOP" "$1" | sed "s#$S#<scratch>#g" | cut -c1-240; }
t_begin=$(date +%s)

# ---- the scratch tree: the runbook, the kit, v3.1's runner and gates, E164's scrub, the lists step 22 v2 checks first
T=$S/tree; B=$S/box; BIN=$S/bin
mkdir -p "$T/tools/claims-v3" "$B/aifoundry3/aifoundry" "$BIN" "$S/out"
for p in e181 e181/rb q141k-runbook/v3.1; do mkdir -p "$T/tools/claims-v3/$p"; cp -p "$SRC/tools/claims-v3/$p"/*.* "$T/tools/claims-v3/$p/" 2>/dev/null; done
mkdir -p "$T/tools/claims-v3/e164" "$T/tools/claims-v3/m11"; cp -p "$SRC/tools/claims-v3/e164/scrub_etwho_e164.py" "$T/tools/claims-v3/e164/"
for f in score_m11_v3.py score_m11_v4.py REGISTRATION.md.dated-note-A9.md a9_posthoc.py a9-posthoc.json a9-posthoc.txt; do cp -p "$SRC/tools/claims-v3/m11/$f" "$T/tools/claims-v3/m11/"; done
mklist() {  # mklist <tree>: the lists step 22 v1 and v2 check first, over that tree's own copies (the committed lists also pin logs and notes)
  ( cd "$1" && shasum -a 256 tools/claims-v3/m11/score_m11_v4.py > tools/claims-v3/m11/SHA256SUMS-score-m11-v4 &&
    shasum -a 256 tools/claims-v3/m11/REGISTRATION.md.dated-note-A9.md tools/claims-v3/m11/a9_posthoc.py tools/claims-v3/m11/a9-posthoc.json \
      tools/claims-v3/m11/a9-posthoc.txt > tools/claims-v3/m11/SHA256SUMS-a9 &&
    shasum -a 256 tools/claims-v3/m11/score_m11_v3.py > tools/claims-v3/m11/SHA256SUMS-score-m11-v3 &&
    shasum -a 256 tools/claims-v3/e181/*.sh tools/claims-v3/e181/*.py > tools/claims-v3/e181/kit-e181.sha256 &&
    shasum -a 256 tools/claims-v3/e181/rb/*.sh tools/claims-v3/e181/rb/*.py > tools/claims-v3/e181/rb/SHA256SUMS-rb-e181 &&
    shasum -a 256 tools/claims-v3/e181/*_v2.sh tools/claims-v3/e181/rb/*_v2.sh tools/claims-v3/e181/rb/s12_a3_host_e181.sh \
      tools/claims-v3/e181/rb/scrub_all_e181.py > tools/claims-v3/e181/SHA256SUMS-note1 )
}
mklist "$T"
REAL_RSYNC=$(command -v rsync)
GDATE=$(command -v gdate)
[ -n "$GDATE" ] || { echo "GNU date (gdate) is needed for the stand-in box"; exit 2; }
cat > "$BIN/date" <<EOF
#!/bin/sh
exec "$GDATE" "\$@"
EOF
cat > "$BIN/ssh" <<EOF
#!/bin/bash
echo "ssh \$*" >> "$S/calls.log"
host=""; cmd=""
while [ \$# -gt 0 ]; do case "\$1" in -o) shift 2 ;; -*) shift ;; *) if [ -z "\$host" ]; then host=\$1; shift; else cmd="\$*"; break; fi ;; esac; done
if [ "\$cmd" = true ]; then
  case "\${Q_PROBE:-answer}" in link) echo "To authenticate, visit: https://login.tail""scale.com/a/e181selftest01" >&2; sleep 30; exit 1 ;; hang) sleep 60; exit 0 ;; *) exit 0 ;; esac
fi
case "\${Q_SSH:-answer}" in hang) sleep 60; exit 0 ;; fail) exit 1 ;; esac
# real ssh hands the remote shell its script through a pipe; so does this stand-in (a seekable file under bash -s lets a backgrounded
# command's fork move the shared offset on macOS's bash 3.2, which re-reads part of a line: a stand-in artifact, not the box's)
cat | HOME="\${Q_BOX:-$B}/\$host" bash -c "cd ~ && \$cmd"
EOF
cat > "$BIN/rsync" <<EOF
#!/bin/bash
echo "rsync \$*" >> "$S/calls.log"
a=()
while [ \$# -gt 0 ]; do case "\$1" in -e) shift 2 ;; *:*) h=\${1%%:*}; p=\${1#*:}; a+=("\${Q_BOX:-$B}/\$h/\$p"); shift ;; *) a+=("\$1"); shift ;; esac; done
exec "$REAL_RSYNC" "\${a[@]}"
EOF
chmod +x "$BIN/ssh" "$BIN/rsync" "$BIN/date"
export PATH="$BIN:$PATH" RB_REPO="$T" RB_OUT="$S/out" RB_LOCK="$S/lock.txt"
: > "$S/calls.log"; : > "$RB_LOCK"
R=$T/tools/claims-v3/e181/rb
A3=$B/aifoundry3/aifoundry
cd "$T" || exit 2

step "A. the dry listing v2: every step exits 0, no ssh or rsync call"
: > "$S/calls.log"
bash "$R/list_steps_e181_v2.sh" "$S/dry-out" > "$S/dry-listing.txt" 2>&1; rc=$?
n=$(grep -c . "$S/calls.log"); tail -n 1 "$S/dry-listing.txt"; echo "calls: $n"
ok "$rc.$n" "0.0" "dry listing v2"

step "P1. a file the runbook pins changed (v3.1's rb_run.py): 16, before any call"
cp -p "$T/tools/claims-v3/q141k-runbook/v3.1/rb_run.py" "$S/rb_run.keep"; echo "# a change" >> "$T/tools/claims-v3/q141k-runbook/v3.1/rb_run.py"
: > "$S/calls.log"
bash "$R/s08_a3_preflight_e181.sh" > "$S/p1.txt" 2>&1; rc=$?
n=$(grep -c . "$S/calls.log"); show "$S/p1.txt" STOP
cp -p "$S/rb_run.keep" "$T/tools/claims-v3/q141k-runbook/v3.1/rb_run.py"
ok "$rc.$n" "16.0" "exit 16, no call"

step "L1. a login link at the probe"
Q_PROBE=link bash "$R/s08_a3_preflight_e181.sh" > "$S/l1.txt" 2>&1; rc=$?
show "$S/l1.txt" STOP; tail -n 1 "$RB_LOCK" | sed -E 's/^[0-9:]+/<HH:MM:SS>/'
lk=$(grep -cE '^[0-9]{2}:[0-9]{2}:[0-9]{2} aifoundry3 needs a check$' "$RB_LOCK")
ok "$rc.$lk" "11.1" "exit 11 and one lock line"
step "L2. a probe that never answers (bound 2 s)"
RB_PROBE_S=2 Q_PROBE=hang bash "$R/s08_a3_preflight_e181.sh" > "$S/l2.txt" 2>&1; rc=$?
show "$S/l2.txt" STOP; ok "$rc" 12 "exit 12"
step "L3. a read past its bound (2 s)"
RB_READ_S=2 Q_SSH=hang bash "$R/s08_a3_preflight_e181.sh" > "$S/l3.txt" 2>&1; rc=$?
show "$S/l3.txt" STOP; ok "$rc" 13 "exit 13"
step "L4. a box whose preflight reads wrong (its three binaries missing: the box list reads 27 of 30)"
mkdir -p "$A3/tools/claims-v3/e181"
( cd "$SRC" && tar -cf - $(awk '{print $2}' tools/claims-v3/e181/frozen-e181.sha256 | grep -v '^build/') tools/claims-v3/e181/frozen-e181.sha256 ) | tar -xf - -C "$A3"
printf 'echo "dmcmd_audit: GO (38 send site(s), 0 disallowed; allow-list: none)"\n' > "$A3/tools/claims-v3/e181/preflight_e181.sh"
bash "$R/s08_a3_preflight_e181.sh" > "$S/l4.txt" 2>&1; rc=$?
show "$S/l4.txt" STOP; seen=0; grep -q 'boxlist' "$S/l4.txt" && seen=1; ok "$rc.$seen" "16.1" "exit 16, the box list named"

mklog() {  # mklog <line> ...: a fresh offset of 2 and a session log of two older lines and the given ones
  mkdir -p "$A3/build/q141k" "$A3/build/e181"
  echo 2 > "$A3/build/q141k/e181.log-offset"
  { echo "2026-11-05 10:00:00 PST session start (an earlier day's)"; echo "2026-11-05 11:15:00 PST session end"; printf '%s\n' "$@"; } > "$A3/build/e181/session.log"
}
step "W1. the session log ends after the offset"
mklog "$(date '+%F %T %Z') session start" "$(date '+%F %T %Z') pass 18120 rc=0" "$(date '+%F %T %Z') session end"
RB_WAIT_LOOP_S=5 bash "$R/s20_wait_e181.sh" > "$S/w1.txt" 2>&1; rc=$?
show "$S/w1.txt" 'has ended'; ok "$rc" 0 "exit 0"
step "W2. no session process and no session end"
mklog "$(date '+%F %T %Z') session start"
RB_WAIT_LOOP_S=5 bash "$R/s20_wait_e181.sh" > "$S/w2.txt" 2>&1; rc=$?
show "$S/w2.txt" 'RUN-GONE'; ok "$rc" 14 "exit 14"
step "W3. the smoke or its gate failed"
mklog "$(date '+%F %T %Z') session start" "$(date '+%F %T %Z') the smoke or its gate failed: no measured pass" "$(date '+%F %T %Z') session end"
RB_WAIT_LOOP_S=5 bash "$R/s20_wait_e181.sh" > "$S/w3.txt" 2>&1; rc=$?
show "$S/w3.txt" 'ended at a gate'; ok "$rc" 16 "exit 16"
step "W4. G0-A6 with A8-4 refused the measured pass"
mklog "$(date '+%F %T %Z') session start" "$(date '+%F %T %Z') pass 18120 rc=7: the start gate (G0-A6 with A8-4: R0's room above 53.9 C, or its residue less 0.414 C above 0.50 C): no hold ran, E181 not started" "$(date '+%F %T %Z') session end"
RB_WAIT_LOOP_S=5 bash "$R/s20_wait_e181.sh" > "$S/w4.txt" 2>&1; rc=$?
show "$S/w4.txt" "start gate refused"; seen=0; grep -q 'G0-REFUSED' "$S/w4.txt" && seen=1; ok "$rc.$seen" "16.1" "exit 16, G0-REFUSED"
step "W5. A6-1 ended the session before the smoke's first launch"
mklog "$(date '+%F %T %Z') session start" "$(date '+%F %T %Z') smoke and stop tests rc=7" "$(date '+%F %T %Z') A6-1: F0 above 53.9 C or unreadable (the smoke's floor mark): the session ends before the smoke's first launch, no hold (exit 7)" "$(date '+%F %T %Z') session end"
RB_WAIT_LOOP_S=5 bash "$R/s20_wait_e181.sh" > "$S/w5.txt" 2>&1; rc=$?
show "$S/w5.txt" "A6-1"; seen=0; grep -q 'STOP: e181 ended at A6-1' "$S/w5.txt" && seen=1; ok "$rc.$seen" "16.1" "exit 16, A6-1 read on its own"

step "S1. fewer than 76 minutes before the last end (s11 v2)"
le=$(date -d '+60 min' '+%H:%M'); lsx=$(date -d '+30 min' '+%H:%M')
if [ "$(date -d '+60 min' +%F)" = "$(date +%F)" ] && [ "$(date -d '+30 min' +%F)" = "$(date +%F)" ]; then
  bash "$R/s02_window_e181.sh" "$(date +%F)" "$lsx" "$le" > "$S/s1w.txt" 2>&1
  : > "$S/calls.log"
  RB_DESKTEST=1 RB_NOW_HM=0900 bash "$R/s11_a3_launch_e181_v2.sh" > "$S/s1.txt" 2>&1; rc=$?
  n=$(grep -c . "$S/calls.log"); show "$S/s1.txt" STOP; ok "$rc.$n" "16.0" "exit 16, no box call"
else
  echo "(skipped: the test runs within an hour of midnight)"
fi
bash "$R/s02_window_e181.sh" "$(date +%F)" 23:58 23:59 > "$S/window.txt" 2>&1
mkdir -p "$A3/build/q141k/jobs"; echo 0 > "$A3/build/q141k/jobs/a3-dry-e181.rc"; echo 1 > "$A3/build/q141k/jobs/a3-dry-e181.pid"
rm -f "$A3/build/e181/session.log" "$A3/build/e181/session-dry.log"
launch() {  # launch <case> [s11 v2 options]: the step at 09:00 by the desk test's clock
  local c=$1; shift
  rm -rf "${A3:?}/build/claims-v3/aifoundry3/e181-smoke"
  RB_DESKTEST=1 RB_NOW_HM=${NOW_HM:-0900} bash "$R/${S11:-s11_a3_launch_e181_v2.sh}" "$@" > "$S/$c.txt" 2>&1
}
step "S2. an earlier E181 smoke on the box, without --later-try"
rm -rf "${A3:?}/build/claims-v3/aifoundry3/e181-smoke"; mkdir -p "$A3/build/claims-v3/aifoundry3/e181-smoke/p18101"
RB_DESKTEST=1 RB_NOW_HM=0900 bash "$R/s11_a3_launch_e181_v2.sh" > "$S/s2.txt" 2>&1; rc=$?
show "$S/s2.txt" 'REFUSED'; seen=0; grep -q 'STOP: e181 refused on the box: REFUSED: an earlier E181 smoke' "$S/s2.txt" && seen=1
ok "$rc.$seen" "10.1" "exit 10, the earlier smoke named"
step "S3. E176's real session ended 10 minutes ago (the 40-minute gate)"
mkdir -p "$A3/build/e176"; { echo "$(date -d '20 min ago' '+%F %T %Z') session start (T0 x)"; echo "$(date -d '10 min ago' '+%F %T %Z') session end"; } > "$A3/build/e176/session.log"
launch s3; rc=$?
show "$S/s3.txt" 'REFUSED'; seen=0; grep -qE "REFUSED: (9|10|11) minutes since E176's session end" "$S/s3.txt" && seen=1
ok "$rc.$seen" "10.1" "exit 10, E176's session end named"
step "S4. the note-2 defect fixed: dry sessions' ends 10 minutes ago are skipped; the real end 3 h ago decides"
{ echo "$(date -d '200 min ago' '+%F %T %Z') session start (T0 x)"; echo "$(date -d '180 min ago' '+%F %T %Z') session end"
  echo "$(date -d '15 min ago' '+%F %T %Z') session start (T0 y)"; echo "$(date -d '14 min ago' '+%F %T %Z') DRY config config-session-start.json"
  echo "$(date -d '10 min ago' '+%F %T %Z') session end"; } > "$A3/build/e176/session.log"
mkdir -p "$A3/build/e181"; { echo "$(date -d '12 min ago' '+%F %T %Z') session start (T0 z) DRY"; echo "$(date -d '10 min ago' '+%F %T %Z') DRY session end"; } > "$A3/build/e181/session-dry.log"
launch s4; rc=$?
show "$S/s4.txt" 'rest: |LAUNCHED'; seen=0; grep -qE 'rest: (179|180|181) minutes since E176' "$S/s4.txt" && grep -q 'e181 launched on aifoundry3' "$S/s4.txt" && seen=1
ok "$rc.$seen" "0.1" "launched; the rest read 180 minutes from E176's real end"
rm -f "$A3/build/e181/session.log"
step "S5. a real session end 50 minutes ago: A7-4's hour"
{ echo "$(date -d '80 min ago' '+%F %T %Z') session start (T0 x)"; echo "$(date -d '50 min ago' '+%F %T %Z') session end"; } > "$A3/build/e176/session.log"
launch s5a; r1=$?; show "$S/s5a.txt" 'REFUSED'
launch s5b --under-an-hour; r2=$?; show "$S/s5b.txt" 'departure'
seen=0; grep -q "REFUSED: (49|50|51) minutes\|A7-4's plan asks for an hour" "$S/s5a.txt" && grep -q 'departure: --under-an-hour' "$RB_OUT/runbook.log" && seen=1
ok "$r1.$r2.$seen" "10.0.1" "refused without the flag; launched with it, the departure logged"
rm -f "$A3/build/e176/session.log" "$A3/build/e181/session.log"
step "S6. at 12:05 PST by the desk test's clock: the cool-hour plan"
NOW_HM=1205 launch s6a; r1=$?; show "$S/s6a.txt" 'STOP'
NOW_HM=1205 launch s6b --after-noon; r2=$?
seen=0; grep -q 'cool-hour plan asks for a launch before 12:00 PST' "$S/s6a.txt" && grep -q 'departure: --after-noon at 1205 PST' "$RB_OUT/runbook.log" && seen=1
ok "$r1.$r2.$seen" "10.0.1" "refused without --after-noon; past the check with it, logged"
rm -f "$A3/build/e181/session.log"
step "S7. FAULT 7: a real block with no session end 25 minutes ago (killed), after a real end 3 h ago"
{ echo "$(date -d '200 min ago' '+%F %T %Z') session start (T0 x)"; echo "$(date -d '180 min ago' '+%F %T %Z') session end"
  echo "$(date -d '30 min ago' '+%F %T %Z') session start (T0 k)"; echo "$(date -d '25 min ago' '+%F %T %Z') smoke and stop tests rc=0"; } > "$A3/build/e176/session.log"
touch -t "$(date -d '25 min ago' '+%Y%m%d%H%M.%S')" "$A3/build/e176/session.log"
launch s7; r2=$?; show "$S/s7.txt" 'REFUSED|note:'
S11=s11_a3_launch_e181.sh launch s7v1; r1=$?; show "$S/s7v1.txt" 'rest: |LAUNCHED'
seen=0; grep -qE "REFUSED: (24|25|26) minutes since E176's last real session line \(its block has no session end: counted as ended at its last line\)" "$S/s7.txt" \
  && grep -qE 'rest: (179|180|181) minutes since E176' "$S/s7v1.txt" && seen=1
ok "$r2.$r1.$seen" "10.0.1" "v2 refused, the unended block counted at its last line; v1 launched on the end 3 h ago (the fault)"
rm -f "$A3/build/e181/session.log"
step "S8. a block that ended at a session gate (no device opened) 10 minutes ago, after a real end 3 h ago"
{ echo "$(date -d '200 min ago' '+%F %T %Z') session start (T0 x)"; echo "$(date -d '180 min ago' '+%F %T %Z') session end"
  echo "$(date -d '10 min ago' '+%F %T %Z') session start (T0 g)"; echo "$(date -d '10 min ago' '+%F %T %Z') no new card session after 2026-11-06 08:00:00 PST: no device opened"; } > "$A3/build/e176/session.log"
launch s8; rc=$?
show "$S/s8.txt" 'rest: |LAUNCHED'; seen=0; grep -qE 'rest: (179|180|181) minutes since E176' "$S/s8.txt" && seen=1
ok "$rc.$seen" "0.1" "the gate block skipped; launched on the real end 3 h ago"
rm -f "$A3/build/e176/session.log" "$A3/build/e181/session.log"

step "H1. step 12's start window on a stand-in hwmon tree (A6-5)"
HWM=$S/hwmon
mkdir -p "$HWM/hwmon0" "$HWM/hwmon1" "$HWM/hwmon2"
echo nvme > "$HWM/hwmon0/name"; echo 38850 > "$HWM/hwmon0/temp1_input"; echo 38850 > "$HWM/hwmon0/temp2_input"; echo 41850 > "$HWM/hwmon0/temp3_input"
echo coretemp > "$HWM/hwmon1/name"; for i in 1 2 3 4 5 6 7 8 9; do echo $((32000 + 1000 * (i % 3))) > "$HWM/hwmon1/temp${i}_input"; done
echo other > "$HWM/hwmon2/name"; echo 99000 > "$HWM/hwmon2/temp1_input"
RB_DESKTEST=1 RB_HWMON="$HWM" RB_HOST_EVERY_S=0 bash "$R/s12_a3_host_e181.sh" start > "$S/h1.txt" 2>&1; rc=$?
show "$S/h1.txt" 'HOST-WINDOW'
seen=0; grep -q 'HOST-WINDOW start: nvme temp1 38.850 C; coretemp 2-9 mean 33.000 (8 sensors) C' "$S/h1.txt" && [ -f "$A3/build/e181/host-start.out" ] \
  && ! grep -q '^other:' "$A3/build/e181/host-start.out" && seen=1
ok "$rc.$seen" "0.1" "read: the NVMe composite and coretemp 2-9; another hwmon left out; host-start.out on the box"
step "H2. step 12's end window"
RB_DESKTEST=1 RB_HWMON="$HWM" RB_HOST_EVERY_S=0 bash "$R/s12_a3_host_e181.sh" end > "$S/h2.txt" 2>&1; rc=$?
seen=0; [ -f "$A3/build/e181/host-end.out" ] && grep -q 'HOST-WINDOW end' "$S/h2.txt" && seen=1; ok "$rc.$seen" "0.1" "host-end.out on the box"
step "H3. the stand-in hwmon tree named without RB_DESKTEST=1: ignored (the dry listing shows the box's own /sys/class/hwmon, 10 s apart)"
RB_DRY=1 RB_HWMON="$HWM" RB_HOST_EVERY_S=0 bash "$R/s12_a3_host_e181.sh" start > "$S/h3.txt" 2>&1; rc=$?
grep -m1 'ACT=start' "$S/h3.txt" | sed "s#$S#<scratch>#g"
seen=0; grep -q 'ACT=start; HW=/sys/class/hwmon; EVERY=10$' "$S/h3.txt" && seen=1; ok "$rc.$seen" "0.1" "the box's own sysfs and the 10 s spacing, the stand-ins ignored"
rm -f "$A3/build/e181/host-start.out" "$A3/build/e181/host-end.out"

# ---- the collection (step 22 v2) with stand-in collector and scorer (selftest_data_e181.py synth, MODE names the fault)
cat > "$S/collect_stub.sh" <<EOF
#!/bin/bash
D=\$1
mkdir -p "\$D/ccheck" "\$D/logs"
f=""
case "\${MODE:-}" in
  noclog) f=no-measured-clog ;; short) f=short-measured ;; smokenolog) f=no-smoke-clog ;; smokenolaunch) f=smoke-nolaunch ;;
  orphan) f=orphan ;; nolaunch) f=measured-nolaunch ;; emptyclog) f=empty-measured-clog ;; norecords) f=no-records ;;
  g0) f=g0-refused ;; f0) f=f0-stopped ;; dup) f=dup-start ;;
esac
/usr/bin/python3 -B "$DATA" synth "\$D" \$f > /dev/null || exit 9
t="2026-11-06 09:00:00 PST"
case "\${MODE:-}" in
  smokefail) printf '%s\n' "\$t session start (T0 x)" "\$t smoke and stop tests rc=1" "\$t smoke gate rc=1: {}" "\$t the smoke or its gate failed: no measured pass" "\$t session end" > "\$D/logs/session.log"
             rm -rf "\${D:?}/aifoundry3/e181" ;;
  stopfile) printf '%s\n' "\$t session start (T0 x)" "\$t smoke gate rc=0: {}" "\$t STOP file: no measured pass" "\$t session end" > "\$D/logs/session.log"
            rm -rf "\${D:?}/aifoundry3/e181" ;;
  nodev) printf '%s\n' "\$t session start (T0 x)" "\$t no new card session after 2026-11-06 08:00:00 PST: no device opened" > "\$D/logs/session.log"
         rm -rf "\${D:?}/aifoundry3" ;;
  nolog) rm -rf "\${D:?}/aifoundry3/e181" ;;
  *) printf '%s\n' "\$t session start (T0 x)" "\$t smoke gate rc=0: {}" "\$t pass 18120 rc=0" "\$t session end" > "\$D/logs/session.log" ;;
esac
[ "\${MODE:-}" = copy ] && echo "rsync e181 rc=23"
[ "\${MODE:-}" = crash ] && rm -f "\$D/ccheck/ccheck-all.json"
[ "\${MODE:-}" = f0 ] && rm -f "\$D/ccheck/ccheck-all.json"
[ "\${MODE:-}" != crash ] && echo "ccheck rc=0"
[ "\${MODE:-}" = stale ] && touch -t 202611050001 "\$D/ccheck/ccheck-all.json"
echo "collected (no score: step 22 scores after its gates)"
EOF
cat > "$S/score_stub.sh" <<EOF
#!/bin/bash
D=\$1
echo "# M11 on aifoundry3 (stand-in)" > "\$D/scored-m11.md"; echo '{}' > "\$D/scored-m11.json"; echo '{"stage": 1}' > "\$D/scored-m11-lines.jsonl"
[ "\${MODE:-}" = path ] && echo "a desk path: \$PWD/build/e181" >> "\$D/scored-m11.md"
if [ "\${MODE:-}" = score ]; then echo "score rc=1"; else echo "score rc=0"; fi
EOF
chmod +x "$S/collect_stub.sh" "$S/score_stub.sh"
DD=$T/docs/reports/data/$(date +%F)-e181-m11-session2-aifoundry3
cn() {  # cn <case> <want rc> <want line> <mode>
  local c=$1 want=$2 line=$3 mode=$4
  rm -rf "${T:?}/docs"
  MODE=$mode RB_DESKTEST=1 E181_COLLECT="$S/collect_stub.sh" E181_SCORE="$S/score_stub.sh" bash "$R/s22_collect_e181_v2.sh" > "$S/$c.txt" 2>&1; rc=$?
  grep -E "$line|STOP" "$S/$c.txt" | head -n 3 | sed "s#$S#<scratch>#g" | cut -c1-260
  local seen=0; grep -qE "$line" "$S/$c.txt" && seen=1
  ok "$rc.$seen" "$want.1" "$c"
}
noscore() {  # noscore <case>: no scored file in the data directory after the step
  local n; n=$(ls "$DD"/scored-m11* 2>/dev/null | wc -l | tr -d ' ')
  echo "   scored files in the data directory after $1: $n"
  [ "$n" -eq 0 ] || { echo "-> FAIL ($1: a scored file was written)"; fail=1; }
}
step "C1. a good collection (the check finished and covers every launch; the score after the gates, rc 0)"
cn C1 0 'E181 collected and scored' ""
step "C2. no check file (the check of C crashed)"; cn C2 14 'CCHECK-MISSING' crash; noscore C2
step "C3. a failed copy inside the collector"; cn C3 14 'a copy inside the collector failed' copy; noscore C3
step "C4. the scorer not rc 0 (the stand-in scorer wrote its files first; the step names them)"; cn C4 14 "scorer did not read rc 0.*scored files left: scored-m11.json" score
step "C5. a check file from an earlier try (backdated)"; cn C5 14 'CCHECK-STALE' stale; noscore C5
step "C6. a desk path in a scored file"; cn C6 16 'HIT ' path
step "C7. the stand-ins named without RB_DESKTEST=1"
rm -rf "${T:?}/docs"
E181_COLLECT="$S/collect_stub.sh" bash "$R/s22_collect_e181_v2.sh" > "$S/C7.txt" 2>&1; rc=$?
grep -m1 STOP "$S/C7.txt" | cut -c1-200; ok "$rc" 10 "exit 10"; noscore C7
step "C8. the measured pass carries no C log, the smoke's is checked"; cn C8 14 'MISSING-CLOG p18120' noclog; noscore C8
step "C9. a short check: the measured pass's last process one launch short"; cn C9 14 'COUNT-SHORT p18120' short; noscore C9
step "C10. the smoke's marks show launches and it carries no C log"; cn C10 14 'MISSING-CLOG p18101' smokenolog; noscore C10
step "C11. the smoke ran no launch and carries no C log (not required)"; cn C11 0 'NOT-REQUIRED p18101' smokenolaunch
step "C12. a checked launch outside every launch mark's window"; cn C12 14 'ORPHAN p18120' orphan; noscore C12
step "C13. the measured pass ran no launch with its gate passed"; cn C13 14 'NO-LAUNCH p18120' nolaunch; noscore C13
step "C14. the measured pass's C log empty"; cn C14 14 'MISSING-CLOG p18120' emptyclog; noscore C14
step "C15. a launch mark without records"; cn C15 14 'COUNT-UNREAD p18120' norecords; noscore C15
step "C16. a listed file that differs: 16, before any box call"
cp -p "$R/cclaunch_e181.py" "$S/cclaunch.keep"; echo "# a change" >> "$R/cclaunch_e181.py"
: > "$S/calls.log"; rm -rf "${T:?}/docs"
RB_DESKTEST=1 E181_COLLECT="$S/collect_stub.sh" E181_SCORE="$S/score_stub.sh" bash "$R/s22_collect_e181_v2.sh" > "$S/C16.txt" 2>&1; rc=$?
n=$(grep -c . "$S/calls.log"); grep -m1 STOP "$S/C16.txt" | sed "s#$S#<scratch>#g" | cut -c1-220
seen=0; grep -q 'STOP: a file of tools/claims-v3/e181/rb/SHA256SUMS-rb-e181 differs' "$S/C16.txt" && seen=1
cp -p "$S/cclaunch.keep" "$R/cclaunch_e181.py"
ok "$rc.$n.$seen" "16.0.1" "exit 16, no box call, the list named"; noscore C16
step "C17. G0-REFUSED: the measured pass's start gate refused"; cn C17 16 'G0-REFUSED p18120' g0; noscore C17
step "C18. F0-STOPPED: A6-1 ended the session before the smoke's first launch"; cn C18 16 'F0-STOPPED p18101' f0; noscore C18
step "C19. the fault-2 fix of note 2: a gate stops the step (COUNT-SHORT) before the scorer, so no scored file exists"; cn C19 14 'COUNT-SHORT p18120' short; noscore C19
step "C20. duplicate t_start_ms in the measured pass's launch marks"; cn C20 14 'COUNT-DUP p18120' dup; noscore C20
step "C21. SMOKE-STOPPED: the session's last block says the smoke or its gate failed; no measured pass"; cn C21 16 'SMOKE-STOPPED' smokefail; noscore C21
step "C22. STOP-FILE: a STOP file before the measured pass"; cn C22 16 'STOP-FILE' stopfile; noscore C22
step "C23. NO-DEVICE: the session ended at a session gate, no device opened"; cn C23 16 'NO-DEVICE' nodev; noscore C23
step "C24. no session log collected"; cn C24 16 'NO-SESSION-LOG' nolog; noscore C24
cd "$S" || exit 2

uc() {  # uc <case> <want rc> <want lines (grep -E, each must match)> <source> <smoke rel> <measured rel> [fault ...]
  local c=$1 want=$2 lines=$3 src=$4 s=$5 m=$6; shift 6
  /usr/bin/python3 -B "$DATA" committed "$src" "$s" "$m" "$S/u/$c" "$@" > /dev/null || { echo "data maker failed"; fail=1; return; }
  /usr/bin/python3 -B "$SRC/tools/claims-v3/e181/rb/cclaunch_e181.py" "$S/u/$c" > "$S/u-$c.txt" 2>&1; local rc=$?
  grep -E '^(COUNT|MISSING|cclaunch)' "$S/u-$c.txt" | cut -c1-230
  local seen=1 l
  IFS='|' read -r -a want_lines <<< "$lines"
  for l in "${want_lines[@]}"; do grep -qE "$l" "$S/u-$c.txt" || seen=0; done
  ok "$rc.$seen" "$want.1" "$c"
}
step "U1. E166's committed session (4 Nov), renamed to E181's passes"
uc U1 0 'COUNT-OK p18120: 6644 checked launches in 493 processes|COUNT-OK p18101: 48 checked launches in 6 processes' \
  "$E166" aifoundry3/e166-smoke/p16601 aifoundry3/e166/p16620
step "U2. E154's committed session (3 Nov), renamed"
uc U2 0 'COUNT-OK p18120: 6288 checked launches in 474 processes|COUNT-OK p18101: 58 checked launches in 7 processes' \
  "$E154" aifoundry3/e154-smoke/p15401 aifoundry3/e154/p15420

# ---- the real collector v2 and M11's scorer v4, end to end, on a stand-in box with E154's committed passes
T2=$S/tree2; B2=$S/box2
mkdir -p "$T2/docs/reports/data" "$S/out2" "$S/cache"
git -C "$SRC" archive HEAD tools workloads rtl-sim/fma_toggle_v2 | tar -x -C "$T2"
for p in e181 e181/rb m11; do mkdir -p "$T2/tools/claims-v3/$p"; cp -p "$SRC/tools/claims-v3/$p"/*.* "$T2/tools/claims-v3/$p/" 2>/dev/null; done
mklist "$T2"
for d in "$SRC"/docs/reports/data/*; do ln -s "$d" "$T2/docs/reports/data/$(basename "$d")"; done
DAY=$(date +%F)
D2=$T2/docs/reports/data/$DAY-e181-m11-session2-aifoundry3
[ -e "$D2" ] && { echo "refused: $D2 exists (a link to the lab clone's data?)"; exit 2; }
OWN=$(grep -ohaE '[^/ "]*/aifoundry/tools' "$E154/aifoundry3/e154/p15420/runs.jsonl" | sort -u | head -n 1 | cut -d/ -f1)   # the box's own login, as its paths name it
[ -n "$OWN" ] || { echo "no box login found in E154's committed runs.jsonl"; exit 2; }
mkbox() {  # mkbox [fault ...]: the stand-in box from E154's committed passes (selftest_data_e181.py box)
  rm -rf "${D2:?}" "${B2:?}"
  /usr/bin/python3 -B "$DATA" box "$E154" aifoundry3/e154-smoke/p15401 aifoundry3/e154/p15420 "$B2" "$@" | sed "s#$S#<scratch>#g"
}
run22() {  # run22 <case> <step file>: step 22 on the stand-in box (s02 first), its output in <case>.txt
  local c=$1 st=$2
  : > "$S/calls.log"
  ( export RB_REPO="$T2" RB_OUT="$S/out2" RB_LOCK="$S/lock2.txt" Q_BOX="$B2" CCHECK_CACHE="$S/cache"
    unset RB_DESKTEST E181_COLLECT E181_SCORE
    cd "$T2" && bash tools/claims-v3/e181/rb/s02_window_e181.sh "$DAY" 23:58 23:59 > /dev/null 2>&1
    cd "$T2" && bash "tools/claims-v3/e181/rb/$st" ) > "$S/$c.txt" 2>&1
}
e2e() {  # e2e <case> <want rc> <want line> <step file>: after mkbox
  local c=$1 want=$2 line=$3 st=$4
  run22 "$c" "$st"; local rc=$?
  grep -E "$line|STOP|COUNT-|MISSING-|GATES-|CCHECK-DONE|score rc|ccheck rc|absent on the box|not this session|LOGIN-LEFT|SCRUB-ALL" "$S/$c.txt" \
    | sed "s#$S#<scratch>#g" | sed "s#$OWN#<owner>#g" | cut -c1-240 | head -n 12
  local seen=0; grep -qE "$line" "$S/$c.txt" && seen=1
  echo "stand-in calls: $(grep -c '^rsync' "$S/calls.log") rsync, $(grep -c '^ssh' "$S/calls.log") ssh (the stand-in box only)"
  ok "$rc.$seen" "$want.1" "$c"
}
nscored() { ls "$D2"/scored-m11* 2>/dev/null | wc -l | tr -d ' '; }
step "E1. the real collector v2 and M11's scorer v4: both C logs on the box, and step 12's two host windows in build/e181/"
mkbox
for hw in "start 38.850 33.000" "end 39.850 34.500"; do
  read -r hw_act hw_nv hw_ct <<< "$hw"
  { echo "$DAY 09:00:00 PST"; printf '%-22s mean %s  min %s  max %s  n 13\n' nvme:temp1_input "$hw_nv" "$hw_nv" "$hw_nv"
    for i in 2 3 4 5 6 7 8 9; do printf '%-22s mean %s  min %s  max %s  n 13\n' "coretemp:temp${i}_input" "$hw_ct" "$hw_ct" "$hw_ct"; done
    echo "$DAY 09:02:00 PST"; } > "$B2/aifoundry3/aifoundry/build/e181/host-$hw_act.out"
done
e2e E1 0 'E181 collected and scored' s22_collect_e181_v2.sh
if [ -f "$D2/scored-m11.json" ]; then
  /usr/bin/python3 -B - "$D2" > "$S/E1-scored.txt" <<'PY'
import json, os, sys
d = sys.argv[1]
j = json.load(open(os.path.join(d, "scored-m11.json")))
st = [json.loads(x)["stage"] for x in open(os.path.join(d, "scored-m11-lines.jsonl")) if x.strip()]
ss = list(j["sessions"].values())
e176, s = ss[0], ss[-1]
f = s.get("FL5c", {}).get("primary", {})
a = j.get("arm_A9", {})
sa = list(a.get("sessions", {}).values())
he = sa[0]["holds"]["H_E"]["delta_e_C"] if sa else None
print(f"   scored-m11.json: scorer {j['scorer']}; E176 excluded: {e176.get('excluded')}; holds scored {sum(1 for h in s['holds'].values() if h.get('scored'))} of 5; "
      f"start gate {s['start_gate_reading']['form']} passed {s['start_gate_reading']['passed']}; FL5(c) {f.get('verdict')} (diff {f.get('diff_w_per_c')}); "
      f"HM-LG {j['aifoundry3']['HM_LG']['verdict']}; label {j['label'][:9]}; lines file stages {st}; staging left {os.path.exists(os.path.join(d, 'scored-m11-lines.jsonl.staging'))}")
print(f"   A9's arm: {a.get('reads')}; H_E's delta e {he} C; smoke named {s.get('smoke_pass_named')}; A6-5 host: {s.get('A6_5_host', {}).get('start', {}).get('read')}; "
      f"A6-3 edge {s.get('A6_3_pattern_edge', {}).get('flag')}")
h = s.get("A6_5_host", {})
dn = (h.get("end_less_start") or {}).get("nvme_temp1_mean_C")
dc = (h.get("end_less_start") or {}).get("coretemp_2_9_mean_C")
print(f"   A6-5's host windows (collected from build/e181/): NVMe composite {h.get('start', {}).get('nvme_temp1_mean_C')} -> "
      f"{h.get('end', {}).get('nvme_temp1_mean_C')} C, coretemp 2-9 {h.get('start', {}).get('coretemp_2_9_mean_C')} -> {h.get('end', {}).get('coretemp_2_9_mean_C')} C")
ok = st == [1, 2, 3, 4, 5, 6] and a.get("reads", "").startswith("SCORED") and he is not None and abs(he - 0.131) <= 0.005 and \
    not os.path.exists(os.path.join(d, "scored-m11-lines.jsonl.staging")) and j["scorer"].endswith("score_m11_v4.py") and \
    dn is not None and abs(dn - 1.0) < 1e-9 and dc is not None and abs(dc - 1.5) < 1e-9
print("E1-SCORED-CHECK " + ("PASS" if ok else "FAIL"))
PY
  cat "$S/E1-scored.txt"
  grep -q '^E1-SCORED-CHECK PASS$' "$S/E1-scored.txt" || { echo "-> FAIL (E1: the scored output's v4 checks)"; fail=1; }
else
  echo "-> FAIL (E1: no scored-m11.json)"; fail=1
fi
step "E2. the real collector v2: the measured pass's C log absent on the box"
mkbox no-measured-clog
e2e E2 14 'MISSING-CLOG p18120' s22_collect_e181_v2.sh
n=$(nscored); echo "   scored files after E2: $n"; [ "$n" -eq 0 ] || { echo "-> FAIL (E2 wrote a score)"; fail=1; }
a61box() {  # the A6-1 box as the real box leaves it: no e181/ directory, the A6-1 session log, step 10's dry smoke-gate.json in build/e181/
  mkbox f0-stopped
  rmdir "$B2/aifoundry3/aifoundry/build/claims-v3/aifoundry3/e181" 2>/dev/null
  t="$DAY 09:00:00 PST"
  printf '%s\n' "$t session start (T0 09:00:00 PST)" "$t the full design (no subset): budget 4560 s from T0" "$t frozen-e181.sha256: every file as registered" \
    "$t dmcmd_audit preflight rc=0 (dmcmd_audit: GO)" "$t config config-session-start.json: {}" "$t smoke and stop tests rc=7" \
    "$t A6-1: F0 above 53.9 C or unreadable (the smoke's floor mark): the session ends before the smoke's first launch, no hold (exit 7)" \
    "$t config config-session-end.json: {}" "$t session end" > "$B2/aifoundry3/aifoundry/build/e181/session.log"
  echo '{"dry": "step 10s V3_DRY session smoke gate"}' > "$B2/aifoundry3/aifoundry/build/e181/smoke-gate.json"
  for f in dmcmd-preflight.txt config-session-start.json config-session-end.json; do echo "{}" > "$B2/aifoundry3/aifoundry/build/e181/$f"; done
}
step "E3. FAULT 2: A6-1 as the real box leaves it (no e181/ directory, step 10's dry smoke gate in build/e181/): s22 v2"
a61box
e2e E3 16 'F0-STOPPED p18101' s22_collect_e181_v2.sh
seen=0; grep -q 'absent on the box: build/claims-v3/aifoundry3/e181/' "$S/E3.txt" && [ -f "$D2/logs/not-this-session/smoke-gate.json" ] && [ ! -e "$D2/logs/smoke-gate.json" ] \
  && [ -f "$D2/logs/config-session-start.json" ] && seen=1
n=$(nscored); echo "   absent directory named, the dry smoke gate set aside, the real config kept: $seen; scored files: $n"; ok "$seen.$n" "1.0" "E3's collection"
step "E3v1. the same box with step 22 v1 (the fault)"
a61box
e2e E3v1 14 'a copy inside collect_e181.sh failed \(rsync e181 rc=23\)' s22_collect_e181.sh
step "E4. G0-REFUSED with the real collector v2"
mkbox g0-refused
e2e E4 16 'G0-REFUSED p18120' s22_collect_e181_v2.sh
n=$(nscored); echo "   scored files after E4: $n"; [ "$n" -eq 0 ] || { echo "-> FAIL (E4 wrote a score)"; fail=1; }
loginbox() {  # a normal box, the box login recorded as s05 records it, and another login's holder line in the measured pass's run.log
  mkbox
  echo "$OWN" > "$S/out2/box-login-aifoundry3.txt"
  echo "/dev/et0_mgmt  otheruser      12345   01:02 /usr/bin/sparsity_host --test fma" >> "$B2/aifoundry3/aifoundry/build/claims-v3/aifoundry3/e181/p18120/run.log"
}
step "E5. FAULT 5: another login in a pass directory: s22 v2's scrub in every directory"
loginbox
e2e E5 16 'another login is in' s22_collect_e181_v2.sh
seen=0; grep -q 'LOGIN-LEFT aifoundry3/e181/p18120/' "$S/E5.txt" && seen=1; n=$(nscored)
echo "   the pass directory named: $seen; scored files: $n"; ok "$seen.$n" "1.0" "E5's scrub"
step "E5v1. the same with step 22 v1 (it reads logs/ only, and scores: the fault)"
loginbox
e2e E5v1 0 'E181 collected and scored' s22_collect_e181.sh
rm -f "$S/out2/box-login-aifoundry3.txt"
liebox() {  # a normal box whose start_gate mark lies: passed true with numbers that refuse (the residue excess over 0.50 C)
  mkbox
  /usr/bin/python3 -B - "$B2/aifoundry3/aifoundry/build/claims-v3/aifoundry3/e181/p18120/marks.jsonl" <<'PY'
import json, sys
p = sys.argv[1]
ms = [json.loads(x) for x in open(p) if x.strip()]
for m in ms:
    if m.get("kind") == "start_gate":
        m["floor_c"] = m["room_c"] - 0.414 - 0.6
        m["residue_c"] = m["room_c"] - m["floor_c"]
        m["residue_excess_c"] = m["residue_c"] - 0.414
        m["passed"] = True
with open(p, "w") as f:
    for m in ms:
        f.write(json.dumps(m) + "\n")
PY
}
step "E6. FAULT 4: a start_gate mark that lies reaches the score: v4 refuses before any file"
liebox
e2e E6 14 "scorer did not read rc 0.*scored files left: none" s22_collect_e181_v2.sh
n=$(nscored); echo "   scored files after E6: $n"; ok "$n" 0 "E6: no scored file left"
step "E6v1. the same with step 22 v1 and M11's scorer v3 (the fault: the lines file left behind)"
liebox
e2e E6v1 14 "scorer did not read rc 0" s22_collect_e181.sh
seen=0; [ -f "$D2/scored-m11-lines.jsonl" ] && seen=1; echo "   scored-m11-lines.jsonl left by v3: $seen"; ok "$seen" 1 "E6v1: v3 left the lines file (the fault)"
rm -rf "${D2:?}"

step "O1. ours_live's pattern names E181's, E178's and E180's processes (and q143k's and k6's), and none of the note's new names"
pat=$(grep -o "pgrep -u \"\$(id -u)\" -f '[^']*'" "$SRC/tools/claims-v3/e181/rb/rb_common_e181.sh" | sed -E "s/^pgrep -u \"\\\$\(id -u\)\" -f '//; s/'$//")
hits=0
for c in "bash tools/claims-v3/e181/session_e181.sh" "bash tools/claims-v3/e181/block_e181.sh 18120" "python3 tools/claims-v3/e181/run_e181.py build/x" \
         "bash tools/claims-v3/e178/session_e178.sh" "bash tools/claims-v3/e178/queue_e178.sh" "bash tools/claims-v3/e178/block_e178.sh 17810" \
         "python3 tools/claims-v3/e178/run_e178.py x" "bash tools/claims-v3/e180/session_e180.sh" "bash tools/claims-v3/e180/block_e180.sh 1" \
         "python3 tools/claims-v3/e180/run_e180.py x" "bash tools/claims-v3/e176/session_e176.sh" "python3 tools/claims-v3/e176/run_e176.py y" \
         "bash tools/claims-v3/e171/session_e171.sh" "python3 tools/claims-v3/e174/queue_e174.py"; do
  printf '%s\n' "$c" | grep -qE "$pat" && hits=$((hits + 1))
done
miss=0
for c in "vim notes.txt" "bash tools/claims-v3/e181/rb/s11_a3_launch_e181.sh" "bash tools/claims-v3/e181/rb/selftest_rb_e181.sh" "python3 tools/claims-v3/e181/dry_intel_e181.sh" \
         "bash tools/claims-v3/e181/rb/s11_a3_launch_e181_v2.sh" "bash tools/claims-v3/e181/rb/s12_a3_host_e181.sh start" "bash tools/claims-v3/e181/rb/s22_collect_e181_v2.sh" \
         "bash tools/claims-v3/e181/rb/selftest_rb_e181_v2.sh x" "python3 -B tools/claims-v3/e181/rb/scrub_all_e181.py d" "bash tools/claims-v3/e181/collect_e181_v2.sh d" \
         "bash tools/claims-v3/e181/score_e181_v2.sh d" "python3 -B tools/claims-v3/m11/score_m11_v4.py score"; do
  printf '%s\n' "$c" | grep -qE "$pat" && miss=$((miss + 1))
done
echo "named: $hits of 14; unrelated commands matched: $miss of 12"
ok "$hits.$miss" "14.0" "ours_live's names"

echo
echo "network calls by the stand-ins: to the stand-in boxes only; elapsed $(( $(date +%s) - t_begin )) s"
echo "SELFTEST-RB-E181-V2 $([ "$fail" -eq 0 ] && echo PASS || echo FAIL)"
exit "$fail"
