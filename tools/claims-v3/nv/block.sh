#!/usr/bin/env bash
# NV: the mesh (NoC) rail voltage step (tools/claims-v3/nv/DESIGN.md). One pass per block, always detached:
#   setsid nohup bash tools/claims-v3/nv/block.sh <pass> [--smoke|--probe] > <log> 2>&1 < /dev/null &
#   V3_DRY=1 bash tools/claims-v3/nv/block.sh 1 [--smoke|--probe]       no device access at all: every device program
#        is a stub from nv/stubs/ (NV_DRY_CARD=aifoundry3|aifoundry2 picks the card a dry run pretends to be;
#        NV_STUB_FAIL injects faults; NV_STUB_SCALE compresses time, default 0.1); data under build/claims-v3-dry/
# Passes 1-99 are development passes and run on aifoundry3 only; passes 101-199 are validation passes and run on
# aifoundry2 only, after DV2's validation there has ended and a person has written build/claims-v3/aifoundry2/nv/
# CARD-RELEASED, and only while every file in nv/LOCK.sha256 and nv/PREREG.sha256 hashes as frozen. Every real block
# (either card, any mode) also needs nv/PREDICTIONS.sha256 to check. --probe (both cards): the voltage steps alone
# (set, read back, dwell, read again, restore), no load; on the validation card it records no power at all.
# --smoke (development card only): 485 and 600 mV, two configurations each.
#
# NV runs only on a host with exactly one card: the stock dev_mngt_service opens every card's management node,
# whatever -n says (DESIGN.md §7). It never sets a rail on BL2 below 0.19.0, whose set also writes the value to the
# card's flash as its boot voltage: nv_set refuses it hard-coded, and nv.json min_bl2 again (DESIGN.md §2).
#
# A pass: the gate (a single-card host, PREDICTIONS.sha256, the card's release file, no other claims-v3 queue or
# block on the host, STOP files, ALERT files, a dirty state file, other users, our own device processes, et-who
# --check), then the card lock (flock -n, held until the block exits, so nobody runs on the card while its rail is off
# 485 mV), then one dev_mngt_service call each for the identity (firmware release and BL2), the uptime, the
# temperature, the rail (must read the base, 485 mV), the on-die monitor, the NoC clock (400 MHz) and the VMIN table;
# on a governor-free card, heating to 76 C (E42's heater); then a restore guardian; then, per segment in the pass's
# voltage order, the step (set, read-back through the regulator and through the on-die monitor), a settle, one idle
# sampler window, and the eight wsep configurations of E42 (tstore_uniq fill; one sampler window holding the 3 s
# burst); then the restore (verified: two reads 1 s apart and the on-die monitor) and a last idle window; then the
# uptime (a reset raises ALERT-NV-RESET) and the VMIN table again (a change raises ALERT-NV-FLASH).
# Every device-opening process is capped at 10 s (timeout -k 3 10): each dev_mngt_service call, each fill, each
# burst, each heater launch and each sampler window (ettelem sample --seconds 9; never left running for the block).
# The restore runs on every way out: the EXIT trap and the HUP, INT, TERM, PIPE, USR1, USR2 and ALRM traps, all
# ignored while it runs; a kill -9 or a crash is covered by the guardian, which holds the card lock until it has
# restored and verified the rail. A restore that cannot be verified writes ALERT-NV-RESTORE.json and the host's
# build/claims-v3/STOP, which stops every queue on the host.
# Exit: 0 ok (or done before, not needed, or a STOP file); 1 failed (block.json says why); 2 refused (usage, card,
# host, predictions, release, freeze, firmware); 3 the card or the host is busy, or the die too warm to start
# (run-queue.sh retries in 10 min).
set -u
NV_SIGS="HUP INT TERM PIPE USR1 USR2 ALRM"
# shellcheck disable=SC2086  # until the EXIT trap below exists nothing has been set: a signal just ends the block
trap 'exit 1' $NV_SIGS
. "$(dirname "${BASH_SOURCE[0]}")/../lib.sh"          # cd's to the tree root; CARD, DATA_ROOT, log, now_ms, others_present
WD=tools/claims-v3/nv
NVPY=(python3 -B "$WD/nvlib.py")
PASS=${1:-}; MODE=full
case "${2:-}" in '') ;; --smoke) MODE=smoke ;; --probe) MODE=probe ;; *) echo "usage: nv/block.sh <pass> [--smoke|--probe]" >&2; exit 2 ;; esac
case "$PASS" in ''|*[!0-9]*|0) echo "usage: nv/block.sh <pass >= 1> [--smoke|--probe]" >&2; exit 2 ;; esac
dry() { [ -n "${V3_DRY:-}" ]; }

# ---- dry runs: a pretend card and the stubs; real runs: no dry-only variable may be set
if dry; then
  CARD=${NV_DRY_CARD:-aifoundry3}
  DATA_ROOT=$V3_ROOT/build/claims-v3-dry/$CARD
  CTL=$V3_ROOT/build/claims-v3-dry                   # the dry STOP and ALERT files: a dry test never stops a real queue
  S=$V3_ROOT/$WD/stubs
  DMS=$S/stub-dms; ETT=$S/stub-ettelem; ENC=$S/stub-enercat; ETWHO=$S/stub-etwho; HEATER_BIN=$S/stub-heater
  export NV_STUB_STATE=${NV_STUB_STATE:-$DATA_ROOT/nv-stub-state} NV_STUB_SCALE=${NV_STUB_SCALE:-0.1}
  SCALE=$NV_STUB_SCALE
  mkdir -p "$NV_STUB_STATE" "$CTL"
  MGMT_NODES=${NV_DRY_MGMT_NODES:-1}
  ps_list() { [ -n "${NV_STUB_PS_FILE:-}" ] && cat "$NV_STUB_PS_FILE"; return 0; }   # never the host's own processes
else
  bad=$(env | grep -o '^NV_\(STUB\|DRY\)[A-Z_]*' | tr '\n' ' ')
  [ -n "$bad" ] && { echo "nv: dry-only variables set without V3_DRY: $bad" >&2; exit 2; }
  CTL=$V3_ROOT/build/claims-v3
  ETT=$ETTELEM; ENC=$ENERCAT2; ETWHO=et-who; SCALE=1; HEATER_BIN=$HEATER
  MGMT_NODES=$(compgen -G '/dev/et*_mgmt' | wc -l)    # a listing of /dev: no device node is opened
  ps_list() { ps -eo pid=,args=; }
fi
if [ -n "${V3_DEVICE:-}" ]; then log "nv: V3_DEVICE is set: NV runs only on single-card hosts, without it"; exit 2; fi
if [ "$MGMT_NODES" != 1 ]; then
  log "nv: this host has $MGMT_NODES management nodes: NV runs only on a host with exactly one card (the stock dev_mngt_service opens every card's node)"; exit 2
