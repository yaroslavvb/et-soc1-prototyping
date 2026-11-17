# E206 arm B: MM1-v1's forecasts, frozen before arm B's first datum

**What.** MM1-v1's forecasts for E206's 113 arm B points (aifoundry1 card 1 at 600 MHz: the points of
`tools/claims-v3/e206/points-e206.csv` with `on_arm_B` true; by family star 28, subset 16, square 14, zeros 14, kladder 13, extreme 13, kinds 8, anchor 7; by format fp32 50, fp16 18, int8 45): the cycles an op (the slowest
minion's, and the counter's mean), the cycles and seconds a GEMM, the watts and joules over idle (with the affine form `A + B / t` for
scoring given the measured seconds) and the transistor-switch estimate, with the timing simulation's two columns beside, made by the frozen
predictor in this folder **unchanged**. This is a freeze line for arm B: the commit that adds this file was pushed to GitHub before arm B's
first card command (arm B books the card from 00:00:30 PST Tue 17 Nov 2026 at the earliest), so the forecasts are blind for arm B. Desk only:
nothing here is a measurement.

| file | sha256 |
|---|---|
| `forecasts-e206-armB.csv` (one row a point) | `3f9340020c061a264254b4497039127dd46f55c37d51f891abb8930cc5b8f02a` |
| `forecasts-e206-armB.json` (every quantity the predictor returns, the arguments, the inputs' sha256) | `98876db1655e01752ac8371118b9bed1d8be3eae4219d4d1c645cfd3cedeb4e8` |
| `forecast_e206_armB.py` (the wrapper that made them) | `6dd07c88adb2fbdca724a94228a6c2861ebbf514450079228be4d5d1a0554e16` |

The predictor as frozen and landed (commit `25d2e74e83f2`, Mon 16 Nov 2026 21:14:55 PST), unchanged: `mm1_v1.py` `6bed4a5b2b441b4464a4c320cb0b5ecb09f42aa1403ff8fb25e705cf5a680a52`, `mm1_core.py`
`3e6ff68dfe4f7eb7e2af5873a8b6df52823cc5daa95066d8292d827ada0d84aa`, `kinds_v1.py` `29728e43ce3a17ad8cdfbe8a60ba12f4a5a9aa73fb603b71b62b9b4e7d742e6a`, `out/mm1_v1_params.json` `4e97654ea01e293bc61fab0fa73e8c25128af574a602e7384a14683d3b208408`;
`SHA256SUMS` checked, 77 of 77 equal, by the wrapper before it ran. `SHA256SUMS-e206-armB` lists this
note and the three files above.

**When.** Made at 21:16:41 PST Mon 16 Nov 2026 on aifoundry2 (`/usr/bin/python3` 3.12.3, numpy 1.26.4, run `-I -B`). No E206 arm B
datum was in any ref then (checked 21:16:54 PST: E206 step 2's own search, `docs/reports/data/*e206*-aifoundry1-c1*`, and the gate-stop form, over every
GitHub head and tag and the lab clone's refs: none; the only E206 data folder is arm A's). The freeze time is the push time of the commit that
adds this file.

**How.** `/usr/bin/python3 -I -B forecast_e206_armB.py --out <dir>`, run from this folder, writes both files byte for byte (it was run twice:
equal). It refuses to run if any file `SHA256SUMS` lists differs from it, and it never overwrites. It calls
`mm1_v1.Model(out/mm1_v1_params.json).predict` once a point, with the arguments `compare_e206.py` gives arm A's points and card 1's in place
of aifoundry3's:

- card `aifoundry1 card 1` (MM1-v1's key `c1`): ledger v2's card-1 zeros anchors and kind rows, MM1-v1's fitted card-1 awake power and its
  one memory-path power; 600 MHz; G = 0;
- **0.517 V, so s_V = 1**: the volts on every card-1 row of MM1-v1's energy fit (`inputs/gemm_table.json`, E190's 18 card-1 points). At 0.517 V
  the predictor gives MM1-v1's own in-sample card-1 watts (`out/points_energy_v1.csv`) within 0.10 W; at 0.499 V (ledger v2's volts
  entry for card 1, which the predictor does not read) it gives them 0.42 to 0.96 W low. README section 7's card-1 worked example is on the same footing (5.75 J over idle for E190's 8,192^3 fp32 GEMM at 0.517 V; at 0.499 V the same call gives 5.44 J). These forecasts use
  the fit's volts; at 0.499 V only the rate term would change, by (0.499 / 0.517)^2 = 0.932;
- each point's shire mask, ops a minion and values from the registered list (minions = 32 x the mask's shires, equal to the registered
  minions at all 113 points); the data kind as `compare_e206.py` builds it (random and zeros from ledger v2's own rows).

A desk check of the convention, run before the freeze: the same wrapper with aifoundry3's arguments (0.522 V) gives MM1-v1's own in-sample
arm A rows (`out/compare_e206.json`) exactly, at 119 of 119 points in time and 115 of 115 in energy.

**Not forecast.** Energy at 8 points (time at all 113): the four real-tile points (p111, p113, p114, p115: ledger v2 has no card-1 row for
E206's real tiles) and the four sparse50 points (p116, p117, p118, p119: no resident price anywhere, as on arm A). J at rest: MM1-v1 carries a rest
law for aifoundry3 only; a J at rest is the run's measured rest x seconds + the J over idle.

**Labels and limits.** Every constant of MM1-v1 is a desk fit made after its own data existed (post hoc as an act), E206 arm A included: the
113 arm B points all ran on aifoundry3 in arm A and are in MM1-v1's fit there, so what is blind here is card 1. Card 1's awake power rests on
one GEMM shape in three formats (E190); MM1-v1's own leave-one-card-out reading for card 1 was 4.2% in cycles and 14.2% in W over idle (README
section 5.1: held out, not blind). E208, the model session's own matmul sweep, ran sessions on card 1 before this freeze: 25 of the 113 arm B configurations (arm, format, data kind, mask) are among its 74 arms (`tools/claims-v3/e208/proposal/src/arms.json`), and by its registered table (`tools/claims-v3/e208/E208.md` section 3) 25 of them were among the arms its card-1 sessions S1 and S2 ran. Those card-1 sessions' data were committed to this repository tonight (a1c1-S1 (d40b6fe8, 20:32:40 PST), a1c1-S2 (76fb5344, 20:33:09 PST)), after MM1-v1's constants were fitted and frozen (the parameter file README section 1 lists, frozen at 19:54 PST from inputs vendored at d7e4f35e; `inputs/MANIFEST.json` names no E208 file). Neither the predictor nor this wrapper reads E208's data; for the configurations E208 ran on card 1 first, these forecasts were made without that datum but not frozen before it. The
switch counts are estimates (README section 7), never scorable. Scope: rgm136's GEMM on its grid (every row's `scope`).

Q201, lane mm1v1-armB. SPDX-License-Identifier: Apache-2.0
