#!/usr/bin/env bash
# E157 (Q139, tools/claims-v3/e157/README.md): one pass of blind pool 6 and K1's six pool-5 tiles on aifoundry1 card 1, every launch's
# C logged, as a lib.sh block. A port of tools/claims-v3/e142/block_e142.sh (E142, blind pool 5 on this card), whose card-1 changes
# (E142 changes 1-6: the live stops and the in-run watcher, E78's protocol, the smoke and the stop-path test, card 1 only with
# run_e78's --max-c 72, every telemetry call through E128's guard and drain_mgmt refused, gen.sha256 and binaries.sha256) it keeps;
# its own changes are marked E157:
#   1. it runs tools/claims-v3/e157/run_e157.py (run_e78.py unchanged, E157's items and order, E142's stops and watcher); every
#      tile is checked against its registered sha256 first; passes 15710-15719, the smoke 15701, the stop-path test 15702;
#   2. THE C CHECK (Q139(k)): every measured launch, the smoke's included, runs through tools/claims-v3/ccheck/sparsity_ccheck.sh
#      (the patched host build/ccheck/b/host/sparsity_host, --c-log <pass>/c-log.jsonl --c-poison, the power passes' kernel
#      build/sparsity/kernel/sparsity.elf); CCHECK_LOG is exported to the runner; the heater stays on build/sparsity/host/sparsity_host;
#      the preflight requires the wrapper, the patched host (with --c-log in it) and the kernel;
#   3. gen.sha256 covers blind pool 6's tiles and manifest and K1's six pool-5 tiles; binaries.sha256 records every binary the block
#      executes, the patched host and the kernel included.
# Everything else - the config reads under timeout 10 at both ends, the card lock, hold10/timeout 10 on every device process, the
# other-user test (D1: an idle login does not block on aifoundry1; another user on this card or any other user's device process does),
# the sampler (no --reset-ms), the STOP file - is block_e142.sh's, lib.sh's and hl/block.sh's, unchanged. Nothing is set: no
# governor, TDP, threshold or clock set, no reset, no --reset-ms. Device commands: README.md, "Device commands sent".
#
#   V3_DEVICE=1 bash tools/claims-v3/e157/block_e157.sh <pass> [--smoke|--stoptest]
#   V3_DEVICE=1 V3_DRY=1 bash tools/claims-v3/e157/block_e157.sh <pass>          # print every device call, touch nothing
. "$(dirname "${BASH_SOURCE[0]}")/../lib.sh"
ETTELEM=tools/claims-v3/e128/ettelem_guard.sh                                                  # E142 change 5
drain_mgmt() { log "E157: drain refused: dev_mngt_service is not in E157's classified command list"; return 0; }   # E142 change 5
# Departure D1 (hl/README.md, kept by E60-E156): on aifoundry1 and aifoundry3 a user who is only logged in does not block (other
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
[ "$CARD" = aifoundry1-c1 ] || { echo "E157 runs on aifoundry1 card 1 only (V3_DEVICE=1; this is $CARD)" >&2; exit 2; }   # E142 change 4
others_present && exit 3
[ -n "${V3_DEVICE:-}" ] && export V3_DEVICE

PASS=${1:?usage: block_e157.sh <pass> [--smoke|--stoptest]}
MODE=; case "${2:-}" in --smoke) MODE=smoke ;; --stoptest) MODE=stoptest ;; '') ;; *) echo "unknown option ${2}" >&2; exit 2 ;; esac
case "$PASS" in ''|*[!0-9]*) echo "pass must be a number" >&2; exit 2 ;; esac
HERE=tools/claims-v3/kinds
E=tools/claims-v3/e157
CC=tools/claims-v3/ccheck/sparsity_ccheck.sh                                                                                  # E157 change 2
CCHOST=build/ccheck/b/host/sparsity_host
CCELF=build/sparsity/kernel/sparsity.elf
TARGET=${E78_TARGET:-58}; PREHEAT=${E78_PREHEAT:-59}; BURNIN=${E78_BURNIN:-2}; MAXC=${E78_MAX_C:-72}                       # E142 change 4
QUIET=${E78_QUIET:-2.0}; TIERS=${E78_TIERS:-1,2}; FMA_S=4; EXPN=${E78_EXPN:-e157}
ITEMS_ARG=()
if [ -n "$MODE" ]; then
  PREHEAT=0; TARGET=200; QUIET=0.2; FMA_S=2; BURNIN=0; EXPN=${E78_EXPN:-e157}-$MODE                                       # E142 change 3
  ITEMS_ARG=(--items "$(python3 -c 'import sys; sys.path.insert(0, sys.argv[1]); import e157_common as e; print(",".join(e.SMOKE_ITEMS))' "$E")")
