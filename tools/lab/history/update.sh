#!/usr/bin/env bash
# update.sh: gather the live collectors' records from the three machines, build the history page, deploy it.
#   update.sh run      what cron runs (every 15 minutes on aifoundry2, "6-59/15"; every 5 until 8 Oct 2026, which spent about
#                      288 of the account's 400 deploys a day; the page draws the live streams while it is open, so a
#                      reader sees new readings between deploys): quiet, logs to ~/.cache/lab-history/update.log
#   update.sh now      the same, printing what it does
# Records: ~/live/history/*.jsonl on each machine (tools/lab/live/live-collector.py); copies in ~/.cache/lab-history/rec/<host>/.
# A machine that does not answer keeps its last copy; the page shows when each machine last recorded.
# The space is public (all AI Foundry pages are, the owner's rule); its uuid is in ~/.cache/lab-history/space.
set -u
# run and now are the only modes. Anything else stops here, before the lock, the rsync, the build and the deploy:
# until 14 Oct 2026 an unknown argument fell through to MODE=<that word> and did the whole run, so a mistyped
# "update.sh status" published the page.
MODE=${1:-run}
if [ "$#" -gt 1 ] || { [ "$MODE" != run ] && [ "$MODE" != now ]; }; then
  { echo "usage: update.sh [run|now]"
    echo "  run   what cron runs (the default): quiet, logs to ~/.cache/lab-history/update.log"
    echo "  now   the same, printing what it does"
  } >&2
  exit 2
fi
export PATH="$HOME/.local/bin:$HOME/.local/node/bin:/usr/local/bin:/usr/bin:/bin"
HERE=$(cd "$(dirname "$0")" && pwd)
C=$HOME/.cache/lab-history; mkdir -p "$C/rec" "$C/page"
LOG=$C/update.log
exec 9>"$C/lock"; flock -n 9 || exit 0
say() { [ "$MODE" = now ] && echo "$*"; }
t0=$(date +%s); got=()
for h in aifoundry1 aifoundry2 aifoundry3; do
  mkdir -p "$C/rec/$h"
  if [ "$h" = "$(hostname)" ]; then src="$HOME/live/history/"; else src="$h:live/history/"; fi
  if timeout 60 rsync -a --delete -e "ssh -o BatchMode=yes -o ConnectTimeout=10" "$src" "$C/rec/$h/" 2>"$C/rsync-$h.err"; then got+=("$h"); say "$h: records copied"
  else say "$h: no answer ($(tail -1 "$C/rsync-$h.err"))"; fi
done
python3 "$HERE/build.py" "$C/rec" "$C/page/index.html" --dash "$HOME/.cache/lab-dashboard/data.json" > "$C/build.log" 2>&1 || { echo "$(date -Is) build failed: $(tail -1 "$C/build.log")" >> "$LOG"; exit 0; }
say "$(cat "$C/build.log")"
uuid=$(cat "$C/space" 2>/dev/null)
if [ -z "$uuid" ]; then dep="skipped (no space yet: put the space's uuid in $C/space)"
else
  if timeout 120 spacesheep deploy "$C/page" --space "$uuid" -m "history $(date '+%H:%M')" > "$C/deploy.log" 2>&1; then dep=ok; else dep="FAILED: $(tail -1 "$C/deploy.log")"; fi
  rm -f "$C/page/.spacesheep.json"
fi
echo "$(date -Is) took=$(( $(date +%s) - t0 ))s hosts=${#got[@]}/3 (${got[*]}) deploy=$dep" >> "$LOG"
say "deploy: $dep"
