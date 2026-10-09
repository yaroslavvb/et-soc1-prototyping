#!/usr/bin/env bash
# burn.sh CARD SECONDS: aifoundry2, after the card-fan swap of Fri 9 Oct 2026 (a dual 92 mm PCI-slot fan bracket in
# place of the stalling 120 mm fan). Byte-for-byte the 6 Oct test (~/claude/work/aifoundry2-fanfix-1006/burn.sh),
# itself the 2 Oct aifoundry1 fan-fix test: repeated sgemm bursts, each under the card lock for <= 8 s (timeout 10),
# then a 2.5 s gap. Stops at the end, at a die mean >= 85 C or a hottest sensor >= 95 C, or if someone else holds a
# card. One log line per burst. Only W differs.
n=$1; dur=${2:-480}; W=~/claude/work/aifoundry2-fanswap-1009; L=$W/burn-c$n.log; end=$(( $(date +%s) + dur ))
cd ~/claude/et-soc1-prototyping/build/sgemm || exit 1
reading() { tail -n 3 ~/live/history/$(date -u +%F).jsonl | python3 -c "
import json,sys
v=None
for l in sys.stdin:
    for c in json.loads(l)[\"cards\"]:
        if c[\"n\"]==$n and c.get(\"die\") is not None: v=c
print(*(v.get(k) for k in (\"die\",\"max\",\"w\")) if v else (\"-\",\"-\",\"-\"))"; }
echo "# $(date "+%F %T") card $n, $dur s" >> "$L"
while [ "$(date +%s)" -lt "$end" ]; do
  et-who --check >/dev/null 2>&1 || { echo "$(date +%T) someone holds a card: stop" >> "$L"; break; }
  ET_DEVICES=$n flock -n /run/lock/etsoc-shire$n.lock timeout 10 host/sgemm_host -n 1024 --reps 100000 --budget 8 >/dev/null 2>&1; rc=$?
  sleep 2.5
  read -r die mx w <<< "$(reading)"
  echo "$(date +%T) rc=$rc die=$die max=$mx w=$w" >> "$L"
  [ "$die" != - ] && { [ "$die" -ge 85 ] || [ "$mx" -ge 95 ]; } && { echo "$(date +%T) STOP: die $die, hottest $mx" >> "$L"; break; }
done
echo "# $(date "+%F %T") done" >> "$L"
