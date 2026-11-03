# E141: M7 against blind pool 5 on aifoundry3 card 0 - heat holds and M7's power bands cover 28 of 30, but the floats read 0.23 W too high (B1 FAIL HIGH) and fp16 misses its rms rule (P2 FAIL) on the registered primary

*On the kinds page, [section 11, what is still open](https://spacesheep.dev/@yaroslavvb/horace-kinds-of-numbers#11-what-is-still-open):
item 6, "a power model across kinds", tested out of sample on a fifth pool written by someone else, on the card M7's power has no card term
for. Mon 2 Nov 2026 (week 45), Q138. Pre-registered in `87a64409` (committed 21:21:27, pushed by 21:21:30 PST), before the claim and before
any card ran a tile of pool 5 on aifoundry3: [`tools/claims-v3/e141/README.md`](../../../../tools/claims-v3/e141/README.md). The model is
Q138(m)'s M7, frozen in `3a210f2b` (19:21 PST); the pool, [blind pool 5](../../../../tools/claims-v3/kinds/blind5/README.md), 36 tiles by an
independent designer, and M7's, M6's and M5's frozen predictions for this card, in `dac39d97` (20:24:02 PST), an ancestor of `87a64409`
(checked: `logs/push-and-claim-times.txt`). aifoundry3 card 0 at 600 MHz in every sample; `ettelem config` read at the session's start
(21:23:33), at both ends of the stop-path test, the smoke and every pass, and at the session's end (22:04:32): TDP 0 W, threshold 65 °C,
max_power, 600 MHz, 522–523 mV, never set. **Every device-management command sent was a read** (nine kinds, two of them PMIC voltage-register
reads, which the owner's rule of 2 November 2026 allows; `since_reset_ms` −1 in all 24,014 samples). Card session 21:23:33–22:04:32 PST,
**41.0 of the 50 card-minutes allowed**: the stop-path test 14102, the smoke 14101 and four passes, 14110–14113 (574–623 s each); the budget
rule stopped before 14114.*

**In plain words.** M7 is the lab's power-and-heat model: from the bytes a matmul multiplies it predicts the watts the chip draws over the
same kernel on zeros, and how far the die warms in a 4.5 s run. E141 ran 36 new kinds of numbers, written by someone who never saw the
model, on the card M7's power numbers are written for. **Heat holds again**: the die's rise is predicted to 0.13 °C rms in every format and
all 30 tiles land inside M7's 95% bands (H1–H4 PASS). **Power's bands now hold**: 28 of 30 tiles land inside M7's bands (C1 PASS), where the
older models' bands held 22 (M6) and 19 (M5) of the same 30. **But M7 still predicts the floats about 0.23 W too high** (B1 FAIL HIGH: the
same direction as M6's −0.28 W on pool 4), and on fp16 its error, 0.32 W rms, is about twice what its nested score claims (P2 FAIL). With the
board meter's dips removed, a reported arm, fp16 passes (0.20 W) and the float bias shrinks to −0.15 W but still fails. M7 is not told apart
from M6 or M5 on these tiles (M1, M2 NOT RESOLVED).

## Results

**Three of four passes kept on the registered primary** (E140's frame: E78's reduction unchanged, leakage `auto` (0.263 W/°C, fitted on
this session's 165 runs), dips kept, E78's run and pass gates): 14111, 14112, 14113. **14110 was set aside by E78's registered random-range
gate** (`fp32.randn` spans 1.704 W, over the 1.0 W line), a reading of the size the board meter's dips make (E82 A2; E140's D1 was the same);
the dips-removed arm keeps all four passes. Every tile has at least two kept passes (`fp16.exp_only` two: E78's runner skipped it once, D2),
so every rule is scored ([`results.md`](results.md), [`scored.json`](scored.json)).

**1. The registered verdicts** (primary; the arms are reported, never the verdict).

| rule | quantity | set | reading | the nested score's interval | verdict | dips removed (4 passes) | leak 0.1994 | leak 0 | gates off (4) |
|---|---|---|---|---|---|---|---|---|---|
| **E141-P1** | power | priority-1 fp32 (9) | rms **0.325 W** | 0.087–0.545 | **PASS** | PASS 0.201 | PASS 0.260 | PASS 0.487 | PASS 0.342 |
| **E141-P2** | power | priority-1 fp16 (8) | rms **0.317 W** | 0.071–0.247 | **FAIL** | PASS 0.195 | PASS 0.233 | FAIL 0.463 | FAIL 0.278 |
| **E141-P3** | power | priority-1 int8 (7) | rms **0.356 W** | 0.093–0.361 | **PASS** | PASS 0.352 | PASS 0.342 | PASS 0.324 | PASS 0.349 |
| **E141-B1** | bias | priority-1 floats (17) | mean(measured − M7) **−0.230 W** | −0.117 to +0.085 | **FAIL HIGH** | FAIL HIGH −0.151 | PASS −0.082 | FAIL LOW +0.381 | FAIL HIGH −0.233 |
| **E141-B2** | bias | priority-1 int8 (7) | **−0.110 W** | −0.225 to +0.103 | **PASS** | PASS −0.126 | PASS −0.076 | PASS +0.031 | PASS −0.119 |
| **E141-C1** | power coverage | 30 non-anchor tiles | **28 of 30** inside | ≥ 26 | **PASS** | PASS 28 | PASS 30 | PASS 27 | PASS 28 |
| **E141-M1** | M7 against M6 | 24 priority-1 | rms(M7) − rms(M6) **−0.009 W** [−0.047, +0.024] | | **NOT RESOLVED** | NOT RESOLVED −0.007 | NOT RESOLVED | NOT RESOLVED | NOT RESOLVED |
| **E141-M2** | M7 against M5 | 24 priority-1 | **−0.040 W** [−0.091, +0.004] | | **NOT RESOLVED** | BETTER −0.049 [−0.106, −0.007] | NOT RESOLVED | NOT RESOLVED | BETTER −0.044 |
| **E141-H1** | die rise | priority-1 fp32 (9) | rms **0.128 °C** | 0.102–0.261 | **PASS** | PASS 0.087 | PASS | PASS | PASS 0.088 |
| **E141-H2** | die rise | priority-1 fp16 (8) | rms **0.129 °C** | 0.083–0.235 | **PASS** | PASS 0.126 | PASS | PASS | PASS 0.127 |
| **E141-H3** | die rise | priority-1 int8 (7) | rms **0.135 °C** | 0.095–0.309 | **PASS** | PASS 0.129 | PASS | PASS | PASS 0.129 |
| **E141-H4** | heat coverage | 30 non-anchor tiles | **30 of 30** inside | ≥ 26 | **PASS** | PASS 30 | PASS 30 | PASS 30 | PASS 30 |

At leakage 0.3803 W/°C (an arm) E78's zeros-line gate sets three passes aside and every rule is NOT SCORED. **Arm-sensitive**: P2 (passes
with dips removed and at 0.1994), B1 (passes at 0.1994, reverses at 0), M2 (BETTER with dips removed and with the gates off). Heat is not
arm-sensitive. Against both cards' reference rows (reported) P1–P3 read the same. **The frozen expectation** was P1–P3 PASS, B1 PASS or FAIL
HIGH, B2 and C1 PASS, M1 NOT RESOLVED, M2 NOT RESOLVED or BETTER, H1–H4 PASS: **P2 did not**; everything else fell as frozen.

**2. M7, M6 and M5 on the same tiles** (reported; measured − model, W; heat °C; primary unless marked):

| model | fp32 rms / bias | fp16 rms / bias | int8 rms / bias | all 30: rms / bias | inside its own 95% band | heat rms fp32 / fp16 / int8 |
|---|---|---|---|---|---|---|
| **M7** | 0.325 / −0.233 | 0.317 / −0.227 | 0.356 / −0.110 | 0.365 / −0.233 | **28 of 30** | 0.128 / 0.129 / 0.135 (30 of 30 inside) |
| M6 | 0.311 / −0.194 | 0.353 / −0.293 | 0.360 / −0.124 | 0.367 / −0.237 | 22 of 30 | 0.128 / 0.123 / 0.140 (30 of 30) |
| M5 | 0.375 / −0.256 | 0.359 / −0.150 | 0.382 / −0.154 | 0.408 / −0.244 | 19 of 30 | — (no heat term) |
| M7, dips removed | 0.201 / −0.163 | 0.195 / −0.137 | 0.352 / −0.126 | 0.266 / −0.164 | 28 of 30 | 0.087 / 0.126 / 0.129 |
| M6, dips removed | 0.158 / −0.124 | 0.249 / −0.203 | 0.358 / −0.140 | 0.266 / −0.168 | 26 of 30 | 0.088 / 0.120 / 0.135 |
| M5, dips removed | 0.269 / −0.186 | 0.256 / −0.060 | 0.380 / −0.170 | 0.315 / −0.175 | 23 of 30 | — |

The three models' power errors are close (their predictions differ by at most 0.6 W on this pool). **What changed with M7 is the band**:
rule B's half-width (k 3.179 floats, 2.483 int8, times the pool rms with the constants' covariance) covers 28 of 30 on the primary and on the
dips-removed arm, where M6's 1.96σ bands cover 22 and 26 and M5's 19 and 23.

**3. Where power misses** (measured − M7, W; per-pass D in `e141.json` › `per_pass`). The primary's largest misses, −0.52 to −0.75 W on
`fp32.lowrank2_w`, `fp32.block_sparse_k4`, `fp32.exp_only_both`, `fp16.real_pythia_qk` and `fp32.sorted_k`, are each one low pass of three:
`fp32.lowrank2_w` read 22.33 W in 14111 against 24.43 and 24.50, and 24.41–24.56 W in all four passes with dips removed (−0.04 W there). The
board meter's dips again (E140's C2). The misses that are steady on both arms:

| tile | case | M7 D, W [95%] | primary (passes) | dips removed | M6 / M5 (primary) |
|---|---|---|---|---|---|
| `int8.b_line_zero_one` | 6 whole-line flip-flops (named in advance) | 3.96 [3.35, 4.57] | **−0.61** (3.30, 3.41, 3.34) | −0.62, **outside** | −0.55 / −0.53 |
| `int8.powerlaw_w` | 8 seeded realistic weights (priority 2) | 6.38 [5.79, 6.96] | **−0.60, outside** | −0.59, **outside** | −0.63 / −0.61 |
| `fp16.real_pythia_softmax_v` | 5 real model | 17.35 [16.83, 17.88] | **−0.60, outside** | −0.41 | −0.53 / −0.59 |
| `fp32.wideexp48_bgate_kblk` | 2 spread exponents beside gated zeros (named) | 13.33 [12.54, 14.13] | −0.35 | −0.36 | −0.20 / −0.41 |
| `fp32.wideexp48_bgate_alt` | 2 (named) | 15.13 [14.30, 15.95] | −0.36 | −0.26 | −0.37 / **+0.19** |
| `int8.real_pythia_w8a8_down` | 5 real model | 6.19 [5.61, 6.77] | **+0.50** | +0.45 | +0.46 / +0.47 |

