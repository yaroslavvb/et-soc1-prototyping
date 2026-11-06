# Q145(b): term S does not enter - a per-position single-high-B-bit term fitted on the seven committed price lists cuts their own held-out error (0.222 → 0.179 W over 95 steps) but fails on card 1 and on pool 6/7's one-base-word S kinds, and post hoc it makes pool 8's class S worse on all four cards (0.273 → 0.357, 0.238 → 0.323 W at 600 MHz); the lists' single bits read 0.10 W below M10 where pool 8's read 0.14-0.20 W above it, and post hoc the miss follows one word in every lane, not the bit position; M10 on the law (the exact one-footing test): M10's lead over M9 survives on both cards (P8-M1 BETTER, -0.052 and -0.091 W)

*On the kinds page, [section 11, what is still open](https://spacesheep.dev/@yaroslavvb/horace-kinds-of-numbers#11-what-is-still-open):
**item 6**, a power model across kinds. It answers the card day critic's rank 6 (the next power term: single high B bits per position,
by format and clock, registered first and fitted nested), the stock-take's MAP step 2, and round A's owed exact test, "M10 on the law".
The owner's goal, in his words of 2 November 2026: to predict the power requirement and heat generation of numeric computations as
accurately as possible.*

*Fri 6 Nov 2026 (week 45), about 02:05-03:10 PST, on the Intel, desk only: no card, no lab box, no device command, no bench sweep, no
post, no Modal. **Registered first:** [`../../../../tools/claims-v3/m10-s/REGISTRATION.md`](../../../../tools/claims-v3/m10-s/REGISTRATION.md)
(`dfc005bf`, about 02:31 PST), before any M10 prediction or residual on a price-list row, any fit of the term, any re-reduction at the
law or any refit; then the code and its self-test (`term_s.py`, `23e23210`), then this directory, written by `term_s_v2.py` (a new file
beside it with the fixes of dated note 1), `law_m10.py` and `posthoc_structure.py`. The departures are in the registration's
[dated note 1](../../../../tools/claims-v3/m10-s/REGISTRATION.md.dated-note-1.md). Python ran on the Intel through the round's local
slot, one job at a time, one core.*

**Labels.** The price-list fit is **held out** (leave one run out). Pool 6's and pool 7's S kinds are **held out** for the term (it never
reads them). **Everything about pool 8 is post hoc:** its class-S errors were read before the registration. "M10 on the law" is **post
hoc** (pool 8 is measured; the refit is mechanical). The structure reading (§ 5) is **post hoc**, after the term's outputs. Nothing here is
blind; the first blind test of anything here is the next blind pool.

## Results

**1. The term on the price lists, held out** (95 steps in six runs: E65 37, E70 1, E79 17, E102 14 on card 1, E134 11, E147 15; 75 fp32,
20 fp16; each step = the list's registered step over its own zero, on M10's footing, less M10's frozen step from the committed three-point
counts; error = measured − predicted, W; [`term-s-reg.json`](term-s-reg.json) › `by_form`):

| form | all 95: rms (bias) | aifoundry3, 81 | card 1, 14 | fp32, 75 | fp16, 20 |
|---|---:|---:|---:|---:|---:|
| S0, M10 as frozen | 0.222 (−0.103) | 0.227 (−0.113) | 0.193 (−0.042) | 0.225 (−0.090) | 0.212 (−0.149) |
| S1, one value per format | 0.214 (−0.033) | 0.215 (−0.052) | 0.205 (+0.075) | 0.220 (−0.022) | 0.190 (−0.077) |
| S2, one per field | 0.203 (−0.032) | 0.201 (−0.058) | 0.215 (+0.117) | 0.202 (−0.021) | 0.207 (−0.077) |
| **S3, one per position** | **0.179 (−0.022)** | 0.173 (−0.057) | 0.211 (+0.177) | 0.167 (−0.011) | 0.217 (−0.065) |

- **M10 over-prices the lists' single bits:** bias −0.103 W. By field (S0): fp32 mantissa −0.041 W (57 steps), fp32 exponent −0.245 W
  (16), sign −0.260 W (2), fp16 −0.149 W. The largest misses are fp32 bit 0 (M10 0.92-0.96 W against 0.60-0.62 W in three lists) and
  exponent bits 28-30 (M10 1.26-1.57 W against 0.80-1.10 W).
- **The lists agree with each other:** at the 27 fp32 positions two or three lists measured with A = 1.0 on aifoundry3 (different base
  words), the measured steps differ by a median 0.087 W (`agreement`).
