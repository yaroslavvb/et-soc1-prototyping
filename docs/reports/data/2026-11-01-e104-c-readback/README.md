# E104: fp16's accumulators read back, and its premium on sums that do or do not move (aifoundry1 card 1, 600 MHz)

*Sun 1 Nov 2026 (week 44), Q132. Pre-registered in `b8d24835` (committed 05:36:57 PST and pushed by 05:37:01, before the claim and the first launch): [`tools/claims-v3/kinds/E104.md`](../../../../tools/claims-v3/kinds/E104.md), frozen numbers in `predictions-e104.json`, tiles and every expected accumulator in `e104/e104.json`; the scorer `score_e104.py` and its self-test (22 of 22) were in the same commit. aifoundry1 card 1 at 600 MHz, 498.8 mV. TDP 65 W / threshold 65 °C / 600 MHz / 499 mV read under the card lock at the session's start (05:37) and end (06:21:50), never set. Nothing was written to the card, and no `--reset-ms` was sent. Claim 1566446179208925195 in #community-lab, posted 05:37:52 PST, released 06:22 PST by an edit of the same post, read back as `<ai> Claude says: using aifoundry1 card 1 for 1 h, until ~06:38 PST doc — released (edited)`.*

**What ran.** First the read-back: 110 launches of exactly n ops, 44 tiles, `sparsity_host` with one flag added (`--dump-c`, built in `build/e104/`, the same kernel ELF), every word of all 1,024 minions against three readings of fp16's accumulate, written down before any launch. Then 20 tiles for power: E92's fp16 tiles the fault names, plus three new designs, in both formats: `z_` (A = −0: the product is zero and the sum truly holds), `u_sub` (the adder swings as in `h_sub`, on 14/15 of its micro-ops, and the two halves of a lane's sums meet at each op's end), and `m_h_sub` with `w_h_add` (moving sums of equal magnitude, adder alternating or not). E78's runner and reduction ran unchanged (sha256-checked), with E82's frame on this card: E78's six anchors three times a pass, the `anchor_pi` tie first and last. Three passes ran (10410–10412), 118 runs of the planned 120, no run failed. **E78's pass gate set pass 10410 aside (`int8.zeros` departs −0.281 W from its line, limit 0.25 W), so the primary keeps two passes, t(0.975, 1) = 12.7.** Every interval is 95% over passes, paired within a pass. In parentheses: the registered arm with E78's pass gates opened, all three passes kept, t = 4.30. It is a sensitivity arm, and it moves no primary verdict.

## Results

**In plain words.** For the first time the accumulators were read off the chip, and they equal the RTL's arithmetic word for word: 110 of 110 reads, all 1,024 minions on one value in each. E92's fp16 "frozen" tiles are not frozen. fp16 truncates each aligned product separately, so an absorbed product that subtracts takes one unit off the sum on that micro-op, even if its partner adds. `h_sub`'s two halves read 4f800000 and 4f7fffe9 after 2 ops and are 12% apart by op 199,874 and 29% apart by op 541,999. The manual's sentence (exact sum, then toward zero) is wrong on silicon for `hh_sub`, `hl_sub`, `s_abs` and E88's `r_abs`; E92's frozen reading is wrong for all of them. fp32's frozen sums hold. **E92's fp16 watts stand and its reading goes: 6.71 W for `h_sub` − `h_add` splits into 3.55 W of the adder alternating, about what fp32 pays (3.76 W), and 3.16 W of the two halves swinging on the result path, the bench's model having said 3.72 and 3.27 W before the data. "1.55× per alternation" goes: with the halves together the ratio is 0.95 ± 0.30. "About 92% remains frozen" goes: in a sum that truly holds, random signs cost 2.15 W, about 45% of fp16's ~4.8 W step.** On sums that move alike the premium is 3.27 ± 1.96 W in fp16 and 2.12 ± 2.46 W in fp32, and that ratio is not resolved.

**1. The read-back settles C on silicon (R2 PASS, R1 RTL, R3 RTL).** Controls first, as registered: `fp16.c_abs`, `fp16.h_add`, `fp32.c_abs`, `fp32.h_add` read what all three readings say. Then every read of every tile equals `accum.c`, on all 256 words, all 1,024 minions. No minion ever disagreed. Each launch's own `iters` is n. (`scored.json` › `readback`, `results.md`, `posthoc-check.txt` F, raw `aifoundry1-c1/kinds/readback-p10402/readback.jsonl`.)

