# DV2 (DESIGN.md rev 2, PREREG-DEV.md; 27 Sep 2026): the shell helpers of dv2/block.sh. Source it after ../lib.sh
# (which cd's to the tree root and sets CARD, HEATER, DATA_ROOT, the lock helpers and the V3_DRY stubs). Most of it is
# a copy of tools/claims-v3/hp/hplib.sh (the per-run sampler and watcher, the caps, the falling edge, the launch
# record, the SP log level's O2 handling, the probe, the dry simulator hooks), with the card-0 guard removed (DV2 runs
# only on aifoundry2) and DV2's additions: the one-shot statistics reset, the stop 2 s after the first 700 MHz sample,
# the C1m target stop, the gate before every run (et-who included), the post-run clock check with ABORT-LATCH, the dump
# scan for the governor's error lines, the night-stop files and the alerts.
#
# The owner's rules it enforces: et-who, who and the process scan before the session, before every run and between
# launches; the card lock (lib block_begin, fd 9) held for the whole session; every device process under hold10
# (timeout 10); chains <= 3 x 7 s (C1m) and lifts + launch <= 4 x 7 + 8 s (T-runs), all inside 150 s; stop at 90 C
# (the watcher: the heater's stop file, the block aborts, the queue and the night stop); no reset, no global-state
# change but the O2 log level (set only after an ALIVE probe, restored and checked); samplers stopped with SIGTERM.
set -u
case "${CARD:-}" in
  aifoundry2) ;;
  aifoundry1-c0) echo "dv2: aifoundry1 card 0 is never used (owner decision): refused" >&2; exit 2 ;;
  *) echo "dv2: block.sh runs on aifoundry2 only (this is ${CARD:-?}); aifoundry3's Z2 is dv2/z2.sh: refused" >&2; exit 2 ;;
esac
DV2_DIR=${DV2_DIR:-tools/claims-v3/dv2}
DV2PY=(python3 "$DV2_DIR/dv2lib.py")
dry() { [ -n "${V3_DRY:-}" ]; }

# ---- binaries (this tree's own builds, README.md): ettelem-dv2 for every management call and the sampler; lib.sh's
# aifoundry2 heater (build/sparsity_t2). DV2_ETTELEM / DV2_HEATER are honoured under V3_DRY only (envcheck).
ETTELEM=${DV2_ETTELEM:-build/ettelem-dv2/ettelem}
HEATER=${DV2_HEATER:-$HEATER}
HEATER_KERNEL=$(dirname "$HEATER")/../kernel/sparsity.elf
case "$HEATER_KERNEL" in /*) HEATER_KERNEL_ABS=$HEATER_KERNEL ;; *) HEATER_KERNEL_ABS=$V3_ROOT/$HEATER_KERNEL ;; esac
SESSION_STOP=$V3_ROOT/build/claims-v3/STOP          # queue.sh stops at the next block boundary when it exists
if [ -n "${DV2_VAL:-}" ]; then DV2_DATA=$DATA_ROOT/dv2v   # PREREG-VAL's frozen replication (dv2v/block.sh starts it)
else DV2_DATA=$DATA_ROOT/dv2; fi                     # every DV2 file of this card (the pass directories, the flags)

# ---- V3_DRY=1: the accelerated simulation (dv2lib.py dry-*) instead of the card
if dry; then
  export HP_DRY_SPEED=${HP_DRY_SPEED:-40}
  export HP_DRY_CARD=$CARD
  export HP_DRY_DIR=${HP_DRY_DIR:-$V3_ROOT/build/claims-v3-dry/dv2-sim}
  mkdir -p "$HP_DRY_DIR"
  if [ -z "${HP_VT0:-}" ]; then [ -s "$HP_DRY_DIR/vt0" ] || date +%s%3N > "$HP_DRY_DIR/vt0"; HP_VT0=$(cat "$HP_DRY_DIR/vt0"); fi
  export HP_VT0
  SESSION_STOP=$V3_ROOT/build/claims-v3-dry/STOP
  now_ms() { local r; r=$(date +%s%3N); echo $(( HP_VT0 + (r - HP_VT0) * HP_DRY_SPEED )); }
  dv2_sleep() { sleep "$(awk -v s="$1" -v k="$HP_DRY_SPEED" 'BEGIN{printf "%.3f", s / k}')"; }
  die_c() { "${DV2PY[@]}" dry-die --card "$CARD"; }
  start_sampler() {   # lib's interface: start_sampler <out> <secs> [--reset-ms R | --reset-once-file F]
    local out=$1 secs=$2; shift 2
    local extra=()
    [ "${1:-}" = --reset-ms ] && extra=(--reset-ms "$2")
    [ "${1:-}" = --reset-once-file ] && extra=(--reset-once-file "$2")
    "${DV2PY[@]}" dry-sampler --card "$CARD" --out "$out.raw" --seconds "$secs" --every-ms 100 "${extra[@]}" &
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
  # test hook (dry only): an intrusion appears when this file exists (the foreign-user paths)
  others_present() { [ -e "$HP_DRY_DIR/intrude" ] && { log "others present (dry hook $HP_DRY_DIR/intrude)"; return 0; }; return 1; }
  clock_mhz() { local f; f=$(mktemp); "${DV2PY[@]}" dry-sampler --card "$CARD" --out "$f" --seconds 1 --every-ms 500;
                sed -n 's/.*"minion":\([0-9]*\).*/\1/p' "$f" | tail -1; rm -f "$f"; }
