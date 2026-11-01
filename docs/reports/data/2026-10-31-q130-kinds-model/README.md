# Q130(c) — the explanation model: every kind's power and clock, predicted before E78 and E80 run

*Dated 1 Nov 2026: this model's failure on the card is followed by [Q132(b)](../2026-11-01-q132-rtl-bench/README.md)'s model and its blind test, [E103](../2026-11-01-e103-model-blind-test/README.md): it narrows the question, for this kernel over zeros at 600 MHz, and does not close it.*

*Sat 31 Oct 2026 (week 44), desk lane of Q130, on the Intel. **No card was touched, claimed or set.** Every
number here is a prediction computed from already-committed measurements by [`model.py`](model.py), frozen for
**E78** (aifoundry3, 600 MHz pinned) and **E80** (aifoundry2, its own governor, no governor move). Model id
`Q130C-M1`. The kinds and tiles are Q130(s) revision 2, commit `7d9c0d9e`, which is where the pre-registration
clock starts. Frozen as **`2bbe03dd`** (pushed 10:39:42 PDT); the README as registered is
`git show 2bbe03dd:docs/reports/data/2026-10-31-q130-kinds-model/README.md`.*

*Corrected the same day by **amendment A1**, after verification found that the explanation built on the freeze
does not hold, and **before any E78 or E80 file exists**. [`predictions.json`](predictions.json) and
[`model.py`](model.py) are byte-identical to the freeze (sha256
`c5a66cb6d5f07a35d783d7db4be0f94a69482cf123defd2eccfda04fb6320a2c`), so E78 and E80 still score the frozen
numbers. A1 changes four things: what those numbers are said to mean, which kinds count as out of sample, three
rule clauses, and the intervals, which were too narrow. Every A1 number is in [`amendment-a1.json`](amendment-a1.json),
written by [`amend_a1.py`](amend_a1.py) from the frozen model's own functions. Its copy of the frozen calibration
reproduces every kind's switching W under both gating arms, and every ci95, in `predictions.json` exactly.*

> 🛑 **Nothing in this file is a measurement.** It is the frozen prediction E78 and E80 are scored against.
> A prediction that fails is reported as failed.

## What A1 withdraws and corrects

| | the frozen claim | A1 |
|---|---|---|
| **1** | σ is the price of the **product's sign**: 15× the operand-bus price of the sign bit. No price list can see it, because E65's and E67's masks never moved the product's sign | **Withdrawn.** E65's `bit_31` and E67's `abit_31` **do** move the product's sign (q = 1.000 and 0.500). They cost **0.563 ± 0.024** and **0.561 ± 0.182 W**. The frozen model, run on the tiles those hosts dumped, gives **8.70** and **4.61 W** (15.5× and 8.2×). E79's sign rungs, public before the freeze, fail the same way: fp16 B sign 0.313 W against 11.72 W, fp16 A 0.327 against 6.19, int8 A MSB 2.399 against 7.75. σ stays in the frozen numbers as a **random-sign term fitted on `signs`**, not a price of anything named |
| **2** | the law's curvature is anchored on E70's one-sided steps, and the intervals carry E70's 0.232 W law rms | at the model's own `WB` = 6.965 W the law **misses E70's own 15-rung fit set by 1.236 W rms**, against E70's own 0.232 W (lq_h23 12.145 → 6.943 W). It misses the A side's 7 rungs by **1.161 W**. It even bends the model's own input: mantissa bit 22 goes from 4.627 to 3.382 W. A1 adds an interval whose law term uses that rms (`switching_w_ci95_a1`) |
| **3** | fp32 `randn` is an **out-of-sample check** that passes to −0.95% | **Selected-on.** The overlap term λ was fitted on it (λ = −0.0288, residual 0) and then dropped; the −0.153 W is what dropping it leaves. What survives: E70's one-sided steps over-add the split's flip term by **1.89 W**, and the random-sign term takes up all but 0.15 W of that |
| **4** | the product-sign rate counts every element | it charges a sign to **zero products** (sign(a) XOR sign(b) on a zero byte or a ±0). A1 takes a zero product's sign as 0, which is what an int8 zero product's own sign bit is. Then fp16 `pair_half_zero` falls by 2.22 W and int8 `sparse50` by 1.44 W. **R3's int8 clause falls from 2.79 to 1.73 W**, under its own 2.0 W, and R9's bus-arm values fall by 0.2–5.4 W |
| **5** | R5 and the "FOR E79" shape claim are predictions about lists E79 "is measuring now" | E79's lists were **pushed at 10:34:38, five minutes before this freeze** (10:39:42). Both are relabelled **post-data comparisons** and scored now, on E79's dumped tiles. fp16 lands at α ≈ **1.0** (1.035 on B, 0.945 on A) against the frozen 1.473. int8 lands at **0.491** on the A side and 0.352 on E79's `kg` B list, outside [0.5, 2.0]. int8's shape claim **fails** |
| **6** | U_int8 = 0.571 W, "15× smaller than fp32's" | E79 measured the same step on E78's own card and clock at **1.834 ± 0.113 W** (exploratory in E79's own labelling); fp16's is 8.736 ± 0.054 W against the model's 8.463. int8's U is **4.7× smaller**, not 15× |
| **7** | R3 includes \|fp32 sparse50 − fp32 wsparse50\| ≤ 1.0 W | **there is no fp32 `wsparse50`**, either in kinds.json revision 2 or here. The clause is dropped |
| **8** | all 18 fp32 kinds are out of sample, and E64's eight "out-of-sample" fp32 kinds score 1.07 W rms | fp32/`zeros` is the basis. fp32/`pi` is in sample: it is E70's `anchor_pi`, one of U's three levels. fp32/`randn` was selected on. Of E64's eight, two are U + E70's step **by construction** and `sparse75` chose the arm. The **clean four score 1.46 W rms**, all under-predicted by 4–10% |
| **9** | the sign bit is the cheapest of the 32 | it is **rank 10 of 32** (0.56 W). Bits 1–8 and 27 are cheaper, and the cheapest is bit 6 at 0.38 W. E65's own A3 scored this FAIL |
| **10** | the known misses are all inside the registered intervals | `sparse75` sits **2.22 σ** off, outside its own 95% (1.46 σ with the draw sd). The 12% band was set with the out-of-sample residuals in view |
| **11** | the stand-in tiles affect only the scoring | WA, WB and σ are fitted on the stand-ins, so the stand-ins set every prediction. On E70's own dumped `nrd` tiles, WB comes out at **7.484** and the randn check at 16.29 W. The fp32 predictions move up by 0 to 0.34 W, and the 51 kinds together by −0.11 to +0.34 W |
| **12** | the speed path reproduces E64's nine sustained clocks to 3.64 MHz | that figure is **in sample**. E64-T1's out-of-sample figure at γ = 3 is **6.2 MHz**, and 8.3 MHz on the five informative cells |
| **13** | the gate rate is ~p, ~p², ~p⁸ | the gate is the **union** of an A test and a B test: ≈ 2p − p², 2p² − p⁴ and p⁴ + p⁸. int8 `sparse50` gates 0.070, which is its A zero-word fraction. fp16 `sparse50` gates **41%**, not 44% |
| **14** | pJ per op = ΔW / 1.1208 Gop/s | for int8 the code uses **1.9244 Gop/s** (1.1208 × 546/318) |
| **15** | the cards agree to 0.03 W, four weeks apart, and E64's step carries to 24.661 W | the 0.03 W is a **cancellation** between components that each miss by ±0.35 W: U is 0.34 W below E64's own ones step, and E70's one-sided steps are 0.37 W above E64's. The two campaigns are **four days** apart (23 and 27 Oct). E64's step carries to **24.649 W**, 0.010 W from E67's |
| **16** | there are E71-slope, E70-W∞ and γ 0/2 sensitivity arms, and an `inputs.transfer_rule` | none of these arms was computed, and `inputs` is empty. **All are now computed** (below) |

