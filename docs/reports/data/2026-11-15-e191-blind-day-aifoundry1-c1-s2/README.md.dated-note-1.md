# E191's second-session data README, dated note 1 (Sun 15 Nov 2026; after the data verifier): the scrub found nothing to replace; S1T's margin on the starting die (post hoc; PASS stands); the readings E191.md 8.4 reports; the commit message's trailer, the reducer's grid and the window file's label; lines for the records

*Written on aifoundry2 from about 15:05 PST on Sun 15 Nov 2026 (week 46) by the clock, desk only (no card, no lab box, no device, no
post), by the lane `fix-e191b` of Q184, after this directory's data verifier `verify-e191b` (Sun 15 Nov 2026, 14:35-15:00 PST: holds
with fixes; two nits and four notes for information, none of them a fault in a datum, a scored figure or a verdict; the four registered
rules re-derived from the raw files by its own code, with the kit's words and counts). [`README.md`](README.md),
[`SHA256SUMS`](SHA256SUMS) and [`FILES.txt`](FILES.txt) (lab `7156ac15`, 14:32:17 PST Sun 15 Nov 2026) stay as committed. **No number,
rule, verdict or gate reading changes, and nothing is scored.** The figures come from [`posthoc_note1_e191.py`](posthoc_note1_e191.py),
which reads only committed files: the files of this directory's data commit (the 257 that `SHA256SUMS` lists, `README.md`,
`SHA256SUMS` and `FILES.txt`), E191's registration list `SHA256SUMS-e191-registration` with the files it pins, E189's registration list
with its `forecast-e189.json` (for § 3), and, as text, the lines this note cites. For §§ 2-3 it loads the frozen scorer,
`score_e191.py`, as registered, only after E191's list reads every entry OK, and uses the scorer's own `score_day()`, pass reader, its
forecast module's `given()` and its verdict count. Its output is [`posthoc-note1-e191.txt`](posthoc-note1-e191.txt) and
[`posthoc-note1-e191.json`](posthoc-note1-e191.json) ("output §" below is that output's), and a re-run from this tree writes both byte
for byte. [`SHA256SUMS-note1`](SHA256SUMS-note1) pins this note, the script, its two outputs, `README.md`, `SHA256SUMS` and
`FILES.txt`, so the line numbers below refer to their committed bytes; with `SHA256SUMS` (257 entries), every file here at this note's
commit is pinned but `SHA256SUMS-note1` itself. Interpreter: `/usr/bin/python3` 3.12.3 on aifoundry2. Labels: **registered** (E191.md,
its note 1, A1 and the kit as committed), **measured** (the session's committed files), **desk check of code**, **reported** (E191.md
8.4's readings, desk arithmetic, deciding nothing), **post hoc** (desk readings after the data, deciding nothing).*

## 1. The scrub found nothing to replace (the verifier's finding 1, nit)

Line 201 says "The collector's scrub ran (the box's home path became `~`, the box login `<login>`)". The scrub ran, and **it replaced
nothing** (output § 1):
- all 207 files that the box's `session/MANIFEST.sha256` lists are at their listed sha256 here. The runner writes that list on the box,
  last, before the copy-back ([`run_e191_v2.py`](../../../../tools/claims-v3/e191/run_e191_v2.py) line 1067), so the scrub changed
  none of them: a text it had changed, or a `.gz` it had rewritten, would read another sha256;
- of the data commit's other 53 files (the 24 `energy.json` and 24 `energy.txt` the desk wrote, `session/MANIFEST.sha256`,
  `session/runner.rc`, `SHA256SUMS`, `FILES.txt` and `README.md`), only `README.md` holds a `~` or the login placeholder at all, once
  each, in that sentence; a replacement
  ([`collect_e191.py`](../../../../tools/claims-v3/e191/collect_e191.py) lines 74 and 76) would have left one;
- no file of the data commit holds a home-directory path, the text inside all 25 `.gz` files included.

Two desk checks by this lane agree: the card lane's raw copy-back (the session directory as copied from the box, before the
collector ran) equals the committed files byte for byte, 209 of 209 (the 207, `MANIFEST.sha256` and `runner.rc`); and the collector's
own printed line, in the card lane's log (not committed; `collect_e191.py` line 180 prints it), reads "the scrub clean", with no home
path and no box login. So line 201 reads: **the collector's scrub ran and found nothing to replace** (no home path and no box login in
any collected file), and the desk-path gate read CLEAN over the 259 files it read. The rest of that paragraph stands. The wording came
from the README form's item 7, as E189's did (E189's note 1, § 3): later kits say what the scrub replaced, or that it found nothing.

## 2. S1T's margin on the starting die (post hoc; the verifier's finding 2)

**Registered.** E191.md 5.2 takes T0 as `die_c.before`, the before bracket's `minshire[0]`. The frozen scorer's E191-S1T (8.3: within
5% on at least 5 of 6) reads **PASS, 5 of 6**. Its e_j_total values are -3.25% (copy, zeros), -4.00% (copy, random), -2.33% (SHA-256),
**-5.22% (sort, sorted: the one outside)**, -4.22% (sort, shuffled) and -2.47% (sparse parity). Every T0 read 50.0-52.0 C, below card
1's footing law's band (56-70 C), so `given()` priced the card at rest by the exponential law in all 24 passes, as registered (output
§ 2). The die reads whole degrees (E191.md 14), and the before bracket averages those readings.

**Post hoc** (deciding nothing): the same frozen code with every pass's T0 moved by one uniform delta, the measured values as committed:
- **downward:** sort, shuffled leaves the 5% band at **-0.650 C**, where S1T's word becomes FAIL (4 of 6). Copy, random leaves at
  -0.904 C (3 of 6), copy, zeros at -1.506 C, SHA-256 at -2.251 C and sparse parity at -2.741 C;
- **upward:** sort, sorted enters the band at **+0.182 C** (6 of 6). Nothing leaves it through +5 C, and the word stays PASS;
- **on a law the registration does not use** (card 1's footing law carried from its 56 C floor down to 40 C, so that it prices every
  pass): S1T reads 6 of 6, its errors -0.80% to -3.62%. A model change, never a reading of the day.

The verifier's own code, which imports nothing from the kit, read the same crossings (-0.65 C, -0.90 C and about +0.18 C) and the same
6 of 6 on the carried law.

**Both readings and the rule.** At T0 as measured, S1T is PASS, 5 of 6. If every T0 were 0.65 C below its reading, S1T would be FAIL, 4
of 6. The rule that decides is E191.md 5.2's T0, the measured `die_c.before`, read by 8.3's E191-S1T: **PASS stands**, and the margin
is reported beside it, never as a reading of the day. The verifier asks that the margin be set beside S1T when `scores-e191.json` is
committed; that commit can cite this section.

**A desk check beside it.** The frozen scorer, run again at the desk on this committed directory as step 13 runs it, wrote the kit's
`scores-e191.json` byte for byte (sha256 `23484c4f546595a728f0c7ffe59e9414d125473108f06891e5dd53283d62ecb8`). This script's delta 0
equals the frozen scorer's own e_j_total for every configuration exactly (difference 0).

## 3. The readings E191.md 8.4 reports (reported, desk arithmetic; the verifier's finding 3)

E191.md 8.4 registers three readings that the README does not carry: section 6's, section 3's literals, and the frozen bands'
coverage. Each is desk arithmetic from the frozen scorer's measured means (its `score_day()` on this directory, output § 3), and none
decides anything. The verifier's own desk arithmetic reads the same figures at the digits it gives.

**Section 6's reading: aifoundry3's prices on card 1** (E191.md lines 201-204: "If card 1 reads closer to it than to E191's own
forecast, card 1's own prices did not help"). J over idle a launch:

| configuration | card 1, measured (mean of 4) | E191's own forecast (given) | its error | E189's frozen forecast (aifoundry3's prices) | its error | nearer |
|---|---:|---:|---:|---:|---:|---|
| copy, zeros | 6.01163 | 5.14344 | -14.44% | 5.14358 | -14.44% | a tie (E189's by 0.002 points) |
| copy, random | 8.25666 | 6.94131 | -15.93% | 6.81368 | -17.48% | E191's own, by 1.55 points |
| SHA-256 | 2.51065 | 2.24593 | -10.54% | 2.30478 | -8.20% | E189's, by 2.34 points |
| sort, sorted | 3.50703 | 2.61968 | -25.30% | 2.71218 | -22.66% | E189's, by 2.64 points |
| sort, shuffled | 3.93060 | 3.18267 | -19.03% | 3.29025 | -16.29% | E189's, by 2.74 points |
| sparse parity | 8.69120 | 8.12737 | -6.49% | 7.34622 | -15.48% | E191's own, by 8.99 points |

So by section 6's words, card 1's own prices did not help for SHA-256 and both sorts, helped for the random copy and sparse parity, and
made no difference for the zeros copy. Sparse parity's E191 figure is the given-seconds mean that S1 scores; its frozen point, 8.13168,
reads -6.44%.

**Section 3's literals** (E191.md lines 88-89: the two literals that carry no card are aifoundry3's rows; card 1's rows were reported
beside them and not used). Each frozen term is bytes times the literal, so card 1's row scales it:

| configuration | literal: frozen, card 1's row | frozen term | card 1's row adds | share of the frozen J over idle | error as registered | error with card 1's row |
|---|---|---:|---:|---:|---:|---:|
| copy, random | the write-back path on random bytes: 325.8, 368.9 pJ/B | 4.89755 J | +0.647896 J | +9.33% | -15.93% | -8.08% |
| SHA-256 | the L2: 2.83, 3.86 pJ/B | 0.0094959 J | +0.003456 J | +0.15% | -10.54% | -10.41% |
| sort, sorted | the L2: 2.83, 3.86 pJ/B | 0.427316 J | +0.155525 J | +5.94% | -25.30% | -20.87% |
| sort, shuffled | the L2: 2.83, 3.86 pJ/B | 0.427316 J | +0.155525 J | +4.89% | -19.03% | -15.07% |

The registration's own column (+0.648 J and +9.3%; +0.156 J, +5.9% and +4.9%; SHA-256 +0.2%) is reproduced at its digits. The copy's
term implies 1.50324e10 bytes written, its 14 GiB a launch.

**The frozen bands' coverage** (the scorer's `j_over_inside_frozen_band` and `j_total_inside_frozen_band`; bands as frozen in
`forecast-e191.json`):

| configuration | J over idle: measured; band; inside | J with the card at rest: measured; band; inside |
|---|---|---|
| copy, zeros | 6.01163; [4.34055, 6.06953]; yes | 33.28934; [20.9251, 33.158]; **no** (above) |
| copy, random | 8.25666; [6.3609, 7.80126]; **no** (above) | 35.58322; [22.9973, 35.173]; **no** (above) |
| SHA-256 | 2.51065; [2.12724, 5.15831]; yes | 15.57101; [13.5419, 39.3626]; yes |
| sort, sorted | 3.50703; [2.06692, 4.83488]; yes | 20.38883; [19.8818, 40.8757]; yes |
| sort, shuffled | 3.93060; [2.60315, 5.8297]; yes | 24.95266; [23.8058, 49.5378]; yes |
| sparse parity | 8.69120; [6.70151, 12.8551]; yes | 24.40809; [20.6229, 37.6575]; yes |

J over idle is inside its frozen band for 5 of 6 and J with the card at rest for 4 of 6. The mean kernel seconds sit inside the frozen
seconds band for 2 of 6 (SHA-256 and sparse parity), which is S2's own term, already in the scorer's output.

## 4. Three notes for the records (the verifier's findings 4, 5 and 6; nothing changes)

1. **The commit message's scan** (finding 4, information). Line 208's "the commit message read 0 lines and 0 sanitizer hits" is about
   the subject and body the card lane wrote. The committed message also carries the two trailer lines that `commit_lab.sh` adds to every
   commit of the round, the session link and the co-author line. On them the lab's sanitizer reads 2 hits, both on the co-author's
   no-reply address (its fixed e-mail pattern, and one entry of the box's local table), and the round's classes read the session link.
   The same trailer is on `1a4bc1e3`, `2d0fe517` and `fa9098c4`. Nothing to fix.
2. **The reducer's grid** (finding 5, information). The unchanged reducer integrates on a grid made by numpy's `arange` from epoch
   seconds ([`energy_reduce.py`](../../../../workloads/sparseparity/tools/energy_reduce.py) lines 136-141) and multiplies the sum by the
   nominal 0.005 s. Near this session's T0, 1794780355 s, floats are 2.38e-7 s apart, so the grid steps by the rounded fl(a + 0.005) -
   a: 0.0050001144 s at T0, +2.3e-5 relative, or one float step lower, -2.5e-5 (output § 4). By the verifier's desk reading, the
   integrals in `energy.json` carry up to about 2e-5 relative from it, at most 1.9e-4 J a launch here, and on an exact 5 ms grid S1's
   rms reads 0.164227 against the scorer's 0.164210. No word moves. The reducer stays unchanged by rule; this is a note for any revision
   of it.
3. **The window file's label** (finding 6, nit). The window file in the card lane's run folder (not committed) carries the kit's
   comment "his go, recorded 2026-11-15 14:03:57 PST by s02_window_e191.sh". 14:03:57 is the moment step 1 wrote the file. In A1's form
   G2 is the card lane's booking, 14:02:10, and line 166 (Departures 3) says so correctly. For a later kit: that comment in
   `s02_window_e191.sh`.

## 5. Lines for the records

1. **The scrub:** it ran and found nothing to replace: 207 of 207 manifest files at the box's own sha256, 209 of 209 equal to the raw
   copy-back, no `~` or login placeholder outside README.md, no home-directory path anywhere (§ 1).
2. **S1T:** PASS, 5 of 6 (registered). Its margin on the starting die (post hoc): S1T's word changes at a uniform -0.650 C (sort,
   shuffled leaves the band: 4 of 6), and sort, sorted enters at +0.182 C (6 of 6). On card 1's footing law carried below 56 C (not
   registered) it reads 6 of 6 (§ 2).
3. **Section 6's reading** (reported): aifoundry3's frozen J over idle reads nearer card 1's measured means than E191's own forecast for
   SHA-256 and both sorts, E191's own is nearer for the random copy and sparse parity, and the zeros copy is a tie (§ 3).
4. **Section 3's literals** (reported): with card 1's rows the random copy reads -8.08%, the sorts -20.87% and -15.07%, SHA-256 -10.41%
   (§ 3).
5. **Band coverage** (reported): J over idle inside the frozen band for 5 of 6 (the random copy above), J with the card at rest for 4 of
   6 (both copies above) (§ 3).
6. **The frozen scorer, re-run at the desk** on the committed directory: byte for byte the kit's `scores-e191.json`, sha256
   `23484c4f...` (§ 2).
7. **The trailer, the grid and the window file's label:** notes only (§ 4).

## What does not change

Every reading, verdict, gate, stop and figure of `README.md` and its files stands. The exceptions are line 201's wording, which § 1
corrects, and the readings §§ 2-3 set beside the verdicts. The reducer, the scorer and the kit read none of this note's files. With the
five new files in this directory (this note, the script, its two outputs and `SHA256SUMS-note1`), before the commit:
- `SHA256SUMS` read 257 of 257 OK and `SHA256SUMS-note1` 7 of 7; the directory held 265 files, and every one but `SHA256SUMS-note1`
  was in one of the two lists;
- the script, run from a copy of this directory into an empty folder and again in place, wrote its two outputs byte for byte;
- the desk-path gate (`nopath_q142s.py`, v3.1, with the lab clone and the lane's folders forbidden) read the five new files with 0 hits,
  and a login check found no home path, no login and no holder line in them;
- the public-text scan (`sanitize_extracts.py`'s fixed list and the box's local table, and the round's lists of private, vendor, access
  and mechanism words) found nothing in the five new files or in this commit's subject and body.

SPDX-License-Identifier: Apache-2.0