else
  dv2_sleep() { sleep "$1"; }
fi
# lib's start_sampler with fds 8 and 9 (the card lock) closed for the sampler it starts (hp review F14)
eval "dv2_lib_start_sampler() $(declare -f start_sampler | tail -n +2)"
start_sampler() { dv2_lib_start_sampler "$@" 8>&- 9>&-; }

# ---- small helpers
jnum() { [ -z "${1:-}" ] || [ "$1" = - ] && echo null || echo "$1"; }
jstr() { python3 -c 'import json,sys; print(json.dumps(sys.argv[1]))' "${1:-}"; }
mark() {  # mark <event> [extra JSON fields, already formatted]
  local extra=${2:-}; [ -n "$extra" ] && extra=",$extra"
  echo "{\"t_ms\":$(now_ms),\"ev\":\"$1\"$extra}" >> "$OUT/marks.jsonl"
}
devlog() {  # devlog <decision> <JSON fields>: PREREG-DEV's decision log (every DEV-n and DEVIATION, with its data)
  mkdir -p "$DV2_DATA"
  echo "{\"t_ms\":$(now_ms),\"pass\":${PASS:-null},\"decision\":\"$1\"${2:+,$2}}" >> "$DV2_DATA/dev-log.jsonl"
}
eval "dv2_lib_die_c() $(declare -f die_c | tail -n +2)"
die_c() { local t=; [ -n "${NO_CARD:-}" ] || t=$(dv2_lib_die_c); echo "${t:-null}"; }
modcount() { if dry; then echo 0; else lsmod 2>/dev/null | awk '$1=="et_soc1"{print $3}'; fi; }

# device processes on this card other than our sampler: ours (any) and other users' (idle/block.sh's scan)
foreign_procs() {
  dry && return 0
  ps -eo uid=,pid=,comm= |
    awk -v me="$(id -u)" -v dev="$DEV_COMM" -v oth="$OTHER_COMM" -v sp="${SAMPLER_PID:-0}" \
      '$2 != sp && (($1 == me && $3 ~ dev) || ($1 != me && $3 ~ oth)) {printf "%s:%s:%s ", $1, $2, $3}'
}
# et-who (et-holders): any holder of a device node or of the card lock that is not this user
etwho_foreign() {
  if dry; then [ -e "$HP_DRY_DIR/intrude-etwho" ] && echo "dry-holder"; return 0; fi
  command -v et-who > /dev/null || { echo "et-who-missing"; return 0; }
  timeout 20 et-who 8>&- 9>&- 2>/dev/null | awk -v me="$USER" '$1 ~ /^\/dev\/et|^lock:/ && $2 != me && $2 != "" {printf "%s:%s:%s ", $1, $2, $3}'
}
# another queue or block of the framework on this host (not our own queue.sh ancestor): hp, a2, V3, a second dv2
# Only shells running a framework script count (a 'grep' or an editor on those paths does not), and a V3_DRY process
# (a dry test, which touches no device) does not; under V3_DRY the test hook $HP_DRY_DIR/intrude-framework stands in.
other_framework() {   # prints "pid:args" of each; our own ancestors (our queue.sh) and descendants do not count
  local anc=" " p=$$ pid q mine
  if dry; then [ -e "$HP_DRY_DIR/intrude-framework" ] && echo "0:dry-framework-hook"; return 0; fi
  while [ -n "$p" ] && [ "$p" -gt 1 ]; do anc="$anc$p "; p=$(ps -o ppid= -p "$p" 2>/dev/null | tr -d ' '); done
  for pid in $(ps -u "$(id -u)" -o pid=,args= | awk '$2 ~ /^(\/[^ ]*\/)?(ba)?sh$/ && $3 ~ /tools\/claims-v3\/(queue\.sh|[a-z0-9_\/]+\/block\.sh|hp\/probe\.sh|hp\/run_[a-z0-9_]+\.sh|dv2\/z2\.sh)$/ {print $1}'); do
    case "$anc" in *" $pid "*) continue ;; esac
    tr '\0' '\n' < "/proc/$pid/environ" 2>/dev/null | grep -q '^V3_DRY=.' && continue
    mine=; q=$pid
    while [ -n "$q" ] && [ "$q" -gt 1 ]; do [ "$q" = "$$" ] && { mine=1; break; }; q=$(ps -o ppid= -p "$q" 2>/dev/null | tr -d ' '); done
    [ -n "$mine" ] && continue
    kill -0 "$pid" 2>/dev/null || continue
    echo "$pid:$(ps -o args= -p "$pid" 2>/dev/null | cut -c1-80)"
  done
}

