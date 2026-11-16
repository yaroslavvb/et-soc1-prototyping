#!/usr/bin/env bash
# E196's LAB PORT of the proposal's run_session.sh (Q185, lane kit-e196, Sun 15 Nov 2026, PST, before any E196 datum): proposal/src/
# run_session.sh (sha256 in SHA256SUMS-e196-registration) with E196.md's registered changes made code and nothing else changed; its diff
# against that file is desk/port-diff-run_session-e196.txt. session_e196.sh (the kit's wrapper on aifoundry3) runs it. The changes:
#   S1 the files: run_block_e196.py (the port, beside this file) and stops_e196.py; make_x14.py, arms.json and stopwatch.py from
#      proposal/src at their registered sha256 (SRC);
#   S2 THE HOSTS (E196.md section 3): LAB_H, the lab's unchanged sparsity host, required; it is the heater (HEATER defaults to it and must
#      be the same file) and runs every pass run and anchor; H, the request's x14_host, runs the trains and the premise runs;
#   S3 THE OPENING CONFIGURATION GATE (E196.md section 6, item 2): config-start.json must read "tdp_w":0 and "minion_mhz":600 (the card
#      as found), else "GATE-STOP: ..." and exit 12 before the sampler (no data); the closing read is reported, never a gate;
#   S4 THE LAB'S LIVE STOPS (E196.md section 9): stops_e196.py beside stopwatch.py (board at or above 65 W on three samples in a row; a
#      die reading at or above 70 C; with STOPS_END_EPOCH, the cap's end-stop), started with it and checked with it before every block;
#   S5 the one-card rule's binary check covers LAB_H too (a host with several card nodes only);
#   S6 the DRY listing names the gate and the lab's stops.
# Everything else below is run_session.sh's, line for line: the holder checks, the configuration reads, the sampler and its starts, the
# smoke, the trains, the passes, the gaps, the deadline, the EXIT trap and its closing read.
#
# The proposal's head, unchanged:
# A session of x14 on one card: a holder check first (nothing is opened while anyone else holds the card); the
# opening configuration read (`$ETTELEM config`, read only, under the card lock, timeout 10); then one sampler for the
# whole session (started as the lab's lib.sh does: it must write its first line within 10 s, else it is stopped with
# SIGTERM and started again, up to six times; stopped with SIGTERM only, always, by the EXIT trap; its own time bound
# is the session's deadline plus 300 s), the live stops (stopwatch.py, checked to be running before every block), a
# smoke block with its gate (run_block.py --smoke: the heater check first; a failed gate runs nothing more), the
# trains (one block each), then the passes, each block under the card lock; between blocks the lock is released, a
# gap is left, and the holder check is repeated before the lock is taken again. Every pass counts (each starts with
# two burn-in runs). A block starts only if it can end before the session's deadline (DEADLINE, or SESSION_MIN minutes
# after the start): a pass's length is the first pass's measured length (until one is measured, its runs at about
# 10.4 s and two 10 s idles), a train's 4.2 min; a window too short for the smoke (90 s) opens nothing.
# The closing configuration read follows the sampler's stop, and only when the card is free: it is skipped, and
# config-end.json says why, when the session ends because the card was not free (exit 3) or on a signal; otherwise it
# runs only after the opening read's holder check passes again (et-who --check exit 0 with our sampler stopped, no
# other user's device process, the card lock free on a probe).
# Before the first block the arm table and tiles are written into GEN (default OUT/gen) by make_x14.py from the lab
# repo's kinds tiles (LAB_TILES, default tools/claims-v3/kinds/tiles/fp32 of the checkout named by LAB_REPO), and
# make_x14.py --check must pass.
#
#   run_session.sh OUT [PASSES]          (6 by default; 7 if the window allows)
# Environment:
#   SAMPLER   ettelem (default): "$ETTELEM sample --seconds T --every-ms 100"
#             pvt: "python3 -B $PVT_SAMPLE --seconds T --every-ms 100" (the lab's per-sensor sampler, same keys plus
#             the raw per-sensor temperature codes; on the card that answers it only)
#   H         the x14 host binary (default build/host/x14_host beside this script)
#   HEATER    the heater, launched before every run up to the preheat reading (as in the lab's E78 kit) with
#             run_block.py's heater arguments, which are this request's host's: default H (the lab's sparsity host
#             takes other arguments and would fail every launch). H and HEATER are made absolute, the session refuses
#             to start unless both are executable files, and the smoke's heater check must pass before anything else
#   TARGET, PREHEAT  launch reading and preheat reading (default 58 and 59)
#   DROP_ARMS pass arms to leave out of every pass, comma-separated (the request's cut order: F.Ae,Z.b50,I.H.mFFFF);
#             never the anchor K.pi; the smoke and the trains are not affected; checked against arms.json before
#             anything opens, and written into marks.jsonl by every pass
#   ET_DEVICES  the card to use on a host with more than one card (one index); unset: the host must have one card
#   LOCK      the card's lock file (default /run/lock/etsoc-shire${ET_DEVICES:-0}.lock); it must exist (the host
#             creates one per card at boot); it is opened read-only and never created, as the lab's tools do
#   GAP       seconds between blocks with the lock released (default 30)
#   TRAINS    the trains to run before the passes (default "T1 T2"; "" for none)
#   SESSION_MIN  the session's card-time budget in minutes (default 60); DEADLINE (epoch seconds) overrides it
#   SAMPLER_S the sampler's own time bound in seconds (default: until the deadline, plus 300)
#   DRY=1     print every device call, open nothing (no sampler, no lock, no holder check)
# Stop by hand: touch OUT/STOP (the launch in flight finishes first). Detach it from a script file, as the lab's
# kits do. Exit codes: 0 done; 3 the card is held or not free (nothing was opened, or the session stopped between
# blocks); 4 the sampler did not start; 5 the live stops (stopwatch.py) were not running before a block (no block ran
# after that); 10 the smoke gate failed (nothing after the smoke ran); 2 a refused setting (nothing opened); other: the
# block's own exit code (run_block.py: 4 telemetry, 6 hot, 8 stopped, 9 heater level, 11 heater failed).
set -u
out=${1:?out dir}; passes=${2:-6}; gen=${GEN:-$out/gen}
here=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
SRC=$here/proposal/src   # S1: the registered make_x14.py, arms.json and stopwatch.py
DEV=${ET_DEVICES:-0}
LOCK=${LOCK:-/run/lock/etsoc-shire$DEV.lock}
SAMPLER=${SAMPLER:-ettelem}
TARGET=${TARGET:-58}; PREHEAT=${PREHEAT:-59}
GAP=${GAP:-30}
TRAINS=${TRAINS-T1 T2}
DROP_ARMS=${DROP_ARMS:-}
T_START=$(date +%s)
DEADLINE=${DEADLINE:-$((T_START + ${SESSION_MIN:-60} * 60))}
SMOKE_S=90; TRAIN_S=252   # the smoke block (about 1 minute); a train block (24 processes of about 7.9 s, 2 anchor runs)
abspath() { case "$1" in /*) echo "$1" ;; *) echo "$PWD/$1" ;; esac; }
H=$(abspath "${H:-$here/build/host/x14_host}")
: "${LAB_H:?set LAB_H to the unchanged sparsity host of the lab (E196.md section 3): nothing opened}"   # S2
LAB_H=$(abspath "$LAB_H")
HEATER=$(abspath "${HEATER:-$LAB_H}")
[ "$HEATER" = "$LAB_H" ] || { echo "refused: HEATER ($HEATER) is not LAB_H ($LAB_H): the lab's E78 heater is the lab's host: nothing opened"; exit 2; }
export H LAB_H
for f in "$H" "$HEATER" "$LAB_H"; do
  [ -f "$f" ] && [ -x "$f" ] || { echo "refused: $f is not an executable file: nothing opened"; exit 2; }
done
fits() {   # a block of $1 seconds ends before the deadline
  [ $(( $(date +%s) + $1 )) -le "$DEADLINE" ]
}
fits "$SMOKE_S" || { echo "refused: the deadline ($DEADLINE) leaves no time for the smoke block: nothing opened"; exit 2; }
mkdir -p "$out"
TEL="$out/telemetry.jsonl"
blk=(python3 -B "$here/run_block_e196.py" "$out" --gen "$gen" --tel "$TEL" --target "$TARGET" --preheat "$PREHEAT"
     --heater "$HEATER" --lab-host "$LAB_H" --host-bin "$H")   # S1, S2
[ -n "$DROP_ARMS" ] && blk+=(--drop "$DROP_ARMS")
LAB_TILES=${LAB_TILES:-${LAB_REPO:-.}/tools/claims-v3/kinds/tiles/fp32}
python3 -B "$SRC/make_x14.py" --lab-tiles "$LAB_TILES" --out "$gen" > /dev/null &&
  python3 -B "$SRC/make_x14.py" --lab-tiles "$LAB_TILES" --out "$gen" --check > "$out/gen_check.json" ||
  { echo "make_x14.py failed or its check did not pass: nothing opened"; exit 2; }
cmp -s "$gen/arms.json" "$SRC/arms.json" || { echo "the generated arm table differs from src/arms.json: nothing opened"; exit 2; }
plan=$("${blk[@]}" 0 --plan 2>&1) || { echo "$plan: nothing opened"; exit 2; }
nruns=${plan#*runs=}; nruns=${nruns%% *}
case "$nruns" in ''|*[!0-9]*) echo "no run count in the pass plan ($plan): nothing opened"; exit 2 ;; esac
PASS_S=$(( (nruns * 104 + 229) / 10 ))   # until a pass is measured: its runs at about 10.4 s and two 10 s idles
secs=${SAMPLER_S:-$(( DEADLINE - $(date +%s) + 300 ))}   # the sampler's own bound; SIGTERM ends it at the session's end
say() { echo "[$(date +%H:%M:%S)] $*" | tee -a "$out/session.log"; }
say "the pass plan: $plan"

if [ -n "${DRY:-}" ]; then
  say "DRY: holder check (et-who --check, other users' device processes), card lock probe ($LOCK), device nodes"
  say "DRY: config read (\$ETTELEM config, under the card lock, timeout 10) -> config-start.json"
  say "DRY: the opening configuration gate: config-start.json reads \"tdp_w\":0 and \"minion_mhz\":600, else GATE-STOP, exit 12, no sampler (S3)"
  say "DRY: sampler ($SAMPLER) for at most $secs s (first line within 10 s, up to 6 starts), stopwatch"
  say "DRY: the lab's live stops (stops_e196.py: board >= 65 W on 3 samples in a row, die >= 70 C${STOPS_END_EPOCH:+, the end-stop at the epoch $STOPS_END_EPOCH}) (S4)"
  say "DRY: stopwatch running; holder check (our sampler only); smoke block (heater: $HEATER; the lab's host: $LAB_H; the request's host: $H)"
  "${blk[@]}" -1 --smoke --dry
  i=0
  for t in $TRAINS; do
    say "DRY: card lock released; gap $GAP s; STOP file; stopwatch running; holder check; card lock taken; deadline check (train ${TRAIN_S} s)"
    "${blk[@]}" $((101 + i)) --train "$t" --dry; i=$((i + 1))
  done
  for p in $(seq 0 $((passes - 1))); do
    say "DRY: card lock released; gap $GAP s; STOP file; stopwatch running; holder check; card lock taken; deadline check (pass ${PASS_S} s)"
    "${blk[@]}" "$p" --dry
  done
  say "DRY: sampler stopped (SIGTERM); after exit 3 or a signal no config read (config-end.json says why); otherwise holder check (et-who --check exit 0, no other user's device process, card lock probe), then config read -> config-end.json"
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
  for f in "$H" "${ETTELEM:-}" "$HEATER" "$LAB_H"; do   # S5
    [ -n "$f" ] || continue
    grep -aqw ET_DEVICES "$f" || { say "refused: $f does not honour ET_DEVICES: it would open every card"; exit 2; }
  done
fi
[ -e "$LOCK" ] || { say "refused: no card lock file $LOCK"; exit 2; }

# --- The holder check: before the sampler, before every block, and before the closing configuration read. ---
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

# The configuration read (clock, power limit, temperature threshold; read only), under the card lock, with the
# sampler not running (the management node takes one opener).
config_read() {
  local f=$1
  exec 9< "$LOCK"
  if flock -n -E 75 9; then
    timeout 10 "$ETTELEM" config < /dev/null 2> /dev/null | grep '^{' | tail -1 > "$f"
    flock -u 9
  else
    echo '{"skipped":"card lock busy"}' > "$f"
  fi
  exec 9<&-
  say "config $(basename "$f"): $(head -c 300 "$f")"
}
config_skip() {   # a configuration read not made: the file says why
  echo "{\"skipped\":\"$2\"}" > "$1"
  say "config $(basename "$1"): skipped: $2"
}
: "${ETTELEM:?set ETTELEM to the sampler binary, which also reads the configuration}"
config_read "$out/config-start.json"
# S3: the opening configuration gate (E196.md section 6, item 2): the card as found, TDP 0 W and 600 MHz, else no session
if ! grep -q '"tdp_w":0,' "$out/config-start.json" 2>/dev/null || ! grep -q '"minion_mhz":600,' "$out/config-start.json" 2>/dev/null; then
  say "GATE-STOP: the opening configuration read is not TDP 0 W and 600 MHz ($(head -c 200 "$out/config-start.json" 2>/dev/null)): no sampler, no block (no data)"
  exit 12
fi

S=; W=; W2=; rc=0; NOT_FREE=
stop_sampler() {   # SIGTERM only: the sampler finishes its request and exits
  [ -n "$S" ] || return 0
  kill -TERM "$S" 2>/dev/null
  local i; for i in $(seq 1 300); do kill -0 "$S" 2>/dev/null || break; sleep 0.1; done
  wait "$S" 2>/dev/null; S=
}
start_sampler() {   # the lab's lib.sh rule: a first line within 10 s, else stop it and start again (up to 6 starts)
  local attempt i
  for attempt in 1 2 3 4 5 6; do
    case "$SAMPLER" in
      pvt) : "${PVT_SAMPLE:?set PVT_SAMPLE to the lab per-sensor sampler}"
           python3 -B "$PVT_SAMPLE" --seconds "$secs" --every-ms 100 >> "$TEL" 2>> "$out/sampler.err" < /dev/null & ;;
      *)   "$ETTELEM" sample --seconds "$secs" --every-ms 100 >> "$TEL" 2>> "$out/sampler.err" < /dev/null & ;;
    esac
    S=$!
    for i in $(seq 1 40); do sleep 0.25; grep -q '^{' "$TEL" 2>/dev/null && { say "sampler up (start $attempt)"; return 0; }; done
    say "sampler start $attempt wrote no line in 10 s: stopped"
    stop_sampler
    sleep 2
  done
  return 1
}
# The EXIT trap: the sampler's stop, then the closing configuration read only when the card is free. After exit 3 (the
# card was not free) or a signal nothing more is opened; otherwise the holder check must pass again first. (NOT_FREE,
# not rc: the trap can run inside a function whose own local rc is still unset.)
finish() {
  local code=$?
  touch "$out/SESSION_DONE"
  stop_sampler
  if [ -n "$W" ]; then wait "$W" 2>/dev/null; fi
  if [ -n "$W2" ]; then wait "$W2" 2>/dev/null; fi   # S4
  [ -n "${CONFIG_END:-}" ] || return 0
  if [ "$code" -eq 3 ] || [ -n "${NOT_FREE:-}" ]; then
    config_skip "$out/config-end.json" "the session ended because the card was not free"
  elif [ "$code" -ge 128 ]; then
    config_skip "$out/config-end.json" "the session was stopped by a signal (exit $code)"
  elif free_before_sampler; then
    config_read "$out/config-end.json"
  else
    config_skip "$out/config-end.json" "the card was not free at the end"
  fi
}
trap finish EXIT
trap 'exit 130' INT TERM HUP
: > "$TEL"
start_sampler || { say "the sampler did not start: nothing more opened"; exit 4; }
CONFIG_END=1
python3 -B "$SRC/stopwatch.py" "$TEL" "$out" 2>> "$out/stopwatch.err" < /dev/null &
W=$!
python3 -B "$here/stops_e196.py" "$TEL" "$out" --board-w 65 --n 3 --max-c 70 ${STOPS_END_EPOCH:+--end-epoch "$STOPS_END_EPOCH"} \
  2>> "$out/stops.err" < /dev/null &   # S4: the lab's live stops on aifoundry3
W2=$!
sleep 5
watch_alive() {   # the live stops must be running before a block
  kill -0 "$W" 2>/dev/null && kill -0 "$W2" 2>/dev/null && return 0   # S4: both
  say "the live stops (stopwatch.py, stops_e196.py) are not running: no block runs"; rc=5; return 1
}
between() {   # the lock is free for GAP seconds: anyone else may take the card; then the checks
  sleep "$GAP"
  [ -e "$out/STOP" ] && { say "STOP: $(cat "$out/STOP")"; return 1; }
  watch_alive || return 1
  free_with_sampler || { say "$1: the card is not free, stopping"; rc=3; NOT_FREE=1; return 1; }
  return 0
}
if ! watch_alive; then
  :
elif ! free_with_sampler; then
  say "the card is not free after the sampler started: no block runs"; rc=3; NOT_FREE=1
else
  locked_block -1 --smoke; rc=$?
  if [ "$rc" -eq 0 ]; then say "smoke gate passed"
  elif [ "$rc" -eq 10 ]; then say "smoke gate FAILED: no train and no pass runs"
  elif [ "$rc" -eq 75 ]; then say "smoke: the card lock was busy, nothing more runs"
  else say "smoke: exit $rc (block stopped), nothing more runs"
  fi
fi
if [ "$rc" -eq 0 ]; then
  i=0
  for t in $TRAINS; do
    between "train $t" || break
    fits "$TRAIN_S" || { say "train $t: does not fit before the deadline, skipped"; i=$((i + 1)); continue; }
    locked_block $((101 + i)) --train "$t"; rc=$?; i=$((i + 1))
    if [ "$rc" -ne 0 ]; then
      say "train $t: exit $rc ($([ "$rc" -eq 75 ] && echo 'card lock busy' || echo 'block stopped')), stopping"; break
    fi
  done
fi
if [ "$rc" -eq 0 ]; then
  for p in $(seq 0 $((passes - 1))); do
    [ -e "$out/STOP" ] && { say "STOP: $(cat "$out/STOP")"; break; }
    between "pass $p" || break
    fits "$PASS_S" || { say "pass $p: does not fit before the deadline (pass ${PASS_S} s): the session ends"; break; }
    t0=$(date +%s)
    locked_block "$p"; rc=$?
    [ "$p" -eq 0 ] && PASS_S=$(( $(date +%s) - t0 + 10 ))   # the first pass's measured length
    if [ "$rc" -ne 0 ]; then
      say "pass $p: exit $rc ($([ "$rc" -eq 75 ] && echo 'card lock busy' || echo 'block stopped')), stopping"; break
    fi
  done
fi
sleep 8
say "session done (rc $rc): $(wc -l 2>/dev/null < "$out/runs.jsonl" || echo 0) pass launches, $(wc -l 2>/dev/null < "$out/train.jsonl" || echo 0) train launches recorded"
exit "$rc"
