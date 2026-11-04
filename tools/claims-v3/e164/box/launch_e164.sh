#!/usr/bin/env bash
# E164 box step 4, ONLY after the day's one post carries the reservation (`using aifoundry1 card 1 for 1.5 h, until ~HH:MM PST`) and
# box steps 1-3 read clean. The deadline is the round's time gate less 10 minutes, as GNU date reads it. From the Intel:
#   ssh -o BatchMode=yes -o ConnectTimeout=10 aifoundry1 'bash -s' -- '<YYYY-MM-DD HH:MM PST>' < tools/claims-v3/e164/box/launch_e164.sh
# Add E164_DROP_P2=1 before setsid only if the registered subset is chosen before the launch (E164.md, the droppable tests).
cd ~/nekko || exit 1
DL=${1:?the deadline: the round time gate less 10 minutes}
date -d "$DL" +%s > /dev/null || { echo "not a date: $DL"; exit 2; }
date '+%T %Z'
timeout 20 et-who 2>&1 | head -3
python3 -B tools/claims-v3/e164/check_e164.py || exit 9
mkdir -p build/e164
if [ -e build/e164/session.log ]; then mv build/e164/session.log build/e164/session.log.before-$(date +%s); fi
E164_T0=$(date +%s); export E164_T0 E164_DEADLINE="$DL"
echo "$E164_T0" > build/e164/T0
setsid nohup bash tools/claims-v3/e164/session_e164.sh > build/e164/session.out 2>&1 < /dev/null &
sleep 8
echo "launched T0=$E164_T0 $(date -d @"$E164_T0" '+%T %Z'), deadline $DL"
cat build/e164/session.log 2>/dev/null
