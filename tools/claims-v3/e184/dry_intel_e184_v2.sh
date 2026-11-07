#!/usr/bin/env bash
# E184 (Q153), kit v2 (KIT.md.dated-note-1.md section 6): dry_intel_e184.sh (v1, which stays as committed) on kit v2's box files
# (check_e184_v2.py, preflight_e184_v2.sh, block_e184{s,b}_v2.sh, queue_e184_v2.sh, session_e184{s,b}_v2.sh, run_e184_v2.py, harness-e184-v2.json),
# with the sessions' files named by T0, and one new check, 3f: queue_e184_v2.sh goes on after a pass that ends partial (rc 7) and stops
# after one that ends rc 1. The rest is v1's:
# E184 (Q153, the kit): the V3_DRY dry pass on the Intel, both arms, in tools/claims-v3/e180/dry_intel_e180_v2.sh's form: it never opens a
# device and never reaches the network. A copy of the tree in the scratch directory; stub binaries for the E184 host and the telemetry
# reader that refuse if run; stand-in ssh, rsync and scp that log and refuse; hostname answers aifoundry3 for arm S and aifoundry1 for
# arm B. Checks:
#   1a the harness; 1b the device-command preflight of each arm (GO; arm S with no WRITE, arm B with the statistics reset alone);
#   1c the box build under V3_DRY (the patch applies to the committed workloads/enercat and gives the pinned file; nothing built);
#   1d the telemetry guards: arm S's block calls E128's, arm B's E184's, neither block nor the runner calls the reader directly, and E184's
#      guard passes config, sample and sample --reset-ms 1000 to the reader and refuses --reset-ms 500, loglevel and sptrace (exit 97);
#   2  every pass of both arms through its block (arm S: one planned host process a quad, the calibration's cal.json from E184_DRY_BASES,
#      parts P and C on its masks; arm B: one process a burst, four a hold, none at idle), no stub executed;
#   2b refusals before any device call: arm B's pass on aifoundry3, arm S's on card 1, card 0 for arm B, the smoke's number without --smoke;
#   3  the queue's budget and deadline rules on stub blocks; the sessions' start gates (no time gates, past the latest start, the other
#      arm's box, both ways); a whole dry session of each arm, which never writes the real session's log;
#   4  no network call.
#   bash tools/claims-v3/e184/dry_intel_e184_v2.sh <scratch dir> > <log>      (Intel only; GNU date as gdate on PATH)
# SPDX-License-Identifier: Apache-2.0
set -u
SRC=$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)
S=${1:?a scratch directory outside the repository}
case "$S" in "$SRC"|"$SRC"/*) echo "the scratch directory must be outside the repository"; exit 2 ;; esac
command -v gdate > /dev/null || { echo "no gdate (GNU date) on PATH"; exit 2; }
T=$S/tree
B=$S/bin
main() {
mkdir -p "$T/tools/claims-v3" "$T/workloads" "$B"
rsync -a --delete --exclude __pycache__ "$SRC/tools/claims-v3/" "$T/tools/claims-v3/"
rsync -a --delete --exclude __pycache__ "$SRC/workloads/enercat/" "$T/workloads/enercat/"
rsync -a --delete --exclude __pycache__ "$SRC/docs/reports/data/2026-09-29-tau-aifoundry1-c1/report.json" "$S/" 2>/dev/null
( cd "$SRC" && git ls-files workloads/enercat ) > "$S/enercat-files.txt"
rm -rf "${T:?}/build"
for f in build/enercat-e184/host/enercat_host build/ettelem/ettelem; do
  mkdir -p "$T/$(dirname "$f")"
  printf '#!/bin/sh\n# strings the preflight looks for: --schedule --stop-file\necho "STUB EXECUTED: %s $*" >&2\nexit 97\n' "$f" > "$T/$f"
  chmod +x "$T/$f"
done
mkdir -p "$T/build/enercat-e184/kernel"; echo "stub kernel (dry pass)" > "$T/build/enercat-e184/kernel/enercat.elf"
printf '#!/bin/sh\necho "${E184_DRY_HOSTNAME:-aifoundry3}"\n' > "$B/hostname"
printf '#!/bin/sh\nexec gdate "$@"\n' > "$B/date"
printf '#!/bin/sh\nexec /usr/bin/python3 "$@"\n' > "$B/python3"
printf '#!/bin/sh\necho "(dry pass on the Intel: no et-who here)"\n' > "$B/et-who"
printf '#!/bin/sh\nexit 1\n' > "$B/flock"
printf '#!/bin/sh\ncd "%s" && cat "%s"\n' "$SRC" "$S/enercat-files.txt" > "$B/git-ls-enercat"
for n in ssh rsync scp; do printf '#!/bin/sh\necho "%s $*" >> "%s"\necho "NETWORK STAND-IN: %s refused in a dry pass" >&2\nexit 97\n' "$n" "$S/network-calls.log" "$n" > "$B/$n"; done
: > "$S/network-calls.log"
chmod +x "$B"/*
export PATH="$B:$PATH" V3_DRY=1
cd "$T" || exit 2
fail=0
step() { echo; echo "== $*"; }
ok() { if [ "$1" -eq 0 ]; then echo "-> PASS"; else echo "-> FAIL (rc $1)"; fail=1; fi; }
step "1a. check_e184_v2.py harness (dry: the box's E184 build is not checked)"
python3 -B tools/claims-v3/e184/check_e184_v2.py harness; ok $?
for arm in S B; do
  step "1b. preflight_e184_v2.sh $arm (dmcmd_audit on arm $arm's kit-v2 file set)"
  bash tools/claims-v3/e184/preflight_e184_v2.sh $arm > "$S/preflight-$arm.txt" 2>&1; rc=$?
  grep -m1 '^dmcmd_audit:' "$S/preflight-$arm.txt"; ok $rc
done
step "1c. build_e184.sh (dry: the patch applies and gives the pinned file; nothing built)"
bash tools/claims-v3/e184/build_e184.sh 2>&1 | tail -3; rc=${PIPESTATUS[0]}
p=$(sha256sum build/enercat-e184-src/host/main.cpp | cut -d' ' -f1); echo "patched host/main.cpp $p"
[ "$rc" -eq 0 ] && [ "$p" = "$(python3 -c 'import json; print(json.load(open("tools/claims-v3/e184/harness-e184-v2.json"))["patched_main_sha256"])')" ]; ok $?
step "1d. the telemetry guards"
g1=$(grep -c '^ETTELEM=tools/claims-v3/e128/ettelem_guard.sh' tools/claims-v3/e184/block_e184s_v2.sh)
g2=$(grep -c '^ETTELEM=tools/claims-v3/e184/ettelem_guard_e184.sh' tools/claims-v3/e184/block_e184b_v2.sh)
x=$(cat tools/claims-v3/e184/block_e184s_v2.sh tools/claims-v3/e184/block_e184b_v2.sh tools/claims-v3/e184/run_e184_v2.py | grep -v -E '^[[:space:]]*#' | grep -c -E 'ettelem sample|ettelem config|build/ettelem/ettelem (sample|config)')
mv build/ettelem/ettelem build/ettelem/ettelem.stub
printf '#!/bin/sh\necho "READER $*"\n' > build/ettelem/ettelem; chmod +x build/ettelem/ettelem
G=tools/claims-v3/e184/ettelem_guard_e184.sh
r1=$(bash $G config); r2=$(bash $G sample --seconds 2 --every-ms 100); r3=$(bash $G sample --seconds 2 --every-ms 100 --reset-ms 1000)
bash $G sample --seconds 2 --every-ms 100 --reset-ms 500 2>/dev/null; q1=$?; bash $G loglevel warning 2>/dev/null; q2=$?; bash $G sptrace 2>/dev/null; q3=$?
mv build/ettelem/ettelem.stub build/ettelem/ettelem
echo "arm S's block sets E128's guard: $g1; arm B's sets E184's: $g2; direct reader calls: $x; E184's guard: '$r1' / '$r2' / '$r3'; refusals rc $q1 $q2 $q3"
[ "$g1" -eq 1 ] && [ "$g2" -eq 1 ] && [ "$x" -eq 0 ] && [ "$r1" = "READER config" ] && [ "$r3" = "READER sample --seconds 2 --every-ms 100 --reset-ms 1000" ] \
  && [ "$q1" -eq 97 ] && [ "$q2" -eq 97 ] && [ "$q3" -eq 97 ]; ok $?
npl() { python3 -c 'import json,sys; p=json.load(open("tools/claims-v3/e184/plan-e184.json")); q=[x for a in ("arm_S","arm_B") for x in p[a]["passes"] if x["pass"]==int(sys.argv[1])][0]
import math; print(sum(1 if i.get("kind","quad")=="burst" or "orient" in i else (0 if i["cfg"]=="idle" else int(math.ceil(i["hold_s"]/i["proc_s"]-1e-9))) for i in q["items"]))' "$1"; }
for spec in "S 18402 stoptest" "S 18401 smoke" "S 18410 pass" "S 18411 pass" "S 18412 pass" "S 18413 pass" "S 18414 pass" "S 18415 pass" "S 18416 pass" "S 18417 pass" "S 18418 pass" \
            "B 18432 stoptest" "B 18431 smoke" "B 18440 pass" "B 18441 pass" "B 18442 pass" "B 18443 pass" "B 18444 pass"; do
  set -- $spec
  arm=$1; p=$2; k=$3
  if [ "$arm" = S ]; then BLK=tools/claims-v3/e184/block_e184s_v2.sh; export E184_DRY_HOSTNAME=aifoundry3; unset V3_DEVICE; CARD=aifoundry3
  else BLK=tools/claims-v3/e184/block_e184b_v2.sh; export E184_DRY_HOSTNAME=aifoundry1 V3_DEVICE=1; CARD=aifoundry1-c1; fi
  n=0; [ "$k" != stoptest ] && n=$(npl "$p")
  step "2. arm $arm, block $p ($k): expect $n planned host processes, no stub executed"
  case "$k" in
    smoke) bash $BLK "$p" --smoke > "$S/dry-$p.log" 2>&1; rc=$? ;;
    stoptest) bash $BLK "$p" --stoptest > "$S/dry-$p.log" 2>&1; rc=$? ;;
    *) E184_DRY_BASES="16:30.40,24:33.10,32:35.60" bash $BLK "$p" > "$S/dry-$p.log" 2>&1; rc=$? ;;
  esac
  runs=$(grep -c 'DRY hold10: build/enercat-e184/host/enercat_host' "$S/dry-$p.log")
  stub=$(grep -c 'STUB EXECUTED' "$S/dry-$p.log")
  rst=$(grep -c 'DRY start_sampler.*--reset-ms 1000' "$S/dry-$p.log")
  want_rst=0; [ "$p" = 18441 ] && want_rst=1
  extra=0
  if [ "$p" = 18413 ]; then
    python3 -c 'import json; c=json.load(open("build/e184/cal.json")); print("cal.json: M_op %d, M_s %d (dry %s)" % (c["M_op"], c["M_s"], c["dry"]))' || extra=1
  fi
  if [ "$k" = stoptest ]; then
    [ -f "build/claims-v3-dry/$CARD/e184-stoptest/p$p/board/stoptest.json" ] && [ -f "build/claims-v3-dry/$CARD/e184-stoptest/p$p/die/stoptest.json" ] || extra=1
  fi
  echo "block rc=$rc; planned host processes: $runs; stubs executed: $stub; reset sampler starts: $rst"
  [ "$rc" -eq 0 ] && [ "$stub" -eq 0 ] && [ "$runs" -eq "$n" ] && [ "$rst" -eq "$want_rst" ] && [ "$extra" -eq 0 ]; ok $?
done
unset V3_DEVICE
for spec in "18442 S aifoundry3" "18410 B aifoundry1" "18440 B0 aifoundry1" "18401 S aifoundry3"; do
  set -- $spec
  step "2b. refused before any device call: pass $1 by $2's block on $3"
  case "$2" in
    S) E184_DRY_HOSTNAME=$3 bash tools/claims-v3/e184/block_e184s_v2.sh "$1" > "$S/dry-r$1$2.log" 2>&1; rc=$? ;;
    B) E184_DRY_HOSTNAME=$3 V3_DEVICE=1 bash tools/claims-v3/e184/block_e184b_v2.sh "$1" > "$S/dry-r$1$2.log" 2>&1; rc=$? ;;
    B0) E184_DRY_HOSTNAME=$3 V3_DEVICE=0 bash tools/claims-v3/e184/block_e184b_v2.sh "$1" > "$S/dry-r$1$2.log" 2>&1; rc=$? ;;
  esac
  tail -n 1 "$S/dry-r$1$2.log" | cut -c1-200
  calls=$(grep -c 'DRY hold10' "$S/dry-r$1$2.log")
  [ "$rc" -ne 0 ] && [ "$calls" -eq 0 ]; ok $?
done
step "3a. the queue's budget rule on stub blocks (3 s each, planned 1 s: after the first the ratio 3 projects 3 s, so an 8 s budget admits two and stops before the third)"
printf '#!/bin/sh\nsleep 3\nexit 0\n' > "$S/stub_block.sh"
E184_ARM=S E184_T0=$(date +%s) E184_DEADLINE="$(date -d '+1 hour' '+%F %T')" E184_BLOCK="$S/stub_block.sh" E184_SEQ="18410 18411 18412" \
  E184_BUDGET_S=8 E184_RESERVE_S=0 E184_GAP_S=0 E184_EST_S=1 E184_MARGIN_S=0 bash tools/claims-v3/e184/queue_e184_v2.sh > "$S/q-budget.log" 2>&1
cat "$S/q-budget.log"
grep -q 'budget: stopping before p18412' "$S/q-budget.log" && [ "$(grep -c 'starts at' "$S/q-budget.log")" -eq 2 ]; ok $?
step "3b. the queue's deadline rule (a deadline one minute ago: nothing starts)"
E184_ARM=B E184_T0=$(date +%s) E184_DEADLINE="$(date -d '-1 minute' '+%F %T')" E184_BLOCK="$S/stub_block.sh" bash tools/claims-v3/e184/queue_e184_v2.sh > "$S/q-deadline.log" 2>&1
cat "$S/q-deadline.log"
grep -q 'budget: stopping before p18440' "$S/q-deadline.log" && ! grep -q 'starts at' "$S/q-deadline.log"; ok $?
step "3c. the plans: arm S nine passes under 8,100 s, arm B five under 1,500 s (3 s stub blocks, planned 1 s)"
E184_ARM=S E184_T0=$(date +%s) E184_DEADLINE="$(date -d '+2 hour' '+%F %T')" E184_BLOCK="$S/stub_block.sh" E184_GAP_S=0 E184_EST_S=1 E184_MARGIN_S=0 \
  bash tools/claims-v3/e184/queue_e184_v2.sh > "$S/q-s.log" 2>&1
E184_ARM=B E184_T0=$(date +%s) E184_DEADLINE="$(date -d '+2 hour' '+%F %T')" E184_BLOCK="$S/stub_block.sh" E184_GAP_S=0 E184_EST_S=1 E184_MARGIN_S=0 \
  bash tools/claims-v3/e184/queue_e184_v2.sh > "$S/q-b.log" 2>&1
head -1 "$S/q-s.log"; tail -1 "$S/q-s.log"; head -1 "$S/q-b.log"; tail -1 "$S/q-b.log"
grep -q 'budget 8100 s' "$S/q-s.log" && grep -q 'done, 9 items' "$S/q-s.log" && grep -q 'budget 1500 s' "$S/q-b.log" && grep -q 'done, 5 items' "$S/q-b.log"; ok $?
for case_ in "S no time gates" "S after the latest start" "S on aifoundry1" "B on aifoundry3"; do
  set -- $case_
  step "3d. session_e184s.sh or session_e184b.sh start gate, arm $1: ${case_#* } (exit 8, no device opened)"
  mkdir -p build/e184; T0=$(date +%s)
  case "${case_#* }" in
    "no time gates") E184_DRY_HOSTNAME=aifoundry3 E184_T0=$T0 bash tools/claims-v3/e184/session_e184s_v2.sh > /dev/null 2>&1; rc=$? ;;
    "after the latest start") E184_DRY_HOSTNAME=aifoundry3 E184_T0=$T0 E184_LATEST_START="$(date -d '-1 minute' '+%F %T')" \
        E184_DEADLINE="$(date -d '+1 hour' '+%F %T')" bash tools/claims-v3/e184/session_e184s_v2.sh > /dev/null 2>&1; rc=$? ;;
    "on aifoundry1") E184_DRY_HOSTNAME=aifoundry1 E184_T0=$T0 E184_LATEST_START="$(date -d '+1 hour' '+%F %T')" \
        E184_DEADLINE="$(date -d '+2 hour' '+%F %T')" bash tools/claims-v3/e184/session_e184s_v2.sh > /dev/null 2>&1; rc=$? ;;
    "on aifoundry3") E184_DRY_HOSTNAME=aifoundry3 E184_T0=$T0 E184_LATEST_START="$(date -d '+1 hour' '+%F %T')" \
        E184_DEADLINE="$(date -d '+2 hour' '+%F %T')" bash tools/claims-v3/e184/session_e184b_v2.sh > /dev/null 2>&1; rc=$? ;;
  esac
  cut -d' ' -f4- "build/e184/session-$1-dry-t$T0.log" 2>/dev/null | tail -2
  [ "$rc" -eq 8 ] && [ -s "build/e184/session-$1-dry-t$T0.log" ] && ! grep -q 'harness check\|stop-path' "build/e184/session-$1-dry-t$T0.log" 2>/dev/null; ok $?
done
for arm in S B; do
  step "3e. a whole dry session, arm $arm: the stop-path test, the smoke and the queue's dry passes; the real session's log is never written"
  rm -f build/e184/cal.json; T0=$(date +%s)
  h=aifoundry3; [ "$arm" = B ] && h=aifoundry1
  sess=tools/claims-v3/e184/session_e184s_v2.sh; [ "$arm" = B ] && sess=tools/claims-v3/e184/session_e184b_v2.sh
  E184_DRY_HOSTNAME=$h E184_DRY_BASES="16:30.40,24:33.10,32:35.60" E184_T0=$T0 E184_LATEST_START="$(date -d '+1 hour' '+%F %T')" \
    E184_DEADLINE="$(date -d '+3 hour' '+%F %T')" E184_GAP_S=0 bash $sess > "$S/session-$arm.out" 2>&1; rc=$?
  cut -d' ' -f4- "build/e184/session-$arm-dry-t$T0.log" | grep -v '^\s*$' | head -12
  want=9; [ "$arm" = B ] && want=5
  tail -1 "build/e184/queue-$arm-dry-t$T0.out" 2>/dev/null
  [ "$rc" -eq 0 ] && grep -q 'stop-path test rc=0' "build/e184/session-$arm-dry-t$T0.log" && grep -q 'smoke rc=0' "build/e184/session-$arm-dry-t$T0.log" \
    && grep -q "session end (T0 $T0)" "build/e184/session-$arm-dry-t$T0.log" \
    && grep -q "done, $want items" "build/e184/queue-$arm-dry-t$T0.out" && ! ls build/e184/session-$arm-t[0-9]*.log > /dev/null 2>&1; ok $?
done
step "3f. the queue v2 goes on after a partial pass (rc 7) and stops after a failed one (rc 1)"
printf '#!/bin/sh\ncase "$1" in 18410) exit 7 ;; 18411) exit 0 ;; 18412) exit 1 ;; *) exit 0 ;; esac\n' > "$S/stub_block_rc.sh"
E184_ARM=S E184_T0=$(date +%s) E184_DEADLINE="$(date -d '+1 hour' '+%F %T')" E184_BLOCK="$S/stub_block_rc.sh" E184_SEQ="18410 18411 18412 18413" \
  E184_GAP_S=0 E184_EST_S=1 E184_MARGIN_S=0 bash tools/claims-v3/e184/queue_e184_v2.sh > "$S/q-partial.log" 2>&1
cat "$S/q-partial.log"
grep -q 'p18410 partial (rc 7)' "$S/q-partial.log" && grep -q 'p18411 starts at' "$S/q-partial.log" && grep -q 'stopping after p18412 (rc 1)' "$S/q-partial.log" \
  && ! grep -q 'p18413 starts at' "$S/q-partial.log"; ok $?
step "4. no network call: the ssh, rsync and scp stand-ins were never called"
n=$(grep -c . "$S/network-calls.log"); echo "network calls: $n"; [ "$n" -eq 0 ]; ok $?
echo
grep -h 'STUB EXECUTED' "$S"/dry-*.log "$S"/q-*.log "$S"/session-*.out 2>/dev/null | head -3
echo "DRY-INTEL-E184-V2 $([ "$fail" -eq 0 ] && echo PASS || echo FAIL): no device opened (V3_DRY=1 and stub binaries that refuse), no network call"
return "$fail"
}
main 2>&1 | sed "s#$T#<dry-tree>#g; s#$S#<scratch>#g; s#$SRC#<repo>#g"
exit "${PIPESTATUS[0]}"
