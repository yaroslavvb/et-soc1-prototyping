# OH (the effect of overheating, E53): the shell helpers of block.sh. Source it after ../lib.sh (which cd's to the tree
# root and sets CARD, HEATER, ETTELEM, ONCHIP, MEMPROBE, MMBENCH_DIR, DATA_ROOT, the lock and the V3_DRY stubs):
#   OH_DIR=tools/claims-v3/oh; . "$OH_DIR/ohlib.sh"
# A pruned copy of ../hp/hplib.sh (hp/ is locked and untouched). The owner's card rules it enforces (CLAUDE.md,
# AGENT.md §5, the orchestrator's task of 28 Sep):
#   - nobody else on the card: lib others_present, the process scan and the et_soc1 use count at block start AND
#     between every two launches (oh_between); the card lock (lib block_begin, fd 9) held for the whole block;
#   - every device process <= 10 s (lib hold10 = timeout 10), the device released between launches;
#   - chains of back-to-back launches <= 150 s, then >= 15 s with no launch (oh_admit: the sampler keeps running);
#   - 88 C: the watcher stops the heater (its --stop-file) and the block when the mean OR any sensor reads >= 88 C,
#     and ends the session (build/claims-v3/STOP); soft caps (a sensor >= 86, the mean >= 85, the board >= 78 W for
#     2 samples) stop heater launches until the reading falls 1 C / 2 W below the cap; 82 W for 2 samples ends it all;
#   - never aifoundry1 card 0: refused here, in ohlib.py and in run_queue.sh; on card 1 a read-only guard sampler on
#     card 0 (ET_DEVICES=0, 1 Hz, no lock, no launch) must read <= 85 C to start and stops card 1's work above 90 C or
#     10 s stale; card 0 must hold no process and no lock holder at every between-launch check;
#   - no global state change: no TDP, threshold, clock, voltage, firmware, trace or SP log level command. The one write
#     is the sampler's statistics reset (ettelem --reset-ms 1000: the SP's min/max statistics, as E52 on both cards),
#     preceded at block start by a read-only sample that records the standing statistics (stats-before.jsonl).
set -u
case "${CARD:-}" in
  aifoundry1-c0) echo "oh: aifoundry1 card 0 is never used: refused (V3_DEVICE=${V3_DEVICE:-})" >&2; exit 2 ;;
  aifoundry1-c1) [ "${ET_DEVICES:-}" = 1 ] || { echo "oh: aifoundry1-c1 needs ET_DEVICES=1 (got '${ET_DEVICES:-}'): refused" >&2; exit 2; } ;;
  aifoundry3) ;;
  *) echo "oh: $CARD is not an OH card: refused" >&2; exit 2 ;;