| what the card holds | tiles | read at n | C[0][0] / C[0][8] at the deciding read | frozen says | manual says | RTL says |
|---|---|---|---|---|---|---|
| **Walks. Frozen is wrong; manual and RTL agree** | `fp16.h_sub`, `c_alt`, `h_allsub` | 2, 16, 1,000, 199,874, 541,999 | `h_sub` n = 2: 4f800000 / **4f7fffe9** | 4f800000 / 4f800000 | 4f800000 / 4f7fffe9 | 4f800000 / 4f7fffe9 |
| **Walks. Frozen and the manual are both wrong** | `fp16.hh_sub`, `hl_sub` | the same | n = 2: 4f800000 / **4f7fffe9** | 4f800000 / 4f800000 | 4f800000 / 4f800000 | 4f800000 / 4f7fffe9 |
| | `fp16.s_abs` | the same | n = 2: **4f7ffff2 / 4f7ffff1**, 9 distinct words | 4f800000, 1 word | 4f7ffffa / 4f7ffff7, 10 words | 4f7ffff2 / 4f7ffff1, 9 words |
| | E88's `fp16.r_abs` | the same | n = 2: **4f7fffe9 / 4f7fffe9**, 1 word | 4f800000, 1 word | 4f7ffff1 / 4f7ffff5, 5 words | 4f7fffe9, 1 word |
| | E88's `fp16.r_walk` | 199,874 | c9c7b3b6 / c77e6a3f, 256 words | off on 256 | off on 256 | equal |
| **Walks in unison, one word** | E104's `fp16.u_sub` | 1,000, 199,874, 541,999 | n = 541,999: 5862b3ed / 5862b3ed | off on 256 | equal | equal |
| **Holds** | `fp16.c_abs`, `h_add` (±), `z_add`, `z_sub`, `z_s`, `z_allsub`, `z_hh`, `z_hl`, `x_add`, `x_sub` | up to 541,999 | `z_sub` n = 541,999: 588452f0 / 588452f0 | equal | equal | equal |
| **Holds at 0** | E88's `fp16.r_cancel`, `c_cancel` | 199,874 | 00000000 | equal | equal | equal |
| **Exact moving sums, as designed** | `fp16.w_c`, `w_h_add`, `w_h_sub`, `m_h_sub`, `signs` | up to 500,000 | `w_h_add` n = 500,000: 4bec82e0 / cb742400; `m_h_sub`: 4bec82e0 / 4b742400: the same magnitudes | equal | equal | equal |
| **fp32 holds** | `fp32.c_abs`, `h_add`, `h_sub`, `u_sub`, `c_alt`, `h_allsub`, `s_abs`, E88's `r_abs`, `z_add`, `z_sub`, `z_s` | up to 541,999 | `h_sub` n = 541,999: 7b0452f0 / 7b0452f0 | equal | equal | equal |
| **fp32, exact moving sums** | `fp32.w_c`, `w_h_add`, `w_h_sub`, `m_h_sub`, `signs` | up to 500,000 | | equal | equal | equal |
| **fp32 rounds step by step: fl(n S) is wrong here** | E90's `fp32.pm_pi`, E102's `fp32.bj_6` | 199,874 | `pm_pi`: 4af18877 / 4a6f8099, 17 words; `bj_6`: 8 words | off on 256 | fp32: equal to RTL | equal |

Of 110 reads, 110 equal the RTL's reading, 89 the manual's and 69 the frozen one, and those are the reads where a reading coincides with the RTL's. `h_sub`'s halves on the card, C[0][8] / C[0][0]: 0.99999 at n = 16, 0.99940 at 1,000, 0.87567 at 199,874, 0.70747 at 541,999 (`posthoc-check.txt` G). int8 was not read back.

**2. Where fp16's premium goes (R4 RESULT-PATH in every arm).** `u_sub` carries `h_sub`'s adder swing with the halves together, so `h_sub` − `u_sub` is the two halves' swing on the result path. E92's frozen reading says it is 1/15 of the alternation, 0.44 W; the bench's model on the RTL's sums said 3.27 ± 1.44 W. **Measured: 3.159 ± 0.507 W (3.183 ± 0.141).** fp32's same contrast, where both sums hold, is the control: 0.249 ± 1.059 W (0.268 ± 0.222), M4 0.46 W. On the minion rail: fp16 2.532 ± 0.301 W, fp32 0.654 ± 2.403 W. With the control taken off, fp16's swing is 2.910 ± 0.552 W (2.915 ± 0.110) over 91,208 more result bits an op: **28.5 fJ per result bit, the price E92 read on fp32's moving sums (29.7–30.0 fJ).** That is a rough count, because it moves with n, and it is post hoc.

