# Dated note 1 beside README.md, Thu 5 Nov 2026 (week 45), about 23:40 PST to Fri 6 Nov about 00:40 PST: the verifier's faults fixed (the vector rows' rails carry their own heating, and so does the delivery-loss fit made on them; the vector rows' named gaps are in-sample; the regulators' line is the fit's minion term; E82's earlier board ratio; the card's fan is assumed; the nits)

*This note sits beside [`README.md`](README.md), not inside it: the README, the NOTE and every file of `538c98ce` (22:54:13 PST) stay
as committed. It answers the adversarial verifier of the anatomy lane (`verify-anat-q145a`, Thu 5 Nov 2026, about 23:00-23:35 PST),
whose verdict was "holds with fixes": one major fault and six minor ones, the last of them eight nits. **Post hoc throughout:** nothing here is a
prediction, a verdict or a fit that enters a model, and nothing is blind or held out. Desk only: no card, no device command, no lab box.
Every figure below is printed by [`posthoc_note1_q145a.py`](posthoc_note1_q145a.py) (pure Python, committed files only) in
[`posthoc-note1-q145a.txt`](posthoc-note1-q145a.txt) and [`posthoc-note1-q145a.json`](posthoc-note1-q145a.json); section numbers
F1-F7 there are the faults below. A companion note sits beside the NOTE:
[`NOTE-2026-11-05-fmadd-ps-public-facts.md.dated-note-1.md`](NOTE-2026-11-05-fmadd-ps-public-facts.md.dated-note-1.md). The
records round puts the anatomy's line in the kinds page's
[section 11](https://spacesheep.dev/@yaroslavvb/horace-kinds-of-numbers#11-what-is-still-open), items 6 and 8.*

**What does not change:** every line of every TensorFMA ledger (at rest, awake on zeros, the data-dependent part on each rail and
off-rail, the window's heating, the board), so the headline step's 47.67 nJ, its 49% at rest and its 36.9% on the minion rail's
data-dependent switching stand; the one-number pairs and their resolution; the rail shares (79-85% and 81-94%); the TensorFMA card
ratios; the virus's flips; the issue rates. **What changes:** the vector rows' minion and off-rail lines (section 1), the NOTE's
minion-rail figure and ratio (the companion note), the vector arm's pooled const-against-zeros reading, and the cross-cut that splits
the off-rail line into the regulators' loss and the named gap (sections 1.5 and 3), whose size for fp32 random moves from 2.0% of the
board to between -0.3% and +0.9%.

## Builds on (additions to the README's block, the stock-take rule of 5 Nov 2026)

- **Checked:** the prior-work inventory, read again Thu 5 Nov 2026 about 23:40 PST: its public rows L06, L11, H05, H07, H19, P03 and P06
  (opaque pointers), with the map's rows 5, 7 and 16, beside the README's own block.
- **Used**, each with what is taken and how it was checked:
  - **Q136(b)'s re-cut of the rail row** (`bba190bb` `docs/reports/data/2026-11-02-q136b-rail-row/recut.py`, `02cf82eb` `recut.json`):
    its method for the catalogue's rails (the die's rise over the rails' own windows, passed through the card's rail filter,
    `recut.py` `cat_bursts`), its drift slopes per rail (`recut.json` `catalogue.<card>.drift_used`, the rail ledger's E38 heating
    runs) as rule B below, and its refit of the same 392 configurations on that footing (`measured_split_filtered`). *Check:* this
    note's code reproduces that refit's coefficients to 3e-12 (aifoundry3) and 9e-12 (aifoundry2) relative, and re-derives the
    catalogue's `die_c_busy` and `die_c_before` from the raw telemetry to 5e-7 °C in all 3,528 bursts (F1 checks).
  - **The catalogue's reduction** (`de262730` `workloads/enercat/analyze_catalogue.py`, lines 82-100): the busy window, the idle
    brackets, the board's correction (the 21 Sep law's slope times the busy die's rise), and the rails read raw over the burst's
    last 0.6 s against a rail idle before the burst, divided by 0.94. The raw telemetry it reads (`921e3158`,
    `docs/reports/data/2026-09-25-claims-v3/raw/<card>/catfull/p*/telemetry.jsonl.gz`), with `catalogue.json` and
    `unmetered_fit.json` (`f1461a68`).
  - **The delivery-loss fit's form** (`f1461a68` `tools/ettelem/fit_unmetered.py`): configuration means over passes, least squares
    with no intercept. *Check:* the published coefficients are reproduced to 1e-14 relative on all three cards.
  - **The registered reduction's rail rule** (`cfd94285` `tools/claims-v3/kinds/reduce_e78.py`, line 238: `c_rb` 0.81, "rail change
    per board change, frozen from E79"), the rule the TensorFMA ledgers' minion lines already use, as rule A.
  - **E82** (`bd86f232` `docs/reports/data/2026-10-31-e82-kinds-aifoundry1/README.md`, lines 20 and 298-299): card 1's board against
    aifoundry3's after each card's V², 1.061 on 31 Oct, the earlier measurement of the same quantity at the same operating point
    (600 MHz, launches near 58 °C, about 522 and 499 mV). *Check:* section 4.
  - **The energy manual's section 4.3** (`b083d80e` `docs/energy-manual/04a-fine-grain.md`, line 212): "The mesh coefficient is not all
    regulator".
  - **Public sources at pinned commits:** aifoundry-org/et-boards `e5e0cf2` (the PMIC firmware: the MAX6660's three uses, section 5);
    aifoundry-org/et-platform `836a4ab60` (`test-compute-kernels/src/vpu_txfma_power_virus/kernel.h`, lines 162-190, the loop).
- **Not used:** the rail ledger's drift for card 1 (none exists, so rule B covers aifoundry3 and aifoundry2 only); the footing law
  (`c14e5f35`) as the vector rows' correction (they keep the catalogue's own law, which the board's correction in the same rows uses;
  the README cites the footing law for the TensorFMA heating line); E77 and E120, except through Q136(b).
- **Tiers:** public only. No NDA-tier check was made or is cited.

## 1. The vector rows' rails carry their own heating (the major fault)

**What was wrong.** In the README's vector table, "above rest, minion rail" (and the SRAM + NoC column) is the catalogue's
`rails_over`: a raw rise, each rail over the burst's last 0.6 s against a rail idle taken before the burst, divided by 0.94, with no
leakage correction. The board's figure, `over_idle_w`, is net of the board's whole leakage correction, and the ledger books that
correction again as its own "burst heating" line. So the rails' own heating sat both inside the minion line (labelled as switching)
and in the heating line, and the off-rail line, a remainder, was short by the same amount. The TensorFMA ledgers do not have this
fault: their minion lines take 0.81 k ΔT off, as the registered reduction does.

**The rules used to take the minion rail's own heating off** (per burst, from the raw telemetry, then the mean over the three passes):

- **A, the registered reduction's rule:** 0.81 times the catalogue's own law slope at the rails' mean die (23.257/36 e^((T-80)/36)
  W/°C, the slope the board's correction in the same rows uses), times the die's rise over the rails' windows passed through the
  card's own rail filter (`catalogue.json` `rail_filter`: tau 1.235 s aifoundry3, 1.153 s card 1, 1.133 s aifoundry2), divided by
  0.94 as the rails are. This puts the minion line on one footing with the board's figure and with the TensorFMA ledgers' rule.
- **Au, the same on the unfiltered rise:** an upper bound, since the rail's filter lags a rising die (the median rise over the rails'
  windows is 1.00 °C raw and 0.35-0.56 °C through the filter).
