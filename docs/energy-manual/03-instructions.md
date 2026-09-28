# 3. Instructions

Energy per instruction retired, above idle, at 600 MHz and 0.50–0.52 V on the minion rail, with both harts of all 1,024 minions running the instruction flat out. Three operand sets: all zeros, one constant everywhere, and random values in [0.5, 2).

Every entry is **mean** [lo–hi]: the mean over every pass on every card, and the full range those passes spanned. "a2", "a3" and "a1c1" are aifoundry2, aifoundry3 and aifoundry1's card 1, each as its own mean ± its pass-to-pass standard error. Three shuffled passes on each of three cards (26 September), so n = 9 for every entry. The full catalogue of 161 instructions is in [3.1](03a-every-instruction.md), with the 15 gather, scatter and packed-atomic instructions of E48.

## Scalar and vector units

| Instruction | zeros pJ | constant pJ | random pJ | random / zeros | issue rate per hart | per card, random | Note |
|---|---|---|---|---|---|---|---|
| `add` | **6.2** [5.6–6.9] | **6.6** [6.0–6.9] | **9.7** [9.3–10.3] | 1.57× | 0.37 | a2: 10.0 ± 0.2 · a3: 9.6 ± 0.2 · a1c1: 9.6 ± 0.1 |  |
| `xor` | **6.0** [5.6–6.6] | — | **9.6** [9.0–10.5] | 1.58× | 0.37 | a2: 9.9 ± 0.3 · a3: 9.5 ± 0.2 · a1c1: 9.3 ± 0.2 |  |
| `mul` | **24.6** [19.0–30.7] | — | **43.4** [39.9–47.4] | 1.76× | 0.05 | a2: 46.0 ± 0.7 · a3: 41.9 ± 1.0 · a1c1: 42.1 ± 0.9 | 64-bit, multi-cycle: 1/8 the rate, so most of this is the awake core amortised over a slow op |
| `fadd.s` | **23.7** [22.0–24.5] | **23.7** [22.5–24.6] | **26.3** [24.1–27.0] | 1.11× | 0.37 | a2: 26.7 ± 0.2 · a3: 26.6 ± 0.1 · a1c1: 25.5 ± 0.7 |  |
| `fmul.s` | **26.0** [24.8–27.2] | — | **29.0** [27.6–29.5] | 1.12× | 0.37 | a2: 29.3 ± 0.1 · a3: 29.2 ± 0.02 · a1c1: 28.5 ± 0.5 |  |
| `fmadd.s` | **27.4** [26.6–28.2] | **27.6** [26.0–30.0] | **31.4** [30.0–32.1] | 1.15× | 0.37 | a2: 32.0 ± 0.1 · a3: 31.5 ± 0.02 · a1c1: 30.6 ± 0.3 |  |
| `fadd.ps (8 lanes)` | **22.4** [21.4–23.0] | **22.9** [22.4–23.3] | **41.1** [40.4–41.5] (5.1/lane) | 1.83× | 0.37 | a2: 41.4 ± 0.1 · a3: 41.4 ± 0.02 · a1c1: 40.6 ± 0.2 |  |
| `fmul.ps (8 lanes)` | **24.1** [22.7–25.3] | — | **49.2** [46.7–53.4] (6.2/lane) | 2.04× | 0.37 | a2: 50.9 ± 1.3 · a3: 48.9 ± 0.4 · a1c1: 47.8 ± 0.7 |  |
| `fmadd.ps (8 lanes)` | **27.1** [26.4–28.9] | **27.2** [26.4–28.3] | **55.8** [53.8–57.0] (7.0/lane) | 2.06× | 0.36 | a2: 55.6 ± 1.0 · a3: 56.2 ± 0.2 · a1c1: 55.4 ± 0.1 | 16 flops |
| `fadd.pi (8 lanes, int32)` | **12.7** [12.1–13.1] | **12.7** [12.2–13.4] | **19.8** [19.2–21.6] (2.5/lane) | 1.56× | 0.37 | a2: 20.6 ± 0.5 · a3: 19.7 ± 0.1 · a1c1: 19.2 ± 0.02 |  |
| `fmul.pi (8 lanes, int32)` | **24.8** [24.0–25.5] | **24.8** [24.2–25.5] | **50.0** [48.1–54.6] (6.3/lane) | 2.02× | 0.37 | a2: 50.9 ± 1.9 · a3: 49.5 ± 0.2 · a1c1: 49.8 ± 0.8 |  |
| `fexp.ps (8 lanes)` | **99.0** [96.5–102.2] | **98.7** [96.9–100.6] | **155.4** [147.3–162.4] (19.4/lane) | 1.57× | 0.09 | a2: 157.4 ± 2.9 · a3: 153.8 ± 3.3 · a1c1: 154.9 ± 1.2 | transcendental unit, ¼ the rate |
| `frcp.ps (8 lanes)` | **69.4** [67.2–73.9] | — | **111.5** [104.2–118.4] (13.9/lane) | 1.61× | 0.12 | a2: 114.7 ± 1.9 · a3: 112.1 ± 0.3 · a1c1: 107.6 ± 1.7 | transcendental unit |

