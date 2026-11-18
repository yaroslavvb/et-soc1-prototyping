# E212 session a1c1-S2's data README, dated note 1 (Tue 17 Nov 2026; after the data verifier): note 7's rest-power figures restated from a stated procedure and its script; the power-state change sits inside E212.md section 5; the box check's line in the committed order (post hoc)

*Written on aifoundry2 from about 19:30 PST on Tue 17 Nov 2026 (week 47) by the clock. This was desk work only: no card, no other lab
box, no device and no post. It was written by the lab's lane `fix-e212d` of round Q208 (continued as Q208c after aifoundry2 went down
at about 15:45 PST), after this directory's data verifier, `verify-e212d`. The verifier's verdict was "holds with fixes" (its record,
REPORTED: with its own code it re-derived all nine committed E212 sessions from their raw files, 213,165 numeric leaves bit-equal and
0 mismatches). It found three low README fixes. Its finding 2 is this directory's, and so is its finding 4 (information). Section 3
answers a line of its reproduce record. [`README.md`](README.md) and [`SHA256SUMS`](SHA256SUMS) (lab `7dfba40b`, 13:47:50 PST Tue 17
Nov 2026) stay as committed, and so does every data file. **No datum, reduction, check or rule changes, nothing is scored, and no
forecast number is here.** **Every figure below is post hoc to the data commit.** The figures come from three places. (a) This
directory's committed files, and those of E212's three other card-1 sessions. (b) This lane's own code,
[`posthoc_note1_e212.py`](posthoc_note1_e212.py), which reads `session/` and the committed reduction and imports nothing from the kit or
the reducer. Its output is in `posthoc-note1-e212-a1c1-S2.txt` and `.json`. (c) This lane's runs of the committed checkers on the
committed files. The interpreter throughout was `/usr/bin/python3` 3.12.3 with `-I -B` on aifoundry2. Labels: **registered**
([`E212.md`](../../../../tools/claims-v3/e212/E212.md)), **measured** (the session's records, and the registered reducer's output from
them), **desk check**, **post hoc** (this lane's desk arithmetic after the data, deciding nothing) and **REPORTED** (verify-e212d's,
not re-run here).*

## 1. Note 7's post hoc figures, restated from a stated procedure (verify-e212d's finding 2, low)

**What README.md says** (note 7, line 15), verbatim, the post hoc sentence:

> *Post hoc, desk check:* the rest windows' board power before each run, adjusted for the die by its own fit (0.355 W a degree), shows
> no step (its mean residual +0.002 W over the first half of the runs, -0.002 W over the second), and the clock read 600 MHz in all
> 24,109 samples.

**What was wrong.** The data lane recorded no procedure and no script for the fit, 0.355 W a degree, or for the two residuals,
+0.002 W and -0.002 W, and nobody has been able to reproduce them.

- The verifier's own readings gave 0.359-0.400 W a degree and +-0.006 to +-0.019 W, depending on the rest window (REPORTED).
- This lane ran 200 fits: five readings of the rest's board power, four of its die, five subsets of runs and two ways to halve an odd
  count (some readings coincide). The slopes came out at 0.326-0.400 W a degree, and none gives 0.355 with +-0.002 W. That exploration
  is not committed.

**So those three figures are withdrawn,** and the stated procedure below replaces them. The clock figure stands (measured: 24,109 of
24,109 samples at 600 MHz, check C4, as the verifier also found).

**The stated procedure** (W1; `posthoc_note1_e212.py`):

1. Take every run that ran, in run order: all 87 (73 arm runs, 7 anchor runs and 7 null runs).
2. For each run, y is its `p_rest_plain_w` in `data-e212-a1c1-S2.json`: the registered reducer's median board power over the last 5 s
   before the run's first process (for a null run, before its window). x is its `die_start_c`: the mean die, the shires' mean, over
   the same 5 s. The script re-derives both from `session/` and finds them equal to the reduction's in 87 of 87 runs.
3. Fit a least-squares line y = a + b x over the 87 runs, and take the residuals in run order.
4. Split the runs in halves, runs 1-43 and 44-87. Give each half's mean residual, the difference between them and its standard error.
   Also scan every split with at least 10 runs on each side for the largest difference over its standard error.
