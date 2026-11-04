# E152: the float B-lane gate's price per flip as a dose ladder — at 1, 2 and 4 lanes the points sit 1.2–2.5% of full scale off a straight line, but their 95% intervals reach 10.4% and 10.0% at two and four lanes, so linearity within 10% reads INCONCLUSIVE as registered; E127's price reads 0.96 of itself, INCONCLUSIVE; post hoc, on Q139(u)'s footing, LINEAR and CARRIES (aifoundry3 card 0, 600 MHz)

*On the kinds page, [section 11, what is still open](https://spacesheep.dev/@yaroslavvb/horace-kinds-of-numbers#11-what-is-still-open):
**item 6**, "A power model across kinds", its tail: the gate's price per flip and its linearity (the list as live at `8ec9ead107aa`).
It answers **Q138's final critic's open rank 12** ("Physical readings of M7's constants and the gate's price ... a registered dose
ladder of gate flips per op at fixed data (1, 2, 4 and 8 lanes switching) with the price frozen from E127. Rule: linear within 10%.").
It builds on [E127](../2026-11-02-e127-b-gate/README.md), whose design, harness and price it uses.*

*Tue 3 Nov 2026 (week 45), Q139, lane `a3-e152-gate-dose`. **Pre-registered in `2a744f4d`** (committed 05:44:49 PST, on origin/main by
05:44:54), before the claim (05:47:03) and the first launch (the smoke, 05:47:33): [`tools/claims-v3/e152/README.md`](../../../../tools/claims-v3/e152/README.md),
frozen numbers in `predictions-e152.json` (sha256 `43f0ed7f…`), the scorer `score_e152.py`, self-test 24 of 24. aifoundry3 card 0 at
600 MHz in every sample, 521.8 mV mean; `ettelem config` (through E128's guard, under the card lock, `timeout 10`) read TDP 0 W, threshold
65 °C, max_power, 600 MHz, 522–523 mV at 18 of its 19 reads, never set (one read returned no line: § Departures). **Every
device-management command sent was a read** (nine kinds, two of them PMIC voltage-register reads, which the owner's rule of 2 November
2026 allows; § Device commands sent); no governor move, no reset, no `--reset-ms`. The day's one card post in #community-lab (message
1567153765390487573) was rewritten at 05:47:03 to add this card's clause and at 06:20:31 to drop it, every other clause kept. Card session
05:47:28–06:20:04 PST, **32.6 of the 40 card-minutes allowed**, six passes of six planned
([`logs/push-and-claim-times.txt`](logs/push-and-claim-times.txt)). **No amendments.***

*Corrected after verification (a dated note, Tue 3 Nov 2026, about 16:30–17:00 PST; desk only: no card, no device command, nothing
re-run, no Modal). E152's first verifier (an earlier attempt died at about 07:46 PST on a usage limit) re-ran the registered collector,
the footing arm and `posthoc_e152.py` in a clean export (every output byte-identical), re-scored every rule with its own scorer (the
same verdicts), decoded the tiles, traced every command sent to a read at `836a4ab`, and matched all 245 raw files to aifoundry3
(read-only). It found five faults in how the result was read, one major and four minor. None changes a measured number, a rule, a
frozen prediction or a registered verdict. Each is corrected in place, marked "corrected after verification, C*n*" (with the old
wording) or "added after verification, C*n*", and listed with the title's old wording in
[§ Corrections after verification](#corrections-after-verification-tue-3-nov-2026) at the end. The numbers they quote are printed by
[`corrections_e152.py`](corrections_e152.py) → [`corrections.txt`](corrections.txt) ([`corrections.json`](corrections.json)), from
committed files only, post hoc. **C1 (major):** the "3% of full scale" figures are point estimates. The 95% bounds reach 10.4% of full
scale, a part spent whenever any lane flips is excluded only above about 11% (9% on the footing), and a per-flip constant carrying to
other kernels is untested, not a consequence of linearity. **C2:** "M8 under-prices the gate by 7%" is a point estimate. As registered,
M8's price lies inside the ladder's interval, so no correction to M8 is resolved. **C3:** 185 of 186 planned runs ran: one anchor was
skipped by E78's launch gate. **C4:** two doses cross τ, not one. **C5:** Q139(u)'s footing was committed 84 minutes before this
registration, which did not register it; on it the session is still about twice as noisy as E127. The registration
([`tools/claims-v3/e152/`](../../../../tools/claims-v3/e152/README.md), `2a744f4d`) gains a dated note (C5) and is otherwise unedited;
`scored*.json`, `results*.md`, the reductions, `posthoc/`, `posthoc_e152.*` and the raw passes are unchanged.*

**In plain words.** E127 found that flipping the chip's float lane gates costs energy of its own, about 0.26 pJ every time one lane's
gate turns on or off, but it measured that at one dose only: all eight lanes switching every cycle. A power model that charges a fixed
price per flip is only right if the cost is the same per flip whether one lane switches or eight. E152 ran five doses, 0, 1, 2, 4 and
8 lanes switching, with everything else held fixed: every product zero, the operand wires moving the same 4,096 bits per operation,
every lane live half the time. **The cost rose in step with the number of lanes.** At one, two and four lanes it sat +0.03, +0.015 and
+0.025 W above the straight line through 0 and 8 lanes. Those are point estimates, 1.2–2.5% of the rule's 1.20 W full scale; their 95%
intervals run from 7.9% below the line to 10.4% above it, so the ladder is consistent with a straight line to about ±10% of full
scale, and is not resolved to 3%. Every
dose's price per flip agreed with one constant (306, 267, 265 and 254 fJ, all intervals overlapping) *(corrected after verification,
C1: this said "At one, two and four lanes it sat +0.03, +0.015 and +0.025 W above the straight line through 0 and 8 lanes, 1–3% of the
1.16 W full scale, and every dose's price per flip agreed")*. Registered, though, the test reads **INCONCLUSIVE**. The rule asked
that every dose's 95% interval stay within 10% of full scale, and two do not: the two-lane dose's reaches 10.4% (0.125 W against a
0.120 W line) and the four-lane dose's 10.0% (0.121 W) *(corrected after verification, C4: this named the two-lane dose alone)*.
This session was about three times noisier than E127's. About 60% of the variance above E127's comes from how the registered
reduction corrects for temperature (§ 4); on the lab's one footing the session is still about twice as noisy as E127 *(corrected
after verification, C5: this said "and the noise comes from how the reduction corrects for temperature")*. Read on that footing
(Q139(u), post hoc: the registration did not register it, though it was committed 84 minutes earlier, § Departures *(added after
verification, C5)*), the same rule reads LINEAR, and E127's price carries. **E127's price
itself** read 251.5 ± 21.9 fJ a flip here, 0.96 of the frozen 262.9 fJ. That is also INCONCLUSIVE against the registered ±10% band,
because the interval crosses its lower edge. The frozen expectation (R1 LINEAR, R2 CARRIES) was not met as registered.

## What this does to predicting power and heat

**The term tested: the gate's per-flip price**, M7's and M8's `gtr` form, a constant per gate flip, and whether it is linear in flips
(the critic's rank 12: "it decides whether the constants extrapolate to other clocks, cards and kernels").

- **Out of sample**, on doses no model or price was fitted on, a price frozen from E127's single dose reads the ladder's four dose
  contrasts to **0.024 W rms (2.1% of full scale)** on the registered reading and 0.014 W (1.1%) on Q139(u)'s footing. M8's frozen
  per-flip price at E127's pair (235.3 fJ, which assumes its bench terms scale with the flips) reads them to 0.061 W (5.2%), low at
  every dose; but the four contrasts share one reference, D(`gd0`), so that is not four independent readings *(added after
  verification, C2)*. M7's (240.9 fJ) reads them to 0.047 W (4.1%). M8's `gtr` term alone (140.7 fJ) reads them to 0.31 W (27%), at
  about half the measured cost. **As registered, both the 0.024 and the 0.061 W lie inside the contrasts' 95% half-widths (0.078–0.149
  W), so this reading does not separate E127's price from M8's; what it resolves is that `gtr` alone is far too low** *(added after
  verification, C2)*. So the price per flip is **consistent with one constant within about ±10% of full scale**: the point departures
  are 1.2–2.5%, their 95% bounds up to 10.4%, and a part spent whenever any lane flips is excluded only above about 11% of full scale
  (9% on the footing) *(corrected after verification, C1: this said "one constant to within the measurement (no shared part larger than
  about 3% of full scale)")*. The ladder's price is 1.07 × M8's whole price as a point estimate (1.10 × on the footing) and 1.8 × its
  `gtr`. M8's 235.3 fJ lies inside the ladder's registered interval [229.6, 273.5] fJ, so **no correction to M8 is resolved as
  registered**. On the footing, which is M8's own basis, the interval [239.1, 279.3] excludes it by 3.8 fJ, and M8's 0.071 W rms there
  just exceeds that reading's smallest half-width (0.065 W), both post hoc *(corrected after verification, C2: this said "M8 under-prices
  the gate by about 7%, 0.09 W at full scale")* ([`posthoc_e152.txt`](posthoc_e152.txt) § 3; [`corrections.txt`](corrections.txt) C1,
  C2).
- **For M7's and M8's gate constants:** *if* the cost is linear in flips (supported here to about ±10% of full scale, in one quiet
  regime, on one card and clock), a constant per flip is the right form, and within that a kernel whose zeros switch one lane at a time
  pays per flip what one that switches all eight pays. Whether the constant carries to other kernels is not tested: linearity is
  necessary for that, not sufficient (§ What this cannot say). A cost per micro-op boundary is not resolved either way (`gd1h` − `gd1`,
  +0.02 W [−0.10, +0.14], is wider than the single-lane contrast itself: 0.25 W against 0.175 W), nor is a cost tied to which lanes switch (the mirror
  pairs, ±0.15–0.22 W) *(corrected after verification, C1: this said "linear in flips means the constant extrapolates **by flip count
  to other kernels**. A kernel whose zeros switch one lane at a time pays the same per flip as one that switches all eight; nothing
  larger than about 3% of full scale is spent per micro-op boundary or for any lane switching")*. The constant must be the **whole**
  price, about 0.25–0.26 pJ (0.92–0.95
  pF of switched capacitance at 521.8 mV), not `gtr`'s 0.14 pJ: in M8 the other 0.10 pJ rides on bench toggle terms that track the
  flips in these quiet tiles and may not in other kernels. **Other clocks and cards are not tested here.** A linear per-flip energy is a
  switched capacitance, so it should scale as f·V² (E72's and E118's V² held on two cards). But M8's card-scale predictor fails by 5%
  on card 1, so a new card still needs its own measured scale.
- **Heat:** no heat term was measured. The ladder spans 1.2 W of D; at M8's heat law (0.119 °C per board W over the 4.5 s run on this
  card) that is 0.14 °C, under the firmware's whole-degree die reading. The gate's watts reach heat only through board power (§ 4).

## Results

**Six passes of six kept (15210–15215), 185 of 186 planned runs, none of the 185 failing a run gate: one anchor (`int8.zeros`, pass
15212 #29) was skipped by E78's registered launch gate, and no E152 tile was skipped** *(corrected after verification, C3: this said
"185 of 185 runs, none failing a run gate"; § Departures)*, **on the registered primary** (E78's `reduce_e78.py`
unchanged, dips removed by E82 A2's definition, 61 samples; leakage `auto`, which fitted **0.308 W/°C** over 63 runs, against E127's 0.191
on this card). [`scored.json`](scored.json) › `primary`, [`results.md`](results.md).

**1. Registered against what happened** (W; δ(n) = C(n) − (n / 8) C(8), C(n) = D(dose n) − D(`gd0`); 95% t(5) over the six passes):

| rule | what | line | result | verdict | arms that move it | what I expected, frozen |
|---|---|---|---|---|---|---|
| **E152-R1** | **linear within 10%**: every \|δ(n)\| + h ≤ τ = 0.10 × C8\* | τ = 0.1203 W | δ(1) **+0.030** [−0.037, +0.097], δ(2) **+0.015** [−0.095, +0.125], δ(4) **+0.025** [−0.070, +0.121]; worst \|δ\| + h **0.1247** (n = 2), and n = 4's 0.1208 also crosses τ *(C4, added after verification)*; C(8) +1.162 ± 0.149 | **INCONCLUSIVE** (not NONLINEAR: the worst \|δ\| − h is −0.037) | leakage 0.1994: **LINEAR** (0.108) | LINEAR: wrong as registered, by 0.004 W at two lanes and 0.0006 W at four *(corrected after verification, C4: this said "by 0.005 W")* |
| **E152-R2** | **E127's price carries**: the ladder's least-squares price per flip within p\* × [0.9, 1.1] = [236.65, 289.24] fJ | p\* 262.9 fJ | **251.5 ± 21.9 fJ** [229.6, 273.5] *(C2: 273.46, this said 273.4, truncated)*; 0.957 × p\*; per pass 224, 244, 266, 264, 278, 234 | **INCONCLUSIVE** | dips kept: **CARRIES** (263.3 ± 19.8); leakage 0.1994: **CARRIES** (259.7 ± 20.1) | CARRIES: not met |
| **E152-S1** | the session tie against E127 | ±0.50 W, int8 ±0.25 | `fp32.randn` 24.43 (E127 24.77), `fp16.randn` 21.91 (22.20), `anchor_pi` 8.37 (8.49), `int8.full` 6.95 (7.08) | **PASS** | leakage 0.3803 and 0 (FAIL: the anchors' level moves with the slope) | PASS |
| **E152-S2** | the bridge: this session's Q2 = `q_chk` − `q_steady` (E127's tiles) | E127 +1.275 ± 0.25 W | **+1.168 ± 0.239 W** | **PASS** | none | PASS |

Every verdict but S2 is arm-sensitive. The registered primary's noise is the leakage slope's (§ 4). Against what I expected: S1 and
S2 came in as frozen. R1 and R2 did not: they read INCONCLUSIVE, not LINEAR and CARRIES.

**2. The doses** (W over `gd0`; the price is C(n) over the flips above `gd0` × 1.12111 × 10⁹ ops a second):

| n lanes switching | tiles | flips/op above gd0 | **C(n) measured** | C(n) frozen, E127's price | price per flip, fJ [95%] | δ(n) / C(8) |
|---:|---|---:|---:|---:|---:|---:|
| 1 | `gd1a`, `gd1b` | 510 | **+0.175 ± 0.078** | +0.150 | 306 [170, 442] | +0.026 [−0.031, +0.082] |
| 2 | `gd2a`, `gd2b` | 1,020 | **+0.305 ± 0.138** | +0.301 | 267 [146, 388] | +0.013 [−0.081, +0.106] |
| 4 | `gd4a`, `gd4b` | 2,040 | **+0.606 ± 0.103** | +0.601 | 265 [220, 310] | +0.022 [−0.061, +0.105] |
| 8 | `gd8` | 4,080 | **+1.162 ± 0.149** | +1.203 | 254 [221, 287] | — |

The least-squares line of the mean C(n) on n (n = 1, 2, 4, 8) has an intercept of **+0.031 W**, 2.7% of C(8): no resolved share is
spent whenever any lane flips (reported; no interval). *(Added after verification, C1, post hoc.)* Fitted per pass, with t(5) over the
six passes, the intercept is **+0.031 ± 0.103 W, −6.0% to +11.1% of the rule's full scale C8\*** (on Q139(u)'s footing +0.018 ± 0.086 W,
−5.6% to +8.7%). So a shared part is not resolved, and only one above about 11% of full scale (9% on the footing) is excluded
([`corrections.txt`](corrections.txt) C1).

