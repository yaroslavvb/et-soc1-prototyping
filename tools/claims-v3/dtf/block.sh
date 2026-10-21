#!/usr/bin/env bash
# V3-DTF (README.md): one pass (one block) of the chosen items on the local card, as a lib.sh block.
# tools/claims-v3/hl/block.sh (E60) with the DF build, a smoke branch per new shape, a camera branch, and our own device
# processes (sys_emu, a stale host) refused before block_begin.
#
#   bash tools/claims-v3/dtf/block.sh <pass> <items> [--smoke | --cam]
#   V3_DEVICE=0 bash tools/claims-v3/dtf/block.sh ...        # aifoundry1: card 0 only (card 1 is another user's)
#   DTF_DUP=<names> ...                                      # items run twice in the pass (README "Per card")
#   HL_TARGET=58 HL_PREHEAT=59 HL_BURNIN=2 DTF_GEN=<make_dtf.py dir> ...   # defaults; DTF_GEN defaults to build/dtf-gen
#
# --smoke: one item per new shape (and an E60 tie) at the current reading, no preheat, 2 s runs: EXPN dtf-smoke.
# --cam: the dtf-cam block (README "E-D7"): <items> is the exact run order, contiguous, no heater, 8 s runs, with the
#        camera poller beside it (frames to build/dtf-cam/p<pass>/, never committed): EXPN dtf-cam.
# Data: $DATA_ROOT/<EXPN>/p<pass>/ (runs.jsonl, marks.jsonl, run.log, telemetry.jsonl.gz, configs.json, manifest.txt,
# gen.sha256 = the operand files that ran, elf.sha256 = the DF kernel and host). A pass whose block.json is not "ok"
# is moved aside to p<pass>.attempt-<epoch> before it is run again.
. "$(dirname "${BASH_SOURCE[0]}")/../lib.sh"
# Departure D1 (E60 README): on aifoundry3 and aifoundry1 a user who is only logged in does not block; another user on
# THIS card does (card-scoped et-holders, failing closed). aifoundry2 keeps lib.sh's own test.
case "$CARD" in aifoundry3|aifoundry1-c*)
  if [ -z "${V3_DRY:-}" ]; then
  others_present() {
    local procs= holders= out n=${V3_DEVICE:-0}
    if [ -z "${V3_DEVICE:-}" ]; then
      procs=$(ps -eo uid=,pid=,comm= | awk -v me="$(id -u)" -v re="$OTHER_COMM" '$1 != me && $3 ~ re {print $1":"$2":"$3}' | tr '\n' ' ')
    fi
    out=$(sudo -n /usr/local/sbin/et-holders 9>&- 8>&- 2>&1) || { log "others present: et-holders unreadable: ${out:0:120}"; return 0; }
    holders=$(printf '%s\n' "$out" | grep -v 'et-holders' |
              awk -v me="$USER" -v d="/dev/et${n}_" -v l="lock:etsoc-shire${n}.lock" \
                  'index($1, d) == 1 || $1 == l { if ($2 != me && $2 != "") print $2":"$3 }' | tr '\n' ' ')
    if [ -n "${procs// /}${holders// /}" ]; then log "others present: procs=[$procs] holders=[$holders]"; return 0; fi
    return 1
  }
  fi ;;
esac
# On aifoundry1 the stock dev_mngt_service opens every card: never drain while anyone is on another card.
case "$CARD" in aifoundry1-c*)
  eval "lib_drain_mgmt() $(declare -f drain_mgmt | tail -n +2)"
  drain_mgmt() {
    local out; out=$(sudo -n /usr/local/sbin/et-holders 9>&- 8>&- 2>/dev/null | grep -v 'et-holders' | grep -v "^/dev/et${V3_DEVICE}_" | grep -v "lock:etsoc-shire${V3_DEVICE}.lock" | grep -E '^/dev/et|^lock:' || true)
    if [ -n "$out" ]; then log "drain deferred: another card is held"; return 0; fi
    lib_drain_mgmt
  } ;;
esac
others_present && exit 3
if [ -z "${V3_DRY:-}" ] && ours_running; then log "our own device process (sys_emu or a stale host) runs here"; exit 3; fi
[ -n "${V3_DEVICE:-}" ] && export V3_DEVICE

