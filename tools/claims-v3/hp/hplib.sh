# Heat placement (HP, DESIGN2): the shell helpers of block.sh, probe.sh and a2/block.sh. Source it after ../lib.sh
# (which cd's to the tree root and sets CARD, HEATER, ETTELEM, DATA_ROOT, the lock and the V3_DRY stubs):
#   HP_DIR=tools/claims-v3/hp; . "$HP_DIR/hplib.sh"        (a2/block.sh sets HP_DIR to its frozen copy)
#
# The owner's rules it enforces (27 Sep 2026; CLAUDE.md/AGENT.md; README.md here):
#   O1  a run may chain back-to-back launches for up to chain_cap_s (150 s); every launch is its own process under
#       hold10 (timeout 10), the device is released between launches, the card lock (lib block_begin, fd 9) stays
#       held, and the other-user check (lib others_present, the process scan, the et_soc1 use count) runs between
#       launches (hp_between);
#   O2  the SP log level is set to WARNING only on a card whose R0 probe was ALIVE (or for aifoundry3's one-shot), and
#       the level found is restored at the end (EXIT trap), except after an intrusion (exit 3: the card is left at once);
#   90 C no die reading ever reaches 90 C: the watcher stops the heater (its --stop-file) and the block at mean or high
#       >= 90 and ends the session (build/claims-v3/STOP); the run caps (80 mean, 85 high, 73 W for 2 samples) end
#       the run long before;
#   card 0 on aifoundry1 a read-only guard sampler on card 0 (ET_DEVICES=0, 1 Hz, no lock, no launch) runs through
#       every card-1 block; a block starts only if card 0 reads <= 85 C, and card 1's work stops if card 0 reads
#       > 90 C or the guard's output is 10 s stale.
# Every device process is hold10 (heater, sptrace, config, loglevel); samplers start and stop only through lib's
# start_sampler/stop_sampler (SIGTERM); nothing else opens the management node while a sampler runs. Background
# processes (samplers, the guard, the watcher) start with fds 8 and 9 closed, so none of them holds a card lock.
set -u
# aifoundry1 card 0 is never used (owner, DESIGN2 §0): refused before anything else, whatever script sources this
case "${CARD:-}" in
  aifoundry1-c0) echo "hp: aifoundry1 card 0 is never used (owner decision, DESIGN2 §0): refused (V3_DEVICE=${V3_DEVICE:-})" >&2; exit 2 ;;
  aifoundry1-c1) [ "${ET_DEVICES:-}" = 1 ] || { echo "hp: aifoundry1-c1 needs ET_DEVICES=1 (got '${ET_DEVICES:-}'): refused" >&2; exit 2; } ;;
esac
HP_DIR=${HP_DIR:-tools/claims-v3/hp}
HPPY=(python3 "$HP_DIR/hplib.py")

# ---- binaries. On aifoundry2 the tree is the heat worktree, built as README.md says (build/ettelem,
# build/sparsity_t2, build/ettelem-hp). HP_BIN_ROOT=<dir> points every binary at another tree's build directory
# instead (e.g. HP_BIN_ROOT=$HOME/claude/et-soc1-prototyping/build, the V3 campaign's binaries on aifoundry2).
if [ -n "${HP_BIN_ROOT:-}" ]; then
  ETTELEM=$HP_BIN_ROOT/ettelem/ettelem
  if [ "$CARD" = aifoundry2 ]; then HEATER=$HP_BIN_ROOT/sparsity_t2/host/sparsity_host
  else HEATER=$HP_BIN_ROOT/sparsity/host/sparsity_host; fi
  ETTELEM_HP=$HP_BIN_ROOT/ettelem-hp/ettelem
