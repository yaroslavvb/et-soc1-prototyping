#!/usr/bin/env bash
# E118 (Q133) on aifoundry1 card 0, one stage per call, from ~/nekko after the e118 directory was copied there from the
# freeze commit (the tree has no git: E118_FREEZE names it in the session's records):
#
#   bash tools/claims-v3/e118/run_e118.sh setup      # NO device access: tree, operand bytes, the ettelem-e118 build, dry run
#   bash tools/claims-v3/e118/run_e118.sh gates      # AFTER the claim: live gates (reads only) and the ring before the pin
#   bash tools/claims-v3/e118/run_e118.sh session    # AFTER the GO commit: session_e118.sh, detached (E118_CAP_END=<epoch>)
#   bash tools/claims-v3/e118/run_e118.sh status     # the session log, its steps and the guard's trips
#   bash tools/claims-v3/e118/run_e118.sh wait       # one bounded wait (<= 9 min) for the session to end
#   bash tools/claims-v3/e118/run_e118.sh final      # host-side closing reads (no device), after the session
set -u
cd "$(dirname "${BASH_SOURCE[0]}")/../../.."
ROOT=$PWD
export V3_DEVICE=0 ET_DEVICES=0 LD_LIBRARY_PATH=/opt/et/lib
export E118_FREEZE=${E118_FREEZE:-unset}
[ "$(hostname)" = aifoundry1 ] || { echo "E118 runs on aifoundry1 only (this is $(hostname))" >&2; exit 2; }
K=tools/claims-v3/e118
S=$ROOT/build/e118
ETT=build/ettelem-e118/ettelem
GEN=$ROOT/build/hl-gen
ITEMS600=anchor_pi,anchor_ones,anchor_zeros,anchor_randn,lq_h0,lq_h1,lq_h2,lq_h4,lq_h8,lq_h12,lq_h16,lq_h23,lb_h0,lb_h1,lb_h2,lb_h4,lb_h8,lb_h12,lb_h16,lb_h23
mkdir -p "$S"
stage=${1:?setup|gates|session|status|wait|final}
ts() { date '+%F %T %Z'; }
mycard() { et-who 2>&1 | awk '$1 ~ /^\/dev\/et0_/ || $1 ~ /^lock:etsoc-shire0\.lock/' | awk '{print $1, ($2==ENVIRON["USER"]?"me":"other"), $3}'; }
othercard() { et-who 2>&1 | awk '$1 ~ /^\/dev\/et1_/ || $1 ~ /^lock:etsoc-shire1\.lock/' | awk '{print $1, ($2==ENVIRON["USER"]?"me":"other"), $3}'; }
devprocs() { ps -eo uid=,comm= | awk -v me="$(id -u)" '$1 != me' | grep -c -E '_host$|ettelem$|dev_mngt_servi|et-powertop$|mmbench_launch|sys_emu$|Runner.Worker$'; }
klog() {
  local src=journalctl txt
  txt=$(journalctl -k -b --no-pager -q 2>/dev/null) || txt=
  [ -n "$txt" ] || { txt=$(dmesg 2>/dev/null) || txt=; src=dmesg; }
  [ -n "$txt" ] || { echo "kernel log: unreadable by this user"; return 0; }
  echo "kernel log ($src): card 0 (0000:01:00.0) lines $(printf '%s\n' "$txt" | grep -c '0000:01:00.0');" \
       "card 0 Error Event Detected $(printf '%s\n' "$txt" | grep '0000:01:00.0' | grep -c 'Error Event');" \
       "card 0 Tried to open same device $(printf '%s\n' "$txt" | grep '0000:01:00.0' | grep -c 'Tried to open same device');" \
       "AER $(printf '%s\n' "$txt" | grep -ci 'AER')"
  printf '%s\n' "$txt" | grep '0000:01:00.0' | tail -2 | cut -c1-160
}

