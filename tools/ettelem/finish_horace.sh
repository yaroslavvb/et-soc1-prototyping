#!/usr/bin/env bash
# Rebuilds the Horace-experiment and why-low-power reports from the data kept in the repo.
#   tools/ettelem/finish_horace.sh            (analyses, model, GIFs, report data, both reports)
# To bring in fresh sessions first, copy them into the data directory the way the README there describes
# (runs.jsonl, starts.jsonl, ends.jsonl, tiles, and telemetry through compact_telemetry.py).
set -eu
cd "$(dirname "${BASH_SOURCE[0]}")/../.."
D=docs/reports/data/2026-09-21-horace-aifoundry2
PATS=zeros,ones,pi,sparse50,uniform,randn,signs,pow2,mant,a_randn_b_ones,a_ones_b_randn,ternary,sparse75,checker
KINDS=hadamard,hadamard_orth,dct,fft_cos,butterfly,kaleidoscope,identity,permutation,diagonal,tridiagonal,block_diag,upper,lowrank,circulant,quant4,relu,negzero

# switching activity from the RTL bench (slow: skipped when the JSON is already there)
[ -e "$D/toggles.json" ] || nice python3 rtl-sim/fma_toggle/toggles.py --tiles-dir "$D/strict/tiles" --patterns "$PATS" --out "$D/toggles.json"
[ -e "$D/structured_toggles.json" ] || nice python3 rtl-sim/fma_toggle/toggles.py --tiles-dir "$D/structured_tiles" --patterns "$KINDS" --out "$D/structured_toggles.json"
python3 - "$D" <<'PY'
import json, sys
d = sys.argv[1]
a = json.load(open(f"{d}/toggles.json")); a.update(json.load(open(f"{d}/structured_toggles.json")))
json.dump(a, open(f"{d}/toggles_all.json", "w"))
PY

# the strict 7 s session, the cool starts, the long runs, the ablations
python3 tools/ettelem/analyze_horace_strict.py "$D/strict" --toggles "$D/toggles.json" --predictions "$D/predictions_before.json" --out "$D/horace3.json" > "$D/horace3.txt"
python3 tools/ettelem/analyze_horace_cold.py "$D/cold1" --out "$D/cold1.json" > "$D/cold1.txt"
python3 tools/ettelem/analyze_horace_cold.py "$D/cold2" --out "$D/cold2.json" > "$D/cold2.txt"
python3 tools/ettelem/analyze_horace_long.py "$D/long" --out "$D/long.json" > "$D/long.txt"
python3 tools/ettelem/analyze_ablation.py "$D/ablation" --out "$D/ablation.json" > "$D/ablation.txt"
[ -d "$D/long2" ] && python3 tools/ettelem/analyze_horace_long.py "$D/long2" --out "$D/long2.json" > "$D/long2.txt"

# the flips-to-temperature model: long session up to the cooling change at 13,950 s, the strict session, idle data from the cool starts,
# and the overnight idle equilibrium (62 C at 26.7 W) as the anchor of the slowest stage
python3 tools/ettelem/flip_thermal_model.py "$D/long@13950" "$D/strict" --leak-only "$D/cold1" "$D/cold2" --anchor 62:26.7 \
  --toggles "$D/toggles_all.json" --out "$D/model.json" > "$D/model.txt"

# out-of-sample tests: every parameter from the first 7,400 s of the long session (plus the strict session), then frozen;
# thermal state at each launch from telemetry before it only (validate_flip_model.py fits nothing)
python3 tools/ettelem/flip_thermal_model.py "$D/long@7400" "$D/strict" --leak-only "$D/cold1" "$D/cold2" --anchor 62:26.7 \
  --toggles "$D/toggles_all.json" --out "$D/model_firsthalf.json" > "$D/model_firsthalf.txt"
python3 tools/ettelem/validate_flip_model.py "$D/long@13950" --model "$D/model_firsthalf.json" --toggles "$D/toggles_all.json" --after 7400 \
  --out "$D/validation_timesplit.json" > "$D/validation_timesplit.txt"
python3 tools/ettelem/validate_flip_model.py "$D/long2" --model "$D/model_firsthalf.json" --toggles "$D/toggles_all.json" \
  --out "$D/validation_afternoon_firsthalf.json" > "$D/validation_afternoon_firsthalf.txt"
python3 tools/ettelem/validate_flip_model.py "$D/long2" --model "$D/model.json" --toggles "$D/toggles_all.json" \
  --out "$D/validation_afternoon.json" > "$D/validation_afternoon.txt"
[ -d "$D/long2" ] && python3 tools/ettelem/flip_thermal_model.py "$D/long2" --evaluate "$D/model.json" --toggles "$D/toggles_all.json" --out "$D/model2.json" > "$D/model2.txt"

python3 tools/ettelem/build_horace_report_data.py --strict "$D/horace3.json" --toggles "$D/toggles.json" --cold "$D/cold1.json" "$D/cold2.json" \
  --before "$D/predictions_before.json" --long "$D/long.json" --model "$D/model.json" \
  --structured-before "$D/structured_predictions_before.json" --ablation "$D/ablation.json" --long2 "$D/long2.json" --model2 "$D/model2.json" \
  --validation "$D/validation_timesplit.json" "$D/validation_afternoon.json" "$D/model_firsthalf.json" --out "$D/report.json"
python3 tools/ettelem/build_lowpower_report_data.py --ablation "$D/ablation.json" --model "$D/model.json" --toggles "$D/toggles.json" --vf "$D/vf.json" --out "$D/lowpower-report.json"

python3 tools/ettelem/make_heating_gif.py "$D/horace3.json" docs/reports/horace-heating.gif --poster docs/reports/horace-heating.png --steps
python3 tools/ettelem/make_heating_gif.py "$D/horace3.json" docs/reports/horace-heating-6.gif --poster docs/reports/horace-heating-6.png --steps \
  --patterns zeros,ones,pi,sparse50,uniform,randn --title "Six kinds of matrix, one matmul, same FLOPs"
python3 tools/ettelem/make_long_gif.py "$D/long.json" docs/reports/horace-long.gif --poster docs/reports/horace-long.png --groups zeros:32,ones:32,randn:32,randn:12

# section 10's second card (and the DVFS report's three-machine block): without this merge the Horace page loses
# section 10's chart, because its script starts with `const C=D.cards;if(!C)return`
python3 tools/ettelem/build_cards_data.py --cards docs/reports/data/2026-09-22-horace-aifoundry3/cards.json \
  --transfer docs/reports/data/2026-09-22-horace-aifoundry3/transfer.json \
  --leak docs/reports/data/2026-09-22-horace-aifoundry3/leakage_crosscard.json \
  --config docs/reports/data/2026-09-22-cards/config.json --driver docs/reports/data/2026-09-22-cards/driver_config.json \
  --sptrace docs/reports/data/2026-09-22-cards/sptrace-aifoundry3.bin --out docs/reports/data/2026-09-22-cards/cards-report.json \
  --merge docs/reports/data/2026-09-22-dvfs-aifoundry2/dvfs.json "$D/report.json"

python3 scripts/build-report.py horace-experiment "$D/report.json" docs/reports/2026-09-20-horace-experiment.html
python3 scripts/build-report.py why-low-power "$D/lowpower-report.json" docs/reports/2026-09-21-why-low-power.html
