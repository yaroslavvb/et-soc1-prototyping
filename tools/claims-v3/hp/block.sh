#!/usr/bin/env bash
# Heat placement (HP, DESIGN2): one block on the local card, from the tree's root.
#
#   bash tools/claims-v3/hp/block.sh <pass> [--smoke]        (aifoundry1: V3_DEVICE=1; card 0 is never used)
#   V3_DRY=1 bash tools/claims-v3/hp/block.sh <pass>         no device access: an accelerated simulation (README.md)
#   bash tools/claims-v3/hp/block.sh --binhash               the binaries a block would run, with sha256 (no device)
#
# Refused (exit 2) before anything else: aifoundry1 card 0 (V3_DEVICE=0), any block on aifoundry2 (its session is
# a2/block.sh), and a block kind the card may not run (hplib.py ALLOWED: development R1-R3, scouting and the one-shot
# only on aifoundry3; R0, V0 and validation only on aifoundry1 card 1). HP_PARAMS_DIR / HP_PREREG_DIR only with V3_DRY;
# V3_FORCE (a re-run into a finished block's directory) only with V3_DRY for validation and on card 1. A validation
# block needs HP_PREREG_SHA256 (PREREG.md's sha256 as recorded when prereg.py --val printed it). Queues of hp schedules
# start through run_queue.sh (it refuses card 0 before queue.sh could read it).
#
# pass = R*1000 + T*100 + k (hplib.py): R 0 R0 / 1-3 development rounds / 5 V0 (card-1 calibration) / 9 validation;
# T 1 S, 2 L16, 3 L8, 4 G8, 5 CAL (V0), 6 SCOUT (R1b), 7 B1 (aifoundry3's one-shot), 8 PROBE (R0), 9 SMOKE.
# --smoke runs the smoke (T=9) under this pass number, into hp-smoke/.
#
# A block (DESIGN2 §4.3-4.4, §6, §7):
#   1  nobody else on the card (lib others_present, ours_running, the et_soc1 use count; on card 1 also card 0 idle:
#      no process of ours on card 0, no holder of its nodes or lock) else exit 3; the card lock file exists; the
#      binaries exist; the R0 probe of this card exists (every block but the probe itself); validation: the PREREG
#      lock (hplib.py vallock: PREREG.md, every hashed file and binary, params-val against prereg.json);
#   2  lib block_begin (card lock on fd 9, held to the end; die reading; code.sha256); on aifoundry1 card 1 the card-0
#      guard starts and must read <= 85 C (else exit 3: the queue retries);
#   3  the SP log level (O2): a set an earlier block left pending is restored first; WARNING only if this card's probe
#      was ALIVE (params trigb auto; in validation also registered) or for the one-shot, and only when the level
#      found is known (hplib.py level-begin); restored to the level first found on the card, and checked with a dump;
#   4  the runs of hplib.py's plan: burn-in CAL run(s) first, then the placements in a Williams order (S: a seeded
#      shuffle). Each run: its own 10 Hz --reset-ms 1000 sampler and live watcher; ALL24 preheat bursts to the target;
#      idle until the mean's falling S+1 -> S edge (cap 600 s); then Tier L: a chain of 2 s launches until 2 launches
#      have started after the mean first read 66, capped at 150 s (O1: lock held, device released, other-user check
#      between launches); Tier S: one 7 s launch and 10 s of idle. The sampler stops; on a TRIG-B card the SP ring is
#      dumped (sp-<run>.bin);
#   5  void runs (and WORK outside +-5% of the block median) are re-run once at the end of the block (hplib blockcheck,
#      from the block's own plan.json: its round and params; a blockcheck that cannot run fails the block);
#   6  level restored, guard stopped, telemetry gzipped, reduce.py --check-pass, lib block_end.
# Exit codes (V3): 0 ok, 1 fail (3 heater failures, stale sampler, a safety or guard stop), 3 someone else on the card.
set -u
. "$(dirname "${BASH_SOURCE[0]}")/../lib.sh"            # cd's to the tree root; CARD, HEATER, ETTELEM, DATA_ROOT
case "$CARD" in
  aifoundry1-c0) echo "hp: aifoundry1 card 0 is never used (owner decision, DESIGN2 §0): refused" >&2; exit 2 ;;
  aifoundry2) echo "hp: aifoundry2 runs only tools/claims-v3/hp/a2/block.sh (its frozen same-day session): refused" >&2; exit 2 ;;
esac
HP_DIR=tools/claims-v3/hp
. "$HP_DIR/hplib.sh"
if [ "${1:-}" = --binhash ]; then hp_binaries_json; exit 0; fi

