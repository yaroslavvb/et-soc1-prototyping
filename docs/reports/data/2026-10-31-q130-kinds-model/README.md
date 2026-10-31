# Q130(c) — the explanation model: every kind's power and clock, predicted before E78 and E80 run

*Sat 31 Oct 2026 (week 44), desk lane of Q130, on the Intel. **No card was touched, claimed or set.** Every
number here is a prediction computed from already-committed measurements by [`model.py`](model.py), frozen for
**E78** (aifoundry3, 600 MHz pinned) and **E80** (aifoundry2, its own governor, no governor move). Model id
`Q130C-M1`. The kinds and tiles are Q130(s) revision 2, commit `7d9c0d9e`, which is where the pre-registration
clock starts.*

> 🛑 **Nothing in this file is a measurement.** It is the frozen prediction E78 and E80 are scored against.
> A prediction that fails is reported as failed.

## Results

**One model, three fitted numbers on the fp32 side and one more per narrow format, predicting all 51 kinds:**

```
dW(kind) = U_T·(1 − g)                       the lane the gate did not switch off
         + Φ(S_A; WA_T) + Φ(S_B; WB_T)       the operand bits, saturating per side
         + σ_T·q                             the product's SIGN, which no operand price can see
```
over that type's own zero-data level, at 600 MHz and 521.8 mV on aifoundry3 — E78's own operating point, so
the fp32 arm needs no card or clock conversion at all. `Φ(S; W) = W(1 − e^(−S/W))` is E70's selected coverage
law; `S_A`, `S_B` are E70's own additive sums, generalised from one mask to a whole per-position flip
histogram; `g` is the gated fraction of the 4,096 column-slot-cycles of one op; `q` is the rate at which the
*product's* sign changes.

| fitted | value | fitted on |
|---|---|---|
| `WB` | **6.965 W** | E70's `nrd_b` 10.785 ± 0.024 W — random B against a constant A |
| `WA` | **5.392 W** | E70's `nrd_a` 7.209 ± 0.015 W — random A against a constant B |
| `σ` | **8.165 W** | E64's fp32 `signs` (±1.0f), 13.10 W over zeros |
| `U` fp32 | 8.555 ± 0.060 W | *read off*, not fitted: E67's and E70's own anchors |
| cross-side overlap | **declared 0** | a fitted one came out at −0.029 — zero to within 3% |
| `α_fp16`, `α_int8` | **1.473**, **0.670** | E64's fp16 `randn` and int8 `randn` (= `full`), one point each |
| `U_fp16`, `U_int8` | **8.463 W**, **0.571 W** | E64's (ones − zeros) per format, one run each |

**Four results, before any card runs.**

1. **fp32 `randn` — the headline kind — is an out-of-sample check, and it passes to 1%.** The model's three
   fp32 numbers come from E70's two *one-sided* random-operand steps and from `signs`. Put a random operand on
   *both* sides and it predicts a flip term of **15.951 W** against the measured **16.104 ± 0.37 W**
   (`inventory.json` > `zeros_random_split`): **−0.15 W, −0.95%, inside the measurement's own error bar**. The
   two sides simply add; there is no interaction term to fit.

2. **The model transfers between the two cards to 0.03 W.** E70 measured the one-sided random-operand steps on
   **aifoundry3** (7.209 and 10.785 W at 600 MHz / 521.8 mV). Carried to **aifoundry2** by the one registered
   rule — the dynamic term at `V²` with `f` fixed, `×(0.5218/0.517)² = 1.01865` — and added to the un-gating
   term, they predict E64's `a_randn_b_ones` **15.76 W** against its measured **15.73 W**, and
   `a_ones_b_randn` **19.34 W** against **19.31 W**. Two different cards, two different campaigns, four weeks
   apart, **0.03 and 0.02 W**. The same rule carries E64's fp32 (randn − zeros) 24.200 W to **24.661 W**
   against E67's own anchors' **24.659 ± 0.37 W**.

