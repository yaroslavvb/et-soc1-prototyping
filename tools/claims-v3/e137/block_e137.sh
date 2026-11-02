#!/usr/bin/env bash
# E137 (Q137, tools/claims-v3/e137/E137.md): one pass on aifoundry1 card 1, as a lib.sh block. A port of tools/claims-v3/e128/block_e128.sh with
# these changes, each marked E137:
#   1. it runs tools/claims-v3/e137/run_e137.py (tools/claims-v3/kinds/run_e78.py unchanged, with E137's items and order installed, and E131's stops:
#      board_w >= 68 W or a minion-shire reading >= 72 C writes STOP and ends the pass): E78's six anchors three times a pass, E128's seven fp16 sign
#      tiles and E78's fp16.ones once, the built-in pi tie first and last; every tile checked against its registered sha256 first;
#   2. the die cap passed to run_e78.py is 72 C (E78_MAX_C, default here 72; E128's was 78), as E131's;
#   3. gen.sha256 covers kinds.json, E78's tiles, E128's e128.json and E128's tiles (E137 runs E128's tiles in place);
#   4. its data goes to $DATA_ROOT/e137/p137<nn>/ (smoke: e137-smoke/), so block_begin's code.sha256 covers tools/claims-v3/e137/*;
#   5. CARE WITH DEVICE COMMANDS (the owner's rule of Mon 2 Nov 2026), E128's change 5 unchanged: every telemetry call goes through
#      tools/claims-v3/e128/ettelem_guard.sh (E128's allow-list, byte for byte: `ettelem config` and `ettelem sample --seconds --every-ms` only), and
#      lib.sh's drain_mgmt is replaced by a refusal, so the vendor tool dev_mngt_service is never run;
#   6. binaries.sha256 records the binaries the block executes (E131's change 5).
# Everything else - timeout 10 on the config reads, the card lock, hold10/timeout 10 on every device process, the other-user test (D1: an idle login
# does not block on aifoundry1; another user on this card or any other user's device process does), the launch protocol, the sampler, the STOP file
# - is block_e128.sh's, lib.sh's and hl/block.sh's, unchanged. Nothing is set: no governor, TDP, threshold or clock set, no reset, no --reset-ms.
#
#   bash tools/claims-v3/e137/block_e137.sh <pass> [--smoke]
#   V3_DRY=1 bash tools/claims-v3/e137/block_e137.sh <pass>          # print every device call, touch nothing
#   E78_TARGET=58 E78_PREHEAT=59 E78_QUIET=2.0 E78_BURNIN=2            # the registered defaults (E78's names, kept)
# --smoke: e137_common.SMOKE_ITEMS at the current reading (no preheat), 2 s runs, data under e137-smoke/.
. "$(dirname "${BASH_SOURCE[0]}")/../lib.sh"
ETTELEM=tools/claims-v3/e128/ettelem_guard.sh                                                  # E137 change 5
drain_mgmt() { log "E137: drain refused: dev_mngt_service is not in E137's classified command list"; return 0; }   # E137 change 5
# Departure D1 (hl/README.md, kept by E60-E108): on aifoundry1 and aifoundry3 a user who is only logged in does not block (other lab users keep idle tmux
# logins there); another user on THIS card does, and so does any other user's device process. Fails closed when et-holders is unreadable.
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

PASS=${1:?usage: block_e137.sh <pass> [--smoke]}
SMOKE=; [ "${2:-}" = --smoke ] && SMOKE=1
case "$PASS" in ''|*[!0-9]*) echo "pass must be a number" >&2; exit 2 ;; esac
HERE=tools/claims-v3/e137
KD=tools/claims-v3/kinds
TARGET=${E78_TARGET:-58}; PREHEAT=${E78_PREHEAT:-59}; BURNIN=${E78_BURNIN:-2}; MAXC=${E78_MAX_C:-72}     # E137 change 2
QUIET=${E78_QUIET:-2.0}; TIERS=${E78_TIERS:-1,2}; FMA_S=4; EXPN=e137                                # E137 change 4
ITEMS_ARG=()
if [ -n "$SMOKE" ]; then
  PREHEAT=0; TARGET=200; FMA_S=2; BURNIN=0; EXPN=e137-smoke
  ITEMS_ARG=(--items "$(python3 -c 'import sys; sys.path.insert(0, sys.argv[1]); import e137_common as e; print(",".join(e.SMOKE_ITEMS))' "$HERE")")   # E137 change 2
fi

# ---- preflight: files only, no device ------------------------------------------------------------------------
pf=()
[ -f "$KD/kinds.json" ] || pf+=("no $KD/kinds.json")
[ -f tools/claims-v3/e128/e128/e128.json ] || pf+=("no tools/claims-v3/e128/e128/e128.json")      # E137 change 3
[ -f "$HERE/predictions-e137.json" ] || pf+=("no $HERE/predictions-e137.json")
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
# E137 change 1: run_e137.py (run_e78.py unchanged, E137's items, order and stops) in the preflight and the pass
LIST=$(python3 "$HERE/run_e137.py" /dev/null --root "$V3_ROOT" --first-block "$PASS" --tiers "$TIERS" --card "$CARD" \
       --fma-s "$FMA_S" --burnin "$BURNIN" ${ITEMS_ARG[@]+"${ITEMS_ARG[@]}"} --list 2>"$V3_ROOT/build/e137-list.err") ||
  pf+=("run_e137 --list (tiles against their sha256): $(tail -c 300 "$V3_ROOT/build/e137-list.err") ${LIST:0:300}")
MAXS=$(python3 -c 'import json,sys; print(json.loads(sys.argv[1])["max_s"])' "$LIST" 2>/dev/null)
case "$MAXS" in ''|*[!0-9]*) pf+=("bad run_e137 --list output: ${LIST:0:200}") ;; esac
if [ ${#pf[@]} -gt 0 ]; then printf 'preflight: %s\n' "${pf[@]}" >&2; exit 2; fi

D=$DATA_ROOT/$EXPN/p$PASS
if [ -e "$D/block.json" ] && ! grep -q '"status":"ok"' "$D/block.json"; then mv "$D" "$D.attempt-$(date +%s)"; fi
if [ -d "$D" ] && [ ! -e "$D/block.json" ]; then mv "$D" "$D.attempt-$(date +%s)"; fi
block_begin "$EXPN" "$PASS"
others_present && { block_end others "another user before the first launch"; exit 3; }
[ -n "${V3_DRY:-}" ] || et-lab-manifest > "$OUT/manifest.txt" 2>/dev/null || true      # E78 change 3 (sysfs and files only; it never opens /dev/et*)
( cd tools/claims-v3 && sha256sum kinds/kinds.json kinds/tiles/*/*.bin e128/e128/e128.json e128/e128/tiles/*/*.bin ) > "$OUT/gen.sha256" 2>/dev/null || true   # E137 change 3
sha256sum "$SPARSITY" "$HEATER" build/ettelem/ettelem "$ETTELEM" > "$OUT/binaries.sha256" 2>/dev/null || true          # E137 change 6
# E78 change 2: the card's static configuration, read only (TDP, threshold, clock, voltage), inside the lock, under timeout 10. `ettelem config` has no setter.
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
python3 "$HERE/run_e137.py" "$OUT" --root "$V3_ROOT" --tel-live "$OUT/telemetry.jsonl.raw" \
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
  *) block_end failed "run_e137 exit $rc"; exit 1 ;;
esac
