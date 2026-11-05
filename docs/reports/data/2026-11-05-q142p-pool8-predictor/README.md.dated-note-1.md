# Dated note 1 beside README.md (Thu 5 Nov 2026; Q142(p)'s fix pass, after its verifier) - `predict_pool8_a2.py` supersedes three of `predict_pool8.py`'s modes; its self-test passes U0-U7, with the frozen T1-T9 re-run identical

*On the kinds page, [section 11, what is still open](https://spacesheep.dev/@yaroslavvb/horace-kinds-of-numbers#11-what-is-still-open):
**item 6**, with items 8 and 9. Written on Thu 5 Nov 2026 from about 00:33 PST, desk only on the Intel, and committed at the time git
records. It answers the lane's verifier (faults 1-11), under
[dated note A2](../../../../tools/claims-v3/m10/POOL8-REGISTRATION.md.dated-note-2.md) beside the registration (lab `68a7c322`,
00:21:34 PST), which was committed before any file or output below.*

**What stays as committed** (`9d81d254`): `predict_pool8.py`, `README.md`, `SHA256SUMS` (16 entries), `selftest-pool8.json` and
`selftest-pool8.txt`. The frozen predictor is unchanged, byte for byte. Its self-test, re-run here, gives the committed JSON exactly.

## Which file does what now

[`predict_pool8_a2.py`](predict_pool8_a2.py) is the entry point the next round's (x) lane runs. It checks `predict_pool8.py` against
`SHA256SUMS` and itself against [`SHA256SUMS-a2`](SHA256SUMS-a2), then imports the frozen file.

| mode | which file's | what changed |
|---|---|---|
| `predict`, `plan` | `predict_pool8_a2.py` supersedes the frozen command line | Exit 3, with nothing written, for a point with a `check_mismatch` or one counted twice with different records. The frozen file exits 1 there, also writing nothing. The predictions are the frozen file's, byte for byte (A2-2). |
| `burst` | `predict_pool8_a2.py` on card 0 | The M10 block's `burst_die_rise_95` is M10's own band. The frozen field, which is M9's law's band, is kept as `burst_die_rise_95_M9_law` (A2-1). On aifoundry2 the output is the frozen one. |
| `intervals` | `predict_pool8_a2.py` | Every section-7 bootstrap and coverage line at the pool's own n, and LG's groups with its power at the pool's own D_ref (A2-3, A2-4). Its P1-P3 lines equal the frozen mode's. |
| `scale`, `primary`, `heat-minutes` | the frozen file's, passed through | nothing |

**A non-zero exit of either file means no predictions.**

## Results: the self-test after the verifier ([`selftest-pool8-a2.json`](selftest-pool8-a2.json), [`selftest-pool8-a2.txt`](selftest-pool8-a2.txt))

| test | what it checks | reading |
|---|---|---|
| U0 | the lists | `SHA256SUMS` 16 and `SHA256SUMS-a2` 9 entries hash as listed; `POOL8-SHA256SUMS` 209 |
| U1 | the frozen T1-T9, re-run in their own process | rc 0, PASS, **the JSON identical to the committed `selftest-pool8.json`** |
| U2 | the command lines of both files, writes enabled (faults 2 and 11) | Points short of N: 3 and 3. A `check_mismatch`: frozen 1, new 3. A point counted twice: frozen 1, new 3. Roles unreadable: 3 and 3. `plan` with a `check_mismatch`: frozen 1, new 3. No predictions file in any refusal. An int8 control: 0 and 0, both writing predictions with identical bytes. `heat-minutes 10.0` passes through: 10.0 (primary) and 10.3199 (arm) |
| U3 | card 0's band on E170's committed reads (fault 1) | h = **0.593 °C**, `numpy.quantile` at 0.95 over the 39 residuals' absolute values, equal to the stdlib linear form. The residuals equal T6's committed list (rms 0.3385 °C), and 37 of 39 lie within h at E170's measured board, in sample. On all 10 tiles M10's band contains its rise, and the M9 blocks and every other M10 field equal the frozen `burst`. The frozen band excludes M10's rise on all 10 |
| U4 | every rule's line on four cards' predictions of committed tiles (fault 3) | 18 rules at 600 MHz, 11 on aifoundry2, 7 on card 0. P1-P3 equal `predict_pool8.intervals` exactly. The references equal the registered figures: aifoundry3 fp32 260 rows at 0.2019 W, fp16 133 at 0.1476, int8 114 at 0.1696; card 1 190 at 0.2004, 154 at 0.1651, 108 at 0.1849; E165's 36 governed cells at 4.50 MHz / 0.78 W, 42 pinned at 2.33 MHz / 0.82 W, 112 heat residuals at 0.6845 °C. The heat references are deterministic, with rms within 3% of the registered. On the real sets, the eight single-high-bit re-runs span only 1.0-1.1 W of D_ref, so their group does not count and LG would read NOT SCORED |
| U5 | the bootstrap engine against committed output | E164's registered precision, all eight intervals, reproduced exactly from E164's references, seeds and draws. The coverage line equals E165's `coverage_line` for n 0-200, and E164's committed 42 of 48 |
| U6 | LG's F tests (fault 4) | The closed form equals numpy's least squares within 2.6e-15 (relative); the F points equal tabulated values within 5e-5; design_power.py's n = 8 block, replayed with its own stream and t point, gives its 14 lines identically; the groups are read from a predictions file as A2-4 says |
| U7 | every file the self-test opens or imports | 233, none unlisted; all 234 listed entries hash as listed |

**LG's power** (A2-4; [`../../../../tools/claims-v3/m10/pool8/design-power-groups.txt`](../../../../tools/claims-v3/m10/pool8/design-power-groups.txt)).
These are percentages for a true 0.6% gain / a true 0.11 W level, at noise 0.0368 W:

| re-runs | reads it |
|---|---|
| 12 in one group, D_ref over 5-25 W | 80 / 88 |
| split 6 + 6 | 63 / 73 |
| 4 + 4 + 4 | 44 / 56 |
| 12 in one group, D_ref over exactly 8 W | 22 / 29 |

## Corrections to README.md's text (faults 5, 8, 9 and 10, as A2-6 gives them)

- **The development runs.** README.md says "three passes of the self-test (23:21-23:24 PST) and one of a CLI smoke ... outputs only in
  the lane's scratch. The committed self-test is the run after the last code change." The slot log holds 11 jobs of the lane:

  | job | times (PST) | what happened |
  |---|---|---|
  | the design script | 22:58:58; 23:07:35 | ran twice |
  | the file trace | 23:00:38; 23:00:49 | the first exited 127 |
  | the self-test in scratch | 23:21:27; 23:22:17; 23:23:55 | failed: the first wrote no output, the other two failed T8 alone |
  | the CLI smokes | 23:24:54; 23:25:51 | two |
  | the self-test into this directory | 23:28:08-23:28:16; 23:28:46-23:28:54 | both passed; the first was overwritten by the second, the committed output |

  Both passing runs came after the last code change (23:27:47).
- **This directory's date.** Its work ran on Wed 4 Nov PST: it was born at 23:15:35 and committed at 23:30:18. The lab dates by the day
  the work happens, so the name is a day late. The path stays, and this note's files are Thu 5 Nov's.
- **A1's dateline,** quoted under "Departures": A1 was last written at 23:26:28 and committed at 23:26:44 (`8a8fa34c`).
- **"The 62"**: section 9's wording holds. They are the 62 files neither M10's registration's 174 nor M10's 68 named, and 60 of them are
  pool-6 and pool-7 tiles that blind6's and blind7's lists already name.

## How the (x) lane uses it, in order (the registration's section 10, with A2-7)

1. Copy pool 8 unchanged into `tools/claims-v3/kinds/blind8/`.
2. On the mini, count the bench's three standard points for every tile. Then repeat `predict_pool8_a2.py plan` and the points it names
   until every float tile is complete.
3. Run `predict_pool8_a2.py predict` for aifoundry3, aifoundry1c1, aifoundry2 and aifoundry1c0. Any non-zero exit means no predictions:
   fix the input and run again. Mark aifoundry2's tiles over 82 W.
4. Run `predict_pool8_a2.py intervals` on all four predictions files. Its LG block states the power at the pool's own groups (A2-4).
5. Commit the pool, the counts, the predictions and the intervals in one commit, before any claim.
6. After each session: `scale`, then `primary`. On the governed cards, run `predict_pool8_a2.py burst` with the session's reads. Every
   verdict reads its line at the scored n (A2-3 (g)).

## What this does to predicting power and heat

It changes no prediction of power or heat: the frozen predictions come out byte for byte, and M10, M9 and every rule stand. It does four
things.
- Card 0's burst heat under M10 now carries its own band, ±0.593 °C at 95% (the law's own held-out error, in sample 37 of 39), where the
  field written before was M9's law's ±1.406 °C, centred 2.1-3.3 °C below M10's rise on the ten tiles tried.