# ---- the night's stop files and alerts (PREREG-DEV §4 "The night stops"): NIGHT-STOP stops every DV2 pass
night_stopped() { [ -e "$DV2_DATA/NIGHT-STOP" ]; }
dv2_alert() {  # dv2_alert <KIND> <why> [nostop]: ALERT-<KIND>.json for the orchestrator; the night and queue stop
  mkdir -p "$DV2_DATA"
  python3 -c 'import json,sys,time; json.dump({"kind": sys.argv[1], "why": sys.argv[2], "pass": sys.argv[3], "t_ms": int(time.time()*1000),
    "dry": sys.argv[4] == "1"}, open(sys.argv[5], "w"), indent=1)' "$1" "$2" "${PASS:-}" "$(dry && echo 1 || echo 0)" "$DV2_DATA/ALERT-$1.json"
  if [ "${3:-}" = nostop ]; then log "dv2: ALERT-$1: $2 (alert only)"
  else
    echo "ALERT-$1 pass ${PASS:-} $(date +%FT%T): $2" >> "$DV2_DATA/NIGHT-STOP"
    touch "$SESSION_STOP"
    log "dv2: ALERT-$1: $2 (the night stops: no further DV2 card work until the owner replies)"
  fi
  [ -n "${OUT:-}" ] && [ -f "$OUT/marks.jsonl" ] && mark alert "\"kind\":\"$1\",\"why\":$(jstr "$2")"
  return 0
}

# ---- abort and cleanup. Exit 3 = someone else on the card: leave it at once (the level is restored by the next pass)
WATCH_PID=; LEVEL_SET=; LEVEL_FOUND=; LEVEL_ORIG=; NO_CARD=
dv2_abort() {  # dv2_abort <exit code> <note>
  mark abort "\"why\":$(jstr "$2"),\"code\":$1"
  [ "$1" = 3 ] && NO_CARD=1
  dv2_run_end_quiet
  [ -z "$NO_CARD" ] && dv2_level_restore
  dv2_gzip_all
  declare -F dv2_on_abort > /dev/null && dv2_on_abort "$1" "$2"
  block_end fail "$2"
  exit "$1"
}
dv2_abort_latch() {  # ABORT-LATCH (DESIGN §4.4, R6): stop all heat, end the session, alert; never reset
  dv2_alert LATCH "$1"
  dv2_abort 1 "ABORT-LATCH: $1"
}
dv2_gzip_all() {
  local f
  for f in "$OUT"/tel-*.jsonl "$OUT"/heater-*.out; do [ -f "$f" ] && gzip -f "$f"; done
  rm -f "$OUT"/.state-* "$OUT"/.ctl-* "$OUT"/.stop-* "$OUT"/.reset-* 2>/dev/null
}
dv2_cleanup() {  # EXIT trap
  dv2_run_end_quiet
  [ -z "$NO_CARD" ] && dv2_level_restore
}

