#!/usr/bin/env bash
# A session of regfile on one card: a holder check first (nothing is opened while anyone else holds the card), then one
# sampler for the whole session (stopped with SIGTERM only, always, by the EXIT trap), the live stops (stopwatch.py), a
# smoke block with its gate, then the blocks of trains.tsv (A, B, C, D; or E, the optional second sitting), each under
# the card lock. The smoke block and the first block run back to back (the lock is free only while the holder check is
# made between them); between two blocks of trains.tsv the lock is free for GAP seconds; the holder check is repeated
# before every block. Run it only inside a window that the lab session has named for this request: the holder check
# sees other users' device processes and the card's holders, not a queue of the same account between its blocks.
#
#   run_session.sh OUT [full|short|ext]       (ext: the optional second sitting, block E, in a window of its own)
# OUT is a fresh folder for every session (the reducer pools several OUT folders): a folder that holds any file of an
# earlier session is refused (exit 2), because its SESSION_DONE would end the live stops at once and its records would
# mix two sessions. A dry run writes only session.log there.
# Environment:
#   SAMPLER   ettelem (default): "$ETTELEM sample --seconds T --every-ms 100"
#             pvt: "python3 -B $PVT_SAMPLE --seconds T --every-ms 100" (the lab's per-sensor sampler, same keys plus
#             the raw per-sensor temperature codes; on the card that answers it only)
#   ET_DEVICES  the card to use on a host with more than one card (one index); unset: the host must have one card
#   LOCK      the card's lock file (default /run/lock/etsoc-shire${ET_DEVICES:-0}.lock); it must exist (the host
#             creates one per card at boot); it is opened read-only and never created, as the lab's tools do
#   GAP       seconds between blocks with the lock released (default 30)
#   CAP_S     card-time cap of the session in seconds, from the sampler's start (default 3000 full, 2400 short,
#             2100 ext); no train starts unless it fits before the cap less 60 s, and no train process unless it
#             would end before then even at its timeout's 11 s bound
#   SAMPLER_S the sampler's own time bound in seconds (default CAP_S + 600)
#   H         the regfile host binary (default ./build/host/regfile_host)
#   DRY=1     print every device call, open nothing (no sampler, no lock, no holder check)
# Stop by hand: touch OUT/STOP (the launch in flight finishes first). A TERM, INT or HUP to this shell writes OUT/STOP
# at once; the block's device process ends after its launch in flight (run_trains.py sends it TERM if it is still
# there 5 s later), then the sampler is stopped. Detach it from a script file, as the lab's kits do. Exit codes:
# 0 done; 2 a refused setting or a used OUT; 3 the card is held or not free (nothing was opened, or the session
# stopped between blocks); 4 telemetry stale; 5 device processes failing; 6 hot; 7 the smoke gate failed; 8 stopped
# by OUT/STOP; 75 the card lock busy; 128 + n signal n.
set -u
out=${1:?out dir}; plan=${2:-full}
case "$plan" in full) blocks="A B C D"; cap=${CAP_S:-3000} ;; short) blocks="A B C D"; cap=${CAP_S:-2400} ;;
  ext) blocks="E"; cap=${CAP_S:-2100} ;;
  *) echo "plan must be full, short or ext" >&2; exit 2 ;; esac
here=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
DEV=${ET_DEVICES:-0}
LOCK=${LOCK:-/run/lock/etsoc-shire$DEV.lock}
SAMPLER=${SAMPLER:-ettelem}
GAP=${GAP:-30}
H=${H:-$here/build/host/regfile_host}
export H
mkdir -p "$out"
TEL="$out/telemetry.jsonl"
blk=(python3 -B "$here/run_trains.py" "$out" --tel "$TEL" --plan "$plan")
say() { echo "[$(date +%H:%M:%S)] $*" | tee -a "$out/session.log"; }
why() {  # a block's exit code in words
  case $1 in 4) echo 'telemetry stale' ;; 5) echo 'device processes failing' ;; 6) echo 'hot' ;;
    7) echo 'smoke gate failed' ;; 8) echo 'stopped' ;; 75) echo 'card lock busy' ;; *) echo 'block stopped' ;; esac
}

# --- A fresh OUT: no file of an earlier session in it. ---
for f in SESSION_DONE STOP telemetry.jsonl runs.jsonl marks.jsonl stderr.txt sampler.err stopwatch.err; do
  [ ! -e "$out/$f" ] || { say "refused: $out holds $f from an earlier session: give every session a fresh OUT"; exit 2; }
done

if [ -n "${DRY:-}" ]; then
  say "DRY: holder check (et-who --check, other users' device processes), card lock probe ($LOCK), device nodes"
  say "DRY: sampler ($SAMPLER) for at most ${SAMPLER_S:-$((cap + 600))} s, stopwatch; cap $cap s"
  "${blk[@]}" smoke --dry
  first=1
  for b in $blocks; do
    [ "$first" -eq 1 ] || say "DRY: card lock released; gap $GAP s; holder check; card lock taken"
    first=0
    "${blk[@]}" "$b" --dry
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
  case "$SAMPLER" in pvt) sampler_file=${PVT_SAMPLE:-} ;; *) sampler_file=${ETTELEM:-} ;; esac
  for f in "$H" "$sampler_file"; do
    [ -n "$f" ] || continue
    grep -aqw ET_DEVICES "$f" || { say "refused: $f does not honour ET_DEVICES: it would open every card"; exit 2; }
  done
