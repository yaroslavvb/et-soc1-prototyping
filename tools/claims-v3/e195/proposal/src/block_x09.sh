#!/usr/bin/env bash
# x09, memory traffic with designed data: one pass (one block) of the arms on the local card, as a block of the public
# lab repo's tools/claims-v3/lib.sh, run by its tools/claims-v3/runitems.py from this request's manifest. It is
# tools/claims-v3/mf/block.sh (E75, the memory-path ladder) with this request's host and manifest in place of
# enercat's, and with lib_x09.sh's four changes to lib.sh (every telemetry call through the lab's E128 guard and no
# drain; the tree; the login; the kits' other-user test); the approach, the anchor, the shuffle, the records and the
# stops are runitems.py's, unchanged.
#
#   X9_ROOT=<tree> bash tools/claims-v3/x09/block_x09.sh <pass> [items]   # this src/ at <tree>/tools/claims-v3/x09/
#   X9_ROOT=<tree> V3_DRY=1 bash tools/claims-v3/x09/block_x09.sh 1       # print every device call, touch nothing
#   X9_GEN=<make_x09.py dir> X9_HOST=<x09mem_host> X9_TARGET=58 X9_PREHEAT=59 X9_BURNIN=2 X9_ITEM_S=4 X9_MAX_C=70  # defaults
#
# The tree holds, beside this folder, the lab repo's tools/claims-v3/lib.sh, runitems.py, text_hash.sh and
# e128/ettelem_guard.sh, and its builds build/ettelem/ettelem and build/sparsity/host/sparsity_host (the anchor and the
# heater); this request's host at build/x09mem/host/x09mem_host and its manifest at build/x09-gen. Everything is
# written under the tree's build/.
# Data: $DATA_ROOT/x09/p<pass>/ (runs.jsonl, marks.jsonl, run.log, telemetry.jsonl.gz, configs.json, manifest.txt,
# gen.sha256, text.sha256 (the host, the heater and the kernel ELF the host launches), code.sha256 (every source file
# of the run, the manifest, the host and the kernel)). A pass whose block.json is not "ok" is moved aside before a
# re-run. Exit 0 ok; 1 failed; 2 refused before the card (preflight, tree, login); 3 another user; 4 no sampler.
HERE=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd -P)
if [ ! -f "$HERE/../lib.sh" ]; then
  echo "no lib.sh beside this folder ($HERE/..): put this src/ at <tree>/tools/claims-v3/x09/" >&2; exit 2
fi
. "$HERE/../lib.sh"        # set -u; goes to its tree (V3_ROOT); CARD, DATA_ROOT, SPARSITY, HEATER
. "$HERE/lib_x09.sh"       # ETTELEM = the guard, no drain; X9_ROOT = V3_ROOT; USER = this login; others_present
others_present && exit 3
[ -n "${V3_DEVICE:-}" ] && export V3_DEVICE

PASS=${1:?usage: block_x09.sh <pass> [items]}
ITEMS=${2:-anchor_pi,x9_}
case "$PASS" in ''|*[!0-9]*) echo "pass must be a number" >&2; exit 2 ;; esac
GEN=${X9_GEN:-$V3_ROOT/build/x09-gen}
HOST=${X9_HOST:-build/x09mem/host/x09mem_host}
TARGET=${X9_TARGET:-58}; PREHEAT=${X9_PREHEAT:-59}; BURNIN=${X9_BURNIN:-2}; MAXC=${X9_MAX_C:-70}
ITEM_S=${X9_ITEM_S:-4}; FMA_S=4; EXPN=${X9_EXPN:-x09}

# ---- preflight: files only, no device ------------------------------------------------------------------------
pf=()
mkdir -p "$V3_ROOT/build"
[ -f "$GEN/manifest.json" ] || pf+=("no $GEN/manifest.json (python3 make_x09.py $GEN --host $HOST --check)")
[ -x "$SPARSITY" ] || pf+=("missing $SPARSITY (anchor_pi and the heater)")
[ -x "$ETTELEM" ] || pf+=("missing $ETTELEM (the lab's E128 guard: every telemetry call goes through it)")
[ -x build/ettelem/ettelem ] || pf+=("missing build/ettelem/ettelem (the reader $ETTELEM execs)")
for f in tools/claims-v3/runitems.py tools/claims-v3/text_hash.sh; do [ -f "$f" ] || pf+=("missing $f"); done
[ -x "$HOST" ] || pf+=("missing $HOST (cmake -S $HERE -B build/x09mem -DCMAKE_PREFIX_PATH=/opt/et)")
KELF=
if [ -x "$HOST" ]; then
  grep -a -q 'X09MEM {' "$HOST" || pf+=("$HOST does not print X09MEM records")
  "$HOST" --list --json > /dev/null 2>&1 || pf+=("$HOST --list fails")
  KELF=$(grep -a -o '/[[:alnum:]/._-]*/x09mem\.elf' "$HOST" | head -1)
  [ -n "$KELF" ] && [ -f "$KELF" ] || pf+=("the kernel ELF compiled into $HOST (${KELF:-no path found}) is not there")
