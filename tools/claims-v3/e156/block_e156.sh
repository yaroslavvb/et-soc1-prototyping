#!/usr/bin/env bash
# E156 (Q139, tools/claims-v3/e156/README.md): one pass of E156's items on aifoundry1 card 1, as a lib.sh block. A copy of E75's
# tools/claims-v3/mf/block.sh (which E132 and E139 ran unchanged on aifoundry3) with these changes, each marked E156:
#   1. the runner is tools/claims-v3/e156/run_e156.py: runitems.py unchanged, with E155's live-sample stops and in-run watcher installed around it
#      (board_w >= 66 W, a minion-shire field >= 72 C, or a sampler line 1.5 s old or older, read from the running sampler's .raw file, writes STOP
#      and ends the pass), and runitems' own die cap --max-c 70 on temp_c.minshire[0] (E139's MF_MAX_C);
#   2. --stoptest runs no launch: the sampler starts, then run_e156.py four times with E156_STOPTEST=die, =board, =watch and =stale, each of which
#      must end with EXIT_HOT (6) and a STOP line read from a live sample, under e156-stoptest/ (E155's stop-path test);
#   3. card 1 only (CARD aifoundry1-c1, V3_DEVICE=1, the lock etsoc-shire1.lock); the images build/e156-gen, the host build/enercat-e99 (E99's
#      source and build script, built on this box), data under e156/ (e156-smoke/ for the smoke);
#   4. CARE WITH DEVICE COMMANDS (the owner's rule of Mon 2 Nov 2026), E128's and E155's change: every telemetry call goes through
#      tools/claims-v3/e128/ettelem_guard.sh, the allow-list that passes only `ettelem config` and `ettelem sample --seconds --every-ms` (the
#      classified READs of README.md) and refuses anything else before the device opens; lib.sh's drain_mgmt is replaced by a refusal, so the vendor
#      tool dev_mngt_service is never run: a sampler that will not start fails the block instead.
# Everything else - the card lock, hold10/timeout 10 on every device process, the other-user test (an idle login does not block on aifoundry1;
# another user on this card or any other user's device process does), the launch protocol, the sampler (no --reset-ms), the STOP file, the
# records - is mf/block.sh's, lib.sh's and runitems.py's, unchanged. Nothing is set: no governor, TDP, threshold or clock set, no reset.
#
#   V3_DEVICE=1 bash tools/claims-v3/e156/block_e156.sh <pass> [items] [--stoptest]
#   V3_DEVICE=1 V3_DRY=1 bash tools/claims-v3/e156/block_e156.sh <pass>          # print every device call, touch nothing
. "$(dirname "${BASH_SOURCE[0]}")/../lib.sh"
ETTELEM=tools/claims-v3/e128/ettelem_guard.sh                                                                     # E156 change 4
drain_mgmt() { log "E156: drain refused: dev_mngt_service is not in E156's classified command list"; return 0; }   # E156 change 4
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
[ "$CARD" = aifoundry1-c1 ] || { echo "E156 runs on aifoundry1 card 1 only (V3_DEVICE=1; this is $CARD)" >&2; exit 2; }   # E156 change 3
others_present && exit 3
[ -n "${V3_DEVICE:-}" ] && export V3_DEVICE

PASS=${1:?usage: block_e156.sh <pass> [items] [--stoptest]}
ITEMS=${2:-anchor_pi,dp_zeros,dm_,wl_,vl_,c3_,eh_,el_,e7_,e2_}
MODE=; [ "${3:-}" = --stoptest ] && MODE=stoptest                                                                   # E156 change 2
case "$PASS" in ''|*[!0-9]*) echo "pass must be a number" >&2; exit 2 ;; esac
GEN=${MF_GEN:-$V3_ROOT/build/e156-gen}                                                                               # E156 change 3
ENERCAT_MF=${MF_ENERCAT:-build/enercat-e99/host/enercat_host}                                                       # E156 change 3
TARGET=${MF_TARGET:-58}; PREHEAT=${MF_PREHEAT:-59}; BURNIN=${MF_BURNIN:-2}; MAXC=${MF_MAX_C:-70}                     # E156 change 1
ITEM_S=${MF_ITEM_S:-4}; FMA_S=4; EXPN=${MF_EXPN:-e156}
[ -n "$MODE" ] && EXPN=${MF_EXPN:-e156}-stoptest

# ---- preflight: files only, no device ------------------------------------------------------------------------
pf=()
[ -f "$GEN/manifest.json" ] || pf+=("no $GEN/manifest.json (python3 tools/claims-v3/e156/make_e156.py $GEN --check)")
[ -x "$SPARSITY" ] || pf+=("missing $SPARSITY (anchor_pi)")
[ -x "$HEATER" ] || pf+=("missing heater $HEATER")
[ -x "$ETTELEM" ] || pf+=("missing $ETTELEM")
[ -x build/ettelem/ettelem ] || pf+=("missing build/ettelem/ettelem")
[ -x "$ENERCAT_MF" ] || pf+=("missing $ENERCAT_MF (bash tools/claims-v3/dm/build_host.sh)")
if [ -x "$ENERCAT_MF" ]; then
  grep -a -q -- '--operands file:' "$ENERCAT_MF" || pf+=("$ENERCAT_MF has no --operands file:")
  grep -a -q 'ld_l1' "$ENERCAT_MF" || pf+=("$ENERCAT_MF has no ld_l1 pattern")
  grep -a -q 'flw_pat' "$ENERCAT_MF" || pf+=("$ENERCAT_MF has no flw_pat pattern")
