#!/usr/bin/env bash
# E131 (Q136, tools/claims-v3/e131/E131.md): one pass of E95's real-tiles matrix on aifoundry1 card 1, as a lib.sh block. A port of
# tools/claims-v3/kinds/block_e95.sh (E95, itself a port of block_e78.sh) with these changes, each marked E131:
#   1. it runs tools/claims-v3/e131/run_e131.py: tools/claims-v3/kinds/run_e78.py unchanged, with E95's items and order installed (e95_common.install,
#      unchanged) and E131's stops (board_w >= 68 W or a minion-shire reading >= 72 C writes STOP and ends the pass); every tile checked against its
#      registered sha256 first;
#   2. the die cap passed to run_e78.py is E131's registered 72 C (E78_MAX_C, default here 72; E95's was 78);
#   3. its data goes to $DATA_ROOT/e131/p131<nn>/ (smoke: e131-smoke/), so block_begin's code.sha256 covers tools/claims-v3/e131/*;
#   4. CARE WITH DEVICE COMMANDS (the owner's rule of Mon 2 Nov 2026), E128's change 5 and E129's change 6 unchanged: every telemetry call goes through
#      tools/claims-v3/e128/ettelem_guard.sh, the allow-list that passes only `ettelem config` and `ettelem sample --seconds --every-ms` (the classified
#      READs of E131.md) and refuses anything else before the device opens; and lib.sh's drain_mgmt is replaced by a refusal, so the vendor tool
#      dev_mngt_service is never run: a sampler that will not start fails the block instead;
#   5. binaries.sha256 records the binaries the block executes.
# Everything else - E95's items, order, smoke items, tile and plan checks, timeout 10 on the config reads, the card lock, hold10/timeout 10 on every
# device process, the other-user test (D1: an idle login does not block on aifoundry1; another user on this card or any other user's device process does),
# the launch protocol, the sampler, the STOP file - is block_e95.sh's, lib.sh's and hl/block.sh's, unchanged. Nothing is set: no governor, TDP, threshold
# or clock set, no reset, no --reset-ms.
#
#   bash tools/claims-v3/e131/block_e131.sh <pass> [--smoke]
#   V3_DRY=1 bash tools/claims-v3/e131/block_e131.sh <pass>          # print every device call, touch nothing
. "$(dirname "${BASH_SOURCE[0]}")/../lib.sh"
ETTELEM=tools/claims-v3/e128/ettelem_guard.sh                                                                     # E131 change 4
drain_mgmt() { log "E131: drain refused: dev_mngt_service is not in E131's classified command list"; return 0; }   # E131 change 4
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
others_present && exit 3
[ -n "${V3_DEVICE:-}" ] && export V3_DEVICE

PASS=${1:?usage: block_e131.sh <pass> [--smoke]}
SMOKE=; [ "${2:-}" = --smoke ] && SMOKE=1
case "$PASS" in ''|*[!0-9]*) echo "pass must be a number" >&2; exit 2 ;; esac
HERE=tools/claims-v3/e131
KIN=tools/claims-v3/kinds
TARGET=${E78_TARGET:-58}; PREHEAT=${E78_PREHEAT:-59}; BURNIN=${E78_BURNIN:-2}; MAXC=${E78_MAX_C:-72}     # E131 change 2
QUIET=${E78_QUIET:-2.0}; TIERS=${E78_TIERS:-1,2}; FMA_S=4; EXPN=${E131_EXPN:-e131}                     # E131 change 3
ITEMS_ARG=()
if [ -n "$SMOKE" ]; then
  PREHEAT=0; TARGET=200; FMA_S=2; BURNIN=0; EXPN=${E131_EXPN:-e131}-smoke
  ITEMS_ARG=(--items "$(python3 -c 'import sys; sys.path.insert(0, sys.argv[1]); import e95_common as e; print(",".join(e.SMOKE_ITEMS))' "$KIN")")
fi

# ---- preflight: files only, no device ------------------------------------------------------------------------
pf=()
[ -f "$KIN/kinds.json" ] || pf+=("no $KIN/kinds.json")
[ -f "$KIN/real2/real2.json" ] || pf+=("no $KIN/real2/real2.json")
[ -f "$KIN/real/real.json" ] || pf+=("no $KIN/real/real.json")
[ -f "$KIN/real2/predictions-real2.json" ] || pf+=("no $KIN/real2/predictions-real2.json")
[ -f "$KIN/predictions-e95.json" ] || pf+=("no $KIN/predictions-e95.json")
[ -f "$HERE/predictions-e131.json" ] || pf+=("no $HERE/predictions-e131.json")
[ -x "$SPARSITY" ] || pf+=("missing $SPARSITY")
[ -x "$HEATER" ] || pf+=("missing heater $HEATER")
[ -x "$ETTELEM" ] || pf+=("missing $ETTELEM")
[ -x build/ettelem/ettelem ] || pf+=("missing build/ettelem/ettelem")
if [ -x "$SPARSITY" ]; then
  for s in 'file:' fp16 int8 '--dump-tiles'; do
    grep -a -q -- "$s" "$SPARSITY" || pf+=("$SPARSITY has no $s")
  done
