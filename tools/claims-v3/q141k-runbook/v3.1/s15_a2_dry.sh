#!/usr/bin/env bash
# Q141(k), go checklist step 15 (Q141(f)'s F5): aifoundry2's four dry passes, no device opened (the toy card), ALL before E165's session
# and never during one, at most two at a time. Each runs detached on the box as a dry job, then is waited on with bounded calls:
#   e165: queue_e165.py --dry with protocol-dry.json and the two dry stop-path protocols, --cap 30 (E165 README box step 6), its own
#         dry slot file; stopped after the smoke and the stop tests by the queue's own RUNS/QUEUE-STOP (touched once the queue is in
#         its slot: it then ends before the session), about 1 minute; `full` runs it to its end, about 13;
#   e167: bash tools/claims-v3/e167/run_e167.sh dry (README box step 3; about 7 minutes);
#   e168: queue_e168.py --dry into build/e168/dry/runs with its slot in build/e168/dry/slot.txt (README step 6; about 3 minutes);
#   e169: the dated note's box step 4, exactly: build/e169/dry with its own dry slot file, then score_e169.py on it, and
#         build/e169/runs must not exist (about 5 minutes).
# An earlier dry directory of the same pass is moved aside first (its records would be read as this pass's). Nothing is collected.
#
#   bash tools/claims-v3/q141k-runbook/s15_a2_dry.sh <e165|e167|e168|e169> start [full]
#   bash tools/claims-v3/q141k-runbook/s15_a2_dry.sh <e165|e167|e168|e169> wait          # 0 passed, 14 failed, 17 call again
# SPDX-License-Identifier: Apache-2.0
. "$(dirname "${BASH_SOURCE[0]}")/rb_common.sh"
rb_init s15_a2_dry
run=${1:-}; act=${2:-}; mode=${3:-short}
case "$run" in e165|e167|e168|e169) ;; *) rb_die $RB_E_USAGE "usage: s15_a2_dry.sh <e165|e167|e168|e169> start [full] | wait" ;; esac
job="a2-dry-$run"
case "$act" in
  start)
    case "$mode" in short|full) ;; *) rb_die $RB_E_USAGE "the only option is full (E165's whole dry queue)" ;; esac
    body=$(rb_file body)
    echo "MODE=$mode" > "$body"
    case "$run" in
      e165) cat >> "$body" <<'EOF'
mkdir -p build/e165
[ -e build/e165/dry ] && mv build/e165/dry build/e165/dry.before-$(date +%s)
now=$(date +%s)
printf 'SLOT E165: start %s (aifoundry2) end %s \n' "$now" "$((now + 2700))" > ~/claude/work/q141-a2-e165-dry-slot.txt
python3 tools/claims-v3/e165/queue_e165.py --dry --slots ~/claude/work/q141-a2-e165-dry-slot.txt --runs build/e165/dry \
  --protocol tools/claims-v3/e165/protocol-dry.json --stoptest-board tools/claims-v3/e165/protocol-stoptest-board-dry.json \
  --stoptest-die tools/claims-v3/e165/protocol-stoptest-die-dry.json --cap 30 > build/e165/dry.out 2>&1 < /dev/null &
q=$!
if [ "$MODE" = short ]; then
  i=0; while [ "$i" -lt 120 ] && ! grep -q '"kind": "before_first_launch"' build/e165/dry/queue.jsonl 2>/dev/null; do sleep 1; i=$((i + 1)); done
  touch build/e165/dry/QUEUE-STOP && echo "QUEUE-STOP touched: the dry queue ends after the smoke and the stop tests"
fi
wait "$q"; r=$?
echo "E165 dry queue rc=$r"
grep -hE '"kind": "(smoke_check|stoptest_check|queue_halt|stop|s1_end|queue_end)"' build/e165/dry/queue.jsonl | cut -c1-260
[ "$r" -eq 0 ] && grep -q '"kind": "smoke_check".*"bad": null' build/e165/dry/queue.jsonl &&
  [ "$(grep -c '"kind": "stoptest_check".*"bad": null' build/e165/dry/queue.jsonl)" -eq 2 ] &&
  grep -q '"kind": "queue_end"' build/e165/dry/queue.jsonl
