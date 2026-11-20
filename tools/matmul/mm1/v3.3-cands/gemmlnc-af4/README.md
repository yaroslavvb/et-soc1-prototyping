# gemmLnc term AF4: a replacement for MM1-v3.2's gemmLnc term F3 that is right at both ends, and E220's frozen forecasts by 'MM1-v3.2 + AF4'

*Fri 20 Nov 2026 (week 47), Pacific time, 05:05-05:55 PST. Round Q234, lane lnc-form (track G). Desk only: no card, no simulator, no ssh, no
booking. Interpreter for every number: `/usr/bin/python3` 3.12.3 with numpy 1.26.4 and scipy 1.11.4, `-I -B`, single threaded (the four
thread variables at 1) inside the round's CPU slots, one slot job at a time, at a 1-minute load under 2. Labels: **post hoc** (every
constant and the design of every new form: their data existed and were looked at first, section 0 of the declaration); **held out**
(left out of the fit that scores it, not blind); **blind** (data that did not exist when the forecast was frozen: E220's, once these hashes are
posted or pushed before its first card command); **REPORTED** (printed beside a rule, never deciding it); **NOT RUN**. Error = forecast /
measured - 1, rms and bias in %. No E220 datum was opened.*

The owner's words that started the matmul model (Mon 16 Nov 2026; a voice transcription in which "matte mold" is the matmul): "I want you to
focus on the matte mold most of all, so I want to have a model which predicts matte mold energy and number of transistor switches and clock
cycles. From based on what I know about the size of a matrix and which operations are contained."

## The answer in five lines

1. **The lead.** F3 (MM1-v3.2: dW = S (c1 dup + c2 first), first = beyond / NB; c1 247.7, c2 448.6 pJ a line) over-predicts the extra
   power where the real excess is small (MM1-v3.2 as landed, W over idle given t: E216's g01 +12.4% and g07-g10 +5.1 to +6.3%; E218's NB
   5-15 points +3.6 to +11.2%; aifoundry3's NB-1 points with A fresh, E213 a082, E215 a031, a032, E218 g09, g10, g12, +5.4 to +10.2%) and
   **under**-predicts it at E218's large-KB points
   (g04 -19%, g08 -24%, g11 -13%).
2. **What the data show.** Over 36 committed gemmLnc points on three cards, the measured excess falls into regimes, each with its own
   measured gemmLnc / gemmL op-time ratio and its own NoC-rail excess: about **5.4 nJ a minion-op** (the 26 duplicate L2 reads alone; gemmLnc
   10-13% faster than its twin; NoC +0.5-0.7 W) wherever the row's A panel is re-used from the L3; about **11-14 nJ** while A streams fresh
   into the row (NB 1, or NB 2 with MB >= 2; NoC +1.8-2.1 W); about **21 nJ** where the near reuse misses the L3 (large KB) or the whole GEMM
   is L3-resident (gemmLnc as slow as or slower than its twin; NoC +1.2-4.5 W). F3's 1 / NB cannot see the row's A reuse (MB = 1 is all reuse)
   nor the L3 edge (large KB).
3. **The form (AF4, two constants, declared and hashed at 05:30:58 PST before any fit).** E = c1 dup + c2 R4 pJ a minion-op, with
   R4 = Lres beyond + (1 - Lres) a3 (14 qA_b + 12 qBF): the re-fetched duplicates are A's 14 (and B's 12 of B lines from DRAM) while A comes
   fresh into the row (a3: 1 at NB 1 or when the near reuse misses MM1-v3.2's own first L3 edge x1 = 37.33 MB; one half at NB 2 with MB >= 2;
   0 otherwise), and every beyond-L2 duplicate when the whole GEMM fits under x1. **c1 236.3, c2 597.3 pJ a line** (all data).
4. **Held out** (the term's constants refitted without each experiment, MM1-v3.2's other constants unchanged): **LOEO 3.88% against F3
   refitted 8.69%** (and MM1-v3.2 as landed 8.95%) over the 36 points; E216's fold 1.54% (F3r 5.08%), E218's 2.84% (11.29%); LOCO aifoundry3
   4.74% (9.75%), aifoundry2 1.54% (5.08%), card 1 8.93% (13.02%). **Kept by the declared rule**: the margin (1 point) met by 4.8 points,
   MM1-v3.2's pooled LOEO without twins 5.048% -> 4.921% (allowed +0.05), a permuted-feature placebo beaten 100 of 100 times.
