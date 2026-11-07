# Q153(m10acc): M10's accumulator-toggle term does not enter - priced on top of M10, the accumulator register's exact toggles over the launch (plus A's non-zero Booth rows for floats) carry nothing M10 does not already price: leave one run out over 1,149 committed rows in 39 runs, the floats read 0.187 → 0.189 W and int8 0.173 → 0.175 W; pool 8's class S stays 0.273 / 0.238 W and his int8 pair stays at P's +0.19 W against +0.053 W measured (post hoc); amendment A1's second reading, the accumulator words a lane takes in from micro-op to micro-op, follows the single-bit lists' watts (r +0.89, post hoc) but does not enter either, because M10's bench already prices that path (its step r +0.99)

*On the kinds page, [section 11, what is still open](https://spacesheep.dev/@yaroslavvb/horace-kinds-of-numbers#11-what-is-still-open):
**item 6**, a power model across kinds. It is the term Q145(b)'s README names as next (a lane-uniform, one-word term tested on data
with one word in every lane), and it takes term S's place as M10's candidate for the single-high-bit class. The owner's goal, in his
words of 2 November 2026: to predict the power requirement and heat generation of numeric computations as accurately as possible.*

*Sat 7 Nov 2026 (week 45), 10:40-12:00 PST, desk only: no card, no lab box, no device command, no post, no Modal. **Registered first:**
[`../../../../tools/claims-v3/m10-acc/REGISTRATION.md`](../../../../tools/claims-v3/m10-acc/REGISTRATION.md) (`b5586759`,
10:56:49 PST), committed alone before the trace program, the fit code or any feature of a registered row; then the code (`b48cf669`,
11:02:22) before the first trace run; then the traces (11:03-11:12, on the mini), the features and their checks, and the registered fit
(11:13:25-11:13:28). Dated amendment A1 (`ceb643ca`, 11:20:21), written after the primary's result was read and before its own first
output, adds a second reading of the feature (§ 6 below). Traces ran on the mini (a Mac, arm64; `run_remote --host mini`, 6
workers, 537 s for the 1,250 tiles); every Python job ran on the Intel through the round's local slot, one at a time, with
`/usr/bin/python3` 3.9.6 (numpy 1.26.4, scipy 1.13.1) pinned.*

