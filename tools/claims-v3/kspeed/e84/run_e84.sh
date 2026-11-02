#!/usr/bin/env bash
# E84 (Q130) on aifoundry1 card 0, one stage per call. Run it from ~/nekko after copying tools/claims-v3/kspeed/
# there from the freeze commit (the tree has no git: E84_FREEZE names the commit in every session's e84.json):
#
#   bash tools/claims-v3/kspeed/e84/run_e84.sh setup     # NO device access: tree, binaries, the ettelem build, dry run
#   bash tools/claims-v3/kspeed/e84/run_e84.sh ident     # AFTER the claim: read-only config and firmware reads
#   bash tools/claims-v3/kspeed/e84/run_e84.sh smoke     # AFTER the claim: three 2 s runs (SMOKE), not analysed
#   bash tools/claims-v3/kspeed/e84/run_e84.sh go        # the measured session, detached on the box
#   bash tools/claims-v3/kspeed/e84/run_e84.sh status    # the session log and its progress
#   bash tools/claims-v3/kspeed/e84/run_e84.sh wait      # one bounded wait (<= 9 min) for the session to end
#   bash tools/claims-v3/kspeed/e84/run_e84.sh final     # read-only closing reads, after the session
#
# Every device process goes through run_e84.py (the card lock, `timeout 10`, the other-user test) or, in ident and
# final, through `timeout 10`/`timeout 20` with the card's lock held non-blocking. Nothing is written to the card.
set -u
cd "$(dirname "${BASH_SOURCE[0]}")/../../../.."
ROOT=$PWD
export V3_DEVICE=0 ET_DEVICES=0 LD_LIBRARY_PATH=/opt/et/lib
export E84_FREEZE=${E84_FREEZE:-unset}
[ "$(hostname)" = aifoundry1 ] || { echo "E84 runs on aifoundry1 only (this is $(hostname))" >&2; exit 2; }
K=tools/claims-v3/kspeed/e84
P=$K/protocol.json
OUT=$ROOT/build/e84
ETT=build/ettelem-e84/ettelem
mkdir -p "$OUT/runs" "$OUT/ident"
stage=${1:?setup|ident|smoke|go|status|wait|final}
ts() { date '+%F %T %Z'; }
mycard() { et-who 2>&1 | awk '$1 ~ /^\/dev\/et0_/ || $1 ~ /^lock:etsoc-shire0\.lock/' | awk '{print $1, ($2==ENVIRON["USER"]?"me":"other")}'; }
othercard() { et-who 2>&1 | awk '$1 ~ /^\/dev\/et1_/ || $1 ~ /^lock:etsoc-shire1\.lock/' | awk '{print $1, ($2==ENVIRON["USER"]?"me":"other")}'; }

case "$stage" in
setup)
  ts; hostname; uptime
  echo "== card 0's own lines in et-who (none expected)"; mycard
  echo "== card 1's lines in et-who"; othercard
  echo "== device processes or CI workers (count)"; ps -eo uid=,comm= | grep -c -E '_host$|ettelem$|dev_mngt_servi|et-powertop$|mmbench_launch|sys_emu$|Runner.Worker$'
  echo "== tree"; echo "root $ROOT, E84_FREEZE=$E84_FREEZE"
  sha256sum tools/claims-v3/hpl/run_hpl.py tools/claims-v3/kspeed/run_kspeed.py $K/run_e84.py $P \
    tools/claims-v3/kinds/kinds.json build/sparsity/host/sparsity_host build/sparsity/kernel/sparsity.elf
  if [ ! -x "$ETT" ]; then
    echo "== building ettelem-dv2 into build/ettelem-e84 (no device access)"
    cmake -S tools/claims-v3/dv2/ettelem-dv2 -B build/ettelem-e84 -DCMAKE_PREFIX_PATH=/opt/et -Wno-dev > build/ettelem-e84.cmake.log 2>&1
    nice -n 10 cmake --build build/ettelem-e84 -j4 > build/ettelem-e84.build.log 2>&1; echo "build rc=$?"
  fi
  ls -l "$ETT"; sha256sum "$ETT"
  for w in residency sptrace config sample; do grep -a -q -- "$w" "$ETT" && echo "  $ETT: $w present" || echo "  $ETT: $w MISSING"; done
  echo "== the plan"; python3 $K/run_e84.py --protocol $P --out "$OUT/runs/list" --list | tail -3
  echo "== dry run of SMOKE (no device)"
  rm -rf "${OUT:?}/runs/dry-smoke"
  python3 $K/run_e84.py --protocol $P --out "$OUT/runs/dry-smoke" --dry --only SMOKE > "$OUT/dry-smoke.log" 2>&1; echo "dry rc=$?"
  tail -2 "$OUT/dry-smoke.log"
  df -h /home | tail -1
  ;;
