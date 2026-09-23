# Reruns for the confidence bars, aifoundry2, 23 September 2026 (13:20–13:50)

Three passes each of the relay by medium (`relay-pass*`, run_onchip_power.sh), the hot-line atomics
(`hotline-pass*`, run_hotline_power.sh) and the nocbench rings + memhier levels (`rl-pass*`,
run_rings_levels_power.sh), every pass preceded by heating the die past 76 °C (`preheat.jsonl`) so the
governor keeps 600 MHz. Driver: `tools/ettelem/run_reruns_warm.sh`, then `run_rl_warm_a2.sh`.

`rings-pass*` and `levels-pass*` are the same rings and levels measured by the older `run_energy.py`
runners, which poll power without the die temperature; they are kept for the record and **not pooled**
(no leakage correction, and the card was cooling from the preheat during them, which reads 10–50% high on
2 W signals). The pooled figures are in `../2026-09-23-energy-manual/reruns.json`, from
`tools/ettelem/analyze_reruns.py`.

The sibling directory `../2026-09-23-reruns-aifoundry2/` is the first attempt (12:51–13:10) on a 65 °C die:
its bursts were contaminated by 700–800 MHz excursions of the governor and the analysis drops all but two
of them; kept as the record of why the passes are preheated.
