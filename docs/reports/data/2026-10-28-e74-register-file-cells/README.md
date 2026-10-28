# E74 — what one bit stored in a register's own cell costs (Q129)

## Results

*Six passes, `p7410`–`p7415`, Wed 28 Oct 2026 11:14:05–11:25:40 PDT on aifoundry3 card 0, 600 MHz and 522 mV,
`--harts 1` (1,024 harts). **11.6 card-minutes** in all. Every pass `block.json` `"status":"ok"`; one pass set
aside by its own registered rule. Pre-registered Tue 27 Oct in `2be3f07e` / `547f4ae3`, both on `origin/main`
before the first launch. Reduced with `reduce.sh`, unchanged.*

**The board ladder does not resolve the cell bit. Rule 5 therefore publishes a bound:**

> ### e_cell < 2.73 fJ per flipped cell bit (95 %)
> point estimate **0.855 fJ**, 95 % t interval **[−1.02, +2.73] fJ** over 5 kept passes (df 4).
> The registered resolution was ±0.23 fJ at 5 passes; the measured half-width is **±1.87 fJ**, 8× worse.
>
> **The minion rail, fitted the same way, does resolve it: 1.643 fJ, 95 % [0.704, 2.583]**, and the board fit
> with a die-temperature covariate gives **1.359 fJ**. E61's cross-kernel 1.267 ± 0.151 fJ sits inside all three.

The design worked and the meter did not. The two falsification tests the registration cared about both came back
clean, which is the substantive result:

- **The issue rate does not move with the data.** `ops_per_cycle_per_hart` read **0.7574 on all 36 `rf_` runs**
  and **0.7356 on all 18 `rfz_` runs** — minimum equal to maximum, to the four decimals the device reports. The
  3 %, ~100×-the-signal confound that E61's cross-kernel subtraction carried is gone by construction here: one
  mode, one `.text`, 96 port bits on every rung, and only the 256 B operand image changing. Measured throughput
  4.65338 × 10¹¹ ops/s against the registered 4.6535 × 10¹¹.
- **The `rfz` null is flat.** Slope over the three `rfz` rungs **1.4 × 10⁻⁵ W per (bit/op)**, 95 % [−1.7, +2.0]
  × 10⁻⁴, i.e. **0.036 × the `rf` slope** against the registered "< 0.3 ×". Nothing leaked into the read ports or
  the result path.

So the ladder is measuring the cell and nothing else; there is simply not enough signal-to-noise in 6 passes of
the board meter. The whole span is 49 mW on a card drawing 32 W.

| | per flipped cell bit | per 256-bit `.pi` op (256 bits of content) | per fp32 MAC (64 bits of content) |
|---|---:|---:|---:|
| board, point | 0.855 fJ | 0.219 pJ | **0.055 pJ** |
| board, 95 % upper bound | 2.728 fJ | 0.698 pJ | **0.175 pJ** |
| board with a temperature covariate | 1.359 fJ | 0.348 pJ | 0.087 pJ |
| minion rail | 1.643 fJ | 0.421 pJ | 0.105 pJ |
| E61 (21 Oct, cross-kernel, same card) | 1.267 ± 0.151 fJ | 0.324 pJ | 0.081 pJ |

### Scoring

| Rule | Reading | Registered | Verdict |
|---|---|---|---|
| **P1** e_cell | point **0.855 fJ**, 95 % [−1.02, +2.73] | 0.8–1.8 fJ | **NOT RESOLVED → bound** (rule 5). The point lands inside the band; the interval spans zero, so this is not a measurement of e_cell and is not reported as one |
| **P2** span, rung 192 − rung 32 | **+48.9 mW**, 95 % [−98, +196] | +60 to +134 mW | **FAIL** — the point is below the band (the interval covers it, but the registration named the point) |
| **P3** linearity | resid rms **83.4 mW**; curvature **−1.81 σ** | ≤ 20 mW; no curvature ≥ 3 σ | **FAIL** on the residual (4.2× the limit), **PASS** on the curvature |
| **P4** the `rfz` null | **0.036 ×** the `rf` slope, interval spans zero | \|slope\| < 0.3 ×, flat within 2 SE | **PASS** |
| **P5** issue rate | `rf` **0.7574** (36 runs, min = max), `rfz` **0.7356** (18 runs, min = max) | 0.7574 ± 0.0020 / 0.7356 ± 0.0020 | **PASS** |
| **P6** cell capacitance | **6.28 fF** at 0.5218 V (6.28 at the measured 522 mV) | 5.9–13.2 fF | inside the band, but it is 2 e/V² of an unresolved e_cell and inherits P1's verdict |

