#!/usr/bin/env bash
# Q141(k): the runbook's desk test. It never reaches a lab box: a stand-in `ssh` and `rsync`, first on PATH in the scratch dir, take
# every call. The stand-in ssh answers the probe (`true`) and, for a remote script, runs it in a stand-in box (a scratch HOME holding
# ~/aifoundry, ~/nekko and ~/claude/et-soc1-prototyping, with stub et-who, who, uptime, sudo, setsid and a GNU date on PATH), or hangs,
# or prints a Tailscale check link and hangs, or fails, as the case sets. RB_REPO is a scratch git repo holding E164's box scripts
# (the committed launch_e164_a1.sh, look_e164.sh and wait_e164.sh run in the stand-in box unchanged). Desk only, on the Intel:
#
#   bash tools/claims-v3/q141k-runbook/selftest_runbook.sh <a new, empty scratch dir> > tools/claims-v3/q141k-runbook/logs/selftest.txt
#
# The cases: (A) success: probes, his window, look-first FREE, a held card polled until free, a held card skipped after 30 minutes
# in all, the one rsync, a detached dry job and its bounded wait, E164's launch with its whole deadline, E165's slot and queue, a
# wait that reads the end; (B) a login link and then a hang: at the probe, on a call's stderr, on a call's stdout, on rsync, on all
# three probes: killed at once, the lock line appended, the link kept; (C) a hang with no output: the probe killed at 15 s, a read,
# a copy, a launch and a wait each killed at its bound; (D) a non-zero exit: a call, rsync, ssh's own 255 at the probe, and the
# kit launcher's own refusal on a card-1 holder; (E) the dry listing: every step, and not one ssh or rsync call. After every case:
# no stand-in process is left running, and no stand-in login appears in any file the runbook wrote.
# SPDX-License-Identifier: Apache-2.0
set -u
T=${1:?usage: selftest_runbook.sh <a new, empty scratch dir>}
[ -d "$T" ] && [ -n "$(ls -A "$T" 2>/dev/null)" ] && { echo "refused: $T is not empty"; exit 2; }
D=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
LAB=$(cd "$D/../../.." && pwd)
mkdir -p "$T/bin" "$T/stubs" "$T/home" "$T/state" "$T/repo" || exit 2
T=$(cd "$T" && pwd -P)
GDATE=$(command -v gdate || command -v date)

# ---- the stand-in ssh: it never connects anywhere ----------------------------------------------------------------------------
cat > "$T/bin/ssh" <<'EOS'
#!/bin/bash
[ -n "${FAKE_LOG:-}" ] && [ -n "${FAKE_HOME:-}" ] || { echo "stand-in ssh: not inside the desk test" >&2; exit 255; }
echo "ssh $*" >> "$FAKE_LOG"
while [ $# -gt 0 ]; do case "$1" in -o|-p|-i|-l|-F) shift 2 ;; -*) shift ;; *) break ;; esac; done
host=$1; shift
case "$host" in aifoundry1|aifoundry2|aifoundry3) ;; *) echo "stand-in ssh: unexpected host $host" >&2; exit 255 ;; esac
if [ "$*" = true ]; then mode=${FAKE_PROBE:-ok}; else mode=${FAKE_CALL:-ok}; fi
case "$mode" in
  ok) ;;
  link) echo "# Tailscale SSH requires an additional check." >&2
        echo "# To authenticate, visit: https://login.tailscale.com/a/desk-test-only" >&2; exec sleep 3617 ;;
  link-stdout) echo "To authenticate, visit: https://login.tailscale.com/a/desk-test-stdout"; exec sleep 3617 ;;
  hang) exec sleep 3617 ;;
  fail) echo "stand-in ssh: the remote command failed" >&2; exit 7 ;;
  refuse) echo "ssh: connect to host $host port 22: Connection refused" >&2; exit 255 ;;
