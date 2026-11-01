# E107: where a large GEMM falls, by reuse and by the L3

*On the kinds page, [section 11, what is still open](https://spacesheep.dev/@yaroslavvb/horace-kinds-of-numbers#11-what-is-still-open): **item 1, "Where a large GEMM falls"**, as it reads at `1fe8377a18af`: "A sweep of block repeats would test whether reuse is the variable at all; 8 blocks, whose 24 MB of operands overflow the L2 and fit the L3, would separate the walk's limit, which is not measured. Then the vendor's own binary, which nobody here has timed."*

*Sun 1 Nov 2026 (week 44), Q133. Pre-registered in `c423a263` ([`tools/claims-v3/e107/E107.md`](../../../../tools/claims-v3/e107/E107.md), frozen numbers in `predictions-e107.json`, rules, scorer, self-test), before the claim and the first launch; amendment A1 `6db10fbe` (the smoke list) before the claim. Builds on [E101](../2026-11-01-e101-real-matmul/README.md) and [E105](../2026-11-01-e105-gemm-layout/README.md) and their tools. **aifoundry3 card 0 at its pinned 600 MHz**: TDP 0 / threshold 65 °C / 600 MHz / 523 mV read under the card lock at the session's start (11:14:26 PST) and end (12:02:54 PST) and at both ends of every pass; nothing set, no `--reset-ms`, no PMIC command. Claim `1566530805172543501` in #community-lab, posted 11:14:08 PST. 48.5 card-minutes: a smoke (11:14-11:16) and three passes (11:16-12:02), 284 of 285 planned runs, all kept.*

## The answer

**Reuse is the variable, and DRAM sets most of a fresh walk's pace.** At aifoundry3's pinned 600 MHz:

- **Passing over each of 16 fresh blocks R times before the walk moves on divides the walk's extra time per op by R.** T(R) = Tinf + D / R fits the five rungs to within 0.22% in fp32, 0.19% in fp16 and 0.49% in int8, with Tinf 0.8% under a repeated block's time in fp32 and fp16 and 3.0% under it in int8 (R3: REUSE IS THE VARIABLE, as frozen). A block's first pass costs what a pass of the cold walk costs, and every pass after it what a repeated block's pass costs: each fresh block adds 108.5 µs to every minion's work in fp32 (134 µs in int8).
- **With the 8 blocks' 24 MB of operands inside the L3, 31% of the cold walk's extra time stays** in fp32 and fp16, and 46% in int8 (R4: DRAM SETS MOST OF IT; frozen 27% and 39%). A line missing from the L2 that the L3 serves costs 4.15 ns of each op; one in the walk that goes to DRAM costs 13.25 ns, ×3.2. The walk leaves DRAM: the DDR rail droops 0.60 and 0.79 mV on zeros and random, as a repeated block does (0.48, 1.00), against 1.90 and 3.07 mV in the 16-block walk (R4c PASS). 4 blocks (14 MB) run within 0.02% of 8 (26 MB), so 26 MB stays resident (R4b PASS).
- **The L3 has to hold C as well.** With each block's C beside it, 40 MB in all, the same 8-block walk keeps 95% of the cold excess (R5: C ALLOCATES). Sharing C in the 16-block walk removes 14% of the excess, not the 40% frozen (R6: PARTIAL).
- **In the walk the L3 serves, minions finish unevenly**: the mean minion takes 749 cycles an op and the slowest 855, and the launch waits for the slowest. Every other arm, the DRAM walk and the whole repeat ladder included, finishes together (slowest ÷ mean 1.000-1.013). On the mean minion the 8-block walk would keep 21% of the excess, not 31% (post hoc).
- **So a large GEMM on this chip falls on two axes**: how many times each L2-sized block is reused before the walk moves on (the extra time divides by that number), and whether the walk's working set, its C included, fits the 32 MB L3 (a missing line costs about a third as much when it does). **E107 still does not run a large GEMM** and does not place one: that needs a GEMM's own reuse and footprint, the speed half (what a clock gap buys in each arm, which needs a governed card: it is left for later), and the vendor's binary, which can be built instrumented from public sources (below) and was not run.

| arm | what | A + B, with C | T at 600 MHz, µs: fp32 | fp16 | int8 | share of the cold excess, fp32 (frozen) | TFLOPS fp32 |
|---|---|---|---|---|---|---|---|
| `c1` | one block, repeated | 3, 5 MB | 0.8997 | 0.8998 | 0.4879 | 0 | 9.32 |
| `c16r32` | 16 blocks, each 32 times | 48, 80 MB | 0.9469 | 0.9469 | 0.5419 | 0.028 (0.031) | 8.86 |
| `c16r8` | each 8 times | 48, 80 MB | 1.1066 | 1.1065 | 0.7381 | 0.122 (0.125) | 7.58 |
| `c16r4` | each 4 times | 48, 80 MB | 1.3182 | 1.3184 | 0.9985 | 0.247 (0.250) | 6.36 |
| `c16r2` | each twice | 48, 80 MB | 1.7396 | 1.7402 | 1.5207 | 0.495 (0.500) | 4.82 |
| `c16` | 16 fresh blocks, once each | 48, 80 MB | 2.5958 | 2.5954 | 2.5822 | 1 | 3.23 |
| `c4s` | 4 blocks, C shared | 12, 14 MB | 1.4306 | 1.4305 | 1.4399 | 0.313 (0.270) | 5.86 |
| **`c8s`** | **8 blocks, C shared** | **24, 26 MB** | **1.4305** | **1.4303** | **1.4401** | **0.313 (0.270)** | **5.86** |
| `c8` | 8 blocks, C per block | 24, 40 MB | 2.5157 | 2.5165 | 2.3931 | 0.953 (1.0) | 3.33 |
| `c16s` | 16 blocks, C shared | 48, 50 MB | 2.3522 | 2.3517 | 2.3115 | 0.856 (0.6) | 3.57 |

T is 1,024 minions over the reducer's rate, the mean of the arm's kinds; every kind's T is within 0.10% of its arm's zeros (R2), and every 95% interval over the three passes is within ±0.005 µs (`scored.json` `T`, `cells.<item>.T_ci95`; `e107.json` `items.<item>.rate`). The share is (T − T(`c1`)) / (T(`c16`) − T(`c1`)) (`scored.json` `f`). Two things stand out beyond the rules: **the walk the L3 serves takes 1.43-1.44 µs an op in every format**, so the multiplier is wholly hidden there; and int8 keeps the largest share of the cold excess there, because its own FMA (0.49 µs an op) hides the least of the L3's service time.

## The repeat ladder: reuse is the variable

| format | Tinf, µs | T(`c1`), µs | Tinf ÷ T(`c1`) | D, µs | worst point off the fit | verdict |
|---|---|---|---|---|---|---|
| fp32 | 0.8928 | 0.8997 | 0.992 | 1.7012 | 0.22% | REUSE IS THE VARIABLE |
| fp16 | 0.8930 | 0.8998 | 0.992 | 1.7010 | 0.19% | REUSE IS THE VARIABLE |
| int8 | 0.4734 | 0.4879 | 0.970 | 2.1059 | 0.49% | REUSE IS THE VARIABLE |

(`scored.json` `rules.R3_reuse.per_format`.) The footprint, the addresses, the ops, C's traffic per op and DRAM's traffic per first pass are the same on every rung; only how many passes find a block's tiles in the L2 changes, and the extra time follows 1/R. The warm passes inside the walk run a little faster than the repeated block itself (Tinf under T(`c1`) by 0.8% and 3.0%), so the first-pass estimate R T(R) − (R − 1) T(`c1`) drifts from 2.596 µs at R = 1 to 2.409 at R = 32 in fp32 (`posthoc.txt` §2, labelled). The DDR rail's droop, read in whole millivolts, rises along the ladder from the repeated block's to the cold walk's (zeros 0.48 to 1.90 mV, random 1.00 to 3.07), roughly as DRAM's traffic per op does; it is too coarse to follow 1/R (`posthoc.txt` §6).

## Eight blocks inside the L3: the walk's limit

- **DRAM sets about 69% of the cold walk's extra time in fp32 and fp16, 55% in int8**; the rest is the L2's misses served by the L3. Frozen: 73% and 61%, from E101's packed arm, whose misses the L3 serves at 3.58 ns a line in fp32 against the 4.15 ns measured in this walk.
- **Is it DRAM's bandwidth?** Not by the bytes alone: past the L3 the cold walk moves 18.9 GB/s of A + B and 12.6 GB/s of C's stores at 600 MHz, under the lab's 47.9-53.4 GB/s past the L3 (`docs/findings/05-claims.md`), and the L2-miss traffic is 101 GB/s in the DRAM walk against 183 GB/s in the L3 walk (`posthoc.txt` §3, labelled). What DRAM costs per line here, 13.25 ns against 4.15, is its service time under this walk's traffic, latency and queueing together; E107 does not separate the two.
- **C counts twice**: as footprint (40 MB with C per block push the 8-block walk back to 95% of the excess, R5) and as traffic (sharing C in the 16-block walk takes 14% of the excess away, R6, against the 40% the bytes would give).

## Power and energy by kind

S, board power over each run's idle, W, and pJ per multiply-add, 95% over three passes (`e107.json` `items.<item>.S`, `.pj_mac_S`; E78's reducer, unchanged):

