#!/usr/bin/env bash
# E145 (Q138, tools/claims-v3/e145/README.md): one block of E138's int8 B single-bit trains, or of E130's A trains (the control), on
# aifoundry1 card 1, as a lib.sh block. A port of tools/claims-v3/e138/block_e138.sh (aifoundry3) with tools/claims-v3/e137/block_e137.sh's
# card-1 changes, each marked E145:
#   1. it runs tools/claims-v3/e145/run_e145.py (run_e78.py unchanged, with E145's items and orders installed, and E137's live stops:
#      board_w >= 60 W or a minion-shire reading >= 72 C in the newest line of the running sampler's file writes STOP and ends the
#      pass); every tile is checked against its registered sha256 first;
#   2. the pass number sets the block, and both are TRAINS (E102's int8 block I: --preheat 0 --target 200 --quiet-s 0.2 --burnin 0):
#      B (14510-14529) E138's B list, A (14530-14539) E130's A list (e145_common.py);
#   3. --smoke runs e145_common.SMOKE_ITEMS (E138's eight), 2 s each, under kinds-smoke/; --stoptest runs no launch at all: the
#      sampler starts, then run_e145.py twice with E145_STOPTEST=die and =board, each of which must end on its first live reading
#      with EXIT_HOT (6) and a STOP line (README.md, "Stops"), under kinds-stoptest/;
#   4. card 1 only (CARD aifoundry1-c1, V3_DEVICE=1, the lock etsoc-shire1.lock); run_e78.py's own die cap --max-c 72 (E137's);
#   5. CARE WITH DEVICE COMMANDS (the owner's rule of Mon 2 Nov 2026), E137's change 5 unchanged: every telemetry call goes through
#      tools/claims-v3/e128/ettelem_guard.sh (`ettelem config` and `ettelem sample --seconds --every-ms` only), and lib.sh's drain_mgmt
#      is replaced by a refusal, so the vendor tool dev_mngt_service is never run;
#   6. gen.sha256 covers Q136(a)'s tiles and e130-items.json; binaries.sha256 records the binaries the block executes.
# Everything else - the config reads under timeout 10 at both ends, the card lock, hold10/timeout 10 on every device process, the
# other-user test (D1: an idle login does not block on aifoundry1; another user on this card or any other user's device process does),
# the sampler (no --reset-ms), the STOP file - is block_e138.sh's, block_e137.sh's, lib.sh's and hl/block.sh's, unchanged. Nothing is
# set: no governor, TDP, threshold or clock set, no reset, no --reset-ms. Device commands: README.md, "Device commands sent".
#
#   V3_DEVICE=1 bash tools/claims-v3/e145/block_e145.sh <pass> [--smoke|--stoptest]
#   V3_DEVICE=1 V3_DRY=1 bash tools/claims-v3/e145/block_e145.sh <pass>          # print every device call, touch nothing
. "$(dirname "${BASH_SOURCE[0]}")/../lib.sh"
ETTELEM=tools/claims-v3/e128/ettelem_guard.sh                                                  # E145 change 5
drain_mgmt() { log "E145: drain refused: dev_mngt_service is not in E145's classified command list"; return 0; }   # E145 change 5
# Departure D1 (hl/README.md, kept by E60-E138): on aifoundry1 and aifoundry3 a user who is only logged in does not block (other
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
[ "$CARD" = aifoundry1-c1 ] || { echo "E145 runs on aifoundry1 card 1 only (V3_DEVICE=1; this is $CARD)" >&2; exit 2; }   # E145 change 4
others_present && exit 3
[ -n "${V3_DEVICE:-}" ] && export V3_DEVICE

PASS=${1:?usage: block_e145.sh <pass> [--smoke|--stoptest]}
MODE=; case "${2:-}" in --smoke) MODE=smoke ;; --stoptest) MODE=stoptest ;; '') ;; *) echo "unknown option ${2}" >&2; exit 2 ;; esac
case "$PASS" in ''|*[!0-9]*) echo "pass must be a number" >&2; exit 2 ;; esac
HERE=tools/claims-v3/kinds
E=tools/claims-v3/e145
TARGET=${E78_TARGET:-58}; PREHEAT=${E78_PREHEAT:-59}; BURNIN=${E78_BURNIN:-2}; MAXC=${E78_MAX_C:-72}                       # E145 change 4
QUIET=${E78_QUIET:-2.0}; TIERS=${E78_TIERS:-1,2}; FMA_S=4; EXPN=${E78_EXPN:-kinds}
ITEMS_ARG=()
case "$PASS" in        # E145 change 2: the pass number says which block; both are trains
  1451[0-9]|1452[0-9]) BLOCK=B; PREHEAT=0; TARGET=200; QUIET=0.2; BURNIN=0 ;;
  1453[0-9]) BLOCK=A; PREHEAT=0; TARGET=200; QUIET=0.2; BURNIN=0 ;;
  *) BLOCK=S ;;
esac
if [ -n "$MODE" ]; then
  PREHEAT=0; TARGET=200; QUIET=0.2; FMA_S=2; BURNIN=0; EXPN=${E78_EXPN:-kinds}-$MODE                                     # E145 change 3
  ITEMS_ARG=(--items "$(python3 -c 'import sys; sys.path.insert(0, sys.argv[1]); import e145_common as e; print(",".join(e.SMOKE_ITEMS))' "$E")")
