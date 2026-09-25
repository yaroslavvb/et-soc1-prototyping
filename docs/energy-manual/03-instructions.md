# 3. Instructions

Energy per instruction retired, above idle, at 600 MHz and 0.52 V, with both harts of all 1,024 minions running the instruction flat out. Three operand sets: all zeros, one constant everywhere, and random values in [0.5, 2).

Every entry is **mean** [lo–hi]: the mean over every pass on every card, and the full range those passes spanned. "a2" and "a3" are aifoundry2 and aifoundry3, each as its own mean ± its pass-to-pass standard error. Three shuffled passes on each of two cards, so n = 6 for every entry (3 where the constant set was not run). The full catalogue of 161 instructions is in [3.1](03a-every-instruction.md).

## Scalar and vector units

| Instruction | zeros pJ | constant pJ | random pJ | random / zeros | issue rate per hart | per card, random | Note |
|---|---|---|---|---|---|---|---|
| `add` | **5.7** [5.2–6.4] | **6.3** [6.1–6.8] | **9.2** [8.6–10.1] | 1.63× | 0.37 | a2: 9.6 ± 0.3 · a3: 8.8 ± 0.1 |  |
| `xor` | **5.9** [5.5–6.5] | — | **9.2** [8.6–10.1] | 1.55× | 0.37 | a2: 9.6 ± 0.5 · a3: 8.8 ± 0.2 |  |
| `mul` | **22.3** [18.2–25.2] | — | **40.9** [37.2–46.9] | 1.84× | 0.05 | a2: 42.8 ± 2.7 · a3: 39.1 ± 0.9 | 64-bit, multi-cycle: 1/8 the rate, so most of this is the awake core amortised over a slow op |
| `fadd.s` | **23.3** [22.8–24.2] | **23.4** [22.8–24.2] | **25.5** [24.7–26.1] | 1.09× | 0.37 | a2: 25.8 ± 0.2 · a3: 25.1 ± 0.2 |  |
| `fmul.s` | **25.6** [24.9–26.5] | — | **29.1** [28.3–30.5] | 1.14× | 0.37 | a2: 29.8 ± 0.3 · a3: 28.3 ± 0.03 |  |
| `fmadd.s` | **27.0** [26.3–28.0] | **27.0** [26.5–27.6] | **31.1** [30.4–32.3] | 1.15× | 0.37 | a2: 31.6 ± 0.4 · a3: 30.5 ± 0.1 |  |
| `fadd.ps (8 lanes)` | **23.2** [22.8–23.9] | **23.4** [22.9–24.0] | **42.2** [41.0–43.6] (5.3/lane) | 1.82× | 0.36 | a2: 43.2 ± 0.2 · a3: 41.2 ± 0.1 |  |
| `fmul.ps (8 lanes)` | **25.2** [24.7–25.6] | — | **50.3** [48.8–51.8] (6.3/lane) | 2.00× | 0.36 | a2: 51.7 ± 0.1 · a3: 48.9 ± 0.05 |  |
| `fmadd.ps (8 lanes)` | **26.6** [25.6–27.7] | **26.9** [25.8–27.7] | **55.9** [53.5–58.1] (7.0/lane) | 2.10× | 0.37 | a2: 57.1 ± 0.5 · a3: 54.6 ± 0.5 | 16 flops |
| `fadd.pi (8 lanes, int32)` | **13.3** [12.8–14.2] | **13.2** [12.6–13.5] | **20.1** [19.6–20.8] (2.5/lane) | 1.51× | 0.36 | a2: 20.5 ± 0.2 · a3: 19.7 ± 0.1 |  |
| `fmul.pi (8 lanes, int32)` | **25.8** [24.4–26.5] | **26.2** [25.5–26.9] | **51.2** [49.6–53.1] (6.4/lane) | 1.99× | 0.37 | a2: 52.7 ± 0.2 · a3: 49.7 ± 0.1 |  |
| `fexp.ps (8 lanes)` | **99.4** [98.0–102.8] | **99.2** [95.4–102.7] | **158.7** [154.8–164.0] (19.8/lane) | 1.60× | 0.09 | a2: 162.4 ± 0.9 · a3: 155.1 ± 0.1 | transcendental unit, ¼ the rate |
| `frcp.ps (8 lanes)` | **73.0** [69.2–75.8] | — | **115.4** [110.7–119.1] (14.4/lane) | 1.58× | 0.15 | a2: 118.5 ± 0.4 · a3: 112.2 ± 0.8 | transcendental unit |

Thirteen instructions trapped in U-mode in a one-off check while the catalogue was written (listed in [3.1](03a-every-instruction.md); the card and the log of that check were not kept), among them every float and vector divide and square root, as expected: this silicon has no hardware divide or square root for them.

