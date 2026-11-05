#!/usr/bin/env bash
# Q142(kg): the desk test of the pool-8 day's ported steps (tools/claims-v3/e173/box/step_e173.sh, tools/claims-v3/e174/box/step_e174.sh, this
# directory's rb_common.sh, s02_window_q142kg.sh and cclist_q142kg.py). It never reaches a lab box: a stand-in `ssh` and `rsync`, first on PATH in
# the scratch dir, take every call. The stand-in ssh answers the probe (`true`) and, for a remote script, saves the script and prints a fixture the
# case names, or hangs, or prints a login-check link and hangs, or fails (FAKE_PROBE, FAKE_CALL, FAKE_FIXTURE, FAKE_RC); the stand-in rsync copies
# nothing, or fails, or prints a link and hangs (FAKE_RSYNC). The bounds are shortened with v3.1's own desk-test overrides (RB_<CLS>_S). The cases:
#   A    the dry listing (RB_DRY=1) of every step of both drivers: exit 0, and the stand-ins log no call
#   B    step_e173 look: FREE (0), the identity stop (16), a held card (17)
#   C    a login link at the probe and in a call: 11, the lock line "<HH:MM:SS> <box> needs a check" appended, the link kept in RB_OUT/links.txt
#   D    a hang with no output: the probe (12) and a call past its bound (13)
#   E    step_e174 launch: a refusal on the box (10), the identity stop (16), the launch line (0); step_e173 launch past the day's last start (16,
#        with no call made)
#   F    step_e174 wait: halted (16), ended (0), still running (17)
#   G    step_e174 sync: the copy fails (14), a link in the copy (11)
#   H    step_e173 tree: every preflight clean (0); the device-command preflight not GO (16)
#   I    the C-log gate (rb_cc_gate over cclist_q142kg.py and v3.1's ccdone_q142s.py) on made-up data directories: every listed session carries a C
#        log and a finished check (0); a listed session without a C log (14); a stale check (14); a resume s2 with a work launch but no check (14)
#   J    ours_live's pattern names E171-E174's queue, runner, session and block processes and v3.1's (by command line)
# After every case no stand-in process is left running.
#
#   bash tools/claims-v3/q142kg-runbook/selftest_steps_q142kg.sh <a new, empty scratch dir> > tools/claims-v3/q142kg-runbook/logs/selftest-steps.txt
# SPDX-License-Identifier: Apache-2.0
set -u
T=${1:?usage: selftest_steps_q142kg.sh <a new, empty scratch dir>}
[ -d "$T" ] && [ -n "$(ls -A "$T" 2>/dev/null)" ] && { echo "refused: $T is not empty"; exit 2; }
mkdir -p "$T/bin" "$T/fix" || exit 2
D=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
REPO=$(cd "$D/../../.." && pwd)
S173="$REPO/tools/claims-v3/e173/box/step_e173.sh"
S174="$REPO/tools/claims-v3/e174/box/step_e174.sh"
# the runner's link pattern (v3.1's rb_run.py LINK), assembled here at run time so this file's text holds no such host: a desk-test fixture
FAKE_L="login.tail""scale.com"
export FAKE_L FAKE_LOG="$T/calls.log"
cat > "$T/bin/ssh" <<'EOS'
#!/bin/bash
echo "$(date +%s) ssh $*" >> "$FAKE_LOG"
last="${!#}"
if [ "$last" = true ]; then
  case "${FAKE_PROBE:-ok}" in
    ok) exit 0 ;;
    link) echo "# To authenticate, visit: https://$FAKE_L/a/desk-test-probe" >&2; exec sleep 3651 ;;
    hang) exec sleep 3651 ;;
  esac
fi
cat > "${FAKE_STDIN:-/dev/null}"
case "${FAKE_CALL:-ok}" in
  ok) [ -n "${FAKE_FIXTURE:-}" ] && cat "$FAKE_FIXTURE"; exit "${FAKE_RC:-0}" ;;
  link) echo "# To authenticate, visit: https://$FAKE_L/a/desk-test-call" >&2; exec sleep 3651 ;;
  hang) exec sleep 3651 ;;
  fail) echo "a stand-in failure"; exit 3 ;;
