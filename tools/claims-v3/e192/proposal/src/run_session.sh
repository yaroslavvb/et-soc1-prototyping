#!/usr/bin/env bash
# A session of intbits on one card: a holder check first (nothing is opened while anyone else holds the card), then one
# sampler for the whole session (stopped with SIGTERM only, always, by the EXIT trap), the live stops (stopwatch.py), a
# smoke block, then the passes, each under the card lock; between passes the lock is released, a gap is left, and the
# holder check is repeated before the lock is taken again. The first measured pass is a warm-up, recorded and set aside
# by the reducer.
#
#   run_session.sh OUT [PASSES]
# Environment:
#   SAMPLER   ettelem (default): "$ETTELEM sample --seconds T --every-ms 100"
#             pvt: "python3 -B $PVT_SAMPLE --seconds T --every-ms 100" (the lab's per-sensor sampler, same keys plus
#             the raw per-sensor temperature codes; on the card that answers it only)
#   HEATER    the lab's heater host (preheat before every run, as in the lab's E78 kit); unset: no preheat
#   TARGET, PREHEAT  launch reading and preheat reading (default 58 and 59)
#   ET_DEVICES  the card to use on a host with more than one card (one index); unset: the host must have one card
#   LOCK      the card's lock file (default /run/lock/etsoc-shire${ET_DEVICES:-0}.lock); it must exist (the host
#             creates one per card at boot); it is opened read-only and never created, as the lab's tools do
#   GAP       seconds between passes with the lock released (default 30)
#   SAMPLER_S the sampler's own time bound in seconds (default PASSES x 600 + 600)
#   H         the intbits host binary (default ./build/host/intbits_host)
#   DRY=1     print every device call, open nothing (no sampler, no lock, no holder check)
# Stop by hand: touch OUT/STOP (the launch in flight finishes first). Detach it from a script file, as the lab's
# kits do. Exit codes: 0 done; 3 the card is held or not free (nothing was opened, or the session stopped between
# passes); 2 a refused setting; other: the block's own exit code.
set -u
out=${1:?out dir}; passes=${2:-9}
here=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
DEV=${ET_DEVICES:-0}
LOCK=${LOCK:-/run/lock/etsoc-shire$DEV.lock}
SAMPLER=${SAMPLER:-ettelem}
TARGET=${TARGET:-58}; PREHEAT=${PREHEAT:-59}
GAP=${GAP:-30}
H=${H:-$here/build/host/intbits_host}
export H
mkdir -p "$out"
TEL="$out/telemetry.jsonl"
blk=(python3 -B "$here/run_block.py" "$out" --tel "$TEL" --target "$TARGET" --preheat "$PREHEAT")
[ -n "${HEATER:-}" ] && blk+=(--heater "$HEATER")
say() { echo "[$(date +%H:%M:%S)] $*" | tee -a "$out/session.log"; }

if [ -n "${DRY:-}" ]; then
  say "DRY: holder check (et-who --check, other users' device processes), card lock probe ($LOCK), device nodes"
  say "DRY: sampler ($SAMPLER) for at most ${SAMPLER_S:-$((passes * 600 + 600))} s, stopwatch"
  "${blk[@]}" -1 --smoke --dry
  for p in $(seq 0 $((passes - 1))); do
    [ "$p" -gt 0 ] && say "DRY: card lock released; gap $GAP s; holder check; card lock taken"
    "${blk[@]}" "$p" --dry
  done
  exit 0
fi

# --- One card only: count the device nodes before anything opens one. ---
nodes=$(ls /dev/et*_ops 2>/dev/null | wc -l)
if [ "$nodes" -eq 0 ]; then say "refused: no /dev/et*_ops node on this host"; exit 2; fi
if [ -n "${ET_DEVICES:-}" ]; then
  case "$ET_DEVICES" in *[!0-9]*) say "refused: ET_DEVICES must be one card index"; exit 2 ;; esac
  [ -c "/dev/et${ET_DEVICES}_ops" ] || { say "refused: no /dev/et${ET_DEVICES}_ops"; exit 2; }
  export ET_DEVICES
fi
if [ "$nodes" -gt 1 ]; then
  [ -n "${ET_DEVICES:-}" ] || { say "refused: $nodes cards on this host and ET_DEVICES unset"; exit 2; }
  # As the lab's kits check: a binary built against a device layer that ignores the selection opens every card.
  for f in "$H" "${ETTELEM:-}" "${HEATER:-}"; do
    [ -n "$f" ] || continue
    grep -aqw ET_DEVICES "$f" || { say "refused: $f does not honour ET_DEVICES: it would open every card"; exit 2; }
  done
fi
[ -e "$LOCK" ] || { say "refused: no card lock file $LOCK"; exit 2; }

