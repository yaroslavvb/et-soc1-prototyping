#!/usr/bin/env bash
# Q141(k) v2: the runbook's desk test. It never reaches a lab box: a stand-in `ssh` and `rsync`, first on PATH in the scratch dir, take
# every call. The stand-in ssh answers the probe (`true`) and, for a remote script, runs it in a stand-in box (a scratch HOME holding
# ~/aifoundry, ~/nekko and ~/claude/et-soc1-prototyping, with stub et-who, who, uptime, sudo, setsid, flock and a GNU date on PATH), or
# hangs, or prints a Tailscale check link and hangs, or fails, as the case sets (for every box, or for one: FAKE_CALL_<box>,
# FAKE_PROBE_<box>; FAKE_CALL_MATCH narrows a call mode to remote commands holding that text). RB_REPO is a scratch git repo holding
# the kit files the cases send or run, copied unchanged from the lab clone (E164's box scripts, collect_e166.sh, collect_e167_bounded.sh
# and the helpers it calls). Desk only, on the Intel:
#
#   bash tools/claims-v3/q141k-runbook/v2/selftest_runbook.sh <a new, empty scratch dir> > tools/claims-v3/q141k-runbook/v2/logs/selftest.txt
#
# A-F are v1's cases (../selftest_runbook.sh), run against v2: (A) success; (B) a login link and then a hang; (C) a hang with no
# output; (D) a non-zero exit; (F) the desk helpers and the window's gates; (E) the dry listing. X1-X10 are the cases for what
# Q141(k)'s verifier tested beyond v1's (its X1-X6) and the faults it found, each with v1 run beside it where that shows the fault:
#   X1  a link printed by rsync inside collect_e166.sh, under GNU timeout's own process group (the verifier's X1; it passed in v1)
#   X2  a link split across two writes (the verifier's X2; it passed in v1)
#   X3  fault 1: s13 refuses while s12's check job runs on aifoundry1, without s12's clean read, and on a check job of another day
#   X4  fault 3: a plain e166 refuses on an earlier smoke, or on one already moved aside; --later-try rests from the later session end
#   X5  fault 2: a lost dry job exits 14, call after call (v1: 17 for ever); a job whose pid comes late still runs; one not started today
#   X6  nit 1: s09 refuses while a card session of ours runs on aifoundry3, and the guard is never called
#   X7  fault 4: s22 e167 probes all three boxes; a link from aifoundry3's history read names aifoundry3 in the lock line (v1: aifoundry2)
#   X8  fault 5: s14's identity by continuity: the boot of record passes, a later boot stops every aifoundry2 run (16)
#   X9  nit 5: another day's state is never today's (s16's dry passes, s20's log offset and status, s11's E166 offset)
#   X10 nit 2: E163 FULL is refused when its 70 minutes would pass the last end; TWO, which fits, is launched
#   V   the files v2 keeps from v1 are byte for byte v1's.
# After every case: no stand-in process is left running, and no stand-in login appears in any file the runbook wrote.
# SPDX-License-Identifier: Apache-2.0
set -u
T=${1:?usage: selftest_runbook.sh <a new, empty scratch dir>}
[ -d "$T" ] && [ -n "$(ls -A "$T" 2>/dev/null)" ] && { echo "refused: $T is not empty"; exit 2; }
D=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
V1=$(cd "$D/.." && pwd)
LAB=$(cd "$D/../../../.." && pwd)
mkdir -p "$T/bin" "$T/stubs" "$T/home" "$T/state" "$T/repo" "$T/carry" || exit 2
T=$(cd "$T" && pwd -P)
GDATE=$(command -v gdate || command -v date)
GTOUCH=$(command -v gtouch || command -v touch)

# ---- the stand-in ssh: it never connects anywhere (its sleeps are 3627 s; v1's test uses 3617, so neither clean-up touches the other)
cat > "$T/bin/ssh" <<'EOS'
#!/bin/bash
[ -n "${FAKE_LOG:-}" ] && [ -n "${FAKE_HOME:-}" ] || { echo "stand-in ssh: not inside the desk test" >&2; exit 255; }
echo "ssh $*" >> "$FAKE_LOG"
while [ $# -gt 0 ]; do case "$1" in -o|-p|-i|-l|-F) shift 2 ;; -*) shift ;; *) break ;; esac; done
host=$1; shift
case "$host" in aifoundry1|aifoundry2|aifoundry3) ;; *) echo "stand-in ssh: unexpected host $host" >&2; exit 255 ;; esac
if [ "$*" = true ]; then
  eval "mode=\${FAKE_PROBE_$host:-\${FAKE_PROBE:-ok}}"
else
  eval "mode=\${FAKE_CALL_$host:-\${FAKE_CALL:-ok}}"
  if [ -n "${FAKE_CALL_MATCH:-}" ]; then case "$*" in *"$FAKE_CALL_MATCH"*) ;; *) mode=ok ;; esac; fi
fi
case "$mode" in
  ok) ;;
  link) echo "# Tailscale SSH requires an additional check." >&2
        echo "# To authenticate, visit: https://login.tailscale.com/a/desk-test-$host" >&2; exec sleep 3627 ;;
  link-stdout) echo "To authenticate, visit: https://login.tailscale.com/a/desk-test-stdout"; exec sleep 3627 ;;
  hang) exec sleep 3627 ;;
  fail) echo "stand-in ssh: the remote command failed" >&2; exit 7 ;;
  refuse) echo "ssh: connect to host $host port 22: Connection refused" >&2; exit 255 ;;
esac
[ "$*" = true ] && exit 0
cd "$FAKE_HOME" || exit 255
# as a real ssh does: the words joined into one command line, split again by the box's shell, and the script on stdin through a
# pipe (ssh's channel), never the seekable file itself (E164 README.md.dated-note.md, "The emulation")
export HOME="$FAKE_HOME" PATH="$FAKE_STUBS:$PATH" FAKE_HOST="$host"
cat | eval "exec $*"
EOS
# ---- the stand-in rsync ------------------------------------------------------------------------------------------------------
cat > "$T/bin/rsync" <<'EOS'
#!/bin/bash
[ -n "${FAKE_LOG:-}" ] || { echo "stand-in rsync: not inside the desk test" >&2; exit 255; }
echo "rsync $*" >> "$FAKE_LOG"
case "${FAKE_RSYNC:-ok}" in
  ok) echo "stand-in rsync: nothing copied"; exit 0 ;;
  link) echo "# To authenticate, visit: https://login.tailscale.com/a/desk-test-rsync" >&2; exec sleep 3627 ;;
  hang) exec sleep 3627 ;;
  fail) echo "rsync error: some files could not be transferred (code 23)" >&2; exit 23 ;;
