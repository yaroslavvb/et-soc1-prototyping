# E140: the power-and-heat model M6 against blind pool 4 - heat holds, power is biased high and its intervals under-cover (aifoundry3 card 0, 600 MHz)

*On the kinds page, [section 11, what is still open](https://spacesheep.dev/@yaroslavvb/horace-kinds-of-numbers#11-what-is-still-open):
item 6, "a power model across kinds", tested out of sample. Mon 2 Nov 2026 (week 45), Q137. Pre-registered in `aa6c0a54` (committed 16:10:25, pushed
16:10:27 PST), before the claim and before any card ran a tile of the pool: [`tools/claims-v3/e140/README.md`](../../../../tools/claims-v3/e140/README.md).
The model is Q137(m)'s M6, frozen in `6a713a9f` (15:56 PST), its predictions for the pool in `03fcd720` (16:06 PST); the pool,
[blind pool 4](../../../../tools/claims-v3/kinds/blind4/README.md), 25 tiles written by a designer who never saw the model, in `67fe20a9`
(15:33 PST). aifoundry3 card 0 at 600 MHz in every sample; `ettelem config` read at the session's start (16:43:09, the smoke's), at both
ends of the smoke and of every pass, and at the queue's end (17:15:03): TDP 0 W, threshold 65 °C, max_power, 600 MHz, 523 mV (522 mV at
three reads: the ends of 14011 and 14012 and the session's end), never set. **Every device-management command sent was a read** (nine kinds, two of them PMIC voltage-register reads,
which the owner's rule of 2 November 2026 allows); no write (`since_reset_ms` −1 in all 18,552 samples). Card session 16:43:09–17:15:03
PST, **31.9 of the 35 card-minutes allowed**: the smoke 14001 and all four registered passes, 14010–14013 (438–469 s each).*

**In plain words.** M6 predicts a matmul's power (watts over the same kernel on zeros) and its heat (how far the die warms in a 4.5 s
run) from the numbers it multiplies. Its makers scored it on the 22 experiments it was fitted on, leaving one kind out at a time. E140
ran 25 kinds nobody fitted on this card. **Heat holds**: the die's rise is predicted to 0.20 °C rms on the floats and 0.16 °C on int8,
inside what the nested score says, and 24 of 25 tiles fall inside M6's own 95% intervals (H1, H2, H3 PASS). **Power passes its rms tests
but is biased**: M6 predicts 0.28 W too high on average (0.38 W on fp32), its rms is 0.41 W on the floats and 0.38 W on int8, near the top
of what its nested score allows (P1, P2 PASS), and **only 19 of 25 tiles fall inside its 95% intervals, against the 21 the rule needs:
P3 FAILS** on the registered primary. On the reported arm with the board meter's dips removed, which keeps the two passes the primary
set aside, every rule PASSES (power rms 0.27 W floats, 0.34 W int8; 21 of 25 inside), so P3's FAIL is arm-sensitive.

## Results

**Two of four passes kept on the registered primary** (E78's reduction unchanged: leakage `auto`, dips kept, E78's run and pass gates):
14012 and 14013. **14010 and 14011 were set aside by E78's registered pass gates** (`fp32.randn` spans 2.489 W in 14010, over the 1.0 W
random-range gate; `anchor_pi` drifts +0.715 W in 14011, over the 0.60 W drift gate). Every tile has its two kept passes; the rules
need at least two ([`results.md`](results.md), [`scored.json`](scored.json)).

**1. The registered verdicts.**

