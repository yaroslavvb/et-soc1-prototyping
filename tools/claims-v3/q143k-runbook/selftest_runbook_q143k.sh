#!/usr/bin/env bash
# Q143(k): the desk test of the runbook for M11's E176 session. Stand-in ssh and rsync sit first on PATH and serve a stand-in box (a local
# directory laid out like aifoundry3's ~/aifoundry); no lab box is reached. A date shim runs GNU date (the box's). Everything runs in a
# scratch copy of the runbook's files under <scratch dir> (never the lab clone): RB_REPO points there. The cases:
#   A   the dry listing: every step exits 0 and no ssh or rsync call is made;
#   L1  a login link printed at the probe: exit 11 and "<HH:MM:SS> aifoundry3 needs a check" appended to the lock file;
#   L2  a probe that never answers (RB_PROBE_S=2): exit 12;
#   L3  a read past its bound (RB_READ_S=2): exit 13;
#   L4  a box whose preflight reads wrong (its binaries missing: the box list 26 of 29): exit 16;
#   W1  the session log ends after the runbook's offset: exit 0;  W2  no session process and no end: exit 14 (RUN-GONE);
#   W3  the smoke or its gate failed: exit 16 (GATE-STOPPED);  W4  the start gate refused the measured pass: exit 16 (G0-REFUSED);
#   S1  fewer than 76 minutes before the last end: exit 16, before any box call;
#   S2  an earlier E176 smoke on the box without --later-try: exit 10 (REFUSED);  S3  E171's session ended 10 minutes ago: exit 10;
#   C1  s22 with a stand-in collector whose check of C finished: exit 0, "E176 collected and scored";
#   C2  no check file (the check crashed): 14;  C3  a failed copy inside the collector: 14;  C4  the scorer not rc 0: 14;
#   C5  a check file from an earlier try (backdated): 14;  C6  a desk path in what the collector wrote: 16;
#   C7  the stand-in named without RB_DESKTEST=1: 10;
#   O1  ours_live's pattern counts E176's session, block and runner and E177's queue, runner and session (and k6's names), and not an
#       unrelated command.
#
#   bash tools/claims-v3/q143k-runbook/selftest_runbook_q143k.sh <scratch dir> > <log>
# SPDX-License-Identifier: Apache-2.0
set -u
SRC=$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)
S=${1:?a scratch directory outside the repository}
case "$S" in "$SRC"|"$SRC"/*) echo "the scratch directory must be outside the repository"; exit 2 ;; esac
rm -rf "${S:?}/tree" "${S:?}/box" "${S:?}/bin" "${S:?}/out" "${S:?}/dry-out"
T=$S/tree; B=$S/box; BIN=$S/bin
mkdir -p "$T/tools/claims-v3" "$B/aifoundry3/aifoundry" "$BIN" "$S/out"
for p in q143k-runbook q141k-runbook/v3.1 e176; do mkdir -p "$T/tools/claims-v3/$p"; cp -p "$SRC/tools/claims-v3/$p"/*.* "$T/tools/claims-v3/$p/" 2>/dev/null; done
mkdir -p "$T/tools/claims-v3/e164"; cp -p "$SRC/tools/claims-v3/e164/scrub_etwho_e164.py" "$T/tools/claims-v3/e164/"
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
  case "\${Q_PROBE:-answer}" in link) echo "To authenticate, visit: https://login.tail""scale.com/a/q143kselftest01" >&2; sleep 30; exit 1 ;; hang) sleep 60; exit 0 ;; *) exit 0 ;; esac
fi
case "\${Q_SSH:-answer}" in hang) sleep 60; exit 0 ;; fail) exit 1 ;; esac
HOME="$B/\$host" bash -c "cd ~ && \$cmd"
EOF
cat > "$BIN/rsync" <<EOF
#!/bin/bash
echo "rsync \$*" >> "$S/calls.log"
a=()
while [ \$# -gt 0 ]; do case "\$1" in -e) shift 2 ;; *:*) h=\${1%%:*}; p=\${1#*:}; a+=("$B/\$h/\$p"); shift ;; *) a+=("\$1"); shift ;; esac; done
exec "$REAL_RSYNC" "\${a[@]}"
EOF
chmod +x "$BIN/ssh" "$BIN/rsync" "$BIN/date"
export PATH="$BIN:$PATH" RB_REPO="$T" RB_OUT="$S/out" RB_LOCK="$S/lock.txt"
: > "$S/calls.log"; : > "$RB_LOCK"
R=$T/tools/claims-v3/q143k-runbook
A3=$B/aifoundry3/aifoundry
fail=0
ok() { if [ "$1" = "$2" ]; then echo "-> PASS ($3)"; else echo "-> FAIL ($3: rc $1, want $2)"; fail=1; fi; }
step() { echo; echo "== $*"; }
show() { grep -m2 -E "$2|STOP" "$1" | sed "s#$S#<scratch>#g" | cut -c1-230; }
cd "$T" || exit 2

step "A. the dry listing: every step exits 0, no ssh or rsync call"
: > "$S/calls.log"
bash "$R/list_steps_q143k.sh" "$S/dry-out" > "$S/dry-listing.txt" 2>&1; rc=$?
n=$(grep -c . "$S/calls.log"); tail -n 1 "$S/dry-listing.txt"; echo "calls: $n"
ok "$rc.$n" "0.0" "dry listing"

step "L1. a login link at the probe"
Q_PROBE=link bash "$R/s08_a3_preflight_q143k.sh" > "$S/l1.txt" 2>&1; rc=$?
show "$S/l1.txt" STOP; tail -n 1 "$RB_LOCK" | sed -E 's/^[0-9:]+/<HH:MM:SS>/'
lk=$(grep -cE '^[0-9]{2}:[0-9]{2}:[0-9]{2} aifoundry3 needs a check$' "$RB_LOCK")
ok "$rc.$lk" "11.1" "exit 11 and one lock line"

step "L2. a probe that never answers (bound 2 s)"
RB_PROBE_S=2 Q_PROBE=hang bash "$R/s08_a3_preflight_q143k.sh" > "$S/l2.txt" 2>&1; rc=$?
show "$S/l2.txt" STOP; ok "$rc" 12 "exit 12"

step "L3. a read past its bound (2 s)"
RB_READ_S=2 Q_SSH=hang bash "$R/s08_a3_preflight_q143k.sh" > "$S/l3.txt" 2>&1; rc=$?
show "$S/l3.txt" STOP; ok "$rc" 13 "exit 13"

step "L4. a box whose preflight reads wrong (its three binaries missing: the box list reads 26 of 29)"
mkdir -p "$A3/tools/claims-v3/e176"
( cd "$SRC" && tar -cf - $(awk '{print $2}' tools/claims-v3/e176/frozen-e176.sha256 | grep -v '^build/') tools/claims-v3/e176/frozen-e176.sha256 ) | tar -xf - -C "$A3"
printf 'echo "dmcmd_audit: GO (38 send site(s), 0 disallowed; allow-list: none)"\n' > "$A3/tools/claims-v3/e176/preflight_e176.sh"
bash "$R/s08_a3_preflight_q143k.sh" > "$S/l4.txt" 2>&1; rc=$?
show "$S/l4.txt" STOP; ok "$rc" 16 "exit 16"

# the wait: the runbook's offset, then the session log's lines after it
mklog() {  # mklog <line> ...: a fresh offset of 2 and a session log of two older lines and the given ones
  mkdir -p "$A3/build/q141k" "$A3/build/e176"
  echo 2 > "$A3/build/q141k/e176.log-offset"
  { echo "2026-11-04 10:00:00 PST session start (an earlier day's)"; echo "2026-11-04 11:15:00 PST session end"; printf '%s\n' "$@"; } > "$A3/build/e176/session.log"
}
step "W1. the session log ends after the offset"
mklog "$(date '+%F %T %Z') session start" "$(date '+%F %T %Z') pass 17620 rc=0" "$(date '+%F %T %Z') session end"
RB_WAIT_LOOP_S=5 bash "$R/s20_wait_q143k.sh" > "$S/w1.txt" 2>&1; rc=$?
show "$S/w1.txt" 'has ended'; ok "$rc" 0 "exit 0"
step "W2. no session process and no session end"
mklog "$(date '+%F %T %Z') session start"
RB_WAIT_LOOP_S=5 bash "$R/s20_wait_q143k.sh" > "$S/w2.txt" 2>&1; rc=$?
show "$S/w2.txt" 'RUN-GONE'; ok "$rc" 14 "exit 14"
step "W3. the smoke or its gate failed"
mklog "$(date '+%F %T %Z') session start" "$(date '+%F %T %Z') the smoke or its gate failed: no measured pass" "$(date '+%F %T %Z') session end"
RB_WAIT_LOOP_S=5 bash "$R/s20_wait_q143k.sh" > "$S/w3.txt" 2>&1; rc=$?
show "$S/w3.txt" 'GATE-STOPPED|ended at a gate'; ok "$rc" 16 "exit 16"
step "W4. the start gate refused the measured pass"
mklog "$(date '+%F %T %Z') session start" "$(date '+%F %T %Z') pass 17620 rc=7: the start gate (R0's room above 53.0 C): no hold ran, E176 not started" "$(date '+%F %T %Z') session end"
RB_WAIT_LOOP_S=5 bash "$R/s20_wait_q143k.sh" > "$S/w4.txt" 2>&1; rc=$?
show "$S/w4.txt" "start gate refused"; ok "$rc" 16 "exit 16"

step "S1. fewer than 76 minutes before the last end"
le=$(date -d '+60 min' '+%H:%M'); lsx=$(date -d '+30 min' '+%H:%M')
if [ "$(date -d '+60 min' +%F)" = "$(date +%F)" ] && [ "$(date -d '+30 min' +%F)" = "$(date +%F)" ]; then
  bash "$R/s02_window_q143k.sh" "$(date +%F)" "$lsx" "$le" > "$S/s1w.txt" 2>&1
  : > "$S/calls.log"
  bash "$R/s11_a3_session_q143k.sh" > "$S/s1.txt" 2>&1; rc=$?
  n=$(grep -c . "$S/calls.log"); show "$S/s1.txt" STOP; ok "$rc.$n" "16.0" "exit 16, no box call"
else
  echo "(skipped: the test runs within an hour of midnight)"
fi
# a window that fits, for S2, S3 and the collections
bash "$R/s02_window_q143k.sh" "$(date +%F)" 23:58 23:59 > "$S/window.txt" 2>&1
mkdir -p "$A3/build/q141k/jobs"; echo 0 > "$A3/build/q141k/jobs/a3-dry-e176.rc"; echo 1 > "$A3/build/q141k/jobs/a3-dry-e176.pid"
rm -f "$A3/build/e176/session.log"          # the wait cases' log: E176's own session end must not decide S2 or S3
step "S2. an earlier E176 smoke on the box, without --later-try"
mkdir -p "$A3/build/claims-v3/aifoundry3/e176-smoke/p17601"
bash "$R/s11_a3_session_q143k.sh" > "$S/s2.txt" 2>&1; rc=$?
show "$S/s2.txt" 'REFUSED'; seen=0; grep -q 'STOP: e176 refused on the box: REFUSED: an earlier E176 smoke' "$S/s2.txt" && seen=1
ok "$rc.$seen" "10.1" "exit 10, the earlier smoke named"
rm -rf "${A3:?}/build/claims-v3/aifoundry3/e176-smoke"
step "S3. E171's session ended 10 minutes ago (the card has not rested)"
mkdir -p "$A3/build/e171"; echo "$(date -d '10 min ago' '+%F %T %Z') session end" > "$A3/build/e171/session.log"
bash "$R/s11_a3_session_q143k.sh" > "$S/s3.txt" 2>&1; rc=$?
show "$S/s3.txt" 'REFUSED'; seen=0; grep -qE "STOP: e176 refused on the box: REFUSED: (9|10|11) minutes since E171's session end" "$S/s3.txt" && seen=1
ok "$rc.$seen" "10.1" "exit 10, E171's session end named"
rm -rf "${A3:?}/build/e171"

# the collection: a stand-in collector that writes what collect_e176.sh writes (MODE=crash|copy|score|stale|path change it)
cat > "$S/collect_stub.sh" <<'EOF'
#!/bin/bash
D=$1
mkdir -p "$D/ccheck" "$D/logs" "$D/aifoundry3/e176/p17620"
[ "${MODE:-}" = copy ] && echo "rsync e176 rc=23"
if [ "${MODE:-}" != crash ]; then
  python3 -B - "$D/ccheck/ccheck-all.json" <<'PY'
import json, sys
L = [{"log": "c-log-p17620.jsonl", "t_start_ms": 1793900000000 + i, "t_end_ms": 1793900000005 + i, "verdict": "PASS", "type": "fp32"} for i in range(5)]
json.dump({"summary": {"launches": len(L), "PASS": len(L), "ROUNDING": 0, "UNMODELLED": 0, "FAIL": 0, "all_pass": True}, "launches": L},
          open(sys.argv[1], "w"))
PY
  echo "ccheck rc=0 (5 launches)"
fi
[ "${MODE:-}" = stale ] && touch -t 202611050001 "$D/ccheck/ccheck-all.json"
echo "# M11 on aifoundry3 (stand-in)" > "$D/scored-m11.md"; echo '{}' > "$D/scored-m11.json"
[ "${MODE:-}" = path ] && echo "a desk path: $PWD/build/e176" >> "$D/scored-m11.md"
if [ "${MODE:-}" = score ]; then echo "score rc=1"; else echo "score rc=0"; fi
EOF
chmod +x "$S/collect_stub.sh"
cn() {  # cn <case> <want rc> <want line> <mode>
  local c=$1 want=$2 line=$3 mode=$4
  rm -rf "${T:?}/docs"
  MODE=$mode RB_DESKTEST=1 Q143K_COLLECT_E176="$S/collect_stub.sh" bash "$R/s22_collect_q143k.sh" > "$S/$c.txt" 2>&1; rc=$?
  grep -E "$line|STOP" "$S/$c.txt" | head -n 3 | sed "s#$S#<scratch>#g" | cut -c1-230
  local seen=0; grep -qE "$line" "$S/$c.txt" && seen=1
  ok "$rc.$seen" "$want.1" "$c"
}
step "C1. a good collection (the check of C finished, the scorer rc 0)"
cn C1 0 'E176 collected and scored' ""
step "C2. no check file (the check of C crashed)"
cn C2 14 'CCHECK-MISSING' crash
step "C3. a failed copy inside the collector"
cn C3 14 'a copy inside collect_e176.sh failed' copy
step "C4. the scorer not rc 0"
cn C4 14 "scorer did not read rc 0" score
step "C5. a check file from an earlier try (backdated)"
cn C5 14 'CCHECK-STALE' stale
step "C6. a desk path in what the collector wrote"
cn C6 16 'HIT ' path
step "C7. the stand-in named without RB_DESKTEST=1"
Q143K_COLLECT_E176="$S/collect_stub.sh" bash "$R/s22_collect_q143k.sh" > "$S/c7.txt" 2>&1; rc=$?
show "$S/c7.txt" STOP; ok "$rc" 10 "exit 10"

step "O1. ours_live's pattern names E176's and E177's processes (and k6's), and not an unrelated command"
pat=$(grep -o "pgrep -u \"\$(id -u)\" -f '[^']*'" "$R/rb_common.sh" | sed -E "s/^pgrep -u \"\\\$\(id -u\)\" -f '//; s/'$//")
hits=0
for c in "bash tools/claims-v3/e176/session_e176.sh" "bash tools/claims-v3/e176/block_e176.sh 17620" "python3 tools/claims-v3/e176/run_e176.py build/x" \
         "python3 tools/claims-v3/e177/queue_e177.py" "python3 tools/claims-v3/e177/run_e177.py" "bash tools/claims-v3/e177/run_e177.sh" \
         "bash tools/claims-v3/e177/session_e177.sh" "bash tools/claims-v3/e171/session_e171.sh" "python3 tools/claims-v3/e173/queue_e173.py" \
         "python3 tools/claims-v3/e174/queue_e174.py"; do
  printf '%s\n' "$c" | grep -qE "$pat" && hits=$((hits + 1))
done
miss=0
for c in "vim notes.txt" "bash tools/claims-v3/q143k-runbook/s11_a3_session_q143k.sh" "bash tools/claims-v3/q143k-runbook/selftest_runbook_q143k.sh"; do
  printf '%s\n' "$c" | grep -qE "$pat" && miss=$((miss + 1))
done
echo "named: $hits of 10; unrelated commands matched: $miss of 3"
ok "$hits.$miss" "10.0" "ours_live's names"

echo
echo "network calls by the stand-ins in the non-dry cases: $(grep -c . "$S/calls.log") (to the stand-in box only)"
echo "SELFTEST-RUNBOOK-Q143K $([ "$fail" -eq 0 ] && echo PASS || echo FAIL)"
exit "$fail"
