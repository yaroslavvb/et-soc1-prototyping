# E92: where a random sign's cost goes (aifoundry3, 600 MHz)

*Sun 1 Nov 2026 (week 44), Q132, item 2 of the kinds page's section 11. Pre-registered in `6b8f23f1` (committed 00:16:46
PDT and pushed by 00:16:51, before the claim and the first launch):
[`tools/claims-v3/kinds/E92.md`](../../../../tools/claims-v3/kinds/E92.md), frozen numbers in `predictions-e92.json`, tiles and
counts in `e92/e92.json`; the scorer `score_e92.py` was in the same commit. aifoundry3 card 0 at 600 MHz, 521.6 mV mean, TDP 0 /
threshold 65 °C / 600 MHz / 523 mV read under the card lock at the session's start (00:17:13) and end (00:55:39), never set.
Nothing was written to the card, and no `--reset-ms` was sent. Claim 1566350374279979111 in #community-lab, posted 00:17:10
PDT, released 00:55 PDT (39 min, inside the registered 45).*

**What ran.** 32 tiles (`tools/claims-v3/kinds/e92/`) that hold the operands fixed and change only the sign the running sum
holds, so the same stream always adds, always subtracts or alternates: the sum's sign is set by the k = 0 product, which a
launch's first MUL pass loads. Frozen sums at magnitude 1 (`c_abs`, `c_neg`, `c_alt`, `h_add`, `h_sub`, `h_allsub`), the A-side
twin (`i_add`, `i_sub`), a ladder of 2, 4, 6 of 8 lanes (`h_sub<m>`), E88's random signs (`s_abs`) and a low-flip control
(`k_only`); frozen sums on random positive magnitudes (`r_abs`, `r_h_add`, `r_h_sub`); moving sums at magnitude 1 (`w_c`,
`w_h_add`, `w_h_sub`) and on random magnitudes (`r_walk`, `wr_h_add`, `wr_h_sub`); E90's `fp32.signs`, `fp16.signs`; fp16's core
(`c_abs`, `c_alt`, `h_add`, `h_sub`, `h_allsub`), its two aligners apart (`hh_sub`, `hl_sub`) and frozen random signs (`s_abs`).
Beside them in every pass: E78's six anchors three times, `fp32.ones` and `fp16.ones` once, the `anchor_pi` tie first and last.
E78's runner and reduction ran unchanged (sha256-checked). Four passes ran (9210–9213), 216 runs, no run failed. **E78's
random-anchor gate set pass 9211 aside (`fp32.randn` spans 1.344 W, limit 1.0, a board-reading dip), so the primary reduction
keeps three passes, 162 runs.** D is a tile's board power over its own type's zeros. Every interval is 95% over passes,
t(0.975, n−1) × SE; every contrast is paired within each pass. Numbers in parentheses are the registered dips-removed arm (E86's
method, all four passes kept), a sensitivity arm here because the primary kept at least three passes; "rail" is `Drail` in the
primary reduction, which the board meter's dips do not touch.

## Results

**In plain words.** Take the same numbers in the same order, and change only the sign the running sum happens to hold. If that
makes the adder alternate between adding and subtracting, the chip draws 4.4 W more in fp32 and 6.9 W more in fp16, with the
same operands (only the sign bits of the one seed row that sets the sum's sign differ) and the result frozen. If the adder only ever subtracts, it draws nothing extra (0.04 W). So a sign's cost
is not the sign bit and not subtraction; it is the *change* from adding to subtracting, about 1,100 fJ a time in fp32, 9× a
sign bit's own flip. **Of random signs' ~5 W in fp32, about 0.6 W is the sign bits, 1.4–2.0 W the add/subtract switching and
2.5–3.0 W the sums moving apart. In fp16 almost all of it is there with the sum frozen.**

**1. The same operands; only the sum's sign differs.** (`scored.json` › `contrasts`, `dips-arm/scored-nodips.json`,
`posthoc-check.txt` A.)

