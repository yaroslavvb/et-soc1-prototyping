# E200 sitting 1's data README, dated note 1 (Mon 16 Nov 2026; after the data verifier): one collected file differs from the box's manifest, by the registered scrub alone; the first card command and the rest read two ways, and the kit's reading decides; the set-aside processes (post hoc); a week number

*Written on aifoundry2 from about 10:37 PST on Mon 16 Nov 2026 (week 47) by the clock. Desk only: no card, no lab box, no device, no
post. Written by the lane `fix-e200d` of Q192, after this experiment's data verifier `verify-e200d` (desk only, 10:10-10:40 PST). The
verifier's verdict was holds with fixes, the fixes documentation only: one low finding, two nits and three for information, none of them
a fault in a datum, the reduction, a check, the clock rule, the seal, a gate or a release. Its own reducer, written from E197.md and
E200.md and importing nothing from the kit, re-derived this sitting's reduction from the committed raw files (1,114 values, 0
mismatches, largest relative difference 1.2e-13) and its checker's 110 rows, and the kit's own reducer and checker and this README's
"Re-make it" lines gave step 13's bytes (REPORTED, verify-e200d's). [`README.md`](README.md) and [`SHA256SUMS`](SHA256SUMS) (lab
`548d736e`, 09:02:36 PST Mon 16 Nov 2026) stay as committed. **No number, rule, verdict or check reading changes, nothing is scored, and
no forecast number is here** (the model session scores its sealed forecast privately). **Every figure below is post hoc to the data
commit.** Sitting 2's dated note 1
([`../2026-11-16-e200-regfile-sitting-2-aifoundry2/README.md.dated-note-1.md`](../2026-11-16-e200-regfile-sitting-2-aifoundry2/README.md.dated-note-1.md))
answers the same findings for both sittings, with the front-end ratios (F4) and the second firmware read (F5), which concern sitting 2
alone; its post hoc read,
[`posthoc_note1_e200.py`](../2026-11-16-e200-regfile-sitting-2-aifoundry2/posthoc_note1_e200.py) with its printed lines
[`posthoc-note1-e200.txt`](../2026-11-16-e200-regfile-sitting-2-aifoundry2/posthoc-note1-e200.txt), reads this directory too. Where the
figures come from: (a) the committed files, read again by that script; (b) the card lane's runbook log and its copy-back of the box's
files (outside the repository); (c) desk checks of code, by line number at the sha256 listed in sitting 2's note, section 8; (d)
verify-e200d's readings where named (REPORTED). Interpreter: `/usr/bin/python3` 3.12.3 on aifoundry2. Labels: **registered**
([`E200.md`](../../../../tools/claims-v3/e200/E200.md), E197.md by reference, the kit), **measured**, **desk check of code**, **desk
arithmetic**, **post hoc** (desk work after the data, deciding nothing), **REPORTED** (verify-e200d's, or a checker row that carries no
verdict).*

## 1. One collected file differs from the box's manifest: the registered scrub (verify-e200d's F1, low, documentation)

`session/MANIFEST.sha256` is the box's list, written on the box before the collection (README.md, Files). Read line by line against
the committed files (desk check, this lane, 10:4x PST; `posthoc_note1_e200.py` section 1 prints it again):

- 33 lines; for 32 the committed file is at the manifest's sha256 (`run/telemetry.jsonl` as unpacked from `run/telemetry.jsonl.gz`);
- the one other is fwgate's read record:

| file | sha256 |
|---|---|
| the manifest's line for `./first/fwgate-aifoundry2-c0-20261116-081326.json` (the box's bytes) | `1aaf66d85177bacf8c23980a8bd9ffbc5480b171c0252fb39563e23bef820e5d` |
| the committed `session/first/fwgate-aifoundry2-c0-20261116-081326.json` | `7c3e0c60ae067f0b2f6519ff8b1a2592e73a5205bce57c422f5f253bfc24ca9a` |

