#!/usr/bin/env bash
# V3-GS (E48): gathers, scatters and packed atomics on the local card, one block per part of a pass.
#
#   bash tools/claims-v3/gs/block.sh <KS> [--smoke]
#   V3_DRY=1 bash tools/claims-v3/gs/block.sh <KS>            # print every device call, touch nothing
#   aifoundry1: V3_DEVICE=1 selects card 1 (lib.sh); card 0 is excluded (it overheats)
#
# <KS>     K = pass 1-9, S = 0 check (C: one verify launch per configuration, checked on the host), 1 energy (E: 101
#          configurations at 1,024 minions, --burst 3 --gap 4.5), 2 rate (R: 57 configurations at 1, 32 in one shire,
#          32 spread, --burst 1 --gap 1, re-heated to 74 C between configurations on governor-free cards). The
#          schedule is gs 10, gs 11, gs 12, (sleep), gs 21, gs 22, (sleep), gs 31, gs 32. E and R leave out the
#          configurations whose verify launch failed in this card's latest C block (its check.json); an E or R block
#          with no C block before it stops at preflight.
# --smoke  eight configurations (four timed, four verified: fgw.ps L1, fscw.ps own scratchpad, famoaddg.pi chip
#          table, fgw.ps DRAM), --burst 1, no heater: about a minute; data go to $DATA_ROOT/gs-smoke/p<any>.
# Every launch goes through tools/claims-v3/gs/run_gs_t10.py, which runs tools/claims-v3/cat/run_catalogue_t10.py
# unchanged on workloads/enercat/gs_catalogue.py's configurations (timeout 10, stdin /dev/null on every process).
# Governor-free cards (lib.sh GOV_FREE: all but aifoundry3) are heated to >= 76 C before E and R blocks, as catfull.
# Data: $DATA_ROOT/gs/p<KS>/ (runs, telemetry, marks gzipped; plan.json, pass.json, configs.json, check.json).
. "$(dirname "${BASH_SOURCE[0]}")/../lib.sh"      # cd's to the tree root; CARD, GOV_FREE, DATA_ROOT, ET_DEVICES
# The runner's own others_present check sources lib.sh again: on aifoundry1 it needs V3_DEVICE in its environment.
[ -n "${V3_DEVICE:-}" ] && export V3_DEVICE
# On a multi-card host lib's drain_mgmt would run dev_mngt_service -n 0, which is not ET_DEVICES-filtered (catfull).
if [ -n "${V3_DEVICE:-}" ]; then drain_mgmt() { log "drain_mgmt skipped (V3_DEVICE=$V3_DEVICE: dev_mngt_service is not ET_DEVICES-filtered)"; }; fi
if [ "$CARD" = aifoundry1-c0 ]; then echo "aifoundry1-c0 is excluded from V3-GS (115-117 C under load)" >&2; exit 2; fi
others_present && exit 3
if ours_running; then log "one of our own device processes on this card is still running"; exit 3; fi

ARG=${1:?usage: block.sh <KS> [--smoke]}
SMOKE=; [ "${2:-}" = --smoke ] && SMOKE=1
case "$ARG" in ''|*[!0-9]*) echo "block must be a number (KS: pass K 1-9, S 0 check / 1 energy / 2 rate)" >&2; exit 2 ;; esac
HERE=tools/claims-v3/gs
LIBPY=$HERE/gslib.py
SHIM=$HERE/run_gs_t10.py
RUNNER=tools/claims-v3/cat/run_catalogue_t10.py     # V3-CAT's patched runner, reused unchanged through the shim
HOST_BIN=build/enercat_gs/host/enercat_host         # workloads/enercat built with -DENERCAT_GS=ON (README)
HEAT_C=76; HEAT_MAX=150                             # governor-free cards: lib.sh heat_to's target and bound
RETRY_MAX=12                                        # configurations without a launch re-run once at the end

if [ -n "$SMOKE" ]; then
  K=0; S=S; KIND=smoke; EXPN=gs-smoke; TIMING=(--burst 1 --gap 4.5 --lead 3); PLANARGS=(--smoke); SET=smoke