3. **The sign bit is the cheapest bit on the operand bus and one of the dearest in the array, and no price
   list can see it.** E65's bit 31 costs **0.56 W** a position against mantissa bit 22's **4.63 W** — the
   cheapest of the 32. But E64's `signs` (±1.0f, where the sign is the *only* thing that moves) costs
   **13.10 W over zeros**, of which only 8.555 W is the lane being on: the remaining 4.5 W is bought by
   ~0.5 sign changes a column-slot-cycle. Priced as one number that is **σ = 8.165 W** per fully-toggling
   product sign — **15× the operand-bus price of the bit that causes it**. The mechanism is that a sign change
   flips the sign of the *product*, hence the whole width of the adder's input, and E65's and E67's masks were
   every one of them measured against a **constant** other operand, where the product's sign never moves.
   E65 says the same thing from the other side: the same B mantissa bit costs **3.2× more** when the held A
   operand is `pi` than when it is `1.0` (`reduce.txt`, `bits (A=pi)` against `bits (A=1.0)`).
   Without this term the model misses `signs` by **−3.95 W**; with it, out-of-sample rms over E64's eight
   other measured fp32 kinds is **1.07 W** (median 5.4% of the value).

4. **int8's lane un-gating term is 15× smaller than fp32's: 0.571 W against 8.555 W.** E64's int8
   (ones − zeros) is **0.56 W** where fp32's is 8.73 and fp16's 8.31. int8 runs on **TIMA with the txfma clock
   off** (`vpu_tensorfma.v:157-166`, `:626-628`), so almost all of what fp32 pays merely to *have a live lane*
   is never switched on. Consequence: **the zero gate is nearly worthless in int8** — not only because the
   gate rate is `~p⁸` there (Q130(s) fact 4) but because what it would switch off costs 0.57 W, not 8.56.
   This rests on **one E64 run per point** (± 1.19 W) and is this file's registered rule **R4**, the one most
   likely to fail.

### The speed path reproduces E64's own nine measured sustained clocks to 3.6 MHz

Burst is E64's **registered** governor (`surface_hpl.py simulate`, τ 1.3 s, pass 0.24 s) at the card's 65 W on
a cool die; sustained is **E64-T1** (`surface_hpl_t.py`) at γ = 3.0, with E66's leakage law in the power curve,
the die a state relaxing towards E64's thermal line **die = 41.88 + 0.4696 °C per W**, τ_th 14 s, and a thermal
limb that steps down on a pass reading ≥ 66 °C. Run on **E64's own fitted `c`**, the two simulations give:

| cell | `c` W | burst MHz | sustained MHz | measured sustained | residual |
|---|---|---|---|---|---|
| fp32/zeros | 1.44 | 800 | 800 | 800.0 | 0.0 |
| fp32/ones | 10.17 | 800 | 739 | 737.9 | +1.0 |
| fp32/randn | 25.64 | 700 | 600 | 600.0 | 0.0 |
| fp16/zeros | 1.39 | 800 | 800 | 794.4 | +5.6 |
| fp16/ones | 9.70 | 800 | 745 | 737.1 | +7.8 |
| fp16/randn | 23.28 | 715 | 600 | 600.5 | −0.5 |
| int8/zeros | 2.12 | 800 | 800 | 800.0 | 0.0 |
| int8/ones | 2.68 | 800 | 800 | 800.0 | 0.0 |
| int8/randn | 9.10 | 800 | 758 | 763.2 | −5.1 |

**3.64 MHz rms over the nine, 4.46 MHz over the six that are not clamped at 800.** So the speed column of the
kinds table is the switching watts put through a governor the lab has already closed; the uncertainty in a
predicted clock is almost entirely the uncertainty in the watts.

### The spine of the table (tier 1), predicted

`switching W` is over that type's own zero-data level, on aifoundry3 at 600 MHz; `burst` and `sustained` are
aifoundry2 MHz. Every value with its 95% interval and its `pJ per MAC` is in
[`predictions.json`](predictions.json), one record per `type/kind`.

