# E186's data README, dated note 1 (Mon 9 Nov 2026; after the data verifier): october-forecast-model's arms stand as the kit's readers committed them, and three passages of the README that sum them up as a score are set aside; the measured rates are 1.0015-1.0017 (floats) and 1.0003 (int8) of the candidates'; of the int8 prices per held bit only beta_A's move with the word is resolved; E186-S23R's DIFFERS LOW rests on a 0.000065 W gap; lines for the records

*Written on the Intel from about 15:55 PST on Mon 9 Nov 2026 (week 46), desk only, after E186's data verifier (Mon 9 Nov 2026, about 14:44-15:30 PST:
holds with fixes; one major finding, not blocking, and minor ones and nits, none in a datum, a scored figure or a verdict; every
registered verdict re-made from the committed bytes). [`README.md`](README.md) and [`SHA256SUMS`](SHA256SUMS) (lab `b880ed63`, 14:40:13
PST) stay as committed, and so does every file of step 11's collection and score and of october-forecast-model's arms. **No number,
rule, verdict or gate reading changes, and nothing is scored.** The note answers the verifier's findings on this directory: three
passages of the README on october-forecast-model's arms (§ 1), one reported figure (§ 2), two sentences of plain words (§ 3), and lines
for the records (§ 4). The figures come from [`posthoc_note1_e186.py`](posthoc_note1_e186.py), which reads only this directory's
committed files (and, as data, the kit's frozen [`forecast-e186.json`](../../../../tools/claims-v3/e186/forecast-e186.json) for the
candidates' rates), reads no october-forecast-model file and imports no lab module. Its output is
[`posthoc-note1-e186.txt`](posthoc-note1-e186.txt) and [`posthoc-note1-e186.json`](posthoc-note1-e186.json) ("output §" below is that
output's), and a re-run from this tree writes both byte for byte. [`SHA256SUMS-note1`](SHA256SUMS-note1) pins this note, the script, its
two outputs, `README.md` and `SHA256SUMS`, so the README's line numbers below refer to its committed bytes; with `SHA256SUMS` (376 files,
unchanged) every file here is pinned but `SHA256SUMS-note1` itself. The runbook's times come from E186's runbook log, kept outside the
repository, and the commits' times from git. For the kinds page's
[section 11](https://spacesheep.dev/@yaroslavvb/horace-kinds-of-numbers#11-what-is-still-open), item 6, as the README.*

## 1. october-forecast-model's arms: three passages set aside (the major finding, not blocking)

october-forecast-model's arms are reported beside E186's rules, never as one of them (E186.md's dated notes M1 and M2), and in this
day's public text they are given only as the kit's readers commit them: [`arm-m1-e186.txt`](arm-m1-e186.txt) and
[`arm-m2-e186.txt`](arm-m2-e186.txt), with their `.json` and `.status.txt`, written by step 11 v4 through each note's gate. In three
passages the README's own prose goes further and sums the reader's output up as a score of the model. Those three are set aside: they
are not readings of the model, and no record quotes them or sums the arms up again.

1. "Reported beside, never a verdict", note M2's sub-bullet: from "Each arm's centre" (line 103) to the end of that sub-bullet's text
   (line 104);
2. the table under it, with its parenthesis (lines 106-113);
3. "What it does to predicting power", its third bullet (lines 263-265).

Every other line of the README on the arms stands, among them the head of their bullet (line 99), note M1's sub-bullet (lines 100-101:
v4 covers none of the ten session trains and FULL reads no kind, so the arm reads nothing), the first sentence of note M2's (lines
102-103: the reader v2 read the four arms, which carry the same int8 and fp32 figures and differ only on H16), the two rows of the files
table (lines 245-246), "The readings, labelled" (lines 117-123) and the last bullet (line 266). Output § 0 finds each README line this
note cites by a short anchor on its first line; the outputs copy none of the set-aside text.

The third passage is also wrong as fact in two details: the trains it calls "all small-swap or sign trains" include S23, the 16-bit fp32
order swap (1.0, 0x3f80ffff) − (0x3f80ffff, 1.0), the session's second-largest train (+0.1545 W); and it counts ten trains for every
arm, where v4 on M12's set reads nine, since it does not cover H16 (as note M2 said before any datum). `arm-m2-e186.txt` is the record.

## 2. The measured rates against the candidates' (minor)

"Reported beside", its fourth bullet (lines 96-98), says the measured rates are "1.0016-1.0017 of the candidates' for the float trains
(1.11896e9-1.11906e9 TensorFMA ops a second) and 1.0004 for the int8 trains (1.92117e9-1.92125e9)". The rates hold; the two ratios do
not (output § 1). Each train's `rate_per_s` in [`trains-e186.json`](trains-e186.json) over its type's rate in `forecast-e186.json`'s
`rates_per_s` reads 1.00154 (H16, against the fp16 rate) to 1.00165 (A23-A15) for the float trains, so 1.0015-1.0017, and 1.00029
(Q3-sign) to 1.00033 (Q63-sign) for the int8 trains, so 1.0003. No rule reads the rounded ratios: the scorer's lines used each train's
measured rate exactly, in all ten trains ([`scored-e186.json`](scored-e186.json) > `trains` > `rate_used_per_s`). So the clause reads:
**the measured rates are 1.0015-1.0017 of the candidates' for the float trains (1.11896e9-1.11906e9 TensorFMA ops a second) and 1.0003
for the int8 trains (1.92117e9-1.92125e9).**

## 3. Two sentences of plain words, with their margins (minor)

**(a) The int8 price per held bit (lines 74-76).** The README says that "the price per bit moves with the word: beta_A +0.0054 at
product 3 and +0.0107 at 63, beta_B +0.0141 and +0.0129". Only beta_A's move is resolved (output § 2). beta_A's 95% intervals at the two
products are apart, [+0.00325, +0.00763] W and [+0.00912, +0.01230] W a held 1-bit a byte; beta_B's overlap, [+0.01102, +0.01709] and
[+0.01057, +0.01513]. As post hoc arithmetic that no rule reads, product 63 less product 3 is +0.0053 W (se 0.0013) on A's side and
−0.0012 W (se 0.0019) on B's. E186-SPLIT3 and E186-SPLIT63 read A+B as scored, and line 260, which quotes beta_A alone, holds. So the
sentence reads: **Held int8 bits cost on both sides again (A+B at products 3 and 63, as E182 read at its products), but the price per
bit moves with the word on A's side: beta_A +0.0054 at product 3 and +0.0107 at 63, their intervals apart, while beta_B's two readings,
+0.0141 and +0.0129, agree within their intervals; M12 has one pair (+0.0084, +0.0099) and M10 puts it all on B.** The sentence after it
stands.

**(b) E186-S23R (lines 77-78, and line 261's last clause).** DIFFERS LOW holds by the registered rule (E186.md's table: the two intervals
overlap or not), by the narrowest of margins (output § 3). S23 × 23/16 reads +0.22209 [+0.21438, +0.22979] W and E182's T5 [+0.22986,
+0.24192], so the two intervals miss each other by 0.000065 W, 0.84% of the scaled interval's half-width (0.0077 W), in a comparison
across two sessions (E182's of Sun 8 Nov and this one). So the plain words read: **Moving 16 bits costs less than 16/23 of moving 23,
by the registered rule and only just (S23R DIFFERS LOW, the intervals 0.000065 W apart): S23 reads +0.155 W, M12 said +0.164, and scaled
by 23/16 its interval ends just below E182's T5 interval.** Line 261's clause reads with the same margin.

## 4. Lines for the records

1. **october-forecast-model's E186 arms:** as `arm-m1-e186.txt` and `arm-m2-e186.txt` commit them, never as the README's three
   set-aside passages or any summary of them (§ 1).
2. **The rates:** the measured rates are 1.0015-1.0017 (floats) and 1.0003 (int8) of the candidates', never 1.0016-1.0017 and 1.0004
   (§ 2).
3. **The int8 price per held bit** moves with the word on A's side (beta_A +0.0054 at product 3, +0.0107 at 63, intervals apart); B's two
   readings agree within their intervals. **E186-S23R DIFFERS LOW** with a 0.000065 W gap between the intervals (§ 3).
4. **"No login is named in any file"** (line 208) means that no other account's login is named. The owner's own box login is part of the
   box's home paths in the committed files: the reviewed class that "Privacy and the public-text scan" counts (56,407 of the scan's
   56,429 matches, and the configs' 22 keys that name it).
5. **The first wait call** (lines 170-172): the runbook's log holds that call's probe line (12:41:17 PST) and no wait line, so the
   entry's "it has no line in the runbook's log" reads "it has no wait line in the runbook's log". `b880ed63`'s message says the call
   was "stopped at the desk and re-made": it was stopped, at about 12:45:50, and the next call, at 12:46:05, carried the waits on, as the
   departures entry says.
6. **A2-3's sentence on day 2's checks** ([A2](../../../../tools/claims-v3/e186/E186.md.dated-amendment-A2.md), frozen): it says that
   day 2's own checks were run with A2 committed, on a scratch clone first and then on the lab clone, and that each read 0. A2 was
   committed at 12:26:15 PST, after the scratch clone's run (12:25:02-12:25:55) and before the lab clone's (12:26:25-12:27:07), which
   then read 0 as it says.

## What does not change

Every reading, verdict, gate, stop and figure of the README stands, except the three set-aside passages, the two ratios, the two
sentences of § 3 and the two phrases that § 4 reads more exactly (items 4 and 5). The scorer and the readers read none of this note's
files. With this note's five new files in the directory (this
note, the script, its two outputs and `SHA256SUMS-note1`), checked on a scratch clone holding this commit, before it was made:
- `SHA256SUMS` reads 376 of 376 OK and `SHA256SUMS-note1` 6 of 6; the directory holds 383 files, and every one but `SHA256SUMS-note1` is
  in one of the two lists;
