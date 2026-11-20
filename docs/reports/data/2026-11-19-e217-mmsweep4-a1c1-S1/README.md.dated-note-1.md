# E217 session a1c1-S1's data README, dated note 1 (Thu 19 Nov 2026; after the data verifier): on card 1 the checker's reproduce line takes no `--plan-w` (post hoc)

*Written on aifoundry2 from about 20:39 PST on Thu 19 Nov 2026 (week 47) by the clock. This was desk work only: no card, no other lab box, no device and no post. It was written by the lab's lane `fix-e217d` of round Q228, after this directory's data verifier, `verify-e217d`. The verifier's verdict was "HOLDS WITH FIXES" (its record, REPORTED: with its own code it re-derived all seven committed E217 sessions, 630 of 630 runs, from their raw files: 186,280 numeric leaves bit-equal and 0 mismatches). It found one low README fix, the same in E217's four card-1 directories (its finding 1), which this note answers; its other findings ask for no change in this directory. [`README.md`](README.md) and [`SHA256SUMS`](SHA256SUMS) (lab `ef4c754a`, 15:27:48 PST Thu 19 Nov 2026) stay as committed, and so does every data file. **No datum, reduction, check or rule changes, nothing is scored, and no forecast number is here.** **Everything below is post hoc to the data commit.** The interpreter throughout was `/usr/bin/python3` 3.12.3 with `-I -B` on aifoundry2. Labels: **registered** ([`E217.md`](../../../../tools/claims-v3/e217/E217.md)), **measured** (the session's records), **desk check** (this lane's runs of the committed code on the committed files) and **REPORTED** (verify-e217d's record, not re-run here).*

## 1. The correction: no `--plan-w` in the checker's line (verify-e217d's finding 1, low)

**What README.md says** (its section "Reproduce", line 82), verbatim:

```
python3 -I -B check_session_e217.py session a1c1 ../../../../tools/claims-v3/e217/proposal/src --plan-w 66.6 --out checks.json --txt checks.txt   # --plan-w: the line this session's claim names (C9)
```

**So the line should read:**

```
python3 -I -B check_session_e217.py session a1c1 ../../../../tools/claims-v3/e217/proposal/src --out checks.json --txt checks.txt
```

**Why.** Check C9 compares every scheduled run's and smoke arm's planned peak with a planning line. `--plan-w` gives the checker the line a claim names, and C9 then labels it "the claims' planning line". Without the flag the checker takes the line of its card table, which for aifoundry1 card 1 is post #13's 66.6 W, labelled "post #13's line for this card (the claim names none)" (`check_session_e217.py` lines 29-31, 52, 121-125 and 416-419). This session's claim, #13.1.2.1.1.1.1 (14:41:06 PST; its words in README note 2), names no planning line, and the lab's record of that claim, committed here as `meta-e217-a1c1-S1.json`, holds no `plan.plan_w`. So the data lane ran the checker without the flag (its step passes `--plan-w` only when that record holds one), and the committed `checks-e217-a1c1-S1.json` and `.txt` carry the label the checker writes only then, as README.md's own C9 row (line 40) does. Only the reproduce line was printed with the flag, and its comment says the claim names the line; the claim names none. E217's three card-0 READMEs print `--plan-w 52` and reproduce as printed, because their claims name that line ("every arm planned at or under 52 W"). a1c1-S2, a1c1-S3 and a1c1-S4 have the same fix in their own dated notes 1.

**What this lane ran** (desk check, in a copy of GitHub main's tree at `022addbb`, with outputs written outside the copy):

- The line as printed: rc 0. Its C9 reads the same `line_w 66.6`, labelled `line_from the claims' planning line`. So its outputs differ from the committed files in that label alone: one line of the JSON (`"line_from"`) and one line of the `.txt` (the C9 line).
- The line without `--plan-w`: rc 0. Both outputs equal `checks-e217-a1c1-S1.json` and `checks-e217-a1c1-S1.txt` byte for byte.
- C9 passes either way: the highest of the 90 planned peaks read (runs and smoke) is 58.5 W and the measured board peak 52.41 W, both under the 66.6 W line. The verdict "ALL PASS (C0-C9)" stands.
- The three card-0 lines as printed (`--plan-w 52`): each one's outputs equal its committed checks files byte for byte, 3 of 3.

## 2. Files and how to reproduce

| file | what | label |
|---|---|---|
| `README.md.dated-note-1.md` | this note | post hoc |
| `SHA256SUMS-note1` | the sha256 of this note, `README.md` and `SHA256SUMS` | - |

```
sha256sum -c SHA256SUMS-note1
python3 -I -B check_session_e217.py session a1c1 ../../../../tools/claims-v3/e217/proposal/src --out checks.json --txt checks.txt
```

The checker's outputs then equal `checks-e217-a1c1-S1.json` and `.txt` byte for byte when `python3` is `/usr/bin/python3` 3.12.3 (the JSON names the interpreter and its version).

**What stays as it was:** every other line of the README. Its other reproduce lines reproduce as printed: the registered reducer, `spot_time_e208.py`, `window_e217.py`, `box_e217.py`, `never_e217.py` and check K's lines (verify-e217d's record, REPORTED).

SPDX-License-Identifier: Apache-2.0
