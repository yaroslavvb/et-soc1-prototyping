# E208 session a2c0-S2's data README, dated note 1 (Mon 16 Nov 2026; after the data verifier): 68 of the 69 arm and anchor runs are read for energy, not 69; 9 of the 11 time-only runs are capped, not 10 (post hoc)

*Written on aifoundry2 from about 23:10 PST on Mon 16 Nov 2026 (week 47) by the clock. This was desk work only: no card, no other lab
box, no device and no post. It was written by the lab's lane `fix-e208d` of round Q200, after this directory's data verifier,
`verify-e208d`. The verifier's verdict was "holds with fixes" (its record, REPORTED: with its own code it re-derived all six E208
sessions' reductions from their raw files and found 0 mismatches). Of 549 numbers and facts in the six READMEs, it found 541 that
agree and 8 that differ. All 8 come from two README findings, and one of them is this directory's. [`README.md`](README.md) and [`SHA256SUMS`](SHA256SUMS) (lab
`eed9624f`, 20:32:59 PST Mon 16 Nov 2026) stay as committed, and so does every data file. **No datum, reduction, check or rule
changes, nothing is scored, and no forecast number is here.** **Every figure below is post hoc to the data commit.** The figures come
from four places. (a) This directory's committed files. (b) This lane's own code,
[`posthoc_note1_e208.py`](posthoc_note1_e208.py), which reads the raw launch records and the committed reduction and imports nothing
from the kit or the reducer. Its output is in `posthoc-note1-e208-a2c0-S2.txt` and `.json`. (c) The registered reducer, re-run by this
lane from a copy at its sha256 on the committed `session/`. Its output equals the committed `data-e208-a2c0-S2.json` in every value,
and the same holds for all six sessions. (d) Desk checks of the registered code, cited by line number at the sha256 listed in section 3.
The interpreter throughout was `/usr/bin/python3` 3.12.3 with `-I -B` on aifoundry2. Labels: **registered** ([`E208.md`](../../../../tools/claims-v3/e208/E208.md)
section 7 and the registered reducer), **measured** (the session's records, and the registered reducer's output from them),
**desk check of code**, **post hoc** (this lane's desk arithmetic after the data, deciding nothing) and **REPORTED** (verify-e208d's,
not re-run here).*

## 1. The correction: arm run 052 is capped, so 68 of the 69 arm and anchor runs are read for energy, and 9 time-only runs are capped (verify-e208d's finding 2, low)

**What README.md says** (its section "The reduction", line 44), verbatim:

> 69 of the 69 runs of arms and the anchor carry an energy figure there; the 11 time-only runs carry none (never read for energy; 10
> of them capped by the governor rule)

**The registered rule** (E208.md section 7, verbatim): "**Capped** (governed cards): of the launches starting 1.0 s or more after
their process's launch 0, fewer than 80% in the 800 MHz band. A capped run's energy is not read nor contrasted; a `time` run is never
read for energy." The reducer applies it where it reads energy (`energy_read()`, `reduce_mms.py` lines 490-494; desk check of code).

**What the records show** (measured; this lane's own re-derivation of the capped flag from the raw launch records agrees with the
reducer's flag and share on all 84 runs). The session has **10 capped runs**:

- **9 time-only runs**: `018-1x2x2-fp32-rnd`, `024-2x1x4-fp32-rnd`, `028-1x2x4-fp32-rnd`, `030-1x4x4-fp32-rnd`, `062-1x1x6-fp32-rnd`,
  `066-1x1x2-fp32-rnd`, `068-1x1x10-fp32-rnd`, `078-1x1x8-fp32-rnd` and `083-1x1x4-fp32-rnd`. In each, 5 to 7 of the 11 launches
  that start 1.0 s or more after the process's launch 0 are in the 800 MHz band (0.455-0.636).
- **1 arm run**: `052-1x1x1-int8-ones`, the arm's only run in this session. 9 of its 12 launches past 1.0 s are in the band, which is
  0.750, under the registered 0.80.
  - Its kernel clock reached the 800 MHz band at launch 3 (1.34 s in; launch 2 read 789.95 MHz).
  - It fell to 600 MHz at launches 4 and 5 (1.71-2.21 s in) and read 681 MHz at launch 6.
  - It held 800 MHz from launch 7 (3.14 s in) to the end.
- No anchor run is capped.

**So the line should read** (post hoc): "**68** of the 69 runs of arms and the anchor carry an energy figure there (arm run
`052-1x1x1-int8-ones` is capped, and the registered rule does not read its energy); the 11 time-only runs carry none (never read for
energy; **9** of them capped by the governor rule)".