**What the table says.**
- **An integer add on zeros, 5.7 pJ [5.2–6.4], is within noise of a `nop` (5.3 pJ) on both cards**: on zeros it cannot be told apart from the awake core that issues it (section 2). Random operands add 3.6 pJ.
- **A scalar float add costs 4.1× an integer add** even on zeros. The FPU does not gate on zero the way the tensor unit does.
- **An 8-lane vector op on zeros costs the same as the scalar op** (23.2 against 23.3 pJ, bars overlapping): lanes computing on zeros add nothing. On random data the eight lanes cost 1.8× — this is the data dependence of docs/findings/10-data-dependent-power.md, in the vector unit.
- **Per lane on random data, `fmadd.ps` is 7.0 pJ per multiply-add** [6.7–7.3]. The tensor unit below does the same multiply-add for 5.8 pJ [5.2–6.0]. Take out the vector instruction's issue — 4.5–5.3 pJ, what a fence or a nop costs (section 2) — and the lane is 6.3–6.4 pJ, about 10% above the tensor unit. Read that way, **of the 1.2 pJ per multiply-add the tensor unit saves, roughly half is instruction issue and the rest datapath** (50–58% issue on aifoundry2, 38–47% on aifoundry3, with the fence or the nop as the issue cost); that is arithmetic on rows whose operands differ (uniform in [0.5, 2) here, normal for the tensor unit), not a measured decomposition.
- **Integer vector adds are half the price of float ones** (13.3 vs 23.2 pJ on zeros); integer vector multiplies are not.
- **The transcendentals rank with the 64-bit divides as the dearest arithmetic**: `flog.ps` at 219 pJ and `fexp.ps` at 159 pJ for eight lanes, at a quarter of the rate, against 142–149 pJ for the 64-bit divides and remainders; `frcp.ps` (115) is cheaper, and `fexp.ps` is 2.8× a vector multiply-add. Only loads and stores that bypass the L1 (290–392 pJ) and atomics (344–1,393 pJ) cost more ([3.1](03a-every-instruction.md)).

## 3.2 The tensor unit

`TensorFMA` on a tile per instruction: fp32 16×16×16 = 4,096 multiply-adds, fp16 8,192, int8 16,384; 546 cycles per instruction for every pattern (318 for int8), all 1,024 minions, launched at 80 °C on aifoundry2 and 56 °C on aifoundry3 (so the per-card fp32 values compare a warm card with a cool one). **Marginal** is board power above idle per multiply-add; **loaded** is total board power, idle included, per multiply-add, which is what a multiply-add costs when it is the only thing running.

The bar on each fp32 row is the envelope of ±1 sd around the ablation's two runs on aifoundry2 and the 22 September transfer's runs on both cards (n = 4); fp16 and int8 were run twice on aifoundry2 only, and their bar is ±1 sd of those two runs: under 1% on random data, 1.5% on int8 zeros, 5–6% on the ones patterns.

| Type, operands | pJ per MAC, marginal | per card | pJ per MAC, loaded (a2) | W over idle (a2) | MACs per second |
|---|---|---|---|---|---|
| TensorFMA fp32, zeros | **0.418** [0.406–0.426] | a2: 0.421 · a3: 0.411 | 8.32 | 1.91 | 4.59 × 10¹² |
| TensorFMA fp32, ones | **2.229** [2.031–2.304] | a2: 2.289 · a3: 2.109 | 10.21 | 10.56 | 4.59 × 10¹² |
| TensorFMA fp32, randn | **5.779** [5.241–6.025] | a2: 5.961 · a3: 5.415 | 13.92 | 27.63 | 4.59 × 10¹² |
| TensorFMA fp16, zeros | **0.207** [0.205–0.208] | a2: 0.207 (a2 only) | 4.16 | 1.90 | 9.18 × 10¹² |
| TensorFMA fp16, ones | **1.094** [1.035–1.154] | a2: 1.094 (a2 only) | 5.04 | 10.05 | 9.18 × 10¹² |
| TensorFMA fp16, randn | **2.699** [2.696–2.701] | a2: 2.699 (a2 only) | 6.65 | 24.78 | 9.18 × 10¹² |
| TensorFMA int8, zeros | **0.082** [0.080–0.083] | a2: 0.082 (a2 only) | 1.23 | 2.57 | 3.15 × 10¹³ |
| TensorFMA int8, ones | **0.134** [0.126–0.141] | a2: 0.134 (a2 only) | 1.29 | 4.22 | 3.15 × 10¹³ |
| TensorFMA int8, randn | **0.316** [0.314–0.319] | a2: 0.316 (a2 only) | 1.47 | 9.98 | 3.15 × 10¹³ |

### Where the tensor unit's energy goes: per flip

The tensor unit is the one place on the chip where the energy has been resolved below the instruction, by simulating its RTL on the operands aifoundry2 actually ran (docs/findings/11-thermal-model.md). Four kinds of event, four energies fitted on that card:

| Event | fJ each | What it is |
|---|---|---|
| ffclk | 3.179 | register bit clocked |
| mult | 0.025 | net toggle in the multiplier tree |
| rest | 0.801 | other net toggle in the unit |
| bus | 15.539 | operand-word bit toggled outside the unit |
| tensor state machines | 1.81 mW per active minion | per minion, whatever the data |

A random-data 16×16×16 tile clocks 2.5 million register bits, toggles 74 million multiplier-tree nets and 13 million other nets, and toggles 140 thousand operand-word bits: at the energies above that is 27.2 W on 1,024 minions, and aifoundry2 measures 27.6. Zeros clock nothing (the lane clock is withheld when an operand word is zero) and cost 1.9 W. Structured matrices — Hadamard, DCT, butterfly, kaleidoscope and ten others — were priced this way to 0.9 W rms **before** they ran on aifoundry2 (one session, two runs each). The four energies are one fit on aifoundry2; their confidence is that 0.9 W rms over fourteen held-out patterns, and the 8% by which aifoundry3 runs below the fit on every pattern (section 8).

Sources: `docs/reports/data/2026-09-23-catalogue-aifoundry2/`, `-aifoundry3/` (3.1), `docs/reports/data/2026-09-21-horace-aifoundry2/ablation.json` and `docs/reports/data/2026-09-22-cards/cards-report.json` (3.2), `docs/reports/data/2026-09-21-horace-aifoundry2/model.json` (flips).
