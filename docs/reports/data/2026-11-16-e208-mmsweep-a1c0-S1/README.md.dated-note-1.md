# E208 session a1c0-S1's data README, dated note 1 (Mon 16 Nov 2026; after the data verifier): 45 of the 46 arm and anchor runs are read for energy, not 46; the anchor's figures over its 8 runs read; a boundary sample in one null run (post hoc)

*Written on aifoundry2 from about 23:10 PST on Mon 16 Nov 2026 (week 47) by the clock. This was desk work only: no card, no other lab
box, no device and no post. It was written by the lab's lane `fix-e208d` of round Q200, after this directory's data verifier,
`verify-e208d`. The verifier's verdict was "holds with fixes" (its record, REPORTED: with its own code it re-derived all six E208
sessions' reductions from their raw files and found 0 mismatches). Of 549 numbers and facts in the six READMEs, it found 541 that
agree and 8 that differ. All 8 come from two README findings, and one of them is this directory's. [`README.md`](README.md) and [`SHA256SUMS`](SHA256SUMS) (lab
`c2d6536c`, 20:32:50 PST Mon 16 Nov 2026) stay as committed, and so does every data file. **No datum, reduction, check or rule
changes, nothing is scored, and no forecast number is here.** **Every figure below is post hoc to the data commit.** The figures come
from four places. (a) This directory's committed files. (b) This lane's own code,
[`posthoc_note1_e208.py`](posthoc_note1_e208.py), which reads the raw launch records and the committed reduction and imports nothing
from the kit or the reducer. Its output is in `posthoc-note1-e208-a1c0-S1.txt` and `.json`. (c) The registered reducer, re-run by this
lane from a copy at its sha256 on the committed `session/`. Its output equals the committed `data-e208-a1c0-S1.json` in every value,
and the same holds for all six sessions. (d) Desk checks of the registered code, cited by line number at the sha256 listed in section 4. The
interpreter throughout was `/usr/bin/python3` 3.12.3 with `-I -B` on aifoundry2. Labels: **registered** ([`E208.md`](../../../../tools/claims-v3/e208/E208.md)
section 7 and the registered reducer), **measured** (the session's records, and the registered reducer's output from them),
**desk check of code**, **post hoc** (this lane's desk arithmetic after the data, deciding nothing) and **REPORTED** (verify-e208d's,
not re-run here).*

## 1. The correction: run 041 is capped, so 45 of the 46 arm and anchor runs are read for energy (verify-e208d's finding 1, low)

**What README.md says** (its section "The reduction", lines 45 and 46), verbatim:

> 46 of the 46 runs of arms and the anchor carry an energy figure there

> **The anchor** (`4x8x8-int8-rnd`, 9 runs): time an op 2.1705-2.1772 us; power over idle 16.88-17.38 W; energy over idle
> 35.82-36.87 nJ an op (mean 36.56, sd 0.35).

**The registered rule** (E208.md section 7, verbatim): "**Capped** (governed cards): of the launches starting 1.0 s or more after
their process's launch 0, fewer than 80% in the 800 MHz band. A capped run's energy is not read nor contrasted; a `time` run is never
read for energy." The reducer applies it where it reads energy (`energy_read()`, `reduce_mms.py` lines 490-494; desk check of code).

**What the records show** (measured; this lane's own re-derivation of the capped flag from the raw launch records agrees with the
reducer's flag and share on all 50 runs):

- Anchor run `041-4x8x8-int8-rnd` is **capped**. Of its 11 launches that start 1.0 s or more after its process's launch 0, 8 are in
  the 800 MHz band. That is 0.727, under the registered 0.80.
- Its kernel clock reached the 800 MHz band at launch 3 (1.36 s in). It fell to 600 MHz at launches 6 and 7 (2.64-3.11 s in) and
  read 643 MHz at launch 8. It held 800 MHz from launch 9 (4.04 s in) to the end.
- No other run of this session is capped.

**So the two lines should read** (post hoc):

- "**45** of the 46 runs of arms and the anchor carry an energy figure there". Anchor run 041 is capped, and the registered rule does
  not read its energy.
- "**The anchor** (`4x8x8-int8-rnd`, 9 runs, **8 of them read for energy**): time an op 2.1705-2.1772 us (all 9 runs, since a capped
  run's time is read); power over idle **17.08-17.38 W**; energy over idle **36.31-36.87 nJ an op (mean 36.65, sd 0.23)** over the 8
  runs read."
- With the registered die-start correction, already in the JSON's `J_op_corr`, the 8 runs read give 36.16-36.95 nJ an op (mean
  36.71).

**Where the reduction already had this right** (measured):

