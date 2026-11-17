# E211 scored for MM1-v2: its frozen forecasts of the second kernel, blind, beside MM1-v1, F1, F2 and the two nulls (REPORTED)

*Q206, lane score-v2-e211, at the desk on aifoundry2, Tue 17 Nov 2026 (week 47), scored at 13:49 PST: no card, no device command, no simulator. E211's registered rules score MM1-v1 only (H7, MM1-v2 against MM1-v1, NOT REGISTERED): every MM1-v2 figure here is REPORTED, never a verdict.*

**What.** MM1-v2's forecasts for E211 (THE SECOND KERNEL: rgm211, rgm136 with its C-block walk swapped, and rgm136's own non-cooperative loads, on aifoundry3 card 0 at its pinned 600 MHz), frozen in `forecasts-e211.json` (this folder; `FREEZE-e211.md`), are scored on E211's committed data (`docs/reports/data/2026-11-17-e211-second-kernel-aifoundry3/`, data commit `38aaf004`, RAN FULL: 38 of 38 runs and the smoke), beside E211's registered forecasts: MM1-v1, F1, F2, the chip-lines null NC and the no-walk null N0 (`tools/claims-v3/e211/forecast-e211.json`), by this lane's own code. Every one of the 26 points and 12 shape pairs is read: cycles an op (the counter's mean and the wall), seconds, W and J over idle given the measured seconds and with the seconds forecast, and J with the card at rest; each pair's ratio rgm211 / rgm136 against each model's ratio.

**Label: BLIND.** MM1-v2's E211 column was pushed to GitHub at 08:12:57 PST, 5 h 8 min 23 s before E211's first card command (13:21:20 PST) and before any E211 datum; the freeze commit `89aa0c94` is an ancestor of the data commit. **REPORTED:** E211's rules do not score MM1-v2.

**E211's own verdicts (the card lane's run of the registered scorer, on MM1-v1 and the others; not this lane's):** R0 PASS, S6 PASS, T1-T3 PASS, E1-E4 PASS; **T4 FAIL** (the controls: rgm211 ran 2.9% and 5.8% fewer wall cycles an op at x01 and x02, where both walks are one op stream), Amendment A1 not applied (the two controls differ by 0.031 in ln, past its 0.005), so family W reads "the controls did not pass: not a model test"; W1 FAIL (5 of 10), W2 PASS, H1-H4 and H6 NOT DECIDED, H5 MM1 BETTER, CT FAIL, CE FAIL, SR READ. That label holds for every ratio reading below, MM1-v2's included: the ratios are read raw (E211's basis) and, REPORTED beside, over the controls' mean offset (c_hat -0.0443 in ln).

## The times (the label's evidence)

| event | when (PST) | source |
|---|---|---|
| MM1-v1, F1, F2, NC, N0 frozen (E211's registration, `forecast-e211.json`) | 00:14 Tue 17 Nov 2026; registration commit `1393a649` 07:59:17 | E211.md section 0 |
| E207's session (the three E207 twins: w01m, w02m, w09m) | 07:06:44-07:53:54 | E207's data commit `867f6a3f` |
| **MM1-v2's E211 column pushed** (commit `89aa0c94`) | **08:12:57** (committed 08:12:53) | the freezing lane's push record; GitHub main then `89aa0c94` |
| E211 booked aifoundry3 (G) | 13:16:49 | the card lane's result |
| **E211's first card command** (step 7's config read, read only) | **13:21:20** | the card lane's run folder (`e211-step7-A.txt`) |
| E211's session (38 runs and the smoke) | 13:21:35-13:39:35 (17.99 card-minutes) | the card lane's result; T0 1794950494 |
| E211's data commit `38aaf004` | 13:41:44 committed, 13:41:48 pushed | git; the card lane's result |
| E211's registered scorer run (on MM1-v1 and the others) | 13:42:03 | the card lane's run folder (`scores-e211-A.json`) |
| this score | 13:49:50 | this lane |

## The answer in short

- **rgm211's 12 points (the kernel no card had run), cycles an op on the wall:** MM1-v2 8.9% (+4.0%) rms (bias), MM1-v1 8.1% (+2.5%), F1 14.5% (+7.8%), NC 23.5% (+16.0%). MM1-v2 closer than MM1-v1 / farther / tied: 3 / 7 / 2 (p 0.34), not decided. Both MM1 versions beat NC (MM1-v2 10 / 2 / 0 (p 0.039)); against F1 neither is decided (MM1-v2 4 / 8 / 0 (p 0.39)): F1 over-forecasts rgm136 by 17-20% at the large shapes and rgm211 ran about that much slower there, so F1 lands near rgm211's cycles while it misses the ratio.
- **The 12 rgm136 twins:** MM1-v2 2.9% (+1.3%), MM1-v1 3.7% (+0.9%), F1 17.2% (+14.7%), NC 14.2% (+11.9%); MM1-v2 closer than MM1-v1 at 8 of 12, farther at 3 (p 0.23). On all 26 points (family C in C1): MM1-v2 6.8% (+2.8%), MM1-v1 6.7% (+2.0%); 12 / 10 / 4 (p 0.83).
- **The ratio rgm211 / rgm136, the question (10 W pairs, raw, ln(model / measured)):** MM1-v2 rms 0.074 (bias +0.020), MM1-v1 0.065, F1 0.128, NC 0.126, N0 0.135; inside W1's 0.05 at 3, 5, 1, 3 and 2 of 10. The direction holds for both MM1 versions (W2's form: 8 decided, 0 missed). MM1-v2 against MM1-v1 3 / 5 / 2 (p 0.73), against F1 7 / 3 / 0 (p 0.34), NC 6 / 3 / 1 (p 0.51), N0 7 / 2 / 1 (p 0.18): none decided (E211's H1-H3 for MM1-v1 read the same). Where A is the far operand (w06-w10) the card measured rgm211 1.156-1.203 times rgm136's cycles: the slowdown both MM1 versions and NC forecast and F1 and N0 did not (F1 rms 0.147 there); MM1-v2 forecast 1.231-1.257 (rms 0.059, bias +0.056), MM1-v1 1.146-1.248 (rms 0.048). Over the controls' mean offset (REPORTED) MM1-v2's A-far rms is 0.022 and MM1-v1's 0.049.
- **Energy, J over idle given the measured seconds:** rgm211's points MM1-v2 3.2% (+0.6%), MM1-v1 3.2% (-0.5%), F1 18.4% (-16.2%); with the seconds forecast MM1-v2 3.6% (+1.0%), MM1-v1 3.4% (-0.3%), F1 11.2% (-10.7%), F2 30.8% (+21.6%). J with the card at rest given the seconds: MM1-v2 1.5% (+0.2%), MM1-v1 1.6% (-0.3%). On all 26 points MM1-v1 is closer more often on J over idle given the seconds (MM1-v2 6 / 19 / 1 (p 0.015)), by small margins: the rms is MM1-v2 5.1% (+0.0%) against MM1-v1 5.2% (-1.1%), both led by family C's c01c.
- **Family C (rgm136's non-cooperative loads, C1 carried on each model's twin):** c01 (2x3x2) wall ratio 0.969 against C1's 0.956 (inside CT's 0.02), J over idle ratio 1.389 against MM1-v2's C1 1.167 and MM1-v1's 1.169 (missed); c02 (3x5x7) wall 0.878 against 0.956 (missed), J 1.155 against 1.152 (held): C1 holds in time at the small shape and in joules at the large one, the same for both versions (their C1 ratios are equal in time and 0.2% apart in J).
- **MM1-v2 against MM1-v1, in all:** no time quantity decided at rgm211's points, the twins or all 26; the two versions' frozen forecasts sit 2.8% apart (rms of ln) on the wall at rgm211's points, 2.0% at the twins and 0.034 on the wall ratio (desk, before the data), small beside the day's misses. Both beat NC on cycles and F1 and F2 on energy at nearly every point; neither beats F1 or the nulls on the ratio on this day.

