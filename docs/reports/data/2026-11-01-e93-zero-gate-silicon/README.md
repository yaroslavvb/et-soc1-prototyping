# E93: the zero gate on silicon — negative zero, denormals, int8's eight-byte rule and its column pairing (Q132, aifoundry1 card 1, 600 MHz)

*On the kinds page, [section 11, what is still open](https://spacesheep.dev/@yaroslavvb/horace-kinds-of-numbers#11-what-is-still-open): "The zero gate on silicon" (old item 4).*

*Sun 1 Nov 2026 (week 44), Q132. Pre-registered in `d470f6a9` (pushed 00:11:18 PDT by origin/main's reflog, before the claim and the first launch):
[`tools/claims-v3/kinds/E93.md`](../../../../tools/claims-v3/kinds/E93.md), frozen numbers in
[`predictions-e93.json`](../../../../tools/claims-v3/kinds/predictions-e93.json) (sha256 `020bb188…`), scorer `score_e93.py` (sha256 `3e35e62c…`) committed
with them. No amendment was written. aifoundry1 card 1 (`V3_DEVICE=1`, its own lock) at 600 MHz in every sample, 498.8 mV mean, TDP 65 W / threshold
65 °C read at both ends of every block, never set; no governor move, no reset, no `--reset-ms`. Claim 1566349187598000201 in #community-lab, posted 00:12:27 PDT, released by editing it at 00:48 PDT (held 36.5 min of the
about 40 registered; device access 33.1 min, 00:12:31–00:45:34; [`logs/push-and-claim-times.txt`](logs/push-and-claim-times.txt)).*

*Corrected after verification, Sun 1 Nov 2026, at the desk, with no card touched and nothing re-run (§ [Corrections after verification](#corrections-after-verification-sun-1-nov-2026), C1–C11). Power agrees with the manual and the RTL on the denormal flush; it does not read the flush. Item 4 of the page is closed at power resolution on one card, in agreement with the RTL, and item 2 stays open. R5's shortfall is decomposed and its registered failure readings restored. Every blog sentence now carries its baseline and its card. No number in `e93*.json`, `runs*.csv`, `scored.json`, `results.md` or `reduce*` changed, no frozen input changed, and no verdict changed (23 PASS, 1 FAIL).*

> **What this is.** The public RTL says the chip's zero gate is one 32-bit raw-word compare taken when an operand register is written, with a lane off when
> `A_zero | (tenB_zero[raddr] & tenB_zero[raddr|1])`. Read off the RTL and matched to E78's sparse tiles, it had never been tested where the rule and "the value is zero" disagree. Seventeen new operand tiles test exactly
> there, in E78's and E82's frame, with E78's runner and reduction unchanged. **Every number here is board switching power over the type's own all-zeros level (D), 1,024 minions, unless it says otherwise.**

## Results

**Five passes of five kept (9310–9314), 198 of 200 runs, none failing a run gate; 23 PASS, 1 FAIL, 0 INCONCLUSIVE of the 24 registered rule verdicts; no verdict moves at any registered arm; the session tie to E82 and to E91 passes.** Item 4 of the kinds page's section 11 is closed at power resolution on one card, in agreement with the RTL: the micro-op counters were not read, so gated lanes are inferred from power, not counted. The one failure, R5, is this registration's own side prediction about the Booth recoder, and does not bear on the gate. [`scored.json` › `primary`]

1. **The gate compares raw words: `-0.0` leaves the lane on.** `-0.0 × -0.0` costs **7.94 ± 0.07 W** in fp32 and **8.02 ± 0.26 W** in fp16, where all-zero words read 0 by definition of D, as a chip that gated on value would read here. That is about a constant's cost: against the tie `anchor_pi` (π × π) in the same pass, -0.15 ± 0.14 W (the interval just excludes 0 and sits inside the registered ±1 W), and E88's clocked lane on this card is 7.92 W. So **`-0.0` costs 7.9 W more than `+0.0`, about what multiplying two constants costs.** With random numbers on the other side, a live `-0` costs **12.11 ± 0.18 W** (A = `-0`) and **12.42 ± 0.13 W** (B = `-0`), 0.50 and 0.52 of random data's 24.01 ± 0.08 W, for a product that is exactly zero; the `+0` mirror reads 0.75 ± 0.12 W in the same pass, so setting A's sign bits reads **11.37 ± 0.13 W** higher there. fp16: 12.48 ± 0.23 and 11.73 ± 0.18 W. [R1, R2; `e93.json` › `items`]
2. **By the manual and the RTL, a denormal is a zero the gate cannot see.** `0x00000001 × 0x00000001` costs **8.01 ± 0.08 W**, 0.08 ± 0.10 W from `-0.0 × -0.0`. Random denormals on both sides cost **9.42 ± 0.07 W** (fp16 9.25 ± 0.27 W), on A alone 12.79 ± 0.12 W (fp16 12.96 ± 0.11 W), on B alone 13.32 ± 0.13 W. The gate does not act on any of them (R3). **Power agrees with the manual and the RTL that the fraction never reaches the multiplier.** The flush itself is the documents' statement: PRM §3.4, the VPU specification §2.2.3.9, `txfma_7s/txfma_f0.v:302-318, 375-377`. No run reads a result (`runs.jsonl` › `result` is `unchecked`), so neither C nor the InputDenorm flag was read. What power shows: random denormal fractions cost 1.40 ± 0.08 W over a constant denormal (R4), about what their raw bits cost on the operand bus: 17.6 ± 1.0 fJ a bit, 25.6 ± 7.3 on A alone and 16.9 ± 3.5 on B alone, against E88's 19.3. In fp16, over `-0.0 × -0.0` because no fp16 constant denormal ran, 1.23 ± 0.29 W, 17.9 ± 4.2 fJ a bit (A alone 20.8 ± 9.3), against E88's 24.7. R4's lines are the midpoints between that bus price (1.54 W; fp16 1.69 W) and the reading if the fraction reached the Booth generator (8.41 W; fp16 5.48 W). That higher reading shares R5's per-bit price, which gives all of `r_abs`'s non-bus power, exponent path included, to Booth bits. R4's verdict does not need it: its high end, 1.488 W, is below the bus price alone and is 22% of the partial-product term even with no bus price at all. **A direct yardstick:** E88's `fp32.r_abs` on this card reads 16.54 ± 0.10 W with a frozen result and 75,694 bus bits, against `dnr_both`'s 9.42 ± 0.07 W with a frozen result and 70,976 bits: 7.1 W more for about the same number of moving bits on normal numbers. That is across sessions, `r_abs`'s exponents also move, and its result is frozen by absorption at a large accumulator where `dnr_both`'s stays `+0`. Cycles per op are 546.001 on every denormal tile, in E78's cycle gate: no stall. [R3, R4; `scored.json` › `reported.cycles_per_op`; [`corrections-check.txt`](corrections-check.txt) C1]
3. **int8's B gate wants eight bytes and pairs columns `(l, l+8)`: at power resolution on this card, in agreement with the RTL.** Three tiles hold the same words in different columns: same A, same eight nonzero B words a line, same operand bus bits. The eight zero words filling `(l, l+8)` pairs read **4.26 ± 0.19 W**; filling `(2l, 2l+1)` pairs **5.58 ± 0.14 W**; one zero word in every pair under both readings **5.50 ± 0.14 W**. So `b_pairs_alt` − `b_pairs_rtl` is **1.33 ± 0.20 W** (R6b), `b_unpaired` − `b_pairs_rtl` **1.25 ± 0.30 W** (R6a) and `b_unpaired` − `b_pairs_alt` -0.08 ± 0.18 W (R6c, the control). **The scorer names the RTL's reading and the data reject `(2l, 2l+1)`, so `gated_lane_frac` in `kinds.json` stands and no int8 gate figure on the page changes.** Stop quoting `gated_lane_frac_alt_grouping`, and do not edit `kinds.json`: it stays sha-pinned and unchanged, because the reducers from E82's to E95's refuse a changed file and `run_e78.py` takes its tile hashes from it. That grouping came from the wording of E79's amendment A4, which described how a lane reads B, not a gate; A6 replaced that wording with the RTL's on 31 Oct, and `docs/reports/data/2026-10-31-q130-rtl-formats/README.md` had settled the pair from the RTL. **What this power test can and cannot pick:** of 2,027,025 perfect pairings of the sixteen columns, 16 give these tiles' pattern (0.5, 0, 0). The data reject `(2l, 2l+1)`, `(l, l+2)`, `(l, l+4)`, `(l, 15-l)` and `(l, 14-l)`; among the 16 the RTL names `(l, l+8)`. Nor can power tell the RTL's AND from a per-unit gate plus lane-shared logic, which the RTL excludes (`vpu_ctrl.v:827`). [R6a–c; `scored.json` › `primary.pairing_reading`; [`corrections-check.txt`](corrections-check.txt) C9, C10]
4. **int8's A test is the whole word.** One nonzero byte in every A word, the other three zero, costs **5.80 ± 0.20 W**, 0.83 of random int8's 6.96 ± 0.20 W; all four bytes zero, with the same B bytes, **0.40 ± 0.25 W**: a difference of **5.40 ± 0.22 W**. Against `int8.full`, whose B is a different draw, the three zero bytes read 1.16 W lower, unregistered. [R7]
5. **A masked sparse tile pays for its negative zeros.** E78's `sparse50` tile reads 6.93 ± 0.22 W (S 8.78 ± 0.29 W over idle). The same tile with 46% of its zero words on both operands made `-0.0` (A 61 of 131, B 63 of 138), as `x * mask` leaves them when `x` is negative, reads **12.75 ± 0.15 W: 5.82 ± 0.15 W more, 1.84× in D (S 14.61 ± 0.17 W, 1.66×), with the same numbers by value.** The gate's share of column slots falls from 0.774 to 0.485 by `tile_stats`. The gain is more than the +3.7 W registered: the tile's own band prediction FAILS ([8.42, 12.42] W), so the frozen prices understate what those lanes cost. The tile is synthetic: E78's zeros with a chosen sign, not a measured pruned network. [R8; tile table; [`corrections-check.txt`](corrections-check.txt) C6]
6. **R5 FAILS.** The prediction was that a live zero costs more on B than on A, by about +3.1 W, because `fa` is the Booth multiplier (`txfma_f1.v:113-114`): A = 0 holds every digit at zero, while B = 0 still lets a negative digit give all ones (`txfma_booth_ppg_32r4_norm.v`, 368,544 partial-product bits an op in `make_e93.py`'s emulation against 0). Measured: **0.31 ± 0.16 W** in fp32, against a line of +1. **The shortfall is 2.793 W: 1.718 W is `a_nz_b_randn` above its point and 1.075 W is `a_randn_b_nz` below its point.** So most of it is a live zero on A costing more than priced, and `a_randn_b_nz` still shows 3.89 W over the clocked lane and its bus bits, against 4.34 W priced. The registered per-bit price was all of `r_abs`'s non-bus power, exponent path included, given to Booth bits. **The registered failure readings** (E93.md) are that the partial products do not swing as the public Booth generator says, or are held off a zero operand. The RTL speaks against a hold-off: `fa_en` and `fb_en` are `REN1` and `REN2`, set by the instruction, not by the operand (`txfma_c0.v:412-413`). Power does not separate the two. This README's first version replaced those readings with two of its own without saying so; they are back, and its two (a swing of whole partial products costing less per bit; B's fan-out, exponent and sign costing more than E88's terms hold) are untested candidates. **fp16's −0.75 ± 0.16 W is the bus** (predicted +0.4 to +1.6 W, reported, no verdict): E88's bus price alone gives −0.77 W, and over it the two tiles leave 2.99 and 2.98 W. Only fp32 has anything left over the bus price, +0.91 W. [R5; `reported.booth_asymmetry_w`; [`corrections-check.txt`](corrections-check.txt) C3, C5]
7. **Item 2 of the page stays open; a tile that would test it.** A = `-0`, B random has a zero-magnitude product, a frozen `+0` result and a sign that flips on about half the micro-ops. Over the clocked lane plus the moving operand's bits at E88's price, the one-sided `-0` tiles leave **2.98 W in fp32 at 0.507 sign flips a lane-cycle and 1.58 exponent bits; 2.98 W in fp16 with A = `-0`, at 0.972 and 2.78; 2.99 W in fp16 with B = `-0`, at 0.512 and 1.47; and 3.89 W in fp32 with B = `-0`, at 0.258 and 0.75** (the last two also have their partial products swinging). The residual does not scale with sign flips or with exponent bits, and B's fraction also reaches the F1 flop, the seventeen Booth muxes and the trailing-zero logic (`txfma_f1.v:81-82, 113-114, 190-205`), so these tiles do not price a sign. `-0 × |randn|` against `-0 × randn` would separate sign flips from the rest. No such tile ran. [[`corrections-check.txt`](corrections-check.txt) C2]
8. **int8's gate law leaves 0.65 W on a half-gated tile.** Live share × `full` + gated share × the fully gated tiles predicts 3.61 W for `b_pairs_rtl`; it reads 4.26 W, 0.611 of `full` with half the units off by the RTL's rule (inferred, not counted; band verdict INCONCLUSIVE). E82's `wsparse50` reads +0.25 ± 0.29 W against the same law, indistinguishable from zero. One reading, untested: something shared, such as the A broadcast, does not scale with live units. Per all 16 units, on the assumption that half of `full` is the data units' (`reported.int8_unit_costs_w`): gated 1.55 ± 0.31 W, live on a zero B word 4.05 ± 0.30 W, so a live unit with a zero B word costs 0.58 of a random one.

**What it means for the blog.** A zero the chip can see is almost free: about 0.4–0.8 W over exact zeros with the other operand random, on this card, against 24 W for random fp32 and 7 W for random int8. A zero it cannot see keeps the lane on. Whether it can see one is a question about bits, not values: `+0.0` is gated, `-0.0` and denormals are not, though by the manual and the RTL the float unit computes all three as zero. In int8 the B side needs all eight bytes of a column pair and the A side all four bytes of its word. See the sentences at the end, each with its baseline, its card and its source.

## The table

D over the type's zeros, S over the idle bracket, pJ/MAC from S at the measured op rate, all ± 95% over the five kept passes at the primary slope, statistical only; the rail is deconvolved and reported, never scored. A ΔT marked † (S ≤ 12 W) is limited by the die reading's 1 °C steps (E82 C1, E89), and does not rank those kinds. "Gated" is `kinds.json` or `tile_stats`' `gated_lane_frac` under the RTL's reading. "Predicted" and the band are the frozen `predictions-e93.json` › `tiles`; E78's own kinds carry none. Source: `e93.json` › `items`.

| tile | gated | D (W) | S (W) | pJ/MAC (S) | ΔT (°C) | Drail (W) | predicted (W) | band (W) | band verdict |
|---|---|---|---|---|---|---|---|---|---|
| `fp32.nz_both` | 0.000 | 7.94 ± 0.07 | 9.70 ± 0.12 | 2.114 ± 0.025 | 1.25† | 6.94 | 7.92 | [6.92, 8.92] | PASS |
| `fp32.dn1_both` | 0.000 | 8.01 ± 0.08 | 9.81 ± 0.19 | 2.137 ± 0.041 | 1.30† | 7.08 | 7.92 | [6.92, 8.92] | PASS |
| `fp32.dnr_both` | 0.000 | 9.42 ± 0.07 | 11.31 ± 0.06 | 2.463 ± 0.012 | 1.68† | 8.24 | 9.46 | [7.92, 10.96] | PASS |
| `fp32.a_nz_b_randn` | 0.000 | 12.11 ± 0.18 | 13.92 ± 0.12 | 3.032 ± 0.027 | 1.82 | 10.55 | 10.40 | [8.13, 12.66] | PASS |
| `fp32.a_dnr_b_randn` | 0.000 | 12.79 ± 0.12 | 14.60 ± 0.13 | 3.181 ± 0.028 | 1.92 | 10.97 | 10.90 | [8.64, 13.17] | PASS |
| `fp32.a_randn_b_nz` | 0.000 | 12.42 ± 0.13 | 14.22 ± 0.14 | 3.097 ± 0.029 | 1.75 | 10.81 | 13.50 | [10.87, 16.13] | PASS |
| `fp32.a_randn_b_dnr` | 0.000 | 13.32 ± 0.13 | 15.11 ± 0.20 | 3.290 ± 0.044 | 1.95 | 11.41 | 14.53 | [11.90, 17.16] | PASS |
| `fp32.sparse50_mask` | 0.485 | 12.75 ± 0.15 | 14.61 ± 0.17 | 3.180 ± 0.037 | 1.79 | 10.99 | 10.42 | [8.42, 12.42] | FAIL |
| `fp32.sparse50` | 0.774 | 6.93 ± 0.22 | 8.78 ± 0.29 | 1.911 ± 0.062 | 1.00† | 6.10 | — | — | — |
| `fp32.a_zeros_b_randn` | 1.000 | 0.75 ± 0.12 | 2.60 ± 0.04 | 0.565 ± 0.009 | 0.42† | 0.70 | — | — | — |
| `anchor_pi` | 0.000 | 8.08 ± 0.08 | 9.99 ± 0.10 | 2.177 ± 0.021 | 1.08† | 7.14 | — | — | — |
| `fp32.randn` | 0.000 | 24.01 ± 0.08 | 25.84 ± 0.09 | 5.629 ± 0.018 | 3.26 | 20.03 | — | — | — |
| `fp32.zeros` | 1.000 | 0.00 ± 0.00 | 1.88 ± 0.13 | 0.409 ± 0.028 | 0.05† | 0.00 | — | — | — |
| `fp16.nz_both` | 0.000 | 8.02 ± 0.26 | 9.74 ± 0.12 | 1.061 ± 0.013 | 1.13† | 7.05 | 7.96 | [6.96, 8.96] | PASS |
| `fp16.dnr_both` | 0.000 | 9.25 ± 0.27 | 11.06 ± 0.14 | 1.204 ± 0.015 | 1.12† | 8.03 | 9.64 | [7.96, 11.14] | PASS |
| `fp16.a_nz_b_randn` | 0.000 | 12.48 ± 0.23 | 14.19 ± 0.09 | 1.545 ± 0.011 | 1.88 | 10.85 | 10.77 | [8.50, 13.03] | PASS |
| `fp16.a_dnr_b_randn` | 0.000 | 12.96 ± 0.11 | 14.66 ± 0.06 | 1.596 ± 0.006 | 1.85 | 11.18 | 11.34 | [9.07, 13.60] | PASS |
| `fp16.a_randn_b_nz` | 0.000 | 11.73 ± 0.18 | 13.56 ± 0.17 | 1.477 ± 0.018 | 1.43 | 10.20 | 11.78 | [9.15, 14.41] | PASS |
| `fp16.randn` | 0.000 | 21.59 ± 0.15 | 23.34 ± 0.10 | 2.542 ± 0.011 | 2.84 | 18.00 | — | — | — |
| `fp16.zeros` | 1.000 | 0.00 ± 0.00 | 1.81 ± 0.13 | 0.197 ± 0.014 | -0.06† | 0.00 | — | — | — |
| `int8.b_pairs_rtl` | 0.500 | 4.26 ± 0.19 | 6.56 ± 0.13 | 0.208 ± 0.004 | 1.00† | 3.75 | 3.61 | [2.86, 4.36] | INCONCLUSIVE |
| `int8.b_pairs_alt` | 0.000 | 5.58 ± 0.14 | 8.05 ± 0.09 | 0.255 ± 0.003 | 1.00† | 4.92 | 5.76 | [3.90, 7.37] | PASS |
| `int8.b_unpaired` | 0.000 | 5.50 ± 0.14 | 7.90 ± 0.20 | 0.250 ± 0.006 | 1.00† | 4.93 | 5.76 | [3.90, 7.37] | PASS |
| `int8.a_3of4_b_full` | 0.000 | 5.80 ± 0.20 | 8.04 ± 0.09 | 0.255 ± 0.003 | 1.00† | 5.08 | 4.68 | [2.00, 7.37] | PASS |
| `int8.a_zeros_b_full` | 1.000 | 0.40 ± 0.25 | 2.81 ± 0.14 | 0.089 ± 0.004 | 0.17† | 0.38 | — | — | — |
| `int8.full` | 0.000 | 6.96 ± 0.20 | 9.35 ± 0.04 | 0.296 ± 0.001 | 1.09† | 6.06 | — | — | — |
| `int8.zeros` | 1.000 | 0.00 ± 0.00 | 2.37 ± 0.20 | 0.075 ± 0.006 | -0.00† | 0.00 | — | — | — |

**Band verdicts: 15 PASS, 1 INCONCLUSIVE (`int8.b_pairs_rtl`), 1 FAIL (`fp32.sparse50_mask`).** E93.md registers that the bands "test the gate law and E88's prices on a new corner", and that a miss "says the prices do not carry there", not that the gate rule is wrong; `int8.b_pairs_rtl`'s band holds no E88 price at all, only the gate law on E82's numbers (0.5 × `full` + 0.5 × the gated tiles). The two that miss are read in results 5 and 8.

## The registered rules

At the primary reduction (dips removed, leakage frozen at E82's 0.2414 W/°C), in pass units, 5 kept passes (`scored.json` › `primary.rules`):

| rule | contrast | W, ± 95% | line | verdict |
|---|---|---|---|---|
| R1-fp32-both | `fp32.nz_both` | 7.936 ± 0.068 | low > 5.0; high < 2.0 fails | **PASS** |
| R1-fp32-a | `fp32.a_nz_b_randn` − `fp32.a_zeros_b_randn` | 11.367 ± 0.133 | low > 5.0; high < 2.0 fails | **PASS** |
| R1-fp32-b | `fp32.a_randn_b_nz` − 0.631 (E82) | 11.791 ± 0.127 | low > 5.0; high < 2.0 fails | **PASS** |
| R1-fp16-both | `fp16.nz_both` | 8.022 ± 0.255 | low > 5.0; high < 2.0 fails | **PASS** |
| R1-fp16-a | `fp16.a_nz_b_randn` − 0.761 (E82) | 11.719 ± 0.231 | low > 5.0; high < 2.0 fails | **PASS** |
| R1-fp16-b | `fp16.a_randn_b_nz` − 0.624 (E82) | 11.101 ± 0.177 | low > 5.0; high < 2.0 fails | **PASS** |
| R2-fp32 | `fp32.nz_both` − `anchor_pi` | -0.147 ± 0.138 | inside ±1.0 | **PASS** |
| R2-fp16 | `fp16.nz_both` − 8.085 (E82) | -0.063 ± 0.255 | inside ±1.0 | **PASS** |
| R3-fp32-one | `fp32.dn1_both` | 8.013 ± 0.080 | low > 5.0; high < 2.0 fails | **PASS** |
| R3-fp32-both | `fp32.dnr_both` | 9.418 ± 0.073 | low > 5.0; high < 2.0 fails | **PASS** |
| R3-fp32-a | `fp32.a_dnr_b_randn` − `fp32.a_zeros_b_randn` | 12.041 ± 0.209 | low > 5.0; high < 2.0 fails | **PASS** |
| R3-fp32-b | `fp32.a_randn_b_dnr` − 0.631 (E82) | 12.694 ± 0.127 | low > 5.0; high < 2.0 fails | **PASS** |
| R3-fp16-both | `fp16.dnr_both` | 9.249 ± 0.274 | low > 5.0; high < 2.0 fails | **PASS** |
| R3-fp16-a | `fp16.a_dnr_b_randn` − 0.761 (E82) | 12.202 ± 0.111 | low > 5.0; high < 2.0 fails | **PASS** |
| R4-fp32-both | `fp32.dnr_both` − `fp32.dn1_both` | 1.405 ± 0.083 | high < 4.98 | **PASS** |
| R4-fp32-a | `fp32.a_dnr_b_randn` − `fp32.a_nz_b_randn` | 0.674 ± 0.191 | high < 3.94 | **PASS** |
| R4-fp16-both | `fp16.dnr_both` − `fp16.nz_both` | 1.227 ± 0.286 | high < 3.58 | **PASS** |
| R4-fp16-a | `fp16.a_dnr_b_randn` − `fp16.a_nz_b_randn` | 0.483 ± 0.215 | high < 2.48 | **PASS** |
| R5-fp32 | `fp32.a_randn_b_nz` − `fp32.a_nz_b_randn` | 0.308 ± 0.158 | low > 1.0; high < 1.0 fails | **FAIL** |
| R6a | `int8.b_unpaired` − `int8.b_pairs_rtl` | 1.249 ± 0.301 | low > 0.3; high < 0.3 fails | **PASS** |
| R6b | `int8.b_pairs_alt` − `int8.b_pairs_rtl` | 1.326 ± 0.196 | low > 0.3; high < 0.3 fails | **PASS** |
| R6c | `int8.b_unpaired` − `int8.b_pairs_alt` | -0.078 ± 0.177 | inside ±0.6 | **PASS** |
| R7 | `int8.a_3of4_b_full` − `int8.a_zeros_b_full` | 5.398 ± 0.217 | low > 1.0; high < 1.0 fails | **PASS** |
| R8 | `fp32.sparse50_mask` − `fp32.sparse50` | 5.821 ± 0.149 | low > 1.0; high < 1.0 fails | **PASS** |

**The arms** (`scored.json` › `arms`): no rule's verdict moves at any of the six. Passes kept, PASS / FAIL / INCONCLUSIVE, the tie and the two sharpest contrasts:

| arm | slope (W/°C) | kept passes | tally | tie E82 / E91 | R6b | R5 |
|---|---|---|---|---|---|---|
| dips_kept | 0.2414 | 4 (9313 set aside) | 23 / 1 / 0 | PASS / PASS | +1.456 | +0.183 |
| auto | 0.2346 | 5 (none set aside) | 23 / 1 / 0 | PASS / PASS | +1.326 | +0.308 |
| leak0.1994 | 0.1994 | 5 (none set aside) | 23 / 1 / 0 | PASS / PASS | +1.322 | +0.306 |
| leak0.3803 | 0.3803 | 5 (none set aside) | 23 / 1 / 0 | PASS / FAIL | +1.341 | +0.315 |
| leak0.545 | 0.5450 | 5 (none set aside) | 23 / 1 / 0 | FAIL {'fp16.randn': -0.73, 'fp32.randn': -0.96, 'int8.full': -0.25} / FAIL | +1.358 | +0.323 |
| leak0 | 0.0000 | 4 (9311 set aside) | 23 / 1 / 0 | FAIL {'fp16.randn': 0.83, 'fp32.randn': 0.8, 'int8.full': 0.4} / FAIL | +1.316 | +0.297 |

The session's own `auto` slope is 0.235 W/°C over 127 runs, within 3% of E82's 0.2414, unlike E91's short session (0.42). The tie's failures at 0.3803, 0.545 and 0 are the slope moving random data by up to 1 W against E82's frame, as they must; across the arms the 24 rule contrasts move by at most 0.60 W, and the int8 contrasts R6a–c and R5 by at most 0.13 W. At `dips_kept` E78's gates set 9313 aside: fp16.randn spans 1.098 W; anchor_pi drifts -0.700 W. At `leak0` E78's gates set 9311 aside: fp32.zeros departs -0.255 W from its straight line.

**The session tie** (`scored.json` › `primary.tie`, `tie_e91`):

| cell | against | D (W) | theirs (W) | difference | band | verdict |
|---|---|---|---|---|---|---|
| `anchor_pi` | E82 | 8.083 ± 0.075 | 8.095 | -0.013 | ±0.5 | PASS |
| `fp16.randn` | E82 | 21.588 ± 0.151 | 21.442 | +0.146 | ±0.5 | PASS |
| `fp32.a_zeros_b_randn` | E82 | 0.747 ± 0.125 | 0.723 | +0.023 | ±0.25 | PASS |
| `fp32.randn` | E82 | 24.006 ± 0.075 | 23.987 | +0.019 | ±0.5 | PASS |
| `fp32.sparse50` | E82 | 6.933 ± 0.216 | 6.760 | +0.173 | ±0.75 | PASS |
| `int8.a_zeros_b_full` | E82 | 0.404 ± 0.255 | 0.335 | +0.068 | ±0.25 | PASS |
| `int8.full` | E82 | 6.963 ± 0.198 | 6.869 | +0.094 | ±0.25 | PASS |
| `anchor_pi` | E91 at 0.1994 | 8.083 ± 0.075 | 8.108 | -0.025 | ±0.5 | PASS |
| `fp16.randn` | E91 at 0.1994 | 21.588 ± 0.151 | 21.713 | -0.125 | ±0.5 | PASS |
| `fp32.randn` | E91 at 0.1994 | 24.006 ± 0.075 | 24.116 | -0.110 | ±0.5 | PASS |
| `int8.full` | E91 at 0.1994 | 6.963 ± 0.198 | 6.943 | +0.020 | ±0.25 | PASS |

**Reported, beside the rules** (`scored.json` › `reported`, `checks`): denormal − `-0` per side: fp32 both 1.48 ± 0.10, constant 0.08 ± 0.10, A 0.67 ± 0.19, B 0.90 ± 0.19; fp16 both 1.23 ± 0.29, A 0.48 ± 0.22 W. So a raw denormal bit costs about what E88's operand-bus price says. E78-R5's checks: idle consistency median 0.080 W (≤ 0.15), rail lag re-fitted 0.95 s, duty 0.9960–0.9964, carry-over 0.0028 ± 0.0011 W/W, cycles per op 546.001 / 546.001 / 318.0, idle 33.08 ± 0.03 W at the launch reading. Dip samples removed per pass: 3, 10, 11, 5, 3.

## Registered against what happened

| | registered | happened |
|---|---|---|
| freeze | before the claim and the first launch | `d470f6a9` pushed 00:11:18; claim 00:12:27; first block's t0 00:12:31 |
| dry | one whole pass with `V3_DRY=1`, before the commit | 00:10:24–00:10:33 on aifoundry1: 42 launches, 17 on E93 tiles, all `ET_DEVICES=1`; every file identical to the freeze |
| smoke | eight 2 s runs, cycles per op, before any pass | 00:12:31–00:13:20: 546.0 on `fp32.dnr_both`, `fp32.nz_both`, `fp16.dnr_both` as on the anchors, 318.0 in int8, ok, 600 MHz, 65/65 (`aifoundry1-c1/kinds/kinds-smoke-p9301`) |
| passes | 9310–9314, at least four, by the budget rule | all five, 00:13:29–00:45:34, 361 / 368 / 368 / 386 / 382 s; the queue ended at 1,940 of 2,280 s. A run took 8.9 s, not the 10.2 s the plan used |
| kept | at least 3 kept to score | **5 of 5**; none set aside by the registered gates |
| skipped runs | a run whose launch reading is not reached is skipped, never launched off protocol | 2 of 200: 9311 `int8.full` (its third anchor) and 9314 `anchor_pi` (the opening tie), each time the reading went back to 59 °C inside the 2.0 s quiet wait. Both passes are kept by the registered code; 9314's tie drift is uncomputable |
| budget | about 40 card-minutes, claim to release | 36.5 min |
| config | read at both ends of every block, never set | TDP 65, threshold 65, `managed_power`, 600 MHz, 499 mV in all twelve reads, smoke included |

**Departures:** none from the registration. The departures from the brief's tile list (the fp16 B-side denormal and constant denormal left out; only the fp32 A-side +0 mirror in the pass) are in E93.md, decided before the data.

## What it closes and what it leaves open

- **Closes item 4 of section 11 at power resolution on one card, in agreement with the RTL** (the zero gate on silicon): int8's eight-byte B rule (R6a), its column pairing (R6b, R6c), denormal words against exact zeros (R3, R4); and the same for negative zero (R1, R2) and int8's A rule (R7). `kinds/README.md` §1.3's open question has its reading on the card: `(l, l+8)`, which the RTL had settled.
- **Item 2 stays open** (where a sign's cost goes): result 7 prices no sign; the tile that would test it is named there.
- **Leaves open, or opens:** R5's failure: why a live zero on A costs 1.72 W more than priced, and why fp32 keeps +0.91 W over the bus price where fp16 keeps none; why the mask tile costs 2.2 W more than E88's prices say; the +0.65 W on a half-gated int8 tile. Power is the only reading here: the micro-op counters were not read, so gated lanes are inferred, not counted. One card, one fixed set of tiles.

## Blog sentences, each with its baseline, its card and its source

- The gate compares raw bits: on one ET-SoC-1 card (1,024 minions, 600 MHz), `-0.0 × -0.0` costs 7.9 W of board power over `+0.0 × +0.0` in fp32 and 8.0 W in fp16, about what multiplying two constants costs. [R1-fp32-both, R1-fp16-both, R2-fp32; the rule: `vpu_ctrl.v:1229-1234`]
- On the same card, `0x00000001 × 0x00000001` costs 8.0 W over exact zeros in fp32, and random denormals on both operands add 1.4 W, about what their raw bits cost on the operand bus. The manual and the RTL say the float unit flushes them, and power agrees: about the same number of moving bits on normal numbers, with a frozen result, costs about 7 W more on this card (E88's `r_abs`, another session, whose exponents also move). [R3-fp32-one, R4-fp32-both; PRM §3.4; `txfma_f0.v:375-377`; `corrections-check.txt` C1]
- With one operand `-0.0` and the other random, the product is exactly zero and still costs 12.1 W over exact zeros in fp32 on this card (A = `-0.0`; 12.4 W with B = `-0.0`), about half of random data's 24.0 W, where a real `+0.0` on A costs 0.75 W. [`e93.json` › `items`]
- A zero the gate sees is almost free, not free: about 0.4–0.8 W over exact zeros with the other operand random on this card, against 24 W for random fp32 and 7 W for random int8. [`corrections-check.txt` C4]
- In int8 on this card, the same words with the same operand bus bits read 4.26 W over int8's zeros when the eight zero words a line fill columns `(l, l+8)`, and 5.50–5.58 W otherwise; `(2l, 2l+1)` is rejected at power resolution, in agreement with the RTL. [R6a–c]
- An int8 A word with one nonzero byte reads 5.8 W over int8's zeros on this card, against 0.4 W when all four bytes are zero, with the same B bytes. [R7]
- A synthetic 50%-sparse fp32 tile with both operands masked and about half its zero words `-0.0`, as `x * mask` leaves them when `x` is negative, goes from 6.9 to 12.8 W over fp32's zeros on this card (8.8 to 14.6 W over idle), with the same numbers by value. It is a synthetic tile, not a measured pruned network. [R8; `corrections-check.txt` C6]
- A prediction that failed: from the public Booth generator, a live zero should cost more on B than on A, by about 3.1 W in fp32 and 0.4 to 1.6 W in fp16. On this card, over each type's zeros, the difference is +0.31 ± 0.16 W in fp32 and −0.75 ± 0.16 W in fp16, and E88's bus price alone accounts for fp16's. [R5-fp32; `reported.booth_asymmetry_w`; `corrections-check.txt` C3, C5]

## Files

`e93.json` the primary reduction (dips removed, 0.2414 W/°C), `e93-dipskept.json`, `e93-auto.json`, `e93-leak<k>.json` the arms, with their `reduce*.txt/.log` and `runs*.csv`; `scored.json` every verdict, arm and reported number; `results.md` the same in tables; `code.sha256`; `corrections-check.py` and `corrections-check.txt` the desk check behind the corrections; `logs/` the queue, the dry pass, push and claim times; `aifoundry1-c1/kinds/p93<nn>/` each pass's raw data (telemetry, marks, runs, tile dumps, config reads, manifest), `kinds-smoke-p9301` the smoke. Reproduce from the raw passes: `PY=python3 bash tools/claims-v3/kinds/collect_e93.sh 'p93[1-9][0-9]' <raw root>`.

## Corrections after verification (Sun 1 Nov 2026)

An independent verifier (Q132's `verify-e93`) checked E93 after the data commit (`9105d764`) and the README (`5048b2f6`). Its verdict: holds with fixes, no major fault, ten minor faults and three trivial points, all in how the results were stated. It re-reduced the raw telemetry with its own code (largest |D − `runs.csv`| 0.0 over 198 rows, every rule's mean and half-width equal to `scored.json`) and re-ran the registered scorer (`results.md` byte for byte, `scored.json` within 1e-9). It found the registration timing, the frozen rules, the harness hashes, the tile dumps, the gate shares and bus bits, the Booth counts and the public text sound. Each fault is corrected above, desk only: no card was touched, nothing was re-run, and no registered prediction, rule, number or verdict changed (23 PASS, 1 FAIL). `e93*.json`, `runs*.csv`, `scored.json`, `results.md`, `reduce*`, `E93.md`, `predictions-e93.json` and `kinds.json` are byte-identical to the data commit; [`corrections-check.txt`](corrections-check.txt) opens with their sha256. Every number below is printed by [`corrections-check.py`](corrections-check.py) into that file, under the section named.

| # | what was wrong | what changed |
|---|---|---|
| C1 | **"The float unit does flush them" was stated as measured** (result 2, two blog sentences). No run reads a result (`runs.jsonl` › `result` is `unchecked` in all 1,980 launch records), so neither C nor the InputDenorm flag was read: R4 bounds multiplier activity only. The raw fraction bits are the whole contrast (17.6 ± 1.0, 25.6 ± 7.3 and 16.9 ± 3.5 fJ a bit in fp32; 17.9 ± 4.2 and 20.8 ± 9.3 in fp16). The 8.41 W yardstick rests on the per-bit price R5 failed on | Result 2 now says power agrees with the manual and the RTL that the fraction never reaches the multiplier, and cites the documents for the flush. It says the 8.41 W shares R5's price, gives R4's high end against the bus price (1.488 against 1.541 W; 22% of the 6.87 W partial-product term with no bus price), and adds the direct yardstick: E88's `r_abs` 16.54 ± 0.10 W against `dnr_both`'s 9.42 ± 0.07 W, 7.1 W, across sessions, `r_abs`'s exponents also moving |
| C2 | **"Narrows item 2" from result 7.** It set A = `-0` × B random's 2.98 W beside E88's 2.52 W sign cost and said that "would make a sign's cost independent of the magnitude it carries". The same residual appears at different flip rates (2.98, 2.98 and 2.99 W at 0.507, 0.972 and 0.512 flips a lane-cycle and 1.58, 2.78 and 1.47 exponent bits), so it scales with neither. The tile reads 0.46 W above the high arm, which already holds the sign price, and B's fraction also reaches the F1 flop, the Booth muxes and the trailing-zero logic | The sentence and the "narrows" wording are deleted. Item 2 stays open. Result 7 gives the residuals and keeps the proposed tile, `-0 × \|randn\|` against `-0 × randn` |
| C3 | **R5's failure was reported, but its cause was asserted** ("What fails is the price, not the gate"), and the registered failure readings were replaced with two new ones without saying so. The shortfall was not decomposed. fp16's "other sign" was listed as open | Result 6 carries the registered readings and what the RTL says of them (`fa_en`, `fb_en` are `REN1`, `REN2`: against a hold-off; power does not separate them), says the replacement happened, and names its two as untested candidates. Shortfall 2.793 W = 1.718 W (`a_nz_b_randn` above its point) + 1.075 W (`a_randn_b_nz` below its point); `a_randn_b_nz` still shows 3.89 W against 4.34 W priced; "the registered per-bit price was all of `r_abs`'s non-bus power". fp16's −0.755 W is the bus (−0.769 W from E88's price; residuals 2.99 and 2.98 W). The open list now asks why fp32 keeps +0.91 W |
| C4 | **"A zero the chip can see is free."** It reads 0.75 ± 0.12 W (fp32 A = +0), E82's 0.62–0.76 W, int8 0.40 ± 0.25 W, and 1.55 ± 0.31 W for gated units in the half-gated tile. The same paragraph's "the test needs all eight bytes" is int8's B side only | "Almost free: about 0.4–0.8 W over exact zeros with the other operand random, against 24 W (fp32) and 7 W (int8)". B needs eight bytes, A four |
| C5 | **The failed-prediction blog sentence mixed predictions**: "about 3 W" is fp32's; fp16's was +0.4 to +1.6 W, unscored | Each format now has its own prediction |
| C6 | **Blog sentences without a baseline or scope.** "Switching power from 6.9 to 12.8 W" reads as over idle, where S is 8.78 to 14.61 W (1.66×, not 1.84×). The mask tile masks both operands, and 46% of its zero words took the sign (A 61 of 131, B 63 of 138), not half | Every blog sentence states its baseline and its card; result 5 and its sentence say both operands, about half (46%), and give S beside D. "A pruned matrix" became "a masked sparse tile" |
| C7 | fp16's R4 number changed baseline silently: "1.40 W over a constant denormal… in fp16 1.23 W". fp16's contrast is over `nz_both`; no fp16 constant denormal ran | Result 2 says so |
| C8 | **The bands were described too narrowly.** E93.md says they test "the gate law and E88's prices"; the README dropped the gate law, and `int8.b_pairs_rtl`'s band holds no E88 price. "Same sign as E82's `wsparse50` residual" hid that the residual is +0.25 ± 0.29 W, indistinguishable from zero | The table's note quotes E93.md and says so; result 8 gives E82's interval |
| C9 | **"`gated_lane_frac_alt_grouping` can be retired" needed a limit.** R6 rejects the grouping, but `kinds.json` is sha-pinned: `reduce_e82.py` to `reduce_e95.py` refuse a changed file, including E94's and E95's, and `run_e78.py` takes its tile hashes from it. The field is also in `real.json` and `real2.json`, and `make_e93.py:323-324` asserts it. A4's wording described read structure, not a gate; A6 replaced it on 31 Oct (`tools/claims-v3/hlp/README.md:274-276`); `q130-rtl-formats/README.md:146` had settled the pair from the RTL | "Stop quoting it; do not edit `kinds.json`", naming A6 and the RTL note. `kinds.json` is unchanged |
| C10 | **"Closed by measurement" should say by power, on one card.** `q130-zero-gate-correction/README.md:74-75` names the micro-op counters as the reading that does not infer; they were not read. 16 of 2,027,025 pairings give the tile pattern, so R6 rejects `(2l, 2l+1)`, `(l, l+2)`, `(l, l+4)`, `(l, 15-l)`, `(l, 14-l)` and the RTL names the rest. Power cannot tell the AND from a per-unit gate plus lane-shared logic, which the RTL excludes (`vpu_ctrl.v:827`). "With half the units off" is inferred | "Closed at power resolution on one card, in agreement with the RTL", in the opening and in § What it closes. Result 3 states the limits; result 8 says inferred |
| C11 | Small things. "The same as multiplying two constants": −0.147 ± 0.138 W just excludes 0, inside the registered ±1 W. "Save 1.2 W against random" was unregistered, and `int8.full`'s B is a different draw from `a_3of4_b_full`'s. Push 00:11:19 against origin/main's reflog 00:11:18; first device access 00:12:32 against the block's t0 00:12:31.3 | "About what two constants cost", with the interval. The 1.16 W is marked unregistered, different draw. The times are fixed here; `logs/push-and-claim-times.txt` keeps the lane's command-output times as written |

The verifier's report was not judged wrong anywhere. Four small refinements of its wording, each stated above: C2's third residual (fp16 with B = `-0`) also has its partial products swinging, and result 7 adds fp32 with B = `-0`, 3.89 W at 0.258 flips, beside its three. C3's decomposition is given to three decimals (its 1.07 W is 1.075 W). The `r_abs` yardstick's result is frozen by absorption at a large accumulator, where `dnr_both`'s stays `+0`. The C2 tile's distance from its high arm is 0.456 W (it wrote 0.45 W).