PASS=${1:?usage: block.sh <pass> [--smoke]}
case "$PASS" in ''|*[!0-9]*) echo "pass must be a number" >&2; exit 2 ;; esac
PASS=$(( 10#$PASS ))
SMOKE=; [ "${2:-}" = --smoke ] && SMOKE=1
export HP_DATA_DIR=$DATA_ROOT
PLAN_PASS=$PASS; [ -n "$SMOKE" ] && PLAN_PASS=$(( PASS / 1000 * 1000 + 900 + PASS % 100 ))
# the card and block kind (hplib.py ALLOWED) and the override variables, before anything else
why=$("${HPPY[@]}" check-card --pass "$PLAN_PASS" --card "$CARD") || { log "hp: pass $PLAN_PASS on $CARD $why"; exit 2; }
hp_envcheck "$([ $(( PLAN_PASS / 1000 )) = 9 ] && echo val || echo dev)"

# ---- 1. the card must be free; what this block is
others_present && exit 3
ours_running && { log "hp: a device process of this user is running on this card: not starting"; exit 3; }
hp_orphan_guards                        # an orphaned card-0 guard of ours first (it would count as card-0 activity)
hp_card0_check "block start"
hp_lock_present
if ! dry; then
  for b in "$HEATER" "$ETTELEM"; do [ -x "$b" ] || { log "hp: missing $b"; exit 1; }; done
  [ -f "$HEATER_KERNEL" ] || { log "hp: missing the heater kernel $HEATER_KERNEL (every launch loads it with --kernel)"; exit 1; }
fi
N0=$(modcount)
if [ -n "$N0" ] && [ "$N0" != 0 ]; then log "hp: et_soc1 use count $N0: someone holds the card"; exit 3; fi
if [ -n "$SMOKE" ]; then EXPNAME=hp-smoke; else EXPNAME=hp; fi
FIRST=$("${HPPY[@]}" sessionfirst --data "$DATA_ROOT")
PLAN_OUT=$(if [ -n "$SMOKE" ]; then "${HPPY[@]}" plan --pass "$PLAN_PASS" --card "$CARD";
           else "${HPPY[@]}" plan --pass "$PASS" --card "$CARD" --first "$FIRST"; fi) || { log "hp: no plan for pass $PASS"; exit 2; }
while IFS= read -r line; do case "$line" in SET\ *) eval "${line#SET }" ;; esac; done <<< "$PLAN_OUT"
mapfile -t RUNS < <(grep '^RUN ' <<< "$PLAN_OUT")
TYPE=$INFO_type; ROUND=$INFO_round
[ -n "$SMOKE" ] && TYPE=SMOKE

if [ "$TYPE" = PROBE ]; then exec bash "$HP_DIR/probe.sh" "$PASS"; fi
hp_probe_class
if [ -z "$PROBE_CLASS" ] && ! dry; then
  log "hp: no R0 probe on $CARD yet (run pass 801 first: DESIGN2 §3.2, the probe comes before any other card work)"; exit 1
fi
[ -z "$PROBE_CLASS" ] && PROBE_CLASS=$(dry && echo "${HP_DRY_PROBE:-SILENT}")
BINS_JSON=$(hp_binaries_json)
if [ "$ROUND" = val ]; then       # the lock (DESIGN2 §6.3): refuse before touching the card
  VL_BINS=$(mktemp); echo "$BINS_JSON" > "$VL_BINS"; VL_REC=$(mktemp)
  why=$("${HPPY[@]}" vallock --card "$CARD" --bins "$VL_BINS" --data "$DATA_ROOT" --record "$VL_REC") || {
    rm -f "$VL_BINS" "$VL_REC"; log "hp val: PREREG lock: $why"; exit 1; }
  log "hp val: $why"
  rm -f "$VL_BINS"
fi
if [ -n "${INFO_skip:-}" ]; then
  block_begin "$EXPNAME" "$PASS"; [ "$ROUND" = val ] && mv "$VL_REC" "$OUT/prereg-lock.json"
  block_end ok "skipped: $INFO_skip"; exit 0
fi
if [ "$TYPE" = B1 ] && { [ "$CARD" != aifoundry3 ] || [ "$PROBE_CLASS" != STUCK ]; }; then
  block_begin "$EXPNAME" "$PASS"; block_end ok "not applicable: the one-shot runs only on aifoundry3 with a STUCK probe (class ${PROBE_CLASS:-none})"; exit 0
fi

# ---- 2. begin
block_begin "$EXPNAME" "$PASS"
trap 'hp_cleanup' EXIT
sha256sum "$HP_DIR"/*.py "$HP_DIR"/*.sh "$HP_DIR"/placements.json "$HP_DIR"/ettelem-hp/ettelem.cpp tools/claims-v3/queue.sh \
  tools/ettelem/flip_thermal_model.py >> "$OUT/code.sha256" 2>/dev/null
echo "$BINS_JSON" > "$OUT/binaries.json"
for b in "$HEATER" "$ETTELEM" "$ETTELEM_HP"; do [ -f "$b" ] && sha256sum "$b" >> "$OUT/binaries.sha256"; done
[ "$ROUND" = val ] && mv "$VL_REC" "$OUT/prereg-lock.json"      # the PREREG this validation block ran under
"${HPPY[@]}" plan --pass "$PLAN_PASS" --card "$CARD" --first "$FIRST" --json "$OUT/plan.json" > /dev/null 2>&1 || true
[ -n "$SMOKE" ] && echo "$PLAN_OUT" > "$OUT/plan.txt"
: > "$OUT/runs.jsonl"; : > "$OUT/launches.jsonl"; : > "$OUT/marks.jsonl"
command -v et-lab-manifest > /dev/null && ! dry && timeout 30 et-lab-manifest > "$OUT/manifest.txt" 2>&1
mark block_begin "\"type\":\"$TYPE\",\"round\":\"$ROUND\",\"seed\":${INFO_seed:-0},\"first_of_session\":$([ "$FIRST" = 1 ] && echo true || echo false),\"probe_class\":\"$PROBE_CLASS\",\"dry\":$(dry && echo true || echo false),\"overrides\":\"$HP_OVERRIDES\""
# the W_idle proxy's baseline is per session: reset at the session's first block (review F12)
if [ "$FIRST" = 1 ] && [ -n "$GUARD_ON" ]; then
  mkdir -p "$DATA_ROOT/hp"
  echo "{\"session_pass\":$PASS,\"session_start_ms\":$(now_ms),\"W_idle\":null}" > "$DATA_ROOT/hp/session-widle.json"
fi
if [ -n "$GUARD_ON" ]; then
  hp_guard_start || { NO_CARD=; hp_guard_stop; block_end fail "card-0 guard gate: card 0 not <= ${P_guard_gate_c} C or no reading"; exit 3; }
fi

# ---- 3. the log level (O2): only where the probe allows it (review F2: no params value can force WARNING)
hp_level_pending_restore
TRIGB=
if [ "$P_trigb" = auto ]; then
  case "$PROBE_CLASS" in ALIVE|ALIVE_CANDIDATE) TRIGB=1 ;; esac
  [ "$ROUND" = val ] && [ "${P_trigb_registered:-}" != 1 ] && TRIGB=     # the frozen registration (vallock-checked)
fi
[ "$TYPE" = B1 ] && [ "$CARD" = aifoundry3 ] && [ "$PROBE_CLASS" = STUCK ] && TRIGB=1
[ "$TYPE" = SMOKE ] && TRIGB=
if [ -n "$TRIGB" ]; then
  hp_level_begin sp-before               # may clear TRIGB (level unknown: nothing is set)
  [ -n "$TRIGB" ] && hp_sptrace "$OUT/sp-idle.bin"          # the idle ring: the coverage baseline of the first run
fi
mark trigb "\"on\":$([ -n "$TRIGB" ] && echo true || echo false),\"level_found\":\"${LEVEL_FOUND:-}\",\"level_set\":$([ -n "$LEVEL_SET" ] && echo true || echo false)"

# ---- 4. the runs
PRED_NAME=; PRED_E=0
run_one() {   # run_one <idx> <slot> <attempt> <role> <name> <mask> <per> <minions> <tier> <edge> <target>
  local idx=$1 slot=$2 att=$3 role=$4 name=$5 mask=$6 per=$7 mins=$8 tier=$9 edge=${10} target=${11}
  RUN_STOP=; PREHEAT_BURSTS=0; PREHEAT_WHY=; EDGE_OK=; EDGE_T=; EDGE_TAUC=; EDGE_S1=
  CH_T0=; CH_T1=; CH_N=0; CH_F66=; CH_CENS=; CH_RCS=; TRIGB_DUMP=
  hp_guard_refresh
  hp_run_begin "$idx"
  mark run_begin "\"idx\":$idx,\"slot\":$slot,\"attempt\":$att,\"role\":\"$role\",\"name\":\"$name\",\"tier\":\"$tier\""
  case "$tier" in
    L|S)
      if hp_preheat "$target" || [ "$PREHEAT_WHY" = stop_c ]; then
        if [ -z "$RUN_STOP" ] && hp_edge_wait "$edge" "$P_edge_wait_cap_s"; then
          hp_widle_check "$role" "at the edge"
          if [ "$tier" = L ]; then hp_chain "$idx" "$mask" "$per"
          else hp_single "$idx" "$mask" "$per" "$P_S_launch_s" "$P_S_idle_after_s"; fi
        elif [ -z "$RUN_STOP" ]; then
          hp_widle_check "$role" "the edge wait timed out"      # a rise that lifts the rest above the edge (review low)
        fi
      fi ;;
    B1)          # from rest: no preheat, no edge; ONE chain of <= chain_cap_s (O1) of 7 s launches (README)
      hp_chain "$idx" "$mask" "$per" 7 ;;
    SMOKE)       # sampler, 2 preheat bursts, one 2 s launch
      hp_between; hp_launch "$idx" preheat 0xffffffff 24 2 "$RUN_SF"; PREHEAT_BURSTS=1
      hp_between; hp_launch "$idx" preheat 0xffffffff 24 2 "$RUN_SF"; PREHEAT_BURSTS=2
      CH_T0=$(now_ms); hp_between; hp_launch "$idx" single "$mask" "$per" 2 "$RUN_SF"; CH_N=1; CH_RCS=$LAST_RC
      hp_sleep 3; hp_live || true; CH_T1=$(now_ms) ;;
  esac
  hp_run_end_quiet
  [ -f "$RUN_TEL" ] && gzip -f "$RUN_TEL"
  for f in "$OUT/heater-$idx.out" "$OUT/heater-$idx-pre.out"; do [ -f "$f" ] && gzip -f "$f"; done
  if [ -n "$TRIGB" ] || [ "$TYPE" = SMOKE ]; then hp_sptrace "$OUT/sp-$idx.bin"; TRIGB_DUMP=sp-$idx.bin; fi
  hp_record_run "$idx" "$slot" "$att" "$role" "$name" "$mask" "$per" "$mins" "$tier" "$edge" "$target"
  log "run $idx ($role $name, $tier): launches $CH_N, first66 $( [ -n "$CH_F66" ] && echo "+$(( (CH_F66 - CH_T0) / 1000 )) s" || echo none), edge $([ -n "$EDGE_OK" ] && echo ok || echo missed), stop ${RUN_STOP:-none}"
  PRED_NAME=$name; PRED_E=$(awk -v m="$mins" -v a="${CH_T0:-0}" -v b="${CH_T1:-0}" 'BEGIN{printf "%.1f", 0.0256*m*(b-a)/1000}')
  rm -f "$RUN_STATE" "$RUN_CTL" "$RUN_SF"
}

n=0
for r in "${RUNS[@]}"; do
  read -r _ idx role name mask per mins tier edge target <<< "$r"
  n=$(( n + 1 ))
  run_one "$n" "$idx" 1 "$role" "$name" "$mask" "$per" "$mins" "$tier" "$edge" "$target"
  if [ "$TYPE" = B1 ] && [ -z "$CH_F66" ]; then     # one chain only (O1, review F7): no crossing is the result
    mark b1_no_crossing "\"why\":\"the one chain (<= ${P_chain_cap_s} s) did not reach 66: the one-shot is reported as no crossing\""
  fi
done

# ---- 5. re-runs (void runs and WORK outliers), once, at the end of the block (not for probe, smoke, one-shot, V0).
# blockcheck reads the round and params from the block's plan.json; if it cannot run, the block fails loudly (review
# high, 27 Sep: its crash went to mgmt.log only and the block ended "ok" with its void runs never re-run)
case "$TYPE" in S|L16|L8|G8)
  BC_OUT=$("${HPPY[@]}" blockcheck --out "$OUT" --card "$CARD" 2>> "$OUT/mgmt.log"); bc_rc=$?
  if [ $bc_rc -ne 0 ]; then
    mark blockcheck_failed "\"rc\":$bc_rc"
    hp_abort 1 "blockcheck failed (rc $bc_rc, see mgmt.log): the void runs cannot be found or re-run (DESIGN2 §4.4)"
  fi
  log "$(grep '^BLOCKCHECK ' <<< "$BC_OUT")"
  mapfile -t RR < <(grep '^RERUN ' <<< "$BC_OUT")
  for r in "${RR[@]}"; do
    read -r _ slot name <<< "$r"
    line=$(grep "^RUN $slot " <<< "$PLAN_OUT" | head -n 1)
    [ -n "$line" ] || continue
    read -r _ idx role name mask per mins tier edge target <<< "$line"
    n=$(( n + 1 ))
    mark rerun "\"slot\":$slot,\"name\":\"$name\""
    run_one "$n" "$slot" 2 "$role" "$name" "$mask" "$per" "$mins" "$tier" "$edge" "$target"
  done ;;
esac

# ---- 6. end
LEVEL_CHECK=
hp_level_restore                       # restores and checks only if this block set the level
hp_guard_stop
hp_gzip_all
dry || sleep 2
note=$(python3 "$HP_DIR/reduce.py" --check-pass "$OUT" --card "$CARD" 2> "$OUT/check.err"); rc=$?
[ -s "$OUT/check.err" ] || rm -f "$OUT/check.err"
[ -n "$LEVEL_CHECK" ] && note="$note; $LEVEL_CHECK"
trap - EXIT
if [ $rc -ne 0 ]; then block_end fail "check: ${note:-reduce.py failed}"; exit 1; fi
block_end ok "$note"
exit 0
