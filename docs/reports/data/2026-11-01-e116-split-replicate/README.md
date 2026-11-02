# E116 — E88's split on a second card, with C read back once per design (Q133, aifoundry3 card 0, 2026-11-01)

*It answers the final critic's item 8, "Replicates for the new sections" ("E88's split itself … not re-run"), which the [Horace hub](https://spacesheep.dev/@yaroslavvb/horace-hub)'s Status fold keeps under "What Q132 did to the two lists it set out from". That item is not a numbered item of the kinds page's [section 11, what is still open](https://spacesheep.dev/@yaroslavvb/horace-kinds-of-numbers#11-what-is-still-open) as of `1fe8377a18af`. On that list it bears on **item 5**, "Where a random sign's ~5 W goes" (E88's held fp32 sign, `s_abs`, on a second card, with C read back), and on **item 6**, "A power model across kinds", only through E88's own model: E88's frozen bands scored unscaled on a second card. That is not section 9's M4, so it does not narrow item 6's "a new card without a scale" (result 5). It also answers two limits in the page's section 5.3: "All of this is one card" and "int8's were not read". Corrected after verification the same evening: see [Corrections after verification](#corrections-after-verification-sun-1-nov-2026).*

*Sun 1 Nov 2026 (week 44), Q133. Pre-registered in **`8bac6da5`** (committed 16:49:57 PST, pushed by 16:50:01):
[`tools/claims-v3/e116/README.md`](../../../../tools/claims-v3/e116/README.md), with frozen numbers in
`predictions-e116.json`, accum.c's words for every tile in `expect-e116.json`, and the scorer `score_e116.py` with its
self-test, all in the same commit. The claim went up 77 s later in `#community-lab` (16:51:17 PST, message
`1566615650871541861`, "using aifoundry3 for 1 h, until ~17:55 PST"). **Card session 16:51:29–17:23:54 PST on
aifoundry3 card 0, 32.4 card-minutes of the 40 allowed:** the read-back 11602 (16:51:29–16:51:40), the smoke 11601
(to 16:52:21), five passes 11610–11614 (16:52:21–17:23:44), and the closing read. Amendment A1 (`3f832bd6`, 17:00:58,
before any power data were read) would have added a pass if the queue had fitted only four; it fitted five, so A1 did
nothing. `ettelem config`, read only under the card lock with `timeout 10`, read TDP 0 W, threshold 65 °C, 600 MHz,
523 mV and max_power at the session's start and end. No knob was written, no `--reset-ms` was sent, and there was no
reset and no PMIC command. **Released at 17:24 PST** by editing the same post, which reads back as
`<ai> Claude says: using aifoundry3 for 1 h, until ~17:55 PST doc — released (edited)`.*

> **What this is.** E88's 22 tiles, byte for byte, ran on a second card with E88's harness unchanged: thirteen designs
> that freeze a multiply-add's result while its operands move, or walk it with the same operands, beside each format's
> zeros, random data and ones. They split board switching power into **(i) the lane being clocked**, **(iii) the
> operand-side multiplier** and **(ii) the result path**. Before the power passes, the card's accumulators were read
> back once per tile, after exactly 199,874 ops, every word of all 1,024 minions, and compared with the RTL's arithmetic.
> The random operands are E88's designed ones, not E78's random tiles: fp32's are positive, and fp16's and int8's come
> in cancelling pairs.

## Results