# ---- device calls other than the heater (each a device process under hold10)
dv2_sptrace() {   # dv2_sptrace <out.bin>
  if dry; then "${DV2PY[@]}" dry-sptrace --card "$CARD" --out "$1" >> "$OUT/mgmt.log" 2>&1
  else hold10 "$ETTELEM" sptrace "$1" >> "$OUT/mgmt.log" 2>&1; fi
}
dv2_config() {    # dv2_config <out.json>
  if dry; then "${DV2PY[@]}" dry-config --card "$CARD" > "$1" 2>> "$OUT/mgmt.log"
  else hold10 "$ETTELEM" config > "$1" 2>> "$OUT/mgmt.log"; fi
}
dv2_loglevel() {  # dv2_loglevel warning|info|debug
  if dry; then "${DV2PY[@]}" dry-loglevel --card "$CARD" --level "$1" >> "$OUT/mgmt.log" 2>&1
  else hold10 "$ETTELEM" loglevel "$1" >> "$OUT/mgmt.log" 2>&1; fi
}
dv2_z2() {        # dv2_z2 <prefix>: residency (raw states 2-6) and uptime, read-only (Z2)
  if dry; then "${DV2PY[@]}" dry-residency 2 3 4 5 6 > "$1-residency.jsonl" 2>> "$OUT/mgmt.log"
               "${DV2PY[@]}" dry-uptime > "$1-uptime.jsonl" 2>> "$OUT/mgmt.log"
  else hold10 "$ETTELEM" residency 2 3 4 5 6 > "$1-residency.jsonl" 2>> "$OUT/mgmt.log"
       hold10 "$ETTELEM" uptime > "$1-uptime.jsonl" 2>> "$OUT/mgmt.log"; fi
}
# every dump is scanned for the governor's error lines, against the previous dump of this card (the night stops on one)
DV2_LASTDUMP=$DV2_DATA/last-dump.bin
dv2_dumpcheck() {   # dv2_dumpcheck <dump.bin>
  [ -s "$1" ] || { mark dumpcheck "\"dump\":\"${1##*/}\",\"ok\":null,\"why\":\"no dump\""; return 0; }
  local out rc=0
  if [ -s "$DV2_LASTDUMP" ]; then out=$("${DV2PY[@]}" dumpcheck --dump "$1" --prev "$DV2_LASTDUMP") || rc=$?
  else out=$("${DV2PY[@]}" dumpcheck --dump "$1") || rc=$?; fi
  mark dumpcheck "\"dump\":\"${1##*/}\",\"rc\":$rc,\"why\":$(jstr "$out")"
  cp -f "$1" "$DV2_LASTDUMP"
  if [ "$rc" = 1 ]; then dv2_alert FAILLINE "$out (${1##*/})"; return 1; fi
  return 0
}

# ---- the SP log level (O2; hp/hplib.sh's code, the state in $DV2_DATA/sp-level.json)
LEVEL_STATE=$DV2_DATA/sp-level.json
dv2_level_infer() {   # <prev.bin> <cur.bin> [--begin]
  if [ -s "$1" ] && [ -s "$2" ]; then python3 "$DV2_DIR/sptrace_events.py" level-since "$1" "$2" ${3:-} 2>/dev/null || echo UNKNOWN
  else echo UNKNOWN; fi
}
dv2_level_dumps() { rm -f "$OUT/$1-0.bin" "$OUT/$1.bin"; dv2_sptrace "$OUT/$1-0.bin"; dv2_sptrace "$OUT/$1.bin"; }
dv2_level_begin() {   # dv2_level_begin <dump-name>: WARNING only after an ALIVE probe (O2); sets SPLINES= when not set
  case "${PROBE_CLASS:-}" in
    ALIVE|ALIVE_CANDIDATE) ;;
    *) SPLINES=; mark level_refused "\"probe_class\":\"${PROBE_CLASS:-}\""; return 0 ;;
  esac
  if [ -n "${DV2_NO_WARNING:-}" ]; then SPLINES=; mark level_refused "\"why\":\"DV2_NO_WARNING (the owner said no to O2)\""; return 0; fi
  mkdir -p "$(dirname "$LEVEL_STATE")"
  dv2_level_dumps "$1"
  LEVEL_FOUND=$(dv2_level_infer "$OUT/$1-0.bin" "$OUT/$1.bin" --begin)
  local LV_ACTION LV_ORIG LV_WHY
  eval "$("${DV2PY[@]}" level-begin --state "$LEVEL_STATE" --found "$LEVEL_FOUND" --block "$PASS")"
  mark level_found "\"level\":\"$LEVEL_FOUND\",\"action\":\"$LV_ACTION\",\"original\":\"$LV_ORIG\",\"why\":$(jstr "$LV_WHY")"
  case "$LV_ACTION" in
    set)
      LEVEL_ORIG=$LV_ORIG
      "${DV2PY[@]}" level-mark --state "$LEVEL_STATE" --block "$PASS" --pending 1 > /dev/null
      LEVEL_SET=1                                   # before the command: a set that times out is still restored
      local rc=0; dv2_loglevel warning || rc=$?
      mark level_set "\"level\":\"WARNING\",\"rc\":$rc,\"restore_to\":\"$LEVEL_ORIG\"" ;;
    none) LEVEL_ORIG= ;;
    *) LEVEL_ORIG=; SPLINES=; mark level_skipped "\"why\":$(jstr "$LV_WHY")" ;;
  esac
}
dv2_level_check() {
  local want=$1 got
  dv2_level_dumps sp-level-check
  got=$(dv2_level_infer "$OUT/sp-level-check-0.bin" "$OUT/sp-level-check.bin")
  "${DV2PY[@]}" level-mark --state "$LEVEL_STATE" --block "$PASS" --checked "$got" > /dev/null
  mark level_check "\"want\":\"$want\",\"got\":\"$got\",\"ok\":$([ "$got" = "$want" ] && echo true || echo false)"
  if [ "$got" = "$want" ]; then LEVEL_CHECK="SP level restored to $want (checked)"
  else LEVEL_CHECK="SP level NOT restored: $got, want $want (pending: the next session restores it)"; fi
  log "$LEVEL_CHECK"
}
dv2_level_restore() {
  [ -n "$LEVEL_SET" ] || return 0
  local lv
  case "$LEVEL_ORIG" in INFO) lv=info ;; DEBUG) lv=debug ;; *) mark level_restore_skipped "\"original\":\"$LEVEL_ORIG\""; LEVEL_SET=; return 0 ;; esac
  local rc=0; dv2_loglevel "$lv" || rc=$?
  LEVEL_SET=
  mark level_restored "\"level\":\"$lv\",\"rc\":$rc"
  dv2_level_check "$LEVEL_ORIG"
}
dv2_level_pending_restore() {
  [ -f "$LEVEL_STATE" ] || return 0
  local LV_PENDING LV_ORIG
  eval "$("${DV2PY[@]}" level-show --state "$LEVEL_STATE")"
  [ -n "$LV_PENDING" ] || return 0
  case "$LV_ORIG" in INFO|DEBUG) ;; *) mark level_pending_unknown "\"original\":\"$LV_ORIG\""; return 0 ;; esac
  mark level_pending "\"original\":\"$LV_ORIG\""
  LEVEL_SET=1; LEVEL_ORIG=$LV_ORIG
  dv2_level_restore
}

