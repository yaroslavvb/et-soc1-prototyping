# Q145(b), post hoc: the dip term on E173, E174 and E175. The in-session calibration predicts 12 of 13 later falls; F2 and C0-F pass with it, and G does not

*Fri 6 Nov 2026 (week 45), about 02:55 PST, on the Intel, desk only. No card, lab box or device was touched.*

**Every figure here is POST HOC.** E173's, E174's and E175's data (lab `ed8b5761`, `e5206b5b`, `9f13d7c3`) existed before the term was
registered: [`tools/claims-v3/dipterm/REGISTRATION.md`](../../../../tools/claims-v3/dipterm/REGISTRATION.md), lab `7a099fb9`, 02:36:55
PST. Its scorer's v2 followed by dated note 1 (`fe4fdf92`), before any figure of the term was read. None of these sessions set a
parameter of the term: the parameters are E100's, Q132(g)'s and E114's. A post hoc reading is never a verdict, and none of the
committed verdicts changes. The term's first blind test is the next governed session that keeps the gaps (number to be assigned).

On the kinds page, section 11, this belongs to item 6 (a power model across kinds: the governed clock rules on aifoundry2 and card 0).

## Results first

1. **The count holds on all three sessions.** DT-N's expected falls over the eligible gaps:

   | session | eligible gaps (mean stamp gap) | expected at δ 0.0 / 0.7 / 1.2 ms | band | seen | DT-N |
   |---|---|---|---|---|---|
   | E173, aifoundry2 | 2,101 (2.63 ms) | 5.53 / 7.00 / 8.05 | 1-14 | 6 | PASS |
   | E174, card 0 | 1,690 (2.73 ms) | 4.61 / 5.79 / 6.64 | 1-12 | 6 | PASS |
   | E175, aifoundry2 | 1,567 (2.60 ms) | 4.07 / 5.17 / 5.95 | 1-11 | 4 | PASS |

   - The stock-take's count, with the gaps after the cap at δ 0, read 5.67 / 4.49 / 4.13 against the same 6 / 6 / 4.
   - Over the three sessions, 16 falls were seen against 14.2 expected at δ 0 and 18.0 at δ 0.7.
   - The same formula on E100's committed session reproduces each arm's registered count. A0 expects 0.90 and saw 3 (E100: 0.96,
     band 0-4). A5 expects 3.19 and saw 3. A20 expects 9.14 and saw 10. A100 expects 25.9 and saw 33, inside its band of 16-36. N
     expects 0 and saw 0. R expects 8.63 and saw 11 by the kernel rule (E100: 12 by its sampler rule, 10 by its kernel counters).
     Every arm PASSES.
2. **The in-session calibration predicts which bursts dip.** The lattice is fitted on each session's earlier falls only, and DT-L
   PASSES on all three sessions:
   - E173: 5 of 5 later falls (P = 0.72-0.87), PPV 0.63;
   - E174: 4 of 5 (P = 0.43-0.99), PPV 0.57;
   - E175: 3 of 3 (P = 0.67-0.96), PPV 1.0.

   No fall lay off the lattice.
3. **The clock rules on the predicted clock:**

   | rule (line) | committed (arm none) | count | **seq, the term** | oracle (all the falls) | dropping the dipped passes (selected on the outcome) |
   |---|---|---|---|---|---|
   | E173 P8-A2-F2 (rms ≤ 4.540 MHz) | 7.012, mean −2.66: FAIL | 6.533: FAIL | **1.582, mean −0.23: PASS** | 0.413 | 0.298 (every pass with a fall); 0.073 (every tile with a dipped pass) |
   | E174 P8-C0-F (rms ≤ 4.540 MHz) | 4.543, mean −1.60: FAIL | 4.382: PASS | **2.916, mean +0.90: PASS** | 2.024 | 0.797; 0.0 |
   | E175 E175-A2-G (rms ≤ 4.0 MHz and \|mean\| ≤ 2.0 MHz) | 4.492, mean +0.12: FAIL | 4.819, +1.71: FAIL | **5.146, mean +1.97: FAIL** | 4.408, +2.04 | 3.816 (every pass with a fall) |
   | E175 E175-A2-F2 (rms ≤ 5.288 MHz) | 1.239, +0.65: PASS | 2.971, +2.78: PASS | **2.938, +2.45: PASS** | 2.836 | |

   **Bp with the dipped launches carried** (|mean| ≤ 0.5 W and rms ≤ 1.0 W):
   - **E173: 1.094 W rms (FAIL) becomes 0.885 W, mean +0.19 (PASS).** Count reads 1.126 (FAIL), oracle 0.841. The three dipped
     tiles' errors move from −1.84 / −2.04 / −2.30 W to −0.78 / −0.80 / −1.17 W.
   - **E175: 0.668 W, mean +0.53 (FAIL) becomes 0.910, mean +0.78 (FAIL).** Count reads 0.896 / +0.79, oracle 0.786 / +0.70. No
     pinned tile dipped in E175, so the term only adds the expected loss.