**In plain words.** The split repeats on a second card. In fp32 and fp16 each part's share moves by at most one point
from card 1's, and in int8 by at most two (E116-S PASS in all three formats). The watts land inside the registered
bands around E88's watts times E82's card scale (E116-W PASS in all three), though the parts' own card ratios run from
0.98 to 1.09 (result 7). Every one of the 22 reads equals the RTL's arithmetic on every word of every
minion (E116-R0 PASS). That includes int8's frozen designs, which nobody had read before: both hold 0. E88's 32
registered verdicts repeat except one: the sign pair's walking half lands at 2.13 ± 0.15 W against its "at least 2 W"
rule, so it reads INCONCLUSIVE where card 1 read PASS. By the registered count that makes E116-H INCONCLUSIVE, and my
frozen guess that P-R32s would pass here was wrong. **Four kept passes, the registered minimum** (pass 11610 set aside
by E78's zero-anchor gate). int8's split rests on three of them, because E78's launch rule skipped `int8.r_walk` once,
so int8's S and W verdicts rest on three passes: the scorer counts kept passes, as registered.

**1. The read-back: every read equals accum.c (E116-R0 PASS, 22 of 22).** E104's one-flag host (`--dump-c`, built
on aifoundry3 into `build/e116/`, with the same kernel ELF) ran one launch per tile of exactly n = 199,874 ops. The
launches ran at 546.001–546.002 and 318.001–318.002 cycles per op and 0.598–0.599 GHz, took 0.34–0.42 s each, and all
22 took 8.7 s. In every read all 1,024 minions held one C, equal to `expect-e116.json`'s 256 words, which were frozen
before the claim. ([`scored.json`](scored.json) › `E116-R0`, [`results.md`](results.md), raw
`aifoundry3/rpath/rpath-readback-p11602/readback.jsonl`, [`posthoc.txt`](posthoc.txt).)

| what the card holds at n = 199,874 | tiles | C[0][0] / C[0][8] | distinct words |
|---|---|---|---|
| **n × 2¹⁰⁰ on every word: nothing but the first slice's product ever entered the sum** | `fp32.c_abs`, `r_abs`, `s_abs` | 7a433080 / 7a433080 | 1 |
| frozen per accumulator, the accumulators differ | `fp32.r_het` | 7a532d3f / 7a4eaad2 | 16 |
| **0: each micro-op's dot product cancels** | `fp16.c_cancel`, `r_cancel`; **`int8.c_cancel`, `r_cancel` (first read)** | 00000000 | 1 |
| walks one unit a micro-op in one word (E104's finding, now on a second card) | `fp16.r_abs` | 57aaebf1 / 57aaebf1 | 1 |
| walks, as designed | `fp32.r_walk`, `s_walk`; `fp16.r_walk`; `int8.r_walk` (int32, wrapped) | e.g. int8 9b2784bc / 625987de | 256, 11, 256, 256 |
| the anchors | zeros (0), ones, `randn`, `int8.full` | | 1 or 256 |

**Seven tiles hold the same words on both cards.** E104 read seven of these tiles at the same n on aifoundry1 card 1:
fp32 `c_abs`, `r_abs` and `s_abs`, and fp16 `c_cancel`, `r_cancel`, `r_abs` and `r_walk`. Its reads equalled accum.c,
and so do these. The arithmetic is digital, so this was expected. What it settles is narrower: which E88 designs freeze
and which walk is now read off a second card, int8 included, and no longer rests on the desk emulation alone.

**2. The split on aifoundry3** (board switching power over each format's zeros, paired within each kept pass, 95%
intervals, t(0.975, 3) = 3.182; int8 t(0.975, 2) = 4.303 over its three complete passes; pJ per MAC through each pass's
measured rate, `scored-e88rules.json` › `primary.splits`):

| random-operand design, result walking | (i) the lane clocked | (iii) operand-side multiplier | (ii) the result path | total |
|---|---|---|---|---|
| **fp32** (`r_walk`, positive operands) | **8.386 ± 0.116 W**, 0.377 ± 0.004 · 1.83 pJ/MAC | **8.855 ± 0.112 W**, 0.398 ± 0.006 · 1.93 pJ/MAC | **5.032 ± 0.147 W**, 0.226 ± 0.006 · 1.10 pJ/MAC | 22.273 ± 0.129 W |
| card 1 (E88) | 7.92 ± 0.18 W, 0.367 | 8.61 ± 0.18 W, 0.399 | 5.04 ± 0.19 W, 0.234 | 21.58 W |
| **fp16** (`r_walk`, cancelling pairs) | **8.376 ± 0.065 W**, 0.394 ± 0.003 · 0.91 pJ/MAC | **6.361 ± 0.145 W**, 0.299 ± 0.009 · 0.69 pJ/MAC | **6.508 ± 0.242 W**, 0.306 ± 0.009 · 0.71 pJ/MAC | 21.244 ± 0.154 W |
| card 1 (E88) | 7.96 ± 0.14 W, 0.389 | 6.19 ± 0.17 W, 0.303 | 6.29 ± 0.21 W, 0.308 | 20.43 W |
| **int8** (`r_walk`, cancelling pairs; 3 passes) | **1.685 ± 0.334 W**, 0.239 ± 0.045 · 0.053 pJ/MAC | **3.397 ± 0.287 W**, 0.482 ± 0.053 · 0.108 pJ/MAC | **1.964 ± 0.326 W**, 0.279 ± 0.039 · 0.062 pJ/MAC | 7.046 ± 0.212 W |
| card 1 (E88) | 1.71 ± 0.13 W, 0.257 | 3.14 ± 0.21 W, 0.472 | 1.81 ± 0.26 W, 0.271 | 6.66 W |

(i) = D(`c_abs` or `c_cancel`); (iii) = D(`r_abs` or `r_cancel`) − (i); (ii) = D(`r_walk`) − D(the same operands
frozen); E88's definitions, through `score_e116.py` (it reproduces E88's card-1 split exactly from E88's own reduction:
`tools/claims-v3/e116/selftest_e116.txt`). int8's parts need all three tiles in a pass, so they use 11611–11613.
`score_e88.py` pairs each contrast on its own and keeps four passes for F8 and M8: 1.678 ± 0.176 and 3.402 ± 0.151 W.

