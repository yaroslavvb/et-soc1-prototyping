#!/bin/bash
# E126: refuse unless the three binaries are E119's and nobody holds the card; write the slot file; start the queue detached on aifoundry2.
# The slot starts now + 20 s and ends 49 min later (2940 s); the session's own cap stops it 150 s before the end; the hard stop touches STOP 120 s before.
set -u
cd ~/claude/et-soc1-prototyping || exit 9
mkdir -p ~/claude/work build/e126
if [ -e build/e126/runs/queue.jsonl ]; then echo "refused: build/e126/runs already holds a queue"; exit 3; fi
ok=1
while read h f; do got=$(sha256sum "$f" | cut -d' ' -f1); if [ "$got" = "$h" ]; then echo "sha256 ok $f"; else echo "refused: $f sha256 $got, E119's $h"; ok=0; fi; done <<'EOL'
4c6253fbbfcf9c9f43354b3900d79221454f1f3163ae60d44e6b6842851a06ef build/e119/host/sparsity_host
27cb001959871fa8c5ef9bf8570cd61add15fb0b8b817ce12a71ed3a7841e318 build/e119/kernel/sparsity.elf
77a46171c915d3a92898af9ffe04d92b86b65f4d36bc29d58f5c086f8accfeb5 build/ettelem-hpl/ettelem
EOL
[ "$ok" = 1 ] || exit 3
w=$(timeout 10 et-who 2>&1 | head -1)
case "$w" in "No process holds"*) echo "et-who: $w" ;; *) echo "refused: et-who: $w"; exit 3 ;; esac
flock -n /run/lock/etsoc-shire0.lock true || { echo "refused: the card lock is held"; exit 3; }
st=$(( $(date +%s) + 20 )); en=$(( st + 2940 ))
echo "SLOT E126: start $st ($(date -d @$st '+%T %Z')) end $en ($(date -d @$en '+%T %Z')) " > ~/claude/work/q136-a2-e126-slot.txt
cat ~/claude/work/q136-a2-e126-slot.txt
cat > build/e126/start_queue.sh <<'EOQ'
#!/bin/bash
cd ~/claude/et-soc1-prototyping || exit 9
setsid nohup python3 tools/claims-v3/e126/queue_e126.py --slots ~/claude/work/q136-a2-e126-slot.txt --runs build/e126/runs --cap 44 --cap-margin-s 150 > build/e126/queue.out 2>&1 < /dev/null &
echo "queue pid $!"
EOQ
bash build/e126/start_queue.sh
sleep 3
head -5 build/e126/queue.out
