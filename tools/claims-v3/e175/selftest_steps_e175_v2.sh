#!/usr/bin/env bash
# selftest_steps_e175_v2.sh (Q143(g) fix pass, Thu 5 Nov 2026, week 45, PST; tools/claims-v3/e175/README.md.dated-note-1.md): v1
# (selftest_steps_e175.sh, lab 16b3d6e3) with one change, its verifier's nit: v1's clean() ran `pkill -f 'sleep 3651'` and none_left()
# `pgrep -f 'sleep 3651'` machine-wide, so beside another agent's test of the same form it could kill that test's stand-ins or count them
# as its own. Here every hang of the stand-in ssh runs under this run's own name (`exec -a e175v2-standin-<tag> sleep 3651`, the tag
# from the clock and this shell's pid), and clean() and none_left() match only that name, which no other process carries (and v1's
# pattern, 'sleep 3651', no longer matches this run's stand-ins either). A new case V0 shows that the name is what pgrep sees; before
# each clean, the stand-ins of this run still alive are counted and printed as information (rb_run.py's own kill should leave none).
# Every other line, case and bound is v1's.
#
# E175 (Q143(g)): the desk test of E175's step driver (tools/claims-v3/e175/box/step_e175_v3.sh, over the q142kg runbook's rb_common_v3.sh,
# s02_window_q142kg.sh and cclist_q142kg_v3.py, all unchanged), in the q142kg runbook's own test form (selftest_steps_q142kg.sh, lab 5a2a9ba0).
# It never reaches a lab box: a stand-in `ssh` and `rsync`, first on PATH in the scratch dir, take every call. The stand-in ssh answers the probe
# (`true`) and, for a remote script, saves the script and prints a fixture the case names, or hangs, or prints a login-check link and hangs
# (FAKE_PROBE, FAKE_CALL, FAKE_FIXTURE, FAKE_RC); the stand-in rsync copies nothing. The bounds are shortened with v3.1's desk-test overrides
# (RB_<CLS>_S). The cases:
#   W    s02_window_q142kg.sh writes a future window
#   A    the dry listing (RB_DRY=1) of every step: exit 0, and the stand-ins log no call; collect lists the collector, v3's list, the C-check gate
#        and the desk-path gate
#   B    look: FREE (0), the identity stop (16), a held card (17); the remote script carries ours_live
#   C    a login link at the probe: 11, the lock line "<HH:MM:SS> aifoundry2 needs a check" appended
#   D    a hang with no output: the probe (12) and a call past its bound (13)
#   E    launch: E175's window gate refusing on the box (10); the identity stop (16); the launch line (0); past the day's last start (16, no call);
#        the launch's remote script carries the after-E173 gate with AFTER=600 and the dry pass's job check
#   G    the after-E173 gate's own lines, run in a made-up box tree (a stand-in `stat` for GNU's -c %Y, which the box has and macOS lacks): no E173
#        record today (ok); E173 ended 30 s ago (refused); ended 700 s ago (ok); halted 700 s ago (ok); a status that reads running (refused); a
#        live queue_e173.py process (refused)
#   F    wait: ended (0), still running (17), halted at a gate (16)
#   I    the C-log gate (rb_cc_gate with v3's list and v3.1's ccdone_q142s.py) on made-up data directories: every listed session carries a C log
#        and a finished check (0); a listed session without a C log (14); a resume s2 with a work launch but no check (14)
# After every case no stand-in process is left running.
#
#   bash tools/claims-v3/e175/selftest_steps_e175_v2.sh <a new, empty scratch dir> > tools/claims-v3/e175/logs/selftest-steps-v2.txt
# SPDX-License-Identifier: Apache-2.0
set -u
T=${1:?usage: selftest_steps_e175_v2.sh <a new, empty scratch dir>}
[ -d "$T" ] && [ -n "$(ls -A "$T" 2>/dev/null)" ] && { echo "refused: $T is not empty"; exit 2; }
mkdir -p "$T/bin" "$T/fix" || exit 2
D=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
REPO=$(cd "$D/../../.." && pwd)
KG="$REPO/tools/claims-v3/q142kg-runbook"
S175="$D/box/step_e175_v3.sh"
FAKE_L="login.tail""scale.com"
export FAKE_L FAKE_LOG="$T/calls.log"
STANDIN_NAME="e175v2-standin-$(date +%s)$$"   # v2: this run's own name for the stand-in's hangs (letters, digits and dashes only)
export STANDIN_NAME
cat > "$T/bin/ssh" <<'EOS'
#!/bin/bash
echo "$(date +%s) ssh $*" >> "$FAKE_LOG"
last="${!#}"
if [ "$last" = true ]; then
  case "${FAKE_PROBE:-ok}" in
    ok) exit 0 ;;
    link) echo "# To authenticate, visit: https://$FAKE_L/a/desk-test-probe" >&2; exec -a "$STANDIN_NAME" sleep 3651 ;;
    hang) exec -a "$STANDIN_NAME" sleep 3651 ;;
  esac