Every case's mean error is negative (M7 too high): seeded realistic weights −0.68 W (2 tiles), whole-line flip-flops −0.36 (3), exponent-only
activity −0.32 (3), structured streams −0.20 (8), fp16 pairs that cancel −0.17 (2), spread exponents beside gated zeros −0.16 (4), real model
tiles −0.14 (7), few mantissa bits −0.08 (1). **Where the models differ** (Q138(x)'s list): on `fp16.sparse24_aligned` M7 reads −0.07 W where
M6 reads −0.33; on `int8.b_line_flipflop_nogate` M7 −0.18 where M6 −0.45 and M5 −0.44; on `fp32.block_sparse_k4` M7 −0.61 where M6 −0.43;
on the wide-exponent gate tiles M5 differs (`fp32.wideexp48_bgate_alt` M5 +0.19 against M7 −0.36; `fp16.wideexp_bgate_alt` M5 +0.52 against
M7 −0.08).

**4. The float bias and the leakage slope.** B1's reading moves with the leakage slope the reduction subtracts: −0.230 W at the session's
own fitted 0.263 W/°C (the registered `auto`, the footing every M7 training session used with its own fit), −0.082 W at E78's 0.1994 (a
PASS), +0.381 W with none (FAIL LOW). A run warms the die about 0.12 °C per board W, so the slope takes about 0.12 × k of every watt: a change
of 0.064 W/°C moves a 20 W float tile by about 0.15 W (the arms move B1 by 0.148 W between 0.263 and 0.1994, and by 0.611 W between 0.263
and 0). The aifoundry3 sessions in M7's training rows that reduced with `auto` fitted between 0.140 (E92) and 0.296 W/°C (E95; E78 0.199,
E115 0.230, E140 0.286), a spread that moves this pool's float bias by about 0.35 W. So the −0.23 W (about 1.2% of the floats' D) is real on
the registered footing, in E140's direction, and of the size the session-to-session leakage fit makes; E141 alone cannot tell a model term
from that footing.