fi
HEATER=${HP_HEATER:-$HEATER}
ETTELEM=${HP_ETTELEM:-$ETTELEM}
ETTELEM_HP=${HP_ETTELEM_HP:-${ETTELEM_HP:-build/ettelem-hp/ettelem}}
# The heater's kernel: the file the locks hash (heater_kernel) and the one every launch loads, passed explicitly with
# --kernel (review low: the heater otherwise loads its compiled-in absolute KERNEL_ELF, which a relocated heater
# (HP_HEATER, HP_BIN_ROOT) does not share with the hashed path)
HEATER_KERNEL=$(dirname "$HEATER")/../kernel/sparsity.elf
case "$HEATER_KERNEL" in /*) HEATER_KERNEL_ABS=$HEATER_KERNEL ;; *) HEATER_KERNEL_ABS=$V3_ROOT/$HEATER_KERNEL ;; esac
SESSION_STOP=$V3_ROOT/build/claims-v3/STOP          # queue.sh stops at the next block boundary when it exists

dry() { [ -n "${V3_DRY:-}" ]; }

# ---- V3_DRY=1: an accelerated simulation instead of the card (hplib.py dry-*). Time runs HP_DRY_SPEED times
# faster (default 40) on a virtual clock shared by this shell and the simulator; no device is touched.
if dry; then
  export HP_DRY_SPEED=${HP_DRY_SPEED:-40}
  export HP_DRY_CARD=$CARD
  export HP_DRY_DIR=${HP_DRY_DIR:-$V3_ROOT/build/claims-v3-dry/hp-sim}
  mkdir -p "$HP_DRY_DIR"
  # one virtual timeline per dry tree (the simulator's state lives on it): kept in the sim directory
  if [ -z "${HP_VT0:-}" ]; then [ -s "$HP_DRY_DIR/vt0" ] || date +%s%3N > "$HP_DRY_DIR/vt0"; HP_VT0=$(cat "$HP_DRY_DIR/vt0"); fi
  export HP_VT0
  SESSION_STOP=$V3_ROOT/build/claims-v3-dry/STOP
  now_ms() { local r; r=$(date +%s%3N); echo $(( HP_VT0 + (r - HP_VT0) * HP_DRY_SPEED )); }
  hp_sleep() { sleep "$(awk -v s="$1" -v k="$HP_DRY_SPEED" 'BEGIN{printf "%.3f", s / k}')"; }
  die_c() { "${HPPY[@]}" dry-die --card "$CARD"; }
  start_sampler() {   # lib's interface: start_sampler <out> <secs> [extra ettelem args]
    local out=$1 secs=$2; shift 2
    local rs=0; [ "${1:-}" = --reset-ms ] && rs=$2
    "${HPPY[@]}" dry-sampler --card "$CARD" --out "$out.raw" --seconds "$secs" --every-ms 100 --reset-ms "$rs" &
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
  # test hook (dry only): an intrusion appears when this file exists (the exit-3 paths)
  others_present() { [ -e "$HP_DRY_DIR/intrude" ] && { log "others present (dry hook $HP_DRY_DIR/intrude)"; return 0; }; return 1; }
else
  hp_sleep() { sleep "$1"; }
fi
# lib's start_sampler, with fds 8 and 9 (the card locks) closed for the sampler it starts (review F14): the redirection
# on the call closes them inside the call only, so this shell keeps its lock
eval "hp_lib_start_sampler() $(declare -f start_sampler | tail -n +2)"
start_sampler() { hp_lib_start_sampler "$@" 8>&- 9>&-; }

# ---- small helpers
jnum() { [ -z "${1:-}" ] || [ "$1" = - ] && echo null || echo "$1"; }
mark() {  # mark <event> [extra JSON fields, already formatted]
  local extra=${2:-}; [ -n "$extra" ] && extra=",$extra"
  echo "{\"t_ms\":$(now_ms),\"ev\":\"$1\"$extra}" >> "$OUT/marks.jsonl"
}
# lib's block_end writes die_c's output unquoted; after an intrusion (NO_CARD) the card is not opened again
eval "hp_lib_die_c() $(declare -f die_c | tail -n +2)"
die_c() { local t=; [ -n "${NO_CARD:-}" ] || t=$(hp_lib_die_c); echo "${t:-null}"; }

# et_soc1 use count (single-card hosts; with V3_DEVICE the module serves both cards, so it is not used there)
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
# idle/block.sh's scan: device processes on this card other than our sampler and our card-0 guard ("F ..."), and ours
# on the other card of the host ("O ...")
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

# ---- abort and cleanup. Exit 3 = someone else on the card: leave it at once (no reading, no level restore: the
# pending level in sp-level.json is restored by the next block on the card).
WATCH_PID=; GUARD_PID=; GUARD_RAW=; GUARD_T0=; LEVEL_SET=; LEVEL_FOUND=; LEVEL_ORIG=; NO_CARD=
hp_session_stop() {   # hp_session_stop <why>: the queue stops at the next block boundary (DESIGN2 §7: end the session)
  touch "$SESSION_STOP"
  mark session_stop "\"why\":\"${1//\"/\'}\",\"file\":\"$SESSION_STOP\""
}
hp_abort() {  # hp_abort <exit code> <note> [session]   ("session": a card-0 stop, which also ends the session)
  mark abort "\"why\":\"${2//\"/\'}\",\"code\":$1"
  [ "${3:-}" = session ] && hp_session_stop "$2"
  [ "$1" = 3 ] && NO_CARD=1
  hp_run_end_quiet
  hp_guard_stop
  [ -z "$NO_CARD" ] && hp_level_restore
  hp_gzip_all
  declare -F hp_on_abort > /dev/null && hp_on_abort "$1" "$2"
  block_end fail "$2"
  exit "$1"
}
hp_gzip_all() {
  local f
  for f in "$OUT"/tel-*.jsonl "$OUT"/heater-*.out "$OUT"/guard.jsonl "$OUT"/heater-*-pre.out; do [ -f "$f" ] && gzip -f "$f"; done
  rm -f "$OUT"/.state-* "$OUT"/.ctl-* "$OUT"/.stop-* "$OUT"/.state-*.tmp "$OUT"/.dryfail-*
}
hp_cleanup() {   # EXIT trap
  hp_run_end_quiet
  hp_guard_stop
  [ -z "$NO_CARD" ] && hp_level_restore
}

# ---- device calls other than the heater: sptrace, config, loglevel (each a device process under hold10)
hp_sptrace() {   # hp_sptrace <out.bin>
  if dry; then "${HPPY[@]}" dry-sptrace --card "$CARD" --out "$1" >> "$OUT/mgmt.log" 2>&1
  else hold10 "$ETTELEM" sptrace "$1" >> "$OUT/mgmt.log" 2>&1; fi
}
hp_config() {    # hp_config <out.json>
  if dry; then "${HPPY[@]}" dry-config --card "$CARD" > "$1" 2>> "$OUT/mgmt.log"
  else hold10 "$ETTELEM" config > "$1" 2>> "$OUT/mgmt.log"; fi
}
hp_loglevel() {  # hp_loglevel critical|error|warning|info|debug   (ettelem-hp: warning sets WARNING, not INFO)
  if dry; then "${HPPY[@]}" dry-loglevel --card "$CARD" --level "$1" >> "$OUT/mgmt.log" 2>&1
  else hold10 "$ETTELEM_HP" loglevel "$1" >> "$OUT/mgmt.log" 2>&1; fi
}
# O2 (DESIGN2 §3.3; review F3). The level first found on this card is kept in $LEVEL_STATE (hplib.py level-*): the
# only restore target. WARNING is set only when that level is known (INFO or DEBUG), never on an unknown one; the
# state is marked pending and LEVEL_SET is set BEFORE the set command, so any attempted set is restored; the end of
# the block restores the original and checks it with a dump (pending cleared only when the dump reads it).
LEVEL_STATE=$DATA_ROOT/hp/sp-level.json
# The level is inferred from the entries NEW between two dumps taken back to back, never from the whole ring (review
# medium, 27 Sep: the 4 KB ring keeps about 50 entries, so INFO-era lines outlive a switch to WARNING and the whole ring
# can read INFO on a card at WARNING, e.g. after a restore that failed). sptrace_events.py level-since.
hp_level_infer() {   # hp_level_infer <prev.bin> <cur.bin> [--begin]: DEBUG | INFO | WARNING_OR_LOWER | UNKNOWN (a dump failed)
  if [ -s "$1" ] && [ -s "$2" ]; then
    python3 "$HP_DIR/sptrace_events.py" level-since "$1" "$2" ${3:-} 2>/dev/null || echo UNKNOWN
  else echo UNKNOWN; fi
}
hp_level_dumps() {   # hp_level_dumps <name>: two dumps back to back, <name>-0.bin and <name>.bin
  rm -f "$OUT/$1-0.bin" "$OUT/$1.bin"; hp_sptrace "$OUT/$1-0.bin"; hp_sptrace "$OUT/$1.bin"
}
hp_level_begin() {   # hp_level_begin <dump-name>; sets TRIGB= when the level is unknown (no TRIG-B in this block)
  # O2 as DESIGN2 §3.2 applies it: only on an ALIVE (or ALIVE_CANDIDATE) probe, or aifoundry3's STUCK one-shot
  case "${PROBE_CLASS:-}" in
    ALIVE|ALIVE_CANDIDATE) ;;
    *) if [ "${PROBE_CLASS:-}" != STUCK ] || [ "${TYPE:-}" != B1 ] || [ "$CARD" != aifoundry3 ]; then
         TRIGB=; mark trigb_refused "\"probe_class\":\"${PROBE_CLASS:-}\",\"type\":\"${TYPE:-}\""; return 0
       fi ;;
  esac
  mkdir -p "$(dirname "$LEVEL_STATE")"
  hp_level_dumps "$1"
  LEVEL_FOUND=$(hp_level_infer "$OUT/$1-0.bin" "$OUT/$1.bin" --begin)
  local LV_ACTION LV_ORIG LV_WHY
  eval "$("${HPPY[@]}" level-begin --state "$LEVEL_STATE" --found "$LEVEL_FOUND" --block "$PASS")"
  mark level_found "\"level\":\"$LEVEL_FOUND\",\"action\":\"$LV_ACTION\",\"original\":\"$LV_ORIG\",\"why\":\"${LV_WHY//\"/\'}\""
  case "$LV_ACTION" in
    set)
      LEVEL_ORIG=$LV_ORIG
      "${HPPY[@]}" level-mark --state "$LEVEL_STATE" --block "$PASS" --pending 1 > /dev/null
      LEVEL_SET=1                                   # before the command: a set that times out is still restored
      local rc=0; hp_loglevel warning || rc=$?
      mark level_set "\"level\":\"WARNING\",\"rc\":$rc,\"restore_to\":\"$LEVEL_ORIG\"" ;;
    none) LEVEL_ORIG= ;;
    *) LEVEL_ORIG=; TRIGB=; mark trigb_skipped "\"why\":\"${LV_WHY//\"/\'}\"" ;;
  esac
}
hp_level_check() {   # the end-of-block check: a dump must read the original level again (then pending is cleared)
  local want=$1 got
  hp_level_dumps sp-level-check
  got=$(hp_level_infer "$OUT/sp-level-check-0.bin" "$OUT/sp-level-check.bin")
  "${HPPY[@]}" level-mark --state "$LEVEL_STATE" --block "$PASS" --checked "$got" > /dev/null
  mark level_check "\"want\":\"$want\",\"got\":\"$got\",\"ok\":$([ "$got" = "$want" ] && echo true || echo false)"
  if [ "$got" = "$want" ]; then LEVEL_CHECK="SP level restored to $want (checked)"
  else LEVEL_CHECK="SP level NOT restored: $got, want $want (pending: the next block restores it)"; fi
  log "$LEVEL_CHECK"
}
hp_level_restore() {
  [ -n "$LEVEL_SET" ] || return 0
  local lv
  case "$LEVEL_ORIG" in INFO) lv=info ;; DEBUG) lv=debug ;; *) mark level_restore_skipped "\"original\":\"$LEVEL_ORIG\""; LEVEL_SET=; return 0 ;; esac
  local rc=0; hp_loglevel "$lv" || rc=$?
  LEVEL_SET=
  mark level_restored "\"level\":\"$lv\",\"rc\":$rc"
  hp_level_check "$LEVEL_ORIG"
}
# a set an earlier block left pending (it was aborted by an intrusion, killed, or its restore failed): restore the
# original level now, before this block reads or uses the ring (a probe, a non-TRIG-B block, or a TRIG-B block)
hp_level_pending_restore() {
  [ -f "$LEVEL_STATE" ] || return 0
  local LV_PENDING LV_ORIG
  eval "$("${HPPY[@]}" level-show --state "$LEVEL_STATE")"
  [ -n "$LV_PENDING" ] || return 0
  case "$LV_ORIG" in INFO|DEBUG) ;; *) mark level_pending_unknown "\"original\":\"$LV_ORIG\""; return 0 ;; esac
  mark level_pending "\"original\":\"$LV_ORIG\""
  LEVEL_SET=1; LEVEL_ORIG=$LV_ORIG
  hp_level_restore
}

# ---- the card-0 guard (aifoundry1 card 1 only). The guard is the only access to card 0: a read-only sampler with no
# lock (fds 8, 9 closed), no launch, no configuration; its lifetime is P_guard_max_s (2700 s), and it is restarted
# between runs after P_guard_refresh_s, so an orphan (a block killed with SIGKILL) ends by itself.
GUARD_ON=; [ "$CARD" = aifoundry1-c1 ] && GUARD_ON=1
hp_guard_start() {   # hp_guard_start [gate C]   (default: the start gate, 85 C)
  [ -n "$GUARD_ON" ] || return 0
  local gate=${1:-$P_guard_gate_c}
  GUARD_RAW=$OUT/guard.jsonl.raw
  local try i
  for try in 1 2 3; do
    : > "$GUARD_RAW"
    if dry; then "${HPPY[@]}" dry-guard --out "$GUARD_RAW" --seconds "$P_guard_max_s" --every-ms 1000 8>&- 9>&- &
    else ET_DEVICES=0 "$ETTELEM" sample --seconds "$P_guard_max_s" --every-ms 1000 > "$GUARD_RAW" 2>/dev/null < /dev/null 8>&- 9>&- & fi
    GUARD_PID=$!; GUARD_T0=$(now_ms)
    for i in $(seq 1 60); do grep -q '^{' "$GUARD_RAW" 2>/dev/null && break; sleep 0.25; done
    grep -q '^{' "$GUARD_RAW" 2>/dev/null && break
    hp_guard_stop; sleep 2
  done
  [ -n "$GUARD_PID" ] || return 1
  local why; why=$("${HPPY[@]}" guardcheck --guard "$GUARD_RAW" --gate "$gate" --max-age "$P_guard_stale_s")
  local rc=$?
  mark guard_start "\"ok\":$([ $rc = 0 ] && echo true || echo false),\"gate\":$gate,\"pid\":$GUARD_PID,\"why\":\"$why\""
  return $rc
}
hp_guard_refresh() {   # between runs: a guard older than P_guard_refresh_s is restarted (the stop threshold as its gate)
  [ -n "$GUARD_ON" ] && [ -n "${GUARD_PID:-}" ] || return 0
  [ $(( $(now_ms) - GUARD_T0 )) -ge $(( P_guard_refresh_s * 1000 )) ] || return 0
  hp_guard_stop
  hp_guard_start "$P_guard_stop_c" || hp_abort 1 "card-0 guard did not restart (refresh)" session
}
hp_guard_stop() {
  [ -n "${GUARD_PID:-}" ] || return 0
  kill -TERM "$GUARD_PID" 2>/dev/null
  local i; for i in $(seq 1 300); do kill -0 "$GUARD_PID" 2>/dev/null || break; sleep 0.1; done
  wait "$GUARD_PID" 2>/dev/null
  GUARD_PID=
  [ -f "$GUARD_RAW" ] && { grep '^{' "$GUARD_RAW" >> "$OUT/guard.jsonl"; rm -f "$GUARD_RAW"; }
}
hp_guard_ok() {
  [ -n "$GUARD_ON" ] || return 0
  GUARD_WHY=$("${HPPY[@]}" guardcheck --guard "$GUARD_RAW" --gate "$P_guard_stop_c" --max-age "$P_guard_stale_s")
}
# lib's drain opens every card's management node: with the guard holding card 0's, stop the guard around it
eval "hp_lib_drain_mgmt() $(declare -f drain_mgmt | tail -n +2)"
drain_mgmt() {
  if [ -n "$GUARD_ON" ] && [ -n "${GUARD_PID:-}" ]; then
    hp_guard_stop; hp_lib_drain_mgmt
    hp_guard_start "$P_guard_stop_c" || hp_abort 1 "card-0 guard did not restart after a drain" session
  else
    hp_lib_drain_mgmt
  fi
}

# ---- card 0 idle (aifoundry1 card 1 only; DESIGN2 §6.1: card 0 holds no process and no lock holder at every
# between-launch check, OUR OWN account included; review F8). Violations: any process of ours on card 0 (ET_DEVICES
# naming card 0 and not card 1; with no ET_DEVICES a process opens every card and foreign_procs already stops the
# block), any holder of a /dev/et0 node or of etsoc-shire0.lock (et-holders, every user), and a flock on
# etsoc-shire0.lock (/proc/locks: read, never taken). Our guard is the one allowed holder of card 0's node.
HP_CARD0_LOCK=/run/lock/etsoc-shire0.lock
hp_card0_violations() {
  local me pid e v= lk ino
  if dry && [ -z "${HP_DRY_CARD0_TEST:-}" ]; then return 0; fi
  me=$(id -u)
  for pid in $(ps -eo uid=,pid=,comm= | awk -v me="$me" -v re="$DEV_COMM" -v gp="${GUARD_PID:-0}" -v sp="${SAMPLER_PID:-0}" \
                 '$1 == me && $3 ~ re && $2 != gp && $2 != sp {print $2}'); do
    e=$(penv_devices "$pid") || continue
    [ -n "$e" ] || continue
    case ",${e// /,}," in *",0,"*) v="$v proc:$pid(ET_DEVICES=$e)" ;; esac
  done
  if ! dry && [ -x /usr/local/sbin/et-holders ]; then
    v="$v $(sudo -n /usr/local/sbin/et-holders 8>&- 9>&- 2>/dev/null |
             awk -v gp="${GUARD_PID:-0}" '($1 ~ /^\/dev\/et0_/ || $1 == "lock:etsoc-shire0.lock") && $3 != gp {printf "holder:%s:%s:%s ", $1, $2, $3}')"
  elif dry && [ -n "${HP_DRY_HOLDERS:-}" ]; then     # dry test: an et-holders listing from a file
    v="$v $(awk -v gp="${GUARD_PID:-0}" '($1 ~ /^\/dev\/et0_/ || $1 == "lock:etsoc-shire0.lock") && $3 != gp {printf "holder:%s:%s:%s ", $1, $2, $3}' "$HP_DRY_HOLDERS")"
  fi
  lk=$HP_CARD0_LOCK; dry && lk=${HP_DRY_CARD0_LOCK:-$lk}
  if [ -e "$lk" ]; then
    ino=$(stat -c %i "$lk" 2>/dev/null)
    [ -n "$ino" ] && v="$v $(awk -v ino="$ino" '{n=split($6, f, ":"); if (f[n] == ino) printf "lock:%s(pid %s) ", "'"${lk##*/}"'", $5}' /proc/locks 2>/dev/null)"
  fi
  v=${v## }; v=${v%% }
  echo "$v"
}
hp_card0_check() {   # hp_card0_check <when>: exit 3 on any card-0 activity other than our guard
  [ -n "$GUARD_ON" ] || return 0
  local v; v=$(hp_card0_violations)
  [ -z "${v// /}" ] && return 0
  if [ -n "${OUT:-}" ] && [ -f "$OUT/marks.jsonl" ]; then hp_abort 3 "card 0 not idle ($1): $v"; fi
  log "hp: card 0 not idle ($1): $v"; exit 3
}
# an orphaned card-0 guard of ours (its block was killed with SIGKILL): an ettelem with ET_DEVICES=0 running the guard's
# command and whose parent is no hp block. It holds card 0's node: stopped with SIGTERM (never SIGKILL) at block start.
hp_orphan_guards() {
  [ -n "$GUARD_ON" ] || return 0
  local me pid e pp pcmd
  dry && [ -z "${HP_DRY_CARD0_TEST:-}" ] && return 0
  me=$(id -u)
  for pid in $(ps -eo uid=,pid=,comm= | awk -v me="$me" '$1 == me && $3 == "ettelem" {print $2}'); do
    e=$(penv_devices "$pid") || continue
    [ "$e" = 0 ] || continue
    tr '\0' ' ' < "/proc/$pid/cmdline" 2>/dev/null | grep -q 'sample --seconds [0-9]* --every-ms 1000' || continue
    pp=$(ps -o ppid= -p "$pid" | tr -d ' ')
    pcmd=$(tr '\0' ' ' < "/proc/$pp/cmdline" 2>/dev/null)
    case "$pcmd" in *tools/claims-v3/hp/block.sh*|*tools/claims-v3/hp/probe.sh*) continue ;; esac
    log "hp: orphaned card-0 guard $pid (parent $pp: ${pcmd:-gone}): SIGTERM"
    kill -TERM "$pid" 2>/dev/null
    local i; for i in $(seq 1 300); do kill -0 "$pid" 2>/dev/null || break; sleep 0.1; done
    kill -0 "$pid" 2>/dev/null && { log "hp: orphaned guard $pid ignored SIGTERM for 30 s: not starting"; exit 3; }
  done
  return 0
}
# the card lock file must exist (lib's block_begin silently skips the lock without it; review F14)
hp_lock_present() {
  local d=/run/lock
  if dry; then [ -n "${HP_DRY_LOCK_DIR:-}" ] || return 0; d=$HP_DRY_LOCK_DIR; fi
  [ -e "$d/etsoc-shire${V3_DEVICE:-0}.lock" ] || { log "hp: $d/etsoc-shire${V3_DEVICE:-0}.lock is missing: not starting without the card lock"; exit 1; }
}
# override variables are honoured only under V3_DRY (review F1, F15); V3_FORCE is refused for validation and on card 1
# (review medium, 27 Sep). A refusal is recorded in build/claims-v3[-dry]/hp-refused.jsonl before the exit.
HP_REFUSED_LOG=$V3_ROOT/build/claims-v3/hp-refused.jsonl; dry && HP_REFUSED_LOG=$V3_ROOT/build/claims-v3-dry/hp-refused.jsonl
hp_refused_record() {   # hp_refused_record <who> <why>
  mkdir -p "$(dirname "$HP_REFUSED_LOG")"
  python3 -c 'import json,sys,time; print(json.dumps({"t_ms": int(time.time()*1000), "who": sys.argv[1], "card": sys.argv[2],
    "pass": sys.argv[3], "why": sys.argv[4], "dry": sys.argv[5] == "1"}))' "$1" "$CARD" "${PASS:-}" "$2" "$(dry && echo 1 || echo 0)" \
    >> "$HP_REFUSED_LOG" 2>/dev/null || true
}
hp_envcheck() {   # hp_envcheck dev|val|a2
  local o; o=$("${HPPY[@]}" envcheck --mode "$1" --card "$CARD") || {
    hp_refused_record "hp_envcheck $1" "$o"; log "hp: refused: $o"; exit 2; }
  HP_OVERRIDES=$o
}
# the binaries a block runs, with their sha256 (binaries.json; the validation and A2 locks check them)
hp_binaries_json() {
  "${HPPY[@]}" binhash "heater=$HEATER" "heater_kernel=$HEATER_KERNEL" "ettelem=$ETTELEM" "ettelem_hp=$ETTELEM_HP"
}