EOF
      ;;
      e167) cat >> "$body" <<'EOF'
bash tools/claims-v3/e167/run_e167.sh dry
EOF
      ;;
      e168) cat >> "$body" <<'EOF'
mkdir -p build/e168/dry
[ -e build/e168/dry/runs ] && mv build/e168/dry/runs build/e168/dry/runs.before-$(date +%s)
now=$(( $(date +%s) + 5 )); end=$((now + 3960))
printf 'SLOT E168: start %s (%s) end %s (%s) \n' "$now" "$(date -d @"$now" '+%H:%M %Z')" "$end" "$(date -d @"$end" '+%H:%M %Z')" > build/e168/dry/slot.txt
python3 tools/claims-v3/e168/queue_e168.py --dry --slots build/e168/dry/slot.txt --runs build/e168/dry/runs \
  --protocol tools/claims-v3/e168/protocol-dry.json \
  --stoptest-board tools/claims-v3/e168/protocol-stoptest-board-dry.json \
  --stoptest-die tools/claims-v3/e168/protocol-stoptest-die-dry.json > build/e168/dry.out 2>&1 < /dev/null
r=$?; echo "E168 dry queue rc=$r"
grep -hE '"kind": "(smoke_check|stoptest_check|queue_halt|s1_end|queue_end)"' build/e168/dry/runs/queue.jsonl | cut -c1-260
[ "$r" -eq 0 ] && grep -q '"kind": "queue_end"' build/e168/dry/runs/queue.jsonl && ! [ -e build/e168/dry/runs/QUEUE-HALT ]
EOF
      ;;
      e169) cat >> "$body" <<'EOF'
mkdir -p build/e169
[ -e build/e169/dry ] && mv build/e169/dry build/e169/dry.before-$(date +%s)
now=$(date +%s)
printf 'SLOT E169: start %s (dry pass on the box) end %s (one hour later) \n' "$now" "$((now + 3600))" > ~/claude/work/q141-a2-e169-dry-slot.txt
nice -n 10 python3 -B tools/claims-v3/e169/queue_e169.py --dry --slots ~/claude/work/q141-a2-e169-dry-slot.txt --runs build/e169/dry \
  --protocol tools/claims-v3/e169/protocol-dry.json --stoptest-board tools/claims-v3/e169/protocol-stoptest-board-dry.json \
  --stoptest-die tools/claims-v3/e169/protocol-stoptest-die-dry.json > build/e169/dry.out 2>&1 < /dev/null
q=$?; echo "E169 dry queue rc=$q"
nice -n 10 python3 -B tools/claims-v3/e169/score_e169.py build/e169/dry/s[1-6] --out build/e169/dry-results.json > build/e169/dry-score.txt
s=$?; echo "E169 dry score rc=$s"
test ! -e build/e169/runs && echo "the real run directory is empty"
grep -hE '"kind": "(smoke_check|stoptest_check|queue_halt|s1_end|queue_end)"' build/e169/dry/queue.jsonl | cut -c1-260
[ "$q" -eq 0 ] && [ "$s" -eq 0 ] && test ! -e build/e169/runs
EOF
      ;;
    esac
    rb_probe aifoundry2
    rb_job_start aifoundry2 "$job" "$body" 2
    ;;
  wait)
    rb_probe aifoundry2
    rb_job_wait aifoundry2 "$job"; rc=$?
    [ -n "${RB_DRY:-}" ] && exit 0
    [ "$rc" -eq 0 ] && [ "$run" = e167 ] && ! rb_has '^dry rc=0 ' && { rb_say "run_e167.sh dry did not print dry rc=0"; exit $RB_E_FAIL; }
    exit "$rc"
    ;;
  *) rb_die $RB_E_USAGE "usage: s15_a2_dry.sh <e165|e167|e168|e169> start [full] | wait" ;;
esac
