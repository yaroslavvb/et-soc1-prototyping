#!/usr/bin/env bash
# E170 box step 5, the launch. Run ONLY after E164 has ended on card 1, the day's one post names aifoundry1's clause for card 0, and box steps 1-3 read
# clean. From the Intel (box/step_e170.sh launch '<deadline>' [subset]), the quoting inside the remote command (E164's fix):
#
#   ssh -o BatchMode=yes -o ConnectTimeout=10 aifoundry1 "bash -s -- '<YYYY-MM-DD HH:MM PST>'" < tools/claims-v3/e170/box/launch_e170.sh
#   ssh -o BatchMode=yes -o ConnectTimeout=10 aifoundry1 "bash -s -- '<YYYY-MM-DD HH:MM PST>' subset" < tools/claims-v3/e170/box/launch_e170.sh
#
# The deadline is the round's last end (19:00 PST on 4 Nov 2026), as GNU date reads it: all the arguments but a last word "subset", joined by spaces.
# The slot is [now, min(now + 45 min, the deadline)]; the queue's own cap ends the session 3 min before the slot's end. Before anything is launched,
# it refuses with
#   exit 2  no deadline, or not a date;
#   exit 4  a deadline that leaves less than the plan needs: the full plan 36 min (the state reads, the two stop tests and the smoke about 3 min, 135
#           bursts about 27 min, the cap's 3 min and a 3 min margin), the registered subset 26 min (90 bursts about 18 min); checked again just before;
#   exit 3  anything holding card 0's node or lock (anyone's), anything of ours on either card (a node, a lock or a device process: E164 must have
#           ended), or et-holders unreadable (fails closed);
#   exit 5  a queue of E170's already ran in build/e170/runs (move it aside by hand, with a dated note, before a second try);
#   exit 9  check_e170.py not HARNESS OK.
# It records the holders at launch as counts, never names (build/e170/holders-at-launch.txt), and sends no device command: et-holders reads /proc;
# everything that touches the card is queue_e170.py's, which reads card 0's state first through E170's guard.
# SPDX-License-Identifier: Apache-2.0
set -u
cd ~/nekko || exit 1
PLAN=full
args=("$@")
n=${#args[@]}
if [ "$n" -gt 0 ] && [ "${args[$((n - 1))]}" = subset ]; then PLAN=subset; last=$((n - 1)); unset "args[$last]"; fi
DL="${args[*]:-}"
[ -n "$DL" ] || { echo "usage: the deadline is required ('YYYY-MM-DD HH:MM PST'): nothing launched"; exit 2; }
DLS=$(date -d "$DL" +%s 2>/dev/null) || { echo "not a date: '$DL': nothing launched"; exit 2; }
if [ "$PLAN" = full ]; then NEED_S=2160; CAP=40; PROTO=tools/claims-v3/e170/protocol.json; else NEED_S=1560; CAP=25; PROTO=tools/claims-v3/e170/protocol-subset.json; fi
now=$(date +%s)
echo "$(date '+%F %T %Z') E170 launch (box/launch_e170.sh), plan $PLAN"
echo "deadline '$DL' = $(date -d @"$DLS" '+%F %T %Z') = $(TZ=America/Los_Angeles date -d @"$DLS" '+%F %T %Z'), $((DLS - now)) s from now"
[ "$DLS" -ge $((now + NEED_S)) ] || { echo "REFUSED: the deadline is $((DLS - now)) s away; plan $PLAN needs $NEED_S s: nothing launched"; exit 4; }
[ ! -e build/e170/runs/queue.jsonl ] || { echo "REFUSED: build/e170/runs/queue.jsonl exists (a queue of E170's already ran): nothing launched"; exit 5; }
out=$(timeout 20 sudo -n /usr/local/sbin/et-holders 2>&1) || { echo "REFUSED: et-holders unreadable: nothing launched"; exit 3; }
cnt() {  # cnt <node prefix> <lock name> ours|other
  printf '%s\n' "$out" | awk -v me="$USER" -v d="$1" -v l="$2" -v who="$3" \
    '(index($1, d) == 1 || $1 == l) && $2 != "" { if ((who == "ours") == ($2 == me)) n++ } END { print n + 0 }'
}
c0o=$(cnt /dev/et0_ lock:etsoc-shire0.lock ours); c0x=$(cnt /dev/et0_ lock:etsoc-shire0.lock other)
c1o=$(cnt /dev/et1_ lock:etsoc-shire1.lock ours); c1x=$(cnt /dev/et1_ lock:etsoc-shire1.lock other)
po=$(ps -eo uid=,comm= | awk -v me="$(id -u)" '$1 == me && $2 ~ /_host$|^ettelem$|^dev_mngt_servi|^et-powertop$|^mmbench_launch|^sys_emu$/ {n++} END {print n + 0}')
line="holders at launch (et-holders and ps, counts only): card 0 ours $c0o, another user $c0x; card 1 ours $c1o, another user $c1x; our device processes $po"
echo "$line"
[ $((c0o + c0x)) -eq 0 ] || { echo "REFUSED: card 0's node or lock is held: nothing launched"; exit 3; }
[ $((c1o + po)) -eq 0 ] || { echo "REFUSED: something of ours is on aifoundry1 (E164 must have ended; never two of our sessions there): nothing launched"; exit 3; }
python3 -B tools/claims-v3/e170/check_e170.py || exit 9
now=$(date +%s)
[ "$DLS" -ge $((now + NEED_S)) ] || { echo "REFUSED: after the harness check the deadline is $((DLS - now)) s away (needs $NEED_S s): nothing launched"; exit 4; }
mkdir -p build/e170/runs
END=$((now + 45 * 60)); [ "$END" -gt "$DLS" ] && END=$DLS
echo "SLOT E170: start $now ($(date -d @"$now" '+%T %Z')) end $END ($(date -d @"$END" '+%T %Z')) " > build/e170/slot.txt
echo "$(date '+%F %T %Z') $line" > build/e170/holders-at-launch.txt
export ET_DEVICES=0 V3_DEVICE=0 PYTHONDONTWRITEBYTECODE=1
setsid nohup python3 tools/claims-v3/e170/queue_e170.py --slots build/e170/slot.txt --runs build/e170/runs --cap "$CAP" --protocol "$PROTO" \
  > build/e170/queue.out 2>&1 < /dev/null &
sleep 5
echo "launched T0=$now ($(date -d @"$now" '+%T %Z')), slot end $(date -d @"$END" '+%T %Z'), plan $PLAN, cap $CAP, protocol $PROTO"
tail -3 build/e170/queue.out 2>/dev/null | cut -c1-240
