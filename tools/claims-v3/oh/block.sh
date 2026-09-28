#!/usr/bin/env bash
# OH (the effect of overheating, E53): one block on the local card, from the tree's root.
#
#   bash tools/claims-v3/oh/block.sh <pass>              (aifoundry1: V3_DEVICE=1; card 0 is never used)
#   V3_DRY=1 bash tools/claims-v3/oh/block.sh <pass>     no device access: an accelerated simulation (README.md)
#   bash tools/claims-v3/oh/block.sh --binhash           the binaries a block would run, with sha256 (no device)
#
# pass = T*100 + k: T 1 = an OH-1 block (the hottest sensor under the most concentrated load: IDLE, ONE-C, ONE-NE and
# B4C in a Williams order), 2 = the OH-2 block (known-answer kernels from rest to a mean of 82-84 C, the refresh period
# at the hot end, the cooling tail), 9 = the smoke. Data: build/claims-v3/<card>/oh/p<pass>/.
# Refused (exit 2) before anything touches a card: aifoundry1 card 0, aifoundry2, any other host, a pass kind the card
# does not run (ohlib.py plan), V3_FORCE or an OH_* override without V3_DRY. Every block but the smoke needs the PREREG
# lock (ohlib.py preregcheck; OH_PREREG_SHA256 = PREREG.md's sha256 as prereg.py printed it).
# Exit codes (V3): 0 ok, 1 fail (a safety stop, stale sampler, heater failures), 3 someone else on the card.
set -u
. "$(dirname "${BASH_SOURCE[0]}")/../lib.sh"            # cd's to the tree root; CARD, HEATER, ETTELEM, ONCHIP, ...
case "$CARD" in
  aifoundry1-c0) echo "oh: aifoundry1 card 0 is never used: refused" >&2; exit 2 ;;
  aifoundry2) echo "oh: aifoundry2 is not an OH card: refused" >&2; exit 2 ;;
esac
OH_DIR=tools/claims-v3/oh
. "$OH_DIR/ohlib.sh"
if [ "${1:-}" = --binhash ]; then oh_binaries_json; exit 0; fi

