# E211 data, dated note 2 (post hoc): the data verifier's four wording findings, answered

*Tue 17 Nov 2026, 14:21 PST, the fix lane `fix-e211d` (Q204), after the data verifier `verify-e211d` (HOLDS WITH FIXES: this directory's data commit `38aaf004` re-derives exactly, and its four findings are wording only, low or nit). A dated note beside this directory's README and dated note 1. **Post hoc**: written after the data and after the frozen scorer's run. It edits no committed file and changes no datum, forecast, rule, label or verdict, and it does not re-run the frozen scorer. Every figure below is desk arithmetic of this directory's measured records and of the registration's frozen files (`forecast-e211.json`, `rules-e211.json` and `points-e211.json`, checked at their registered sha256). They are printed by `posthoc_note2_e211.py` in this directory, run from this directory under `/usr/bin/python3` 3.12.3: its printout is `posthoc-note2-e211.txt` and its JSON `posthoc-note2-e211.json`, both listed in `SHA256SUMS-note2`.*

## 1. The head to head per W pair, with the registered tie (finding 1)

The card lane's own result (a lane file, never committed) named, for each W pair, the model closer in H1 (MM1 against F1), H2 (MM1 against the chip-lines null NC) and H3 (MM1 against the no-walk null N0). It took them from a per-case table that counted every nonzero d as a win, that is, a tie of 0. E211's rules register a tie of **0.005 in ln** for H1-H3 (`rules-e211.json`, H, `tie_ln_cycles`; E211.md section 7). There d = |ln(measured / second)| - |ln(measured / MM1)|: MM1 is closer where d > 0.005, the second model where d < -0.005, and a tie otherwise.

Under that tie, two of the thirty readings are ties: **H3 at w01 (d +0.0007) and at w03 (d +0.0021)**. So any post or note that quotes per-pair winners reads **w01 F1 / NC / tie** and **w03 MM1 / MM1 / tie**. Every other reading is as the card lane gave it. The per-pair readings give back the frozen scorer's counts exactly: H1 8/2/0, H2 7/3/0 and H3 7/1/2 (MM1 closer / the other closer / ties). The scorer's output is committed beside this directory by a later lane.

| pair | shape | measured wall ratio rgm211/rgm136 | MM1 | F1 | NC | N0 | d (H1) | d (H2) | d (H3) | closer: H1 / H2 / H3 |
|---|---|---|---|---|---|---|---|---|---|---|
| w01 | 2x3x2 | 0.94605 | 0.99933 | 0.97959 | 0.97959 | 1 | -0.0200 | -0.0200 | +0.0007 | F1 / NC / **tie** |
| w02 | 3x3x4 | 1.09107 | 1.04430 | 1.15267 | 1.35156 | 1 | +0.0111 | +0.1703 | +0.0433 | MM1 / MM1 / MM1 |
| w03 | 3x6x3 | 0.98287 | 0.96806 | 0.82876 | 0.78621 | 1 | +0.1554 | +0.2081 | +0.0021 | MM1 / MM1 / **tie** |
| w04 | 2x8x4 | 0.99797 | 0.88052 | 0.87046 | 0.83622 | 1 | +0.0115 | +0.0516 | -0.1232 | MM1 / MM1 / N0 |
| w05 | 2x9x4 | 0.81270 | 0.89506 | 0.87298 | 0.84223 | 1 | -0.0250 | -0.0608 | +0.1109 | F1 / NC / MM1 |
| w06 | 3x5x7 | 1.17364 | 1.18060 | 1.02721 | 1.26796 | 1 | +0.1273 | +0.0714 | +0.1542 | MM1 / MM1 / MM1 |
| w07 | 3x6x6 | 1.20269 | 1.14642 | 1.03425 | 1.28923 | 1 | +0.1030 | +0.0216 | +0.1366 | MM1 / MM1 / MM1 |
| w08 | 4x3x6 | 1.15601 | 1.24789 | 0.98344 | 1.17451 | 1 | +0.0852 | -0.0606 | +0.0685 | MM1 / NC / MM1 |
| w09 | 6x6x6 | 1.16732 | 1.23569 | 1.00000 | 1.25674 | 1 | +0.0978 | +0.0169 | +0.0978 | MM1 / MM1 / MM1 |
| w10 | 3x5x7, int8 | 1.16671 | 1.18060 | 1.02385 | 1.30059 | 1 | +0.1188 | +0.0968 | +0.1424 | MM1 / MM1 / MM1 |

The measured ratios are desk arithmetic of the measured runs: each pair's own W-block runs, the mean wall cycles an op of its gemmLn runs over that of its gemmL runs. They equal the README's pairs table. The MM1, F1, NC and N0 columns are the frozen forecasts (blind). The d and closer columns follow the registered definition.

These are the raw ratios, the basis the frozen scorer reads. T4 failed and Amendment A1 did not apply (the two controls differ by 0.0306 in ln), so these readings carry the registered words **"the controls did not pass: not a model test"**, as W1, W2 and the H1-H3 verdicts do. The verdicts are the frozen scorer's: H1, H2 and H3 are NOT DECIDED.

## 2. The smoke table's p_rest and mJ over idle at s02 and s03 are not rest readings (finding 2)

For each smoke process, the README's smoke table prints the reducer's `p_rest_w`: the median board W over the 5 s before the process started. `reduce_e211.py`'s docstring names it as a kit choice: "the 5 s before it its rest: the end of the 30 s rest reading for s01, the previous process's tail for the others; kit". The three smoke processes ran back to back:

| smoke | its process (PST) | its 5 s window (50 samples) | p_rest in the README | reading |
|---|---|---|---|---|
| s01 | 13:22:05.827 to 13:22:08.852 | all 50 in the smoke's 30 s rest reading | 23.04 W | at rest |
| s02 | 13:22:08.855 to 13:22:11.778, 3 ms after s01 ended | 20 in the rest reading, 30 in s01's process | 25.26 W | **not a rest reading** |
| s03 | 13:22:11.780 to 13:22:14.253, 2 ms after s02 ended | 21 in s01's process, 29 in s02's, none at rest | 47.7 W | **not a rest reading** |

So at s02 and s03, two kinds of cell do not measure against the card at rest: p_rest (25.26 and 47.7 W) and mJ over idle (17.93 and 8.266), which subtracts it. These cells are unaffected: s01's, and every process's mJ at rest (p_work x t_gemm: 36.75, 36.4 and 43.98). No rule reads any of these cells: of the smoke, R0 reads only its checks, walk, identity gate and counter mean, never its watts. The 38 runs are unaffected too: in all 38, the 5 s window before the process lies inside the run's own 10 s rest read.

The session's own rest reading is the smoke's 30 s rest: 13:21:35.820 to 13:22:05.821 PST, 299 samples, median 23.08 W (`session/smoke/rest.json`). The README's smoke-gate lines already read each process against it: the gate's `board_rise` reads 24.47, 26.7 and 35.66 W over 23.08 W. **Post hoc**, on that rest reading, mJ over idle ((p_work - 23.08 W) x t_gemm) reads 18.92 at s01, 19.52 at s02 and 26.7 at s03. These figures are REPORTED here only and are never a rule's input.

## 3. The shires' mean peak, as a span (finding 3)

The README's results table gives the shires' mean peak as "59 C at 13:37:46". The session's highest shires' mean (`minshire[0]`, over all of its 10,781 samples) is **59 C, on 25 samples from 13:36:31 to 13:37:46 PST**: the first at 13:36:31.185, the last at 13:37:46.990, 25 of the 758 samples in that span. All 25 fall inside family C's two `gemmLnc2x3x2` (c01c) processes: run 036 holds 13 and run 038 holds 12. The README's 13:37:46 is the last of them. Restated, the peak is 59 C from 13:36:31 to 13:37:46 PST.

## 4. The never-run search's own gap (finding 4)

Departure 6 quotes step 6n's summary line. The scan's report in this directory (`neverrun-e211-card.txt` and `.json`) also states its own gap. Of its four scans, round-lanes on aifoundry2 (1,194 roots, 415,675 files read) could not read 29 files and skipped 2 files over 400 MB. The other three scans (aifoundry2-work, aifoundry3-box and lab-head) read every file. Restated, the search read every file in its scope except those 31, as the scan prints. It stays REPORTED, as departure 6 says: a desk read (E211.md section 4) that no rule reads.

## What this note changes

It changes nothing measured, forecast, registered or scored. It adds five new files: this note, the script, its printout, its JSON, and `SHA256SUMS-note2`. `SHA256SUMS-note2` also lists `README.md`, `README.md.dated-note-1.md` and `SHA256SUMS` as the data commit holds them. Every committed file stands as committed. To reproduce: from this directory, `/usr/bin/python3 -I -B posthoc_note2_e211.py --json <a new path>` prints `posthoc-note2-e211.txt` byte for byte, using Python's own modules only.

SPDX-License-Identifier: Apache-2.0
