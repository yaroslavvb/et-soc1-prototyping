# E191's third-session data README, dated note 1 (Mon 16 Nov 2026): the frozen scorer's output on the data commit `a28e4f3e`, committed beside it and REPORTED (E191.md's dated amendment A2: the repeat's words, never verdicts of E191) - E191-S1 FAIL, E191-S1T PASS, E191-S2 FAIL, E191-S2T FAIL, the same words as E191's registered verdicts, which are the second session's and stand; the repeat reading and the data verifier's re-derivation beside them

*Beside [`README.md`](README.md), [`SHA256SUMS`](SHA256SUMS) and [`FILES.txt`](FILES.txt), which stay as committed in `a28e4f3e`.
Written on aifoundry2 from 00:58 PST on Mon 16 Nov 2026 (week 47) by the clock, desk only (no card, no lab box, no device, no
post), by Q191's lane `scores-e191c`, after this directory's data verifier `verify-e191c` (00:39-00:58 PST: holds). The kit's step 13 v3
([`rb/s24_score_e191_v3.sh`](../../../../tools/claims-v3/e191/rb/s24_score_e191_v3.sh), the kit's
[dated note 3](../../../../tools/claims-v3/e191/KIT.md.dated-note-3.md)) runs the frozen scorer only after the data commit and leaves its
outputs to a later commit, and README.md's "Next" says the same; this lane is that later lane. This note commits the four outputs byte for
byte, with the scorer's printed lines, labels the third session's words and figures and the repeat reading REPORTED (`scores-e191-s2.json`
is the registered verdicts' own bytes, re-derived), and sets the data verifier's figures beside them.
**No number, rule, verdict, forecast, band, threshold or gate reading changes, and nothing is scored again. E191's registered verdicts are
the second session's and stand** ([A2-1](../../../../tools/claims-v3/e191/E191.md.dated-amendment-A2.md)): E191-S1 FAIL, E191-S1T PASS,
E191-S2 FAIL, E191-S2T FAIL, from
[`../2026-11-15-e191-blind-day-aifoundry1-c1-s2/scores-e191.json`](../2026-11-15-e191-blind-day-aifoundry1-c1-s2/scores-e191.json)
(`f74c81e3`). Interpreter: `/usr/bin/python3` 3.12.3 on aifoundry2. Labels: **registered** (E191.md, its note 1, A1, A2 and the kit with
its notes 2 and 3, as committed), **measured** (the session's committed files and the runbook's records), **REPORTED** (the third session's
words and figures in `scores-e191-s3.json` and `scores-e191-s3.txt`, and the repeat reading: A2-1, "desk arithmetic of measured passes,
deciding nothing"), **desk check of code** (the re-runs and the
verifier's figures) and **post hoc** (§ 6).*

## 1. The new files

| file | what | bytes | sha256 |
|---|---|---|---|
| [`scores-e191-s3.json`](scores-e191-s3.json) | the frozen scorer's output on this directory ([`score_e191.py`](../../../../tools/claims-v3/e191/score_e191.py), registered in `300d76e4`, unchanged): the rules E191-S1, S1T, S2 and S2T with their words, counts and word fields; each configuration's errors, figures and flags, pass by pass; the arms v2.1 and v2c; the section 8.4 cross-checks. All REPORTED (A2-1); its bare `verdict` and `verdict_of_the_day` fields are the repeat's words, never verdicts of E191 | 32,338 | `72443d12...` |
| [`scores-e191-s3.txt`](scores-e191-s3.txt) | the scorer's printed lines on this directory, copied byte for byte from the runbook's capture of step 13 v3's call 7 (its stdout and stderr as they came), not rewritten | 85 | `7c681003...` |
| [`scores-e191-s2.json`](scores-e191-s2.json) | the frozen scorer's output on the second session's directory, re-derived by step 13 v3's call 8 before anything was set beside the verdicts (A2-1's gate): the registered verdicts' bytes, the same as [`../2026-11-15-e191-blind-day-aifoundry1-c1-s2/scores-e191.json`](../2026-11-15-e191-blind-day-aifoundry1-c1-s2/scores-e191.json) (`f74c81e3`); the input the repeat reader read | 31,567 | `23484c4f...` |
| [`repeat-e191-s3.json`](repeat-e191-s3.json) | the repeat reading (`repeat_e191.py`, kit note 3) of the two outputs above: each configuration's errors in both sessions and their differences, the arms, the counts; REPORTED, and labelled so inside | 15,326 | `bbcca4bd...` |
| [`repeat-e191-s3.txt`](repeat-e191-s3.txt) | the repeat reader's printed lines, which the runbook wrote to this file (step 13 v3's call 10; byte-equal to the runbook's capture of that call) | 2,843 | `e3fe7221...` |
| `README.md.dated-note-1.md` | this note | | |

[`SHA256SUMS-note1`](SHA256SUMS-note1) pins these six and `README.md`, `SHA256SUMS` and `FILES.txt` as committed. With `SHA256SUMS`
(257 files, unchanged), every file here is pinned but `SHA256SUMS-note1` itself. The scorer's printed lines on the second session (step 13
v3's call 8) are byte-identical to call 7's and to
[`../2026-11-15-e191-blind-day-aifoundry1-c1-s2/scores-e191.txt`](../2026-11-15-e191-blind-day-aifoundry1-c1-s2/scores-e191.txt)
(`f74c81e3`), so they are not added again.

## 2. When, where and on which commit step 13 v3 ran (measured)

From the runbook's log (`runbook.log`) and its capture of each call, both kept outside the repository in the card lane's runbook folder
RB_OUT, and from the lab clone's own log of its HEAD:

- **Step 13 v3** ([`rb/s24_score_e191_v3.sh`](../../../../tools/claims-v3/e191/rb/s24_score_e191_v3.sh)): Mon 16 Nov 2026 at **00:36:46
  PST**, on aifoundry2, in the lab clone with its HEAD at **`a28e4f3e`**, the data commit (made at 00:36:35 PST and pushed by 00:36:40),
  which stayed the clone's HEAD until the next commit (`72514ce5`, E194's data) at 00:58:14 PST.