# ---- between launches (O1): nobody else on the card, no foreign device process, the use count, card 0, the guard
hp_between() {
  others_present && hp_abort 3 "another user or device process present between launches"
  local fp; fp=$(foreign_procs)
  [ -n "${fp// /}" ] && hp_abort 3 "device process on this card between launches: $fp"
  local n; n=$(modcount)
  [ -n "$n" ] && [ -n "${NS:-}" ] && [ "$n" -gt "$NS" ] && hp_abort 3 "et_soc1 use count $n > $NS between launches"
  hp_card0_check "between launches"
  if [ -n "$GUARD_ON" ]; then hp_guard_ok || hp_abort 1 "card-0 guard: $GUARD_WHY" session; fi
  return 0
}

# ---- one heater process: hp_launch <run> <kind> <mask> <per_shire> <seconds> [stop-file]; sets LAST_RC, L_TS, L_TE
hp_launch() {
  local run=$1 kind=$2 mask=$3 per=$4 secs=$5 sf=${6:-} log
  log=$OUT/heater-$run.out
  [ "$kind" = preheat ] && log=$OUT/heater-$run-pre.out     # the measured process(es) alone in heater-<run>.out (t0)
  local args=(--test fma --type fp32 --pattern none --values randn --shires "$mask" --per-shire "$per" --seconds "$secs" --seed 1
              --kernel "$HEATER_KERNEL_ABS")
  [ -n "$sf" ] && args+=(--stop-file "$sf")
  L_TS=$(now_ms)
  if dry; then "${HPPY[@]}" dry-heater --card "$CARD" -- "${args[@]}" >> "$log" 2>&1; LAST_RC=$?
    # dry test hook HP_DRY_HEATER_FAIL=<run>: that run's first measured launch fails (a void run: the re-run path)
    if [ -n "${HP_DRY_HEATER_FAIL:-}" ] && [ "$run" = "$HP_DRY_HEATER_FAIL" ] && [ "$kind" != preheat ] && [ ! -e "$OUT/.dryfail-$run" ]; then
      : > "$OUT/.dryfail-$run"; LAST_RC=1
    fi
  else hold10 "$HEATER" "${args[@]}" >> "$log" 2>&1; LAST_RC=$?; fi
  L_TE=$(now_ms)
  echo "{\"run\":\"$run\",\"kind\":\"$kind\",\"mask\":\"$mask\",\"per_shire\":$per,\"seconds\":$secs,\"t_start_ms\":$L_TS,\"t_end_ms\":$L_TE,\"rc\":$LAST_RC}" >> "$OUT/launches.jsonl"
  return $LAST_RC
}