**5. Heat** (measured − M7, °C): bias +0.004 (fp32), +0.110 (fp16), +0.032 (int8), rms 0.13 in each format, all 30 tiles inside M7's bands
and all six pool anchors inside too. **The rise against M7's 0.1186 °C per board W** (reported): a line through the origin of each tile's
mean `dT_win` on its mean S gives 0.1220 °C/W over the 30 tiles (+2.9%). At the measured run length (median T_run 4.49 s fp32 and fp16, 4.42
s int8, with M7's ST term, −0.0490 °C/W/s): rms 0.124 / 0.124 / 0.134 °C, 30 of 30 inside. M6's heat term, the same rule, reads the same.
The small int8 rises still land on whole degrees (`dT_win` exactly 1.0 °C on eight int8 tiles), the readout floor.

**6. What it does to predicting power and heat** (the before/after the owner's goal asks for; aifoundry3 card 0, 600 MHz):

| | before: M7's nested leave-one-kind-out score, aifoundry3 rows | after: blind pool 5, primary | dips removed (reported) |
|---|---:|---:|---:|
| power, fp32 | 0.247 W rms | **0.325 W** (bias −0.233) | 0.201 W (−0.163) |
| power, fp16 | 0.162 W | **0.317 W** (−0.227) | 0.195 W (−0.137) |
| power, int8 | 0.226 W | **0.356 W** (−0.110) | 0.352 W (−0.126) |
| power, 95% bands | 95% (rule B, calibrated, not tested) | **93% (28 of 30)** | 93% (28 of 30) |
| heat, fp32 / fp16 / int8 | 0.181 / 0.159 / 0.205 °C | **0.128 / 0.129 / 0.135 °C** | 0.087 / 0.126 / 0.129 °C |
| heat, 95% bands | 95% | **100% (30 of 30)** | 100% |

The blind record before this, on this card: M6 on pool 4 (E140) read 0.406 W (priority-1 floats) and 0.384 W (int8), biased −0.28 W, its
bands holding 19 of 25; heat 0.204 / 0.164 °C. So: **the heat term (0.1186 °C per board W over a 4.5 s run) can be quoted for new kinds on this
card**, with two blind pools and two models behind it. **M7's power bands can be quoted** (28 of 30, where M6's held 19 of 25 on pool 4 and 22
of 30 here). **M7's power point estimate cannot yet, as stated**: on new kinds it runs 1.3× (fp32), 2.0× (fp16) and 1.6× (int8) its nested rms
on the registered primary and reads the floats 0.23 W high; the meter's dips carry most of the fp32 and fp16 excess (0.201 and 0.195 W with
them removed: inside the rules' intervals, fp32 below its nested 0.247 W, fp16 still above its 0.162 W), not int8's, whose misses are steady.

**The anchors** (reported, D in W): E78's anchors on the kept passes, `fp32.randn` 24.52, `fp16.randn` 21.91, `int8.full` 7.15, against
E140's 24.44, 21.85 and 7.01 on this card this afternoon; the pool's own random anchors inside M7's bands (fp32 +0.11, fp16 −0.04, int8
−0.00 W) and its zeros tiles within 0.03 W of E78's built-in zeros (fp32 +0.024, fp16 0.000, int8 −0.002 W).

