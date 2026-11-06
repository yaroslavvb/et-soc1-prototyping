# Q148(c): M10's constant-lane term, frozen before E178 - a level per float format for tiles whose lanes each hold a constant word reads +0.035 W in fp32 (95% −0.053 to +0.124, jackknife over 32 runs) and +0.070 W in fp16 (+0.024 to +0.116, 13 runs) on aifoundry3; on aifoundry3 alone the fp32 kinds read +0.110 W (+0.098 to +0.122); E178's 27 float one-number kinds are forecast at P + L, a REPORTED arm scored after E178's data, never one of its rules

*On the kinds page, [section 11, what is still open](https://spacesheep.dev/@yaroslavvb/horace-kinds-of-numbers#11-what-is-still-open):
**item 6**, a power model across kinds. It answers critic-q145b's `next` rank 5 and its answer: post hoc, M10 misses by about +0.07 W on
tiles whose lanes each hold a constant word, flipping bit or not, and the old single-bit lists cannot see that level. The owner's goal,
in his words of 2 November 2026: to predict the power requirement and heat generation of numeric computations as accurately as
possible.*

*Fri 6 Nov 2026 (week 45), 05:13-05:50 PST, on the Intel, desk only: no card, no lab box, no device command, no bench sweep, no post,
no Modal. **Registered first:** [`REGISTRATION.md`](REGISTRATION.md) (`c71fbc7f`, 05:27:58 PST), before any level, forecast or tie
residual existed; then the code and its self-test with the registration's [dated note 1](REGISTRATION.md.dated-note-1.md)
(`413d252b`, before the first fit run); then the fit, run at 05:34:53 PST, and this directory's outputs, committed together with this
README. **No E178 datum exists at any of these commits** (`git log --all` shows no `docs/reports/data/*e178*`), and nothing under
`tools/claims-v3/e178/` is written. Python ran through the round's local slot, one job at a time, one core (the fit 13 s).*

**Labels.** The levels are fitted on committed rows. **Every held-out figure is post hoc**: the reading came from M10's part of these
rows, and leaving one run out does not make them blind. The E178 forecasts are **frozen**, a **reported arm**. The power is design
arithmetic. The single-bit and pool-8 readings are **post hoc**, on rows the term never fits. **Nothing here is blind; the first blind
test is E178's float kinds.**

## Results

**1. The term, frozen** (primary K: each kind's mean miss, then the mean over kinds, rows of M10's own T_S zeros plus the built-in pi tie
in 32 sessions, both cards pooled; the level in J per op, carried by the session's scale, the card term and the rate as M10's prices are;
[`termc-fit.json`](termc-fit.json) › `levels.primary_K`):

| format | rows / runs / kinds (one word) | λ, pJ per op | L on aifoundry3, W [95%, jackknife over runs] | beside: run bootstrap | L on card 1, W | σ_C, W |
|---|---|---:|---|---|---:|---:|
| fp32 | 50 / 32 / 6 | +31.7 | **+0.0354 [−0.0533, +0.1241]** | [−0.0053, +0.0986] | +0.0340 | 0.094 |
| fp16 | 16 / 13 / 5 | +62.9 | **+0.0703 [+0.0241, +0.1164]** | [+0.0450, +0.0993] | +0.0676 | 0.055 |

- **fp32's interval holds 0; fp16's does not.** Five runs each move fp32's level by about ±0.02 W when left out (E78, E82, E93, E102,
  E121: the runs that hold the kinds measured once or twice, `neg_ones`, `aq`, `nz_both`, `dn1_both`).
