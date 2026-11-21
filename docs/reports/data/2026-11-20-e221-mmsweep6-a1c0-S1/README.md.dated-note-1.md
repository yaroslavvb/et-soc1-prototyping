# E221 session a1c0-S1's data README, dated note 1 (Fri 20 Nov 2026; after the data verifier): check B's list leaves out one of the lab's card days on this box, and check B's line leaves out its listing (post hoc)

*Written on aifoundry2 from about 17:31 PST on Fri 20 Nov 2026 (week 47) by the clock. This was desk work only: no card, no other lab box, no device and no post. It was written by the lab's lane `fix-e221d` of round Q235, after this directory's data verifier, `verify-e221d`. The verifier's verdict was "HOLDS WITH FIXES" (its record, REPORTED: with its own code it re-derived all nine committed E221 sessions, 847 of 847 runs, from their raw files: 268,666 leaves equal, 252,204 of them numeric and bit-equal, and 0 mismatches; the committed session files equal the boxes' own by sha256). It found three low fixes, and none of them changes a datum or a verdict. Its findings 2 and 3 apply here (sections 1 and 2); its finding 1 is about session a1c1-S1's folder alone. [`README.md`](README.md) and [`SHA256SUMS`](SHA256SUMS) (lab `3b89d84a`, 07:58:18 PST Fri 20 Nov 2026) stay as committed, and so does every data file. **No datum, reduction, check verdict or rule changes, nothing is scored, and no forecast number is here.** **Everything below is post hoc to the data commit.** The interpreter throughout was `/usr/bin/python3` 3.12.3 with `-I -B` on aifoundry2. Labels: **registered** ([`E221.md`](../../../../tools/claims-v3/e221/E221.md)), **measured** (the session's records), **desk check** (this lane's runs of the committed code on copies of the committed files) and **REPORTED** (verify-e221d's record, not re-run here).*

## 1. Check B's list leaves out one of the lab's card days on this box (verify-e221d's finding 2; low)

**What README.md says** (note 2, and row B on line 41, in the same words): no other E221 session ran on aifoundry1 while this one did (07:17:46-07:54:44), "and no other session committed in the lab within a day on that box overlaps it". The list names twelve sessions, E217's seven and E219's five (all the model session's), each apart.

**What it leaves out.** `box_e221.py` reads a committed `session/queue.json` under `--lab` only when the queue names a card on the box. It takes `q.get("card") or ""` and skips the queue when its first two characters are not the box's (lines 68 and 71). The queues it does read carry a `card` key: the model session's sessions, and on aifoundry2 the lab's card days E216 and E220 arm B. The lab's card days on aifoundry1 carry none. So check B read none of them there, though the checker's own description promises "the lab's own card days, E220 among them when committed" (lines 5-7). There are four such committed card days on aifoundry1, all on card 1:

| folder | the card day | span (PST) | its data commit | its T0, from this session's T0 (07:17:46 PST Fri 20 Nov) | inside check B's window (a day either way) | against this session |
|---|---|---|---|---|---|---|
| `2026-11-17-e206-matmul-sweep-aifoundry1-c1` | E206 arm B, card 1 | Tue 17 Nov 00:13:25-01:38:14 | `79340bfa` (Tue 01:42:43) | -79.07 h | no | apart |
| `2026-11-18-e213-blind-matmul-aifoundry1-c1` | E213 arm B, card 1 | Wed 18 Nov 15:15:27-15:45:12 | `b0c727c5` (Wed 15:49:38) | -40.04 h | no | apart |
| `2026-11-19-e215-blind-matmul-aifoundry1-c1` | E215 arm B, card 1 | Thu 19 Nov 13:42:22-14:10:55 | `4f648f24` (Thu 14:14:38) | -17.59 h | **yes: left out** | apart |
| `2026-11-20-e220-blind-matmul-aifoundry1-c1` | E220 arm A, card 1 | Fri 20 Nov 14:55:15-15:38:38 | `fd074f9e` (Fri 15:41:40) | +7.62 h | yes, but committed only after this directory's commit (and not read at main either) | apart |

So the list should also have named E215 arm B, Thu 19 Nov 13:42:22-14:10:55 PST: apart. It began 17.59 h before this session's T0 and ended long before it, so the statement holds with it, and **B PASS stands**. E220 arm A ran after this session's close and was committed after this directory's commit; its queue names no card either, so the line leaves it out at today's main too. It is apart as well.

**What this lane ran** (desk check): it read every committed `session/queue.json` at GitHub main `e5ae242a`, 65 of them, as data. 13 name no card, and 4 of those are on aifoundry1 (by their folder names, which name the box and the card). The spans above are each queue's own `t0` to `t_close_ms`. None overlaps any of E221's six aifoundry1 sessions. verify-e221d's own span check of the 37 sessions committed on aifoundry1 and aifoundry2 since Wednesday also found no overlap with any E221 session (REPORTED).

## 2. Check B's reproduce line leaves out the listing (verify-e221d's finding 3; low)

**What README.md says** (its section "Reproduce", line 85), verbatim:

```
python3 -I -B box_e221.py session --others ../2026-11-20-e221-mmsweep6-a1c1-S1/session --lab ../../../.. --out box.json --txt box.txt   # --lab: the lab's committed sessions on the box within a day, read at the commit named in note 6
```

**The line with every input the check read** (the data lane's step, written from this directory; the input in angle brackets is not in the repository, and README.md's last paragraph names it):

```
python3 -I -B box_e221.py session --others ../2026-11-20-e221-mmsweep6-a1c1-S1/session --listing <the lab's listing of the box's sessions folder, made at this session's copy> --lab ../../../.. --out box.json --txt box.txt   # --lab: read at the commit named in note 6
```

**Why.** The committed check B output names the stopped first start of a1c1-S1, `1795182836-a1c1-S1 (T0 05:53:56; not copied: only its start is known)` (README.md quotes it in note 2 and row B). `box_e221.py` writes that row only from a listing of the box's sessions folder (its lines 55-62). A line of the listing counts when it holds a name of the form `<10-digit T0>-a<box>c<card>-S<n>` on this box that is neither this session nor one of `--others`. The data lane made that listing on the box at this session's copy. It lists the model session's own folder on the box, which the lab does not publish. A file holding the one line `1795182836-a1c1-S1` stands in for it exactly (section 3's block). The printed line does give `--others`: the one E221 session of this box that ran before this one, the folder committed beside this one (`others_dirs` in the committed `box-e221-a1c0-S1.json`). verify-e221d's run "as printed" left it out, so its finding reads as if the line gave `--lab` alone. The one input the line leaves out is the listing.