fi
ENVTXT=$("${NVPY[@]}" env --card "$CARD" --pass "$PASS" --mode "$MODE" --data "$DATA_ROOT") || { log "nv: refused (above)"; exit 2; }
eval "$ENVTXT"
[ -n "$NV_SKIP" ] && { log "nv p$PASS: $NV_SKIP: not run"; exit 0; }
dry || DMS=$NV_DMS_PATH
dry && export NV_STUB_FW=$NV_FW_EXPECT
NVROOT=$DATA_ROOT/nv                                   # the NV state file, the NV STOP file, ALERT copies, the release
STOPF=$CTL/STOP
mkdir -p "$NVROOT"
ts() { awk -v a="$1" -v s="$SCALE" 'BEGIN { printf "%.3f", a * s }'; }        # a nv.json time, scaled in dry runs
tms() { awk -v a="$1" -v s="$SCALE" 'BEGIN { printf "%d", a * s * 1000 }'; }
nap() { sleep "$(ts "$1")"; }
until_ms() { local d=$(( $1 - $(now_ms) )); [ "$d" -gt 0 ] && sleep "$(awk -v d="$d" 'BEGIN { printf "%.3f", d / 1000 }')"; return 0; }
jl() { "${NVPY[@]}" jline "$@"; }
stop_requested() { [ -e "$STOPF" ] || [ -e "$NVROOT/STOP" ]; }
# another claims-v3 queue or block on this host (DV2's validation on aifoundry2, say): NV's own runner and blocks aside
other_queue() {
  ps_list | awk -v me=$$ '$1 != me' | grep -E 'tools/claims-v3/(queue\.sh|[A-Za-z0-9_.-]+/(block|run_queue|run-queue|probe)\.sh)' |
    grep -v 'tools/claims-v3/nv/' | head -3 | tr '\n' ';'
}

# ---- the gate (no device access, and before our own lock: et-who --check counts a lock we hold as held)
if ! dry || [ -n "${NV_DRY_CHECK_PREDICTIONS:-}" ]; then
  if ! sha256sum -c --quiet "$WD/PREDICTIONS.sha256" > /dev/null 2>&1; then
    log "nv p$PASS: refused: $WD/PREDICTIONS.sha256 is missing or does not check (the predictions are fixed before any card write: freeze.sh --predictions)"; exit 2
  fi
fi
if [ -n "$NV_RELEASE_FILE" ] && [ ! -e "$NVROOT/$NV_RELEASE_FILE" ]; then
  log "nv p$PASS: refused: $CARD is not released for NV ($NVROOT/$NV_RELEASE_FILE is missing; DESIGN.md §8)"; exit 2
fi
if [ "$NV_ROLE" = val ] && [ "$MODE" = full ]; then
  if dry && [ -n "${NV_DRY_SKIP_LOCK:-}" ]; then log "nv: DRY: freeze check skipped"
  elif ! sha256sum -c --quiet "$WD/LOCK.sha256" > /dev/null 2>&1 || ! sha256sum -c --quiet "$WD/PREREG.sha256" > /dev/null 2>&1; then
    log "nv p$PASS: refused: a validation pass needs every file in $WD/LOCK.sha256 and $WD/PREREG.sha256 as frozen"; exit 2
  fi
fi
oq=$(other_queue)
[ -n "$oq" ] && { log "nv p$PASS: another claims-v3 queue or block runs on this host: $oq not starting"; exit 3; }
alerts=$(ls "$CTL"/ALERT-NV-*.json "$NVROOT"/ALERT-NV-*.json 2>/dev/null | tr '\n' ' ')
[ -n "$alerts" ] && { log "nv p$PASS: refused: unresolved alert(s): $alerts(a person must look first)"; exit 1; }
if stop_requested; then log "nv p$PASS: a STOP file is present ($STOPF or $NVROOT/STOP): not starting"; exit 0; fi
if [ -e "$NVROOT/NV-STATE.json" ] && grep -q '"state": *"dirty"' "$NVROOT/NV-STATE.json"; then
  j=$(jl kind=STATE why="the state file is dirty: an earlier block set the rail and never verified its restore" state="$(cat "$NVROOT/NV-STATE.json")" t_ms="$(now_ms)" card="$CARD" pass="$PASS")
  echo "$j" > "$CTL/ALERT-NV-STATE.json"; cp "$CTL/ALERT-NV-STATE.json" "$NVROOT/"; touch "$STOPF"
  log "nv p$PASS: ALERT STATE: $NVROOT/NV-STATE.json is dirty; STOP set"; exit 1
fi
others_present && exit 3
ours_running && { log "nv: one of our own device processes is running: not starting"; exit 3; }
if dry; then echo "DRY et-who --check (stub)" >&2; fi
command -v "$ETWHO" > /dev/null || { log "nv: et-who is not installed: not starting"; exit 2; }
"$ETWHO" --check > /dev/null 2>&1; rc=$?
[ "$rc" = 0 ] || { log "nv p$PASS: et-who --check says $rc (1 held, 2 failed): not starting"; exit 3; }

