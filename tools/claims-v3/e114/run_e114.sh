#!/usr/bin/env bash
# E114 (Q133) on aifoundry1 card 0, one stage per call. E84's stage script (tools/claims-v3/kspeed/e84/run_e84.sh) with
# E114's protocol, its own output folder (build/e114), the firmware read under `timeout 10` (E84's correction C5), and a
# `start` stage that chains ident -> checks -> smoke -> checks -> go. Run it from ~/nekko after copying
# tools/claims-v3/e114/ there from the freeze commit (the tree has no git: E114_FREEZE names the commit):
#
#   bash tools/claims-v3/e114/run_e114.sh setup     # NO device access: tree, hashes, tiles, the plan, a dry SMOKE
#   bash tools/claims-v3/e114/run_e114.sh start     # AFTER the claim: ident, then the smoke only if the start read is
#                                                   # E84's (65 W / 65 C, release 1.4.0 / BL2 0.22.0 / PMIC 1.6.1),
#                                                   # then the session (detached) only if the smoke passed its checks
#   bash tools/claims-v3/e114/run_e114.sh status    # the session log and its progress
#   bash tools/claims-v3/e114/run_e114.sh wait      # one bounded wait (<= 9 min) for the session to end
#   bash tools/claims-v3/e114/run_e114.sh final     # read-only closing reads, after the session
#
# Every device process goes through E84's runner, tools/claims-v3/kspeed/e84/run_e84.py, unchanged (the card lock,
# `timeout 10` on every launch, the other-user test on both cards, the configuration check after every run, the sampler
# without --reset-ms), or, in ident and final, through `timeout 10` with the card's lock held non-blocking. Nothing is
# written to the card: no TDP, threshold, clock, voltage, governor, reset or PMIC command.
set -u
cd "$(dirname "${BASH_SOURCE[0]}")/../../.."
ROOT=$PWD
export V3_DEVICE=0 ET_DEVICES=0 LD_LIBRARY_PATH=/opt/et/lib
export E114_FREEZE=${E114_FREEZE:-unset}
export E84_FREEZE=$E114_FREEZE          # run_e84.py writes it into the session's e84.json
[ "$(hostname)" = aifoundry1 ] || { echo "E114 runs on aifoundry1 only (this is $(hostname))" >&2; exit 2; }
K=tools/claims-v3/e114
RUNNER=tools/claims-v3/kspeed/e84/run_e84.py
P=$K/protocol.json
OUT=$ROOT/build/e114
ETT=build/ettelem-e84/ettelem
mkdir -p "$OUT/runs" "$OUT/ident"
stage=${1:?setup|start|status|wait|final}
ts() { date '+%F %T %Z'; }
mycard() { et-who 2>&1 | awk '$1 ~ /^\/dev\/et0_/ || $1 ~ /^lock:etsoc-shire0\.lock/' | awk '{print $1, ($2==ENVIRON["USER"]?"me":"other")}'; }
othercard() { et-who 2>&1 | awk '$1 ~ /^\/dev\/et1_/ || $1 ~ /^lock:etsoc-shire1\.lock/' | awk '{print $1, ($2==ENVIRON["USER"]?"me":"other")}'; }
hashes() {
  sha256sum tools/claims-v3/hpl/run_hpl.py tools/claims-v3/hpl/reduce_hpl.py tools/claims-v3/kspeed/run_kspeed.py \
    $RUNNER tools/claims-v3/kspeed/e84/reduce_e84.py $P $K/predictions-e114.json $K/reduce_e114.py $K/run_e114.sh \
    tools/claims-v3/kinds/kinds.json build/sparsity/host/sparsity_host build/sparsity/kernel/sparsity.elf "$ETT"
}

ident() {
  f=$OUT/ident/ident-$(date +%H%M%S).out
  {
    ts; echo "== card 0's own lines in et-who (none expected)"; mycard; echo "== card 1's lines"; othercard
    echo "== ettelem config, card 0 (read only; card 0's lock held non-blocking)"
    flock -n /run/lock/etsoc-shire0.lock timeout 10 "$ETT" config < /dev/null; echo "rc=$?"
    echo "== ettelem uptime, card 0 (read only)"
    flock -n /run/lock/etsoc-shire0.lock timeout 10 "$ETT" uptime < /dev/null; echo "rc=$?"
    echo "== firmware revisions, card 0 (read only; the stock dev_mngt_service opens both cards' management nodes,"
    echo "   so both locks are held non-blocking for the one call; timeout 10 with its own 5,000 ms reply timeout)"
    flock -n /run/lock/etsoc-shire0.lock flock -n /run/lock/etsoc-shire1.lock \
      timeout 10 /opt/et/bin/dev_mngt_service -m DM_CMD_GET_MODULE_FIRMWARE_REVISIONS -n 0 -u 5000 < /dev/null 2>&1 \
      | grep -E 'revision|versions|succeeded|rror' | sed 's/^.*\]: //'
    echo "dev_mngt_service rc=${PIPESTATUS[0]}"
    echo "== et-who after"; mycard; othercard; ts
  } > "$f" 2>&1
  cat "$f"
  IDENT_FILE=$f
}

