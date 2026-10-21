#!/usr/bin/env bash
# V3-DTF: start this card's registered passes (cards.json from make_dtf.py) detached, as queue_dtf.sh.
#   bash tools/claims-v3/dtf/start_card.sh <aifoundry3|aifoundry2|aifoundry1-c0> [first-pass] [--cam]
# The electrical passes launch at 58 C after a 59 C preheat (57 / 58 on aifoundry1 card 0, as E60); --cam starts the
# dtf-cam block on aifoundry2 instead: per pass 5 runs of each of the four halves in contiguous same-side runs, W-first
# in odd passes and E-first in even ones (README "E-D7").
set -u
cd "$(dirname "${BASH_SOURCE[0]}")/../../.."
card=${1:?card}; first=${2:-1}; mode=${3:-}
J=build/dtf-gen/cards.json
[ -f "$J" ] || { echo "no $J"; exit 2; }
items=$(python3 -c 'import json,sys; print(",".join(json.load(open(sys.argv[1]))[sys.argv[2]]["items"]))' "$J" "$card")
dup=$(python3 -c 'import json,sys; print(",".join(json.load(open(sys.argv[1]))[sys.argv[2]]["dup"]))' "$J" "$card")
passes=$(python3 -c 'import json,sys; print(json.load(open(sys.argv[1]))[sys.argv[2]]["passes"])' "$J" "$card")
dev=; t=58; p=59
case "$card" in aifoundry1-c0) dev=0; t=57; p=58 ;; esac
if [ "$mode" = --cam ]; then
  n=$(python3 -c 'import json,sys; print(json.load(open(sys.argv[1]))[sys.argv[2]]["cam"]["passes"])' "$J" "$card")
  for i in $(seq "$first" $((first + n - 1))); do
    if [ $((i % 2)) -eq 1 ]; then o="d7w_hi d7e_hi d7w_lo d7e_lo"; else o="d7e_hi d7w_hi d7e_lo d7w_lo"; fi
    order=$(for x in $o; do for k in 1 2 3 4 5; do printf '%s,' "$x"; done; done)
    echo "dtf-cam p$i: ${order%,}"
    bash tools/claims-v3/dtf/block.sh "$i" "${order%,}" --cam < /dev/null; echo "dtf-cam p$i rc=$?"
  done
  exit 0
fi
echo "$(date +%T) $card: passes $first..$((first + passes - 1)), $(echo "$items" | tr ',' '\n' | wc -l) items, dup [$dup], launch $t after $p"
V3_DEVICE=$dev DTF_DUP=$dup HL_TARGET=$t HL_PREHEAT=$p setsid nohup bash tools/claims-v3/dtf/queue_dtf.sh "$first" "$passes" "$items" \
  > "build/dtf-queue-$card.log" 2>&1 < /dev/null &
sleep 2
echo "started: build/dtf-queue-$card.log"
