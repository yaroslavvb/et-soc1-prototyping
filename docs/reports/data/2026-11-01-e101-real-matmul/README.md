# E101: the same kinds of numbers in a matmul that streams its operands

*Sun 1 Nov 2026 (week 44), Q132, the top gap named by the previous round's final critic: every per-kind number on the [kinds page](https://spacesheep.dev/@yaroslavvb/horace-kinds-of-numbers) comes from one 16×16 TensorFMA repeating on resident tiles, and a real matmul also streams its tiles. Pre-registered in `bb860eb4` ([`tools/claims-v3/kinds/E101.md`](../../../../tools/claims-v3/kinds/E101.md), frozen numbers in `predictions-e101.json`, rules in `rules-e101.json`, scorer and self-test), before the claim and the first launch; amendments A1 `ddf59efa`, A2 `5057ccbc`, A3 `be2cb1a7` before the claim, A4 `c72e7e05` after the smoke and before the first pass. Session 1: aifoundry3 card 0 at 600 MHz, TDP 0 / threshold 65 °C / 600 MHz / 523 mV read under the card lock at the session's start (01:24:16 PST) and end (02:28:36 PST), never set. Nothing was written to the card and no `--reset-ms` was sent. Claim 1566382343843881015 in #community-lab, posted 01:24:12 PST, released 02:28 PST. Session 2, the clock under aifoundry2's own governor (A5 `bc053660`), ran 04:20–05:03 PST and **ended on its registered 97 W stop at run 82 of 96.***

**Which real matmul this is.** The critic took the benchmark's source to be outside the repo; it is in it (`kernels/mmbench`), and so, in the vendored SDK, is **the vendor's real GEMM**, `gp-sdk/device/sdk/libautogen/matmul_f32_1024_512_512`: C (1024 × 512) = A (1024 × 512) × B (512 × 512), fp32, with a partition under which one shire's operands come to 512 KB, the size of its L2, **cooperative loads** (the 8 minions of a neighbourhood load one A tile together, the 4 minions at one position load one B tile together), and a TensorStore per output tile. So this experiment runs a ladder, every rung on the same kinds and in E78's frame: `res` is the page's loop; `tenb` is E39's, B streamed; `mm16` is the benchmark's loop, op for op; **`gemm1` is the vendor kernel's partition, cooperative loads and stores, in all three formats, one block repeated inside a launch; `gemm16` walks 16 blocks, 48 MB of operands, past the 32 MB L3**; `gemmnc1` is `gemm1` with no cooperation; `mmp64` is the benchmark on private pools, from DRAM. **What stays different from a production GEMM:** only fp32 has a vendor kernel, and fp16 and int8 are that pattern with the type changed and K scaled, written here; tiles are packed where the vendor strides a row-major matrix; a block repeats where a production run walks new ones, and `gemm16` never accumulates C across blocks; a launch every 0.5 s. E101.md says all of it. The kernel is [`tools/claims-v3/rgm/`](../../../../tools/claims-v3/rgm/README.md).

## The answer: do the page's headline gaps survive a real matmul?

**Not as speed, in this real GEMM. The kind of number still sets the power, the heat and the clock, but here the memory sets the pace, so the clock buys little.** And "int8 hardly slows" is true of the loop and of the GEMM and false of the benchmark. Rates are the kernel's own, zeros over random, on aifoundry2 under its own governor (`results-speed.json` `rules.S1_fp32_burst.cells`, `rules.S2_fp32_sustained.cells`):

| format | arm | zeros ÷ random, burst, rate | sustained, rate | the page's (the loop's) |
|---|---|---|---|---|
| fp32 | the loop, `res` | ×1.15 (clock ×1.12) | not reached | ×1.13–1.15, ×1.29–1.33 |
| fp32 | the benchmark, `mm16` | not measured | not measured | |
| fp32 | a real GEMM, `gemm1` | ×1.03 (clock ×1.06) | ×1.09 (clock ×1.27) | |
| fp16 | the loop, `res` | ×1.12 (clock ×1.10) | not reached | ×1.12–1.13, ×1.30–1.32 |
| fp16 | the benchmark, `mm16` | not measured | not measured | |
| fp16 | a real GEMM, `gemm1` | ×1.01 (clock ×1.03) | ×1.06 (clock ×1.18) | |
| int8 | the loop, `res` | ×1.00 (clock ×1.00) | not reached | ×1.00, ×1.01 |
| int8 | the benchmark, `mm16` | ×1.17 (clock ×1.14) | ×1.32 (clock ×1.32) | |
| int8 | a real GEMM, `gemm1` | ×1.00 (clock ×1.00) | ×1.00 (clock ×1.01) | |

