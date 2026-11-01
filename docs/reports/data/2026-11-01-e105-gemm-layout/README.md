# E105: does the gap come back when the tiles fit the L2?

*On the kinds page, [section 11, what is still open](https://spacesheep.dev/@yaroslavvb/horace-kinds-of-numbers#11-what-is-still-open): "Whether the gap comes back when a GEMM's tiles fit", "Where a large GEMM falls" and "Random fp32 and fp16 in the benchmark, and sustained random fp32 by column" (new items).*

*Sun 1 Nov 2026 (week 44), Q132. The first open item left by E101's verifier: E101's `gemm1` is one port of the vendor's GEMM pattern, whose packed tiles miss the L2 on most lines, so is that why its speed gap all but vanished? Pre-registered in `3ad06644` ([`tools/claims-v3/kspeed/e105/E105.md`](../../../../tools/claims-v3/kspeed/e105/E105.md), frozen numbers in `predictions-e105.json`, rules, self-test), before either claim and any launch; A1 `6a347e4b` added the power arm before any launch; A2 `3e577e7f` records a queue path fix with no effect on data. Binary: [`tools/claims-v3/rgm105/`](../../../../tools/claims-v3/rgm105/README.md), E101's kernel plus one field: same partition, op order, cooperative loads and tile contents, only the addresses differ. **aifoundry2 card 0 under its own governor,** 07:36–08:26 PST, 48.1 card-minutes, 65 W / 65 °C read after every run and at both ends. **aifoundry3 card 0 at its pinned 600 MHz,** 07:36–08:11 PST, TDP 0 / 65 °C / 600 MHz read at both ends of every pass, E101 session 1's own tools. Nothing was set on either card. No `--reset-ms`. No `mm16`, no hot start.*

## Corrections after verification

*Sun 1 Nov 2026 (week 44), about 09:30 PST. An independent verifier found the data, every number it recomputed and the registered verdicts sound, and "by column the fixed term goes and the rate follows the clock" sound, with the NoC rail as a check this README lacked. The sentence about reuse was not. I checked each fault against the data; all hold. The wrong sentences below were replaced in place, so this README is `make_readme_e105.py`'s output with these corrections applied. No frozen file, data file or verdict changed. Numbers here are recomputed from this directory's files by `corrections-check.py` into [`corrections-check.txt`](corrections-check.txt).*

- **C1, the major one. "The regime is set by how often a tile is reused" goes.** `gemm1`, `gemmv1` and `gemmc1` run the same loop with the same ops, repeating one block 5,485 to 11,425 passes per launch in fp32, and differ only in addresses, so the variable that moved M from 0.826 to 0.019 µs is set aliasing. Reuse changes only in the 16-block walk (164 to 199 passes per launch, each over 16 blocks), which also overflows the L2 and the 32 MB L3 and reads DRAM. No arm repeats a block a chosen number of times, and none walks fresh blocks that fit the L3. **It now reads "whether an op's tiles are in the L2 when it needs them", and whether reuse itself is the variable is untested.**
- **C2. C and M are a line through two clocks.** Only 600 and 800 MHz ever held for a whole launch, on every layout; none sat wholly at 700. The launches between are time mixes of the governor's hunt, so the form is hardly tested. The ± is launch-level on correlated launches: the same arm's C moved from 344.3 in E101 to 354.8 here, 5.5× the printed ±1.9. The tables now print per-run C and what is directly measured, **what ×1.333 of clock buys: as run ×1.115, strides ×1.165, by column ×1.324, half K ×1.316 (two launches at 600 MHz), cold by column ×1.064, cold strides ×1.041 (two launches at 600 MHz); fp16 by column ×1.324, int8 by column ×1.319.** **Cold strides are unresolved:** 225 and 321 in its two runs, 6 launches below 780 MHz, so "271 ± 48" is not a result. The frozen premise, C fixed and M alone carrying the misses, is false: C rises as misses fall (355, 407, 527), so the FMA's 529 cycles overlap the wait by 122–174, and int8 strides' 346 is above the FMA's own 280. **C is the clock-following share of the op, and a count of nothing except by column. M is the wait outside the minion clock, not all memory time:** the part of the wait that follows the clock is inside C. M has support (post hoc): NoC rail per op over by column's base, as a share of as-run's, reads strides 0.56–0.60 (desk 0.559), cold by column 0.85–0.89 (desk 0.889) and cold strides 1.36–1.56 (desk 1.07), and M per unit of that traffic is the same in the two steady layouts (0.53 and 0.55 µs per nJ on zeros). By column sits at 0.18 nJ per op on zeros.
- **C3. R8's gap PASS says nothing about the pace.** ×1.002 and ×0.999 are at clock ×1.000: both kinds ran 800 MHz in the burst, so the rate could not part. Registered as written and scored correctly, so the verdict stands; its reading does not. What shows the pace is T: ×1.333 of clock buys ×1.064 and ×1.041.
- **C4. "DRAM's bandwidth is the likely limit" goes: what limits the cold walk is not measured.** Against it: distinct A + B run 17–20 GB/s and C's stores 11–13 GB/s at 600 MHz, under the lab's 76 GB/s of lines and 48–53 GB/s past the L3 (`docs/findings/05-claims.md`), and the same bytes in three layouts take 2.49, 2.59 and 2.90 µs per op, with packed, the most desk misses, fastest. For it: L2-miss traffic is 101–158 GB/s, so DRAM could bind if the L3 does not absorb the sharers' reads. **DRAM, the L3 and the walk are not separable here.** The same NoC traffic per op as as-run (1.58 and 1.75 nJ on zeros) costs 2.4× the M, so service time differs and not the miss count. With C the footprint is 80 MB, not 48. The separating arm: 8 blocks, 24 MB of A + B, overflow the L2 and fit the L3.
- **C5. The power failure's size.** "From a cool die" pointed the wrong way: fp16 random's 94.32 W came 43.5 s in on a hot die, against its burst's 91.91 W. Adding that +2.41 W to by-column fp32 random's 96.25 W gives about 98.7 W (an extrapolation), and E101's hot start read 101.15 W. **So sustained random fp32 by column could not be expected to complete under the 97 W stop on this card, and the refusal is not a gap to fill by rerunning.** The error is systematic: the estimate ran 3.2–8.4 W under the reading on 19 of 63 runs, the high-power cells, and 8.42 W of the 9 W margin went in that one burst. The lock let fp16 random run at an estimate of 86.13 W, 1.7 W under the estimate that had just read 96.25 W. **The rule for future runs: estimate from the same kind's S on a pinned card (P4's relation read 94.6 W against 95.2 W measured, and aifoundry3 had that S before the burst ran), not from a lower kind's rho, and lock by layout and format.**
- **C6. int8's "because" is now labelled, with the dip-free figure.** E101's frozen relation on each arm's own c gives the loop ×1.02 (c 9.1), by column ×1.19 (c 17.24), the benchmark ×1.33 (c 26.54), against the page's ×1.01 and this lane's ×1.17 and ×1.32 measured (post hoc). Why c is 0.65 of the benchmark's at 94% of the rate is not measured: cooperative loads are a reading, and "its one difference" was wrong, because by column also has a TensorStore every 32 ops, 8,192 lines per shire against 512, and its own tile pool, and no non-cooperative by-column arm exists. `gemmc1-int8-zeros` sustained reads 786 MHz through 9 dips of 1.2–1.3 s, 6 of them at process boundaries, which `idle_resets_sus` mostly does not count. **On dip-free zeros ×1.166 reads ×1.188.**
- **C7. `score_e105p.py`, the scorer of P1–P5, was first committed with the data** (`18b28633`), after the passes ended and after this lane had looked at the results. The verifier read it against `predictions-e105-a1.json`, frozen before those passes: all five rules are implemented as frozen, so no verdict moves.
- **C8. Wording.**
  - The sampled clock reads the hunt high, which is how a rate gap prints above its clock gap, and the law forbids that. On the kernel's own clock (cycles_max ÷ wall): ×1.238 on ×1.244, ×1.221 on ×1.228, ×1.320 on ×1.330, ×1.166 on ×1.174. R4 as registered uses the sampled clock and passes either way.
  - "One edit" is from E101's own packing, in a block repeated thousands of times per launch. Against the vendor's strides the rate gains ×1.51.
  - "Brackets" was unshown. E105 does not place a large GEMM, and does not show it lies between these conditions.
  - Horace He's gap implies only that his clock set enough of his pace to show ×1.148.
  - "The law crosses cards": one point does. T at 600 MHz crosses cards, and aifoundry3 has no slope.
  - c explains the burst misses (12.7 MHz rms on measured c, against 39.3 frozen) but only part of the sustained (35.0, or 23.7 without as-run sparse25, against 69.2), and the clocks run about 25 MHz above the relation. R4's kind read 21.44 W against 26.41 frozen, and sparse25's c_ref was interpolated, never measured.
- **C9. Small.** A2 was pushed at 07:41:46 PST, 5.7 min after the fix it records had run; no data was touched. The pass-level `aifoundry3/*/binaries.sha256` names `build/e101/kernel/sparsity.elf`, which did not run: `block_e101.sh` hardcodes the name, the host's compiled-in path is `build/e105/kernel`, the queue's own `aifoundry3/binaries.sha256` has the right one, and 536.6 cycles prove it. E105.md's half-K cold 33.3% is the desk's; the kernel would give 66.7%, and no arm uses it. `skipped.jsonl` prints 93.0 W, the lock's bar, where the run read 96.25 W.

## The answer

**Yes, for a repeated block. With its tiles in the L2 the part of each op that ignores the clock goes, and the speed gap comes back, as large as the clock gap. In a walk over fresh blocks past the L2 and the L3, ×1.333 of clock buys only ×1.064 and ×1.041, and zeros and random both ran 800 MHz in the burst, so there was no clock gap to pass.**

| layout, on aifoundry2 | desk L2 model, lines missing | what ×1.333 of clock buys, fp32 | C, a slope over two clocks; per-run range | M, µs | frozen C, M | T at 800 MHz, zeros, µs | TFLOPS at 800 MHz, burst | TFLOPS at 600 MHz, aifoundry3 |
|---|---|---|---|---|---|---|---|---|
| `gemm1`, as E101 ran it | 75.0% | ×1.115 | 354.8; 345–370 over 6 runs | 0.826 | 344.3, 0.838 | 1.270 | 6.61 | 5.93 (E101) |
| `gemmv1`, the vendor's strides | 41.9% | ×1.165 | 407.1; 395–414 over 11 runs | 0.516 | 344.3, 0.468 | 1.024 | 8.21 | 7.02 |
| `gemmc1`, B packed by column | 0.0% | **×1.324** | 526.9; 526–528 over 10 runs | **0.019** | 529, 0 | 0.678 | 12.37 | 9.32 |
| `gemmh1`, by column, half K | 0.0% | ×1.316, two launches at 600 MHz | 526.3; one run | 0.035 | 529, 0 | 0.694 | 12.09 | |
| `gemmc16`, by column, 16 blocks, cold | 66.7% | ×1.064 | 374.2; 367–377 over 3 runs | 1.968 | 344.3, 1.271 | 2.435 | 3.44 | 3.23 |
| `gemmv16`, strides, 16 blocks, cold | 80.2% | ×1.041, two launches at 600 MHz | unresolved: 225 and 321 in its two runs | 2.4, unresolved | 344.3, 1.529 | 2.774 | 3.02 | 2.88 |

T = C/f + M per op, over the launches of at least 0.1 s between 590 and 810 MHz, T = wall ÷ ops per minion, f = cycles_max ÷ wall (`results-speed.json` `fits`, whose ± is launch-level; C2). **Only 600 and 800 MHz held for a whole launch, so C and M are a line through two clocks.** C is the clock-following share of the op and a count of nothing except by column; M is the wait outside the minion clock, not all memory time. The strides' zeros burst had an idle reset, so its TFLOPS are from sparse50's burst. fp16 and int8, launch-level: by column C 527.3, M 0.018 and C 289.5, M 0.015; strides C 410.1, M 0.511 and C 345.7, M 0.534. **One edit from E101's own packing, B by column, in a block repeated thousands of times per launch, takes M from 0.83 to 0.019 µs and C to the FMA's own 529, and nearly doubles the rate;** against the vendor's strides the rate gains ×1.51. Half the chip on random fp32 reads C 527.1, M 0.017. **T at 600 MHz crosses cards:** aifoundry3's pinned 600 MHz reads within 0.6% of aifoundry2's T there in every layout (`scored-p.json` `two_cards`); aifoundry3 has no slope of its own.

**Zeros ÷ kind, aifoundry2, its own governor: rate (clock).** n is runs per kind, burst and sustained, one card, one session (`results-speed.json` `gaps`, `cells`). The clock in parentheses is the sampled one, which reads the governor's hunt high; on the kernel's own clock the bold cells read ×1.238 on ×1.244, ×1.221 on ×1.228, ×1.320 on ×1.330, ×1.166 on ×1.174 (`corrections-check.txt`).

| layout | kind | burst | sustained | n |
|---|---|---|---|---|
| as run | fp32 random | ×1.029 (×1.057) | ×1.088 (×1.248) | 1, 1 |
| as run | fp32 sparse25 | ×0.997 (×1.000) | ×1.001 (×1.000), see below | 1, 1 |
| strides | fp32 random | ×1.031 (×1.043), see below | ×1.145 (×1.287) | 1, 1 |
| strides | fp32 sparse25 | ×0.963 (×0.945), see below | ×1.083 (×1.145) | 1, 2 |
| **by column** | **fp32 random** | **×1.238 (×1.224)** | refused: the burst read 96.25 W | 1, 0 |
| **by column** | **fp32 sparse25** | **×1.084 (×1.068)** | **×1.221 (×1.211)** | 1, 2 |
| by column | fp32 ones | ×1.000 (×1.000) | ×1.029 (×1.023) | 1, 1 |
| **by column** | **fp16 random** | **×1.176 (×1.156)** | **×1.320 (×1.329)** | 1, 1 |
| **by column** | **int8 full** | ×1.022 (×1.015) | **×1.166 (×1.156)** | 1, 2 |
| cold, by column | fp32 random | ×1.002 (×1.000), both at 800 MHz | no zeros run | 1, 1 |
| cold, strides | fp32 random | ×0.999 (×1.000), both at 800 MHz | no zeros run | 1, 0 |

- **fp32 by column: the rate now follows the clock.** Random reads ×1.24 in the burst on a clock gap of ×1.22 (one run), against as-run's ×1.03 on ×1.06. **Sustained random fp32 by column was not measured at full chip:** after the burst read 96.25 W the rule refused it. The registered primary kind, sparse25, reads ×1.22 on ×1.21 over two runs: R4 COMES BACK. fp16 random did reach sustained: **×1.32 on ×1.33,** one run, the size of fp16 in the page's loop. For sustained fp32 random the law gives ×1.32: expected, not measured, and such a run could not be expected to complete (C5).
- **int8 slows too once its tiles fit:** ×1.17 sustained on ×1.16, two runs (R5 COMES BACK; ×1.19 on dip-free zeros), against as-run's ×1.00. It is under the benchmark's ×1.32, and one relation on each arm's own c gives ×1.02, ×1.19 and ×1.33 for the loop, by column and the benchmark (post hoc, C6). Why by column's c is smaller is not measured.
- **The vendor's strides sit between:** random fp32 sustained ×1.145 on a clock gap of ×1.287. M is 0.52 µs, a share of as-run's that is close to the desk model's (R2).
- **The kind still never changes the count at a given clock:** T at or above 790 MHz reads 0.6768 to 0.6783 µs by column across zeros, ones, sparse50, sparse25 and random, and 1.0222 to 1.0278 with strides (`results-speed.json` `t800_us`).
- **Two soft cells.** `gemmv1` zeros' only burst, and its int8 zeros' burst, each hit a governor idle reset (756 MHz, `cells.<cell>.idle_resets_burst`), so the strides' burst ratios read under 1; against sparse50's reset-free burst at 800 MHz, 8.206 TFLOPS, random's is ×1.070 (clock ×1.103). As-run sparse25's sustained run was the session's first, from a die of 49 °C where the others started at 53–58 °C, and it did not reach the 65 °C trip in its 76 s, so its ×1.00 understates that kind and R6's lower anchor is soft.
- **Every check of C held on both cards:** exact or approx, none wrong (`results-speed.json` `cells.<cell>.checks`; `aifoundry3/*/p*/runs.jsonl`).

**Power at 600 MHz on aifoundry3 (A1).** S over idle, W, and pJ per multiply-add, random (`scored-p.json` `cells`; E101's `e101.json`). By column stands on two passes. **Strides stand on one:** E78's own gate set `p10521` aside (fp32 random spanned 1.72 W against its 1 W). Real tensors read within 0.4 W of random in fp32 and fp16 by column.

| format | the loop | as run | strides | by column | benchmark | cold, by column | cold, strides |
|---|---|---|---|---|---|---|---|
| fp32 | 26.43 W, 5.76 pJ | 24.80 W, 8.37 pJ | 26.68 W, 7.60 pJ | **32.99 W, 7.08 pJ** | 36.45 W, 7.69 pJ | 15.27 W, 9.46 pJ | 14.21 W, 9.85 pJ |
| fp16 | 23.78 W, 2.59 pJ | 22.55 W, 3.80 pJ | 23.89 W, 3.41 pJ | **30.06 W, 3.22 pJ** | 33.40 W, 3.52 pJ | 14.39 W, 4.46 pJ | 13.41 W, 4.64 pJ |
| int8 | 9.66 W, 0.31 pJ | 10.44 W, 0.89 pJ | 11.20 W, 0.74 pJ | **18.23 ± 4.67 W, 0.54 pJ** | 27.39 W, 0.77 pJ | 8.17 W, 1.26 pJ | 7.11 W, 1.40 pJ |

- **At the benchmark's rate, by column draws less than the benchmark:** 9.32 against 9.48 TFLOPS on 33.0 W against 36.5 W, and 67.2 against 71.5 TOPS on 18.2 W against 27.4 W. Why is not measured. Cooperative loads, which E101's R8 priced, are a reading; by column also has a TensorStore every 32 ops, 8,192 lines per shire against 512, and its own tile pool, and no non-cooperative by-column arm exists.
- **So a random fp32 multiply-add costs 7.08 pJ in a GEMM pattern whose tiles fit,** at 600 MHz on aifoundry3, against the port's 8.37, which carried its misses and stall time, and the loop's 5.76. Zeros: 0.81 pJ.
- **The benchmark's +18 W comes back in part:** int8's premium over the loop is 8.6 W by column (as run 0.8, benchmark 17.45): P3 PARTIAL, with ±4.7 W on two passes.
- **Zeros' share by column:** 11.4%, 12.7%, 27.4%, close to the benchmark's (P5 PASS), on two passes; fp32 zeros carry ±2.3 W.

## The cold variant, 16 blocks

**A walk over 48 MB of A + B, each block touched once per pass, is held by something that ignores the clock: ×1.333 of clock buys ×1.064 by column and ×1.041 with strides (two launches at 600 MHz).** Zeros ÷ random reads ×1.002 and ×0.999 in the burst, one run each, at clock ×1.000: both kinds ran 800 MHz, because random's watts never reached a limit, so the rate could not part. R8's gap PASS stands as registered and says nothing about the pace (C3). Random draws 15.3 W over idle against zeros' 4.0 W at 600 MHz on aifoundry3, and sustained it held 791 MHz.

**The frozen model of it failed.** M does not scale with the desk model's miss share there: 1.97 µs by column against 1.27 frozen, and with strides about 2.4 against 1.53, unresolved. **By column is no faster than as-run when cold:** 3.23 TFLOPS at 600 MHz against E101's as-run 3.37, and strides are slower still at 2.88. **What limits the walk is not measured** (C4). DRAM, the L3 and the walk are not separable from these arms. Against DRAM's bandwidth: distinct A + B run 17–20 GB/s and C's stores 11–13 GB/s, under the lab's 76 GB/s of lines and 48–53 GB/s past the L3, and packed, with the most desk misses, is fastest. For it: L2-miss traffic is 101–158 GB/s, if the L3 does not absorb the sharers' reads. The separating arm is 8 blocks, 24 MB of A + B, which overflow the L2 and fit the L3. The block's C here is overwritten, never accumulated across blocks, and no block was warmed first.

## What sets the pace, on this chip

**On this chip the pace depends on whether an op's tiles are in the L2 when it needs them. With a repeated block whose tiles all fit, T = 527/f + 0.02 µs and the clock sets the pace. Where they alias in the L2, 0.5–0.8 µs of each op ignores the clock. Where a walk over fresh blocks overflows the L2 and the L3, about 2–2.4 µs does. The kind of number does not move any of this. Whether reuse itself is the variable is untested.**

`gemm1`, `gemmv1` and `gemmc1` repeat one block with the same ops and differ only in addresses, so the variable between them is set aliasing. Reuse changes only in the 16-block walk, tied to the L2 and L3 overflow. **E105 does not place a large GEMM, on this chip or any other, and does not show it lies between these conditions:** the vendor's binary is untimed, and its one-pass launch and prefetch files are outside these arms; no arm sweeps block repeats; no arm walks fresh blocks that fit the L3; and every arm is one kernel on one card in one session. This partition reads each A tile once and each B tile twice per block, so a walk over fresh blocks leans to the third condition. That is the desk model's reading.

## Registered against what happened

**Rules on aifoundry2** (`results-speed.json` `rules`, 57 runs, 1 refused, nothing wrong in any check of C):

| rule | registered | measured | verdict |
|---|---|---|---|
| R1 by column removes M | M ≤ 0.15 µs, C in 470–590 | M 0.0186, C 526.9 | **PASS** |
| R2 strides' M | M ÷ as-run's in 0.35–0.78 (desk 0.559) | 0.624 | **PASS** |
| R3 the tie to E101 | C within 30 of 344.3, M within 0.08 of 0.838 | C 354.8, M 0.826 | **PASS** |
| R4 fp32 gap by column | sustained ≥ 1.15 and within 0.03 of the clock | ×1.221 on ×1.211 (frozen ×1.33) | **COMES BACK**; the size missed: the rate followed the clock, and the clock fell less than frozen |
| R5 int8 gap by column | sustained ≥ 1.15 | ×1.166 on ×1.156 (frozen ×1.33) | **COMES BACK**; the size missed |
| R6 strides between | strictly between as-run and by column | 1.001 < 1.083 < 1.221 | **PASS**, on as-run's soft cell |
| R7 T at 800 MHz, 12% | as run 1.268, strides 0.898, by column 0.661 | 1.270, 1.024, 0.678; order holds | as run **PASS**, **strides FAIL (+14%)**, by column **PASS** |
| R8 cold T, 25% | by column 1.701, strides 1.959 | 2.435, 2.774 | **FAIL, FAIL (+43%, +42%)** |
| R8 cold gap | ≤ ×1.06 | ×1.002, ×0.999, burst only, at clock ×1.000 | **PASS** as registered; it says nothing about the pace (C3) |
| R9 half K, 5% | 0.661 | 0.694 (+4.9%) | **PASS**; R1 and R7 did not miss on `gemmc1`, so it was not needed |

**Rules on aifoundry3** (`scored-p.json` `rules`; `score_e105p.py` was first committed with the data, and implements them as frozen, C7):

| rule | registered | measured | verdict |
|---|---|---|---|
| P1 rate at 600 MHz, by column, 5% | 9.50, 18.99, 71.6 | 9.32, 18.65, 67.2 | PASS, PASS, **int8 FAIL (−6.1%)** |
| P1 strides, 15% | 8.04, 16.02, 31.7 | 7.02, 14.02, 30.1 | PASS, PASS, PASS |
| P1 cold, 25% | fp32 4.54 by column, 3.98 strides | 3.23, 2.88 | **FAIL in all six** (−27% to −36%) |
| P2 random's S by column, 15% | 39.3, 36.0, 29.6 W | 33.0, 30.1, 18.2 W | **FAIL, FAIL, FAIL** (−16%, −17%, −38%) |
| P3 int8 premium | ≥ 12 W comes back, < 6 W does not | 8.6 W | **PARTIAL** |
| P4 the refusal | by-column random fp32 at 800 MHz, from S | 94.6 W, at or above 88 W | **the cell should have been refused; it was not** (next section) |
| P5 zeros' share, 0.05 | benchmark's 0.126, 0.138, 0.280 | 0.114, 0.127, 0.274 | **PASS** ×3 |

**Why the frozen numbers missed.**
- **Cold:** M was scaled by miss share, and it does not scale. That model is wrong for a walk past the L2 and the L3.
- **Strides:** C is 407, not 344, and M 0.516, not 0.468, so T at 800 MHz is 14% long. The desk model has M's share about right (0.62 against 0.56). The premise that C stays fixed while M carries the misses is false: C rises as misses fall (C2).
- **By column's watts:** the frozen c assumed 1.08 × the benchmark's. It measured 0.90 in fp32 random and 0.65 in int8 full. So the frozen clocks ran low: 39.3 MHz rms in the burst and 69.2 sustained over 25 and 18 cells (labelled, no rule), and the gaps came in at ×1.22 and ×1.17 where ×1.33 was frozen. Measured c explains the burst misses (12.7 MHz rms) but only part of the sustained (35.0), and the clocks run about 25 MHz above the relation (C8).

## The power rule did not do what it was for

**The rule admitted the one cell it existed to catch.** By-column random fp32 was estimated at 87.83 W from its sparse50 probe (rho 0.81), 0.17 W under the 88 W limit. It measured 95.2 W at 800 MHz and **peaked at 96.25 W, 0.75 W under the session's 97 W stop.** The probe's rho read low: random's true share was 0.90. The stop did not fire, and the registered 93 W lock then refused its sustained run (`aifoundry2/s1/skipped.jsonl`), which is why that cell is missing. fp16 random by column went on under the lock, estimated 86.13 W, and read 91.91 and 94.32 W. The error is systematic: the estimate ran 3.2–8.4 W under the reading on 19 of 63 runs, the high-power cells. **So by-column random fp32 sits at this card's stop. Its sustained run could not be expected to complete under it: fp16's sustained run read +2.41 W over its burst, on a hot die, and the same on fp32 gives about 98.7 W (an extrapolation), so the refusal is not a gap to fill by rerunning.** **The rule for future runs: estimate from the same kind's S on a pinned card (P4's relation read 94.6 W against 95.2 W measured), not from a lower kind's rho, and lock by layout and format.** Three highest readings: 96.25 W (A-11-gemmc1-fp32-randn-r1), 94.32 W (E-05-gemmc1-fp16-randn-r1), 91.91 W (E-04-gemmc1-fp16-randn-r1) (`aifoundry2/admission.json`).

## Departures

- **The aifoundry2 start was 07:36, not about 07:20:** E98's claim read released at 07:21, and a desk machine's load guard then paused the claim post for about 5 minutes. A2.
- **The power arm's queue first exited 127 before touching the card,** going one directory short of the root. Fixed and restarted at 07:36:04 PST. A2.
- **Its claim post, `1566472292924661822`, could not be released by the usual edit.** It was posted at 07:21:38 PST, and at 08:40 PST it was no longer in the channel, nor were the other posts between 31 Oct and aifoundry2's claim; no entry for it is in the card-post archive, and this lane did not delete it. Its queue had ended at 08:11 PST. aifoundry2's claim `1566475985451491350` was edited to read released at 08:38 PST and read back.
- **One power-arm run was skipped:** `p10520` #25, resident `fp16.sparse50`, did not reach its launch reading. It is not one of E105's cells.
- **`p10521` was set aside by E78's gate,** so the strides' S rests on one pass and has no interval.
- **The vendor's binary was not run:** about 58 µs per launch against about 2 ms of launch overhead, and no cycle counter, so timing it needs an instrumented build. It stays open.
- **`score_e105p.py` was first committed with the data** (C7).
- The reductions ran on a desk machine, because another's load guard pauses tool children in its hot tier.

## What E105 says about the page

- **Lede.** May add: at a given clock the count is the layout's and not the kind's (T at 800 MHz within 0.2% by column and 0.55% with strides, across kinds; 0.678, 1.024, 1.270 µs by layout). May not say a real GEMM has or lacks the gap.
- **§1.** May add, each with card, clock and n: in a repeated GEMM-pattern block whose tiles fit the L2, the whole clock gap reaches the rate: fp32 random ×1.24 burst (one run), fp16 random ×1.32 sustained (one run), fp32 sparse25 ×1.22 sustained (two), on aifoundry2. In the port as run, ×1.03 and ×1.09. May say "×1.32 expected, not measured" for sustained fp32 random. May not print it as measured, or call it the loop's size in fp32. May not use the cold ×1.00 as a gap without "both at 800 MHz".
- **§2.** May add: a random fp32 multiply-add costs 7.08 pJ in a repeated block whose tiles fit, at 600 MHz on aifoundry3, and 9.46 pJ in the cold walk.
- **§3.** "int8 hardly slows" holds in the loop and as run only: ×1.17 by column (two runs), ×1.32 benchmark, and one relation on each arm's c gives ×1.02, ×1.19, ×1.33 (post hoc). May not state why by column int8 draws less. May add: sustained random fp32 by column is at this card's 97 W stop and was refused.
- **A new section, regimes.** May carry three measured conditions, none a GEMM on real data. (1) Tiles fit, block repeated: ×1.333 of clock buys ×1.324. (2) Tiles alias, block repeated: ×1.115 and ×1.165, with M tracking the NoC traffic. (3) Fresh blocks past the L3: ×1.064 and ×1.041; rate 3.2 and 2.9 TFLOPS at 600 MHz; layout barely helps, and the desk's miss share does not predict T. May give the bound with its label: this partition reads each A tile once and each B tile twice per block, so a walk over fresh blocks leans to (3) (desk reading). May not say "the regime is set by how often a tile is reused", name DRAM bandwidth as the cause, call C a cycle count outside by column, or print "271 ± 48" as a result.
- **Is a large GEMM placed by this?** No. On this chip? No: the vendor's binary is untimed, no arm sweeps block repeats, no arm walks fresh blocks that fit the L3, and every arm is one kernel on one card in one session.
- **§11.** Close "does the gap come back when the tiles fit" for a repeated block; sustained fp32 random stays unmeasured. **New open items, first:** a sweep of block repeats; 8 blocks, 24 MB of A + B, which overflow the L2 and fit the L3; then the vendor's binary.

**The one honest sentence about the hook:**

> Horace He's ×1.148 on an A100 needs his clock to set at least that much of his pace; on the ET-SoC-1 the same mechanism reaches the rate only where the clock sets the pace: a repeated block whose tiles fit the L2 passes the whole clock gap (×1.24 in a one-run fp32 burst, ×1.32 sustained in one fp16 run, aifoundry2), one port whose tiles alias in the L2 passes about a third of it (×1.09 on ×1.25), and a walk over fresh blocks has no clock gap to pass (both kinds at 800 MHz), and where a large GEMM falls, on this chip or on his, nobody here has measured.

**For the post, in short sentences.** Each names its card and clock.
- On aifoundry2 under its own governor, one edit from E101's own packing, in a block repeated thousands of times per launch, took the part of each op's time that ignores the clock from 0.83 µs to 0.02 µs, and its rate from 6.6 to 12.4 TFLOPS at 800 MHz (`results-speed.json` `fits`).
- With the tiles in the L2, zeros beat random numbers by 24% in a burst in fp32 (one run), and by 32% sustained in fp16 (one run), matching the clock gap, on aifoundry2 under its own governor (`results-speed.json` `gaps`).
- Walking fresh blocks past the L2 and the L3 on aifoundry2, a third more clock bought only 6% more rate by column and 4% with strides. Zeros and random ran within 0.2% in a burst, both at 800 MHz: random's watts never reached a limit (`corrections-check.txt`; `results-speed.json` `rules.R8`).
- So on this chip the pace depends on whether an op's tiles are in the L2 when it needs them. Nobody here has measured where a production GEMM falls.

## Files

`corrections-check.py`, `corrections-check.txt` (the corrections' numbers). `results-speed.json`, `reduce-speed.txt` (aifoundry2, `reduce_e105.py`); `e105c.json`, `e105v.json`, `-runs.csv`, `-reduce.txt` (aifoundry3, E101 session 1's `reduce_e101.py` unchanged, with `E101_GEMM` set; its `gemm1.*` and `gemm16.*` items ran the layout the file names); `scored-p.json`, `scored-p.txt` (`score_e105p.py`); `aifoundry2/` (`smoke/`, `s1/`: `runs.jsonl`, `skipped.jsonl`, `marks.jsonl`, `launches.jsonl.gz`, `tel/`, `sp/`; the queue's `queue.jsonl`, `admission.json`, `config-*.txt`, `sensors-*.json`, `history-before.jsonl`, the binaries' sha256); `aifoundry3/` (`kinds-e105c/`, `kinds-e105v/`, and their `-smoke/`: every pass's raw data); `logs/` (both queues, both builds); `code.sha256`. The registration and the desk L2 model are in [`tools/claims-v3/kspeed/e105/`](../../../../tools/claims-v3/kspeed/e105/E105.md).
