# E200 sitting 2's data README, dated note 1 (Mon 16 Nov 2026; after the data verifier): one collected file differs from the box's manifest, by the registered scrub alone; the first card command and the rest read two ways, and the kit's reading decides; the set-aside processes and the front-end ratios (post hoc, REPORTED); the second firmware read; a week number

*Written on aifoundry2 from about 10:37 PST on Mon 16 Nov 2026 (week 47) by the clock. Desk only: no card, no lab box, no device, no
post. Written by the lane `fix-e200d` of Q192, after this experiment's data verifier `verify-e200d` (desk only, 10:10-10:40 PST). The
verifier's verdict was holds with fixes, the fixes documentation only: one low finding, two nits and three for information, none of them
a fault in a datum, the reduction, a check, the clock rule, the seal, a gate or a release. Its own reducer, written from E197.md and
E200.md and importing nothing from the kit, re-derived both reductions from the committed raw files (1,114 values for sitting 1 and
1,240 pooled, 0 mismatches, largest relative difference 1.2e-13) and both checkers' rows (110 and 111), and the kit's own reducer and
checker and both READMEs' "Re-make it" lines gave step 13's bytes (REPORTED, verify-e200d's). [`README.md`](README.md) and
[`SHA256SUMS`](SHA256SUMS) (lab `ca53ed29`, 10:06:26 PST Mon 16 Nov 2026) stay as committed. **No number, rule, verdict or check reading
changes, nothing is scored, and no forecast number is here** (the model session scores its sealed forecast privately). **Every figure
below is post hoc to the data commit.** Where the figures come from: (a) the committed files of this directory and of sitting 1's
([`../2026-11-16-e200-regfile-sitting-1-aifoundry2/`](../2026-11-16-e200-regfile-sitting-1-aifoundry2/), `548d736e`), read again by
[`posthoc_note1_e200.py`](posthoc_note1_e200.py), whose printed lines are [`posthoc-note1-e200.txt`](posthoc-note1-e200.txt); (b) the
card lane's runbook log and its copy-back of the box's files (outside the repository); (c) desk checks of code, by line number at the
sha256 listed in section 8; (d) verify-e200d's readings where named (REPORTED). Interpreter: `/usr/bin/python3` 3.12.3 on aifoundry2.
Labels: **registered** ([`E200.md`](../../../../tools/claims-v3/e200/E200.md), E197.md by reference, the kit), **measured** (the sessions'
records and step 13's outputs from them), **desk check of code**, **desk arithmetic**, **post hoc** (desk work after the data, deciding
nothing), **REPORTED** (verify-e200d's, or a checker row that carries no verdict).*

## 1. One collected file differs from the box's manifest: the registered scrub (verify-e200d's F1, low, documentation)

`session/MANIFEST.sha256` is the box's list, written on the box before the collection (README.md, Files). Read line by line against
the committed files (desk check, this lane, 10:4x PST; `posthoc_note1_e200.py` section 1 prints it again):

- 33 lines; for 32 the committed file is at the manifest's sha256 (`run/telemetry.jsonl` as unpacked from `run/telemetry.jsonl.gz`);
- the one other is fwgate's read record:

| file | sha256 |
|---|---|
| the manifest's line for `./first/fwgate-aifoundry2-c0-20261116-093717.json` (the box's bytes) | `d912877d443929d30778d98f90428c37e3e2df3275ab2de8579af7274d15c283` |
| the committed `session/first/fwgate-aifoundry2-c0-20261116-093717.json` | `270c4bbd3133d52f8ede28a06685b6d948ab3624d990a128d72c2098fdfe181b` |

**Why.** The record holds one "~", in its line 34: `"ledger": "~/.local/state/fwgate/aifoundry2-c0.jsonl",` (fwgate's attempt
ledger for this card). With the box's home written back in place of that "~", the file's sha256 is the one on the manifest's line. The card lane's
copy-back of the box's file has the manifest's sha256 and differs from the committed file in line 34 alone (111 lines each). That is
the kit's collector at work, registered before any datum
([`collect_e200.py`](../../../../tools/claims-v3/e200/collect_e200.py)):

- step 4, the scrub, writes the box's home as "~" in every text file (docstring lines 28-30; `scrub()` lines 130-131);
- step 2, the box-tree gate, allows the box's home in a collected file only as the home itself, inside the box tree, or in this ledger
  path (lines 14-19).

In this sitting's files the box's home stood in that one line alone: the record's raw answer (`.stdout`, `.stderr`) and every other file
the manifest lists are at their manifest lines, so the scrub changed nothing else there. README.md's "Re-make it" lines set only the
three run files against the manifest (they print "the box's bytes"), so they never meet this line; a reader who checks every manifest
line meets it once, and this is its reason. The record's own verdict field reads "EQUAL" as committed (README.md's Results row quotes
the read in full).

