# Q129's waterfall — one random fp32 multiply-add, rebuilt bottom up

## Results

*Desk work on the Intel, Wed 28 Oct 2026 (week 44). No card, no simulation, no re-reduction: every number
below is read at build time from a committed Q129 data directory by `waterfall.py`, which writes
`waterfall-v2.json` and is what the page's own `build_data.py` reads. Nothing here was pre-registered,
because it is an assembly of seven measurements made for seven separate questions.*

**Q128's waterfall named 1.95 of the board's 5.78 pJ. This one names 3.97–4.19 pJ of them:**

> ### the remainder against the board falls 3.84 pJ → **0.72–0.94 pJ** (band 0.34–1.28)
> ### and against the minion rail 2.39 pJ → **0.58–0.81 pJ**

**and the largest row it adds is a model the card's own zeros measurement already contradicts**, so the
true remainder is bigger than those numbers by whatever that model over-prices. That is the honest
headline, and it is why no single closure percentage appears here without its band.

| | Q128, 27 Oct | Q129, 28 Oct | band |
|---|---:|---:|---:|
| at the board (E38, 3 cards) | 5.783 pJ | 5.783 pJ | — |
| at the minion rail | 4.337 pJ *carried from E60* | **4.774 pJ measured** | 4.55–4.95 |
| the lane's arithmetic, bottom up | 1.946 pJ | **2.705 pJ** | 2.39–3.03 |
| the lane's transport | *not counted* | **1.261–1.484 pJ** | — |
| accounted, on the rail | 1.946 pJ | **3.966–4.190 pJ** | 3.65–4.51 |
| closure against the rail | 44.9% | **83.1–87.8%** | 73.7–99.1% |
| closure against the board, with the regulators' step | 33.7% | **83.7–87.6%** | 77.9–94.1% |

## The rows, and what each one is

### The board-to-rail step: 1.01 pJ, measured, and *smaller* than Q128 assumed

Q128 put the minion rail at 4.337 pJ — 0.75 × the board, carried across from E60's per-flipped-bit ratio.
Q129's rail ledger measures it from E38's own telemetry on two cards: **4.774 pJ, band 4.55–4.95**
(ratio 0.825 [0.787–0.856]; per card 4.62 aifoundry2 / 4.93 aifoundry3). The whole band sits inside
Q128's own stated 0.70–0.89 spread, so nothing in Q128 is contradicted — the 0.75 was at the bottom of
what the multiply-add shows. Because the rail is bigger, the step below it **shrinks** from 1.446 to
1.01 pJ, and the four rows sum to it exactly:

| row | pJ, central footing | over the three footings |
|---|---:|---|
| the regulators' delivery loss + logic in step with the rails | 0.875 | 0.859–0.935 |
| the SRAM rail | 0.011 | **withdrawn as a switching energy** |
| the NoC rail | −0.019 | **withdrawn as a switching energy** |
| the off-rail fit's residual | 0.142 | −0.230 … +0.259, consistent with zero |

The SRAM and NoC rows are withdrawn because their whole window delta is their own leakage rise (66%/61%
and 100%/103% of it): at most 0.13 pJ together, about zero centrally. The residual is the fit's residual
and nothing else — it changes sign between sibling configurations of one pattern on one card and is
negative in 12 of 16 configurations on aifoundry3. **"4.5% of the board is on no meter" is withdrawn.**

### The lane's arithmetic: 2.705 pJ, measured end to end — and why the three wire rows are *one* row

Three Q129 directories priced the same capacitance at three stages of knowledge. Only the last is in the
ledger; the first two are the reconciliation that shows it is the same measurement reached another way.

| | pJ | what it is |
|---|---:|---|
| Q128's bottom-up count | 1.9465 | Steiner wire estimate, 50.5% of the farads priced, no glitches |
| the routed wire (Q129(a)) | −0.137 | wire between the cells 0.590 → 0.453 pJ at Miller *k*=1 |
| the capacitance that was unpriced (Q129) | +0.101 | the nets CTS and `repair_design` made after the simulation |
| **walked forward** | **1.910** | |
| **Q129(b)'s own measured zero-delay** | **1.925** | the routed netlist against the extracted per-net table |
| | **+0.015** | how far apart the two roads land |
| **+ the measured glitch factor** | **+0.781** | ×1.331 energy, ×1.572 toggles at the whole unit |
| **= the lane's arithmetic** | **2.705** | band 2.39 (*k*=0) – 3.03 (*k*=2) |