**What follows** (measured):

- The arm `1x1x1-int8-ones` has no energy figure from this session. Its row in `reduce-e208-a2c0-S2.txt` shows "-" in every energy
  column and capped 1. Its time an op, 0.491 us, is read.
- The reducer still writes the capped run's window figures in `data-e208-a2c0-S2.json`, but no reading uses them.
- On aifoundry2 the arm's energy comes from session a2c0-S1 alone (post hoc). Its run `028-1x1x1-int8-ones` there has 13 of 13
  launches in the band, is read, and its row in `reduce-e208-a2c0-S1.txt` gives 9.02 nJ an op.

**What stays as it was:** every other line of the README stands. That includes the anchor line: no anchor run is capped, all 9 are
read, and this lane's arithmetic gives the README's figures (time an op 2.1686-2.1813 us; power over idle 18.24-18.66 W; energy over
idle 38.79-39.68 nJ an op, mean 39.21, sd 0.35). Every data file, the reduction and the lab's checks C0-C8 were right all along.

## 2. How the README went wrong (desk check of code)

The data lane's own README script, which is not committed, made two slips:

- It counted a run as carrying an energy figure when the run's primary view held a power figure. The registered reducer writes one
  for a capped run's window too, because it applies the capped rule where it reads energy, not where it computes a view.
- It put the session's count of capped runs of every role (10) into the sentence about the time-only runs.

The same cause gave a1c0-S1's README its wrong counts (that directory's dated note 1, which also records verify-e208d's finding 3 on
two null runs elsewhere in E208). This lane ran the same check on the other four E208 sessions, and their READMEs' counts are right:

- a2c0-S1: 69 of 69 arm and anchor runs read; its 9 capped runs are all time-only, as its README says.
- Card 1's sessions: never capped.

## 3. Files, the code cited, and how to reproduce

| file | what | label |
|---|---|---|
| `README.md.dated-note-1.md` | this note | post hoc |
| `posthoc_note1_e208.py` | this lane's code: the capped flag re-derived from the raw launch records and compared with the reduction's; the runs read for energy; the anchor's figures over the runs read and over every anchor run (Python's own modules; reads only) | lab code, post hoc |
| `posthoc-note1-e208-a2c0-S2.txt`, `posthoc-note1-e208-a2c0-S2.json` | its printed lines and its output on this directory | post hoc |
| `SHA256SUMS-note1` | the sha256 of the four files above, `README.md` and `SHA256SUMS` | - |

The registered code this note cites, at the registration's sha256 (lab `d005dc53`):

| file | sha256 |
|---|---|
| `tools/claims-v3/e208/E208.md` | `5e0cf91cb369382b3c71a7379985fdf06f57a144db61104e4fc0c7f64396b971` |
| `tools/claims-v3/e208/proposal/src/reduce_mms.py` (the registered reducer) | `b9e32618020d28a590a615f97e5655c1ea458a6a757bf5658f2517a87fc3e0a5` |
| `tools/claims-v3/e208/proposal/src/mms_common.py` (its constants) | `c3fc7883544ad73c3e455f7e950b62b9b155fd2ed972cee5e3524d74a378569c` |

```
sha256sum -c SHA256SUMS-note1
python3 -I -B posthoc_note1_e208.py session data-e208-a2c0-S2.json --json posthoc.json
```

The second line prints `posthoc-note1-e208-a2c0-S2.txt` and writes `posthoc-note1-e208-a2c0-S2.json`, byte for byte. It exits 0
when every re-derived capped flag equals the reduction's.

SPDX-License-Identifier: Apache-2.0
