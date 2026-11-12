# E185's data README, dated note 1 (Thu 12 Nov 2026; after the data verifier): E181's held-out figures carry A1-1's label; each D is the scorer's own; the frozen chain under-predicts L1, L2 and S2, where the README says it runs warm; E185-C on B is quoted only as printed; 102.6 card-minutes of the 105 cap for the session collected and 109.2 on card 0 in all; step 10 v2's rest rule never read E186's session log (a later kit's fix; harmless today); note M1's two passages that sum october-forecast-model's arm up as a score are set aside beside it; lines for the records

*Written on the Intel from 07:13 PST on Thu 12 Nov 2026 (week 46) by the clock, desk only (no card, no lab box, no post, no deploy), by the
lane `fix-q163d` of Q163, after E185's data verifier (Thu 12 Nov 2026, about 06:45-07:15 PST: holds with fixes; three minor faults and four
nits, none blocking and none in a datum, a scored figure or a verdict; every registered verdict re-made from the raw data by its own code;
the kit's scorer re-run with `scored-m11.json` and `scored-m11.md` byte for byte, and note M1's reader re-run byte for byte).
[`README.md`](README.md) and [`SHA256SUMS`](SHA256SUMS) (lab `190bad0d`, git 06:27:38 PST) stay as committed, and so do every file of step
14's collection and score and note M1 with its outputs and its list (`265dfd4c`, git 06:28:51 PST). **No number, rule, verdict or gate
reading changes, and nothing is scored.** This note answers the verifier's findings on the README (§§ 1-6); its finding on note M1 is
answered beside that note (§ 7); § 8 gives lines for the records. The figures come from [`posthoc_note1_e185.py`](posthoc_note1_e185.py),
which reads only committed files: this directory's README, note M1 and `arm-m1-e185.txt` (as text), `scored-m11.json` and the session's two
config-read times; and, as data or text, the kit's [`arms-e185-e181.json`](../../../../tools/claims-v3/e185/arms-e185-e181.json), step 10
v2's script, E186's launch step and the session-end lines of E186's and E184 arm S's committed session logs. It reads no
october-forecast-model file and imports no lab module. Its output is [`posthoc-note1-e185.txt`](posthoc-note1-e185.txt) and
[`posthoc-note1-e185.json`](posthoc-note1-e185.json) ("output §" below is that output's), and a re-run from this tree writes both byte for
byte. [`SHA256SUMS-note1`](SHA256SUMS-note1) pins both notes, the script, its two outputs, `README.md`, `SHA256SUMS`, note M1 and
`SHA256SUMS-m1`, so the line numbers below refer to their committed bytes; with `SHA256SUMS` (50 entries) and `SHA256SUMS-m1` (3), every
file here is pinned but `SHA256SUMS-note1` itself. For the kinds page's [section
11](https://spacesheep.dev/@yaroslavvb/horace-kinds-of-numbers#11-what-is-still-open), items 9 and 8, as the README.*

## 1. E181's held-out figures carry A1-1's label (minor)

"What it does to predicting power and heat" (lines 207-208) quotes "E181's held-out ranking (Rl 0.198, B 0.231, F 0.296 °C)" and E181's
frozen chain at "0.30 °C". These are E181's two-pass held-out rms over its five holds: F 0.2963, B 0.2312 and Rl 0.1978 °C
(`arms-e185-e181.json` › `two_pass` › `held_out` › `rms`; output § 1). E185's amendment
[A1](../../../../tools/claims-v3/e185/E185.md.dated-note-A1.md), A1-1, labels them "held out; the reading chosen by A10 after both
readings were seen", and asks every record that quotes them to carry that label. The README carries it on no line. So the sentence reads:
**E181's held-out ranking (Rl 0.198, B 0.231, F 0.296 °C; held out; the reading chosen by A10 after both readings were seen) did not
carry: the frozen chain read E185, blind, better than it read E181 (0.21 against 0.30 °C, E181's with the same label).**

On the reading stated at 20:03 PST, A1-1's other label ("held out; the reading stated at 20:03 PST"), E181's rms were Rl 0.195, B 0.263 and
F 0.293 °C (`held_out` › `rms`). The order is the same, and E181's frozen chain lies above E185's blind 0.2146 °C on both readings. So the
sentence's words hold on either reading; only the label was missing.

## 2. Each D is the scorer's own (nit)

"The answer" (lines 78-80) writes each D as a subtraction of the rms printed to four decimals. Four of the six reproduce; two do not, by
one in the last digit (output § 2):
- E185-RF on A10's reading prints "0.2158 − 0.2146 = +0.0013", and those operands give +0.0012;
- the stated reading's arm prints "D −0.0217 (0.2010 − 0.2226)", and those operands give −0.0216.

In all six the printed D is the scorer's `D_C`, computed from the unrounded rms (`scored-m11.json` › `E185` › `rules`, and ›
`one_pass_reported` › `rules`). As a desk check, the rms of the six per-hold misses as the score prints them give F 0.21454 and Rl
0.21581 °C, so D +0.00127 °C, which the scorer's +0.0013 rounds. No word moves: E185-RF's |D| is 0.0013 against τ 0.0361 °C. So each D is
quoted as the scorer prints it: **E185-RF +0.0013, E185-BF +0.0432 and E185-RB −0.0420 °C** on A10's reading, and −0.0217, +0.0627 and
−0.0843 °C in the stated reading's arm, never as a difference of the printed rms.

## 3. "Runs warm" means the frozen chain under-predicts (nit)

The paragraph after "Each hold" (lines 103-106) says that the frozen chain "runs warm on L1, L2 and S2 (+0.26, +0.20 and +0.35 °C)". The
misses are e = R − P (line 91), so a positive miss means the die rose more than the arm predicted: the arm under-predicts that hold (output
§ 3: e_F +0.2638, +0.1962 and +0.3466 °C). The same paragraph says "over-predicts" of the board gain and the rail chain, rightly, for
negative misses, and beside those "runs warm" reads backwards. So the sentence reads: **The frozen chain under-predicts L1, L2 and S2
(+0.26, +0.20 and +0.35 °C) and reads H_E and S within 0.07 °C.** The paragraph's other sentences hold as written.

## 4. E185-C on B is quoted only as the scorer printed it (nit)

E185-C's consequence is read on F alone (A1-2), and its F line reads NOT RESOLVED, so nothing follows (line 82). B's line (line 83) is
reported and decides nothing: d̄ +0.2503 °C, 95% interval [−0.0014, +0.5021], NOT RESOLVED (output § 4). Its lower end lies 0.0014 °C
below 0. An interval that excluded 0, with |d̄| at least 0.05 °C, would read THE SHAPE MISSES (E185.md § 6), so B's word rests on a margin
of 0.0014 °C.
- The data verifier's own code, with the registered reader's 0.2 s grid moved by 0.1 s (a desk sensitivity, not the registered reading,
  deciding nothing), read B's line as THE SHAPE MISSES ([+0.014, +0.518] °C). Every registered word stayed: E185-RF, -BF, -RB, -BEST,
  and E185-C on F. This note's lane re-ran that code on the committed data and got the same lines.
- So records quote E185-C on B only as the scorer printed it, labelled reported, and never as a finding about the cool-down. E185-C is
  quoted from its F line.

## 5. The card-minutes (nit)

E185's cap is 105 card-minutes a session, enforced from T0 by `session_e185.sh` (E185.md § 8). The session collected here used **102.6**,
from its config read at 04:32:45 PST to the one at 06:15:21 PST (`logs/config-session-start.json.time`,
`logs/config-session-end.json.time`). The first try, refused at its start gate, used 6.6 with no hold: T0 03:24:56 PST (`T1794482696`) to
its session end at 03:31:32 PST (lines 40 and 44). The later try ran on the path that kit note 1 provides after a start-gate refusal
("Major 1"). So card 0 carried E185 for **109.2 minutes in all** (output § 5). Line 136 gives both figures and stands. Records say
"102.6 of the 105 cap for the session collected; 109.2 on card 0 for E185 in all, with the first try's 6.6 (no hold)", and never call
109.2 "within the cap".

## 6. Step 10 v2's rest rule never read E186's session log (minor; the README discloses it, lines 56-60)

Confirmed at the desk (output § 6):
- **The patterns.** Step 10 v2's rest rule ([`rb/s11_a3_launch_e185_v2.sh`](../../../../tools/claims-v3/e185/rb/s11_a3_launch_e185_v2.sh)
  line 51) loops over four patterns: `build/e17[0-9]/session.log`, `build/e18[0-4]/session.log`, `build/e18[0-9]/session-*.log` and
  `build/e185/T[0-9]*/session.log`. E186's runbook writes its session log at `build/e186/T<T0>/session.log`
  ([`rb/s11_a3_session_e186.sh`](../../../../tools/claims-v3/e186/rb/s11_a3_session_e186.sh) line 39; E186's T0 1794256853), and none of
  the four matches it. E184 arm S's log, `build/e184/session-S-t1794133299.log`, is matched by the third.
- **The minutes.** From arm S's session end (Sun 8 Nov 2026 02:22:24 PST, its committed log) to the first try's launch (03:24:55 PST,
  line 39) is 5,822.5 minutes: the 5,822 that step 10 read. From E186's session end (Mon 9 Nov 2026 14:19:08 PST, its committed log) it is
  3,665.8 minutes: the README's "about 3,666" (line 59). Both are far over the rule's 40 minutes and A7-4's hour, so nothing changed
  today. The later try's 61 minutes were read from E185's own first try.
- **A desk case** of this note's lane, outside the repository and with no box: step 10 v2's own lines 50-89, unchanged, ran in a stand-in
  `build/` tree holding copies of those two committed logs at their box paths, with the clock fixed at the first try's launch. They read
  "rest: 5822 minutes since E184's session end". With `build/e18[0-9]/T[0-9]*/session.log` added to the loop's list, the same lines read
  "rest: 3665 minutes since E186's session end (2026-11-09 14:19:08 PST ...)".
- **For a later kit, not this one:** its rest rule reads `build/e18[0-9]/T[0-9]*/session.log` too (E186's form; it also covers E185's own
  `build/e185/T[0-9]*/session.log`), with a desk case of its own. E185's data need no change.

## 7. Note M1: two passages set aside, beside it

[`README.md.dated-note-M1.md.dated-note-1.md`](README.md.dated-note-M1.md.dated-note-1.md) answers the verifier's second minor fault. It
sets aside the clause of note M1's title after "both versions read alike" and note M1's post hoc bullet (lines 47-48), which sum
october-forecast-model's arm up as a score. That is the class E186's data note 1 set aside. The arm stands only as
[`arm-m1-e185.txt`](arm-m1-e185.txt) prints it.

## 8. Lines for the records

1. **E181's held-out figures** (Rl 0.198, B 0.231, F 0.296 °C; F 0.30) carry "held out; the reading chosen by A10 after both readings were
   seen" wherever they are quoted, and the stated reading's (Rl 0.195, B 0.263, F 0.293 °C) carry "held out; the reading stated at 20:03
   PST" (§ 1).
2. **E185's verdicts** are quoted on A10's reading, with the stated reading's arm beside them (A1-1): E185-RF NOT RESOLVED (D +0.0013 °C),
   E185-BF WORSE (+0.0432), E185-RB BETTER (−0.0420), E185-BEST NOT SEPARATED (F, Rl) (rms F 0.2146, B 0.2578, Rl 0.2158 °C). Each D is
   the scorer's `D_C` (§ 2).
3. **E185-C** is quoted from its F line: NOT RESOLVED, d̄ +0.0063 °C [−0.2387, +0.2513], n 4, so nothing follows. B's and Rl's lines are
   quoted only as printed, reported (§ 4).
4. **The pooled HM-CAL and HM-CAL-I8** printed with E185 are E181's, never E185's (A1-3; line 116, unchanged).
5. **The frozen chain under-predicts L1, L2 and S2** (+0.26, +0.20 and +0.35 °C); never "runs warm" (§ 3).
6. **The card-minutes:** 102.6 of the 105 cap for the session collected; 109.2 on card 0 for E185 in all, with the first try's 6.6 (no
   hold) (§ 5).
