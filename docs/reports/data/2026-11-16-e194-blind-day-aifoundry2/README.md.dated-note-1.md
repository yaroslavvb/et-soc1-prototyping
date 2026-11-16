# E194's data README, dated note 1 (Mon 16 Nov 2026): the frozen scorer's output, run on the data commit `72514ce5`, committed beside it - E194-S1 FAIL, E194-S1T FAIL, E194-S2 FAIL, E194-S2T FAIL; the data verifier's own re-derivation gives the same words and counts

*Beside [`README.md`](README.md), [`SHA256SUMS`](SHA256SUMS) and [`FILES.txt`](FILES.txt), which stay as committed in `72514ce5`. Written on
aifoundry2 from 01:22 PST on Mon 16 Nov 2026 (week 47) by the clock, desk only (no card, no lab box, no device, no post), by Q191's lane
`scores-e194`, after this directory's data verifier `verify-e194d` (01:02:27-01:21:36 PST: holds). The kit's step 13
([`KIT.md`](../../../../tools/claims-v3/e194/KIT.md), its table of steps: "`score_e194.py` (registered, unchanged) on the committed data;
RB_OUT/scores-e194.json; read the words"; [`rb/s24_score_e194.sh`](../../../../tools/claims-v3/e194/rb/s24_score_e194.sh)) runs the frozen
scorer only after the data commit and leaves its output to a later commit, and README.md's "Next" says the same; this lane is that later
lane. This note commits the output byte for byte, with the scorer's printed lines, sets the data verifier's figures beside the scorer's, and
answers the verifier's three findings in dated clauses (§ 5). **No number, rule, verdict, forecast, band, threshold or gate reading changes,
and nothing is scored again.** Interpreter: `/usr/bin/python3` 3.12.3 on aifoundry2. Labels: **registered** (E194.md, its note 1, A1 and the
kit as committed), **measured** (the session's committed files), **desk check of code** (the re-runs, this lane's readings of the committed
bytes and the verifier's figures), **REPORTED** (E194.md 6 and 8.4: beside the rules, deciding nothing), **post hoc** (desk readings after
the data). The verdicts are the frozen scorer's own output on the committed data.*

## 1. The new files

| file | what | bytes | sha256 |
|---|---|---|---|
| [`scores-e194.json`](scores-e194.json) | the frozen scorer's output ([`score_e194.py`](../../../../tools/claims-v3/e194/score_e194.py), registered in `b6ef1ad3`, unchanged), copied byte for byte from the card lane's RB_OUT: the rules E194-S1, S1T, S2 and S2T with their words, counts and verdicts; each configuration's errors, figures and flags, pass by pass; the arms v2.1 and v2c (reported); the readings of E194.md 6 (reported, not scored) | 41,733 | `38f5d232...` |
| [`scores-e194.txt`](scores-e194.txt) | the scorer's printed lines, copied byte for byte from the runbook's capture of that call (its stdout and stderr as they came), not rewritten | 85 | `663806d7...` |
| `README.md.dated-note-1.md` | this note | | |

[`SHA256SUMS-note1`](SHA256SUMS-note1) pins these three and `README.md`, `SHA256SUMS` and `FILES.txt` at their committed bytes. With
`SHA256SUMS` (257 files, unchanged), every file here is pinned but `SHA256SUMS-note1` itself.

## 2. When, where and on which commit the scorer ran

From the runbook's log (`runbook.log`) and its capture of each call, both kept outside the repository in the card lane's runbook folder
RB_OUT, and from the lab clone's own log of its HEAD:

- **Step 13, the frozen scorer** ([`rb/s24_score_e194.sh`](../../../../tools/claims-v3/e194/rb/s24_score_e194.sh), the kit's): Mon 16 Nov
  2026 at **00:58:43 PST**, on aifoundry2, in the lab clone with its HEAD at **`72514ce5`**, the data commit (made at 00:58:14 PST and
  pushed by 00:58:18), which was still the clone's HEAD when this note was built (01:37:41 PST).
- **Its gates**, the log's lines 97-100, at 00:58:42-00:58:43 PST, each with rc 0: the data directory committed (the last commit naming it:
  `72514ce5`); the directory clean (no line); `SHA256SUMS` 257 of 257 entries OK; the history check, `HISTORY OK` (991 files added since
  `46a16bd0` on E194's paths, none changed or removed; E194's registration `b6ef1ad3` and kit `f01e1cb2`, E191's registration `300d76e4`,
  note 1 `8c8f825f` and kit `eb1ac923`, and E189's registration `c86940c1` and kit `b42dc95c`: nothing under `tools/claims-v3/e194`, `e191`
  or `e189` changed since; nothing untracked; no shadowing addition or uncommitted file in the folders the day's Python puts first).
- **The scorer**, the log's line 101 (its last): `/usr/bin/python3 -I -B tools/claims-v3/e194/score_e194.py
  docs/reports/data/2026-11-16-e194-blind-day-aifoundry2 --out RB_OUT/scores-e194.json`, rc 0 in 0.1 s. `scores-e194.json` was last written
  at 00:58:43.340, the same instant as the runbook's capture of the scorer's printed lines (the step's fifth call). The step then printed
  its own last line, which the card lane's log of the step holds: `[s24_score_e194] scored:
  {"E194-S1":"FAIL","E194-S1T":"FAIL","E194-S2":"FAIL","E194-S2T":"FAIL"} (RB_OUT/scores-e194.json; the records lane commits it beside the
  data)`. `runbook.log` itself holds each call's line, not its output; the runbook's bounded runner (v3.1's `rb_run.py`) writes each call's
  stdout and stderr, as they come, to that call's capture file, and `scores-e194.txt` is the scorer's.
- **The scorer as registered:** `score_e194.py`, its list `SHA256SUMS-e194-registration` and the files it reads (`forecast_e194.py`,
  `forecast-e194.json`, `plan-e194.json`, `E194.md`, the ledger v2's `tools/ledger/ledger_v2.py` and `frozen-v2.json`) are the same git
  blobs at the registration `b6ef1ad3`, the kit `f01e1cb2`, A1 `04b6f022`, the data commit and the lab's HEAD when this note was built; from
  the registration to that HEAD, `tools/claims-v3/e194` changed by additions only, and `tools/ledger` and the ledger v2's data folder not at
  all. The scorer refuses unless the 15 frozen files of that list (all but its two self-test outputs) read OK, and its record reads
  `frozen_files_checked` 15 and `not_used` `[]`; the whole list reads 17 of 17.
- **The interpreter:** `/usr/bin/python3` 3.12.3 on aifoundry2, isolated (`-I -B`); the history check's line names it.
- **Re-run since, at the desk, on the committed bytes** (a desk check of code): by this lane (01:27 PST) from a fresh extract of
  `72514ce5`'s own tree holding the four folders the scorer reads (`tools/claims-v3/e194`, `tools/ledger`,
  `docs/reports/data/2026-11-12-q166-ledger-v2` and this directory: 374 files, where `SHA256SUMS` read 257 of 257 and the registration's
  list 17 of 17), run as the runbook ran it, in the round's CPU slot with no device node reachable: its JSON is byte-equal to
  `scores-e194.json` and its printed lines to `scores-e194.txt`, and it wrote nothing into the extract.

## 3. The four rules' words, as the frozen scorer gives them

[`scores-e194.txt`](scores-e194.txt), verbatim (`scores-e194.json` > `verdict_of_the_day`):

```
{
 "E194-S1": "FAIL",
 "E194-S1T": "FAIL",
 "E194-S2": "FAIL",
 "E194-S2T": "FAIL"
}
```

Behind the words (`scores-e194.json` > `rules`; the rules are E194.md 8.3's, registered; each configuration's error is e = the mean of its
passes' forecast / the mean of its passes' measured value - 1, and S2 alone reads the ratio mean t_k / point):

| rule | the scorer's words | scored | within | outside | word |
|---|---|---|---|---|---|
| **E194-S1** | score 1, given the measured seconds: J over idle a launch within 10% on at least 5 of the 6 configurations, and the rms of the six errors at most 10% | 6 | 0 | 6 | **FAIL** (rms 0.4527) |
| **E194-S1T** | score 1, given the measured seconds: J with the card at rest a launch within 5% on at least 5 of 6 | 6 | 0 | 6 | **FAIL** |
| **E194-S2** | score 2, with the seconds forecast: the measured kernel seconds inside the frozen two-sided band and within 15% of the point, on at least 5 of 6 | 6 | 1 | 5 | **FAIL** |
| **E194-S2T** | score 2, with the seconds forecast: J with the card at rest a launch, at the forecast seconds and die, within 15% on at least 5 of 6 | 6 | 3 | 3 | **FAIL** |

Each configuration (`scores-e194.json` > `configs`; 4 passes each, every one counted by E194.md 8.2; `not_used` is empty). Copy random's
four passes are SHORT, scored on the launches they ran, as E194.md 8.2 registers; the scorer's flags read "host ran 7 of 8 launches
(budget)" and "SHORT: the host's budget cut the burst short; scored on the launches it ran". Score 1, given the measured seconds:

| configuration | J over idle a launch (J), given / measured | error | within 10% (S1) | J with the card at rest a launch (J), given / measured | error | within 5% (S1T) |
|---|---|---|---|---|---|---|
| copy, zeros | 5.145 / 11.634 | -55.78% | no | 25.740 / 32.537 | -20.89% | no |
| copy, random | 6.928 / 13.803 | -49.81% | no | 27.570 / 34.719 | -20.59% | no |
| SHA-256 | 3.500 / 5.417 | -35.39% | no | 11.436 / 13.341 | -14.28% | no |
| sort, sorted | 3.823 / 7.216 | -47.02% | no | 14.020 / 17.442 | -19.62% | no |
| sort, shuffled | 4.677 / 8.733 | -46.45% | no | 17.093 / 21.311 | -19.79% | no |
| sparse parity | 8.769 / 13.071 | -32.91% | no | 18.113 / 22.586 | -19.80% | no |

Score 2, with the seconds forecast (`e_t`, point / mean t_k - 1, is reported beside S2 and does not decide it):

| configuration | mean t_k / point (s) | ratio | frozen band (s) | inside it | S2 | J with the card at rest a launch at the forecast (J), forecast / measured | error | within 15% (S2T) | e_t |
|---|---|---|---|---|---|---|---|---|---|
| copy, zeros | 0.9071 / 0.6557 | 1.383 | 0.5568-0.7546 | no | no | 21.271 / 32.537 | -34.63% | no | -27.72% |
| copy, random | 0.9060 / 0.6557 | 1.382 | 0.5568-0.7546 | no | no | 23.119 / 34.719 | -33.41% | no | -27.64% |
| SHA-256 | 0.3237 / 0.4277 | 0.757 | 0.2886-0.7133 | yes | no | 14.026 / 13.341 | +5.13% | yes | +32.13% |
| sort, sorted | 0.4195 / 0.5549 | 0.756 | 0.4505-0.7819 | no | no | 17.453 / 17.442 | +0.06% | yes | +32.29% |
| sort, shuffled | 0.5206 / 0.6745 | 0.772 | 0.5361-0.9434 | no | no | 21.244 / 21.311 | -0.31% | yes | +29.56% |
| sparse parity | 0.3848 / 0.3861 | 0.997 | 0.3474-0.5019 | yes | yes | 18.479 / 22.586 | -18.18% | no | +0.31% |

The arms v2.1 and v2c (`scores-e194.json` > `arms`; registered arms, REPORTED: the day's verdict is the primary's): v2.1, S1 FAIL (0 of 6
within, rms 0.4577), S1T FAIL (0 of 6), S2 FAIL (1 of 6), S2T FAIL (3 of 6); v2c, S1 FAIL (0 of 6 within, rms 0.4580), S1T FAIL (0 of 6), S2
FAIL (1 of 6), S2T FAIL (3 of 6). In both arms the three errors of each of the five plain configurations equal the primary's; sparse
parity's e_j_over reads -36.83% / -37.05%, its e_j_total -22.14% / -22.27% and its e_j_total_forecast -20.53% / -20.67% (v2.1 / v2c),
against the primary's -32.91%, -19.80% and -18.18%.

The readings of E194.md 6 (`scores-e194.json` > `readings_reported`, labelled there "REPORTED, never scored (E194.md section 6)"; each a
frozen J over idle a launch over the measured mean; they decide nothing):

| configuration | measured J over idle (J) | the primary, given the measured seconds | the same ledger at 600 MHz | E189 frozen (aifoundry3, 600 MHz) | E191 frozen (card 1, 600 MHz) | the primary + E136's base |
|---|---|---|---|---|---|---|
| copy, zeros | 11.634 | 5.145 (0.442) | 5.144 (0.442) | 5.144 (0.442) | 5.143 (0.442) | 12.547 (1.079) |
| copy, random | 13.803 | 6.928 (0.502) | 6.927 (0.502) | 6.814 (0.494) | 6.941 (0.503) | 14.329 (1.038) |
| SHA-256 | 5.417 | 3.500 (0.646) | 2.461 (0.454) | 2.305 (0.426) | 2.246 (0.415) | 6.318 (1.166) |
| sort, sorted | 7.216 | 3.823 (0.530) | 2.812 (0.390) | 2.712 (0.376) | 2.620 (0.363) | 7.457 (1.033) |
| sort, shuffled | 8.733 | 4.677 (0.536) | 3.412 (0.391) | 3.290 (0.377) | 3.183 (0.364) | 9.111 (1.043) |
| sparse parity | 13.071 | 8.769 (0.671) | 7.373 (0.564) | 7.346 (0.562) | 8.132 (0.622) | 12.075 (0.924) |

Each cell is the frozen J over idle a launch, with its ratio to the measured mean in brackets. The primary + E136's base reads 0.924-1.166
of the measured means; the other four columns read 0.363-0.671. Reported as the scorer gives them; no reading here is a verdict.

## 4. Beside verify-e194d's independent re-derivation

`verify-e194d` (Mon 16 Nov 2026, 01:02:27-01:21:36 PST) re-derived the four rules from this directory's committed raw files, extracted from
`72514ce5`, with its own code: importing nothing from the kit; E194.md 5.2's formulas written fresh; THE CLOCK RULE (8.2) from the pass
telemetry and the host's own launch times; the frozen points from `forecast-e194.json` at the registration `b6ef1ad3` (sha256 `6d2df791...`)
and aifoundry2's laws from the ledger v2's `frozen-v2.json` (the bytes the registration holds, the same blob at the data commit, § 2);
`/usr/bin/python3 3.12.3`. Its figures are a desk check of code. Each pair below is **the scorer / verify-e194d**, generated from
`scores-e194.json` and from the verifier's own output file (`rederive.json`), not typed.

| rule | scored | within | word | S1's rms |
|---|---|---|---|---|
| E194-S1 | 6 / 6 | 0 / 0 | FAIL / FAIL | 0.452697318 / 0.452697309 |
| E194-S1T | 6 / 6 | 0 / 0 | FAIL / FAIL |  |
| E194-S2 | 6 / 6 | 1 / 1 | FAIL / FAIL |  |
| E194-S2T | 6 / 6 | 3 / 3 | FAIL / FAIL |  |

| configuration | e_j_over (S1) | e_j_total (S1T) | mean t_k in s (S2) | e_j_total_forecast (S2T) | e_t | S1, S1T, S2, S2T |
|---|---|---|---|---|---|---|
| copy, zeros | -55.7761% / -55.7761% | -20.8893% / -20.8893% | 0.907074 / 0.907074 | -34.6254% / -34.6254% | -27.7179% / -27.7179% | no no no no / no no no no |
| copy, random | -49.8109% / -49.8109% | -20.5931% / -20.5931% | 0.906042 / 0.906042 | -33.4120% / -33.4120% | -27.6356% / -27.6356% | no no no no / no no no no |
| SHA-256 | -35.3895% / -35.3895% | -14.2762% / -14.2762% | 0.323719 / 0.323719 | +5.1346% / +5.1346% | +32.1335% / +32.1335% | no no no yes / no no no yes |
| sort, sorted | -47.0196% / -47.0196% | -19.6164% / -19.6164% | 0.419482 / 0.419482 | +0.0644% / +0.0644% | +32.2919% / +32.2919% | no no no yes / no no no yes |
| sort, shuffled | -46.4473% / -46.4473% | -19.7925% / -19.7925% | 0.520622 / 0.520622 | -0.3121% / -0.3121% | +29.5565% / +29.5565% | no no no yes / no no no yes |
| sparse parity | -32.9147% / -32.9147% | -19.8048% / -19.8048% | 0.384845 / 0.384845 | -18.1843% / -18.1843% | +0.3148% / +0.3148% | no no yes no / no no yes no |

**Agree or differ.** The four rules' words and counts are the same by both, in the primary and in both arms (v2.1 S1's rms 0.4577008 /
0.4577007, v2c 0.4579973 / 0.4579973). S1's rms differs by 9.0e-09. Over the six configurations the figures above differ by at most 7.4e-08
(e_j_over), 4.4e-08 (e_j_total), 0 (t_k_mean), 0 (e_j_total_forecast), 0 (e_t): the verifier's given values, written fresh from E194.md 5.2,
sit within 1.1e-07 of the frozen code's (relative), and the measured values, seconds, starting dies and points are equal. Over every figure
it compared, pass by pass and configuration by configuration, its largest relative difference is 3.6e-06, on `given_plus_e136` (the REPORTED
E136 reading, where it used E136's base as printed), and it lists 0 mismatches. Nothing differs that could move a word or a count.

**More of its readings** (desk checks of code, from its output files): THE CLOCK RULE's first half held in all 24 passes on 16-58 samples
after the climb, every one at 800 MHz, each count equal to the runner's live count; 24 of 24 passes count by 8.2, 4 SHORT (copy random).
Over the session's 9,309 samples the clock read 600, 700 and 800 MHz 8,208, 47 and 1,054 times; `since_reset_ms` was -1 in every one; the
board's highest reading was 64.59 W (none at or above 65 W), the die's 55 C and the latch's 58 C. The config read 65 W / 65 C / low_power /
600 MHz / 519 mV at both ends; of 61 commands none carries a set, reset, management-service, power-top, PMIC, flash or governor word. Card
time 932.25 s = 15.54 card-minutes (cap 110); the session sits inside the window (G 00:03:59, last start 01:34, last end 03:34).
`SHA256SUMS` 257 of 257 OK; the session's `MANIFEST.sha256` 207 of 207 on the copy-back and 207 of 207 on the box's own session folder; no
home path and no login in any file.

## 5. The verifier's three findings, answered (dated clauses, Mon 16 Nov 2026, PST)

### 5.1 Finding 1 (low): copy random's 7 of 8 launches

**The verifier's reading** (a desk check of code, from its `sessionchecks.json`): the ledger host stops launching once the time left in its
budget is less than its model's seconds plus 0.5 s; with the copy's model of 1.5032 s (each copy random pass's committed `host-raw.json`
reads `model_s` 1.5032, `launches` 7, `status` FAIL, and its `host.err` reads "budget spent before launch 7", the eighth counting from 0),
launch 8 had to begin by 7.4968 s after the host's start. Copy random's host took 1.181-1.198 s to its first launch and its seven launches
ended at 7.532-7.551 s, 0.035-0.054 s past that point; copy zeros took 1.074-1.114 s to its first and ran all 8. The launches themselves
took 0.9064-0.9072 s each in both copies. So the shortfall is the host's budget, by tens of milliseconds, not the clock (THE CLOCK RULE held
in all four passes, § 4 and § 5.2).

**Answered, Mon 16 Nov 2026:** read and accepted as the reason. It changes nothing in E194: E194.md 8.2 registers that "A burst the host's
budget cut short is scored on the launches it ran and flagged SHORT", and the frozen scorer did exactly that (§ 3; the four passes count,
none is set aside). The verifier's advice stands for later runs, not for this one: a kit that runs these copies at K = 8 under a governor's
800 MHz should expect SHORT, or register K = 7, before any datum.

### 5.2 Finding 2 (low): THE CLOCK RULE's second half, pass by pass

**The verifier's finding:** the rule's second half (E194.md 8.2: "the burst's last launch ran at 800 MHz by its own count: its slowest
minion's cycles over its wall seconds read 780-810 MHz") is recorded per pass in no committed file, and not in `scores-e194.json`, where
only `not_used` `[]` implies it.

**Answered, Mon 16 Nov 2026: the 24 values, now committed here.** This lane read each pass with the frozen scorer's own functions
(`last_json()`, `clock_rule()` and `read_pass()` of `score_e194.py`, imported unchanged from the extract of `72514ce5`; the ledger programs'
cycles from `host-raw.json` > `hart0_cycles` > `max`, sparse parity's from `host.json` > `kernel` > `cycles_max`, the seconds from
`host.json` > `launch_s`, its last entry; the clock = cycles / seconds / 1e6, `clock_rule()`'s own expression), under `/usr/bin/python3
3.12.3`, in the round's CPU slot with no device node reachable. `clock_rule()` returned no reason and `read_pass()` a record in all 24.
Every clock lies in 780-810 MHz: 799.00-799.72 MHz. The verifier's own code gives the same 24 floats (the difference is 0 in every pass). A
desk check of code; the scorer's verdicts do not change.

| configuration | pass | launches | the last launch: slowest minion's cycles | its wall seconds | its clock (MHz), the scorer's functions / verify-e194d |
|---|---|---|---|---|---|
| copy, zeros | p1 | 8 | 725,851,930 | 0.907800 | 799.5725 / 799.5725 |
| copy, zeros | p2 | 8 | 725,398,941 | 0.907200 | 799.6020 / 799.6020 |
| copy, zeros | p3 | 8 | 725,319,159 | 0.907000 | 799.6904 / 799.6904 |
| copy, zeros | p4 | 8 | 726,065,435 | 0.907900 | 799.7196 / 799.7196 |
| copy, random | p1 | 7 | 725,223,866 | 0.906900 | 799.6735 / 799.6735 |
| copy, random | p2 | 7 | 723,887,461 | 0.905400 | 799.5223 / 799.5223 |
| copy, random | p3 | 7 | 724,257,509 | 0.905800 | 799.5777 / 799.5777 |
| copy, random | p4 | 7 | 725,964,670 | 0.907800 | 799.6967 / 799.6967 |
| SHA-256 | p1 | 9 | 258,974,534 | 0.324100 | 799.0575 / 799.0575 |
| SHA-256 | p2 | 9 | 258,974,975 | 0.324100 | 799.0589 / 799.0589 |
| SHA-256 | p3 | 9 | 258,975,976 | 0.324000 | 799.3086 / 799.3086 |
| SHA-256 | p4 | 9 | 258,974,427 | 0.324100 | 799.0572 / 799.0572 |
| sort, sorted | p1 | 8 | 335,583,295 | 0.419900 | 799.1981 / 799.1981 |
| sort, sorted | p2 | 8 | 335,595,001 | 0.419800 | 799.4164 / 799.4164 |
| sort, sorted | p3 | 8 | 335,588,034 | 0.419900 | 799.2094 / 799.2094 |
| sort, sorted | p4 | 8 | 335,576,289 | 0.419800 | 799.3718 / 799.3718 |
| sort, shuffled | p1 | 7 | 416,495,155 | 0.521000 | 799.4149 / 799.4149 |
| sort, shuffled | p2 | 7 | 416,497,885 | 0.521000 | 799.4201 / 799.4201 |
| sort, shuffled | p3 | 7 | 416,496,236 | 0.521000 | 799.4170 / 799.4170 |
| sort, shuffled | p4 | 7 | 416,501,991 | 0.521000 | 799.4280 / 799.4280 |
| sparse parity | p1 | 9 | 307,608,203 | 0.384889 | 799.2128 / 799.2128 |
| sparse parity | p2 | 9 | 307,860,996 | 0.385162 | 799.3026 / 799.3026 |
| sparse parity | p3 | 9 | 308,157,340 | 0.385598 | 799.1674 / 799.1674 |
| sparse parity | p4 | 9 | 307,876,140 | 0.385325 | 799.0038 / 799.0038 |

### 5.3 Finding 3 (nit): the idle anchors' sample counts

**The verifier's finding:** `README.md` (line 34, "What ran", the clock) says "all 1,198 samples of each idle anchor", but one anchor holds
1,199.

**Answered, Mon 16 Nov 2026 (a correction, in this note's words; `README.md` stays as committed):** anchors 1 and 3 hold 1,198 samples each
and anchor 2 holds 1,199, under each of three boundary conventions (t0 <= t <= t1, t0 <= t < t1 and t0 < t <= t1, on
`session/anchors.json`'s windows over `session/telemetry.jsonl.gz`); every sample of all three anchors reads 600 MHz either way. A post hoc
desk count by this lane, equal to the verifier's; it decides nothing, and no figure or verdict rests on it.

## 6. Checks before the commit

- `scores-e194.json` and `scores-e194.txt` as staged are byte-equal to the card lane's RB_OUT file and to the runbook's capture of the
  scorer's call (`cmp`), and to this lane's desk re-run (§ 2); the card lane's log of the step holds the same printed lines once.
- In a copy of this directory with the four new files: `SHA256SUMS` 257 of 257 and `SHA256SUMS-note1` 6 of 6 entries OK; 264 files, every
  one in a list but `SHA256SUMS-note1`.
- The desk-path gate (`nopath_q142s.py`, v3.1, with the lab clone and the round's folders forbidden) read the four new files with 0 hits,
  and a login check found no home path, no login and no holder line in them or in this commit's subject and body.
- The public-text scan (the lab's `sanitize_extracts.py`, its fixed list and the box's local table, and the round's lists of private,
  vendor, access and mechanism words) found nothing in this note, `scores-e194.txt`, `SHA256SUMS-note1` or this commit's subject and body.
  In `scores-e194.json` it matched twice, both on one word of the round's desk-path list that the frozen scorer uses as its key and its text
  for a card memory term in sparse parity's rail cross-check (`score_e194.py` lines 278-280, committed in the registration): a false match,
  kept as written, since the file is committed byte for byte.
- The commit holds these four files and nothing else.

## What does not change

Every reading, verdict, gate, stop and figure of `README.md` and its files stands, except the one count § 5.3 corrects in this note's words
(`README.md` itself stays as committed); this note adds the scorer's output beside them and reads it, and changes nothing. The reducer, the
scorer and the kit read none of this note's files. This lane reached no box, opened no device and changed no committed file.

SPDX-License-Identifier: Apache-2.0
