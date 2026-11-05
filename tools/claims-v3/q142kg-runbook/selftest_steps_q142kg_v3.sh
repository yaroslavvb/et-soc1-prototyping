#!/usr/bin/env bash
# Q142(v2) fix pass, Thu 5 Nov 2026: the desk test of the v3 step drivers (tools/claims-v3/e173/box/step_e173_v3.sh,
# tools/claims-v3/e174/box/step_e174_v3.sh), this directory's rb_common_v3.sh, cclist_q142kg_v3.py and list_steps_q142kg_v3.sh.
# selftest_steps_q142kg_v2.sh (34436d68) stays as committed and still covers every step v3 hands to v2. It never reaches a lab box: logging
# stand-ins for `ssh` and `rsync`, first on PATH in the scratch dir, record any call (none is expected). The cases:
#   A  the v3 dry listing (list_steps_q142kg_v3.sh): the window and all 17 steps exit 0 and call nothing; it prints each box's prelude once at the
#      top (ours_live, jobs_live and hold_read defined there for aifoundry2 and aifoundry1: the first verifier of v2's fault 5); each collect lists
#      cclist_q142kg_v3.py and is named _q142kg3
#   D  every step but collect is v2's: the dry listing of each of the 15 through v3 is byte for byte the one through v2
#   L  v3's C-log list through rb_common_v3.sh's gate: v2's L0-L7 again (each the same result), and
#      L8  the verifier's D3: a session the queue's record names only in its session_end (9.5 card-minutes), its start line and its directory lost:
#          v2's gate passed it (0); v3's stops it (14: V3-ADDED, MISSING-CLOG);
#      L9  the verifier's D4 (control): the directory there, its launches lost, 9.5 card-minutes: 14 by v2's rule (b), as in v2;
#      L10 stoptest-die named only by its session_end, its directory lost: not required (v1's rule for stoptest-die): 0;
#      L11 on every case above, v3's REQUIRED list less its V3-ADDED sessions is v2's REQUIRED list (cclist_q142kg_v2.py on the same dirs).
#
#   bash tools/claims-v3/q142kg-runbook/selftest_steps_q142kg_v3.sh <a new, empty scratch dir> > tools/claims-v3/q142kg-runbook/logs/selftest-steps-v3.txt
# SPDX-License-Identifier: Apache-2.0
set -u
T=${1:?usage: selftest_steps_q142kg_v3.sh <a new, empty scratch dir>}
[ -d "$T" ] && [ -n "$(ls -A "$T" 2>/dev/null)" ] && { echo "refused: $T is not empty"; exit 2; }
mkdir -p "$T/bin" || exit 2
D=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
REPO=$(cd "$D/../../.." && pwd)
S173v2="$REPO/tools/claims-v3/e173/box/step_e173_v2.sh"; S173="$REPO/tools/claims-v3/e173/box/step_e173_v3.sh"
S174v2="$REPO/tools/claims-v3/e174/box/step_e174_v2.sh"; S174="$REPO/tools/claims-v3/e174/box/step_e174_v3.sh"
export FAKE_LOG="$T/calls.log"
printf '#!/bin/bash\necho "$(date +%%s) ssh $*" >> "$FAKE_LOG"\necho "a stand-in: no call is expected here" >&2\nexit 97\n' > "$T/bin/ssh"
printf '#!/bin/bash\necho "$(date +%%s) rsync $*" >> "$FAKE_LOG"\necho "a stand-in: no call is expected here" >&2\nexit 97\n' > "$T/bin/rsync"
chmod +x "$T/bin/ssh" "$T/bin/rsync"
export PATH="$T/bin:$PATH"
: > "$FAKE_LOG"
N=0; F=0
ok() { N=$((N + 1)); if [ "$1" = 1 ]; then echo "PASS $2"; else F=$((F + 1)); echo "FAIL $2"; fi; }
calls() { grep -c . "$FAKE_LOG" | tr -d ' '; }