7. **The rest rule:** step 10 v2 did not read E186's T0-named session log. It was harmless today (5,822 minutes read, 3,665.8 true). A
   later kit reads `build/e18[0-9]/T[0-9]*/session.log` (§ 6).
8. **october-forecast-model's E185 arm** is quoted only by `arm-m1-e185.txt`'s lines, as note M1's dated note 1 says.

## What does not change

Every reading, verdict, gate, stop and figure of the README stands. The exceptions are the label § 1 adds, the two subtractions of § 2
(whose D's stand), the word § 3 replaces, and the readings §§ 4-6 make more exact. The scorer and the reader read none of this note's
files. With the six new files in the directory (the two notes, the script, its two outputs and `SHA256SUMS-note1`), on a scratch clone
holding this commit, before it was made:
- `SHA256SUMS` read 50 of 50 OK, `SHA256SUMS-m1` 3 of 3 and `SHA256SUMS-note1` 9 of 9; the directory held 62 files, and every one but
  `SHA256SUMS-note1` was in one of the three lists;
- the post hoc script, run in place and into two empty folders, wrote its two outputs byte for byte;
- note M1's reader, re-run by its own command line on the committed data, wrote `arm-m1-e185.json` and `arm-m1-e185.txt` byte for byte;
- the login checks read the directory clean: E164's `--check` in every directory, with the owner's recorded box login (through E185's
  `rb/scrub_all_e185.py`, each `.gz` unpacked outside the repository), and a count-only scan that found 0 home paths of another name
  and 0 holder lines of another account;
- the desk-path gate (`nopath_q142s.py`, v3.1) read the six new files with 0 hits;
- the public-text scan (`sanitize_extracts.py`'s fixed list with the private-network, Mac-home, scratch and e-mail patterns, and a list of
  private and mechanism words) found nothing in the six new files or in this commit's subject and body. It checked names against the
  fixed list only: the lab's private name table is absent on the Intel, the coverage limit the README states;
- the day-2 check v2 (`check_day2_v2.py tree`, no pull) read 0, and day 2's anchor lines 1-4 held, with no call to any box;
- every hash list in the repository: 166 lists, 5,826 entries, 5,809 OK; the 17 others are E85's code list, whose 17 entries all match
  their files under `tools/claims-v3/{hlc,hlk,hm}/`.

SPDX-License-Identifier: Apache-2.0