| contrast | what differs | fp32 D (W), primary (dips-removed) | registered, verdict | fp16 D (W), primary (dips-removed) | registered, verdict |
|---|---|---|---|---|---|
| `h_add` − `c_abs` | B, product and sum signs all move, the adder always adds | **0.558 ± 0.143** (0.538 ± 0.100) | bits 0.563; ≤ 1.126: **CONFIRMED** | 0.954 ± 1.026 (0.482 ± 0.176) | bits 0.313; ≤ 0.626: INCONCLUSIVE |
| `h_sub` − `h_add` | the same operands at k ≥ 1; alternates against always adds | **4.425 ± 0.443** (4.396 ± 0.247) | 3.72, [1.86, 7.44]: **CONFIRMED** | **6.856 ± 0.405** (6.812 ± 0.246) | 4.03, [2.01, 8.05]: **CONFIRMED** |
| `c_alt` − `c_abs` | no operand or product sign moves at k ≥ 1; alternates against always adds | **5.076 ± 0.446** (5.059 ± 0.237) | 3.72, [1.86, 7.44]: **CONFIRMED** | 7.766 ± 1.583 (7.258 ± 0.212) | 4.03, [2.01, 8.05]: INCONCLUSIVE (high end 9.35; CONFIRMED in the dips arm) |
| `h_allsub` − `h_add` | the same operands at k ≥ 1; always subtracts against always adds | **0.040 ± 0.348** (0.049 ± 0.186) | ±0.50: **CONFIRMED** | 0.186 ± 0.319 (0.147 ± 0.204) | ±0.50: INCONCLUSIVE (high end 0.505; CONFIRMED in the dips arm) |
| `c_neg` − `c_abs` | nothing moves at k ≥ 1; always subtracts against always adds | **0.015 ± 0.062** (0.013 ± 0.034) | ±0.50: **CONFIRMED** | not run | |

Nothing here is REFUTED. On the rail the two core contrasts are 3.463 ± 0.461 and 5.375 ± 0.116 W, and `c_alt` − `c_abs` 4.161
± 0.110 and 5.906 ± 0.392 W. **E65's `bit_31` was cheap because its accumulators only ever add:** `h_add`, the same layout with
frozen sums, costs 0.558 W against E65's 0.563 W. E88's named guess is right, and it has a size: `c_alt` flips no operand and no
product sign at k ≥ 1 and costs 5.08 W; a steady subtract, 0.015 W.

**2. The factorial: the add/subtract switch is nearly all of it.** With `c_abs` as the origin, `h_add` = α + β, `c_alt` = β + γ +
δ/2, `h_sub` = α + γ + δ/2, `h_allsub` = α + β + δ, solved per pass (`scored.json` › `factorial`; reported, no verdict):

| | γ: the add/subtract switch (W) | fJ per lane alternation | α: B and product signs (W) | β: C and result signs (W) | δ: a steady subtract (W) |
|---|---|---|---|---|---|
| fp32 | **4.731 ± 0.134** (4.703 ± 0.105) | 1,099 (1,092) | 0.233 ± 0.198 (0.206 ± 0.133) | 0.326 ± 0.338 (0.332 ± 0.178) | 0.040 ± 0.348 (0.049 ± 0.186) |
| fp16 | **7.218 ± 0.836** (6.962 ± 0.123) | 1,677 (1,617) | 0.499 ± 0.426 (0.259 ± 0.106) | 0.455 ± 0.601 (0.223 ± 0.094) | 0.186 ± 0.319 (0.147 ± 0.204) |

An alternation costs 9× a sign-bit flip in the same layout (fp32: 1,099 against 122 fJ per lane-micro-op; `posthoc-check.txt` H).