- **fp32:** the loop, re-read this session, is the page's: ×1.145 in the burst. **The real GEMM's gap is ×1.03 in the burst and ×1.09 sustained**, though its clocks part by ×1.06 and ×1.27: S1 SHRINKS and S2 FAILS, against a frozen prediction of about ×1.2 and ×1.33.
- **fp16:** the GEMM's ×1.01 and ×1.06, clocks ×1.03 and ×1.18.
- **int8:** the GEMM hardly slows, ×1.00 and ×1.00 (S3 HARDLY, against the frozen SLOWS), because the memory holds it far under both limits. **The benchmark slows like fp32 does on the page: ×1.17 and ×1.32 (S3 SLOWS),** 95.6 against 81.9 TOPS and 94.9 against 71.8.
- **The benchmark's random fp32 and fp16 were not measured:** the session hit its 97 W stop on the way to them. On the measured watts the relation expects ×1.27 and ×1.22 by clock in the burst and ×1.33 sustained (`tools/claims-v3/kspeed/e101/predictions-session1.json`, labelled).
- **So the gap belongs to the regime.** Where the multiplier sets the pace (the loop, the benchmark) the clock is the speed and the gap shows, in int8 too once the streaming watts reach the limits. Where the memory sets it (this GEMM) the gap all but goes. A production GEMM sits somewhere between, and E101 does not say where: **this GEMM is one block of the vendor's pattern, not the vendor's binary in a tuned run.**

**What stays different from a production GEMM.** Only fp32 has a vendor kernel, and fp16 and int8 are its pattern with the type changed and K scaled, written here. Tiles are packed where the vendor strides a row-major matrix. One block repeats inside a launch at 0.5 s a launch; `gemm16` cycles 16 blocks without accumulating C across them. No helper threads (the vendor's are empty in this kernel). Nobody in this lab has timed the vendor's own binary, so nothing yet says its pace matches.

## Results of session 1: power at a pinned 600 MHz

**In plain words.**

- **The first cooperative loads in this lab worked, and the kernels compute the right thing on every kind.** Every process checked C against the host's own reference: zeros and every int8 run exact, nothing wrong (`scored.json` `rules.R9_correct`). **The data never changes the cycle count, streaming or not:** every kind in an arm and format within 0.03%, and within 0.41% in the DRAM arm, whose count wanders from launch to launch anyway (R9b).
- **The benchmark's loop is E37's:** 529.0 / 529.0 / 280.3 cycles per op, and E37's own ±1 / ±2 fill reads 22.66 ± 0.19, 23.83 ± 0.17, 25.84 ± 0.09 W over idle against E37's 24.4, 25.5, 26.3 (R1).
- **The +18 W is the kernel, not the fill:** on one fill, int8's benchmark over its resident loop is +17.45 ± 0.14 W (R4; fp32 +6.22, fp16 +6.77).
- **But the +18 W belongs to the benchmark, not to a real matmul.** The real GEMM's random int8 draws **10.44 ± 1.03 W** over idle against the loop's 9.66 ± 0.12 and the benchmark's 27.39 ± 0.26; random fp32 draws 24.80 ± 0.38, under the loop's 26.43 ± 0.09 and the benchmark's 36.45 ± 0.09. The reason is the next line.
- **A real GEMM runs slower than the benchmark:** 740 cycles per op on a minion's mean, about 846 for the slowest, **in all three formats**, against 529 / 529 / 280. So 5.93 TFLOPS against 9.48 in fp32 and **23.6 TOPS against 71.5 in int8**, at the same clock. The same count in three formats whose multipliers' own floors are 529 and 280 says the memory, not the multiplier, sets the rate. It costs more energy per op, not less: 34.3 against 31.5 nJ in fp32, 14.5 against 12.5 nJ in int8, the loop's being 23.6 and 5.0. Past the L3, `gemm16` takes about 1,489 cycles per op and 41.3 nJ.
- **Cooperative loads save power and cost speed.** Over the same GEMM with every minion loading for itself they save 5.6, 5.5, 5.1 W (R8), about 6 nJ per op, at 740 cycles against 677 on a minion's mean, 5.93 against 6.20 TFLOPS.
- **The memory path's data-dependent power is much larger than the frozen prediction said.** In the benchmark, random over zeros costs the path 6.78 ± 0.20, 6.33 ± 0.32, 11.66 ± 0.28 W, against 2.42, 2.38, 5.33 from E75's prices per changed bit: **R5 fails, by 2.2–2.8×**. And a constant costs the path 2.09 ± 0.32, 1.74 ± 0.09, 2.43 ± 0.57 W more than zeros: R5b fails too. So the path pays for set bits, not only for changing ones: post hoc, labelled, a constant of 2.7 nJ and about 0.34 pJ per carried one, on top of E75's changed-bit prices, fit the 18 cells to 0.50 nJ rms (`posthoc-path.json` `fit_mm16_e75_held`).
- **Post hoc, labelled: the path's cost per op is a property of the 2 KB, not of the format.** Charging every watt above the loop's energy per op to the path gives, in the benchmark, about 2.1 nJ on zeros and 7.5–7.9 nJ on random in **all three formats** (the third table).
- **The kinds keep their order.** Spearman ρ against the loop is 1.0 in fp16 and int8 in both arms and 0.9 in fp32, where sparse50 and ones swap: the path pays for sparse50's bits and not for a constant's changes (R6).
- **Zeros still save most of the power, but less of it.** Zeros ÷ random: 0.126 / 0.138 / 0.280 in the benchmark and 0.170 / 0.199 / 0.363 in the GEMM, against 0.074 / 0.082 / 0.27 for the loop (R7a and R7b pass).
- **A watt on the memory path heats the die sensor as a watt on the lanes does:** 0.122 °C per W over 34 cells, all arms, at or above 12 W, against E78's 0.113–0.129 (R10). The die rise over the 2 s window reaches 4.46 °C on the benchmark's random fp32.
- **Most of the streaming watts are not on the minion rail.** Over fp32's resident zeros, the benchmark's random reads 34.3 W at the board and 22.1 W on the rail, the loop's 24.3 and 19.4: of the extra 10.0 W only 2.7 W reach that rail (`e101.json` `items.<cell>.D`, `.Drail`).

**S, board power over each run's idle, W, 95% over four passes** (`e101.json` `items.<cell>.S`; cycles `.cycles_per_op`, a minion's mean; rates from the launch records, `.rate`). Real: four Q132(r) tiles with no zero word per format, repeated through the pool.