**Labels.** The fit is **held out**: every row is predicted by a fit that left its run out. **Pool 8 and E178 are post hoc** for this
term: their misses were read before the registration. **Every reading in § 5 is post hoc**, made after the fit. **A1 is post hoc in its
choice** (its form was chosen after one look at the primary's result). Nothing here is blind; the next blind pool and E182 are the
first blind tests.

## Results

**1. The features, exact.** For every tile, `acctrace_m10acc.c` steps all 256 accumulators through every op of a launch of the
kit's own size with the lab's committed arithmetic (`rtl-sim/fma_toggle_v2/accum.c`, unchanged), and counts the accumulator word's
Hamming distance at every step: **x_acc**, toggles per op (per micro-op: / 512 floats, / 256 int8). For floats it also counts
**x_bth**: A's non-zero radix-4 Booth digits beyond A = 1.0's (the open RTL's recoder, which recodes A), times B's toggled significand
bits, over one op's micro-op transitions in the PRM's order. The launch size is each experiment's median timed launch from its
committed `runs.jsonl` files. **Checks, all passed:** on E178's 40 kinds x_acc equals E178's flip model's `c_store` launch mean to
4.8e-5 a op (T1); x_bth computed again in Python equals the C value on 113 tiles (T2); the mini's build and the Intel's give
byte-identical output on three random tiles at 27,000 and 54,000 ops; every tile hashes as its source says; every response
reproduces its source (M10's held-out errors, pool 8's D − M10, E178's D − P, term S's steps).

**2. The term on 1,149 committed rows, held out (leave one run out; W, measured − predicted)** ([`fit-m10acc.json`](fit-m10acc.json),
[`fit-output.txt`](fit-output.txt)):

| rows | n | runs | M10 rms (bias) | M10-ACC rms (bias) | d |
|---|---:|---:|---:|---:|---:|
| floats, all | 884 | 39 | 0.1873 (−0.015) | 0.1886 (−0.021) | **+0.0013** [−0.0004, +0.0036] |
| floats, aifoundry3 / card 1 | 515 / 369 | | 0.1877 / 0.1866 | 0.1887 / 0.1884 | +0.0010 / +0.0018 |
| floats, the S class (M10's 26, pool 8's 16) | 42 | | 0.2425 (+0.104) | 0.2428 (+0.104) | +0.0004 |
| int8, all | 265 | 24 | 0.1729 (−0.010) | 0.1748 (−0.006) | **+0.0018** [+0.0008, +0.0029] |
| int8, aifoundry3 / card 1 | 142 / 123 | | 0.1675 / 0.1790 | 0.1699 / 0.1802 | +0.0024 / +0.0012 |

The rows: (a) M10's 959 rows with their committed held-out errors; (b) pool 8's 40 kinds on E171 and E172 (80 rows); (c) the five
single-bit lists outside M10's rows, E65, E67, E70, E79 and E134 (70 steps); (d) E178's 40 kinds. d's interval is the registered
cluster bootstrap over runs (2,000 draws, seed 1532).

**3. The rule (REGISTRATION.md § 5): the term does NOT enter, in either family.**

| family | R1: d ≤ −0.005 W, interval below 0 | R2: d < 0 on each card | R3: S class no worse | enters |
|---|---|---|---|---|
| floats | +0.0013 [−0.0004, +0.0036]: fails | +0.0010, +0.0018: fails | +0.0004: fails | **no** |
| int8 | +0.0018 [+0.0008, +0.0029]: fails | +0.0024, +0.0012: fails | | **no** |

**The frozen prices** ([`m10acc.json`](m10acc.json); J a toggle, fitted on every row; jackknife over runs, t with n − 1 df):

| price | value | jackknife 95% | runs bootstrap 95% | leave-one-run-out range |
|---|---:|---|---|---|
| τ_acc, floats | +0.124 fJ | [−3.31, +3.55] | [−2.70, +2.73] | [−0.14, +1.65] |
| τ_bth, floats | +0.065 fJ | [−0.14, +0.26] | [−0.12, +0.23] | [−0.00, +0.10] |
| τ_acc, int8 | −0.084 fJ | [−1.00, +0.83] | [−0.95, +0.69] | [−0.28, +0.09] |

Every interval holds 0, and each price changes sign between folds: the term is not resolved. σ_ACC, one new row's scatter around
M10-ACC: floats 0.189 W (fp32 0.203, fp16 0.163), int8 0.175 W. **M10 stays as frozen**, and M10-ACC is a **reported arm** in the next
blind pool and in E182.

**The reported arms:** ACC1 (floats, x_acc alone) τ +0.637 fJ, d +0.0008 W (its S class −0.0020 W): it fails R1 and R2.
**strict** (fitted on (a) and (c) only, so pool 8 and E178 are never in its fit): floats τ_acc −0.560 fJ, τ_bth +0.057 fJ; int8 +0.014
fJ; on pool 8 and E178, predicted from that fit, d −0.000 W (floats) and +0.000 W (int8).

**4. Post hoc: pool 8's class S, E178's int8 levels and his pair** (`fit-m10acc.json` › `posthoc`):

| set | M10 | M10-ACC (held out by run) | strict arm | term S, for comparison |
|---|---:|---:|---:|---:|
| pool 8 class S, aifoundry3 (8 tiles) | 0.273 (+0.195) | 0.274 (+0.196) | 0.278 (+0.201) | 0.357 (+0.260) |
| pool 8 class S, card 1 (8 tiles) | 0.238 (+0.138) | 0.239 (+0.138) | 0.242 (+0.144) | 0.323 (+0.200) |
| E178's 13 int8 levels, D − P | 0.184 (−0.160) | 0.187 (−0.163) | 0.185 (−0.160) | |
| E178's 14 fp32 / 13 fp16 levels | 0.091 (+0.083) / 0.054 (+0.029) | 0.092 (+0.084) / 0.055 (+0.030) | 0.096 / 0.057 | |

E178's F arm (M10 with the accumulator's launch mean at M10's own `c_end` price) reads the int8 levels 0.186 (−0.162). **His int8
pair, 5s − 4s:** measured +0.0532 W [+0.0217, +0.0848] (E178-H-int8, registered); P +0.1857 W; P + the term +0.1876 W (the fold that
leaves E178 out), +0.1839 W (frozen), +0.1860 W (strict). The term moves his pair by under 0.002 W; it does not explain why the card
reads 0.29 of P.

**5. Post hoc, after the fit: why it carries nothing** ([`posthoc-m10acc.txt`](posthoc-m10acc.txt)):
- **A single high B bit hardly moves the accumulator register.** Over the lists' 70 steps, x_acc's step (the item's less its zero's) is
  about 0 a micro-op (median −0.00; p10 −0.97, p90 +0.75), and the measured steps (median 1.49 W) do not follow it: r −0.03. M10's own
  step follows them: r +0.99. When a lane's two columns hold u and u with one bit flipped, both accumulators still add a constant
  every step, and an accumulator that adds a constant toggles about as many bits whatever the constant.
- **M10 already carries the accumulator's toggles where they vary.** Over M10's 611 float whole tiles, x_acc correlates +0.92 with M10's
  `c_end` feature, and M10's ten float features explain 90% of its variance (R² 0.898).
- **Class S is not a high-toggle class.** x_acc a micro-op: pool 8's class S 20.5 (median), M10's S class 21.5, E178's one-word floats
  19.0, M10's other float tiles 14.7 (p10-p90 0.4-26.6).
- **One-number int8 kinds:** x_acc depends on the product of the two words' bytes only, so (a, b) and (b, a) read the same in all
  153 pairs of the grid. The term cannot tell A's held bits from B's: E182's A-only against B-only contrasts are untouched by it.

**6. Dated amendment A1: the accumulator words a lane's datapath takes in**
([`../../../../tools/claims-v3/m10-acc/REGISTRATION.md.dated-note-A1.md`](../../../../tools/claims-v3/m10-acc/REGISTRATION.md.dated-note-A1.md),
`ceb643ca`, 11:20:21 PST; post hoc in its choice). In the PRM's order a lane takes a different accumulator at every micro-op
(C[i][l], then C[i][8 + l], ...), so its C operand toggles by the distance between two accumulators whenever they differ, which x_acc
never counts. **x_lane** counts it (`acctrace_m10acc_a1.c`, traces on the mini 11:20:32-11:37:23; check A1-T1: its x_acc equals the
committed features in all 1,737 values; A1-T2: on E178's 40 kinds x_lane equals the flip model's `c_in` to 1.0e-4 a op). Same rows,
folds, seeds and rule ([`fit-m10acc-a1.json`](fit-m10acc-a1.json), [`fit-output-a1.txt`](fit-output-a1.txt)). **ACC-L does not enter
either:**

| family | τ_L, frozen | jackknife 95% | d, all [runs 95%] | d, aifoundry3 / card 1 | d, S class | enters |
|---|---:|---|---|---|---:|---|
| floats (τ_bth +0.120 fJ [−0.05, +0.29]) | −0.278 fJ | [−1.07, +0.52] | +0.0008 [−0.0004, +0.0022] | +0.0013 / −0.0001 | +0.0071 | **no** |
| int8 | +0.180 fJ | [−0.17, +0.53] | +0.0007 [−0.0023, +0.0038] | −0.0000 / +0.0015 | | **no** |

Post hoc, with ACC-L: pool 8's class S reads 0.281 (+0.204) and 0.244 (+0.146) W, worse than M10; E178's int8 levels 0.184 (−0.160),
unchanged; his pair P + the term +0.1859 W. **Post hoc, the reason** ([`posthoc-m10acc-a1.txt`](posthoc-m10acc-a1.txt)): the lists'
measured steps do follow x_lane's step, r +0.89 over the 70 steps (mantissa bits +0.88, exponent bits +0.74; x_lane's step a median
+17.9 a micro-op, p90 +93): a single high B bit's watts go with the accumulator words its lane alternates between. But M10's own step
follows them closer (r +0.99), and M10's ten float features explain 89% of x_lane's variance over its whole tiles: the bench counts
that path's nets, so M10 already prices it and its errors hold nothing more for the term. One-number kinds barely move x_lane (E178's
floats 0.59 a micro-op, int8 3.5), once a k-pass.

