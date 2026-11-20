# blind-e219-scores: dated note 1, the folder as landed and verify-blind-e219's findings on it

*Fri 20 Nov 2026, Pacific time. Written by the lab's lane land-blind-e219 (round Q232) at 01:27 PST for this folder's commit, after verify-blind-e219 held it WITH FIXES (00:32-01:05 PST). Desk only: no card, no device, no simulator. Interpreter `/usr/bin/python3` 3.12.3 (-I -B), numpy 1.26.4 for the model's loader, single-threaded in the round's CPU slots. This note changes no file of the folder and no number, forecast, rule or verdict. Labels: **measured** is E219's committed data, **blind** the forecasts frozen before any E219 datum, **desk** this lane's re-run, **post hoc** its re-counts, which decide nothing.*

## What is committed here

- **The folder** is blind-e219's land byte for byte: 41 files and `SHA256SUMS` (sha256 `ccf3bed905531556...`, 41 of 41 OK), written at 00:29 PST, after the measured-conditions forecasts were hashed (00:12:50), the scorer was hashed (00:21:05, `scripts/s03_score.py` as run: `28039e171fbf72672452ccabcee9e0f222148150fc821a58c736ef148a00702b`) and the data were read and scored (00:21:14).
- **The declaration it scores** is `../blind-e219/`, committed just before as 5877bc1a, so this README's links to it resolve.
- **The verification.** verify-blind-e219 re-derived this score with its own code: the declared test PASSES, part A's 14 cells are equal on both footings with the same misses, and all five sessions are BLIND (their first card commands came 68.25 to 232.31 minutes after the freeze post #14.1.1). Its own forecasts at the measured conditions equal 18,232 of the 18,270 fields here bit for bit; the other 38 differ by one unit in the last place (a pass's seconds and joules over idle of the three count controls at the 6 subset cases). Its own scorer gives the 486 headline cells and 180 comparison cells equal, and 11,259 per-case values equal to their 6 digits.
- **This note adds one new file**, itself, and `SHA256SUMS-note1` with its sha256. It edits no file.

## A full-precision re-run of the hashed scorer (desk)

This lane ran the hashed scorer once more on the same committed data (GitHub main e97216b7, read only), in its own folder, with only the two lines that round its statistics changed (`rms_pct`, `bias_pct` to 3 decimals; `rms_W`, `bias_W` to 4), and the post hoc step with its six roundings removed; then the README builder as run, on those outputs:

- **`scores/scores-blind-e219.json`:** 33,089 leaves equal, and 30,516 statistics whose full-precision value rounds back to the value here; nothing else differs but the two run-time fields. **`scores/posthoc-e219.json`:** 313 equal, 271 round back, nothing else. The cases, runs and out-of-domain tables are byte-equal. So every verdict, count, p and miss set here is the full-precision one.
- **T3 against T1:** 162 rms and bias statistics compared at full precision, every model, scope and selection; the largest difference is 1.1e-14 percentage points. The README's "the same rms and bias on every scope: True" (line 69) was decided on the 3-decimal statistics; it holds to floating-point noise.
- **The README rounds 20 figures twice**: stored at 3 or 4 decimals, then printed at 2, 3 or 1. verify-blind-e219 named 14 of them; the re-run finds 6 more. Read each as the full-precision column says:

| README line | the figure | printed | read as | full precision | named by the verifier |
|---|---|---|---|---|---|
| 60 | headline table (no twin, pooled): MM1-v3.1, J over idle given t (E1), bias | -1.78 | -1.79 | -1.7854 | yes |
| 61 | headline table (no twin, pooled): MM1-v3, E1, watts rms (the 2 watts cases) | 0.011 | 0.010 | 0.01048 | yes |
| 61 | headline table (no twin, pooled): MM1-v3, J over idle with t forecast (E2), watts bias | -0.009 | -0.010 | -0.00955 | yes |
| 61 | headline table (no twin, pooled): MM1-v3, J at rest given t (E3), rms | 1.01 | 1.02 | 1.0153 | yes |
| 62 | headline table (no twin, pooled): MM1-v2, E2, rms | 7.96 | 7.95 | 7.9546 | yes |
| 63 | headline table (no twin, pooled): v3.1+contention, E1, bias | -1.78 | -1.79 | -1.7854 | yes |
| 64 | headline table (no twin, pooled): ctrl N1+N2, E1, bias | -1.78 | -1.79 | -1.7854 | yes |
| 64 | headline table (no twin, pooled): ctrl N1+N2, E2, watts rms | 0.011 | 0.012 | 0.01152 | yes |
| 65 | headline table (no twin, pooled): ctrl G1, E1, bias | -1.78 | -1.79 | -1.7854 | yes |
| 65 | headline table (no twin, pooled): ctrl G1, E2, bias | -2.10 | -2.09 | -2.0949 | yes |
| 66 | headline table (no twin, pooled): ctrl G1+N1, E1, bias | -1.78 | -1.79 | -1.7854 | yes |
| 66 | headline table (no twin, pooled): ctrl G1+N1, E2, rms | 5.00 | 5.01 | 5.0051 | yes |
| 67 | headline table (no twin, pooled): ctrl F1-layout-blind, E1, bias | -1.78 | -1.79 | -1.7854 | yes |
| 73 | per card (no twin): aifoundry1 card 1, E3, bias | -0.55 | -0.54 | -0.5446 | yes |
| 76 | the twins paragraph: MM1-v3.1 on all cases (twins in), E1, watts rms (the 4 watts cases) | 0.026 | 0.027 | 0.02652 | no |
| 111 | by class (MM1-v3.1, no twin): C16R, E3, rms | 0.67 | 0.66 | 0.6649 | no |
| 126 | by class, the three models: C16R, MM1-v3.1, E3 rms | 0.67 | 0.66 | 0.6649 | no |
| 128 | by class, the three models: CTRL, MM1-v3, wall rms | 0.01 | 0.02 | 0.0153 | no |
| 139 | the R ladder: card 0 fp16 zeros, R 8, MM1-v3.1's wall error | -0.9 | -1.0 | -0.954 | no |
| 199 | the nominal footing (REPORTED): MM1-v3.1 no twin, pooled, wall bias | -0.99 | -1.00 | -0.9952 | no |

Percentages are in % and watts in W, as the README prints them. No rule cell, count, p or verdict depends on any of them. blind-e219's own result files, outside this folder, print the same figures.

## verify-blind-e219's findings on this folder, answered

1. **Double-rounded figures (nit).** Answered by the table above: the 14 cells the verifier named and 6 more, each with its full-precision value.
2. **Card 1's time rules rest on the C16R ladder (info, post hoc).** Re-counted here from `cases/scores-blind-e219-cases.csv` by the declared rule (a case enters a rule unless it is MM1-v3.1's twin for that rule's kind; it passes within the rule's band, or within the watts band at a watts case; PASS needs 90% of at least 10 cases). With every class the re-count gives all 14 of part A's cells, misses included, exactly. Without the C16R ladder's cases (47 on card 1, 26 on card 0):
   - card 1 T1 and T3 read 24/28 (85.7%, under 90%), and T2 26/28;
   - card 0 passes every rule (T1, T3 and E4 25/26; the others 26/26), and so does every energy rule on card 1 (E1 and E2 31/32, E3 32/32, E4 30/32);
   - the GAP class alone reads card 1 T1 16/20, as the README says.
   The declared rule pools every in-domain class, so the PASS stands; read card 1's time PASS as the ladder's.
3. **The reading of "NO DATA with none" (info).** The verifier confirms the scorer's reading (NO DATA only when no case is compared). The other reading would change only 46 D3 cells, across both footings, from TOO FEW to NO DATA, and no D1 or D2 cell. Nothing changes.
4. **The CTRL tie to E217 (info).** E217 never ran E219's 8 CTRL configurations on the same card, so the declared tie has nothing to compare; this README reports the 4 that ran on the other card (REPORTED). Nothing changes.
5. **MM1-v3.2 (info).** It is not declared, so it is not scored here (it first entered GitHub main after the freeze; see `../blind-e219/README.md.dated-note-1.md`). Nothing changes.

## What the verifier did not check

- blind-e219's inline one-off checks (they are not files), the post hoc R-ladder line fits, and the E217 other-card ratios.

SPDX-License-Identifier: Apache-2.0