# ---- the block: its directory, the card lock, the record of the code
OUT=$DATA_ROOT/$NV_EXP/p$PASS
if [ -e "$OUT/block.json" ] && [ -z "${V3_FORCE:-}" ]; then log "$NV_EXP p$PASS already done"; exit 0; fi
if [ -d "$OUT" ]; then
  case "$OUT" in "$V3_ROOT"/build/claims-v3-dry/*) rm -rf "$OUT" ;;
    *) mv "$OUT" "$OUT.attempt-$(date +%s)"; log "earlier attempt of $NV_EXP p$PASS set aside" ;; esac
fi
LK=/run/lock/etsoc-shire$NV_DMS_IDX.lock
if ! dry; then
  [ -e "$LK" ] || { log "nv: $LK is missing: not starting"; exit 2; }
  exec 9<>"$LK"; flock -n 9 || { log "nv: card lock $LK is held by another process: not starting"; exit 3; }
fi
mkdir -p "$OUT/dms"
BLOCK_T0=$(now_ms); DIE0=null; DIE1=null
{ sha256sum tools/claims-v3/lib.sh "$WD"/*.sh "$WD"/*.py "$WD"/*.json "$WD"/*.md \
    tools/claims-v3/wire/configs.json workloads/enercat/analyze_wire.py workloads/enercat/run_wire.py
  dry || sha256sum "$ETT" "$ENC" "$DMS"
  dry || [ -z "$NV_HEATER" ] || sha256sum "$HEATER_BIN"; } > "$OUT/code.sha256" 2>/dev/null
command -v et-lab-manifest > /dev/null && timeout 30 et-lab-manifest > "$OUT/manifest.txt" 2>&1
echo "$CARD $NV_EXP pass $PASS mode $MODE role $NV_ROLE levels [$NV_LEVELS] base $NV_BASE_MV dms_index $NV_DMS_IDX spare ${NV_SPARE:-0} replaces ${NV_REPLACES:-none} needed $NV_NEEDED${NV_NEEDED_PROVISIONAL:+ (provisional)} heater ${NV_HEATER:-0} et_devices ${ET_DEVICES:-unset} scale $SCALE $(date +%FT%T)" >> "$OUT/run.log"
log "$NV_EXP p$PASS begins ($MODE, levels $NV_LEVELS) -> $OUT"

# ---- device calls
DMS_OUT=; DMS_CWD=
dms() {  # dms <tag> <args...>: one dev_mngt_service call under timeout -k 3 10; output in $DMS_OUT; returns its status
  local tag=$1 n t0 rc; shift
  # numbered through a file: the get_* helpers below run in command substitutions (subshells)
  n=$(( $(cat "$OUT/dms/.n" 2>/dev/null || echo 0) + 1 )); echo "$n" > "$OUT/dms/.n"
  DMS_OUT=$OUT/dms/$(printf %03d "$n")-$tag.txt
  dry && echo "DRY dms: timeout -k 3 10 dev_mngt_service $* -n $NV_DMS_IDX" >&2
  t0=$(now_ms)
  ( if [ -n "$DMS_CWD" ]; then cd "$DMS_CWD" || exit 99; fi
    exec timeout -k 3 10 env -u ET_DEVICES "$DMS" "$@" -n "$NV_DMS_IDX" ) > "$DMS_OUT" 2>&1 < /dev/null; rc=$?
  [ "$rc" = 0 ] || : > "$OUT/dms/.failed"           # a later verification drains the queue first (a late reply)
  jl tag="$tag" args="$*" rc="$rc" t0_ms="$t0" t1_ms="$(now_ms)" out="${DMS_OUT##*/}" >> "$OUT/dms.jsonl"
  return $rc
}
dms_ok() { [ "$1" = 0 ] && "${NVPY[@]}" dms ok "$DMS_OUT"; }
get_module() { local rc; dms get-module -m DM_CMD_GET_MODULE_VOLTAGE -u "$NV_U_GET"; rc=$?; dms_ok $rc && "${NVPY[@]}" dms module "$DMS_OUT"; return $rc; }
get_asic()   { local rc; dms get-asic -m DM_CMD_GET_ASIC_VOLTAGE -u "$NV_U_GET"; rc=$?; dms_ok $rc && "${NVPY[@]}" dms asic "$DMS_OUT"; return $rc; }
get_nocmhz() { local rc; dms get-freq -m DM_CMD_GET_ASIC_FREQUENCIES -u "$NV_U_GET"; rc=$?; dms_ok $rc && "${NVPY[@]}" dms nocmhz "$DMS_OUT"; return $rc; }
get_temps()  { local rc; dms get-temp -m DM_CMD_GET_MODULE_CURRENT_TEMPERATURE -u "$NV_U_GET"; rc=$?; dms_ok $rc && "${NVPY[@]}" dms temps "$DMS_OUT"; return $rc; }
get_uptime() { local rc; dms uptime -m DM_CMD_GET_MODULE_UPTIME -u "$NV_U_GET"; rc=$?; dms_ok $rc && "${NVPY[@]}" dms uptime "$DMS_OUT"; return $rc; }
vmin_snap() {  # vmin_snap <tag>: GET_VMIN_LUT into $OUT/vmin-<tag>/; prints the table's sha256 (nothing if it failed)
  local d=$OUT/vmin-$1 rc
  mkdir -p "$d"; DMS_CWD=$d
  dms "vmin-$1" -m DM_CMD_GET_VMIN_LUT -u "$NV_U_GET"; rc=$?
  DMS_CWD=
  [ "$rc" = 0 ] && [ -s "$d/$NV_VMIN_FILE" ] && sha256sum < "$d/$NV_VMIN_FILE" | cut -c1-64
  return 0
}
asic_ok() { awk -v a="$1" -v t="$2" -v f="$NV_ASIC_TOL" 'BEGIN { exit !(a != "" && a >= t * (1 - f) && a <= t * (1 + f)) }'; }
# the windows' rule for the on-die monitor: within die_tol_mv of the level scaled by the block's own reading at 485 mV
die_ok() { awk -v a="$1" -v l="$2" -v r="$DIE_REF" -v b="$NV_BASE_MV" -v t="$NV_DIE_TOL" 'BEGIN { d = a - l * r / b; if (d < 0) d = -d; exit !(a != "" && r != "" && d <= t) }'; }
step() { jl "$@" pass="$PASS" t_ms="$(now_ms)" >> "$OUT/steps.jsonl"; }
state() { jl state="$1" mv="$2" card="$CARD" exp="$NV_EXP" pass="$PASS" t_ms="$(now_ms)" > "$NVROOT/NV-STATE.json"; }
drain() { dms drain -m DM_CMD_GET_MODULE_POWER -u "$NV_U_GET" > /dev/null || true; }

