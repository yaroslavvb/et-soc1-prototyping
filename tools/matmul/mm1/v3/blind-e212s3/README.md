# MM1-v3 scored BLIND on E212 aifoundry2 card 0 S3, the re-run of Wed 18 Nov 2026 (round Q223, lane blind-v3-e212s3)

**BLIND, and REPORTED: no pass rule is registered for S3.**

- **Frozen:** MM1-v3's forecasts for this session (`out/mm1_v3_e212_s3s4.csv`, sha256 `00222665...`) were frozen in b1493082, pushed at
  20:52:51 PST on Tue 17 Nov 2026.
- **Declared:** this scoring (`DECLARED-blind-s3.md` `23d9cdd6...`, `.json` `f6603956...`, scorer `45803a24...`) was hashed into the
  lane's log at 14:10:50 PST on Wed 18 Nov.
- **Run:** the re-run's first card command came at 16:00:08 PST. The model session ran S3 with its registered schedule unchanged, 55 of
  55 runs.
- **Read:** the lab committed the data in 321f992c at 16:31:02 PST. They were read here only after that, at 16:31:31.

The model session asked for the re-run with the owner's word: "Run E212's aifoundry2 S3 again, given that we know what caused the
crash." (#11.13, 12:23:29 PST Wed 18 Nov).