fi
cat > "${FAKE_STDIN:-/dev/null}"
case "${FAKE_CALL:-ok}" in
  ok) [ -n "${FAKE_FIXTURE:-}" ] && cat "$FAKE_FIXTURE"; exit "${FAKE_RC:-0}" ;;
  link) echo "# To authenticate, visit: https://$FAKE_L/a/desk-test-call" >&2; exec -a "$STANDIN_NAME" sleep 3651 ;;
  hang) exec -a "$STANDIN_NAME" sleep 3651 ;;
esac
EOS
cat > "$T/bin/rsync" <<'EOS'
#!/bin/bash
echo "$(date +%s) rsync $*" >> "$FAKE_LOG"
exit 0
EOS
chmod +x "$T/bin/ssh" "$T/bin/rsync"
export PATH="$T/bin:$PATH"
N=0; F=0
ok() { N=$((N + 1)); if [ "$1" = 1 ]; then echo "PASS $2"; else F=$((F + 1)); echo "FAIL $2"; fi; }
clean() { pkill -f "$STANDIN_NAME" 2>/dev/null; sleep 0.2; }      # v2: only this run's stand-ins
none_left() { pgrep -f "$STANDIN_NAME" > /dev/null && echo 0 || echo 1; }   # v2: only this run's stand-ins
run() {  # run <name> <expected rc> <env...> -- <script> <args...>: one step in its own RB_OUT; prints its rc
  local name=$1 want=$2; shift 2
  local envs=()
  while [ "$1" != -- ]; do envs+=("$1"); shift; done; shift
  mkdir -p "$T/out-$name"
  [ -f "$T/window-q142kg.env" ] && cp "$T/window-q142kg.env" "$T/out-$name/"
  env RB_OUT="$T/out-$name" RB_LOCK="$T/lock-$name.txt" FAKE_STDIN="$T/out-$name/stdin.sh" ${envs[@]+"${envs[@]}"} bash "$@" > "$T/out-$name/result.txt" 2>&1
  local rc=$?
  echo "$rc" > "$T/out-$name/rc"
  local alive; alive=$(pgrep -f "$STANDIN_NAME" | wc -l | tr -d ' ')   # v2, information: this run's stand-ins alive when the step returned
  [ "$alive" != 0 ] && echo "$name:$alive" >> "$T/alive-before-clean.txt"
  clean
  [ "$rc" = "$want" ] && return 0 || { echo "     ($name: rc $rc, wanted $want; last lines: $(tail -n 2 "$T/out-$name/result.txt" | tr '\n' ' ' | cut -c1-240))"; return 1; }
}
calls() { [ -f "$FAKE_LOG" ] && wc -l < "$FAKE_LOG" | tr -d ' ' || echo 0; }
cd "$REPO" || exit 2

