#!/usr/bin/env bash
# Q141(k), go checklist step 18: E168 on aifoundry2, after E167's queue has ended (or E167 was skipped), launched detached (it returns
# at once). The kit's commands (README step 7): `SLOT E168: start <epoch s> (<HH:MM PST>) end <epoch s + 3960> (<HH:MM PST>) ` (a
# trailing space) in ~/claude/work/q141-a2-e168-slot.txt, then `setsid nohup python3 tools/claims-v3/e168/queue_e168.py --slots
# ~/claude/work/q141-a2-e168-slot.txt --runs build/e168/runs > build/e168/queue.out 2>&1 < /dev/null &`. The queue runs the smoke
# (the check of C on all four launches) and both stop-path tests first; its first cold gate waits at most 360 s for 46 C.
#
#   bash tools/claims-v3/q141k-runbook/v2/s18_a2_e168.sh
# v2 (Q141(k)'s verifier, nit 5): E168's dry pass counts only if it ended rc 0 today.
# SPDX-License-Identifier: Apache-2.0
. "$(dirname "${BASH_SOURCE[0]}")/rb_common.sh"
rb_init s18_a2_e168
rb_window
[ "$RB_PLAN" = full ] || rb_die $RB_E_USAGE "plan $RB_PLAN does not run E168"
rb_need_start
rb_need_end 3960
f=$(rb_file e168)
{ rb_prelude aifoundry2
  rb_guard_text
  cat <<'EOF'
job_ok_today a2-dry-e168 || { echo "REFUSED: E168's dry pass has not ended rc 0 today (s15_a2_dry.sh e168)"; exit 3; }
if [ -e build/e167/runs/status.json ] && ! grep -q '"state": "ended"' build/e167/runs/status.json; then echo "REFUSED: E167's queue has not ended"; exit 3; fi
[ -e build/e168/runs/queue.jsonl ] && { echo "REFUSED: build/e168/runs already holds a queue"; exit 3; }
mkdir -p build/e168
now=$(date +%s); end=$((now + 3960))
printf 'SLOT E168: start %s (%s) end %s (%s) \n' "$now" "$(date -d @"$now" '+%H:%M %Z')" "$end" "$(date -d @"$end" '+%H:%M %Z')" > ~/claude/work/q141-a2-e168-slot.txt
setsid nohup python3 tools/claims-v3/e168/queue_e168.py --slots ~/claude/work/q141-a2-e168-slot.txt --runs build/e168/runs > build/e168/queue.out 2>&1 < /dev/null &
sleep 3
echo "LAUNCHED e168 $(date '+%F %T %Z')"
cat ~/claude/work/q141-a2-e168-slot.txt; tail -n 3 build/e168/queue.out | cut -c1-300
EOF
} > "$f"
rb_probe aifoundry2
rb_remote launch aifoundry2 "E168's slot (66 min) and detached queue" "$f"
[ -n "${RB_DRY:-}" ] && exit 0
rb_launched e168
rb_say "E168's queue started; wait with s20_wait.sh e168 (about 42-53 card-minutes)"