# The rail. CUR_MV is what the rail was last verified at ("?" after an unverified set); DIRTY is set from just before
# the first set until a restore is verified; SET_MADE once any set was issued.
CUR_MV=?; DIRTY=; NO_RESTORE=; STEP_WHY=; VERIFY_WHY=; SET_MADE=; NV_BL2=; NV_BL2_OK=; DIE_REF=; UP0=; VMIN0=; HI0=; VMIN_AFTER_SET=; FLASH_SEEN=
nv_set() {  # the only place a set is issued; any level but 485, 540 and 600 mV is refused here, whatever nv.json says
  local mv=$1 arg a b c
  case "$mv" in 485|540|600) ;; *) log "nv_set: $mv mV refused"; return 2 ;; esac
  case " $NV_ALLOWED " in *" $mv "*) ;; *) log "nv_set: $mv mV is not in nv.json allowed_mv"; return 2 ;; esac
  # hard-coded: never on BL2 below 0.19.0, whose set also writes the value to the card's flash as its boot voltage
  IFS=. read -r a b c <<< "${NV_BL2:-}"
  case "${a:-x}${b:-x}${c:-x}" in *[!0-9]*) log "nv_set: BL2 version '${NV_BL2:-}' not read: refused"; return 2 ;; esac
  if [ "$a" -eq 0 ] && [ "$b" -lt 19 ]; then log "nv_set: BL2 $NV_BL2 is below 0.19.0 (its set writes the flash): refused"; return 2; fi
  [ "${NV_BL2_OK:-}" = 1 ] || { log "nv_set: BL2 not checked against nv.json min_bl2: refused"; return 2; }
  arg=${NV_SET_ARG//\{mv\}/$mv}
  [ "$arg" = "NOC,$mv" ] || { log "nv_set: the set argument '$arg' is not NOC,$mv: refused"; return 2; }
  state dirty "$mv"; DIRTY=1; SET_MADE=1                  # before the call: from here a crash leaves the state dirty
  dms "set$mv" -m DM_CMD_SET_MODULE_VOLTAGE -v "$arg" -u "$NV_U_SET"
}
LAST_READ=
verify_base() {  # the rail is back at the base only if: a drain first when an earlier call failed (a late reply is
  # matched by tag alone); two fresh module reads verify_gap s apart both read the base; and the on-die monitor reads
  # within asic_tol of the base (an independent path: 540 mV is 11% away)
  local r1 r2 a
  if [ -e "$OUT/dms/.failed" ]; then drain; rm -f "$OUT/dms/.failed"; fi
  r1=$(get_module); nap "$NV_T_VERIFY_GAP"; r2=$(get_module); a=$(get_asic)
  step what=verify_base r1="${r1:-null}" r2="${r2:-null}" asic_mv="${a:-null}"
  LAST_READ=${r2:-${r1:-none}}
  if [ "$r1" = "$NV_BASE_MV" ] && [ "$r2" = "$NV_BASE_MV" ] && asic_ok "${a:-}" "$NV_BASE_MV"; then
    CUR_MV=$NV_BASE_MV; DIRTY=; state clean "$NV_BASE_MV"; return 0
  fi
  VERIFY_WHY="module reads '${r1}' and '${r2}', on-die '${a}'"
  CUR_MV=?
  return 1
}
goto_level() {  # goto_level <mV>: set (if the rail is elsewhere) and verify; 0 ok, 1 failed (STEP_WHY)
  local mv=$1 rc cur asic
  if [ "$CUR_MV" != "$mv" ]; then
    nv_set "$mv"; rc=$?
    step what=set mv="$mv" rc="$rc" out="${DMS_OUT##*/}"
    CUR_MV=?
    if [ "$rc" != 0 ] || ! "${NVPY[@]}" dms ok "$DMS_OUT"; then STEP_WHY="the set to $mv mV failed (rc $rc)"; return 1; fi
  fi
  if [ "$mv" = "$NV_BASE_MV" ] && [ -n "$DIRTY" ]; then
    verify_base && return 0
    STEP_WHY="back at $mv mV but not verified: $VERIFY_WHY"; return 1
  fi
  cur=$(get_module); rc=$?
  [ "$cur" = "$mv" ] || { STEP_WHY="read-back after the set to $mv: '${cur}' (rc $rc)"; step what=readback mv="$mv" got="${cur:-null}" rc="$rc"; return 1; }
  CUR_MV=$mv
  if [ -z "$VMIN_AFTER_SET" ]; then   # once, after the first set off the base: was the set written to the flash?
    VMIN_AFTER_SET=$(vmin_snap after-set)
    step what=vmin_after_set mv="$mv" sha256="${VMIN_AFTER_SET:-null}"
    if [ -n "$VMIN_AFTER_SET" ] && [ "$VMIN_AFTER_SET" != "$VMIN0" ]; then
      FLASH_SEEN=1; STEP_WHY="the VMIN table changed after the set to $mv mV: the set was written to the card's flash"; return 1
    fi
  fi
  asic=$(get_asic)
  step what=verify mv="$mv" module_mv="$cur" asic_mv="${asic:-null}"
  asic_ok "${asic:-}" "$mv" || { STEP_WHY="the on-die monitor reads '${asic}' mV at $mv mV (tolerance $NV_ASIC_TOL)"; return 1; }
  return 0
}
nv_restore() {  # back to the base and verified (verify_base), up to restore_tries times, waiting restore_wait s
  # whenever the card does not answer (a watchdog reset brings it back at its boot value); 0 verified, 1 not
  local i cur rc
  for i in $(seq 1 "$NV_RESTORE_TRIES"); do
    cur=$(get_module); LAST_READ=${cur:-none}
    if [ -n "$cur" ]; then
      if [ "$cur" != "$NV_BASE_MV" ]; then nv_set "$NV_BASE_MV"; rc=$?; step what=restore_set mv="$NV_BASE_MV" rc="$rc" found="$cur" try="$i"; nap 1; fi
      if verify_base; then step what=restore_verified mv="$NV_BASE_MV" try="$i"; return 0; fi
      step what=restore_unverified try="$i" why="$VERIFY_WHY"
    else step what=restore_noread try="$i"; nap "$NV_T_RESTORE_WAIT"; fi
  done
  if verify_base; then step what=restore_verified mv="$NV_BASE_MV" try=last; return 0; fi
  step what=restore_failed found="$LAST_READ"; return 1
}
alert() {  # alert <KIND> <why>: ALERT-NV-<KIND>.json here and in build/claims-v3/, and the host's STOP file
  local j; j=$(jl kind="$1" why="$2" card="$CARD" pass="$PASS" exp="$NV_EXP" cur_mv="$CUR_MV" base_mv="$NV_BASE_MV" t_ms="$(now_ms)" out="$OUT")
  echo "$j" > "$CTL/ALERT-NV-$1.json"; echo "$j" > "$NVROOT/ALERT-NV-$1.json"; echo "$j" > "$OUT/ALERT-NV-$1.json"
  touch "$STOPF"
  log "ALERT $1: $2 -- ${CTL#"$V3_ROOT"/}/ALERT-NV-$1.json written and ${STOPF#"$V3_ROOT"/} set: every queue on this host stops"
}

# ---- the restore guardian (a kill -9, the OOM killer or a crash would otherwise leave the rail stepped and let the
# kernel release the card lock at once): a subshell that holds the lock's descriptor too, polls the block, and if the
# block dies with the state file dirty, waits for our device processes to end, restores and verifies the base
# (alerting if it cannot), and only then exits, releasing the lock. finish stops it after its own restore.
GPID=
start_guard() {
  local bpid=$$ bst
  bst=$(awk '{print $22}' "/proc/$$/stat" 2>/dev/null)
  rm -f "$OUT/.guard-stop"
  (
    # shellcheck disable=SC2086
    trap '' $NV_SIGS
    trap - EXIT
    alive() { [ -n "$bst" ] && [ "$(awk '{print $22}' "/proc/$bpid/stat" 2>/dev/null)" = "$bst" ]; }
    while alive && [ ! -e "$OUT/.guard-stop" ]; do sleep 0.5; done
    [ -e "$OUT/.guard-stop" ] && exit 0
    grep -q '"state": *"dirty"' "$NVROOT/NV-STATE.json" 2>/dev/null || exit 0
    log "guardian: block $bpid died with the rail dirty: waiting for its device processes, then restoring"
    lim=$(( $(now_ms) + $(tms "$NV_T_GUARD_WAIT_MAX") ))
    while [ "$(now_ms)" -lt "$lim" ] && pgrep -u "$(id -u)" -f -- "$DMS|$ETT|$ENC|$HEATER_BIN" > /dev/null 2>&1; do sleep 0.2; done
    DIRTY=1; CUR_MV=?; WPID=
    if nv_restore; then
      ok=true; note="the block process died (kill -9, OOM or crash) with the rail dirty; the guardian restored $NV_BASE_MV mV and verified it"
      log "guardian: rail restored to $NV_BASE_MV mV and verified"
    else
      ok=false; note="the block process died with the rail dirty and the guardian could not verify a restore (last read $LAST_READ)"
      alert RESTORE "$note"
    fi
    [ -e "$OUT/block.json" ] || jl --compact exp="$NV_EXP" pass="$PASS" card="$CARD" mode="$MODE" levels="$NV_LEVELS" \
      t0_ms="$BLOCK_T0" t1_ms="$(now_ms)" restored="$ok" status=fail guardian=true note="$note" > "$OUT/block.json"
  ) >> "$OUT/run.log" 2>&1 < /dev/null &
  GPID=$!
}
stop_guard() { [ -n "$GPID" ] || return 0; : > "$OUT/.guard-stop"; wait "$GPID" 2>/dev/null; GPID=; }

