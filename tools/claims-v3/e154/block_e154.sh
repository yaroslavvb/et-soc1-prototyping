#!/usr/bin/env bash
# E154 (Q139, tools/claims-v3/e154/README.md): one pass on aifoundry3 card 0, as a lib.sh block. A port of tools/claims-v3/e144/block_e144.sh
# (E144, itself tools/claims-v3/e97/block_e97.sh ported) with these changes, each marked E154 below:
#   1. the runner is tools/claims-v3/e154/run_e154.py (Q139(e)'s frozen holds from the bits, E144's stops; it imports E97's run_e97b.py
#      unchanged); --smoke runs its smoke plan and then the stop-path tests (run_e154.py --smoke --stoptest), data in $DATA_ROOT/e154-smoke/p<pass>/;
#      the measured pass goes to $DATA_ROOT/e154/p<pass>/ with --design $E154_DESIGN and --deadline-epoch $E154_DEADLINE_EPOCH;
#   2. THE C CHECK (Q139(k), tools/claims-v3/ccheck/README.md, "The exact use"): every launch runs through the wrapper
#      tools/claims-v3/ccheck/sparsity_ccheck.sh (--sparsity), which runs the C-logging host build/ccheck/b/host/sparsity_host with E78's kernel
#      build/sparsity/kernel/sparsity.elf (the runner passes no --kernel, so the wrapper appends it) and appends --c-log "$CCHECK_LOG" --c-poison;
#      CCHECK_LOG is the pass's c-log.jsonl. The check itself runs at the desk on the Intel (ccheck.py check), never here;
#   3. aifoundry3 card 0 only (CARD aifoundry3, no V3_DEVICE, the lock etsoc-shire0.lock); gen.sha256 covers kinds.json, blind6.json and the five
#      hold tiles; binaries.sha256 records the host, the kernel, the wrapper, ettelem and the guard.
# Kept from E144 unchanged: the two config reads through tools/claims-v3/e128/ettelem_guard.sh (config only), lib.sh's drain_mgmt replaced by a
# refusal (dev_mngt_service is never run), the card lock (flock -n, lib.sh's block_begin), timeout 10 on every device process, the other-user test
# (D1: an idle login does not block on aifoundry3; another user on this card or any other user's device process does), et-lab-manifest, E89's
# per-sensor sampler (tools/claims-v3/e89/pvt_sample.py, command 74 group 0 only, no statistics reset) and its start and stop. Nothing is set.
#
#   bash tools/claims-v3/e154/block_e154.sh <pass> [--smoke]
#   V3_DRY=1 bash tools/claims-v3/e154/block_e154.sh <pass> [--smoke]        # print every device call, touch nothing
. "$(dirname "${BASH_SOURCE[0]}")/../lib.sh"
ETTELEM=tools/claims-v3/e128/ettelem_guard.sh                                                   # E144 change 3
drain_mgmt() { log "E154: drain refused: dev_mngt_service is not in E154's classified command list"; return 0; }   # E144 change 3
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
[ "$CARD" = aifoundry3 ] && [ -z "${V3_DEVICE:-}" ] || { echo "E154 runs on aifoundry3 card 0 only (no V3_DEVICE; this is $CARD)" >&2; exit 2; }   # E154 change 3
others_present && exit 3

PASS=${1:?usage: block_e154.sh <pass> [--smoke]}
shift
SMOKE=
for x in "$@"; do case "$x" in --smoke) SMOKE=1 ;; *) echo "unknown $x" >&2; exit 2 ;; esac; done
case "$PASS" in ''|*[!0-9]*) echo "pass must be a number" >&2; exit 2 ;; esac
HERE=tools/claims-v3/e154
EXPN=e154; [ -n "$SMOKE" ] && EXPN=e154-smoke
RUNNER_PY=$HERE/run_e154.py                                                                      # E154 change 1
MEAS=tools/claims-v3/ccheck/sparsity_ccheck.sh; CCHOST=build/ccheck/b/host/sparsity_host; KERNEL=build/sparsity/kernel/sparsity.elf   # E154 change 2
RUN_ARGS=(--design "${E154_DESIGN:-full}")
[ -n "${E154_DEADLINE_EPOCH:-}" ] && RUN_ARGS+=(--deadline-epoch "$E154_DEADLINE_EPOCH")
[ -n "$SMOKE" ] && RUN_ARGS+=(--smoke --stoptest)

# ---- preflight: files only, no device ------------------------------------------------------------------------
pf=()
[ -f tools/claims-v3/kinds/kinds.json ] || pf+=("no tools/claims-v3/kinds/kinds.json")
[ -f tools/claims-v3/kinds/blind6/blind6.json ] || pf+=("no tools/claims-v3/kinds/blind6/blind6.json")
[ -x "$MEAS" ] || pf+=("missing the C-check wrapper $MEAS")
[ -x "$CCHOST" ] || pf+=("missing the C-logging host $CCHOST")
[ -f "$KERNEL" ] || pf+=("missing the kernel $KERNEL")
[ -x build/ettelem/ettelem ] || pf+=("missing build/ettelem/ettelem")
[ -f "$ETTELEM" ] || pf+=("missing $ETTELEM")
[ -f tools/claims-v3/e89/pvt_sample.py ] || pf+=("missing tools/claims-v3/e89/pvt_sample.py")
if [ -x "$CCHOST" ]; then
  for s in 'file:' int8 fp16 '--dump-tiles' '--stop-file' '--c-log' '--c-poison'; do grep -a -q -- "$s" "$CCHOST" || pf+=("$CCHOST has no $s"); done
