# Q141(t): pool 7's single high bits recounted at 27 launch points, a reported arm frozen before any pool-7 data

*Wed 4 Nov 2026 (week 45), 09:00-10:15 PST, on the Intel, desk only (no card, device command, lab box, Discord, Modal or archive).
Registered first in [`REGISTRATION.md`](REGISTRATION.md) (`0830f65b`, 09:11:50 PST), before any count it names and before any
pool-7 measurement. What happened while it ran is in [`REGISTRATION.md.dated-note.md`](REGISTRATION.md.dated-note.md). It answers
the Q140 final critic's open **rank 4** (single high bits: the bench's counting against a missing price) through its `desk_next` 6,
for the kinds page's [section 11](https://spacesheep.dev/@yaroslavvb/horace-kinds-of-numbers#11-what-is-still-open), **item 6**.
The convergence rule's 81-point step (`desk_next` 10) is [`step81/`](step81/), committed separately.*

## Results

**1. The arm `M9_27pt` is frozen for E163 (aifoundry3) and E164 (aifoundry1 card 1).** It is M9's frozen prices on 27-point counts,
and it is **reported only**: M9's frozen predictions stay primary.
- The S class's 27-point counts move M9's D by **−0.52 to +0.30 W** across pool 7's seven priority-1 single-bit tiles, and by
  **+0.39 W** on the b20-on-1/3 tile under A = 1.5.
