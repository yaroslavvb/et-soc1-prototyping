# Dated note 1 beside README.md (Fri 6 Nov 2026, week 45): the study's Builds-on block, the check the registration promised, and the dip term under amendment A1. POST HOC

*This note sits beside [`README.md`](README.md) and changes nothing in it: the README, `posthoc_dips_q145b.py`,
`posthoc-dips.json`, `posthoc-dips.txt` and `SHA256SUMS` stay as committed in `006c85eb`. **Every figure here is POST HOC.** The
data of E64-E87, E100 and E173-E175 existed before amendment A1 ([`REGISTRATION.md.dated-note-4.md`](../../../../tools/claims-v3/dipterm/REGISTRATION.md.dated-note-4.md),
lab `3002edaf`), and A1's rule was chosen after its author read the dip lane's verifier's Q132(g) check and E173-E175's rings. A
post hoc reading is never a verdict, and no committed verdict changes. The term's first blind test is still the next governed
session that keeps the gaps (number to be assigned). Its time is its commit's. Desk only: no card, lab box or device was
touched.*

On the kinds page, section 11, this belongs to item 6, as the README does.

## Builds on (the study's block, owed since `006c85eb`, and this note's)

1. **Checked:** the prior-work inventory, read Fri 6 Nov 2026 about 03:50 PST. Public rows read: P01, P02, P03, P08, L22, H08,
   H10, H19, H23, H24, H26. The ids are opaque pointers into a private inventory.
2. **Used** (each piece, what is taken, its source):
   - **The dip term and its scorers**: the registration `7a099fb9` with `dipterm.py` and the scorer v2 (`fe4fdf92`), run by the
     study; amendment A1 with `dipterm_a1.py` and the scorer v4 (`3002edaf`), run by this note. Both are imported after a
     check against their hash lists (`SHA256SUMS-1`; `SHA256SUMS-5`, `04dfb746`).
   - **E173, E174 and E175's committed data** (`ed8b5761`, `e5206b5b`, `9f13d7c3`): the launch records, `runs.jsonl`,
     `results.json` (`run_rows`, `score.reported.tiles`, `score.rules`), the 10 Hz telemetry and the SP rings, read with
     [`tools/claims-v3/hpl/sptrace_full.py`](../../../../tools/claims-v3/hpl/sptrace_full.py) (sha256 `58dd8b04…`).
   - **The frozen predictions**: pool 8's `tools/claims-v3/kinds/blind8/predictions-pool8-aifoundry2.json` (`4576fb90`) and
     E175's `tools/claims-v3/e175/predictions-e175.json` (`b3f5e83c`), for each tile's M10 D; M9's aifoundry2 relation
     ([`2026-11-04-q140l-a2-session-terms/m9_a2.json`](../2026-11-04-q140l-a2-session-terms/m9_a2.json), `5b98bd5c`) for the
     board's levels.
   - **E100** ([`2026-11-01-e100-idle-reset/`](../2026-11-01-e100-idle-reset/README.md), `f9fe3f57`, corrections `2e2dea21`): its
     arms, their registered predictions, bands and falls (`results.json` > `arms`).
   - **Q132(g)** ([`2026-11-01-q132-governor-desk/`](../2026-11-01-q132-governor-desk/README.md), `13de3994`): its six sessions'
     committed data (E64, E69, E80, E83, E87, E84), its count (25 falls against 23.5 expected), and `ir_lib.fit_lattice` for the
     rings' lattice on the SP tick (the study's result 5).
   - **The check against earlier measurements of the same quantity**: the dip count against E100's committed arms and
     Q132(g)'s committed count, at the same operating point (the 800 MHz cap, the sparsity host's back-to-back launches). That is
     results 1 and 2 below; the study ran the first and not the second.
3. **Not used:**
   - E165's and E160's dipped passes: not re-scored, owed to a records lane, as registered.
   - The oracle arm and the reference figures that drop dipped passes as predictions: post hoc by construction, and selected on
     the outcome.
4. **Tiers:** public only. Every piece is the lab's committed data or public code at a pinned commit.

## Results first

