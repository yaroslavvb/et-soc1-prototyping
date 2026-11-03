#!/usr/bin/env bash
# E148 (Q138, tools/claims-v3/e148/README.md): one pass of E148's arms on aifoundry1 card 1, as a lib.sh block. A port of
# tools/claims-v3/e129/block_e129.sh (E129, this card, this morning) with tools/claims-v3/e142/block_e142.sh's live stops and stop-path test
# (E142, this card, 20:50-21:36 PST today), each change marked E148:
#   1. it runs tools/claims-v3/e148/run_e148.py (tools/claims-v3/kinds/run_e78.py unchanged, with E148's items and order installed, E142's live
#      stops and in-run watcher: board_w >= 66 W or a minion-shire field >= 72 C in the newest line of the running sampler's file writes STOP and
#      ends the pass): each format's zeros three times a pass, the built-in pi tie first and last, E148's six arms once; every tile checked
#      against its registered sha256 first;
#   2. --smoke runs e148_common.SMOKE_ITEMS (2 s each, no preheat) under e148-smoke/; --stoptest (E142's change 3) runs no launch at all: the
#      sampler starts, then run_e148.py three times with E148_STOPTEST=die, =board and =watch, each of which must end with EXIT_HOT (6) and a
#      STOP line read from a live sample, under e148-stoptest/;
#   3. gen.sha256 covers kinds.json and its fp32 and int8 zeros tiles (E148 uses no other tile);
#   4. card 1 only (CARD aifoundry1-c1, V3_DEVICE=1, the lock etsoc-shire1.lock); run_e78.py's own die cap --max-c 72 (E131's, E137's, E142's
#      and E145's on this card; E129's was 78);
#   5. $SPARSITY is build/e109/host/sparsity_host: E109's sp109 as E124 built it on aifoundry1 and E129 ran it (its sha256 checked by
#      check_e148.py); $HEATER stays lib.sh's, E78's heater;
#   6. CARE WITH DEVICE COMMANDS (the owner's rule of Mon 2 Nov 2026), E128's change 5 unchanged: every telemetry call goes through
#      tools/claims-v3/e128/ettelem_guard.sh, the allow-list that passes only `ettelem config` and `ettelem sample --seconds --every-ms` (the
#      classified READs of README.md) and refuses anything else before the device opens; and lib.sh's drain_mgmt is replaced by a refusal, so the
#      vendor tool dev_mngt_service is never run: a sampler that will not start fails the block instead.
# Everything else - timeout 10 on the config reads, the card lock, hold10/timeout 10 on every device process, the other-user test (D1: an idle
# login does not block on aifoundry1; another user on this card or any other user's device process does), the launch protocol, the sampler (no
# --reset-ms), the STOP file - is block_e129.sh's, block_e142.sh's, lib.sh's and hl/block.sh's, unchanged. Nothing is set: no governor, TDP,
# threshold or clock set, no reset, no --reset-ms.
#
#   V3_DEVICE=1 bash tools/claims-v3/e148/block_e148.sh <pass> [--smoke|--stoptest]
#   V3_DEVICE=1 V3_DRY=1 bash tools/claims-v3/e148/block_e148.sh <pass>          # print every device call, touch nothing
. "$(dirname "${BASH_SOURCE[0]}")/../lib.sh"
ETTELEM=tools/claims-v3/e128/ettelem_guard.sh                                                                     # E148 change 6
drain_mgmt() { log "E148: drain refused: dev_mngt_service is not in E148's classified command list"; return 0; }   # E148 change 6
SPARSITY=${E148_SPARSITY:-build/e109/host/sparsity_host}   # E148 change 5
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
[ "$CARD" = aifoundry1-c1 ] || { echo "E148 runs on aifoundry1 card 1 only (V3_DEVICE=1; this is $CARD)" >&2; exit 2; }   # E148 change 4
others_present && exit 3
[ -n "${V3_DEVICE:-}" ] && export V3_DEVICE

PASS=${1:?usage: block_e148.sh <pass> [--smoke|--stoptest]}
MODE=; case "${2:-}" in --smoke) MODE=smoke ;; --stoptest) MODE=stoptest ;; '') ;; *) echo "unknown option ${2}" >&2; exit 2 ;; esac
case "$PASS" in ''|*[!0-9]*) echo "pass must be a number" >&2; exit 2 ;; esac
[ -n "$MODE" ] || case "$PASS" in 1481[0-9]) ;; *) echo "pass $PASS is no E148 pass (14810-14819)" >&2; exit 2 ;; esac
SMOKE=; [ -n "$MODE" ] && SMOKE=1
HERE=tools/claims-v3/e148
KIN=tools/claims-v3/kinds
TARGET=${E78_TARGET:-58}; PREHEAT=${E78_PREHEAT:-59}; BURNIN=${E78_BURNIN:-2}; MAXC=${E78_MAX_C:-72}                       # E148 change 4
QUIET=${E78_QUIET:-2.0}; TIERS=${E78_TIERS:-1,2}; FMA_S=4; EXPN=${E148_EXPN:-e148}   # E148 change 4
ITEMS_ARG=()
if [ -n "$SMOKE" ]; then
  PREHEAT=0; TARGET=200; FMA_S=2; BURNIN=0; EXPN=${E148_EXPN:-e148}-$MODE                                               # E148 change 2
  ITEMS_ARG=(--items "$(python3 -c 'import sys; sys.path.insert(0, sys.argv[1]); import e148_common as e; print(",".join(e.SMOKE_ITEMS))' "$HERE")")   # E148 change 2