esac
EOS
cat > "$T/bin/rsync" <<'EOS'
#!/bin/bash
echo "$(date +%s) rsync $*" >> "$FAKE_LOG"
case "${FAKE_RSYNC:-ok}" in
  ok) exit 0 ;;
  fail) echo "rsync: a stand-in failure" >&2; exit 23 ;;
  link) echo "# To authenticate, visit: https://$FAKE_L/a/desk-test-rsync" >&2; exec sleep 3651 ;;
esac
EOS
chmod +x "$T/bin/ssh" "$T/bin/rsync"
export PATH="$T/bin:$PATH"
N=0; F=0
ok() { N=$((N + 1)); if [ "$1" = 1 ]; then echo "PASS $2"; else F=$((F + 1)); echo "FAIL $2"; fi; }
clean() { pkill -f 'sleep 3651' 2>/dev/null; sleep 0.2; }
none_left() { pgrep -f 'sleep 3651' > /dev/null && echo 0 || echo 1; }
run() {  # run <name> <expected rc> <env...> -- <script> <args...>: one step in its own RB_OUT; prints its rc
  local name=$1 want=$2; shift 2
  local envs=()
  while [ "$1" != -- ]; do envs+=("$1"); shift; done; shift
  mkdir -p "$T/out-$name"
  [ -f "$T/window-q142kg.env" ] && cp "$T/window-q142kg.env" "$T/out-$name/"
  env RB_OUT="$T/out-$name" RB_LOCK="$T/lock-$name.txt" FAKE_STDIN="$T/out-$name/stdin.sh" ${envs[@]+"${envs[@]}"} bash "$@" > "$T/out-$name/result.txt" 2>&1
  local rc=$?
  echo "$rc" > "$T/out-$name/rc"
  clean
  [ "$rc" = "$want" ] && return 0 || { echo "     ($name: rc $rc, wanted $want; last lines: $(tail -n 2 "$T/out-$name/result.txt" | tr '\n' ' ' | cut -c1-240))"; return 1; }
}
calls() { [ -f "$FAKE_LOG" ] && wc -l < "$FAKE_LOG" | tr -d ' ' || echo 0; }

# ---- the day's window, a future one (s02_window_q142kg.sh, desk only)
day=$(TZ=America/Los_Angeles date -v+1d +%F 2>/dev/null || TZ=America/Los_Angeles date -d tomorrow +%F)
env RB_OUT="$T/w" RB_LOCK="$T/lock-w.txt" bash "$D/s02_window_q142kg.sh" "$day" 22:00 23:30 > "$T/w.txt" 2>&1
ok "$([ $? = 0 ] && grep -q '^RB_E174_DEADLINE=' "$T/w/window-q142kg.env" && echo 1 || echo 0)" "W  s02_window_q142kg.sh writes the day's window (last start 22:00, last end 23:30 tomorrow) with E174's deadline"
cp "$T/w/window-q142kg.env" "$T/window-q142kg.env"

# ---- A: the dry listing of every step
c0=$(calls)
a=1
for s in look tree "dry start" "dry wait" launch "launch subset" wait collect; do
  # shellcheck disable=SC2086
  run "A173-${s// /-}" 0 RB_DRY=1 -- "$S173" $s || a=0
done
for s in look sync check launch "launch subset" wait pull collect; do
  # shellcheck disable=SC2086
  run "A174-${s// /-}" 0 RB_DRY=1 -- "$S174" $s || a=0
done
ok "$a" "A  the dry listing of all 16 steps exits 0"
ok "$([ "$(calls)" = "$c0" ] && echo 1 || echo 0)" "A  the dry listing called no ssh and no rsync"
ok "$(grep -h 'collect_e173_bounded.sh' "$T"/out-A173-collect/result.txt > /dev/null && grep -h 'ccdone_q142s.py' "$T"/out-A173-collect/result.txt > /dev/null \
      && grep -h 'cclist_q142kg.py' "$T"/out-A174-collect/result.txt > /dev/null && grep -h 'nopath_q142s.py\|no desk path' "$T"/out-A174-collect/result.txt > /dev/null && echo 1 || echo 0)" \
   "A  each collect step lists its collector, the C-log list, the C-check gate and the desk-path gate"

