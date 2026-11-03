# E158: a large GEMM's time per op as the L3's retention by reuse distance, under aifoundry2's own governor

*On the kinds page, [section 11, what is still open](https://spacesheep.dev/@yaroslavvb/horace-kinds-of-numbers#11-what-is-still-open): **item 1, "Where a large GEMM falls"**, its rest after [E146](../2026-11-02-e146-gemm-stores/README.md), and **rank 7 of Q138's final critic**: *"A large GEMM's time per op: the L3's retention by reuse distance ... Register a ladder of B-panel reuse distances from 20 to 56 MB, with and without C's traffic, with MAB's frozen prices predicting the L3-served share. Rule: the fitted retention curve predicts F6's time per op within 3%."* Q139 continues the owner's ask of 2 November 2026: *"feel free to settle any unanswered questions regarding horace's power model"*, with Q137's goal, *"to be able to predict the power requirement and heat generation of various kinds of numeric computations as accurately as possible"*.*

*Tue 3 Nov 2026 (week 45), Q139. Pre-registered in `2cfc4525` ([`tools/claims-v3/e158/E158.md`](../../../../tools/claims-v3/e158/E158.md): the desk's exact stack distance of every line, three frozen time models through E146's MAB prices, the scorer, rules R0-R8, a self-test, a toy-card dry run of the whole queue and the device-command audit), committed at 04:37:54 PST and pushed before the claim (04:38 PST) and the first card touch (04:39:07 PST). **aifoundry2 card 0 under its own governor**: `ettelem config` read 65 W / 65 °C (low_power, 600 MHz, 519 mV) at the queue's start and end and after every run; nothing was set, no statistics reset, no firmware-revisions query, no residency read, **no WRITE command of any kind** ([Device commands sent](#device-commands-sent)). E136's binary, unchanged (its sha256 checked before every session): every shape is an argument. Zeros in every cell. The card post was the day's single post in #community-lab, message `1567153765390487573` (posted at 04:29 PST by another lane of this round), rewritten at 04:38 PST to add "using aifoundry2 for 1 h, until ~05:38 PST" and at 05:00 PST to drop that clause, the two other cards' clauses kept word for word. **20.8 card-minutes** (04:39:07 to 04:59:57 PST): the smoke, the two stop-path tests and one session of 98 runs (19.7 min), none refused, none cut. No other user was logged in at any check (`aifoundry2/idle_logins.jsonl`: `other_users` 0 throughout).*

*Corrected after verification (a dated note, Tue 3 Nov 2026, about 05:40-05:55 PST; desk only: no card, no device command,
nothing re-run). An independent verifier re-derived the reduction (0 differences), the post hoc file (byte-identical) and
every command's class, and found the registered verdicts sound. It found two major faults and three minor ones in what this
README draws from them. None changes a measured, frozen or registered number or verdict. Each is corrected by a dated note
beside the text it concerns, the text itself left as it was, and set out in full in
[§ Corrections after verification](#corrections-after-verification-tue-3-nov-2026) at the end. The numbers are printed by
[`corrections_e158.py`](corrections_e158.py) → [`corrections.txt`](corrections.txt) ([`corrections.json`](corrections.json)),
labelled post hoc. **C1:** `F6` was never *fitted*, but it was *run*: E146 ran it on 2 November, and its 0.33 share shaped
this ladder. R3's registered pass rests on one rung: refitted without `K4n8`, ISO misses `F6` by +8.0 / +7.9 / +5.9% (a FAIL
of the 3% rule). For a new shape the figure is the out-of-sample one: E146's ladder 7.2% → 6.0% rms (KB ≥ 2; 10.9% → 10.6%
on all 24), `D2` and `D4` here 13.1% → 6.3%. **C2:** the collapse is read from two rungs with one row of blocks, not a law of
power-of-two strides. `F6`, `K6n4`'s layout with three row blocks, kept 0.33, and `K4n8` ran 6.5% slower than if every far
line came from DRAM, so part of its cost lies outside the L3. The next term is a block-stride term (the L3's set mapping or
the DRAM's channel and bank mapping), for a stride ladder with the pools' device addresses logged to test.*

## The answer

**The L3 serves every far B line whose reuse distance (C's lines counted) is under 32 MB, 72-94% of them at 35-37 MB, and about half from 39 to 59 MB, in all three families (nine rungs, 0.46-0.56, mean 0.51 ± 0.04 sd, with no fall from 39 to 59 MB; the C-heavy rungs, C 44-45% of the distance, a little lower, 0.48 on average, than the others, 0.55, with C at 16-27%), except in two block structures, where it serves 18% or less: NB 8 with KB 4 (`K4n8`, −0.20, slower than all-fresh; E146's `D4` the same, −0.07) and NB 4 with KB 6 (`K6n4`, 0.18), a B panel of four to six blocks at a power-of-two stride.** So **retention is not a function of reuse distance at any weight of C** (R2: NO SINGLE CURVE, the best rms 0.129 in share against the 0.06 bar, near-best w 0.3-1.0), C's share of the distance moves it by about 0.07 at most, and E146's two readings were each one shape's case: `D2`'s 58% is the step region (38 MB), `F6`'s 33% lies between the plateau and its (NB, KB) twin's collapse. Every share replicated across the three passes within 0.017. **The critic's rule passes as registered: ISO, the isotonic retention curve fitted on the 22 rungs, predicts `F6`'s time per op within 3% in every format, +0.41% (fp32), +0.26% (fp16), −0.76% (int8), where E146's MAB (strict LRU, "before") was −10.0%, −10.3% and −9.4%, and in each pass alone (0.05-0.94%)** (R3, R6). *But the pass rests on ISO pooling the plateau with the two collapse rungs in `F6`'s distance bins (r 0.44 at 42-48 MB, 0.17 at 54 MB; `F6` measured 0.33): read rung by rung, `F6` misses by +10.5% (the plateau's 0.51), −3.7% (its (NB, KB) twin `K6n4`) and +12.9% (the rung nearest in distance), so the next term is the L3's set mapping, not a curve (post hoc, [`posthoc.txt`](posthoc.txt) §2-§3).* Numbers from `results.json` (`rules`, `errors`) and `posthoc.txt`.

*(Dated note, Tue 3 Nov 2026, after verification, C1, C2 and C4.)* Four readings above go further than the data.
**(a)** "A B panel of four to six blocks at a power-of-two stride" names a rule read from two rungs, both with one row of
blocks (`K6n4`, `K4n8`; no other plateau rung has NB 4 or 8 with KB ≥ 4). The shapes with more row blocks disagree: `F6`
(`K6n4`'s NB 4 and KB 6, three row blocks) kept **0.329**, and E146's `D4` (`K4n8`'s NB 8 and KB 4, four row blocks) read
−0.071. **(b)** `K4n8`'s −0.20 is not a fraction the L3 kept: its T800 is **6.5% above MAB's all-fresh price** (2.125 against
1.996 µs; `D4` 2.2% above), so part of its time lies outside the L3, in a DRAM-side mapping at that stride or in conflicts
with A's lines. **(c)** "At any weight of C" holds for the 22 rungs as registered (R2). Post hoc, the 20 rungs off the two
collapses fall on one ISO curve at **w 0.8-1.0, rms 0.026**, against 0.147 at w = 0; by R2's words that reads **C OCCUPIES THE
L3** (C's lines take the L3 like the operands'). And the 0.07 that "C's share moves it" is **KB 2 against KB 4-6**: every
C-heavy rung is KB 2 and no other plateau rung is, so C's share and KB are confounded by design. **(d)** The pass is carried by
`K4n8`: without it ISO misses `F6` by +8.0 / +7.9 / +5.9%, without both collapses by +10.3 / +10.3 / +7.8%. "The L3's set
mapping" should read **a block-stride term (the L3's set mapping or the DRAM's channel and bank mapping)**.
[§ Corrections, C1, C2, C4](#corrections-after-verification-tue-3-nov-2026).

| rung (arm) | far B distance, MB: C counted (operand + C) | C's share | T800 fp32, µs | far-B share served by the L3 (passes 1 / 2 / 3) |
|---|---|---|---|---|
| `K2n4`-`K2n7` (`gemmL1x{4-7}x2`) | 19-31 (12-18 + 7-13) | 37-42% | 1.323-1.328 | 0.997-1.005 |
| `K4n2`-`K4n4` (`gemmL1x{2-4}x4`), `K6n2` (`gemmL1x2x6`) | 19-31 (16-24 + 3-7) | 11-23% | 1.339-1.344 | 1.004-1.012 |
| `K2n8` (`gemmL1x8x2`) / `K6n3` (`gemmL1x3x6`) / `K4n5` (`gemmL1x5x4`) | 35 / 35 / 37 | 43% / 14% / 24% | 1.364 / 1.409 / 1.530 | **0.942** / **0.903** / **0.717** |
| `K2n9`-`K2n13` (`gemmL1x{9-13}x2`) | 39-55 (22-30 + 17-25) | 44-45% | 1.642-1.678 | **0.457-0.514** (each within 0.015 across passes) |
| `K4n6`, `K4n7` | 43, 49 | 26%, 27% | 1.633, 1.649 | **0.559, 0.534** |
| `K6n5`, `K6n6` | 51, 59 | 18%, 19% | 1.635, 1.645 | **0.555, 0.540** |
| **`K6n4`** (`gemmL1x4x6`: NB 4, KB 6) | 43 (36 + 7) | 16% | 1.878 | **0.181** (0.186 / 0.183 / 0.174) |
| **`K4n8`** (`gemmL1x8x4`: NB 8, KB 4) | 55 (40 + 15) | 27% | 2.125 | **−0.199** (−0.199 / −0.197 / −0.202): slower than MAB's all-fresh 1.996 |
| E146's `D2` (`gemmL4x8x2`) / `D4` (`gemmL4x8x4`) / **`F6`** (`gemmL3x4x6`) | 38.3 / 61.5 / 50.5 | 39% / 24% / 14% | 1.664 / 2.106 / **1.911** | 0.578 / −0.071 / **0.329** (E146: 0.574 / −0.067 / 0.327) |

The share is read through MAB's frozen prices from the measured T800 (`model_e158.share_of`: the far B lines all fresh against all from the L3, every other line as strict LRU says); in fp32 its axis spans 0.65 µs, so 0.01 of share is 0.0065 µs. The fp16 and int8 K4 rungs read the same shares within 0.014 (fp16) and 0.03-0.12 higher (int8, through MAB's int8 prices) (`posthoc.txt` §1). Every check of C against the host's own reference over the whole K read **exact**, in the smoke and in all 98 runs (R0).

**So for the blog's kinds table, on aifoundry2 under its own governor:** what a large GEMM's time per op depends on, past the 32 MB L3, is not how far a block of B travels before it comes back but how its blocks fall on the L3: about half of a returning B panel is still in the L3 at 39-59 MB, unless the panel's blocks sit at a power-of-two stride, when almost none is (18% or less). The kind of number does not enter (every cell zeros; E146's R7). For zeros, the energy per op follows the time per op: 46.8 µJ an op step on the L3-held rungs against 72.2 µJ on the slowest (+54%), the board drawing 34.1-35.4 W throughout (`posthoc.txt` §5).

*(Dated note, Tue 3 Nov 2026, after verification, C2 and C3.)* "Unless the panel's blocks sit at a power-of-two stride, when
almost none is" holds for the two single-row-block rungs only (post hoc); `F6`, with `K6n4`'s layout and three row blocks,
kept 33%. **The 46.8 → 72.2 µJ (+54%) is the whole board's energy per op step, the base included.** Over the idle rest
(21.70 W) it is **17.8 → 26.3 µJ (+48%)**; over E119's 800 MHz base (33.61 W) it **falls, 1.84 → 1.13 µJ (−38%)**, because
the slower shapes draw a little less (34.1 W against 34.5-35.4). [§ Corrections, C3](#corrections-after-verification-tue-3-nov-2026).

## Registered against what happened

98 runs in one session, none refused by the admission rule, none cut by the cap.

| rule | registered | measured | verdict |
|---|---|---|---|
| R0 the ties | every check of C exact or approx; smoke cycles 50-250% of STRICT-C's; `K4n2` (= E146's `L4`), `D2`, `D4`, `F6` T800 within 2% of E146's | all exact; the smoke passed the queue's check; −0.31% to +0.29% (8 cells) | **PASS**; replicate **PASS** (8 of 8) |
| R1 the shape | every share in [−0.10, 1.10]; STRICT if every rung within 0.15 of STRICT-C's share | `K4n8` −0.199 (outside); 14 of 22 rungs more than 0.15 off STRICT-C, 12 off STRICT-NOC | **INCONSISTENT** (`K4n8`: MAB cannot carry it); **SOFT** against both |
| R2 C's weight | ISO's near-best interval of w; NO SINGLE CURVE if its least rms > 0.06 | least rms 0.129 (w 0.8-1.0 tied); 0.192 at w = 0; near-best 0.3-1.0. LOGI: x50 45.2 MB, s 8.0 MB, w 0.92, rms 0.188 | **NO SINGLE CURVE** |
| **R3 `F6` (the critic's rule)** | ISO at its w predicts `F6`'s T800 here within 3%, per format; fp32 primary | ISO +0.41% / +0.26% / −0.76% (fp32 / fp16 / int8); against E146's `F6` +0.47% / +0.17% / −0.45%; LOGI −0.40% / −0.49% / −2.26% | **PASS** ×3 (LOGI PASS ×3) |
| R4 out of sample | ISO's rms on E146's 18 KB ≥ 2 cells at least 2 points under STRICT-C's | ISO 6.0%, STRICT-C 7.2% (all 24: 10.6% against 10.9%); `D2`, `D4` here: ISO 6.3%, STRICT-C 13.1% | **NOT BETTER** |
| R5 the formats | ISO (fitted on fp32) predicts the K4 rungs in fp16 and int8 within 3% | 10 of 14; misses `K4n7` −3.8% (both), `K4n8` +12.4% / +13.3% (ISO misses those rungs in fp32 too) | 10 PASS / 4 FAIL |
| R6 the passes | shares per pass; ISO refitted per pass | every rung within 0.017 across passes; ISO's w 0.9 in each; `F6` +0.05% to +0.64% (fp32, fp16), −0.55% to −0.94% (int8) | reported; R3 holds in every pass |
| R7 power (reported) | zeros' p800 against P0, strict and ISO's lines | P0 3.57 W rms (reads 2.7-4.4 W high in every cell; 34 of 42 within 4 W); with ISO's lines 3.48 W | reported |
| R8 cycles (printed) | per rung, cycles per op at the measured clock | 1,056-1,075 cycles an op held; 1,305-1,344 on the plateau; 1,498-1,700 on the collapses; `F6` 1,523-1,537 (`posthoc.txt` §6) | printed |

**The failed rules have one cause: retention past 32 MB is set by the shape's block structure, not by its distance.** R1 fails because one such structure (`K4n8`) runs slower than MAB's all-fresh time (its DRAM lines cost more than `c16`'s, or its B panel conflicts with A's lines, which MAB holds in the L3); R2 because no weight of C lines the families up; R4 and R5 because ISO, a curve, cannot carry the collapses (it reads `D4` and `D8` 8.5% and 11.9% fast, `K4n8` 12-13% fast).

*(Dated note, Tue 3 Nov 2026, after verification, C1 and C2.)* "One cause" goes too far for R1. `K4n8` runs 6.5% slower
than if every far line came from DRAM, which no retention fraction, and no L3 set-mapping term alone, can carry: its cost is
partly outside the L3. And the misses named last are of two kinds: `D4` (+8.5-8.7%) and `D8` (+11.8-11.9%) are out of
sample, while `K4n8` (+12.4-13.3%) and `K6n4` (+10.0%) are rungs ISO was fitted on.
[§ Corrections, C1, C2](#corrections-after-verification-tue-3-nov-2026).

## What E158 does to predicting power and heat

| quantity | before | after | |
|---|---|---|---|
| time per op of the fresh shape `F6`, fp32 / fp16 / int8 (never fitted) | E146's MAB (STRICT-C) −10.0% / −10.3% / −9.4%; PRIOR (a curve fitted on E146's ladder) the same | **ISO +0.41% / +0.26% / −0.76%** (0.52% rms); LOGI 1.36% rms | registered (R3); the pass is the pooled curve's (above) |
| time per op of the 22 ladder rungs (fp32) | STRICT-C 15.0% rms; PRIOR 11.9% | ISO 4.6% rms (in sample) | — |
| time per op of E146's committed ladder (another session), the 18 KB ≥ 2 cells / all 24 | STRICT-C 7.2% / 10.9% rms | ISO 6.0% / 10.6%; LOGI 4.5% / 8.5% | registered (R4: not better by 2 points) |
| zeros' burst board power, 42 cells | P0 (E136's law, strict lines) 3.57 W rms, reading high in every cell | P0 with ISO's lines 3.48 W | reported (R7) |
| zeros' energy per op | — | follows time per op: +54% from the L3-held rungs to the slowest, at 34-35 W | post hoc §5 |

*(Dated note, Tue 3 Nov 2026, after verification, C1 and C3.)* **Row 1:** `F6` was never fitted, but E146 ran it on 2
November (T800 1.9121 / 1.9064 / 1.9240 µs) and its 0.33 share shaped this ladder. The registered 0.3-0.8% is a pooled
curve's pass that one rung carries: refitted without `K4n8`, ISO misses `F6` by **+8.0 / +7.9 / +5.9%**. **For a new shape,
read row 3** (E146's ladder, out of sample: **7.2% → 6.0%** rms on the 18 KB ≥ 2 cells, 10.9% → 10.6% on all 24) and `D2` and
`D4` here (**13.1% → 6.3%**), with ISO's single misses on the power-of-two-stride panels (`D4` +8.5%, `D8` +11.9%, out of
sample). **Row 5:** the +54% is the whole board's energy per op step (46.8 → 72.2 µJ, the base included); over the idle rest
it is **+48%** (17.8 → 26.3 µJ), over E119's 800 MHz base **−38%** (1.84 → 1.13 µJ).
[§ Corrections, C1, C3](#corrections-after-verification-tue-3-nov-2026).

The term this measures is **where a large GEMM's missing lines are served** (strict LRU's line classes, E146's MAB input). Its time error on a never-run shape falls from 9-10% to under 1%. The result does not carry to other shapes as a law. A distance curve misses the block structures that collapse (8.5-13% on `D4`, `D8` and `K4n8`), so the next term is the L3's set mapping of a panel's block stride, which these records cannot model without the pools' device addresses (not logged). For heat, nothing changes directly. The die read 48-51 °C in every zeros burst (the heat law is E146's), and a GEMM's power and heat follow its time per op through E = P·T and the governor's clock, so the gain is in the time.

*(Dated note, Tue 3 Nov 2026, after verification, C1 and C2.)* "A never-run shape" should read **a never-fitted shape**
(`F6`, which E146 ran on 2 November), and its "9-10% to under 1%" is one rung's pass (without `K4n8`, +8.0 / +7.9 / +5.9%).
The time term's error on new shapes is the out-of-sample one: 7.2% → 6.0% (KB ≥ 2), 10.9% → 10.6% (all 24), `D2` and `D4`
13.1% → 6.3%. **The next term is a block-stride term, the L3's set mapping or the DRAM's channel and bank mapping**: `K4n8`
runs slower than all-fresh, so the L3 alone cannot be the whole of it. A stride ladder tests both: NB 4 and 8 against 5 and
7, with KB 4-8, at 39-59 MB, the host printing the pools' device addresses.
[§ Corrections, C1, C2](#corrections-after-verification-tue-3-nov-2026).

## The stops, and their test on live samples

The session's stops: `abs_stop_c` 80 °C on one sample, `board_cap_w` **60 W** on three in a row (Q139's rule for aifoundry2: at most 85 W), the admission limit 82 W at the estimate (no cell's estimate above 39.8 W: nothing duty-cycled or dropped). Before the session the queue ran **both stops on live samples**: **stoptest-board** (`board_cap_w` 30 W; one 6 s burst of `K4n8` fp32 zeros over a 22 W rest) tripped **62 ms after the third live sampler line over 30 W, while the work launch ran, and the launch ended 250 ms after the trip**; **stoptest-die** (`abs_stop_c` 30 °C) tripped **60 ms after the first live line, before any launch**. Both ended with exit 4 and passed the queue's registered check (`aifoundry2/queue.jsonl` `stoptest_detail`, `stoptest_check`; `posthoc.txt` §7).

## Device commands sent

*Q136's rule ("take more care for writing commands"), kept in Q137-Q139: the classified list is [`E158.md`](../../../../tools/claims-v3/e158/E158.md) "Device commands sent", frozen in `2cfc4525`, from et-platform `836a4ab` (aifoundry2's BL2 0.22.0), checked by Q136(w)'s `dmcmd_audit.py` before the claim ([`logs/dmcmd-audit.txt`](../../../../tools/claims-v3/e158/logs/dmcmd-audit.txt): 19 send sites, every one READ, GO; one reviewed exception, the residency read run_e119.py rewrites to raw states 1-3, which this `ettelem` refuses before it opens the device). **E158 sent no WRITE.** Counted from the session's records (`posthoc.txt` §7): 12,368 sampler samples (each `GET_MODULE_POWER`, `GET_SP_STATS`, `GET_MODULE_CURRENT_TEMPERATURE`, `GET_ASIC_VOLTAGE`, `GET_MODULE_VOLTAGE`, `GET_ASIC_FREQUENCIES`: all READ; 11 PMIC voltage-register reads each, the owner's allowed read-only PMIC voltage reads of 2 November 2026); an `ettelem config` (three RAM getters, the ASIC voltage and PLL reads) after each of the 103 recorded runs, at each session's start and end and in the queue's two snapshots; `ettelem sptrace` (an MMIO copy, nothing sent to the SP) after each run; no statistics reset, no firmware-revisions query, no residency read, no set. `sparsity_host` (rgm136) opens the ops node only: the kernel load, the DMA of the tiles and C and the launches, no management command.*

## Safety

The session's highest board reading was 36.1 W (`K2n8` fp32, pass 3), 23.9 W under the 60 W stop; the die mean's highest was 51 °C, 29 °C under the 80 °C stop. The hottest-sensor field read 70 °C at every sample from the smoke's idle rest on: the SP's running maximum carried from before the session, as E146 saw (69 °C), not a live reading. Neither stop fired in the session. The smoke's rest reading (30 s, idle card): 21.70 W, die 45.0 °C.

## Departures and notes

- **"Without C's traffic" is the C-light family**, as registered: the large-GEMM kernel stores every C block to its own place, so no rung has none; the families put C at 37-45%, 16-27% and 11-19% of the distance.
- **Zeros only**, as registered (the kind does not move time per op: E146 R7). The power readings are zeros'.
- **ISO's flat extrapolation.** ISO is flat past its last rung (58 MB), so it gave `F6`'s 16 first-touch A lines an op at 77 MB an r of 0.17. With r = 0 past the ladder, `F6` reads −0.74% / −0.87% / −2.10%: still inside 3% (post hoc, `posthoc.txt` §3).
- **R3's pass and R2's verdict together.** R3 passes as registered; the reading that it is a pooled curve's, not a law's, is post hoc (§2, §3) and changes no verdict.
- **MAB's prices stay frozen.** `K4n8`'s share below zero says those prices (solved from `c16` and E136's `g4k`) do not carry every DRAM-bound structure. That is a limit of the inference, recorded as R1's INCONSISTENT.
- **One session, three passes.** The unit of replication is the pass, and every share repeated within 0.017. No interval is between sessions; `F6`, `D2`, `D4` and `L4` repeat E146's session of 2 November within 0.31%.
- **The registration's stated time** is "about 05:00 PST"; `2cfc4525` was committed at 04:37:54 and pushed by 04:38, before the claim (04:38) and the queue's first card touch (04:39:07).

## What E158 says about the page and the model

- **Section 11 item 1 narrows again:** a large GEMM's time per op past the L3 depends on the L3's retention, which is about half of a returning B panel from 39 to 59 MB but collapses for B panels of 4-6 blocks at a power-of-two stride, and moves little with C's share of the distance (0.48 against 0.55). A curve by reuse distance predicts the never-run `F6` to under 1% (R3 PASS), but as a pooled average: the open part is the L3's set mapping (the pools' device addresses and the L3's hash), the KB = 1 shapes' A lines, the vendor's binary and a second card.
- **For the power model (Q139):** the time term's error on the fresh shape, 9-10% → 0.3-0.8% (registered); on E146's ladder out of sample 7.2% → 6.0% (KB ≥ 2); and, post hoc, a zeros GEMM's energy per op follows its time per op (+54% held to slowest).

*(Dated note, Tue 3 Nov 2026, after verification, C1-C4.)* Read these two bullets with the corrections. "Collapses for B
panels of 4-6 blocks at a power-of-two stride": in two single-row-block rungs; `F6`, the same layout with three row blocks,
kept 0.33. "Moves little with C's share (0.48 against 0.55)": that 0.07 is KB 2 against KB 4-6, C's share confounded; post
hoc, off the two collapses one curve fits at w 0.8-1.0 (rms 0.026), so C's lines occupy the L3. "The never-run `F6`": never
fitted (E146's). "The open part is the L3's set mapping": a block-stride term (the L3's or the DRAM's mapping). For the power
model, the time term on new shapes is E146's ladder out of sample, 7.2% → 6.0% (KB ≥ 2; 10.9% → 10.6% on all 24), and `D2`
and `D4` 13.1% → 6.3%; `F6`'s registered 0.3-0.8% stands beside them as a pooled curve's pass that `K4n8` carries. The "+54%
held to slowest" is the whole board's energy per op step (over idle +48%, over the 800 MHz base −38%).
[§ Corrections](#corrections-after-verification-tue-3-nov-2026).

**For the post, in short sentences.** Each names its card and clock.
- On aifoundry2 at 800 MHz, a large matrix multiply whose blocks of B come back before 32 MB of other data have gone by finds every one of them still in the chip's 32 MB L3 (`results.json` `rules.shares`).
- Past 39 MB, about half of each returning block is still there, out to 59 MB, a little less (48% against 55%) when the traffic in between is mostly the result than when it is mostly the inputs (`posthoc.txt` §2).
- But when a block of B is laid out as four to six pieces at a power-of-two stride, 18% or less of it survives, and the multiply runs 15-29% slower per step than its neighbour in the ladder with one column block more or fewer, though that neighbour's B travels further or less far (`K6n4` against `K6n5`, `K4n8` against `K4n7`; `posthoc.txt` §1).
- A curve of retention against distance, fitted on 22 shapes, predicted a never-run 3,072 × 2,048 × 3,072 multiply to within 0.8% in every number format, where the model with a sharp 32 MB cutoff was 9-10% slow (`rules.R3`). That works because the curve averages over the layouts, not because retention follows distance (`rules.R2`, `posthoc.txt` §3).

*(Dated note, Tue 3 Nov 2026, after verification, C1-C4: the post's sentences as corrected; use these in place of the second,
third and fourth above.)*
- Past 39 MB, about half of each returning block is still there, out to 59 MB. It is a little less (48% against 55%) in the shapes that write their result every 64 steps than in those that write it every 128 or 192. Those are also the shapes whose traffic in between is mostly the result, so this design cannot tell the two apart (`corrections.txt` C4).
- Leaving out the two shapes that collapse, the other 20 fall on one curve when the result's traffic is counted like the inputs': the result's lines take the L3 too (post hoc, `corrections.txt` C4).
- In two shapes with one row of blocks, laid out as four or eight column blocks (a power-of-two stride), 18% or less of a returning block survived, and the multiply ran 15-29% slower per step than the next shape in its family (in one pair, the next shape's blocks travel further). One of the two ran 6.5% slower than if every returning block came from DRAM, so part of the cost is outside the L3. A shape with the same layout and three rows of blocks kept 33% (post hoc, `corrections.txt` C2).
- A curve of retention against distance, fitted on 22 shapes, predicted a 3,072 × 2,048 × 3,072 multiply it had never seen (run the day before, in E146) to within 0.8% in every number format, where the model with a sharp 32 MB cutoff was 9-10% slow. That pass rests on one shape: without it the curve misses by 6-8%. On the ladder of shapes run the day before, the curve's error is 6.0% against the sharp cutoff's 7.2% (`rules.R3`, `rules.R4`, `corrections.txt` C1).
- For a zeros GEMM the whole board's energy per multiply step rises 54% from the L3-held shapes to the slowest (48% over the idle card), but the energy above the 800 MHz base falls 38%, because the slower shapes draw a little less power (`corrections.txt` C3).

## Files

`results.json`, `reduce.txt` (`tools/claims-v3/e158/reduce_e158.py`, the registered reduction: per-run metrics, T and X per shape and format, the shares, ISO and LOGI, the rules, the errors per model, the safety record); `posthoc_e158.py`, `posthoc.txt`, `posthoc.json` (labelled, post hoc: the shares with their structure, the plateau and the collapses, `F6` under other readings, E146's ladder cell by cell, the zeros' power and energy per op, cycles per op at the measured clock, card time and commands, the stop tests, the rest reading); `aifoundry2/` (the queue's `queue.jsonl`, `status.json`, `admission.json`, `idle_logins.jsonl` (counts only), `snapshot-*.json`, `config-*.txt`, `sensors-*.json`, `history-before.jsonl`; `smoke/`, `stoptest-board/`, `stoptest-die/` and `s1/`: `runs.jsonl`, `marks.jsonl`, `launches.jsonl.gz`, `tel/*.jsonl.gz`, `sp/`, `session.json`, `e158.json`, `manifest.txt`, `queries.jsonl`, `run.log`, `end.json`; `smoke.out`, `stoptest-*.out`, `s1.out`); `logs/` (the queue's output and start script). The registration, the desk model and the code: [`tools/claims-v3/e158/`](../../../../tools/claims-v3/e158/README.md).

*(Dated note, Tue 3 Nov 2026, after verification.)* [`corrections_e158.py`](corrections_e158.py), [`corrections.txt`](corrections.txt)
and [`corrections.json`](corrections.json): the numbers of the corrections below, from the committed files, with the frozen
model and scorer imported unchanged (post hoc).

## Corrections after verification (Tue 3 Nov 2026)

*Desk only, about 05:40-05:55 PST: no card, no device command, nothing re-run. An independent verifier re-ran
`reduce_e158.py` on the committed data (0 differences in `reduce.txt` and `results.json`) and `posthoc_e158.py`
(byte-identical). It re-classified every command from et-platform `836a4ab` (all READ, no WRITE; `dmcmd_audit.py` GO),
checked the code on the box against `2cfc4525`, and checked the stops on live samples. It found the registered verdicts
sound: R0 PASS, R1 INCONSISTENT and SOFT, R2 NO SINGLE CURVE, R3 PASS ×3, R4 NOT BETTER, R5 10 of 14, R6 holds in every pass.
Its faults are in what the text draws from them. Every number below is printed by [`corrections_e158.py`](corrections_e158.py)
([`corrections.txt`](corrections.txt), [`corrections.json`](corrections.json)) from committed files, with the registered scorer
imported unchanged and run on subsets chosen after the data, so all of it is post hoc. No measured, frozen or registered number
or verdict changes.*

**C1 (major): `F6` was run before; R3's pass rests on one rung; the figure for a new shape is the out-of-sample one.**
- `F6` (`gemmL3x4x6`) is E146's fresh shape: new in E146 ("never run" in [E146's README](../2026-11-02-e146-gemm-stores/README.md)), it ran there on 2 November, T800 1.9121 / 1.9064 / 1.9240 µs (fp32 / fp16 / int8), far-B share 0.327. E158's registration gives that share as the reason for this ladder ("Why"). So here `F6` is **never fitted** (no curve saw it), not never run. The text above said "never-run" at "What E158 does to predicting power and heat" and in the post's fourth sentence.
- R3 passes as registered (+0.41 / +0.26 / −0.76%), and at every w of ISO's near-best interval, 0.3-1.0 (worst 1.64%). But **refitted without `K4n8`, ISO misses `F6` by +8.0 / +7.9 / +5.9%; without `K6n4` and `K4n8`, by +10.3 / +10.3 / +7.8%**: FAILs of the 3% rule. (Without `K6n4` alone it passes, +1.5 / +1.3 / +0.1%.) Half of `F6`'s 64 far B lines an op sit at 54 MB, where ISO's r is 0.171, the pool of `K4n8`'s −0.199 and `K6n6`'s 0.540; at 42-48 MB its 0.443 pools `K6n4`'s 0.181 with plateau rungs.
- **What carries to a new shape** is ISO out of sample: on E146's committed ladder (another session), **7.2% → 6.0% rms** on the 18 KB ≥ 2 cells (R4 NOT BETTER by its 2-point bar) and 10.9% → 10.6% on all 24; on `D2` and `D4` here, **13.1% → 6.3%**. ISO's single misses on the power-of-two-stride panels are `D4` +8.5-8.7% and `D8` +11.8-11.9% (out of sample), and `K4n8` +12.4-13.3% and `K6n4` +10.0% (rungs it was fitted on). LOGI reads E146's ladder at 4.5% and 8.5%, and `D2`/`D4` at 5.9%.

**C2 (major): the collapse is two rungs' reading, and part of it lies outside the L3.**
- The only MB = 1 rungs past 38 MB with NB 4 or 8 and KB ≥ 4 are `K6n4` and `K4n8`, each with one row of blocks. The two shapes with more row blocks and the same layouts disagree: `F6` (NB 4, KB 6, three row blocks) kept **0.329**, while `D4` (NB 8, KB 4, four row blocks) read −0.071. So "a B panel of four to six blocks at a power-of-two stride keeps 18% or less" is not a law. It is what two single-row-block rungs did (post hoc).
- `K4n8`'s −0.199 is not a retention fraction. Its T800, 2.125 µs, is **6.5% above MAB's price with every far line fresh** (1.996 µs; `D4` 2.106 against 2.060, +2.2%). A retention curve cannot carry that (R1 INCONSISTENT), and neither can an L3 set-mapping term alone. Part of the time lies outside the L3: a DRAM-side mapping at a power-of-two stride, or conflicts with A's lines, which MAB prices as L3 hits.
- **The next term is a block-stride term: the L3's set mapping or the DRAM's channel and bank mapping.** A stride ladder with the pools' device addresses logged would test it.

**C3 (minor): the +54% is the whole board's energy per op step.** p800 × T800 includes the board's base, which zeros' power barely clears. From the 10 L3-held fp32 cells (T800 < 1.40 µs) to the slowest (`D4`, `K4n8`):
- whole board, **46.8 → 72.2 µJ (+54%)**;
- over the idle rest (21.70 W), **17.8 → 26.3 µJ (+48%)**;
- over E119's 800 MHz base (33.61 W), **1.84 → 1.13 µJ (−38%)**, because the slower shapes draw 34.1 W against 34.5-35.4.

The lab compares switching power over idle, so +54% is never quoted alone as an energy-per-op change.

**C4 (minor): C's occupancy, and the plateau's 0.07.**
- Post hoc, the 20 rungs off the two collapses fall on one ISO curve: **w 0.9 (tied and near-best 0.8-1.0), rms 0.026** in share, under R2's 0.06 bar, against 0.147 at w = 0. By R2's registered words that reads **C OCCUPIES THE L3**: C's lines take the L3 like the operands'. LOGI on the same 20 gives w 1.0 at rms 0.121. The registered R2 on all 22 stays NO SINGLE CURVE.
- On the plateau the C-heavy rungs hold 0.477 and the others 0.547. **Every C-heavy rung is KB 2, and every other plateau rung is KB 4 or 6**: the family sets both C's share and how often C is stored. So the 0.07 is KB 2 against KB 4-6, with C's share confounded, not a C-occupancy effect.

**C5 (minor): records and wording.**
- 23 rungs ran; `K6n1` has no far B lines, so 22 have a share. Of the 98 bursts, 69 are the ladder in fp32 (23 rungs, three passes), 15 are E146's `F6`, `D2` and `D4` again, and 14 are the K4 rungs in fp16 and int8.
- The end-of-run check: at 05:00:27 PST `et-who` on aifoundry2 read "No process holds an ET-SoC-1 device node or card lock.", and no `queue_e158`, `run_e158`, `sparsity_host` or `ettelem` process remained. It was printed in the lane's session and not saved to a file; it is quoted here from that session's log. The verifier's read-only check at 05:34:40 PST also found no E158 process.
- The release edit ran 05:00:27-05:00:52 PST; the lane's release record gave the claim's start, 04:38:25, as the release's. This directory's data commit, `f8272c64`, was made at 05:08:27 PST and reached origin at 05:08:34.