Thirteen instructions trapped in U-mode in a one-off check while the catalogue was written (listed in [3.1](03a-every-instruction.md); the card and the log of that check were not kept), among them every float and vector divide and square root, as expected: this silicon has no hardware divide or square root for them.

**What the table says.**
- **An integer add on zeros, 6.2 pJ [5.6–6.9], costs little more than a `nop`** (5.1 pJ; 0.8–1.2 pJ more on each card): on zeros it is mostly the awake core that issues it (section 2). Random operands add 3.5 pJ.
- **A scalar float add costs 3.8× an integer add** even on zeros. The FPU does not gate on zero the way the tensor unit does.
- **An 8-lane vector op on zeros costs the same as the scalar op** (22.4 against 23.7 pJ, bars overlapping): lanes computing on zeros add nothing. On random data the eight lanes cost 1.8× — this is the data dependence of docs/findings/10-data-dependent-power.md, in the vector unit.
- **Per lane on random data, `fmadd.ps` is 7.0 pJ per multiply-add** [6.7–7.1]. The tensor unit below does the same multiply-add for 5.8 pJ [5.3–6.1]. Take out the vector instruction's issue — 4.4–5.1 pJ, what a fence or a nop costs (section 2) — and the lane is 6.3–6.4 pJ, about 10% above the tensor unit. Read that way, **of the 1.2 pJ per multiply-add the tensor unit saves, roughly half is instruction issue and the rest datapath** (54–64% issue on aifoundry2, 33–39% issue on aifoundry3 and 62–71% issue on aifoundry1 card 1, with the fence or the nop as the issue cost); that is arithmetic on rows whose operands differ (uniform in [0.5, 2) here, normal for the tensor unit), not a measured decomposition.
- **Integer vector adds are half the price of float ones** (12.7 vs 22.4 pJ on zeros); integer vector multiplies are not.
- **The transcendentals rank with the 64-bit divides as the dearest arithmetic**: `flog.ps` at 218 pJ and `fexp.ps` at 155 pJ for eight lanes, at a quarter of the rate, against 141–157 pJ for the 64-bit divides and remainders; `frcp.ps` (111) is cheaper, and `fexp.ps` is 2.8× a vector multiply-add. Only loads and stores that bypass the L1 (317–418 pJ) and atomics (351–1,450 pJ) cost more ([3.1](03a-every-instruction.md)).

## 3.2 The tensor unit

`TensorFMA` on a tile per instruction: fp32 16×16×16 = 4,096 multiply-adds, fp16 8,192, int8 16,384; 546 cycles per instruction for every pattern (318 for int8), all 1,024 minions, each run 7 s, launched at 80 °C (57 °C on aifoundry3): aifoundry3's values compare a cool card with warm ones. The registered switching values carry a launch-temperature offset (AMENDMENTS.md, note C2): they are referenced to 80.9 °C (aifoundry2 and aifoundry1 card 1) and 55.8 °C (aifoundry3) while the runs launched at whole-degree readings of 80.1, 57.4 and 80.0 °C in that order; the references were taken at launches on a downward step of the reading, so the die at these launches was at the reading or up to 0.96 °C above it, which the reading cannot tell apart, so at the die temperature of each launch aifoundry2's are between 0.62 W lower and 0.15 W higher, aifoundry3's are 0.91–1.43 W higher and aifoundry1 card 1's are between 0.73 W lower and 0.05 W higher: about 1.3–1.5 W of any difference between aifoundry3 and aifoundry2 comes from the reduction, most of the spread on the zeros rows; at the die temperature of each launch the fp32 rows read 0.24–0.41, 0.37–0.48 and 0.09–0.26 pJ per MAC on zeros and 5.76–5.93, 5.60–5.72 and 5.90–6.07 on random data (aifoundry2, aifoundry3 and aifoundry1 card 1). **Marginal** is board power above idle per multiply-add; **loaded** is total board power, idle included, per multiply-add, which is what a multiply-add costs when it is the only thing running.

