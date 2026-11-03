# E140: blind pool 4 on the card - the power-and-heat model M6 against 25 tiles its designer never fitted (Q137, aifoundry3 card 0, 600 MHz)

*Pre-registered Mon 2 Nov 2026 (week 45), on the Intel, before the claim of aifoundry3 and before any card has run a tile of the pool,
in Q137 (the owner's words that afternoon: "The overall goal is to be able to predict the power requirement and heat generation of
various kinds of numeric computations as accurately as possible"). **It answers item 6 of the kinds page's section 11**, "a power
model across kinds" ([horace-kinds-of-numbers § 11, item 6](https://spacesheep.dev/@yaroslavvb/horace-kinds-of-numbers#11-what-is-still-open)),
and is the out-of-sample test Q137(m)'s README names for itself ("E140 is the test"). **Every prediction E140 scores is Q137(m)'s,
frozen before this was written**: the pool [`../kinds/blind4/`](../kinds/blind4/README.md) (`67fe20a9`, 15:33 PST, before any M6 fit),
the model [`m6.json`](../../../docs/reports/data/2026-11-02-q137m-model/m6.json) (`6a713a9f`, 15:56 PST), and its predictions for the
pool, power and die rise, [`predictions-blind4.json`](../kinds/blind4/predictions-blind4.json) (`03fcd720`, 16:06 PST). E140 adds no
prediction. What it adds is frozen in [`predictions-e140.json`](predictions-e140.json), written by
[`make_predictions_e140.py`](make_predictions_e140.py) through [`m6_inputs.py`](m6_inputs.py) from the committed files it names, every
number read from its file and each file's sha256 recorded: the hashes it refuses to run without, the plan, the rules and the reference
errors behind them. Any change after this commit goes in Amendments, dated, before the data it touches. Card: **aifoundry3 card 0
only**, 600 MHz as its boot-time TDP of 0 latches it, TDP 0 / threshold 65 °C as read, never set. **E140 sends no write command of
any kind** (§ Device commands sent).*

## What it does to predicting power and heat

M6 is the lab's whole prediction of a matmul kernel's power and heat from the bytes it multiplies: **power** D, board W over the
type's own zeros at 600 MHz, from the bench's gate-level counts plus per-flip and gate-state terms; **heat**, the die's rise over a
4.5 s run from launch, 0.118 °C per board W of S (= D + the zeros' S) on this card. Its accuracy so far is a nested
leave-one-kind-out score on 22 experiments it was fitted on: 0.227 W (fp32), 0.179 W (fp16), 0.260 W (int8); heat 0.304, 0.283,
0.175 °C (Q137(m) README, § 1 and § 3). **E140 measures the out-of-sample error on kinds no fit ever saw, written by a designer who
never saw the model**, and asks whether that score holds: R1/R2 test the rms error against the interval the nested score implies for
that many tiles, R3 tests whether M6's own 95% intervals cover what they claim. The numbers it reports are the before/after the
owner's goal needs: the nested estimate (before) against the blind rms (after), per format and for each of power and heat, with M5's
frozen power predictions beside M6's on the same tiles (M6 is resolved better than M5 for fp16, not for fp32, resolved worse for
int8, by the nested score). A PASS says the stated error bars can be quoted for new kinds; a FAIL says where they cannot, by case.

## The question

1. **Is M6's power as accurate on the blind pool as its nested score says?** Floats (P1) and int8 (P2).
2. **Is its heat as accurate?** Floats (H1) and int8 (H2): the die rise over each run's window, the quantity M6's heat term predicts.
3. **Do its frozen 95% intervals hold?** Power (P3) and heat (H3).

## The models and the pool, frozen elsewhere

| what | file | sha256 | frozen in |
|---|---|---|---|
| the pool: 25 tiles (11 fp32, 7 fp16, 7 int8; 20 priority 1), by an independent designer | [`blind4.json`](../kinds/blind4/blind4.json), `SHA256SUMS`, `tiles/` | `0bf9526f…`, recorded in `predictions-e140.json` | `67fe20a9` |
| M6 (floats `G6_gtr_psgn_fields`, int8 `J1_gtr`, heat `H2_per_card_runlength`) | [`m6.json`](../../../docs/reports/data/2026-11-02-q137m-model/m6.json) | `87c17e08…` | `6a713a9f` |
| its nested scores | [`loko-m6.json`](../../../docs/reports/data/2026-11-02-q137m-model/loko-m6.json) | `1fd26042…` | `6a713a9f` |
| every power row's nested error (post hoc to the freeze, before E140; "nothing frozen changes") | [`bootstrap-m6.json`](../../../docs/reports/data/2026-11-02-q137m-model/bootstrap-m6.json) | `636faf42…` | `03fcd720` |
| M6's and M5's predictions for the pool, power and heat, with 95% intervals | [`predictions-blind4.json`](../kinds/blind4/predictions-blind4.json) | `a58f0dc4…` | `03fcd720` |

`make_predictions_e140.py` refuses unless `predictions-blind4.json` names the committed `m6.json`'s sha256; `run_e140.py`,
`reduce_e140.py` and `run_e140.sh setup` check the pool's files and every tile again.

**The independence of the pool** (its README, § Independence): the designer read only `tools/claims-v3/kinds/README.md` and
`make_kinds.py` (lines 1–851), no model, prediction, data README or earlier pool; one directory listing showed file names, none
opened. The pool was committed before any M6 fit ran. **The model and E140's scoring were written by different lanes** (Q137(m) and this
one); Q137(m)'s own README says one lane wrote its model and its scoring code, which is not E140's. After its first fit was read,
Q137(m) changed its heat rows (runs of 5.0 s or less) and its heat "before" (README, Order 5), post hoc on its training data, never on
the pool. So the pool's independence is fully met, where E115's was half met (its pool's designer had read the model's commit subjects).