**Do not add the first two rows to the last.** Q129(b) simulates the *routed* netlist against the
extracted per-net table, so it prices 100% of the extracted farads and every glitch in one pass: both
earlier deltas are inside it. Adding them again double-counts.

Two findings inside that row are worth carrying separately. The global-route Steiner estimate was never a
coupling-free floor — the ORFS asap7 `setRC.tcl` hands it 0.1658 fF/µm, a layer's *total* capacitance with
neighbour coupling bundled in and grounded, so it runs **20–23% above** the extraction and closing the
routing blocker *widened* the gap by 0.137 pJ. And the glitch factor is strongly activity-dependent:
×1.002 with the operands held still, ×1.232 at *h*=8, ×1.572 at random, with a measured ×1.000 on the
clock tree. No single factor transfers to a load whose activity is not random's.

### The lane's transport: 1.261–1.484 pJ, the biggest single mover, and the weakest row

Q128's ledger covered one lane's multiplier and adder. The board also pays for the lane's register files,
operand bus, result path and control, and Q129(scope) synthesised and simulated those: **1.033 pJ
switching, 1.484 pJ with the cells' internal energy**. That is 32.9–38.7% of Q128's entire 3.837 pJ gap —
more than the glitch factor, the routed wire and the unpriced capacitance put together.

*It is a range, and the range is its own clock nets.* 63% of the transport's switching survives zero
operands (0.654 of 1.033 pJ): 0.223 pJ of clock nets and 0.431 pJ of signal. The signal two thirds is the
accumulator index sweeping 2*i*+*h* through a 64-entry read mux tree, which the card performs in the same
micro-op order with zero data, so no idle subtract can contain it — it belongs in "over idle". The clock
third belongs there only if the lane's register-file clock branches are gated when the card idles, and
that is unmeasured on silicon. Hence 1.261 pJ (clock nets removed) to 1.484 pJ (all of it).

*The glitch factor is deliberately not applied to it.* That netlist has no detailed route, no SDF and
37.0% of its capacitance priced, so no glitch factor was measured on it. At ×1.33 the ledger would read
4.38–4.68 pJ, 92–98% of the rail — on top of a register-file row that is already over-priced.

*And it is over-priced.* The 0.4815 pJ/MAC register-file array is a standard-cell latch array standing in
for a compiled macro. In the zeros stimulus, one lane's transport model costs 0.654 pJ where the **whole
board** costs 0.27 pJ per multiply-add over idle (E38, per card 0.163 / 0.403 / 0.251) — 2.42×, or 1.60×
on its signal part alone, and the register-file row by itself is 1.13×. So this is a *violated* ceiling,
not an open-ended one, and a true accounting sits **below** the bottom of every range on this page.
E74 (28 Oct) bounds the cell bit at **e_cell < 2.73 fJ (95%)** but not the array's own per-MAC energy.

### Leakage is not a row