# --- The holder check: before the sampler, and again before every pass. ---
DEV_COMM='_host$|^ettelem$|^dev_mngt_servi|^et-powertop$|^mmbench_launch|^sys_emu$|^Runner.Worker$'
others_procs() {  # another user's device process (or a CI job) running
  ps -eo uid=,pid=,comm= | awk -v me="$(id -u)" -v re="$DEV_COMM" '$1 != me && $3 ~ re {print $1":"$2":"$3}' | tr '\n' ' '
}
# free_before_sampler: nothing held at all (et-who --check exit 0), no other user's device process, and the card lock
# free on a probe. Returns 0 when free.
free_before_sampler() {
  local o rc p
  o=$(et-who --check 2>&1); rc=$?
  case $rc in
    0) ;;
    1) say "held: $(echo "$o" | grep -E '^(/dev/et|lock:)' | tr -s ' ' | tr '\n' ';')"; return 1 ;;
    *) say "et-who --check failed (exit $rc)"; return 1 ;;
  esac
  p=$(others_procs); [ -z "${p// /}" ] || { say "another user's device process: $p"; return 1; }
  exec 9< "$LOCK"
  flock -n -E 75 9; rc=$?
  flock -u 9 2>/dev/null; exec 9<&-
  [ "$rc" -eq 0 ] || { say "card lock $LOCK held by another process (probe exit $rc)"; return 1; }
  return 0
}
# free_with_sampler: while our sampler runs, et-who --check counts it as a holder, so the holder lines are read: every
# line must be our own sampler (its pid) on one of this card's nodes; and no other user's device process.
free_with_sampler() {
  local o rc bad p
  o=$(et-who --check 2>&1); rc=$?
  case $rc in
    0) ;;
    1) bad=$(echo "$o" | grep -E '^(/dev/et|lock:)' |
             awk -v me="$(id -un)" -v pid="$S" -v node="/dev/et${DEV}_" '!(index($1, node) == 1 && $2 == me && $3 == pid)' |
             tr -s ' ' | tr '\n' ';')
       [ -z "$bad" ] || { say "held: $bad"; return 1; } ;;
    *) say "et-who --check failed (exit $rc)"; return 1 ;;
  esac
  p=$(others_procs); [ -z "${p// /}" ] || { say "another user's device process: $p"; return 1; }
  return 0
}
# A block under the card lock: the lock file opened read-only (never created) on fd 9, taken with flock -n (never
# waited for), released when the block ends. Exit 75: the lock was busy, nothing ran.
locked_block() {
  local rc
  exec 9< "$LOCK"
  if ! flock -n -E 75 9; then exec 9<&-; return 75; fi
  "${blk[@]}" "$@"; rc=$?
  flock -u 9; exec 9<&-
  return $rc
}

free_before_sampler || { say "the card is not free: nothing opened"; exit 3; }

secs=${SAMPLER_S:-$((passes * 600 + 600))}   # a bound on the sampler's own life; SIGTERM ends it at the session's end
S=; W=
finish() {
  touch "$out/SESSION_DONE"
  if [ -n "$S" ]; then kill -TERM "$S" 2>/dev/null; wait "$S" 2>/dev/null; fi
  if [ -n "$W" ]; then wait "$W" 2>/dev/null; fi
}
trap finish EXIT
trap 'exit 130' INT TERM HUP
case "$SAMPLER" in
  pvt) : "${PVT_SAMPLE:?set PVT_SAMPLE to the lab per-sensor sampler}"
       python3 -B "$PVT_SAMPLE" --seconds "$secs" --every-ms 100 > "$TEL" 2> "$out/sampler.err" < /dev/null & ;;
  *)   : "${ETTELEM:?set ETTELEM to the sampler binary}"
       "$ETTELEM" sample --seconds "$secs" --every-ms 100 > "$TEL" 2> "$out/sampler.err" < /dev/null & ;;
esac
S=$!
python3 -B "$here/stopwatch.py" "$TEL" "$out" 2>> "$out/stopwatch.err" < /dev/null &
W=$!
sleep 10
rc=0
if ! free_with_sampler; then
  say "the card is not free after the sampler started: no block runs"; rc=3
else
  locked_block -1 --smoke; rc=$?
  [ "$rc" -eq 0 ] || say "smoke: exit $rc ($([ "$rc" -eq 75 ] && echo 'card lock busy' || echo 'block stopped')), no pass runs"
fi
if [ "$rc" -eq 0 ]; then
  for p in $(seq 0 $((passes - 1))); do
    [ -e "$out/STOP" ] && { say "STOP: $(cat "$out/STOP")"; break; }
    if [ "$p" -gt 0 ]; then
      sleep "$GAP"   # the lock is free for this long: anyone else may take the card
      [ -e "$out/STOP" ] && { say "STOP: $(cat "$out/STOP")"; break; }
    fi
    free_with_sampler || { say "pass $p: the card is not free, stopping"; rc=3; break; }
    locked_block "$p"; rc=$?
    if [ "$rc" -ne 0 ]; then
      say "pass $p: exit $rc ($([ "$rc" -eq 75 ] && echo 'card lock busy' || echo 'block stopped')), stopping"; break
    fi
  done
fi
sleep 8
say "session done (rc $rc): $(wc -l < "$out/runs.jsonl" 2>/dev/null || echo 0) launches recorded"
exit "$rc"