fi
[ -n "$MODE" ] || [ "$BLOCK" != S ] || { echo "pass $PASS is no E145 block (B 14510-14529, A 14530-14539)" >&2; exit 2; }
log "E145 block $BLOCK${MODE:+ $MODE}, pass $PASS: target $TARGET preheat $PREHEAT quiet $QUIET burnin $BURNIN fma $FMA_S s, die cap $MAXC C"

# ---- preflight: files only, no device ------------------------------------------------------------------------
pf=()
[ -f "$HERE/kinds.json" ] || pf+=("no $HERE/kinds.json")
for f in e130/e130.json e130/sha256.txt; do [ -f "$HERE/$f" ] || pf+=("no $HERE/$f"); done
for f in e130-items.json predictions-e145.json; do [ -f "$E/$f" ] || pf+=("no $E/$f"); done
[ -x "$SPARSITY" ] || pf+=("missing $SPARSITY")
[ -x "$HEATER" ] || pf+=("missing heater $HEATER")
[ -x "$ETTELEM" ] || pf+=("missing $ETTELEM")
[ -x build/ettelem/ettelem ] || pf+=("missing build/ettelem/ettelem")
if [ -x "$SPARSITY" ]; then
  for s in 'file:' int8 '--dump-tiles'; do
    grep -a -q -- "$s" "$SPARSITY" || pf+=("$SPARSITY has no $s")
  done
fi
for b in "$SPARSITY" "$HEATER"; do [ -x "$b" ] && { grep -a -q -- '--stop-file' "$b" || pf+=("$b has no --stop-file"); }; done
LK=/run/lock/etsoc-shire${V3_DEVICE:-0}.lock
[ -n "${V3_DRY:-}" ] || [ -e "$LK" ] || pf+=("no card lock $LK")
mkdir -p "$V3_ROOT/build"
# E145 change 1: run_e145.py (run_e78.py unchanged, E145's items and orders, the live stops) in the preflight and the pass
LIST=$(python3 "$E/run_e145.py" /dev/null --root "$V3_ROOT" --first-block "$PASS" --tiers "$TIERS" --card "$CARD" \
       --fma-s "$FMA_S" --burnin "$BURNIN" ${ITEMS_ARG[@]+"${ITEMS_ARG[@]}"} --list 2>"$V3_ROOT/build/e145-list.err") ||
  pf+=("run_e145 --list (tiles against their sha256): $(tail -c 300 "$V3_ROOT/build/e145-list.err") ${LIST:0:300}")
MAXS=$(python3 -c 'import json,sys; print(json.loads(sys.argv[1])["max_s"])' "$LIST" 2>/dev/null)
case "$MAXS" in ''|*[!0-9]*) pf+=("bad run_e145 --list output: ${LIST:0:200}") ;; esac
if [ ${#pf[@]} -gt 0 ]; then printf 'preflight: %s\n' "${pf[@]}" >&2; exit 2; fi

D=$DATA_ROOT/$EXPN/p$PASS
if [ -e "$D/block.json" ] && ! grep -q '"status":"ok"' "$D/block.json"; then mv "$D" "$D.attempt-$(date +%s)"; fi
if [ -d "$D" ] && [ ! -e "$D/block.json" ]; then mv "$D" "$D.attempt-$(date +%s)"; fi
block_begin "$EXPN" "$PASS"
others_present && { block_end others "another user before the first launch"; exit 3; }
[ -n "${V3_DRY:-}" ] || et-lab-manifest > "$OUT/manifest.txt" 2>/dev/null || true      # sysfs and files only; it never opens /dev/et*
( sha256sum $HERE/kinds.json $HERE/e130/e130.json $HERE/e130/sha256.txt $HERE/e130/tiles/int8/*.bin $E/e130-items.json ) \
    > "$OUT/gen.sha256" 2>/dev/null || true                                                                                  # E145 change 6
sha256sum "$E"/* > "$OUT/e145-code.sha256" 2>/dev/null || true
sha256sum "$SPARSITY" "$HEATER" build/ettelem/ettelem "$ETTELEM" > "$OUT/binaries.sha256" 2>/dev/null || true             # E145 change 6
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
  python3 "$E/run_e145.py" "$OUT" --root "$V3_ROOT" --tel-live "$OUT/telemetry.jsonl.raw" \
    --heater "$HEATER" --sparsity "$SPARSITY" --first-block "$PASS" --seed "$PASS" --tiers "$TIERS" \
    --target "$TARGET" --preheat "$PREHEAT" --quiet-s "$QUIET" --max-c "$MAXC" --fma-s "$FMA_S" --burnin "$BURNIN" \
    --card "$CARD" --shires "${E78_SHIRES:-0xffffffff}" --per-shire "${E78_PER_SHIRE:-32}" ${ITEMS_ARG[@]+"${ITEMS_ARG[@]}"} &
  RUNNER=$!
  wait "$RUNNER"; rc=$?
  RUNNER=
}
if [ "$MODE" = stoptest ]; then                                                                                               # E145 change 3
  st=()
  for k in die board; do
    export E145_STOPTEST=$k
    run_pass
    st+=("$k:rc=$rc")
    log "E145 stop-path test ($k): run_e145 exit $rc"
    unset E145_STOPTEST
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
case $rc in
  0) block_end ok "block $BLOCK${MODE:+ $MODE}" ;;
  3) block_end others "another user on the card"; exit 3 ;;
  *) block_end failed "run_e145 exit $rc${MODE:+ ($MODE)}"; exit 1 ;;
esac