- **B, Q136(b)'s measured drift:** the rail ledger's minion drift slope (0.114 W/°C of the board's 0.358 on aifoundry3; 0.268 of 0.725
  on aifoundry2), on the filtered rise, /0.94. A smaller minion share than A's 0.81, measured on E38's heating runs.

### 1.1 The vector rows, re-split on footing A (pJ an instruction, the catalogue's wall-rate convention)

Only two columns of the README's vector table move: the minion line loses its own heating and the off-rail line takes it back. The
board, the rest, the heating line and the SRAM + NoC column (raw, as in the TensorFMA ledgers) are unchanged, and the books still close
(to 6.7e-7 W, the catalogue's own rounding).

| instruction | card | above rest, minion rail: committed (raw) | its own heating, rule A (Au; B) | share of the raw line | minion rail, footing A | above rest, off-rail: committed | off-rail, footing A |
|---|---|---:|---:|---:|---:|---:|---:|
| `fadd.pi/zeros/h2` | aifoundry3 | 10.45 | 0.19 (0.37; 0.08) | 1.8% | 10.26 | 2.02 | 2.22 |
| `fadd.pi/const/h2` | aifoundry3 | 10.70 | 0.30 (0.54; 0.12) | 2.8% | 10.40 | 1.75 | 2.05 |
| `fadd.pi/random/h2` | aifoundry3 | 16.25 | 0.40 (0.72; 0.16) | 2.5% | 15.85 | 3.09 | 3.49 |
| `fadd.ps/zeros/h2` | aifoundry3 | 19.06 | 0.50 (0.67; 0.20) | 2.6% | 18.57 | 2.94 | 3.44 |
| `fadd.ps/const/h2` | aifoundry3 | 19.36 | 0.73 (1.12; 0.30) | 3.8% | 18.63 | 3.00 | 3.73 |
| `fadd.ps/random/h2` | aifoundry3 | 34.46 | 1.16 (1.66; 0.45) | 3.4% | 33.30 | 6.28 | 7.44 |
| `fmadd.ps/zeros/h2` | aifoundry3 | 22.53 | 0.93 (1.37; 0.37) | 4.1% | 21.60 | 3.77 | 4.70 |
| `fmadd.ps/const/h2` | aifoundry3 | 22.73 | 0.65 (1.04; 0.26) | 2.9% | 22.08 | 3.85 | 4.50 |
| `fmadd.ps/random/h2` | aifoundry3 | 46.16 | 1.65 (2.54; 0.63) | 3.6% | 44.52 | 9.21 | 10.86 |
| `nop/zeros/h2` | aifoundry3 | 4.20 | -0.04 (0.00; -0.02) | -1.1% | 4.25 | 1.02 | 0.98 |
| `fadd.pi/zeros/h2` | aifoundry1-c1 | 10.76 | 0.34 (0.56; -) | 3.2% | 10.42 | 1.38 | 1.72 |
| `fadd.pi/const/h2` | aifoundry1-c1 | 10.98 | 0.34 (0.63; -) | 3.1% | 10.64 | 1.26 | 1.59 |
| `fadd.pi/random/h2` | aifoundry1-c1 | 16.78 | 0.63 (1.03; -) | 3.8% | 16.15 | 1.91 | 2.55 |
| `fadd.ps/zeros/h2` | aifoundry1-c1 | 19.58 | 0.61 (0.86; -) | 3.1% | 18.97 | 2.19 | 2.81 |
| `fadd.ps/const/h2` | aifoundry1-c1 | 19.97 | 0.61 (0.79; -) | 3.1% | 19.36 | 2.23 | 2.85 |
| `fadd.ps/random/h2` | aifoundry1-c1 | 35.86 | 1.62 (2.10; -) | 4.5% | 34.24 | 3.75 | 5.36 |
| `fmadd.ps/zeros/h2` | aifoundry1-c1 | 23.21 | 0.93 (1.22; -) | 4.0% | 22.28 | 2.56 | 3.49 |
| `fmadd.ps/const/h2` | aifoundry1-c1 | 23.54 | 0.92 (1.22; -) | 3.9% | 22.62 | 3.61 | 4.52 |
| `fmadd.ps/random/h2` | aifoundry1-c1 | 47.54 | 1.99 (2.68; -) | 4.2% | 45.55 | 6.52 | 8.51 |
| `nop/zeros/h2` | aifoundry1-c1 | 4.36 | 0.22 (0.42; -) | 5.0% | 4.15 | 0.47 | 0.68 |
| `fadd.pi/zeros/h2` | aifoundry2 | 10.51 | 0.52 (0.68; 0.32) | 4.9% | 9.99 | 1.84 | 2.36 |
| `fadd.pi/const/h2` | aifoundry2 | 10.69 | 0.23 (0.67; 0.14) | 2.2% | 10.46 | 1.86 | 2.10 |
| `fadd.pi/random/h2` | aifoundry2 | 16.62 | 1.05 (1.80; 0.54) | 6.3% | 15.57 | 3.41 | 4.46 |
| `fadd.ps/zeros/h2` | aifoundry2 | 19.07 | 0.85 (1.09; 0.53) | 4.4% | 18.22 | 3.05 | 3.89 |
| `fadd.ps/const/h2` | aifoundry2 | 19.52 | 1.08 (1.40; 0.64) | 5.5% | 18.45 | 2.97 | 4.05 |
| `fadd.ps/random/h2` | aifoundry2 | 34.62 | 2.21 (3.03; 1.36) | 6.4% | 32.41 | 5.86 | 8.07 |
| `fmadd.ps/zeros/h2` | aifoundry2 | 22.97 | 1.58 (2.15; 0.81) | 6.9% | 21.39 | 3.87 | 5.45 |
| `fmadd.ps/const/h2` | aifoundry2 | 22.74 | 1.03 (1.39; 0.61) | 4.5% | 21.71 | 4.38 | 5.41 |
| `fmadd.ps/random/h2` | aifoundry2 | 46.00 | 2.75 (3.79; 1.69) | 6.0% | 43.25 | 8.41 | 11.16 |
| `nop/zeros/h2` | aifoundry2 | 4.20 | -0.03 (0.09; -0.02) | -0.7% | 4.23 | 1.02 | 1.00 |

So the README's vector table is to be read as follows: its minion and SRAM + NoC columns are **raw, with their own heating at the
burst's end**; its off-rail column is **net of the board's whole correction and short by those rails' heating**; its heating column is
the board's correction. On footing A the minion line loses 0.2-2.0 pJ an instruction on aifoundry3 and card 1 and 0.2-2.8 pJ on the
hotter aifoundry2 (1.8-6.9% of the raw line, the nop rows aside), and the off-rail line gains the same. The minion line's electrons
scale with it.

### 1.2 Card 1 against aifoundry3 after V², the vector minion rail

On footing A, `fmadd.ps` random's minion rail reads card 1 at **1.124** times aifoundry3 after each card's V² (the README's raw 1.131);
`fadd.ps` random 1.129 (raw 1.143); `fadd.pi` random **1.119** (the README's 1.134). Card 1's 12-13% above a V²-scaled expectation
on the vector minion rail stands (the TensorFMA steps read 8-10%).

### 1.3 The vector arm's const-against-zeros reading, pooled again

Pooled over the three cards as the README pools them (card-blocked, df 6; mean ± 95% half-width, pJ an instruction):

| pair | board | minion rail, raw | minion rail, A | minion rail, Au | off-rail, raw | off-rail, A | the minion rail's own heating, A |
|---|---:|---:|---:|---:|---:|---:|---:|
| `fadd.pi` const - zeros | +0.05 ± 0.22 | +0.22 ± 0.57 | +0.28 ± 0.43 | +0.14 ± 0.45 | -0.12 ± 0.72 | -0.19 ± 0.53 | -0.06 ± 0.29 |
| `fadd.ps` const - zeros | +0.44 ± 0.44 | +0.38 ± 0.31 | +0.23 ± 0.24 | +0.15 ± 0.41 | +0.01 ± 0.66 | +0.16 ± 0.65 | +0.16 ± 0.23 |
| `fmadd.ps` const - zeros | +0.15 ± 0.39 | +0.10 ± 0.34 | +0.38 ± 0.34 | +0.45 ± 0.43 | +0.55 ± 0.83 | +0.27 ± 1.02 | -0.28 ± 0.38 |
| `fadd.pi` random - zeros | +7.15 ± 0.41 | +5.98 ± 0.26 | +5.63 ± 0.21 | +5.33 ± 0.14 | +1.06 ± 0.45 | +1.40 ± 0.47 | +0.34 ± 0.35 |
| `fadd.ps` random - zeros | +18.70 ± 0.47 | +15.74 ± 0.47 | +14.73 ± 0.43 | +14.35 ± 0.42 | +2.57 ± 0.74 | +3.58 ± 0.62 | +1.01 ± 0.15 |
| `fmadd.ps` random - zeros | +28.67 ± 1.25 | +23.66 ± 0.45 | +22.68 ± 0.49 | +22.23 ± 0.57 | +4.65 ± 1.44 | +5.63 ± 1.60 | +0.98 ± 0.27 |

The README's `fadd.ps` "+0.38 ± 0.31 pJ on the minion rail" carried the two bursts' different heating: net of it, **+0.23 ± 0.24 pJ,
not resolved** (Au +0.15 ± 0.41). On footing A it is `fmadd.ps` whose minion rail clears zero instead (+0.38 ± 0.34; +0.10 ± 0.34 raw),
because its zeros bursts heated more than its const bursts. Still two of the fifteen pooled line tests clear zero (the board's
`fadd.ps`, by 0.001 pJ, and the minion rail's `fmadd.ps`, by 0.04 pJ), but which ones moves with the footing. So **no
const-against-zeros term is resolved on the vector unit**, per card or pooled; the board's readings, which the README states first, do
not change. This still fits E178's dated note A1-2 and its withdrawal of the "null", and the vector arm's later registration still
owns the question.

### 1.4 What the double count touches beyond the vector rows: the delivery-loss fit was made on the same raw rails

The energy manual's section 4.3 fit (`unmetered_fit.json`), whose coefficients the TensorFMA ledgers' regulators' cross-cut and named
gap use, was fitted on exactly these catalogue rows: the board net of its correction, the rails raw (Q136(b), result 1). Its unmetered
watts were therefore short by the rails' heating, and its minion coefficient low. Re-made here in its own form (fit_unmetered.py's rows
and least squares), with only the minion rail taken net of its own heating:

| card | footing of the fit | minion coefficient | SRAM | mesh | DRAM, pJ/B | rms over 392 configurations, W |
|---|---|---:|---:|---:|---:|---:|
| aifoundry3 | published (rails raw; reproduced to 1e-14) | 0.1810 ± 0.0025 | 0.043 | 0.294 | 72.7 | 0.308 |
| aifoundry3 | **A: the minion rail net, the registered rule** | **0.2166 ± 0.0023** | 0.075 | 0.342 | 72.4 | 0.282 |
| aifoundry3 | Au: the same, unfiltered rise | 0.2370 ± 0.0025 | 0.096 | 0.364 | 72.9 | 0.290 |
| aifoundry3 | B: the minion rail net, the rail ledger's drift | 0.1947 ± 0.0024 | 0.055 | 0.312 | 72.6 | 0.295 |
| aifoundry3 | Q136(b)'s `measured_split_filtered` (every rail and the board on their drift; reproduced to 3e-12) | 0.2070 ± 0.0023 | 0.066 | 0.331 | 72.5 | 0.287 |
| aifoundry1-c1 | published (reproduced to 2e-15) | 0.1022 ± 0.0037 | 0.540 | 0.205 | 81.6 | 0.478 |
| aifoundry1-c1 | **A** | **0.1428 ± 0.0038** | 0.594 | 0.261 | 81.0 | 0.471 |
| aifoundry1-c1 | Au | 0.1642 ± 0.0040 | 0.624 | 0.282 | 82.1 | 0.486 |
| aifoundry2 | published (reproduced to 1e-14) | 0.1879 ± 0.0027 | 0.034 | 0.291 | 72.7 | 0.332 |
| aifoundry2 | **A** | **0.2527 ± 0.0025** | 0.091 | 0.382 | 71.1 | 0.291 |
| aifoundry2 | Au | 0.2830 ± 0.0028 | 0.130 | 0.408 | 72.2 | 0.327 |
| aifoundry2 | B | 0.2243 ± 0.0025 | 0.065 | 0.343 | 71.8 | 0.297 |
| aifoundry2 | Q136(b)'s `measured_split_filtered` (reproduced to 9e-12) | 0.2341 ± 0.0024 | 0.070 | 0.360 | 70.9 | 0.295 |

Every footing that takes the rails' heating off through the rail's filter (A, B and Q136(b)'s) fits the 392 configurations better
than the published one, as Q136(b) found for its own, and A fits best on aifoundry3 and aifoundry2; the unfiltered Au fits worse on
card 1 (0.486 W against 0.478). The minion coefficient on a footing like the TensorFMA ledgers' own is therefore **0.19-0.24 on
aifoundry3** (B to Au; A 0.217), not 0.181, and **0.14-0.16 on card 1** (A to Au), not 0.102. These are post hoc readings of the same
committed rows; the published fit is not replaced, and Q136(b)'s E77-and-E120 band for aifoundry2 (0.175 [0.151, 0.199], at 600 MHz
and 52-55 °C, after its fan swap) is a different operating point from the catalogue's 26 Sep rows (about 74 °C there).

### 1.5 The TensorFMA cross-cut under each fit (W, with the share of the board)

The ledgers' lines do not move: only the cross-cut that splits "off-rail above rest" into the fit's terms and the named gap does.

| step (session) | card | off-rail above rest | the fit's minion term, published | SRAM + mesh terms, published | named gap, published | the fit's minion term, A | named gap, A | named gap, Au | named gap, Q136(b)'s fit |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| `fp32.randn` (E171) | aifoundry3 | 4.98 | 3.86 (7.3%) | 0.060 | +1.06 (+2.0%) | 4.62 (8.7%) | +0.28 (+0.5%) | -0.16 (-0.3%) | +0.49 (+0.9%) |
| `fp16.randn` (E171) | aifoundry3 | 4.27 | 3.53 (7.0%) | 0.054 | +0.69 (+1.4%) | 4.22 | -0.02 (-0.0%) | -0.43 (-0.8%) | +0.17 (+0.3%) |
| `int8.full` (E171) | aifoundry3 | 1.35 | 1.48 (4.1%) | 0.016 | -0.14 (-0.4%) | 1.77 | -0.44 (-1.2%) | -0.61 (-1.7%) | -0.36 (-1.0%) |
| `anchor_pi` (E171) | aifoundry3 | 1.54 | 1.57 (4.3%) | 0.019 | -0.05 (-0.1%) | 1.88 | -0.37 (-1.0%) | -0.55 (-1.5%) | -0.28 (-0.8%) |
| `fp32.randn` (E172) | aifoundry1-c1 | 3.71 | 2.19 (3.7%) | 0.185 | +1.33 (+2.2%) | 3.06 (5.1%) | +0.43 (+0.7%) | -0.04 (-0.1%) | - |
| `fp16.randn` (E172) | aifoundry1-c1 | 3.29 | 1.98 (3.5%) | 0.167 | +1.14 (+2.0%) | 2.77 | +0.33 (+0.6%) | -0.10 (-0.2%) | - |
| `int8.full` (E172) | aifoundry1-c1 | 0.91 | 0.83 (2.0%) | 0.040 | +0.04 (+0.1%) | 1.16 | -0.30 (-0.7%) | -0.48 (-1.1%) | - |
| `anchor_pi` (E172) | aifoundry1-c1 | 1.08 | 0.89 (2.1%) | 0.080 | +0.10 (+0.2%) | 1.25 | -0.26 (-0.6%) | -0.45 (-1.1%) | - |
| `fp32.ones` (E78) | aifoundry3 | 1.44 | 1.59 (4.4%) | 0.022 | -0.17 (-0.5%) | 1.90 | -0.49 (-1.4%) | -0.68 (-1.9%) | -0.41 (-1.1%) |
| `int8.ones` (E78) | aifoundry3 | 0.44 | 0.67 (2.2%) | 0.001 | -0.23 (-0.8%) | 0.80 | -0.36 (-1.2%) | -0.44 (-1.4%) | -0.33 (-1.1%) |
| `fp32.ones` (E82) | aifoundry1-c1 | 1.13 | 0.86 (2.0%) | 0.080 | +0.19 (+0.4%) | 1.21 | -0.16 (-0.4%) | -0.35 (-0.8%) | - |
| `int8.ones` (E82) | aifoundry1-c1 | 0.37 | 0.36 (1.0%) | 0.013 | -0.01 (-0.0%) | 0.51 | -0.15 (-0.4%) | -0.23 (-0.6%) | - |

Every item is in [`posthoc-note1-q145a.txt`](posthoc-note1-q145a.txt), F3. Over every non-zeros TensorFMA item (E82's `fp32.pi`, the
flagged transient, aside), the named gap reads -0.24 to +1.06 W (-0.8% to +2.0% of the board) on aifoundry3 and -0.02 to +1.35 W
(-0.1% to +2.3%) on card 1 with the published fit, and **-0.56 to +0.28 W (-1.6% to +0.5%) and -0.31 to +0.45 W (-0.7% to +0.7%) on
footing A**. No fit closes every item: the published one leaves the random steps high, footing A leaves the one-number and int8 steps
low. On footing A every item's gap is within twice the fit's own rms (0.28 W a configuration on aifoundry3, 0.47 W on card 1); on
the published fit the random steps' gaps are 2.8-3.4 times its rms (0.31 and 0.48 W).

**So the README's "the named gap is 2.0% (2.2% on card 1)" is the published fit's reading, made on raw rails.** On a footing like the
ledgers' own (A) it is **+0.28 W, 0.5% of the board, for fp32 random on aifoundry3 and +0.43 W, 0.7%, on card 1**, and between -0.3% and
+0.9% across the lab's net footings. The regulators' line on the data-dependent and awake watts reads 3.86 W (7.3%) on the published
fit's minion term and 4.62 W (8.7%) on footing A's (card 1: 2.19 W, 3.7%, and 3.06 W, 5.1%). The README's heat bullet ("3.9 W, 7.4%,
on aifoundry3; 2.4 W, 4.0%, on card 1") becomes 3.86-4.62 W (7.3-8.7%) and 2.19-3.06 W (3.7-5.1%), with section 3's labels. The books
still close by construction; what a bottom-up ledger can be checked against is the measured rail lines (the minion rail's data line
at ±0.15 W), not a gap whose size and sign depend on the fit's footing.

## 2. The vector rows' named gap is the fit's own residual (minor)

All 36 vector rows (12 configurations on 3 cards) are rows of the section 4.3 fit's own 392-configuration sets, and each row's named
gap equals the fit's residual on that row to 6e-15 W (0.0015 W against `unmetered_fit.json`'s `per_config`, which is rounded to three
decimals). The README's "-0.8 to +1.2 pJ an instruction (under 1% of the board) on the vector rows" are therefore small because the fit
was made on these rows, not because the books close independently: **only the TensorFMA gaps are tested on data the fit did not use**,
and those on a footing it was not made on (section 1.5).

## 3. The regulators' line is the fit's minion term; its SRAM and mesh terms are unmetered watts it attributes (minor)

The README's cross-cut "the regulators' conversion loss ... (section 4.3's fit: 0.181 x minion + 0.043 x SRAM + 0.294 x NoC)" is the
whole fit. The energy manual says of its mesh term: "The mesh coefficient is not all regulator: 29% is too much for a delivery loss"
(04a-fine-grain.md line 212), and card 1's SRAM term, 0.540 W per SRAM-rail watt, is no regulator's loss. So the line is renamed:
**the regulators' conversion loss is the fit's minion term alone; the SRAM and mesh terms are unmetered watts the fit attributes to
SRAM and mesh activity, not all of them regulator.** The named gap (the off-rail above rest less the whole fit) does not change. For
fp32 random, on the published fit: aifoundry3 3.863 W minion term (7.3% of the board) and 0.060 W SRAM + mesh (1.5% of the fit's
3.923 W); card 1 2.191 W (3.7%) and 0.185 W (7.8% of its 2.376 W). Section 1.5's table gives them for the other steps and on footing A.

## 4. Scope: the meter's note is owed, and E82's board ratio (minor)

- **The meter's dated note is owed, not written.** The map's step 6 asked for one beside this anatomy: one fixed board-meter current
  gain in the public PMIC firmware for every board; the rails cannot place the card term; E64's fitted 1.3 s on aifoundry2 against E58's
  measured filter plus one pass. This lane wrote one sentence of it (the README's card-ratio bullet) and listed E64's filter as not
  applicable. It is owed to round B, or to a lane the orchestrator names.
- **The board ratio after V², beside E82's** (the Builds-on rule (2)). E82 read card 1's board at 1.061 times aifoundry3's after each
  card's V² on 31 Oct: (521.7 / 498.7 mV)² / 1.031, the median D ratio over 32 kinds that switch 5 W or more, on E82's registered
  footing (its README lines 20 and 298-299; its interquartile 1.025-1.034 makes that 1.058-1.068). This anatomy's pool-8 steps read
  **1.057** (fp32 random), **1.057** (fp16 random), **1.047** (`anchor_pi`) and **1.039** (`int8.full`), and E78's and E82's own kinds,
  re-read here on Q139(u)'s footing, 1.025-1.056 (F5). So the 1.04-1.06 agrees with E82's 1.061, five days later: the random steps
  sit at the bottom of E82's interquartile range, and `anchor_pi` and `int8.full` a little below it, inside its extremes across kinds
  (1.006-1.080 in D, 1.013-1.088 after V²). The cause of card 1's excess is no better placed.

## 5. The card's own fan: assumed, not concluded (minor)

The README's "So no fan draws from the card's metered 12 V, and every line above is on the card" should read: **the ledger assumes
that no fan draws from the card's metered 12 V.** aifoundry2's card is recorded passive (findings 14, 9 Oct), and the V3 card's public
documentation lists no fan, but aifoundry3's and aifoundry1's cooling is not recorded; a card-powered fan there is not excluded, and its
draw would sit inside "at rest, off the three metered rails". The board's MAX6660 (a remote-diode temperature sensor and fan-speed
regulator) has three uses in the public PMIC firmware (et-boards `e5e0cf2`, `firmware/et-soc1-pmic`), not one: a CLI test command that
writes and reads it (`cmdU`, `runtime/PowerManager/src/IoTask.c` lines 1145 and 1170-1177); the PMIC's temperature-alert interrupt
(`POWER_ALERT_TEMPERATURE`, "EIC interrupt event from temperature sensor MAX6660", `runtime/PowerManager/inc/power_manager_event.h` line
50; pin `TEMP_ALERT_IN`, `power_manager_event.c` line 53; handled by `handleTemperatureAlert`, `IoTask.c` line 210); and a CLI register
dump (`dumpFan`, `runtime/CLI/src/CLITask.c` lines 733 and 1084-1095). The ledger's own label, "assumed none (recorded on aifoundry2
only)", was the right one.

## 6. The nits (none moves a headline number)

- (a) **The NOTE's virus loop.** Not "20 pairs a loop": the loop's inner block is 24 `fmadd.ps` (12 pairs, destinations f4-f27), run 20
  times (240 pairs, 480 instructions) before each gold check. The triples alternate across the blocks' boundaries too, so the flip
  counts stand. The companion note says so beside the NOTE.
- (b) **"Gap below 1e-13 W" in every ledger:** the TensorFMA ledgers close to 1.4e-14 W; the 36 vector ledgers close to 6.7e-7 W, from
  the catalogue's six-decimal rounding.
- (c) **The SRAM rail's 0.54 s arm** moves the SRAM lines by up to 0.0275 W, not "0.02 W at most".
- (d) **The NoC line above zeros** spans 0.010-0.357 W over every non-zeros item (E171 0.041-0.191, E172 0.077-0.357, E78 0.010-0.194,
  E82 0.031-0.342), not "0.04-0.36 W".
- (e) **The voltages behind the electrons.** "minion 521.6 mV on aifoundry3, 499 mV on card 1" are the sessions' means (`e171.json` and
  `e172.json` `v_mean`, 0.52161 and 0.49866 V). Each ledger and each V² ratio uses its own item's window voltage (fp32 random: 521.0 and
  498 mV). So the fp32 random step's data-dependent minion line, 17.585 nJ, is 2.107e11 electrons at 0.521 V (2.104e11 at 0.5216 V).
