# Dated note A2 beside POOL8-REGISTRATION.md (Thu 5 Nov 2026; Q142(p)'s fix pass, after its verifier) - card 0's M10 die-rise band, the two stops that exit 3, every section-7 line, LG's power with k groups, and the readings, wording and datelines the verifier corrected

*Written on Thu 5 Nov 2026 from about 00:20 PST on the Intel, desk only, and committed at the time git records. POOL8-REGISTRATION.md,
`pool8-registration.json`, both hash lists, `pool8/design_power.py` and `pool8/design-power.txt` (`3e97f583`), dated note A1
(`8a8fa34c`) and the predictor's directory (`9d81d254`) stay as committed. This note is committed before every output it governs: no
pool-8 tile, prediction, scale or score exists, and the new file that computes A2-1's band and A2-3's lines (`predict_pool8_a2.py`,
A2-7) is committed after it. It changes no price, card term, power band, rule, threshold or verdict of M10 or M9 and no rule of section 7.
It registers one reported band (A2-1), maps two stops to the registered exit status (A2-2), fixes how each section-7 line is computed
(A2-3), restates LG's power (A2-4), and corrects readings, wording and datelines (A2-5, A2-6). It answers the lane's verifier, faults
1-11 (the kinds page's [section 11](https://spacesheep.dev/@yaroslavvb/horace-kinds-of-numbers#11-what-is-still-open), item 6, with
items 8 and 9).*

## A2-1. Card 0's die rise under M10 has its own band; the frozen field is M9's law's band (fault 1)

**What sections 1 and 5 say:** card 0's 6 s burst rise is `predict_m10.rise_card0_burst(P_board, m10)`, 0.2415 °C per board W over
21.5 W (term c2), on M10 carried's predicted board. No band was registered for it.

**What the frozen code does:** `predict_pool8.py`'s `burst` mode on card 0 writes c2's rise into the M10 block's `burst_die_rise_c` but
keeps `e170_common.pred_card0`'s `burst_die_rise_95`. That is aifoundry2's burst heat law's band (0.1400 °C/W, ± its `q95_abs_c` of
1.406 °C), centred on M9's law's rise on M10's board (`burst_die_rise_c_M9_law`). On every tile the verifier tried it excludes M10's own
rise (fp32.b_onebit_b20_one: 7.58 °C against [2.99, 5.80]).

**So:** that field is M9's law's band, not M10's, and is never read.

**M10's card-0 band, registered now:** the rise R ± h.
- h is the 95th percentile of the absolute values of term c2's 39 leave-one-tile-out residuals on E170: the list
  `predict_pool8.t6_card0` returns (rms 0.3385 °C), taken as `numpy.quantile(sorted |r|, 0.95)` with numpy's default linear
  interpolation.
- That is the form of aifoundry2's own band: `fit_m9_a2.q95` over that burst heat law's 112 residuals gives its 1.406 °C.
- R is c2's rise on the burst mode's predicted board, unrounded; the band's ends are rounded to 0.001 °C.
- Like the band it mirrors, it is the heat law's error at a given board, not the board's.
- It is reported beside the rise, and no rule reads it: P8-C0-H1 (an rms bootstrap on the residuals of A2-3 (d)) and P8-C0-HK (paired)
  are unchanged.
- `predict_pool8_a2.py`'s `burst` writes it as the M10 block's `burst_die_rise_95` and keeps the frozen field as
  `burst_die_rise_95_M9_law`. h is computed by that file after this note's commit, not here.

## A2-2. A check_mismatch or a twice-counted point exits 3, as registered (faults 2 and 11)

**What section 2 says:** a float tile whose points do not reach its N, a point with a `check_mismatch`, or a point that appears twice
with different counts: the tile gets no prediction, and the run exits 3 without writing a predictions file.

**What the frozen code does:**
- The first case exits 3 (a `Refused`).
- The other two stop through `stop()`, which raises SystemExit with a message, so the process exits 1. The verifier's runs printed
  "POOL8 STOPPED: ... check_mismatch" and "... counted twice with different records".
