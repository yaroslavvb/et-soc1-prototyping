#!/usr/bin/env bash
# Q141(k), go checklist step 16: E165 on aifoundry2, first there, launched detached (it returns at once), ONLY after the day's post
# names aifoundry2, step 14 reads clean and the planned dry passes of step 15 have all ended rc 0. The kit's command (README box
# step 7): the slot file ~/claude/work/q141-a2-e165-slot.txt with one line `SLOT E165: start <epoch> (aifoundry2) end <epoch + 2700> `,
# then `setsid nohup python3 tools/claims-v3/e165/queue_e165.py --slots ~/claude/work/q141-a2-e165-slot.txt --runs build/e165/runs
# --cap 40 > build/e165/queue.out 2>&1 < /dev/null &`; the registered subset (passes 1-2): --cap 25 and a 1,800 s slot. The queue runs
# the smoke, the DMA rule and both stop-path tests itself, and halts with QUEUE-HALT and no session if any fails.
#
#   bash tools/claims-v3/q141k-runbook/v2/s16_a2_e165.sh [full|subset]
# v2 (Q141(k)'s verifier, nit 5): a planned dry pass counts only if it ended rc 0 today; another card day's exit status never does.
#
# Refused (10) before any launch: past the last start, a slot that would pass the last end, a planned dry pass not ended rc 0, a dry
# pass still running, a session of ours on the card, or build/e165/runs already holding a queue.
# SPDX-License-Identifier: Apache-2.0
. "$(dirname "${BASH_SOURCE[0]}")/rb_common.sh"
rb_init s16_a2_e165
mode=${1:-full}
case "$mode" in full) slot=2700; cap=40 ;; subset) slot=1800; cap=25 ;; *) rb_die $RB_E_USAGE "usage: s16_a2_e165.sh [full|subset]" ;; esac
rb_window
rb_need_start
rb_need_end "$slot"
case "$RB_PLAN" in full) planned="e165 e167 e168 e169" ;; b) planned="e165 e167" ;; a) planned="e165" ;; esac
f=$(rb_file e165)
{ rb_prelude aifoundry2
  echo "PLANNED=$(printf '%q' "$planned"); SLOT=$slot; CAP=$cap"
  rb_guard_text
  cat <<'EOF'
for r in $PLANNED; do
  job_ok_today "a2-dry-$r" || { echo "REFUSED: the dry pass of $r has not ended rc 0 today (s15_a2_dry.sh $r): all planned ones before E165's session"; exit 3; }
done
[ -e build/e165/runs/queue.jsonl ] && { echo "REFUSED: build/e165/runs already holds a queue"; exit 3; }
mkdir -p build/e165
now=$(date +%s)
printf 'SLOT E165: start %s (aifoundry2) end %s \n' "$now" "$((now + SLOT))" > ~/claude/work/q141-a2-e165-slot.txt
setsid nohup python3 tools/claims-v3/e165/queue_e165.py --slots ~/claude/work/q141-a2-e165-slot.txt --runs build/e165/runs --cap "$CAP" > build/e165/queue.out 2>&1 < /dev/null &
sleep 3
echo "LAUNCHED e165 $(date '+%F %T %Z') (--cap $CAP, slot $SLOT s)"
cat ~/claude/work/q141-a2-e165-slot.txt; tail -n 3 build/e165/queue.out | cut -c1-300
EOF
} > "$f"
rb_probe aifoundry2
rb_remote launch aifoundry2 "E165's slot and detached queue (--cap $cap)" "$f"
[ -n "${RB_DRY:-}" ] && exit 0
rb_launched e165
rb_say "E165's queue started (--cap $cap); wait with s20_wait.sh e165 and read its smoke and stop-test checks"