## Registered against what happened

| | registered | happened |
|---|---|---|
| order | `dac39d97` before the registration; the registration before the claim and the first launch | `dac39d97` (20:24:02) an ancestor of `87a64409` (21:21:27, pushed by 21:21:30); claim saved 21:23:12; first device access 21:23:33 |
| passes | 14110–14113, 14114 if it fits (2,940 s from T0, before 23:40 PST); at least 2 kept | four ran (623, 574, 586, 582 s); the budget rule stopped before 14114 at T0+2459 s (projected end T0+3082 s); **three kept** (14111–14113) |
| card time | ≤ 50 min | **41.0 min** (21:23:33–22:04:32 PST) |
| stop-path test 14102 | die, board and watcher each end `run_e141.py` with EXIT_HOT on a live sample ≤ 2.0 s old, no launch | **PASS**: die on `minshire[0]` 50 °C read 0.081 s after the sample, board 23.31 W at 0.023 s, the watcher 23.38 W at 0.052 s; no launch record |
| smoke 14101 | the gate (`smoke_gate_e141.py`) | **PASS**: 546.001 / 318.0 cycles per op, 0.599–0.600 GHz, config 0 W / 65 °C / 600 MHz at both ends, every pool tile's dump equal to its sha256, 373 live samples, `since_reset_ms` −1, board 23.05–51.98 W |
| stops | board ≥ 65 W or `minshire[0]` ≥ 70 °C, live, main path and in-run watcher | highest board 55.33 W, highest `minshire[0]` 63 °C; no stop fired |
| expectation | P1–P3 PASS; B1 PASS or FAIL HIGH; B2, C1 PASS; M1 NOT RESOLVED; M2 NOT RESOLVED or BETTER; H1–H4 PASS | **P2 FAIL**; the rest as frozen (B1 FAIL HIGH) |
| departures | — | **D1**: E78's random-range gate set 14110 aside (as E140's D1); the dips-removed arm keeps it. **D2**: E78's runner skipped two runs by its own rule, "launch reading not reached" (`fp16.exp_only` in 14111, `int8.full` in 14112); `fp16.exp_only` keeps two passes on the primary. **D3**: the collector's Python was the Intel's `/usr/bin/python3` 3.9.6 with numpy 1.26.4. **D4**: a Tailscale check appeared at 22:05:48, after the session's end (22:04:32); the probe at 22:06:33 needed it and the one at 22:09:33 passed; nothing on the box waited. **D5**: a reduction of the three passes then on the Intel was read at about 22:07, after the queue had ended (no pass could be added); the registered numbers are the collect over all four passes from this directory, which reproduces it |

## Device commands sent

