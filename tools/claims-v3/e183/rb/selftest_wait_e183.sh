#!/usr/bin/env bash
# E183 (the kit's dated note 6, KIT.md.dated-note-6.md, Fri 13 Nov 2026, before any E183 train datum): the desk test of step 10 v2
# (rb/s20_wait_e183_v2.sh), with step 10 v1 (rb/s20_wait_e183.sh) as its negative control. On aifoundry3 on Fri 13 Nov 2026 step 10 v1 read
# RUN-GONE (14) while session_e183_v2.sh ran its smoke: its pgrep pattern, "session_e183\.sh", matches no later version. No desk test of
# the kit had run step 10. Here each step runs whole (rb_init, the probe, one bounded remote wait through k6's rb_run.py) against a
# stand-in aifoundry3: a FAKE ssh that runs the remote script with `bash -s` in a local directory laid out as the box's ~/aifoundry (the
# day's T0 file and that T0's session log), and refuses any other host or command. The box's pgrep is the real one, so the test runs in a
# private PID namespace of its own (bubblewrap, re-executing itself; no /dev/et*, refused if one is visible): the only processes it can see
# are its own stand-in "sessions", small shell scripts named as each form, started with setsid -f and stopped with a plain kill.
#   W0  v1 with session_e183_v2.sh running and no session end: RUN-GONE, 14 (the false reading of Fri 13 Nov 2026, at the desk);
#   W1  v2, the same: RUN-RUNNING, 17;
#   W2-W7  v2 with one form running alone: session_e183.sh, session_e183_v3.sh, session_e183_v10.sh (a later version), queue_e183.sh,
#       queue_e183_v2.sh, queue_e183_v3.sh: each 17;
#   W8  v2 with only names that are not E183's session running (session_e185_v2.sh, session_e1830.sh, block_e183_v3.sh): RUN-GONE, 14;
#   W9  v2 with nothing running and no session end: RUN-GONE, 14;
#   W10 v2 after the log's "session end (T0 <T0>)": RUN-ENDED, 0; W11 with a gate line before it ("smoke gate failed ..."): GATE-STOPPED,
#       16 (what v1 read at 13:17:32 that day, after the session had ended);
#   W12 v2's dry listing: the remote script with the new pattern, exit 0, no call;
#   W13 v2 is v1 with exactly two lines changed (the step's name and the pattern) and its header.
#   bash tools/claims-v3/e183/rb/selftest_wait_e183.sh <scratch dir outside the repository> > <log>
# Prints SELFTEST-WAIT-E183 PASS or FAIL (<n> of <m>). About two minutes (each running case waits one 15 s loop of the step).
# SPDX-License-Identifier: Apache-2.0
set -u
SRC=$(cd "$(dirname "${BASH_SOURCE[0]}")/../../../.." && pwd)
S=${1:?a scratch directory outside the repository}
case "$S" in "$SRC"|"$SRC"/*) echo "the scratch directory must be outside the repository"; exit 2 ;; esac
case "$S" in *session_e183*|*queue_e183*) echo "the scratch directory's path must not name a session or a queue"; exit 2 ;; esac
ls /dev/et* > /dev/null 2>&1 && { echo "REFUSED: a /dev/et* node is visible here: run this test only inside a no-device sandbox"; exit 2; }
if [ "${E183WT_INNER:-}" != 1 ]; then
  [ -x /usr/bin/bwrap ] || { echo "no /usr/bin/bwrap (bubblewrap)"; exit 2; }
  mkdir -p "$S" || exit 2
  SELF=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)/$(basename "${BASH_SOURCE[0]}")
  E183WT_INNER=1 exec /usr/bin/bwrap --dev-bind / / --dev /dev --tmpfs /run/lock --unshare-pid --proc /proc --die-with-parent -- \
    /bin/bash "$SELF" "$S"
fi
for v in RB_DRY RB_PROBE_S RB_READ_S RB_COPY_S RB_WAIT_S RB_LAUNCH_S RB_DESK_S; do
  [ -z "${!v:-}" ] || { echo "$v is set: this test runs with rb_run.py's own bounds"; exit 2; }
done
S=$(cd "$S" && pwd)
ME=$(id -un)
main() {
rm -rf "${S:?}/box" "${S:?}/bin" "${S:?}/out" "${S:?}/pids"
BOX=$S/box/aifoundry3; BT=$BOX/aifoundry; BIN=$S/bin
mkdir -p "$BT/build/q141k" "$BT/build/e183" "$BT/tools/claims-v3/e183" "$BT/tools/claims-v3/e185" "$BIN" "$S/out" "$S/pids"
cat > "$BIN/ssh" <<EOF
#!/bin/bash
echo "ssh \$*" >> "$S/calls.log"
host=""; cmd=""
while [ \$# -gt 0 ]; do case "\$1" in -o) shift 2 ;; -*) shift ;; *) if [ -z "\$host" ]; then host=\$1; shift; else cmd="\$*"; break; fi ;; esac; done
[ "\$host" = aifoundry3 ] || { echo "STAND-IN SSH: refusing host \$host" >&2; exit 97; }
[ "\$cmd" = true ] && exit 0
[ "\$cmd" = "bash -s" ] || { echo "STAND-IN SSH: refusing the command \$cmd" >&2; exit 97; }
cd "$BOX" && HOME="$BOX" exec bash -s
EOF
for n in rsync scp; do printf '#!/bin/sh\necho "%s $*" >> "%s"\necho "NETWORK STAND-IN: %s refused" >&2\nexit 97\n' "$n" "$S/calls.log" "$n" > "$BIN/$n"; done
chmod +x "$BIN"/*
standin() {  # standin <path under the box tree>: a small script named as that form, which records its pid and waits to be stopped
  mkdir -p "$(dirname "$BT/$1")"
  printf '#!/bin/bash\necho $$ > "%s/pids/%s.pid"\nwhile :; do sleep 1; done\n' "$S" "$(basename "$1")" > "$BT/$1"
}
start() { local j; setsid -f bash "$BT/$1" < /dev/null > /dev/null 2>&1; for j in 1 2 3 4 5 6 7 8 9 10; do [ -s "$S/pids/$(basename "$1").pid" ] && return 0; sleep 0.2; done; return 1; }
stop() { local f p; for f in "$S"/pids/*.pid; do [ -e "$f" ] || continue; p=$(cat "$f"); kill "$p" 2> /dev/null; rm -f "$f"; done; sleep 1.5; }
for n in session_e183.sh session_e183_v2.sh session_e183_v3.sh session_e183_v10.sh queue_e183.sh queue_e183_v2.sh queue_e183_v3.sh \
         block_e183_v3.sh session_e1830.sh; do standin "tools/claims-v3/e183/$n"; done
standin tools/claims-v3/e185/session_e185_v2.sh
export PATH="$BIN:$PATH" RB_OUT="$S/out" RB_LOCK="$S/lock.txt" RB_WAIT_LOOP_S=3
: > "$S/calls.log"; : > "$RB_LOCK"
T0=$(date +%s)
echo "$T0" > "$BT/build/q141k/e183.t0"
L=$BT/build/e183/session-t$T0.log
echo "$(date '+%F %T %Z') session start (T0 $T0 = $(date -d @"$T0" '+%T %Z')), kit note 6; plan FULL" > "$L"
fail=0; npass=0; ncase=0
ok() { ncase=$((ncase + 1)); if [ "$1" = "$2" ]; then npass=$((npass + 1)); echo "-> PASS ($3)"; else echo "-> FAIL ($3: got $1, want $2)"; fail=1; fi; }
step() { echo; echo "== $*"; }
R=$SRC/tools/claims-v3/e183/rb
wait1() { bash "$R/s20_wait_e183.sh" > "$S/w.out" 2>&1; local r=$?; grep -E '^(RUN-|GATE-)|STOP|still runs|has ended' "$S/w.out" | cut -c1-160; return "$r"; }
wait2() { bash "$R/s20_wait_e183_v2.sh" > "$S/w.out" 2>&1; local r=$?; grep -E '^(RUN-|GATE-)|STOP|still runs|has ended' "$S/w.out" | cut -c1-160; return "$r"; }
seen() { echo "visible in this namespace: $(pgrep -c -f '(session|queue|block)_e18' ) stand-in(s): $(pgrep -a -f '(session|queue|block)_e18' | sed 's#^[0-9]* bash .*/##' | tr '\n' ' ')"; }

