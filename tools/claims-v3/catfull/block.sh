#!/usr/bin/env bash
# V3-CATFULL (amendment of 25 Sep 2026, the four-card campaign): the energy manual's FULL catalogue
# (workloads/enercat/run_catalogue.py, 392 configurations) on the local card, one third of a pass per block.
#
#   bash tools/claims-v3/catfull/block.sh <KS> [--smoke]
#   V3_DRY=1 bash tools/claims-v3/catfull/block.sh <KS>          # print every device call, touch nothing
#   aifoundry1: V3_DEVICE=0|1 selects the card (lib.sh)
#
# <KS>     pass K (1-3 planned, 4-9 extra passes), part S (1-3): 11 12 13 21 22 23 31 32 33. A pass is the whole
#          catalogue once, in the order random.Random(40<K>).shuffle gives, cut into three parts of 130-131
#          configurations (~18 min of runner time each); the runner shuffles its part again with --seed 40<K><S>.
# --smoke  three configurations (compute, scratchpad prefill, dramrow2), --burst 1, no heater: under a minute;
#          data go to $DATA_ROOT/catfull-smoke/p<KS> (any number), always re-run.
# Every launch goes through tools/claims-v3/cat/run_catalogue_t10.py (timeout 10, stdin /dev/null), E27's timing
# (--burst 3 --gap 4.5), one pass. Governor-free cards (lib.sh GOV_FREE: all but aifoundry3) are heated to >= 76 C
# before the sampler starts, as the 23 Sep catalogue started on a warm die; no heater runs inside a part.
# Data: $DATA_ROOT/catfull/p<KS>/ (runs, telemetry gzipped; pass.json, configs.json, check.json, preheat.jsonl).
. "$(dirname "${BASH_SOURCE[0]}")/../lib.sh"      # cd's to the tree root; CARD, GOV_FREE, DATA_ROOT, ET_DEVICES
# On a multi-card host (V3_DEVICE set) lib's drain_mgmt must not run: it calls /opt/et/bin/dev_mngt_service -n 0, a
# build that ignores ET_DEVICES and opens every card, so it would reach card 0 (with V3_DEVICE=1 it drains the wrong
# card) while the other card's queue may be sampling. lib's start_sampler (second failed start) and stop_sampler (after
# a SIGKILL) call it; here they skip it and say so. A card whose management queue stays blocked then fails the block.
if [ -n "${V3_DEVICE:-}" ]; then drain_mgmt() { log "drain_mgmt skipped (V3_DEVICE=$V3_DEVICE: dev_mngt_service is not ET_DEVICES-filtered)"; }; fi
others_present && exit 3
if ours_running; then log "one of our own device processes on this card is still running"; exit 3; fi

ARG=${1:?usage: block.sh <KS> [--smoke]}
SMOKE=; [ "${2:-}" = --smoke ] && SMOKE=1
case "$ARG" in ''|*[!0-9]*) echo "block must be a number (KS: pass K 1-9, part S 1-3)" >&2; exit 2 ;; esac
HERE=tools/claims-v3/catfull
LIBPY=$HERE/cflib.py
RUNNER=tools/claims-v3/cat/run_catalogue_t10.py    # V3-CAT's patched runner, reused unchanged
HOST_BIN=$ENERCAT2                                  # build/enercat_v2/host/enercat_host (dramrow2 needs --jump-every)
HEAT_C=76; HEAT_MAX=150                             # governor-free cards: lib.sh heat_to's target and bound
BURST=3; GAP=4.5; PARTS=3                           # E27: run_catalogue.py DATA --passes 3 --burst 3 --gap 4.5
RETRY_MAX=12                                        # configurations without a launch re-run once at the end

if [ -n "$SMOKE" ]; then
  K=0; S=0; EXPN=catfull-smoke; TIMING=(--burst 1 --gap "$GAP" --lead 3); PLANARGS=(--smoke)
else
  [[ "$ARG" =~ ^[1-9][1-3]$ ]] || { echo "block $ARG: need KS with pass K 1-9 and part S 1-3 (11 12 13 21 ...)" >&2; exit 2; }
  K=${ARG:0:1}; S=${ARG:1:1}; EXPN=catfull; TIMING=(--burst "$BURST" --gap "$GAP"); PLANARGS=(--pass "$K" --part "$S" --parts "$PARTS")