| arm | format | zeros | ones | sparse50 | real | random | cycles per op | T(FL)OP/s |
|---|---|---|---|---|---|---|---|---|
| `res`, E78's loop | fp32 | 2.13 ± 0.07 | 10.20 ± 0.23 | 9.27 ± 0.32 | 25.93 ± 0.02 | 26.43 ± 0.09 | 546.0 | 9.18 |
| `res`, E78's loop | fp16 | 2.03 ± 0.21 | 10.37 ± 0.09 | 15.34 ± 0.19 | 22.89 ± 0.17 | 23.78 ± 0.21 | 546.0 | 18.36 |
| `res`, E78's loop | int8 | 2.54 ± 0.08 | 4.15 ± 0.14 | 8.04 ± 0.26 | 8.33 ± 0.09 | 9.66 ± 0.12 | 318.0 | 63.10 |
| `tenb`, E39's: B streamed | fp32 |  |  |  |  | 28.85 ± 0.13 | 529.0 | 9.48 |
| `tenb`, E39's: B streamed | int8 |  |  |  |  | 15.68 ± 0.26 | 270.0 | 74.34 |
| `mm16`, E37's benchmark loop | fp32 | 4.60 ± 0.13 | 15.02 ± 0.22 | 17.73 ± 0.52 | 35.77 ± 0.13 | 36.45 ± 0.09 | 529.0 | 9.48 |
| `mm16`, E37's benchmark loop | fp16 | 4.62 ± 0.09 | 14.97 ± 0.25 | 23.10 ± 1.02 | 32.86 ± 0.23 | 33.40 ± 0.26 | 529.0 | 18.97 |
| `mm16`, E37's benchmark loop | int8 | 7.65 ± 0.17 | 11.92 ± 0.51 | 22.94 ± 0.14 | 25.51 ± 0.02 | 27.39 ± 0.26 | 280.3 | 71.54 |
| `gemm1`, a real GEMM, cooperative | fp32 | 4.21 ± 0.30 | 10.59 ± 0.53 | 12.65 ± 0.29 | 23.91 ± 1.54 | 24.80 ± 0.38 | 740.1 (slowest 846) | 5.93 |
| `gemm1`, a real GEMM, cooperative | fp16 | 4.49 ± 0.27 | 11.21 ± 0.75 | 16.45 ± 1.23 | 21.91 ± 1.87 | 22.55 ± 1.43 | 740.1 (slowest 846) | 11.85 |
| `gemm1`, a real GEMM, cooperative | int8 | 3.78 ± 0.28 | 5.21 ± 0.26 | 9.07 ± 0.43 | 9.80 ± 0.58 | 10.44 ± 1.03 | 738.5 (slowest 852) | 23.56 |
| `gemmnc1`, the same, not cooperative | fp32 |  |  |  |  | 30.35 ± 1.17 | 677.3 (slowest 809) | 6.20 |
| `gemmnc1`, the same, not cooperative | fp16 |  |  |  |  | 28.10 ± 2.19 | 677.3 (slowest 809) | 12.40 |
| `gemmnc1`, the same, not cooperative | int8 |  |  |  |  | 15.49 ± 0.44 | 675.3 (slowest 810) | 24.78 |
| `gemm16`, 16 blocks, past the L3 | fp32 | 4.78 ± 0.11 |  |  |  | 17.00 ± 0.72 | 1,488.5 | 3.37 |
| `gemm16`, 16 blocks, past the L3 | fp16 | 4.74 ± 0.27 |  |  |  | 16.23 ± 0.16 | 1,489.3 | 6.74 |
| `gemm16`, 16 blocks, past the L3 | int8 | 4.50 ± 0.11 |  |  |  | 9.81 ± 0.17 | 1,487.4 | 13.49 |
| `mmp64`, private pools, DRAM | fp32 | 6.60 ± 0.21 |  |  |  | 10.76 ± 0.35 | 15,376.0 | 0.31 |