- **Eight lane words** (E102 only, in sample, never held out): fp32 +53.2, fp16 +110.6 pJ per op. It enters nothing (registration § 4 (iv)).
- **The kinds behind it** (M10's mean held-out miss per kind, W; `kinds`):

| kind | format | rows | aifoundry3 | card 1 |
|---|---|---:|---:|---:|
| `pi` (the tie, 32 sessions, and `fp32.pi`) | fp32 | 34 | +0.111 (16) | +0.055 (18) |
| `ones` | fp32 | 9 | +0.103 (4) | +0.055 (5) |
| `neg_ones` | fp32 | 2 | +0.112 | −0.111 |
| `dn1_both` | fp32 | 2 | +0.142 | −0.016 |
| `nz_both` | fp32 | 2 | +0.087 | +0.001 |
| `aq` | fp32 | 1 | | −0.049 |
| `ones` | fp16 | 10 | +0.110 (4) | +0.063 (6) |
| `neg_ones` | fp16 | 2 | +0.095 | +0.041 |
| `nz_both` | fp16 | 2 | +0.039 | +0.090 |
| `c_cancel` | fp16 | 1 | | +0.117 |
| `aq` | fp16 | 1 | | +0.013 |

- **The card split, post hoc.** On aifoundry3 every constant-lane kind reads +0.04 to +0.14 W above M10. On card 1 the fp32 kinds
  spread from −0.11 to +0.06 W. So the reported per-card arm (K-card) reads **fp32 +0.110 W [+0.098, +0.122]** on aifoundry3 (15 runs)
  and −0.011 W [−0.058, +0.037] on card 1 (17 runs); fp16 +0.081 [+0.014, +0.148] and +0.064 [+0.017, +0.111]. The arm R (the post hoc
  reading's construction, M10's rows only, each row equal) reads fp32 +0.063 and fp16 +0.077 W; its check reproduces the reading's
  +0.069 W over the 34 rows exactly.
- **M10 as frozen is in sample for the kind pi** (two of its rows): its held-out and in-sample misses there differ by +0.0023 and +0.0022 W.

**2. Held out by run, post hoc** (each run's rows predicted by the level fitted without that run; rms with the bias in brackets, W;
`heldout_posthoc`):

| rows | M10 | M10 + the level (primary K) | M10 + the per-card level (arm) |
|---|---|---|---|
| fp32, one word, all 50 | 0.097 (+0.073) | 0.079 (+0.037); kind-weighted 0.088 → 0.094 | |
| fp32, aifoundry3, 23 | 0.117 (+0.110) | 0.090 (+0.081) | **0.039 (−0.001)** |
| fp32, card 1, 27 | 0.076 (+0.041) | 0.069 (−0.000) | 0.082 (+0.048) |
| fp16, one word, all 16 | 0.096 (+0.076) | **0.062 (+0.007)**; kind-weighted 0.084 → 0.055 | |
| fp16, aifoundry3, 6 | 0.106 (+0.096) | 0.056 (+0.027) | 0.059 (+0.015) |
| fp16, card 1, 10 | 0.089 (+0.064) | 0.065 (−0.005) | 0.067 (−0.001) |
| the tie alone, 32 | 0.097 (+0.078) | 0.074 (+0.043) | |
| eight lane words, 3 (through the fallback) | fp32 0.071 (+0.058), fp16 0.120 | fp32 0.041 (+0.006), fp16 0.038 | |

**3. The frozen forecasts for E178's 27 float one-number kinds, a REPORTED arm** ([`forecast-m10c-e178.txt`](forecast-m10c-e178.txt),
[`forecast-m10c-e178.json`](forecast-m10c-e178.json)): each kind's **P + L**, P E178's registered `P_w` (s = 1, E171's zeros rate). Every
fp32 kind gets the same L, as does every fp16 kind, so the forecasts keep E178's own order and differences.

| card | fp32 (14 kinds): P + L, W | fp16 (13 kinds): P + L, W | the kind's 95% predictive half-width |
|---|---|---|---|
| aifoundry3 (E178's card) | 8.1920 (`e178_uf`) to 8.2843 (the crosses); L +0.0354 | 8.2932 (0.5) to 8.3146 (1.5, 6); L +0.0703 | fp32 ±0.185, fp16 ±0.108 |
| card 1 (its fallback) | 7.8774 to 7.9662; L +0.0340 | 7.9748 to 7.9954; L +0.0676 | the same |

- The per-card arm's forecasts sit beside (aifoundry3: fp32 P + 0.110, fp16 P + 0.081 W), and arm R's.
- **How it is scored, after E178's data** (registration § 5-6; `termc.py score --scored <E178 scored.json> --fit termc-fit.json`): for
  each fp32 and fp16 kind E178 keeps (C all PASS, a D in 2 or more kept passes), x = D_w − P_w from E178's own `scored.json` (P at the
  session's s and measured rate) and x' = x − (P_w / P) × L. **C1:** rms(x') − rms(x) ≤ −0.010 W with its 95% bootstrap interval over
  kinds below 0 reads BETTER. **C2:** the same sign in fp32 and in fp16. If both hold, the term enters M10 as M10-C for the next blind
  pool's constant-lane tiles; otherwise it stays a reported arm. Reported beside: each format's mean x with its interval, against L.
- **E178's registration, notes A1-A3, kit, scorer, rules, forecasts, plan, stops and card-minutes are unchanged.** No E178 verdict reads
  this arm.

**4. The entry rule's power** (design arithmetic, aifoundry3's L and σ_C, 2,000 draws a case; `power`):

| truth | no common miss | 0.02 W common | 0.04 W common |
|---|---|---|---|
| the level is right: enters | 0.56 | 0.49 | 0.53 |
| half the level: enters / WORSE | 0.04 / 0.04 | 0.16 / 0.14 | 0.26 / 0.28 |
| no level: enters / WORSE | 0.001 / 0.59 | 0.009 / 0.54 | 0.10 / 0.50 |

E178 rarely admits a wrong term (at most 0.10) and admits a right one about half the time: fp32's L (+0.035 W) is small beside its
σ_C (0.094 W).

**5. Post hoc, not fit rows: tiles with a flipping bit** (`posthoc_single_bit`, [`posthoc-classs-n1.txt`](posthoc-classs-n1.txt)):

| rows | M10, rms (bias), W | with the one-word level |
|---|---|---|
| **pool 8's class S, 8 N1 tiles, aifoundry3 (E171)** | 0.273 (+0.195), reproduced | **0.235 (+0.142)** |
| **pool 8's class S, 8 N1 tiles, card 1 (E172)** | 0.238 (+0.138), reproduced | **0.212 (+0.087)** |
| pool 8's 12 single-bit tiles on one base word, aifoundry3 / card 1 | 0.281 (+0.138) / 0.228 (+0.121) | 0.254 (+0.088) / 0.206 (+0.073) |
| M10's single-bit rows on one base word, fp32 17 / fp16 6 | 0.273 (+0.096) / 0.175 (+0.105) | 0.262 (+0.061) / 0.144 (+0.036) |
| M10's single-bit rows on eight base words (E102, E127), fp32 8 / fp16 3 | 0.207 (+0.006) / 0.020 (+0.015) | 0.211 (−0.047) / 0.068 (−0.067) |

So the constant-lane level carries about a quarter of class S's bias on aifoundry3 and a third on card 1; the rest is the bit's own step
(and A's word), the class-S term's other part. On eight base words the level over-corrects. E147's rows are left out: they are steps over a
constant-lane zero, where a level cancels (dated note 1, item 4).

## What this changes for predicting power

- **Nothing blind yet.** M10 stays as frozen. The term is registered, fitted and frozen with its forecasts before E178's first datum, and
  E178's float kinds (constant-lane tiles every one, none measured before) are its first blind test.
- **What it predicts for E178:** the floats read above M10's P by about +0.035 W (fp32) and +0.070 W (fp16) on aifoundry3. If the card
  split seen post hoc holds, aifoundry3's fp32 kinds read nearer +0.11 W, the per-card arm's forecast. The rule reads the primary only.
- **For class S** (the largest blind miss): post hoc, a constant-lane level takes about 0.05 W off its bias; the bit's own step remains,
  and needs the class-S term registered with it and a one-base-word single-bit list (critic-q145b's rank 5).

## What this cannot say

- **Post hoc throughout, except the forecasts:** these rows produced the reading; holding out a run does not make them blind.
- **Few kinds:** six fp32 and five fp16. The tie is one kind (pi), measured in 32 sessions; kinds measured once or twice set fp32's
  interval. A level that differs by word is carried by σ_C, not modelled.
- **The card split is not modelled by the primary:** registered as one level per format, the primary pools two cards whose fp32 kinds
  disagree (post hoc). Only the arm reads them apart, and the rule does not read the arm.
- **A level against a price, and against the session scale:** a level common to every constant-lane tile cannot be told here from a
  missed share of a price they all carry (most of their 8.2 W is M10's live-lane and clock terms) or from the session scale (read from
  random anchors) not carrying to constant-lane tiles.
- **Mechanism:** not resolved (registration § 1). **Scope:** M10's registered footing, 600 MHz, fp32 and fp16 only.
- **E178 is one session on one card;** the other card's first test is the next blind pool.

## Registered, and what happened

- **As registered:** T_S by bytes, the rows (a) and (b), ρ in J per op, the kind-weighted level per format and class with the fallback,
  leave one run out, the jackknife interval with the run bootstrap beside, σ_C, the two arms, the frozen forecasts, the entry rule and its
  scorer, the power, the post hoc readings. The checks first: the classing reproduces posthoc-structure.json row for row; `d600`
  reproduces `fp32.pi`'s two rows and E178's 54 frozen float P values exactly; the tiles and the tie's bytes; the scorer on synthetic
  sessions (self-test 7 of 7). The fit re-ran byte for byte into a scratch directory.
- **Departures** ([dated note 1](REGISTRATION.md.dated-note-1.md)): the registration's header times were written ahead of time (true:
  written 05:22-05:27:40, committed 05:27:58 PST); E178's dated note A3 (`77768027`) landed before it, unread, and changes no field the arm
  reads; the session scale is M10's rule computed exactly; E147's step rows are left out of the single-bit reading. Added after the fit,
  post hoc and labelled: `posthoc_classs_n1.py` (class S's 8 N1 tiles a card, which the 12-tile reading of § 8 contains).

## Files

| file | what |
|---|---|
| [`REGISTRATION.md`](REGISTRATION.md), [`REGISTRATION.md.dated-note-1.md`](REGISTRATION.md.dated-note-1.md) | the registration and its note |
| [`termc.py`](termc.py), [`selftest-termc.txt`](selftest-termc.txt) | the code (`selftest`, `fit`, `score`) and its self-test |
| [`termc-fit.json`](termc-fit.json), [`termc-fit.txt`](termc-fit.txt) | every row (with e, ρ, the held-out level and e'), the kinds, the levels and arms with intervals, the held-out readings, the post hoc readings, the power, the forecasts, the inputs' sha256 |
| [`forecast-m10c-e178.json`](forecast-m10c-e178.json), [`forecast-m10c-e178.txt`](forecast-m10c-e178.txt) | the frozen forecasts for E178's 27 float kinds, both cards, with the arms |
| [`posthoc_classs_n1.py`](posthoc_classs_n1.py), [`posthoc-classs-n1.txt`](posthoc-classs-n1.txt) | pool 8's class S with the level, post hoc |
| [`SHA256SUMS`](SHA256SUMS) | this directory's files |

## Re-run

From the top of the tree, numpy 1.26 (the Intel's `/usr/bin/python3`), one core, about 15 s:
`python3 -B tools/claims-v3/m10-c/termc.py selftest`; `python3 -B tools/claims-v3/m10-c/termc.py fit --out <dir>` (writes the four
outputs, byte for byte these); `python3 -B tools/claims-v3/m10-c/posthoc_classs_n1.py`; `shasum -a 256 -c tools/claims-v3/m10-c/SHA256SUMS`.

SPDX-License-Identifier: Apache-2.0
