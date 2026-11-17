# E207: MM1-v2's forecasts for the blind matmul day, frozen before E207's first card command

**What.** MM1-v2's forecasts for E207's 53 points (47 cases; aifoundry3 card 0 at its pinned 600 MHz, rgm136 unchanged). The points are
MM1-v1's blind-day list (`../v1/out/mm1_v1_blind_day.csv`, landed in 25d2e74e), which E207's registration reads and never re-chooses
(`tools/claims-v3/e207/points-e207.csv`). By family: inside the L3 9, the knee 9, past the L3 8, subsets 8, stride 7, kinds 6, int8 one K
block 3, long K 3; by format fp32 31, int8 18, fp16 4. For each point the forecast gives:

- the cycles an op (the slowest minion's, and the counter's mean) and the cycles and seconds a GEMM;
- the watts and joules over idle, with the affine form `A + B / t_us` for scoring given the measured seconds;
- the rest law's J at rest (REPORTED);
- the transistor-switch estimate, with the timing simulation's two columns beside.

They were made by the predictor in this folder **unchanged**. Desk only: nothing here is a measurement.

**Blindness: BLIND.** The commit that adds this file was pushed to GitHub before E207's first card command and before any lane booked
aifoundry3 for it. Checked at 02:03:44-02:03:45 PST Tue 17 Nov 2026:

- the round's booking list held no booking of any box;
- E207's card lane had not started;
- no E207 datum was in any ref. Every GitHub ref was fetched and searched, and the lab clone's refs too: no commit adds a
  `docs/reports/data/*e207*` path, and no subject is an E207 data commit. E207's registration and run kit were not yet in any ref.

The lane's commit script repeated this check right before the commit and would have stopped had any of it changed. The freeze time is the
push time of the commit that adds this file.