| format | kind | gated | switching W | 95% | pJ/MAC | burst | sust | limit |
|---|---|---|---|---|---|---|---|---|
| fp32 | zeros | 1.000 | 0.00 | 0.00–0.30 | 0.000 | 800 | 800 | power |
| fp32 | a_randn_b_zeros | 1.000 | 0.00 | 0.00–0.30 | 0.000 | 800 | 800 | power |
| fp32 | sparse90 | 0.992 | 0.46 | 0.14–0.78 | 0.099 | 800 | 800 | power |
| fp32 | ones | 0.000 | 8.55 | 7.99–9.12 | 1.863 | 800 | 745 | thermal |
| fp32 | sparse50 | 0.774 | 9.50 | 7.58–11.42 | 2.069 | 800 | 728 | thermal |
| fp32 | pow2 | 0.000 | 13.19 | 11.93–14.46 | 2.874 | 800 | 681 | thermal |
| fp32 | nn_like | 0.508 | 16.00 | 13.04–18.97 | 3.486 | 785 | 649 | thermal |
| fp32 | smallint | 0.118 | 17.39 | 14.91–19.88 | 3.789 | 770 | 639 | thermal |
| fp32 | randn_sorted | 0.000 | 22.77 | 19.24–26.29 | 4.959 | 706 | 600 | thermal |
| fp32 | bf16trunc | 0.000 | 23.26 | 19.62–26.90 | 5.067 | 706 | 600 | thermal |
| fp32 | randn | 0.000 | 24.21 | 20.34–28.08 | 5.274 | 700 | 600 | thermal |
| fp16 | zeros | 1.000 | 0.00 | 0.00–0.30 | 0.000 | 800 | 800 | power |
| fp16 | ones | 0.000 | 8.46 | 6.05–10.88 | 0.922 | 800 | 745 | thermal |
| fp16 | wsparse50 | 0.760 | 9.04 | 4.60–13.48 | 0.985 | 800 | 735 | thermal |
| fp16 | sparse50 | 0.414 | 15.51 | 8.75–22.27 | 1.689 | 794 | 656 | thermal |
| fp16 | nn_like | 0.195 | 19.38 | 11.28–27.48 | 2.111 | 752 | 621 | thermal |
| fp16 | pair_half_zero | 0.000 | 20.94 | 12.79–29.09 | 2.280 | 727 | 608 | thermal |
| fp16 | randn_sorted | 0.000 | 21.44 | 12.99–29.90 | 2.335 | 715 | 604 | thermal |
| fp16 | randn | 0.000 | 22.30 | 18.91–25.68 | 2.429 | 715 | 600 | thermal |
| int8 | zeros | 1.000 | 0.00 | 0.00–0.30 | 0.000 | 800 | 800 | power |
| int8 | ones | 0.000 | 0.57 | 0.00–2.97 | 0.018 | 800 | 800 | power |
| int8 | neg_ones | 0.000 | 0.57 | 0.00–2.97 | 0.018 | 800 | 800 | power |
| int8 | wsparse50 | 0.644 | 3.27 | 0.94–5.60 | 0.104 | 800 | 800 | power |
| int8 | pos | 0.000 | 3.45 | 0.32–6.58 | 0.109 | 800 | 800 | power |
| int8 | sorted | 0.000 | 5.98 | 1.50–10.47 | 0.190 | 800 | 776 | thermal |
| int8 | sparse50 | 0.070 | 6.06 | 1.59–10.54 | 0.192 | 800 | 774 | thermal |
| int8 | ternary | 0.008 | 6.42 | 1.68–11.16 | 0.203 | 800 | 768 | thermal |
| int8 | full | 0.000 | 7.11 | 3.73–10.48 | 0.225 | 800 | 758 | thermal |
| int8 | smallint | 0.000 | 7.13 | 1.95–12.31 | 0.226 | 800 | 757 | thermal |
| int8 | gauss_q | 0.000 | 7.10 | 1.93–12.28 | 0.225 | 800 | 758 | thermal |