fi

# ---- preflight: files only, no device --------------------------------------------------------------------------
pf=()
python3 -c 'import numpy' 2>/dev/null || pf+=("python3 has no numpy")
PLAN=$(python3 "$LIBPY" plan --root "$V3_ROOT" "${PLANARGS[@]}" 2>&1) || pf+=("plan: $PLAN")
[ -f "$RUNNER" ] || pf+=("missing $RUNNER")
[ -f workloads/enercat/analyze_catalogue.py ] || pf+=("missing workloads/enercat/analyze_catalogue.py (post-block check)")
[ -x "$HOST_BIN" ] || pf+=("missing $HOST_BIN")
[ -x "$ETTELEM" ] || pf+=("missing $ETTELEM")
if [ -x "$HOST_BIN" ]; then
  grep -a -q -- '--jump-every' "$HOST_BIN" || pf+=("$HOST_BIN has no --jump-every (dramrow2)")
  kelf=$(grep -a -o '/[[:alnum:]/._-]*/enercat\.elf' "$HOST_BIN" | head -1)
  [ -n "$kelf" ] && [ ! -f "$kelf" ] && pf+=("kernel $kelf (compiled into $HOST_BIN) not found")
fi
if [ -n "$GOV_FREE" ] && [ -z "$SMOKE" ]; then
  if [ ! -x "$HEATER" ]; then pf+=("missing heater $HEATER")
  else grep -a -q -- '--per-shire' "$HEATER" && grep -a -q 'randn' "$HEATER" || pf+=("$HEATER lacks --per-shire/randn"); fi
