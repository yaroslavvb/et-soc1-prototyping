# E219 session a1c1-S1's data README, dated note 1 (Thu 19 Nov 2026; after the data verifier): the checker's reproduce line takes no `--plan-w`, and check B's line leaves out one input, the orchestrator's E217 record (post hoc)

*Written on aifoundry2 from about 23:53 PST on Thu 19 Nov 2026 (week 47) by the clock. This was desk work only: no card, no other lab box, no device and no post. It was written by the lab's lane `fix-e219d` of round Q232, after this directory's data verifier, `verify-e219d`. The verifier's verdict was "HOLDS WITH FIXES" (its record, REPORTED: with its own code it re-derived all five committed E219 sessions, 412 of 412 runs, from their raw files: 120,716 numeric leaves bit-equal, 8,911 other leaves equal and 0 mismatches). It found two low README fixes, both in reproduce lines, and both apply here: its finding 1 (section 1 of this note) and its finding 2 (section 2). Its other findings ask for no change in this directory. [`README.md`](README.md) and [`SHA256SUMS`](SHA256SUMS) (lab `022addbb`, 20:28:52 PST Thu 19 Nov 2026) stay as committed, and so does every data file. **No datum, reduction, check or rule changes, nothing is scored, and no forecast number is here.** **Everything below is post hoc to the data commit.** The interpreter throughout was `/usr/bin/python3` 3.12.3 with `-I -B` on aifoundry2. Labels: **registered** ([`E219.md`](../../../../tools/claims-v3/e219/E219.md)), **measured** (the session's records), **desk check** (this lane's runs of the committed code on the committed files) and **REPORTED** (verify-e219d's record, not re-run here).*

## 1. The correction: no `--plan-w` in the checker's line (verify-e219d's finding 1, low)

**What README.md says** (its section "Reproduce", line 83), verbatim:

```
python3 -I -B check_session_e219.py session a1c1 ../../../../tools/claims-v3/e219/proposal/src --plan-w 66.6 --out checks.json --txt checks.txt   # --plan-w: the line this session's claim names (C9)
```

**So the line should read:**

```
python3 -I -B check_session_e219.py session a1c1 ../../../../tools/claims-v3/e219/proposal/src --out checks.json --txt checks.txt
```

**Why.** Check C9 compares every scheduled run's and smoke arm's planned peak with a planning line. `--plan-w` gives the checker the line a claim names, and C9 then labels it "the claims' planning line". Without the flag the checker takes the line of its card table, which for aifoundry1 card 1 is post #14's 66.6 W, labelled "post #14's line for this card (the claim names none)" (`check_session_e219.py` lines 29-31, 52, 121-125 and 416-419). This session's claim, #14.1.1.1 (19:50:39 PST; its words in README note 2), names no planning line, and the lab's record of that claim, committed here as `meta-e219-a1c1-S1.json`, holds no `plan.plan_w`. So the data lane ran the checker without the flag (its step passes `--plan-w` only when that record holds one), and the committed `checks-e219-a1c1-S1.json` and `.txt` carry the label the checker writes only then, as README.md's own C9 row (line 40) does. Only the reproduce line was printed with the flag, and its comment says the claim names the line; the claim names none. E219's other four READMEs print the flag and reproduce as printed, because their claims name the line: "Every run planned at or under 66.6 W" (card 1's S2 and S3) and "every arm planned at or under 52 W" (card 0's S1 and S2). It is the defect E217's four card-1 READMEs had (their dated notes 1, lab `9f8b66bf`), here in one session.

**What this lane ran** (desk check, in a copy of GitHub main's tree at `64e37eec`; each line taken from its README and run from the session's directory, its outputs then moved outside the copy):

- The line as printed: rc 0. Its C9 reads the same `line_w 66.6`, labelled `line_from the claims' planning line`. So its outputs differ from the committed files in that label alone: one line of the JSON (`"line_from"`) and one line of the `.txt` (the C9 line).
- The line without `--plan-w`: rc 0. Both outputs equal `checks-e219-a1c1-S1.json` and `checks-e219-a1c1-S1.txt` byte for byte.
- C9 passes either way: the highest of the 82 planned peaks read (runs and smoke) is 62.8 W and the measured board peak 48.77 W, both under the 66.6 W line. The verdict "ALL PASS (C0-C9)" stands.
- The other four sessions' checker lines as printed (`--plan-w 66.6` for card 1's S2 and S3, `--plan-w 52` for card 0's S1 and S2): each one's outputs equal its committed checks files byte for byte, 4 of 4.

## 2. Check B's line: one input it read is not in the line (verify-e219d's finding 2, low)

**What README.md says** (its section "Reproduce", line 87), verbatim:

