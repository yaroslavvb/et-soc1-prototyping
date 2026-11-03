# E162: which operand pairing a GPU pays for, row against K, on A100 boards (on the L40S the power controller holds the clock)

*On the kinds page, [section 11, what is still open](https://spacesheep.dev/@yaroslavvb/horace-kinds-of-numbers#11-what-is-still-open):
**item 2, "a GPU measured the same way"**, in the form Q138's final critic ranked **9th**: which operand pairing an
A100 pays for (R4b fails; lag 32 does no better blind; G4 is unstable), and a later generation with headroom under its
cap. The question was left open by [E149](../2026-11-02-e149-gpu-model-check/README.md)'s correction C3 ("only 'not lag
1' is confirmed; which pairing the A100 pays for is open") and by [E150](../2026-11-02-e150-second-gpu/README.md) ("a
later part with headroom under its cap would answer that").*

*Tue 3 Nov 2026 (week 45), Q139, which continues the owner's mandate of Mon 2 Nov 2026, about 18:40 PST: "all cards are
available, feel free to settle any unanswered questions regarding horace's power model using [the private archive's
host, withheld], runs on aifoundry and modal for sanity checks on GPUs (don't exceed $20 on modal)", with Q137's goal,
"to be able to predict the power requirement and heat generation of various kinds of numeric computations as accurately
as possible". Pre-registered in `038db597` ([`tools/gpu/e162/E162.md`](../../../../tools/gpu/e162/E162.md): the kinds,
the held-out kinds, the ridge row+K form, the rules, a selftest), committed at 04:32:27 PST and pushed at 04:32:29,
before any GPU call; amendments A1 and A2 (`0e8479c9`, committed 04:48:57, pushed 04:49:00) after the declared L40S
smoke and before any stage-1 data was read; the freeze `54e8f87d` (committed 04:54:02, pushed 04:54:05) before stage
2's first call *(push times added after verification, C8)*. Modal workspace `yaroslavvb`, app `e162-gpu-row-k`.*

*Corrected after verification (a dated note, Tue 3 Nov 2026, about 06:05 PST; desk only: no GPU, no Modal app started,
nothing re-run, no device command). An independent verifier re-derived E162 from the committed raw samples, the bill
and the commit history: the spend, the order of registration, amendments, freeze and calls, the clock under the cap,
both reductions to 0 W, the blind score and every registered verdict. It found one major fault and five minor ones, and
correcting them found two slips more. None changes a measured number, a frozen model, a prediction, a rule or a
verdict. Each is corrected in place, marked "corrected after verification, C<n>", and listed in
[§ Corrections after verification](#corrections-after-verification) at the end; the numbers they quote are printed by
[`corrections-numbers.py`](corrections-numbers.py) → [`corrections-numbers.txt`](corrections-numbers.txt). The main one,
C1: **the row-lag is identified, the K-lag is not.** On an A100 it is A's rows one apart that cost. Along K, pairs 8 or
more apart cost where pairs 1, 2 or 4 apart do not, but blind, the same form refitted at K-lag 16 or 32 predicts the
held-out kinds as well as at K-lag 8 (15.8 and 16.2 W against 15.7, post hoc), so "K-steps of 8" was RK's stage-1
choice, not a finding. The registration ([`tools/gpu/e162/E162.md`](../../../../tools/gpu/e162/E162.md), `038db597` with
A1-A2) is frozen and unchanged, apart from a dated note appended under its amendments (C2, C4).*

## Results

**On an A100 the operand pairing that costs power is A's rows, not neighbours along K.** Square waves along K with a
random phase per row cost **38-48 W more** than the same waves with one phase shared by every row (W1 holds:
`bf16.sq1` − `bf16.kS1` = +44.0 ± 1.7 W, b = 16 +38.5 ± 2.2, b = 64 +48.0 ± 4.0). With the row flips removed,
consecutive elements along K are still not a pairing (W2 fails, `kS1` − `kS64` = −6.7 ± 2.8 W), while consecutive rows
are (W3 holds, `rS1` − `rS64` = +60.4 ± 2.6 W). Rows random and constant along K cost more than K random and constant
down the rows in every format (W4: bf16 +58.9 ± 3.2 W, fp16 +44.6 ± 3.9, int8 +21.3 ± 3.8), and the rolled sorts agree
(W5: `drollK` − `rollM` = +27.9 ± 4.6 W). **It is A's rows** (M, at one k): a row wave on A alone costs 88.1 W, on B
alone 20.9 W, while a K wave costs the same on either side (25.1 against 24.1 W). Along K, the elements that cost are
**8-16 apart**: with no row flips, waves in blocks of 1, 2 or 4 cost 24-29 W and blocks of 8 or 16 cost 51-52 W
(`model-e162-a100.json` `rules_stage1`; `posthoc.txt` §5).

**Blind, on 22 held-out kinds never measured before, on two A100 boards the fit never saw, the constrained (ridge)
row+K form RK predicts power to 15.7 W rms [9.9, 21.8], 10.1% of the 154.7 W from zeros to random bf16, biased
+2.7 W; E149's frozen G1, the ET-SoC-1 model's form, reads the same kinds to 52.4 W [39.3, 64.1], 33.8%.** RK chose
K-lag 8 and row-lag 1 on stage 1 *(corrected after verification, C1: the row-lag is identified, the K-lag is not.
Blind, the same form at K-lag 8 with row-lags 2-32 reads 19.2-37.9 W. Along K, stage 1's scan does not resolve lag 8
from 2, 4 or 32; blind, refitted at K-lag 16 or 32, the form reads 15.8 or 16.2 W, not resolved from lag 8's 15.7,
while lags 4, 2 and 1 read 17.8, 20.3 and 24.9 W, each resolved worse; all post hoc. So along K the data identify
pairs 8 or more apart, not 1, 2 or 4 apart)*. **BEAT holds** (ratio 0.299 against a bar of 0.8; the paired
bootstrap's 95% interval for rms(G1) − rms(RK) is [+22.1, +50.1] W), **STABLE holds** (fully nested 13.9 / 15.4 /
12.7 W in bf16 / fp16 / int8 against in-sample 10.1 / 8.7 / 9.7 W, pooled 14.0 W against 67.3 W for G1's form refitted
on the same rows; 14.9 / 15.5 / 13.1 W, pooled 14.7, with the column scale recomputed in each fold, *corrected after
verification, C2*), and **BEAT_p holds** too: G1's form refitted on the same data reads 48.0 W, so the gain is the form, not the
data. The critic's rule (BEAT with STABLE) **holds**. The same form fitted without the ridge runs to 112 W nested in
fp16 and 37 W in int8; E149's G4 explodes on the held-out kinds (550 W rms, fp16 kinds predicted at −1,263 to
+1,729 W) (`score-e162-a100.json` `models`, `rules`; `model-e162-a100.json` `rk`, `stable`; `posthoc.txt` §1).