5. **E220's frozen forecasts** (`forecasts-e220-af4.csv` sha256 `3005869e...`, json `37ace71c...`, term `dfcd58a0...`; files written
   05:35:07, **final 05:35:36 PST**, before any E220 datum): 306 rows (arm A 84 points at 600 MHz; arm B 74 points at 799, 700 and 600 MHz);
   the 260 cooperative rows equal MM1-v3.2; at the 28 gemmLnc points (46 rows with arm B's three clocks) AF4 moves MM1-v3.2's W over idle by
   -1.7 to +5.9 W at the registered clocks: down where the row re-uses A or NB is 1 (E218's XG shapes on card 1), up at the large-KB G2 block
   (n01-n07) and xg04, xg08, xg11. **Safety (information):** arm B's gemmLnc rows
   at 799 MHz read 39.5-40.0 W over idle with the term (MM1-v3.2 34.0-34.5 W): planning peak 64.7-65.2 W plain, 71.4-72.0 W in E220's
   drop-line form, against its 70 W stop.

## 1. The data

36 points, every committed rgm136 gemmLnc energy point through E219 (`data/s01_points.json`, made by `scripts/s01_data.py`; sha256 in
`DECLARED.sha256`), each on the full chip with random data (34 fp32, 2 int8), and their 30 cooperative gemmL twins:

| experiment | card, clock | gemmLnc points | read from |
|---|---|---|---|
| E211 | aifoundry3 card 0, 600 MHz | c01c, c02c | MM1-v3.2's own records, `tools/matmul/mm1/v3.2/out/points_energy_v32.csv` |
| E213 | aifoundry3 card 0 (a075, a079, a082, a086, a087); aifoundry1 card 1 (k37, k40) | 7 | the same |
| E215 | aifoundry3 card 0 (a024, a026, a031, a032); aifoundry1 card 1 (b013) | 5 | the same |
| E216 | aifoundry2 card 0, governed, 799 MHz (route c) | g01-g10 | `docs/reports/data/2026-11-19-e216-blind-matmul-aifoundry2/data-e216.json` (E208's reducer, view 'win'): equal to the frozen scorer's measured_route_c W and op time at all 20 points and twins |
| E218 | aifoundry3 card 0, 600 MHz | g01-g12 | `docs/reports/data/2026-11-20-e218-blind-matmul-aifoundry3/data-e218.json`, E215's reading |

E212, E214, E217 and E219 hold no gemmLnc arm. **The base** is MM1-v3.2 frozen (params landed 4e386f75) with F3 removed, at each point's
measured clock, die, volts and governed base: `s01_data.py` re-makes MM1-v3.2's in-sample W given t at its 14 gemmLnc points and their twins
to 7e-15 W. No constant of MM1-v3.2 is refitted; the term replaces F3 alone. MM1-v3.2's base at the 30 twins (term 0): rms 2.69%, bias +1.27%.

### Table 1. The measured excess by regime (post hoc description; the regimes are AF4's, from MM1-v3.2's map and the token alone)

Excess = (W measured - base) / S, in nJ a minion-op, S = D sL n / t_op 1e-12 as F3's.

| regime | points | R4 | measured excess: mean (range) | gemmLnc / gemmL op time, measured | F3 at MM1-v3.2's constants |
|---|---|---|---|---|---|
| A re-used from the L3 within the row (R4 0) | E211 c02c, E213 a079, E215 a026, a024, E216 g01, g07-g10, E218 g01, g02, g03, g05, g06, g07 | 0 | **5.39 (4.25-6.02)** | 0.867-0.904 | 7.22-12.27 |
| L2-resident | E213 a087, k40 (card 1) | 0 | 6.95 (6.06-7.85) | 0.920 | 6.44 |
| NB 2, MB >= 2: half the A reads fresh into the row | E216 g02-g06 | 8.9 | **10.99 (10.58-11.19)** | 0.925-0.928 | 12.27 |
| NB 1: every A read fresh into the row | E213 a082, E215 a031, a032, E218 g09, g10, g12 | 14.0 | **14.14 (13.50-14.64)** | 0.964-0.975 | 18.11 |
| the whole GEMM L3-resident | E211 c01c, E213 a075, k37 (card 1) | 25-26 | 20.62 (15.96-25.02) | 0.967-0.969 | 10.18-18.11 |
| the near reuse misses the L3 (large KB) | E213 a086, E215 b013 (card 1), E218 g04, g08, g11 | 20.1-24.1 | **20.88 (19.73-22.89)** | 1.020-1.154 | 7.27-18.11 |

**The rails agree** (REPORTED, post hoc; committed telemetry, gemmLnc minus its twin): the NoC rail's excess is +0.49 to +0.70 W at every
R4-0 point on all three cards (E211 c02c 0.56, E213 a079 0.53, E216 g01 and g07-g10 0.49-0.54, E218 g01-g03, g05, g06 0.53-0.70) and +1.19 to
+4.53 W at every point AF4 gives re-fetches (E216 g02-g06 1.83-1.93; E218 g04, g08-g12 1.19-2.12; lnc-energy's committed E211 c01c 2.28, E213
a075, a082, a086 1.88-3.80, k37 4.53). At the large-KB points the minion rail falls (-0.3 to -0.8 W: gemmLnc runs slower) and the three rails
carry only 0.38-0.54 of the board excess (E218 g04, g08, g11), the reading of duplicates re-fetched from DRAM, beyond the three on-chip rails.
`scripts/s05_rails_e216.py` (E216: E208's reducer's own rail split in its win view) and `scripts/s06_rails_e218.py` (E218: lnc-energy's
committed rail reducer, its reading unchanged, on E218's session) -> `data/s05_rails_e216.json`, `data/s06_rails_e218_points.json`.

The reading behind the form (a description, not derived): while A streams fresh into the row, the 8 minions sharing an A line wait on one
fetch and stay in lockstep, so the duplicates arrive while the line is in flight and are fetched again; while the row re-uses A from the L3
the minions run free (gemmLnc 10-13% faster than its twin) and every duplicate finds the line in the L2.

## 2. The declaration (before any fit)

`DECLARED-lnc-form.md` (sha256 `7e1c01e4eaf758263d35778ba8c5ffb35ba21362ede5d3f9f85b2272cae0b414`) with one stub per form
(`DECLARED-<form>.md`), hashed together at **2026-11-20 05:30:58 PST** in `DECLARED.sha256` (mode 444), before any fit of any form. It
fixes: the data, the base, the features (from the token, the format and MM1-v3.2's frozen map only), the nine forms, the fit, the folds, the
keep rule with its margin, the pooled guard, the placebo, the choice and the frozen quantities. **Its section 0 discloses** that the per-point
excess table and three listings of it (`scripts/s01b_show.py`, `s01c_feat.py`, `s01d_groups.py`; no fit, no constant estimated) were looked
at before the forms were written: the new forms are post hoc in design. Two paths in `DECLARED.sha256` point into the lane's work folder;
here they are `data/s01_points.json` (byte for byte) and `scripts/s01_data.py` (its path lines made environment variables: `RUN-SHA256.txt`
holds every script's sha256 as it ran).

The forms (each 0 off gemmLnc; c1, c2 in [0, 10,000] pJ a line):

| form | E (pJ a minion-op) | constants |
|---|---|---|
| F3r (the comparator) | c1 dup + c2 first, first = beyond / NB | 2 |
| F1r, F2r, F4r | c1 dup; c1 dup + c2 beyond; c2 beyond (verify-lnc's siblings) | 1, 2, 1 |
| STEPr | c1 dup + c2 beyond [NB <= 3] (verify-lnc's step form) | 2 |
| AF1 | c1 dup + c2 a_f (14 qA_b + 12 qBF), a_f = (1 - phi) + phi m | 2 |
| AF2 | AF1 with the L3-resident clause: R = Lres beyond + (1 - Lres) R1 | 2 |
| AF3 | c1 dup + c2 a3 (14 qA_b + 12 qBF), a3 = 1 at NB 1 or m = 1, (1 - phi) at NB 2, else 0 | 2 |
| **AF4** | AF3 with the L3-resident clause: **R4 = Lres beyond + (1 - Lres) a3 (14 qA_b + 12 qBF)** | 2 |

dup = 26; beyond = 14 (1 - qA_L2) + 12 (1 - qB_L2); qA_b = 1 - qA_L2; qBF = B's fresh share; phi = 1 at MB = 1, else (NB - 1) / NB (MM1-v3's
line map: the share of A reads that are near reuse within a row); m = 1 when the row's A panel and one C block's B panel (2 KB sa + KB sb MB)
exceed x1; Lres = 1 when MM1's footprint is at or under x1; x1 = 37.334 MB is MM1-v3.2's own first L3 edge (its time theta). Q = (Q0 + Q1) / 2
is MM1-v3.2's map at its all-data constants.

**The fit**: relative least squares of W over idle given the measured op time (bvls). **Held out**: LOEO by experiment (deciding), LOCO by
card and LOPO (REPORTED), the base unchanged. **The keep rule**: LOEO at least 1.0 point under F3r's; MM1-v3.2's pooled LOEO without twins
(its 1,829-point record, 4.976%, plus E216's and E218's 22 gemmLnc points at its frozen forecasts) up by at most 0.05 points, in-fit gemmLnc
points priced at MM1-v3.2's own LOEO fold base (its fold W minus its fold F3, `out/holdout_v32.json`) plus the term refitted without that
experiment; a permuted-feature placebo (100 draws, numpy default_rng(20261120 + j)) beaten at least 95 times. **The choice**: the lowest
LOEO among kept forms (a 0.25-point window, then fewer constants, then the declared order).

## 3. The fit and the held-out record

`scripts/s02_fit.py` -> `data/fit-record.json` (the lane's `work/s02_fit.json`, sha256 `e87ae81c...`, with one path field made relative);
`logs/s02_fit.log`. A self-check (`scripts/s04_check.py`, `logs/s04_check.log`): plain numpy least squares re-makes AF4's and F3r's constants
and LOEO rms exactly (AF4 236.349, 597.345 pJ, LOEO 3.8794%; F3r 239.611, 396.193 pJ, 8.6877%).

### Table 2. Every declared form

| form | c1, c2 (pJ a line) | in sample rms (bias) | **LOEO** rms (bias) | LOCO rms (bias) | LOPO rms (bias) | pooled MM1 LOEO no twins | placebo wins / 100 | kept |
|---|---|---|---|---|---|---|---|---|
| F3r | 239.6, 396.2 | 8.34% (-0.12) | **8.69% (-0.22)** | 9.06% (+1.32) | 8.72% (-0.16) | 5.039% | 100 | comparator |
| F1r | 344.7 | 12.09% (-2.67) | **12.22% (-2.55)** | 12.14% (-2.40) | 12.55% (-2.52) | 5.178% | n/a | no |
| F2r | 263.2, 130.4 | 11.45% (-1.12) | **12.38% (+0.11)** | 11.89% (-0.34) | 12.01% (-1.01) | 5.186% | 41 | no |
| F4r | 393.9 | 15.19% (-3.46) | **15.45% (-3.11)** | 15.36% (-2.76) | 15.45% (-3.42) | 5.345% | 0 | no |
| STEPr | 259.4, 324.5 | 8.26% (-0.20) | **9.05% (-0.21)** | 9.19% (-0.16) | 8.62% (-0.19) | 5.051% | 100 | no |
| AF1 | 224.7, 676.0 | 5.54% (+0.54) | **6.78% (+0.41)** | 6.50% (+2.08) | 5.96% (+0.44) | 4.982% | 100 | kept |
| AF2 | 221.0, 600.4 | 4.23% (+0.59) | **5.58% (+0.23)** | 5.40% (+2.18) | 4.77% (+0.49) | 4.953% | 100 | kept |
| AF3 | 245.9, 661.2 | 5.16% (+0.20) | **5.65% (+0.25)** | 6.21% (+1.82) | 5.48% (+0.18) | 4.955% | 100 | kept |
| **AF4** | **236.3, 597.3** | **3.23% (+0.37)** | **3.88% (+0.14)** | **4.65% (+2.03)** | **3.71% (+0.33)** | **4.921%** | **100** | **KEPT, chosen** |

MM1-v3.2 as landed (F3 at 247.7, 448.6 pJ): pooled 5.048% (n 1,851: its own record 4.976%, n 1,829, plus the 22 E216 and E218 gemmLnc
points at its frozen forecasts). AF4's placebo: real LOEO 3.88% against a placebo median 12.30% (best of 100: 10.97%).

### Table 3. Held out by fold (rms, bias; W over idle given the measured op time, at each fold's gemmLnc points)

| fold | n | MM1-v3.2 as landed | F3r | AF1 | AF2 | AF3 | **AF4** |
|---|---|---|---|---|---|---|---|
| LOEO E211 | 2 | 10.15 (-1.44) | 10.44 (-2.75) | 11.06 (-3.35) | 9.19 (+8.93) | 13.80 (-8.54) | **8.45 (+6.96)** |
| LOEO E213 | 7 | 8.68 (-4.90) | 8.92 (-5.55) | 11.43 (-8.48) | 8.99 (-5.76) | 8.62 (-5.31) | **5.79 (-3.37)** |
| LOEO E215 | 5 | 7.23 (+4.62) | 5.58 (+0.90) | 2.13 (-0.05) | 3.23 (-1.81) | 2.47 (+0.95) | **2.96 (-0.97)** |
| LOEO E216 (the lead's fold) | 10 | 5.52 (+4.47) | 5.08 (+3.85) | 3.71 (+3.22) | 3.10 (+2.31) | 2.30 (+2.25) | **1.54 (+1.37)** |
| LOEO E217 | 0 | no gemmLnc point: the term is 0 at every point of the fold, which equals MM1-v3.2 there | | | | | |
| LOEO E218 (the lead's fold) | 12 | 11.48 (+0.54) | 11.29 (-0.56) | 5.28 (+4.08) | 4.46 (+1.40) | 3.70 (+2.99) | **2.84 (+0.50)** |
| LOEO E219 | 0 | no gemmLnc point (as E217; E212 and E214 likewise) | | | | | |
| **LOEO, all 36** | 36 | 8.95 (+1.03) | 8.69 (-0.22) | 6.78 (+0.41) | 5.58 (+0.23) | 5.65 (+0.25) | **3.88 (+0.14)** |
| LOCO aifoundry3 card 0 (the lead's 1.4-1.55x card) | 23 | 9.67 (+1.13) | 9.75 (+2.07) | 6.07 (+3.46) | 5.18 (+3.69) | 6.36 (+3.26) | **4.74 (+3.70)** |
| LOCO aifoundry1 card 1 | 3 | 11.91 (-11.22) | 13.02 (-12.88) | 13.37 (-12.24) | 10.58 (-9.82) | 11.67 (-10.62) | **8.93 (-8.53)** |
| LOCO aifoundry2 card 0 | 10 | 5.52 (+4.47) | 5.08 (+3.85) | 3.71 (+3.22) | 3.10 (+2.31) | 2.30 (+2.25) | **1.54 (+1.37)** |

"MM1-v3.2 as landed" is its own LOEO fold forecast at the 14 points in its fit and its frozen forecast at the measured op time at E216's and
E218's 22 points (outside its fit), in every row (it is not refitted per card in the LOCO rows).

### Table 4. Every gemmLnc point (forecast / measured - 1, %)

| point | token | card | NB | R4 | first | measured W | MM1-v3.2 as landed | F3r LOEO | **AF4 LOEO** | AF4 LOCO | AF4 in sample |
|---|---|---|---|---|---|---|---|---|---|---|---|
| E211 c01c | gemmLnc2x3x2 | aifoundry3 card 0 | 3 | 25.0 | 8.34 | 36.09 | -11.5 | -12.8 | **+11.7** | +14.7 | +10.2 |
| E211 c02c | gemmLnc3x5x7 | aifoundry3 card 0 | 5 | 0.0 | 5.20 | 25.15 | +8.6 | +7.3 | **+2.2** | +3.9 | +2.2 |
| E213 a087 | gemmLnc1x1x1 int8 | aifoundry3 card 0 | 1 | 0.0 | 0.00 | 26.27 | -4.6 | -1.3 | **-3.7** | +5.1 | +0.6 |
| E213 a086 | gemmLnc1x1x44 | aifoundry3 card 0 | 1 | 21.7 | 26.00 | 21.72 | -3.9 | -7.3 | **-1.4** | +2.5 | -1.1 |
| E213 a079 | gemmLnc1x6x5 | aifoundry3 card 0 | 6 | 0.0 | 4.33 | 26.23 | +4.0 | +4.3 | **-0.4** | +2.8 | +1.2 |
| E213 a075 | gemmLnc3x1x3 | aifoundry3 card 0 | 1 | 26.0 | 26.00 | 39.18 | -7.2 | -9.8 | **+1.3** | +5.7 | +1.4 |
| E213 a082 | gemmLnc4x1x6 | aifoundry3 card 0 | 1 | 14.0 | 26.00 | 23.08 | +5.4 | +2.5 | **-0.0** | +3.8 | +0.7 |
| E213 k40 | gemmLnc1x1x1 int8 | aifoundry1 card 1 | 1 | 0.0 | 0.00 | 29.31 | -14.5 | -11.5 | **-13.6** | -12.3 | -9.8 |
| E213 k37 | gemmLnc3x1x3 | aifoundry1 card 1 | 1 | 26.0 | 26.00 | 41.96 | -13.6 | -15.8 | **-5.7** | -6.4 | -5.5 |
| E215 a026 | gemmLnc1x12x4 | aifoundry3 card 0 | 12 | 0.0 | 2.17 | 25.77 | +5.5 | +3.6 | **+1.2** | +2.8 | +1.2 |
| E215 a024 | gemmLnc1x15x3 | aifoundry3 card 0 | 15 | 0.0 | 1.73 | 26.30 | +4.1 | +2.4 | **+0.4** | +1.9 | +0.3 |
| E215 a032 | gemmLnc5x1x10 | aifoundry3 card 0 | 1 | 14.0 | 26.00 | 22.86 | +10.2 | +4.8 | **+0.5** | +4.0 | +0.8 |
| E215 a031 | gemmLnc8x1x5 | aifoundry3 card 0 | 1 | 14.0 | 26.00 | 23.23 | +8.9 | +3.7 | **-0.6** | +2.8 | -0.3 |
| E215 b013 | gemmLnc2x1x37 | aifoundry1 card 1 | 1 | 21.6 | 26.00 | 24.80 | -5.6 | -10.0 | **-6.4** | -6.9 | -6.0 |
| E216 g01 | gemmLnc1x2x12 | aifoundry2 card 0 | 2 | 0.0 | 13.00 | 36.24 | +12.4 | +11.5 | **+2.7** | +2.7 | +2.5 |
| E216 g02 | gemmLnc2x2x12 | aifoundry2 card 0 | 2 | 8.9 | 13.00 | 37.81 | +1.6 | +0.8 | **+0.5** | +0.5 | +0.4 |
| E216 g03 | gemmLnc4x2x12 | aifoundry2 card 0 | 2 | 8.9 | 13.00 | 37.41 | +2.4 | +1.6 | **+1.4** | +1.4 | +1.3 |
| E216 g04 | gemmLnc5x2x12 | aifoundry2 card 0 | 2 | 8.9 | 13.00 | 37.55 | +2.1 | +1.2 | **+1.0** | +1.0 | +0.9 |
| E216 g05 | gemmLnc6x2x12 | aifoundry2 card 0 | 2 | 8.9 | 13.00 | 37.91 | +1.5 | +0.7 | **+0.5** | +0.5 | +0.4 |
| E216 g06 | gemmLnc7x2x12 | aifoundry2 card 0 | 2 | 8.9 | 13.00 | 37.80 | +1.6 | +0.8 | **+0.6** | +0.6 | +0.5 |
| E216 g07 | gemmLnc3x5x10 | aifoundry2 card 0 | 5 | 0.0 | 5.20 | 37.77 | +5.1 | +4.8 | **+1.1** | +1.1 | +0.9 |
| E216 g08 | gemmLnc4x5x10 | aifoundry2 card 0 | 5 | 0.0 | 5.20 | 37.95 | +5.7 | +5.4 | **+1.7** | +1.7 | +1.5 |
| E216 g09 | gemmLnc5x5x10 | aifoundry2 card 0 | 5 | 0.0 | 5.20 | 38.05 | +5.9 | +5.6 | **+1.9** | +1.9 | +1.7 |
| E216 g10 | gemmLnc6x5x10 | aifoundry2 card 0 | 5 | 0.0 | 5.20 | 37.83 | +6.3 | +6.0 | **+2.2** | +2.2 | +2.0 |
| E218 g01 | gemmLnc2x6x8 | aifoundry3 card 0 | 6 | 0.0 | 4.33 | 25.12 | +5.9 | +4.8 | **+1.0** | +2.1 | +0.5 |
| E218 g02 | gemmLnc2x6x7 | aifoundry3 card 0 | 6 | 0.0 | 4.33 | 25.54 | +5.6 | +4.6 | **+0.8** | +1.9 | +0.3 |
| E218 g03 | gemmLnc2x5x8 | aifoundry3 card 0 | 5 | 0.0 | 5.20 | 24.02 | +11.2 | +10.1 | **+5.2** | +6.4 | +4.7 |
| E218 g04 | gemmLnc7x5x14 | aifoundry3 card 0 | 5 | 20.1 | 5.20 | 21.89 | -19.4 | -20.2 | **-4.0** | -0.2 | -3.6 |
| E218 g05 | gemmLnc8x6x3 | aifoundry3 card 0 | 6 | 0.0 | 4.33 | 26.81 | +7.9 | +6.8 | **+3.0** | +4.1 | +2.5 |
| E218 g06 | gemmLnc1x14x4 | aifoundry3 card 0 | 14 | 0.0 | 1.86 | 25.98 | +3.7 | +2.8 | **+1.6** | +2.7 | +1.0 |
| E218 g07 | gemmLnc1x13x4 | aifoundry3 card 0 | 13 | 0.0 | 2.00 | 26.11 | +3.6 | +2.6 | **+1.3** | +2.4 | +0.7 |
| E218 g08 | gemmLnc2x14x16 | aifoundry3 card 0 | 14 | 20.5 | 1.86 | 22.57 | -23.7 | -24.4 | **-5.8** | -2.0 | -5.3 |
| E218 g09 | gemmLnc5x1x3 | aifoundry3 card 0 | 1 | 14.0 | 26.00 | 22.78 | +9.1 | +7.6 | **+1.7** | +5.1 | +2.0 |
| E218 g10 | gemmLnc2x1x12 | aifoundry3 card 0 | 1 | 14.0 | 26.00 | 22.79 | +8.2 | +6.7 | **+0.9** | +4.3 | +1.1 |
| E218 g11 | gemmLnc6x2x48 | aifoundry3 card 0 | 2 | 24.1 | 13.00 | 19.64 | -12.7 | -13.6 | **+0.5** | +4.9 | +1.1 |
| E218 g12 | gemmLnc5x1x8 | aifoundry3 card 0 | 1 | 14.0 | 26.00 | 23.04 | +7.1 | +5.6 | **-0.2** | +3.2 | +0.1 |

What is left (held out): E211's c01c +11.7% (the L3-resident clause prices every duplicate at NB 3, where about two thirds were re-fetched);
**card 1 low by 6-14%** (k40, k37, b013: card 1's excess is 1.2-1.3x aifoundry3's at the same shape, and two constants carry no card factor);
E218 g03 +5.2%.

## 4. The frozen forecasts: E220, both arms

E220's points FINAL at 05:24:17 PST (reg-e220, Q233: POINTS.txt sha256 `058984a0...`, points-e220.csv `64a7c99a...`, points-e220.json
`2451ca9d...`; tokens, cards and clocks only). `scripts/s03_freeze.py` made the forecasts at E220's own call (card, token, format, kind
random, mask, f = 600.0 MHz on arm A, aifoundry1 card 1; 799.0 MHz with 700.0 and 600.0 MHz columns on arm B, aifoundry2 card 0; kernel
rgm136; V, G, t0_c, minions, ops not given), re-making E220's registered planning peaks PP32 at all 158 points exactly (largest difference
0.0 W), F3 removed and AF4 added at MM1-v3.2's own op time. **Quantities** (per row): wall cycles an op and the counter's mean (MM1-v3.2's,
unchanged), seconds a GEMM, W over idle at the forecast op time, **the affine form for W over idle given a measured op time t (us, the slowest
minion): W(t) = A_W + B_W_us / t** (J over idle given t = W(t) x the measured seconds a GEMM), J over idle a GEMM with t forecast, J at rest
a GEMM with t forecast (MM1-v3.2's rest law at its T0 forecast: arm A 31.76 W at 55 C, arm B 23.19 W at 51 C), the term's energy a
minion-op and watts, MM1-v3.2's W and its F3 beside, the planning peak with the term (plain: W + rest + 2 W; and in E220's drop-line form, W x
(1 + 2 x 0.0843) + rest + 2 W at a gemmLnc point). The json also carries every other declared form's W and J at the gemmLnc rows (REPORTED)
and every gemmLnc row's features.

| file | sha256 | final |
|---|---|---|
| `forecasts-e220-af4.csv` | `3005869e7c490061100b741da2b90f20731b89ea4c0838c09719ca264f538952` | 2026-11-20 05:35:36 PST |
| `forecasts-e220-af4.json` | `37ace71c028a707ef07e9658cfdb2a4b3743ec0498b20b3bae93f79ac6af93e4` | 2026-11-20 05:35:36 PST |
| `term-gemmlnc-af4.json` | `dfcd58a025b56d547d5b16a334f2a9db12d2d3ba008d18e3ddc423c60fc3900e` | 2026-11-20 05:35:36 PST |

Written 05:35:07 PST, mode 444 since, recorded in `FROZEN-e220.txt` (the lane's FROZEN.txt, written 05:35:36 PST) with the declaration's,
the data table's and the fit record's sha256. A check after the freeze (`s04_check.py`): the 46 frozen gemmLnc rows re-made from the term
file's words on MM1-v3.2's predictor output agree to 1.8e-10 relative (the CSV's printed digits).

### Table 6. E220's gemmLnc points (arm A at 600 MHz, arm B at 799 MHz); every cooperative point equals MM1-v3.2

| arm | id | token | regime, R4 | MM1-v3.2 W over idle | F3 in it | AF4 term | **MM1-v3.2 + AF4 W over idle** | J over idle a GEMM, t forecast | J at rest a GEMM | planning peak: plain / E220 form | stop |
|---|---|---|---|---|---|---|---|---|---|---|---|
| A | xg01 | gemmLnc2x6x8 | A re-used, 0 | 24.16 | 4.40 | 3.23 | **22.98** | 0.2754 | 0.6558 | 56.7 / 60.6 | 72 |
| A | xg02 | gemmLnc2x6x7 | A re-used, 0 | 24.45 | 4.46 | 3.27 | **23.26** | 0.2406 | 0.5691 | 57.0 / 60.9 | 72 |
| A | xg03 | gemmLnc2x5x8 | A re-used, 0 | 24.19 | 4.57 | 3.20 | **22.82** | 0.2298 | 0.5496 | 56.6 / 60.4 | 72 |
| A | xg04 | gemmLnc7x5x14 | near reuse misses, 20.1 | 20.38 | 3.66 | 7.57 | **24.29** | 1.871 | 4.318 | 58.1 / 62.1 | 72 |
| A | xg05 | gemmLnc8x6x3 | A re-used, 0 | 25.90 | 4.72 | 3.46 | **24.64** | 0.4131 | 0.9455 | 58.4 / 62.6 | 72 |
| A | xg06 | gemmLnc1x14x4 | A re-used, 0 | 25.15 | 4.09 | 3.46 | **24.51** | 0.1600 | 0.3672 | 58.3 / 62.4 | 72 |
| A | xg07 | gemmLnc1x13x4 | A re-used, 0 | 25.22 | 4.13 | 3.46 | **24.54** | 0.1485 | 0.3406 | 58.3 / 62.4 | 72 |
| A | xg08 | gemmLnc2x14x16 | near reuse misses, 20.5 | 19.71 | 3.02 | 7.64 | **24.33** | 1.722 | 3.970 | 58.1 / 62.2 | 72 |
| A | xg09 | gemmLnc5x1x3 | NB 1, 14.0 | 25.97 | 8.27 | 6.63 | **24.32** | 0.05233 | 0.1207 | 58.1 / 62.2 | 72 |
| A | xg10 | gemmLnc2x1x12 | NB 1, 14.0 | 24.78 | 7.95 | 6.38 | **23.21** | 0.08314 | 0.1969 | 57.0 / 60.9 | 72 |
| A | xg11 | gemmLnc6x2x48 | near reuse misses, 24.1 | 21.53 | 4.94 | 8.27 | **24.86** | 2.333 | 5.313 | 58.6 / 62.8 | 72 |
| A | xg12 | gemmLnc5x1x8 | NB 1, 14.0 | 24.84 | 7.95 | 6.37 | **23.26** | 0.1388 | 0.3283 | 57.0 / 60.9 | 72 |
| A | n01 | gemmLnc1x6x48 | near reuse misses, 24.1 | 19.96 | 3.37 | 8.27 | **24.86** | 1.166 | 2.656 | 58.6 / 62.8 | 72 |
| A | n02 | gemmLnc2x6x24 | near reuse misses, 23.8 | 20.00 | 3.38 | 8.21 | **24.83** | 1.162 | 2.647 | 58.6 / 62.8 | 72 |
| A | n03 | gemmLnc2x6x28 | near reuse misses, 23.8 | 19.99 | 3.38 | 8.22 | **24.83** | 1.355 | 3.089 | 58.6 / 62.8 | 72 |
| A | n04 | gemmLnc2x6x32 | near reuse misses, 23.8 | 19.99 | 3.38 | 8.22 | **24.82** | 1.549 | 3.530 | 58.6 / 62.8 | 72 |
| A | n05 | gemmLnc1x6x40 | near reuse misses, 23.8 | 19.98 | 3.38 | 8.22 | **24.82** | 0.9677 | 2.206 | 58.6 / 62.8 | 72 |
| A | n06 | gemmLnc2x6x20 | near reuse misses, 23.1 | 20.04 | 3.40 | 8.10 | **24.74** | 0.9592 | 2.191 | 58.5 / 62.7 | 72 |
| A | n07 | gemmLnc4x6x16 | near reuse misses, 20.5 | 20.17 | 3.48 | 7.64 | **24.33** | 1.476 | 3.403 | 58.1 / 62.2 | 72 |
| B | xg04 | gemmLnc7x5x14 | near reuse misses, 20.1 | 34.83 | 4.39 | 9.08 | **39.52** | 2.857 | 4.534 | 64.7 / 71.4 | 70 |
| B | xg08 | gemmLnc2x14x16 | near reuse misses, 20.5 | 33.99 | 3.62 | 9.17 | **39.54** | 2.627 | 4.168 | 64.7 / 71.4 | 70 |
| B | n01 | gemmLnc1x6x48 | near reuse misses, 24.1 | 34.15 | 4.05 | 9.93 | **40.03** | 1.763 | 2.785 | 65.2 / 72.0 | 70 |
| B | n02 | gemmLnc2x6x24 | near reuse misses, 23.8 | 34.21 | 4.06 | 9.86 | **40.01** | 1.757 | 2.776 | 65.2 / 71.9 | 70 |
| B | n03 | gemmLnc2x6x28 | near reuse misses, 23.8 | 34.20 | 4.06 | 9.86 | **40.00** | 2.050 | 3.239 | 65.2 / 71.9 | 70 |
| B | n04 | gemmLnc2x6x32 | near reuse misses, 23.8 | 34.19 | 4.06 | 9.86 | **40.00** | 2.343 | 3.701 | 65.2 / 71.9 | 70 |
| B | n05 | gemmLnc1x6x40 | near reuse misses, 23.8 | 34.18 | 4.06 | 9.86 | **39.99** | 1.464 | 2.313 | 65.2 / 71.9 | 70 |
| B | n06 | gemmLnc2x6x20 | near reuse misses, 23.1 | 34.28 | 4.08 | 9.72 | **39.92** | 1.453 | 2.297 | 65.1 / 71.8 | 70 |
| B | n07 | gemmLnc4x6x16 | near reuse misses, 20.5 | 34.54 | 4.17 | 9.17 | **39.54** | 2.252 | 3.573 | 64.7 / 71.4 | 70 |

**What E220 tests (stated before its data):** its G2 block (n01-n07: NB 6 with KB 16-48, never run) sits where F3's 1 / NB says "small
excess" and AF4's L3-edge clause says "large": AF4 puts them 4.2-4.9 W (arm A) and 5.0-5.9 W (arm B at 799 MHz) above MM1-v3.2. XG's
re-used-A points (xg01-xg03, xg05-xg07) sit 0.6-1.4 W and its NB-1 points (xg09, xg10, xg12) 1.6-1.7 W below MM1-v3.2 on card 1. AF4's
held-out forecasts at card 1's three committed points were 6-14% low (section 3), so arm A's gemmLnc rows may read high by about that much.
**Blindness, by family:** the G2 block's shapes never ran on any card, so G2 is a shape-blind test of AF4; E220's XG gemmLnc points (arm A's twelve, arm B's xg04
and xg08) are E218's configurations, which are **in AF4's fit** (measured on aifoundry3), so on cards 1 and aifoundry2 they are a card-transfer test of
the term (configuration twins), not a shape-blind one: score them apart.

**Safety, for the orchestrator (information only; a trip is the registered stop, and nothing is changed by this lane).** Arm B (aifoundry2
card 0 at 799 MHz): with the term, xg04, xg08 and n01-n07 forecast 39.5-40.0 W over idle (MM1-v3.2: 34.0-34.5 W); on the rest law (23.19 W)
that is a board mean of about 62.7-63.2 W, a planning peak of 64.7-65.2 W plain against the 70 W stop, and 71.4-72.0 W in E220's own
drop-line form (over its 67.0 W drop line). E216's G block on this card peaked at 62.25 W (g05), about 2.4 W over that point's W over idle
plus rest, and the card's governor holds a 65 W TDP, so those runs may step down to 700 MHz (route m). Arm A (card 1): highest gemmLnc planning peak with the term 58.6 W plain, 62.8 W in E220's form,
against 72 W.

## 5. Gaps and NOT RUN

- **Post hoc in design.** The four new forms were written after the per-point excess was looked at (DECLARED section 0). The LOEO folds test
  the constants, not the design: E216's NB-2 half clause and the MB = 1 reading were designed seeing E216, and the L3-edge clause seeing E218's
  g04, g08 and g11. E220's G2 block is the first test of the L3-edge clause on shapes it was not designed from.
- **The card.** Two constants, no card factor: card 1's three points read 6-14% above AF4. aifoundry2's ten (all at 799 MHz, in two regimes
  only) read +0.5 to +2.7%.
- **The edges.** m and Lres are steps at MM1-v3.2's x1 (37.33 MB), with no width: E216's g01-g06 sit 1.3 MB under it (3 KB = 36 MB at KB 12).
  NB 3-4 has one point (c01c, L3-resident) and the NB-2 half one shape family (E216).
- **The format and the data kind.** Every point is random data; the only int8 points are the L2-resident 1x1x1, so the term's format and
  data dependence is not identified. E220's gemmLnc points are all fp32 random.
- **Time.** The term is energy only. In the near-reuse-miss regime E218's gemmLnc points ran 12-24% slower than MM1-v3.2's op time (the
  re-fetches cost time too) and in the re-used-A regime 9-13% faster; MM1-v3.2 prices gemmLnc's cycles within about 2% of its twin's. So
  E220's 'with t forecast' joules at gemmLnc points carry that time error; no time term was declared.
- **The mechanism** (lockstep while A streams fresh, re-fetches over the NoC and from DRAM) is a reading of the rails and the op-time ratios,
  not derived: no simulator here has caches with time.
- **NOT RUN:** a refit of MM1-v3.2's own constants with AF4 in place of F3 (by the brief: other constants unchanged; the in-fit gemmLnc
  points enter the pooled guard at MM1-v3.2's own LOEO fold base); MM1-v3.2's W given t at E217's and E219's points (equal for every form by
  construction: no gemmLnc point); the E213, E215 and E218 gemmLnc smokes (their rest is not the reducer's); an independent verifier of this
  lane; any card or simulator run; any commit.

## 6. Files

| file | what |
|---|---|
| `README.md` | this file |
| `term-gemmlnc-af4.json` | **the frozen term**: form, features, constants, fit, held-out record, keep rule, placebo, pooled guard, base |
| `forecasts-e220-af4.csv`, `forecasts-e220-af4.json` | **the frozen E220 forecasts** (306 rows; the json with every form's W and J at the gemmLnc rows, REPORTED) |
| `FROZEN-e220.txt` | the lane's FROZEN record: the three files' sha256 and the time they were final, the declaration's and records' sha256, the safety note |
| `DECLARED-lnc-form.md`, `DECLARED-<form>.md` (9), `DECLARED.sha256` | the declaration, byte for byte, hashed 05:30:58 PST before any fit |
| `data/s01_points.json` | the 36 points and twins with MM1-v3.2's base, F3, map and features (step 1) |
| `data/fit-record.json` | every form's fit, folds, per-point errors, the pooled guard, the placebo, the keep rule and the choice (step 2) |
| `data/s05_rails_e216.json`, `data/s06_rails_e218_points.json`, `data/s06_rails_e218_runs.json` | the rail splits (REPORTED) |
| `data/s07_tables.md` | the tables above as `s07_tables.py` printed them |
| `scripts/` | every script of the lane (path lines as environment variables: LNC_FORM_DIR, LAB_DIR, E220_REG_DIR, ROUND_DIR); `RUN-SHA256.txt` their sha256 as run |
| `logs/` | the steps' outputs and the lane's progress log |
| `SHA256SUMS` | every file here but itself |

To re-run (a clone of the lab repo at main 0f046200 or later): `git archive` its `tools/` into `$LNC_FORM_DIR/work/repo`, then
`/usr/bin/python3 -I -B scripts/s01_data.py`, `s02_fit.py`, `s03_freeze.py`, `s04_check.py` with the four thread variables at 1 and the
environment variables set.