**3. It is linear in lanes, and half at half the rate.** The ladder, 2, 4, 6 of 8 lanes alternating, lies on the line through
`c_abs` and `h_sub` to +0.091 ± 0.142, −0.068 ± 0.131 and −0.191 ± 0.271 W (R5 **CONFIRMED**, band ±0.744): slope 0.603 ± 0.036
W per lane, intercept 0.057 ± 0.114 W, 1,121 fJ per alternation (`scored.json` › `ladder`). The A-side twin, alternating every two
micro-ops through the A word's sign: `i_sub` − `i_add` = 2.494 ± 1.529 W (2.169 ± 0.193; rail 1.931 ± 0.095), half of `h_sub`'s
to +0.282 ± 1.347 W (R4 INCONCLUSIVE: a dip in pass 9212's `i_add`; −0.029 ± 0.082 W in the dips arm, CONFIRMED). **Random signs
cost a little less per alternation in fp32:** `s_abs` beyond its bits is 0.41–0.44 of `h_sub` beyond its bits, where the
alternation count says 0.54 (R6 fp32 −0.605 ± 0.502 W, INCONCLUSIVE; −0.436 ± 0.192, CONFIRMED in the dips arm). In fp16 they
cost more per flip: 0.61–0.64, where the two `eff_sub` counts added say 0.50 and "either changes" says 0.74 (R6 fp16 +1.036 ± 0.540 W,
INCONCLUSIVE; +0.808 ± 0.112 in the dips arm, whose interval straddles the ±0.805 W band, also INCONCLUSIVE) (`posthoc-check.txt` D). So R6 is INCONCLUSIVE.

**4. In fp32 the alternation's price follows the adder's flops, across every regime.** The premium, always add against alternate
on the same operands (`posthoc-check.txt` B, I):

| regime | premium (W), primary (dips-removed) | rail (W) | flop bits the reading adds an op | fJ per flop bit | frozen prediction (W) | verdict |
|---|---|---|---:|---|---|---|
| frozen, magnitude 1 | **4.425 ± 0.443** (4.396 ± 0.247) | 3.463 | 560,592 | 7.0 | alt 3.72; e88+flops 3.92 | R2 CONFIRMED |
| frozen, random magnitudes | **4.381 ± 0.644** (4.460 ± 0.425) | 3.511 | 560,592 | 7.0 | the same as above within ±0.744 | R7 **CONFIRMED** (−0.043 ± 0.206) |
| moving sums, magnitude 1 | **2.785 ± 0.356** (2.797 ± 0.189) | 2.115 | 343,288 | 7.2 | e88+flops 2.49 | R8 CONFIRMED |
| moving sums, random magnitudes | 0.407 ± 3.186 (**1.106 ± 0.181**) | 0.592 | 155,761 | 6.3 (dips arm) | e88+flops 0.65; E90 read as linear 2.57 | R8 INCONCLUSIVE (a −21.5 W dip in pass 9213's `wr_h_sub`); CONFIRMED in the dips arm, which excludes 2.57 W |

An absorbed product is zapped before the inversion, so its magnitude does not matter (R7). With moving sums, and more with random
ones, the adder's inputs already move, and an alternation has less left to flip: **part of why E90's sign step is 5.0 W at magnitude 1
and only 1.9 W on random magnitudes.** On random magnitudes with moving sums the premium is about a quarter of the frozen one (the dips arm; the primary cannot resolve it).

**5. fp16's alternation is dearer, and its two aligned products share most of it.** Over `c_abs`, only the high product alternating
(`hh_sub`) costs 6.871 ± 1.584 W (6.403 ± 0.423; rail 5.238), only the low one (`hl_sub`) 5.829 ± 1.149 W (5.501 ± 0.237; rail 4.371),
both (`h_sub`) 7.810 ± 1.411 W (7.294 ± 0.121; rail 5.828). Either alone costs 75–88% of both, so they do not add: hh + hl − both is
**+4.890 ± 1.627 W** (+4.611 ± 0.511). The registered direction holds, `hh_sub` − `hl_sub` = +1.043 ± 0.516 W (0.902 ± 0.329), the
52-bit bus above the 29-bit one, but its lower bound misses the registered 0.686 W: R10 INCONCLUSIVE. The flop reading predicted the
non-additivity at +1.77 W, and it prices fp16's alternation at half of what it costs: 11–18 fJ per flop bit, against fp32's 7
(`posthoc-check.txt` C, I). **fp16 pays 1.5× fp32 per alternation, and the RTL bench saw it coming.** Q132(b)'s bench, core-et's whole `vpu_top` with a correct multiply-add, froze its
prediction from E78 and RTL counts alone at 00:43:14 PDT (`de545f0c`), before any E92 pass was read ([`e92-bench-prediction.json`](../2026-11-01-q132-rtl-bench/e92-bench-prediction.json), `nets_hier2`): `hh_sub` 0.855 and `hl_sub` 0.737
of both (measured 0.88 and 0.75), hh + hl − both +4.04 W (measured +4.89 ± 1.63, +4.61 ± 0.51). Its counts say why: fp32's alternation moves almost only the adder and normaliser (1.36 M of 1.53 M net toggles a minion-op over the
unit), and fp16's moves them more (1.79 M) and also the operand (0.32 M), exponent (0.30 M), result (0.23 M), control (0.16 M) and multiplier (0.12 M) stages (`posthoc-check.txt` K).

**6. Where the ~5 W goes.** (`scored.json` › `budget`, `posthoc-check.txt` E.)

| | fp32 (W) | fp16 (W) |
|---|---|---|
| ±1 − +1, this session | 4.851 ± 1.128 (5.016 ± 0.219); E90 5.006 ± 0.517 | 4.826 ± 0.467 (4.965 ± 0.089); E90 5.079 ± 0.403 |
| frozen: `s_abs` − `c_abs` | **2.377 ± 0.556** (2.520 ± 0.171); E88 on card 1: 2.524 ± 0.185 | **5.073 ± 1.239** (4.587 ± 0.116) |
| of which the sign bits (E65/E67/E79's prices, frozen) | 0.569 | 0.297 |
| of which the rest, read as the add/subtract switch | 1.81 (1.95) | 4.78 (4.29) |
| the moving-sum part: ±1 − +1, less frozen | **2.474 ± 1.597** (2.497 ± 0.367) | −0.246 ± 1.374 (0.378 ± 0.096) |
| frozen share | 0.495 ± 0.228 (0.503 ± 0.053) | 1.052 ± 0.285 (0.924 ± 0.019) |
| the switch at its moving-sum price × ±1's rate | 1.43 (1.43), leaving 2.83 (2.99) for the moving sums | no moving-sum pair run in fp16 |

So in fp32, about 0.6 W is the sign bits, 1.4–2.0 W the switch (frozen price above, moving-sum price below) and 2.5–3.0 W the sums moving
apart. **E90's equal 5 W steps in fp32 and fp16 are not one mechanism's price:** half of fp32's is there with the sum frozen, and 92–105%
of fp16's.

**7. The kinds page's design point.** A design where every product over the whole op keeps one sign forces the signs onto k alone: `k_only`
flips 256 sign bits an op and costs 0.094 ± 0.295 W (0.070 ± 0.175; R9 **CONFIRMED**, ±0.50). So that design tests nothing, as this
run's brief expected. But one sign *per accumulator* allows full-rate flips (`h_add`, `i_add`), at the sign bits' own price (E92.md, "A design
point, checked").

**8. The models.** Frozen before the data (`predictions-e92.json`), over the 22 contrasts with a rule (`scored.json` › `rules.E92-S2`, `posthoc-check.txt` J):

| model | fp32 rms, 15 contrasts (W) | fp16 rms, 7 contrasts (W) | what it gets wrong |
|---|---|---|---|
| **e88+flops**: E88's frozen prices + one price per flop bit of the adder, calibrated on E88's M32s alone | **0.283** (0.270) | 2.220 (1.959) | fp16's alternation, at half |
| **e88**: E88's frozen four prices, no term for the effective operation | 2.916 (2.922) | 5.128 (4.850) | it says `h_sub` − `h_add` is −0.41 W; 9 of 22 inside its bands |
| **the RTL bench** (Q132(b), frozen `de545f0c`, before any pass was read: 1.827 fJ per merged-net toggle + 1.082 fJ per clocked register bit, fitted on E78 alone) | 0.759 (0.727) | **0.611 (0.299)** | fp32's alternation, about a quarter low (3.22 W against 4.43); it has fp16's right (6.44 against 6.86) |
| **Q130(n)'s predictor** | | | 21 of 32 tiles inside its 95% intervals: it prices sign flips, not alternations (`h_add` 13.96 W, measured 9.00) |

**Post hoc, labelled, no rule depends on it** ([`posthoc-fit.txt`](posthoc-fit.txt), `posthoc_fit_e92.py`): refit on this card alone, over E78's,
E90's and E92's float tiles, four prices give rms 1.304 W (leave-one-out 1.433) over 47 fp32 tiles and 1.788 W (1.995) over 34 fp16 tiles; **adding the
one flop price gives 0.288 W (0.325) and 0.485 W (0.577)**, at 7.7 and 10.8 fJ per flop bit. On E86's six real GPT-2 float tiles, never in the fit, it
misses by 0.174 W (fp32) and 0.524 W (fp16) rms, where "each costs E78's random kind" already scores 0.353 and 0.446 W and Q130(n) 0.155 and 0.393 W: those tiles sit too near
random to test it. It is a strong lead on the kinds page's item 6, not a validated model.

**9. The session tied.** Every reference lies within its band of E78's and E90's (S1 **PASS**; `posthoc-check.txt` G): fp32 and fp16 randn
+0.23 / +0.11 W, ones +0.24 / +0.02 W against E78, `anchor_pi` +0.15 W, int8 full +0.07 W; `fp32.signs`, `fp16.signs` +0.01 / −0.10 W against E90.
Against E88 across cards (S3): `s_abs` − `c_abs` 2.377 W against the scaled 2.602 W; `c_abs` 8.437 W against the scaled 8.166 W, both inside.
**Heat and pJ** (reported, `e92.json` › `items`): `fp32.c_abs` 2.25 pJ/MAC by S, `h_sub` 3.33, `fp16.c_abs` 1.07, `h_sub` 1.93; on the whole-degree reading `h_sub` warms the
die 2.0 °C in 2 s (S 15.3 W), `c_abs` 1.35 °C (S 10.3 W, below the ~12 W where the reading decides a 2 s window).

## Registered against happened

| rule | registered | happened | primary | leakage arms 0.1994 / 0.3803 / 0 | dips-removed arm |
|---|---|---|---|---|---|
| E92-R1 sign bits | `h_add` − `c_abs` ≤ 2 × bits | fp32 0.558 ± 0.143 against 1.126 CONFIRMED; fp16 0.954 ± 1.026 against 0.626 INCONCLUSIVE | **INCONCLUSIVE** | the same | INCONCLUSIVE (fp16 0.482 ± 0.176: high end 0.658) |
| E92-R2 alternation | `h_sub` − `h_add`, `c_alt` − `c_abs` inside [0.5, 2] × alt | three CONFIRMED; fp16 `c_alt` 7.766 ± 1.583 high end above 8.05 | **INCONCLUSIVE** | the same | CONFIRMED |
| E92-R3 steady subtract | inside ±0.50 W | fp32 and `c_neg` CONFIRMED; fp16 0.186 ± 0.319, high end 0.505 | **INCONCLUSIVE** | CONFIRMED / INCONCLUSIVE / INCONCLUSIVE (slope-sensitive) | CONFIRMED |
| E92-R4 A-side | half, ±0.744 W | +0.282 ± 1.347 | **INCONCLUSIVE** | the same | CONFIRMED (−0.029 ± 0.082) |
| E92-R5 ladder | linear, ±0.744 W | all three rungs inside | **CONFIRMED** | the same | CONFIRMED |
| E92-R6 random at the same price | ±0.744, ±0.805 W | −0.605 ± 0.502; +1.036 ± 0.540 | **INCONCLUSIVE** | the same | INCONCLUSIVE (fp32 CONFIRMED) |
| E92-R7 magnitude | ±0.744 W | −0.043 ± 0.206 | **CONFIRMED** | the same | CONFIRMED |
| E92-R8 moving sums | e88+flops, [0.5, 2] × | `w` 2.785 ± 0.356 CONFIRMED; `wr` 0.407 ± 3.186 INCONCLUSIVE | **INCONCLUSIVE** | the same | CONFIRMED (`wr` 1.106 ± 0.181) |
| E92-R9 low-flip control | ±0.50 W | 0.094 ± 0.295 | **CONFIRMED** | CONFIRMED / INCONCLUSIVE / CONFIRMED (slope-sensitive) | CONFIRMED |
| E92-R10 two aligners | lower bound ≥ 0.686 W | +1.043 ± 0.516 | **INCONCLUSIVE** | the same | INCONCLUSIVE (0.902 ± 0.329) |
| E92-S1 session tie | within bands | all cells inside | **PASS** | PASS / FAIL / FAIL (those arms correct D by another slope than the one E78's and E90's values carry, as in E86 and E90) | PASS |
| E92-S2 models, S3 tie to E88 | reported | as above | reported | | |

**Primary: 3 CONFIRMED, 7 INCONCLUSIVE, 0 REFUTED of the ten rules; S1 PASS.** Of the 20 per-contrast tests inside them, 12 are CONFIRMED, 8 INCONCLUSIVE and none REFUTED; most of the
INCONCLUSIVE ones are wide intervals from the dips. **The dips-removed arm, all four passes: 7 CONFIRMED, 3 INCONCLUSIVE (R1, R6, R10), 0 REFUTED.** It is a registered
sensitivity arm, and it moves no primary verdict. The core rule's contrast, `h_sub` − `h_add`, is CONFIRMED in fp32 and fp16 in every arm.

**The dips.** The board meter's launch-gap dips were unusually frequent: 39 in four passes, 22 in power windows (E90: 19 in three, 4), up to 21.5 W deep, on a handful of runs each
(`dips-arm/dips.json`; `posthoc-check.txt` F). They set pass 9211 aside and widen the primary's intervals; they do not move its means by much except where noted. The rail shows none of it.
**Checks:** leakage slope 0.1396 W/°C over 194 runs (E90: 0.2203); idle consistency median |S − S0 − D| 0.085 W; carry-over 0.0003 ± 0.0023 W/W; rail lag 1.0 s; duty 0.9958–0.9966;
cycles per op 546.001 / 546.001 / 318.0; every dumped tile equal to its registered sha256; the tie's drift 0.24–0.43 W a pass; 600 MHz, 521.6 mV throughout.

**Departures and disclosures.** None from E92.md's protocol. (1) The collection ran over a copy of the raw passes inside the repo's ignored `build/` tree, as E86 and E90 did. (2) No interim look at power:
the waits read only the queue log. The collection script was exercised on the self-test's synthetic passes first. (3) `posthoc_fit_e92.py` was written during the run, before any pass was read, and first run
on synthetic E92 values with E78's and E90's measured ones; its held-out test on E86's tiles and `posthoc-check.py` were written after the data. Neither is a registered test, and no rule depends on them. (4) The
registered budget expected ~43 card-min and 10 min a pass; it took 39 and 9. (5) The runner's log lines read "E78 pass … tiles verified against kinds.json": `run_e78.py`'s unchanged strings, as in E90.
(6) `code.sha256` was refreshed after the collection for one file, `posthoc_fit_e92.py`, edited after it ran. (7) The comparison with Q132(b)'s bench is post hoc on my side; the bench's prediction is its lane's, frozen before these passes were read, and E92 was not designed to test it.

## Interpretation (labelled: a reading of the public RTL, not measured)

The fused multiply-add's effective operation is `eff_sub1 = sign(P) ^ sign(C)` (`external/core-et/rtl/shire/minion/vpu/txfma_7s/txfma_c2.v:144`, `:161`). On an effective subtract, **all 52 bits of the
aligned operand are inverted** into the carry-save adder (`txfma_c2.v:303`, `:364`; `txfma_f3.v:384-421`), whose sum and carry are flopped (`:120-121`) and fed to a 52-bit adder, a leading-digit anticipator and a
trailing-zero counter (`txfma_f4.v:61-119`). A product shifted out of range is zapped to 0, so the bus is all 0s when adding and all 1s when subtracting, whatever the product is. When the operation holds, none of it
moves; when it flips, all of it does. That is what the measurements show in fp32: nothing for a steady subtract, about 1,100 fJ a flip, no dependence on an absorbed product's magnitude, and a price that falls as
moving sums and random mantissas already move those nets. A flop-level count of the reading, with one price calibrated on one datum from another card, predicted fp32's 15 contrasts to 0.28 W rms before the data.
**E92 itself does not identify the gates**: the count is a reading, the card's C was not read back (the host skips its check for file tiles, E88 C8), and any net that moves with `eff_sub` is inside γ. fp16's extra cost is not
in the flop count. The stage comes from the RTL bench's net counts (`de545f0c`): the adder and normaliser take 89% of fp32's alternation and 60% of fp16's, and its predictions track the silicon (result 8). The moving-sum part is E88's stream count of the C read and the result bus swinging between accumulators that have drifted apart (R32s, R32bus), not split further here.

## What it changes

- **The kinds page's item 2 closes.** The "adder alternates between adding and subtracting" guess is confirmed on silicon: with the operands fixed, the sum's sign alone moves 4.4–5.1 W in fp32 and 6.9–7.8 W in fp16, and a steady
  subtract moves nothing; the RTL bench, frozen first, places it in the adder and normaliser. Left open: fp16's alternation with moving sums (no pair run); the bench's quarter-low price on fp32's alternation; the moving-sum part's split.
- **"Power is paid for operand bits that change" needs one more clause.** A sign bit costs what a sign bit costs (0.56 W for 4,096 flips) unless it flips the adder's operation.
- **E90's "fp16 pays the same 5 W as fp32" is two different splits** that land on the same number. Its reading, that a sign's cost lives on the accumulate side and not on the operand bits, stands in both formats.
- **The kinds page's item 6 gains a lead:** one more feature, the adder's flop bits, cuts the four-price model's error 3.7–4.5× over every fp32 and fp16 tile on this card (post hoc).

## Caveats

Three passes in the primary (t = 4.30), four in the dips arm (t = 3.18), one card, one clock. All tiles are designed: C sits at ±(n+1)·2^100 or a small integer, not where a real tensor's lands, and 1 µop in 16 (k = 0) moves the sum even in the frozen
designs. Frozen against walking rests on the desk emulation (`make_e92.py --check`, 32 of 32) and on the power agreeing with it; C was not read back. The split in result 6 subtracts a frozen design from a walking one with different draws in fp32 (E88's `s_abs`
beside E90's `signs`), and it assumes the frozen cost carries over to a moving sum, which result 4 says it only partly does; hence the range. fp16's bits price is a bound. The flop count is a reading at the flop level, not a gate-level count. The post-hoc fit's
leave-one-out rms is in-family. The watts are the board's; the rail figures are about 0.8 of them.

## Files

`e92.json` (the registered reduction: every item, per pass), `runs.csv`, `reduce.txt`, the leakage arms (`e92-leak0.1994 / 0.3803 / 0 .json`, `.csv`, `.txt`), `scored.json` and `results.md` (every rule, the factorial, the budget, the ladder), `dips-arm/` (the registered dips-removed arm:
`dips.json`, `e92-nodips.json`, `scored-nodips.json`, `results-nodips.md`), `code.sha256`, `logs/` (the queue and dry-run logs, the session's start and end config reads, the binaries' sha256), `aifoundry3/kinds/` (the four passes' raw data and the smoke, `kinds-smoke-p9201`),
`posthoc-check.py` / `.txt` (labelled post hoc: every number above beyond `scored.json`, from committed files, standard library only), `posthoc-fit.json` / `.txt` / `posthoc-fit-nodips.txt` (labelled post hoc). The tiles and the registration are in `tools/claims-v3/kinds/` (`E92.md`, `e92/`,
`predictions-e92.json`, `make_e92.py`, `make_predictions_e92.py`, `e92_common.py`, `run_e92.py`, `reduce_e92.py`, `score_e92.py`, `posthoc_dips_e92.py`, `posthoc_fit_e92.py`, `block_e92.sh`, `queue_e92.sh`, `run_e92.sh`, `collect_e92.sh`, `selftest_e92.py`).
