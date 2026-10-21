#!/usr/bin/env bash
# V3-HL, the bit-flip ladder (README.md): one pass (one block) of the chosen items on the local card, as a lib.sh block.
#
#   bash tools/claims-v3/hl/block.sh <pass> <items> [--smoke]
#   V3_DEVICE=<0|1> bash tools/claims-v3/hl/block.sh ...     # aifoundry1: card 0 or 1 (lib.sh: ET_DEVICES)
#   V3_DRY=1 bash tools/claims-v3/hl/block.sh ...            # print every device call, touch nothing
#   HL_TARGET=58 HL_PREHEAT=59 HL_BURNIN=2 HL_GEN=<make_hl.py dir> ...   # defaults; HL_GEN defaults to build/hl-gen
#
# <items>: comma-separated item names or family prefixes from manifest.json (README "Per card" has tonight's lists).
# The shuffle seed is the pass number, so each pass is an independent replicate with its own order.
# --smoke: anchor_pi, lq_h8 and xin_h16 (if built) at the current reading (no preheat), 2 s runs.
# Data: $DATA_ROOT/hl/p<pass>/ (runs.jsonl, marks.jsonl, run.log, telemetry.jsonl.gz, tiles/ as dumped, configs.json,
# manifest.txt = et-lab-manifest, gen.sha256 = the operand files that ran). A pass whose block.json is not "ok" is moved
# aside to p<pass>.attempt-<epoch> before it is run again.
. "$(dirname "${BASH_SOURCE[0]}")/../lib.sh"
# Departure D1 (README): on aifoundry3 and aifoundry1 a user who is only logged in does not block (two idle tmux logins
# of other users on aifoundry3; on aifoundry1 another user, whose card is card 1); another user on THIS
# card does, and so does any other user's device process on a one-card host. Fails closed when et-holders is unreadable.
# aifoundry2 keeps lib.sh's own test.
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
[ -n "${V3_DEVICE:-}" ] && export V3_DEVICE

PASS=${1:?usage: block.sh <pass> <items> [--smoke]}
ITEMS=${2:?usage: block.sh <pass> <items> [--smoke]}
SMOKE=; [ "${3:-}" = --smoke ] && SMOKE=1
case "$PASS" in ''|*[!0-9]*) echo "pass must be a number" >&2; exit 2 ;; esac
HERE=tools/claims-v3/hl
GEN=${HL_GEN:-$V3_ROOT/build/hl-gen}
ENERCAT_HL=build/enercat-hl/host/enercat_host
TARGET=${HL_TARGET:-58}; PREHEAT=${HL_PREHEAT:-59}; BURNIN=${HL_BURNIN:-2}; MAXC=${HL_MAX_C:-78}
FMA_S=4; EC_S=4; EXPN=hl
if [ -n "$SMOKE" ]; then
  PREHEAT=0; TARGET=200; FMA_S=2; EC_S=2; BURNIN=0; EXPN=hl-smoke
  ITEMS=anchor_pi,lq_h8; [ -x "$ENERCAT_HL" ] && ITEMS=$ITEMS,xin_h16
fi

# ---- preflight: files only, no device ------------------------------------------------------------------------
pf=()
[ -f "$GEN/manifest.json" ] || pf+=("no $GEN/manifest.json (python3 $HERE/make_hl.py $GEN)")
[ -x "$SPARSITY" ] || pf+=("missing $SPARSITY")
[ -x "$HEATER" ] || pf+=("missing heater $HEATER")
[ -x "$ETTELEM" ] || pf+=("missing $ETTELEM")
if [ -x "$SPARSITY" ]; then grep -a -q 'file:' "$SPARSITY" || pf+=("$SPARSITY has no --values file:"); fi
for b in "$SPARSITY" "$HEATER"; do [ -x "$b" ] && { grep -a -q -- '--stop-file' "$b" || pf+=("$b has no --stop-file"); }; done
case ",$ITEMS," in *,x*|*,a[!n]*) [ -x "$ENERCAT_HL" ] || pf+=("missing $ENERCAT_HL (cmake -S workloads/enercat -B build/enercat-hl)") ;; esac
if [ -x "$ENERCAT_HL" ]; then grep -a -q -- '--operands file:' "$ENERCAT_HL" || pf+=("$ENERCAT_HL has no --operands file:"); fi
if [ -n "${V3_DEVICE:-}" ]; then   # a stock device layer ignores ET_DEVICES and would open every card
  for b in "$ETTELEM" "$SPARSITY" "$HEATER" "$ENERCAT_HL"; do
    [ -x "$b" ] && { grep -qa ET_DEVICES "$b" || pf+=("$b has no ET_DEVICES"); }
  done
  grep -qa ET_DEVICES /opt/et/lib/libdeviceLayer.a || pf+=("/opt/et's device layer has no ET_DEVICES")