# ---- the heater (a governor-free card: below ~68 C its governor lifts the clock off 600 MHz; lib.sh GOV_FREE)
LAST_DIE=
heater_launch() {  # one 2 s launch (timeout -k 3 10), marked in marks.jsonl so analyze_wire keeps it out of every bracket
  local t0 rc
  t0=$(now_ms)
  dry && echo "DRY heater: timeout -k 3 10 heater $NV_HEATER_ARGS" >&2
  # shellcheck disable=SC2086  # the heater's arguments: simple tokens
  timeout -k 3 10 "$HEATER_BIN" $NV_HEATER_ARGS > /dev/null 2>> "$OUT/heater.err" < /dev/null; rc=$?
  printf '{"kind":"heater","cfg":"%s","pass":%s,"t_start_ms":%s,"t_end_ms":%s,"rc":%s}\n' "$1" "$PASS" "$t0" "$(now_ms)" "$rc" >> "$OUT/marks.jsonl"
  nap "$NV_T_HEATER_GAP"
  return $rc
}
heat_to() {  # heat to heat_c under the lock; the die from GET_MODULE_CURRENT_TEMPERATURE between launches
  local i t c
  for i in $(seq 1 "$NV_HEAT_MAX"); do
    t=$(get_temps); c=${t%% *}
    echo "{\"t_ms\":$(now_ms),\"die_c\":${c:-null}}" >> "$OUT/heat.jsonl"
    [ -n "$c" ] || return 1
    LAST_DIE=$c
    [ "$c" -ge "$NV_HEAT_C" ] && return 0
    heater_launch heat || return 1
  done
  return 1
}
warm_if_cool() {  # before an idle window or a configuration: one launch if the last reading is below warm_c
  [ -n "$NV_HEATER" ] || return 0
  [ -n "$LAST_DIE" ] && [ "${LAST_DIE%.*}" -ge "$NV_WARM_C" ] && return 0
  heater_launch "$1"
}

# ---- sampler windows (the sampler never outlives one window: at most 10 s on the management node)
WPID=; WIN_N=0; WIN_WHY=; WIN_ST=; WIN_CHK=; SEG_IDLE_W=; BURST_TIMEOUT=; BURST_RC=
FIRST_MAX_MS=$(tms "$NV_T_FIRST_LINE_MAX"); LATEST_MS=$(tms "$NV_T_BURST_LATEST_AFTER_LAUNCH")
if dry; then   # compressed time: python stubs need ~50 ms to start, so the start limits get a floor
  [ "$FIRST_MAX_MS" -lt 400 ] && FIRST_MAX_MS=400
  m=$(( FIRST_MAX_MS + $(tms "$NV_T_PRE_BURST") + 300 )); [ "$LATEST_MS" -lt "$m" ] && LATEST_MS=$m
fi
stop_window() {  # SIGTERM (ettelem finishes its request); 4 s later a stuck one is killed and the queue drained
  local p=${WPID:-} i c
  [ -n "$p" ] || return 0
  kill -TERM "$p" 2>/dev/null
  for i in $(seq 1 40); do kill -0 "$p" 2>/dev/null || break; sleep 0.1; done
  if kill -0 "$p" 2>/dev/null; then
    log "sampler $p ignored SIGTERM for 4 s: SIGKILL and drain"
    for c in $(pgrep -P "$p"); do kill -KILL "$c" 2>/dev/null; done; kill -KILL "$p" 2>/dev/null; sleep 1; drain
  fi
  wait "$p" 2>/dev/null; WPID=
}
wait_window() {  # the sampler ends by itself (--seconds, or timeout -k 3 10); allow 13.5 s from its launch, then stop it
  local p=$WPID lim=$(( $1 + $(tms 13.5) ))
  while kill -0 "$p" 2>/dev/null && [ "$(now_ms)" -lt "$lim" ]; do sleep 0.05; done
  if kill -0 "$p" 2>/dev/null; then stop_window; WIN_WHY=sampler_overran; return 1; fi
  wait "$p" 2>/dev/null; WPID=; return 0
}
# window <idle|idle_wait|burst> <seg> <mV> <cfg> <fill end ms> [burst args...]: one sampler process (--seconds 9 under
# timeout -k 3 10); for a burst, the burst starts >= pre_burst s after the sampler's first line and >= fill_to_burst_min
# s after the fill, and never later than burst_latest_after_launch s after the sampler's launch (else "late": 2, the
# caller repeats the configuration). Telemetry, launches and the check go to the pass's files only if the window is
# good. Returns 0 ok, 1 bad (WIN_ST: the check's status, or no_sampler/sampler_overran/burst_timeout), 2 late.
window() {
  local kind=$1 seg=$2 lv=$3 cfg=$4 fe=$5; shift 5
  local raw=$OUT/win.raw try L F= tb=0 brc=null n=0 chk crc
  WIN_N=$((WIN_N + 1)); WIN_WHY=; WIN_ST=; WIN_CHK=
  for try in $(seq 1 "$NV_SAMPLER_ATTEMPTS"); do
    : > "$raw"; L=$(now_ms)
    dry && echo "DRY window $WIN_N ($kind $cfg @ $lv): timeout -k 3 10 ettelem sample --seconds $NV_T_SAMPLER_SECONDS --every-ms 100" >&2
    timeout -k 3 10 "$ETT" sample --seconds "$NV_T_SAMPLER_SECONDS" --every-ms 100 > "$raw" 2>> "$OUT/ettelem.err" < /dev/null &
    WPID=$!
    local lim=$(( L + FIRST_MAX_MS ))
    while [ "$(now_ms)" -lt "$lim" ]; do grep -q '^{' "$raw" 2>/dev/null && { F=$(now_ms); break; }; sleep 0.02; done
    [ -n "$F" ] && break
    stop_window
    echo "window $WIN_N: sampler start $try gave no line in ${NV_T_FIRST_LINE_MAX} s" >> "$OUT/run.log"
    [ "$try" = 3 ] && drain
    nap "$NV_T_SAMPLER_RETRY_WAIT"
  done
  if [ -z "$F" ]; then WIN_ST=no_sampler; return 1; fi
  if [ "$kind" = burst ]; then
    tb=$(( F + $(tms "$NV_T_PRE_BURST") )); local tf=$(( fe + $(tms "$NV_T_FILL_TO_BURST_MIN") ))
    [ "$tf" -gt "$tb" ] && tb=$tf
    if [ "$tb" -gt $(( L + LATEST_MS )) ]; then
      wait_window "$L"; grep '^{' "$raw" >> "$OUT/telemetry-rejected.jsonl"
      jl win="$WIN_N" kind="$kind" seg="$seg" mv="$lv" cfg="$cfg" status=late t_launch_ms="$L" t_first_ms="$F" >> "$OUT/windows-rejected.jsonl"
      WIN_ST=late; return 2
    fi
    until_ms "$tb"
    dry && echo "DRY burst: timeout -k 3 10 enercat_host $* --seconds 3 --window 240000000 --budget 8" >&2
    timeout -k 3 10 "$ENC" "$@" --seconds 3 --window 240000000 --budget 8 > "$OUT/burst.out" 2>> "$OUT/host.err" < /dev/null
    brc=$?; BURST_RC=$brc
    # a burst that timeout stopped may leave a kernel running: no further set until the rail is back at its idle
    case "$brc" in 124|137) BURST_TIMEOUT=1 ;; esac
    n=$(grep -c '^ENERCAT {' "$OUT/burst.out")
  fi
  wait_window "$L" || { WIN_ST=$WIN_WHY; }
  chk=$("${NVPY[@]}" wincheck "$raw" --level "$lv" --kind "$kind" --die-ref "${DIE_REF:-$NV_BASE_MV}" --hi-ref "${HI0:-0}"); crc=$?
  WIN_CHK=$chk
  LAST_DIE=$(echo "$chk" | sed -n 's/.*"die_mean_last_c": *\([0-9.]*\).*/\1/p')
  [ -z "$WIN_ST" ] && [ "$kind" = burst ] && case "$brc" in 124|137) WIN_ST=burst_timeout ;; esac
  [ -z "$WIN_ST" ] && [ "$crc" != 0 ] && WIN_ST=$(echo "$chk" | sed -n 's/.*"status": *"\([a-z_]*\)".*/\1/p')
  [ -z "$WIN_ST" ] && [ "$kind" = burst ] && [ "$n" = 0 ] && WIN_ST=no_launches
  local rec
  rec=$(jl win="$WIN_N" kind="$kind" seg="$seg" mv="$lv" cfg="$cfg" try="$try" t_launch_ms="$L" t_first_ms="$F" t_burst_ms="$tb" \
          fill_end_ms="$fe" burst_rc="$brc" launches="$n" status="${WIN_ST:-ok}" check="$chk")
  if [ -z "$WIN_ST" ]; then
    grep '^{' "$raw" >> "$OUT/telemetry.jsonl"; echo "$rec" >> "$OUT/windows.jsonl"
    [ "$kind" = burst ] && sed -n "s|^ENERCAT {|{\"host\":\"$CARD\",\"pass\":$PASS,\"cfg\":\"$cfg@$lv\",\"nv_mv\":$lv,\"seg\":$seg,\"win\":$WIN_N,|p" "$OUT/burst.out" >> "$OUT/runs.jsonl"
    rm -f "$raw" "$OUT/burst.out"; return 0
  fi
  grep '^{' "$raw" >> "$OUT/telemetry-rejected.jsonl"; echo "$rec" >> "$OUT/windows-rejected.jsonl"
  [ -e "$OUT/burst.out" ] && sed -n "s|^ENERCAT {|{\"cfg\":\"$cfg@$lv\",\"win\":$WIN_N,|p" "$OUT/burst.out" >> "$OUT/runs-rejected.jsonl"
  rm -f "$raw" "$OUT/burst.out"
  echo "window $WIN_N ($kind $cfg @ $lv): $WIN_ST" >> "$OUT/run.log"
  return 1
}
fill() {  # fill <pattern> <operands> <cfg>: the scratchpads' image for the next burst (tstore_uniq, as E42); FILL_END
  local t0 rc
  t0=$(now_ms)
  dry && echo "DRY fill: timeout -k 3 10 enercat_host --pattern $1 --operands $2 --slice-bytes 32K --scp --seconds 0.3 --window 60000000 --budget 8" >&2
  timeout -k 3 10 "$ENC" --pattern "$1" --operands "$2" --slice-bytes 32K --scp --seconds 0.3 --window 60000000 --budget 8 \
    > /dev/null 2>> "$OUT/host.err" < /dev/null
  rc=$?; FILL_END=$(now_ms)
  printf '{"kind":"fill","cfg":"%s","pass":%s,"t_start_ms":%s,"t_end_ms":%s,"rc":%s}\n' "$3" "$PASS" "$t0" "$FILL_END" "$rc" >> "$OUT/marks.jsonl"
  return $rc
}
PCIE_CHECKED=
pcie_check() {  # the device layer names the node it opened ("PCIe target: /dev/etN_ops"): it must be this card's
  local seen bad
  [ -n "$PCIE_CHECKED" ] && return 0
  PCIE_CHECKED=1
  seen=$(grep -ho 'PCIe target: *[^ ]*' "$OUT/host.err" "$OUT/ettelem.err" 2>/dev/null | awk '{print $3}' | sort -u | tr '\n' ' ')
  bad=$(echo "$seen" | tr ' ' '\n' | grep . | grep -v "^/dev/et${NV_DMS_IDX}_" | tr '\n' ' ')
  echo "PCIe targets seen: ${seen:-none printed}" >> "$OUT/run.log"
  if [ -n "$bad" ]; then touch "$NVROOT/STOP"; finish fail "the fill opened $bad, not card $NV_DMS_IDX's node (NV STOP set)" 1; fi
  return 0
}
foreign_device() {  # another user's device process (or a CI job) appeared mid-block
  dry && { [ -n "${NV_STUB_FOREIGN:-}" ]; return; }
  ps -eo uid=,comm= | awk -v me="$(id -u)" -v re="$OTHER_COMM" '$1 != me && $2 ~ re {f=1} END {exit !f}'
}
wait_idle_rail() {  # after a burst that timeout stopped: before the next set, an idle window at the current level must
  # show the rail back within idle_back_w of the segment's idle (three windows at most; then the restore goes ahead)
  local i m
  case "$CUR_MV" in 485|540|600) ;; *) return 0 ;; esac
  for i in 1 2 3; do
    window idle_wait wait "$CUR_MV" - 0
    m=$(echo "$WIN_CHK" | sed -n 's/.*"noc_w_idle_mean": *\([0-9.]*\).*/\1/p')
    step what=idle_wait try="$i" mv="$CUR_MV" idle_w="${m:-null}" seg_idle_w="${SEG_IDLE_W:-null}"
    if [ -n "$m" ] && [ -n "$SEG_IDLE_W" ] && awk -v m="$m" -v s="$SEG_IDLE_W" -v d="$NV_IDLE_BACK_W" 'BEGIN { exit !(m <= s + d) }'; then
      return 0
    fi
  done
  log "the rail did not come back to its idle in 3 windows: restoring anyway"
  return 1
}

