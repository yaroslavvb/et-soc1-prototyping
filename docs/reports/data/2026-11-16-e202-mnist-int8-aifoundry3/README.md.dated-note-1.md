# E202's data README, dated note 1 (Mon 16 Nov 2026): the frozen scorer's output and the ledger v3 note's REPORTED readings, run on the data commit `ec9c9fe8`, committed beside it - E202-S1 FAIL, E202-S1T PASS, E202-S2 FAIL, E202-S2T FAIL, E202-S3 PASS; the data verifier's own re-derivation gives the same words

*Beside [`README.md`](README.md) and [`SHA256SUMS`](SHA256SUMS), which stay as committed in `ec9c9fe8`. Written on aifoundry2 from 13:09 PST
on Mon 16 Nov 2026 (week 47) by the clock, desk only (no card, no lab box, no device, no post), by Q198's lane `scores-e202`, after this
directory's data verifier `verify-e202d` (12:44:48-13:08:32 PST: holds). The kit's step 13
([`CARD-LANE-BRIEF.md`](../../../../tools/claims-v3/e202/CARD-LANE-BRIEF.md), its table of steps: "the frozen scorer:
RB_OUT/scores-e202.json and its printed words (E202-S1, S1T, S2, S2T, S3: PASS, FAIL or NO DATA); then the ledger v3 note's REPORTED
readings, RB_OUT/v3-scores-e202.json (fix-e202: S2T-v3, never a verdict); the records lane commits both beside the data";
[`rb/s24_score_e202.sh`](../../../../tools/claims-v3/e202/rb/s24_score_e202.sh)) runs the frozen scorer and then the ledger v3 note only
after the data commit and leaves their output to a later commit;
[`DATA-README-FORM-e202.md`](../../../../tools/claims-v3/e202/DATA-README-FORM-e202.md) says "The scorer runs after the data commit (step
13): its words are not in this README at the commit; the records lane adds them in a dated note beside it", and README.md says "a later lane
commits its words beside it". This lane is that later lane. This note commits both outputs byte for byte, with their printed lines, sets the
data verifier's figures beside the scorer's, and answers the card lane's and the data verifier's findings in dated clauses (section 6). **No
number, rule, verdict, forecast, band, threshold or gate reading changes, and nothing is scored again.** Interpreter: `/usr/bin/python3`
3.12.3 on aifoundry2. Labels: **registered** ([`E202.md`](../../../../tools/claims-v3/e202/E202.md), its ledger v3 note
[`E202-ledger-v3-note.md`](../../../../tools/claims-v3/e202/E202-ledger-v3-note.md) and the kit, as committed), **measured** (the session's
committed files), **desk check of code** (the re-runs, this lane's readings of the committed bytes and the verifier's figures), **REPORTED**
(E202.md 7.3 and the v3 note: beside the rules, deciding nothing), **post hoc** (desk readings after the data). The verdicts are the frozen
scorer's own output on the committed data. Every number below is against the card's own meter, whose absolute scale is one fixed gain for
every board (README.md, "The meter's absolute scale").*

## 1. The new files