esac
EOS
# ---- the stand-in box's commands ---------------------------------------------------------------------------------------------
printf '#!/bin/bash\nexec %s "$@"\n' "$GDATE" > "$T/stubs/date"
printf '#!/bin/bash\nexec "$@"\n' > "$T/stubs/setsid"
printf '#!/bin/bash\n# stand-in flock -n <lock> <command...>: no lock on this desk; run the command\nshift 2; exec "$@"\n' > "$T/stubs/flock"
cat > "$T/stubs/pgrep" <<'EOS'
#!/bin/bash
# stand-in pgrep: the real one, keeping only this desk test's own processes (their command line names the test's scratch dir), so
# the stand-in box never counts another session's processes on this Mac as a card session of ours
out=$(/usr/bin/pgrep -l "$@" 2>/dev/null | awk -v s="$FAKE_SCOPE" 'index($0, s) {print $1}')
[ -n "$out" ] || exit 1          # as pgrep: 1 when nothing matches
echo "$out"
EOS
cat > "$T/stubs/et-who" <<'EOS'
#!/bin/bash
n=$(cat "$FAKE_STATE/etwho-held" 2>/dev/null || echo 0)
if [ "$n" -gt 0 ]; then
  echo $((n - 1)) > "$FAKE_STATE/etwho-held"
  printf '%-14s %s\n' /dev/et0_ops "zz_other_user   4242   01:02:03 /home/zz_other_user/bin/sparsity_host --test fma"
  printf '%-14s %s\n' lock:etsoc-shire0.lock "zz_other_user   4242   01:02:03 /home/zz_other_user/bin/sparsity_host --test fma"
elif [ -e "$FAKE_STATE/etwho-card1" ]; then
  printf '%-14s %s\n' /dev/et1_ops "zz_other_user   4243   00:10:00 sparsity_host --test fma"
else
  echo "No process holds an ET-SoC-1 device node or card lock."
fi
EOS
cat > "$T/stubs/sudo" <<'EOS'
#!/bin/bash
# only the one call the kit makes: sudo -n /usr/local/sbin/et-holders (never the real sudo)
[ "$1" = -n ] && [ "$2" = /usr/local/sbin/et-holders ] && exec et-who
echo "stand-in sudo: refused $*" >&2; exit 1
EOS
printf '#!/bin/bash\nprintf "zz_other_user pts/1        2026-10-26 15:19\\nzz_other_user pts/2        2026-10-26 15:20\\n"\n' > "$T/stubs/who"
cat > "$T/stubs/uptime" <<'EOS'
#!/bin/bash
if [ "${1:-}" = -s ]; then if [ -s "$FAKE_STATE/boot" ]; then cat "$FAKE_STATE/boot"; else echo "2026-10-26 09:00:00"; fi; exit 0; fi
echo " 10:00:00 up 9 days,  2 users,  load average: 0.50, 0.40, 0.30"
EOS
printf '#!/bin/bash\necho "host         stand-in box (desk test)"\n' > "$T/stubs/et-lab-manifest"
chmod +x "$T/bin/"* "$T/stubs/"*
# ---- the stand-in box's trees ------------------------------------------------------------------------------------------------
H=$T/home
A3=$H/aifoundry; A1=$H/nekko; A2=$H/claude/et-soc1-prototyping
mkdir -p "$A3/build" "$A1/tools/claims-v3/e164/box" "$A1/build" "$H/claude/work" "$H/live/history" \
  "$A2/tools/claims-v3/e165" "$A2/build/q141k/jobs" "$A3/tools/claims-v3/e166" "$A3/tools/claims-v3/e163" "$A3/tools/claims-v3/e128"
printf 'print("HARNESS OK: 107 files match harness-e164.json")\n' > "$A1/tools/claims-v3/e164/check_e164.py"
cat > "$A1/tools/claims-v3/e164/session_e164.sh" <<'EOS'
mkdir -p build/e164
env | grep '^E164_' | sort > build/e164/session-env.txt
echo "$(date '+%F %T %Z') session start (stand-in)" >> build/e164/session.log
echo "$(date '+%F %T %Z') session end" >> build/e164/session.log
EOS
cat > "$A1/tools/claims-v3/e164/box/check_box_e164.sh" <<'EOS'
echo "$(date '+%F %T %Z')"
echo "== check_e164 (with the binaries)"; echo "HARNESS OK: 107 files match harness-e164.json"; echo "rc=0"
echo "== preflight"; echo "rc=0 dmcmd_audit: GO (32 send sites, 0 disallowed)"
echo "== tiles"; echo '{"tiles": 72, "problems": []}'; echo "rc=0"
echo "== pool 7's SHA256SUMS"; echo "91"
echo "== dry pass 16410"; echo "rc=0 (want 0) 98 device calls printed"
echo "== dry smoke 16401"; echo "rc=0 (want 0)"
echo "== dry stop-path test 16402"; echo "rc=1 (a dry run ends 1: its stops need live samples)"
et-who | tail -3
EOS
cat > "$A2/tools/claims-v3/e165/queue_e165.py" <<'EOS'
import json, os, sys
a = sys.argv[1:]
runs = a[a.index("--runs") + 1]
os.makedirs(runs, exist_ok=True)
open(os.path.join(runs, "argv.txt"), "w").write(" ".join(a) + "\n")
with open(os.path.join(runs, "queue.jsonl"), "a") as f:
    f.write(json.dumps({"t_ms": 1, "kind": "smoke_check", "rc": 0, "bad": None}) + "\n")
    f.write(json.dumps({"t_ms": 2, "kind": "queue_end"}) + "\n")
json.dump({"state": "ended", "why": "done"}, open(os.path.join(runs, "status.json"), "w"))
print("stand-in queue_e165: started and ended")
EOS
for w in e166 e163; do   # stand-in sessions on aifoundry3: a start and an end line in the kit's own form, then gone
  printf 'mkdir -p build/%s\necho "$(date '"'"'+%%F %%T %%Z'"'"') session start (stand-in)" >> build/%s/session.log\necho "$(date '"'"'+%%F %%T %%Z'"'"') session end" >> build/%s/session.log\n' \
    "$w" "$w" "$w" > "$A3/tools/claims-v3/$w/session_$w.sh"
