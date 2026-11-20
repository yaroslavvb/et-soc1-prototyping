# E219 session a1c1-S3's data README, dated note 1 (Thu 19 Nov 2026; after the data verifier): check B's reproduce line leaves out one input, the orchestrator's E217 record; the release's "every check exact" read against the records (post hoc)

*Written on aifoundry2 from about 23:53 PST on Thu 19 Nov 2026 (week 47) by the clock. This was desk work only: no card, no other lab box, no device and no post. It was written by the lab's lane `fix-e219d` of round Q232, after this directory's data verifier, `verify-e219d`. The verifier's verdict was "HOLDS WITH FIXES" (its record, REPORTED: with its own code it re-derived all five committed E219 sessions, 412 of 412 runs, from their raw files: 120,716 numeric leaves bit-equal, 8,911 other leaves equal and 0 mismatches). It found two low README fixes, both in reproduce lines: its finding 1, in a1c1-S1's README only, and its finding 2, in all five, which this note answers in section 1. Its finding 3 (information, no fix asked) is read against this directory's records in section 2. Its other findings ask for no change here. [`README.md`](README.md) and [`SHA256SUMS`](SHA256SUMS) (lab `64e37eec`, 23:06:40 PST Thu 19 Nov 2026) stay as committed, and so does every data file. **No datum, reduction, check or rule changes, nothing is scored, and no forecast number is here.** **Everything below is post hoc to the data commit.** The interpreter throughout was `/usr/bin/python3` 3.12.3 with `-I -B` on aifoundry2. Labels: **registered** ([`E219.md`](../../../../tools/claims-v3/e219/E219.md)), **measured** (the session's records), **desk check** (this lane's runs of the committed code on the committed files) and **REPORTED** (verify-e219d's record, not re-run here).*

## 1. Check B's line: one input it read is not in the line (verify-e219d's finding 2, low)

**What README.md says** (its section "Reproduce", line 86), verbatim:

```
python3 -I -B box_e219.py session --others ../2026-11-19-e219-mmsweep5-a1c0-S1/session ../2026-11-19-e219-mmsweep5-a1c0-S2/session ../2026-11-19-e219-mmsweep5-a1c1-S1/session ../2026-11-19-e219-mmsweep5-a1c1-S2/session --e217-dirs ../2026-11-19-e217-mmsweep4-a1c0-S1/session ../2026-11-19-e217-mmsweep4-a1c0-S2/session ../2026-11-19-e217-mmsweep4-a1c0-S3/session ../2026-11-19-e217-mmsweep4-a1c1-S1/session ../2026-11-19-e217-mmsweep4-a1c1-S2/session ../2026-11-19-e217-mmsweep4-a1c1-S3/session ../2026-11-19-e217-mmsweep4-a1c1-S4/session --out box.json --txt box.txt
```