Three readings a blog can use. **The kind of number moves fp32's switching power 54×** (0.46 W for 90%-sparse
against 24.2 W for random normals) **and its sustained clock by 200 MHz**, 600 to 800. **Every int8 kind bursts
at 800 MHz** — none of them is dear enough to trip the 65 W power test — and the spread moves only the
*sustained* clock, 757 to 800. And **int8's whole range (0 to 7.1 W) sits below fp32's `ones`**, a kind that
computes nothing interesting at all.

## What is calibrated, and what is therefore out of sample

| arm | what it may use | what is fitted | what is out of sample |
|---|---|---|---|
| **fp32** | E65's B-side and E67's A-side 32-position price lists, E70's law and its two measured one-sided random steps, the zero-gate rule, E67/E70's anchors, and E64's own measured fp32 kinds | `WA`, `WB`, `σ` — **three** | all 18 kinds in `kinds.json`; and of E64's own ten, eight (only `signs` is fitted; `randn` is a check) |
| **fp16** | **E64's three kinds only**: zeros, ones, randn | `U_fp16`, `α_fp16` — **two** | **15 of 17 kinds** |
| **int8** | **E64's three kinds only**: zeros, ones, randn (= `full`) | `U_int8`, `α_int8` — **two** | **14 of 16 kinds** |

For fp16 and int8 there is no per-bit price list yet — E79 is measuring those now — so each element bit is
priced off **fp32's** list by field role, with the mantissa aligned at the **MSB** (a significand bit's price
is set by how many partial-product columns it drives, so the narrow format's array is the top of the wide
one: fp16's 10 mantissa bits take fp32's prices 13…22, int8's 7 magnitude bits take 16…22) and the exponent at
the **LSB** (it is a counter into one shifter). The whole list, the law's curvature **and** σ are then scaled
by one number per format,

> `β_T = r_T · α_T`, with `r_fp16 = 11/24` and `r_int8 = 8/24` — the significand width over fp32's —
> and α_T the only quantity fitted.

**α = 1 would mean the significand-width scaling is exactly right.** It comes out at **1.473 (fp16)** and
**0.670 (int8)**, so that rule is right to within a factor of 1.5 — which is registered rule **R5**, and
exactly what E79's own fp16/int8 price lists will falsify or confirm.

## The registered rules E78, E79 and E80 are scored against

Machine-readable in [`predictions.json`](predictions.json) > `decision_rules`.