done
cat > "$A3/tools/claims-v3/e128/ettelem_guard.sh" <<'EOS'
echo '{"tdp_w":0,"temp_threshold_c":65,"power_state":0,"power_state_name":"max_power","minion_mhz":600,"minion_mv":523}'
echo "config read $(date '+%T')" >> "$HOME/guard-calls.txt"
EOS
for r in e165 e167 e168 e169; do echo 0 > "$A2/build/q141k/jobs/a2-dry-$r.rc"; done
# ---- the scratch repo (RB_REPO): the kit files the cases send or run, unchanged -----------------------------------------------
mkdir -p "$T/repo/tools/claims-v3/e164/box" "$T/repo/tools/claims-v3/e166" "$T/repo/tools/claims-v3/e167" "$T/repo/tools/claims-v3/e111" \
  "$T/repo/tools/claims-v3/e133" "$T/repo/tools/claims-v3/kspeed/e98"
for f in look_e164.sh launch_e164_a1.sh wait_e164.sh; do cp "$LAB/tools/claims-v3/e164/box/$f" "$T/repo/tools/claims-v3/e164/box/"; done
for f in e166/collect_e166.sh e167/collect_e167_bounded.sh e111/scrub_logins_e111.py e133/utc_days_e133.py kspeed/e98/thin_history.py; do
  cp "$LAB/tools/claims-v3/$f" "$T/repo/tools/claims-v3/$f"
done
( cd "$T/repo" && git init -q && git add -A && git -c user.name=desk-test -c user.email=desk-test commit -q -m "desk test" ) || exit 2

