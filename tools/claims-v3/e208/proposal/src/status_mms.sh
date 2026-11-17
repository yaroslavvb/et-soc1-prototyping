#!/usr/bin/env bash
# 1116-mmsweep: how a card's session stands (read-only; opens no device).
#   bash ~/claude/work/ee-1116-mmsweep/src/status_mms.sh <card> [<session id>]
# Prints the session's id, whether it runs, its progress (status.json: card-minutes, runs done of planned, the last run, the
# last sample's board, die and clock), any stop, and the last lines of its log.
# Exit 0 ended (MANIFEST.sha256 written); 17 still running (no runner.rc yet and run/box.lock held: a session holds it from
# its start's checks to its end); 14 gone (no runner left and no manifest: read session.log); 10 no such session.
# SPDX-License-Identifier: Apache-2.0
set -u
cd "$(dirname "${BASH_SOURCE[0]}")/.." || exit 2
CARD=${1:-}
case "$CARD" in a2c0|a1c1|a1c0) ;; *) echo "usage: status_mms.sh a2c0|a1c1|a1c0 [<session id>]"; exit 2 ;; esac
SID=${2:-$(cat "run/current-$CARD" 2>/dev/null)}
D=sessions/$SID
[ -n "$SID" ] && [ -d "$D" ] || { echo "NO SESSION ${SID:-<none>} for $CARD"; exit 10; }
echo "session $SID on $(hostname | cut -d. -f1), $(TZ=America/Los_Angeles date '+%F %T %Z')"
if [ -f "$D/status.json" ]; then
  python3 -B - "$D/status.json" <<'PY'
import json, sys
s = json.load(open(sys.argv[1]))
lr = s.get("last_run") or {}
ls = s.get("last_sample") or {}
print(f"card-minutes {s.get('card_min')}; runs {s.get('runs_done')} of {s.get('runs_total')} done ({s.get('runs_ran')} ran); "
      f"rest die {s.get('rest_die_c')} C; stop {s.get('stop')}")
print(f"last run: {lr.get('i')} {lr.get('arm')} ran {lr.get('ran')} rc {lr.get('rc')} check {lr.get('check')} {lr.get('why') or ''}")
print(f"last sample: board {ls.get('board_w')} W, die {ls.get('die_c')} C, minion {ls.get('minion_mhz')} MHz")
if s.get("closing"):
    print(f"closing: {s.get('closing')}")
lo = s.get("leftover")
if lo:
    if isinstance(lo, dict):
        print(f"LEFTOVER: {len(lo.get('records') or [])} record(s); still alive at the release {lo.get('still_alive_at_release')}; "
              f"resolved {lo.get('resolved')}: do not post the release; tell the owner (never kill -9)")
    else:
        print(f"LEFTOVER: {len(lo)} record(s) so far: the session holds the card's lock until they are gone (at most 10 min)")
PY
fi
[ -f "$D/session.log" ] && tail -n 8 "$D/session.log"
if [ -f "$D/MANIFEST.sha256" ]; then
  RC=$(cat "$D/runner.rc" 2>/dev/null || echo '?')
  echo "ENDED: runner rc $RC, MANIFEST.sha256 $(wc -l < "$D/MANIFEST.sha256") files"
  [ "$RC" = 16 ] && echo "rc 16: a gate refused before any run (see the log above): nothing was measured"
  exit 0
fi
if [ ! -f "$D/runner.rc" ] && ! flock -n run/box.lock true; then echo "RUNNING"; exit 17; fi
echo "GONE: the session's runner is not running (runner.rc written, or run/box.lock free) and no manifest is written (read $D/session.log and $D/runner.out)"
exit 14
