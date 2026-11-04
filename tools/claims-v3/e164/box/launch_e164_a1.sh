#!/usr/bin/env bash
# E164 box step 5, the launch, as corrected by Q141(b)'s fix pass (Wed 4 Nov 2026, before any E164 data or claim; README.md.dated-note.md,
# § 1). It replaces box/launch_e164.sh, which stays as committed (ce10e301) and must NOT be used: its usage line passed the deadline as
# three words, so the box saw only the date (that day's 00:00, already past), and the session would have run the stop-path test and the
# smoke and then no pass. Run this ONLY after the day's one post carries the reservation (`using aifoundry1 card 1 for 1.5 h, until
# ~HH:MM PST`) and box steps 1-3 read clean. From the Intel, at the top of the lab tree:
#
#   ssh -o BatchMode=yes -o ConnectTimeout=10 aifoundry1 "bash -s -- '<YYYY-MM-DD HH:MM PST>'" < tools/claims-v3/e164/box/launch_e164_a1.sh
#
# and, only if the registered subset (E164.md, the droppable tests) was chosen before the launch:
#
#   ssh -o BatchMode=yes -o ConnectTimeout=10 aifoundry1 "E164_DROP_P2=1 bash -s -- '<YYYY-MM-DD HH:MM PST>'" < tools/claims-v3/e164/box/launch_e164_a1.sh
#
# The deadline is the round's time gate less 10 minutes, as GNU date reads it. It is ALL the arguments joined by single spaces, so the old
# unquoted form ('bash -s' -- '<deadline>') gives the same string. Before anything is launched, it refuses with
#   exit 2  no deadline, or not a date;
#   exit 4  a deadline that leaves less than the scoring minimum of two passes even if each pass takes the queue's 900 s first-pass
#           estimate: 1,930 s from now (about 120 s for the opening reads, the stop-path test, the smoke and its gate; two passes of
#           900 s; the 10 s gap). Checked again just before the launch;
#   exit 3  any holder of card 1's nodes or lock (ours or another user's), anything of ours on either card (a node, a lock or a device
#           process: never two of our sessions on aifoundry1), or et-holders unreadable (fails closed);
#   exit 9  check_e164.py not HARNESS OK.
# It prints the parsed deadline (the box's zone and Pacific time) and how many of the 4 planned passes to expect by the queue's rule,
# and records the holders at launch as counts, never names (build/e164/holders-at-launch.txt: whether card 0 was in use, E164.md.dated-note.md
# A1-2). It sends no device command: et-holders reads /proc only, and everything that touches the card is session_e164.sh's, unchanged.
set -u
cd ~/nekko || exit 1
DL="$*"
[ -n "$DL" ] || { echo "usage: the deadline is required (the round's time gate less 10 minutes, 'YYYY-MM-DD HH:MM PST'): nothing launched"; exit 2; }
DLS=$(date -d "$DL" +%s 2>/dev/null) || { echo "not a date: '$DL': nothing launched"; exit 2; }
MIN_S=1930
now=$(date +%s)
echo "$(date '+%F %T %Z') E164 launch (box/launch_e164_a1.sh)"
echo "deadline '$DL' = $(date -d @"$DLS" '+%F %T %Z') = $(TZ=America/Los_Angeles date -d @"$DLS" '+%F %T %Z'), $((DLS - now)) s from now"
if [ "$DLS" -lt $((now + MIN_S)) ]; then
  echo "REFUSED: the deadline is $((DLS - now)) s away; the scoring minimum, two passes, needs at least $MIN_S s: nothing launched"; exit 4
fi
# The passes to expect, by queue_e164.sh's own admission rule (a pass starts only if now + projected <= the deadline and E164_T0 + 3,840 s;
# projected is 900 s for the first pass, then the longest pass measured): the first pass about 60 s after E164_T0 (E157's 58 s on this
# card), every pass taking E157's longest on this card scaled to E164's 98 launches (848 s), 10 s between. An estimate, never a gate.
fit=0; s=$((now + 60)); lim=$((now + 3840)); proj=900
while [ "$fit" -lt 4 ]; do { [ $((s + proj)) -le "$DLS" ] && [ $((s + proj)) -le "$lim" ]; } || break; fit=$((fit + 1)); s=$((s + 848 + 10)); proj=848; done
echo "passes expected by the queue's rule: $fit of the 4 planned (two kept passes are the scoring minimum)"
# Holders, read as E164's block and session read them (et-holders through sudo -n), counted per card; no name is printed or kept.
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
[ "$c0x" -gt 0 ] || [ "$px" -gt 0 ] && echo "note: another user is on card 0 or runs a device process; that does not block E164 (E164.md.dated-note.md A1-2), recorded"
python3 -B tools/claims-v3/e164/check_e164.py || exit 9
now=$(date +%s)
if [ "$DLS" -lt $((now + MIN_S)) ]; then
  echo "REFUSED: after the harness check the deadline is $((DLS - now)) s away (needs $MIN_S s): nothing launched"; exit 4
fi
mkdir -p build/e164
if [ -e build/e164/session.log ]; then mv build/e164/session.log build/e164/session.log.before-$(date +%s); fi
echo "$(date '+%F %T %Z') $line" > build/e164/holders-at-launch.txt
E164_T0=$(date +%s); export E164_T0 E164_DEADLINE="$DL"
[ -n "${E164_DROP_P2:-}" ] && export E164_DROP_P2
echo "$E164_T0" > build/e164/T0
setsid nohup bash tools/claims-v3/e164/session_e164.sh > build/e164/session.out 2>&1 < /dev/null &
sleep 8
echo "launched T0=$E164_T0 $(date -d @"$E164_T0" '+%T %Z'), E164_DEADLINE='$DL' ($(date -d @"$DLS" '+%T %Z')), E164_DROP_P2=${E164_DROP_P2:-0}"
cat build/e164/session.log 2>/dev/null | sed -E 's#^(/dev/et[0-9]+_[a-z]+|lock:[^ ]+)( +)[^ ]+#\1\2<holder>#'   # et-who's logins never printed
