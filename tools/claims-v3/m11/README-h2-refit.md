# Q142(h2), part 2: M11's refit for (c) HC1 and (d) I8P on the committed rows. Neither enters by its registered rules

*Thu 5 Nov 2026 (week 45), PST, desk only: no card, no device command, no lab box, no post in the lab's channel, no Modal, no archive.
Written from about 10:10 PST and committed at the time git records. It comes after part 1, the HC1-B and I8P-B reader
([`README-h2-reader.md`](README-h2-reader.md), lab `21666b23`, 10:07:38 PST). **No E171-E174 data exists** in any ref or in the tree
(`git log --all` and the data directories, checked again before this commit), so this refit reads committed rows only and precedes the
two blind readings it decides for. It answers `critic-q142v2rh`'s `next` **rank 7** ("M11's refit on the committed rows, for (c) HC1
(its two-thirds clause) and (d) I8P (its spread clause), frozen with a hash list"). It is [`REGISTRATION.md`](REGISTRATION.md)
section 13 step 3 for (c) and (d); (a), heat over minutes, is decided by M11's own hold sessions and is not touched. It serves the kinds
page's [section 11](https://spacesheep.dev/@yaroslavvb/horace-kinds-of-numbers#11-what-is-still-open), items 9 and 8 (heat) and 6 (the
power model). The owner's goal, in his words of 2 November 2026: to predict the power requirement and heat generation of numeric
computations as accurately as possible.*

**Held out, not blind.** Nothing frozen changes: M10, M9, pool 8, E171-E174's registrations, REGISTRATION.md, A1 and every M11 list
stay as committed. This adds new files only.

## The result

| term | entry clause (REGISTRATION.md section 8 or 9, as numbers) | reading on the committed rows | clause |
|---|---|---|---|
| **(c) HC1**, card 1's 4.5 s heat scale | pooled: card 1's held-out rms with h₁ minus without ≤ −0.010 °C, 95% interval below 0 | −0.1123 °C [−0.1367, −0.0852] over 448 rows, 315 kinds (0.2855 → 0.1731 °C) | PASS (known since M10) |
| | **two thirds**: the difference ≤ 0 in at least ⅔ of card 1's sessions with ≥ 10 heat rows | **9 of 14** sessions; 10 needed. Worse with h₁: E102 +0.0032, E104 +0.0049, E142 +0.0031, E88 +0.0042, E93 +0.0123 °C, each with h₁ within 1.6% of 1 | **FAIL** |
| | bias: card 1's heat bias does not change sign and grow | +0.0071 → −0.0026 °C: the sign changes, the size falls | PASS (known since A1-1) |
| | **HC1** | | **DOES NOT ENTER** |
| **(d) I8P**, card 1's paired-anchor int8 term | pooled: over the paired sessions' card-1 int8 rows, held-out rms with k minus without ≤ −0.010 W, interval below 0 | +0.00036 W [−0.0142, +0.0188] over 97 rows, 83 kinds (0.1778 → 0.1781 W) | **FAIL** |
| | E164's priority-1 int8 bias falls in size and keeps its sign | −0.0811 → +0.0577 W: the sign changes | **FAIL** |
| | every card-1 int8 row's rms rises by ≤ 0.001 W | 0.18491 → 0.18522 W (+0.0003) over 108 rows | PASS |
| | **I8P** | | **DOES NOT ENTER** |

**I8P's not-wanted clauses, read where the committed rows can read them** (they cannot bring in a term that failed its entry):
- **Over-correction** ("the bias changes sign and grows"):
  - on E164's 24 int8 rows, −0.0748 → +0.0656 W: no (the size falls);
  - over the paired sessions' 97 card-1 int8 rows, −0.0029 → +0.0410 W: **yes**.
- **The spread** (A1-3, "k varies across the pairs no more than the anchors' own errors give"): the sd of k over the nine pairs is
  0.00979, against 0.00763 from the anchors' own errors (ratio 1.284). **Not met**: k varies between the pairs more than its noise.
  - The reading is the same in all 106 folds that read every anchor (ratio 1.284301 in each).
  - The held-out kind `int8.full`'s fold reads 2 pairs (ratio 1.83): also not met.
- **I8P-B WORSE**: blind, read by part 1's reader on E172 with E171.

