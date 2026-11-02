# E130: which int8 multiplier - Q136(a)'s single-bit set on aifoundry3, each netlist's frozen prediction scored (aifoundry3 card 0, 600 MHz)

*On the kinds page, [section 11, what is still open](https://spacesheep.dev/@yaroslavvb/horace-kinds-of-numbers#11-what-is-still-open):
item 12, "int8 at gate level", its first open point, "which multiplier the chip has (the single bits favour Booth on B, the
kind-level watts Booth on A; neither test registered)". Asked by Q134's final critic, its item 8.*

*Mon 2 Nov 2026 (week 45), Q136. Pre-registered in `57506b0f` (pushed 09:01:48 PST), with amendments A1–A3 after its verification
(`5e770149` 10:34:08 and `7dae3ed2` 10:34:38 PST) and A4 for this session (`d1218f6e` 12:31:34 PST), all before the claim and before
any E130 data: [`tools/claims-v3/e130/README.md`](../../../../tools/claims-v3/e130/README.md). The predictions it scores were frozen by
[Q136(a)](../2026-11-02-q136a-int8-netlist-predictions/README.md) in `d64ea98c` (its corrections, `8ab2ed9d`, change no frozen
number) and are copied number for number into `predictions-e130.json` (sha256 `497bb63d…`), with the thresholds, bands and rules.
**The first session ran nothing**: the lab hosts' Tailscale SSH approvals lapsed from about 08:40 to 10:04 PST and every ssh of the
first lane to aifoundry3 stopped at the check, so this second session is E130's only one, with the whole registered budget (A4).
aifoundry3 card 0 at 600 MHz in every sample, 522 mV in every run; `ettelem config` read at the session's start (12:33:39) and end
(13:01:59), and at both ends of the smoke and of every block, under the card lock with `timeout 10`: TDP 0 W, threshold 65 °C,
max_power, 600 MHz, 523 mV, all 23 reads alike, never set. **Every device-management command sent was a read** (nine kinds, two of
them PMIC voltage-register reads, which the owner's rule of 2 November 2026 allows; § Device commands sent); no governor move, no
reset, no `--reset-ms`, no firmware-revisions query, no residency read. The day's one card post in #community-lab (message
1566837317765963987) was rewritten at 12:32:52 to add this card's clause and at 13:02:59 to append " — released" (by then it was the
last card held). Card session 12:33:39–13:01:59 PST, **28.3 of the 30 card-minutes allowed**; all ten registered blocks ran
([`logs/push-and-claim-times.txt`](logs/push-and-claim-times.txt)).*