- Nothing is written in any case: every stop comes before the write.
- T4 tested only the first case. Its `files_written` proved nothing, because it called `predict(write=False)`.

**So:**
- The (x) lane runs `predict_pool8_a2.py`. Its `predict` and `plan` map exactly these two stops to exit 3, with nothing written: the
  frozen messages that contain `check_mismatch` or `counted twice`.
- Every other stop (inputs that differ from a hash list, a manifest that cannot be read) stays exit 1.
- **A non-zero exit of either file means no predictions.**
- The new self-test runs both files' command lines on temporary pools, with writes enabled. It checks each exit status, and checks that
  no predictions file appears.

## A2-3. How every section-7 line is computed (fault 3; section 8's "the intervals mode prints them at the pool's own n")

`predict_pool8_a2.py intervals` prints them for each card's predictions file, and the (x) lane commits its output with the predictions.
Before this note, `predict_pool8.py intervals` printed P8-P1-P3 only.
- **(a) The bootstrap line.** This covers every rule section 7 calls "bootstrap": P8-P1-P3, B1, B2, H1-H3, A2-F1, A2-F2, A2-W1, A2-W2,
  A2-H1, C0-W, C0-F and C0-H1.
  - The engine is `predict_pool8.boot_range` as frozen.
  - It makes 20,000 draws from one stream, `random.Random(80000 + the sum of the rule id's character codes)`. The rule id is written as
    section 7's tables write it: `P8-P1`, `P8-B1`, `P8-H1`, `P8-A2-F1`, `P8-A2-W1`, `P8-A2-H1`, `P8-C0-W`, `P8-C0-F`, `P8-C0-H1` and so on.
  - Each draw takes n reference errors in turn, with replacement.
  - The line is the sorted statistics' `vals[int(0.025 x 20000)]` to `vals[int(0.975 x 20000) - 1]`.
- **(b) B1 and B2** take the mean.
  - B1's "same format mix": each draw takes F1's fp16 count of errors from fp16's reference, then its fp32 count from fp32's. The
    formats go in sorted order, E164's `interval` form, all from the one stream of (a).
  - B2 takes I1's count from int8's reference.
- **(c) H1-H3's reference:**
  - 2,000 draws of `rng.gauss(0.0, r)` from `random.Random("P8|heat-reference|<card>|<t>")`.
  - `<card>` is the predictions file's card (`aifoundry3` or `aifoundry1c1`) and `<t>` the format.
  - r is `pool8-registration.json` › `bands.heat_4p5s.rms_c[a3|c1][t]`.
  - The line is then (a).
- **(d) The references.**
  - P1-P3, B1 and B2: as section 7 and `pool8-registration.json` say (`rows-m10.json` through `predict_pool8.ref_errors`).
  - A2-F1 and A2-F2: `tools/claims-v3/e165/predictions-e165.json` › `reference.e2e.governed.mhz_err` (36 cells) and
    `.pinned.mhz_err` (42). A2-W1 and A2-W2: their `w_err`. A2-H1: `reference.heat.rise_err_c` (112).
  - C0-W: the 42 pinned `w_err`. C0-F: the 42 pinned `mhz_err`.
  - C0-H1: the 39 residuals of A2-1 (`selftest-pool8.json` › T6 › `c0_h1_reference_residuals_c`).
- **(e) The coverage lines** (P8-C1, P8-H4): the smallest k with P(X ≤ k) ≥ 0.025 for X ~ Binomial(n, 0.95). This is E163's and
  E164's `binom_low`, the same as E165's `coverage_line`.