export PATH="$T/bin:$PATH" FAKE_LOG="$T/calls.txt" FAKE_HOME="$H" FAKE_STUBS="$T/stubs" FAKE_STATE="$T/state" RB_REPO="$T/repo" FAKE_SCOPE="$T"
[ "$(command -v ssh)" = "$T/bin/ssh" ] && [ "$(command -v rsync)" = "$T/bin/rsync" ] || { echo "refused: the stand-ins are not first on PATH"; exit 2; }
cat > "$T/day.py" <<'PY'
import datetime
print(datetime.date.today() + datetime.timedelta(days=2))
PY
DAY=$(/usr/bin/python3 -I "$T/day.py")
echo "# Q141(k) v2 runbook desk test: $(date '+%a %d %b %Y %H:%M:%S %Z'); ssh and rsync on PATH are the stand-ins; a sample window, on $DAY"
fails=0; n=0
ok() { n=$((n + 1)); if [ "$1" = 1 ]; then echo "ok   $2"; else echo "FAIL $2"; fails=$((fails + 1)); fi; }
left() { pgrep -f 'sleep 3627' > /dev/null && { pkill -f 'sleep 3627'; echo yes; } || echo no; }
secs() { /usr/bin/python3 -I "$T/secs.py" "$1" "$2"; }
cat > "$T/secs.py" <<'PY'
import sys
print(round(float(sys.argv[2]) - float(sys.argv[1]), 1))
PY
cat > "$T/cmpf.py" <<'PY'
import sys
a, op, b = float(sys.argv[1]), sys.argv[2], float(sys.argv[3])
sys.exit(0 if (a < b if op == "lt" else a >= b) else 1)
PY
run_() {  # run_ <dir of the runbook> <name> <expected rc> <step> [args...]: one step with a fresh RB_OUT; sets RC, SECS, O
  local dir=$1 name=$2 want=$3; shift 3
  O=$T/out-$name; mkdir -p "$O"
  for c in "$T"/carry/*; do [ -e "$c" ] && cp "$c" "$O/"; done
  [ -n "${CASE_WINDOW:-}" ] && cp "$CASE_WINDOW" "$O/window.env"
  [ -n "${CASE_DROP:-}" ] && rm -f "$O/$CASE_DROP"
  : > "$FAKE_LOG"
  local t0 t1; t0=$("$GDATE" +%s.%N)
  RB_OUT=$O RB_LOCK=$O/lock.txt bash "$dir/$1" "${@:2}" > "$O/stdout.txt" 2>&1
  RC=$?
  t1=$("$GDATE" +%s.%N)
  SECS=$(secs "$t0" "$t1")
  ok "$([ "$RC" = "$want" ] && echo 1 || echo 0)" "$name: $([ "$dir" = "$V1" ] && echo "v1's ")$1 ${*:2} -> exit $RC (want $want) in $SECS s"
  ok "$([ "$(left)" = no ] && echo 1 || echo 0)" "$name: no stand-in process left running"
  ok "$(grep -rqs 'zz_other_user' "$O" && echo 0 || echo 1)" "$name: no stand-in login in any file the runbook wrote"
}
case_() { run_ "$D" "$@"; }
case_v1() { run_ "$V1" "$@"; }
lockline() { grep -qE "^[0-2][0-9]:[0-5][0-9]:[0-5][0-9] $1 needs a check$" "$O/lock.txt" 2>/dev/null && echo 1 || echo 0; }
fast() { /usr/bin/python3 -I "$T/cmpf.py" "$SECS" lt "$1" && echo 1 || echo 0; }
between() { /usr/bin/python3 -I "$T/cmpf.py" "$SECS" ge "$1" && /usr/bin/python3 -I "$T/cmpf.py" "$SECS" lt "$2" && echo 1 || echo 0; }
has() { grep -qE -- "$1" "$O/stdout.txt" && echo 1 || echo 0; }
hasnot() { grep -qE -- "$1" "$O/stdout.txt" && echo 0 || echo 1; }
stale() { "$GTOUCH" -d '-1 day' "$@"; }   # written yesterday, by the Pacific calendar's day before

echo; echo "== A. success"
case_ A1 0 s01_probe.sh
ok "$( [ "$(grep -c 'class=probe .*rc=0 .*status=ok' "$O/runbook.log")" -eq 3 ] && echo 1 || echo 0)" "A1: three probe lines in the log, each rc=0 status=ok"
ok "$(grep -q 'step=s01_probe_v2 ' "$O/runbook.log" && echo 1 || echo 0)" "A1: the log names the step as v2's (step=s01_probe_v2)"
case_ A2 0 s02_window.sh "$DAY" 15:30 16:30 full
cp "$O/window.env" "$T/carry/window.env"
ok "$(grep -q "^RB_E164_DEADLINE=.*$DAY\\\\ 16:20\\\\ P[SD]T" "$T/carry/window.env" && echo 1 || echo 0)" "A2: the window holds E164's deadline, the last end less 10 minutes"
case_ A3 0 s05_look.sh aifoundry3
ok "$(grep -q '^HOLDER-RULE: FREE' "$O"/calls/*.out && grep -q 'logins 2 (an idle login does not block)' "$O"/calls/*.out && echo 1 || echo 0)" "A3: FREE with two idle logins (they do not block)"
echo 2 > "$T/state/etwho-held"
RB_HOLD_POLL_S=1 RB_WAIT_LOOP_S=20 case_ A4 0 s05_look.sh aifoundry2 --wait
ok "$(grep -q '^HOLDER-RULE: FREE after [0-9]* s of polls' "$O"/calls/*.out && echo 1 || echo 0)" "A4: a held card polled on the box until free"
echo 999 > "$T/state/etwho-held"
RB_HOLD_POLL_S=1 RB_WAIT_LOOP_S=2 case_ A5a 17 s05_look.sh aifoundry2 --wait
mkdir -p "$T/out-A5b"; echo $(( $(date +%s) - 1810 )) > "$T/out-A5b/hold-aifoundry2.since"
RB_HOLD_POLL_S=1 RB_WAIT_LOOP_S=2 case_ A5b 15 s05_look.sh aifoundry2 --wait
rm -f "$T/state/etwho-held"
case_ A6 0 s07_a3_sync.sh
ok "$(grep -q -- '-a -c -R --exclude __pycache__ -e ssh -o BatchMode=yes -o ConnectTimeout=10 tools/claims-v3/e163/ .* tools/claims-v3/e166/ aifoundry3:aifoundry/' "$FAKE_LOG" && echo 1 || echo 0)" "A6: one rsync with E163's step-4 paths and tools/claims-v3/e166/ to aifoundry3:aifoundry/"
case_ A7a 0 s12_a1_check.sh start
case_ A7b 0 s12_a1_check.sh wait
ok "$(grep -q '^JOB-DONE a1-check rc=0$' "$O"/calls/*.out && echo 1 || echo 0)" "A7: the detached check job ended rc 0 and its lines read clean"
ok "$(grep -q "^$DAY clean " "$O/a1-check-clean.txt" 2>/dev/null && echo 1 || echo 0)" "A7: the clean read is recorded for s13 (RB_OUT/a1-check-clean.txt names the window's day)"
cp "$O/a1-check-clean.txt" "$T/carry/"
case_ A8 0 s13_a1_launch.sh
ok "$(grep -qx "E164_DEADLINE=$DAY 16:20 P[SD]T" "$A1/build/e164/session-env.txt" && echo 1 || echo 0)" "A8: the session got the whole deadline through ssh ('$DAY 16:20 PST', not the date alone)"
ok "$(grep -q "bash -s -- '$DAY 16:20 P[SD]T'" "$FAKE_LOG" && echo 1 || echo 0)" "A8: launch_e164_a1.sh's usage line, the quoting inside the remote command"
ok "$(grep -q '^GUARD-OK' "$O"/calls/*guard*.out && echo 1 || echo 0)" "A8: the guard read came first and found no dry pass, no session of ours, s12's check of today"
case_ A9 0 s16_a2_e165.sh full
cat > "$T/slot_check.py" <<'PY'
import re, sys
m = re.search(r"SLOT E165: start (\d+) .*?end (\d+) ", open(sys.argv[1]).read())
sys.exit(0 if m and int(m.group(2)) - int(m.group(1)) == 2700 else 1)
PY
ok "$(/usr/bin/python3 -I "$T/slot_check.py" "$H/claude/work/q141-a2-e165-slot.txt" && echo 1 || echo 0)" "A9: E165's slot line parses by the queue's own pattern, 2,700 s"
ok "$(grep -q -- '--runs build/e165/runs --cap 40' "$A2/build/e165/runs/argv.txt" && echo 1 || echo 0)" "A9: the queue started with --runs build/e165/runs --cap 40"
case_ A10 0 s20_wait.sh e165
touch "$T/state/etwho-card1"
case_ A11 17 s05_look.sh aifoundry1
ok "$(grep -q '^/dev/et1_ops *<holder> *4243 *00:10:00 <command withheld>$' "$O"/calls/*.out && echo 1 || echo 0)" "A11: look_e164.sh's raw et-who line kept with its login and command masked"
ok "$(grep -q 'identity: the host booted .*: ok' "$O"/calls/*.out && echo 1 || echo 0)" "A11: look_e164.sh's identity line read (booted before E82's firmware read)"
rm -f "$T/state/etwho-card1"

echo; echo "== B. a login link, then a hang"
FAKE_PROBE=link case_ B1 11 s05_look.sh aifoundry2
ok "$(lockline aifoundry2)" "B1: '<HH:MM:SS> aifoundry2 needs a check' appended to the lock file"
ok "$(grep -q 'https://login.tailscale.com/a/desk-test-aifoundry2' "$O/links.txt" && echo 1 || echo 0)" "B1: the link kept in RB_OUT/links.txt for the approval"
ok "$(fast 6)" "B1: killed at once (under 6 s, not at the probe's 15 s)"
FAKE_CALL=link case_ B2 11 s09_a3_reads.sh
ok "$(lockline aifoundry3)" "B2: the link on a call's stderr: lock line for aifoundry3"; ok "$(fast 6)" "B2: killed at once"
FAKE_CALL=link-stdout case_ B3 11 s14_a2_tree.sh
ok "$(lockline aifoundry2)" "B3: the link on a call's stdout: lock line for aifoundry2"; ok "$(fast 6)" "B3: killed at once"
FAKE_RSYNC=link case_ B4 11 s07_a3_sync.sh
ok "$(lockline aifoundry3)" "B4: the link on rsync's stderr: lock line for aifoundry3"; ok "$(fast 6)" "B4: killed at once"
FAKE_PROBE=link case_ B5 11 s01_probe.sh
ok "$( [ "$(grep -c 'needs a check$' "$O/lock.txt")" -eq 3 ] && [ "$(wc -l < "$O/links.txt" | tr -d ' ')" -eq 3 ] && echo 1 || echo 0)" "B5: three boxes, three lock lines, three links"

echo; echo "== C. a hang with no output"
FAKE_PROBE=hang case_ C1 12 s05_look.sh aifoundry1
ok "$(between 14.5 19.5)" "C1: the probe hard-killed at its 15 s"; ok "$( [ ! -s "$O/lock.txt" ] && echo 1 || echo 0)" "C1: no lock line (no link was printed)"
FAKE_CALL=hang RB_READ_S=3 case_ C2 13 s08_a3_preflight.sh
ok "$(between 2.5 8)" "C2: a read killed at its bound (60 s; 3 s here)"
FAKE_RSYNC=hang RB_COPY_S=3 case_ C3 13 s07_a3_sync.sh
ok "$(between 2.5 8)" "C3: a copy killed at its bound (600 s; 3 s here)"
FAKE_CALL=hang FAKE_CALL_MATCH="bash -s -- " RB_LAUNCH_S=3 case_ C4 13 s13_a1_launch.sh
ok "$(between 2.5 8)" "C4: a launch killed at its bound (60 s; 3 s here), after its guard read answered"
FAKE_CALL=hang RB_WAIT_S=3 case_ C5 13 s20_wait.sh e167
ok "$(between 2.5 8)" "C5: a wait killed at its bound (600 s; 3 s here)"

echo; echo "== D. a non-zero exit"
FAKE_CALL=fail case_ D1 14 s05_look.sh aifoundry3
ok "$(grep -q 'rc=14 child_rc=7 status=exit 7' "$O/runbook.log" && echo 1 || echo 0)" "D1: the call's own status (7) in the log line"
FAKE_RSYNC=fail case_ D2 14 s07_a3_sync.sh
ok "$(grep -q 'rc=14 child_rc=23 status=exit 23' "$O/runbook.log" && echo 1 || echo 0)" "D2: rsync's own status (23) in the log line"
FAKE_PROBE=refuse case_ D3 12 s01_probe.sh aifoundry2
touch "$T/state/etwho-card1"
case_ D4 14 s13_a1_launch.sh
ok "$(has "REFUSED: card 1's nodes or lock are held: nothing launched")" "D4: launch_e164_a1.sh's own refusal (exit 3) on a card-1 holder, reported"
rm -f "$T/state/etwho-card1"

echo; echo "== F. the desk helpers and the window's gates (no ssh)"
r=$(/usr/bin/python3 -B "$D/frozen26.py" "$LAB"); ok "$([ "$r" = "FROZEN 26 OK" ] && echo 1 || echo 0)" "F1: frozen26.py on the lab clone: $r"
mkdir -p "$T/f2" "$T/f3"
cat > "$T/f2/results.json" <<'JS'
{"score": {"anchors": {"fp32": [{"burst_w": 40.1, "burst_mhz": 800.0, "die_start": 54.0}], "fp16": [], "int8": [{"burst_w": 38.2, "burst_mhz": 800.0, "die_start": 54.2}]},
           "anchor_delta": {"delta_w": {"fp32": 0.11, "fp16": 0.05, "int8": -0.02}, "delta_source": "the session's own zeros anchors"}}}
JS
/usr/bin/python3 -B "$D/anchors_e165.py" "$T/f2" > "$T/f2/out.txt"; r=$?
cat > "$T/f2/cmp.py" <<'PY'
import json, sys
d = sys.argv[1]
res = json.load(open(d + "/results.json"))["score"]
sys.exit(0 if json.load(open(d + "/anchors-for-e167-e168.json")) == res["anchors"]
         and json.load(open(d + "/anchor-delta-e165.json")) == res["anchor_delta"] else 1)
PY
ok "$([ "$r" = 0 ] && /usr/bin/python3 -I "$T/f2/cmp.py" "$T/f2" && echo 1 || echo 0)" "F2: anchors_e165.py writes score.anchors and score.anchor_delta unchanged"
echo '{"score": {"note": "fewer than 2 governed passes: every rule NOT SCORED"}}' > "$T/f3/results.json"
/usr/bin/python3 -B "$D/anchors_e165.py" "$T/f3" > "$T/f3/out.txt"; r=$?
ok "$([ "$r" = 3 ] && [ ! -e "$T/f3/anchors-for-e167-e168.json" ] && echo 1 || echo 0)" "F3: a NOT SCORED E165 writes no anchors file (exit 3)"
rm -rf "${D:?}/__pycache__"
cat > "$T/near.py" <<'PY'
import datetime
a = datetime.datetime.now() + datetime.timedelta(minutes=40)
b = datetime.datetime.now() + datetime.timedelta(minutes=90)
print(a.date().isoformat(), a.strftime("%H:%M"), b.strftime("%H:%M"), "same" if a.date() == b.date() else "cross")
PY
/usr/bin/python3 -I "$T/near.py" > "$T/near.txt"
read -r nd na nb same < "$T/near.txt"
if [ "$same" = same ]; then
  mv "$T/carry/window.env" "$T/window.keep"
  case_ F4 16 s02_window.sh "$nd" "$na" "$nb" full
  ok "$(has 'plans that fit: none')" "F4: a window under 1 h 45 min fits no plan"
  mv "$T/window.keep" "$T/carry/window.env"
else
  echo "skip F4: the near window would cross midnight"
fi
case_ F5 10 s17_a2_e167.sh go 14:30 13:10 15:00 16:00
ok "$(has 'smoke-not-before <= smoke-latest < no-start-after < cutoff')" "F5: E167's four gates out of order are refused before any call"
ok "$( [ ! -s "$FAKE_LOG" ] && echo 1 || echo 0)" "F5: no ssh before the gates are read"
case_ F6 16 s17_a2_e167.sh go 13:00 13:30 16:00 16:30
ok "$(has "no-start-after 16:00 is past the round's last start 15:30")" "F6: a no-start-after past the window's last start is refused"

echo; echo "== X1-X2. the verifier's two cases that passed in v1, kept"
FAKE_RSYNC=link case_ X1 11 s22_collect.sh e166
ok "$(lockline aifoundry3)" "X1: a link from rsync inside collect_e166.sh (GNU timeout's own process group): lock line for aifoundry3"
ok "$(fast 6)" "X1: killed at once"
cat > "$T/split.sh" <<'EOS'
printf 'visit https://login.tail' >&2; sleep 1; printf 'scale.com/a/split-check\n' >&2; exec sleep 3627
EOS
O=$T/out-X2; mkdir -p "$O"
RB_LOCK=$O/lock.txt RB_LOG=$O/log.txt RB_LINKS=$O/links.txt /usr/bin/python3 -B "$D/rb_run.py" --cls read --host aifoundry2 --step X2 --what split -- bash "$T/split.sh" > "$O/stdout.txt" 2>&1; r=$?
ok "$([ "$r" = 11 ] && [ "$(lockline aifoundry2)" = 1 ] && grep -q 'split-check' "$O/links.txt" && echo 1 || echo 0)" "X2: a link split across two writes: exit $r, the lock line and the whole link kept"
ok "$([ "$(left)" = no ] && echo 1 || echo 0)" "X2: no stand-in process left running"
rm -rf "${D:?}/__pycache__"

echo; echo "== X3. fault 1: s13 holds the order of steps 12 and 13"
J1=$A1/build/q141k/jobs/a1-check
printf 'exec sleep 3628\n' > "$T/sleeper.sh"     # a live check job: 3628, killed by pid below (left() looks for 3627 only)
bash "$T/sleeper.sh" > /dev/null 2>&1 < /dev/null &
SP=$!
echo "$SP" > "$J1.pid"; rm -f "$J1.rc"; echo "true" > "$J1.sh"
nl0=$(wc -l < "$A1/build/e164/session.log" | tr -d ' ')
case_ X3a 10 s13_a1_launch.sh
ok "$(has 'REFUSED: a dry pass of the runbook still runs on aifoundry1')" "X3a: refused on the box while s12's check job still runs (V3_DRY 16410, 16401, 16402)"
ok "$(grep -q "bash -s -- " "$FAKE_LOG" && echo 0 || echo 1)" "X3a: launch_e164_a1.sh never sent"
ok "$([ "$(wc -l < "$A1/build/e164/session.log" | tr -d ' ')" = "$nl0" ] && echo 1 || echo 0)" "X3a: no session started in the stand-in box"
case_v1 X3v1 0 s13_a1_launch.sh
ok "$(has 'launched T0=')" "X3v1: v1's s13 in the same state launched E164 beside the running check job (the verifier's X3)"
kill "$SP" 2>/dev/null; wait "$SP" 2>/dev/null
echo 0 > "$J1.rc"
CASE_DROP=a1-check-clean.txt case_ X3b 10 s13_a1_launch.sh
ok "$(has "s12_a1_check.sh wait has not read aifoundry1's box check clean today")" "X3b: refused without s12's clean read (step 12, then 13)"
ok "$( [ ! -s "$FAKE_LOG" ] && echo 1 || echo 0)" "X3b: not one ssh call"
stale "$J1.rc"
case_ X3c 10 s13_a1_launch.sh
ok "$(has "s12's box check job has not ended rc 0 today")" "X3c: refused on a check job's exit status from another day"
echo 0 > "$J1.rc"

echo; echo "== X4. fault 3: a later E166 try"
SM=$A3/build/claims-v3/aifoundry3/e166-smoke
mkdir -p "$SM/p16601" "$A3/build/e163" "$A3/build/e166"
echo '{"status":"ok"}' > "$SM/p16601/block.json"
: > "$A3/build/e166/session.log"; l166=0
case_ X4a 10 s11_a3_session.sh e166
ok "$(has 'REFUSED: an earlier E166 smoke is on the box')" "X4a: a plain e166 refused on the earlier smoke p16601 (it would have read the old gate as GO)"
ok "$([ -e "$SM/p16601/block.json" ] && [ "$(wc -l < "$A3/build/e166/session.log" | tr -d ' ')" = "$l166" ] && echo 1 || echo 0)" "X4a: p16601 left in place, no session started"
case_v1 X4v1 0 s11_a3_session.sh e166
ok "$(has 'LAUNCHED e166')" "X4v1: v1's plain e166 launched over the earlier smoke (the verifier's X4)"
mv "$SM/p16601" "$SM/p16601.try1"
case_ X4b 10 s11_a3_session.sh e166
ok "$(has "REFUSED: an earlier try's smoke was moved aside")" "X4b: a plain e166 refused when an earlier try's smoke was moved aside (a further try needs its own amendment)"
mv "$SM/p16601.try1" "$SM/p16601"
echo "$("$GDATE" -d '-60 min' '+%F %T %Z') session end" > "$A3/build/e163/session.log"
echo "$("$GDATE" -d '-5 min' '+%F %T %Z') session end" > "$A3/build/e166/session.log"
case_ X4c 10 s11_a3_session.sh e166 --later-try
ok "$(has "REFUSED: [45] minutes since E166's session end")" "X4c: --later-try rests from E166's own end, 5 minutes ago (v1 read only E163's, 60)"
ok "$([ -e "$SM/p16601/block.json" ] && echo 1 || echo 0)" "X4c: nothing moved"
echo "$("$GDATE" -d '-50 min' '+%F %T %Z') session end" > "$A3/build/e166/session.log"
case_ X4d 0 s11_a3_session.sh e166 --later-try
ok "$(has 'moved the earlier smoke aside: p16601 -> p16601.try1')" "X4d: 50 and 60 minutes of rest: the earlier smoke moved aside"
ok "$(has 'LAUNCHED e166')" "X4d: and the later try launched"
ok "$([ -e "$SM/p16601.try1/block.json" ] && [ ! -e "$SM/p16601" ] && echo 1 || echo 0)" "X4d: p16601.try1 holds the earlier smoke"

echo; echo "== X5. fault 2: a lost dry job"
J2=$A2/build/q141k/jobs/a2-dry-e167
rm -f "$J2.rc"; echo "true" > "$J2.sh"; echo "JOB-BEGIN a2-dry-e167 (stand-in)" > "$J2.out"; echo 4194301 > "$J2.pid"
case_ X5a 14 s15_a2_dry.sh e167 wait
ok "$(has '^JOB-LOST a2-dry-e167')" "X5a: JOB-LOST read"; ok "$(hasnot '^JOB-RUNNING')" "X5a: and no JOB-RUNNING line after it"
ok "$(fast 10)" "X5a: at once (the 2 s grace, not the 520 s loop)"
case_ X5a2 14 s15_a2_dry.sh e167 wait
case_v1 X5v1 17 s15_a2_dry.sh e167 wait
ok "$(has '^JOB-RUNNING')" "X5v1: v1's wait read the same lost job as still running: call again (the verifier's X5)"
rm -f "$J2.pid"
printf 'sleep 1\necho "$$" > "$1"\nexec sleep 3628\n' > "$T/late_pid.sh"
bash "$T/late_pid.sh" "$J2.pid" > /dev/null 2>&1 < /dev/null &
LP=$!
RB_WAIT_LOOP_S=5 case_ X5b 17 s15_a2_dry.sh e167 wait
ok "$(has '^JOB-RUNNING a2-dry-e167')" "X5b: a job whose pid comes a second late is still running, not lost"
kill "$LP" 2>/dev/null; wait "$LP" 2>/dev/null
stale "$J2.sh"
case_ X5c 10 s15_a2_dry.sh e167 wait
ok "$(has 'JOB-UNKNOWN a2-dry-e167: not started today')" "X5c: a job started on another day is not today's"
rm -f "$J2.sh" "$J2.out" "$J2.pid"; echo 0 > "$J2.rc"

echo; echo "== X6. nit 1: s09's config read waits for a session of ours"
mkdir -p "$T/fakesess/tools/claims-v3/e166"
printf 'sleep 3628\n' > "$T/fakesess/tools/claims-v3/e166/session_e166.sh"     # a session of ours: bash stays its parent
bash "$T/fakesess/tools/claims-v3/e166/session_e166.sh" > /dev/null 2>&1 < /dev/null &
FS=$!
sleep 1
rm -f "$H/guard-calls.txt"
case_ X6 10 s09_a3_reads.sh
ok "$(has 'REFUSED: a card session of ours runs on aifoundry3: the config read waits')" "X6: refused while a session of ours runs"
ok "$([ ! -e "$H/guard-calls.txt" ] && echo 1 || echo 0)" "X6: the guard was never called"
case_v1 X6v1 0 s09_a3_reads.sh
ok "$([ "$(wc -l < "$H/guard-calls.txt" 2>/dev/null | tr -d ' ')" = 1 ] && echo 1 || echo 0)" "X6v1: v1's s09 read the card through the guard beside the session (the verifier's X6)"
kill "$FS" 2>/dev/null; wait "$FS" 2>/dev/null; pkill -f 'sleep 3628' 2>/dev/null; true

echo; echo "== X7. fault 4: E167's collector reaches three boxes"
now=$(date +%s); fr=$((now - 3600)); to=$((now - 1800))
FAKE_PROBE_aifoundry1=link case_ X7a 11 s22_collect.sh e167 "$fr" "$to"
ok "$(lockline aifoundry1)" "X7a: aifoundry1's probe found the check: lock line for aifoundry1"
ok "$(grep -q '^rsync ' "$FAKE_LOG" && echo 0 || echo 1)" "X7a: the collector never ran"
FAKE_CALL_aifoundry3=link case_ X7b 11 s22_collect.sh e167 "$fr" "$to"
ok "$( [ "$(grep -c ' true$' "$FAKE_LOG")" -eq 3 ] && echo 1 || echo 0)" "X7b: three probes first (aifoundry1, aifoundry3, aifoundry2)"
ok "$(lockline aifoundry3)" "X7b: a link from aifoundry3's history read names aifoundry3 in the lock line"
ok "$(grep -q 'aifoundry2 needs a check' "$O/lock.txt" && echo 0 || echo 1)" "X7b: and not aifoundry2"
ok "$(grep -q ' aifoundry3 https://login.tailscale.com/a/desk-test-aifoundry3' "$O/links.txt" && echo 1 || echo 0)" "X7b: the links line names aifoundry3 and keeps the link"
ok "$(grep -q 'host=aifoundry2 link_host=aifoundry3 ' "$O/runbook.log" && echo 1 || echo 0)" "X7b: the log line says host=aifoundry2 link_host=aifoundry3"
ok "$(has 'a login check is needed on aifoundry3')" "X7b: the step's message names aifoundry3"
FAKE_CALL_aifoundry3=link case_v1 X7v1 11 s22_collect.sh e167 "$fr" "$to"
ok "$(lockline aifoundry2)" "X7v1: v1 wrote 'aifoundry2 needs a check' for aifoundry3's link (the verifier's fault 4)"
ok "$( [ "$(grep -c ' true$' "$FAKE_LOG")" -eq 1 ] && echo 1 || echo 0)" "X7v1: v1 probed one box"

echo; echo "== X8. fault 5: aifoundry2's firmware identity by continuity"
echo "2026-10-26 15:13:03" > "$T/state/boot"
case_ X8a 16 s14_a2_tree.sh
ok "$(grep -q '^IDENTITY-OK: the host booted 2026-10-26 15:13:03, before E69' "$O"/calls/*reads*.out && echo 1 || echo 0)" "X8a: the boot of record reads IDENTITY-OK"
ok "$(has 'does not read clean for:')" "X8a: so the step goes on to the runs' own checks (the stand-in box holds no kit: 16 there)"
ok "$(grep -q ' identity=1 ' "$O/a2-tree.txt" && echo 1 || echo 0)" "X8a: a2-tree.txt records identity=1"
echo "2026-11-01 09:00:00" > "$T/state/boot"
case_ X8b 16 s14_a2_tree.sh
ok "$(has "aifoundry2's firmware identity is not carried: IDENTITY-STOP: the host booted 2026-11-01 09:00:00, after E69")" "X8b: a later boot stops every aifoundry2 run"
ok "$(grep -q ' identity=0 ' "$O/a2-tree.txt" && echo 1 || echo 0)" "X8b: a2-tree.txt records identity=0"
case_v1 X8v1 16 s14_a2_tree.sh
ok "$(grep -qi 'identity' "$O/stdout.txt" && echo 0 || echo 1)" "X8v1: v1 printed the later boot and checked nothing (its stop is the runs' own checks)"
rm -f "$T/state/boot"

echo; echo "== X9. nit 5: another day's state is never today's"
for r in e165 e167 e168 e169; do stale "$A2/build/q141k/jobs/a2-dry-$r.rc"; done
case_ X9a 10 s16_a2_e165.sh full
ok "$(has 'REFUSED: the dry pass of e165 has not ended rc 0 today')" "X9a: dry passes that ended rc 0 on another day do not admit E165"
for r in e165 e167 e168 e169; do echo 0 > "$A2/build/q141k/jobs/a2-dry-$r.rc"; done
stale "$A3/build/q141k/e166.log-offset"
case_ X9b 10 s20_wait.sh e166
ok "$(has 'RUN-UNKNOWN e166: not launched today')" "X9b: a log offset from another day: not launched today"
case_v1 X9v1 0 s20_wait.sh e166
ok "$(has 'e166 has ended')" "X9v1: v1 read that day's 'session end' as today's (the verifier's nit 5)"
case_ X9c 10 s11_a3_session.sh e163 FULL
ok "$(has 'REFUSED: E166 has not run today')" "X9c: E163 waits for an E166 launched today, not another day's"
stale "$A2/build/e165/runs/status.json"
case_ X9d 10 s20_wait.sh e165
ok "$(has 'RUN-UNKNOWN e165: no queue process and no status.json written today')" "X9d: a queue status from another day: not launched today"
"$GTOUCH" "$A3/build/q141k/e166.log-offset" "$A2/build/e165/runs/status.json"

echo; echo "== X10. nit 2: E163's plan must end by the last end"
cat > "$T/win.py" <<'PY'
import sys, time
now = int(time.time()); a, b = now + 1800, now + 3600
fmt = lambda e: time.strftime("%Y-%m-%d %H:%M %Z", time.localtime(e))
q = lambda s: s.replace(" ", "\\ ")
print(f"RB_DAY={time.strftime('%Y-%m-%d', time.localtime(a))}\nRB_LAST_START={q(fmt(a))}\nRB_LAST_END={q(fmt(b))}\n"
      f"RB_LAST_START_EPOCH={a}\nRB_LAST_END_EPOCH={b}\nRB_LAST_START_HM={time.strftime('%H:%M', time.localtime(a))}\n"
      f"RB_LAST_END_HM={time.strftime('%H:%M', time.localtime(b))}\nRB_E164_DEADLINE={q(fmt(b - 600))}\nRB_PLAN=a\nRB_GO_EPOCH={now}")
PY
TZ=America/Los_Angeles /usr/bin/python3 -I "$T/win.py" > "$T/window-near.env"
CASE_WINDOW=$T/window-near.env case_ X10a 16 s11_a3_session.sh e163 FULL
ok "$(has "70 more minutes would pass the round's last end")" "X10a: FULL refused with 60 minutes to the last end"
ok "$( [ ! -s "$FAKE_LOG" ] && echo 1 || echo 0)" "X10a: before any call"
CASE_WINDOW=$T/window-near.env case_ X10b 0 s11_a3_session.sh e163 TWO
ok "$(has 'LAUNCHED e163 .*plan TWO')" "X10b: TWO, 38 minutes, launched"
CASE_WINDOW=$T/window-near.env case_v1 X10v1 0 s11_a3_session.sh e163 FULL
ok "$(has 'LAUNCHED e163 .*plan FULL')" "X10v1: v1 launched FULL with 60 minutes left (the verifier's nit 2)"

echo; echo "== V. the files v2 keeps from v1"
for f in s01_probe.sh s02_window.sh s03_desk.sh s05_look.sh s07_a3_sync.sh s08_a3_preflight.sh s10_a3_dry.sh s15_a2_dry.sh s17_a2_e167.sh \
         list_steps.sh frozen26.py anchors_e165.py; do
  ok "$(cmp -s "$V1/$f" "$D/$f" && echo 1 || echo 0)" "V: v2/$f is byte for byte v1's"
done

echo; echo "== E. the dry listing"
: > "$FAKE_LOG"
O=$T/out-E; mkdir -p "$O/run"
env -u RB_REPO bash "$D/list_steps.sh" "$O/run" > "$O/listing.txt" 2>&1; RC=$?    # the listing reads the real clone's paths
ok "$([ "$RC" = 0 ] && echo 1 || echo 0)" "E: list_steps.sh exits 0"
ok "$( [ ! -s "$FAKE_LOG" ] && echo 1 || echo 0)" "E: not one ssh or rsync call ($(wc -l < "$FAKE_LOG" | tr -d ' ') recorded)"
ne=$(grep -c '^(exit 0)$' "$O/listing.txt"); nx=$(grep -c '^(exit ' "$O/listing.txt")
ok "$([ "$ne" -eq "$nx" ] && [ "$ne" -ge 50 ] && echo 1 || echo 0)" "E: every step listed and exits 0 ($ne of $nx)"
for k in "aifoundry1 \"bash -s -- '" "< tools/claims-v3/e164/box/launch_e164_a1.sh" "E164_S_RECOUNT=docs/reports/data/2026-11-04-q141t-s7-recount/arm/arm27-aifoundry1c1.json" \
         "tools/claims-v3/dmcmd_table.json tools/claims-v3/e166/ aifoundry3:aifoundry/" "anchors_e165.py" "--e165-anchors" "reduce_e168.py" "--anchors" \
         "build/e168/runs/" "build/e169/runs/" "collect_e165_bounded.sh" "collect_e167_bounded.sh" "latch_check_e167.py" "run_e167.sh dry" \
         "build/e169/dry" "QUEUE-STOP" "score_rank4.py" "score_s7arm_a1.py" "arm27-aifoundry3.json" \
         "GUARD-OK" "job_ok_today a1-check" "IDENTITY-OK" "2026-10-27 13:56:26 PDT" "names its own box in the lock line" "probe aifoundry1, hard-killed" \
         "REFUSED: an earlier E166 smoke is on the box" "fresh build/q141k/e166.log-offset" "gate: now + 70 min" "_v2] dry listing"; do
  ok "$(grep -qF -- "$k" "$O/listing.txt" && echo 1 || echo 0)" "E: the listing holds: $k"
done
ok "$(grep -qE 'box/launch_e164\.sh([^_]|$)' "$O/listing.txt" && echo 0 || echo 1)" "E: box/launch_e164.sh (it would run 0 passes) is never sent"
ok "$(grep -qE '/Use[r]s/|/home/[a-z]' "$O/listing.txt" && echo 0 || echo 1)" "E: no home path in the listing"
rm -rf "${D:?}/__pycache__"
pgrep -f 'sleep 3628' > /dev/null && { pkill -f 'sleep 3628'; echo "note: a 3628 stand-in was still running at the end (killed)"; }
echo; echo "$((n - fails)) of $n checks pass"
[ "$fails" -eq 0 ] && echo "ALL PASS" || echo "$fails FAIL"
exit $([ "$fails" -eq 0 ] && echo 0 || echo 1)