**Heat, through E149's frozen heat model**: a cell's die reading over its two references (a 5 s window, from bits
only, through E149's frozen two-pole model) is predicted to **1.28 °C rms with RK's power against 3.33 °C with G1's**
(HT1 holds); the heat model driven by the measured power reads 0.69 °C, its own floor here (`score-e162-a100.json`
`heat_cells`). *Corrected after verification, C6 (this said "Heat follows"):* no heat term is tested. Through that
linear model a power error becomes 0.061 °C per W over a 5 s cell (R² 0.99995), so HT1 is BEAT's power gain in
degrees, on the heat model's 0.69 °C floor.

**The L40S cannot test this in this harness: its power controller holds its clock in every window** *(corrected after
verification, C4: this said it "runs these GEMMs at its power controller's limit")*. In the declared smoke every window
from 1024³ to 4096³, random and zeros alike, ran with the SW power-cap reason bit set in every 100 ms sample, below its
2520 MHz maximum, zeros included at 60-69% of the 350 W limit, so no clock is held. The data move its clock as well as
its power: random bf16 drew 321-350 W, 109-123 W more than zeros, at an 8.6-19.8% lower mean SM clock. At 2048³ it ran
at 1875-1905 MHz and 222.7 TFLOPS against zeros' 2235 MHz and 261.0, and at 4096³ 19% fewer TFLOPS (Horace He's
regime, as on the L4 in E150); at 1024³ it ran 2% fewer, and at 1536³ and 3072³ 2-4% more (one 5 s window each). By
the registered rule the L40S arm stopped after the smoke (amendment A1; `choice-ls.json`).

| what is predicted (A100, held-out kinds, new boards) | before E162 | after E162 | source |
|---|---|---|---|
| **power of a new kind**, 22 kinds built to separate the pairings | E149's frozen G1 **52.4 W** rms (33.8% of the span), bias +3.2 W; G1's form refitted on the same rows 48.0 W; the best form frozen before E162, E149's S1 (static bits), **36.1 W** (23.3%) *(added after verification, C5)* | **RK 15.7 W** rms [9.9, 21.8] (10.1%), bias +2.7 W; 20 of 22 inside its band | `score-e162-a100.json` `models`, `rules`; `posthoc.txt` §1; `corrections-numbers.txt` C5 |
| power of a new kind, E149's 17 held-out kinds (E149's boards; seen by the designer, no verdict) | G1 24.7 W; E149's G4, picked after scoring, 12.8 W | RK 12.8 W (12.1 W without the checkerboard, G1 16.1 W) | `score-e162-a100.json` `seen_kinds_e149_stage2`; `posthoc.txt` §4 |
| **heat**: a cell's die reading over its references, from bits | G1's power: **3.33 °C** rms | RK's power: **1.28 °C**; measured power 0.69 °C. This is the power gain through E149's frozen heat model (0.061 °C per W of power error); no heat term is retested *(corrected after verification, C6)* | `score-e162-a100.json` `heat_cells`; `corrections-numbers.txt` C6 |
| which pairing an A100 pays for | open (E149 C3): "not lag 1" only | A's rows one apart (row-lag 1, A over B), chosen on stage 1 and confirmed blind; along K, pairs 8 or more apart rather than 1, 2 or 4, with 8, 16 and 32 not told apart (RK counts lag 8, its stage-1 choice) *(corrected after verification, C1: this said "A's consecutive rows and K-steps of 8 (… confirmed blind)")* | `model-e162-a100.json` `rk.s`, `rk.r`, `rules_stage1`; `corrections-numbers.txt` C1 |
| a later generation with headroom under its cap | E150: the L4 runs at its 72 W cap | the L40S's power controller holds its clock in every window too: the SW power-cap reason bit in every sample, zeros included at 60-69% of its 350 W limit *(corrected after verification, C4: this said it "runs at its power limit")* | `choice-ls.json`; `corrections-numbers.txt` C4 |

## The L40S: cap-bound at every size

`modal billing rates`, read Tue 3 Nov 2026 04:05:39 PST: L40S $1.95/h, A100-40GB $2.10/h, so the L40S qualified by
rate. The declared smoke (run `e162-20261103-smoke`, one board, `6aceaa9c621a`, 350 W enforced, NVML maximum 2520 MHz,
04:32:51-04:35:32 PST) read, one 5 s window each (`choice-ls.json` `table`):

| size | random W | random MHz | random TFLOPS | zeros W | zeros MHz | zeros TFLOPS |
|---|---:|---:|---:|---:|---:|---:|
| 1024³ | 345.8 | 2190-2310 | 150.9 | 227.2 | 2475-2490 | 154.1 |
| 1536³ | 340.1 | 2145-2160 | 146.1 | 223.7 | 2385-2400 | 143.3 |
| 2048³ | 349.6 | 1875-1905 | 222.7 | 226.5 | 2235 | 261.0 |
| 3072³ | 321.4 | 2235 | 191.8 | 209.7 | 2445 | 185.1 |
| 4096³ | 349.5 | 1740-1770 | 220.0 | 240.3 | 2175-2190 | 272.2 |