1. **The check the registration promised: DT-N's formula on Q132(g)'s six sessions** ([`posthoc-dips-a1.json`](posthoc-dips-a1.json)
   > `Q132g_check`). Falls against expected at δ 0.7 ms, and the verdict:

   | session | registered rule | Q132(g)'s rule | A1, all blocks | registered, burst blocks | A1, burst blocks |
   |---|---|---|---|---|---|
   | E64, aifoundry2 | 8 / 2.80 PASS | 2 / 2.07 PASS | 2 / 2.13 PASS | no burst block | no burst block |
   | E69, aifoundry2 | 7 / 1.56 **FAIL** | 2 / 1.10 PASS | 2 / 1.14 PASS | 5 / 0.48 **FAIL** | 1 / 0.39 PASS |
   | E80, aifoundry2 | 35 / 5.36 **FAIL** | 5 / 3.79 PASS | 5 / 4.00 PASS | 3 / 0.91 PASS | 2 / 0.84 PASS |
   | E83, aifoundry2 | 54 / 11.07 **FAIL** | 7 / 9.31 PASS | 7 / 9.53 PASS | 5 / 1.86 PASS | 3 / 1.58 PASS |
   | E87, aifoundry2 | 39 / 3.07 **FAIL** | 5 / 2.24 PASS | 5 / 2.28 PASS | 2 / 0.67 PASS | 1 / 0.42 PASS |
   | E84, card 0 | 45 / 3.44 **FAIL** | 2 / 3.12 PASS | 2 / 3.22 PASS | 7 / 0.59 **FAIL** | 0 / 0.56 PASS |
   | **all six** | **188 / 27.3, 5 FAIL** | **23 / 21.6, all PASS** | **23 / 22.3, all PASS** (P(X ≥ 23) 0.47) | 22 / 4.5 | **7 / 3.8, all PASS** (P(X ≥ 7) 0.09) |

   - **The registered rule fails as registered**, as the verifier found: 188 falls against 27.3 expected. A1 leaves out 165 of
     them (`Q132g_check.pooled.registered_falls_not_counted_by_A1`):
     - 73 lie inside their process's first heartbeat period, at gaps the registered rule leaves out of its own exposure;
     - 55 follow a dither launch (0.65-0.79 GHz) in a run whose ring shows the governor stepping to 600 MHz, or does not reach
       back to the previous dump;
     - 37 lie in processes with an alarm step (32 of them on card 0's E84, at 300 MHz).

     E173-E175 hold none of the first and third kinds; the second kind is result 3's two drops.
   - **Q132(g)'s own rule** through DT-N's formula counts 23 of its 25 falls. The other two (E87's `SUS-08` and E84's `SUS-05`,
     0.62-0.63 s into their processes) lie inside their process's first second. A fall there needs the clock to have carried over
     at 800 MHz from the process before, with no heartbeat in the gap between them (Q132(g)'s item 4). DT-N's structure leaves
     those gaps out of both its count and its exposure.
   - **A1 passes on all six sessions**, with all blocks or with burst blocks only. In burst blocks only, the pooled 7 against 3.8
     expected sits at P(X ≥ 7) = 0.09.
2. **E100 under the same formula**, corrected wording. The README's result 1 says the formula "reproduces each arm's registered
   count". That is withdrawn: **each arm lies inside its band**, but pooled over the five gapped arms (A0, A5, A20, A100, R) the
   formula expects **47.7 falls against 60 seen** (z 1.77, P(X ≥ 60) = 0.048), so its expectation runs about a fifth under the
   pooled count. A100's 25.9 sits below E100's own registered 29.78. A1 reads E100 exactly as the registered rule does: every E100
   process is clear.
3. **E173, E174 and E175 under A1** (`posthoc-dips-a1.json` > `sessions`). The scope: E173 holds 131 clear processes of 165 (20
   rings do not reach back to the previous dump, 14 show a step to 600 MHz); E174 126 of 126; E175 96 of 126 (20 with steps, 10
   not reaching back). No process holds an alarm step.
   - **A1 drops two of the 16 falls.** E173's `BURST-141` (`fp16.u8_tdist_93475b`; the launch before it at 0.764 GHz) and E175's
     `BURST-68` (`fp32.e5c10_ar_i_t10_adc630`, 0.683 GHz) lie in runs whose rings show the power arm stepping to 600 MHz three
     times. Both falls sit on the lattice of their session's other falls (0.89 and 0.17 ms off;
     `sessions.*.loo_residuals_registered_falls`), so each was probably an idle reset arriving while the power arm held 600 MHz or
     was about to. A1 counts neither, by design: from the launch clocks the two causes cannot be told apart.
   - **DT-N:** E173 5 falls against 6.11 expected (band 1-13), E174 6 against 5.79 (1-12), E175 3 against 4.40 (0-10): **PASS ×3**,
     as a rate check.
   - **DT-L:** E173 4 of 4 later falls predicted (PPV 0.57): **PASS**. E174 4 of 5 (PPV 0.57): **PASS**. E175 **NOT SCORED**: its
     calibration now starts at `BURST-87`, which leaves 2 later falls (both predicted, at P 0.65 and 0.96).
   - **The rules on the predicted clock**, each with its Monte Carlo standard error (A1-4: 8 batches of 500 draws):

     | rule (line) | committed (none) | count | **seq, the term** | oracle | registered rule, seq, at A1-4's draws | the study (seq, one seed of 400) |
     |---|---|---|---|---|---|---|
     | E173 P8-A2-F2 (rms ≤ 4.540 MHz) | 7.012: FAIL | 6.543 ± 0.015: FAIL | **2.066 ± 0.024, mean −0.35: PASS** | 0.671 | 1.666 ± 0.026 | 1.582 |
     | E174 P8-C0-F (rms ≤ 4.540 MHz) | 4.543: FAIL | 4.248 ± 0.014: PASS | **2.804 ± 0.013, mean +0.74: PASS** | 1.901 | 2.933 ± 0.015, +0.91 | 2.916 |
     | E175 E175-A2-G (rms ≤ 4.0, \|mean\| ≤ 2.0 MHz) | 4.492, +0.12: FAIL | 4.853, +1.66: FAIL | **5.183 ± 0.011, mean +2.07: FAIL** | 4.464, +2.03 | 5.157 ± 0.015, +1.90 | 5.146, +1.97 |
     | E175 E175-A2-F2 (rms ≤ 5.288 MHz) | 1.239: PASS | 2.920: PASS | **3.180 ± 0.018: PASS** | 3.212 | 2.758 | 2.938 |
     | E173 P8-A2-Bp (\|mean\| ≤ 0.5, rms ≤ 1.0 W) | 1.094: FAIL | 1.128: FAIL | **0.894 ± 0.001, mean +0.18: PASS** | 0.838 | 0.884 | 0.885 |
     | E175 E175-A2-Bp (the same) | 0.668, +0.53: FAIL | 0.891, +0.79: FAIL | **0.918, mean +0.79: FAIL** | 0.813, +0.72 | 0.896, +0.77 | 0.910, +0.78 |

     No figure lies within two standard errors of its line. **Reported, never verdicts:** seq-gc reads E175's G at 4.765 ± 0.007
     (mean +1.42), still over its 4.0 line. seq-lag (the board at a 0.17 s lag) reads E173's Bp at 0.873 W and E175's at 0.887 W.
   - **What moved under A1**, read against the registered rule at the same 4,000 draws (`sessions.*.registered_rule_at_a1_draws`):
     - E173's F2 rescue reads 2.07 MHz under A1, against 1.67 under the registered rule. So the study's 1.58 owed about 0.08 MHz to
       its single seed, which sat at the favourable end. A1 adds about 0.40, because `BURST-141`'s fall leaves the calibration and
       the later falls are placed from fewer earlier ones (its next later fall is predicted at P 0.54).
     - E174's C0-F improves under A1-5: 2.80 against 2.93 MHz, mean +0.74 against +0.91.
     - E175's G worsens slightly (5.18 against 5.16), because its calibration starts 19 bursts later.
     - The pinned-clock rescue (F2, C0-F) and E173's Bp still hold post hoc, and the governed clock is still not rescued.
4. **The period from each session's falls**, with the card's prior (as the registration fits it) and without it, registered
   falls: E173 **1000.0104 ± 0.0006 ms with the prior, 1000.0105 ± 0.0007 without**; E174 1000.0194 ± 0.0007 and 1000.0198 ± 0.0011;
   E175 1000.0097 ± 0.0009 and 1000.0098 ± 0.0012. Each lies within its card's prior (aifoundry2 1000.0095 ± 0.0015, card 0
   1000.0190 ± 0.0010). The study's README quotes the first figure of each pair, so read those as "with the card's prior".