*Corrected after an independent verification, Mon 2 Nov 2026 (§ [Corrections after verification](#corrections-after-verification-mon-2-nov-2026),
C1–C5): the rail arm's R1 and R4 labels are a reading in rail fJ against board-fJ lines, now given in board units beside them; the
sign bits' base words and held operands; the session's noise set against the plan like for like; the scope of "every netlist is
excluded"; the die after the first block. Desk only, no card touched. No registered rule, prediction, number or verdict changed.*

**In plain words.** Four gate-level versions of the chip's int8 multiplier, built from the public RTL, disagree about what flipping
one bit costs. Two recode the B operand in radix-4 Booth digits, so B's odd bits should cost about four times its even bits; one
recodes A instead; one recodes neither. E130 ran 26 tiles, each one bit away from its own zero tile, on base words chosen and
predicted before the card saw them. **The A operand is not recoded**: A's odd and even bits cost the same (odd − even −1.7
[−6.6, +3.2] fJ a flipped bit), and A's sign bit costs 67.8 [58.8, 76.8] fJ more when B is dense, as only a multiplier that keeps A
whole predicts; both registered rules agree at every reading, so the netlist that recodes A is out. **Whether B is recoded stays
undecided.** B's odd bits cost more than its even bits, +33.8 [+11.0, +56.7] fJ (2.4×), about what E79 read on this card at its own
base words (+40 fJ, 2.2×), half the +60 fJ (4.3×) the Booth-on-B netlists predict and far above the +1 fJ of the one with no
recoder. The registered line between those two groups is at 30.7 fJ, the interval straddles it, so **the registered primary reads
INCONCLUSIVE between Booth on B and no Booth**. On the registered primary each of the four netlists misses at least one of the three
separating contrasts, so none predicts the card's single bits as a whole; at the dips-kept arm the two Booth-on-B netlists survive
*(corrected after verification, [C4](#corrections-after-verification-mon-2-nov-2026): this first gave the primary's reading without
naming it)*. My frozen expectation, Booth on B, was not confirmed.

## Results

**Ten blocks of ten kept** (B 13010–13015, A 13020–13023), **304 of 304 runs**, none failing a run gate (600 MHz, 318 cycles an op,
duty ≥ 0.996, every dumped tile equal to its registered sha256), none set aside by the train gate, on the registered primary: the
board's `p_raw` over each item's own zero interpolated in time, dips removed by E82 A2's definition, no temperature term
([`results.md`](results.md), [`scored.json`](scored.json)).

**1. The registered verdicts.**

| rule | what it asks | primary (board `p_raw`) | rail (rail fJ, see [C1](#corrections-after-verification-mon-2-nov-2026)) | board `p80` | dips kept | gates off |
|---|---|---|---|---|---|---|
| E130-R1 | is B recoded? B's odd − even against T_B = 30.68 fJ | **INCONCLUSIVE** | FLAT | INCONCLUSIVE | INCONCLUSIVE | INCONCLUSIVE |
| E130-R2 | is A recoded? A's odd − even against T_A = 27.58 fJ | **FLAT** | FLAT | FLAT | FLAT | FLAT |
| E130-R3 | does A's sign cost more with a dense B? against T_S = 18.07 fJ | **RISES** | RISES | RISES | RISES | RISES |
| **E130-R4** | **which multiplier (the registered primary)** | **INCONCLUSIVE between BOOTH ON B / NO BOOTH** (2 of 3 rules decided) | NO BOOTH | INCONCLUSIVE B/none | INCONCLUSIVE B/none | INCONCLUSIVE B/none |
| E130-R5 | A's sign, word 2 ÷ word 1, in the shared band [0.990, 1.011] | **HOLDS** | HOLDS | HOLDS | HOLDS | HOLDS |
| E130-R6 | B's sign, word 2 ÷ word 1, in the shared band [1.008, 1.026] | **HOLDS** | FAILS (BELOW) | HOLDS | HOLDS | HOLDS |

R1, R4 and R6 are **arm-sensitive** (they move at the rail arm). R2 and R3 contradict Booth on A, which predicts (FLAT, RECODED, FLAT),
at every arm. R5 and R6 HOLD, which only fails to exclude: in the self-test's model, with every netlist right, R6 reads FAILS in 4.2%
of sessions and R5 in 1.2% (A3.3), and here B's ratio, 0.57 [0.05, 1.30], is too wide to test anything.

*Dated note ([C1](#corrections-after-verification-mon-2-nov-2026)), Mon 2 Nov 2026, after verification. Post hoc, labelled, no label
changes: **the rail's R1 FLAT and R4 NO BOOTH are a reading in rail fJ against board-fJ lines.** The registered code divides the
rail's watts by the same flips and rate and scores them against T_B, T_A, T_S and the netlists' bands, which are board fJ (each
netlist's k is fitted on board watts). At E78's frozen rail-per-board constant, 0.81 (`reduce_e78.py --c-rb`, "frozen from E79"; A's
bits 0–6 here give 0.811 [0.756, 0.872]), the rail's B odd − even, +26.9 [+23.9, +29.8] rail-fJ, is **+33.2 [+29.6, +36.7]
board-equivalent fJ: it straddles T_B = 30.68 as the primary does**, and R1 and R4 read there what the primary reads. The rail's R1
reads FLAT, and its R4 NO BOOTH, only if one rail-fJ is worth at least 0.970 board-fJ; RECODED and BOOTH ON B at 0.780 or less. B's
own rail/board level ratio, 1.128 [0.883, 1.603], is too wide to pin that scale for B. The rail's R2 FLAT and R3 RISES hold at any
scale from 0.11 to 2.7, and its R6 is a ratio of two rail readings, in no unit. The rail's B odd ÷ even, 1.79 [1.68, 1.92], also in
no unit, lies between the groups' frozen ratios (Booth on B 4.16–4.39, the others 1.05–1.09) and fits neither; the board's, 2.41
[1.26, 38.2], excludes the others' and not Booth on B's. The ratios are reported, never a rule
([`corrections_e130.txt`](corrections_e130.txt) [A]).*

**2. The separators**, fJ per flipped bit on the board, 95% over blocks; each netlist's frozen prediction (`nets_map`; `nets_hier`):

| statistic | card | `booth_tree` | `booth` | `booth_swap` | `plain` | line |
|---|---|---|---|---|---|---|
| **B: odd (1, 3, 5) − even (0, 2, 4)** | **+33.8 [+11.0, +56.7]** | 60.4; 60.7 | 60.3; 60.6 | 0.5; 0.8 | 0.8; 1.1 | T_B 30.68 |
| **A: odd − even** | **−1.7 [−6.6, +3.2]** | 0.5; 1.1 | −1.0; 0.8 | 86.1; 50.6 | 4.5; 2.9 | T_A 27.58 |
| **A sign: B = 0x55 − B = 1** | **+67.8 [+58.8, +76.8]** | 31.9; 49.4 | 34.3; 47.6 | −8.2; 4.2 | 53.4; 34.1 | T_S 18.07 |
| B odd ÷ even | 2.41 [1.26, 38.2] | 4.39; 4.27 | 4.30; 4.16 | 1.05; 1.07 | 1.07; 1.09 | reported |
| A odd ÷ even | 0.98 [0.92, 1.04] | 1.01; 1.04 | 0.98; 1.03 | 2.52; 2.62 | 1.10; 1.13 | reported |
| A sign, B = 0x55 ÷ B = 1 | 1.43 [1.36, 1.51] | 1.11; 1.32 | 1.12; 1.32 | 0.96; 1.03 | 1.22; 1.24 | reported |
| A sign, word 2 ÷ word 1 | 1.02 [0.98, 1.07] | 1.00; 1.01 | 1.01; 1.01 | 1.01; 0.99 | 1.01; 1.00 | band [0.990, 1.011] |
| B sign, word 2 ÷ word 1 | 0.57 [0.05, 1.30] | 1.03; 1.02 | 1.02; 1.02 | 1.01; 1.01 | 1.02; 1.01 | band [1.008, 1.026] |
| B sign: A = 0x55 − A = 1 | +18.0 [−24.3, +60.3] | −7.7; −10.1 | −8.0; −10.2 | 8.4; 6.4 | −17.5; −19.5 | separates nothing |
| B list mean, bits 0–6 (a level) | +41.9 [+28.3, +55.6] | 43.9; 44.8 | 44.4; 45.3 | 11.7; 12.4 | 11.6; 12.3 | reported |
| A list mean, bits 0–6 (a level) | +79.8 [+75.9, +83.8] | 54.7; 28.5 | 55.0; 27.9 | 95.5; 53.4 | 47.8; 24.2 | reported |

**3. Each netlist's frozen prediction, scored (E130-N).** A netlist SURVIVES if the card's interval overlaps its band on all three
separators.

| netlist | group | verdict | items consistent / above / below its bands | rms, fJ: `nets_map`; `nets_hier` | Spearman, B list; A list |
|---|---|---|---|---|---|
| `booth_tree` | Booth on B | **EXCLUDED** by the A sign step (card 58.8–76.8, band 29.1–53.9) | 11 / 8 / 1 | 55.5; 38.4 | +0.67; +0.60 |
| `booth` | Booth on B | **EXCLUDED** by the A sign step (band 31.2–51.9) | 11 / 8 / 1 | 54.4; 39.2 | +0.74; +0.69 |
| `booth_swap` | Booth on A | **EXCLUDED** by all three | 12 / 6 / 2 | 47.0; 41.8 | +0.69; −0.12 |
| `plain` | no Booth | **EXCLUDED** by B's odd − even (band 0.7–1.2) | 9 / 10 / 1 | 48.3; 46.0 | +0.90; +0.40 |

On B's odd − even the card's interval overlaps the Booth-on-B bands (54.8–66.2) by under 2 fJ and lies far above `plain`'s; on the A
sign step it lies above both Booth-on-B bands and touches `plain`'s (30.4–59.1) by 0.3 fJ. The A sign step is a difference of two
levels, so it carries k (2–5% s.e.) and the merge. At the dips-kept arm (block 13021 set aside there by the train gate, so three A
blocks), the A step's interval widens to [51.2, 85.2] and `booth` and `booth_tree` SURVIVE; at the rail arm every netlist is
EXCLUDED by B's odd − even. Every arm: [`scored.json`](scored.json) › `arms`. *(Dated note, [C1](#corrections-after-verification-mon-2-nov-2026):
the rail's E130-N is read in rail fJ too, but it does not rest on the unit: B's odd − even excludes all four bands at any
rail-per-board scale from 0.54 to 19.5, and no netlist survives at any scale from 0.1 to 30. Which separators exclude `booth` and
`booth_tree` there does depend on it: at 0.81 the A sign step, +62.2 [+61.3, +63.1] board-equivalent fJ, lies above both their bands
as on the primary; [`corrections_e130.txt`](corrections_e130.txt) [A].)*

**4. Every item**, board fJ per flipped bit [95%] over 6 B or 4 A blocks, and the step in watts; `booth_tree` and `plain` at
`nets_map` (`booth` is within 1–6 fJ of `booth_tree` on every item, `booth_swap` is in [`results.md`](results.md)):

| tile | bit | card fJ | step, W | `booth_tree` | `plain` | | tile | bit | card fJ | step, W | `booth_tree` | `plain` |
|---|---:|---|---|---:|---:|---|---|---:|---|---|---:|---:|
| `b1_0` | 0 | +3.3 [−35.6, +42.1] | 0.006 | 9.7 | 9.7 | | `a1_0` | 0 | +83.0 [+74.0, +92.1] | 1.310 | 46.6 | 41.8 |
| `b1_1` | 1 | +44.0 [−2.7, +90.7] | 0.087 | 90.3 | 8.4 | | `a1_1` | 1 | +77.2 [+73.1, +81.3] | 1.218 | 47.5 | 45.0 |
| `b1_2` | 2 | +22.1 [+4.0, +40.1] | 0.043 | 19.7 | 11.3 | | `a1_2` | 2 | +71.8 [+61.8, +81.9] | 1.133 | 50.6 | 44.8 |
| `b1_3` | 3 | +67.2 [+54.6, +79.8] | 0.133 | 79.3 | 13.4 | | `a1_3` | 3 | +78.0 [+62.7, +93.4] | 1.231 | 56.2 | 49.4 |
| `b1_4` | 4 | +46.8 [+11.5, +82.1] | 0.092 | 24.0 | 12.2 | | `a1_4` | 4 | +87.7 [+85.0, +90.3] | 1.383 | 62.9 | 47.2 |
| `b1_5` | 5 | +62.5 [+32.5, +92.4] | 0.123 | 64.8 | 13.9 | | `a1_5` | 5 | +82.3 [+79.2, +85.3] | 1.297 | 57.8 | 53.1 |
| `b1_6` | 6 | +47.7 [+23.4, +72.1] | 0.094 | 19.6 | 12.3 | | `a1_6` | 6 | +78.7 [+77.4, +80.0] | 1.242 | 61.1 | 53.2 |
| `b1_7` | sign | +98.9 [+71.0, +126.9] | 0.195 | 127.2 | 135.3 | | `a1_7` | sign | +156.7 [+150.7, +162.6] | 2.471 | 294.1 | 247.5 |
| `b2_7` | sign, word 2 | +56.5 [+5.2, +107.9] | 0.111 | 130.4 | 137.3 | | `a2_7` | sign, word 2 | +160.2 [+157.7, +162.7] | 2.527 | 294.1 | 250.2 |
| `b1d_7` | sign, A = 0x55 | +117.0 [+79.7, +154.2] | 0.231 | 119.5 | 117.7 | | `a1d_7` | sign, B = 0x55 | +224.5 [+219.8, +229.2] | 3.541 | 326.0 | 300.9 |

The steps run 0.006–0.231 W on the B list and 1.13–3.54 W on the A list. On the A list, `nets_hier` puts the sign bit at 133–153 fJ
(`booth_tree` 152.9), where the card reads 157 and 160, and the magnitude bits at 20–33 in the three netlists that do not recode A,
against the card's 72–88.

**5. Registered against what happened.** Frozen expectation: R1 RECODED (**wrong**: INCONCLUSIVE), R2 FLAT (right), R3 RISES
(right), so R4 BOOTH ON B (**wrong**: INCONCLUSIVE between Booth on B and no Booth); R5 and R6 HOLDS (right). Per netlist: `booth` and
`booth_tree` "SURVIVE, or are EXCLUDED only by B's amplitude" (**wrong**: on the primary they are EXCLUDED by the A sign step, and B's
amplitude is inside their bands only because its interval is wide); `booth_swap` and `plain` EXCLUDED by B's odd − even (right).
**The precision was short of the plan.** The zero reads scatter about their neighbours' line with an sd of 0.040 W on the board
(0.036 W on the rail; 72 interior reads). In the self-test's own model that same statistic reads 0.033 W at the planning σ of 0.025 W
a run, so the session's per-run σ was about 0.030 W, **about 1.2× the plan's** (σ from 0.025 to 0.038 W puts the session's scatter
inside the model's 5–95% range; [`corrections_e130.txt`](corrections_e130.txt) [B]). B's odd − even came out at ±22.8 fJ, against the
registered self-test's median 8.7–10.3 fJ at 0.025 W and 12.3–14.4 fJ at 0.035 W over its five worlds
([`selftest.txt`](../../../../tools/claims-v3/e130/selftest.txt), [`selftest-power.txt`](../../../../tools/claims-v3/e130/selftest-power.txt))
and the same model's 10.4–11.6 fJ at 0.030 W ([B]): about twice what that per-run noise gives. Post hoc (§ 6), most of the width is
one block, 13010 (+75.9 fJ; without it ±9.7 fJ over five blocks). *(Corrected after verification, [C3](#corrections-after-verification-mon-2-nov-2026): this first set the scatter against σ itself,
"against the planning σ of 0.025 W a run", which makes the shortfall look like 1.6×, and gave the 0.035 W medians as 12.6–14.4 fJ.)*
The registration named this case before the data: at E79's amplitude
(+40 fJ, 9 fJ above T_B), R4 reads BOOTH ON B in 25 of 40 sessions at 0.025 W and 15 of 40 at 0.035 W, INCONCLUSIVE in the rest,
never a wrong group ([`selftest-power.txt`](../../../../tools/claims-v3/e130/selftest-power.txt)). The card sits there, a little
lower, at a noisier session's precision.

**6. Post hoc, labelled; no verdict moves** ([`posthoc_e130.py`](posthoc_e130.py) → [`posthoc_e130.txt`](posthoc_e130.txt), committed
files only):
- **Block by block**, B's odd − even reads +75.9 in the session's first block (13010, while the die warmed from 51 to 53 °C under the
  trains; it read 52–55 °C from then on *(corrected after verification, [C5](#corrections-after-verification-mon-2-nov-2026): "53–55 °C")*)
  and +16.5 to +34.0 in the other five. Left out one block at a time, it reads +25.4 [+15.8, +35.1] without
  13010 and +33.8 to +37.3 without any other: it straddles T_B every time. A's two separators are steady block to block (A odd − even
  −5.4 to +1.9; the A sign step +60.3 to +72.4).
- **B's list against E79's on this card**, board fJ: odd bits 57.9 against 73.2, even 24.0 against 32.9, odd − even +33.8 against
  +40.2, odd ÷ even 2.41 against 2.22. At new base words (B1 shares two of its bytes with E79's word, in other lanes) the card's B
  list keeps E79's shape and roughly its amplitude, not the Booth netlists' 4.3×.
- **The minion rail** (an arm, where the multiplier draws): B's odd − even +26.9 [+23.9, +29.8] rail-fJ, odd ÷ even 1.79
  [1.68, 1.92]; much tighter than the board's, and wholly below T_B, which is why R1 reads FLAT there. That FLAT is the registered
  word for "below the line", not "no alternation": the interval is far from zero and from `plain`'s +1. A's odd − even −0.5
  [−3.8, +2.9]; the A sign step +50.4 [+49.6, +51.1], 1.42× [1.41, 1.42]. The rail reads A's bits 0–6 at 0.81 of the board's level,
  the rail-per-board constant E78's reduction froze from E79 (`--c-rb 0.81`), so the rail's fJ are not the netlists' board fJ.
  *(Dated note, [C1](#corrections-after-verification-mon-2-nov-2026): at that constant the rail's B odd − even is +33.2 [+29.6, +36.7]
  board-equivalent fJ, which straddles T_B. "Wholly below T_B" holds in rail fJ only; the note under § 1 gives every scale.)*
- **The A sign bit's price does not move with the base word**: 156.7 and 160.2 fJ at A1 and A2 (R5 HOLDS, 1.02 [0.98, 1.07]),
  against E79's 152.1 at its own word. Every netlist's `nets_map` puts it at 228–294 (1.4–1.9× the card), `nets_hier` at 133–153.
  *(Added after verification, [C2](#corrections-after-verification-mon-2-nov-2026); post hoc:)* both E130 readings are with B held at
  1; with B = 0x55 it is 224.5 [219.8, 229.2] fJ (`a1d_7`). **B's sign bit is not shown to behave this way**: +98.9 [+71.0, +126.9]
  and +56.5 [+5.2, +107.9] fJ at B1 and B2 with A held at 1, a ratio of 0.57 [0.05, 1.30] on the board, too wide to test, and 0.61
  [0.49, 0.75] on the rail, a ratio in no unit that excludes 1 (R6 FAILS BELOW there); E79 read +16.8 at its own word, on its heated
  protocol. E79's two figures are [`predictions-e130.json`](../../../../tools/claims-v3/e130/predictions-e130.json) ›
  `card_precision_e79` (`a_list_board_fJ[7]`, `b_list_board_fJ[7]`); the held operands are
  [`e130-items.json`](../../../../tools/claims-v3/e130/e130-items.json) › `held` ([`corrections_e130.txt`](corrections_e130.txt) [D]).
  The ratio to the card was "1.5–1.9×": `booth_swap`'s 228–230 fJ is 1.43–1.45× it.

## What it changes

- **Item 12, which multiplier: narrowed, not closed.** On base words chosen and predicted before the card saw them, the card's int8
  single bits exclude a Booth recoder on A (E130-R2 FLAT and E130-R3 RISES, registered, at every arm): the netlist that E78's
  kind-level watts favoured (`booth_swap`, Q133(a) result 6) is out. Booth on B against no recoder is **INCONCLUSIVE** (E130-R4):
  B's odd bits cost 2.4× its even bits, +33.8 [+11.0, +56.7] fJ, an interval that straddles the registered line at 30.7 fJ. The card's
  B list alternates at about half the Booth netlists' contrast and far above the plain array's, and on the registered primary every
  one of Q133(a)'s four netlists is EXCLUDED on at least one separator (E130-N; so too at three of the four arms, while at the
  dips-kept arm `booth` and `booth_tree` survive; *corrected after verification,
  [C4](#corrections-after-verification-mon-2-nov-2026)*). Post hoc (§ 6), the B-list shape E79 read is the card's at a second set of
  base words too, and none of the four structures reproduces it together with A's dense-B sign step (1.43× against 0.96–1.32× in the
  four).
- **For the kinds page's section 11**: item 12's "the single bits favour Booth on B, the kind-level watts Booth on A; neither test
  registered" becomes "a registered single-bit test excludes Booth on A (E130); Booth on B against no recoder is inconclusive, B's
  odd bits costing 2.4× its even (odd − even +33.8 [+11.0, +56.7] fJ; the ratio's own interval is [1.26, 38.2]), half the Booth
  netlists' contrast; on the registered primary none of the four netlists fits the card's single bits as a whole". The sign bit's
  price "about twice the card's" stands for `nets_map` (A's sign 1.4–1.9× the card's 157–160 fJ at two new words, B held at 1), not
  for `nets_hier`. *(Corrected after verification, [C4](#corrections-after-verification-mon-2-nov-2026) and
  [C2](#corrections-after-verification-mon-2-nov-2026): the proposed text gave the 2.4× without an interval and the netlists' reading
  without naming the primary, and the ratio read "1.5–1.9×".)*
- **For the hubs' Levels/Status**: item 12 narrowed by E130 (registered, one card); what remains is B's recoding, the structure that
  gives B half Booth's alternation and A's sign its dense-B rise, glitches (zero delay), and the clock term.

## Device commands sent

As registered ([`tools/claims-v3/e130/README.md`](../../../../tools/claims-v3/e130/README.md) § Device commands sent, with A1),
classified from the firmware source at et-platform `836a4ab`, the public BL2 0.22.0: **nine management commands, every one a read**,
and no write of any kind. `ettelem config` (`GET_MODULE_STATIC_TDP_LEVEL`, `GET_MODULE_TEMPERATURE_THRESHOLDS`,
`GET_MODULE_POWER_STATE`, `GET_ASIC_FREQUENCIES`, `GET_ASIC_VOLTAGE`) at the smoke's two ends, at both ends of each of the ten blocks
and once at the session end: 23 reads of the five. `ettelem sample` at 10 Hz through the smoke and each block (`GET_MODULE_POWER`,
`GET_SP_STATS`, `GET_MODULE_CURRENT_TEMPERATURE`, `GET_ASIC_VOLTAGE`, `GET_MODULE_VOLTAGE`, `GET_ASIC_FREQUENCIES`; 16,091 samples in
the eleven telemetry files), and two 1 s `die_c` samples at each block's two ends. The PMIC accesses are `GET_ASIC_VOLTAGE`'s two
voltage-register reads and `GET_MODULE_VOLTAGE`'s nine, which the owner's rule of 2 November 2026 allows. **Not sent:** the statistics
reset (no E130 call passes `--reset-ms`; `since_reset_ms` reads −1 in all 16,091 samples), the firmware-revisions query, any residency
read, any set. The lib.sh drain (`dev_mngt_service -m DM_CMD_GET_MODULE_POWER`, a read, after a sampler fails to start twice or
ignores SIGTERM) never ran: no sampler failed, and no block log or the queue log has a drain or sampler-failure line. The host
program (`sparsity_host`) opened the ops node only. Binaries: the registered `sparsity_host` `20e760c2…` and `ettelem` `16037641…`
([`logs/binaries.sha256`](logs/binaries.sha256)); that `ettelem` was built from the box tree's `tools/ettelem/ettelem.cpp`
(`ba9a0ac3…`), whose `config` and `sample` code is byte-identical to the reviewed source's
([E132's `logs/ettelem-binary-check.txt`](../2026-11-02-e132-memory-split/logs/ettelem-binary-check.txt) and its correction C1).

**The preflight at this session's commit** (A1.2, A4.4): Q136(w)'s corrected checker (`dmcmd_audit.py` `f29e91ca…`, table
`50168632…`) at `d1218f6e`, from the repository root on the eleven files the registration names, reads NO-GO on one line only, the
conditional `STATS_RESET` at `lib.sh:154` (`start_sampler` forwards `"$@"`), and **GO, 31 send sites, 0 disallowed** with A1's reviewed
exception (`block_e130.sh:106`, E130's only `start_sampler` call, passes the output file and the duration and nothing else):
[`logs/dmcmd_audit_e130_session2.txt`](logs/dmcmd_audit_e130_session2.txt),
[`logs/dmcmd_audit_e130_session2_except.txt`](logs/dmcmd_audit_e130_session2_except.txt).

**The residual** (A1.1): aifoundry3 runs the thermal firmware build first flashed there on 7 October 2026, not the public `836a4ab`;
it answers command 74, which `836a4ab` lacks, and its source is not held. So "every command a read" on the running build rests on the
public source and on the nine reads' unchanged behaviour. A1's condition held: the session-start `ettelem config` and the smoke's
telemetry came back in E127's form (the same fields; TDP 0 W, 65 °C, 600 MHz; `since_reset_ms` −1 in all 341 smoke samples;
[`logs/a1-form-check.txt`](logs/a1-form-check.txt)), and so did every later read: all 23 config reads equal the session-start read, and
all 16,091 samples carry E127's fields.

## How it ran

| PST | what |
|---|---|
| 12:29:19 | E134's lane released card 0 (its clause left the day's post at 12:29:58) |
| 12:30–12:31 | this lane read the day's post (no aifoundry3 clause) and probed aifoundry3 read-only: `et-who` "No process holds an ET-SoC-1 device node or card lock"; other users' logins idle since 26 Oct, which do not block on this card (`hl/README.md`'s departure D1, kept since E60) |
| 12:31:34 | A4 committed and pushed (`d1218f6e`); the checker run at it (12:31:48) |
| 12:31:57–12:32:23 | `run_e130.sh setup` on the box, no device access: every hash identical to the freeze, both binaries the registered ones, dry runs of a B and an A block, the queue's stub test ([`logs/box-setup.txt`](logs/box-setup.txt)) |
| 12:32:52 | the claim: the day's post rewritten (`edit_replace.mjs`, `EXPECT_TEXT`, dry run then `--save`) to add `using aifoundry3 for 1 h, until ~13:35 PST`, the aifoundry2 clause kept word for word |
| 12:33:39–12:34:16 | the smoke, 13001, the session start: 318 cycles an op on all eight tiles, every dump equal to its sha256, 341 samples, die 51–52 °C ([`logs/smoke.txt`](logs/smoke.txt)); A1's form check PASS at 12:34:27 |
| 12:34:34–13:01:59 | the queue: B A B A B A B A B B, every block rc 0, B blocks 177–178 s, A blocks 133–134 s; all ten fit the 1,740 s budget (1,700 s used) |
| 13:01:59 | the session-end `ettelem config` read; `et-who`: no holder (and again at 13:02:18) |
| 13:02:59 | the release: the post then held only this card's clause, so ` — released` was appended, every word kept |

Highest readings: board 32.55 W (stop 65 W), die 55 °C (stop 70 °C); the die read 51 °C at the first block's start and 52–55 °C after
*(corrected after verification, [C5](#corrections-after-verification-mon-2-nov-2026): "53–55 °C"; the telemetry's die reads 52 °C in
13020, 13011, 13021, 13012 and 13022, [`corrections_e130.txt`](corrections_e130.txt) [C])*.

## Departures

- **A4, the second session** (dated, before any data): the first session ran nothing, so this session is E130's only one, with the
  whole budget and every block number used once (the registration's README, Amendments).
- **The collector's interpreter.** The registration's run steps say `PY=python3`; the desk's system Python has no numpy, so
  `collect_e130.sh` ran with `PY` pointing at Python 3.14.10 with numpy 2.5.4 through `uv` (the registered code unchanged; the box's
  venv has numpy 1.26.4). It ran from the repository root with the raw root `docs/reports/data/2026-11-02-e130-int8-netlists/aifoundry3`,
  so the reductions name the raw blocks repository-relative (E127's correction C1).
- **Disclosed, no departure:** `delete_msg.mjs --plan`'s `text` field (the post's source as the client holds it) lagged both saved
  edits for at least a minute, while its rendered text and `edit_replace.mjs`'s "saved" line showed them; each edit's dry run opened
  on the expected text.

## What this cannot say

One card, one clock (aifoundry3 card 0, 600 MHz), one session of ten blocks. The netlists are Q133(a)'s, an open 7 nm library from
the public RTL's later revision, at zero delay; the ET-SoC-1's own multiplier is not public, so a verdict says which of these four
structures the card's single bits follow, not what the silicon's netlist is. `booth` and `booth_tree` are not separable here. k is a
fitting constant: levels carry it and the merge, and the A sign step, a difference of two levels, carries it too. A train's step has
no temperature term: an item's self-heating inside its window is in its step (the registration's bound, about 0.12 W on a 5 W step;
these steps are at most 3.5 W). The board is the
primary; the rail is an arm and lags the board by about 1 s. B's precision here, ±22.8 fJ on its odd − even, cannot tell Booth on B
from no recoder at the card's amplitude; a finer B list (more blocks, or the rail as a registered primary) would. A rail primary needs
its own rail-footed thresholds, or a registered rail-per-board scale, since its fJ are not the netlists' board fJ *(added after
verification, [C1](#corrections-after-verification-mon-2-nov-2026))*.

## Corrections after verification (Mon 2 Nov 2026)

An independent verifier read the registration and its four amendments, this data, the logs, the source of the box's `ettelem` binary
and the firmware handlers the nine commands reach at `836a4ab`, the same afternoon. It recomputed every primary and rail statistic
from [`runs.csv`](runs.csv) with its own code (B odd − even +33.84 [+11.02, +56.67], A odd − even −1.67 [−6.57, +3.22], the A sign
step +67.83 [+58.84, +76.82], the five Fieller ratios to 1e-12), the R4 group logic, R5, R6 and E130-N, and checked all 160 frozen
predictions against Q136(a)'s `d64ea98c`. The write lens passes: nine READs and no write (`since_reset_ms` −1 in all 16,091 samples;
the checker GO at `d1218f6e` with A1's exception and NO-GO without it on `lib.sh:154` only; the box's lab helpers byte-identical to
`tools/lab/*`; no drain, STOP file or heater run). A4 was on origin/main before the claim and the smoke, the box ran the committed code,
and the day's one card post was rewritten and released by the one-post rule. Its one nit, not a fault: § Device commands sent and the
registration cite each getter in `thermal_pwr_mgmt.c` and skip the handler hop in `thermal_power_monitor.c`; every class stands. What
it found is wording, here and in the lane's own result: C1–C5. They are made above as marked edits and dated notes. The registration
([`tools/claims-v3/e130/README.md`](../../../../tools/claims-v3/e130/README.md)), the scorer's outputs ([`results.md`](results.md),
[`scored.json`](scored.json)), [`posthoc_e130.txt`](posthoc_e130.txt) and every number, label and verdict are unchanged. The checks
behind them are post hoc: [`corrections_e130.py`](corrections_e130.py) → [`corrections_e130.txt`](corrections_e130.txt), committed
files only, with the registered `score_e130.py` and `selftest_e130.py` imported unchanged.

| | what was wrong | what changed |
|---|---|---|
| C1 | **The rail's R1 FLAT and R4 NO BOOTH were read as findings.** The registered code scores the rail arm's fJ (rail watts over the same flips and rate) against T_B and the netlists' bands, which are board fJ. § 6 called the rail's interval "wholly below T_B", and the lane's result read "NO BOOTH at the rail arm" in its headline and its R1 and R4 lines, without that caveat | Dated notes under § 1 (the rail column marked), § 3 and § 6, and a line in What this cannot say. At E78's frozen 0.81 the rail's B odd − even is +33.2 [+29.6, +36.7] board-equivalent fJ and straddles T_B, as the primary does. R1 reads FLAT there only at a scale of 0.970 or more and RECODED at 0.780 or less, so R4 can read any of the three outcomes. B's own rail/board ratio, 1.128 [0.883, 1.603], cannot pin the scale. The unit-free B odd ÷ even, 1.79 [1.68, 1.92], fits neither group. The rail's E130-N does not rest on the unit: no netlist survives at any scale from 0.1 to 30, and B's odd − even alone excludes all four bands from 0.54 to 19.5. A follow-up that registers the rail needs rail-footed thresholds ([A]). The registered labels stand |
| C2 | **The sign bits' base words.** The lane's result said "a sign bit's price belongs to the bit, not the word" as if it held for any sign bit, and cited `posthoc_e130.txt` § 3 for E79's 152 fJ, which is not there. It holds for A's sign bit with B held at 1. § 6 and What it changes gave the netlists' A sign at "1.5–1.9×" the card's | § 6's sign bullet adds the held operands, `a1d_7`'s 224.5 fJ with B = 0x55, and B's sign bit at its two words: 0.57 [0.05, 1.30] on the board, and 0.61 [0.49, 0.75] on the rail, which excludes 1. It also adds E79's +16.8, and names the source of E79's two figures, `predictions-e130.json` › `card_precision_e79`. The ratio is 1.4–1.9×, because `booth_swap`'s 228–230 fJ is 1.43–1.45× the card's ([D]) |
| C3 | **The noise was set against the plan unlike for like.** § 5 compared the zeros' scatter about their neighbours' line (0.040 W) with the planning per-run σ (0.025 W), which makes the shortfall look like 1.6×. It also gave the self-test's 0.035 W medians as 12.6–14.4 fJ; over its five worlds they are 12.3–14.4 | In the self-test's own model the scatter reads 0.033 W at σ = 0.025 W. So the session's σ was about 0.030 W, 1.2× the plan's, and 0.025–0.038 W fits (500 sessions a σ over the five worlds, [B]; the verifier's 20 sessions in one world gave 0.032 W). B's ±22.8 fJ is about twice the model's 10.4–11.6 fJ at 0.030 W. Post hoc, most of it is block 13010: without it, ±9.7 fJ over five blocks |
| C4 | **The scope of "every netlist excluded", and the 2.4×.** "Each of the four netlists misses at least one" is the registered primary's reading, and that of three of the four arms. At the dips-kept arm, `booth` and `booth_tree` survive. The proposed kinds-page text gave B's 2.4× with no interval | The plain-words paragraph, What it changes and the proposed text now name the primary and the dips-kept arm. They give the difference's interval, +33.8 [+11.0, +56.7] fJ, and the ratio's own, [1.26, 38.2] ([E]). The lane's result gets the same scope in its blog points, "1.43 times as much" for "1.43× more", and "with B held at 1" on the A prices |
| C5 | **The die after the first block** read 52–55 °C, not 53–55 °C | How it ran and § 6 ([C]) |

## Files

- [`results.md`](results.md), [`scored.json`](scored.json), [`score.log`](score.log): `score_e130.py`'s verdicts, statistics, netlists
  and items, primary and arms.
- [`e130.json`](e130.json), [`runs.csv`](runs.csv), [`reduce.txt`](reduce.txt), [`reduce.log`](reduce.log): E78's reduction, unchanged,
  on the primary (dips removed); `e130-dipskept.*`, `runs-dipskept.csv`, `reduce-dipskept.*` and `e130-gatesoff.*`,
  `runs-gatesoff.csv`, `reduce-gatesoff.*`: the two registered arms.
- [`code.sha256`](code.sha256): the code and tiles the collector ran.
- [`posthoc_e130.py`](posthoc_e130.py), [`posthoc_e130.txt`](posthoc_e130.txt): § 6, post hoc.
- `aifoundry3/kinds/p130<nn>/`: each block's raw data (block.json, configs, plan, marks, runs, the telemetry, the dumped tiles, the
  config reads, the manifest, the code hashes); `aifoundry3/kinds/kinds-smoke-p13001/`: the smoke.
- `logs/`: the queue log, the session reads, the dry runs, the binaries' hashes, the box setup and smoke output, the checker's two
  outputs, A1's form check, the post-session look and [`push-and-claim-times.txt`](logs/push-and-claim-times.txt).
- Added by the corrections after verification: [`corrections_e130.py`](corrections_e130.py) (post hoc; committed files only; it imports
  the registered `score_e130.py` and `selftest_e130.py` unchanged) and its output [`corrections_e130.txt`](corrections_e130.txt).