```
python3 -I -B box_e219.py session --e217-dirs ../2026-11-19-e217-mmsweep4-a1c0-S1/session ../2026-11-19-e217-mmsweep4-a1c0-S2/session ../2026-11-19-e217-mmsweep4-a1c0-S3/session ../2026-11-19-e217-mmsweep4-a1c1-S1/session ../2026-11-19-e217-mmsweep4-a1c1-S2/session ../2026-11-19-e217-mmsweep4-a1c1-S3/session ../2026-11-19-e217-mmsweep4-a1c1-S4/session --out box.json --txt box.txt
```

**The line with every input the check read** (the data lane's step, written from this directory; the two inputs in angle brackets are not in the repository, and the last paragraph of README.md names both):

```
python3 -I -B box_e219.py session --listing <the lab's listing of the box's sessions folder, made at this session's copy> --e217-dirs ../2026-11-19-e217-mmsweep4-a1c0-S1/session ../2026-11-19-e217-mmsweep4-a1c0-S2/session ../2026-11-19-e217-mmsweep4-a1c0-S3/session ../2026-11-19-e217-mmsweep4-a1c1-S1/session ../2026-11-19-e217-mmsweep4-a1c1-S2/session ../2026-11-19-e217-mmsweep4-a1c1-S3/session ../2026-11-19-e217-mmsweep4-a1c1-S4/session --e217-record <the orchestrator's E217 record of claims and releases> --out box.json --txt box.txt
```

**Why only one field differs.** `box_e219.py` takes `--e217-record`, the orchestrator's record of E217's claims and releases on aifoundry1, for any E217 session not yet committed (`box_e219.py` line 38). All seven E217 sessions on the box were committed before this check ran, and the check read each one exactly from its committed folder through `--e217-dirs`; the code skips the record's entry for every E217 session read that way (line 91). So the record adds no row and changes no verdict: it sets only the JSON's `e217_record_read` (line 115), which is true whenever a record is given. `--listing` (lines 36 and 53-60) adds a session only when the listing holds one that is neither this session nor among `--others`; the lab's listing made at this session's copy (README note 3) held only this session, and the committed `listed_not_copied` is empty. The printed line gives no `--others`, rightly: no E219 session ran before this one, and the committed `box-e219-a1c1-S1.json` lists none (`others_dirs` is empty).

**What this lane ran** (desk check, in the same copy):

- The line as printed: rc 0. `box.txt` equals `box-e219-a1c1-S1.txt` byte for byte. `box.json` differs from `box-e219-a1c1-S1.json` in one line, `"e217_record_read": false`, where the committed file reads `true`; a key-by-key comparison finds that 1 of its 26 leaves differs and no other.
- The line with `--e217-record` added (the record as it stands: unchanged since 19:46:34 PST Thu 19 Nov 2026, before E219's first release at 20:25:22 PST, so every E219 check read it as it is now): both outputs equal the committed files byte for byte. With the lab's listing made at this session's copy added too: both byte for byte.
- B1 passes either way. The same three results hold in all five E219 sessions, 5 of 5. verify-e219d's own span check of the twelve sessions on aifoundry1 (E217's seven and E219's five) finds no overlap (REPORTED).

## 3. Files and how to reproduce

| file | what | label |
|---|---|---|
| `README.md.dated-note-1.md` | this note | post hoc |
| `SHA256SUMS-note1` | the sha256 of this note, `README.md` and `SHA256SUMS` | - |

```
sha256sum -c SHA256SUMS-note1
python3 -I -B check_session_e219.py session a1c1 ../../../../tools/claims-v3/e219/proposal/src --out checks.json --txt checks.txt
python3 -I -B box_e219.py session --e217-dirs ../2026-11-19-e217-mmsweep4-a1c0-S1/session ../2026-11-19-e217-mmsweep4-a1c0-S2/session ../2026-11-19-e217-mmsweep4-a1c0-S3/session ../2026-11-19-e217-mmsweep4-a1c1-S1/session ../2026-11-19-e217-mmsweep4-a1c1-S2/session ../2026-11-19-e217-mmsweep4-a1c1-S3/session ../2026-11-19-e217-mmsweep4-a1c1-S4/session --out box.json --txt box.txt
```

`checks.json` and `checks.txt` then equal `checks-e219-a1c1-S1.json` and `.txt` byte for byte, and `box.txt` equals `box-e219-a1c1-S1.txt`, when `python3` is `/usr/bin/python3` 3.12.3 (the JSON files name the interpreter and its version). `box.json` equals `box-e219-a1c1-S1.json` but for its line `"e217_record_read": false` (section 2).

**What stays as it was:** every other line of the README. Its other reproduce lines reproduce as printed: the registered reducer, `spot_time_e208.py`, `window_e219.py`, `never_e219.py` (at the lab's commit named in note 6) and check K's block (verify-e219d's record, REPORTED).

SPDX-License-Identifier: Apache-2.0
