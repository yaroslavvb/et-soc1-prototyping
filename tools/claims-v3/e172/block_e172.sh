#!/usr/bin/env bash
# E172 (Q142(k6), tools/claims-v3/e172/E172.md): pool 8 in E164's form on aifoundry1 card 1: one pass of blind pool 8, the smoke or the stop-path test, every launch's C logged, as a lib.sh block. A port of
# tools/claims-v3/e164/block_e164.sh (E164, blind pool 7 on this card), whose card-1 changes (E142's: the live stops and the in-run watcher,
# E78's protocol, the smoke and the stop-path test, card 1 only with run_e78's --max-c 72, every telemetry call through E128's guard and
# drain_mgmt refused, gen.sha256 and binaries.sha256) and C log (E157 change 2) it keeps; its own changes are marked E172:
#   1. it runs tools/claims-v3/e172/run_e172.py (run_e78.py unchanged, E172's items and order, E142's stops and watcher); every tile is
#      checked against its registered sha256 first; passes 17210-17219 (84 runs: E78's six anchors three times, the tie twice, pool 8's
#      64 tiles once; 75 with E172_DROP_P2=1), the smoke 17201, the stop-path test 17202;
#   2. the files the preflight requires are pool 8's frozen files, plan-e172.json and harness-e172.json;
#   3. gen.sha256 covers pool 8's tiles and manifest files; e172-code.sha256 also names the watcher that ran (run_e172.py's) and the
#      pinned watcher_q142s.py with its two amendments (E172.md, "The watcher"); E172_DROP_P2 is logged with the pass and reaches the
#      runner through the environment.
# Everything else - the config reads under timeout 10 at both ends, the card lock, hold10/timeout 10 on every device process, the
# other-user test (D1: an idle login does not block on aifoundry1; another user on this card or any other user's device process does),
# the sampler (no --reset-ms), the STOP file, the C log through Q139(k)'s wrapper - is block_e164.sh's, lib.sh's and hl/block.sh's,
# unchanged. Nothing is set: no governor, TDP, threshold or clock set, no reset, no --reset-ms. Device commands: E172.md, "Device
# commands sent".
#
#   V3_DEVICE=1 bash tools/claims-v3/e172/block_e172.sh <pass> [--smoke|--stoptest]
#   V3_DEVICE=1 V3_DRY=1 bash tools/claims-v3/e172/block_e172.sh <pass>          # print every device call, touch nothing
. "$(dirname "${BASH_SOURCE[0]}")/../lib.sh"
ETTELEM=tools/claims-v3/e128/ettelem_guard.sh                                                  # E142 change 5
drain_mgmt() { log "E172: drain refused: dev_mngt_service is not in E172's classified command list"; return 0; }   # E142 change 5
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
[ "$CARD" = aifoundry1-c1 ] || { echo "E172 runs on aifoundry1 card 1 only (V3_DEVICE=1; this is $CARD)" >&2; exit 2; }   # E142 change 4
others_present && exit 3
[ -n "${V3_DEVICE:-}" ] && export V3_DEVICE

PASS=${1:?usage: block_e172.sh <pass> [--smoke|--stoptest]}
MODE=; case "${2:-}" in --smoke) MODE=smoke ;; --stoptest) MODE=stoptest ;; '') ;; *) echo "unknown option ${2}" >&2; exit 2 ;; esac
case "$PASS" in ''|*[!0-9]*) echo "pass must be a number" >&2; exit 2 ;; esac
HERE=tools/claims-v3/kinds
E=tools/claims-v3/e172
CC=tools/claims-v3/ccheck/sparsity_ccheck.sh                                                                                  # E157 change 2
CCHOST=build/ccheck/b/host/sparsity_host
CCELF=build/sparsity/kernel/sparsity.elf
TARGET=${E78_TARGET:-58}; PREHEAT=${E78_PREHEAT:-59}; BURNIN=${E78_BURNIN:-2}; MAXC=${E78_MAX_C:-72}                       # E142 change 4
QUIET=${E78_QUIET:-2.0}; TIERS=${E78_TIERS:-1,2}; FMA_S=4; EXPN=${E78_EXPN:-e172}
ITEMS_ARG=()
if [ -n "$MODE" ]; then
  PREHEAT=0; TARGET=200; QUIET=0.2; FMA_S=2; BURNIN=0; EXPN=${E78_EXPN:-e172}-$MODE                                       # E142 change 3
  ITEMS_ARG=(--items "$(python3 -B -c 'import sys; sys.path.insert(0, sys.argv[1]); import e172_common as e; print(",".join(e.SMOKE_ITEMS))' "$E")")