5. **The SP pass under the 10 Hz sampler**, as the mean time between `board_w` changes at 800 MHz in a run (median over runs, p10
   to p90): **E173 164.9 ms (156.0-175.2), E175 166.8 ms (160.1-183.5)** on aifoundry2, and E174 161.9 ms (157.3-175.1) on card 0.
   That agrees with findings 14's 156 ms (E41, line 794), not with the 0.24-0.26 s of aifoundry3's pass. A1-6's 0.17 s lag arm
   uses it.
6. **Card 0's fall, before and after A1-5** (`sessions.E174.fall_costs`; in sample, because E174's falls enter A1-5's pooled
   climb, and E114's alone give nearly the same: c7 0.064, c8 0.265 s). On the four falls that run their full length, the
   measured cost is 44.9, 46.0, 42.0 and 44.9 MHz. The term reads 45.1, 49.8, 45.0 and 49.5 MHz with the registered climb (mean
   +2.9 MHz, +6.5%, and never low), and 41.5, 46.3, 41.5 and 46.1 MHz with A1-5's (mean −0.6 MHz). aifoundry2's falls are
   unchanged (the climb is the registered one there).
7. **Still open, post hoc: the late climbs at a process start.** The seq arm expects 0.12, 7.20 and 0.55 late climbs on E173, E174
   and E175, against 3, 3 and 5 seen in the telemetry. That is under-predicted on aifoundry2 and over-predicted on card 0, where the
   excess adds to C0-F's positive mean (+0.74 MHz). A re-read of the climb at a process start, on both cards, is owed before card
   0's blind session; A1 leaves the start climb as registered.