# ---- the end: every way out comes through here (the EXIT trap and every signal trap included)
FINISHED=; IN_FINISH=
finish() {  # finish <ok|fail> <note> <exit code> [ALERT kind]
  [ -n "$IN_FINISH" ] && return 0                          # a re-entry (a trap during the restore) changes nothing
  IN_FINISH=1
  # shellcheck disable=SC2086
  trap '' $NV_SIGS                                         # nothing interrupts the restore
  local st=$1 note=$2 rc=$3 ak=${4:-} t up1= vm1= vsame=null restored
  stop_window
  if [ -z "$NO_RESTORE" ] && { [ -n "$DIRTY" ] || [ "$CUR_MV" != "$NV_BASE_MV" ]; } && [ "$CUR_MV" != skip ]; then
    [ -n "$BURST_TIMEOUT" ] && wait_idle_rail
    if nv_restore; then log "rail restored to $NV_BASE_MV mV and verified"
    else
      alert RESTORE "the NoC rail could not be restored to $NV_BASE_MV mV and verified (last read: ${LAST_READ:-none} mV; $note)"
      st=fail; rc=1; note="RESTORE FAILED; $note"; ak=
    fi
  fi
  [ -n "$ak" ] && alert "$ak" "$note"
  if [ -n "$SET_MADE" ]; then                              # a reset, and the flash: both checked after every set
    up1=$(get_uptime)
    if [ -n "$UP0" ] && [ -n "$up1" ] && [ "$up1" -lt "$UP0" ]; then
      alert RESET "the card reset during the block (uptime $UP0 min at the start, $up1 min at the end): a reset clears et-board-clock-guard's TDP 0 and 600 MHz pin on aifoundry3, so the lab admin must re-run the clock guard before anyone measures on this card ($note)"
      st=fail; rc=1; note="CARD RESET; $note"
    fi
    [ -z "$up1" ] && note="$note; uptime not read at the end"
    vm1=$(vmin_snap end)
    if [ -n "$FLASH_SEEN" ]; then vsame=false
    elif [ -n "$VMIN0" ] && [ -n "$vm1" ]; then
      if [ "$vm1" = "$VMIN0" ]; then vsame=true; else
        vsame=false
        alert FLASH "the VMIN table changed during the block (sha256 ${VMIN0:0:16} -> ${vm1:0:16}): a set may have been written to the card's flash as its boot voltage ($note)"
        st=fail; rc=1; note="VMIN TABLE CHANGED; $note"
      fi
    else note="$note; VMIN table not read at the end"; fi
  fi
  t=$(get_temps 2>/dev/null); DIE1=${t%% *}
  restored=$([ -z "$DIRTY" ] && [ -z "$NO_RESTORE" ] && { [ "$CUR_MV" = "$NV_BASE_MV" ] || [ "$CUR_MV" = skip ]; } && echo true || echo false)
  jl --compact exp="$NV_EXP" pass="$PASS" card="$CARD" mode="$MODE" levels="$NV_LEVELS" spare="$([ -n "$NV_SPARE" ] && echo true || echo false)" \
    replaces="${NV_REPLACES:-null}" t0_ms="$BLOCK_T0" t1_ms="$(now_ms)" die_c_start="${DIE0:-null}" die_c_end="${DIE1:-null}" \
    bl2="${NV_BL2:-null}" uptime_min_start="${UP0:-null}" uptime_min_end="${up1:-null}" vmin_same="$vsame" \
    restored="$restored" rail_mv_end="$CUR_MV" status="$st" note="$note" > "$OUT/block.json"
  stop_guard
  log "$NV_EXP p$PASS ends: $st $note"
  FINISHED=1
  exit "$rc"
}
trap '[ -n "$FINISHED" ] || finish fail "the block exited unexpectedly" 1' EXIT
for s in $NV_SIGS; do
  # shellcheck disable=SC2064  # the signal's name is fixed now
  trap "finish fail 'interrupted by SIG$s' 1" "$s"
