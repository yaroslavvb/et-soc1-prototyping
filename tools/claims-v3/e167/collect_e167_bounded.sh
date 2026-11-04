#!/bin/bash
# E167 (Q141(h), the fix pass): collect_e167.sh with every rsync and ssh call bounded (E167.md.dated-note-2.md and README.md.dated-note.md).
# collect_e167.sh (unchanged, committed in 4f4e7620) runs rsync and ssh with no timeout, as collect_e161.sh did; a Tailscale check on the
# boxes would hold such a call until a person answers it. Here each call runs under `timeout` (E167_RSYNC_TIMEOUT_S, default 900 s, for
# the runs directory; E167_SMALL_TIMEOUT_S, default 120 s, for each small file and each box's history), its stderr is watched once a
# second, and a login.tailscale.com line stops the call and the collection at once with exit 7 (the line goes to the terminal's stderr,
# never into the data directory). Otherwise it does exactly what collect_e167.sh does: read-only on the boxes; the copy of the day's session
# from aifoundry2; E111's login scrub; gzip of the telemetry, the launches and the C logs; the three boxes' own 5 s history over the
# session, numbers only (E98's thin_history.py). Run from the Intel, at the top of the lab clone:
#     bash tools/claims-v3/e167/collect_e167_bounded.sh <data dir> <from epoch s> <to epoch s> [<runs dir on the box, default build/e167/runs>]
# Exit: 0 done; 3 the runs directory's copy failed or timed out; 4 a login is still in a file; 7 a Tailscale check is needed.
set -u
DST="${1:?data dir}"; A="${2:?from}"; B="${3:?to}"; RUNS="${4:-build/e167/runs}"
TB=${E167_RSYNC_TIMEOUT_S:-900}; TS=${E167_SMALL_TIMEOUT_S:-120}
SSH="ssh -o BatchMode=yes -o ConnectTimeout=10"
REMOTE="claude/et-soc1-prototyping/$RUNS"
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ERR=$(mktemp -t collect-e167.XXXXXX)   # the user's temp directory (TMPDIR), never the data directory
trap 'rm -f "${ERR:?}"' EXIT
tailscale_stop() {   # $1 = what was called
  echo "TAILSCALE CHECK NEEDED ($1): $(grep -m1 -o 'https://login.tailscale.com[^ ]*' "$ERR")" >&2
  exit 7
}
bounded() {   # bounded <seconds> <what> <command...>: the command under timeout; stdout passes through; a Tailscale link stops it at once
  local t=$1 what=$2 pid rc; shift 2
  : > "$ERR"
  timeout "$t" "$@" 2> "$ERR" &
  pid=$!
  while kill -0 "$pid" 2>/dev/null; do
    if grep -q 'login.tailscale.com' "$ERR" 2>/dev/null; then kill -TERM "$pid" 2>/dev/null; wait "$pid" 2>/dev/null; tailscale_stop "$what"; fi
    sleep 1
  done
  wait "$pid"; rc=$?
  grep -q 'login.tailscale.com' "$ERR" 2>/dev/null && tailscale_stop "$what"
  return "$rc"
}
mkdir -p "$DST/history"
bounded "$TB" "rsync of $REMOTE" rsync -a -e "$SSH" --exclude='STOP' "aifoundry2:$REMOTE/" "$DST/"; rc=$?
[ "$rc" -eq 0 ] || { echo "the runs directory's copy failed (rc $rc$( [ "$rc" -eq 124 ] && echo ": timed out after $TB s")): $(tail -c 300 "$ERR")"; exit 3; }
bounded "$TS" "rsync of schedule.json and queue.out" rsync -a -e "$SSH" "aifoundry2:$(dirname "$REMOTE")/schedule.json" \
  "aifoundry2:$(dirname "$REMOTE")/queue.out" "$DST/" || echo "schedule.json / queue.out: not copied (rc $?)"
python3 "$HERE/../e111/scrub_logins_e111.py" "$DST" || { echo "a login is still in a file: stop"; exit 4; }
for f in "$DST"/*/tel/*.jsonl "$DST"/*/launches.jsonl "$DST"/*/c-log.jsonl; do [ -f "$f" ] && gzip -9 -n -f "$f"; done
for box in aifoundry1 aifoundry2 aifoundry3; do
  for day in $(python3 "$HERE/../e133/utc_days_e133.py" "$A" "$B"); do
    bounded "$TS" "ssh $box cat history $day" $SSH "$box" "cat ~/live/history/$day.jsonl" > "$DST/history/$box.raw"; rc=$?
    if [ "$rc" -ne 0 ]; then rm -f "${DST:?}/history/$box.raw"; echo "history $box $day: not read (rc $rc)"; continue; fi
    python3 "$HERE/../kspeed/e98/thin_history.py" "$DST/history/$box.raw" "$A" "$B" | gzip -9 -n > "$DST/history/$box-$day.jsonl.gz"
    rm -f "${DST:?}/history/$box.raw"
  done
done
du -sh "$DST"/* | tail -30