**Dated sentence (Mon 16 Nov 2026, PST):** the registered scrub changed one line of one collected file here, line 34 of
`session/first/fwgate-aifoundry2-c0-20261116-093717.json` (fwgate's attempt-ledger path, the box's home written as "~"), so that file
alone differs from its line in `session/MANIFEST.sha256`; the run files and every other file the manifest lists are the box's bytes.

## 2. The first card command and the rest, read two ways; the kit's reading decides (verify-e200d's F2, nit)

**What E197.md 6 registers** (E200's by reference, E200.md 5 and 11): "A sitting's first card command is the first command of the
sitting that reaches the card or its management node (a configuration read included) or the sitting's first holder check, whichever
comes first ... The cap and the rest both count from that moment." The rest is at least 40 minutes after the previous session of ours
on this card (E200.md 11).

**Two readings of "the sitting's first holder check"** (desk arithmetic; the times are README.md's and sitting 1's, the moments of the
first card command are `session/first-card-command.txt`'s):

| | the kit's reading: step 7's first command (registered) | the other: step 4's look counted as the sitting's first holder check |
|---|---|---|
| sitting 1: the moment | 08:13:25 PST (fwgate's read) | 08:12:16 PST (the look) |
| sitting 1: the rest after E194's end, 00:49:00 (40 required) | 444.4 min | 443.3 min |
| sitting 1: card-minutes to its end, 08:57:03 (cap 50) | 43.63 | 44.8 |
| sitting 2: the moment | 09:37:16 PST (fwgate's read) | 09:18:32 PST (the look) |
| sitting 2: the rest after sitting 1's end, 08:57:03 (40 required) | 40.2 min | 21.5 min |
| sitting 2: card-minutes to its end, 10:03:43 (cap 35) | 26.45 | 45.2 |

verify-e200d gave 21.5 and 44.78 in the second column; 443.3 and 45.2 are this lane's.

**What the other reading would change.** Sitting 2's look fell inside its rest. E200.md 13 reads a rest gate before the sampler as "no
sitting (or none that day): no data", and its row "sitting 2 does not happen" makes sitting 1's reduction E200's result: T7 and T14
NOT SCORED (not run), `dest_n8` and `read_n8` with them, and T1 at sitting 1's size. That would change verdicts, so the rule that
decides is named here, and nothing is re-scored.

**The rule that decides: KIT.md 4, stated before any E200 datum.** E200's kit (`b4a5f6f2`, 06:57:03 PST, 76 minutes before sitting 1's
first card command) reads E197.md 6 so, in [`KIT.md`](../../../../tools/claims-v3/e200/KIT.md) section 4 (lines 105-106): "Step 7's
first command to the card: fwgate's one firmware read when its look reads NEEDS-READ, else the config read; both come before every
holder check of the session". Its last item (line 141) keeps E197's kit section 4 unchanged, and there
([`../../../../tools/claims-v3/e197/KIT.md`](../../../../tools/claims-v3/e197/KIT.md) lines 109-110): "k6's look (step 4) is the
runbook's look at the box, not the sitting's holder check: `et-who` runs `et-holders`, which stats the nodes and never opens them, so
it sends nothing to the card". E200's look, [`rb/s05_look_e200.sh`](../../../../tools/claims-v3/e200/rb/s05_look_e200.sh), reads
fwgate's look (no device), `et-who` as counts, `ps` and our own jobs, and says in its header (lines 19-20): "Nothing here opens a
device or takes a lock" (`et-who` lists holders through `tools/lab/et-holders`, which by its own header never opens the card's device
nodes). E197.md 18.2 lists "the look (`et-who`, `who`, `uptime`, `ps`) before and after" apart from "the first card command as
section 6 defines it", and E193 sitting A's data note 1 (section 2) read k6's look the same way. **So the registered readings stand:**
sitting 2's rest 40.2 minutes (README.md's "rest: 40 minutes", notes 3 and 9) and its 26.45 card-minutes of 35; sitting 1's 444 minutes
and 43.63 of 50; the pooled reduction is E200's registered result. Read this clause beside README.md's rest rows (Registered against
happened, "the second sitting's condition") and its notes 3 and 9.

## 3. The set-aside processes: no slow climbs (verify-e200d's F3, information; post hoc)

THE CLOCK RULE set aside 3 of this sitting's 266 train processes (block E, T1 processes 53, 126 and 224): C3 judged them OFF live,
never two in a row (measured, README.md), and C1, in step 13's reduction, set aside three for samples off 800 MHz after the 1.5 s
allowance, the same three (verify-e200d, REPORTED; this lane's sample test below finds the same). This lane's own read
(`posthoc_note1_e200.py` section 2; post hoc, deciding nothing; times in seconds after the process's first launch's start):

| process | climb to 800 MHz | the one run off 800 MHz | clocks in it | die (`minshire[0]`) | latch (`minshire[2]`) | board |
|---|---|---|---|---|---|---|
| E, T1 53 | 0.069 s | 3.271-4.472 s (13 samples) | 600, 700 MHz | 57-58 C | 61 C | 29.21-40.57 W |
| E, T1 126 | 0.009 s | 0.810-2.022 s (13 samples) | 600, 700 MHz | 57-58 C | 61 C | 29.27-40.51 W |
| E, T1 224 | 0.075 s | 0.875-2.076 s (13 samples) | 600, 700 MHz | 58 C | 61 C | 29.39-40.87 W |

Each reached 800 MHz within 0.08 s of its first launch's start and left it once, for 1.20-1.21 s from the first off sample to the last;
the clock was at 800 MHz again on the next sample. Over each run the die and the board read under the card's threshold (65 C) and TDP
(65 W) as configured; what moved the clock was not read. These were not slow climbs: the largest climb of this sitting's 266 processes
was 1.369 s (under C1's 1.5 s), the median 0.074 s, and 188 read 800 MHz within 0.1 s of their first launch's start. Sitting 1's six
were alike (its note 1, section 3): climbs 0.067-1.181 s, one run off 800 MHz each, of 1.10-1.20 s, from 0.88-3.98 s in, die 52-58 C,
board 25.06-40.62 W. verify-e200d's wording, "dipped to 600/700 MHz for 0.5-1.2 s, between 1.52 and 5.08 s in" (REPORTED), counts the
part of each run from 1.5 s on, the samples C1 judges. Nothing changes: the registered rule set these processes aside, and these lines
decide nothing.

## 4. The front-end ratios beside T7 and T14 (verify-e200d's F4, information; REPORTED)

The kit's checker, on step 13's pooled reduction, reports instruction-cache misses per iteration for each train as the F kind's median
over the S kind's (measured; the checker's REPORTED rows, re-derived by verify-e200d): **T7 1.103 and T14 1.069**; T1 1.032 and T2 1.032;
the other eleven trains 0.9996-1.0008. E197.md 14 stated before the data that T7's and T14's bodies "are equal in every per-instruction
count but not at a coarser grain", and: "If the front end moves the instruction stream in 8- or 16-byte units, a non-zero T7 or T14 is
not a register-file price alone". The two higher ratios sit beside T7 POSITIVE and T14 NEGATIVE, so `dest_n8` (POSITIVE) and
`read_n8` (NEGATIVE) carry that caveat. REPORTED: no word changes.

## 5. The second firmware read on this boot (verify-e200d's F5, information)

Nothing to add. README.md note 11 records it: this sitting's look read NEEDS-READ again (sitting 1's EQUAL record lives in sitting 1's
own folder, not among fwgate's committed records), and step 7 sent fwgate's query a second time this boot (09:37:17), as E200.md 8
registers the read for each sitting on NEEDS-READ, where KIT.md 6 and CARD-LANE-BRIEF.md 5 say "once a boot". It was a READ by the
owner's rulings (README.md, Device commands sent) and read EQUAL, as sitting 1's did (08:13:26). verify-e200d agrees with the card lane.

## 6. A week number (verify-e200d's F6, nit)

**Dated clause (Mon 16 Nov 2026, PST):** Mon 16 Nov 2026 is in ISO week 47 (`/usr/bin/python3` 3.12.3: `datetime.date(2026, 11,
16).isocalendar()` gives year 2026, week 47, weekday 1), as both data READMEs say. Four of E200's pinned files write "Mon 16 Nov 2026
(week 46)": E200.md line 17, KIT.md line 3, CARD-LANE-BRIEF.md line 3 and DATA-README-FORM-e200.md line 3 (verify-e200d named the first
two; this lane found the other two). Read "week 47" there; the dates themselves are right, the files stay as pinned, and nothing else
changes. E200.md line 3's "Sun 15 Nov 2026, week 46" is right.

## 7. What stays

`README.md` and `SHA256SUMS` stay as committed in `ca53ed29`, and no committed data file changed (this lane read every `SHA256SUMS`
entry, 36 of 36 here and 36 of 36 in sitting 1's directory; `posthoc_note1_e200.py` section 0). Every check word stands as the kit's
checker prints it (measured). The pooled reduction is E200's registered result. Step 13's outputs are not committed here; a later dated
note commits them beside the data: `regfile-e200.json` (sha256 `9e70c813a1e140f867bdc6434a354ded9bbc3b8d8379d07df03f91d97983cfde`) and
`checks-e200-2.json` (`9e72317aceb4cda82fb1f34ec5dd13ed440dc56c99f41260527f1d2c7e5d891b`), the bytes verify-e200d re-made with the
committed reducer and checker (REPORTED). Our next session on this card could start no earlier than 10:43:43 PST (E200.md 11: 40
minutes after this sitting's end at 10:03:43). Nothing is scored here, and no forecast number is in this note.

## 8. Files

| path | what |
|---|---|
| `README.md.dated-note-1.md` | this note |
| `posthoc_note1_e200.py` | the post hoc read behind sections 1 and 3 and sitting 1's note 1 (both sittings; standard library only) |
| `posthoc-note1-e200.txt` | its printed lines (`/usr/bin/python3` 3.12.3) |
| `SHA256SUMS-note1` | the sha256 of these three files, `README.md` and `SHA256SUMS` |

Re-make the post hoc lines from the top of the repository (no device; it reads only the two data commits' files, each checked against
its `SHA256SUMS` first):

    /usr/bin/python3 -I -B docs/reports/data/2026-11-16-e200-regfile-sitting-2-aifoundry2/posthoc_note1_e200.py | cmp - docs/reports/data/2026-11-16-e200-regfile-sitting-2-aifoundry2/posthoc-note1-e200.txt && echo "the same lines"

The code this note cites, at these sha256 (each pinned by E200's or E197's registration or kit lists, or by the lab's tree):

| file | sha256 |
|---|---|
| `tools/claims-v3/e200/E200.md` | `c4721b7e6c9eb4eaf830eb8357cf6d4d977831a9703f2b2c26721c0e09f059fc` |
| `tools/claims-v3/e200/KIT.md` | `71872149a75e8b0f2d1d319e10507d857c6a790fbec2e3256603d1de34b4557d` |
| `tools/claims-v3/e200/collect_e200.py` (the collector and its scrub) | `63121a40fcf6df8acc6960bd4fa6726841a35e97b36fa904942de52eff9475b9` |
| `tools/claims-v3/e200/rb/s05_look_e200.sh` (step 4, the look) | `ad1d2262f76b9513d4adb6dc8fa076bbfac3da4da8e6a5a522d3536d6df1b91c` |
| `tools/claims-v3/e200/check_e200.py` (the kit's checker) | `9fa7c9d6233fb19957d0f45a09d6235ec2b9f8a62e92ffba1927ecbbf7005e65` |
| `tools/claims-v3/e200/reduce_e200.py` (the registered reduction) | `10a4403430b20686050ccfc7ae1af3db2107f6ccc56511bfc00a6c8056c147ef` |
| `tools/claims-v3/e200/CARD-LANE-BRIEF.md` | `b15fb65fd6bb1f1c54be887ad7175b9d8f0eed6ec155ed420716bc50f8b25e3c` |
| `tools/claims-v3/e200/DATA-README-FORM-e200.md` | `5343777448c04205efce95267d80f9cba3b63c2f89513df04d180521ce54966d` |
| `tools/claims-v3/e197/E197.md` | `5932e41a13dbc1833938b10cbc40ca850723029e60c231f1908426ef38ee8c35` |
| `tools/claims-v3/e197/KIT.md` | `816571c0dab651bb73abdee337700e2acdcf349b5f197d9f51c61e7e9d99d8b5` |
| `tools/lab/et-holders` (the holder listing behind `et-who`) | `77a37588f1e814e574ddb4ad1525119fcb33f1ab8d34f932249810516cd2efb1` |

SPDX-License-Identifier: Apache-2.0
