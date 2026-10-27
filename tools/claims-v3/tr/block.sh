#!/usr/bin/env bash
# V3-TR, E76, the instructions that trap in U-mode (README.md): one pass (one block) of the chosen items on the local card,
# as a lib.sh block. The runner is tools/claims-v3/runitems.py, which takes each item's enercat arguments from the
# manifest (a probe item needs --window 0 --seconds 0.001, which hl/run_hl.py does not carry).
#
# EVERY PROBE ITEM IS EXPECTED TO FAIL ITS LAUNCH on a trapping mode: the kernel dies on that hart, the host
# prints "ok":false with no ops, and runitems.py records the line and goes on. That IS the measurement.
#
#   bash tools/claims-v3/tr/block.sh <pass> [items]
#   V3_DRY=1 bash tools/claims-v3/tr/block.sh 1          # print every device call, touch nothing
#   TR_GEN=<make_tr.py dir> TR_TARGET=58 TR_PREHEAT=59 TR_BURNIN=2 TR_ITEM_S=4 ...   # defaults
#
# Data: $DATA_ROOT/tr/p<pass>/ (runs.jsonl, marks.jsonl, run.log, telemetry.jsonl.gz, configs.json,
# manifest.txt, gen.sha256, text.sha256). A pass whose block.json is not "ok" is moved aside before a re-run.
. "$(dirname "${BASH_SOURCE[0]}")/../lib.sh"
# Departure D1 of hl/README.md, kept verbatim: on aifoundry3 and aifoundry1 a user who is only logged in does not
# block; another user on THIS card does, and so does any other user's device process on a one-card host.
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

PASS=${1:?usage: block.sh <pass> [items]}
ITEMS=${2:-anchor_pi,trp_}
case "$PASS" in ''|*[!0-9]*) echo "pass must be a number" >&2; exit 2 ;; esac
GEN=${TR_GEN:-$V3_ROOT/build/tr-gen}
ENERCAT_TR=${TR_ENERCAT:-build/enercat-tr/host/enercat_host}
TARGET=${TR_TARGET:-58}; PREHEAT=${TR_PREHEAT:-59}; BURNIN=${TR_BURNIN:-2}; MAXC=${TR_MAX_C:-78}
ITEM_S=${TR_ITEM_S:-4}; FMA_S=4; EXPN=${TR_EXPN:-tr}

# ---- preflight: files only, no device ------------------------------------------------------------------------
pf=()
[ -f "$GEN/manifest.json" ] || pf+=("no $GEN/manifest.json (python3 tools/claims-v3/tr/make_tr.py $GEN --check)")
[ -x "$SPARSITY" ] || pf+=("missing $SPARSITY (anchor_pi and the heater)")
[ -x "$ETTELEM" ] || pf+=("missing $ETTELEM")
[ -x "$ENERCAT_TR" ] || pf+=("missing $ENERCAT_TR (cmake -S workloads/enercat -B build/enercat-tr -DENERCAT_TR=ON)")
if [ -x "$ENERCAT_TR" ]; then
  grep -a -q 'tr.fdiv.s' "$ENERCAT_TR" || pf+=("$ENERCAT_TR has no tr.fdiv.s (built without -DENERCAT_TR=ON)")
  grep -a -q 'tr.csrr.cycle' "$ENERCAT_TR" || pf+=("$ENERCAT_TR has no tr.csrr.cycle")
  grep -a -q 'tr.ctl.frcp.ps' "$ENERCAT_TR" || pf+=("$ENERCAT_TR has no tr.ctl.frcp.ps (the controls)")
fi
[ -x "$SPARSITY" ] && { grep -a -q -- '--stop-file' "$SPARSITY" || pf+=("$SPARSITY has no --stop-file"); }
LK=/run/lock/etsoc-shire${V3_DEVICE:-0}.lock
[ -n "${V3_DRY:-}" ] || [ -e "$LK" ] || pf+=("no card lock $LK")
LIST=$(python3 tools/claims-v3/runitems.py /dev/null --root "$V3_ROOT" --gen "$GEN" --items "$ITEMS" \
        --tool "$ENERCAT_TR" --burnin "$BURNIN" --item-s "$ITEM_S" --list 2>"$V3_ROOT/build/tr-list.err") ||
  pf+=("runitems --list: $(tail -c 300 "$V3_ROOT/build/tr-list.err")")
MAXS=$(python3 -c 'import json,sys; print(json.loads(sys.argv[1])["max_s"])' "$LIST" 2>/dev/null)
case "$MAXS" in ''|*[!0-9]*) pf+=("bad runitems --list output: ${LIST:0:200}") ;; esac
if [ ${#pf[@]} -gt 0 ]; then printf 'preflight: %s\n' "${pf[@]}" >&2; exit 2; fi

D=$DATA_ROOT/$EXPN/p$PASS
if [ -e "$D/block.json" ] && ! grep -q '"status":"ok"' "$D/block.json"; then mv "$D" "$D.attempt-$(date +%s)"; fi
if [ -d "$D" ] && [ ! -e "$D/block.json" ]; then mv "$D" "$D.attempt-$(date +%s)"; fi
block_begin "$EXPN" "$PASS"
others_present && { block_end others "another user before the first launch"; exit 3; }
et-lab-manifest > "$OUT/manifest.txt" 2>/dev/null || true
( cd "$GEN" && sha256sum manifest.json srcs/* ) > "$OUT/gen.sha256" 2>/dev/null || true
bash tools/claims-v3/text_hash.sh "$ENERCAT_TR" "$SPARSITY" > "$OUT/text.sha256" 2>/dev/null || true
start_sampler "$OUT/telemetry.jsonl" $((MAXS + 900)) || { block_end failed "sampler did not start"; exit 4; }
sleep 3
RUNNER=
on_signal() { [ -n "$RUNNER" ] && kill -TERM "$RUNNER" 2>/dev/null; wait "$RUNNER" 2>/dev/null; stop_sampler; block_end failed "signal"; exit 1; }
trap on_signal TERM INT HUP
python3 tools/claims-v3/runitems.py "$OUT" --root "$V3_ROOT" --gen "$GEN" --items "$ITEMS" \
  --tool "$ENERCAT_TR" --tel-live "$OUT/telemetry.jsonl.raw" --heater "$HEATER" --sparsity "$SPARSITY" \
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
