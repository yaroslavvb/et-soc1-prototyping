# E136: a large GEMM on the ET-SoC-1, predicted first, under aifoundry2's own governor

*On the kinds page, [section 11, what is still open](https://spacesheep.dev/@yaroslavvb/horace-kinds-of-numbers#11-what-is-still-open): **item 1, "Where a large GEMM falls"**: "Still open: a large GEMM itself, which needs its own reuse per L2-sized block and its footprint, C included". Q137's first lane, on the owner's words of 2 November 2026: the goal is to predict the power and heat of numeric work as accurately as possible. So every number here is set beside the number frozen for it before the run.*

*Mon 2 Nov 2026 (week 45), Q137. Pre-registered in `61e5232f` ([`tools/claims-v3/e136/E136.md`](../../../../tools/claims-v3/e136/E136.md): the binary's source, the desk reuse model, frozen numbers in `predictions-e136.json`, rules R0-R8, the scorer, a self-test, a toy-card dry run and the device-command audit), pushed before the claim (15:49:47 PST) and the first card touch (15:50:22 PST). **aifoundry2 card 0 under its own governor**: `ettelem config` read 65 W / 65 °C (low_power, 600 MHz, 519 mV) at the queue's start and end and after every run; nothing was set, no statistics reset, no firmware-revisions query, no residency read, **no WRITE command of any kind** ([Device commands sent](#device-commands-sent)). The card post was the day's single post in #community-lab, message `1566837317765963987`, rewritten at 15:49:47 PST to add "using aifoundry2 for 1 h, until ~16:55 PST" and at 16:15:06 PST to drop that clause, the other cards' clauses kept word for word. **23.7 card-minutes** (15:50:22 to 16:14:05 PST): the smoke (1.0 min) and one session (22.7 min), all 32 planned runs, none refused, none cut; the cap never bound. No other user was logged in at any of 250 checks.*

## The answer

**A real large GEMM in the vendor's pattern, 4,096 × 4,096 × 4,096 in fp32 (192 MB with C), ran 7.2% faster than frozen (2.173 against 2.341 µs an op at 800 MHz) and gained more from the clock (×1.089 for ×1.333, against ×1.056 frozen); its board power came in 2.3-5.1 W under the frozen numbers, and the governor never held it back: random fp32 sustained 800 MHz at 57.5 W, so zeros and random ran at the same speed (×0.995 sustained, ×1.000 in a burst).** The GEMM the L3 holds (2,048 × 1,024 × 1,024, 20 MB) ran 10.7% faster than frozen, drew 62-70 W in a burst with random-like data, and the governor held random fp32 to 656 MHz sustained, so there **zeros led random by ×1.090 sustained**, the gap the frozen G1 footing predicted to 0.011 (×1.079). Numbers from `results.json` (`per_gemm`, `cells`, `rules`, `errors`), re-derived by independent code in [`rederive.txt`](rederive.txt).

**How well the frozen model predicted, out of sample** (measured − predicted; `results.json` `errors`):

| quantity | cells | rms error | mean error | verdict |
|---|---|---|---|---|
| time per op at 800 MHz, `g4k` (fp32, fp16; int8) | 3 | −7.2%, −7.3%; −12.5% | faster than frozen | R1 point FAIL ×3; placement A HELD (h 1.44, 1.44), int8 OUTSIDE (h 1.83) |
| time per op at 800 MHz, `g2k` | 3 | −10.7% to −12.8% | faster | R2 FAIL ×3 |
| burst board power at 800 MHz (first second) | 20 | **3.37 W** | −2.27 W | R3 15 PASS / 5 FAIL (band 4 W); all 20 under the admission estimate |
| sustained board power, G1 (registered) / G2 | 12 | 4.12 / **2.28 W** | +1.87 / −1.31 W | — |
| sustained clock, G1 / G2 | 12 | 35.7 / **25.9 MHz** | — | R4: 8 / 11 of 12 within 30 MHz; **G2 predicts better** |
| burst rate | 20 | 11.5% | faster | R8 FAIL (the time error) |
| sustained rate, G1 / G2 | 12 | 10.5% / 9.7% | faster | R8 FAIL |
| die, burst maximum | 20 | **0.82 °C** | −0.30 °C | R6 PASS ×20 |
| die, sustained window mean, G1 / G2 | 12 | 3.35 / **1.60 °C** | — | R6 (G1): 7 PASS / 5 FAIL; on G2 every cell inside 3 °C |
| zeros ÷ kind, burst; sustained | 14; 9 | — | — | R5 PASS ×14 and ×9 |
| the kind changes T at 800 MHz | 14 | worst 0.42% | — | R7 PASS |

- **Power and heat predicted well; time per op did not.** The heat law (E111's and E133's 0.67 °C per board W, its shape fitted on E119 and E126) predicted every burst's die maximum to 0.8 °C rms and, given G2's power, every sustained window to 1.6 °C. The board power came within 3.4 W rms in bursts. The time per op, which the frozen law built from what a missing line costs in E119's arms, was 7-13% slow, so every rate was 10-12% low.
- **G2 beats G1.** E101's sustained cap (49.75 W, G1) put random fp32 on `g4k` at 718 MHz and 49.7 W; it ran at 800 MHz and 57.5 W. G2, the cap refitted on E126's five held runs this morning, put it at 800 MHz and 57.5 W. The governor's sustained point on this card is better predicted from the latest session than from E101's relation (R4).
- **`g2k` fp32 random is the one cell the governor held**, and the one where neither footing got the clock: 656 MHz measured, 627 (G1) and 739 (G2) frozen; its sustained board power read 55.2 W against 49.9 and 62.1. Its die held at 65.7 °C, the trip.

| GEMM, format | T at 800 MHz, µs: measured (frozen P1) | X measured (frozen) | burst rate, measured (frozen) | random: burst W, measured (frozen P800) | random sustained: MHz, W, die °C (G1; G2 frozen MHz) | zeros ÷ random, sustained (frozen G1) |
|---|---|---|---|---|---|---|
| `g4k` fp32 | **2.173** (2.341) | 1.089 (1.056) | 3.86 TFLOPS (3.58) | 52.5 (57.5) | 800.0, 57.5, 63.3 (718; 800) | ×0.995 (×1.019) |
| `g4k` fp16 | **2.175** (2.345) | 1.087 (1.054) | 7.73 TFLOPS (7.16) | 52.0 (55.0) | 791.3, 55.2, 63.3 (742; 800) | ×1.008 (×1.013) |
| `g4k` int8 | **2.175** (2.486) | 1.087 (1.077) | 15.47 TOPS (13.50) | 42.0 (44.7) | 790.6, 42.9, 58.1 (800; 800) | ×1.006 (×1.000) |
| `g2k` fp32 | **1.326** (1.486) | 1.137 (1.095) | 6.30 TFLOPS (5.65) | 62.4 (68.1) | 656.3, 55.2, 65.7 (627; 739) | **×1.090** (×1.079) |
| `g2k` fp16 | **1.323** (1.488) | 1.144, fit (1.093) | 12.64 TFLOPS (11.27) | 67.0 (63.5) | not run sustained | — |
| `g2k` int8 | **1.405** (1.612) | 1.146, fit (1.112) | 23.89 TOPS (20.82) | 46.1 (46.0) | not run sustained | — |

T = wall ÷ ops per minion over the launches whose kernel clock read at or above 790 MHz, every kind pooled (`g4k` 478-641 launches a format, sd 0.004-0.005 µs; `rederive.txt`). Every check of C against the host's own reference over the whole K was exact (zeros) or approx (the rest), in the smoke and in every run (R0 PASS).

**The kinds on the large GEMM** (`cells`): sparse50 drew between zeros and random as frozen (`g4k` fp32 burst 42.1 W against 46.5 frozen; fp16 46.3 against 49.0; int8 40.4 against 42.7); the real kind (E101's four GPT-2, BERT and ViT tiles) drew random's power in fp32 and fp16 (52.4 and 52.3 W, random 52.5 and 52.0) and less in int8 (40.6 against full's 42.0), as E95's ratios said. None changed the speed: at 800 MHz every kind's T is within 0.42% of zeros' (R7).

**So for the blog's kinds table, on aifoundry2 under its own governor: in a real large GEMM that streams to DRAM, the kind of number changes the power (zeros 33.6 W, sparse 42.1, random and real 52.4-52.5 at 800 MHz in fp32 bursts) and the die (57.3 against 63.3 °C sustained), and not the speed: the memory path holds the GEMM to 3.86 TFLOPS, too slow for random's power to reach the governor's limit. Horace He's effect appears only where the operands sit close to the cores: in the L3-held GEMM random fp32 sustained 9% slower than zeros.**

## Registered against what happened

32 runs in one session, none refused by the admission rule, none cut by the cap.

| rule | registered | measured | verdict |
|---|---|---|---|
| R0 the ties | every check of C exact or approx; smoke cycles within 50-250% of P1's | all exact or approx; smoke 1,734-1,740 cycles an op at 800 MHz for `g4k` (P1 1,873-1,989), 984 for `g2k` int8 (1,289) | **PASS** |
| R1 where `g4k` falls | h between P2 (A fresh) and P1 (A held); point within 5% of P1 | h 1.439 / 1.444 / 1.834; T800 −7.2% / −7.3% / −12.5% | **A HELD** (fp32, fp16), **OUTSIDE** (int8); **point FAIL ×3** |
| R2 `g2k` | T800 within 5%, X within 0.03 | −10.7% / −11.1% / −12.8%; X +0.041 / +0.051 / +0.034 | **FAIL ×3** |
| R3 burst power | within 4 W of P(800); at or below estimate + 1 W | 15 of 20 within (fails: `g4k` fp32 zeros −4.85, randn −5.01, sparse50 −4.42, real −5.07; `g2k` fp32 randn −5.76); 20 of 20 under the estimate | **15 PASS, 5 FAIL**; estimate holds |
| R4 sustained clock | within 30 MHz, G1 and G2 | G1 8 of 12 (rms 35.7), G2 11 of 12 (rms 25.9) | **G2 better** |
| R5 the gap | burst within 0.03, sustained within 0.05 of G1 | 14 of 14, 9 of 9 | **PASS** |
| R6 the die | within 3 °C | bursts 20 of 20; sustained (G1) 7 of 12 | **bursts PASS; sustained 5 FAIL** (all on random-like data: G1 under-predicted their power) |
| R7 the kind | T800 within 1% of zeros' | worst 0.42% | **PASS** |
| R8 the rates | burst within 5%, sustained within 7% | rms 11.5% and 10.5%, all faster | **FAIL** |

**The failed predictions have one cause and one secondary one.** (1) The frozen speed law priced a missing line from E119's arms, each of which stores a C tile after every 32 ops; the large GEMM stores one after every 256 (`g4k`) or 64 (`g2k`). E126 found that C's traffic costs mostly minion cycles. *Post hoc* ([`posthoc.txt`](posthoc.txt) §1), the same law with the fresh lines priced at E126's `c16s` (16 fresh blocks, C shared) predicts `g4k` fp32 and fp16 to −1.5% and −1.4%, int8 to −7.1%; it changes nothing for `g2k`, whose lines are all L3 lines priced at `c8s` (already C shared), and `g2k` stays 11-13% faster than any arm says. (2) The power and clock errors on random-like data follow the time error (a faster op is a higher rate) and G1's low sustained cap.

## Device commands sent

*Q136's rule ("take more care for writing commands"), kept in Q137: the classified list is [`E136.md`](../../../../tools/claims-v3/e136/E136.md) "Device commands sent", frozen in `61e5232f`, from et-platform `836a4ab` (aifoundry2's BL2 0.22.0) and checked by Q136(w)'s `dmcmd_audit.py` before the claim ([`logs/dmcmd-audit.txt`](../../../../tools/claims-v3/e136/logs/dmcmd-audit.txt): 19 send sites, every one READ, GO; one reviewed exception, the residency read run_e119.py rewrites to raw states 1-3, which this `ettelem` refuses before it opens the device). **E136 sent no WRITE.** Counted from the session's records ([`posthoc.txt`](posthoc.txt) §3): 14,165 sampler samples (each `GET_MODULE_POWER`, `GET_SP_STATS`, `GET_MODULE_CURRENT_TEMPERATURE`, `GET_ASIC_VOLTAGE`, `GET_MODULE_VOLTAGE`, `GET_ASIC_FREQUENCIES`: all READ; 11 PMIC voltage-register reads each, the owner's allowed read-only PMIC voltage reads of 2 November 2026), an `ettelem config` (three RAM getters and the ASIC voltage read) after each of the 37 runs, at each session's start and end and in the queue's two snapshots; `ettelem sptrace` (an MMIO copy, nothing sent to the SP) after each run; no statistics reset, no firmware-revisions query, no set. `sparsity_host` (rgm136) opens the ops node only: the kernel load, the DMA of the tiles and C and the launches, no management command.*

## Safety

The session's highest board reading was 76.09 W (`g2k` fp32 random, sustained), 16.9 W under the session's 93 W stop and 20.9 W under E101's registered 97 W; the die mean's highest reading was 66 °C, 14 °C under the 80 °C stop. The hottest sensor read 69 °C at the smoke's first rest sample, before any load, and never higher: a running maximum carried from before the session (E126's C5), so this session's hottest sensor read at most 69 °C. Neither stop fired; no reading reached the 93 W lock. The smoke's rest reading (30 s, idle card): 22.02 W, die 46.0 °C (`posthoc.txt` §2), against E126's 21.3 W and 43 °C this morning.

## Departures and notes

- **The build.** rgm136 was built on aifoundry2 (`cmake`, `nice -n 10`, `-j2`, card idle, about a minute) at 15:37 PST, before the registration; its sources on the box were byte-identical to the committed ones when the queue started (27 files' sha256, checked at 15:48 PST), and the runner's preflight checked the three binaries' sha256 before the session. A short build on a lab host is a departure from the "no heavy compute on aifoundry2/3" rule only in kind: nobody held the card.
- **No sys_emu run of the new kernel.** Its correctness rests on the host's check of C over the whole K on silicon, in the smoke and in every run (exact or approx in all 36 work runs).
- **Two frozen inputs were the same session's predecessors.** G2 and the heat law's two shape constants were fitted on E119's and E126's committed cells before this run: they are out of sample for these GEMMs, not for this card.
- **The window definitions.** The registered reducer's burst clock and power start at its first 800 MHz second; `rederive_e136.py` averages the whole work window, first 600 MHz launch included, so its burst clocks read 770-794 MHz where the reducer reads 782-800. The two agree on every T and X to the fourth decimal, and on the sustained clocks within 2.6 MHz and power within 0.93 W (the sustained window's edges differ by a sample or two).
- **One run per cell, one session.** No interval here is between sessions; the T intervals are over launches inside one session.

## What E136 says about the page and the model

- **Section 11 item 1 narrows:** "a large GEMM itself" is measured on aifoundry2: its reuse per L2-sized block (none: every line of the 4,096³ GEMM misses the L2, 176 of 192 in the 20 MB one, by E105's L2 model), its footprint with C (192 MB and 20 MB), and its speed, power, clock and die in three formats and four kinds. Still open: the vendor's own binary, and a second card or session.
- **For the power model (Q137):** the energy-per-op interpolation by line class and E119's power rule predicted a never-fitted GEMM's burst board power to 3.4 W rms (over-reading by 2.3 W on average); the heat term predicted its die to 0.8 °C (bursts) and 1.6 °C (sustained, on G2's power). The time term needs C's store frequency as a variable: with the fresh lines priced at C shared, the DRAM-streaming GEMM's time error falls from −7.2% to −1.5% in fp32 (post hoc); the L3-held GEMM's −11% has no explanation yet.
- **For the governor:** the sustained clock is predicted better by a cap refitted on the latest session (G2, 25.9 MHz rms) than by E101's relation (G1, 35.7 MHz).
- **For section 3, speed:** a real large GEMM that streams from DRAM shows no zeros-against-random speed gap on this card (×0.995-1.011 sustained); the L3-held one shows ×1.090 in fp32.

**For the post, in short sentences.** Each names its card and clock.
- On aifoundry2, a real 4,096 × 4,096 × 4,096 fp32 matrix multiply ran at 3.86 TFLOPS at 800 MHz, about a third of what the same cores do with their data in their own caches (`per_gemm`).
- Multiplying zeros, random numbers, half-zero numbers or real model weights made no difference to its speed: the memory path, not the governor, set the pace (`rules.R7`, `rules.R5`).
- The numbers still changed the power: 33.6 W for zeros, 42.1 W half zeros, 52.5 W random, in the first second at 800 MHz (`rules.R3`).
- In a smaller multiply whose data fits in the chip's 32 MB L3, random numbers drew enough power that the governor slowed them to 656 MHz, and zeros ran 9% faster (`cells`, `gaps`).
- Predicted before the run, the board power came within about 3 W and the chip temperature within 1-2 °C; the speed came out 7-13% faster than predicted (`errors`).

## Corrections after verification

*None yet.* A re-derivation of the headline by independent code is in [`rederive.txt`](rederive.txt).

## Files

`results.json`, `reduce.txt` (`tools/claims-v3/e136/reduce_e136.py`, the registered reduction: per-run metrics, T and X per GEMM and format, the rules, the errors, the safety record); `rederive_e136.py`, `rederive.txt`, `rederive.json` (the headline re-derived from the raw records with independent code, post hoc); `posthoc_e136.py`, `posthoc.txt`, `posthoc.json` (the speed law on E126's c16s footing, the rest reading, card time and commands, post hoc); `aifoundry2/` (the queue's `queue.jsonl`, `status.json`, `admission.json`, `idle_logins.jsonl` (counts only), `snapshot-*.json`, `config-*.txt`, `sensors-*.json`, `history-before.jsonl`; `smoke/` and `s1/`: `runs.jsonl`, `marks.jsonl`, `launches.jsonl.gz`, `tel/*.jsonl.gz`, `sp/`, `session.json`, `e136.json`, `manifest.txt`, `queries.jsonl`, `run.log`; `smoke.out`, `s1.out`); `logs/` (the queue's output and start script). The registration, the binary's source and the desk model: [`tools/claims-v3/e136/`](../../../../tools/claims-v3/e136/README.md).
