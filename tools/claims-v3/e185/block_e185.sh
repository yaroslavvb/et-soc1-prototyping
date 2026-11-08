#!/usr/bin/env bash
# E185 (M11's session 3; tools/claims-v3/e185/E185.md, 98fe28b7; the kit tools/claims-v3/e185/KIT.md): one pass on aifoundry3 card 0, as a
# lib.sh block. A port of tools/claims-v3/e181/block_e181.sh (33cdccf6, which stays as committed) with E185's names and these changes, each
# marked E185:
#   1. the runner is tools/claims-v3/e185/run_e185.py (E185's six holds; E171's stops, a stop ending the pass); --smoke runs its smoke plan
#      (A6-1's floor mark first) and then the six stop-path tests, data in $DATA_ROOT/e185-smoke/p<pass>/; the measured pass goes to
#      $DATA_ROOT/e185/p<pass>/ with --deadline-epoch $E185_DEADLINE_EPOCH and --floor-marks $E185_FLOOR_MARKS;
#   2. exit 6 from the runner is a stop line (E171's stops: the hold's line ended the pass, or the session line): block.json status "stop",
#      exit 6;
#   3. gen.sha256 names E185's files.
# Kept from E181 unchanged: exit 7 as A6-1 (the smoke) or the start gate (the measured pass); the C check on every launch (Q139(k)'s wrapper
# with the C-logging host); the two config reads through E128's guard (config only); the drain refused; the card lock; timeout 10 on every
# device process; the other-user test (an idle login does not block on aifoundry3); et-lab-manifest; E89's per-sensor sampler (command 74
# group 0 only, no statistics reset). Nothing is set.
#
#   bash tools/claims-v3/e185/block_e185.sh <pass> [--smoke]
#   V3_DRY=1 bash tools/claims-v3/e185/block_e185.sh <pass> [--smoke]        # print every device call, touch nothing
if [ -n "${E185_DESK:-}" ] && [ -z "${V3_DRY:-}" ]; then echo "E185_DESK is for a dry pass only (V3_DRY=1)" >&2; exit 2; fi
. "$(dirname "${BASH_SOURCE[0]}")/../lib.sh"
ETTELEM=tools/claims-v3/e128/ettelem_guard.sh
drain_mgmt() { log "E185: drain refused: dev_mngt_service is not in E185's classified command list"; return 0; }
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
[ "$CARD" = aifoundry3 ] && [ -z "${V3_DEVICE:-}" ] || { echo "E185 runs on aifoundry3 card 0 only (no V3_DEVICE; this is $CARD)" >&2; exit 2; }
others_present && exit 3

PASS=${1:?usage: block_e185.sh <pass> [--smoke]}
shift
SMOKE=
for x in "$@"; do case "$x" in --smoke) SMOKE=1 ;; *) echo "unknown $x" >&2; exit 2 ;; esac; done
case "$PASS" in ''|*[!0-9]*) echo "pass must be a number" >&2; exit 2 ;; esac
HERE=tools/claims-v3/e185
EXPN=e185; [ -n "$SMOKE" ] && EXPN=e185-smoke
RUNNER_PY=$HERE/run_e185.py                                                                      # E185 change 1
MEAS=tools/claims-v3/ccheck/sparsity_ccheck.sh; CCHOST=build/ccheck/b/host/sparsity_host; KERNEL=build/sparsity/kernel/sparsity.elf
RUN_ARGS=()
[ -n "${E185_DEADLINE_EPOCH:-}" ] && RUN_ARGS+=(--deadline-epoch "$E185_DEADLINE_EPOCH")
[ -n "$SMOKE" ] && RUN_ARGS+=(--smoke --stoptest)
[ -z "$SMOKE" ] && [ -n "${E185_FLOOR_MARKS:-}" ] && RUN_ARGS+=(--floor-marks "$E185_FLOOR_MARKS")              # E185 change 1

# ---- preflight: files only, no device ------------------------------------------------------------------------
pf=(); desk=()
need_bin() {   # under E185_DESK a box-only binary is listed, not required (E181's)
  if [ -n "${E185_DESK:-}" ]; then desk+=("$1"); else pf+=("$1"); fi
}
[ -f tools/claims-v3/kinds/kinds.json ] || pf+=("no tools/claims-v3/kinds/kinds.json")
[ -x "$MEAS" ] || pf+=("missing the C-check wrapper $MEAS")
[ -x "$CCHOST" ] || need_bin "missing the C-logging host $CCHOST"
[ -f "$KERNEL" ] || need_bin "missing the kernel $KERNEL"
[ -x build/ettelem/ettelem ] || need_bin "missing build/ettelem/ettelem"
[ -f "$ETTELEM" ] || pf+=("missing $ETTELEM")
[ -f tools/claims-v3/e89/pvt_sample.py ] || pf+=("missing tools/claims-v3/e89/pvt_sample.py")
if [ -x "$CCHOST" ]; then
  for s in 'file:' int8 fp16 '--dump-tiles' '--stop-file' '--c-log' '--c-poison'; do grep -a -q -- "$s" "$CCHOST" || pf+=("$CCHOST has no $s"); done