- **(f) The sets on aifoundry2 and card 0.** Section 7's paragraph "The sets, from the manifest's bytes and fields only" holds on every
  card.
  - The scored tiles there are N1: re-runs and anchors are never among them.
  - On aifoundry2, the tiles the frozen file marks `admission_82w_out` are left out.
  - aifoundry2's governed and pinned groups are the frozen file's M10-carried `a2_fallback` group: governed if the burst is predicted
    below 795 MHz at the fallback and T_ref, as section 7 says.
  - The minimums are `pool8-registration.json`'s: A2_group 8, A2_all 10, C0 8, C0_M1 10.
- **(g) The line a verdict reads** is the line at the scored n, from the same function and seed. The table the (x) lane commits, at the
  planned n (every tile of the set), is the forecast. A rule whose scored n is under its minimum is NOT SCORED.
- **(h) No line before the data:** the paired rules (M1, M1f, M1i, A1, A2-M1, C0-M1, C0-HK, HM) and KA. The table gives their planned n
  and minimum.
- **(i) The fixed lines** (A2-G, A2-Bg, A2-Bp, C0-B) are section 7's, printed with their planned n.
- **(j) LG:** A2-4.

## A2-4. LG's power with k reference groups (fault 4)

**What section 8 says:** at 12 re-runs a 0.6% gain reads GAIN in 80% of draws and a 0.11 W level reads LEVEL in 87%. Those draws had one
reference group, with D_ref spread evenly over 5-25 W. Section 7 groups the re-runs by reference session: pool 6's by E153 or E157, pool
7's by E163 or E164.

**Computed before writing** (design only, committed rows only, no pool-8 data): [`pool8/design_power_groups.py`](pool8/design_power_groups.py)
→ [`pool8/design-power-groups.txt`](pool8/design-power-groups.txt), standard library.
- It runs the registered test exactly: two F tests at 5% with (k, n − 2k) df; a group counts at 4 or more tiles spanning 8 W; n − 2k must
  be at least 4.
- Its F points come from the incomplete beta function, and they match tabulated values to 4 decimals.
- It replays `design_power.py`'s one-group power with that file's own random stream and its t points squared: all 42 lines come out
  identical to `design-power.txt`. So the registered figures are this test's.
- The noise is recomputed from the same rows: 0.0368 W over 17 tiles.

**The power** (noise 0.0368 W, 5,000 draws a cell, as GAIN % / LEVEL %, for a true 0.6% gain / a true 0.11 W level):

| re-runs | D_ref over 5-25 W | at 1.5 × the noise | each group's D_ref over exactly 8 W |
|---|---|---|---|
| 12 in one group | 80 / 88 | 49 / 60 | 22 / 29 |
| 6 + 6 (two sessions) | 63 / 73 | 31 / 39 | 16 / 20 |
| 8 + 4 | 63 / 73 | 31 / 39 | 16 / 20 |
| 9 + 3 (a group of 3 does not count) | 65 / 75 | 36 / 43 | 17 / 21 |
| 4 + 4 + 4 | 44 / 56 | 20 / 25 | 12 / 14 |
| 16 in one group | 90 / 93 | 61 / 73 | 28 / 36 |
| 8 + 8 | 80 / 89 | 45 / 56 | 22 / 28 |

With no difference the test reads NOT SEPARATED in 93-95% of draws in every row.

**So:**
- Section 8's 80% / 87% hold only for one reference group whose D_ref spans about 20 W.
- Split over sessions, or over a narrower span, the same 12 re-runs read much less often.
- The rule is unchanged, and its verdict reads as registered.
- **Before any pool-8 session, the (x) lane commits LG's power at the pool's own design.** That is `predict_pool8_a2.py intervals`' LG block
  for each 600 MHz card:
  - the groups by reference session, k, n, each group's D_ref span, the df and the F points;
  - the power at 0.0368 W for five truths (none, a 0.6% and a 1.0% gain, a 0.11 W and a 0.15 W level), from `power_at` at the D_ref
    the committed predictions file holds (`lg_reference`). Each design takes 5,000 draws, seeded `"P8-LG|power|<card>|<truth>"`.
