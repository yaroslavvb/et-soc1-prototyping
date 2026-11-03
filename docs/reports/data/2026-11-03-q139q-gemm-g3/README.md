# Q139(q): G3, a large GEMM's sustained power and governed clock on aifoundry2, from P0 through the frozen heat chain and the trip rule; E159's predictions frozen

*On the kinds page, [section 11, what is still open](https://spacesheep.dev/@yaroslavvb/horace-kinds-of-numbers#11-what-is-still-open): **item 1**
("Where a large GEMM falls") and **item 6** (the power model). It answers **rank 3** of Q138's final critic: "A large GEMM's sustained power and
governed clock on aifoundry2". That rank was set by E146's R5 miss on the fresh shape `F6`: fp32 random drew 56.15 W at 745 MHz where G2 said 52.5 W
at 800, and its window die read 3.6-4.6 °C over E136's law. The critic's desk check found that Q138(t)'s chain, given the measured watts, reads that die
to about 1 °C, so the miss is the power and clock path, not heat. Q139 runs on the owner's words of 2 November 2026: "feel free to settle any
unanswered questions regarding horace's power model", with the goal "to be able to predict the power requirement and heat generation of various kinds of
numeric computations as accurately as possible".*

*Tue 3 Nov 2026 (week 45), about 04:00-05:15 PST. Desk only: no card, no device command, no ssh. Everything here is computed from committed data:
E119, E126, E136 and E146's sessions; E136's and E146's frozen predictions; Q138(t)'s frozen chain (`model-q138t.json` a2, amendment A1 at
`c2f9920d`). **The check on the four sessions is post hoc.** Every run in it was committed before G3 was written, and two of G3's constants were
chosen on those runs (nested scores below). **E159 is G3's blind test.** Its design and predictions are frozen here, before any E159 claim.*

## The answer

**G3 reads a large GEMM's sustained clock to about 10 MHz, its board power to about 1.9 W and its window die to about 0.7 °C rms on 56 sustained runs,
scored leave one session out (post hoc). E136's law reads the same runs to 37.7 MHz, 3.7 W and 1.4 °C.** The power and clock path, not heat, carried
the miss. G3 takes E136's burst law P0 as the power at each clock. It closes that power through Q138(t)'s frozen chain and the governor's trip, and it
needs no sustained power cap fitted to earlier runs. The board-power error that remains is mostly P0's own level. Given each run's first second, G3
reads board power to 1.5 W. The registered E159 arms keep the two apart.

| arm (measured − predicted; 56 sustained runs of E119, E126, E136, E146; post hoc) | clock, MHz rms (mean) | inside 15 MHz | board, W rms (mean) | inside 2 W | window die, °C rms (mean) | inside 1 °C |
|---|---|---|---|---|---|---|
| **G3, nested** (each session scored with the constants chosen on the other three) | **10.8 (−6.7)** | 48 | **1.86 (−0.69)** | 34 | **0.72 (−0.31)** | 47 |
| G3, final constants (0.1 W/°C, 65.5 °C; chosen on all four, in sample) | 10.3 (−6.4) | 48 | 1.76 (−0.92) | 37 | 0.68 (−0.41) | 47 |
| G3 at Q138(t)'s constants (0.442 W/°C, 65.9 °C; nothing chosen here) | 18.4 (+5.4) | 40 | 2.68 (−2.00) | 33 | 1.16 (−0.91) | 36 |
| **E136's law** (footing G2 on the same P0 levels; its frozen die law; the "before") | 37.7 (−22.3) | 37 | 3.71 (−2.43) | 31 | 1.39 (+0.95) | 29 |
| Q138(t)'s chain on the measured board trace (heat alone, given the watts) | — | — | — | — | 0.39 (+0.12) | 54 |
| G3 given each run's own first second (P0's level scaled to its p800; a diagnostic) | 16.5 (−1.5) | — | 1.47 (−0.91) | — | 0.55 (−0.34) | — |

Sources: [`posthoc-g3.txt`](posthoc-g3.txt) / [`posthoc-g3.json`](posthoc-g3.json) for the arms at Q138(t)'s constants, E136's law, the chain and the
p800 diagnostic, and [`fit-g3.txt`](fit-g3.txt) / [`fit-g3.json`](fit-g3.json) (`nested_pooled`, `final`) for G3's nested and final rows.