| file | sha256 |
|---|---|
| `forecasts-e207.csv` (one row a point) | `873360bb7ef028c4922f6f55c6c61133a32da28fa6e19a6a02fa7f77d45d63d3` |
| `forecasts-e207.json` (every quantity the predictor returns, the arguments, the inputs' sha256) | `3dc28ccb3a3e37c796d04a20729b14ea087057b0166ab5d84d6368b62db8171f` |
| `forecast_e207.py` (the wrapper that made them) | `91a604a1eb5e960d366b6c5d0b4f5b79f9d5a1a25b24c39c51eb96a9f9a6b4ad` |

The predictor is unchanged, as frozen and landed in commit `3ca4b71799`, pushed 01:44:48 PST Tue 17 Nov 2026:

- `mm1_v2.py` `5abf3a0a49757e15a776f3a1b5cdb4f7fa90943de2e016fe8b26aa4bf5324c08`
- `mm1_core_v2.py` `f78c21b4f8b4c43a9a6c7319f12092937e9e92c69d3e7dc036f0e1f92b9d7e08`
- `kinds_v2.py` `14c72c298956c551439a6eddb77f9d75a7b7fe3414cbb78cfbd0ad5a70ed686d`
- `out/mm1_v2_params.json` `9d79040bb8f86336987ff4b6aeaf7e5e6e3b2b2ba07e4bcdc4aa5f5b65c43fa5`

The wrapper checked `SHA256SUMS` before it ran: 114 of 114 equal. `SHA256SUMS-e207` lists this note and the three files above.

**When.** Made at 02:00:32 PST Tue 17 Nov 2026 on aifoundry2 (`/usr/bin/python3` 3.12.3, numpy 1.26.4, run `-I -B`). It was run twice,
once with E207's registration points file checked and once without it; the outputs were byte for byte equal.

**How.** `/usr/bin/python3 -I -B forecast_e207.py --out <dir>`, run from this folder, writes both files byte for byte. It refuses to run if
any file `SHA256SUMS` lists differs from it, or if MM1-v1's list is not the landed one, and it never overwrites. It calls
`mm1_v2.Model(out/mm1_v2_params.json).predict` once a point:

- **the card and clock:** `aifoundry3 card 0` (MM1-v2's key `a3`) at 600 MHz. E207 sets nothing and the card is pinned, so MM1-v2's two
  clock routes (given the measured clock, and with the clock forecast) are the same call, and no governor model is used;
- **volts and governed base:** the predictor's defaults for this card, 0.522 V (s_V = 1.019) and G = 0;
- **mask and size:** the shire mask and the ops a minion from the list; minions = 32 x the mask's shires;
- **the data kind**, as MM1-v1's blind day built it:
  - random: ledger v2's own rows;
  - e37 (b42, b43): ledger v2's `fp32.small_int`, with the e37 generator's phi;
  - blind4 (b49-b51) and blind3 (b52): their own sources;
- **the rest law's start die:** its forecast, 54.4 C.

E207's registration points file (`tools/claims-v3/e207/points-e207.csv`, sha256 `1e6067bcf0fc123c81bf927472bbc27a312b64139de5890add3b4c2991d9b114`,
as its registration and fix lanes held it before the land) was checked against the list: 53 of 53 rows equal. The fields compared were id,
arm, format, data kind, mask as a number, shires, minions, M, N, K, ops, values and the watts flag.

One spelling differs: b37's mask is `0x0f0f0f0f` in MM1-v1's list and `0xf0f0f0f` in E207's. It is one number, and the predictor gives the
same numbers for both spellings (checked). The rows carry E207's spelling in `mask` and `case`, and MM1-v1's in `mask_in_mm1_v1_list`.

**A desk check of the convention**, run before the freeze: the same arguments on E206 arm A's 119 points give MM1-v2's own in-sample rows.
Those points are the card, clock and kernel MM1-v2 was fitted on here (aifoundry3 card 0, 600 MHz, rgm136).

- Cycles: 119 of 119 equal `out/points_time_v2.csv` (`v2_in`, to its 3 decimals).
- W over idle at each point's measured op time: within 0.0008% of `out/points_energy_v2.csv` (`v2_in_wg`, 109 points).

**Not forecast.** Energy at 4 points: b49, b50 and b51 (blind4's real tiles) and b52 (blind3's constant-column A). Time is forecast at all
53. MM1-v2's predictor prices a resident op only for ones, zeros, random and ledger v2's kind rows. MM1-v1 priced these four from frozen
per-tile predictions (M6, M5), which MM1-v2's predictor does not read.

**Predicted gaps to MM1-v1's frozen forecasts** (desk, not a score). These compare with `../v1/out/mm1_v1_blind_day.csv` as rms of
ln(v2 / v1), over the points both price:

| quantity | rms | detail |
|---|---|---|
| cycles an op (wall) | 3.18% | mean +1.46%; 13 of 47 cases more than 3% apart; largest +14.65% at b40, gemmL1x2x2 on 2 shires |
| the counter's mean | 3.26% | |
| seconds | 3.18% | |
| W over idle at each model's own seconds | 3.53% | from -15.46% at b40 to +3.71% at b09 |
| J over idle | 2.19% | |
| J at rest by the rest law | 2.93% | |

By family (cycles, mean): subsets +5.6%, the knee +3.4%, long K +1.6%, every other family within 1%.

**Labels and limits.**

- Every constant of MM1-v2 is a desk fit made after its own data existed (post hoc as an act).
- Its fit read 13 experiments on four cards (1,072 time points), among them E206 arm A (aifoundry3 card 0, E207's card and clock) and E208
  (the other three cards). E207's points never ran on any card: E207's registration and fix lanes searched and found 53 of 53 points and 47
  of 47 cases never run.
- E207's registered rules (T1-T3, E1-E4, H1-H4) name MM1-v1, F1 and F2, not MM1-v2. A score of these forecasts is REPORTED, beside them.
- MM1-v2's held-out numbers (README section 3) are held out, not blind.
- The switch counts are estimates (README section 7), never scorable.
- Scope: rgm136's GEMM on its grid (every row's `scope`).

Q202, lane mm1v2-e207. SPDX-License-Identifier: Apache-2.0
