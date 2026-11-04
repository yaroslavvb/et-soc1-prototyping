# E160: start the detached queue on aifoundry2 (the claim is posted; the registration 2e016917 is pushed)
set -u
cd ~/claude/et-soc1-prototyping || exit 9
date "+%H:%M:%S %Z"
timeout 10 et-who | head -3
NOW=$(date +%s); END=$((NOW+3000))
mkdir -p build/e160 ~/claude/work
if [ -e build/e160/runs ]; then echo "build/e160/runs exists: refusing"; exit 3; fi
echo "SLOT E160: start $NOW (E160, aifoundry2 card 0, Q139) end $END (at most 50 card-minutes)" > ~/claude/work/q139-a2-e160-slot.txt
cat ~/claude/work/q139-a2-e160-slot.txt
setsid nohup python3 tools/claims-v3/e160/queue_e160.py --slots ~/claude/work/q139-a2-e160-slot.txt --runs build/e160/runs --cap 40 > build/e160/queue.out 2>&1 < /dev/null &
sleep 3
head -5 build/e160/queue.out
echo launched
