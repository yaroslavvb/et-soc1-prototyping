#!/usr/bin/env bash
# E153 (Q139, tools/claims-v3/e153/README.md): one pass of blind pool 6 (and the 6 K1 tiles of pool 5) on aifoundry3 card 0, as a lib.sh
# block. A copy of tools/claims-v3/e141/block_e141.sh (E141, blind pool 5 on this card) with these changes, each marked E153:
#   1. it runs tools/claims-v3/e153/run_e153.py (run_e78.py unchanged, with E153's items and order installed, E141's live stops and
#      in-run watcher: board_w >= 65 W or the minion-shire reading minshire[0] >= 70 C in the newest line of the running sampler's file
#      writes STOP and ends the pass); every tile is checked against its registered sha256 first;
#   2. THE C CHECK (Q139(k), tools/claims-v3/ccheck/README.md, "The exact use"): the measured launches run through the wrapper
#      tools/claims-v3/ccheck/sparsity_ccheck.sh (--sparsity), which runs the C-logging host build/ccheck/b/host/sparsity_host with the
#      power passes' own kernel build/sparsity/kernel/sparsity.elf and appends --c-log "$CCHECK_LOG" --c-poison; CCHECK_LOG is the pass's
#      c-log.jsonl. The heater stays on build/sparsity/host/sparsity_host (its C is not a measurement). The check itself runs at the
#      desk on the Intel (ccheck.py check), never here;
#   3. --smoke runs e153_common.SMOKE_ITEMS, 2 s each, no preheat, under e153-smoke/; --stoptest runs no launch at all (E141's);
#   4. aifoundry3 card 0 only (CARD aifoundry3, no V3_DEVICE, the lock etsoc-shire0.lock); run_e78.py's own die cap --max-c 70;
#   5. CARE WITH DEVICE COMMANDS (the owner's rule of Mon 2 Nov 2026), E141's change 5 unchanged: every telemetry call goes through
#      tools/claims-v3/e128/ettelem_guard.sh (`ettelem config` and `ettelem sample --seconds --every-ms` only), and lib.sh's
#      drain_mgmt is replaced by a refusal, so the vendor tool dev_mngt_service is never run;
#   6. gen.sha256 covers blind pool 6's tiles and manifest and the K1 tiles; binaries.sha256 records every binary and the wrapper.
# Everything else - the config reads under timeout 10 at both ends, the card lock, hold10/timeout 10 on every device process, the
# other-user test (D1: an idle login does not block on aifoundry3; another user on this card or any other user's device process does),
# the sampler (no --reset-ms), the STOP file - is block_e141.sh's, lib.sh's and hl/block.sh's, unchanged. Nothing is set: no governor,
# TDP, threshold or clock set, no reset, no --reset-ms. Device commands: README.md, "Device commands sent".
#
#   bash tools/claims-v3/e153/block_e153.sh <pass> [--smoke|--stoptest]
#   V3_DRY=1 bash tools/claims-v3/e153/block_e153.sh <pass>          # print every device call, touch nothing
. "$(dirname "${BASH_SOURCE[0]}")/../lib.sh"
ETTELEM=tools/claims-v3/e128/ettelem_guard.sh                                                  # E153 change 5
drain_mgmt() { log "E153: drain refused: dev_mngt_service is not in E153's classified command list"; return 0; }   # E153 change 5
# Departure D1 (hl/README.md, kept by E60-E152): on aifoundry1 and aifoundry3 a user who is only logged in does not block (other
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
[ "$CARD" = aifoundry3 ] && [ -z "${V3_DEVICE:-}" ] || { echo "E153 runs on aifoundry3 card 0 only (no V3_DEVICE; this is $CARD)" >&2; exit 2; }   # E153 change 4
others_present && exit 3
[ -n "${V3_DEVICE:-}" ] && export V3_DEVICE