4. **Why G does not pass, read pass by pass.** The term's cost of a fall is right for a pinned pass and too large for a governed one.
   Each fall's pass is set against the same tile's passes with no fall:
   - **Pinned passes, E173:** the measured cost is 48.0, 50.0, 20.4, 47.1 and 47.1 MHz. The term's cost, on the lattice fitted on all
     the falls, is 48.5, 51.1, 19.6, 47.8 and 47.7 MHz. The board measures 3.78, 4.50, 1.22, 4.39 and 3.54 W lower, against the
     term's 3.92, 4.24, 0.97, 3.99 and 3.80 W.
   - **Pinned passes, E174 (card 0):** 21.3, 44.9, 46.0, 20.5, 42.0 and 44.9 MHz measured, against 19.9, 45.1, 49.8, 19.8, 45.0 and
     49.5 MHz from the term.
   - **Governed passes, E175's three:** 24.2, 21.7 and 27.0 MHz measured, against 32.4, 37.5 and 39.2 MHz from the term. That is
     0.58-0.75 of the term's cost, 0.67 on average. (E173's `fp16.u8_tdist_93475b` fell in a governed pass too, 25.6 MHz against the
     term's 38.7. It is not a scored tile and has no governed prediction, so the term measured it against 800 MHz; it is not
     comparable.)

   That is the approximation the registration states: the power arm's catch-up after a dip is not modelled, so a governed burst's
   deficit is over-stated. On E175 two more things add to it:
   - its first fall came at burst 68 of 126, so the calibration predicted only the second half;
   - the expected loss spread over the uncalibrated passes adds about 1.6 MHz to every governed tile's predicted deficit.

   G's miss is mostly not dips: `fp16.e5c24` reads +9.79 MHz in every pass.
5. **The mechanism's timing, re-derived:**
   - **The period, from each session's own falls** (the lattice fitted on all of them): E173 1000.0104 ± 0.0006 ms (6 falls over
     1,876 beats), E174 1000.0194 ± 0.0007 ms (6 over 1,332), E175 1000.0097 ± 0.0009 ms (4 over 1,148). Each lies within its card's
     registered prior: aifoundry2 1000.0095 ± 0.0015, card 0 1000.0190 ± 0.0010.
   - **The period on the SP's own tick**, from the rings' POWER_IDLE records: E173 1.00000092 s (175 records, R 0.9953), E174
     1.00000114 s (138, R 0.9981), E175 1.00000094 s (135, R 0.9924). The residuals' p10-p90 run ±12-14 ms. Those records are too
     coarse to place a lattice point in a 3-4 ms zone, as the registration said.
   - **A fall's length, from the 10 Hz telemetry:**
     - at 600 MHz: medians of 1.101, 1.062 and 1.101 s (four falls a session that recovered in the trace; the term uses P + c7 =
       1.12 s on aifoundry2 and 1.13 s on card 0);
     - at 700 MHz: 0.20, 0.25 and 0.20 s (the term: 0.19 and 0.28 s).
   - **Late climbs:** a process's first 800 MHz reading came after the window opened (1.5 s) in 3, 3 and 5 processes. Over all
     processes it came at a median 0.93, 1.07 and 1.02 s after the process start.
   - **Where each fall sits:** each lies inside its zone, with its nearer edge 0.3-1.8 ms away. In sample, 16 lattice points sat in a zone
     and fell; 4 sat in a zone and did not fall (3 in E173, 1 in E174); no fall lay away from a lattice point.
   - **The rings behind the falls:** 11 of the 16 runs with a fall show a second POWER_IDLE record in their dump. The other 5 show
     one; the ring may have lost the other.

## What this changes

- **For the governed clock rules:** the dips are now a counted term with a working in-session calibration.
  - On the pinned clock (E173's F2, E174's C0-F), the term turns two FAILs into PASSes post hoc.
  - On the pinned board it turns E173's Bp into a PASS.
  - It does not rescue E175's governed G: its cost per governed fall is about 1.5 times too large, and G's miss is mostly a data
    term.
  - None of this is a verdict. The first blind test is the next governed session that keeps the gaps (REGISTRATION.md section 6).
- **The governed approximation needs a catch-up model** before DT-G can help. E175's three governed falls suggest a factor of about
  0.67 on a governed pass's deficit (post hoc, n 3). Any such factor must be registered before the blind session, as a dated
  amendment beside the registration.
- **The count alone does not fix a clock rule's rms.** It spreads the expected loss of about 2 MHz a pass over every pass (the
  registered forecast said so).
- **One kernel per burst** (kit v4's default) removes both the falls and the late climbs. Its option is
  `tools/claims-v3/kitv4-onekernel/`, committed after this directory.

## Files

| file | what |
|---|---|
| [`posthoc_dips_q145b.py`](posthoc_dips_q145b.py) | the study; it imports the registered `dipterm.py` and `score_dipterm_v2.py` after checking them against `SHA256SUMS` and `SHA256SUMS-1` |
| [`posthoc-dips.json`](posthoc-dips.json) | everything: per session the timing, DT-N, DT-L, each arm's rules with every tile, the reference figures, each fall's cost; E100's arms |
| [`posthoc-dips.txt`](posthoc-dips.txt) | the printed summary |
| [`SHA256SUMS`](SHA256SUMS) | the hash list of the files above |

Rebuild from the repository root (Python 3, no third-party module; about 30 s on one core):

```bash
python3 -I -B docs/reports/data/2026-11-06-q145b-dips-posthoc/posthoc_dips_q145b.py --root . \
  --out docs/reports/data/2026-11-06-q145b-dips-posthoc/posthoc-dips.json > docs/reports/data/2026-11-06-q145b-dips-posthoc/posthoc-dips.txt
```

SPDX-License-Identifier: Apache-2.0