done
abort_step() {  # a set or read-back went wrong: restore, then an ALERT (a person looks before any further set)
  step what=abort why="$STEP_WHY"
  [ -n "$FLASH_SEEN" ] && finish fail "$STEP_WHY" 1 FLASH
  finish fail "$STEP_WHY" 1 SET
}
abort_window() {  # a window's check failed for good
  local n
  case "$WIN_ST" in
    hot_sensor) touch "$NVROOT/STOP"; finish fail "window $WIN_N: $WIN_ST: a reading reached $NV_SENSOR_MAX_C C (NV STOP set: no further NV block on this card)" 1 ;;
    hot)       # the minion-shire mean reached die_mean_abort_c: restore and fail the pass; a repeat stops NV here
      jl pass="$PASS" win="$WIN_N" t_ms="$(now_ms)" check="$WIN_CHK" >> "$NVROOT/hot-aborts.jsonl"
      n=$(wc -l < "$NVROOT/hot-aborts.jsonl")
      [ "$n" -ge 2 ] && touch "$NVROOT/STOP"
      finish fail "window $WIN_N: hot: the minion-shire mean reached the limit (hot abort $n on this card; NV STOP at 2)" 1 ;;
    volt_reg|volt_die|clock_noc) finish fail "window $WIN_N: $WIN_ST: the card is not in the state that was set" 1 STATE ;;
    current)   # a burst's rail current over the limit in three samples: drop it and restore; a repeat stops NV here
      jl pass="$PASS" win="$WIN_N" t_ms="$(now_ms)" check="$WIN_CHK" >> "$NVROOT/current-aborts.jsonl"
      n=$(wc -l < "$NVROOT/current-aborts.jsonl")
      [ "$n" -ge "$NV_CURRENT_STOP" ] && touch "$NVROOT/STOP"
      finish fail "window $WIN_N: the rail current read over the limit: burst dropped and the rail restored (current abort $n on this card; NV STOP at $NV_CURRENT_STOP)" 1 ;;
    burst_timeout) finish fail "window $WIN_N: the burst overran timeout 10 (rc $BURST_RC): pass abandoned, restored once the rail was idle" 1 ;;
    *) finish fail "window $WIN_N: $WIN_ST" 1 ;;
  esac
}

# ---- pre-flight, one dev_mngt_service call each: identity and BL2, uptime, temperature, rail, on-die, clock, VMIN
miss=
for f in "$DMS" "$ETT"; do [ -x "$f" ] || miss="$miss $f"; done
[ "$MODE" = probe ] || [ -x "$ENC" ] || miss="$miss $ENC"
[ -n "$NV_HEATER" ] && { [ -x "$HEATER_BIN" ] || miss="$miss $HEATER_BIN"; }
[ -n "$miss" ] && { CUR_MV=skip; finish fail "missing:$miss" 1; }
dms fw -m DM_CMD_GET_MODULE_FIRMWARE_REVISIONS -u "$NV_U_GET"
fw=$("${NVPY[@]}" dms fw "$DMS_OUT"); NV_BL2=$("${NVPY[@]}" dms bl2 "$DMS_OUT")
[ "$fw" = "$NV_FW_EXPECT" ] || { CUR_MV=skip; finish fail "identity: firmware release '$fw', expected $NV_FW_EXPECT for $CARD: no set made" 1; }
if ! "${NVPY[@]}" bl2ok "${NV_BL2:-none}"; then
  touch "$NVROOT/STOP"; CUR_MV=skip
  finish fail "BL2 '${NV_BL2}' is below $NV_MIN_BL2: its NoC set also writes the card's flash; no set made, NV STOP set" 2
fi
NV_BL2_OK=1
UP0=$(get_uptime)
[ -n "$UP0" ] || { CUR_MV=skip; finish fail "the card's uptime could not be read (a reset could not be detected): no set made" 1; }
# "<minion-shire mean> <hottest current reading> <highest latched watermark>": the watermarks (the PVT's HILO "High"
# values) hold for hours, so the 90 C rule is on current readings, and on a watermark that rises to 90 C in the block
t=$(get_temps); read -r DIE0 tmax HI0 <<< "$t"
if [ -z "$t" ] || [ "$DIE0" -gt "$NV_START_MAX_C" ] || [ "$tmax" -ge "$NV_SENSOR_MAX_C" ]; then
  CUR_MV=skip; finish fail "temperature at the start: '${t}' (minion-shire mean, hottest current reading, watermark; limits $NV_START_MAX_C and < $NV_SENSOR_MAX_C)" 3
fi
LAST_DIE=$DIE0
cur=$(get_module); rc=$?
if [ "$cur" != "$NV_BASE_MV" ]; then
  if [ -z "$cur" ]; then CUR_MV=skip; finish fail "the rail's voltage could not be read at the start (rc $rc)" 1; fi
  CUR_MV=$cur; NO_RESTORE=1
  finish fail "the rail reads $cur mV at the start, not the base $NV_BASE_MV mV: nothing set, nothing restored" 1 STATE
