# The footing law's post hoc study, dated note 1 (post hoc): corrected readings for one die coordinate, card 1's earlier fits, the estimators, FL7's companion, E60's referral and the runner, with the quotes for the records

*Beside [`README.md`](README.md) (`0f4204e9`, committed 23:16:59 PST Thu 5 Nov 2026; its "about 22:20-23:30 PST" overruns its own commit).
It edits none of the study's files (`SHA256SUMS` 40 of 40 still pass) and changes no committed output: every one re-runs byte for byte
(N7). Written Fri 6 Nov 2026 (week 45), from about 00:00 PST until its commit, on the Intel, desk only, by the lane fix-heat-q145a of
Q145(a), round A, from the faults an adversarial verifier found (one major, seven minor). **Post hoc, like the study:** the sessions,
arms and laws it reads were all seen before. The registration's side is the footing law's dated note 1
([`FOOTING-LAW.md.dated-note-1.md`](../../../../tools/claims-v3/footing-law/FOOTING-LAW.md.dated-note-1.md)), committed with it; its
section numbers N1-N6 are cited here as "the registration's N1" and so on.*

## N1. "Two sensors, one law" (section 2) and "within 0.003" (section 4)

Section 2 sets FL1's 0.3509 W/°C at 58 °C (the firmware's whole degree) beside E97's 0.3498 (the 34-sensor mean, which reads 0.75-0.96
°C higher at rest), and section 4 says "the same law within 0.003 W/°C". **Read in one coordinate, E97's rests sit 0.005-0.015 W/°C
above FL1 at 55-62 °C** (0.012 W/°C rms by FL1's own method, 0.009 over every degree). That is about what FL1's own two seasons differ
by (E44 against E71, 0.016 rms, up to 0.029 W/°C), and FL2's registered 0.01 line is exceeded over part of the range (the registration's
N1, with its table). The loop gain of section 4 is unchanged: the chain keeps E97's law in its own coordinate.

## N2. Card 1's row of section 1's table

"The same, three cycles (never fitted before) | none" becomes: *"the same, three cycles; committed as a residual: E44's IDLE-a
(`2026-09-25-claims-v3/results/idle.json`, `921e3158`) fitted them over aifoundry2's September law, 0.237 W/°C over 57-81 °C (with
IDLE-c, the metered rails 0.767 W/°C at 75-80 °C, and IDLE-e, the SRAM rail 0.051 W/°C)"*. Re-joined to that law, IDLE-a's residual
gives 0.5401 / 0.5209 / 0.5324 W/°C per cycle at 58-62 °C against this study's 0.5495 / 0.5183 / 0.5313 (`fix-note1.json` ›
`A_card1_E44_items`). The 0.5313 stands as card 1's first board-power slope at 58-62 °C stated as such.

Section 2's "Card to card" sentence ends "Process spread, not voltage". It should read *"process spread or the idle state its older
firmware sets (E44's note: card 1 runs 1.2.0, the other two 1.3.1, and the firmware sets the idle state), not voltage"*.

## N3. The estimators (section 2), worded to the evidence

- **The rests.** "A Monte Carlo with the law's slope reproduces the pattern" becomes: *"a Monte Carlo with the law's slope matches the
  OLS (0.21-0.22, 0.28-0.31), not the reverse regressions (0.53-0.65 and 0.55-0.70 against the observed 0.455 / 0.512); the rests alone
  admit any slope in [0.206, 0.455] (aifoundry3) and [0.313, 0.512] W/°C (card 1), the law among them"* (`sim.json`; `fix-note1.json` ›
  `D_quoted`).
