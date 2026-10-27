#!/bin/bash
# Q129: price every scope run's SAIF against the extracted capacitance, then build the ledger.
#   SCRATCH=... LAB=... bash tools/open-flow/scope/reduce.sh
set -u
S=${SCRATCH:?set SCRATCH}
L=${LAB:-$HOME/claude/et-soc1-prototyping}
W=$S/work-scope
CAP=${CAP:-$W/pnr-mixed/net_cap_globalroute.txt}
CE=$L/docs/reports/data/2026-10-26-asap7-cell-energies/asap7-cell-energies.json
OUT=${OUT:-$W/res/power-mixed}
mkdir -p "$OUT"
for p in randn zeros ones lq_h0 lq_h1 lq_h2 lq_h4 lq_h8 lb_h0 lb_h1 lb_h2 lb_h4 lb_h8 \
         randn_accfix randn_resfix; do
  [ -s "$W/sim/out/${p}_o1.saif" ] || { echo "skip $p"; continue; }
  nice -n 19 python3 -I "$L/tools/open-flow/txfma/power.py" \
      --saif "$W/sim/out/${p}_o1.saif" --saif-base "$W/sim/out/${p}_o0.saif" \
      --netcap "$CAP" --strip tb/dut --muladds 512 --block-depth 3 \
      --cell-energies "$CE" --out "$OUT/power_gr_$p.json" > "$OUT/power_$p.log" 2>&1
  echo "power rc=$? $p"
done
nice -n 19 python3 -I "$L/tools/open-flow/scope/ledger_scope.py" \
    --power "$OUT" --acct "$W/sim/out" --census "$W/res/census_mixed.json" \
    --out "$W/res/ledger-scope.json"