else
  case "$PASS" in 1721[0-9]) ;; *) echo "pass $PASS is no E172 pass (17210-17219)" >&2; exit 2 ;; esac                    # E172 change 1
fi
log "E172 pass $PASS${MODE:+ ($MODE)}: target $TARGET preheat $PREHEAT quiet $QUIET burnin $BURNIN fma $FMA_S s, die cap $MAXC C; C log via $CC; E172_DROP_P2=${E172_DROP_P2:-0}"

# ---- preflight: files only, no device ------------------------------------------------------------------------
pf=()
[ -f "$HERE/kinds.json" ] || pf+=("no $HERE/kinds.json")
for f in blind8/blind8.json blind8/SHA256SUMS blind8/MANIFEST blind8/predictions-pool8-aifoundry1c1.json blind8/intervals-pool8.json; do
  [ -f "$HERE/$f" ] || pf+=("no $HERE/$f")
done
for f in plan-e172.json harness-e172.json; do [ -f "$E/$f" ] || pf+=("no $E/$f"); done                                # E172 change 2
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
# E172 change 1: run_e172.py (run_e78.py unchanged, E172's items and order, the live stops) in the preflight and the pass
LIST=$(python3 -B "$E/run_e172.py" /dev/null --root "$V3_ROOT" --first-block "$PASS" --tiers "$TIERS" --card "$CARD" \
       --fma-s "$FMA_S" --burnin "$BURNIN" ${ITEMS_ARG[@]+"${ITEMS_ARG[@]}"} --list 2>"$V3_ROOT/build/e172-list.err") ||
  pf+=("run_e172 --list (tiles against their sha256): $(tail -c 300 "$V3_ROOT/build/e172-list.err") ${LIST:0:300}")
MAXS=$(python3 -B -c 'import json,sys; print(json.loads(sys.argv[1])["max_s"])' "$LIST" 2>/dev/null)
case "$MAXS" in ''|*[!0-9]*) pf+=("bad run_e172 --list output: ${LIST:0:200}") ;; esac
if [ ${#pf[@]} -gt 0 ]; then printf 'preflight: %s\n' "${pf[@]}" >&2; exit 2; fi

D=$DATA_ROOT/$EXPN/p$PASS
if [ -e "$D/block.json" ] && ! grep -q '"status":"ok"' "$D/block.json"; then mv "$D" "$D.attempt-$(date +%s)"; fi
if [ -d "$D" ] && [ ! -e "$D/block.json" ]; then mv "$D" "$D.attempt-$(date +%s)"; fi
block_begin "$EXPN" "$PASS"
others_present && { block_end others "another user before the first launch"; exit 3; }
[ -n "${V3_DRY:-}" ] || et-lab-manifest > "$OUT/manifest.txt" 2>/dev/null || true      # sysfs and files only; it never opens /dev/et*
( sha256sum $HERE/kinds.json $HERE/blind8/blind8.json $HERE/blind8/MANIFEST $HERE/blind8/SHA256SUMS $HERE/blind8/tiles/*/*.bin \
    $HERE/blind8/predictions-pool8-aifoundry1c1.json $HERE/blind8/intervals-pool8.json ) > "$OUT/gen.sha256" 2>/dev/null || true   # E172 change 3
sha256sum "$E"/*.py "$E"/*.sh "$E"/*.json "$E"/E172.md tools/claims-v3/hpl/watcher_q142s.py tools/claims-v3/hpl/run_hpl.py.dated-note.md \
  tools/claims-v3/hpl/run_hpl.py.dated-note-2.md > "$OUT/e172-code.sha256" 2>/dev/null || true
echo "watcher: the kinds watcher of $E/run_e172.py (sha256 $(sha256sum "$E/run_e172.py" 2>/dev/null | cut -c1-64)); watcher_q142s.py pinned, not imported (no run_hpl module)" >> "$OUT/e172-code.sha256"
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
  python3 -B "$E/run_e172.py" "$OUT" --root "$V3_ROOT" --tel-live "$OUT/telemetry.jsonl.raw" \
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
    export E172_STOPTEST=$k
    run_pass
    st+=("$k:rc=$rc")
    log "E172 stop-path test ($k): run_e172 exit $rc"
    unset E172_STOPTEST
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
  *) block_end failed "run_e172 exit $rc${MODE:+ ($MODE)}"; exit 1 ;;
esac