esac
[ "$*" = true ] && exit 0
cd "$FAKE_HOME" || exit 255
# as a real ssh does: the words joined into one command line, split again by the box's shell, and the script on stdin through a
# pipe (ssh's channel), never the seekable file itself: a detached child forked from a script read off a seekable file moves
# bash's read offset and lines run twice (E164 README.md.dated-note.md, "The emulation")
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
  link) echo "# To authenticate, visit: https://login.tailscale.com/a/desk-test-rsync" >&2; exec sleep 3617 ;;
  hang) exec sleep 3617 ;;
  fail) echo "rsync error: some files could not be transferred (code 23)" >&2; exit 23 ;;
esac
EOS
# ---- the stand-in box's commands ---------------------------------------------------------------------------------------------
printf '#!/bin/bash\nexec %s "$@"\n' "$GDATE" > "$T/stubs/date"
printf '#!/bin/bash\nexec "$@"\n' > "$T/stubs/setsid"
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
printf '#!/bin/bash\n[ "${1:-}" = -s ] && { echo "2026-10-26 09:00:00"; exit 0; }\necho " 10:00:00 up 9 days,  2 users,  load average: 0.50, 0.40, 0.30"\n' > "$T/stubs/uptime"
printf '#!/bin/bash\necho "host         stand-in box (desk test)"\n' > "$T/stubs/et-lab-manifest"
chmod +x "$T/bin/"* "$T/stubs/"*
# ---- the stand-in box's trees ------------------------------------------------------------------------------------------------
H=$T/home
mkdir -p "$H/aifoundry/build" "$H/nekko/tools/claims-v3/e164/box" "$H/nekko/build" "$H/claude/work" "$H/live/history" \
  "$H/claude/et-soc1-prototyping/tools/claims-v3/e165" "$H/claude/et-soc1-prototyping/build/q141k/jobs"
printf 'print("HARNESS OK: 107 files match harness-e164.json")\n' > "$H/nekko/tools/claims-v3/e164/check_e164.py"
cat > "$H/nekko/tools/claims-v3/e164/session_e164.sh" <<'EOS'
mkdir -p build/e164
env | grep '^E164_' | sort > build/e164/session-env.txt
echo "$(date '+%F %T %Z') session start (stand-in)" >> build/e164/session.log
echo "$(date '+%F %T %Z') session end" >> build/e164/session.log
EOS
cat > "$H/nekko/tools/claims-v3/e164/box/check_box_e164.sh" <<'EOS'
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
cat > "$H/claude/et-soc1-prototyping/tools/claims-v3/e165/queue_e165.py" <<'EOS'
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
for r in e165 e167 e168 e169; do echo 0 > "$H/claude/et-soc1-prototyping/build/q141k/jobs/a2-dry-$r.rc"; done
# ---- the scratch repo (RB_REPO): E164's committed box scripts, unchanged ------------------------------------------------------
mkdir -p "$T/repo/tools/claims-v3/e164/box"
for f in look_e164.sh launch_e164_a1.sh wait_e164.sh; do cp "$LAB/tools/claims-v3/e164/box/$f" "$T/repo/tools/claims-v3/e164/box/"; done
( cd "$T/repo" && git init -q && git add -A && git -c user.name=desk-test -c user.email=desk-test commit -q -m "desk test" ) || exit 2