fi
for b in "$SPARSITY" "$HEATER"; do [ -x "$b" ] && { grep -a -q -- '--stop-file' "$b" || pf+=("$b has no --stop-file"); }; done
LK=/run/lock/etsoc-shire${V3_DEVICE:-0}.lock
[ -n "${V3_DRY:-}" ] || [ -e "$LK" ] || pf+=("no card lock $LK")
mkdir -p "$V3_ROOT/build"
LIST=$(python3 tools/claims-v3/e156/run_e156.py /dev/null --root "$V3_ROOT" --gen "$GEN" --items "$ITEMS" \
        --tool "$ENERCAT_MF" --burnin "$BURNIN" --item-s "$ITEM_S" --list 2>"$V3_ROOT/build/e156-list.err") ||
  pf+=("run_e156 --list (harness against its freeze, then runitems --list): $(tail -c 300 "$V3_ROOT/build/e156-list.err")")
MAXS=$(python3 -c 'import json,sys; print(json.loads(sys.argv[1])["max_s"])' "$LIST" 2>/dev/null)
case "$MAXS" in ''|*[!0-9]*) pf+=("bad run_e156 --list output: ${LIST:0:200}") ;; esac
if [ ${#pf[@]} -gt 0 ]; then printf 'preflight: %s\n' "${pf[@]}" >&2; exit 2; fi

D=$DATA_ROOT/$EXPN/p$PASS
if [ -e "$D/block.json" ] && ! grep -q '"status":"ok"' "$D/block.json"; then mv "$D" "$D.attempt-$(date +%s)"; fi
if [ -d "$D" ] && [ ! -e "$D/block.json" ]; then mv "$D" "$D.attempt-$(date +%s)"; fi
block_begin "$EXPN" "$PASS"
others_present && { block_end others "another user before the first launch"; exit 3; }
[ -n "${V3_DRY:-}" ] || et-lab-manifest > "$OUT/manifest.txt" 2>/dev/null || true
( cd "$GEN" && sha256sum manifest.json srcs/* ) > "$OUT/gen.sha256" 2>/dev/null || true
bash tools/claims-v3/text_hash.sh "$ENERCAT_MF" "$SPARSITY" > "$OUT/text.sha256" 2>/dev/null || true
sha256sum "$ENERCAT_MF" build/enercat-hl/kernel/enercat.elf "$SPARSITY" "$HEATER" build/ettelem/ettelem "$ETTELEM" > "$OUT/binaries.sha256" 2>/dev/null || true
start_sampler "$OUT/telemetry.jsonl" $((MAXS + 900)) || { block_end failed "sampler did not start"; exit 4; }
sleep 3
RUNNER=
on_signal() { [ -n "$RUNNER" ] && kill -TERM "$RUNNER" 2>/dev/null; wait "$RUNNER" 2>/dev/null; stop_sampler; block_end failed "signal"; exit 1; }
trap on_signal TERM INT HUP
run_pass() {
  python3 tools/claims-v3/e156/run_e156.py "$OUT" --root "$V3_ROOT" --gen "$GEN" --items "$ITEMS" \
    --tool "$ENERCAT_MF" --tel-live "$OUT/telemetry.jsonl.raw" --heater "$HEATER" --sparsity "$SPARSITY" \
    --blocks 1 --first-block "$PASS" --seed "$PASS" --target "$TARGET" --preheat "$PREHEAT" --max-c "$MAXC" \
    --item-s "$ITEM_S" --fma-s "$FMA_S" --burnin "$BURNIN" --card "$CARD" &
  RUNNER=$!
  wait "$RUNNER"; rc=$?
  RUNNER=
}
if [ "$MODE" = stoptest ]; then                                                                                     # E156 change 2
  st=()
  for k in die board watch stale; do
    export E156_STOPTEST=$k
    run_pass
    st+=("$k:rc=$rc")
    log "E156 stop-path test ($k): run_e156 exit $rc"
    unset E156_STOPTEST
    # runitems refuses to start while its STOP file exists, so each test's STOP line is kept under its own name
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
[ -s "$OUT/telemetry.jsonl" ] && gzip -f "$OUT/telemetry.jsonl"
case $rc in
  0) block_end ok "$ITEMS${MODE:+ $MODE}" ;;
  3) block_end others "another user on the card"; exit 3 ;;
  *) block_end failed "run_e156 exit $rc${MODE:+ ($MODE)}"; exit 1 ;;
esac