| rule | quantity | set | reading | the nested score's interval | verdict | dips removed (4 passes) | leak 0.1994 | leak 0.3803 | leak 0 | gates off |
|---|---|---|---|---|---|---|---|---|---|---|
| **E140-P1** | power | priority-1 floats (14) | rms **0.406 W** | 0.114–0.474 | **PASS** | PASS 0.274 | PASS | FAIL | FAIL | PASS |
| **E140-P2** | power | priority-1 int8 (6) | rms **0.384 W** | 0.101–0.434 | **PASS** | PASS 0.342 | PASS | PASS | PASS | PASS |
| **E140-P3** | power | all 25 | **19 of 25** inside M6's 95% | ≥ 21 | **FAIL** | PASS 21 | PASS | FAIL | FAIL | FAIL |
| **E140-H1** | die rise | priority-1 floats (14) | rms **0.204 °C** | 0.188–0.403 | **PASS** | PASS 0.134 | PASS | PASS | PASS | PASS |
| **E140-H2** | die rise | priority-1 int8 (6) | rms **0.164 °C** | 0.080–0.271 | **PASS** | PASS 0.061 | PASS | PASS | PASS | PASS |
| **E140-H3** | die rise | all 25 | **24 of 25** inside | ≥ 21 | **PASS** | PASS 25 | PASS | PASS | PASS | PASS |

Arm-sensitive: P1 (FAILS at leakage 0.3803 and 0 W/°C) and P3 (PASSES with dips removed and at leakage 0.1994). Heat is not
arm-sensitive. The frozen expectation was all six PASS: P3 did not.

**2. Where power misses** (measured − M6, W; all 25 tiles, primary):

| format | tiles | mean error (bias) | rms | outside M6's 95% |
|---|---:|---:|---:|---|
| fp32 | 11 | **−0.38** | 0.50 | `a_exp_busy_b_const` −0.79, `real_qwen_q_down` −0.97, `wideexp_bgate_alt` −0.71 |
| fp16 | 7 | −0.19 | 0.25 | `pair_cancel` −0.48, `wideexp_gate30` −0.36 |
| int8 | 7 | −0.20 | 0.37 | `b_line_flipflop` −0.56 |
| all | 25 | **−0.28** | 0.41 | 6 tiles, all over-predicted |