- the post hoc script, re-run in place and into two empty directories, writes its two outputs byte for byte;
- the kit's two readers, re-run by their own command lines on a copy of the committed `scored-e186.json`, write `arm-m1-e186.json`,
  `arm-m1-e186.txt`, `arm-m2-e186.json` and `arm-m2-e186.txt` byte for byte;
- the login checks read the directory clean: `scrub_tree_e178.py --check` with the owner's recorded box login (0 left), E164's `--check`
  in every directory, and a count-only scan that finds 0 home paths of another name and 0 holder lines of another account;
- the desk-path gate (`nopath_q142s.py`, v3.1) reads the five new files with 0 hits;
- the public-text scan (`sanitize_extracts.py`'s fixed list with the private-network, Mac-home, scratch and e-mail patterns, and a list of
  private and mechanism words) finds nothing in the five new files or in this commit's subject and body;
- day 2's checks (the day-2 check v2 with `tree --pull`, E185's step 2 v5, E183's step 2 v4, and day 2's anchor lines 1-4 and 6) each
  read 0, with stand-in windows in scratch output folders and no call to any box;
- every hash list in the repository: 163 lists, 5,764 entries, 5,747 OK; the 17 others are E85's code list, whose 17 entries all match
  their files under `tools/claims-v3/{hlc,hlk,hm}/`.

SPDX-License-Identifier: Apache-2.0