- **The count error of three points** (RECOUNT-RULE's e(3), item and zero): median 0.061 W a step, largest 0.93 W. The count bias δ from
  Q141(t)'s and M10's 13 recounted S tiles is not resolved (fp32 +0.049 W [−0.287, +0.385], fp16 +0.171 W [−0.838, +1.180]), so it is not
  applied.
- **σ_S**, S3's held-out rms by format: fp32 0.167 W, fp16 0.217 W.
- **The frozen values** (S3 on all 95 steps; `frozen_values`, J per op, with intervals over steps and over runs; here in W at
  aifoundry3's nominal rate): within ±0.16 W at every fp32 mantissa position but bit 0 (−0.38 W) and bit 15 (+0.21 W); −0.07 to −0.16 W
  at exponent bits 23-26 (bit 27 +0.01 W), −0.49 to −0.52 W at bits 28-30, −0.27 W at the sign; fp16 −0.04 to −0.29 W except bits 4-6
  (+0.04 to +0.10 W).

**2. The entry rule (REGISTRATION.md § 4, on M10's registered footing): term S does NOT enter.**

| rule | reading | holds? |
|---|---|---|
| **E1**: best form beats S0 by ≤ −0.010 W, interval below 0 | S3: −0.043 W [−0.083, −0.006] | yes |
| **E2**: negative on each card | aifoundry3 −0.054 W; **card 1 +0.018 W** | **no** |
| **E3**: no worse on pool 6/7's 13 held-out S kinds (26 rows) | **+0.008 W** [−0.014, +0.042] (0.234 → 0.242 W; bias +0.065 → +0.099 W) | **no** |

So M10 stays as frozen for class S, and term S is a **reported arm** in the next blind pool's predictor (§ 8).

**3. Post hoc: pool 8** (the term frozen on all 95 steps, S3, added inside each session's scale and card term; `posthoc_pool8`):

| set | card | M10, rms (bias), W | M10 + term S |
|---|---|---:|---:|
| class S, 8 N1 tiles, 600 MHz | aifoundry3 (E171) | **0.273 (+0.195)** | 0.357 (+0.260) |
| | card 1 (E172) | **0.238 (+0.138)** | 0.323 (+0.200) |
| class S, 8 scored tiles, the 800 MHz cap, board | aifoundry2 (E173, rule E's carry) | **1.158 (+1.062)** | 1.308 (+1.183) |
| | card 0 (E174) | **0.939 (+0.713)** | 1.133 (+0.827) |
| B1's float excess, F1 (19 tiles) | aifoundry3 | +0.092 | +0.120 |
| | card 1 | +0.105 | +0.132 |
| F1 less the 8 class-S tiles (11) | aifoundry3 | **+0.018** | (unchanged) |
| | card 1 | **+0.082** | (unchanged) |

Every M10 figure reproduces the critic's (E171 0.273 / +0.195; E172 0.238 / +0.138; E173 +1.062 and E174 +0.7126, checked by the code;
the B1 split +0.018 / +0.082). The term moves every class-S figure the wrong way, on all four cards, because pool 8's S tiles read
**above** M10 where the lists' single bits read **below** it: the term lowers predictions that were already too low. The 800 MHz carry is
each frozen tile's own linear ratio (1.871-1.874 on aifoundry2; ×κ0 0.9463 on card 0), so the carried term keeps the 600 MHz term's sign
and widens the miss there too.

**4. The footing law (FL1-FL6) and M10 on the law** ([`law-k.json`](law-k.json), [`m10-law.json`](m10-law.json),
[`p8-law.json`](p8-law.json), [`term-s-law.json`](term-s-law.json)):
- **The lists at the law** (FL3's k_s from each list's own `runs.csv`: E65 0.361, E70 0.362, E79 0.357, E134 0.379, E147 0.404 on
  aifoundry3; E102 0.494 on card 1): the term reads the same (S3 0.175 W against S0 0.222; E1 −0.047 [−0.087, −0.009]; E2 card 1
  +0.018; E3 +0.005), so it does not enter on the law either. Post hoc, pool 8's class S on the law, with M10 on the law: 0.262 (+0.185)
  and 0.227 (+0.138) W, with the term 0.354 and 0.304 W. B1 on the law: +0.089 / +0.085 W (without class S +0.020 / +0.047 W).
- **M10 on the law, the exact one-footing test** (§ 6): all 30 training sessions re-reduced by FL3 at their own T_mid (58.3-59.0 °C;
  k_s 0.357-0.362 on aifoundry3, 0.481-0.496 on card 1; E147 0.404 at 62.5 °C) by their registered reducers, each first reproducing its
  committed reduction exactly at Q139(u)'s slope; 958 of 959 rows keep a D; M10's frozen variant and M9's forms refitted (the machinery
  reproduces `m10.json` and `m9.json` to 4.5e-12 first). On the law M10's float prices fall 0.4-6.4% and card 1's term 0.9616 → 0.9564.
  Pool 8 scored at FL7's committed law reductions, post hoc:

| card | footing | P8-M1 (N1, 31): M10 − M9 rms, W [95%] | M10 / M9 rms, W | P8-M1f (F1) | P8-M1i (I1) | P8-A1 |
|---|---|---|---|---|---|---|
| aifoundry3 (E171) | registered (as committed) | BETTER −0.065 [−0.122, −0.012] | 0.180 / 0.245 | BETTER −0.091 | NOT RESOLVED +0.002 | BETTER −0.062 |
| | **the law, both refitted** | **BETTER −0.052 [−0.106, −0.003]** | 0.168 / 0.220 | BETTER −0.071 | NOT RESOLVED −0.002 | BETTER −0.045 |
| card 1 (E172) | registered (as committed) | BETTER −0.080 [−0.134, −0.034] | 0.185 / 0.266 | BETTER −0.112 | NOT RESOLVED +0.009 | BETTER −0.095 |
| | **the law, both refitted** | **BETTER −0.091 [−0.144, −0.040]** | 0.174 / 0.264 | BETTER −0.128 | NOT RESOLVED +0.010 | BETTER −0.111 |

  **M10's lead over M9 survives one footing on both cards: it was never the footing's.** On aifoundry3 the margin shrinks and the
  interval's upper end is −0.003 W. Both models read lower on the law (M10 0.168 / 0.174 W). The mixed arm (the law's test reduction
  with the frozen models) is beside in `p8-law.json`; it reproduces round A's E172 plain-law reading (M1i WORSE +0.0093 W).
- **The law moves pass gates:** with every other part of each registered reduction unchanged, E78's pass gate sets passes aside in nine
  sessions at the law (E141 keeps 1 of 4, E163 1 of 3); one row loses its D (E141's `fp16.exp_only`). Recorded (dated note 1, item 3).

**5. Post hoc, after the term's outputs: where the miss sits** ([`posthoc-structure.txt`](posthoc-structure.txt); M10's committed
held-out errors on its own 959 rows, classed by T_S on each tile's bytes):

| tiles | rows | M10 bias (rms), W |
|---|---:|---:|
| a single B bit, **one base word in every lane** (pool 6's and 7's case S, E127's `q_alt`) | 23 | **+0.098** (0.251); aifoundry3 +0.129, card 1 +0.065 |
| a single B bit, eight base words (E102's and E147's list rows) | 26 | −0.036 (0.189) |
| T_S's zero, **one word in every lane** (`ones`, `neg_ones`, `pi`, `nz_both`, ...) | 34 | **+0.069** (0.096); aifoundry3 +0.106, card 1 +0.043 |
| everything else | 651 | −0.024 (0.186) |

M10 under-predicts tiles whose lanes all hold one word, with or without a toggling bit, and over-predicts the lists' eight-word single bits.
So the class-S miss follows **one word in every lane**, not the position of the bit: a reading, not a test.

## What this changes

- **M10 stays as frozen for class S.** No per-position term enters; term S is a reported arm for the next blind pool (REGISTRATION.md
  § 8). The committed price lists cannot price pool 8's class-S miss: their tiles hold eight base words, and the miss is a one-word one.
- **M10's lead over M9 holds on one footing.** Round A's owed test is answered (post hoc): P8-M1 BETTER on both cards on the law. FL3 can
  become a later session's primary with M10 on the law ([`m10-law.json`](m10-law.json)) as its model, as FL3 itself says.
- **Next:** a lane-uniform (one-word) term, registered first and tested on data with one word in every lane. E178's float one-number
  kinds (registered `48171930`, not run) are such tiles; on M10's own rows the one-word zeros read +0.106 W above M10 on aifoundry3, so
  E178's float readings against M10's frozen D will test this reading directly (no prediction of E178's registered rules is made here).
  A one-base-word single-bit price list (each lane's B the same word) would separate the bit's own part from the word's. Neither is
  registered here.

## Registered, and what happened

- **As registered:** T_S by bytes; the 95 steps; M8's step form for the footing; M10's frozen step from the committed counts; S0-S3 left
  one run out; E1-E3 with their seeds; σ_S; δ; the frozen table; the 800 MHz carry; F-reg and F-law; M10 on the law with its checks;
  every post hoc reading labelled.
- **Checks, all passed:** `predict_m10.py selftest` (1.4e-14 W); this lane's step features on E147's 15 B steps equal M9's committed ones
  exactly; T_S agrees with `make_blind8.single_bit_b` on pool 8's 13 case-S tiles; every pool-8 tile hashes as `blind8.json` says; the
  route reproduces all 30 committed reductions at Q139(u)'s slopes (largest |ΔD| 0); the refit reproduces `m10.json` and `m9.json`; the
  scoring code reproduces E171's and E172's committed P8-M1, M1f, M1i, A1 and s; E173's and E174's class-S means reproduce.
- **Departures** ([dated note 1](../../../../tools/claims-v3/m10-s/REGISTRATION.md.dated-note-1.md)): `term_s.py`'s first fit run stopped
  on a coding error, so the fit runs as `term_s_v2.py`, a new file with that fix and, after the first output, three changes that move no
  figure of it (`term_s.py` stays as committed); `law_m10.py` ran before its commit (two runs stopped on coding errors before any output); the law
  moves pass gates; E3 on the law reads the registered held-out errors; E147's factor differs from M10's rows by 0.5%; the 800 MHz
  carry's linearity is assumed.

## What this cannot say

- **Counting:** the lists' counts are three-point launch averages (e3 up to 0.93 W on a high bit), so a per-step residual carries the
  bench's launch error. A recount of the 95 steps' tiles at 27-243 points is owed (about 190 tiles, a bench sweep on the mini).
- **Coverage:** card 1 is one run (E102); there is no 800 MHz list; nearly every list base word has exponent 127 (1.0-2.0) and a plus
  sign (the items at fp32 bit 30 and fp16 bit 14 use words far below 1), where pool 8's have exponents 124-130 of either sign.
- **The structure reading (§ 5) is post hoc** and rests on M10's own held-out errors; it names where to look, not a cause. Why lanes
  holding one word cost more than the bench says (the silicon's full-custom register file, Ditzel 2026, is one public reason the bench
  may be blind there) is not resolved here.
- **M10 on the law is post hoc** on pool 8; its blind test is the next 600 MHz session registered with FL3 primary.

## Files

| file | what |
|---|---|
| [`term-s-reg.json`](term-s-reg.json), [`term-s-reg-output.txt`](term-s-reg-output.txt) | term S on M10's registered footing: the 95 steps (each with its sources, step features' inputs, k, factor, residual, e3, held-out errors), the forms, E1-E3, the frozen table with intervals, σ_S, δ, the agreement table, pool 8 post hoc (600 and 800 MHz, all forms) |
| [`term-s-law.json`](term-s-law.json), [`term-s-law-output.txt`](term-s-law-output.txt) | the same on the law, with M10 on the law as the base, and pool 8 post hoc on the law |
| [`law-k.json`](law-k.json) | per session: T_mid, k_s, the route check, the kept passes at both slopes, the law reduction's sha256 |
| [`m10-law.json`](m10-law.json), [`rows-m10-law.json`](rows-m10-law.json) | M10 and M9 refitted on the law, the price shifts, the refit check; every row's D on both footings |
| [`p8-law.json`](p8-law.json), [`law-m10-output.txt`](law-m10-output.txt) | P8-M1, M1f, M1i and A1 on the registered footing (reproduction), on the law, and mixed; every tile's law prediction |
| [`posthoc-structure.json`](posthoc-structure.json), [`posthoc-structure.txt`](posthoc-structure.txt) | § 5, post hoc |
| [`SHA256SUMS`](SHA256SUMS) | this directory's files and the code |

## Re-run

From the top of the tree, numpy 1.26 (the Intel's `/usr/bin/python3`), one core:
`python3 -B tools/claims-v3/m10-s/term_s_v2.py selftest`; `python3 -B tools/claims-v3/m10-s/law_m10.py all --scratch <dir> --out <this dir>`
(about 2 minutes: 60 reductions and two refits; the law reductions go to `<dir>`, about 44 MB); `python3 -B
tools/claims-v3/m10-s/term_s_v2.py fit --out <this dir>`; the same with `--footing law --base <this dir>/m10-law.json`; `python3 -B
tools/claims-v3/m10-s/posthoc_structure.py <this dir>`.

SPDX-License-Identifier: Apache-2.0
