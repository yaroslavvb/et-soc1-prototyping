#!/usr/bin/env bash
# E89 (Q130, tools/claims-v3/e89/E89.md): one pass of the low-power heat lock-in on the local card, as a lib.sh block.
# A port of tools/claims-v3/kinds/block_e78.sh (E78) with these changes, each marked E89 below:
#   1. it runs tools/claims-v3/e89/run_e89.py (the lock-in schedule) on kinds.json's tiles, checked first;
#   2. the 10 Hz sampler is tools/claims-v3/e89/pvt_sample.py, which reads what `ettelem sample` reads plus the 34
#      per-sensor temperatures (command 74, group 0, a read); E89_SAMPLER=ettelem falls back to lib.sh's sampler
#      (registered fallback, used only if the probe finds no command 74);
#   3. its data goes to $DATA_ROOT/e89/p<pass>/ (block_begin's code.sha256 covers tools/claims-v3/e89/*).
# Everything else - the card lock (flock -n), timeout 10 on every device process, the other-user test (E78's D1 form
# for aifoundry3), the two read-only `ettelem config` reads under timeout 10, et-lab-manifest - is block_e78.sh's.
#
#   bash tools/claims-v3/e89/block_e89.sh <pass> [--smoke]
#   V3_DRY=1 bash tools/claims-v3/e89/block_e89.sh <pass>          # print every device call, touch nothing
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

PASS=${1:?usage: block_e89.sh <pass> [--smoke]}
SMOKE=; [ "${2:-}" = --smoke ] && SMOKE=1
case "$PASS" in ''|*[!0-9]*) echo "pass must be a number" >&2; exit 2 ;; esac
HERE=tools/claims-v3/e89
EXPN=e89; [ -n "$SMOKE" ] && EXPN=e89-smoke
SAMPLER_KIND=${E89_SAMPLER:-pvt}
RUN_ARGS=(); [ -n "$SMOKE" ] && RUN_ARGS=(--smoke)

# ---- preflight: files only, no device ------------------------------------------------------------------------
pf=()
[ -f tools/claims-v3/kinds/kinds.json ] || pf+=("no tools/claims-v3/kinds/kinds.json")
[ -x "$SPARSITY" ] || pf+=("missing $SPARSITY")
[ -x "$ETTELEM" ] || pf+=("missing $ETTELEM")
[ -f "$HERE/pvt_sample.py" ] || pf+=("missing $HERE/pvt_sample.py")
if [ -x "$SPARSITY" ]; then
  for s in 'file:' int8 '--dump-tiles' '--stop-file'; do grep -a -q -- "$s" "$SPARSITY" || pf+=("$SPARSITY has no $s"); done
fi
LK=/run/lock/etsoc-shire${V3_DEVICE:-0}.lock
[ -n "${V3_DRY:-}" ] || [ -e "$LK" ] || pf+=("no card lock $LK")
case "$SAMPLER_KIND" in pvt|ettelem) ;; *) pf+=("E89_SAMPLER must be pvt or ettelem") ;; esac
mkdir -p "$V3_ROOT/build"
LIST=$(python3 "$HERE/run_e89.py" /dev/null --root "$V3_ROOT" --pass-no "$PASS" --card "$CARD" ${RUN_ARGS[@]+"${RUN_ARGS[@]}"} \
       --list 2>"$V3_ROOT/build/e89-list.err") ||
  pf+=("run_e89 --list (tiles against kinds.json): $(tail -c 300 "$V3_ROOT/build/e89-list.err") ${LIST:0:300}")