## What this changes

- **For the records** (quote these, labelled POST HOC):
  - the registered DT-N fails on Q132(g)'s sessions (188 against 27.3); A1's rule passes there (23 against 22.3);
  - under A1 the term turns E173's F2 (7.01 to 2.07 ± 0.02 MHz) and E174's C0-F (4.54 to 2.80 ± 0.01 MHz) from FAIL to PASS,
    and E173's Bp (1.094 to 0.894 W);
  - it does not rescue E175's G (5.18; seq-gc 4.77, reported);
  - DT-N PASSES on all three as a rate check; DT-L PASSES on E173 and E174, and E175's is NOT SCORED.
- **The committed verdicts stand.** Never "the dips are solved" or "F2 passes".
- The registration's own wording fixes are in dated note 5 beside it (`04dfb746`).

## Files

| file | what |
|---|---|
| `README.md.dated-note-1.md` | this note |
| [`posthoc_dips_a1.py`](posthoc_dips_a1.py) | the re-run: results 1-7; it imports `dipterm.py`, `dipterm_a1.py` and `score_dipterm_v4.py` after checking `SHA256SUMS-5` |
| [`posthoc-dips-a1.json`](posthoc-dips-a1.json) | everything, per session and arm, with every tile and each figure's batch values |
| [`posthoc-dips-a1.txt`](posthoc-dips-a1.txt) | the printed summary |
| [`SHA256SUMS-1`](SHA256SUMS-1) | the files above, plus every file `SHA256SUMS` lists and `SHA256SUMS` itself, all unchanged |

Rebuild from the repository's top level (Python 3, no third-party module; about a minute on one core):

```bash
python3 -I -B docs/reports/data/2026-11-06-q145b-dips-posthoc/posthoc_dips_a1.py --lab . \
  --out docs/reports/data/2026-11-06-q145b-dips-posthoc/posthoc-dips-a1.json > docs/reports/data/2026-11-06-q145b-dips-posthoc/posthoc-dips-a1.txt
```

SPDX-License-Identifier: Apache-2.0