else
  [[ "$ARG" =~ ^[1-9][0-2]$ ]] || { echo "block $ARG: need KS with pass K 1-9 and S 0 (check), 1 (energy), 2 (rate)" >&2; exit 2; }
  K=${ARG:0:1}; S=${ARG:1:1}; EXPN=gs; PLANARGS=(--block "$ARG" --data-root "$DATA_ROOT" ${V3_DRY:+--dry})
  case "$S" in
    0) KIND=C; SET=C; TIMING=(--burst 0 --gap 0.3 --lead 0) ;;
    1) KIND=E; SET=E; TIMING=(--burst 3 --gap 4.5) ;;
    2) KIND=R; SET=R; TIMING=(--burst 1 --gap 1) ;;
  esac
fi
NEED_TEL=1; [ "$KIND" = C ] && NEED_TEL=      # the check block reads no power
NEED_HEAT=; [ -n "$GOV_FREE" ] && { [ "$KIND" = E ] || [ "$KIND" = R ]; } && NEED_HEAT=1
# R on a governor-free card: its 57 configurations run at 1 or 32 minions, near idle for ~4 min, and a die that cools
# from the preheat's 76 C toward the ~65 C where the governor lifts the clock would lose launches to the clock rule.
# The t10 runner's own hold (V3-CAT's --hold-hot path) heats before a configuration while the live telemetry's die is
# under 74 C. R reads no idle brackets, so no wait after a burst is needed (--hold-after 0).
[ "$KIND" = R ] && [ -n "$NEED_HEAT" ] && TIMING+=(--hold-hot 74 --hold-max 3 --hold-after 0 --heat-settle 0.3 --heater "$HEATER")

# ---- preflight: files only, no device --------------------------------------------------------------------------
pf=()
python3 -c 'import numpy' 2>/dev/null || pf+=("python3 has no numpy")
PLAN=$(python3 "$LIBPY" plan --root "$V3_ROOT" "${PLANARGS[@]}" 2>&1) || pf+=("plan: $PLAN")
for f in "$SHIM" "$RUNNER" workloads/enercat/gs_catalogue.py workloads/enercat/analyze_catalogue.py tools/claims-v3/catfull/cflib.py; do
  [ -f "$f" ] || pf+=("missing $f")
done
[ -x "$HOST_BIN" ] || pf+=("missing $HOST_BIN (cmake -B build/enercat_gs -S workloads/enercat -DENERCAT_GS=ON ...)")
[ -n "$NEED_TEL" ] && [ ! -x "$ETTELEM" ] && pf+=("missing $ETTELEM")
KELF=
if [ -x "$HOST_BIN" ]; then
  grep -a -q -- '--gs-index' "$HOST_BIN" || pf+=("$HOST_BIN has no --gs-index (not an ENERCAT_GS build)")
  KELF=$(grep -a -o '/[[:alnum:]/._-]*/enercat\.elf' "$HOST_BIN" | head -1)
  if [ -z "$KELF" ] || [ ! -f "$KELF" ]; then pf+=("kernel ${KELF:-?} (compiled into $HOST_BIN) not found")
  elif ! grep -a -q 'gs_run' "$KELF"; then pf+=("kernel $KELF has no gs_run (not an ENERCAT_GS build)"); fi
fi
if [ -n "$NEED_HEAT" ]; then
  if [ ! -x "$HEATER" ]; then pf+=("missing heater $HEATER")
  else grep -a -q -- '--per-shire' "$HEATER" && grep -a -q 'randn' "$HEATER" || pf+=("$HEATER lacks --per-shire/randn"); fi
