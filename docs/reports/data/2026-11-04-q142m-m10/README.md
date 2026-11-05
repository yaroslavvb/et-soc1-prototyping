# Q142(m): M10, held out but not blind - two power terms enter by their registered rules: each session's own random anchors set a float scale (held-out float rms 0.208 → 0.202 W), and the single high bits counted at 27-243 launch points instead of 3 (the S class 0.502 → 0.257 W); together the floats read 0.185 W held out and pool 7's float rows 0.197 W (M9 as frozen, blind there, 0.358 W); int8's anchors do not help; the 4.5 s heat scale per session cuts card 1's error by 39% but fails the rule on aifoundry3; card 0's burst rise is 0.24 °C per board W (enters, one session); the heat chain's gain of +3.2% enters; card 0's κ on the die-start footing does not; frozen for blind pool 8

*On the kinds page, [section 11, what is still open](https://spacesheep.dev/@yaroslavvb/horace-kinds-of-numbers#11-what-is-still-open):
**item 6**, a power model across kinds, with **items 8 and 9** (heat) for terms (c) and (d). It answers the card half's final
critic's `next` **rank 2**: M10's registration, then its nested refit, before any more card time on the power model. The owner's
goal, in his words of 2 November 2026: to predict the power requirement and heat generation of numeric computations as accurately
as possible.*

*Wed 4 Nov 2026 (week 45), 19:20-20:45 PST, desk only: no card, no device command, no card step on a lab box, no post in the
lab's channel, no Modal, no archive. **The registration, [`../../../../tools/claims-v3/m10/REGISTRATION.md`](../../../../tools/claims-v3/m10/REGISTRATION.md),
was committed and pushed (`e9367b66`, 19:33:42 PST) before `fit_m10.py` existed**, with the hashes of the 174 inputs it names
([`SHA256SUMS`](../../../../tools/claims-v3/m10/SHA256SUMS)); the bench driver followed (`0b3ddeef`, 19:35:05) before its first
count, and one dated amendment (A1, [`REGISTRATION.md.dated-note-1.md`](../../../../tools/claims-v3/m10/REGISTRATION.md.dated-note-1.md),
`3bcb3fcd`, 19:43:44) before the fitter first ran. Where it ran: the bench counts on the mini (a Mac, arm64, Verilator 5.052,
`-fno-dfg`; Q141(t2)'s recorded build, its binaries re-hashed equal to its record, 4 jobs, each call capped in memory and time),
after one new point counted on both the mini's and the Intel's builds read identical in every field; the registered fit on a lab
host (aifoundry1, capped at 4 GB and 900 s; no card session was going there); on the Intel, git, the checks, one bench point on one
core and four development runs of the fitter through the round's local slot (2 threads, about a minute or less each, written
outside this directory; one stopped at a coding error before any fit, one ran under an import trace to list the files to stage),
plus one on the lab host with term b's counts not yet complete; their numbers for terms a, c1, c2, d and e equal the registered
run's. The registered run ran twice on the lab host, 20:21 and 20:22 PST: the second only after `rows-m10.json`'s in-sample D was
stored at full precision for the predictor's self-test (it had been rounded to 1e-6 W); `heldout-m10.json` and `m10.json` are
identical between the two.*

**This is held out, not blind.** Every row below is predicted by a fit that never read that row's kind (leave one kind out; for
c2 and e, one tile; for d, one session), but every candidate term was named from misses already seen on pool 7 and the heat
replicates, and the entry rule read the same held-out errors it reports. **The blind test is pool 8, drawn by an independent
designer in a later round, after a critic reads M10.** No pool and no prediction for any tile that has not run is made here.

## Results

**1. Which terms entered, by the registered rules** (REGISTRATION.md § 6; every figure leave-one-kind-out on Q139(u)'s footing;
d = the variant's rms minus the base's on the same rows, with its paired-bootstrap 95% interval, 2,000 draws, seed 142):