| contrast, W | fp32 | fp16 | M4 before the data, fp32 / fp16 | E92's frozen reading, fp32 / fp16 |
|---|---:|---:|---:|---:|
| `h_sub` − `h_add`: E92's premium | 4.006 ± 0.423 (3.898 ± 0.472) | **6.713 ± 0.219** (6.660 ± 0.232) | 3.99 / 6.99 | 4.27 / 6.62 |
| `u_sub` − `h_add`: the adder swinging, the halves together | 3.757 ± 1.482 (3.630 ± 0.618) | **3.554 ± 0.288** (3.478 ± 0.334) | 3.53 / 3.72 | 3.99 / **6.18** |
| `h_sub` − `u_sub`: the halves' swing | 0.249 ± 1.059 (0.268 ± 0.222) | **3.159 ± 0.507** (3.183 ± 0.141) | 0.46 / 3.27 | 0.28 / **0.44** |
| `z_sub` − `z_add`: the alternation on zero products, the adder's output still | 2.603 ± 5.319 (2.631 ± 1.047) | **one kept pass: 3.635** (3.762 ± 1.618, n = 2) | 2.56 / 3.58 | 4.27 / **6.62** |
| `w_h_add` − `h_add`: the sums moving, the adder always adding (post hoc) | 3.677 ± 0.695 (3.763 ± 0.395) | 4.036 ± 3.302 (3.987 ± 0.680) | | |

**E92's watts stand** (R8 PASS): `h_sub` − `h_add` on this card is 6.713 W against E92's 6.812 W × 0.9722 = 6.623 W. `fp16.z_sub` ran in only two passes, one of them the set-aside pass: E78's runner skipped it in 10412 (below), so its contrast has no interval in the primary and no rule rests on it.

**3. fp16's alternation premium on sums that move alike (R6 INCONCLUSIVE).** `m_h_sub` and `w_h_add` hold the same magnitudes (read back: the same words at n = 500,000 apart from the sign bit) and differ only in whether the adder alternates. **fp16: 3.271 ± 1.961 W (3.253 ± 0.392), rail 2.465 ± 0.981 W (2.549 ± 0.407), about 760 fJ per lane alternation. fp32: 2.121 ± 2.457 W (2.099 ± 0.489), rail 1.920 ± 3.019 W (1.906 ± 0.593), about 490 fJ.** M4 said 2.65 ± 0.88 and 1.71 ± 1.25 W; E92's reading, 1.552 × fp32's, said 4.20 W. The primary cannot separate them: two passes, t = 12.7.

**4. fp16 against fp32 on real sums.** The ratio depends on what the sum does, so there is no one number per alternation.

| regime | fp16 / fp32, per pass, board | rail | fJ per lane alternation, fp32 / fp16 (board, primary) | what it is |
|---|---:|---:|---:|---|
| E92's `h_sub` − `h_add` | 1.676 ± 0.232 (1.711 ± 0.156) | 1.491 ± 1.015 (1.544 ± 0.302) | 931 / 1,560 | fp16's sums part, fp32's hold: not like for like. E92 read 1.552 ± 0.250 |
| **the halves together, `u_sub` − `h_add` (R5 1.55x GOES)** | **0.947 ± 0.297** (0.960 ± 0.079) | 0.962 ± 0.106 (0.946 ± 0.076) | 965 / 913 | like for like with the result bus quiet: about equal. Arm-sensitive: INCONCLUSIVE with dips kept (0.882 ± 1.128) and at leakage 0.545 (0.909 ± 0.688) |
| zero products, `z_sub` − `z_add` | one kept pass: 1.203 (1.325 ± 1.553, n = 2) | | 605 / 844 | the inverted operand alone; M4 said 1.40; not resolved |
| **moving alike, `m_h_sub` − `w_h_add` (R6 INCONCLUSIVE)** | **1.562 ± 2.734** (1.563 ± 0.535) | 1.309 ± 2.568 (1.355 ± 0.540) | 493 / 760 | M4 said 1.55; not resolved in any arm |