case "$stage" in
setup)
  ts; hostname; uptime
  echo "== card 0's own lines in et-who (none expected)"; mycard
  echo "== card 1's lines in et-who"; othercard
  echo "== device processes or CI workers (count)"; ps -eo uid=,comm= | grep -c -E '_host$|ettelem$|dev_mngt_servi|et-powertop$|mmbench_launch|sys_emu$|Runner.Worker$'
  echo "== tree"; echo "root $ROOT, E114_FREEZE=$E114_FREEZE"
  hashes
  ls -l "$ETT"
  for w in residency sptrace config sample; do grep -a -q -- "$w" "$ETT" && echo "  $ETT: $w present" || echo "  $ETT: $w MISSING"; done
  echo "== the plan"; python3 $RUNNER --protocol $P --out "$OUT/runs/list" --list --only SUS | tail -16
  python3 $RUNNER --protocol $P --out "$OUT/runs/list" --list --only SMOKE | tail -3
  echo "== dry run of SMOKE (no device)"
  rm -rf "${OUT:?}/runs/dry-smoke"
  python3 $RUNNER --protocol $P --out "$OUT/runs/dry-smoke" --dry --only SMOKE > "$OUT/dry-smoke.log" 2>&1; echo "dry rc=$?"
  tail -2 "$OUT/dry-smoke.log"
  df -h /home | tail -1
  ;;
start)
  [ -e "$OUT/runs/s1/session.json" ] && { echo "s1 already started"; exit 0; }
  ident
  if ! grep -q '"tdp_w":65,"temp_threshold_c":65' "$IDENT_FILE"; then echo "STOP: the start read is not 65 W / 65 C (see $IDENT_FILE)"; exit 3; fi
  for want in 'Firmware release revision: Major: 1 Minor: 4 Revision: 0' 'BL2 Firmware versions: Major: 0 Minor: 22 Revision: 0' \
              'PMIC Firmware versions: Major: 1 Minor: 6 Revision: 1'; do
    grep -q "$want" "$IDENT_FILE" || { echo "STOP: firmware differs from E84's read: missing '$want' (see $IDENT_FILE)"; exit 3; }
  done
  echo "== start read is E84's; the smoke"
  if [ ! -e "$OUT/runs/smoke/session.json" ]; then
    python3 $RUNNER --protocol $P --out "$OUT/runs/smoke" --only SMOKE --max-card-min 5 > "$OUT/smoke.log" 2>&1
    echo "smoke rc=$?"; tail -8 "$OUT/smoke.log"
  fi
  python3 - "$OUT/runs/smoke" <<'PY' || { echo "STOP: the smoke failed its checks; no session"; exit 4; }
import gzip, json, os, sys
rd = sys.argv[1]
end = json.load(open(os.path.join(rd, "end.json")))
runs = [json.loads(l) for l in open(os.path.join(rd, "runs.jsonl"))]
bad = []
if end.get("exit") != 0:
    bad.append(f"exit {end.get('exit')} {end.get('reason')}")
if len(runs) != 2:
    bad.append(f"{len(runs)} smoke runs, not 2")
for r in runs:
    if any(L.get("rc") != 0 for L in r.get("launches", [])) or not r.get("launches"):
        bad.append(f"{r['run']}: a launch rc != 0")
    cfg = (r.get("queries") or {}).get("config") or {}
    if cfg.get("tdp_w") != 65 or cfg.get("temp_threshold_c") != 65:
        bad.append(f"{r['run']}: config {cfg}")
print("smoke checks:", "ok" if not bad else "; ".join(bad))
sys.exit(1 if bad else 0)
PY
  {
    echo "{\"experiment\": \"E114\", \"freeze_commit\": \"$E114_FREEZE\", \"started\": \"$(ts)\", \"sha256\": {"
    hashes | awk '{printf "%s\"%s\": \"%s\"", (NR>1?", ":""), $2, $1} END {print "}}"}'
  } > "$OUT/e114-start.json"
  setsid nohup python3 $RUNNER --protocol $P --out "$OUT/runs/s1" > "$OUT/s1.log" 2>&1 < /dev/null &
  echo "E114 session started: pid $!, log $OUT/s1.log, $(ts)"
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
    ts; echo "== our E114 processes"; pgrep -u "$USER" -f run_e84.py | wc -l
    echo "== card 0's own lines in et-who"; mycard; echo "== card 1's lines"; othercard
    echo "== ettelem config, card 0 (read only)"
    flock -n /run/lock/etsoc-shire0.lock timeout 10 "$ETT" config < /dev/null; echo "rc=$?"
    echo "== et-who after"; mycard; othercard; df -h /home | tail -1; ts
  } > "$f" 2>&1
  cat "$f"
  ;;
*) echo "unknown stage $stage" >&2; exit 2 ;;
esac