**Every one of these windows carried the SW power-cap bit (0x4) in 100% of its samples**, zeros at 210-240 W (60-69% of
the limit) included, and none held the maximum clock. The registered rule needs a held clock (the maximum, or a clock
that zeros at 1024³ holds with no reason bit) and a random window under 90% of the limit with that clock: none
qualifies. So in this harness no clock is held, and the data move the L40S's clock as well as its power: random drew
109-123 W more than zeros at every size, at an 8.6-19.8% lower mean SM clock, and ran 15-19% fewer TFLOPS at 2048³ and
4096³ (2% fewer at 1024³, 2-4% more at 1536³ and 3072³) *(corrected after verification, C4: this said its power "reads
its power controller, not the data" and that the data move its clock "instead")*. NVML's instantaneous power (field 186) peaked at
most 10 W above a window's mean for random (355.5 W at 1024³) and 2 W for zeros (at most 241.5 W), so it is not peaks
near 350 W that set the bit in the zeros windows; what the controller limits there is not read here.
The smoke's plumbing step built all 58 E162 kinds of every format at 512 on the L40S, with every C finite and the flip
patterns as designed. No other later-generation GPU on Modal is at or under the A100-40GB's rate, so E162 has no
later-generation arm (amendment A1).

## Stage 1: what an A100 pays for

Run `e162-20261103-a1`, boards **A** `ac97f0c6a6ae` and **B** `83190b6e35b9` (A100-SXM4-40GB, neither one of E135's or
E149's), 04:33:50-04:52:00 PST, two passes each. **All 52 kinds kept every window valid on both boards** (1410 MHz in
every 100 ms sample, no reason bit; V0 holds); the hottest window drew 376.8 W, 23 W under the 400 W limit
(`reduce-a1.json`). **E149's thirteen bridge kinds read E149's watts again**: bf16 randn 154.7 W (E149 154.7), `drollK`
143.9 (143.0), `dsortK` 99.6 (103.2), `sq1` 72.9 (72.2), `mk3` 100.2 (100.2); the session scale is 0.995 / 0.986 /
0.989 in bf16 / fp16 / int8, rms differences 1.1-1.6 W (`model-e162-a100.json` `scale`). E162's feature code
reproduces E149's committed features exactly on E149's bytes (113 kinds, sha256 equal, largest difference 0;
`checks`).

y below is watts over the same GEMM on zeros, ± SE over 2 boards × 2 passes (`reduce-a1.json` `kinds.*.y`, `se`):

| block b | 1 | 2 | 4 | 8 | 16 | 32 | 64 |
|---|---:|---:|---:|---:|---:|---:|---:|
| along K, one phase for every row (`kS`) | 28.9 ± 0.8 | 28.1 ± 0.9 | 24.3 ± 1.9 | 51.1 ± 0.8 | 52.4 ± 1.1 | 36.5 ± 1.3 | 35.6 ± 2.7 |
| along K, a phase per row (E149's `sq`) | 72.9 ± 1.5 | | | | 90.9 ± 2.0 | | 83.6 ± 3.0 |
| along the rows, one phase for every column (`rS`) | 97.5 ± 2.5 | 61.3 ± 1.6 | 67.7 ± 1.2 | 48.5 ± 0.9 | 47.1 ± 0.6 | 38.4 ± 1.9 | 37.1 ± 0.6 |

| bf16 kind | y | | bf16 kind | y |
|---|---:|---|---|---:|
| `rowc` (rows random, constant along K) | 128.8 ± 2.9 | | `colc` (K random, constant down the rows) | 69.9 ± 1.3 |
| `rowcA_colcB` | 134.8 ± 4.3 | | `colcA_rowcB` | 75.2 ± 1.9 |
| `drollK` (K smooth, rows out of step) | 143.9 ± 3.8 | | `rollM` (rows smooth, K out of step) | 116.1 ± 2.6 |
| `rS1A` (row wave on A only) | 88.1 ± 1.9 | | `rS1B` (row wave on B only) | 20.9 ± 1.3 |
| `kS1A` (K wave on A only) | 25.1 ± 2.0 | | `kS1B` (K wave on B only) | 24.1 ± 1.2 |
| `rC16` (rows, a phase per column) | 70.5 ± 1.1 | | randn | 154.7 ± 3.9 |

fp16: `rowc` 108.1 ± 3.3, `colc` 63.5 ± 2.1, `kS1` 27.9 ± 0.7, `kS16` 39.5 ± 1.8, `rS1` 78.8 ± 2.5, `rS16` 44.6 ± 1.6,
randn 123.4 ± 4.2. int8: `rowc` 71.9 ± 2.7, `colc` 50.6 ± 2.7, `kS1` 27.1 ± 1.3, `kS16` 33.8 ± 2.2, `rS1` 51.1 ± 2.4,
`rS16` 31.9 ± 2.6, random 83.8 ± 2.7. *(Five SEs corrected after verification, C7: `kS1`, `kS8`, `rS1`, `rowcA_colcB`
and int8 random had been rounded twice, from `reduce-a1.txt`'s two decimals.)*

- **Rows cost, K neighbours do not** (W1 holds; W2 fails as registered; W3 holds). A wave with a phase per row flips
  half of the row pairs at every row lag, and that costs 38-48 W at any block size; the same wave with no row flips
  costs 24-52 W. Consecutive elements along K, with the rows identical, cost nothing beyond what every two-value kind
  costs (`kS1` 28.9 W against `kS64` 35.6 W). E149's R4b fails again (`sq1` − `sq64` = −10.8 ± 3.3 W).
- **Along K the cost sits 8-16 elements apart.** With no row flips, blocks of 8 and 16 (whose pairs 8 or 16 apart
  differ) cost twice what blocks of 1-4 cost (whose pairs 8, 16 and 32 apart are equal). Blocks of 32 and 64 cost less
  than 8 and 16, though their pairs 32 apart differ: K-lag 32 is not where the cost is. *(Added after verification, C1:
  the waves locate the cost; as RK's one K-lag, 8, 16 and 32 predict the held-out kinds alike, post hoc, so the blind
  test does not pin the model's lag.)*
- **Along the rows the cost sits one row apart, on A**: alternating rows (`rS1`) cost 97.5 W, the most of any wave,
  and on A alone 88.1 W against 20.9 W on B alone. In this GEMM (`A @ B.t()`, A stored M × K, B stored N × K, cuBLAS)
  the M direction of A is the costly one and B's N direction is cheap. Nothing here reads which operands meet on which
  wire; this says which counting predicts the power.

## The model, fitted on stage 1 and frozen

RK (E162.md, "The models"): G1's terms at a K-lag s, plus each field's flips at a row-lag r (A + B), the A − B row
asymmetry and the row gate transitions, by ridge with the penalty chosen by exact leave-one-kind-out error; (s, r)
chosen once, pooled over the formats. The fit rows are E149's stage-1 kinds (E149's y) and E162's 36 new kinds (their
y over the session scale): 75 bf16, 26 fp16 and 24 int8 rows (`model-e162-a100.json` `n_rows`).

| model | bf16 in · nested | fp16 in · nested | int8 in · nested |
|---|---|---|---|
| **RK** (ridge, s = 8, r = 1; nested = fully nested) | 10.13 · **13.94** | 8.70 · **15.40** | 9.65 · **12.66** |
| the same form by OLS | 10.01 · 12.87 | 6.51 · 112.30 | 6.87 · 37.48 |
| G1p (G1's form by OLS on the same rows) | 29.33 · 33.49 | 28.80 · 132.84 | 19.64 · 30.98 |
| G4p (G4's form by OLS, its own lag scan picked 2) | 14.06 · 18.04 | 7.14 · 37.13 | 7.80 · 13.89 |

The scan's best (s, r) by pooled leave-one-kind-out rms: (8, 1) 12.40 W, (4, 1) 13.15, (32, 1) 13.34, (2, 1) 13.47,
(16, 1) 13.74, (1, 1) 15.66; every pairing with a row-lag other than 1 does worse than every one with row-lag 1 (the
best of them, (8, 4), 16.06 W). Inside the fully nested folds the choice was (8, 1)
or (4, 1) in bf16 and (8, 1) in every fp16 and int8 fold. *(Added after verification, C1 and C2.)* The scan carries no
interval: a paired bootstrap over the 125 rows (approximate, since leave-one-out residuals share rows) resolves (8, 1)
from (16, 1) and (1, 1) but not from (4, 1), (32, 1) or (2, 1), and in fp16 lag 8 ranks fourth. These are the code's
closed-form LOKO (`ridge_loo`), which holds the column scale at all the rows, the left-out one included; E162.md calls
it exact for columns scaled over the training rows. With the scale recomputed on each fold's training rows the choice
and every λ are the same, so the frozen model is too, but the scan reads (8, 1) 12.90 W, (32, 1) 13.67, (4, 1) 13.73,
(2, 1) 13.99, (16, 1) 14.77 and (1, 1) 16.84, with (8, 4) 16.45 and (8, 2) 16.46 below (1, 1): "every pairing with a
row-lag other than 1 does worse" holds in the closed form only. RK's fully nested errors are then 14.89 / 15.52 /
13.14 W (pooled 14.71), and the folds chose (8, 1) in 73 of 75 bf16 folds ((4, 1) and (32, 1) once each), 24 of 26 fp16
folds ((32, 1) and (32, 4) once each) and all 24 int8 folds. λ = 0.03, 0.1, 0.3 (bf16, fp16, int8). E149's frozen G1 reads
E162's 36 new stage-1 kinds, which it never saw, to 58.5 W rms. The coefficients are predictors at E149's footing, not a
price list (`model-e162-a100.json` `rk.fmts.*.coef`); in bf16 a row flip of the sign is priced +19.5 W per unit share,
of the exponent +5.9 and of a mantissa bit +6.0, with A's row flips above B's (the A − B row term +4.7).

## Stage 2, blind: 22 held-out kinds on two new boards

Run `e162-20261103-a2`, after the freeze (`54e8f87d`, 04:54:02 PST), 04:54:25-05:05:14 PST, two passes per board
(amendment A2): boards **A** `d31f897269bd` and **B** `80d5c1565177` (A100-SXM4-40GB), neither a fit board (the guard's
refuse list: E149's and E162's stage-1 boards) nor one of E135's or E149's stage-2 boards; none refused. Every operand's
sha256 matched the frozen predictions'. Every window held 1410 MHz with no reason bit; the hottest cell drew 381.2 W.
**Two cells were dropped by E149's validity rule**, `int8.walkK` and `int8.zeros` in board B's pass 2: their bracketing
reference caught 12 NVML samples where the rule wants 60% of the expected ~20 (a sampler gap; 1410 MHz, no reason bit),
so `int8.walkK` has 3 replicates and every other held-out kind 4 (`reduce-a2.json` `kinds.*.invalid`).

| kind | measured y ± SE | RK | G1 (E149) | G1p | E149's G4 |
|---|---:|---:|---:|---:|---:|
| `bf16.cdup8` (runs of 8 along K) | 148.2 ± 4.4 | 159.5 | 50.6 | 55.3 | 158.2 |
| `bf16.checkv` (two values, (i − k) parity) | 94.3 ± 2.0 | 112.4 | 135.7 | 84.6 | 137.8 |
| `bf16.kB8_4` (K wave, a phase per 8 rows) | 49.5 ± 1.0 | 33.3 | 60.4 | 54.5 | 33.8 |
| `bf16.rdup8` (rows repeated 8 times) | 85.2 ± 2.6 | 88.9 | 158.6 | 132.1 | 80.3 |
| `bf16.rollM_A` | 113.6 ± 2.0 | 104.7 | 158.7 | 132.3 | 122.3 |
| `bf16.sinpos` (positional table) | 113.6 ± 3.4 | 93.8 | 134.0 | 106.5 | 90.7 |
| `bf16.stripeK0` (odd columns zero) | 104.7 ± 2.4 | 79.8 | 207.1 | 233.7 | 79.1 |
| `bf16.stripeR0` (odd rows zero) | 109.1 ± 2.4 | 156.8 | 75.7 | 62.4 | 149.3 |
| `bf16.t16x16` | 56.0 ± 1.3 | 58.6 | 43.0 | 49.9 | 75.2 |
| `bf16.t32x4` | 78.4 ± 1.6 | 81.2 | 66.0 | 66.3 | 72.0 |
| `bf16.t4x32` | 67.1 ± 1.4 | 60.9 | 39.1 | 47.1 | 70.3 |
| `bf16.walk2` | 118.2 ± 2.8 | 99.7 | 122.9 | 106.9 | 102.6 |
| `bf16.walkK` | 159.8 ± 3.3 | 159.1 | 119.9 | 109.5 | 155.7 |
| `bf16.walkR` | 130.9 ± 2.9 | 125.3 | 195.9 | 173.8 | 140.5 |
| `fp16.cdup8` | 121.7 ± 3.8 | 127.6 | 28.7 | 41.7 | 130.1 |
| `fp16.rdup8` | 75.8 ± 2.7 | 64.7 | 132.8 | 89.7 | −1174.4 |
| `fp16.t16x16` | 51.3 ± 1.7 | 41.3 | 21.3 | 38.3 | −1263.0 |
| `fp16.walkK` | 123.7 ± 3.9 | 130.0 | 89.5 | 61.7 | 1729.2 |
| `int8.cdup8` | 83.0 ± 3.6 | 85.0 | 14.5 | 31.3 | 90.8 |
| `int8.rdup8` | 59.7 ± 4.9 | 50.8 | 92.7 | 70.0 | 40.1 |
| `int8.t16x16` | 50.9 ± 3.6 | 30.6 | 8.9 | 28.5 | 43.3 |
| `int8.walkK` | 77.8 ± 4.2 | 69.9 | 45.5 | 38.6 | −806.1 |

| model (22 kinds) | rms W | bias W | worst W | bf16 | fp16 | int8 | board-scaled |
|---|---:|---:|---:|---:|---:|---:|---:|
| **RK** | **15.65** | +2.68 | 47.7 | 17.98 | 8.64 | 11.84 | 15.82 |
| E149's S1 (static bits) | 36.07 | −12.08 | 79.8 | 41.26 | 32.16 | 12.80 | 36.64 |
| E149's G0 (density) | 45.72 | +30.74 | 89.3 | 47.78 | 54.66 | 22.77 | 45.37 |
| G1p | 47.98 | +11.72 | 129.0 | 50.17 | 51.47 | 34.70 | 48.26 |
| E149's G1s (K-lag 32) | 49.98 | −21.56 | 97.5 | 55.47 | 47.88 | 26.07 | 50.85 |
| **G1 (E149, frozen)** | **52.35** | +3.24 | 102.4 | 51.92 | 59.11 | 46.35 | 52.89 |
| G4p | 177.59 | +43.49 | 826.8 | 22.90 | 18.91 | 413.84 | 179.77 |
| E149's G4 | 550.04 | +82.49 | 1605.5 | 20.53 | 1211.23 | 442.09 | 556.20 |

- **Where RK misses**: its two worst kinds are the zero stripes, `stripeR0` over-read by 47.7 W and `stripeK0` under-read
  by 24.9 W; without them RK reads 11.2 W rms and G1 49.4 W (`posthoc.txt` §2). Its row term counts a row step between
  a zero row and a value row as full flips, which costs less than that, and its K-lag of 8 sees no gate change in a
  period-2 zero pattern, which costs more than nothing. How zeros move along each direction is the next term to fit.
- **G1 reads high where K neighbours differ and low where rows do**: runs of 8 along K (`cdup8`: no lag-1 flips inside
  a run, so G1 sees almost none) cost 148.2 W where G1 says 50.6, and rows repeated 8 times (`rdup8`) cost 85.2 W where
  G1 says 158.6.
- **The boards**: RK reads 15.7 W on board A (bias −1.7 W) and 17.1 W on board B (+7.3 W); their random bf16 drew 0.964
  and 1.058 of the fit's span, and the board-scaled arm (E149's A2) changes nothing (15.8 W) (`posthoc.txt` §2;
  `score-e162-a100.json` `secondary_board_scale`).
- **E149's 17 held-out kinds** (the seen-kinds arm, no verdict: their watts were public and the designer had seen how a
  ridge row+K form does on them in the disclosed desk run): RK 12.8 W rms, G1 24.7, G4p 15.6, G1p 29.3; the
  checkerboard, G1's worst (214.6 W against 135.9), reads 156.8 with RK (`posthoc.txt` §4).

## Heat

HT1 (registered; no extra GPU time): each blind cell's die reading over its two references, the window's mean
temperature after its 1.5 s settle minus its references' mean, predicted by E149's frozen pooled heat model
(`model-e149.json` `heat.pooled`: τ₁ 0.2 s, τ₂ 31.8 s, 0.116 °C per board W) driven by the session's measured power with
the cell's samples replaced by the reference power plus the pass's zeros offset plus the model's y. The measured
readings run −5.7 to +0.1 °C (the cells are cooler than random-bf16 references). **RK's power gives 1.28 °C rms (bias
+0.80), G1's 3.33 °C (+0.83); the measured power gives 0.69 °C (+0.62)**, so the heat model's own error is about half
of RK's in rms terms (29% of its squared error) and the rest is RK's power error, while G1's is mostly power error (`score-e162-a100.json` `heat_cells`;
`posthoc.txt` §3). These are 5 s windows read in whole degrees and averaged over ~35 samples and four replicates; they
test the fast pole, not the 30 s holds E149 scored. *(Added after verification, C6.)* HT1 retests no heat term. In
E149's frozen linear model a model's cell heat minus the measured-power reading is that model's power error times one
gain, 0.0612 °C per W over these cells (through the origin over the 22 kinds × RK and G1: residual 0.016 °C,
R² 0.99995). RK's 1.28 °C is the heat model's own 0.69 °C combined with 0.96 °C from RK's 15.65 W of power error, and
G1's 3.33 °C the same 0.69 °C with 3.20 °C from G1's 52.35 W: HT1 is BEAT in degrees.

