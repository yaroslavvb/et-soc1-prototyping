# Q139(q): G3, a large GEMM's sustained power and governed clock on aifoundry2, from P0 through the frozen heat chain and the trip rule; E159's predictions frozen

*On the kinds page, [section 11, what is still open](https://spacesheep.dev/@yaroslavvb/horace-kinds-of-numbers#11-what-is-still-open): **item 1**
("Where a large GEMM falls") and **item 6** (the power model). It answers **rank 3** of Q138's final critic: "A large GEMM's sustained power and
governed clock on aifoundry2". That rank was set by E146's R5 miss on the fresh shape `F6`: fp32 random drew 56.15 W at 745 MHz where G2 said 52.5 W
at 800, and its window die read 3.6-4.6 °C over E136's law. The critic's desk check found that Q138(t)'s chain, given the measured watts, reads that die
to about 1 °C, so the miss is the power and clock path, not heat. Q139 runs on the owner's words of 2 November 2026: "feel free to settle any
unanswered questions regarding horace's power model", with the goal "to be able to predict the power requirement and heat generation of various kinds of
numeric computations as accurately as possible".*

*Tue 3 Nov 2026 (week 45), about 03:59-04:16 PST, about 20 minutes (C4). Desk only: no card, no device command, no ssh. Everything here is computed
from committed data: E119, E126, E136 and E146's sessions; E136's and E146's frozen predictions; Q138(t)'s frozen chain (`model-q138t.json` a2,
amendment A1 at `c2f9920d`). **The check on the four sessions is post hoc.** Every run in it was committed before G3 was written, two of G3's
constants were chosen on those runs (nested scores below), and G3's structure and its gap share were set on the same sessions (C3). **E159 is G3's
blind test.** Its design and predictions are frozen here, before any E159 claim.*

## Corrections after verification (Tue 3 Nov 2026, about 04:47-05:10 PST, before E159's claim)

The verifier re-ran every script byte for byte and re-derived all 56 runs with its own code, and the numbers hold. It found the following wrong:
- the reading of G3's leakage constant and of what remains;
- calling the 56 runs "large GEMMs";
- the out-of-sample labels;
- the stated times;
- the chain row's count and anchor;
- the missing intervals;
- how new E159's shapes are for P0;
- two hazards in the frozen scorer.

**C1-C8 correct the desk text in place** (the text at `91def7c4` is in git). **No frozen file changes.** `g3_model.py`, `e159_g3.py`,
`predictions-e159.json`, `predictions-e159.txt` and every other file the scorer imports or opens keep their bytes at `91def7c4`: 28 files, listed in
[`frozen-sha256.json`](frozen-sha256.json) and checked by `python3 score_e159.py check`. No constant, prediction, rule, arm, stop or design changes.
The numbers below come from [`posthoc_fix_g3.py`](posthoc_fix_g3.py) ([`posthoc-fix-g3.txt`](posthoc-fix-g3.txt),
[`posthoc-fix-g3.json`](posthoc-fix-g3.json), keys in brackets), which runs G3's committed code unchanged. They are post hoc.

- **C1 (major): G3's k = 0.1 W/°C is an effective constant, not the GEMM's leakage slope. "What remains is P0's level" is withdrawn.**
  - **The GEMM's own slope is about the idle one.** Inside runs at a fixed 800 MHz, the board rises 0.41-0.56 W per °C on the 4 runs whose window
    clock stays at 800 MHz (median 0.50). Over all 41 runs with at least 100 such samples and a die span of at least 3 °C, the median is 0.405
    (`leakage_slope_at_800MHz`). Q138(t)'s idle slope is 0.442.
  - **k absorbs P0's bias.** P0 over-reads each run's first second: p800 − P0(800) is −1.57 W mean and 2.77 W rms over the 56 runs
    (`P0_first_second_bias_W`). The die rises 5.6 °C on average from a run's start to its window, so at k = 0.1 instead of 0.442 the raised level
    sits 1.92 W lower there (`die_rise_start_to_window_C`), about P0's over-read.
  - **Given the level, the clock gets worse.** Given each run's first second, at G3's own constants (0.1, 65.5):
    - board: 1.76 → 1.50 W;
    - die: 0.68 → 0.55 °C;
    - clock: 10.3 → 16.6 MHz (mean −6.4 → −9.9) (`p800_diagnostic` `0.1|65.5`).

    So G3's clock skill partly rests on k offsetting P0's bias. With the level given (trip 65.5), the best k is 0.2-0.3 W/°C: board 1.22-1.29 W, die
    0.41-0.45 °C, clock 15.4-15.7 MHz. **The next gain needs P0's per-shape level and the clock mapping in the held state together.**
  - **The diagnostic row was at Q138(t)'s constants.** The row the table carried (16.5 MHz, 1.47 W, 0.55 °C) is at (0.442, 65.9), because
    `posthoc_g3.py` calls `simulate()` with its defaults. It is now labelled, and a row at G3's constants is added. The registered E159 diagnostic arm
    uses G3's constants (`e159_g3.py` `score`).
- **C2: the 56 runs are GEMM-pattern runs, and only 14 of them are large GEMMs.**
  - **The 42 others** are E119's and E126's arms of the vendor's GEMM pattern.
  - **On the 14 large-GEMM runs** (E136, E146), nested: 12.8 MHz, 1.21 W, 0.69 °C rms (12 / 11 / 12 of 14 inside). E136's law reads 28.0 MHz,
    2.17 W, 1.77 °C (10 / 11 / 2) (`subsets.large_gemms_E136_E146`). Paired over those 14, the gain is resolved for the clock ([1.4, 28.8] MHz) and
    the die ([0.63, 1.52] °C), but not for board power ([−0.21, 2.38] W).
  - **F6 out of sample** (E146 held out, k 0.0, trip 65.3; `F6`):
    - fp32 random reads 781.0 MHz, 56.15 W, 64.96 °C against 745.1, 56.15, 65.25 measured: the clock is 36 MHz high, the die 0.3 °C low;
    - int8 full reads 800, 44.71, 61.18 against 794.1, 45.48, 61.71.

    The F6 "after" figures quoted before (774 MHz, +0.0 / +0.4 °C) are at the final constants, which are in sample for F6.
  - **"F6's clock sits at the edge of what G3 resolves" is withdrawn.** 29-36 MHz is about three times G3's nested rms. The 15 MHz band is about
    1.4 times that rms, not 1.5.
- **C3: the before → after labels.** Read the before → after as:
  - nested in G3's two constants only;
  - E136's law partly in sample on E119 and E126;
  - G3's structure and gap share set on these sessions.

  The details:
  - **The after.** G3 was written and iterated on these runs. OFF_SHARE 0.5 came from E146's two sustained runs with the calibration dispatches
    counted as off; on the model's own kernel mask those runs give 0.40 and 0.44 (`gap_share_E146`).
  - **The before.** E136's law has G2's 60.827 W cap refitted on E126's five held runs, and its die law's shape constants fitted on E119's and
    E126's committed cells ([E136's README](../2026-11-02-e136-large-gemm/README.md), results and departures). So it is in sample on the 42
    E119/E126 runs.
  - **The effect of the unregistered choices is small** (`sensitivities_final_constants_in_sample`). G3 at its final constants (in sample) reads
    clock 9.7-12.2 MHz, board 1.72-1.89 W and die 0.59-0.80 °C across:
    - gap shares 0 to 1;
    - P_REF ±0.5 W, re-anchored as G3 runs (it moves almost nothing);
    - anchors of 5 and 60 s;
    - a 30 s window.

    The verifier's P_REF variant moved the reference inside the run only, a ±0.5 W step into the chain. It gave die 0.56-0.83 °C.
