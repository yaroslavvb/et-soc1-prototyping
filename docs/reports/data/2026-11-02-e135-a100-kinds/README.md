# E135: a GPU measured the same way, Horace He's kinds of numbers on two A100s

*On the kinds page, [section 11, what is still open](https://spacesheep.dev/@yaroslavvb/horace-kinds-of-numbers#11-what-is-still-open):
**item 2, "A GPU measured the same way"**, as it read on 1 Nov 2026: "Clocks, power and temperature logged per kind, in a
burst and sustained, at the default cap and a lower one, and the layout question beside them." E135 answers it at the
default cap on two boards, with a size ladder for the size half of the layout question; the lower cap could not be set
(below).*

*Mon 2 Nov 2026 (week 45). The owner's OK that morning: "btw you can do 'gpu measured the same way' by using modal, not
exceeding $10 in experiments (use A100 or cheaper)". Pre-registered in `89378ba6`
([`tools/gpu/e135/E135.md`](../../../../tools/gpu/e135/E135.md), frozen numbers in `predictions-e135.json`, the reducer,
a selftest showing each rule holding and failing), pushed before any GPU call; amendment A1 in `73fc73a7`, after the
declared 2048³ smoke and before the first measured call. Measured 11:05–11:58 PST on Modal (workspace `yaroslavvb`, app
`e135-a100-kinds`): two containers, units A and B, each on its own A100-SXM4-40GB. **Metered cost $3.62** of the $10
ceiling ([`billing.json`](billing.json)), against $6.41 projected, a budget guard at $7.94 and the functions' timeouts at
$8.66 ([`corrections-check.txt`](corrections-check.txt) §C13).*

## Corrections after verification

*Mon 2 Nov 2026 (week 45), about 13:30 PST. An independent verifier re-derived every cell, gap, replicate and rule from
the committed logs and found the data, the reduction, the registered verdicts, the timeline and the cost sound: all 150
logs are byte-identical to the Modal Volume, and every derived file rebuilds byte-identical. It found the comparison
with the ET-SoC-1 not like for like, the post-hoc 330 W figure quoted without its own calibration, and smaller slips. I
checked each fault against the committed files, and all hold. The wrong sentences were replaced in place, so this README
reads as corrected. No frozen file, data file, derived file or verdict changed. The numbers here are recomputed from
committed files by [`corrections-check.py`](corrections-check.py) into [`corrections-check.txt`](corrections-check.txt),
by the section named.*

- **C1, the major one. The comparison set a kernel against a chip.** Its ET-SoC-1 figures are the resident loop's (E80,
  E83: one 16×16 TensorFMA repeating on the same tiles); the A100's are a streaming 8192³ cuBLAS GEMM. The lab's
  GEMM-pattern kernels read differently. E105's repeated block, B by column, tiles in the L2, gives fp32 random ×1.238 in
  a burst, fp16 random ×1.176 in a burst and ×1.320 sustained, and int8 ×1.022 and ×1.166. E119's and E126's walks over fresh
  blocks give fp32 ×1.229 down to ×1.00 sustained, falling with reuse. Zeros keep 11–13% of random's switching in E105's
  block in fp32 and fp16 (27% in int8), 13–14% in the benchmark, 26–30% on the cold walks and 61% in an arm fed from
  DRAM, against the resident loop's 3–12% (§C1; the Q130 literature README §6a and its dated note of 1 Nov). So "int8 is
  where the two chips differ most", "the data effect is smaller on the A100" and "the fp16 burst gap is about the same on
  both chips" go: each was the loop's against the GEMM's. **"Against the ET-SoC-1" now labels every ET-SoC-1 figure by
  its kernel, puts E105's block beside the loop, names the walks, and draws no chip-level contrast from a gap's size.**
- **C2, the other major one. The 330 W view carries its calibration.** In bf16, his format, the relation gives ×1.217 on
  unit B and ×1.193 after its own +0.025 error at 400 W, just below his ×1.213–1.221; unit A has no bf16 value. fp16 and
  tf32 give ×1.22–1.24, and ×1.22–1.23 after their own errors (§C2). "What this changes" said it "gives his ×1.22"; it now
  reads ×1.19–1.22 in bf16 on one board.
- **C3. The bf16 sustained interval.** ±0.006 is over the four passes, which share two boards. Over the boards (means
  ×1.111 and ×1.105, n = 2) the 95% interval is ±0.038 (§C3). Both are printed.
