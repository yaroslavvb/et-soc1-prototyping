# MM1-v3 amendment A2: the energy pin for the fold without the kc reference card (post hoc)

*Written Tue 17 Nov 2026 about 20:20 PST (Pacific), round Q214, lane fix-mm1v3, at aifoundry2's desk. **Post hoc**: written after every
MM1-v3 fit, after MM1-v3's first record (the local commit b75952c1, never pushed) and after its verification (verify-mm1v3, finding 1),
which had shown the held-out figure along the line below. `DECLARED-v3.md` (sha256 8365e655..., written before any fit) is unchanged; this
file adds one pin to its section 5.*

**What the fit cannot identify.** kc is each card's factor on the per-op energy, relative to aifoundry3 card 0, whose kc is 1 by definition
(`energy_v3.W_v3`, form v3). Only one fold holds aifoundry3 out: LOCO aifoundry3 card 0. In it, the three training cards' kc and the
constants they multiply trade exactly. Those constants are Eub (fp32, fp16, int8), a_op, a_lane, a8 and b0. Multiplying every kc by s and
dividing those constants by s leaves every training prediction unchanged, so the training cost stays at 1.000131025 along the whole line.
The held-out card is priced at kc = 1, so its forecast moves along the line. With every kc inside its declared bounds (0.5 to 2):
- pooled LOCO W over idle given t runs from 6.77% to 43.53%;
- aifoundry3's own error runs from 6.45% to 86.84% (`out/postcheck_loco_a3_line.json`).

The first record's 7.01% (aifoundry3 7.44%) was simply where its optimizer stopped, at a mean training kc of 1.045.

**The pin.** In a fold without aifoundry3, the training cards' mean kc is 1. The held-out card then sits at the training cards' mean. This
reads the same as the declared rule for an absent card's awake power (DECLARED-v3.md section 5: "a held-out card takes the other cards' mean
Pa and kc 1"). `fit_v3.fit_energy` applies the pin after the fit by that exact rescaling of the fitted point: with s the mean kc as fitted,
every kc becomes kc / s and every per-op constant above is multiplied by s. The fold's record carries it (`pin_A2`: s, the kc before and
after, and the training cost before and after, equal to 15 digits).

**What it changes.** Only that fold of the energy form v3. The energy fits were re-run on Tue 17 Nov 2026, 20:04:57-20:05:44 PST,
single-threaded. Every other fold of v3 and of v3-ledger, and both all-data fits, came out identical to the first record. The parameter
file is byte for byte the same (`1fdc0749...`), and so are E213's and E212 a2c0-S3/S4's forecast values. The rows that change:

| W over idle given t, LOCO (points both forms price, at 3 W or more) | first record | under A2 | v2form |
|---|---|---|---|
| aifoundry3 held out (n 376) | 7.44% (+3.91) | **9.70% (+7.32)** | 13.39% (+9.70) |
| pooled, four cards (n 1,525) | 7.01% (-2.13) | **7.66% (-1.29)** | 11.59% (-3.31) |

Acceptance rule 2's energy half (v2form's 11.59% + 0.3 points = 11.89%) still passes.

**Why this pin, and the alternatives (disclosed).** The pin was chosen after the line had been seen. The alternatives below all sit on the
same line, at the same training cost:

| pin | pooled LOCO |
|---|---|
| aifoundry1 card 1's kc = 1 | 7.39% |
| aifoundry2's kc = 1 | 7.98% |
| aifoundry1 card 0's kc = 1 | 7.65% |
| the line's lowest point (mean kc 1.094) | 6.77% |

Rule 2's energy half passes for any mean training kc from 0.868 to 1.491 and fails outside that range. v2form needs no such pin: it prices a
held-out card from that card's own ledger anchor (MM1-v2's design).