## Forecasts

- **For the next blind pool's rule (F-P9):** from the held-out errors on pool 8's 40 kinds per card, a pool drawn like pool 8 would
  read P9-ACC's d at floats −0.0024 W [−0.0070, +0.0005] (aifoundry3) and −0.0044 W [−0.0082, −0.0013] (card 1), class S +0.0011 and
  +0.0005 W, int8 +0.0027 and +0.0004 W: under any card's resolution, so P9-ACC is forecast NOT RESOLVED.
- **For E182's planned kinds** ([`forecasts-e182-m10acc.json`](forecasts-e182-m10acc.json)): the term's watts for a grid of 566
  one-number kinds (int8 18 × 18 words, fp32 and fp16 11 × 11 values), on aifoundry3 and card 1 at E178's launch sizes (539,132 /
  538,872 / 913,813 ops) and median measured rates, s = 1. For example int8 5s −0.0031 W and 4s −0.0013 W (5s − 4s −0.0017 W,
  95% [−0.021, +0.017]); fp32 5s +0.0016 W and 4s +0.0011 W. A1's ACC-L beside it
  ([`forecasts-e182-m10acc-a1.json`](forecasts-e182-m10acc-a1.json)): int8 5s +0.0004 W and 4s +0.0002 W, fp32 5s −0.0001 W. Both are
  reported arms (neither entered M10). E182's lane adds them to its own M10 forecast P; a kind outside the grid runs through
  [`predict_m10acc.py`](../../../../tools/claims-v3/m10-acc/predict_m10acc.py) or
  [`predict_m10acc_a1.py`](../../../../tools/claims-v3/m10-acc/predict_m10acc_a1.py) unchanged. For one-number int8 kinds both terms
  depend only on the product of the words' bytes, so (a, b) and (b, a) read the same.