**The line with every input the check read** (the data lane's step, written from this directory; the two inputs in angle brackets are not in the repository, and the last paragraph of README.md names both):

```
python3 -I -B box_e219.py session --others ../2026-11-19-e219-mmsweep5-a1c0-S1/session ../2026-11-19-e219-mmsweep5-a1c0-S2/session ../2026-11-19-e219-mmsweep5-a1c1-S1/session ../2026-11-19-e219-mmsweep5-a1c1-S2/session --listing <the lab's listing of the box's sessions folder, made at this session's copy> --e217-dirs ../2026-11-19-e217-mmsweep4-a1c0-S1/session ../2026-11-19-e217-mmsweep4-a1c0-S2/session ../2026-11-19-e217-mmsweep4-a1c0-S3/session ../2026-11-19-e217-mmsweep4-a1c1-S1/session ../2026-11-19-e217-mmsweep4-a1c1-S2/session ../2026-11-19-e217-mmsweep4-a1c1-S3/session ../2026-11-19-e217-mmsweep4-a1c1-S4/session --e217-record <the orchestrator's E217 record of claims and releases> --out box.json --txt box.txt
```

**Why only one field differs.** `box_e219.py` takes `--e217-record`, the orchestrator's record of E217's claims and releases on aifoundry1, for any E217 session not yet committed (`box_e219.py` line 38). All seven E217 sessions on the box were committed before this check ran, and the check read each one exactly from its committed folder through `--e217-dirs`; the code skips the record's entry for every E217 session read that way (line 91). So the record adds no row and changes no verdict: it sets only the JSON's `e217_record_read` (line 115), which is true whenever a record is given. `--listing` (lines 36 and 53-60) adds a session only when the listing holds one that is neither this session nor among `--others`; the lab's listing made at this session's copy (README note 3) held only this session and the ones given by `--others`, and the committed `listed_not_copied` is empty. verify-e219d's record (REPORTED) says the printed line also leaves out `--others`. It does not: line 86 gives `--others` with the four E219 sessions committed before this one (a1c0-S1, a1c0-S2, a1c1-S1 and a1c1-S2), in sorted order, exactly the `others_dirs` of the committed `box-e219-a1c1-S3.json`. The verifier's reproduce step ran a fixed line without it; by its record, its runs with `--others` reproduced the `.txt`.

**What this lane ran** (desk check, in a copy of GitHub main's tree at `64e37eec`; each line taken from its README and run from the session's directory, its outputs then moved outside the copy):

- The line as printed: rc 0. `box.txt` equals `box-e219-a1c1-S3.txt` byte for byte. `box.json` differs from `box-e219-a1c1-S3.json` in one line, `"e217_record_read": false`, where the committed file reads `true`; a key-by-key comparison finds that 1 of its 35 leaves differs and no other.
- The line with `--e217-record` added (the record as it stands: unchanged since 19:46:34 PST Thu 19 Nov 2026, before E219's first release at 20:25:22 PST, so every E219 check read it as it is now): both outputs equal the committed files byte for byte. With the lab's listing made at this session's copy added too: both byte for byte.
- B1 passes either way. The same three results hold in all five E219 sessions, 5 of 5. verify-e219d's own span check of the twelve sessions on aifoundry1 (E217's seven and E219's five) finds no overlap (REPORTED).

## 2. A reading note on the release's words "every check exact" (verify-e219d's finding 3, information; no fix asked)

README note 3 (line 11) quotes the model session's release post verbatim, and the post says "every check exact". The records say more. In this session the host's result check reads `approx` in 17 of 64 device processes and `exact` in the other 47 (each run record's `procs[].check`, measured). The 17 are the session's 13 fp32 and 4 fp16 random-data processes, which are all of its fp16 or fp32 random-data processes (17 of 17); no other process reads `approx`. All 64 have their check ok (`check_ok` true) and rc 0, and the smoke's three processes read `exact`. The registered runner accepts a check of C that is exact or approx (E219.md section 6, for the smoke; for every run's process, `run_mms.py` line 845 of the proposal copy counts it as failed only when its rc is not 0, its check is neither, or its check is not ok). README.md's C2 row ("its result check ok") and the `checks` column of the reduction table, which shows `approx` on those arms, already say this rightly. The quote stays a quote, and nothing here changes it.

## 3. Files and how to reproduce

| file | what | label |
|---|---|---|
| `README.md.dated-note-1.md` | this note | post hoc |
| `SHA256SUMS-note1` | the sha256 of this note, `README.md` and `SHA256SUMS` | - |

```
sha256sum -c SHA256SUMS-note1
python3 -I -B box_e219.py session --others ../2026-11-19-e219-mmsweep5-a1c0-S1/session ../2026-11-19-e219-mmsweep5-a1c0-S2/session ../2026-11-19-e219-mmsweep5-a1c1-S1/session ../2026-11-19-e219-mmsweep5-a1c1-S2/session --e217-dirs ../2026-11-19-e217-mmsweep4-a1c0-S1/session ../2026-11-19-e217-mmsweep4-a1c0-S2/session ../2026-11-19-e217-mmsweep4-a1c0-S3/session ../2026-11-19-e217-mmsweep4-a1c1-S1/session ../2026-11-19-e217-mmsweep4-a1c1-S2/session ../2026-11-19-e217-mmsweep4-a1c1-S3/session ../2026-11-19-e217-mmsweep4-a1c1-S4/session --out box.json --txt box.txt
```

`box.txt` then equals `box-e219-a1c1-S3.txt` byte for byte when `python3` is `/usr/bin/python3` 3.12.3, and `box.json` equals `box-e219-a1c1-S3.json` but for its line `"e217_record_read": false` (section 1).

**What stays as it was:** every other line of the README. The checker's line reproduces as printed (this lane's desk check, byte for byte). The other reproduce lines reproduce as printed too: the registered reducer, `spot_time_e208.py`, `window_e219.py`, `never_e219.py` (at the lab's commit named in note 6) and check K's block (verify-e219d's record, REPORTED).

SPDX-License-Identifier: Apache-2.0