## Per case: every point against every model

Error = forecast / measured - 1 (positive: the model forecasts more); rms (bias) over the points; a point is the mean of its runs. F1 and NC carry one cycles figure an op, read against the wall and the counter's mean; F2's seconds are F1's; F2 has no frozen function of the seconds (its given-t columns NOT AVAILABLE). At family C's two points MM1-v2 and MM1-v1 are read in their C1 columns (E211's registered family C rule, E101's measured one-block figures carried on each model's twin).

**rgm211's 12 points (gemmLn: the second kernel, never run before E211)**

| quantity | MM1-v2 | MM1-v1 | F1 | F2 | NC | MM1-v2 worst | MM1-v1 worst |
|---|---:|---:|---:|---:|---:|---|---|
| cycles an op, the wall | 8.9% (+4.0%) | 8.1% (+2.5%) | 14.5% (+7.8%) | - | 23.5% (+16.0%) | w04n -15.4% | w05n +14.7% |
| cycles an op, the counter's mean | 8.9% (+4.0%) | 8.2% (+2.5%) | 17.1% (+10.1%) | - | 24.7% (+18.2%) | w04n -15.3% | w05n +15.9% |
| seconds a GEMM | 8.8% (+4.0%) | 8.0% (+2.5%) | 14.4% (+7.8%) | - | 23.4% (+16.0%) | w04n -15.5% | w05n +14.6% |
| W over idle, given the measured seconds | 3.2% (+0.6%) | 3.2% (-0.5%) | 18.4% (-16.2%) | - | - | w01n -8.5% | w01n -9.7% |
| W over idle, seconds forecast | 7.7% (-2.3%) | 7.4% (-2.2%) | 18.4% (-16.2%) | 27.9% (+14.4%) | - | w04n +14.0% | w05n -13.4% |
| J over idle, given the measured seconds | 3.2% (+0.6%) | 3.2% (-0.5%) | 18.4% (-16.2%) | - | - | w01n -8.5% | w01n -9.7% |
| J over idle, seconds forecast | 3.6% (+1.0%) | 3.4% (-0.3%) | 11.2% (-10.7%) | 30.8% (+21.6%) | - | w01n -8.3% | w01n -9.5% |
| J with the card at rest, given the seconds (measured rest) | 1.5% (+0.2%) | 1.6% (-0.3%) | 8.4% (-7.1%) | - | - | w01n -4.5% | w01n -5.1% |
| J with the card at rest, seconds forecast (measured rest) | 6.0% (+2.7%) | 5.2% (+1.2%) | 6.8% (-0.4%) | 16.3% (+12.2%) | - | w04n -10.7% | w04n -9.9% |
| J with the card at rest, the model's own rest law (REPORTED) | 7.1% (+4.1%) | 5.9% (+2.7%) | 7.4% (-2.9%) | 14.7% (+9.8%) | - | x02n +11.1% | w04n -9.0% |

**the 12 gemmL twins (rgm136: 4 in both models' fit, 3 run in E207 before the freeze, 5 never run)**

| quantity | MM1-v2 | MM1-v1 | F1 | F2 | NC | MM1-v2 worst | MM1-v1 worst |
|---|---:|---:|---:|---:|---:|---|---|
| cycles an op, the wall | 2.9% (+1.3%) | 3.7% (+0.9%) | 17.2% (+14.7%) | - | 14.2% (+11.9%) | x02m +5.3% | x01m -5.3% |
| cycles an op, the counter's mean | 2.7% (+0.3%) | 3.5% (-0.0%) | 18.2% (+15.9%) | - | 14.7% (+13.0%) | x02m +5.1% | w03m -6.2% |
| seconds a GEMM | 2.9% (+1.2%) | 3.7% (+0.8%) | 17.1% (+14.6%) | - | 14.1% (+11.8%) | x02m +5.2% | x01m -5.4% |
| W over idle, given the measured seconds | 2.7% (+1.1%) | 2.5% (-0.1%) | 21.8% (-20.9%) | - | - | w01m -6.6% | w01m -7.8% |
| W over idle, seconds forecast | 2.5% (+0.1%) | 3.1% (-0.7%) | 21.8% (-20.9%) | 19.2% (+10.4%) | - | w01m -5.2% | w01m -6.6% |
| J over idle, given the measured seconds | 2.7% (+1.1%) | 2.5% (-0.1%) | 21.8% (-20.9%) | - | - | w01m -6.6% | w01m -7.8% |
| J over idle, seconds forecast | 2.9% (+1.3%) | 2.7% (+0.0%) | 10.1% (-9.8%) | 31.5% (+26.1%) | - | w01m -6.6% | w01m -7.9% |
| J with the card at rest, given the seconds (measured rest) | 1.2% (+0.4%) | 1.2% (-0.1%) | 9.5% (-9.0%) | - | - | w01m -3.3% | w01m -4.0% |
| J with the card at rest, seconds forecast (measured rest) | 2.6% (+1.2%) | 3.0% (+0.5%) | 6.9% (+4.1%) | 21.3% (+18.8%) | - | x02m +4.2% | w01m -4.7% |
| J with the card at rest, the model's own rest law (REPORTED) | 3.5% (+2.5%) | 3.5% (+1.8%) | 5.6% (+1.3%) | 19.0% (+16.2%) | - | x02m +6.3% | w10m +5.7% |

**all 26 points (family C in C1)**

| quantity | MM1-v2 | MM1-v1 | F1 | F2 | NC | MM1-v2 worst | MM1-v1 worst |
|---|---:|---:|---:|---:|---:|---|---|
| cycles an op, the wall | 6.8% (+2.8%) | 6.7% (+2.0%) | 16.9% (+12.2%) | - | 19.5% (+14.1%) | w04n -15.4% | w05n +14.7% |
| cycles an op, the counter's mean | 6.5% (+2.1%) | 6.3% (+1.3%) | 19.3% (+14.6%) | - | 20.6% (+16.2%) | w04n -15.3% | w05n +15.9% |
| seconds a GEMM | 6.7% (+2.7%) | 6.6% (+2.0%) | 16.8% (+12.2%) | - | 19.4% (+14.0%) | w04n -15.5% | w05n +14.6% |
| W over idle, given the measured seconds | 5.1% (+0.0%) | 5.2% (-1.1%) | 22.9% (-20.5%) | - | - | c01c -21.8% | c01c -22.7% |
| W over idle, seconds forecast | 6.9% (-2.1%) | 7.1% (-2.6%) | 22.9% (-20.5%) | 25.2% (+8.9%) | - | c01c -19.7% | c01c -20.7% |
| J over idle, given the measured seconds | 5.1% (+0.0%) | 5.2% (-1.1%) | 22.9% (-20.5%) | - | - | c01c -21.8% | c01c -22.7% |
| J over idle, seconds forecast | 5.3% (+0.3%) | 5.4% (-0.9%) | 13.4% (-11.8%) | 31.2% (+20.9%) | - | c01c -21.9% | c01c -22.8% |
| J with the card at rest, given the seconds (measured rest) | 2.9% (-0.2%) | 3.0% (-0.7%) | 11.0% (-9.3%) | - | - | c01c -13.0% | c01c -13.6% |
| J with the card at rest, seconds forecast (measured rest) | 5.5% (+1.5%) | 5.2% (+0.5%) | 7.5% (+1.2%) | 19.2% (+14.4%) | - | c01c -14.2% | c01c -14.7% |
| J with the card at rest, the model's own rest law (REPORTED) | 6.2% (+2.9%) | 5.7% (+1.8%) | 7.4% (-1.4%) | 17.4% (+12.0%) | - | c01c -13.5% | c01c -14.0% |

**The twins by history** (wall cycles an op; rms (bias))

| twins | points | MM1-v2 | MM1-v1 | F1 | NC |
|---|---|---:|---:|---:|---:|
| in both models' fit (E206 arm A) | w04m, w06m, w07m, w10m | 2.6% (+1.7%) | 4.1% (+2.8%) | 15.5% (+13.1%) | 14.2% (+9.8%) |
| run in E207 before the freeze (not read) | w01m, w02m, w09m | 2.8% (+1.6%) | 2.4% (+1.1%) | 15.7% (+15.3%) | 13.0% (+10.4%) |
| never run before E211 | w03m, w05m, w08m, x01m, x02m | 3.2% (+0.8%) | 4.0% (-0.7%) | 19.2% (+15.7%) | 14.8% (+14.4%) |

## The ratios rgm211 / rgm136, pair by pair (the question)

The controls (both walks one op stream; every model says 1): x01 ln -0.0290, x02 ln -0.0596; T4 (|ln| <= 0.01) FAIL; c_hat -0.0443; Amendment A1 applies: no; E211's ratio rules read the **raw** ratios. Both readings are given for MM1-v2; the basis E211's rules use is the first.

**The wall ratio, raw** (measured; each model's ratio with ln(model / measured) in brackets)

| pair | shape | measured | MM1-v2 | MM1-v1 | F1 | NC | N0 |
|---|---|---:|---:|---:|---:|---:|---:|
| w01 | 2x3x2 | 0.9460 | 0.9993 (+0.0548) | 0.9993 (+0.0548) | 0.9796 (+0.0348) | 0.9796 (+0.0348) | 1 (+0.0555) |
| w02 | 3x3x4 | 1.0911 | 1.0632 (-0.0259) | 1.0443 (-0.0438) | 1.1527 (+0.0549) | 1.3516 (+0.2141) | 1 (-0.0872) |
| w03 | 3x6x3 | 0.9829 | 0.9332 (-0.0518) | 0.9681 (-0.0152) | 0.8288 (-0.1705) | 0.7862 (-0.2233) | 1 (+0.0173) |
| w04 | 2x8x4 | 0.9980 | 0.8593 (-0.1496) | 0.8805 (-0.1252) | 0.8705 (-0.1367) | 0.8362 (-0.1768) | 1 (+0.0020) |
| w05 | 2x9x4 | 0.8127 | 0.8896 (+0.0904) | 0.8951 (+0.0965) | 0.8730 (+0.0715) | 0.8422 (+0.0357) | 1 (+0.2074) |
| w06 | 3x5x7 | 1.1736 | 1.2305 (+0.0473) | 1.1806 (+0.0059) | 1.0272 (-0.1333) | 1.2680 (+0.0773) | 1 (-0.1601) |
| w07 | 3x6x6 | 1.2027 | 1.2343 (+0.0259) | 1.1464 (-0.0479) | 1.0342 (-0.1509) | 1.2892 (+0.0695) | 1 (-0.1846) |
| w08 | 4x3x6 | 1.1560 | 1.2510 (+0.0790) | 1.2479 (+0.0765) | 0.9834 (-0.1617) | 1.1745 (+0.0159) | 1 (-0.1450) |
| w09 | 6x6x6 | 1.1673 | 1.2569 (+0.0739) | 1.2357 (+0.0569) | 1.0000 (-0.1547) | 1.2567 (+0.0738) | 1 (-0.1547) |
| w10 | 3x5x7 int8 | 1.1667 | 1.2305 (+0.0532) | 1.1806 (+0.0118) | 1.0238 (-0.1306) | 1.3006 (+0.1086) | 1 (-0.1542) |
| **rms (bias)** | | | 0.0737 (+0.0197) | 0.0646 (+0.0070) | 0.1284 (-0.0877) | 0.1256 (+0.0230) | 0.1351 (-0.0604) |
| **inside 0.05 (W1's form)** | | | 3 of 10 | 5 of 10 | 1 of 10 | 3 of 10 | 2 of 10 |

| group (E211.md section 1) | MM1-v2 rms (bias) | MM1-v1 | F1 | NC | N0 |
|---|---:|---:|---:|---:|---:|
| A far w06 w10 | 0.0591 (+0.0559) | 0.0481 (+0.0206) | 0.1467 (-0.1462) | 0.0752 (+0.0690) | 0.1603 (-0.1597) |
| B far w04 w05 | 0.1236 (-0.0296) | 0.1118 (-0.0143) | 0.1091 (-0.0326) | 0.1276 (-0.0706) | 0.1467 (+0.1047) |
| L3 and knee w01 w03 | 0.0460 (-0.0077) | 0.0414 (-0.0014) | 0.1054 (-0.0269) | 0.1797 (+0.0086) | 0.0605 (-0.0048) |

Direction (W2's form, REPORTED for MM1-v2): MM1-v2 PASS (8 decided, 0 missed); MM1-v1 PASS (8 decided, 0 missed).

| head to head on the wall ratio (10 W pairs, tie 0.005 in ln) | first / second / tied, p: reading |
|---|---|
| MM1-v2 against MM1-v1 | 3 / 5 / 2, p 0.73: NOT DECIDED |
| MM1-v2 against F1 | 7 / 3 / 0, p 0.34: NOT DECIDED |
| MM1-v2 against NC | 6 / 3 / 1, p 0.51: NOT DECIDED |
| MM1-v2 against N0 | 7 / 2 / 1, p 0.18: NOT DECIDED |
| MM1-v1 against F1 | 8 / 2 / 0, p 0.11: NOT DECIDED |
| MM1-v1 against NC | 7 / 3 / 0, p 0.34: NOT DECIDED |
| MM1-v1 against N0 | 7 / 1 / 2, p 0.07: NOT DECIDED |

**The wall ratio, control-corrected** (measured; each model's ratio with ln(model / measured) in brackets)

| pair | shape | measured | MM1-v2 | MM1-v1 | F1 | NC | N0 |
|---|---|---:|---:|---:|---:|---:|---:|
| w01 | 2x3x2 | 0.9889 | 0.9993 (+0.0105) | 0.9993 (+0.0105) | 0.9796 (-0.0094) | 0.9796 (-0.0094) | 1 (+0.0112) |
| w02 | 3x3x4 | 1.1405 | 1.0632 (-0.0702) | 1.0443 (-0.0881) | 1.1527 (+0.0106) | 1.3516 (+0.1698) | 1 (-0.1314) |
| w03 | 3x6x3 | 1.0274 | 0.9332 (-0.0961) | 0.9681 (-0.0595) | 0.8288 (-0.2148) | 0.7862 (-0.2675) | 1 (-0.0270) |
| w04 | 2x8x4 | 1.0431 | 0.8593 (-0.1939) | 0.8805 (-0.1695) | 0.8705 (-0.1810) | 0.8362 (-0.2211) | 1 (-0.0422) |
| w05 | 2x9x4 | 0.8495 | 0.8896 (+0.0461) | 0.8951 (+0.0522) | 0.8730 (+0.0273) | 0.8422 (-0.0086) | 1 (+0.1631) |
| w06 | 3x5x7 | 1.2268 | 1.2305 (+0.0030) | 1.1806 (-0.0384) | 1.0272 (-0.1775) | 1.2680 (+0.0330) | 1 (-0.2044) |
| w07 | 3x6x6 | 1.2571 | 1.2343 (-0.0184) | 1.1464 (-0.0922) | 1.0342 (-0.1952) | 1.2892 (+0.0252) | 1 (-0.2288) |
| w08 | 4x3x6 | 1.2084 | 1.2510 (+0.0347) | 1.2479 (+0.0322) | 0.9834 (-0.2060) | 1.1745 (-0.0284) | 1 (-0.1893) |
| w09 | 6x6x6 | 1.2202 | 1.2569 (+0.0296) | 1.2357 (+0.0126) | 1.0000 (-0.1990) | 1.2567 (+0.0295) | 1 (-0.1990) |
| w10 | 3x5x7 int8 | 1.2195 | 1.2305 (+0.0090) | 1.1806 (-0.0324) | 1.0238 (-0.1749) | 1.3006 (+0.0643) | 1 (-0.1985) |
| **rms (bias)** | | | 0.0752 (-0.0246) | 0.0742 (-0.0372) | 0.1619 (-0.1320) | 0.1253 (-0.0213) | 0.1598 (-0.1046) |
| **inside 0.05 (W1's form)** | | | 7 of 10 | 5 of 10 | 3 of 10 | 6 of 10 | 3 of 10 |

| group (E211.md section 1) | MM1-v2 rms (bias) | MM1-v1 | F1 | NC | N0 |
|---|---:|---:|---:|---:|---:|
| A far w06 w10 | 0.0224 (+0.0116) | 0.0494 (-0.0236) | 0.1909 (-0.1905) | 0.0388 (+0.0247) | 0.2044 (-0.2040) |
| B far w04 w05 | 0.1409 (-0.0739) | 0.1254 (-0.0586) | 0.1294 (-0.0769) | 0.1565 (-0.1148) | 0.1191 (+0.0604) |
| L3 and knee w01 w03 | 0.0690 (-0.0519) | 0.0617 (-0.0457) | 0.1243 (-0.0712) | 0.1830 (-0.0357) | 0.0777 (-0.0491) |

Direction (W2's form, REPORTED for MM1-v2): MM1-v2 FAIL (9 decided, 2 missed); MM1-v1 FAIL (9 decided, 2 missed).

| head to head on the wall ratio (10 W pairs, tie 0.005 in ln) | first / second / tied, p: reading |
|---|---|
| MM1-v2 against MM1-v1 | 5 / 3 / 2, p 0.73: NOT DECIDED |
| MM1-v2 against F1 | 6 / 3 / 1, p 0.51: NOT DECIDED |
| MM1-v2 against NC | 6 / 2 / 2, p 0.29: NOT DECIDED |
| MM1-v2 against N0 | 7 / 2 / 1, p 0.18: NOT DECIDED |
| MM1-v1 against F1 | 7 / 2 / 1, p 0.18: NOT DECIDED |
| MM1-v1 against NC | 5 / 3 / 2, p 0.73: NOT DECIDED |
| MM1-v1 against N0 | 7 / 2 / 1, p 0.18: NOT DECIDED |

**The other ratios** (raw; ln(model / measured): rms (bias) over the W pairs; MM1-v2 against MM1-v1 on each)

| ratio | MM1-v2 | MM1-v1 | F1 | F2 | NC | N0 | MM1-v2 against MM1-v1 |
|---|---:|---:|---:|---:|---:|---:|---|
| counter's mean | 0.0789 (+0.0308) | 0.0699 (+0.0181) | 0.1234 (-0.0766) | - | 0.1255 (+0.0340) | 0.1358 (-0.0493) | 3 / 5 / 2, p 0.73: NOT DECIDED |
| seconds | 0.0732 (+0.0207) | 0.0645 (+0.0080) | 0.1271 (-0.0868) | - | 0.1238 (+0.0239) | 0.1352 (-0.0594) | 3 / 5 / 2, p 0.73: NOT DECIDED |
| W over idle (forecast) | 0.0680 (-0.0255) | 0.0576 (-0.0137) | 0.1157 (+0.0722) | 0.1525 (+0.0347) | - | 0.1170 (+0.0474) | 2 / 7 / 1, p 0.18: NOT DECIDED |
| J over idle (seconds forecast) | 0.0187 (-0.0049) | 0.0212 (-0.0057) | 0.0194 (-0.0146) | 0.1462 (-0.0521) | - | 0.0255 (-0.0120) | 4 / 0 / 6, p 0.12: TOO FEW |
| J over idle given each side's measured seconds | 0.0172 (-0.0074) | 0.0187 (-0.0067) | 0.1157 (+0.0722) | - | - | 0.0255 (-0.0120) | 2 / 0 / 8, p 0.5: TOO FEW |

## Head to head per point

d = |ln(measured / second)| - |ln(measured / first)|; first / second / tied (tie 0.001 in ln for cycles and seconds, 0.005 for watts and joules), the exact two-sided sign test; REPORTED.

**rgm211's 12 points**

| quantity | MM1-v2 against MM1-v1 | MM1-v2 against F1 | MM1-v2 against NC or F2 | MM1-v1 against F1 |
|---|---|---|---|---|
| cycles an op, the wall | 3 / 7 / 2, p 0.34: NOT DECIDED | 4 / 8 / 0, p 0.39: NOT DECIDED | NC: 10 / 2 / 0, p 0.039: MM1-v2 BETTER | 6 / 6 / 0, p 1: NOT DECIDED |
| cycles an op, the counter's mean | 3 / 7 / 2, p 0.34: NOT DECIDED | 4 / 8 / 0, p 0.39: NOT DECIDED | NC: 11 / 1 / 0, p 0.0063: MM1-v2 BETTER | 5 / 7 / 0, p 0.77: NOT DECIDED |
| seconds a GEMM | 3 / 7 / 2, p 0.34: NOT DECIDED | 4 / 8 / 0, p 0.39: NOT DECIDED | NC: 10 / 2 / 0, p 0.039: MM1-v2 BETTER | 6 / 6 / 0, p 1: NOT DECIDED |
| W over idle, given the measured seconds | 3 / 8 / 1, p 0.23: NOT DECIDED | 11 / 1 / 0, p 0.0063: MM1-v2 BETTER | - | 11 / 1 / 0, p 0.0063: MM1-v1 BETTER |
| J over idle, given the measured seconds | 3 / 8 / 1, p 0.23: NOT DECIDED | 11 / 1 / 0, p 0.0063: MM1-v2 BETTER | - | 11 / 1 / 0, p 0.0063: MM1-v1 BETTER |
| J over idle, seconds forecast | 3 / 8 / 1, p 0.23: NOT DECIDED | 12 / 0 / 0, p 0.00049: MM1-v2 BETTER | F2: 10 / 2 / 0, p 0.039: MM1-v2 BETTER | 12 / 0 / 0, p 0.00049: MM1-v1 BETTER |
| J with the card at rest, given the seconds (measured rest) | 2 / 3 / 7, p 1: TOO FEW | 11 / 1 / 0, p 0.0063: MM1-v2 BETTER | - | 11 / 1 / 0, p 0.0063: MM1-v1 BETTER |
| J with the card at rest, seconds forecast (measured rest) | 4 / 6 / 2, p 0.75: NOT DECIDED | 4 / 8 / 0, p 0.39: NOT DECIDED | F2: 10 / 1 / 1, p 0.012: MM1-v2 BETTER | 5 / 7 / 0, p 0.77: NOT DECIDED |

**the 12 twins**

| quantity | MM1-v2 against MM1-v1 | MM1-v2 against F1 | MM1-v2 against NC or F2 | MM1-v1 against F1 |
|---|---|---|---|---|
| cycles an op, the wall | 8 / 3 / 1, p 0.23: NOT DECIDED | 11 / 1 / 0, p 0.0063: MM1-v2 BETTER | NC: 11 / 1 / 0, p 0.0063: MM1-v2 BETTER | 11 / 1 / 0, p 0.0063: MM1-v1 BETTER |
| cycles an op, the counter's mean | 9 / 2 / 1, p 0.065: NOT DECIDED | 11 / 1 / 0, p 0.0063: MM1-v2 BETTER | NC: 12 / 0 / 0, p 0.00049: MM1-v2 BETTER | 11 / 1 / 0, p 0.0063: MM1-v1 BETTER |
| seconds a GEMM | 8 / 3 / 1, p 0.23: NOT DECIDED | 11 / 1 / 0, p 0.0063: MM1-v2 BETTER | NC: 11 / 1 / 0, p 0.0063: MM1-v2 BETTER | 11 / 1 / 0, p 0.0063: MM1-v1 BETTER |
| W over idle, given the measured seconds | 2 / 10 / 0, p 0.039: MM1-v1 BETTER | 12 / 0 / 0, p 0.00049: MM1-v2 BETTER | - | 12 / 0 / 0, p 0.00049: MM1-v1 BETTER |
| J over idle, given the measured seconds | 2 / 10 / 0, p 0.039: MM1-v1 BETTER | 12 / 0 / 0, p 0.00049: MM1-v2 BETTER | - | 12 / 0 / 0, p 0.00049: MM1-v1 BETTER |
| J over idle, seconds forecast | 2 / 8 / 2, p 0.11: NOT DECIDED | 12 / 0 / 0, p 0.00049: MM1-v2 BETTER | F2: 12 / 0 / 0, p 0.00049: MM1-v2 BETTER | 12 / 0 / 0, p 0.00049: MM1-v1 BETTER |
| J with the card at rest, given the seconds (measured rest) | 1 / 2 / 9, p 1: TOO FEW | 12 / 0 / 0, p 0.00049: MM1-v2 BETTER | - | 12 / 0 / 0, p 0.00049: MM1-v1 BETTER |
| J with the card at rest, seconds forecast (measured rest) | 8 / 3 / 1, p 0.23: NOT DECIDED | 11 / 1 / 0, p 0.0063: MM1-v2 BETTER | F2: 12 / 0 / 0, p 0.00049: MM1-v2 BETTER | 11 / 1 / 0, p 0.0063: MM1-v1 BETTER |

**all 26 points (family C in C1)**

| quantity | MM1-v2 against MM1-v1 | MM1-v2 against F1 | MM1-v2 against NC or F2 | MM1-v1 against F1 |
|---|---|---|---|---|
| cycles an op, the wall | 12 / 10 / 4, p 0.83: NOT DECIDED | 17 / 9 / 0, p 0.17: NOT DECIDED | NC: 23 / 3 / 0, p 8.8e-05: MM1-v2 BETTER | 19 / 7 / 0, p 0.029: MM1-v1 BETTER |
| cycles an op, the counter's mean | 13 / 9 / 4, p 0.52: NOT DECIDED | 17 / 9 / 0, p 0.17: NOT DECIDED | NC: 25 / 1 / 0, p 8e-07: MM1-v2 BETTER | 18 / 8 / 0, p 0.076: NOT DECIDED |
| seconds a GEMM | 12 / 10 / 4, p 0.83: NOT DECIDED | 17 / 9 / 0, p 0.17: NOT DECIDED | NC: 23 / 3 / 0, p 8.8e-05: MM1-v2 BETTER | 19 / 7 / 0, p 0.029: MM1-v1 BETTER |
| W over idle, given the measured seconds | 6 / 19 / 1, p 0.015: MM1-v1 BETTER | 25 / 1 / 0, p 8e-07: MM1-v2 BETTER | - | 25 / 1 / 0, p 8e-07: MM1-v1 BETTER |
| J over idle, given the measured seconds | 6 / 19 / 1, p 0.015: MM1-v1 BETTER | 25 / 1 / 0, p 8e-07: MM1-v2 BETTER | - | 25 / 1 / 0, p 8e-07: MM1-v1 BETTER |
| J over idle, seconds forecast | 6 / 17 / 3, p 0.035: MM1-v1 BETTER | 26 / 0 / 0, p 3e-08: MM1-v2 BETTER | F2: 24 / 2 / 0, p 1e-05: MM1-v2 BETTER | 26 / 0 / 0, p 3e-08: MM1-v1 BETTER |
| J with the card at rest, given the seconds (measured rest) | 4 / 5 / 17, p 1: NOT DECIDED | 25 / 1 / 0, p 8e-07: MM1-v2 BETTER | - | 25 / 1 / 0, p 8e-07: MM1-v1 BETTER |
| J with the card at rest, seconds forecast (measured rest) | 14 / 9 / 3, p 0.4: NOT DECIDED | 16 / 10 / 0, p 0.33: NOT DECIDED | F2: 24 / 1 / 1, p 1.5e-06: MM1-v2 BETTER | 17 / 9 / 0, p 0.17: NOT DECIDED |

## Family C: rgm136's own non-cooperative loads (gemmLnc over its twin)

| pair | shape | quantity | measured | v2-C1 | v1-C1 | C0 (no change) | inside CT/CE's tolerance: v2-C1 / v1-C1 |
|---|---|---|---:|---:|---:|---:|---|
| c01 | 2x3x2 | wall | 0.9690 | 0.9563 (-0.0131) | 0.9563 (-0.0131) | 1 (+0.0315) | yes / yes |
| c01 | 2x3x2 | mean | 0.9220 | 0.9150 (-0.0076) | 0.9150 (-0.0076) | 1 (+0.0812) | - |
| c01 | 2x3x2 | J | 1.3891 | 1.1665 (-0.1746) | 1.1685 (-0.1729) | 1 (-0.3287) | no / no |
| c02 | 3x5x7 | wall | 0.8779 | 0.9563 (+0.0855) | 0.9563 (+0.0855) | 1 (+0.1302) | no / no |
| c02 | 3x5x7 | mean | 0.8778 | 0.9150 (+0.0415) | 0.9150 (+0.0415) | 1 (+0.1303) | - |
| c02 | 3x5x7 | J | 1.1552 | 1.1522 (-0.0026) | 1.1528 (-0.0021) | 1 (-0.1443) | yes / yes |

## Every point

Measured (the mean of the point's runs) and each model's error (forecast / measured - 1). Family C's rows carry C1 for MM1-v2 and MM1-v1.

| point | arm | runs | wall cycles an op | MM1-v2 | MM1-v1 | F1 | NC | J over idle given t (J) | MM1-v2 | MM1-v1 | F1 | J seconds forecast: MM1-v2 | MM1-v1 | F2 |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| c01c | `gemmLnc2x3x2` | 2 | 876.6 | -2.7% | -2.6% | +14.2% | +3.1% | 0.04051 | -21.8% | -22.7% | -46.4% | -21.9% | -22.8% | -42.9% |
| c02c | `gemmLnc3x5x7` | 2 | 1030.5 | +12.1% | +14.0% | +33.9% | +28.7% | 0.29048 | +1.6% | +0.7% | -40.9% | +2.3% | +1.7% | +13.7% |
| w01m | `gemmL2x3x2` | 2 | 904.7 | -1.4% | -1.3% | +10.6% | -0.1% | 0.02905 | -6.6% | -7.8% | -22.8% | -6.6% | -7.9% | -20.3% |
| w01n | `gemmLn2x3x2` | 1 | 855.9 | +4.1% | +4.2% | +14.6% | +3.5% | 0.02937 | -8.5% | -9.7% | -27.1% | -8.3% | -9.5% | -21.8% |
| w02m | `gemmL3x3x4` | 1 | 1047.5 | +4.1% | +0.8% | +17.4% | +18.8% | 0.08345 | +1.5% | +0.0% | -21.1% | +1.8% | +0.1% | +12.9% |
| w02n | `gemmLn3x3x4` | 1 | 1142.9 | +1.4% | -3.6% | +24.0% | +47.2% | 0.08553 | +0.7% | -1.0% | -25.3% | +0.8% | -1.3% | +37.9% |
| w03m | `gemmL3x6x3` | 1 | 1117.5 | -2.7% | -5.2% | +22.6% | +16.7% | 0.12819 | +0.6% | -1.1% | -24.9% | +0.3% | -1.6% | +31.1% |
| w03n | `gemmLn3x6x3` | 1 | 1098.4 | -7.6% | -6.6% | +3.4% | -6.6% | 0.12370 | +3.0% | +1.8% | -11.1% | +2.5% | +1.3% | -0.1% |
| w04m | `gemmL2x8x4` | 2 | 1376.9 | -1.8% | -2.3% | -1.3% | -7.2% | 0.15873 | +0.8% | +0.1% | -10.9% | +0.6% | -0.2% | +23.8% |
| w04n | `gemmLn2x8x4` | 2 | 1374.1 | -15.4% | -13.8% | -13.9% | -22.3% | 0.16030 | -2.3% | -2.8% | -0.8% | -3.7% | -4.2% | -2.1% |
| w05m | `gemmL2x9x4` | 2 | 1128.2 | +2.8% | +4.2% | +20.1% | +12.4% | 0.17299 | +1.2% | +0.2% | -24.4% | +1.4% | +0.5% | +27.2% |
| w05n | `gemmLn2x9x4` | 2 | 916.9 | +12.5% | +14.7% | +29.0% | +16.5% | 0.16978 | -0.6% | -1.7% | -29.7% | +0.2% | -0.7% | +4.0% |
| w06m | `gemmL3x5x7` | 3 | 1173.6 | +2.9% | +4.7% | +17.6% | +13.0% | 0.25176 | +2.2% | +1.4% | -22.4% | +2.5% | +1.8% | +31.2% |
| w06n | `gemmLn3x5x7` | 2 | 1377.2 | +7.9% | +5.3% | +2.9% | +22.1% | 0.25646 | +2.1% | +1.2% | -12.5% | +2.8% | +1.7% | +34.2% |
| w07m | `gemmL3x6x6` | 1 | 1150.9 | +3.1% | +4.9% | +19.1% | +13.3% | 0.25592 | +3.1% | +2.1% | -22.5% | +3.3% | +2.6% | +31.3% |
| w07n | `gemmLn3x6x6` | 1 | 1384.2 | +5.8% | -0.0% | +2.4% | +21.5% | 0.26382 | +1.9% | +0.6% | -12.0% | +2.5% | +0.6% | +34.1% |
| w08m | `gemmL4x3x6` | 2 | 1180.5 | +0.9% | +0.0% | +20.0% | +19.8% | 0.17115 | +1.8% | +0.4% | -22.9% | +1.9% | +0.4% | +37.9% |
| w08n | `gemmLn4x3x6` | 2 | 1364.7 | +9.2% | +8.0% | +2.1% | +21.7% | 0.17441 | +2.5% | +1.7% | -11.4% | +3.4% | +2.6% | +31.9% |
| w09m | `gemmL6x6x6` | 1 | 1161.4 | +2.2% | +4.0% | +18.0% | +12.3% | 0.51546 | +2.4% | +1.5% | -22.4% | +2.6% | +1.9% | +30.4% |
| w09n | `gemmLn6x6x6` | 1 | 1355.7 | +10.0% | +10.0% | +1.1% | +20.9% | 0.52056 | +2.7% | +2.0% | -10.3% | +3.6% | +3.0% | +29.1% |
| w10m | `gemmL3x5x7 int8` | 1 | 1179.9 | +2.4% | +4.1% | +17.0% | +20.1% | 0.12380 | +3.0% | +1.3% | -27.7% | +3.4% | +2.0% | +60.1% |
| w10n | `gemmLn3x5x7 int8` | 1 | 1376.6 | +8.0% | +5.3% | +2.7% | +33.9% | 0.12984 | +1.5% | -0.2% | -19.8% | +3.0% | +0.9% | +63.3% |
| x01m | `gemmL1x5x5` | 1 | 1084.2 | -2.5% | -5.3% | +22.1% | +10.2% | 0.05887 | +1.4% | -0.5% | -24.4% | +1.2% | -0.9% | +25.2% |
| x01n | `gemmLn1x5x5` | 1 | 1053.2 | +0.4% | -2.5% | +25.7% | +13.5% | 0.05867 | +1.5% | -0.4% | -26.3% | +1.6% | -0.6% | +25.6% |
| x02m | `gemmL3x1x8` | 1 | 1412.4 | +5.3% | +2.6% | -6.3% | +13.1% | 0.05794 | +2.3% | +1.3% | -4.0% | +2.8% | +1.6% | +22.1% |
| x02n | `gemmLn3x1x8` | 1 | 1330.7 | +11.8% | +8.9% | -0.6% | +20.0% | 0.05718 | +3.0% | +2.1% | -8.3% | +4.1% | +3.0% | +23.7% |

## The worst cases, and why

**The controls: two compiled loops, not one loop walked two ways (shared by every model).** At x01 (1x5x5) and x02 (3x1x8) the desk map gives both walks the same op stream, and every model forecasts a ratio of 1; the card ran rgm211 2.9% and 5.8% fewer wall cycles an op (ratios 0.971 and 0.942). E211.md section 6 (Amendment A1) had read the static loops at 31 instructions an op in rgm211's gemmLn against 36 in rgm136's gemmL and estimated about -0.4% to -1.5% at x01 at the desk; the card's offset at x01 is about twice the estimate's far end, at x02 about four times, and the two controls part by more than A1 allows. Neither MM1 version has a term for the compiled loop, so part of every rgm211 point's error is this offset: MM1-v2's bias on the wall is +4.0% at rgm211's points against +1.3% at the twins (MM1-v1 +2.5% against +0.9%). w01 (2x3x2, inside the L3, where both walks are nearly one stream) misses by the same sign: measured 0.946 against 0.999 (+0.055 in ln for both versions), +0.010 over the controls' mean offset.

**2x8x4 and 2x9x4, where B's large panel was rgm136's far operand: the largest misses, shared.** At 2x8x4 (NB 8, a power of two) rgm211 ran at 0.998 of rgm136's cycles where MM1-v2 forecast 0.859 and MM1-v1 0.881: rgm136's own 2x8x4 (w04m) was forecast within 1.8% (MM1-v2) and 2.3% (MM1-v1), but rgm211's (w04n) ran 15.4% more cycles than MM1-v2 forecast (13.8% for MM1-v1): MM1-v2's worst point. At 2x9x4 (NB 9) rgm211 gained more than forecast: ratio 0.813 against 0.890 and 0.895; w05n ran 12.5% fewer cycles than MM1-v2 forecast (14.7%, MM1-v1's worst point). SR's form: s = ln(ratio at 2x8x4 / ratio at 2x9x4) = +0.205 measured, against MM1-v2's four stride readings: the literal carryover (its forecast) -0.035, no stride term -0.003, zeta on both halves +0.006, the stride on rgm136's walk only -0.154 (MM1-v1's, as E211 registered them, -0.016, +0.004, +0.024, -0.136); no frozen reading comes within 0.18 in ln (the closest, zeta on both halves, is the one E211's SR names). rgm211 itself ran 50% more cycles an op at NB 8 than at NB 9, rgm136 22%. *Post hoc, not tested:* in rgm211's walk B's column panel is used for both row blocks in a row, a reuse both models count as near; a power-of-two row stride (16 KB at NB 8) may keep that panel from staying in the cache, which would cost the nb-outer walk its gain at NB 8 alone. A ladder of NB at fixed MB and KB in rgm211 would test it.

**Where A is the far operand (w06-w10), the ratio's size.** The card measured the slowdown both MM1 versions forecast (1.156-1.203), and F1 (0.983-1.034) and N0 (1) did not: the chip's DRAM traffic, not the lines a shire-op, sets the time there, as E211's map said. Raw, MM1-v2 forecasts more slowdown than measured at all five (bias +0.056 in ln), MM1-v1 more at 4 and less at 1 (bias +0.021); over the controls' mean offset MM1-v2 sits within 0.035 in ln at all five (rms 0.022) and MM1-v1 within 0.092 (rms 0.049). Which reading is right turns on whether the controls' offset carries to the A-far shapes, which this day cannot say (A1 did not apply). In absolute cycles, after 2x8x4 and 2x9x4 MM1-v2's largest misses are x02n +11.8% (MM1-v1 +8.9%), the control with the larger offset, and the A-far rgm211 points w09n +10.0%, w08n +9.2%, w10n +8.0% and w06n +7.9% (MM1-v1 +10.0%, +8.0%, +5.3%, +5.3%).

**Energy.** Both versions forecast J over idle given the seconds within 8.5% (MM1-v2) at every rgm211 point; the worst is w01n (2x3x2): -8.5% (MM1-v1 -9.7%): rgm211 drew 26.8 W over idle there against its twin's 25.1 W while running 5.4% fewer wall cycles, so its joules a GEMM came out 1.5% above the twin's, where both versions forecast 0.6% below. The largest energy miss of the day is family C's c01c (2x3x2 without cooperation): 36.1 W over idle against the twin's 25.1 W, J over idle given the seconds -21.8% for MM1-v2's C1 (-22.7% for MM1-v1's): E101's one-block energy figure carried by C1 gives +17% for losing the cooperation where the card drew +39%; mm-kernel2's draft rule C2 (REPORTED) was within 0.029 in ln there and +0.189 at c02. F2 over-forecasts J at nearly every point (bias +21.6% at rgm211's), worst w10n (int8) +63.3%; F1 under-forecasts W over idle by about 16-21% at the full chip on this card.

**v2S, E211's sharing-aware rule on MM1-v2 (A's fresh lines priced twice):** J over idle given the seconds at rgm211's points 11.7% (+7.8%) against MM1-v2's 3.2% (+0.6%); MM1-v2 closer 8 / 1 / 3 (p 0.039): the card follows the literal per-shire-line price on this day, as E211's H6 read MM1-v1 against MM1-S (NOT DECIDED, 8 / 2 / 2).

## Reported beside

- **Inside MM1-v1's bands** (E211's T1-T3, E1-E4 bands, the registered error form, at rgm211's 12 points): MM1-v2 T1 11, T2 11, T3 11, E1 12, E2 12, E3 12, E4 12 of 12 (at least 11 would read PASS); MM1-v1 (registered, PASS each) 11, 12, 11, 12, 12, 11, 12.
- **The smoke** (2 s processes, the counter's mean against MM1-v2): s01 -3.6%, s02 +4.7%, s03 +4.7% (v2-C1 -4.2%); inside R0's 50-250% band at all three.
- **The timing simulation's step column** (rgm136's cooperative gemmL step law at every point, the same column in both versions; simulator steps, not time, and at the gemmLn and gemmLnc points not the count of their own ELF): the card's wall cycles a GEMM over it run 18.2-30.2 times (median 24.7).
- **The rest law:** the measured rest 23.52-24.34 W against MM1-v2's (and MM1-v1's) aifoundry3 rest law, 24.74 W at its 54.4 C forecast die: +0.40 to +1.22 W.
- **The replicates:** the two to four runs of a point agree within 0.14% in wall cycles and within 1.1% in J over idle (w06m's three runs, one in family C's block, within 4.2%): the errors above are the models', not the day's noise.
- **The other ratios** (raw, rms of ln over the W pairs): the counter's mean MM1-v2 0.079, MM1-v1 0.070; seconds 0.073 and 0.065; J over idle (seconds forecast) 0.019 and 0.021 (F1 0.019, F2 0.146, N0 0.026): the joules hardly change with the walk (the op count is equal), and every MM1 column and N0 read that.

## The cross-check against E211's registered scorer

This code re-implements E211's measured side and MM1-v1's readings independently; on E211's data it reproduces the registered scorer's output (the card lane's run folder, `scores-e211-A.json`, sha256 `71c991f9...`, not in the repository when this was written): MM1-v1's T1-T3 and E1-E4 errors at the 12 rgm211 points, 84 numbers, largest difference 0; the measured pair ratios, 40 numbers, largest relative difference 0; family C's ratios, 6 numbers, 0; H1-H6's counts equal (H1 8/2/0; H2 7/3/0; H3 7/1/2; H4 6/6/0; H5 10/1/1; H6 8/2/2); T4 FAIL, c_hat -0.04428, A1 False in both.

## Inputs

| input | path | sha256 |
|---|---|---|
| data | `docs/reports/data/2026-11-17-e211-second-kernel-aifoundry3/data-e211.json` | `76dbb7341f4d05960f725ebd15b3e32091cf584c4d241fdbeaff87e82fdd0f1e` |
| points | `tools/claims-v3/e211/points-e211.json` | `234b496a9488eb078734e0c26ff833fe56ab5b4194e4ddc7f7f9d20141f5a537` |
| rules | `tools/claims-v3/e211/rules-e211.json` | `53c54fbe278fb9aa9e1a3875cdea0782339b25bd831a55f48f3fd912b26d37ca` |
| v1 | `tools/claims-v3/e211/forecast-e211.json` | `90e8d1ae4c68c162eab687624f72bf15599ae26d2050012c3381f179453108f5` |
| v2 | `tools/matmul/mm1/v2/forecasts-e211.json` | `0dce8a5e9ae3a593cfd5af6d9d399f7db337c37c36edcd04ddf6ba78baedecce` |

## How it was made

- `score_v2_e211.py` (this folder): the lane's own code, Python's standard library only; it imports nothing from E211's kit, E211's scorer or any model. It checks every input's sha256 against the config and, for the four frozen files, against its own pins (exit 4 on any difference), re-implements E211's measured side (E211.md section 7) and writes `score-e211.json` (every point, run, pair and reading) and `score-e211.txt` (the printed summary). Run from the repository's top: `/usr/bin/python3 -I -B tools/matmul/mm1/v2/score_v2_e211.py --config tools/matmul/mm1/v2/score-e211-config.json --out OUT.json --txt OUT.txt` (it never overwrites).
- `score-e211-config.json`: the inputs by path and sha256, the labels and the times.
- `selftest_score_v2_e211.py` and its output `selftest-score-v2-e211.txt`: six stand-in days made from the frozen forecasts (every run at MM1-v2's forecast, at MM1-v1's, at F1's; a common -2% code-path offset on rgm211's wall cycles in families X and W, where T4 fails and Amendment A1 applies; family C missing and one run set aside; every W over idle x 1.05) and a changed copy of forecasts-e211.json (refused), each with its result stated before the run by arithmetic on the frozen files; E211's registered scorer was run on the same days and this code's MM1-v1 readings, measured pair ratios and H1-H6 counts equal its output. The stand-in days live outside the repository and outside every folder a never-run search reads.
- `SHA256SUMS-score-e211`: the seven files above (`sha256sum -c SHA256SUMS-score-e211` from this folder).
- Interpreter: `/usr/bin/python3` 3.12.3, run `-I -B`; at the desk on aifoundry2 inside the round's CPU slot; no card, no device command, no simulator.

## Labels and limits

- **Every MM1-v2 figure here is REPORTED.** E211 registered no MM1-v2 forecast and its head-to-head H7 (MM1-v2 against MM1-v1) is NOT REGISTERED (E211.md sections 0 and 7); these readings are this lane's, beside E211's registered verdicts on MM1-v1, never in place of them.
- **BLIND:** MM1-v2's forecasts were pushed to GitHub before E211's first card command (the times above), made by MM1-v2 as landed in `3ca4b717`, unchanged, through E211's committed desk map at MM1-v2's own L3 retention (`FREEZE-e211.md`). MM1-v2's constants are desk fits made after their own data existed (post hoc as an act); they were refitted with E208 (rgm136 on aifoundry2 card 0 and aifoundry1 cards 0 and 1), never on E207's or E211's data.
- **The twins' history:** w04m, w06m, w07m and w10m are E206 arm A points, in both models' fits; w01m, w02m and w09m (and family C's twin runs of w01m) ran in E207 on this card at 07:06-07:53 PST, before MM1-v2's E211 freeze (08:12:57), and MM1-v2's forecasts there were made without reading that datum; E211's runs of them are still blind. w03m, w05m, w08m, x01m and x02m never ran before E211. rgm211's 12 points and family C's two are a kernel and a load mode no card had run.
- **One day, one card:** aifoundry3 card 0 at its pinned 600 MHz; each point is the mean of its two or four runs (one twin run more in family C for w01m and w06m); the day's replicate spread is in the JSON (per run).
- **F2's given-t columns are NOT AVAILABLE:** E211 froze F2's watts and joules at F1's seconds and no function of the seconds; this lane runs no model's route. F2 is read with its seconds forecast only. F1 and NC carry one cycles figure an op, read against both the wall and the counter's mean.
- **Family C:** MM1-v2 and MM1-v1 have no term for the load mode; their C1 columns carry E211's registered rule (E101's measured one-block figures) on each model's own twin, and their literal columns (C0: no change) are given beside.
- **No transistor switch is measured**; MM1-v2's switch estimates are not scored. The timing simulation's step column (rgm136's gemmL step law at every point) is REPORTED beside, never scored.
- **Not read:** the model session's sealed forecasts (no number of theirs is here). Every input is a public lab commit named above.

Q206, lane score-v2-e211. SPDX-License-Identifier: Apache-2.0