# ---- the gate (before the session, before every run, between launches): another user, a foreign device process,
# a foreign holder in et-who, the et_soc1 use count, another framework queue or block; any of them ends the session
NS=
dv2_gate() {   # dv2_gate <when>: exit 3 (the card is left at once) on anything foreign
  others_present && dv2_abort 3 "another user or device process present ($1)"
  local fp; fp=$(foreign_procs)
  [ -n "${fp// /}" ] && dv2_abort 3 "device process on the card ($1): $fp"
  local ew; ew=$(etwho_foreign)
  [ -n "${ew// /}" ] && dv2_abort 3 "et-who shows a foreign holder ($1): $ew"
  local n; n=$(modcount)
  if [ -n "$n" ]; then
    if [ -n "${SAMPLER_PID:-}" ]; then [ -n "$NS" ] && [ "$n" -gt "$NS" ] && dv2_abort 3 "et_soc1 use count $n > $NS ($1)"
    else [ "$n" != 0 ] && dv2_abort 3 "et_soc1 use count $n with no process of ours ($1)"; fi
  fi
  local of; of=$(other_framework)
  [ -n "$of" ] && dv2_abort 3 "another queue or block of the framework runs ($1): $of"
  night_stopped && dv2_abort 1 "the night stop is set ($1): $(tail -1 "$DV2_DATA/NIGHT-STOP")"
  return 0
}

# ---- one heater process: dv2_launch <run> <kind> <mask> <per_shire> <seconds> [stop-file]; sets LAST_RC, L_TS, L_TE
dv2_launch() {
  local run=$1 kind=$2 mask=$3 per=$4 secs=$5 sf=${6:-} lg
  lg=$OUT/heater-$run.out
  case "$kind" in lift|preheat) lg=$OUT/heater-$run-pre.out ;; esac     # the measured process alone in heater-<run>.out
  local args=(--test fma --type fp32 --pattern none --values randn --shires "$mask" --per-shire "$per" --seconds "$secs" --seed 1
              --kernel "$HEATER_KERNEL_ABS")
  [ -n "$sf" ] && args+=(--stop-file "$sf")
  L_TS=$(now_ms)
  if dry; then "${DV2PY[@]}" dry-heater --card "$CARD" -- "${args[@]}" >> "$lg" 2>&1; LAST_RC=$?
  else hold10 "$HEATER" "${args[@]}" >> "$lg" 2>&1; LAST_RC=$?; fi
  L_TE=$(now_ms)
  echo "{\"run\":\"$run\",\"kind\":\"$kind\",\"mask\":\"$mask\",\"per_shire\":$per,\"seconds\":$secs,\"t_start_ms\":$L_TS,\"t_end_ms\":$L_TE,\"wall_s\":$(awk -v a="$L_TS" -v b="$L_TE" 'BEGIN{printf "%.3f", (b-a)/1000}'),\"rc\":$LAST_RC}" >> "$OUT/launches.jsonl"
  return $LAST_RC
}