| term | the rule (REGISTRATION.md § 6) | reading | enters? |
|---|---|---|---|
| (a) floats: a scale per session from its own random anchors | pooled d ≤ −0.005 W, interval below 0, d < 0 on each card | pooled -0.0063 [-0.0105, -0.0024] W; aifoundry3 -0.0071 [-0.0111, -0.0033] W; card 1 -0.0054 [-0.0106, -0.0001] W | **yes** |
| (a) int8 | the same | pooled +0.0018 [-0.0031, +0.0068] W; aifoundry3 +0.0007 [-0.0084, +0.0101] W; card 1 +0.0028 [-0.0043, +0.0112] W | **no** |
| (b) the S class at 27-243 launch points | S rows d ≤ −0.050 W, interval (13 kinds) below 0, d < 0 on each card, pooled float rms up ≤ 0.001 W | S rows -0.2452 [-0.3806, -0.1098] W; aifoundry3 -0.2100 [-0.3217, -0.1028] W; card 1 -0.2845 [-0.4564, -0.1132] W; pooled floats -0.0157 [-0.0304, -0.0036] W | **yes** |
| (c1) a 4.5 s heat scale per session | pooled d ≤ −0.010 °C, interval below 0, d < 0 on each card | pooled -0.0600 [-0.0755, -0.0445] °C; aifoundry3 +0.0020 [-0.0029, +0.0072] °C; card 1 -0.1123 [-0.1367, -0.0852] °C | **no** |
| (c2) card 0's 6 s burst rise per board W | d ≤ −0.25 °C, interval below 0 (39 tiles) | -2.116 [-2.306, -1.929] °C; k 0.2415 °C/W against 0.1400 | **yes** |
| (d) the chain's gain, one γ | large rises d ≤ −0.10 °C, interval below 0, d < 0 on each card kind | -0.199 [-0.327, -0.002] °C; by card kind {'aifoundry2': -0.3464, 'aifoundry3': -0.0846}; γ {'all': 0.03199} | **yes** |
| (d) the chain's gain, γ per card kind | large rises d ≤ −0.10 °C, interval below 0, d < 0 on each card kind | -0.180 [-0.366, +0.029] °C; by card kind {'aifoundry2': -0.3225, 'aifoundry3': -0.0699}; γ {'aifoundry2': 0.04515, 'aifoundry3': 0.02349} | **no** |
| (e) card 0's κ on the die-start footing | d ≤ −0.05 W, interval below 0 (39 tiles) | -0.096 [-0.180, +0.016] W; κ {'float': 0.9619, 'int8': 0.9189} against 0.9463 | **no** |