fi

# ---- preflight: files only, no device ------------------------------------------------------------------------
pf=()
[ -f "$KIN/kinds.json" ] || pf+=("no $KIN/kinds.json")
[ -f "$HERE/predictions-e148.json" ] || pf+=("no $HERE/predictions-e148.json")
[ -x "$SPARSITY" ] || pf+=("missing $SPARSITY")
[ -x "$HEATER" ] || pf+=("missing heater $HEATER")
[ -x "$ETTELEM" ] || pf+=("missing $ETTELEM")
[ -x build/ettelem/ettelem ] || pf+=("missing build/ettelem/ettelem")
if [ -x "$SPARSITY" ]; then
  for s in 'file:' int8 '--dump-tiles' 'E109: shape= needs a' 'E109: rows and cols must be 1-16'; do     # sp109's shape grammar
    grep -a -q -- "$s" "$SPARSITY" || pf+=("$SPARSITY has no $s")
  done
fi
for b in "$SPARSITY" "$HEATER"; do [ -x "$b" ] && { grep -a -q -- '--stop-file' "$b" || pf+=("$b has no --stop-file"); }; done
LK=/run/lock/etsoc-shire${V3_DEVICE:-0}.lock
[ -n "${V3_DRY:-}" ] || [ -e "$LK" ] || pf+=("no card lock $LK")
mkdir -p "$V3_ROOT/build"
LIST=$(python3 "$HERE/run_e148.py" /dev/null --root "$V3_ROOT" --first-block "$PASS" --tiers "$TIERS" --card "$CARD" \
       --fma-s "$FMA_S" --burnin "$BURNIN" ${ITEMS_ARG[@]+"${ITEMS_ARG[@]}"} --list 2>"$V3_ROOT/build/e148-list.err") ||
  pf+=("run_e148 --list (harness and tiles against their sha256): $(tail -c 300 "$V3_ROOT/build/e148-list.err") ${LIST:0:300}")
MAXS=$(python3 -c 'import json,sys; print(json.loads(sys.argv[1])["max_s"])' "$LIST" 2>/dev/null)
case "$MAXS" in ''|*[!0-9]*) pf+=("bad run_e148 --list output: ${LIST:0:200}") ;; esac
if [ ${#pf[@]} -gt 0 ]; then printf 'preflight: %s\n' "${pf[@]}" >&2; exit 2; fi

D=$DATA_ROOT/$EXPN/p$PASS
if [ -e "$D/block.json" ] && ! grep -q '"status":"ok"' "$D/block.json"; then mv "$D" "$D.attempt-$(date +%s)"; fi
if [ -d "$D" ] && [ ! -e "$D/block.json" ]; then mv "$D" "$D.attempt-$(date +%s)"; fi
block_begin "$EXPN" "$PASS"
others_present && { block_end others "another user before the first launch"; exit 3; }
[ -n "${V3_DRY:-}" ] || et-lab-manifest > "$OUT/manifest.txt" 2>/dev/null || true
( cd "$KIN" && sha256sum kinds.json tiles/fp32/zeros.bin tiles/int8/zeros.bin ) > "$OUT/gen.sha256" 2>/dev/null || true   # E148 change 3
sha256sum "$SPARSITY" build/e109/kernel/sparsity.elf "$HEATER" build/ettelem/ettelem "$ETTELEM" > "$OUT/binaries.sha256" 2>/dev/null || true
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
  python3 "$HERE/run_e148.py" "$OUT" --root "$V3_ROOT" --tel-live "$OUT/telemetry.jsonl.raw" \
    --heater "$HEATER" --sparsity "$SPARSITY" --first-block "$PASS" --seed "$PASS" --tiers "$TIERS" \
    --target "$TARGET" --preheat "$PREHEAT" --quiet-s "$QUIET" --max-c "$MAXC" --fma-s "$FMA_S" --burnin "$BURNIN" \
    --card "$CARD" --shires "${E78_SHIRES:-0xffffffff}" --per-shire "${E78_PER_SHIRE:-32}" ${ITEMS_ARG[@]+"${ITEMS_ARG[@]}"} &
  RUNNER=$!
  wait "$RUNNER"; rc=$?
  RUNNER=
}
if [ "$MODE" = stoptest ]; then                                                                                               # E148 change 2
  st=()
  for k in die board watch; do
    export E148_STOPTEST=$k
    run_pass
    st+=("$k:rc=$rc")
    log "E148 stop-path test ($k): run_e148 exit $rc"
    unset E148_STOPTEST
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
  0) block_end ok "tiers $TIERS${MODE:+ $MODE}" ;;
  3) block_end others "another user on the card"; exit 3 ;;
  *) block_end failed "run_e148 exit $rc${MODE:+ ($MODE)}"; exit 1 ;;
esac
