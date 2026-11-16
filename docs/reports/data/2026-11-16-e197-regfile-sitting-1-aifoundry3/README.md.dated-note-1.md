# E197 sitting 1's data README, dated note 1 (Mon 16 Nov 2026; after the data verifier): sitting 2 did not run, because the step-0 anchor read had no sitting-2 form; where the reduction's outputs go; three nits (post hoc)

*Written on aifoundry2 from about 06:54 PST on Mon 16 Nov 2026 (week 47) by the clock. Desk only: no card, no lab box, no device, no
post. Written by the lane `fix-e197d` of Q191, after this directory's data verifier `verify-e197d`. The verifier's verdict was holds
with fixes: one minor finding and four nits, none of them a fault in a datum, a check or a verdict. Its own reducer, written from E197.md
and importing nothing from the kit, re-derived all 13 trains, 21 prices and 24 anchors from the committed raw files (largest relative
difference 6.9e-13) and all 109 checker rows; the README's re-make gave step 13's bytes. [`README.md`](README.md) and
[`SHA256SUMS`](SHA256SUMS) (lab `ae3c1ee0`, 06:25:28 PST Mon 16 Nov 2026) stay as committed. **No number, rule, verdict or check reading
changes, nothing is scored, and no forecast number is here** (the model session scores its sealed forecast privately). **Every figure
below is post hoc to the data commit.** Where the figures come from: (a) the registered reducer
[`reduce_regfile.py`](../../../../tools/claims-v3/e197/proposal/src/reduce_regfile.py) and the kit's checker
[`check_e197.py`](../../../../tools/claims-v3/e197/check_e197.py), run by the README's "Re-make it" lines on this directory: this lane
re-ran both from the repository's tree at `b4a5f6f2` (which holds `ae3c1ee0` and no change to this directory) and got step 13's bytes
(section 2); (b) the card lane's runbook log and its step-0 record for sitting 2; (c) desk checks of the registered code, by line number
at the sha256 listed in section 5; (d) verify-e197d's readings where named. Interpreter: `/usr/bin/python3` 3.12.3 on aifoundry2.
Labels: **registered** ([`E197.md`](../../../../tools/claims-v3/e197/E197.md), the kit), **measured** (the session's records, the runbook's
log, and the registered reducer's and checker's outputs from them), **desk check of code**, **post hoc** (desk work after the data,
deciding nothing), **REPORTED** (verify-e197d's, not re-run here).*

## 1. Sitting 2 did not run: the step-0 anchor read had no sitting-2 form (verify-e197d's F1, minor; fail-safe)

**What E197 registers.** E197.md 6: sitting 2 is block E (230 more processes of T1, then T7 and T14; about 28 card-minutes, cap 35). It
"runs only after sitting 1 has run its smoke and at least one train block with no stop that names the card", and "its first card command
comes at least 40 minutes after sitting 1's end, in a window of its own (section 12), on the same Pacific day or a later one". Sitting 1
met the condition. The session's summary reads "SITTING-RESULT: smoke passed; train blocks complete 4 (A B C D); card stop none"
(06:10:45 PST, measured).

**What happened (measured, from the card lane's records).** This directory's data commit was pushed at 06:25:33 PST and step 13 ran at
06:26:11-06:26:14. The card lane then began sitting 2 on the same booking. Its step 0 is "the go's anchor lines at LAB's HEAD". It read
them at 06:29:16-06:29:17 PST, at HEAD `985554c6` (then the remote's main), and printed "GO-ANCHORS-E197: NOT AS STATED: 3 of 63
lines ...: no box step today (row E)", exit 1. The three lines:

| line | what it reads | wants | read |
|---|---|---|---|
| R6a | `git log --all --oneline -- 'docs/reports/data/*e197*' \| wc -l` | 0 | 1 (`ae3c1ee0` itself) |
| R6b | E197 data paths at every ref's tip | none | 75 |
| K8 | the same command as R6a (the kit's anchor 8) | 0 | 1 |

The card lane took row E: it released the booking at 06:29:34. Nothing was sent to the card or to aifoundry3 for sitting 2 (no step 1,
no step 2, no box step).

**Why (desk check of code).** The step-0 read is in neither the kit nor the registration. Row 0 of
[`CARD-LANE-BRIEF.md`](../../../../tools/claims-v3/e197/CARD-LANE-BRIEF.md) names `uptime` and "the go's anchor lines at LAB's HEAD", and
nothing more. The readiness check (`ready-e197`, READY WITH GAPS) wrote those lines as a script in its own desk folder, outside the
repository, from the land notes' anchors. Those anchors (the registration's anchor 6, the kit's anchor 8) want zero lines from
`git log --all -- 'docs/reports/data/*e197*'`, which holds only until the day's first sitting is committed. The script takes no
sitting, so R6a, R6b and K8 count every E197 data path in any ref; after sitting 1's own data commit they can only read NOT AS STATED.
The kit's own gate for sitting 2 already makes the distinction: step 2,
[`rb/s03_desk_e197.sh`](../../../../tools/claims-v3/e197/rb/s03_desk_e197.sh) lines 21-22 and 107-114, wants "before sitting 2, none but
sitting 1's own data directory (\*-e197-regfile-sitting-1-aifoundry3/)". E193's readiness check carried such a sitting form (its lines B1
and B2); E197's did not.

**The reading.** Fail-safe: a gate refused before any box step. No datum was lost, no rule was broken and no verdict changes. E197.md 11
(registered): "sitting 2 does not happen | sitting 1's reduction is E197's result: T1 at the first sitting's size, T7 and T14 NOT SCORED
(not run), and `dest_n8`, `read_n8` with them". That is E197's result as of this note. T1 stands at 134 processes (67 units), of
the 364 the registered plan pools from both sittings (the checker's T1 row: processes 134, planned 364). The checker's two NOT SCORED rows
are T7's and T14's gates (0 units each).

**What sitting 2 needs.** No amendment: E197.md 6 allows a later day. Four things:

1. **A sitting-2 form of the step-0 anchors.** It keeps every other line and replaces R6a, R6b and K8 with step 2's own rule, plus lines
   that pin sitting 1's directory to its data commit:
   - **S2a:** no `docs/reports/data/*e197*` path in any ref's history but sitting 1's own directory;
   - **S2b:** the same at every ref's tip;
   - **S2c:** sitting 1's directory present at HEAD;
   - **S2d:** the oldest commit in any ref that touches an E197 data path is `ae3c1ee0`;
   - **S2e:** since `ae3c1ee0`, sitting 1's directory has only gained files (dated notes, such as this one), and no committed file changed
     or went;
   - **S2f:** `ae3c1ee0` is an ancestor of HEAD.

   This lane drafted that form as a copy of the readiness script and desk-tested it in the desk's lab clone at its HEAD, read only
   (desk check of code; the draft is not committed and not verified):

   - the sitting-1 form read exactly R6a, R6b and K8 NOT AS STATED (3 of 63 lines, exit 1), as the card lane read them at 06:29:17;
   - the sitting-2 form read 66 of 66 lines as stated (exit 0);
   - with sitting 1's directory name swapped for a wrong one, S2a, S2b and S2c failed;
   - with the data commit's sha swapped for E196's (`4bc7a07a`, which touches no E197 path), S2d failed;
   - S2e's command counted 1 changed file on a data directory whose README a later commit modified.

   The test ran at 07:10:19-07:10:24 PST, at HEAD `b4a5f6f2`, inside the lab-git lock. Not run: a stand-in clone holding an extra E197
   path or a changed sitting-1 file (negative controls for the next readiness check).
2. **An independent verification of that form.**
3. **A new readiness check that runs it.** Sitting 2 also needs its own day, window (G = its booking, E197.md 12), booking and build
   (the brief: "else sitting 2 on a later day (its own window; its build started again that day)").
4. **The 40-minute rest** after any session of ours on aifoundry3 card 0 (E197.md 6).

If sitting 2 runs, its step 13 pools both sittings by unit (`rb/s24_reduce_e197.sh 2`, `regfile-e197.json`), "the pooled reduction,
which is then E197's registered result" (E197.md 7). Sitting 1's own reduction stays committed beside it.

## 2. The reduction's outputs go in a dated note beside the README; the README stays as committed (verify-e197d's F2, nit)

The README's section "Reduced (not here)" says step 13's outputs "are committed beside it by a later lane in a dated note, which fills
this section". **Dated clause:** read with the lab's practice (E195 data note 2, `250f825b`; E196 data note 2, `d362d84f`; E199 data
note 2, `60bae324`), that later note is a new file beside the README: `README.md.dated-note-2.md` here, with the outputs and its own sums
list. "Fills this section" means that note carries what the section points to. `README.md` itself is not edited.

Step 13 ran at 06:26:11-06:26:14 PST (measured, the runbook's log), after the data commit's push. It ran on this directory as committed:
the directory clean and named by a commit, every entry of `SHA256SUMS` OK, the history check holding, and the reducer at its registered
sha256. Its outputs (measured), which that note is to commit byte for byte, and this lane's re-run of the README's "Re-make it" lines
(07:02:45-07:02:48 PST; the three run files read "the box's bytes"):

| output | sha256 (step 13) | this lane's re-run |
|---|---|---|
| the reducer's JSON (`regfile-e197-s1.json`) | `6c742a8b546840380d66ff11e014d57274f41d45fb4b6b4ecb31a24aeb857139` | the same bytes |
| its printed lines (`regfile-e197-s1.txt`) | `e655b38d502b5d7069366a8bed56f1394dc3a8b4b883477e981154a60d7fc54c` | the same bytes |
| the checker's JSON (`checks-e197-1.json`) | `ad69afe589821ea0f5c67187e2d15159c1f9189d381cb67f679734a2ded91355` | the same bytes |
| the checker's printed lines (step 13's capture of its output) | `9cd4cf605cde0b95f9ba2497f8fc3ee7a0ab58535ee7262ff0a8ce113464c893` | the same bytes (110 lines) |

The checker's last line, as printed: "CHECKS READ: 109 rows (APPLIED 16, NOT SCORED 2, PASS 13, REPORTED 78)". verify-e197d's own re-make
gave the first three bytes too (REPORTED).

## 3. The three nits (verify-e197d's findings 3-5)

- **Finding 3 (nit, scans).** Step 12a scanned the commit's subject and body files. `commit_lab_inner.sh` then appended the round's two
  trailer lines: the session line and the co-author line. `ae3c1ee0`'s final message ends with them (desk check), and they hold the one
  "network" line the tier scan reads and the one mail address the public-text scan reads. That trailer is on every commit of the round since Q177, so
  nothing in E197 changes. This note's own commit message was scanned in full, trailer included, before the commit, and its pushed
  message is read back after the push.
- **Finding 4 (nit, post hoc reading).** "Nothing set" rests on two things:
  - the device-command audit: `dmcmd_audit` GO, 11 send sites, every one a READ
    ([`KIT.md`](../../../../tools/claims-v3/e197/KIT.md) 6);
  - the telemetry: every regulator setpoint and clock constant held over the 25,930 samples (verify-e197d, REPORTED), and 600 MHz in
    every one (measured, the README's Results).

  The TDP and the threshold were read once, at step 7 (05:27:28 PST: TDP 0 W, threshold 65 C, power state max_power, 600 MHz, 523 mV;
  measured), and not after the session. E197 registers no closing read, so this is no gap against E197.md. A closing configuration read
  in later kits would show it directly.
- **Finding 5 (nit, reported, never a gate).** The README's note 10 compares the box's kernel file (`a950ea13...`, different from the
  desk build's) and its `.text` (12,696 B, `ce8c93c6...`, the desk build's). It does not compare the 72 B `.rodata`, the only other loaded section
  (verify-e197d, REPORTED). The box's ELF bytes were not collected, so this desk cannot compare that section after the fact. verify-e197d
  reads the file difference as fitting the box's toolchain string, "(g1b306039a) 15.1.0", in `.comment` (REPORTED). Later build records
  can compare `.rodata` too. Nothing changes: E197.md 17.5 reports the kernel file and never gates on it.

## 4. What stays

`README.md` and `SHA256SUMS` stay as committed in `ae3c1ee0`, and no committed data file changed. Every check word stands as the kit's
checker prints it (measured). Until a sitting 2 runs, sitting 1's reduction is E197's result (E197.md 11). The reduction's dated note
is to publish the reduced prices beside the outputs. Nothing is scored here, and no forecast number is in this note.

## 5. Files

| path | what |
|---|---|
| `README.md.dated-note-1.md` | this note |
| `SHA256SUMS-note1` | the sha256 of this note, `README.md` and `SHA256SUMS` |

The code this note cites, at these sha256 (each pinned by E197's registration or kit sums or by step 0's lines):

| file | sha256 |
|---|---|
| `tools/claims-v3/e197/E197.md` | `5932e41a13dbc1833938b10cbc40ca850723029e60c231f1908426ef38ee8c35` |
| `tools/claims-v3/e197/proposal/src/reduce_regfile.py` (the registered reducer) | `f325bd0e3e916b81ee12304db7b47d79ad6daa5172ded19952f0ef1b0565eb87` |
| `tools/claims-v3/e197/check_e197.py` (the kit's checker) | `b0b3012db6cd3f22b06374af16f1423f6968375881189d17e5b2c2947bbe5fdc` |
| `tools/claims-v3/e197/rb/s03_desk_e197.sh` (step 2) | `e0e2a7713f4d5997d8c849081b113122a16babf2a9e18c7934394bee77661fe7` |
| `tools/claims-v3/e197/rb/s24_reduce_e197.sh` (step 13) | `a38b57af3d24733117a3b674174fd2263549f77467aeaa4638996f29b6cb2270` |
| `tools/claims-v3/e197/rb/check_history_e197.py` (the history check) | `8460d62da5aaa3cb9fb64e32004c91e348aa306bf91a92af5c36cb219385b165` |
| `tools/claims-v3/e197/CARD-LANE-BRIEF.md` | `c142796cfe16c9e24aa43195f14eca88813bd144f63cef55e5678317b61695a8` |
| `tools/claims-v3/e197/KIT.md` | `816571c0dab651bb73abdee337700e2acdcf349b5f197d9f51c61e7e9d99d8b5` |
| `tools/claims-v3/e197/DATA-README-FORM-e197.md` | `a8bc8c760ead6c67a93fc1a283279477b3cd0e2b69be9ae7893cafd88f53726f` |

SPDX-License-Identifier: Apache-2.0