# ---- B: step_e173 look
printf 'IDENTITY-OK: the host booted 2026-10-26 15:13:03, before ...\nholders: ...\nHOLDER-RULE: FREE\n' > "$T/fix/look-free.txt"
printf 'IDENTITY-STOP: the host booted 2026-11-05 01:00:00, after ...\nHOLDER-RULE: FREE\n' > "$T/fix/look-idstop.txt"
printf 'IDENTITY-OK: ...\nHOLDER-RULE: HELD\n' > "$T/fix/look-held.txt"
run B1 0 FAKE_FIXTURE="$T/fix/look-free.txt" -- "$S173" look; ok "$([ $? = 0 ] && echo 1 || echo 0)" "B1 step_e173 look, a free card: 0"
ok "$(grep -q 'ours_live' "$T/out-B1/stdin.sh" && grep -q 'queue|run)_e17\[0-9\]' "$T/out-B1/stdin.sh" && echo 1 || echo 0)" "B1 the remote script carries the q142kg prelude's ours_live (E171-E174 named)"
run B2 16 FAKE_FIXTURE="$T/fix/look-idstop.txt" -- "$S173" look; ok "$([ $? = 0 ] && echo 1 || echo 0)" "B2 step_e173 look, a host booted after E69's read: 16"
run B3 17 FAKE_FIXTURE="$T/fix/look-held.txt" -- "$S173" look; ok "$([ $? = 0 ] && echo 1 || echo 0)" "B3 step_e173 look, a held card: 17"

# ---- C: login links
run C1 11 FAKE_PROBE=link RB_PROBE_S=5 -- "$S173" look
ok "$([ $? = 0 ] && grep -qE '^[0-9]{2}:[0-9]{2}:[0-9]{2} aifoundry2 needs a check$' "$T/lock-C1.txt" && grep -q 'desk-test-probe' "$T/out-C1/links.txt" && echo 1 || echo 0)" \
   "C1 a link at the probe: 11, the lock line appended, the link kept in RB_OUT/links.txt"
run C2 11 FAKE_CALL=link RB_READ_S=8 -- "$S174" look
ok "$([ $? = 0 ] && grep -qE ' aifoundry1 needs a check$' "$T/lock-C2.txt" && echo 1 || echo 0)" "C2 a link in step_e174 look's call: 11, the lock line names aifoundry1"
ok "$(none_left)" "C  no stand-in process left after the link cases"

# ---- D: hangs
run D1 12 FAKE_PROBE=hang RB_PROBE_S=3 -- "$S174" look; ok "$([ $? = 0 ] && echo 1 || echo 0)" "D1 a probe that hangs: 12"
run D2 13 FAKE_CALL=hang RB_READ_S=3 -- "$S173" look; ok "$([ $? = 0 ] && echo 1 || echo 0)" "D2 a call that hangs past its bound: 13"
ok "$(none_left)" "D  no stand-in process left after the hang cases"

# ---- E: launches
printf 'REFUSED: something of ours is on aifoundry1 (E172 must have ended; never two of our sessions there): nothing launched\n' > "$T/fix/l-ref.txt"
printf "IDENTITY-STOP: aifoundry1 booted '2026-11-05 01:00:00', not before E84's identity read\n" > "$T/fix/l-id.txt"
printf 'LAUNCHED e174 T0=1 (00:00:01 PST), slot end 00:45:01 PST, plan full, slot 45 min, cap 40, protocol tools/claims-v3/e174/protocol.json\n' > "$T/fix/l-ok.txt"
run E1 10 FAKE_FIXTURE="$T/fix/l-ref.txt" FAKE_RC=3 -- "$S174" launch; ok "$([ $? = 0 ] && echo 1 || echo 0)" "E1 step_e174 launch refused on the box: 10"
run E2 16 FAKE_FIXTURE="$T/fix/l-id.txt" FAKE_RC=3 -- "$S174" launch; ok "$([ $? = 0 ] && echo 1 || echo 0)" "E2 step_e174 launch, the identity stop: 16"
run E3 0 FAKE_FIXTURE="$T/fix/l-ok.txt" -- "$S174" launch; ok "$([ $? = 0 ] && echo 1 || echo 0)" "E3 step_e174 launch, its launch line: 0"
ok "$(grep -q "bash -s -- '$(sed -n 's/^RB_E174_DEADLINE=//p' "$T/window-q142kg.env" | tr -d "'" | sed 's/\\//g')'" "$T/calls.log" && echo 1 || echo 0)" \
   "E3 the launch passed the window file's E174 deadline to launch_e174.sh"
