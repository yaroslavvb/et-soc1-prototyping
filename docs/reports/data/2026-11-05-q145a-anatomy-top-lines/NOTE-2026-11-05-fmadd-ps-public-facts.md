# Dated note, Thu 5 Nov 2026: the vector fmadd.ps - public facts beside the energy manual's fmadd.ps row (post hoc)

*Written Thu 5 Nov 2026 (week 45), about 22:40-23:20 PST, on the Intel, desk only, by Q145(a). It sits beside the energy
manual's `fmadd.ps (8 lanes)` row ([`docs/energy-manual/03-instructions.md`](../../../energy-manual/03-instructions.md), line 19) and
changes nothing there. Every figure is computed by [`anatomy_q145a.py`](anatomy_q145a.py) from public source at a pinned commit
or from the lab's committed catalogue, and is printed in [`anatomy.json`](anatomy.json) under `virus`, `vector` and `extras`.
Post hoc: nothing is a prediction or a verdict. It holds public facts only.*

## 1. Esperanto's public vector power virus

- **Where:** github.com/aifoundry-org/et-platform at `836a4ab60`, `test-compute-kernels/src/vpu_txfma_power_virus/kernel.h`
  (sha256 `24c8ce52...1cd64715`; the operand sets in `vpu_pv_setup0()` and `vpu_pv_setup1()`, the loop in `vpu_power_virus()`);
  the same loop at the RTL in github.com/openhwfoundation/core-et at `b38a1a3`,
  `dv/tests/minion_core/c_asm_tests/power_vpu/ps/kernel.h` (sha256 `53d1236b...e7714219`), whose operands are written as decimal
  floats: converted to fp32 they equal et-platform's words, all 96 of them.
- **What it runs:** thread 0 of each minion loads one set of operands and thread 1 another. Each hart then repeats
  `fmadd.ps f(even), f1, f2, f3` and `fmadd.ps f(odd), f28, f29, f30`, alternating, 20 pairs a loop, and checks the results
  against gold values every loop. So every instruction's three source operands differ from the previous instruction's on that
  hart, and the two triples are random-looking floats: exponent bytes 0x7c to 0x82 (magnitudes from 0.125 to just under 16), 14.3 (hart 0) and 14.6
  (hart 1) one-bits a word.
- **Its operand-port bit flips** (three source ports of eight 32-bit lanes, 768 bits; the Hamming distance from one instruction's
  operands to the next's): **334 an instruction on hart 0 and 348 on hart 1** as each hart alternates its two triples; **318, 348,
  352 and 322 (mean 335)** if the two harts' instructions alternate one for one at the unit's ports.
- **The lab's catalogue loop, against it** (`workloads/enercat`: `kernel/enercat.c` VMABLOCK, `host/main.cpp` `sources()`): eight
  instructions rotate the sources f0-f7, so no port reads the same register twice running, and every word is a float drawn uniform
  in [0.5, 2): the sign is 0, the exponent 0x7e or 0x7f (probability 1/3 and 2/3), the 23 mantissa bits uniform. Two such words
  differ in 11.5 + 4/9 = 11.94 bits on average, so **the random rotation flips about 287 operand bits an instruction (286.7
  expected)**. The constant column (1.0f, 0x3f800000, in every word) flips **0**.
- **So the virus switches like random data, not like the constant column:** 318-352 operand-port flips an instruction against
  about 287 for the lab's random rotation and 0 for its constant.

## 2. The lab's random fmadd.ps, re-read from the catalogue

From `docs/reports/data/2026-09-23-energy-manual/catalogue.json` (26 Sep 2026; three passes on each of aifoundry3, aifoundry1 card
1 and aifoundry2; 600 MHz; both harts of all 1,024 minions; above each burst's idle):

| | aifoundry3 | aifoundry1 card 1 | aifoundry2 | the three cards |
|---|---:|---:|---:|---:|
| board, pJ an instruction (the catalogue's convention: watts x wall seconds / instructions) | 56.25 | 55.44 | 55.59 | **55.76** (n 9; the manual's 55.8) |
| minion rail, pJ an instruction, the same convention | 46.16 | 47.54 | 46.00 | **46.57** |
| minion rail, pJ an instruction, at the device-time rate (`ops_per_s`) | 45.99 | 47.33 | 45.83 | 46.38 |
| board over minion rail, one convention | 1.218 | 1.166 | 1.208 | - |
| issues per hart-cycle, both harts running | 0.3649 | 0.3651 | 0.3648 | **0.730 per minion-cycle** |
| issues per hart-cycle, one hart (`fmadd.ps/random/h1`) | 0.5814 | 0.5814 | 0.5814 | - |

- The wall-time and device-time rates differ by 0.4% (3.212 s of wall against 3.200 s of device time a burst); a board figure
  at one rate beside a rail figure at the other (55.76 with 46.38 pJ) mixes the two.
- **The two-hart issue rate is the core's, not the unit's:** across the catalogue's 150 random-data, two-hart instruction rows, the
  fastest is `nop` at 0.390 issues per hart-cycle (0.78 per minion-cycle); 102 of the 150 sit at 0.30-0.45, the median at 0.369,
  and `fmadd.ps` issues at 94% of the `nop`'s rate.
- **Not measured:** the virus's own issue rate and power on these cards. A card run of either the TXFMA or the TIMA virus is a new
  kernel class: the kinds harness runs one TensorFMA on tile files and cannot run it.
