# E78 — the kinds-of-numbers energy matrix (Q130, aifoundry3, 2026-10-31)

*Pre-registered in [`tools/claims-v3/kinds/E78.md`](../../../../tools/claims-v3/kinds/E78.md) with
[`predictions-e78.json`](../../../../tools/claims-v3/kinds/predictions-e78.json), committed as **`cfd94285`** at
**12:45:37 PDT**, with amendment A1 (plumbing only) as **`09c6e29b`** at **12:48:23 PDT** — 7 min 26 s before the
card was claimed in `#community-lab` (12:55:49 PDT, message `1566178906489356342`) and 9 min 10 s before the first
measured pass began (12:57:33 PDT, pass 7810's `block_begin`). Card runs 2026-10-31 **12:56:13–14:03:25 PDT** on
**aifoundry3 card 0 only**: a read-only `ettelem config`, the smoke (12:56:34–12:57:14), six passes 7810–7815
(12:57:33–14:02:54) and a closing read-only `ettelem config`. The card's governor is latched at 600 MHz by its
boot-time TDP of 0, so every number here is a **600 MHz, 521.7 mV** number. 64.8 card-minutes in blocks of the
registered 90 (expected 66). No knob was written. **Released at 14:15:49 PDT** by an edit of the same post, 49 s
after this directory's first commit (`410c56f6`, 14:15:00), read back as `<ai> Claude says: using aifoundry3 for
1.5 h, until ~14:30 PDT doc — released (edited)`. The words "for 1.5 h, until ~14:30 PDT" were added to the post at
13:15 PDT by an edit this lane did not make; the release kept every word.*

> **What this is.** One protocol, one card, one clock, and **all 51 kinds** of
> [`kinds.json`](../../../../tools/claims-v3/kinds/kinds.json) — 18 fp32, 17 fp16, 16 int8, every tile Q130(b) replayed
> in the RTL and Q130(c) predicted — so the blog's kinds table has a measured **switching power**, **energy per
> operation** and **heat** cell for every format × kind, with 95% intervals from six independent passes, and both
> frozen models are scored against it.

## Results

**All six passes ran and all six were kept; 388 of 390 planned runs ran and 388 of 388 passed every per-run gate**
(two were skipped before launch by the registered launch-reading rule; § Registered against what happened). Not one
idle bracket was invalid: the new quiet rule worked (in E79, 109 of 480 brackets began before the previous process
had ended). Leakage
slope (the registered `auto` primary) 0.1994 W/°C over 250 runs; idle 25.911 ± 0.012 W; cycles per op **546.001 /
546.001 / 318.000** for fp32 / fp16 / int8 on every kind; duty 0.9959–0.9967 on every kind
([`e78.json`](e78.json) `leak`, `idle_level`, `cycles_per_op`, `checks.duty`).

**Registered tally: 28 pass, 2 fail, 0 inconclusive, 0 not scored (30 verdicts)** — the same 28 / 2 at both
registered leakage arms (E71's 0.3803 W/°C and 0), and no single verdict moves between arms
([`scored.json`](scored.json) `tally`, `arms`). The two failures are both **E78-R2**, the accuracy of the frozen
empirical model Q130(c): rms **2.270 W** against a 2.0 W bound in fp32, **1.054 W** against 1.0 W in int8 (fp16
passes at 1.757 W). Q130(c) ranks every format right (E78-R1, ρ = 0.941 / 0.948 / 0.867 ≥ 0.80). Scored as its own
README says, Q130(c) passes 8 of its 10 pass/fail verdicts: **C-R1 fp32 fails** (0.533 of the out-of-sample fp32
kinds inside the frozen 95%, need 0.70; R1-A1's wider interval gives 0.733) and **C-R2 int8 fails** (ρ 0.867, need
0.90). **C-R9 selects the gate arm**, Q130(c)'s primary: one operand all zero costs 0.616 W in fp32 (0.528 W in
pass 7810, where it ran first), against the bus arm's 5.19 W.

**1. The matrix.** Switching power over the type's own zeros (**D**, paired, the zeros interpolated in time), over
the idle bracket (**S**), and energy per operation, for every cell (the full tables are below; one "op" is one
minion's 16 × 16 TensorFMA, 4,096 / 8,192 / 16,384 multiply-adds):

| | random data (D over zeros) | a constant (1.0 / 0x01) | all zeros, over idle (S) | random data, energy over idle |
|---|---|---|---|---|
| **fp32** | **24.725 ± 0.082 W** | 8.257 ± 0.221 W | 1.986 ± 0.059 W | **5.816 ± 0.012 pJ per MAC** (2.908 pJ per flop; 23,823 ± 50 pJ per op) |
| **fp16** | **22.162 ± 0.054 W** | 8.448 ± 0.082 W | 1.987 ± 0.052 W | **2.625 ± 0.003 pJ per MAC** (1.312 pJ per flop; 21,504 ± 27 pJ per op) |
| **int8** | **7.056 ± 0.059 W** | 1.561 ± 0.069 W | 2.605 ± 0.028 W | **0.306 ± 0.003 pJ per MAC** (5,010 ± 42 pJ per op) |

([`e78.json`](e78.json) `items.<type>.<kind>.D`, `.S`, `.pj_mac_S`, `.pj_flop_S`, `.pj_op_S`; ± is the 95% interval
over six passes.) A random fp32 multiply-add costs 2.2× a random fp16 one and 19× a random int8 one, per MAC.

**2. Which kinds are cheap, and why.** Three things set a kind's power, and a fourth barely moves it:

- **The zero gate.** Every kind under 1.5 W over its type's zeros is one the zero gate catches on 82–100% of
  lane-cycles: zeros, either operand all zero, 90% element- or word-sparse. **One operand all zero costs 0.62–0.81 W
  in fp32 and 0.66–0.78 W in fp16, 2.5–3.5% of random data**, and 0.31–0.50 W in int8, 4.3–7.1% (E78-R3a, every
  cell ≤ 0.15 at 95%). The gate switches the lane off whichever side is zero. In fp32 and fp16 the other operand's
  bus keeps moving 27,920–55,806 bits an op, and if all of the residual is that bus, it is **12.5–20.9 fJ per
  moving bus bit** (derived below, not registered). So a gated lane pays almost none of what its moving operand
  costs an ungated one: 0.6 W where Q130(c)'s bus arm said 5.2 W (C-R9).
- **A lane switched on with nothing changing.** A constant (1.0, π, −1.0) costs **8.1–8.5 W** in fp32 and
  **8.4 W** in fp16 — 0.33× and 0.38× of random data — and only **1.56–1.63 W** in int8, 0.22× of random int8 and
  a fifth of the float constant. Nothing in the operands toggles; the lane is clocked and its accumulator still
  walks. Static ones are free: int8 −1 (every bit set) against +1 (one bit a byte) is **+0.067 W [−0.050, +0.184]**
  (E78-R3f PASS); fp16 −0.067 W [−0.221, +0.087]; fp32 −0.113 W [−0.521, +0.295] (inconclusive, reported only).
- **Bits that change.** Everything above the constant is operand bits changing from one multiply-add to the next:
  16.5 W in fp32, 13.7 W in fp16, 5.5 W in int8. **Magnitude does not matter** (σ = 2⁻¹⁰ and 2¹⁰ against σ = 1:
  1.002× and 0.999×, E78-R3c). **Mantissa bits do**: zeroing the low 13 mantissa bits (`fp16grid`) saves 5.1 W,
  the low 16 (`bf16trunc`) 6.6 W, a zero mantissa and sign (`pow2`) 10.7 W; small integers −8..7 save 10.6 W (fp32) and
  5.2 W (fp16); an e4m3 grid held in fp16 saves 4.1 W. A sign and exponent held to one range (`uniform01`) saves
  only 2.1 W (fp32) and 2.7 W (fp16). In int8, ±64 (`highbit`, one magnitude bit and the sign changing) is
  0.458× random, ternary 0.735×, the int4 range 0.851×, the positive half 0.875×.
- **Order is a small lever.** The same words sorted into the stream order of least change move 23–27% fewer operand
  bits but cost only **5.4% / 6.4% / 6.6% less** (fp32 / fp16 / int8: 1.341, 1.414 and 0.468 W; E78-R3e PASS in all
  three; `scored.json` `rules.E78-R3e.cells[].power_ratio`).

**3. A zero is worth most in fp32 and least in int8.** The gate tests a whole 32-bit word, so half the *elements*
zero is 0.295× random power in fp32 (an element is a word), **0.595×** in fp16 and **0.774×** in int8 (E78-R3h
PASS: fp16 − fp32 0.300 [0.276, 0.325], int8 − fp16 0.179 [0.163, 0.194]). Half the *words* zero brings it back:
0.318× in fp16 and 0.445× in int8 (E78-R3i: sparse50 − wsparse50 = 6.138 and 2.322 W). Where the gate acts, the
lane-cycles it leaves on (1 − kinds.json's `gated_lane_frac`) track the power: 0.226 and 0.586 left on against
0.295× and 0.595× measured for fp32 and fp16 `sparse50`, 0.240 and 0.356 against 0.318× and 0.445× for fp16 and int8
`wsparse50`. int8's `sparse50` gates only 7% of its lane-cycles, and its saving follows its operand bits instead
(53,480 against 69,312 bus bits an op, 0.772×, measured 0.774×; int8's bus counts are provisional). fp16 has **no
pair gate**: one zero half in every two-term pair costs 0.908× random [0.883, 0.933] (E78-R3g PASS).

**4. Speed and heat.** At a pinned clock the kind of number changes **power and heat, never speed**: all 51 kinds
ran at 546.001 / 546.001 / 318.000 cycles per op with duty 0.996–0.997, so a matmul's speed depends on its data only
where a governor turns power or heat into clock (E64, E80 on aifoundry2). Heat follows switching power: over the 2 s
window from a 58 °C launch the die reading rises **3.16 °C** on random fp32, **2.80 °C** on fp16, **1.01 °C** on
int8 and 0.06 °C on fp32 zeros, 0.08–0.13 °C per watt of S (`items.<…>.dT_win`).

**5. Both frozen models, against the card.** The empirical model (Q130(c)) gets the **order** of the kinds right
but overstates what is left after truncating mantissas by 4–5 W (`bf16trunc` predicted 23.26 W, measured 18.14 W;
`fp16grid` 23.95 W against 19.62 W): its saturating law puts a full and a truncated mantissa near the same ceiling
(Q130(c)'s own A1 found that cap against E70's mantissa rungs), so it predicts a short mantissa saves 1 W where the
card says a quarter of the power. It also prices int8's constant at 0.571 W against 1.561 W measured
(as E79 had already found post-data, 1.834 W). The RTL toggle predictor (Q130(b) r2) ranks the kinds best (ρ =
0.974 / 0.978 in fp32 / fp16) and gets the size of the mantissa steps nearer (predicted 2.30 W and 6.88 W for
`fp16grid − bf16trunc` and `randn − fp16grid`, measured 1.49 and 5.10 W, against Q130(c)'s 0.69 and 0.26 W), but
its int8 scale is off by an order of magnitude: it puts int8 ones 15.0 W above fp32 zeros against 2.17 W measured
(mean error +6.2 to +6.8 W over the 16 int8 kinds). Its `g` re-fitted per format on E78's anchors is **1.023** of
fp32's in fp16 (r2's E64 value 0.95 ± 0.10) and **0.110** in int8 (r2's 0.037 ± 0.048); and int8 zeros sit **0.612
± 0.053 W** above fp32 zeros (E64: 0.68 ± 0.51 W; r2 predicts 0.00).

**6. Replication.** E67's anchors on this card four days ago reproduce: fp32 ones 8.257 W (E67 8.217), π 8.470 W
(8.496), random 24.725 W (24.659), all inside ±0.6 / ±0.6 / ±1.0 W (E78-R4). So do E79's constant-to-zeros steps
from this morning, with E78's different constants: fp16 8.448 W (8.736 ± 0.8), int8 1.561 W (1.834 ± 0.6). The
host's built-in π and the same bytes read from a file give the same power: −0.067 ± 0.104 W (E78-R4, ± 0.25 W).

## The tables — aifoundry3 card 0, 600 MHz, 521.7 mV, six passes

D = switching power over the type's own zeros, paired within the pass (the three zeros runs interpolated in time); S = over the run's own idle bracket [t0 − 1.2, t0 − 0.2) s; pJ/op = 10¹² × W / R at the measured op rate R (one op = one minion's 16 × 16 TensorFMA, 4,096 / 8,192 / 16,384 MACs); ΔT = the die reading's mean over the window [t0 + 1, t0 + 3) s minus the 58 °C launch reading; rail D = the minion rail, deconvolved (τ 0.95 s), over the type's zeros — reported beside the board, never instead of it. ± is the 95% interval t(0.975, n − 1) × SE over passes. Sorted by D. Source: [`e78.json`](e78.json) › `items`.

### fp32

| kind | gated lane-cycles | D over own zeros (W) | ±95% | S over idle (W) | ±95% | pJ/op (S) | ±95% | pJ/MAC (S) | pJ/flop (S) | pJ/op (D) | ±95% | ΔT (°C) | rail D (W) | passes |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| randn_small | 0.000 | 24.764 | 0.463 | 26.661 | 0.472 | 23786 | 429 | 5.807 | 2.904 | 22093 | 421 | 3.16 | 19.986 | 6 |
| randn | 0.000 | 24.725 | 0.082 | 26.701 | 0.054 | 23823 | 50 | 5.816 | 2.908 | 22060 | 76 | 3.16 | 19.794 | 6 |
| randn_large | 0.000 | 24.711 | 0.084 | 26.657 | 0.096 | 23779 | 82 | 5.806 | 2.903 | 22044 | 77 | 3.02 | 19.780 | 6 |
| randn_sorted | 0.000 | 23.384 | 0.376 | 25.378 | 0.362 | 22639 | 319 | 5.527 | 2.764 | 20861 | 332 | 2.99 | 18.956 | 6 |
| uniform01 | 0.000 | 22.646 | 0.093 | 24.636 | 0.055 | 21975 | 43 | 5.365 | 2.683 | 20201 | 81 | 2.87 | 18.151 | 6 |
| fp16grid | 0.000 | 19.624 | 0.065 | 21.546 | 0.092 | 19224 | 85 | 4.693 | 2.347 | 17509 | 61 | 2.61 | 15.990 | 6 |
| bf16trunc | 0.000 | 18.136 | 0.046 | 20.144 | 0.082 | 17969 | 75 | 4.387 | 2.193 | 16178 | 43 | 2.38 | 14.818 | 6 |
| smallint | 0.118 | 14.079 | 0.058 | 16.023 | 0.132 | 14296 | 118 | 3.490 | 1.745 | 12562 | 52 | 1.98 | 11.577 | 6 |
| pow2 | 0.000 | 13.985 | 0.159 | 15.984 | 0.218 | 14258 | 193 | 3.481 | 1.741 | 12475 | 139 | 2.00 | 11.472 | 6 |
| nn_like | 0.508 | 13.036 | 0.066 | 15.034 | 0.057 | 13413 | 51 | 3.275 | 1.637 | 11630 | 61 | 1.93 | 10.737 | 6 |
| pi | 0.000 | 8.470 | 0.113 | 10.397 | 0.152 | 9274 | 136 | 2.264 | 1.132 | 7556 | 100 | 1.16 | 7.131 | 6 |
| anchor_pi (the built-in pi tie) | 0.000 | 8.360 | 0.072 | 10.398 | 0.080 | 9277 | 72 | 2.265 | 1.132 | 7459 | 64 | 0.81 | 7.141 | 6 |
| ones | 0.000 | 8.257 | 0.221 | 10.288 | 0.208 | 9179 | 184 | 2.241 | 1.121 | 7366 | 197 | 1.20 | 7.048 | 6 |
| neg_ones | 0.000 | 8.143 | 0.408 | 10.116 | 0.435 | 9025 | 386 | 2.203 | 1.102 | 7264 | 363 | 1.08 | 7.045 | 6 |
| sparse50 | 0.774 | 7.302 | 0.063 | 9.243 | 0.147 | 8245 | 134 | 2.013 | 1.006 | 6514 | 55 | 1.00 | 6.149 | 6 |
| a_zeros_b_randn | 1.000 | 0.810 | 0.065 | 2.839 | 0.039 | 2533 | 35 | 0.618 | 0.309 | 723 | 58 | 0.17 | 0.687 | 6 |
| a_randn_b_zeros | 1.000 | 0.616 | 0.122 | 2.574 | 0.169 | 2295 | 151 | 0.560 | 0.280 | 550 | 109 | -0.08 | 0.552 | 6 |
| sparse90 | 0.992 | 0.577 | 0.073 | 2.509 | 0.138 | 2238 | 123 | 0.546 | 0.273 | 515 | 65 | 0.13 | 0.499 | 6 |
| zeros | 1.000 | 0.000 | 0.000 | 1.986 | 0.059 | 1772 | 53 | 0.433 | 0.216 | 0 | 0 | 0.06 | 0.000 | 6 |

fp32 zeros over idle (its zero-data level): S = 1.986 ± 0.059 W, D32 = 0.000 ± 0.000 W.

### fp16

| kind | gated lane-cycles | D over own zeros (W) | ±95% | S over idle (W) | ±95% | pJ/op (S) | ±95% | pJ/MAC (S) | pJ/flop (S) | pJ/op (D) | ±95% | ΔT (°C) | rail D (W) | passes |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| randn_small | 0.000 | 22.209 | 0.086 | 24.131 | 0.092 | 21528 | 80 | 2.628 | 1.314 | 19813 | 74 | 2.82 | 18.046 | 6 |
| randn | 0.000 | 22.162 | 0.054 | 24.102 | 0.030 | 21504 | 27 | 2.625 | 1.312 | 19773 | 50 | 2.80 | 17.789 | 6 |
| randn_sorted | 0.000 | 20.748 | 0.426 | 22.695 | 0.415 | 20244 | 367 | 2.471 | 1.236 | 18507 | 374 | 2.69 | 17.053 | 6 |
| pair_half_zero | 0.000 | 20.122 | 0.569 | 22.091 | 0.542 | 19707 | 481 | 2.406 | 1.203 | 17951 | 505 | 2.55 | 16.535 | 6 |
| uniform01 | 0.000 | 19.426 | 0.086 | 21.371 | 0.109 | 19064 | 96 | 2.327 | 1.164 | 17328 | 77 | 2.60 | 15.775 | 6 |
| fp8grid | 0.000 | 18.052 | 0.126 | 19.978 | 0.090 | 17823 | 79 | 2.176 | 1.088 | 16105 | 113 | 2.29 | 14.731 | 6 |
| nn_like | 0.195 | 17.602 | 0.118 | 19.480 | 0.226 | 17383 | 201 | 2.122 | 1.061 | 15707 | 105 | 2.23 | 14.378 | 6 |
| smallint | 0.004 | 17.000 | 0.302 | 18.926 | 0.235 | 16883 | 215 | 2.061 | 1.030 | 15166 | 274 | 2.25 | 14.056 | 6 |
| sparse50 | 0.414 | 13.196 | 0.540 | 15.220 | 0.575 | 13576 | 510 | 1.657 | 0.829 | 11771 | 479 | 1.83 | 11.104 | 6 |
| ones | 0.000 | 8.448 | 0.082 | 10.376 | 0.081 | 9256 | 75 | 1.130 | 0.565 | 7536 | 74 | 1.09 | 7.111 | 6 |
| neg_ones | 0.000 | 8.382 | 0.133 | 10.355 | 0.103 | 9239 | 92 | 1.128 | 0.564 | 7478 | 119 | 1.17 | 7.033 | 6 |
| wsparse50 | 0.760 | 7.058 | 0.035 | 9.090 | 0.091 | 8109 | 83 | 0.990 | 0.495 | 6295 | 32 | 1.00 | 5.965 | 6 |
| sparse90 | 0.961 | 1.410 | 0.113 | 3.380 | 0.086 | 3015 | 76 | 0.368 | 0.184 | 1258 | 101 | 0.37 | 1.208 | 6 |
| a_zeros_b_randn | 1.000 | 0.782 | 0.063 | 2.713 | 0.054 | 2420 | 48 | 0.295 | 0.148 | 698 | 57 | 0.53 | 0.630 | 6 |
| wsparse90 | 0.990 | 0.743 | 0.111 | 2.643 | 0.109 | 2358 | 98 | 0.288 | 0.144 | 663 | 99 | 0.27 | 0.592 | 6 |
| a_randn_b_zeros | 1.000 | 0.659 | 0.080 | 2.669 | 0.085 | 2381 | 75 | 0.291 | 0.145 | 588 | 72 | 0.21 | 0.558 | 6 |
| zeros | 1.000 | 0.000 | 0.000 | 1.987 | 0.052 | 1773 | 46 | 0.216 | 0.108 | 0 | 0 | -0.06 | 0.000 | 6 |

fp16 zeros over idle (its zero-data level): S = 1.987 ± 0.052 W, D32 = -0.009 ± 0.031 W.

### int8

| kind | gated lane-cycles | D over own zeros (W) | ±95% | S over idle (W) | ±95% | pJ/op (S) | ±95% | pJ/MAC (S) | pJ/op (D) | ±95% | ΔT (°C) | rail D (W) | passes |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| full | 0.000 | 7.056 | 0.059 | 9.648 | 0.081 | 5010 | 42 | 0.306 | 3664 | 30 | 1.01 | 5.943 | 6 |
| gauss_q | 0.000 | 6.598 | 0.069 | 9.161 | 0.135 | 4757 | 69 | 0.290 | 3426 | 35 | 1.00 | 5.548 | 6 |
| sorted | 0.000 | 6.588 | 0.073 | 9.170 | 0.118 | 4763 | 61 | 0.291 | 3422 | 37 | 1.00 | 5.500 | 6 |
| pos | 0.000 | 6.171 | 0.206 | 8.733 | 0.207 | 4536 | 108 | 0.277 | 3205 | 107 | 1.00 | 5.239 | 6 |
| smallint | 0.000 | 6.003 | 0.142 | 8.628 | 0.096 | 4481 | 51 | 0.273 | 3117 | 75 | 1.00 | 5.118 | 6 |
| sparse50 | 0.070 | 5.463 | 0.146 | 8.061 | 0.126 | 4187 | 66 | 0.256 | 2838 | 76 | 1.00 | 4.593 | 6 |
| ternary | 0.008 | 5.186 | 0.051 | 7.727 | 0.097 | 4013 | 50 | 0.245 | 2693 | 26 | 1.00 | 4.371 | 6 |
| highbit | 0.000 | 3.233 | 0.036 | 5.853 | 0.068 | 3039 | 35 | 0.186 | 1679 | 19 | 0.83 | 2.746 | 6 |
| wsparse50 | 0.644 | 3.142 | 0.056 | 5.743 | 0.088 | 2983 | 46 | 0.182 | 1632 | 29 | 0.83 | 2.710 | 6 |
| neg_ones | 0.000 | 1.628 | 0.169 | 4.176 | 0.134 | 2169 | 69 | 0.132 | 846 | 88 | 0.81 | 1.448 | 6 |
| ones | 0.000 | 1.561 | 0.069 | 4.146 | 0.078 | 2153 | 40 | 0.131 | 811 | 36 | 1.00 | 1.356 | 6 |
| sparse90 | 0.822 | 1.145 | 0.057 | 3.763 | 0.083 | 1955 | 44 | 0.119 | 595 | 29 | 0.83 | 0.949 | 6 |
| wsparse90 | 0.980 | 0.538 | 0.051 | 3.079 | 0.069 | 1599 | 36 | 0.098 | 280 | 27 | 0.37 | 0.454 | 6 |
| a_full_b_zeros | 1.000 | 0.497 | 0.085 | 3.115 | 0.034 | 1618 | 18 | 0.099 | 258 | 44 | 0.33 | 0.391 | 6 |
| a_zeros_b_full | 1.000 | 0.305 | 0.070 | 2.900 | 0.062 | 1506 | 32 | 0.092 | 159 | 37 | 0.48 | 0.253 | 6 |
| zeros | 1.000 | 0.000 | 0.000 | 2.605 | 0.028 | 1353 | 15 | 0.083 | 0 | 0 | 0.22 | 0.000 | 6 |

int8 zeros over idle (its zero-data level): S = 2.605 ± 0.028 W, D32 = 0.612 ± 0.053 W.

### Predicted against measured: Q130(c) (frozen 2bbe03dd + A1 320f3fdd) on D

| cell | measured D (W) | ±95% | Q130(c) predicted (W) | frozen 95% | inside | A1 out-of-sample |
|---|---|---|---|---|---|---|
| fp32/randn_small | 24.764 | 0.463 | 24.452 | [20.52, 28.38] | yes | yes |
| fp32/randn | 24.725 | 0.082 | 24.210 | [20.34, 28.08] | yes | no |
| fp32/randn_large | 24.711 | 0.084 | 24.488 | [20.55, 28.42] | yes | yes |
| fp32/randn_sorted | 23.384 | 0.376 | 22.765 | [19.24, 26.29] | yes | yes |
| fp32/uniform01 | 22.646 | 0.093 | 20.365 | [17.42, 23.31] | yes | yes |
| fp32/fp16grid | 19.624 | 0.065 | 23.953 | [20.14, 27.76] | no | yes |
| fp32/bf16trunc | 18.136 | 0.046 | 23.260 | [19.62, 26.90] | no | yes |
| fp32/smallint | 14.079 | 0.058 | 17.395 | [14.91, 19.88] | no | yes |
| fp32/pow2 | 13.985 | 0.159 | 13.194 | [11.93, 14.46] | yes | yes |
| fp32/nn_like | 13.036 | 0.066 | 16.005 | [13.04, 18.97] | no | yes |
| fp32/pi | 8.470 | 0.113 | 8.555 | [7.99, 9.12] | yes | no |
| fp32/ones | 8.257 | 0.221 | 8.555 | [7.99, 9.12] | yes | yes |
| fp32/neg_ones | 8.143 | 0.408 | 8.555 | [7.99, 9.12] | yes | yes |
| fp32/sparse50 | 7.302 | 0.063 | 9.500 | [7.58, 11.42] | no | yes |
| fp32/a_zeros_b_randn | 0.810 | 0.065 | 0.000 | [0.00, 0.30] | no | yes |
| fp32/a_randn_b_zeros | 0.616 | 0.122 | 0.000 | [0.00, 0.30] | no | yes |
| fp32/sparse90 | 0.577 | 0.073 | 0.456 | [0.14, 0.78] | yes | yes |
| fp32/zeros | 0.000 | 0.000 | 0.000 | [0.00, 0.30] | yes | no |
| fp16/randn_small | 22.209 | 0.086 | 22.190 | [13.29, 31.09] | yes | yes |
| fp16/randn | 22.162 | 0.054 | 22.298 | [18.91, 25.68] | yes | no |
| fp16/randn_sorted | 20.748 | 0.426 | 21.443 | [12.99, 29.90] | yes | yes |
| fp16/pair_half_zero | 20.122 | 0.569 | 20.936 | [12.79, 29.09] | yes | yes |
| fp16/uniform01 | 19.426 | 0.086 | 16.733 | [11.04, 22.43] | yes | yes |
| fp16/fp8grid | 18.052 | 0.126 | 21.441 | [12.99, 29.89] | yes | yes |
| fp16/nn_like | 17.602 | 0.118 | 19.383 | [11.28, 27.48] | yes | yes |
| fp16/smallint | 17.000 | 0.302 | 20.115 | [12.44, 27.79] | yes | yes |
| fp16/sparse50 | 13.196 | 0.540 | 15.512 | [8.75, 22.27] | yes | yes |
| fp16/ones | 8.448 | 0.082 | 8.463 | [6.05, 10.88] | yes | no |
| fp16/neg_ones | 8.382 | 0.133 | 8.463 | [6.05, 10.88] | yes | yes |
| fp16/wsparse50 | 7.058 | 0.035 | 9.041 | [4.60, 13.48] | yes | yes |
| fp16/sparse90 | 1.410 | 0.113 | 1.190 | [0.56, 1.82] | yes | yes |
| fp16/a_zeros_b_randn | 0.782 | 0.063 | 0.000 | [0.00, 0.30] | no | yes |
| fp16/wsparse90 | 0.743 | 0.111 | 0.459 | [0.07, 0.84] | yes | yes |
| fp16/a_randn_b_zeros | 0.659 | 0.080 | 0.000 | [0.00, 0.30] | no | yes |
| fp16/zeros | 0.000 | 0.000 | 0.000 | [0.00, 0.30] | yes | no |
| int8/full | 7.056 | 0.059 | 7.108 | [3.73, 10.48] | yes | no |
| int8/gauss_q | 6.598 | 0.069 | 7.104 | [1.93, 12.28] | yes | yes |
| int8/sorted | 6.588 | 0.073 | 5.984 | [1.50, 10.47] | yes | yes |
| int8/pos | 6.171 | 0.206 | 3.447 | [0.32, 6.58] | yes | yes |
| int8/smallint | 6.003 | 0.142 | 7.129 | [1.95, 12.31] | yes | yes |
| int8/sparse50 | 5.463 | 0.146 | 6.063 | [1.59, 10.54] | yes | yes |
| int8/ternary | 5.186 | 0.051 | 6.417 | [1.68, 11.16] | yes | yes |
| int8/highbit | 3.233 | 0.036 | 4.493 | [0.84, 8.14] | yes | yes |
| int8/wsparse50 | 3.142 | 0.056 | 3.269 | [0.94, 5.60] | yes | yes |
| int8/neg_ones | 1.628 | 0.169 | 0.571 | [0.00, 2.97] | yes | yes |
| int8/ones | 1.561 | 0.069 | 0.571 | [0.00, 2.97] | yes | no |
| int8/sparse90 | 1.145 | 0.057 | 0.793 | [0.08, 1.50] | yes | yes |
| int8/wsparse90 | 0.538 | 0.051 | 0.269 | [0.00, 0.62] | yes | yes |
| int8/a_full_b_zeros | 0.497 | 0.085 | 0.000 | [0.00, 0.30] | no | yes |
| int8/a_zeros_b_full | 0.305 | 0.070 | 0.000 | [0.00, 0.30] | no | yes |
| int8/zeros | 0.000 | 0.000 | 0.000 | [0.00, 0.30] | yes | no |

`frozen 95%` is Q130(c)'s registered `switching_w_ci95`; the gated kinds' intervals are clipped at [0.00, 0.30] W, which is why the one-sided kinds miss on a real 0.6–0.8 W. `A1 out-of-sample` marks the kinds C-R1, C-R2, E78-R1 and E78-R2 are scored on.

### Predicted against measured: Q130(b) r2 (fcfe82a7) on D32, both variants

| cell | measured D32 (W) | r2 A predicted | error A (W) | z A | r2 B predicted | error B (W) | z B |
|---|---|---|---|---|---|---|---|
| fp32.randn_small | 24.764 | 23.920 | -0.844 | -3.9 | 23.920 | -0.844 | -3.9 |
| fp32.randn | 24.725 | 24.198 | -0.527 | -4.2 | 24.198 | -0.527 | -4.2 |
| fp32.randn_large | 24.711 | 23.931 | -0.780 | -6.4 | 23.931 | -0.780 | -6.4 |
| fp32.randn_sorted | 23.384 | 22.826 | -0.558 | -3.0 | 22.826 | -0.558 | -3.0 |
| fp32.uniform01 | 22.646 | 22.579 | -0.067 | -0.5 | 22.579 | -0.067 | -0.5 |
| fp32.fp16grid | 19.624 | 17.325 | -2.299 | -9.9 | 17.325 | -2.299 | -9.9 |
| fp32.bf16trunc | 18.136 | 15.016 | -3.120 | -10.4 | 15.016 | -3.120 | -10.4 |
| fp32.smallint | 14.079 | 10.738 | -3.341 | -9.7 | 10.738 | -3.341 | -9.7 |
| fp32.pow2 | 13.985 | 9.811 | -4.174 | -9.0 | 9.811 | -4.174 | -9.0 |
| fp32.nn_like | 13.036 | 12.377 | -0.659 | -9.5 | 12.377 | -0.659 | -9.5 |
| fp32.pi | 8.470 | 8.733 | 0.263 | 0.5 | 8.733 | 0.263 | 0.5 |
| fp32.ones | 8.257 | 8.732 | 0.475 | 0.9 | 8.732 | 0.475 | 0.9 |
| fp32.neg_ones | 8.143 | 8.732 | 0.589 | 1.1 | 8.732 | 0.589 | 1.1 |
| fp32.sparse50 | 7.302 | 5.630 | -1.672 | -44.2 | 5.630 | -1.672 | -44.2 |
| fp32.a_zeros_b_randn | 0.810 | 0.091 | -0.719 | -28.5 | 0.091 | -0.719 | -28.5 |
| fp32.a_randn_b_zeros | 0.616 | 0.046 | -0.570 | -12.0 | 0.046 | -0.570 | -12.0 |
| fp32.sparse90 | 0.577 | 0.238 | -0.339 | -11.9 | 0.238 | -0.339 | -11.9 |
| fp32.zeros | 0.000 | 0.000 | 0.000 | — | 0.000 | 0.000 | — |
| fp16.randn_small | 22.207 | 20.187 | -2.020 | -12.8 | 21.346 | -0.861 | -6.4 |
| fp16.randn | 22.138 | 20.412 | -1.726 | -11.3 | 21.593 | -0.545 | -4.1 |
| fp16.randn_sorted | 20.705 | 19.392 | -1.313 | -5.6 | 20.470 | -0.235 | -1.1 |
| fp16.pair_half_zero | 20.105 | 17.832 | -2.273 | -7.4 | 18.752 | -1.353 | -4.7 |
| fp16.uniform01 | 19.393 | 18.756 | -0.637 | -3.2 | 19.770 | 0.377 | 2.2 |
| fp16.fp8grid | 18.005 | 14.859 | -3.146 | -10.3 | 15.478 | -2.527 | -8.8 |
| fp16.nn_like | 17.511 | 15.599 | -1.912 | -12.0 | 16.466 | -1.045 | -7.3 |
| fp16.smallint | 16.960 | 13.197 | -3.763 | -10.3 | 13.652 | -3.308 | -9.4 |
| fp16.sparse50 | 13.180 | 11.310 | -1.870 | -6.9 | 11.937 | -1.243 | -4.7 |
| fp16.ones | 8.410 | 8.759 | 0.349 | 0.7 | 8.762 | 0.352 | 0.7 |
| fp16.neg_ones | 8.384 | 8.759 | 0.375 | 0.8 | 8.762 | 0.378 | 0.8 |
| fp16.wsparse50 | 7.089 | 4.967 | -2.122 | -45.9 | 5.257 | -1.832 | -43.1 |
| fp16.sparse90 | 1.414 | 0.697 | -0.717 | -28.6 | 0.733 | -0.681 | -27.5 |
| fp16.a_zeros_b_randn | 0.758 | 0.090 | -0.668 | -29.9 | 0.099 | -0.659 | -29.5 |
| fp16.a_randn_b_zeros | 0.714 | 0.045 | -0.669 | -40.8 | 0.050 | -0.664 | -40.5 |
| fp16.wsparse90 | 0.672 | 0.225 | -0.447 | -12.9 | 0.239 | -0.433 | -12.5 |
| fp16.zeros | -0.009 | 0.000 | 0.009 | 0.7 | 0.000 | 0.009 | 0.7 |
| int8.full | 7.667 | 16.018 | 8.351 | 10.2 | 17.278 | 9.611 | 12.3 |
| int8.sorted | 7.206 | 15.929 | 8.723 | 10.6 | 17.081 | 9.875 | 12.6 |
| int8.gauss_q | 7.202 | 16.008 | 8.806 | 10.7 | 17.257 | 10.055 | 12.9 |
| int8.pos | 6.761 | 15.687 | 8.926 | 10.7 | 16.543 | 9.782 | 12.1 |
| int8.smallint | 6.615 | 15.958 | 9.343 | 11.3 | 17.144 | 10.529 | 13.4 |
| int8.sparse50 | 6.085 | 14.793 | 8.708 | 11.4 | 15.844 | 9.759 | 13.3 |
| int8.ternary | 5.790 | 15.700 | 9.910 | 12.1 | 16.715 | 10.925 | 13.9 |
| int8.highbit | 3.841 | 15.422 | 11.581 | 13.8 | 15.954 | 12.113 | 14.7 |
| int8.wsparse50 | 3.770 | 5.862 | 2.092 | 7.2 | 6.497 | 2.727 | 10.1 |
| int8.neg_ones | 2.237 | 15.003 | 12.766 | 14.9 | 15.020 | 12.783 | 14.9 |
| int8.ones | 2.170 | 15.003 | 12.833 | 15.1 | 15.020 | 12.850 | 15.1 |
| int8.sparse90 | 1.743 | 2.934 | 1.191 | 8.1 | 3.255 | 1.512 | 11.1 |
| int8.wsparse90 | 1.155 | 0.429 | -0.726 | -36.4 | 0.586 | -0.569 | -33.3 |
| int8.a_full_b_zeros | 1.130 | 0.066 | -1.064 | -26.1 | 0.147 | -0.983 | -23.9 |
| int8.a_zeros_b_full | 0.913 | 0.004 | -0.909 | -27.2 | 0.009 | -0.904 | -27.1 |
| int8.zeros | 0.612 | -0.000 | -0.612 | -29.6 | -0.000 | -0.612 | -29.6 |

Error = predicted − measured D32 (watts above fp32 zeros), z = error / √(σ²pred + se²), as registered. Both variants are provisional by Q130(b)'s own statement (its bench fails a functional check).

### The registered verdicts (E78-R1 … R4), at the primary slope and both registered arms

| rule | cell | measured (95%) | registered band | verdict | at leak 0.3803 W/°C | at leak 0 W/°C |
|---|---|---|---|---|---|---|
| E78-R1 | Q130(c) fp32 (15 kinds) | rho 0.941 | rho >= 0.80 | **PASS** | PASS | PASS |
| E78-R1 | Q130(c) fp16 (14 kinds) | rho 0.948 | rho >= 0.80 | **PASS** | PASS | PASS |
| E78-R1 | Q130(c) int8 (13 kinds) | rho 0.867 | rho >= 0.80 | **PASS** | PASS | PASS |
| E78-R2 | Q130(c) fp32 (15 kinds) | rms 2.270 W | rms <= 2 W | **FAIL** | FAIL | FAIL |
| E78-R2 | Q130(c) fp16 (14 kinds) | rms 1.757 W | rms <= 2 W | **PASS** | PASS | PASS |
| E78-R2 | Q130(c) int8 (13 kinds) | rms 1.054 W | rms <= 1 W | **FAIL** | FAIL | FAIL |
| E78-R3a | fp32.a_randn_b_zeros/randn | 0.025 [0.020, 0.030] | <= 0.15 | **PASS** | PASS | PASS |
| E78-R3a | fp32.a_zeros_b_randn/randn | 0.033 [0.030, 0.035] | <= 0.15 | **PASS** | PASS | PASS |
| E78-R3a | fp16.a_randn_b_zeros/randn | 0.030 [0.026, 0.033] | <= 0.15 | **PASS** | PASS | PASS |
| E78-R3a | fp16.a_zeros_b_randn/randn | 0.035 [0.032, 0.038] | <= 0.15 | **PASS** | PASS | PASS |
| E78-R3a | int8.a_full_b_zeros/full | 0.071 [0.058, 0.083] | <= 0.15 | **PASS** | PASS | PASS |
| E78-R3a | int8.a_zeros_b_full/full | 0.043 [0.034, 0.053] | <= 0.15 | **PASS** | PASS | PASS |
| E78-R3b | fp32.sparse90/randn | 0.023 [0.020, 0.026] | <= 0.25 | **PASS** | PASS | PASS |
| E78-R3b | fp16.sparse90/randn | 0.064 [0.059, 0.069] | <= 0.25 | **PASS** | PASS | PASS |
| E78-R3b | int8.sparse90/full | 0.162 [0.154, 0.170] | <= 0.25 | **PASS** | PASS | PASS |
| E78-R3c | fp32.randn_small/randn | 1.002 [0.981, 1.022] | in [0.909, 1.10] | **PASS** | PASS | PASS |
| E78-R3c | fp32.randn_large/randn | 0.999 [0.997, 1.002] | in [0.909, 1.10] | **PASS** | PASS | PASS |
| E78-R3d | fp32 bf16trunc < fp16grid < randn | fp16grid−bf16trunc 1.488 [1.425, 1.551] W; randn−fp16grid 5.101 [4.978, 5.224] W | both 95% lower bounds > 0 | **PASS** | PASS | PASS |
| E78-R3e | order alone, fp32 + fp16 + int8 | fp32.randn - fp32.randn_sorted 1.341 [1.006, 1.676] W (PASS); fp16.randn - fp16.randn_sorted 1.414 [1.016, 1.812] W (PASS); int8.full - int8.sorted 0.468 [0.368, 0.568] W (PASS) | every 95% lower bound > 0 | **PASS** | PASS | PASS |
| E78-R3f | int8 neg_ones − ones (static bits; fp32, fp16 reported) | int8.neg_ones - int8.ones 0.067 [-0.050, 0.184] W (PASS); fp32.neg_ones - fp32.ones -0.113 [-0.521, 0.295] W (INCONCLUSIVE, reported); fp16.neg_ones - fp16.ones -0.067 [-0.221, 0.087] W (PASS, reported) | int8: 95% inside ± 0.30 W | **PASS** | PASS | PASS |
| E78-R3g | fp16 pair_half_zero / randn | 0.908 [0.883, 0.933] | >= 0.40 | **PASS** | PASS | PASS |
| E78-R3h | sparse50/random: fp32 < fp16 < int8 | fp32 0.295 [0.292, 0.298]; fp16 0.595 [0.571, 0.620]; int8 0.774 [0.753, 0.795]; fp16−fp32 0.300 [0.276, 0.325]; int8−fp16 0.179 [0.163, 0.194] | both 95% lower bounds > 0 | **PASS** | PASS | PASS |
| E78-R3i | fp16.sparse50 - fp16.wsparse50 | 6.138 [5.606, 6.670] | 95% lower bound > 0 | **PASS** | PASS | PASS |
| E78-R3i | int8.sparse50 - int8.wsparse50 | 2.322 [2.154, 2.489] | 95% lower bound > 0 | **PASS** | PASS | PASS |
| E78-R4 | fp32.ones | 8.257 ± 0.221 | 8.217 ± 0.6 W | **PASS** | PASS | PASS |
| E78-R4 | fp32.pi | 8.470 ± 0.113 | 8.496 ± 0.6 W | **PASS** | PASS | PASS |
| E78-R4 | fp32.randn | 24.725 ± 0.082 | 24.659 ± 1 W | **PASS** | PASS | PASS |
| E78-R4 | fp16.ones | 8.448 ± 0.082 | 8.736 ± 0.8 W | **PASS** | PASS | PASS |
| E78-R4 | int8.ones | 1.561 ± 0.069 | 1.834 ± 0.6 W | **PASS** | PASS | PASS |
| E78-R4 | pi_builtin_vs_file | -0.067 ± 0.104 | within ± 0.25 W | **PASS** | PASS | PASS |

Tally at the primary slope: **28 pass, 2 fail, 0 inconclusive, 0 not scored** (30 verdicts). The registered arms: at `leak0.3803`: 28 pass, 2 fail, 0 inconclusive, 0 not scored; at `leak0`: 28 pass, 2 fail, 0 inconclusive, 0 not scored.

E78-R1 and R2 beside the primary (Q130(b) r2, not in the tally): ρ = 0.974 / 0.978 / 0.912 (A) and 0.974 / 0.978 / 0.934 (B); rms 1.826 / 1.868 / 7.845 W (A) and 1.826 / 1.408 / 8.511 W (B) — fp32 / fp16 / int8 ([`scored.json`](scored.json) `rules.E78-R1.by_model`, `rules.E78-R2.by_model`).

**E78-R5, the instrument checks (reported, never a verdict):** idle consistency 0.064 W (≤ 0.15); rail τ re-fit 0.95 s (in [0.80, 1.15]); duty 0.9959–0.9967 (in [0.990, 1.000]); carry-over slope 0.0008 ± 0.0009 W/W over 382 pairs; the built-in pi tile equal to `fp32.pi`'s in every pass. All ok.

### Q130(c), scored as its README and A1 say

- C-R1 fp32: out of sample 0.533 inside the frozen 95% (need 0.7) → **FAIL**; R1-A1 0.733 → PASS; E78's secondary (intervals overlap) 0.600; all kinds 0.611 → FAIL
- C-R1 fp16: out of sample 0.857 inside the frozen 95% (need 0.5) → **PASS**; R1-A1 0.857 → PASS; E78's secondary (intervals overlap) 0.857; all kinds 0.882 → PASS
- C-R1 int8: out of sample 0.846 inside the frozen 95% (need 0.5) → **PASS**; R1-A1 0.846 → PASS; E78's secondary (intervals overlap) 0.923; all kinds 0.875 → PASS
- C-R2 fp32: rho 0.941 → **PASS** (all kinds 0.950)
- C-R2 fp16: rho 0.948 → **PASS** (all kinds 0.960)
- C-R2 int8: rho 0.867 → **FAIL** (all kinds 0.908)
- C-R3 fp16: sparse50 − wsparse50 6.138 W → **PASS**
- C-R3 int8: sparse50 − wsparse50 2.322 W → **PASS**; favours frozen
- C-R4: int8 ones − zeros 1.561 W → **PASS**
- C-R6: → **PASS** (random sign patterns against a constant (A1.6), not a product-sign price)
- C-R9: fp32 a_randn_b_zeros 0.616 W (pass 7810, run first: 0.528) → selects the **gate** arm

### Q130(b) r2, errors in watts above fp32 zeros

- variant A fp32: rms 1.672 W, mean error -1.019 W, |z| ≤ 2 for 0.222 of 18
- variant A fp16: rms 1.748 W, mean error -1.326 W, |z| ≤ 2 for 0.176 of 17
- variant A int8: rms 8.042 W, mean error 6.245 W, |z| ≤ 2 for 0.000 of 16
- variant B fp32: rms 1.672 W, mean error -1.019 W, |z| ≤ 2 for 0.222 of 18
- variant B fp16: rms 1.287 W, mean error -0.839 W, |z| ≤ 2 for 0.235 of 17
- variant B int8: rms 8.659 W, mean error 6.841 W, |z| ≤ 2 for 0.000 of 16
- g per format, re-fitted on E78's anchors (g_t = D(t.ones) / (4,096 x R), as a ratio to fp32's): fp32 1.000 (1.798e-12 W per live slot-cycle/s), fp16 1.023 (1.840e-12 W per live slot-cycle/s), int8 0.110 (1.980e-13 W per live slot-cycle/s); r2's E64 values fp16 0.95 +- 0.10, int8 0.037 +- 0.048

### A derived reading, not registered: what a moving operand bus costs a gated lane

In the one-sided kinds every lane is gated while one operand's bus keeps moving; kinds.json counts those bits
(`bus_bits_per_op`). Dividing the whole residual D by them, at the measured op rate R, bounds the price of a moving
bus bit from above (it charges everything left to the bus):

| cell | D (W) | moving bus bits / op | R (op/s) | ≤ fJ per moving bus bit |
|---|---|---|---|---|
| fp32 `a_randn_b_zeros` (A moves) | 0.616 ± 0.122 | 27,920 | 1.1212 × 10⁹ | **19.7** [15.8, 23.6] |
| fp32 `a_zeros_b_randn` (B moves) | 0.810 ± 0.065 | 55,798 | 1.1206 × 10⁹ | **13.0** [11.9, 14.0] |
| fp16 `a_randn_b_zeros` (A moves) | 0.659 ± 0.080 | 28,096 | 1.1208 × 10⁹ | **20.9** [18.4, 23.5] |
| fp16 `a_zeros_b_randn` (B moves) | 0.782 ± 0.063 | 55,806 | 1.1208 × 10⁹ | **12.5** [11.5, 13.5] |

The two formats agree side for side. int8's bus counts are provisional in kinds.json, so int8 is not priced this way
(4.0 and 38.3 fJ, which disagree with each other). For scale: E60 priced a read-port bit into an XOR at 20.8 fJ
([`docs/findings/03-experiments.md`](../../../findings/03-experiments.md), § E60, `e_in`).

## What it changes

- **For the blog's kinds table:** every format × kind cell now has a measured switching power (D over the type's own
  zeros, S over idle), an energy per op, per MAC and per flop, and a heat column, with 95% intervals over six
  passes, on one card at one clock. The table above is the source; `e78.json` › `items` holds every number with its
  SE and n. The cheap kinds are cheap for three reasons of very different size: the zero gate (a 32-bit word test,
  so it pays most in fp32), a lane that is on but sees nothing change (a third of random data in the floats, a
  fifth in int8), and changing operand bits (mostly mantissa bits; magnitude is free, order is worth 5–7%).
- **Horace hub, Status item 9 ("fp16 and int8"):** the kinds half is closed on aifoundry3 at 600 MHz: fp16 and int8
  now have 17 and 16 measured kinds beside fp32's 18, on the same card, clock and voltage as E65/E67/E79. The fp16
  all-ones *sustained clock* cell named in that item is E80's (aifoundry2), not E78's.
- **For the models:** neither frozen model is good enough to stand in for the table. Q130(c) is a ranking model
  (ρ 0.87–0.95) that misses mantissa truncation by 4–5 W; Q130(b) r2 ranks better and gets the truncation steps'
  size nearer, but its int8 scale is wrong by an order of magnitude. Its `g` per format, re-fitted here, is the
  number to carry: int8 0.110 of fp32's, not 0.037.
- **For E64's int8 cells:** E64's int8 `--values randn` and `--values uniform` are this table's `full` and `pos`.

## Registered against what happened

| registered (E78.md, `predictions-e78.json`) | happened |
|---|---|
| freeze and A1 on origin/main before the claim and any launch | `cfd94285` 12:45:37, `09c6e29b` 12:48:23; claim 12:55:49; first device-opening command 12:56:13 |
| the harness copied into the aifoundry3 binaries tree (`~/aifoundry`) | rsync 12:54:22; all 68 files' sha256 identical on the box and the Intel ([`logs/box-harness.sha256`](logs/box-harness.sha256)) |
| `run_e78.sh setup`, opening no device node | 12:54:36–12:54:45: `lib.sh` identical to the freeze's (`033d0776…`), `{"tiles": 51, "problems": []}`, the binary's five strings present, numpy 1.26.4, `dry rc=0`, 67 device launches in the dry pass ([`logs/e78-dry.log`](logs/e78-dry.log)) |
| the smoke: six items, ok, cycles/op 546 / 546 / 318 | p7801, 12:56:34–12:57:14: 6 items × 6 launches, every record ok, 546.0 / 546.0 / 318.0 (each run's first launch 546.014–546.017 / 318.015, inside 0.5%) |
| passes 7810–7815, at least four, inside 85 card-minutes and before 19:15 | all six ran (the budget rule never acted); 64.1 min in passes, 0.66 in the smoke; the queue ended 14:03:09 ([`logs/e78-queue.log`](logs/e78-queue.log)) |
| 65 runs a pass (the tie twice, the six anchors three times, 45 kinds); pass 7810 runs `fp32.a_randn_b_zeros` first | 65, 64, 64, 65, 65, 65 runs; `fp32.a_randn_b_zeros` ran first in 7810 (0.528 W) |
| a run whose launch reading is not reached is skipped, never launched off protocol; three in a row stop the pass | **two skips**, neither part of a run of three: 7811 #14 `int8.zeros` and 7812 #64 `anchor_pi` (the closing tie). Both times the reading came down to 58 °C and went back to 59 °C inside the 2.0 s quiet wait (1.71 s and 1.41 s of quiet) |
| per-run gates (clock, mV, launch reading, quiet, records, cycles/op, window, duty, tile dump) | 388 of 388 runs pass every gate (`e78.json` › `failed` is empty) |
| pass gates (failed runs, zeros straight line and span, random span, tie drift ≤ 0.60 W, TDP 0 and 65 °C at both ends) | no pass set aside. Tie drift 0.246 / 0.213 / — / 0.181 / 0.080 / 0.237 W. **Pass 7812's drift gate could not be evaluated**, because its closing tie was the skipped run; its zeros anchors (spans 0.160 / 0.258 / 0.128 W, mid-run departures −0.033 / +0.082 / +0.017 W) and random anchors (0.079 / 0.133 / 0.160 W) all pass, so the registered code keeps it. Every config read: TDP 0, 65 °C, 600 MHz, 522–523 mV (`config_start.json`, `config_end.json` in every pass) |
| leakage: `auto` primary, arms 0.3803 and 0, every verdict reported at each | k = 0.1994 W/°C (250 runs); no verdict moves between arms; D(fp32 randn) 25.344 / 24.725 / 24.163 W at k = 0 / 0.199 / 0.380, inside R4's ± 1.0 W at all three |
| the rail deconvolved (τ 0.95 s), arms 0.80 and 1.10 s; reported, never scored | rail D / board D 0.800–0.865 over the 36 kinds above 3 W; τ re-fit 0.95–1.00 s per pass (median 0.95), c 0.803–0.816 |
| R5 checks: idle consistency ≤ 0.15 W; τ in [0.80, 1.15] s; duty in [0.990, 1.000]; carry-over; the pi tile | 0.064 W; 0.95 s; 0.9959–0.9967; slope 0.0008 ± 0.0009 W/W over 382 pairs; the host's built-in pi dumped equal to `fp32.pi`'s tile in all six passes. All five ok |
| the scorer refuses to score on a changed frozen input | `frozen_inputs_verified: true` |
| fewer than four kept passes makes every rule NOT SCORED | six kept: all 30 verdicts scored |

## Departures (dated)

- **D1** (registered, E60's): on aifoundry3 a user who is only logged in does not block. Other lab users kept idle
  logins there throughout (12:53 PDT: several sessions). None held the card, a device node or the card lock: `et-who`
  read free at 12:53, 12:54, 12:56, 12:57 and 14:03, and no pass logged an "others present" line.
- **D2 — the data directory's name (Sat 31 Oct, decided at 12:57, before any data).** The run lane's brief named
  `docs/reports/data/2026-10-31-e78-kinds-of-numbers/`. The registration names this directory
  (`E78.md` § Files; `predictions-e78.json` › `harness.data_dir`), and the registered one is used.
- **D3 — the collect ran twice on the Intel (Sat 31 Oct, 14:10).** The first assembly ran `collect_e78.sh` over a
  copy of the raw passes in the lane's scratch directory, so `e78.json`, its arms and `runs.csv` recorded that
  directory, a Mac home path, in their `dirs` / `dir` fields. The lab's public-text rule forbids it. The collect was
  run again, as registered, over a copy at the box's own relative path (`build/claims-v3/aifoundry3` in the Intel
  clone). `scored.json` and `results.md` came out byte-identical, and every item and check of all five reductions
  identical; only the path strings changed.
- **D4 — two device processes are not under `timeout 10` (inherited, as E60–E79).** The registration's Safety line
  says every device process runs under `timeout 10`. Every launch (`run_e78.py` `dev()`) and every `ettelem config`
  read (`block_e78.sh` change 2, and the two session reads below) did. `lib.sh`'s `die_c` in `block_begin` and
  `block_end` runs `ettelem sample --seconds 1` under `timeout 20`, and the 10 Hz sampler runs for the whole pass by
  design (`start_sampler`). `lib.sh` is frozen at `033d0776…`, so this is the code that ran (`code.sha256`).
- **D5 — two session-level `ettelem config` reads outside the passes (12:56:13 and 14:03:24).** Not in the run
  order, which reads the configuration inside each pass. Both were read-only, after the claim, under
  `flock -n /run/lock/etsoc-shire0.lock` and `timeout 10`: TDP 0, 65 °C, 600 MHz, 523 mV both times
  ([`ident/config_session_start.json`](ident/config_session_start.json), [`ident/config_session_end.json`](ident/config_session_end.json)).

## How it ran

On the Intel: `origin/main` contained `09c6e29b`; `rsync -a --exclude __pycache__ tools/claims-v3/kinds/
aifoundry3:aifoundry/tools/claims-v3/kinds/`. On aifoundry3, from `~/aifoundry`, each step in a script file run by
`ssh -o BatchMode=yes aifoundry3 'bash -s' < file`:

```bash
bash tools/claims-v3/kinds/run_e78.sh setup        # 12:54:36, no device access
# 12:55:49  the #community-lab claim (one line)
flock -n /run/lock/etsoc-shire0.lock timeout 10 build/ettelem/ettelem config < /dev/null   # 12:56:13, read only
bash tools/claims-v3/kinds/run_e78.sh smoke        # 12:56:34-12:57:14
bash tools/claims-v3/kinds/run_e78.sh go 7810 6    # 12:57:32, detached; queue done 14:03:09
flock -n /run/lock/etsoc-shire0.lock timeout 10 build/ettelem/ettelem config < /dev/null   # 14:03:24, read only
```

Waits were bounded remote loops of at most 525 s. The raw passes, the smoke, both logs and the two reads were copied
to the Intel, and the registered collect ran there (A1):
`PY=/usr/bin/python3 nice -n 10 bash tools/claims-v3/kinds/collect_e78.sh 'p78[1-9][0-9]' build/claims-v3/aifoundry3`.

| pass | began | ended | minutes | die (block start → end) | runs | heater launches |
|---|---|---|---|---|---|---|
| smoke 7801 | 12:56:34 | 12:57:14 | 0.66 | 50 → 51 °C | 6 | 0 |
| 7810 | 12:57:33 | 13:08:52 | 11.32 | 51 → 58 °C | 65 | 36 |
| 7811 | 13:09:07 | 13:19:28 | 10.35 | 57 → 58 °C | 64 (1 skipped) | 20 |
| 7812 | 13:19:43 | 13:30:05 | 10.36 | 57 → 57 °C | 64 (1 skipped) | 22 |
| 7813 | 13:30:20 | 13:40:57 | 10.62 | 57 → 57 °C | 65 | 21 |
| 7814 | 13:41:12 | 13:51:55 | 10.72 | 56 → 57 °C | 65 | 22 |
| 7815 | 13:52:10 | 14:02:54 | 10.73 | 57 → 58 °C | 65 | 22 |

The quiet before a run was 3.3–3.6 s at the median (the rule asks ≥ 2.0 s; the wait for 58 °C after heating usually
supplies more).

## Joins and traps

- **E64's names.** int8 `full` is E64's int8 `--values randn` (uniform −128..127) and `pos` its `--values uniform`
  (0..127).
- **A `file:` run's metadata is wrong and its math is unchecked** (`main.cpp:587-591`, `:614`): ignore `nnz_a`,
  `a_elems` and `fp16_one_sided_pairs` in `runs.jsonl`; use kinds.json. E78 verifies no arithmetic.
- **One tile a cell is a draw.** Each cell is one fixed tile; quote kinds.json's `replicates` for a rule. E78's
  `fp32.randn` tile moves 1.8% fewer operand bits than its rule's mean.
- **int8's bus and Hamming counts are provisional** in kinds.json; its gated fractions are not.
- **fp32 `smallint` is not zero-free** (1/16 of its words are zero, 11.8% of lane-cycles gate); `pow2` and
  `bf16trunc` are the zero-free low-entropy fp32 kinds.
- **E78 does not validate the A-side weight in ungated lanes**: its one-sided kinds are fully gated. E70's
  `nrd_a` / `nrd_b` pair is that measurement.
- **S includes each type's zero-data level** (1.99 / 1.99 / 2.61 W); D does not. Quote S for "what a multiply-add
  costs over an idle card", D for "what the data costs".
- **The ΔT column is the die reading's mean over the window minus the launch reading**, in whole-degree steps
  (most int8 cells read 1.00 or 0.83 °C because of the steps).

## Files

| file | what |
|---|---|
| `README.md` | this file |
| [`results.md`](results.md), [`scored.json`](scored.json) | `score_e78.py`: the matrix, every registered rule, Q130(c) and Q130(b) r2, both leakage arms |
| [`e78.json`](e78.json), [`runs.csv`](runs.csv), [`reduce.txt`](reduce.txt) | `reduce_e78.py` at the primary slope: every item over passes (mean, SE, n, ci95), per pass, the anchors, the checks; one row per run |
| `e78-leak0.3803.json`, `e78-leak0.json` (+ csv, txt, log) | the registered leakage arms |
| `e78-tau0.80.json`, `e78-tau1.10.json` | the registered rail-lag arms |
| [`manifest.json`](manifest.json) | what ran, the frozen inputs' sha256, the claim, every file's sha256 |
| [`code.sha256`](code.sha256) | the harness, as committed; each pass's own `code.sha256` records what ran on the box |
| `ident/` | the two session `ettelem config` reads and the box's `et-lab-manifest` |
| `logs/` | the queue log, the setup's dry-run log, the harness hashes on the box |
| `aifoundry3/kinds/p7810` … `p7815`, `kinds-smoke-p7801` | raw: `telemetry.jsonl.gz` (10 Hz), `runs.jsonl` (host launch records), `marks.jsonl`, `run.log`, `configs.json`, `plan.json`, `config_start/end.json`, `manifest.txt`, `tiles/` (every tile the host dumped) |
