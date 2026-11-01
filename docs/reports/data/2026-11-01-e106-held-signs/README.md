# E106: a random sign's ~5 W split on one card (aifoundry1 card 1, 600 MHz)

*Sun 1 Nov 2026 (week 44), Q132. Pre-registered in `94bd6f2d` (committed 08:46:19 PST, before the claim and the first launch): [`tools/claims-v3/kinds/E106.md`](../../../../tools/claims-v3/kinds/E106.md), frozen numbers in `predictions-e106.json`, tiles and every expected accumulator in `e106/e106.json`; the scorer `score_e106.py` and its self-test (21 of 21) were in the same commit. aifoundry1 card 1 at 600 MHz, 498.8 mV. TDP 65 W / threshold 65 °C / 600 MHz / 499 mV read under the card lock at the session's start (08:47:08) and end (09:09:17), never set. Nothing was written to the card, and no `--reset-ms` was sent. Claim 1566493797209219173 in #community-lab, posted 08:47:05 PST, released 09:09 PST by an edit of the same post, read back as `<ai> Claude says: using aifoundry1 card 1 for 0.5 h, until ~09:16 PST doc — released (edited)`. Not yet checked by an independent verifier.*

**The complaint this answers:** the line [E104's README](../2026-11-01-e104-c-readback/README.md) left on item 2 of the kinds page, from its verifier: the split of a random sign's ~5 W was an estimate by subtraction across two cards, and fp16 had no held tile with both operands' signs moving.

**What ran.** First the read-back: 40 launches of exactly n ops, n = 2, 1,000, 199,874, 541,999, on 10 tiles, with E104's read-back host. Then, for power: `signs` and `ones` in both formats, the two sides of the step, beside held tiles with both operands' signs moving: fp32's `s_abs` (absorbed products) over `c_abs`; fp16's `z_ss` (zero products, both `eff_sub` flipping independently, as in `signs`) over `c_abs`, and `x_s` (products that cancel, the two `eff_sub` in opposite phase) over `x_c`. E78's runner and reduction ran unchanged (sha256-checked), in E82's frame on this card: E78's six anchors three times a pass, the `anchor_pi` tie first and last. Three passes ran (10610–10612), 90 runs, no run failed or was skipped, and E78's gates kept all three, so t = 4.30. Every interval is 95% over passes, paired within a pass. Numbers are the board's unless marked rail.

## Results

**In plain words.** On one card, in one session, with every accumulator read back: random ±1 costs 4.79 W more than all +1 in fp32 and 4.72 W more in fp16. With both operands' signs still moving and the sum read back as held, 2.67 W of it remains in fp32 (0.56) and 2.09 W in fp16 (0.45). The rest, 2.12 W and 2.63 W, by subtraction, goes with the sums moving. **So about half of a random sign's ~5 W is there with the sum held, in each format, on designed tiles.** fp16's held part depends on the design: when its two aligned operands flip in opposite phase on products that cancel, it is only 0.89 W (0.19), as the bench said it would be. E92's carry across cards holds: the steps land at 0.98 of the carried values. The bench's model, frozen before the run, predicted all ten tiles to 0.076 W rms.

**1. The split, one card, one session.** (`scored.json` › `contrasts`, `shares`; `posthoc-check.txt` A, B.)

| W, board (rail beside) | fp32 | fp16 | M4 before the data, fp32 / fp16 |
|---|---:|---:|---:|
| **the step, `signs` − `ones`** | **4.792 ± 0.421** (rail 4.401 ± 0.561) | **4.716 ± 1.118** (rail 3.954 ± 0.255) | 4.80 / 4.85 |
| **held, both operands' signs moving, the nearer twin:** fp32 `s_abs` − `c_abs`; fp16 `z_ss` − `c_abs` | **2.668 ± 0.210** (rail 2.036 ± 1.179) | **2.091 ± 0.442** (rail 1.787 ± 0.442) | 2.62 / 2.22 |
| **its share of the step, per pass** | **0.557 ± 0.074** (rail 0.461 ± 0.223): R3 ABOUT HALF | **0.445 ± 0.113** (rail 0.452 ± 0.100): R4 ABOUT HALF | 0.546 / 0.458 |
| **the rest, by subtraction, paired** | **2.124 ± 0.509** (rail 2.365 ± 0.806) | **2.625 ± 1.058** (rail 2.167 ± 0.366) | 2.18 / 2.63 |
| held, the second design: fp16 `x_s` − `x_c` | | 0.887 ± 0.369 (rail 0.758 ± 0.441) | / 1.09 |
| its share | | 0.187 ± 0.040 (rail 0.192 ± 0.109): R5 LITTLE | / 0.224 |

fp16's interval on the step is wide because pass 10610 reads 4.199 W against 5.018 and 4.931 W; the rail, which the board meter's dips do not touch, reads 3.904, 3.885 and 4.072 W. The per-pass shares are 0.591, 0.534, 0.547 in fp32 and 0.477, 0.393, 0.465 in fp16.

**2. The formats' shares are close, and not shown equal (R6 INCONCLUSIVE).** fp16's `z_ss` share less fp32's `s_abs` share is −0.112 ± 0.073 on the board: its interval excludes 0 and is not inside ±0.15. On the rail it is −0.009 ± 0.123. fp32's held tile has absorbed products and fp16's zero ones, so an absorbed fp32 subtraction also swings the adder's output (E104), which `z_ss` does not.

**3. What depends on the design (R5 LITTLE).** `z_ss` and `x_s` both hold, both move both operands' signs, and have nearly the same sign flips (A 1,760 and 1,984, B 3,802 and 3,480 an op, against `signs`' 2,032 and 4,050). They differ in the adder: `z_ss`'s two `eff_sub` flip independently (2,030 and 1,828 an op, against `signs`' 2,070 and 2,026), and `x_s`'s together in opposite phase. M4 said 0.46 and 0.22 before the data; the card says 0.45 and 0.19. So the held part is not one number in fp16: **0.45 on the design whose adder behaves as `signs`' does, 0.19 on the one whose two aligned operands partly undo each other.** I take `z_ss` as the nearer twin, and that is a judgement, registered before the data. Its B words at k ≥ 1 are `signs`' own; its A words are zeros, not ±1, so its aligned operands are empty. `s_abs` in fp32 is a different draw from `signs`.

