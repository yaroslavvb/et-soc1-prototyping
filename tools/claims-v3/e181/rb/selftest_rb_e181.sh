#!/usr/bin/env bash
# E181 (M11's session 2): the desk test of E181's runbook, in the form of ../../q143k-runbook/selftest_runbook_q143k.sh and _v2.sh (92a1b27f,
# 6b013ad9, which stay as committed). Stand-in ssh and rsync sit first on PATH and serve a stand-in box (a local directory laid out like
# aifoundry3's ~/aifoundry); no lab box is reached. A date shim runs GNU date. Every tree is a scratch copy under <scratch dir>, never the
# lab clone. The cases:
#   A    the dry listing: every step exits 0, no ssh or rsync call;
#   P1   a file the runbook pins (v3.1's rb_run.py) changed: 16, before any call;
#   L1   a login link at the probe: 11 and one lock line;  L2  a probe that never answers: 12;  L3  a read past its bound: 13;
#   L4   a box whose box list reads 27 of 30 (its three binaries missing): 16;
#   W1   the session log ends after the offset: 0;  W2  no session process and no end: 14;  W3  the smoke or its gate failed: 16;
#   W4   G0-A6 with A8-4 refused the measured pass: 16, G0-REFUSED;  W5  A6-1 ended the session before the smoke's first launch: 16;
#   S1   fewer than 76 minutes before the last end: 16, before any box call;
#   S2   an earlier E181 smoke on the box without --later-try: 10;
#   S3   E176's real session ended 10 minutes ago: 10 (the runbook's 40-minute gate);
#   S4   THE NOTE-2 DEFECT: a dry session's end 10 minutes ago (in E176's style, inside build/e176/session.log after a real end 3 h ago, and
#        in build/e181/session-dry.log): the rest rule skips both and launches (0, "rest: 180 minutes");
#   S5   a real session end 50 minutes ago: 10 without --under-an-hour (A7-4's hour), 0 with it (the departure logged);
#   S6   at 12:05 PST (the desk test's clock): 10 without --after-noon (A6/A7's cool-hour plan), and past that check with it;
#   C1-C7 v1's collection cases with a stand-in collector and scorer (good 0; check crashed 14; failed copy 14; scorer not rc 0 14; stale
#        check 14; desk path in a scored file 16; stand-ins without RB_DESKTEST=1 10);
#   C8-C16 v2's launch-gate cases (MISSING-CLOG p18120, COUNT-SHORT, MISSING-CLOG p18101, NOT-REQUIRED, ORPHAN, NO-LAUNCH, an empty C log,
#        COUNT-UNREAD; a listed file that differs: 16 before any box call);
#   C17  G0-REFUSED: 16, and no scored file written;  C18  F0-STOPPED (A6-1): 16, and no scored file written;
#   C19  THE FAULT-2 FIX: a gate stops the step (COUNT-SHORT) and no scored file exists in the data directory (the scorer never ran);
#   C20  duplicate t_start_ms in the measured pass: 14, COUNT-DUP;
#   U1   E166's committed session renamed to E181's passes: COUNT-OK 6,644 / 493 and 48 / 6;  U2  E154's: COUNT-OK 6,288 / 474 and 58 / 7;
#   E1   the real collector and M11's scorer v3 end to end, on a stand-in box holding E154's committed passes (holds renamed to M11's, an
#        A6-1 floor mark and an A6-2-with-A8-4 start gate added): 0, "E181 collected and scored", the scorer's three stages and FL5(c);
#   E2   the same with the measured pass's C log absent on the box: 14, MISSING-CLOG p18120, and no scored file;
#   O1   ours_live names E181's, E178's and E180's processes (and q143k's and k6's), and not an unrelated command.
#
#   bash tools/claims-v3/e181/rb/selftest_rb_e181.sh <scratch dir> > <log>
# SPDX-License-Identifier: Apache-2.0
set -u
SRC=$(cd "$(dirname "${BASH_SOURCE[0]}")/../../../.." && pwd)
S=${1:?a scratch directory outside the repository}
case "$S" in "$SRC"|"$SRC"/*) echo "the scratch directory must be outside the repository"; exit 2 ;; esac
mkdir -p "$S"
S=$(cd "$S" && pwd -P)
rm -rf "${S:?}/tree" "${S:?}/tree2" "${S:?}/box" "${S:?}/box2" "${S:?}/bin" "${S:?}/out" "${S:?}/out2" "${S:?}/dry-out" "${S:?}/u" "${S:?}/cache"
DATA=$SRC/tools/claims-v3/e181/rb/selftest_data_e181.py
E166=$SRC/docs/reports/data/2026-11-04-e166-heat-replicate-aifoundry3
E154=$SRC/docs/reports/data/2026-11-03-e154-heat-e2e-aifoundry3
fail=0
ok() { if [ "$1" = "$2" ]; then echo "-> PASS ($3)"; else echo "-> FAIL ($3: rc $1, want $2)"; fail=1; fi; }
step() { echo; echo "== $*"; }
show() { grep -m2 -E "$2|STOP" "$1" | sed "s#$S#<scratch>#g" | cut -c1-240; }
t_begin=$(date +%s)

# ---- the scratch tree: the runbook, the kit, v3.1's runner and gates, E164's scrub, the lists step 22 checks first
T=$S/tree; B=$S/box; BIN=$S/bin
mkdir -p "$T/tools/claims-v3" "$B/aifoundry3/aifoundry" "$BIN" "$S/out"
for p in e181 e181/rb q141k-runbook/v3.1; do mkdir -p "$T/tools/claims-v3/$p"; cp -p "$SRC/tools/claims-v3/$p"/*.* "$T/tools/claims-v3/$p/" 2>/dev/null; done
mkdir -p "$T/tools/claims-v3/e164" "$T/tools/claims-v3/m11"; cp -p "$SRC/tools/claims-v3/e164/scrub_etwho_e164.py" "$T/tools/claims-v3/e164/"
cp -p "$SRC/tools/claims-v3/m11/score_m11_v3.py" "$T/tools/claims-v3/m11/"
mklist() {  # mklist <tree>: the three lists step 22 checks first, over that tree's own copies (the committed lists also pin logs and notes)
  ( cd "$1" && shasum -a 256 tools/claims-v3/m11/score_m11_v3.py > tools/claims-v3/m11/SHA256SUMS-score-m11-v3 &&
    shasum -a 256 tools/claims-v3/e181/*.sh tools/claims-v3/e181/*.py > tools/claims-v3/e181/kit-e181.sha256 &&
    shasum -a 256 tools/claims-v3/e181/rb/*.sh tools/claims-v3/e181/rb/*.py > tools/claims-v3/e181/rb/SHA256SUMS-rb-e181 )
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

step "A. the dry listing: every step exits 0, no ssh or rsync call"
: > "$S/calls.log"
bash "$R/list_steps_e181.sh" "$S/dry-out" > "$S/dry-listing.txt" 2>&1; rc=$?
n=$(grep -c . "$S/calls.log"); tail -n 1 "$S/dry-listing.txt"; echo "calls: $n"
ok "$rc.$n" "0.0" "dry listing"

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

step "S1. fewer than 76 minutes before the last end"
le=$(date -d '+60 min' '+%H:%M'); lsx=$(date -d '+30 min' '+%H:%M')
if [ "$(date -d '+60 min' +%F)" = "$(date +%F)" ] && [ "$(date -d '+30 min' +%F)" = "$(date +%F)" ]; then
  bash "$R/s02_window_e181.sh" "$(date +%F)" "$lsx" "$le" > "$S/s1w.txt" 2>&1
  : > "$S/calls.log"
  RB_DESKTEST=1 RB_NOW_HM=0900 bash "$R/s11_a3_launch_e181.sh" > "$S/s1.txt" 2>&1; rc=$?
  n=$(grep -c . "$S/calls.log"); show "$S/s1.txt" STOP; ok "$rc.$n" "16.0" "exit 16, no box call"
else
  echo "(skipped: the test runs within an hour of midnight)"
fi
bash "$R/s02_window_e181.sh" "$(date +%F)" 23:58 23:59 > "$S/window.txt" 2>&1
mkdir -p "$A3/build/q141k/jobs"; echo 0 > "$A3/build/q141k/jobs/a3-dry-e181.rc"; echo 1 > "$A3/build/q141k/jobs/a3-dry-e181.pid"
rm -f "$A3/build/e181/session.log" "$A3/build/e181/session-dry.log"
launch() {  # launch <case> [s11 options]: the step at 09:00 by the desk test's clock
  local c=$1; shift
  rm -rf "${A3:?}/build/claims-v3/aifoundry3/e181-smoke"
  RB_DESKTEST=1 RB_NOW_HM=${NOW_HM:-0900} bash "$R/s11_a3_launch_e181.sh" "$@" > "$S/$c.txt" 2>&1
}
step "S2. an earlier E181 smoke on the box, without --later-try"
rm -rf "${A3:?}/build/claims-v3/aifoundry3/e181-smoke"; mkdir -p "$A3/build/claims-v3/aifoundry3/e181-smoke/p18101"
RB_DESKTEST=1 RB_NOW_HM=0900 bash "$R/s11_a3_launch_e181.sh" > "$S/s2.txt" 2>&1; rc=$?
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

# ---- the collection (step 22) with stand-in collector and scorer (selftest_data_e181.py synth, MODE names the fault)
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
  MODE=$mode RB_DESKTEST=1 E181_COLLECT="$S/collect_stub.sh" E181_SCORE="$S/score_stub.sh" bash "$R/s22_collect_e181.sh" > "$S/$c.txt" 2>&1; rc=$?
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
step "C3. a failed copy inside the collector"; cn C3 14 'a copy inside collect_e181.sh failed' copy; noscore C3
step "C4. the scorer not rc 0"; cn C4 14 "scorer did not read rc 0" score
step "C5. a check file from an earlier try (backdated)"; cn C5 14 'CCHECK-STALE' stale; noscore C5
step "C6. a desk path in a scored file"; cn C6 16 'HIT ' path
step "C7. the stand-ins named without RB_DESKTEST=1"
E181_COLLECT="$S/collect_stub.sh" bash "$R/s22_collect_e181.sh" > "$S/C7.txt" 2>&1; rc=$?
grep -m1 STOP "$S/C7.txt" | cut -c1-200; ok "$rc" 10 "exit 10"
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
RB_DESKTEST=1 E181_COLLECT="$S/collect_stub.sh" E181_SCORE="$S/score_stub.sh" bash "$R/s22_collect_e181.sh" > "$S/C16.txt" 2>&1; rc=$?
n=$(grep -c . "$S/calls.log"); grep -m1 STOP "$S/C16.txt" | sed "s#$S#<scratch>#g" | cut -c1-220
seen=0; grep -q 'STOP: a file of tools/claims-v3/e181/rb/SHA256SUMS-rb-e181 differs' "$S/C16.txt" && seen=1
cp -p "$S/cclaunch.keep" "$R/cclaunch_e181.py"
ok "$rc.$n.$seen" "16.0.1" "exit 16, no box call, the list named"
step "C17. G0-REFUSED: the measured pass's start gate refused"; cn C17 16 'G0-REFUSED p18120' g0; noscore C17
step "C18. F0-STOPPED: A6-1 ended the session before the smoke's first launch"; cn C18 16 'F0-STOPPED p18101' f0; noscore C18
step "C19. the fault-2 fix: a gate stops the step (COUNT-SHORT) before the scorer, so no scored file exists"; cn C19 14 'COUNT-SHORT p18120' short; noscore C19
step "C20. duplicate t_start_ms in the measured pass's launch marks"; cn C20 14 'COUNT-DUP p18120' dup; noscore C20
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

# ---- the real collector and M11's scorer v3, end to end, on a stand-in box with E154's committed passes
T2=$S/tree2; B2=$S/box2
mkdir -p "$T2/docs/reports/data" "$S/out2" "$S/cache"
git -C "$SRC" archive HEAD tools workloads rtl-sim/fma_toggle_v2 | tar -x -C "$T2"
for p in e181 e181/rb m11; do mkdir -p "$T2/tools/claims-v3/$p"; cp -p "$SRC/tools/claims-v3/$p"/*.* "$T2/tools/claims-v3/$p/" 2>/dev/null; done
mklist "$T2"
for d in "$SRC"/docs/reports/data/*; do ln -s "$d" "$T2/docs/reports/data/$(basename "$d")"; done
DAY=$(date +%F)
D2=$T2/docs/reports/data/$DAY-e181-m11-session2-aifoundry3
[ -e "$D2" ] && { echo "refused: $D2 exists (a link to the lab clone's data?)"; exit 2; }
e2e() {  # e2e <case> <want rc> <want line> [fault ...]
  local c=$1 want=$2 line=$3; shift 3
  rm -rf "${D2:?}" "${B2:?}"
  /usr/bin/python3 -B "$DATA" box "$E154" aifoundry3/e154-smoke/p15401 aifoundry3/e154/p15420 "$B2" "$@" | sed "s#$S#<scratch>#g"
  : > "$S/calls.log"
  ( export RB_REPO="$T2" RB_OUT="$S/out2" RB_LOCK="$S/lock2.txt" Q_BOX="$B2" CCHECK_CACHE="$S/cache"
    unset RB_DESKTEST E181_COLLECT E181_SCORE
    cd "$T2" && bash tools/claims-v3/e181/rb/s02_window_e181.sh "$DAY" 23:58 23:59 > /dev/null 2>&1
    cd "$T2" && bash tools/claims-v3/e181/rb/s22_collect_e181.sh ) > "$S/$c.txt" 2>&1; local rc=$?
  grep -E "$line|STOP|COUNT-|MISSING-|GATES-|CCHECK-DONE|score rc|ccheck rc" "$S/$c.txt" | sed "s#$S#<scratch>#g" | cut -c1-240 | head -n 9
  local seen=0; grep -qE "$line" "$S/$c.txt" && seen=1
  echo "stand-in calls: $(grep -c '^rsync' "$S/calls.log") rsync, $(grep -c '^ssh' "$S/calls.log") ssh (the stand-in box only)"
  ok "$rc.$seen" "$want.1" "$c"
}
step "E1. the real collector and M11's scorer v3: both C logs on the box"
e2e E1 0 'E181 collected and scored'
if [ -f "$D2/scored-m11.json" ]; then
  /usr/bin/python3 -B - "$D2" <<'PY'
import json, os, sys
d = sys.argv[1]
j = json.load(open(os.path.join(d, "scored-m11.json")))
st = [json.loads(x)["stage"] for x in open(os.path.join(d, "scored-m11-lines.jsonl")) if x.strip()]
ss = list(j["sessions"].values())
e176, s = ss[0], ss[-1]
f = s.get("FL5c", {}).get("primary", {})
print(f"   scored-m11.json: scorer {j['scorer']}; E176 excluded: {e176.get('excluded')}; holds scored {sum(1 for h in s['holds'].values() if h.get('scored'))} of 5; "
      f"start gate {s['start_gate_reading']['form']} passed {s['start_gate_reading']['passed']}; FL5(c) {f.get('verdict')} (diff {f.get('diff_w_per_c')}); "
      f"HM-LG {j['aifoundry3']['HM_LG']['verdict']}; label {j['label'][:9]}; lines file stages {st}")
PY
fi
step "E2. the real collector: the measured pass's C log absent on the box"
e2e E2 14 'MISSING-CLOG p18120' no-measured-clog
n=$(ls "$D2"/scored-m11* 2>/dev/null | wc -l | tr -d ' '); echo "   scored files after E2: $n"; [ "$n" -eq 0 ] || { echo "-> FAIL (E2 wrote a score)"; fail=1; }
rm -rf "${D2:?}"

step "O1. ours_live's pattern names E181's, E178's and E180's processes (and q143k's and k6's), and not an unrelated command"
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
for c in "vim notes.txt" "bash tools/claims-v3/e181/rb/s11_a3_launch_e181.sh" "bash tools/claims-v3/e181/rb/selftest_rb_e181.sh" "python3 tools/claims-v3/e181/dry_intel_e181.sh"; do
  printf '%s\n' "$c" | grep -qE "$pat" && miss=$((miss + 1))
done
echo "named: $hits of 14; unrelated commands matched: $miss of 4"
ok "$hits.$miss" "14.0" "ours_live's names"

echo
echo "network calls by the stand-ins: to the stand-in boxes only; elapsed $(( $(date +%s) - t_begin )) s"
echo "SELFTEST-RB-E181 $([ "$fail" -eq 0 ] && echo PASS || echo FAIL)"
exit "$fail"
