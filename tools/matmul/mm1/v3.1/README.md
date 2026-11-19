# MM1-v3.1: the lab's matmul model fitted exactly by its declaration on every committed matmul point through E213, frozen for its blind day E215

MM1-v3.1 predicts a matmul's clock cycles, seconds, joules (over idle and with the card at rest) and transistor switches on the ET-SoC-1 cards from the matrix size, the format, the data kind, the shire mask, the card, the clock and the operations the kernel contains. It is MM1-v3 (`../v3/`, landed b1493082) with the changes its declaration (`DECLARED-v31.md`, `declared-v31.json`, `t7_v31.py`, `comparator_4a_v31.py`; landed 7375bc9c, frozen by their sha256 before any E213 datum) declares, each decided by the declaration's own rule in its declared order. It was fitted at the lab box aifoundry2's desk (round Q222, lane fit-v31) on everything committed at GitHub main **f0d58c84** when the fit started (2026-11-18 17:03:47 PST): 1906 time points and 1832 energy points, E213's arms A, B. Desk only: this commit measured nothing.

**The data's gate (the declaration's section 9).** E213 arm A entered after its scores' commit (01283623) was on GitHub main; arm B entered after Q219's scores-e213b commit was on GitHub main (its data commit b0c727c5, RAN SHORT: 79 of 85 runs). E212 a2c0-S3, re-run by the model session and committed at 16:31:02 PST (321f992c) before the fit started, entered as section 9 says. E214 (the model session's third sweep) is a new matmul experiment and enters only by a dated amendment (none was made).

**Every choice below was made by a declared rule, in the declared order, on this data; the lane's rehearsal on E213 arm A alone (Wed 18 Nov 12:20-15:37 PST, the same code) checked the code and the timings and is not reported here: nothing was chosen from it.**

**What the rules chose, in one line:** every time item kept MM1-v3's form (item 8 not decided by the sign test, then T5r by its step 3; item 3 G0; item 4 n/32, T7 losing on its LOEO condition), so **v3.1's time model is MM1-v3's form refitted on v3.1's data**; the energy split chose E1t (b2 = d2 = 0, E1b's all-data fit at that bound), with item 6's census and item 7's counts and phi as inputs.

**Acceptance:** rule 1 FAILS on its time half (v3.1's LOEO wall equals MM1-v3 refitted's, 4.723% against 4.723%: equal, not lower; the energy half passes, 5.476% against 5.517%); rule 2 FAILS on its energy half (LOCO W given t by the anchor route 10.92% against 8.85%, bar +0.30; the fallback route beside: 9.64% against 9.11%); rules 3, 4(a) and 4(b) PASS. By the declaration v3.1 is frozen as built, the failing rules named.

**A finding (post hoc) about the LOLO compact fold:** every subset point that carries the row-imbalance term (all column groups, not all row groups) is compact under item 4's classes ({'compact': 122, 'other': 0, 'spread': 0}), so with compact held out no training point carries it, eta is not identified, and the declared pin rule (MM1-v3's: eta never pinned) leaves it where the optimizer stops: at its bound 2.0 under n/32 and T7L, which reads the compact class 118.2% and 121.8%; re-read with that fold's constants and eta at its neutral 0 (REPORTED, post hoc) it reads 6.17% and 7.03%. Item 4's decision does not rest on it: T7 had the lowest LOLO but failed its LOEO condition.

**Answered before the land** (lane fix-fit-v31, round Q222): verify-fit-v31 re-derived, with independent code, every decision and every number that fixes v3.1 (HOLDS WITH FIXES) and found four things, none of which changes a decision, a frozen constant or a forecast. (1) Item 3's scores of Gplace, Goperand and Gcoop are unidentified: `Tcoop_2` moves no training prediction in the E213 fold, so those scores read where the optimizer stopped; they are labelled with their ranges (section 3, `out/decisions_v31.json`, `out/item3_flat_v31.json`) and G0 holds at every value. (2, 3) E215's family C top half rests on a 1-ulp score difference, and family P's random half on two readings the declaration leaves open: both are named in section 7 for E215's registration to state; the point lists and forecasts are unchanged. (4) `out/points_time_v31.csv`'s cycles column holds T x f and is relabelled `meas_T_x_f` (section 4).

The owner's words that started the matmul model (Mon 16 Nov 2026, at or before 09:48:24 PST; a voice transcription in which "matte mold" is the matmul): "I want you to focus on the matte mold most of all, so I want to have a model which predicts matte mold energy and number of transistor switches and clock cycles. From based on what I know about the size of a matrix and which operations are contained. See check how well the timing simulation for the matte mold matches reality and the energy."

**Labels.** *Registered*: declared before any E213 datum (`DECLARED-v31.md`). *Desk*: computed at a desk from committed files. *Post hoc*: fitted or read after its data existed (every constant of v3.1 is). *Held out*: left out of the fit that scores it (not blind). *Blind*: scored on data that did not exist when the forecast was frozen. *REPORTED*: printed beside a rule, never deciding it. *NOT RUN*: a check that did not run. *Unidentified*: read from a fold in which a fitted constant moves no training prediction at all (the fold's training cost is flat along it), so the figure is where the optimizer stopped; printed with its range over the constant's declared bounds (section 3). Error = forecast / measured - 1; rms and bias in %. **Headline held-out figures exclude configuration twins** (a scored point whose card, kernel, arm, format, mask and clock to 25 MHz, and for energy the kind, are in the training set that priced it); the figures with them are beside. Interpreter: `/usr/bin/python3` 3.12.3, numpy 1.26.4, scipy 1.11.4, `-I -B`, single-threaded, in the round's CPU slots.

## 0. On one screen

| declared step | the rule's inputs | outcome |
|---|---|---|
| 1. item 8, T5r or tC (no fit) | E213's measured wall cycles at family C (arm A) and BK (arm B): 20 untied of 20 cases, tC closer 10, T5r closer 10, exact sign test p 1.0000 | **NOT DECIDED** |
| 2. item 4, the trace check | the committed verdict (walk/T7-TRACE-CHECK.json) and T7's desk precondition re-run with every subset shape of the data | **PASS** |
| 3. item 3, G0 / Gplace / Goperand / Gcoop | LOEO wall rms over the touched points (rgm211's two loops and gemmLnc), no twins: G0 6.58%, Gplace 24.40% (unidentified: 9.16-24.40%), Goperand 13.23% (unidentified: 9.09-24.37%), Gcoop 9.19% (unidentified: 9.13-24.39%); guard (pooled LOEO within 0.05 of G0's) True; the unidentified scores read `Tcoop_2` in the LOEO E213 fold, where the training cost is flat (post hoc, section 3) | **G0** (at every value of the flat constant) |
| 4. item 4, T7 / T7L / n/32 | LOLO wall rms over subset points / pooled LOEO wall rms: T7 14.40% / 6.20%, demand 92.50% / 4.39%, n32 89.78% / 4.29% | **n32** (T7 stays out; T7L against n/32 by v3's declared time rule) |
| 4b. item 8's step 3 | pooled LOEO wall rms: T5r 4.29%, tC 4.44% | **T5r** |
| 5. the final time form | every fold, MM1-v3 refitted beside | **T5r+G0+n32** |
| 6. item 1, the energy split | LOEO W over idle given t, no twins, >= 3 W: E1u 5.52%, E1b 5.48%, E1t 5.48%, E1m 5.73% | **E1t** |
| 7. item 2, a card left out | pooled LOCO W given t (held-out cards' anchor points out): anchor route 10.92% (+1.77), n 1748, fallback 9.64% (-2.69), n 1748 | the anchor route (declared) |

Form names: `T5r+G0+n32` = item 8's T5r, item 3's G0, item 4's n/32 (MM1-v3's own form); T7L appears as `demand` (engine_v3's name for it). The LOLO figures of n/32 and T7L read the compact class with an unidentified eta (the finding above).

**Held out, the same points and folds for MM1-v3.1 and MM1-v3 refitted on exactly v3.1's inputs** (wall cycles; energy W over idle given the measured seconds at 3 W and above):

| set | MM1-v3.1 | MM1-v3 refitted | with twins (v3.1 / v3 refitted) |
|---|---|---|---|
| LOEO, all points | 4.72% (-0.17), n 1299 | 4.72% (-0.17), n 1299 | 4.29% (-0.25), n 1906 / 4.29% (-0.25), n 1906 |
| LOCO | 4.15% (-0.16), n 1906 | 4.15% (-0.16), n 1906 | 4.15% (-0.16), n 1906 / 4.15% (-0.16), n 1906 |
| leave rgm211 out | 6.25% (-1.39), n 20 | 6.25% (-1.39), n 20 | 6.25% (-1.39), n 20 / 6.25% (-1.39), n 20 |
| the E212 fold | 5.43% (-0.81), n 346 | 5.43% (-0.81), n 346 | 4.78% (-0.73), n 478 / 4.78% (-0.73), n 478 |
| the E213 fold | 4.10% (-1.04), n 116 | 4.10% (-1.04), n 116 | 4.07% (-1.02), n 118 / 4.07% (-1.02), n 118 |
| subsets (LOEO) | 6.47% (-0.46), n 193 | 6.47% (-0.46), n 193 | 6.17% (-0.43), n 212 / 6.17% (-0.43), n 212 |
| energy LOEO | 5.48% (+0.63), n 1344 | 5.52% (+0.65), n 1344 | 5.29% (+0.28), n 1756 / 5.31% (+0.29), n 1756 |
| energy LOCO (anchor route) | 10.92% (+1.77), n 1748 | 8.85% (-5.24), n 1748 | 10.92% (+1.77), n 1748 / 8.85% (-5.24), n 1748 |
| energy LOCO (fallback) | 9.64% (-2.69), n 1748 | 9.11% (-2.42), n 1748 | 9.64% (-2.69), n 1748 / 9.11% (-2.42), n 1748 |
| energy, the newly counted kinds (LOEO) | 7.69% (+4.06), n 46 | 7.87% (+3.81), n 46 | 7.69% (+4.06), n 46 / 7.87% (+3.81), n 46 |

**Acceptance** (MM1-v3's four rules restated in the declaration's section 9, against MM1-v3 refitted on the same points and folds): rule 1 FAIL; rule 2 FAIL; rule 3 PASS; rule 4a PASS; rule 4b PASS; **accepted: False**.

**E215, v3.1's blind day (arm A, aifoundry3 card 0 at 600 MHz)**: by item 10's point rule on both frozen models and a never-run scan in E213's form: C 10 of 10; L 0 of 20 (post hoc reading: 20); P 12 of 12; R 10 of 10; S 0 of 8 (post hoc reading: 8). Forecasts in `out/e215/mm1_v31_e215.csv` and `.json` (section 7).

## 1. The data and the inputs

Time points by experiment: {'E105': 73, 'E107': 224, 'E119': 63, 'E126': 46, 'E136': 36, 'E146': 108, 'E158': 102, 'E159': 13, 'E168': 14, 'E169': 54, 'E190': 36, 'E206': 232, 'E207': 53, 'E208': 184, 'E209': 46, 'E211': 26, 'E212': 478, 'E213': 118}. Energy points: {'E105': 45, 'E107': 179, 'E119': 63, 'E126': 46, 'E136': 24, 'E146': 108, 'E158': 102, 'E159': 13, 'E168': 12, 'E169': 54, 'E190': 36, 'E206': 232, 'E207': 53, 'E208': 173, 'E209': 43, 'E210': 22, 'E211': 26, 'E212': 473, 'E213': 128} (1832 priced by v3.1's counts and phi). E146's 87 store-cadence rungs are in no training set and are scored apart (as MM1-v3). E212's cases are re-made over every committed session (ten: MM1-v3's eight, a2c0-S4 and the re-run a2c0-S3; a case run in two sessions is one record, as `comparator_4a_v31.py` makes them for its nine; the records the re-run S3 changes leave rule 4(a)'s comparison and are listed); E213's time points are one a (card, case), the mean of its runs, and its energy points one a (card, configuration, kind).

| input | sha256 |
|---|---|
| `DECLARED-v31.md` (frozen, posted before any E213 datum) | `d58601fa0696cdf42611a3e7a179179eedb3fc4f7015e8638e608fa99e3d0860` |
| `comparator_4a_v31.py` (frozen, posted before any E213 datum) | `17b336e10b9f4b0a521c0cb83630575f9f54b5d1d993436677aedefdcf38f960` |
| `declared-v31.json` (frozen, posted before any E213 datum) | `26c3fedb2c0a2623d2a02fd0acb2add306259ca4042433fed92d8c9c56d3365c` |
| `t7_v31.py` (frozen, posted before any E213 datum) | `893ae962174678fcd1560dfc423722361e706319a188687f8f572a4e3ca89242` |
| `counts/SHA256SUMS` (v31-counts, landed 3e8991d0; posted #2.7.2.1.1) | `c74c2d49c336159f6ca63aad2652601a10e22d6a8b5db00d46c66bfb1cf8aa7f` (sha256sum -c rc 0) |
| `inputs/census/census-v3.1.json` (item 6) | `3e5a088eb260d3f06eb8248a52e1267dc333e06c77a6206a2edd117b022058c1` |
| `inputs/SOURCES.tsv` | `76f5e7af41021f518cfcec6bc9431e50fcdd3be35bf1dad50682f8dc52c4570f` |
| `inputs/census/census-v3.1.json` | `3e5a088eb260d3f06eb8248a52e1267dc333e06c77a6206a2edd117b022058c1` |
| `inputs/e212/a2c0-S3__data-e212-a2c0-S3.json` | `9bc0c2f8cb779846f894578c7f64713250f88a20305ec8b62c7a81ba0ec2678e` |
| `inputs/e213/data-e213-A.json` | `d53caacb98e8bcf251073714926742886f6629725779dd0b9a6828ecb164c05f` |
| `inputs/e213/data-e213-B.json` | `93fe3e7ec189faecde16cb89aea751b5a150a64286bbd4c3e3854ddacaafc3f1` |
| `inputs/e213/points-e213.csv` | `8bab916516e74e3d23f9aff29bf105d1bd9e7ece73ee5aa765de2c007633ad82` |

**The census paths' check** (the declaration's deferred item, made first): only census-v3.json's own rgm136 gemmL check holds such a record; E211's dated correction 1 (tools/claims-v3/e211-notes/E211.md.A1-correction-1.md, its item 6) lists a counted run of any rgm211 loop or of gemmLnc's as NOT RUN: no committed counted run of those loops, so their census entries stand (v3.1 README).

**T7's desk precondition**, re-run at the fit's start with every subset shape of the data (25 shapes): 1 precondition PASS (72 shape-walks); 2 distances PASS (10); 3 WalkShape PASS (worst 0); 4 op_time PASS {'v3+T5r': {'points': 131, 'max_rel_diff': 0.0}, 'v3': {'points': 131, 'max_rel_diff': 0.0}}; 5 n_eff(full) = 1 PASS, 22 E213 subset points mapped CHECK PASS (record `out/t7_check.json`).

**The declared starts** (`check_starts_v31.py`): S0-S5 equal MM1-v3's `fit_v3.STARTS` and the declared new-name values; S6-S17 and the energy draws re-drawn from their seeds: PASS.

## 2. What MM1-v3.1 computes: the frozen constants

Time form **T5r+G0+n32** (`time_v31.py`; `mm1_v31_params.json` holds every constant), energy form **E1t** (`energy_v31.py`). Every constant's all-data value, its bound activity and its relative standard error from the Jacobian at the all-data fit (above 100%: not identified, the fit unchanged):

| constant | value | rse | bound | | constant | value | rse | bound |
|---|---|---|---|---|---|---|---|---|
| F2 | 379.721 | 5.4% |  | | Eub\|fp16 | 9.46998 | 1.6% |  |
| T2 | 0.0154861 | 202.7% (not identified) |  | | Eub\|fp32 | 9.4717 | 1.6% |  |
| c3 | 398.498 | 3.3% |  | | Eub\|int8 | 2.5824 | 4.3% |  |
| cF | 381.995 | 5.0% |  | | Pa\|aifoundry1 card 0 | 0.584305 | 31.3% |  |
| chi3 | 0.0742656 | 29.5% |  | | Pa\|aifoundry1 card 1 | 1.07755 | 10.0% |  |
| chiF | 0.0983047 | 8.6% |  | | Pa\|aifoundry2 card 0 | 1.22965 | 13.2% |  |
| d8 | 0.0485289 | 8.2% |  | | Pa\|aifoundry3 card 0 | 0.600172 | 16.3% |  |
| eta | 2.19583e-20 | - (at its lower bound, not identified) | lower | | Pm | 0.329121 | 7.0% |  |
| kA | 0.89286 | 0.6% |  | | a8 | 1.23209 | 6.9% |  |
| m3 | 0.834624 | 2.4% |  | | a_lane | 3.59081 | 11.7% |  |
| mF | 1.9797 | 1.5% |  | | a_op | 7.45266 | 1.6% |  |
| pB | 0.5248 | 6.9% |  | | b0 | 5.89695 | 1.1% |  |
| piF0 | 0.0463181 | 22.6% |  | | b3 | 425.569 | 5.0% |  |
| r2 | 0.638155 | 4.1% |  | | bF | 1071.34 | 4.1% |  |
| w1 | 1.82935 | 8.0% |  | | d3 | 830.022 | 3.1% |  |
| w2 | 11.4285 | 13.1% |  | | dF | 953.065 | 3.5% |  |
| x1 | 37.1837 | 0.5% |  | | eC | 2.9678 | 5.0% |  |
| x2 | 65.4171 | 3.7% |  | | g | 0.758174 | 1.0% |  |
| zeta | 0.726011 | 3.0% |  | | kc\|aifoundry1 card 0 | 1.12235 | 3.0% |  |
|  | | |  | | kc\|aifoundry1 card 1 | 1.02661 | 0.8% |  |
|  | | |  | | kc\|aifoundry2 card 0 | 1.08437 | 0.9% |  |
|  | | |  | | m\|fp16 | 1.07395 | 1.2% |  |
|  | | |  | | m\|int8 | 3.05773 | 2.8% |  |
|  | | |  | | xi | 0.247354 | 33.3% |  |

## 3. The decisions, in the declared order (`out/decisions_v31.json`)

**Step 1, item 8** (T5r against tC from their frozen forecasts, no fit): sources {'A': {'path': 'docs/reports/data/2026-11-18-e213-blind-matmul-aifoundry3/scores-e213-A.json', 'sha256': '6d894c0307e14bbf3c86fc355ea35855950d11a27c2ea67a2f66b56164bb39e7'}, 'B': {'path': 'docs/reports/data/2026-11-18-e213-blind-matmul-aifoundry1-c1/scores-e213-B.json', 'sha256': '692bfed37711d069c8fb185f2dae2c21490f5d957fac0cc365bdb3bfccdebb52'}}. Cases (measured wall cycles an op as E213's frozen scorer reports them; d = |ln(m / F_T5r)| - |ln(m / F_tC)|, a tie at |d| <= 0.005):

| case | arm | measured | T5r | tC | d |
|---|---|---|---|---|---|
| a037 | A | 908.6 | 888.5 | 856.8 | -0.0364 |
| a038 | A | 872.1 | 857.0 | 834.5 | -0.0266 |
| a039 | A | 912.9 | 972.4 | 926.0 | 0.0490 |
| a040 | A | 886.5 | 954.8 | 928.1 | 0.0284 |
| a041 | A | 1012.3 | 1045.6 | 1010.9 | 0.0309 |
| a042 | A | 984.7 | 1030.9 | 1012.8 | 0.0178 |
| a043 | A | 906.9 | 945.9 | 895.1 | 0.0291 |
| a044 | A | 880.2 | 927.4 | 897.8 | 0.0324 |
| a045 | A | 975.9 | 939.0 | 884.6 | -0.0597 |
| a046 | A | 950.5 | 920.5 | 888.7 | -0.0352 |
| a047 | A | 1126.7 | 1020.6 | 962.2 | -0.0589 |
| a048 | A | 1110.5 | 1007.8 | 973.6 | -0.0345 |
| k20 | B | 893.5 | 881.3 | 837.2 | -0.0514 |
| k21 | B | 861.8 | 853.0 | 823.3 | -0.0355 |
| k22 | B | 928.0 | 971.0 | 896.3 | 0.0105 |
| k23 | B | 900.5 | 951.5 | 892.5 | 0.0462 |
| k24 | B | 1010.3 | 1045.6 | 1010.9 | 0.0337 |
| k25 | B | 983.7 | 1030.9 | 1012.8 | 0.0178 |
| k26 | B | 1018.2 | 1077.1 | 1087.8 | -0.0099 |
| k27 | B | 983.2 | 1047.7 | 1053.6 | -0.0057 |

Verdict: **NOT DECIDED**.

**Step 2, item 4's trace check: PASS** (PASS = (a), (b) and (c) at both masks (t7-0xf's u2 at 0xf with verify-v31trace's u1 at 0x1111: the minimum log set met at both masks), verify-v31trace HOLDS WITH FIXES with its fix (the 0xf run) applied and the check re-run, verify-t7-0xf HOLDS WITH FIXES (wording), and the desk precondition re-run here (step 0)).

**Step 3, item 3**: rule winner G0, guard True, **G0**; not wanted (G0 wins, or every constant within 1% of 0): True. Each form's all-data constants: G0 {}; Gcoop {"Tcoop_2": 9.0223, "Tcoop_3": 27.1483, "Tcoop_F": 49.2851}; Goperand {"Tcoop_2": 9.0247, "Tcoop_3": 43.3456, "Tcoop_F": 52.2946, "gamma_A": 0.8447, "gamma_B": -0.7781}; Gplace {"Tcoop_2": 9.0234, "Tcoop_3": 42.1424, "Tcoop_F": 47.212, "gamma_3": -0.7325, "gamma_F": 0.1024}. Per fold: `out/decisions_v31.json`.

**Item 3's scores checked for identification** (post hoc, REPORTED; `item3_flat_v31.py`, `out/item3_flat_v31.json`; fix-fit-v31 (Q222), answering verify-fit-v31 finding 1 (medium)): with step 3's scores re-made first (equal to the stored ones), every free item 3 constant of Gplace, Goperand and Gcoop was moved alone to its two declared bounds in every LOEO fold, the fold's other constants held: 234 (form, fold, constant) checked, 3 flat (no training prediction moves at all): Gplace's `Tcoop_2` in the LOEO E213 fold (fitted -299.99); Goperand's `Tcoop_2` in the LOEO E213 fold (fitted -122.61); Gcoop's `Tcoop_2` in the LOEO E213 fold (fitted -8.2227). In that fold the constant's pin set holds E211|c01c alone, whose op time does not depend on it, so the declared pin rule (a constant is pinned only when its set is empty) leaves it where the optimizer stopped, and the fold's held-out predictions move with it. Over the bounds, every other fold as stored: Gplace touched (no twin) 9.16-24.40%, pooled LOEO 4.365-5.180% (training cost span 0); Goperand touched (no twin) 9.09-24.37%, pooled LOEO 4.363-5.178% (training cost span 0); Gcoop touched (no twin) 9.13-24.39%, pooled LOEO 4.362-5.178% (training cost span 0). So those forms' item 3 scores above, and their pooled LOEO, are **unidentified**: labelled so in `out/decisions_v31.json` (step3: `identification_post_hoc`, and each form's `scores_identified`). **The decision holds:** G0 (6.58%, no constant) is lower than every form at every value, so item 3's rule gives G0 at every value and every combination of values; a rule win would also fail the guard, the pooled LOEO being at least 4.362% at every value against G0's 4.294% + 0.05. A later declaration could pin any constant whose training Jacobian column is zero in a fold.

verify-fit-v31 (Q222) shows the same flat line from the optimizer's side with its own fitter: given fit-v31's data in fit-v31's order it lands on fit-v31's E213-fold values bit for bit (Gplace -300, Goperand -122.6); with one time point's mean 1 ulp apart (the order in which that point's runs are summed) it stops at +600 and +8.3 at equal cost and reads Gplace 10.37% and Goperand 9.07%. Gcoop's 9.19% is where both fitters happened to stop (about -8.2), on the same flat line. Item 3's decision rests on none of these values (REPORTED).

**Step 4, item 4**: T7 stays out; T7L against n/32 by v3's declared time rule: **n32**. LOLO by class (each form): T7 {"compact": 12.961, "other": 18.657, "spread": 14.315}; demand {"compact": 121.772, "other": 8.251, "spread": 6.536}; n32 {"compact": 118.215, "other": 6.471, "spread": 6.546}.

**Step 6, item 1**: candidates within 0.10 points of the lowest of E1b / E1t / E1m: ['E1b', 'E1t']; winner of the three E1t; E1u lower by more than 0.30 points: False: **E1t**; E1b's all-data b2, d2 at their bound 0: True.

## 4. Held out, beside MM1-v3 refitted (`out/holdout_v31.json`, `out/points_time_v31.csv`, `out/points_energy_v31.csv`)

| wall cycles, held out (no twin) | MM1-v3.1 | MM1-v3 refitted |
|---|---|---|
| LOEO E146 store rungs (never trained) | 5.89% (+1.76), n 57 | 5.89% (+1.76), n 57 |
| LOEO E212 a1c0 | 5.57% (-0.89), n 84 | 5.57% (-0.89), n 84 |
| LOEO E212 a1c1 | 5.26% (-1.45), n 136 | 5.26% (-1.45), n 136 |
| LOEO E212 a2c0 | 5.52% (-0.05), n 126 | 5.52% (-0.05), n 126 |
| LOEO E213 arm A | 4.37% (-1.57), n 85 | 4.37% (-1.57), n 85 |
| LOEO E213 arm B | 3.25% (+0.42), n 31 | 3.25% (+0.42), n 31 |
| LOEO E213 family A:C | 5.73% (+0.25), n 12 | 5.73% (+0.25), n 12 |
| LOEO E213 family A:E | 3.71% (-3.42), n 4 | 3.71% (-3.42), n 4 |
| LOEO E213 family A:I | 1.51% (-1.02), n 16 | 1.51% (-1.02), n 16 |
| LOEO E213 family A:M | 5.21% (-3.48), n 24 | 5.21% (-3.48), n 24 |
| LOEO E213 family A:P | 4.19% (-0.63), n 15 | 4.19% (-0.63), n 15 |
| LOEO E213 family A:R | 3.99% (-0.96), n 14 | 3.99% (-0.96), n 14 |
| LOEO E213 points (no reference) | 4.12% (-1.03), n 115 | 4.12% (-1.03), n 115 |
| LOEO aifoundry1 card 0 | 5.13% (-0.85), n 108 | 5.13% (-0.85), n 108 |
| LOEO aifoundry1 card 1 | 5.00% (-0.48), n 256 | 5.00% (-0.48), n 256 |
| LOEO aifoundry2 card 0 | 4.93% (+0.08), n 556 | 4.93% (+0.08), n 556 |
| LOEO aifoundry3 card 0 | 4.06% (-0.12), n 379 | 4.06% (-0.12), n 379 |
| LOEO all | 4.72% (-0.17), n 1299 | 4.72% (-0.17), n 1299 |
| LOEO exp E105 | 2.00% (-1.63), n 16 | 2.00% (-1.63), n 16 |
| LOEO exp E107 | 2.06% (-0.63), n 125 | 2.06% (-0.63), n 125 |
| LOEO exp E119 | 2.59% (-1.36), n 51 | 2.59% (-1.36), n 51 |
| LOEO exp E126 | 3.48% (+1.89), n 40 | 3.48% (+1.89), n 40 |
| LOEO exp E136 | 1.54% (-1.44), n 18 | 1.54% (-1.44), n 18 |
| LOEO exp E146 | 5.73% (+1.84), n 62 | 5.73% (+1.84), n 62 |
| LOEO exp E158 | 4.22% (-0.42), n 76 | 4.22% (-0.42), n 76 |
| LOEO exp E159 | 5.44% (-1.27), n 11 | 5.44% (-1.27), n 11 |
| LOEO exp E168 | 0.90% (-0.41), n 14 | 0.90% (-0.41), n 14 |
| LOEO exp E169 | 7.42% (-0.73), n 47 | 7.42% (-0.73), n 47 |
| LOEO exp E190 | 5.76% (+4.26), n 18 | 5.76% (+4.26), n 18 |
| LOEO exp E206 | 4.82% (+1.30), n 170 | 4.82% (+1.30), n 170 |
| LOEO exp E207 | 4.46% (+1.29), n 50 | 4.46% (+1.29), n 50 |
| LOEO exp E208 | 3.80% (-1.27), n 80 | 3.80% (-1.27), n 80 |
| LOEO exp E209 | 5.66% (+0.37), n 40 | 5.66% (+0.37), n 40 |
| LOEO exp E211 | 7.47% (+0.15), n 19 | 7.47% (+0.15), n 19 |
| LOEO exp E212 | 5.43% (-0.81), n 346 | 5.43% (-0.81), n 346 |
| LOEO exp E213 | 4.10% (-1.04), n 116 | 4.10% (-1.04), n 116 |
| LOEO fp16 | 3.56% (-0.17), n 230 | 3.56% (-0.17), n 230 |
| LOEO fp32 | 5.16% (-0.30), n 695 | 5.16% (-0.30), n 695 |
| LOEO int8 | 4.50% (+0.08), n 374 | 4.50% (+0.08), n 374 |
| LOEO layout compact | 6.47% (+0.65), n 106 | 6.47% (+0.65), n 106 |
| LOEO layout other | 6.11% (-4.03), n 32 | 6.11% (-4.03), n 32 |
| LOEO layout spread | 6.67% (-0.53), n 55 | 6.67% (-0.53), n 55 |
| LOEO loop rgm136 gemmL | 5.04% (-0.13), n 1029 | 5.04% (-0.13), n 1029 |
| LOEO loop rgm136 gemmLnc | 7.27% (+2.74), n 9 | 7.27% (+2.74), n 9 |
| LOEO loop rgm211 gemmL | 2.50% (-0.87), n 4 | 2.50% (-0.87), n 4 |
| LOEO loop rgm211 gemmLn | 6.86% (-1.45), n 16 | 6.86% (-1.45), n 16 |
| LOEO run_gemm | 2.57% (-0.33), n 241 | 2.57% (-0.33), n 241 |
| LOEO subsets | 6.47% (-0.46), n 193 | 6.47% (-0.46), n 193 |
| LOCO E212 a1c0 | 4.88% (-0.64), n 100 | 4.88% (-0.64), n 100 |
| LOCO E212 a1c1 | 4.24% (-0.87), n 203 | 4.24% (-0.87), n 203 |
| LOCO E212 a2c0 | 4.65% (+0.37), n 175 | 4.65% (+0.37), n 175 |
| LOCO E213 arm A | 4.20% (-1.33), n 86 | 4.20% (-1.33), n 86 |
| LOCO E213 arm B | 3.22% (+0.34), n 32 | 3.22% (+0.34), n 32 |
| LOCO aifoundry1 card 0 | 4.31% (-0.56), n 138 | 4.31% (-0.56), n 138 |
| LOCO aifoundry1 card 1 | 3.93% (-0.26), n 440 | 3.93% (-0.26), n 440 |
| LOCO aifoundry2 card 0 | 4.44% (-0.12), n 778 | 4.44% (-0.12), n 778 |
| LOCO aifoundry3 card 0 | 3.84% (-0.03), n 550 | 3.84% (-0.03), n 550 |
| LOCO all | 4.15% (-0.16), n 1906 | 4.15% (-0.16), n 1906 |
| LOCO layout compact | 5.82% (+0.86), n 122 | 5.82% (+0.86), n 122 |
| LOCO layout other | 5.01% (-3.23), n 35 | 5.01% (-3.23), n 35 |
| LOCO layout spread | 6.52% (+0.00), n 55 | 6.52% (+0.00), n 55 |
| LOCO loop rgm136 gemmL | 4.39% (-0.11), n 1451 | 4.39% (-0.11), n 1451 |
| LOCO loop rgm136 gemmLnc | 7.55% (+2.91), n 9 | 7.55% (+2.91), n 9 |
| LOCO loop rgm211 gemmL | 2.39% (-0.68), n 4 | 2.39% (-0.68), n 4 |
| LOCO loop rgm211 gemmLn | 6.74% (-1.23), n 16 | 6.74% (-1.23), n 16 |
| LOKO E213 arm A | 4.09% (-0.29), n 13 | 4.09% (-0.29), n 13 |
| LOKO E213 arm B | 1.77% (+1.31), n 2 | 1.77% (+1.31), n 2 |
| LOKO aifoundry1 card 1 | 3.19% (+1.75), n 11 | 3.19% (+1.75), n 11 |
| LOKO aifoundry2 card 0 | 2.82% (-0.65), n 140 | 2.82% (-0.65), n 140 |
| LOKO aifoundry3 card 0 | 3.48% (-0.48), n 304 | 3.48% (-0.48), n 304 |
| LOKO all | 3.28% (-0.48), n 455 | 3.28% (-0.48), n 455 |
| LOKO loop rgm136 gemmLnc | 7.08% (+2.77), n 9 | 7.08% (+2.77), n 9 |
| LOKO loop rgm211 gemmL | 2.20% (-0.78), n 4 | 2.20% (-0.78), n 4 |
| LOKO loop rgm211 gemmLn | 6.89% (-1.53), n 16 | 6.89% (-1.53), n 16 |
| LEAVE rgm211 E213 arm A | 2.72% (-1.21), n 8 | 2.72% (-1.21), n 8 |
| LEAVE rgm211 aifoundry3 card 0 | 6.25% (-1.39), n 20 | 6.25% (-1.39), n 20 |
| LEAVE rgm211 all | 6.25% (-1.39), n 20 | 6.25% (-1.39), n 20 |
| LEAVE rgm211 loop rgm211 gemmL | 2.27% (-0.81), n 4 | 2.27% (-0.81), n 4 |
| LEAVE rgm211 loop rgm211 gemmLn | 6.89% (-1.53), n 16 | 6.89% (-1.53), n 16 |
| LOLO E212 a1c0 | 87.75% (+42.54), n 24 | 87.75% (+42.54), n 24 |
| LOLO E212 a1c1 | 79.30% (+35.31), n 47 | 79.30% (+35.31), n 47 |
| LOLO E212 a2c0 | 86.04% (+41.25), n 51 | 86.04% (+41.25), n 51 |
| LOLO E213 arm A | 73.34% (+33.04), n 22 | 73.34% (+33.04), n 22 |
| LOLO aifoundry1 card 0 | 91.25% (+45.22), n 27 | 91.25% (+45.22), n 27 |
| LOLO aifoundry1 card 1 | 90.23% (+45.63), n 71 | 90.23% (+45.63), n 71 |
| LOLO aifoundry2 card 0 | 93.11% (+46.21), n 70 | 93.11% (+46.21), n 70 |
| LOLO aifoundry3 card 0 | 82.45% (+43.02), n 44 | 82.45% (+43.02), n 44 |
| LOLO all | 89.78% (+45.23), n 212 | 89.78% (+45.23), n 212 |
| LOLO layout compact | 118.21% (+79.94), n 122 | 118.21% (+79.94), n 122 |
| LOLO layout other | 6.47% (-4.70), n 35 | 6.47% (-4.70), n 35 |
| LOLO layout spread | 6.55% (+0.01), n 55 | 6.55% (+0.01), n 55 |
| LOLO loop rgm136 gemmL | 89.78% (+45.23), n 212 | 89.78% (+45.23), n 212 |
| LOEO sub E212 a1c0 | 5.29% (-0.66), n 84 | 5.29% (-0.66), n 84 |
| LOEO sub E212 a1c1 | 5.05% (-1.35), n 136 | 5.05% (-1.35), n 136 |
| LOEO sub E212 a2c0 | 5.38% (+0.32), n 126 | 5.38% (+0.32), n 126 |
| LOEO sub E213 arm A | 4.38% (-1.61), n 85 | 4.38% (-1.61), n 85 |
| LOEO sub E213 arm B | 3.27% (+0.51), n 31 | 3.27% (+0.51), n 31 |
| LOEO sub aifoundry1 card 0 | 5.29% (-0.66), n 84 | 5.29% (-0.66), n 84 |
| LOEO sub aifoundry1 card 1 | 4.77% (-1.01), n 167 | 4.77% (-1.01), n 167 |
| LOEO sub aifoundry2 card 0 | 5.38% (+0.32), n 126 | 5.38% (+0.32), n 126 |
| LOEO sub aifoundry3 card 0 | 4.38% (-1.61), n 85 | 4.38% (-1.61), n 85 |
| LOEO sub all | 4.97% (-0.69), n 462 | 4.97% (-0.69), n 462 |
| LOEO sub layout compact | 5.90% (-0.10), n 68 | 5.90% (-0.10), n 68 |
| LOEO sub layout other | 7.40% (-5.93), n 15 | 7.40% (-5.93), n 15 |
| LOEO sub layout spread | 6.69% (-0.20), n 49 | 6.69% (-0.20), n 49 |
| LOEO sub loop rgm136 gemmL | 5.00% (-0.71), n 447 | 5.00% (-0.71), n 447 |
| LOEO sub loop rgm136 gemmLnc | 5.00% (+1.08), n 7 | 5.00% (+1.08), n 7 |
| LOEO sub loop rgm211 gemmL | 2.50% (-0.85), n 4 | 2.50% (-0.85), n 4 |
| LOEO sub loop rgm211 gemmLn | 3.29% (-1.64), n 4 | 3.29% (-1.64), n 4 |
| LOEO counter mean (all / no twin) | 5.31% (-0.13), n 1870 / 6.05% (+0.20), n 1281 | 5.31% (-0.13), n 1870 / 6.05% (+0.20), n 1281 |

v3.1's time form is MM1-v3 refitted's (the decisions above), so the two time columns are the same fits. The LOLO rows carry the compact fold's unidentified eta (the finding above; `out/reported_v31.json`, item4_LOLO_compact_eta_not_identified_post_hoc).

| energy, held out (no twin) | quantity | MM1-v3.1 | MM1-v3 refitted |
|---|---|---|---|
| LOEO all | W given t (>= 3 W) | 5.48% (+0.63), n 1344 | 5.52% (+0.65), n 1344 |
| LOEO all | J over idle t forecast (>= 3 W) | 6.01% (+0.53), n 1344 | 6.08% (+0.55), n 1344 |
| LOEO all | J at rest given t | 2.15% (+0.10), n 1416 | 2.16% (+0.11), n 1416 |
| LOEO all | J at rest t forecast | 4.47% (-0.09), n 1416 | 4.49% (-0.08), n 1416 |
| LOEO aifoundry3 card 0 | W given t (>= 3 W) | 6.26% (+0.71), n 357 | 6.41% (+0.77), n 357 |
| LOEO aifoundry1 card 1 | W given t (>= 3 W) | 6.62% (+0.24), n 281 | 6.66% (+0.28), n 281 |
| LOEO aifoundry2 card 0 | W given t (>= 3 W) | 4.23% (+0.46), n 587 | 4.20% (+0.47), n 587 |
| LOEO aifoundry1 card 0 | W given t (>= 3 W) | 5.42% (+2.12), n 119 | 5.36% (+2.12), n 119 |
| LOEO exp E210 | W given t (>= 3 W) | 3.74% (-3.02), n 17 | 4.37% (-3.16), n 17 |
| LOEO exp E212 | W given t (>= 3 W) | 5.30% (+0.69), n 378 | 5.33% (+0.65), n 378 |
| LOEO exp E213 | W given t (>= 3 W) | 9.83% (-0.86), n 104 | 9.91% (-0.70), n 104 |
| LOEO kinds newly counted (v31-counts) | W given t (>= 3 W) | 7.69% (+4.06), n 46 | 7.87% (+3.81), n 46 |
| LOEO zeros on card 1 | W given t (>= 3 W) | 5.83% (+0.35), n 76 | 5.55% (+0.29), n 76 |
| LOCO (anchor route) all | W given t (>= 3 W) | 10.92% (+1.77), n 1748 | 8.85% (-5.24), n 1748 |
| LOCO (anchor route) aifoundry3 card 0 | W given t (>= 3 W) | 10.66% (-6.19), n 474 | 8.37% (-4.49), n 474 |
| LOCO (anchor route) aifoundry1 card 1 | W given t (>= 3 W) | 12.47% (+7.63), n 405 | 12.55% (-10.09), n 405 |
| LOCO (anchor route) aifoundry2 card 0 | W given t (>= 3 W) | 10.75% (+2.98), n 734 | 6.78% (-4.92), n 734 |
| LOCO (anchor route) aifoundry1 card 0 | W given t (>= 3 W) | 7.12% (+5.54), n 135 | 6.67% (+4.93), n 135 |
| LOCO (anchor route) exp E210 | W given t (>= 3 W) | 14.24% (-13.27), n 22 | 10.54% (-9.83), n 22 |
| LOCO (anchor route) exp E212 | W given t (>= 3 W) | 10.83% (+4.00), n 444 | 10.35% (-5.39), n 444 |
| LOCO (anchor route) exp E213 | W given t (>= 3 W) | 13.25% (-2.11), n 106 | 12.24% (-6.76), n 106 |
| LOCO (anchor route) kinds newly counted (v31-counts) | W given t (>= 3 W) | 20.07% (+13.04), n 46 | 7.94% (-2.77), n 46 |
| LOCO (anchor route) zeros on card 1 | W given t (>= 3 W) | 4.86% (-0.75), n 106 | 17.37% (-16.81), n 106 |
| LOCO (fallback route) all | W given t (>= 3 W) | 9.64% (-2.69), n 1748 | 9.11% (-2.42), n 1748 |
| LOCO (fallback route) aifoundry3 card 0 | W given t (>= 3 W) | 11.07% (+8.46), n 474 | 9.54% (+6.67), n 474 |
| LOCO (fallback route) aifoundry1 card 1 | W given t (>= 3 W) | 8.16% (-5.62), n 405 | 12.55% (-10.09), n 405 |
| LOCO (fallback route) aifoundry2 card 0 | W given t (>= 3 W) | 9.96% (-9.23), n 734 | 6.78% (-4.92), n 734 |
| LOCO (fallback route) aifoundry1 card 0 | W given t (>= 3 W) | 5.93% (+2.55), n 135 | 5.74% (+2.32), n 135 |
| LOCO (fallback route) exp E210 | W given t (>= 3 W) | 5.89% (+5.11), n 22 | 4.49% (+3.39), n 22 |
| LOCO (fallback route) exp E212 | W given t (>= 3 W) | 8.98% (-5.47), n 444 | 10.20% (-5.93), n 444 |
| LOCO (fallback route) exp E213 | W given t (>= 3 W) | 12.02% (+1.92), n 106 | 12.47% (-0.20), n 106 |
| LOCO (fallback route) kinds newly counted (v31-counts) | W given t (>= 3 W) | 8.74% (+1.27), n 46 | 8.15% (+0.44), n 46 |
| LOCO (fallback route) zeros on card 1 | W given t (>= 3 W) | 8.74% (-7.41), n 106 | 17.37% (-16.81), n 106 |
| LOKO all | W given t (>= 3 W) | 7.40% (-1.38), n 378 | 8.68% (-1.68), n 378 |
| LOKO aifoundry3 card 0 | W given t (>= 3 W) | 7.69% (-1.31), n 237 | 9.32% (-2.07), n 237 |
| LOKO aifoundry1 card 1 | W given t (>= 3 W) | 19.72% (-10.17), n 11 | 19.77% (-9.95), n 11 |
| LOKO aifoundry2 card 0 | W given t (>= 3 W) | 4.28% (-0.76), n 130 | 5.24% (-0.27), n 130 |
| LOKO exp E213 | W given t (>= 3 W) | 24.17% (-15.39), n 15 | 24.30% (-15.43), n 15 |
| LOKO zeros on card 1 | W given t (>= 3 W) | 9.01% (+8.30), n 2 | 9.37% (+9.29), n 2 |
| LEAVE rgm211 all | W given t (>= 3 W) | 3.70% (+1.32), n 20 | 3.75% (+1.43), n 20 |
| LEAVE rgm211 aifoundry3 card 0 | W given t (>= 3 W) | 3.70% (+1.32), n 20 | 3.75% (+1.43), n 20 |
| LEAVE rgm211 exp E213 | W given t (>= 3 W) | 4.19% (+0.70), n 8 | 4.18% (+0.75), n 8 |
| LOLO all | W given t (>= 3 W) | 6.52% (+0.23), n 140 | 6.58% (+0.33), n 140 |
| LOLO aifoundry3 card 0 | W given t (>= 3 W) | 5.39% (+2.87), n 11 | 5.26% (+2.81), n 11 |
| LOLO aifoundry1 card 1 | W given t (>= 3 W) | 9.51% (-0.08), n 32 | 9.57% (-0.02), n 32 |
| LOLO aifoundry2 card 0 | W given t (>= 3 W) | 4.21% (-1.86), n 70 | 4.25% (-1.74), n 70 |
| LOLO aifoundry1 card 0 | W given t (>= 3 W) | 7.47% (+4.96), n 27 | 7.62% (+5.13), n 27 |
| LOLO exp E212 | W given t (>= 3 W) | 7.09% (-0.61), n 96 | 7.18% (-0.50), n 96 |
| LOLO exp E213 | W given t (>= 3 W) | NOT RUN | NOT RUN |
| LOLO kinds newly counted (v31-counts) | W given t (>= 3 W) | 6.01% (+4.79), n 6 | 6.54% (+5.69), n 6 |
| LOLO zeros on card 1 | W given t (>= 3 W) | 9.78% (-6.82), n 5 | 9.77% (-6.74), n 5 |

**`out/points_time_v31.csv`** (one row a time point, in the fit's order): `meas_T_x_f` is the measured wall op time T as the fit reads it (us) times the point's mean clock f (MHz), in cycles an op, rounded to 3 decimals: the quantity every prediction column (`v31_*`, `v3r_*`: the predicted T times the same f) is compared with, so its errors are the fit's. It is not the mean of the runs' wall cycles: the two differ by at most 0.0021 cycles before the 3-decimal rounding (0.0023 after it), and before the rounding by more than 0.0005 cycles at 6 points, all on aifoundry2 card 0 under its governor. The column was headed `meas_cyc_wall` until fix-fit-v31 relabelled it (verify-fit-v31's nit; no value changed; `summary_v31.py` writes the new name). `out/v31-e212-fold.csv`'s `meas_cyc_wall`, rule 4(a)'s input to the frozen comparator, is the runs' mean wall cycles and keeps its name.

## 5. The acceptance rules (`out/decisions_v31.json` step7)

1. LOEO wall (no twin) v3.1 4.723% against v3 refitted 4.723%; LOEO W given t (no twin, >= 3 W) 5.476% against 5.517%: **FAIL**.
2. LOCO wall 4.150% against 4.150%; LOCO W given t (anchor route) 10.920% against 8.848% (bar: 0.30 points): **FAIL**; the fallback route beside: 9.64% (-2.69), n 1748 against 9.11% (-2.42), n 1748.
3. Leave rgm211 out: wall 6.248% over 20 points (bar 8.0%), E211's W pairs inside 0.05: 8 of 10 (bar 7): **PASS**.
4. (a) The E212 fold against MM1-v2's unread error on the same records (`comparator_4a_v31.py`): wall v3.1 4.95% (-0.77), n 432 against 6.81% (-3.41), n 432; W given t 5.05% (+0.31), n 373 against 7.70% (+2.05), n 373: **PASS**.
   (b) The E213 fold against MM1-v3's blind error on the same points: wall per case v3.1 4.12% (-1.03), n 115 against 4.27% (+1.19), n 115; W given t per point 9.88% (-0.88), n 103 against 15.36% (+1.77), n 103: **PASS**. The E213 fold is held out for every constant and post hoc for the forms E213 helped choose (items 8, 1, 3 and 4).

**Accepted: False.** If a rule fails v3.1 is still frozen as built (the declaration's rule) and the failing rule is named.

## 6. REPORTED (`out/reported_v31.json`; never deciding a rule)

- Item 8: family C by format under both frozen forms: {"all": {"T5r": {"bias_pct": 1.5428, "n": 20, "rms_pct": 5.2743}, "tC": {"bias_pct": -2.0666, "n": 20, "rms_pct": 6.1771}}, "fp32": {"T5r": {"bias_pct": 1.9641, "n": 10, "rms_pct": 5.5463}, "tC": {"bias_pct": -0.8826, "n": 10, "rms_pct": 5.7237}}, "int8": {"T5r": {"bias_pct": 1.1215, "n": 10, "rms_pct": 4.9875}, "tC": {"bias_pct": -3.2506, "n": 10, "rms_pct": 6.5994}}}; E146's store rungs under both forms: {"T5r": {"E146 store rungs (never trained)": {"bias_pct": 0.8479, "n": 87, "rms_pct": 5.095}, "source": "its LOEO E146 fold (the record)"}, "tC": {"E146 store rungs (never trained)": {"bias_pct": -0.9261, "n": 87, "rms_pct": 3.5218}, "source": "its LOEO E146 fold (the record)"}}.
- Item 2 per LOCO fold (kc from the anchor, the fallback's kc, validity, the anchor points' residuals): see step7 `v31_routes` in `out/decisions_v31.json`; not wanted (the anchor route's pooled LOCO above the fallback's): True.
- Item 1: b2, d2 and xi per fold and their bound activity in step6; the joules by class at E213's points: {"L2_share_min_max": [0.0, 0.0], "how": "W by class at the measured op time, x the die factor; share of the model W", "mean_share_by_class": {"C_stores": 0.03553, "awake_memory_path": 0.07528, "awake_minions": 0.07264, "data_switches": 0.28655, "governed_base": 0.0, "instructions_vs_rgm136": -0.00028, "lines_L2": 0.0, "lines_L3": 0.15645, "lines_fresh": 0.15238, "ungated_base": 0.37952, "zero_gate_saving": -0.15806}}.
- v3-ledger (never chosen): {"LOEO W given t (>= 3 W)": {"bias_pct": 0.1794, "n": 1678, "rms_pct": 5.4193}, "LOKO W given t (>= 3 W)": {"bias_pct": -1.2482, "n": 378, "rms_pct": 7.4248}}.
- E213's rgm211 / rgm136 pairs under leave rgm211 out: {"aifoundry1 card 1 (1, 1, 1) int8 rgm136 gemmLnc": 0.0247, "aifoundry1 card 1 (3, 1, 3) fp32 rgm136 gemmLnc": 0.00897, "aifoundry3 card 0 (1, 1, 1) int8 rgm136 gemmLnc": 0.0249, "aifoundry3 card 0 (1, 1, 44) fp32 rgm136 gemmLnc": -0.03372, "aifoundry3 card 0 (1, 1, 44) fp32 rgm211 gemmL": 0.0036, "aifoundry3 card 0 (1, 1, 44) fp32 rgm211 gemmLn": -0.0053, "aifoundry3 card 0 (1, 6, 5) fp32 rgm136 gemmLnc": 0.08599, "aifoundry3 card 0 (1, 6, 5) fp32 rgm211 gemmL": -0.00183, "aifoundry3 card 0 (1, 6, 5) fp32 rgm211 gemmLn": -0.0193, "aifoundry3 card 0 (3, 1, 3) fp32 rgm136 gemmLnc": 0.0091, "aifoundry3 card 0 (3, 1, 3) fp32 rgm211 gemmL": 0.0044, "aifoundry3 card 0 (3, 1, 3) fp32 rgm211 gemmLn": -0.01246, "aifoundry3 card 0 (4, 1, 6) fp32 rgm136 gemmLnc": 0.0198, "aifoundry3 card 0 (4, 1, 6) fp32 rgm211 gemmL": 0.02069, "aifoundry3 card 0 (4, 1, 6) fp32 rgm211 gemmLn": 0.03155}.
- MM1-v3's blind E213 score as committed: {"A": {"E1": {"n": 87, "pass": 82}, "E2": {"n": 87, "pass": 82}, "E3": {"n": 87, "pass": 81}, "E4": {"n": 87, "pass": 78}, "T1": {"n": 84, "pass": 81}, "T2": {"n": 84, "pass": 82}, "T3": {"n": 84, "pass": 81}, "verdicts": {"E1": "PASS", "E2": "PASS", "E3": "PASS", "E4": "FAIL", "H1": "MM1-v3 BETTER", "H2": "MM1-v3 BETTER", "H3": "MM1-v3 BETTER", "H4": "MM1-v3 BETTER", "H5": "MM1-v3 BETTER", "R0": "PASS", "S6": "PASS", "T1": "PASS", "T2": "PASS", "T3": "PASS"}}, "B": {"E1": {"n": 38, "pass": 36}, "E2": {"n": 38, "pass": 36}, "E3": {"n": 38, "pass": 36}, "E4": {"n": 38, "pass": 36}, "T1": {"n": 31, "pass": 31}, "T2": {"n": 31, "pass": 31}, "T3": {"n": 31, "pass": 31}, "verdicts": {"E1": "PASS", "E2": "PASS", "E3": "PASS", "E4": "PASS", "H1": "MM1-v3 BETTER", "H2": "NOT DECIDED", "H3": "MM1-v3 BETTER", "H4": "MM1-v3 BETTER", "H5": "MM1-v3 BETTER", "R0": "PASS", "S6": "PASS", "T1": "PASS", "T2": "PASS", "T3": "PASS"}}}.

## 7. E215: the points and the forecasts (`e215_v31.py`, `out/e215/`)

Arm A only: aifoundry3 card 0 at 600 MHz (the round's brief). The never-run scan in E213's form (`out/e215/scan-e215.json`, sha256 `2cafc497d2575bac504b6c98a51c43cb5ce979ef240e43c74a65c885128e23da`), the point rule of item 10 on v3.1's frozen predictor (params sha256 `d01009a0f586bb6e58ce5a5a1376fa0aaa567f086798f96c0d9dac7a83c9a7e3`) and MM1-v3's.

| family | grid | never-run candidates (literal) | chosen | post hoc reading: candidates / chosen |
|---|---|---|---|---|
| C | 1020 | 826 | 10 of 10 | - / - |
| L | 193392 | 0 | 0 of 20 | 192054 / 20 |
| P | 2416 | 2043 | 12 of 12 | - / - |
| R | 518 | 354 | 10 of 10 | - / - |
| S | 19 | 0 | 0 of 8 | 14 / 8 |

Card time, desk estimate in E213's run form: {"cap_A_min": 70, "literal_minutes": 14.7, "literal_runs": 32, "note": "S as A B B A blocks (4 runs a kind); one run a point otherwise; the registration plans the runs", "pace_s_per_run": 25.959633027522933, "smoke_min": 0.89, "with_posthoc_L_S_minutes": 37.2, "with_posthoc_L_S_runs": 84}.

| family | reading | how | point (loop, arm, format, kind, mask) | score | v3.1 cycles (wall) | v3 cycles (wall) | v3.1 W over idle | v3 W over idle |
|---|---|---|---|---|---|---|---|---|
| L | posthoc | by score (1 of 10) | rgm136 gemmL, gemmL1x9x6, fp32, random, 0xf0ffffff | 0.021621 | 1196.2048 | 1170.6191 | 16.67380 | 16.99977 |
| L | posthoc | by score (2 of 10) | rgm136 gemmL, gemmL1x9x6, fp32, random, 0xff0fffff | 0.021621 | 1196.2048 | 1170.6191 | 16.67380 | 16.99977 |
| L | posthoc | by score (3 of 10) | rgm136 gemmL, gemmL1x9x6, fp32, random, 0xfff0ffff | 0.021621 | 1196.2048 | 1170.6191 | 16.67380 | 16.99977 |
| L | posthoc | by score (4 of 10) | rgm136 gemmL, gemmL1x9x6, fp32, random, 0xffff0fff | 0.021621 | 1196.2048 | 1170.6191 | 16.67380 | 16.99977 |
| L | posthoc | by score (5 of 10) | rgm136 gemmL, gemmL1x9x6, fp32, random, 0xfffff0ff | 0.021621 | 1196.2048 | 1170.6191 | 16.67380 | 16.99977 |
| L | posthoc | by score (6 of 10) | rgm136 gemmL, gemmL1x9x6, fp32, random, 0xffffff0f | 0.021621 | 1196.2048 | 1170.6191 | 16.67380 | 16.99977 |
| L | posthoc | by score (7 of 10) | rgm136 gemmL, gemmL1x9x6, fp32, random, 0xfffffff | 0.021621 | 1196.2048 | 1170.6191 | 16.67380 | 16.99977 |
| L | posthoc | by score (8 of 10) | rgm136 gemmL, gemmL1x9x6, fp32, random, 0xfffffff0 | 0.021621 | 1196.2048 | 1170.6191 | 16.67380 | 16.99977 |
| L | posthoc | by score (9 of 10) | rgm136 gemmL, gemmL1x9x6, fp32, random, 0xbbbbbbbb | 0.021420 | 1187.0144 | 1161.8590 | 14.44383 | 14.71127 |
| L | posthoc | by score (10 of 10) | rgm136 gemmL, gemmL1x9x6, fp32, random, 0xdddddddd | 0.021420 | 1187.0144 | 1161.8590 | 14.44383 | 14.71127 |
| L | posthoc | random draw 1 of 10 | rgm136 gemmL, gemmL1x6x5, fp32, random, 0x33000333 | 0.002346 | 1057.0123 | 1059.4947 | 6.83956 | 6.79252 |
| L | posthoc | random draw 2 of 10 | rgm136 gemmL, gemmL1x2x13, fp32, random, 0x77007707 | 0.002284 | 1393.1347 | 1389.9561 | 8.05973 | 8.04333 |
| L | posthoc | random draw 3 of 10 | rgm136 gemmL, gemmL2x3x5, fp32, random, 0x99990000 | 0.000623 | 1060.8587 | 1061.5204 | 5.50106 | 5.45565 |
| L | posthoc | random draw 4 of 10 | rgm136 gemmL, gemmL8x1x4, fp32, random, 0x30000000 | 0.000418 | 1304.4660 | 1303.9211 | 1.41451 | 1.34642 |
| L | posthoc | random draw 5 of 10 | rgm136 gemmL, gemmL1x9x6, fp32, random, 0x2002202 | 0.020366 | 1141.0627 | 1118.0587 | 2.77329 | 2.75262 |
| L | posthoc | random draw 6 of 10 | rgm136 gemmL, gemmL2x6x10, fp32, random, 0x4404444 | 0.010090 | 1298.3323 | 1285.2986 | 3.63607 | 3.60291 |
| L | posthoc | random draw 7 of 10 | rgm136 gemmL, gemmL1x8x6, fp32, random, 0xd000dd0 | 0.014868 | 1244.9272 | 1226.5548 | 5.42813 | 5.44743 |
| L | posthoc | random draw 8 of 10 | rgm136 gemmL, gemmL2x4x16, fp32, random, 0x990009 | 0.002466 | 1455.2514 | 1451.6673 | 3.37543 | 3.32121 |
| L | posthoc | random draw 9 of 10 | rgm136 gemmL, gemmL1x7x6, fp32, random, 0x10100000 | 0.013590 | 1091.3475 | 1076.6166 | 1.59693 | 1.54185 |
| L | posthoc | random draw 10 of 10 | rgm136 gemmL, gemmL2x4x4, fp32, random, 0xee0e00 | 0.004178 | 1115.2587 | 1119.9276 | 5.94968 | 5.89394 |
| P | literal | by score (1 of 6) | rgm211 gemmLn, gemmLn1x15x3, fp32, random, 0xffffffff | 0.023431 | 1147.4496 | 1120.8758 | 19.94845 | 20.41674 |
| P | literal | by score (2 of 6) | rgm211 gemmLn, gemmLn1x12x4, fp32, random, 0xffffffff | 0.023282 | 1144.9613 | 1118.6125 | 19.84865 | 20.29569 |
| P | literal | by score (3 of 6) | rgm211 gemmLn, gemmLn1x10x5, fp32, random, 0xffffffff | 0.023167 | 1145.2204 | 1118.9938 | 19.76405 | 20.19723 |
| P | literal | by score (4 of 6) | rgm136 gemmLnc, gemmLnc1x15x3, fp32, random, 0xffffffff | 0.022872 | 1175.1996 | 1148.6258 | 19.55394 | 20.00003 |
| P | literal | by score (5 of 6) | rgm211 gemmLn, gemmLn1x9x6, fp32, random, 0xffffffff | 0.022768 | 1155.6496 | 1129.6350 | 19.56622 | 19.98111 |
| P | literal | by score (6 of 6) | rgm136 gemmLnc, gemmLnc1x12x4, fp32, random, 0xffffffff | 0.022725 | 1172.7113 | 1146.3625 | 19.45567 | 19.88109 |
| P | literal | random draw 1 of 6 | rgm211 gemmL, gemmL1x5x7, fp32, random, 0xffffffff | 0.005063 | 1109.0272 | 1103.4265 | 20.14378 | 20.27650 |
| P | literal | random draw 2 of 6 | rgm136 gemmL, gemmL1x15x1, int8, random, 0xffffffff | 0.003619 | 1038.0118 | 1041.7748 | 10.39140 | 10.57573 |
| P | literal | random draw 3 of 6 | rgm136 gemmL, gemmL1x4x5, fp32, random, 0xffffffff | 0.005591 | 1091.0956 | 1097.2133 | 20.43488 | 20.38025 |
| P | literal | random draw 4 of 6 | rgm136 gemmL, gemmL1x10x1, int8, random, 0xffffffff | 0.000689 | 877.4422 | 878.0473 | 10.83359 | 10.82564 |
| P | literal | random draw 5 of 6 | rgm136 gemmLnc, gemmLnc8x1x5, fp32, random, 0xffffffff | 0.002381 | 1389.8284 | 1393.1413 | 16.58201 | 16.59567 |
| P | literal | random draw 6 of 6 | rgm136 gemmLnc, gemmLnc5x1x10, fp32, random, 0xffffffff | 0.002528 | 1390.8072 | 1394.3281 | 16.44607 | 16.44383 |
| C | literal | by score (1 of 5) | rgm136 gemmL, gemmL2x15x2, fp32, random, 0xffffffff | 0.014206 | 1165.5593 | 1149.1180 | 19.70893 | 20.04939 |
| C | literal | by score (2 of 5) | rgm136 gemmL, gemmL3x15x2, fp32, random, 0xffffffff | 0.014206 | 1165.5593 | 1149.1180 | 19.70893 | 20.04939 |
| C | literal | by score (3 of 5) | rgm136 gemmL, gemmL10x15x2, fp32, random, 0xffffffff | 0.014206 | 1165.5593 | 1149.1180 | 19.70893 | 20.04939 |
| C | literal | by score (4 of 5) | rgm136 gemmL, gemmL11x15x2, fp32, random, 0xffffffff | 0.014206 | 1165.5593 | 1149.1180 | 19.70893 | 20.04939 |
| C | literal | by score (5 of 5) | rgm136 gemmL, gemmL12x15x2, fp32, random, 0xffffffff | 0.014206 | 1165.5593 | 1149.1180 | 19.70893 | 20.04939 |
| C | literal | random draw 1 of 5 | rgm136 gemmL, gemmL11x11x1, int8, random, 0xffffffff | 0.000314 | 968.1397 | 967.8358 | 10.86494 | 11.09392 |
| C | literal | random draw 2 of 5 | rgm136 gemmL, gemmL8x15x1, int8, random, 0xffffffff | 0.002686 | 1069.4547 | 1072.3307 | 10.21773 | 10.40654 |
| C | literal | random draw 3 of 5 | rgm136 gemmL, gemmL4x13x1, fp32, random, 0xffffffff | 0.003496 | 1041.8582 | 1045.5064 | 21.45126 | 21.61189 |
| C | literal | random draw 4 of 5 | rgm136 gemmL, gemmL15x9x2, fp32, random, 0xffffffff | 0.003466 | 1103.5492 | 1107.3804 | 20.58995 | 20.65089 |
| C | literal | random draw 5 of 5 | rgm136 gemmL, gemmL16x9x2, fp32, random, 0xffffffff | 0.003466 | 1103.5492 | 1107.3804 | 20.58995 | 20.65089 |
| R | literal | by score (1 of 5) | rgm136 gemmL, gemmL2x1x7, fp32, random, 0xffffffff | 0.012051 | 1239.2010 | 1224.3574 | 18.14915 | 18.37071 |
| R | literal | by score (2 of 5) | rgm136 gemmL, gemmL2x1x7, int8, random, 0xffffffff | 0.011033 | 1253.4030 | 1239.6498 | 8.84879 | 8.94273 |
| R | literal | by score (3 of 5) | rgm136 gemmL, gemmL1x1x41, fp32, random, 0xffffffff | 0.010523 | 1554.2112 | 1537.9419 | 15.83571 | 15.89914 |
| R | literal | by score (4 of 5) | rgm136 gemmL, gemmL1x1x41, int8, random, 0xffffffff | 0.010523 | 1554.2112 | 1537.9419 | 8.49273 | 8.47256 |
| R | literal | by score (5 of 5) | rgm136 gemmL, gemmL1x1x39, fp32, random, 0xffffffff | 0.010428 | 1549.2000 | 1533.1294 | 15.84891 | 15.91144 |
| R | literal | random draw 1 of 5 | rgm136 gemmL, gemmL2x3x12, int8, random, 0xffffffff | 0.005716 | 1460.9988 | 1452.6720 | 8.39852 | 8.41100 |
| R | literal | random draw 2 of 5 | rgm136 gemmL, gemmL2x2x11, int8, random, 0xffffffff | 0.001631 | 1415.3169 | 1413.0110 | 8.43846 | 8.46661 |
| R | literal | random draw 3 of 5 | rgm136 gemmL, gemmL1x4x22, fp32, random, 0xffffffff | 0.000105 | 1578.2246 | 1578.0593 | 15.54560 | 15.55659 |
| R | literal | random draw 4 of 5 | rgm136 gemmL, gemmL1x1x37, int8, random, 0xffffffff | 0.009855 | 1543.1693 | 1528.0358 | 8.46924 | 8.44990 |
| R | literal | random draw 5 of 5 | rgm136 gemmL, gemmL2x2x11, fp32, random, 0xffffffff | 0.001765 | 1411.6790 | 1409.1895 | 16.54219 | 16.59199 |
| S | posthoc | by score (1 of 4) | rgm136 gemmL, gemmL3x1x3, int8, pattern:i8_den6, 0xffffffff | 0.052944 | 946.2101 | 945.5506 | 6.52341 | NOT FORECAST |
| S | posthoc | by score (2 of 4) | rgm136 gemmL, gemmL3x1x3, int8, pattern:i8_den3, 0xffffffff | 0.028323 | 946.2101 | 945.5506 | 5.87749 | NOT FORECAST |
| S | posthoc | by score (3 of 4) | rgm136 gemmL, gemmL3x1x3, fp32, pattern:pow2, 0xffffffff | 0.020753 | 902.8328 | 903.3098 | 13.66801 | NOT FORECAST |
| S | posthoc | by score (4 of 4) | rgm136 gemmL, gemmL3x1x3, fp32, pattern:den21, 0xffffffff | 0.011999 | 902.8328 | 903.3098 | 19.46672 | NOT FORECAST |
| S | posthoc | random draw 1 of 4 | rgm136 gemmL, gemmL3x1x3, int8, pattern:i8_pm1, 0xffffffff | 0.010493 | 946.2101 | 945.5506 | 10.79489 | NOT FORECAST |
| S | posthoc | random draw 2 of 4 | rgm136 gemmL, gemmL3x1x3, fp32, pattern:lanes2, 0xffffffff | 0.003558 | 902.8328 | 903.3098 | 11.73110 | NOT FORECAST |
| S | posthoc | random draw 3 of 4 | rgm136 gemmL, gemmL3x1x3, fp32, pattern:fp16grid, 0xffffffff | 0.009056 | 902.8328 | 903.3098 | 18.77172 | NOT FORECAST |
| S | posthoc | random draw 4 of 4 | rgm136 gemmL, gemmL3x1x3, fp32, pattern:bf16trunc, 0xffffffff | 0.010677 | 902.8328 | 903.3098 | 17.27647 | NOT FORECAST |

- `out/e215/mm1_v31_e215.csv`: sha256 `f8fe39b4fb847791352d5ccbcc92406f32cf28347fb3af1bca96b851bc8bc2cc`
- `out/e215/mm1_v31_e215.json`: sha256 `90742cddce9a355ddf53e85eb80a8075bc67613d36e804d12a8d422d342fd4d4`
- `out/e215/e215_choice.json`: sha256 `c1bfd070c9d48aa1cf60aa0c7983e4387f75a543c7e7da4e07c89e945d0cee84`

**Two readings the declaration leaves open, named for E215's registration** (verify-fit-v31's findings 2 and 3, low; REPORTED; nothing re-applied here: which reading holds is the registration's to state by a dated note, after which it re-applies the point rule, and forecasts for any changed point come from the frozen predictor `mm1_v31.py` with `out/mm1_v31_params.json` before any E215 datum). The lists and forecasts above are the reading applied here, unchanged.

- *Family C's top half rests on a 1-ulp difference.* The rule takes ceil(q / 2) of the quota by descending score, 'ties by the sorted token'. In `out/e215/e215_choice.json` gemmL3x15x2 fp32 scores 0.014206373479944604 and gemmL10x15x2, 11x15x2 and 12x15x2 score 0.014206373479944386: the same v3.1 forecast (1165.5592688305471 cycles) and v3 forecasts of 1149.1179607420363 against 1149.1179607420365 cycles, one ulp apart, so gemmL3x15x2 took a top-half place by score. verify-fit-v31 finds 13 fp32 candidates exactly at the lower score (gemmL4x15x2 to 16x15x2) and gemmL3x15x2 one ulp above; read as one tie broken by the sorted token, the top half is gemmL2x15x2, 10x15x2, 11x15x2, 12x15x2 and 13x15x2, the random half then draws gemmL15x9x2 and 16x9x2 as int8 instead of fp32, and 3 of family C's 10 points change. A tie tolerance stated by the registration (for example 1e-12 relative) settles it.

- *Family P's random half rests on two readings.* (a) The grid's '(int8 at KB <= 2)': read here as int8 beside fp32 at KB <= 2 (a grid of 2416); E213's family P, the precedent, ran int8 instead of fp32 at KB 1, and under that reading (a grid of 2168) verify-fit-v31 finds the six points by score unchanged and all six random points changed. (b) The order inside a shared token: E213's never-run token names the shape alone, and 516 of P's tokens are shared by several candidates; read here by (arm token, loop, format, kind, mask) (section 8), while (arm token, format, loop, ...) gives a different random half (verify-fit-v31).

## 8. Departures, gaps and NOT RUN

- E215 is arm A only: aifoundry3 card 0 at 600 MHz (the round's brief). Item 10 names arm B (aifoundry1 card 1) as the lab's bookings and the model session's claims allow; the model session holds aifoundry1 tonight, so no arm B point was chosen (NOT RUN).
- E215's families L and S: E213's shape-level never-run token removes every candidate (L's shapes ran full-chip on aifoundry3 by the grid's own condition; S's gemmL3x1x3 ran in E213), so the literal rule chooses none of them. Beside the literal list, labelled post hoc and a named departure for E215's registration to adopt or not by a dated amendment: L by a configuration-level reading (a (shape, mask) that no measured point of MM1-v3.1's data holds and no scanned file holding the shape token names) and S by a kind-level one (a counted kind never run in a GEMM on aifoundry3 card 0), each chosen by item 10's score and draw; their forecasts are frozen with the rest.
- E215's family L candidates are scored at one product mask per (shape, |G|, |C|): at a product mask both models' op times depend on (shape, |G|, |C|) only (the masked stream is the same up to an order-preserving relabeling of tiles; n/32, n_eff and the row imbalance read |G| and |C|); the chosen points' own masks were checked equal (e215_choice.json, L_representative_mask_check).
- E215's family P grid read as fp32 random at every KB and int8 random at KB <= 2 (both); E215's tie order and draw order sort by (arm token, loop, format, kind, mask), since E213's token names the shape alone.
- E215's never-run scan: E213's scan code (its token rule, roots, folder classes and reader) with nothing subtracted (E213 has run; no E215 folder exists) and MM1-v3.1's measured points in place of MM1-v3's. MM1-v2's E215 forecasts: NOT RUN (left to E215's registration).
- E212's sparse50f / sparse50i arms are priced in energy as the committed sparse50 kind (the counts' README, section 1; the unread test's group C); their time cases keep MM1-v3's spelling.
- E213's time points pool a case's runs (the declaration's 'the mean of its runs'); E213's scorer averages a case's points' means instead (at most 0.06% apart on arm A): item 8 and rule 4(b), whose declared source is the scorer, use the scorer's figures.
- Item 5's flag (a winner one start alone reached) is read as: at most one of the 18 phase-1 costs within 1e-3 relative of the winner's phase-2 cost; phase 2's restart test measures each leg's relative fall from that leg's starting cost (the first leg's from the phase-1 end).
- Item 3's not-identified reading (every constant within 1% of 0): |constant| <= 0.01 (REPORTED only).
- Seconds are scored on the energy points with a measured seconds a GEMM; MM1-v3's time records of E206-style data carry none.
- The identification report's Jacobian is central differences at the all-data fit (scipy's own is not kept); relative standard errors from s2 pinv(J^T J).
- In the LOCO fold without aifoundry3 the anchor route solves a factor on aifoundry3's per-op term (its kc, 1 by definition elsewhere) after A2's rescale, as item 2 says.
- MM1-v3's own LOLO sets: the subset points' membership under MM1-v3's sets is reported beside the declared classes; fits on MM1-v3's own sets NOT RUN.
- The census paths' check (the declaration's deferred item): no committed counted simulator run of gemmLnc or of rgm211's loops exists at GitHub main (E211's dated correction 1 lists them NOT RUN), so their census entries stand.
- Not built, as declared: T6A, T8, a_row, lambda fitted (0.0048 a C), a kappa of their own for scalar instruction classes, tensor-queue blocking and the second hart; E202's kernel as a fourth kernel out NOT RUN.
- The background time limit of the lane's tools stopped the fit jobs at two hours; each restart resumed from the last finished fold (every fold record is kept as it ends), so no fold was fitted twice into the record.
- Lane fix-fit-v31 (Q222), answering verify-fit-v31 (HOLDS WITH FIXES) before the land: `item3_flat_v31.py` added (post hoc, no fit) with `out/item3_flat_v31.json`; `out/decisions_v31.json` gained step3's identification labels (new keys only: every value fit-v31 wrote is unchanged); `out/points_time_v31.csv`'s header relabelled (`meas_cyc_wall` to `meas_T_x_f`; every data row unchanged) and `summary_v31.py`'s writer with it (that string and a comment); `readme_v31.py` prints the labels and the lanes' new lines, and this README was re-made by it. No fit, constant, decision, forecast, parameter file, fit record or other output changed: each is byte for byte fit-v31's.

## 9. Files and how to reproduce

Code: `data_v31.py` (the points), `energy_v31.py`, `time_v31.py` (imports `t7_v31.py` unchanged), `fit_v31.py` (the fits and folds), `run_v31.py` (the declared order of decisions), `summary_v31.py`, `reported_v31.py`, `check_starts_v31.py`, `mm1_v31.py` (the predictor), `e215_v31.py` (the blind day's points and forecasts), `item3_flat_v31.py` (item 3's identification check and labels, post hoc), `readme_v31.py` (this file). Inputs: `inputs/` (E213's committed data and registered points, census-v3.1, E212's plan tiles for phi; `inputs/SOURCES.tsv`) and MM1-v3's (`../v3/inputs/`, read in place). Outputs: `out/` (fits in `out/fits/`, E215 in `out/e215/`). `SHA256SUMS`: every file this commit adds but itself (`sha256sum -c SHA256SUMS` from this folder; the four frozen declaration files' sha256 are in section 1).

From this folder, single-threaded (OMP_NUM_THREADS=1 and the like), each with `/usr/bin/python3 -I -B`: `run_v31.py --out out --tag final --lanes <the round's lane folders> --scores-A <E213 arm A scores> --scores-B <arm B scores>`; `summary_v31.py --out out`; `reported_v31.py --out out --scores A=... --scores B=...`; `check_starts_v31.py out`; `e215_v31.py scan --lab <the lab> --lanes <lane folders> --out out/e215`; `e215_v31.py choose --scan out/e215/scan-e215.json --params out/mm1_v31_params.json --out out/e215`; then `item3_flat_v31.py --out out --label` (post hoc: `out/item3_flat_v31.json` and the labels in `out/decisions_v31.json`'s step3, new keys only); `readme_v31.py --out out --readme README.md --extra <the lanes' lines>` writes this file.