export PATH="$T/bin:$PATH" FAKE_LOG="$T/calls.txt" FAKE_HOME="$H" FAKE_STUBS="$T/stubs" FAKE_STATE="$T/state" RB_REPO="$T/repo"
[ "$(command -v ssh)" = "$T/bin/ssh" ] && [ "$(command -v rsync)" = "$T/bin/rsync" ] || { echo "refused: the stand-ins are not first on PATH"; exit 2; }
DAY=$(/usr/bin/python3 -c 'import datetime; print(datetime.date.today() + datetime.timedelta(days=2))')
echo "# Q141(k) runbook desk test: $(date '+%a %d %b %Y %H:%M:%S %Z'); ssh and rsync on PATH are the stand-ins; the window's day $DAY (sample)"
fails=0; n=0
ok() { n=$((n + 1)); if [ "$1" = 1 ]; then echo "ok   $2"; else echo "FAIL $2"; fails=$((fails + 1)); fi; }
left() { pgrep -f 'sleep 3617' > /dev/null && { pkill -f 'sleep 3617'; echo yes; } || echo no; }
case_() {  # case_ <name> <expected rc> <step> [args...]: run one step with a fresh RB_OUT; sets RC, SECS, O
  local name=$1 want=$2; shift 2
  O=$T/out-$name; mkdir -p "$O"
  [ -f "$T/window.env" ] && cp "$T/window.env" "$O/window.env"
  : > "$FAKE_LOG"
  local t0 t1; t0=$("$GDATE" +%s.%N)
  RB_OUT=$O RB_LOCK=$O/lock.txt bash "$D/$1" "${@:2}" > "$O/stdout.txt" 2>&1
  RC=$?
  t1=$("$GDATE" +%s.%N)
  SECS=$(/usr/bin/python3 -c "import sys; print(round(float(sys.argv[2]) - float(sys.argv[1]), 1))" "$t0" "$t1")
  ok "$([ "$RC" = "$want" ] && echo 1 || echo 0)" "$name: $1 ${*:2} -> exit $RC (want $want) in $SECS s"
  ok "$([ "$(left)" = no ] && echo 1 || echo 0)" "$name: no stand-in process left running"
  ok "$(grep -rqs 'zz_other_user' "$O" && echo 0 || echo 1)" "$name: no stand-in login in any file the runbook wrote"
}
lockline() { grep -qE "^[0-2][0-9]:[0-5][0-9]:[0-5][0-9] $1 needs a check$" "$O/lock.txt" 2>/dev/null && echo 1 || echo 0; }
fast() { /usr/bin/python3 -c "import sys; sys.exit(0 if float(sys.argv[1]) < float(sys.argv[2]) else 1)" "$SECS" "$1" && echo 1 || echo 0; }
between() { /usr/bin/python3 -c "import sys; sys.exit(0 if float(sys.argv[2]) <= float(sys.argv[1]) <= float(sys.argv[3]) else 1)" "$SECS" "$1" "$2" && echo 1 || echo 0; }