The rows are the version-3 check's ablation (V3-ABL-A, 26 September), four runs on each of three cards; the bar on each row is the range over every run on every card: ±6–10% on random data and ±32–59% on zeros, most of it the difference between the cards. The rates are the same on every card (546 cycles per instruction, 318 for int8, in every timed launch). The loaded and W columns are aifoundry2's means. Until 25 September these rows were the 21 September ablation's two runs on aifoundry2 and, for fp32, the 22 September card transfer.

| Type, operands | pJ per MAC, marginal | per card | pJ per MAC, loaded (a2) | W over idle (a2) | MACs per second |
|---|---|---|---|---|---|
| TensorFMA fp32, zeros | **0.273** [0.141–0.445] | a2: 0.403 · a3: 0.163 · a1c1: 0.251 | 8.32 | 1.85 | 4.59 × 10¹² |
| TensorFMA fp32, ones | **2.131** [1.879–2.294] | a2: 2.258 · a3: 1.925 · a1c1: 2.211 | 10.17 | 10.37 | 4.59 × 10¹² |
| TensorFMA fp32, randn | **5.782** [5.347–6.133] | a2: 5.920 · a3: 5.369 · a1c1: 6.058 | 13.84 | 27.18 | 4.59 × 10¹² |
| TensorFMA fp16, zeros | **0.134** [0.076–0.234] | a2: 0.205 · a3: 0.082 · a1c1: 0.116 | 4.16 | 1.88 | 9.18 × 10¹² |
| TensorFMA fp16, ones | **1.067** [0.959–1.147] | a2: 1.126 · a3: 0.969 · a1c1: 1.104 | 5.09 | 10.34 | 9.18 × 10¹² |
| TensorFMA fp16, randn | **2.590** [2.397–2.730] | a2: 2.661 · a3: 2.410 · a1c1: 2.700 | 6.62 | 24.44 | 9.18 × 10¹² |
| TensorFMA int8, zeros | **0.060** [0.043–0.081] | a2: 0.080 · a3: 0.044 · a1c1: 0.056 | 1.23 | 2.51 | 3.15 × 10¹³ |
| TensorFMA int8, ones | **0.118** [0.098–0.148] | a2: 0.139 · a3: 0.099 · a1c1: 0.115 | 1.29 | 4.39 | 3.15 × 10¹³ |
| TensorFMA int8, randn | **0.295** [0.260–0.317] | a2: 0.313 · a3: 0.262 · a1c1: 0.309 | 1.47 | 9.88 | 3.15 × 10¹³ |

### Where the tensor unit's energy goes: per flip

The tensor unit is the one place on the chip where the energy has been resolved below the instruction, by simulating its RTL on the operands aifoundry2 actually ran (docs/findings/11-thermal-model.md). Four kinds of event, four energies fitted on that card:

| Event | fJ each | What it is |
|---|---|---|
| ffclk | 3.179 | register bit clocked |
| mult | 0.025 | net toggle in the multiplier tree |
| rest | 0.801 | other net toggle in the unit |
| bus | 15.539 | operand-word bit toggled outside the unit |
| tensor state machines | 1.81 mW per active minion | per minion, whatever the data |

A random-data 16×16×16 tile clocks 2.5 million register bits, toggles 74 million multiplier-tree nets and 13 million other nets, and toggles 140 thousand operand-word bits: at the energies above that is 27.2 W on 1,024 minions, and aifoundry2 measured 27.6 in the 21 September runs they were fitted to (27.2 in the four runs of 26 September). Zeros clock nothing (the lane clock is withheld when an operand word is zero) and cost 1.9 W. Structured matrices — Hadamard, DCT, butterfly, kaleidoscope and ten others — were priced this way to 0.9 W rms **before** they ran on aifoundry2 (one session, two runs each). The four energies are one fit on aifoundry2; their confidence is that 0.9 W rms over fourteen held-out patterns, and the 8% by which aifoundry3 runs below the fit on every pattern (section 8).

Sources: `docs/reports/data/2026-09-25-claims-v3/raw/<card>/catfull/` (the version-3 full catalogue, reduced by `tools/claims-v3/catfull/reduce.py` into `docs/reports/data/2026-09-23-energy-manual/catalogue.json`) (3.1), `docs/reports/data/2026-09-25-claims-v3/results/abla.runs.json` (3.2), `docs/reports/data/2026-09-21-horace-aifoundry2/model.json` (flips).