- The anchor arm's energy is over 8 runs (`n_energy_runs` 8). Its row in `reduce-e208-a1c0-S1.txt` reads 17.26 W and 36.65 nJ an op.
- The die slope's fit is over 8 anchors (`die_slope.n_anchors` 8).
- Run 041 has no die-corrected figure.
- The reducer still writes run 041's window figures: 16.88 W and 35.82 nJ an op in `data-e208-a1c0-S1.json`. It also lists every
  anchor run that ran, capped or not, in its `anchors` list (`reduce_mms.py` lines 566-567) and in the printed table's `anchors` line.
  That listing is not a reading: no reading uses those two figures.

**What stays as it was:** every other line of the README stands. That includes its die-start correction line, which already gives
the reducer's 8-anchor fit, and its null runs. Every data file, the reduction and the lab's checks C0-C8 were right all along.

## 2. How the README went wrong (desk check of code)

The data lane's own README script, which is not committed, made two slips:

- It counted a run as carrying an energy figure when the run's primary view held a power figure. The registered reducer writes one
  for a capped run's window too, because it applies the capped rule where it reads energy, not where it computes a view.
- It took the anchor line from the reducer's `anchors` list, which lists every anchor run that ran.

The same cause gave a2c0-S2's README its wrong counts (that directory's dated note 1). This lane ran the same check on the other four
E208 sessions, and their READMEs' counts and anchor lines are right:

- a2c0-S1: 69 of 69 arm and anchor runs read; its 9 capped runs are all time-only, as its README says.
- Card 1's sessions (a1c1-S1, S2 and S3): never capped; 82, 82 and 31 runs read, as stated.

## 3. The verifier's other reading on this directory: a boundary sample counted twice in null run 049-null-4 (verify-e208d's finding 3, info; no change)

**The mechanism** (desk check of code):

- A view gathers each launch's board samples with a window closed at both ends (`reduce_mms.py` line 306, with `between()` at lines
  137-139).
- A null run's pretend launches touch end to end (lines 377-379).
- So a sample whose time falls exactly on a shared boundary is counted once for each launch.

**What it changes** (post hoc: this lane re-ran the registered reducer's copy, and beside it a copy whose line 306 counts each sample
once, on all six sessions):

| run | samples counted twice | largest change in a mean-based dP figure | median-based dP | the session's null means |
|---|---|---|---|---|
| this session's `049-null-4` | 2 in `burst`, 1 in `win` | 0.0026 W (`win` dP 0.0342 W counted twice, 0.0316 W counted once) | 0.0003 W | 0.00065 W at most (e.g. `win.dP_line` +0.0478 to +0.0472 W) |
| a1c1-S2's `006-null-2` | 1 | 0.0031 W | 0.020 W (`dP_med_w`, a median over 55 samples against 54) | 0.0008 W at most |

- No other run of E208 changes, and no measured run does.
- verify-e208d REPORTED "0.003 W or less". To three decimals that holds for the mean-based figures (at most 0.0031 W): the primary dP
  and the three baseline rules the null summaries give. The median-based side figure in a1c1-S2's null moves 0.020 W.
- **The registered code governs**, so nothing changes here. a1c1-S2's README needs no correction and gets no note: its figures are in
  this table.

## 4. Files, the code cited, and how to reproduce

| file | what | label |
|---|---|---|
| `README.md.dated-note-1.md` | this note | post hoc |
| `posthoc_note1_e208.py` | this lane's code: the capped flag re-derived from the raw launch records and compared with the reduction's; the runs read for energy; the anchor's figures over the runs read and over every anchor run (Python's own modules; reads only) | lab code, post hoc |
| `posthoc-note1-e208-a1c0-S1.txt`, `posthoc-note1-e208-a1c0-S1.json` | its printed lines and its output on this directory | post hoc |
| `SHA256SUMS-note1` | the sha256 of the four files above, `README.md` and `SHA256SUMS` | - |

The registered code this note cites, at the registration's sha256 (lab `d005dc53`):

| file | sha256 |
|---|---|
| `tools/claims-v3/e208/E208.md` | `5e0cf91cb369382b3c71a7379985fdf06f57a144db61104e4fc0c7f64396b971` |
| `tools/claims-v3/e208/proposal/src/reduce_mms.py` (the registered reducer) | `b9e32618020d28a590a615f97e5655c1ea458a6a757bf5658f2517a87fc3e0a5` |
| `tools/claims-v3/e208/proposal/src/mms_common.py` (its constants) | `c3fc7883544ad73c3e455f7e950b62b9b155fd2ed972cee5e3524d74a378569c` |

```
sha256sum -c SHA256SUMS-note1
python3 -I -B posthoc_note1_e208.py session data-e208-a1c0-S1.json --json posthoc.json
```

The second line prints `posthoc-note1-e208-a1c0-S1.txt` and writes `posthoc-note1-e208-a1c0-S1.json`, byte for byte. It exits 0
when every re-derived capped flag equals the reduction's.

SPDX-License-Identifier: Apache-2.0
