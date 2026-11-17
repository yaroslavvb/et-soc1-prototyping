# E211: MM1-v2's forecasts, frozen before E211's first datum

**What.** MM1-v2's forecasts for E211's 26 points and 3 smoke processes (THE SECOND KERNEL, on aifoundry3 card 0 at its pinned 600 MHz, the full chip: rgm211's `gemmLn` arms, their rgm136 `gemmL` twins, and rgm136's non-cooperative `gemmLnc` under rgm211's host; `tools/claims-v3/e211/points-e211.json`), made by the predictor in this folder **unchanged**, through E211's committed desk map re-run at MM1-v2's own L3 retention: the cycles an op (the slowest minion's, and the counter's mean), the cycles and seconds a GEMM, the watts and joules over idle (with the affine form `A + B / t` for scoring given the measured op time), J with the card at rest by v2's rest law (REPORTED), the transistor-switch estimate and the timing simulation's two columns; and the ratios rgm211 / rgm136 per pair, with MM1-v1's frozen ratios beside. This is a freeze line: the commit that adds this file was pushed to GitHub before E211's first card command, so the forecasts are blind for E211. Desk only: nothing here is a measurement.

| file | sha256 |
|---|---|
| `forecasts-e211.csv` (one row a point) | `2d1af89701275d531ed8c980101d4eb74a3c85605fa6ce01ed0cd60caf0fa35b` |
| `forecasts-e211.json` (every quantity the predictor returns, the columns beside it, the pairs, family C, the inputs' sha256) | `0dce8a5e9ae3a593cfd5af6d9d399f7db337c37c36edcd04ddf6ba78baedecce` |
| `map-e211-v2.json` (E211's desk map at MM1-v2's retention) | `1b71536954d14c3438beee8f0e8fe4cc32f0eee1fc8e19b5b68de33661133282` |
| `forecast_e211.py` (the wrapper that made them) | `a207c4005dd087b6ca4ec704cf2b70b44dbf6f5afd4fa1427199c08571d37c31` |

**The predictor as landed** (commit `3ca4b7179979`, pushed 01:44:45 PST Tue 17 Nov 2026), unchanged: `mm1_v2.py` `5abf3a0a49757e15a776f3a1b5cdb4f7fa90943de2e016fe8b26aa4bf5324c08`, `mm1_core_v2.py` `f78c21b4f8b4c43a9a6c7319f12092937e9e92c69d3e7dc036f0e1f92b9d7e08`, `kinds_v2.py` `14c72c298956c551439a6eddb77f9d75a7b7fe3414cbb78cfbd0ad5a70ed686d`, `out/mm1_v2_params.json` `9d79040bb8f86336987ff4b6aeaf7e5e6e3b2b2ba07e4bcdc4aa5f5b65c43fa5`; `SHA256SUMS` (`eafb6558c4eaa053e4e33b8a4d6b2a644175f325df9e9ba56a1b6373b556f2f2`) checked, 114 of 114 OK, by the wrapper before it ran. **E211 as landed** (registration `1393a64935c0`, kit `2b7f261f8db9`): `desk/map_e211.py` `36319654d3e8a7954baabfafb5932dedbb46026a9b3998b49ce2f1d2b13bd01b`, `desk/map-e211.json` `02675c8f3bacb21d880e6d88b3433571950a0ac01b49b699fcf0e7641f7eec91`, `points-e211.json` `234b496a9488eb078734e0c26ff833fe56ab5b4194e4ddc7f7f9d20141f5a537`, `forecast-e211.json` `90e8d1ae4c68c162eab687624f72bf15599ae26d2050012c3381f179453108f5`, `SHA256SUMS-e211-registration` `477fb113cd6a6b6cd3cea12b1ff7ca6264e55a7b1e2fb5a40e9aeb3a99bac166`. `SHA256SUMS-e211` lists this note and the four files above (`sha256sum -c SHA256SUMS-e211` from this folder).

**When, and blindness.** Made at 2026-11-17 08:03:22 PST on aifoundry2 (`/usr/bin/python3` 3.12.3, numpy 1.26.4, run `-I -B`), from GitHub main `c83a29d133d7`. No E211 datum was in any ref then (checked 2026-11-17 08:07:07 PST: E211 step 2's own search, `docs/reports/data/*e211*`, over every GitHub head and the lab clone's refs: none), and E211's card lane had not booked aifoundry3 (the round's bookings, read 2026-11-17 08:07:07 PST). The freeze time is the push time of the commit that adds this file.

**How.** `/usr/bin/python3 -I -B forecast_e211.py --out <dir>`, run from anywhere, writes the three outputs byte for byte (it was run twice: equal); `--check` re-makes them in memory and compares them with the files here. It refuses to run if a pinned input or any file this folder's `SHA256SUMS` lists differs from its pin, and it never overwrites.

- **The map at v2's retention.** E211's tool (`tools/claims-v3/e211/desk/map_e211.py`, imported from its path, not edited) makes the exact LRU stack distance of every operand request of the whole chip's lock-step request stream for each walk, its L2 model and its analysis, for its own 13 shapes in both walks; the analysis runs at MM1-v2's retention (x50 39.74 MB, s 4.535 MB, zeta 0.7205) beside MM1-v1's (43.59, 7.14, 0.679), as E211's registration lane recorded a v2 forecast needs (E211.md section 0, in A1's dated clause, names these files MM1-v2's E211 column, outside E211's pinned folder). **The remake check**, every run: PASS: at MM1-v1's retention the tool re-made desk/map-e211.json's entry number for number at 26 of 26 shape-walks (13 shapes, both walks); every section but the logistic one is retention-free and equal at both retentions. The map's logistic section keeps the tool's key name (`mm1v1_logistic`) and records the retention it was made at (MM1-v2's here); the F1 anchors are not re-made (F1 is not MM1-v2's).
- **v2 through the map** (E211.md section 6's MM1, with MM1-v2 in MM1-v1's place): each point's walk's op classes (Q0, Q1) from the map in place of v2's closed form, the map's shape object handed to v2's own `Model.predict`; v2's stride rule r1 carried literally in both walks (B's second-use retention x zeta where NB is a power of two >= 4 and the footprint passes 32 MB, piF0 on B's first-use fresh stream where NB is a power of two >= 4: of E211's shapes, 2x8x4 only).
- **The arguments**: `aifoundry3 card 0`, 600 MHz, v2's own defaults for that card (0.522 V, no governed base); random data (ledger v2's fp32 randn and int8 full rows on aifoundry3); 1,024 minions; the ops a minion a GEMM as E211's points file gives them (v2's own count is equal to it at every point).
- **Beside v2, E211's own forms on v2**: `v2S`, E211's sharing-aware rule (A's fresh lines a shire-op priced twice, v2's bF and dF); `v2cf`, v2's own closed form at the gemmL points (REPORTED); family C: `v2-C0` (v2 literally: no load-mode term, so gemmLnc = its twin), `v2-C1` (E211's registered rule C1, E101's measured one-block figures, carried on v2's twin) and `v2-C2` (REPORTED).