fi
[ -e "$LOCK" ] || { say "refused: no card lock file $LOCK"; exit 2; }

# --- The holder check: before the sampler, and again before every block. ---
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
  exec 9<&-   # closing the probe's only descriptor releases its lock
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
# A block under the card lock: the lock file opened read-only (never created) on fd 9 and taken with flock -n (never
# waited for). The block inherits fd 9 and keeps it open in every device process it starts (--lock-fd), so the lock
# lasts while any of them runs: it is released by closing, never by an explicit unlock, which would free the card for
# every process that shares the descriptor (a device process outliving its block would then run on a free card). The
# block runs in the background and this shell waits for it, so that a signal to this shell is handled at once (bash
# runs a trap only after a foreground command has ended, but a trapped signal interrupts wait). Exit 75: the lock was
# busy, nothing ran.
locked_block() {
  local rc
  exec 9< "$LOCK"
  if ! flock -n -E 75 9; then exec 9<&-; return 75; fi
  "${blk[@]}" "$@" --lock-fd 9 &
  C=$!
  wait "$C"; rc=$?
  C=
  exec 9<&-
  return $rc
}

free_before_sampler || { say "the card is not free: nothing opened"; exit 3; }

secs=${SAMPLER_S:-$((cap + 600))}   # a bound on the sampler's own life; SIGTERM ends it at the session's end
S=; W=; C=
nap() { sleep "$1" & C=$!; wait "$C"; C=; }   # a pause that a signal to this shell ends at once
finish() {
  trap '' INT TERM HUP   # nothing interrupts the stopping
  if [ -n "$C" ]; then   # a block (or a pause) is still running: it sees OUT/STOP; wait for it to end
    kill -TERM "$C" 2>/dev/null; wait "$C" 2>/dev/null
  fi
  touch "$out/SESSION_DONE"
  if [ -n "$S" ]; then kill -TERM "$S" 2>/dev/null; wait "$S" 2>/dev/null; fi
  if [ -n "$W" ]; then wait "$W" 2>/dev/null; fi
}
on_signal() {  # $1: the signal's number. OUT/STOP first (the host and run_trains.py check it), then the EXIT trap.
  trap '' INT TERM HUP
  [ -e "$out/STOP" ] ||
    printf '{"by": "run_session", "why": "signal %s", "t_ms": %s}\n' "$1" "$(date +%s%3N)" > "$out/STOP"
  say "signal $1: OUT/STOP written, stopping"
  exit $((128 + $1))
}
trap finish EXIT
trap 'on_signal 2' INT
trap 'on_signal 15' TERM
trap 'on_signal 1' HUP
case "$SAMPLER" in
  pvt) : "${PVT_SAMPLE:?set PVT_SAMPLE to the lab per-sensor sampler}"
       python3 -B "$PVT_SAMPLE" --seconds "$secs" --every-ms 100 > "$TEL" 2> "$out/sampler.err" < /dev/null & ;;
  *)   : "${ETTELEM:?set ETTELEM to the sampler binary}"
       "$ETTELEM" sample --seconds "$secs" --every-ms 100 > "$TEL" 2> "$out/sampler.err" < /dev/null & ;;
esac
S=$!
t_start=$(date +%s)
deadline=$((t_start + cap - 60))
python3 -B "$here/stopwatch.py" "$TEL" "$out" 2>> "$out/stopwatch.err" < /dev/null &
W=$!
nap 10
rc=0
if ! free_with_sampler; then
  say "the card is not free after the sampler started: no block runs"; rc=3
else
  locked_block smoke; rc=$?
  [ "$rc" -eq 0 ] || say "smoke: exit $rc ($(why "$rc")), no block runs"
fi
if [ "$rc" -eq 0 ]; then
  first=1
  for b in $blocks; do
    [ -e "$out/STOP" ] && { say "STOP: $(cat "$out/STOP")"; rc=8; break; }
    if [ "$first" -eq 0 ]; then
      nap "$GAP"   # the lock is free for this long: anyone else may take the card
      [ -e "$out/STOP" ] && { say "STOP: $(cat "$out/STOP")"; rc=8; break; }
    fi
    first=0
    [ "$(date +%s)" -lt "$deadline" ] || { say "cap reached before block $b"; break; }
    free_with_sampler || { say "block $b: the card is not free, stopping"; rc=3; break; }
    locked_block "$b" --deadline "$deadline"; rc=$?
    if [ "$rc" -ne 0 ]; then
      say "block $b: exit $rc ($(why "$rc")), stopping"; break
    fi
  done
fi
# The sampler's last seconds after the last block, only when the session ended well: after a holder, a busy lock, a
# stop or a failure the EXIT trap stops the sampler at once.
[ "$rc" -ne 0 ] || nap 8
say "session done (rc $rc): $(wc -l < "$out/runs.jsonl" 2>/dev/null || echo 0) launches recorded"
exit "$rc"