A reading of the two formats, from the bench's counts and these contrasts: fp32's premium has an inverted-operand part (`z`, about 2.6 W) and a part where the adder's output swings between C and C − ε before rounding back (`u` − `z`, 1.153 ± 6.801 W, 0.998 ± 1.487 W with all three, M4 0.97 W). fp16's window clears those low bits (`txfma_f4.v`, `f5.v`), so its `u` − `z` is near nothing (−0.334 ± 2.932 W, n = 2, M4 0.14 W), and it pays for two aligned operands instead of one. Those roughly cancel when the result bus is quiet. The result path itself costs the same per bit in both formats (result 2, and `w_h_add` − `h_add` in the table).

**5. Where a random sign's ~5 W goes, in each format.** No ±1 tile ran here; the step is E92's on aifoundry3 with its dips removed, carried by card 1's float scale, 0.9722, an estimate. Rows marked measured are contrasts on one card; on E92's rows the parentheses are its dips-removed arm.

| | fp32 (W) | fp16 (W) |
|---|---|---|
| **measured, E92, aifoundry3:** ±1 − +1 | 4.851 ± 1.128 (5.016 ± 0.219) | 4.826 ± 0.467 (4.965 ± 0.089) |
| carried to this card | 4.88 | 4.83 |
| **measured here, C read back as held:** random B signs on zero products, `z_s` − `c_abs` (A's signs still) | **1.728 ± 0.827** (1.663 ± 0.322) | **2.153 ± 0.330** (2.172 ± 0.103) |
| its share of the step | 0.354 ± 0.170 (0.341 ± 0.066) | **0.446 ± 0.068** (0.450 ± 0.021) |
| **measured, E92 and E88, C read back here as held:** `s_abs` − `c_abs`, absorbed, A's signs moving too | **2.377 ± 0.556** (2.520 ± 0.171), share 0.50 | not a held sum |
| **measured here:** E92's `s_abs` − `c_abs`, read back as 9 words | | 4.374 ± 1.653 (4.467 ± 0.515), M4 4.63 |
| **measured here:** that against `z_s`: parted sums and A's sign bits | | 2.220 ± 1.323 (2.295 ± 0.412), M4 2.43 |
| a residual: the step less the held part, read as the sums moving apart | 2.4–3.2 | 2.7 |

So the two formats have the same budget, within what this resolves: **about a third to a half of the ~5 W is there with the sum read back as held, and about half goes with the sums moving apart.** "92% in fp16 against half in fp32" was an artefact of a tile whose sums were parting; E92's 5.8 fJ per result bit against 30 fJ was the same artefact, with the bits miscounted. This split is by subtraction: it crosses two cards and designed tiles, `z_s` keeps A's signs still (zero products forbid (+0, +0) words, which the gate would close), and no tile holds ±1's own sums in fp16.

**6. The bench's model held (R7 PASS).** rms(D − M4) = 0.312 W over 19 float tiles, with `fp16.z_sub`, one kept pass, left out (0.288 W over all 20 with all three passes); M4 runs 0.22 W high on average, worst `fp16.c_alt` −0.59 W, 18 of 19 inside their frozen intervals. Every one of the 19 frozen contrasts lies inside M4's interval in both reductions (`posthoc-check.txt` I). The frozen reading misses `u_sub` − `h_add` by 2.70 W, `z_sub` − `z_add` by 2.86 W, `h_sub` − `u_sub` by 2.74 W and `z_s` − `c_abs` by 2.29 W, all-three means.

**7. The session tied (S1 PASS).** Against E82 with dips removed: `fp32.randn` +0.05 W, `fp16.randn` +0.03 W, `anchor_pi` −0.06 W, `int8.full` +0.11 W, 600 MHz, 498.8 mV, 546.001 cycles per op. Tie drift 0.34 W a pass.

## What the page may now say

**§5.3.** The table stands; no number moves. Its fp32 row freezes by absorption and its fp16 row by cancellation, and both are now read back. Replace "the frozen sums were checked by a desk emulation, not read back from the card" with: "E104 read them back: fp32's `r_abs` and `c_abs` hold n × 2¹⁰⁰ on every word of all 1,024 minions through a launch, and fp16's `r_cancel` and `c_cancel` hold 0 (one read each, n = 199,874); int8's were not read back." It may add: "fp16 cannot be frozen by absorption when a product subtracts: it truncates each aligned product separately, so E88's other fp16 design, `r_abs`, walks one unit a micro-op."

**§5.4.** Replace "Where the cost goes is not measured", and the guess it names, with: in both formats, with the operands fixed and the sum's sign alone changed, the adder alternating costs real power with the result held: 3.76 ± 1.48 W in fp32 and 3.55 ± 0.29 W in fp16 at 14/15 of the micro-ops (one card, 600 MHz, two kept passes, designed tiles, C read back), about 900–960 fJ per lane alternation in both. A steady subtract costs nothing measurable in fp32 (E92, 0.04 ± 0.35 W). When two halves of a lane's sums part, the result path adds about 30 fJ per result bit, the same in both formats: 3.16 ± 0.51 W on fp16's `h_sub`. Of the ~5 W random-sign step, about a third to a half is there with the sum read back as held; the rest, by subtraction, goes with the sums moving apart. E88's 2.52 ± 0.19 W of 4.78 in fp32 now sits on a sum read back as held. A reading: neither format's step is priced by its sign bits, which is how fp16 can pay what fp32 pays with twice the flips.

**May not say:** "92% remains frozen"; "1.55× per alternation", or "fp16's alternation is dearer", with the result bus quiet; "frozen" for fp16's `h_sub`, `c_alt`, `hh_sub`, `hl_sub`, `s_abs`, `h_allsub` or E88's `r_abs`; "rounds toward zero" as the whole reason; the manual's §9.3.3 sentence as what silicon does; the moving-sum ratio as decided; the split as measured; anything about other cards. Say "board power", "one card", "designed tiles".

**Item 2.** Its named guess closes: the "adder alternates" reading is tested on silicon in both formats, with C read back, and it holds, and fp16's half of the question is answered on real sums. As a measured budget it does not close: the split of ±1 itself is by subtraction across two cards, and R6 is INCONCLUSIVE. **I would take the guess off the open list and keep one line: "the split of a random sign's ~5 W is an estimate by subtraction; a held sum with both operands' signs moving has run in fp32 only (`s_abs`)."** fp16's could be built from products that cancel exactly, with random signs (`x_`'s design); nothing here ran it for power.

## Registered against what happened

| rule | what | registered | happened | primary | arms that move |
|---|---|---|---|---|---|
| E104-R2 | the controls: where the three readings coincide | every read equal | 31 tiles, every read equal | **PASS** | read-back has no arm |
| E104-R1 | E92's six fp16 tiles | RTL / MANUAL / FROZEN / NONE | every read of all six equals `accum.c` | **RTL** | read-back has no arm |
| E104-R3 | E88's `r_abs`, `r_walk`, `fp16.u_sub`, `fp32.pm_pi`, `bj_6` | the same | equal `accum.c` | **RTL** | read-back has no arm |
| E104-R4 | fp16 `h_sub` − `u_sub` | above +1 W: RESULT-PATH; inside ±1 W: FROZEN-READING | 3.159 ± 0.507 W | **RESULT-PATH** | none (lowest lower bound 2.22 W, dips kept) |
| E104-R5 | fp16 / fp32, `u_sub` − `h_add` | below 1.552: GOES; holds it and above 1.2: HOLDS | 0.947 ± 0.297 | **1.55x GOES** | INCONCLUSIVE: dips kept (0.882 ± 1.128), leak 0.545 (0.909 ± 0.688) |
| E104-R6 | fp16 / fp32, `m_h_sub` − `w_h_add` | the same | 1.562 ± 2.734 | **INCONCLUSIVE** | none |
| E104-R7 | M4's rms over the float tiles | PASS ≤ 0.60 W, FAIL > 1.00 W | 0.312 W, n = 19 | **PASS** | INCONCLUSIVE at leak 0.545 (0.76 W) |
| E104-R8 | fp16 `h_sub` − `h_add` against E92's × 0.9722 | within ±1 W of 6.623 W | 6.713 W | **PASS** | none |
| E104-S1 | the session tie | E94's bands | every cell inside | **PASS** | FAIL at leak 0.545 and leak 0: those arms correct D by another slope than E82's values carry, as in E92 |

**What I expected, frozen:** R2 PASS, R1 RTL, R3 RTL, R4 RESULT-PATH near 3.27 W, R5 GOES, R6 INCONCLUSIVE or HOLDS, R7, R8, S1 PASS. All came out so. Nothing here tested the bench's arithmetic blind beyond these tiles.

**Departures and disclosures.**
1. **The primary keeps two passes.** Pass 10410 is set aside by a registered gate on a kind this experiment does not study, `int8.zeros` (0.281 W against 0.25 W). The rule was E78's, and it stands; every interval in the primary carries t = 12.7. The all-three arm is the registered gates-off arm: labelled, in parentheses, and no verdict comes from it.
2. **Two runs did not run.** E78's runner skips an item whose die reading has not come back to the launch reading in its wait: `fp32.zeros` in 10410 and `fp16.z_sub` in 10412. So `fp16.z_sub` has one kept pass, and E104's `z` premium has no interval in the primary. No rule rests on it, and the registered plan was three passes, so no fourth ran.
3. **`u_sub` and `z_` were added at the desk, with the third reading, before the registration,** after I found that a zero product does not reproduce an absorbed one even on fp32 (M4 3.99 against 2.56 W) and after E102's verifier sharpened the fault to three readings. Nothing in this experiment was amended after `b8d24835`.
4. **The card sat claimed and idle from 05:38:45 to 05:47:28:** an `ssh … | cut` of mine hung on a new ssh control master. The smoke had finished and nothing was running.
5. **Where the desk compute ran.** The Intel's load guard stopped `make_e104.py` and then the collection (state T), so both ran on aifoundry1's CPU in `nice`, with its cards idle and no process holding either: the accumulators and `make_e104.py` before the claim, the collection after the release. The outputs were copied back.
6. **`score_e104.py` was run on the read-back alone before the first pass was read,** at 05:50, while the queue ran, to report the lane's status. It read no power data.
7. The runner's log lines read "E78 pass … tiles verified against kinds.json": `run_e78.py`'s unchanged strings.

## Caveats

Two kept passes in the primary. One card, one clock, designed tiles. C sits at n × 2^31 or small integers, not where real tensors land. The reads are at the end of a launch of n ops, so they say nothing of C inside a launch beyond what the words imply. The power runs use the existing host and the read-back an added flag, with the same kernel; the reads ran on the same tiles, sha256-checked. The E92 values on this page are from another card, carried by a scale. `z_` measures a design with zero products, whose multiplier path does not move, and `z_s` holds A's signs still, so it is not `s_abs` with the walk removed. `u_sub`'s halves differ by up to 7 ulps inside an op and meet at its end, and it walks 7 ulps an op; its B stream also moves at the k joins, where `h_sub`'s does not. The bit counts behind fJ per result bit move with n (E102's verifier: 58,584–142,936 at one index; 102,851 at 128). The watts are the board's; the rail figures are about 0.8 of them.

## Files

`e104.json` (the registered reduction: every item, per pass), `runs.csv`, `reduce.txt`, the arms (`e104-dipskept`, `e104-gatesoff`, `e104-auto`, `e104-leak0.1994 / 0.3803 / 0.545 / 0`, `.json`, `.csv` beside them, `reduce-*.txt`, `reduce-*.log`), `scored.json` and `results.md` (every rule, every read, every contrast, every tile), `score.log`, `code.sha256`, `logs/` (the queue, read-back and dry-run logs, the session's start and end config reads, the binaries' sha256), `aifoundry1-c1/kinds/` (the three passes, `kinds-smoke-p10401`, and `readback-p10402` with `readback.jsonl`), `desk/` (the desk check on the fixed bench, `desk-e104*.txt`, `.json`; the bench's counts, `counts-e104*.json`; the verifier's table and `tab-check.txt`, 45 of 45 rows the same), `posthoc-check.py` / `.txt` (labelled post hoc: every number above beyond `scored.json`, standard library only). The tiles and the registration are in `tools/claims-v3/kinds/` (`E104.md`, `predictions-e104.json`, `make_predictions_e104.py`, `e104/`, `make_e104.py`, `manual_e104.c`, `desk_e104.py`, `tabcheck_e104.py`, `patch_host_e104.py`, `build_host_e104.sh`, `readback_e104.py`, `block_readback_e104.sh`, `e104_common.py`, `run_e104.py`, `block_e104.sh`, `queue_e104.sh`, `run_e104.sh`, `reduce_e104.py`, `score_e104.py`, `collect_e104.sh`, `selftest_e104.py`).
