# Finding: the same matmul costs 38 to 63 W depending on the operand values

**Sources:** E9 (the measurement), E11 and E13 (the RTL explanation), E15 (validation on new matrices),
R8 (the GPU result this reproduces). Published as A4.

---

## The result

Every run below does **identical arithmetic**: hart 0 of each of 1,024 minions repeats one 16×16×16 fp32
`TensorFMA` on a tile pair held in the L1 scratchpad, at 546.001 cycles per op, 600 MHz, 9.18 TFLOPS. The
clock and the core voltage never move. Only the numbers in A and B differ.

Board power is quoted at the launch temperature (80 °C), corrected for the leakage the run's own heating adds
during seconds 1–3. "Rise" is the de-quantised temperature gain over a 7.3 s run (see
[14-card-behaviour.md](14-card-behaviour.md) for why the raw sensor cannot give this directly).

| Operands (A and B) | Runs | Board W at 80 °C | ± sd | Rise in 7 s | m°C per 10¹² FLOPs | pJ/FLOP | pJ/FLOP over idle |
|---|---|---|---|---|---|---|---|
| zeros | 5 | **38.29** | 0.03 | +0.08 °C | 1.3 | 4.17 | 0.22 |
| checkerboard 1,0,1,0 | 2 | 40.94 | 0.04 | +0.04 | 0.6 | 4.47 | 0.51 |
| random normal, 75% zeroed | 2 | 41.04 | 0.05 | +0.26 | 3.9 | 4.49 | 0.55 |
| ternary −1, 0, 1 | 2 | 45.70 | 0.22 | +1.40 | 20.6 | 5.07 | 1.12 |
| random normal, 50% zeroed | 5 | 46.13 | 0.32 | +1.73 | 25.6 | 5.13 | 1.18 |
| **ones** | 5 | **46.73** | 0.07 | +1.81 | 26.8 | 5.21 | 1.26 |
| π everywhere | 5 | 46.96 | 0.02 | +1.83 | 27.0 | 5.23 | 1.28 |
| random sign, ±1 | 2 | 51.41 | 0.15 | +2.80 | 41.2 | 5.78 | 1.83 |
| random exponent, 2^k | 2 | 52.60 | 0.00 | +2.88 | 42.5 | 5.93 | 1.97 |
| A random, B ones | 2 | 54.29 | 0.10 | +2.87 | 42.5 | 6.13 | 2.19 |
| A ones, B random | 2 | 57.93 | 0.22 | +3.69 | 54.7 | 6.57 | 2.62 |
| random mantissa, [1,2) | 2 | 60.41 | 0.19 | +4.08 | 60.5 | 6.85 | 2.90 |
| random uniform [0,1) | 5 | 61.29 | 0.04 | +4.74 | 70.0 | 7.01 | 3.05 |
| **random normal** | 5 | **63.40** | 0.08 | +5.15 | 75.9 | 7.27 | 3.31 |

The idle card just before each launch drew 36.29 W ± 0.06.

### What to take from it

- **The runs cluster by kind, tightly.** Random normal repeats to 0.08 W across five *different* random
  matrices; zeros to 0.03 W. The run-to-run spread is far smaller than the gap between kinds.
- **Heating follows power over idle, not total power.** Zeros add 2.0 W to an idle card and the die gains
  under a tenth of a degree. Random normal adds 27 W and gains 5.2 °C. Hence 1 against 76 m°C per trillion
  FLOPs, while total energy per FLOP only moves from 4.2 to 7.3 pJ.
- **Over the idle card the data decides a factor of 15** in energy per FLOP (0.22 against 3.31 pJ).
- **Which bits are random matters.** Random signs alone cost 51.4 W, random exponents alone 52.6 W, random
  mantissas alone 60.4 W, all three 63.4 W.
- **Order matters.** One random operand with the other pinned at 1: 54.3 W when A is random, 57.9 W when B is.
- **Only the core rail moves.** Late in the run, random normal is 29.6 W above zeros at the board; the minion
  rail accounts for 21.5 W, SRAM and mesh for 1.0 W between them, and about 7 W never reaches the die at all
  (regulator loss, which grows with current).

## Why: three mechanisms, all visible in the RTL

Replaying the card's own operand tiles through eight copies of the chip's fused multiply-add unit (E11) gives
per-op, per-minion counts that explain the ordering:

| Operands | Multiply-adds not gated (of 4,096) | Register bits clocked | Net toggles | In the multiplier tree |
|---|---|---|---|---|
| zeros | 0 | 0.025 M | ~0 | — |
| ones | 4,096 | 2.47 M | 0.031 M | 3% |
| π | 4,096 | 2.47 M | 0.041 M | 2% |
| random normal | 4,096 | 2.47 M | **87.4 M** | 85% |

