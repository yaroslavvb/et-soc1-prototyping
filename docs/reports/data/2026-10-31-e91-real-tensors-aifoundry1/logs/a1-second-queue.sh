# E91 A1: wait (<= 520 s) for the first queue to stop; if its budget rule stopped it before p9114, start pass 9114
# alone with E91_BUDGET_MIN = floor(35 - card-minutes used since the claim (21:10:07 PDT) - 3) and E91_FIRST_S = the
# longest pass the first queue measured (from its log), deadline 22:25.
cd ~/nekko
L=build/e91-queue.log
end=$(( $(date +%s) + 520 ))
while [ "$(date +%s)" -lt "$end" ]; do
  grep -q -E 'queue done|budget: stopping|stopping after|exists: stopping' "$L" 2>/dev/null && break
  sleep 2
done
date '+%T %Z'; tail -4 "$L"
if grep -q 'budget: stopping before p9114' "$L"; then
  claim=$(date -d '2026-10-31 21:10:07 PDT' +%s); now=$(date +%s)
  longest=$(awk '/ p91[0-9][0-9] starts /{split($1,a,":"); s[$2]=a[1]*3600+a[2]*60+a[3]} / p91[0-9][0-9] rc=0 /{split($1,a,":"); d=a[1]*3600+a[2]*60+a[3]-s[$2]; if (d>m) m=d} END{print m}' "$L")
  budget=$(python3 -c "import math,sys; print(max(0, math.floor(35 - (int(sys.argv[1]) - int(sys.argv[2])) / 60.0 - 3)))" "$now" "$claim")
  echo "A1: used $(( (now - claim) )) s since the claim; E91_BUDGET_MIN=$budget; E91_FIRST_S=$longest"
  mv "$L" build/e91-queue-1.log
  E91_BUDGET_MIN=$budget E91_FIRST_S=$longest E91_DEADLINE=22:25 bash tools/claims-v3/kinds/run_e91.sh go 9114 1
  sleep 4; tail -3 "$L"
else
  echo "A1: nothing to add (the first queue did not stop at its budget before p9114)"
fi
pgrep -u "$(id -u)" -f 'queue_e86.sh|block_e86.sh|run_e86.py' > /dev/null && echo "QUEUE RUNNING" || echo "QUEUE ENDED"