fi
LK=/run/lock/etsoc-shire0.lock
[ -n "${V3_DRY:-}" ] || [ -e "$LK" ] || pf+=("no card lock $LK")
mkdir -p "$V3_ROOT/build"
LIST=$(python3 "$RUNNER_PY" /dev/null --root "$V3_ROOT" --pass-no "$PASS" --card "$CARD" ${RUN_ARGS[@]+"${RUN_ARGS[@]}"} \
       --list 2>"$V3_ROOT/build/e154-list.err") ||
  pf+=("runner --list (tiles against their sha256): $(tail -c 300 "$V3_ROOT/build/e154-list.err") ${LIST:0:300}")
MAXS=$(python3 -c 'import json,sys; print(json.loads(sys.argv[1])["max_s"])' "$LIST" 2>/dev/null)
case "$MAXS" in ''|*[!0-9]*) pf+=("bad runner --list output: ${LIST:0:200}") ;; esac
if [ ${#pf[@]} -gt 0 ]; then printf 'preflight: %s\n' "${pf[@]}" >&2; exit 2; fi

D=$DATA_ROOT/$EXPN/p$PASS
if [ -e "$D/block.json" ] && ! grep -q '"status":"ok"' "$D/block.json"; then mv "$D" "$D.attempt-$(date +%s)"; fi
if [ -d "$D" ] && [ ! -e "$D/block.json" ]; then mv "$D" "$D.attempt-$(date +%s)"; fi
block_begin "$EXPN" "$PASS"
others_present && { block_end others "another user before the first launch"; exit 3; }
[ -n "${V3_DRY:-}" ] || et-lab-manifest > "$OUT/manifest.txt" 2>/dev/null || true
( sha256sum tools/claims-v3/kinds/kinds.json tools/claims-v3/kinds/blind6/blind6.json tools/claims-v3/kinds/tiles/int8/full.bin \
    tools/claims-v3/kinds/blind6/tiles/fp32/fp32.real_smol_softmax_v_causal.bin tools/claims-v3/kinds/blind6/tiles/int8/int8.real_qwen_w8a8_v.bin \
    tools/claims-v3/kinds/blind6/tiles/int8/int8.b_line_zero_ff.bin tools/claims-v3/kinds/blind6/tiles/fp32/fp32.a_onebit_b5_third.bin
  sha256sum tools/claims-v3/e154/*.py tools/claims-v3/e154/*.sh tools/claims-v3/e97/run_e97b.py tools/claims-v3/e97/e97_common.py \
    tools/claims-v3/e89/run_e89.py tools/claims-v3/e89/pvt_sample.py tools/claims-v3/kinds/e78_common.py tools/claims-v3/kinds/e86_common.py
) > "$OUT/gen.sha256" 2>/dev/null || true
sha256sum "$CCHOST" "$KERNEL" "$MEAS" build/ettelem/ettelem "$ETTELEM" > "$OUT/binaries.sha256" 2>/dev/null || true   # E154 change 3
export CCHECK_LOG=$OUT/c-log.jsonl                                                               # E154 change 2
card_config() {
  if [ -n "${V3_DRY:-}" ]; then echo "DRY ettelem config" >&2; echo '{"dry":true}'; return 0; fi
  timeout 10 "$ETTELEM" config 2>/dev/null < /dev/null | grep '^{' | tail -1 || true
}
card_config > "$OUT/config_start.json"
# the per-sensor sampler, started the way lib.sh starts ettelem (first line awaited, retried; no drain); lib.sh's stop_sampler stops it
start_pvt_sampler() {
  local out=$1 secs=$2 attempt i
  if [ -n "${V3_DRY:-}" ]; then echo "DRY start_pvt_sampler $*" >&2; SAMPLER_PID=; SAMPLER_OUT=$out; : > "$out"; return 0; fi
  for attempt in 1 2 3 4; do
    python3 tools/claims-v3/e89/pvt_sample.py --seconds "$secs" --every-ms 100 > "$out.raw" 2>> "$OUT/sampler.err" < /dev/null &
    SAMPLER_PID=$!; SAMPLER_OUT=$out
    for i in $(seq 1 40); do sleep 0.25; grep -q '^{' "$out.raw" 2>/dev/null && return 0; done
    stop_sampler
    [ "$attempt" = 2 ] && drain_mgmt
    sleep 2
  done
  log "pvt sampler failed to start"; return 1
}
start_pvt_sampler "$OUT/telemetry.jsonl" $((MAXS + 900)) || { block_end failed "pvt sampler did not start"; exit 4; }
echo '{"sampler":"pvt"}' > "$OUT/sampler.json"
sleep 3
RUNNER=
on_signal() { [ -n "$RUNNER" ] && kill -TERM "$RUNNER" 2>/dev/null; wait "$RUNNER" 2>/dev/null; stop_sampler; block_end failed "signal"; exit 1; }
trap on_signal TERM INT HUP
python3 "$RUNNER_PY" "$OUT" --root "$V3_ROOT" --tel-live "$OUT/telemetry.jsonl.raw" --sparsity "$MEAS" \
  --pass-no "$PASS" --card "$CARD" ${RUN_ARGS[@]+"${RUN_ARGS[@]}"} &
RUNNER=$!
wait "$RUNNER"; rc=$?
RUNNER=
sleep 3
stop_sampler
card_config > "$OUT/config_end.json"
[ -s "$OUT/telemetry.jsonl" ] && gzip -f "$OUT/telemetry.jsonl"
case $rc in
  0) block_end ok "sampler pvt${SMOKE:+ smoke and stop tests}" ;;
  3) block_end others "another user on the card"; exit 3 ;;
  *) block_end failed "runner exit $rc"; exit 1 ;;
esac