| # | rule |
|---|---|
| **R1** | E78: measured switching power over the type's own zeros level is inside `switching_w_ci95` for ≥ 70% of the fp32 kinds run and ≥ 50% of the fp16/int8 kinds |
| **R2** | E78: the **order** is right — Spearman ρ of predicted against measured ≥ 0.90 within each format |
| **R3** | E78: the gate's signature — (sparse50 − wsparse50) ≥ 2 W in **both** fp16 and int8, and \|fp32 sparse50 − fp32 wsparse50\| ≤ 1.0 W, because in fp32 element sparsity **is** word sparsity |
| **R4** | E78: int8 (ones − zeros) ≤ 2.0 W against fp32's 8.555. **The sharpest structural prediction here and the likeliest to fail** — it rests on one E64 run per point |
| **R5** | E79: α_fp16 and α_int8 land in [0.5, 2.0] when re-solved against E79's own measured fp16/int8 per-bit prices |
| **R6** | E78: the product-sign term is real — fp32 `neg_ones` within 1 W of `ones` (every element is −1.0, so the product's sign never *changes*), while int8 `ternary` and `highbit`, whose signs do change, cost ≥ 1 W more than int8 `ones` |
| **R7** | E80: predicted burst MHz within 25 MHz for ≥ 70% of cells, and every cell predicted at 800 measures ≥ 790 |
| **R8** | E80: the sustained **limit** (thermal vs power) is called right for every cell, and the clock is within 40 MHz for ≥ 70% |
| **R9** | E78: the gate's **reach** — see below. Run it first |

### R9, and the one cell E78 should run first

The gate clears `ex_txfma_valid` and `vpu_lane.v` clock-gates the lane, so a gated column-slot-cycle does no
multiply. Whether it still pays its **operand bus** flips is not settled by any committed measurement, and it
is the single largest open term in this model. Both readings are carried:

| cell | `gate` arm (primary) | `bus` arm | spread |
|---|---|---|---|
| fp32 `a_zeros_b_randn` | 0.00 W | 10.78 W | **10.78** |
| fp16 `a_zeros_b_randn` | 0.00 W | 10.02 W | 10.02 |
| fp32 `a_randn_b_zeros` | 0.00 W | 7.30 W | 7.30 |
| fp32 `sparse50` | 9.50 W | 16.63 W | 7.13 |
| fp32 `sparse90` | 0.46 W | 6.71 W | 6.25 |
| fp16 `wsparse50` | 9.04 W | 15.05 W | 6.01 |

**`a_randn_b_zeros` decides it in one launch**: every lane is gated by the B side while the A operand bus keeps
moving 27,920 bits an op. The `gate` arm says ≈ 0 W over zeros; the `bus` arm says ≈ 7 W. The primary arm was
selected on E64's fp32 `sparse75`, the only measured kind that is mostly gated: the `gate` arm misses it by
**+0.83 W** and the `bus` arm by **+10.14 W**, and over E64's eight out-of-sample fp32 kinds the two arms score
**1.07 W** and **3.73 W** rms. That is a clear selection, but it rests on one mostly-gated kind, and the two
arms are a **binary declared choice**, not an interval. Every kind's value under the other arm is
`switching_w_alt_gating_arm`.

## Conversions, stated

| | rule | why |
|---|---|---|
| **card and clock** | `W(aifoundry3, 600 MHz, 521.8 mV) = c(aifoundry2, 600 MHz, 517 mV) × (0.5218/0.517)² = c × 1.01865` | the dynamic term at `V²` with `f` fixed, which is E64's own `s_f` at `f/600 = 1`; E72 — the price follows the voltage; E60's cross-card check 1.300 W predicted against 1.291 measured, 0.7%. Checked here to 0.03 W on `a_randn_b_ones` / `a_ones_b_randn` and to 0.002 W on fp32 (randn − zeros) |
| **leakage** | **it cancels**: every figure is a *difference* of two runs at a common die reading | the slope de-leaking the inputs is each campaign's own registered one — E65 0.182, E67 0.175, E70 0.1975 W/°C solved from their own runs; E64 E60's 0.442 W/°C constant referred to 58 °C. **Sensitivity arm:** E71's measured **0.3803 W/°C** on aifoundry3 over 58–62 °C, which moves every price down 2–5% and the un-gating term by 0.105 W against its own 0.060 W standard error |
| **voltage law for the die** | γ = 3.0 in the leakage term of the sustained simulation | E64-T1's best out-of-sample sustained rms (6.2 MHz over nine SUS cells) and the exponent E64's own within-run busy slope implies (3.12). γ = 0 and 2 are the sensitivity arms |
| **energy** | `pJ per op = ΔW / 1.1208 GHz_op`, and per MAC ÷ 4,096 (fp32), 8,192 (fp16), 16,384 (int8) | E70's measured whole-card TensorFMA rate at 600 MHz, held to 1.1208–1.1210 Gop/s over seven passes |

## Checks that ran

| check | result |
|---|---|
| all 51 tiles' sha256 against `kinds.json` | **51 / 51** |
| this file's own stream, gate and bus counter against `kinds.json` `stats.bus_bits_per_op` and `stats.gated_lane_frac`, every kind | **0 failures of 51** (and the per-position histogram sums to the bus count exactly) |
| E70's own additive sums `S` re-derived from this file's price lists, 16 `lq` and `alq` rungs | max \|Δ\| **0.013 W** — the 2 dp rounding of the published lists |
| this file's copy of E64's governor against the import | identical, and it reproduces E64's cap-table 65 W fp32-randn cell at 700 MHz |
| the sustained simulation on E64's own `c` against its nine measured SUS clocks | **3.64 MHz rms** |
| fp16 and int8 `zeros` (both terms must vanish) | **0.0000 W** each |

## Departures, dated 31 Oct 2026

1. **E64's own tiles were never dumped**, so the fp32 scoring tiles for its ten host kinds are **stand-ins**
   drawn from the host's own rules (`workloads/sparsity/host/main.cpp:458-478`) with numpy, not libstdc++'s
   distributions. Each row carries its draw sd over 24 draws (largest: `sparse75`, 0.43 W).
2. **The law's curvature is anchored on E70's measured `nrd_a` / `nrd_b`, not on E70's own fitted `W∞`.**
   E70 warns that its fit is not a ceiling and that its own top rungs exceed it (7.209 > 6.37, 10.785 > 10.52).
   E70's 6.37 / 10.52 W are carried as the sensitivity arm.
3. **E70 rejects the saturating *form* on the A side** (its increments accelerate where saturation needs them
   to decay). The A arm is therefore **declared, not selected**; ρ = 1.246 is the alternative pricing, and the
   ×8 (int8: ×16) A-broadcast multiplier is a **counting convention, not a measurement** — E78 must validate
   the A-side weight before any A-against-B energy claim.
4. **The product-sign term is new here.** It makes E64's fp32 `signs` a calibration kind, so fp32 has three
   fitted numbers against eight out-of-sample measured kinds.
5. **int8's bus and Hamming figures are PROVISIONAL** in `kinds.json` (they rest on the reconstructed
   256-micro-op / 16-slot TIMA stream), so every int8 switching prediction here is provisional with them. Its
   `gated_*` figures are not.
