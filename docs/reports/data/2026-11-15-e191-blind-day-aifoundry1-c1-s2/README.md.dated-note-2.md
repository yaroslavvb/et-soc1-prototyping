# E191's second-session data README, dated note 2 (Sun 15 Nov 2026): the frozen scorer's output, run on the data commit `7156ac15`, committed beside it - E191-S1 FAIL, E191-S1T PASS, E191-S2 FAIL, E191-S2T FAIL; the data verifier's own re-derivation gives the same words and counts

*Beside [`README.md`](README.md), [`SHA256SUMS`](SHA256SUMS) and [`FILES.txt`](FILES.txt), which stay as committed in `7156ac15`, and
note 1's five files ([`README.md.dated-note-1.md`](README.md.dated-note-1.md) and the four beside it, `aaf70691`), which stay as committed
too. Written on aifoundry2 from 17:18 PST on Sun 15 Nov 2026 (week 46) by the clock, desk only (no card, no lab box, no device, no post),
by Q184's lane `scores-e191`, after this directory's data verifier `verify-e191b` (14:35-15:00 PST: holds with fixes) and note 1
(`fix-e191b`, committed 17:11:50 PST). The kit's step 13 ([`KIT.md`](../../../../tools/claims-v3/e191/KIT.md), its table of steps:
"`score_e191.py` (registered, unchanged) on the committed data; RB_OUT/scores-e191.json; read the words"), in its v2 form for this
directory ([`rb/s24_score_e191_v2.sh`](../../../../tools/claims-v3/e191/rb/s24_score_e191_v2.sh), the kit's dated note 2), runs the frozen
scorer only after the data commit and leaves its output to a later commit, and README.md's "Next" says the same; this lane is that later
lane. This note commits the output byte for byte, with the scorer's printed lines, and sets the data verifier's figures beside the
scorer's. **No number, rule, verdict, forecast, band, threshold or gate reading changes, and nothing is scored again.** Interpreter:
`/usr/bin/python3` 3.12.3 on aifoundry2. Labels: **registered** (E191.md, its note 1, A1 and the kit as committed), **measured** (the
session's committed files), **desk check of code** (the re-runs and the verifier's figures), **post hoc** and **reported** (§ 5, from note
1). The verdicts are the frozen scorer's own output on the committed data. The first session's record (`1a4bc1e3`, the directory
[`../2026-11-15-e191-blind-day-aifoundry1-c1/`](../2026-11-15-e191-blind-day-aifoundry1-c1/)) gets its own scorer output and note in
the same commit as this note; it is used by no rule (A1-2).*

## 1. The new files

| file | what | bytes | sha256 |
|---|---|---|---|
| [`scores-e191.json`](scores-e191.json) | the frozen scorer's output ([`score_e191.py`](../../../../tools/claims-v3/e191/score_e191.py), registered in `300d76e4`, unchanged): the rules E191-S1, S1T, S2 and S2T with their words, counts and verdicts; each configuration's errors, figures and flags, pass by pass; the arms v2.1 and v2c (reported); the section 8.4 cross-checks (reported, not scored) | 31,567 | `23484c4f...` |
| [`scores-e191.txt`](scores-e191.txt) | the scorer's printed lines, copied byte for byte from the runbook's capture of that call (its stdout and stderr as they came), not rewritten | 85 | `7c681003...` |
| `README.md.dated-note-2.md` | this note | | |

[`SHA256SUMS-note2`](SHA256SUMS-note2) pins these three and `SHA256SUMS-note1`. With `SHA256SUMS` (257 files, unchanged) and
`SHA256SUMS-note1` (7 entries: note 1's four files, `README.md`, `SHA256SUMS` and `FILES.txt`), every file here is pinned but
`SHA256SUMS-note2` itself.

## 2. When, where and on which commit the scorer ran

From the runbook's log (`runbook.log`) and its capture of each call, both kept outside the repository in the card lane's runbook folder
RB_OUT, and from the lab clone's own log of its HEAD:

- **Step 13 v2, the frozen scorer** ([`rb/s24_score_e191_v2.sh`](../../../../tools/claims-v3/e191/rb/s24_score_e191_v2.sh), the kit's): Sun
  15 Nov 2026 at **14:32:33 PST**, on aifoundry2, in the lab clone with its HEAD at **`7156ac15`**, the data commit (made at 14:32:17 PST
  and pushed by 14:32:22), which stayed the clone's HEAD until the next commit (`e8a85229`, Q182 records) at 14:32:45 PST.
- **Its gates**, the log's lines 99-102, at 14:32:32-14:32:33 PST, each with rc 0: the data directory committed (the last commit naming it:
  `7156ac15`); the directory clean (no line); `SHA256SUMS` 257 of 257 entries OK; the history check, `HISTORY OK` (168 files added since
  `46a16bd0` on E191's paths, none changed or removed; E191's registration `300d76e4`, its note 1 `8c8f825f` and its kit `eb1ac923`, and
  E189's registration `c86940c1` and kit `b42dc95c`: nothing under `tools/claims-v3/e191` or `tools/claims-v3/e189` changed since; nothing
  untracked; no shadowing addition or uncommitted file in the folders the day's Python puts first).
- **The scorer**, the log's line 103 (its last): `/usr/bin/python3 -I -B tools/claims-v3/e191/score_e191.py
  docs/reports/data/2026-11-15-e191-blind-day-aifoundry1-c1-s2 --out RB_OUT/scores-e191.json`, rc 0 in 0.0 s (under 0.05 s).
  `scores-e191.json` was last written at 14:32:33.289, the same instant as the runbook's capture of the scorer's printed lines (the step's
  fifth call). The step then printed its own last line, which card-e191b's log of the step holds: `[s24_score_v2_e191] scored:
  {"E191-S1":"FAIL","E191-S1T":"PASS","E191-S2":"FAIL","E191-S2T":"FAIL"} (RB_OUT/scores-e191.json; the records lane commits it beside the
  data)`. `runbook.log` itself holds each call's line, not its output; the runbook's bounded runner (v3.1's `rb_run.py`) writes each call's
  stdout and stderr, as they come, to that call's capture file, and `scores-e191.txt` is the scorer's.
- **The scorer as registered:** `score_e191.py`, its list `SHA256SUMS-e191-registration` and the files it reads (`forecast_e191.py`,
  `forecast-e191.json`, `plan-e191.json`, `E191.md`, the ledger v2's `tools/ledger/ledger_v2.py` and `frozen-v2.json`) are the same git
  blobs at the registration `300d76e4`, note 1 `8c8f825f`, the kit `eb1ac923`, the kit's dated note 2 `2d0fe517`, the data commit and this
  note's parent; from the registration to this note's parent, `tools/claims-v3/e191` changed by additions only, and `tools/ledger` and the
  ledger v2's data folder not at all. The scorer refuses unless the 9 frozen files of that list (all but its two self-test outputs) read OK,
  and its record reads `frozen_files_checked` 9 and `not_used` `[]`; the whole list reads 11 of 11.
- **The interpreter:** `/usr/bin/python3` 3.12.3 on aifoundry2, isolated (`-I -B`); the history check's line names it.
- **Re-run since, at the desk, on the committed bytes** (desk checks of code; each JSON byte-equal to `scores-e191.json`, and each run's
  printed lines to `scores-e191.txt`): by `fix-e191b` (15:14 PST) from an extract of the lab at `e8a85229`; and by this lane (17:25 PST)
  from a fresh extract of `7156ac15`'s own tree holding the four folders the scorer reads (`tools/claims-v3/e191`, `tools/ledger`,
  `docs/reports/data/2026-11-12-q166-ledger-v2` and this directory: 389 files, where `SHA256SUMS` read 257 of 257 and the registration's
  list 11 of 11), run as the runbook ran it, in the round's CPU slot with no device node reachable. The run wrote nothing into the extract.

## 3. The four rules' words, as the frozen scorer gives them

[`scores-e191.txt`](scores-e191.txt), verbatim (`scores-e191.json` > `verdict_of_the_day`):

```
{
 "E191-S1": "FAIL",
 "E191-S1T": "PASS",
 "E191-S2": "FAIL",
 "E191-S2T": "FAIL"
}
```

Behind the words (`scores-e191.json` > `rules`; the rules are E191.md 8.3's, registered; each configuration's error is e = the mean of
its passes' forecast / the mean of its passes' measured value - 1, and S2 alone reads the ratio mean t_k / point):

| rule | the scorer's words | scored | within | outside | word |
|---|---|---|---|---|---|
| **E191-S1** | score 1, given the measured seconds: J over idle a launch within 10% on at least 5 of the 6 configurations, and the rms of the six errors at most 10% | 6 | 1 | 5 | **FAIL** (rms 0.1642) |
| **E191-S1T** | score 1, given the measured seconds: J with the card at rest a launch within 5% on at least 5 of 6 | 6 | 5 | 1 | **PASS** |
| **E191-S2** | score 2, with the seconds forecast: the measured kernel seconds inside the frozen two-sided band and within 15% of the point, on at least 5 of 6 | 6 | 1 | 5 | **FAIL** |
| **E191-S2T** | score 2, with the seconds forecast: J with the card at rest a launch, at the forecast seconds and die, within 15% on at least 5 of 6 | 6 | 1 | 5 | **FAIL** |

Each configuration (`scores-e191.json` > `configs`; 4 passes each, every one valid by E191.md 8.2 and none SHORT; `not_used` is empty).
Score 1, given the measured seconds:

| configuration | J over idle a launch (J), given / measured | error | within 10% (S1) | J with the card at rest a launch (J), given / measured | error | within 5% (S1T) |
|---|---|---|---|---|---|---|
| copy, zeros | 5.143 / 6.012 | -14.44% | no | 32.209 / 33.289 | -3.25% | yes |
| copy, random | 6.941 / 8.257 | -15.93% | no | 34.161 / 35.583 | -4.00% | yes |
| SHA-256 | 2.246 / 2.511 | -10.54% | no | 15.208 / 15.571 | -2.33% | yes |
| sort, sorted | 2.620 / 3.507 | -25.30% | no | 19.325 / 20.389 | -5.22% | no |
| sort, shuffled | 3.183 / 3.931 | -19.03% | no | 23.900 / 24.953 | -4.22% | yes |
| sparse parity | 8.127 / 8.691 | -6.49% | yes | 23.805 / 24.408 | -2.47% | yes |

Score 2, with the seconds forecast (`e_t`, point / mean t_k - 1, is reported beside S2 and does not decide it):

| configuration | mean t_k / point (s) | ratio | frozen band (s) | inside it | S2 | J with the card at rest a launch at the forecast (J), forecast / measured | error | within 15% (S2T) | e_t |
|---|---|---|---|---|---|---|---|---|---|
| copy, zeros | 0.9074 / 0.6557 | 1.384 | 0.5568-0.7546 | no | no | 26.080 / 33.289 | -21.66% | no | -27.74% |
| copy, random | 0.9072 / 0.6557 | 1.384 | 0.5568-0.7546 | no | no | 27.982 / 35.583 | -21.36% | no | -27.73% |
| SHA-256 | 0.4316 / 0.5702 | 0.757 | 0.3848-0.9448 | yes | no | 20.324 / 15.571 | +30.52% | no | +32.10% |
| sort, sorted | 0.5593 / 0.7399 | 0.756 | 0.6007-1.0136 | no | no | 26.062 / 20.389 | +27.82% | no | +32.29% |
| sort, shuffled | 0.6942 / 0.8993 | 0.772 | 0.7148-1.2288 | no | no | 31.676 / 24.953 | +26.94% | no | +29.56% |
| sparse parity | 0.5129 / 0.5147 | 0.996 | 0.4633-0.6692 | yes | yes | 24.805 / 24.408 | +1.63% | yes | +0.35% |

The arms v2.1 and v2c (`scores-e191.json` > `arms`; registered arms, REPORTED: the day's verdict is the primary's): v2.1, S1 FAIL (0 of 6
within, rms 0.1678), S1T PASS (5 of 6), S2 FAIL (1 of 6), S2T FAIL (1 of 6); v2c, S1 FAIL (0 of 6 within, rms 0.1679), S1T PASS (5 of 6), S2
FAIL (1 of 6), S2T FAIL (1 of 6). In both arms the three errors of each of the other five configurations (copy, zeros; copy, random;
SHA-256; sort, sorted; sort, shuffled) equal the primary's; sparse parity's e_j_over reads -10.64% / -10.80% and its e_j_total -4.02% /
-4.08% (v2.1 / v2c), against the primary's -6.49% and -2.47%.

## 4. Beside verify-e191b's independent re-derivation

`verify-e191b` (Sun 15 Nov 2026, 14:35-15:00 PST) re-derived the four rules from this directory's committed raw files, taken from
`7156ac15`, with its own code: the standard library only, importing nothing from the kit or the lab; `given()` written from E191.md 5.2
and the ledger's formulas, the rules from 8.2-8.3, card 1's laws and prices read as data from the ledger v2's `frozen-v2.json` and the
frozen points from `forecast-e191.json` (`300d76e4`); `/usr/bin/python3` 3.12.3. Its figures are a desk check of code. Each pair below is
**the scorer / verify-e191b**, generated from `scores-e191.json` and from the verifier's own output file, not typed.

| rule | scored | within | word | S1's rms |
|---|---|---|---|---|
| E191-S1 | 6 / 6 | 1 / 1 | FAIL / FAIL | 0.164209527 / 0.164209527 |
| E191-S1T | 6 / 6 | 5 / 5 | PASS / PASS |  |
| E191-S2 | 6 / 6 | 1 / 1 | FAIL / FAIL |  |
| E191-S2T | 6 / 6 | 1 / 1 | FAIL / FAIL |  |

| configuration | e_j_over (S1) | e_j_total (S1T) | mean t_k in s (S2) | e_j_total_forecast (S2T) | e_t | S1, S1T, S2, S2T |
|---|---|---|---|---|---|---|
| copy, zeros | -14.4419% / -14.4419% | -3.2464% / -3.2464% | 0.907397 / 0.907397 | -21.6578% / -21.6578% | -27.7436% / -27.7436% | no yes no no / no yes no no |
| copy, random | -15.9308% / -15.9308% | -3.9969% / -3.9969% | 0.907200 / 0.907200 | -21.3629% / -21.3629% | -27.7280% / -27.7280% | no yes no no / no yes no no |
| SHA-256 | -10.5440% / -10.5440% | -2.3319% / -2.3319% | 0.431619 / 0.431619 | +30.5233% / +30.5233% | +32.1021% / +32.1021% | no yes no no / no yes no no |
| sort, sorted | -25.3020% / -25.3020% | -5.2190% / -5.2190% | 0.559301 / 0.559301 | +27.8249% / +27.8249% | +32.2929% / +32.2929% | no no no no / no no no no |
| sort, shuffled | -19.0283% / -19.0283% | -4.2172% / -4.2172% | 0.694154 / 0.694154 | +26.9432% / +26.9432% | +29.5580% / +29.5580% | no yes no no / no yes no no |
| sparse parity | -6.4874% / -6.4874% | -2.4699% / -2.4699% | 0.512928 / 0.512928 | +1.6278% / +1.6278% | +0.3534% / +0.3534% | yes yes yes yes / yes yes yes yes |

**Agree or differ.** The four rules' words and counts are the same by both, and S1's rms is the same number by both (0.16420952693502544).
Every configuration figure above, and beneath it each configuration's given and measured means, is the same float by both (the verifier's
largest difference over the six configurations: 0); pass by pass, its given values differ from the scorer's by at most 3.6e-15 J, its
measured values, seconds and T0 by 0. Nothing differs that could move a word or a count.

**More of its readings** (desk checks of code): its own reduction of the raw telemetry, with no `energy.json` at all (an exact integral of
the board average and the before bracket), gives the same words and counts (S1 FAIL 1 of 6, S1T PASS 5 of 6, S2 FAIL 1 of 6, S2T FAIL 1 of
6; S1's rms 0.164229); so do the reducer's 5 ms grid on the same samples (S1's rms 0.164227), that grid with numpy's `arange` step rule
(S1's rms 0.164210; against `energy.json` at most 5.0e-06 J apart on J over idle and 5.0e-06 J on J with the card at rest, T0 equal, t_w at
most 3.0e-06 s apart) and E191.md 5.2's printed six-digit constants (S1's rms 0.164209); and the arms v2.1 and v2c, re-derived, read the
scorer's words and counts in all four rules, S1's rms 0.167777 / 0.167777 and 0.167950 / 0.167950 (the scorer / verify-e191b).

## 5. S1T's margin and E191.md 8.4's readings (post hoc and reported; note 1 §§ 2-3)

The verifier asked (its findings 2 and 3) that S1T's margin on the starting die be set beside S1T when `scores-e191.json` is committed,
and that the three readings E191.md 8.4 reports be given. Note 1 §§ 2-3 computed both with the frozen scorer's own code; its output,
[`posthoc-note1-e191.json`](posthoc-note1-e191.json), gives the figures below (generated from that file, not typed). **The registered word
stands: S1T PASS, 5 of 6 within 5%, at T0 as measured** (E191.md 5.2: `die_c.before`).

- **At T0 as measured:** every pass's T0 read 50-52 °C, below card 1's footing law's band (56-70 °C), so `given()` priced the card at rest
  by the exponential law in all 24 passes, as registered (note 1 § 2).
- **Downward**, every pass's T0 moved by one uniform delta (post hoc): sort, shuffled leaves the 5% band at -0.650 °C, where S1T's word
  becomes FAIL (4 of 6 within); copy, random at -0.904 °C (3 of 6); then copy, zeros at -1.506 °C; SHA-256 at -2.251 °C; sparse parity at
  -2.741 °C.
- **Upward:** sort, sorted enters the band at +0.182 °C (6 of 6 within); no configuration leaves it upward in note 1's scan (from -5 to +5
  °C), and the word stays PASS.
- **On a law the registration does not use** (card 1's footing law carried from its floor down to 40 °C): S1T reads 6 of 6, PASS. A model
  change, never a reading of the day.
- A reading beside the word, never the day's word: E191.md 5.2's T0, the measured `die_c.before`, read by 8.3's E191-S1T, decides.
- **E191.md 8.4's readings** (reported, desk arithmetic, deciding nothing; note 1 § 3): by section 6's reading, aifoundry3's frozen J over
  idle (E189's) reads nearer card 1's measured means than E191's own forecast for SHA-256, the sort on sorted input and the sort on shuffled
  input; E191's own reads nearer for the random copy and sparse parity; the zeros copy reads -14.44% by both (E189's nearer by 0.002
  points), a tie. With card 1's rows for section 3's two literals, the errors read the random copy -8.08% (registered -15.93%); the sort on
  sorted input -20.87% (registered -25.30%); the sort on shuffled input -15.07% (registered -19.03%); SHA-256 -10.41% (registered -10.54%).
  J over idle is inside its frozen band for 5 of 6 (the random copy above it) and J with the card at rest for 4 of 6 (the zeros copy and the
  random copy above it).

## 6. Checks before the commit

- `scores-e191.json` and `scores-e191.txt` as staged are byte-equal to the card lane's RB_OUT file and to the runbook's capture of the
  scorer's call (`cmp`), and to both desk re-runs (§ 2); the card lane's log of the step holds the same printed lines.
- In a copy of this directory with the four new files: `SHA256SUMS` 257 of 257, `SHA256SUMS-note1` 7 of 7 and `SHA256SUMS-note2` 4 of 4
  entries OK; 269 files, every one in a list but `SHA256SUMS-note2`.
- The desk-path gate (`nopath_q142s.py`, v3.1, with the lab clone and the round's folders forbidden) read the four new files with 0 hits,
  and a login check found no home path, no login and no holder line in them or in this commit's subject and body.
- The public-text scan (the lab's `sanitize_extracts.py`, its fixed list and the box's local table, and the round's lists of private,
  vendor, access and mechanism words) found nothing in this note, `scores-e191.txt`, `SHA256SUMS-note2` or this commit's subject and body.
  In `scores-e191.json` it matched twice, both on one word of the round's desk-path list that the frozen scorer uses as its key and its text
  for a card memory term in sparse parity's rail cross-check (`score_e191.py` lines 217-219, committed since the registration): a false
  match, kept as written, since the file is committed byte for byte.
- Both directories' new files went into one commit, with nothing else.

## What does not change

Every reading, verdict, gate, stop and figure of `README.md`, note 1 and their files stands; this note adds the scorer's output beside
them and reads it, and changes nothing. The reducer, the scorer and the kit read none of this note's files. This lane reached no box,
opened no device and changed no committed file.

SPDX-License-Identifier: Apache-2.0