fi
if [ ${#pf[@]} -eq 0 ]; then
  jget() { python3 -c 'import json,sys; v=json.loads(sys.argv[1])[sys.argv[2]]; print(",".join(v) if isinstance(v, list) else v)' "$1" "$2"; }
  ONLY=$(jget "$PLAN" names); NPLAN=$(jget "$PLAN" n); SEED=$(jget "$PLAN" seed_run)
  RCARD=(); grep -q -- '"--card"' "$RUNNER" && RCARD=(--card "$CARD")   # runs' "host" = the card id, if supported
  LIST=$(python3 "$RUNNER" /dev/null --root "$V3_ROOT" --only "$ONLY" --passes 1 "${TIMING[@]}" --seed "$SEED" \
         --host-bin "$HOST_BIN" --list 2>&1) || pf+=("runner --list: $LIST")
fi
if [ ${#pf[@]} -eq 0 ]; then
  NRUN=$(python3 -c 'import json,sys; print(json.loads(sys.argv[1])["n"])' "$LIST")
  MAXS=$(python3 -c 'import json,sys; print(json.loads(sys.argv[1])["max_s"])' "$LIST")
  [ "$NRUN" = "$NPLAN" ] || pf+=("the runner selects $NRUN configurations, the plan $NPLAN")
fi
if [ ${#pf[@]} -gt 0 ]; then printf 'preflight: %s\n' "${pf[@]}" >&2; exit 2; fi

# ---- helpers -----------------------------------------------------------------------------------------------------
HEAT_ARGS=(--test fma --type fp32 --pattern none --values randn --shires 0xffffffff --per-shire 32 --seconds 2 --seed 1)
# block_end prints die_c's output unquoted; finish() gives it null for an empty reading, and none after an intrusion
eval "lib_die_c() $(declare -f die_c | tail -n +2)"
finish() {  # finish <status> <note>
  if [ "$1" = others ]; then die_c() { echo null; }; else die_c() { local t; t=$(lib_die_c); echo "${t:-null}"; }; fi
  block_end "$1" "$2"
}
gz_out() { local f; for f in telemetry.jsonl runs.jsonl marks.jsonl; do [ -s "$OUT/$f" ] && gzip -f "$OUT/$f"; done; return 0; }
yield_exit() { stop_sampler; gz_out; finish others "$1"; exit 3; }
# cf_heat_to <C> <log>: lib.sh heat_to's loop (die_c, then a 2 s random fp32 matmul launch, <= 150 launches), with
# others_present before every reading; after two empty readings one drain, but only when this host has one card in
# play (lib's drain_mgmt runs dev_mngt_service -n 0, which is not ET_DEVICES-filtered and would reach card 0).
HEAT_END=
cf_heat_to() {
  local target=$1 out=$2 t= i empty=0
  if [ -n "${V3_DRY:-}" ]; then echo "DRY cf_heat_to $target (<= $HEAT_MAX x hold10 $HEATER ${HEAT_ARGS[*]})" >&2; HEAT_END=80; return 0; fi
  for i in $(seq 1 "$HEAT_MAX"); do
    others_present && yield_exit "others present during the preheat"
    t=$(die_c); echo "{\"t_ms\":$(now_ms),\"die_c\":${t:-null},\"target\":$target}" >> "$out"
    if [ -z "$t" ]; then
      empty=$((empty + 1))
      [ $empty -eq 2 ] && drain_mgmt                  # a no-op with V3_DEVICE set (above)
      [ $empty -ge 4 ] && { log "cf_heat_to: no die temperature"; HEAT_END=; return 1; }
      sleep 2; continue
    fi
    empty=0; HEAT_END=$t
    [ "$t" -ge "$target" ] && return 0
    hold10 "$HEATER" "${HEAT_ARGS[@]}" > /dev/null 2>&1
  done
  log "cf_heat_to $target: stopped at ${t:-?} C after $HEAT_MAX launches"; return 1
}

# ---- the block ---------------------------------------------------------------------------------------------------
d=$DATA_ROOT/$EXPN/p$ARG
if [ -d "$d" ] && { [ -n "$SMOKE" ] || [ ! -e "$d/block.json" ] || [ -n "${V3_FORCE:-}" ]; }; then
  mv "$d" "$d.attempt-$(date +%s)"     # never append to an earlier attempt's runs.jsonl
fi
[ -n "$SMOKE" ] && export V3_FORCE=1
block_begin "$EXPN" "$ARG"
{ sha256sum tools/claims-v3/lib.sh $(find "$HERE" -maxdepth 1 -type f | sort) "$RUNNER" \
    workloads/enercat/run_catalogue.py workloads/enercat/analyze_catalogue.py "$HOST_BIN" 2>/dev/null; } > "$OUT/code.sha256"
echo "$PLAN" > "$OUT/plan.json"
# the card's clock before anything runs on it (aifoundry1 card 0 idles at 300 MHz in its low_power state); a sampler
# started right after block_begin's die reading fails about one time in three (lib.sh), so one retry after 2 s
IDLE_MHZ0=$(clock_mhz || true)
[ -z "$IDLE_MHZ0" ] && { sleep 2; IDLE_MHZ0=$(clock_mhz || true); }
case "$IDLE_MHZ0" in ''|*[!0-9]*) IDLE_MHZ0= ;; esac
HEAT_NOTE=; HEAT_OK=None
if [ -z "$SMOKE" ] && [ -n "$GOV_FREE" ]; then
  if cf_heat_to "$HEAT_C" "$OUT/preheat.jsonl"; then HEAT_OK=True
  else HEAT_OK=False; HEAT_NOTE="preheat stopped at ${HEAT_END:-?} C (target $HEAT_C)"; fi
fi
python3 - "$OUT/pass.json" "$PLAN" <<EOF
import json, sys
json.dump({"exp": "catfull", "card": "$CARD", "block": "$ARG", "pass": $K, "part": $S, "parts": $PARTS,
           "smoke": bool("$SMOKE"), "gov_free": bool("$GOV_FREE"), "v3_device": "${V3_DEVICE:-}" or None,
           "et_devices": "${ET_DEVICES:-}" or None, "seed_pass": json.loads(sys.argv[2])["seed_pass"],
           "seed_run": $SEED, "n_cfg": $NPLAN, "n_total": json.loads(sys.argv[2])["n_total"],
           "timing": "${TIMING[*]}", "host_bin": "$HOST_BIN", "runner": "$RUNNER",
           "heater": "$HEATER" if "$GOV_FREE" else None, "heat_target_c": $HEAT_C if "$GOV_FREE" and not "$SMOKE" else None,
           "heat_reached": $HEAT_OK, "die_c_after_heat": ${HEAT_END:-None},
           "idle_mhz_start": ${IDLE_MHZ0:-None}, "max_s": $MAXS}, open(sys.argv[1], "w"), indent=1)
EOF
log "$EXPN p$ARG: pass $K part $S seed $SEED; $NPLAN configurations, <= $((MAXS / 60 + 1)) min; idle ${IDLE_MHZ0:-?} MHz${HEAT_NOTE:+; $HEAT_NOTE}"
others_present && yield_exit "others present after the preheat"

# the sampler's own time limit is a backstop only (stop_sampler ends it): the runner's bound, the retry, 5 min
start_sampler "$OUT/telemetry.jsonl" $((MAXS + RETRY_MAX * 12 + 300)) || { finish fail "sampler would not start"; exit 1; }
rargs=(--root "$V3_ROOT" --passes 1 "${TIMING[@]}" --seed "$SEED" --host-bin "$HOST_BIN" --tel-live "$OUT/telemetry.jsonl.raw" "${RCARD[@]}")
if [ -n "${V3_DRY:-}" ]; then
  python3 "$RUNNER" "$OUT" --only "$ONLY" "${rargs[@]}" --dry; rc=$?
else
  python3 "$RUNNER" "$OUT" --only "$ONLY" "${rargs[@]}" > "$OUT/runner.out" 2>&1; rc=$?
fi
# a configuration whose burst process printed no launch (e.g. aifoundry3's intermittent host crash): once more at the
# end of the part, while the sampler still runs; its launches are appended to runs.jsonl (retry/ keeps the record)
if [ -z "${V3_DRY:-}" ] && [ "$rc" = 0 ]; then
  MISS=$(python3 "$LIBPY" missing "$OUT")
  nmiss=$(echo "$MISS" | tr ',' '\n' | grep -c . || true)
  if [ "$nmiss" -gt 0 ] && [ "$nmiss" -le "$RETRY_MAX" ]; then
    log "retrying $nmiss configurations without a launch: $MISS"
    mkdir -p "$OUT/retry"
    python3 "$RUNNER" "$OUT/retry" --only "$MISS" "${rargs[@]}" --lead 0 > "$OUT/retry/runner.out" 2>&1; rc=$?
    [ -s "$OUT/retry/runs.jsonl" ] && cat "$OUT/retry/runs.jsonl" >> "$OUT/runs.jsonl"
  fi
fi
stop_sampler
[ "$rc" = 3 ] && yield_exit "another user or device process appeared during the part (runner stopped)"

if [ -n "${V3_DRY:-}" ]; then
  st=ok; note="dry run (runner rc $rc)"
else
  # stderr (numpy warnings, a traceback) goes to check.err so it cannot become the status word
  res=$(python3 "$LIBPY" check "$OUT" --card "$CARD" --gov-free "$([ -n "$GOV_FREE" ] && echo 1 || echo 0)" \
        --root "$V3_ROOT" 2> "$OUT/check.err") || res="fail post-block check crashed: $(tail -1 "$OUT/check.err")"
  res=$(printf '%s\n' "$res" | tail -1); [ -s "$OUT/check.err" ] || rm -f "$OUT/check.err"
  case "${res%% *}" in ok|offclock|partial|fail) ;; *) res="fail post-block check printed no status: $res" ;; esac
  st=${res%% *}; note=${res#* }
  [ "$rc" = 4 ] && { st=fail; note="the sampler stopped writing: runner stopped the part; $note"; }
  [ "$rc" != 0 ] && [ "$st" != fail ] && { st=fail; note="runner rc $rc; $note"; }
fi
gz_out
finish "$st" "${note//\"/\'}${HEAT_NOTE:+; $HEAT_NOTE}"
[ "$st" = ok ] && exit 0
[ -n "$SMOKE" ] && [ "$st" = offclock ] && exit 0    # the smoke checks the pipeline, not the clock
exit 1