| arm | format | zeros, W | sparse50, W | random, W | random, pJ/MAC | zeros, pJ/MAC | zeros ÷ random |
|---|---|---|---|---|---|---|---|
| `c1` | fp32 | 3.78 ± 0.09 | 14.59 ± 0.21 | 31.89 ± 4.31 | 6.84 ± 0.93 | 0.81 | 0.119 |
| `c1` | fp16 | 3.71 ± 0.04 | 19.98 ± 0.46 | 29.96 ± 0.19 | 3.21 ± 0.02 | 0.40 | 0.124 |
| `c1` | int8 | 4.81 ± 0.45 | 15.67 ± 0.31 | 18.31 ± 2.82 | 0.53 ± 0.08 | 0.14 | 0.262 |
| `c16r4` | fp32 | 3.75 ± 0.07 | 11.82 ± 0.07 | 24.20 ± 0.41 | 7.60 ± 0.13 | 1.18 | 0.155 |
| `c16r4` | fp16 | 3.76 ± 0.18 | 15.42 ± 0.09 | 22.17 ± 0.86 | 3.48 ± 0.14 | 0.59 | 0.170 |
| `c16r4` | int8 | 4.05 ± 0.12 | 10.21 ± 0.29 | 12.15 ± 0.38 | 0.72 ± 0.02 | 0.24 | 0.333 |
| `c8s` | fp32 | 3.43 ± 0.06 | 11.50 ± 0.89 | 24.42 ± 0.29 | 8.33 ± 0.10 | 1.17 | 0.140 |
| `c8s` | fp16 | 3.68 ± 0.25 | 14.53 ± 0.82 | 21.72 ± 1.67 | 3.70 ± 0.29 | 0.63 | 0.169 |
| `c8s` | int8 | 2.85 ± 0.40 | 7.43 ± 0.44 | 9.25 ± 1.50 | 0.79 ± 0.13 | 0.25 | 0.308 |
| `c8` | fp32 | 3.93 ± 0.32 | 9.25 ± 0.24 | 15.61 ± 0.12 | 9.36 ± 0.07 | 2.36 | 0.252 |
| `c16` | fp32 | 3.87 ± 0.23 | 8.90 ± 0.41 | 15.18 ± 0.21 | 9.39 ± 0.13 | 2.40 | 0.255 |
| `c16` | fp16 | 3.94 ± 0.13 | 10.81 ± 0.19 | 14.31 ± 0.26 | 4.43 ± 0.09 | 1.22 | 0.275 |
| `c16` | int8 | 3.60 ± 0.21 | 7.03 ± 0.19 | 8.15 ± 0.15 | 1.25 ± 0.02 | 0.55 | 0.442 |