mkdir -p "$T/past"
env RB_OUT="$T/past" RB_LOCK="$T/lock-p.txt" bash "$D/s02_window_q142kg.sh" "$day" 22:00 23:30 > /dev/null 2>&1
sed -i.bak 's/^RB_LAST_START_EPOCH=.*/RB_LAST_START_EPOCH=1000/' "$T/past/window-q142kg.env"
c1=$(calls)
cp "$T/window-q142kg.env" "$T/window-q142kg.env.keep"; cp "$T/past/window-q142kg.env" "$T/window-q142kg.env"
run E4 16 -- "$S173" launch; e4=$?
cp "$T/window-q142kg.env.keep" "$T/window-q142kg.env"
ok "$([ $e4 = 0 ] && [ "$(calls)" = "$c1" ] && echo 1 || echo 0)" "E4 step_e173 launch past the day's last start: 16, and no call was made"

# ---- F: waits
printf '== status: {"state": "halted"}\n' > "$T/fix/w-h.txt"; printf '== status: {"state": "ended"}\n' > "$T/fix/w-e.txt"; printf '== status: {"state": "running"}\n' > "$T/fix/w-r.txt"
run F1 16 FAKE_FIXTURE="$T/fix/w-h.txt" -- "$S174" wait; f1=$?
run F2 0 FAKE_FIXTURE="$T/fix/w-e.txt" -- "$S174" wait; f2=$?
run F3 17 FAKE_FIXTURE="$T/fix/w-r.txt" -- "$S174" wait; f3=$?
ok "$([ $f1 = 0 ] && [ $f2 = 0 ] && [ $f3 = 0 ] && echo 1 || echo 0)" "F  step_e174 wait: halted 16, ended 0, still running 17"

# ---- G: the sync's copy (RB_REPO an empty scratch git repo, so its clean-tree read does not depend on the lab clone's state)
git init -q "$T/repo"
run G1 14 FAKE_RSYNC=fail RB_REPO="$T/repo" -- "$S174" sync; g1=$?
run G2 11 FAKE_RSYNC=link RB_COPY_S=8 RB_REPO="$T/repo" -- "$S174" sync; g2=$?
ok "$([ $g1 = 0 ] && [ $g2 = 0 ] && grep -qE ' aifoundry1 needs a check$' "$T/lock-G2.txt" && echo 1 || echo 0)" "G  step_e174 sync: a failed copy 14; a link in the copy 11 with its lock line"

# ---- H: step_e173 tree
printf 'pull rc=0\nancestry rc=0\nporcelain lines: 0\nHEAD 0000000 2026-11-05\n' > "$T/fix/t-tree.txt"
printf 'HARNESS OK 250 + 3 binaries\n64 tiles; frozen inputs, Q139(k)'"'"'s files and tiles: OK\nblind8 OK: 89\npreflight rc=0 dmcmd_audit: GO (19 send site(s), 0 disallowed; allow-list: none)\nlist rc=0 (165 BURST runs listed)\n' > "$T/fix/t-pre.txt"
sed 's/dmcmd_audit: GO.*/dmcmd_audit: NO-GO/' "$T/fix/t-pre.txt" > "$T/fix/t-pre-nogo.txt"
cat "$T/fix/t-tree.txt" "$T/fix/t-pre.txt" > "$T/fix/t-all.txt"; cat "$T/fix/t-tree.txt" "$T/fix/t-pre-nogo.txt" > "$T/fix/t-nogo.txt"
run H1 0 FAKE_FIXTURE="$T/fix/t-all.txt" -- "$S173" tree; h1=$?
run H2 16 FAKE_FIXTURE="$T/fix/t-nogo.txt" -- "$S173" tree; h2=$?
ok "$([ $h1 = 0 ] && [ $h2 = 0 ] && echo 1 || echo 0)" "H  step_e173 tree: clean 0; the device-command preflight NO-GO 16"