**Energy per op, from S** (`e101.json` `items.<cell>.pj_op_S`, `.pj_mac_S`):

| arm | format | zeros, nJ per op | random, nJ per op | random, pJ per multiply-add | zeros ÷ random, watts |
|---|---|---|---|---|---|
| `res` | fp32 | 1.90 | 23.58 | 5.756 | 0.081 |
| `res` | fp16 | 1.81 | 21.22 | 2.590 | 0.085 |
| `res` | int8 | 1.32 | 5.01 | 0.306 | 0.263 |
| `mm16` | fp32 | 3.97 | 31.49 | 7.688 | 0.126 |
| `mm16` | fp16 | 3.99 | 28.85 | 3.522 | 0.138 |
| `mm16` | int8 | 3.51 | 12.54 | 0.766 | 0.280 |
| `gemm1` | fp32 | 5.82 | 34.27 | 8.367 | 0.170 |
| `gemm1` | fp16 | 6.20 | 31.17 | 3.804 | 0.199 |
| `gemm1` | int8 | 5.25 | 14.52 | 0.886 | 0.362 |
| `gemm16` | fp32 | 11.62 | 41.35 | 10.095 | 0.281 |
| `gemm16` | fp16 | 11.54 | 39.46 | 4.817 | 0.292 |
| `gemm16` | int8 | 10.93 | 23.82 | 1.454 | 0.459 |

**POST HOC, labelled, never a verdict: what the memory path costs, nJ per op:** `[S(arm) − r S(res)] / rate`, with the arm's own measured rate (`posthoc-path.json` `path.<cell>.E_path_nj_op`, `posthoc-path.txt`). It charges everything above the loop's energy per op to the path.

| arm | format | zeros | ones | sparse50 | real | random |
|---|---|---|---|---|---|---|
| `mm16` | fp32 | 2.07 | 3.88 | 7.05 | 7.78 | 7.93 |
| `mm16` | fp16 | 2.18 | 3.69 | 6.28 | 7.98 | 7.65 |
| `mm16` | int8 | 2.19 | 3.30 | 6.33 | 7.36 | 7.53 |
| `gemm1` | fp32 | 3.65 | 4.24 | 8.03 | 6.61 | 7.33 |
| `gemm1` | fp16 | 4.14 | 4.92 | 7.10 | 6.94 | 6.92 |
| `gemm1` | int8 | 3.73 | 4.76 | 7.79 | 8.65 | 8.73 |
| `gemm16` | fp32 | 9.72 |  |  |  | 17.78 |
| `gemm16` | fp16 | 9.73 |  |  |  | 18.26 |
| `gemm16` | int8 | 9.61 |  |  |  | 18.81 |

## Registered against what happened, session 1