step "W0. step 10 v1 with session_e183_v2.sh running and no session end (Fri 13 Nov 2026's reading)"
start tools/claims-v3/e183/session_e183_v2.sh; seen
wait1; rc=$?; ok "$rc" 14 "W0 v1 reads RUN-GONE for a running session v2"
step "W1. step 10 v2, the same"
wait2; rc=$?; stop; ok "$rc" 17 "W1 v2 reads RUN-RUNNING"
k=2
for n in session_e183.sh session_e183_v3.sh session_e183_v10.sh queue_e183.sh queue_e183_v2.sh queue_e183_v3.sh; do
  step "W$k. step 10 v2 with $n running alone"
  start "tools/claims-v3/e183/$n"; seen
  wait2; rc=$?; stop; ok "$rc" 17 "W$k v2 reads RUN-RUNNING for $n"
  k=$((k + 1))
done
step "W8. step 10 v2 with only names that are not E183's session running"
start tools/claims-v3/e185/session_e185_v2.sh; start tools/claims-v3/e183/session_e1830.sh; start tools/claims-v3/e183/block_e183_v3.sh; seen
wait2; rc=$?; stop; ok "$rc" 14 "W8 v2 reads RUN-GONE (another run's session, a longer name, a block)"
step "W9. step 10 v2 with nothing running and no session end"
seen; wait2; rc=$?; ok "$rc" 14 "W9 v2 reads RUN-GONE"
step "W10. step 10 v2 after the log's session end"
echo "$(date '+%F %T %Z') session end (T0 $T0)" >> "$L"
wait2; rc=$?; ok "$rc.$(grep -c '^RUN-ENDED e183' "$S/w.out")" "0.1" "W10 v2 reads RUN-ENDED (0)"
step "W11. step 10 v2 with a gate line before the session end"
sed -i "\$i $(date '+%F %T %Z') smoke gate failed (stop test rc 0, smoke rc 1, gate 0): no train block runs" "$L"
wait2; rc=$?; ok "$rc.$(grep -c '^GATE-STOPPED e183' "$S/w.out")" "16.1" "W11 v2 reads RUN-ENDED and GATE-STOPPED (16)"
step "W12. step 10 v2's dry listing"
n0=$(grep -c . "$S/calls.log")
RB_DRY=1 bash "$R/s20_wait_e183_v2.sh" > "$S/w12.out" 2>&1; rc=$?
grep -F 'pgrep -u "$(id -u)" -f "(session|queue)_e183(_v[0-9]+)?\.sh"' "$S/w12.out" | sed 's/^ *| *//' | cut -c1-140
ok "$rc.$(grep -cF '(session|queue)_e183(_v[0-9]+)?\.sh' "$S/w12.out").$(( $(grep -c . "$S/calls.log") - n0 ))" "0.1.0" "W12 the listing shows the new pattern and makes no call"
step "W13. step 10 v2 is v1 with two lines changed, and its header"
d=$(diff "$R/s20_wait_e183.sh" "$R/s20_wait_e183_v2.sh" | grep -E '^[<>]' | grep -v '^> #')
printf '%s\n' "$d"
ok "$(printf '%s\n' "$d" | grep -c '^<').$(printf '%s\n' "$d" | grep -c '^>')" "2.2" "W13 two lines out, two in"
step "Z. no stand-in left; no rsync or scp; the lock file untouched"
left=$(pgrep -c -f '(session|queue|block)_e18'); nl=$(grep -c . "$RB_LOCK"); nn=$(grep -c -E '^(rsync|scp) ' "$S/calls.log")
echo "stand-ins left: $left; lock file lines: $nl; rsync or scp calls: $nn; ssh calls: $(grep -c '^ssh ' "$S/calls.log")"
ok "$left.$nl.$nn" "0.0.0" "Z"
echo
echo "SELFTEST-WAIT-E183 $([ "$fail" -eq 0 ] && echo PASS || echo FAIL) ($npass of $ncase): step 10 v2 reads every session and queue version of E183; v1 misreads session v2 as gone"
return "$fail"
}
main 2>&1 | sed "s#$S#<scratch>#g; s#$SRC#<repo>#g; s#$HOME#<home>#g; s#\\b$ME\\b#<login>#g"
exit "${PIPESTATUS[0]}"