PASS=${1:?usage: block_e153.sh <pass> [--smoke|--stoptest]}
MODE=; case "${2:-}" in --smoke) MODE=smoke ;; --stoptest) MODE=stoptest ;; '') ;; *) echo "unknown option ${2}" >&2; exit 2 ;; esac
case "$PASS" in ''|*[!0-9]*) echo "pass must be a number" >&2; exit 2 ;; esac
HERE=tools/claims-v3/kinds
E=tools/claims-v3/e153
CC=tools/claims-v3/ccheck                                                                   # E153 change 2
MEAS=$CC/sparsity_ccheck.sh; CCHOST=build/ccheck/b/host/sparsity_host; KERNEL=build/sparsity/kernel/sparsity.elf
TARGET=${E78_TARGET:-58}; PREHEAT=${E78_PREHEAT:-59}; BURNIN=${E78_BURNIN:-2}; MAXC=${E78_MAX_C:-70}                       # E153 change 4
QUIET=${E78_QUIET:-2.0}; TIERS=${E78_TIERS:-1,2}; FMA_S=4; EXPN=${E78_EXPN:-e153}
ITEMS_ARG=()
if [ -n "$MODE" ]; then
  PREHEAT=0; TARGET=200; QUIET=0.2; FMA_S=2; BURNIN=0; EXPN=${E78_EXPN:-e153}-$MODE                                       # E153 change 3
  ITEMS_ARG=(--items "$(python3 -c 'import sys; sys.path.insert(0, sys.argv[1]); import e153_common as e; print(",".join(e.SMOKE_ITEMS))' "$E")")
else
  case "$PASS" in 1531[0-9]) ;; *) echo "pass $PASS is no E153 pass (15310-15319)" >&2; exit 2 ;; esac
fi
log "E153 pass $PASS${MODE:+ ($MODE)}: target $TARGET preheat $PREHEAT quiet $QUIET burnin $BURNIN fma $FMA_S s, die cap $MAXC C"

# ---- preflight: files only, no device ------------------------------------------------------------------------
pf=()
[ -f "$HERE/kinds.json" ] || pf+=("no $HERE/kinds.json")
for f in blind6/blind6.json blind6/MANIFEST blind6/SHA256SUMS blind6/predictions-blind6-aifoundry3.json blind5/blind5.json blind5/SHA256SUMS; do
  [ -f "$HERE/$f" ] || pf+=("no $HERE/$f"); done
[ -f "$E/predictions-e153.json" ] || pf+=("no $E/predictions-e153.json")
[ -x "$SPARSITY" ] || pf+=("missing $SPARSITY")
[ -x "$HEATER" ] || pf+=("missing heater $HEATER")
[ -x "$ETTELEM" ] || pf+=("missing $ETTELEM")
[ -x build/ettelem/ettelem ] || pf+=("missing build/ettelem/ettelem")
[ -x "$MEAS" ] || pf+=("missing the C-check wrapper $MEAS")                                      # E153 change 2
[ -x "$CCHOST" ] || pf+=("missing the C-logging host $CCHOST (tools/claims-v3/ccheck/build_host_ccheck.sh)")
[ -f "$KERNEL" ] || pf+=("missing the kernel $KERNEL")
for b in "$SPARSITY" "$CCHOST"; do
  [ -x "$b" ] || continue
  for s in 'file:' int8 fp16 '--dump-tiles'; do
    grep -a -q -- "$s" "$b" || pf+=("$b has no $s")
  done
done
if [ -x "$CCHOST" ]; then for s in '--c-log' '--c-poison'; do grep -a -q -- "$s" "$CCHOST" || pf+=("$CCHOST has no $s"); done; fi   # E153 change 2
for b in "$SPARSITY" "$HEATER" "$CCHOST"; do [ -x "$b" ] && { grep -a -q -- '--stop-file' "$b" || pf+=("$b has no --stop-file"); }; done
LK=/run/lock/etsoc-shire${V3_DEVICE:-0}.lock
[ -n "${V3_DRY:-}" ] || [ -e "$LK" ] || pf+=("no card lock $LK")
mkdir -p "$V3_ROOT/build"
# E153 change 1: run_e153.py (run_e78.py unchanged, E153's items and order, the live stops) in the preflight and the pass
LIST=$(python3 "$E/run_e153.py" /dev/null --root "$V3_ROOT" --first-block "$PASS" --tiers "$TIERS" --card "$CARD" \
       --fma-s "$FMA_S" --burnin "$BURNIN" ${ITEMS_ARG[@]+"${ITEMS_ARG[@]}"} --list 2>"$V3_ROOT/build/e153-list.err") ||
  pf+=("run_e153 --list (tiles against their sha256): $(tail -c 300 "$V3_ROOT/build/e153-list.err") ${LIST:0:300}")