### Why the scatter, and what it would cost to close

The five kept passes give slopes 2.68, 15.84, 3.83, −0.76 and −1.70 (× 10⁻⁴ W per bit/op). Their within-pass
residual rms is 36.7, **243.2**, 36.1, 74.7 and 26.0 mW — E60 worked at 32 mW, so four passes are 1.1–2.3× E60's
noise and one (`p7411`) is 7.6×. Rule 5 said in advance that a scatter worse than E60's turns the result into a
bound, and it did. At the measured between-pass SE the half-width falls as 1/√n: **≈ 40 passes** of this harness
(about 80 card-minutes) would bring the board interval to ±0.6 fJ, and ~250 passes to the registered ±0.23 fJ.
The cheaper route is the one this run stumbled on: **the minion rail is 4× tighter than the board** on the same
runs (SE 1.6 × 10⁻⁴ against 3.1 × 10⁻⁴ W per bit/op), because it does not carry the board's fan and regulator
noise. A follow-up should pre-register the rail as the estimator and the board as the check, not the reverse.

### The leakage correction is the other half of the uncertainty

| leakage slope used | e_cell (board) | span | `rfz` null slope ÷ `rf` | verdict |
|---|---:|---:|---:|---|
| `auto` — reduce_hl.py's own within-run estimator, **−0.007 W/°C** from 18 qualifying runs (registered default) | **0.855 fJ** | 48.9 mW | **0.036** | the null stays clean |
| 0.2936 W/°C — E66 on aifoundry2 (the registered sensitivity) | 1.560 fJ | 91.0 mW | 0.39 | the null **fails** |
| 0.3803 W/°C — E71 on **this** card over 58–62 °C, published the same day | 1.763 fJ | 103.1 mW | 0.44 | the null **fails** |

This is worth naming: a fixed idle slope roughly doubles e_cell *and* injects a matching k-dependence into the
null arm, which has no cell writes at all. The rungs that burn more power run their 2 s window hotter, so a
fixed-slope correction is itself a function of k — exactly the systematic E71 §S5 flagged for E65 and E67. The
`auto` estimator is near zero here because these runs barely heat (launch 58.0 °C, window mean 58.6–58.9 °C), and
it is the only one of the three that leaves P4 passing. Reported as registered: the board fit at `auto` is the
result, the other two are labelled sensitivities, and the pooled covariate fit (which estimates 0.208 W/°C from
the data rather than imposing it) gives 1.359 fJ.

## What ran, and what was registered

| | registered | happened |
|---|---|---|
| card | aifoundry3, 600 MHz, `--harts 1` | aifoundry3 card 0, 600 MHz, 522 mV, 1,024 harts, TDP 0 untouched |
| rungs | `rf_k32…k192`, C = 96, W = 128 on every rung | all six, operand sha256s identical to `BUILD-HASHES-2026-10-27.md` |
| null | `rfz_k32/k96/k192` | all three |
| passes | target 6, extend to 10 if the lane is free | **6 run, not extended** (the lane owed E75 and E76 the same afternoon) |
| approach | preheat 59 °C, launch at ≤ 58 °C, cap 78 °C | every launch on protocol at 58.0 °C; 0 unreachable, 0 over the cap |
| gates | one clock, 3 mV, 0.5 °C, 0.2 % rate | 0 run-level failures of any gate in 66 runs |
| pass gate | > 1 failing run, or anchor drift > 0.3 W | `p7412` set aside: anchor drift **−0.387 W** (others +0.08 to +0.23) |

## Departures, dated

- **D-R1 (28 Oct 2026) — the registered reducer did not exist.** The registration said "hl/reduce_hl.py reads
  E74's data directly". It cannot: `reduce_hl.py` subtracts each item from its family's zero rung, has no `rf`
  entry in its `ZERO` map, and has no path that fits a free-intercept line over an `ec` family — and E74 has no
  zero rung by construction (`k = 0` forces `C = 0`; the ladder's zero *is* the fit's intercept). Written on the
  day as `tools/claims-v3/rf/reduce_rf.py`, which imports `reduce_hl.py`'s per-run machinery unchanged
  (`runs_of_pass`, `leak_slope`, `fit_line`, `mean_se`, `units`), so no window, gate or correction is new, and
  adds only the registered estimator and the registered scoring.