case "$stage" in
setup)
  ts; hostname; uptime
  echo "== card 0's lines in et-who"; mycard; echo "== card 1's lines in et-who"; othercard
  echo "== other users' device processes or CI workers: $(devprocs)"
  echo "== tree (E118_FREEZE=$E118_FREEZE)"
  sha256sum $K/*.py $K/*.sh $K/ettelem-e118/ettelem.cpp tools/claims-v3/hl/run_hl.py tools/claims-v3/lib.sh \
    build/sparsity/host/sparsity_host build/sparsity/kernel/sparsity.elf "$GEN/manifest.json"
  echo "== building ettelem-e118 into build/ettelem-e118 (no device access)"
  cmake -S $K/ettelem-e118 -B build/ettelem-e118 -DCMAKE_PREFIX_PATH=/opt/et -Wno-dev > build/ettelem-e118.cmake.log 2>&1
  nice -n 10 cmake --build build/ettelem-e118 -j4 --clean-first > build/ettelem-e118.build.log 2>&1; echo "build rc=$?"
  grep -i -E 'error' build/ettelem-e118.build.log | head -5
  ls -l "$ETT"; sha256sum "$ETT"
  grep -aq E118-NO-PMIC-READ "$ETT" && echo "  marker E118-NO-PMIC-READ present" || echo "  MARKER MISSING"
  grep -qa ET_DEVICES /opt/et/lib/libdeviceLayer.a && echo "  /opt/et device layer honours ET_DEVICES" || echo "  device layer WITHOUT ET_DEVICES"
  echo "== refusals checked without opening the card"
  "$ETT" sample --reset-ms 1000 > /dev/null 2>&1; echo "  sample --reset-ms rc=$? (2 expected)"
  "$ETT" loglevel info > /dev/null 2>&1; echo "  loglevel rc=$? (2 expected)"
  "$ETT" threshold set 70 > /dev/null 2>&1; echo "  threshold set rc=$? (2 expected)"
  echo "== operand bytes against E60's card-0 list (docs/reports/data/2026-10-20-bitflip-ladder/gen-a1.sha256)"
  ref=docs/reports/data/2026-10-20-bitflip-ladder/gen-a1.sha256
  n=0; bad=0; miss=0
  while read -r h f; do
    case "$f" in tiles/*|srcs/*) ;; *) continue ;; esac
    if [ -f "$GEN/$f" ]; then g=$(sha256sum < "$GEN/$f" | cut -d' ' -f1); n=$((n + 1)); [ "$g" = "$h" ] || { bad=$((bad + 1)); echo "  DIFFERS: $f"; }
    else miss=$((miss + 1)); echo "  MISSING: $f"; fi
  done < "$ref"
  echo "  byte-identical to E60's card-0 list: $((n - bad))/$n (missing $miss)"
  echo "== the plan (run_hl --list)"
  python3 tools/claims-v3/hl/run_hl.py /dev/null --root "$ROOT" --gen "$GEN" --items "$ITEMS600" --burnin 2 --list
  python3 tools/claims-v3/hl/run_hl.py /dev/null --root "$ROOT" --gen "$GEN" --items anchor_pi,lq_h0,lq_h2,lq_h8 --burnin 2 --list
  echo "== dry runs (no device access)"
  rm -rf "${ROOT:?}/build/claims-v3-dry/aifoundry1-c0/e118" "${ROOT:?}/build/claims-v3-dry/aifoundry1-c0/e118c"
  V3_DRY=1 HL_EXPN=e118 HL_TARGET=57 HL_PREHEAT=58 HL_MAX_C=72 bash $K/block_e118.sh 7260 "$ITEMS600" > build/e118-dry.log 2>&1; echo "  dry 600 MHz pass rc=$?"; tail -2 build/e118-dry.log
  V3_DRY=1 HL_EXPN=e118c HL_TARGET=57 HL_PREHEAT=58 HL_MAX_C=72 E118_HEATER=$K/heater_pi.sh bash $K/block_e118.sh 7261 anchor_pi,lq_h0,lq_h2,lq_h8 > build/e118c-dry.log 2>&1; echo "  dry control pass rc=$?"; tail -2 build/e118c-dry.log
  df -h /home | tail -1
  ;;
gates)
  f=$S/gates-$(date +%H%M%S).out
  {
    ts; hostname; uptime
    echo "== card 0's lines in et-who (none expected)"; mycard; echo "== card 1's lines (none expected)"; othercard
    echo "== other users' device processes or CI workers: $(devprocs)"
    echo "== driver module"; lsmod | awk 'NR==1 || /^et/' | head -4
    echo "== kernel log before"; klog
    echo "== gov_e118.py gates (ettelem-e118 config and uptime under card 0's lock; the vmin-LUT read under both locks)"
    python3 -I $K/gov_e118.py gates --out "$S"; echo "gates rc=$?"
    echo "== SP ring before the pin (read only, card 0's lock)"
    python3 -I $K/gov_e118.py ring --out "$S" --tag before-pin; echo "ring rc=$?"
    echo "== et-who after"; mycard; othercard; ts
  } > "$f" 2>&1
  cat "$f"
  ;;
session)
  [ -e "$S/steps.jsonl" ] && { echo "the session already started"; exit 0; }
  : "${E118_CAP_END:?set E118_CAP_END (epoch)}"
  E118_CAP_END=$E118_CAP_END setsid nohup bash $K/session_e118.sh > "$S/session.out" 2>&1 < /dev/null &
  echo "E118 session started: pid $!, cap end $(date -d @"$E118_CAP_END" '+%T %Z'), log $S/session.log"
  ;;
status)
  tail -8 "$S/session.log" 2>/dev/null; echo "--"; tail -4 "$S/steps.jsonl" 2>/dev/null
  grep -h TRIP "$S/guard.jsonl" 2>/dev/null | tail -3
  [ -e "$S/end.json" ] && cat "$S/end.json"
  ;;
wait)
  t=0; while [ ! -e "$S/end.json" ] && [ $t -lt 530 ]; do sleep 10; t=$((t + 10)); done
  tail -5 "$S/session.log" 2>/dev/null; echo "--"; tail -3 "$S/steps.jsonl" 2>/dev/null
  grep -h TRIP "$S/guard.jsonl" 2>/dev/null | tail -3
  [ -e "$S/end.json" ] && cat "$S/end.json" || echo "not ended"
  ;;
final)
  f=$S/final-$(date +%H%M%S).out
  {
    ts; echo "== our E118 processes: $(pgrep -u "$USER" -f '[s]ession_e118|[g]uard_e118|[b]lock_e118' | wc -l)"
    echo "== watchdog"; cat "$S/watchdog.log" 2>/dev/null; pgrep -u "$USER" -f '[w]atchdog.sh' | wc -l
    echo "== card 0's lines in et-who"; mycard; echo "== card 1's lines"; othercard
    echo "== other users' device processes or CI workers: $(devprocs)"
    echo "== kernel log after"; klog
    df -h /home | tail -1; ts
  } > "$f" 2>&1
  cat "$f"
  ;;
*) echo "unknown stage $stage" >&2; exit 2 ;;
esac
