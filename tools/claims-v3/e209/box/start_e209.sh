#!/usr/bin/env bash
# E209 (Q202, lane kit-e209, Tue 17 Nov 2026, before any E209 datum): start E209's session detached on aifoundry2 and return at once.
# E208's src/start_mms.sh (tools/claims-v3/e208/proposal/src/start_mms.sh, unchanged beside it in the box's src/) for E209's one
# session, with three refusals more (THE REBOOT GATE's folder, THE FIRST CARD COMMAND's age, the quiet desk flag's owner): runbook
# step 9 (rb/s11_session_e209.sh) calls it from the box root, right after fwgate's own guard over step 7's folder.
#   [E209_QUIET_FILE=<the round's quiet-desk flag> E209_QUIET_LANE=<lane>] \
#     bash <root>/src/start_e209.sh <last end: epoch seconds> <step 7's first card command: epoch seconds>
# Refusals (exit 3, the reason printed; nothing started, no device opened):
#   - this host is not aifoundry2; the schedule src/sched/a2c0-E209.json is missing;
#   - the last end is more than 4 hours away or less than 10 minutes away (E208's);
#   - THE FIRST CARD COMMAND (step 7's stamp, <first>) is in the future or more than E209_FIRST_MAX_S (120) seconds back;
#   - THE REBOOT GATE's folder first/<first> (step 7 wrote it) is missing, or holds neither one fwgate read record of THIS boot,
#     written today, verdict EQUAL, desk_test false (fwgate.py read's record: a second layer under fwgate's own guard, which step 9
#     ran just before this call), nor fwgate's CONTINUITY line (look.txt, written by step 7 when fwgate's look read CONTINUITY and
#     nothing was sent); a record of a desk test is taken only with E209_DESKTEST=1, and then the start line and the session folder
#     say DESKTEST (the collection refuses such a session outside a desk test);
#   - E209_QUIET_FILE is given and does not exist, or its first word is not E209_QUIET_LANE (THE QUIET DESK FLAG is the card lane's);
#   - the box lock run/box.lock is held (a session, a build or a dry pass of the kit), no build record, the harness differs (E208's);
#   - sessions/<T0>-a2c0-E209 exists already (one session a second).
# Then: step 7's folder is copied into the session's first/ (committed with the data), a stale run/STOP is moved aside, run/current-a2c0
# names the session, and session_e209.sh is started with setsid nohup, fd 9 (the box lock) and MMS_BOX_LOCK_FD=9: the runner holds
# that same lock from its first act to its end. Exit 0 started; 2 usage; 3 refused.
# SPDX-License-Identifier: Apache-2.0
set -u
cd "$(dirname "${BASH_SOURCE[0]}")/.." || exit 2
END=${1:-}; FIRST=${2:-}
case "$END" in ''|*[!0-9]*) echo "usage: start_e209.sh <last end epoch> <first card command epoch>"; exit 2 ;; esac
case "$FIRST" in ''|*[!0-9]*) echo "usage: start_e209.sh <last end epoch> <first card command epoch>"; exit 2 ;; esac
MAXF=${E209_FIRST_MAX_S:-120}
BOX=$(hostname | cut -d. -f1)
[ "$BOX" = aifoundry2 ] || { echo "REFUSED: this is $BOX, E209's card is on aifoundry2"; exit 3; }
[ -f src/sched/a2c0-E209.json ] || { echo "REFUSED: no schedule src/sched/a2c0-E209.json (run the sync, step 5)"; exit 3; }
NOW=$(date +%s)
[ "$END" -lt $((NOW + 4 * 3600)) ] || { echo "REFUSED: the last end ($END) is more than 4 hours away"; exit 3; }
[ "$END" -gt $((NOW + 600)) ] || { echo "REFUSED: the last end ($END) is less than 10 minutes away"; exit 3; }
[ "$FIRST" -le "$NOW" ] || { echo "REFUSED: the first card command ($FIRST) is in the future"; exit 3; }
[ $((NOW - FIRST)) -le "$MAXF" ] || { echo "REFUSED: the first card command was $((NOW - FIRST)) s ago, more than $MAXF s (step 7 again, on a new folder)"; exit 3; }
FD7=first/$FIRST
[ -d "$FD7" ] || { echo "REFUSED: no step 7 folder $FD7 (the reboot gate's read or look)"; exit 3; }
G=$(/usr/bin/python3 -I -B - "$FD7" "${E209_DESKTEST:-}" <<'PY'
import datetime, glob, json, os, sys
d, desk = sys.argv[1], sys.argv[2] == "1"
bt = int([ln.split()[1] for ln in open("/proc/stat") if ln.startswith("btime ")][0])
bid = open("/proc/sys/kernel/random/boot_id").read().strip()
try:
    from zoneinfo import ZoneInfo
    tz = ZoneInfo("America/Los_Angeles")
except Exception:  # noqa: BLE001
    tz = None
today = datetime.datetime.now(tz).date()
recs, bad, deskrec = [], [], False
for p in sorted(glob.glob(os.path.join(d, "fwgate-*.json"))):
    try:
        r = json.load(open(p))
    except (OSError, ValueError):
        bad.append(f"{os.path.basename(p)} unreadable")
        continue
    if r.get("schema") != "fwgate-read/1" or r.get("box") != "aifoundry2" or r.get("card") != 0:
        bad.append(f"{os.path.basename(p)} not a fwgate read of aifoundry2 card 0")
        continue
    t = r.get("read_epoch")
    why = []
    if r.get("verdict") != "EQUAL":
        why.append(f"verdict {r.get('verdict')}")
    if r.get("boot_epoch") != bt or r.get("boot_id") != bid or not isinstance(t, (int, float)) or t <= bt:
        why.append("not this boot")
    elif datetime.datetime.fromtimestamp(t, tz).date() != today:
        why.append("not today")
    if r.get("desk_test") is not False:
        if desk:
            deskrec = True
        else:
            why.append("a desk test's record")
    (bad if why else recs).append(f"{os.path.basename(p)}" + (f" ({'; '.join(why)})" if why else ""))
look = os.path.join(d, "look.txt")
cont = os.path.exists(look) and open(look).read().startswith("CONTINUITY:")
if bad:
    print("NO " + "; ".join(bad))
elif recs:
    print(("DESKTEST " if deskrec else "") + "READ " + ", ".join(recs))
elif cont:
    print("CONTINUITY look.txt")
else:
    print("NO neither an EQUAL read of this boot nor fwgate's CONTINUITY line")
PY
)
case "$G" in READ*|CONTINUITY*|"DESKTEST READ"*) ;; *) echo "REFUSED: step 7's folder $FD7: ${G:-unreadable}"; exit 3 ;; esac
DESK=""; case "$G" in DESKTEST*) DESK=" DESKTEST" ;; esac
if [ -n "${E209_QUIET_FILE:-}" ]; then
  [ -f "$E209_QUIET_FILE" ] || { echo "REFUSED: THE QUIET DESK FLAG ($E209_QUIET_FILE) is not up"; exit 3; }
  QL=$(head -n 1 "$E209_QUIET_FILE" | cut -d' ' -f1)
  [ -n "${E209_QUIET_LANE:-}" ] && [ "$QL" = "${E209_QUIET_LANE:-}" ] || { echo "REFUSED: THE QUIET DESK FLAG is not this lane's (it reads '$QL')"; exit 3; }
