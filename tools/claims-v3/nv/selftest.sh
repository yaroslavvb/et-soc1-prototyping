#!/usr/bin/env bash
# NV self-test, no device access: every scenario runs nv/block.sh (or run-queue.sh) under V3_DRY=1 with the stubs of
# nv/stubs/ (faults injected through NV_STUB_FAIL), then checks the exit code, block.json, the ALERT/STOP files, the
# state file and the stub's record of the calls it received; then reduce.py --self-test and a short Monte Carlo of the
# decision rules. About 6.5 minutes (42 checks).
#   bash tools/claims-v3/nv/selftest.sh [scenario ...]
# Dry output only: build/claims-v3-dry/ (its own STOP and ALERT files; a dry run never stops a real queue).
set -u
export V3_DRY=1                                  # every child inherits it: nothing here may reach a card
cd "$(dirname "${BASH_SOURCE[0]}")/../../.."
B=tools/claims-v3/nv/block.sh
Q=tools/claims-v3/nv/run-queue.sh
DRY=build/claims-v3-dry
export NV_STUB_SCALE=${NV_STUB_SCALE:-0.1}
PASSED=0; FAILED=0; FAILS=
only=" $* "
A3=$DRY/aifoundry3; A2=$DRY/aifoundry2
reset() {
  rm -rf "$A3"/nv* "$A2"/nv* "$DRY"/STOP "$DRY"/ALERT-NV-*.json
  mkdir -p "$A2/nv"; echo "dry: released for the self-test" > "$A2/nv/CARD-RELEASED"
}
run() {  # run <name> <expected rc> <env assignments...> -- <block args...>
  local name=$1 want=$2; shift 2
  local envs=()
  while [ "$1" != -- ]; do envs+=("$1"); shift; done; shift
  RUN_LOG=$DRY/selftest-$name.log
  env "${envs[@]}" bash "$B" "$@" > "$RUN_LOG" 2>&1
  RC=$?
  [ "$RC" = "$want" ] || { note "$name: exit $RC, expected $want"; return 1; }
  return 0
}
note() { echo "    $*"; BAD=1; }
check() {  # check <description> <command...>
  local d=$1; shift
  "$@" > /dev/null 2>&1 || note "failed: $d"
}
bj() { python3 -c "import json,sys; b=json.load(open(sys.argv[1])); print(b.get(sys.argv[2]))" "$1" "$2" 2>/dev/null; }
scenario() {  # scenario <name> <body function>
  case "$only" in "  ") ;; *" $1 "*) ;; *) return ;; esac
  reset; BAD=
  "$2"
  if [ -z "$BAD" ]; then echo "[ok]   $1"; PASSED=$((PASSED + 1)); else echo "[FAIL] $1 (log: $RUN_LOG)"; FAILED=$((FAILED + 1)); FAILS="$FAILS $1"; fi
}
sets() { grep -o 'NOC,[0-9]*' "$1/nv-stub-state/calls.log" 2>/dev/null | tr '\n' ' '; }
no_set() { ! grep -q SET_MODULE_VOLTAGE "$1/nv-stub-state/calls.log" 2>/dev/null; }
fresh_counts() { rm -f "$1"/nv-stub-state/sampler_starts "$1"/nv-stub-state/fills "$1"/nv-stub-state/bursts; }  # faults count per run
wait_for() {  # wait_for <file> <pattern> <tenths>
  local i; for i in $(seq 1 "$3"); do grep -q "$2" "$1" 2>/dev/null && return 0; sleep 0.1; done; return 1
}
scratch_tree() {  # a copy of the files NV needs, for tests that must not touch the real tree's hash files
  local T; T=$(mktemp -d)
  mkdir -p $T/tools/claims-v3/nv $T/tools/claims-v3/wire $T/workloads/enercat
  cp -r tools/claims-v3/nv/*.sh tools/claims-v3/nv/*.py tools/claims-v3/nv/*.json tools/claims-v3/nv/*.txt tools/claims-v3/nv/*.md \
    tools/claims-v3/nv/stubs $T/tools/claims-v3/nv/
  rm -f $T/tools/claims-v3/nv/*.sha256
  cp tools/claims-v3/lib.sh tools/claims-v3/queue.sh $T/tools/claims-v3/; cp tools/claims-v3/wire/configs.json $T/tools/claims-v3/wire/
  cp workloads/enercat/analyze_wire.py workloads/enercat/run_wire.py $T/workloads/enercat/
  echo "$T"
}

# ---- the normal paths
t_probe() { run probe 0 -- 1 --probe
  check "probe restored" [ "$(bj $A3/nv-probe/p1/block.json restored)" = True ]
  check "sets 540, 600, 485 in order" [ "$(sets $A3)" = "NOC,540 NOC,600 NOC,485 " ]
  check "state clean" grep -q '"clean"' $A3/nv/NV-STATE.json
  check "BL2 recorded" [ "$(bj $A3/nv-probe/p1/block.json bl2)" = 0.20.0 ]
  check "VMIN table unchanged" [ "$(bj $A3/nv-probe/p1/block.json vmin_same)" = True ]
  check "the restore read twice and the on-die monitor" grep -q '"what": "verify_base", "r1": 485, "r2": 485' $A3/nv-probe/p1/steps.jsonl; }
t_smoke() { run smoke 0 -- 1 --smoke
  check "smoke ok" [ "$(bj $A3/nv-smoke/p1/block.json status)" = ok ]
  check "7 windows kept" [ "$(wc -l < $A3/nv-smoke/p1/windows.jsonl)" = 7 ]
  check "32 launches" [ "$(wc -l < $A3/nv-smoke/p1/runs.jsonl)" = 32 ]
  check "the PCIe target was checked" grep -q 'PCIe targets seen: /dev/et0_ops' $A3/nv-smoke/p1/run.log
  check "every device call capped at 10 s with a kill" bash -c "! grep -E '^DRY (dms|window|fill|burst|heater)' $RUN_LOG | grep -v 'timeout -k 3 10'"
  check "no heater on the pinned card" [ ! -e $A3/nv-stub-state/heater.log ]; }
t_full() { run full 0 -- 1
  check "pass ok" [ "$(bj $A3/nv/p1/block.json status)" = ok ]
  check "28 windows" [ "$(wc -l < $A3/nv/p1/windows.jsonl)" = 28 ]
  check "levels 485 540 600 (pass 1's order)" [ "$(bj $A3/nv/p1/block.json levels)" = "485 540 600" ]
  check "192 launches" [ "$(wc -l < $A3/nv/p1/runs.jsonl)" = 192 ]
  check "restored" [ "$(bj $A3/nv/p1/block.json restored)" = True ]; }
# ---- the firmware and the host
t_bl2() { run bl2-old 2 NV_STUB_BL2=0.18.0 -- 1 --probe
  check "no set was issued" no_set $A3
  check "NV STOP set" [ -e $A3/nv/STOP ]
  check "said why" grep -q 'below 0.19.0' $A3/nv-probe/p1/block.json; }
t_flash() { run flash-written 1 NV_STUB_FAIL=flash -- 1 --probe
  check "ALERT-NV-FLASH" [ -e $DRY/ALERT-NV-FLASH.json ]
  check "dry STOP set" [ -e $DRY/STOP ]
  check "stopped after the first set: 540, then the restore" [ "$(sets $A3)" = "NOC,540 NOC,485 " ]
  check "restored" [ "$(bj $A3/nv-probe/p1/block.json restored)" = True ]
  check "vmin_same false" [ "$(bj $A3/nv-probe/p1/block.json vmin_same)" = False ]; }
t_multicard() { run multi-card 2 NV_DRY_MGMT_NODES=2 -- 1 --probe
  check "no block directory" [ ! -d $A3/nv-probe/p1 ]
  check "no device call" [ ! -s $A3/nv-stub-state/calls.log ]; }
t_otherq() {
  local f=$DRY/fake-ps.txt; mkdir -p $DRY
  printf '  101 bash tools/claims-v3/queue.sh tools/claims-v3/schedule-dv2val-aifoundry2.txt\n  102 bash tools/claims-v3/dv2/block.sh 6051\n' > $f
  run other-queue 3 NV_STUB_PS_FILE=$f -- 1 --probe
  check "no block directory" [ ! -d $A3/nv-probe/p1 ]
  printf '  201 bash tools/claims-v3/nv/run-queue.sh tools/claims-v3/nv/schedule-dev-aifoundry3.txt\n  202 bash tools/claims-v3/nv/block.sh 2\n' > $f
  run other-queue-nv-only 0 NV_STUB_PS_FILE=$f -- 1 --probe; }
t_pred() {   # a real block refuses until PREDICTIONS.sha256 checks (run in a scratch copy of the tree)
  local T; T=$(scratch_tree)
  RUN_LOG=$DRY/selftest-predictions.log
  check "refused without PREDICTIONS.sha256" bash -c "NV_DRY_CHECK_PREDICTIONS=1 bash $T/tools/claims-v3/nv/block.sh 1 --probe > $RUN_LOG 2>&1; [ \$? = 2 ]"
  check "no set" bash -c "! grep -q SET_MODULE $T/build/claims-v3-dry/aifoundry3/nv-stub-state/calls.log 2>/dev/null"
  check "freeze.sh --predictions writes it" bash $T/tools/claims-v3/nv/freeze.sh --predictions
  check "runs once it checks" bash -c "NV_DRY_CHECK_PREDICTIONS=1 bash $T/tools/claims-v3/nv/block.sh 1 --probe >> $RUN_LOG 2>&1"
  check "a second --predictions leaves it" bash $T/tools/claims-v3/nv/freeze.sh --predictions
  sed -i 's/"c_bw_tol_frac": 0.005/"c_bw_tol_frac": 0.02/' $T/tools/claims-v3/nv/predictions.json
  check "an edited predictions.json is refused" bash -c "NV_DRY_CHECK_PREDICTIONS=1 bash $T/tools/claims-v3/nv/block.sh 2 --probe >> $RUN_LOG 2>&1; [ \$? = 2 ]"
  check "and freeze.sh --predictions will not re-fix it" bash -c "! bash $T/tools/claims-v3/nv/freeze.sh --predictions"
  rm -rf "$T"; }
# ---- faults in a set
t_set_fails() { run set-fails 1 NV_STUB_FAIL=set:600 -- 1 --smoke
  check "ALERT-NV-SET" [ -e $DRY/ALERT-NV-SET.json ]
  check "dry STOP set" [ -e $DRY/STOP ]
  check "restored and verified" [ "$(bj $A3/nv-smoke/p1/block.json restored)" = True ]
  check "the stub's rail is back at 485" [ "$(cat $A3/nv-stub-state/level)" = 485 ]
  check "no reset alert" [ ! -e $DRY/ALERT-NV-RESET.json ]; }
t_readback() { run readback 1 NV_STUB_FAIL=readback:600 -- 1 --smoke
  check "ALERT-NV-SET" [ -e $DRY/ALERT-NV-SET.json ]
  check "restored" [ "$(bj $A3/nv-smoke/p1/block.json restored)" = True ]
  check "rail 485" [ "$(cat $A3/nv-stub-state/level)" = 485 ]; }
t_hang() { run hang 1 NV_STUB_FAIL=hang:600 -- 1 --smoke
  check "ALERT-NV-SET" [ -e $DRY/ALERT-NV-SET.json ]
  check "ALERT-NV-RESET (the uptime went back)" [ -e $DRY/ALERT-NV-RESET.json ]
  check "the reset alert names the clock guard" grep -q 'clock guard' $DRY/ALERT-NV-RESET.json
  check "set timed out (rc 124)" grep -q '"tag": "set600".*"rc": 124' $A3/nv-smoke/p1/dms.jsonl
  check "restore verified after the reset" grep -q restore_verified $A3/nv-smoke/p1/steps.jsonl
  check "a drain before the verification" grep -q '"tag": "drain"' $A3/nv-smoke/p1/dms.jsonl
  check "restored" [ "$(bj $A3/nv-smoke/p1/block.json restored)" = True ]; }
t_restore_fails() { run restore-fails 1 NV_STUB_FAIL=restore -- 1 --smoke
  check "ALERT-NV-RESTORE" [ -e $DRY/ALERT-NV-RESTORE.json ]
  check "dry STOP set" [ -e $DRY/STOP ]
  check "block.json says not restored" [ "$(bj $A3/nv-smoke/p1/block.json restored)" = False ]
  check "state file dirty" grep -q '"dirty"' $A3/nv/NV-STATE.json
  check "the next block refuses" run restore-fails-next 1 -- 2 --smoke; }
t_stale() { run stale-read 0 NV_STUB_FAIL=stale485 -- 1 --smoke
  check "the stale 485 was not taken as the restore" grep -q restore_unverified $A3/nv-smoke/p1/steps.jsonl
  check "set 485 twice" [ "$(sets $A3)" = "NOC,600 NOC,485 NOC,485 " ]
  check "rail 485" [ "$(cat $A3/nv-stub-state/level)" = 485 ]
  check "restored, state clean" grep -q '"clean"' $A3/nv/NV-STATE.json; }
# ---- faults in a window
t_hot() { run hot-window 1 NV_STUB_FAIL=tel_hot:2 -- 1 --smoke
  check "no NV STOP after one hot mean" [ ! -e $A3/nv/STOP ]
  check "no ALERT" bash -c "! ls $DRY/ALERT-NV-*.json"
  check "restored" [ "$(bj $A3/nv-smoke/p1/block.json restored)" = True ]
  fresh_counts $A3; run hot-window-again 1 NV_STUB_FAIL=tel_hot:2 -- 2 --smoke
  check "NV STOP after the second" [ -e $A3/nv/STOP ]
  check "the next block does not start" run hot-next 0 -- 3 --smoke
  check "... and made no directory" [ ! -d $A3/nv-smoke/p3 ]; }
t_hotwm() {  # a latched 93 C watermark from before the block does not stop it; a watermark rising to 95 C does
  run standing-watermark 0 NV_STUB_HI_WM=93 -- 1 --smoke
  check "ran" [ "$(bj $A3/nv-smoke/p1/block.json status)" = ok ]
  fresh_counts $A3; run rising-watermark 1 NV_STUB_HI_WM=80 NV_STUB_FAIL=tel_hiwm:3 -- 2 --smoke
  check "NV STOP set at once" [ -e $A3/nv/STOP ]
  check "said why" grep -q hot_sensor $A3/nv-smoke/p2/block.json
  check "restored" [ "$(bj $A3/nv-smoke/p2/block.json restored)" = True ]; }
t_regdrift() { run reg-drift 1 NV_STUB_FAIL=tel_reg:5 -- 1 --smoke
  check "ALERT-NV-STATE" [ -e $DRY/ALERT-NV-STATE.json ]
  check "restored" [ "$(bj $A3/nv-smoke/p1/block.json restored)" = True ]; }
t_current() { run current 1 NV_STUB_FAIL=tel_amps:5 -- 1 --smoke
  check "no ALERT, no host STOP" bash -c "! ls $DRY/ALERT-NV-*.json && [ ! -e $DRY/STOP ]"
  check "restored" [ "$(bj $A3/nv-smoke/p1/block.json restored)" = True ]
  check "one current abort recorded" [ "$(wc -l < $A3/nv/current-aborts.jsonl)" = 1 ]
  check "no NV STOP after one" [ ! -e $A3/nv/STOP ]
  fresh_counts $A3; run current-again 1 NV_STUB_FAIL=tel_amps:5 -- 2 --smoke
  check "NV STOP after the second" [ -e $A3/nv/STOP ]; }
t_bursthang() { run burst-timeout 1 NV_STUB_FAIL=burst_hang:3 -- 1 --smoke     # the first burst at 600 mV
  check "no ALERT" bash -c "! ls $DRY/ALERT-NV-*.json"
  check "an idle window before the restore's set" grep -q '"what": "idle_wait"' $A3/nv-smoke/p1/steps.jsonl
  check "restored" [ "$(bj $A3/nv-smoke/p1/block.json restored)" = True ]
  check "said why" grep -q 'overran' $A3/nv-smoke/p1/block.json; }
t_pcie() { run pcie-wrong-node 1 NV_STUB_PCIE_NODE=/dev/et1_ops -- 1 --smoke
  check "NV STOP set" [ -e $A3/nv/STOP ]
  check "restored" [ "$(bj $A3/nv-smoke/p1/block.json restored)" = True ]; }
t_nostart() { run sampler-retry 0 NV_STUB_FAIL=tel_nostart:2 -- 1 --smoke
  check "the retry is logged" grep -q 'sampler start 1 gave no line' $A3/nv-smoke/p1/run.log; }
t_fill() { run fill-retry 0 NV_STUB_FAIL=fill_fail:1 -- 1 --smoke
  check "the failed fill is marked" grep -q '"rc":139' $A3/nv-smoke/p1/marks.jsonl
  check "all 4 bursts ran" [ "$(wc -l < $A3/nv-smoke/p1/runs.jsonl)" = 32 ]; }
# ---- gates before any set
t_etwho() { run etwho-held 3 NV_STUB_ETWHO_RC=1 -- 1 --smoke
  check "no block directory" [ ! -d $A3/nv-smoke/p1 ]; }
t_fw() { run wrong-card 1 NV_STUB_FAIL=fw -- 1 --smoke
  check "identity failure recorded" grep -q identity $A3/nv-smoke/p1/block.json
  check "no set was issued" no_set $A3; }
t_hotstart() { run hot-start 3 NV_STUB_FAIL=hot -- 1 --smoke
  check "no set was issued" no_set $A3; }
t_stopfile() { mkdir -p $DRY; touch $DRY/STOP; run stop-file 0 -- 1 --smoke
  check "no block directory" [ ! -d $A3/nv-smoke/p1 ]; }
t_alertfile() { mkdir -p $DRY; echo '{}' > $DRY/ALERT-NV-RESTORE.json; run alert-file 1 -- 1 --smoke
  check "no block directory" [ ! -d $A3/nv-smoke/p1 ]; }
t_dirty() { mkdir -p $A3/nv; echo '{"state": "dirty", "mv": 600}' > $A3/nv/NV-STATE.json; run dirty-state 1 -- 1 --smoke
  check "ALERT-NV-STATE" [ -e $DRY/ALERT-NV-STATE.json ]
  check "no set was issued" no_set $A3; }
# ---- signals and kills
t_sigterm() {
  RUN_LOG=$DRY/selftest-sigterm.log
  bash "$B" 3 > "$RUN_LOG" 2>&1 &
  local p=$!
  wait_for "$A3/nv-stub-state/calls.log" 'NOC,540' 200
  sleep 1.5; kill -TERM "$p"; wait "$p"; RC=$?
  check "exit 1" [ "$RC" = 1 ]
  check "interrupted" grep -q 'interrupted by SIGTERM' $A3/nv/p3/block.json
  check "restored" [ "$(bj $A3/nv/p3/block.json restored)" = True ]
  check "rail 485" [ "$(cat $A3/nv-stub-state/level)" = 485 ]
  check "state clean" grep -q '"clean"' $A3/nv/NV-STATE.json; }
t_hup3() {   # an ssh drop: HUP three times, the later ones while the restore runs
  RUN_LOG=$DRY/selftest-hup.log
  bash "$B" 4 --smoke > "$RUN_LOG" 2>&1 &
  local p=$! i
  wait_for "$A3/nv-stub-state/calls.log" 'NOC,600' 300
  sleep 0.5
  for i in 1 2 3 4 5 6; do kill -HUP "$p" 2>/dev/null; sleep 0.25; done
  wait "$p"; RC=$?
  check "exit 1" [ "$RC" = 1 ]
  check "interrupted by SIGHUP" grep -q 'interrupted by SIGHUP' $A3/nv-smoke/p4/block.json
  check "restored" [ "$(bj $A3/nv-smoke/p4/block.json restored)" = True ]
  check "rail 485" [ "$(cat $A3/nv-stub-state/level)" = 485 ]
  check "state clean" grep -q '"clean"' $A3/nv/NV-STATE.json; }
t_kill9() {  # kill -9 mid-pass: the guardian restores and verifies, then writes block.json
  RUN_LOG=$DRY/selftest-kill9.log
  bash "$B" 5 > "$RUN_LOG" 2>&1 &
  local p=$!
  wait_for "$A3/nv-stub-state/calls.log" 'NOC,' 300     # pass 5: order 4, 600 mV first
  sleep 1.0; kill -KILL "$p"; wait "$p" 2>/dev/null
  check "the guardian wrote block.json" wait_for "$A3/nv/p5/block.json" guardian 400
  check "restored by the guardian" [ "$(bj $A3/nv/p5/block.json restored)" = True ]
  check "rail 485" [ "$(cat $A3/nv-stub-state/level)" = 485 ]
  check "state clean" grep -q '"clean"' $A3/nv/NV-STATE.json
  check "no ALERT" bash -c "! ls $DRY/ALERT-NV-*.json"; }
# ---- the validation card (aifoundry2)
t_released() { rm -f $A2/nv/CARD-RELEASED; run val-not-released 2 NV_DRY_CARD=aifoundry2 -- 101 --probe
  check "no block directory" [ ! -d $A2/nv-probe/p101 ]
  check "no device call" [ ! -s $A2/nv-stub-state/calls.log ]; }
t_valprobe() { run val-probe 0 NV_DRY_CARD=aifoundry2 -- 101 --probe
  check "every call uses -n 0" bash -c "! grep -v -- '-n 0' $A2/nv-stub-state/calls.log | grep -q ."
  check "no sampler on the validation card before the freeze" [ ! -e $A2/nv-stub-state/sampler_starts ]
  check "no heater in a probe" [ ! -e $A2/nv-stub-state/heater.log ]
  check "restored" [ "$(bj $A2/nv-probe/p101/block.json restored)" = True ]; }
t_valprobe_die() { run val-probe-die 1 NV_DRY_CARD=aifoundry2 NV_STUB_FAIL=asic:600 -- 101 --probe
  check "the windows' on-die rule stops it" grep -q "windows' rule" $A2/nv-probe/p101/block.json
  check "restored" [ "$(bj $A2/nv-probe/p101/block.json restored)" = True ]
  check "no sampler" [ ! -e $A2/nv-stub-state/sampler_starts ]; }
t_valfreeze() { run val-unfrozen 2 NV_DRY_CARD=aifoundry2 -- 101
  check "no block directory" [ ! -d $A2/nv/p101 ]; }
t_valfull() { run val-full 0 NV_DRY_CARD=aifoundry2 NV_DRY_SKIP_LOCK=1 -- 102
  check "pass 102 runs order 1 (600 540 485)" [ "$(bj $A2/nv/p102/block.json levels)" = "600 540 485" ]
  check "heated to 76 C first" grep -q '"die_c":7[6-9]\|"die_c":8' $A2/nv/p102/heat.jsonl
  check "heater launches marked" grep -q '"kind":"heater"' $A2/nv/p102/marks.jsonl
  check "restored" [ "$(bj $A2/nv/p102/block.json restored)" = True ]; }
t_spare() {   # N validation passes ended ok: the first spare does not run; one failed: the spare takes its order
  local p; for p in 101 102 103 104 105 106; do mkdir -p $A2/nv/p$p; echo '{"status":"ok"}' > $A2/nv/p$p/block.json; done
  run spare-not-needed 0 NV_DRY_CARD=aifoundry2 NV_DRY_SKIP_LOCK=1 -- 107
  check "no p107" [ ! -d $A2/nv/p107 ]
  check "said why" grep -q 'a spare, not needed' $RUN_LOG
  run beyond-plan 0 NV_DRY_CARD=aifoundry2 NV_DRY_SKIP_LOCK=1 -- 109
  check "109 is beyond the plan" grep -q 'beyond the plan' $RUN_LOG
  echo '{"status":"fail"}' > $A2/nv/p103/block.json
  local env
  env=$(python3 -B tools/claims-v3/nv/nvlib.py env --card aifoundry2 --pass 107 --data $A2)
  check "107 replaces 103" bash -c "echo \"$env\" | grep -qx 'NV_REPLACES=103'"
  check "107 takes 103's order (540 600 485)" bash -c "echo \"$env\" | grep -qx \"NV_LEVELS='540 600 485'\""
  mkdir -p $A2/nv/p107; echo '{"status":"ok"}' > $A2/nv/p107/block.json; echo '{"replaces": 103}' > $A2/nv/p107/order.json
  echo '{"status":"fail"}' > $A2/nv/p105/block.json
  env=$(python3 -B tools/claims-v3/nv/nvlib.py env --card aifoundry2 --pass 108 --data $A2)
  check "108 then replaces 105 (600 485 540)" bash -c "echo \"$env\" | grep -qx \"NV_LEVELS='600 485 540'\""; }
# ---- the tools around the block
t_queue() {   # NV's own queue: two probes, then "end"; then a busy card is retried and the queue stops on a refusal
  local s=$DRY/sched-test.txt; mkdir -p $DRY
  printf '# test\nnv 1 --probe\nnv 2 --probe\nend\nnv 3 --probe\n' > $s
  RUN_LOG=$DRY/selftest-queue.log
  check "the queue ran" bash -c "NV_RUNQ_GAP_S=0 bash $Q $s > $RUN_LOG 2>&1"
  check "p1 and p2 ran" bash -c "[ -e $A3/nv-probe/p1/block.json ] && [ -e $A3/nv-probe/p2/block.json ]"
  check "end stopped it" [ ! -d $A3/nv-probe/p3 ]
  printf 'nv 4 --probe\nnv 5 --probe\n' > $s
  check "a busy card is retried, then the queue stops" bash -c "NV_STUB_ETWHO_RC=1 NV_RUNQ_GAP_S=0 NV_RUNQ_RETRY_S=0 bash $Q $s >> $RUN_LOG 2>&1; [ \$(grep -c '\"pass\":4,.*\"rc\":3' $A3/nv/queue-state.jsonl) = 12 ] && [ ! -d $A3/nv-probe/p5 ]"
  printf 'nv 6 --probe\nnv 7 --probe\n' > $s
  check "a refusal stops the queue" bash -c "NV_DRY_MGMT_NODES=2 NV_RUNQ_GAP_S=0 bash $Q $s >> $RUN_LOG 2>&1; grep -q 'p6 was refused' $RUN_LOG && ! grep -q '\"pass\":7' $A3/nv/queue-state.jsonl"; }
t_freeze() {   # refuses the real skeleton; freezes and checks a complete copy in a scratch tree
  RUN_LOG=$DRY/selftest-freeze.log
  local bin T; bin=$(mktemp)
  printf '%064d  build/ettelem/ettelem\n%064d  build/enercat_v2/host/enercat_host\n%064d  /opt/et/bin/dev_mngt_service\n%064d  build/sparsity_t2/host/sparsity_host\n' 1 2 3 4 > "$bin"
  check "refuses the skeleton" bash -c "! bash tools/claims-v3/nv/freeze.sh --binaries $bin --out-dir $DRY/freeze-test > $RUN_LOG 2>&1"
  check "wrote nothing" [ ! -e $DRY/freeze-test/LOCK.sha256 ]
  T=$(scratch_tree)
  echo "# NV PREREG (test copy, complete)" > $T/tools/claims-v3/nv/PREREG.md
  echo '{"nD": 2.0, "sdD": 0.2, "nDev": 6, "tol": 0.35, "val_passes": 7}' > $T/tools/claims-v3/nv/prereg.json
  check "refuses before the predictions are fixed" bash -c "! bash $T/tools/claims-v3/nv/freeze.sh --binaries $bin >> $RUN_LOG 2>&1"
  bash $T/tools/claims-v3/nv/freeze.sh --predictions >> $RUN_LOG 2>&1
  check "refuses a pass count off the rule" bash -c "! bash $T/tools/claims-v3/nv/freeze.sh --binaries $bin >> $RUN_LOG 2>&1"
  echo '{"nD": 2.0, "sdD": 0.2, "nDev": 6, "tol": 0.35, "val_passes": 6}' > $T/tools/claims-v3/nv/prereg.json
  check "freezes a complete copy" bash $T/tools/claims-v3/nv/freeze.sh --binaries $bin
  check "LOCK lists 17 files" [ "$(wc -l < $T/tools/claims-v3/nv/LOCK.sha256)" = 17 ]
  check "PREREG.sha256 checks" bash -c "cd $T && sha256sum -c --quiet tools/claims-v3/nv/PREREG.sha256"
  check "the sources check before an edit" bash -c "cd $T && ! sha256sum -c --quiet tools/claims-v3/nv/LOCK.sha256 2>/dev/null | grep -v '^build/\|^/opt/' | grep -q ."
  check "an edit breaks the lock" bash -c "cd $T && echo ' ' >> tools/claims-v3/nv/nv.json && sha256sum -c --quiet tools/claims-v3/nv/LOCK.sha256 2>/dev/null | grep -q 'nv/nv.json: FAILED'"
  rm -rf "$T" "$bin"; }
t_refusals() {
  run refuse-dev-pass-on-val 2 NV_DRY_CARD=aifoundry2 -- 1 --probe
  run refuse-val-pass-on-dev 2 -- 101 --smoke
  run refuse-smoke-on-val 2 NV_DRY_CARD=aifoundry2 -- 101 --smoke
  run refuse-aifoundry1-c1 2 NV_DRY_CARD=aifoundry1-c1 -- 101 --probe
  run refuse-aifoundry1-c0 2 NV_DRY_CARD=aifoundry1-c0 -- 1 --probe
  run refuse-usage 2 -- 0; }
t_whitelist() {   # nv_set, lifted out of block.sh, with dms/state/log replaced by recorders
  local f out out18
  f=$(mktemp)
  { echo 'NV_ALLOWED="485 540 600"; NV_SET_ARG="NOC,{mv}"; NV_U_SET=7000; DIRTY=; CALLED=; NV_BL2=$1; NV_BL2_OK=1
dms() { CALLED="$CALLED $*"; return 0; }; state() { :; }; log() { :; }'
    sed -n '/^nv_set() {/,/^}/p' tools/claims-v3/nv/block.sh
    echo 'for mv in 605 1680 400 480 590 485 540 600; do nv_set $mv; echo "$mv:$?"; done; echo "CALLED:$CALLED"'; } > "$f"
  out=$(bash "$f" 0.20.0); out18=$(bash "$f" 0.18.0); rm -f "$f"
  RUN_LOG=/dev/null
  check "605 1680 400 480 590 refused (2); 485 540 600 made" bash -c "echo '$out' | tr '\n' ' ' | grep -q '605:2 1680:2 400:2 480:2 590:2 485:0 540:0 600:0'"
  check "only NOC,485/540/600 reached the tool" bash -c "echo '$out' | grep '^CALLED' | grep -o 'NOC,[0-9]*' | tr '\n' ' ' | grep -qx 'NOC,485 NOC,540 NOC,600 '"
  check "on BL2 0.18.0 every level is refused, hard-coded" bash -c "echo '$out18' | tr '\n' ' ' | grep -q '485:2 540:2 600:2 CALLED: *\$'"; }

scenario probe t_probe
scenario smoke t_smoke
scenario full t_full
scenario bl2-old t_bl2
scenario flash-written t_flash
scenario multi-card t_multicard
scenario other-queue t_otherq
scenario predictions t_pred
scenario set-fails t_set_fails
scenario readback t_readback
scenario hang t_hang
scenario restore-fails t_restore_fails
scenario stale-read t_stale
scenario hot-window t_hot
scenario hot-watermark t_hotwm
scenario reg-drift t_regdrift
scenario current t_current
scenario burst-timeout t_bursthang
scenario pcie-wrong-node t_pcie
scenario sampler-retry t_nostart
scenario fill-retry t_fill
scenario etwho-held t_etwho
scenario wrong-card t_fw
scenario hot-start t_hotstart
scenario stop-file t_stopfile
scenario alert-file t_alertfile
scenario dirty-state t_dirty
scenario sigterm t_sigterm
scenario hup3 t_hup3
scenario kill9 t_kill9
scenario val-not-released t_released
scenario val-probe t_valprobe
scenario val-probe-die t_valprobe_die
scenario val-unfrozen t_valfreeze
scenario val-full t_valfull
scenario spare t_spare
scenario queue t_queue
scenario freeze t_freeze
scenario refusals t_refusals
scenario whitelist t_whitelist
reset
case "$only" in "  "|*" reduce "*)
  if python3 -B tools/claims-v3/nv/reduce.py --self-test > "$DRY/selftest-reduce.log" 2>&1; then
    echo "[ok]   reduce.py --self-test"; PASSED=$((PASSED + 1))
  else echo "[FAIL] reduce.py --self-test ($DRY/selftest-reduce.log)"; FAILED=$((FAILED + 1)); FAILS="$FAILS reduce"; fi ;;
esac
case "$only" in "  "|*" mc "*)
  if python3 -B tools/claims-v3/nv/reduce.py --monte-carlo --reps 300 --check > "$DRY/selftest-mc.log" 2>&1; then
    echo "[ok]   reduce.py --monte-carlo (decision rules' error rates)"; PASSED=$((PASSED + 1))
  else echo "[FAIL] reduce.py --monte-carlo ($DRY/selftest-mc.log)"; FAILED=$((FAILED + 1)); FAILS="$FAILS mc"; fi ;;
esac
echo "NV selftest: $PASSED passed, $FAILED failed${FAILS:+:$FAILS}"
[ "$FAILED" = 0 ]
