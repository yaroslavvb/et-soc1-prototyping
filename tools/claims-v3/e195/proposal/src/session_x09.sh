#!/usr/bin/env bash
# x09: the card session, a reference for the lab session's own kit. Run detached on the box from a script file, in the
# tree that holds this src/ at tools/claims-v3/x09/ (beside the lab's lib.sh; block_x09.sh names the rest the tree
# needs) and the generated manifest at build/x09-gen (X9_GEN), after the day's go and inside the window it names:
#
#   X9_ROOT=<the tree> X9_LATEST_START='<date>' X9_DEADLINE='<date>' \
#     setsid nohup bash tools/claims-v3/x09/session_x09.sh > build/x09/session.out 2>&1 < /dev/null &
#
# A port of the public lab repo's tools/claims-v3/e139/session_e139.sh and queue_e139.sh, with the gates of its
# e183/session_e183_v3.sh. Nothing is set on the card.
#  0. Refused before any device opens (exit 8; 3 for the preflight): X9_ROOT must be this tree's absolute path
#     (everything is written under its build/); X9_LATEST_START and X9_DEADLINE (dates) are required, no session
#     starts after the first, and the smoke must fit before the second; USER, when set, must be this login (unset, it
#     is set to it); no stop file (build/x09-STOP, build/claims-v3/STOP) may exist; the device-command preflight
#     (preflight_x09.sh, the lab's dmcmd_audit.py on every file this session runs) must read GO.
#  1. et-who, and the opening `ettelem config` through the lab's E128 guard (read only), only while `et-who --check`
#     reads the card free, under the card lock, timeout 10.
#  2. The board-power watcher (watch_x09.py: telemetry files only). No block starts unless it is running.
#  3. The smoke block and its gate (smoke_gate_x09.py). A failed gate runs no pass.
#  4. The passes, each one block_x09.sh block, the first the registered warm-up. A pass starts only when no stop file
#     exists, the watcher runs, the session has run less than X9_START_CAP_MIN minutes (38), and now + the longest
#     pass so far (X9_PASS_EST_S, 360 s, until one has run) + 60 s for the close is before X9_DEADLINE. A pass in
#     flight is never cut; a pass that fails ends the queue.
#  5. The closing config read (as in 1) and et-who.
# The data land in the tree's build/claims-v3/<card>/x09/; the session's own files in build/x09/.
set -u
HERE=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd -P)
ROOT=$(cd "$HERE/../../.." && pwd -P)
cd "$ROOT" || exit 8
unset V3_DEVICE ET_DEVICES            # one card: the host refuses a host with more
mkdir -p build/x09
LOG=build/x09/session.log
say() { echo "$(date '+%F %T %Z') $*" >> "$LOG"; }
refuse() { say "refused, no device opened: $1"; say "session end"; exit "${2:-8}"; }
num() { case "$2" in ''|*[!0-9]*) refuse "$1 must be a whole number, not '$2'" ;; esac; }
say "session start in $ROOT"
[ -f "$HERE/../lib.sh" ] || refuse "no lib.sh beside $HERE: this src/ must sit at <tree>/tools/claims-v3/x09/"
case "${X9_ROOT:-}" in /*) ;; *) refuse "X9_ROOT='${X9_ROOT:-}' must be the absolute path of this tree ($ROOT)" ;; esac
[ "$(cd "$X9_ROOT" 2>/dev/null && pwd -P)" = "$ROOT" ] || refuse "X9_ROOT='$X9_ROOT' must name this tree ($ROOT)"
export X9_ROOT
ME=$(id -un 2>/dev/null)
[ -n "${USER:-}" ] || export USER="$ME"
[ -n "$ME" ] && [ "$USER" = "$ME" ] || refuse "USER is '$USER', not this login ('$ME'): the holder checks compare with it"
SMOKE=${X9_SMOKE_PASS:-901}; num X9_SMOKE_PASS "$SMOKE"
SMOKE_ITEMS=${X9_SMOKE_ITEMS:-anchor_pi,x9_rd_rnd,x9_wr_u4,x9_wrh_rnd,x9_wrh_nst}
PASSES=${X9_PASSES:-910 911 912 913 914 915 916 917}
for p in $PASSES; do num X9_PASSES "$p"; done
CAP_MIN=${X9_START_CAP_MIN:-38}; num X9_START_CAP_MIN "$CAP_MIN"
longest=${X9_PASS_EST_S:-360}; num X9_PASS_EST_S "$longest"
SMOKE_S=${X9_SMOKE_EST_S:-150}; num X9_SMOKE_EST_S "$SMOKE_S"
CLOSE_S=60
[ -n "${X9_LATEST_START:-}" ] && [ -n "${X9_DEADLINE:-}" ] ||
  refuse "X9_LATEST_START and X9_DEADLINE are required: the window of the day's go"
latest=$(date -d "$X9_LATEST_START" +%s 2>/dev/null) || refuse "X9_LATEST_START '$X9_LATEST_START' is not a date"
deadline=$(date -d "$X9_DEADLINE" +%s 2>/dev/null) || refuse "X9_DEADLINE '$X9_DEADLINE' is not a date"
t_start=$(date +%s)
[ "$t_start" -le "$latest" ] || refuse "no session starts after $(date -d @"$latest" '+%F %T %Z')"
[ $((t_start + SMOKE_S + CLOSE_S)) -le "$deadline" ] ||
  refuse "the smoke ($SMOKE_S s) and the close would end after the deadline $(date -d @"$deadline" '+%F %T %Z')"
for f in build/x09-STOP build/claims-v3/STOP; do [ -e "$f" ] && refuse "$f exists"; done
EXPN=${X9_EXPN:-x09}; export X9_EXPN=$EXPN
DATA=build/claims-v3/$(hostname)/$EXPN
export X9_GEN=${X9_GEN:-$ROOT/build/x09-gen} X9_MAX_C=${X9_MAX_C:-70}
P=build/x09/dmcmd-preflight.txt
bash "$HERE/preflight_x09.sh" > "$P" 2>&1; a=$?
say "device-command preflight rc=$a: $(grep -m1 '^dmcmd_audit:' "$P")"
[ "$a" -eq 0 ] || refuse "the device-command preflight is not GO ($P)" 3
rm -f build/x09/session-end.time
say "passes $PASSES (the first the warm-up); no pass starts after $CAP_MIN min or past $(date -d @"$deadline" '+%F %T %Z')"
cfg() {
  if ! timeout 20 et-who --check > /dev/null 2>&1; then
    say "config $(basename "$1"): not read (et-who --check does not read the card free)"; return 0
  fi
  flock -n /run/lock/etsoc-shire0.lock timeout 10 bash tools/claims-v3/e128/ettelem_guard.sh config < /dev/null 2> "$1.err" |
    grep '^{' | tail -1 > "$1"
  say "config $(basename "$1"): $(head -c 300 "$1")"
}
timeout 20 et-who >> "$LOG" 2>&1
cfg build/x09/config-session-start.json
python3 "$HERE/watch_x09.py" --root "$DATA" --stop-w 70 --n 3 --session-stop build/x09-STOP \
  --end-flag build/x09/session-end.time --max-s $((deadline - t_start + 600)) >> build/x09/watch.log 2>&1 &
WPID=$!
watching() { kill -0 "$WPID" 2>/dev/null; }
sleep 2
if ! watching; then
  say "the board-power watcher did not start: no block runs"
else
  bash "$HERE/block_x09.sh" "$SMOKE" "$SMOKE_ITEMS" < /dev/null > build/x09/smoke.log 2>&1; rc=$?
  say "smoke rc=$rc"
  python3 "$HERE/smoke_gate_x09.py" "$DATA/p$SMOKE" "$SMOKE_ITEMS" >> "$LOG" 2>&1; g=$?
  if [ "$rc" -ne 0 ] || [ "$g" -ne 0 ] || [ -e build/x09-STOP ]; then
    say "smoke gate failed or a stop is set (block rc $rc, gate $g): no pass runs"
  else
    say "smoke gate passed: the passes start"
    for p in $PASSES; do
      stop=
      for f in build/x09-STOP build/claims-v3/STOP; do [ -e "$f" ] && stop=$f; done
      if [ -n "$stop" ]; then say "$stop exists: stopping before p$p"; break; fi
      if ! watching; then say "the board-power watcher is not running: stopping before p$p"; break; fi
      now=$(date +%s)
      el=$(( (now - t_start) / 60 ))
      if [ "$el" -ge "$CAP_MIN" ]; then say "$el min into the session: no pass starts after $CAP_MIN (before p$p)"; break; fi
      if [ $((now + longest + CLOSE_S)) -gt "$deadline" ]; then
        say "deadline: p$p would end after $(date -d @"$deadline" '+%T %Z') (longest pass $longest s + $CLOSE_S s)"; break
      fi
      t0=$(date +%s)
      bash "$HERE/block_x09.sh" "$p" < /dev/null >> build/x09/passes.log 2>&1; rc=$?
      d=$(( $(date +%s) - t0 ))
      [ "$d" -gt "$longest" ] && longest=$d
      say "p$p rc=$rc ($d s)"
      if [ "$rc" -ne 0 ]; then say "stopping after p$p (rc $rc)"; break; fi
      sleep 15
    done
  fi
fi
cfg build/x09/config-session-end.json
date --iso-8601=seconds > build/x09/session-end.time
sleep 2; kill "$WPID" 2>/dev/null
timeout 20 et-who >> "$LOG" 2>&1
say "session end ($(( ($(date +%s) - t_start) / 60 )) min)"