PASS=${1:?usage: block.sh <pass>}
case "$PASS" in ''|*[!0-9]*) echo "pass must be a number" >&2; exit 2 ;; esac
PASS=$(( 10#$PASS ))
why=$("${OHPY[@]}" check-card --pass "$PASS" --card "$CARD") || { log "oh: pass $PASS on $CARD $why"; exit 2; }
oh_envcheck
BATTERY_FILE=$OH_DIR/battery.txt
if [ -n "${OH_BATTERY:-}" ]; then BATTERY_FILE=$OH_BATTERY; fi

# ---- 1. the card must be free
others_present && exit 3
ours_running && { log "oh: a device process of this user is running on this card: not starting"; exit 3; }
oh_orphan_guards
oh_card0_check "block start"
oh_lock_present
if ! dry; then
  for b in "$HEATER" "$ETTELEM" "$ONCHIP" "$MEMPROBE" "$MMB_LAUNCHER"; do [ -x "$b" ] || { log "oh: missing $b"; exit 1; }; done
  for b in "$HEATER_KERNEL" "$MMB_KERNEL"; do [ -f "$b" ] || { log "oh: missing $b"; exit 1; }; done
fi
N0=$(modcount)
if [ -n "$N0" ] && [ "$N0" != 0 ]; then log "oh: et_soc1 use count $N0: someone holds the card"; exit 3; fi
PLAN_OUT=$("${OHPY[@]}" plan --pass "$PASS" --card "$CARD") || { log "oh: no plan for pass $PASS"; exit 2; }
while IFS= read -r line; do case "$line" in SET\ *) eval "${line#SET }" ;; esac; done <<< "$PLAN_OUT"
KIND=$INFO_kind
BINS_JSON=$(oh_binaries_json)
PL_REC=
if [ "$KIND" != SMOKE ]; then     # the PREREG lock: refuse before touching the card
  PL_BINS=$(mktemp); echo "$BINS_JSON" > "$PL_BINS"; PL_REC=$(mktemp)
  why=$("${OHPY[@]}" preregcheck --card "$CARD" --bins "$PL_BINS" --record "$PL_REC") || {
    rm -f "$PL_BINS" "$PL_REC"; oh_refused_record preregcheck "$why"; log "oh: PREREG lock: $why"; exit 1; }
  log "oh: $why"; rm -f "$PL_BINS"
fi
mapfile -t BATTERY < <(grep -v '^\s*\(#\|$\)' "$BATTERY_FILE")
[ "${#BATTERY[@]}" -ge 1 ] || { log "oh: empty battery $BATTERY_FILE"; exit 1; }

# ---- 2. begin
block_begin oh "$PASS"
trap 'oh_cleanup' EXIT
mkdir -p "$OUT/k" "$OUT/run" "$OUT/mp"
sha256sum "$OH_DIR"/*.py "$OH_DIR"/*.sh "$OH_DIR"/*.json "$BATTERY_FILE" "$OH_DIR"/prereg/* tools/claims-v3/queue.sh \
  workloads/memprobe/gen_ops.py >> "$OUT/code.sha256" 2>/dev/null
echo "$BINS_JSON" > "$OUT/binaries.json"
[ -n "$PL_REC" ] && mv "$PL_REC" "$OUT/prereg-lock.json"
echo "$PLAN_OUT" > "$OUT/plan.txt"
: > "$OUT/launches.jsonl"; : > "$OUT/marks.jsonl"
command -v et-lab-manifest > /dev/null && ! dry && timeout 30 et-lab-manifest > "$OUT/manifest.txt" 2>&1
mark block_begin "\"kind\":\"$KIND\",\"pass\":$PASS,\"dry\":$(dry && echo true || echo false),\"overrides\":\"$OH_OVERRIDES\",\"die_c\":$(jnum "$BLOCK_C0")"
if [ -n "$GUARD_ON" ]; then
  oh_guard_start || { NO_CARD=; oh_guard_stop; block_end fail "card-0 guard gate: card 0 not <= ${P_guard_gate_c} C or no reading"; exit 3; }
fi
# the standing SP statistics, read-only, before this block's first statistics reset
start_sampler "$OUT/stats-before.jsonl" 3 && { oh_sleep 1.5; stop_sampler; }

# ---- the battery: one checked kernel with the void rule and the hot follow-up
FOLLOW=
bat_line() { local i=$1; echo "${BATTERY[$(( i % ${#BATTERY[@]} ))]}"; }
oh_checked() {   # oh_checked <battery line> <role>
  local line=$1 role=$2 name tool args
  IFS='|' read -r name tool args <<< "$line"
  # shellcheck disable=SC2086
  set -- $args
  oh_admit 10; oh_live; oh_between
  KROLE=$role KATTEMPT=1 oh_kernel "$name" "$tool" "$@"
  if [ "$KSTAT" = NORESULT ] && [ "$LAST_RC" -ne 0 ]; then       # a host crash (aifoundry3's g3log race): void, once more
    mark void "\"name\":\"$name\",\"rc\":$LAST_RC,\"seq\":$SEQ"
    oh_admit 10; oh_live; oh_between
    KROLE=$role-void-rerun KATTEMPT=2 oh_kernel "$name" "$tool" "$@"
  fi
  if [ "$KSTAT" = BAD ] && [ "$KIND" = OH2 ] && [ "$role" != followup-hot ] && [ "$role" != followup-cool ]; then
    mark kernel_bad "\"name\":\"$name\",\"why\":\"$KWHY\",\"band\":\"${BAND:-}\",\"mean\":$(jnum "$ST_MEAN")"
    case " $FOLLOW " in *" $name "*) ;; *) FOLLOW="$FOLLOW $name" ;; esac
    local r
    for r in $(seq 1 "$P2_followup_repeats"); do
      [ -n "${HOLD_LO:-}" ] && oh_hold "$HOLD_LO" "$HOLD_HI"
      oh_checked "$line" followup-hot
    done
  fi
}
oh_battery() {   # oh_battery <start index> <role>
  local s=$1 role=$2 i
  for i in $(seq 0 $(( ${#BATTERY[@]} - 1 ))); do
    [ -n "${HOLD_LO:-}" ] && oh_hold "$HOLD_LO" "$HOLD_HI"
    oh_checked "$(bat_line $(( s + i )))" "$role"
  done
}
# hold a band: heat if below lo (to the band's target, at most hold_heat_s), wait while above hi (at most
# cool_wait_s). Amendment 2: a band whose first heating (at most band_heat_s) did not reach its target (the die's
# plateau under the heater at the chain duty, or a soft cap) is held one degree below the highest mean that heating
# reached (PLATEAU); later bands keep that plateau. Every launch's band is its measured mean, as registered.
PLATEAU=
oh_hold() {
  local lo=$1 hi=$2 t0
  oh_live
  if [ "$ST_MEAN" -lt "$lo" ]; then oh_heat_to "$HOLD_TGT" "$P2_hold_heat_s"; fi
  t0=$(now_ms)
  while [ "$ST_MEAN" -gt "$hi" ] && [ $(( $(now_ms) - t0 )) -lt $(( P2_cool_wait_s * 1000 )) ]; do
    oh_live; [ $(( $(now_ms) - ${LAST_BETWEEN:-0} )) -ge 5000 ] && oh_between; oh_sleep 0.2
  done
}
oh_refresh() {   # the memprobe refresh programs (generated before, off the card)
  oh_admit 10; oh_live; oh_between
  KROLE=refresh oh_kernel refresh_jit MEMPROBE --program "$OUT/mp/refresh_jit.ops" --out-dir "$OUT/mp"
  [ -n "${HOLD_LO:-}" ] && oh_hold "$HOLD_LO" "$HOLD_HI"
  oh_admit 10; oh_live; oh_between
  KROLE=refresh oh_kernel refresh MEMPROBE --program "$OUT/mp/refresh.ops" --out-dir "$OUT/mp"
}
gen_refresh() {
  # shellcheck disable=SC2086
  python3 workloads/memprobe/gen_ops.py refresh --out "$OUT/mp" --name refresh_jit $P2_rjit >> "$OUT/mp/gen.log" 2>&1 &&
  python3 workloads/memprobe/gen_ops.py refresh --out "$OUT/mp" $P2_rlocked >> "$OUT/mp/gen.log" 2>&1 ||
    oh_abort 1 "memprobe op generation failed"
}

STATUS=ok; NOTE=
case "$KIND" in
SMOKE)
  # one heater launch, every battery kernel once, one single-shire launch, the refresh programs, 10 s idle
  gen_refresh
  BAND=smoke; oh_run_begin smoke
  oh_admit 4; oh_live; oh_between; rm -f "$RUN_SF"; oh_heat_launch heat "$P_heat_mask" "$(oh_heat_per)" "$P_heat_s"
  oh_battery 0 smoke
  oh_admit 4; oh_live; oh_between; rm -f "$RUN_SF"; oh_heat_launch cond-ONE-C 0x00004000 32 2
  oh_refresh
  oh_wait_s 10
  oh_run_end
  ;;
OH1)
  mapfile -t ORDER < <(python3 -c 'import json,sys; print("\n".join(json.loads(sys.argv[1])))' "$INFO_order")
  mark order "\"williams_row\":$INFO_williams_row,\"order\":$INFO_order"
  declare -A CMASK CPER
  while read -r _ n m p; do CMASK[$n]=$m; CPER[$n]=$p; done < <(grep '^COND ' <<< "$PLAN_OUT")
  i=0
  for cond in "${ORDER[@]}"; do
    i=$(( i + 1 )); BAND=$cond
    oh_run_begin "$i-$cond"
    for att in 1 2 3 4; do       # the preheat and the whole condition in one chain (<= 150 s)
      oh_heat_to "$P1_preheat_c" 140 "$P1_preheat_per_shire"
      { [ "$cond" = IDLE ] || oh_chain_room $(( P1_condition_s + 2 )); } && break
      oh_gap
    done
    TC=$(now_ms)
    mark cond_begin "\"run\":\"$RUN_ID\",\"cond\":\"$cond\",\"mask\":\"${CMASK[$cond]}\",\"per_shire\":${CPER[$cond]},\"mean\":$(jnum "$ST_MEAN"),\"high\":$(jnum "$ST_HIGH"),\"preheat\":\"$HEAT_WHY\""
    if [ "$cond" = IDLE ]; then
      oh_wait_s "$P1_condition_s"
    else
      while :; do
        el=$(( $(now_ms) - TC )); rem=$(( P1_condition_s * 1000 - el ))
        [ "$rem" -lt 700 ] && break
        secs=$(( rem / 1000 )); [ "$secs" -gt "$P1_launch_s" ] && secs=$P1_launch_s; [ "$secs" -lt 1 ] && secs=1
        oh_admit $(( secs + 2 )); oh_live; oh_between; rm -f "$RUN_SF"
        oh_heat_launch "cond-$cond" "${CMASK[$cond]}" "${CPER[$cond]}" "$secs"
      done
    fi
    mark cond_end "\"run\":\"$RUN_ID\",\"cond\":\"$cond\",\"t_begin_ms\":$TC,\"mean\":$(jnum "$ST_MEAN"),\"high\":$(jnum "$ST_HIGH")"
    oh_wait_s "$P1_tail_s"
    oh_run_end
  done
  ;;
OH2)
  gen_refresh
  bi=0
  while read -r _ name lo hi tgt nbat refresh rest restwait; do
    BAND=$name; HOLD_LO=; HOLD_HI=; HOLD_TGT=
    oh_run_begin "$name"
    if [ "$lo" = - ]; then       # the rest band: wait (sampler on) until the die rests
      t0=$(now_ms)
      while [ "$ST_MEAN" -gt "$rest" ] && [ $(( $(now_ms) - t0 )) -lt $(( restwait * 1000 )) ]; do oh_wait_s 1; done
      mark rest "\"mean\":$(jnum "$ST_MEAN"),\"high\":$(jnum "$ST_HIGH"),\"rest_max\":$rest,\"waited_s\":$(( ($(now_ms) - t0) / 1000 ))"
    else
      HOLD_LO=$lo; HOLD_HI=$hi; HOLD_TGT=$tgt
      if [ -n "$PLATEAU" ]; then        # amendment 2: the previous band already sat at the plateau
        HOLD_LO=$PLATEAU; HOLD_TGT=$PLATEAU
        mark plateau "\"band\":\"$name\",\"carried\":true,\"hold_at\":$PLATEAU,\"mean\":$(jnum "$ST_MEAN"),\"high\":$(jnum "$ST_HIGH")"
        oh_heat_to "$PLATEAU" "$P2_band_heat_s"
      else
        oh_heat_to "$tgt" "$P2_band_heat_s"
        if [ "$HEAT_WHY" != target ]; then
          PLATEAU=$(( HEAT_MAX - 1 )); HOLD_LO=$PLATEAU; HOLD_TGT=$PLATEAU
          mark plateau "\"band\":\"$name\",\"why\":\"$HEAT_WHY\",\"target\":$tgt,\"max_mean\":$HEAT_MAX,\"hold_at\":$PLATEAU,\"mean\":$(jnum "$ST_MEAN"),\"high\":$(jnum "$ST_HIGH")"
        fi
      fi
    fi
    for j in $(seq 1 "$nbat"); do oh_battery $(( j - 1 + bi )) battery; done
    [ "$refresh" = 1 ] && { [ -n "$HOLD_LO" ] && oh_hold "$HOLD_LO" "$HOLD_HI"; oh_refresh; }
    oh_run_end
    bi=$(( bi + 1 ))
  done < <(grep '^BAND ' <<< "$PLAN_OUT")
  # the cooling tail: sampler only, one battery (and every kernel that failed hot) when the mean first reads <= 65
  BAND=tail; HOLD_LO=; HOLD_HI=
  oh_run_begin tail
  t0=$(now_ms); done_=
  while [ $(( $(now_ms) - t0 )) -lt $(( P2_tail_s * 1000 )) ]; do
    oh_live
    if [ -z "$done_" ] && [ "$ST_MEAN" -le "$P2_tail_battery_at_c" ]; then
      mark tail_battery "\"mean\":$ST_MEAN,\"after_s\":$(( ($(now_ms) - t0) / 1000 ))"
      oh_battery 0 tail
      for n in $FOLLOW; do for b in "${BATTERY[@]}"; do [ "${b%%|*}" = "$n" ] && oh_checked "$b" followup-cool; done; done
      done_=1
    fi
    [ $(( $(now_ms) - ${LAST_BETWEEN:-0} )) -ge 5000 ] && oh_between
    oh_sleep 0.2
  done
  if [ -z "$done_" ]; then
    mark tail_battery "\"mean\":$ST_MEAN,\"late\":true"
    oh_battery 0 tail-late
    for n in $FOLLOW; do for b in "${BATTERY[@]}"; do [ "${b%%|*}" = "$n" ] && oh_checked "$b" followup-cool; done; done
  fi
  oh_run_end
  if [ -n "$FOLLOW" ]; then
    NOTE="kernel(s) failed hot:$FOLLOW (follow-up recorded; the session stops for the owner)"
    oh_session_stop "$NOTE"
  fi
  ;;
esac

# ---- end
oh_guard_stop
oh_gzip_all
python3 "$OH_DIR/reduce.py" --check-pass "$OUT" > "$OUT/check.json" 2> "$OUT/check.err" || NOTE="${NOTE:+$NOTE; }check-pass failed (check.err)"
block_end "$STATUS" "${NOTE:-$KIND done}"
exit 0