- A re-run's group is the reference session of its own entry in the frozen file's `lg_reference`: the entry whose tile name equals the
  re-run's manifest name, else the first listed. A tile with more than one entry is listed. A re-run with no entry (its reference
  session's footing holds no item for it) is in no group, and is listed.
- A verdict read at a design whose stated power for a 0.6% gain or a 0.11 W level is under 50% says so beside it.

**A worked example at a committed design** (post hoc design only): E163's K14 float re-runs. E141's 7 tiles span 8.0 W of D_ref; E152's 6
span 0.65 W and do not count. There the test would read a 0.6% gain in 17% of draws and a 0.11 W level in 14%.

## A2-5. RR is a set; what the governed outcomes mean; C0-F's verdict (faults 6 and 7)

- **RR is a set, not a rule.** A1-2's "(P8-LG, P8-RR)" reads "(P8-LG, on the set RR)". Section 7's "(LG, RR)" names the rule and its set,
  and defines no P8-RR. M10's errors on RR are reported only.
- **P8-C0-F's verdict** (its cell reads "bootstrap") is **PASS** at or below the bootstrap's 97.5% point, else **FAIL**.
- **What each governed outcome means** (section 7 gave A2-M1, C0-M1, C0-H1 and C0-HK only):
  - **A2-G** PASS: M10 carried gets aifoundry2's governed burst clock within rank 2's lines (rms ≤ 4.0 MHz, |mean| ≤ 2.0 MHz) on new kinds.
    FAIL: the clock term or the carried D misses under the governor by more than rank 2 allows.
  - **A2-Bg** PASS: no resolved board level on governed bursts (|mean| ≤ 0.5 W). FAIL: a level the session's zeros anchors did not remove.
  - **A2-Bp** PASS: pinned bursts' board within |mean| ≤ 0.5 W and rms ≤ 1.0 W, so M10's D at 800 MHz through the part's relation holds.
    FAIL: it does not.
  - **A2-R2** PASS: rank 2's three lines all hold for M10 carried on new kinds. FAIL: the record names the line that failed.
  - **A2-F1, A2-F2** PASS: the burst clock's rms on a new pool is no worse than Q140(l)'s end-to-end held-out clock error, for governed or
    pinned bursts. FAIL: worse than held out.
  - **A2-W1, A2-W2** PASS: the board's rms is no worse than those cells' held-out board error. FAIL: worse.
  - **A2-H1** PASS: aifoundry2's burst heat law (0.1400 °C/W, unchanged) holds on new kinds within its held-out error. FAIL: worse.
  - **C0-W** PASS: card 0's board under its own governor, through κ0 and the session's zeros level, is no worse than aifoundry2's
    end-to-end pinned error. FAIL: the card term does not carry M10's D to card 0 that well.
  - **C0-B** PASS: no resolved board level (|mean| ≤ 0.5 W) and rms ≤ 1.0 W on card 0. FAIL: a level or a spread the card term misses.
  - **C0-F** PASS: card 0's burst clock is no worse than aifoundry2's pinned end-to-end clock error. FAIL: worse; card 0's governor does
    not pin as aifoundry2's does.

## A2-6. Wording, datelines and counts (faults 5, 8, 9 and 10), and section 8's parenthesis on E163

- **(a) "The 62"** (the registration's line 14, "the 62 inputs no earlier hash list named"; and `3e97f583`'s message, which cannot
  change).
  - Section 9's wording is the right one: the 62 are the files M10's chain opens that neither M10's registration's 174 nor M10's own 68
    named.
  - 60 of them are pool-6 and pool-7 tile files that blind6's and blind7's `SHA256SUMS` already name. Only `counts-v2.json` and
    `predictions-e145.json` were in no hash list.