## What this does to predicting power and heat

**Section 11 item 2 ("a GPU measured the same way"), the critic's rank 9: answered for the A100's row direction and,
along K, for "8 or more apart, not 1, 2 or 4"; open for which lag from 8 up and for a later generation** *(corrected
after verification, C1: this said "answered for the A100")*. **Tested and corrected: the operand pairing of the toggle
model.** The ET-SoC-1 model counts bit changes between consecutive operands along K. E162 shows that on an A100
consecutive elements along K are not what costs, that A's rows one apart are (row-lag 1, A over B), and that along K
pairs 8 or more apart cost where pairs 1, 2 or 4 apart do not; whether 8, 16 or 32 apart, the data do not tell
*(corrected after verification, C1: this said "A's consecutive rows and K-steps of 8 are")*. It replaces the pairing
with RK's (row-lag 1, the A − B row asymmetry, and K-lag 8, its stage-1 choice), fitted by ridge. **Out-of-sample
error, power** (22 held-out kinds built to separate pairings, two new boards): **before**, E149's frozen G1 52.4 W rms
(33.8% of the 154.7 W zeros-to-random span; 48.0 W for G1's form refitted on the same data), and the best form frozen
before E162, E149's S1, 36.1 W (23.3%) *(added after verification, C5)*; **after**, RK **15.7 W [9.9, 21.8]** (10.1%), a
resolved gain of 36.7 W [22.1, 50.1] over G1 (20.4 W [9.4, 32.1] over S1, no verdict), stable out of kind (fully nested
12.7-15.4 W by format; 13.1-15.5 W with the column scale recomputed in each fold, C2). On E149's own 17 held-out kinds,
24.7 → 12.8 W (seen kinds, no verdict). **Heat**: no heat term is tested *(corrected after verification, C6)*. A 5 s
cell's die reading from the bits goes 3.33 → 1.28 °C rms, against 0.69 °C from measured power, but through E149's
unchanged linear heat model that is BEAT's power gain at 0.061 °C per W. **Measured**: the prices of row-direction flips
(bf16: sign +19.5, exponent +5.9, mantissa +6.0 W per unit share, A above B) and of K-lag-8 flips (one lag standing for
pairs 8 or more apart, C1), at E149's footing (upper bounds on switching energy by the leakage share E149's C2 named).
**Still open**: zeros' transitions along each direction (the stripes, RK's worst kinds); which K-lag from 8 up (C1); a
later generation under its cap (the L40S, like the L4 in E150, ran every window with its power-cap reason bit set, so no
clock is held, C4); other GEMM libraries and shapes; a lower cap (it needs a host that allows `nvidia-smi -pl`, and his
word).

