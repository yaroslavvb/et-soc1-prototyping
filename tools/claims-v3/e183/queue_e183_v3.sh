#!/usr/bin/env bash
# E183 (the kit's dated note 6, KIT.md.dated-note-6.md, Fri 13 Nov 2026, before any E183 train datum): the queue, v3. It is queue_e183_v2.sh
# (24b9b99e, which stays as committed) with ONE change, marked "note 6": each item runs block_e183_v3.sh (the post-block check on a train
# block only, the harness v3), not block_e183_v2.sh. The block is the queue's default, so the real session sets no variable the dry pass's
# stub test reads (E183_BLOCK stays the dry pass's alone). Its plans, budgets, gates, order and stops are v2's, line for line. Run by
# session_e183_v3.sh.
# v2's words follow:
# E183 (the kit's dated note 4, KIT.md.dated-note-4.md, Thu 12 Nov 2026, before any E183 datum): the queue, v2. It is queue_e183.sh
# (cc597bf2, which stays as committed) with ONE change: each item runs block_e183_v2.sh (the train change read from the host's behaviour,
# not grepped), not block_e183.sh. Its plans, budgets, gates, order and stops are v1's, line for line. Run by session_e183_v2.sh.
# v1's words follow:
# E183 (Q155, the kit): the registered train blocks on aifoundry3 card 0, run by session_e183.sh after the stop-path test and the smoke gate
# have passed. E180's queue v2 (queue_e180_v2.sh, the budget anchored on the session's T0), ported to E183's plan (E183.md section 7):
#   1. the plan (E183_PLAN): FULL 18310-18315 (T3, T1, T4, T6, T2, T5; budget 3,900 s: the 65 card-minute cap); SHORT 18310 18311 18312
#      18314 (T3, T1, T4, T2; 1,920 s, the 32 card-minute cap); each item block_e183.sh;
#   2. an item starts only if now + projected <= E183_T0 + the budget - E183_RESERVE_S (60 s, the closing config read inside the budget)
#      and now + projected <= E183_DEADLINE (required); projected is the block's plan estimate (plan-e183.json est_s) times the largest
#      ratio of measured to planned time among the blocks already ended (1 until one ends), plus 30 s; a block in flight is never cut;
#   3. it stops at the first item that does not fit (nothing is skipped ahead), before the next item on build/e183/STOP or
#      build/claims-v3/STOP, and after any item that does not end ok (rc 3 another user or a device process; rc 5 a live stop; rc 1 the
#      block failed): never retried.
# Nothing is set. No item is added after any reduction is read.
#
#   E183_T0=<anchor epoch> E183_DEADLINE='<date>' [E183_PLAN=FULL|SHORT] bash tools/claims-v3/e183/queue_e183.sh > <the session's queue file> 2>&1 < /dev/null
# SPDX-License-Identifier: Apache-2.0
set -u
cd "$(dirname "${BASH_SOURCE[0]}")/../../.."
unset V3_DEVICE
T0=${E183_T0:?E183_T0 - the session anchor, epoch seconds}
DL=${E183_DEADLINE:?E183_DEADLINE - the latest end of any item, a date string}
PLAN=${E183_PLAN:-FULL}
case "$PLAN" in
  FULL) SEQ="18310 18311 18312 18313 18314 18315"; BUDGET_S=3900 ;;
  SHORT) SEQ="18310 18311 18312 18314"; BUDGET_S=1920 ;;
  *) echo "E183_PLAN=$PLAN: only FULL or SHORT"; exit 2 ;;
esac
SEQ=${E183_SEQ:-$SEQ}                # E183_SEQ, E183_BUDGET_S, E183_GAP_S and E183_BLOCK exist only for the dry pass's stub test
BUDGET_S=${E183_BUDGET_S:-$BUDGET_S}; RESERVE_S=${E183_RESERVE_S:-60}; GAP_S=${E183_GAP_S:-10}
BLOCK=${E183_BLOCK:-tools/claims-v3/e183/block_e183_v3.sh}     # note 6: block v3
limit=$((T0 + BUDGET_S - RESERVE_S))
deadline=$(date -d "$DL" +%s) || { echo "E183_DEADLINE '$DL' is not a date"; exit 2; }
est_of() { python3 -c 'import json,sys; p=json.load(open("tools/claims-v3/e183/plan-e183.json")); print(int(round([t["est_s"] for t in p["trains"] if t["block"]==int(sys.argv[1])][0])))' "$1"; }
ratio=1000                           # the measured-to-planned ratio, in thousandths
rel() { echo "T0+$(( $1 - T0 )) s"; }
mkdir -p build/e183
echo "$(date +%T) e183: plan $PLAN, items ${SEQ}; budget ${BUDGET_S} s from the anchor ($(date -d @"$T0" +%T)), reserve ${RESERVE_S} s, last end $(date -d @"$limit" +%T), deadline $(date -d @"$deadline" '+%F %T')"
n=0
for p in $SEQ; do
  if [ -e build/e183/STOP ] || [ -e build/claims-v3/STOP ]; then echo "$(date +%T) STOP: stopping before p$p"; break; fi
  e=$(est_of "$p") || { echo "$(date +%T) p$p has no plan estimate: stopping"; break; }
  est=$(( e * ratio / 1000 + 30 ))
  now=$(date +%s)
  if [ $((now + est)) -gt "$limit" ] || [ $((now + est)) -gt "$deadline" ]; then
    echo "$(date +%T) budget: stopping before p$p (now $(rel "$now"), projected ${est} s, would end $(rel $((now + est))) > $(rel "$limit") or the deadline)"
    break
  fi
  echo "$(date +%T) p$p starts at $(rel "$now") (projected ${est} s: plan ${e} s x $((ratio / 10))% + 30 s)"
  t0=$(date +%s)
  bash "$BLOCK" "$p" < /dev/null; rc=$?
  d=$(( $(date +%s) - t0 ))
  echo "$(date +%T) p$p rc=$rc ($d s)"
  [ "$rc" -eq 0 ] || { echo "$(date +%T) stopping after p$p (rc $rc)"; break; }
  r=$(( d * 1000 / (e > 0 ? e : 1) ))
  [ "$r" -gt "$ratio" ] && ratio=$r
  n=$((n + 1))
  sleep "$GAP_S"
done
echo "$(date +%T) e183: done, $n items, at $(rel "$(date +%s)")"
