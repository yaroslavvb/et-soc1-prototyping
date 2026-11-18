# MM1-v3's switch route on runs it never read in energy: an UNREAD test with the new switch counts (unread-e212sw, Q218, Wed 18 Nov 2026)

**Label: UNREAD.** MM1-v3 (landed b1493082) and the switch counts it lacked (fix-v31counts, `SHA256SUMS` c74c2d49..., frozen by the orchestrator's post #2.7.2.1.1 at 06:28:37 PST; committed unchanged as `tools/matmul/mm1/v3.1/counts/` in 3e8991d0 at 07:23:56 PST) were both frozen before this lane read any power, energy or seconds of the runs scored here. **Not blind:** the data existed, the data lanes had read them, and MM1-v3's design and spec lanes had tabulated some of them; for the E206 and E207 points, so had its build lane and mm-residuals (`DECLARED-unread.md` section g and its dated note 1). Desk only: no card, no simulator, nothing refitted, no constant changed. **Corrected after the verify** (section 9, dated, post hoc): the declaration, the forecasts and the scores are unchanged; this README's wording, fifteen figures it had rounded twice, and an addendum (E209's three real points, missed by the declared list) are what changed.

The owner's words that set the matmul focus (Mon 16 Nov 2026, a voice transcription, where "matte mold" is the matmul): "I want to have a model which predicts matte mold energy and number of transistor switches and clock cycles." No card counts switches. The count can be checked only through energy, when only the data changes (E210). Here the check is made on data patterns MM1-v3 could not price before, because their kinds had no count (MM1-v3 README section 7).

## 0. On one screen

- **Verdict (the declared pass rule, decided by `scripts/s03_score.py`): PASS.** P1-P4 all hold against the declared null N, which is each format's mean of the counted kinds (zeros, ones, random) priced by MM1-v3 itself at the run's own conditions.
- **Q1, W over idle given the run's measured seconds**, group A, 42 cases: MM1-v3 with the new counts reads **6.83% rms (+2.61)**, against N's 24.97% (-16.04). MM1-v3 is closer on 35 cases and N on 5, with 2 ties (exact sign test p = 1.4e-06).
- **Q2, the data-dependent power as a share of D** (E210's registered metric), 29 cases with in-session random and zeros: **5.70% of D rms (+1.93)**, against N's 21.64% (-12.38). MM1-v3 is closer on 23 of 29 (p = 0.0023).
- **By format (group A, Q1 / Q2):** fp32 3.80% (+1.85), n 24 / 3.09% of D (+0.25), n 18; fp16 8.20% (+4.03), n 9 / 8.59% of D (+7.38), n 5; int8 10.57% (+3.23), n 9 / 8.17% of D (+2.41), n 6. fp32's count is gate-level, and the route holds best there. fp16's count is estimated (RTL x the fp32 ratio) and runs high: MM1-v3 over-forecasts its patterns' data share by about 7% of D. int8's count leaves out the arithmetic, and its worst case is `i8_pm1`, at +18.8% of D.
- **Not tabulated by an MM1-v3 design or spec lane** (15 cases: E212 a2c0-S2's 8 on aifoundry2 under its governor, E206 arm A's p112 and E207's 6 points): Q1 5.08% (+1.22), n 15 and Q2 3.04% of D (-2.95), n 6. Seven of them (p112 and E207's six) are not clean: MM1-v3's own build lane wrote their measured W into its committed `out/points_energy_v3.csv` before the freeze, and mm-residuals' committed table holds them too. **The cleanest part is E212 a2c0-S2's 8 runs**, tabulated in energy by no MM1-v3 lane (design, spec or build) and by no residual lane: Q1 1.34% (+0.96), n 8 and Q2 3.04% of D (-2.95), n 6 (section 9.2).
- **REPORTED:** against the stricter null N2 (ones and random only), MM1-v3 also wins every condition: Q1 25.67%, Q2 19.96% of D. Against **MM1-v1's kind term**, which applies on aifoundry3's 10 E206/E207 points, MM1-v1 reads 5.98% and MM1-v3 7.82%, NOT DECIDED (5 of 9). MM1-v1 prices each real tile from ledger v2's per-tile row or a frozen per-tile prediction (and E206 arm A's points were in its own in-sample scoring), while MM1-v3's route prices them from the count at one constant per format. With phi = 1 for every new kind, group A reads Q1 8.29% (+3.20), n 42, so the declared phi rule helps. **Post hoc (addendum 1, section 9.1):** E209's real points e35 (int8) and e36 (fp16), which the declared list missed, read Q1 -0.01% and +4.75% (N -23.13% and -31.74%); with them group A reads 6.71% against N's 25.10%, 37 of 42, p = 4.4e-07, so the verdict is unchanged.
- REPORTED, the checkpoint's other scorings (per run, group A): J at rest given t 2.37% (+1.07), n 59; J over idle with the seconds forecast 7.17% (+2.90), n 59. **Group B** (E206 fp32 real, phi only, 3 points): Q1 4.43% (-0.20), n 3, Q2 0.62% of D (-0.34), n 3. **Group C** (E212's 7 gen-sparse50 runs, the committed sparse50 kind): Q1 2.79% (+2.19), n 7, Q2 3.42% of D (+0.28), n 6.
- Every case's configuration (card, kernel, arm, format, mask, clock) is in MM1-v3's energy fit with other kinds (a configuration twin). Every kind is new to the fit, so the test is of the data term on known configurations, not of new shapes.

## 1. What was scored (`DECLARED-unread.md` section a)