# ---- one run's sampler and watcher. Modes: once (--reset-once-file: T, ADD, C1m, the smoke), periodic (--reset-ms
# 1000: RST, DEV-12), none (no reset)
RUN_ID=; RUN_TEL=; RUN_STATE=; RUN_CTL=; RUN_SF=; RUN_RF=
dv2_run_begin() {   # dv2_run_begin <run id> <once|periodic|none>
  RUN_ID=$1; RUN_TEL=$OUT/tel-$1.jsonl; RUN_STATE=$OUT/.state-$1; RUN_CTL=$OUT/.ctl-$1; RUN_SF=$OUT/.stop-$1; RUN_RF=$OUT/.reset-$1
  rm -f "$RUN_SF" "$RUN_STATE" "$RUN_RF"; : > "$RUN_CTL"
  local mode=()
  case "$2" in once) mode=(--reset-once-file "$RUN_RF") ;; periodic) mode=(--reset-ms 1000) ;; none) ;; esac
  start_sampler "$RUN_TEL" 900 "${mode[@]}" || dv2_abort 1 "sampler did not start (run $1)"
  local caps="abs_stop_c=$P_abs_stop_c,cap_mean_c=$P_cap_mean_c,cap_high_c=$P_cap_high_c,cap_board_w=$P_cap_board_w"
  caps+=",cap_consecutive=$P_cap_consecutive"
  "${DV2PY[@]}" watch --tel "$RUN_TEL.raw" --state "$RUN_STATE" --ctl "$RUN_CTL" --stop-file "$RUN_SF" \
    --reset-file "$RUN_RF" --session-stop "$SESSION_STOP" --caps "$caps" 8>&- 9>&- &
  WATCH_PID=$!
  local i; for i in $(seq 1 200); do dv2_state && [ "$ST_N" != - ] && [ "$ST_N" -ge 1 ] && break; sleep 0.05; done
  dv2_state || dv2_abort 1 "the watcher saw no sample (run $1)"
  kill -0 "$WATCH_PID" 2>/dev/null || dv2_abort 1 "the watcher did not start (run $1)"
  NS=0; local n; for i in 1 2 3; do n=$(modcount); [ -n "$n" ] && [ "$n" -gt "$NS" ] && NS=$n; done
  return 0
}
dv2_run_end_quiet() {
  if [ -n "${WATCH_PID:-}" ]; then
    echo quit >> "$RUN_CTL" 2>/dev/null
    local i; for i in $(seq 1 40); do kill -0 "$WATCH_PID" 2>/dev/null || break; sleep 0.05; done
    kill "$WATCH_PID" 2>/dev/null; wait "$WATCH_PID" 2>/dev/null; WATCH_PID=
  fi
  stop_sampler
}
dv2_state() {   # the watcher's newest state line into ST_*
  local l; l=$(cat "$RUN_STATE" 2>/dev/null) || return 1
  read -r ST_T ST_MEAN ST_HIGH ST_W ST_MHZ ST_N ST_STOP ST_EDGE ST_TAUC ST_S1 ST_AGE ST_RESETS ST_T700 ST_PLANSTOP ST_TARGET ST_RTOUCH ST_WALL <<< "$l"
  [ -n "${ST_T:-}" ] && [ "$ST_T" != - ]
}
# the live checks: the watcher alive and fresh (real clock), a sticky safety stop, a stale sampler
dv2_live() {   # 0 normally, 1 on a run stop (RUN_STOP set); aborts on ABS90/stale/watcher gone
  if [ -n "${WATCH_PID:-}" ] && ! kill -0 "$WATCH_PID" 2>/dev/null; then
    dv2_abort 1 "the run's watcher (pid $WATCH_PID) is gone: no safety stops without it"
  fi
  dv2_state || dv2_abort 1 "watcher state missing"
  if [ -n "${ST_WALL:-}" ] && [ "$ST_WALL" != - ] && [ $(( $(date +%s%3N) - ST_WALL )) -gt $(( P_sampler_stale_s * 1000 )) ]; then
    dv2_abort 1 "the watcher's state is $(( $(date +%s%3N) - ST_WALL )) ms old: watcher stalled"
  fi
  case "$ST_STOP" in
    ABS90) dv2_alert ABS90 "a die reading reached ${P_abs_stop_c} C (run $RUN_ID)"; dv2_abort 1 "a die reading reached ${P_abs_stop_c} C: session and night stopped" ;;
    -) ;;
    *) RUN_STOP=$ST_STOP; return 1 ;;
  esac
  if [ "$ST_AGE" != - ] && [ "$ST_AGE" -gt $(( P_sampler_stale_s * 1000 )) ]; then
    dv2_abort 1 "sampler output stale for ${ST_AGE} ms"
  fi
  return 0
}

