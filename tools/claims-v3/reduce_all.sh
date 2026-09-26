#!/usr/bin/env bash
# Run every reducer of the campaign on collected data (tools/claims-v3/collect.sh), with the campaign's cards
# (tools/claims-v3/campaign.py) as each one's default:
#   tools/claims-v3/reduce_all.sh <data> <out>      # writes <out>/<exp>.json and <out>/<exp>.log
# Three registered rules need values from another experiment. Their exporters run first, just before the reducer that
# reads them, and write <out>/inputs/<name>.json with a .log beside it (AMENDMENTS.md, implementation note of 26 Sep):
#   ablb --mmb-values  ablb/export_mmb_values.py  V3-MMB's int8 above-idle W per pass (ABLB-2b's kernel clause)
#   rl   --flop        rl/export_flop.py          V3-ABL-A's fp32 pJ/MAC per block, from <out>/abla.runs.json (RL-X4)
#   rl   --low-edge    rl/export_low_edge.py      V3-CATFULL's low edge per pass, cards outside the 23 Sep catalogue (RL-f)
# A reducer whose input could not be built runs without it (that rule then reads INSUFFICIENT or pending).
set -u
data=$(realpath "${1:?collected data}"); out=$(realpath -m "${2:?output directory}")
cd "$(dirname "${BASH_SOURCE[0]}")/../.."
inp="$out/inputs"
mkdir -p "$out" "$inp"
input() {  # input <name> <exporter> <args...>: build $inp/<name>.json; status 0 when it was built
  local n=$1 s=$2 rc; shift 2
  rm -f "$inp/$n.json"
  nice -n 10 python3 "$s" "$@" --out "$inp/$n.json" > "$inp/$n.log" 2>&1; rc=$?
  echo "  input $n rc=$rc $(tail -1 "$inp/$n.log" | cut -c1-140)"
  return $rc
}
for e in mem lat mmb abla ablb x5 tel wire rl idle cat catfull gs; do
  [ "$e" = gs ] && ! ls -d "$data"/*/gs >/dev/null 2>&1 && continue
  extra=()
  case $e in
    ablb) input mmb_values tools/claims-v3/ablb/export_mmb_values.py --data "$data" && extra+=(--mmb-values "$inp/mmb_values.json") ;;
    rl)   input flop tools/claims-v3/rl/export_flop.py --runs "$out/abla.runs.json" && extra+=(--flop "$inp/flop.json")
          input low_edge tools/claims-v3/rl/export_low_edge.py --data "$data" && extra+=(--low-edge "$inp/low_edge.json") ;;
  esac
  nice -n 10 python3 "tools/claims-v3/$e/reduce.py" --data "$data" --out "$out/$e.json" "${extra[@]}" > "$out/$e.log" 2>&1
  echo "$e rc=$? $(tail -1 "$out/$e.log" | cut -c1-150)"
done
