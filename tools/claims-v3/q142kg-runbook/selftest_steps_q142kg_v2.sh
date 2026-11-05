#!/usr/bin/env bash
# Q142(kg) fix pass, Thu 5 Nov 2026: the desk test of the v2 step drivers (tools/claims-v3/e173/box/step_e173_v2.sh,
# tools/claims-v3/e174/box/step_e174_v2.sh, this directory's rb_common_v2.sh and cclist_q142kg_v2.py). selftest_steps_q142kg.sh (v1) stays as
# committed. It never reaches a lab box: a stand-in `ssh` and `rsync`, first on PATH in the scratch dir, take every call. Besides v1's fixture modes
# (the stand-in ssh prints a fixture the case names, or hangs, or prints a login-check link and hangs, or fails), the stand-in ssh has one more:
# with FAKE_EXEC=1, a script that opens with the runbook's own prelude (`set -u`, then `cd ~/<tree>`) is RUN here, in a sandbox home that holds
# the box's tree, with only the box's tools stood in (GNU date for date; uptime -s; a pgrep that names a process of ours only when the case gives
# one and the runbook's own pattern matches it; setsid). So the refusals below are the generated remote scripts' own, not a fixture's. A kit's
# committed box script (launch_e174.sh, look, wait) is never run: it gets the case's fixture. The cases:
#   W     the day's window
#   A     the dry listing of all 17 steps of both v2 drivers exits 0 and calls nothing; it shows each new gate
#   B-J   v1's cases, on the v2 drivers (E174's launch through the restored guard)
#   K     E174's restored aifoundry1 gates (the kits' verifier's fault 1): the box check refuses to start beside E172's session (each of its four
#         processes) or beside another dry pass, and removes a stale clean file; it starts, runs and reads clean (the day's clean file written),
#         or reads unclean (16, no file), or was not started today (10); the launch refuses with no clean file today or one of another day (10, no
#         call made), and on the box when the check job has not ended rc 0 today, a dry pass runs, E172 runs (10, the launcher never sent), or the
#         host booted after the firmware read (16); with all of them clean it launches (0); the sync refuses beside E172 (10, no rsync) and runs
#         when nothing of ours does (0)
#   L     v2's C-log list (fault 7) through rb_common_v2.sh's gate: v1's four I cases again; no queue.jsonl (14); a lost launches.jsonl with runs
#         (14); stoptest-board's launches lost with its board stop in the queue's record (14); a lost launches.jsonl with card-minutes (14); an s1 that
#         ran nothing beside an s2 that ran everything (0, no false stop); an s2 directory the queue's record does not start (14); and the parents'
#         committed sessions, E165's and E170's, through the whole gate (0, v2's list equal to v1's)
# After every case no stand-in process is left running.
#
#   bash tools/claims-v3/q142kg-runbook/selftest_steps_q142kg_v2.sh <a new, empty scratch dir> > tools/claims-v3/q142kg-runbook/logs/selftest-steps-v2.txt
# SPDX-License-Identifier: Apache-2.0
set -u
T=${1:?usage: selftest_steps_q142kg_v2.sh <a new, empty scratch dir>}
[ -d "$T" ] && [ -n "$(ls -A "$T" 2>/dev/null)" ] && { echo "refused: $T is not empty"; exit 2; }
mkdir -p "$T/bin" "$T/fix" "$T/boxbin" || exit 2
D=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
REPO=$(cd "$D/../../.." && pwd)
S173="$REPO/tools/claims-v3/e173/box/step_e173_v2.sh"
S174="$REPO/tools/claims-v3/e174/box/step_e174_v2.sh"
GDATE=$(command -v gdate 2>/dev/null || true)
[ -n "$GDATE" ] || { echo "refused: the K cases need GNU date (gdate) to stand in for the box's date"; exit 2; }
# the runner's link pattern (v3.1's rb_run.py LINK), assembled here at run time so this file's text holds no such host: a desk-test fixture
FAKE_L="login.tail""scale.com"
export FAKE_L FAKE_LOG="$T/calls.log" FAKE_BOXBIN="$T/boxbin"
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
if [ -n "${FAKE_EXEC:-}" ] && [ -n "${FAKE_STDIN:-}" ] && [ "$(sed -n 1p "$FAKE_STDIN")" = "set -u" ] && sed -n 2p "$FAKE_STDIN" | grep -q '^cd ~/'; then
  echo "$(date +%s) exec $(sed -n 3p "$FAKE_STDIN")" >> "$FAKE_LOG"
  HOME="$FAKE_HOME" PATH="$FAKE_BOXBIN:$PATH" bash "$FAKE_STDIN" < /dev/null
  exit $?
