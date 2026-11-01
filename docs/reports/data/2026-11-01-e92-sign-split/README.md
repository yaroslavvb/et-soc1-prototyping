# E92: where a random sign's cost goes (aifoundry3, 600 MHz)

*On the kinds page, [section 11, what is still open](https://spacesheep.dev/@yaroslavvb/horace-kinds-of-numbers#11-what-is-still-open): "Where a random sign's ~5 W goes" (old item 2).*

*Sun 1 Nov 2026 (week 44), Q132, item 2 of the kinds page's section 11. Pre-registered in `6b8f23f1` (committed 00:16:46
PDT and pushed by 00:16:51, before the claim and the first launch):
[`tools/claims-v3/kinds/E92.md`](../../../../tools/claims-v3/kinds/E92.md), frozen numbers in `predictions-e92.json`, tiles and
counts in `e92/e92.json`; the scorer `score_e92.py` was in the same commit. aifoundry3 card 0 at 600 MHz, 521.6 mV mean, TDP 0 /
threshold 65 °C / 600 MHz / 523 mV read under the card lock at the session's start (00:17:13) and end (00:55:39), never set.
Nothing was written to the card, and no `--reset-ms` was sent. Claim 1566350374279979111 in #community-lab, posted 00:17:10
PDT, released 00:55 PDT (39 min, inside the registered 45).*

