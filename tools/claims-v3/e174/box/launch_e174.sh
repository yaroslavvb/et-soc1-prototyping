#!/usr/bin/env bash
# E174 box step 5, the launch. Run ONLY after E172 has ended on card 1, the day's one post names aifoundry1's clause for card 0, and box steps 1-3
# read clean. From the Intel (box/step_e174.sh launch [subset], which passes the day's window from the runbook's window file):
#
#   ssh -o BatchMode=yes -o ConnectTimeout=10 aifoundry1 "bash -s -- '<deadline>' '<last start>' '<last end>' [subset]" < tools/claims-v3/e174/box/launch_e174.sh
#
# Each time is as GNU date reads it ('YYYY-MM-DD HH:MM PST'). The deadline is the latest the slot may end (the runbook passes the day's last end less
# 5 minutes). The slot is [now, min(now + 45 min, the deadline)] for the full plan and [now, min(now + 30 min, the deadline)] for the registered
# subset; the queue's own cap ends the session 3 min before the slot's end. E170's launch_e170.sh, with the window passed in (E170's read the round's
# two times from defaults dated 4 Nov 2026). Before anything is launched, it refuses with
#   exit 2  a missing or unreadable time;
#   exit 6  outside the day's window: now after its last start, or a deadline after its last end; the last start is checked again just before the
#           launch;
#   exit 4  a deadline that leaves less than the plan needs: the full plan 35 min (the state reads, the two stop tests and the smoke about 3 min, 126
#           bursts about 26.4 min, the cap's 3 min and a margin), the registered subset 25 min (84 bursts about 17.6 min); checked again just before;
#   exit 3  anything holding card 0's node or lock (anyone's), anything of ours on either card (a node, a lock or a device process), a run queue or
#           session of ours still alive (queue_, session_, block_ or run_eNNN of ours: E172's), or et-holders unreadable (fails closed): E172 must
#           have ended; never two sessions of ours on aifoundry1;
#   exit 5  a queue of E174's already ran in build/e174/runs (move it aside by hand, with a dated note, before a second try);
#   exit 9  check_e174.py not HARNESS OK.
# It records the holders at launch as counts, never names (build/e174/holders-at-launch.txt), and sends no device command: et-holders reads /proc;
# everything that touches the card is queue_e174.py's, which reads card 0's state first through E170's guard.
# SPDX-License-Identifier: Apache-2.0
set -u
cd ~/nekko || exit 1
PLAN=full
args=("$@")
n=${#args[@]}
if [ "$n" -gt 0 ] && [ "${args[$((n - 1))]}" = subset ]; then PLAN=subset; n=$((n - 1)); fi
[ "$n" -eq 3 ] || { echo "usage: '<deadline>' '<last start>' '<last end>' [subset] (each 'YYYY-MM-DD HH:MM PST'): nothing launched"; exit 2; }
DL=${args[0]}; LS_TXT=${args[1]}; EG_TXT=${args[2]}
DLS=$(date -d "$DL" +%s 2>/dev/null) || { echo "not a date: the deadline '$DL': nothing launched"; exit 2; }
LSS=$(date -d "$LS_TXT" +%s 2>/dev/null) || { echo "not a date: the day's last start '$LS_TXT': nothing launched"; exit 2; }
EGS=$(date -d "$EG_TXT" +%s 2>/dev/null) || { echo "not a date: the day's last end '$EG_TXT': nothing launched"; exit 2; }
if [ "$PLAN" = full ]; then NEED_S=2100; CAP=40; SLOT_MIN=45; PROTO=tools/claims-v3/e174/protocol.json
else NEED_S=1500; CAP=25; SLOT_MIN=30; PROTO=tools/claims-v3/e174/protocol-subset.json; fi
now=$(date +%s)
echo "$(date '+%F %T %Z') E174 launch (box/launch_e174.sh), plan $PLAN: slot $SLOT_MIN min, cap $CAP card-minutes, needs $NEED_S s"
echo "deadline '$DL' = $(TZ=America/Los_Angeles date -d @"$DLS" '+%F %T %Z'), $((DLS - now)) s from now"
echo "the day's window: no start after $(TZ=America/Los_Angeles date -d @"$LSS" '+%F %T %Z'), every run ends by $(TZ=America/Los_Angeles date -d @"$EGS" '+%F %T %Z')"
[ "$now" -le "$LSS" ] || { echo "REFUSED: it is $((now - LSS)) s past the day's last start ($LS_TXT): nothing launched"; exit 6; }
[ "$DLS" -le "$EGS" ] || { echo "REFUSED: the deadline is $((DLS - EGS)) s after the day's last end ($EG_TXT): nothing launched"; exit 6; }
[ "$DLS" -ge $((now + NEED_S)) ] || { echo "REFUSED: the deadline is $((DLS - now)) s away; plan $PLAN needs $NEED_S s: nothing launched"; exit 4; }
[ ! -e build/e174/runs/queue.jsonl ] || { echo "REFUSED: build/e174/runs/queue.jsonl exists (a queue of E174's already ran): nothing launched"; exit 5; }
boot=$(date -d "$(uptime -s)" +%s 2>/dev/null); e84=$(date -d '2026-10-31 15:42:00 PDT' +%s)   # v3's fault 12: the identity in the launch's own call
if [ -z "$boot" ] || [ "$boot" -ge "$e84" ]; then
  echo "IDENTITY-STOP: aifoundry1 booted '$(uptime -s)', not before E84's identity read of 2026-10-31 15:42:00 PDT: card 0's image is not carried: nothing launched"; exit 3
fi
echo "identity: aifoundry1 booted $(uptime -s), before E84's identity read: ok (the queue's state gate then reads card 0's module uptime)"
out=$(timeout 20 sudo -n /usr/local/sbin/et-holders 2>&1) || { echo "REFUSED: et-holders unreadable: nothing launched"; exit 3; }
cnt() {  # cnt <node prefix> <lock name> ours|other
  printf '%s\n' "$out" | awk -v me="$USER" -v d="$1" -v l="$2" -v who="$3" \
    '(index($1, d) == 1 || $1 == l) && $2 != "" { if ((who == "ours") == ($2 == me)) n++ } END { print n + 0 }'
}
c0o=$(cnt /dev/et0_ lock:etsoc-shire0.lock ours); c0x=$(cnt /dev/et0_ lock:etsoc-shire0.lock other)
c1o=$(cnt /dev/et1_ lock:etsoc-shire1.lock ours); c1x=$(cnt /dev/et1_ lock:etsoc-shire1.lock other)
po=$(ps -eo uid=,comm= | awk -v me="$(id -u)" '$1 == me && $2 ~ /_host$|^ettelem$|^dev_mngt_servi|^et-powertop$|^mmbench_launch|^sys_emu$/ {n++} END {print n + 0}')
pq=$(ps -eo uid=,args= | awk -v me="$(id -u)" '$1 == me && /(queue|session|block|run)_e1[0-9][0-9]/ {n++} END {print n + 0}')
line="holders at launch (et-holders and ps, counts only): card 0 ours $c0o, another user $c0x; card 1 ours $c1o, another user $c1x; our device processes $po; our run queues or sessions $pq"
echo "$line"
[ $((c0o + c0x)) -eq 0 ] || { echo "REFUSED: card 0's node or lock is held: nothing launched"; exit 3; }
[ $((c1o + po)) -eq 0 ] || { echo "REFUSED: something of ours is on aifoundry1 (E172 must have ended; never two of our sessions there): nothing launched"; exit 3; }
[ "$pq" -eq 0 ] || { echo "REFUSED: a run queue or session of ours is alive on aifoundry1 ($pq; E172's queue may hold no node or lock between its passes): nothing launched"; exit 3; }
python3 -B tools/claims-v3/e174/check_e174.py || exit 9
now=$(date +%s)
[ "$now" -le "$LSS" ] || { echo "REFUSED: after the harness check it is $((now - LSS)) s past the day's last start ($LS_TXT): nothing launched"; exit 6; }
[ "$DLS" -ge $((now + NEED_S)) ] || { echo "REFUSED: after the harness check the deadline is $((DLS - now)) s away (needs $NEED_S s): nothing launched"; exit 4; }
mkdir -p build/e174/runs
END=$((now + SLOT_MIN * 60)); [ "$END" -gt "$DLS" ] && END=$DLS
echo "SLOT E174: start $now ($(date -d @"$now" '+%T %Z')) end $END ($(date -d @"$END" '+%T %Z')) " > build/e174/slot.txt
echo "$(date '+%F %T %Z') $line" > build/e174/holders-at-launch.txt
export ET_DEVICES=0 V3_DEVICE=0 PYTHONDONTWRITEBYTECODE=1
setsid nohup python3 tools/claims-v3/e174/queue_e174.py --slots build/e174/slot.txt --runs build/e174/runs --cap "$CAP" --protocol "$PROTO" \
  > build/e174/queue.out 2>&1 < /dev/null &
sleep 5
echo "LAUNCHED e174 T0=$now ($(date -d @"$now" '+%T %Z')), slot end $(date -d @"$END" '+%T %Z'), plan $PLAN, slot $SLOT_MIN min, cap $CAP, protocol $PROTO"
tail -3 build/e174/queue.out 2>/dev/null | cut -c1-240