**The footing.** D as E78's reduction reads it on this card, the card M6's predictions are written for (`a3`), with no scale. E115's
anchor footing needs the model's prediction of each type's random anchor; `predictions-blind4.json` gives none, so **E140 has no anchor
footing** (a departure from E115, decided here, before data). The session's own anchors are reported against E115's and E78's.

**Heat: what is measured.** M6's heat term predicts `dT_win`: "the die reading at the window less the launch reading" over the kinds
harness's run (Q137(m) README, § How it was done, Heat rows), the field E78's `reduce_e78.py` writes for every run. E140 reads it per
tile and pass from the reduction (`per_pass[pass][tile].dT_win`) and averages over kept passes. Runs launch at 58 °C after a 2.0 s quiet,
4 s each, as in M6's training rows (whose runs of 4.4–5.0 s fitted the run-length slope; E140's are inside that range by construction).
The long-hold figures in `predictions-blind4.json` (60 s, 300 s, plateau) are quoted, not scored: no run here holds.

## The frozen predictions

D in W over the type's own zeros, and the die rise over the run in °C, aifoundry3 card 0, 600 MHz; each with M6's 95% interval
(power: 1.96 × the type's nested rms on this card in quadrature with the constants' jackknife covariance; heat: from M6's nested
heat rms), copied from `predictions-blind4.json` by `m6_inputs.py`; M5's power prediction beside (reported only).

