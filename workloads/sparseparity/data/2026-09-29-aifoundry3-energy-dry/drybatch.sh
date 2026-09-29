#!/usr/bin/env bash
# energy.sh --dry --real-plan on aifoundry3 (no device, no lock): every preset on both test cards, one 20 Hz run,
# then the combines (a valid one per card, and the refusals)
cd ~/nekko/build/sparseparity-t-src || exit 2
O=$HOME/nekko/build/sparseparity-t-energy-dry
mkdir -p $O
E=workloads/sparseparity/energy.sh
for card in base alt; do
  for p in l1 l2 f5h0 f5h1; do
    nice -n 19 bash $E $p --dry --real-plan --stub-card $card --build ../sparseparity-t --out $O/$p-$card > $O/$p-$card.log 2>&1 &
  done
  wait
done
nice -n 19 bash $E l1 --dry --real-plan --stub-card alt --every-ms 50 --build ../sparseparity-t --out $O/l1-alt-20hz > $O/l1-alt-20hz.log 2>&1
PY=python3; [ -x ~/nekko/.venv/bin/python3 ] && PY=~/nekko/.venv/bin/python3
R=workloads/sparseparity/tools/energy_reduce.py
{ for card in base alt; do
    echo "--- combine f5h0-$card f5h1-$card"; nice -n 19 $PY $R combine $O/f5h0-$card $O/f5h1-$card --label "(256,5) $card" --json $O/f5-$card.json; echo "rc $?"
  done
  echo "--- refusal: f5h1 twice and l1";   nice -n 19 $PY $R combine $O/f5h1-base $O/f5h1-base $O/l1-base --label "(256,5)"; echo "rc $?"
  echo "--- refusal: f5h1 twice";          nice -n 19 $PY $R combine $O/f5h1-base $O/f5h1-alt --label "(256,5)"; echo "rc $?"
  echo "--- refusal: one half";            nice -n 19 $PY $R combine $O/f5h0-base --label "(256,5)"; echo "rc $?"
} > $O/combine.log 2>&1
echo DONE > $O/DONE
