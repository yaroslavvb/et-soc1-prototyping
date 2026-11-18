# E212 session a1c0-S2's data README, dated note 1 (Tue 17 Nov 2026; after the data verifier): the box check's reproduce line, in the committed order (post hoc)

*Written on aifoundry2 from about 19:30 PST on Tue 17 Nov 2026 (week 47) by the clock. This was desk work only: no card, no other lab
box, no device and no post. It was written by the lab's lane `fix-e212d` of round Q208 (continued as Q208c after aifoundry2 went down
at about 15:45 PST), after this directory's data verifier, `verify-e212d`. The verifier's verdict was "holds with fixes" (its record,
REPORTED: with its own code it re-derived all nine committed E212 sessions from their raw files, 213,165 numeric leaves bit-equal and
0 mismatches). None of its three README findings is this directory's. This note answers a line of its reproduce record instead: "box 5
of 9 (the other 4 differ only in the order of the sessions listed)", and this directory is one of the four. [`README.md`](README.md) and
[`SHA256SUMS`](SHA256SUMS) (lab `a90105da`, 10:15:48 PST Tue 17 Nov 2026) stay as committed, and so does every data file. **No
datum, reduction, check or rule changes, nothing is scored, and no forecast number is here.** **Everything below is post hoc to the data
commit.** The interpreter throughout was `/usr/bin/python3` 3.12.3 with `-I -B` on aifoundry2. Labels: **desk check** (this lane's runs
of the committed code on the committed files) and **REPORTED** (verify-e212d's, not re-run here).*

## 1. The box check's line, in the committed order

**What README.md prints** (its section "Reproduce", line 83) lists the other three sessions in the order a1c0-S1, a1c1-S1 and a1c1-S4.
The committed `box-e212-a1c0-S2.json` and `.txt` list them in the order the data lane passed them, their T0 order: a1c1-S1 (05:30:01), a1c0-S1 (06:16:04), a1c1-S4 (07:02:03).

**What this lane ran** (desk check, in a copy of GitHub main's tree at `95ff5098`):

- **As printed:** rc 0. The verdict is PASS, with the same three sessions, all apart. The outputs differ from the committed ones only
  in the order the sessions are listed: the rows are equal as a set, the statement's items are equal as a set, and every other field is
  equal.
- **In T0 order:** rc 0. Both outputs equal `box-e212-a1c0-S2.json` and `.txt` byte for byte.
- **The listing:** the README says the data lane's run also read a listing of the box's sessions folder. That listing named no session
  the lab had not copied (`listed_not_copied` is empty), so the line without `--listing` reproduces the committed files.

**So the line should read:**

```
python3 -I -B box_e212.py session --others ../2026-11-17-e212-mmsweep2-a1c1-S1/session ../2026-11-17-e212-mmsweep2-a1c0-S1/session ../2026-11-17-e212-mmsweep2-a1c1-S4/session --out box.json --txt box.txt
```

**What stays as it was:** every other line of the README. Every other reproduce line reproduces as printed (verify-e212d's record,
REPORTED).

## 2. Files and how to reproduce

| file | what | label |
|---|---|---|
| `README.md.dated-note-1.md` | this note | post hoc |
| `SHA256SUMS-note1` | the sha256 of this note, `README.md` and `SHA256SUMS` | - |

```
sha256sum -c SHA256SUMS-note1
python3 -I -B box_e212.py session --others ../2026-11-17-e212-mmsweep2-a1c1-S1/session ../2026-11-17-e212-mmsweep2-a1c0-S1/session ../2026-11-17-e212-mmsweep2-a1c1-S4/session --out box.json --txt box.txt
```

The second line writes `box.json` and `box.txt` equal to `box-e212-a1c0-S2.json` and `box-e212-a1c0-S2.txt` byte for byte when `python3` is
`/usr/bin/python3` (the JSON names the interpreter).

SPDX-License-Identifier: Apache-2.0