| tile | case | prio | M6 D, W [95%] | M5 D, W | M6 die rise, °C [95%] |
|---|---|---:|---|---:|---|
| `fp16.a_hi_busy_lo_const` | 3 A with a busy partner | 1 | **20.48** [20.14, 20.82] | 20.43 | **2.66** [2.10, 3.21] |
| `fp16.band_local` | 4 partial sparsity | 2 | **2.92** [2.55, 3.29] | 3.11 | **0.58** [0.02, 1.13] |
| `fp16.block_sparse_37` | 4 partial sparsity | 1 | **12.14** [11.80, 12.47] | 11.93 | **1.67** [1.11, 2.23] |
| `fp16.pair_cancel` | 1 signs on moving sums | 1 | **16.82** [16.46, 17.18] | 16.62 | **2.22** [1.67, 2.78] |
| `fp16.real_pythia_embed_qkv` | 5 real model | 1 | **22.23** [21.90, 22.56] | 22.16 | **2.86** [2.31, 3.42] |
| `fp16.real_qwen_ln_down` | 5 real model | 1 | **20.26** [19.91, 20.61] | 20.32 | **2.63** [2.08, 3.19] |
| `fp16.wideexp_gate30` | 2 spread exponents under a gate | 1 | **13.34** [13.00, 13.68] | 13.14 | **1.81** [1.26, 2.37] |
| `fp32.a_const_b_busy` | 3 A with a busy partner | 1 | **19.23** [18.71, 19.75] | 19.22 | **2.51** [1.92, 3.11] |
| `fp32.a_exp_busy_b_const` | 3 A with a busy partner | 2 | **12.19** [11.68, 12.69] | 12.19 | **1.68** [1.08, 2.27] |
| `fp32.b_3of8_k` | 4 partial sparsity | 1 | **11.18** [10.69, 11.68] | 11.06 | **1.56** [0.96, 2.15] |
| `fp32.cancel_pairs` | 1 signs on moving sums | 1 | **24.34** [23.85, 24.84] | 24.39 | **3.12** [2.52, 3.71] |
| `fp32.denormals_only` | own choice (surprise) | 1 | **11.56** [11.02, 12.09] | 11.39 | **1.60** [1.01, 2.20] |
| `fp32.real_pythia_embed_qkv` | 5 real model | 1 | **19.70** [19.21, 20.18] | 19.79 | **2.57** [1.97, 3.16] |
| `fp32.real_qwen_q_down` | 5 real model | 1 | **18.12** [17.64, 18.61] | 18.22 | **2.38** [1.78, 2.98] |
| `fp32.rowcol_sparse` | 4 partial sparsity | 2 | **15.58** [15.08, 16.07] | 15.39 | **2.08** [1.48, 2.67] |
| `fp32.sign_drift` | 1 signs on moving sums | 1 | **23.15** [22.66, 23.65] | 23.21 | **2.98** [2.38, 3.57] |
| `fp32.wideexp_agate_rows` | 2 spread exponents under a gate | 2 | **14.18** [13.68, 14.69] | 13.85 | **1.91** [1.32, 2.51] |
| `fp32.wideexp_bgate_alt` | 2 spread exponents under a gate | 1 | **13.91** [13.40, 14.42] | 13.22 | **1.88** [1.28, 2.48] |
| `int8.a_full_b_const` | 3 A with a busy partner | 1 | **6.47** [5.95, 6.99] | 6.45 | **1.07** [0.72, 1.41] |
| `int8.b_line_flipflop` | own choice (surprise) | 1 | **4.05** [3.53, 4.56] | 4.03 | **0.78** [0.44, 1.12] |
| `int8.band_a` | 4 partial sparsity | 2 | **2.78** [2.29, 3.27] | 2.79 | **0.63** [0.29, 0.97] |
| `int8.pair_gate_37` | 4 partial sparsity | 1 | **4.35** [3.86, 4.85] | 4.34 | **0.82** [0.47, 1.16] |
| `int8.real_pythia_embed_mlpout` | 5 real model | 1 | **6.35** [5.83, 6.86] | 6.33 | **1.05** [0.71, 1.40] |
| `int8.real_qwen_q_down` | 5 real model | 1 | **6.33** [5.82, 6.85] | 6.32 | **1.05** [0.71, 1.40] |
| `int8.sign_runs_i` | 1 signs on moving sums | 1 | **5.43** [4.93, 5.93] | 5.44 | **0.94** [0.60, 1.29] |

## Decision rules

On the primary (E78's reduction unchanged: leakage `auto`, dips kept, E78's run and pass gates), over kept passes. Each tile's
measured value is its mean over the passes it ran in; a tile with fewer than 2 kept passes is left out and named. **Fewer than 2 kept
passes: every rule NOT SCORED.**

| rule | quantity | set | verdict |
|---|---|---|---|
| **E140-P1** | power D | priority-1 fp32 and fp16 tiles (14), at least 5 | rms(D − M6) against the 2.5–97.5% range of the rms of the same format mix drawn with replacement from M6's nested leave-one-kind-out errors of every power row of those formats (`bootstrap-m6.json` › `row_errors`, both cards: E115's R1 rule): **PASS** if at or below the 97.5% point, **FAIL** above it; below the 2.5% point is reported as "better than the nested score says" |
| **E140-P2** | power D | priority-1 int8 tiles (6), at least 4 | as P1, int8's errors |
| **E140-P3** | power D | all 25 | coverage: **PASS** if the number of tiles inside M6's frozen 95% interval is at least the 2.5% point of Binomial(n, 0.95) (21 of 25), **FAIL** if fewer; NOT SCORED under 10 tiles |
| **E140-H1** | die rise `dT_win` | priority-1 fp32 and fp16 (14), at least 5 | as P1, against M6's nested heat errors: no per-row heat error is committed, so a deterministic normal sample of 2,000 points with M6's nested heat rms of that format (`m6.json` › `heat.interval_pool_c`) |
| **E140-H2** | die rise | priority-1 int8 (6), at least 4 | as H1 |
| **E140-H3** | die rise | all 25 | as P3 |