echo; echo "== A. success"
case_ A1 0 s01_probe.sh
ok "$( [ "$(grep -c 'class=probe .*rc=0 .*status=ok' "$O/runbook.log")" -eq 3 ] && echo 1 || echo 0)" "A1: three probe lines in the log, each rc=0 status=ok"
case_ A2 0 s02_window.sh "$DAY" 15:30 16:30 full
cp "$O/window.env" "$T/window.env"
ok "$(grep -q "^RB_E164_DEADLINE=.*$DAY\\\\ 16:20\\\\ P[SD]T" "$T/window.env" && echo 1 || echo 0)" "A2: the window holds E164's deadline, the last end less 10 minutes"
case_ A3 0 s05_look.sh aifoundry3
ok "$(grep -q '^HOLDER-RULE: FREE' "$O"/calls/*.out && grep -q 'logins 2 (an idle login does not block)' "$O"/calls/*.out && echo 1 || echo 0)" "A3: FREE with two idle logins (they do not block)"
echo 2 > "$T/state/etwho-held"
RB_HOLD_POLL_S=1 RB_WAIT_LOOP_S=20 case_ A4 0 s05_look.sh aifoundry2 --wait
ok "$(grep -q '^HOLDER-RULE: FREE after [0-9]* s of polls' "$O"/calls/*.out && echo 1 || echo 0)" "A4: a held card polled on the box until free"
echo 999 > "$T/state/etwho-held"
RB_HOLD_POLL_S=1 RB_WAIT_LOOP_S=2 case_ A5a 17 s05_look.sh aifoundry2 --wait
cp "$O/hold-aifoundry2.since" "$T/since" 2>/dev/null; echo $(( $(date +%s) - 1810 )) > "$T/since"
mkdir -p "$T/out-A5b"; cp "$T/since" "$T/out-A5b/hold-aifoundry2.since"
RB_HOLD_POLL_S=1 RB_WAIT_LOOP_S=2 case_ A5b 15 s05_look.sh aifoundry2 --wait
rm -f "$T/state/etwho-held"
case_ A6 0 s07_a3_sync.sh
ok "$(grep -q -- '-a -c -R --exclude __pycache__ -e ssh -o BatchMode=yes -o ConnectTimeout=10 tools/claims-v3/e163/ .* tools/claims-v3/e166/ aifoundry3:aifoundry/' "$FAKE_LOG" && echo 1 || echo 0)" "A6: one rsync with E163's step-4 paths and tools/claims-v3/e166/ to aifoundry3:aifoundry/"
case_ A7a 0 s12_a1_check.sh start
case_ A7b 0 s12_a1_check.sh wait
ok "$(grep -q '^JOB-DONE a1-check rc=0$' "$O"/calls/*.out && echo 1 || echo 0)" "A7: the detached check job ended rc 0 and its lines read clean"
case_ A8 0 s13_a1_launch.sh
ok "$(grep -qx "E164_DEADLINE=$DAY 16:20 P[SD]T" "$H/nekko/build/e164/session-env.txt" && echo 1 || echo 0)" "A8: the session got the whole deadline through ssh ('$DAY 16:20 PST', not the date alone)"
ok "$(grep -q "\"bash -s -- '$DAY 16:20 P[SD]T'\"" "$FAKE_LOG" 2>/dev/null || grep -q "bash -s -- '$DAY 16:20 P[SD]T'" "$FAKE_LOG" && echo 1 || echo 0)" "A8: launch_e164_a1.sh's usage line, the quoting inside the remote command"
case_ A9 0 s16_a2_e165.sh full
cat > "$T/slot_check.py" <<'PY'
import re, sys
m = re.search(r"SLOT E165: start (\d+) .*?end (\d+) ", open(sys.argv[1]).read())
sys.exit(0 if m and int(m.group(2)) - int(m.group(1)) == 2700 else 1)
PY
ok "$(/usr/bin/python3 "$T/slot_check.py" "$H/claude/work/q141-a2-e165-slot.txt" && echo 1 || echo 0)" "A9: E165's slot line parses by the queue's own pattern, 2,700 s"
ok "$(grep -qx -- '--slots .*/claude/work/q141-a2-e165-slot.txt --runs build/e165/runs --cap 40' "$H/claude/et-soc1-prototyping/build/e165/runs/argv.txt" 2>/dev/null || grep -q -- '--runs build/e165/runs --cap 40' "$H/claude/et-soc1-prototyping/build/e165/runs/argv.txt" && echo 1 || echo 0)" "A9: the queue started with --runs build/e165/runs --cap 40"
case_ A10 0 s20_wait.sh e165
touch "$T/state/etwho-card1"
case_ A11 17 s05_look.sh aifoundry1
ok "$(grep -q '^/dev/et1_ops *<holder> *4243 *00:10:00 <command withheld>$' "$O"/calls/*.out && echo 1 || echo 0)" "A11: look_e164.sh's raw et-who line kept with its login and command masked"
ok "$(grep -q 'identity: the host booted .*: ok' "$O"/calls/*.out && echo 1 || echo 0)" "A11: look_e164.sh's identity line read (booted before E82's firmware read)"
rm -f "$T/state/etwho-card1"

