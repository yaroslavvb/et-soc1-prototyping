#!/usr/bin/env bash
# E134 (Q136, tools/claims-v3/e134/README.md): one block of E134's fp32 single-bit trains on aifoundry3 card 0, as a lib.sh
# block. A port of tools/claims-v3/e130/block_e130.sh, itself a port of tools/claims-v3/e127/block_e127.sh (E127's aifoundry3
# block, run on this card on 2 Nov 2026), with these changes, each marked E134:
#   1. it runs tools/claims-v3/e134/run_e134.py (run_e78.py unchanged, with E134's items and orders installed); every tile
#      is checked against its registered sha256 first;
#   2. the pass number sets the block, and both blocks are TRAINS, E102's train protocol: --preheat 0 --target 200
#      --quiet-s 0.2 --burnin 0, E78's runner's own options, so no heater, no launch reading, no burn-in, no anchors:
#      A (13410-13419) the A side on two words, B (13420-13429) the B side (e134_common.py);
#   3. --smoke runs e134_common.SMOKE_ITEMS, 2 s each, under kinds-smoke/;
#   4. gen.sha256 covers E134's tiles (tools/claims-v3/e134/e134/) and their manifest, and e134-code.sha256 records
#      tools/claims-v3/e134/*;
#   5. its data goes to $DATA_ROOT/kinds/p134<nn>/ (E78's directory, E134's pass numbers);
#   6. the stops are E127's and E130's: die 70 C (E78_MAX_C default 70) and board power 65 W (run_e134.py).
# Everything else - the config reads under timeout 10 at both ends, the card lock, hold10/timeout 10 on every device
# process, the other-user test, the sampler (no --reset-ms), the STOP file - is block_e127.sh's, lib.sh's and hl/block.sh's,
# unchanged. Device commands: README.md, "Device commands sent" (every one a read; no write of any kind).
#
#   bash tools/claims-v3/e134/block_e134.sh <pass> [--smoke]
#   V3_DRY=1 bash tools/claims-v3/e134/block_e134.sh <pass>          # print every device call, touch nothing
. "$(dirname "${BASH_SOURCE[0]}")/../lib.sh"
# Departure D1 (hl/README.md, kept by E60-E127): on aifoundry3 a user who is only logged in does not block (other
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
[ "$CARD" = aifoundry3 ] || { echo "E134 runs on aifoundry3 card 0 only (this is $CARD)" >&2; exit 2; }   # E134
others_present && exit 3
[ -n "${V3_DEVICE:-}" ] && export V3_DEVICE

PASS=${1:?usage: block_e134.sh <pass> [--smoke]}
SMOKE=; [ "${2:-}" = --smoke ] && SMOKE=1
case "$PASS" in ''|*[!0-9]*) echo "pass must be a number" >&2; exit 2 ;; esac
HERE=tools/claims-v3/kinds
E=tools/claims-v3/e134                                                                   # E134
TARGET=${E78_TARGET:-58}; PREHEAT=${E78_PREHEAT:-59}; BURNIN=${E78_BURNIN:-2}; MAXC=${E78_MAX_C:-70}
QUIET=${E78_QUIET:-2.0}; TIERS=${E78_TIERS:-1,2}; FMA_S=4; EXPN=${E78_EXPN:-kinds}   # E78 change 4
ITEMS_ARG=()
case "$PASS" in        # E134 change 2: the pass number says which block; both are trains
  1341[0-9]) BLOCK=A; PREHEAT=0; TARGET=200; QUIET=0.2; BURNIN=0 ;;
  1342[0-9]) BLOCK=B; PREHEAT=0; TARGET=200; QUIET=0.2; BURNIN=0 ;;
  *) BLOCK=S ;;
esac
if [ -n "$SMOKE" ]; then
  PREHEAT=0; TARGET=200; QUIET=0.2; FMA_S=2; BURNIN=0; EXPN=${E78_EXPN:-kinds}-smoke
  ITEMS_ARG=(--items "$(python3 -c 'import sys; sys.path.insert(0, sys.argv[1]); import e134_common as e; print(",".join(e.SMOKE_ITEMS))' "$E")")   # E134 change 3