**For the ET-SoC-1's model**: nothing changes there. The ET-SoC-1's pairing (the micro-op stream along K, PRM 9.4) is
its own, measured on the cards; E162 says the GPU's is different and which counting predicts it.

## Registered against what happened

| rule | registered | E162 | verdict |
|---|---|---|---|
| V0 | ≥ 90% of stage-1 kinds valid on each board | 52 of 52 on both | **HOLDS** |
| W1 | a phase per row costs more than a shared phase, b = 1, 16, 64, all resolved | +44.0 ± 1.7, +38.5 ± 2.2, +48.0 ± 4.0 W | **HOLDS** (expected) |
| W2 | with no row flips, `kS1` costs more than `kS64` | −6.7 ± 2.8 W | **FAILS** (expected) |
| W3 | with no K flips, `rS1` costs more than `rS64` | +60.4 ± 2.6 W | **HOLDS** (registered as a guess) |
| W4 | rows against K at the same values, each format | bf16 +58.9 ± 3.2, fp16 +44.6 ± 3.9, int8 +21.3 ± 3.8 W | **ROW>K** ×3 (expected in bf16) |
| W5 | `drollK` against `rollM` | +27.9 ± 4.6 W | **ROW>K** (expected) |
| W6 | one-sided waves (reported) | K wave A ≈ B (+0.9 ± 2.3 W); row wave A > B (+67.2 ± 2.2 W) | reported |
| R4b | E149's: `sq1` costs more than `sq64` | −10.8 ± 3.3 W | **FAILS** (as in E149) |
| STABLE | (i) nested ≤ 3 × in-sample per format; (ii) pooled nested ≤ G1's form's | 1.38 / 1.77 / 1.31; 14.0 against 67.3 W (with the column scale recomputed in each fold 1.47 / 1.78 / 1.36; 14.7, C2) | **HOLDS** (expected), either way |
| BEAT | rms(RK) ≤ 0.8 rms(G1) and the bootstrap's 95% interval above 0 | 0.299; [+22.1, +50.1] W | **HOLDS** (expected, at about 60%) |
| BEAT_p | the same against G1's form refitted on the same rows | 0.326; [+14.8, +48.5] W | **HOLDS** |
| HT1 | the cell heat with RK's power no worse than with G1's | 1.28 against 3.33 °C (BEAT's power gain through E149's frozen heat model, C6) | **HOLDS** |
| L40S | a size under its cap with a held clock, else the arm stops | none: 0x4 in every sample of every window | **arm stopped** (A1) |