# ---- one run's sampler and watcher
RUN_ID=; RUN_TEL=; RUN_STATE=; RUN_CTL=; RUN_SF=
hp_run_begin() {   # hp_run_begin <run id>: the 10 Hz --reset-ms sampler for the run and its live watcher
  RUN_ID=$1; RUN_TEL=$OUT/tel-$1.jsonl; RUN_STATE=$OUT/.state-$1; RUN_CTL=$OUT/.ctl-$1; RUN_SF=$OUT/.stop-$1
  rm -f "$RUN_SF" "$RUN_STATE"; : > "$RUN_CTL"
  start_sampler "$RUN_TEL" 1800 --reset-ms "$P_reset_ms" || hp_abort 1 "sampler did not start (run $1)"
  local caps="abs_stop_c=$P_abs_stop_c,cap_mean_c=$P_cap_mean_c,cap_high_c=$P_cap_high_c,cap_board_w=$P_cap_board_w"
  caps+=",cap_consecutive=$P_cap_consecutive,guard_stop_c=$P_guard_stop_c,guard_stale_s=$P_guard_stale_s"
  "${HPPY[@]}" watch --tel "$RUN_TEL.raw" --state "$RUN_STATE" --ctl "$RUN_CTL" --stop-file "$RUN_SF" \
    --session-stop "$SESSION_STOP" --guard "${GUARD_RAW:-}" --caps "$caps" 8>&- 9>&- &
  WATCH_PID=$!
  local i; for i in $(seq 1 200); do hp_state && [ "$ST_N" != - ] && [ "$ST_N" -ge 1 ] && break; sleep 0.05; done
  hp_state || hp_abort 1 "the watcher saw no sample (run $1)"
  kill -0 "$WATCH_PID" 2>/dev/null || hp_abort 1 "the watcher did not start (run $1)"
  # the use count with only our sampler open: the intrusion baseline
  NS=0; local n; for i in 1 2 3; do n=$(modcount); [ -n "$n" ] && [ "$n" -gt "$NS" ] && NS=$n; done
  [ "$MODCHECK" = on ] || NS=
  return 0
}
hp_run_end_quiet() {
  if [ -n "${WATCH_PID:-}" ]; then
    echo quit >> "$RUN_CTL" 2>/dev/null
    local i; for i in $(seq 1 40); do kill -0 "$WATCH_PID" 2>/dev/null || break; sleep 0.05; done
    kill "$WATCH_PID" 2>/dev/null; wait "$WATCH_PID" 2>/dev/null; WATCH_PID=
  fi
  stop_sampler
}
hp_state() {   # the watcher's newest state line into ST_*; non-zero if there is none
  local l; l=$(cat "$RUN_STATE" 2>/dev/null) || return 1
  read -r ST_T ST_MEAN ST_HIGH ST_W ST_MHZ ST_N ST_STOP ST_F66 ST_EDGE ST_TAUC ST_S1 ST_AGE ST_GMEAN ST_GAGE ST_WALL <<< "$l"
  [ -n "${ST_T:-}" ] && [ "$ST_T" != - ]
}
# the live checks every loop makes: the watcher alive and its state fresh (real clock), a sticky stop from the
# watcher, and a stale sampler (review F11: a dead watcher leaves a state line that still looks fresh)
hp_live() {   # returns 0 normally, 1 on a run stop (RUN_STOP set); aborts on ABS90/guard/stale/watcher gone
  if [ -n "${WATCH_PID:-}" ] && ! kill -0 "$WATCH_PID" 2>/dev/null; then
    hp_abort 1 "the run's watcher (pid $WATCH_PID) is gone: no safety stops without it"
  fi
  hp_state || hp_abort 1 "watcher state missing"
  if [ -n "${ST_WALL:-}" ] && [ "$ST_WALL" != - ] && [ $(( $(date +%s%3N) - ST_WALL )) -gt $(( P_sampler_stale_s * 1000 )) ]; then
    hp_abort 1 "the watcher's state is $(( $(date +%s%3N) - ST_WALL )) ms old (> ${P_sampler_stale_s} s): watcher stalled"
  fi
  case "$ST_STOP" in
    ABS90) hp_abort 1 "a die reading reached ${P_abs_stop_c} C: block and session stopped" ;;
    GUARD90|GUARD_STALE) hp_abort 1 "card-0 guard stop: $ST_STOP (card 0 mean $ST_GMEAN, age $ST_GAGE s)" session ;;
    -) ;;
    *) RUN_STOP=$ST_STOP; return 1 ;;
  esac
  if [ "$ST_AGE" != - ] && [ "$ST_AGE" -gt $(( P_sampler_stale_s * 1000 )) ]; then
    hp_abort 1 "sampler output stale for ${ST_AGE} ms"
  fi
  return 0
}

