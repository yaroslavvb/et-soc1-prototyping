#!/usr/bin/env bash
# E164 (Q141(b), tools/claims-v3/e164/E164.md): one pass of blind pool 7, rank 7's eight pool-6 repeat tiles and pool 6's three
# random anchors on aifoundry1 card 1, every launch's C logged, as a lib.sh block. A port of tools/claims-v3/e157/block_e157.sh (E157,
# blind pool 6 on this card), whose card-1 changes (E142 changes 1-6: the live stops and the in-run watcher, E78's protocol, the smoke
# and the stop-path test, card 1 only with run_e78's --max-c 72, every telemetry call through E128's guard and drain_mgmt refused,
# gen.sha256 and binaries.sha256) and C log (E157 change 2) it keeps; its own changes are marked E164:
#   1. it runs tools/claims-v3/e164/run_e164.py (run_e78.py unchanged, E164's items and order, E142's stops and watcher); every
#      tile is checked against its registered sha256 first; passes 16410-16419, the smoke 16401, the stop-path test 16402;
#   2. the files the preflight requires are pool 7's and pool 6's frozen files, predictions-e164.json and harness-e164.json;
#   3. gen.sha256 covers blind pool 7's tiles and manifest files, and the eleven pool-6 tiles (K7's eight, the scale's three anchors);
#      E164_DROP_P2 (the registered priority-2 switch) is logged with the pass and reaches the runner through the environment.
# Everything else - the config reads under timeout 10 at both ends, the card lock, hold10/timeout 10 on every device process, the
# other-user test (D1: an idle login does not block on aifoundry1; another user on this card or any other user's device process does),
# the sampler (no --reset-ms), the STOP file, the C log through Q139(k)'s wrapper - is block_e157.sh's, lib.sh's and hl/block.sh's,
# unchanged. Nothing is set: no governor, TDP, threshold or clock set, no reset, no --reset-ms. Device commands: E164.md, "Device
# commands sent".
#
#   V3_DEVICE=1 bash tools/claims-v3/e164/block_e164.sh <pass> [--smoke|--stoptest]
#   V3_DEVICE=1 V3_DRY=1 bash tools/claims-v3/e164/block_e164.sh <pass>          # print every device call, touch nothing
. "$(dirname "${BASH_SOURCE[0]}")/../lib.sh"
ETTELEM=tools/claims-v3/e128/ettelem_guard.sh                                                  # E142 change 5
drain_mgmt() { log "E164: drain refused: dev_mngt_service is not in E164's classified command list"; return 0; }   # E142 change 5
# Departure D1 (hl/README.md, kept by E60-E157): on aifoundry1 and aifoundry3 a user who is only logged in does not block (other
# lab users keep idle tmux logins there); another user on THIS card does, and so does any other user's device process. Fails closed
# when et-holders is unreadable.
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
[ "$CARD" = aifoundry1-c1 ] || { echo "E164 runs on aifoundry1 card 1 only (V3_DEVICE=1; this is $CARD)" >&2; exit 2; }   # E142 change 4
others_present && exit 3
[ -n "${V3_DEVICE:-}" ] && export V3_DEVICE

PASS=${1:?usage: block_e164.sh <pass> [--smoke|--stoptest]}
MODE=; case "${2:-}" in --smoke) MODE=smoke ;; --stoptest) MODE=stoptest ;; '') ;; *) echo "unknown option ${2}" >&2; exit 2 ;; esac
case "$PASS" in ''|*[!0-9]*) echo "pass must be a number" >&2; exit 2 ;; esac
HERE=tools/claims-v3/kinds
E=tools/claims-v3/e164
CC=tools/claims-v3/ccheck/sparsity_ccheck.sh                                                                                  # E157 change 2
CCHOST=build/ccheck/b/host/sparsity_host
CCELF=build/sparsity/kernel/sparsity.elf
TARGET=${E78_TARGET:-58}; PREHEAT=${E78_PREHEAT:-59}; BURNIN=${E78_BURNIN:-2}; MAXC=${E78_MAX_C:-72}                       # E142 change 4
QUIET=${E78_QUIET:-2.0}; TIERS=${E78_TIERS:-1,2}; FMA_S=4; EXPN=${E78_EXPN:-e164}
ITEMS_ARG=()
if [ -n "$MODE" ]; then
  PREHEAT=0; TARGET=200; QUIET=0.2; FMA_S=2; BURNIN=0; EXPN=${E78_EXPN:-e164}-$MODE                                       # E142 change 3
  ITEMS_ARG=(--items "$(python3 -B -c 'import sys; sys.path.insert(0, sys.argv[1]); import e164_common as e; print(",".join(e.SMOKE_ITEMS))' "$E")")
