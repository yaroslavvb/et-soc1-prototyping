#!/usr/bin/env bash
# E186 (Q158, the kit): the registered blocks on aifoundry3 card 0, run by session_e186.sh after the stop-path test and the smoke gate have
# passed. A copy of tools/claims-v3/e182/queue_e182.sh (E182's, run on this card on 8 Nov 2026: the budget anchored on the session's T0),
# each change marked E186:
#   1. the plan (E186_PLAN, E186.md section 7): FULL = the ten trains in plan-e186.json's order (18610-18619: H16, S23, Q63-sign,
#      Q63-swap, B15-B7, B23-B15, Q3-sign, Q3-swap, A15-A7, A23-A15; rank order, so a budget stop drops the lowest-ranked) and NO kinds pass
#      (budget 6,000 s: the 100 card-minute cap); PASSES = 18620 18621 18622 18623 18624 (2,400 s: the 40 card-minute cap), the trains'
#      fallback when the train host's build or the smoke's train gate fails; each item block_e186.sh;
#   2. the budget: an item starts only if now + projected <= E186_T0 + the plan's budget - E186_RESERVE_S (60 s, the closing config read
#      inside the budget) and now + projected <= E186_DEADLINE (required: set at his go from the window's last end); projected is the
#      first estimate by kind (a train: plan-e186.json's est_s for that block plus 30 s, or the longest train measured if longer, E182's
#      rule; E186: a kinds pass plan-e186.json's fallback_pass_s, 304.5 s, plus 30 s until a pass ends, then the longest measured, the same
#      rule, since E182's 640 s was a 70-run pass's and E186's fallback pass is 35 runs and two burn-ins); exact integer seconds;
#   3. it stops at the first item that does not fit (nothing is skipped ahead), before the next item on build/e186/STOP or
#      build/claims-v3/STOP, and after any item that fails (rc 3 = another user on the card or a device process; rc 1 = the block
#      failed, a registered stop included: never retried).
# An item in flight is never cut. No item is added after any reduction is read. Nothing is set.
#
#   E186_T0=<anchor epoch> E186_DEADLINE='<date>' [E186_PLAN=FULL|PASSES] bash tools/claims-v3/e186/queue_e186.sh > <session dir>/queue.out 2>&1 < /dev/null
# SPDX-License-Identifier: Apache-2.0
set -u
cd "$(dirname "${BASH_SOURCE[0]}")/../../.."
unset V3_DEVICE
T0=${E186_T0:?E186_T0 - the session anchor, epoch seconds}
DL=${E186_DEADLINE:?E186_DEADLINE - the latest end of any item, from the window of his go, a date string}
PLAN=${E186_PLAN:-FULL}
P=tools/claims-v3/e186/plan-e186.json
TRAIN_SEQ=$(python3 -B -c 'import json,sys; print(" ".join(str(t["block"]) for t in json.load(open(sys.argv[1]))["trains"]))' "$P") ||
  { echo "plan-e186.json unreadable"; exit 2; }
PASS_SEQ=$(python3 -B -c 'import json,sys; print(" ".join(str(p) for p in sorted(int(x) for x in json.load(open(sys.argv[1]))["fallback_kinds_passes"])))' "$P") ||
  { echo "plan-e186.json unreadable"; exit 2; }
case "$PLAN" in
  FULL)   SEQ="$TRAIN_SEQ"; BUDGET_S=6000 ;;                                                                  # E186 change 1: no kinds pass
  PASSES) SEQ="$PASS_SEQ"; BUDGET_S=2400 ;;
  *) echo "E186_PLAN=$PLAN: only FULL or PASSES"; exit 2 ;;
esac
SEQ=${E186_SEQ:-$SEQ}                # E186_SEQ exists only for the stub self-test (dry_intel_e186.sh); session_e186.sh never sets it
BUDGET_S=${E186_BUDGET_S:-$BUDGET_S}; RESERVE_S=${E186_RESERVE_S:-60}; GAP_S=${E186_GAP_S:-10}
BLOCK=${E186_BLOCK:-tools/claims-v3/e186/block_e186.sh}      # E186_BLOCK exists only for the stub self-test
limit=$((T0 + BUDGET_S - RESERVE_S))
deadline=$(date -d "$DL" +%s) || { echo "E186_DEADLINE '$DL' is not a date"; exit 2; }
kind() { case "$1" in 1862[0-9]) echo kinds ;; 1861[0-9]) echo train ;; *) echo other ;; esac; }
train_est() { python3 -B -c 'import json,sys; print(int(next(t["est_s"] for t in json.load(open(sys.argv[1]))["trains"] if t["block"] == int(sys.argv[2]))) + 30)' "$P" "$1"; }
pass_est=$(python3 -B -c 'import json,math,sys; print(math.ceil(json.load(open(sys.argv[1]))["fallback_pass_s"]) + 30)' "$P") ||
  { echo "plan-e186.json unreadable"; exit 2; }
est_kinds=${E186_FIRST_KINDS_S:-$pass_est}; est_train=; est_other=1000000
seen_kinds=0; seen_train=0; seen_other=0
rel() { echo "T0+$(( $1 - T0 )) s"; }
mkdir -p build/e186
echo "$(date +%T) e186: plan $PLAN, items ${SEQ}; budget ${BUDGET_S} s from the anchor ($(date -d @"$T0" +%T)), reserve ${RESERVE_S} s, last end $(date -d @"$limit" +%T), deadline $(date -d @"$deadline" '+%F %T'); first estimate kinds ${est_kinds} s, trains by plan-e186.json"
n=0
for p in $SEQ; do
  if [ -e build/e186/STOP ] || [ -e build/claims-v3/STOP ]; then echo "$(date +%T) STOP: stopping before p$p"; break; fi
  k=$(kind "$p")
  if [ "$k" = train ]; then   # E182's rule: a train's projection is its own plan estimate, or the longest train measured if longer
    proj=$(train_est "$p") || { echo "no estimate for train $p"; break; }
    [ -n "$est_train" ] && [ "$est_train" -gt "$proj" ] && proj=$est_train
  else eval "proj=\$est_$k"; fi
  now=$(date +%s)
  if [ $((now + proj)) -gt "$limit" ] || [ $((now + proj)) -gt "$deadline" ]; then
    echo "$(date +%T) budget: stopping before p$p ($k; now $(rel "$now"), projected ${proj} s, would end $(rel $((now + proj))) > $(rel "$limit") or the deadline)"
    break
  fi
  echo "$(date +%T) p$p ($k) starts at $(rel "$now") (projected ${proj} s)"
  t0=$(date +%s)
  bash "$BLOCK" "$p" < /dev/null; rc=$?
  d=$(( $(date +%s) - t0 ))
  echo "$(date +%T) p$p rc=$rc ($d s)"
  [ "$rc" -eq 0 ] || { echo "$(date +%T) stopping after p$p (rc $rc)"; break; }
  eval "seen=\$seen_$k"
  if [ "$k" = train ]; then { [ -z "$est_train" ] || [ "$d" -gt "$est_train" ]; } && est_train=$d   # the longest train measured
  elif [ "$seen" -eq 0 ] || [ "$d" -gt "$proj" ]; then eval "est_$k=$d"; fi   # the first estimate holds until an item of its kind ends
  eval "seen_$k=1"
  n=$((n + 1))
  sleep "$GAP_S"
done
echo "$(date +%T) e186: done, $n items, at $(rel "$(date +%s)")"
