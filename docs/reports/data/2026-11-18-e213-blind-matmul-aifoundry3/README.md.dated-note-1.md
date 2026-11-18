# E213 arm A data, dated note 1 (post hoc): the data verifier's findings on this directory, answered

*Wed 18 Nov 2026 (week 47), PST, the fix lane `fix-e213d` (Q216), after the data verifier `verify-e213d` (HOLDS WITH FIXES: this
directory's data commit `c69a12aa` re-derives exactly from its raw records; its findings are a record, a note on the points file, a wording
point for the scores' write-up, and one finding that looks ahead to arm B). A dated note beside this directory's README. **Post hoc**:
written after the data and after the frozen scorer's run (step 13), whose outputs a later lane commits beside this directory. It edits no
committed file and changes no datum, forecast, rule, label or verdict, and it does not re-run the frozen scorer. The figures in sections 2
and 3 are printed by `posthoc_note1_e213a.py` in this directory, run under `/usr/bin/python3` 3.12.3 from this directory's measured
records and E213's frozen files, each checked at its registered sha256: its printout is `posthoc-note1-e213a.txt` and its JSON
`posthoc-note1-e213a.json`, both listed in `SHA256SUMS-note1`.*

## 1. The model session's second sealed forecast (departure 9 names the first only)

Departure 9 records the model session's first sealed forecast of E213 (sha256 `76f0b2f4643b8d2a599085041d6fcc5f063345465687f51ec75f7363c0b20325`),
registered by `8e91dda6` before this arm booked. The README does not name a second one, posted during this arm's session and registered
after this directory's data commit:

- **The seal:** sha256 `d622ce167c421999ee646c9ec60a478e365b7fc4f2177504b6750efbde0327bd`, the model session's forecast of E213's 131
  points and 117 cases on both arms from its own refitted model, posted on the round's coordination thread at **06:53:32 PST** Wed 18 Nov
  2026.
- **Its place in this arm's day:** after this arm's booking (06:32:00) and its first card command (06:37:09); before the session's end
  (07:19:59) and before this directory's data commit `c69a12aa` (committed 07:23:29, pushed by 07:23:33).
- **Its registration:** `tools/claims-v3/sealed-e213/e213-freeze-lines-2.md`, commit `d8404ef2` (committed 07:54:47, pushed 07:54:53
  PST), after this directory's data commit. That note's paragraph on arm A labels the seal post-data. Its dated correction 1,
  `tools/claims-v3/sealed-e213/e213-freeze-lines-2-correction-1.md` (commit `f3de54a2`, committed 08:03:15 PST by the round's
  orchestrator), corrects that label by E213.md section 0, which ties it to the time the seal was posted: "One posted after an arm's first
  card command is REPORTED as sealed during the session, or after its data commit as post-data."
- **So, for this arm:** the second seal is **REPORTED as sealed during this arm's session, before its data commit**. It is not a freeze
  line of arm A (it was posted after the booking) and not post-data (the post came before the data commit; only its registration came
  after it). For arm B it is freeze line 2.
- Its numbers are not quoted here (its sha256 only), and the lab does not score it. Nothing in this directory depended on it; nothing
  changes.

## 2. The smoke's arguments in `points-e213.json` (a note on the points file)

`points-e213.json` lists every smoke process (this arm's s01-s04 and arm B's s11-s14) with `host_args` carrying `--seconds 6 --budget 7.5`,
the form of a scored run. The kit's `host_argv` (`tools/claims-v3/e213/e213_common.py`) sets `--seconds` and `--budget` to the process's own
form when it builds each command line: `SMOKE_SECONDS, SMOKE_BUDGET = 2.0, 3.5` for the smoke (`run_e213.py`'s smoke step) and
`RUN_SECONDS, RUN_BUDGET = 6.0, 7.5` for every run. This session's four smoke command lines (`session/smoke/s01` to `s04`, `smoke.json`,
`argv`) read **`--seconds 2 --budget 3.5`**, as E213.md section 3 ("one checked 2 s process each") and Amendment A1 clause 1 (s04,
`--seconds 2 --budget 3.5`) register, and as the README's smoke row says ("2 s each"). So the points file's smoke arguments are the template
the runner fills, not what ran. No rule reads the smoke's arguments, and nothing changes. The same holds for arm B's four smoke rows, which
have not run.

## 3. The gemmLnc points' board power against their planning peaks (the part of the verifier's medium finding that is this directory's)

E213.md section 6 plans each point's peak as MM1-v3's W over idle + its rest law + 2 W (`plan_e213.py`), keeps every point's planning peak
under the **65 W line**, and arms the live stops (the board strictly above 70 W on 3 samples in a row; the die at 70 C). Read post hoc against this
directory's records (each run's highest board reading inside its process window, and the reducer's `p_work`):

- **96 of the 102 point and reference runs** stayed under their planning peaks: board peak minus planning peak, median -3.16 W, highest
  -0.43 W.
- **The six runs over theirs are every run of the five 'rgm136 gemmLnc' points** (a079 ran twice):

| run | point | configuration | p_work (W) | board peak (W, at PST) | planning peak (W) | peak - plan (W) | under the 65 W line by (W) | its gemmL twin: peak - plan (W) |
|---|---|---|---|---|---|---|---|---|
| 075-pass1-a086 | a086 | gemmLnc1x1x44 fp32 random 0xffffffff | 44.97 | 47.44 (07:06:33.615) | 42.81 | +4.63 | 17.56 | a083: -4.80 |
| 079-pass1-a082 | a082 | gemmLnc4x1x6 fp32 random 0xffffffff | 46.69 | 47.66 (07:07:56.842) | 43.29 | +4.37 | 17.34 | a030: -3.48 and -2.80 |
| 083-pass1-a079 | a079 | gemmLnc1x6x5 fp32 random 0xffffffff | 50.03 | 50.79 (07:09:46.809) | 47.54 | +3.25 | 14.21 | a076: -2.53 |
| 087-pass1-a075 | a075 | gemmLnc3x1x3 fp32 random 0xffffffff | 62.93 | 64.22 (07:12:07.029) | 51.31 | **+12.91** | **0.78** | a006: -1.71 |
| 089-pass1-a087 | a087 | gemmLnc1x1x1 int8 random 0xffffffff | 50.02 | 50.55 (07:13:21.948) | 42.01 | +8.54 | 14.45 | a088: -2.59 |
| 094-pass2-a079 | a079 | gemmLnc1x6x5 fp32 random 0xffffffff | 49.91 | 50.77 (07:15:35.950) | 47.54 | +3.23 | 14.23 | a076: -2.53 |

- Their gemmL twins (the same shape, format, data kind and mask on rgm136's cooperative loop) stayed 1.71-4.80 W under their planning
  peaks. The session's highest board reading, 64.22 W in a075's run (the README's results), was 12.91 W over that point's planning peak and
  12.21 W over the arm's highest planning peak (52.01 W at a073, E213.md section 6's predicted peak); it stayed 0.78 W under the 65 W line
  and under the 70 W stop, and no stop fired.
- So MM1-v3's planning peak under-reads the gemmLnc loop's board power on this card, by 3.2-12.9 W in these runs, while it holds for every
  other loop here. The labels: the board readings are **measured**; the planning peaks, the line and the stops are **registered**; the
  differences are **desk arithmetic, post hoc, REPORTED**. No rule reads them and no verdict changes (the scorer's energy rules read
  joules, not planning peaks).
- The verifier's finding asks that this be read against arm B's four gemmLnc points, which are planned by the same form on aifoundry1 card
  1, before arm B books again. That reading, and any decision it leads to, are the round orchestrator's; nothing of arm B's points,
  forecasts, order, lines or stops changes here.

## 4. Not in this note

The verifier's wording point on E4 (a miss by one point, and E4's exact failing points) is for the scores' write-up, which a later lane
commits beside this directory with the frozen scorer's outputs.

## What this note changes

Nothing measured, forecast, registered or scored. It adds five new files: this note, the script `posthoc_note1_e213a.py`, its printout
`posthoc-note1-e213a.txt`, its JSON `posthoc-note1-e213a.json`, and `SHA256SUMS-note1`, which lists the other four and `README.md` and
`SHA256SUMS` as the data commit holds them. Every committed file stands as committed. To reproduce: from this directory,
`/usr/bin/python3 -I -B posthoc_note1_e213a.py --json <a new path>` prints `posthoc-note1-e213a.txt` byte for byte, using Python's own
modules only.

SPDX-License-Identifier: Apache-2.0