else
  case "$PASS" in 1641[0-9]) ;; *) echo "pass $PASS is no E164 pass (16410-16419)" >&2; exit 2 ;; esac                    # E164 change 1
fi
log "E164 pass $PASS${MODE:+ ($MODE)}: target $TARGET preheat $PREHEAT quiet $QUIET burnin $BURNIN fma $FMA_S s, die cap $MAXC C; C log via $CC; E164_DROP_P2=${E164_DROP_P2:-0}"

# ---- preflight: files only, no device ------------------------------------------------------------------------
pf=()
[ -f "$HERE/kinds.json" ] || pf+=("no $HERE/kinds.json")
for f in blind7/blind7.json blind7/SHA256SUMS blind7/MANIFEST blind7/predictions-blind7-aifoundry1c1.json blind6/blind6.json blind6/SHA256SUMS; do
  [ -f "$HERE/$f" ] || pf+=("no $HERE/$f")
done
for f in predictions-e164.json harness-e164.json; do [ -f "$E/$f" ] || pf+=("no $E/$f"); done                                # E164 change 2
[ -x "$SPARSITY" ] || pf+=("missing $SPARSITY")
[ -x "$HEATER" ] || pf+=("missing heater $HEATER")
[ -x "$ETTELEM" ] || pf+=("missing $ETTELEM")
[ -x build/ettelem/ettelem ] || pf+=("missing build/ettelem/ettelem")
[ -x "$CC" ] || pf+=("missing the C-logging wrapper $CC")                                                                    # E157 change 2
[ -x "$CCHOST" ] || pf+=("missing the patched host $CCHOST (tools/claims-v3/ccheck/build_host_ccheck.sh)")
[ -f "$CCELF" ] || pf+=("missing the kernel $CCELF")
if [ -x "$CCHOST" ]; then
  for s in 'file:' int8 fp16 '--dump-tiles' '--stop-file' '--c-log' '--c-poison'; do
    grep -a -q -- "$s" "$CCHOST" || pf+=("$CCHOST has no $s")
  done
fi
for b in "$HEATER"; do [ -x "$b" ] && { grep -a -q -- '--stop-file' "$b" || pf+=("$b has no --stop-file"); }; done
LK=/run/lock/etsoc-shire${V3_DEVICE:-0}.lock
[ -n "${V3_DRY:-}" ] || [ -e "$LK" ] || pf+=("no card lock $LK")
mkdir -p "$V3_ROOT/build"
# E164 change 1: run_e164.py (run_e78.py unchanged, E164's items and order, the live stops) in the preflight and the pass
LIST=$(python3 -B "$E/run_e164.py" /dev/null --root "$V3_ROOT" --first-block "$PASS" --tiers "$TIERS" --card "$CARD" \
       --fma-s "$FMA_S" --burnin "$BURNIN" ${ITEMS_ARG[@]+"${ITEMS_ARG[@]}"} --list 2>"$V3_ROOT/build/e164-list.err") ||
  pf+=("run_e164 --list (tiles against their sha256): $(tail -c 300 "$V3_ROOT/build/e164-list.err") ${LIST:0:300}")