**3. The registered rules** ([`scored.json`](scored.json) › `power`; bands frozen in `predictions-e116.json`):

| rule | registered | happened | verdict |
|---|---|---|---|
| **E116-S** fp32 | every share within ±0.04 of card 1's | +0.010, −0.001, −0.008 | **PASS** |
| **E116-S** fp16 | ±0.04 | +0.005, −0.004, −0.002 | **PASS** |
| **E116-S** int8 | ±0.08 | −0.018, +0.010, +0.008 | **PASS** |
| **E116-W** fp32 | each part within max(0.6 W, 12%) of E88 × 1.030 (8.160, 8.873, 5.193 W) | +0.226, −0.018, −0.161 W | **PASS** |
| **E116-W** fp16 | of E88 × 1.033 (8.219, 6.396, 6.497 W) | +0.157, −0.035, +0.011 W | **PASS** |
| **E116-W** int8 | of E88 × 1.027 (1.757, 3.230, 1.858 W) | −0.072, +0.167, +0.106 W | **PASS** |
| **E116-H** | E88's 13 mechanism verdicts repeat | 12 of 13; H4-signs-result INCONCLUSIVE (R32s 2.134 ± 0.153 W against ≥ 2.0; card 1 2.259 ± 0.158, PASS) | **INCONCLUSIVE** |
| **E116-P** (reported) | E88's 19 frozen bands, unscaled | 17 of 19, the same 17 as card 1; P-M32s and P-R32s fail | 17 of 19 |
| **E116-T** | `fp32.randn`, `fp16.randn`, `int8.full` within max(0.4 W, 3%) of E78 here | 24.744 ± 0.098 vs 24.725; 22.149 ± 0.085 vs 22.162; 7.160 ± 0.062 vs 7.056 W | **PASS** |
| **E116-R0** | 22 reads equal accum.c | 22 of 22, all 1,024 minions | **PASS** |

All 32 of E88's rules, by `score_e88.py` unchanged ([`results-e88rules.md`](results-e88rules.md)): 28 PASS, 3 FAIL
(H4-signs-mult, P-M32s, P-R32s), 1 INCONCLUSIVE (H4-signs-result). Card 1 had 29 PASS and 3 FAIL. The mechanism
rules on this card: the constants' walks cost 0.026 ± 0.020 W (fp32), 0.018 ± 0.072 W (fp16) and −0.104 ± 0.113 W
(int8), H1 PASS in all three. The result path is 5.03 / 6.51 / 1.96 W, H2 PASS. The bus-swing share of fp32's result
path is **0.773 ± 0.025** (card 1 0.754 ± 0.018), H5 PASS, on the raw ratio as registered, without E88's C2 correction
for `r_het`'s own operand toggles. fp16's absorbed design is 0.410 ± 0.133 W above its cancelled one (card 1
0.388 ± 0.111), H6 PASS.