- **C4: the times.** This lane ran about 03:59-04:16 PST, about 20 minutes: its scratch files run 03:59:10-04:17:16, and the commit landed at
  04:16:13. It did not run "about 04:00-05:15", and not "75 minutes". The overrun line is dropped.
- **C5: the chain row.**
  - **The count** inside 1 °C is 56 of 56 (largest error 0.92 °C), not 54 (`chain_on_measured`).
  - **The anchor.** Its 0.39 °C is at G3's own anchor: each run is anchored on the measured die over the 20 s before its first process. Q139(c)'s
    committed check reads the same 56 windows at 0.47, 0.49 and 0.63 °C with the first-gate, run-start and rest anchors
    ([`../2026-11-03-q139c-critic-checks/chain_gemm.json`](../2026-11-03-q139c-critic-checks/chain_gemm.json) `pooled`).
  - **The law's footing.** E136's law's 1.39 °C here is the law fed P0's power. On the measured watts, Q139(c) reads it at 2.18 °C (same file,
    `pooled.e136_law`).
- **C6: intervals** (95% bootstrap on the rms, 10,000 resamples; `intervals`):

  | | clock, MHz | board, W | die, °C |
  |---|---|---|---|
  | G3 nested, over the 56 runs | [8.5, 13.2] | [1.60, 2.11] | [0.60, 0.83] |
  | G3 nested, over the four sessions as clusters | [9.4, 15.2] | [1.21, 2.20] | [0.47, 0.87] |
  | E136's law, over the 56 runs | [27.5, 46.6] | [2.82, 4.52] | [1.17, 1.58] |
  | paired: the law's rms minus G3's | [17.4, 35.5] | [0.96, 2.70] | [0.40, 0.93] |

  So over all 56 runs the gain is resolved on all three quantities.