**2. Power at 600 MHz, held out** (W of D, rms with the bias measured − predicted in brackets; "M10" is the frozen variant: floats
B+a+b, int8 B; "B" is M9's frozen form refitted on all 959 rows; "M9 as frozen" is `m9.json` unchanged, in sample on
M9's 855 rows and blind on pool 7's, at each row's measured rate, amendment A1-2):

| rows | card | M10 | B | M9 as frozen |
|---|---|---:|---:|---:|
| floats, all | all | 0.185 (-0.016) | 0.208 (-0.016) | 0.203 (+0.002) |
| floats, all | card a3 | 0.185 (-0.020) | 0.206 (-0.026) | 0.202 (-0.010) |
| floats, all | card c1 | 0.185 (-0.011) | 0.210 (-0.005) | 0.204 (+0.015) |
| floats, pool 7, priority 1 | all | 0.197 (+0.061) | 0.342 (+0.195) | 0.358 (+0.213) |
| floats, pool 7, priority 1 | card a3 | 0.216 (+0.055) | 0.347 (+0.188) | 0.363 (+0.207) |
| floats, pool 7, priority 1 | card c1 | 0.176 (+0.068) | 0.336 (+0.201) | 0.353 (+0.219) |
| floats, S class | all | 0.234 (+0.065) | 0.502 (+0.058) | 0.499 (+0.102) |
| floats, S class | card a3 | 0.265 (+0.090) | 0.497 (+0.078) | 0.496 (+0.123) |
| floats, S class | card c1 | 0.198 (+0.041) | 0.507 (+0.037) | 0.502 (+0.081) |
| floats, M9's 855 rows | all | 0.185 (-0.022) | 0.194 (-0.033) | 0.186 (-0.015) |
| floats, M9's 855 rows | card a3 | 0.183 (-0.026) | 0.192 (-0.041) | 0.185 (-0.026) |
| floats, M9's 855 rows | card c1 | 0.186 (-0.019) | 0.196 (-0.023) | 0.186 (-0.002) |
| int8, all | all | 0.177 (-0.007) | 0.177 (-0.007) | 0.169 (-0.005) |
| int8, all | card a3 | 0.170 (-0.005) | 0.170 (-0.005) | 0.164 (-0.003) |
| int8, all | card c1 | 0.185 (-0.009) | 0.185 (-0.009) | 0.173 (-0.006) |
| int8, pool 7, priority 1 | all | 0.195 (-0.019) | 0.195 (-0.019) | 0.195 (+0.002) |
| int8, pool 7, priority 1 | card a3 | 0.191 (+0.043) | 0.191 (+0.043) | 0.196 (+0.065) |
| int8, pool 7, priority 1 | card c1 | 0.199 (-0.081) | 0.199 (-0.081) | 0.195 (-0.060) |
| int8, M9's 855 rows | all | 0.174 (-0.005) | 0.174 (-0.005) | 0.163 (-0.008) |
| int8, M9's 855 rows | card a3 | 0.165 (-0.019) | 0.165 (-0.019) | 0.157 (-0.023) |
| int8, M9's 855 rows | card c1 | 0.183 (+0.010) | 0.183 (+0.010) | 0.169 (+0.008) |
| pool 7's 48 priority-1 kinds, all formats | card a3 | 0.205 (+0.050) | 0.287 (+0.122) | 0.298 (+0.142) |
| pool 7's 48 priority-1 kinds, all formats | card c1 | 0.187 (-0.000) | 0.282 (+0.072) | 0.292 (+0.091) |

M9's registered blind figures on the same 48 kinds, at the formats' nominal rates (E163's and E164's `scored.json`): 0.278 W
(bias +0.105) on aifoundry3 and 0.273 W (+0.054) on card 1. Pool 6's and pool 7's sessions ran 0.28-0.36% below the nominal rate
(each item's measured `rate`), so at measured rates M9 as frozen reads those kinds 0.298 / 0.292 W; M10 is fitted and scored at
measured rates throughout.

**In plain words.** M10 is M9 with two more pieces. First, before predicting a session, it reads that session's own random-data
anchors (E78's random fp32, fp16 and int8 tiles, which every session runs, and any pool anchors) and scales its float
predictions by how far those anchors read above or below the model. Over all 31 sessions the float scale runs from 1.0008 to
1.0102; pool 7's two sessions are the two highest (1.0099 and 1.0102), about 0.6% above the median session, which is the float
excess the card-half critic found. Taking that out lowers the held-out float error on both cards and, alone, halves pool 7's float bias
(+0.195 → +0.106 W); the rest is not a session level. For int8 the same scale does not help (its anchors over-correct, as
the critic saw post hoc; int8's random anchor reads 0.97-1.00 of the model in every session, so it carries a model miss on that
one tile more than a session level, a post hoc reading), so int8 keeps M9's form. Second, for the single high bits the miss was the bench's own arithmetic: it averaged a 0.5 s launch from three points. Counted at 9 to 243 points, until each tile's counting error is under 0.10 W (or 243 points), the 13 S tiles' features move by -0.57 to +1.05 W at M9's prices, their held-out error falls from 0.50 to 0.26 W, and with the session scale to 0.23 W; the floats' pooled held-out error falls from 0.208 to 0.185 W, and pool 7's float rows from 0.342 to 0.197 W (bias +0.195 to +0.061 W). For heat, the session's own anchors would cut card 1's 4.5 s
error from 0.285 to 0.173 °C, but they do nothing on aifoundry3, and the rule asked for both cards. Card 0's die rises 0.24 °C per
board W in a 6 s burst, 1.7 times aifoundry2's, and that coefficient carries card 0's burst heat from 2.45 to 0.34 °C rms (one
session, held out by tile). Over minutes, Q138(t)'s chain reads large rises 3.2% low on both card kinds; a gain of 1.032 takes the
large-rise plateaus from 0.49 to 0.29 °C rms, held out by session. Card 0's switching scale referred to each tile's die start
reads 0.962 (floats) and 0.919 (int8) against κ0's 0.9463, but the board error it saves (0.73 → 0.63 W) is not resolved.

**3. The sessions' float scales** (the frozen variant fitted on all rows; [`tables-m10.md`](tables-m10.md) lists all 31): median
1.0035 on aifoundry3 and 1.0047 on card 1; E163 1.00991, E164 1.01024; E147 (no random anchor) 1. int8's, had term a entered:
0.9694 to 1.0000.

**4. Term b, the single high bits** (RECOUNT-RULE.md's estimator at M9's frozen float prices, bound 0.10 W):

| tile | counted to | N used | e(N), W | met | 3pt − N, W |
|---|---:|---:|---:|---|---:|
| `fp16.b_onebit_b6_third` | 243 | 243 | 0.041 | yes | +0.632 |
| `fp16.b_onebit_b8_pi` | 81 | 81 | 0.094 | yes | -0.134 |
| `fp16.b_onebit_b9_one` | 81 | 81 | 0.087 | yes | +0.015 |
| `fp32.a_onebit_b16_half` | 9 | 9 | 0.027 | yes | +0.001 |
| `fp32.a_onebit_b5_third` | 9 | 9 | 0.006 | yes | +0.000 |
| `fp32.b_onebit_b12_third` | 27 | 27 | 0.060 | yes | -0.026 |
| `fp32.b_onebit_b20_full` | 81 | 81 | 0.073 | yes | -0.102 |
| `fp32.b_onebit_b20_one` | 81 | 81 | 0.095 | yes | +0.374 |
| `fp32.b_onebit_b20_pi` | 243 | 243 | 0.055 | yes | -0.157 |
| `fp32.b_onebit_b20_seventh` | 243 | 243 | 0.089 | yes | -0.567 |
| `fp32.b_onebit_b20_third` | 243 | 243 | 0.088 | yes | +1.049 |
| `fp32.b_onebit_b20_third_a1p5` | 81 | 81 | 0.082 | yes | +0.414 |
| `fp32.b_onebit_b22_third` | 243 | 243 | 0.119 | no (at the cap) | -0.496 |

**5. Heat at 600 MHz (c1)** (°C; 932 window rows, 453 kinds, 30 sessions): M7's law as frozen 0.234; M7's form refitted, held out, 0.233 (aifoundry3 0.172, card 1 0.285); with the session heat scale 0.173 (aifoundry3 0.174, card 1 0.173): it helps card 1 and not aifoundry3, so it does not enter. End to end (the refitted law at M10's held-out D, the 767 rows that are power rows) 0.231 °C, against 0.232 at the measured S: the power error adds almost nothing to the 4.5 s heat error. M7's form refitted on all 932 rows reads
S|aifoundry3 0.1198 and S|card 1 0.1194 °C per W (M7's 0.1186 and 0.1151), and that refit is M10's 4.5 s law.

**6. Card 0 (c2, e)**: (c2) the frozen burst law (k 0.1400 °C/W) reads card 0's burst rise at the measured board 2.45 °C rms (bias +2.39); k fitted leave one tile out (0.2407-0.2433) reads 0.34 °C (+0.03); on all 39 tiles k = 0.2415 °C/W. (e) the board through κ0 = 0.9463 reads 0.728 W (bias -0.090), the leave-one-tile-out κ (floats 0.960-0.967, int8 0.916-0.922) 0.631 W (-0.008): not resolved.

**7. The heat chain's gain (d)** (leave one session out; nine large-rise holds in six sessions; the trip-regime holds and E166's
long window left out as registered): one γ = +0.0320 on all fitted holds; the large-rise plateau errors go from 0.493 to 0.294 °C rms (9 holds) and over every fitted hold from 0.413 to 0.256 °C; per card kind γ would be {'aifoundry2': 0.04515, 'aifoundry3': 0.02349}, and that variant's interval reaches above zero. The per-hold table is in [`tables-m10.md`](tables-m10.md).

## M10, frozen

[`m10.json`](m10.json), written by [`fit_m10.py`](fit_m10.py) on all rows; [`SHA256SUMS`](SHA256SUMS) holds the hashes of the code,
the parameters and every output here.
- **Floats** (B+a+b): M9's form `G8+c_end+xstage`, refitted on 737 rows; `coef_J` the prices (pass 2), `pass1_coef_J`
  the prices a new session's scale is read with; card 1's term 0.9616; band k 2.002 (700 of 737 rows inside).
- **int8** (B): M9's form `J8+bsat+bpp_r4` refitted on 222 rows; card 1's term 0.9616; band k 1.829 (210 of 222 rows inside).
- **A new session's float scale:** the median over its random anchors of measured D / (rate × pass-1 prices × features × card
  term); 1 when it runs none. So M10's float prediction for a session needs E78's random tiles (or pool anchors) run in it.
- **A case-S tile** (one high bit on a base word): its counts come from RECOUNT-RULE.md's steps (9, 27, 81, 243 launch points) until e(N) <= 0.10 W or N = 243, before its features are computed. `fp32.b_onebit_b22_third` stays above the bound at 243 points (e 0.119 W) and is carried with that error.
- **Heat:** the 4.5 s window law, M7's form with M10's refitted coefficients; card 0's 6 s burst rise 0.2415 °C per board W over
  21.5 W; Q138(t)'s chain's rise times 1.032 (fitted on every non-trip hold, judged on the large rises); card 0's κ stays κ0 = 0.9463; aifoundry2 keeps M9's part unchanged.
- **The predictor:** [`predict_m10.py`](predict_m10.py) computes D, the session scale and the heat terms from `m10.json` alone; its
  self-test reproduces the fit's in-sample D for pool 7's 104 rows ([`selftest-predict-m10.txt`](selftest-predict-m10.txt)).

## What this does to predicting power and heat

| quantity | before | after (held out, not blind) | source |
|---|---|---|---|
| power, floats, every row (737; 398 kinds) | M9's form refitted 0.208 W; M9 as frozen 0.203 (in sample on 681 rows) | **0.185 W** (term a alone 0.202, term b alone 0.192) | `heldout-m10.json` › `power.float` |
| power, pool 7's float rows (26 priority-1 kinds x 2 cards) | M9 as frozen, blind: 0.358 W, bias +0.213; B 0.342, +0.195 | **0.197 W, bias +0.061** | the same |
| power, pool 7's 48 priority-1 kinds per card, all formats | M9 registered blind 0.278 / 0.273 W (nominal rates); at measured rates 0.298 / 0.292; B 0.287 / 0.282 | **0.205 / 0.187 W** (aifoundry3 / card 1) | `rows-m10.json`, `tables-m10.md` |
| power, the S class (13 tiles, 26 rows) | B 0.502 W; M9 as frozen 0.499 | **0.234 W** (term b alone 0.257) | `power.float` › `S class` |
| power, int8 every row (222; 107 kinds) | M9's form refitted 0.177 W | unchanged: term a does not enter (0.179) | `power.int8` |
| heat, the 4.5 s window rise (932 rows) | M7's law 0.234 °C | M7's form refitted 0.233 °C (with a session heat scale 0.173, not entered: card 1 0.285 → 0.173, aifoundry3 0.172 → 0.174) | `heat_c1` |
| heat, card 0's 6 s bursts (39 tiles, one session) | aifoundry2's burst law 2.45 °C rms | **0.34 °C** (k 0.2415 °C/W, leave one tile out) | `heat_c2_card0_burst` |
| heat over minutes, large rises (9 holds, 6 sessions) | Q138(t)'s chain given the watts 0.493 °C rms | **0.294 °C** (rise x 1.032, leave one session out) | `heat_d_chain_gain` |
| card 0's burst board (39 tiles) | κ0 0.728 W | 0.631 W with κ read leave one tile out, not resolved, not entered | `kappa_e_card0` |

## Registered, and what happened

- **As registered:** the rows (959, none missing), the anchors (E147 none), the two passes, the card term kept from pass 1, the
  S class and its counts by the convergence rule, every variant on the same folds, each entry rule as written, the bands.
- **Checks, all passed:** the 174 registered inputs hashed as committed; M10's fitter against `fit_m7.Fam` on M9's 855 rows, every
  row within 1.4e-12 W, and against `nested-m9.json`'s aggregates within 5e-16 W (A1-1); the feature chain on pool 6's anchors and
  pool 7's S tiles, and on every S row's three-point counts, exact (A1-3); every row's D equal to its session's footing reduction
  (889 rows compared, largest difference 0); C checked at every bench point (`check_mismatch` 0); the one-point build check
  identical in every field; the predictor's self-test; and after the lane the four frozen hash lists (blind7 91, e168 9, the
  e168 scorer 18, predict_q140e's 26).
- **Departures, named:** A1 (the self-test's reference and the rate, before the fitter ran); the development runs and the
  registered run's repeat (header); the end-to-end heat figure beside c1, which § 3c promised, was added to `fit_m10.py` before
  the registered run; the counts' steps were set one at a
  time from each step's e(N), as RECOUNT-RULE.md says, so the counting ran in four steps.

## What this cannot say

- **Not blind.** The terms were named from pool 7's and the replicates' misses; the entry decision read the errors it reports.
- **Term a is a session's own reading.** It predicts a session only after that session has run its random anchors; it says
  nothing about why pool 7's sessions read 0.6% high, and it leaves half of pool 7's float excess in place. The critic's rank 3
  (is the excess a level or a gain, of the day, the session or the card) is still the test for it.
- **The rate.** M10 is fitted and scored at each row's measured rate. Pool 6's and 7's sessions ran 0.28-0.36% below the nominal
  rate; a blind prediction made before a session needs a stated rate, which pool 8's registration has to name.
- **c2 and e rest on one session of card 0**, held out by tile, not by session.
- **d rests on nine large-rise holds in six sessions;** its interval reaches −0.002 °C at the edge, and it fixes the chain's
  output, not why the chain reads low.
- **c1 is not entered**, though card 1's session heat scales run 0.63-1.10 of the law. A rule for card 1 alone was not registered;
  that is a candidate for the next registration, not a result.
- **E147's single-bit steps keep three-point counts**, and M10's D is not carried to aifoundry2's governed bursts or to card 0's
  (M9's aifoundry2 part is unchanged).

## Files

| file | what |
|---|---|
| `fit_m10.py` | the refit: rows, anchors, the S recount's features, the fitter and its self-test, every variant, the heat and card-0 terms |
| `m10.json`, `heldout-m10.json`, `rows-m10.json`, `fit-output.txt` | M10 frozen; every held-out figure and bootstrap; per row, each variant's held-out error, M9's frozen error and M10's in-sample D; the run's log |
| `tables_m10.py` → `tables-m10.md` | the tables above and more, mechanically from `heldout-m10.json` |
| `predict_m10.py` → `selftest-predict-m10.txt` | the frozen predictor and its self-test |
| `bench/bench_m10.py`, `bench/counts-m10-*.json` (+ `-run.json`, `.log`) | term b's counts on the mini, chunk by chunk |
| `bench/counts-b1-*.json`, `bench/check-b1.json` | the one-point build check (the mini's against the Intel's) |
| `SHA256SUMS` | the frozen form's hash list |

## Re-run

From the top of the tree (numpy 1.26): `python3 -B docs/reports/data/2026-11-04-q142m-m10/fit_m10.py` (about a minute; it stops if
any registered input's hash differs), then `predict_m10.py selftest` and `tables_m10.py > tables-m10.md` in that directory.