5. Do the same on E212's three other card-1 sessions, as the yardstick. Their power state did not change: S1 and S4 read 3 at both
   ends, and S3 read 1.

**Results** (post hoc, from `posthoc-note1-e212-a1c1-S2.txt`; W1):

| session (power state, start to end) | slope, W a degree | residual sd, W | mean residual, first half / second half, W | difference / its standard error | largest split ratio (at least 10 runs a side) |
|---|---|---|---|---|---|
| **a1c1-S2 (3 to 1)** | **0.3610** | 0.1115 | **+0.0181 / -0.0177** | -0.0358 W / 0.0237 W = -1.51 | **2.53** (before run 062: -0.0639 W) |
| a1c1-S1 (3 to 3) | 0.3601 | 0.1233 | +0.0335 / -0.0327 | -0.0661 W / 0.0262 W = -2.53 | 3.32 (before run 035: -0.0834 W) |
| a1c1-S3 (1 to 1) | 0.3802 | 0.1100 | +0.0005 / -0.0005 | -0.0009 W / 0.0251 W = -0.04 | 1.11 (before run 029: +0.0279 W) |
| a1c1-S4 (3 to 3) | 0.3543 | 0.1210 | +0.0015 / -0.0014 | -0.0029 W / 0.0262 W = -0.11 | 2.33 (before run 065: +0.0555 W) |

- **Other windows.** The script also reads two other windows: W2, the mean of the last 5 s, and W3, the mean of the whole rest (10 s
  before a burst, 20 s before a three-process run or a null window). Each takes the die over the same window. For this session they give
  0.3590 and 0.3996 W a degree, half means of +0.0188 / -0.0184 W and +0.0064 / -0.0063 W, and largest split ratios of 2.48 and 1.74.
  The other three sessions give 1.40-3.17 (W2) and 1.67-3.29 (W3).
- **The verifier's readings.** Its three readings (0.359-0.400 W a degree, +-0.006 to +-0.019 W) agree with these three windows.
- **Drift.** In every one of the four sessions, the residuals' means over ten-run stretches wander by up to about 0.1 W (from -0.101 to
  +0.098 W over the four). In this session they run from -0.050 to +0.060 W.

**So the sentence should read** (post hoc): "the rest's board power before each run (the median of its last 5 s, `p_rest_plain_w`),
adjusted for the die by its own least-squares fit over the 87 runs (0.361 W a degree), shows no step beyond the drift that E212's three
other card-1 sessions show with their power state unchanged. Its mean residual is +0.018 W over runs 1-43 and -0.018 W over runs 44-87,
a difference of 1.5 standard errors. The largest step at any split is 2.5 standard errors, against 1.1-3.3 in those sessions. The clock
read 600 MHz in all 24,109 samples."

**What it does and does not say** (post hoc):

- The telemetry does not record the power state, so the time of the change stays unknown, as note 7 says.
- Each run's power over idle is read against a baseline taken from that run's own rest (registered: E212.md section 7, the reducer's
  `line`, `plain` and `bracket` rules). So a step in the idle power that fell between two runs would cancel out of the next run's
  figure. A step inside a run's rest or process would not cancel fully.
- The anchor runs' primary-view power over idle (`dP_w`, measured) reads 9.151-9.586 W over the 7 anchor runs here. The sessions with
  no change read 9.272-9.459 W (S1, 6 runs), 9.365-9.555 W (S3, 7 runs) and 9.199-9.563 W (S4, 8 runs).
- The registered reduction still treats the session as one, as note 7 says. Nothing is corrected.

## 2. The power-state change sits inside the registered conditions (verify-e212d's finding 4, information)

Check C3's config sub-check FAILS by the lab checker's own rule: the config read at the start must equal the one at the end
(`check_session_e212.py` lines 257-262; `checks-e212-a1c1-S2.txt`, "config_end_equal False"). The registration is wider than that
rule. E212.md section 5 (registered), in its row "the start config read must be", reads for aifoundry1 card 1, verbatim: "TDP 65 W,
threshold 65 C, minion 600 MHz, power state 1 or 3 (card 1 reads either; any change recorded at the closing read)".