# ---- A: the v3 dry listing, with each box's prelude printed once at the top
bash "$D/list_steps_q142kg_v3.sh" "$T/listing" > "$T/listing.txt" 2>&1; arc=$?
L=$T/listing.txt
top=$(awk '/^################/{exit} {print}' "$L")
ok "$([ "$arc" = 0 ] && grep -q '^dry listing: 0 step(s) exited non-zero$' "$L" && [ "$(grep -c '^(exit 0)$' "$L")" = 18 ] && echo 1 || echo 0)" \
   "A  the v3 dry listing: the window and all 17 steps exit 0 ($(grep -c '^(exit 0)$' "$L") of 18)"
ok "$([ "$(calls)" = 0 ] && echo 1 || echo 0)" "A  the dry listing called no ssh and no rsync ($(calls) calls)"
np=$(printf '%s\n' "$top" | grep -c '^---- the runbook.s prelude for aifoundry[12]:')
no=$(printf '%s\n' "$top" | grep -c '^    | ours_live() {'); nj=$(printf '%s\n' "$top" | grep -c '^    | jobs_live() {'); nh=$(printf '%s\n' "$top" | grep -c '^    | hold_read() {')
nm=$(grep -c 'printed once at the top of the listing' "$L")
ok "$([ "$np" = 2 ] && [ "$no" -ge 2 ] && [ "$nj" = 2 ] && [ "$nh" = 2 ] && [ "$nm" -ge 13 ] && echo 1 || echo 0)" \
   "A  the preludes for aifoundry2 and aifoundry1 are printed once at the top ($np; ours_live $no definitions with q142kg's redefinition, jobs_live $nj, hold_read $nh), above the $nm lines that point to them"
ok "$(printf '%s\n' "$top" | grep -q "queue|run)_e17\[0-9\]" && echo 1 || echo 0)" "A  the printed prelude carries q142kg's ours_live, which names E171-E174's processes"
c3=$(grep -c 'cclist_q142kg_v3.py' "$L"); c2=$(grep -c 'cclist_q142kg_v2.py' "$L"); k3=$(grep -c '_q142kg3\]' "$L")
ok "$([ "$c3" -ge 2 ] && [ "$c2" = 0 ] && [ "$k3" -ge 2 ] && echo 1 || echo 0)" "A  each collect lists v3's C-log list ($c3 lines; v2's $c2) and is named _q142kg3 ($k3 lines)"