## Results, as corrected

**One model with three fitted numbers on the fp32 side and one more per narrow format, predicting all 51 kinds.**
One more fp32 number (λ) was fitted on fp32 `randn` and dropped:

```
dW(kind) = U_T·(1 − g)                       the lane the gate did not switch off
         + Φ(S_A; WA_T) + Φ(S_B; WB_T)       the operand bits, saturating per side
         + σ_T·q                             a random-sign term fitted on `signs` (A1: not a price of the product's sign)
```
All three terms are over that type's own zero-data level, at 600 MHz and 521.8 mV on aifoundry3. That is E78's
own operating point, so the fp32 arm needs no card or clock conversion. `Φ(S; W) = W(1 − e^(−S/W))` is E70's
selected coverage law. `S_A` and `S_B` are E70's own additive sums, generalised from one mask to a whole
per-position flip histogram. `g` is the gated fraction of the 4,096 column-slot-cycles of one op. `q` is the rate
at which sign(a) XOR sign(b) changes, counted on every element including zero products (see A1 item 4).

| fitted | value | fitted on |
|---|---|---|
| `WB` | **6.965 W** | E70's `nrd_b` 10.785 ± 0.024 W (random B against a constant A), through 24 numpy stand-in tiles |
| `WA` | **5.392 W** | E70's `nrd_a` 7.209 ± 0.015 W (random A against a constant B), the same way |
| `σ` | **8.165 W** | E64's fp32 `signs` (±1.0f), 13.10 W over zeros |
| `U` fp32 | 8.555 ± 0.060 W | *read off*, not fitted: E67's zeros anchor and E70's three constant-operand levels (`lq_h0`, `aq_h0`, `anchor_pi`) |
| cross-side overlap λ | **declared 0** | **fitted on fp32 `randn`'s split in a first pass (−0.029) and dropped, so randn selected the form** (A1) |
| `α_fp16`, `α_int8` | **1.473**, **0.670** | E64's fp16 `randn` and int8 `randn` (= `full`), one point each |
| `U_fp16`, `U_int8` | **8.463 W**, **0.571 W** | E64's (ones − zeros) per format, one run each (± 1.19 W). **E79 measured 8.736 ± 0.054 and 1.834 ± 0.113 W** at aifoundry3 (A1, post-data) |

**Five results, after A1.**

1. **The two sides add once the random-sign term takes up the over-add. But randn chose the form, so this is
   not an out-of-sample check.** E70's one-sided random steps sum to 7.209 + 10.785 = 17.994 W. That over-adds the
   split's flip term (16.104 ± 0.37 W, `inventory.json` > `zeros_random_split`) by **1.89 W**. The random-sign term
   is fitted on `signs`, and it takes up all but 0.15 W of the gap: the model predicts 15.951 W. λ was fitted on
   this same split in a first pass (−0.0288, residual 0) and then dropped, so the 15.951 W is a model selection,
   not a test. E67's host drew seven fresh randn tiles and dumped them; on those, the frozen model gives 15.87 W
   (−0.24 W). On E70's own dumped `nrd` tiles it misses `nrd_b` by −0.42 W, because WA and WB were fitted on numpy
   stand-ins rather than on those tiles (`amendment-a1.json` > `check_e67_anchors_on_dumped_operands`,
   `arms.frozen_replica.e70_nrd_tiles`).

2. **The card transfer holds, but only within the scatter of its parts.** E64's `a_randn_b_ones` and
   `a_ones_b_randn` are U + E70's one-sided steps by construction. They test only the transfer: ×1.01865 from
   aifoundry2 at 517 mV to aifoundry3 at 521.8 mV. They agree to 0.03 and 0.02 W, but their parts disagree by
   ±0.35 W and cancel:
   - U is 0.34 W below E64's own (ones − zeros), which is 8.895 W.
   - E70's steps are 0.37 W above E64's (6.836 and 10.420 W).
   - The fitted c of E64's three `ones` runs alone spans 9.65–11.16 W.

   The two campaigns ran on two cards, four days apart (23 and 27 Oct). E64's fp32 (randn − zeros), 24.198 W,
   carries to **24.649 W**, against E67's anchors' 24.659 ± 0.37 W: a 0.010 W difference.