**4. A's signs add nothing measurable to the held part.** E104's `z_s` (the same B, A's signs still) over `c_abs` read 2.153 ± 0.330 W; `z_ss` here 2.091 ± 0.442 W (`posthoc-check.txt` D). Across sessions, same card.

**5. The carry across cards holds (R2 PASS).** E92's aifoundry3 steps × 0.9722 said 4.877 and 4.827 W; here 4.792 and 4.716 W, 0.98 of them. fp32's `s_abs` − `c_abs` here 2.668 ± 0.210 W; E88 on this card 2.524 ± 0.185 W; E92 carried 2.450 W. E104's 0.45 and its bracket stand, and this replaces them with one card's numbers.

**6. Every sum held, read back (R1 PASS).** 40 of 40 reads, all 1,024 minions on one value, equal the frozen words. On these 10 tiles the three readings coincide, so this does not re-test E104's question: a miss would have meant a tile is not what it is called. `x_s` and `x_c` read 16 n, 4b0452f0 at n = 541,999, one word; `z_ss` and `c_abs` read n × 2^31, 588452f0, one word; `s_abs` and fp32's `c_abs` read n × 2^100, 7b0452f0, one word. `signs` reads 15 words in fp16 and 11 in fp32, exact integers.

**7. The bench's model held (R7 PASS).** rms(D − M4) = 0.076 W over 10 tiles, bias 0.008 W, worst `fp32.c_abs` −0.11 W, all 10 inside their frozen intervals; every contrast inside M4's interval. These tiles are simpler than E103's or E104's. **The session tied (S1 PASS):** against E82 with dips removed, `fp32.randn` −0.13 W, `fp16.randn` +0.01 W, `anchor_pi` 0.00 W, `int8.full` −0.05 W; 600 MHz, 498.8 mV, 546.001 cycles per op; tie drift under 0.16 W a pass.

**Modelled, not measured** (`posthoc-check.txt` G, H). By E92's price list the sign bits themselves are about 0.55 W in fp32 and 0.29 W in fp16, inside the held part. "The rest goes with the sums moving" is a reading, and it is not one mechanism: the alternation's price falls on moving sums (E104), so part of the rest may be the adder alternating at that lower price. With E104's moving premiums at `signs`' rate that part would be about 1.1 W in fp32 and 1.8 W in fp16 (the fp16/fp32 ratio there, R6 of E104, is unresolved), leaving about 3.2 and 2.7 W. These figures are not additive with the held column: the held part and this reading price the same alternations at different prices.

## What the page may now say

**§5.4,** replacing in E104's text the sentences from "Of the ~5 W random-sign step" through "goes with the sums moving":

> On one card in one session (E106; aifoundry1 card 1, 600 MHz, three passes, designed tiles, C read back), random ±1 costs 4.79 ± 0.42 W more than all +1 in fp32 and 4.72 ± 1.12 W in fp16. With both operands' signs still moving and the sum read back as held, 2.67 ± 0.21 W remains in fp32, on absorbed products (0.56 ± 0.07 of the step), and 2.09 ± 0.44 W in fp16, on zero products (0.45 ± 0.11). The rest, 2.12 ± 0.51 W and 2.63 ± 1.06 W by subtraction, goes with the sums moving, and part of it may be the adder alternating at its lower price on moving sums. The held part depends on the design: in fp16, with products that cancel and the two aligned operands flipping in opposite phase, it is 0.89 ± 0.37 W (0.19 ± 0.04). The formats' shares differ by −0.11 ± 0.07 on the board and −0.01 ± 0.12 on the rail: close, not shown equal.

The rest of E104's §5.4 text stands. **May not say,** beyond E104's list: "half and half" without the design; fp16's 0.45 as the only held value; "the same split in both formats"; the rest as "the result bus" or "the result path"; the split of a ±1 tile's own sums as measured, because the held tiles are twins of `signs`, not `signs`; anything about other cards.

**Item 2 closes, on its question, with one thing left beside it.** Its guess is tested: the adder alternating is a real cost, in both formats, with C read back (E92, E104). Where the ~5 W goes is now measured on one card in each format: about half with the sum held, the rest by subtraction with the sums moving. fp16 has held tiles with both operands' signs moving, and they show the held part depends on the design. What stays open is not this item's question: **the moving-sum ratio, E104-R6, 1.56 ± 2.73**, which I would carry as one line under item 6. This is my reading, and no verifier has checked E106.

## Registered against what happened

| rule | what | registered | happened | primary | arms that move |
|---|---|---|---|---|---|
| E106-R1 | every tile, every length, every word | all equal | 40 of 40 | **PASS** | read-back has no arm |
| E106-R2 | the step against E92's × 0.9722 | both within ±1 W | 4.792 and 4.716 W | **PASS** | none |
| E106-R3 | fp32's held share | inside [0.35, 0.65]: ABOUT HALF | 0.557 ± 0.074 | **ABOUT HALF** | INCONCLUSIVE: dips kept (a pass set aside, 0.569 ± 0.276), leak 0 (0.573 ± 0.639) |
| E106-R4 | fp16's held share, `z_ss` | inside [0.30, 0.70]: ABOUT HALF | 0.445 ± 0.113 | **ABOUT HALF** | INCONCLUSIVE: leak 0 (0.431 ± 0.643) |
| E106-R5 | fp16's held share, `x_s` | the same bands | 0.187 ± 0.040 | **LITTLE** | INCONCLUSIVE: dips kept (0.188 ± 0.206) |
| E106-R6 | fp16's share less fp32's | inside ±0.15: ALIKE; outside: DIFFER | −0.112 ± 0.073 | **INCONCLUSIVE** | ALIKE: leak 0 (−0.142 ± 0.004, two passes) |
| E106-R7 | M4's rms over the float tiles | PASS ≤ 0.60 W, FAIL > 1.00 W | 0.076 W, n = 10 | **PASS** | none |
| E106-S1 | the session tie | E94's bands | every cell inside | **PASS** | FAIL at leak 0.3803, 0.545 and 0: those arms correct D by another slope than E82's values carry, as in E92 and E104 |

**What I expected, frozen:** R1 PASS, R2 PASS, R3 ABOUT HALF, R4 ABOUT HALF near 0.46, R5 LITTLE or INCONCLUSIVE near 0.22, R6 ALIKE or INCONCLUSIVE, R7 PASS, S1 PASS. All came out so. Because the bench predicted this much so closely, the rules were not hard to pass: R2's ±1 W is wide against 0.1 W misses.

**Departures and disclosures.**
1. **Three passes ran, not the registered four.** Passes took 305–329 s against the 290 s estimated, so the registered budget rule stopped before 10613 (992 s elapsed + 329 s > 1,250 s). That is about 18 card-minutes, near the 15 asked for. No pass was set aside, so it cost nothing in t.
2. The card sat idle under the claim only for seconds between stages. The queue ended 09:05:20 and the claim was released at 09:09.
3. `score_e106.py` was run on the read-back alone before any pass was read, to report the lane's status.
4. The generator, the bench and the collection ran on the mini, not on the card's host.
5. The runner's log lines read "E78 pass … tiles verified against kinds.json": `run_e78.py`'s unchanged strings.

## Caveats

Three passes, one card, one clock, designed tiles. All three held tiles are twins of `signs`, not `signs`: their sums are n × a seed, and `signs`' moving sums are small exact integers. `z_ss`'s A words are zeros from three of the four sign patterns, because (+0, +0) would close the gate, and its products and aligned operands are zero. fp32's `s_abs` differs from `signs` in its draws and has absorbed products, which also swing the adder's output. So R3 and R4 are not like for like, which R6's reading respects. The board's step in fp16 carries one low pass; the rail's does not. The watts are the board's; the rail figures are about 0.8–0.9 of them.

## Files

`e106.json` (the registered reduction: every item, per pass), `runs.csv`, `reduce.txt`, the arms (`e106-dipskept`, `e106-gatesoff`, `e106-auto`, `e106-leak0.1994 / 0.3803 / 0.545 / 0`, `.json`, `.csv` beside them, `reduce-*.txt`, `reduce-*.log`), `scored.json` and `results.md` (every rule, read, contrast, share and tile), `score.log`, `code.sha256`, `logs/` (the queue, read-back, smoke and dry-run logs, the session's start and end config reads, the binaries' sha256), `aifoundry1-c1/kinds/` (the three passes, `kinds-smoke-p10601`, and `readback-p10602` with `readback.jsonl`), `desk/` (the desk check on the fixed bench, `desk-e106.txt`, `.json`; the bench's counts, `counts-e106.json`), `posthoc-check.py` / `.txt` (labelled post hoc: every number above beyond `scored.json`, standard library only). The tiles and the registration are in `tools/claims-v3/kinds/` (`E106.md`, `predictions-e106.json`, `make_predictions_e106.py`, `make_e106.py`, `e106/`, `readback_e106.py`, `block_readback_e106.sh`, `e106_common.py`, `run_e106.py`, `block_e106.sh`, `queue_e106.sh`, `run_e106.sh`, `reduce_e106.py`, `score_e106.py`, `collect_e106.sh`, `selftest_e106.py`).
