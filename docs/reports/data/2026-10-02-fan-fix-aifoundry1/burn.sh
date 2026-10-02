#!/usr/bin/env bash
# burn.sh CARD SECONDS: aifoundry1, after card 0's fan was replaced (2 Oct 2026). Repeated sgemm bursts on one card:
# each takes the card's lock and runs <= 8 s (timeout 10), then a 2 s gap (others can get in; the live collector reads
# the temperature). Stops at the end, at a die mean >= 90 C or a hottest sensor >= 100 C, or if someone else holds a card.
# Logs one line per burst to ~/fan-test/burn-c<CARD>.log: time, burst rc, the last die/hottest/W reading.
n=$1; dur=${2:-480}; L=~/fan-test/burn-c$n.log; end=$(( $(date +%s) + dur ))
cd ~/nekko/build/sgemm || exit 1
reading() { tail -n 3 ~/live/history/$(date -u +%F).jsonl | python3 -c "
import json,sys
v=None
for l in sys.stdin:
    for c in json.loads(l)['cards']:
        if c['n']==$n and c.get('die') is not None: v=c
print(*(v.get(k) for k in ('die','max','w')) if v else ('-','-','-'))"; }
echo "# $(date '+%F %T') card $n, $dur s" >> "$L"
while [ "$(date +%s)" -lt "$end" ]; do
  et-who --check >/dev/null 2>&1 || { echo "$(date +%T) someone holds a card: stop" >> "$L"; break; }
  ET_DEVICES=$n flock -n /run/lock/etsoc-shire$n.lock timeout 10 host/sgemm_host -n 1024 --reps 100000 --budget 8 >/dev/null 2>&1; rc=$?
  sleep 2.5
  read -r die mx w <<< "$(reading)"
  echo "$(date +%T) rc=$rc die=$die max=$mx w=$w" >> "$L"
  [ "$die" != - ] && { [ "$die" -ge 90 ] || [ "$mx" -ge 100 ]; } && { echo "$(date +%T) STOP: die $die, hottest $mx" >> "$L"; break; }
done
echo "# $(date '+%F %T') done" >> "$L"