"Over idle" is already a leakage-corrected quantity: E38's registered metric subtracts
leak × (*t*<sub>early</sub> − *t*<sub>launch</sub>) from each window, so the window's own die heating is
out of the board figure before anything divides it. What Q129 adds is the slope's band. Re-footing the
whole rail ledger on three slopes moves it 4.774 (E38's registered 0.81/0.55 W/°C) → 4.723 (this ledger's
measured within-run 0.725/0.358) → 4.690 pJ (E66's measured idle 0.294 on aifoundry2): a **0.084 pJ
spread, 1.8%** — smaller than every other band here.

What *did* change is the understanding of the slope itself. E66 measured aifoundry2's idle slope at
0.2936 W/°C over 51–58 °C; E71 measured aifoundry3's at **0.3803 ± 0.0036 W/°C over 58–62 °C**, the band
E65 and E67 actually launched in, and re-fitted aifoundry2's own coolings over the same band at
0.3452 (sd 0.0112 over 18 passes, per-pass 0.3183–0.3613). About three fifths of the gap between the two
published figures is the temperature band, not the card (69.5% measured the other way round). **A leakage
slope is not a card constant**: it rises about 0.009 W/°C per °C of die temperature on aifoundry2 and
0.011 on aifoundry3 over 51–65 °C, so a correction quoted without its band is ambiguous at the 20–30%
level — larger than the 10% card-to-card difference it is usually invoked for. The registered estimator's
1.508 W/°C is 4.0–5.1× every measured idle slope and stays refuted.

## What is still unaccounted, and what it would take

0.58–0.81 pJ against the rail, 0.72–0.94 pJ against the board, on the central footing at Miller *k*=1
(0.04–1.30 and 0.34–1.28 over the whole band), where Q128 had 2.39 and 3.84. Of Q126(e)'s three reasons
the bottom-up figure was a floor, two are now closed — Q129(a) retired the coupling/SPEF one (and found
it pointed the other way) and Q129(b) retired the coverage one, at 100% of the extracted farads on a
routed design. The third stands in a narrower form: the transport netlist is itself a floor on the same
three axes the arithmetic netlist has cleared.

Four things would close the rest, in the order they matter:

1. **E74's register-file array measured rather than modelled**, or a compiled-macro energy figure. It is
   the largest row in the ledger and the only one a card measurement has already contradicted.
2. **E77, the rail ledger's matched hart ladder** — the only way to split the published 0.875 pJ
   "delivery loss + in-step logic" row into the regulators' conversion loss and off-rail logic. Its plan
   is rebuilt and matched (arm B = 0.523 × arm A harts), and it needs a governor move on aifoundry2 card 0
   under the field manual's gates, including the rule-8 firmware read that can make it NO-GO.
3. **A detailed route, an SDF and a glitch measurement on the transport netlist**, which would do for the
   transport row what Q129(a) and Q129(b) did for the arithmetic — and might move it in either direction.
4. **Whether the lane's register files are clock-gated at idle on silicon**, worth 0.223 pJ: the whole
   width of the transport range.

## Reproduce

```bash
python3 docs/reports/data/2026-10-28-q129-waterfall/waterfall.py . \
        docs/reports/data/2026-10-28-q129-waterfall/waterfall-v2.json
python3 docs/reports/data/2026-10-27-matmul-to-transistor/build_data.py . \
        docs/reports/data/2026-10-27-matmul-to-transistor/data.json
python3 scripts/build-report.py matmul-to-transistor \
        docs/reports/data/2026-10-27-matmul-to-transistor/data.json \
        docs/reports/2026-10-27-matmul-to-transistor.html
```

`waterfall.py` asserts the four board-to-rail rows sum to the step, and that the two roads to the
zero-delay arithmetic figure land within 0.02 pJ of each other; either failing stops the build.

## Q128's version is kept

`docs/reports/data/2026-10-27-matmul-to-transistor/data-2026-10-27-q128.json` is the data block the
27 October page was built from, byte for byte. `data.json` carries both: `waterfall` is Q129's and
`waterfall.v1` is Q128's four steps, its 4.337 pJ rail and its 3.837 pJ remainder, so the old page
rebuilds from either file.

## Sources

| row | directory | commits |
|---|---|---|
| board 5.783 pJ, zeros 0.27 pJ | `2026-10-27-transistor-ledger` (E38 registered means, 3 cards) | — |
| the rail and the board-to-rail step | `2026-10-27-q129-rail-ledger` | `68c50c37`, `b8b8691c` |
| the routed wire | `2026-10-27-q129-routed-netlist` | `273fe126`, `01964253` |
| the capacitance that was unpriced | `2026-10-27-q129-unpriced-capacitance` | `e7a2cbc2`, `6e154623` |
| the glitch factor, waterfall (C) | `2026-10-27-q129-glitch` | `4a6a840a`, `2778b089` |
| the lane's transport | `2026-10-27-q129-ledger-scope` | `39315c56`, `936b0b88` |
| the leakage slopes | `2026-10-27-e66-idle-long`, `2026-10-27-e71-idle-slope-aifoundry3` | `5db5f5d9` |
| the register-file cell bound | `2026-10-28-e74-register-file-cells` | — |

## Departures

- **D1 (28 Oct).** Nothing here is pre-registered. It is an assembly of seven post-hoc reductions, each
  pre-registered in its own directory where it was a card run, and the assembly's own arithmetic is
  asserted in code rather than scored against a frozen prediction.
- **D2 (28 Oct).** The internal-energy terms of Q129(b)'s waterfall (C) — 0.4127 pJ zero-delay and
  0.6933 pJ timed — are read as constants from that directory's `summary.txt` rather than from a JSON,
  because it publishes them only there. Every other number is read from a JSON.
- **D3 (28 Oct).** The transport row's internal-energy estimate uses the *arithmetic* netlist's cell mix,
  deliberately: it is what lets the two ledgers add. Its own mix would raise that row 2.1%.
