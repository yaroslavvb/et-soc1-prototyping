#!/usr/bin/env bash
# 1119-mmsweep4: the dry mode: one card's whole session with the doubles (src/fake_card_mms.py), every device call printed and
# kept in device-calls.txt, no device node opened, no card lock taken (a stand-in lock in the dry folder), time scaled.
#   bash ~/claude/work/ee-1119-mmsweep4/src/dry_mms.sh <card> <S1..S9> [scale]    (default scale 0.02: an hour-long session in ~2 min)
# Writes dry/<T0>-<card>-<S>/ in the kit's folder; prints the session's last lines, the count of device calls and DRY PASS
# when the session ran its whole schedule (every run started, every process rc 0 with its check exact or approx, the null
# runs with none) and wrote its manifest. Refused (DRY REFUSED, exit 3) while the kit's box lock run/box.lock is held (a
# session, a build or another dry pass of the kit), or while any card of this box is held or measured, or a CI job runs: no
# host compute beside a card run. It holds run/box.lock itself from its first check to its end, so no session of the kit
# starts beside it.
# SPDX-License-Identifier: Apache-2.0
set -u
cd "$(dirname "${BASH_SOURCE[0]}")/.." || exit 2
CARD=${1:-}; S=${2:-}; SCALE=${3:-0.02}
case "$CARD" in a2c0|a1c1|a1c0) ;; *) echo "usage: dry_mms.sh a2c0|a1c1|a1c0 S1..S9 [scale]"; exit 2 ;; esac
case "$S" in S[1-9]) ;; *) echo "usage: dry_mms.sh <card> S1..S9 [scale]"; exit 2 ;; esac
[ -f "src/sched/$CARD-$S.json" ] || { echo "no schedule src/sched/$CARD-$S.json"; exit 2; }
# No host compute beside a card run (the lab's rule): refused unless et-who --check reads every card of this box free and no
# device process (anyone's) and no CI job runs here.
quiet_box() {
  local chk=9 devn cin
  if command -v et-who > /dev/null 2>&1; then timeout 20 et-who --check > /dev/null 2>&1; chk=$?; fi
  devn=$(ps -eo comm= | grep -Ec '(_host$|^ettelem$|^dev_mngt_servi|^et-powertop$|^mmbench_launch|^sys_emu$)')
  cin=$(ps -eo comm= | grep -c '^Runner\.Worker$')
  if [ "$chk" -ne 0 ] || [ "$devn" -ne 0 ] || [ "$cin" -ne 0 ]; then
    echo "a card of this box is held or measured, or a CI job runs (et-who --check rc $chk: 0 free, 1 held, 2 failed, 9 no et-who; device processes $devn; CI jobs $cin)"
    return 1
  fi
  return 0
}
mkdir -p run
exec 9>>run/box.lock    # held (fd 9) until this script ends
if ! flock -n 9; then echo "DRY REFUSED: run/box.lock is held (a session, a build or a dry pass of this kit runs on this box)"; exit 3; fi
WHY=$(quiet_box) || { echo "DRY REFUSED: $WHY"; exit 3; }
T0=$(date +%s)
OUT=dry/$T0-$CARD-$S
mkdir -p "$OUT"
nice -n 10 python3 -B src/run_mms.py session --dry --scale "$SCALE" --card "$CARD" --sched "src/sched/$CARD-$S.json" \
  --t0 "$T0" --out "$OUT" > "$OUT/runner.out" 2>&1 < /dev/null
RC=$?
tail -n 4 "$OUT/session.log"
python3 -B - "$OUT" "$CARD" "$S" "$RC" <<'PY'
import json, os, sys
out, card, s, rc = sys.argv[1], sys.argv[2], sys.argv[3], int(sys.argv[4])
q = json.load(open(os.path.join(out, "queue.json")))
sched = json.load(open(os.path.join("src", "sched", f"{card}-{s}.json")))
calls = open(os.path.join(out, "device-calls.txt")).read().splitlines()
ran = [x for x in q["queue"] if x.get("ran")]
bad = [x for x in q["queue"] if not x.get("ran") or (x.get("form") != "null" and (not x.get("rcs") or any(r != 0 for r in x["rcs"])
       or any(c not in ("exact", "approx") for c in x.get("checks") or [None])))]
print(f"device calls {len(calls)} (config {sum(1 for c in calls if c.endswith(' config'))}, sampler "
      f"{sum(1 for c in calls if ' sample ' in c)}, host {sum(1 for c in calls if 'sparsity_host' in c)}); runs ran {len(ran)} of "
      f"{len(sched['runs'])} ({sum(1 for x in ran if x.get('form') == 'null')} null); card-minutes (unscaled) {q.get('card_min')}; "
      f"stop {q.get('stop')}")
ok = rc == 0 and not bad and len(ran) == len(sched["runs"]) and os.path.exists(os.path.join(out, "MANIFEST.sha256"))
print(("DRY PASS " if ok else "DRY FAIL ") + f"{card} {s} (runner rc {rc}; {len(bad)} runs not clean)")
sys.exit(0 if ok else 1)
PY