**Reported beside, never carried:** the constant that would do, the card term × the median k over the pairs, is
0.9616 × 0.9966 = **0.9584** [0.9488, 0.9672] (a bootstrap over the pairs, 2,000 draws, seed 142). The median k's interval,
[0.9867, 1.0059], includes 1. The nine pairs' k:

| pair | anchors in both | k (all rows) | k over the folds | A1-1's preview | card-1 int8 rows |
|---|---|---:|---|---:|---:|
| E82 / E78 | `int8.full` | 0.99600 | 0.99470-0.99844 | 0.99599 | 15 |
| E91 / E86 | `int8.full` | 0.98669 | 0.98541-0.98911 | 0.98669 | 4 |
| E131 / E95 | `int8.full` | 0.99012 | 0.98883-0.99255 | 0.99011 | 12 |
| E93 / E121 | `int8.full` | 1.00588 | 1.00456-1.00834 | 1.00587 | 5 |
| E108 / E122 | `int8.full` | 0.99670 | 0.99540-0.99915 | 0.9967 | 0 |
| E94 / E123 | `int8.full` | 1.00859 | 1.00727-1.01106 | 1.00858 | 11 |
| E142 / E141 | `int8.full` | 0.99893 | 0.99762-1.00138 | 0.99892 | 9 |
| E157 / E153 | `int8.anchor6_full`, `int8.full` | 0.99664 | 0.99379-0.99908 | 0.99664 | 17 |
| E164 / E163 | `int8.anchor7_full_a`, `_b`, `int8.full` | 0.97630 | 0.97367-0.97869 | 0.9756 | 24 |

**So M11 carries neither term.** Card 1's 4.5 s heat stays M10's law, and card 1's int8 stays M10's B with its 0.9616 card term.
Part 1's blind readings on E172 (HC1-B, I8P-B) are still read on the card day and reported. By section 10's "one way only", they
cannot bring either term in. The registration's expectation for (d) ("(d) does not enter, or enters and is not wanted by
over-correction") held: it did not enter, and it over-corrects over the paired rows.

## What it does to predicting power and heat

M11's card-1 power and 4.5 s heat predictions are M10's, unchanged. The figures are held out and not blind: heat 0.2855 °C rms on card
1's 448 rows; card-1 int8 0.1849 W rms on its 108 rows. A per-session heat scale would have lowered card 1's pooled heat rms to
0.1731 °C. The registered rule asks more than the pooled gain, though: it asks for no harm in most sessions. The scale made 5 of 14
judged sessions slightly worse, each one whose own scale is within 1.6% of 1, where applying it can only add its noise. The paired int8
anchors lower no held-out error (+0.0004 W) and flip E164's bias. The next registration's candidates, named here, are a heat scale
applied only when a session's scale departs from 1 by more than its own noise, and the constant card term 0.9584 [0.9488, 0.9672]. Nothing
of either is registered here.

## How each was computed (M10's committed code, unchanged)

- **Inputs first.** M11's three lists (58, 6, 9) pass, then M10's 174 registered inputs (`fit_m10.check_inputs`), then
  `fit_m10.assemble`'s 959 rows.
- **(c)** `fit_m10.heat_c1`, unchanged. In each leave-one-kind-out fold the law is refitted, and each session's h is the median over
  its random anchors (M10 REGISTRATION section 3a's set) of dT_win / the law, the held-out kind's anchors left out.
  - Its output reproduces `heldout-m10.json` › `heat_c1` in 15 of 15 compared fields: rows, kinds, sessions, anchors, every rms and
    bias, the coefficients, the session scales, the bootstraps and the entry flag.
  - Not compared: the end-to-end block, which needs the power fits' held-out D and is not used here.
  - Per card-1 session: d = rms(held-out errors with h) − rms(without). The pooled clause is `heat_c1`'s own card-1 bootstrap (M10's
    `boot`: over kinds, 2,000 draws, seed 142).