**Why.** The record holds one "~", in its line 34: `"ledger": "~/.local/state/fwgate/aifoundry2-c0.jsonl",` (fwgate's attempt
ledger for this card). With the box's home written back in place of that "~", the file's sha256 is the one on the manifest's line. The card lane's
copy-back of the box's file has the manifest's sha256 and differs from the committed file in line 34 alone (111 lines each). That is
the kit's collector at work, registered before any datum
([`collect_e200.py`](../../../../tools/claims-v3/e200/collect_e200.py)): step 4, the scrub, writes the box's home as "~" in every text
file (docstring lines 28-30; `scrub()` lines 130-131), and step 2, the box-tree gate, allows the box's home in a collected file only as
the home itself, inside the box tree, or in this ledger path (lines 14-19). In this sitting's files the box's home stood in that one
line alone: the record's raw answer (`.stdout`, `.stderr`) and every other file the manifest lists are at their manifest lines, so the
scrub changed nothing else there. README.md's "Re-make it" lines set only the three run files against the manifest (they print "the
box's bytes"), so they never meet this line; a reader who checks every manifest line meets it once, and this is its reason. The
record's own verdict field reads "EQUAL" as committed (README.md's Results row quotes the read in full).

**Dated sentence (Mon 16 Nov 2026, PST):** the registered scrub changed one line of one collected file here, line 34 of
`session/first/fwgate-aifoundry2-c0-20261116-081326.json` (fwgate's attempt-ledger path, the box's home written as "~"), so that file
alone differs from its line in `session/MANIFEST.sha256`; the run files and every other file the manifest lists are the box's bytes.

## 2. The first card command and the rest, read two ways; the kit's reading decides (verify-e200d's F2, nit)

E197.md 6 (E200's by reference) counts the cap and the rest from "the first command of the sitting that reaches the card or its
management node (a configuration read included) or the sitting's first holder check, whichever comes first". For this sitting (desk
arithmetic; the moments from README.md and `session/first-card-command.txt`):