echo; echo "== B. a login link, then a hang"
FAKE_PROBE=link case_ B1 11 s05_look.sh aifoundry2
ok "$(lockline aifoundry2)" "B1: '<HH:MM:SS> aifoundry2 needs a check' appended to the lock file"
ok "$(grep -q 'https://login.tailscale.com/a/desk-test-only' "$O/links.txt" && echo 1 || echo 0)" "B1: the link kept in RB_OUT/links.txt for the approval"
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
FAKE_CALL=hang RB_LAUNCH_S=3 case_ C4 13 s13_a1_launch.sh
ok "$(between 2.5 8)" "C4: a launch killed at its bound (60 s; 3 s here)"
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
ok "$(grep -q "REFUSED: card 1's nodes or lock are held: nothing launched" "$O/stdout.txt" && echo 1 || echo 0)" "D4: launch_e164_a1.sh's own refusal (exit 3) on a card-1 holder, reported"
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
ok "$([ "$r" = 0 ] && /usr/bin/python3 -B "$T/f2/cmp.py" "$T/f2" && echo 1 || echo 0)" "F2: anchors_e165.py writes score.anchors and score.anchor_delta unchanged"
echo '{"score": {"note": "fewer than 2 governed passes: every rule NOT SCORED"}}' > "$T/f3/results.json"
/usr/bin/python3 -B "$D/anchors_e165.py" "$T/f3" > "$T/f3/out.txt"; r=$?
ok "$([ "$r" = 3 ] && [ ! -e "$T/f3/anchors-for-e167-e168.json" ] && echo 1 || echo 0)" "F3: a NOT SCORED E165 writes no anchors file (exit 3)"
cat > "$T/near.py" <<'PY'
import datetime
a = datetime.datetime.now() + datetime.timedelta(minutes=40)
b = datetime.datetime.now() + datetime.timedelta(minutes=90)
print(a.date().isoformat(), a.strftime("%H:%M"), b.strftime("%H:%M"), "same" if a.date() == b.date() else "cross")
PY
/usr/bin/python3 -B "$T/near.py" > "$T/near.txt"
read -r nd na nb same < "$T/near.txt"
if [ "$same" = same ]; then
  cp "$T/window.env" "$T/window.env.keep"; rm -f "$T/window.env"
  case_ F4 16 s02_window.sh "$nd" "$na" "$nb" full
  ok "$(grep -q 'plans that fit: none' "$O/stdout.txt" && echo 1 || echo 0)" "F4: a window under 1 h 45 min fits no plan"
  cp "$T/window.env.keep" "$T/window.env"
else
  echo "skip F4: the near window would cross midnight"
fi
case_ F5 10 s17_a2_e167.sh go 14:30 13:10 15:00 16:00
ok "$(grep -q 'smoke-not-before <= smoke-latest < no-start-after < cutoff' "$O/stdout.txt" && echo 1 || echo 0)" "F5: E167's four gates out of order are refused before any call"
ok "$( [ ! -s "$FAKE_LOG" ] && echo 1 || echo 0)" "F5: no ssh before the gates are read"
case_ F6 16 s17_a2_e167.sh go 13:00 13:30 16:00 16:30
ok "$(grep -q "no-start-after 16:00 is past the round's last start 15:30" "$O/stdout.txt" && echo 1 || echo 0)" "F6: a no-start-after past the window's last start is refused"

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
         "build/e169/dry" "QUEUE-STOP" "score_rank4.py" "score_s7arm_a1.py" "arm27-aifoundry3.json"; do
  ok "$(grep -qF -- "$k" "$O/listing.txt" && echo 1 || echo 0)" "E: the listing holds: $k"
done
ok "$(grep -qE 'box/launch_e164\.sh([^_]|$)' "$O/listing.txt" && echo 0 || echo 1)" "E: box/launch_e164.sh (it would run 0 passes) is never sent"
ok "$(grep -qE '/Use[r]s/|/home/[a-z]' "$O/listing.txt" && echo 0 || echo 1)" "E: no home path in the listing"
echo; echo "$((n - fails)) of $n checks pass"
[ "$fails" -eq 0 ] && echo "ALL PASS" || echo "$fails FAIL"
exit $([ "$fails" -eq 0 ] && echo 0 || echo 1)