- (f) **The combined "SRAM and NoC" rows** of the first table show the SRAM rail's 0.698 V, but their electrons are each rail's at its own
  voltage, added: awake 5.75e8 at 0.698 V and -1.85e8 at 0.484 V; data 9.73e8 at 0.698 V and 2.21e9 at 0.484 V.
- (g) **The script's docstring** leaves out its required `--md` option and says it writes only `--out` and `--txt`; it writes all three
  (`--out`, `--txt`, `--md`), as the README's re-make command gives them. It reads two of the clones in `external/` (et-platform's
  `kernel.h` and core-et's `ps/kernel.h`); et-man's card schematic is cited, read by hand, and its 1 mOhm sense resistor is a constant
  in the script.
- (h) **"The clocks and always-on switching at rest"** (the at-rest board less the idle law's leakage) is the temperature-independent
  part of the rest: the clocks and always-on switching, but also the PHYs' and regulators' static draw and DRAM refresh.

## Files of this note

- [`posthoc_note1_q145a.py`](posthoc_note1_q145a.py): the re-run, pure Python, committed files only (this directory's `anatomy.json`,
  the catalogue, its raw V3-CATFULL telemetry, `unmetered_fit.json`, Q136(b)'s `recut.json`, `e171.json`, `e172.json` and
  et-platform's `kernel.h` in `external/`). About 5 s on one core. From the top of the repository:

  ```
  python3 -I docs/reports/data/2026-11-05-q145a-anatomy-top-lines/posthoc_note1_q145a.py --repo . \
    --out docs/reports/data/2026-11-05-q145a-anatomy-top-lines/posthoc-note1-q145a.json \
    --txt docs/reports/data/2026-11-05-q145a-anatomy-top-lines/posthoc-note1-q145a.txt
  shasum -a 256 -c docs/reports/data/2026-11-05-q145a-anatomy-top-lines/SHA256SUMS-note1
  ```
- [`posthoc-note1-q145a.json`](posthoc-note1-q145a.json) and [`posthoc-note1-q145a.txt`](posthoc-note1-q145a.txt): every number above,
  with the inputs' sha256.
- [`NOTE-2026-11-05-fmadd-ps-public-facts.md.dated-note-1.md`](NOTE-2026-11-05-fmadd-ps-public-facts.md.dated-note-1.md): the NOTE's
  corrections.
- `SHA256SUMS-note1`: this note's five files. The README's `SHA256SUMS` (6 of 6) is unchanged.

*Compute for this note:* slot jobs on the Intel, one at a time, at nice 10, one core each, each under 10 s; no bench, no mini, no lab box.
