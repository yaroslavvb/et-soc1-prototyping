#!/bin/bash
# v31-trace (Q217): send one of this lane's remote scripts to aifoundry3 (ssh ... bash -s < script), or copy the payload there, ONLY while no
# lane books aifoundry3 (bash W/book.sh show read just before) and no claim file stands for it; for a simulator run (r_trace.sh) also only when
# queue_state.py reads QUEUE OVER for e213a (THE SIMULATOR's rule and this lane's text). kit-e211's a3_send.sh form. Nothing here sends a
# signal to any process; the remote scripts bound themselves with a plain timeout.
#   bash a3_send.sh script <remote script> [args...]
#   bash a3_send.sh payload <payload.tgz>
set -u
W=<W>
mode=$1; shift
bk=$(bash "$W/book.sh" show 2>&1)
if printf '%s\n' "$bk" | grep -q '^aifoundry3'; then echo "BOOKED: aifoundry3 is booked, nothing sent: $(printf '%s\n' "$bk" | grep '^aifoundry3' | head -2)"; exit 9; fi
if printf '%s\n' "$bk" | grep -qi 'aifoundry3'; then echo "BOOKED?: book.sh show names aifoundry3, nothing sent: $(printf '%s' "$bk" | tr '\n' ';' | cut -c1-200)"; exit 9; fi
[ -e "$W/out/orch/claim-aifoundry3.txt" ] && { echo "CLAIMED: out/orch/claim-aifoundry3.txt exists, nothing sent"; exit 9; }
echo "book.sh show at $(TZ=America/Los_Angeles date '+%T %Z'): no booking of aifoundry3 ($(printf '%s' "$bk" | tr '\n' ';' | cut -c1-120))"
case "$mode" in
  payload)
    f=$1
    ssh -o BatchMode=yes -o ConnectTimeout=10 aifoundry3 mkdir -p claude/work || exit 3
    scp -o BatchMode=yes -o ConnectTimeout=10 -q "$f" aifoundry3:claude/work/ || exit 3
    echo "copied $(basename "$f") at $(TZ=America/Los_Angeles date '+%T %Z')"
    ;;
  script)
    f=$1; shift
    [ -f "$f" ] || { echo "no script $f"; exit 2; }
    if [ "$(basename "$f")" = r_trace.sh ]; then
      q=$(python3 "$W/out/orch/queue_state.py" aifoundry3 e213a 2>&1); qrc=$?
      [ "$qrc" = 0 ] || { echo "QUEUE NOT OVER (rc $qrc): no simulator run: $(printf '%s' "$q" | tr '\n' ';' | cut -c1-200)"; exit 9; }
      echo "queue_state aifoundry3 e213a: $(printf '%s' "$q" | tail -1)"
    fi
    ssh -o BatchMode=yes -o ConnectTimeout=10 aifoundry3 bash -s -- "$@" < "$f"
    rc=$?
    echo "remote rc=$rc at $(TZ=America/Los_Angeles date '+%T %Z')"
    exit $rc
    ;;
  *) echo "mode must be script or payload"; exit 2 ;;
esac