- **The in-run fits.**
  - *The series.* Section 2 quotes E171's and E172's trace-start series from the dips-kept variant (0.290 → 0.233 → 0.183; 0.395 →
    0.377 → 0.303) beside the dips-removed own slopes. The dips-removed series are 0.285 → 0.225 → 0.177 and 0.403 → 0.374 → 0.302
    (`inrun.json`).
  - *The Monte Carlo.* "The Monte Carlo gives 0.29-0.59 of the true slope" is withdrawn as an account of the data. A model of the
    per-run estimator with only the whole-degree quantisation and sensor noise (`sim_attenuation.py`'s), its rise and time constant
    fitted to each session's committed mean profile (`profile.json`) and its truth set to the law, reads **1.8-3.2 times below the
    observed medians on E171, E172 and E60's aifoundry3 runs, and falls faster with a later start than they do** (`fix-note1.json` ›
    `C_inrun_model`; the model reproduces `sim.json`'s grid point, 0.1549 against 0.1555). So quantisation does not account for the
    in-run values, and something else lifts them; neither candidate is measured (the reading lagging the hotter parts of the die,
    power drifting within a run).
  - *The ensemble* moves with the start time: E171 0.441 → 0.378 → 0.305 from 1.0 / 1.5 / 2.0 s; E60 on aifoundry3 0.425 → 0.450 →
    0.541; E172 0.621 → 0.602 → 0.545 (`law.json` › `ensemble_inrun`). It straddles the law (0.36) on aifoundry3 and sits above it
    (0.49) on card 1; with the per-run medians it brackets the law and does not measure it.
- **The reading, then:** *the footing's and the in-run slopes are consistent with one quasi-static law per card (inside the rests'
  bracket; the per-run medians below the law and the ensemble at or above it), not measured in-run; the blind tests are FL5(c) and the
  first FL3-armed session.* The lane's "physically identified" and "answered at the desk" are withdrawn.
- **E60's 0.442 W/°C at 800 MHz.** "So it is a referral for its own use … kept there as the check at that point, not a law" becomes:
  *"kept unchanged in `surface_hpl.py` because the governor model was fitted with it; an in-run estimate whose relation to the
  quasi-static law is not identified, so the 800 MHz referral may be understated; a quasi-static cooling at 800 MHz needs a governor
  move, which waits on his word"*. Post hoc and untested: where the law is known, the same estimator from 0.8 s reads 0.56-0.82 of it.
  At that ratio the quasi-static slope at 800 MHz and 617 mV would be about 0.54-0.79 W/°C, +0.35 to +1.2 W over a 3.5 °C window rise.
  The quantisation-only model run on aifoundry2's own profile (rise 4.75 °C, τ 1.92 s) implies 0.52-0.60, rising with the start, but
  that model does not reproduce the 600 MHz sessions (above), so it sizes nothing.

## N4. FL7 (section 3): what the companion shows, and what the table left out

- **The first-order identity.** To first order the one-footing companion is the registered footing's errors times f. E171, 64 tiles:
  the companion's M10 rms 0.1670 W against f × registered 0.1664, M9 0.2265 against 0.2323, the errors correlated 0.971. E172: M10
  0.1675 against 0.1683, M9 0.2182 against 0.2370, correlation 0.964 (`fix-note1.json` › `B_FL7`). So the companion shows that a
  footing shared by the model and the data leaves the verdicts in place. It does not test the law.
- **The plain law arm's other changes,** beside E171's P2 FAIL → PASS (0.238 → 0.215 W) and LG NOT SEPARATED → GAIN:
  - E172's **M1i reads WORSE** on the law arm (+0.0093 W [+0.0014, +0.0191]; NOT RESOLVED +0.0086 on the registered footing);
  - E172's A1 BETTER → NOT RESOLVED and B2 PASS → FAIL HIGH, both already in section 3's table;
  - E172's LG NOT SEPARATED → BOTH;
  - E172's int8 rms (P3) rises 0.125 → 0.216 W (both PASS), the int8 mismatch that no session scale absorbs;
  - on E171, P3 rises 0.131 → 0.150 W.
- **Withdrawn:** the bold "So M1 BETTER and term a's carry (A1, KA, pooled KA) survive on the leakage law, on both cards, once the model
  and the data share one footing", and "The 5 Nov caveat … was mostly the arms' mismatch" as a replacement for the caveat. **The
  reading for the records** keeps the 5 Nov caveat and adds a dated post hoc clause (the quotes, below).

## N5. The first blind tests (section 5)