- **C4. His lower limit is not tested here.** That his random kinds run slower than ours is consistent with his 330 W,
  not a test of it: the cap could not be set (R5 N/A), and his unit, its cooling and his April 2024 software differ from
  ours (torch 2.5.1, cuBLAS 12.4.5.8; §C11).
- **C5. Why his loop reads less is a post-hoc reading,** now marked as one, with its ranges corrected. In `gist6` the
  randn trials sample 1275–1410 MHz (A) and 1290–1410 MHz (B), and their last samples read 1275–1305 and 1290–1395 MHz.
  It said they sample 1290–1395 and settle at 1290–1305. The die means are 47–48 °C in `gist6` and 50–51 °C in
  `article9` (§C5).
- **C6. The capped kinds' order.** They all draw 393–399 W, the cap. Their order is that of the power they would draw at
  the full clock, which is the post-hoc demand.
- **C7. The ladder's 8192³ figure** is unit B's own ×1.104 (one run per size), not the four-pass ×1.108 (§C9).
- **C8. The ET-SoC-1's sustained range** in its resident loop is ×1.29–1.32 (1.293–1.316 measured), not ×1.29–1.33:
  1.33 is the nominal 800/600 clock ratio (§C1).
- **C9. Digits.** The post-boost burst gap is ×1.097 (1.0975), not ×1.098. fp16's clock gap is ×1.136 (1.1364), not
  ×1.137. The lane's summary called the 3 s burst gap "equal to the clock ratio", but that window's sampled clock ratio
  averages ×1.090 against its ×1.097: the gaps that equal their clock ratios are the sustained ones (to 0.003) and the
  post-boost burst's (×1.097 on ×1.098) (§C9).
- **C10. The pre-boost readings are partly sensor lag.** The boost came 0.21–0.43 s after the first call, so each kind's
  pre-boost power is one to three 100 ms samples of a reading that updates about every 0.1 s, at times 0.2 s. Of the 19
  cells that fit n, four have two readings that agree within 5%, giving n = 2.89–3.12. So the median 2.99 stands, and the
  2.31–3.75 range is partly lag (§C10; the caveat is now in "Post hoc").
- **C11. What identifies a board.** The `nvidia-smi -q` text keeps the GPU PDI, the Board ID and the PCI bus id; only the
  UUID, serial, chassis-serial and cluster-UUID lines are replaced. None is a secret, and the logs stay byte-identical to
  the Volume. E135.md's "the board is logged only as a 12-hex hash of its UUID" overclaims the same way; it is frozen and
  not edited (§C11).
- **C12. Scope.** The ladder answers the size half of the layout question: the operands stay square and K-contiguous.
  Gregersen, Patel and Choukse's 2048³ A100 was a PCIe part (300 W) running CUTLASS (Q130(e) §2).
- **C13. The cost's ceilings.** $7.94 is the budget guard (each unit stops itself at its budget), which kept the run
  under the $8 stop; $8.66 is the functions' timeouts, the backstop (§C13). The lane's summary had called $8.66 the
  guard.

## The answer