Sources: `model-e162-a100.json` `rules_stage1`, `stable`; `score-e162-a100.json` `rules`; `choice-ls.json`. The L40S's
BEAT_L, STABLE and HT1 were not scored: its arm stopped.

## How it ran

| when (PST, Tue 3 Nov 2026) | what | commit |
|---|---|---|
| 04:05 | `modal billing rates` and the metered total before E162 ($10.39) read | — |
| 04:32:27 | registration committed (pushed 04:32:29, C8), before any GPU call (the smoke's app was created at 04:32:46) | `038db597` |
| 04:32:51-04:35:32 | the declared L40S smoke; plumbing passed at 04:33:02 | — |
| 04:33:50-04:52:00 | A100 stage 1, boards A and B (launched 04:33:45, after the plumbing, using E149's A100 sizes) | — |
| 04:48:57 | A1 (the L40S arm stops; the `choose` slip fixed) and A2 (two stage-2 passes per board) committed (pushed 04:49:00, C8), before any stage-1 data was fetched | `0e8479c9` |
| 04:52-04:54 | stage 1 fetched, reduced, fitted and frozen | — |
| 04:54:02 | the freeze committed (pushed 04:54:05, C8): model and held-out predictions | `54e8f87d` |
| 04:54:25-05:05:14 | A100 stage 2 on two new boards | — |
| 05:05-05:10 | stage 2 reduced and scored; post hoc; this README (pushed 05:11:19) | `c30af4f6` |
| 05:15-05:40 | an independent verification, read only | — |
| 05:45-06:05 | the corrections after verification (C1-C8), desk only | the commit that adds `corrections-numbers.py` |

## Departures, dated

- **A1 (04:48:57, before any L40S stage-1 call)**: the L40S arm stops, by the registered rule. The `choose` code's
  fallback test had an operator-precedence slip (`rsn_or & CAP_BITS == 0`), fixed to the registered text; the outcome is
  the same with either code, since the zeros window carried 0x4 in every sample.
- **A2 (04:48:57, before any stage-2 call and before stage 1 was fetched)**: two stage-2 passes per board instead of one,
  with the L40S's freed budget.
- **The A100's stage 1 was launched before A1** (04:33:45, after the smoke's plumbing had passed); it uses nothing the
  smoke reads.
- **The registration's disclosed desk run, made precise**: in that dry run on E149's committed logs every E149 kind
  entered the pooled fit twice (once as an E149 row and once dressed as a new row), so its 13.8 W on E149's held-out
  kinds is not even a fair post hoc reading. It touched only the seen-kinds arm, which carries no verdict.

## What this cannot say

- RK is a predictor, not the A100's circuit: which operands meet on which wire is set by cuBLAS's kernel and the tensor
  cores' dataflow, which nothing here reads. Row-lag 1 is the row counting that predicts best, chosen on stage 1 and
  confirmed blind; along K the data identify only "8 or more apart, not 1, 2 or 4", since K-lags 8, 16 and 32 predict
  the held-out kinds alike *(corrected after verification, C1: this said "A's rows and K-steps of 8" was the counting
  chosen on stage 1 and confirmed blind)*. A lag of 8 would fit the shape of an MMA fragment (a thread's registers hold
  A at k and k + 8, rows g and g + 8), but that is a hypothesis, not a reading.
- One GPU model, the A100-SXM4, at 1410 MHz only. E162's four boards are 40GB parts; E149's two stage-1 boards, whose
  watts make 89 of RK's 125 fit rows and E149's frozen G1, are one 80GB part (`dbf92f75735f`) and one 40GB part
  (`660a9fe7d69f`), and the seen-kinds arm's watts come from E149's stage-2 boards, again one of each *(corrected after
  verification, C3: this said "A100-SXM4-40GB, four boards here, E149's two")*. One library (cuBLAS through torch
  2.5.1); square K-contiguous operands at E149's sizes (bf16 2048³, fp16 and int8 1024³).
- Watts are NVML's board power over zeros, each window at its own fast-pole temperature (E149's C2), so RK's prices are
  upper bounds on switching energy by about 11-16%.