- **(b) A1's dateline** ("about 23:26-23:30 PST"): A1 was last written at 23:26:28 and committed at 23:26:44 (`8a8fa34c`).
- **(c) The predictor's data directory**, `docs/reports/data/2026-11-05-q142p-pool8-predictor/`, holds work of Wed 4 Nov PST: it was
  born at 23:15:35 and committed at 23:30:18. The lab dates a data directory by the day its work happens, so the name is a day late. The
  path is frozen and stays, and the records say 4 Nov PST. This fix pass's files in it are Thu 5 Nov's.
- **(d) The development runs.** The registration's section 12 says the design arithmetic and the file trace ran "one job each". The
  predictor's README says "three passes of the self-test (23:21-23:24 PST) and one of a CLI smoke ... outputs only in the lane's
  scratch", and "the committed self-test is the run after the last code change". The round's slot log holds 11 jobs that name the
  lane's paths:

  | job | times (PST) | what happened |
  |---|---|---|
  | the design script | 22:58:58, from scratch; 23:07:35, the committed copy | ran twice |
  | the file trace | 23:00:38; 23:00:49 | the first exited 127 before running (no `timeout` at the path it named) |
  | the self-test, development runs | 23:21:27; 23:22:17; 23:23:55 | all three failed. The first wrote no output; the other two failed T8 alone, because the predictor's own list did not yet exist |
  | the CLI smokes | 23:24:54; 23:25:51 | two, not one |
  | the self-test, written into the committed path | 23:28:08-23:28:16; 23:28:46-23:28:54 | both passed. The first was overwritten by the second, which is the committed output |

  - The last code change was at 23:27:47, so both passing runs ran the committed code.
  - Only the design script and the trace ran before the registration's commit, and both are disclosed. No registered criterion changed.
  - The first pass's result said 12 slot jobs.
- **(e) Section 8's parenthesis** "(post hoc, E163 against E141 read a level)" overstates.
  - With both terms fitted, the level reads +0.11 W.
  - The registered test on those committed differences (k 1, n 7) reads NOT SEPARATED: F_level 2.60 against 6.61, and the level's 95%
    interval is −0.066 to +0.289 W.
  - Its null is rejected: the sessions differ, and the form is unresolved (`design-power-groups.txt` § 4; post hoc, design only).
  - The expectation itself, "LG LEVEL or NOT SEPARATED", stays as written.

## A2-7. What supersedes what, and the order

1. This note, `pool8/design_power_groups.py` and `pool8/design-power-groups.txt`, in one commit, before any output A2 governs.
2. The next commit, new files in the predictor's directory:
   - `predict_pool8_a2.py`;
   - its self-test's output, `selftest-pool8-a2.json` and `.txt`. That self-test re-runs the frozen T1-T9 unchanged and compares them
     with `selftest-pool8.json`, then tests A2-1 to A2-4 on committed data;
   - its hash list, `SHA256SUMS-a2`;
   - a dated note beside the predictor's README, `README.md.dated-note-1.md`.
3. These stay as committed: `predict_pool8.py`, its README, `SHA256SUMS` (16), `selftest-pool8.json` / `.txt`, `design_power.py`,
   `design-power.txt`, the registration and A1.
4. `predict_pool8_a2.py` imports `predict_pool8.py` after checking it against `SHA256SUMS`, and its `predict` and `plan` give the same
   predictions bytes. It supersedes three things:
   - the frozen command line, for the exit status of A2-2's two stops;
   - the frozen `burst` mode on card 0, for the M10 block's band (A2-1); on aifoundry2 its output is the frozen one's;
   - the frozen `intervals` mode (A2-3 and A2-4), whose P1-P3 lines it gives unchanged.

   `scale`, `primary` and `heat-minutes` pass through unchanged.
5. The (x) lane does everything section 10 says, with `predict_pool8_a2.py` in place of `predict_pool8.py`. Its `intervals` output (every
   line, and LG's block per 600 MHz card) is committed with the predictions, before any claim.

## Compute

The design script ran twice through the round's local slot, at nice 10, about 40 s each. The second run wrote the committed output,
byte-identical to the first. No lab box, no `run_remote`, no card.
