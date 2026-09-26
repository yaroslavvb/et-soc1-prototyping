#!/usr/bin/env bash
# Run every reducer of the campaign on collected data (tools/claims-v3/collect.sh), with the campaign's cards
# (tools/claims-v3/campaign.py) as each one's default:
#   tools/claims-v3/reduce_all.sh <data> <out>      # writes <out>/<exp>.json and <out>/<exp>.log
set -u
data=$(realpath "${1:?collected data}"); out=$(realpath -m "${2:?output directory}")
cd "$(dirname "${BASH_SOURCE[0]}")/../.."
mkdir -p "$out"
for e in mem lat mmb abla ablb x5 tel wire rl idle cat catfull gs; do
  [ "$e" = gs ] && ! ls -d "$data"/*/gs >/dev/null 2>&1 && continue
  nice -n 10 python3 "tools/claims-v3/$e/reduce.py" --data "$data" --out "$out/$e.json" > "$out/$e.log" 2>&1
  echo "$e rc=$? $(tail -1 "$out/$e.log" | cut -c1-150)"
done
