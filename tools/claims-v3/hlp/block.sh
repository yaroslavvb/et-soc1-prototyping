#!/usr/bin/env bash
# V3-HLP (E79, README.md): one pass (one block) of the fp16/int8 bit-flip-ladder items on the local card.
# A port of tools/claims-v3/hl/block.sh (E60/E65/E67/E70) with four changes, each marked E79 below:
#   1. it runs tools/claims-v3/hlp/run_hlp.py (the per-item --type runner) and the operand set build/hlp-gen;
#   2. the enercat preflight and items are gone (E79 has no catalogue items);
#   3. it writes a read-only `ettelem config` at the start and at the end of every pass (TDP and threshold, the
#      reading CONTEXT section 4 asks for), which is the only management read it makes;
#   4. its data goes to $DATA_ROOT/hlp/p<pass>/.
# Everything else - the card lock, hold10/timeout 10 on every device process, the other-user test, the launch
# protocol, the sampler, the STOP file - is lib.sh's and hl/block.sh's, unchanged.
#
#   bash tools/claims-v3/hlp/block.sh <pass> <items> [--smoke]
#   V3_DRY=1 bash tools/claims-v3/hlp/block.sh ...                       # print every device call, touch nothing
#   HLP_TARGET=58 HLP_PREHEAT=59 HLP_BURNIN=2 HLP_GEN=<make_hlp.py dir>  # defaults
#
# <items>: comma-separated item names or family prefixes from manifest.json. The shuffle seed is the pass number.
# --smoke: anchor_pi, h16q, b16_9, h8q, b8_6 at the current reading (no preheat), 2 s runs.
. "$(dirname "${BASH_SOURCE[0]}")/../lib.sh"
# Departure D1 (hl/README.md, kept): on aifoundry3 a user who is only logged in does not block (other lab users
# keep idle tmux logins there); another user on THIS card does, and so does any other user's device process.
# Fails closed when et-holders is unreadable.
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

PASS=${1:?usage: block.sh <pass> <items> [--smoke]}
ITEMS=${2:?usage: block.sh <pass> <items> [--smoke]}
SMOKE=; [ "${3:-}" = --smoke ] && SMOKE=1
case "$PASS" in ''|*[!0-9]*) echo "pass must be a number" >&2; exit 2 ;; esac
HERE=tools/claims-v3/hlp                       # E79 change 1
GEN=${HLP_GEN:-$V3_ROOT/build/hlp-gen}         # E79 change 1
TARGET=${HLP_TARGET:-58}; PREHEAT=${HLP_PREHEAT:-59}; BURNIN=${HLP_BURNIN:-2}; MAXC=${HLP_MAX_C:-78}
FMA_S=4; EXPN=${HLP_EXPN:-hlp}                 # E79 change 4
if [ -n "$SMOKE" ]; then
  PREHEAT=0; TARGET=200; FMA_S=2; BURNIN=0; EXPN=${HLP_EXPN:-hlp}-smoke
  ITEMS=anchor_pi,h16q,b16_9,h8q,b8_6
fi

# ---- preflight: files only, no device ------------------------------------------------------------------------
pf=()
[ -f "$GEN/manifest.json" ] || pf+=("no $GEN/manifest.json (python3 $HERE/make_hlp.py $GEN)")
[ -x "$SPARSITY" ] || pf+=("missing $SPARSITY")
[ -x "$HEATER" ] || pf+=("missing heater $HEATER")
[ -x "$ETTELEM" ] || pf+=("missing $ETTELEM")
if [ -x "$SPARSITY" ]; then
  grep -a -q 'file:' "$SPARSITY" || pf+=("$SPARSITY has no --values file:")
  # E79: the same binary must take fp16 and int8 for --test fma
  grep -a -q 'fp16' "$SPARSITY" || pf+=("$SPARSITY has no fp16")
  grep -a -q 'int8' "$SPARSITY" || pf+=("$SPARSITY has no int8")