# ---- V0 (v2): the stand-in's hang runs under this run's own name, so clean() and none_left() see only this run's stand-ins
cat > "$T/v0.py" <<'EOP'
import subprocess, sys, time
p = subprocess.Popen([sys.argv[1], "v0-desk-test", "true"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
time.sleep(0.5)
q = subprocess.run(["pgrep", "-f", sys.argv[2]], capture_output=True, text=True).stdout.split()
p.terminate()
try:
    p.wait(5)
except subprocess.TimeoutExpired:
    p.kill()
    p.wait()
print(1 if q == [str(p.pid)] else 0)
EOP
v0=$(FAKE_PROBE=hang python3 -I "$T/v0.py" "$T/bin/ssh" "$STANDIN_NAME")
ok "$v0" "V0 (v2) the stand-in's hang runs under this run's own name: pgrep -f finds exactly its pid, and nothing else carries the name"
ok "$(none_left)" "V0 (v2) and it is gone after its kill"

# ---- W: the window, a future one
day=$(TZ=America/Los_Angeles date -v+1d +%F 2>/dev/null || TZ=America/Los_Angeles date -d tomorrow +%F)
env RB_OUT="$T/w" RB_LOCK="$T/lock-w.txt" bash "$KG/s02_window_q142kg.sh" "$day" 21:00 22:00 > "$T/w.txt" 2>&1
ok "$([ $? = 0 ] && grep -q '^RB_LAST_END_EPOCH=' "$T/w/window-q142kg.env" && echo 1 || echo 0)" "W  s02_window_q142kg.sh writes the window (last start 21:00, last end 22:00, tomorrow)"
cp "$T/w/window-q142kg.env" "$T/window-q142kg.env"

# ---- A: the dry listing of every step
c0=$(calls)
a=1
for s in look tree "dry start" "dry wait" launch "launch subset" wait collect; do
  # shellcheck disable=SC2086
  run "A-${s// /-}" 0 RB_DRY=1 -- "$S175" $s || a=0
done
ok "$a" "A  the dry listing of all 8 steps exits 0"
ok "$([ "$(calls)" = "$c0" ] && echo 1 || echo 0)" "A  the dry listing called no ssh and no rsync"
ok "$(grep -q 'collect_e175_bounded.sh' "$T/out-A-collect/result.txt" && grep -q 'cclist_q142kg_v3.py' "$T/out-A-collect/result.txt" \
      && grep -q 'ccdone_q142s.py' "$T/out-A-collect/result.txt" && grep -qE 'nopath_q142s.py|no desk path' "$T/out-A-collect/result.txt" && echo 1 || echo 0)" \
   "A  collect lists its collector, v3's C-log list, the C-check gate and the desk-path gate"
ok "$(grep -q 'protocol-subset.json' "$T/out-A-launch-subset/result.txt" && grep -q 'SLOT=1860; CAP=25' "$T/out-A-launch-subset/result.txt" \
      && grep -q 'SLOT=2880; CAP=42' "$T/out-A-launch/result.txt" && echo 1 || echo 0)" \
   "A  launch lists the full plan (48-minute slot, cap 42) and the subset (31-minute slot, cap 25)"

# ---- B: look
printf 'IDENTITY-OK: the host booted 2026-10-26 15:13:03, before ...\nholders: ...\nHOLDER-RULE: FREE\n' > "$T/fix/look-free.txt"
printf 'IDENTITY-STOP: the host booted 2026-11-05 01:00:00, after ...\nHOLDER-RULE: FREE\n' > "$T/fix/look-idstop.txt"
printf 'IDENTITY-OK: ...\nHOLDER-RULE: HELD\n' > "$T/fix/look-held.txt"
run B1 0 FAKE_FIXTURE="$T/fix/look-free.txt" -- "$S175" look; ok "$([ $? = 0 ] && echo 1 || echo 0)" "B1 look, a free card: 0"
ok "$(grep -q 'ours_live' "$T/out-B1/stdin.sh" && grep -q 'queue|run)_e17\[0-9\]' "$T/out-B1/stdin.sh" && echo 1 || echo 0)" \
   "B1 the remote script carries the q142kg prelude's ours_live (queue_e175.py and run_e175.py match its pattern)"
run B2 16 FAKE_FIXTURE="$T/fix/look-idstop.txt" -- "$S175" look; ok "$([ $? = 0 ] && echo 1 || echo 0)" "B2 look, a host booted after E69's read: 16"
run B3 17 FAKE_FIXTURE="$T/fix/look-held.txt" -- "$S175" look; ok "$([ $? = 0 ] && echo 1 || echo 0)" "B3 look, a held card: 17"

# ---- C: a login link
run C1 11 FAKE_PROBE=link RB_PROBE_S=5 -- "$S175" look
ok "$([ $? = 0 ] && grep -qE '^[0-9]{2}:[0-9]{2}:[0-9]{2} aifoundry2 needs a check$' "$T/lock-C1.txt" && echo 1 || echo 0)" \
   "C1 a link at the probe: 11, the lock line appended"
ok "$(none_left)" "C  no stand-in process left after the link case"

# ---- D: hangs
run D1 12 FAKE_PROBE=hang RB_PROBE_S=3 -- "$S175" look; ok "$([ $? = 0 ] && echo 1 || echo 0)" "D1 a probe that hangs: 12"
run D2 13 FAKE_CALL=hang RB_READ_S=3 -- "$S175" look; ok "$([ $? = 0 ] && echo 1 || echo 0)" "D2 a call that hangs past its bound: 13"
ok "$(none_left)" "D  no stand-in process left after the hang cases"

# ---- E: launches
printf "REFUSED: E173's queue ended 30 s ago; E175 waits 600 s after it (E175.md, The window)\n" > "$T/fix/l-ref.txt"
printf "IDENTITY-STOP: aifoundry2 booted '2026-11-05 01:00:00', not before E69's firmware read of 2026-10-27 13:56:26 PDT\n" > "$T/fix/l-id.txt"
printf 'LAUNCHED e175 2026-11-05 20:00:00 PST (--cap 42, slot 2880 s, tools/claims-v3/e175/protocol.json)\n' > "$T/fix/l-ok.txt"
run E1 10 FAKE_FIXTURE="$T/fix/l-ref.txt" FAKE_RC=3 -- "$S175" launch; ok "$([ $? = 0 ] && echo 1 || echo 0)" "E1 launch refused on the box by E175's window gate: 10"
ok "$(grep -q 'queue_e173' "$T/out-E1/stdin.sh" && grep -q 'build/e173/runs/status.json' "$T/out-E1/stdin.sh" && grep -q 'AFTER=600' "$T/out-E1/stdin.sh" \
      && grep -q 'job_ok_today a2-dry-e175' "$T/out-E1/stdin.sh" && grep -q 'IDENTITY-STOP' "$T/out-E1/stdin.sh" && echo 1 || echo 0)" \
   "E1 the launch's remote script carries the after-E173 gate (AFTER=600), the dry pass's job check and the guard's identity lines"
run E2 16 FAKE_FIXTURE="$T/fix/l-id.txt" FAKE_RC=3 -- "$S175" launch; ok "$([ $? = 0 ] && echo 1 || echo 0)" "E2 launch, the identity stop: 16"
run E3 0 FAKE_FIXTURE="$T/fix/l-ok.txt" -- "$S175" launch; ok "$([ $? = 0 ] && echo 1 || echo 0)" "E3 launch, its launch line: 0"
mkdir -p "$T/past"
cp "$T/window-q142kg.env" "$T/window-q142kg.env.keep"
sed 's/^RB_LAST_START_EPOCH=.*/RB_LAST_START_EPOCH=1000/' "$T/window-q142kg.env.keep" > "$T/window-q142kg.env"
c1=$(calls)
run E4 16 -- "$S175" launch; ok "$([ $? = 0 ] && [ "$(calls)" = "$c1" ] && echo 1 || echo 0)" "E4 launch past the day's last start: 16, with no call made"
cp "$T/window-q142kg.env.keep" "$T/window-q142kg.env"

# ---- G: the after-E173 gate's own lines, in a made-up box tree
G=$T/gbox
mkdir -p "$G/build/e173/runs" "$T/gbin"
cat > "$T/gbin/stat" <<'EOS'
#!/bin/bash
# a stand-in for GNU stat's "-c %Y <file>" (the box's coreutils), on macOS
if [ "$1" = -c ] && [ "$2" = %Y ]; then exec /usr/bin/stat -f %m "$3"; fi
exec /usr/bin/stat "$@"
EOS
chmod +x "$T/gbin/stat"
awk '/^# E175.md, The window: after E173/{p=1} p&&/^fi$/{print; exit} p' "$S175" > "$T/gate-body.sh"
{ echo 'set -u'
  echo 'fresh() { [ -e "$1" ] && [ "$(TZ=America/Los_Angeles date -r "$1" +%F 2>/dev/null)" = "$(TZ=America/Los_Angeles date +%F)" ]; }'
  echo 'AFTER=600'
  cat "$T/gate-body.sh"
  echo 'echo GATE-PASSED'; } > "$T/gate.sh"
gate() { (cd "$G" && PATH="$T/gbin:$PATH" bash "$T/gate.sh") 2>&1; }
ok "$(grep -c . "$T/gate-body.sh" | awk '{print ($1 >= 10)}')" "G0 the gate's lines are cut from the step driver itself ($(grep -c . "$T/gate-body.sh") lines)"
o=$(gate); ok "$(printf '%s' "$o" | grep -q 'no E173 queue record written today' && printf '%s' "$o" | grep -q GATE-PASSED && echo 1 || echo 0)" "G1 no E173 record today: the gate passes"
printf '{"state": "ended"}\n' > "$G/build/e173/runs/status.json"
touch -t "$(date -v-30S +%Y%m%d%H%M.%S)" "$G/build/e173/runs/status.json"
o=$(gate); ok "$(printf '%s' "$o" | grep -q '^REFUSED: E173.s queue ended' && ! printf '%s' "$o" | grep -q GATE-PASSED && echo 1 || echo 0)" "G2 E173 ended 30 s ago: refused"
touch -t "$(date -v-700S +%Y%m%d%H%M.%S)" "$G/build/e173/runs/status.json"
o=$(gate); ok "$(printf '%s' "$o" | grep -q 'its queue ended [0-9]* s ago (at least 600 s): ok' && printf '%s' "$o" | grep -q GATE-PASSED && echo 1 || echo 0)" "G3 E173 ended 700 s ago: the gate passes"
printf '{"state": "halted"}\n' > "$G/build/e173/runs/status.json"
touch -t "$(date -v-700S +%Y%m%d%H%M.%S)" "$G/build/e173/runs/status.json"
o=$(gate); ok "$(printf '%s' "$o" | grep -q GATE-PASSED && echo 1 || echo 0)" "G4 E173 halted 700 s ago: the gate passes"
printf '{"state": "running"}\n' > "$G/build/e173/runs/status.json"
o=$(gate); ok "$(printf '%s' "$o" | grep -q '^REFUSED: E173.s status.json' && echo 1 || echo 0)" "G5 a status that reads running: refused"
rm -f "$G/build/e173/runs/status.json"
cat > "$T/gbin/pgrep" <<'EOS'
#!/bin/bash
# a stand-in pgrep: with FAKE_E173_LIVE=1 it reports one process for E173's queue pattern; else the real pgrep
if [ "${FAKE_E173_LIVE:-}" = 1 ] && printf '%s\n' "$@" | grep -q 'queue_e173'; then echo 4242; exit 0; fi
exec /usr/bin/pgrep "$@"
EOS
chmod +x "$T/gbin/pgrep"
o=$(cd "$G" && FAKE_E173_LIVE=1 PATH="$T/gbin:$PATH" bash "$T/gate.sh" 2>&1)
ok "$(printf '%s' "$o" | grep -q "^REFUSED: E173's queue still runs" && ! printf '%s' "$o" | grep -q GATE-PASSED && echo 1 || echo 0)" "G6 a live queue_e173.py process (a stand-in pgrep reports one): refused"
o=$(gate); ok "$(printf '%s' "$o" | grep -q GATE-PASSED && echo 1 || echo 0)" "G7 the same tree with no such process and no record: the gate passes"

# ---- F: wait
printf '{"state": "ended"}\nRUN-ENDED e175\n' > "$T/fix/w-end.txt"
printf 'RUN-RUNNING e175 after 540 s\n' > "$T/fix/w-run.txt"
printf 'QUEUE-HALT:\nsmoke: bad\nRUN-ENDED e175\nGATE-STOPPED e175\n' > "$T/fix/w-halt.txt"
run F1 0 FAKE_FIXTURE="$T/fix/w-end.txt" -- "$S175" wait; ok "$([ $? = 0 ] && echo 1 || echo 0)" "F1 wait, ended: 0"
run F2 17 FAKE_FIXTURE="$T/fix/w-run.txt" -- "$S175" wait; ok "$([ $? = 0 ] && echo 1 || echo 0)" "F2 wait, still running: 17"
run F3 16 FAKE_FIXTURE="$T/fix/w-halt.txt" -- "$S175" wait; ok "$([ $? = 0 ] && echo 1 || echo 0)" "F3 wait, halted at a gate: 16"

# ---- I: the C-log gate with v3's list, on made-up data directories
mk_q() {  # mk_q <dir> <sessions with a work launch...>
  local q=$1; shift
  mkdir -p "$q"
  : > "$q/queue.jsonl"
  for s in smoke stoptest-board stoptest-die "$@"; do
    mkdir -p "$q/$s"
    echo "{\"kind\": \"session_start\", \"name\": \"$s\"}" >> "$q/queue.jsonl"
    [ "$s" = stoptest-die ] && continue
    echo '{"role": "work", "run": "r0"}' > "$q/$s/launches.jsonl"
    echo '{"run": "r0"}' > "$q/$s/runs.jsonl"
    : > "$q/$s/c-log.jsonl"
  done
}
cc_ok() {  # cc_ok <data dir> <sessions>: a finished check for each, written now, in ccheck.py's summary form (what ccdone_q142s.py reads)
  local d=$1; shift
  for s in "$@"; do echo '{"summary": {"launches": 1, "PASS": 1, "ROUNDING": 0, "UNMODELLED": 0, "FAIL": 0, "all_pass": true}, "launches": [{"run": "r0"}]}' > "$d/ccheck-$s.json"; done
}
cat > "$T/gate-cc.sh" <<EOS
. "$KG/rb_common_v3.sh"
rb_init e175_cctest
rb_cc_gate E175 "\$1" "\$2" "\$3"
EOS
d1=$T/dd1; mk_q "$d1/aifoundry2" s1; t0=$(( $(date +%s) - 5 )); cc_ok "$d1" smoke stoptest-board s1
mkdir -p "$T/out-I1"; env RB_OUT="$T/out-I1" RB_LOCK="$T/lock-I1.txt" bash "$T/gate-cc.sh" "$t0" "$d1/aifoundry2" "$d1" > "$T/out-I1/r.txt" 2>&1; r=$?
ok "$([ $r = 0 ] && grep -q "v3's list" "$T/out-I1/r.txt" && echo 1 || echo 0)" "I1 every listed session carries a C log and a finished check: 0 (rc $r)"
d2=$T/dd2; mk_q "$d2/aifoundry2" s1; rm -f "$d2/aifoundry2/stoptest-board/c-log.jsonl"; cc_ok "$d2" smoke s1
mkdir -p "$T/out-I2"; env RB_OUT="$T/out-I2" RB_LOCK="$T/lock-I2.txt" bash "$T/gate-cc.sh" "$t0" "$d2/aifoundry2" "$d2" > "$T/out-I2/r.txt" 2>&1; r=$?
ok "$([ $r = 14 ] && echo 1 || echo 0)" "I2 a listed session (stoptest-board) without a C log: 14 (rc $r)"
d3=$T/dd3; mk_q "$d3/aifoundry2" s1 s2; cc_ok "$d3" smoke stoptest-board s1
mkdir -p "$T/out-I3"; env RB_OUT="$T/out-I3" RB_LOCK="$T/lock-I3.txt" bash "$T/gate-cc.sh" "$t0" "$d3/aifoundry2" "$d3" > "$T/out-I3/r.txt" 2>&1; r=$?
ok "$([ $r = 14 ] && echo 1 || echo 0)" "I3 a resume s2 with a work launch but no check of C: 14 (rc $r)"
ok "$(none_left)" "after every case: no stand-in process left"
echo "     information (v2): this run's stand-ins still alive when a step returned, before clean(): $([ -s "$T/alive-before-clean.txt" ] && tr '\n' ' ' < "$T/alive-before-clean.txt" || echo none)"
echo
echo "$([ $F = 0 ] && echo ALL PASS || echo FAILED): $((N - F)) of $N"
[ $F = 0 ]