**On `F6`, the fresh shape that set rank 3** (E146 R5; measured 745.1 MHz, 56.15 W, 65.3 °C for fp32 random and 794.1 MHz, 45.48 W, 61.7 °C for int8
full):

| arm | fp32 random: MHz, W, die | int8 full: MHz, W, die |
|---|---|---|
| G2, as E146 registered it (PS power, R5) | 800, 52.5, 60.7 (die FAIL +4.6) | 800, 42.7, 58.1 (die FAIL +3.6) |
| E136's law on P0's levels | 799.4, 57.9, 62.9 | 800, 44.7, 59.0 |
| G3 at Q138(t)'s constants | **735.3, 56.9, 65.9** | 800, 46.7, 62.0 |
| G3, final constants | 774.1, 56.6, 65.2 | 800, 45.1, 61.3 |

At the final constants G3 puts F6's die and board inside the critic's bands, but reads its fp32 clock 29 MHz high, outside 15. With E146 held out, the
nested choice (0.0 W/°C, 65.3 °C) reads it 36 MHz high (781 MHz). At Q138(t)'s constants G3 reads that clock to +10 MHz, but its
pooled error is twice the final constants' (18 against 10 MHz). So F6's clock sits at the edge of what G3 resolves. The critic's 15 MHz band is
about 1.5 times G3's nested rms, so on E159's three fp32 random holds a clock FAIL is likely on at least one.

## What G3 is

G3 is a time-stepped closed loop with a 0.2 s step, the chain's own grid: [`g3_model.py`](g3_model.py). It runs from the moment a sustained run starts.

- **Power at each clock: P0**, E136's burst law as frozen. For E136's GEMMs that is `cells.*.P_w`, for E146's shapes `cells.*.P0_w`, and for a new
  shape E146's `levels0` on the desk's line split, unchanged. For E119's and E126's arms in the post hoc check it is the law's arm form, with E107's
  pinned S and the session's own T(f) fit. P0 is never PS: the store energy term is dropped, as E146 R3/R4 recommended.
- **Leakage:** every level rises by k (T − T_start), with the run's start die as P0's reference (P0 is a first-second law). k is **0.1 W per °C**,
  chosen on the four sessions (below). Q138(t)'s idle slope of 0.442 is the registered arm.
- **The power limit:** E119's dither at the burst cap (66.15 ± 2.75 W) on the raised levels gives the highest clock the TDP allows.
- **The trip rule:** the governor holds the die at **65.5 °C**. That is E136's law's own trip value, chosen here over Q138(t)'s kinds-loop 65.9. At each
  step the power is the capped power, unless that would carry the chain's die past the trip. Then it is the power that puts the die at the trip (the
  chain's one-step inverse), never under the floor's level P(600) + leakage.