fi
mkdir -p run sessions
exec 9>>run/box.lock    # held from here; handed to the session below
if ! flock -n 9; then echo "REFUSED: run/box.lock is held (a session, a build or a dry pass of this kit runs on this box)"; exit 3; fi
[ -f build/BUILD-mms.json ] || { echo "REFUSED: no build record: run the build (step 6) first"; exit 3; }
/usr/bin/python3 -B src/check_mms.py --box > "run/harness-$NOW.txt" 2>&1 || { echo "REFUSED: the harness differs (run/harness-$NOW.txt)"; exit 3; }
T0=$NOW
SID=$T0-a2c0-E209
mkdir "sessions/$SID" 2> /dev/null || { echo "REFUSED: sessions/$SID exists already (one session a second)"; exit 3; }
cp -p -r "$FD7" "sessions/$SID/first" || { echo "REFUSED: step 7's folder could not be copied into the session"; rmdir "sessions/$SID" 2>/dev/null; exit 3; }
[ -n "$DESK" ] && echo "DESKTEST: a desk test's reboot-gate record (E209_DESKTEST=1); this session is never collected as data" > "sessions/$SID/DESKTEST"
if [ -e run/STOP ]; then mv run/STOP "run/STOP.cleared-$NOW" && echo "a stale run/STOP (no session running) moved to run/STOP.cleared-$NOW"; fi
echo "$SID" > run/current-a2c0
setsid nohup env MMS_BOX_LOCK_FD=9 E209_T0="$T0" E209_DEADLINE="$END" bash src/session_e209.sh \
  > "sessions/$SID.start.out" 2>&1 < /dev/null &
sleep 3
echo "STARTED$DESK $SID (T0 $T0 = $(TZ=America/Los_Angeles date -d "@$T0" '+%F %T %Z'); last end $(TZ=America/Los_Angeles date -d "@$END" '+%T %Z'); first card command $((NOW - FIRST)) s before; the reboot gate: $G)"
[ -f "sessions/$SID/session.log" ] && tail -n 5 "sessions/$SID/session.log"
exit 0