# ---- I: the C-log gate on made-up data directories (rb_cc_gate, cclist_q142kg.py, v3.1's ccdone_q142s.py)
mk_session() {  # mk_session <runs dir> <session> <work launches> <with a C log 0|1>
  mkdir -p "$1/$2"; : > "$1/$2/launches.jsonl"
  local i=0; while [ "$i" -lt "$3" ]; do echo '{"role": "work"}' >> "$1/$2/launches.jsonl"; i=$((i + 1)); done
  gzip -n "$1/$2/launches.jsonl"; echo '{"dry": false}' > "$1/$2/session.json"
  [ "$4" = 1 ] && { echo '{}' > "$1/$2/c-log.jsonl"; gzip -n "$1/$2/c-log.jsonl"; }
  echo "{\"kind\": \"session_start\", \"name\": \"$2\"}" >> "$1/queue.jsonl"
}
mk_check() { printf '{"summary": {"launches": 2, "PASS": 2, "ROUNDING": 0, "UNMODELLED": 0, "FAIL": 0, "all_pass": true}, "launches": [{}, {}]}\n' > "$1"; }
gate() {  # gate <case> <data dir> <since>
  cat > "$T/gate-$1.sh" <<EOF
. "$D/rb_common.sh"
rb_init gate_$1
rb_cc_gate GATE "$3" "$2/runs" "$2"
EOF
  env RB_OUT="$T/out-gate-$1" RB_LOCK="$T/lock-gate.txt" bash "$T/gate-$1.sh" > "$T/gate-$1.txt" 2>&1
}
for c in ok noclog stale resume; do
  G="$T/data-$c"; mkdir -p "$G/runs"
  mk_session "$G/runs" stoptest-die 0 0; mk_session "$G/runs" stoptest-board 1 1; mk_session "$G/runs" smoke 2 1; mk_session "$G/runs" s1 9 1
  [ "$c" = noclog ] && rm -f "$G/runs/smoke/c-log.jsonl.gz"
  [ "$c" = resume ] && mk_session "$G/runs" s2 3 1
  mk_check "$G/ccheck-stoptest-board.json"; mk_check "$G/ccheck-smoke.json"; mk_check "$G/ccheck-s1.json"
done
since=$(( $(date +%s) - 60 ))
gate ok "$T/data-ok" "$since"; i1=$?
gate noclog "$T/data-noclog" "$since"; i2=$?
gate stale "$T/data-stale" "$(( $(date +%s) + 3600 ))"; i3=$?
gate resume "$T/data-resume" "$since"; i4=$?
ok "$([ $i1 = 0 ] && grep -q '3 listed sessions carry a C log' "$T/gate-ok.txt" && echo 1 || echo 0)" "I1 every listed session (stoptest-board, smoke, s1) carries a C log and a finished check: 0"
ok "$([ $i2 = 14 ] && grep -q 'MISSING-CLOG smoke' "$T/gate-noclog.txt" && echo 1 || echo 0)" "I2 a listed session (smoke) without a C log: 14"
ok "$([ $i3 = 14 ] && grep -q 'CCHECK-STALE' "$T/gate-stale.txt" && echo 1 || echo 0)" "I3 a check written before the collection began: 14"
ok "$([ $i4 = 14 ] && grep -q 'CCHECK-MISSING' "$T/gate-resume.txt" && echo 1 || echo 0)" "I4 a resume s2 that ran a work launch, with no check of C: 14"

# ---- J: ours_live's pattern
P=$(sed -n "s/.*pgrep -u \"\$(id -u)\" -f '\([^']*\)'.*/\1/p" "$T/out-B1/stdin.sh" | tail -n 1)
j=1
for cmd in "python3 tools/claims-v3/e173/queue_e173.py --slots s --runs build/e173/runs" "python3 tools/claims-v3/e174/run_e174.py --protocol p" \
           "python3 tools/claims-v3/e171/queue_e171.py --slots s" "bash tools/claims-v3/e172/session_e172.sh" "bash block_e172 16410" \
           "python3 tools/claims-v3/e170/queue_e170.py" "python3 tools/claims-v3/e165/queue_e165.py"; do
  printf '%s\n' "$cmd" | grep -qE "$P" || { j=0; echo "     not matched: $cmd"; }
done
printf '%s\n' "python3 tools/claims-v3/e173/score_e173.py" | grep -qE "$P" && { j=0; echo "     matched a desk scorer"; }
ok "$j" "J  ours_live's pattern names E171-E174's queue, runner, session and block processes and v3.1's, and not a desk scorer"

ok "$(none_left)" "   no stand-in process left at the end"
echo "selftest_steps_q142kg: $((N - F)) of $N checks pass"
[ "$F" -eq 0 ]
