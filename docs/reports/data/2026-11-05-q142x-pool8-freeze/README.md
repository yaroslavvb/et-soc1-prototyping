# Q142(x): pool 8's predictions frozen - M10 primary and M9 beside on four cards, term b counted by the convergence rule on every float tile, the pool and its blind8.json, all committed before any card claim

*Thu 5 Nov 2026 (week 45), desk only: no card, no device command, no lab box, no post in the lab's channel, no Modal, no archive. The
work ran from 01:24 PST (the lab clone pulled at `37f11663`) to this directory's commit; this file was written from about 02:25 PST.
**Dated note A1 beside the pool's design ([`DESIGN.md.dated-note-1.md`](../../../../tools/claims-v3/kinds/blind8/DESIGN.md.dated-note-1.md)),
with the blind8.json converter and its pool-7 round trip, was committed and pushed (`ebf68c52`, 01:38:29 PST) before `blind8.json`, any
bench count of a pool-8 tile or any pool-8 prediction existed.** It answers the Q142(r)/(p)/(d) critic's `next` **rank 1** (its `pool8`
field, steps 1-7, in order) and its faults 1 and 4, for the kinds page's
[section 11](https://spacesheep.dev/@yaroslavvb/horace-kinds-of-numbers#11-what-is-still-open), **item 6** (a power model across kinds),
with items 8 and 9 (heat). The owner's goal, in his words of 2 November 2026: to predict the power requirement and heat generation of
numeric computations as accurately as possible. Where it ran: the bench counts on the mini (a Mac, arm64, Verilator 5.052, `-fno-dfg`;
Q141(t2)'s recorded build, as M10 used it, its binaries re-hashed equal to its record; one chunk at a time, 4 jobs, each call capped in
memory and time); everything else on the Intel, Python through the round's local slot, one job at a time.*

## Results

**1. Pool 8 is in the tree, unchanged, and the frozen predictor reads it.** The designer's 90 files are copied into
[`tools/claims-v3/kinds/blind8/`](../../../../tools/claims-v3/kinds/blind8/) beside `DESIGN.md` and `make_blind8.py` (`153b720f`):
every file's sha256 equals the designer's copy, the pool's own `SHA256SUMS` passes (89), and `make_blind8.py check` reads "checked 64
tiles: 0 problems" ([`pool-copy-check.txt`](pool-copy-check.txt)). `blind8.json` was then written by the committed converter
(`blind8_json.py convert`, 01:38:42 PST; 64 tiles; its sha256 `370d8a97…`), and the predictor's own functions read exactly what dated
note A1-3 requires
([`sets-blind8.json`](../../../../tools/claims-v3/kinds/blind8/sets-blind8.json), PASS):

| what the predictor reads | read | required |
|---|---|---|
| the manifest | `blind8.json` | `blind8.json` |
| roles | zeros 3 (from the bytes), scale 6, check 3 (the role field) | 3 / 6 / 3 |
| N1 | 31: fp32 11, fp16 8, int8 12 | the same |
| F1, I1, RR, KA | 19, 12, 12, 2 | the same |

Beside them: RR's int8 part 0, pool 8's float scale anchors 4, the zeros anchors 3 and 9 tiles of priority 2. With no counts given,
`predict_pool8_a2.py plan` exited 0 ([`plan-0.json`](plan-0.json)): 45 float tiles, 3 complete from committed points (the re-runs
`fp16.b_onebit_b8_pi` at N 81, `fp32.b_onebit_b20_one` at N 81, `fp32.a_onebit_b5_third` at N 9), 345 points for the next step; int8 0 of
19, as the critic forecast.

**2. Term b's counts: every float tile reached its N; none is above the bound.** 906 bench points in four steps, each step's points
named by the frozen predictor's `plan` ([`plan-1.json`](plan-1.json) … [`plan-4.json`](plan-4.json)):

| step | what | points | outcome (plan after the step) |
|---|---|---:|---|
| 1 | the 31 new float tiles at N = 9; 9 re-runs and the 2 float floors to N = 9; int8's own three points on all 19 int8 tiles | 402 | 38 of 45 float tiles meet e(N) <= 0.10 W; int8 19 of 19 |
| 2 | 7 single-bit tiles to N = 27 | 126 | 41 of 45 |
| 3 | 4 to N = 81 | 216 | 44 of 45 |
| 4 | `fp32.s8_onebit_b19_c11b3dd2` to N = 243 | 162 | 45 of 45; e(243) = 0.077 W |

- **Final N:** 36 tiles at 9, 3 at 27 (`fp16.s8_onebit_b10`, `fp32.s8_onebit_b13` with A other than 1.0, `fp32.s8_onebit_b14`), 5 at 81
  (`fp16.s8_onebit_b4`, `fp16.s8_onebit_b7`, `fp32.s8_onebit_b18`, and the re-runs `fp16.b_onebit_b8_pi` and `fp32.b_onebit_b20_one` from
  committed points), 1 at 243 (`fp32.s8_onebit_b19`). Three new single bits met the bound at 9: fp32 bits 7 and 26 (the exponent bit) and
  fp16 bit 2.
- **What the counting changes** (three-point average minus the N-point average, W of D at M9's float prices, the predictions' `recount`):
  `fp32.s8_onebit_b18` **+0.495**, `fp32.b_onebit_b20_one` +0.374, `fp16.s8_onebit_b10` +0.219, `fp16.s8_onebit_b7` **−0.337**,
  `fp32.s8_onebit_b19` −0.207, `fp32.s8_onebit_b13` −0.149, `fp16.b_onebit_b8_pi` −0.134; every other float tile within ±0.055 W (the
  next are `fp32.u8_bimodal` +0.055, `fp32.r8_dsqwen_l1_qk` −0.053 and `fp16.real_qwen_dequant_v` −0.042). That is where M10 (N-point
  counts) and M9 (three-point counts) differ on new kinds.
- **The bench:** C checked at every point, 0 mismatches; every run record carries the committed driver's sha256 (`497bffd0…`); 2,288 s
  of wall on the mini at 4 jobs (2.5 s a point; about 2.5 bench-hours), 01:41:55-02:21:54 PST.

**3. The build checks pass.** One new pool-8 float point (`fp32.s8_onebit_b13_41783e4a_A40080727` at n0 30525) counted on the mini's
build and on the Intel's is identical in every field ([`bench/check-b1.json`](bench/check-b1.json)); the int8 floor's three points counted
on the mini equal pool 7's committed Intel count of the same bytes in every field ([`bench/check-i1.json`](bench/check-i1.json)); and the
step's own counts of those points equal the checks' ([`bench/check-d-intel.json`](bench/check-d-intel.json),
[`check-d-mini.json`](bench/check-d-mini.json), [`check-d-i8-mini.json`](bench/check-d-i8-mini.json),
[`check-d-i8-pool7.json`](bench/check-d-i8-pool7.json)).

**4. The predictions, on four cards, frozen** (`predict_pool8_a2.py predict`, exit 0 on each; never `predict_pool8.py`): in
`tools/claims-v3/kinds/blind8/`, [`predictions-pool8-aifoundry3.json`](../../../../tools/claims-v3/kinds/blind8/predictions-pool8-aifoundry3.json),
[`-aifoundry1c1.json`](../../../../tools/claims-v3/kinds/blind8/predictions-pool8-aifoundry1c1.json),
[`-aifoundry2.json`](../../../../tools/claims-v3/kinds/blind8/predictions-pool8-aifoundry2.json) and
[`-aifoundry1c0.json`](../../../../tools/claims-v3/kinds/blind8/predictions-pool8-aifoundry1c0.json), each with its `.md` table. A re-run
writes all eight files byte for byte.
- **aifoundry3 and card 1 (600 MHz):** per tile, M10's per-op coefficient (the primary at scoring is s × the measured rate × it), **M10's
  a-priori arm** (D at s = 1 and the stated rate) with its 95% band, the three-point and pass-1 arms, M9's D at the nominal and the stated
  rate with its band, the 4.5 s die rise and band, N, e(N) and the counting correction. On N1, M10's a-priori D runs 4.33-25.08 W on
  aifoundry3 (4.17-24.11 W on card 1), and the 4.5 s rise 0.82-3.24 °C (0.78-3.09 °C).
- **M10 against M9 before any data** (both at the stated rate, on N1; a difference of predictions, not an error): aifoundry3 fp32 mean
  −0.015 W, rms 0.105 W (11 tiles); fp16 −0.037, 0.174 (8); int8 +0.005, 0.025 (12). Card 1: −0.015 / 0.101, −0.035 / 0.168, +0.005 /
  0.024.
- **Heat over minutes:** the chain's factor 1.0 is the primary and ×1.03199 the arm, in every file.
- **aifoundry2 and card 0:** M10 carried by rule E (s = 1, the nominal rate, aifoundry3's footing, term b's features) through M9's
  aifoundry2 part and on to card 0 through E170's card term, with M9's part on M9's D beside: each tile's governed fallback block (burst
  clock, board, burst D, die rise and their bands at the fallback and 54.38 °C, the group, the upper-95% peak), and on card 0 the card-0
  fallback (κ0 0.9463).

**5. aifoundry2's 82 W marks: 11 tiles are left out there, all fp32.** Their upper-95% peak (the larger of M10's and M9's) is 84.4-87.3 W:
the three random and check anchors, `fp32.r8_dsqwen_l1_qk`, `fp32.r8_granite_l3_qk`, the re-run `fp32.real_s360_l1_qk`, and all five fp32 U
tiles. The highest tile kept reads 81.88 W (`fp32.r8_granite_l3_x2up`, priority 2). Seven of the 11 are in N1, so aifoundry2 scores 24 tiles:
**3 governed** (fp16, predicted at 727-777 MHz) and 21 pinned.

**6. Every section-7 line at the planned n** ([`intervals-pool8.json`](../../../../tools/claims-v3/kinds/blind8/intervals-pool8.json),
`predict_pool8_a2.py intervals`; a verdict reads its line at the scored n):

| rule | aifoundry3 | card 1 |
|---|---|---|
| P8-P1, rms, fp32 (11) | 0.098-0.300 W | 0.098-0.308 W |
| P8-P2, fp16 (8) | 0.063-0.237 W | 0.075-0.268 W |
| P8-P3, int8 (12) | 0.101-0.249 W | 0.105-0.269 W |
| P8-B1, mean, F1 (19) | −0.097 to +0.064 W | −0.097 to +0.070 W |
| P8-B2, mean, I1 (12) | −0.105 to +0.089 W | −0.115 to +0.096 W |
| P8-C1, P8-H4 (31) | at least 27 inside | at least 27 inside |
| P8-H1 / H2 / H3, 4.5 s heat | 0.104-0.248 / 0.083-0.225 / 0.116-0.261 °C | 0.179-0.431 / 0.163-0.455 / 0.091-0.212 °C |
| P8-M1 (31), M1f (19), M1i (12), A1 (19) | paired, no line before the data | the same |
| P8-KA | 2 a session (1 needed), 4 pooled | the same |

- **On aifoundry2: P8-A2-G, A2-Bg, A2-F1 and A2-W1 are NOT SCORED at the planned n** (their governed group holds 3 tiles, under its
  minimum of 8), so A2-R2 (rank 2 on M10 carried) is NOT SCORED too. Scored: A2-Bp (21, the fixed line), A2-F2 (0.174-4.540 MHz), A2-W2
  (0.528-1.113 W), A2-M1 (24, paired) and A2-H1 (24, 0.491-0.870 °C).
- **On card 0** (31 scored): C0-W 0.574-1.066 W, C0-F 0.245-4.489 MHz, C0-H1 0.235-0.450 °C, C0-B the fixed line, C0-M1 and C0-HK paired;
  M10's card-0 rise band ±0.593 °C (reported, A2-1).
- **HM** is expected NOT SCORED: pool 8's planned sessions hold nothing.

**7. LG's block is the critic's forecast, exactly.** aifoundry3: E153's 8 re-runs (D_ref 1.355-21.878 W) and E163's 4 (9.854-24.814 W),
k 2, n 12, df (2, 8), F point 4.459; a 0.6% gain reads GAIN in **76.4%** of draws and a 1.0% gain in 94.6%; a 0.11 W level reads LEVEL in
**90.0%** and 0.15 W in 94.8%; no difference reads NOT SEPARATED in 93.6%. Card 1: E157's 8 (1.42-21.17 W) and E164's 4 (9.43-23.86 W),
**73.0%**, 94.6%, **89.7%**, 94.5%, 92.8%. The forecast (A1-3, committed before the intervals existed) was 76.4% / 90.0% and 73.0% /
89.7%: no difference to explain (the forecast's text, quoted in A1-3, rounds E153's lowest D_ref to 1.36 W; it is 1.3546 W,
`fp32.a_zeros_b_complement`). No re-run lacks a reference, and none has two.

## What it does to predicting power and heat

- **The blind test of M10 is frozen as registered.** Before any card measures pool 8, M10's and M9's predictions for its 64 tiles on four
  cards are committed, with every rule's line. When a card day runs it, M10's held-out figures (floats 0.185 W; pool 7's 48 kinds 0.205 /
  0.187 W against M9's blind 0.278 / 0.273 W; int8 0.177 W; the 4.5 s law per card) become blind figures on kinds drawn by a designer who
  saw no model's errors. Until then nothing new is measured and no accuracy figure changes.
- **Term b on new single bits.** The counting moves seven tiles' D by 0.13-0.50 W at M9's prices (result 2), the size of M10's and M9's
  held-out errors; elsewhere it moves D by at most 0.055 W. So M1f (M10 against M9 on floats) has tiles where the two models differ by more
  than their noise, and M10's a-priori arm differs from M9 by 0.10-0.17 W rms on floats and 0.02 W on int8 (result 4): M1i is expected NOT
  RESOLVED, as registered.
- **aifoundry2:** pool 8 cannot test rank 2's governed-clock line (A2-G) or the governed board level (A2-Bg): the tiles that would run
  governed are the hot fp32 ones, and the 82 W rule leaves them out. The pinned bursts, M10 against M9 on the board (A2-M1) and the burst
  heat law (A2-H1) are tested on 21-24 tiles.
- **Heat:** the 4.5 s rise is predicted per tile on both 600 MHz cards (H1-H4 at n 8-31) and card 0's burst rise through M10's 0.2415 °C
  per board W (C0-H1); heat over minutes stays the chain unscaled (primary) with the ×1.032 arm, unscored here.
- **LG's power at the pool's own design:** 76% / 73% for a 0.6% gain and 90% for a 0.11 W level, so one session per 600 MHz card can
  likely say whether term a's float excess is a gain in D or a session level.

## Checks

- The 12 earlier hash lists pass after this lane, from the committed blobs and the work tree: blind7 91, blind6 80, e168 9 and 18,
  predict_q140e 26, M10's registration 174, M10 68 and its SHA256SUMS-a2 10, POOL8-SHA256SUMS 209 and -62 62, the predictor's SHA256SUMS
  16 and -a2 9.
- The converter's round trip on pool 7: 61 of 61 tiles give blind7.json's read fields, and the predictor reads the same roles and sets
  from both manifests ([`roundtrip-blind7.json`](../../../../tools/claims-v3/kinds/blind8/roundtrip-blind7.json)).
- The facts A1-5 records about the designer's six faults ([`a1-checks.txt`](../../../../tools/claims-v3/kinds/blind8/a1-checks.txt)):
  the generator's sha256 `fee9a4f0…a76d14ea` in the TEST pool's provenance at 23:18:39 PST, equal to the committed file; the two `hold`
  re-runs measured in E153 (4 passes; 9.443 and 13.317 W) and E157 (3 passes; 8.964 and 12.827 W), 40 C-checked launches each, all PASS;
  a rebuild identical in 88 of 90 files; DESIGN.md last committed at 23:22:03; the seed `0x1da1fde559d92805` from `c996d135`, an ancestor.
- In sample only, a sanity reading (not a score): M10's a-priori D on the 12 re-runs sits 0.229 W rms (aifoundry3) and 0.207 W (card 1)
  from their reference sessions' measured D. These tiles trained M10, and s = 1 leaves each reference session's own scale in place.

## Registered, and what happened

- **As registered** (POOL8-REGISTRATION.md sections 2, 4, 5, 7 and 10; A1 and A2 beside it; dated note A1 beside DESIGN.md): the pool
  copied unchanged; `blind8.json` by the committed rule; the predictor's reading checked before any count; term b by RECOUNT-RULE.md's e(N) on
  every fp32 and fp16 tile from the plan's own points, with committed points reused by bytes; int8's own three points; C at every point;
  the build checked against the Intel's on one new point; `predict_pool8_a2.py` on the four cards; the intervals; one commit before any
  claim.
- **Departures, named:**
  - `make_blind8.py check` ran under `python3.10 -I` (the designer's interpreter, numpy 1.24.2): the Intel's `python3` has no numpy under
    `-I`. The generator's docstring says `python3 -I`; the critic's step says `python3.10 -I`.
  - The bench driver was written after A1 and committed with the counts, not before them. A1-4 (`ebf68c52`) gave its rule before any
    count, and every run record carries its sha256, equal to the committed file's.
  - Development runs, disclosed: the converter's round trip and A1's checks ran once into the scratch (01:34:58, 01:35:55 PST) before
    their committed runs; the converter was then edited once (a variable renamed for the public-text scan) and its two outputs re-run
    (01:38:19) before `ebf68c52`; the committed outputs are the re-run's. One `predict` on aifoundry2 ran at 02:06:43 on the counts after
    step 2, with 4 float tiles short of their N, as a smoke test of the governed path: it refused (exit 3) and wrote nothing.
  - The int8 floor's three points were counted twice on the mini (the build check and step 1); both equal pool 7's committed count.
  - The pool's own text files carry 14 matches of the public-text scan's credentials word list. Every one is the language-model word for
    a text position, in the real tiles' description of activations quantised one text position at a time (their provenance and README);
    none is a credential. They are committed unchanged, as the pool must be.

## What this cannot say

- **Nothing here is measured.** These are predictions; the blind test needs the card day (E171-E174), which waits on the owner's word and
  fresh lab approvals.
- **M10's primary needs each session's own anchors.** Only the a-priori arm (s = 1, the stated rate) is frozen in full before a session.
- **aifoundry2's governed rules** (A2-G, A2-Bg, A2-F1, A2-W1, hence A2-R2) get no test from this pool at the planned design.
- **Term b's counts are the bench's** (one minion's vector unit in Verilator), and e(N) is priced at M9's float prices.
- **Card 0** carries M10 through E170's card term, fitted on one session; its burst-heat k rests on that session too.

## For the card lanes (E171-E174)

- A run's registration descends from this directory's commit and from `ebf68c52`, and names both.
- **What it reads:** its card's predictions file (frozen; listed in [`SHA256SUMS`](SHA256SUMS)) and `intervals-pool8.json`; at scoring, the
  predictor's `scale` then `primary` (600 MHz) or `burst` (aifoundry2 and card 0) on the session's own reads, as registered.
- **aifoundry3 and card 1 (600 MHz):** E78's `fp32.randn`, `fp16.randn` and `int8.full` plus the 64 tiles in every pass, every launch
  C-logged.
- **aifoundry2 (its own governor):** the 11 tiles marked `admission_82w_out` are left out there.
- **Card 0:** E170's admission and its 66 W one-sample / 72 °C stops apply; the predictions hold no card-0 admission. M10's highest
  card-0 burst D is 30.1 W, on fp16 tiles at about 731-733 MHz, before the session's zeros level is added.

## Files

| file | what |
|---|---|
| `README.md` | this file |
| `pool-copy-check.txt` | the pool's copy: 90 sha256 equal, and `make_blind8.py check`'s output |
| `plan-0.json` … `plan-4.json` | the frozen predictor's `plan` before any count and after each step |
| `predict-<card>.log` | each `predict` run's printed table |
| `bench/bench_pool8.py` | the bench driver (A1-4) |
| `bench/counts-x-s<k>-<chunk>.json`, `-run.json`, `bench-x-s<k>-<chunk>.log` | the steps' counts (run_kinds.py's own form), run records and logs |
| `bench/counts-b1-*.json`, `counts-i1-mini.json`, `check-b1.json`, `check-i1.json`, `point-*.json`, `check-d-*.json` | the build checks and check D |
| `SHA256SUMS` | the sha256 of every new file of this lane (both commits), from the repo top |
| `../../../../tools/claims-v3/kinds/blind8/` | the pool (90 files), A1 and its files (`ebf68c52`), `blind8.json`, `sets-blind8.json`, the four predictions files (`.json`, `.md`), `intervals-pool8.json`, `README-predictions.md` |

## Re-run

From the top of the tree (the Intel's `/usr/bin/python3`, numpy 1.26):

```
python3 -B tools/claims-v3/kinds/blind8/blind8_json.py convert tools/claims-v3/kinds/blind8 --out <new file>   # equals blind8.json
python3 -B tools/claims-v3/kinds/blind8/blind8_json.py sets tools/claims-v3/kinds/blind8
python3 -B docs/reports/data/2026-11-05-q142p-pool8-predictor/predict_pool8_a2.py plan tools/claims-v3/kinds/blind8 --counts <each bench/counts-x-*.json>
python3 -B docs/reports/data/2026-11-05-q142p-pool8-predictor/predict_pool8_a2.py predict tools/claims-v3/kinds/blind8 <card> --counts <each bench/counts-x-*.json> --out <dir>
python3 -B docs/reports/data/2026-11-05-q142p-pool8-predictor/predict_pool8_a2.py intervals <the four predictions files> --out <file>
```

The counts: `bench/bench_pool8.py run <bench dir> <out> --tiles <names> (--points <n0,...> | --launch) [--build-record <record>] --jobs 4`, in
the bench's build directory (`rtl-sim/fma_toggle_v2`, built with `-fno-dfg`).

## Compute

- **The mini:** 10 bench calls (the build checks' 2, capped at 4 GB and 240 s, and the steps' 8 chunks, capped at 6 GB and 900 s), one at
  a time, 4 jobs at most; 910 points in all. No lab box was used, and no sign-in link appeared.
- **The Intel:** 18 jobs through the round's local slot, one at a time, each under a minute: the check, the round trip and A1's checks
  (with their development runs), `blind8.json` and the A1-3 reading, the Intel's one bench point (20.9 s on one core at nice 10), four
  plans, the smoke `predict`, four `predict`s, the intervals and their byte-for-byte re-run. Beside them: git, hashing, the public-text
  scan and bounded copies to and from the mini.