*Corrected after verification, Sun 1 Nov 2026, at the desk, with no card touched and nothing re-run (§ [Corrections after
verification](#corrections-after-verification-sun-1-nov-2026), C1–C13). The kinds page's item 2 narrows rather than closes: R2 is
INCONCLUSIVE in the primary and in the leakage arms, and the split is an estimate. fp16's frozen share is stated arm by arm, and nothing is claimed
about a different mechanism. The fp32 split is labelled modelled; 1,100 fJ and 9× hold with the result frozen; the post-hoc refit's 0.29 / 0.49 W are
in-sample; the bench said 2.0× for fp16 over fp32, not 1.5×. No number in `e92*.json`, `runs*.csv`, `scored.json`, `results.md` or `dips-arm/` changed, no
registered verdict changed, and no frozen input changed.*

*Corrected again, Sun 1 Nov 2026, after [E104](../2026-11-01-e104-c-readback/README.md) read the accumulators back off the card (§ [Corrections after E104](#corrections-after-e104-sun-1-nov-2026), C14–C24). **E92's fp16 "frozen" tiles are not frozen on silicon** (read on aifoundry1 card 1, not on aifoundry3: the arithmetic is digital, and the same tile bytes ran on another card of the same chip). No registered verdict label changes, all of fp32 stands, R10 stands, and every frozen and data file stays. What goes is the fp16 reading: the prose on "sum frozen" for fp16, "about 92% remains", the 5.8 against 30 fJ gap as unexplained, "1.55× per alternation", and the fp16 fit prices. R2's, R3's and R6's fp16 legs did not test a frozen sum.*

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
method, all four passes kept; its rule is in C12), a sensitivity arm here because the primary kept at least three passes; "rail" is `Drail` in the
primary reduction, which the board meter's dips do not touch.

## Results

**In plain words.** One card, 600 MHz, board power, designed tiles. Take the same numbers in the same order, and change only the sign the
running sum holds (only the sign bits of the one seed row that sets it differ). With the sum frozen, making the adder alternate between adding and
subtracting draws 4.4 W more in fp32 than always adding; the sign bits themselves work against that number. The same design in fp16 draws 6.9 W more, but its sums are not frozen: [E104](../2026-11-01-e104-c-readback/README.md) read them back, and about 3 W of it goes with the two halves of each lane's sums parting (C14). Always subtracting, with
the sum frozen, draws nothing measurable in fp32 (0.04 ± 0.35 W). So with the result frozen a sign's cost is not its bit and not subtraction; it is the *change*
from adding to subtracting, about 1,100 fJ a time in fp32, 9× all four sign paths moving while the adder only adds. The premium falls as sums move: 4.4 W frozen, 2.8 W
with moving sums at magnitude 1, about 1.1 W on random magnitudes (the dips-removed and raw-median readings; the primary cannot resolve that one). **Measured: ±1 − +1 is 4.851 ±
1.128 W (5.016 ± 0.219) in fp32, and 2.377 ± 0.556 W (2.520 ± 0.171) of it remains with the sum frozen, about half; in fp16, 4.826 ± 0.467 W (4.965 ± 0.089), E92 ran no frozen tile, and in [E104](../2026-11-01-e104-c-readback/README.md)'s, which holds on zero products, on another card, about 45% remains, an estimate (C15). Estimated by subtraction, not measured: of fp32's ~5 W, about 0.6 W is the sign bits, 1.4–2.0 W the
add/subtract switching and 2.5–3.0 W the sums moving apart.** The registered rule for the alternation, R2, is INCONCLUSIVE in the primary, because one contrast of four runs above its band.

**1. The same operands; only the sum's sign differs.** (`scored.json` › `contrasts`, `dips-arm/scored-nodips.json`,
`posthoc-check.txt` A.)

| contrast | what differs | fp32 D (W), primary (dips-removed) | registered, verdict | fp16 D (W), primary (dips-removed) | registered, verdict |
|---|---|---|---|---|---|
| `h_add` − `c_abs` | B, product and sum signs all move, the adder always adds | **0.558 ± 0.143** (0.538 ± 0.100) | bits 0.563; ≤ 1.126: **CONFIRMED** | 0.954 ± 1.026 (0.482 ± 0.176) | bits 0.313; ≤ 0.626: INCONCLUSIVE |
| `h_sub` − `h_add` | the same operands at k ≥ 1; alternates against always adds | **4.425 ± 0.443** (4.396 ± 0.247) | 3.72, [1.86, 7.44]: **CONFIRMED** | **6.856 ± 0.405** (6.812 ± 0.246) | 4.03, [2.01, 8.05]: **CONFIRMED** |
| `c_alt` − `c_abs` | no operand or product sign moves at k ≥ 1; alternates against always adds | **5.076 ± 0.446** (5.059 ± 0.237) | 3.72, [1.86, 7.44]: **CONFIRMED** | 7.766 ± 1.583 (7.258 ± 0.212) | 4.03, [2.01, 8.05]: INCONCLUSIVE (high end 9.35; CONFIRMED in the dips arm) |
| `h_allsub` − `h_add` | the same operands at k ≥ 1; always subtracts against always adds | **0.040 ± 0.348** (0.049 ± 0.186) | ±0.50: **CONFIRMED** | 0.186 ± 0.319 (0.147 ± 0.204) | ±0.50: INCONCLUSIVE (high end 0.505; CONFIRMED in the dips arm) |
| `c_neg` − `c_abs` | nothing moves at k ≥ 1; always subtracts against always adds | **0.015 ± 0.062** (0.013 ± 0.034) | ±0.50: **CONFIRMED** | not run | |

Nothing here is REFUTED, **and the registered rule R2 is INCONCLUSIVE** in the primary and in all three leakage arms (CONFIRMED only in the dips-removed sensitivity arm): three
of its four contrasts are CONFIRMED, and `fp16.c_alt` − `c_abs` runs above its band, high end 9.35 W against 8.05 W, on the dips in `fp16.c_abs` (C1, C2). The core contrast, `h_sub` −
`h_add`, is CONFIRMED in fp32 and fp16 in every arm, and the lowest lower bound of the four is 3.98 W against a refutation line of 0.93 W. On the rail the two core contrasts are 3.463 ±
0.461 and 5.375 ± 0.116 W, and `c_alt` − `c_abs` 4.161 ± 0.110 and 5.906 ± 0.392 W. **E65's `bit_31` is the always-adding case:** its accumulators only ever add, and `h_add`, the same layout with
frozen sums, costs 0.558 W against E65's 0.563 W (the other always-adding pairs are in result 10). E88's named guess is answered on silicon with the sum frozen, in fp32 (fp16's legs did not test a frozen sum, C14), and it has a size: `c_alt` flips no
operand and no product sign at k ≥ 1 (its k = 0 row flips 256 B and product signs an op) and costs 5.08 W, which includes the sum signs' own β, 0.33 W; a steady subtract with nothing moving at k ≥ 1, 0.015 W.
A steady subtract was tested only with an absorbed product; no always-subtracting tile with moving sums ran.

**2. The factorial: with the sum frozen, in fp32, the add/subtract switch is nearly all of it (fp16's row is not a frozen sum, C14).** With `c_abs` as the origin, `h_add` = α + β, `c_alt` = β + γ +
δ/2, `h_sub` = α + γ + δ/2, `h_allsub` = α + β + δ, solved per pass (`scored.json` › `factorial`; reported, no verdict):

| | γ: the add/subtract switch (W) | fJ per lane alternation | α: B and product signs (W) | β: C and result signs (W) | δ: a steady subtract (W) |
|---|---|---|---|---|---|
| fp32 | **4.731 ± 0.134** (4.703 ± 0.105) | 1,099 (1,092) | 0.233 ± 0.198 (0.206 ± 0.133) | 0.326 ± 0.338 (0.332 ± 0.178) | 0.040 ± 0.348 (0.049 ± 0.186) |
| fp16 | **7.218 ± 0.836** (6.962 ± 0.123) | 1,677 (1,617) | 0.499 ± 0.426 (0.259 ± 0.106) | 0.455 ± 0.601 (0.223 ± 0.094) | 0.186 ± 0.319 (0.147 ± 0.204) |

With the result frozen, an alternation costs about 9× all four sign paths moving while the adder only adds (fp32: 1,099 against 122 fJ per lane-micro-op; `posthoc-check.txt` H). The 122 fJ is not one
bit's: B and product signs alone, α, are 51 fJ, and C and result signs, β, 71 fJ. The premium per alternation falls as sums move: 1,028 fJ frozen, 647 (650) fJ with moving sums at magnitude 1,
and 257 fJ in the dips arm on random magnitudes with moving sums, so 2–9× (`corrections-check.txt` C8). fp16's primary row carries the dips in `fp16.c_abs` (C1), and its γ and fJ are not a switch's price: `h_sub` and `c_alt` part their halves, so γ also holds what goes with the halves parting, 3.16 ± 0.51 W in [E104](../2026-11-01-e104-c-readback/README.md), whose halves-together premium is 3.55 ± 0.29 W at 0.904 of the alternations, 913 ± 74 fJ per lane alternation (C14, C16).

**3. It is linear in lanes (R5); half at half the rate is what the rail and the dips arm read, and R4 is INCONCLUSIVE in the primary.** The ladder, 2, 4, 6 of 8 lanes alternating, lies on the line through
`c_abs` and `h_sub` to +0.091 ± 0.142, −0.068 ± 0.131 and −0.191 ± 0.271 W (R5 **CONFIRMED**, band ±0.744): slope 0.603 ± 0.036
W per lane, intercept 0.057 ± 0.114 W, 1,121 fJ per alternation (`scored.json` › `ladder`). The A-side twin, alternating every two
micro-ops through the A word's sign: `i_sub` − `i_add` = 2.494 ± 1.529 W (2.169 ± 0.193; rail 1.931 ± 0.095, per pass 1.890, 1.965, 1.937), half of `h_sub`'s
to +0.282 ± 1.347 W (R4 INCONCLUSIVE: a dip in pass 9212's `i_add`; −0.029 ± 0.082 W in the dips arm, CONFIRMED). **Random signs
cost a little less per alternation in fp32:** `s_abs` beyond its bits is 0.41–0.44 of `h_sub` beyond its bits, where the
alternation count says 0.54 (R6 fp32 −0.605 ± 0.502 W, INCONCLUSIVE; −0.436 ± 0.192, CONFIRMED in the dips arm). In fp16, on tiles whose sums move (C19), they
cost more per flip: 0.61–0.64, where the two `eff_sub` counts added say 0.50 and "either changes" says 0.74 (R6 fp16 +1.036 ± 0.540 W,
INCONCLUSIVE; +0.808 ± 0.112 in the dips arm, whose interval straddles the ±0.805 W band, also INCONCLUSIVE) (`posthoc-check.txt` D). So R6 is INCONCLUSIVE.

**4. In fp32 the alternation's premium tracks the count of adder bits in three regimes, and the regime nearest real data runs above it.** The premium, always add against alternate
on the same operands. "Adder bits" are what E92.md and `posthoc-check.txt` call flop bits: `csa_in3`, 199,680 of `h_sub`'s 560,624, is combinational, so they are bit changes on the adder's inputs and flops
(`corrections-check.txt` C4). The fJ column is (premium − the model's e88 part) / adder bits:

| regime | premium (W), primary (dips-removed) | rail (W) | adder bits the reading adds an op | fJ per adder bit, primary (dips-removed) | frozen prediction (W) | this contrast's verdict |
|---|---|---|---:|---|---|---|
| frozen, magnitude 1 | 4.425 ± 0.443 (4.396 ± 0.247) | 3.463 | 560,592 | 7.69 ± 0.70 (7.64 ± 0.39) | alt 3.72; e88+flops 3.92 | CONFIRMED (R2 as a rule: INCONCLUSIVE) |
| frozen, random magnitudes | 4.381 ± 0.644 (4.460 ± 0.425) | 3.511 | the same count | 7.62 ± 1.02 (7.74 ± 0.68) | the same as above within ±0.744 | R7 CONFIRMED (−0.043 ± 0.206) |
| moving sums, magnitude 1 | 2.785 ± 0.356 (2.797 ± 0.189) | 2.115 | 343,288 | 7.67 ± 0.92 (7.70 ± 0.49) | e88+flops 2.49 | CONFIRMED (R8 as a rule: INCONCLUSIVE) |
| moving sums, random magnitudes | 0.407 ± 3.186 (1.106 ± 0.181) | 0.592 | 155,761 | 5.41 ± 18.25 (9.42 ± 1.04) | e88+flops 0.65; E90 read as linear 2.57 | INCONCLUSIVE (a −21.5 W dip in pass 9213's `wr_h_sub`); CONFIRMED in the dips arm |

The two frozen rows share one count, so this is three tests, not four, and they agree at 7.6–7.7 fJ. The fourth does not: in the dips arm its interval [0.925, 1.287] W excludes E90's 2.57 W and also the model's registered
0.652 W. It reads CONFIRMED only through the [0.5, 2]× band, and the model misses it by 0.45 W, 1.7×. The raw median says 1.06 ± 0.10 W. The registered f is 6.68 fJ on card 1; dividing the premium by the card scale first
gives 7.4–7.5 fJ in the first three rows and 9.2 in the fourth. 7 fJ per bit is about 26 fF at 0.52 V: a proxy for everything downstream of those bits, not a flop's price. A reading: an absorbed product is zapped before the
inversion, so its magnitude does not matter (R7), and with moving sums, and more with random ones, the adder's inputs already move, so an alternation has less left to flip. That is part of why E90's sign step is 5.0 W at magnitude 1
and only 1.9 W on random magnitudes. On random magnitudes with moving sums the premium is about a quarter of the frozen one in the dips arm and the raw medians; the primary cannot resolve it.

**5. fp16's `h_sub` premium is dearer than fp32's, and its two aligned products share most of it: they share one walk, as [E104](../2026-11-01-e104-c-readback/README.md) read back (C16).** Over `c_abs`, only the high product alternating
(`hh_sub`) costs 6.871 ± 1.584 W (6.403 ± 0.423; rail 5.238), only the low one (`hl_sub`) 5.829 ± 1.149 W (5.501 ± 0.237; rail 4.371),
both (`h_sub`) 7.810 ± 1.411 W (7.294 ± 0.121; rail 5.828). Either alone costs 75–88% of both, so they do not add: hh + hl − both is
**+4.890 ± 1.627 W** (+4.611 ± 0.511). The registered direction holds, `hh_sub` − `hl_sub` = +1.043 ± 0.516 W (0.902 ± 0.329), the
52-bit bus above the 29-bit one, but its lower bound misses the registered 0.686 W: R10 INCONCLUSIVE. The adder-bit count, taken from sums that do not exist on the card, predicted the
non-additivity at +1.77 W and priced these tiles at 11–17 fJ per adder bit with the model's e88 part, against fp32's 7.6–7.7 (`posthoc-check.txt` C; `corrections-check.txt` C4): those counts are wrong (C17). **The ratio of the two contrasts' watts is 1.552 ± 0.250 (1.552 ± 0.131). It is not a price per alternation: with the halves together on absorbed products, in [E104](../2026-11-01-e104-c-readback/README.md), the ratio is 0.947 ± 0.297, and on moving sums it is not resolved (C16). The RTL bench saw the direction and the two aligned products' overlap; it said 2.0×, outside both intervals (C6).** Q132(b)'s bench, core-et's whole `vpu_top` with a correct multiply-add, froze its
prediction from E78 and RTL counts alone at 00:43:14 PDT (`de545f0c`), before any E92 pass was read ([the file at that commit](https://github.com/yaroslavvb/et-soc1-prototyping/blob/de545f0c/docs/reports/data/2026-11-01-q132-rtl-bench/e92-bench-prediction.json), copied here as [`bench-prediction-de545f0c.json`](bench-prediction-de545f0c.json), `nets_hier2`; `e7cb1f21` later rewrote the path and added a post-hoc variant, not used here): `hh_sub` 0.855 and `hl_sub` 0.737
of both (measured 0.88 and 0.75), hh + hl − both +4.04 W (measured +4.89 ± 1.63, +4.61 ± 0.51). A reading of why, from its counts: fp32's alternation moves almost only the adder and normaliser (1.36 M of 1.53 M net toggles a minion-op over the
unit), and fp16's moves them more (1.79 M) and also the operand (0.32 M), exponent (0.30 M), result (0.23 M), control (0.16 M) and multiplier (0.12 M) stages (`posthoc-check.txt` K).

**6. How much of the ~5 W remains with the sum frozen, and an estimate of the split.** The first two rows and the frozen share are measured; the rest of the table is modelled or a residual. (`scored.json` › `budget`, `posthoc-check.txt` E, `corrections-check.txt` C1, C3.)

| | fp32 (W) | fp16 (W) |
|---|---|---|
| **measured:** ±1 − +1, this session | 4.851 ± 1.128 (5.016 ± 0.219); E90 5.006 ± 0.517 | 4.826 ± 0.467 (4.965 ± 0.089); E90 5.079 ± 0.403 |
| **measured:** `s_abs` − `c_abs`; frozen in fp32, **not frozen in fp16 (C14)** | **2.377 ± 0.556** (2.520 ± 0.171); E88 on card 1: 2.524 ± 0.185 | **5.073 ± 1.239** (4.587 ± 0.116) |
| **measured:** that over the step (raw medians beside); a frozen share in fp32 only | 0.495 ± 0.228 (0.503 ± 0.053); 0.468 | 1.052 ± 0.285 (0.924 ± 0.019); 0.933: **not a frozen share (C15)** |
| modelled: the sign bits (E65/E67/E79's prices × `s_abs`'s flips) | 0.569 | 0.297 |
| modelled: the rest of frozen, read as the add/subtract switch | 1.81 (1.95) | 4.78 (4.29): not the switch, C14 |
| a residual: ±1 − +1, less frozen | 2.474 ± 1.597 (2.497 ± 0.367) | −0.246 ± 1.374 (0.378 ± 0.096): two moving sums' difference, C15 |
| registered: γ × ±1's alternation rate | 2.424 ± 0.069 (2.410 ± 0.054) | 3.850 ± 0.446 (3.713 ± 0.066): this γ is not a switch's price, C14 |
| registered: frozen left after the bits and γ × `s_abs`' rate | −0.754 ± 0.484 (−0.597 ± 0.188) | +1.185 ± 0.830 (+0.827 ± 0.126): the same γ, and not a frozen tile, C14 |
| modelled: the switch at its moving-sum price × ±1's rate | 1.43 (1.43), leaving 2.83 (2.99) | no moving-sum pair run in E92; [E104](../2026-11-01-e104-c-readback/README.md): `m_h_sub` − `w_h_add` 3.271 ± 1.961 W |

**fp32, an estimate by subtraction, not a measurement:** about 0.6 W is the sign bits, 1.4–2.0 W the switch and 2.5–3.0 W the sums moving apart. The 0.6 W is a price list × `s_abs`' flips, not measured on that layout. The 1.4–2.0 W is two point estimates
under two assumptions, not an interval. Upper: all of `s_abs` − `c_abs` beyond the bits is the switch (1.808, [1.25, 2.36]; 1.951, [1.78, 2.12]), though γ at `s_abs`' rate, 2.55–2.56 W, overshoots what is there. Lower: the moving-sum premium × ±1's rate, 1.43 W, which assumes
linearity in alternation *rate* on moving sums, and nothing tested that (R5 is lanes on frozen sums, and random alternation costs 0.75–0.82× per flip). The 2.5–3.0 W is a residual, 2.474 ± 1.597 W in the primary, across different draws, and "the sums moving apart" is a reading. It has support:
`w_c` − `c_abs`, 3.987 ± 0.171 W with no alternation, is 29.7 fJ per result bit after the adder bits, and the moving part is 29.7 (30.0) fJ per bit. At that price reading (b) leaves 0.35 (0.50) W unaccounted (0.592 + 1.434 + 2.493 = 4.52 W against 5.016).

**fp16: E92 measured no frozen share.** Its `s_abs` is not frozen (C14): [E104](../2026-11-01-e104-c-readback/README.md) read it back as 9 distinct words where E92's emulation said one. Over `signs` − `ones` it reads 0.924 ± 0.019 in the dips arm and 1.052 ± 0.285 in the primary, high because two of its three passes carry dips in `fp16.c_abs` (D per kept pass 7.627, 8.473, 7.752; dips removed 8.582, 8.415, 8.468, 8.307); the raw medians give 0.933. That is the ratio of two tiles with moving sums, not a frozen share. **In a sum that truly holds, [E104](../2026-11-01-e104-c-readback/README.md)'s `z_s` − `c_abs`, random signs cost 2.153 ± 0.330 W, about 45% of the step carried to that card** (0.446 ± 0.068; post hoc, with A's signs still and zero products, so not `s_abs` less its walk). "fp16's moving part is 5.8 fJ per result bit against fp32's 30.0" is withdrawn as a gap: its 58,544 bits came from the frozen start, and on the RTL's sums `s_abs` holds more result bits than `signs` (71,292–79,196 against 61,068–63,698 an op, by the count and the op indices), so there was no such difference to price. [E104](../2026-11-01-e104-c-readback/README.md)'s `h_sub` − `u_sub` less fp32's same contrast is about 28 fJ per result bit as a lump, everything that moves when the halves part over the result bits (post hoc); that is not the 29.7 fJ above, which takes the adder bits off first (C17). An fp16 moving pair ran there too: 3.271 ± 1.961 W against fp32's 2.121 ± 2.457 W, ratio not resolved.

**7. The kinds page's design point.** A design where every product over the whole op keeps one sign forces the signs onto k alone: `k_only`
flips 256 sign bits an op and costs 0.094 ± 0.295 W (0.070 ± 0.175; R9 **CONFIRMED**, ±0.50). So that design tests nothing, as this
run's brief expected. But one sign *per accumulator* allows full-rate flips (E92.md, "A design point, checked"): `h_add` at 0.558 W, E65's price, and `i_add` at −0.031 ± 1.345 W (0.263 ± 0.136), under E67's 0.561 W and near its clean 0.297 W.

**8. The models.** Frozen before the data (`predictions-e92.json`), over the 22 contrasts with a rule (`scored.json` › `rules.E92-S2`, `posthoc-check.txt` J):

| model | fp32 rms, 15 contrasts (W) | fp16 rms, 7 contrasts (W) | what it gets wrong |
|---|---|---|---|
| **e88+flops** (its registered name): E88's frozen prices + one price per adder bit, calibrated on E88's M32s alone | **0.283** (0.270) | 2.220 (1.959) | fp16's `h_sub`-type tiles, counted from sums the card does not hold (C17) |
| **e88**: E88's frozen four prices, no term for the effective operation | 2.916 (2.922) | 5.128 (4.850) | it says `h_sub` − `h_add` is −0.41 W; 9 of 22 inside its bands |
| **the RTL bench** (Q132(b), frozen `de545f0c`, before any pass was read: 1.827 fJ per merged-net toggle + 1.082 fJ per clocked register bit, fitted on E78 alone) | 0.759 (0.727) | **0.611 (0.299)** | fp32's alternation, about a quarter low (3.22 W against 4.43); fp16's within 6% (6.44 against 6.86), and their ratio at 2.0× against 1.55× |
| **Q130(n)'s predictor** | | | 21 of 32 tiles inside its 95% intervals: it prices sign flips, not alternations (`h_add` 13.96 W, measured 9.00) |

**Post hoc, labelled, no rule depends on it** ([`posthoc-fit.txt`](posthoc-fit.txt), `posthoc_fit_e92.py`, `corrections-check.txt` C5): refit on this card alone, over E78's,
E90's and E92's float tiles. **In-sample**, four prices give rms 1.304 W over 47 fp32 tiles and 1.788 W over 34 fp16 tiles, and adding the one adder-bit price gives 0.288 W and 0.485 W, at 7.7 and 10.8 fJ. Leave-one-out on designed families
(0.325, 0.577 W) is in-family too. These are not a model's accuracy. **The fp16 prices in this paragraph (5.5, 10.8 fJ, "not identified") rest on the same miscounted bits and are withdrawn (C18); the fp32 ones stand.** **Out of family the price does not transfer:** fitted on the tiles E92 did not design and used to predict E92's designs, it scores 1.428 W in fp32 (four prices 2.370) and 2.743 W in fp16 (5.114), with 12.5 fJ per adder bit on those tiles against 7.3 on E92's designs in fp32, and
5.4 against 11.9 in fp16, opposite directions. That fit puts `h_sub` − `h_add` at +7.72 W in fp32 (measured +4.43) and +2.94 W in fp16 (measured +6.86), and fp16's result-bit price swings from 5.6 fJ (all tiles) to 32.9 fJ: not identified. The feature does help out of family, 1.7–1.9×, so it is a lead on the kinds page's item 6, not a validated model.
The fit also tried the alternation count in its place: in-sample 0.535 and 0.738 W; out of family 0.849 W in fp32, better, and 3.343 W in fp16, worse. On E86's six real GPT-2 float tiles, never in the fit, adder bits miss by 0.174 W (fp32) and 0.524 W (fp16) rms and alternations by 0.139 and 0.713 W, where "each costs E78's random kind" already scores 0.353 and 0.446 W and Q130(n) 0.155 and 0.393 W: those tiles sit too near
random to test it.

**9. The session tied.** Every reference lies within its band of E78's and E90's (S1 **PASS**; `posthoc-check.txt` G): fp32 and fp16 randn
+0.23 / +0.11 W, ones +0.24 / +0.02 W against E78, `anchor_pi` +0.15 W, int8 full +0.07 W; `fp32.signs`, `fp16.signs` +0.01 / −0.10 W against E90.
Against E88 across cards (S3): `s_abs` − `c_abs` 2.377 W against the scaled 2.602 W; `c_abs` 8.437 W against the scaled 8.166 W, both inside.
**Heat and pJ** (reported, `e92.json` › `items`): `fp32.c_abs` 2.25 pJ/MAC by S, `h_sub` 3.33, `fp16.c_abs` 1.07 (1.12 in the dips arm, C13), `h_sub` 1.93; on the whole-degree reading `h_sub` warms the
die 2.0 °C in 2 s (S 15.3 W), `c_abs` 1.35 °C (S 10.3 W, below the ~12 W where the reading decides a 2 s window).

**10. The rest of what E92.md registers as reported.** The sign bits against E65's 0.563 W, each pair always adding (`corrections-check.txt` C11): `h_add` − `c_abs` 0.558 ± 0.143 (0.538 ± 0.100); `w_h_add` − `w_c`, with sums walking as E65's do, 0.550 ± 0.311 (0.532 ± 0.175); `r_h_add` − `r_abs` 0.578 ± 0.522 (0.510 ± 0.347); `wr_h_add` − `r_walk` 1.622 ± 1.937 (1.188 ± 0.178), 2× E65 in the
dips arm, probably through its seed's extra result bits (121,679 against 108,962; a reading). E88's contrasts on this card: M32 `r_abs` − `c_abs` 8.886 ± 0.138 (8.884 ± 0.073; E88 on card 1 8.614 ± 0.175), R32 `r_walk` − `r_abs` 4.589 ± 2.040 (5.006 ± 0.205; E88 5.042 ± 0.193), W32 `ones` − `c_abs` 0.062 ± 0.425 (0.052 ± 0.226; E88 0.100 ± 0.311). Every tile, primary, with the dips arm's D beside it:

| tile | D (W), primary (dips-removed) | S (W) | rail, Drail (W) | pJ/op by S | pJ/MAC by S | ΔT in 2 s (°C) |
|---|---|---|---|---|---|---|
| `fp32.c_abs` | 8.437 ± 0.087 (8.433 ± 0.047) | 10.348 ± 0.379 | 7.110 ± 0.196 | 9230 ± 348 | 2.2535 ± 0.0849 | 1.35 ± 0.43 |
| `fp32.c_neg` | 8.452 ± 0.083 (8.446 ± 0.043) | 10.386 ± 0.155 | 7.086 ± 0.067 | 9265 ± 128 | 2.2619 ± 0.0313 | 1.25 ± 0.43 |
| `fp32.c_alt` | 13.513 ± 0.376 (13.493 ± 0.200) | 15.456 ± 0.512 | 11.270 ± 0.213 | 13789 ± 447 | 3.3665 ± 0.1092 | 2.00 ± 0.00 |
| `fp32.h_add` | 8.995 ± 0.155 (8.971 ± 0.100) | 10.889 ± 0.042 | 7.564 ± 0.134 | 9715 ± 40 | 2.3717 ± 0.0098 | 1.37 ± 0.80 |
| `fp32.h_sub` | 13.420 ± 0.288 (13.367 ± 0.204) | 15.301 ± 0.298 | 11.028 ± 0.430 | 13646 ± 273 | 3.3316 ± 0.0666 | 2.00 ± 0.00 |
| `fp32.h_allsub` | 9.035 ± 0.230 (9.020 ± 0.124) | 10.972 ± 0.207 | 7.453 ± 0.127 | 9791 ± 188 | 2.3905 ± 0.0459 | 1.42 ± 0.19 |
| `fp32.i_add` | 8.405 ± 1.419 (8.696 ± 0.125) | 10.251 ± 1.280 | 7.226 ± 0.034 | 9145 ± 1140 | 2.2326 ± 0.2784 | 1.12 ± 0.26 |
| `fp32.i_sub` | 10.899 ± 0.134 (10.865 ± 0.106) | 12.827 ± 0.092 | 9.157 ± 0.084 | 11440 ± 83 | 2.7930 ± 0.0203 | 1.83 ± 0.19 |
| `fp32.h_sub2` | 9.773 ± 0.209 (9.749 ± 0.120) | 11.647 ± 0.168 | 8.279 ± 0.107 | 10390 ± 150 | 2.5366 ± 0.0365 | 1.61 ± 0.09 |
| `fp32.h_sub4` | 10.860 ± 0.123 (10.818 ± 0.126) | 12.819 ± 0.063 | 9.108 ± 0.215 | 11431 ± 44 | 2.7908 ± 0.0108 | 1.85 ± 0.12 |
| `fp32.h_sub6` | 11.983 ± 0.476 (11.973 ± 0.249) | 14.006 ± 0.512 | 9.957 ± 0.252 | 12495 ± 460 | 3.0505 ± 0.1123 | 1.95 ± 0.12 |
| `fp32.s_abs` | 10.814 ± 0.471 (10.953 ± 0.157) | 12.865 ± 0.468 | 9.292 ± 0.271 | 11475 ± 416 | 2.8015 ± 0.1015 | 1.58 ± 1.27 |
| `fp32.k_only` | 8.531 ± 0.287 (8.503 ± 0.166) | 10.372 ± 0.259 | 7.087 ± 0.018 | 9253 ± 227 | 2.2591 ± 0.0555 | 1.23 ± 0.59 |
| `fp32.r_abs` | 17.323 ± 0.100 (17.317 ± 0.055) | 19.302 ± 0.235 | 14.126 ± 0.226 | 17220 ± 214 | 4.2040 ± 0.0522 | 2.40 ± 0.25 |
| `fp32.r_h_add` | 17.901 ± 0.453 (17.828 ± 0.308) | 19.793 ± 0.540 | 14.618 ± 0.451 | 17658 ± 487 | 4.3110 ± 0.1188 | 2.42 ± 0.26 |
| `fp32.r_h_sub` | 22.282 ± 0.311 (22.288 ± 0.174) | 24.271 ± 0.347 | 18.129 ± 0.535 | 21649 ± 298 | 5.2853 ± 0.0727 | 2.95 ± 0.22 |
| `fp32.w_c` | 12.424 ± 0.203 (12.441 ± 0.135) | 14.393 ± 0.431 | 10.267 ± 0.324 | 12845 ± 377 | 3.1359 ± 0.0921 | 2.00 ± 0.00 |
| `fp32.w_h_add` | 12.973 ± 0.166 (12.973 ± 0.089) | 14.852 ± 0.209 | 10.701 ± 0.340 | 13246 ± 165 | 3.2339 ± 0.0403 | 1.67 ± 1.43 |
| `fp32.w_h_sub` | 15.758 ± 0.209 (15.770 ± 0.128) | 17.680 ± 0.411 | 12.815 ± 0.211 | 15771 ± 379 | 3.8504 ± 0.0926 | 2.05 ± 0.12 |
| `fp32.r_walk` | 21.912 ± 1.995 (22.323 ± 0.194) | 23.862 ± 2.093 | 18.043 ± 0.500 | 21289 ± 1859 | 5.1974 ± 0.4538 | 2.87 ± 0.07 |
| `fp32.wr_h_add` | 23.534 ± 0.066 (23.512 ± 0.043) | 25.555 ± 0.099 | 18.990 ± 0.742 | 22799 ± 108 | 5.5661 ± 0.0263 | 3.13 ± 0.14 |
| `fp32.wr_h_sub` | 23.941 ± 3.127 (24.618 ± 0.169) | 25.883 ± 2.772 | 19.582 ± 0.918 | 23089 ± 2454 | 5.6370 ± 0.5990 | 3.20 ± 0.22 |
| `fp32.signs` | 13.350 ± 0.781 (13.502 ± 0.053) | 15.295 ± 0.588 | 11.082 ± 0.421 | 13641 ± 537 | 3.3304 ± 0.1311 | 1.90 ± 0.43 |
| `fp16.c_abs` † | 7.951 ± 1.135 (8.443 ± 0.182) | 9.820 ± 1.373 | 7.020 ± 0.280 | 8758 ± 1219 | 1.0691 ± 0.1488 | 1.05 ± 0.22 |
| `fp16.c_alt` | 15.716 ± 0.514 (15.701 ± 0.268) | 17.663 ± 0.519 | 12.926 ± 0.333 | 15758 ± 472 | 1.9235 ± 0.0577 | 2.08 ± 0.64 |
| `fp16.h_add` | 8.905 ± 0.165 (8.925 ± 0.118) | 10.958 ± 0.257 | 7.473 ± 0.166 | 9771 ± 235 | 1.1928 ± 0.0287 | 1.20 ± 0.43 |
| `fp16.h_sub` | 15.761 ± 0.391 (15.737 ± 0.208) | 17.716 ± 0.182 | 12.848 ± 0.209 | 15806 ± 171 | 1.9295 ± 0.0209 | 2.05 ± 0.12 |
| `fp16.h_allsub` | 9.091 ± 0.226 (9.072 ± 0.123) | 10.979 ± 0.189 | 7.641 ± 0.080 | 9795 ± 165 | 1.1956 ± 0.0201 | 1.45 ± 0.25 |
| `fp16.hh_sub` | 14.822 ± 0.518 (14.846 ± 0.292) | 16.734 ± 0.612 | 12.258 ± 0.409 | 14927 ± 552 | 1.8222 ± 0.0673 | 2.00 ± 0.25 |
| `fp16.hl_sub` | 13.779 ± 0.453 (13.944 ± 0.269) | 15.744 ± 0.547 | 11.391 ± 0.180 | 14045 ± 492 | 1.7144 ± 0.0601 | 2.00 ± 0.00 |
| `fp16.s_abs` | 13.023 ± 0.219 (13.030 ± 0.126) | 14.995 ± 0.068 | 10.833 ± 0.364 | 13374 ± 63 | 1.6326 ± 0.0076 | 2.00 ± 0.00 |
| `fp16.signs` | 13.294 ± 0.448 (13.421 ± 0.100) | 15.221 ± 0.679 | 11.089 ± 0.010 | 13576 ± 597 | 1.6572 ± 0.0728 | 1.98 ± 0.07 |
| `fp32.ones` | 8.498 ± 0.348 (8.486 ± 0.184) | 10.341 ± 0.419 | 7.063 ± 0.174 | 9226 ± 364 | 2.2524 ± 0.0890 | 1.13 ± 0.57 |
| `fp16.ones` | 8.468 ± 0.027 (8.456 ± 0.022) | 10.427 ± 0.101 | 7.026 ± 0.271 | 9300 ± 83 | 1.1352 ± 0.0102 | 1.47 ± 0.14 |
| `fp32.randn` | 24.950 ± 0.011 (24.923 ± 0.042) | 26.962 ± 0.081 | 19.818 ± 0.181 | 24052 ± 59 | 5.8721 ± 0.0144 | 3.16 ± 0.28 |
| `fp16.randn` | 22.269 ± 0.585 (22.332 ± 0.117) | 24.244 ± 0.445 | 18.030 ± 0.216 | 21636 ± 404 | 2.6411 ± 0.0493 | 2.88 ± 0.06 |
| `int8.full` | 7.130 ± 0.170 (7.148 ± 0.110) | 9.736 ± 0.116 | 6.011 ± 0.090 | 5056 ± 60 | 0.3086 ± 0.0037 | 0.99 ± 0.06 |
| `anchor_pi` | 8.509 ± 0.097 (8.514 ± 0.083) | 10.444 ± 0.102 | 7.185 ± 0.197 | 9316 ± 90 | 2.2744 ± 0.0219 | 1.01 ± 0.25 |
| `fp32.zeros` | 0.000 ± 0.000 (0.000 ± 0.000) | 1.988 ± 0.044 | 0.000 ± 0.000 | 1773 ± 40 | 0.4329 ± 0.0097 | -0.03 ± 0.22 |
| `fp16.zeros` | 0.000 ± 0.000 (0.000 ± 0.000) | 1.997 ± 0.219 | 0.000 ± 0.000 | 1782 ± 195 | 0.2175 ± 0.0238 | -0.02 ± 0.29 |
| `int8.zeros` | 0.000 ± 0.000 (0.000 ± 0.000) | 2.594 ± 0.071 | 0.000 ± 0.000 | 1347 ± 37 | 0.0822 ± 0.0022 | 0.59 ± 0.10 |

† Two of the three kept passes carry dips in this tile's window (C1, C13); every fp16 contrast over `c_abs` moves 0.3–0.5 W between the arms. ΔT is the whole-degree reading, so ±0.00 is identical readings, not a precision.

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
sensitivity arm, and it moves no primary verdict. R2 as a rule is INCONCLUSIVE in the primary and in all three leakage arms; its core contrast, `h_sub` − `h_add`, is CONFIRMED in fp32 and fp16 in every arm.

**The dips.** The board meter's launch-gap dips were unusually frequent: 39 in four passes, 22 in power windows (E90: 19 in three, 4), 4.04–23.89 W below their neighbours (up to 21.52 W in a power window), all 31 in runs within 148 ms after a launch boundary
(`dips-arm/dips.json`; `posthoc-check.txt` F; `corrections-check.txt` C12). They set pass 9211 aside and widen the primary's intervals, and they move some of its means: every fp16 contrast over `c_abs` by 0.3–0.5 W (`fp16.c_abs` itself 7.951 → 8.443 W), `wr_h_sub` − `wr_h_add` 0.407 → 1.106 W, `r_walk` − `r_abs` 4.589 → 5.006 W, `wr_h_add` − `r_walk` 1.622 → 1.188 W, `i_sub` − `i_add` 2.494 → 2.169 W. The rail shows none of it. A cruder reading agrees, with no reduction at all: the median board power in each run's window, all four passes, no gate and no correction, gives `h_sub` − `h_add` +4.66 ± 0.60 W (fp32) and +6.70 ± 0.24 W (fp16), `wr_h_sub` − `wr_h_add` +1.06 ± 0.10 W, `h_allsub` − `h_add` +0.05 ± 0.12 W ([`crude-check.txt`](crude-check.txt), labelled post hoc).
**Checks:** leakage slope 0.1396 W/°C over 194 runs (E90: 0.2203); idle consistency median |S − S0 − D| 0.085 W; carry-over 0.0003 ± 0.0023 W/W; rail lag 1.0 s; duty 0.9958–0.9966;
cycles per op 546.001 / 546.001 / 318.0; every dumped tile equal to its registered sha256; the tie's drift 0.24–0.43 W a pass; 600 MHz, 521.6 mV throughout.

**Departures and disclosures.** None from E92.md's protocol. (1) The collection ran over a copy of the raw passes inside the repo's ignored `build/` tree, as E86 and E90 did. (2) No interim look at power:
the waits read only the queue log. The collection script was exercised on the self-test's synthetic passes first. (3) `posthoc_fit_e92.py` was written during the run, before any pass was read, and first run
on synthetic E92 values with E78's and E90's measured ones; its held-out test on E86's tiles and `posthoc-check.py` were written after the data. Neither is a registered test, and no rule depends on them. (4) The
registered budget expected ~43 card-min and 10 min a pass; it took 39 and 9. (5) The runner's log lines read "E78 pass … tiles verified against kinds.json": `run_e78.py`'s unchanged strings, as in E90.
(6) `code.sha256` was refreshed after the collection for one file, `posthoc_fit_e92.py`, edited after it ran. (7) The comparison with Q132(b)'s bench is post hoc on my side; the bench's prediction is its lane's, frozen before these passes were read, and E92 was not designed to test it.
(8) E92.md's one-line description of the dips-removed arm ("board-reading samples 5–20 W low just after a launch boundary") is not its registered code's rule (`posthoc_dips_e92.py`: `board_w[i] < min(board_w[i−2], board_w[i+2]) − 4.0 W`, any depth, anywhere; E86's logic unchanged). E92.md stays frozen, and no number moves: the raw medians agree.

## Interpretation (labelled: a reading of the public RTL, not measured)

The fused multiply-add's effective operation is `eff_sub1 = sign(P) ^ sign(C)` (`external/core-et/rtl/shire/minion/vpu/txfma_7s/txfma_c2.v:144`, `:161`). On an effective subtract, **all 52 bits of the
aligned operand are inverted** into the carry-save adder (`txfma_c2.v:303`, `:364`; `txfma_f3.v:384-421`), whose sum and carry are flopped (`:120-121`) and fed to a 52-bit adder, a leading-digit anticipator and a
trailing-zero counter (`txfma_f4.v:61-119`). A product shifted out of range is zapped to 0, so the bus is all 0s when adding and all 1s when subtracting, whatever the product is. When the operation holds, none of it
moves; when it flips, all of it does. That is what the measurements show in fp32 with the result frozen: nothing for a steady subtract, about 1,100 fJ a flip, no dependence on an absorbed product's magnitude; and a price that falls as
moving sums and random mantissas already move those nets. A count of the reading's adder bits, with one price calibrated on one datum from another card, predicted fp32's 15 contrasts to 0.28 W rms before the data, and those contrasts share counts, so they are fewer than 15 independent tests.
**E92 itself does not identify the gates**: the count is a reading, the card's C was not read back here (the host skips its check for file tiles, E88 C8; [E104](../2026-11-01-e104-c-readback/README.md) added the read), and any net that moves with `eff_sub` is inside γ. fp16's extra cost over fp32 on these tiles goes with the two halves parting ([E104](../2026-11-01-e104-c-readback/README.md)). The stage comes from the RTL bench's net counts (`de545f0c`), a simulation: the adder and normaliser take 89% of the net toggles of fp32's alternation and 60% of fp16's, in a bench 27% low on fp32's contrast and 6% low on fp16's (result 8). The moving-sum part is E88's stream count of the C read and the result bus swinging between accumulators that have drifted apart (R32s, R32bus), not split further here.

## What it changes

- **The kinds page's item 2 narrows, and [E104](../2026-11-01-e104-c-readback/README.md) narrows it further.** The alternation guess is answered on silicon with the sum frozen in fp32: with the operands fixed, the sum's sign alone moves 4.4–5.1 W, and a steady subtract moves nothing measurable. In fp16 the same change moves 6.9–7.8 W, of which about 3 W goes with the sums parting (C14). **R2 is INCONCLUSIVE at the registered level, because one contrast of four runs above its band; the core contrast is CONFIRMED in fp32 and fp16 in every arm, on watts; its fp16 leg did not test a frozen sum.** The split is an estimate: no same-operands pair exists in the ±1 regime itself, and its largest fp32 piece is a residual.
  The RTL bench, frozen before any pass was read, places the alternation in the adder and normaliser. [E104](../2026-11-01-e104-c-readback/README.md) ran the fp16 moving pair (R6 INCONCLUSIVE), and its count of the result bits answers the 5.8 against 30 fJ. Left open: the bench's quarter-low price on fp32's alternation; the moving-sum part's split; an always-subtracting tile with moving sums.
- **"Power is paid for operand bits that change" needs one more clause, in fp32 at these points.** With the sum frozen, or at magnitude 1 with moving sums, a sign flip that leaves the adder's operation alone costs about what E65 priced (`h_add`, `w_h_add` − `w_c`, `r_h_add` − `r_abs`: 0.55–0.58 W against 0.563 W; `wr_h_add` − `r_walk` runs 2× that, result 10), and one that flips the operation costs several times more (2–9×, result 2).
- **E90's fp16 and fp32 steps.** With the sum frozen, about half of fp32's step remains. fp16's 92% is withdrawn (C15): in a sum that truly holds, about 45% remains ([E104](../2026-11-01-e104-c-readback/README.md)). E90's reading that most of a sign's cost is not in the operand bits stands in both formats. The two formats' equal steps split similarly, not shown equal ([E104](../2026-11-01-e104-c-readback/README.md), result 5).
- **The kinds page's item 6 gains a lead, no more:** one more feature, the adder bits, cuts the four-price model's in-sample error 3.7–4.5× over every fp32 and fp16 tile on this card, and its out-of-family error 1.7–1.9×, with a price that does not transfer between families (post hoc).

## Caveats

Three passes in the primary (t = 4.30), four in the dips arm (t = 3.18), one card, one clock. All tiles are designed: C sits at ±(n+1)·2^100 or a small integer, not where a real tensor's lands, and 1 µop in 16 (k = 0) moves the sum even in the frozen
designs. Frozen against walking rested on the desk emulation (`make_e92.py --check`, 32 of 32), and in fp16 that emulation was wrong: it rounds to nearest, over four ops, where fp16 truncates each aligned product (`make_e88.py:408`; C14). [E104](../2026-11-01-e104-c-readback/README.md) read C back. The split in result 6 subtracts a frozen design from a walking one with different draws in fp32 (E88's `s_abs`
beside E90's `signs`), and it assumes the frozen cost carries over to a moving sum, which result 4 says it only partly does; hence two readings, and they are not an interval. fp16's bits price is a bound. The adder-bit count is a reading at the flop level, not a gate-level count. The post-hoc fit's
rms is in-sample and its leave-one-out rms in-family. A steady subtract was tested only with an absorbed, zapped product. `fp16.c_abs`'s primary values carry dips (C13). The watts are the board's; the rail figures are about 0.8 of them.

## Files

`e92.json` (the registered reduction: every item, per pass), `runs.csv`, `reduce.txt`, the leakage arms (`e92-leak0.1994 / 0.3803 / 0 .json`, `.csv`, `.txt`), `scored.json` and `results.md` (every rule, the factorial, the budget, the ladder), `dips-arm/` (the registered dips-removed arm:
`dips.json`, `e92-nodips.json`, `scored-nodips.json`, `results-nodips.md`), `code.sha256`, `logs/` (the queue and dry-run logs, the session's start and end config reads, the binaries' sha256), `aifoundry3/kinds/` (the four passes' raw data and the smoke, `kinds-smoke-p9201`),
`corrections-check.py` / `.txt` (the desk check behind the corrections: every number they cite, from committed files, standard library only), `bench-prediction-de545f0c.json` (Q132(b)'s frozen prediction, byte for byte as of that commit), `posthoc-check.py` / `.txt` (labelled post hoc: every number above beyond `scored.json`, from committed files, standard library only), `crude-check.py` / `.txt` (labelled post hoc: raw medians), `posthoc-fit.json` / `.txt` / `posthoc-fit-nodips.txt` (labelled post hoc). The read-back and the numbers in C14–C24 are in [E104](../2026-11-01-e104-c-readback/README.md)'s directory: `scored.json`, `posthoc-check.txt`. The tiles and the registration are in `tools/claims-v3/kinds/` (`E92.md`, `e92/`,
`predictions-e92.json`, `make_e92.py`, `make_predictions_e92.py`, `e92_common.py`, `run_e92.py`, `reduce_e92.py`, `score_e92.py`, `posthoc_dips_e92.py`, `posthoc_fit_e92.py`, `block_e92.sh`, `queue_e92.sh`, `run_e92.sh`, `collect_e92.sh`, `selftest_e92.py`).

## Corrections after verification (Sun 1 Nov 2026)

An independent verifier checked E92 after the data commit. It rebuilt every number from the raw telemetry with its own code and got the same values to three decimals and the same verdict on every rule, and it found the registration, the harness, the scoring, the tile designs and the public text sound. It found two major and eleven minor faults in what the prose builds on them. I checked each against the data, and none is rejected.
Each is corrected above, in place, at the desk: no card was touched, nothing was re-run, and no frozen or data file changed (`e92*.json`, `runs*.csv`, `reduce*`, `scored.json`, `results.md`, `dips-arm/`, the raw passes, `E92.md`, `predictions-e92.json`, `e92/`). The registered verdicts stand: primary 3 CONFIRMED, 7 INCONCLUSIVE, 0 REFUTED; dips-removed arm 7, 3, 0; S1 PASS. [`corrections-check.py`](corrections-check.py) prints every number below from committed files, and [`corrections-check.txt`](corrections-check.txt) is its output, under the section named.

| # | what was wrong | what changed |
|---|---|---|
| C1 (major) | **"E90's equal 5 W steps … are not one mechanism's price … 92–105% of fp16's", and "two different splits", in What it changes and the blog line "fp16 pays the same 5 W for a different reason".** The 105% is a dip artefact: `fp16.c_abs` D per kept pass 7.627, 8.473, 7.752, dips removed 8.582, 8.415, 8.468, 8.307, and it moves every fp16 contrast over `c_abs` by 0.3–0.5 W (frozen 5.073 → 4.587, moving part −0.246 → +0.378, `h_sub` − `c_abs` 7.810 → 7.294, γ 7.218 → 6.962), while the README said the dips "do not move its means by much except where noted". A frozen share is not a mechanism's share, and no fp16 moving pair ran | Struck. Result 6 states the share in each arm: 0.924 ± 0.019 dips arm, 1.052 ± 0.285 primary and high because of `fp16.c_abs`'s dips, raw medians 0.933; fp32 about half. It adds that fp16's moving part is 5.8 fJ per result bit against fp32's 30.0, unexplained, and the verifier's arithmetic (5.02 W with fp32's two prices), which proves nothing about fp16. Left open: an fp16 moving pair. The dips paragraph lists the means that move |
| C2 (major) | **"The kinds page's item 2 closes", "confirmed on silicon", "E88's named guess is right".** R2 is INCONCLUSIVE in the primary and in all three leakage arms: `fp16.c_alt` − `c_abs` 7.766 ± 1.583, high end 9.35 W against 8.05 W. The prose never said so where it drew the conclusion. And the other half of item 2, where the cost goes, is an estimate | **Item 2 narrows.** The alternation guess is answered on silicon with the sum frozen; R2 is INCONCLUSIVE at the registered level because one contrast of four runs above its band; the core contrast is CONFIRMED in fp32 and fp16 in every arm, lowest lower bound 3.98 W against a refutation line of 0.93 W; the split is an estimate. The integration step should not move item 2 to closed |
| C3 | **The fp32 split was stated as a result.** Only `signs` − `ones` (4.851 ± 1.128; 5.016 ± 0.219) and `s_abs` − `c_abs` (2.377 ± 0.556; 2.520 ± 0.171) are measured | "In plain words" and result 6 say "estimated by subtraction", name what is measured and what is modelled, give the two assumptions behind 1.4–2.0 W, call 2.5–3.0 W a residual, cite `w_c` − `c_abs` (3.987 ± 0.171 W, no alternation, 29.7 fJ per result bit after the adder bits; the moving part 29.7–30.0 fJ) and say that price leaves 0.35–0.50 W unaccounted |
| C4 | **"The alternation's price follows the adder's flops, across every regime".** The fJ column ignored the model's e88 part; with it the first three rows agree better (7.69, 7.62, 7.67 fJ) and the regime nearest real data does not (9.42 ± 1.04 fJ in the dips arm, 5.41 ± 18.25 in the primary). Its "6.3" was the dips arm's alone. "Excludes 2.57 W" left out that [0.925, 1.287] also excludes the registered 0.652 W. The two frozen rows share one count. `csa_in3`, 199,680 of `h_sub`'s 560,624 bits, is combinational (`txfma_f3.v:430`), and 7 fJ per bit is about 26 fF at 0.52 V: not a flop's price | Result 4's heading, column and text. The model misses the fourth regime by 0.45 W, 1.7×. Three tests, not four. "Adder bits" in the prose; `e88+flops`, `posthoc-check.py` and the frozen files keep their names. With the card scale taken off first the column reads 7.4–7.5 fJ and 9.2 fJ |
| C5 | **The refit's 1.30 / 1.79 → 0.29 / 0.49 W is in-sample, and the README never said so**; 3.7–4.5× was quoted with no out-of-family caveat, and the alternation variant in `posthoc-fit.txt` was not mentioned | Result 8 and What it changes say in-sample. Out of family: fitted on the tiles E92 did not design, it predicts E92's designs at 1.428 W (fp32; four prices 2.370) and 2.743 W (fp16; 5.114), at 12.5 against 7.3 fJ per adder bit and 5.4 against 11.9 fJ, opposite directions; it puts `h_sub` − `h_add` at +7.72 W (measured +4.43) and +2.94 W (measured +6.86); fp16's result-bit price swings 5.6 → 32.9 fJ. The alternation variant is disclosed: out of family 0.849 W (fp32) and 3.343 W (fp16); on E86's tiles 0.139 and 0.713 W |
| C6 | **"fp16 pays 1.5× fp32 per alternation, and the RTL bench saw it coming."** The frozen bench says 2.00× (6.44 / 3.22). The measured per-pass ratio is 1.552 ± 0.250 (1.552 ± 0.131): 2.00 is outside both | "The RTL bench saw the direction and the two aligned products' overlap; it said 2.0×." It is also 27% low on fp32's contrast |
| C7 | **`posthoc-check.py` no longer ran at HEAD, and the bench link no longer showed the frozen file.** `e7cb1f21` (01:10:16 PDT) rewrote `e92-bench-prediction.json` after this README: the stage field is gone, and a post-hoc variant sits on top. Its `nets_hier2` predictions are unchanged | `bench-prediction-de545f0c.json` here is that commit's file, byte for byte, and `posthoc-check.py` reads it. Rerun: the output differs from the committed one only in section K's header line. The README links the blob at `de545f0c` |
| C8 | **"About 1,100 fJ a time, 9× a sign bit's own flip" holds only with the result frozen, and the 122 fJ is not one bit's.** Per alternation: 1,028 fJ frozen, 647 (650) fJ with moving sums, 257 fJ (dips arm) on random magnitudes, so 2–9×. The 122 fJ moves B, product, C-read and result signs together; B and product alone (α) are 51 fJ | "With the result frozen" and "all four sign paths moving", in "In plain words", result 2 and the interpretation |
| C9 | **The sensitivity arm stood in, in prose.** Result 3's heading "half at half the rate" with R4 INCONCLUSIVE in the primary; the fourth regime's only bold was the dips arm's; "6.3–7.2 fJ each in every regime" in the lane's result dropped the arm | Heading reworded, with the rail per pass (1.890, 1.965, 1.937 W); the bold removed from result 4's table; arms named wherever the dips arm carries a statement |
| C10 | **Blog-facing wording.** "The chip draws" (it is the board on one card, in designed tiles; rail 3.46 and 5.38 W). "No operand and no product sign moving at all" (the k = 0 row flips 256 B and product signs an op, and the 5.1 W includes β, 0.33 W). "It is the change that costs, not the subtraction" (tested only with an absorbed product, no moving-sum always-subtract tile; fp16's R3 is INCONCLUSIVE in the primary by 0.005 W). "Says why" (a reading). "Frozen before the measurement" (frozen 00:43:14 PDT, when 9210 and 9211 had finished and 9212 was running: "before any pass was read"), and 89% is a share of net toggles in a bench 27% low on that contrast | "In plain words", result 1 and the interpretation reworded. The lane's blog sentences are rewritten inside the verifier's may and may-not lists |
| C11 | **Registered reported items were missing from the README, one against its claim.** E92.md asks for `r_h_add` − `r_abs`, `wr_h_add` − `r_walk`, `w_h_add` − `w_c` against E65's 0.563 W, E88's M32, R32 and W32 on this card, every tile's numbers, and γ at `signs`' rate. `wr_h_add` − `r_walk`, 2× E65, contradicted "A sign bit costs what a sign bit costs … unless it flips the adder's operation", and `i_add` − `c_abs` contradicted "at the sign bits' own price" | Result 10 reports them all, with a table of every tile; result 6 adds γ at ±1's rate and what is left of frozen. The two sentences are restricted to what was measured |
| C12 | **The dips arm's description differs from its code, and "up to 21.5 W deep" was the deepest in a power window.** `E92.md:189` says "samples 5–20 W low just after a launch boundary"; `posthoc_dips_e92.py` removes anything more than 4.0 W below both ±2-sample neighbours, any depth, anywhere. The 39 dips run 4.04–23.89 W deep; the −21.5 W pair moves `wr_h_sub` − `wr_h_add` from 0.407 to 1.106 W | Disclosure (8) under Departures, and the dips paragraph. `E92.md` stays frozen. The raw median agrees (1.064 ± 0.103 W), so no number moves |
| C13 | **A carried dip in the tables.** `fp16.c_abs` is D 7.951 ± 1.135 W, 1.0691 pJ/MAC in the primary, against 8.443 ± 0.182 W, 1.1232 pJ/MAC in the dips arm | They are the registered primary, so they stay, marked in result 10's table. **For integration:** a kinds-table cell for `fp16.c_abs` carries this note |

## Corrections after E104 (Sun 1 Nov 2026)

Lane `a1c1-e102-bits` found a fault in `make_e88.simulate` and `make_e92.sign_counts` ([E102's README, § A fault in two lab tools](../2026-11-01-e102-balanced-bit-prices/README.md#a-fault-in-two-lab-tools-make_e88-and-make_e92-start-an-op-from-c--fln1-s)), E102's verifier reproduced and sharpened it, and [E104](../2026-11-01-e104-c-readback/README.md) tested it on silicon (aifoundry1 card 1, 600 MHz, registered `b8d24835`). The accumulators were read back: 110 of 110 reads, all 1,024 minions, equal the RTL's arithmetic word for word. These corrections are made in place above and at the desk: no E92 pass was re-run, and no frozen or data file changed (`e92*.json`, `runs*.csv`, `reduce*`, `scored.json`, `results.md`, `dips-arm/`, the raw passes, `E92.md`, `predictions-e92.json`, `e92/`, the checks of C1–C13).

**What stands.** No registered verdict label changes: every rule is on watts, and the watts stand (`h_sub` − `h_add` on card 1 is 6.713 ± 0.219 W against E92's 6.812 W × 0.9722, E104-R8 PASS). **All of fp32 stands**: `fp32.c_abs`, `h_add`, `h_sub`, `c_alt`, `h_allsub`, `s_abs`, `r_abs` read back as held, word for word. **R10 stands and reads cleaner**: `hh_sub` − `hl_sub` shares one walk, read back as the same words, so the walk cancels. `h_add` − `c_abs` stands: fp16's `c_abs` and `h_add` hold.

| # | what was wrong | what changed |
|---|---|---|
| C14 | **"With the sum frozen" for fp16.** `h_sub`, `c_alt`, `hh_sub`, `hl_sub`, `s_abs` and `h_allsub` are not frozen. fp16 truncates each aligned term separately (`vpu_tensorfma.v:692-693`, `txfma_c2.v:309-310`, `txfma_f4.v:82-85`), so an absorbed product that subtracts takes one unit off the sum. `h_sub`'s C[0][8] reads 4f7fffe9 at n = 2 where E92 said 4f800000, and its halves are 12% apart by op 199,874 (E104-R1, RTL). Root cause: `make_e92.self_check` "proved" them frozen with `make_e88.emulate_launch`, which rounds to nearest (`make_e88.py:408`), over four ops | "In plain words", results 1, 2, 3, 5 and 6, the interpretation, What it changes and Caveats. **Of the 6.7 W, 3.16 ± 0.51 W goes with the two halves parting** (E104-R4, RESULT-PATH in every arm; M4 3.27 W; where, only as the bench's reading: 38.6% adder and normaliser, 31.3% the FMA's other blocks, 27.6% VPU lane, bypass and register file) **and 3.55 ± 0.29 W with the adder alternating and the halves together, at 0.904 of the alternations** (M4 3.72 W). At `h_sub`'s own alternations, about 2.8–2.9 W and 3.8–3.9 W |
| C15 | **"About 92% remains frozen."** `s_abs` read back as 9 words, not one. 0.924 is a ratio of two moving-sum tiles | Struck. In a sum that truly holds, `z_s` − `c_abs` is 2.153 ± 0.330 W, about 45% of the step carried to card 1 (post hoc, an estimate across two cards: zero products, A's signs still, so a floor; fp32's twin 1.728 ± 0.827 W, about 35%, and its absorbed `s_abs` about 50%). The formats are similar, not shown equal |
| C16 | **"fp16 pays 1.55× fp32 per alternation."** The per-alternation reading is gone; 1.552 ± 0.250 stays as the ratio of two contrasts' watts on tiles whose fp16 sums part | With the halves together on absorbed products: 0.947 ± 0.297 (E104-R5, 1.55x GOES; INCONCLUSIVE in the dips-kept and 0.545 arms). Per lane alternation over `h_add`: 965 ± 381 fJ in fp32, 913 ± 74 fJ in fp16. **That does not conflict with "about 1,100 fJ" above:** E92's 1,099 is γ, with the C-sign term added back; add β and the B flips `u_sub` lacks and they read 1,056 and 979 fJ, against E92's γ × 0.9722 = 1,062. On sums moving alike: 1.562 ± 2.734 (R6 INCONCLUSIVE), centred near 1.55. Result 5's title and its bold sentence are rewritten |
| C17 | **"fp16's moving part is 5.8 fJ per result bit against fp32's 30.0, and that gap is unexplained", and "e88+flops: fp16's alternation, at half".** The bits were miscounted: the emulation's C has no parted halves, so `s_abs`'s 748 result bits are in truth about 70,000–79,000, and the +1.77 W non-additivity comes from the same counts | Withdrawn: on the sums the card holds, `signs` − `s_abs` is about −16,000 bits, not +58,544, so there was no such difference to price. As a lump, `h_sub` − `u_sub` less fp32's same contrast is 2.910 ± 0.552 W over 91,208 bits, about 28 fJ per result bit (post hoc). It is not the 29.7 fJ, which takes 7 fJ per adder bit off first; raw, that contrast is 36.0 fJ. `w_h_add` − `h_add`, the same bits in both formats, the adder always adding: fp16 4.036 ± 3.302 W, fp32 3.677 ± 0.695 W: alike, not shown the same |
| C18 | **The post-hoc fp16 prices.** 5.5, 10.8 fJ and "not identified" rest on those counts. E102's verifier (F1) adds a warning that binds here: the improvement on refitting from real sums is not evidence for the walk, because leaving the five tiles out does the same | Withdrawn in result 8. The fp32 fit stands. The evidence for the walk is the read-back |
| C19 | **The rules' premises.** R2's and R3's fp16 legs and R6's fp16 leg did not test a frozen sum. Their labels stand, on watts | Said in "What it changes" and here. R2's fp32 legs did test it |
| C20 | **"Registered predictions" for fp16.** `sign_counts` and `simulate` start from fl((n−1) S), so the fp16 rows of `predictions-e92.json` and `e92.json` › `sign` count the wrong sums | The files stay frozen. Read those rows as what the frozen reading predicted |
| C21 | **"An fp16 moving pair would settle…"** | Run in E104: `m_h_sub` − `w_h_add` 3.271 ± 1.961 W (3.253 ± 0.392 with all three passes); fp32 2.121 ± 2.457 W (2.099 ± 0.489) |
| C22 | **The manual.** ET Programmer's Reference Manual §9.3.3 says the three values are added with no intermediate rounding and the final sum rounds toward zero. E92 did not cite it | On silicon that sentence fails for `hh_sub`, `hl_sub`, `s_abs` and E88's `r_abs`, `r_walk` (E104-R1, R3): each aligned product truncates separately |
| C23 | **E88's `fp16.r_abs`.** E88's "below half an ulp" and its result 6, "two ways of freezing agree … cancellation stops about as much of the result path as absorption", fail on the card: `r_abs` walks one unit a micro-op in one word, 4f7fffe9 at n = 2, while `r_cancel` holds 0 (E104-R3). **What its numbers keep:** A16 = 0.388 ± 0.111 W and H6 PASS stand as numbers, E88's fit stands, and §5.3's fp16 row, frozen by cancellation, stands. A16 is about the size of that walk, a size match, not a finding: `r_abs` writes about 8,000 more store bits an op than `r_cancel`, 0.28–0.49 W at 30–52 fJ (`posthoc-check.txt` J). At E88's price R16abs's model falls from 7.23 to about 6.77 W against 5.90 ± 0.14 W (E102's verifier) | A dated note in E88's README, result 6, and here |
| C24 | **"C was not read back".** True when written | Now read: `aifoundry1-c1/kinds/readback-p10402/` in E104's directory |

*C14–C17 and C23 were reworded the same morning after [E104](../2026-11-01-e104-c-readback/README.md)'s own verifier (its C1, C3, C4, C8, C12): no number or verdict changed.*

**For integration.** The kinds page's §5.3 and §5.4 and item 2: see E104's README, "What the page may now say". The blog sentences of E92's lane on "sum frozen" and "92%" for fp16, and "1.55× per alternation", are not to be used.
