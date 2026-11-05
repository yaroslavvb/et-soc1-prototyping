#!/usr/bin/env bash
# E172 box step 5, the launch (Q142(k6); E172.md, "Card rules, budget and time gates"). It is E164's corrected launcher,
# tools/claims-v3/e164/box/launch_e164_a1.sh (Q141(b)'s fix pass: the deadline is ALL the arguments joined by spaces, so a quoted or an
# unquoted date-time reaches the session whole), with E172's names, its first-pass estimate (800 s) and its pass time (763 s). Run it ONLY
# after the day's one post carries the reservation (`using aifoundry1 card 1 for 1.5 h, until ~HH:MM PST`) and box steps 1-3 read clean.
# From the Intel, at the top of the lab tree:
#
#   ssh -o BatchMode=yes -o ConnectTimeout=10 aifoundry1 "bash -s -- '<YYYY-MM-DD HH:MM PST>'" < tools/claims-v3/e172/box/launch_e172.sh
#
# and, only if the registered subset (E172.md, "The plans": the nine priority-2 kinds dropped) was chosen before the launch:
#
#   ssh -o BatchMode=yes -o ConnectTimeout=10 aifoundry1 "E172_DROP_P2=1 bash -s -- '<YYYY-MM-DD HH:MM PST>'" < tools/claims-v3/e172/box/launch_e172.sh
#
# The deadline is the round's time gate less 10 minutes, as GNU date reads it. Before anything is launched, it refuses with
#   exit 2  no deadline, or not a date;
#   exit 4  a deadline that leaves less than the scoring minimum of two passes even if each pass takes the queue's 800 s first-pass
#           estimate: 1,730 s from now (about 120 s for the opening reads, the stop-path test, the smoke and its gate; two passes of
#           800 s; the 10 s gap). Checked again just before the launch;
#   exit 3  any holder of card 1's nodes or lock (ours or another user's), anything of ours on either card (a node, a lock or a device
#           process: never two of our sessions on aifoundry1, so card 0's E174 starts only after E172 has ended), or et-holders
#           unreadable (fails closed);
#   exit 9  check_e172.py not HARNESS OK (its line `HARNESS DIFFERS - refusing:`, which v3.1's s13 reads as a refusal).
# It prints the parsed deadline (the box's zone and Pacific time) and how many of the 4 planned passes to expect by the queue's rule,
# and records the holders at launch as counts, never names (build/e172/holders-at-launch.txt). It sends no device command: et-holders
# reads /proc only, and everything that touches the card is session_e172.sh's.
set -u
cd ~/nekko || exit 1
DL="$*"
[ -n "$DL" ] || { echo "usage: the deadline is required (the round's time gate less 10 minutes, 'YYYY-MM-DD HH:MM PST'): nothing launched"; exit 2; }
DLS=$(date -d "$DL" +%s 2>/dev/null) || { echo "not a date: '$DL': nothing launched"; exit 2; }
MIN_S=1730                # E172: 120 s for the opening reads, the stop-path test, the smoke and its gate; two passes at the queue's 800 s first estimate; one 10 s gap
now=$(date +%s)
echo "$(date '+%F %T %Z') E172 launch (box/launch_e172.sh)"
echo "deadline '$DL' = $(date -d @"$DLS" '+%F %T %Z') = $(TZ=America/Los_Angeles date -d @"$DLS" '+%F %T %Z'), $((DLS - now)) s from now"
if [ "$DLS" -lt $((now + MIN_S)) ]; then
  echo "REFUSED: the deadline is $((DLS - now)) s away; the scoring minimum, two passes, needs at least $MIN_S s: nothing launched"; exit 4