- **Its ten calls**, the log's lines 111-120 (its last ten), all at 00:36:46 PST, each with rc 0, each logged at 0.3 s or less: (1) this
  directory committed, the last commit naming it `a28e4f3e`; (2) clean (no line); (3) its `SHA256SUMS`, 257 of 257 entries OK; (4) the
  second session's directory clean; (5) its `SHA256SUMS`, 257 of 257 OK; (6) the history check, `HISTORY OK` (188 files added since
  `46a16bd0` on E191's paths, none changed or removed; nothing under `tools/claims-v3/e191` or `tools/claims-v3/e189` changed since E191's
  registration, note 1 and kit and E189's registration and kit; nothing untracked; no shadowing addition or uncommitted file in the folders
  the day's Python puts first); (7) the frozen scorer on this directory, `/usr/bin/python3 -I -B tools/claims-v3/e191/score_e191.py
  docs/reports/data/2026-11-16-e191-blind-day-aifoundry1-c1-s3 --out RB_OUT/scores-e191-s3.json`; (8) the same on the second session's
  directory into `RB_OUT/scores-e191-s2.json`; (9) its sha256, which read `23484c4f...`, the registered verdicts' bytes, so A2-1's gate let
  the repeat be set beside them; (10) `repeat_e191.py` on the two, into `RB_OUT/repeat-e191-s3.json`, its printed lines into
  `RB_OUT/repeat-e191-s3.txt`.
- **The times:** `scores-e191-s3.json`, `scores-e191-s2.json` and `repeat-e191-s3.json` were each last written at the same instant as the
  runbook's capture of their call (00:36:46.689, 00:36:46.753 and 00:36:46.831 PST). The step's own last line, in the card lane's log of the
  step, begins `[s24_score_v3_e191] scored (REPORTED, the third session's words: A2; never a verdict`. `runbook.log` holds each call's line,
  not its output; the runbook's bounded runner writes each call's stdout and stderr, as they come, to that call's capture file, and
  `scores-e191-s3.txt` is call 7's.
- **Nothing ran the scorer or the repeat reader on data before:** the log's earlier lines run the scorer only as its E59 self-test (line 43,
  step 2's desk checks), and the repeat reader not at all.
- **The scorer and the repeat reader as registered:** the frozen scorer, its list `SHA256SUMS-e191-registration` and the files it reads
  (`forecast_e191.py`, `forecast-e191.json`, `plan-e191.json`, `E191.md`, the ledger v2's `tools/ledger/ledger_v2.py` and `frozen-v2.json`)
  are the same git blobs at the registration `300d76e4`, note 1 `8c8f825f`, the kit `eb1ac923`, kit note 2 `2d0fe517`, A2 with kit note 3
  `318a0985`, the data commit and this note's parent; `repeat_e191.py`, step 13 v3, A2 and kit note 3 are the same blobs at `318a0985`, the
  data commit and this note's parent. From the registration to this note's parent, `tools/claims-v3/e191` changed by additions only, and
  `tools/ledger` and the ledger v2's data folder not at all. Both scorer outputs read `frozen_files_checked` 9 and `not_used` `[]`; the
  registration's list reads 11 of 11.
- **The interpreter:** `/usr/bin/python3` 3.12.3 on aifoundry2, isolated (`-I -B`); the history check's line names it.
- **Re-run since, at the desk, on the committed bytes** (a desk check of code): by this lane (01:06 PST) from a fresh extract of
  `a28e4f3e`'s own tree holding the folders the three computations read (`tools/claims-v3/e191`, `tools/ledger`,
  `docs/reports/data/2026-11-12-q166-ledger-v2`, this directory and the second session's: 677 files, where each directory's `SHA256SUMS`
  read 257 of 257, the registration's list 11 of 11 and A2's list 17 of 17), run as the runbook ran them, in the round's CPU slot with no
  device node reachable: both scorer outputs, the repeat reading and every set of printed lines came out byte-identical to RB_OUT's files
  and the runbook's captures (calls 7, 8 and 10), and the runs wrote nothing into the extract.

## 3. The four rules' words on this directory: REPORTED, beside the registered verdicts

[`scores-e191-s3.txt`](scores-e191-s3.txt), verbatim (`scores-e191-s3.json` > `verdict_of_the_day`, the scorer's word for this directory,
which A2-1 makes REPORTED, never a verdict of E191):

```
{
 "E191-S1": "FAIL",
 "E191-S1T": "PASS",
 "E191-S2": "FAIL",
 "E191-S2T": "FAIL"
}
```

Behind the words (`rules` in each output; the rules are E191.md 8.3's, registered; e = the mean of a configuration's passes' forecast / the
mean of its passes' measured value - 1, and S2 alone reads the ratio mean t_k / point):

| rule | the scorer's words | registered verdict (second session; it stands) | this session (REPORTED): scored, within, outside | this session's word (REPORTED) |
|---|---|---|---|---|
| **E191-S1** | score 1, given the measured seconds: J over idle a launch within 10% on at least 5 of the 6 configurations, and the rms of the six errors at most 10% | **FAIL**, 1 of 6 within (rms 0.1642) | 6, 1, 5 | **FAIL** (rms 0.1867) |
| **E191-S1T** | score 1, given the measured seconds: J with the card at rest a launch within 5% on at least 5 of 6 | **PASS**, 5 of 6 within | 6, 5, 1 | **PASS** |
| **E191-S2** | score 2, with the seconds forecast: the measured kernel seconds inside the frozen two-sided band and within 15% of the point, on at least 5 of 6 | **FAIL**, 1 of 6 within | 6, 1, 5 | **FAIL** |
| **E191-S2T** | score 2, with the seconds forecast: J with the card at rest a launch, at the forecast seconds and die, within 15% on at least 5 of 6 | **FAIL**, 1 of 6 within | 6, 1, 5 | **FAIL** |

Each configuration on this directory (`scores-e191-s3.json` > `configs`; 4 passes scored each, the scorer scoring only passes valid by
E191.md 8.2, and README.md lists none SHORT; `not_used` is empty). Every figure is REPORTED. Score 1, given the measured seconds:

| configuration | J over idle a launch (J), given / measured | error | within 10% (S1) | J with the card at rest a launch (J), given / measured | error | within 5% (S1T) |
|---|---|---|---|---|---|---|
| copy, zeros | 5.143 / 6.211 | -17.19% | no | 33.507 / 34.480 | -2.82% | yes |
| copy, random | 6.941 / 8.281 | -16.18% | no | 35.303 / 36.721 | -3.86% | yes |
| SHA-256 | 2.246 / 2.596 | -13.49% | no | 15.804 / 16.173 | -2.28% | yes |
| sort, sorted | 2.620 / 3.619 | -27.61% | no | 20.092 / 21.156 | -5.03% | no |
| sort, shuffled | 3.183 / 4.121 | -22.77% | no | 24.894 / 25.910 | -3.92% | yes |
| sparse parity | 8.127 / 8.871 | -8.38% | yes | 24.529 / 25.178 | -2.58% | yes |

Score 2, with the seconds forecast (`e_t`, point / mean t_k - 1, is reported beside S2 and does not decide it):

| configuration | mean t_k / point (s) | ratio | frozen band (s) | inside it | S2 | J with the card at rest a launch at the forecast (J), forecast / measured | error | within 15% (S2T) | e_t |
|---|---|---|---|---|---|---|---|---|---|
| copy, zeros | 0.9072 / 0.6557 | 1.384 | 0.5568-0.7546 | no | no | 26.080 / 34.480 | -24.36% | no | -27.73% |
| copy, random | 0.9073 / 0.6557 | 1.384 | 0.5568-0.7546 | no | no | 27.982 / 36.721 | -23.80% | no | -27.73% |
| SHA-256 | 0.4316 / 0.5702 | 0.757 | 0.3848-0.9448 | yes | no | 20.324 / 16.173 | +25.67% | no | +32.10% |
| sort, sorted | 0.5593 / 0.7399 | 0.756 | 0.6007-1.0136 | no | no | 26.062 / 21.156 | +23.19% | no | +32.29% |
| sort, shuffled | 0.6942 / 0.8993 | 0.772 | 0.7148-1.2288 | no | no | 31.676 / 25.910 | +22.25% | no | +29.55% |
| sparse parity | 0.5127 / 0.5147 | 0.996 | 0.4633-0.6692 | yes | yes | 24.805 / 25.178 | -1.48% | yes | +0.39% |

The arms v2.1 and v2c (`scores-e191-s3.json` > `arms`; registered arms, REPORTED in both sessions): v2.1, S1 FAIL (0 of 6 within, rms
0.1904), S1T PASS (5 of 6), S2 FAIL (1 of 6), S2T FAIL (1 of 6); v2c, S1 FAIL (0 of 6 within, rms 0.1906), S1T PASS (5 of 6), S2 FAIL (1 of
6), S2T FAIL (1 of 6). In both arms the three errors of each of the other five configurations (copy, zeros; copy, random; SHA-256; sort,
sorted; sort, shuffled) equal the primary's; sparse parity's e_j_over reads -12.45% / -12.61% and its e_j_total -4.09% / -4.15% (v2.1 /
v2c), against the primary's -8.38% and -2.58%. The arms' words are the same in both sessions (`repeat-e191-s3.txt`).

## 4. The repeat reading: this session minus the second (REPORTED)

[`repeat-e191-s3.json`](repeat-e191-s3.json) and its printed lines [`repeat-e191-s3.txt`](repeat-e191-s3.txt) (`repeat_e191.py`, kit
note 3; it reads the two scorer outputs, unchanged, and labels itself REPORTED). Each difference is the third session minus the second: an
error's in percentage points, a measured mean's as a ratio, and S1's and S1T's over the two sessions' combined standard error of the
per-pass errors. Generated from `repeat-e191-s3.json`, not typed:

| configuration | passes 2nd / 3rd | S1 error 2nd / 3rd | S1 difference (points; over the combined SE) | S1T error 2nd / 3rd | S1T difference (points; over the combined SE) | S2 ratio 2nd / 3rd | S2T error 2nd / 3rd (difference, points) | J over idle, J at rest, mean t_k: 3rd / 2nd - 1 | T0 mean 2nd / 3rd (C) |
|---|---|---|---|---|---|---|---|---|---|
| copy, zeros | 4 / 4 | -14.44% / -17.19% | -2.75; -2.61 | -3.25% / -2.82% | +0.42; +3.59 | 1.3840 / 1.3837 | -21.66% / -24.36% (-2.71) | +3.32%, +3.58%, -0.02% | 50.59 / 53.75 |
| copy, random | 4 / 4 | -15.93% / -16.18% | -0.25; -0.21 | -4.00% / -3.86% | +0.14; +0.97 | 1.3837 / 1.3838 | -21.36% / -23.80% (-2.44) | +0.30%, +3.20%, +0.01% | 50.75 / 53.50 |
| SHA-256 | 4 / 4 | -10.54% / -13.49% | -2.94; -1.02 | -2.33% / -2.28% | +0.05; +0.19 | 0.7570 / 0.7570 | +30.52% / +25.67% (-4.86) | +3.40%, +3.87%, +0.00% | 51.00 / 54.00 |
| sort, sorted | 4 / 4 | -25.30% / -27.61% | -2.31; -1.51 | -5.22% / -5.03% | +0.19; +2.41 | 0.7559 / 0.7559 | +27.82% / +23.19% (-4.63) | +3.19%, +3.76%, -0.00% | 50.75 / 53.77 |
| sort, shuffled | 4 / 4 | -19.03% / -22.77% | -3.74; -1.14 | -4.22% / -3.92% | +0.30; +0.84 | 0.7719 / 0.7719 | +26.94% / +22.25% (-4.69) | +4.84%, +3.84%, +0.00% | 50.75 / 53.90 |
| sparse parity | 4 / 4 | -6.49% / -8.38% | -1.90; -3.70 | -2.47% / -2.58% | -0.11; -1.00 | 0.9965 / 0.9961 | +1.63% / -1.48% (-3.11) | +2.06%, +3.16%, -0.04% | 51.00 / 53.98 |

Every configuration meets or misses the same rules in both sessions: E191-S1 6 of 6, E191-S1T 6 of 6, E191-S2 6 of 6, E191-S2T 6 of 6. The
repeat reader's last line: `REPEAT-E191 REPORTED: 6 configurations compared, 0 with NO DATA in a session; the registered verdicts stand:
E191-S1 FAIL, E191-S1T PASS, E191-S2 FAIL, E191-S2T FAIL`. Its per-rule lines set each registered verdict (the second session's, which
stands) beside this session's REPORTED word; they are the same four words, with the same counts, and S1's rms reads 0.1642 then 0.1867.

## 5. Beside verify-e191c's independent re-derivation (desk check of code)

`verify-e191c` (Mon 16 Nov 2026, 00:39:35-00:57:42 PST) re-derived the four rules from this directory's committed raw files, taken from
`a28e4f3e`, and from the second session's (`7156ac15`), with its own code: the standard library only, importing nothing from the kit or the
lab; card 1's laws and prices read as data from the ledger v2's `frozen-v2.json` and the frozen points from `forecast-e191.json`
(`300d76e4`); `/usr/bin/python3` 3.12.3. It then computed the third-minus-second differences itself. Its figures are a desk check of code.
Each pair below is **the scorer / verify-e191c**, generated from `scores-e191-s3.json` and from the verifier's own output file, not typed.

| rule | scored | within | word (REPORTED) | S1's rms |
|---|---|---|---|---|
| E191-S1 | 6 / 6 | 1 / 1 | FAIL / FAIL | 0.186655 / 0.186655 |
| E191-S1T | 6 / 6 | 5 / 5 | PASS / PASS |  |
| E191-S2 | 6 / 6 | 1 / 1 | FAIL / FAIL |  |
| E191-S2T | 6 / 6 | 1 / 1 | FAIL / FAIL |  |

| configuration | e_j_over (S1) | e_j_total (S1T) | e_j_total_forecast (S2T) | S1, S1T, S2, S2T |
|---|---|---|---|---|
| copy, zeros | -17.194% / -17.194% | -2.822% / -2.822% | -24.364% / -24.364% | no, yes, no, no / no, yes, no, no |
| copy, random | -16.181% / -16.181% | -3.861% / -3.861% | -23.800% / -23.800% | no, yes, no, no / no, yes, no, no |
| SHA-256 | -13.485% / -13.485% | -2.283% / -2.283% | +25.665% / +25.665% | no, yes, no, no / no, yes, no, no |
| sort, sorted | -27.612% / -27.612% | -5.027% / -5.027% | +23.191% / +23.191% | no, no, no, no / no, no, no, no |
| sort, shuffled | -22.768% / -22.768% | -3.919% / -3.919% | +22.254% / +22.254% | no, yes, no, no / no, yes, no, no |
| sparse parity | -8.384% / -8.384% | -2.578% / -2.578% | -1.481% / -1.481% | yes, yes, yes, yes / yes, yes, yes, yes |

**Agree or differ.** The same words and counts for every rule, and S1's rms agrees to 3.5e-08; every configuration's errors agree within
4.7e-07 (the verifier's own worst difference, recorded in its file, is the same number) and every one of the 24 rule flags is the same. Its
re-derivation of the second session gives the registered words and counts (S1 rms 0.164210), its errors within 4.8e-07 of `23484c4f...`. Its
own third-minus-second differences, 60 values over the six configurations, agree with `repeat-e191-s3.json` within 1e-6 in 59 cases (its S2
ratio difference is the repeat's `t_ratio_points` under another name); the one other, sparse parity's S1T difference over the combined SE,
reads -0.996032 / -0.996036 (verifier / repeat), 4.2e-06 apart, which the verifier puts down to its own rounded sparse-parity constants. The
verifier's other checks held: the files and their lists, the scrub, card 1's identity, 600 MHz throughout, reads only, the window, the rest
and the flags released (its result, outside the repository).

## 6. verify-e191c's findings, each answered (dated clauses, Mon 16 Nov 2026, PST)

1. **Finding 1 (low): `scores-e191-s3.json` carries no REPORTED label inside it** (its `verdict` and `verdict_of_the_day` fields are bare),
   though A2-1 makes them REPORTED. **Answered here, Mon 16 Nov 2026:** the file is the frozen scorer's output and is committed byte for
   byte, so its label is this note's: every `verdict`, `verdict_of_the_day` and `ok_` flag in `scores-e191-s3.json`, and every word in
   `scores-e191-s3.txt`, is the third session's REPORTED word, never a verdict of E191, and the registered verdicts are the second session's
   (A2-1). `repeat-e191-s3.json` and `repeat-e191-s3.txt` carry the label themselves. `scores-e191-s2.json` is the registered verdicts' own
   bytes, re-derived. The verifier's post hoc margin (finding 2) is quoted next, as it asked.
2. **Finding 2 (information, post hoc, deciding nothing): S1T's margin.** This session's REPORTED S1T PASS (5 of 6 within 5%) rests on
   whole-degree starting-die readings (T0), with sort, sorted the one outside at -5.03%. In the verifier's post hoc reading (its own code),
   if every pass's T0 read 1 C lower, 3 of 6 would be within (outside: copy, random at -5.02%; sort, sorted at -6.27%; sort, shuffled at
   -5.18%); if 1 C higher, 6 of 6. The registered verdict, from the second session, is untouched by it; the second session's own margin is
   in that directory's note 1, section 2.
3. **Finding 3 (information, REPORTED): the sessions differ by more than their scatter in two places.** S1's error moved by -2.75 points for
   copy, zeros (-2.61 combined SE) and by -1.90 points for sparse parity (-3.70); J over idle a launch rose by +3.32% and +2.06%. The die
   started 2.75 to 3.16 C warmer, and the config reads gave power state 1 where Sunday's gave 3 (README.md, Departures and notes 12, post
   hoc; nothing was set). Every configuration meets or misses the same rules in both sessions (§ 4). No frozen item is read from it (A2-1).
4. **Finding 4 (nit): README.md's privacy sentence.** It reads "The collector's scrub ran (the box's home path became `~`, the box login
   `<login>`)". **Clause, Mon 16 Nov 2026:** the parenthesis states what the scrub does, not a change it made here; on this session's files
   the scrub replaced nothing. The verifier found all 207 files of the session's manifest equal to the raw copy-back (0 equal only after a
   scrub, none different or missing); the collector's own line read that the scrub was clean (no home path, no box login); and this lane's
   search of the committed text files finds the login mark only in README.md's own sentence and no path beginning `~/`. Read it as "The
   collector's scrub ran and found nothing to replace".
5. **Finding 5 (nit): a label in the card lane's own log, outside the repository.** A window helper the lane reused printed its window under
   the second session's label (G2) where it was G3. **Clause, Mon 16 Nov 2026:** no committed file of this directory carries that label
   (this lane's search of the data commit: 0 files), and README.md gives the window as run: G3 = the lane's booking of aifoundry1 at
   00:00:41 PST, last start 01:31 and last end 03:31 PST. Nothing changes.

## 7. Checks before the commit

Run by this lane before the commit (its `s05_check.sh`, in the round's CPU slot), over the exact bytes committed:
- **The bytes:** the five byte-for-byte files equal RB_OUT's files and the runbook's capture of call 7, and this lane's re-run (§ 2); the
  card lane's log of step 13 holds captures 7 and 10.
- **The directory as it will stand** (a copy: the data commit's files plus the seven new ones): 267 files; `SHA256SUMS` 257 of 257 and
  `SHA256SUMS-note1` 9 of 9 entries OK; every file in a list but `SHA256SUMS-note1`.
- **The desk-path gate** (the lab's `nopath_q142s.py` v3.1, the lab clone, the round's folders and the session's scratch folders forbidden):
  CLEAN on the seven files.
- **The login check:** no home path, no login, no e-mail address, no device-holder line, in the seven files or the message.
- **The public-text scan** (the lab's sanitizer, `tools/timeline/sanitize_extracts.py`, its fixed list and the local privacy table, and the
  tier classes: foundry, process, vendor and design-file words, credentials, network and access words, private words and paths): 0 counted
  hits in the seven files and the commit message. 4 reviewed matches are listed, not counted: the scorer's own key and text for its card
  memory term in sparse parity's rail cross-check, twice in each scorer output (`score_e191.py`, registered in `300d76e4`). They stay,
  because those files are committed byte for byte.

## What does not change

Every reading, gate, stop and figure of `README.md` and its files stands, and so do E191's verdicts, the second session's (A2-1); this
note adds the scorer's outputs beside them, labels them REPORTED and reads them, and changes nothing. The first and second sessions'
directories (`...-c1`, `...-c1-s2`) and their notes stay as committed. The reducer, the scorer and the kit read none of this note's files.
This lane reached no box, opened no device and changed no committed file.

SPDX-License-Identifier: Apache-2.0
