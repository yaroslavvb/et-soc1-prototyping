# E191's first-session data README, dated note 1 (Sun 15 Nov 2026): the frozen scorer's output, run on the stop record `1a4bc1e3`, committed beside it as a record - every rule NOT DECIDED (no pass ran, every configuration NO DATA); used by no rule

*Beside [`README.md`](README.md), [`SHA256SUMS`](SHA256SUMS) and [`FILES.txt`](FILES.txt), which stay as committed in `1a4bc1e3`.
Written on aifoundry2 from 17:18 PST on Sun 15 Nov 2026 (week 46) by the clock, desk only (no card, no lab box, no device, no post), by
Q184's lane `scores-e191`, after this record's verifier `verify-n2e191` (Sun 15 Nov 2026: the stop record holds, with no finding). The
kit's step 13 ([`KIT.md`](../../../../tools/claims-v3/e191/KIT.md), its table of steps: "`score_e191.py` (registered, unchanged) on the
committed data; RB_OUT/scores-e191.json; read the words"; [`rb/s24_score_e191.sh`](../../../../tools/claims-v3/e191/rb/s24_score_e191.sh))
runs the frozen scorer only after the data commit and leaves its output to a later commit, and README.md's "Next" says the same ("a later
lane commits it beside this directory"); this lane is that later lane. This note commits the output byte for byte, with the scorer's
printed lines, **as a record**: E191.md's dated amendment A1 (A1-2) uses the first session's readings in no rule, and E191's words are
the second session's, scored on its own directory
([`../2026-11-15-e191-blind-day-aifoundry1-c1-s2/`](../2026-11-15-e191-blind-day-aifoundry1-c1-s2/), data commit `7156ac15`; its dated
note 2 commits that output in the same commit as this note). **No number, rule, verdict, forecast, band, threshold or gate reading
changes, and nothing is scored again.** Interpreter: `/usr/bin/python3` 3.12.3 on aifoundry2. Labels: **registered** (E191.md, its note
1 and the kit as committed), **measured** (the session's committed files), **desk check of code** (the re-runs). The words are the frozen
scorer's own output on the committed record.*

## 1. The new files

| file | what | bytes | sha256 |
|---|---|---|---|
| [`scores-e191.json`](scores-e191.json) | the frozen scorer's output ([`score_e191.py`](../../../../tools/claims-v3/e191/score_e191.py), registered in `300d76e4`, unchanged): the rules E191-S1, S1T, S2 and S2T with their words, counts and verdicts (each NOT DECIDED); each configuration NO DATA with 0 passes; the arms v2.1 and v2c (reported, the same) | 6,762 | `cac54fd5...` |
| [`scores-e191.txt`](scores-e191.txt) | the scorer's printed lines, copied byte for byte from the runbook's capture of that call (its stdout and stderr as they came), not rewritten | 113 | `24f54a88...` |
| `README.md.dated-note-1.md` | this note | | |

[`SHA256SUMS-note1`](SHA256SUMS-note1) pins these three and `README.md`, `SHA256SUMS` and `FILES.txt` at their committed bytes. With
`SHA256SUMS` (22 files, unchanged), every file here is pinned but `SHA256SUMS-note1` itself.

## 2. When, where and on which commit the scorer ran

From the runbook's log (`runbook.log`) and its capture of each call, both kept outside the repository in the card lane's runbook folder
RB_OUT, and from the lab clone's own log of its HEAD:

- **Step 13, the frozen scorer** ([`rb/s24_score_e191.sh`](../../../../tools/claims-v3/e191/rb/s24_score_e191.sh), the kit's): Sun 15 Nov
  2026 at **10:23:25 PST**, on aifoundry2, in the lab clone with its HEAD at **`1a4bc1e3`**, the data commit (made at 10:23:05 PST and
  pushed by 10:23:10), which stayed the clone's HEAD until the next commit (`fe08ed67`, E193 data, sitting A) at 11:13:37 PST.
- **Its gates**, the log's lines 85-88, at 10:23:24-10:23:25 PST, each with rc 0: the data directory committed (the last commit naming it:
  `1a4bc1e3`); the directory clean (no line); `SHA256SUMS` 22 of 22 entries OK; the history check, `HISTORY OK` (131 files added since
  `46a16bd0` on E191's paths, none changed or removed; E191's registration `300d76e4`, its note 1 `8c8f825f` and its kit `eb1ac923`, and
  E189's registration `c86940c1` and kit `b42dc95c`: nothing under `tools/claims-v3/e191` or `tools/claims-v3/e189` changed since; nothing
  untracked; no shadowing addition or uncommitted file in the folders the day's Python puts first).
- **The scorer**, the log's line 89 (its last): `/usr/bin/python3 -I -B tools/claims-v3/e191/score_e191.py
  docs/reports/data/2026-11-15-e191-blind-day-aifoundry1-c1 --out RB_OUT/scores-e191.json`, rc 0 in 0.0 s (under 0.05 s). `scores-e191.json`
  was last written at 10:23:25.300, the same instant as the runbook's capture of the scorer's printed lines (the step's fifth call). The
  step then printed its own last line, which card-e191's log of the step holds: `[s24_score_e191] scored:
  {"E191-S1":"NOTDECIDED","E191-S1T":"NOTDECIDED","E191-S2":"NOTDECIDED","E191-S2T":"NOTDECIDED"} (RB_OUT/scores-e191.json; the records lane
  commits it beside the data)` (the step's line drops every space and newline of the scorer's printed lines, so it reads NOTDECIDED).
  `runbook.log` itself holds each call's line, not its output; the runbook's bounded runner (v3.1's `rb_run.py`) writes each call's stdout
  and stderr, as they come, to that call's capture file, and `scores-e191.txt` is the scorer's.
- **The scorer as registered:** `score_e191.py`, its list `SHA256SUMS-e191-registration` and the files it reads (`forecast_e191.py`,
  `forecast-e191.json`, `plan-e191.json`, `E191.md`, the ledger v2's `tools/ledger/ledger_v2.py` and `frozen-v2.json`) are the same git
  blobs at the registration `300d76e4`, note 1 `8c8f825f`, the kit `eb1ac923`, the data commit and this note's parent; from the registration
  to this note's parent, `tools/claims-v3/e191` changed by additions only, and `tools/ledger` and the ledger v2's data folder not at all.
  The scorer refuses unless the 9 frozen files of that list (all but its two self-test outputs) read OK, and its record reads
  `frozen_files_checked` 9 and `not_used` `[]`; the whole list reads 11 of 11.
- **The interpreter:** `/usr/bin/python3` 3.12.3 on aifoundry2, isolated (`-I -B`); the history check's line names it.
- **Re-run since, at the desk, on the committed bytes** (desk checks of code; each JSON byte-equal to `scores-e191.json`, and each run's
  printed lines to `scores-e191.txt`): by `verify-n2e191` (11:50 PST) in its scratch clone of the lab at `fe08ed67` (its log's first 113
  bytes, the scorer's printed lines, then its own line `scorer rc 0`); and by this lane (17:25 PST) from a fresh extract of `1a4bc1e3`'s own
  tree holding the four folders the scorer reads (`tools/claims-v3/e191`, `tools/ledger`, `docs/reports/data/2026-11-12-q166-ledger-v2` and
  this directory: 117 files, where `SHA256SUMS` read 22 of 22 and the registration's list 11 of 11), run as the runbook ran it, in the
  round's CPU slot with no device node reachable. The run wrote nothing into the extract.

## 3. The four rules' words, as the frozen scorer gives them

[`scores-e191.txt`](scores-e191.txt), verbatim (`scores-e191.json` > `verdict_of_the_day`):

```
{
 "E191-S1": "NOT DECIDED",
 "E191-S1T": "NOT DECIDED",
 "E191-S2": "NOT DECIDED",
 "E191-S2T": "NOT DECIDED"
}
```

Behind the words (`scores-e191.json` > `rules`; the rules are E191.md 8.3's, registered):

| rule | the scorer's words | scored | within | outside | word |
|---|---|---|---|---|---|
| **E191-S1** | score 1, given the measured seconds: J over idle a launch within 10% on at least 5 of the 6 configurations, and the rms of the six errors at most 10% | 0 | 0 | 0 | **NOT DECIDED** |
| **E191-S1T** | score 1, given the measured seconds: J with the card at rest a launch within 5% on at least 5 of 6 | 0 | 0 | 0 | **NOT DECIDED** |
| **E191-S2** | score 2, with the seconds forecast: the measured kernel seconds inside the frozen two-sided band and within 15% of the point, on at least 5 of 6 | 0 | 0 | 0 | **NOT DECIDED** |
| **E191-S2T** | score 2, with the seconds forecast: J with the card at rest a launch, at the forecast seconds and die, within 15% on at least 5 of 6 | 0 | 0 | 0 | **NOT DECIDED** |

Each configuration (`scores-e191.json` > `configs`): copy, zeros **NO DATA**, 0 passes; copy, random **NO DATA**, 0 passes; SHA-256 **NO
DATA**, 0 passes; sort, sorted **NO DATA**, 0 passes; sort, shuffled **NO DATA**, 0 passes; sparse parity **NO DATA**, 0 passes, each with
the scorer's note "fewer than 2 good passes: no data, never a failed prediction"; no error, figure or flag is computed. The arms v2.1 and
v2c (`scores-e191.json` > `arms`; registered arms, REPORTED) read the same: every rule NOT DECIDED with 0 scored, every configuration NO
DATA with 0 passes. `not_used` is empty and `frozen_files_checked` reads 9.

## 4. Why every word is NOT DECIDED (measured, from this record)

The session (T0 1794766494, 10:14:54 PST) stopped at its smoke gate at 10:14:56 PST, before any pass: the smoke's first card run exited 0
and read FAILED with status None, because the device runtime printed a line inside the ledger host's own output and the kit's reader took
the broken head (README.md; the kit's dated note 2, section 1). `runner.rc` is 16, the record holds no `passes/` directory, and the scorer
found no pass to read for any configuration. By E191.md 8.2, a configuration with fewer than 2 good passes reads NO DATA, never a failed
prediction; by 8.3, a rule is PASS when at least 5 configurations meet it, FAIL when 2 or more miss it, and otherwise NOT DECIDED, with NO
DATA counting neither way. With all six configurations NO DATA, none meets or misses any rule, so each of the four reads NOT DECIDED.
These four words say that no rule had a reading that session; they are not a verdict on the forecasts. The day's E191 words are the
second session's (`7156ac15`, scored on its own directory; its dated note 2).

## 5. Checks before the commit

- `scores-e191.json` and `scores-e191.txt` as staged are byte-equal to the card lane's RB_OUT file and to the runbook's capture of the
  scorer's call (`cmp`), and to this lane's desk re-run (§ 2); the card lane's log of the step holds the same printed lines.
- In a copy of this directory with the four new files: `SHA256SUMS` 22 of 22 and `SHA256SUMS-note1` 6 of 6 entries OK; 29 files, every one
  in a list but `SHA256SUMS-note1`.
- The desk-path gate (`nopath_q142s.py`, v3.1, with the lab clone and the round's folders forbidden) read the four new files with 0 hits,
  and a login check found no home path, no login and no holder line in them or in this commit's subject and body.
- The public-text scan (the lab's `sanitize_extracts.py`, its fixed list and the box's local table, and the round's lists of private,
  vendor, access and mechanism words) found nothing in the four new files or in this commit's subject and body.
- Both directories' new files went into one commit, with nothing else.

## What does not change

Every reading, gate, stop and figure of `README.md` and its files stands; this note adds the scorer's output beside them and reads it, and
changes nothing. The record stays used by no rule (A1-2). The reducer, the scorer and the kit read none of this note's files. This lane
reached no box, opened no device and changed no committed file.

SPDX-License-Identifier: Apache-2.0