fi
[ -n "$SMOKE" ] || [ "$BLOCK" != S ] || { echo "pass $PASS is no E134 block (A 13410-13419, B 13420-13429)" >&2; exit 2; }
log "E134 block $BLOCK${SMOKE:+ smoke}, pass $PASS: target $TARGET preheat $PREHEAT quiet $QUIET burnin $BURNIN fma $FMA_S s, die stop $MAXC C"

# ---- preflight: files only, no device ------------------------------------------------------------------------
pf=()
[ -f "$HERE/kinds.json" ] || pf+=("no $HERE/kinds.json")
for f in e134/e134-tiles.json e134/sha256.txt predictions-e134.json; do [ -f "$E/$f" ] || pf+=("no $E/$f"); done   # E134 change 4
[ -x "$SPARSITY" ] || pf+=("missing $SPARSITY")
[ -x "$HEATER" ] || pf+=("missing heater $HEATER")
[ -x "$ETTELEM" ] || pf+=("missing $ETTELEM")
if [ -x "$SPARSITY" ]; then
  for s in 'file:' fp32 '--dump-tiles'; do
    grep -a -q -- "$s" "$SPARSITY" || pf+=("$SPARSITY has no $s")
  done
fi
for b in "$SPARSITY" "$HEATER"; do [ -x "$b" ] && { grep -a -q -- '--stop-file' "$b" || pf+=("$b has no --stop-file"); }; done
LK=/run/lock/etsoc-shire${V3_DEVICE:-0}.lock
[ -n "${V3_DRY:-}" ] || [ -e "$LK" ] || pf+=("no card lock $LK")
mkdir -p "$V3_ROOT/build"
# E134 change 1: run_e134.py (run_e78.py unchanged, E134's items and orders) in the preflight and the pass
LIST=$(python3 "$E/run_e134.py" /dev/null --root "$V3_ROOT" --first-block "$PASS" --tiers "$TIERS" --card "$CARD" \
       --fma-s "$FMA_S" --burnin "$BURNIN" ${ITEMS_ARG[@]+"${ITEMS_ARG[@]}"} --list 2>"$V3_ROOT/build/e134-list.err") ||
  pf+=("run_e134 --list (tiles against their sha256): $(tail -c 300 "$V3_ROOT/build/e134-list.err") ${LIST:0:300}")
MAXS=$(python3 -c 'import json,sys; print(json.loads(sys.argv[1])["max_s"])' "$LIST" 2>/dev/null)
case "$MAXS" in ''|*[!0-9]*) pf+=("bad run_e134 --list output: ${LIST:0:200}") ;; esac
if [ ${#pf[@]} -gt 0 ]; then printf 'preflight: %s\n' "${pf[@]}" >&2; exit 2; fi

D=$DATA_ROOT/$EXPN/p$PASS
if [ -e "$D/block.json" ] && ! grep -q '"status":"ok"' "$D/block.json"; then mv "$D" "$D.attempt-$(date +%s)"; fi
if [ -d "$D" ] && [ ! -e "$D/block.json" ]; then mv "$D" "$D.attempt-$(date +%s)"; fi
block_begin "$EXPN" "$PASS"
others_present && { block_end others "another user before the first launch"; exit 3; }
[ -n "${V3_DRY:-}" ] || et-lab-manifest > "$OUT/manifest.txt" 2>/dev/null || true      # E78 change 3
( sha256sum $HERE/kinds.json $E/e134/e134-tiles.json $E/e134/sha256.txt $E/e134/tiles/fp32/*.bin ) \
    > "$OUT/gen.sha256" 2>/dev/null || true   # E134 change 4
sha256sum "$E"/* > "$OUT/e134-code.sha256" 2>/dev/null || true                                  # E134 change 4
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
python3 "$E/run_e134.py" "$OUT" --root "$V3_ROOT" --tel-live "$OUT/telemetry.jsonl.raw" \
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
  0) block_end ok "block $BLOCK${SMOKE:+ smoke}" ;;
  3) block_end others "another user on the card"; exit 3 ;;
  *) block_end failed "run_e134 exit $rc"; exit 1 ;;
esac