**4. The held fp32 sign repeats on aifoundry3, with C read back (item 5).** `s_abs` − `c_abs` (M32s) is
**2.627 ± 0.218 W**, and `s_abs` reads n × 2¹⁰⁰ on every word, as `c_abs` does (result 1): the sum grows by the first
slice's 2¹⁰⁰ each op, and the signs never change it. That makes five readings on two cards, 2.38–2.67 W, within 0.3 W
of each other: on card 1, E88 2.524 ± 0.185, E106 2.67 ± 0.21 and E108 2.480 ± 0.320
([E108](../2026-11-01-e108-sign-located/README.md), `fp32.held_abs`); on aifoundry3, E92 2.377 ± 0.556 (2.520 ± 0.171
with dips removed; [E92](../2026-11-01-e92-sign-split/README.md)) and E116 here. The walking half, `s_walk` − `s_abs`
(R32s), is 2.134 ± 0.153 W, against card 1's 2.259 ± 0.158 (E88) and 2.235 ± 0.169 (E108, `fp32.rest`): 0.94–0.96 of
card 1's. The sum is 4.76 W (card 1 4.78). ([`corrections-check.txt`](corrections-check.txt) C2.)

**5. E88's own model on a second card, unscaled (not section 9's M4: item 6 is not narrowed).** E88's stream model
with a result-path term was fitted on card 1's E82 before E88 existed. It is not the kinds page's M4, whose constants
were fitted on this card's E78 and which [E95](../2026-11-01-e95-real-tensors-energy/README.md) has already scored here
without a scale. Here E88's model puts the same 17 of 19 contrasts inside its registered bands of ±0.75 to ±1.80 W
(±1.09 to ±1.80 W in fp32 and fp16), with no card scale. Those bands are too wide to test a card scale: E82's 3% moves
any of its predictions by at most 0.29 W (M32), under a quarter of a band's half-width. It misses the same pair: M32s
(0.24 W predicted, 2.63 measured) and R32s (band low edge 2.262 W, measured 2.134). Inside the bands it misses where it
missed on card 1 (E88's C3), by similar fractions: R32bus 3.89 W against 4.75 predicted (−18%), M32 8.86 against 9.72
(−9%), R16 6.51 against 7.36 (−12%), R16abs 6.10 against 7.23 (−16%), R8 1.96 against 3.07 (−36%), and M8 3.40 against
2.12 (+60%) (`scored-e88rules.json` › `primary.contrasts.*.predicted`; [`corrections-check.txt`](corrections-check.txt)
C1).

**6. As shares of the random anchors** (E88's correction C1, so the shares can be read against E78's random tiles):
fp32 0.339 / 0.358 / 0.203, plus **0.100 ± 0.004** the split does not place (card 1: 0.333 / 0.362 / 0.212 + 0.094 ±
0.007). E78's random fp32 costs 2.471 ± 0.113 W more than the positive design (X32; card 1 2.241 ± 0.173). fp16:
0.378 / 0.287 / 0.294 + 0.041 ± 0.004 (card 1 0.373 / 0.291 / 0.295 + 0.041). int8: 0.235 / 0.474 / 0.274 + 0.017 ±
0.035 (card 1 0.251 / 0.461 / 0.265 + 0.023).

**7. The rail, the scale, and pass health (post hoc, labelled, [`posthoc.txt`](posthoc.txt)).**
- **On the minion rail** (`Drail`) the shares are fp32 0.397 / 0.387 / 0.216 of 17.91 W (card 1's rail 0.387 / 0.396 /
  0.217), fp16 0.414 / 0.299 / 0.287 of 17.07 W (0.400 / 0.307 / 0.293), and int8 0.255 / 0.475 / 0.269 of 5.89 W
  (0.245 / 0.473 / 0.282). On the rail, aifoundry3's shares are within 1.4 points of card 1's rail shares. Rail and
  board shares differ by up to 2.1 points on either card (2.09 here, 1.99 on card 1;
  [`corrections-check.txt`](corrections-check.txt) C4).
- **The observed scale, E116 over E88:** the `r_walk` totals are 1.032 / 1.040 / 1.057 and the random anchors 1.039 /
  1.040 / 1.050, against E82's 1.030 / 1.033 / 1.027; int8's total sits about twice as far above 1 as E82's scale. The
  parts do not all scale alike: they run from 0.985 (int8's clocked lane) to 1.086 (int8's result path). The clocked
  lane is 1.059 and 1.053 in fp32 and fp16, while fp32's result path is 0.998. That is why fp32's shares move a point
  between (i) and (ii). No registered test separates the parts' scales, and the shares stay inside their bands
  ([`corrections-check.txt`](corrections-check.txt) C5).
- **Passes:** five ran (177 runs). E78's launch rule skipped three runs because the die had not come back to 58 °C in
  the quiet wait: 11613 `int8.zeros` and `fp32.randn`, and 11614 `int8.r_walk`. Pass 11610 is set aside by E78's
  zero-anchor gate (`int8.zeros` departs −0.316 W from its straight line, against a 0.25 W limit). That leaves 141 runs
  in four passes, at 600 MHz, 521.6 mV and 546.001 / 546.001 / 318.000 cycles per op, with idle at 25.909 ± 0.012 W
  and a fitted leakage slope of 0.197 W/°C (130 runs; card 1's was 0.315). The primary removes 51 launch-gap dip samples
  (E82 A2's definition, E88's registered primary). E78's own aifoundry3 reduction kept them. **A weak baseline in
  11613:** the skipped `int8.zeros` was the first of that pass's three (#9), so int8's zero line there rests on two
  runs, at positions 22 and 30 (0.002 W apart). The zero-anchor gate's straight-line test, the one that set 11610
  aside, needs three runs and could not check it (its range test passed), and the six int8 runs at positions 1–20
  (`c_cancel`, `r_walk`, `r_cancel`, `ones` and two of `full`) are measured against the run at 22, the line held flat
  back in time as `reduce_e78.py` holds it. 11613 carries int8's lowest readings (`c_cancel` 1.530 W against
  1.657–1.777, `ones` 1.358 against 1.636–1.651) and its lowest (i) share, 0.218 against 0.249 and 0.250. int8's S passes with or without it: without 11613 the shares move −0.007, +0.001 and
  +0.006 from card 1's, against ±0.08 ([`corrections-check.txt`](corrections-check.txt) C7).
- **The arms** (`scored.json` › `arms`). The no-leakage arm keeps all five passes, and S, W and T pass there in every
  format. Three arms fall below the registered four passes and are not scored, which is why their kept-pass counts
  differ. Dips kept keeps two: the random-range gate also sets aside 11612 (`fp32.randn` spans 1.659 W) and 11614
  (`fp16.randn` spans 1.043 W). Leakage 0.545 and 0.3803 keep three each: 11614's `int8.zeros` departs from its line.
  Read as exploratory, S and W pass in every format in all three of those arms. T fails at leakage 0.545.

## Registered against what happened

| | registered (`8bac6da5`) | happened |
|---|---|---|
| card, clock | aifoundry3 card 0, 600 MHz by its boot-time TDP 0, nothing set | as registered; TDP 0 W / 65 °C / 600 MHz at both ends, and at both ends of every pass; 523 mV at the session's ends and at every pass start, 522 mV at four of the five pass ends (no pass flagged by the config gate) |
| budget | at most 40 card-minutes, queue at most 34 | 32.4 card-minutes, queue 31.5 |
| read-back | 22 tiles, n = 199,874, against accum.c | 22 of 22 equal (R0 PASS) |
| passes for scoring | at least 4 kept | 4 kept of 5 (11610 set aside by E78's zero-anchor gate); int8's split, and its S and W verdicts, on the three passes that hold all three int8 tiles (11611–11613), because the scorer counts kept passes, as registered |
| reduction | `reduce_e88.py` unchanged, dips removed, leakage auto; E88's four arms | as registered |
| what I expected | R0, S ×3, W ×3, H, T PASS; P 18 of 19 with P-R32s passing | R0, S ×3, W ×3 and T PASS; **H INCONCLUSIVE** (H4-signs-result) and **P 17 of 19: P-R32s fails**, because R32s came in at 0.94× card 1's value, not 1.03× |

**Departures and disclosures.**
- **A1** (`3f832bd6`, written during pass 11611 and committed at 17:00:58 PST, before any power data were read; its header says "~17:02", an estimate about a minute late, and is left as committed). The queue's 34-minute
  rule looked as if it would fit only four of aifoundry3's 409 s passes. A1 added one more pass after the queue, inside
  the 40 card-minutes, but only if fewer than five ended ok. The later passes ran 5.6–6.1 minutes, so the queue fitted a
  fifth (11614) on its own, and A1 logged "five passes already ok: no extra pass" and did nothing. No data came from it.
- **The reducer's fixed strings.** `reduce_e88.py` writes `"experiment": "E88"` into `e116*.json` and names card 1's
  65 W / 65 °C substitution in `reduce*.txt`. Those strings are in its code, which runs unchanged. On aifoundry3 the
  substitution never fires (TDP 0 / 65 °C is reduce_e78.py's own gate).
- **Where code ran.** The read-back host was built on aifoundry3's CPU at 16:41 PST, before the claim, with `nice -n
  10`. The build took 3 s, the card was idle and no device was opened. Everything else on the desk (accum.c's words,
  the reduction, the scoring) ran on my desk machine.
- **No interim look.** During the session I read only the session and queue logs, the smoke gate's line, the
  read-back's log lines, `block.json` files and run counts. Nothing was reduced until the claim was released.
- **The collection ran twice.** The second run used a repo-relative copy of the raw passes, so that no committed file
  carries a desk path. Both runs gave the same numbers. The box's own working-tree path (`/home/…/aifoundry`) stays in
  the raw records and logs, as in earlier runs.
- **Other users.** Other lab users' idle logins on aifoundry3 (since 26 Oct) did not block, under E60's departure D1 as
  `block_e88.sh` carries it. et-who showed no holder at the setup, before the claim, at the session's start and at its
  end. Nobody is named here.

## What this changes

- **For the blog and the kinds page, section 5.3:** "All of this is one card" goes. aifoundry3 repeats the split
  (E116, four passes, int8 on three after one launch-rule skip, board power). Each share is within one point of card
  1's in fp32 and fp16 and within two in int8. The `r_walk` totals are 3–6% higher in watts (E82's card scale is
  2.7–3.3%), and the parts' ratios run from 0.98 to 1.09. "int8's were not read" goes too: aifoundry3's card holds 0 on
  every word of `int8.c_cancel` and `int8.r_cancel`. Every E88 design's C equals the RTL's arithmetic on a second card,
  including fp16's walking `r_abs`. Quote the shares, not the watts: the parts' card ratios differ (0.98–1.09).
- **For the Horace hub and section 11:** the final critic's "E88's split itself not re-run" (its item 8, kept in the
  Horace hub's Status fold) is done. Item 6 is not narrowed: E116 scored E88's own model (not section 9's M4) on a
  second card, unscaled, and found 17 of 19 inside its ±0.75 to ±1.80 W bands, too wide to test a 3% card scale, with
  the same misplacements inside them. Item 5's held fp32 sign has a fifth reading, 2.63 ± 0.22 W on aifoundry3 with C
  read back: five readings on two cards, 2.4–2.7 W (E88, E106 and E108 on card 1; E92 and E116 on aifoundry3). The split
  is still for designed operands: positive in fp32, cancelling pairs in fp16 and int8. About 10% of random fp32 is not
  placed (0.100 here, 0.094 on card 1).
- **For the records:** E116 goes in `03-experiments.md`, with the claim, the registration (`8bac6da5`), A1 (`3f832bd6`)
  and this directory.

## Corrections after verification (Sun 1 Nov 2026)

*The Q133 verifier checked E116 and returned "holds with fixes": eight minor faults and no major one. It reproduced
every registered number and verdict byte for byte from the raw passes. These corrections were made at the desk the same
evening: no card was touched and nothing was re-run. No reduction, score, frozen input or verdict changed (the sha256 of
each output is the check's first section), and the registration is left as frozen.
[`corrections-check.py`](corrections-check.py) prints the numbers below from committed files, and
[`corrections-check.txt`](corrections-check.txt) is its output.*

| | what was wrong | what changed |
|---|---|---|
| C1 | Result 5 and "What this changes" offered E88's bands holding 17 of 19 unscaled as a data point for section 11's item 6, "a new card without a scale". That open case belongs to section 9's M4, a different model. This card is the one M4 was fitted on (E78), and E95 had already scored M4 here without a scale. Result 5 also gave "17 of 19" without the band widths, which E88's C3 puts beside that number. | Result 5 names the model (E88's own, not M4) and says item 6 is not narrowed. It gives the bands (±0.75 to ±1.80 W; ±1.09 to ±1.80 W in fp32 and fp16) and shows that E82's 3% moves any prediction by at most 0.29 W, under a quarter of a half-width. It names the six misses inside the bands as C3 does, with R32bus added. The first line and "What this changes" say the same. The verifier's suggested "±1.25 to 1.80 W" covers 13 of the 19 bands, so the text uses the full range, as E88's C3 and the kinds page do. |
| C2 | Result 4 counted "four readings on two cards" of the held fp32 sign. That left out E108 (card 1, data committed 12:19 PST, before E116's registration): `s_abs` − `c_abs` 2.480 ± 0.320 W, and `s_walk` − `s_abs` 2.235 ± 0.169 W. | Five readings on two cards, 2.38–2.67 W (E88, E106 and E108 on card 1; E92 and E116 on aifoundry3), with E108's 2.235 beside card 1's R32s. aifoundry3's walking half is 0.94–0.96 of card 1's, so that reading stands. |
| C3 | The first line put the final critic's item 8 ("Replicates for the new sections") in the kinds page's section 11 as of `1fe8377a18af`. That section has no replicates item: the critic's thirteen items are kept in the Horace hub's Status fold. E114 made the same misplacement (its C6). | The first line says where item 8 is kept, as E114's corrected line does, and keeps the section-11 link for items 5 and 6. The registration (`8bac6da5`) has the same misplacement in its first line. It is left as frozen (it is hashed in `code.sha256`), and this row corrects it. |
| C4 | Result 7 said "Rail and board shares agree within 1.4 points on both cards". They differ by up to 2.09 points here and 1.99 on card 1. | What stays within 1.4 points (1.39) is aifoundry3's rail shares against card 1's rail shares. Result 7 now says that, and gives the rail–board gap. |
| C5 | "What this changes" said the parts are "about 3–6% higher in watts, near E82's card scale" and that "the parts' card scales differ (1.00–1.09)". The parts run 0.985–1.086. Only the `r_walk` totals are 3–6% higher (1.032, 1.040, 1.057), and int8's 1.057 is about twice as far above 1 as E82's 1.027. | "What this changes" and result 7 now say: the `r_walk` totals are 3–6% higher (E82's card scale is 2.7–3.3%), and the parts' ratios run from 0.98 to 1.09. "In plain words" says the watts land inside the registered bands around E82's scale, not where the scale puts them. |
| C6 | int8's S and W PASS rest on three passes (11611–11613; 11614 has no `int8.r_walk`), because the scorer applies the four-pass minimum to kept passes, as registered. "In plain words" disclosed this, but "What this changes" said "four passes" alone. | "int8 on three after one launch-rule skip" appears wherever four passes are named, and the passes row of "Registered against what happened" says how the scorer counts. The verdicts stay as scored. |
| C7 | Not disclosed: 11613's `int8.zeros` line rests on two runs, because the launch rule skipped the first. E78's straight-line test, which set 11610 aside, therefore could not check it, and int8's runs at positions 1–20 are measured against the run at 22, held flat. 11613 also carries int8's lowest (i) share. | A passage in result 7's "Passes" bullet says so, gives the readings, and shows that int8's S passes with or without 11613. |
| C8 | Wording. Result 4 called the read-back "C read back as held" without saying what it holds. The README said 523 mV at both ends of every pass, but four of the five pass ends read 522 mV. The blog lines handed on with this result said four more things that do not hold. A held sum "provably does not change", but it reads n × 2¹⁰⁰ and grows by 2¹⁰⁰ each op, as `c_abs`'s does. A constant's walk "costs nothing measurable", but 0.026 ± 0.020 W excludes 0. The shares "do not" move, but fp32's (i) moves +0.009 ± 0.004. The session ties with E78 "within 0.10 W", but int8 differs by +0.104 W. | Result 4 says `s_abs` reads n × 2¹⁰⁰ as the constant's does, so the signs never change the sum. "Registered against what happened" says 523 mV at the session's ends and the pass starts and 522 mV at four pass ends. The blog lines now say: "a sum the signs do not change (it reads n × 2¹⁰⁰, as the constant's does)", "a few hundredths of a watt, inside E88's ≤ 1 W rule", "each share moves by at most a point (two in int8)", and "within 0.11 W (1.5%)". |

Also found while correcting: `predictions-e116.json` › `registration` names `tools/claims-v3/e116/E116.md`, but the
registration is that directory's `README.md`. The frozen file is left as committed.

## Files

| file | what |
|---|---|
| `corrections-check.py`, `corrections-check.txt` | the desk check behind "Corrections after verification" (post hoc, standard library; prints every number the corrections quote from committed files) |
| `e116.json`, `runs.csv`, `reduce.txt`, `reduce.log` | the primary reduction (`reduce_e88.py` → `reduce_e78.py`, unchanged; dips removed, leakage auto) |
| `e116-keepdips.json`, `e116-leak0.545.json`, `e116-leak0.3803.json`, `e116-leak0.json` (+ `.csv`, `.txt`, `.log`) | the registered arms |
| `scored.json`, `results.md`, `score.log` | `score_e116.py`: R0, S, W, H, P, T, the splits, the arms |
| `scored-e88rules.json`, `results-e88rules.md`, `score-e88rules.log` | `score_e88.py` unchanged: E88's 32 rules, contrasts and splits on this card |
| `posthoc_e116.py`, `posthoc.txt`, `posthoc.json` | post hoc, labelled: the rail split, the observed card ratios, the read-back launches |
| `aifoundry3/rpath/p11610`–`p11614` | raw passes: telemetry (10 Hz), launch records, marks, tile dumps, config reads, manifests |
| `aifoundry3/rpath/rpath-smoke-p11601`, `rpath-readback-p11602` | the smoke, and the read-back (`readback.jsonl`: per read the SPARSITY record, every distinct C with its minion count and hex) |
| `logs/` | the session, queue, read-back and smoke logs, A1's note, the session's start and end config reads, the dry run, the read-back host's build log |
| `code.sha256` | every file the run and the reduction used |

Code: [`tools/claims-v3/e116/`](../../../../tools/claims-v3/e116/) (the registration, A1, `make_predictions_e116.py`,
`build_host_e116.sh`, `readback_e116.py`, `block_readback_e116.sh`, `setup_e116.sh`, `session_e116.sh`,
`extra_e116.sh`, `score_e116.py`, `selftest_e116.py`, `collect_e116.sh`) and, reused unchanged,
[`tools/claims-v3/rpath/`](../../../../tools/claims-v3/rpath/) (E88), `kinds/run_e78.py`, `kinds/reduce_e78.py`,
`kinds/patch_host_e104.py` and `lib.sh`. Reproduce from the raw passes:
`PY=/usr/bin/python3 bash tools/claims-v3/e116/collect_e116.sh <dir holding rpath/, rpath-smoke/, rpath-readback/, logs/>`.