PASS=${1:?usage: block.sh <pass> <items> [--smoke|--cam]}
ITEMS=${2:?usage: block.sh <pass> <items> [--smoke|--cam]}
MODE=${3:-}
case "$PASS" in ''|*[!0-9]*) echo "pass must be a number" >&2; exit 2 ;; esac
HERE=tools/claims-v3/dtf
GEN=${DTF_GEN:-$V3_ROOT/build/dtf-gen}
ENERCAT_DF=build/enercat-df/host/enercat_host
TARGET=${HL_TARGET:-58}; PREHEAT=${HL_PREHEAT:-59}; BURNIN=${HL_BURNIN:-2}; MAXC=${HL_MAX_C:-78}
EC_S=4; EXPN=dtf; EXTRA=()
[ -n "${DTF_DUP:-}" ] && EXTRA+=(--dup "$DTF_DUP")
case "$MODE" in
  --smoke) PREHEAT=0; TARGET=200; EC_S=2; BURNIN=0; EXPN=dtf-smoke
           ITEMS=d2A_h32,d1b_h32,d3_L8,d2X_h32,d5_a5,d6_one,xin_h32; EXTRA=() ;;
  --cam)   PREHEAT=0; TARGET=200; EC_S=8; BURNIN=0; EXPN=dtf-cam
           EXTRA=(--contiguous --order "$ITEMS"); ITEMS=$(printf '%s\n' "${ITEMS//,/$'\n'}" | awk '!s[$0]++' | paste -sd,) ;;
  '') ;;
  *) echo "unknown mode $MODE" >&2; exit 2 ;;
esac

# ---- preflight: files only, no device ------------------------------------------------------------------------
pf=()
[ -f "$GEN/manifest.json" ] || pf+=("no $GEN/manifest.json (python3 $HERE/make_dtf.py $GEN --check)")
[ -x "$SPARSITY" ] || pf+=("missing $SPARSITY")
[ -x "$HEATER" ] || pf+=("missing heater $HEATER")
[ -x "$ETTELEM" ] || pf+=("missing $ETTELEM")
[ -x "$ENERCAT_DF" ] || pf+=("missing $ENERCAT_DF (cmake -S workloads/enercat -B build/enercat-df -DENERCAT_DF=ON)")
if [ -x "$ENERCAT_DF" ]; then
  grep -a -q -- '--operands file:' "$ENERCAT_DF" || pf+=("$ENERCAT_DF has no --operands file:")
  ndf=$("$ENERCAT_DF" --list 2>/dev/null | grep -c '^df\.')
  [ "$ndf" = 10 ] || pf+=("$ENERCAT_DF lists $ndf df. modes, want 10")
  # proof step 3 as a gate: the built kernel holds exactly the generated blocks (check_elf.py)
  /opt/et/bin/riscv64-unknown-elf-objdump -d build/enercat-df/kernel/enercat.elf > "$V3_ROOT/build/dtf-dis.txt" 2>/dev/null &&
    python3 "$HERE/check_elf.py" "$V3_ROOT/build/dtf-dis.txt" workloads/enercat/enercat_df_modes.json > "$V3_ROOT/build/dtf-elfcheck.txt" 2>&1 ||
    pf+=("check_elf.py: $(tail -1 "$V3_ROOT/build/dtf-elfcheck.txt" 2>/dev/null)")
fi
for b in "$SPARSITY" "$HEATER"; do [ -x "$b" ] && { grep -a -q -- '--stop-file' "$b" || pf+=("$b has no --stop-file"); }; done
if [ -n "${V3_DEVICE:-}" ]; then   # a stock device layer ignores ET_DEVICES and would open every card
  for b in "$ETTELEM" "$SPARSITY" "$HEATER" "$ENERCAT_DF"; do
    [ -x "$b" ] && { grep -qa ET_DEVICES "$b" || pf+=("$b has no ET_DEVICES"); }
  done
  grep -qa ET_DEVICES /opt/et/lib/libdeviceLayer.a || pf+=("/opt/et's device layer has no ET_DEVICES")
