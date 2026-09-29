#!/usr/bin/env bash
# TAU (the observability ladder's rung 4, the rails' 1 s filter): square step bursts that pin each rail's time
# constant and delay on the local card, for tools/ettelem/deconv.py. One pass per block, from the tree's root:
#   bash tools/claims-v3/tau/block.sh <pass> [--smoke]           aifoundry1: V3_DEVICE=1 (card 0 is refused)
#   V3_DRY=1 [TAU_DRY_CARD=aifoundry3|aifoundry1-c1] bash tools/claims-v3/tau/block.sh <pass> [--smoke]
#        no device access at all: every device program is a stub from tau/stubs/ (a simulated card with the offline
#        filters, noise and creep; TAU_STUB_SCALE compresses time, default 0.1; TAU_STUB_FAIL injects faults); data
#        under build/claims-v3-dry/<card>/tau/
# Passes (tau.json cards): 1-99 development, aifoundry1's card 1 only; 101-199 validation, aifoundry3 only, and only
# while tau/LOCK.sha256 and tau/PREREG.sha256 check (a smoke there too); 201-299 aifoundry2, only after DV2
# (TAU_A2_OK=1), frozen too.
# --smoke: ten idle 3 s sampler windows back to back (the sampler's start latency and failure rate) and two short
# bursts (~1 min of card time), data to tau-smoke/p<pass>, always re-run.
#
# A pass: the gate (STOP files, other users, our own device processes, et-who --check, the binaries; no device
# access), the card lock (flock -n, held until the block exits), then one sampler window per schedule entry (tau.json
# "full": an idle window, then 12 bursts of 2-4 s in a seeded order per pass: fmadd.ps random (M, ~20 W on the minion
# rail), fmadd.ps zeros (H, ~10 W) and a DRAM row walk (D, ~8 W on each of the SRAM and NoC rails); eight under the
# 10 Hz sampler and four under a 20 Hz one, whose longer SP pass separates "one pass late" from "a fixed delay"). A
# window is one `timeout 10 ettelem sample --seconds 9` process (the sampler never outlives a window); its burst is one
# `timeout 10 enercat_host ... --seconds <2-4>` (build/enercat: the g3log-fixed build) launched 1.5 s after the
# sampler's first line, so every window holds >= 2 s of idle before the kernel and >= 2 s after it. No --reset-ms: a
# reset restarts the rails' average (E41). A sampler with no line in 10 s is a failed start: retried (6 tries; one
# drain after the second failure, never on aifoundry1, where two failures in a row or any SIGKILL write tau/STOP and
# end the block: the owner must drain card 1's queue). A first line too late for the burst is a late start: the
# window is repeated without a burst. The idle window's die mean must be <= start_max_c (72 C) for the bursts to
# start (else exit 3). Between windows: STOP files, other users, a foreign device process. A window whose die mean
# reaches 90 C ends the block and writes tau/STOP for this card. After the block: the card lock released, et-who
# --check recorded. Exit: 0 ok (or done, or a STOP file); 1 failed; 2 refused; 3 busy (or the die too warm).
set -u
. "$(dirname "${BASH_SOURCE[0]}")/../lib.sh"          # cd's to the tree root; CARD, DATA_ROOT, log, now_ms, others_present
WD=tools/claims-v3/tau
PY=(python3 -B "$WD/reduce.py")
PASS=${1:-}; MODE=full
case "${2:-}" in '') ;; --smoke) MODE=smoke ;; *) echo "usage: tau/block.sh <pass> [--smoke]" >&2; exit 2 ;; esac
case "$PASS" in ''|*[!0-9]*|0) echo "usage: tau/block.sh <pass >= 1> [--smoke]" >&2; exit 2 ;; esac
PASS=$(( 10#$PASS ))
dry() { [ -n "${V3_DRY:-}" ]; }
a1() { case "$CARD" in aifoundry1-*) return 0 ;; esac; return 1; }

if dry; then
  CARD=${TAU_DRY_CARD:-aifoundry3}
  DATA_ROOT=$V3_ROOT/build/claims-v3-dry/$CARD; CTL=$V3_ROOT/build/claims-v3-dry
  S=$V3_ROOT/$WD/stubs; ETT=$S/stub-ettelem; ENC=$S/stub-enercat; ETWHO=$S/stub-etwho; KELF=
  export TAU_STUB_SCALE=${TAU_STUB_SCALE:-0.1} TAU_STUB_CARD=$CARD TAU_STUB_STATE=$DATA_ROOT/tau-stub-state
  SCALE=$TAU_STUB_SCALE; rm -rf "$TAU_STUB_STATE"; mkdir -p "$TAU_STUB_STATE" "$CTL"
  # the stubs' virtual clock runs 1/SCALE times faster; each dry pass starts 60 s after the last one ended, so passes
  # never overlap in virtual time (the pooled report needs that)
  v0=$(date +%s%3N); vl=$(cat "$DATA_ROOT/tau-stub-vlast" 2>/dev/null || echo 0); [ "$vl" -gt 0 ] && v0=$(( vl + 60000 ))
  echo "$(date +%s%3N) $v0" > "$TAU_STUB_STATE/epoch"
else
  bad=$(env | grep -o '^TAU_\(STUB\|DRY\)[A-Z_]*' | tr '\n' ' ')
  [ -n "$bad" ] && { echo "tau: dry-only variables set without V3_DRY: $bad" >&2; exit 2; }
  CTL=$V3_ROOT/build/claims-v3; ETT=$ETTELEM; ENC=$ENERCAT; ETWHO=et-who; SCALE=1
  KELF=$(grep -a -o '/[[:alnum:]/._-]*/enercat\.elf' "$ENC" 2>/dev/null | head -1)
fi
ENVTXT=$("${PY[@]}" env --card "$CARD" --pass "$PASS" --mode "$MODE") || { log "tau: refused (above)"; exit 2; }
eval "$ENVTXT"                                          # TAU_ROLE TAU_DEV TAU_EXP T_* SCHED TAU_ORDER BURST_*
if ! dry && [ "${V3_DEVICE:-0}" != "$TAU_DEV" ]; then log "tau: $CARD is card $TAU_DEV, V3_DEVICE is '${V3_DEVICE:-}': refused"; exit 2; fi
ms() { awk -v a="$1" -v s="$SCALE" 'BEGIN { printf "%d", a * s * 1000 }'; }         # tau.json seconds -> wall ms
nap() { sleep "$(awk -v a="$1" -v s="$SCALE" 'BEGIN { printf "%.3f", a * s }')"; }
until_ms() { local d=$(( $1 - $(now_ms) )); [ "$d" -gt 0 ] && sleep "$(awk -v d="$d" 'BEGIN { printf "%.3f", d / 1000 }')"; return 0; }
TAUROOT=$DATA_ROOT/tau; mkdir -p "$TAUROOT"
stop_requested() { [ -e "$CTL/STOP" ] || [ -e "$TAUROOT/STOP" ]; }

# ---- the gate (no device access, and before our own lock: et-who --check counts a lock we hold as held)
# Off the development card nothing runs, not even a smoke (whose check prints the card's fits), before the freeze.
if [ "$TAU_ROLE" != development ]; then
  if dry && [ -n "${TAU_DRY_SKIP_LOCK:-}" ]; then log "tau: DRY: freeze check skipped"
  elif ! sha256sum -c --quiet "$WD/LOCK.sha256" > /dev/null 2>&1 || ! sha256sum -c --quiet "$WD/PREREG.sha256" > /dev/null 2>&1; then
    log "tau p$PASS: refused: a $TAU_ROLE card runs (a smoke included) only while every file in $WD/LOCK.sha256 and $WD/PREREG.sha256 is as frozen"; exit 2
  fi
fi
if stop_requested; then log "tau p$PASS: a STOP file is present ($CTL/STOP or $TAUROOT/STOP): not starting"; exit 0; fi
others_present && exit 3
ours_running && { log "tau: one of our own device processes is running: not starting"; exit 3; }
command -v "$ETWHO" > /dev/null || { log "tau: et-who is not installed: not starting"; exit 2; }
"$ETWHO" --check > /dev/null 2>&1; rc=$?
[ "$rc" = 0 ] || { log "tau p$PASS: et-who --check says $rc (1 held, 2 failed): not starting"; exit 3; }
if ! dry; then   # the binaries (read, never run): the fixed enercat build (E49's g3log fix), its flags and its kernel
  pf=()
  [ -x "$ETT" ] || pf+=("missing $ETT")
  [ -x "$ENC" ] || pf+=("missing $ENC")
  grep -a -q 'VERBOSE_MID' "$ENC" 2>/dev/null || pf+=("$ENC lacks the g3log fix (registerRuntimeLogLevels)")
  { grep -a -q -- '--stride' "$ENC" && grep -a -q 'tload_pat' "$ENC"; } 2>/dev/null || pf+=("$ENC lacks tload_pat or --stride")
  { [ -n "$KELF" ] && [ -f "$KELF" ]; } || pf+=("the kernel compiled into $ENC ('$KELF') is missing")
  [ ${#pf[@]} = 0 ] || { log "tau: ${pf[*]}: not starting"; exit 2; }
fi

# ---- the block: its directory, the card lock, the record of the code
OUT=$DATA_ROOT/$TAU_EXP/p$PASS
if [ "$MODE" = full ] && [ -z "${V3_FORCE:-}" ] && grep -q '"status":"ok"' "$OUT/block.json" 2>/dev/null; then
  log "$TAU_EXP p$PASS already done (ok)"; exit 0
fi
if [ -d "$OUT" ]; then   # a failed, interrupted or refused attempt (or an earlier smoke): never mixed into this one
  case "$OUT" in "$V3_ROOT"/build/claims-v3-dry/*) rm -rf "$OUT" ;;
    *) mv "$OUT" "$OUT.attempt-$(date +%s)"; log "an earlier attempt of $TAU_EXP p$PASS set aside" ;; esac
fi
LK=/run/lock/etsoc-shire${TAU_DEV}.lock
if ! dry; then
  [ -e "$LK" ] || { log "tau: $LK is missing: not starting"; exit 2; }
  exec 9<>"$LK"; flock -n 9 || { log "tau: card lock $LK is held by another process: not starting"; exit 3; }
fi
mkdir -p "$OUT"
BLOCK_T0=$(now_ms)
{ sha256sum tools/claims-v3/lib.sh tools/claims-v3/queue.sh "$WD"/*.sh "$WD"/*.py "$WD"/*.json "$WD"/*.md "$WD"/stubs/* tools/ettelem/deconv.py
  if ! dry; then
    sha256sum "$ETT" "$ENC" "$KELF"
    command -v readelf > /dev/null && echo "$(readelf -x .text "$KELF" 2>/dev/null | sha256sum | cut -d' ' -f1)  $KELF:.text"
  fi; } > "$OUT/code.sha256" 2>/dev/null
dry || { command -v et-lab-manifest > /dev/null && timeout 30 et-lab-manifest > "$OUT/manifest.txt" 2>&1; }
echo "$CARD $TAU_EXP pass $PASS mode $MODE role $TAU_ROLE dev $TAU_DEV et_devices ${ET_DEVICES:-unset} scale $SCALE $(date +%FT%T)" >> "$OUT/run.log"
echo "order: $TAU_ORDER" >> "$OUT/run.log"
log "$TAU_EXP p$PASS begins ($MODE, $TAU_ROLE, ${#SCHED[@]} windows: $TAU_ORDER) -> $OUT"

# ---- sampler windows (the sampler never outlives one window: at most 10 s on the management node)
WPID=; WIN_N=0; WIN_ST=; WIN_CHK=; EXTRA_MS=0; KILLED=; START_FAILS=0; DIE0=; DIE1=
dry && EXTRA_MS=400                                     # the python stubs need ~50-300 ms to start at any time scale
TICK=$(awk -v s="$SCALE" 'BEGIN { printf "%.3f", 0.1 * s }')
drain() {   # a stale reply in the management queue (a sampler killed mid-request). Never on aifoundry1: the stock
  # dev_mngt_service opens every card's management node there, card 0's included
  if a1; then log "drain skipped on $CARD (dev_mngt_service would open card 0)"; return 0; fi
  echo "drain: timeout 10 dev_mngt_service -m DM_CMD_GET_MODULE_POWER -n 0 -u 5000$(dry && echo ' (DRY: not run)')" >> "$OUT/run.log"
  if dry; then return 0; fi
  timeout 10 "$DEVMNGT" -m DM_CMD_GET_MODULE_POWER -n 0 -u 5000 > /dev/null 2>&1 < /dev/null || true
}
a1_stop() {  # aifoundry1 cannot drain: say so where the owner and every later run will see it, and stop
  printf '%s %s p%s: %s. Card %s management queue may hold a stale reply; a drain needs the owner (the stock dev_mngt_service opens card 0 too). Remove this file after the drain.\n' \
    "$(date +%FT%T)" "$TAU_EXP" "$PASS" "$1" "$TAU_DEV" >> "$TAUROOT/STOP"
  log "tau: $1: wrote $TAUROOT/STOP (card $TAU_DEV's management queue may hold a stale reply; the owner must drain it)"
}
stop_window() {  # SIGTERM only (ettelem finishes its request); 30 s later a stuck one is killed (and drained, off aifoundry1)
  local p=${WPID:-} i c
  [ -n "$p" ] || return 0
  kill -TERM "$p" 2>/dev/null
  for i in $(seq 1 300); do kill -0 "$p" 2>/dev/null || break; sleep "$TICK"; done
  if kill -0 "$p" 2>/dev/null; then
    KILLED=1
    log "sampler $p ignored SIGTERM for 30 s: SIGKILL"
    for c in $(pgrep -P "$p"); do kill -KILL "$c" 2>/dev/null; done; kill -KILL "$p" 2>/dev/null; sleep 1
    if a1; then a1_stop "a sampler that ignored SIGTERM was killed with SIGKILL"; else drain; fi
  fi
  wait "$p" 2>/dev/null; WPID=
}
# window <rate_ms> <kind> <secs> <sampler_s>: one sampler process, and for a burst kind one enercat launch inside it.
# Returns 0 ok, 1 bad (WIN_ST says why; the entry is repeated), 3 hot, 4 the block must end (WIN_ST says why).
window() {
  local rate=$1 kind=$2 secs=$3 sws=$4 raw try L F= tb=0 brc=null n=0 chk crc args fails=0 late_ms p lim lim2
  WIN_N=$((WIN_N + 1)); WIN_ST=; WIN_CHK=
  raw=$OUT/tel-$(printf %02d "$WIN_N").jsonl
  # the latest first line that leaves room for pre + setup + burst + post inside the sampler's timeout
  late_ms=$(ms "$(awk -v t="$T_TIMEOUT" -v a="$T_PRE" -v b="$T_SETUP" -v c="$secs" -v d="$T_POST" 'BEGIN { print t - a - b - c - d }')")
  for try in $(seq 1 "$T_ATTEMPTS"); do
    : > "$raw.raw"; L=$(now_ms); F=
    dry && echo "DRY window $WIN_N ($kind $secs s @ $rate ms): timeout $T_TIMEOUT ettelem sample --seconds $sws --every-ms $rate" >&2
    timeout "$T_TIMEOUT" "$ETT" sample --seconds "$sws" --every-ms "$rate" > "$raw.raw" 2>> "$OUT/ettelem.err" < /dev/null &
    WPID=$!
    lim=$(( L + $(ms "$T_FIRST_MAX") + EXTRA_MS ))
    while [ "$(now_ms)" -lt "$lim" ]; do
      grep -q '^{' "$raw.raw" 2>/dev/null && { F=$(now_ms); break; }
      kill -0 "$WPID" 2>/dev/null || { grep -q '^{' "$raw.raw" 2>/dev/null && F=$(now_ms); break; }
      sleep 0.02
    done
    [ -n "$F" ] && break
    stop_window
    fails=$((fails + 1)); START_FAILS=$((START_FAILS + 1))
    echo "window $WIN_N: sampler start $try gave no line in $T_FIRST_MAX s" >> "$OUT/run.log"
    [ -n "$KILLED" ] && { WIN_ST=sampler_killed; break; }
    if a1; then
      [ "$fails" -ge "$T_A1_STOP_FAILS" ] && { a1_stop "$fails failed sampler starts in a row (window $WIN_N)"; WIN_ST=a1_no_sampler; break; }
    elif [ "$fails" = "$T_DRAIN_AFTER" ]; then drain; fi
    nap "$T_RETRY_WAIT"
  done
  if [ -z "$F" ]; then WIN_ST=${WIN_ST:-no_sampler}
  elif [ "$kind" != idle ] && [ $((F - L)) -gt $((late_ms + EXTRA_MS)) ]; then
    WIN_ST=late_start                                   # too little of the sampler's 10 s left: no burst, stop it now
    echo "window $WIN_N: first line $((F - L)) ms after the launch (> $late_ms ms): no burst" >> "$OUT/run.log"
    stop_window
  else
    if [ "$kind" != idle ]; then
      tb=$(( F + $(ms "$T_PRE") )); until_ms "$tb"
      eval "args=(\"\${BURST_$kind[@]}\")"
      dry && echo "DRY burst: timeout 10 enercat_host ${args[*]} --seconds $secs ${BURST_COMMON[*]}" >&2
      timeout 10 "$ENC" "${args[@]}" --seconds "$secs" "${BURST_COMMON[@]}" > "$OUT/burst.out" 2>> "$OUT/host.err" < /dev/null
      brc=$?
      n=$(grep -c '^ENERCAT {' "$OUT/burst.out")
    fi
    p=$WPID; lim2=$(( L + $(ms "$T_WALL_MAX") + EXTRA_MS ))   # the sampler ends by itself (--seconds, or its timeout)
    while kill -0 "$p" 2>/dev/null && [ "$(now_ms)" -lt "$lim2" ]; do sleep 0.05; done
    if kill -0 "$p" 2>/dev/null; then stop_window; WIN_ST=sampler_overran; else wait "$p" 2>/dev/null; WPID=; fi
  fi
  [ -n "$KILLED" ] && WIN_ST=sampler_killed
  grep '^{.*}$' "$raw.raw" > "$raw" 2>/dev/null; rm -f "$raw.raw"
  chk=$("${PY[@]}" wincheck "$raw" --kind "$kind" --stop-c "$T_STOP_C" 2>> "$OUT/wincheck.err"); crc=$?
  case "$crc" in 0|1|3) ;; *) chk= ;; esac
  [ -n "$chk" ] || { crc=1; chk='{"status":"check_error"}'; }       # a check that crashed is a bad window, never an ok one
  WIN_CHK=$chk
  [ -z "$WIN_ST" ] && [ "$crc" != 0 ] && WIN_ST=$(sed -n 's/.*"status": *"\([a-z_]*\)".*/\1/p' <<< "$chk")
  [ -z "$WIN_ST" ] && [ "$crc" != 0 ] && WIN_ST=check_error
  if [ "$kind" != idle ] && [ -z "$WIN_ST" ]; then
    [ "$n" = 0 ] && WIN_ST=no_launches
    [ -z "$WIN_ST" ] && [ "$brc" != 0 ] && WIN_ST=burst_rc_$brc
  fi
  "${PY[@]}" winrec --out "$OUT" --win "$WIN_N" --rate "$rate" --kind "$kind" --secs "$secs" --sampler-s "$sws" \
    --try "$try" --fails "$fails" --t-launch "$L" --t-first "${F:-0}" --t-burst "$tb" --burst-rc "$brc" --launches "$n" \
    --status "${WIN_ST:-ok}" --check "$chk" --burst-out "$OUT/burst.out" >> "$OUT/run.log" 2>&1
  rm -f "$OUT/burst.out"
  local d; d=$(sed -n 's/.*"die_last": *\([0-9.]*\).*/\1/p' <<< "$chk"); [ -n "$d" ] && DIE1=$d
  [ "$crc" = 3 ] && return 3
  [ -z "$WIN_ST" ] && return 0
  echo "window $WIN_N ($kind $secs s @ $rate ms): $WIN_ST" >> "$OUT/run.log"
  case "$WIN_ST" in sampler_killed|a1_no_sampler) return 4 ;; esac
  return 1
}
foreign_device() {  # another user's device process (or a CI job) appeared mid-block
  dry && { [ -n "${TAU_STUB_FOREIGN:-}" ]; return; }
  ps -eo uid=,comm= | awk -v me="$(id -u)" -v re="$OTHER_COMM" '$1 != me && $2 ~ re {f=1} END {exit !f}'
}

# ---- the end: every way out comes through here (the EXIT trap included)
FINISHED=
finish() {  # finish <ok|fail> <note> <exit code>
  local st=$1 note=$2 rc=$3 ew ewrc
  trap '' INT TERM
  stop_window
  dry || exec 9>&-                                      # release the card lock, then ask who holds the card now
  ew=$(timeout 20 "$ETWHO" --check 2>&1 < /dev/null); ewrc=$?
  ew=$(printf '%s' "$ew" | head -c 300 | tr '\n"\\' "  '")
  printf '{"exp":"%s","pass":%s,"card":"%s","mode":"%s","role":"%s","t0_ms":%s,"t1_ms":%s,"windows":%s,"dry":%s,"order":"%s","sampler_failed_starts":%s,"die_c_start":%s,"die_c_end":%s,"et_who_after":{"rc":%s,"out":"%s"},"status":"%s","note":"%s"}\n' \
    "$TAU_EXP" "$PASS" "$CARD" "$MODE" "$TAU_ROLE" "$BLOCK_T0" "$(now_ms)" "$WIN_N" "$(dry && echo true || echo false)" \
    "$TAU_ORDER" "$START_FAILS" "${DIE0:-null}" "${DIE1:-null}" "$ewrc" "$ew" "$st" "${note//\"/\'}" > "$OUT/block.json"
  log "$TAU_EXP p$PASS ends: $st $note (et-who --check after: $ewrc)"
  FINISHED=1
  exit "$rc"
}
trap '[ -n "$FINISHED" ] || finish fail "the block exited unexpectedly" 1' EXIT
trap 'finish fail "interrupted by a signal" 1' INT TERM

# ---- the pass
bad=0
for e in "${SCHED[@]}"; do
  read -r rate kind secs sws <<< "$e"
  stop_requested && finish fail "a STOP file appeared before window $((WIN_N + 1))" 0
  others_present && finish fail "another user before window $((WIN_N + 1))" 3
  foreign_device && finish fail "a foreign device process before window $((WIN_N + 1))" 3
  wok=
  for k in $(seq 1 "$T_BURST_TRIES"); do
    window "$rate" "$kind" "$secs" "$sws"; wr=$?
    if [ "$wr" = 3 ]; then
      echo "$(date +%FT%T) $TAU_EXP p$PASS window $WIN_N: the die mean reached $T_STOP_C C. Remove this file once the card is understood." >> "$TAUROOT/STOP"
      finish fail "window $WIN_N: the die mean reached $T_STOP_C C (tau/STOP set for this card)" 1
    fi
    [ "$wr" = 4 ] && finish fail "window $WIN_N: $WIN_ST (the block ends$(a1 && echo '; tau/STOP set'))" 1
    [ "$wr" = 0 ] && { wok=1; break; }
    case "$WIN_ST" in no_sampler) finish fail "window $WIN_N: the sampler did not start in $T_ATTEMPTS tries" 1 ;; esac
    bad=$((bad + 1))
  done
  if [ -z "$DIE0" ] && [ "$kind" = idle ] && [ -n "$wok" ]; then   # the start gate: the first idle window's die mean
    DIE0=$(sed -n 's/.*"die_mean": *\([0-9.]*\).*/\1/p' <<< "$WIN_CHK")
    if [ -n "$DIE0" ] && awk -v d="$DIE0" -v m="$T_START_MAX_C" 'BEGIN { exit !(d > m) }'; then
      finish fail "the idle window's die mean is $DIE0 C, above $T_START_MAX_C C: no bursts (let the card cool, then re-run)" 3
    fi
  fi
done
note=$("${PY[@]}" check-pass "$OUT" 2> "$OUT/check.err"); rc=$?
[ -s "$OUT/check.err" ] || rm -f "$OUT/check.err"
[ -s "$OUT/wincheck.err" ] || rm -f "$OUT/wincheck.err"
[ -f "$OUT/check.json" ] || echo '{}' > "$OUT/check.json"
if [ "$rc" != 0 ]; then finish fail "check: ${note:-reduce.py check-pass failed} ($bad bad windows)" 1; fi
finish ok "$note ($bad bad windows)" 0