fi
if [ ${#pf[@]} -eq 0 ]; then
  jget() { python3 -c 'import json,sys; v=json.loads(sys.argv[1])[sys.argv[2]]; print(",".join(v) if isinstance(v, list) else v)' "$1" "$2"; }
  ONLY=$(jget "$PLAN" names); NPLAN=$(jget "$PLAN" n); SEED=$(jget "$PLAN" seed_run)
  LIST=$(python3 "$SHIM" --set "$SET" /dev/null --root "$V3_ROOT" --only "$ONLY" --passes 1 "${TIMING[@]}" --seed "$SEED" \
         --host-bin "$HOST_BIN" --card "$CARD" --list 2>&1) || pf+=("runner --list: $LIST")
fi
if [ ${#pf[@]} -eq 0 ]; then
  NRUN=$(python3 -c 'import json,sys; print(json.loads(sys.argv[1])["n"])' "$LIST")
  MAXS=$(python3 -c 'import json,sys; print(json.loads(sys.argv[1])["max_s"])' "$LIST")
  [ "$NRUN" = "$NPLAN" ] || pf+=("the runner selects $NRUN configurations, the plan $NPLAN")
fi
if [ ${#pf[@]} -gt 0 ]; then printf 'preflight: %s\n' "${pf[@]}" >&2; exit 2; fi

# ---- helpers (catfull's) -----------------------------------------------------------------------------------------
HEAT_ARGS=(--test fma --type fp32 --pattern none --values randn --shires 0xffffffff --per-shire 32 --seconds 2 --seed 1)
eval "lib_die_c() $(declare -f die_c | tail -n +2)"
finish() {  # finish <status> <note>
  if [ "$1" = others ]; then die_c() { echo null; }; else die_c() { local t; t=$(lib_die_c); echo "${t:-null}"; }; fi
  block_end "$1" "$2"
}
gz_out() { local f; for f in telemetry.jsonl runs.jsonl marks.jsonl; do [ -s "$OUT/$f" ] && gzip -f "$OUT/$f"; done; return 0; }
yield_exit() { stop_sampler; gz_out; finish others "$1"; exit 3; }
HEAT_END=
gs_heat_to() {   # catfull's cf_heat_to: lib.sh heat_to's loop with others_present before every reading
  local target=$1 out=$2 t= i empty=0
  if [ -n "${V3_DRY:-}" ]; then echo "DRY gs_heat_to $target (<= $HEAT_MAX x hold10 $HEATER ${HEAT_ARGS[*]})" >&2; HEAT_END=80; return 0; fi
  for i in $(seq 1 "$HEAT_MAX"); do
    others_present && yield_exit "others present during the preheat"
    t=$(die_c); echo "{\"t_ms\":$(now_ms),\"die_c\":${t:-null},\"target\":$target}" >> "$out"
    if [ -z "$t" ]; then
      empty=$((empty + 1))
      [ $empty -eq 2 ] && drain_mgmt
      [ $empty -ge 4 ] && { log "gs_heat_to: no die temperature"; HEAT_END=; return 1; }
      sleep 2; continue
    fi
    empty=0; HEAT_END=$t
    [ "$t" -ge "$target" ] && return 0
    hold10 "$HEATER" "${HEAT_ARGS[@]}" > /dev/null 2>&1
  done
  log "gs_heat_to $target: stopped at ${t:-?} C after $HEAT_MAX launches"; return 1
}

# ---- the block ---------------------------------------------------------------------------------------------------
d=$DATA_ROOT/$EXPN/p$ARG
if [ -d "$d" ] && { [ -n "$SMOKE" ] || [ ! -e "$d/block.json" ] || [ -n "${V3_FORCE:-}" ]; }; then
  mv "$d" "$d.attempt-$(date +%s)"     # never append to an earlier attempt's runs.jsonl
fi
[ -n "$SMOKE" ] && export V3_FORCE=1
block_begin "$EXPN" "$ARG"
{ sha256sum tools/claims-v3/lib.sh $(find "$HERE" -maxdepth 1 -type f | sort) "$RUNNER" \
    workloads/enercat/gs_catalogue.py workloads/enercat/analyze_catalogue.py workloads/enercat/analyze_gs.py \
    tools/claims-v3/catfull/cflib.py "$HOST_BIN" ${KELF:+"$KELF"} 2>/dev/null; } > "$OUT/code.sha256"
echo "$PLAN" > "$OUT/plan.json"
IDLE_MHZ0=
if [ -n "$NEED_TEL" ]; then
  IDLE_MHZ0=$(clock_mhz || true)
  [ -z "$IDLE_MHZ0" ] && { sleep 2; IDLE_MHZ0=$(clock_mhz || true); }
  case "$IDLE_MHZ0" in ''|*[!0-9]*) IDLE_MHZ0= ;; esac
fi
HEAT_NOTE=; HEAT_OK=None
if [ -n "$NEED_HEAT" ] && [ -z "$SMOKE" ]; then
  if gs_heat_to "$HEAT_C" "$OUT/preheat.jsonl"; then HEAT_OK=True
  else HEAT_OK=False; HEAT_NOTE="preheat stopped at ${HEAT_END:-?} C (target $HEAT_C)"; fi
fi
python3 - "$OUT/pass.json" "$PLAN" <<EOF
import json, sys
p = json.loads(sys.argv[2])
json.dump({"exp": "gs", "card": "$CARD", "block": "$ARG", "kind": "$KIND", "pass": $K, "part": "$S", "smoke": bool("$SMOKE"),
           "gov_free": bool("$GOV_FREE"), "v3_device": "${V3_DEVICE:-}" or None, "et_devices": "${ET_DEVICES:-}" or None,
           "seed_run": $SEED, "n_cfg": $NPLAN, "n_set": p.get("n_set"), "excluded": p.get("excluded", []),
           "check_block": p.get("check_block"), "timing": "${TIMING[*]}", "host_bin": "$HOST_BIN", "kernel": "$KELF",
           "runner": "$SHIM -> $RUNNER", "heater": "$HEATER" if "$NEED_HEAT" else None,
           "heat_target_c": $HEAT_C if "$NEED_HEAT" and not "$SMOKE" else None, "heat_reached": $HEAT_OK,
           "die_c_after_heat": ${HEAT_END:-None}, "idle_mhz_start": ${IDLE_MHZ0:-None}, "max_s": $MAXS},
          open(sys.argv[1], "w"), indent=1)
EOF
log "$EXPN p$ARG: kind $KIND pass $K seed $SEED; $NPLAN configurations, <= $((MAXS / 60 + 1)) min; idle ${IDLE_MHZ0:-?} MHz${HEAT_NOTE:+; $HEAT_NOTE}"
others_present && yield_exit "others present after the preheat"

rargs=(--root "$V3_ROOT" --passes 1 "${TIMING[@]}" --seed "$SEED" --host-bin "$HOST_BIN" --card "$CARD")
if [ -n "$NEED_TEL" ]; then
  # the sampler's own time limit is a backstop only (stop_sampler ends it): the runner's bound, the retry, 5 min
  start_sampler "$OUT/telemetry.jsonl" $((MAXS + RETRY_MAX * 12 + 300)) || { finish fail "sampler would not start"; exit 1; }
  rargs+=(--tel-live "$OUT/telemetry.jsonl.raw")
fi
if [ -n "${V3_DRY:-}" ]; then
  python3 "$SHIM" --set "$SET" "$OUT" --only "$ONLY" "${rargs[@]}" --dry; rc=$?
else
  python3 "$SHIM" --set "$SET" "$OUT" --only "$ONLY" "${rargs[@]}" > "$OUT/runner.out" 2>&1; rc=$?
fi
# a configuration whose process printed no launch: once more at the end of the block (at most 12; retry/ keeps the
# record, its launches are appended to runs.jsonl)
if [ -z "${V3_DRY:-}" ] && [ "$rc" = 0 ]; then
  MISS=$(python3 "$LIBPY" missing "$OUT")
  nmiss=$(echo "$MISS" | tr ',' '\n' | grep -c . || true)
  if [ "$nmiss" -gt 0 ] && [ "$nmiss" -le "$RETRY_MAX" ]; then
    log "retrying $nmiss configurations without a launch: $MISS"
    mkdir -p "$OUT/retry"
    python3 "$SHIM" --set "$SET" "$OUT/retry" --only "$MISS" "${rargs[@]}" --lead 0 > "$OUT/retry/runner.out" 2>&1; rc=$?
    [ -s "$OUT/retry/runs.jsonl" ] && cat "$OUT/retry/runs.jsonl" >> "$OUT/runs.jsonl"
  fi
fi
[ -n "$NEED_TEL" ] && stop_sampler
[ "$rc" = 3 ] && yield_exit "another user or device process appeared during the block (runner stopped)"

if [ -n "${V3_DRY:-}" ]; then
  st=ok; note="dry run (runner rc $rc)"
else
  res=$(python3 "$LIBPY" check "$OUT" --kind "$KIND" --card "$CARD" --gov-free "$([ -n "$GOV_FREE" ] && echo 1 || echo 0)" \
        --root "$V3_ROOT" 2> "$OUT/check.err") || res="fail post-block check crashed: $(tail -1 "$OUT/check.err")"
  res=$(printf '%s\n' "$res" | tail -1); [ -s "$OUT/check.err" ] || rm -f "$OUT/check.err"
  case "${res%% *}" in ok|checkfail|offclock|partial|fail) ;; *) res="fail post-block check printed no status: $res" ;; esac
  st=${res%% *}; note=${res#* }
  [ "$rc" = 4 ] && { st=fail; note="the sampler stopped writing: runner stopped the block; $note"; }
  [ "$rc" != 0 ] && [ "$st" != fail ] && { st=fail; note="runner rc $rc; $note"; }
fi
gz_out
finish "$st" "${note//\"/\'}${HEAT_NOTE:+; $HEAT_NOTE}"
[ "$st" = ok ] && exit 0
[ -n "$SMOKE" ] && [ "$st" = offclock ] && exit 0
exit 1
