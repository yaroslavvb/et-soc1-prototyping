#!/usr/bin/env bash
# DV2's V3_DRY=1 tests (DESIGN §9 T4/T5; PREREG-DEV §4 row 3): every branch and failure path against the simulator of
# the 0.20.0 governor. No device is touched: every scenario runs with V3_DRY=1 and lib.sh's dry stubs. Each scenario
# starts from an empty dry tree (build/claims-v3-dry) and its data are kept in build/dv2-dry-tests/<scenario>/.
#   bash tools/claims-v3/dv2/selftest/dry_all.sh [scenario ...]      (default: all)
# Exit 0 if every check passed; the summary is build/dv2-dry-tests/summary.txt.
set -u
ROOT=$(cd "$(dirname "${BASH_SOURCE[0]}")/../../../.." && pwd)
cd "$ROOT"
export V3_DRY=1 DV2_ANY_TIME=1
B=tools/claims-v3/dv2/block.sh
DRY=build/claims-v3-dry
DV=$DRY/aifoundry2/dv2
KEEP=build/dv2-dry-tests
mkdir -p "$KEEP"
SUM=$KEEP/summary.txt; : > "$SUM"
FAILS=0
check() {  # check <scenario> <description> <command...>: the command must succeed
  local sc=$1 what=$2; shift 2
  if "$@" > /dev/null 2>&1; then echo "PASS  $sc: $what" | tee -a "$SUM"; else echo "FAIL  $sc: $what" | tee -a "$SUM"; FAILS=$((FAILS + 1)); fi
}
fresh() { rm -rf "$DRY"; mkdir -p "$DV"; }
keep() { rm -rf "$KEEP/$1"; cp -r "$DRY" "$KEEP/$1"; }
jq_() { python3 -c "import json,sys; d=json.load(open(sys.argv[1])); print(eval(sys.argv[2], {}, {'d': d}))" "$@"; }
runs_where() { python3 -c "
import json, sys
rs = [json.loads(l) for l in open(sys.argv[1])]
print(sum(1 for r in rs if eval(sys.argv[2], {}, {'r': r})))" "$@"; }

nat_scenario() {   # nat_scenario <rest> <expected branch>
  local rest=$1 br=$2 sc="nat-rest$1"
  fresh; export HP_DRY_REST=$rest
  bash "$B" 1001 > "$KEEP/$sc.log" 2>&1
  check "$sc" "Z1 reads COOL at rest $rest" grep -q '"cool": true' "$DV/p1001/z1.json"
  bash "$B" 6001 >> "$KEEP/$sc.log" 2>&1
  check "$sc" "a NAT candidate does nothing while NAT-AUTOSTART is off" test ! -e "$DV/p6001"
  touch "$DV/NAT-AUTOSTART"
  timeout 3000 bash "$B" 6002 >> "$KEEP/$sc.log" 2>&1; local rc=$?
  check "$sc" "the NAT session exits 0 (rc $rc)" test "$rc" = 0
  check "$sc" "branch $br" grep -q "\"branch\": \"$br\"" "$DV/p6002/session.json"
  check "$sc" "probe ALIVE, the smoke passed" grep -q '"ev":"smoke","reset":"ok"' "$DV/p6002/marks.jsonl"
  check "$sc" "WARNING set after ALIVE and INFO restored (checked)" grep -q '"ev":"level_check","want":"INFO","got":"INFO","ok":true' "$DV/p6002/marks.jsonl"
  check "$sc" "no run is void on the reset rule (every T/ADD run: exactly one reset before t0)" test "$(runs_where "$DV/p6002/runs.jsonl" "r.get('kind') in ('T','ADD') and r.get('rc') == 0 and not r.get('reset_check','').startswith('ONE')")" = 0
  check "$sc" "every post-run clock check passed" test "$(runs_where "$DV/p6002/runs.jsonl" "r.get('post_rc') not in (0, None)")" = 0
  check "$sc" "ADD first and last" python3 -c "
import json; rs=[json.loads(l) for l in open('$DV/p6002/runs.jsonl') if json.loads(l).get('kind') != 'SMOKE']
assert rs[0]['kind'] == 'ADD' and rs[-1]['kind'] == 'ADD', [r['kind'] for r in rs]"
  check "$sc" "the global-state table: threshold 65 at the start and the end" test "$(grep -c '"threshold_c": 65' "$DV/p6002/global-state.jsonl")" -ge 2
  check "$sc" "a second NAT candidate does nothing (one session a night)" bash -c "bash $B 6003 >/dev/null 2>&1; test ! -e $DV/p6003"
  keep "$sc"
}

want() { [ $# = 0 ] || [[ " $* " == *" $1 "* ]]; }
SEL=("$@")
sel() { [ ${#SEL[@]} = 0 ] && return 0; local x; for x in "${SEL[@]}"; do [ "$x" = "$1" ] && return 0; done; return 1; }

# ---- 1. LOOP at 66 and 70: Z1, the smoke, C1m (12 runs), no NAT
for rest in 66 70; do
  sc="loop-rest$rest"; sel "$sc" || continue
  fresh; export HP_DRY_REST=$rest
  bash "$B" 1001 > "$KEEP/$sc.log" 2>&1
  check "$sc" "Z1 reading $rest, not COOL" grep -q '"cool": false' "$DV/p1001/z1.json"
  bash "$B" 5001 >> "$KEEP/$sc.log" 2>&1
  check "$sc" "C1m refuses before a passed smoke" grep -q 'no smoke' "$DV/p5001/block.json"
  rm -rf "$DV/p5001"
  bash "$B" 4001 >> "$KEEP/$sc.log" 2>&1
  check "$sc" "the smoke passes (one reset, 600 MHz)" grep -q '"status":"ok"' "$DV/p4001/block.json"
  touch "$DV/NAT-AUTOSTART"
  bash "$B" 6001 >> "$KEEP/$sc.log" 2>&1
  check "$sc" "no NAT session at a warm Z1" test ! -e "$DV/p6001"
  timeout 3000 bash "$B" 5001 >> "$KEEP/$sc.log" 2>&1
  check "$sc" "C1m ran 12 runs" test "$(grep -c '"kind": "C1M"' "$DV/p5001/runs.jsonl")" = 12
  check "$sc" "C1m: every run at 600 MHz (no off-600 sample)" test "$(runs_where "$DV/p5001/runs.jsonl" "(r.get('obs') or {}).get('off600', 0) > 0")" = 0
  check "$sc" "C1m: every run one reset before t0" test "$(runs_where "$DV/p5001/runs.jsonl" "not r.get('reset_check','').startswith('ONE')")" = 0
  check "$sc" "C1m rows in DESIGN 5.4 order" python3 -c "
import json; n=[json.loads(l)['name'] for l in open('$DV/p5001/runs.jsonl')]
assert n == ['INT16@32','PER16@32','UNI32@16','UNI32@16','PER16@32','INT16@32','PER16@32','INT16@32','UNI32@16','UNI32@16','INT16@32','PER16@32'], n"
  bash "$B" 5002 >> "$KEEP/$sc.log" 2>&1
  check "$sc" "a second C1m does nothing" grep -q 'already ran' "$DV/p5002/block.json"
  keep "$sc"
done

# ---- 2. NAT branches at 60, 61, 62, 64
sel nat-rest60 && nat_scenario 60 NAT-4
sel nat-rest61 && nat_scenario 61 NAT-3
sel nat-rest62 && nat_scenario 62 NAT-2
sel nat-rest64 && nat_scenario 64 NAT-1

# ---- 3. the latch: the loop's first reduce from 800 fails; the clock stays at 800 -> ABORT-LATCH, the night stops
if sel latch; then
  sc=latch; fresh; export HP_DRY_REST=60 DV2_DRY_LATCH=1
  bash "$B" 1001 > "$KEEP/$sc.log" 2>&1; touch "$DV/NAT-AUTOSTART"
  timeout 3000 bash "$B" 6001 >> "$KEEP/$sc.log" 2>&1; rc=$?
  check "$sc" "the session exits 1 (rc $rc)" test "$rc" = 1
  check "$sc" "ALERT-LATCH or ALERT-FAILLINE written" bash -c "ls $DV/ALERT-LATCH.json $DV/ALERT-FAILLINE.json 2>/dev/null | grep -q ."
  check "$sc" "NIGHT-STOP written and the queue stop touched" bash -c "test -e $DV/NIGHT-STOP && test -e $DRY/STOP"
  check "$sc" "the level restored after the abort" grep -q '"ev":"level_check","want":"INFO","got":"INFO"' "$DV/p6001/marks.jsonl"
  bash "$B" 1002 >> "$KEEP/$sc.log" 2>&1
  check "$sc" "a pass after the night stop does nothing" test ! -e "$DV/p1002"
  unset DV2_DRY_LATCH
  keep "$sc"
fi

# ---- 3b. a latch whose error line never reaches the dump: the post-run clock check alone must catch it
if sel latch-silent; then
  sc=latch-silent; fresh; export HP_DRY_REST=60 DV2_DRY_LATCH_SILENT=1
  bash "$B" 1001 > "$KEEP/$sc.log" 2>&1; touch "$DV/NAT-AUTOSTART"
  timeout 3000 bash "$B" 6001 >> "$KEEP/$sc.log" 2>&1; rc=$?
  check "$sc" "the session exits 1 (rc $rc)" test "$rc" = 1
  check "$sc" "ALERT-LATCH written by the post-run clock check (no error line in any dump)" bash -c "test -e $DV/ALERT-LATCH.json && test ! -e $DV/ALERT-FAILLINE.json"
  check "$sc" "NIGHT-STOP written" test -e "$DV/NIGHT-STOP"
  unset DV2_DRY_LATCH_SILENT
  keep "$sc"
fi

# ---- 4. a foreign user appears during the session -> exit 3, the card left at once; the next session restores the level
if sel intrude; then
  sc=intrude; fresh; export HP_DRY_REST=60
  bash "$B" 1001 > "$KEEP/$sc.log" 2>&1; touch "$DV/NAT-AUTOSTART"
  ( sleep 6; touch "$DRY/dv2-sim/intrude" ) &
  timeout 3000 bash "$B" 6001 >> "$KEEP/$sc.log" 2>&1; rc=$?
  wait
  check "$sc" "the session exits 3 (rc $rc)" test "$rc" = 3
  check "$sc" "no level restore on exit 3 (the card left at once)" bash -c "! grep -q level_restored $DV/p6001/marks.jsonl"
  rm -f "$DRY/dv2-sim/intrude"
  check "$sc" "the level is pending after the intrusion" python3 -c "import json; assert json.load(open('$DV/sp-level.json'))['pending']"
  bash "$B" 4001 >> "$KEEP/$sc.log" 2>&1
  check "$sc" "the next pass restores the pending level first (checked)" grep -q '"ev":"level_check","want":"INFO","got":"INFO","ok":true' "$DV/p4001/marks.jsonl"
  touch "$DRY/dv2-sim/intrude-etwho"
  bash "$B" 1002 >> "$KEEP/$sc.log" 2>&1
  check "$sc" "Z1 skips its cycle when et-who shows a foreign holder" grep -q 'skipped' "$DV/p1002/block.json"
  rm -f "$DRY/dv2-sim/intrude-etwho"
  touch "$DRY/dv2-sim/intrude-etwho"
  bash "$B" 4003 >> "$KEEP/$sc.log" 2>&1; rc=$?
  check "$sc" "a session does not start (exit 3, no directory) while et-who shows a foreign holder (rc $rc)" bash -c "test $rc = 3 && test ! -e $DV/p4003"
  rm -f "$DRY/dv2-sim/intrude-etwho"
  touch "$DRY/dv2-sim/intrude-framework"
  bash "$B" 1003 >> "$KEEP/$sc.log" 2>&1
  check "$sc" "Z1 skips its cycle while another framework block runs" grep -q 'skipped' "$DV/p1003/block.json"
  bash "$B" 4002 >> "$KEEP/$sc.log" 2>&1; rc=$?
  check "$sc" "a session refuses (exit 3) while another framework block runs (rc $rc)" test "$rc" = 3
  rm -f "$DRY/dv2-sim/intrude-framework"
  keep "$sc"
fi

# ---- 4b. Z1 restores a log level a killed session left pending (no further session that night)
if sel z1-level; then
  sc=z1-level; fresh; export HP_DRY_REST=60
  bash "$B" 1001 > "$KEEP/$sc.log" 2>&1; touch "$DV/NAT-AUTOSTART"
  ( sleep 6; touch "$DRY/dv2-sim/intrude" ) &
  timeout 3000 bash "$B" 6001 >> "$KEEP/$sc.log" 2>&1; wait
  rm -f "$DRY/dv2-sim/intrude"
  check "$sc" "the level is pending after the intrusion" python3 -c "import json; assert json.load(open('$DV/sp-level.json'))['pending']"
  bash "$B" 1002 >> "$KEEP/$sc.log" 2>&1
  check "$sc" "the next Z1 cycle restores it (checked)" grep -q '"ev":"level_check","want":"INFO","got":"INFO","ok":true' "$DV/p1002/marks.jsonl"
  check "$sc" "and the level is no longer pending" python3 -c "import json; assert not json.load(open('$DV/sp-level.json'))['pending']"
  keep "$sc"
fi

# ---- 4c. C1m on a card that leaves its loop (rest 66 with the simulated threshold at 67): C1m stops, no heat off 600
if sel c1m-exit; then
  sc=c1m-exit; fresh; export HP_DRY_REST=66
  bash "$B" 1001 > "$KEEP/$sc.log" 2>&1
  bash "$B" 4001 >> "$KEEP/$sc.log" 2>&1
  DV2_DRY_THR=69 timeout 3000 bash "$B" 5001 >> "$KEEP/$sc.log" 2>&1
  check "$sc" "C1m ended out of the loop, or never saw a clock off 600 MHz (the simulated governor's timing varies)" bash -c "grep -q 'c1m_out_of_loop\|c1m_offclock' $DV/p5001/marks.jsonl || ! grep -q '\"off600\": [1-9]' $DV/p5001/runs.jsonl"
  check "$sc" "a threshold other than 65 (the simulated SP holds 69) raises ALERT-THRESHOLD at the session's end" test -e "$DV/ALERT-THRESHOLD.json"
  check "$sc" "every C1m run with a sample off 600 MHz is void, and C1m ran no run after it" python3 -c "
import json; rs=[json.loads(l) for l in open('$DV/p5001/runs.jsonl')]
bad=[i for i, r in enumerate(rs) if (r.get('obs') or {}).get('off600', 0) > 0]
assert all((rs[i].get('obs') or {}).get('void') for i in bad), bad
assert not bad or bad[0] == len(rs) - 1, (bad, len(rs))"
  keep "$sc"
fi

# ---- 5. refusals and the threshold alert
if sel refusals; then
  sc=refusals; fresh; export HP_DRY_REST=66
  check "$sc" "D1 (7001) refused" bash -c "bash $B 7001; test \$? = 2"
  check "$sc" "an unknown pass refused" bash -c "bash $B 9001; test \$? = 2"
  check "$sc" "dry-only variables refused without V3_DRY (envcheck)" bash -c "env -u V3_DRY DV2_DRY_LATCH=1 python3 tools/claims-v3/dv2/dv2lib.py envcheck; test \$? = 1"
  check "$sc" "ettelem-dv2 refuses 'threshold set' before opening the node" bash -c "build/ettelem-dv2/ettelem threshold set 70; test \$? = 2"
  DV2_DRY_THR=70 bash "$B" 1001 > "$KEEP/$sc.log" 2>&1
  check "$sc" "Z1 at a threshold of 70 with no pending.json: ALERT-THRESHOLD and the night stop" bash -c "test -e $DV/ALERT-THRESHOLD.json && test -e $DV/NIGHT-STOP"
  keep "$sc"
fi

# ---- 6. the queue: queue.sh runs a short dry schedule end to end (Z1, the smoke, C1m skipped at a cool rest, NAT)
if sel queue; then
  sc=queue; fresh; export HP_DRY_REST=61
  S=$KEEP/schedule-dry.txt
  printf 'dv2 1001\ndv2 4001\ndv2 5001\ndv2 1002\ndv2 6001\ndv2 1003\ndv2 6002\nend\n' > "$S"
  touch "$DV/NAT-AUTOSTART"
  timeout 3000 bash tools/claims-v3/queue.sh "$S" > "$KEEP/$sc.log" 2>&1; rc=$?
  check "$sc" "queue.sh ends (rc $rc)" test "$rc" = 0
  check "$sc" "the smoke passed" grep -q '"status":"ok"' "$DV/p4001/block.json"
  check "$sc" "C1m skipped at a cool rest" grep -q 'not LOOP\|reading <= 64' "$DV/p5001/block.json"
  check "$sc" "one NAT session ran (NAT-3) and the second candidate did nothing" bash -c "grep -q NAT-3 $DV/p6001/session.json && test ! -e $DV/p6002"
  keep "$sc"
fi

echo "---- $(grep -c '^PASS' "$SUM") passed, $FAILS failed (summary: $SUM)"
[ "$FAILS" = 0 ]