- **The law:** FL5(c) as the registration's N1 fixes it. M11's next aifoundry3 session's rests are read per whole firmware degree
  against FL1 by the same estimator at the same degrees and weights (PASS within ±0.02 W/°C). Beside it, the rests on the 34 codes are
  read against E97's law. It is no longer "its slope at 52-58 °C within ±0.02 W/°C of 0.280-0.351", a figure taken on the 34-sensor
  mean and set against a firmware-degree law.
- **The footing's consequences:** E178, the next 600 MHz kinds session on aifoundry3, was registered before the rule and keeps its
  registered footing (the registration's N2). The first FL3-bound session that scores M1, A1 and KA is pool 8's day 2 or pool 9, not
  yet registered.

## N6. Times

This README was written 22:20-23:16 PST and committed at 23:16:59.

## N7. The runner, and a docstring

- **`run_posthoc.sh` leaves out `rederive_e97.py`,** though "Files and how to reproduce" says it re-runs everything and lists
  `e97-law.json`. [`run_posthoc-v2.sh`](run_posthoc-v2.sh) (new) runs `run_posthoc.sh`, then `rederive_e97.py`, then this note's
  `fix_note1.py`, and compares every output with its committed copy, E172's three scored files after the README's label for the one
  scratch path:
  ```bash
  bash docs/reports/data/2026-11-05-q145a-footing-law/run_posthoc-v2.sh <a scratch directory outside the repository>
  ```
  Run Fri 6 Nov 2026 at 00:24-00:27 PST from the lab clone's top, before this note's commit and with its files in place: all 31 of
  the study's committed outputs (6 here and 25 in `fl7/`, `e97-law.json` among them) and this note's two match byte for byte, E172's
  three scored files after the label (exit 0).
- **`rederive_idle.py`'s docstring, line 14,** is superseded by: *"Of each cycle's marks it reads the cool_start mark alone."*

## Quotes for the records (each labelled)

1. **The footing caveat** (05, the kinds page's section 11 item 6), kept and extended: *"M1 BETTER, A1 BETTER and KA PASS on the
   registered footing (Q139(u)'s, frozen beforehand); with the session's own leakage slope, M1, M1f and A1 read NOT RESOLVED and KA
   FAILS (blind). Post hoc (6 Nov): those arms mixed footings (data at the session's slope, M9 and the a-priori arm at the registered
   one); to first order a footing shared by model and data is a common gain, under which a first-order companion reads M1 BETTER (E171
   by a hair: its interval ends at −0.004 W), A1 BETTER and KA PASS on both cards; that shows the verdicts do not hang on a shared
   footing, not that the leakage law is right; the exact refit, M10 on the law, is owed."*
2. **The law** (post hoc): *"one quasi-static leakage law per card at its idle operating point (aifoundry3 0.351 W/°C at 58 °C on the
   firmware reading, nine dedicated cycles; card 1 0.476, three); read in one die coordinate, E97's rests sit 0.005-0.015 W/°C above
   it at 55-62 °C, about what its own two seasons differ by; the in-pass and in-run slopes are consistent with it but not measured
   in-run; only it closes E97's steady heat balance (0.99-1.00)."*
3. **Card 1** (post hoc): *"its first board-power slope at 58-62 °C stated as such, 0.531 W/°C (E44's IDLE-a fitted the same cycles in
   September as a residual over aifoundry2's law)"*.
4. **E60's referral:** *"kept in the governor model, which was fitted with it; possibly understated at 800 MHz; open until a
   quasi-static cooling there, a governor move that waits on his word."*

## Files (this note's hash list: `SHA256SUMS-note1`)

| file | what |
|---|---|
| `README.md.dated-note-1.md` | this note |
| `fix_note1.py` | A card 1's E44 items against FL1's cycles; B FL7's identity and the arms' changed rules; C the in-run estimator's model, calibrated where the law is known; D the series quoted. `python3 -B docs/reports/data/2026-11-05-q145a-footing-law/fix_note1.py . <out.json>` from the lab clone's top |
| `fix-note1.json`, `fix-note1.txt` | its output and printout |
| `run_posthoc-v2.sh` | every step of the study and the byte-for-byte comparison (N7) |

SPDX-License-Identifier: Apache-2.0
