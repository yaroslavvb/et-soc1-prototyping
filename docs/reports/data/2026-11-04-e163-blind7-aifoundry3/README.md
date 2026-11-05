# E163: blind pool 7 on aifoundry3 card 0 - M9 resolved better than M6 on 48 new kinds (−0.098 W [−0.148, −0.056]), every launch's C bit-exact, but E163-RANK1 FAIL on the bias rules (the session reads +0.151 W above M9 on floats, +0.051 W on int8); fp32 misses its rms rule (P1 FAIL, the single high bits), the 4.5 s heat inside in every format (H1-H4 PASS), rank 14's E151 block reproduced (KE PASS) while the 16 in-pass re-runs read 0.01-0.28 W higher than before (K14 FAIL)

*On the kinds page, [section 11, what is still open](https://spacesheep.dev/@yaroslavvb/horace-kinds-of-numbers#11-what-is-still-open):
**item 6**, "a power model across kinds". It answers Q140's final critic's **rank 1** on this card (M9 against M6 on pool 7's 48 priority-1
kinds, blind; E164 is card 1's half), with rank 4's reference half (the paired-anchor scale, scored after E164 by `score_rank4.py`), rank 9 (the
real tiles), rank 7's exponent-heavy excess (class E) and rank 11 (Q139's critic's rank 14: C-checked re-runs of earlier file tiles), plus
Q141(t)'s reported 27-point arm, as that critic left E163 (`card_half[0]`). Wed 4 Nov 2026 (week 45), the card
half of Q141, on the owner's go of that day (about 13:55 PST). The mandate: his words of 2 November 2026 ("settle any unanswered questions regarding
horace's power model"), with his goal "to be able to predict the power requirement and heat generation of various kinds of numeric computations as
accurately as possible".*

- **Card:** aifoundry3 card 0, **600 MHz in all 36,223 samples**; `ettelem config` through E128's guard at the session's start (15:35:54 PST) and
  end (16:37:40): TDP 0 W, threshold 65 °C, max_power, 600 MHz, 523 mV both times. **Nothing was set.** `since_reset_ms` −1 in every sample: no
  statistics reset.
- **Card session** 15:35:54-16:37:40 PST, **61.8 card-minutes** (T0+3,706 s), inside FULL's cap of 70: the stop-path test 16302, the smoke 16301
  and its gate (PASS at 15:36:56), then **FULL as registered**: kinds passes 16310 (1,023 s), 16311 (1,001 s) and 16312 (1,025 s), E151's block
  16350-16352 (178-179 s each); the budget rule stopped before 16313 (it would have ended at T0+4,731 s against T0+4,140 s), as A1-2 plans.
  **All three kinds passes kept** on the registered primary; nothing set aside; no tile left out.
- **Every launch's C is bit-exact:** 4,062 of 4,062 PASS against the RTL's arithmetic (Q139(k)'s `ccheck.py`, `--jobs 2`; fp32 1,296, fp16 648,
  int8 2,118; no ROUNDING, UNMODELLED or FAIL; no broken record): 990 in each kinds pass, 340 in each E151 block, 72 in the smoke. **E163-KC
  PASS.**
- **No stop fired** in any pass: the highest live readings were 54.3 W board and 63 °C `minshire[0]` (kinds passes; stops 65 W / 70 °C), and
  30.36 W / 58 °C in the E151 block (E151's stops 45 W / 68 °C). The stop-path test fired all three stops on live samples with no launch.
- **Every device-management command sent was a read** (§ Device commands sent).
- E166 ran on this card first, 14:20:51-15:35:05 ([`../2026-11-04-e166-heat-replicate-aifoundry3/`](../2026-11-04-e166-heat-replicate-aifoundry3/README.md)).

## Results

**In plain words.** A designer who never saw the model wrote 61 new tiles; M9, frozen before them, predicted each one's power and its 4.5 s die
rise on this card. Over the 48 priority-1 kinds M9's error is 0.278 W rms, clearly better than M6's, M7's and M8's on the same tiles (each
difference resolved by a paired bootstrap), its bands hold 42 of 48, its heat is inside on every format, and the ten real tiles cut from public
models are within 0.16 W rms, every one inside its band. But the whole session reads higher than M9 predicts, by 0.15 W on the floats and 0.05
W on int8, beyond what M9's own nested errors allow, so rank 1's conjunction fails on the bias rules, not on M1 as registered beforehand. The
single high B bits remain the largest miss, and the 16 tiles re-run from earlier sessions all read higher today than they did then.

**The registered verdicts** ([`results.md`](results.md), [`scored.json`](scored.json) › `verdicts`; the scorer `score_e163.py` as frozen in
`442474d5`, on Q139(u)'s footing, leakage 0.20563713796102187 W/°C, dips removed):

| rule | reading | interval (registered draws) | verdict |
|---|---|---|---|
| E163-P1 (fp32 power, 17) | rms 0.389 W | [0.115, 0.283] | **FAIL** |
| E163-P2 (fp16 power, 9) | rms 0.192 W | [0.068, 0.287] | PASS |
| E163-P3 (int8 power, 22) | rms 0.191 W | [0.117, 0.230] | PASS |
| E163-B1 (floats bias, 26) | mean(measured − M9) +0.151 W | [−0.103, +0.042] | **FAIL LOW** (M9 predicts too little) |
| E163-B2 (int8 bias, 22) | +0.051 W | [−0.096, +0.045] | **FAIL LOW** |
| E163-C1 (coverage, 48) | 42 of 48 inside M9's 95% bands | low end 42 | PASS (outside: five single-high-bit tiles and `int8.bheld_01`) |
| **E163-M1** (M9 − M6, 48) | **−0.098 W** | **[−0.148, −0.056]** | **BETTER** |
| E163-M2 (M9 − M8, 48) | −0.143 W | [−0.235, −0.058] | BETTER |
| E163-M3 (M9 − M7, 48) | −0.101 W | [−0.169, −0.043] | BETTER |
| E163-U1 (M9 − M6 on the 12 unaimed) | −0.039 W | [−0.076, −0.000] | PASS (reads BETTER) |
| E163-H1 / H2 / H3 (4.5 s rise) | rms 0.226 / 0.163 / 0.124 °C | [0.120, 0.240] / [0.086, 0.234] / [0.143, 0.265] | PASS / PASS / PASS |
| E163-H4 (heat coverage) | 46 of 48 inside | low end 42 | PASS |
| E163-R1 (10 real tiles) | rms 0.158 W | [0.127, 0.379] | PASS |
| E163-R2 (10 real tiles inside) | 10 of 10 | — | PASS |
| **E163-RANK1** | M1 BETTER, U1 PASS, C1 PASS, **B1 FAIL LOW, B2 FAIL LOW** | needs all five | **FAIL** |
| E163-KC (the C check) | 4,062 of 4,062 PASS | — | PASS |
| E163-K14 (16 in-pass re-runs, flat 0.05 W) | K14-C PASS; K14-D: 3 of 16 within 0.05 W, every difference positive (+0.013 to +0.278 W) | — | **FAIL** |
| E163-K14′ (Welch) | 11 of 16 inside | — | **FAIL** |
| E163-KE (E151's block, `int8.b1_0`-`b1_5`) | KE-C PASS; each step within 0.05 W of E151's (−0.021 to +0.024 W) | — | PASS |
| E163-KE′ (Welch) | 6 of 6 inside | — | PASS |

**Against the registered forecast** (E163.md § Precision, "frozen so it can be wrong"): KC, K14-C and KE-C PASS, K14-D FAIL, KE-D PASS, P2,
P3, C1, U1, H1-H4, R1 and R2 PASS, and M2 BETTER, as forecast; **M1 read BETTER where NOT RESOLVED was forecast**; **B1 read FAIL LOW and B2
FAIL LOW, where B1 PASS or FAIL HIGH and B2 PASS were forecast**; K14-W FAIL where PASS was forecast; RANK1 FAIL as forecast, but on B1 and B2,
not on M1. The likeliest misses named beforehand: class S was the largest; classes E and L were not (M9 0.181 and 0.189 W rms).

**Each model on the same 48 priority-1 kinds** (`results.md`, reported):

| model | fp32 rms | fp16 rms | int8 rms | rms (48) | bias (48) | real tiles rms | inside 95% | heat rms fp32 / fp16 / int8 (°C) |
|---|---|---|---|---|---|---|---|---|
| **M9** | 0.389 | 0.192 | 0.191 | **0.278** | +0.105 | 0.158 | 42 of 48 | 0.226 / 0.163 / 0.124 |
| M8 | 0.377 | 0.173 | 0.513 | 0.420 | +0.195 | 0.201 | 40 of 48 | 0.227 / 0.162 / 0.138 |
| M7 | 0.401 | 0.203 | 0.415 | 0.379 | +0.175 | 0.259 | 45 of 48 | 0.230 / 0.165 / 0.128 |
| M6 | 0.432 | 0.193 | 0.386 | 0.376 | +0.181 | 0.251 | 38 of 48 | 0.236 / 0.168 / 0.120 |

**By class** (priority 1, W; rms / bias, and the paired M9 − M6):

| class | n | M9 | M8 | M7 | M6 | M9 − M6 |
|---|---|---|---|---|---|---|
| S (single high bits) | 7 | 0.577 / +0.327 | 0.520 / +0.269 | 0.540 / +0.295 | 0.592 / +0.367 | NOT RESOLVED −0.015 [−0.043, +0.020] |
| E (exponent-heavy) | 6 | 0.181 / +0.110 | 0.252 / +0.213 | 0.237 / +0.196 | 0.276 / +0.231 | BETTER −0.095 [−0.135, −0.041] |
| L (whole-line int8) | 7 | 0.189 / +0.087 | 0.676 / +0.607 | 0.415 / +0.358 | 0.315 / +0.133 | BETTER −0.126 [−0.211, −0.041] |
| H (int8, B held) | 6 | 0.254 / −0.047 | 0.623 / −0.069 | 0.595 / −0.204 | 0.591 / +0.013 | BETTER −0.336 [−0.465, −0.208] |
| U (aimed at nothing) | 12 | 0.156 / +0.079 | 0.152 / +0.086 | 0.207 / +0.154 | 0.195 / +0.143 | NOT RESOLVED −0.039 [−0.077, +0.001] |
| R (real tiles) | 10 | 0.158 / +0.082 | 0.201 / +0.133 | 0.259 / +0.203 | 0.251 / +0.200 | BETTER −0.093 [−0.145, −0.035] |

**What carries the misses.**
- **P1 and class S: the single high B bits.** `fp32.b_onebit_b20_full` +0.827 W, `_seventh` +0.736, `_pi` +0.563 and `_one` −0.676 W, and
  `fp16.b_onebit_b8_pi` +0.463 W; five of C1's six tiles outside M9's bands are these. The byte twin `fp32.b_onebit_b20_pi` (= `fp32.cal_pi_b20`)
  measured 12.655 W against M9's 12.093, an error of +0.563 W against the counting-only expectation of +0.311 ± 0.198 W (reported).
  **Q141(t)'s 27-point arm** (reported, A1-5): over its 8 tiles the rms is 0.542 W with the three-point counts and **0.380 W with 27 points**.
- **B1 and B2: the session sits above M9.** The floats' anchors and random kinds read +0.25 to +0.33 W over M9 (`fp32.anchor7_randn_a` +0.259,
  `_b` +0.331, `fp32.uniform_pm1` +0.257, `fp32.laplace_both` +0.254 W), and every one of the 16 re-run tiles reads higher than in its earlier
  session (+0.013 to +0.278 W; `int8.b_line_flipflop_nogate` +0.278, `int8.real_pythia_w8a8_up` +0.196 W). The card scale reads 1.0056 [1.0031,
  1.0104] on the floats and 1.0112 [1.0022, 1.0218] on int8 (`results.md` § Card scale, reported; M9 applies 1 on its own card). E151's block,
  measured as steps over its own zero on the minion rail, reproduced within 0.025 W. So the excess is a level of the whole board reading on this
  day, which M9 does not model, more than a per-kind error.
- **The arms** (reported, never the verdict): with leakage 0.1994 W/°C, with the leakage fitted on this session and the dips removed, and with
  the pass gates opened, every power and heat rule reads as the primary; with leakage 0, P2, C1 and R2 also fail. Three arms (the session-own
  footing, the frozen slope with the dips kept, leakage 0.3803 W/°C) kept one pass each, E78's pass gates setting two aside (with the dips kept,
  `fp16.randn` spans 2.3 W in one pass and `fp32.randn` 1.16 W in another; at 0.3803 W/°C `fp32.zeros` departs about 0.3 W from its line in two),
  so by the registered rule they score nothing (`{}` in `results.md`).

## What it does to predicting power and heat

- **The term tested:** M9's whole 600 MHz power model (Q140(m), frozen in `1f244140`) and its bands, with M7's heat law for the 4.5 s rise, on 48
  kinds written by an independent designer, on M9's own card; the card term at 1 on that card.
- **Before:** M9's nested leave-one-kind-out error on aifoundry3's rows, 0.200 / 0.168 / 0.169 W (fp32 / fp16 / int8); the blind record of a new
  kind's 600 MHz power, 0.24-0.32 W rms per card (M8 on pool 6 here, E153: 0.330 / 0.125 / 0.296 W); the 4.5 s rise, 0.10-0.18 °C.
- **After (blind, this session):** M9 **0.389 / 0.192 / 0.191 W** (0.278 W over the 48, +0.105 W bias), better than M6, M7 and M8 on the same
  tiles by 0.10-0.14 W, resolved (M1-M3 BETTER); heat **0.226 / 0.163 / 0.124 °C**, inside on every format. On the blind record (different pools
  and models), int8's error fell from 0.296 W (M8 on pool 6, E153) to 0.191 W (M9 on pool 7); fp32's rose from 0.330 to 0.389 W, carried by the
  single high bits and the session's level.
- **What it says to change:** a day-to-day level term (this session read +0.15 W on the floats, and every re-run tile read high), which a refit
  cannot take from the bits alone, and the single-high-bit counts (the 27-point counts lower that class's error from 0.54 to 0.38 W rms, reported).
  **Nothing frozen changes here**; rank 1 needs E164's half too, and rank 4's pair score follows E164's collection.

## Registered before any data, and what the box ran

- **Frozen first:** blind pool 7 with M9's, M8's, M7's and M6's predictions, Q140(x) `75802201` (03:27:39 PST) and its notes `3c9bb2ba`
  (04:18:24); M9 `1f244140` (01:12:04), registration `8dfafae3` (00:45:51). Q141(t)'s reported arm M9_27pt, `67d5e44f` (10:07:40), and its
  amendment A1, `c31e7ae3` (12:16:56). Nothing was fitted here.
- **Registered** (Q141(a)), every commit before any E163 data, claim or launch: [`E163.md`](../../../../tools/claims-v3/e163/E163.md) alone,
  `64dff136` (09:33:22 PST); the freeze (M9's reference errors, rank 14's picks, `predictions-e163.json`, the scorer and its self-tests),
  `442474d5` (09:38:32); the run kit and `harness-e163.json` (142 files), `1c47ce62` (09:52:17); amendment A1 and the README's dated note,
  `f13e0b39` (10:49:52). Q141(f), the readiness critic, re-ran the parent self-test (9,853 fields, 0 differ) and the Intel dry pass before his go.
- **The tree on the box:** the same one rsync as E166's (14:18:34 PST, Q141(k)'s `s07_a3_sync.sh`). On the box at 14:18:47-49: blind7
  `sha256sum -c` **91 OK**; `check_e163.py` **HARNESS OK: 142 files** (the four binaries `99ed75fb…`, `d521e432…`, `20e760c2…`, `16037641…`
  among them); `preflight_e163.sh` **GO, 32 send sites, 0 disallowed**; `e163_common.py --verify` 0 problems (77 tiles: pool 7's 61 and 16
  re-runs; 26 E151 items; 48 priority-1 kinds). The session re-ran the check and the preflight at its start.
- **The V3_DRY passes on the box** (14:19:12-14:19:36, no device opened): blocks 16310 (99 launches through the wrapper), 16350 (34, E151's
  stops 45 W / 68 °C) and 16301 `--smoke` (12), each rc 0; the session's start gate refusing with exit 8 at a past `E163_LATEST_START`.

## Registered against what happened

| | registered | happened |
|---|---|---|
| order | the registration (`64dff136`), the freeze (`442474d5`), the kit (`1c47ce62`) and A1 (`f13e0b39`) before the claim and the first launch, each descending from the frozen pool (`75802201`, `3c9bb2ba`) and M9 (`1f244140`, `8dfafae3`) | all ancestors of the synced tree (`5e1bb309`); the claim 14:11:27 PST; first device access on this card 14:18:55 (the config read); E163's first launch 15:36 |
| plan | FULL if 70 minutes remain before `E163_DEADLINE`, else TWO or SHORT; 4,200 s from T0 with a 60 s reserve; at least 2 kept passes | 183 minutes remained: FULL; three kinds passes and the E151 block ran, the budget rule stopped before 16313; three passes kept |
| card time | the cap 70 card-minutes; no session after 18:15, every run ends by 19:00 PST | **61.8 card-minutes** (15:35:54-16:37:40 PST); the kinds passes took 1,001-1,025 s against the kit's 892-947 s estimate, so the session ran longer than Q141(f)'s 56-59 |
| stop-path test 16302 | the guard's die and board stops and the in-run watcher each end `run_e163.py` with EXIT_HOT on a live sample at most 2.0 s old, no launch | **PASS**: the die stop on `minshire[0]` 54.0 °C read 0.082 s after the sample, the board stop on 24.51 W at 0.123 s, the watcher on 24.58 W at 0.052 s (`aifoundry3/e163-stoptest/p16302/STOP.*`); no launch record |
| smoke 16301 | the gate (`smoke_gate_e163.py`) | **PASS** (`SMOKE-GATE PASS {'bad': []}`, 15:36:56): its twelve items, the C log's 72 records, 600 MHz, the config reads |
| stops | board ≥ 65 W or `minshire[0]` ≥ 70 °C, live, main path and in-run watcher (E151's block: 45 W / 68 °C) | highest 54.3 W and 63 °C in the kinds passes, 30.36 W and 58 °C in the block; no stop fired |
| the C check | every pool-7 launch, bit-exact | 4,062 of 4,062 PASS; no tile left out |
| departures | — | **D1, the collection route** (dated here, Wed 4 Nov 2026, before the registered reduction ran): the raw copy was made straight into this directory's `aifoundry3/` and `collect_e163.sh` was run over that repo-relative copy, as E153's data was assembled, instead of the runbook's `s22_collect.sh e163`, which copies into an absolute `build/e163-raw`: `reduce_e78.py` records the pass directories as given (`dirs`), so that route would have written the Intel's home path into `e163.json` and every arm. The collector, its arguments, the registered code and the reading of `results.md written` are unchanged; its outputs also stay in `build/e163-out/2026-11-04-e163-blind7-aifoundry3/`, where E164's collection reads them. No other departure. |

## Device commands sent

As registered ([`tools/claims-v3/e163/E163.md`](../../../../tools/claims-v3/e163/E163.md) § Device commands sent): E153's harness, E78's card
code unchanged, every telemetry call through E128's guard (`ettelem config` with no argument, `ettelem sample --seconds --every-ms` and nothing
else), `ettelem config` at the session's start, at both ends of the stop-path test, the smoke, every pass and every E151 block, and at the
session's end, `ettelem sample` at 10 Hz in every block. Sent: GET_MODULE_STATIC_TDP_LEVEL, GET_MODULE_TEMPERATURE_THRESHOLDS,
GET_MODULE_POWER_STATE, GET_ASIC_FREQUENCIES, **GET_ASIC_VOLTAGE**, GET_MODULE_POWER, GET_SP_STATS, GET_MODULE_CURRENT_TEMPERATURE,
**GET_MODULE_VOLTAGE**: **all READs**, classified from et-platform `836a4ab` (BL2 0.22.0), the two in bold PMIC voltage-register reads, which the
owner's rule of 2 November 2026 allows. **Never sent**: the statistics reset (`SET_STATS_RUN_CONTROL`; `since_reset_ms` −1 in every one of the session's 36,223 samples), any SET_*, the
firmware-revisions query, any residency read, any governor, TDP, threshold or clock set, any reset, and `dev_mngt_service`. The host programs
(E78's `sparsity_host` `20e760c2…` as the heater; the C-logging host `99ed75fb…` through `sparsity_ccheck.sh` for every measured launch) open
the ops node only. The checker (`dmcmd_audit.py`, unchanged), run by the session on the box before any device opened: **GO**, 32 send sites, 0
disallowed, with the one reviewed exception (`lib.sh:154`, the conditional `--reset-ms` forward that `block_e163.sh` never uses)
([`logs/dmcmd-preflight.txt`](logs/dmcmd-preflight.txt)). Residual, as registered: aifoundry3's thermal firmware build (since 7 Oct 2026) is not
public, so the classes rest on `836a4ab`'s handlers.

## Card and post

`et-who` at the look-first reads (14:18:26, 14:20:50 and 15:35:53 PST), at the session's start (15:35:54) and at its end (16:37:40): no process
held a device node or card lock; other accounts' idle logins were present, which do not block (the owner's ruling of 1 November 2026), and no
device process of theirs. E166 ran on this card first (14:20:51-15:35:05 PST,
[`../2026-11-04-e166-heat-replicate-aifoundry3/`](../2026-11-04-e166-heat-replicate-aifoundry3/README.md)); E163 needs no rest after it (its
protocol heats to 59 °C before every launch).

Wed 4 Nov's one `#community-lab` post is message `1567662592850399304`, created at 14:11:27 PST by the card half's claim with one clause per
box. aifoundry3's, `using aifoundry3 for 3 h, until ~17:11 PST [doc](<https://spacesheep.dev/@yaroslavvb/horace-kinds-of-numbers>)`, covered E166
and E163 in one reservation (the README's dated note). **The release, 16:38:11 PST**, under the Discord lock and `EXPECT_TEXT`, dry-run, saved and
read back (16:38:16, one post that day, its text equal to the intended one): the aifoundry3 clause dropped, the aifoundry1 and aifoundry2 clauses
kept word for word and no " — released", because those cards were still held:
`<ai> **Claude says:** using aifoundry1 for 3 h, until ~17:11 PST [doc](<https://spacesheep.dev/@yaroslavvb/horace-kinds-of-numbers>); using aifoundry2 for 4.25 h, until ~18:26 PST [doc](<https://spacesheep.dev/@yaroslavvb/horace-kinds-of-numbers>)`.
Mon 2 Nov's and Tue 3 Nov's posts were not touched.

## How to reproduce

```bash
# from the lab clone: the registered collector over this directory's raw copy (Python 3.9 with numpy), as it was run
PY=/usr/bin/python3 E163_DATE=2026-11-04 nice -n 10 bash tools/claims-v3/e163/collect_e163.sh \
  docs/reports/data/2026-11-04-e163-blind7-aifoundry3/aifoundry3 docs/reports/data/2026-11-04-q141t-s7-recount/arm/arm27-aifoundry3.json
# (gunzip the c-log.jsonl.gz files under aifoundry3/ first; the collector writes build/e163-out/2026-11-04-e163-blind7-aifoundry3/)
python3 -B tools/claims-v3/e163/selftest_e163.py --parent    # the parent self-test (E153's scored.json, 9,853 fields)
```

## Files

| file | what |
|---|---|
| `scored.json`, `results.md` | the registered scorer's output on the registered primary (Q139(u)'s footing), every arm beside, the E151 block, Q141(t)'s 27-point arm |
| `scored-session.json`, `results-session.md` | the session-own footing scored alone (reported, never the verdict) |
| `e163.json`, `runs.csv`, `reduce.txt`, `reduce.log` | the registered primary reduction of the three kinds passes |
| `e163-session.json`, `e163-auto-nodips.json`, `e163-kfrozen-dips.json`, `e163-leak*.json`, `e163-gatesoff.json` (with their `runs-*.csv`, `reduce-*.txt`, `reduce-*.log`) | the arms |
| `e163-e151.json`, `runs-e151.csv`, `reduce-e151.txt`, `reduce-e151.log` | the E151 blocks under E151's registered primary |
| `ccheck/` | the C logs (`c-log-p163*.jsonl.gz`) and `ccheck.py`'s output (`ccheck-all.json`, `ccheck.txt`) |
| `aifoundry3/e163/p16310`-`p16312`, `p16350`-`p16352` | the passes and E151 blocks as the box wrote them (`telemetry.jsonl.raw.gz`, `runs.jsonl`, `run.log`, `block.json`, the config reads, `c-log.jsonl.gz`, …) |
| `aifoundry3/e163-smoke/p16301`, `aifoundry3/e163-stoptest/p16302` | the smoke and the stop-path test |
| `aifoundry3/logs/`, `logs/` | the box's `build/e163/` (the session log, `session.out`, `queue.out`, the session's config reads, the device-command preflight, `binaries.sha256`); the session log's first two lines are the dry pass's start-gate test (exit 8, no device opened). Its et-who readings name no other account (E164's scrub in `--check` mode: 0 left) |
| `code.sha256` | the code the collector ran, hashed |

SPDX-License-Identifier: Apache-2.0