**On an A100 the zeros-against-random gap is set the way the ET-SoC-1's burst gap is: by how far random data's power
would overshoot the power cap. On these two boards that is all that sets it, in a burst and sustained.** At 8192³ in
bf16, at the boards' 400 W limit, all-zero matrices ran **293.5 TFLOPS at the full 1410 MHz**, drawing 254–261 W, with no
clock-event reason set. Random normal ones sat **on the cap**, at 396–398 W with the SW power cap reason in every 100 ms
sample and no thermal reason, at **1267–1277 MHz and 264–266 TFLOPS**. **Zeros ÷ random = ×1.108 sustained** (four
passes on two boards, 1.104–1.113; board means ×1.111 and ×1.105; 95% ±0.006 over the passes, ±0.038 over the two
boards) and **×1.097 in the 3 s burst from a cool, idle GPU**. Each sustained gap is the
clock ratio to within 0.003 (a burst's within 0.011, its sampled clock catching the boost ramp): TFLOPS per GHz agrees
across kinds to 0.34% in every sustained group, so at a given clock the kind of number never changed the speed ([`results.json`](results.json) `replicates`, `rules.R1`, `rules.R2`).

| 8192³, 400 W, sustained (3–63 s) | TFLOPS (TOPS) A · B | SM MHz A · B | board W A · B | SW power cap share | zeros ÷ this, rate (clock) |
|---|---|---|---|---|---|
| bf16 zeros | 293.5 · 293.6 | 1410 · 1410 | 260.9 · 253.9 | 0 · 0 | — |
| bf16 twos | 293.6 · 293.8 | 1410 · 1410 | 286.5 · 277.4 | 0 · 0 | ×1.000 (×1.000) |
| bf16 all π | 292.6 · 293.6 | 1410 · 1410 | 301.4 · 294.0 | 0 · 0 | ×1.002 (×1.000) |
| bf16 one bit | 293.4 · 293.8 | 1410 · 1410 | 320.3 · 316.4 | 0 · 0 | ×1.000 (×1.000) |
| bf16 ternary | 288.4 · 291.4 | 1385 · 1401 | 396.3 · 398.0 | 1.00 · 0.58 | ×1.013 (×1.012) |
| bf16 75% sparse | 285.5 · 287.3 | 1371 · 1380 | 397.9 · 393.4 | 1.00 · 1.00 | ×1.025 (×1.025) |
| bf16 rand | 275.1 · 277.7 | 1321 · 1333 | 398.6 · 398.9 | 1.00 · 1.00 | ×1.062 (×1.063) |
| bf16 checkerboard | 270.2 · 270.9 | 1298 · 1301 | 398.7 · 398.9 | 1.00 · 1.00 | ×1.085 (×1.085) |
| **bf16 randn** | **263.8 · 266.0** | **1267 · 1277** | **398.4 · 397.1** | **1.00 · 1.00** | **×1.108 (×1.108)**, four passes |
| fp16 zeros · randn | 293.5 · 293.1 / 258.1 · 258.6 | 1410 / 1240 · 1242 | 257.0 · 251.0 / 399.3 · 398.4 | 0 / 1.00 | **×1.135** (×1.136) |
| tf32 zeros · randn | 147.5 · 147.7 / 129.5 · 129.8 | 1410 / 1235 · 1238 | 309.8 · 302.8 / 399.3 · 397.5 | 0 / 1.00 | **×1.139** (×1.140) |
| int8 zeros · random −128…127 | 439.7 · 439.6 / 406.1 · 405.6 | 1410 / 1305 · 1302 | 270.8 · 272.9 / 398.2 · 398.7 | 0 / 1.00 | **×1.083** (×1.082) |

Pass 1 of each unit (`results.json` `cells["<unit>|default|8192|<format>|<kind>|1"].windows.sus`: `tflops`,
`sm_mean`, `power_w`, `frac.sw_power`); the right column is the mean over units (bf16: four passes) of
`gaps[*].gap_rate` (`gap_clock`) for zeros against that kind, computed here for the middle rows from the same cells. The
bf16 burst gap is ×1.097 (1.086–1.105), ×1.097 after the boost on a clock ratio of ×1.098 (`burst_b`, 0.5–3 s, A1),
fp16 ×1.117, tf32 ×1.118, int8 ×1.070 (`replicates["default|8192|<format>|burst"]`). Power is the energy counter's slope over the window.

- **The ET-SoC-1's mechanism, on the A100** (R1, registered P2: **HOLDS**, 4 of 4 replicates). Random's sustained clock
  is 0.899–0.906 of zeros', the SW power cap reason is set in 100% of random's samples, every thermal reason in 0%, and
  random draws 0.991–0.996 of the enforced 400 W (`rules.R1.detail`).
- **Speed follows the clock** (R2, P3: **HOLDS**). TFLOPS per GHz is 208.2 in bf16 and fp16 (94% of the 16-bit peak of
  221 per GHz), 104.8 in tf32 and 311.4 TOPS in int8, the same for every kind: spreads 1.0005–1.0034 sustained and
  1.0035–1.0143 in the bursts, whose sampled clock includes the boost ramp (`rules.R2.detail`).
- **The cap's dichotomy** (R3, P4: **HOLDS**, 47 cells). Every kind under 95% of the limit held 1410 MHz with the SW cap
  bit clear: zeros, twos, π and one bit in bf16, and zeros and twos in every format. Every kind with the bit set ≥ 50% sat
  at 98–100% of 400 W (393.4–401.6 W, 25 cells). The one edge is unit B's ternary: 398.0 W at 1401 MHz with the bit set 58% of the time
  (`rules.R3`).
- **The gap where and only where the cap acts** (R4, P9: **HOLDS**). All 20 format × window × pass pairs have random
  capped and zeros not, and all 20 gaps exceed 1.02 (1.059–1.139). The ladder supplies the other half, unscored: at
  2048³ random bf16 draws 310 W at 1410 MHz, under the cap, and the gap is ×1.002 (below).
- **Thermal limits never act** (R8, P8: **HOLDS**, 51 cells): the die peaked at 66 °C and HBM at 59 °C, against this
  board's 85 °C GPU maximum and 89 °C slowdown (`rules.R8`; `units.A.static.temp_threshold_*`).
- **No slow governor** (R7, P7: **HOLDS**): the sustained gap minus the burst gap is +0.002 to +0.023 (`rules.R7`). The
  controller takes the GPU from its 1095 MHz application clock straight to a clock that fits 400 W within about 0.1–0.2 s
  of the boost (`posthoc.txt` §2). Random bf16 never ran a 100 ms sample at 1410 MHz.
- **His gap carried to our cap** (R6, P6: **HOLDS**): A ×1.111 and B ×1.105 lie inside the registered band
  [1.000, 1.122] at 400 W, near its n = 3 end (`rules.R6`). Post hoc, these boards' own exponent is 2.99 (below).
- **The post's chart order** (R9, P10: **HOLDS**): Spearman ρ = 0.90 between the nine kinds' sustained TFLOPS and the
  chart's bars (`rules.R9`).
- **His protocol reads less than the sustained cells** (R10, P11: **FAILS** on unit A). `mm_weird.py`'s loop reads ×1.081
  (A) and ×1.087 (B) against the cells' ×1.113 and ×1.104: a difference of −0.032 (bar 0.03) and −0.017. Why is below
  (`rules.R10`).
- **The lower cap** (R5, P5: **N/A**). `nvidia-smi -i 0 -pl 330` exited 4 with "Failed to set power management limit for
  GPU …: Insufficient Permissions" inside Modal's container. The limit read 400 W before and after, and nothing needed
  restoring (`lowcap.A`). R6's registered 330 W check is N/A with it.

## Horace He's numbers beside these

| `mm_weird.py`, bf16 8192³ | randn | twos | sparse (negative half 0) | one bit | rand | zeros | zeros ÷ randn |
|---|---:|---:|---:|---:|---:|---:|---:|
| his A100, 330 W limit, 28 Apr 2024 | 239.41 | 287.43 | 257.72 | 287.80 | 251.97 | 292.30 | **1.221** |
| E135 unit A, 400 W, his loop | 271.37 | 292.26 | 285.46 | 292.10 | 281.86 | 293.25 | **1.081** |
| E135 unit B, 400 W, his loop | 269.61 | 292.34 | 284.60 | 291.90 | 281.24 | 293.06 | **1.087** |

His row is Q132(g) §d's reading of the gist's comment image (`predictions-e135.json` `horace.gist_runs`); ours are
`results.json` `protocols["<unit>|default|gist6"]`. The post's nine-kind chart reads ×1.217 against our `article9` ×1.080
and ×1.082.

- **His zeros and ours agree (292.30 against 293.06–293.25), and every random kind is faster on ours.** That is what a
  power cap predicts: zeros run at the full clock under either limit, while random is held at his 330 W and at our
  400 W. It is consistent with his lower limit, not a test of it: the cap could not be set here (R5 N/A), and his unit,
  its cooling and his April 2024 software differ from ours (torch 2.5.1, cuBLAS 12.4.5.8). It also bears out P6's
  assumption that his zeros were not held back.
- **Post hoc, our boards' own relation comes close to his number at his limit.** Each kind's power was read loaded at
  the 1095 MHz application clock before the boost, which came 0.21–0.43 s after the first call: one to three 100 ms
  samples of a reading that updates about every 0.1 s ("Post hoc", below). The kinds that stay under the cap give
  P − P_idle ∝ f^n with n = 2.99 (the median of 19 cells, 2.31–3.75; the four with two readings that agree give
  2.89–3.12). With these, the clock where random bf16 draws 330 W gives **zeros ÷ randn = ×1.19–1.22 in bf16, on one
  board**: ×1.217 on unit B as the relation gives it, ×1.193 after its own +0.025 error at 400 W (unit A's random bf16 has
  no clean pre-boost reading). fp16 and tf32 give ×1.22–1.24 on both units, ×1.22–1.23 after their own errors
  (`posthoc.json` `at_330`). His gist recorded ×1.213–1.221 and his chart ×1.217, so the calibrated bf16 figure sits just
  below his. This is a model fitted after the data, not a measurement at 330 W.
- **Why his loop likely reads a smaller gap than the cells** (post hoc: two readings, neither tested). Each `do_bench`
  window is about 0.145 s, about as long as the controller takes to settle. A zeros trial that follows randn starts at
  randn's clock and reads 283.7–289.9 against 292.6–293.8 after a quiet kind. In `gist6` the randn trials sample
  1275–1410 MHz (A) and 1290–1410 MHz (B), and their last samples read 1275–1305 and 1290–1395 MHz, against the cells'
  sustained 1267–1277. The interleaved, L2-flushed loop also keeps the die cooler (a 47–48 °C mean in `gist6` and
  50–51 °C in `article9`, against 58–63 °C in the random cells' sustained windows), and a cooler die leaks less at the
  same 400 W. Both would shrink the gap ([`corrections-check.txt`](corrections-check.txt) §C5, from the trial-by-trial
  samples in `logs/`).

## Against the ET-SoC-1: kernel against kernel

| zeros ÷ random, the kernel's rate | ET-SoC-1, its resident loop (aifoundry2; E80, E83): 6 s burst · sustained | ET-SoC-1, a repeated GEMM-pattern block, B by column (aifoundry2; E105): 6 s burst · sustained | A100, cuBLAS 8192³ GEMM (E135): 3 s burst · sustained |
|---|---|---|---|
| fp32 (ET) · tf32 (A100) | ×1.142–1.149 · ×1.293–1.306 | ×1.238 · not run (refused after a 96.25 W burst); sparse25 ×1.221 | ×1.118 · ×1.139 |
| fp16 | ×1.119–1.129 · ×1.297–1.316 | ×1.176 · ×1.320 | ×1.117 · ×1.135 |
| bf16 | — | — | ×1.097 · ×1.108 |
| int8 | ×1.00 · ×0.99–1.03 | ×1.022 · ×1.166 | ×1.070 · ×1.083 |
| zeros' switching ÷ random's, at one clock | 3–12% (fp32) | 11%, 13%, 27% (fp32, fp16, int8; 600 MHz, aifoundry3) | about 40% (bf16, unit B, post hoc) |
| what holds random back | the 65 W power test in a burst, the 65 °C thermal trip sustained | the same governor | the 400 W SW power cap in both |

Resident loop: `predictions-e135.json` `etsoc1.gaps` (E80's and E83's `results.json` `cells.*.burst_rate`, `sus_rate`)
and the Q130 literature README §6a. E105: `docs/reports/data/2026-11-01-e105-gemm-layout/results-speed.json`
`gaps["gemmc1-*"]`, one run each except int8's and fp32 sparse25's sustained, two; its `scored-p.json` `rules.P5`. A100:
`results.json` `replicates`, `posthoc.json` `overshoot`. All are printed in
[`corrections-check.txt`](corrections-check.txt) §C1.

**None of the ET-SoC-1's kernels is a large streaming GEMM, and its gap depends on the kernel.** E105's block repeats
one block whose tiles fit the L2 thousands of times per launch, so the clock sets its whole pace (×1.333 of clock buys
×1.324), as it sets the A100 GEMM's (TFLOPS per GHz the same at every clock it ran, R2). Walks over fresh blocks pass
less of the clock gap. E119's fp32 random reads ×1.229, ×1.148 and ×1.062 sustained at 8, 4 and 2 passes per block, and
×1.079 on the walk the L3 serves (`docs/reports/data/2026-11-01-e119-gemm-speed/results.json` `rules.R5`). E126's second
session read ×1.189, ×1.088, ×1.025 and ×1.023 on the same four, and ×1.00 on the walks past the L3 (`c8` ×0.998, `c16s`
×1.004; `docs/reports/data/2026-11-02-e126-gemm-arms/results.json` `gaps`). On the two walks the L3 serves, int8 random
read ×0.999 and ×0.993. Zeros keep 13–14% of random's switching in the benchmark, 26–30% on the cold walks and 61% in an
arm fed from DRAM (the Q130 literature README's dated note of 1 Nov, §6a). Where a large GEMM falls on this chip is not
measured (E105, E107, E119). So these columns set one kernel against another, not one chip against the other.

- **What matches.** In each kernel, random data's power would pass a limit, and kinds that stay under it keep the full
  clock. The clock falls with how far a kind's demand overshoots. In the resident loop random fp32 draws 82.7 W at
  800 MHz against the 65 W test and bursts at 711.9 MHz (E80's `results.json` `cells["fp32/randn"]`). On the A100 unit
  B's random bf16 would draw about 550 W at 1410 MHz (post hoc) against 400 W, and runs at 1282 MHz early and 1277 MHz
  sustained. In every kernel measured on either chip the kind changes the speed only through the clock (R2 here; E105's
  T at 800 MHz across kinds; E119's R4). The resident loop's fp16 burst gap (×1.12–1.13) is close to the A100 GEMM's
  (×1.117), but E105's block reads ×1.18 in its one burst: a coincidence of kernels, not a property of either chip.
- **What differs between the chips: the limit and the controller.**
  1. The A100's sustained gap stays set by its power cap: in 60 s the die never reaches a thermal limit (at most 66 °C).
     Where random's heat reaches the ET-SoC-1's 65 °C trip, the trip sets its sustained gap. Random fp32 and fp16 fall
     to 604–612 MHz in the resident loop, at the 600 MHz floor, and fp32 to 604–695 MHz on E119's walks.
  2. The A100 moves its clock in 15 MHz steps and settles in 0.1–0.2 s. So its gap tracks each kind's demand
     continuously and is about the same in a burst and sustained (R7: +0.002 to +0.023). The ET-SoC-1's governor moves
     in 100 MHz steps on a ~1.3 s average, and in the resident loop its sustained gap is a clamp: random falls to the
     floor while zeros keep about 800 MHz (×1.29–1.32).
- **What the kernel decides, on either chip.**
  3. Whether int8 slows. Random int8 barely slows in the ET-SoC-1's resident loop (×1.00 in a burst, ×0.99–1.03
     sustained) and on its walks, but slows ×1.17 sustained in E105's block (two runs) and, as E105 cites it, ×1.32 in
     the benchmark (E105's README, "What E105 says about the page", §3). The A100 GEMM reads ×1.083 at its cap. So
     "int8 hardly slows" is the loop's, not the chip's.
  4. How much of random's switching zeros keep. In the A100 GEMM, zeros keep about 40% of random's at the same clock
     (post hoc: 254–261 W at 1410 MHz against unit B's random demand of about 550 W, over a 56–59 W idle). On the
     ET-SoC-1 the share runs from 3–12% in the resident loop, through 11–13% in E105's block and 13–14% in the benchmark
     in fp32 and fp16 (27–28% in int8), to 26–30% on the cold walks and 61% from DRAM. The A100's 40% sits inside the
     ET-SoC-1's own range across kernels, so it does not separate the chips. On the A100 the share still decides the
     clock, because random bf16 would overshoot the cap by about 38%.

## The size half of the layout question: where the gap needs a large GEMM (unit B, exploratory)

| bf16, 400 W, sustained | zeros T/s, W | randn T/s, MHz, W, SW share | zeros ÷ randn |
|---|---|---|---|
| 2048³ | 157.4, 167.7 W | 157.1, 1410, 310.0 W, 0 | ×1.002 |
| 4096³ | 269.6, 244.8 W | 249.4, 1305, 397.7 W, 1.00 | ×1.081 |
| 8192³ | 293.6, 253.9 W | 266.0, 1277, 397.1 W, 1.00 | ×1.104 |

(`results.json` `cells["B|default|<n>|bf16|*|1"]`, `gaps`; one run each, 3 s + 30 s for the two smaller sizes.) At every
size the rate follows the clock. What changes with size is whether random data's power reaches the cap. At 2048³ it does
not, and nothing separates the kinds. That is the size at which Gregersen, Patel and Choukse saw no speed effect, on an
A100 PCIe (300 W) running CUTLASS (Q130(e) §2). Only the size moved here: the operands stay square and K-contiguous,
on one board, one run per size.

## Post hoc (no verdicts; `posthoc_e135.py`, written after the registration)

- **The readings these rest on** (C10). NVML's power reading updates about every 0.1 s, at times every 0.2 s: 16% of
  consecutive 100 ms samples in the sustained windows repeat the value before, and in the first second the power-usage
  reading can trail the instantaneous field by a sample (`posthoc.txt` §2). The boost came 0.21–0.43 s after the first
  call, so a kind's pre-boost power is one to three samples. On 15 of the 19 cells that fit n it is a single reading, or
  two that differ by more than 5% (unit A's bf16 zeros: 134.3 W at 1095 MHz, then 173.4 and 255.2 W at 1410 MHz; its
  n_fit is 3.75). The four cells with two readings that agree within 5% give n = 2.89–3.12, around the median 2.99, so
  the 2.31–3.75 range is partly this lag. Every post-hoc number that uses n carries it: the demands, the clocks at the
  limit, the 330 W gaps and zeros' 40% share ([`corrections-check.txt`](corrections-check.txt) §C10).
- **The A100's cool-die ladder** (`posthoc.txt` §6, `posthoc.json` `overshoot`). Each kind's power at the 1095 MHz
  application clock, read loaded before the boost, with n = 2.99, gives its demand at 1410 MHz and the clock at which it
  would draw 400 W. Demands in bf16: zeros 220–249 W, twos 266–276, π 290, one bit 305–314, ternary 367–409, 75% sparse
  400–410, rand 445–489, checkerboard 488–493, randn 550. fp16 randn 551–572, tf32 randn 552–555, int8 random 486–502.
  The predicted clocks of the 19 capped cells with a clean reading fall within 15.7 MHz rms of the measured early clocks
  (mean −7.1, range −33 to +24).
- **Leakage at the cap** (§3): on unit A the capped kinds' clocks fall 1.0–2.0 MHz per °C as the die warms 7–13 °C over
  the minute. Unit B's cells often started warm, their die changed by −3 to +11 °C, and its fits range from −3.6 to +1.3 MHz/°C. A warmer
  die leaks more at the same 400 W, which would explain why the sustained gap sits a little above the burst gap.
- **Energy per multiply-add** (§5; board · over idle). bf16 randn 2.99–3.02 · 2.57 pJ, zeros 1.73–1.78 · 1.35–1.38. fp16
  randn 3.08–3.09 · 2.64–2.65. tf32 randn 6.13–6.17 · 5.26–5.27, zeros 4.10–4.20 · 3.34–3.40. int8 random 1.95–1.97 ·
  1.67–1.69, zeros 1.23–1.24 · 0.96–0.99. These are at each kind's own clock (capped kinds run at lower clock and
  voltage), and they include an 8192³ GEMM's memory traffic. They are not like for like with the ET-SoC-1's
  resident-loop prices.

## Registered against what happened

| rule (prediction) | registered | measured | verdict |
|---|---|---|---|
| R1 (P2) | random below zeros' clock, SW cap ≥ 50%, thermal ≤ 5%, 0.95–1.03 of the limit | 0.899–0.906 of the clock, 100%, 0%, 0.991–0.996, 4 of 4 | **HOLDS** |
| R2 (P3) | TFLOPS per MHz across kinds within 3% | spreads ≤ 1.0034 sustained, ≤ 1.0143 burst | **HOLDS** |
| R3 (P4) | under 95% of the limit → ≥ 99% of 1410 MHz, SW ≤ 10%; SW ≥ 50% → ≥ 95% of the limit | 47 of 47 | **HOLDS** |
| R4 (P9) | capped random against uncapped zeros → ≥ 1.02; neither → within 0.02 | 20 of 20, all the first case, 1.059–1.139 | **HOLDS** |
| R5 (P5) | at a lower cap: random on it, a wider gap, quiet kinds keep their clock | the cap could not be set (rc 4) | **N/A** |
| R6 (P6) | bf16 sustained gap in [1.000, 1.122] at 400 W; at 330 W in 1.17–1.26 | ×1.111 (A), ×1.105 (B); 330 W not run | **HOLDS**; at 330 W **N/A** |
| R7 (P7) | sustained − burst gap in −0.01 to +0.05 | +0.002 to +0.023 | **HOLDS** |
| R8 (P8) | thermal reasons ≤ 5% in every sustained window | 0% in 51 cells; die ≤ 66 °C | **HOLDS** |
| R9 (P10) | Spearman ρ ≥ 0.7 with the chart | ρ = 0.90 | **HOLDS** |
| R10 (P11) | his loop within 0.03 of the cells | −0.032 (A), −0.017 (B) | **FAILS** |

P1 (his numbers) is the comparison above. The checks in `reduce.txt` all pass: both units are A100s, zeros give C = 0
in every format, and ≥ 90% of the expected samples fall in every sustained window. 7 of 51 cells (all on unit B) started 2–9 °C above
their cooling target after the 120 s cap, as the registered rule allows (`reduce.txt` § Checks).

## Departures, dated

- **D1, Mon 2 Nov 2026 ~11:05 PST, amendment A1, before the measured run.** Three changes:
  1. The smoke's container got an A100-SXM4-80GB, billed as `A100-40GB`. Both measured units got A100-SXM4-40GB boards
     (driver 610.57.04, VBIOS 92.00.45.00.03, 1215 MHz memory, a 1095 MHz application clock).
  2. A1 added the reported post-boost window `burst_b`.
  3. A1 added the band at each unit's own idle (58.9 and 55.9 W) beside R6's registered 88 W. It reads [1.000, 1.088,
     1.131] and [1.000, 1.090, 1.132], which also hold both gaps (`rules.R6.detail[*].band_at_own_idle`).
- **D2, ~11:20 PST, during the run.** The lower cap was refused, so the arm's five steps did not run. The 13 s cell after
  it ran at 400 W as planned (unit A `randn` pass 3).
- **D3, after the data.** `posthoc_e135.py` sections 6–7 (the pre-boost ladder, the 330 W prediction) were written after
  the data had been read. They are labelled post hoc everywhere, carry no verdict and change no registered number.
- Nothing else: no step was skipped on the budget, no unit was restarted, and no getter failed beyond field 185, the 1 s
  average power, which A1 had noted (`reduce.txt` § Checks).

## What this changes

- **For the blog.** The A100 measurement the post was missing now exists: the same kinds, the same windows, clocks and
  reasons logged. It says the gap is the power cap's, kind by kind. The burst and sustained gaps nearly agree (within
  0.023). The sustained gap equals the clock gap to 0.003. At Horace's own 330 W, a relation fitted on these boards gives
  ×1.19–1.22 in bf16 on one board, against his ×1.21–1.22 (post hoc, not measured at 330 W). Set beside the ET-SoC-1 it
  is one kernel against others, not one chip against the other (above). It does not settle where his 295/257 pair came
  from (the kinds page's item 3 stays a question for him).
- **For the kinds page, section 11 item 2:** narrowed, not closed. What it asked for at the default cap is measured on two
  boards, and the size ladder answers the size half of the layout question (one board, one run per size). Still open:
  - a lower cap on the same board, which needs a host where `nvidia-smi -pl` is allowed;
  - his unit and an H100;
  - shapes other than square and K-contiguous;
  - a large streaming GEMM on the ET-SoC-1 to set beside this one (E105, E107 and E119 do not run one).
- **Every cell this fills** (format × kind × {TFLOPS, clock, board W, energy per op, die °C, limit}) is in `results.json`
  `cells`. The headline cells are in the table at the top.

## Files

| path | what |
|---|---|
| `logs/e135-20261102-r1/{A,B}/` | the measured run, as the Volume holds it: `steps/NNN_<label>.json.gz` (every step's record: the plan entry, seeds, operand statistics, the cooling wait, every CUDA event's time), `samples/NNN.jsonl.gz` (every 100 ms NVML sample), `plan.json`, `STARTED`, `DONE` |
| `logs/e135-20261102-smoke1/S/` | the declared smoke (2048³, plumbing only, not scored) |
| `reduce.txt`, `results.json` | the registered reduction (`tools/gpu/e135/reduce_e135.py`): cells, gaps, replicates, Horace's loop, the lower cap, R1–R10, checks |
| `posthoc.txt`, `posthoc.json` | the post-hoc views (`tools/gpu/e135/posthoc_e135.py`), no verdicts |
| `smoke-reduce.txt` | the smoke through the same reducer |
| `billing.json` | the metered cost by app and resource, and the GPU-seconds |
| `rebuild.sh` | rebuilds every derived file here from `logs/` with Python 3 and no third-party modules |
| `corrections-check.py`, `corrections-check.txt` | the numbers behind the corrections after verification, recomputed from committed files (`python3 corrections-check.py > corrections-check.txt`, from this directory) |

The board's UUID appears only as a 12-hex hash (`static.uuid_sha12`): the `nvidia-smi -q` text in each static step has
its UUID, serial-number, chassis-serial and cluster-UUID lines replaced. That text keeps the GPU PDI, the Board ID and
the PCI bus id, which identify a rented cloud board or its slot and are no secret (C11). No token, key or workspace
secret is in any file.