## What this changes

- **M10 stays as frozen** in both families and for class S. Neither M10-ACC (the register's toggles) nor A1's M10-ACC-L (the
  lane's accumulator words) enters; both are reported arms in the next blind pool and in E182, never a primary.
- **Class S's miss is not in the accumulator beyond M10,** read either way. M10's bench already prices the path a single high B bit
  drives (r +0.99 with the lists' steps), so pool 8's +0.14 to +0.20 W excess on one-base-word tiles sits elsewhere. Q148(c)'s
  constant-lane level was not resolved on E178 either. Where it sits is not resolved here.
- **For E182:** in a one-number int8 kind both terms depend only on the product of the two words' bytes, so they read (a, b) and
  (b, a) the same. Whatever E182's unequal-popcount kinds measure between A-only and B-only held bits lies outside both terms.
- **E178's int8 pair** (0.29 of P) is not an accumulator-pricing error of M10 in either sense: both terms move it by under 0.002 W.

## Registered, and what happened

- **As registered:** the features; the four row sets and their responses; one form per family; OLS through the origin; leave one run
  out over 39 runs; the jackknife, the runs bootstrap and the OLS errors; R1-R3; the arms ACC1 and strict; F-P9; the E182 grid; the
  post hoc readings, labelled.
- **Departures:** none from the registration's fit. The registration's dateline says "about 10:55-11:25"; it was committed at
  10:56:49. Its § 3 (a) speaks of "the rows' measured rates as `fit_m10.py`'s `assemble` reads them": the code reads the same fields
  directly (M9's rows file, pool 7's footing reductions), without importing `fit_m10.py`. The public-text scan's hits on the code
  are all one variable's name, the path of the repository's top directory, as in M10's committed `fit_m10.py`; the lab's privacy table
  is not on the Intel, so the scan used its fixed list and this round's patterns.

## What this cannot say

- The features are the open RTL's structure, and the term prices them empirically; that it carries nothing beyond M10 says the
  accumulator register's toggles are not where M10's misses are, not that the register costs nothing.
- x_bth's gate rule is an assumption (a gated lane keeps its operands).
- One launch size per experiment and type: E67's ran 269,962-543,669 ops, and its largest step (`ix_b22`) reads 600, 399 and 335
  toggles an op at the smallest, median and largest launch.
- Pool 8 and E178 are post hoc; the strict arm reads them without fitting on them, after their misses were known.

## Files

| file | what |
|---|---|
| [`features-m10acc.json`](features-m10acc.json) | per tile (by sha256): x_acc at each launch size (with sign, exponent and mantissa), x_bth, unique elements; the launch sizes; the E182 grid; checks T1 and T2 |
| [`rows-m10acc.json`](rows-m10acc.json) | the 1,149 rows: source, run, card, response, s, c, rate, N, features, regressors, held-out errors (primary, ACC1, strict) |
| [`fit-m10acc.json`](fit-m10acc.json), [`fit-output.txt`](fit-output.txt) | the fit, its intervals, the readings, the rule, the arms, F-P9, the post hoc readings, E67's launch sensitivity |
| [`m10acc.json`](m10acc.json) | the frozen term: prices, intervals, σ_ACC, the rule's readings, the arms' prices |
| [`forecasts-e182-m10acc.json`](forecasts-e182-m10acc.json) | the E182 grid's term watts |
| [`posthoc-m10acc.json`](posthoc-m10acc.json), [`posthoc-m10acc.txt`](posthoc-m10acc.txt) | § 5, post hoc |
| [`selftest-predict-m10acc.txt`](selftest-predict-m10acc.txt) | the predictor's self-test |
| [`features-m10acc-a1.json`](features-m10acc-a1.json) | A1: x_lane per tile (under `x_acc.<N>.total`), the register's x_acc beside, x_bth; checks A1-T1 and A1-T2 |
| [`rows-m10acc-a1.json`](rows-m10acc-a1.json), [`fit-m10acc-a1.json`](fit-m10acc-a1.json), [`fit-output-a1.txt`](fit-output-a1.txt), [`m10acc-a1.json`](m10acc-a1.json), [`forecasts-e182-m10acc-a1.json`](forecasts-e182-m10acc-a1.json) | A1's rows, fit, frozen term and E182 grid, by `fit_m10acc.py`'s code unchanged (in them `acc` / `x_acc` is x_lane) |
| [`posthoc-m10acc-a1.json`](posthoc-m10acc-a1.json), [`posthoc-m10acc-a1.txt`](posthoc-m10acc-a1.txt), [`selftest-predict-m10acc-a1.txt`](selftest-predict-m10acc-a1.txt) | A1's post hoc readings and its predictor's self-test |
| [`SHA256SUMS`](SHA256SUMS) | these files and the code |

## Re-run

From the top of the tree, `/usr/bin/python3` (3.9.6, numpy 1.26.4, scipy 1.13.1): `python3 -B tools/claims-v3/m10-acc/fit_m10acc.py
selftest`; `... fit_m10acc.py tiles --job <dir>` (the rows and a job list); copy `<dir>`, `acctrace_m10acc.c`, `accum.c` and the two
runner scripts to a Mac or Linux box and run `bash run_traces_m10acc.sh joblist.txt 6` there (about 9 minutes on the mini); copy
`out/` back; `... fit_m10acc.py features --job <dir> --out <this dir>`; `... fit_m10acc.py fit --out <this dir>`;
`python3 -B tools/claims-v3/m10-acc/posthoc_m10acc.py --out <this dir>`; `python3 -B tools/claims-v3/m10-acc/predict_m10acc.py selftest`.
A1: `bash run_traces_m10acc_a1.sh joblist.txt 6` in the same job directory (about 17 minutes on the mini), `out-a1/` copied back, then
`fit_m10acc_a1.py features --job <dir> --out <this dir>`, `fit_m10acc_a1.py fit --out <this dir>`, `posthoc_m10acc_a1.py --out <this
dir>` and `predict_m10acc_a1.py selftest`.

SPDX-License-Identifier: Apache-2.0