# ---- card 1's secondary card-0 proxy (DESIGN2 §7): W_idle (the last 2 s of the live sampler) against the session's
# first measured run; checked at the edge and also when the edge wait times out (review low, 27 Sep: a rise that lifts
# card 1's rest above its edge would otherwise never reach the check)
hp_widle_check() {   # hp_widle_check <role> <when>
  [ -n "$GUARD_ON" ] && [ "$1" != cal ] || return 0
  "${HPPY[@]}" widle --tel "$RUN_TEL.raw" --session "$DATA_ROOT/hp/session-widle.json" --pass "$PASS" \
    --rise "$P_guard_widle_rise_w" >> "$OUT/mgmt.log" 2>&1 ||
    hp_abort 1 "card-1 W_idle rose > ${P_guard_widle_rise_w} W since the session's first block (card-0 proxy, $2)" session
}

# ---- preheat to a target with ALL24 bursts (DESIGN2 §4.4 step 1); sets PREHEAT_BURSTS, PREHEAT_WHY
hp_preheat() {   # hp_preheat <target C> [mask per_shire seconds max_bursts]   (default: ALL24 2 s bursts)
  local target=$1 pm=${2:-0xffffffff} pp=${3:-24} ps=${4:-$P_preheat_s} pmax=${5:-$P_preheat_max_bursts}
  PREHEAT_BURSTS=0; PREHEAT_WHY=target
  while :; do
    hp_live || { PREHEAT_WHY=stop; return 1; }
    [ "$ST_MEAN" -ge "$target" ] && return 0
    [ "$ST_MEAN" -ge "$P_preheat_stop_c" ] && { PREHEAT_WHY=stop_c; return 0; }
    [ "$PREHEAT_BURSTS" -ge "$pmax" ] && { PREHEAT_WHY=bursts; return 1; }
    hp_between
    hp_launch "$RUN_ID" preheat "$pm" "$pp" "$ps" "$RUN_SF"
    if [ "$LAST_RC" -ne 0 ]; then
      PH_FAILS=$(( ${PH_FAILS:-0} + 1 )); [ "$PH_FAILS" -ge 3 ] && hp_abort 1 "3 heater failures in preheat"
    else PH_FAILS=0; fi
    PREHEAT_BURSTS=$(( PREHEAT_BURSTS + 1 ))
    hp_sleep 0.3
  done
}