- **C7: E159 is new for P0 at one point** (a dated note on the design section, below; the design is unchanged; `E159_levels_beside_fit_set`).
  - **H3's levels are g2k's.** H3 (`gemmL1x2x2`: 176 L3 lines an op, 0 fresh) has E146's L2 split, which is E136's `g2k`. Its P0 levels equal
    g2k's exactly: 47.5 / 56.25 / 68.12 W fp32 random, 33.24 / 38.22 / 45.98 W int8 full, 28.34 / 31.9 / 38.12 W zeros. g2k's fp32 random and zeros
    sustained runs are in G3's fit set, where G3 at the final constants reads g2k fp32 random's clock 16.8 MHz high.
  - **H1's levels sit beside fitted ones.** Its P0(800) (57.09 W fp32 random, 44.62 W int8) sits beside D8 (= g4k: 57.53, 44.67) and F6 (57.98,
    44.71), both in the fit set.
  - **Only H2 (160 / 32) is a new point** for P0's line law. All three shapes are blind for G3's two constants, and nothing of E159 exists.
- **C8: the frozen scorer's hygiene** (no frozen file edited).
  - **The docstring.** `g3_model.py`'s docstring gives 0.442 W/°C and 65.9 °C as G3's leakage and trip. Those are Q138(t)'s constants, kept as
    `K_LEAK` / `T_TRIP` for the registered arm. G3's frozen constants are `K_LEAK_G3` 0.1 and `TRIP_G3` 65.5, and `e159_g3.py` scores G3 with them.
  - **The self-test.** `e159_g3.py selftest` rewrites the frozen `predictions-e159.json` in place and restores it in a `finally`, so an interrupted
    self-test would leave F6's levels in H1's cells.
  - **The hash check.** `score()` checks no hash.

  New, beside the frozen files, [`score_e159.py`](score_e159.py):
  - `check`: the 28 files the scorer imports or opens equal their bytes at `91def7c4` ([`frozen-sha256.json`](frozen-sha256.json));
  - `selftest`: the same self-test, with its relabelled predictions in a temp dir. [`selftest-score-e159.txt`](selftest-score-e159.txt) prints what
    `selftest-e159.txt` holds, and the frozen file's sha256 is unchanged after;
  - `score`: the check, then `e159_g3.score` unchanged.

  **The E159 lane runs `score_e159.py check` before its claim and `score_e159.py score` after; never `e159_g3.py selftest`.**

## The answer

**On 56 sustained GEMM-pattern runs on aifoundry2, scored leave one session out (post hoc), G3 reads the sustained clock to 10.8 MHz, the board to
1.86 W and the window die to 0.72 °C rms. E136's law reads the same runs to 37.7 MHz, 3.71 W and 1.39 °C.** The 56 are E119's and E126's 42 arm runs
and E136's and E146's 14 large GEMMs. On the 14 large GEMMs alone, G3 reads 12.8 MHz, 1.21 W and 0.69 °C, against the law's 28.0 MHz, 2.17 W and
1.77 °C (C2).

The power and clock path, not heat, carried the miss. G3 takes E136's burst law P0 as the power at each clock. It closes that power through Q138(t)'s
frozen chain and the governor's trip, and it needs no sustained power cap fitted to earlier runs. Its leakage constant (0.1 W/°C) is an effective one:
it offsets P0's over-read of each run's first second, while the GEMM's own slope is about the idle 0.44 (C1). Given each run's first second, the board
error falls 1.76 → 1.50 W but the clock error rises 10.3 → 16.6 MHz. **The next gain needs P0's per-shape level and the clock mapping in the held
state together.** The registered E159 arms keep the two apart.

