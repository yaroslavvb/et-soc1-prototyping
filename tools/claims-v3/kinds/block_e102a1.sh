#!/usr/bin/env bash
# E102 amendment A1 (E102.md, "Amendments"): one added block on the local card, as a lib.sh block. A port of block_e102.sh, which is not changed, with these changes, each marked A1:
#   1. it takes passes 10214 (short G, E78's protocol) and 10240-10243 (R, a dense train: --preheat 0 --target 200 --quiet-s 0.2 --burnin 0) and no others;
#   2. it hands run_e102.py the block's exact item list, from e102a1_common.py (`--items`, an option run_e78.py already has);
#   3. --smoke runs e102a1_common.SMOKE, four 2 s runs, as pass 10202.
# Everything else is block_e102.sh's: the config reads under timeout 10 at both ends, the card lock, hold10/timeout 10 on every device process, the other-user test, the sampler, the STOP file. No knob is written; no --reset-ms.
#
#   bash tools/claims-v3/kinds/block_e102a1.sh <pass> [--smoke]
#   V3_DRY=1 bash tools/claims-v3/kinds/block_e102a1.sh <pass>        # print every device call, touch nothing
. "$(dirname "${BASH_SOURCE[0]}")/../lib.sh"
# Departure D1 (hl/README.md, kept by E60-E79): on aifoundry3 a user who is only logged in does not block (other
# lab users keep idle tmux logins there); another user on THIS card does, and so does any other user's device
# process. Fails closed when et-holders is unreadable.
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

PASS=${1:?usage: block_e78.sh <pass> [--smoke]}
SMOKE=; [ "${2:-}" = --smoke ] && SMOKE=1
case "$PASS" in ''|*[!0-9]*) echo "pass must be a number" >&2; exit 2 ;; esac
HERE=tools/claims-v3/kinds
TARGET=${E78_TARGET:-58}; PREHEAT=${E78_PREHEAT:-59}; BURNIN=${E78_BURNIN:-2}; MAXC=${E78_MAX_C:-78}
QUIET=${E78_QUIET:-2.0}; TIERS=${E78_TIERS:-1,2}; FMA_S=4; EXPN=${E78_EXPN:-kinds}   # E78 change 4
ITEMS_ARG=()
case "$PASS" in        # A1 change 1
  10214) BLOCK=GS ;;
  1024[0-9]) BLOCK=R; PREHEAT=0; TARGET=200; QUIET=0.2; BURNIN=0 ;;
  10202) BLOCK=S ;;
  *) echo "pass $PASS is no A1 block" >&2; exit 2 ;;
esac
log "E102 A1 block $BLOCK, pass $PASS: target $TARGET preheat $PREHEAT quiet $QUIET burnin $BURNIN"
if [ -n "$SMOKE" ]; then
  PREHEAT=0; TARGET=200; QUIET=0.2; FMA_S=2; BURNIN=0; EXPN=${E78_EXPN:-kinds}-smoke
  ITEMS_ARG=(--items "$(python3 -c 'import sys; sys.path.insert(0, sys.argv[1]); import e102a1_common as e; print(",".join(e.SMOKE))' "$HERE")")   # A1 change 3
else
  ITEMS_ARG=(--items "$(python3 "$HERE/e102a1_common.py" --order "$PASS" --card "$CARD")")   # A1 change 2
fi

# ---- preflight: files only, no device ------------------------------------------------------------------------
pf=()
[ -f "$HERE/kinds.json" ] || pf+=("no $HERE/kinds.json")
[ -f "$HERE/e102/e102.json" ] || pf+=("no $HERE/e102/e102.json")      # E102 change 4
[ -f "$HERE/predictions-e102.json" ] || pf+=("no $HERE/predictions-e102.json")
[ -x "$SPARSITY" ] || pf+=("missing $SPARSITY")
[ -x "$HEATER" ] || pf+=("missing heater $HEATER")
[ -x "$ETTELEM" ] || pf+=("missing $ETTELEM")
if [ -x "$SPARSITY" ]; then
  for s in 'file:' fp16 int8 '--dump-tiles'; do
    grep -a -q -- "$s" "$SPARSITY" || pf+=("$SPARSITY has no $s")
  done
fi
for b in "$SPARSITY" "$HEATER"; do [ -x "$b" ] && { grep -a -q -- '--stop-file' "$b" || pf+=("$b has no --stop-file"); }; done
LK=/run/lock/etsoc-shire${V3_DEVICE:-0}.lock
[ -n "${V3_DRY:-}" ] || [ -e "$LK" ] || pf+=("no card lock $LK")
mkdir -p "$V3_ROOT/build"
# E102 change 1: run_e102.py (run_e78.py unchanged, E102's items and orders) in the preflight and the pass
LIST=$(python3 "$HERE/run_e102.py" /dev/null --root "$V3_ROOT" --first-block "$PASS" --tiers "$TIERS" --card "$CARD" \
       --fma-s "$FMA_S" --burnin "$BURNIN" ${ITEMS_ARG[@]+"${ITEMS_ARG[@]}"} --list 2>"$V3_ROOT/build/e102a1-list.err") ||
  pf+=("run_e102 --list (tiles against their sha256): $(tail -c 300 "$V3_ROOT/build/e102a1-list.err") ${LIST:0:300}")
MAXS=$(python3 -c 'import json,sys; print(json.loads(sys.argv[1])["max_s"])' "$LIST" 2>/dev/null)
case "$MAXS" in ''|*[!0-9]*) pf+=("bad run_e102 --list output: ${LIST:0:200}") ;; esac
if [ ${#pf[@]} -gt 0 ]; then printf 'preflight: %s\n' "${pf[@]}" >&2; exit 2; fi

D=$DATA_ROOT/$EXPN/p$PASS
if [ -e "$D/block.json" ] && ! grep -q '"status":"ok"' "$D/block.json"; then mv "$D" "$D.attempt-$(date +%s)"; fi
if [ -d "$D" ] && [ ! -e "$D/block.json" ]; then mv "$D" "$D.attempt-$(date +%s)"; fi
block_begin "$EXPN" "$PASS"
others_present && { block_end others "another user before the first launch"; exit 3; }
[ -n "${V3_DRY:-}" ] || et-lab-manifest > "$OUT/manifest.txt" 2>/dev/null || true      # E78 change 3
( cd "$HERE" && sha256sum kinds.json tiles/*/*.bin e102/e102.json e102/tiles/*/*.bin ) > "$OUT/gen.sha256" 2>/dev/null || true   # E102 change 4
# E78 change 2: the card's static configuration, read only (TDP, threshold, clock, voltage), inside the lock,
# under timeout 10. `ettelem config` has no setter.
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
python3 "$HERE/run_e102.py" "$OUT" --root "$V3_ROOT" --tel-live "$OUT/telemetry.jsonl.raw" \
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
  *) block_end failed "run_e102 exit $rc"; exit 1 ;;
esac
