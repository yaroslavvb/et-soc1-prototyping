# E180's data README, dated note 1 (Fri 6 Nov 2026; after the card day's data verifier): E180-I is NULL within its ±0.30 W margin while its interval lies above 0 (+0.10 W [+0.04, +0.17]), so the integer add is not "flat"; a burst raised the die by a median of 0.87 °C and a mean of 0.80 °C; six figures of the per-kind bullets were rounded twice (the verifier named two); the card lane's local waits

*Written on the Intel at about 14:55 PST on Fri 6 Nov 2026, desk only, after the card day's data verifier of E180 (Fri 6 Nov 2026, about
13:55–14:20 PST: holds with fixes, 0 critical, 0 major, 1 minor and 3 nits, all in the README's words and figures or in the card lane's
process, none in a measured number, a verdict or a gate). [`README.md`](README.md) and [`SHA256SUMS`](SHA256SUMS) (lab `c8a3a6ee`, 13:47:01
PST) stay as committed, and so does every file of step 22 v3's collection and score. **No number, rule, verdict or gate reading changes,
and nothing is scored.** The note answers the verifier's four faults: the words "the integer add is flat" (§ 1, fault 1), the die rise's
"mean" (§ 2, fault 2), the rounding of the per-kind bullets (§ 3, fault 3, where this note finds six figures, not the verifier's two) and
the card lane's local waits (§ 4, fault 4, nothing in this directory). The figures come from
[`posthoc_note1_e180.py`](posthoc_note1_e180.py), which reads only this directory's committed files (and, as text or data, six committed
files of the kit that the note quotes: `E180.md`, its dated note A1, `power_e180.py`, `score_e180.py`, `score_e180_v2.py` and
`forecast-e180.json`) and imports no lab module. Its output is [`posthoc-note1-e180.txt`](posthoc-note1-e180.txt) and
[`posthoc-note1-e180.json`](posthoc-note1-e180.json) ("output §" below is that output's), and a re-run from this tree with the Intel's
`/usr/bin/python3` writes both byte for byte. [`SHA256SUMS-note1`](SHA256SUMS-note1) pins this note, the script and its two outputs; with
`SHA256SUMS` (89 files, unchanged) it pins every file here but `README.md` and the two lists. For the kinds page's [section
11](https://spacesheep.dev/@yaroslavvb/horace-kinds-of-numbers#11-what-is-still-open), item 6, as the README.*

## 1. E180-I is NULL within its margin, and its interval lies above 0 (fault 1, minor)

The README says it three times: in its title (line 1), "the integer add is flat (E180-I NULL)"; in its plain words (line 58), "the
integer add reads flat inside its margin"; and in What it does to predicting power (lines 226–227), "the integer add's held write-back is
flat within ±0.30 W (E180-I NULL)". The data commit's subject (`c8a3a6ee`) says "the integer add flat (E180-I NULL)". "Flat" is the
registration's expectation ([`E180.md`](../../../../tools/claims-v3/e180/E180.md) § 10, line 306: "The integer add is flat (E180-I
NULL)"), not what the card read.

