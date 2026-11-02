# E123: the dagger rows E94 left, re-drawn on aifoundry3 (aifoundry3 card 0, 600 MHz)

*On the kinds page, [section 11, what is still open](https://spacesheep.dev/@yaroslavvb/horace-kinds-of-numbers#11-what-is-still-open): the entry "Tile-to-tile spread" (old item 11) in its list "Closed, or answered as far as tested", which says the item is "narrowed for the † rows no card ran" and that "fp32 ReLU × small weights stays unresolved as registered". It follows [E94](../2026-11-01-e94-tile-spread/README.md).*

*Sun 1 Nov 2026 (week 44), Q134 (optional lane `a3-e123-tile-spread`). Pre-registered in `8f186695` (committed 21:15:00 PST, on
origin/main by 21:15:12, before the claim and the first launch): [`tools/claims-v3/e123/E123.md`](../../../../tools/claims-v3/e123/E123.md),
frozen numbers in `predictions-e123.json` (sha256 `6ddc39da…`), the scorer `score_e123.py` (sha256 `3174d65b…`) and its self-test
(28 of 28) in the same commit. aifoundry3 card 0 (no `V3_DEVICE`, `/run/lock/etsoc-shire0.lock`); the reduction reads 600 MHz and
521.7 mV mean. TDP 0 W, threshold 65 °C, `max_power`, 600 MHz, 522–523 mV were read under the card lock at the session's start
(21:16:48), at both ends of the smoke and of both passes, and at the session's end (21:41:53): seven reads, never set. Nothing
was written to the card, and no `--reset-ms` or other PMIC command was sent (the stock `ettelem` telemetry's own PMIC register
reads, the owner's open question of section 14, are what every kinds run makes). Claim: the day's post 1566603178164617247 in
#community-lab, rewritten at 21:16:47 PST to add "using aifoundry3 for 1 h, until ~22:20 PST"; released by rewriting it at
21:42:19 (25 min 32 s of card time, inside the 35 allowed).*

*Dated note, Mon 2 Nov 2026 (Q136's records): the open question is answered. The owner's ruling of 2 November 2026 allows
read-only PMIC voltage-register reads, so these reads are allowed ([AGENT.md](../../../../AGENT.md) §5, "Device commands").*

*Corrected after verification, Sun 1 Nov 2026, at the desk, with no card touched and nothing re-run (§ [Corrections after
verification](#corrections-after-verification-sun-1-nov-2026), C1–C7). fp16 50% zeros' NO CORRECTION is now labelled as registered,
on class G's pooled SD: on the rule's own SD it reads UNRESOLVED, and the predicted +0.52 W is not excluded. The gate-share gaps'
predicted offsets, fp16 50% zeros in the page's frame, the spread of the same draws on both cards, what the gate share leaves per
kind and three roundings are corrected. No registered prediction, rule, number or verdict changed (R2: 10 NO CORRECTION, 2
UNRESOLVED, 0 CORRECTION; every other rule as before).*

**What ran.** Thirty-six fresh draws of the eleven † rows no card had re-drawn (seeds `sha256("E123/<type>/<kind>/draw<r>")`,
none rejected), E94's six fresh draws of fp32 "ReLU × small weights" byte for byte as a bridge to card 1, E78's committed tile
of all twelve rules, and E78's six anchors three times a pass: 74 runs a pass, two passes (12310, 12311), E78's runner and
reduction unchanged and sha256-checked. **Both passes were kept; 146 of 146 recorded runs passed every gate.** Two runs of pass
12311 were skipped by the launch rule (the reading did not come back to 58 °C inside the quiet wait), so two tiles have one
pass and, by the registered rule, left their rules (departure 1). The unit of replication is **the draw**. D is a tile's board
power over its own type's zeros; S is over the idle bracket.

## Results

**1. On aifoundry3 itself, ten of the twelve rows need no correction as registered, and two int8 rows stay open; none needs a correction**
(`scored.json` › `primary.rules_of_number`; the registered primary, each draw moved to its rule's mean gate share with the
frozen slope, the SD pooled over the rule's class):

| row (rule) | class | draws | gate share: tile → kind | kind's D ± 95%, W | committed − kind ± 95%, W | R2 | kind's S ± 95%, W | the page's S (E78's tile) | nJ per op, kind | pJ per MAC, kind | E94's form (plain mean) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| fp32 ReLU × small weights (`fp32.nn_like`) | G | 7 | 0.508 → 0.501 | **13.20** ± 0.14 | **−0.13** ± 0.14 | **NO CORRECTION** | 15.19 ± 0.14 | 15.03 ± 0.06 | 13.55 | 3.308 | UNRESOLVED (+0.16 ± 0.75) |
| fp16 50% zeros (`fp16.sparse50`) | G | 5 | 0.414 → 0.437 | **13.23** ± 0.15 | **+0.27** ± 0.15 | **NO CORRECTION** on class G's pooled SD (own SD: UNRESOLVED, result 3) | 15.19 ± 0.15 | 15.22 ± 0.57 | 13.55 | 1.654 | UNRESOLVED (+0.02 ± 0.68) |
| fp16 50% zero words (`fp16.wsparse50`) | G | 4 | 0.760 → 0.749 | **7.26** ± 0.15 | **−0.22** ± 0.16 | **NO CORRECTION** | 9.25 ± 0.16 | 9.09 ± 0.09 | 8.25 | 1.008 | UNRESOLVED (−0.15 ± 1.37) |
| fp32 integers −8…7 (`fp32.smallint`) | LF | 3 | 0.118 → 0.121 | **13.95** ± 0.13 | **+0.13** ± 0.17 | **NO CORRECTION** | 15.85 ± 0.17 | 16.02 ± 0.13 | 14.14 | 3.452 | UNRESOLVED (−0.21 ± 0.98) |
| fp32 90% zeros (`fp32.sparse90`) | LF | 3 | 0.992 → 0.990 | **0.68** ± 0.12 | **−0.13** ± 0.16 | **NO CORRECTION** | 2.61 ± 0.16 | 2.51 ± 0.14 | 2.33 | 0.568 | NO CORRECTION (−0.10 ± 0.39) |
| fp16 90% zeros (`fp16.sparse90`) | LF | 3 | 0.961 → 0.964 | **1.35** ± 0.12 | **+0.05** ± 0.16 | **NO CORRECTION** | 3.27 ± 0.16 | 3.38 ± 0.09 | 2.92 | 0.356 | NO CORRECTION (−0.01 ± 0.37) |
| fp16 90% zero words (`fp16.wsparse90`) | LF | 3 | 0.990 → 0.990 | **0.67** ± 0.12 | **+0.02** ± 0.16 | **NO CORRECTION** | 2.69 ± 0.16 | 2.64 ± 0.11 | 2.40 | 0.293 | NO CORRECTION (+0.01 ± 0.16) |
| fp16 integers −8…7 (`fp16.smallint`) | LF | 2 | 0.004 → 0.008 | **16.85** ± 0.14 | **+0.19** ± 0.18 | **NO CORRECTION** | 18.87 ± 0.18 | 18.93 ± 0.24 | 16.83 | 2.054 | — (two draws) |
| int8 50% zero words (`int8.wsparse50`) | LI | 3 | 0.644 → 0.624 | **3.26** ± 0.11 | **−0.05** ± 0.16 | **NO CORRECTION** | 5.85 ± 0.16 | 5.74 ± 0.09 | 3.04 | 0.185 | NO CORRECTION (+0.05 ± 0.18) |
| int8 90% zero bytes (`int8.sparse90`) | LI | 3 | 0.822 → 0.807 | **1.30** ± 0.11 | **−0.12** ± 0.16 | **UNRESOLVED** | 3.83 ± 0.16 | 3.76 ± 0.08 | 1.99 | 0.122 | UNRESOLVED (−0.16 ± 0.30) |
| int8 90% zero words (`int8.wsparse90`) | LI | 2 | 0.980 → 0.981 | **0.45** ± 0.13 | **+0.14** ± 0.18 | **UNRESOLVED** | 2.97 ± 0.18 | 3.08 ± 0.07 | 1.54 | 0.094 | — (two draws) |
| int8 ternary −1, 0, 1 (`int8.ternary`) | LI | 2 | 0.008 → 0.013 | **5.12** ± 0.13 | **+0.03** ± 0.18 | **NO CORRECTION** | 7.65 ± 0.18 | 7.73 ± 0.10 | 3.98 | 0.243 | — (two draws) |

The kind's S is this session's committed S less the offset; the page's S and its ± are E78's tile on this card (`predictions-e123.json`
› `rules_of_number.<rule>.e78_a3`, 6 passes). Applying the measured offsets to the page's own cells instead gives the same picture
within 0.25 W (`posthoc_e123.txt` [B]). The two int8 rows that stay open are inside int8's ±0.25 W band by their central values
(−0.12 and +0.14 W) and their intervals reach past it; by the registered statement, their rows print the kind's mean and interval and
make no claim on the tile. E94's own form (the plain mean over draws, the rule's own SD) resolves four of the nine rows with three
or more draws as NO CORRECTION and leaves five UNRESOLVED, with intervals of ±0.16 to ±1.37 W: knowing each draw's gate share is what
resolves the float rows that gate 25–75% of their lanes. One of the ten rests on the class pooling: fp16 50% zeros' adjusted draws
spread 0.22 W, against 0.06 and 0.07 W for the other two rules of class G (Bartlett p 0.011), and on its own SD its offset is
+0.27 ± 0.29 W, UNRESOLVED (result 3; [`corrections-check.txt`](corrections-check.txt) [C1]). On their own SDs, fp32 ReLU, fp16 50%
zero words and the five LF rows stay NO CORRECTION; int8 50% zero words and int8 ternary, with 4.8 and 2.1 df, sit at int8's band,
just past it or just inside it by the t convention (§ Caveats).

**2. fp32 "ReLU × small weights" needs no correction on aifoundry3, the card whose table it is: the committed tile reads
−0.13 ± 0.14 W from its kind's mean, D 13.20 ± 0.14 W, S 15.19 ± 0.14 W** (`E123-R2:fp32.nn_like`). E94 left it UNRESOLVED as
registered (+0.45 ± 0.60 W on card 1, six draws) and read it post hoc as needing no correction (−0.13 ± 0.19 W). On this card, with
the same six draws less one and two new ones, its plain mean is still wide (12.91 ± 0.75 W, UNRESOLVED), and the gate-share
adjusted mean is 13.20 ± 0.14 W. E94's post-hoc law-adjusted mean on card 1, scaled by E82's fp32 card scale (1.0300), is
13.32 ± 0.16 W, 0.12 W from E123's (`posthoc_e123.txt` [C]). Its between-draw SD on this card is 0.81 W [0.52, 1.78] (E94 on card 1:
0.55 W [0.34, 1.36]).

**3. fp16 "50% zeros": as registered, its committed tile reads +0.27 ± 0.15 W from its kind's mean (NO CORRECTION), not the
+0.52 / +0.50 W both laws predicted. That interval rests on class G's pooled SD; on the rule's own SD the offset is +0.27 ± 0.29 W,
UNRESOLVED, with the prediction inside. So the registered verdict does not support the page's predicted note ("S about 14.7 W
against 15.22, at the band"), and on the rule's own SD the note is not excluded** (`E123-R2:fp16.sparse50`, `posthoc_e123.txt` [E],
[`corrections-check.txt`](corrections-check.txt) [C1]). Its draws are the ones the gate share explains least: what the adjustment
leaves of them is 0.22 W (4 df), against 0.06–0.07 W for the other two rules of class G (`scored.json` ›
`primary.rules_of_number.<rule>.rule_s_w`), and the data reject one SD for the class (Bartlett p 0.011, Brown-Forsythe p 0.018; in LF
and LI they do not, Bartlett p 0.14 and 0.41). With its own SD in the scorer's formula (4.4 df, t floored as the scorer's t975) the offset is
+0.27 ± 0.29 W, [−0.03, +0.56] (at the exact fractional df ±0.285, [−0.02, +0.55]): the interval holds both 0 and the frozen +0.517 /
+0.495 W. It reads UNRESOLVED with dips kept as well (result 6). In the page's frame the kind's S is **14.95 ± 0.15 W** (E78's 15.22
less the offset; ±0.29 on the rule's own SD); in this session's frame it is 15.19 ± 0.15 W; its gate share is 0.437 (the tile's
0.414). The two frames differ by 0.24 W here because this session's committed tile read above E78's: S 15.46 against 15.22 W, and
D 0.30 W above (13.50 against 13.20 W; E78's own 95% interval on that tile is ±0.54 W, and S1's band is ±0.50 W), the largest of the
sixteen session-tie cells; on the other eleven rows the frames differ by 0.13 W or less (`corrections-check.txt` [C3]).

**4. The † note, measured on aifoundry3:** float kinds gating 25–75% of their lanes have a between-draw SD of **0.55–0.86 W** here
(fp16 50% zeros 0.55 [0.33, 1.58], fp32 ReLU 0.81 [0.52, 1.78], fp16 50% zero words 0.86 [0.49, 3.22]; pooled **0.75 W [0.54, 1.21]**,
13 df), so about ±1.1–1.7 W at 95% for one tile. E94 read 0.49–0.57 W on card 1's three rows of this class, but only fp32 ReLU is a
rule of both, and the same five draws spread alike on both cards (0.61 W here, 0.58 W on card 1 at E82's scale): the ranges differ by
row and draw, not by card. fp32 ReLU's 0.81 W here comes from its new draw `e123d1` (14.14 W; 0.66 W without it)
([`corrections-check.txt`](corrections-check.txt) [C4]). Each held the gate law's expected SD (R3 PASS three times: 0.87, 0.66 and
0.69 W predicted). **The other float † rows: pooled 0.21 W [0.14, 0.39]** (9 df, R4:LF PASS against 0.50 W).
**The int8 † rows: pooled 0.10 W [0.05, 0.24]** (6 df, R4:LI PASS against 0.25 W). Once each draw is moved to its rule's mean gate
share, what is left between draws is 0.13 W in class G (per kind 0.06 W for fp32 ReLU, 0.22 W for fp16 50% zeros and 0.07 W for fp16
50% zero words), 0.09 W in the other float rows and 0.08 W in int8 (each with the tile's own noise in it), so the gate share carries
most of a float kind's spread, and of fp16 50% zeros' the least (result 3; `posthoc_e123.txt` [D], `corrections-check.txt` [C5]).

**5. The frozen slope, the laws and the bridge hold on this card.** The slope the adjustment leaves in class G is **+0.58 ± 2.54 W
per unit of gate share** (R5 PASS, 16 draws, 12 df): the price of a gated lane is D(random) per unit of gate share here, as E94 read on
card 1 after its data, now as a registered test. The gate law's frozen per-draw deltas land class G's 16 draws to **0.21 W rms**,
against 0.69 W for predicting no move (R6 PASS; 0.08 W in the other float rows, against 0.21 W; 0.08 W in int8, against 0.15 W). E94's
frozen desk table offsets of the eleven rows it did not run miss the measured offsets by **0.11 W rms** (gate law) and **0.12 W rms**
(Q130(n)) (R7 PASS twice); the largest miss of both is fp16 50% zeros (result 3). **E94's draws move alike on both cards:** five of its
fp32 ReLU draws, read on card 1 and here, agree to **0.070 W rms** after E82's card scale, where predicting no move gives 0.751 W (R8
PASS; E94's own R8 on E90's draws read 0.131 W). The session tie is inside its band in all sixteen cells (S1 PASS; largest +0.30 W,
fp16 50% zeros; the random anchors and the pi tie within 0.031 W of E78).

| draw | D(draw) − D(committed), aifoundry3, W | card 1 (E94), W | card 1 × 1.0300, W | difference, W |
|---|---|---|---|---|
| `fp32.nn_like_e94d1` | −1.113 | −1.118 | −1.151 | −0.039 |
| `fp32.nn_like_e94d2` | −0.507 | −0.524 | −0.540 | −0.033 |
| `fp32.nn_like_e94d3` | −0.971 | −0.999 | −1.029 | −0.058 |
| `fp32.nn_like_e94d4` | +0.448 | +0.304 | +0.313 | −0.135 |
| `fp32.nn_like_e94d5` | −0.425 | −0.391 | −0.403 | +0.022 |

**6. The arms widen intervals and never call a correction.** No verdict moves to CORRECTION at any arm (`scored.json` ›
`arm_sensitive`, `posthoc_e123.txt` [A]). With the meter's launch-gap dips kept (21 and 7 samples a pass), the intervals grow two- to
threefold in the float rows (to ±0.33–0.46 W) and 1.4-fold in int8 (to ±0.22–0.25 W), and six rows read UNRESOLVED (fp16 50% zeros,
fp16 50% zero words, fp32 and fp16 integers, int8 50% zero words, int8 ternary); R4:LF reads INCONCLUSIVE. The offsets themselves move
by 0.12 W or less there, except int8 ternary (+0.03 → −0.13 W). At the leakage slopes 0.3803 and 0.545 W/°C, int8 50% zero words and
int8 ternary, and fp32 integers at 0.545, read UNRESOLVED; with no leakage correction int8 90% zero words reads NO CORRECTION; R4:LI
reads INCONCLUSIVE at 0.545 and with no correction. S1 fails at 0.3803, 0.545 and 0, a change of frame against E78's reference at
0.1994, as in E90 and E94. E78's pass gates set no pass aside, so the gates-off arm equals the primary.

## Registered against happened

| rule | registered | happened | verdict |
|---|---|---|---|
| E123-R2 (12) | NO CORRECTION / CORRECTION / UNRESOLVED against ±0.50 W (float), ±0.25 W (int8), the primary estimator | the power table gave NO CORRECTION 0.01 for fp16 50% zeros and 0.06 for int8 50% zero words: both offsets came in smaller than the frozen expectations (+0.27 against +0.52 W; −0.05 against −0.17 W), and the noise was smaller than the 0.10 W the table assumed (class N 0.02–0.05 W); the other ten as their tables' likeliest outcomes or their second | **10 NO CORRECTION, 2 UNRESOLVED** (`int8.sparse90`, `int8.wsparse90`), 0 CORRECTION; `fp16.sparse50`'s NO CORRECTION is on class G's pooled SD (UNRESOLVED on its own SD, C1) |
| E123-R3 (3) | the gate law's expected SD inside the plain τ's 95% interval | 0.87 in [0.52, 1.78]; 0.66 in [0.33, 1.58]; 0.69 in [0.49, 3.22] | **PASS ×3** |
| E123-R4:LF | pooled τ's upper bound ≤ 0.50 W | 0.21 [0.14, 0.39] W | **PASS** |
| E123-R4:LI | pooled τ's upper bound ≤ 0.25 W | 0.10 [0.05, 0.24] W | **PASS** |
| E123-R4:G | reported | 0.75 [0.54, 1.21] W | reported |
| E123-R5 | the slope left in class G contains 0 | +0.58 ± 2.54 W per unit (−1.96, +3.12) | **PASS** (the frozen slope stands) |
| E123-R6 | gate law, class G: rms ≤ 0.30 W and below no-move | 0.21 W, no move 0.69 W | **PASS** |
| E123-R7 (2) | the desk table's offsets: rms ≤ 0.50 W | gate law 0.11 W, Q130(n) 0.12 W | **PASS ×2** |
| E123-R8 | E94's draws on both cards: rms ≤ 0.30 W | 0.070 W (five draws) | **PASS** |
| E123-S1 | sixteen cells within ±0.50 / ±0.25 W of E78 | all inside; largest +0.30 W (`fp16.sparse50`) | **PASS** |
| secondary: E94's form, R1 and R2 (the nine rules with three draws or more) | as E94 | R1: 8 PASS, 1 INCONCLUSIVE (`int8.wsparse50`); R2: 4 NO CORRECTION, 5 UNRESOLVED | secondary |

**Checks:** cycles per op 546.001 / 546.001 / 318.000; duty 0.9957–0.9970; idle consistency median |S − S0 − D| 0.062 W; carry-over
−0.00002 ± 0.0005 W/W; rail lag 1.00 s; tie drift −0.02 and +0.22 W a pass; dip samples removed 21 / 7; every dumped tile equal to
its registered sha256 (the per-run gate); config 0 W / 65 °C / 600 MHz / 522–523 mV at every read (`e123.json` ›
`reducer.config_reads_raw`, `logs/config-session-*.json`, the smoke's `config_start.json` and `config_end.json`). The smoke (pass 12301,
eight 2 s runs) passed its gate before any pass: every run ok on 1,024 minions, cycles per op as above (`logs/smoke.log`).

**Departures from E123.md.**

1. **Two runs were skipped by the launch rule in pass 12311** (`fp32.nn_like_e94d6` at #38 and `fp16.wsparse50_e123d5` at #47: "launch
   reading not reached … skipped", `logs/e123-queue.log`), as E94's pass 9410 skipped one. Each of those two tiles has one pass, so,
   by the registered rule ("a tile missing a kept pass leaves its rule, named"), they left their rules: fp32 ReLU has 7 draws, not 8,
   fp16 50% zero words 4, not 5; class G's pooled SD has 13 df, not 15; R5 has 16 draws (12 df); R8 has five draws, not six. Nothing
   was chosen: the runner's launch rule skipped them.
2. **The first collection named the raw root by its desk path.** It ran over a copy of the raw passes in the lane's scratch, so the
   eight reductions and eight runs CSVs recorded a Mac home path. It was run again, by the same registered collector at `8f186695`,
   over a copy inside the repo's ignored `build/` tree (`build/e123-raw/aifoundry3`), so the recorded directories are repo-relative.
   Every primary and arm number in `scored.json` is identical between the two collections (checked).
3. **The card time was 25.5 minutes,** well inside the registered 35, so the post's "for 1 h, until ~22:20 PST" held the card on
   paper longer than it was used; it was marked released at 21:42:19.

No amendment was made. Before registration, the reducer wrapper was run on two of E78's committed aifoundry3 passes (p7810, p7811) as a
mechanics test (every D equal to E78's own per-pass value; no E123 number existed).

## Interpretation (labelled: not measured by E123)

A float kind with random zeros moves with the draw by about its gate share times D(random): a draw that gates 1% more of its
lane-cycles costs about 1% of random data's power less, on both cards (E94 result 8 post hoc; E123-R5 as a registered test). That is
why its spread is 0.5–0.9 W and why moving each draw to its rule's mean gate share leaves 0.06–0.22 W per kind (0.13 W pooled in class
G): what else a draw changes, its operand bits, costs little beside it (E94 result 9). It is also why the committed tiles of these rows
sit near their kinds' means: E78's tiles gate within 0.000–0.023 of their rules' mean share, which at D(random) per unit predicts
offsets of 0.24 W or less on every row but fp16 50% zeros (fp16 50% zero words −0.24 and fp32 ReLU −0.17 W, both near their measured
−0.22 and −0.13 W; the rest 0.14 W or less), and 0.51 W for fp16 50% zeros, 0.023 short of its rule
([`corrections-check.txt`](corrections-check.txt) [C2]). That row came in at about half of it as registered (+0.27 ± 0.15 W; ±0.29 W
on its own SD, an interval that holds the 0.51 W), and its draws are the ones the gate share explains least (result 3), so something
besides the gate share moves fp16 50% zeros' draws by a few tenths of a watt. Nothing here says a gated lane costs nothing.

## What it changes

**Section 11, the entry "Tile-to-tile spread": every one of the fifteen † rows now has a measured verdict, and two stay open.**
Twelve were measured on aifoundry3, the card whose table they are (E123): ten need no correction as registered (fp32 ReLU × small
weights among them, which E94 left unresolved; fp16 50% zeros only on its class's pooled SD, and on its own SD it is unresolved,
+0.27 ± 0.29 W), and int8 90% zero bytes and 90% zero words stay UNRESOLVED (−0.12 ± 0.16 and +0.14 ± 0.18 W against ±0.25 W)
and print their kind's mean. Two were measured on card 1 and translated here (E94's corrections, fp16 ReLU × small weights and fp32 50%
zeros), and one on card 1 only (int8 50% zero bytes, NO CORRECTION there). E123 did not run those three, and they keep what E94 gave
them.

**The kinds table, section 2 (for the page lane):**
- **The † note gets measured numbers for every † row:** float kinds gating 25–75% of lanes: between-draw SD 0.55–0.86 W on aifoundry3
  (pooled 0.75 W [0.54, 1.21]), about ±1.1–1.7 W at 95% for one tile (E94 read 0.49–0.57 W on card 1's rows of this class; the same
  five draws spread alike on both cards, 0.61 and 0.58 W, so the ranges differ by row and draw, not by card); the other float † rows
  0.21 W [0.14, 0.39] pooled; int8's † rows 0.10 W [0.05, 0.24] pooled (int8 50% zero bytes 0.07 W, E94). Replace "predicted on fp16
  50% zeros and 50% zero words" and "the other nine † rows 0.32 W or less, predicted" with these.
- **fp32 ReLU × small weights: NO CORRECTION on aifoundry3** (−0.13 ± 0.14 W, and ±0.11 W on its own SD; kind's S 15.17 ± 0.14 W in
  the page's frame, 15.19 in this session's; gate closes 50%). The row drops "kind on card 1: 14.16 ± 0.58" and "aifoundry3 gets no
  number for it from E94"; its cell stands.
- **fp16 50% zeros: the predicted note** ("S about 14.7 W against 15.22, at the band") **becomes a measured one.** In the page's
  frame the kind's S is 14.95 ± 0.15 W (E78's 15.22 less the measured offset, +0.27 ± 0.15 W: NO CORRECTION as registered, on class
  G's pooled SD). Its own adjusted SD is 0.22 W, and class G's SDs are unequal (Bartlett p 0.01): on its own SD the offset is
  +0.27 ± 0.29 W, UNRESOLVED, and the predicted +0.52 W lies inside that interval. So the registered verdict does not support the
  predicted note, and on the rule's own SD it is not excluded. This session's committed tile read +0.30 W above E78 (D 13.50 against
  13.20 W, inside S1's ±0.50 W). The gate closes 44% for the kind (41% the tile). The cell stands, as registered.
- **int8 90% zero bytes and 90% zero words** print their kind's mean beside the tile (S 3.89 ± 0.16 and 2.94 ± 0.18 W in the page's
  frame; 3.83 and 2.97 W in this session's), with no claim on the tile. Every other † row E123 ran keeps its cell.
- Beside E78's cells, a kind's S belongs in the page's frame (E78's S less the measured offset, `posthoc_e123.txt` [B]); it differs
  from this session's frame by 0.13 W or less on every row but fp16 50% zeros (0.24 W; `corrections-check.txt` [C3]).

**Records:** 03-experiments gains E123 (Q134); 05-claims' tile-spread line gains aifoundry3's measured SDs and the twelve verdicts
(fp16 50% zeros' as registered, on class G's pooled SD);
the hub's tile-spread entry links this README (the fix links its complaint). 14-card-behaviour: this session's sixteen tie cells sit
within −0.05 to +0.07 W of E78 except the committed fp16 50% zeros tile (+0.30 W).

**Blog-ready sentences** (D over the type's zeros on aifoundry3 at 600 MHz unless they say otherwise; each with its source):
- On the card whose table it is, ten of twelve randomly drawn kinds of numbers cost what their table row says, within half a watt
  (a quarter watt in int8), as registered; for one of the ten, fp16 "50% zeros", that rests on pooling its draws' spread with two
  similar kinds', and on its own spread it is unresolved. The other two, both int8, are inside a quarter watt by their central values,
  and none needs a correction (E123 R2, C1).
- A float kind gating 25–75% of its lanes moves 0.55–0.86 W from one random draw to the next; knowing how many lanes each draw gates
  leaves 0.06–0.22 W per kind (0.13 W pooled) (E123 result 4, R3, R5, C5).
- The power a gated lane saves is about D(random) per unit of gate share, tested as a frozen number: +0.58 ± 2.54 W per unit was left
  over (E123 R5).
- The same tiles, read on two different cards, moved alike to 0.07 W and spread alike (0.61 and 0.58 W) (E123 R8, C4).
- fp32 "ReLU × small weights" costs 13.20 ± 0.14 W over zeros as a kind, 0.13 W more than its table tile read in the same session;
  fp16 "50% zeros" 13.23 ± 0.15 W as registered (±0.29 W on its own spread), 0.27 W less than its tile (E123 R2, C1).

## Caveats

One card, one clock, one session, two passes. The primary pools each class's SD of the adjusted draws, as registered ("the pooling
assumes the adjusted draws' SD is common inside a class"). **In class G the data reject one SD** (Bartlett p 0.011, Brown-Forsythe
p 0.018: 0.22 W for fp16 50% zeros against 0.06 and 0.07 W), so fp16 50% zeros' NO CORRECTION is as registered, on class G's pooled
SD: with its own SD the offset is +0.27 ± 0.29 W, UNRESOLVED, and the predicted +0.52 W lies inside that interval (result 3,
[`corrections-check.txt`](corrections-check.txt) [C1]). fp32 ReLU and fp16 50% zero words hold on their own SDs (±0.11 and ±0.12 W).
Two or three draws on the nine rows of classes LF and LI: their verdicts lean on the class's pooled SD, an assumption the
registration names (per-rule SDs of the adjusted draws are 0.02–0.15 W in LF and 0.01–0.12 W in LI, `scored.json` › `rule_s_w`).
There the data do not reject one SD (Bartlett p 0.14 and 0.41). On their own SDs the five LF rows stay NO CORRECTION and int8 90% zero
bytes and words stay UNRESOLVED; int8 50% zero words and int8 ternary, with 4.8 and 2.1 df, sit at int8's ±0.25 W band: 0.001 and
0.006 W past it with the scorer's floored t (UNRESOLVED), 0.012 and 0.003 W inside it at the exact fractional df (NO CORRECTION; C1).
The primary's slope was frozen from E94's post-hoc reading; R5 tests it in class G only. In LF and LI the
gate share varies little, so there the adjustment is at most 0.26 W, except `fp32.smallint_e123d3`'s −0.90 W (it gates 0.085 against
the rule's 0.121; its measured move, +0.65 W, is near where the gate law put it, +0.53 W). The primary does not carry the dips-kept arm's noise: with dips kept, six of the ten NO CORRECTION rows
read UNRESOLVED (result 6), so their NO CORRECTION rests on the registered dip removal (E82 A2's definition, as E93, E94 and E121). The
rule is synthetic: nothing here says what a real tensor's kind is, and the speed columns were not re-drawn. int8's bus counts are
provisional (kinds README). fp16 50% zeros' committed tile read 0.30 W above E78 in this session, inside S1's band and E78's own
interval; a session effect on that one tile would move its offset by that much, and its verdict would still be NO CORRECTION, on
either SD.

## Files

`e123.json` (the registered reduction), `runs.csv`, `reduce.txt`, `reduce.log`; the arms `e123-dipskept`, `e123-gatesoff`, `e123-auto`,
`e123-leak0.2414`, `e123-leak0.3803`, `e123-leak0.545`, `e123-leak0` (`.json`, with `runs-*.csv`, `reduce-*.txt`, `reduce-*.log`);
`scored.json` and `results.md` (`score_e123.py`: every rule, each verdict at every arm, the arm-sensitive list); `posthoc_e123.py` and its
output `posthoc_e123.txt` (A the arms per rule, B the page's frame, C fp32 ReLU on two cards, D the SDs, E fp16 50% zeros; standard library
only; it changes nothing); `corrections-check.py` and its output `corrections-check.txt` (C1–C7 of § Corrections after verification:
the class pooling and each rule's own SD, the gate-share gaps, the page's frame, the bridge's spread on both cards, what the gate share
leaves, the table cells with their intervals, E94's form rounded once; standard library only, post hoc; it changes nothing);
`code.sha256`; `logs/` (`e123-queue.log`, `e123-dry.log`, `e123-list.err`, `setup.log`, `smoke.log`,
`config-session-start.json`, `config-session-end.json`, `push-and-claim-times.txt`); `aifoundry3/kinds/p12310`, `p12311` (raw telemetry,
marks, launch records, tile dumps, configs, manifests) and `kinds-smoke-p12301`. Code and the registration: `tools/claims-v3/e123/`.
Reproduce: copy `aifoundry3/` to `build/e123-raw/aifoundry3/` (with `logs/`), then
`PY=python3 bash tools/claims-v3/e123/collect_e123.sh 'p123[1-9][0-9]' build/e123-raw/aifoundry3`.

## Corrections after verification (Sun 1 Nov 2026)

An independent verifier (Q134's) checked E123 the same evening, after the data commit (`27080c8b`). Its verdict: holds with fixes,
one major fault and six minor ones, all in how the results were stated. It re-ran the registered collector over the committed raw
passes (`e123.json`, the seven arm reductions, `runs*.csv`, `reduce.txt`, `scored.json`, `results.md` and `score.log` byte-identical),
re-ran the self-test (28 of 28), matched all 164 committed raw files against aifoundry3's copies by sha256 (read only), rebuilt the 42
tiles from their registered seeds, recomputed every rule from E123.md's text, and found the registration timing, the frozen rules,
the card's safety and the posting protocol sound. Each fault is corrected above, at the desk: no card was touched, nothing was re-run,
and no registered prediction, rule, number or verdict changed (R2: 10 NO CORRECTION, 2 UNRESOLVED, 0 CORRECTION; every other rule as
before). Every file of `27080c8b` is byte-identical except this README; `corrections-check.py` and its output
[`corrections-check.txt`](corrections-check.txt) are new and print every new number below from `scored.json` and the frozen
`predictions-e123.json` (its statistics were checked against scipy at the desk: t quantiles to 1e-10, the p-values to 1e-6).

| # | what was wrong | what changed |
|---|---|---|
| C1 | **fp16 50% zeros' NO CORRECTION rests on class G's pooled SD, which the data reject, and the README named the pooling caveat only for LF and LI.** Its adjusted draws spread 0.22 W (4 df), against 0.06 and 0.07 W for fp32 ReLU and fp16 50% zero words (Bartlett p 0.011, Brown-Forsythe p 0.018; Bartlett in LF p 0.14, in LI p 0.41). Result 3 said the page's predicted note "does not hold", and the blog sentence gave the 0.27 W with no caveat | The verdict stays as registered and is labelled "on class G's pooled SD" in result 1's table, results 1 and 3, § Registered against happened, § What it changes, the blog sentences and § Caveats, each with: on its own SD (the scorer's formula with s' and its df swapped) the offset is +0.27 ± 0.29 W (4.4 df, t floored as the scorer's; ±0.285 at the exact df), UNRESOLVED, an interval that holds both 0 and the frozen +0.52 / +0.50 W. Result 3 now says the registered verdict does not support the predicted note and, on the rule's own SD, does not exclude it. fp32 ReLU's verdict holds on its own SD (±0.11 W). § Caveats also gives the LF and LI rows' own-SD reading (`corrections-check.txt` [C1]) |
| C2 | **An arithmetic slip in § Interpretation:** "predicts offsets of 0.14 W or less on every row but fp16 50% zeros". Two rows exceed it: fp16 50% zero words −0.239 W (gap 0.0108 × 22.16) and fp32 ReLU −0.170 W (0.0069 × 24.72) | "0.24 W or less on every row but fp16 50% zeros (fp16 50% zero words −0.24 and fp32 ReLU −0.17 W, both near their measured −0.22 and −0.13 W; the rest 0.14 W or less)" ([C2]) |
| C3 | **fp16 50% zeros' kind's S went to the page in this session's frame** (15.19 ± 0.15 W) beside E78's tile cell (15.22), so the page would show kind and tile 0.03 W apart where the same-session contrast is +0.27 W | § What it changes gives the page's frame, 14.95 ± 0.15 W (E78's 15.22 less the offset; ±0.29 on the rule's own SD), and says this session's committed tile read +0.30 W above E78; result 3 names both frames and why they differ (0.24 W here, 0.13 W or less on the other eleven rows) ([C3]). Found in this pass: the fp32 ReLU and int8 bullets had this session's frame too (0.02–0.06 W from the page's); they now give the page's frame (15.17, 3.89 and 2.94 W, from `posthoc_e123.txt` [B]), and a closing bullet says the page uses that frame beside E78's cells |
| C4 | **"0.55–0.86 W on aifoundry3" against "0.49–0.57 W on card 1" invited reading a card difference.** The rows differ (only fp32 ReLU is a rule of both), and the same draws spread alike on both cards | Result 4 and the † note's proposal add that the same five draws spread alike on both cards (0.61 W here, 0.58 W on card 1 at E82's scale), so the ranges differ by row and draw, not by card, and that fp32 ReLU's 0.81 W here comes from its new draw `e123d1` (14.14 W; 0.66 W without it) ([C4]) |
| C5 | **"Leaves about 0.1 W"** (the second blog sentence and § Interpretation): in class G the gate share leaves 0.13 W pooled, and 0.22 W for fp16 50% zeros | "leaves 0.06–0.22 W per kind (0.13 W pooled)"; result 4 gives the three per-kind values ([C5]) |
| C6 | **Three of E94's-form values in result 1's table were rounded twice:** fp16 90% zeros' offset −0.0146 (printed −0.02), int8 50% zero words' +0.0546 (printed +0.06), fp32 integers' half-width 0.9845 (printed 0.99) | −0.01, +0.05 and 0.98. Every other cell of that table was checked against `scored.json` and the frozen predictions at the desk; none else differs ([C7]) |
| C7 | **Found in this pass, not by the verifier:** § What it changes said "about ±1–2 W at 95% for one tile" where result 4 says ±1.1–1.7 W | ±1.1–1.7 W in both |

One more of the verifier's faults was in the lane's report to the integration lanes, not in this page (it carried no table cells:
each kind's D, S, nJ per op and pJ per MAC with their 95% intervals, now printed in `corrections-check.txt` [C6]); it was corrected
there.