**3. Every tile** (D over fp32's zeros, W, 95% over six passes):

| tile | n | flips/op | D | | tile | n | flips/op | D |
|---|---:|---:|---:|---|---|---:|---:|---:|
| `fp32.gd0` | 0 | 16 | 4.668 ± 0.061 | | `fp32.gd2b` | 2 | 1,036 | 4.947 ± 0.097 |
| `fp32.gd1a` | 1 | 526 | 4.862 ± 0.133 | | `fp32.gd4a` | 4 | 2,056 | 5.294 ± 0.093 |
| `fp32.gd1b` | 1 | 526 | 4.824 ± 0.087 | | `fp32.gd4b` | 4 | 2,056 | 5.254 ± 0.107 |
| `fp32.gd1h` | 1\* | 528 | 4.863 ± 0.114 | | `fp32.gd8` | 8 | 4,096 | 5.830 ± 0.111 |
| `fp32.gd2a` | 2 | 1,036 | 5.000 ± 0.138 | | `fp32.q_chk` (E127's) | 8 | 4,096 | 5.899 ± 0.122 (E127 5.993) |
| | | | | | `fp32.q_steady` (E127's) | 0 | 0 | 4.731 ± 0.185 (E127 4.718) |

Every tile ran at 546.0 cycles an op, the dumped tile equal to its registered sha256 in every run.

**Reported, never a verdict** (`scored.json` › `primary.reported`): the mirror pairs, lane l against lane 7 − l, read +0.04 ± 0.22
(n = 1), +0.05 ± 0.15 (n = 2) and +0.04 ± 0.17 W (n = 4): no lane-assignment effect resolved. `gd1h` − mean(`gd1a`, `gd1b`) = +0.02 ±
0.12 W. That is the single-lane dose at four live lanes in every micro-op, its flips on 258 boundaries against 512, so a per-boundary
cost and the single-lane tiles' live-count spread are not resolved either. `gd0` − `q_steady` = −0.06 ± 0.18 W (frozen +0.07, if
E127's lane position adds per live lane-cycle); `gd8` − `q_chk` = −0.07 ± 0.11 W (frozen 0). Against the models, the ladder's price is
**1.07 × M8's whole per-flip price** at E127's pair (235.3 fJ), 1.04 × M7's (240.9), 1.01 × M6's (247.9) and **1.79 × M8's `gtr`**
(140.7 fJ).

**4. Post hoc, labelled, never a verdict** ([`posthoc_e152.py`](posthoc_e152.py), [`posthoc_e152.txt`](posthoc_e152.txt)):

- **Why this session is noisier than E127's.** The registered `auto` leakage slope fitted 0.308 W/°C on this session's 63 runs (E127:
  0.191; E78's fixed arm 0.1994; Q139(u)'s frozen aifoundry3 slope 0.2056). The window's die rise is read in whole degrees (0 or 1.0 for
  the same tile in different passes), and at 0.31 W/°C each step moves D by about 0.3 W. `q_steady` reads 4.84 W in the four passes where
  its window rose under 0.3 °C and 4.52 W in the two where it read 1 °C (+0.32 W). The per-pass spread of the contrasts is about 3× E127's
  (Q2's per-pass sd 0.23 W against 0.08). *(Added after verification, C5.)* The slope explains part of it, not all: on the footing
  (aifoundry3's frozen 0.2056 W/°C) Q2's per-pass sd is still 0.157 W, about twice E127's 0.076. Replacing the registered slope with the
  footing's removes about 60% of the variance above E127's (0.046 W² registered, 0.019 W² on the footing; a point reading from six and
  five passes' sd; [`corrections.txt`](corrections.txt) C5).
- **On the lab's one reduction footing** (Q139(u), the critic's rank 1: the registered reducer unchanged, dips removed once, leakage
  at aifoundry3's frozen 0.2056 W/°C; [`posthoc/`](posthoc/)): **R1 LINEAR** (δ(1) +0.014 [−0.052, +0.080], δ(2) +0.009 [−0.072, +0.090],
  δ(4) +0.025 [−0.059, +0.109]; worst \|δ\| + h 0.1085 ≤ 0.1203), **R2 CARRIES** (259.2 ± 20.1 fJ, 0.986 × p\*), S1 PASS, S2 PASS
  (Q2 +1.220 ± 0.165). The registered arm closest to it (E78's 0.1994) reads the same. *(Added after verification, C5.)* This reading
  is post hoc because E152's registration did not register it, not because the footing did not exist: Q139(u)'s footing rule (`d4c36bfe`,
  04:02 PST) and its frozen aifoundry3 slope (`f47669d1`, 04:20) were committed 84 minutes before the registration (`2a744f4d`, 05:44:49)
  and are its ancestors, and M8, whose frozen bridge columns E152 reports, is fitted on it (§ Departures).
- **Every frozen predictor of the ladder, out of sample** (rms of measured − predicted C(n) over n = 1, 2, 4, 8, registered / footing):
  E127's price 0.024 / 0.014 W; E127's unnetted price 0.057 / 0.044; M8 whole at E127's pair 0.061 / 0.071 (all low); M7 whole 0.047 /
  0.057; M8's `gtr` alone 0.31 / 0.32; M7's `gtr` alone 0.30 / 0.31.
- **As a capacitance:** 251.5 fJ (259.2 on the footing) at 521.8 mV is 0.92 (0.95) pF switched per lane-gate flip, every net that moves
  with one lane's gate together. M8's `gtr` is 0.52 pF of it.

## What it changes

**For item 6 of section 11 and the critic's rank 12.** The float B-lane gate's cost is **consistent with a constant per flip within
about ±10% of full scale**. From one lane switching to eight, at fixed data, the point departures from the straight line are 0.015–0.030
W (1.2–2.5% of the 1.2 W full scale), but their 95% intervals reach 0.125 W (10.4%), and every dose's price agrees with one value
*(corrected after verification, C1: this said "is, to the measurement, a **constant per flip**. From one lane switching to eight, at
fixed data, no dose sits more than about 0.03 W (3% of the 1.2 W full scale) off the straight line")*. The registered rule (every dose's
95% interval within 10% of full scale) reads INCONCLUSIVE on the registered reduction, missed by 0.004 W at the two-lane dose and 0.0006 W
at the four-lane dose *(corrected after verification, C4: this said "missed by 0.005 W at the two-lane dose")*, and LINEAR on the one
reduction footing the lab now uses for every test (post hoc) and at E78's fixed leakage arm. **E127's price** reads 0.96 of itself
(registered, INCONCLUSIVE) and 0.99 (footing, CARRIES). So M7's and M8's `gtr` *form* is consistent with the ladder, to about ±10% of
full scale *(corrected after verification, C1: this said "is the right shape")*. Their *value* is not the whole price: the gate's whole
cost is about 0.25–0.26 pJ a flip, of which `gtr` carries 0.14 pJ and the bench toggle terms the rest at E127's pair. M8 as a whole
reads 7% under the ladder's price as a point estimate, a gap the registered reading does not resolve: M8's price lies inside its
interval, and on the footing, post hoc, 3.8 fJ outside *(corrected after verification, C2: this said "and M8 as a whole still
under-prices it by about 7%")*. **Still open:** what physically spends the price (a lane's clock gate and branch, the enable logic, the
valid pipeline, the write-back mask: a cost consistent with linear in lanes points to per-lane hardware, but a shared path below
about 11% of full scale is not excluded *(corrected after verification, C1: this said "linear in lanes, so per-lane hardware, not a
shared path")*), the A side's gate and int8's, other
clocks and cards (the price's f·V² scaling is E72's and E118's, not tested here), and a registered PASS on one footing (a replicate on
Q139(u)'s footing, registered first).

**For the blog material.** Within what this test can resolve, about ±10% of full scale, switching a lane's zero gate costs the same
each time, however many lanes switch together. With every product held at zero and the operand wires moving the same bits, flipping one lane's gate every cycle cost
0.175 W, two lanes 0.305 W, four 0.606 W and eight 1.16 W. That is consistent with one constant per flip within about ±10% of full
scale: the points sit 1–2.5% off a straight line, but the registered test was inconclusive. It is about a quarter of a picojoule for
each time one lane's gate turns on or off, the energy of charging about a picofarad. So, in this one regime, what counts for the gates'
power is how many times they flip; whether the way the flips are spread across lanes matters at the 10% level is not resolved
*(corrected after verification, C1: this said "Switching a lane's zero gate costs the same each time, however many lanes switch
together", "within about 3% of a straight line" and "So for power, what counts is how many times the lanes' gates flip, not how the
flips are spread across lanes")*.

## Device commands sent

As registered ([`tools/claims-v3/e152/README.md`](../../../../tools/claims-v3/e152/README.md) § Device commands sent, classified from the
firmware source at et-platform `836a4ab`, BL2 0.22.0): **nine management commands, every one a read**. `ettelem config`
(`GET_MODULE_STATIC_TDP_LEVEL`, `GET_MODULE_TEMPERATURE_THRESHOLDS`, `GET_MODULE_POWER_STATE`, `GET_ASIC_FREQUENCIES`, `GET_ASIC_VOLTAGE`),
through E128's guard, at both ends of the smoke, of each stop test and of each of the six passes, and once at the session end: 19 reads of
the five. `ettelem sample` at 10 Hz through each block (`GET_MODULE_POWER`, `GET_SP_STATS`, `GET_MODULE_CURRENT_TEMPERATURE`,
`GET_ASIC_VOLTAGE`, `GET_MODULE_VOLTAGE`, `GET_ASIC_FREQUENCIES`; 18,376 samples in all, `since_reset_ms` −1 in every one), and two 1 s
`die_c` samples at each block's ends. The PMIC reads are `GET_ASIC_VOLTAGE`'s two voltage registers and `GET_MODULE_VOLTAGE`'s nine,
which the owner's rule of 2 November 2026 allows. **Not sent:** the statistics reset (no E152 call passes `--reset-ms`, and E128's guard
refuses it before the device opens), lib.sh's `drain_mgmt` (replaced by a refusal), the firmware-revisions query, any residency read,
any set. The checker `tools/claims-v3/dmcmd_audit.py` read GO on the box before the smoke (32 send sites, 0 disallowed, with the reviewed
`lib.sh:154` exception; [`logs/dmcmd-preflight-smoke.txt`](logs/dmcmd-preflight-smoke.txt)). The host program opened the ops node only.
Binaries: the registered `sparsity_host` `20e760c2…` and `ettelem` `16037641…` ([`logs/binaries.sha256`](logs/binaries.sha256)).
Residual, as E127's C4: aifoundry3 runs the thermal firmware build flashed on 7 October 2026, whose source is not held. So "every command
a read" rests on `836a4ab`'s handlers and on these nine reads' unchanged behaviour; this session's replies were normal.

## How it ran

| | |
|---|---|
| desk | Tue 3 Nov 05:14–05:44 PST: the design (`make_e152.py`), M8's/M7's/M6's frozen predictions of E127's two tiles by the committed `predict_blind6.py` (no bench run: the Intel's bench was busy with another lane's pool), the freeze, the self-test (24 of 24), the device-command audit (GO) |
| registration | `2a744f4d`, committed 05:44:49 PST; `run_e152.sh setup` on aifoundry3 05:45:29–05:45:45, no device access: every reused, code and tile hash identical, the preflight GO, both binaries the registered ones, a `V3_DRY` pass of 33 launches (11 on E152 tiles, no `--reset-ms`), the queue's stub test ([`logs/box-setup.txt`](logs/box-setup.txt)) |
| before the claim | #community-lab read at 05:46:47 (the day's post held one clause, aifoundry2's); `et-who` 05:46:46: no process holds an ET-SoC-1 device node or card lock, no device process of any user (other lab users' idle logins only, which E78's D1 rule lets pass) |
| smoke 15201 | 05:47:28–05:48:13: seven 2 s runs, 546.0 cycles an op on every item, every record ok, 0.5995 GHz, launch coverage ≥ 0.9975; config TDP 0 / 65 °C / 600 MHz / 523 mV at both ends; the board stop read its first live line 0.08 s old ([`logs/smoke.txt`](logs/smoke.txt)) |
| stop test | 15202 (board line 1 W) 05:48:27–05:48:33 and 15203 (die line 20 °C) 05:48:34–05:48:43: each stop fired at the first pre-launch reading on a live line (0.08 s and 0.07 s old), exit 6, no launch, no record ([`logs/stoptest.txt`](logs/stoptest.txt)) |
| passes | 15210 05:48:54–05:54:35 (341 s); 15211 –05:59:44 (294 s); 15212 –06:04:38 (279 s); 15213 –06:09:48 (295 s); 15214 –06:14:55 (292 s); 15215 06:15:10–06:20:04 (294 s): the budget rule let all six start ([`logs/e152-queue.log`](logs/e152-queue.log)) |
| stops | never near: the highest board reading 54.18 W (stop 65 W) and die 62 °C (stop 70 °C) |
| end | the session-end read 06:20:04, TDP 0 / 65 °C / max_power / 600 MHz / 523 mV; `et-who` clean; the post rewritten at 06:20:31 to drop this clause |
| reduction | `collect_e152.sh` on the Intel at nice 10, from a copy of the raw passes: E78's `reduce_e78.py` unchanged (sha256 checked), dips removed (61 samples), leakage `auto` 0.308 W/°C; E78-R5's checks: idle consistency median \|S − S0 − D\| 0.088 W (≤ 0.15), carry-over 0.0004 ± 0.0007 W/W (≤ 0.01), rail lag re-fit median 0.95 s, 600 MHz in every sample, 521.8 mV mean |

## Departures

- **None from the registered procedure.** The primary, its arms and every rule ran as written.
- **Disclosed, not a departure:** pass 15214's start `ettelem config` read returned no line within `timeout 10` (`config_start.json` is
  empty; the block's read tolerates that, as E127's did, and its stderr is not kept, so the cause is not recorded). The reads either side
  (15213's end, 06:09:4x; 15214's end, 06:14:55) read TDP 0 / 65 °C / max_power / 600 MHz / 522 mV, and nothing in E152 sets anything.
  18 of the 19 config reads returned the static configuration.
- **A rounding in the registration's prose, not a rule:** its README gives R2's band as [236.6, 289.2] fJ. The frozen value in
  `predictions-e152.json` is 0.9 × 262.9449 = 236.650, which is 236.7 at one decimal, and the scorer used the frozen value. The verdict is
  the same either way (the interval [229.6, 273.5] crosses either edge *(C2: this said 273.4, truncated)*).
- **Disclosed, not a departure:** no reduction was run before the queue ended; the post hoc footing arm (§ 4) was run after the
  registered collector, on the committed raw passes, with the unchanged reducer and scorer.
- **Disclosed after verification, not a departure (C3): one planned run was skipped.** 186 runs were planned (31 a pass) and 185 ran.
  Pass 15212's #29, the anchor `int8.zeros`, was skipped by E78's registered launch gate at 06:04:23 PST. 0.7 s into its approach the
  die read 59.0 °C, above the 58 °C launch line, so the approach ended off protocol and the runner skipped the run, as E78's runner does
  ([`aifoundry3/kinds/p15212/run.log`](aifoundry3/kinds/p15212/run.log) line 33; [`logs/e152-queue.log`](logs/e152-queue.log) line
  119). Every E152 tile ran in every pass. The skip leaves int8's zeros level in that pass on two runs, the reference of `int8.full`,
  which is an S1 cell only; R1, R2 and S2 use fp32 tiles alone. This README said "185 of 185 runs" and did not mention the skip.
- **Disclosed after verification (C5): the one footing existed when E152 registered.** Q139(u)'s footing rule (`d4c36bfe`, committed
  04:02:21 PST) and its frozen per-card slopes, aifoundry3's 0.2056 W/°C among them (`f47669d1`, 04:20:29), are ancestors of E152's
  registration (`2a744f4d`, 05:44:49): they were committed 84 minutes before it, in its history. The footing is the critic's rank 1 in Q139's target list,
  and M8, whose frozen columns the registration reports (`m8-bridge/`: "Q139(u)'s footing"), is fitted on it. The registration does
  not mention it (no "Q139(u)", no "0.2056"; its one "footing" names E78's run protocol), and registered it neither as the primary nor
  as an arm. Its stated reason for the primary is that it is E127's primary on this card (§ What runs). That is the reduction E127's
  frozen price p\* was read on, so R2 compares like with like. The footing readings in § 4 are post hoc for this reason, not because the
  footing came later. A dated note now says so in the registration
  ([`tools/claims-v3/e152/README.md`](../../../../tools/claims-v3/e152/README.md), at its end).

## What this cannot say

One card, one clock, one format (fp32), one data regime (quiet: the products zero, the operand bus fixed). Linear in flips is necessary
for a per-flip constant to carry to other kernels, not sufficient for it to carry to other clocks or cards. "The gate's cost" is
everything that changes with the gate pattern at equal operand bits, and E152 cannot tell those apart, only that they add over lanes.
The single-lane tiles' live count varies (3–5 a micro-op, average 4); `gd1h` holds it at 4 and agrees within 0.12 W, a bound, not a
test. The quiet tiles rest on the denormal flush (no result read back). The models' ladder columns rest on an assumption (their bench
terms scale with the flips) or on one term; they are reported, never scored. The registered verdicts are INCONCLUSIVE. The post hoc
footing's LINEAR and CARRIES are not registered verdicts: they would need a replicate registered on that footing.

## Files

- [`results.md`](results.md), [`scored.json`](scored.json): the registered reading, every rule, dose, tile and reported contrast, with every arm.
- `e152.json`, `runs.csv`, `reduce.txt`: the primary reduction (dips removed); `e152-dipskept.json`, `e152-leak{0.1994,0.3803,0}.json`,
  `e152-gatesoff.json` and their csv/txt/log files: the arms.
- [`posthoc_e152.py`](posthoc_e152.py), [`posthoc_e152.txt`](posthoc_e152.txt): § 4's numbers, standard library only; [`posthoc/`](posthoc/): the
  re-reduction on Q139(u)'s footing (`e152-footing-q139u.json`, `runs-footing-q139u.csv`, `scored-footing-q139u.json`, `results-footing-q139u.md`).
- `aifoundry3/`, the raw root as the box wrote it: `kinds/p15210`–`p15215` (every pass's runs, marks, telemetry, dumped tiles, config
  reads, manifest and the runner's log), `kinds-smoke/p15201`, `kinds-stoptest/p15202` and `p15203` (with `stoptest.json`); the reductions
  name this repo-relative root. `logs/`: the queue log, the dry run, the setup, smoke and stop-test transcripts, the session reads, the
  binaries' sha256, the device-command preflight, the times and the post's texts (`logs/post/`).
- `code.sha256`: every file the run and the reduction used.
- [`corrections_e152.py`](corrections_e152.py) → [`corrections.txt`](corrections.txt), [`corrections.json`](corrections.json): the
  numbers the corrections after verification quote, standard library only, from committed files only (post hoc) *(added after
  verification)*.
- Registration, tiles and code: [`tools/claims-v3/e152/`](../../../../tools/claims-v3/e152/README.md). The price: E127,
  [`../2026-11-02-e127-b-gate/`](../2026-11-02-e127-b-gate/README.md). The models: Q139(m)'s M8, [`../2026-11-03-q139m-model/`](../2026-11-03-q139m-model/README.md);
  Q138(m)'s M7, [`../2026-11-02-q138m-model/`](../2026-11-02-q138m-model/README.md). The footing: Q139(u), [`../2026-11-03-q139u-footing/`](../2026-11-03-q139u-footing/README.md).

To reproduce from the committed raw passes (a python with numpy), from the repository root:
`PY=python3 bash tools/claims-v3/e152/collect_e152.sh 'p152[1-9][0-9]' docs/reports/data/2026-11-03-e152-gate-dose/aifoundry3`. It writes
`build/e152-out/2026-11-03-e152-gate-dose/`, whose `e152*.json`, `runs*.csv`, `reduce*`, `scored.json`, `results.md`, `score.log` and
`code.sha256` are these. The footing arm (§ 4) is `reduce_e152.py docs/reports/data/2026-11-03-e152-gate-dose/aifoundry3/kinds/p1521[0-5]
--drop-dips --leak 0.20563713796102187 --no-refit --out <json>` scored by `score_e152.py --e152 <json>`; then
`python3 docs/reports/data/2026-11-03-e152-gate-dose/posthoc_e152.py`.
Since the corrections after verification, `python3 docs/reports/data/2026-11-03-e152-gate-dose/corrections_e152.py >
docs/reports/data/2026-11-03-e152-gate-dose/corrections.txt` prints the numbers they quote (standard library; it also writes
`corrections.json`).

## Corrections after verification (Tue 3 Nov 2026)

E152's first independent verifier (lane `verify-a3-e152-gate-dose`, about 15:55–16:20 PST; an earlier attempt died at about 07:46 PST on
a usage limit) re-ran the registered `collect_e152.sh` on the committed raw passes in a `git archive` export (all 22 outputs
byte-identical), re-ran the footing arm and `posthoc_e152.py` (byte-identical) and the self-test (24 of 24), re-scored every rule with
its own scorer (R1 INCONCLUSIVE, R2 INCONCLUSIVE, S1 PASS, S2 PASS; on the footing LINEAR and CARRIES), decoded every tile's flips from
the committed bytes (510 × n above `gd0`, as registered), traced every command sent to a read at et-platform `836a4ab` (`since_reset_ms`
−1 in all 18,376 samples), and matched all 245 raw files and 9 logs to aifoundry3's copies in a read-only session. Its verdict: the run
holds, with fixes to how it is read. The corrections (desk only, about 16:30–17:00 PST; no card, no device command, nothing re-run, no
Modal) change no measured number, rule, frozen prediction or registered verdict. Their numbers are printed by
[`corrections_e152.py`](corrections_e152.py) into [`corrections.txt`](corrections.txt), written independently of the verifier's scripts;
they reproduce every number it gave, and add two (R2's upper end is 273.46 fJ, truncated to 273.4 before; on the footing, M8's 0.071 W
rms just exceeds that reading's smallest contrast half-width, 0.065 W). The title said: "no departure from a straight line larger than
3% of full scale at any dose, but the registered reading is INCONCLUSIVE by 0.005 W; E127's price reads 0.96 of itself, INCONCLUSIVE"
(C1, C4).

- **C1 (major): the linearity was stated to its point estimates, not its bounds.** The title, the plain words, What this does to
  predicting power and heat, What it changes and the blog paragraph said no dose departs from the straight line by more than about 3% of
  full scale, that no shared part larger than about 3% exists, that nothing larger than about 3% is spent per micro-op boundary or for
  any lane switching, and that the gate "costs the same each time, however many lanes switch together". Those are point estimates:
  δ(1), δ(2) and δ(4) are +2.5, +1.2 and +2.1% of the rule's full scale C8\* = 1.203 W (+2.6, +1.3 and +2.2% of the session's own
  C(8)), and their 95% intervals run −3.1 to +8.1, −7.9 to +10.4 and −5.8 to +10.0%. That is why R1 reads INCONCLUSIVE: the session
  resolves departures only to about 10% of full scale. The least-squares intercept, fitted per pass with t(5), is +0.031 ± 0.103 W,
  −6.0 to +11.1% of C8\* (on the footing +0.018 ± 0.086 W, −5.6 to +8.7%), so a part spent whenever any lane flips is excluded only above
  about 11% (9%). The per-boundary test (`gd1h` − `gd1`, +0.020 W [−0.104, +0.144], an interval wider than the single-lane contrast
  itself, 0.175 W) and the mirror pairs (±0.15–0.22 W) resolve nothing. "Linear in flips means the constant extrapolates by flip count to other
  kernels" contradicted this README's own "necessary, not sufficient": it is now conditional, and carrying the constant to other kernels
  is untested. Corrected in place: the title, the plain words, both prediction bullets, Results 2 (the intercept's interval, added),
  What it changes, the blog paragraph.
- **C2 (minor): M8's 7% is a point estimate, not a resolved correction.** "M8 under-prices the gate by about 7%, 0.09 W at full
  scale", M8's errors "low at every dose" and, in the lane's returned result, a "+7%" candidate correction for M8 read as measured
  differences. As registered they are not resolved: M8's
  whole price, 235.3 fJ, lies inside the ladder's 95% interval [229.6, 273.5] fJ (by 5.7 fJ; M7's 240.9 and M6's 247.9 too), and C(8)'s
  [1.013, 1.311] W holds both M8's 1.076 and E127's 1.203 W. Both rms errors (E127's price 0.024, M8 0.061 W) lie inside the contrasts'
  95% half-widths, 0.078–0.149 W. Every C(n) is taken over the same D(`gd0`) (4.668 ± 0.061 W), so a shift of that one reference inside
  its own half-width moves all four together by more than M8's gaps at one and two lanes (+0.041, +0.036 W): "low at every dose" is not
  four independent readings. M8 is fitted on Q139(u)'s footing, so the like-for-like comparison is the footing's, which is post hoc:
  there the interval [239.1, 279.3] excludes 235.3 fJ by 3.8 fJ (ladder / M8 1.101), and M8's 0.071 W rms just exceeds the smallest
  half-width (0.065 W). The 7% (1.069) stays, as a point estimate. R2's upper end, 273.46 fJ, was truncated to 273.4 (Results 1 and
  § Departures, corrected).
- **C3 (minor): one planned run was skipped, undisclosed.** Results said "185 of 185 runs, none failing a run gate". Six passes of 31
  items planned 186 runs and 185 ran: pass 15212's #29, the anchor `int8.zeros`, was skipped by E78's registered launch gate at
  06:04:23 PST (the die read 59.0 °C, above the 58 °C launch line; `aifoundry3/kinds/p15212/run.log` line 33, `logs/e152-queue.log`
  line 119). No E152 tile was skipped, so R1, R2 and S2 are unaffected; int8's zeros level in that pass rests on two runs, the reference
  of `int8.full`, an S1 cell. Corrected in Results and disclosed in § Departures.
- **C4 (minor): two doses cross τ, not one.** The INCONCLUSIVE was put on the two-lane dose alone, "by 0.005 W". Both the two-lane and
  the four-lane doses cross τ = 0.1203 W: \|δ(2)\| + h = 0.1247 W (10.4% of C8\*, over by 0.0044 W, which is 0.004, not 0.005) and
  \|δ(4)\| + h = 0.1208 W (10.0%, over by 0.0006 W). Corrected in the title, the plain words, Results 1 and What it changes.
- **C5 (minor): the footing existed at registration; the noise is not all the slope's.** Q139(u)'s footing rule (`d4c36bfe`, 04:02:21
  PST) and its frozen aifoundry3 slope 0.2056 W/°C (`f47669d1`, 04:20:29), the critic's rank 1, are ancestors of E152's registration
  (`2a744f4d`, 05:44:49), 84 minutes earlier, and M8's frozen bridge columns are on that footing. The registration mentions neither and
  registered the footing neither as the primary nor as an arm; it gives as the primary's reason that it is E127's primary on this card,
  the reduction E127's frozen price p\* was read on, so R2 compares like with like. This README called the footing's LINEAR and CARRIES
  post hoc without saying the footing existed, and put the session's noise wholly on the registered `auto` slope. On the footing Q2's
  per-pass sd is still 0.157 W, about twice E127's 0.076 (registered 0.228), so the slope explains about 60% of the variance above
  E127's. Disclosed in § Departures and § 4, corrected in the plain words; the registration gains a dated note at its end.

**What the corrections do to predicting power and heat.** No number moves; what moves is how far the numbers can be read. The term
tested is still the float B-lane gate's per-flip price (M7's and M8's `gtr` form, a constant per gate flip) and its linearity in flips.
Out of sample on the four dose contrasts (rms of measured − predicted, registered / footing): E127's frozen price 0.024 / 0.014 W,
M8's whole price at E127's pair 0.061 / 0.071 W, M8's `gtr` alone 0.31 / 0.32 W. Before the corrections these read as "M8 is 7% low
and E127's price is right"; after them, as registered, the gap between M8 and E127's price lies inside the contrasts' 95% half-widths,
so no correction to M8 is resolved (post hoc, on M8's own footing, its price falls 3.8 fJ outside the ladder's interval). What is
resolved is that `gtr` alone carries about half the cost, so a model must price the whole per-flip cost. Linearity is supported to
about ±10% of full scale, not 3%, and a shared part above about 11% (9% on the footing) is excluded; a per-flip constant is the right
form within that, in one quiet regime on one card at one clock, and carrying it to other kernels, clocks or cards is untested. Heat was
not measured: the ladder's 1.2 W span is 0.14 °C at M8's heat law, so heat prediction is unchanged.

**Not changed:** the registration's text (`tools/claims-v3/e152/`, `2a744f4d`; only a dated note at its end, C5),
`predictions-e152.json`, `scored.json`, `results.md`, every reduction and arm, `posthoc/`, `posthoc_e152.py` and `.txt`, `code.sha256`,
the raw passes and logs, and every verdict: **R1 INCONCLUSIVE, R2 INCONCLUSIVE, S1 PASS, S2 PASS** as registered; LINEAR and CARRIES
on the footing, post hoc.