- The held-out kinds were designed by the same agent that designed the fit set (no independent designer); they were
  registered before any measurement and none was measured anywhere before stage 2.
- The L40S result is one board, one 5 s window per cell, in a rented slot.

## Cost

**Metered $2.28** (`billing.json`: `modal billing report --for today --show-resources --json`, read 05:07 PST, app
`e162-gpu-row-k` only): the L40S smoke $0.09 (`ap-0WUD…`), A100 stage 1 $1.37 (`ap-K8gL…`), A100 stage 2 $0.82
(`ap-wAkT…`). Function-seconds from the Volume's `STARTED`/`DONE` (`ledger.json`): 3,615 s, $2.26 at the registered
rates. Projected at registration $4.24 (two L40S stages included), about $2.82 after A1 and A2; the timeouts capped what
could still run at $3.74; E162's cap $6, its stop $5. **The owner's $20 for GPU checks: E135 $3.62 + E149 $4.48 + E150
$2.29 + E162 $2.28 = $12.67** (the ceiling for this round was $16.39). No container is left running; the Volume
`e162-gpu-row-k` (about 2 MB, every log committed here) remains.

## Files

| path | what |
|---|---|
| `logs/<run>/<unit>/` | every run as the Volume holds it: `steps/NNN_<label>.json.gz`, `samples/NNN.jsonl.gz` (every 100 ms NVML sample), `features-<set>.json.gz` (each kind's operand-bit features and sha256), `plan.json`, `STARTED`, `DONE`; runs `e162-20261103-smoke` (L40S), `-a1` (A100 stage 1), `-a2` (A100 stage 2) |
| `choice-ls.json` | the L40S smoke's rule and every size's readings (`analyze_e162.py choose`) |
| `reduce-a1.json`, `.txt`; `reduce-a2.json`, `.txt` | the two stages' windows reduced (`analyze_e162.py reduce`) |
| `model-e162-a100.json` | **the freeze**: RK (scan, coefficients, nested error), G1p, G4p, STABLE, the session scale, the pairing rules, the checks |
| `predictions-e162-a100.json` | **the frozen predictions**: every model's, for the 22 held-out kinds and for E149's 17 held-out kinds |
| `score-e162-a100.json`, `.txt` | the blind scores, BEAT, BEAT_p, HT1 and the heat cells, the board-scaled and seen-kinds arms (`analyze_e162.py score`) |
| `summary.md` | the tables, printed by `tools/gpu/e162/summarize_e162.py` from the JSON files |
| `posthoc.txt`, `posthoc.json` | post hoc readings, no verdicts (`tools/gpu/e162/posthoc_e162.py`): intervals on the blind rms, the stripes, per board, the heat cells per kind, the seen-kinds arm per kind, stage 1 model-free |
| `ledger.json`, `billing.json` | function-seconds per call (`ledger_e162.py`) and the metered bill by app and resource |
| `corrections-numbers.py`, `corrections-numbers.txt` | every number of the corrections after verification, from committed files only (post hoc, no verdict) |
| `pushes-e162.json` | E162's four commits: git's commit time and GitHub's ref-update time for `main` (C8) |

## Corrections after verification

Tue 3 Nov 2026, about 06:05 PST, desk only: no GPU call, no Modal app started, nothing re-run, no device command. An
independent verifier (05:15-05:40 PST) re-derived E162 with its own reducer, scorer and heat filter from the committed
raw 100 ms samples, read the bill (`modal billing report`, `app list`, `container list`), checked the plans that ran
against the registered code with a stub `modal` module, and re-ran the freeze to 3e-14. It found one major and five
minor faults (C1-C6); correcting them found two slips more (C7, C8). None changes a measured number, a frozen file, a
prediction, a rule or a verdict: `model-e162-a100.json`, `predictions-e162-a100.json`, `score-e162-a100.json`, the
reductions, the logs, `ledger.json` and `billing.json` are unchanged, and so is the registration (`E162.md` gains only
a dated note under its amendments, on C2 and C4). Every number below is printed by `corrections-numbers.py` into
`corrections-numbers.txt` from committed files only; the refits in C1 and C2 are post hoc and carry no verdict.

- **C1 (major), the K-lag.** This README and the lane's result presented "A's consecutive rows and K-steps of 8" as the
  pairing an A100 pays for, "chosen on stage 1 and confirmed blind". The row-lag is identified; the K-lag is not.
  - **Row-lag 1**: chosen on stage 1, and blind the same form refitted at K-lag 8 with row-lag 2, 4, 8, 16 or 32 reads
    19.2-37.9 W against row-lag 1's 15.65 W.
  - **Along K, stage 1**: the scan carries no interval. (8, 1) 12.40 W against (4, 1) 13.15, (32, 1) 13.34 and
    (2, 1) 13.47; a paired bootstrap over the 125 rows (approximate) does not resolve lag 8 from 4, 32 or 2, only from
    16 (+1.34 [+0.45, +2.30] W) and 1. In fp16 lag 8 ranks fourth (13.09 W against lag 4's 11.87).
  - **Along K, blind** (RK's registered per-pairing procedure on the frozen rows, at row-lag 1, scored on the 22
    held-out kinds): K-lag 8 15.65 W, 16 15.83, 32 16.20, 4 17.79, 2 20.27, 1 24.90. Against lag 8, by the registered
    paired bootstrap: 16 +0.18 [−2.23, +3.78] W and 32 +0.55 [−3.98, +6.27], not resolved; 4 +2.14 [+0.96, +3.81],
    2 +4.62 [+1.94, +8.13] and 1 +9.25 [+4.21, +14.96], each resolved worse. Of all 36 pairings the best three blind
    are (8, 1), (16, 1) and (32, 1).
  - **So what is identified** is A's rows one apart (A over B), and along K pairs 8 or more apart rather than 1, 2 or 4
    apart; stage 1's waves put the K cost 8-16 apart (blocks of 8 and 16 cost 51-52 W, of 1-4 24-29 W, of 32 and 64
    36 W). Which lag from 8 up a model should count is open; K-lag 8 is RK's stage-1 choice. No W rule tests a K-lag:
    W1 and W3-W6 test the row direction and rows against K.
  - Corrected in Results, the summary table, the stage-1 bullets, the model section, "What this does" and "What this
    cannot say".
- **C2, the LOKO was exact only for a column scale held at all the rows.** E162.md chooses λ by "exact closed-form"
  LOKO on "columns scaled to unit RMS over the training rows"; the code's closed form (`ridge_loo`, whose docstring
  says so) holds the scale at all the rows, the left-out one included. With the scale recomputed on each fold's
  training rows (a vectorized exact refit, equal to a brute-force refit loop to better than 1e-8 W):
  - the choice is the same, (8, 1) with λ 0.03 / 0.1 / 0.3, so the frozen model and every prediction are what the
    registered text's procedure gives, and BEAT is unchanged;
  - LOO at the choice reads 12.42 / 14.92 / 12.00 W (bf16 / fp16 / int8) against the closed form's 12.36 / 13.09 /
    11.71, and the fully nested errors 14.89 / 15.52 / 13.14 W, pooled 14.71, against the frozen 13.94 / 15.40 /
    12.66 and 14.03. STABLE still holds: 1.47 / 1.78 / 1.36 ≤ 3, and 14.71 ≤ 67.29 W;
  - the scan reads (8, 1) 12.90 W, (32, 1) 13.67, (4, 1) 13.73, (2, 1) 13.99, (16, 1) 14.77 and (1, 1) 16.84, with
    (8, 4) 16.45 and (8, 2) 16.46 below (1, 1), so "every pairing with a row-lag other than 1 does worse than every one
    with row-lag 1" holds in the closed form only;
  - the nested folds chose (8, 1) in 73 of 75 bf16 folds, (4, 1) and (32, 1) once each (closed form: 74 and one (4, 1)),
    in 24 of 26 fp16 folds, (32, 1) and (32, 4) once each (closed form: all 26), and in all 24 int8 folds;
  - RK's band, 1.645 × the nested rms, would be 24.5 / 25.5 / 21.6 W against the frozen 22.9 / 25.3 / 20.8; 20 of the
    22 held-out kinds fall inside either.
