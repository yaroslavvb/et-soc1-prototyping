# E195's kit (Q185, lane kit-e195, Sun 15 Nov 2026, before any E195 datum): the kit's changes to tools/claims-v3/lib.sh beyond the
# registered lib_x09.sh's four, sourced by block_e195.sh right after lib_x09.sh (lib.sh has set -u and has gone to its tree). E195.md
# section 10: "lib.sh's stop_sampler sends SIGKILL to a sampler that ignores SIGTERM for 30 s; the lab never kills a device process, so the
# kit replaces that branch (a sampler that ignores SIGTERM is left to end at its own --seconds bound, which the block sets to the pass's
# longest estimate plus 900 s; the session stops and the lane reports)", and "the kit keeps the card lock and the session until no device
# process of ours runs (lib.sh's ours_running), and never kills one". Four changes, each a whole function:
#  1. stop_sampler: lib.sh's (SIGTERM, then up to 30 s for the sampler to finish its request and exit), but a sampler still alive after
#     that is NEVER killed and no drain is sent: it is left to end at its own --seconds bound; the block writes the pass's STOP (runitems.py
#     ends the pass before its next item), the session's stop file build/x09-STOP (no further pass; every host launches nothing more) and
#     the marker <pass>/SAMPLER-STUCK (the session then skips its closing config read), sets X9K_STUCK, copies the sampler's lines so far
#     into telemetry.jsonl and leaves telemetry.jsonl.raw in place (the sampler still writes it);
#  2. start_sampler: lib.sh's, but with the file and the duration only (block_e195.sh's one call passes nothing else, so no word can
#     reach `ettelem sample` but --seconds and --every-ms), and it starts no sampler while a stuck one lives (never two samplers at once);
#  3. die_c: no management read while a stuck sampler lives (lib.sh: "while it runs nothing else may open the management node"): it
#     prints nothing, so block_end records die_c_end null;
#  4. x9k_on_signal, the block's signal path (block_e195.sh's on_signal calls it): it WRITES THE PASS'S STOP AND THE SESSION'S STOP FILE
#     FIRST and lets runitems end by itself at its next item (exit 8), at most 180 s, never sending it a signal while it runs: the
#     registered on_signal sent runitems SIGTERM at once, and a device process then running (its stdout a pipe to runitems) would end at
#     its next record by SIGPIPE, not "run on" (the real-path desk test's case BS found it on the stand-ins); with the two stop files the
#     host stops after its launch in flight and the heater after its calibration launch, each by itself. Only if runitems still runs
#     after 180 s does it get the registered SIGTERM (reported in the block's log). Then the sampler's stop (1 above) and
#     x9k_wait_ours: the card lock (fd 9, which this block holds until it exits) kept until no device process of ours runs (lib.sh's
#     DEV_COMM, our uid; a stuck sampler, which only reads, is not waited for), at most 30 s, polling every 0.5 s, never a signal.
# Under V3_DRY lib.sh's own stubs stay (changes 1-3 are made only on the real path); x9k_wait_ours then finds nothing (ours_running is
# lib.sh's dry stub). SPDX-License-Identifier: Apache-2.0
X9K_STUCK=
x9k_wait_ours() {
  local i pids
  for i in $(seq 1 60); do
    if [ -n "${V3_DRY:-}" ]; then return 0; fi
    pids=$(ps -eo uid=,pid=,comm= | awk -v me="$(id -u)" -v re="$DEV_COMM" -v skip="${X9K_STUCK:-0}" '$1 == me && $3 ~ re && $2 != skip {print $2}' | tr '\n' ' ')
    [ -z "${pids// /}" ] && { [ "$i" -gt 1 ] && log "x09k: no device process of ours runs: the card lock is released with this block"; return 0; }
    [ "$i" -eq 1 ] && log "x09k: a device process of ours still runs (pid ${pids% }): the card lock is kept until it ends (at most 30 s; nothing is killed)"
    sleep 0.5
  done
  log "x09k: a device process of ours still runs after 30 s (pid ${pids% }): the block ends now and the lock goes with it; nothing was killed (reported)"
  return 0
}
if [ -z "${V3_DRY:-}" ]; then
stop_sampler() {
  [ -n "${SAMPLER_PID:-}" ] || return 0
  kill -TERM "$SAMPLER_PID" 2>/dev/null
  local i; for i in $(seq 1 300); do kill -0 "$SAMPLER_PID" 2>/dev/null || break; sleep 0.1; done
  if kill -0 "$SAMPLER_PID" 2>/dev/null; then
    log "x09k: sampler $SAMPLER_PID ignored SIGTERM for 30 s: NOT killed (E195.md 10): it ends at its own --seconds bound; this pass and the session stop"
    X9K_STUCK=$SAMPLER_PID
    local d; d=$(dirname "$SAMPLER_OUT")
    echo "sampler $SAMPLER_PID ignored SIGTERM for 30 s at $(date '+%F %T %Z'): left to end at its own --seconds bound" >> "$d/SAMPLER-STUCK"
    echo "sampler stuck: $SAMPLER_PID at $(date '+%T')" >> "$d/STOP"
    echo "sampler stuck in $(basename "$d"): $SAMPLER_PID at $(date '+%T')" >> "$V3_ROOT/build/x09-STOP"
    grep '^{' "$SAMPLER_OUT.raw" >> "$SAMPLER_OUT" 2>/dev/null
    SAMPLER_PID=; SAMPLER_OUT=
    return 0
  fi
  wait "$SAMPLER_PID" 2>/dev/null
  grep '^{' "$SAMPLER_OUT.raw" >> "$SAMPLER_OUT" 2>/dev/null; rm -f "$SAMPLER_OUT.raw"
  SAMPLER_PID=; SAMPLER_OUT=
}
start_sampler() {
  local out=$1 secs=$2
  local attempt i
  if [ -n "${X9K_STUCK:-}" ]; then log "x09k: a stuck sampler ($X9K_STUCK) still lives: no second sampler"; return 1; fi
  for attempt in 1 2 3 4 5 6; do
    "$ETTELEM" sample --seconds "$secs" --every-ms 100 > "$out.raw" 2>/dev/null < /dev/null &
    SAMPLER_PID=$!; SAMPLER_OUT=$out
    for i in $(seq 1 40); do sleep 0.25; grep -q '^{' "$out.raw" 2>/dev/null && return 0; done
    stop_sampler
    if [ -n "${X9K_STUCK:-}" ]; then log "x09k: the sampler that did not start is stuck ($X9K_STUCK): no second sampler"; return 1; fi
    [ "$attempt" = 2 ] && drain_mgmt
    sleep 2
  done
  log "sampler failed to start"; return 1
}
die_c() {
  [ -n "${X9K_STUCK:-}" ] && return 0
  timeout 20 "$ETTELEM" sample --seconds 1 --every-ms 500 2>/dev/null | grep '^{' | tail -1 |
    sed -n 's/.*"minshire":\[\([0-9]*\),.*/\1/p'
}
fi
x9k_on_signal() {
  log "x09k: a signal to the block: this pass's STOP and the session's stop file written; runitems ends at its next item by itself (at most 180 s); nothing is killed"
  [ -n "${OUT:-}" ] && [ -d "$OUT" ] && echo "signal to the block at $(date '+%T')" >> "$OUT/STOP"
  echo "signal to the block${OUT:+ in $(basename "$OUT")} at $(date '+%T')" >> "$V3_ROOT/build/x09-STOP"
  local i
  if [ -n "${RUNNER:-}" ]; then
    for i in $(seq 1 360); do kill -0 "$RUNNER" 2>/dev/null || break; sleep 0.5; done
    if kill -0 "$RUNNER" 2>/dev/null; then
      log "x09k: runitems still runs after 180 s: SIGTERM to it, as the registered block (a device process of it still running can then end at its next write: reported)"
      kill -TERM "$RUNNER" 2>/dev/null
    fi
    wait "$RUNNER" 2>/dev/null
  fi
  RUNNER=
  stop_sampler
  x9k_wait_ours
  block_end failed "signal"
  exit 1
}
