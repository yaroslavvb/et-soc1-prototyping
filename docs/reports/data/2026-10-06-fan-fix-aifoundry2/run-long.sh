#!/usr/bin/env bash
# Wait for burn.sh to finish, then repeat the 21 Sep long session's randn run with its own protocol:
# preheat to 84 C, idle to 80 C, run randn x32 per shire for up to 600 s, stop at a 90 C mean or 73 W; then 180 s idle.
W=~/claude/work/aifoundry2-fanfix-1006
until grep -q " done$" $W/burn-c0.log 2>/dev/null; do sleep 5; done
sleep 20
et-who --check >/dev/null 2>&1 || { echo "$(date +%T) someone holds a card: not starting" ; exit 1; }
echo "$(date "+%F %T") start"
~/claude/et-soc1-prototyping/tools/ettelem/run_horace_long.sh $W/long-1006 $W/long-1006/schedule.txt 80 84 90 900 18600 180
echo "$(date "+%F %T") end rc=$?"