- Over the seven, the shift is **0.29 W rms**. That is about M9's own nested float error (0.193 W, RECOUNT-RULE.md section 3) and
  the best models' blind rms over pool 6's 30 new kinds (0.24-0.32 W, the Q140 critic's `prediction_now`). For single high bits,
  the bench's three-point counting error alone is as large as the model's error.
- On average the three-point counts read these tiles **0.135 ± 0.085 W low** (aifoundry3; 0.130 ± 0.082 on card 1, 1 s.e.).
  Pool 6's b20-on-1/3, by contrast, read 0.78 W high.

| tile | e(9) | e(27) | met at 27 | aifoundry3 P3 | P27 | k ± u | card 1 P3 | P27 | k ± u |
|---|---:|---:|---|---:|---:|---|---:|---:|---|
| `fp32.b_onebit_b20_one` | 0.314 | 0.142 | no | 13.177 | 12.876 | +0.301 ± 0.142 | 12.671 | 12.382 | +0.289 ± 0.137 |
| `fp32.b_onebit_b20_full` | 0.163 | 0.127 | no | 12.219 | 12.309 | −0.090 ± 0.127 | 11.750 | 11.836 | −0.086 ± 0.122 |
| `fp32.b_onebit_b20_pi` | 0.653 | 0.198 | no | 12.093 | 12.404 | −0.311 ± 0.198 | 11.628 | 11.928 | −0.299 ± 0.190 |
| `fp32.b_onebit_b20_seventh` | 0.517 | 0.241 | no | 11.975 | 12.316 | −0.341 ± 0.240 | 11.515 | 11.843 | −0.328 ± 0.231 |
| `fp32.b_onebit_b22_third` | 0.662 | 0.392 | no | 12.914 | 13.434 | −0.520 ± 0.392 | 12.418 | 12.918 | −0.500 ± 0.377 |
| `fp16.b_onebit_b9_one` | 0.184 | 0.202 | no | 13.580 | 13.471 | +0.109 ± 0.202 | 13.058 | 12.954 | +0.105 ± 0.194 |
| `fp16.b_onebit_b8_pi` | 0.341 | 0.169 | no | 12.124 | 12.215 | −0.091 ± 0.169 | 11.658 | 11.746 | −0.088 ± 0.163 |
| `fp32.b_onebit_b20_third_a1p5` (priority 2) | 0.271 | 0.196 | no | 13.217 | 12.828 | +0.390 ± 0.197 | 12.710 | 12.335 | +0.375 ± 0.189 |

How to read the table:
- Every figure is W of D, at 600 MHz, on Q139(u)'s footing.
- P3 is M9 as frozen: the primary, from `tools/claims-v3/kinds/blind7/predictions-blind7-<card>.json`, `75802201`.
- P27 is the arm (`arm/predictions-<card>.json`).
- **k = P3 − P27** is the three-point count's error at M9's prices.
- u = s × e(27) is its 1-s.e. counting error left at 27 points, with s = 0.9616 on card 1.
- e(N) comes from RECOUNT-RULE.md's rule, at M9's prices on aifoundry3's footing.

The full record is [`arm-s7.json`](arm-s7.json), with [`arm-s7.txt`](arm-s7.txt) as a table. The hand-off form that
`tools/claims-v3/e163/score_e163.py --arm27` reads is [`arm/arm27-aifoundry3.json`](arm/arm27-aifoundry3.json) (and
`arm27-aifoundry1c1.json`).

**2. No S tile converges at 27 points.** e(27) is 0.127-0.392 W on all eight, against the rule's bound of 0.10 W
([`recount-s7.json`](recount-s7.json), [`recount-s7.txt`](recount-s7.txt)).
- So the arm separates counting from price only coarsely per tile. Of the seven, |k| exceeds u on 4 and 2u on 1
  (`fp32.b_onebit_b20_one`, 2.1 u).
- The class mean is better placed: −0.135 ± 0.085 W.
- The 1/√N law's planning projection puts the bound at 44-415 points per tile. This is planning only, never in place of counts;
  `step81/` measures how e(N) actually falls on the calibration tiles.
- e(9)/e(27) is 0.91-3.30 (the law gives 1.73). The two error estimates, the sample s.e. and the interleaved sub-rules, are noisy at
  these N.

**3. Every registered check passed** (`arm-s7.json` `checks`):
- **C:** all 216 counted points have `check_mismatch` 0.
- **D1:** each tile's three standard points reproduce its committed `counts-blind7.json` row exactly, and run_kinds' `mean_rows`
  reproduces the committed means.
- **D2:** `fp32.b_onebit_b20_pi`'s 27 points equal its byte twin `fp32.cal_pi_b20`'s committed 27 exactly. That is 24 repeated
  points beyond D1's, so the bench is deterministic, and its k (−0.311 ± 0.198 W) is the dated note A1-2's figure.
- **RR:** the per-tile code reproduces Q140(m)'s committed `recount-rule.json` (210 fields, 16 tiles).
- The frozen `predict_blind7.py`, run unchanged on the arm's counts, gives pool 7's other 53 tiles exactly their frozen
  predictions on both cards.
- The recorded hashes of `m9.json`, `predict_blind7.py`, `fit_m9.py` and the manifest equal the frozen files'.
- After the lane, `blind7/SHA256SUMS` 91 of 91, `frozen-sha256-e168.json` 9 of 9, `frozen-sha256-e168-scorer.txt` 18 of 18 and
  predict_q140e's 26 frozen inputs all still pass.

**4. The scorer is self-tested on the parent runs' committed data.** It is [`score_s7arm.py`](score_s7arm.py), standard library
only; its output is [`selftest-score-s7arm.txt`](selftest-score-s7arm.txt), with the JSON beside it. Verdict: PASS.
- **T1, T2:** on E153's and E157's `scored.json` with pool 6's frozen predictions (M8 primary, as registered then), the reader
  reproduces all 300 power and heat rows of each run exactly (errors to 0.0 W, inside flags 300 of 300).
  - It also reproduces the row-derived verdicts: P1 FAIL, P2 PASS, P3 PASS and C1 PASS on both runs, with their rms against the
    committed intervals.
  - And it reproduces E153's committed S-class reading: M8 0.4307 W rms, bias −0.2474.
- **T3, post hoc** (M9 was fitted on pool 6's rows): the arm's machinery on pool 6's two byte twins reproduces the recount rule's
  committed corrections exactly. k is +0.784 W for `b20_third` and −0.026 W for `b12_third` on aifoundry3, so M9's `clk` term does
  not move between launch points. M9's in-sample error on pool 6's b20-on-1/3 goes −0.720 → +0.064 W on aifoundry3 and
  −1.005 → −0.251 W on card 1.
- **T4:** known-answer rows built from the arm's numbers give COUNT, PRICE or COUNT+PRICE, or NOT SEPARATED, where they must.

**5. Heat.** Through M7's law (which M9 carries), the arm moves M9's 4.5 s die rise by −0.061 to +0.046 °C on these tiles. That is
small beside the heat band, so counting barely matters for these tiles' heat prediction.

## What it does to predicting power and heat

- **What it tests:** the bench's launch average (counting) against a single-bit price, on the S class. Q140(m)'s correction C1 left
  that split open, and the Q140 critic's rank 4 asks for it.
- **What it makes scorable:** E163's and E164's S-class blind errors can be split into a counting part k (frozen now, ± u) and a
  price part r27 = D − P27, read by REGISTRATION.md section 3's R1-R6 through `score_s7arm.py`.
- **Error before and after:** there is no out-of-sample error yet, because no pool-7 data exists. Before the data, the counting part
  alone is 0.29 W rms over the seven S tiles, and still uncertain by 0.13-0.39 W a tile at 27 points.
- **What it does not change:** no frozen prediction, band, rule or verdict. M9 stays primary on every tile, and E163's and E164's
  registrations are their own.
- **For the next model:** a single-bit term fitted on three-point counts would partly fit the bench's quadrature. A term fitted on
  27-point counts would still carry 0.13-0.39 W of counting error on rows like these. The next step's figures are in `step81/`.

## What was registered and what happened

Everything in REGISTRATION.md sections 1-3 ran as registered, with three things it did not foresee (dated note, about 10:05 PST):
- The session reniced the bench from nice 10 to 20 about 8 minutes into the run. That is gentler and slower (2,720 s for 216 points),
  and changes no count: D1 and D2 hold.
- `bench_s7.py` crashed after the bench had finished, on `os.nice(0)` (EPERM), so its run record is reconstructed and marked so.
  The 81-point step runs it unchanged through `bench_s7_run.py`.
- The arm's builder briefly used a fifth core while the 81-point step's 4 bench jobs ran.

REGISTRATION.md section 2 named its three departures from RECOUNT-RULE.md section 6 before the counts:
- the recount comes before pool 7's data, not after;
- N is fixed at 27;
- the standard points are counted again.

## Files

| file | what |
|---|---|
| `REGISTRATION.md`, `bench_s7.py` | the registration and its bench driver (`0830f65b`) |
| `REGISTRATION.md.dated-note.md`, `bench_s7_run.py` | what happened while it ran; the driver's safe wrapper |
| `counts-s7-27.json`, `bench-s7-27.log`, `counts-s7-27-run.json` | run_kinds.py's 27-point counts of the 8 tiles, its log, the run record (reconstructed) |
| `make_arm_s7.py` | the arm's builder and its checks |
| `counts-arm-s7.json` | pool 7's 61 count rows, with the 8 S rows' mean at 27 points |
| `arm/predictions-<card>.json`, `.md` | the frozen predictor's output on them |
| `arm/arm27-<card>.json` | `{tile: P27}`, the form score_e163.py's `--arm27` reads |
| `arm/pool6-twins/` | the same predictor on pool 6, with three-point counts (`3pt/`) and with its two byte twins at 27 points (`27pt/`): post hoc, R6's and T3's input |
| `recount-s7.json`, `.txt` | e(9) and e(27) per S tile by the registered rule |
| `arm-s7.json`, `.txt` | P3, P27, k, u, the die rise, the other models' k, the checks, the hashes |
| `score_s7arm.py`, `selftest-score-s7arm.txt`, `.json` | the scorer and its self-test |
| `step81/` | the convergence rule's 81-point step (its own commit) |

## Re-run

Run these from the top of the tree. The bench needs a build of `rtl-sim/fma_toggle_v2` whose seven files hash as
`../2026-11-04-q140m-m9/bench-check/bench-sha256.txt` (Q133(b)'s build). The predictor needs numpy: here macOS's `/usr/bin/python3`
3.9 with numpy 1.26.

```
python3 -B docs/reports/data/2026-11-04-q141t-s7-recount/bench_s7_run.py <bench build> s27 docs/reports/data/2026-11-04-q141t-s7-recount/counts-s7-27.json --jobs 4
python3 -B docs/reports/data/2026-11-04-q141t-s7-recount/make_arm_s7.py
python3 -B docs/reports/data/2026-11-04-q141t-s7-recount/score_s7arm.py --selftest
python3 -B docs/reports/data/2026-11-04-q141t-s7-recount/score_s7arm.py --a3 <E163 scored.json> --c1 <E164 scored.json> --out <score.json>
```

The bench takes about 45 minutes at 4 jobs on a loaded Intel. The builder rewrites every output byte for byte from the committed
counts.