fi
LK=/run/lock/etsoc-shire${V3_DEVICE:-0}.lock
[ -n "${V3_DRY:-}" ] || [ -e "$LK" ] || pf+=("no card lock $LK")
LIST=$(python3 "$HERE/run_hl.py" /dev/null --root "$V3_ROOT" --gen "$GEN" --items "$ITEMS" --burnin "$BURNIN" --list 2>"$V3_ROOT/build/hl-list.err") ||
  pf+=("run_hl --list: $(tail -c 300 "$V3_ROOT/build/hl-list.err")")
MAXS=$(python3 -c 'import json,sys; print(json.loads(sys.argv[1])["max_s"])' "$LIST" 2>/dev/null)
case "$MAXS" in ''|*[!0-9]*) pf+=("bad run_hl --list output: ${LIST:0:200}") ;; esac
if [ ${#pf[@]} -gt 0 ]; then printf 'preflight: %s\n' "${pf[@]}" >&2; exit 2; fi

D=$DATA_ROOT/$EXPN/p$PASS
if [ -e "$D/block.json" ] && ! grep -q '"status":"ok"' "$D/block.json"; then mv "$D" "$D.attempt-$(date +%s)"; fi
if [ -d "$D" ] && [ ! -e "$D/block.json" ]; then mv "$D" "$D.attempt-$(date +%s)"; fi
block_begin "$EXPN" "$PASS"
others_present && { block_end others "another user before the first launch"; exit 3; }
et-lab-manifest > "$OUT/manifest.txt" 2>/dev/null || true
( cd "$GEN" && sha256sum manifest.json tiles/* srcs/* ) > "$OUT/gen.sha256" 2>/dev/null || true
start_sampler "$OUT/telemetry.jsonl" $((MAXS + 900)) || { block_end failed "sampler did not start"; exit 4; }
sleep 3
RUNNER=
on_signal() { [ -n "$RUNNER" ] && kill -TERM "$RUNNER" 2>/dev/null; wait "$RUNNER" 2>/dev/null; stop_sampler; block_end failed "signal"; exit 1; }
trap on_signal TERM INT HUP
python3 "$HERE/run_hl.py" "$OUT" --root "$V3_ROOT" --gen "$GEN" --items "$ITEMS" --tel-live "$OUT/telemetry.jsonl.raw" \
  --heater "$HEATER" --sparsity "$SPARSITY" --enercat "$ENERCAT_HL" --blocks 1 --first-block "$PASS" --seed "$PASS" \
  --target "$TARGET" --preheat "$PREHEAT" --max-c "$MAXC" --fma-s "$FMA_S" --ec-s "$EC_S" --burnin "$BURNIN" --card "$CARD" &
RUNNER=$!
wait "$RUNNER"; rc=$?
RUNNER=
sleep 5
stop_sampler
[ -s "$OUT/telemetry.jsonl" ] && gzip -f "$OUT/telemetry.jsonl"
case $rc in
  0) block_end ok "$ITEMS" ;;
  3) block_end others "another user on the card"; exit 3 ;;
  *) block_end failed "run_hl exit $rc"; exit 1 ;;
esac