| | the kit's reading: step 7's first command (registered) | the other: step 4's look counted as the sitting's first holder check |
|---|---|---|
| the moment | 08:13:25 PST (fwgate's read) | 08:12:16 PST (the look) |
| the rest after E194's end, 00:49:00 (40 required) | 444.4 min | 443.3 min |
| card-minutes to the end, 08:57:03 (cap 50) | 43.63 | 44.8 |

Both readings meet this sitting's rest and cap (verify-e200d gave the 44.78; 443.3 is this lane's). They differ for sitting 2, whose
look came 21.5 minutes after this sitting's end: under the other reading sitting 2 would have broken its rest, and E200's result would
be this sitting's reduction alone (sitting 2's note 1, section 2, gives both readings in full). **The rule that decides is KIT.md 4,
stated before any E200 datum** (E200's kit `b4a5f6f2`, 06:57:03 PST; [`KIT.md`](../../../../tools/claims-v3/e200/KIT.md) lines 105-106
and 141, with E197's [`KIT.md`](../../../../tools/claims-v3/e197/KIT.md) section 4 kept unchanged, its lines 109-110): the first card
command is step 7's first command, here fwgate's read,
and "k6's look (step 4) is the runbook's look at the box, not the sitting's holder check: `et-who` runs `et-holders`, which stats the
nodes and never opens them, so it sends nothing to the card". E200's look says so in its own header
([`rb/s05_look_e200.sh`](../../../../tools/claims-v3/e200/rb/s05_look_e200.sh) lines 19-20: "Nothing here opens a device or takes a
lock"). **So the registered readings stand:** the rest of 444 minutes (README.md's note 8) and 43.63 card-minutes of 50. Read this
clause beside README.md's rest row (Registered against happened, "the 40-minute rest before the sitting's first card command") and its
note 8. Nothing is re-scored.

## 3. The set-aside processes: no slow climbs (verify-e200d's F3, information; post hoc)

THE CLOCK RULE set aside 6 of this sitting's 400 train processes: C3 judged them OFF live, never two in a row (measured, README.md),
and C1, in step 13's reduction, set aside six for samples off 800 MHz after the 1.5 s allowance, the same six (verify-e200d, REPORTED;
this lane's sample test below finds the same). This lane's own read (`posthoc_note1_e200.py` section 2; post hoc, deciding nothing;
times in seconds after the process's first launch's start):

| process | climb to 800 MHz | the one run off 800 MHz | clocks in it | die (`minshire[0]`) | latch (`minshire[2]`) | board |
|---|---|---|---|---|---|---|
| A, T1 43 | 0.067 s | 1.268-2.469 s (13 samples) | 600, 700 MHz | 57-58 C | 60 C | 29.29-40.62 W |
| A, T1 100 | 1.114 s | 1.915-3.116 s (13 samples) | 600, 700 MHz | 57 C | 61 C | 29.15-40.35 W |
| A, T1 112 | 0.090 s | 1.291-2.392 s (12 samples) | 600, 700 MHz | 57-58 C | 61 C | 29.18-40.48 W |
| B, T3 8 | 0.077 s | 0.878-2.079 s (13 samples) | 600, 700 MHz | 52-53 C | 61 C | 25.19-33.41 W |
| B, T5 14 | 1.181 s | 3.983-5.084 s (12 samples) | 600, 700 MHz | 53 C | 61 C | 25.06-33.12 W |
| D, T12 6 | 0.096 s | 2.899-4.100 s (13 samples) | 600, 700 MHz | 52-53 C | 61 C | 25.10-33.22 W |

Each reached 800 MHz 0.067-1.181 s after its first launch's start and left it once, for 1.10-1.20 s from the first off sample to the
last; the clock was at 800 MHz again on the next sample. Over each run the die and the board read under the card's threshold (65 C) and
TDP (65 W) as configured; what moved the clock was not read. These were not slow climbs: the largest climb of this sitting's 400
processes was 1.423 s (under C1's 1.5 s), the median 0.070 s, and 281 read 800 MHz within 0.1 s of their first launch's start.
Sitting 2's three were alike (its note 1, section 3). verify-e200d's wording, "dipped to 600/700 MHz for 0.5-1.2 s, between 1.52 and
5.08 s in" (REPORTED), counts the part of each run from 1.5 s on, the samples C1 judges. Nothing changes: the registered rule set these
processes aside, and these lines decide nothing.

## 4. A week number (verify-e200d's F6, nit)

**Dated clause (Mon 16 Nov 2026, PST):** Mon 16 Nov 2026 is in ISO week 47 (`/usr/bin/python3` 3.12.3: `datetime.date(2026, 11,
16).isocalendar()` gives year 2026, week 47, weekday 1), as this README says. Four of E200's pinned files write "Mon 16 Nov 2026 (week
46)": E200.md line 17, KIT.md line 3, CARD-LANE-BRIEF.md line 3 and DATA-README-FORM-e200.md line 3. Read "week 47" there; the dates
themselves are right, the files stay as pinned, and nothing else changes.

## 5. What stays

`README.md` and `SHA256SUMS` stay as committed in `548d736e`, and no committed data file changed (36 of 36 `SHA256SUMS` entries read;
`posthoc_note1_e200.py` section 0). Every check word stands as the kit's checker prints it (measured). Step 13's outputs for this
sitting are not committed here; a later dated note commits them beside the data: `regfile-e200-s1.json` (sha256
`aa18f2d8c6fac8a0dc2838a2610a006e4c58615864ced7bbf6ac75dd16ffdf24`) and `checks-e200-1.json`
(`eaae1105046de09406f69632395bd7321ef72a30c5b27d8321a9725dba0c3099`), the bytes verify-e200d re-made with the committed reducer and
checker (REPORTED). Sitting 2 ran, so the pooled reduction in sitting 2's directory is E200's registered result. Nothing is scored here,
and no forecast number is in this note.

## 6. Files

| path | what |
|---|---|
| `README.md.dated-note-1.md` | this note |
| `SHA256SUMS-note1` | the sha256 of this note, `README.md` and `SHA256SUMS` |

The post hoc read behind sections 1 and 3 and its printed lines are in sitting 2's directory (its note 1, section 8, with the line that
re-makes them and the sha256 of the code both notes cite).

SPDX-License-Identifier: Apache-2.0