**Reported, never a verdict** (`scored.json`, `results.md`): every tile's measured D and rise with its passes; M5's rms beside M6's on
each power set; each verdict at every arm (leakage 0.1994, 0.3803 and 0 W/°C; dips removed; gates off: E115's arms, `collect_e140.sh`);
the session tie and the anchors against E115's; the priority-2 tiles; the errors by case; the rise against the quoted 0.118 °C per W.

**Why these lines, before the data.** They are E115's, so the two blind tests read alike. R1/R2 ask whether the out-of-sample error is
as small as the in-sample nested score claims: the nested errors are the only honest estimate the model has, and the interval is what
they imply for that many new tiles. Power's errors have heavy tails (E115's `fp32.a_colconst_b_randn` −1.70 W is among them), so its
97.5% point is wide; heat's normal sample has no tail, so H1/H2 are the stricter test. R3 asks whether the stated intervals are
calibrated, which is what a reader quoting "D ± x" needs.

## Precision, before the data

[`planned-intervals.txt`](planned-intervals.txt), from the frozen registration, for the tiles the pool holds: **P1** 0.114–0.474 W
(median 0.185) over 14 float tiles; **P2** 0.101–0.434 W (median 0.240) over 6 int8; **H1** 0.188–0.403 °C (median 0.288); **H2**
0.080–0.271 °C (median 0.165); P3 and H3 need 21 of 25 inside. [`selftest.txt`](selftest.txt) ([`selftest_e140.py`](selftest_e140.py),
100 sessions a world on the frozen registration, three passes, 0.05 W/°C pass noise; nothing there is a measurement): when the model is
as good as its nested score (errors drawn from its own reference errors), P1 PASS 97, P2 98, P3 100, H1 100, H2 99, H3 100 of 100;
**twice as bad**, P1 still PASSES 81 of 100 and P2 46 (power's wide tails make them weak tests), while H1 FAILS 96, H2 74, P3 78, H3 95;
three times as bad, every rule FAILS in 78–100. So a power PASS means "no worse than about twice its nested score", and the coverage
rules are the sharper power test. With 0.05 W of pass noise, three passes leave a tile's mean about 0.03 W from its truth, small beside the
0.17–0.26 W being tested; the die's whole-degree readings put about
0.1–0.13 °C on an item (Q137(m) § 3's readout floor), which is inside M6's heat errors, so it is in the reference too.

**What I expect, frozen so it can be wrong:** all six PASS. The likeliest misses, named now: `fp32.denormals_only` (a flush-to-zero
datapath would make it far cheaper than its busy bits), `int8.b_line_flipflop` (whole-line flips at every boundary, no training row
like it), the A-with-a-busy-partner tiles (E115's worst cases were of that kind) and the wide-exponent gate tiles (M6's steady-gate
overprediction, its § 5).

**The statement the page gets, decided now.** All PASS: "on 25 tiles written by a designer who never saw the model, M6 predicted
power within X W rms (floats) and Y W (int8), and the die's rise within Z °C, as its nested score said it would". A FAIL is stated with
the rms, its interval and the tiles that carry it, by case. **No tile, prediction, interval, rule or reference error changes after this
commit; only tiles that ran are scored.**

## What the rules cannot say

One card, one clock, one session. The heat scored is the 4.5 s window only: the long-hold rises M6 quotes are not tested. The power
reference errors are both cards' (as E115's), the heat reference a normal model of the nested rms, not the rows themselves. A PASS
fails to find a miss at this many tiles; it does not bound M6's error on kinds unlike these 25.

## What runs

| | E115 (blind pool 3, this card, 1 Nov) | E140 | why |
|---|---|---|---|
| a run | E78's: `sparsity_host --test fma --type <t> --pattern none --values file:<tile> --shires 0xffffffff --per-shire 32 --seconds 4`, 1,024 minions, heat to 59 °C, launch at 58 °C after 2.0 s quiet | **the same** | the protocol M6's training rows were measured with |
| the tiles | blind pool 3's 25 | **blind pool 4's 25** (`tools/claims-v3/kinds/blind4/`, 67fe20a9; 11 fp32, 7 fp16, 7 int8; 20 priority 1): `tiles/<type>/<name>.bin`, items `<name>` | the pool |
| anchors | E78's six (each type's zeros and random) three times a pass, the tie `anchor_pi` first and last | the same | drift, the zeros D is measured over, the anchor footing |
| a pass | 45 runs: the tie, three segments of the six anchors and 9, 8, 8 tiles, the tie; `Random("E115\|aifoundry3\|<pass>")` | 45 runs, the same dealing, `Random("E140\|aifoundry3\|<pass>")` | |
| passes | 11510–11512, at least two kept | **14010–14013** (the budget rule decides: three fit for certain, the fourth only if passes run at E115's 455–463 s), **at least two kept** | 35 card-minutes |
| smoke | blind3.json's eight | **14001**: the tie, `fp32.cancel_pairs`, `fp32.wideexp_bgate_alt`, `fp32.denormals_only`, fp32's zeros and random, `fp16.wideexp_gate30`, `int8.b_line_flipflop`, int8's zeros, 2 s each, no preheat | blind4.json has no smoke list; one tile of each own-choice and gate case, before any pass |
| stops | die 78 °C | **die ≥ 70 °C** (E78's `--max-c`) and **board ≥ 65 W** (E130's guard in `run_e140.py`, unchanged); E115's passes here read at most 55.07 W and 63 °C | margin to the PMIC's own limits; no path drives the card toward a reset |
| config reads | `ettelem config` under the lock, `timeout 10`, both ends of every pass, the session-end read | the same | |
| data | `kinds/p115<nn>/`, `build/e115-logs/` | `build/claims-v3/aifoundry3/kinds/p140<nn>/`, `build/e140-logs/`; results `docs/reports/data/2026-11-02-e140-blind4/` | |

**What is E78's, byte for byte.** `run_e140.py`, `reduce_e140.py` and `run_e140.sh setup` check `tools/claims-v3/lib.sh` `033d0776…`,
`kinds/e78_common.py` `c58923a5…`, `kinds/run_e78.py` `f3efd783…`, `kinds/reduce_e78.py` `6a158cee…` and `kinds/kinds.json` `9586568f…`
against `predictions-e140.json` › `harness.reused_unchanged_sha256` and refuse on any difference. `e140_common.install()` replaces
`load_items` (E78's items plus the pool's 25, every number from `blind4.json`) and `pass_order` on the shared module in memory; then
`run_e78.main()` / `reduce_e78.main()` run as they are. Ported from E115 with marked changes: `e140_common.py` (blind4's JSON layout),
`run_e140.py` (plus E130's board-power guard), `block_e140.sh` (die stop 70), `queue_e140.sh` (budget 2,040 s, deadline 21:40 PST),
`run_e140.sh`, `reduce_e140.py`, `collect_e140.sh`. New: `score_e140.py`, `selftest_e140.py`, `m6_inputs.py`,
`make_predictions_e140.py`. Binaries: the tree's own (`sparsity_host` `20e760c2…`, `ettelem` `16037641…`), checked by `setup`.

## Device commands sent

*The owner's rule of Mon 2 Nov 2026: every device-management command a run's harness, sampler, host program and helpers send,
classified READ or WRITE from the firmware source; Q137 allows read-only PMIC voltage reads and no write but the statistics reset,
and **E140 does not send the reset**.* The sending code is E115's and E130's (`lib.sh` unchanged, the same `ettelem` binary,
`block_e140.sh`'s config reads and its one `start_sampler` call as theirs), so the list is theirs, classified from et-platform
`836a4ab` (BL2 0.22.0): GET_MODULE_STATIC_TDP_LEVEL, GET_MODULE_TEMPERATURE_THRESHOLDS, GET_MODULE_POWER_STATE (`ettelem config`: SP
RAM copies); GET_ASIC_FREQUENCIES (PLL register reads); **GET_ASIC_VOLTAGE** (`config` and `sample`: PVT reads and two PMIC
voltage-register reads); GET_MODULE_POWER, GET_SP_STATS (SP RAM copies); GET_MODULE_CURRENT_TEMPERATURE (PVT reads);
**GET_MODULE_VOLTAGE** (`sample`: nine PMIC voltage-register reads). **All nine are READs**; the two PMIC voltage reads are the ones
the owner's rule of 2 November 2026 allows. Never sent: SET_STATS_RUN_CONTROL (no `--reset-ms` anywhere), any SET_*, the
firmware-revisions query, any residency read. The host program opens the ops node only; the heater (`hl` block's, as E115) sends no
management command.

**The checker** `tools/claims-v3/dmcmd_audit.py` (unchanged since `32e9c109`), from the repository root on `tools/claims-v3/e140/`,
`lib.sh`, `run_e78.py`, `e78_common.py` and `reduce_e78.py`: **NO-GO** without an exception, at the one conditional site E115's and
E130's lanes reviewed (`lib.sh:154`, `start_sampler` forwards `"$@"`, which might carry `--reset-ms`); with the reviewed exception
(`block_e140.sh:98`, the only `start_sampler` call, passes the output file and the duration and nothing else) **GO, 31 send sites, 0 disallowed**
([`dmcmd-audit.txt`](dmcmd-audit.txt), [`dmcmd-audit-except.txt`](dmcmd-audit-except.txt)). E130's A1 caveat binds unchanged:
aifoundry3 runs a thermal firmware build first flashed on 7 Oct 2026 whose source is not public, so the classes rest on `836a4ab`'s
handlers and on these reads' unchanged behaviour on this card; if the session-start `ettelem config` or the smoke's telemetry comes
back in another form than E138's run recorded today (the same fields, TDP 0 W / 65 °C / 600 MHz, `since_reset_ms` −1), it is NO-GO.
**Verdict before the first launch: GO.**

## Card budget

**At most 35 card-minutes**, from the session-start config read (the smoke's) to the session-end read. Expected about 26–34: the smoke
about 1 min, then three or four passes of about 7.5–8 min (E115's passes here took 455–488 s) with 15 s between. `queue_e140.sh` starts
a pass only if its projected end (the longest measured pass; 480 s until the first ends) is inside **2,040 s** of the session start and
before **21:40 PST**; a pass in flight is never cut. No session starts after 21:00 PST; every run ends by 21:45 PST. It starts only
after E139 has released card 0, with `et-who` clean and the day's post in `#community-lab` rewritten to carry this reservation.

## How to run it (for this lane)

On the Intel, after this commit is on origin/main: `rsync -a --exclude __pycache__ tools/claims-v3/e140/` and
`tools/claims-v3/kinds/blind4/` to the same paths under `aifoundry3:aifoundry/`. On aifoundry3, from `~/aifoundry`:
`bash tools/claims-v3/e140/run_e140.sh setup` (no device access), the day's post rewritten, then `run_e140.sh smoke`,
`run_e140.sh go`, `run_e140.sh wait` (bounded). Collect on the Intel: `PY=<python with numpy> nice -n 10 bash
tools/claims-v3/e140/collect_e140.sh 'p140[1-9][0-9]' <copy>` (reduction, its arms, `score_e140.py`).

## Files

All in `tools/claims-v3/e140/`: `README.md` (this); `make_predictions_e140.py` and `m6_inputs.py` → `predictions-e140.json` (the
freeze, with every file's sha256); `e140_common.py`, `run_e140.py`, `block_e140.sh`, `queue_e140.sh`, `run_e140.sh`, `reduce_e140.py`,
`collect_e140.sh` (ports of E115's); `score_e140.py` (every rule), `selftest_e140.py`, `selftest.txt`, `planned-intervals.txt`;
`dmcmd-audit.txt`, `dmcmd-audit-except.txt`. The pool: `tools/claims-v3/kinds/blind4/` (Q137(m)'s designer). Data:
`docs/reports/data/2026-11-02-e140-blind4/`.

## Amendments

*(none)*