As registered ([`tools/claims-v3/e141/README.md`](../../../../tools/claims-v3/e141/README.md) § Device commands sent): E78's harness
unchanged, every telemetry call through E128's guard (`ettelem config` with no argument, `ettelem sample --seconds --every-ms` and nothing
else), `ettelem config` at the session's start, at both ends of the stop-path test, the smoke and every pass, and at the session's end,
`ettelem sample` at 10 Hz in every block. Sent: GET_MODULE_STATIC_TDP_LEVEL, GET_MODULE_TEMPERATURE_THRESHOLDS, GET_MODULE_POWER_STATE,
GET_ASIC_FREQUENCIES, **GET_ASIC_VOLTAGE**, GET_MODULE_POWER, GET_SP_STATS, GET_MODULE_CURRENT_TEMPERATURE, **GET_MODULE_VOLTAGE**: **all
READs**, classified from et-platform `836a4ab` (BL2 0.22.0), the two in bold PMIC voltage-register reads, which the owner's rule of 2 November
2026 allows. **Never sent**: the statistics reset (`SET_STATS_RUN_CONTROL`; `since_reset_ms` −1 in every one of the session's 24,014
samples), any SET_*, the firmware-revisions query, any residency read, any governor, TDP, threshold or clock set, any reset, and
`dev_mngt_service` (lib.sh's drain is replaced by a refusal; never needed). The host program (`sparsity_host`, `20e760c2…`) opens the ops node
only. The checker (`dmcmd_audit.py`, unchanged), run by the session on the box before any device opened: **GO**, 32 send sites, 0 disallowed,
with the one reviewed exception (`lib.sh:154`, the conditional `--reset-ms` forward that `block_e141.sh`'s only `start_sampler` call never
uses); NO-GO without it ([`logs/dmcmd-preflight.txt`](logs/dmcmd-preflight.txt); the registration's `dmcmd-audit*.txt`). Residual, as
registered: aifoundry3's thermal firmware build is not public, so the classes rest on `836a4ab`'s handlers; the config reads and the telemetry
came back in the form E147 read on this card tonight (the smoke gate checks it).

## Card and post

`et-who` at the session's start (21:23:33) and at its end (22:04:32): no process held a device node or card lock; other users' idle logins
were present, no device process of theirs. The previous aifoundry3 lane (E147) had released card 0 at 20:57:44. The day's post (message
1566837317765963987) was rewritten under EXPECT_TEXT and the Discord lock, each edit dry-run, saved and read back: at 21:23:12 PST this lane's
clause, "using aifoundry3 for 1 h, until ~22:30 PST [doc](<https://spacesheep.dev/@yaroslavvb/horace-kinds-of-numbers>)", was added to the
two clauses then held (aifoundry1 card 1, aifoundry2); at 22:10:14 PST, the release, rebuilt after a refusal with exit 7 (another lane had
rewritten the post meanwhile), dropped it and kept the aifoundry2 clause word for word, with no " — released" because that card is still held:
"<ai> **Claude says:** using aifoundry2 for 1.5 h, until ~23:30 PST [doc](<https://spacesheep.dev/@yaroslavvb/horace-kinds-of-numbers>)"
(`logs/push-and-claim-times.txt` holds every before and after).

## What it changes

- **Item 6**: on this card, the item's "a power model whose bands cover on new kinds" is met by M7 (28 of 30, registered C1 PASS; M6's
  held 19 of 25 on pool 4), and heat is answered again out of sample (H1–H4 PASS on a second blind pool). Still open: M7's power is biased high
  on the floats (−0.23 W, registered B1 FAIL HIGH, of the size the session's leakage fit makes), fp16's rms is twice its nested claim on the
  registered primary (P2 FAIL; the meter's dips carry it), M7 is not resolved from M6 or M5, and int8 has three steady misses (whole-line
  zero/one flip-flops and power-law weights 0.6 W high, a real w8a8 tile 0.5 W low).
- **The model**: a next fit should carry a float offset or a leakage footing shared across sessions, and int8's line flip-flop; the bands
  (rule B) stand as they are. **For E142**: `e141.json` is the aifoundry3 footing its card-term rules X1 and X2 read.

## Files

`scored.json` and `results.md` (primary, with every arm's verdicts), `scored-nodips.json` and `results-nodips.md` (dips removed, scored alone),
`e141*.json`, `runs*.csv`, `reduce*.txt|log` (the reduction and each arm: leakage 0.1994, 0.3803, 0; dips removed; gates off), `score*.log`,
`code.sha256`, `logs/` (the session log, the queue, the session's two config reads, the device-command preflight, the binaries' hashes, the
pre-commit dry runs, the order of events), `aifoundry3/e141/p1411*`, `aifoundry3/e141-smoke/p14101`, `aifoundry3/e141-stoptest/p14102` (raw,
as copied from the box; the reduction's `dir` fields point here), `aifoundry3/logs/` (the box's copy of the logs).