- **The clock:** the clock whose raised level gives that power (the dither's own interpolation).
- **The die:** Q138(t)'s frozen aifoundry2 chain (τ 1, 3, 10, 60 and 120 s; R 0.663 °C per board W in all).
- **Between kernels:** each process spends about 0.25 s on set-up and calibration and about 0.1 s on a tail. There the board is at half the switching
  power over the rest power (E146's two holds: 38.5 and 34.9 W off, 57.4 and 45.3 W on).
- **The start:** the chain runs open loop on the session's measured board trace up to the run's first process, anchored on the measured die over the
  20 s before it. After the start nothing measured enters: power, clock and die are all G3's.
- **The reading:** reduce_hpl's sustained window, the in-kernel samples of the last 40 s of work.

**The two constants chosen here** ([`fit_g3.py`](fit_g3.py)) are the leakage slope on P0 and the held die. They were chosen on a grid (k 0, 0.1, 0.2,
0.3, 0.442; trip 65.1-65.9 °C) by the critic's three bands combined into one loss, Σ (clock/15)² + (W/2)² + (die/1)². Leave one session out, the choices
were (0.0, 65.1), (0.1, 65.5), (0.1, 65.5) and (0.0, 65.3) for E119, E126, E136 and E146 held out. On all four the choice was 0.1 W/°C and 65.5 °C, and
those are frozen for E159. Nearby points score within 10% of the loss (0.0/65.5: 13.5 MHz, 1.64 W, 0.61 °C; 0.1/65.3: 9.7 MHz, 1.83 W, 0.69 °C). The
slope the GEMMs carry above their first second is about a quarter of the idle slope. P0 is a first-second law and already over-reads most bursts
(E146: −1.48 W mean), so a steep leakage term on top of it double counts.

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

## What this does to predicting power and heat

- **The term corrected** is the governed GEMM's sustained power and clock path. E136's sustained law had a fixed sustained cap (60.83 W, fitted to E126's
  held clocks) and a two-parameter die law. G3 replaces it with P0's levels, a small leakage slope, the burst cap, and the trip closed through Q138(t)'s
  chain.
- **Out of sample, before → after,** 56 sustained runs, leave one session out (post hoc):
  - clock: 37.7 → 10.8 MHz rms;
  - board power: 3.71 → 1.86 W;
  - window die: 1.39 → 0.72 °C.
- **F6 alone:** the die goes from +4.6 / +3.6 °C (G2, registered) to −0.6 / −0.3 °C at Q138(t)'s constants and +0.0 / +0.4 °C at the final constants.
  F6's clock goes from 800 against 745 MHz to 735 (Q138(t)'s constants) or 774 MHz (the final constants).
- **Heat:** the chain given the watts stays at 0.39 °C. The heat path carries over to the GEMM unchanged.
- **What remains** is P0's level: E136's line law misses bursts by about 2.7 W rms on E146. Given the first second, board power is 1.47 W and the die
  0.55 °C. The next term is P0's per-shape level, which depends on the L3's retention (critic rank 7, E158).
- **E159 is the blind test** of G3's constants and of P0 on three new shapes.

## Departures and limits

- **Post hoc, labelled.** The two constants were chosen on the 56 runs. The nested score is the honest out-of-sample number, the final constants' score
  is in sample, and E159 is blind.
- **One card, one governor build.** aifoundry2 only, under BL2 0.22.0's governor. Q138(t)'s chain was fitted on E111 and E133; nothing here refits it.
- **The trip is a level, not the firmware's controller.** G3 pins the die at a held reading. It does not model the 1 s steps or the whole-degree
  hysteresis, so the clock's fine structure inside a window is not predicted. Only the window means are.
- **E119's and E126's P0 levels** use each session's own T(f) fit, which is measured. Their clock and board scores are therefore slightly kinder than a
  bits-only prediction would be.
- **Time:** about 75 minutes, against the brief's 60.

## Files

| file | what |
|---|---|
| `g3_model.py` | G3: the closed loop, the schedule, the window means, E136's law arm; G3's frozen constants (`K_LEAK_G3`, `TRIP_G3`) |
| `posthoc_g3.py`, `posthoc-g3.txt`, `posthoc-g3.json`, `posthoc-g3-inputs.json` | the post hoc check on 56 runs at Q138(t)'s constants, every arm; the per-run inputs the grid uses |
| `fit_g3.py`, `fit-g3.txt`, `fit-g3.json` | the two constants: the grid, nested leave one session out, and the final choice |
| `e159_g3.py`, `predictions-e159.json`, `predictions-e159.txt` | **frozen for E159**: the design, the nominal predictions, the rules and arms, and the scorer |
| `selftest-e159.txt` | the scorer's self-test on E146's session |

## How to reproduce

```bash
cd docs/reports/data/2026-11-03-q139q-gemm-g3
python3 posthoc_g3.py > posthoc-g3.txt          # ~5 s; numpy (the desk's Python 3.9, numpy 1.26.4)
python3 fit_g3.py > fit-g3.txt                  # ~30 s
python3 e159_g3.py predict > predictions-e159.txt
python3 e159_g3.py selftest > selftest-e159.txt
python3 e159_g3.py score <E159 session dir> results-e159.json    # after E159
```

## Device commands sent

None. This lane opened no device and ran nothing on any box.