# ---- wait for the falling S+1 -> S edge (§4.4 step 2); sets EDGE_T, EDGE_TAUC, EDGE_S1, EDGE_OK
hp_edge_wait() {   # hp_edge_wait <S> <cap s>
  local S=$1 cap=$2 t0 last_chk
  t0=$(now_ms); last_chk=$t0
  echo "edge $S $t0" >> "$RUN_CTL"
  EDGE_OK=; EDGE_T=; EDGE_TAUC=; EDGE_S1=
  while :; do
    hp_live || return 1
    if [ "$ST_EDGE" != - ]; then EDGE_OK=1; EDGE_T=$ST_EDGE; EDGE_TAUC=$ST_TAUC; EDGE_S1=$ST_S1; return 0; fi
    local now; now=$(now_ms)
    [ $(( now - t0 )) -ge $(( cap * 1000 )) ] && return 1
    if [ $(( now - last_chk )) -ge 10000 ]; then last_chk=$now; hp_between; fi
    sleep 0.05
  done
}

# ---- the Tier L chain (O1): 2 s launches until chain_after_66 launches have started after the live mean first
# read >= 66, or the cap; sets CH_N, CH_T0, CH_T1, CH_F66, CH_CENS, RUN_STOP, CH_RCS
hp_chain() {   # hp_chain <run> <mask> <per_shire> [launch seconds]
  local run=$1 mask=$2 per=$3 secs=${4:-$P_chain_launch_s} after=0 fails=0 el
  CH_T0=$(now_ms); CH_N=0; CH_F66=; CH_CENS=; CH_RCS=
  echo "arm66 $CH_T0" >> "$RUN_CTL"
  while :; do
    hp_live || break
    [ "$ST_F66" != - ] && CH_F66=$ST_F66
    [ -n "$CH_F66" ] && [ "$after" -ge "$P_chain_after_66" ] && break
    el=$(( $(now_ms) - CH_T0 ))
    if [ $(( el + (secs + 1) * 1000 )) -gt $(( P_chain_cap_s * 1000 )) ]; then [ -z "$CH_F66" ] && CH_CENS=1; break; fi
    hp_between
    hp_launch "$run" chain "$mask" "$per" "$secs" "$RUN_SF"
    CH_RCS="${CH_RCS:+$CH_RCS,}$LAST_RC"; CH_N=$(( CH_N + 1 ))
    if [ "$LAST_RC" -ne 0 ]; then fails=$(( fails + 1 )); [ "$fails" -ge 3 ] && hp_abort 1 "heater failed 3 times in a row"
    else fails=0; fi
    hp_state && [ "$ST_F66" != - ] && CH_F66=$ST_F66
    [ -n "$CH_F66" ] && [ "$L_TS" -ge "$CH_F66" ] && after=$(( after + 1 ))
  done
  CH_T1=$(now_ms)
}