- **C3, the boards.** "What this cannot say" read "A100-SXM4-40GB, four boards here, E149's two for the fit's E149
  rows". E162's four boards are A100-SXM4-40GB (`ac97f0c6a6ae`, `83190b6e35b9`; `d31f897269bd`, `80d5c1565177`); E149's
  stage-1 unit A, `dbf92f75735f`, is an A100-SXM4-80GB (81,920 MiB) and unit B, `660a9fe7d69f`, a 40GB part (E149's
  D4). Their watts make 89 of RK's 125 fit rows and E149's frozen G1. E149's stage-2 boards, the seen-kinds arm's, are
  also one 80GB (`8a5db1cd3afd`) and one 40GB part (`5d6c11c9a424`).
- **C4, the L40S wording.** The Results paragraph said it "runs these GEMMs at its power controller's limit", the
  summary table "runs at its power limit too", the L40S section that its power "reads its power controller, not the
  data" and that the data move its clock "instead"; the lane's result added "every window at its power cap" and
  "random data slows its clock by 15-19% instead of raising its power". From `choice-ls.json`: the SW power-cap reason
  bit is set in every sample of every window, but zeros draw 209.7-240.3 W, 60-69% of the 350 W limit; random draws
  321.4-349.6 W, 109-123 W more than zeros at every size, at an 8.6-19.8% lower mean SM clock; its TFLOPS deficit is
  14.7% at 2048³ and 19.2% at 4096³, 2.1% at 1024³, and at 1536³ and 3072³ random ran 2.0% and 3.6% faster (one 5 s
  window per cell). The registered stop stands: no clock is held. A1's own sentence, "Its power reads its power
  controller, not the data", gets a dated note in `E162.md`.
- **C5, the best form before E162.** The before/after named only E149's frozen G1 (52.35 W) and G1's form refitted
  (47.98 W). The best form frozen before E162 on these kinds is E149's S1, static bits, at 36.07 W (23.3% of the
  span); RK beats it by 20.42 W [9.40, 32.09] (paired bootstrap, no verdict). BEAT stays registered against G1, as the
  critic asked. E149's other frozen forms read 45.72 (G0), 49.98 (G1s), 550.04 (G4) and 2,035.36 W (G3).
- **C6, HT1 tests no heat term.** With E149's frozen linear heat model, a model's cell heat minus the measured-power
  reading is that model's power error times one gain: 0.0612 °C per W over these 5 s cells (through the origin over the
  22 kinds × RK and G1: residual 0.016 °C, R² 0.99995). RK's 1.276 °C is the heat model's own 0.694 °C (bias +0.62)
  with 0.959 °C from RK's power error; G1's 3.334 °C the same 0.694 °C with 3.204 °C from G1's. So 3.33 → 1.28 °C is
  BEAT's power gain in degrees, on the heat model's 0.69 °C floor; the heat model itself is not retested. Corrected
  in Results, the summary table, Heat, the registered table and "What this does".
- **C7, cosmetic.** Five stage-1 SEs were rounded twice from `reduce-a1.txt`'s two decimals: `bf16.kS1` 0.846 and
  `bf16.kS8` 0.849 (printed 0.9, now 0.8), `bf16.rS1` 2.547 (2.6, now 2.5), `bf16.rowcA_colcB` 4.347 (4.4, now 4.3) and
  int8 random 2.749 (2.8, now 2.7); `summary.md` had them right. `score-e162-a100.txt` prints `inside_band_RK None`
  where `score-e162-a100.json` has 20 of 22; the frozen score files are left as they are.
- **C8, times.** The header and "How it ran" gave commit times as push times. GitHub's ref updates for `main`
  (`pushes-e162.json`): the registration pushed 04:32:29 (committed 04:32:27), the amendments 04:49:00 (04:48:57), the
  freeze 04:54:05 (04:54:02), the results 05:11:19 (05:11:04). The order holds: the registration's push precedes the
  smoke's app (04:32:46) and the freeze's push precedes stage 2's first call (04:54:25).