**On all 46 cases** (51 runs; 37 cases with energy), each model was called at the run's measured kernel clock, minion volts and die at
start (MM1-v3's README section 5 form). MM1-v3 against MM1-v2, both as frozen:

| quantity | MM1-v3 | MM1-v2 |
|---|---|---|
| wall cycles | **2.70% (-0.06)** | 4.33% (-2.84) |
| counter mean | 5.35% | 6.45% |
| W over idle given the measured seconds | **3.55% (-2.11)** | 5.65% (+3.13) |
| J over idle with the seconds forecast | 4.22% | 5.77% |
| J at rest given t | 1.31% | 2.24% |
| J at rest with t forecast | 3.11% | 4.19% |

Per case, MM1-v3 is closer than MM1-v2 on 26 cases in cycles, farther on 4, with 16 ties. In W it is closer on 19 and farther on 11, with
7 ties.

**S3 is a weak test of time**, as MM1-v3's README warned: 29 of the 46 cases repeat a configuration in its fit data.

- **Repeated configurations (29 cases):** MM1-v3's wall cycles read 1.07%, against MM1-v2's 2.07%.
- **New configurations (17 cases):** MM1-v3 reads **4.21% (+0.67)**, against MM1-v2's 6.58% (-5.42). v2form, MM1-v2's form refitted on
  MM1-v3's data and shown beside, reads 4.08%.
- **Energy (21 cases whose configuration and kind are new):** W given t reads 4.01% (-2.67) for MM1-v3 and 5.50% (+3.52) for MM1-v2. Per
  case MM1-v2 is closer on 10 of them and MM1-v3 on 9, with 2 ties.
- **MM1-v3's own estimates:** these blind figures sit inside its held-out ones. Its cycles LOEO is 4.53%, or 5.04% without configuration
  twins, and its energy LOEO is 4.85%.

**Largest misses (post hoc reading).** MM1-v3's three largest time misses are the spread-mask 2x4x16 fp32 zeros cases: 0x33333333 at
+9.68%, 0x1111 at +9.40% and 0x11111111 at +9.13%. On all three MM1-v2 is closer. MM1-v3's README names spread masks as its known gap:
held out at 6.74%, with no subset-layout model. On the contiguous subsets, MM1-v3 is far closer: s4 reads -0.23% against MM1-v2's
-12.76%, and s8 reads -1.67% against -12.34%.

**The literal frozen numbers.** At 799 MHz given, they score the same in cycles (2.70%), and 3.25% (+1.28) in W given t. They differ from
the section 5 call in two ways. The CSV used the model's default minion volts and die at start where the section 5 call takes the run's
measured ones. Its clock is also a fraction of a MHz different (799.0 given against 798.9-799.2 measured).

## 0. The order of the hashes and the times (Pacific)

| when (PST) | what | sha256 |
|---|---|---|
| Tue 17 Nov 20:52:46 (committed), 20:52:51 (pushed) | MM1-v3 landed as b1493082: the predictor, its constants and the forecast file `tools/matmul/mm1/v3/out/mm1_v3_e212_s3s4.csv` (46 a2c0-S3 rows, 799 MHz given); the land lane read GitHub main = b1493082 at 20:52:52 | forecast file `002226651404b291739894cc187d528e68b741d4e4df8b8d53d37172f4933faf`; MM1-v3 `SHA256SUMS` `c24efc149110d0cb3d1c8603f0bb7ee83db85eebf9af7ba4254d267c7c85dc74` |
| Wed 18 Nov 14:02:26-27 | work copies by `git archive` of b1493082 (MM1-v3, MM1-v2) and of main fcbf60c4 (E212's registration): MM1-v3 sums 170/170, MM1-v2 114/114, registration 87/87; the registered schedule = MM1-v3's copy | schedule `ea72bc7b908bc5ce8568ff01eca23371f88e13b0512ebbc3d370ef1a33937c95` |
| Wed 18 Nov 14:07:15-22 | the scorer `scripts/s03_score.py` written and desk-tested on E212 a2c0-S4 (reproduces MM1-v3's README section 5): `test-s4/` runs, cases, json | scorer `45803a24eb73e20816467aaa672bb742909f14d1d6f5e18ec294f95b638112c6`; test outputs `79ad071d...`, `051f12fb...`, `e83d8d2b...` |
| Wed 18 Nov 14:08:09 | the arms against the forecasts and the twin flags at 800 MHz: `s3-arms-twins.json` | `b8919725102dd01c00978b684577fe61beb39fb8c11f04929d6344cae6d4d30a` |
| Wed 18 Nov 14:10:50 (logged) | **the declaration**: `DECLARED-blind-s3.md` and `DECLARED-blind-s3.json` | md `23d9cdd6ce8b94f4aea5ff198a9039e934f11256a43f25514bc9c7303e3d8792`; json `f6603956e9cd3ea97cf0c3cb6fe4c6c0002f9abea1c94aec7c471d22d629f42a` |
| Wed 18 Nov 15:46:14 | the model session's claim of aifoundry2 card 0 for the re-run, 16:00-17:07 (#11.14; schedule unchanged) |  |
| Wed 18 Nov 16:00:05 / 16:00:08 | the re-run's session start (T0) / **its first card command** (the configuration read), from the committed session log |  |
| Wed 18 Nov 16:23:09 / 16:23:38 | the session's end (55 of 55 runs, 23.02 card-minutes) / the release (#11.14.1) |  |
| Wed 18 Nov 16:31:02 | **the data commit** 321f992c924aaebc7b8cabe2aa3f2ea7fbd7455d (`docs/reports/data/2026-11-18-e212-mmsweep2-a2c0-S3/`), on GitHub main by ls-remote at 16:31:17 | data file `9bc0c2f8cb779846f894578c7f64713250f88a20305ec8b62c7a81ba0ec2678e`; folder `SHA256SUMS` `44cec501ac37af3b809bed62c91f95e3ade4ef6e0ad0687a8dd46e23e8cde1c6` (216/216) |
| Wed 18 Nov 16:31:31 | the data read (archive of main 321f992c) and the order check: `order-s3.json`, label BLIND | `26b0341a8baf7104871c1e48491973beef6e5f3766b64559f96a96c06d40ee6d` |
| Wed 18 Nov 16:31:31-32 | **the score**, by the declared scorer unchanged: `blind_v3_e212s3_runs.csv`, `blind_v3_e212s3_cases.csv`, `blind_v3_e212s3.json` | `30e619486a3bab6d2cf966290197f7eb2fd37cbeda08d62b6fa11692636728f8`, `0e756b3509d09478f0fb221ccc1d5c5b1ad34ab2f2893cac2eb31ae8e7d7082d`, `395a0a2075b3cf0529e460723712685cb3f64d355abed2fc46b9b159dd645a74` |

The order check (`order-s3.json`): b1493082's push before the re-run's first card command **True**; the declaration's logged time before it **True**; both before the session start (T0) **True** / **True**; no session-log line older than b1493082's push **True**. Label: **BLIND**.

## 1. The scores (BLIND; REPORTED: no pass rule is registered for S3)

Each model called at the run's measured kernel clock, minion volts and die at start (MM1-v3's README section 5 form). Error = forecast / measured - 1; rms in %, the signed mean in brackets; W over idle and J over idle scored at 3 W and above.

| E212 a2c0-S3, BLIND | MM1-v3 (frozen, b1493082) | MM1-v2 (frozen, 3ca4b717) | v2form (refitted, all data; beside) |
|---|---|---|---|
| wall cycles, 46 cases | **2.70% (-0.06)** | 4.33% (-2.84) | 3.02% (-0.47) |
| counter mean, 46 cases | **5.35% (+0.21)** | 6.45% (-2.54) | - |
| W over idle given t, 37 cases | **3.55% (-2.11)** | 5.65% (+3.13) | 5.25% (+2.11) |
| J over idle with t forecast, 37 cases | **4.22% (-1.87)** | 5.77% (+0.82) | 6.15% (+2.09) |
| J at rest given t, 37 cases | 1.31% (-0.74) | 2.24% (+1.23) | - |
| J at rest with t forecast, 37 cases | 3.11% (-0.57) | 4.19% (-1.63) | - |
| per run (51 runs; 42 with energy): wall / counter mean / W given t / J at rest given t / J at rest t forecast | 2.56% (-0.07) / 5.09% (+0.07) / 3.41% (-2.03) / 1.27% (-0.72) / 2.94% (-0.60) | 4.19% (-2.83) / 6.24% (-2.66) / 5.94% (+3.67) / 2.43% (+1.50) / 3.96% (-1.27) | - |
| per case, closer to measured (ties within 0.5% in cycles, 1% in W) | v3 26, v2 4, ties 16 (cycles); v3 19, v2 11, ties 7 (W) | | |

MM1-v3's predictor equals its fit code on every case (op time max relative difference 0.0e+00; W 7.1e-15 W).

**Configuration twins** (MM1-v3's postcheck rule, against its all-data fit set; clock to 25 MHz at the case's measured clock):

| split | cases | MM1-v3 | MM1-v2 | v2form | closer v3 / v2 / ties |
|---|---|---|---|---|---|
| wall cycles, in the fit data | 29 | 1.07% (-0.48) | 2.07% (-1.33) | 2.18% (-0.87) | 12 / 1 / 16 |
| wall cycles, new | 17 | 4.21% (+0.67) | 6.58% (-5.42) | 4.08% (+0.21) | 14 / 3 / 0 |
| W given t (time configuration), in the fit data | 20 | 3.00% (-1.65) | 5.76% (+2.73) | 5.40% (+2.21) | 12 / 3 / 5 |
| W given t (time configuration), new | 17 | 4.10% (-2.67) | 5.52% (+3.61) | 5.08% (+2.00) | 7 / 8 / 2 |
| W given t (configuration and kind), in the fit data | 16 | 2.83% (-1.38) | 5.84% (+2.62) | 5.51% (+1.94) | 10 / 1 / 5 |
| W given t (configuration and kind), new | 21 | 4.01% (-2.67) | 5.50% (+3.52) | 5.05% (+2.24) | 9 / 10 / 2 |

**The literal frozen numbers** of `out/mm1_v3_e212_s3s4.csv` (799 MHz given), against the same cases:

| literal, 799 MHz given | MM1-v3 | MM1-v2 |
|---|---|---|
| wall cycles, 46 cases | 2.70% (-0.06) | 4.33% (-2.85) |
| counter mean, 46 cases | 5.34% (+0.21) | 6.45% (-2.55) |
| W given t (the CSV's A + B / t_meas), 37 cases | 3.25% (+1.28) | 5.53% (+2.96) |

**Coverage:** 46 of the 46 declared arms have a scored case (46 cases, 51 runs scored; 37 cases with energy). Arms with no scored run (NOT RUN or left out by the loader): none. Scored labels outside the declared arms: none. Cases without a literal frozen row: none.

**Every case** (errors in %; twin = time configuration in the fit data):

| case | kind | mask | runs | MHz | twin | measured cycles | v3 cycles | v2 cycles | v3 W given t | v2 W given t |
|---|---|---|---|---|---|---|---|---|---|---|
| 1x16x4-fp32-zeros-m77777777 | zeros | 0x77777777 | 1 | 799.2 | no | 1648.9 | -0.67 | -5.31 | -1.95 | +2.27 |
| 1x16x4-fp32-zeros-s24 | zeros | 0xffffff | 1 | 799.2 | no | 1653.2 | -0.93 | -5.56 | -5.02 | -0.47 |
| 1x16x4-fp32-zeros | zeros | 0xffffffff | 1 | 799.0 | yes | 1701.3 | -1.99 | -4.68 | -2.65 | +2.06 |
| 1x1x16-fp32-zeros-m77777777 | zeros | 0x77777777 | 1 | 799.1 | no | 1735.9 | +0.38 | -2.74 | +3.66 | +10.61 |
| 1x1x16-fp32-zeros-s24 | zeros | 0xffffff | 1 | 799.2 | no | 1729.6 | +0.76 | -2.37 | -1.84 | +4.73 |
| 1x1x16-fp32-zeros | zeros | 0xffffffff | 1 | 799.1 | yes | 1740.6 | +2.20 | +1.90 | -0.59 | +5.80 |
| 1x1x16-int8-ones | ones | 0xffffffff | 1 | 799.1 | yes | 1790.7 | -0.66 | -0.95 | -0.53 | +7.25 |
| 1x1x16-int8-rnd-m33333333 | random | 0x33333333 | 1 | 799.1 | no | 1753.2 | -2.68 | -8.57 | +3.40 | +12.33 |
| 1x1x16-int8-rnd-m77777777 | random | 0x77777777 | 1 | 799.2 | no | 1768.3 | -1.45 | -4.51 | -6.34 | +2.40 |
| 1x1x16-int8-rnd-s16 | random | 0xffff | 1 | 799.1 | no | 1760.2 | -3.07 | -8.93 | +0.59 | +9.29 |
| 1x1x16-int8-rnd-s24 | random | 0xffffff | 1 | 799.1 | no | 1770.6 | -1.58 | -4.64 | -1.04 | +8.20 |
| 1x1x16-int8-rnd | random | 0xffffffff | 1 | 799.0 | yes | 1793.9 | -0.84 | -1.13 | +0.37 | +9.68 |
| 1x1x16-int8-zeros | zeros | 0xffffffff | 1 | 799.2 | yes | 1795.2 | -0.90 | -1.18 | -0.17 | +7.83 |
| 1x1x1-fp16-ones | ones | 0xffffffff | 1 | 799.1 | yes | 542.7 | -0.22 | -0.22 | -2.25 | -1.27 |
| 1x1x1-fp16-fld16_sign | pattern:fld16_sign | 0xffffffff | 1 | 799.0 | yes | 542.9 | -0.24 | -0.24 | - | - |
| 1x1x1-fp16-zeros | zeros | 0xffffffff | 1 | 799.1 | yes | 542.8 | -0.23 | -0.23 | -4.93 | -6.66 |
| 1x1x1-fp32-ones-s16 | ones | 0xffff | 1 | 799.0 | yes | 541.7 | -0.03 | -0.03 | +0.33 | +1.67 |
| 1x1x1-fp32-ones | ones | 0xffffffff | 1 | 798.9 | yes | 542.8 | -0.23 | -0.23 | -1.37 | -0.20 |
| 1x1x1-fp32-fld_sign-s16 | pattern:fld_sign | 0xffff | 1 | 799.0 | yes | 541.8 | -0.06 | -0.06 | - | - |
| 1x1x1-fp32-fld_sign | pattern:fld_sign | 0xffffffff | 1 | 798.9 | yes | 542.8 | -0.23 | -0.23 | - | - |
| 1x1x1-fp32-lanes2-s16 | pattern:lanes2 | 0xffff | 1 | 799.0 | yes | 541.9 | -0.07 | -0.07 | - | - |
| 1x1x1-fp32-lanes2 | pattern:lanes2 | 0xffffffff | 1 | 799.0 | yes | 542.8 | -0.23 | -0.23 | - | - |
| 1x1x1-fp32-rnd-s16 | random | 0xffff | 1 | 799.0 | yes | 541.9 | -0.06 | -0.06 | +2.85 | +3.48 |
| 1x1x1-fp32-zeros-s16 | zeros | 0xffff | 1 | 799.0 | yes | 541.8 | -0.05 | -0.05 | -4.75 | -4.60 |
| 1x1x1-fp32-zeros | zeros | 0xffffffff | 1 | 799.0 | yes | 542.9 | -0.24 | -0.24 | -5.18 | -6.53 |
| 1x1x8-int8-ones | ones | 0xffffffff | 1 | 799.1 | yes | 1140.1 | -1.36 | -3.35 | -4.40 | -0.56 |
| 1x1x8-int8-rnd | random | 0xffffffff | 1 | 799.1 | yes | 1135.3 | -0.95 | -2.95 | -3.56 | +2.59 |
| 1x1x8-int8-zeros | zeros | 0xffffffff | 1 | 799.1 | yes | 1145.0 | -1.79 | -3.77 | -5.72 | -1.99 |
| 2x2x4-int8-ones | ones | 0xffffffff | 1 | 799.1 | no | 1136.3 | -0.78 | -2.66 | -2.98 | +0.26 |
| 2x2x4-int8-rnd | random | 0xffffffff | 1 | 799.1 | no | 1140.9 | -1.18 | -3.06 | -3.19 | +2.17 |
| 2x2x4-int8-zeros | zeros | 0xffffffff | 1 | 799.1 | no | 1139.7 | -1.08 | -2.96 | -4.23 | -1.07 |
| 2x4x16-fp32-zeros-m1111 | zeros | 0x1111 | 1 | 799.2 | no | 1650.7 | +9.40 | -4.34 | -1.76 | +3.91 |
| 2x4x16-fp32-zeros-m11111111 | zeros | 0x11111111 | 1 | 799.1 | no | 1672.8 | +9.13 | -2.71 | -2.62 | +3.56 |
| 2x4x16-fp32-zeros-m33333333 | zeros | 0x33333333 | 1 | 799.2 | no | 1700.7 | +9.68 | +1.40 | -2.61 | +4.17 |
| 2x4x16-fp32-zeros-s4 | zeros | 0xf | 1 | 799.1 | no | 1810.0 | -0.23 | -12.76 | -7.87 | -2.34 |
| 2x4x16-fp32-zeros-s8 | zeros | 0xff | 1 | 799.1 | no | 1856.7 | -1.67 | -12.34 | -7.24 | -1.25 |
| 2x4x16-fp32-zeros-s16 | zeros | 0xffff | 1 | 799.1 | no | 1916.7 | -2.68 | -10.03 | -4.28 | +2.62 |
| 2x4x16-fp32-zeros | zeros | 0xffffffff | 1 | 799.2 | yes | 1897.4 | +2.51 | +1.12 | +0.65 | +8.83 |
| 4x8x8-fp32-ones | ones | 0xffffffff | 1 | 799.0 | yes | 1734.2 | -1.01 | -2.58 | -0.58 | +5.85 |
| 4x8x8-fp32-den4 | pattern:den4 | 0xffffffff | 1 | 799.1 | yes | 1734.1 | -1.01 | -2.58 | - | - |
| 4x8x8-fp32-den8 | pattern:den8 | 0xffffffff | 1 | 799.1 | yes | 1733.4 | -0.97 | -2.54 | - | - |
| 4x8x8-fp32-fld_sign | pattern:fld_sign | 0xffffffff | 1 | 799.0 | yes | 1735.6 | -1.09 | -2.67 | - | - |
| 4x8x8-fp32-lanes2 | pattern:lanes2 | 0xffffffff | 1 | 799.0 | yes | 1741.6 | -1.43 | -3.00 | - | - |
| 4x8x8-fp32-rnd | random | 0xffffffff | 1 | 799.1 | yes | 1740.2 | -1.35 | -2.92 | +3.29 | +9.89 |
| 4x8x8-fp32-zeros | zeros | 0xffffffff | 1 | 799.0 | yes | 1738.1 | -1.24 | -2.81 | -2.33 | +3.74 |
| 4x8x8-int8-rnd | random | 0xffffffff | 6 | 798.9 | yes | 1736.0 | -0.22 | -2.70 | -1.40 | +7.64 |

## 2. Notes

- **Coverage.** All 46 declared arms are scored. The loader kept all 51 non-null runs and left none out, and none is NOT RUN. The 6
  anchor runs make one case.
- **The data lane's checks**, as committed in the data folder, all pass:
  - session checks C0-C9: the schedule equals the registered one, runner rc 0, 55 of 55 runs, the card's identity, the governed clocks, the
    stops, no timeout or kill, nothing left running, the sampler, and the power plan (board at most 61.28 W);
  - re-run checks R1-R5: the builder's one-job rebuild is a dated departure, and the host equals Tuesday's build; the freeze lines come
    before the first card command at 16:00:08.320 PST; the load guard never had to act; the first try's folder was left unopened.
  - This score does not depend on the verifier lane of the same round (verify-e212s3d), and this lane did not run it.
- **The model session's seals of S3** are E212's freeze lines: v3.2 `8f2df483...` (Tue 12:58), v3.3 `6842eca5...` (registered in
  fcbf60c4) and v3.4 `0dca417d...` (registered in d8dc4897). They are known by sha256 only, and none is read or used here.
- **The S4 desk test** (`test-s4/`) reproduces MM1-v3's README section 5 and `out/postcheck_twins.json` exactly. Two of that README's
  twin figures, 4.42% and 3.25%, are `postcheck_twins.json`'s 4.415% and 3.245% rounded a second time; unrounded they are 4.4149% and
  3.2447%, which the scorer prints as 4.41% and 3.24%.
- **Labels.** The figures are blind: data that did not exist when MM1-v3 was frozen, scored by rules hashed before the session's first
  card command. They are REPORTED, because no pass rule is registered. The readings of the misses are post hoc. Held out is not blind.

## 3. Files

| file | what |
|---|---|
| `DECLARED-blind-s3.md`, `DECLARED-blind-s3.json` | the declaration, as hashed at 14:10:50 PST Wed 18 Nov (byte for byte) |
| `s3-arms-twins.json` | the registered schedule's 46 non-null arms against MM1-v3's frozen rows, with their twin flags at 800 MHz (desk, before any datum) |
| `blind_v3_e212s3.json`, `blind_v3_e212s3_cases.csv`, `blind_v3_e212s3_runs.csv` | the score: every figure, every case and every run |
| `order-s3.json` | the order check: the session log's time records, the data commit, and the label rule's checks |
| `test-s4/` | the scorer's desk test on E212 a2c0-S4, made before any S3 datum |
| `scripts/` | the scorer and every script of the lane. The shell scripts show this box's paths as `<W>` (the round's folder), `<LAB>` (the lab clone) and `<EE>` (the model session's kit folder) |
| `logs/` | the lane's progress log (up to the build of this folder) and step logs, with the same placeholders; the lane's own land, scan and commit scripts and their logs stay in the round's folder |
| `scripts-and-logs.json` | the sha256 of each placeholder copy as run and as landed, and of each verbatim script |
| `SHA256SUMS` | every file here |

## 4. How to reproduce

```
git archive b1493082 tools/matmul/mm1/v3 tools/matmul/mm1/v2 | tar -x -C <dir>
/usr/bin/python3 -I -B scripts/s03_score.py --v3 <dir>/tools/matmul/mm1/v3 \
    --data docs/reports/data/2026-11-18-e212-mmsweep2-a2c0-S3/data-e212-a2c0-S3.json --session a2c0-S3 --label BLIND --out <out>
# the S4 desk test:
/usr/bin/python3 -I -B scripts/s03_score.py --v3 <dir>/tools/matmul/mm1/v3 \
    --data <dir>/tools/matmul/mm1/v3/inputs/e212-unread/a2c0-S4__data-e212-a2c0-S4.json --session a2c0-S4 --label TEST-S4 --out <out>
```

The outputs equal this folder's byte for byte. Interpreter: `/usr/bin/python3` 3.12.3, numpy 1.26.4, scipy 1.11.4, run `-I -B`,
single-threaded (OMP, OpenBLAS, MKL and NumExpr at one thread) inside the round's CPU slots on the lab box aifoundry2. Desk only: this
lane measured nothing and touched no card.
