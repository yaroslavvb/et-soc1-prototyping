#!/usr/bin/env bash
# E88 (Q130, tools/claims-v3/rpath/E88.md): one pass of the result-path experiment on the local card, as a lib.sh
# block. block_e78.sh (E78/E82) with these changes, each marked E88 below:
#   1. it runs tools/claims-v3/rpath/run_e88.py (run_e78.py unchanged, with e88_common's 22 tiles and order);
#   2. its preflight reads e88.json, not kinds.json, and gen.sha256 covers rpath's tiles;
#   3. its data goes to $DATA_ROOT/rpath/p<pass>/ (so block_begin's code.sha256 covers tools/claims-v3/rpath/*);
#   4. the smoke runs anchor_pi, fp32.zeros, fp32.r_abs, fp32.r_walk, fp16.r_cancel, int8.r_cancel.
# Everything else - the card lock, timeout 10 on every device process, the other-user test (with E78's aifoundry1
# reading of it), the launch protocol, the sampler (no --reset-ms), the STOP file - is E78's, unchanged.
#
#   bash tools/claims-v3/rpath/block_e88.sh <pass> [--smoke]
#   V3_DRY=1 bash tools/claims-v3/rpath/block_e88.sh <pass>          # print every device call, touch nothing
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
HERE=tools/claims-v3/rpath                                    # E88 change 1
TARGET=${E78_TARGET:-58}; PREHEAT=${E78_PREHEAT:-59}; BURNIN=${E78_BURNIN:-2}; MAXC=${E78_MAX_C:-78}
QUIET=${E78_QUIET:-2.0}; TIERS=1; FMA_S=4; EXPN=rpath           # E88 change 3
ITEMS_ARG=()
if [ -n "$SMOKE" ]; then
  PREHEAT=0; TARGET=200; FMA_S=2; BURNIN=0; EXPN=rpath-smoke                     # E88 change 4
  ITEMS_ARG=(--items anchor_pi,fp32.zeros,fp32.r_abs,fp32.r_walk,fp16.r_cancel,int8.r_cancel)
fi

# ---- preflight: files only, no device ------------------------------------------------------------------------
pf=()
[ -f "$HERE/e88.json" ] || pf+=("no $HERE/e88.json")   # E88 change 2
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
LIST=$(python3 "$HERE/run_e88.py" /dev/null --root "$V3_ROOT" --first-block "$PASS" --tiers "$TIERS" --card "$CARD" \
       --fma-s "$FMA_S" --burnin "$BURNIN" ${ITEMS_ARG[@]+"${ITEMS_ARG[@]}"} --list 2>"$V3_ROOT/build/e88-list.err") ||
  pf+=("run_e88 --list (tiles against e88.json): $(tail -c 300 "$V3_ROOT/build/e88-list.err") ${LIST:0:300}")
MAXS=$(python3 -c 'import json,sys; print(json.loads(sys.argv[1])["max_s"])' "$LIST" 2>/dev/null)
case "$MAXS" in ''|*[!0-9]*) pf+=("bad run_e88 --list output: ${LIST:0:200}") ;; esac
if [ ${#pf[@]} -gt 0 ]; then printf 'preflight: %s\n' "${pf[@]}" >&2; exit 2; fi

D=$DATA_ROOT/$EXPN/p$PASS
if [ -e "$D/block.json" ] && ! grep -q '"status":"ok"' "$D/block.json"; then mv "$D" "$D.attempt-$(date +%s)"; fi
if [ -d "$D" ] && [ ! -e "$D/block.json" ]; then mv "$D" "$D.attempt-$(date +%s)"; fi
block_begin "$EXPN" "$PASS"
others_present && { block_end others "another user before the first launch"; exit 3; }
[ -n "${V3_DRY:-}" ] || et-lab-manifest > "$OUT/manifest.txt" 2>/dev/null || true      # E78 change 3
( cd "$HERE" && sha256sum e88.json tiles/*/*.bin ) > "$OUT/gen.sha256" 2>/dev/null || true   # E88 change 2
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
python3 "$HERE/run_e88.py" "$OUT" --root "$V3_ROOT" --tel-live "$OUT/telemetry.jsonl.raw" \
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
  *) block_end failed "run_e88 exit $rc"; exit 1 ;;
esac