1. **Zero gating.** On an accumulate pass, `vpu_ctrl.v` withholds the valid bit from a lane whose A or B
   operand word is zero (signal `ex_fma_gate_mask`; the PRM's pseudo-code says the same, `if (a != 0 && b != 0)`).
   The pipeline registers are enabled by their stage's valid bit, so a gated lane **clocks no register and
   flips no net**. That is the zeros case: 2.0 W over idle for a full-rate matmul.
2. **Register clocking.** A valid multiply-add clocks about 600 register bits per lane on its way down the
   pipe whether or not the data changed. That is what a constant costs: 2.47 M bits per op at 3.18 fJ each is
   8.8 W across the chip, and ones measure 8.4 W more than zeros.
3. **Data toggles.** Random operands flip 87 M counted nets per op. 85% of those are in the multiplier tree,
   but the tree is cheap per toggle (0.025 fJ against 0.80 fJ elsewhere), so most of the *energy* is in the
   exponent path, aligner, adder and normaliser. This is why sign-only or exponent-only randomness, which
   leaves the tree still, still costs 5–6 W over ones.

**Negative zero is not zero.** The gating tests the all-zero bit pattern, so a matrix of −0.0 clocks every
register: 46.71 W, the same as ones, against 38.23 W for +0.0 (E15). In practice: mask with a select, not by
multiplying by zero, because `x · 0` is −0.0 for every negative x.

## Structured matrices: predicted before they ran

17 kinds of structured operand pair were generated (E13), their power predicted from the tiles alone and
**written to disk at 13:08:33**, and 14 of them run on the card starting at 13:16 (E14, E15).

| Matrix (A and B) | Multiply-adds not gated | Net toggles | Predicted W | Measured W | Error |
|---|---|---|---|---|---|
| identity | 16 | 0.04 M | 38.67 | 38.50 | +0.17 |
| butterfly factors | 64 | 1.09 M | 39.51 | 39.27 | +0.23 |
| random tridiagonal | 134 | 2.63 M | 40.54 | 40.20 | +0.34 |
| random 4×4 blocks | 256 | 5.29 M | 41.35 | 41.13 | +0.22 |
| random upper-triangular | 816 | 19.2 M | 45.51 | 44.42 | +1.09 |
| all −0.0 | 4,096 | 0.00 M | 47.16 | 46.71 | +0.46 |
| DFT, cos and sin parts | 2,272 | 13.4 M | 46.97 | 49.76 | **−2.79** |
| Hadamard, ±1 | 4,096 | 3.30 M | 50.16 | 50.07 | +0.09 |
| weights × ReLU activations | 2,024 | 37.2 M | 51.53 | 52.75 | −1.22 |
| 4-bit quantised random | 2,883 | 30.1 M | 53.47 | 54.21 | −0.74 |
| rank 1 | 4,096 | 87.0 M | 63.15 | 63.08 | +0.07 |
| circulant | 4,096 | 86.9 M | 63.60 | 63.82 | −0.22 |
| kaleidoscope (butterfly products) | 4,096 | 87.7 M | 63.68 | 63.86 | −0.18 |
| DCT-II | 4,096 | 81.9 M | 63.41 | 63.95 | −0.54 |

**0.92 W rms over a 25 W range**, and 11 of the 14 within 0.6 W.

- **Structure in the values buys nothing.** Kaleidoscope products (the family that generalises the FFT), the
  DCT, circulant and rank-1 matrices are dense, and they cost exactly what random normal costs: their mantissa
  bits are just as busy. A Hadamard matrix costs 50 W, like random signs — only the sign and the adder move.
- **Structure in the zeros buys a lot,** because it survives the gating. Butterfly factors keep 64 of 4,096
  products and cost 39.3 W, a whisker over zeros.
- **The worst miss is the DFT pair**, 2.8 W low. Its products cancel almost exactly, which works the
  normaliser harder than any pattern the flip energies were fitted on; one energy for every toggle outside the
  multiplier tree is too coarse there.

## Relation to the GPU result this reproduces

Horace He measured an A100 doing an 8192³ matmul at 257 TFLOPS on random data and 295 on zeros, and explained
it as: predictable data flips fewer transistors, draws less power, and a power-limited GPU then clocks higher
(R8).

On this card the *cause* is the same and much larger — 25 W of data-dependent power at identical FLOPs — but
the *effect* is different, because a hot die is pinned at 600 MHz by the firmware. Speed only moves when the
die starts cool; then zeros run at 11.4–11.8 TFLOPS and random data at 9.3, a 25% gap
([14-card-behaviour.md](14-card-behaviour.md)).
