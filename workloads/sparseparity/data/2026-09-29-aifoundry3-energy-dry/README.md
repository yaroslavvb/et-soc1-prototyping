# `energy.sh --dry` on both test cards, aifoundry3, 29 September 2026 (11:14-11:17 PDT)

No card was opened: `--dry` runs `tools/energy_stub.py`'s host and sampler doubles (no device, no lock, no `et-who`
wait), and `--real-plan` takes the plan from the real host's `--dry` (`build/sparseparity-t`, R4's sources, CPU only,
niced). Everything ran at `nice -n 19` in `~/nekko/build/sparseparity-t-src` while `et-who --check` showed the card
free. `drybatch.sh` is the driver (each card's four presets at once, then L1 on the alt card at 20 Hz, then the
combines). The reductions were redone on aifoundry2 with the final `tools/energy_reduce.py` (the same numbers; a
flag's wording changed), which rewrote each `energy.json` and `energy.txt`, `combine.log` and `f5-*.json`.

**The two cards** (`tools/energy_stub.py`'s docstring). `base` has the reducer's own laws (the catalogue's leakage
law, unit-gain first-order filters with tau 1.05 s, one slow thermal stage, the host's launch marks as the card's
edges): a plumbing test. `alt` breaks each of them: aifoundry3's own idle curve as the leakage law (20 W
e^((T-80)/40), 0.27 W/°C at 56 °C against the reducer's 0.33), `docs/findings/11-thermal-model.md`'s thermal chain
(stages of 1.5 s and 4 s heat the die within the burst and let it cool within seconds of its end), the SP's board
average with gain 1.01 and tau 0.8 s, the rails with tau 1.3 s, `board_w` one SP pass late, other rail shares, the idle
die at 55.7 °C (base 55.3 °C: the whole-degree reading rounds the other way), and the card's power starting 5 ms after
the host's launch mark and ending 3 ms before its end mark. Both use E58's SP pass: 0.255 s at 10 Hz, 0.296 s at 20 Hz.

| File | What |
|---|---|
| `<preset>-<card>/` | One run each (`l1`, `l2`, `f5h0`, `f5h1` x `base`, `alt`; `l1-alt-20hz` with `--every-ms 50`): `run.json` (energy.sh's marks, with `host_cpu_ext_s` from bash `times`), `plan.json` (the real host's `--dry` line), `host.json` (the host double's line, with `host_cpu_s`), `telemetry.jsonl.gz` (the sampler double's lines), `stub_truth.json` (the injected energies), `stub_sched.jsonl` (the launches), `energy.json` and `energy.txt` (the reduction and its TRUTH check), `energy.log`. |
| `<preset>-<card>.log` | `energy.sh`'s own log of the run. |
| `combine.log`, `f5-base.json`, `f5-alt.json` | `energy_reduce.py combine` of the two halves on each card, and three refusals (f5h1 twice with l1; f5h1 twice; one half alone): exit 2 each. |
| `errors.txt`, `drysum.py` | Each run's error against the injected energy, % (the table below). |
| `drybatch.sh` | The driver. |

**Every run TRUTH PASS.** Error against the injected energy, % (the README's "Energy per solve" has the claims):

| Run | Headline (±3) | Total (±2) | Catalogue (at idle / busy, expected) | Ramp (not checked) | Rails: minion, SRAM, NoC (-2..+7) | Unmetered (±15) | Edges, ms |
|---|---|---|---|---|---|---|---|
| l1 base | -2.83 | -0.76 | -6.70 (2/19, 0.6) | -0.11 | -0.22, +0.52, -0.49 | -10.9 | -0.5 / -0.6 |
| l2 base | -1.77 | -0.49 | +0.58 (0/19, 0.2) | -0.08 | -0.18, +0.59, -0.50 | -6.8 | -0.1 / -0.8 |
| f5h0 base | -2.15 | -0.63 | +0.03 (0/20, 0.1) | +0.03 | -0.08, +0.60, -0.38 | -8.6 | -0.2 / -0.4 |
| f5h1 base | -2.74 | -0.78 | +0.14 (0/15, 0.0) | +0.06 | -0.05, +0.44, -0.24 | -11.0 | -0.7 / -0.3 |
| l1 alt | +0.95 | +1.05 | -0.66 (2/21, 0.6) | +4.39 | +1.32, +5.80, +1.90 | -2.0 | -5.6 / +3.0 |
| l2 alt | +0.56 | +0.79 | -2.47 (1/22, 0.2) | +4.32 | +1.34, +5.88, +1.92 | -3.7 | -5.3 / +3.0 |
| f5h0 alt | +0.89 | +0.91 | +0.87 (0/20, 0.1) | +4.49 | +1.39, +5.91, +2.05 | -2.5 | -5.2 / +2.5 |
| f5h1 alt | +1.47 | +1.18 | +0.34 (0/17, 0.0) | +4.63 | +1.28, +5.65, +1.86 | +0.3 | -5.7 / +2.7 |
| l1 alt, 20 Hz | +0.94 | +1.05 | -7.92 (3/18, 0.5) | +4.32 | +1.33, +5.86, +1.95 | -2.1 | -5.4 / +2.1 |

What it shows. The headline (the SP's board average less the leakage law on the measured die temperature) follows
the whole-degree rounding: -1.8% to -2.8% with the idle die at 55.3 °C, +0.6% to +1.5% at 55.7 °C. The ramp baseline
(the headline of the first version of this tool, which R4 reviewed) is exact on the base card and 4.3-4.6% high on the
alt one, whose fast thermal stages the late bracket cannot see: that is why the headline changed a second time. The
catalogue's method follows its readings at idle: -6.7% and -7.9% with 2 and 3 of them against 0.5-0.6 expected. The
host doubles report one core busy through the burst (a made-up figure: the real host's is measured on the card), so
the host's share here is only plumbing.
