# E199's data README, dated note 1 (Mon 16 Nov 2026; after the data verifier): the scorer's recorded input path, the null rate beside each FAIL, step 12's delay and the pooled slope; three nits answered (post hoc)

*Written on aifoundry2 from about 05:44 PST on Mon 16 Nov 2026 (week 47) by the clock, desk only (no card, no lab box, no device, no
post), by the lane `fix-e199d` of Q191, after this directory's data verifier `verify-e199d` (holds with fixes: two low findings and five
nits, none of them a fault in a datum or a verdict; with its own filter, reducer and scorer, importing nothing from the kit, it removed the
same 22 of 36,150 samples, matched the registered reduction's 10,572 fields with the largest relative difference 3.8e-13, and matched the
scorer's 8 verdicts and 818 fields). [`README.md`](README.md) and [`SHA256SUMS`](SHA256SUMS) (lab `6d1f3a5a`, 05:12:14 PST Mon 16 Nov
2026) stay as committed. **No number, rule, verdict or check reading changes, nothing is re-scored, and no number of the sealed card-1
forecast is here** (the lab knows it only by its sha256, E199.md's freeze line 2; the model session scores it privately). **Every figure
below is post hoc to the data commit.** Where the figures come from: (a) E199's registered pipeline, re-run by this lane from the committed
raw files (section 1); (b) [`E199.md`](../../../../tools/claims-v3/e199/E199.md) as registered; (c) the card lane's own records of step 12;
(d) verify-e199d's own code, REPORTED (not re-run here). Interpreter: `/usr/bin/python3` 3.12.3 on aifoundry2, for step 13 and for this
lane's re-run. Labels: **registered** (E199.md, E192.md), **measured** (the session's records, and the registered pipeline's outputs from
them), **desk check of code**, **post hoc** (desk arithmetic after the data, deciding nothing), **REPORTED** (verify-e199d's, not re-run
here).*

## 1. The scorer's recorded input path (verify-e199d's finding 1, low)

The registered scorer records the reduction's path exactly as its command line gives it: `"card1_file": {"path": card1_path, ...}`
([`score_e199.py`](../../../../tools/claims-v3/e199/score_e199.py) lines 416 and 427, sha256 `e578bf74...`; a desk check of code). Step 13
gave it the reduction at the card lane's scratch location on aifoundry2, so step 13's `scores-e199.json` (sha256 `64d3b218...`, not
committed) holds an absolute home-directory path that names a login. **No lab file carries it:** the data commit holds no step-13 output
(the README's "The commits").

**This lane's re-run** (post hoc, 05:52:03-05:52:11 PST, inside one of the round's CPU slots, with no device node reachable):