- **Group A** (the pass rule's pool): 46 E212 runs (aifoundry1 card 1 sessions S2 and S3, 38 runs; aifoundry2 card 0 session S2, 8 runs), 19 plan-tile kinds (fp32 10, fp16 5, int8 4), at `gemmL1x1x1` on 32 and 16 shires and at `gemmL4x8x8`. Also 13 E206/E207 points (26 runs): E206's fp16 and int8 real tiles on aifoundry3 and aifoundry1 card 1, and E207's e37, real:blind4 (three formats) and blind3. Each had no switch count in MM1-v3 and has one in the frozen counts. All 59 entered energy by the loaders' own rules, and none was set aside.
- **Group B** (REPORTED): E206's fp32 real points (p110 and p111 on aifoundry3, p111 on card 1). Their count was committed, and only phi was missing.
- **Group C** (REPORTED): E212's 7 gen-sparse50 runs (`sparse50f`, `sparse50i`), the committed sparse50 kind. MM1-v3 had read them for time only.
- **Not scored for Q2:** 13 group A entries have no in-session random-and-zeros pair: a2c0-S2's two 1x1x1 full-chip runs, E206 p112 (arm A) and p113 and p115 (both arms), and E207's six. Group C's a1c0-S2 run lost its random reference to the loader's rule (that reference run is capped).

## 2. The order, the hashes and their times (Pacific, from the box's clock; `logs/progress.txt`)

| when (PST, Wed 18 Nov 2026) | step | what was hashed |
|---|---|---|
| 06:30:22 | before step 1 | the counts' land dir: `sha256sum -c SHA256SUMS` 71 of 71 OK, `SHA256SUMS` c74c2d49c336159f6ca63aad2652601a10e22d6a8b5db00d46c66bfb1cf8aa7f |
| 06:41:58-06:41:59 | step 0 | work copies by `git archive` of GitHub main 8e91dda6: MM1-v3 (its `SHA256SUMS` c24efc14..., 170/170 OK), MM1-v1 (77/77), E212's registration (87/87); the counts copied (71/71) |
| **06:53:28** | **step 1, the declaration** | `DECLARED-unread.md` f1daf832cc0078ef8fe90d108ce646cd3d656ca96634928deb2cfe6787aae44f, `declared-unread.json` 5eb2c93d2d60640347bdd6f827f2800cccb6bfd96ea6744f8e5036839a4c03cc; every step-1 file in `logs/step1-sha256.txt` (8182bf85...) |
| 06:55:50 | step 2 starts | `sha256sum -c SHA256SUMS` in the counts' land dir and in the work copy: 71 of 71 OK each, `SHA256SUMS` c74c2d49... |
| **06:56:16** | **step 2, the forecasts** | `forecasts-unread.csv` 2c26f0138f03f98b52686adee629cf1235364aad86f89aec59e92f11f658c9ee, `forecasts-unread.json` 8938bbebd1a6db028d55602773e7c2bce7286f6e378f2bcede948f82deb79f01, `s02_forecast.py` c8166622... |
| 06:59:05 | the scorer, before the read | `s03_score.py` 74df0a0688179a22c2f65c5567a7989eed0f6940abff6ba308aab176bdb743ab (it refuses to run unless the declaration and the forecasts hash as above) |
| **06:59:15-06:59:16** | **step 3, the first read of the test runs and the score** | `scores-unread.json` a535d78c..., `scores-unread-runs.csv` 892628bb..., `scores-unread-cases.csv` 78cfa3fb... (logged 07:00:09) |
| 07:00:50 | step 4, a re-check | the verdict's four numbers re-derived from the cases CSV alone, and one run by hand from the committed data file (`logs/s04_recheck.out`) |

Every file here, with the scripts as run, is in `SHA256SUMS`. The scripts in `scripts/` are the scripts as run, with the box's paths replaced by `<W>` and `<LAB>`. Their as-run sha256 are in the logs and in the table at the end.

- **Seen before the declaration** (verify-unread-e212sw, from the harness transcript): two measured numbers, neither a group A value nor an input to any forecast: E210.md's quote of E206's S1 random-minus-zeros D (29.78 W, the reference D of group B's p110), and a1c1-S2's session rest values in its `queue.json` (29.91 W, 51 C).
- **The counts, committed** (dated line, Wed 18 Nov 2026, fix-unread-e212sw): the counts folder used here (fix-v31counts' land dir, `SHA256SUMS` c74c2d49...) is on GitHub main unchanged as `tools/matmul/mm1/v3.1/counts/`, added by commit 3e8991d0 (07:23:56 PST): `diff -r` against the land dir used finds no difference, and `sha256sum -c` reads 71 of 71 OK (07:42:01 PST). The hashed declaration keeps the scratch name.

## 3. How each figure was made (summary; the declaration is the rule)

- **MM1-v3 (V3):** the landed predictor, unchanged. The frozen counts were added as rows of the tables `counts()` reads (fp32 at GEMM states; fp16 and int8 in the switch-table form), with no existing row touched. phi follows the declared desk rule, MM1-v3's own formula `kinds_v3.phi` over each kind's tile files. Each run's W over idle is frozen in step 2 in a form exact in its measured conditions, W = [K0 + g G(f) + (1e6/t)(sV K1 + (1 + xi (sV - 1)) K2)] x (1 + 0.0048 (T0 - 50)). In step 3 that form equals the predictor called at the measured conditions to 4.4e-16 (193 calls).
- **N:** the mean of MM1-v3's own W for zeros, ones and random at the run's conditions. N2 is the same over ones and random. **V1:** MM1-v1 frozen, with its own kind term where it has a source.
- **Q1** = W_fc / W_meas - 1 at W_meas >= 3 W (every scored entry is above 3 W). **Q2** = [(W_fc(P) - W_fc(R)) - (W_P - W_R)] / D, with D = W_R - W_Z measured in the same session (E212) or experiment arm (E206).
- **Readings:** E212 from each committed session file at GitHub main 8e91dda6, byte-equal to MM1-v3's vendored copies. The reduction is `data_v3.mms_runs`'s own, and equals it on 1,942 fields of the reference runs. E206/E207 come from MM1-v3's own loader records, whose vendored inputs are byte-equal to the committed data files.

## 4. Results by group, card and format (rms % (signed mean), n; Q2 in % of D)

| set | cases | Q1 MM1-v3 | Q1 N | Q1 N2 | Q2 MM1-v3 | Q2 N | Q2 N2 |
|---|---:|---|---|---|---|---|---|
| A: all | 42 | 6.83% (+2.61), n 42 | 24.97% (-16.04), n 42 | 25.67% (+9.56), n 42 | 5.70% (+1.93), n 29 | 21.64% (-12.38), n 29 | 19.96% (+9.63), n 29 |
| A: card=aifoundry1 card 1 | 24 | 7.45% (+3.44), n 24 | 24.91% (-15.86), n 24 | 26.56% (+11.45), n 24 | 6.33% (+3.44), n 22 | 23.21% (-13.41), n 22 | 20.13% (+8.29), n 22 |
| A: card=aifoundry2 card 0 | 8 | 1.34% (+0.96), n 8 | 6.07% (+1.05), n 8 | 29.07% (+27.20), n 8 | 3.04% (-2.95), n 6 | 7.37% (-4.46), n 6 | 19.84% (+18.93), n 6 |
| A: card=aifoundry3 card 0 | 10 | 7.82% (+1.95), n 10 | 33.15% (-30.12), n 10 | 19.96% (-9.09), n 10 | 2.11% (-2.11), n 1 | 37.38% (-37.38), n 1 | 16.69% (-16.69), n 1 |
| A: fmt=fp16 | 9 | 8.20% (+4.03), n 9 | 34.99% (-32.06), n 9 | 21.21% (-7.88), n 9 | 8.59% (+7.38), n 5 | 21.01% (-17.77), n 5 | 12.12% (+4.58), n 5 |
| A: fmt=fp32 | 24 | 3.80% (+1.85), n 24 | 19.32% (-11.33), n 24 | 25.29% (+16.49), n 24 | 3.09% (+0.25), n 18 | 19.35% (-12.10), n 18 | 18.26% (+10.55), n 18 |
| A: fmt=int8 | 9 | 10.57% (+3.23), n 9 | 26.24% (-12.55), n 9 | 30.33% (+8.50), n 9 | 8.17% (+2.41), n 6 | 27.79% (-8.72), n 6 | 28.32% (+11.09), n 6 |
| A: source=E206A | 4 | 7.99% (+1.19), n 4 | 39.16% (-37.89), n 4 | 21.92% (-19.94), n 4 | 2.11% (-2.11), n 1 | 37.38% (-37.38), n 1 | 16.69% (-16.69), n 1 |
| A: source=E206B | 3 | 8.19% (+2.74), n 3 | 34.05% (-33.03), n 3 | 17.74% (-16.09), n 3 | 3.62% (-3.62), n 1 | 38.04% (-38.04), n 1 | 17.87% (-17.87), n 1 |
| A: source=E207 | 6 | 7.71% (+2.45), n 6 | 28.45% (-24.94), n 6 | 18.54% (-1.86), n 6 | - | - | - |
| A: source=E212 | 29 | 6.28% (+2.83), n 29 | 20.09% (-9.42), n 29 | 28.00% (+18.64), n 29 | 5.85% (+2.28), n 27 | 19.94% (-10.51), n 27 | 20.14% (+11.62), n 27 |
| A: tabulated by an MM1-v3 design/spec lane | 27 | 7.62% (+3.38), n 27 | 26.25% (-17.89), n 27 | 25.78% (+8.34), n 27 | 6.21% (+3.20), n 23 | 24.00% (-14.45), n 23 | 19.99% (+7.21), n 23 |
| A: not tabulated by any MM1-v3 design/spec lane | 15 | 5.08% (+1.22), n 15 | 22.48% (-12.70), n 15 | 25.47% (+11.75), n 15 | 3.04% (-2.95), n 6 | 7.37% (-4.46), n 6 | 19.84% (+18.93), n 6 |
| B: all | 3 | 4.43% (-0.20), n 3 | 44.52% (-44.23), n 3 | 26.40% (-25.97), n 3 | 0.62% (-0.34), n 3 | 53.25% (-53.23), n 3 | 31.30% (-31.30), n 3 |
| B: card=aifoundry1 card 1 | 1 | 3.45% (+3.45), n 1 | 39.87% (-39.87), n 1 | 21.92% (-21.92), n 1 | 0.21% (-0.21), n 1 | 54.17% (-54.17), n 1 | 31.81% (-31.81), n 1 |
| B: card=aifoundry3 card 0 | 2 | 4.85% (-2.03), n 2 | 46.67% (-46.41), n 2 | 28.38% (-27.99), n 2 | 0.75% (-0.41), n 2 | 52.79% (-52.77), n 2 | 31.05% (-31.04), n 2 |
| B: fmt=fp32 | 3 | 4.43% (-0.20), n 3 | 44.52% (-44.23), n 3 | 26.40% (-25.97), n 3 | 0.62% (-0.34), n 3 | 53.25% (-53.23), n 3 | 31.30% (-31.30), n 3 |
| B: source=E206A | 2 | 4.85% (-2.03), n 2 | 46.67% (-46.41), n 2 | 28.38% (-27.99), n 2 | 0.75% (-0.41), n 2 | 52.79% (-52.77), n 2 | 31.05% (-31.04), n 2 |
| B: source=E206B | 1 | 3.45% (+3.45), n 1 | 39.87% (-39.87), n 1 | 21.92% (-21.92), n 1 | 0.21% (-0.21), n 1 | 54.17% (-54.17), n 1 | 31.81% (-31.81), n 1 |
| B: tabulated by an MM1-v3 design/spec lane | 2 | 2.96% (+2.91), n 2 | 40.68% (-40.67), n 2 | 22.62% (-22.61), n 2 | 0.22% (+0.00), n 2 | 54.15% (-54.15), n 2 | 31.71% (-31.71), n 2 |
| B: not tabulated by any MM1-v3 design/spec lane | 1 | 6.43% (-6.43), n 1 | 51.34% (-51.34), n 1 | 32.68% (-32.68), n 1 | 1.04% (-1.04), n 1 | 51.41% (-51.41), n 1 | 30.48% (-30.48), n 1 |
| C: all | 7 | 2.79% (+2.19), n 7 | 17.83% (-10.35), n 7 | 26.09% (+11.43), n 7 | 3.42% (+0.28), n 6 | 25.05% (-16.52), n 6 | 20.31% (+4.80), n 6 |
| C: card=aifoundry1 card 0 | 1 | 3.59% (+3.59), n 1 | 16.31% (-16.31), n 1 | 4.42% (-4.42), n 1 | - | - | - |
| C: card=aifoundry1 card 1 | 4 | 2.27% (+1.34), n 4 | 20.36% (-10.84), n 4 | 31.17% (+15.22), n 4 | 4.18% (+0.61), n 4 | 24.97% (-15.81), n 4 | 20.90% (+5.16), n 4 |
| C: card=aifoundry2 card 0 | 2 | 3.24% (+3.20), n 2 | 12.28% (-6.38), n 2 | 20.72% (+11.79), n 2 | 0.42% (-0.37), n 2 | 25.22% (-17.94), n 2 | 19.07% (+4.08), n 2 |
| C: fmt=fp32 | 3 | 3.06% (+1.88), n 3 | 6.01% (+5.36), n 3 | 38.46% (+37.39), n 3 | 0.97% (+0.18), n 3 | 4.17% (+2.02), n 3 | 24.54% (+24.34), n 3 |
| C: fmt=int8 | 4 | 2.57% (+2.43), n 4 | 23.01% (-22.13), n 4 | 9.04% (-8.03), n 4 | 4.74% (+0.39), n 3 | 35.19% (-35.07), n 3 | 14.92% (-14.74), n 3 |
| C: source=E212 | 7 | 2.79% (+2.19), n 7 | 17.83% (-10.35), n 7 | 26.09% (+11.43), n 7 | 3.42% (+0.28), n 6 | 25.05% (-16.52), n 6 | 20.31% (+4.80), n 6 |
| C: tabulated by an MM1-v3 design/spec lane | 5 | 2.59% (+1.79), n 5 | 19.62% (-11.94), n 5 | 27.95% (+11.29), n 5 | 4.18% (+0.61), n 4 | 24.97% (-15.81), n 4 | 20.90% (+5.16), n 4 |
| C: not tabulated by any MM1-v3 design/spec lane | 2 | 3.24% (+3.20), n 2 | 12.28% (-6.38), n 2 | 20.72% (+11.79), n 2 | 0.42% (-0.37), n 2 | 25.22% (-17.94), n 2 | 19.07% (+4.08), n 2 |

Per run (group A, 59): Q1 MM1-v3 7.20% (+2.97), n 59; Q2 6.26% (+2.98), n 46 (46 runs with a D).

Row "A: card=aifoundry2 card 0" is E212 a2c0-S2's 8 runs, the cleanest part (section 9.2). The "not tabulated" rows mean not tabulated by an MM1-v3 design or spec lane; seven of group A's 15 such cases were tabulated by MM1-v3's build lane and by mm-residuals, and so was group B's one (E206 arm A p110). Fifteen figures in this section and in sections 0 and 6 were printed from values already rounded to 3 decimals; they are re-printed from the unrounded values (section 9.4).

## 5. Every case (group A, then B, then C; errors in %, Q2 in % of D; the share s = (W - W_zeros) / D)

| group | case | runs | W over idle measured (W) | D (W) | s measured | s MM1-v3 | Q1 MM1-v3 | Q1 N | Q1 V1 | Q2 MM1-v3 | Q2 N |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| A | `aifoundry1 card 1|gemmL1x1x1|fp32|pattern:den4|0xffffffff` | 2 | 17.77 | 29.63 | 0.453 | 0.502 | +4.0 | -4.2 | - | +4.9 | +0.0 |
| A | `aifoundry1 card 1|gemmL1x1x1|fp32|pattern:pow2|0xffffffff` | 2 | 19.91 | 29.63 | 0.525 | 0.541 | -1.4 | -14.1 | - | +1.6 | -7.0 |
| A | `aifoundry1 card 1|gemmL1x1x1|fp32|pattern:den8|0xffffffff` | 2 | 20.03 | 29.63 | 0.529 | 0.580 | +3.9 | -14.5 | - | +5.1 | -7.3 |
| A | `aifoundry1 card 1|gemmL1x1x1|fp32|pattern:lanes2|0xffffffff` | 2 | 15.34 | 29.63 | 0.370 | 0.401 | +1.1 | +11.7 | - | +3.1 | +8.6 |
| A | `aifoundry1 card 1|gemmL1x1x1|fp32|pattern:fld_sign|0xffffffff` | 2 | 17.51 | 29.63 | 0.444 | 0.478 | +1.5 | -2.4 | - | +3.4 | +1.1 |
| A | `aifoundry1 card 1|gemmL1x1x1|fp32|pattern:den21|0xffff` | 2 | 13.49 | 13.85 | 0.816 | 0.816 | +4.3 | -36.5 | - | +0.0 | -39.8 |
| A | `aifoundry1 card 1|gemmL1x1x1|fp32|pattern:fld_mant|0xffff` | 2 | 14.05 | 13.85 | 0.857 | 0.911 | +9.5 | -39.2 | - | +5.4 | -44.0 |
| A | `aifoundry1 card 1|gemmL1x1x1|fp32|pattern:den16|0xffff` | 2 | 12.10 | 13.85 | 0.716 | 0.721 | +5.4 | -29.2 | - | +0.5 | -29.7 |
| A | `aifoundry1 card 1|gemmL1x1x1|int8|pattern:i8_den6|0xffffffff` | 2 | 7.89 | 11.36 | 0.299 | 0.266 | -11.8 | +13.2 | - | -3.4 | +13.9 |
| A | `aifoundry1 card 1|gemmL1x1x1|int8|pattern:i8_den3|0xffffffff` | 2 | 7.50 | 11.36 | 0.265 | 0.272 | -6.3 | +19.0 | - | +0.6 | +17.3 |
| A | `aifoundry1 card 1|gemmL1x1x1|int8|pattern:i8_pm1|0xffffffff` | 2 | 12.77 | 11.36 | 0.729 | 0.917 | +12.5 | -30.3 | - | +18.8 | -29.2 |
| A | `aifoundry1 card 1|gemmL1x1x1|int8|pattern:i8_den1|0xffffffff` | 2 | 7.08 | 11.36 | 0.228 | 0.270 | -1.0 | +26.1 | - | +4.1 | +21.0 |
| A | `aifoundry1 card 1|gemmL1x1x1|fp16|pattern:fld16_mant|0xffffffff` | 2 | 25.78 | 26.78 | 0.798 | 0.829 | +2.4 | -36.6 | - | +3.1 | -34.4 |
| A | `aifoundry1 card 1|gemmL1x1x1|fp16|pattern:den16_4|0xffffffff` | 2 | 18.96 | 26.78 | 0.543 | 0.681 | +18.4 | -13.6 | - | +13.9 | -8.8 |
| A | `aifoundry1 card 1|gemmL1x1x1|fp16|pattern:den16_10|0xffffffff` | 2 | 23.81 | 26.78 | 0.724 | 0.815 | +9.3 | -31.2 | - | +9.1 | -26.9 |
| A | `aifoundry1 card 1|gemmL1x1x1|fp16|pattern:fld16_sign|0xffffffff` | 2 | 17.81 | 26.78 | 0.500 | 0.590 | +12.3 | -8.1 | - | +9.0 | -4.5 |
| A | `aifoundry1 card 1|gemmL1x1x1|fp16|pattern:fld16_exp|0xffffffff` | 2 | 20.35 | 26.78 | 0.595 | 0.613 | +1.3 | -19.9 | - | +1.8 | -14.2 |
| A | `aifoundry1 card 1|gemmL4x8x8|fp32|pattern:fld_sign|0xffffffff` | 1 | 10.05 | 12.34 | 0.451 | 0.425 | +1.6 | +0.3 | - | -2.7 | -3.7 |
| A | `aifoundry1 card 1|gemmL4x8x8|fp32|pattern:den8|0xffffffff` | 1 | 11.23 | 12.34 | 0.546 | 0.535 | +3.2 | -10.1 | - | -1.1 | -13.1 |
| A | `aifoundry1 card 1|gemmL1x1x1|fp32|pattern:fp16grid|0xffff` | 1 | 12.61 | 13.71 | 0.753 | 0.753 | +4.8 | -32.1 | - | +0.1 | -33.9 |
| A | `aifoundry1 card 1|gemmL1x1x1|fp32|pattern:bf16trunc|0xffffffff` | 1 | 24.45 | 29.78 | 0.676 | 0.695 | -0.6 | -30.1 | - | +1.9 | -22.4 |
| A | `aifoundry2 card 0|gemmL4x8x8|fp32|pattern:fld_sign|0xffffffff` | 1 | 20.01 | 18.45 | 0.450 | 0.425 | +1.3 | -0.2 | - | -2.5 | -4.2 |
| A | `aifoundry2 card 0|gemmL4x8x8|fp32|pattern:lanes2|0xffffffff` | 1 | 18.86 | 18.45 | 0.388 | 0.350 | +0.1 | +6.2 | - | -3.8 | +2.3 |
| A | `aifoundry2 card 0|gemmL4x8x8|fp32|pattern:den4|0xffffffff` | 1 | 20.71 | 18.45 | 0.489 | 0.457 | +0.7 | -3.3 | - | -3.2 | -7.6 |
| A | `aifoundry2 card 0|gemmL4x8x8|fp32|pattern:den8|0xffffffff` | 1 | 22.05 | 18.45 | 0.561 | 0.542 | +1.7 | -9.0 | - | -1.9 | -14.7 |
| A | `aifoundry2 card 0|gemmL1x1x1|fp32|pattern:fld_sign|0xffffffff` | 1 | 39.27 | - | - | - | +0.2 | -3.0 | - | - | - |
| A | `aifoundry2 card 0|gemmL1x1x1|fp32|pattern:lanes2|0xffffffff` | 1 | 35.27 | - | - | - | -0.4 | +8.6 | - | - | - |
| A | `aifoundry2 card 0|gemmL1x1x1|fp32|pattern:lanes2|0xffff` | 1 | 20.45 | 26.24 | 0.383 | 0.345 | +1.3 | +9.1 | - | -3.8 | +2.3 |
| A | `aifoundry2 card 0|gemmL1x1x1|fp32|pattern:fld_sign|0xffff` | 1 | 22.28 | 26.24 | 0.453 | 0.428 | +2.7 | -0.1 | - | -2.5 | -4.9 |
| C | `aifoundry1 card 0|gemmL2x4x1|int8|pattern:sparse50i|0xffffffff` | 1 | 17.96 | - | - | - | +3.6 | -16.3 | - | - | - |
| C | `aifoundry1 card 1|gemmL1x1x1|int8|pattern:sparse50i|0xffffffff` | 1 | 13.04 | 11.45 | 0.750 | 0.814 | +1.3 | -31.9 | - | +6.4 | -31.3 |
| C | `aifoundry1 card 1|gemmL1x1x1|fp32|pattern:sparse50f|0xffffffff` | 1 | 15.74 | 29.78 | 0.384 | 0.399 | -1.5 | +9.1 | - | +1.5 | +7.2 |
| C | `aifoundry1 card 1|gemmL2x4x4|fp32|pattern:sparse50f|0xffffffff` | 1 | 11.56 | 15.76 | 0.437 | 0.432 | +3.4 | +2.8 | - | -0.4 | -0.9 |
| C | `aifoundry1 card 1|gemmL2x4x1|int8|pattern:sparse50i|0xffffffff` | 1 | 9.14 | 7.09 | 0.769 | 0.718 | +2.2 | -23.5 | - | -5.1 | -38.3 |
| C | `aifoundry2 card 0|gemmL2x4x1|int8|pattern:sparse50i|0xffffffff` | 1 | 19.23 | 10.57 | 0.731 | 0.729 | +2.6 | -16.9 | - | -0.2 | -35.7 |
| C | `aifoundry2 card 0|gemmL2x4x4|fp32|pattern:sparse50f|0xffffffff` | 1 | 22.32 | 24.05 | 0.416 | 0.410 | +3.8 | +4.1 | - | -0.6 | -0.2 |
| A | `E206A|p112` | 1 | 30.50 | - | - | - | -4.1 | -49.3 | -2.8 | - | - |
| A | `E206A|p113` | 1 | 22.75 | - | - | - | -2.2 | -44.8 | -6.8 | - | - |
| A | `E206A|p114` | 1 | 12.43 | 10.48 | 0.776 | 0.755 | -3.8 | -33.5 | +10.9 | -2.1 | -37.4 |
| A | `E206A|p115` | 1 | 8.54 | - | - | - | +14.8 | -23.9 | +2.6 | - | - |
| A | `E206B|p113` | 1 | 23.47 | - | - | - | -1.1 | -43.3 | - | - | - |
| A | `E206B|p114` | 1 | 13.28 | 11.01 | 0.789 | 0.753 | -4.2 | -32.7 | - | -3.6 | -38.0 |
| A | `E206B|p115` | 1 | 9.25 | - | - | - | +13.5 | -23.0 | - | - | - |
| A | `E207|b42` | 1 | 14.40 | - | - | - | -6.4 | -10.0 | -6.3 | - | - |
| A | `E207|b43` | 1 | 11.31 | - | - | - | -0.1 | -3.6 | +1.9 | - | - |
| A | `E207|b49` | 1 | 18.59 | - | - | - | -2.6 | -30.5 | -5.3 | - | - |
| A | `E207|b50` | 1 | 21.61 | - | - | - | -0.0 | -41.8 | -6.0 | - | - |
| A | `E207|b51` | 1 | 8.97 | - | - | - | +15.4 | -27.7 | +4.3 | - | - |
| A | `E207|b52` | 1 | 17.06 | - | - | - | +8.5 | -36.1 | +7.2 | - | - |
| B | `E206A|p110` | 1 | 33.41 | 29.78 | 0.984 | 0.974 | -6.4 | -51.3 | -3.0 | -1.0 | -51.4 |
| B | `E206A|p111` | 1 | 19.38 | 15.63 | 0.969 | 0.971 | +2.4 | -41.5 | +1.0 | +0.2 | -54.1 |
| B | `E206B|p111` | 1 | 20.07 | 16.11 | 0.964 | 0.962 | +3.5 | -39.9 | - | -0.2 | -54.2 |

The per-run table, with every condition and every model, is `scores-unread-runs.csv`.

## 6. The pass rule, and the reported variants

| test | Q1: MM1-v3 / other rms, closer, p | Q2: MM1-v3 / other rms, closer, p | verdict |
|---|---|---|---|
| **declared: group A against N** | 6.83 / 24.97%, 35 of 40, p 1.4e-06 | 5.70 / 21.64%, 23 of 29, p 0.0023 | PASS |
| REPORTED: group A against N2 | 6.83 / 25.67%, 35 of 40, p 1.4e-06 | 5.70 / 19.96%, 25 of 27, p 5.6e-06 | PASS |
| REPORTED: against V1 where it applies (aifoundry3) | 7.82 / 5.98%, 5 of 9, p 1 | 2.11 / 10.87%, 1 of 1, p 1 | NOT DECIDED |
| REPORTED: E212 alone against N | 6.28 / 20.09%, 22 of 27, p 0.0015 | 5.85 / 19.94%, 21 of 27, p 0.0059 | PASS |
| REPORTED: E206/E207 alone against N | 7.91 / 33.36%, 13 of 13, p 0.00024 | 2.96 / 37.71%, 2 of 2, p 0.5 | NOT DECIDED |
| REPORTED, post hoc (addendum 1, section 9.1): group A with E209's e35 and e36, against N | 6.71 / 25.10%, 37 of 42, p 4.4e-07 | unchanged (no E209 point has a share of D) | P1 and P2 hold |

## 7. What this cannot say

- **It is not blind.** The model's constants and the counts never saw these runs' energy. But one of MM1-v3's design lanes had printed 14 of the 46 E212 runs' shares of D, and its spec lane had tabulated 38 of them before MM1-v3's form was chosen. The 15 cases no MM1-v3 design or spec lane tabulated are given apart (section 4); seven of them were tabulated by MM1-v3's build lane and by mm-residuals, so the cleanest part is E212 a2c0-S2's 8 runs (section 9.2).
- **Known configurations:** every case's configuration is in MM1-v3's energy fit with other kinds, and only the kind is new. Their time is in MM1-v3's time fit (time is kind-blind), and Q1 and Q2 use the measured time.
- **Energy through the count, not the count:** no card counts switches. fp16's count is an RTL estimate, int8's leaves out the arithmetic, and both are at launch points, not GEMM states. The fp16 bias (+7.4% of D) and `i8_pm1` (+18.8% of D) are where the count and the card part.
- **Narrow shapes:** E212's patterns ran at `gemmL1x1x1` (32 and 16 shires) and `gemmL4x8x8` on two cards; fp16 and int8 on card 1 only. Q2 for E206/E207 rests on 2 points.
- **phi is a desk rule,** never checked on a card's line order; with phi = 1 the group A Q1 error rises from 6.83% to 8.29%.

## 8. Files and how to reproduce

- `DECLARED-unread.md`, `declared-unread.json`: the declaration (step 1). `inputs/runs-listed.json` holds the runs from schedules, queues and point files; `inputs/phi-declared.json` holds phi from tile bytes; `inputs/earlier-lanes.json` holds the search for earlier reads (one entry, a scratch script's file name, is left out of this public copy: section 9.5). `DECLARED-unread.md.dated-note-1.md` holds the post hoc corrections to the declaration (section 9).
- `forecasts-unread.csv`, `forecasts-unread.json`: the forecasts (step 2), 133 rows (69 test entries and 64 references), every model's frozen coefficients.
- `scores-unread.json`, `scores-unread-runs.csv`, `scores-unread-cases.csv`: the score (step 3).
- `scripts/`: `s00_setup.sh` (work copies), `s01_list.py`, `s01g_search.py`, `s01h_context.py`, `s01p_phi.py`, `s01d_declare.py`, `s01m_md.py` (step 1), `s02_forecast.py` (step 2), `s03_score.py` (step 3), `s04_recheck.py` (step 4) and `s05_land.py` (this folder). `logs/` holds the lane's log and the scorer's output. The fix lane's scripts are in `scripts/fix/` and its logs in `logs/fix/`; addendum 1's declaration, forecasts and scores are in `addendum-1-e209/`.
- To reproduce, from a checkout of GitHub main 8e91dda6 (or any commit where `tools/matmul/mm1/v3` is b1493082's) and the counts folder: put MM1-v3, MM1-v1 and E212's registration under `work/lab/` and the counts under `work/counts/`, then run steps 1-4 in order. Each runs single-threaded (`OMP_NUM_THREADS=1` and the like), with `/usr/bin/python3` 3.12.3 `-I -B` and numpy 1.26.4.
- The fix lane's steps, in order (each script asserts the hashes of the files before it): `scripts/fix/f00_setup.sh` (work copies by `git archive` of GitHub main 3e8991d0 and the counts' checks), `f01_rerun.py` (the unread lane's `s03_score.py` re-run unchanged, and the unrounded figures), `a01_declare_e209.py`, `a02_forecast_e209.py` and `a03_score_e209.py` (addendum 1: declared, forecast, then read and scored), `f02_readme.py` (this README) and `f03_land.py` (this folder); each Python step ran inside the round's CPU slot (`slotpy.sh`), single-threaded.

**The scripts' sha256 as run** (before the path replacement):

| script | sha256 as run |
|---|---|
| `s00_setup.sh` | `d14d16b086e8671b388a68b7ae5c8b5896ecc1cde0efad91aadeb388216b711f` |
| `s01_list.py` | `bd1fd36cedc8cfbe45834cfc5a5379d993f46685f2b2a90cb5ce53d86533e48e` |
| `s01d_declare.py` | `536c0b3eefb7c7cfb3c6d5c6150f2d288c971274045e42d7531f3d2494aea37d` |
| `s01g_search.py` | `2f0ba037cb693883d5c7ef0a0d7783eeb3f4866c782b66a8145f87a5a5b248ee` |
| `s01h_context.py` | `a95663142029e981944b3232e8f4faacb750896649b2edd279cdddcc4e769cfc` |
| `s01m_md.py` | `f456ed83cad569f3f8405b207391eb37cd7d12767acd3e8c22b2ec4fb67876b9` |
| `s01p_phi.py` | `1b465ec67cc5a4025120a0a5adafd35a80676a2777b81c42a3610c284c15a0bc` |
| `s02_forecast.py` | `c8166622189cd9d986a19e6ba4bfe54617f56860c62a613db5dd1dd3f09747ff` |
| `s03_score.py` | `74df0a0688179a22c2f65c5567a7989eed0f6940abff6ba308aab176bdb743ab` |
| `s04_recheck.py` | `5e66d69f1064e5abcb9c52550cc194746281488e6b5ece72c638b8f1f954beb1` |
| `s05_land.py` | `09b168cdeddcc3337ce1e87b7f845948b08529c13d5b906f3e6849bace3ff368` |

## 9. After the verify: what changed, and why (fix-unread-e212sw, Wed 18 Nov 2026, from 07:35 PST; post hoc)

verify-unread-e212sw (07:04-07:35 PST) found that the score re-derives exactly, the order holds and the declared rule gives PASS (HOLDS WITH FIXES), with eight findings. **Unchanged:** `DECLARED-unread.md` (f1daf832...), `declared-unread.json` (5eb2c93d...), the forecasts (2c26f013..., 8938bbeb...), the scores (a535d78c..., 892628bb..., 78cfa3fb...) and every script as run. The frozen scorer, re-run unchanged at 07:44:06 PST from a fresh copy of its inputs (`scripts/fix/f01_rerun.py`), gives byte-equal CSVs and an equal JSON apart from its two clock stamps. The post hoc corrections to the declaration are in `DECLARED-unread.md.dated-note-1.md`.

### 9.1 Addendum 1, post hoc: E209's three real points (finding 1)

- **What section a missed.** By its own rule, the declared list missed three E209 points on aifoundry2 card 0 under its governor. They ran with E206's real2 tiles, byte-equal to the files rule e and the counts read. e35 (int8) and e36 (fp16) have no count in MM1-v3 as landed and have one in the frozen counts, so they belong in group A. e34 (fp32) has its count but no phi, so it belongs in group B. They were missed because the brief named only E212, E206 and E207, and the counts lane's list scanned only energy points and E212 runs.
- **How they were scored.** The same rules and the same order, each step hashed before the next:
  1. the addendum's declaration at 07:47:44 PST (`addendum-1-e209/addendum-declared-e209.json`, 5f9e7f219104afa78f8d2ba89bfe1c5ca4af0e2295ac1c9be858d9321c3531bb);
  2. its forecasts at 07:53:34 PST (`forecasts-e209-posthoc.json`, 18438c3f82d0c0859542403135b371fb9736613fdb262bae0d53951eb7139b65), by the unread lane's step-2 machinery unchanged, which re-made four frozen entries bit for bit;
  3. the first read of E209's data file by this lane, and the score, at 07:55:15 PST (`scores-e209-posthoc.json`).
- **Only Q1 can be scored.** E209 has no zeros point at these configurations (random only: e01, e18, e19), so the share of D is NOT SCORED.
- **The figures equal the verifier's** own post hoc numbers to 2.2e-16.

| point | group | format, shape | runs | clock (MHz) | W over idle measured (W) | Q1 MM1-v3 | Q1 N | Q1 N2 | J at rest given t | J over idle, t forecast |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| e35 | A | int8 `gemmL1x3x2` | 1 | 799.1 | 20.27 | -0.01% | -23.13% | -12.69% | -0.01% | -0.76% |
| e36 | A | fp16 `gemmL3x5x5` | 1 | 799.0 | 31.88 | +4.75% | -31.74% | -16.18% | +2.82% | +5.09% |
| e34 | B | fp32 `gemmL2x6x10` | 2 | 799.1 | 31.25 | +2.18% | -33.12% | -18.47% | +1.27% | +3.34% |

- **Group A, Q1, with e35 and e36 added** (44 cases): MM1-v3 6.71% rms (+2.60) against N's 25.10% (-16.55). MM1-v3 is closer on 37 of 42 non-tied cases (2 ties), p = 4.4e-07. Against N2 the null reads 25.27%.
  - P1 and P2 hold. Q2's 29 cases are unchanged, so P3 and P4 are as declared.
  - The pass rule would still read PASS. **The verdict of record is the declared one.**
- **Group B with e34 added** (4 points): MM1-v3 3.99% (+0.39) against N's 41.96%. **E209's three alone:** MM1-v3 3.02%, N 29.66%, N2 15.96%.
- **Label: post hoc and UNREAD, not blind.** MM1-v3 and the counts were frozen before any lane read these runs for this test. These lanes had read them earlier:
  - E209's own lanes: card-e209 (the session and its checks), collect-e209 (the collection and the step-13 scorer, joules per point against the frozen MM1 forecasts), verify-e209d, fix-e209d and scores-e209;
  - MM1-v3's design lane v3-design-a, which tabulated MM1-v2's J-over-idle error at all 45 E209 points (these three included);
  - this round's verifier, which scored them first.

### 9.2 Earlier reads, corrected (findings 2, 3, 5, 6)

- **mm-residuals**, under E206 arms A and B as well as E207. Its committed table `tools/matmul/mm1/residuals/residuals-2026-11-17.csv` (a514caf0) holds the measured W over idle of E206 arm A's p110-p115 and arm B's p111 and p113-p115. v3-design-a's `diag_terms.py` and `diag2_groups.py` read it before MM1-v3's freeze.
- **mm-data is withdrawn** from section g's E206 arm A line. Its 43 files date from 09:54-10:31 PST Mon 16 Nov, about eight hours before E206 arm A's data commit d7e4f35e (18:26:14 PST). Its search hit was the token `e37`, the older experiment E37's kind name.
- **The cleanest part.** Of the 15 cases no MM1-v3 design or spec lane tabulated, E206 p112 and E207's six have their measured W in MM1-v3's committed `out/points_energy_v3.csv` (written by its build lane before the freeze) and in mm-residuals' table. Only E212 a2c0-S2's 8 runs were tabulated in energy by no MM1-v3 lane: MM1-v3's `out/unread_v2_e212_runs.csv` holds them for time only, every energy column empty, and mm-residuals predates them. There MM1-v3 reads Q1 1.34% (+0.96), n 8, and Q2 3.04% of D (-2.95), n 6 (null N: 6.07% and 7.37%). The declaration's own words already named this split; section 0 now does too.
- **Seen before the declaration:** E210.md's quote of E206's S1 D (29.78 W) and a1c1-S2's session rest values (29.91 W, 51 C) (section 2).

### 9.3 The counts, by their commit (finding 4)

The counts used here are committed unchanged as `tools/matmul/mm1/v3.1/counts/` in 3e8991d0 (07:23:56 PST Wed 18 Nov 2026); `SHA256SUMS` c74c2d49c336159f6ca63aad2652601a10e22d6a8b5db00d46c66bfb1cf8aa7f; `diff -r` against the land dir the test used: no difference. This folder's files are all new on GitHub main: no file under its path at 3e8991d0 (07:42:02 PST), nor at d8404ef2 (08:03:03 PST), the commit after it.

### 9.4 Figures re-printed from unrounded values (finding 7)

The unread lane printed every rms and mean from values already rounded to 3 decimals. Where the third decimal was a 5, the second could come out one step off. The unchanged scorer's unrounded values (`logs/fix/rerun-full.json`) give these 15 corrections; no other printed figure differs.

| where | printed | unrounded | now |
|---|---|---|---|
| section 0 (Q1 line), section 4 (A: all), section 6 (declared row): N's Q1 rms | 24.96% | 24.965160 | 24.97% |
| section 0 (REPORTED), section 4 (A: card=aifoundry3 card 0), section 6 (V1 row): MM1-v3's Q1 rms on aifoundry3 | 7.83% | 7.824510 | 7.82% |
| section 4, per run, group A: MM1-v3's Q1 mean (the verifier's finding 7) | +2.96 | 2.965008 | +2.97 |
| section 4, A: card=aifoundry1 card 1, Q2 N2 rms | 20.12% | 20.125127 | 20.13% |
| section 4, A: fmt=fp16, Q1 N2 rms | 21.20% | 21.205179 | 21.21% |
| section 4, A: source=E206A, Q1 N2 mean | -19.93 | -19.935247 | -19.94 |
| section 4, B: card=aifoundry3 card 0 and B: source=E206A, Q2 N rms | 52.78% | 52.785373 | 52.79% |
| section 4, C: card=aifoundry1 card 1, Q1 N mean | -10.85 | -10.844982 | -10.84 |
| section 4, C: card=aifoundry2 card 0 and C: not tabulated, Q1 MM1-v3 mean | +3.19 | 3.195480 | +3.20 |

### 9.5 The public copy of `inputs/earlier-lanes.json` (finding 8)

One entry is left out of the public copy: lane data-e212's scratch script, matched on the token `sparse50f`. Only its file name was listed, never its content. The file as run in step 1 is sha256 f20b2fb67bcb5c111b9a899cdb423c60dc3047ef3f324af001ddb3d3d92e1e60 (in `logs/step1-sha256.txt`), and `SHA256SUMS` gives the public copy's. The declaration's section g, its counts and its search totals are unchanged by it.

### 9.6 This README

It replaces the unread lane's README (sha256 7f0ca663d9b27d7df1dd38c9988331df7fadd27940e9b0a30bdfc272d14c0a38). `scripts/fix/f02_readme.py` makes it from that README by exact, counted replacements. They change:

- the label paragraph: the counts' commit, the lanes that had read the runs, and a pointer to this section;
- section 0: N's Q1 figure, MM1-v3's figure against MM1-v1, the cleanest-part bullet and the addendum's line;
- section 2: two lines, the numbers seen before the declaration and the counts' commit;
- section 4: the re-printed figures and the note under the table;
- section 6: two figures and the addendum's row;
- section 7: the wording on the cleanest part;
- section 8: the new files and the fix lane's steps;
- this section, which is new.

**The fix lane's scripts as run** (`scripts/fix/`, before the path replacement; `f02_readme.py` and `f03_land.py` as in their final run):

| script | sha256 as run |
|---|---|
| `slotpy.sh` | `861345252fd35948053086f891b312cb79e9266de5c232043bea8fb7a1ecd8bc` |
| `f00_setup.sh` | `bc6fcf1d4f0761545e9ffad1460cd2396f0b4943675bfc42dbda0854d344afa6` |
| `f01_rerun.py` | `a8606c83b45280f81d9ecb7449532b742dfb2ed3242a17ba47b668b82d217fb7` |
| `a01_declare_e209.py` | `9f2514e7e2a2c3634ee09ab5312cc185e3d8b4c4e524450da1189f3e44b274b5` |
| `a02_forecast_e209.py` | `1ea00f51cd2c2f1609ae503f7b86cd5ea7257c3fda9050dafb5e9c8d7fd73d6c` |
| `a03_score_e209.py` | `36c60bcba186161c3bfca6b3432a0f8be53e09b74b489bd0c0a9bcf3741cbbf0` |
| `f02_readme.py` | `eac147b65525ea29ba334b8724ce4bb165801337c87c742cb84265f4742965e1` |
| `f03_land.py` | `48636167a3ae394b863df87bbc22c9ae2bb7c4c0d55fdc9593b808b12b96a9d4` |