else
  case "$PASS" in 1571[0-9]) ;; *) echo "pass $PASS is no E157 pass (15710-15719)" >&2; exit 2 ;; esac                    # E157 change 1
fi
log "E157 pass $PASS${MODE:+ ($MODE)}: target $TARGET preheat $PREHEAT quiet $QUIET burnin $BURNIN fma $FMA_S s, die cap $MAXC C; C log via $CC"

# ---- preflight: files only, no device ------------------------------------------------------------------------
pf=()
[ -f "$HERE/kinds.json" ] || pf+=("no $HERE/kinds.json")
for f in blind6/blind6.json blind6/SHA256SUMS blind6/MANIFEST blind6/predictions-blind6-aifoundry1c1.json blind5/blind5.json blind5/SHA256SUMS; do
  [ -f "$HERE/$f" ] || pf+=("no $HERE/$f")
done
[ -f "$E/predictions-e157.json" ] || pf+=("no $E/predictions-e157.json")
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
# E157 change 1: run_e157.py (run_e78.py unchanged, E157's items and order, the live stops) in the preflight and the pass
LIST=$(python3 "$E/run_e157.py" /dev/null --root "$V3_ROOT" --first-block "$PASS" --tiers "$TIERS" --card "$CARD" \
       --fma-s "$FMA_S" --burnin "$BURNIN" ${ITEMS_ARG[@]+"${ITEMS_ARG[@]}"} --list 2>"$V3_ROOT/build/e157-list.err") ||
  pf+=("run_e157 --list (tiles against their sha256): $(tail -c 300 "$V3_ROOT/build/e157-list.err") ${LIST:0:300}")
MAXS=$(python3 -c 'import json,sys; print(json.loads(sys.argv[1])["max_s"])' "$LIST" 2>/dev/null)
case "$MAXS" in ''|*[!0-9]*) pf+=("bad run_e157 --list output: ${LIST:0:200}") ;; esac
if [ ${#pf[@]} -gt 0 ]; then printf 'preflight: %s\n' "${pf[@]}" >&2; exit 2; fi

D=$DATA_ROOT/$EXPN/p$PASS
if [ -e "$D/block.json" ] && ! grep -q '"status":"ok"' "$D/block.json"; then mv "$D" "$D.attempt-$(date +%s)"; fi
if [ -d "$D" ] && [ ! -e "$D/block.json" ]; then mv "$D" "$D.attempt-$(date +%s)"; fi
block_begin "$EXPN" "$PASS"
others_present && { block_end others "another user before the first launch"; exit 3; }
[ -n "${V3_DRY:-}" ] || et-lab-manifest > "$OUT/manifest.txt" 2>/dev/null || true      # sysfs and files only; it never opens /dev/et*
( sha256sum $HERE/kinds.json $HERE/blind6/blind6.json $HERE/blind6/MANIFEST $HERE/blind6/SHA256SUMS $HERE/blind6/tiles/*/*.bin \
    $HERE/blind5/blind5.json $HERE/blind5/SHA256SUMS $HERE/blind5/tiles/fp32/fp32.b_exp_busy_a_const.bin \
    $HERE/blind5/tiles/fp32/fp32.real_pythia_ln1_q.bin $HERE/blind5/tiles/fp16/fp16.sparse24_aligned.bin \
    $HERE/blind5/tiles/fp16/fp16.exp_only.bin $HERE/blind5/tiles/int8/int8.gray_a.bin \
    $HERE/blind5/tiles/int8/int8.b_line_zero_one.bin ) > "$OUT/gen.sha256" 2>/dev/null || true                              # E157 change 3
sha256sum "$E"/* > "$OUT/e157-code.sha256" 2>/dev/null || true
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
  python3 "$E/run_e157.py" "$OUT" --root "$V3_ROOT" --tel-live "$OUT/telemetry.jsonl.raw" \
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
    export E157_STOPTEST=$k
    run_pass
    st+=("$k:rc=$rc")
    log "E157 stop-path test ($k): run_e157 exit $rc"
    unset E157_STOPTEST
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
  *) block_end failed "run_e157 exit $rc${MODE:+ ($MODE)}"; exit 1 ;;
esac