| file | what | bytes | sha256 |
|---|---|---|---|
| [`scores-e202.json`](scores-e202.json) | the frozen scorer's output ([`score_e202.py`](../../../../tools/claims-v3/e202/score_e202.py), registered in `68abdd97`, unchanged), copied byte for byte from the card lane's RB_OUT: the gate E202-R0, the rules E202-S1, S1T, S2, S2T and S3 with their words, counts and verdicts; each scored configuration's errors, figures and flags, burst by burst; per image and per issued multiply-add; the dram pair and the arms v2.1 and epi-only (REPORTED) | 13,326 | `0073a712...` |
| [`scores-e202.txt`](scores-e202.txt) | the scorer's printed lines, copied byte for byte from the runbook's capture of that call (its stdout and stderr as they came), not rewritten | 105 | `9ef98177...` |
| [`v3-scores-e202.json`](v3-scores-e202.json) | the ledger v3 note's readings ([`v3note_e202.py`](../../../../tools/claims-v3/e202/v3note_e202.py) `--score`, committed in the kit `ad0a1427`, unchanged), copied byte for byte from RB_OUT: S2T-v3 for each configuration, and S1, S1T and S2 through v3's route (equal to v2's by construction); REPORTED, never a verdict | 2,148 | `c0f24b47...` |
| [`v3-scores-e202.txt`](v3-scores-e202.txt) | the v3 note's printed lines, copied byte for byte from the runbook's capture of that call (the file's text and the newline its print adds) | 2,149 | `1736f77b...` |
| `README.md.dated-note-1.md` | this note | | |

[`SHA256SUMS-note1`](SHA256SUMS-note1) pins these five and `README.md` and `SHA256SUMS` at their committed bytes. With `SHA256SUMS` (145
files, unchanged), every file here is pinned but `SHA256SUMS-note1` itself.

## 2. When, where and on which commit the scorer ran

From the runbook's log (`runbook.log`) and its capture of each call, both kept outside the repository in the card lane's runbook folder
RB_OUT, and from the lab clone's own log of its HEAD (a desk check of code: this lane's provenance check, 46 checks, all OK):

- **Step 13** ([`rb/s24_score_e202.sh`](../../../../tools/claims-v3/e202/rb/s24_score_e202.sh), the kit's): Mon 16 Nov 2026 at
  **12:41:20-12:41:21 PST**, on aifoundry2, in the lab clone with its HEAD at **`ec9c9fe8`**, the data commit (made at 12:40:49 PST and
  pushed by 12:40:54, the card lane's log), which was still the clone's HEAD, with nothing moved since, when this note was built (13:29:12
  PST).
- **Its gates**, the log's lines 80-83, at 12:41:20 PST, each with rc 0: the data directory committed (the last commit naming it:
  `ec9c9fe8`); the directory clean (no line); `SHA256SUMS` 145 of 145 entries OK; the history check: `HISTORY OK: 65 files added since the
  program commit 4a7b48b1 on E202's paths, none changed or removed, workloads/mnistmlp unchanged; the registration 68abdd97fb76; the kit
  ad0a14273790: nothing under tools/claims-v3/e202 changed since; nothing untracked; no shadowing addition or uncommitted file in the 8
  folders the day's Python puts first (16 module files added there since 4a7b48b1, 0 uncommitted) (329 names: sys.stdlib_module_names
  (Python 3.12.3), and the day's own)`
- **The scorer**, the log's line 84: `/usr/bin/python3 -I -B tools/claims-v3/e202/score_e202.py
  docs/reports/data/2026-11-16-e202-mnist-int8-aifoundry3 --out RB_OUT/scores-e202.json`, rc 0 in 0.2 s. `scores-e202.json` was last written
  at 12:41:20.894, while that call ran (its capture closed at 12:41:20.897).
- **The ledger v3 note**, the log's line 85 (its last of 85): `/usr/bin/python3 -I -B tools/claims-v3/e202/v3note_e202.py --score
  docs/reports/data/2026-11-16-e202-mnist-int8-aifoundry3 --out RB_OUT/v3-scores-e202.json`, rc 0 in 0.3 s. `v3-scores-e202.json` was last
  written at 12:41:21.172 (its capture closed at 12:41:21.175).
- The step then printed its own last line, which the card lane's log of the step holds: `[s24_score_e202] scored:
  {"E202-S1":"FAIL","E202-S1T":"PASS","E202-S2":"FAIL","E202-S2T":"FAIL","E202-S3":"PASS"} (RB_OUT/scores-e202.json; the v3 note's REPORTED
  readings in RB_OUT/v3-scores-e202.json; the records lane commits both beside the data)`. `runbook.log` holds each call's line, not its
  output; the runbook's bounded runner (v3.1's `rb_run.py`) writes each call's stdout and stderr, as they come, to that call's capture file,
  and writes the call's log line when it ends: `scores-e202.txt` and `v3-scores-e202.txt` are the captures of the step's fifth and sixth
  calls. No earlier line of the log runs the scorer on data or the v3 note's `--score` (the scorer's stand-in self-test is line 25, the v3
  note's `--check` line 40).
- **The scorer as registered:** `score_e202.py`, its list `SHA256SUMS-e202-registration` (12 files) and what it reads (`forecast_e202.py`,
  `forecast-e202.json` and the forecast's 14 inputs named by sha256 in `forecast-e202.json` > `inputs_sha256`) are the same git blobs at the
  registration `68abdd97`, the kit `ad0a1427`, the data commit and the lab's HEAD when this note was built; the v3 note's files and the
  step's own scripts are the same blobs at the kit, the data commit and HEAD, and ledger v3's `tools/ledger/ledger_v3.py` and
  `frozen-v3.json` at its landing `50795847` as well. From the registration to that HEAD, `tools/claims-v3/e202` changed by additions only
  (the kit's), and not at all since the kit; `tools/ledger` not at all. The scorer refuses unless the 11 frozen files of its list (all but
  the self-test stub) read OK and `forecast_e202.py` recomputes `forecast-e202.json` to the byte; its record reads `frozen_files_checked` 11
  and `not_used` `[]`. The registration's list reads 12 of 12 and the kit's 50 of 50 in the lab clone now.
- **The interpreter:** `/usr/bin/python3` 3.12.3 on aifoundry2, isolated (`-I -B`); the history check's line names it, and
  `v3-scores-e202.json` > `interpreter` reads "/usr/bin/python3 3.12.3 wrote the files (named)".
- **Re-run since, at the desk, on the committed bytes** (a desk check of code): by this lane (13:17:47 PST) from a fresh extract of
  `ec9c9fe8`'s own tree holding the folders the two programs read (447 files: `tools/claims-v3/e202`, `tools/ledger`, `tools/counter`,
  `workloads/ledger`, `workloads/nocroute`, `workloads/sparseparity/tools`, the four data folders the forecast's inputs name, and this
  directory; `SHA256SUMS` 145 of 145, the registration's list 12 of 12 and the kit's 50 of 50 there), each run as the runbook ran it, in the
  round's CPU slot with no device node reachable: both JSON files came out byte-equal to the two committed here and both printed outputs to
  the two `.txt` files, and the runs wrote nothing into the extract.

## 3. The five rules' words, as the frozen scorer gives them

[`scores-e202.txt`](scores-e202.txt), verbatim (`scores-e202.json` > `verdict_of_the_day`):

```
{
 "E202-S1": "FAIL",
 "E202-S1T": "PASS",
 "E202-S2": "FAIL",
 "E202-S2T": "FAIL",
 "E202-S3": "PASS"
}
```

**The gate (E202-R0, E202.md 7.2):** "the scp pair's smokes passed: the scp pair is scored" (`scores-e202.json` > `gate`). Each smoke arm's
host result, as the scorer read it:

| arm | status | core | logits | tensor_error | on-card test accuracy |
|---|---|---|---|---|---|
| T-scp | PASS | PASS | PASS | 0 |  |
| Z-scp | PASS | PASS | PASS | 0 |  |
| T-dram | PASS | PASS | PASS | 0 |  |
| Z-dram | PASS | PASS | PASS | 0 |  |
| ACC | PASS | PASS | NOT CHECKED | 0 | 9,849 / 10,000 = 98.49% |

Behind the words (`scores-e202.json` > `rules`; the rules are E202.md 7.3's, registered; for each scored configuration, e = the mean over
its bursts of the forecast / the mean over its bursts of the measured value - 1; S3 reads the mean measured kernel seconds a pass against
the frozen point and band):

| rule | the scorer's words | scored | within | word |
|---|---|---|---|---|
| **E202-S1** | score 1, given the measured seconds: J over idle a pass within 10% (forecast / measured - 1), each scored configuration | 2 | 0 | **FAIL** |
| **E202-S1T** | score 1, given the measured seconds: J with the card at rest a pass within 10%, each scored configuration | 2 | 2 | **PASS** |
| **E202-S2** | score 2, with the seconds forecast too: J over idle a pass at the frozen point within 15%, each scored configuration | 2 | 0 | **FAIL** |
| **E202-S2T** | score 2, with the seconds forecast too: J with the card at rest a pass at the frozen point (the forecast seconds and die) within 15%, each scored configuration | 2 | 0 | **FAIL** |
| **E202-S3** | the seconds as their own score: the mean measured kernel seconds a pass inside the frozen two-sided band and within 15% of the point (0.85 <= mean / point <= 1.15), each scored configuration | 2 | 2 | **PASS** |

S1T's "within 5%" (REPORTED beside it, E202.md 7.3): no (trained-scp) and no (random-scp). Every burst counts (E202.md 7.2): 4 of 4 in each
scored configuration, all at R = 96; `not_used` is empty. Read S1T's PASS with section 6.1.

**Both scores, both numbers, a pass** (`scores-e202.json` > `configs`; J a pass; measured: the means of the four bursts; score 1: the frozen
model given each burst's measured seconds and starting die; score 2: the frozen point, at its own seconds and die):

| configuration | number, a pass | measured | score 1: given the measured seconds | e | rule (threshold): within | score 2: the frozen point | e | rule (threshold): within |
|---|---|---|---|---|---|---|---|---|
| trained-scp | J over idle | 0.39524 | 0.49204 | +24.49% | S1 (10%): no | 0.49419 | +25.04% | S2 (15%): no |
| trained-scp | J with the card at rest | 1.12130 | 1.19916 | +6.94% | S1T (10%): yes | 1.29204 | +15.23% | S2T (15%): no |
| random-scp | J over idle | 0.39818 | 0.50975 | +28.02% | S1 (10%): no | 0.51190 | +28.56% | S2 (15%): no |
| random-scp | J with the card at rest | 1.12863 | 1.21507 | +7.66% | S1T (10%): yes | 1.31042 | +16.11% | S2T (15%): no |

**Both scores, both numbers, an image** (a pass is 60,000 images: the training split, `forecast-e202.json` > `per_pass_units`; the measured
figures are the scorer's own `per_image`; the forecasts an image are the figures above / 60,000, desk arithmetic, and the frozen point's
equal `forecast-e202.json` > `per_image`; each e is the same as a pass's):

| configuration | number, an image | measured | score 1: given the measured seconds | score 2: the frozen point |
|---|---|---|---|---|
| trained-scp | uJ over idle | 6.5873 | 8.2007 | 8.2366 |
| trained-scp | uJ with the card at rest | 18.688 | 19.986 | 21.534 |
| trained-scp | kernel microseconds | 0.4907 | (given: the measured) | 0.5209 |
| random-scp | uJ over idle | 6.6363 | 8.4958 | 8.5317 |
| random-scp | uJ with the card at rest | 18.810 | 20.251 | 21.840 |
| random-scp | kernel microseconds | 0.4907 | (given: the measured) | 0.5209 |

**The seconds as their own score (E202-S3)** (`t_k_pass_mean`: the slowest minion's cycles a launch / 600 MHz / R, the mean of four bursts;
the frozen point and band at R = 96):

| configuration | mean measured kernel ms a pass | frozen point (ms) | measured / point | frozen band (ms) | inside it | within 15% (0.85-1.15) | S3 |
|---|---|---|---|---|---|---|---|
| trained-scp | 29.4437 | 31.2551 | 0.9420 | 23.606-47.756 | yes | yes | yes |
| random-scp | 29.4406 | 31.2551 | 0.9419 | 23.606-47.756 | yes | yes | yes |

**Burst by burst** (`scores-e202.json` > `configs` > `per_burst`; J a pass; e = given / measured - 1 for the burst; t_w the wall seconds of
the launch / R):

| configuration | burst | R | T0 (C) | J over idle: measured | given | e | J at rest: measured | given | e | t_k a pass (ms) | t_w a pass (ms) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| trained-scp | 1 | 96 | 50 | 0.40276 | 0.49204 | +22.17% | 1.11852 | 1.19202 | +6.57% | 29.4433 | 29.4481 |
| trained-scp | 2 | 96 | 51 | 0.40283 | 0.49204 | +22.15% | 1.12645 | 1.20154 | +6.67% | 29.4442 | 29.4481 |
| trained-scp | 3 | 96 | 51 | 0.39807 | 0.49204 | +23.60% | 1.12580 | 1.20154 | +6.73% | 29.4429 | 29.4481 |
| trained-scp | 4 | 96 | 51 | 0.37729 | 0.49204 | +30.41% | 1.11441 | 1.20154 | +7.82% | 29.4442 | 29.4481 |
| random-scp | 1 | 96 | 50 | 0.39820 | 0.50974 | +28.01% | 1.12282 | 1.21037 | +7.80% | 29.4395 | 29.4481 |
| random-scp | 2 | 96 | 50 | 0.39279 | 0.50974 | +29.78% | 1.12176 | 1.21012 | +7.88% | 29.4387 | 29.4373 |
| random-scp | 3 | 96 | 51 | 0.40516 | 0.50975 | +25.81% | 1.13770 | 1.21990 | +7.23% | 29.4416 | 29.4481 |
| random-scp | 4 | 96 | 51 | 0.39658 | 0.50975 | +28.54% | 1.13224 | 1.21990 | +7.74% | 29.4425 | 29.4481 |

**More of what E202.md 7.3 reports** (REPORTED, never a verdict): the spread of the bursts' S1 errors (`e_j_over_burst_sd`) 0.0395
(trained-scp) and 0.0165 (random-scp). The frozen two-sided bands (`forecast-e202.json`): the measured J over idle a pass lies outside its
band, below it, in both configurations (0.39524 against 0.40409-0.64267; 0.39818 against 0.42023-0.65324), and the measured J with the card
at rest inside its band in both (1.12130 in 0.96780-1.99958; 1.12863 in 0.98426-2.01115). Per issued multiply-add (669,204,480,000 a pass,
`forecast-e202.json` > `per_pass_units`), measured over idle / at rest: 0.5906 / 1.6756 pJ (trained-scp) and 0.5950 / 1.6865 pJ
(random-scp); the frozen point's 0.7385 / 1.9307 and 0.7649 / 1.9582 pJ. The scored bursts' starting die T0 (`energy.json` > `die_c` >
`before`, the mean over the before bracket) reads 50-51 C, and the runner's die at each start (`burst.json` > `die_start_c`) 49-51 C: below
the forecast's band of 52-60 C (frozen point 55 C); E202.md 8: "below 52 C does not block (scored given its own T0, labelled so)". Every
burst carries one flag of the reducer's, quoted: "the host has no host_cpu_s: its share uses the whole process's CPU time (an upper bound)".

**The dram pair** (`scores-e202.json` > `reported`: REPORTED, never a verdict, since the scp pair is scored; two bursts each):

| configuration | bursts | J over idle, given the seconds: e | J at rest, given the seconds: e | J over idle, frozen point: e | J at rest, frozen point: e | measured / point seconds |
|---|---|---|---|---|---|---|
| trained-dram | 2 | +25.77% | +7.15% | +26.27% | +14.14% | 0.9470 |
| random-dram | 2 | +25.11% | +7.25% | +25.59% | +14.14% | 0.9470 |

**The arms** (`arms_reported`, E202.md 7.3: REPORTED), J over idle given the measured seconds, e: v2.1 +15.62% (trained-scp) and +19.21%
(random-scp); epi-only +22.12% and +25.66%; the primary's are +24.49% and +28.02%.

## 4. The ledger v3 note's readings (REPORTED, never a verdict)

[`v3-scores-e202.json`](v3-scores-e202.json) > `configs` (its `what`: "E202's ledger v3 readings (v3note_e202.py --score), REPORTED, never a
verdict; the verdicts are score_e202.py's (v2)"; the note, frozen before any datum, is
[`E202-ledger-v3-note.md`](../../../../tools/claims-v3/e202/E202-ledger-v3-note.md); its gate reads "the scp pair's smokes passed: the scp
pair is scored"). S2T-v3 is J with the card at rest a pass at ledger v3's point against the same measured mean; S1, S1T and S2 through v3's
route are v2's by construction:

| configuration | bursts | the scored pair | S2T-v3: e | within 15% | S1 through v3 (= v2's) | S1T through v3 (= v2's) | S2 through v3 (= v2's) |
|---|---|---|---|---|---|---|---|
| trained-scp | 4 | yes | +10.27% | yes | +24.49% | +6.94% | +25.04% |
| random-scp | 4 | yes | +11.18% | yes | +28.02% | +7.66% | +28.56% |
| trained-dram | 2 | no | +9.24% | yes | +25.77% | +7.15% | +26.27% |
| random-dram | 2 | no | +9.31% | yes | +25.11% | +7.25% | +25.59% |

S1, S1T and S2 through v3's route equal the scorer's to 9.5e-07 or less (the v3 note rounds to six significant figures). Ledger v3's S2T
reads +10.3% and +11.2% on the scored pair, against v2's +15.2% and +16.1% (E202-S2T, the verdict).

## 5. Beside verify-e202d's independent re-derivation

`verify-e202d` (Mon 16 Nov 2026, 12:44:48-13:08:32 PST) re-derived the five rules from this directory's committed raw files with its own
code: importing nothing from the kit; its own reduction of every burst from the committed telemetry, the window from the host's own launch
times; E202.md 6's given-seconds formula written fresh from E202.md 6 and the ledger v2's formulas; the frozen forecasts read as data
(`forecast-e202.json`, sha256 `d1dc7679...`, and the ledger v2's `frozen-v2.json`); `/usr/bin/python3` 3.12.3. Its figures are a desk check
of code. Each pair below is **the scorer / verify-e202d**, generated from `scores-e202.json` and `v3-scores-e202.json` and from the
verifier's own output file (`score.json`), not typed.

| rule | word, the scorer / verify-e202d |
|---|---|
| E202-S1 | FAIL / FAIL |
| E202-S1T | PASS / PASS |
| E202-S2 | FAIL / FAIL |
| E202-S2T | FAIL / FAIL |
| E202-S3 | PASS / PASS |
| E202-R0 (the scored pair) | scp / scp |

| configuration | S1: e_j_over | S1T: e_j_total | S2: e_j_over_forecast | S2T: e_j_total_forecast | S3: measured / point | S2T-v3 (REPORTED) |
|---|---|---|---|---|---|---|
| trained-scp | +24.4916% / +24.4915% | +6.9438% / +6.9437% | +25.0370% / +25.0370% | +15.2271% / +15.2272% | 0.94204 / 0.94204 | +10.272% / +10.272% |
| random-scp | +28.0193% / +28.0192% | +7.6594% / +7.6593% | +28.5615% / +28.5616% | +16.1073% / +16.1074% | 0.94195 / 0.94194 | +11.182% / +11.182% |
| trained-dram (REPORTED) | +25.7720% / +25.7719% | +7.1523% / +7.1523% | +26.2722% / +26.2721% | +14.1369% / +14.1368% | 0.94699 / 0.94699 | +9.242% / +9.242% |
| random-dram (REPORTED) | +25.1095% / +25.1095% | +7.2486% / +7.2486% | +25.5902% / +25.5903% | +14.1397% / +14.1394% | 0.94696 / 0.94696 | +9.311% / +9.311% |

| configuration | measured J over idle a pass | measured J at rest a pass | given J over idle | given J at rest | uJ over idle an image | pJ over idle an issued multiply-add |
|---|---|---|---|---|---|---|
| trained-scp | 0.395239 / 0.395239 | 1.121298 / 1.121298 | 0.492039 / 0.492039 | 1.199158 / 1.199158 | 6.58731 / 6.58731 | 0.59061 / 0.59061 |
| random-scp | 0.398179 / 0.398179 | 1.128628 / 1.128628 | 0.509746 / 0.509745 | 1.215073 / 1.215073 | 6.63631 / 6.63631 | 0.59500 / 0.59500 |

**Agree or differ.** The five words and the gate are the same by both. Over every error and ratio above, the largest difference is 2.6e-06
(absolute); over the means a pass, 3.1e-07 (relative); the starting dies are equal burst by burst (T0, the scorer's `die_c.before`, against
the verifier's own mean of minshire[0] over each burst's before bracket). Nothing differs that could move a word.

**More of its readings** (desk checks of code; its result's own lines, quoted):

- "labels: 0 label bytes and 0 checksums differ in 4 x 3,750 + 625 card lines; 8/8 expected files = pins; ACC 9,849/10,000 (model and card);
  train 59,988/60,000"
- "files: SHA256SUMS 145/145 OK; manifest 118/118 equal; README tables 208 cells, 0 differ"
- "window: G 12:21:01 -> last start 13:52, last end 15:52; T0 12:24:48; first card command 12:24:48.516; close 12:33:10.674"
- "card-minutes 8.369 (cap 35); last burst start 6.01 min (<= 33); rest 370 / 373 / 374 min (booking / step 7 / step 9) after E197's
  06:10:45"
- "telemetry: 5,012/5,012 samples at 600 MHz; peaks 39.5 W, 54 C (minshire[0]); max gap 101 ms; 0 samples >= 65 W or >= 70 C; since_reset_ms
  -1 in all"

## 6. The findings, answered (dated clauses, Mon 16 Nov 2026, PST)

### 6.1 verify-e202d's finding 1 (low): how to read S1T

**The verifier's reading** (post hoc): E202.md 6 prices the card at rest as "the card at rest over t_w at T0's idle law". The ledger v2's
rest law for aifoundry3 (`frozen-v2.json` > `idle_laws` > `aifoundry3`) is the footing law over 52-66 C and an exponential branch outside
it. The scored bursts started at 50-51 C, on the exponential branch, where the law gives 23.165-23.471 W against each burst's own measured
idle (the board's mean over its before bracket, 3.5-0.3 s before the launch, read by the verifier from the committed telemetry) of
24.061-24.570 W: 0.88-1.13 W low. J over idle is forecast 24.5% and 28.0% high, and the rest term low, so the two partly cancel in J with
the card at rest. With each burst's measured idle in the law's place, S1T would read +9.45% (trained-scp, inside 10%) and +10.41%
(random-scp, outside); the dram pair +9.48% and +9.52% (REPORTED).

| configuration | burst | T0 (C) | the rest law at T0 (W), branch | the burst's measured idle (W) | measured - law (W) |
|---|---|---|---|---|---|
| trained-scp | 1 | 50 | 23.165, exp | 24.061 | +0.896 |
| trained-scp | 2 | 51 | 23.471, exp | 24.351 | +0.880 |
| trained-scp | 3 | 51 | 23.471, exp | 24.414 | +0.943 |
| trained-scp | 4 | 51 | 23.471, exp | 24.570 | +1.099 |
| random-scp | 1 | 50 | 23.165, exp | 24.197 | +1.032 |
| random-scp | 2 | 50 | 23.165, exp | 24.293 | +1.128 |
| random-scp | 3 | 51 | 23.471, exp | 24.474 | +1.003 |
| random-scp | 4 | 51 | 23.471, exp | 24.528 | +1.057 |

**Answered, Mon 16 Nov 2026:** recorded here, beside S1T, as the verifier asks: a post hoc reading, not a verdict. E202-S1T reads PASS as
registered: E202.md 6 registers the card at rest at T0's idle law, and E202.md 8 registers that "below 52 C does not block (scored given its
own T0, labelled so)"; the frozen scorer did both. Read S1T's PASS with it: on this day the rest law reads below the bursts' own idle and
offsets part of J over idle's high forecast in the at-rest total; with the measured idle the trained pair stays inside 10% and the random
pair does not. S2 and S2T read the frozen point at its own die (55 C, inside the footing law's band), so they do not use the exponential
branch. A later registration that wants S1T to test the load alone can score it at each burst's measured idle, or hold T0 inside the law's
band.

### 6.2 verify-e202d's finding 2 (nit): README departure 3's timeout clause

**The verifier's finding:** README.md's departure 3 ends "a plain `timeout 10` (never `-k`) on every device process", but the session's
sampler, a management-node process, runs without `timeout 10`.

**Answered, Mon 16 Nov 2026 (a correction, in this note's words; README.md stays as committed):** read the clause as "a plain `timeout 10`
(never `-k`) on every host process and config read". The session's sampler (each burst's `run.json` > `sampler`: `bash
tools/claims-v3/e128/ettelem_guard.sh sample --seconds 3300 --every-ms 100`) ran without `timeout 10`: it is bounded by its own `--seconds
3300` (the cap of 35 minutes and 20 more) and stopped by SIGTERM only (`run_e202.py`'s `stop_sampler`), as in every kit of this line.
Nothing sent or arranged a SIGKILL to any device process (the verifier's kill scan).

### 6.3 verify-e202d's finding 3 (note): the data commit's message scan

**The verifier's note:** the card lane scanned its commit message before `commit_lab.sh` added the round's standard trailer (a session line
and a co-author line), which two scan classes flag; every lab commit of the round carries the same trailer. **Answered, Mon 16 Nov 2026:**
read; nothing to fix for E202. This lane's scan (section 7) reads the full message as `commit_lab.sh` builds it, sets those two lines apart
by name and scans the rest.

### 6.4 verify-e202d's finding 4 (note): the runner's Python bounds

**The verifier's note:** the runner's `subprocess.run(..., timeout=30)` around `timeout 10 <host>` and the config read would end only the
`timeout` wrapper, never the device process; none fired, since every process exited 0. **Answered, Mon 16 Nov 2026:** read; it agrees with
the round's standing rule that no run sends or arranges a SIGKILL to a device process. No change for E202.

### 6.5 verify-e202d's finding 5 (note): a fixed 87 C sensor

**The verifier's note:** minshire[2] reads 87 C in every sample, idle included, so it is a fixed sensor value. **Answered, Mon 16 Nov
2026:** this lane's own count of the session's telemetry (`session/telemetry.jsonl.gz`) agrees: 87 C in all 5,012 samples, while minshire[0]
peaks at 54 C. Recorded here so that no reader takes `energy.json` > `die_c` > `max_high` (87 C in all 12 bursts) for the die: the
registered stop reads minshire[0], and the scorer's T0 (`die_c.before`) equals the verifier's minshire[0] mean burst by burst (section 5).

### 6.6 verify-e202d's finding 6 and the card lane's low finding: benign scan matches in the data directory

**The findings:** over the data directory, the round's `pubscan_all.py` matches 12 times, all on the unchanged reducer's own note about the
host's package counter in each burst's `energy.json`, and the tier scan's desk-path class matches one word, the name of the card's on-chip
memory in the device layer's address-format printout, in `host.err` and `sampler.err`; earlier committed data directories carry both.
**Answered, Mon 16 Nov 2026:** read and agreed, and this lane's own run of the same two scans over the directory reads the same: 12 matches,
one in each of the 12 `energy.json`, every one that note; the tier class in 17 `host.err` files and 1 `sampler.err`, 12 lines in each, every
one that printout. Both are the lab's own text; the data directory stays as committed. This lane's six files and message scan clean (section
7).

### 6.7 The card lane's note: what this run says for the matmul

**The card lane's note:** the card ran 5.8% faster than the cycle model's frozen point, and the forecast of J over idle runs about a quarter
high. **Answered, Mon 16 Nov 2026:** the scorer's figures carry it unchanged: measured / point seconds 0.942 and 0.942 (S3 PASS, inside the
band); J over idle given the seconds +24.5% and +28.0% (S1 FAIL); at rest +6.9% and +7.7% (S1T PASS, read with section 6.1); at the frozen
point +15.2% and +16.1% (S2T FAIL); ledger v3's S2T +10.3% and +11.2% (REPORTED). The verifier's own reading of the cycles, post hoc and
REPORTED, quoted: "post hoc cycles (scp): 4.818 M a round vs 5.114 M point (fast 3.863 M); 360.6 cycles an op if the rest is at its point
(point 387.8, fast 319.1); barrier waits 367 mean / 487 max-minion vs 533". These feed the round's matmul model (cycles, joules and
switching from a matmul's sizes and operations); this note decides nothing about that model.

### 6.8 The card lane's other notes

- **The eight scored bursts started at a die of 49-51 C, below the forecast band's 52 C** (the runner's die at each start; the scorer's T0
  reads 50-51 C). Answered, Mon 16 Nov 2026: the runner labelled each, and E202.md 8 scores them given their own T0; section 6.1 is what it
  means for S1T. Nothing else changes.
- **8.37 card-minutes against the plan's estimate of about 17.** Answered, Mon 16 Nov 2026: README.md's departure 10 records it; no reading
  rests on the estimate.
- **The build step's log line calls the build job "the dry pass a3-build-e202"**, the runbook's generic job wording. Answered, Mon 16 Nov
  2026: the line is in the card lane's own log, in no file of this directory; nothing to change.

## 7. Checks before the commit

- `scores-e202.json`, `scores-e202.txt`, `v3-scores-e202.json` and `v3-scores-e202.txt` as staged are byte-equal to the card lane's two
  RB_OUT files and to the runbook's captures of the step's fifth and sixth calls (`cmp`), and to this lane's desk re-run (section 2); the
  card lane's log of step 13 holds each capture's bytes once.
- In a copy of this directory with the six new files: `SHA256SUMS` 145 of 145 and `SHA256SUMS-note1` 7 of 7 entries OK; 153 files, every one
  in a list but `SHA256SUMS-note1`.
- The desk-path gate (`nopath_q142s.py`, v3.1, with the lab clone and the round's folders forbidden) read the six new files with 0 hits, and
  a login check found no home path, no login and no holder line in them or in this commit's subject and body.
- The public-text scans (the lab's `sanitize_extracts.py` with its fixed list and the box's local table, the round's `pubscan_all.py` and
  `tiers_scan.sh`, and the tier classes of private, vendor, access and mechanism words) found nothing in the six files or in this commit's
  subject and body (its two standard trailer lines set apart by name).
- The commit holds these six files and nothing else.

## What does not change

Every reading, verdict, gate, stop and figure of `README.md` and its files stands, except the one clause section 6.2 words anew in this note
(`README.md` itself stays as committed); this note adds the scorer's and the v3 note's outputs beside them and reads them, and changes
nothing. The reducer, the scorer, the v3 note and the kit read none of this note's files. This lane reached no box, opened no device and
changed no committed file.

SPDX-License-Identifier: Apache-2.0