1. the committed `run/telemetry.jsonl.gz` unpacked, and `run/runs.jsonl` and `run/marks.jsonl` copied, each equal to its line in
   `session/MANIFEST.sha256` (the box's bytes), as step 13 checks;
2. at the lab's HEAD `4bc7a07a` (this directory clean), the registered tools at the sha256 step 13 printed: `prefilter_e199.py`
   (`79c699ec...`, with E151's `railfilter_e151.py` at `87bffb5f...`), E192's reducer `reduce_intbits.py` (`715fddaa...`), E192's checker
   `check_e192.py` (`ceb99e7c...`), `score_e199.py` (`e578bf74...`), and the reducer again on the unfiltered telemetry;
3. the scorer run from a directory laid out as the repository, given the reduction by its repository path,
   `docs/reports/data/2026-11-16-e199-intbits-aifoundry1-c1/intbits-e199.json`.

What it gave (measured; sha256):

| output | step 13 (05:18:57-05:19:03 PST) | this lane's re-run |
|---|---|---|
| the filter's census `railfilter-e199.json`, and its filtered `telemetry.jsonl`, `runs.jsonl` and `marks.jsonl` | `518aee91...`, `54d4d913...`, `d89caf26...`, `e25b8275...` | the same bytes |
| `intbits-e199.json` (the reduction, filtered) | `5033f861...` | the same bytes |
| `checks-e199.json` (E192's checks on card 1) | `905586f8...` | the same bytes |
| `intbits-e199-unfiltered.json` (REPORTED beside) | `066d5f6c...` | the same bytes |
| `scores-e199.json` | `64d3b218...` | `69a55603...`: **1 of its 2,748 values differs, `card1_file` > `path`**, now the repository path above; the file's own `sha256` (`5033f861...`) and every verdict, count, scale, z and ratio are equal |
| the printed lines | step 13's log, 135 lines | the same 135 lines, in order |

**The scores file to commit beside the reduction is therefore this re-run's** (sha256
`69a556037ab75390c67403de721bc86be9c1f14c6670ab5df800df202c2989fa`): the registered scorer's own output on the same bytes, with no home
path in it. The records lane's dated note says which file it committed.

## 2. The null rate beside each FAIL (verify-e199d's finding 2, low)

E199.md 6.8 (registered before any datum): "**Beside any family FAIL: the null rate at its number of passes**" ... "A FAIL is still
reported as FAIL, with the row for the smallest number of measured passes behind it." Every decided price in all four families rests on 8
measured passes on card 1 (`scores-e199.json` > `families` > `card1_passes` reads [8, 8] in A, B, C and D; measured), so the row is
E199.md 6.8's row for 8 passes. Beside the registered scorer's words (step 13's printed lines; re-derived by verify-e199d with its own code;
the same lines in this lane's re-run):

| rule | family, meter | the scorer's word (decided; hold / miss) | the null rate at 8 passes (E199.md 6.8's table: the share of draws with no card difference that read FAIL) |
|---|---|---|---|
| **E199-T1** (the headline) | A, board, per-arm contrasts | **FAIL** (29 of 31; 21 / 8; FAIL at 5 misses) | **1.5 %** |
| **E199-T2** (the headline) | A | **FAIL** (23 / 6 at s* 1.03393; s_hat 1.0408 +- 0.02368, which meets the allowance [0.943145, 1.03707]) | **0.3 %** |
| E199-T1L | B, board ladders | FAIL (22 of 24; 14 / 8; FAIL at 4) | 6.3 % |
| E199-T2L | B | FAIL (14 / 8 at s* 1.03493; s_hat 1.05713 +- 0.04524, which meets it) | 1.5 % |
| E199-T1R | C, core rail, per-arm contrasts | FAIL (31 of 31; 24 / 7; FAIL at 5) | 2.3 % |
| E199-T2R | C | PASS (29 / 2 at s* 1.03707) | (0.5 %; a PASS needs none) |
| E199-T1RL | D, core rail ladders | FAIL (24 of 24; 18 / 6; FAIL at 4) | 4.3 % |
| E199-T2RL | D | PASS (21 / 3 at s* 1.03707) | (1.2 %) |

The rates are E199.md 6.8's simulation (600 draws a row; each price drawn from E192's own per-pass spread with no card difference, the
prices independent, "though the real ones share controls"), there labelled REPORTED, a desk check of code: reported beside, never a
verdict. Every FAIL stays FAIL.

## 3. Step 12's delay (verify-e199d's nit 3)

Step 12's first placement of this directory was refused at 04:53:00 PST (rc 16): the lab clone held another card lane's new data
directory (E196's, still untracked while it was being placed), and the card lane's own placement script places only into a clean clone,
so nothing was copied. After two bounded waits the card lane changed its own placement and commit scripts (lane scripts, not E199's kit and
not a registered item) at about 05:12 to allow another lane's untracked new data directory and nothing else; it placed this directory at
05:12:09 and committed and pushed it at 05:12:14 (37 files, 0 paths outside this directory, the other lane's files untouched), and
released the hold and the booking the same second. That was about 19 minutes after the README was written (04:52:47) and 30 minutes
after the session's end (04:42:32): no card time, window or rest was affected.

## 4. The pooled temperature slope behind the corrected prices (verify-e199d's nit 5; REPORTED and post hoc)

E192's reducer (registered unchanged by E199.md 6.5) corrects every arm-minus-control power for temperature with one pooled slope a meter,
fitted over all arm-control pairs of the used passes (E192.md section 4, "Temperature (primary)"). Its fit on card 1 (measured,
`intbits-e199.json` > `beta_W_per_C`): board **0.1372 W/°C** and core rail **-0.0562 W/°C**, over a pair-demeaned temperature spread
(`sum_dT2`) of **0.938 °C²**. On aifoundry3 (E192's committed `intbits-e192.json`): board 0.0552 W/°C and rail 0.0496 W/°C, over
17.377 °C², about 18.5 times card 1's spread (post hoc arithmetic). Card 1's slopes rest on little temperature contrast, and its rail
slope has the other sign.

verify-e199d's post hoc readings with its own code (REPORTED; deciding nothing):

| reading | E199-T1 | E199-T2 | T1L | T2L | T1R | T2R | T1RL | T2RL |
|---|---|---|---|---|---|---|---|---|
| **registered** (E151's filter, then E192's reducer with its slope; E199.md 6.5 and 6.6) | FAIL (21 / 8) | FAIL (23 / 6) | FAIL | FAIL | FAIL | PASS | FAIL | PASS |
| no slope: both cards' uncorrected contrasts and ladders | FAIL (22 / 9) | FAIL (26 / 5 at s* 1.0371) | FAIL | FAIL | PASS | PASS | PASS | FAIL |
| no filter: the registered rules on the unfiltered telemetry | FAIL (21 / 8) | FAIL (23 / 6) | FAIL | FAIL | FAIL | FAIL | FAIL | FAIL |

**Which rule decides:** E199.md 6.5 registers the pipeline (E151's rail filter, then E192's reducer unchanged, its slope included) and 6.6
the verdicts, so the registered row is the reading; the other two rows are post hoc and change nothing. The headline, E199-T1 and E199-T2,
reads FAIL in all three; the core-rail families' words move with the slope and with the filter.

## 5. Three nits that need no change (verify-e199d's nits 4, 6 and 7)

- **Nit 4, the window file's label.** The card lane's runbook file `window.env` (not committed here) labels `RB_GO_EPOCH` "his go", but it
  holds 1794829229 = 03:40:29 PST, when step 1 recorded the window, not G = the booking, 03:37:03 PST (1794829023). Nothing reads it, and
  the bounds written beside it are G's: 03:37:03 + 1:30 = 05:07:03 and + 3:30 = 07:07:03, rounded up to 05:08 and 07:08 (the README's
  departure 3); from 03:40:29 they would read 05:11 and 07:11. The README's window stands.
- **Nit 6, a manifest line not committed.** `box-manifest.txt` line 29 names `build/e199/launch-T1794829335.out`, which is not in this
  directory; its sha256, `7576565f...`, is that of `session/session.log` (`box-manifest.txt` line 27, and [`SHA256SUMS`](SHA256SUMS)),
  which is.
- **Nit 7, the checker's pass count.** `check_e192.py`'s checks 1 and 2 count all 9 passes (3,240 launches and 324 runs, the warm-up pass 0
  included) while `checks-e199.json` > `used_passes` lists 1-8. Their words stand either way (verify-e199d; and a desk reading of the counts): check 1's failure counts are
  0 over all 9 passes, so 0 over passes 1-8 (PASS); check 2 fails on L1d misses in every one of the 324 runs, so in every run of passes 1-8
  too (FAIL).

## Files

[`SHA256SUMS-note1`](SHA256SUMS-note1) lists this note, with `README.md` and `SHA256SUMS` (unchanged). New files only: no committed file
changed.

SPDX-License-Identifier: Apache-2.0