- **D-R2 (28 Oct 2026) — the run is a day later than the registration.** Yesterday's lane agent died in setup at
  16:45 Tue with 0 launches; the data directory carries the date of the run.
- **D-R3 (28 Oct 2026) — the cross-box binary check cannot be met as written, and was met where it is
  meaningful.** The registration requires the `.text`/`code` hashes to equal aifoundry1's "before any number from
  the two boxes is compared". The **device kernel** matched exactly (`code kernel 82923db2…`), which is the code
  that executes the ladder. The **host** `code` hash does not match on any binary, including `enercat-tr` freshly
  built on this box, because the host statically links each box's own device layer and those differ. The host
  disassembly is therefore not a box-independent identity; `text.sha256` in every pass directory records what
  actually ran here.
- **D-R4 (28 Oct 2026) — a third leakage sensitivity.** E71 measured this card's own idle slope (0.3803 W/°C over
  58–62 °C) hours before this run; it is added to the registered 0.2936 W/°C sensitivity rather than replacing
  the registered `auto` estimator.
- **Not extended to 10 passes** (the registration's option). Named above with its consequence: the bound.

## What it changes

1. **Q128 §2's unpriced line gets a ceiling.** The 1.946 pJ bottom-up ledger omits "register-file read ports, the
   operand bus, the result path, pipeline registers"; of those the cells are now bounded. At 64 bits of register
   content per fp32 multiply-add the cells cost **0.055 pJ/MAC (point), at most 0.175 pJ/MAC at 95 %** — so they
   can account for **1.4 % of the 3.837 pJ unaccounted, and at most 4.6 %.** A ceiling is what the waterfall
   needs here: it says this term cannot be the explanation.
2. **E61's number survives the removal of its confound.** E61 reached the cell only by subtracting two kernels
   whose issue rates differ by 3 %, and was "not identified" on the other two cards. E74 removes that subtraction
   by construction and confirms the design is clean (P5 exact, P4 flat), and every estimator here — rail 1.643
   [0.704, 2.583], covariate 1.359, board point 0.855 — contains E61's 1.267 ± 0.151 fJ. The cell price is real
   and of order 1 fJ; it is not an artefact of the cross-kernel step.
3. **Levels tab stop 4** moves from "what the register file's own cells cost — missing" to *bounded, consistent
   with E61, resolved on the rail and not on the board*, with the price of resolving it stated: pre-register the
   rail, or ~40 passes (80 card-minutes) of the board.
4. **A method lesson for every ladder on this card**: a fixed idle leakage slope is not a safe correction for a
   power-dependent ladder — it doubled e_cell here and broke a null arm that has no signal in it. Use the
   within-run estimator or a fitted covariate, and report the fixed-slope numbers as sensitivities.

## Files

| file | what it is |
|---|---|
| `passes/p7410`–`p7415` | the six passes: `runs.jsonl`, `marks.jsonl`, `telemetry.jsonl.gz`, `configs.json`, `block.json`, `gen.sha256` (the operand files that ran), `text.sha256` (the binaries), `manifest.txt`, `run.log` |
| `gen/manifest.json` | the operand set's manifest as generated on this box (sha256s in `passes/*/gen.sha256`) |
| `rf.json` | the reduction at the registered `auto` leakage slope — the result |
| `rf-leak0.2936.json`, `rf-leak0.3803.json` | the two labelled sensitivities |
| `runs.csv` | one row per run: item, rung, p_raw, p80, rail, mV, rate, gate failures |
| `reduce.sh` | the three reduction commands, exactly as run |
| `queue.log` | the queue's own log, 11:14:05–11:25:40 PDT |

Code: `tools/claims-v3/rf/` (`make_rf.py`, `block.sh`, `queue_rf.sh`, `run_e74.sh`, `predictions.json`,
`reduce_rf.py`), runner `tools/claims-v3/hl/run_hl.py` unchanged.

## Reproducing it

    bash tools/claims-v3/rf/run_e74.sh setup       # operand set + --check, hashes, dry run. No card.
    bash tools/claims-v3/rf/run_e74.sh go 7410 6   # the six passes; log build/e74-rf.log
    bash docs/reports/data/2026-10-28-e74-register-file-cells/reduce.sh
