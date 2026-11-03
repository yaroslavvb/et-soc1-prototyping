# Q139(u): one reduction footing for M7's training rows and every blind test, M7u refitted on it, E140-E142 re-scored (post hoc)

*Tue 3 Nov 2026 (week 45), 03:55-04:32 PST (C5), on the Intel; corrected after an independent verification, § Corrections
after verification. Desk only: no card, no ssh, no Modal. It answers Q138's final
critic's open **rank 1** (the kinds page's [section 11](https://spacesheep.dev/@yaroslavvb/horace-kinds-of-numbers#11-what-is-still-open),
**item 6**, the power model) and the desk part of **rank 5** (E142's registered X1/X2 card-term rules scored on one footing).
The footing rule, [`FOOTING-RULE.md`](FOOTING-RULE.md), was committed and pushed (`d4c36bfe`, 04:02 PST) before any row,
pass or reduced value was read. Everything after it is **post hoc**: no frozen model, prediction, band or verdict of any
earlier lane changes, and no number here is a blind result.*

## Corrections after verification (dated note, Tue 3 Nov 2026, about 06:10 PST; post hoc)

An independent verifier re-derived every number of `d4c36bfe`, `f47669d1` and `97b2843d` (all 44 committed JSONs reproduce
with no numeric difference) and found one fault in a reading and four in the reporting. Each note below rests on
[`fix_checks.py`](fix_checks.py) → [`fix-checks.json`](fix-checks.json) (and C1's example on [`fix_trace.py`](fix_trace.py)
→ [`fix-trace.txt`](fix-trace.txt)), run on committed files only. **No frozen file,
slope, reduction, fit, prediction, score or verdict changed**: `FOOTING-RULE.md`, `footing.json`, `reduced/`,
`rows-m7u.json`, `m7u.json`, `scores-m7u.json`, `score/`, `checks-footing.json`, `e143-nodips.json` and
`sens-footing.json` are as committed. Sentences corrected in place below are marked *(C1)* to *(C5)*.

- **C1 (major): on aifoundry2, A2's "dips" are the governor's own low-voltage phases, not a held meter reading, so its
  committed dips-kept reduction is its one footing.** The README said "aifoundry2 is not yet on one footing" and that M8
  "needs E80/E83 re-reduced with A2"; both are withdrawn. Its last line, "remove A2's dips from training and test alike,
  or from neither", which M8's registration quotes in choosing neither, now says to keep them in both. E82 A2 was
  written for card 1's board reading landing in the
  1-2 ms gap between two launches and being held for one SP pass, with the minion rail not moving (E82's README, "Card 1's
  board meter and the launch gaps"). On aifoundry2's governed bursts the dips are something else. In E143's scored
  session, 449 of the 480 dips sit at a level of 55 W or more (the lower of A2's two reference samples). There, 98.4% of
  them have a sampled clock and set-point change within ±2 samples (36.8% of the other samples at that level). The SP's
  own clock reading, which is refreshed together with the board reading, is lower at the dip than at one of A2's
  reference samples in 97.8% of them (4.0% of the others). And the SP's minion rail falls with them: the lowest of
  samples i to i+3 less sample i−2 has a median of −2.33 W, against +0.73 W. Matched to the samples A2 keeps within 8
  samples in the same trace at the same SP clock and voltage reading, the 199 dips that have such samples read a median
  −0.03 W from them, and 79% are within ±3 W. Yet they sit a median 14.4 W below A2's reference samples. So the board
  reading is the level of the governor's state at that moment. One trace (`BURST-11-b5-fp32.anchor_randn-r1`, samples
  36-98; [`fix-trace.txt`](fix-trace.txt)) shows it. The board reads a median 84.2 W while the SP reports 800 MHz at
  616 mV, 66.0 W at 700 MHz and 567 mV,
  and 49.9 W at 600 MHz and 517 mV. Its eight dips at the 600 MHz reading read 51.2-51.9 W, the level of that state.
  A2 removes the 600 MHz phase whenever it lasts two readings or fewer. (The trace's two dips at the 800 MHz reading,
  39.6 W, are of the other kind, below.) On the 600 MHz cards the dips are
  card 1's held reading: none of E141's 48 or E142's 68 dips has a clock or set-point change, the rail does not fall
  (+0.61 and +0.26 W), and matched the same way they read a median 11.0 and 7.8 W below the kept samples of their own
  state, none of them within ±3 W. Removing A2's dips from E143 lifts the 19 governed tiles' mean board power from
  66.43 W to 68.89 W (+2.46 W; the three governed session-link cells +2.59 W), past M7's cap W* of 65.58 W, while the 17
  pinned tiles move +0.06 W. That is why W1 fails under A2 (1.60 → 4.11 W rms), and it is not a footing mismatch. E80's
  and E83's governed bursts move the same way under A2: +2.30 W and +3.06 W on average over their 14 and 24 governed
  bursts, in kspeed's burst window. So **A2 holds on the two 600 MHz cards only. On aifoundry2, E80, E83, E143 and pool
  6's E160 keep the committed kspeed reductions, dips kept** (`FOOTING-RULE.md` F4: "That is already one footing"). M8
  (`122da8b6`) kept them, which is this footing. A launch-gap reading on aifoundry2 is not excluded for a few dips: the 24
  of E143's 199 matched dips that are at the SP's 800 MHz reading sit a median 13.0 W below their state's kept samples,
  and 20 of the 480 have no clock or set-point change within ±2 samples. Dropping only those needs a registered arm (only the
  dips that read below their own state's kept samples, or only those with no clock or set-point change). None is run
  here. Together they are at most 44 samples, against 5,803 in E143's burst windows.
- **C2 (minor): pool 4's figures, by registered rule.** "Floats 0.419 → 0.212 W, bias −0.306 → −0.024 W; int8 0.370 →
  0.314 W" are over all 18 float and all 7 int8 tiles (priorities 1 and 2). The registered rules read: **P1**, the 14
  priority-1 float tiles, 0.406 → 0.234 W, its bias −0.290 → −0.017 W; **P2**, the 6 priority-1 int8 tiles,
  0.384 → 0.333 W; **P3** 19 → 23 of 25. Both sets are now quoted, labelled.
- **C3 (minor): the card term's own interval.** X1's FAIL stands: its rule tests the point term against the measured
  ratio's interval. But M7u's C0 float term has a sampling interval of its own, **0.9616 [0.9600, 0.9629]** (a
  bootstrap over its 33 E78/E82 kind pairs, 20,000 draws), and it overlaps the ratio's [0.9626, 0.9667]. The int8 term's
  is 0.9616 [0.9565, 0.9672] over 13 pairs. M7's own float term, on M7's rows, is 0.9711 [0.9685, 0.9737]; the committed
  ratio, 0.9821 [0.9796, 0.9955], does not overlap it, so X1's earlier FAIL stands on either reading. Across the slope
  grid the term sits **0.0003-0.0012** below the ratio's interval (0.0014-0.0024 below its median), not "0.0010-0.0025".
  The slopes move the
  term and the ratio together, so the eight per-card arms are not independent evidence. "A 0.2% systematic" is withdrawn:
  a card-term miss on one footing is not resolved.
- **C4 (minor): post hoc labels, card 1's frozen FAIL, and the slope's value.** Pool 5's numbers here are post hoc: the
  footing was fitted on sessions that include E140-E142's rests, and M7u was fitted knowing the critic's reading. "Blind"
  names the pool, not this reading of it. Beside aifoundry3's +0.012 W, quote card 1's: on the same footing the frozen M7
  reads card 1 high (−0.125 W, B1 FAIL HIGH). The idle-rest slope is a fit over a narrow spread. Within each pass the rests
  span 0.33 °C (aifoundry3) and 0.36 °C (card 1), and the die reading moves in 0.1 °C steps. The reverse regression (die
  reading on board W, inverted) gives 0.45 and 0.51 W/°C, which is the bound if the error is in the die reading alone.
  E71's dedicated idle cycles read aifoundry3 at 0.32-0.38. So 0.2056 and 0.3134 are the footing, one frozen number per
  card, not a measured leakage.
- **C5 (minor): times and denominators.** `FOOTING-RULE.md`'s "written … about 04:05 PST" is wrong. It was committed at
  04:02:21 PST and pushed at 04:02:23 (origin/main's reflog); the file stays unedited, as the registration. This README's
  header said 03:55-04:50; the lane's last commit is 04:31:29. F4's "480 of 16,679 samples (69 of 123 traces)" counted the
  smoke and two stop-test sessions too. The scored session `s1` has the 480 dips in 16,134 samples, in 69 of its 117
  traces; the other three sessions hold none. "E80 6.8%, E83 3.9% of samples" are shares of every sampler line in `s1` and
  `smoke`, idle included. In `s1` alone they are 1,669 of 24,221 (6.9%) and 1,901 of 48,344 (3.9%), and inside the
  counted burst windows (kspeed's: 1.5 s after the first launch to the end of the work) 107 of 1,781 (6.0%) and 210 of
  3,755 (5.6%). F4 registered the count "in every counted burst's sampled window": that is the in-window figure (E143:
  465 of 5,803, 8.0%).
  `checks_footing.py`'s docstring promises that count and does not make it; `fix_checks.py` makes it.

## Results

| | before (each session's own footing) | after (one footing, post hoc) | source |
|---|---|---|---|
| leakage slope, aifoundry3 card 0 | 0.140-0.296 W/°C, one per session (E141: 0.2634) | **0.2056 W/°C** [0.1916, 0.2204], 2,334 idle rests in 49 passes | `footing.json` › `slopes.a3` |
| leakage slope, aifoundry1 card 1 | 0.2414 frozen, or the session's own (E88 0.315, E91 0.422) | **0.3134 W/°C** [0.2955, 0.3320], 2,700 rests in 74 passes | `footing.json` › `slopes.c1` |
| the board meter's dips | kept in 154 of M7's 247 aifoundry3 float rows, removed in 93 | removed everywhere on the two 600 MHz cards (E82 A2); on aifoundry2 kept, as committed, where they are the governor's own low phases *(C1)* | `checks-footing.json` › `passes`; `fix-checks.json` › `C1_dips` |
| **pool 5 on aifoundry3 (E141), float bias, measured − M7** | −0.230 W, **B1 FAIL HIGH** (band −0.117 to +0.085) | frozen M7: +0.012 W, B1 PASS; **M7u: −0.072 W, B1 PASS** | `scores-m7u.json` › `scores.E141_*.B1` |
| pool 5 on aifoundry3, rms fp32 / fp16 / int8 | 0.325 / 0.317 / 0.356 W | frozen M7: 0.146 / 0.149 / 0.336; M7u: 0.161 / 0.148 / 0.342 | `scores.E141_*.reported.M7.power` |
| pool 5 on aifoundry3, 30 kinds rms; inside 95% | 0.365 W; 28 of 30 | frozen M7: 0.231 W, 30 of 30; M7u: 0.241 W, 29 of 30 | `scores.E141_*.reported.M7` |
| **pool 5 on card 1 (E142), float bias** | +0.050 W, B1 PASS | frozen M7: −0.125 W, **B1 FAIL HIGH**; **M7u: −0.027 W, B1 PASS** | `scores.E142_*.B1` |
| pool 5 on card 1, rms fp32 / fp16 / int8 | 0.169 / 0.149 / 0.251 W | frozen M7: 0.165 / 0.197 / 0.261; M7u: 0.130 / 0.147 / 0.256 (30 of 30) | `scores.E142_*.reported.M7.power` |
| **card term X1 (floats): card 1 / aifoundry3, measured median ratio** | 0.9821 [0.9796, 0.9955] against M7's 0.9711: **FAIL** | 0.9635 [0.9626, 0.9667] against M7u's 0.9616: **FAIL by 0.0010** (against M7's 0.9711: FAIL); the term's own 95% interval, 0.9616 [0.9600, 0.9629], overlaps the ratio's *(C3)* | `scores.E142_*.X1`; `fix-checks.json` › `C3_card_term` |
| card term X2 (int8) | 0.9809 [0.9688, 1.0050] against 0.9735: PASS | 0.9646 [0.9510, 0.9913] against M7u's 0.9616: PASS | `scores.E142_*.X2` |
| **pool 4 (E140), M6 frozen, the registered P1 (14 priority-1 float tiles) / P2 (6 priority-1 int8 tiles) rms; P1's bias** | 0.406 / 0.384 W; −0.290 W | 0.234 / 0.333 W; −0.017 W *(C2)* | `score/scored-E140_*_frozen.json` › `primary.power.rules`; `fix-checks.json` › `C2_pool4` |
| pool 4 (E140), M6 frozen, all 18 float tiles (priorities 1 and 2) rms; bias *(C2)* | 0.419 W; −0.306 W | 0.212 W; −0.024 W | `score/scored-E140_*_frozen.json` › `primary.power.rows` |
| pool 4, M6 frozen, all 7 int8 tiles rms; bias *(C2)* | 0.370 W; −0.197 W | 0.314 W; −0.044 W | same |
| pool 4, M6 frozen, all 25 tiles inside 95% | 19 of 25 (E140-P3 FAIL) | 23 of 25 (P3 PASS) | same, `primary.power.rules.E140-P3` |
| pool 4 out of sample, M7's form (M7 nested / M7u fitted without E140's rows) | floats 0.370 W, 0.22 W high (Q138(m) README) | M7u: floats 0.201 W (fp32 0.240, fp16 0.116), bias +0.007; int8 0.233, −0.048; 25 of 25 | `scores-m7u.json` › `families.*.pool4_out_of_sample` |
| M7's form, leave one kind out on the 637 rows, floats / int8 | 0.209 / 0.240 W | 0.184 / 0.244 W (M6's form 0.190 / 0.251; M5's 0.209 / 0.253) | `families.*.loko_old_rows`, `loko_footing_rows` |
| aifoundry2 (E143), F4: A2's dips in its bursts | not looked for | 480 of the scored session `s1`'s 16,134 samples, in 69 of its 117 traces *(C5)*; removed: clock rules unchanged (F1 6.58 MHz PASS), board W1 1.60 → **4.11 W FAIL**, W3 FAIL, because there A2 removes the governor's own low phases: the 19 governed tiles' mean board power goes 66.43 → 68.89 W, past M7's 65.58 W cap, while the 17 pinned tiles move +0.06 W *(C1)*. The committed dips-kept reduction stands | `e143-nodips.json`; `fix-checks.json` › `C1_dips`, `C5_sessions` |

**The critic's decisive reading, reported either way: half of it holds.** On one footing, the blind float bias falls inside
B1's band on both 600 MHz cards with M7u (aifoundry3 −0.072 W, card 1 −0.027 W). **X1 still fails**, narrowly: the
measured float ratio is 0.9635 [0.9626, 0.9667] and M7u's card term is 0.9616, 0.0010 below the interval's low end. The
card term's miss of the median shrinks from 1.1% (0.9711 against 0.982) to 0.2%. *(C3)* That FAIL is the registered
rule's, which tests the point term against the ratio's interval. The term has a sampling interval of its own, 0.9616
[0.9600, 0.9629] over its 33 E78/E82 kind pairs, and it overlaps the ratio's, so whether the C0 term is off at all on one
footing is not resolved. The nested procedure on the new rows re-chooses the all-pairs term C1 for floats, and its
scale, 0.9596, is further out (`scores-m7u.json` › `nested_procedure_footing_rows`). *(Added 04:31 PST, § Sensitivity to the
slope: B1 holds on both cards at every slope pair scored. X1 fails at all eight per-card pairs and passes only with one
slope, 0.2056, on both cards.)* *(C3: the slopes move the term and the ratio together, so the eight arms are not
independent evidence.)*

**In plain words.** Post hoc, most of aifoundry3's float error on blind pool 5 was the reduction's footing, not the
model *(C4)*. When every row and every test is reduced the same way (one leakage slope per card, the meter's dips removed
on the two 600 MHz cards *(C1)*), the frozen M7 reads
pool 5's floats on aifoundry3 to 0.15 W (from 0.32 W), and pool 4's float bias under M6 falls from −0.31 W to −0.02 W.
Card 1's slope is higher (0.31 against the 0.24 it used), so card 1's measured watts fall by about 0.1 W per float kind. The
frozen M7, trained on the old footing, then reads card 1 high (B1 FAIL); refitted on the one footing (M7u), it reads both
cards without a float bias. int8 does not move: its 0.25-0.34 W is in the model, not the footing. M7 is still not resolved
better than M6 on any card (M1 NOT RESOLVED in every arm). On card 1 at the footing it is resolved better than M5
(M2: −0.076 W [−0.142, −0.021] for M7u; `scores.E142_footing_m7u.M2`).

## What this does to predicting power and heat

**The term corrected is the reduction, not the model:** the leakage correction (one slope per card, from idle rests
pooled over all sessions, instead of each session's in-run fit) and the meter's dips (E82 A2's rule on every pass of the
two 600 MHz cards *(C1)*). It moves
the measured D of every training row and every test row. **Out-of-sample error, before → after (post hoc):** blind pool 5
on aifoundry3, floats 0.325 / 0.317 W → 0.161 / 0.148 W (M7u) or 0.146 / 0.149 W (the frozen M7 on the re-reduced
measurements), with the float bias −0.230 W → −0.072 W (B1 FAIL → PASS); int8 0.356 → 0.342 W (unchanged within its spread).
Card 1: floats 0.169 / 0.149 → 0.130 / 0.147 W (M7u), bias +0.050 → −0.027 W, while the frozen M7 on the re-reduced card 1
reads −0.125 W (B1 FAIL HIGH) *(C4)*; int8 0.251 → 0.256 W. Pool 4 (M6 frozen), by registered rule: P1 floats 0.406 →
0.234 W, P2 int8 0.384 → 0.333 W, P3 19 → 23 of 25 (all 18 float tiles 0.419 → 0.212 W) *(C2)*. Leave one kind out on the
training rows: floats 0.209 → 0.184 W, int8 0.240 → 0.244 W. The card term: the measured float ratio moves from 0.982 to
0.9635 and M7u's term from 0.9711 to 0.9616; X1 still fails by its rule, by 0.001, inside the term's own interval
0.9616 [0.9600, 0.9629] *(C3)*. **Heat is not changed**: the window's die rise does not depend on the slope (only which
passes are kept moves it),
and no heat term was refitted. **aifoundry2 stays on its committed footing** *(C1)*: on its governed bursts A2's dips are the
governor's own low-voltage phases, not the held reading A2 was written for, so removing them from E143 (+1.43 W on average,
0 to 4.02 W) biases its board power up, which is why W1 fails under A2. E80, E83 and E143 already share one reduction with
the dips kept, and its governed-burst board error stays 1.60 W rms (W1 PASS). Pool 6 (E153, E157) is the first blind test
of the footing.

## The rule and what it gave

The rule ([`FOOTING-RULE.md`](FOOTING-RULE.md), `d4c36bfe`) chose **(a) one leakage slope per card from its idle rests**
over (b) the die temperature as a model input. In a kinds run the window's rise is set by the run's own power, so a jointly
fitted temperature term trades against every price. Idle rests carry no switching.

- **F1.** Each rest is the reducer's own 1 s idle bracket before a run, valid by its idle test, the run passing every
  per-run gate. The fit is ordinary least squares of the bracket's board W on its die reading, one intercept per pass, one
  slope per card, with a bootstrap over passes. aifoundry3 **0.2056 W/°C** [0.1916, 0.2204] (49 passes, 12 experiments,
  rests at 58.0-58.9 °C, within-pass spread 0.33 °C, residual 0.074 W). Card 1 **0.3134 W/°C** [0.2955, 0.3320] (74 passes,
  14 experiments, 55-59 °C, 0.36 °C, 0.090 W). Per experiment the within-pass slopes run 0.152-0.284 on aifoundry3 and
  0.242-0.626 on card 1 (`footing.json` › `slopes.*.by_experiment`).
- **F2.** E82 A2's rule on every pass, applied exactly once. The registered wrappers of 20 experiments (18 wrapper files,
  each with A2's 4.0 W and i ± 2) already apply it: built in for 16, as `--drop-dips` for E115, E127, E140 and E141. The six
  reducers with no dip handling (E78, E82, E86, E90, E92, E95) ran on A2-filtered copies (`reduce_footing.EXPS`,
  column 4).
- **F3.** Each experiment's registered reducer ran unchanged with `--leak k_c --no-refit`. With the dips gone, passes the
  registered reductions had set aside are kept by the same gates: E82 (+8210, 8216), E86 (+8614), E92 (+9211), E95 (+9513),
  E115 (+11510, 11511), E140 (+14010, 14011), E141 (+14110). E88, E91, E104 and E137 set aside the same pass as before; no
  experiment lost a pass, and none of the 637 rows was lost (`checks-footing.json` › `passes`; `scores-m7u.json` ›
  `rows_lost` = []).
- **D moved** (footing − M7's rows): aifoundry3 fp32 +0.063 W on average (−0.21 to +1.20), fp16 +0.040, int8 +0.037;
  card 1 fp32 −0.103, fp16 −0.113, int8 −0.040 (`scores-m7u.json` › `D_shift_footing_minus_m7_w`).
- **F4.** See the last row of the Results table and the paragraph above.

**M7u** keeps M7's forms (floats `G8_gtr_glive`, int8 `J8_b138`) and its card term (C0, E78/E82 pairs). Refitted on the 637
re-reduced rows: floats mult 1.62, add32 1.64, add16 1.57, bus 6.58, rest 2.35, clk 0.62, gtr 136 ± 19 fJ (M7: 145.5);
int8 nets 3.39, bus 16.2, clk 1.89, b138 −21.3 ± 10.1 fJ (M7: −23.4). The card-1 scale is 0.9616 floats and 0.9616 int8,
against M7's 0.9711 and 0.9735 (`m7u.json`). M7's whole nested procedure on the new rows picks the same forms; for floats it
picks the all-pairs card term (nested 0.185 W floats, 0.244 W int8).

**How pool 5 was scored**: the registered scorers (`tools/claims-v3/e141/score_e141.py`, `e142/score_e142.py`) ran
unchanged. Their inputs: (i) the committed reductions and frozen predictions, which reproduce the committed and critic's
numbers exactly (B1 −0.2303 FAIL HIGH; X1 0.9821 [0.9796, 0.9955] FAIL); (ii) the re-reduced measurements with the frozen
predictions; (iii) the re-reduced measurements with M7u's predictions in a copy of each registration (`score/reg-e14x-m7u.json`:
M7's power entries replaced, M7's frozen band half-widths kept, heat entries M7's; for E142, `model.card1_scale` set to
M7u's). B1's band is the registered interval drawn from M7's reference errors, unchanged.

## What this cannot say

- **Nothing here is blind.** The rule was fixed first, but the slope was fitted on sessions that include E140-E142's idle
  rests, and M7u was fitted knowing the critic's reading. Pool 6 on the frozen k_c is the test.
- **The slope's value is not settled physics.** The rests sit within about ±0.3 °C of each pass's launch target, and the
  die reading's noise in a 1 s mean can attenuate a slope fitted on that spread. E71's dedicated idle cycles read
  aifoundry3 at 0.3200 W/°C (52-58 °C) and 0.3803 (58-62 °C), above F1's 0.2056. One footing removes the inconsistency
  between rows. A common error in k is absorbed into the prices on a card. But the card term depends on both cards' slopes,
  so X1's verdict is a slope question as well as a model one. *(Added after the first commit: § Sensitivity to the slope
  runs it. X1 fails at every per-card combination scored and passes only with one slope on both cards.)* *(C4)* Within
  each pass the rests span 0.33 °C (aifoundry3) and 0.36 °C (card 1), and the die reading moves in 0.1 °C steps. If the
  error is in the die reading alone, the slope lies between the OLS fit and the reverse regression's (die reading on board
  W, inverted): 0.2056-0.45 W/°C on aifoundry3, 0.3134-0.51 on card 1. The frozen k_c is the footing, one number per card,
  not a measured leakage.
- **X1's interval is narrow** (±0.002: 21 tiles whose ratios agree closely on one footing), and the rule tests a point card
  term with no interval of its own. *(C3)* That term's own interval is 0.9616 [0.9600, 0.9629], wider than its gap to the
  ratio's.
- **int8 is not explained by the footing.** Its 0.24-0.34 W blind error stays, and is M8's job (E141's whole-line,
  power-law and W8A8 misses; E138/E145's per-position B prices).
- *(C1, C5)* **aifoundry2 is on one footing already** (F4: E80, E83 and E143 share one reduction, dips kept). A2's dips there
  (in `s1`, 6.9% of E80's and 3.9% of E83's sampler lines, idle included; 6.0% and 5.6% of the samples inside the counted
  burst windows) are the governor's own low phases, so A2 is not applied on aifoundry2.
- The pool-4 out-of-sample band is k × the pool rms (M7's frozen k and pools; no parameter term), because pool 4 has no
  frozen M7 prediction. Heat rules were not re-scored. Rates and features are M7's rows' own; only D, its se and dT_win
  were replaced.
- No launch's C is checked on file tiles (rank 14), here as in every earlier pool.

## Sensitivity to the slope (added 04:31 PST, after the first commit `f47669d1`; post hoc, not the rule)

[`sens_footing.py`](sens_footing.py) re-reduced each card's experiments at other slopes (A2 once, as F3) and ran
`fit_m7u.py` unchanged on each combination. It covers F1's bootstrap ends per card, aifoundry3 at E71's dedicated idle-cycle
slopes, and one slope on both cards. M7u refitted every time ([`sens-footing.json`](sens-footing.json) › `grid`):

| arm | k aifoundry3 / card 1 (W/°C) | B1 aifoundry3 (M7u) | B1 card 1 (M7u) | X1: measured ratio [95%] vs M7u's term | X2 | LOKO floats / int8 (W) | passes kept E141 / E142 |
|---|---|---|---|---|---|---|---|
| **F1 (the footing)** | 0.2056 / 0.3134 | PASS −0.072 | PASS −0.027 | 0.9635 [0.9626, 0.9667] vs 0.9616 **FAIL** | PASS | 0.184 / 0.244 | 4 / 5 |
| aifoundry3 low | 0.1916 / 0.3134 | PASS −0.072 | PASS −0.027 | 0.9619 [0.9608, 0.9651] vs 0.9599 FAIL | PASS | 0.184 / 0.243 | 4 / 5 |
| aifoundry3 high | 0.2204 / 0.3134 | PASS −0.071 | PASS −0.028 | 0.9652 [0.9644, 0.9685] vs 0.9634 FAIL | PASS | 0.184 / 0.244 | 4 / 5 |
| card 1 low | 0.2056 / 0.2955 | PASS −0.071 | PASS −0.030 | 0.9656 [0.9648, 0.9690] vs 0.9641 FAIL | PASS | 0.184 / 0.244 | 4 / 5 |
| card 1 high | 0.2056 / 0.3320 | PASS −0.073 | PASS −0.025 | 0.9613 [0.9602, 0.9644] vs 0.9590 FAIL | PASS | 0.184 / 0.244 | 4 / 5 |
| aifoundry3 low, card 1 high | 0.1916 / 0.3320 | PASS −0.073 | PASS −0.024 | 0.9597 [0.9585, 0.9627] vs 0.9573 FAIL | PASS | 0.184 / 0.243 | 4 / 5 |
| aifoundry3 high, card 1 low | 0.2204 / 0.2955 | PASS −0.070 | PASS −0.030 | 0.9674 [0.9666, 0.9708] vs 0.9659 FAIL | PASS | 0.184 / 0.244 | 4 / 5 |
| aifoundry3 at E71's 52-58 °C slope | 0.3200 / 0.3134 | PASS −0.062 | PASS −0.031 | 0.9775 [0.9763, 0.9799] vs 0.9761 FAIL | PASS | 0.185 / 0.248 | 3 / 5 |
| aifoundry3 at E71's 58-62 °C slope | 0.3803 / 0.3134 | NOT SCORED (E141 keeps 1 pass) | PASS −0.030 | NOT SCORED | NOT SCORED | 0.187 / 0.255 | 1 / 5 |
| one slope on both, 0.2056 | 0.2056 / 0.2056 | PASS −0.067 | PASS −0.030 | 0.9798 [0.9752, 0.9811] vs 0.9766 **PASS** | PASS | 0.185 / 0.245 | 4 / 4 |
| one slope on both, 0.3134 | 0.3134 / 0.3134 | PASS −0.062 | PASS −0.031 | 0.9766 [0.9755, 0.9791] vs 0.9752 FAIL | PASS | 0.185 / 0.248 | 3 / 5 |

**What it shows.** (1) **B1 is robust.** With M7u refitted, the blind float bias lies inside B1's band on both cards in
every scored arm, at −0.06 to −0.07 W on aifoundry3 and −0.02 to −0.03 W on card 1. That half of the decisive reading does
not hang on the slope. (2) **X1 is not robust, and it fails at the footing.** The measured ratio and M7u's card term move
together with the slopes, from 0.960 to 0.980. M7u's C0 term sits 0.0003-0.0012 below the low end of the ratio's interval
(0.0014-0.0024 below its median) in every failing per-card arm *(C3)*. It passes only where one slope is used on both cards
and E142 loses a pass, which widens the interval. The card term (fitted on E78's and E82's pairs) reads pool 5's median
float ratio 0.14-0.24% low on every footing tried *(C3)*. Because the slopes move the term and the ratio together, and the
gap lies inside the term's own interval (0.9616 [0.9600, 0.9629] at the footing), that is not shown to be a systematic:
rank 5's card-scale predictor should be tested against the term's interval, not its point. (3) **The fit does not care
which slope is used**: M7's
form out of kind stays at 0.184-0.187 W for floats. Higher aifoundry3 slopes (E71's) cost int8 accuracy (0.244 → 0.255 W)
and passes: at 0.38 W/°C the gates keep one of E141's four. F1's in-session slope keeps every pass.

## Files

| file | what |
|---|---|
| [`FOOTING-RULE.md`](FOOTING-RULE.md) | the rule and the analysis plan, committed first (`d4c36bfe`, 04:02 PST) |
| [`reduce_footing.py`](reduce_footing.py) | **for later lanes to import**: `drop_dips` (A2), `filtered_copy`, `reduce(exp, k, …)` (each experiment's registered reducer at slope k, A2 once), `rests_from_csv`, `fit_slope`, `EXPS` (26 experiments: data dir, card, wrapper, dip class), `K_FROZEN` (from `footing.json`) |
| [`footing.json`](footing.json) | **the frozen footing**: per card k, its bootstrap interval, rests, passes, temperature range, residual and per-experiment slopes; the dip rule; the k = 0 stage's reductions |
| [`reduced/`](reduced/) | the 26 experiments re-reduced at the footing (`<exp>-footing.json`, each reducer's own output format) |
| [`rows-m7u.json`](rows-m7u.json) | M7's 637 rows with D, D_se and dT_win at the footing (`D_m7`, `dT_win_m7` keep M7's) |
| [`fit_m7u.py`](fit_m7u.py), [`m7u.json`](m7u.json), [`scores-m7u.json`](scores-m7u.json), [`fit-m7u-output.txt`](fit-m7u-output.txt) | M7u, its leave-one-kind-out scores beside M5's and M6's forms on the old and new rows, pool 4 out of sample, the scorer arms, the nested procedure on the new rows |
| [`score/`](score/) | the registered scorers' outputs for every arm, and the two registration copies carrying M7u's predictions |
| [`checks_footing.py`](checks_footing.py), [`checks-footing.json`](checks-footing.json) | E140's registered scorer on both footings, A2's dips on aifoundry2 (E143, E80, E83), the passes kept per experiment |
| [`e143_dips.py`](e143_dips.py), [`e143-nodips.json`](e143-nodips.json) | F4: E143's registered reduction on its traces with A2's dips removed, beside the committed results |
| [`sens_footing.py`](sens_footing.py), [`sens-footing.json`](sens-footing.json) | *(added 04:31 PST)* the slope sensitivity: eleven slope pairs, M7u refitted on each, B1/X1/X2 and the passes kept |
| [`fix_checks.py`](fix_checks.py), [`fix-checks.json`](fix-checks.json) | *(added after verification)* the checks behind the dated notes C1-C5: what A2's dips are on each card, E143 reduced with them removed cell by cell, the dips inside the counted burst windows, pool 4 by registered rule, the C0 term's own interval and X1's gaps across the grid, the rests' errors-in-variables bracket, F4's denominators per session |
| [`fix_trace.py`](fix_trace.py), [`fix-trace.txt`](fix-trace.txt) | *(added after verification)* C1's example: one governed E143 burst's board reading by the SP's clock and voltage reading, dips against kept samples |

Rerun from the top of the repository, with a python that has numpy (each step takes seconds; `fix_checks.py` about 20
minutes):

```
python3 docs/reports/data/2026-11-03-q139u-footing/reduce_footing.py rests  <scratch>   # stage A: k = 0, rests, footing.json
python3 docs/reports/data/2026-11-03-q139u-footing/reduce_footing.py reduce <scratch>   # stage B: reduced/<exp>-footing.json
python3 docs/reports/data/2026-11-03-q139u-footing/fit_m7u.py <scratch> > docs/reports/data/2026-11-03-q139u-footing/fit-m7u-output.txt
python3 docs/reports/data/2026-11-03-q139u-footing/checks_footing.py
python3 docs/reports/data/2026-11-03-q139u-footing/e143_dips.py <scratch>
python3 docs/reports/data/2026-11-03-q139u-footing/fix_checks.py <scratch>   # after verification: the checks behind C1-C5, fix-checks.json
python3 docs/reports/data/2026-11-03-q139u-footing/fix_trace.py > docs/reports/data/2026-11-03-q139u-footing/fix-trace.txt
```

The committed JSONs have the Intel's absolute paths replaced by tree-relative ones (the reducers record their input
directories; the A2-filtered copies are named `<A2-filtered copy (reduce_footing.filtered_copy)>/…`).

**For later lanes (pool 6 on aifoundry3 and card 1):** `import reduce_footing as RF`, then reduce each pass with A2
applied once and `--leak RF.K_FROZEN[card]` (0.2056 aifoundry3, 0.3134 card 1). Never refit k on a new session. *(C1)* For
aifoundry2's governed bursts (E80, E83, E143, and pool 6's E160), keep A2's dips in training and test alike: the committed
kspeed reductions are aifoundry2's one footing, and A2 would remove the governor's own low phases there. M8 (`122da8b6`)
does so.