# ---- D: every step but collect is v2's, byte for byte
day=$(TZ=America/Los_Angeles date -v+1d +%F 2>/dev/null || TZ=America/Los_Angeles date -d tomorrow +%F)
mkdir -p "$T/dw"; env RB_OUT="$T/dw" RB_LOCK="$T/dw/lock.txt" RB_DRY=1 bash "$D/s02_window_q142kg.sh" "$day" 22:00 23:30 > /dev/null 2>&1
same=0; tot=0
for pair in "e173:look" "e173:tree" "e173:dry start" "e173:dry wait" "e173:launch" "e173:launch subset" "e173:wait" \
            "e174:look" "e174:sync" "e174:check start" "e174:check wait" "e174:launch" "e174:launch subset" "e174:wait" "e174:pull"; do
  r=${pair%%:*}; st=${pair#*:}; tot=$((tot + 1))
  [ "$r" = e173 ] && { a=$S173v2; b=$S173; } || { a=$S174v2; b=$S174; }
  for v in v2 v3; do mkdir -p "$T/d-$v"; cp "$T/dw/window-q142kg.env" "$T/d-$v/"; done
  # shellcheck disable=SC2086
  env RB_OUT="$T/d-v2" RB_LOCK="$T/d-v2/lock.txt" RB_DRY=1 bash "$a" $st > "$T/d-v2.txt" 2>&1
  # shellcheck disable=SC2086
  env RB_OUT="$T/d-v3" RB_LOCK="$T/d-v3/lock.txt" RB_DRY=1 bash "$b" $st > "$T/d-v3.txt" 2>&1
  sed "s#$T/d-v[23]#<RB_OUT>#g" "$T/d-v2.txt" > "$T/d-v2.m"; sed "s#$T/d-v[23]#<RB_OUT>#g" "$T/d-v3.txt" > "$T/d-v3.m"
  if cmp -s "$T/d-v2.m" "$T/d-v3.m" && [ -s "$T/d-v3.m" ]; then same=$((same + 1)); else echo "     $pair differs: $(diff "$T/d-v2.m" "$T/d-v3.m" | head -n 3 | tr '\n' ' ' | cut -c1-200)"; fi
done
ok "$([ "$same" = "$tot" ] && [ "$(calls)" = 0 ] && echo 1 || echo 0)" "D  every step but collect through v3 lists exactly what v2 lists ($same of $tot byte for byte; $(calls) calls)"

# ---- L: v3's C-log list through rb_common_v3.sh's gate
mk_session() {  # mk_session <runs dir> <session> <work launches> <with a C log 0|1> [<runs records>]   (v2's test's, copied)
  mkdir -p "$1/$2"; : > "$1/$2/launches.jsonl"
  local i=0; while [ "$i" -lt "$3" ]; do echo '{"role": "work"}' >> "$1/$2/launches.jsonl"; i=$((i + 1)); done
  gzip -n "$1/$2/launches.jsonl"; echo '{"dry": false}' > "$1/$2/session.json"
  [ "$4" = 1 ] && { echo '{}' > "$1/$2/c-log.jsonl"; gzip -n "$1/$2/c-log.jsonl"; }
  i=0; while [ "$i" -lt "${5:-0}" ]; do echo '{"run": 1}' >> "$1/$2/runs.jsonl"; i=$((i + 1)); done
  echo "{\"kind\": \"session_start\", \"name\": \"$2\"}" >> "$1/queue.jsonl"
}
mk_end() { echo "{\"kind\": \"session_end\", \"name\": \"$2\", \"rc\": $3, \"end\": {\"exit\": $3, \"reason\": \"$4\", \"card_min\": $5}}" >> "$1/queue.jsonl"; }
mk_check() { printf '{"summary": {"launches": 2, "PASS": 2, "ROUNDING": 0, "UNMODELLED": 0, "FAIL": 0, "all_pass": true}, "launches": [{}, {}]}\n' > "$1"; }
gate() {  # gate <v2|v3> <case> <runs dir> <ccheck dir> <since>
  local v=$1 c=$2
  cat > "$T/gate-$v-$c.sh" <<EOF
. "$D/rb_common_$v.sh"
rb_init gate_$c
rb_cc_gate GATE "$5" "$3" "$4"
EOF
  env RB_OUT="$T/out-gate-$v-$c" RB_LOCK="$T/lock-gate.txt" bash "$T/gate-$v-$c.sh" > "$T/gate-$v-$c.txt" 2>&1
}
SUB=0; SUBN=0
subset() {  # subset <case> <runs dir> <ccheck dir>: v3's REQUIRED less its V3-ADDED equals v2's REQUIRED (L11)
  /usr/bin/python3 -B "$D/cclist_q142kg_v2.py" "$2" "$3" > "$T/l2-$1.txt" 2>&1
  /usr/bin/python3 -B "$D/cclist_q142kg_v3.py" "$2" "$3" > "$T/l3-$1.txt" 2>&1
  local a b
  a=$(grep '^REQUIRED' "$T/l2-$1.txt" | awk '{print $2}' | sort | tr '\n' ' ')
  b=$(grep '^REQUIRED' "$T/l3-$1.txt" | awk '{print $2}' | grep -vxF -f <(sed -n 's/^V3-ADDED \([^:]*\):.*/\1/p' "$T/l3-$1.txt"; echo '#') | sort | tr '\n' ' ')
  SUBN=$((SUBN + 1)); [ "$a" = "$b" ] && SUB=$((SUB + 1)) || echo "     L11 $1: v2 [$a] v3 less V3-ADDED [$b]"
}
base() {  # base <data dir>: v2's test's I-case session set (stoptest-die, stoptest-board, smoke, s1) with the checks
  mkdir -p "$1/runs"
  mk_session "$1/runs" stoptest-die 0 0; mk_end "$1/runs" stoptest-die 4 "safety:die 69 C >= 30 C" 0.0
  mk_session "$1/runs" stoptest-board 1 1; mk_end "$1/runs" stoptest-board 4 "safety:board 28.6 W > 25 W on 1 samples" 0.1
  mk_session "$1/runs" smoke 2 1 2; mk_end "$1/runs" smoke 0 done 0.8
  mk_session "$1/runs" s1 9 1 9; mk_end "$1/runs" s1 0 done 28.3
  mk_check "$1/ccheck-stoptest-board.json"; mk_check "$1/ccheck-smoke.json"; mk_check "$1/ccheck-s1.json"
}
since=$(( $(date +%s) - 60 ))
both() {  # both <case> <runs dir> <ccheck dir> <since>: the gate through v2 and v3, and L11 on the case; sets r2 and r3
  gate v2 "$1" "$2" "$3" "$4"; r2=$?; gate v3 "$1" "$2" "$3" "$4"; r3=$?; subset "$1" "$2" "$3"
}
for c in ok noclog stale resume; do
  G="$T/data-$c"; base "$G"
  [ "$c" = noclog ] && rm -f "$G/runs/smoke/c-log.jsonl.gz"
  [ "$c" = resume ] && mk_session "$G/runs" s2 3 1 3
done
both ok "$T/data-ok/runs" "$T/data-ok" "$since"; i1=$r3; j1=$r2
both noclog "$T/data-noclog/runs" "$T/data-noclog" "$since"; i2=$r3; j2=$r2
both stale "$T/data-stale/runs" "$T/data-stale" "$(( $(date +%s) + 3600 ))"; i3=$r3; j3=$r2
both resume "$T/data-resume/runs" "$T/data-resume" "$since"; i4=$r3; j4=$r2
ok "$([ "$i1.$i2.$i3.$i4" = "0.14.14.14" ] && [ "$j1.$j2.$j3.$j4" = "$i1.$i2.$i3.$i4" ] && grep -q '3 listed sessions carry a C log' "$T/gate-v3-ok.txt" \
      && grep -q 'MISSING-CLOG smoke' "$T/gate-v3-noclog.txt" && grep -q 'CCHECK-STALE' "$T/gate-v3-stale.txt" && grep -q 'CCHECK-MISSING' "$T/gate-v3-resume.txt" && echo 1 || echo 0)" \
   "L0 v1's four I cases through v3's gate (0, 14, 14, 14), each as through v2's ($j1, $j2, $j3, $j4)"
G="$T/data-L1"; base "$G"; rm -f "$G/runs/queue.jsonl"; rm -rf "$G/runs/smoke"
gate v2 L1 "$G/runs" "$G" "$since"; l1v2=$?; gate v3 L1 "$G/runs" "$G" "$since"; l1=$?
ok "$([ "$l1" = 14 ] && [ "$l1v2" = 14 ] && grep -q 'MISSING-QUEUE' "$T/gate-v3-L1.txt" && echo 1 || echo 0)" "L1 no queue.jsonl and no smoke directory: v3 14 (MISSING-QUEUE), as v2 ($l1v2)"
G="$T/data-L2"; base "$G"; rm -f "$G/runs/s1/launches.jsonl.gz" "$G/runs/s1/c-log.jsonl.gz"
both L2 "$G/runs" "$G" "$since"
ok "$([ "$r3" = 14 ] && [ "$r2" = 14 ] && grep -q 'V2-ADDED s1: (a)' "$T/gate-v3-L2.txt" && grep -q 'MISSING-CLOG s1' "$T/gate-v3-L2.txt" && echo 1 || echo 0)" \
   "L2 s1's launches.jsonl and C log lost, its runs.jsonl there: v3 14 (s1 added by v2's rule (a)), as v2 ($r2)"
G="$T/data-L3"; base "$G"; rm -f "$G/runs/stoptest-board/launches.jsonl.gz" "$G/runs/stoptest-board/c-log.jsonl.gz"
both L3 "$G/runs" "$G" "$since"
ok "$([ "$r3" = 14 ] && [ "$r2" = 14 ] && grep -qE 'V2-ADDED stoptest-board: \((b|c)\)' "$T/gate-v3-L3.txt" && echo 1 || echo 0)" \
   "L3 stoptest-board's launches and C log lost, its board stop in the queue's record: v3 14, as v2 ($r2)"
G="$T/data-L4"; base "$G"; rm -f "$G/runs/s1/launches.jsonl.gz" "$G/runs/s1/c-log.jsonl.gz" "$G/runs/s1/runs.jsonl"
both L4 "$G/runs" "$G" "$since"
ok "$([ "$r3" = 14 ] && [ "$r2" = 14 ] && grep -q 'V2-ADDED s1: (b)' "$T/gate-v3-L4.txt" && echo 1 || echo 0)" "L4 s1's launches, runs and C log lost, 28.3 card-minutes: v3 14, as v2 ($r2)"
G="$T/data-L5"; base "$G"; rm -rf "$G/runs/s1"; mkdir -p "$G/runs/s1"; echo '{"dry": false}' > "$G/runs/s1/session.json"
sed -i.bak 's/"name": "s1", "rc": 0, "end": {"exit": 0, "reason": "done", "card_min": 28.3}/"name": "s1", "rc": 0, "end": {"exit": 0, "reason": "slot", "card_min": 0.0}/' "$G/runs/queue.jsonl"
mk_session "$G/runs" s2 9 1 9; mk_check "$G/ccheck-s2.json"; rm -f "$G/ccheck-s1.json"
both L5 "$G/runs" "$G" "$since"
ok "$([ "$r3" = 0 ] && [ "$r2" = 0 ] && grep -q 'REQUIRED s2' "$T/gate-v3-L5.txt" && ! grep -q 'REQUIRED s1' "$T/gate-v3-L5.txt" && echo 1 || echo 0)" \
   "L5 an s1 that ran nothing beside an s2 that ran everything: v3 0 (s2 required, s1 not), as v2 ($r2): no false stop"
G="$T/data-L6"; base "$G"; mk_session "$G/runs" s2 4 0 0; grep -v '"name": "s2"' "$G/runs/queue.jsonl" > "$G/q.tmp"; mv "$G/q.tmp" "$G/runs/queue.jsonl"
both L6 "$G/runs" "$G" "$since"
ok "$([ "$r3" = 14 ] && [ "$r2" = 14 ] && grep -q 'V2-ADDED s2: (d)' "$T/gate-v3-L6.txt" && echo 1 || echo 0)" \
   "L6 an s2 directory with work launches that the queue's record does not start, no C log: v3 14, as v2 ($r2)"
l7=1
for p in "docs/reports/data/2026-11-04-e165-blind7-aifoundry2:aifoundry2" "docs/reports/data/2026-11-04-e170-blind7-card0:aifoundry1-c0"; do
  dd=$REPO/${p%%:*}; q=$dd/${p##*:}; nm=$(basename "$dd")
  gate v3 "L7-$nm" "$q" "$dd" 0 || { l7=0; echo "     $nm: the v3 gate rc $?: $(tail -n 2 "$T/gate-v3-L7-$nm.txt" | tr '\n' ' ' | cut -c1-200)"; }
  /usr/bin/python3 -B "$D/cclist_q142kg.py" "$q" "$dd" > "$T/v1-L7-$nm.txt" 2>&1
  subset "L7-$nm" "$q" "$dd"
  a1=$(grep '^REQUIRED' "$T/v1-L7-$nm.txt" | awk '{print $2}' | sort | tr '\n' ' ')
  a3=$(grep '^REQUIRED' "$T/gate-v3-L7-$nm.txt" | awk '{print $2}' | sort | tr '\n' ' ')
  [ -n "$a1" ] && [ "$a1" = "$a3" ] && ! grep -q 'V3-ADDED' "$T/gate-v3-L7-$nm.txt" || { l7=0; echo "     $nm: v1 [$a1] v3 [$a3]"; }
  echo "     $nm: v1 and v3 both list [$a1]"
done
ok "$l7" "L7 the parents' committed sessions (E165 on aifoundry2, E170 on card 0) through the whole v3 gate: 0, v3's list equal to v1's and v2's, no V3-ADDED"
G="$T/data-L8"; base "$G"; mk_session "$G/runs" s2 9 1 9; mk_end "$G/runs" s2 0 done 9.5; mk_check "$G/ccheck-s2.json"
grep -v '"kind": "session_start", "name": "s2"' "$G/runs/queue.jsonl" > "$G/q.tmp"; mv "$G/q.tmp" "$G/runs/queue.jsonl"; rm -rf "$G/runs/s2"
both L8 "$G/runs" "$G" "$since"
ok "$([ "$r2" = 0 ] && [ "$r3" = 14 ] && grep -q 'V3-ADDED s2: named only by the queue.s session_end' "$T/gate-v3-L8.txt" && grep -q 'MISSING-CLOG s2' "$T/gate-v3-L8.txt" && echo 1 || echo 0)" \
   "L8 the verifier's D3: s2 named only by its session_end (9.5 card-minutes), its start line and directory lost: v2's gate $r2 (the gap), v3's $r3 (V3-ADDED, MISSING-CLOG)"
G="$T/data-L9"; base "$G"; mk_session "$G/runs" s2 9 0 0; mk_end "$G/runs" s2 0 done 9.5; rm -f "$G/runs/s2/launches.jsonl.gz"
both L9 "$G/runs" "$G" "$since"
ok "$([ "$r2" = 14 ] && [ "$r3" = 14 ] && grep -q 'V2-ADDED s2: (b)' "$T/gate-v3-L9.txt" && echo 1 || echo 0)" \
   "L9 the verifier's D4 (control): s2's directory there, its launches lost, 9.5 card-minutes: v3 14 by v2's rule (b), as v2 ($r2)"
G="$T/data-L10"; base "$G"; grep -v '"kind": "session_start", "name": "stoptest-die"' "$G/runs/queue.jsonl" > "$G/q.tmp"; mv "$G/q.tmp" "$G/runs/queue.jsonl"
rm -rf "$G/runs/stoptest-die"
both L10 "$G/runs" "$G" "$since"
ok "$([ "$r2" = 0 ] && [ "$r3" = 0 ] && ! grep -q 'REQUIRED stoptest-die' "$T/gate-v3-L10.txt" && echo 1 || echo 0)" \
   "L10 stoptest-die named only by its session_end, its directory lost: not required (v1's rule for stoptest-die): v3 $r3, v2 $r2"
ok "$([ "$SUB" = "$SUBN" ] && echo 1 || echo 0)" "L11 on every case, v3's REQUIRED list less its V3-ADDED sessions is v2's ($SUB of $SUBN)"
ok "$([ "$(calls)" = 0 ] && echo 1 || echo 0)" "   no ssh or rsync call in the whole test ($(calls))"
echo "selftest_steps_q142kg_v3: $((N - F)) of $N checks pass"
[ "$F" -eq 0 ]
