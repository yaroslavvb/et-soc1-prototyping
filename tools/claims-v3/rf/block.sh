#!/usr/bin/env bash
# V3-RF, E74, the register-file cell ladder (README.md): one pass (one block) of the chosen items on the local
# card, as a lib.sh block. The runner is hl/run_hl.py, unchanged — the items are ordinary `ec` items whose
# --pattern is one of the two V3-DTF kernels (gen_df.py, build/enercat-df).
#
#   bash tools/claims-v3/rf/block.sh <pass> [items]
#   V3_DRY=1 bash tools/claims-v3/rf/block.sh 1          # print every device call, touch nothing
#   RF_GEN=<make_rf.py dir> RF_TARGET=58 RF_PREHEAT=59 RF_BURNIN=2 ...   # defaults; RF_GEN is build/rf-gen
#   V3_DEVICE=<0|1> ...                                  # aifoundry1 only, and never on a card there
#
# Data: $DATA_ROOT/rf/p<pass>/ (runs.jsonl, marks.jsonl, run.log, telemetry.jsonl.gz, configs.json,
# manifest.txt = et-lab-manifest, gen.sha256 = the operand files that ran, text.sha256 = the binaries' .text).
# A pass whose block.json is not "ok" is moved aside to p<pass>.attempt-<epoch> before it is run again.
. "$(dirname "${BASH_SOURCE[0]}")/../lib.sh"
# Departure D1 of hl/README.md, kept verbatim: on aifoundry3 and aifoundry1 a user who is only logged in does not
# block (idle tmux logins); another user on THIS card does, and so does any other user's device process on a
# one-card host. Fails closed when et-holders is unreadable.
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
ITEMS=${2:-anchor_pi,rf_,rfz_}
case "$PASS" in ''|*[!0-9]*) echo "pass must be a number" >&2; exit 2 ;; esac
HERE=tools/claims-v3/rf
GEN=${RF_GEN:-$V3_ROOT/build/rf-gen}
ENERCAT_RF=${RF_ENERCAT:-build/enercat-df/host/enercat_host}
TARGET=${RF_TARGET:-58}; PREHEAT=${RF_PREHEAT:-59}; BURNIN=${RF_BURNIN:-2}; MAXC=${RF_MAX_C:-78}
FMA_S=4; EC_S=${RF_EC_S:-4}; EXPN=${RF_EXPN:-rf}

# ---- preflight: files only, no device ------------------------------------------------------------------------
pf=()
[ -f "$GEN/manifest.json" ] || pf+=("no $GEN/manifest.json (python3 $HERE/make_rf.py $GEN --check)")
[ -x "$SPARSITY" ] || pf+=("missing $SPARSITY (anchor_pi)")
[ -x "$ETTELEM" ] || pf+=("missing $ETTELEM")
[ -x "$ENERCAT_RF" ] || pf+=("missing $ENERCAT_RF (cmake -S workloads/enercat -B build/enercat-df -DENERCAT_DF=ON)")
if [ -x "$ENERCAT_RF" ]; then
  grep -a -q -- '--operands file:' "$ENERCAT_RF" || pf+=("$ENERCAT_RF has no --operands file:")
  grep -a -q 'df.un1a.fnot' "$ENERCAT_RF" || pf+=("$ENERCAT_RF has no df.un1a.fnot (built without -DENERCAT_DF=ON)")
  grep -a -q 'df.un1b.fnot' "$ENERCAT_RF" || pf+=("$ENERCAT_RF has no df.un1b.fnot")
fi
[ -x "$SPARSITY" ] && { grep -a -q -- '--stop-file' "$SPARSITY" || pf+=("$SPARSITY has no --stop-file"); }
if [ -n "${V3_DEVICE:-}" ]; then   # a stock device layer ignores ET_DEVICES and would open every card
  for b in "$ETTELEM" "$SPARSITY" "$ENERCAT_RF"; do
    [ -x "$b" ] && { grep -qa ET_DEVICES "$b" || pf+=("$b has no ET_DEVICES"); }
  done
fi
LK=/run/lock/etsoc-shire${V3_DEVICE:-0}.lock
[ -n "${V3_DRY:-}" ] || [ -e "$LK" ] || pf+=("no card lock $LK")
LIST=$(python3 "tools/claims-v3/hl/run_hl.py" /dev/null --root "$V3_ROOT" --gen "$GEN" --items "$ITEMS" \
        --burnin "$BURNIN" --ec-s "$EC_S" --fma-s "$FMA_S" --list 2>"$V3_ROOT/build/rf-list.err") ||
  pf+=("run_hl --list: $(tail -c 300 "$V3_ROOT/build/rf-list.err")")
MAXS=$(python3 -c 'import json,sys; print(json.loads(sys.argv[1])["max_s"])' "$LIST" 2>/dev/null)
case "$MAXS" in ''|*[!0-9]*) pf+=("bad run_hl --list output: ${LIST:0:200}") ;; esac
if [ ${#pf[@]} -gt 0 ]; then printf 'preflight: %s\n' "${pf[@]}" >&2; exit 2; fi

D=$DATA_ROOT/$EXPN/p$PASS
if [ -e "$D/block.json" ] && ! grep -q '"status":"ok"' "$D/block.json"; then mv "$D" "$D.attempt-$(date +%s)"; fi
if [ -d "$D" ] && [ ! -e "$D/block.json" ]; then mv "$D" "$D.attempt-$(date +%s)"; fi
block_begin "$EXPN" "$PASS"
others_present && { block_end others "another user before the first launch"; exit 3; }
et-lab-manifest > "$OUT/manifest.txt" 2>/dev/null || true
( cd "$GEN" && sha256sum manifest.json srcs/* ) > "$OUT/gen.sha256" 2>/dev/null || true
bash tools/claims-v3/text_hash.sh "$ENERCAT_RF" "$SPARSITY" > "$OUT/text.sha256" 2>/dev/null || true
start_sampler "$OUT/telemetry.jsonl" $((MAXS + 900)) || { block_end failed "sampler did not start"; exit 4; }
sleep 3
RUNNER=
on_signal() { [ -n "$RUNNER" ] && kill -TERM "$RUNNER" 2>/dev/null; wait "$RUNNER" 2>/dev/null; stop_sampler; block_end failed "signal"; exit 1; }
trap on_signal TERM INT HUP
python3 "tools/claims-v3/hl/run_hl.py" "$OUT" --root "$V3_ROOT" --gen "$GEN" --items "$ITEMS" \
  --tel-live "$OUT/telemetry.jsonl.raw" --heater "$HEATER" --sparsity "$SPARSITY" --enercat "$ENERCAT_RF" \
  --blocks 1 --first-block "$PASS" --seed "$PASS" --target "$TARGET" --preheat "$PREHEAT" --max-c "$MAXC" \
  --fma-s "$FMA_S" --ec-s "$EC_S" --burnin "$BURNIN" --card "$CARD" \
  --shires "${RF_SHIRES:-0xffffffff}" --per-shire "${RF_PER_SHIRE:-32}" &
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