**What this lane ran** (desk check, from this directory in two copies of every committed `session/queue.json`: one at this directory's data commit `3b89d84a` (the tree note 6 names, `2a509f5a`, with this directory added) and one at GitHub main `e5ae242a`):

- The line as printed: rc 0, and B PASS. Both outputs differ from `box-e221-a1c0-S1.json` and `.txt` only by that row. In the JSON, `listed_not_copied` is empty, and the statement that quotes it lacks the row. The `.txt` is the same statement, so it lacks the row too.
- With `--listing` of the one-line file, both outputs equal the committed files byte for byte. With the data lane's own listing in its place, they are byte for byte too.
- At main the three results are the same: the lab's later card day on this box, E220 arm A, is not read there either (section 1).

## 3. Files and how to reproduce

| file | what | label |
|---|---|---|
| `README.md.dated-note-1.md` | this note | post hoc |
| `SHA256SUMS-note1` | the sha256 of this note, `README.md` and `SHA256SUMS` | - |

```
sha256sum -c SHA256SUMS-note1
printf '%s\n' 1795182836-a1c1-S1 > listing.txt
python3 -I -B box_e221.py session --others ../2026-11-20-e221-mmsweep6-a1c1-S1/session --listing listing.txt --lab ../../../.. --out box.json --txt box.txt
```

`box.json` and `box.txt` equal `box-e221-a1c0-S1.json` and `.txt` byte for byte. This holds in a checkout of this directory's data commit, where `--lab ../../../..` is the repository's top and reads the tree note 6 names. It also holds at GitHub main `e5ae242a`. It needs `python3` to be `/usr/bin/python3` 3.12.3 (the JSON files name the interpreter and its version).

**What stays as it was:** every other line of README.md. Its other reproduce lines reproduce as printed: `sha256sum -c`, the checker, the registered reducer, `spot_time_e208.py`, `window_e221.py` and check K's block (verify-e221d's record, REPORTED; this lane re-ran the window line, byte for byte). `never_e221.py`'s line needs the whole lab tree at the commit note 6 names, and neither verify-e221d nor this lane re-ran it. verify-e221d re-read the never-run labels with its own code instead: 9 of 9 equal (REPORTED).

SPDX-License-Identifier: Apache-2.0