fi
for b in "$SPARSITY" "$HEATER"; do [ -x "$b" ] && { grep -a -q -- '--stop-file' "$b" || pf+=("$b has no --stop-file"); }; done
LK=/run/lock/etsoc-shire${V3_DEVICE:-0}.lock
[ -n "${V3_DRY:-}" ] || [ -e "$LK" ] || pf+=("no card lock $LK")
mkdir -p "$V3_ROOT/build"
LIST=$(python3 "$HERE/run_e131.py" /dev/null --root "$V3_ROOT" --first-block "$PASS" --tiers "$TIERS" --card "$CARD" \
       --fma-s "$FMA_S" --burnin "$BURNIN" ${ITEMS_ARG[@]+"${ITEMS_ARG[@]}"} --list 2>"$V3_ROOT/build/e131-list.err") ||
  pf+=("run_e131 --list (harness and tiles against their sha256): $(tail -c 300 "$V3_ROOT/build/e131-list.err") ${LIST:0:300}")
MAXS=$(python3 -c 'import json,sys; print(json.loads(sys.argv[1])["max_s"])' "$LIST" 2>/dev/null)
case "$MAXS" in ''|*[!0-9]*) pf+=("bad run_e131 --list output: ${LIST:0:200}") ;; esac
if [ ${#pf[@]} -gt 0 ]; then printf 'preflight: %s\n' "${pf[@]}" >&2; exit 2; fi

D=$DATA_ROOT/$EXPN/p$PASS
if [ -e "$D/block.json" ] && ! grep -q '"status":"ok"' "$D/block.json"; then mv "$D" "$D.attempt-$(date +%s)"; fi
if [ -d "$D" ] && [ ! -e "$D/block.json" ]; then mv "$D" "$D.attempt-$(date +%s)"; fi
block_begin "$EXPN" "$PASS"
others_present && { block_end others "another user before the first launch"; exit 3; }
[ -n "${V3_DRY:-}" ] || et-lab-manifest > "$OUT/manifest.txt" 2>/dev/null || true
( cd "$KIN" && sha256sum kinds.json tiles/*/*.bin real2/real2.json real2/predictions-real2.json real2/tiles/*/*.bin real/real.json real/tiles/*/*.bin ) > "$OUT/gen.sha256" 2>/dev/null || true
sha256sum "$SPARSITY" "$HEATER" build/ettelem/ettelem "$ETTELEM" > "$OUT/binaries.sha256" 2>/dev/null || true          # E131 change 5
card_config() {
  if [ -n "${V3_DRY:-}" ]; then echo "DRY ettelem config" >&2; echo '{"dry":true}'; return 0; fi
  timeout 10 "$ETTELEM" config 2>/dev/null < /dev/null | grep '^{' | tail -1 || true
}
card_config > "$OUT/config_start.json"
start_sampler "$OUT/telemetry.jsonl" $((MAXS + 900)) || { block_end failed "sampler did not start"; exit 4; }
sleep 3
RUNNER=
on_signal() { [ -n "$RUNNER" ] && kill -TERM "$RUNNER" 2>/dev/null; wait "$RUNNER" 2>/dev/null; stop_sampler; block_end failed "signal"; exit 1; }
trap on_signal TERM INT HUP
python3 "$HERE/run_e131.py" "$OUT" --root "$V3_ROOT" --tel-live "$OUT/telemetry.jsonl.raw" \
  --heater "$HEATER" --sparsity "$SPARSITY" --first-block "$PASS" --seed "$PASS" --tiers "$TIERS" \
  --target "$TARGET" --preheat "$PREHEAT" --quiet-s "$QUIET" --max-c "$MAXC" --fma-s "$FMA_S" --burnin "$BURNIN" \
  --card "$CARD" --shires "${E78_SHIRES:-0xffffffff}" --per-shire "${E78_PER_SHIRE:-32}" ${ITEMS_ARG[@]+"${ITEMS_ARG[@]}"} &
RUNNER=$!
wait "$RUNNER"; rc=$?
RUNNER=
sleep 5
stop_sampler
card_config > "$OUT/config_end.json"
[ -s "$OUT/telemetry.jsonl" ] && gzip -f "$OUT/telemetry.jsonl"
case $rc in
  0) block_end ok "tiers $TIERS${SMOKE:+ smoke}" ;;
  3) block_end others "another user on the card"; exit 3 ;;
  *) block_end failed "run_e131 exit $rc"; exit 1 ;;
esac