So the change from 3 at the start to 1 at the end sits inside the registered conditions. The power state was read, never set, and the
change was recorded at the closing read: note 7 quotes `session.log`, and the model session's release says the same. The FAIL is the
lab's checker being stricter than the registration. Nothing else in note 7 changes.

For context (measured, from the config reads): a1c1-S3, which began 6.7 min after this session closed, read power state 1 at both ends.

## 3. The box check's line, in the committed order (verify-e212d's reproduce record: "box 5 of 9")

**What README.md prints** (its section "Reproduce", line 86) lists the other sessions in the order a1c0-S1, a1c0-S2, a1c1-S1, a1c1-S4.
The committed `box-e212-a1c1-S2.json` and `.txt` list them in the order the data lane passed them, their T0 order: a1c1-S1 (05:30:01),
a1c0-S1 (06:16:04), a1c1-S4 (07:02:03), a1c0-S2 (09:32:02).

**What this lane ran** (desk check, in a copy of GitHub main's tree at `95ff5098`):

- **As printed:** rc 0. The verdict is PASS, with the same four sessions, all apart. The outputs differ from the committed ones only in
  the order the sessions are listed: the rows are equal as a set, the statement's items are equal as a set, and every other field is
  equal.
- **In T0 order:** rc 0. Both outputs equal `box-e212-a1c1-S2.json` and `.txt` byte for byte.
- **The listing:** the README says the data lane's run also read a listing of the box's sessions folder. That listing named no session
  the lab had not copied (`listed_not_copied` is empty), so the line without `--listing` reproduces the committed files.

```
python3 -I -B box_e212.py session --others ../2026-11-17-e212-mmsweep2-a1c1-S1/session ../2026-11-17-e212-mmsweep2-a1c0-S1/session ../2026-11-17-e212-mmsweep2-a1c1-S4/session ../2026-11-17-e212-mmsweep2-a1c0-S2/session --out box.json --txt box.txt
```

**What stays as it was:** every other line of the README. Every other reproduce line reproduces as printed: the checker, the
registered reducer, `spot_time_e208.py`, `window_e212.py`, `patterns_e212.py` and `laws_e212.py` (verify-e212d's record, REPORTED).

## 4. Files and how to reproduce

| file | what | label |
|---|---|---|
| `README.md.dated-note-1.md` | this note | post hoc |
| `posthoc_note1_e212.py` | this lane's code. It re-derives each run's rest board power and start die from `session/` and checks them against the reduction. It fits the rest power on the die (W1, W2, W3), then gives the halves, the split scan, the ten-run residual means, the anchors and the config reads' power state, for this session and for any session folders passed with `--others`. Python's own modules only; reads only. | lab code, post hoc |
| `posthoc-note1-e212-a1c1-S2.txt`, `posthoc-note1-e212-a1c1-S2.json` | its printed lines and its output, run on this directory with E212's other three card-1 sessions | post hoc |
| `SHA256SUMS-note1` | the sha256 of the four files above, `README.md` and `SHA256SUMS` | - |

```
sha256sum -c SHA256SUMS-note1
python3 -I -B posthoc_note1_e212.py session data-e212-a1c1-S2.json --others ../2026-11-17-e212-mmsweep2-a1c1-S1 ../2026-11-17-e212-mmsweep2-a1c1-S3 ../2026-11-17-e212-mmsweep2-a1c1-S4 --json posthoc.json
python3 -I -B box_e212.py session --others ../2026-11-17-e212-mmsweep2-a1c1-S1/session ../2026-11-17-e212-mmsweep2-a1c0-S1/session ../2026-11-17-e212-mmsweep2-a1c1-S4/session ../2026-11-17-e212-mmsweep2-a1c0-S2/session --out box.json --txt box.txt
```

- **The second line** prints `posthoc-note1-e212-a1c1-S2.txt` and writes `posthoc.json` equal to `posthoc-note1-e212-a1c1-S2.json`,
  byte for byte, when `python3` is `/usr/bin/python3` (the JSON names the interpreter). It exits 0 when every re-derived rest figure
  equals the reduction's.
- **The third line** writes `box.json` and `box.txt` equal to `box-e212-a1c1-S2.json` and `.txt`, byte for byte.

SPDX-License-Identifier: Apache-2.0