MAXS=$(python3 -c 'import json,sys; print(json.loads(sys.argv[1])["max_s"])' "$LIST" 2>/dev/null)
case "$MAXS" in ''|*[!0-9]*) pf+=("bad run_e89 --list output: ${LIST:0:200}") ;; esac
if [ ${#pf[@]} -gt 0 ]; then printf 'preflight: %s\n' "${pf[@]}" >&2; exit 2; fi

D=$DATA_ROOT/$EXPN/p$PASS
if [ -e "$D/block.json" ] && ! grep -q '"status":"ok"' "$D/block.json"; then mv "$D" "$D.attempt-$(date +%s)"; fi
if [ -d "$D" ] && [ ! -e "$D/block.json" ]; then mv "$D" "$D.attempt-$(date +%s)"; fi
block_begin "$EXPN" "$PASS"
others_present && { block_end others "another user before the first launch"; exit 3; }
[ -n "${V3_DRY:-}" ] || et-lab-manifest > "$OUT/manifest.txt" 2>/dev/null || true
( cd tools/claims-v3/kinds && sha256sum kinds.json e78_common.py tiles/*/*.bin ) > "$OUT/gen.sha256" 2>/dev/null || true
card_config() {
  if [ -n "${V3_DRY:-}" ]; then echo "DRY ettelem config" >&2; echo '{"dry":true}'; return 0; fi
  timeout 10 "$ETTELEM" config 2>/dev/null < /dev/null | grep '^{' | tail -1 || true
}
card_config > "$OUT/config_start.json"
# E89 change 2: the per-sensor sampler, started the way lib.sh starts ettelem (first line awaited, retried, a drain
# after the second failure); lib.sh's stop_sampler stops it (SIGTERM only; SIGKILL and a drain after 30 s).
start_pvt_sampler() {
  local out=$1 secs=$2 attempt i
  if [ -n "${V3_DRY:-}" ]; then echo "DRY start_pvt_sampler $*" >&2; SAMPLER_PID=; SAMPLER_OUT=$out; : > "$out"; return 0; fi
  for attempt in 1 2 3 4; do
    python3 "$HERE/pvt_sample.py" --seconds "$secs" --every-ms 100 > "$out.raw" 2>> "$OUT/sampler.err" < /dev/null &
    SAMPLER_PID=$!; SAMPLER_OUT=$out
    for i in $(seq 1 40); do sleep 0.25; grep -q '^{' "$out.raw" 2>/dev/null && return 0; done
    stop_sampler
    [ "$attempt" = 2 ] && drain_mgmt
    sleep 2
  done
  log "pvt sampler failed to start"; return 1
}
if [ "$SAMPLER_KIND" = pvt ]; then
  start_pvt_sampler "$OUT/telemetry.jsonl" $((MAXS + 900)) || { block_end failed "pvt sampler did not start"; exit 4; }
else
  start_sampler "$OUT/telemetry.jsonl" $((MAXS + 900)) || { block_end failed "sampler did not start"; exit 4; }
fi
echo "{\"sampler\":\"$SAMPLER_KIND\"}" > "$OUT/sampler.json"
sleep 3
RUNNER=
on_signal() { [ -n "$RUNNER" ] && kill -TERM "$RUNNER" 2>/dev/null; wait "$RUNNER" 2>/dev/null; stop_sampler; block_end failed "signal"; exit 1; }
trap on_signal TERM INT HUP
python3 "$HERE/run_e89.py" "$OUT" --root "$V3_ROOT" --tel-live "$OUT/telemetry.jsonl.raw" --sparsity "$SPARSITY" \
  --pass-no "$PASS" --card "$CARD" ${RUN_ARGS[@]+"${RUN_ARGS[@]}"} &
RUNNER=$!
wait "$RUNNER"; rc=$?
RUNNER=
sleep 3
stop_sampler
card_config > "$OUT/config_end.json"
[ -s "$OUT/telemetry.jsonl" ] && gzip -f "$OUT/telemetry.jsonl"
case $rc in
  0) block_end ok "sampler $SAMPLER_KIND${SMOKE:+ smoke}" ;;
  3) block_end others "another user on the card"; exit 3 ;;
  *) block_end failed "run_e89 exit $rc"; exit 1 ;;
esac