| arm (measured − predicted; 56 sustained GEMM-pattern runs of E119, E126, E136, E146; post hoc) | clock, MHz rms (mean) [95%] | inside 15 MHz | board, W rms (mean) [95%] | inside 2 W | window die, °C rms (mean) [95%] | inside 1 °C |
|---|---|---|---|---|---|---|
| **G3, nested** (each session scored with the constants chosen on the other three) | **10.8 (−6.7)** [8.5, 13.2] | 48 | **1.86 (−0.69)** [1.60, 2.11] | 34 | **0.72 (−0.31)** [0.60, 0.83] | 47 |
| G3, final constants (0.1 W/°C, 65.5 °C; chosen on all four, in sample) | 10.3 (−6.4) [8.4, 12.2] | 48 | 1.76 (−0.92) [1.51, 2.01] | 37 | 0.68 (−0.41) [0.56, 0.81] | 47 |
| G3 at Q138(t)'s constants (0.442 W/°C, 65.9 °C; nothing chosen here) | 18.4 (+5.4) [14.1, 22.3] | 40 | 2.68 (−2.00) [2.16, 3.20] | 33 | 1.16 (−0.91) [0.93, 1.37] | 36 |
| **E136's law** (footing G2 on the same P0 levels, so on P0's power, not the measured watts; its frozen die law; the "before", partly in sample on E119/E126, C3) | 37.7 (−22.3) [27.5, 46.6] | 37 | 3.71 (−2.43) [2.82, 4.52] | 31 | 1.39 (+0.95) [1.17, 1.58] | 29 |
| Q138(t)'s chain on the measured board trace (heat alone, given the watts; each run anchored on the 20 s before it, C5) | — | — | — | — | 0.39 (+0.12) [0.32, 0.45] | 56 |
| G3 given each run's own first second, at Q138(t)'s constants (0.442, 65.9; P0's level scaled to its p800; a diagnostic) | 16.5 (−1.5) | — | 1.47 (−0.91) | — | 0.55 (−0.34) | — |
| G3 given each run's own first second, at G3's constants (0.1, 65.5; the registered diagnostic arm; C1) | 16.6 (−9.9) | — | 1.50 (+0.32) | — | 0.55 (+0.19) | — |

Sources: [`posthoc-g3.txt`](posthoc-g3.txt) / [`posthoc-g3.json`](posthoc-g3.json) for the arms at Q138(t)'s constants, E136's law, the chain and the
first p800 row; [`fit-g3.txt`](fit-g3.txt) / [`fit-g3.json`](fit-g3.json) (`nested_pooled`, `final`) for G3's nested and final rows;
[`posthoc-fix-g3.json`](posthoc-fix-g3.json) for the intervals (`intervals`), the chain's count (`chain_on_measured`) and the second p800 row
(`p800_diagnostic`).

**By subset** (nested; `posthoc-fix-g3.json` `subsets`):

| subset | G3 nested: clock, board, die rms (inside) | E136's law | paired gain, law − G3 [95%] |
|---|---|---|---|
| the 14 large GEMMs (E136, E146) | 12.8 MHz, 1.21 W, 0.69 °C (12 / 11 / 12) | 28.0, 2.17, 1.77 (10 / 11 / 2) | clock [1.4, 28.8], board [−0.21, 2.38], die [0.63, 1.52] |
| the 42 GEMM-pattern arms (E119, E126) | 10.0 MHz, 2.03 W, 0.73 °C (36 / 23 / 35) | 40.4, 4.09, 1.23 (27 / 20 / 27) | |

**On `F6`, the fresh shape that set rank 3** (E146 R5; measured 745.1 MHz, 56.15 W, 65.3 °C for fp32 random and 794.1 MHz, 45.48 W, 61.7 °C for int8
full):

| arm | fp32 random: MHz, W, die | int8 full: MHz, W, die |
|---|---|---|
| G2, as E146 registered it (PS power, R5) | 800, 52.5, 60.7 (die FAIL +4.6) | 800, 42.7, 58.1 (die FAIL +3.6) |
| E136's law on P0's levels | 799.4, 57.9, 62.9 | 800, 44.7, 59.0 |
| G3 at Q138(t)'s constants | 735.3, 56.9, 65.9 | 800, 46.7, 62.0 |
| **G3, nested** (E146 held out: 0.0 W/°C, 65.3 °C; out of sample, C2) | **781.0, 56.15, 64.96** | **800, 44.71, 61.18** |
| G3, final constants (in sample for F6) | 774.1, 56.6, 65.2 | 800, 45.1, 61.3 |

Out of sample, G3 reads F6's fp32 random clock 36 MHz high (781 MHz) and its die 0.3 °C low. int8 full is inside all three bands. At the final
constants, which are in sample for F6, the fp32 clock is 29 MHz high (774 MHz). At Q138(t)'s constants G3 reads that clock to +10 MHz, but its pooled
error is nearly twice the final constants' (18 against 10 MHz). A 29-36 MHz miss is about three times G3's nested rms: a miss, not the edge of what G3
resolves (C2). The critic's 15 MHz band is about 1.4 times G3's nested rms, so on E159's three fp32 random holds a clock FAIL is likely on at least one.

## What G3 is

G3 is a time-stepped closed loop with a 0.2 s step, the chain's own grid: [`g3_model.py`](g3_model.py). It runs from the moment a sustained run starts.

- **Power at each clock: P0**, E136's burst law as frozen. For E136's GEMMs that is `cells.*.P_w`, for E146's shapes `cells.*.P0_w`, and for a new
  shape E146's `levels0` on the desk's line split, unchanged. For E119's and E126's arms in the post hoc check it is the law's arm form, with E107's
  pinned S and the session's own T(f) fit. P0 is never PS: the store energy term is dropped, as E146 R3/R4 recommended.
- **Leakage:** every level rises by k (T − T_start), with the run's start die as P0's reference (P0 is a first-second law). k is **0.1 W per °C**,
  chosen on the four sessions (below). It is an effective constant, not the GEMM's leakage slope, which is about the idle one (C1). Q138(t)'s idle
  slope of 0.442 is the registered arm.
- **The power limit:** E119's dither at the burst cap (66.15 ± 2.75 W) on the raised levels gives the highest clock the TDP allows.
- **The trip rule:** the governor holds the die at **65.5 °C**. That is E136's law's own trip value, chosen here over Q138(t)'s kinds-loop 65.9. At each
  step the power is the capped power, unless that would carry the chain's die past the trip. Then it is the power that puts the die at the trip (the
  chain's one-step inverse), never under the floor's level P(600) + leakage.
- **The clock:** the clock whose raised level gives that power (the dither's own interpolation).
- **The die:** Q138(t)'s frozen aifoundry2 chain (τ 1, 3, 10, 60 and 120 s; R 0.663 °C per board W in all).
- **Between kernels:** each process spends about 0.25 s on set-up and calibration and about 0.1 s on a tail. There the board is at half the switching
  power over the rest power (E146's two holds: 38.5 and 34.9 W off, 57.4 and 45.3 W on). Those means count the calibration dispatches as off. On the
  model's own kernel mask, the two runs give 0.40 and 0.44 (C3).
- **The start:** the chain runs open loop on the session's measured board trace up to the run's first process, anchored on the measured die over the
  20 s before it. After the start nothing measured enters: power, clock and die are all G3's.
- **The reading:** reduce_hpl's sustained window, the in-kernel samples of the last 40 s of work.

**The two constants chosen here** ([`fit_g3.py`](fit_g3.py)) are the leakage slope on P0 and the held die. They were chosen on a grid (k 0, 0.1, 0.2,
0.3, 0.442; trip 65.1-65.9 °C) by the critic's three bands combined into one loss, Σ (clock/15)² + (W/2)² + (die/1)². Leave one session out, the choices
were (0.0, 65.1), (0.1, 65.5), (0.1, 65.5) and (0.0, 65.3) for E119, E126, E136 and E146 held out. On all four the choice was 0.1 W/°C and 65.5 °C, and
those are frozen for E159. Nearby points score within 10% of the loss (0.0/65.5: 13.5 MHz, 1.64 W, 0.61 °C; 0.1/65.3: 9.7 MHz, 1.83 W, 0.69 °C). k =
0.1 is an effective constant: it absorbs P0's mean over-read of the first second (−1.57 W on these runs). Inside a run at a fixed 800 MHz, the board
rises 0.41-0.56 W per °C, about the idle slope (C1).

## E159: the design and the frozen predictions

[`predictions-e159.json`](predictions-e159.json), printed in [`predictions-e159.txt`](predictions-e159.txt), is written by
[`e159_g3.py`](e159_g3.py) `predict` from committed inputs only.

**Three shapes nobody has run**, all on E136's binary unchanged (rgm136 `SP_GEMM_LARGE`; any `gemmL<MB>x<NB>x<KB>` is an argument). The line counts are
E146's desk split at a 32 MB L3, unchanged. KB = 1 is avoided, since E146 found the desk wrong there.

| hold | arm | M × N × K (fp32) | with C | C store every | lines an op missing the L2: L3 / fresh | fp32 random P0 600/700/800 W | predicted peak (P0(800) + 8.51 W) |
|---|---|---|---|---|---|---|---|
| H1 | `gemmL2x4x8` | 2,048 × 2,048 × 4,096 | 80 MB, streams | 256 ops | 100.1 / 91.9 | 41.0 / 47.6 / 57.1 | 65.6 W |
| H2 | `gemmL4x2x4` | 4,096 × 1,024 × 2,048 | 56 MB | 128 | 160.0 / 32.0 | 44.4 / 52.0 / 62.6 | 71.1 W |
| H3 | `gemmL1x2x2` | 1,024 × 1,024 × 1,024 | 12 MB, the L3 holds it | 64 | 176.0 / 0 | 47.5 / 56.2 / 68.1 | 76.6 W |

- **Kinds:** fp32 random, int8 full and fp32 zeros on each shape, nine holds. The three fp32 random levels (57, 63, 68 W at 800 MHz) put the trip
  regime at three different clocks.
- **The order:** H1 fp32, H1 int8, H2 fp32, H2 int8, H3 fp32, H3 int8, then the three zeros. **The registered subset** is the first six.
- **A hold** is 12 processes of `--seconds 8` (budget 9.5, tail 6), about 106 s, from a cool start at or below 57 °C (E146's sustained gate). The last
  40 s are read.
- **The power rule** (section 22): the predicted peak is P0(800) + 8.51 W, the largest 10 Hz excursion over P0(800) in the 56 committed sustained runs.
  It must be at most 82 W. Every hold passes, the highest at 76.6 W (H3 fp32 random).
- **The stops:** board above 85 W on 3 live samples in a row, or a die reading at or above 76 °C, ends the session. Both are tested on live samples in
  the smoke, with E146's stoptest-board (30 W) and stoptest-die (30 °C).
- **Card time:** about 31 card-minutes planned (nine holds, their cool-downs, the smoke and the stop tests), cap 40. The subset takes about 22.
- **Device commands:** E146's chain unchanged, and every command is READ. The E159 lane re-runs `tools/claims-v3/dmcmd_audit.py` before its claim.

*Dated note, C7 (Tue 3 Nov 2026, after verification, before E159's claim; the design above is unchanged).* The three shapes are new for G3's two
constants, but only H2 is a new point for P0's line law. H3's split (176 L3 lines an op, 0 fresh, a store every 64 ops) is E146's L2 and E136's
`g2k`. So its P0 levels equal g2k's exactly in all three kinds: 47.5 / 56.25 / 68.12 W fp32 random, 33.24 / 38.22 / 45.98 W int8 full, and 28.34 /
31.9 / 38.12 W zeros. g2k's fp32 random and zeros sustained runs are in G3's fit set. H1's P0(800), 57.09 W fp32 random, sits beside D8's (= g4k)
57.53 W and F6's 57.98 W (`posthoc-fix-g3.json` `E159_levels_beside_fit_set`).

**G3's predictions at two nominal starts** (the primary is computed per hold from the hold's own measured start, below). "rest" starts at a 46.0 °C
rest; "gate57" starts after the same shape's governed fp32 random hold, idled to 57 °C:

| hold | G3 from rest: MHz, W, die | **G3 from the 57 °C gate** | G3 at Q138(t)'s constants, gate57 | E136's law, gate57 |
|---|---|---|---|---|
| H1 fp32 random | 799.2, 58.83, 64.18 | **748.8, 53.09, 65.49** | 722.3, 53.7, 65.9 | 799.8, 57.1, 63.7 |
| H1 int8 full | 800, 45.79, 57.73 | **800, 44.99, 60.69** | 800, 46.6, 61.5 | 800, 44.6, 58.5 |
| H1 zeros | 800, 39.30, 54.53 | **800, 38.50, 57.50** | 800, 38.8, 57.7 | 800, 38.5, 56.0 |
| H2 fp32 random | 741.0, 58.31, 65.45 | **697.4, 52.79, 65.49** | 666.0, 53.5, 65.9 | 781.3, 62.1, 65.5 |
| H2 int8 full | 800, 46.36, 58.00 | **800, 45.56, 61.03** | 800, 47.3, 61.9 | 800, 45.2, 58.8 |
| H2 zeros | 800, 39.07, 54.41 | **800, 38.27, 57.44** | 800, 38.5, 57.6 | 800, 38.2, 55.9 |
| H3 fp32 random | 683.9, 56.99, 65.49 | **649.4, 52.74, 65.50** | 622.2, 53.4, 65.9 | 738.6, 62.1, 65.5 |
| H3 int8 full | 800, 47.22, 58.43 | **800, 46.43, 61.47** | 800, 48.4, 62.4 | 800, 46.0, 59.1 |
| H3 zeros | 800, 38.95, 54.35 | **800, 38.16, 57.39** | 800, 38.4, 57.6 | 800, 38.1, 55.8 |

So G3 says the governor holds every fp32 random shape at the trip in the window, at 650-750 MHz from a warm gate, even where P0(800) is under the TDP. It
also says the clock falls with the shape's power: H1 about 750, H2 about 700, H3 about 650 MHz. E136's law calls H1 unheld at 800 MHz and holds H2 and H3
at 62 W. int8 and zeros stay at 800 MHz under the trip.

**The rules** (the critic's; `predictions-e159.json` `rules`). For each hold, G3's mechanical prediction is computed with these levels and constants,
from the session's measured state before the hold and on the hold's own kernel windows. Measured minus predicted:

- **clock** within 15 MHz;
- **board** within 2 W;
- **window die** within 1 °C.

A quantity PASSES when every scored hold is inside; otherwise it FAILS, with the count given. Each arm's rms is reported beside G3, and G3 beats E136's
law on a quantity when its rms is lower. The registered arms are:

- G3 at Q138(t)'s constants;
- Q138(t)'s chain on the measured trace (heat given the watts, die only; it reads the 56 runs to 0.39 °C);
- E136's law, the old arm;
- G3 given the hold's first second, a diagnostic with no verdict.

Attribution, registered: a G3 clock or board miss on a hold whose first-second power is more than 4 W from P0(800) (E146 R3's band) is P0's level. A
die miss where the chain on the measured trace is inside 1 °C is the power path, not heat.

**The scorer:** `e159_g3.py score <E159 session dir> [out.json]`. It needs `runs.jsonl` (each hold labelled as the cell, `processes` ≥ 2),
`launches.jsonl.gz` and `tel/`, in run_hpl's formats. Its self-test (`e159_g3.py selftest`, [`selftest-e159.txt`](selftest-e159.txt)) runs E146's
session through it with F6's holds relabelled as E159 cells at F6's own P0. The code path works, and it returns clock 1 of 2 (the 29 MHz F6 miss above),
board 2 of 2 and die 2 of 2.

*Dated note, C8 (Tue 3 Nov 2026, after verification, before E159's claim; the scorer above is unchanged).* Run it as
`python3 score_e159.py score <E159 session dir> [out.json]`: that checks the 28 files the scorer reads against their bytes at `91def7c4`, then calls
`e159_g3.score` unchanged. Run the self-test as `python3 score_e159.py selftest`
([`selftest-score-e159.txt`](selftest-score-e159.txt)), never as `e159_g3.py selftest`, which rewrites `predictions-e159.json` in place while it
runs. G3 is scored with `K_LEAK_G3` 0.1 and `TRIP_G3` 65.5; the 0.442 and 65.9 in `g3_model.py`'s docstring are the Q138(t)-constants arm's.

## What this does to predicting power and heat

- **The term corrected** is the governed GEMM's sustained power and clock path. E136's sustained law had a fixed sustained cap (60.83 W, fitted to E126's
  held clocks) and a two-parameter die law. G3 replaces it with P0's levels, a small effective leakage constant (C1), the burst cap, and the trip closed
  through Q138(t)'s chain.
- **Before → after,** 56 sustained GEMM-pattern runs, leave one session out (post hoc). This is nested in G3's two constants only. E136's law is partly
  in sample on E119/E126. G3's structure and gap share were set on these sessions (C3).
  - clock: 37.7 → 10.8 MHz rms [8.5, 13.2];
  - board power: 3.71 → 1.86 W [1.60, 2.11];
  - window die: 1.39 → 0.72 °C [0.60, 0.83].

  On the 14 large GEMMs: 28.0 → 12.8 MHz, 2.17 → 1.21 W (the board gain not resolved there), 1.77 → 0.69 °C.
- **F6 alone, out of sample** (E146 held out): the die goes from +4.6 / +3.6 °C (G2, registered) to +0.3 / +0.5 °C. The fp32 clock goes from 800
  against 745 MHz to 781 MHz, 36 MHz high. At the final constants, in sample for F6, the die is +0.0 / +0.4 °C and the clock 774 MHz. At Q138(t)'s
  constants they are −0.6 / −0.3 °C and 735 MHz.
- **Heat:** the chain given the watts reads these runs to 0.39 °C at G3's 20 s anchor, and to 0.47-0.63 °C at Q139(c)'s three anchors (C5). The heat
  path carries over to the GEMM unchanged.
- **What remains is not P0's level alone** (C1). Given each run's first second, at G3's own constants, the board error falls 1.76 → 1.50 W and the die
  0.68 → 0.55 °C. But the clock error rises 10.3 → 16.6 MHz, because k = 0.1 offsets P0's −1.57 W mean over-read. With the level given, the best k is
  0.2-0.3 W/°C. **The next gain needs P0's per-shape level (it depends on the L3's retention: critic rank 7, E158) and the clock mapping in the held
  state together.**
- **E159 is the blind test** of G3's two constants on three shapes nobody has run. For P0's line law only H2 is a new point: H3's levels are g2k's, and
  H1's sit beside D8's and F6's (C7).

## Departures and limits

- **Post hoc, labelled.** The two constants were chosen on the 56 runs, and G3's structure and its gap share were set on these sessions (C3). The
  nested score is out of sample in the two constants only. The final constants' score is in sample. E159 is blind.
- **One card, one governor build.** aifoundry2 only, under BL2 0.22.0's governor. Q138(t)'s chain was fitted on E111 and E133; nothing here refits it.
- **The trip is a level, not the firmware's controller.** G3 pins the die at a held reading. It does not model the 1 s steps or the whole-degree
  hysteresis, so the clock's fine structure inside a window is not predicted. Only the window means are.
- **E119's and E126's P0 levels** use each session's own T(f) fit, which is measured. Their clock and board scores are therefore slightly kinder than a
  bits-only prediction would be.

## Files

| file | what |
|---|---|
| `g3_model.py` | G3: the closed loop, the schedule, the window means, E136's law arm; G3's frozen constants (`K_LEAK_G3`, `TRIP_G3`) |
| `posthoc_g3.py`, `posthoc-g3.txt`, `posthoc-g3.json`, `posthoc-g3-inputs.json` | the post hoc check on 56 runs at Q138(t)'s constants, every arm; the per-run inputs the grid uses |
| `fit_g3.py`, `fit-g3.txt`, `fit-g3.json` | the two constants: the grid, nested leave one session out, and the final choice |
| `e159_g3.py`, `predictions-e159.json`, `predictions-e159.txt` | **frozen for E159**: the design, the nominal predictions, the rules and arms, and the scorer |
| `selftest-e159.txt` | the scorer's self-test on E146's session |
| `posthoc_fix_g3.py`, `posthoc-fix-g3.txt`, `posthoc-fix-g3.json` | corrections after verification (C1-C7, post hoc): every arm per run, intervals, subsets, F6 out of sample, P0's bias, the p800 diagnostic on a k grid, the slope at 800 MHz, sensitivities, the gap share, E159's levels beside the fit set |
| `score_e159.py`, `frozen-sha256.json`, `selftest-score-e159.txt` | C8: the frozen scorer run behind a sha256 check of the 28 files it reads, and its self-test without writing into the tree |

## How to reproduce

```bash
cd docs/reports/data/2026-11-03-q139q-gemm-g3
python3 posthoc_g3.py > posthoc-g3.txt          # ~5 s; numpy (the desk's Python 3.9, numpy 1.26.4)
python3 fit_g3.py > fit-g3.txt                  # ~30 s
python3 e159_g3.py predict > predictions-e159.txt
python3 posthoc_fix_g3.py > posthoc-fix-g3.txt  # ~80 s; the corrections' numbers
python3 score_e159.py check                     # the 28 files the scorer reads, against 91def7c4
python3 score_e159.py selftest > selftest-score-e159.txt   # not e159_g3.py selftest (C8)
python3 score_e159.py score <E159 session dir> results-e159.json    # after E159
```

## Device commands sent

None. This lane opened no device and ran nothing on any box.