fi
CUR_MV=$cur
asic=$(get_asic); mhz=$(get_nocmhz)
DIE_REF=$asic
step what=start module_mv="$cur" asic_mv="${asic:-null}" noc_mhz="${mhz:-null}" fw="$fw" bl2="$NV_BL2" uptime_min="$UP0" die_c="$DIE0" hottest_c="$tmax" watermark_c="$HI0"
[ "$mhz" = "$NV_NOC_MHZ" ] || finish fail "the NoC clock reads '${mhz}' MHz at the start, not $NV_NOC_MHZ: not starting" 1
asic_ok "${asic:-}" "$cur" || finish fail "the on-die monitor reads '${asic}' mV at the start (rail $cur mV)" 1
VMIN0=$(vmin_snap start)
[ -n "$VMIN0" ] || finish fail "the VMIN table could not be read at the start: no set made" 1
step what=vmin_start sha256="$VMIN0"
"${NVPY[@]}" plan --card "$CARD" --pass "$PASS" --mode "$MODE" --data "$DATA_ROOT" --json "$OUT/order.json" > "$OUT/plan.tsv" \
  || finish fail "nvlib.py plan failed" 1
mapfile -t PLAN < "$OUT/plan.tsv"
if [ -n "$NV_HEATER" ] && [ "$MODE" != probe ]; then
  heat_to || finish fail "heating to $NV_HEAT_C C gave up (last ${LAST_DIE:-?} C)" 1
fi
start_guard

# ---- the pass
if [ "$MODE" = probe ]; then
  for row in "${PLAN[@]}"; do
    IFS=$'\t' read -r seg lv _ <<< "$row"
    stop_requested && finish fail "stopped by a STOP file" 1
    goto_level "$lv" || abort_step
    if [ "$NV_ROLE" = dev ]; then
      nap "$NV_T_SETTLE_AFTER_SET"
      window idle "$seg" "$lv" - 0 || abort_window
    else
      nap "$NV_T_PROBE_DWELL"                          # the validation card: no power recorded before the freeze
    fi
    c2=$(get_module); a2=$(get_asic); m2=$(get_nocmhz); t2=$(get_temps)
    step what=probe_hold mv="$lv" module_mv="${c2:-null}" asic_mv="${a2:-null}" noc_mhz="${m2:-null}" temps="${t2:-}" die_ref_mv="$DIE_REF"
    [ "$c2" = "$lv" ] || { STEP_WHY="after the dwell the rail reads '${c2}' at $lv mV"; abort_step; }
    asic_ok "${a2:-}" "$lv" || { STEP_WHY="after the dwell the on-die monitor reads '${a2}' at $lv mV (the firmware's 5%)"; abort_step; }
    # the windows' own rule, so that a card the passes would reject is found here, with no power recorded
    die_ok "${a2:-}" "$lv" || { STEP_WHY="after the dwell the on-die monitor reads '${a2}' at $lv mV: more than $NV_DIE_TOL mV off $lv x $DIE_REF / $NV_BASE_MV (the windows' rule)"; abort_step; }
    [ "$m2" = "$NV_NOC_MHZ" ] || { STEP_WHY="the NoC clock reads '${m2}' MHz at $lv mV"; abort_step; }
    read -r tm tt hw <<< "$t2"
    if [ -z "$t2" ] || [ "$tm" -ge "$NV_START_MAX_C" ] || [ "$tt" -ge "$NV_SENSOR_MAX_C" ] || { [ "$hw" -gt "$HI0" ] && [ "$hw" -ge "$NV_SENSOR_MAX_C" ]; }; then
      touch "$NVROOT/STOP"; finish fail "temperature '${t2}' at $lv mV (watermark at the start $HI0; NV STOP set)" 1
    fi
  done
else
  cur_seg=; SKIPS=0
  i=0
  while [ "$i" -lt "${#PLAN[@]}" ]; do
    IFS=$'\t' read -r seg lv cfg fpat fops args <<< "${PLAN[$i]}"
    if [ "$seg" != "$cur_seg" ]; then                      # a new segment: the step, the settle, an idle window
      cur_seg=$seg
      stop_requested && finish fail "stopped by a STOP file before segment $seg" 1
      goto_level "$lv" || abort_step
      echo "segment $seg: $lv mV" >> "$OUT/run.log"
      nap "$NV_T_SETTLE_AFTER_SET"
      warm_if_cool "idle@$lv"
      if ! window idle "$seg" "$lv" - 0; then
        case "$WIN_ST" in short|no_sampler|sampler_overran) window idle "$seg" "$lv" - 0 || abort_window ;; *) abort_window ;; esac
      fi
      SEG_IDLE_W=$(echo "$WIN_CHK" | sed -n 's/.*"noc_w_idle_mean": *\([0-9.]*\).*/\1/p')
      nap "$NV_T_BETWEEN_WINDOWS"
    fi
    stop_requested && finish fail "stopped by a STOP file (segment $seg, before $cfg)" 1
    foreign_device && finish fail "another user's device process appeared (before $cfg @ $lv)" 3
    done_cfg=
    for attempt in 1 2; do
      warm_if_cool "$cfg@$lv"
      frc=1
      for ft in 1 2; do fill "$fpat" "$fops" "$cfg@$lv"; frc=$?; [ "$frc" = 0 ] && break
        echo "fill $cfg @ $lv: rc $frc (try $ft)" >> "$OUT/run.log"; done
      pcie_check
      if [ "$frc" != 0 ]; then echo "$cfg @ $lv: the fill failed twice: no burst (the image would be stale)" >> "$OUT/run.log"; break; fi
      nap "$NV_T_FILL_GAP"
      # shellcheck disable=SC2086  # args: simple tokens
      window burst "$seg" "$lv" "$cfg" "$FILL_END" $args; wrc=$?
      nap "$NV_T_BETWEEN_WINDOWS"
      [ "$wrc" = 0 ] && { done_cfg=1; break; }
      case "$WIN_ST" in late|short|no_sampler|no_launches|sampler_overran) echo "$cfg @ $lv: $WIN_ST, attempt $attempt" >> "$OUT/run.log" ;;
        *) abort_window ;; esac
    done
    if [ -n "$done_cfg" ]; then SKIPS=0; else
      SKIPS=$((SKIPS + 1)); echo "$cfg @ $lv: skipped (${WIN_ST:-fill})" >> "$OUT/run.log"
      [ "$SKIPS" -ge 2 ] && { WIN_ST="two configurations in a row failed (${WIN_ST:-fill})"; abort_window; }
    fi
    i=$((i + 1))
  done
fi

# ---- the restore, verified twice: by nv_restore (two reads and the on-die monitor), and in the telemetry of one
# last idle window (not on the validation card's probe: no power before the freeze)
nv_restore || finish fail "the restore to $NV_BASE_MV mV could not be verified ($VERIFY_WHY)" 1
if [ "$NV_ROLE" = dev ] || [ "$MODE" = full ]; then
  nap "$NV_T_SETTLE_AFTER_SET"
  window idle end "$NV_BASE_MV" - 0 || abort_window
fi
touch "$OUT/runs.jsonl" "$OUT/marks.jsonl"
[ -s "$OUT/telemetry.jsonl" ] && gzip -f "$OUT/telemetry.jsonl"
[ -s "$OUT/telemetry-rejected.jsonl" ] && gzip -f "$OUT/telemetry-rejected.jsonl"
NB=$(cat "$OUT/windows.jsonl" 2>/dev/null | wc -l); NR=$(cat "$OUT/windows-rejected.jsonl" 2>/dev/null | wc -l)
finish ok "$([ -n "${V3_DRY:-}" ] && echo 'dry run: ')$NB windows kept, $NR set aside" 0