MAXS=$(python3 -c 'import json,sys; print(json.loads(sys.argv[1])["max_s"])' "$LIST" 2>/dev/null)
case "$MAXS" in ''|*[!0-9]*) pf+=("bad run_e153 --list output: ${LIST:0:200}") ;; esac
if [ ${#pf[@]} -gt 0 ]; then printf 'preflight: %s\n' "${pf[@]}" >&2; exit 2; fi

D=$DATA_ROOT/$EXPN/p$PASS
if [ -e "$D/block.json" ] && ! grep -q '"status":"ok"' "$D/block.json"; then mv "$D" "$D.attempt-$(date +%s)"; fi
if [ -d "$D" ] && [ ! -e "$D/block.json" ]; then mv "$D" "$D.attempt-$(date +%s)"; fi
block_begin "$EXPN" "$PASS"
others_present && { block_end others "another user before the first launch"; exit 3; }
[ -n "${V3_DRY:-}" ] || et-lab-manifest > "$OUT/manifest.txt" 2>/dev/null || true      # sysfs and files only; it never opens /dev/et*
( sha256sum $HERE/kinds.json $HERE/blind6/blind6.json $HERE/blind6/MANIFEST $HERE/blind6/SHA256SUMS $HERE/blind6/tiles/*/*.bin \
    $HERE/blind5/blind5.json $HERE/blind5/SHA256SUMS $HERE/blind5/tiles/*/*.bin ) > "$OUT/gen.sha256" 2>/dev/null || true     # E153 change 6
sha256sum "$E"/* "$CC"/*.sh "$CC"/*.py > "$OUT/e153-code.sha256" 2>/dev/null || true
sha256sum "$SPARSITY" "$HEATER" "$CCHOST" "$MEAS" "$KERNEL" build/ettelem/ettelem "$ETTELEM" > "$OUT/binaries.sha256" 2>/dev/null || true   # E153 change 6
export CCHECK_LOG="$OUT/c-log.jsonl"                                                                                          # E153 change 2
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
run_pass() {
  python3 "$E/run_e153.py" "$OUT" --root "$V3_ROOT" --tel-live "$OUT/telemetry.jsonl.raw" \
    --heater "$HEATER" --sparsity "$MEAS" --first-block "$PASS" --seed "$PASS" --tiers "$TIERS" \
    --target "$TARGET" --preheat "$PREHEAT" --quiet-s "$QUIET" --max-c "$MAXC" --fma-s "$FMA_S" --burnin "$BURNIN" \
    --card "$CARD" --shires "${E78_SHIRES:-0xffffffff}" --per-shire "${E78_PER_SHIRE:-32}" ${ITEMS_ARG[@]+"${ITEMS_ARG[@]}"} &
  RUNNER=$!
  wait "$RUNNER"; rc=$?
  RUNNER=
}
if [ "$MODE" = stoptest ]; then                                                                                               # E153 change 3
  st=()
  for k in die board watch; do
    export E153_STOPTEST=$k
    run_pass
    st+=("$k:rc=$rc")
    log "E153 stop-path test ($k): run_e153 exit $rc"
    unset E153_STOPTEST
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
# E153 change 2: c-log.jsonl stays as written (ccheck.py reads it as text at the desk; collect_e153.sh gzips the committed copy)
case $rc in
  0) block_end ok "pass $PASS${MODE:+ $MODE}" ;;
  3) block_end others "another user on the card"; exit 3 ;;
  *) block_end failed "run_e153 exit $rc${MODE:+ ($MODE)}"; exit 1 ;;
esac
