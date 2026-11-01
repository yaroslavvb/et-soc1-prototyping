#!/usr/bin/env bash
# E97 (Q132, tools/claims-v3/e97/E97.md): one pass on the local card, as a lib.sh block. A port of tools/claims-v3/e89/block_e89.sh
# (E89, sha256 in predictions-e97.json) with these changes, each marked E97 below:
#   1. Part A runs tools/claims-v3/e97/run_e97.py (run_e89.py unchanged, E97's blocks and order installed); --holds runs Part B,
#      tools/claims-v3/e97/run_e97b.py (the steady holds, on the same sampler);
#   2. --smoke: Part A's smoke blocks (SMOKE_BLOCKS), or with --holds a 65 s pass with a forced stop;
#   3. its data goes to $DATA_ROOT/e97/p<pass>/ (block_begin's code.sha256 covers tools/claims-v3/e97/*), and gen.sha256 also covers
#      real/real.json and its tiles;
#   4. the E89_SAMPLER fallback is gone: command 74 answered in all 22,976 of E89's samples, and the probe comes first.
# Everything else - the card lock (flock -n), timeout 10 on every device process, the other-user test (E78's D1 form for aifoundry3),
# the two read-only `ettelem config` reads under timeout 10, et-lab-manifest, the sampler's start and stop - is block_e89.sh's.
#
#   bash tools/claims-v3/e97/block_e97.sh <pass> [--holds] [--smoke]
#   V3_DRY=1 bash tools/claims-v3/e97/block_e97.sh <pass> [--holds]         # print every device call, touch nothing
. "$(dirname "${BASH_SOURCE[0]}")/../lib.sh"
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

PASS=${1:?usage: block_e97.sh <pass> [--holds] [--smoke]}
shift
SMOKE=; HOLDS=
for x in "$@"; do case "$x" in --smoke) SMOKE=1 ;; --holds) HOLDS=1 ;; *) echo "unknown $x" >&2; exit 2 ;; esac; done
case "$PASS" in ''|*[!0-9]*) echo "pass must be a number" >&2; exit 2 ;; esac
HERE=tools/claims-v3/e97
EXPN=e97; [ -n "$SMOKE" ] && EXPN=e97-smoke
RUNNER_PY=$HERE/run_e97.py; [ -n "$HOLDS" ] && RUNNER_PY=$HERE/run_e97b.py     # E97 change 1
DEADLINE=${E97_DEADLINE:-2026-11-01 07:13 PST}
RUN_ARGS=(); [ -n "$SMOKE" ] && RUN_ARGS=(--smoke)
[ -n "$HOLDS" ] && RUN_ARGS+=(--deadline "$DEADLINE")

# ---- preflight: files only, no device ------------------------------------------------------------------------
pf=()
[ -f tools/claims-v3/kinds/kinds.json ] || pf+=("no tools/claims-v3/kinds/kinds.json")
[ -x "$SPARSITY" ] || pf+=("missing $SPARSITY")
[ -x "$ETTELEM" ] || pf+=("missing $ETTELEM")
[ -f tools/claims-v3/e89/pvt_sample.py ] || pf+=("missing tools/claims-v3/e89/pvt_sample.py")
if [ -x "$SPARSITY" ]; then
  for s in 'file:' int8 fp16 '--dump-tiles' '--stop-file'; do grep -a -q -- "$s" "$SPARSITY" || pf+=("$SPARSITY has no $s"); done
fi
LK=/run/lock/etsoc-shire${V3_DEVICE:-0}.lock
[ -n "${V3_DRY:-}" ] || [ -e "$LK" ] || pf+=("no card lock $LK")
mkdir -p "$V3_ROOT/build"
LIST=$(python3 "$RUNNER_PY" /dev/null --root "$V3_ROOT" --pass-no "$PASS" --card "$CARD" ${RUN_ARGS[@]+"${RUN_ARGS[@]}"} \
       --list 2>"$V3_ROOT/build/e97-list.err") ||
  pf+=("runner --list (tiles against their sha256): $(tail -c 300 "$V3_ROOT/build/e97-list.err") ${LIST:0:300}")
MAXS=$(python3 -c 'import json,sys; print(json.loads(sys.argv[1])["max_s"])' "$LIST" 2>/dev/null)
case "$MAXS" in ''|*[!0-9]*) pf+=("bad runner --list output: ${LIST:0:200}") ;; esac
if [ ${#pf[@]} -gt 0 ]; then printf 'preflight: %s\n' "${pf[@]}" >&2; exit 2; fi

D=$DATA_ROOT/$EXPN/p$PASS
if [ -e "$D/block.json" ] && ! grep -q '"status":"ok"' "$D/block.json"; then mv "$D" "$D.attempt-$(date +%s)"; fi
if [ -d "$D" ] && [ ! -e "$D/block.json" ]; then mv "$D" "$D.attempt-$(date +%s)"; fi
block_begin "$EXPN" "$PASS"
others_present && { block_end others "another user before the first launch"; exit 3; }
[ -n "${V3_DRY:-}" ] || et-lab-manifest > "$OUT/manifest.txt" 2>/dev/null || true
( cd tools/claims-v3/kinds && sha256sum kinds.json e78_common.py e86_common.py real/real.json tiles/*/*.bin real/tiles/*/*.bin ) > "$OUT/gen.sha256" 2>/dev/null || true
card_config() {
  if [ -n "${V3_DRY:-}" ]; then echo "DRY ettelem config" >&2; echo '{"dry":true}'; return 0; fi
  timeout 10 "$ETTELEM" config 2>/dev/null < /dev/null | grep '^{' | tail -1 || true
}
card_config > "$OUT/config_start.json"
# the per-sensor sampler, started the way lib.sh starts ettelem (first line awaited, retried, a drain after the second failure); lib.sh's
# stop_sampler stops it (SIGTERM only; SIGKILL and a drain after 30 s)
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
python3 "$RUNNER_PY" "$OUT" --root "$V3_ROOT" --tel-live "$OUT/telemetry.jsonl.raw" --sparsity "$SPARSITY" \
  --pass-no "$PASS" --card "$CARD" ${RUN_ARGS[@]+"${RUN_ARGS[@]}"} &
RUNNER=$!
wait "$RUNNER"; rc=$?
RUNNER=
sleep 3
stop_sampler
card_config > "$OUT/config_end.json"
[ -s "$OUT/telemetry.jsonl" ] && gzip -f "$OUT/telemetry.jsonl"
case $rc in
  0) block_end ok "sampler pvt${SMOKE:+ smoke}${HOLDS:+ holds}" ;;
  3) block_end others "another user on the card"; exit 3 ;;
  *) block_end failed "runner exit $rc"; exit 1 ;;
esac