fi
[ -x "$SPARSITY" ] && { grep -a -q -- '--stop-file' "$SPARSITY" || pf+=("$SPARSITY has no --stop-file"); }
LK=/run/lock/etsoc-shire${V3_DEVICE:-0}.lock
[ -n "${V3_DRY:-}" ] || [ -e "$LK" ] || pf+=("no card lock $LK")
LIST=$(python3 tools/claims-v3/runitems.py /dev/null --root "$V3_ROOT" --gen "$GEN" --items "$ITEMS" \
        --tool "$HOST" --burnin "$BURNIN" --item-s "$ITEM_S" --list 2>"$V3_ROOT/build/x09-list.err") ||
  pf+=("runitems --list: $(tail -c 300 "$V3_ROOT/build/x09-list.err")")
MAXS=$(python3 -c 'import json,sys; print(json.loads(sys.argv[1])["max_s"])' "$LIST" 2>/dev/null)
case "$MAXS" in ''|*[!0-9]*) pf+=("bad runitems --list output: ${LIST:0:200}") ;; esac
if [ ${#pf[@]} -gt 0 ]; then printf 'preflight: %s\n' "${pf[@]}" >&2; exit 2; fi

D=$DATA_ROOT/$EXPN/p$PASS
if [ -e "$D/block.json" ] && ! grep -q '"status":"ok"' "$D/block.json"; then mv "$D" "$D.attempt-$(date +%s)"; fi
if [ -d "$D" ] && [ ! -e "$D/block.json" ]; then mv "$D" "$D.attempt-$(date +%s)"; fi
block_begin "$EXPN" "$PASS"
others_present && { block_end others "another user before the first launch"; exit 3; }
et-lab-manifest > "$OUT/manifest.txt" 2>/dev/null || true
( cd "$GEN" && sha256sum manifest.json counts.json ) > "$OUT/gen.sha256" 2>/dev/null || true
{ bash tools/claims-v3/text_hash.sh "$HOST" "$SPARSITY"; x9_kernel_hash "$KELF"; } > "$OUT/text.sha256" 2>/dev/null
# what ran, file by file (lib.sh's own code.sha256 globs this folder, which hashes neither host/ nor kernel/)
{ sha256sum tools/claims-v3/lib.sh tools/claims-v3/runitems.py tools/claims-v3/text_hash.sh "$ETTELEM" \
    "$HERE"/*.* "$HERE"/host/* "$HERE"/kernel/* "$GEN/manifest.json" "$GEN/counts.json" \
    "$HOST" "$KELF" "$SPARSITY"; } > "$OUT/code.sha256" 2>/dev/null
start_sampler "$OUT/telemetry.jsonl" $((MAXS + 900)) || { block_end failed "sampler did not start"; exit 4; }
sleep 3
RUNNER=
on_signal() { [ -n "$RUNNER" ] && kill -TERM "$RUNNER" 2>/dev/null; wait "$RUNNER" 2>/dev/null; stop_sampler; block_end failed "signal"; exit 1; }
trap on_signal TERM INT HUP
python3 tools/claims-v3/runitems.py "$OUT" --root "$V3_ROOT" --gen "$GEN" --items "$ITEMS" \
  --tool "$HOST" --tel-live "$OUT/telemetry.jsonl.raw" --heater "$HEATER" --sparsity "$SPARSITY" \
  --blocks 1 --first-block "$PASS" --seed "$PASS" --target "$TARGET" --preheat "$PREHEAT" --max-c "$MAXC" \
  --item-s "$ITEM_S" --fma-s "$FMA_S" --burnin "$BURNIN" --card "$CARD" &
RUNNER=$!
wait "$RUNNER"; rc=$?
RUNNER=
sleep 5
stop_sampler
[ -s "$OUT/telemetry.jsonl" ] && gzip -f "$OUT/telemetry.jsonl"
case $rc in
  0) block_end ok "$ITEMS" ;;
  3) block_end others "another user on the card"; exit 3 ;;
  *) block_end failed "runitems exit $rc"; exit 1 ;;
esac