311 of 311 runs kept, four of four passes, none set aside. Idle 25.805 W; leakage slope, the registered `auto`, 0.3298 W/°C (E78's 0.1994); arms 0.1994, 0.3803 and 0: **no verdict moves** (`scored.json` `slope_sensitive`). Idle bracket consistency median 0.064 W; carry-over -0.0004 ± 0.0017 W/W; `anchor_pi` drift +0.07 to +0.23 W first to last.

| rule | registered | measured | verdict |
|---|---|---|---|
| R1 tie to E37 | ±1.5 W of E37 less 0.8 W; cycles within 0.5% | 22.66 / 23.83 / 25.84 against 23.58 / 24.69 / 25.45 W; 529.0 / 529.0 / 280.3 | **PASS** |
| R2 tie to E78 | ±0.60 W, 12 cells, new binary | worst 0.32 W | **PASS** |
| R3 premium | > 1 W at 95%, 12 cells | smallest +2.27 W | **PASS** |
| R3b model | rms ≤ 3 W `mm16`, ≤ 4 W `gemm1` | 2.25 and 5.62 W | **PASS, FAIL** |
| R4 clause | int8 17.28 [14.78, 19.78] | +17.45 [+17.30, +17.59] | **PASS** |
| R5 memory, data | 2.42 [1.68, 3.17] fp32, 2.38 fp16, 5.33 [3.7, 6.98] int8 | +6.78 [+6.57, +6.98], +6.33 [+6.01, +6.64], +11.66 [+11.38, +11.94] | **FAIL** |
| R5b memory, constant | inside ±1 W | +2.09 [+1.77, +2.41], +1.74 [+1.65, +1.83], +2.43 [+1.87, +3.00] | **FAIL** |
| R6 rank | ρ ≥ 0.9 | 0.9, 1.0, 1.0, 0.9, 1.0, 1.0 | **PASS** |
| R7 zeros' share | a) above the loop's; b) below 0.75 | see the bullet above; worst upper bound 0.409 | **PASS, PASS** |
| R8 cooperative | > 0 at 95%, six differences | smallest lower bound +2.17 W | **PASS** |
| R9 correct | none wrong; zeros and int8 exact | none wrong, all exact where required, on 46 items | **PASS** |
| R9b cycles | within 1% per arm and format | worst 0.41% | **PASS** |
| R10 heat | OLS in [0.10, 0.14] °C/W | 0.122 | **PASS** |
| R11 DRAM | 4.42 [3.31, 5.52] | +4.16 [+3.75, +4.57], cycles 15,376 | **PASS** |
| R12 past the L3 | > 0 at 95% | +12.22 [+11.58, +12.87], +11.48 [+11.19, +11.78], +5.31 [+5.21, +5.41]; cycles ×2.01 of `gemm1` | **PASS** |

**Why the frozen numbers missed.**
- `mm16`: 15 of 18 frozen intervals hold the measurement. The misses are all three zeros: `E_base`, 4.67 nJ, came from E37's fill, which carries set bits, so it overstated the path on zeros (2.1 nJ), and E75's prices understated random's data part. The two errors cancel near random.
- `gemm1`: 3 of 15. **The frozen number gave it the benchmark's 529 / 529 / 280 cycles; it runs about 740 in all three.** The smoke showed this before the first pass and A4 wrote it down; no band moved. It is the prediction's largest error, and R3b's FAIL.
- `gemmnc1`: 0 of 3, the same reason. `tenb`: 2 of 2. R11, on E75's chord at E37's traffic: inside its range.

## Departures

- **A3:** four passes, not three, and 62 card-minutes, not 44: the card came free early. **The session took 55 card-minutes against the brief's guess of 25.**
- **A4:** the first smoke (`p10101`) marked `mm16.fp32.randn` and `tenb.fp32.randn` not ok: 9 million fp32 additions per word round past the check's tolerance. The host now ends a process with one short launch that the check reads, after the power window. The binary was rebuilt before the first pass; `p10102` is the smoke on it. Both smokes are kept in `aifoundry3/kinds-smoke/`.
- E78's check "built-in pi against file" reads None: E101 does not run the `fp32.pi` tile.
- The new arms' `duty` in `e101.json` divides by a minion's mean cycles; in `gemm1` and `gemmnc1` it reads 0.83–0.87 because launches end with the slowest minion. Rates and energies come from the launch records and stand.
- Uploading the big pools just before the first launch did not disturb the idle bracket: `S − D` of the random cells reads 2.13 W in `gemm16` and 2.06 W in `mmp64`, against 2.13 W for fp32's resident zeros.
- No run was skipped, retried or set aside. The tie, `anchor_pi`, stayed inside E78's gate.

## Results of session 2: the clock under aifoundry2's own governor