MAXS=$(python3 -B -c 'import json,sys; print(json.loads(sys.argv[1])["max_s"])' "$LIST" 2>/dev/null)
case "$MAXS" in ''|*[!0-9]*) pf+=("bad run_e164 --list output: ${LIST:0:200}") ;; esac
if [ ${#pf[@]} -gt 0 ]; then printf 'preflight: %s\n' "${pf[@]}" >&2; exit 2; fi

D=$DATA_ROOT/$EXPN/p$PASS
if [ -e "$D/block.json" ] && ! grep -q '"status":"ok"' "$D/block.json"; then mv "$D" "$D.attempt-$(date +%s)"; fi
if [ -d "$D" ] && [ ! -e "$D/block.json" ]; then mv "$D" "$D.attempt-$(date +%s)"; fi
block_begin "$EXPN" "$PASS"
others_present && { block_end others "another user before the first launch"; exit 3; }
[ -n "${V3_DRY:-}" ] || et-lab-manifest > "$OUT/manifest.txt" 2>/dev/null || true      # sysfs and files only; it never opens /dev/et*
( sha256sum $HERE/kinds.json $HERE/blind7/blind7.json $HERE/blind7/MANIFEST $HERE/blind7/SHA256SUMS $HERE/blind7/tiles/*/*.bin \
    $HERE/blind6/blind6.json $HERE/blind6/SHA256SUMS $HERE/blind6/tiles/fp32/fp32.real_qwen_softmax_v.bin \
    $HERE/blind6/tiles/fp32/fp32.real_smol_softmax_v_causal.bin $HERE/blind6/tiles/fp16/fp16.real_qwen_qk.bin \
    $HERE/blind6/tiles/fp16/fp16.e5m2grid_wide.bin $HERE/blind6/tiles/int8/int8.powerlaw_df4_pc.bin \
    $HERE/blind6/tiles/int8/int8.bheld_bit1.bin $HERE/blind6/tiles/int8/int8.bheld_bit4.bin \
    $HERE/blind6/tiles/int8/int8.real_qwen_w8a8_gate.bin $HERE/blind6/tiles/fp32/fp32.anchor6_randn.bin \
    $HERE/blind6/tiles/fp16/fp16.anchor6_randn.bin $HERE/blind6/tiles/int8/int8.anchor6_full.bin ) > "$OUT/gen.sha256" 2>/dev/null || true   # E164 change 3
sha256sum "$E"/* > "$OUT/e164-code.sha256" 2>/dev/null || true
sha256sum "$SPARSITY" "$HEATER" "$CCHOST" "$CCELF" "$CC" build/ettelem/ettelem "$ETTELEM" > "$OUT/binaries.sha256" 2>/dev/null || true
# The card's static configuration, read only (TDP, threshold, clock, voltage), inside the lock, under timeout 10. `ettelem config`
# has no setter, and the guard admits `config` with no argument only.
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
export CCHECK_LOG="$OUT/c-log.jsonl"                                                                                        # E157 change 2
run_pass() {
  python3 -B "$E/run_e164.py" "$OUT" --root "$V3_ROOT" --tel-live "$OUT/telemetry.jsonl.raw" \
    --heater "$HEATER" --sparsity "$CC" --first-block "$PASS" --seed "$PASS" --tiers "$TIERS" \
    --target "$TARGET" --preheat "$PREHEAT" --quiet-s "$QUIET" --max-c "$MAXC" --fma-s "$FMA_S" --burnin "$BURNIN" \
    --card "$CARD" --shires "${E78_SHIRES:-0xffffffff}" --per-shire "${E78_PER_SHIRE:-32}" ${ITEMS_ARG[@]+"${ITEMS_ARG[@]}"} &
  RUNNER=$!
  wait "$RUNNER"; rc=$?
  RUNNER=
}
if [ "$MODE" = stoptest ]; then                                                                                               # E142 change 3
  st=()
  for k in die board watch; do
    export E164_STOPTEST=$k
    run_pass
    st+=("$k:rc=$rc")
    log "E164 stop-path test ($k): run_e164 exit $rc"
    unset E164_STOPTEST
    # run_e78 refuses to start while its STOP file exists (EXIT_STOP), so each test's STOP line is kept under its own name
    [ -e "$OUT/STOP" ] && mv "$OUT/STOP" "$OUT/STOP.$k"
    sleep 1
  done
  rc=0
  for x in "${st[@]}"; do [ "${x#*:}" = rc=6 ] || rc=1; done
  printf '%s\n' "${st[@]}" > "$OUT/stoptest.rc"
else
  run_pass
fi
sleep 5
stop_sampler
card_config > "$OUT/config_end.json"
[ -s "$OUT/telemetry.jsonl" ] && gzip -f "$OUT/telemetry.jsonl"
[ -s "$OUT/c-log.jsonl" ] && gzip -f "$OUT/c-log.jsonl"
case $rc in
  0) block_end ok "pass $PASS${MODE:+ $MODE}" ;;
  3) block_end others "another user on the card"; exit 3 ;;
  *) block_end failed "run_e164 exit $rc${MODE:+ ($MODE)}"; exit 1 ;;
esac