fi
for b in "$SPARSITY" "$HEATER"; do [ -x "$b" ] && { grep -a -q -- '--stop-file' "$b" || pf+=("$b has no --stop-file"); }; done
LK=/run/lock/etsoc-shire${V3_DEVICE:-0}.lock
[ -n "${V3_DRY:-}" ] || [ -e "$LK" ] || pf+=("no card lock $LK")
LIST=$(python3 "$HERE/run_hlp.py" /dev/null --root "$V3_ROOT" --gen "$GEN" --items "$ITEMS" --burnin "$BURNIN" --list 2>"$V3_ROOT/build/hlp-list.err") ||
  pf+=("run_hlp --list: $(tail -c 300 "$V3_ROOT/build/hlp-list.err")")
MAXS=$(python3 -c 'import json,sys; print(json.loads(sys.argv[1])["max_s"])' "$LIST" 2>/dev/null)
case "$MAXS" in ''|*[!0-9]*) pf+=("bad run_hlp --list output: ${LIST:0:200}") ;; esac
if [ ${#pf[@]} -gt 0 ]; then printf 'preflight: %s\n' "${pf[@]}" >&2; exit 2; fi

D=$DATA_ROOT/$EXPN/p$PASS
if [ -e "$D/block.json" ] && ! grep -q '"status":"ok"' "$D/block.json"; then mv "$D" "$D.attempt-$(date +%s)"; fi
if [ -d "$D" ] && [ ! -e "$D/block.json" ]; then mv "$D" "$D.attempt-$(date +%s)"; fi
block_begin "$EXPN" "$PASS"
others_present && { block_end others "another user before the first launch"; exit 3; }
et-lab-manifest > "$OUT/manifest.txt" 2>/dev/null || true
( cd "$GEN" && sha256sum manifest.json tiles/* ) > "$OUT/gen.sha256" 2>/dev/null || true
# E79 change 3: the card's static configuration, read only (TDP, temperature threshold, clock, voltage), while
# this block holds the card lock. Nothing is written: `ettelem config` has no setter.
card_config() {
  if [ -n "${V3_DRY:-}" ]; then echo "DRY ettelem config" >&2; echo '{"dry":true}'; return 0; fi
  timeout 20 "$ETTELEM" config 2>/dev/null < /dev/null | grep '^{' | tail -1 || true
}
card_config > "$OUT/config_start.json"
start_sampler "$OUT/telemetry.jsonl" $((MAXS + 900)) || { block_end failed "sampler did not start"; exit 4; }
sleep 3
RUNNER=
on_signal() { [ -n "$RUNNER" ] && kill -TERM "$RUNNER" 2>/dev/null; wait "$RUNNER" 2>/dev/null; stop_sampler; block_end failed "signal"; exit 1; }
trap on_signal TERM INT HUP
python3 "$HERE/run_hlp.py" "$OUT" --root "$V3_ROOT" --gen "$GEN" --items "$ITEMS" --tel-live "$OUT/telemetry.jsonl.raw" \
  --heater "$HEATER" --sparsity "$SPARSITY" --blocks 1 --first-block "$PASS" --seed "$PASS" \
  --target "$TARGET" --preheat "$PREHEAT" --max-c "$MAXC" --fma-s "$FMA_S" --burnin "$BURNIN" --card "$CARD" \
  --shires "${HLP_SHIRES:-0xffffffff}" --per-shire "${HLP_PER_SHIRE:-32}" &
RUNNER=$!
wait "$RUNNER"; rc=$?
RUNNER=
sleep 5
stop_sampler
card_config > "$OUT/config_end.json"
[ -s "$OUT/telemetry.jsonl" ] && gzip -f "$OUT/telemetry.jsonl"
case $rc in
  0) block_end ok "$ITEMS" ;;
  3) block_end others "another user on the card"; exit 3 ;;
  *) block_end failed "run_hlp exit $rc"; exit 1 ;;
esac