esac
OH_DIR=${OH_DIR:-tools/claims-v3/oh}
OHPY=(python3 "$OH_DIR/ohlib.py")
HEATER_KERNEL=$(dirname "$HEATER")/../kernel/sparsity.elf
case "$HEATER_KERNEL" in /*) HEATER_KERNEL_ABS=$HEATER_KERNEL ;; *) HEATER_KERNEL_ABS=$V3_ROOT/$HEATER_KERNEL ;; esac
MMB_LAUNCHER=$MMBENCH_DIR/build/launchers/mmbench_launcher
MMB_KERNEL=$MMBENCH_DIR/build/kernels/nekko/mmbench.elf
MEMPROBE_KERNEL=$(dirname "$MEMPROBE")/../kernel/memprobe.elf
SESSION_STOP=$V3_ROOT/build/claims-v3/STOP
dry() { [ -n "${V3_DRY:-}" ]; }

# ---- V3_DRY=1: an accelerated simulation instead of the card (ohlib.py dry-*); no device is touched
if dry; then
  export OH_DRY_SPEED=${OH_DRY_SPEED:-40}
  export OH_DRY_CARD=$CARD
  export OH_DRY_DIR=${OH_DRY_DIR:-$V3_ROOT/build/claims-v3-dry/oh-sim}
  mkdir -p "$OH_DRY_DIR"
  if [ -z "${OH_VT0:-}" ]; then [ -s "$OH_DRY_DIR/vt0" ] || date +%s%3N > "$OH_DRY_DIR/vt0"; OH_VT0=$(cat "$OH_DRY_DIR/vt0"); fi
  export OH_VT0
  SESSION_STOP=$V3_ROOT/build/claims-v3-dry/STOP
  now_ms() { local r; r=$(date +%s%3N); echo $(( OH_VT0 + (r - OH_VT0) * OH_DRY_SPEED )); }
  oh_sleep() { sleep "$(awk -v s="$1" -v k="$OH_DRY_SPEED" 'BEGIN{printf "%.3f", s / k}')"; }
  die_c() { "${OHPY[@]}" dry-die --card "$CARD"; }
  start_sampler() {
    local out=$1 secs=$2; shift 2
    local rs=0; [ "${1:-}" = --reset-ms ] && rs=$2
    "${OHPY[@]}" dry-sampler --card "$CARD" --out "$out.raw" --seconds "$secs" --every-ms 100 --reset-ms "$rs" &
    SAMPLER_PID=$!; SAMPLER_OUT=$out
    local i; for i in $(seq 1 100); do grep -q '^{' "$out.raw" 2>/dev/null && return 0; sleep 0.02; done
    return 0
  }
  stop_sampler() {
    [ -n "${SAMPLER_PID:-}" ] || return 0
    kill -TERM "$SAMPLER_PID" 2>/dev/null; wait "$SAMPLER_PID" 2>/dev/null
    grep '^{' "$SAMPLER_OUT.raw" >> "$SAMPLER_OUT" 2>/dev/null; rm -f "$SAMPLER_OUT.raw"
    SAMPLER_PID=; SAMPLER_OUT=
  }
  others_present() { [ -e "$OH_DRY_DIR/intrude" ] && { log "others present (dry hook $OH_DRY_DIR/intrude)"; return 0; }; return 1; }
else
  oh_sleep() { sleep "$1"; }
fi
# lib's start_sampler with fds 8 and 9 (the card locks) closed for the sampler it starts
eval "oh_lib_start_sampler() $(declare -f start_sampler | tail -n +2)"
start_sampler() { oh_lib_start_sampler "$@" 8>&- 9>&-; }

jnum() { [ -z "${1:-}" ] || [ "$1" = - ] && echo null || echo "$1"; }
mark() {  # mark <event> [extra JSON fields]
  local extra=${2:-}; [ -n "$extra" ] && extra=",$extra"
  echo "{\"t_ms\":$(now_ms),\"ev\":\"$1\"$extra}" >> "$OUT/marks.jsonl"
}
eval "oh_lib_die_c() $(declare -f die_c | tail -n +2)"
die_c() { local t=; [ -n "${NO_CARD:-}" ] || t=$(oh_lib_die_c); echo "${t:-null}"; }

if [ -n "${V3_DEVICE:-}" ]; then MODCHECK=skipped; else MODCHECK=on; fi
modcount() {
  [ "$MODCHECK" = on ] || { echo; return 0; }
  if dry; then echo 0; else lsmod 2>/dev/null | awk '$1=="et_soc1"{print $3}'; fi
}
penv_devices() {
  local env; env=$( { tr '\0' '\n' < "/proc/$1/environ"; } 2>/dev/null ) || return 1
  [ -n "$env" ] || [ -e "/proc/$1" ] || return 1
  sed -n 's/^ET_DEVICES=//p' <<< "$env" | head -n 1
}
# device processes on this card other than our sampler, our guard and our current launch ("F ..."); ours on the host's
# other card ("O ...")
scan_procs() {
  dry && return 0
  local me uid pid comm e
  me=$(id -u)
  ps -eo uid=,pid=,comm= |
    awk -v me="$me" -v dev="$DEV_COMM" -v oth="$OTHER_COMM" -v sp="${SAMPLER_PID:-0}" -v gp="${GUARD_PID:-0}" \
      '$2 != sp && $2 != gp && (($1 == me && $3 ~ dev) || ($1 != me && $3 ~ oth)) {print $1, $2, $3}' |
    while read -r uid pid comm; do
      if [ -n "${V3_DEVICE:-}" ] && [ "$uid" = "$me" ] && [ "$comm" != dev_mngt_servi ]; then
        e=$(penv_devices "$pid") || continue
        if [ -n "$e" ]; then
          case ",${e// /,}," in *",$V3_DEVICE,"*) ;; *) echo "O $uid:$pid:$comm"; continue ;; esac
        fi
      fi
      echo "F $uid:$pid:$comm"
    done
}
foreign_procs() { scan_procs | awk '$1 == "F" {print $2}' | tr '\n' ' '; }

# ---- abort and cleanup. Exit 3 = someone else on the card: leave it at once.
WATCH_PID=; GUARD_PID=; GUARD_RAW=; GUARD_T0=; NO_CARD=
oh_session_stop() { touch "$SESSION_STOP"; mark session_stop "\"why\":\"${1//\"/\'}\",\"file\":\"$SESSION_STOP\""; }
oh_abort() {  # oh_abort <exit code> <note> [session]
  mark abort "\"why\":\"${2//\"/\'}\",\"code\":$1"
  [ "${3:-}" = session ] && oh_session_stop "$2"
  [ "$1" = 3 ] && NO_CARD=1
  oh_run_end_quiet
  oh_guard_stop
  oh_gzip_all
  block_end fail "$2"
  exit "$1"
}
oh_gzip_all() {
  local f
  for f in "$OUT"/tel-*.jsonl "$OUT"/guard.jsonl "$OUT"/stats-before.jsonl; do [ -f "$f" ] && gzip -f -n -9 "$f"; done
  if [ -d "$OUT/k" ] && [ -n "$(ls -A "$OUT/k" 2>/dev/null)" ]; then
    tar -C "$OUT" -cf - k | gzip -n -9 > "$OUT/k.tar.gz" && rm -rf "$OUT/k"
  fi
  rm -f "$OUT"/.state-* "$OUT"/.ctl-* "$OUT"/.stop-*
  rm -rf "$OUT/run"
  if [ -d "$OUT/mp" ]; then     # the memprobe programs: the op lists are regenerated from gen.log's commands
    rm -f "$OUT"/mp/*.ops
    for f in "$OUT"/mp/*.json "$OUT"/mp/*.u32; do [ -f "$f" ] && gzip -f -n -9 "$f"; done
  fi
}
oh_cleanup() { oh_run_end_quiet; oh_guard_stop; }

# ---- the card-0 guard (aifoundry1 card 1 only): the only access to card 0, a read-only sampler with no lock
GUARD_ON=; [ "$CARD" = aifoundry1-c1 ] && GUARD_ON=1
oh_guard_start() {   # oh_guard_start [gate C]
  [ -n "$GUARD_ON" ] || return 0
  local gate=${1:-$P_guard_gate_c}
  GUARD_RAW=$OUT/guard.jsonl.raw
  local try i
  for try in 1 2 3; do
    : > "$GUARD_RAW"
    if dry; then "${OHPY[@]}" dry-guard --out "$GUARD_RAW" --seconds "$P_guard_max_s" --every-ms 1000 8>&- 9>&- &
    else ET_DEVICES=0 "$ETTELEM" sample --seconds "$P_guard_max_s" --every-ms 1000 > "$GUARD_RAW" 2>/dev/null < /dev/null 8>&- 9>&- & fi
    GUARD_PID=$!; GUARD_T0=$(now_ms)
    for i in $(seq 1 60); do grep -q '^{' "$GUARD_RAW" 2>/dev/null && break; sleep 0.25; done
    grep -q '^{' "$GUARD_RAW" 2>/dev/null && break
    oh_guard_stop; sleep 2
  done
  [ -n "$GUARD_PID" ] || return 1
  local why; why=$("${OHPY[@]}" guardcheck --guard "$GUARD_RAW" --gate "$gate" --max-age "$P_guard_stale_s")
  local rc=$?
  mark guard_start "\"ok\":$([ $rc = 0 ] && echo true || echo false),\"gate\":$gate,\"pid\":$GUARD_PID,\"why\":\"$why\""
  return $rc
}
oh_guard_refresh() {
  [ -n "$GUARD_ON" ] && [ -n "${GUARD_PID:-}" ] || return 0
  [ $(( $(now_ms) - GUARD_T0 )) -ge $(( P_guard_refresh_s * 1000 )) ] || return 0
  oh_guard_stop
  oh_guard_start "$P_guard_stop_c" || oh_abort 1 "card-0 guard did not restart (refresh)" session
}
oh_guard_stop() {
  [ -n "${GUARD_PID:-}" ] || return 0
  kill -TERM "$GUARD_PID" 2>/dev/null
  local i; for i in $(seq 1 300); do kill -0 "$GUARD_PID" 2>/dev/null || break; sleep 0.1; done
  wait "$GUARD_PID" 2>/dev/null
  GUARD_PID=
  [ -f "$GUARD_RAW" ] && { grep '^{' "$GUARD_RAW" >> "$OUT/guard.jsonl"; rm -f "$GUARD_RAW"; }
}
oh_guard_ok() {
  [ -n "$GUARD_ON" ] || return 0
  GUARD_WHY=$("${OHPY[@]}" guardcheck --guard "$GUARD_RAW" --gate "$P_guard_stop_c" --max-age "$P_guard_stale_s")
}
eval "oh_lib_drain_mgmt() $(declare -f drain_mgmt | tail -n +2)"
drain_mgmt() {
  if [ -n "$GUARD_ON" ] && [ -n "${GUARD_PID:-}" ]; then
    oh_guard_stop; oh_lib_drain_mgmt
    oh_guard_start "$P_guard_stop_c" || oh_abort 1 "card-0 guard did not restart after a drain" session
  else
    oh_lib_drain_mgmt
  fi
}
# card 0 idle: no process of ours naming card 0, no holder of /dev/et0_* or etsoc-shire0.lock (any user, our guard
# excepted), no flock on etsoc-shire0.lock (/proc/locks, read, never taken)
OH_CARD0_LOCK=/run/lock/etsoc-shire0.lock
oh_card0_violations() {
  local me pid e v= ino
  dry && return 0
  me=$(id -u)
  for pid in $(ps -eo uid=,pid=,comm= | awk -v me="$me" -v re="$DEV_COMM" -v gp="${GUARD_PID:-0}" -v sp="${SAMPLER_PID:-0}" \
                 '$1 == me && $3 ~ re && $2 != gp && $2 != sp {print $2}'); do
    e=$(penv_devices "$pid") || continue
    [ -n "$e" ] || continue
    case ",${e// /,}," in *",0,"*) v="$v proc:$pid(ET_DEVICES=$e)" ;; esac
  done
  if [ -x /usr/local/sbin/et-holders ]; then
    v="$v $(sudo -n /usr/local/sbin/et-holders 8>&- 9>&- 2>/dev/null |
             awk -v gp="${GUARD_PID:-0}" '($1 ~ /^\/dev\/et0_/ || $1 == "lock:etsoc-shire0.lock") && $3 != gp {printf "holder:%s:%s:%s ", $1, $2, $3}')"
  fi
  if [ -e "$OH_CARD0_LOCK" ]; then
    ino=$(stat -c %i "$OH_CARD0_LOCK" 2>/dev/null)
    [ -n "$ino" ] && v="$v $(awk -v ino="$ino" '{n=split($6, f, ":"); if (f[n] == ino) printf "lock:etsoc-shire0.lock(pid %s) ", $5}' /proc/locks 2>/dev/null)"
  fi
  v=${v## }; v=${v%% }
  echo "$v"
}
oh_card0_check() {
  [ -n "$GUARD_ON" ] || return 0
  local v; v=$(oh_card0_violations)
  [ -z "${v// /}" ] && return 0
  if [ -n "${OUT:-}" ] && [ -f "$OUT/marks.jsonl" ]; then oh_abort 3 "card 0 not idle ($1): $v"; fi
  log "oh: card 0 not idle ($1): $v"; exit 3
}
# an orphaned card-0 guard of ours (its block was SIGKILLed): stopped with SIGTERM at block start
oh_orphan_guards() {
  [ -n "$GUARD_ON" ] || return 0
  dry && return 0
  local me pid e pp pcmd
  me=$(id -u)
  for pid in $(ps -eo uid=,pid=,comm= | awk -v me="$me" '$1 == me && $3 == "ettelem" {print $2}'); do
    e=$(penv_devices "$pid") || continue
    [ "$e" = 0 ] || continue
    tr '\0' ' ' < "/proc/$pid/cmdline" 2>/dev/null | grep -q 'sample --seconds [0-9]* --every-ms 1000' || continue
    pp=$(ps -o ppid= -p "$pid" | tr -d ' ')
    pcmd=$(tr '\0' ' ' < "/proc/$pp/cmdline" 2>/dev/null)
    case "$pcmd" in *tools/claims-v3/hp/block.sh*|*tools/claims-v3/hp/probe.sh*|*tools/claims-v3/oh/block.sh*) continue ;; esac
    log "oh: orphaned card-0 guard $pid (parent $pp: ${pcmd:-gone}): SIGTERM"
    kill -TERM "$pid" 2>/dev/null
    local i; for i in $(seq 1 300); do kill -0 "$pid" 2>/dev/null || break; sleep 0.1; done
    kill -0 "$pid" 2>/dev/null && { log "oh: orphaned guard $pid ignored SIGTERM for 30 s: not starting"; exit 3; }
  done
  return 0
}
oh_lock_present() {
  dry && return 0
  [ -e "/run/lock/etsoc-shire${V3_DEVICE:-0}.lock" ] || { log "oh: /run/lock/etsoc-shire${V3_DEVICE:-0}.lock is missing: not starting without the card lock"; exit 1; }
}
OH_REFUSED_LOG=$V3_ROOT/build/claims-v3/oh-refused.jsonl; dry && OH_REFUSED_LOG=$V3_ROOT/build/claims-v3-dry/oh-refused.jsonl
oh_refused_record() {
  mkdir -p "$(dirname "$OH_REFUSED_LOG")"
  python3 -c 'import json,sys,time; print(json.dumps({"t_ms": int(time.time()*1000), "who": sys.argv[1], "card": sys.argv[2],
    "pass": sys.argv[3], "why": sys.argv[4], "dry": sys.argv[5] == "1"}))' "$1" "$CARD" "${PASS:-}" "$2" "$(dry && echo 1 || echo 0)" \
    >> "$OH_REFUSED_LOG" 2>/dev/null || true
}
oh_envcheck() {
  local o; o=$("${OHPY[@]}" envcheck --card "$CARD") || { oh_refused_record "oh_envcheck" "$o"; log "oh: refused: $o"; exit 2; }
  OH_OVERRIDES=$o
}
oh_binaries_json() {
  "${OHPY[@]}" binhash "heater=$HEATER" "heater_kernel=$HEATER_KERNEL" "ettelem=$ETTELEM" "onchip=$ONCHIP" \
    "onchip_kernel=$(dirname "$ONCHIP")/../kernel/onchip.elf" "memprobe=$MEMPROBE" "memprobe_kernel=$MEMPROBE_KERNEL" \
    "mmbench=$MMB_LAUNCHER" "mmbench_kernel=$MMB_KERNEL"
}

# ---- between launches: nobody else on the card, no foreign device process, the use count, card 0, the guard
oh_between() {
  others_present && oh_abort 3 "another user or device process present between launches"
  local fp; fp=$(foreign_procs)
  [ -n "${fp// /}" ] && oh_abort 3 "device process on this card between launches: $fp"
  local n; n=$(modcount)
  [ -n "$n" ] && [ -n "${NS:-}" ] && [ "$n" -gt "$NS" ] && oh_abort 3 "et_soc1 use count $n > $NS between launches"
  oh_card0_check "between launches"
  if [ -n "$GUARD_ON" ]; then oh_guard_ok || oh_abort 1 "card-0 guard: $GUARD_WHY" session; fi
  LAST_BETWEEN=$(now_ms)
  return 0
}

# ---- the chain rule: back-to-back launches for at most chain_cap_s, then >= chain_gap_s with no launch
CHAIN_T0=; CHAIN_N=0; LAST_END=0
oh_admit() {   # oh_admit <expected seconds of the next launch>
  local exp=$1 now; now=$(now_ms)
  if [ -z "$CHAIN_T0" ] || [ $(( now - LAST_END )) -ge $(( P_chain_gap_s * 1000 )) ]; then
    CHAIN_T0=$now; CHAIN_N=$(( CHAIN_N + 1 )); return 0
  fi
  if [ $(( now + (exp + 1) * 1000 - CHAIN_T0 )) -gt $(( P_chain_cap_s * 1000 )) ]; then
    mark chain_gap "\"chain\":$CHAIN_N,\"chain_s\":$(( (now - CHAIN_T0) / 1000 ))"
    while [ $(( $(now_ms) - LAST_END )) -lt $(( P_chain_gap_s * 1000 + 200 )) ]; do
      oh_live || true
      [ $(( $(now_ms) - ${LAST_BETWEEN:-0} )) -ge 5000 ] && oh_between
      oh_sleep 0.2
    done
    CHAIN_T0=$(now_ms); CHAIN_N=$(( CHAIN_N + 1 ))
  fi
}
oh_chain_room() {   # oh_chain_room <seconds>: 0 if the current chain can still take that many seconds of launches
  local now; now=$(now_ms)
  [ -z "$CHAIN_T0" ] && return 0
  [ $(( now - LAST_END )) -ge $(( P_chain_gap_s * 1000 )) ] && return 0
  [ $(( now + ($1 + 1) * 1000 - CHAIN_T0 )) -le $(( P_chain_cap_s * 1000 )) ]
}
oh_gap() {   # a full gap now (sampler on, checks run), so the next launch starts a new chain
  mark chain_gap "\"chain\":$CHAIN_N,\"forced\":true"
  while [ $(( $(now_ms) - LAST_END )) -lt $(( P_chain_gap_s * 1000 + 200 )) ]; do
    oh_live || true
    [ $(( $(now_ms) - ${LAST_BETWEEN:-0} )) -ge 5000 ] && oh_between
    oh_sleep 0.2
  done
  CHAIN_T0=
}

# ---- one heater process: oh_heat_launch <kind> <mask> <per_shire> <seconds>; sets LAST_RC, L_TS, L_TE
SEQ=0
oh_record_launch() {   # oh_record_launch <kind> <name> <tool> <file> [extra JSON]
  local extra=${5:-}; [ -n "$extra" ] && extra=",$extra"
  echo "{\"seq\":$SEQ,\"run\":\"$RUN_ID\",\"band\":\"${BAND:-}\",\"kind\":\"$1\",\"name\":\"$2\",\"tool\":\"$3\",\"file\":\"${4#"$OUT"/}\",\"chain\":$CHAIN_N,\"t_start_ms\":$L_TS,\"t_end_ms\":$L_TE,\"rc\":$LAST_RC,\"mean_before\":$(jnum "${L_MEAN0:-}"),\"high_before\":$(jnum "${L_HIGH0:-}")$extra}" >> "$OUT/launches.jsonl"
}
oh_heat_launch() {
  local kind=$1 mask=$2 per=$3 secs=$4 f
  SEQ=$(( SEQ + 1 )); f=$OUT/k/$(printf %04d "$SEQ")-$kind.out
  local args=(--test fma --type fp32 --pattern none --values randn --shires "$mask" --per-shire "$per" --seconds "$secs" --seed 1
              --kernel "$HEATER_KERNEL_ABS" --stop-file "$RUN_SF")
  L_MEAN0=$ST_MEAN; L_HIGH0=$ST_HIGH
  L_TS=$(now_ms)
  if dry; then "${OHPY[@]}" dry-heater --card "$CARD" -- "${args[@]}" > "$f" 2>&1; LAST_RC=$?
  else hold10 "$HEATER" "${args[@]}" > "$f" 2>&1; LAST_RC=$?; fi
  L_TE=$(now_ms); LAST_END=$L_TE
  oh_record_launch "$kind" "$kind" SPARSITY "$f" "\"mask\":\"$mask\",\"per_shire\":$per,\"seconds\":$secs"
  if [ "$LAST_RC" -ne 0 ]; then
    HEAT_FAILS=$(( ${HEAT_FAILS:-0} + 1 )); [ "$HEAT_FAILS" -ge 3 ] && oh_abort 1 "heater failed 3 times in a row"
  else HEAT_FAILS=0; fi
  return 0
}
# the heater's mask for the current die temperature: ALL32, or ALL24 above all24_above_c (card 1's board power)
oh_heat_per() { if [ "$ST_MEAN" != - ] && [ "$ST_MEAN" -ge "$P_all24_above_c" ]; then echo "$P_heat_all24"; else echo "$P_heat_all32"; fi; }

# ---- one checked process (battery kernel or memprobe program): oh_kernel <name> <tool> <args...>; sets KSTAT
oh_kernel() {
  local name=$1 tool=$2; shift 2
  local f bin
  SEQ=$(( SEQ + 1 )); f=$OUT/k/$(printf %04d "$SEQ")-$name.out
  L_MEAN0=$ST_MEAN; L_HIGH0=$ST_HIGH
  L_TS=$(now_ms)
  if dry; then
    "${OHPY[@]}" dry-kernel --card "$CARD" --name "$name" --tool "$tool" -- "$@" > "$f" 2>&1; LAST_RC=$?
  else
    case "$tool" in
      SPARSITY) hold10 "$HEATER" "$@" --kernel "$HEATER_KERNEL_ABS" > "$f" 2>&1; LAST_RC=$? ;;
      ONCHIP)   hold10 "$ONCHIP" "$@" > "$f" 2>&1; LAST_RC=$? ;;
      MMB)      ( cd "$OUT/run" && hold10 "$MMB_LAUNCHER" -k "$MMB_KERNEL" -d silicon "$@" ) > "$f" 2>&1; LAST_RC=$?
                find "$OUT/run" -mindepth 1 -delete 2>/dev/null ;;   # the launcher's 8 MB trace dump
      MEMPROBE) hold10 "$MEMPROBE" "$@" --budget 8 > "$f" 2>&1; LAST_RC=$? ;;
      *) oh_abort 1 "unknown tool $tool" ;;
    esac
  fi
  L_TE=$(now_ms); LAST_END=$L_TE
  read -r KSTAT KN KWHY <<< "$("${OHPY[@]}" kcheck --file "$f" --tool "$tool")"
  oh_record_launch "${KKIND:-check}" "$name" "$tool" "$f" "\"status\":\"$KSTAT\",\"n_checked\":$KN,\"why\":\"$KWHY\",\"attempt\":${KATTEMPT:-1},\"role\":\"${KROLE:-battery}\""
  return 0
}

# ---- one run's sampler and watcher
RUN_ID=; RUN_TEL=; RUN_STATE=; RUN_CTL=; RUN_SF=
ST_MEAN=-; ST_HIGH=-
oh_run_begin() {   # oh_run_begin <run id>
  RUN_ID=$1; RUN_TEL=$OUT/tel-$1.jsonl; RUN_STATE=$OUT/.state-$1; RUN_CTL=$OUT/.ctl-$1; RUN_SF=$OUT/.stop-$1
  rm -f "$RUN_SF" "$RUN_STATE"; : > "$RUN_CTL"
  oh_guard_refresh
  start_sampler "$RUN_TEL" 3600 --reset-ms "$P_reset_ms" || oh_abort 1 "sampler did not start (run $1)"
  "${OHPY[@]}" watch --tel "$RUN_TEL.raw" --state "$RUN_STATE" --ctl "$RUN_CTL" --stop-file "$RUN_SF" \
    --session-stop "$SESSION_STOP" --guard "${GUARD_RAW:-}" 8>&- 9>&- &
  WATCH_PID=$!
  local i; for i in $(seq 1 200); do oh_state && [ "$ST_N" != - ] && [ "$ST_N" -ge 1 ] && break; sleep 0.05; done
  oh_state || oh_abort 1 "the watcher saw no sample (run $1)"
  kill -0 "$WATCH_PID" 2>/dev/null || oh_abort 1 "the watcher did not start (run $1)"
  NS=0; local n; for i in 1 2 3; do n=$(modcount); [ -n "$n" ] && [ "$n" -gt "$NS" ] && NS=$n; done
  [ "$MODCHECK" = on ] || NS=
  mark run_begin "\"run\":\"$1\",\"mean\":$(jnum "$ST_MEAN"),\"high\":$(jnum "$ST_HIGH")"
  return 0
}
oh_run_end_quiet() {
  if [ -n "${WATCH_PID:-}" ]; then
    echo quit >> "$RUN_CTL" 2>/dev/null
    local i; for i in $(seq 1 40); do kill -0 "$WATCH_PID" 2>/dev/null || break; sleep 0.05; done
    kill "$WATCH_PID" 2>/dev/null; wait "$WATCH_PID" 2>/dev/null; WATCH_PID=
  fi
  stop_sampler
}
oh_run_end() { mark run_end "\"run\":\"$RUN_ID\",\"mean\":$(jnum "$ST_MEAN"),\"high\":$(jnum "$ST_HIGH")"; oh_run_end_quiet; }
oh_state() {
  local l; l=$(cat "$RUN_STATE" 2>/dev/null) || return 1
  read -r ST_T ST_MEAN ST_HIGH ST_W ST_MHZ ST_N ST_HARD ST_SOFT ST_TGT ST_AGE ST_GMEAN ST_GAGE ST_WALL ST_IO ST_TGTHIT <<< "$l"
  [ -n "${ST_T:-}" ] && [ "$ST_T" != - ]
}
oh_live() {   # 0 normally; aborts on a hard stop, a stale or dead watcher or sampler
  if [ -n "${WATCH_PID:-}" ] && ! kill -0 "$WATCH_PID" 2>/dev/null; then oh_abort 1 "the run's watcher is gone"; fi
  oh_state || oh_abort 1 "watcher state missing"
  if [ -n "${ST_WALL:-}" ] && [ "$ST_WALL" != - ] && [ $(( $(date +%s%3N) - ST_WALL )) -gt $(( P_sampler_stale_s * 1000 )) ]; then
    oh_abort 1 "the watcher's state is stale (> ${P_sampler_stale_s} s)"
  fi
  if [ "$ST_HARD" != - ] && [ -f "$RUN_STATE.hard" ]; then mark hard_trigger "\"reading\":$(head -n 1 "$RUN_STATE.hard")"; fi
  case "$ST_HARD" in
    ABS88) oh_abort 1 "a die reading reached ${P_abs_stop_c} C ($(head -c 200 "$RUN_STATE.hard" 2>/dev/null | tr -d '"{}')): block and session stopped" session ;;
    HARDW) oh_abort 1 "board power reached ${P_hard_board_w} W ($ST_W): block and session stopped" session ;;
    GUARD90|GUARD_STALE) oh_abort 1 "card-0 guard stop: $ST_HARD (card 0 mean $ST_GMEAN, age $ST_GAGE s)" session ;;
  esac
  if [ "$ST_AGE" != - ] && [ "$ST_AGE" -gt $(( P_sampler_stale_s * 1000 )) ]; then oh_abort 1 "sampler output stale for ${ST_AGE} ms"; fi
  return 0
}
oh_wait_s() {   # idle with the sampler on for <s> seconds (live checks; the other-user check every 5 s)
  local end=$(( $(now_ms) + $1 * 1000 ))
  while [ "$(now_ms)" -lt "$end" ]; do
    oh_live
    [ $(( $(now_ms) - ${LAST_BETWEEN:-0} )) -ge 5000 ] && oh_between
    oh_sleep 0.2
  done
}

# ---- heat to a target mean with 2 s heater launches (the watcher stops each launch at the target or a soft cap);
# oh_heat_to <target C> <max seconds> [per_shire]; HEAT_WHY = target | soft | time
# Amendment 1 (28 Sep, 10:33 PDT): the target counts as reached once ANY sample read the mean at or above it (the
# watcher's sticky tgt_hit). Before, the loop re-read the mean after the heater had stopped at the target, found it one
# degree lower (whole-degree readings) and launched again, holding the die at the target until the time cap.
oh_heat_to() {
  local target=$1 maxs=$2 per=${3:-} t0 soft_since=
  t0=$(now_ms); HEAT_WHY=time; HEAT_N=0; HEAT_MAX=0
  echo "target $target" >> "$RUN_CTL"
  oh_sleep 0.15
  while [ $(( $(now_ms) - t0 )) -lt $(( maxs * 1000 )) ]; do
    oh_live
    [ "$ST_MEAN" -gt "$HEAT_MAX" ] && HEAT_MAX=$ST_MEAN
    if [ "$ST_MEAN" -ge "$target" ] || [ "${ST_TGTHIT:-0}" = 1 ]; then HEAT_WHY=target; break; fi
    if [ "$ST_SOFT" != - ]; then
      [ -z "$soft_since" ] && soft_since=$(now_ms)
      if [ $(( $(now_ms) - soft_since )) -ge 30000 ]; then HEAT_WHY=soft; break; fi
      [ $(( $(now_ms) - ${LAST_BETWEEN:-0} )) -ge 5000 ] && oh_between
      oh_sleep 0.2; continue
    fi
    soft_since=
    oh_admit $(( P_heat_s + 2 ))
    oh_live
    { [ "$ST_MEAN" -ge "$target" ] || [ "${ST_TGTHIT:-0}" = 1 ]; } && { HEAT_WHY=target; break; }
    [ "$ST_SOFT" != - ] && continue
    oh_between
    rm -f "$RUN_SF"
    oh_heat_launch heat "$P_heat_mask" "${per:-$(oh_heat_per)}" "$P_heat_s"
    HEAT_N=$(( HEAT_N + 1 ))
    oh_state && [ "$ST_MEAN" != - ] && [ "$ST_MEAN" -gt "$HEAT_MAX" ] && HEAT_MAX=$ST_MEAN
    oh_sleep 0.3
  done
  echo "target off" >> "$RUN_CTL"
  oh_sleep 0.15; oh_live
  mark heat "\"target\":$target,\"why\":\"$HEAT_WHY\",\"launches\":$HEAT_N,\"mean\":$(jnum "$ST_MEAN"),\"high\":$(jnum "$ST_HIGH")"
}
