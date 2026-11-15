# E189's data README, dated note 2 (Sat 14 Nov 2026): the frozen scorer's output, run on the data commit `fa9098c4`, committed beside it - E189-S1 FAIL, E189-S1T PASS, E189-S2 FAIL, E189-S2T FAIL; the data verifier's own re-derivation gives the same words and counts

*Beside [`README.md`](README.md) and [`SHA256SUMS`](SHA256SUMS), which stay as committed in `fa9098c4`, and note 1's five files
([`README.md.dated-note-1.md`](README.md.dated-note-1.md) and the four beside it, `caca0c1f`), which stay as committed too. Written on
aifoundry2 from 22:19 PST on Sat 14 Nov 2026 (week 46) by the clock, desk only (no card, no lab box, no device, no post), by Q174's lane
`scores-e189`, after E189's data verifier `verify-e189d` (20:37-20:59 PST: holds with fixes) and note 1 (`fix-e189d`, 22:17 PST). The
kit's step 13 ([`KIT.md`](../../../../tools/claims-v3/e189/KIT.md), its table of steps: "`score_e189.py` (registered, unchanged) on the
committed data; its output to RB_OUT, committed by the records lane") runs the frozen scorer only after the data commit and leaves its
output to a later commit, and README.md's "Next" says the same; this lane is that records lane. This note commits the output byte for
byte, with the scorer's printed lines, and sets the data verifier's figures beside the scorer's. **No number, rule, verdict, forecast,
band, threshold or gate reading changes, and nothing is scored again.** Interpreter: `/usr/bin/python3` 3.12.3 on aifoundry2. Labels:
**registered** (E189.md and the kit as committed), **measured** (the session's committed files), **desk check of code** (the re-runs and
the verifier's figures), **post hoc** (§ 5). The verdicts are the frozen scorer's own output on the committed data.*

## 1. The new files

| file | what | bytes | sha256 |
|---|---|---|---|
| [`scores-e189.json`](scores-e189.json) | the frozen scorer's output ([`score_e189.py`](../../../../tools/claims-v3/e189/score_e189.py), registered in `c86940c1`, unchanged): the rules E189-S1, S1T, S2 and S2T with their words, counts and verdicts; each configuration's errors, figures and flags, pass by pass; the arms v2.1 and v2c (reported); the section 8.4 readings (reported, not scored) | 33,711 | `ac8770ba...` |
| [`scores-e189.txt`](scores-e189.txt) | the scorer's printed lines, copied byte for byte from the runbook's capture of that call (its stdout and stderr as they came), not rewritten | 85 | `6e6e2731...` |
| `README.md.dated-note-2.md` | this note | | |

[`SHA256SUMS-note2`](SHA256SUMS-note2) pins these three. With `SHA256SUMS` (228 files, unchanged) and `SHA256SUMS-note1` (6 entries:
note 1's four files, `README.md` and `SHA256SUMS`), every file here is pinned but `SHA256SUMS-note1` and `SHA256SUMS-note2` themselves.

## 2. When, where and on which commit the scorer ran

From the runbook's log (`runbook.log`) and its capture of each call, both kept outside the repository in the card lane's runbook folder
RB_OUT, and from the lab clone's own log of its HEAD:

- **Step 13, the frozen scorer** ([`rb/s24_score_e189.sh`](../../../../tools/claims-v3/e189/rb/s24_score_e189.sh), the kit's): Sat 14
  Nov 2026 at **20:34:30 PST**, on aifoundry2, in the lab clone with its HEAD at **`fa9098c4`**, the data commit (made at 20:34:12 PST and
  pushed by 20:34:15), which stayed the clone's HEAD until the next commit (E192's data, `a6e17e83`) at 22:16:26 PST.
- **Its gates**, the log's lines 71-74, each at 20:34:30 with rc 0: the data directory committed (the last commit naming it: `fa9098c4`);
  the directory clean (no line); `SHA256SUMS` 228 of 228 entries OK; the history check, `HISTORY OK` (59 files added since `46a16bd0` on
  E189's paths, none changed or removed; the registration `c86940c1`; the kit `b42dc95c`; nothing under `tools/claims-v3/e189` changed
  since; nothing untracked; no shadowing addition or uncommitted file in the folders the day's Python puts first).
- **The scorer**, the log's line 75: `/usr/bin/python3 -I -B tools/claims-v3/e189/score_e189.py
  docs/reports/data/2026-11-14-e189-blind-day-aifoundry3 --out RB_OUT/scores-e189.json`, rc 0 in 0.0 s (under 0.05 s). `scores-e189.json`
  was last written at 20:34:30.728, the same instant as the runbook's capture of the scorer's printed lines (the step's fifth call). The
  step then printed its own last line, which the card lane's log of the step holds: `[s24_score_e189] scored:
  {"E189-S1":"FAIL","E189-S1T":"PASS","E189-S2":"FAIL","E189-S2T":"FAIL"} (RB_OUT/scores-e189.json; the records lane commits it beside the
  data)`. `runbook.log` itself holds each call's line, not its output; the runbook's bounded runner (v3.1's `rb_run.py`) writes each
  call's stdout and stderr, as they come, to that call's capture file, and `scores-e189.txt` is the scorer's.
- **The scorer as registered:** `score_e189.py`, its list `SHA256SUMS-e189-registration` and the files it reads (`forecast_e189.py`,
  `forecast-e189.json`, `plan-e189.json`, `E189.md`, the ledger v2's `tools/ledger/ledger_v2.py` and `frozen-v2.json`) are the same git
  blobs at the registration `c86940c1`, the kit `b42dc95c`, the data commit and this note's parent; from the registration to this note's
  parent, `tools/claims-v3/e189` changed by additions only, and `tools/ledger` and the ledger v2's data folder not at all. The scorer
  refuses unless the 8 frozen files of that list (all but its two self-test outputs) read OK, and its record reads
  `frozen_files_checked` 8 and `not_used` `[]` (no pass set aside); the whole list reads 10 of 10.
- **The interpreter:** `/usr/bin/python3` 3.12.3 on aifoundry2, isolated (`-I -B`); the history check's line names it. E189.md and
  KIT.md name 3.9 and 3.13 (README.md, Departures, 7).
- **Re-run since, at the desk, on the committed bytes** (desk checks of code; each JSON byte-equal to `scores-e189.json`, and each run's
  printed lines to `scores-e189.txt`): by `fix-e189d` in the lab clone at `fa9098c4` (21:11 PST); and by this lane (22:28 PST) from a
  fresh extract of `fa9098c4`'s own tree holding the four folders the scorer reads (`tools/claims-v3/e189`, `tools/ledger`,
  `docs/reports/data/2026-11-12-q166-ledger-v2` and this directory: 307 files, where `SHA256SUMS` read 228 of 228 and the registration's
  list 10 of 10), run as the runbook ran it, in the round's CPU slot with no device node reachable. The run wrote nothing into the
  extract.

## 3. The four rules' words, as the frozen scorer gives them

[`scores-e189.txt`](scores-e189.txt), verbatim (`scores-e189.json` > `verdict_of_the_day`):

```
{
 "E189-S1": "FAIL",
 "E189-S1T": "PASS",
 "E189-S2": "FAIL",
 "E189-S2T": "FAIL"
}
```

Behind the words (`scores-e189.json` > `rules`; the rules are E189.md 8.3's, registered; each configuration's error is e = the mean of
its passes' forecast / the mean of its passes' measured value - 1, and S2 alone reads the ratio mean t_k / point):

| rule | the scorer's words | scored | within | outside | word |
|---|---|---|---|---|---|
| **E189-S1** | score 1, given the measured seconds: J over idle a launch within 10% on at least 5 of the 6 configurations, and the rms of the six errors at most 10% | 6 | 3 | 3 | **FAIL** (rms 0.1322) |
| **E189-S1T** | score 1, given the measured seconds: J with the card at rest a launch within 5% on at least 5 of 6 | 6 | 6 | 0 | **PASS** |
| **E189-S2** | score 2, with the seconds forecast: the measured kernel seconds inside the frozen two-sided band and within 15% of the point, on at least 5 of 6 | 6 | 1 | 5 | **FAIL** |
| **E189-S2T** | score 2, with the seconds forecast: J with the card at rest a launch, at the forecast seconds and die, within 15% on at least 5 of 6 | 6 | 1 | 5 | **FAIL** |

Each configuration (`scores-e189.json` > `configs`; 4 passes each, every one valid by E189.md 8.2; the copy passes SHORT at 7 of their 8
launches, cut by the host's own budget, and scored on the launches they ran). Score 1, given the measured seconds:

| configuration | J over idle a launch (J), given / measured | error | within 10% (S1) | J with the card at rest a launch (J), given / measured | error | within 5% (S1T) |
|---|---|---|---|---|---|---|
| copy, zeros | 5.144 / 5.431 | -5.29% | yes | 26.533 / 26.747 | -0.80% | yes |
| copy, random | 6.814 / 7.468 | -8.76% | yes | 28.246 / 28.893 | -2.24% | yes |
| SHA-256 | 2.305 / 2.603 | -11.46% | no | 12.486 / 12.811 | -2.53% | yes |
| sort, sorted | 2.712 / 3.382 | -19.80% | no | 15.885 / 16.643 | -4.55% | yes |
| sort, shuffled | 3.290 / 4.125 | -20.23% | no | 19.684 / 20.495 | -3.95% | yes |
| sparse parity | 7.342 / 7.599 | -3.38% | yes | 19.525 / 19.900 | -1.88% | yes |

Score 2, with the seconds forecast (`e_t`, point / mean t_k - 1, is reported beside S2 and does not decide it):

| configuration | mean t_k / point (s) | ratio | frozen band (s) | inside it | S2 | J with the card at rest a launch at the forecast (J), forecast / measured | error | within 15% (S2T) | e_t |
|---|---|---|---|---|---|---|---|---|---|
| copy, zeros | 0.9071 / 0.6557 | 1.383 | 0.5568-0.7546 | no | no | 21.683 / 26.747 | -18.93% | no | -27.72% |
| copy, random | 0.9080 / 0.6557 | 1.385 | 0.5568-0.7546 | no | no | 23.416 / 28.893 | -18.96% | no | -27.79% |
| SHA-256 | 0.4316 / 0.5704 | 0.757 | 0.3849-0.9447 | yes | no | 16.610 / 12.811 | +29.66% | no | +32.15% |
| sort, sorted | 0.5593 / 0.7403 | 0.756 | 0.6009-1.0136 | no | no | 21.269 / 16.643 | +27.79% | no | +32.36% |
| sort, shuffled | 0.6942 / 0.8998 | 0.771 | 0.7151-1.2288 | no | no | 25.845 / 20.495 | +26.10% | no | +29.62% |
| sparse parity | 0.5131 / 0.5147 | 0.997 | 0.4633-0.6692 | yes | yes | 20.456 / 19.900 | +2.79% | yes | +0.31% |

The arms v2.1 and v2c (`scores-e189.json` > `arms`; registered arms, REPORTED: the day's verdict is the primary's): v2.1, S1 FAIL (3 of 6
within, rms 0.1356), S1T PASS (6 of 6), S2 FAIL (1 of 6), S2T FAIL (1 of 6); v2c, S1 FAIL (3 of 6 within, rms 0.1360), S1T PASS (6 of 6), S2
FAIL (1 of 6), S2T FAIL (1 of 6). In both arms the three errors of each of the other five configurations (copy, zeros; copy, random;
SHA-256; sort, sorted; sort, shuffled) equal the primary's; sparse parity's e_j_over reads -8.13% / -8.54% and its e_j_total -3.76% / -3.92%
(v2.1 / v2c), against the primary's -3.38% and -1.88%.

## 4. Beside verify-e189d's independent re-derivation

`verify-e189d` (Sat 14 Nov 2026, 20:37-20:59 PST) re-derived the four rules from this directory's committed raw files, taken from
`fa9098c4`, with its own code: the standard library only, importing nothing from the kit or the lab; `given()` written from E189.md 5.2
and the rules from 8.3, the frozen numbers read as data from `forecast-e189.json` (`c86940c1`) and the ledger v2's `frozen-v2.json`;
`/usr/bin/python3` 3.12.3. Its figures are a desk check of code. Each pair below is **the scorer / verify-e189d**, generated from
`scores-e189.json` and from the verifier's own output file, not typed.

| rule | scored | within | word | S1's rms |
|---|---|---|---|---|
| E189-S1 | 6 / 6 | 3 / 3 | FAIL / FAIL | 0.132195775 / 0.132195785 |
| E189-S1T | 6 / 6 | 6 / 6 | PASS / PASS |  |
| E189-S2 | 6 / 6 | 1 / 1 | FAIL / FAIL |  |
| E189-S2T | 6 / 6 | 1 / 1 | FAIL / FAIL |  |

| configuration | e_j_over (S1) | e_j_total (S1T) | mean t_k in s (S2) | e_j_total_forecast (S2T) | e_t | S1, S1T, S2, S2T |
|---|---|---|---|---|---|---|
| copy, zeros | -5.2919% / -5.2919% | -0.8009% / -0.8009% | 0.907076 / 0.907076 | -18.9342% / -18.9342% | -27.7181% / -27.7181% | yes yes no no / yes yes no no |
| copy, random | -8.7556% / -8.7556% | -2.2412% / -2.2412% | 0.908010 / 0.908010 | -18.9575% / -18.9575% | -27.7925% / -27.7925% | yes yes no no / yes yes no no |
| SHA-256 | -11.4595% / -11.4595% | -2.5326% / -2.5326% | 0.431621 / 0.431621 | +29.6612% / +29.6612% | +32.1457% / +32.1457% | no yes no no / no yes no no |
| sort, sorted | -19.7973% / -19.7973% | -4.5547% / -4.5547% | 0.559297 / 0.559297 | +27.7950% / +27.7950% | +32.3627% / +32.3627% | no yes no no / no yes no no |
| sort, shuffled | -20.2284% / -20.2284% | -3.9549% / -3.9549% | 0.694161 / 0.694161 | +26.1030% / +26.1030% | +29.6216% / +29.6216% | no yes no no / no yes no no |
| sparse parity | -3.3823% / -3.3823% | -1.8840% / -1.8840% | 0.513145 / 0.513145 | +2.7924% / +2.7924% | +0.3110% / +0.3110% | yes yes yes yes / yes yes yes yes |

**Agree or differ.** The four rules' words and counts are the same by both. Every figure above agrees to the digits shown; beneath them,
every one agrees to 1e-12 but two: sparse parity's e_j_over, -0.0338226800 / -0.0338229251, apart by 2.5e-07; sparse parity's e_j_total,
-0.0188397635 / -0.0188398605, apart by 9.7e-08. S1's rms reads 0.1321957750 / 0.1321957855, apart by 1.0e-08. Both numbers of each are
given here; none of them moves a word or a count. The verifier's largest differences over the six configurations, as its output gives them:
e_j_over 2.5e-07, e_j_total 9.7e-08, e_j_total_forecast 0, e_t 0, mean t_k 0.

**Two more of its readings** (desk checks of code): its own reduction of the raw telemetry, with no `energy.json` at all (an exact integral
of the board average and the before bracket; against `energy.json` at most 3.4e-05 apart on J over idle, 1.6e-05 on J with the card at rest
and 3.9e-06 on t_w, relative, with T0 equal), gives the same words and counts (S1 FAIL 3 of 6, S1T PASS 6 of 6, S2 FAIL 1 of 6, S2T FAIL 1
of 6; S1's rms 0.132212); and the arms v2.1 and v2c, re-derived, read the scorer's words and counts in all four rules, S1's rms 0.135594 /
0.135594 and 0.136013 / 0.136013 (the scorer / verify-e189d).

## 5. S1T's margin on the starting die (post hoc; note 1 § 6)

The verifier asked (its note 6) that S1T's margin be set beside S1T when `scores-e189.json` is committed; note 1 § 6 computed it with the
frozen scorer's own pass reader, `given()` and verdict count, and its output, [`posthoc-note1-e189.json`](posthoc-note1-e189.json) >
`s6_s1t_margin`, gives the figures below (generated from that file, not typed). **The registered word stands: S1T PASS, 6 of 6 within 5%,
at T0 as measured** (E189.md 5.2: `die_c.before`).

- **At T0 as measured:** every pass's T0 read 49-51 °C, below the footing law's 52-66 °C band, so `given()` priced the card at rest by the
  exponential law in all 24 passes, as registered.
- **Downward**, every pass's T0 moved by one uniform delta (post hoc): sort, sorted leaves the 5% band at -0.428 °C (5 of 6 still within:
  PASS); sort, shuffled at -0.997 °C, where S1T's word becomes FAIL (4 of 6 within at -1.0 °C); then SHA-256 at -2.423 °C; copy, random at
  -2.914 °C; sparse parity at -4.029 °C; copy, zeros at -4.197 °C.
- **Upward:** only copy, zeros leaves the band, at +4.772 °C, and S1T stays PASS through +5 °C.
- A reading beside the word, never the day's word.

## 6. Checks before the commit

- `scores-e189.json` and `scores-e189.txt` as staged are byte-equal to the card lane's RB_OUT file and to the runbook's capture of the
  scorer's call (`cmp`), and to both desk re-runs (§ 2).
- In a copy of this directory with the four new files: `SHA256SUMS` 228 of 228, `SHA256SUMS-note1` 6 of 6 and `SHA256SUMS-note2` 3 of 3
  entries OK; 239 files, every one in a list but `SHA256SUMS-note1` and `SHA256SUMS-note2`.
- The desk-path gate (`nopath_q142s.py`, v3.1, with the lab clone and the round's folders forbidden) read the four new files with 0 hits,
  and a login check found no home path, no login and no holder line in them or in this commit's subject and body.
- The public-text scan (the lab's `sanitize_extracts.py`, its fixed list and the box's local table, and the round's lists of private,
  vendor, access and mechanism words) found nothing in this note, `scores-e189.txt`, `SHA256SUMS-note2` or this commit's subject and body.
  In `scores-e189.json` it matched twice, both on one word of the round's desk-path list that the frozen scorer uses as its name for a card
  memory term in its 8.4 cross-check (`score_e189.py` lines 218-219, committed since the registration): a false match, kept as written,
  since the file is committed byte for byte.

## What does not change

Every reading, verdict, gate, stop and figure of `README.md`, note 1 and their files stands; this note adds the scorer's output beside
them and reads it, and changes nothing. The reducer, the scorer and the kit read none of this note's files. This lane reached no box,
opened no device and changed no committed file.

SPDX-License-Identifier: Apache-2.0
