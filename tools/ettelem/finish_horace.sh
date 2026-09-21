#!/usr/bin/env bash
# Everything after run_horace_strict.sh and run_horace_cold.sh: activity counts, analyses, GIFs, report data, report.
#   tools/ettelem/finish_horace.sh <strict-run-dir> <cold-run-dir>... 
# Writes docs/reports/data/2026-09-21-horace-aifoundry2/ and docs/reports/2026-09-20-horace-experiment.html.
set -eu
cd "$(dirname "${BASH_SOURCE[0]}")/../.."
strict=${1:?strict run dir}; shift
D=docs/reports/data/2026-09-21-horace-aifoundry2
PATS=zeros,ones,pi,sparse50,uniform,randn,signs,pow2,mant,a_randn_b_ones,a_ones_b_randn,ternary,sparse75,checker
mkdir -p "$D/strict/tiles"
cp "$strict"/runs.jsonl "$strict"/starts.jsonl "$D/strict/"
cp "$strict"/tiles/*.bin "$D/strict/tiles/"
python3 tools/ettelem/compact_telemetry.py "$strict/telemetry.jsonl" "$D/strict/telemetry.jsonl.gz"
[ -e "$D/toggles.json" ] || nice python3 rtl-sim/fma_toggle/toggles.py --tiles-dir "$D/strict/tiles" --patterns "$PATS" --out "$D/toggles.json"
python3 tools/ettelem/analyze_horace_strict.py "$D/strict" --toggles "$D/toggles.json" --out "$D/horace3.json" \
  ${PRED:+--predictions "$PRED"} | tee "$D/horace3.txt"
colds=()
n=1
for c in "$@"; do
  mkdir -p "$D/cold$n"
  cp "$c"/runs.jsonl "$c"/starts.jsonl "$D/cold$n/"
  python3 tools/ettelem/compact_telemetry.py "$c/telemetry.jsonl" "$D/cold$n/telemetry.jsonl.gz"
  python3 tools/ettelem/analyze_horace_cold.py "$D/cold$n" --out "$D/cold$n.json" | tee "$D/cold$n.txt"
  colds+=("$D/cold$n.json"); n=$(( n + 1 ))
done
python3 tools/ettelem/build_horace_report_data.py --strict "$D/horace3.json" --toggles "$D/toggles.json" --cold "${colds[@]}" \
  ${PRED:+--before "$PRED"} --out "$D/report.json"
python3 tools/ettelem/make_heating_gif.py "$D/horace3.json" docs/reports/horace-heating.gif --poster docs/reports/horace-heating.png --steps
python3 tools/ettelem/make_heating_gif.py "$D/horace3.json" docs/reports/horace-heating-6.gif --steps --patterns zeros,ones,pi,sparse50,uniform,randn \
  --title "Six kinds of matrix, one matmul, same FLOPs"
python3 scripts/build-report.py horace-experiment "$D/report.json" docs/reports/2026-09-20-horace-experiment.html