# ---- one single launch (Tier S, A2) then an idle tail with the sampler; sets CH_* like hp_chain
hp_single() {   # hp_single <run> <mask> <per_shire> <seconds> <idle after s>
  local run=$1 mask=$2 per=$3 secs=$4 idle=$5 end
  CH_T0=$(now_ms); CH_N=0; CH_F66=; CH_CENS=; CH_RCS=
  echo "arm66 $CH_T0" >> "$RUN_CTL"
  hp_live || { CH_T1=$(now_ms); return 0; }
  hp_between
  hp_launch "$run" single "$mask" "$per" "$secs" "$RUN_SF"
  CH_RCS=$LAST_RC; CH_N=1
  hp_state && [ "$ST_F66" != - ] && CH_F66=$ST_F66
  end=$(( $(now_ms) + idle * 1000 ))
  while [ "$(now_ms)" -lt "$end" ]; do hp_live || true; sleep 0.1; done
  hp_state && [ "$ST_F66" != - ] && CH_F66=$ST_F66
  CH_T1=$(now_ms)
}

# ---- the R0 probe (DESIGN2 §3.2): one light launch with no sampler, dumps before and after, no state change.
# Writes probe.json into the directory given. The card lock is held by the caller (block_begin).
hp_probe() {   # hp_probe <dir>
  local d=$1 R cls
  mkdir -p "$d"
  { command -v et-who > /dev/null && timeout 20 et-who; } > "$d/et-who.txt" 2>&1 || true
  who > "$d/who.txt" 2>&1 || true
  R=$(die_c)
  echo "{\"t_ms\":$(now_ms),\"die_c\":$(jnum "$R")}" > "$d/reading.json"
  hp_sptrace "$d/p0.bin"
  hp_launch probe probe 0xffffffff 4 2
  local rc=$LAST_RC
  hp_sptrace "$d/p1.bin"                 # immediately, no query in between
  hp_config "$d/config.json"
  python3 "$HP_DIR/sptrace_events.py" classify "$d/p0.bin" "$d/p1.bin" --config "$d/config.json" > "$d/class.json" 2> "$d/class.err"
  python3 - "$d" "$CARD" "$R" "$rc" <<'PY'
import json, os, sys
d, card, R, rc = sys.argv[1], sys.argv[2], sys.argv[3], int(sys.argv[4])
try: c = json.load(open(os.path.join(d, "class.json")))
except Exception as e: c = {"class": None, "error": str(e)}
R = int(R) if R.lstrip("-").isdigit() else None
cls = c.get("class")
# DESIGN2 §3.2 predictions, fixed before any data
pred = {"aifoundry3": "SILENT (latched; STUCK if rebooted since 25 Sep)", "aifoundry1-c1": "SILENT (DVFS off)",
        "aifoundry2": ("SILENT (LOOP: in the thermal loop at rest >= 66)" if R is not None and R >= 66 else "ALIVE")}.get(card, "?")
reason = None
if cls == "SILENT":
    reason = {"aifoundry3": "latched (predicted)", "aifoundry1-c1": "DVFS off (predicted)"}.get(card)
    if card == "aifoundry2":
        reason = "LOOP: rest %s C >= 66, the governor sits in its thermal loop" % R if R is not None and R >= 66 else "no governor line"
trigb = cls in ("ALIVE", "ALIVE_CANDIDATE")
p = {"card": card, "rest_c": R, "class": cls, "silent_reason": reason, "level": c.get("level"), "counts": c.get("counts"),
     "tdp_w": c.get("tdp_w"), "heater_rc": rc, "prediction": pred,
     "prediction_met": (cls is not None and pred.split(" ")[0] == ("SILENT" if cls == "SILENT" else cls)),
     "trigb_allowed": trigb, "b1_one_shot": card == "aifoundry3" and cls == "STUCK"}
json.dump(p, open(os.path.join(d, "probe.json"), "w"), indent=1)
print("probe: class %s, level %s, rest %s C (predicted %s)" % (cls, c.get("level"), R, pred))
PY
}