*E80's design, E64's runner unchanged, 10 Hz sampler, no `--reset-ms`, 65 W / 65 °C read before and after every run and at both ends, nothing set. Slot 04:20–05:35 PST under claim 1566355908076765257, no post of its own; nobody else logged in (`who` showed none at 03:25 PST, and E64's check never fired). Smoke 04:20–04:21 PST, session 04:21:38–05:03:35 PST, `aifoundry2/`.*

🛑 **The session ended on its registered safety stop, at run 82 of 96: board 101.15 W on three samples, over the 97 W cap.** The run was `mm16` fp16 random, on the hot start E101.md chose for the cells above the limit. **That choice was wrong:** it assumed a die heated to the trip holds the clock low. In fact, under the resident heater at the 65 °C trip, the clock cycled 600–700–800–700–600 MHz about once a second, and the board 53–67–87–68 W (`aifoundry2/s1/tel/SUS-19-mm16-fp16-randn-r1.jsonl.gz`). The work started on a rising edge: the clock read 700, then 800, then 700 MHz in its first half second, under a load the rule had put at 94.9 W at 800 MHz from a 58 °C reference. The watcher stopped the session within a second, as registered. The die read 66 °C. The card came back by itself: 26 W at +3 s, 22 W and a 46 °C die within minutes, its usual rest (`aifoundry2/rest-after-stop.txt`), and the config still read 65 W / 65 °C. **Lost, not run:** `mm16` random in fp32 and fp16, burst and sustained; resident fp32 random and int8 full sustained; the four replicates; `mm16` ones sustained. A safety stop is not a login, so the queue did not resume, as registered. The slot's last 31 minutes went unused. No run was retried; nothing else ran on the card from this lane.

**In plain words.**

- **Kinds still set power, heat and clock in the GEMM.** Sustained, random fp32 holds 621 MHz at 53.5 W and a 65.8 °C die, at the trip; zeros hold 789 MHz at 37.1 W and 56.9 °C.
- **But the GEMM's rate hardly follows the clock.** 6.64 TFLOPS at 800 MHz, 6.01 at 621 MHz, and 5.93 at 600 MHz on aifoundry3. Its wall cycles per op (clock × minions × operations per op ÷ rate) rise with the clock: about 849 at 600 MHz on aifoundry3, 867 at 621 MHz, 983 at 756 MHz, 1011 at 800 MHz, the same in all three formats at one clock.
- **The benchmark's count does not move:** 530 and 281 wall cycles per op at 800 MHz, as at 600. So the L2 keeps up with the minions, and what holds the GEMM back lies beyond it. Reading, not a measurement.
- **The chain from kind to watts to clock carries over, once the watts are right.** E83's relation on session 1's measured watts misses by 14.8 MHz rms in the burst and 21.6 sustained, and on this session's measured c by 11.4 and 17.7. On the frozen watts, which gave `gemm1` the benchmark's cycles: 39.9 and 66.2 (S4 FAIL).
- **Real tensors stream at random data's speed:** within 15.7 MHz, every format, burst and sustained (S5 PASS).
- **The heat path sits where E80 left it:** E80's die line reads the 19 sustained cells to 0.93 °C rms, and `gemm1` random fp32's 53.5 W reads 65.8 °C against its 65.5 °C.
- **Ties:** the resident bursts read 715.7 against 710.9 MHz (fp32 random) and 726.1 against 725.5 (fp16 random), 800 on the rest, on the new binary.

| rule | registered | measured | verdict |
|---|---|---|---|
| S1 fp32 burst, `gemm1` | GROWS ≥ 1.20 (predicted), SURVIVES ≥ 1.10, SHRINKS below | ×1.030; `mm16` not measured | **SHRINKS**: the prediction failed |
| S2 fp32 sustained, `gemm1` | SURVIVES in [1.20, 1.40] | ×1.093; `mm16` not measured | **FAILS** |
| S3 int8, sustained | SLOWS ≥ 1.05 (predicted 1.19, 1.22), HARDLY < 1.03 | `gemm1` ×1.002; `mm16` ×1.322 | **HARDLY** (the prediction failed); **SLOWS** (it held) |
| S4 relation on the frozen watts | ≤ 40 MHz rms, burst and sustained | 39.9, 66.2, over 25 and 19 cells | **FAIL** |
| S5 real against random, `gemm1` | within 25 MHz | worst 15.7 | **PASS** |

Every streaming cell's check of C read as at 600 MHz: exact on zeros, ones and int8, approx elsewhere, none wrong (`results-speed.json` `cells.<cell>.checks`). Wall cycles below are derived, by the formula above, from each cell's clock and rate. `results-speed.json`, `reduce-speed.txt`:

| cell | burst MHz | burst T(FL)OP/s | wall cycles per op | sustained MHz | T(FL)OP/s | wall cycles per op | board W | die °C | limit | frozen clocks, burst / sustained | on session 1's watts |
|---|---|---|---|---|---|---|---|---|---|---|---|
| `gemm1` fp32 zeros | 800 | 6.64 | 1011 | 789 | 6.57 | 1009 | 37.1 | 56.9 | none | 800 / 800 | 800 / 800 |
| `gemm1` fp32 ones | 800 | 6.64 | 1011 | 795 | 6.58 | 1013 | 50.6 | 63.9 | none | 800 / 718 | 800 / 775 |
| `gemm1` fp32 sparse50 | 800 | 6.59 | 1018 | 792 | 6.59 | 1007 | 53.5 | 64.8 | none | 800 / 725 | 800 / 744 |
| `gemm1` fp32 real | 770 | 6.51 | 993 | 619 | 6.00 | 865 | 53.3 | 65.9 | thermal | 665 / 600 | 734 / 614 |
| `gemm1` fp32 random | 756 | 6.44 | 983 | 621 | 6.01 | 867 | 53.5 | 65.8 | thermal | 664 / 600 | 726 / 609 |
| `gemm1` fp16 zeros | 800 | 13.20 | 1016 | 794 | 13.15 | 1013 | 38.1 | 58.2 | none | 800 / 800 | 800 / 800 |
| `gemm1` fp16 ones | 774 | 13.03 | 996 | 794 | 13.24 | 1007 | 50.5 | 63.6 | none | 800 / 718 | 800 / 765 |
| `gemm1` fp16 sparse50 | 800 | 13.27 | 1011 | 727 | 12.71 | 960 | 53.1 | 65.4 | thermal | 773 / 649 | 798 / 694 |
| `gemm1` fp16 real | 789 | 13.15 | 1007 | 659 | 12.26 | 902 | 54.8 | 65.6 | thermal | 692 / 600 | 754 / 630 |
| `gemm1` fp16 random | 778 | 13.08 | 998 | 675 | 12.36 | 916 | 56.8 | 65.6 | thermal | 687 / 600 | 747 / 624 |
| `gemm1` int8 zeros | 800 | 26.34 | 1019 | 795 | 26.27 | 1015 | 36.2 | 55.9 | none | 800 / 778 | 800 / 800 |
| `gemm1` int8 ones | 800 | 26.32 | 1020 | 794 | 26.22 | 1017 | 38.6 | 57.0 | none | 800 / 752 | 800 / 800 |
| `gemm1` int8 sparse50 | 800 | 26.39 | 1017 | 794 | 26.24 | 1016 | 45.9 | 61.9 | none | 795 / 679 | 800 / 791 |
| `gemm1` int8 real | 800 | 26.39 | 1017 | 795 | 26.26 | 1016 | 46.8 | 62.0 | none | 795 / 679 | 800 / 782 |
| `gemm1` int8 random | 800 | 26.36 | 1018 | 789 | 26.22 | 1010 | 48.8 | 62.9 | none | 778 / 654 | 800 / 773 |
| `mm16` fp32 zeros | 800 | 12.67 | 530 | 800 | 12.67 | 530 | 41.8 | 60.0 | none | 800 / 800 | 800 / 800 |
| `mm16` fp32 ones | 800 | 12.67 | 530 |  |  |  |  |  |  | 799 / 698 | 800 / 713 |
| `mm16` fp32 sparse50 | 791 | 12.46 | 532 |  |  |  |  |  |  | 796 / 684 | 794 / 678 |
| `mm16` fp16 zeros | 800 | 25.34 | 530 | 795 | 25.18 | 530 | 41.1 | 59.0 | none | 800 / 800 | 800 / 800 |
| `mm16` fp16 ones | 800 | 25.34 | 530 |  |  |  |  |  |  | 799 / 698 | 800 / 713 |
| `mm16` fp16 sparse50 | 723 | 22.40 | 542 |  |  |  |  |  |  | 740 / 618 | 742 / 620 |
| `mm16` int8 zeros | 800 | 95.60 | 281 | 794 | 94.87 | 281 | 48.6 | 63.7 | none | 800 / 734 | 800 / 799 |
| `mm16` int8 ones | 800 | 95.60 | 281 |  |  |  |  |  |  | 800 / 712 | 800 / 750 |
| `mm16` int8 sparse50 | 732 | 86.25 | 285 |  |  |  |  |  |  | 737 / 616 | 741 / 619 |
| `mm16` int8 random | 704 | 81.94 | 288 | 600 | 71.76 | 281 | 55.2 | 66.6 | thermal | 710 / 602 | 701 / 601 |
| `res` fp32 zeros | 800 | 12.28 | 547 |  |  |  |  |  |  | 800 / 800 | 800 / 800 |
| `res` fp32 random | 716 | 10.72 | 560 |  |  |  |  |  |  | 709 / 602 | 712 / 603 |
| `res` fp16 zeros | 800 | 24.55 | 547 |  |  |  |  |  |  | 800 / 800 | 800 / 800 |
| `res` fp16 random | 726 | 21.89 | 557 |  |  |  |  |  |  | 732 / 612 | 735 / 615 |
| `res` int8 zeros | 800 | 84.30 | 318 |  |  |  |  |  |  | 800 / 800 | 800 / 800 |
| `res` int8 random | 800 | 84.30 | 318 |  |  |  |  |  |  | 800 / 786 | 800 / 785 |

**Departures, session 2.** The safety stop above: 15 of 96 runs never ran, and S1 and S2 stand on `gemm1` alone. The reduction ran on the mini, not the Intel: the Intel's load guard had stopped the reducer in its hot tier; the code and inputs are the committed ones. E98's lane gave up its P4 and P5 for this slot, and the session ended 31 minutes before the slot did, too late to give them back.

## What E101 says about the page

- **The lede and §1's speed gaps are the loop's.** In a real GEMM of this pattern: fp32 ×1.03 and ×1.09 in rate, fp16 ×1.01 and ×1.06. Clocks still part, ×1.27 sustained in fp32. The cards table needs a line for it, with its "one block, not the vendor's binary".
- **§3's "int8 hardly slows" needs its arm:** true of the loop and of this GEMM, false of the benchmark (×1.17, ×1.32).
- **"The data never changes the cycle count" survives** in all six streaming arms at 600 MHz and in the benchmark at 800. New: in the GEMM the count follows the clock, because the memory holds the time per op.
- **§2's watts and "a random fp32 multiply-add costs 5.8 pJ" are the loop's.** It is 7.69 pJ in the benchmark, 8.37 in the GEMM and 10.09 past the L3, at 600 MHz. int8's 0.31 pJ becomes 0.77, 0.89 and 1.45.
- **§7's "zeros cost 5–7% of random" is the loop's:** about 13% in the benchmark and 17–20% in the GEMM, in fp32 and fp16.
- **§5.8, the memory path, grows from a footnote to a term:** 2.1 nJ per op on zeros and 7.5–7.9 on random in the benchmark, in every format (labelled), E75's changed-bit prices short by 2.2–2.8× (R5 FAIL), and a price for set bits at the L2 (R5b FAIL, labelled).
- **§4, heat, stands:** a watt on the memory path heats the sensor as a watt on the lanes does (R10), and E80's die line holds on streaming cells.
- **Section 11:** this closes the critic's top item for one GEMM pattern. Item 6, a model of every kind, gains a memory-path term. Item 12 narrows: zeros' transport about 2.1 nJ per op, labelled, and the set-bit price shows at the L2 as well as at DRAM. **New open items:** why a GEMM block runs at 740–1,019 cycles and not 529, and what the vendor's own binary does; the benchmark's random fp32 and fp16 speed, which needs a start that does not meet the 97 W stop.

**For the post, in short sentences.**
- Feed the matmul benchmark zeros and it draws 4.6 W over idle in fp32; feed it random numbers and it draws 36.5 W (`e101.json` `items.mm16.fp32.zeros`, `.randn`).
- The kind of number never changes the cycle count at a given clock, whether the operands sit in the minion or stream from memory (`scored.json` `rules.R9b_cycles`).
- Streaming a tile costs energy that depends on the data: about 2 nJ an op for zeros, about 8 nJ for random numbers, in every format (`posthoc-path.json`, post hoc).
- A real GEMM in the vendor's pattern takes 740 cycles an op in every format at 600 MHz: 5.9 TFLOPS in fp32 and 23.6 TOPS in int8, because memory sets the pace (`e101.json` `items.gemm1.*`).
- Its cooperative loads save about 5 W at the board and about 6 nJ an op, and cost about 4% in rate (`scored.json` `rules.R8_coop`; `e101.json` `items.gemmnc1.*`).
- Past the L3 the same GEMM halves again, and zeros still draw 4.8 W against random's 17.0 W in fp32 (`e101.json` `items.gemm16.*`).
- Under the governor that GEMM's zeros beat random by only 3% in a burst and 9% sustained in fp32, though the clocks part by 6% and 27%, because the memory sets the pace (`results-speed.json` `rules.S1_fp32_burst`, `rules.S2_fp32_sustained`).
- In the benchmark, where the memory keeps up, int8 zeros beat random by 17% in a burst and 32% sustained; in the loop and in that GEMM int8 hardly slows (`results-speed.json` `rules.S3_int8`).
- Real tensors ran within 16 MHz of random numbers in that GEMM (`results-speed.json` `rules.S5_real`).

## Files

`e101.json`, `runs.csv`, `reduce.txt` (E78's reduction, `reduce_e101.py`); `e101-leak*.json`, `runs-leak*.csv`, `reduce-leak*.txt` (the leakage arms); `scored.json`, `results.md` (`score_e101.py`); `posthoc-path.json`, `.txt` (labelled; `posthoc_path_e101.py`); `aifoundry3/kinds/p1011[0-3]/` (every pass's raw data: `runs.jsonl`, `marks.jsonl`, `telemetry.jsonl.gz`, `tiles/`, `config_*.json`, `manifest.txt`, `binaries.sha256`); `aifoundry3/kinds-smoke/`; `logs/` (the queue, `coop1.jsonl`, the build, both config reads); `code.sha256`. Session 2: `results-speed.json`, `reduce-speed.txt` (`tools/claims-v3/kspeed/e101/reduce_e101s.py` with session 1's `e101.json`); `aifoundry2/` (`smoke/`, `s1/`: `runs.jsonl`, `marks.jsonl`, `launches.jsonl.gz`, `tel/`, `sp/`, the queue's `queue.jsonl`, `config-*.txt`, `sensors-*.json`, `history-before.jsonl`, `rest-after-stop.txt`, the binaries' sha256).