# ---- lifts / preheat to a target mean (T-runs: 7 s UNI32@4 launches, <= 4; C1m: 2 s ALL24 bursts, <= 30)
dv2_lift() {   # dv2_lift <target C> <mask> <per> <seconds> <max>; sets LIFTS, LIFT_WHY
  local target=$1 m=$2 p=$3 s=$4 mx=$5 fails=0
  LIFTS=0; LIFT_WHY=target
  while :; do
    dv2_live || { LIFT_WHY=stop; return 1; }
    [ "$ST_MEAN" -ge "$target" ] && return 0
    [ "$LIFTS" -ge "$mx" ] && { LIFT_WHY=max; return 1; }
    if [ -n "${LIFT_REQUIRE_600:-}" ] && [ "$ST_MHZ" != 600 ]; then LIFT_WHY=offclock; return 1; fi   # C1m: 600 MHz only
    dv2_gate "between launches"
    [ -e "$RUN_SF" ] && { LIFT_WHY=stopfile; return 1; }
    dv2_launch "$RUN_ID" lift "$m" "$p" "$s" "$RUN_SF"
    if [ "$LAST_RC" -ne 0 ]; then fails=$(( fails + 1 )); [ "$fails" -ge 3 ] && dv2_abort 1 "3 heater failures in the lifts"; else fails=0; fi
    LIFTS=$(( LIFTS + 1 ))
    dv2_sleep "$P_gap_between_launches_s"
  done
}

# ---- the falling S+1 -> S edge (the watcher's rule; the one-shot reset at S+1); sets EDGE_T, EDGE_TAUC, EDGE_S1, EDGE_OK
dv2_edge_wait() {   # dv2_edge_wait <S> <cap s>
  local S=$1 cap=$2 t0 last_chk
  t0=$(now_ms); last_chk=$t0
  echo "edge $S $t0" >> "$RUN_CTL"
  EDGE_OK=; EDGE_T=; EDGE_TAUC=; EDGE_S1=; EDGE_WAIT_S=
  while :; do
    dv2_live || return 1
    if [ "$ST_EDGE" != - ]; then EDGE_OK=1; EDGE_T=$ST_EDGE; EDGE_TAUC=$ST_TAUC; EDGE_S1=$ST_S1; EDGE_WAIT_S=$(( ( $(now_ms) - t0 ) / 1000 )); return 0; fi
    local now; now=$(now_ms)
    [ $(( now - t0 )) -ge $(( cap * 1000 )) ] && { EDGE_WAIT_S=$cap; return 1; }
    if [ $(( now - last_chk )) -ge 10000 ]; then last_chk=$now; dv2_gate "edge wait"; fi
    sleep 0.05
  done
}
# the one-shot reset must show in the sampler (resets 1) before the launch
dv2_wait_reset() {   # dv2_wait_reset <seconds>: 0 when the sampler reports the reset (real time: the sampler's and
  # the watcher's latencies are real, also under V3_DRY's virtual clock)
  local end=$(( $(date +%s%3N) + $(awk -v s="$1" 'BEGIN{printf "%d", s*1000}') ))
  while [ "$(date +%s%3N)" -lt "$end" ]; do
    dv2_live || return 1
    [ "$ST_RESETS" = 1 ] && return 0
    sleep 0.05
  done
  dv2_state; [ "$ST_RESETS" = 1 ]
}

# ---- the tail: sample for <s> after the launch (the exit event, the post-run clock check)
dv2_tail() { local end=$(( $(now_ms) + $1 * 1000 )); while [ "$(now_ms)" -lt "$end" ]; do dv2_live || true; sleep 0.1; done; }

