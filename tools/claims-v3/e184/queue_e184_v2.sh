#!/usr/bin/env bash
# E184 (Q153), kit v2 (KIT.md.dated-note-1.md section 5): queue_e184.sh (v1, which stays as committed) with two changes: the blocks are
# block_e184s_v2.sh and block_e184b_v2.sh, and a pass that ends "partial" (rc 7: the clock held and at least half its items read) does not
# stop the queue (the verifier's fault 11; reduce_e184_v2.py keeps a partial pass's readable quads, E180's rule). The rest is v1's:
# E184 (Q153, the kit): an arm's registered passes in plan-e184.json's order, after the stop-path test and the smoke gate (session_e184.sh).
# tools/claims-v3/e180/queue_e180_v2.sh's form (the budget anchored on the session's T0):
#   1. E184_ARM=S: 18410 18411 18412 18413 18414 18415 18416 18417 18418 (budget 8,100 s: the 135 card-minute cap), each block_e184s.sh;
#      E184_ARM=B: 18440 18441 18442 18443 18444 (budget 1,500 s: the 25 card-minute cap), each block_e184b.sh (V3_DEVICE=1);
#   2. an item starts only if now + projected <= E184_T0 + the budget - E184_RESERVE_S (60 s, the closing config read inside the budget)
#      and now + projected <= E184_DEADLINE (required); projected is the plan's estimate for that pass (plan-e184.json est_s) times the
#      largest ratio of measured to planned time over the passes run so far (1 before the first), plus 60 s;
#   3. it stops at the first item that does not fit (nothing is skipped ahead), before the next item on build/e184/STOP or
#      build/claims-v3/STOP, and after any item that does not end ok (rc 3 another user or device process; rc 5 a live stop; rc 1 the
#      block failed): never retried. So the scan's passes, last in arm S, are the first a budget cuts.
#   E184_T0=<epoch> E184_DEADLINE='<date>' E184_ARM=S|B bash tools/claims-v3/e184/queue_e184_v2.sh > build/e184/queue-<arm>-t<T0>.out 2>&1 < /dev/null
# SPDX-License-Identifier: Apache-2.0
set -u
cd "$(dirname "${BASH_SOURCE[0]}")/../../.."
T0=${E184_T0:?E184_T0 - the session anchor, epoch seconds}
DL=${E184_DEADLINE:?E184_DEADLINE - the latest end of any item, a date string}
ARM=${E184_ARM:?E184_ARM - S or B}
case "$ARM" in
  S) SEQ="18410 18411 18412 18413 18414 18415 18416 18417 18418"; BUDGET_S=8100; BLOCK=tools/claims-v3/e184/block_e184s_v2.sh; unset V3_DEVICE ;;
  B) SEQ="18440 18441 18442 18443 18444"; BUDGET_S=1500; BLOCK=tools/claims-v3/e184/block_e184b_v2.sh; export V3_DEVICE=1 ;;
  *) echo "E184_ARM=$ARM: only S or B"; exit 2 ;;
esac
SEQ=${E184_SEQ:-$SEQ}                # E184_SEQ, E184_BUDGET_S, E184_BLOCK, E184_EST_S and E184_MARGIN_S exist only for the dry pass's stub test
BUDGET_S=${E184_BUDGET_S:-$BUDGET_S}; RESERVE_S=${E184_RESERVE_S:-60}; GAP_S=${E184_GAP_S:-10}
BLOCK=${E184_BLOCK:-$BLOCK}
limit=$((T0 + BUDGET_S - RESERVE_S))
deadline=$(date -d "$DL" +%s) || { echo "E184_DEADLINE '$DL' is not a date"; exit 2; }
rel() { echo "T0+$(( $1 - T0 )) s"; }
MARGIN_S=${E184_MARGIN_S:-60}
est_of() { [ -n "${E184_EST_S:-}" ] && { echo "$E184_EST_S"; return; }
  python3 -c 'import json,sys; p=json.load(open("tools/claims-v3/e184/plan-e184.json")); print([q["est_s"] for a in ("arm_S","arm_B") for q in p[a]["passes"] if q["pass"]==int(sys.argv[1])][0])' "$1"; }
ratio=1.0
mkdir -p build/e184
echo "$(date +%T) e184 arm $ARM: items ${SEQ}; budget ${BUDGET_S} s from the anchor ($(date -d @"$T0" +%T)), reserve ${RESERVE_S} s, last end $(date -d @"$limit" +%T), deadline $(date -d @"$deadline" '+%F %T')"
n=0
for p in $SEQ; do
  if [ -e build/e184/STOP ] || [ -e build/claims-v3/STOP ]; then echo "$(date +%T) STOP: stopping before p$p"; break; fi
  plan_s=$(est_of "$p") || { echo "no estimate for p$p"; break; }
  est=$(python3 -c 'import math,sys; print(int(math.ceil(float(sys.argv[1]) * float(sys.argv[2]))) + int(sys.argv[3]))' "$plan_s" "$ratio" "$MARGIN_S")
  now=$(date +%s)
  if [ $((now + est)) -gt "$limit" ] || [ $((now + est)) -gt "$deadline" ]; then
    echo "$(date +%T) budget: stopping before p$p (now $(rel "$now"), projected ${est} s, would end $(rel $((now + est))) > $(rel "$limit") or the deadline)"
    break
  fi
  echo "$(date +%T) p$p starts at $(rel "$now") (projected ${est} s)"
  t0=$(date +%s)
  bash "$BLOCK" "$p" < /dev/null; rc=$?
  d=$(( $(date +%s) - t0 ))
  echo "$(date +%T) p$p rc=$rc ($d s)"
  ratio=$(python3 -c 'import sys; print(max(float(sys.argv[1]), float(sys.argv[2]) / max(1.0, float(sys.argv[3]))))' "$ratio" "$d" "$plan_s")
  if [ "$rc" -eq 7 ]; then
    echo "$(date +%T) p$p partial (rc 7): its readable items are kept; the queue goes on (kit v2)"
  elif [ "$rc" -ne 0 ]; then
    echo "$(date +%T) stopping after p$p (rc $rc)"; break
  fi
  n=$((n + 1))
  sleep "$GAP_S"
done
echo "$(date +%T) e184 arm $ARM: done, $n items, at $(rel "$(date +%s)")"