# ---- the newest probe of this card (from the R0 probe block, pass 8xx): sets PROBE_CLASS, PROBE_JSON
hp_probe_class() {
  PROBE_JSON=$(ls -d "$DATA_ROOT"/hp/p8[0-9][0-9]/probe.json 2>/dev/null | tail -n 1)
  PROBE_CLASS=
  [ -n "$PROBE_JSON" ] && PROBE_CLASS=$(python3 -c "import json,sys; print(json.load(open(sys.argv[1])).get('class') or '')" "$PROBE_JSON")
  return 0
}

# ---- record one run in runs.jsonl
hp_record_run() {   # hp_record_run <idx> <slot> <attempt> <role> <name> <mask> <per> <minions> <tier> <edge> <target>
  local pe=${PRED_E:-0}
  printf '{"idx":%s,"slot":%s,"attempt":%s,"role":"%s","name":"%s","mask":"%s","per_shire":%s,"minions":%s,"tier":"%s","edge":%s,"target":%s,"pred":"%s","pred_energy_ws":%s,"preheat_bursts":%s,"preheat_why":"%s","edge_ok":%s,"s1_ms":%s,"edge_ms":%s,"tau_c_s":%s,"chain_t0_ms":%s,"chain_t1_ms":%s,"launches":%s,"rcs":[%s],"first66_live_ms":%s,"t66_live_s":%s,"censored_live":%s,"stop":%s,"trigb_dump":"%s","t_end_ms":%s}\n' \
    "$1" "$2" "$3" "$4" "$5" "$6" "$7" "$8" "$9" "$(jnum "${10}")" "$(jnum "${11}")" "${PRED_NAME:-}" "$pe" \
    "${PREHEAT_BURSTS:-0}" "${PREHEAT_WHY:-}" "$([ -n "${EDGE_OK:-}" ] && echo true || echo false)" \
    "$(jnum "${EDGE_S1:-}")" "$(jnum "${EDGE_T:-}")" "$(jnum "${EDGE_TAUC:-}")" "$(jnum "${CH_T0:-}")" "$(jnum "${CH_T1:-}")" \
    "${CH_N:-0}" "${CH_RCS:-}" "$(jnum "${CH_F66:-}")" \
    "$( [ -n "${CH_F66:-}" ] && awk -v a="$CH_F66" -v b="$CH_T0" 'BEGIN{printf "%.2f", (a-b)/1000}' || echo null)" \
    "$([ -n "${CH_CENS:-}" ] && echo true || echo false)" \
    "$([ -n "${RUN_STOP:-}" ] && echo "\"$RUN_STOP\"" || echo null)" "${TRIGB_DUMP:-}" "$(now_ms)" >> "$OUT/runs.jsonl"
}
