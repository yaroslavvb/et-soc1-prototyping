#!/usr/bin/env bash
# Q141(k), go checklist step 19: E169 on aifoundry2, last there, after E168's queue has ended, launched detached (it returns at once).
# The kit's commands (README box step 5, with the dated note's step 4 run before it): build/e169/runs must not exist; then
# `SLOT E169: start <epoch s> (...) end <epoch s> (...) ` (about 45 minutes) in ~/claude/work/q141-a2-e169-slot.txt and
# `setsid nohup python3 tools/claims-v3/e169/queue_e169.py --slots ~/claude/work/q141-a2-e169-slot.txt --runs build/e169/runs >
# build/e169/queue.out 2>&1 < /dev/null &`. The smoke and both stop-path tests run inside it; if the hottest-sensor field reads 76 C
# or more after E168, the smoke's die stop halts the queue before any work launch (safe; a retry needs a dated amendment).
#
#   bash tools/claims-v3/q141k-runbook/s19_a2_e169.sh
# SPDX-License-Identifier: Apache-2.0
. "$(dirname "${BASH_SOURCE[0]}")/rb_common.sh"
rb_init s19_a2_e169
rb_window
[ "$RB_PLAN" = full ] || rb_die $RB_E_USAGE "plan $RB_PLAN does not run E169"
rb_need_start
rb_need_end 2700
f=$(rb_file e169)
{ rb_prelude aifoundry2
  rb_guard_text
  cat <<'EOF'
[ "$(cat build/q141k/jobs/a2-dry-e169.rc 2>/dev/null)" = 0 ] || { echo "REFUSED: E169's dry pass has not ended rc 0"; exit 3; }
if [ -e build/e168/runs/status.json ] && ! grep -qE '"state": "(ended|halted)"' build/e168/runs/status.json; then echo "REFUSED: E168's queue has not ended"; exit 3; fi
[ -e build/e169/runs ] && { echo "REFUSED: build/e169/runs exists (README.md.dated-note.md, box step 4: the queue must start in an empty directory)"; exit 3; }
mkdir -p build/e169
now=$(date +%s); end=$((now + 2700))
printf 'SLOT E169: start %s (%s) end %s (%s) \n' "$now" "$(date -d @"$now" '+%H:%M %Z')" "$end" "$(date -d @"$end" '+%H:%M %Z')" > ~/claude/work/q141-a2-e169-slot.txt
setsid nohup python3 tools/claims-v3/e169/queue_e169.py --slots ~/claude/work/q141-a2-e169-slot.txt --runs build/e169/runs > build/e169/queue.out 2>&1 < /dev/null &
sleep 3
echo "LAUNCHED e169 $(date '+%F %T %Z')"
cat ~/claude/work/q141-a2-e169-slot.txt; tail -n 3 build/e169/queue.out | cut -c1-300
EOF
} > "$f"
rb_probe aifoundry2
rb_remote launch aifoundry2 "E169's slot (45 min) and detached queue" "$f"
[ -n "${RB_DRY:-}" ] && exit 0
rb_launched e169
rb_say "E169's queue started; wait with s20_wait.sh e169 (about 11-16 card-minutes)"