fi
LK=/run/lock/etsoc-shire0.lock
[ -n "${V3_DRY:-}" ] || [ -e "$LK" ] || pf+=("no card lock $LK")
[ ${#desk[@]} -gt 0 ] && printf 'desk dry pass (E185_DESK): box-only, not checked here: %s\n' "${desk[@]}" >&2
mkdir -p "$V3_ROOT/build"
LIST=$(python3 "$RUNNER_PY" /dev/null --root "$V3_ROOT" --pass-no "$PASS" --card "$CARD" ${RUN_ARGS[@]+"${RUN_ARGS[@]}"} \
       --list 2>"$V3_ROOT/build/e185-list.err") ||
  pf+=("runner --list (tiles against their sha256): $(tail -c 300 "$V3_ROOT/build/e185-list.err") ${LIST:0:300}")
MAXS=$(python3 -c 'import json,sys; print(json.loads(sys.argv[1])["max_s"])' "$LIST" 2>/dev/null)
case "$MAXS" in ''|*[!0-9]*) pf+=("bad runner --list output: ${LIST:0:200}") ;; esac
if [ ${#pf[@]} -gt 0 ]; then printf 'preflight: %s\n' "${pf[@]}" >&2; exit 2; fi

D=$DATA_ROOT/$EXPN/p$PASS
if [ -e "$D/block.json" ] && ! grep -q '"status":"ok"' "$D/block.json"; then mv "$D" "$D.attempt-$(date +%s)"; fi
if [ -d "$D" ] && [ ! -e "$D/block.json" ]; then mv "$D" "$D.attempt-$(date +%s)"; fi
block_begin "$EXPN" "$PASS"
others_present && { block_end others "another user before the first launch"; exit 3; }
[ -n "${V3_DRY:-}" ] || et-lab-manifest > "$OUT/manifest.txt" 2>/dev/null || true
( sha256sum tools/claims-v3/kinds/kinds.json tools/claims-v3/kinds/tiles/fp32/randn.bin tools/claims-v3/kinds/tiles/fp32/zeros.bin \
    tools/claims-v3/kinds/tiles/int8/full.bin tools/claims-v3/kinds/tiles/int8/neg_ones.bin
  sha256sum tools/claims-v3/e185/run_e185.py tools/claims-v3/e185/smoke_gate_e185.py tools/claims-v3/e185/*.sh tools/claims-v3/e97/run_e97b.py tools/claims-v3/e97/e97_common.py \
    tools/claims-v3/e89/run_e89.py tools/claims-v3/e89/pvt_sample.py tools/claims-v3/kinds/e78_common.py tools/claims-v3/kinds/e86_common.py
) > "$OUT/gen.sha256" 2>/dev/null || true
sha256sum "$CCHOST" "$KERNEL" "$MEAS" build/ettelem/ettelem "$ETTELEM" > "$OUT/binaries.sha256" 2>/dev/null || true
export CCHECK_LOG=$OUT/c-log.jsonl
card_config() {
  if [ -n "${V3_DRY:-}" ]; then echo "DRY ettelem config" >&2; echo '{"dry":true}'; return 0; fi
  timeout 10 "$ETTELEM" config 2>/dev/null < /dev/null | grep '^{' | tail -1 || true
}
card_config > "$OUT/config_start.json"
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
  6) block_end stop "a stop line ended the pass (E171's stops: a firmware reading >= 70 C, a 34-sensor mean >= 72 C or a board >= 65 W; or the session line)"; exit 6 ;;   # E185 change 2
  7) if [ -n "$SMOKE" ]; then
       block_end gate "A6-1: F0 above 53.9 C or unreadable: the session ends before the smoke's first launch, no hold"; exit 7
     fi
     block_end gate "the start gate (G0-A6 with A8-4): R0's room above 53.9 C, or its residue less 0.414 C above 0.50 C, or unreadable; no hold ran"; exit 7 ;;
  *) block_end failed "runner exit $rc"; exit 1 ;;
esac