- **(d)** `fit_m10.Fit10` on the int8 family, unchanged: M10's B, with prices and card term refitted in each fold and no session scale.
  The anchors are `fit_m10.assemble_anchors`' int8 anchors.
  - Its held-out errors equal `rows-m10.json`'s `err_w[B]` to 4.97e-7 W: that file keeps 6 decimals.
  - Its all-rows prices equal `m10.json`'s to a relative 3.2e-14, and its card term exactly.
  - k per pair in each fold: the median, over the int8 anchors run in both sessions and not of the held-out kind, of
    [D_σ / D̂_σ] / [D_ρ / D̂_ρ], with D̂ the fold's prediction of the anchor; 1 if no anchor is left (M10's rule).
  - Each paired card-1 int8 row is predicted as k × M10's fold prediction.
  - The pooled clause is M10's `boot` over kinds (2,000 draws, seed 142).

## Where the text leaves a form open: the one it implies, taken here

1. **"Each pair's k in its own fold"** (A1-3, the spread).
   - The anchor's prices cancel in k, because one tile has the same features in both sessions. So a pair's k in a fold is its all-rows
     k times the all-rows card term over the fold's, the same factor for every pair of that fold.
   - The spread's verdict is therefore read on the all-rows fit, which is where M10's own form reads its scales
     (`section7_m10.term_c1` and `term_a_noise`).
   - The same reading in every fold is reported beside: the ratio is 1.284301 in all 106 folds that read every anchor, and `int8.full`'s
     fold reads 2 pairs (1.83). The verdict is the same in every fold.
2. **The noise of k** follows M10's form (`section7_m10.median_noise` and `spread_by_card`).
   - Each anchor's D in both sessions is drawn as D + se × N(0, 1), with the model value held. The se is the anchor's D se in its
     session's footing reduction (`fit_m10.footing_items`).
   - Each pair's k is drawn 2,000 times, and the sd taken with ddof 1. The expected sd is the rms of the pairs' sds.
   - One generator, `numpy.random.default_rng(142)`, is used for the pairs in section 9's order: each pair's card-1 draws, then its
     aifoundry3 draws.
   - A pair with an anchor lacking an se would be left out of both and named. None is.
3. **"At least two thirds"** is 3 × count ≥ 2 × n, in whole numbers.
4. **"Falls in size and keeps its sign"** is |b₁| < |b₀| and b₀ b₁ > 0. **"Changes sign and grows"** is b₀ b₁ < 0 and |b₁| > |b₀|.
5. **The reproduction bound for M10's int8 prices** is a relative 1e-9, the bound of `predict_m10`'s self-test, not bit for bit.
   `m10.json` was fitted with another machine's numpy. A first run (10:11:40-10:11:41 PST) that asked for bit equality stopped at this
   check, after printing (c)'s figures and before any (d) output. The check was then relaxed and nothing else changed.
6. **The constant's interval** is a bootstrap over the nine pairs. Each draw takes nine pairs with replacement from
   `numpy.random.default_rng(142)` and computes the median of their k. The interval is the 2.5% and 97.5% quantiles, as M9's
   `boot_diff`.

## Files

| file | what |
|---|---|
| [`refit_m11_cd.py`](refit_m11_cd.py) | the refit: `--out <json> --txt <txt>`; imports `fit_m10` unchanged |
| [`refit-m11-cd.json`](refit-m11-cd.json), [`refit-m11-cd.txt`](refit-m11-cd.txt) | its output: every clause, the per-session and per-pair tables, the reproduction checks, the decision. These are the frozen parameters: no new parameter is fitted, so the frozen form is M10's (`m10.json`'s law coefficients and int8 prices, by sha256) with the two decisions |
| [`SHA256SUMS-h2-refit`](SHA256SUMS-h2-refit) | this part's files, with M10's registered list of 174 inputs |

## Compute

On the Intel, desk only. Five local slot jobs ran at nice 10 on one core:
- 10:11:40-10:11:41 PST, stopped at the bit-equality check (see 5 above);
- 10:12:06 PST, the first full run, and 10:13:04-10:13:05, byte-identical to it;
- 10:14:52-10:14:54 and 10:15:04-10:15:06, after two edits to the code's docstring only: one phrase reworded for the public-text scan.
  The last is the committed output. Its log is byte-identical to the 10:12:06 run's, and so is every value in its JSON but the
  refit's own sha256.

Outside the slot there were sub-second reads of committed JSON, git, `shasum` and the public-text scan. No lab box, no remote host,
no card.

SPDX-License-Identifier: Apache-2.0
