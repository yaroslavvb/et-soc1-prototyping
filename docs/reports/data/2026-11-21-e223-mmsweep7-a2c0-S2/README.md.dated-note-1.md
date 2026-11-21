# E223 session a2c0-S2's data README, dated note 1 (Sat 21 Nov 2026; after the data verifier): check B's reproduce line leaves out its listing (post hoc)

*Written on aifoundry2 from about 07:07 PST on Sat 21 Nov 2026 (week 47) by the clock. This was desk work only: no card, no other lab box, no device and no post. It was written by the lab's lane `fix-e223d` of round Q239, after this directory's data verifier, `verify-e223d`. The verifier's verdict was "HOLDS WITH FIXES" (its record, REPORTED: with its own code it re-derived E223's three committed aifoundry2 card 0 sessions, 280 of 280 runs, from their raw files: 92,787 of 92,787 leaves equal, 87,061 of them numeric and bit-equal, and 0 mismatches; the committed session files equal the box's own by sha256, 909 of 909). It found two low fixes, and neither changes a datum or a verdict. Its finding 2 applies here (section 1); its finding 1 is about session a2c0-S3's folder alone. [`README.md`](README.md) and [`SHA256SUMS`](SHA256SUMS) (lab `3047b8dc`, 04:10:46 PST Sat 21 Nov 2026) stay as committed, and so does every data file. **No datum, reduction, check verdict or rule changes, nothing is scored, and no forecast number is here.** **Everything below is post hoc to the data commit.** The interpreter throughout was `/usr/bin/python3` 3.12.3 with `-I -B` on aifoundry2. Labels: **registered** ([`E223.md`](../../../../tools/claims-v3/e223/E223.md) and its proposal copy of the kit's source), **measured** (the session's records), **desk check** (this lane's runs of the committed code on copies of the committed files), and **REPORTED** (verify-e223d's record, not re-run here).*

## 1. Check B's reproduce line leaves out the listing (verify-e223d's finding 2; low)

**What README.md says** (its section "Reproduce", line 85), verbatim:

```
python3 -I -B box_e223.py session --others ../2026-11-21-e223-mmsweep7-a2c0-S1/session --lab ../../../.. --out box.json --txt box.txt   # --lab: the lab's committed sessions on the box within a day, read at the commit named in note 6
```

**The line with every input the check read** (the data lane's step, written from this directory; the input in angle brackets is not in the repository, and README.md's last paragraph names it):

```
python3 -I -B box_e223.py session --others ../2026-11-21-e223-mmsweep7-a2c0-S1/session --listing <the lab's listing of the box's sessions folder, made at this session's copy> --lab ../../../.. --out box.json --txt box.txt   # --lab: read at the commit named in note 6
```

**Why.** The committed check B output names the box's next session, `1795262908-a2c0-S3 (T0 04:08:28; not copied: only its start is known)` (README.md quotes it in note 2 and in row B, line 41). `box_e223.py` writes that row only from a listing of the box's sessions folder (its lines 55-62). A line of the listing counts when it holds a name of the form `<10-digit T0>-a<box>c<card>-S<n>` on this box that is neither this session nor one of `--others`. The data lane made that listing on the box at this session's copy (04:10:13 PST, note 3). It lists the model session's kit folder on the box, which the lab does not publish. A file holding the one line `1795262908-a2c0-S3` stands in for it exactly (section 2's block). The printed line does give `--others`: a2c0-S1, the E223 session of this box that ran before this one, whose folder is committed beside this one (`others_dirs` in the committed `box-e223-a2c0-S2.json`). The one input the line leaves out is the listing.

**What this lane ran** (desk check, from this directory in two copies of every committed `session/queue.json`: one at this directory's data commit `3047b8dc` (the tree note 6 names, `2ef1ea15`, with this directory added) and one at GitHub main `7d540724`):

- The line as printed: rc 0, and B PASS. Both outputs differ from `box-e223-a2c0-S2.json` and `.txt` only by that row. In the JSON, `listed_not_copied` is empty, and the statement that quotes it lacks the row. The `.txt` is the same statement, so it lacks the row too.
- With `--listing` of the one-line file, both outputs equal the committed files byte for byte. With the data lane's own listing in its place, they are byte for byte too.
- At main the results are the same.

## 2. Files and how to reproduce

| file | what | label |
|---|---|---|
| `README.md.dated-note-1.md` | this note | post hoc |
| `SHA256SUMS-note1` | the sha256 of this note, `README.md` and `SHA256SUMS` | - |

```
sha256sum -c SHA256SUMS-note1
printf '%s\n' 1795262908-a2c0-S3 > listing.txt
python3 -I -B box_e223.py session --others ../2026-11-21-e223-mmsweep7-a2c0-S1/session --listing listing.txt --lab ../../../.. --out box.json --txt box.txt
```

`box.json` and `box.txt` equal `box-e223-a2c0-S2.json` and `.txt` byte for byte. This holds in a checkout of this directory's data commit, where `--lab ../../../..` is the repository's top and reads the tree note 6 names. It also holds at GitHub main `7d540724`. It needs `python3` to be `/usr/bin/python3` 3.12.3 (the JSON files name the interpreter and its version).

**What stays as it was:** every other line of README.md. Its other reproduce lines reproduce as printed: `sha256sum -c`, the checker, the registered reducer, `spot_time_e208.py`, `window_e223.py` and check K's block (verify-e223d's record, REPORTED). `never_e223.py`'s line needs the whole lab tree at the commit note 6 names, and neither verify-e223d nor this lane re-ran it. verify-e223d re-read the never-run labels with its own code instead: 3 of 3 sessions equal, 0 differences (REPORTED).

SPDX-License-Identifier: Apache-2.0
