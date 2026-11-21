# E220, the pooled rules over both arms, dated note 17 of arm B's data directory: the frozen scorer on both arms' committed measured sides at once - HP1-HP5 MM1-v3.2 BETTER than MM1-v3; HP7, HP9 and HP10 MM1-v3.2 BETTER than MM1-v3.1, HP6 and HP8 NOT DECIDED; CXP-T and CXP-E LARGER HERE, each printed beside dated note 1's rates; with verify-e220d's pooled reading beside

*Fri 20 Nov 2026 (week 47), PST; written from about 16:40 PST by Q233's lane `scores-e220` at the desk on aifoundry2, under `/usr/bin/python3` 3.12.3 (`-I -B`), each numerical step single-threaded inside the round's CPU slots. It comes after both arms' data commits (arm A `fd074f9e`, 15:41:40 PST, aifoundry1 card 1; arm B `257496b7`, 15:44:26 PST, aifoundry2 card 0), after `verify-e220d` (HOLDS: it made the pooled reading first, by its own code and by the frozen scorer's two-arm run, and both agree on all 53 verdicts), after arm A's dated note 1 and after this directory's dated note 16 (arm B's step-13 outputs, committed just before this note). It adds new files only: no committed file, datum, forecast, rule, band, label or scorer is changed.* **Labels:** **BLIND** (every forecast E220 scores was frozen before either arm's first device access: MM1-v3.2's land `4e386f75`, committed 19:50:04 PST Thu 19 Nov 2026, and E220's registration `6901854c`, committed 12:31:40 PST and pushed 12:31:45 PST Fri 20 Nov 2026, with MM1-v3.1's, MM1-v3's and MM1-v2's E220 forecasts, the points, the bands, the rules and the scorer; the model session's sealed forecast was registered in `d5df9568`, committed 14:44:58 PST, before both bookings at 14:50:53 PST, and none of its numbers is read here; arm A's first device access was fwgate's read at 14:53:55 PST, arm B's at 14:57:42 PST), **measured** (the committed records), **registered** (E220.md, its dated note 1 and its kit), **REPORTED** (a reading, never a verdict), **post hoc** (anything read after the data), **desk** (a check of code at the desk).

**The words.** E220.md section 7: "H1-H5 MM1-v3.2 vs MM1-v3: wall, the counter's mean, seconds (per case), W over idle given the measured op time (Wg; per point), J over idle with t forecast (Jf; per point), over every registered point of the arm; H6-H10 the same against MM1-v3.1; HP1-HP10 the same pooled over both arms' points, each case with its own arm's tie." and, for the cross-card rule, "CX-T the wall cycles an op; CX-E W over idle given the measured op time, at the twins measured at 3 W and above on both cards; per arm, and pooled (CXP-T, CXP-E)." "R0 (every check of C exact or approx; the smoke good; the G block's smoke s03 failing while no gemmLnc point ran is flagged, not an R0 failure) and, arm A, S6 (every kept run's samples at 590-610 MHz): a FAIL labels every other verdict of its arm and of the pooled tests." Neither arm reads R0 FAIL and arm A reads S6 PASS, so no pooled verdict carries a label. Each card lane's step 13 ran the frozen scorer on its own arm only, so neither one-arm file holds the registered pooled reading (their pooled lines are one arm each: arm A's note 1 and this directory's note 16, clause 1 of each).

## 1. The new files

| file | bytes | sha256 | what |
|---|---|---|---|
| `scores-e220-pooled.json` | 200,577 | `cc1aad9287050c37c66b0df6a56fd3e23c9a39628ec4786f4169cb6fd78d8ec8` | the frozen scorer's `scores-e220.json` from its run on both arms at once: both arms' verdicts and sections (each equal to its arm's own file) and the registered pooled HP1-HP10, CXP-T and CXP-E |
| `scores-e220-pooled.txt` | 900 | `4d80bea4e89209d2ad102f866d44c3759024a71d9e3878f4aff0731d9a566d31` | its `scores-e220.txt`, which is also the run's printed lines byte for byte |
| `cx-beside-e220-pooled.txt` | 1,504 | `33e329edfc6641499725c750a3107594f29c39f00ee8b5afab915b37234f5e14` | dated note 1's printer ([`cx_null_e220_note1.py`](../../../../tools/claims-v3/e220-notes/cx_null_e220_note1.py) `beside`) on that JSON: every cross-card verdict, per arm and pooled, with the note's two false LARGER HERE rates beside it, as the note asks of this lane |
| `README.md.dated-note-17.md` | (this note) | listed in `SHA256SUMS-note17` | this dated note |
| `SHA256SUMS-note17` | 5 lines | (not listed in itself) | the four files above and `SHA256SUMS-note16` |

With `SHA256SUMS`, `SHA256SUMS-note16` and `SHA256SUMS-note17`, every file of this directory is in a list except `SHA256SUMS-note17` itself.

## 2. How the pooled verdicts were made (desk checks of code)

- **The run.** The command, in the committed paths and from the lab's top, under THE CPU RULE's slot: `/usr/bin/python3 -I -B tools/claims-v3/e220/score_e220.py --a docs/reports/data/2026-11-20-e220-blind-matmul-aifoundry1-c1/data-e220a.json --a-tag A --b docs/reports/data/2026-11-20-e220-blind-matmul-aifoundry2/data-e220b.json --out <a folder>`, then `/usr/bin/python3 -I -B tools/claims-v3/e220-notes/cx_null_e220_note1.py beside <that folder>/scores-e220.json`. The JSON and text it writes are `scores-e220-pooled.json` and `.txt` (renamed only), and the printer's lines are `cx-beside-e220-pooled.txt`.
- **The inputs.** Arm A's measured side is its committed `data-e220a.json` (`fd074f9e`, sha256 `3eaef558f957d7cd...`, its directory's `SHA256SUMS` line); arm B's is this directory's `data-e220b.json` (note 16: step 13's reduction of the committed session, byte for byte, sha256 `c7a50cb1aeefcf1b...`), the same measured side each card lane's step 13 scored. The scorer's frozen points, forecasts and rules are at their registered sha256 (it refuses otherwise), and the scorer is `3c771990` as pinned.
- **The labels.** Both arms' committed step-6n labels name no point (arm A's `labels-e220.json`, `{"A": []}`; arm B's `ranbefore-e220b.json`, `{"B": []}`), so the run takes no `--labels`, as arm B's step 13 did; a second run with `--labels` on one file holding both empty sets wrote the same bytes, and so did a third with RB_OUT's own copy of arm B's reduction as `--b`.
- **The checks.** The run was made before this commit on a tree exported from the lab clone's own objects at HEAD, with arm B's reduction as step 13 makes it (byte for byte this directory's `data-e220b.json`); it equals verify-e220d's two-arm run byte for byte (`scores-e220.json` cc1aad92...; its 53 of 53 verdicts equal verify-e220d's own code's). Its arm A section equals arm A's own file's (`scores-e220-A.json`) and its arm B section arm B's (`scores-e220.json`, note 16), exactly. Every pooled count is the sum of its two arms' counts (HP1 74/40/42 = 49/22/13 + 25/18/29, ..., CXP-E 42/16/12 = 21/12/8 + 21/4/4), and every p is the scorer's `sign_p()` of its counts. The printer's output equals verify-e220d's printout of the same run byte for byte, and on each arm's RB_OUT JSON it equals the card lanes' printed lines.

## 3. The pooled verdicts (registered; BLIND)

The words of the head-to-head: "per case d = |ln(measured / second)| - |ln(measured / first)| (at a watts point |W - second| - |W - first|, in W), decided when |d| exceeds the arm's tie; the exact two-sided sign test over the decided: 'MM1-v3.2 BETTER' or '<second> BETTER' at p < 0.05 with at least 10 decided, NOT DECIDED otherwise, TOO FEW under 10, NO DATA with none."

| rule | quantity | MM1-v3.2 against | over | MM1-v3.2 closer / the other closer / ties | p (exact, two-sided) | verdict (the frozen scorer) | arm A | arm B | verify-e220d (own code) |
|---|---|---|---|---|---|---|---|---|---|
| **HP1** | the wall cycles | MM1-v3 | 156 | 74/40/42 | 0.00187 | **MM1-v3.2 BETTER** | 49/22/13 | 25/18/29 | the same counts, p and verdict |
| **HP2** | the counter's mean | MM1-v3 | 156 | 74/35/47 | 2.37e-4 | **MM1-v3.2 BETTER** | 48/17/19 | 26/18/28 | the same counts, p and verdict |
| **HP3** | seconds | MM1-v3 | 156 | 74/40/42 | 0.00187 | **MM1-v3.2 BETTER** | 49/22/13 | 25/18/29 | the same counts, p and verdict |
| **HP4** | W over idle given t | MM1-v3 | 156 | 68/26/62 | 1.73e-5 | **MM1-v3.2 BETTER** | 58/2/24 | 10/24/38 | the same counts, p and verdict |
| **HP5** | J over idle, t forecast | MM1-v3 | 156 | 69/14/73 | 6.80e-10 | **MM1-v3.2 BETTER** | 46/2/36 | 23/12/37 | the same counts, p and verdict |
| **HP6** | the wall cycles | MM1-v3.1 | 156 | 65/45/46 | 0.0696 | **NOT DECIDED** | 39/25/20 | 26/20/26 | the same counts, p and verdict |
| **HP7** | the counter's mean | MM1-v3.1 | 156 | 65/39/52 | 0.0138 | **MM1-v3.2 BETTER** | 39/19/26 | 26/20/26 | the same counts, p and verdict |
| **HP8** | seconds | MM1-v3.1 | 156 | 65/45/46 | 0.0696 | **NOT DECIDED** | 39/25/20 | 26/20/26 | the same counts, p and verdict |
| **HP9** | W over idle given t | MM1-v3.1 | 156 | 45/19/92 | 0.00156 | **MM1-v3.2 BETTER** | 35/2/47 | 10/17/45 | the same counts, p and verdict |
| **HP10** | J over idle, t forecast | MM1-v3.1 | 156 | 64/20/72 | 1.58e-6 | **MM1-v3.2 BETTER** | 36/2/46 | 28/18/26 | the same counts, p and verdict |
| **CXP-T** | wall cycles, X twins | aifoundry3 card 0's error (E218) | 92 | 20/8/64 (larger here / larger on aifoundry3 / ties) | 0.0357 | **LARGER HERE** | 0/4/48 | 20/4/16 | the same counts, p and verdict |
| **CXP-E** | W over idle given t, X twins at 3 W and above | aifoundry3 card 0's error (E218) | 70 | 42/16/12 (larger here / larger on aifoundry3 / ties) | 8.62e-4 | **LARGER HERE** | 21/12/8 | 21/4/4 | the same counts, p and verdict |

The registered answer: over both cards' points pooled, **MM1-v3.2 is closer than MM1-v3 in every quantity (HP1-HP5)**, and closer than MM1-v3.1 in the counter's mean and both energy quantities (HP7, HP9, HP10); against MM1-v3.1 the wall cycles and the seconds read NOT DECIDED (HP6, HP8: 65/45/46, p 0.0696). E220.md section 8, stated before the data: "a NOT DECIDED says the models' time forecasts are close, not that they are equally good".

## 4. The cross-card rule, pooled, with dated note 1's rates beside

The words: "per X twin with data on the arm and in E218 (aifoundry3 card 0), e_here = |ln(measured / MM1-v3.2's frozen forecast)| on this card at its registered clock and e_a3 = the same in E218"; "d = e_here - e_a3, decided when |d| exceeds the arm's tie; the exact two-sided sign test over the decided: 'LARGER HERE' (MM1-v3.2's error larger on this card) or 'SMALLER HERE' at p < 0.05 with at least 10 decided, NOT DECIDED otherwise, TOO FEW under 10, NO DATA with none." `cx-beside-e220-pooled.txt`, all of it:

```
A:CX-E: NOT DECIDED (41 twins, 21 larger here, 12 larger on aifoundry3, p 0.16275565745308995) | dated note 1: false LARGER HERE at equal distribution 0.0032 (resampled aifoundry3 errors), at equal rms with normal errors 0.1084 (registered 0.095)
B:CX-E: LARGER HERE (29 twins, 21 larger here, 4 larger on aifoundry3, p 0.0009105205535888672) | dated note 1: false LARGER HERE at equal distribution 0.0019 (resampled aifoundry3 errors), at equal rms with normal errors 0.3379 (registered 0.331)
CXP-E: LARGER HERE (70 twins, 42 larger here, 16 larger on aifoundry3, p 0.0008617822405421263) | dated note 1: false LARGER HERE at equal distribution 0.0033 (resampled aifoundry3 errors), at equal rms with normal errors 0.4986
A:CX-T: TOO FEW (52 twins, 0 larger here, 4 larger on aifoundry3, p none) | dated note 1: false LARGER HERE at equal distribution 0.0039 (resampled aifoundry3 errors), at equal rms with normal errors 0.0088 (registered 0.009)
B:CX-T: LARGER HERE (40 twins, 20 larger here, 4 larger on aifoundry3, p 0.001543879508972168) | dated note 1: false LARGER HERE at equal distribution 0.0039 (resampled aifoundry3 errors), at equal rms with normal errors 0.0021 (registered 0.004)
CXP-T: LARGER HERE (92 twins, 20 larger here, 8 larger on aifoundry3, p 0.03569813817739487) | dated note 1: false LARGER HERE at equal distribution 0.0052 (resampled aifoundry3 errors), at equal rms with normal errors 0.0089
CX-BESIDE-E220-NOTE1: 6 cross-card verdict(s) printed with the null rates beside
```

E220.md section 8: "The cross-card energy test reads LARGER HERE at equal error with a simulated rate of 0.095 on arm A and 0.331 on arm B" (no pooled rate was registered). Dated note 1, before any datum: "A LARGER HERE there is read as "this card's errors are not distributed like aifoundry3's: larger, or less heavy-tailed". It is not read as "larger at an equal shape"." So **CXP-E LARGER HERE** (42/16/12, p 8.62e-4) carries a false LARGER HERE rate of 0.4986 at equal rms with normal errors and 0.0033 at equal distribution: by note 1's reading it says that MM1-v3.2's energy errors on these two cards are not distributed like its errors on aifoundry3 (larger, or less heavy-tailed), not that they are larger at an equal shape. **CXP-T LARGER HERE** (20/8/64, p 0.0357) rests on arm B alone: arm A's twins read 0/4/48 and arm B's 20/4/16, so all 20 'larger here' are arm B's (arm B's twins ran under its governor and were scored at 799.0 MHz; its median card offset is +0.199 in ln, arm A's -0.0016).

## 5. Each model's rms, per arm and pooled (REPORTED; BLIND; desk arithmetic)

rms (bias) of ln(measured / forecast) in %, every registered point with data (arm B by route c), in verify-e220d's definitions, made here with the frozen scorer's `predicted()` and equal to verify-e220d's figures (72 of 72 to 1e-9 points):

| quantity | scope (n) | MM1-v3.2 | MM1-v3.1 | MM1-v3 | MM1-v2 |
|---|---|---|---|---|---|
| wall cycles | arm A (84) | 7.55 (+1.02) | 9.68 (-0.40) | 9.30 (+0.18) | 12.27 (+4.32) |
| wall cycles | arm B (72) | 6.88 (+1.27) | 9.06 (-0.27) | 8.68 (-0.03) | 13.30 (+6.72) |
| wall cycles | pooled (156) | 7.25 (+1.14) | 9.40 (-0.34) | 9.02 (+0.08) | 12.75 (+5.42) |
| the counter's mean | arm A (84) | 8.96 (+2.48) | 10.81 (+1.06) | 10.53 (+1.64) | 14.19 (+5.78) |
| the counter's mean | arm B (72) | 8.48 (+2.88) | 10.26 (+1.34) | 9.93 (+1.58) | 15.48 (+8.33) |
| the counter's mean | pooled (156) | 8.74 (+2.67) | 10.56 (+1.19) | 10.26 (+1.61) | 14.80 (+6.95) |
| seconds | arm A (84) | 7.42 (+1.05) | 9.56 (-0.37) | 9.18 (+0.21) | 12.21 (+4.34) |
| seconds | arm B (72) | 6.88 (+1.26) | 9.06 (-0.28) | 8.68 (-0.05) | 13.29 (+6.70) |
| seconds | pooled (156) | 7.18 (+1.15) | 9.33 (-0.33) | 8.95 (+0.09) | 12.72 (+5.43) |
| W over idle given t (3 W and above) | arm A (63) | 10.80 (+1.03) | 20.12 (+7.27) | 20.03 (+6.84) | 19.66 (+8.11) |
| W over idle given t (3 W and above) | arm B (72) | 6.11 (-1.28) | 8.91 (-0.49) | 9.01 (+0.13) | 8.70 (-2.10) |
| W over idle given t (3 W and above) | pooled (135) | 8.62 (-0.20) | 15.21 (+3.13) | 15.18 (+3.26) | 14.86 (+2.66) |
| J over idle, t forecast (3 W and above) | arm A (63) | 11.02 (+1.14) | 20.35 (+7.20) | 20.29 (+6.84) | 20.23 (+8.34) |
| J over idle, t forecast (3 W and above) | arm B (72) | 7.27 (-0.95) | 10.69 (-0.42) | 10.79 (+0.25) | 12.17 (+1.87) |
| J over idle, t forecast (3 W and above) | pooled (135) | 9.21 (+0.03) | 15.94 (+3.14) | 15.94 (+3.32) | 16.43 (+4.89) |
| J at rest given t (every point) | arm A (84) | 3.90 (+0.47) | 6.99 (+2.38) | 6.97 (+2.32) | 6.89 (+2.77) |
| J at rest given t (every point) | arm B (72) | 3.36 (-1.04) | 5.17 (-0.39) | 5.19 (-0.11) | 5.03 (-1.18) |
| J at rest given t (every point) | pooled (156) | 3.66 (-0.23) | 6.22 (+1.11) | 6.21 (+1.20) | 6.10 (+0.95) |

## 6. Each model's error by family, pooled (REPORTED)

The wall cycles:

| family / subfamily | n | MM1-v3.2 | MM1-v3.1 | MM1-v3 | MM1-v2 |
|---|---|---|---|---|---|
| X | 92 | 6.58 (-1.51) | 10.25 (-3.86) | 9.59 (-3.33) | 12.44 (+1.57) |
| X/XF | 28 | 7.66 (-6.61) | 14.52 (-12.47) | 13.51 (-11.55) | 12.27 (-9.63) |
| X/XG | 14 | 10.06 (-1.94) | 12.92 (-4.27) | 12.09 (-3.62) | 12.35 (-3.08) |
| X/XGt | 20 | 2.93 (+0.73) | 5.55 (-1.61) | 4.71 (-1.06) | 6.07 (+1.23) |
| X/XY | 30 | 4.98 (+1.94) | 5.20 (+2.88) | 5.33 (+2.96) | 15.44 (+14.42) |
| L3 | 16 | 5.47 (+2.34) | 6.00 (+1.00) | 5.83 (+1.53) | 8.71 (+3.29) |
| L3/L3-1 | 10 | 6.66 (+4.76) | 6.19 (+4.78) | 6.50 (+5.00) | 10.52 (+7.26) |
| L3/L3-2 | 6 | 2.42 (-1.68) | 5.67 (-5.30) | 4.49 (-4.25) | 4.25 (-3.32) |
| Y2 | 20 | 4.53 (+0.57) | 4.48 (+1.26) | 4.65 (+1.46) | 15.33 (+14.74) |
| Y2/Y2-pair | 12 | 5.37 (-0.49) | 4.92 (-0.04) | 5.12 (+0.23) | 13.23 (+12.62) |
| Y2/Y2-control | 8 | 2.85 (+2.15) | 3.72 (+3.19) | 3.86 (+3.30) | 18.04 (+17.93) |
| G2 | 14 | 14.36 (+13.56) | 13.95 (+13.31) | 14.19 (+13.48) | 16.86 (+16.06) |
| G2/G2-NB56 | 14 | 14.36 (+13.56) | 13.95 (+13.31) | 14.19 (+13.48) | 16.86 (+16.06) |
| G2t | 14 | 5.64 (+5.59) | 5.44 (+5.32) | 5.59 (+5.49) | 9.40 (+9.26) |
| G2t/G2t-NB56 | 14 | 5.64 (+5.59) | 5.44 (+5.32) | 5.59 (+5.49) | 9.40 (+9.26) |
| **all** | 156 | 7.25 (+1.14) | 9.40 (-0.34) | 9.02 (+0.08) | 12.75 (+5.42) |

W over idle given t (3 W and above on both sides):

| family / subfamily | n | MM1-v3.2 | MM1-v3.1 | MM1-v3 | MM1-v2 |
|---|---|---|---|---|---|
| X | 81 | 6.81 (-2.05) | 12.85 (+1.22) | 12.78 (+1.28) | 13.03 (+0.93) |
| X/XF | 28 | 5.56 (-5.30) | 6.20 (-5.91) | 6.32 (-6.12) | 6.31 (-5.67) |
| X/XG | 14 | 12.17 (+3.60) | 28.70 (+25.83) | 28.45 (+25.60) | 28.82 (+26.36) |
| X/XGt | 20 | 4.96 (-4.62) | 5.33 (-5.04) | 5.23 (-5.01) | 6.07 (-5.32) |
| X/XY | 19 | 4.13 (+1.30) | 3.22 (+0.18) | 3.46 (+0.90) | 3.81 (-1.51) |
| L3 | 16 | 4.28 (-3.25) | 4.63 (-3.73) | 4.74 (-3.95) | 4.23 (-0.89) |
| L3/L3-1 | 10 | 4.20 (-2.85) | 4.42 (-3.20) | 4.71 (-3.55) | 3.62 (+0.66) |
| L3/L3-2 | 6 | 4.41 (-3.92) | 4.96 (-4.62) | 4.80 (-4.62) | 5.09 (-3.47) |
| Y2 | 10 | 4.38 (+4.04) | 2.09 (+1.26) | 2.79 (+2.23) | 1.70 (+0.32) |
| Y2/Y2-pair | 6 | 4.50 (+3.95) | 2.42 (+1.16) | 3.00 (+2.12) | 2.15 (+0.34) |
| Y2/Y2-control | 4 | 4.19 (+4.16) | 1.48 (+1.40) | 2.44 (+2.39) | 0.55 (+0.29) |
| G2 | 14 | 19.27 (+17.09) | 34.74 (+32.65) | 34.78 (+32.87) | 32.31 (+29.74) |
| G2/G2-NB56 | 14 | 19.27 (+17.09) | 34.74 (+32.65) | 34.78 (+32.87) | 32.31 (+29.74) |
| G2t | 14 | 6.52 (-6.36) | 6.34 (-6.17) | 6.01 (-5.92) | 8.96 (-8.64) |
| G2t/G2t-NB56 | 14 | 6.52 (-6.36) | 6.34 (-6.17) | 6.01 (-5.92) | 8.96 (-8.64) |
| **all** | 135 | 8.62 (-0.20) | 15.21 (+3.13) | 15.18 (+3.26) | 14.86 (+2.66) |

Equal to verify-e220d's pooled family table (128 groups, 0 differ).

## 7. Q234's MM1-v3.3 candidates pooled (REPORTED, never a registered rule; as verify-e220d scored them)

Frozen and posted before any E220 datum (05:47:36 and 06:05:46 PST): BLIND. verify-e220d's pooled figures, quoted as it scored them (each candidate's files checked against its post first; the same sign test and each case's own arm's tie):

- **'MM1-v3.2 + gemmLnc term AF4'**: pooled head to head against MM1-v3.2 (candidate closer / MM1-v3.2 closer / ties): the wall cycles TOO FEW 0/0/156; the counter's mean TOO FEW 0/0/156; seconds TOO FEW 0/0/156; W over idle given t the candidate BETTER 21/4/131, p 9.11e-4; J over idle, t forecast the candidate BETTER 24/3/129, p 4.92e-5. Pooled rms over the changed points, the candidate vs MM1-v3.2: wall 12.40% vs 12.40% (n 28); Wg 5.35% vs 16.12% (n 28); Jf 4.82% vs 16.95% (n 28).
- **'MM1-v3.2 + posimb'**: pooled head to head against MM1-v3.2 (candidate closer / MM1-v3.2 closer / ties): the wall cycles the candidate BETTER 21/9/126, p 0.0428; the counter's mean NOT DECIDED 10/8/138, p 0.815; seconds the candidate BETTER 21/9/126, p 0.0428; W over idle given t TOO FEW 0/0/156; J over idle, t forecast TOO FEW 8/0/148. Pooled rms over the changed points, the candidate vs MM1-v3.2: wall 4.59% vs 4.81% (n 50); Wg 4.22% vs 4.22% (n 29); Jf 4.89% vs 5.60% (n 29).
- **'MM1-v3.2 + L3S'**: pooled head to head against MM1-v3.2 (candidate closer / MM1-v3.2 closer / ties): the wall cycles MM1-v3.2 BETTER 11/27/118, p 0.0139; the counter's mean MM1-v3.2 BETTER 10/28/118, p 0.0051; seconds MM1-v3.2 BETTER 11/26/119, p 0.0201; W over idle given t TOO FEW 0/0/156; J over idle, t forecast TOO FEW 1/2/153. Pooled rms over the changed points, the candidate vs MM1-v3.2: wall 6.99% vs 6.95% (n 78); Wg 8.01% vs 7.96% (n 78); Jf 8.55% vs 8.42% (n 78).

So, in verify-e220d's words: "AF4 is the strong one (arm A E1-E4 would PASS"; "posimb has the right sign at half size"; "L3S fixes L3 but loses pooled wall". These readings choose nothing: they are REPORTED beside E220's registered rules, never a registered rule.

## 8. verify-e220d's pooled reading, beside (its own code; verdict HOLDS)

verify-e220d made the registered pooled reading first, by its own code (importing nothing from the kit or the scorer) and by the frozen scorer's two-arm run, and the two agree on all 53 verdicts and on every pooled count and p (12 of 12). Its result: HP1 wall 74/40/42, p 0.0019; HP4 W given t 68/26/62, p 1.7e-5; HP5 J with t forecast 69/14/73, p 6.8e-10; HP6 wall NOT DECIDED, 65/45/46, p 0.070; CXP-T LARGER HERE, 92 twins, 20/8/64, p 0.036; CXP-E LARGER HERE, 70 twins, 42/16/12, p 0.00086. This note's table is the frozen scorer's, equal to those.

## 9. Findings, answered as dated clauses (Fri 20 Nov 2026, after the data; post hoc; nothing re-scored)

1. **The one-arm files' pooled lines are not this reading** (card-e220a's and card-e220b's findings, info; verify-e220d's finding 8): arm A's file reads HP1-HP5 MM1-v3.2 BETTER and CXP-T TOO FEW, CXP-E NOT DECIDED over arm A's points alone; arm B's reads HP4 MM1-v3 BETTER and CXP-T, CXP-E LARGER HERE over arm B's alone. The registered reading over both arms is section 3's.
2. **CXP-T rests on arm B alone** and **CXP-E carries note 1's rate of 0.4986 at equal rms** (verify-e220d's finding 4, info): read them as section 4 says, with E220.md section 8's caution ("E220 tests never-run configurations on known cards, not a held-out card.").
3. **HP4 pooled reads MM1-v3.2 BETTER (68/26/62) while arm B's H4 reads MM1-v3 BETTER (10/24/38)** (verify-e220d's finding 4, info): arm A's lead (58/2/24) outweighs arm B's. Both are as registered.

## 10. What this note does not do

It changes no committed file, datum, forecast, rule, band, label or scorer; the pooled verdicts are the frozen scorer's, run once on the two committed measured sides with step 13's arguments. It adds no forecast, reads no box's disk and no model session's folder, and opens none of the model session's sealed numbers. The candidates' figures are verify-e220d's (REPORTED). Not re-made here: the registration's power simulations and dated note 1's simulation (its printer is re-run; its rates are the note's).

## 11. `SHA256SUMS-note17`

Five lines, in this order: `scores-e220-pooled.json`, `scores-e220-pooled.txt`, `cx-beside-e220-pooled.txt`, `README.md.dated-note-17.md`, `SHA256SUMS-note16`, each with its sha256; `sha256sum -c SHA256SUMS-note17` from this directory reads 5 of 5 OK.

SPDX-License-Identifier: Apache-2.0