fi
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
# the box's tools, stood in for the generated scripts that FAKE_EXEC runs (never on PATH outside them)
printf '#!/bin/bash\nexec %s "$@"\n' "$GDATE" > "$T/boxbin/date"
cat > "$T/boxbin/uptime" <<'EOS'
#!/bin/bash
if [ "${1:-}" = -s ]; then echo "${FAKE_BOOT:-2026-10-20 09:00:00}"; else echo " 05:40:00 up 15 days,  1 user,  load average: 0.10, 0.10, 0.10"; fi
EOS
cat > "$T/boxbin/pgrep" <<'EOS'
#!/bin/bash
# the runbook's ours_live calls pgrep -u <uid> -f '<its pattern>': a process of ours exists only when the case names its command line and the
# runbook's own pattern matches it
pat="${!#}"
if [ -n "${FAKE_PGREP_CMD:-}" ] && printf '%s\n' "$FAKE_PGREP_CMD" | grep -qE -- "$pat"; then echo 424242; exit 0; fi
exit 1
EOS
printf '#!/bin/bash\nexec "$@"\n' > "$T/boxbin/setsid"
chmod +x "$T/bin/ssh" "$T/bin/rsync" "$T/boxbin/date" "$T/boxbin/uptime" "$T/boxbin/pgrep" "$T/boxbin/setsid"
export PATH="$T/bin:$PATH"
N=0; F=0
ok() { N=$((N + 1)); if [ "$1" = 1 ]; then echo "PASS $2"; else F=$((F + 1)); echo "FAIL $2"; fi; }
clean() { pkill -f 'sleep 3651' 2>/dev/null; sleep 0.2; }
none_left() { pgrep -f 'sleep 3651' > /dev/null && echo 0 || echo 1; }
run() {  # run <name> <expected rc> <env...> -- <script> <args...>: one step in its own RB_OUT (an RB_OUT= among the envs overrides it)
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
calls() { [ -f "$FAKE_LOG" ] && grep -cE ' ssh | rsync ' "$FAKE_LOG" | tr -d ' ' || echo 0; }        # the stand-ins' calls (not their exec lines)
lines() { [ -f "$FAKE_LOG" ] && grep -c . "$FAKE_LOG" | tr -d ' ' || echo 0; }
since_calls() { tail -n +"$(($1 + 1))" "$FAKE_LOG" 2>/dev/null | grep -E ' ssh | rsync '; }       # since_calls <lines()>: the calls since
mk_home() {  # mk_home <dir>: the box's trees in a sandbox home; E174's box check stood in by a script that prints $FAKE_BOXCHECK
  mkdir -p "$1/nekko/build/q141k/jobs" "$1/nekko/tools/claims-v3/e174/box" "$1/claude/et-soc1-prototyping/build/q141k/jobs"
  printf '#!/bin/bash\ncat "$FAKE_BOXCHECK"\n' > "$1/nekko/tools/claims-v3/e174/box/check_box_e174.sh"
}
job_state() {  # job_state <home> <rc> [old]: E174's box check job as the box would hold it after it ended (old: dated yesterday)
  local j="$1/nekko/build/q141k/jobs/a1c0-check-e174"
  echo "# the job" > "$j.sh"; echo 999999 > "$j.pid"; cp "$T/fix/box-clean.txt" "$j.out"; echo BOX-CHECK-CLEAN >> "$j.out"; echo "$2" > "$j.rc"
  [ "${3:-}" = old ] && touch -t "$(TZ=America/Los_Angeles "$GDATE" -d yesterday +%Y%m%d1200)" "$j.sh" "$j.rc"
  return 0
}
day_out() {  # day_out <dir> [clean]: a card day's RB_OUT with the window, and the day's clean file if asked
  mkdir -p "$1"; cp "$T/window-q142kg.env" "$1/"
  [ "${2:-}" = clean ] && echo "$(sed -n "s/^RB_DAY=//p" "$T/window-q142kg.env") clean (made by the desk test)" > "$1/a1c0-check-clean-e174.txt"
  return 0
}

# ---- W: the day's window, a future one (s02_window_q142kg.sh, desk only)
day=$(TZ=America/Los_Angeles "$GDATE" -d tomorrow +%F)
env RB_OUT="$T/w" RB_LOCK="$T/lock-w.txt" bash "$D/s02_window_q142kg.sh" "$day" 22:00 23:30 > "$T/w.txt" 2>&1
ok "$([ $? = 0 ] && grep -q '^RB_E174_DEADLINE=' "$T/w/window-q142kg.env" && echo 1 || echo 0)" "W  s02_window_q142kg.sh writes the day's window (last start 22:00, last end 23:30 tomorrow) with E174's deadline"
cp "$T/w/window-q142kg.env" "$T/window-q142kg.env"

# ---- the fixtures of E174's box check (check_box_e174.sh's own lines)
cat > "$T/fix/box-clean.txt" <<'EOF'
2026-11-05 05:40:00 PST
== check_e174 (harness + binaries)
HARNESS OK 110 + 3 binaries
rc=0
== preflight
rc=0 dmcmd_audit: GO (33 send site(s), 0 disallowed; allow-list: none)
== tiles and frozen inputs
64 tiles; frozen inputs, Q139(k)'s files and tiles: OK
kappa0 0.9463
rc=0
== pool 8's SHA256SUMS: 89 OK (want 89)
== dry pass on the box (the toy card; no device)
stoptest-die dry rc=4 (want 4)
smoke dry rc=0 (want 0)
list rc=0 (126 BURST runs listed; want 126)
No process holds an ET-SoC-1 device node or card lock
EOF
sed 's/dmcmd_audit: GO/dmcmd_audit: NO-GO/' "$T/fix/box-clean.txt" > "$T/fix/box-nogo.txt"

# ---- A: the dry listing of every step
c0=$(calls)
a=1
for s in look tree "dry start" "dry wait" launch "launch subset" wait collect; do
  # shellcheck disable=SC2086
  run "A173-${s// /-}" 0 RB_DRY=1 -- "$S173" $s || a=0
done
for s in look sync "check start" "check wait" launch "launch subset" wait pull collect; do
  # shellcheck disable=SC2086
  run "A174-${s// /-}" 0 RB_DRY=1 -- "$S174" $s || a=0
done
ok "$a" "A  the dry listing of all 17 steps of the v2 drivers exits 0"
ok "$([ "$(calls)" = "$c0" ] && echo 1 || echo 0)" "A  the dry listing called no ssh and no rsync"
ok "$(grep -q 'cclist_q142kg_v2.py' "$T"/out-A173-collect/result.txt && grep -q 'ccdone_q142s.py' "$T"/out-A173-collect/result.txt \
      && grep -q 'cclist_q142kg_v2.py' "$T"/out-A174-collect/result.txt && grep -q 'nopath_q142s.py\|no desk path' "$T"/out-A174-collect/result.txt && echo 1 || echo 0)" \
   "A  each collect step lists its collector, v2's C-log list, the C-check gate and the desk-path gate"
r=$T/out-A174-check-start/result.txt
ok "$(grep -q 'JOB-REFUSED: a card session of ours runs on $BOX' "$r" && grep -q 'check_box_e174.sh' "$r" && grep -q 'BOX-CHECK-CLEAN' "$r" && echo 1 || echo 0)" \
   "A  step_e174_v2 check start lists a detached dry job that refuses during a session of ours, running check_box_e174.sh and reading it on the box"
r=$T/out-A174-launch/result.txt
ok "$(grep -q 'a1c0-check-clean-e174.txt' "$r" && grep -q 'job_ok_today a1c0-check-e174' "$r" && grep -q 'REFUSED: a dry pass of the runbook still runs' "$r" \
      && grep -q 'REFUSED: a card session of ours already runs' "$r" && grep -q 'GUARD-OK' "$r" && grep -q 'launch_e174.sh' "$r" && echo 1 || echo 0)" \
   "A  step_e174_v2 launch lists the day's clean-check gate, then the box's guard (no dry pass, no session of ours, today's check job), then launch_e174.sh"
ok "$(grep -q 'QUIET-OK' "$T/out-A174-sync/result.txt" && grep -q 'is-ancestor 5a2a9ba0' "$T/out-A173-tree/result.txt" && grep -q '_q142kg2\]' "$T/out-A173-look/result.txt" && echo 1 || echo 0)" \
   "A  step_e174_v2 sync reads the box quiet first; step_e173_v2 tree checks ancestry of 5a2a9ba0; the steps are named _q142kg2"

# ---- B: step_e173_v2 look
printf 'IDENTITY-OK: the host booted 2026-10-26 15:13:03, before ...\nholders: ...\nHOLDER-RULE: FREE\n' > "$T/fix/look-free.txt"
printf 'IDENTITY-STOP: the host booted 2026-11-05 01:00:00, after ...\nHOLDER-RULE: FREE\n' > "$T/fix/look-idstop.txt"
printf 'IDENTITY-OK: ...\nHOLDER-RULE: HELD\n' > "$T/fix/look-held.txt"
run B1 0 FAKE_FIXTURE="$T/fix/look-free.txt" -- "$S173" look; ok "$([ $? = 0 ] && echo 1 || echo 0)" "B1 step_e173_v2 look, a free card: 0"
ok "$(grep -q 'ours_live' "$T/out-B1/stdin.sh" && grep -q 'queue|run)_e17\[0-9\]' "$T/out-B1/stdin.sh" && echo 1 || echo 0)" "B1 the remote script carries the q142kg prelude's ours_live (E171-E174 named)"
run B2 16 FAKE_FIXTURE="$T/fix/look-idstop.txt" -- "$S173" look; ok "$([ $? = 0 ] && echo 1 || echo 0)" "B2 step_e173_v2 look, a host booted after E69's read: 16"
run B3 17 FAKE_FIXTURE="$T/fix/look-held.txt" -- "$S173" look; ok "$([ $? = 0 ] && echo 1 || echo 0)" "B3 step_e173_v2 look, a held card: 17"

# ---- C: login links
run C1 11 FAKE_PROBE=link RB_PROBE_S=5 -- "$S173" look
ok "$([ $? = 0 ] && grep -qE '^[0-9]{2}:[0-9]{2}:[0-9]{2} aifoundry2 needs a check$' "$T/lock-C1.txt" && grep -q 'desk-test-probe' "$T/out-C1/links.txt" && echo 1 || echo 0)" \
   "C1 a link at the probe: 11, the lock line appended, the link kept in RB_OUT/links.txt"
run C2 11 FAKE_CALL=link RB_READ_S=8 -- "$S174" look
ok "$([ $? = 0 ] && grep -qE ' aifoundry1 needs a check$' "$T/lock-C2.txt" && echo 1 || echo 0)" "C2 a link in step_e174_v2 look's call: 11, the lock line names aifoundry1"
ok "$(none_left)" "C  no stand-in process left after the link cases"

# ---- D: hangs
run D1 12 FAKE_PROBE=hang RB_PROBE_S=3 -- "$S174" look; ok "$([ $? = 0 ] && echo 1 || echo 0)" "D1 a probe that hangs: 12"
run D2 13 FAKE_CALL=hang RB_READ_S=3 -- "$S173" look; ok "$([ $? = 0 ] && echo 1 || echo 0)" "D2 a call that hangs past its bound: 13"
ok "$(none_left)" "D  no stand-in process left after the hang cases"

# ---- E: launches (E174's through v2's guard: the day's clean file, and the box's guard run in a sandbox where the check job ended rc 0 today)
printf 'REFUSED: something of ours is on aifoundry1 (E172 must have ended; never two of our sessions there): nothing launched\n' > "$T/fix/l-ref.txt"
printf "IDENTITY-STOP: aifoundry1 booted '2026-11-05 01:00:00', not before E84's identity read\n" > "$T/fix/l-id.txt"
printf 'LAUNCHED e174 T0=1 (00:00:01 PST), slot end 00:45:01 PST, plan full, slot 45 min, cap 40, protocol tools/claims-v3/e174/protocol.json\n' > "$T/fix/l-ok.txt"
for c in E1 E2 E3; do mk_home "$T/home-$c"; job_state "$T/home-$c" 0; day_out "$T/day-$c" clean; done
run E1 10 FAKE_EXEC=1 FAKE_HOME="$T/home-E1" RB_OUT="$T/day-E1" FAKE_FIXTURE="$T/fix/l-ref.txt" FAKE_RC=3 -- "$S174" launch
ok "$([ $? = 0 ] && grep -q 'GUARD-OK' "$T/out-E1/result.txt" && echo 1 || echo 0)" "E1 step_e174_v2 launch, the guard passes and launch_e174.sh refuses on the box: 10"
run E2 16 FAKE_EXEC=1 FAKE_HOME="$T/home-E2" RB_OUT="$T/day-E2" FAKE_FIXTURE="$T/fix/l-id.txt" FAKE_RC=3 -- "$S174" launch
ok "$([ $? = 0 ] && echo 1 || echo 0)" "E2 step_e174_v2 launch, launch_e174.sh's own identity stop: 16"
run E3 0 FAKE_EXEC=1 FAKE_HOME="$T/home-E3" RB_OUT="$T/day-E3" FAKE_FIXTURE="$T/fix/l-ok.txt" -- "$S174" launch
ok "$([ $? = 0 ] && echo 1 || echo 0)" "E3 step_e174_v2 launch, the guard passes and launch_e174.sh prints its launch line: 0"
ok "$(grep -q "bash -s -- '$(sed -n 's/^RB_E174_DEADLINE=//p' "$T/window-q142kg.env" | tr -d "'" | sed 's/\\//g')'" "$T/calls.log" && echo 1 || echo 0)" \
   "E3 the launch passed the window file's E174 deadline to launch_e174.sh"
mkdir -p "$T/past"
env RB_OUT="$T/past" RB_LOCK="$T/lock-p.txt" bash "$D/s02_window_q142kg.sh" "$day" 22:00 23:30 > /dev/null 2>&1
sed -i.bak 's/^RB_LAST_START_EPOCH=.*/RB_LAST_START_EPOCH=1000/' "$T/past/window-q142kg.env"
c1=$(calls)
cp "$T/window-q142kg.env" "$T/window-q142kg.env.keep"; cp "$T/past/window-q142kg.env" "$T/window-q142kg.env"
run E4 16 -- "$S173" launch; e4=$?
cp "$T/window-q142kg.env.keep" "$T/window-q142kg.env"
ok "$([ $e4 = 0 ] && [ "$(calls)" = "$c1" ] && echo 1 || echo 0)" "E4 step_e173_v2 launch past the day's last start: 16, and no call was made"

# ---- F: waits
printf '== status: {"state": "halted"}\n' > "$T/fix/w-h.txt"; printf '== status: {"state": "ended"}\n' > "$T/fix/w-e.txt"; printf '== status: {"state": "running"}\n' > "$T/fix/w-r.txt"
run F1 16 FAKE_FIXTURE="$T/fix/w-h.txt" -- "$S174" wait; f1=$?
run F2 0 FAKE_FIXTURE="$T/fix/w-e.txt" -- "$S174" wait; f2=$?
run F3 17 FAKE_FIXTURE="$T/fix/w-r.txt" -- "$S174" wait; f3=$?
ok "$([ $f1 = 0 ] && [ $f2 = 0 ] && [ $f3 = 0 ] && echo 1 || echo 0)" "F  step_e174_v2 wait: halted 16, ended 0, still running 17"

# ---- G: the sync's copy (RB_REPO an empty scratch git repo, so its clean-tree read does not depend on the lab clone's state; the box quiet)
git init -q "$T/repo"
mk_home "$T/home-G"
run G1 14 FAKE_EXEC=1 FAKE_HOME="$T/home-G" FAKE_RSYNC=fail RB_REPO="$T/repo" -- "$S174" sync; g1=$?
run G2 11 FAKE_EXEC=1 FAKE_HOME="$T/home-G" FAKE_RSYNC=link RB_COPY_S=8 RB_REPO="$T/repo" -- "$S174" sync; g2=$?
ok "$([ $g1 = 0 ] && [ $g2 = 0 ] && grep -qE ' aifoundry1 needs a check$' "$T/lock-G2.txt" && grep -q 'QUIET-OK' "$T/out-G1/result.txt" && echo 1 || echo 0)" \
   "G  step_e174_v2 sync (the box quiet): a failed copy 14; a link in the copy 11 with its lock line"

# ---- H: step_e173_v2 tree
printf 'pull rc=0\nancestry rc=0\nporcelain lines: 0\nHEAD 0000000 2026-11-05\n' > "$T/fix/t-tree.txt"
printf 'HARNESS OK 250 + 3 binaries\n64 tiles; frozen inputs, Q139(k)'"'"'s files and tiles: OK\nblind8 OK: 89\npreflight rc=0 dmcmd_audit: GO (19 send site(s), 0 disallowed; allow-list: none)\nlist rc=0 (165 BURST runs listed)\n' > "$T/fix/t-pre.txt"
sed 's/dmcmd_audit: GO.*/dmcmd_audit: NO-GO/' "$T/fix/t-pre.txt" > "$T/fix/t-pre-nogo.txt"
cat "$T/fix/t-tree.txt" "$T/fix/t-pre.txt" > "$T/fix/t-all.txt"; cat "$T/fix/t-tree.txt" "$T/fix/t-pre-nogo.txt" > "$T/fix/t-nogo.txt"
run H1 0 FAKE_FIXTURE="$T/fix/t-all.txt" -- "$S173" tree; h1=$?
run H2 16 FAKE_FIXTURE="$T/fix/t-nogo.txt" -- "$S173" tree; h2=$?
ok "$([ $h1 = 0 ] && [ $h2 = 0 ] && echo 1 || echo 0)" "H  step_e173_v2 tree: clean 0; the device-command preflight NO-GO 16"

# ---- J: ours_live's pattern (the prelude is v1's, unchanged)
P=$(sed -n "s/.*pgrep -u \"\$(id -u)\" -f '\([^']*\)'.*/\1/p" "$T/out-B1/stdin.sh" | tail -n 1)
j=1
for cmd in "python3 tools/claims-v3/e173/queue_e173.py --slots s --runs build/e173/runs" "python3 tools/claims-v3/e174/run_e174.py --protocol p" \
           "python3 tools/claims-v3/e171/queue_e171.py --slots s" "bash tools/claims-v3/e172/session_e172.sh" "bash block_e172 16410" \
           "python3 tools/claims-v3/e170/queue_e170.py" "python3 tools/claims-v3/e165/queue_e165.py"; do
  printf '%s\n' "$cmd" | grep -qE "$P" || { j=0; echo "     not matched: $cmd"; }
done
printf '%s\n' "python3 tools/claims-v3/e173/score_e173.py" | grep -qE "$P" && { j=0; echo "     matched a desk scorer"; }
ok "$j" "J  ours_live's pattern names E171-E174's queue, runner, session and block processes and v3.1's, and not a desk scorer"

# ---- K: E174's restored aifoundry1 gates (the kits' verifier's fault 1)
J174=nekko/build/q141k/jobs/a1c0-check-e174
k=1
for proc in "bash tools/claims-v3/e172/queue_e172.sh --runs build/e172/runs" "bash tools/claims-v3/e172/session_e172.sh 1" \
            "bash tools/claims-v3/e172/block_e172.sh 17210" "python3 tools/claims-v3/e172/run_e172.py --protocol tools/claims-v3/e172/protocol.json"; do
  n=K1-$(printf '%s' "$proc" | sed -E 's/.*\/([a-z_0-9]+)\.(sh|py).*/\1/')
  mk_home "$T/home-$n"; day_out "$T/day-$n" clean
  run "$n" 14 FAKE_EXEC=1 FAKE_HOME="$T/home-$n" RB_OUT="$T/day-$n" FAKE_PGREP_CMD="$proc" FAKE_BOXCHECK="$T/fix/box-clean.txt" -- "$S174" check start || k=0
  grep -q 'JOB-REFUSED: a card session of ours runs on aifoundry1: no dry pass during a session' "$T/out-$n/result.txt" || { k=0; echo "     $n: no JOB-REFUSED line"; }
  [ ! -e "$T/home-$n/$J174.sh" ] && [ ! -e "$T/home-$n/$J174.pid" ] || { k=0; echo "     $n: the job was written"; }
  [ ! -e "$T/day-$n/a1c0-check-clean-e174.txt" ] || { k=0; echo "     $n: the stale clean file stayed"; }
done
ok "$k" "K1 check start beside E172's queue, session, block or runner (the generated job script run in a sandbox): 14 with JOB-REFUSED, no job written, the stale clean file removed"
mk_home "$T/home-K2"; day_out "$T/day-K2"
live=$$          # a live pid for a dry job still running (this test's own shell: alive throughout, nothing started for it)
echo "$live" > "$T/home-K2/nekko/build/q141k/jobs/a1-check-e172.pid"
run K2 14 FAKE_EXEC=1 FAKE_HOME="$T/home-K2" RB_OUT="$T/day-K2" FAKE_BOXCHECK="$T/fix/box-clean.txt" -- "$S174" check start; k2=$?
ok "$([ $k2 = 0 ] && grep -q 'JOB-REFUSED: 1 dry passes already run on aifoundry1' "$T/out-K2/result.txt" && [ ! -e "$T/home-K2/$J174.sh" ] && echo 1 || echo 0)" \
   "K2 check start while another dry pass of the runbook runs there (E172's box check): 14 with JOB-REFUSED, no job written"
mk_home "$T/home-K3"; day_out "$T/day-K3"
run K3 0 FAKE_EXEC=1 FAKE_HOME="$T/home-K3" RB_OUT="$T/day-K3" FAKE_BOXCHECK="$T/fix/box-clean.txt" -- "$S174" check start; k3=$?
ok "$([ $k3 = 0 ] && grep -q '^JOB-STARTED a1c0-check-e174' "$T/out-K3/result.txt" && [ "$(cat "$T/home-K3/$J174.rc" 2>/dev/null)" = 0 ] \
      && grep -q '^BOX-CHECK-CLEAN$' "$T/home-K3/$J174.out" && echo 1 || echo 0)" \
   "K3 check start with nothing of ours on aifoundry1: 0; the detached job ran check_box_e174.sh, read it clean on the box and ended rc 0"
run K3b 0 FAKE_EXEC=1 FAKE_HOME="$T/home-K3" RB_OUT="$T/day-K3" RB_WAIT_LOOP_S=20 -- "$S174" check wait; k3b=$?
ok "$([ $k3b = 0 ] && [ "$(cut -d' ' -f1-2 "$T/day-K3/a1c0-check-clean-e174.txt" 2>/dev/null)" = "$day clean" ] && echo 1 || echo 0)" \
   "K3 check wait: 0, and RB_OUT/a1c0-check-clean-e174.txt names the window's day"
mk_home "$T/home-K4"; day_out "$T/day-K4"
run K4s 0 FAKE_EXEC=1 FAKE_HOME="$T/home-K4" RB_OUT="$T/day-K4" FAKE_BOXCHECK="$T/fix/box-nogo.txt" -- "$S174" check start > /dev/null
run K4 16 FAKE_EXEC=1 FAKE_HOME="$T/home-K4" RB_OUT="$T/day-K4" RB_WAIT_LOOP_S=20 -- "$S174" check wait; k4=$?
ok "$([ $k4 = 0 ] && [ "$(cat "$T/home-K4/$J174.rc" 2>/dev/null)" = 1 ] && grep -q 'BOX-CHECK-UNCLEAN: preflight' "$T/out-K4/result.txt" \
      && grep -q 'did not read clean: preflight' "$T/out-K4/result.txt" && [ ! -e "$T/day-K4/a1c0-check-clean-e174.txt" ] && echo 1 || echo 0)" \
   "K4 a box check whose preflight reads NO-GO: the job ends rc 1 on the box, check wait 16, and no clean file"
mk_home "$T/home-K5"; job_state "$T/home-K5" 0 old; day_out "$T/day-K5"
run K5 10 FAKE_EXEC=1 FAKE_HOME="$T/home-K5" RB_OUT="$T/day-K5" RB_WAIT_LOOP_S=20 -- "$S174" check wait; k5=$?
ok "$([ $k5 = 0 ] && grep -q 'JOB-UNKNOWN a1c0-check-e174: not started today' "$T/out-K5/result.txt" && [ ! -e "$T/day-K5/a1c0-check-clean-e174.txt" ] && echo 1 || echo 0)" \
   "K5 check wait on a check job from another day: 10 (JOB-UNKNOWN), and no clean file"
day_out "$T/day-K6"; c1=$(calls)
run K6 10 FAKE_EXEC=1 FAKE_HOME="$T/home-K3" RB_OUT="$T/day-K6" FAKE_FIXTURE="$T/fix/l-ok.txt" -- "$S174" launch; k6=$?
ok "$([ $k6 = 0 ] && [ "$(calls)" = "$c1" ] && grep -q 'has not read E174.s box check clean today' "$T/out-K6/result.txt" && echo 1 || echo 0)" \
   "K6 launch with no clean check today: 10, and no call was made"
day_out "$T/day-K7"; echo "2026-11-01 clean (another day)" > "$T/day-K7/a1c0-check-clean-e174.txt"; c1=$(calls)
run K7 10 FAKE_EXEC=1 FAKE_HOME="$T/home-K3" RB_OUT="$T/day-K7" FAKE_FIXTURE="$T/fix/l-ok.txt" -- "$S174" launch; k7=$?
ok "$([ $k7 = 0 ] && [ "$(calls)" = "$c1" ] && echo 1 || echo 0)" "K7 launch with a clean check of another day: 10, and no call was made"
c1=$(lines)
run K8 0 FAKE_EXEC=1 FAKE_HOME="$T/home-K3" RB_OUT="$T/day-K3" FAKE_FIXTURE="$T/fix/l-ok.txt" -- "$S174" launch; k8=$?
g=$(ls "$T"/day-K3/calls/*-guard.sh 2>/dev/null | tail -n 1)
ok "$([ $k8 = 0 ] && grep -q '^GUARD-OK' "$T/out-K8/result.txt" && grep -q 'job_ok_today a1c0-check-e174' "$g" && grep -q 'jobs_live' "$g" && grep -q 'ours_live' "$g" \
      && grep -q 'IDENTITY-STOP' "$g" && [ "$(since_calls "$c1" | grep -c ' ssh ')" = 3 ] && echo 1 || echo 0)" \
   "K8 launch after K3's clean check (the day's file, and the box's job rc 0 today): the guard reads GUARD-OK, then launch_e174.sh: 0 (probe, guard, launch)"
k9=1
for c in norc drylive e172live; do
  mk_home "$T/home-K9$c"; day_out "$T/day-K9$c" clean
  envx=()
  [ "$c" != norc ] && job_state "$T/home-K9$c" 0
  if [ "$c" = drylive ]; then echo "$live" > "$T/home-K9$c/nekko/build/q141k/jobs/a1-check-e172.pid"; fi
  [ "$c" = e172live ] && envx=(FAKE_PGREP_CMD="bash tools/claims-v3/e172/session_e172.sh 1")
  c1=$(lines)
  run "K9$c" 10 FAKE_EXEC=1 FAKE_HOME="$T/home-K9$c" RB_OUT="$T/day-K9$c" FAKE_FIXTURE="$T/fix/l-ok.txt" ${envx[@]+"${envx[@]}"} -- "$S174" launch || k9=0
  [ "$(since_calls "$c1" | grep -c ' ssh ')" = 2 ] || { k9=0; echo "     K9$c: launch_e174.sh was sent"; }
  grep -q '^\[e174_launch_q142kg2\] STOP: refused on the box: REFUSED' "$T/out-K9$c/result.txt" || { k9=0; echo "     K9$c: no REFUSED line"; }
done
ok "$k9" "K9 launch with the day's clean file but, on the box, no check job ended rc 0 today, or a dry pass running, or E172's session alive: 10, launch_e174.sh never sent"
mk_home "$T/home-K10"; job_state "$T/home-K10" 0; day_out "$T/day-K10" clean
run K10 16 FAKE_EXEC=1 FAKE_HOME="$T/home-K10" RB_OUT="$T/day-K10" FAKE_BOOT="2026-11-05 01:00:00" FAKE_FIXTURE="$T/fix/l-ok.txt" -- "$S174" launch; k10=$?
ok "$([ $k10 = 0 ] && grep -q 'IDENTITY-STOP: aifoundry1 booted' "$T/out-K10/result.txt" && echo 1 || echo 0)" "K10 launch on a host booted after the firmware read of record: 16 at the guard"
mk_home "$T/home-K11"
c1=$(lines)
run K11 10 FAKE_EXEC=1 FAKE_HOME="$T/home-K11" FAKE_PGREP_CMD="python3 tools/claims-v3/e172/run_e172.py --protocol p" RB_REPO="$T/repo" -- "$S174" sync; k11=$?
ok "$([ $k11 = 0 ] && [ "$(since_calls "$c1" | grep -c ' rsync ')" = 0 ] && grep -q 'REFUSED: a card session of ours runs on aifoundry1' "$T/out-K11/result.txt" && echo 1 || echo 0)" \
   "K11 sync beside E172's runner: 10, and no rsync was made"
run K12 0 FAKE_EXEC=1 FAKE_HOME="$T/home-K11" RB_REPO="$T/repo" -- "$S174" sync; k12=$?
ok "$([ $k12 = 0 ] && grep -q 'synced E174' "$T/out-K12/result.txt" && echo 1 || echo 0)" "K12 sync with nothing of ours on aifoundry1: 0"
ok "$(none_left)" "K  no stand-in process left after the gate cases"

# ---- L: v2's C-log list through rb_common_v2.sh's gate (the kits' verifier's fault 7)
mk_session() {  # mk_session <runs dir> <session> <work launches> <with a C log 0|1> [<runs records>]
  mkdir -p "$1/$2"; : > "$1/$2/launches.jsonl"
  local i=0; while [ "$i" -lt "$3" ]; do echo '{"role": "work"}' >> "$1/$2/launches.jsonl"; i=$((i + 1)); done
  gzip -n "$1/$2/launches.jsonl"; echo '{"dry": false}' > "$1/$2/session.json"
  [ "$4" = 1 ] && { echo '{}' > "$1/$2/c-log.jsonl"; gzip -n "$1/$2/c-log.jsonl"; }
  i=0; while [ "$i" -lt "${5:-0}" ]; do echo '{"run": 1}' >> "$1/$2/runs.jsonl"; i=$((i + 1)); done
  echo "{\"kind\": \"session_start\", \"name\": \"$2\"}" >> "$1/queue.jsonl"
}
mk_end() { echo "{\"kind\": \"session_end\", \"name\": \"$2\", \"rc\": $3, \"end\": {\"exit\": $3, \"reason\": \"$4\", \"card_min\": $5}}" >> "$1/queue.jsonl"; }
mk_check() { printf '{"summary": {"launches": 2, "PASS": 2, "ROUNDING": 0, "UNMODELLED": 0, "FAIL": 0, "all_pass": true}, "launches": [{}, {}]}\n' > "$1"; }
gate() {  # gate <case> <runs dir> <ccheck dir> <since>
  cat > "$T/gate-$1.sh" <<EOF
. "$D/rb_common_v2.sh"
rb_init gate_$1
rb_cc_gate GATE "$4" "$2" "$3"
EOF
  env RB_OUT="$T/out-gate-$1" RB_LOCK="$T/lock-gate.txt" bash "$T/gate-$1.sh" > "$T/gate-$1.txt" 2>&1
}
v1list() { /usr/bin/python3 -B "$D/cclist_q142kg.py" "$1" "$2" > "$T/v1-$3.txt" 2>&1; }
base() {  # base <data dir>: v1's I-case session set (stoptest-die, stoptest-board, smoke, s1) with the checks
  mkdir -p "$1/runs"
  mk_session "$1/runs" stoptest-die 0 0; mk_end "$1/runs" stoptest-die 4 "safety:die 69 C >= 30 C" 0.0
  mk_session "$1/runs" stoptest-board 1 1; mk_end "$1/runs" stoptest-board 4 "safety:board 28.6 W > 25 W on 1 samples" 0.1
  mk_session "$1/runs" smoke 2 1 2; mk_end "$1/runs" smoke 0 done 0.8
  mk_session "$1/runs" s1 9 1 9; mk_end "$1/runs" s1 0 done 28.3
  mk_check "$1/ccheck-stoptest-board.json"; mk_check "$1/ccheck-smoke.json"; mk_check "$1/ccheck-s1.json"
}
since=$(( $(date +%s) - 60 ))
for c in ok noclog stale resume; do
  G="$T/data-$c"; base "$G"
  [ "$c" = noclog ] && rm -f "$G/runs/smoke/c-log.jsonl.gz"
  [ "$c" = resume ] && mk_session "$G/runs" s2 3 1 3
done
gate ok "$T/data-ok/runs" "$T/data-ok" "$since"; i1=$?
gate noclog "$T/data-noclog/runs" "$T/data-noclog" "$since"; i2=$?
gate stale "$T/data-stale/runs" "$T/data-stale" "$(( $(date +%s) + 3600 ))"; i3=$?
gate resume "$T/data-resume/runs" "$T/data-resume" "$since"; i4=$?
ok "$([ $i1 = 0 ] && grep -q '3 listed sessions carry a C log' "$T/gate-ok.txt" && [ $i2 = 14 ] && grep -q 'MISSING-CLOG smoke' "$T/gate-noclog.txt" \
      && [ $i3 = 14 ] && grep -q 'CCHECK-STALE' "$T/gate-stale.txt" && [ $i4 = 14 ] && grep -q 'CCHECK-MISSING' "$T/gate-resume.txt" && echo 1 || echo 0)" \
   "L0 v1's four I cases through v2's gate: every listed session checked 0; smoke without a C log 14; a stale check 14; a resume s2 unchecked 14"
G="$T/data-L1"; base "$G"; rm -f "$G/runs/queue.jsonl"; rm -rf "$G/runs/smoke"
gate L1 "$G/runs" "$G" "$since"; l1=$?; v1list "$G/runs" "$G" L1; l1v=$?
ok "$([ $l1 = 14 ] && grep -q 'MISSING-QUEUE' "$T/gate-L1.txt" && [ $l1v = 0 ] && echo 1 || echo 0)" \
   "L1 no queue.jsonl and no smoke directory (the verifier's V7): v2 14 (MISSING-QUEUE); v1's list passed it ($l1v)"
G="$T/data-L2"; base "$G"; rm -f "$G/runs/s1/launches.jsonl.gz" "$G/runs/s1/c-log.jsonl.gz"
gate L2 "$G/runs" "$G" "$since"; l2=$?; v1list "$G/runs" "$G" L2; l2v=$?
ok "$([ $l2 = 14 ] && grep -q 'V2-ADDED s1: (a)' "$T/gate-L2.txt" && grep -q 'MISSING-CLOG s1' "$T/gate-L2.txt" && [ $l2v = 0 ] && echo 1 || echo 0)" \
   "L2 s1's launches.jsonl and C log lost, its runs.jsonl there (V8): v2 14 (s1 added by its runs); v1's list passed it ($l2v)"
G="$T/data-L3"; base "$G"; rm -f "$G/runs/stoptest-board/launches.jsonl.gz" "$G/runs/stoptest-board/c-log.jsonl.gz"
gate L3 "$G/runs" "$G" "$since"; l3=$?; v1list "$G/runs" "$G" L3; l3v=$?
ok "$([ $l3 = 14 ] && grep -qE 'V2-ADDED stoptest-board: \((b|c)\)' "$T/gate-L3.txt" && grep -q 'MISSING-CLOG stoptest-board' "$T/gate-L3.txt" && [ $l3v = 0 ] && echo 1 || echo 0)" \
   "L3 stoptest-board's launches and C log lost, its board stop in the queue's record: v2 14; v1's list passed it ($l3v)"
G="$T/data-L4"; base "$G"; rm -f "$G/runs/s1/launches.jsonl.gz" "$G/runs/s1/c-log.jsonl.gz" "$G/runs/s1/runs.jsonl"
gate L4 "$G/runs" "$G" "$since"; l4=$?
ok "$([ $l4 = 14 ] && grep -q 'V2-ADDED s1: (b)' "$T/gate-L4.txt" && echo 1 || echo 0)" \
   "L4 s1's launches, runs and C log lost, 28.3 card-minutes in the queue's record: v2 14 (s1 added by its card-minutes)"
G="$T/data-L5"; base "$G"; rm -rf "$G/runs/s1"; mkdir -p "$G/runs/s1"; echo '{"dry": false}' > "$G/runs/s1/session.json"
sed -i.bak 's/"name": "s1", "rc": 0, "end": {"exit": 0, "reason": "done", "card_min": 28.3}/"name": "s1", "rc": 0, "end": {"exit": 0, "reason": "slot", "card_min": 0.0}/' "$G/runs/queue.jsonl"
mk_session "$G/runs" s2 9 1 9; mk_check "$G/ccheck-s2.json"; rm -f "$G/ccheck-s1.json"
gate L5 "$G/runs" "$G" "$since"; l5=$?
ok "$([ $l5 = 0 ] && grep -q 'REQUIRED s2' "$T/gate-L5.txt" && ! grep -q 'REQUIRED s1' "$T/gate-L5.txt" && echo 1 || echo 0)" \
   "L5 an s1 that ran nothing (no runs, no launches, 0 card-minutes) beside an s2 that ran everything: v2 0 (s2 required, s1 not): no false stop"
G="$T/data-L6"; base "$G"; mk_session "$G/runs" s2 4 0 0; grep -v '"name": "s2"' "$G/runs/queue.jsonl" > "$G/q.tmp"; mv "$G/q.tmp" "$G/runs/queue.jsonl"
gate L6 "$G/runs" "$G" "$since"; l6=$?; v1list "$G/runs" "$G" L6; l6v=$?
ok "$([ $l6 = 14 ] && grep -q 'V2-ADDED s2: (d)' "$T/gate-L6.txt" && grep -q 'MISSING-CLOG s2' "$T/gate-L6.txt" && [ $l6v = 0 ] && echo 1 || echo 0)" \
   "L6 an s2 directory with work launches that the queue's record does not start, and no C log: v2 14; v1's list passed it ($l6v)"
l7=1
for p in "docs/reports/data/2026-11-04-e165-blind7-aifoundry2:aifoundry2" "docs/reports/data/2026-11-04-e170-blind7-card0:aifoundry1-c0"; do
  dd=$REPO/${p%%:*}; q=$dd/${p##*:}; nm=$(basename "$dd")
  gate "L7-$nm" "$q" "$dd" 0 || { l7=0; echo "     $nm: the v2 gate rc $?: $(tail -n 2 "$T/gate-L7-$nm.txt" | tr '\n' ' ' | cut -c1-200)"; }
  v1list "$q" "$dd" "L7-$nm"
  a1=$(grep '^REQUIRED' "$T/v1-L7-$nm.txt" | awk '{print $2}' | sort | tr '\n' ' ')
  a2=$(grep '^REQUIRED' "$T/gate-L7-$nm.txt" | awk '{print $2}' | sort | tr '\n' ' ')
  [ -n "$a1" ] && [ "$a1" = "$a2" ] || { l7=0; echo "     $nm: v1 [$a1] v2 [$a2]"; }
  echo "     $nm: v1 and v2 both list [$a1]"
done
ok "$l7" "L7 the parents' committed sessions (E165 on aifoundry2, E170 on card 0) through the whole v2 gate: 0, v2's list equal to v1's, every listed check finished"

ok "$(none_left)" "   no stand-in process left at the end"
echo "selftest_steps_q142kg_v2: $((N - F)) of $N checks pass"
[ "$F" -eq 0 ]