fi
# The passes to expect, by queue_e172.sh's own admission rule (a pass starts only if now + projected <= the deadline and E172_T0 + 3,840 s;
# projected is 800 s for the first pass, then the longest pass measured): the first pass about 60 s after E172_T0 (E157's 58 s on this
# card), every pass taking E164's longest on this card scaled to E172's 86 launches (763 s), 10 s between. An estimate, never a gate.
fit=0; s=$((now + 60)); lim=$((now + 3840)); proj=800
while [ "$fit" -lt 4 ]; do { [ $((s + proj)) -le "$DLS" ] && [ $((s + proj)) -le "$lim" ]; } || break; fit=$((fit + 1)); s=$((s + 763 + 10)); proj=763; done
echo "passes expected by the queue's rule: $fit of the 4 planned (two kept passes are the scoring minimum)"
# Holders, read as E172's block and session read them (et-holders through sudo -n), counted per card; no name is printed or kept.
OTHER_COMM='_host$|^ettelem$|^dev_mngt_servi|^et-powertop$|^mmbench_launch|^sys_emu$|^Runner.Worker$'     # lib.sh's OTHER_COMM
DEV_COMM='_host$|^ettelem$|^dev_mngt_servi|^et-powertop$|^mmbench_launch|^sys_emu$'                       # lib.sh's DEV_COMM
out=$(timeout 20 sudo -n /usr/local/sbin/et-holders 2>&1) || { echo "REFUSED: et-holders unreadable: nothing launched"; exit 3; }
cnt() {  # cnt <node prefix> <lock name> ours|other
  printf '%s\n' "$out" | awk -v me="$USER" -v d="$1" -v l="$2" -v who="$3" \
    '(index($1, d) == 1 || $1 == l) && $2 != "" { if ((who == "ours") == ($2 == me)) n++ } END { print n + 0 }'
}
c1o=$(cnt /dev/et1_ lock:etsoc-shire1.lock ours); c1x=$(cnt /dev/et1_ lock:etsoc-shire1.lock other)
c0o=$(cnt /dev/et0_ lock:etsoc-shire0.lock ours); c0x=$(cnt /dev/et0_ lock:etsoc-shire0.lock other)
cz=$(printf '%s\n' "$out" | awk '($1 ~ /^\/dev\/et/ || $1 ~ /^lock:/) && $1 !~ /^\/dev\/et[01]_/ && $1 != "lock:etsoc-shire0.lock" && $1 != "lock:etsoc-shire1.lock" {n++} END {print n + 0}')
pso=$(ps -eo uid=,pid=,comm=)
po=$(printf '%s\n' "$pso" | awk -v me="$(id -u)" -v re="$DEV_COMM" '$1 == me && $3 ~ re {n++} END {print n + 0}')
px=$(printf '%s\n' "$pso" | awk -v me="$(id -u)" -v re="$OTHER_COMM" '$1 != me && $3 ~ re {n++} END {print n + 0}')
pci=$(printf '%s\n' "$pso" | awk '$3 ~ /^Runner.Worker$/ {n++} END {print n + 0}')
line="holders at launch (et-holders and ps, counts only): card 1 ours $c1o, another user $c1x; card 0 ours $c0o, another user $c0x; other nodes or locks $cz; our device processes $po; other users' device processes $px (CI jobs $pci)"
echo "$line"
if [ $((c1o + c1x)) -gt 0 ]; then echo "REFUSED: card 1's nodes or lock are held: nothing launched"; exit 3; fi
if [ $((c0o + po)) -gt 0 ]; then echo "REFUSED: something of ours is on aifoundry1 (never two of our sessions there): nothing launched"; exit 3; fi
[ "$c0x" -gt 0 ] || [ "$px" -gt 0 ] && echo "note: another user is on card 0 or runs a device process; that does not block E172 (E164.md.dated-note.md A1-2, carried), recorded"
python3 -B tools/claims-v3/e172/check_e172.py || exit 9
now=$(date +%s)
if [ "$DLS" -lt $((now + MIN_S)) ]; then
  echo "REFUSED: after the harness check the deadline is $((DLS - now)) s away (needs $MIN_S s): nothing launched"; exit 4
fi
mkdir -p build/e172
if [ -e build/e172/session.log ]; then mv build/e172/session.log build/e172/session.log.before-$(date +%s); fi
echo "$(date '+%F %T %Z') $line" > build/e172/holders-at-launch.txt
E172_T0=$(date +%s); export E172_T0 E172_DEADLINE="$DL"
[ -n "${E172_DROP_P2:-}" ] && export E172_DROP_P2
echo "$E172_T0" > build/e172/T0
setsid nohup bash tools/claims-v3/e172/session_e172.sh > build/e172/session.out 2>&1 < /dev/null &
sleep 8
echo "launched T0=$E172_T0 $(date -d @"$E172_T0" '+%T %Z'), E172_DEADLINE='$DL' ($(date -d @"$DLS" '+%T %Z')), E172_DROP_P2=${E172_DROP_P2:-0}"
cat build/e172/session.log 2>/dev/null | sed -E 's#^(/dev/et[0-9]+_[a-z]+|lock:[^ ]+)( +)[^ ]+#\1\2<holder>#'   # et-who's logins never printed
