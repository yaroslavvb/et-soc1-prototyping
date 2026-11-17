# MM1-v0's forecasts for E206 arm B: a freeze line (Mon 16 Nov 2026)

**What.** MM1-v0's forecasts for the 113 points of E206's **arm B**: aifoundry1 card 1 at 600 MHz, the points with `on_arm_B` True in
`tools/claims-v3/e206/points-e206.csv`. The frozen predictor `mm1_v0.py` made them **unchanged**. These files add no model, no refit
and no constant. They are a desk product: no card was read.

**When.** The forecasts were made at 20:08 PST on Mon 16 Nov 2026 and made again at 20:09 PST, byte for byte the same. They are
committed and pushed in this commit, and the push time of this commit is the freeze line. Every ref on GitHub and every ref of the
lab's clone was searched for an E206 arm B datum, at 20:06 PST and again just before the commit. None held one: no
`docs/reports/data/<day>-e206-matmul-sweep-aifoundry1-c1/` directory and no gate-stop record for it. Arm B's card day books from
00:00:30 PST on Tue 17 Nov 2026 at the earliest. **For arm B these forecasts are blind.** As a fit they are post hoc: every
constant was fitted before E206 existed (README.md, section 4).

| file | sha256 |
|---|---|
| `forecasts-e206-armB.csv` (the forecasts: the arm A file's columns) | `1edf61ff0d7a4c40c25131e79bb702bab104c6379d71a26653486ed86a798aae` |
| `forecasts-e206-armB.json` (the same rows, the card's arguments, predict()'s switch output) | `7f5aef5f782267b4663236ca75a824191b33426831dfcfd41c4f5898d7244f56` |
| `forecasts-e206-armB.py` (the wrapper that made them) | `a3f3fc1e302c6baf0fccb26a6d2f30db2bc2a71e2cf956bbf994f6287c8025e7` |
| `mm1_v0.py` (the frozen predictor, unchanged since 2d1413f5) | `7dabaeac53c67ed52815aa7e11d356e550058085f6f5a83469be38430d5f7971` |
| `../../../claims-v3/e206/points-e206.csv` (E206's registered points, at GitHub main 50476f31) | `105e1e8298e4909bd37aa6c8db64875ac0945e88e8661968bb335e0f92a9e7b1` |

`forecasts-e206-armB.sha256` lists the four files of this folder above and this note. The folder's `SHA256SUMS` belongs to the
freeze of 2d1413f5 and is unchanged.

## How

`forecasts-e206-armB.py` does five things, and stops at the first that fails:

1. It checks `mm1_v0.py`'s sha256 against the committed one and prints it first.
2. It imports `mm1_v0.py` as it stands. The predictor's own module code runs: the energy refit, its arm A forecasts and the blind-day
   plan. It writes its four outputs into a scratch folder, and they must equal the committed ones byte for byte. They did, both times.
3. It rebuilds arm A's 119 rows from `predict()` and checks them byte for byte against `mm1_v0_e206.csv`. They matched, so the row form
   the wrapper uses is the frozen code's own.
4. It takes card 1's arguments from the frozen code and its vendored inputs (below).
5. It calls `predict()` for each arm B point and writes the rows in the arm A file's form: the same columns, rounding and notes.

Reproduce, from the repository's top, with Python 3 and numpy:

```
/usr/bin/python3 -I -B tools/matmul/mm1/v0/forecasts-e206-armB.py --scratch /tmp/mm1v0b-scratch --out /tmp/mm1v0b
cmp /tmp/mm1v0b/forecasts-e206-armB.csv tools/matmul/mm1/v0/forecasts-e206-armB.csv && echo SAME
(cd tools/matmul/mm1/v0 && sha256sum -c forecasts-e206-armB.sha256)
```

The forecasts were made on aifoundry2 under `/usr/bin/python3` 3.12.3 with numpy 1.26.4, run `-I -B`. That is the interpreter the
frozen outputs were written with. Another numpy or BLAS may move the last digits of the energy refit, and the wrapper then refuses at
step 2.

## Card 1's arguments, and the one choice

- **The card name, `'aifoundry1 card 1'`.** It is one of the predictor's three cards. Its awake power from the frozen refit is
  **3.660 W** at 1,024 minions. That figure comes from 18 points of one shape, 8,192³ (E190 arm B).
- **The ledger key, `'c1'`.** Every card-1 row of the vendored energy table (`inputs/gemm_table.json`) carries ledger v2's `c1`
  resident anchors (`inputs/tables.json`). They cover fp32 and fp16 zeros and random, and int8 zeros and full. The 8 real and sparse50
  points therefore carry no energy, as on arm A.
- **The clock, 600 MHz.** This is E206's registered clock, and card 1 does not raise its clock.
- **G = 0.** Card 1 is a pinned card, so the governed term is zero. That is `predict()`'s default.
- **The voltage: V = 0.517 V, so s_V = 1.** Every card-1 row of the vendored energy table carries this voltage, and the frozen refit
  fitted card 1's awake power at it.
  - The lab's committed card-1 records read the minion rail at **499 mV** at 600 MHz (E190 arm B's config reads, E198, E199). Card 1's
    rows in the table carry the table's 600 MHz default instead.
  - Card 1's resident anchors were measured on card 1 itself.
  - **0.499 V is not used.** It would scale the voltage-scaled terms by (0.499/0.517)² = 0.9316, against the fit's own calibration of
    card 1. That is a change the frozen predictor never made.
  - *Desk sensitivity, not a forecast:* at 0.499 V, W over idle and J over idle would read 2.3% to 6.1% lower (median 5.4%). Cycles and
    seconds do not depend on the voltage.

## What the forecasts are, and are not

- **Time.** MM1-v0's time model has no card term. Its cycles and seconds for card 1 therefore equal its arm A forecasts at the same
  points: 113 of 113 are equal. Arm B tests blind whether that timing carries to another card.
- **Energy.** 105 of the 113 rows carry W over idle and J over idle a GEMM; the 8 real and sparse50 rows do not. Card 1's awake power
  rests on one shape. Leaving card 1 out read W over idle 16.5% rms (−14.6%; README.md, section 4): the awake power does not carry
  across cards. Arm B is the first test of card 1's energy at shapes other than 8,192³.
- **Shire subsets.** The subset rows carry v0's known fault (README.md, section 6): they are mapped at the full chip's footprint, with
  the note "v0 has no contention term".
- **Not forecast.** J with the card at rest is not forecast; it takes the run's measured rest, as on arm A. Launch, leakage and
  epilogue terms are not in v0.
- **Switches.** The JSON's `switches_reported` holds `predict()`'s own transistor-switch output: fin edges a GEMM, a counted tensor
  unit and an energy-scaled rest. It is **reported, not scorable**, because no card measures switches.

Labels: *desk* (arithmetic at a desk); *post hoc as a fit*; *blind* for arm B (frozen and pushed before any arm B datum existed).

SPDX-License-Identifier: Apache-2.0