Every miss on the primary is M6 predicting too much power. *(Corrected after verification, C2.)* **Two of the six are the board
meter's dips, not the model**: `fp32.a_exp_busy_b_const` read 11.975 and 10.816 W in its two kept passes and `fp32.real_qwen_q_down`
17.521 and 16.780; with dips removed the same passes read 11.992 / 12.002 and 17.971 / 17.959 W and both tiles fall inside M6's
intervals. The four left are the two wide-exponent gate tiles (named in advance as M6's steady-gate overprediction), the fp16 pair that
cancels every two-term update, and int8's whole-line flip-flop (named in advance); `fp32.a_exp_busy_b_const` (case 3) was named in
advance too. `fp32.denormals_only`, also named, read −0.37 W, inside. On the dips-removed arm the bias shrinks to −0.15 W (fp32
−0.18), the rms to 0.28 W, and the misses are not all one-sided: `int8.a_full_b_const` falls outside there, under-predicted by +0.53 W.

**3. Heat** (measured − M6, °C): bias +0.03 °C over all 25 (fp32 +0.08, fp16 −0.05, int8 +0.02), rms 0.22 °C; the one tile outside
its interval is `int8.band_a` (+0.37 °C, a 1.0 °C reading against 0.63 predicted). The die reads in whole degrees; `dT_win` is a window mean, so it is fractional (2.775, 1.737), but the small int8 rises land on 0.5 or
1.0 °C; that floor is inside M6's reference. **The rise against the quoted 0.118 °C per board W** (reported): a line through the origin
of each run's `dT_win` on its S gives 0.119 °C per W on the primary's 86 tile runs and 0.118 on the dips-removed arm's 172.

**4. What it does to predicting power and heat** (the before/after the owner's goal asks for):

| | before (M6's nested leave-one-kind-out score) | after (blind pool 4, this card, primary) | dips removed |
|---|---:|---:|---:|
| power, fp32 | 0.227 W rms | 0.50 W (bias −0.38) | 0.28 W |
| power, fp16 | 0.179 W | 0.25 W (bias −0.19) | 0.22 W |
| power, int8 | 0.260 W | 0.37 W (bias −0.20) | 0.32 W |
| power, 95% intervals | 95% | 76% (19 of 25) | 84% (21 of 25) |
| heat, fp32 / fp16 / int8 | 0.304 / 0.283 / 0.175 °C | 0.18 / 0.27 / 0.21 °C | 0.12 / 0.20 / 0.07 °C (four passes, not dips: gates-off gives the same) |
| heat, 95% intervals | 95% | 96% (24 of 25) | 100% |

So: **the heat prediction's stated error can be quoted for new kinds** (die rise ≈ 0.118 °C per board W, within about 0.2 °C over a
4.5 s run on this card). **The power prediction's cannot yet, as stated**: on new kinds M6's power error is up to about twice its
nested score on fp32 and one-sided (too high), so its 95% intervals cover about three in four. The bias points at what to change: the
over-predicted tiles are those where M6 counts bits that switch in its bench but cost less on the card (wide exponents beside gated
zeros, exponent-only activity, mantissas with many zero low bits). *(Corrected after verification, C1: this said M5's predictions for the pool were not provided; they were, frozen into
`predictions-e140.json` › `tiles.*.power_m5`, and `scored.json` › `primary.reported_m5` reports them.)* **M5, the model M6 replaced,
does better on this pool**: P1's tiles M5 0.337 W rms against M6's 0.406, P2's 0.379 against 0.384; all 25 tiles 0.358 against 0.406, M5
better in every format (0.44 / 0.15 / 0.37 W against 0.50 / 0.25 / 0.37); dips removed, P1 0.166 against 0.274. So M6's added per-flip
terms did not improve the out-of-sample power prediction here; heat is new in M6 and has no M5 counterpart. **The anchors** (reported,
D in W): this session's kept passes `fp32.randn` 24.44, `fp16.randn` 21.85, `int8.full` 7.01 (dips removed 24.51, 21.97, 7.08), against
E115's 24.64, 22.07, 7.15 on this card (its `runs.csv`): about 0.1-0.2 W lower, the size of the session-to-session spread M6's
reference carries. **Better than the nested score:** on the dips-removed and gates-off arms H1 (0.134 °C) and H2 (0.061 °C) fall below
their intervals' 2.5% points (0.188, 0.080): heat there reads better than the nested score says.

## Registered against what happened

| | registered | happened |
|---|---|---|
| passes | 14010–14013, the budget rule decides (2,040 s); at least 2 kept | four ran (438–469 s); **two kept** (14012, 14013) |
| card time | ≤ 35 min | 31.9 min |
| stops | die ≥ 70 °C; board ≥ 65 W | highest die 62 °C, board 54.17 W; no stop |
| form check | config 0 W / 65 °C / 600 MHz; `since_reset_ms` −1 | PASS (`logs/a1-form-check.txt`), made after the smoke and before `go` |
| expectation | all six PASS | P3 FAIL; five PASS |
| departures | — | **D1**: E78's pass gates set aside half the passes. Both gate readings (a 2.49 W span of `fp32.randn`, a 0.72 W tie drift) are of the size the board meter's dips make (E82 A2); the registered dips-removed arm keeps all four passes and is reported, never the verdict. **D2**: at about 16:42 PST, before the smoke, the registration's earlier no-device dry pass (made by the preparing lane at 15:41 from an uncommitted copy, `build/claims-v3-dry/`) was renamed aside so `setup` would rerun its dry pass on the registered files; it did (47 launches, 25 on pool tiles). **D3**: the collector's Python was numpy through `uv` on the Intel |

## Device commands sent

As registered (the registration's § Device commands sent): E78's harness unchanged, `ettelem config` at both ends of the smoke and of
every pass and at the session's end, `ettelem sample` at 10 Hz; GET_MODULE_STATIC_TDP_LEVEL, GET_MODULE_TEMPERATURE_THRESHOLDS,
GET_MODULE_POWER_STATE, GET_ASIC_FREQUENCIES, **GET_ASIC_VOLTAGE**, GET_MODULE_POWER, GET_SP_STATS, GET_MODULE_CURRENT_TEMPERATURE,
**GET_MODULE_VOLTAGE**: **all READs**, the two in bold PMIC voltage-register reads. Never sent: the statistics reset, any SET_*, the
firmware-revisions query, a residency read. The host program (`sparsity_host`, `20e760c2…`) opens the ops node only. Checker: NO-GO
bare, GO with the reviewed `lib.sh:154` exception (`block_e140.sh:98`), 31 sites (the registration's `dmcmd-audit*.txt`). Residual:
aifoundry3's 7 Oct thermal build is not public.

## Card and post

`et-who` before the smoke (16:43) and at the queue's end (17:15:03): no process held a device node or card lock; other users' idle
logins were present, no device process of theirs. The day's post (message 1566837317765963987) had its aifoundry3 clause rewritten at
16:43:0x PST to "using aifoundry3 for 1 h, until ~17:40 PST" (EXPECT_TEXT, dry run, then save), and at 17:15:42 PST, the last card held,
" — released" was appended to that text, every word kept: "<ai> **Claude says:** using aifoundry3 for 1 h, until ~17:40 PST
[doc](<https://spacesheep.dev/@yaroslavvb/horace-kinds-of-numbers>) — released".

## What it changes

- **Item 6**: answered for heat (M6's heat term holds out of sample, with intervals that cover), and **not yet for power**: on new kinds
  M6 over-predicts (−0.28 W bias; two of its six misses are meter dips) and does no better than M5 and its intervals under-cover (19 of 25, registered FAIL; 21 of 25 with dips removed).
- **The model**: a next fit should look at the six over-predicted tiles' cases before widening any interval; E138's per-position int8
  B prices and E139's encoded-toggle term are two terms measured today that M6 does not carry.

## Files

`scored.json` and `results.md` (primary), `scored-nodips.json` and `results-nodips.md` (dips removed), `e140*.json`, `runs*.csv`,
`reduce*.txt|log` (the reduction and each arm), `score*.log`, `code.sha256`, `logs/` (queue, session reads, form check, dry run),
`aifoundry3/kinds/p1401*`, `aifoundry3/kinds-smoke/p14001` (raw), `aifoundry3/logs/` (the box's copy of the logs).

## Corrections after verification (Mon 2 Nov 2026)

*An independent verifier regenerated the freeze byte for byte, re-derived every tile, rms, coverage count and bootstrap interval with its
own code, and reproduced all six verdicts on every arm. Its faults are corrected in place; no rule, prediction, number or verdict changed.*

- **C1 (substantive)**: M5's frozen predictions were in the registration and are reported: M5 beats M6 on this pool (in place, § 4).
- **C2 (substantive)**: two of the six power misses are meter dips on the kept passes, and on the dips-removed arm one miss is
  under-predicted (in place, § 2).
- **C3**: the registered reported items added: M5's rms, the anchors against E115's, the rise per board W, and "better than the nested
  score" for H1 and H2 on two arms.
- **C4** (wording): the bias is −0.28 W (−0.2753; the commit subject's −0.27 stands as written); `dT_win` is fractional; the
  registration's push time; the three 522 mV reads; `fp32.a_exp_busy_b_const` was named in advance; the heat column's improvement
  comes from four passes, not from removing dips.

*Dated note, Tue 3 Nov 2026 (Q138's records; Q138(b)'s finding): two of the fp32 tiles scored here, `fp32.wideexp_bgate_alt` (−0.71 W, one of the misses above) and `fp32.wideexp_agate_rows`, hold the accumulator C at ±Inf from the first op in 109 and 133 of their 256 elements, with no NaN, by the desk's emulation of the pool's C ([`tools/claims-v3/kinds/blind5/CORRECTIONS.md`](../../../../tools/claims-v3/kinds/blind5/CORRECTIONS.md) § C2; `corrections-check.json` › `blind4.c_op1_nonfinite_of_256`). So part of the wide-exponent miss may come from a result path held at infinity rather than from the exponents themselves. It is an emulation, not a measurement; no number, rule or verdict here changes, and the frozen text above is as committed.*