E180-I's statistic (E180.md § 5, line 200) is, in each pass, the mean D of the eight fadd.pi R4 kinds less D(fadd.pi zeros), and the
rule reads NULL "if the interval lies inside +-0.30 W". Re-made here from the committed reduction with the registered t(0.975, 5) = 2.571
([`power_e180.py`](../../../../tools/claims-v3/e180/power_e180.py)'s table), it is **+0.1022 W [+0.0385, +0.1659]**, equal to
`scored-e180.json` to 1e-12, and each of the six passes reads above 0, from +0.039 to +0.206 W (output § 1). The scorer tests the margin
first ([`score_e180.py`](../../../../tools/claims-v3/e180/score_e180.py) lines 116–125: the margin at line 120, then lo > 0 at line 122),
so an interval inside ±0.30 W reads NULL whatever its sign, and the verdict NULL stands. Read beside the verdict, the interval lies above
0. The arms' forecasts of the same statistic: P, C and E forecast 0 (the integer write-back holds its value, so it has no named flips), and all three lie **below**
the interval; F's +0.041 W and A's +0.046 W (a uniform price per RTL toggle) lie **inside** it. These are the reported arms' words
(inside, above, below), not SIZE verdicts: E180-I registers none. E180.md § 5 reads "the integer add's held write-back costs nothing by
the number" only for E180-I NULL *with* E180-X POSITIVE (line 219); E180-X is NOT RESOLVED, so the session does not reach that reading.

So the sentence reads: **E180-I is NULL within its registered ±0.30 W margin; the eight one-number integer kinds read +0.10 W [+0.04,
+0.17] above fadd.pi zeros, above 0 in each of the six passes (reported: P's, C's and E's 0 lie below the interval, F's +0.041 and A's
+0.046 W inside).** Never "the integer add is flat" or "costs nothing", and never "flat" without the margin.

## 2. The die's rise over a burst: a median of 0.87 °C and a mean of 0.80 °C (fault 2, nit)

Line 233 says "a burst's mean rise was 0.87 °C". A1 § 4.3 ([`E180.md.dated-note-A1.md`](../../../../tools/claims-v3/e180/E180.md.dated-note-A1.md)
line 239) reports the rise per kind: each kind's mean rise (Tb − Ti) over the passes, with a kind more than 0.5 °C from the median named.
The scorer's 0.870 °C (`scored-e180.json` `reported_v2.rise`; [`score_e180_v2.py`](../../../../tools/claims-v3/e180/score_e180_v2.py)
line 130) is that median: the median of the 41 kinds' mean rises, 0.8703 °C (their mean is 0.793 °C). Over the 282 kept bursts
themselves (`reduced-e180-v3.json`, `runs_v2`), the median is 0.8696 °C and the mean **0.7993 °C**; the quartiles are 0.674 and
1.000 °C, and 14 bursts read no rise (output § 2). So 0.87 °C is a median either way, and the mean is 0.80 °C.

Line 84's "median 0.870 °C" holds as printed: the kinds' median is A1's statistic, and the bursts' own median rounds to the same 0.870.
Its "more than 0.5 °C off it, only `fadd.ps/random`" is the kinds' reading (`fadd.ps/random`'s mean rise is 1.598 °C). Line 233's other
figure holds too: the live die reading, `temp_c.minshire[0]`, stayed at 50–57 °C over all 24,301 samples (50 °C in the stop-path test,
the smoke and the first pass; 53–57 °C in the other five passes).

So the sentence reads: **the die's live reading stayed at 50–57 °C; a burst raised it by a median of 0.87 °C (the 41 kinds' mean rises,
as A1 § 4.3 reports them; the 282 bursts' own median rounds to the same) and by a mean of 0.80 °C over the 282 bursts.** The card lane's
own result says "a burst's mean rise 0.87 C"; it is read the same way.

## 3. Six figures of the per-kind bullets were rounded twice (fault 3, nit; the verifier named two)

The verifier named two figures of the bullet "Each kind's D above its mode's zeros, against P" (lines 88–93) that were rounded to four
decimals and then again to three: fadd.ps const's D above zeros, +0.06746 W, printed "+0.068", and fadd.pi random's P, +9.63847 W,
printed "+9.639". This note re-read every figure of the bullets after the reported table (lines 84–96: the die rise, the rates, each
kind's D and forecasts, and the pairs of E180.md § 4), 64 in all, against its committed value at the printed precision (output § 3). Six
disagree, all six the same double rounding, and the other 58 agree:

| line | figure | printed | committed (W) | at three decimals |
|---|---|---|---|---|
| 90 | fadd.ps const, D above zeros | +0.068 | +0.067456 | **+0.067** |
| 90 | fadd.ps 3s, D above zeros | +0.094 | +0.093467 | **+0.093** |
| 91 | fadd.ps −4, D above zeros | +0.060 | +0.059492 | **+0.059** |
| 91 | fadd.pi random, P | +9.639 | +9.638474 | **+9.638** |
| 93 | fadd.pi.acc int 1, P | +1.199 | +1.198499 | **+1.198** |
| 93 | fadd.pi.acc int 4, P | +1.199 | +1.198499 | **+1.198** |

The same reading over the rest of the README finds no other. The 123 figures of the two tables' measured and forecast cells and of
E180-A's band (lines 42–49 and 73–82) all agree. Of the 59 other figures printed to three decimals or fewer from a committed figure (the
title, the plain words and the price, What it does to predicting power), 58 agree; the 59th is line 233's 0.87 °C, a median called a
mean (§ 2). No verdict, SIZE word or reported reading rests on a printed figure: the scorer reads its own values, and the six corrected
figures are reported readings and forecasts only.

