#!/bin/bash
# verify-v31trace (Q217): every ssh/scp to aifoundry3 goes through here. ONLY while no lane books aifoundry3 ('bash W/book.sh show' read
# just before) and no claim file stands for it; for the one simulator run (mode 'run') also only while queue_state.py reads QUEUE OVER for
# e213a (THE SIMULATOR rule; this lane's text). Nothing here sends a signal to any process.
#   bash a3.sh look <remote script>            (read-only remote script, ssh bash -s)
#   bash a3.sh put <local file> <remote dir>   (scp into this lane's own remote folder)
#   bash a3.sh run <remote script> [args]      (the simulator run)
#   bash a3.sh get <remote path> <local dir>   (scp back)
set -u
W=<W>
mode=$1; shift
bk=$(bash "$W/book.sh" show 2>&1)
if printf '%s\n' "$bk" | grep -qi 'aifoundry3'; then echo "BOOKED: book.sh show names aifoundry3, nothing sent: $(printf '%s' "$bk" | tr '\n' ';' | cut -c1-200)"; exit 9; fi
[ -e "$W/out/orch/claim-aifoundry3.txt" ] && { echo "CLAIMED: out/orch/claim-aifoundry3.txt exists, nothing sent"; exit 9; }
echo "book.sh show at $(TZ=America/Los_Angeles date '+%T %Z'): no booking of aifoundry3 ($(printf '%s' "$bk" | tr '\n' ';' | cut -c1-80)); no claim file"
SSH="ssh -o BatchMode=yes -o ConnectTimeout=10"
SCP="scp -o BatchMode=yes -o ConnectTimeout=10 -q"
case "$mode" in
  look)
    $SSH aifoundry3 bash -s < "$1"; rc=$?; echo "remote rc=$rc at $(TZ=America/Los_Angeles date '+%T %Z')"; exit $rc ;;
  put)
    case "$2" in claude/work/q217-verify-v31trace*) ;; *) echo "put only into claude/work/q217-verify-v31trace"; exit 2 ;; esac
    $SCP "$1" "aifoundry3:$2/" || exit 3; echo "put $(basename "$1") -> $2 at $(TZ=America/Los_Angeles date '+%T %Z')" ;;
  run)
    q=$(python3 "$W/out/orch/queue_state.py" aifoundry3 e213a 2>&1); qrc=$?
    [ "$qrc" = 0 ] || { echo "QUEUE NOT OVER (rc $qrc): no simulator run: $(printf '%s' "$q" | tr '\n' ';' | cut -c1-200)"; exit 9; }
    echo "queue_state aifoundry3 e213a: $(printf '%s' "$q" | tail -1) at $(TZ=America/Los_Angeles date '+%T %Z')"
    f=$1; shift
    $SSH aifoundry3 bash -s -- "$@" < "$f"; rc=$?; echo "remote rc=$rc at $(TZ=America/Los_Angeles date '+%T %Z')"; exit $rc ;;
  get)
    case "$1" in claude/work/q217-verify-v31trace/*) ;; *) echo "get only from claude/work/q217-verify-v31trace"; exit 2 ;; esac
    $SCP "aifoundry3:$1" "$2/" || exit 3; echo "got $1 at $(TZ=America/Los_Angeles date '+%T %Z')" ;;
  *) echo "mode: look | put | run | get"; exit 2 ;;
esac