ident)
  f=$OUT/ident/ident-$(date +%H%M%S).out
  {
    ts; echo "== card 0's own lines in et-who (none expected)"; mycard; echo "== card 1's lines"; othercard
    echo "== ettelem config, card 0 (read only; card 0's lock held non-blocking)"
    flock -n /run/lock/etsoc-shire0.lock timeout 10 "$ETT" config < /dev/null; echo "rc=$?"
    echo "== ettelem uptime, card 0 (read only)"
    flock -n /run/lock/etsoc-shire0.lock timeout 10 "$ETT" uptime < /dev/null; echo "rc=$?"
    echo "== firmware revisions, card 0 (read only; the stock dev_mngt_service opens both cards' management nodes,"
    echo "   so both locks are held non-blocking for the one call)"
    flock -n /run/lock/etsoc-shire0.lock flock -n /run/lock/etsoc-shire1.lock \
      timeout 20 /opt/et/bin/dev_mngt_service -m DM_CMD_GET_MODULE_FIRMWARE_REVISIONS -n 0 -u 5000 < /dev/null 2>&1 \
      | grep -E 'revision|versions|succeeded|rror' | sed 's/^.*\]: //'
    echo "dev_mngt_service rc=${PIPESTATUS[0]}"
    echo "== et-who after"; mycard; othercard; ts
  } > "$f" 2>&1
  cat "$f"
  ;;
smoke)
  [ -e "$OUT/runs/smoke/session.json" ] && { echo "smoke already ran"; exit 0; }
  python3 $K/run_e84.py --protocol $P --out "$OUT/runs/smoke" --only SMOKE --max-card-min 5 > "$OUT/smoke.log" 2>&1
  echo "smoke rc=$?"; tail -12 "$OUT/smoke.log"
  ;;
go)
  [ -e "$OUT/runs/s1/session.json" ] && { echo "s1 already started"; exit 0; }
  setsid nohup python3 $K/run_e84.py --protocol $P --out "$OUT/runs/s1" > "$OUT/s1.log" 2>&1 < /dev/null &
  echo "E84 session started: pid $!, log $OUT/s1.log"
  ;;
status)
  tail -6 "$OUT/s1.log" 2>/dev/null
  printf 'runs done: %s\n' "$(grep -c . "$OUT/runs/s1/runs.jsonl" 2>/dev/null)"
  [ -e "$OUT/runs/s1/end.json" ] && cat "$OUT/runs/s1/end.json"; echo
  ;;
wait)
  t=0; while [ ! -e "$OUT/runs/s1/end.json" ] && [ $t -lt 530 ]; do sleep 10; t=$((t + 10)); done
  tail -4 "$OUT/s1.log" 2>/dev/null
  printf 'runs done: %s; ended: %s\n' "$(grep -c . "$OUT/runs/s1/runs.jsonl" 2>/dev/null)" "$([ -e "$OUT/runs/s1/end.json" ] && cat "$OUT/runs/s1/end.json" || echo no)"
  ;;
final)
  f=$OUT/ident/final-$(date +%H%M%S).out
  {
    ts; echo "== our E84 processes"; pgrep -u "$USER" -f run_e84.py | wc -l
    echo "== card 0's own lines in et-who"; mycard; echo "== card 1's lines"; othercard
    echo "== ettelem config, card 0 (read only)"
    flock -n /run/lock/etsoc-shire0.lock timeout 10 "$ETT" config < /dev/null; echo "rc=$?"
    echo "== et-who after"; mycard; othercard; df -h /home | tail -1; ts
  } > "$f" 2>&1
  cat "$f"
  ;;
*) echo "unknown stage $stage" >&2; exit 2 ;;
esac

# --- Dated note, Mon 2 Nov 2026 (week 45), added by Q136(w), the write-command audit, without editing any line above ---
# Lines 62-67 send DM_CMD_GET_MODULE_FIRMWARE_REVISIONS, and the echo at line 62 calls it "read only". It is not a read.
# At et-platform 836a4ab (BL2 0.22.0, the build all four lab cards report) its handler writes the PMIC's
# firmware-management command register twice, ACTIVE_SLOT then VERSION, and reads the data register after each
# (device-bootloaders/src/ServiceProcessorBL2/services/firmware_update.c:903 -> driver/pmic_controller.c:952-974,
# # the two writes at :2543 and :2587): a PMIC command by E85 C1's standard. E84 sent it once, on aifoundry1 card 0 at 15:42:00 PDT on
# 31 Oct 2026 (docs/reports/data/2026-10-31-e84-speed-aifoundry1-card0/ident/ident-154200.out); the card answered normally.
# Under the owner's rules of 2 Nov 2026 (AGENT.md section 5) every device command a run can send is classified before its
# first launch, and a write outside the allowed statistics reset is NO-GO. So do not reuse this script as it stands:
# python3 tools/claims-v3/dmcmd_audit.py tools/claims-v3/kspeed/e84/run_e84.sh lists line 64 as a WRITE (NO-GO). Take a
# card's identity from its module uptime (DM_CMD_GET_MODULE_UPTIME, service-processor RAM) against its last committed
# revisions read instead (E77, E118, E120). The audit: docs/reports/data/2026-11-02-q136w-write-audit/README.md.