fi
LK=/run/lock/etsoc-shire${V3_DEVICE:-0}.lock
[ -n "${V3_DRY:-}" ] || [ -e "$LK" ] || pf+=("no card lock $LK")
LIST=$(python3 "$HERE/run_dtf.py" /dev/null --root "$V3_ROOT" --gen "$GEN" --items "$ITEMS" --burnin "$BURNIN" "${EXTRA[@]}" --list 2>"$V3_ROOT/build/dtf-list.err") ||
  pf+=("run_dtf --list: $(tail -c 300 "$V3_ROOT/build/dtf-list.err")")
MAXS=$(python3 -c 'import json,sys; print(json.loads(sys.argv[1])["max_s"])' "$LIST" 2>/dev/null)
case "$MAXS" in ''|*[!0-9]*) pf+=("bad run_dtf --list output: ${LIST:0:200}") ;; esac
if [ ${#pf[@]} -gt 0 ]; then printf 'preflight: %s\n' "${pf[@]}" >&2; exit 2; fi

D=$DATA_ROOT/$EXPN/p$PASS
if [ -e "$D/block.json" ] && ! grep -q '"status":"ok"' "$D/block.json"; then mv "$D" "$D.attempt-$(date +%s)"; fi
if [ -d "$D" ] && [ ! -e "$D/block.json" ]; then mv "$D" "$D.attempt-$(date +%s)"; fi
block_begin "$EXPN" "$PASS"
others_present && { block_end others "another user before the first launch"; exit 3; }
et-lab-manifest > "$OUT/manifest.txt" 2>/dev/null || true
( cd "$GEN" && sha256sum manifest.json cards.json srcs/* ) > "$OUT/gen.sha256" 2>/dev/null || true
sha256sum "$ENERCAT_DF" build/enercat-df/kernel/enercat.elf > "$OUT/elf.sha256" 2>/dev/null || true
start_sampler "$OUT/telemetry.jsonl" $((MAXS + 900)) || { block_end failed "sampler did not start"; exit 4; }
sleep 3
RUNNER=; CAM=
if [ "$MODE" = --cam ]; then
  mkdir -p "$V3_ROOT/build/dtf-cam/p$PASS"
  nice -n 19 python3 "$HERE/camera_poll.py" --out "$V3_ROOT/build/dtf-cam/p$PASS" --max-s $((MAXS + 120)) \
    --stop-file "$OUT/CAMSTOP" --no-nice > "$OUT/camera.log" 2>&1 < /dev/null &
  CAM=$!
fi
on_signal() { [ -n "$RUNNER" ] && kill -TERM "$RUNNER" 2>/dev/null; wait "$RUNNER" 2>/dev/null; [ -n "$CAM" ] && touch "$OUT/CAMSTOP";
              stop_sampler; block_end failed "signal"; exit 1; }
trap on_signal TERM INT HUP
python3 "$HERE/run_dtf.py" "$OUT" --root "$V3_ROOT" --gen "$GEN" --items "$ITEMS" "${EXTRA[@]}" --tel-live "$OUT/telemetry.jsonl.raw" \
  --heater "$HEATER" --sparsity "$SPARSITY" --enercat "$ENERCAT_DF" --blocks 1 --first-block "$PASS" --seed "$PASS" \
  --target "$TARGET" --preheat "$PREHEAT" --max-c "$MAXC" --ec-s "$EC_S" --burnin "$BURNIN" --card "$CARD" &
RUNNER=$!
wait "$RUNNER"; rc=$?
RUNNER=
[ -n "$CAM" ] && { touch "$OUT/CAMSTOP"; wait "$CAM" 2>/dev/null; cp "$V3_ROOT/build/dtf-cam/p$PASS/frames.jsonl" "$OUT/" 2>/dev/null; }
sleep 5
stop_sampler
[ -s "$OUT/telemetry.jsonl" ] && gzip -f "$OUT/telemetry.jsonl"
case $rc in
  0) block_end ok "$ITEMS" ;;
  3) block_end others "another user on the card"; exit 3 ;;
  *) block_end failed "run_dtf exit $rc"; exit 1 ;;
esac