- The pool's refusals are uniform: any missing or bad count stops the run with exit 3 and no file.
- Every rule has its line before the data, so no scorer chooses one later.
- The level-or-gain test's power is stated honestly. It reaches 80% / 87% only for 12 re-runs in one session spanning about 20 W. Split
  over sessions or over a narrow span it falls to 63% / 73% or lower, so the (x) lane states it at the pool's own design before any
  session.

## Compute

Every job ran on the Intel through the round's local slot, one at a time, at nice 10. No lab box, `run_remote` or card was used.

| job | times (Thu 5 Nov, PST) | what happened |
|---|---|---|
| the design script, `design_power_groups.py` | 00:14:21-00:15:01, into scratch; 00:17:59-00:18:40, the committed output | the second's output is byte-identical to the first's |
| the new self-test, development | 00:28:25-00:29:18 | rc 1: U6's replay used the t point of 8 df for n = 8, and the code was corrected |
| a one-off replay check | 00:29:42-00:29:55 | the check behind that correction |
| the new self-test, development | 00:30:52-00:31:37 | PASS |
| the new self-test, committed | 00:32:01-00:32:38 | PASS, identical to the second development run |
| reads of the round's slot log, filtered to this lane's own jobs | 00:05:13; 00:05:29 | |

The last code change was at 00:30:38.

## Files

| file | what |
|---|---|
| `predict_pool8_a2.py` | the entry point after the verifier, and its self-test U0-U7 |
| `selftest-pool8-a2.json`, `selftest-pool8-a2.txt` | the committed self-test, and its one-line summary |
| `SHA256SUMS-a2` | the files `predict_pool8_a2.py` reads beyond `POOL8-SHA256SUMS` and `SHA256SUMS`: itself, A2, the k-group power script and its output, `selftest-pool8.json`, E164's two committed reference files, and E163's and E164's `scored.json` (the design scripts read them; the registration's list named neither) |

Re-run from the top of the tree, with numpy 1.26: `python3 -B docs/reports/data/2026-11-05-q142p-pool8-predictor/predict_pool8_a2.py
selftest --out <file>`. It takes about 40 s, and spawns the frozen self-test and 13 command-line runs: six cases on each file, plus `heat-minutes`. Then run
`shasum -a 256 -c docs/reports/data/2026-11-05-q142p-pool8-predictor/SHA256SUMS-a2`.
