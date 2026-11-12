#!/usr/bin/env bash
# E188 (Q165, the kit): the registered blocks on aifoundry3 card 0, run by session_e188.sh after the stop-path test and the smoke gate have
# passed. A port of tools/claims-v3/e186/queue_e186.sh (E186's, run on this card on 9 Nov 2026; itself E182's: the budget anchored on the
# session's T0), each change marked E188:
#   1. the plan (E188_PLAN, E188.md section 6; plan-e188.json > plans): FULL = the first kinds pass 18820, the seven trains in
#      plan-e188.json's order (18810-18816: B05, PAIR, B19, AALL, B10, B22, B04), then the second kinds pass 18821 (budget 6,000 s: the
#      100 card-minute cap); PASSES = 18830 18831 18832 18833 18834 (2,400 s: the 40 card-minute cap), the trains' registered fallback when
#      the train host's build or the smoke's train gate fails; each item block_e188.sh;
#   2. the budget: an item starts only if now + projected <= E188_T0 + the plan's budget - E188_RESERVE_S (60 s, the closing config read
#      inside the budget) and now + projected <= E188_DEADLINE (required: set at his go from the window's last end); projected is the
#      first estimate by kind (a train: plan-e188.json's est_s for that block plus 30 s, or the longest train measured if longer, E182's
#      rule; a kinds pass: its plan's pass estimate plus 30 s - FULL's 44-run pass plan-e188.json's kinds_pass_s, 378.6 s, the fallback's
#      35-run pass fallback_pass_s, 304.5 s - until a pass ends, then the longest measured, the same rule); exact integer seconds. So
#      18821, last in FULL, starts only if its projected end fits the cap less the reserve and the deadline (E188.md section 6);
#   3. it stops at the first item that does not fit (nothing is skipped ahead), before the next item on build/e188/STOP or
#      build/claims-v3/STOP, and after any item that fails (rc 3 = another user on the card or a device process; rc 1 = the block
#      failed, a registered stop included: never retried).
# An item in flight is never cut. No item is added after any reduction is read. Nothing is set.
#
#   E188_T0=<anchor epoch> E188_DEADLINE='<date>' [E188_PLAN=FULL|PASSES] bash tools/claims-v3/e188/queue_e188.sh > <session dir>/queue.out 2>&1 < /dev/null
# SPDX-License-Identifier: Apache-2.0
set -u
cd "$(dirname "${BASH_SOURCE[0]}")/../../.."
unset V3_DEVICE
T0=${E188_T0:?E188_T0 - the session anchor, epoch seconds}
DL=${E188_DEADLINE:?E188_DEADLINE - the latest end of any item, from the window of his go, a date string}
PLAN=${E188_PLAN:-FULL}
P=tools/claims-v3/e188/plan-e188.json
seqof() { python3 -B -c 'import json,sys; print(" ".join(str(x) for x in json.load(open(sys.argv[1]))["plans"][sys.argv[2]]["sequence"] if isinstance(x, int)))' "$P" "$1"; }
case "$PLAN" in                                                                                               # E188 change 1
  FULL)   SEQ=$(seqof FULL) || { echo "plan-e188.json unreadable"; exit 2; }; BUDGET_S=6000
          pass_key=kinds_pass_s ;;
  PASSES) SEQ=$(seqof PASSES) || { echo "plan-e188.json unreadable"; exit 2; }; BUDGET_S=2400
          pass_key=fallback_pass_s ;;
  *) echo "E188_PLAN=$PLAN: only FULL or PASSES"; exit 2 ;;
esac
SEQ=${E188_SEQ:-$SEQ}                # E188_SEQ exists only for the stub self-test (dry_intel_e188.sh); session_e188.sh never sets it
BUDGET_S=${E188_BUDGET_S:-$BUDGET_S}; RESERVE_S=${E188_RESERVE_S:-60}; GAP_S=${E188_GAP_S:-10}
BLOCK=${E188_BLOCK:-tools/claims-v3/e188/block_e188.sh}      # E188_BLOCK exists only for the stub self-test
limit=$((T0 + BUDGET_S - RESERVE_S))
deadline=$(date -d "$DL" +%s) || { echo "E188_DEADLINE '$DL' is not a date"; exit 2; }
kind() { case "$1" in 188[23][0-9]) echo kinds ;; 1881[0-6]) echo train ;; *) echo other ;; esac; }
train_est() { python3 -B -c 'import json,sys; print(int(next(t["est_s"] for t in json.load(open(sys.argv[1]))["trains"] if t["block"] == int(sys.argv[2]))) + 30)' "$P" "$1"; }
pass_est=$(python3 -B -c 'import json,math,sys; print(math.ceil(json.load(open(sys.argv[1]))["estimate"][sys.argv[2]]) + 30)' "$P" "$pass_key") ||
  { echo "plan-e188.json unreadable"; exit 2; }
est_kinds=${E188_FIRST_KINDS_S:-$pass_est}; est_train=; est_other=1000000
seen_kinds=0; seen_train=0; seen_other=0
rel() { echo "T0+$(( $1 - T0 )) s"; }
mkdir -p build/e188
echo "$(date +%T) e188: plan $PLAN, items ${SEQ}; budget ${BUDGET_S} s from the anchor ($(date -d @"$T0" +%T)), reserve ${RESERVE_S} s, last end $(date -d @"$limit" +%T), deadline $(date -d @"$deadline" '+%F %T'); first estimate kinds ${est_kinds} s, trains by plan-e188.json"
n=0
for p in $SEQ; do
  if [ -e build/e188/STOP ] || [ -e build/claims-v3/STOP ]; then echo "$(date +%T) STOP: stopping before p$p"; break; fi
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
echo "$(date +%T) e188: done, $n items, at $(rel "$(date +%s)")"
