# 3. Instructions

Energy per instruction retired, above idle, at 600 MHz and 0.517 V, with both harts of all 1,024 minions running the instruction flat out. Three operand sets: all zeros, one constant everywhere, and random values in [0.5, 2). The last column is the same measurement on the second card.

## 3.1 Scalar and vector units

| Instruction | zeros pJ | constant pJ | random pJ | random / zeros | issue rate per hart | aifoundry3, random | Note |
|---|---|---|---|---|---|---|---|
| `add` | 6.6 | 6.9 | **9.6** | 1.44× | 0.37 | 9.3 |  |
| `xor` | 6.1 | 6.4 | **8.7** | 1.42× | 0.37 | 8.8 |  |
| `mul` | 24.1 | 31.0 | **41.4** | 1.72× | 0.04 | 38.9 | 64-bit, multi-cycle: 1/8 the rate, so most of this is the awake core amortised over a slow op |
| `fadd.s` | 23.2 | 23.5 | **26.1** | 1.12× | 0.37 | 25.1 |  |
| `fmul.s` | 25.8 | 25.5 | **29.2** | 1.13× | 0.37 | 28.1 |  |
| `fmadd.s` | 27.4 | 27.2 | **31.3** | 1.14× | 0.37 | 30.3 |  |
| `fadd.ps (8 lanes)` | 24.0 | 23.9 | **43.3** (5.4/lane) | 1.81× | 0.36 | 41.3 |  |
| `fmul.ps (8 lanes)` | 25.5 | 25.4 | **51.0** (6.4/lane) | 2.00× | 0.37 | 48.7 |  |
| `fmadd.ps (8 lanes)` | 27.8 | 28.3 | **59.4** (7.4/lane) | 2.13× | 0.37 | 56.3 | 16 flops |
| `fadd.pi (8 lanes, int32)` | 13.0 | 13.3 | **20.5** (2.6/lane) | 1.57× | 0.37 | 19.7 |  |
| `fmul.pi (8 lanes, int32)` | 25.7 | 27.0 | **52.5** (6.6/lane) | 2.04× | 0.36 | 48.9 |  |
| `fexp.ps (8 lanes)` | 105.1 | 104.2 | **166.9** (20.9/lane) | 1.59× | 0.09 | 156.6 | transcendental unit, ¼ the rate |
| `frcp.ps (8 lanes)` | 76.5 | 77.0 | **121.0** (15.1/lane) | 1.58× | 0.15 | 113.4 | transcendental unit |

`fdiv.ps` and `fsqrt.ps` trap: there is no hardware divide or square root in U-mode on this silicon.

**What the table says.**
- **An integer add is the cheapest thing a core does, 6.6 pJ on zeros**, and almost all of that is the awake core (section 2: 7.4 pJ per `addi`). Random operands add 2.9 pJ.
- **A scalar float add costs 3.5× an integer add** even on zeros. The FPU does not gate on zero the way the tensor unit does.
- **An 8-lane vector op on zeros costs the same as the scalar op** (24.0 against 23.2 pJ): idle lanes are free. On random data the eight lanes cost 1.8× — this is the data dependence of docs/findings/10-data-dependent-power.md, in the vector unit.
- **Per lane on random data, `fmadd.ps` is 7.4 pJ per multiply-add**, and its marginal cost over the `addi` loop is 6.5 pJ. The tensor unit below does the same multiply-add for 6.0 pJ. **The datapath energy per multiply-add is the same in both units; what the tensor unit saves is instruction issue.**
- **Integer vector adds are half the price of float ones** (13.0 vs 24.0 pJ on zeros); integer vector multiplies are not.
- **Transcendentals are the most expensive instructions on the chip**: `fexp.ps` at 167 pJ for eight lanes is 2.8× a vector multiply-add, at a quarter of the rate.

## 3.2 The tensor unit

`TensorFMA32` on a 16×16×16 tile, 4,096 multiply-adds per instruction, 546 cycles per instruction for every pattern (318 for int8), all 1,024 minions, launched at 80 °C. Marginal is above idle; loaded is total board power divided by the rate, which is what a multiply-add costs when it is the only thing running.

| Type, operands | pJ per MAC, marginal | pJ per MAC, loaded | W over idle | MACs per second |
|---|---|---|---|---|
| TensorFMA fp32, zeros | **0.416** | 8.32 | 1.91 | 4.59e+12 |
| TensorFMA fp32, ones | **2.300** | 10.21 | 10.56 | 4.59e+12 |
| TensorFMA fp32, randn | **6.017** | 13.92 | 27.63 | 4.59e+12 |
| TensorFMA fp16, zeros | **0.207** | 4.16 | 1.90 | 9.18e+12 |
| TensorFMA fp16, ones | **1.094** | 5.04 | 10.05 | 9.18e+12 |
| TensorFMA fp16, randn | **2.699** | 6.65 | 24.78 | 9.18e+12 |
| TensorFMA int8, zeros | **0.082** | 1.23 | 2.57 | 3.15e+13 |
| TensorFMA int8, ones | **0.134** | 1.29 | 4.22 | 3.15e+13 |
| TensorFMA int8, randn | **0.316** | 1.47 | 9.98 | 3.15e+13 |

### Where the tensor unit's energy goes: per flip

The tensor unit is the one place on the chip where the energy has been resolved below the instruction, by simulating its RTL on the operands the card actually ran (docs/findings/11-thermal-model.md). Four kinds of event, four fitted energies:

| Event | fJ each | What it is |
|---|---|---|
| ffclk | 3.179 | register bit clocked |
| mult | 0.025 | net toggle in the multiplier tree |
| rest | 0.801 | other net toggle in the unit |
| bus | 15.539 | operand-word bit toggled outside the unit |
| tensor state machines | 1.81 mW per active minion | per minion, whatever the data |

A random-data 16×16×16 tile clocks 2.5 million register bits, toggles 74 million multiplier-tree nets and 13 million other nets, and toggles 140 thousand operand-word bits: at the energies above that is 27.2 W on 1,024 minions, and the card measures 27.6. Zeros clock nothing (the lane clock is withheld when an operand word is zero) and cost 1.9 W. Structured matrices — Hadamard, DCT, butterfly, kaleidoscope and ten others — were priced this way to 0.9 W rms **before** they ran.

Sources: `docs/reports/data/2026-09-23-enercat-aifoundry2/` (3.1), `docs/reports/data/2026-09-21-horace-aifoundry2/ablation.json` (3.2), `docs/reports/data/2026-09-21-horace-aifoundry2/model.json` (flips).