## 4. The card lane's waits at the desk (fault 4, nit; nothing in this directory)

Between the runbook's own bounded waits on the box (box step 10's five calls, each ending within the box's loop of 520 s), the card lane
also waited at the desk for its own step log to grow: a local wait of at most 540 s that read a local file every 5 s and sent nothing to
the box. The card day's rule for unattended work makes a wait on a remote run a bounded remote call, repeated, and never a long local
wait. E178's lane waited the same way. It touched no card, box or file here, and nothing in this directory depends on it. The next card
lane waits for its background job's own completion notice instead.

## Lines for the records

1. E180-I: NULL within its registered ±0.30 W margin; the eight one-number integer kinds read +0.10 W [+0.04, +0.17] above fadd.pi
   zeros, above 0 in each of the six passes (reported: P's, C's and E's 0 below the interval; F's +0.041 and A's +0.046 W inside). Never
   "the integer add is flat" (the README's title, the data commit's subject) or "costs nothing", and never "flat" without the margin.
   Lab 03, the kinds page's section 11 item 6 and the hubs quote this line.
2. The die's rise over a burst: a median of 0.87 °C (the 41 kinds' mean rises, A1 § 4.3's reading; the 282 bursts' own median rounds the
   same) and a mean of 0.80 °C; the live die reading 50–57 °C. Never "a mean rise of 0.87 °C".
3. The per-kind figures at three decimals, as corrected: fadd.ps const +0.067, 3s +0.093 and −4 +0.059 W above zeros; fadd.pi random's
   P +9.638 W; fadd.pi.acc int 1's and int 4's P +1.198 W. Every other figure of the README stands as printed (246 re-read).
4. The card lane's local waits between box step 10's bounded calls: disclosed and harmless; the next card lane waits on its background
   job's completion notice.

## What does not change

Every reading, verdict, gate, stop and figure of the README stands, except the words and the six figures above. With this note's five
new files in the directory (the four it pins and `SHA256SUMS-note1`):
- `SHA256SUMS` reads 89 of 89 OK, and `SHA256SUMS-note1` 4 of 4;
- the post hoc script, re-run in place, writes its two outputs byte for byte;
- the login checks read every directory clean: `scrub_tree_e178.py --check` (81 text files in 12 directories, and the text of the 15
  `.gz` files, 0 left), and E164's `--check` in all 29 directories of both; run_e78's stop line appears nowhere but in the README's own
  description of that search (line 193);
- the desk-path gate (`nopath_q142s.py`) reads all 96 files with 0 hits;
- the public-text scan (`sanitize_extracts.py`'s fixed list, its e-mail pattern bounded; the private-network, Mac-home, scratch and e-mail
  patterns; and the data verifiers' wider lists, 72 patterns) reads every file, each `.gz` decompressed. In the data commit's files it
  finds only reviewed text: the owner's own box path 8 times, as the README says; the card's configuration dump, whose address lines name
  the device's on-chip memory (24, in the two `logs/config-session-*.json.err`); `logs/build-e180.json`'s own description of the fields it
  leaves out (1); and the README's description of the stop-line search (1). It finds nothing in this note's five files or in its commit
  message's subject and body, and the six strings planted in a scratch copy of this note are all caught. The lab's private name table is
  absent on the Intel (the README's stated coverage limit), so the note's files were also checked for each of the 16 other logins that the
  public repository names in its home-directory paths: none appears.

The scorer reads none of this note's files, and the data verifier re-made its output byte for byte from the committed directory at
`c8a3a6ee`, so no scored figure can move.

SPDX-License-Identifier: Apache-2.0
