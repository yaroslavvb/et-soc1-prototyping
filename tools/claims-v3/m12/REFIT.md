# M12: M10 refitted POST HOC on E182's committed rows - held-word terms for one-number tiles (int8 held 1-bits on A's side and on B's, the int8 flips priced by class, fp32 operand placement, a level offset), held out on E178's committed rows and pool 8's class S, with frozen forecasts for a next one-number run's candidate kinds (Q157, the refit's rules)

*Written Sun 8 Nov 2026 (week 45), PST, on the Intel, desk only: no card, device command, card session, lab box, post or deploy. **This
file is the refit's rules. It is committed first and alone, before the fitter, the held-out scorer and the candidates' forecasts exist
as committed files and before any held-out residual is computed.** Nothing here is registered: M12 is a post hoc model, and its
candidate forecasts are a candidate for the next registration, not a registration.*

*It answers the card day critic's rank 5 of Sun 8 Nov 2026 (refit M10 on E182, post hoc, held out on E178 and pool 8) and serves the
kinds page's [section 11, item 6](https://spacesheep.dev/@yaroslavvb/horace-kinds-of-numbers#11-what-is-still-open), "a power model
across kinds", for the owner's ask of Thu 5 Nov 2026, about 19:30 PST: "here's a matrix filled with one number, and here's a matrix
filled with another number, and they require different number of transistor flips, therefore they will use different power, and I
have a model which actually tracks it down."*

## 0. What M12 is, in one paragraph

**M10 stays frozen** (`tools/claims-v3/m10/`, `docs/reports/data/2026-11-04-q142m-m10/`): nothing of it is edited, and every M10 figure
here is its frozen predictor's. **M12 is a new model, the lab's next free model name** (no `M12` model exists in `AGENT.md`'s index or
in `docs/findings/`; the only other `M12` strings in the tree's text files are self-test case labels in `tools/claims-v3/e180/` and
metal-layer names in the process research of `docs/reports/data/2026-10-01-ladder/` and its copies). It changes M10 only for
**held-word tiles**, where every lane's A word and B word hold still through the launch:
E182 (Sun 8 Nov, blind) showed that there held 1-bits cost on **both** operand sides (E182-SPLIT A+B: beta_A +0.00834, beta_B +0.00988 W
a held 1-bit a byte, where M10 said B only at +0.0157), that M10's int8 price per flip is about twice the card's (E182-W-int8 FAIL HIGH,
3.79 fJ against 7.04), and that in fp32 the same 23 held 1-bits cost +0.2359 W more on B's side than on A's (E182-F, every forecast 0),
with his fp32 pair above every forecast (E182-H32T +0.0285 W). Every other tile is M10 unchanged.

## 1. Builds on (the stock-take's rule for lanes)

1. **Checked:** the stock-take's inventory rule (public rows only); the pieces newer than it are cited by commit. The refit reads
   committed lab files only.