Every arm and format, zeros and random: [`results.md`](results.md).

- **The kind of number still sets the power in every regime, and the regime sets how much of it is spent per op.** A random fp32 multiply-add costs 6.84 pJ with the tiles in the L2 (7.06 on two passes; E105 7.08), 7.60 with each block used four times, 8.33 when fresh blocks come from the L3 and 9.39 when they come from DRAM (R8 PASS: the energy per op rises along the ladder).
- **Zeros' energy per op triples in the DRAM walk** (0.81 to 2.40 pJ a multiply-add in fp32), and zeros' share of random's watts doubles (0.12 to 0.26): moving a fresh block costs energy whatever the numbers in it, and DRAM's part of that is the largest.
- **The frozen power model held**: on the 48 cells of the eight new arms, rms 0.95 W (R7 PASS).
- **One held board reading.** Pass 10712's `c1.fp32.randn` holds 30.99 W on two samples at a launch boundary (t0 + 1,589 and 1,689 ms) while the minion rail kept rising, and reads 29.88 W against 32.89 and 32.88 in the other passes; that is the ±4.31. Without the two samples it reads 32.7 W (`glitches.txt`, labelled; no registered number changes). Of the 28 runs with a board sample more than 10 W under their window's median, 24 are `c4s` and `c8s`, where those samples are the real tails of launches that wait for the slowest minion.