3. **The product-sign mechanism is withdrawn.**
   - **The failure.** E65's `bit_31` alternates B between +base and −base across the column halves, with A = 1.0,
     so the product's sign changes on every micro-op (q = 1.000). It costs **0.563 ± 0.024 W**. E67's `abit_31`
     changes the sign every second micro-op (q = 0.500) and costs **0.561 ± 0.182 W**. The frozen model, run on
     the tiles those hosts dumped, gives 8.70 and 4.61 W. No other rung of the 64 has a sign change, and on those
     62 the model is within 0.36 W rms of its own price lists
     (`check_sign_term_on_price_list_rungs`).
   - **The same failure in fp16 and int8.** E79's single-bit rungs were public five minutes before the freeze. On
     those tiles, the frozen model's sign rungs come out 3–38× too dear: the fp16 B sign 11.72 W against 0.313 ±
     0.516 W, the fp16 A sign 6.19 W against 0.327 ± 0.258 W, and the int8 A MSB 7.75 W against 2.399 ± 0.077 W.
     The other rungs, mantissa and exponent, come within 0.24–0.40 W rms (`score_r5_post_data`).
   - **What σ absorbs is real.** E64's `signs` (±1.0f on both sides) costs 13.10 W over zeros, 4.5 W above U.
     What that 4.5 W is remains open.
   - **Two candidates fit both cheap rungs.** E79's Result 5 measured, at fp32 B bit 22, that E65's construction
     prices a flip 7.0× above a layout that keeps the accumulators balanced. It reads the gap, as a hypothesis it
     did not test, as the result path swinging between two diverging accumulators. That E65's other positions and
     E67's A side carry the same composite is inferred there, not measured.
     (a) In `bit_31` and `abit_31`, every accumulator the result path alternates between holds the same
     magnitude with the opposite sign. So the result path moves one bit, the same mechanism E79's 1b gives for the
     cheap exponent. In `signs` the accumulators random-walk and differ in many bits. (b) The rate of effective add/subtract changes against each column's running
     accumulator, which is zero on both cheap rungs and high on `signs`.
   - **The checks a successor must pass.** A successor model must pass three checks the frozen one cannot: E65
     `bit_31` 0.563 ± 0.024 W, E67 `abit_31` 0.561 ± 0.182 W, and E64 `signs` 13.10 W.
   - **The sign bit's real rank.** It is rank 10 of 32 on E65's list (0.56 W; the cheapest is bit 6 at 0.38 W;
     E65's A3 FAIL), not the cheapest.

4. **int8's lane un-gating term: E79 measured it at 1.834 ± 0.113 W, 4.7× below fp32's 8.555, not 15×.** The
   model's 0.571 ± 1.19 W rests on one E64 run per point on aifoundry2. E79's paired zeros − h0 step measures
   exactly this quantity (`h8q` is a constant nonzero operand, with no flips and no sign change) on E78's own card
   and clock. E79 published it five minutes before the freeze, and labels it exploratory: its amendment A7 defined
   the quantity after three of its four passes had been seen. The same step in fp16 is 8.736 ± 0.054 W, against
   the model's 8.463 W (`score_u_post_data`). Every constant kind in a format (`ones`, `neg_ones`) is predicted
   at U, so these numbers already score those kinds after the data. int8 still gets the least from a zero. Its
   gate fires only when a whole A word, or both B words of a pair, are zero: about p⁴ + p⁸ at element sparsity p,
   which is 0.070 at p = 0.5. And what the gate switches off costs 1.8 W, not 8.6.

5. **The law's curvature is the model's weakest part, and its misses point to it.**
   - **The cap.** At WB = 6.965 W the B-side bit term can never exceed 6.97 W. E70 measured mantissa-only rungs,
     which have no sign change, at 12.145 W (`lq_h23`) and 9.749 W (`ls_h16`, inside E70's fit set).
   - **The rms.** Over E70's 15-rung fit set, the law at the model's W misses by **1.236 W rms**. E70's own law
     achieves 0.232 W there at W∞ = 10.52 W, and that 0.232 W is what every frozen interval borrows. On the A
     side the law misses E70's 7 rungs by **1.161 W**; E70's own A fit is 1.063 W, and E70 rejects that form.
   - **Its own inputs.** The single-bit rung at mantissa bit 22, 4.627 W on E65's list, comes out at 3.382 W.
   - **The two cannot both hold.** With E70's own W∞ and σ refitted, the randn flip check reads 19.25 W against
     16.10 W, and `nrd_b` reads 12.92 W against 10.785 W. So σ and E70's law cannot both hold
     (`check_law_on_e70_ladder`, `arms.e70_winf`).
   - **The misses.** This is the direction of the clean fp32 misses: under by 4–10% (uniform −2.26 W, mant
     −1.53, pow2 −0.97, ones −0.34).

### The speed path reproduces E64's own nine sustained clocks to 3.6 MHz in sample (6.2 MHz out of sample)

Burst is E64's **registered** governor (`surface_hpl.py simulate`, τ 1.3 s, pass 0.24 s) at the card's 65 W on
a cool die. Sustained is **E64-T1** (`surface_hpl_t.py`) at γ = 3.0. It puts E66's leakage law in the power curve,
makes the die a state relaxing towards E64's thermal line **die = 41.88 + 0.4696 °C per W** with τ_th 14 s, and
adds a thermal limb that steps down on a pass reading ≥ 66 °C. Run on **E64's own fitted `c`**, the two
simulations give:

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

**3.64 MHz rms over the nine, and 4.46 MHz over the six that are not clamped at 800.** **This is in sample (A1):**
`surface_hpl_t.build()` fits B_f, c, the die line, τ_th and the governor on these same runs, and γ = 3 was chosen
on the same nine cells. The speed path's accuracy is E64-T1's **out-of-sample** figure: **6.2 MHz** at γ = 3,
and 8.3 MHz on the five informative cells. At γ = 2 those are 7.1 and 9.6 MHz, and at γ = 0 they are 9.6 and
12.9 MHz (`figures-t1.json`).

The γ arms are computed in `amendment-a1.json` > `gamma_arms`, on the frozen switching W:
- **Within-sample rms.** On E64's own c it is 3.65 MHz at γ = 3, 6.46 MHz at γ = 2 and 10.9 MHz at γ = 0.
- **Moves.** Across the 51 kinds, γ = 2 moves a sustained prediction by at most 9 MHz (fp16 `ones`, `neg_ones`,
  `wsparse50`). γ = 0 moves one by at most **20 MHz** (int8 `sorted` and `sparse50`). That is more than the "few
  MHz" the frozen text said.

### The spine of the table (tier 1), predicted

`switching W` is over that type's own zero-data level, on aifoundry3 at 600 MHz. `burst` and `sust` are
aifoundry2 MHz. The frozen columns are unchanged. **95% (A1)** is the frozen interval with the law term at the
law's own rms at the model's W (A1 item 2). **W, zero products unsigned** is the A1 sign accounting, shown only
where it moves by at least 0.05 W ("=" otherwise). Every value is in [`predictions.json`](predictions.json) and
[`amendment-a1.json`](amendment-a1.json).

| format | kind | status (A1) | gated | switching W | 95% (frozen) | 95% (A1) | W, zero products unsigned | pJ/MAC | burst | sust | limit |
|---|---|---|---|---|---|---|---|---|---|---|---|
| fp32 | zeros | basis | 1.000 | 0.00 | 0.00–0.30 | 0.00–0.30 | = | 0.000 | 800 | 800 | power |
| fp32 | a_randn_b_zeros | out | 1.000 | 0.00 | 0.00–0.30 | 0.00–0.30 | = | 0.000 | 800 | 800 | power |
| fp32 | sparse90 | out | 0.992 | 0.46 | 0.14–0.78 | 0.14–0.78 | = | 0.099 | 800 | 800 | power |
| fp32 | ones | out (not blind) | 0.000 | 8.55 | 7.99–9.12 | 7.99–9.12 | = | 1.863 | 800 | 745 | thermal |
| fp32 | sparse50 | out | 0.774 | 9.50 | 7.58–11.42 | 7.44–11.56 | = | 2.069 | 800 | 728 | thermal |
| fp32 | pow2 | out | 0.000 | 13.19 | 11.93–14.46 | 9.60–16.79 | = | 2.874 | 800 | 681 | thermal |
| fp32 | nn_like | out | 0.508 | 16.00 | 13.04–18.97 | 12.61–19.40 | = | 3.486 | 785 | 649 | thermal |
| fp32 | smallint | out | 0.118 | 17.39 | 14.91–19.88 | 13.53–21.26 | = | 3.789 | 770 | 639 | thermal |
| fp32 | randn_sorted | out | 0.000 | 22.77 | 19.24–26.29 | 17.90–27.63 | = | 4.959 | 706 | 600 | thermal |
| fp32 | bf16trunc | out | 0.000 | 23.26 | 19.62–26.90 | 18.31–28.21 | = | 5.067 | 706 | 600 | thermal |
| fp32 | randn | selected-on | 0.000 | 24.21 | 20.34–28.08 | 19.09–29.34 | = | 5.274 | 700 | 600 | thermal |
| fp16 | zeros | basis | 1.000 | 0.00 | 0.00–0.30 | 0.00–0.30 | = | 0.000 | 800 | 800 | power |
| fp16 | ones | calibration | 0.000 | 8.46 | 6.05–10.88 | 6.05–10.88 | = | 0.922 | 800 | 745 | thermal |
| fp16 | wsparse50 | out | 0.760 | 9.04 | 4.60–13.48 | 4.57–13.52 | = | 0.985 | 800 | 735 | thermal |
| fp16 | sparse50 | out | 0.414 | 15.51 | 8.75–22.27 | 8.62–22.40 | 14.45 | 1.689 | 794 | 656 | thermal |
| fp16 | nn_like | out | 0.195 | 19.38 | 11.28–27.48 | 11.08–27.68 | 18.50 | 2.111 | 752 | 621 | thermal |
| fp16 | pair_half_zero | out | 0.000 | 20.94 | 12.79–29.09 | 12.48–29.39 | 18.72 | 2.280 | 727 | 608 | thermal |
| fp16 | randn_sorted | out | 0.000 | 21.44 | 12.99–29.90 | 12.69–30.20 | = | 2.335 | 715 | 604 | thermal |
| fp16 | randn | calibration | 0.000 | 22.30 | 18.91–25.68 | 18.22–26.37 | = | 2.429 | 715 | 600 | thermal |
| int8 | zeros | basis | 1.000 | 0.00 | 0.00–0.30 | 0.00–0.30 | = | 0.000 | 800 | 800 | power |
| int8 | ones | calibration | 0.000 | 0.57 | 0.00–2.97 | 0.00–2.97 | = | 0.018 | 800 | 800 | power |
| int8 | neg_ones | out | 0.000 | 0.57 | 0.00–2.97 | 0.00–2.97 | = | 0.018 | 800 | 800 | power |
| int8 | wsparse50 | out | 0.644 | 3.27 | 0.94–5.60 | 0.92–5.62 | 2.89 | 0.104 | 800 | 800 | power |
| int8 | pos | out | 0.000 | 3.45 | 0.32–6.58 | 0.23–6.67 | = | 0.109 | 800 | 800 | power |
| int8 | sorted | out | 0.000 | 5.98 | 1.50–10.47 | 1.43–10.54 | = | 0.190 | 800 | 776 | thermal |
| int8 | sparse50 | out | 0.070 | 6.06 | 1.59–10.54 | 1.53–10.59 | 4.62 | 0.192 | 800 | 774 | thermal |
| int8 | ternary | out | 0.008 | 6.42 | 1.68–11.16 | 1.62–11.22 | 5.44 | 0.203 | 800 | 768 | thermal |
| int8 | full | calibration | 0.000 | 7.11 | 3.73–10.48 | 3.65–10.56 | = | 0.225 | 800 | 758 | thermal |
| int8 | smallint | out | 0.000 | 7.13 | 1.95–12.31 | 1.89–12.37 | 6.90 | 0.226 | 800 | 757 | thermal |
| int8 | gauss_q | out | 0.000 | 7.10 | 1.93–12.28 | 1.88–12.33 | 7.05 | 0.225 | 800 | 758 | thermal |

`out (not blind)`: E67 measured fp32/`ones`'s operands (`anchor_ones`, A = B = 1.0f) on aifoundry3 at 600 MHz
before the freeze, at **8.217 W** over `anchor_zeros`. The model was not fitted on that number: U uses `lq_h0`,
`aq_h0` and `anchor_pi`. So E78's fp32 `ones` tests the model, but not blind.

Three readings a blog can use, **all of them predictions**:
- **fp32's range.** The kind of number is predicted to move fp32's switching power **53×**: 0.46 W for 90%-sparse
  data against 24.2 W for random normals. It moves the sustained clock by 200 MHz, from 600 to 800.
- **int8's clocks.** **Every int8 kind is predicted to burst at 800 MHz**, so the spread can only move the
  *sustained* clock, 757 to 800 MHz.
- **int8's range.** int8's whole predicted range (0 to 7.1 W) sits below fp32's `ones`. Its constants are
  predicted at U_int8: frozen at 0.57 W, against the 1.83 W E79 measured five minutes before the freeze.

## What is calibrated, and what is therefore out of sample (corrected by A1)

| arm | what it may use | what is fitted | what is out of sample |
|---|---|---|---|
| **fp32** | E65's B-side and E67's A-side 32-position price lists; E70's law and its two one-sided random steps; the zero-gate rule; E67/E70's anchors; E64's own measured fp32 kinds | `WA`, `WB`, `σ` — **three**, plus λ, fitted on the randn split and dropped | **15 of the 18 kinds**: zeros is the basis, pi is in sample, randn was selected on, and ones is out of sample but not blind. Of E64's ten: **the clean four** (ones, pow2, mant, uniform). The other six are signs (fitted), randn (selected on), sparse75 (arm-selected), the two one-sided kinds (by construction) and zeros (basis) |
| **fp16** | **E64's three kinds only**: zeros, ones, randn | `U_fp16`, `α_fp16` — **two** | **14 of 17 kinds** (the frozen 15 counted zeros, the basis, as out of sample) |
| **int8** | **E64's three kinds only**: zeros, ones, randn (= `full`) | `U_int8`, `α_int8` — **two** | **13 of 16 kinds** (the frozen 14 counted zeros the same way) |

For fp16 and int8 there was no per-bit price list at the freeze. So each element bit is priced off **fp32's**
list by field role. The mantissa is aligned at the **MSB**: fp16's 10 mantissa bits take fp32's prices 13…22, and
int8's 7 magnitude bits take 16…22. The exponent is aligned at the **LSB**. The whole list, the law's curvature
**and** σ are then scaled by one number per format,

> `β_T = r_T · α_T`, with `r_fp16 = 11/24` and `r_int8 = 8/24` — the significand width over fp32's —
> and α_T the only quantity fitted.

**α = 1 would mean the significand-width scaling is exactly right.** It comes out at **1.473 (fp16)** and
**0.670 (int8)**. **A1:** E79's fp16 and int8 lists were public five minutes before the freeze, and were not used.
They are scored against now (`score_r5_post_data`), on E79's dumped tiles. For each rung, α is E79's step over its
own zero divided by the model's linear operand sum at α = 1 on the same operands. The model's own flip counting
therefore applies to both, and no counting convention enters:

| E79 list | footing | α, ratio of sums | α, significand only | α at the top significand bit | frozen model's rms on the list | significand ρ (E79 / model) | sign or MSB rank, dearest first (E79 / model) | dearer than fp32's at the same index |
|---|---|---|---|---|---|---|---|---|
| fp16 B | `jg`, E65's construction | **1.035** | 1.047 | 1.069 | 2.88 W (0.40 without the sign rung) | 1.000 / 1.000 | 16 / 15 of 16 | 10 of 10 |
| fp16 A | E67's construction | **0.945** | 0.973 | 0.953 | 1.50 W (0.33) | 0.855 / 0.818 | 16 / 14 of 16 | 8 of 10 |
| int8 A | E67's construction | **0.491** | 0.401 | 0.282 | 1.91 W (0.24) | **0.143** / 0.857 | **1** / 8 of 8 | **0 of 7** |
| int8 B | `kg`, balanced accumulators (not E65's footing; a bound at E71's slope) | 0.352 | 0.344 | 0.251 | 0.18 W | 0.500 / 1.000 | 8 / 8 of 8 | 0 of 7 |
| int8 B | `jg` | the model's own int8 stream counts **no** flips here, as E79's A4 found: both column halves issue in one cycle | | | 0.07 W | | | |

- **R5 as a post-data comparison: fp16 in the band, int8 not.** The width scaling **holds for fp16 at α ≈ 1.0**.
  The frozen α_fp16 = 1.473 is 41% above what the per-bit prices imply, so in fp16 `randn` the model's β-scaled
  law and sign term under-account by that much.
- **int8 lands at 0.491 on the A side.** Half that factor is the A-broadcast counting convention (departure 3).
  On E79's per-lane footing the same prices give 0.98 per flip. E79's own text says one A read feeds both TIMA
  units of a lane.
- **The int8 shape claim fails.** The model maps int8's magnitude bits onto fp32's rising 16…22, and its MSB onto
  fp32's cheap bit 31. E79's int8 A list is flat over the magnitude bits (ρ 0.14). Its MSB is the **dearest**
  position (152 fJ), and none of its magnitude bits is dearer than fp32's at the same index.

## The registered rules E78, E79 and E80 are scored against

Machine-readable in [`predictions.json`](predictions.json) > `decision_rules`, unchanged. A1's status for each
rule is in the last column, and the amendments are listed after the table.

| # | rule, as registered | A1 |
|---|---|---|
| **R1** | E78: measured switching power over the type's own zeros level is inside `switching_w_ci95` for ≥ 70% of the fp32 kinds run and ≥ 50% of the fp16/int8 kinds | scored over the **out-of-sample kinds only** (A1.3), on the frozen ci95. **R1-A1**, on `switching_w_ci95_a1`, is reported beside it as a secondary |
| **R2** | E78: the **order** is right — Spearman ρ of predicted against measured ≥ 0.90 within each format | over the out-of-sample kinds only (A1.3) |
| **R3** | E78: the gate's signature — (sparse50 − wsparse50) ≥ 2 W in **both** fp16 and int8, and \|fp32 sparse50 − fp32 wsparse50\| ≤ 1.0 W, because in fp32 element sparsity **is** word sparsity | **fp32 clause dropped** (no such kind, A1.1). The int8 clause is scored as registered and now **discriminates** between sign accountings: frozen 2.79 W, zero products unsigned 1.73 W (A1.2) |
| **R4** | E78: int8 (ones − zeros) ≤ 2.0 W against fp32's 8.555. **The sharpest structural prediction here and the likeliest to fail.** It rests on one E64 run per point | scored as registered. E79 has since measured the same step at **1.834 ± 0.113 W** (post-data): under the 2.0 W threshold, and 3.2× the model's 0.571 |
| **R5** | E79: α_fp16 and α_int8 land in [0.5, 2.0] when re-solved against E79's own measured fp16/int8 per-bit prices | **post-data comparison, not a prediction** (A1.5). fp16 is in the band (B 1.035, A 0.945). int8 is not (A 0.491; `kg` B 0.352). So R5 **fails** as a comparison, and could not have counted as a passed prediction |
| **R6** | E78: the product-sign term is real — fp32 `neg_ones` within 1 W of `ones` (every element is −1.0, so the product's sign never *changes*), while int8 `ternary` and `highbit`, whose signs do change, cost ≥ 1 W more than int8 `ones` | scored as registered, but read as a test of **random sign patterns costing more than a constant**, not of a product-sign price (A1.6) |
| **R7** | E80: predicted burst MHz within 25 MHz for ≥ 70% of cells, and every cell predicted at 800 measures ≥ 790 | unchanged |
| **R8** | E80: the sustained **limit** (thermal vs power) is called right for every cell, and the clock is within 40 MHz for ≥ 70% | unchanged. Its accuracy is 6.2 MHz out of sample, not 3.64 (A1.9) |
| **R9** | E78: the gate's **reach** — see below. Run it first | scored as registered. The bus-arm alternatives are restated with zero products unsigned (A1.7) |

### R9, and the one cell E78 should run first

The gate clears `ex_txfma_valid`, and `vpu_lane.v` clock-gates the lane, so a gated column-slot-cycle does no
multiply. Whether it still pays its **operand bus** flips is not settled by any committed measurement. It is the
single largest open term in this model, so both readings are carried. **A1** adds the bus arm with zero products
unsigned: the frozen bus arm charged σ to products that are all zero.

| cell | `gate` arm (primary) | `bus` arm, frozen | sign charged to zero products (A1 removes it) | `bus` arm, A1 |
|---|---|---|---|---|
| fp32 `a_zeros_b_randn` | 0.00 W | 10.78 W | 4.14 W (every product is zero) | **6.64 W** |
| fp16 `a_zeros_b_randn` | 0.00 W | 10.02 W | 5.36 W (every product is zero) | **4.67 W** |
| fp32 `a_randn_b_zeros` | 0.00 W | 7.30 W | 2.10 W (every product is zero) | **5.19 W** |
| fp32 `sparse50` | 9.50 W | 16.63 W | 1.74 W | 14.89 W |
| fp32 `sparse90` | 0.46 W | 6.71 W | 1.14 W | 5.57 W |
| fp16 `wsparse50` | 9.04 W | 15.05 W | 2.79 W | 12.27 W |

**`a_randn_b_zeros` decides it in one launch.** Every lane is gated by the B side, while the A operand bus keeps
moving 27,920 bits an op. The `gate` arm says ≈ 0 W over zeros; the `bus` arm says 5.2 W (A1), or 7.3 W frozen.
The primary arm was selected on E64's fp32 `sparse75`, the only measured kind that is mostly gated. The `gate`
arm misses it by **+0.83 W** (2.22 σ, outside its own 95%) and the `bus` arm by **+10.14 W**. That is a clear
selection, but it rests on one mostly-gated kind, and the two arms are a **binary declared choice**, not an
interval. Every kind's value under the other arm is `switching_w_alt_gating_arm`.

## Amendment A1 — the rules, dated Sat 31 Oct 2026, written before any E78 or E80 data

None of these moves a registered band, and none changes a frozen number.

| | what | why |
|---|---|---|
| **A1.1** | R3's fp32 clause is dropped; R3 is scored on its fp16 and int8 clauses | fp32 has no `wsparse50` kind in kinds.json revision 2 or in `predictions.json`; in fp32, element sparsity is word sparsity, so the matrix has nothing to compare |
| **A1.2** | R3's int8 clause is scored as registered (≥ 2.0 W). The report must say which sign accounting the measured int8 difference favours: frozen 2.79 W, or zero products unsigned 1.73 W | the frozen rate charges a sign to zero products; an int8 zero product's sign bit is 0 |
| **A1.3** | R1 and R2 are scored over the **out-of-sample** kinds only: fp32 drops zeros (basis), pi (in sample) and randn (selected on); fp16 and int8 drop zeros, ones and randn/full (calibration). The as-registered all-kinds score is reported beside it | the excluded kinds score free hits (`scoring_sets_a1`) |
| **A1.4** | **R1-A1** is added as a secondary: R1 on `switching_w_ci95_a1` | the frozen intervals' law term uses 0.232 W, but the law at the model's own W misses E70's ladder by 1.236 W (B) and 1.161 W (A) |
| **A1.5** | R5 and the "FOR E79" shape claim are **post-data comparisons**, scored now (table above), and never counted as passed predictions | E79's lists were pushed at 10:34:38, before the 10:39:42 freeze |
| **A1.6** | R6 is read as "random sign patterns cost more than a constant", not as evidence for a product-sign price | E65 `bit_31` and E67 `abit_31` (A1 item 1) |
| **A1.7** | R9 is scored as registered. Its bus-arm alternatives are carried in both accountings | the frozen bus arm charges σ to all-zero products |
| **A1.8** | any successor model must pass E65 `bit_31` (0.563 ± 0.024 W), E67 `abit_31` (0.561 ± 0.182 W) and E64 `signs` (13.10 W), and must be calibrated on E70's dumped `nrd` tiles, not on stand-ins | A1 items 1 and 11 |
| **A1.9** | R8 is unchanged. The speed path's accuracy is quoted as E64-T1's out-of-sample 6.2 MHz (8.3 on the informative cells) | A1 item 12 |

## Conversions, stated (corrected by A1)

| | rule | why |
|---|---|---|
| **card and clock** | `W(aifoundry3, 600 MHz, 521.8 mV) = c(aifoundry2, 600 MHz, 517 mV) × (0.5218/0.517)² = c × 1.01865` | the dynamic term at `V²` with `f` fixed, which is E64's own `s_f` at `f/600 = 1`; E72 — the price follows the voltage; E60's cross-card check, 1.300 W predicted against 1.291 measured (0.7%). Checked here to 0.010 W on fp32 (randn − zeros): 24.649 against 24.659. On `a_randn_b_ones` / `a_ones_b_randn` it agrees to 0.03 W only by a cancellation of ±0.35 W components (Result 2) |
| **leakage** | **it cancels**: every figure is a *difference* of two runs at a common die reading | the slope de-leaking the inputs is each campaign's own registered one: E65 0.182, E67 0.175 and E70 0.1975 W/°C, each solved from its own runs; E64 uses E60's 0.442 W/°C constant, referred to 58 °C. **The sensitivity arm is computed (A1):** E71's measured **0.3803 W/°C** on aifoundry3. The E65/E67 prices are scaled by their own leak-sensitivity ratios, E70's `nrd` steps are carried by its three fixed-slope reductions (7.048 and 10.562 W), and U = 8.451 W (Q130(a)). The calibration then gives WA 5.162, WB 6.584 and σ 8.401. fp32 predictions fall by 0 to 0.66 W (randn 24.21 → 23.66), and fp16 and int8 predictions move by −0.26 to +0.10 W |
| **voltage law for the die** | γ = 3.0 in the leakage term of the sustained simulation | E64-T1's best out-of-sample sustained rms (6.2 MHz over nine SUS cells), and the exponent E64's own within-run busy slope implies (3.12). **γ = 0 and 2 are computed (A1):** they move a sustained prediction by up to 20 and 9 MHz |
| **energy** | `pJ per op = ΔW / rate`. The rate is 1.1208 Gop/s for fp32 and fp16, and **1.9244 Gop/s for int8** (1.1208 × 546/318). Per MAC, divide by 4,096 (fp32), 8,192 (fp16) or 16,384 (int8) | E70's measured whole-card TensorFMA rate at 600 MHz, 1.1208–1.1210 Gop/s over seven passes, scaled by cycles per op for int8 (`model.py` line 661) |

## Checks that ran

| check | result |
|---|---|
| all 51 tiles' sha256 against `kinds.json` | **51 / 51** |
| this file's own stream, gate and bus counter against `kinds.json` `stats.bus_bits_per_op` and `stats.gated_lane_frac`, every kind | **0 failures of 51** (and the per-position histogram sums to the bus count exactly) |
| E70's own additive sums `S` re-derived from this file's price lists, 16 `lq` and `alq` rungs | max \|Δ\| **0.013 W** — the 2 dp rounding of the published lists |
| this file's copy of E64's governor against the import | identical, and it reproduces E64's cap-table 65 W fp32-randn cell at 700 MHz |
| the sustained simulation on E64's own `c` against its nine measured SUS clocks | **3.64 MHz rms, in sample** (A1) |
| fp16 and int8 `zeros` (both terms must vanish) | **0.0000 W** each |
| **A1:** the replica of the frozen calibration against `predictions.json` | every kind's W under both arms, and every ci95, exact to the file's rounding |
| **A1:** the frozen model on E65's 32 and E67's 32 dumped single-bit rungs | the two sign rungs miss by 15.5× and 8.2×; the other 62 come within 0.355 W rms, worst bit 22 (−1.245 W) |
| **A1:** the frozen model on E70's 23 dumped ladder rungs | 1.236 W rms on the 15-rung fit set; worst `lq_h23`, −5.20 W. E70's own law reproduces its published 0.232 and 1.063 W |
| **A1:** E67's anchors on their dumped operands | `anchor_pi` +0.06, `anchor_ones` +0.34, `anchor_randn` −0.24 W (7 distinct draws) |

## Departures, dated 31 Oct 2026 at the freeze (kept as registered; A1's corrections in brackets)

1. **E64's own tiles were never dumped**, so the fp32 scoring tiles for its ten host kinds are **stand-ins**,
   drawn from the host's own rules (`workloads/sparsity/host/main.cpp:458-478`) with numpy, not libstdc++'s
   distributions. Each row carries its draw sd over 24 draws (largest: `sparse75`, 0.43 W). [A1: WA, WB and σ
   are fitted on these stand-ins, so they set every prediction, not only the scoring. The E70-tiles arm moves the
   fp32 predictions up by 0 to 0.34 W.]
2. **The law's curvature is anchored on E70's measured `nrd_a` / `nrd_b`, not on E70's own fitted `W∞`.**
   E70 warns that its fit is not a ceiling, and that its own top rungs exceed it (7.209 > 6.37, 10.785 > 10.52).
   E70's 6.37 / 10.52 W are carried as the sensitivity arm. [A1: computed. With σ refitted it puts the randn flip
   check at 19.25 W against 16.10 W, so σ and E70's law cannot both hold.]
3. **E70 rejects the saturating *form* on the A side** (its increments accelerate where saturation needs them
   to decay). The A arm is therefore **declared, not selected**. ρ = 1.246 is the alternative pricing. The
   ×8 A-broadcast multiplier (int8: ×16) is a **counting convention, not a measurement**: E78 must validate
   the A-side weight before any A-against-B energy claim.
4. **The product-sign term is new here.** It makes E64's fp32 `signs` a calibration kind, so fp32 has three
   fitted numbers against eight out-of-sample measured kinds. [A1: the term is withdrawn as a product-sign price.
   λ was a fourth fitted number, fitted on randn. Of the eight, only four are clean.]
5. **int8's bus and Hamming figures are PROVISIONAL** in `kinds.json` (they rest on the reconstructed
   256-micro-op / 16-slot TIMA stream), so every int8 switching prediction here is provisional with them. Its
   `gated_*` figures are not.
6. **γ = 3.0 is this lane's declared choice** among E64-T1's arms. It is not a figure E64-T1 itself registers.
7. **The sustained predictions inherit E69's FAILED drift check.** The same cell read 49.38 W at 65.4 °C on
   23 Oct and 51.89 W at 65.2 °C on 27 Oct: **+2.51 W at one die temperature**, more than the clamp band's
   whole 2.13 W width. A sustained miss of that size is a **thermal-path drift, not a model failure**, and E80
   should re-read the die line before scoring R8.

## Known misses, in their own direction (corrected by A1)

The model's residuals against E64 are not symmetric, and E78 should expect the same signs. `z` is the residual
over the file's own interval rule applied to the row:

| kind | status | predicted | E64 measured | residual | z |
|---|---|---|---|---|---|
| fp32 `uniform` (= `uniform01`) | clean | 20.35 W | 22.61 W | **−2.26** | −1.54 |
| fp32 `mant` | clean | 20.28 W | 21.81 W | **−1.53** | −1.05 |
| fp32 `pow2` | clean | 12.98 W | 13.95 W | −0.97 | −1.58 |
| fp32 `ones` | clean | 8.55 W | 8.89 W | −0.34 | −1.2 |
| fp32 `sparse75` | arm-selected | 3.36 W | 2.53 W | **+0.83** | **+2.22, outside its 95%** |
| fp32 `randn` | selected-on | 24.50 W | 24.65 W | −0.14 | −0.07 |

So the model **under**-predicts the dense clean kinds by 4–10%, and the cause is now shown, not guessed. At the
model's WB the law caps a mantissa-only B-side term at 6.97 W, where E70 measured mantissa-only rungs at up to
12.15 W (Result 5). It **over**-predicts the one mostly-gated kind by 0.8 W, which is the gating arm's own
residual error. **`sparse75` is outside its own 95% interval**: 1.46 σ only if the 0.43 W stand-in draw sd is
added in quadrature. The 12% relative band was set with these residuals in view.

## What it changes

- **For the blog:** the kinds table's power and speed columns have a frozen, predicted value for all 51 kinds.
  `predictions.json` carries the three terms separately per kind. **A1:** the "product sign" reading of the third
  term is withdrawn. So is every claim that rested on it: the "15×", "the sign bit is the cheapest", "randn passes
  out of sample", the saturation readings of `bf16trunc` and `randn_sorted`, and int8's "15×". Under E70's own W∞,
  `bf16trunc` and `randn_sorted` read 25.47 and 25.32 W, not 23.26 and 22.77. What stands is the ranked table of
  predictions, which E78 now tests.
- **For the Levels tab:** stop 9's chain has a quantitative bridge from operand statistics to the governor's
  clock, closed on E64's own nine sustained cells to 3.6 MHz in sample and 6.2 MHz out of sample.
- **For E78:** run `a_randn_b_zeros` first (R9). Say in its README that E64's int8 `--values randn` and
  `uniform` are this spec's `full` and `pos`, or the join back to the 23 Oct int8 cells is lost. Score R1 and R2
  on A1's out-of-sample sets, and report which sign accounting R3's int8 clause favours.
- **For E79:** done already, after the data. The width scaling holds for fp16 at α ≈ 1.0. int8 lands at 0.49, and
  its shape claim fails (the R5 table above). The sign rungs fail in every format.

## Erratum — the frozen text that A1 supersedes

`predictions.json` and `model.py` are the freeze, so their text is not edited. Where they say the following, read
A1:

| where | frozen text | A1 |
|---|---|---|
| `model.py` docstring, THE MODEL | "THREE fp32 numbers are fitted and nothing else … fp32 randn … is therefore an OUT-OF-SAMPLE CHECK" | λ was fitted on randn and dropped; randn is selected-on |
| `model.py` docstring §4; `predictions.json` `calibration.fp32.sign_term_reading` | "A sign bit is the cheapest bit on the operand bus … E65's and E67's masks were measured against a CONSTANT other operand"; "15x less" | rank 10 of 32; `bit_31` and `abit_31` move the product's sign and cost 0.56 W; σ is a random-sign term, not a product-sign price |
| `model.py` docstring §5 | "the gate rate is ~p, ~p^2, ~p^8" | the union of the A and B tests: ≈ 2p − p², 2p² − p⁴, p⁴ + p⁸ |
| `model.py` docstring §6; this README as registered | "E79 is measuring those now" | E79's lists were pushed five minutes before the freeze |
| `model.py` docstring §7 | "E64's fp32 (randn - zeros) carries to 24.661 W"; "to 0.1 W" | 24.649 W (0.010 W); the 0.03/0.02 W is a cancellation |
| `predictions.json` `departures[3]` | "four fitted numbers (WA, WB, lam, sigma) against six out-of-sample measured kinds" | three fitted plus λ selected on randn; four clean E64 kinds |
| `predictions.json` `calibration.fp32_out_of_sample.what` | "with its four fp32 numbers fixed … NOT fitted on" | eight rows, of which four are clean (`check_e64_rows_relabelled`) |
| `predictions.json` `calibration.u_per_format.reading` | "0.57 W against fp32's 8.555 -- 15x smaller" | E79: 1.834 ± 0.113 W, 4.7× |
| `predictions.json` `interval_rule.what` | "(ii) E70's law fit rms 0.232 W" | at the model's W the law's rms is 1.236 (B) / 1.161 W (A): `interval_a1` |
| `predictions.json` `decision_rules.R3` | "and \|fp32 sparse50 - fp32 wsparse50\| <= 1.0 W" | dropped (A1.1) |
| `predictions.json` `decision_rules.R5` | a prediction for E79 | a post-data comparison (A1.5) |
| `predictions.json` `inputs` | `{}`; the lane's result cited `inputs.transfer_rule` | the transfer rule is the Conversions table above |

## Rebuild

```bash
cd docs/reports/data/2026-10-31-q130-kinds-model
python3 model.py --out predictions.json > predictions.txt      # numpy only; about 40 s; must hash to c5a66cb6…
sha256sum predictions.json
PYTHONDONTWRITEBYTECODE=1 python3 amend_a1.py --out amendment-a1.json > amendment-a1.txt   # about 10 s
```

`model.py` carries the whole frozen model in its module docstring, and no number in it is typed without a
citation beside it. `amend_a1.py` asserts the freeze's sha256, imports `model.py` without editing it, and reads
the dumped tiles of E65, E67 and E70 and the committed lists of E70, E71 and E79.