2. **Used** (each unchanged, read by path; the fitter records every input's sha256):
   - **E182** (registration `58b88850` with notes 1-3; data `0f6a8c45`, fix `a8ae359a`;
     `docs/reports/data/2026-11-08-e182-one-number-r2-aifoundry3/`): `trains-e182.json` (the six trains' estimates and standard errors,
     `e182_stats.py`'s statistic), `scored.json` > `reported` > `kinds` (each kind's kinds-pass D over its format's zeros on E178's footing,
     its pass sd and count, its measured rate, and M10's P scored at the session's float scale s = 1.00947 and the measured rate) and
     `scored.json` > `rules` (the trains' forecast lines). The kinds' words, popcounts and **flips by class** (E178's exact flip model,
     launch mean) are `tools/claims-v3/e182/forecast-e182.json` > `kinds`. *Check:* the fitter recomputes E182-A and E182-B from
     `trains-e182.json` by E182.md section 5.1's formulas and asserts the committed values to 1e-12.
   - **E178** (registration `48171930`, A1-A4; data `f7820e70`, fix `f68f0380`;
     `docs/reports/data/2026-11-06-e178-one-number-aifoundry3/`), **held out**: `scored.json` > `primary` > `reported` > `kinds` (40 kinds:
     D, sd, n, rate, M10's scored P at s = 1.00590) and > `rules` > `E178-H-int8` (his pair, +0.0532 W [+0.0217, +0.0848]); the flips by
     class and popcounts are `tools/claims-v3/e178/forecast-e178.json` > `kinds`.
   - **Pool 8** (design `153b720f`, tiles `tools/claims-v3/kinds/blind8/tiles/`; E171 data
     `docs/reports/data/2026-11-05-e171-blind8-aifoundry3/`, E172 `docs/reports/data/2026-11-05-e172-blind8-card1/`), **held out**: the
     class S rows of `scored.json` > `primary` > `rows` (D, per-pass D, M10's primary at the session's s), and each tile's bytes for its
     A and B words' popcounts.
   - **M10** (registered `e9367b66`, frozen `6829c9ba`): `m10.json`, `fit_m10.chain_feats` and `predict_m10.d600` unchanged, for the
     candidate kinds' P from their bench counts.
   - **The toggle bench** (`rtl-sim/fma_toggle_v2`, the recorded build on the mini that E178's and E182's counts came from, `Vtb` sha256
     `a740318c...`) and **E178's flip model** (`tools/claims-v3/e178/flipmodel_e178.c` against `rtl-sim/fma_toggle_v2/accum.c`, both
     unchanged): the candidate kinds' counts and flips. *Check:* each format's zeros row and the committed reference tiles' rows equal
     E178's committed counts to the net, and the flip model reproduces E182's committed flips for E182's kinds, before any candidate
     figure is used.
   - **E184 arm B** (data `8bf74b26`, notes `9a8b9d3e`): card 1's SRAM-rail factor, `scored-e184-v3.json` > `arm_B` > `E184-M` >
     `implied_rail_over_reading` (1.41205, with E184-M NOT RESOLVED and the factor load-dependent): **carried as a reported candidate
     only, never applied** (M12 is a board-level model, and no M12 term reads the SRAM rail).
3. **Not used:** E182's dated note M1 and its arm files (a reported arm; this refit uses only the lab's own registered data and models);
   M10-ACC (it did not enter M10 and cancels inside every E182 product group); card 0 and aifoundry2 rows; every pool other than pool 8;
   any per-electron or design-data model.
4. **Tiers:** every file here is public tier and cites public pieces only. No private-tier check enters.
5. **Readiness:** this block is the refit's own; a verifier checks it against the cited commits.

## 2. The model

**Scope.** M12 applies to **held-word tiles**: (a) **one-number tiles**, every A word one value and every B word one value; (b) **one-base-word
tiles** (pool 8's class S and its re-runs), one side one value and the other side two values one bit apart. **Every other tile is M10
unchanged.** Popcounts are of the 32-bit lane words (an fp16 word holds two halves); h is the popcount a byte (int8: the word's popcount
over 4); for a one-base-word side, the mean popcount over the tile's words of that side.

**int8 one-number tiles** (W over the int8 zeros, aifoundry3):

    D8 = c8 + R (k_w F_walk + k_s F_scp) + beta_A h_A + beta_B h_B

- R the op rate (the kind's measured rate where one exists, else E182's mean int8 rate over its 20 kinds); F_walk = c_store + c_in +
  c_out and F_scp = scp, E178's flip model's launch-mean flips an op by class (the accumulator's walk, and the scratchpad read data
  alternating A and B chunks). TenB's flips (`tenb_rz`, 1,024 h_B an op) are not priced by k: beta_B carries B's held bits.
- **Why two flip prices:** in exploration of E182's own rows (training data, before this file), one price for all flips could not
  hold both T1 (his pair, a walk-only difference at fixed held bits) and the kinds passes' spread: one price fitted to the kinds alone
  forecasts T1 at +0.082 W against the measured +0.0470 [+0.0403, +0.0537]; with the walk and the scratchpad's A/B switching priced
  apart, the kinds passes give a walk price near T1's and leave a kinds-pass residual sd of 0.037 W against one price's 0.064. The task's
  single price "near 3.79 fJ" is kept as two reported arms (section 3).

**Float held-word tiles** (fp32 and fp16, W over the format's zeros):

    Df = P10 + c_f + gamma_A pc_A + gamma_B pc_B

- P10 is M10 frozen at the session's float scale s and the measured rate (the committed scorer's P where one exists; a candidate's from
  its bench counts at s = 1 and E182's median rate). pc_A, pc_B the A and B words' popcounts (a one-base-word side: the mean).
- gamma_B - gamma_A is the **operand-placement term** (T5); gamma_A + gamma_B carries his fp32 pair's excess over M10 (T6 - its P line,
  where both sides gain one held bit); c_f is the **level offset**.
- **fp16 uses fp32's c_f, gamma_A and gamma_B** per held 1-bit of the 32-bit word (rule F16-SAME): E182 ran no fp16 kind, so fp16 is
  an extrapolation, and E178's 13 fp16 kinds and pool 8's 4 fp16 class S tiles test it held out.

**Cards.** M12 is fitted on aifoundry3 only and scored there. On aifoundry1 card 1 (secondary, reported) the float increment
(Df - P10) is multiplied by M10's float card term (0.96160); nothing else is carried to card 1.

## 3. The fit (E182 only; every input committed)

- **int8:** weighted least squares over 24 rows: the 20 int8 kinds' kinds-pass means (design 1, R F_walk, R F_scp, h_A, h_B; one
  common variance sigma_K^2, set to the kinds rows' own residual variance and iterated to convergence) and the trains T1-T4 (design 0,
  R dF_walk, R dF_scp, dh_A, dh_B at the kinds' mean rate, first kind minus second; each its own se^2 from `trains-e182.json`).
  Parameters c8, k_w, k_s, beta_A, beta_B, with their covariance.
- **fp32:** weighted least squares over 6 rows: the 4 fp32 kinds' r = D - P10 (design 1, pc_A, pc_B; each kind's variance its pass
  sd^2 / n) and the trains T5 and T6 (design 0, dpc_A, dpc_B; target the train minus its committed P line, `scored.json` > `rules`:
  E182-F 0, E182-H32T +0.010517 W; variance se^2). Parameters c_f, gamma_A, gamma_B, with their covariance.
- **Each prediction's se** is the delta method on the parameter covariance (no residual scatter added).
- **Arms, reported, never primary:**
  - **M12-1K:** int8 with one price k for F_walk + F_scp, the same joint fit.
  - **M12-KO:** int8 with one price fitted to the 20 kinds alone, beta_A and beta_B fixed at E182-A's and E182-B's values (the
    kinds-pass slope, E182-W-int8's analogue net of the held bits).
  - **M12-G (the level as a gain):** fp32 Df = g_f P10 + gamma_A pc_A + gamma_B pc_B, g_f in place of c_f, the same rows.
  - **M10-O and M10-G:** M10's own levels with an offset (D = P10 + c) or a gain (D = g P10), per format, c and g fitted on E182's kinds
    of that format (int8 20, fp32 4; fp16 takes fp32's): the test of gain against offset on M10's levels.
  - **F16-NOHB:** fp16 with c_f only (no held-bit term).
  - **M12-S1 (a session anchor, chosen after a look; section 6):** the int8 part's c8 moved per session by that session's own random
    int8 anchor, D(int8.full, session) - D(int8.full, E182), each the mean over its kept passes (`e178.json` / `e182.json` > `items`).

## 4. The held-out test (computed after this file is committed)

**Rows, never fitted:** E178's 40 kinds (int8 13, fp32 14, fp16 13) and his pair E178-H-int8; pool 8's class S on aifoundry3 (E171): the
10 new `s8_onebit` tiles (8 priority 1, 2 priority 2) and its 3 re-run single-bit tiles, the re-runs reported apart; the same on card 1
(E172), secondary.

**For each row:** the residual e = D - D_M12 and its 95% interval e +- sqrt((t(0.975, n - 1) sd / sqrt n)^2 + (1.96 se_pred)^2), n the
row's kept passes; M10's residual beside it. For his pair: M12's D(5s) - D(4s) at E178's rate against E178-H-int8's interval.

**For each group** (E178 int8, fp32, fp16; E178 all 40; class S new, priority 1, re-runs): rms, bias (mean e), centred rms (the sd of
e about its mean: the shape with the level taken out), M10's three beside, and the paired difference rms(M12) - rms(M10) with its 95%
interval by a bootstrap over the group's rows (2,000 draws, `random.Random(1570)`), and the same for each arm.

**Gain against offset** (on E178's rows, by format, for M10-O against M10-G and for M12 against M12-G): the difference of held-out rms,
gain minus offset, with its bootstrap interval. **OFFSET** if it is above 0 and its interval excludes 0; **GAIN** if below 0 and its
interval excludes 0; **NOT SEPARABLE** otherwise. The words are reported, never a verdict.

## 5. The candidate kinds for a next one-number run (operand words only), and their frozen forecasts

Chosen by the rule below before any forecast of them; each kind is a one-number tile (one A word, one B word); each pair is read as a
train, first kind minus second, in E182's form.

| set | kinds (A word, B word) | trains | what they test |
|---|---|---|---|
| **C8, the int8 +-1-byte quartets** at new products b = 3 (0x03, popcount 2) and b = 63 (0x3F, popcount 6) | (1, b), (b, 1), (-1, -b), (-b, -1): bytes 01/03, 03/01, ff/fd, fd/ff and 01/3f, 3f/01, ff/c1, c1/ff | Q3-swap (1, 3) - (3, 1); Q3-sign (-1, -3) - (1, 3); Q63-swap (1, 63) - (63, 1); Q63-sign (-1, -63) - (1, 63); X8 (1, 63) - (1, 3) | beta_A and beta_B blind at new products (inside a quartet the walk and the A/B distance are shared); X8 the two flip prices and beta_B together |
| **C32B, fp32 B-side held-bit slope** | A 0x3f800000 (1.0); B 0x3f8000ff (popcount 15), 0x3f80ffff (23), with the committed (1.0, 1.0) and (1.0, 0x3fffffff) | B23-B15, B15-B7 | gamma_B alone (A fixed) |
| **C32A, fp32 A-side held-bit slope** | B 0x3f800000; A 0x3f8000ff, 0x3f80ffff | A23-A15, A15-A7 | gamma_A alone (B fixed) |
| **C32S, fp32 swaps at smaller moves** | the C32B and C32A kinds, paired | S15 (1.0, 0x3f8000ff) - (0x3f8000ff, 1.0); S23 (1.0, 0x3f80ffff) - (0x3f80ffff, 1.0) | the placement term's linearity in the bits moved (8 and 16, against T5's 23) |
| **C16, an fp16 swap** | (0x3c00, 0x3fff) and (0x3fff, 0x3c00): words 0x3c003c00 and 0x3fff3fff | H16 (1.0, 0x3fff) - (0x3fff, 1.0) | rule F16-SAME, blind |
| **CEQ, equal popcount at different bit positions** | fp32 B 0x3f80000f (four low mantissa bits) and 0x3ff00000 (four high), popcount 11 each, A 1.0; and the A-side mirror | EB (1.0, 0x3ff00000) - (1.0, 0x3f80000f); EA (0x3ff00000, 1.0) - (0x3f80000f, 1.0) | a popcount term (M12: held-bit increment 0, only M10's walk) against a position-dependent one |

**Forecasts frozen in a new file** (`candidates-m12.json`, with `candidates-m12.md` and a freeze line with its sha256 and the time PST):
each kind's D under M12 and M10 (aifoundry3, s = 1, E182's median rates), each train's difference under M12 (with its se) and M10, and
each train's power at E182's train noise: a half-width of 0.0051 W at 32 units (64 int8 processes; 76 fp32 processes give 38 units at
the same half-width by E182's sizing rule): the chance the train's interval excludes 0 if M12 is true, and the separation of M12's and
M10's forecasts in units of the train's se. **A candidate for the next registration; nothing is registered here.**

## 6. Labels and disclosures

- **Post hoc:** every M12 parameter, and every held-out residual (the rows were not fitted, but they were not unseen; below).
  **Held out:** E178's 40 kinds, his pair and pool 8's class S, never fitted. **Blind:** nothing here; the candidates' forecasts become
  blind only if a later registration commits them before its first datum. **Reported:** every arm and every gain/offset word.
  **Registered:** nothing.
- **What this lane saw before writing this file**, while learning the committed files' layouts: E178's per-kind D, sd and D - P
  (`scored.json` > `primary` > `reported` > `kinds`), both sessions' anchor and zeros levels (`e178.json` and `e182.json` > `items`), and
  pool 8's class S rows on aifoundry3 and card 1 (`scored.json` > `primary` > `rows`). No M12 residual was computed on them. The design
  above was fixed after that look; **M12-S1 was added after it** (the two sessions' int8 zeros read about 0.1 W apart), so it is post
  hoc in the strong sense and reported only.
- **Exploration on E182's training rows only** (before this file): the int8 fits with one and with two flip prices (section 2) and the
  fp32 fit from T5 and T6.

## 7. Files (this directory)

`REFIT.md` (this file, committed alone first); then `m12_common.py`, `fit_m12.py` -> `m12.json` and `fit-m12.txt`; `heldout_m12.py` ->
`heldout-m12.json` and `heldout-m12.md`; `selftest_m12.py` (synthetic data) -> `logs/selftest-m12.txt`; `candidates_m12.py`,
`bench/bench_m12.sh` -> `bench/counts-m12.json`, `tiles/`, `candidates-m12.json`, `candidates-m12.md`, `FREEZE-m12.md`; `README.md`;
`SHA256SUMS-m12` (every file but itself and README.md).

SPDX-License-Identifier: Apache-2.0