# ---- the post-run clock check (R6): 600 MHz within 3 s of the kernel end, held to the tail's end; else ABORT-LATCH
dv2_postcheck() {   # dv2_postcheck <tel.jsonl> <kernel end ms>
  local out rc=0 m
  out=$("${DV2PY[@]}" postcheck --tel "$1" --t-end "$2" --within-s "$P_post_within_s" --tail-s "$P_tail_s") || rc=$?
  POST_WHY=$out; POST_RC=$rc
  if [ "$rc" = 2 ]; then          # the telemetry cannot tell: one 1 s reading decides (the sampler is stopped)
    m=$(clock_mhz)
    mark postcheck_direct "\"mhz\":$(jnum "$m"),\"why\":$(jstr "$out")"
    if [ "$m" = 600 ]; then POST_RC=0; POST_WHY="$out; a direct read shows 600 MHz"; else POST_RC=1; POST_WHY="$out; a direct read shows ${m:-nothing}"; fi
  fi
  mark postcheck "\"rc\":$POST_RC,\"why\":$(jstr "$POST_WHY")"
  [ "$POST_RC" = 1 ] && dv2_abort_latch "run ${RUN_ID}: $POST_WHY"
  return 0
}

# ---- the R0 probe (hp/hplib.sh's hp_probe; DESIGN §4.1): one 2 s UNI32@4 launch with no sampler, dumps around it
dv2_probe() {   # dv2_probe <dir>; sets PROBE_CLASS
  local d=$1 R rc
  mkdir -p "$d"
  { command -v et-who > /dev/null && timeout 20 et-who 8>&- 9>&-; } > "$d/et-who.txt" 2>&1 || true
  who > "$d/who.txt" 2>&1 || true
  R=$(die_c)
  echo "{\"t_ms\":$(now_ms),\"die_c\":$(jnum "$R")}" > "$d/reading.json"
  dv2_sptrace "$d/p0.bin"
  dv2_launch probe probe 0xffffffff 4 2
  rc=$LAST_RC
  dv2_sptrace "$d/p1.bin"
  dv2_config "$d/config.json"
  python3 "$DV2_DIR/sptrace_events.py" classify "$d/p0.bin" "$d/p1.bin" --config "$d/config.json" > "$d/class.json" 2> "$d/class.err"
  PROBE_CLASS=$(python3 -c "import json,sys; print(json.load(open(sys.argv[1])).get('class') or '')" "$d/class.json" 2>/dev/null)
  echo "{\"rest_c\":$(jnum "$R"),\"class\":\"$PROBE_CLASS\",\"heater_rc\":$rc}" > "$d/probe.json"
  mark probe "\"rest_c\":$(jnum "$R"),\"class\":\"$PROBE_CLASS\",\"heater_rc\":$rc"
  log "dv2 probe: class $PROBE_CLASS at rest $R C"
}

# ---- the global-state table (DESIGN §4.2): found / set / restored / verified, one per session
dv2_state_table() {   # dv2_state_table <when> <config.json>
  python3 - "$OUT/global-state.jsonl" "$1" "$2" "${LEVEL_FOUND:-}" "${LEVEL_ORIG:-}" "${LEVEL_CHECK:-}" "$(now_ms)" <<'PY'
import json, sys
out, when, cfgp, lf, lo, lc, t = sys.argv[1:8]
try: cfg = json.load(open(cfgp))
except Exception: cfg = {}
row = {"t_ms": int(t), "when": when, "threshold_c": cfg.get("temp_threshold_c"), "tdp_w": cfg.get("tdp_w"),
       "power_state": cfg.get("power_state_name"), "minion_mhz": cfg.get("minion_mhz"),
       "sp_level_found": lf or None, "sp_level_restore_target": lo or None, "sp_level_check": lc or None,
       "stats_trace": "not changed by DV2 (the one-shot and periodic resets send control 2, as every --reset-ms did)",
       "threshold_set_by_dv2": False, "tdp_apm_clocks_voltages_set_by_dv2": False}
open(out, "a").write(json.dumps(row) + "\n")
print("global state (%s): threshold %s, TDP %s, %s, level found %s%s" % (when, row["threshold_c"], row["tdp_w"],
      row["power_state"], lf or "-", ("; " + lc) if lc else ""))
PY
}
dv2_threshold_ok() {   # dv2_threshold_ok <config.json>: 0 if 65; 2 if unreadable (no alert); else the alert and 1
  local thr; thr=$(python3 -c "import json,sys; print(json.load(open(sys.argv[1])).get('temp_threshold_c'))" "$1" 2>/dev/null)
  [ "$thr" = 65 ] && return 0
  case "$thr" in ''|None|null) mark threshold_unread "\"file\":\"${1##*/}\""; return 2 ;; esac
  if [ -e "$DV2_DATA/pending.json" ]; then dv2_alert THRESHOLD "threshold reads $thr with pending.json present: this build has no D1; restore needs the owner"
  else dv2_alert THRESHOLD "threshold reads $thr, no pending.json: someone else changed it; alert only, never touched"; fi
  return 1
}