**The frozen answer** (desk; rgm211 over rgm136 at the same shape; MM1-v1's ratios as E211 froze them, `forecast-e211.json` > `pairs`):

| pair | shape (fmt) | wall cycles: v2 | MM1-v1 (frozen) | ln(v2 / v1) | counter mean: v2 | J over idle: v2 | MM1-v1 (frozen) | v2S |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| w01 | 2x3x2 fp32 | 0.999 | 0.999 | -0.000 | 0.999 | 0.994 | 0.994 | 0.993 |
| w02 | 3x3x4 fp32 | 1.063 | 1.044 | +0.018 | 1.063 | 1.015 | 1.011 | 1.022 |
| w03 | 3x6x3 fp32 | 0.933 | 0.968 | -0.037 | 0.933 | 0.986 | 0.994 | 0.978 |
| w04 | 2x8x4 fp32 | 0.859 | 0.881 | -0.024 | 0.859 | 0.966 | 0.969 | 0.959 |
| w05 | 2x9x4 fp32 | 0.890 | 0.895 | -0.006 | 0.890 | 0.970 | 0.969 | 0.964 |
| w06 | 3x5x7 fp32 | 1.231 | 1.181 | +0.041 | 1.231 | 1.022 | 1.018 | 1.104 |
| w07 | 3x6x6 fp32 | 1.234 | 1.146 | +0.074 | 1.234 | 1.023 | 1.011 | 1.107 |
| w08 | 4x3x6 fp32 | 1.251 | 1.248 | +0.002 | 1.251 | 1.034 | 1.041 | 1.104 |
| w09 | 6x6x6 fp32 | 1.257 | 1.236 | +0.017 | 1.257 | 1.020 | 1.022 | 1.111 |
| w10 | 3x5x7 int8 | 1.231 | 1.181 | +0.041 | 1.231 | 1.045 | 1.037 | 1.204 |
| x01 | 1x5x5 fp32 (control) | 1.000 | 1.000 | +0.000 | 1.000 | 1.000 | 1.000 | 1.000 |
| x02 | 3x1x8 fp32 (control) | 1.000 | 1.000 | +0.000 | 1.000 | 1.000 | 1.000 | 1.000 |

**In short** (desk): v2 puts rgm211's wall cycles an op at 1.231-1.257 of rgm136's where A is the far operand (w06-w10; MM1-v1 1.146-1.248), 0.859-0.890 where B's large panel was the far operand (w04, w05; v1 0.881-0.895), 0.933-1.063 inside the L3 and at the knee (w01-w03; v1 0.968-1.044), and 1 at the controls, where the two walks are one op stream; like MM1-v1 it has no term for the two ELFs' compiled loops (rgm136's own gemmL against rgm211's), so any code-path offset between them reads at the controls on the card, not here. J over idle moves far less than the time (the op count is equal and v2's W falls as its op time rises).

The stride readings at 2x8x4 with v2 (the wall ratio): the literal carryover (v2's forecast) 0.859; no stride term 0.887; zeta on both halves 0.895; the stride on rgm136's walk only 0.763. Family C (gemmLnc over its twin): v2-C0 1 in everything; v2-C1 the wall 0.956, the counter's mean 0.915, J over idle 1.167 (2x3x2) and 1.152 (3x5x7).

Every point (desk; v2 through the map; seconds and joules a GEMM; J at rest by v2's rest law for aifoundry3, REPORTED):

| point | arm | fmt | wall | mean | seconds | W over idle | J over idle | J at rest (REPORTED) | v2S J |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|
| w01m | `gemmL2x3x2` | fp32 | 891.8 | 792.0 | 0.001142 | 23.76 | 0.02712 | 0.05536 | 0.02714 |
| w01n | `gemmLn2x3x2` | fp32 | 891.2 | 791.5 | 0.001141 | 23.62 | 0.02694 | 0.05517 | 0.02696 |
| w02m | `gemmL3x3x4` | fp32 | 1090.0 | 1078.1 | 0.004186 | 20.29 | 0.08492 | 0.18847 | 0.08799 |
| w02n | `gemmLn3x3x4` | fp32 | 1158.9 | 1146.2 | 0.004450 | 19.37 | 0.08621 | 0.19631 | 0.08996 |
| w03m | `gemmL3x6x3` | fp32 | 1087.2 | 1075.4 | 0.006262 | 20.54 | 0.12861 | 0.28355 | 0.13114 |
| w03n | `gemmLn3x6x3` | fp32 | 1014.6 | 1003.6 | 0.005844 | 21.70 | 0.12681 | 0.27140 | 0.12826 |
| w04m | `gemmL2x8x4` | fp32 | 1352.3 | 1337.6 | 0.009232 | 17.30 | 0.15969 | 0.38809 | 0.16200 |
| w04n | `gemmLn2x8x4` | fp32 | 1162.0 | 1149.4 | 0.007933 | 19.45 | 0.15431 | 0.35058 | 0.15536 |
| w05m | `gemmL2x9x4` | fp32 | 1159.3 | 1146.7 | 0.008904 | 19.70 | 0.17542 | 0.39571 | 0.17775 |
| w05n | `gemmLn2x9x4` | fp32 | 1031.3 | 1020.1 | 0.007920 | 21.48 | 0.17016 | 0.36612 | 0.17134 |
| w06m | `gemmL3x5x7` | fp32 | 1208.1 | 1195.0 | 0.013531 | 19.06 | 0.25794 | 0.59271 | 0.26512 |
| w06n | `gemmLn3x5x7` | fp32 | 1486.6 | 1470.4 | 0.016650 | 15.83 | 0.26365 | 0.67559 | 0.29271 |
| w07m | `gemmL3x6x6` | fp32 | 1186.8 | 1173.9 | 0.013673 | 19.34 | 0.26436 | 0.60263 | 0.27005 |
| w07n | `gemmLn3x6x6` | fp32 | 1464.9 | 1448.9 | 0.016875 | 16.02 | 0.27032 | 0.68784 | 0.29888 |
| w08m | `gemmL4x3x6` | fp32 | 1191.4 | 1178.4 | 0.009150 | 19.06 | 0.17438 | 0.40076 | 0.18144 |
| w08n | `gemmLn4x3x6` | fp32 | 1490.4 | 1474.2 | 0.011447 | 15.75 | 0.18031 | 0.46351 | 0.20040 |
| w09m | `gemmL6x6x6` | fp32 | 1186.9 | 1173.9 | 0.027345 | 19.34 | 0.52872 | 1.20526 | 0.54010 |
| w09n | `gemmLn6x6x6` | fp32 | 1491.7 | 1475.5 | 0.034369 | 15.69 | 0.53937 | 1.38968 | 0.59978 |
| w10m | `gemmL3x5x7` | int8 | 1208.1 | 1195.0 | 0.013531 | 9.46 | 0.12804 | 0.46281 | 0.13522 |
| w10n | `gemmLn3x5x7` | int8 | 1486.6 | 1470.4 | 0.016650 | 8.03 | 0.13375 | 0.54569 | 0.16280 |
| x01m | `gemmL1x5x5` | fp32 | 1057.0 | 1045.5 | 0.002819 | 21.14 | 0.05959 | 0.12933 | 0.05968 |
| x01n | `gemmLn1x5x5` | fp32 | 1057.0 | 1045.5 | 0.002819 | 21.14 | 0.05959 | 0.12933 | 0.05968 |
| x02m | `gemmL3x1x8` | fp32 | 1487.3 | 1471.1 | 0.003807 | 15.64 | 0.05954 | 0.15374 | 0.06620 |
| x02n | `gemmLn3x1x8` | fp32 | 1487.3 | 1471.1 | 0.003807 | 15.64 | 0.05954 | 0.15374 | 0.06620 |
| c01c | `gemmLnc2x3x2` | fp32 | 891.8 | 792.0 | 0.001142 | 23.76 | 0.02712 | 0.05536 | 0.02714 |
| c02c | `gemmLnc3x5x7` | fp32 | 1208.1 | 1195.0 | 0.013531 | 19.06 | 0.25794 | 0.59271 | 0.26512 |
| s01 | `gemmL2x2x2` | fp32 | 889.2 | 789.7 | 0.000759 | 23.82 | 0.01807 | 0.03684 | 0.01808 |
| s02 | `gemmLn2x2x2` | fp32 | 889.4 | 789.9 | 0.000759 | 23.65 | 0.01795 | 0.03673 | 0.01796 |
| s03 | `gemmLnc2x2x2` | fp32 | 889.2 | 789.7 | 0.000759 | 23.82 | 0.01807 | 0.03684 | 0.01808 |
| c01c (v2-C1) | `gemmLnc2x3x2` | fp32 | 852.9 | 724.7 | 0.001092 | 28.98 | 0.03163 | 0.05864 | - |
| c02c (v2-C1) | `gemmLnc3x5x7` | fp32 | 1155.4 | 1093.4 | 0.012940 | 22.97 | 0.29721 | 0.61735 | - |
| s03 (v2-C1) | `gemmLnc2x2x2` | fp32 | 850.3 | 722.6 | 0.000726 | 29.05 | 0.02108 | 0.03903 | - |

**Not scored by E211's rules.** E211 registered no MM1-v2 forecast, and its head-to-head H7 (v2 against v1) is NOT REGISTERED (E211.md sections 0 and 7); Amendment A1 added no v2 forecast, and E211.md section 0 (A1's dated clause) names these files MM1-v2's E211 column, read here, never by E211's rules or scorer. Every reading of them on E211's data is REPORTED (blind: frozen before E211's first card command). E211's card plan (`plan-e211.json`, made with MM1-v1) is not changed by anything here; the largest point of each column in E211's planning form (26.0 W + 1.10 x W over idle + 1 W), REPORTED only: v2 53.2 W (s01), v2-C1 59.0 W (s03), v2-C2 64.5 W (s03).

**Labels and limits.** Every constant of MM1-v2 is a desk fit made after its own data existed (post hoc as an act). E206 arm A's twins (2x8x4, 3x5x7 fp32 and int8, 3x6x6: w04m, w06m, w10m, w07m) are in v2's fit, as in MM1-v1's; E207's twins (2x3x2, 3x3x4 and 6x6x6 fp32: w01m, w02m, w09m, and c01c's twin w01m) ran in E207 on this card before this freeze (E207's first data commit 867f6a3f3e2b, 07:58:54 PST Tue 17 Nov): the forecasts there were made without reading that datum but were not frozen before it, and MM1-v2's constants never read E207; v2 was refitted with E208 (rgm136 on aifoundry2 card 0 and aifoundry1 cards 0 and 1; no aifoundry3 point). Neither the predictor nor this wrapper reads E206 arm B's or E207's data. rgm211 has never run on any card (E211.md section 4); the map is a desk model of the kernels' addresses (one fully associative LRU over 1 KB tiles under the logistic retention), tied by E211 to E206's registered lines on rgm136's walk; rgm211's map is checked only by construction and by the exact controls (x01, x02: the two walks give the same map, so every v2 ratio there is 1). v2 has no term for the load mode: v2-C1 is E211's registered carriage of E101's measured cooperation, not a v2 term. The timing simulation's two columns are v2's own (rgm136's cooperative gemmL step law and the measured floor): at the gemmLn and gemmLnc points they are not a count of the loop that runs (each record says so; REPORTED, never scored). The switch counts are estimates (README section 7), never scorable. Scope: rgm136's GEMM on its grid; rgm211 is a second kernel outside v2's fit by construction (E211's question).

**Scanner safety.** These files hold no host record or command line that E206's never-run scanner counts as a run (the JSON has no `type` key and no host argument list; E206's scanner, unchanged, over the four files above, before this note was written: 4 files read, 0 records found). This note and `SHA256SUMS-e211` hold none either (no `"arm"` key, no `--type` or `--values` argument): E211's never-run search (its step 6n, which reads `tools/matmul/` at HEAD) finds nothing new here.

Q206, lane mm1v2-e211. SPDX-License-Identifier: Apache-2.0