## Registered against what happened

284 runs, three passes, none set aside, no run failed a gate; one run was not started (`p10711` #78, `c16r32.int8.zeros`: its launch reading was not reached, E78's rule, as in E101's C3), so that item rests on two passes. Leakage slope, the registered `auto`, 0.2105 W/°C over 168 runs; idle consistency median 0.063 W; carry-over +0.0037 ± 0.0018 W/W; the pi tie drifts +0.11, +0.14, −0.05 W first to last (`e107.json` `checks`, `tie_drift_w`).

| rule | registered | measured | verdict |
|---|---|---|---|
| R1 the ties | T(`c1`) within 2%, T(`c16`) within 3% of E105's, each format | fp32 −0.02% and −0.13%; fp16 −0.01% and −0.16%; **int8 `c1` −2.3%** (0.4879 against 0.4993 µs; 290.0 against 296.6 cycles per op), `c16` −0.22% | **FAIL** |
| R2 the kind | each kind within 1% of zeros' T | worst 0.10% over 45 | **PASS** |
| R3 reuse | Tinf within 5% of T(`c1`), every point within 3% of the fit | 0.992 / 0.992 / 0.970; 0.22 / 0.19 / 0.49% | **REUSE IS THE VARIABLE**, all three |
| R4 the walk | f8 ≤ 0.50 DRAM; ≥ 0.85 not | 0.313 / 0.313 / 0.455 (frozen 0.270 / 0.270 / 0.394) | **DRAM SETS MOST OF IT** |
| R4b residency | c4s within 5% of c8s | 0.01 / 0.02 / 0.01% | **PASS** |
| R4c the DRAM check | droop(c8s) − droop(c1) ≤ half of droop(c16) − droop(c1) | zeros +0.12 against half of +1.42 mV; random −0.21 against half of +2.07 | **PASS** |
| R5 C in the L3 | f8c ≥ f8 + 0.30 | 0.953 against 0.313 | **C ALLOCATES** |
| R6 C's traffic | f16s ≤ 0.85 part, ≥ 0.95 not | 0.856 (frozen 0.6) | **PARTIAL**: the frozen size failed |
| R7 power | rms ≤ 2.0 W, 48 cells | 0.95 W | **PASS** |
| R8 energy order | rising along the ladder | 28.01 < 29.14 < 29.64 < 31.15 < 33.49 < 38.48 nJ an op | **PASS** |

**R1 failed, so every other verdict is labelled, as registered.** fp32 and fp16 tie E105 to 0.16% at both ends, and int8's cold end to 0.22%; int8's repeated block runs 2.3% faster than E105's binary did, 290.0 cycles per op against 296.6, on the same card and clock, in every launch and kind. rgm107's kernel source differs from rgm105's only by the repeat loop and the shared-C select, and the compiled `entry_point` differs (6,554 against 6,592 bytes): int8's 280-cycle FMA hides less of the loop than fp32's 529 do, so a different instruction schedule shows there first. Which instructions cost E105's binary the 6.6 cycles was not traced. It moves the int8 rows: with E105's T(`c1`) int8's f8 would read 0.452 against 0.455, and the ladder's Tinf 0.948 of it against 0.970. No verdict changes.

**Why the frozen numbers missed.** R4's share came in higher than frozen (0.313 against 0.270) because an L3-served line costs 4.15 ns in a cold walk against 3.58 in E101's packed repeated block; and on the mean minion the walk keeps 0.209. R6's 0.6 assumed DRAM's cost follows its bytes; C's stores take 14% of the excess, not 40%. R5's 1.0 assumed nothing survives 40 MB cycling through 32 MB; 0.953 reads as a little surviving (a reading, not measured).

## The vendor's own binary: can an instrumented build be made from public sources?

*Desk only: nothing was built or run. Section 11 item 1's last sentence.*

**Yes, from public sources alone, with two libraries the boxes do not have installed.**

- **The kernel** is in et-platform (`external/et-platform` at `836a4ab60`, Apache-2.0): `gp-sdk/device/sdk/libautogen/matmul_f32_1024_512_512/`, a static library whose entry, `uberKernel_RAWKERNEL_entry_point`, is gp-sdk's test kernel `autogen_matmul.elf` (`gp-sdk/device/tests/CMakeLists.txt` lines 136-137, `tests/autogenMatmul/autogen_matmul.cpp`). **Its host** is `gp-sdk/host/sdk/src/autogen_matmul/autogen_matmul.cpp`, the `matmul_launcher` executable (`gp-sdk/host/sdk/CMakeLists.txt` lines 104-109; `-k` kernel, `-n` launches, `-d sysemu|fake|silicon`).
- **What the boxes lack:** `libautogen` links `dnnLibrary::dnn_lib`, and the launcher links gp-sdk's `etsoc_gpsdk`. aifoundry3's `/opt/et`, listed today, has et-common-libs, the runtime, the device layer, sw-sysemu and the RISC-V toolchain, and neither dnnLibrary nor gp-sdk. et-platform's own superbuild builds both from the same tree (its `CMakeLists.txt` lines 67-97: `DeviceProject(dnn-library ...)`, then gp-sdk's `HostProject(host ...)` and `DeviceProject(device ...)`).
- **The instrumentation** is the minion cycle counter the lab's kernels already read (`hpmcounter3`; et-common-libs `include/etsoc/drivers/pmu/pmu.h` has the read), at the entry and the exit of `startUberKernelComputes` on each compute hart (thread 0 of shires 0-31, `uberKernel.cc` line 42), written to one 64-byte line per hart in a buffer the launcher reads back, as this lab's `SpResult` does. That gives each launch's compute time with the 2 ms launch overhead out of it, and needs no loop inside the launch. The helper threads have nothing to time: `MatmulCmd_act_pref.cc` and `MatmulCmd_w_pref.cc` only send credits, as E101 found.
- **"About 58 µs a launch" is not a timing.** It is E101.md's desk figure, 64 ops a minion at the FMA's 546 cycles and 600 MHz (58.2 µs). Nobody here has timed the binary.
- **What E107 adds** (a desk prediction, labelled): the vendor's launch is one cold pass over one block, and the host's upload leaves A and B in the L3 (a host write allocates in its line's L3 home, `docs/findings/05-claims.md`, T34-A). That is E107's L3-served cold pass with the vendor's strides, which the desk L2 model has missing 80.2% of lines in a cold pass (154 of 192). At an L3-served line's price, 3.58 ns (E101's packed arm) to 4.15 ns (this walk), one launch would take **about 93-98 µs** at 600 MHz, not 58 (`posthoc.txt` §4). For whoever times the instrumented build.

## The speed half: not measured here

aifoundry3's clock is pinned, so what a clock gap buys in each arm needs a governed card (aifoundry2, E111's today); it is left for later, and E107's power per kind on every arm is the input that card's run would predict its clocks from (E105's rule: estimate from the same kind's S on a pinned card). A bound only, labelled: if no more than the FMA's 529 cycles of an fp32 op follow the clock, as in every fp32 arm E105 fitted, ×1.333 of clock buys at most ×1.324 in `c1`, ×1.201 in `c16r4`, ×1.182 in `c8s` and ×1.093 in `c16` (`scored.json` `speed_half_bound_fp32`). E105 measured ×1.324 and ×1.064 at the two ends on aifoundry2.

## Departures

- **A1, before the claim:** the smoke list named an item that does not exist; it was replaced (E107.md).
- **sys_emu could not check the new paths**: it aborts any SP_GEMM launch that stores a C tile twice, E105's own binary included (`tools/claims-v3/e107/sim-check.txt`). The smoke (`aifoundry3/e107-smoke/p10701`) ran every new arm once: every check of C exact or approx, none wrong; so did every run of the passes (`ok_records`). The smoke's 2 s runs do not cover the reducer's power window, so its rates read long; it was a plumbing check and nothing here uses it.
- **One run not started** (`p10711` #78), as above.
- **R1 failed** on int8's repeated block, as above; every verdict is labelled.
- **Written after the data, labelled, never a verdict:** `posthoc_e107.py` (`posthoc.json`, `.txt`: the price of a missing line, the first pass, the traffic, the vendor prediction, the speed bound, the rails per op) and `glitch_e107.py` (`glitches.txt`), and the minion spread above, from the launch records' `cycles_max` and `cycles_mean`.
- The reduction ran on the Intel (`uv` for numpy), with the committed code and inputs.
- The session took 48.5 card-minutes against the brief's 60; the queue's deadline never bound.

## What E107 says about the page

- **§11 item 1 narrows; it does not close.** It may read: reuse is the variable (a block's extra time divides by its passes, to 0.5%, at 600 MHz on aifoundry3); DRAM sets about two thirds of a fresh walk's extra time and the L3-served path the rest (31% in fp32 and fp16, 46% in int8); the L3 must hold C as well; a large GEMM is still not placed: it needs its own reuse and footprint, the speed half on a governed card, and the vendor's binary, which public sources can build instrumented (dnn-library and gp-sdk) and nobody has timed. It must say R1 failed on int8's repeated block, labelled.
- **The regimes section** may add two measured conditions to E105's three, none a GEMM on real data: (4) fresh blocks inside the L3: 1.43 µs an op in every format at 600 MHz on aifoundry3, minions uneven; (5) a block used R times in a walk past the L3: the cold excess over R. It may state the map: extra time per op = (misses per op ÷ reuse) × (4.15 ns from the L3, 13.25 ns in this DRAM walk), for this partition at 600 MHz, labelled as E107's arms.
- **§2** may add: a random fp32 multiply-add costs 6.84 pJ with the tiles in the L2, 7.60 with each block used four times, 8.33 with fresh blocks from the L3, 9.39 from DRAM, at 600 MHz on aifoundry3 (three passes); zeros 0.81 to 2.40 pJ.
- **§3, speed:** nothing new about a clock gap; the bound only.
- **§6 item 6, the power model:** the memory path's term now has two prices per missing line, from the L3 and from DRAM (labelled).

**For the post, in short sentences.** Each names its card and clock.
- On aifoundry3 at 600 MHz, reading each of 16 fresh blocks twice before moving on halves the extra time a fresh walk costs; four times quarters it; 32 times leaves 3% of it (`scored.json` `f`).
- Each fresh block costs every minion about 109 µs more than a block already in its L2, in fp32 (`posthoc.txt` §2).
- When the walk's 24 MB of operands sit in the 32 MB L3, about two thirds of that extra time goes: DRAM was most of it (`scored.json` `rules.R4_walk`).
- A line the L3 serves costs 4 ns of each op; a line from DRAM in the same walk costs 13 ns (`posthoc.txt` §1).
- The L3 has to hold the results too: with each block's output beside it, the 8-block walk is as slow as the 16-block one (`scored.json` `rules.R5_c_in_l3`).
- The kind of number still sets the power in every case: a random fp32 multiply-add costs 6.8 pJ with the tiles in the L2 and 9.4 pJ when they come from DRAM; zeros cost 0.8 and 2.4 (`e107.json` `items.c1.fp32.*`, `items.c16.fp32.*`).
- Nothing here places a large GEMM; it gives the two axes one falls on: how often each block is reused, and whether the working set fits the L3.

## Files

`e107.json`, `runs.csv`, `reduce.txt`, `reduce.log` (`tools/claims-v3/e107/reduce_e107.py`: E78's reducer, byte-identical, with E107's items); `rails-e107.json` (`rails_e107.py`); `scored.json`, `results.md` (`score_e107.py`); `posthoc.json`, `posthoc.txt` (`posthoc_e107.py`, labelled); `glitches.txt` (`glitch_e107.py`, labelled); `aifoundry3/e107/p1071[0-2]/` (every pass's raw data: `runs.jsonl`, `marks.jsonl`, `telemetry.jsonl.gz`, `tiles/`, `config_start.json`, `config_end.json`, `manifest.txt`, `binaries.sha256`, `code.sha256`, `gen.sha256`, `configs.json`, `plan.json`, `run.log`, `block.json`); `aifoundry3/e107-smoke/p10701/`; `logs/` (the queue, the watcher, the smoke, the build, the dry run, the session's two config reads, the queue's binaries' sha256). The registration, binary and code: [`tools/claims-v3/e107/`](../../../../tools/claims-v3/e107/README.md).
