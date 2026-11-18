# E212 session a2c0-S2's data README, dated note 1 (Tue 17 Nov 2026; after the data verifier): the checker's reproduce line needs the claim's planning line, `--plan-w 73.3` (post hoc)

*Written on aifoundry2 from about 19:30 PST on Tue 17 Nov 2026 (week 47) by the clock. This was desk work only: no card, no other lab
box, no device and no post. It was written by the lab's lane `fix-e212d` of round Q208 (continued as Q208c after aifoundry2 went down
at about 15:45 PST), after this directory's data verifier, `verify-e212d`. The verifier's verdict was "holds with fixes" (its record,
REPORTED: with its own code it re-derived all nine committed E212 sessions from their raw files, 213,165 numeric leaves bit-equal and
0 mismatches). It found three low README fixes, and its finding 1 is this directory's. [`README.md`](README.md) and
[`SHA256SUMS`](SHA256SUMS) (lab `58f01105`, 15:00:32 PST Tue 17 Nov 2026) stay as committed, and so does every data file. **No datum,
reduction, check or rule changes, nothing is scored, and no forecast number is here.** **Everything below is post hoc to the data
commit.** The interpreter throughout was `/usr/bin/python3` 3.12.3 with `-I -B` on aifoundry2. Labels: **registered**
([`E212.md`](../../../../tools/claims-v3/e212/E212.md)), **measured** (the session's records), **desk check** (this lane's runs of the
committed code on the committed files) and **REPORTED** (verify-e212d's, not re-run here).*

## 1. The correction: the checker's line needs `--plan-w 73.3` (verify-e212d's finding 1, low)

**What README.md says** (its section "Reproduce", line 78), verbatim:

```
python3 -I -B check_session_e212.py session a2c0 ../../../../tools/claims-v3/e212/proposal/src --out checks.json --txt checks.txt
```

**So the line should read:**

```
python3 -I -B check_session_e212.py session a2c0 ../../../../tools/claims-v3/e212/proposal/src --plan-w 73.3 --out checks.json --txt checks.txt
```

**Why.** Check C9 compares every scheduled run's planned peak with the planning line that the claim names for its own session. The
checker holds the lines of aifoundry1's two cards (66.6 W and 52 W, from #11 and #11.2) but none for aifoundry2 card 0
(`check_session_e212.py` line 50, `"plan_w": None`). Without `--plan-w` it falls back to the schedule's own `line_w`, 80 W, which is
the registered planning line for this card (E212.md section 5). This session's claim, #11.10 (14:17:43 PST), names 73.3 W: "every run
is planned at or under 73.3 W (the four time-only arms; the card's 82 W peak rule and 85 W live stop stand)" (README note 2). The data
lane passed that line as `--plan-w 73.3`, read from this directory's `meta-e212-a2c0-S2.json` (`plan.plan_w`), so the committed
`checks-e212-a2c0-S2.json` and `.txt` read 73.3.

**What this lane ran** (desk check, in a copy of GitHub main's tree at `95ff5098`, with outputs written outside the copy):

- The line as printed: rc 0. Its C9 reads `line_w 80.0; line_from the schedule's own line_w (no claim line set here)`, so its outputs
  differ from the committed files in that check alone: 2 lines of the JSON and 1 line of the `.txt`.
- The line with `--plan-w 73.3`: rc 0. Both outputs equal `checks-e212-a2c0-S2.json` and `checks-e212-a2c0-S2.txt` byte for byte.
- C9 passes either way: the highest planned peak is 73.3 W and the measured board peak 72.75 W. The verdict "ALL PASS (C0-C9)" stands.

**What stays as it was:** every other line of the README. Every other reproduce line reproduces as printed: the registered reducer,
`spot_time_e208.py`, `window_e212.py`, `patterns_e212.py` and `laws_e212.py` (verify-e212d's record, REPORTED), and `box_e212.py`
(re-run by this lane: byte for byte).

## 2. Files and how to reproduce

| file | what | label |
|---|---|---|
| `README.md.dated-note-1.md` | this note | post hoc |
| `SHA256SUMS-note1` | the sha256 of this note, `README.md` and `SHA256SUMS` | - |

```
sha256sum -c SHA256SUMS-note1
python3 -I -B check_session_e212.py session a2c0 ../../../../tools/claims-v3/e212/proposal/src --plan-w 73.3 --out checks.json --txt checks.txt
```

The second line writes `checks.json` and `checks.txt` equal to `checks-e212-a2c0-S2.json` and `checks-e212-a2c0-S2.txt` byte for byte
when `python3` is `/usr/bin/python3` (the JSON names the interpreter).

SPDX-License-Identifier: Apache-2.0