6. **γ = 3.0 is this lane's declared choice** among E64-T1's arms. It is not a figure E64-T1 itself registers.
7. **The sustained predictions inherit E69's FAILED drift check.** The same cell read 49.38 W at 65.4 °C on
   23 Oct and 51.89 W at 65.2 °C on 27 Oct: **+2.51 W at one die temperature**, more than the clamp band's
   whole 2.13 W width. A sustained miss of that size is a **thermal-path drift, not a model failure**, and E80
   should re-read the die line before scoring R8.

## Known misses, in their own direction

The model's out-of-sample residuals against E64 are not symmetric, and E78 should expect the same signs:

| kind | predicted | E64 measured | residual |
|---|---|---|---|
| fp32 `uniform` (= `uniform01`) | 20.35 W | 22.61 W | **−2.26** |
| fp32 `mant` | 20.28 W | 21.81 W | **−1.53** |
| fp32 `pow2` | 12.98 W | 13.95 W | −0.97 |
| fp32 `sparse75` | 3.36 W | 2.53 W | **+0.83** |
| fp32 `ones` | 8.55 W | 8.89 W | −0.34 |
| fp32 `randn` (a check) | 24.50 W | 24.65 W | −0.14 |

So the model **under**-predicts dense mantissa-only and exponent-only kinds by 5–10% — most likely because the
saturating law, anchored on a random word, bends too early for a histogram concentrated in one field — and
**over**-predicts a mostly-gated kind by 0.8 W, which is the gating arm's own residual error. Both are inside
the registered intervals; both are directional, and E78 will see them.

## What it changes

- **For the blog:** the kinds table's power and speed columns now have a predicted value for all 51 kinds,
  with a mechanism per kind in plain language (`result.md` of this lane; `predictions.json` carries the three
  terms separately per kind, so a figure can show *why* a kind is dear: lane-on, operand bits, product sign).
- **For the Levels tab:** stop 9's chain now has a quantitative bridge from the operand statistics to the
  governor's clock, closed on E64's own nine sustained cells to 3.6 MHz.
- **For E78:** run `a_randn_b_zeros` first (R9), and say in its README that E64's int8 `--values randn` and
  `uniform` are this spec's `full` and `pos`, or the join back to the 23 Oct int8 cells is lost.
- **For E79:** α_fp16 = 1.473 and α_int8 = 0.670 are a direct prediction about the fp16/int8 price lists it is
  measuring now (R5).

## Rebuild

```bash
cd docs/reports/data/2026-10-31-q130-kinds-model
python3 model.py --out predictions.json > predictions.txt      # numpy only; about 40 s
sha256sum predictions.json
```

`model.py` carries the whole model in its module docstring and no number in it is typed without a citation
beside it.
