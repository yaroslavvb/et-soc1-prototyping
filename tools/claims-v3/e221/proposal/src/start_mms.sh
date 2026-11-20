#!/usr/bin/env bash
# 1120-mmsweep6: start one card's session detached on its box and return at once (the operator runs it through the relay).
#   bash ~/claude/work/ee-1120-mmsweep6/src/start_mms.sh <card> <S1..S9> <last end: epoch seconds, or HH:MM PST (its next
#   occurrence: today's, or tomorrow's when today's has passed)>
# It takes the kit's box lock run/box.lock first (flock -n on fd 9; refused while a session, a build or a dry pass of the kit
# holds it: so never two of ours on aifoundry1) and keeps it through its checks: the box is the card's; the build record is
# present (the runner checks it is today's); every src/ file is at its sha256 (src/check_mms.py --box). Then the session's
# folder sessions/<T0>-<card>-<S> is made (refused if it exists); a stale run/STOP (no session can be running: the lock is ours)
# is moved aside to run/STOP.cleared-<epoch> and said so; run/current-<card> names the session; and session_mms.sh is started
# with setsid nohup, its output in sessions/<T0>-<card>-<S>.start.out, with fd 9 and MMS_BOX_LOCK_FD=9: the runner holds that
# same lock from its first act to its end, so the lock is never free between these checks and the session's end.
# Exit 0 started; 2 usage; 3 refused (the reason printed).
# SPDX-License-Identifier: Apache-2.0
set -u
cd "$(dirname "${BASH_SOURCE[0]}")/.." || exit 2
CARD=${1:-}; S=${2:-}; END=${3:-}
case "$CARD" in a2c0) WANT=aifoundry2 ;; a1c1|a1c0) WANT=aifoundry1 ;; *) echo "usage: start_mms.sh a2c0|a1c1|a1c0 S1..S9 <last end>"; exit 2 ;; esac
case "$S" in S[1-9]) ;; *) echo "usage: start_mms.sh <card> S1..S9 <last end>"; exit 2 ;; esac
[ -f "src/sched/$CARD-$S.json" ] || { echo "REFUSED: no schedule src/sched/$CARD-$S.json"; exit 3; }
BOX=$(hostname | cut -d. -f1)
[ "$BOX" = "$WANT" ] || { echo "REFUSED: this is $BOX, card $CARD is on $WANT"; exit 3; }
case "$END" in
  '') echo "REFUSED: give the window's last end (epoch seconds, or HH:MM PST today)"; exit 3 ;;
  *:*) DL=$(TZ=America/Los_Angeles date -d "today $END" +%s 2>/dev/null) || { echo "REFUSED: cannot read '$END'"; exit 3; }
        if [ "$DL" -le "$(date +%s)" ]; then DL=$(TZ=America/Los_Angeles date -d "tomorrow $END" +%s); fi ;;
  *[!0-9]*) echo "REFUSED: cannot read '$END' (epoch seconds, or HH:MM PST)"; exit 3 ;;
  *) DL=$END ;;
esac
NOW=$(date +%s)
[ "$DL" -lt $((NOW + 4 * 3600)) ] 2>/dev/null || { echo "REFUSED: the last end ($DL) is more than 4 hours away: give it as epoch seconds if meant"; exit 3; }
[ "$DL" -gt $((NOW + 600)) ] 2>/dev/null || { echo "REFUSED: the last end ($DL) is less than 10 minutes away"; exit 3; }
mkdir -p run sessions
exec 9>>run/box.lock    # held from here; handed to the session below
if ! flock -n 9; then echo "REFUSED: run/box.lock is held (a session, a build or a dry pass of this kit runs on this box)"; exit 3; fi
[ -f build/BUILD-mms.json ] || { echo "REFUSED: no build record: run src/build_mms.sh first"; exit 3; }
python3 -B src/check_mms.py --box > "run/harness-$NOW.txt" 2>&1 || { echo "REFUSED: the harness differs (run/harness-$NOW.txt)"; exit 3; }
T0=$NOW
SID=$T0-$CARD-$S
mkdir "sessions/$SID" 2> /dev/null || { echo "REFUSED: sessions/$SID exists already (one session a second)"; exit 3; }
if [ -e run/STOP ]; then mv run/STOP "run/STOP.cleared-$NOW" && echo "a stale run/STOP (no session running) moved to run/STOP.cleared-$NOW"; fi
echo "$SID" > "run/current-$CARD"
setsid nohup env MMS_CARD="$CARD" MMS_SESSION="$S" MMS_T0="$T0" MMS_DEADLINE="$DL" MMS_BOX_LOCK_FD=9 bash src/session_mms.sh \
  > "sessions/$SID.start.out" 2>&1 < /dev/null &
sleep 3
echo "STARTED $SID (T0 $T0 = $(TZ=America/Los_Angeles date -d "@$T0" '+%F %T %Z'); last end $(TZ=America/Los_Angeles date -d "@$DL" '+%T %Z'))"
[ -f "sessions/$SID/session.log" ] && tail -n 5 "sessions/$SID/session.log"
exit 0
