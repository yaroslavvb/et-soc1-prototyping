#!/usr/bin/env bash
# E182 (Q153, the kit): the registered blocks on aifoundry3 card 0, run by session_e182.sh after the stop-path test and the smoke gate have
# passed. A copy of tools/claims-v3/e178/queue_e178.sh (the budget anchored on the session's T0), each change marked E182:
#   1. the plan (E182_PLAN, E182.md section 7): FULL = the six trains in plan-e182.json's order (18210-18215: T4, T5, T3, T6, T2, T1),
#      then the kinds passes 18220 18221 18222, and 18223 only if the budget rule admits it (budget 6,000 s: the 100 card-minute cap);
#      PASSES = 18220 18221 18222 (2,400 s: the 40 card-minute cap), the trains' fallback when the train smoke fails; each item
#      block_e182.sh;
#   2. the budget: an item starts only if now + projected <= E182_T0 + the plan's budget - E182_RESERVE_S (60 s, the closing config read
#      inside the budget) and now + projected <= E182_DEADLINE (required: set at his go from the round's time gate); projected is the
#      first estimate by kind (a train: plan-e182.json's est_s for that block plus 30 s, or the longest train measured if longer; a kinds
#      pass 640 s, E178's measured 8.23 s a run over 70 runs plus its first-pass heat, until a pass ends, then the longest measured);
#      exact integer seconds;
#   3. it stops at the first item that does not fit (nothing is skipped ahead), before the next item on build/e182/STOP or
#      build/claims-v3/STOP, and after any item that fails (rc 3 = another user on the card or a device process; rc 1 = the block
#      failed, a registered stop included: never retried).
# An item in flight is never cut. No item is added after any reduction is read. Nothing is set.
#
#   E182_T0=<anchor epoch> E182_DEADLINE='<date>' [E182_PLAN=FULL|PASSES] bash tools/claims-v3/e182/queue_e182.sh > build/e182/queue.out 2>&1 < /dev/null
set -u
cd "$(dirname "${BASH_SOURCE[0]}")/../../.."
unset V3_DEVICE
T0=${E182_T0:?E182_T0 - the session anchor, epoch seconds}
DL=${E182_DEADLINE:?E182_DEADLINE - the latest end of any item, from the time gate of the round, a date string}
PLAN=${E182_PLAN:-FULL}
TRAIN_SEQ=$(python3 -B -c 'import json,sys; print(" ".join(str(t["block"]) for t in json.load(open(sys.argv[1]))["trains"]))' tools/claims-v3/e182/plan-e182.json) ||
  { echo "plan-e182.json unreadable"; exit 2; }
case "$PLAN" in
  FULL)   SEQ="$TRAIN_SEQ 18220 18221 18222 18223"; BUDGET_S=6000 ;;
  PASSES) SEQ="18220 18221 18222"; BUDGET_S=2400 ;;
  *) echo "E182_PLAN=$PLAN: only FULL or PASSES"; exit 2 ;;
esac
SEQ=${E182_SEQ:-$SEQ}                # E182_SEQ exists only for the stub self-test (dry_intel_e182.sh); session_e182.sh never sets it
BUDGET_S=${E182_BUDGET_S:-$BUDGET_S}; RESERVE_S=${E182_RESERVE_S:-60}; GAP_S=${E182_GAP_S:-10}
BLOCK=${E182_BLOCK:-tools/claims-v3/e182/block_e182.sh}      # E182_BLOCK exists only for the stub self-test
limit=$((T0 + BUDGET_S - RESERVE_S))
deadline=$(date -d "$DL" +%s) || { echo "E182_DEADLINE '$DL' is not a date"; exit 2; }
kind() { case "$1" in 1822[0-9]) echo kinds ;; 1821[0-5]) echo train ;; *) echo other ;; esac; }
train_est() { python3 -B -c 'import json,sys; print(int(next(t["est_s"] for t in json.load(open(sys.argv[1]))["trains"] if t["block"] == int(sys.argv[2]))) + 30)' tools/claims-v3/e182/plan-e182.json "$1"; }
est_kinds=${E182_FIRST_KINDS_S:-640}; est_train=; est_other=1000000
seen_kinds=0; seen_train=0; seen_other=0
rel() { echo "T0+$(( $1 - T0 )) s"; }
mkdir -p build/e182
echo "$(date +%T) e182: plan $PLAN, items ${SEQ}; budget ${BUDGET_S} s from the anchor ($(date -d @"$T0" +%T)), reserve ${RESERVE_S} s, last end $(date -d @"$limit" +%T), deadline $(date -d @"$deadline" '+%F %T'); first estimate kinds ${est_kinds} s, trains by plan-e182.json"
n=0
for p in $SEQ; do
  if [ -e build/e182/STOP ] || [ -e build/claims-v3/STOP ]; then echo "$(date +%T) STOP: stopping before p$p"; break; fi
  k=$(kind "$p")
  if [ "$k" = train ]; then   # E182: a train's projection is its own plan estimate, or the longest train measured if longer
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
  if [ "$k" = train ]; then { [ -z "$est_train" ] || [ "$d" -gt "$est_train" ]; } && est_train=$d   # E182: the longest train measured
  elif [ "$seen" -eq 0 ] || [ "$d" -gt "$proj" ]; then eval "est_$k=$d"; fi   # the first estimate holds until an item of its kind ends
  eval "seen_$k=1"
  n=$((n + 1))
  sleep "$GAP_S"
done
echo "$(date +%T) e182: done, $n items, at $(rel "$(date +%s)")"
