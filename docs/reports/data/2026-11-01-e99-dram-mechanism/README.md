# E99 — which mechanism carries the DRAM pattern effect (Q132)

*On the kinds page, [section 11, what is still open](https://spacesheep.dev/@yaroslavvb/horace-kinds-of-numbers#11-what-is-still-open): "The memory path" (part of old item 12).*

*Corrected after verification, Sun 1 Nov 2026, at the desk, with no card touched and nothing re-run (§ [Corrections after verification](#corrections-after-verification-sun-1-nov-2026), C1–C10). A verifier rebuilt every number from the raw telemetry and found them right, and found two readings that were not: where a one pays, and what the period ladder says. New, post hoc and labelled: the NoC and SRAM rails, which the registered reducer did not read (`tools/claims-v3/dm/posthoc_rails.py`, `posthoc-rails.txt`). No number in `dm*.json`, `runs.csv` or `dips.json`, no scored verdict and no registered file changed.*

## Results

*Six passes, `p9910`–`p9915`, Sun 1 Nov 2026 01:08:07–01:34:37 PDT on aifoundry3 card 0, 600 MHz, `--harts 1` (1,024 harts), 29 DRAM items and the
drift anchor per pass, after a smoke (`p9901`, 01:06:17). **26.7 card-minutes** of the registered 33. Every pass `block.json` `"status":"ok"`, 186
runs, **no run-gate failure**, no pass set aside (drift 0.07–0.17 W). Pre-registered in `590f9b7e` (01:03:40 PDT), before the claim (01:05:58) and the first
launch. Reduced with `reduce.sh` (the registered `tools/claims-v3/dm/reduce_dm.py`, unchanged). Pass 9910 is the registered warm-up, so **the headline is five
passes, 9911–9915** (df = 4). Every number below is from `dm.json` `headline` (the registered primary arm: the board meter's dips removed) unless it says otherwise.
Intervals are 95 % t over the five headline passes at the registered `auto` leakage slope (0.0046 W/°C); the two registered sensitivities are in
§ [The leakage footing and the unfiltered arm](#the-leakage-footing-and-the-unfiltered-arm).*

**The registered overall reading is PARTIAL: R7, R11 and R12 FAIL, R2 and R4 are UNRESOLVED, and R1, R3, R5, R8 and R13 PASS.** On this card read data-bus inversion behaves as live, and pins driven high do pay: about a quarter (13–33 %) of E81's 1.636 W.
About half of a one's price is on the NoC rail. High pins, pin toggles and `half` are on no metered rail. The 1 W floor is gone; about 0.1 W remains, on the SRAM rail. On board power the channel count alone does not set the period ladder.

> | what | isolated by | W [95 %] | price | at 0.2936 / 0.3803 W/°C |
> |---|---|---:|---:|---:|
> | **a one bit**, with the pins held equal | `tie27`: 448 ones against 128, 128 high pins each, no toggle | +1.195 [1.048, 1.342] | **3.18** [2.79, 3.58] pJ per one | 2.97 / 2.90 |
> | | `tie18`: 512 against 64, 64 high pins each | +1.727 [1.620, 1.833] | **3.29** [3.08, 3.49] | 3.07 / 3.00 |
> | | `tie45`: 320 against 256, 256 high pins each: the rule's tie | +0.262 [0.191, 0.332] | **3.48** [2.55, 4.42] | 3.48 / 3.48 |
> | **a pin driven high**, per beat | `hi_t0`: the same 256 ones, no toggle, 256 high pins against 32 | +0.386 [0.293, 0.479] | **1.47** [1.12, 1.82] pJ | 1.58 / 1.61 |
> | | `hi_ta`: the same ones, raw and encoded toggles, 224 against 32 | +0.418 [0.258, 0.578] | **1.86** [1.15, 2.57] | 1.69 / 1.64 |
> | | `tent_S`: free of any linear price of ones | +0.513 [0.312, 0.715] | **1.71** [1.04, 2.38] | 1.63 / 1.61 |
> | **a pin toggle** after inversion | `t_both`: 0x0F/0xF0 beats against constant 0x0F, the same 256 high pins | +0.475 [0.396, 0.554] | **0.82** [0.68, 0.95] pJ | 0.87 / 0.88 |
> | **a raw toggle that inversion hides** | `t_raw`: 0x00/0xFF beats against constant lanes: raw +496, only the DMI pin moves | −0.026 [−0.199, +0.148] | **none** (absent) | absent at both |
> | **a bit that differs between a line's 32 B halves** | `half`: `dp_c1` against `dm_l08`, the same ones and high pins, not the same everything (below) | +0.850 [0.785, 0.915] | at most **2.83** [2.61, 3.05] pJ | 3.08 / 3.16 |
> | **one bit in every line**, over an all-zero line | `floor_w1` | +0.112 [0.040, 0.184] | absent by the rule's ±0.30 W: **the 1 W floor is gone**; about 0.1 W remains, on the SRAM rail | unresolved (+0.21, +0.24) |

Each of those holds its other counts equal by construction (`gen/counts.json`, `tools/claims-v3/dm/make_dm.py --check`), except `half`: `dp_c1` against `dm_l08` also moves `r32` +32, `r64` +64, `r128` +128, `t_raw` +16 and `t_enc` +2, and `dp_c1` has all its ones in the first 32 B. So 2.83 pJ is an upper bound; the post-hoc fit below gives 2.53. The rails clear the registered risk that the first half goes further: `half` reads NoC +0.020, SRAM +0.006, minion +0.019 W. Five readings:

1. **Read DBI behaves as live on this card.** Nothing was read from the card's memory controller, so this is what the card does. The same +496 raw toggles per line cost nothing measurable when the bytes
   alternate 0x00/0xFF (`t_raw`, −0.026 W [−0.199, +0.148]), which inversion turns into one moving DMI pin, and +0.475 W when they alternate 0x0F/0xF0 (`t_both`), which it cannot hide: **+0.501 W** [0.327, 0.675] between the two
   (+0.466 and +0.456 W at the sensitivities, each interval above 0; per-pass differences of `dm.json` `per_pass`). At the same ones and the same raw toggles, the watts climb with the high pins: 1.129, 1.435, 1.547 W
   at 32, 160, 224 high (`dm_a08`, `dm_a26`, `dm_a35`). Whole bytes of ones in random places cost what runs cost, +0.093 W [−0.059, +0.244] over `dp_c2`, while the same raw toggles from scattered bits cost +0.806 W more
   (`L2_vs_r08`). And the tent has its kink: on constant bytes the step is 4.82 pJ per added one below p = 4, 3.48 across the tie, 1.40 above p = 5 (table below). The mean of the outer two, 3.11, is about the ties' price of a one, and half their difference, 1.71 pJ, is the pin's. The exact claim is about a 16-bit encoded stage: in all four beat images every piece of 32 bits or wider is constant, so no wider path can tell `t_raw` from `t_both`. The pins, the DRAM's output serializer and the PHY's receive stage all fit, and it is on no metered rail (`t_both`: NoC −0.015, SRAM 0.000, minion +0.010 W).
2. **High pins carry about a quarter of it (13–33 %).** Of E81's 1.636 W (+1.666 W here), the 177 high pins that random bits add come to 0.31–0.39 W at the three prices' point estimates, and 0.22–0.53 W, 13–33 %, across their 95 % intervals (1.04–2.57 pJ). On the arrangement alone (`arr_L2`, +0.899 W), the direct prices give +0.390 W for its 179 high pins, +0.233 W for its 253 encoded toggles and −0.035 W for its 208 raw toggles: 0.588 W, 0.311 W short, and **R12 fails**, just outside its ±0.30 W band (by more at the two sensitivities, 0.42 and 0.45 W). That FAIL by 0.011 W rests on a raw price of −0.14 pJ [−0.42, +0.14] that is itself consistent with zero: with raw at zero the parts are 0.622 W, 69 % of the arrangement, and the miss is 0.276 W, inside the band. R12 stays FAIL as frozen. The rest needs a path this design did not isolate (post-hoc account, below). All of it is off every metered rail (`arr_L2`: NoC −0.018, SRAM −0.025, minion +0.046 W).
3. **The largest price is a raw one. It is not on the pins, and about half of it is on the NoC rail.** All-0xFF bytes hold every data pin low and still cost +2.174 W over zeros (`ones_u8`). Three independent pairs at equal high pins give 3.18, 3.29 and 3.48 pJ per one, and **E75's 3.255 pJ** [2.97, 3.55], from contiguous images, sits among them. So E75's price was right and it is not a pin's. Post hoc, the rails say where it goes (table below): fitted over the no-toggle images a one costs 3.24 ± 0.25 pJ at the board, **1.60 ± 0.08 pJ on the NoC rail**, 0.16 ± 0.08 on the SRAM rail, 0.17 ± 0.06 on the minion rail, and about 1.3 pJ off every metered rail. That 1.3 pJ is what stays open.
4. **On board power the channel count alone does not set the period ladder.** R11 fails in the primary arm because period 16 costs (`h16` +0.304 W; +0.22 to +0.24 W and never absent in the other three arms, where R11 is UNRESOLVED). Period 8 reads +0.115 W [−0.040, +0.271], inside the rule's absent band, and +0.100 [0.051, 0.148] on the SRAM rail, so it is not free. The reducer's registered named reading, "a path of the 8-way interleave pays", is **one candidate, not a finding**: the rails split the ladder (table below). SRAM and NoC carry 58 % of `D` and 59 % of `h16`, with their steps in different places, and off every metered rail an 8-way and a 16-way count fit alike (0.037 against 0.042 W rms). A public example of such a path is each memory shire's 512-bit AXI port (datasheet §7.1.1.1), but the memory shires' logic sits on a rail nothing meters (E30), and off the metered rails L16 − L8 is +0.084 W [−0.129, +0.297].
5. **The 1 W floor is gone; about 0.1 W remains, on the SRAM rail.** All six models frozen before the data needed +0.99 to +1.72 W for any non-zero line, and `floor_w1` reads +0.112 W [0.040, 0.184]: absent by the rule's ±0.30 W, yet above zero, and about 19 times what one bit and one high pin cost at the measured prices (0.006 W). Fitted over the no-toggle images the floor is +0.102 W [0.036, 0.168] on the board and +0.097 [0.065, 0.129] on the SRAM rail, with the NoC and minion floors consistent with zero. On the board only the primary arm's interval excludes zero (+0.145 [−0.108, +0.397] and +0.158 [−0.189, +0.504] at the sensitivities, +0.050 [−0.074, +0.174] unfiltered). What the fits called a floor looks like toggling on wide paths (post hoc, below), which every E75 and E81 image had: `dm_l08` carries the same 256 ones and 32 high pins as E75's images, with every 16-bit word alike, and costs +1.155 W against their +1.77–2.35 W (`posthoc-fit.txt`).

### The tent, and the ladder

| constant byte | p | ones | high pins | W over zeros [95 %] | step, pJ per added one (at 0.3803 W/°C) |
|---|---:|---:|---:|---:|---:|
| `dm_w1` (one bit, not a constant byte) | | 1 | 1 | 0.112 [0.040, 0.184] | |
| `dm_u1` 0x01 | 1 | 64 | 64 | 0.447 [0.385, 0.509] | 5.96 [5.12, 6.79] over zeros (5.96) |
| `dm_u2` 0x03 | 2 | 128 | 128 | 0.818 [0.763, 0.873] | 4.94 [4.60, 5.28] (4.34) |
| `dm_u4` 0x0F | 4 | 256 | 256 | 1.541 [1.430, 1.652] | **4.82** [4.28, 5.35] (4.37) |
| `dm_u5` 0x1F | 5 | 320 | **256** | 1.803 [1.732, 1.874] | **3.48** [2.55, 4.42] (3.48) |
| `dm_u7` 0x7F | 7 | 448 | 128 | 2.013 [1.889, 2.137] | **1.40** [0.46, 2.34] (1.15) |
| `dm_u8` 0xFF | 8 | 512 | 64 | 2.174 [2.093, 2.254] | 2.14 [1.23, 3.05] (2.14) |

| period (lines) | values a 16-way channel sees | an 8-way path | W over `dm_L2` [95 %] | class | share of the top step | registered channel reading |
|---|---:|---:|---:|---|---:|---|
| 1 | 1 | 1 | −0.041 [−0.105, +0.024] (`h1` read the other way) | absent | | |
| 3 | 3 | 3 | **+0.495** [0.456, 0.535] | present | 66 % | 67 % |
| 4 | 1 | 1 | +0.152 [0.110, 0.193] | absent | 20 % | 0 |
| 8 | 1 | 1 | +0.115 [−0.040, +0.271] | absent | 15 % | 0 |
| **16** | **1** | **2** | **+0.304** [0.188, 0.421] | **present** | **40 %** | **0** (R11 FAIL in this arm) |
| 17 | 17 | 17 | +0.628 [0.585, 0.671] | present | 83 % | 94 % |
| 32 | 2 | 4 | +0.465 [0.419, 0.511] | present | 62 % | 50 % |
| 256 | 16 | 32 | +0.602 [0.550, 0.654] | present | 80 % | 94 % |
| 8,192 (`D`) | 512 | 1,024 | +0.755 [0.670, 0.840] | present | 100 % | 100 % (E81: +0.640) |

*`h4`'s interval excludes 0 at this slope; it reads +0.033 and −0.002 W at the sensitivities. `dp_bern` − `dm_L8192` = +0.012 W [−0.090, +0.114]: E81's random bits and these lines of one byte distribution cost the same, so the ±11-bit spread E81's note ¹ worried about moves nothing.
A line's change in one hart's stream costs little: `h1` is absent on the board, as E75's k-arm said, though the SRAM rail reads `dp_c2` − `dp_c1` +0.083 W [0.054, 0.111].*

### Where it is paid: the metered rails (POST HOC, labelled: `tools/claims-v3/dm/posthoc_rails.py`, `posthoc-rails.txt`, `posthoc-rails.json`)

*Not registered and not scored. The registered reducer reads only the minion rail; this was written after the data, when a verifier pointed out that the telemetry records the NoC and SRAM rails too. It reads `sp.noc_w`, `sp.sram_w` and `sp.minion_w` exactly as the reducer reads the minion rail: window [t0+2 s, t0+4 s), the primary arm's telemetry, raw, within-pass differences, 95 % t, n = 5; its minion column reproduces `dm.json` `per_pass.rail_W` in all 145 item-passes. A rail is the PMIC's running average at the regulator's output (E58, E30), so such a window reads about 93.5 % of a settled step and these rail prices are about 7 % low: the NoC rail's 1.60 pJ would be 1.71. The board is the 12 V input, so "off", the board less the three rails, holds those regulators' own loss as well as what no rail meters: the DDR and I/O rails, the memory shires' logic, the DRAM chips (`docs/findings/14-card-behaviour.md`, E30). Each class below is sized for the board, so on one rail read the interval.*

| | board | NoC rail | SRAM rail | minion rail | off every metered rail |
|---|---:|---:|---:|---:|---:|
| `tie18`: 448 more ones, the same high pins, W | +1.727 [1.620, 1.833] | +0.828 [0.790, 0.865] | +0.079 [0.059, 0.099] | +0.103 [0.084, 0.123] | +0.716 [0.590, 0.842] |
| `tie27`: 320 more ones, the same high pins, W | +1.195 [1.048, 1.342] | +0.601 [0.543, 0.659] | +0.051 [−0.006, +0.109] | +0.058 [−0.010, +0.126] | +0.486 [0.350, 0.621] |
| **a one**, fitted over the eight no-toggle images, pJ | 3.24 ± 0.25 | **1.60 ± 0.08** | 0.16 ± 0.08 | 0.17 ± 0.06 | 1.32 ± 0.25 |
| **a high pin**, the same fit, pJ | 1.55 ± 0.30 | 0.04 ± 0.15 | −0.01 ± 0.12 | −0.01 ± 0.18 | **1.54 ± 0.40** |
| **the floor**, the same fit, W | +0.102 [0.036, 0.168] | +0.021 [−0.008, +0.049] | **+0.097** [0.065, 0.129] | +0.005 [−0.040, +0.049] | −0.021 [−0.080, +0.038] |
| `hi_t0`, W | +0.386 [0.293, 0.479] | +0.010 [−0.027, +0.047] | +0.002 [−0.025, +0.029] | −0.012 [−0.056, +0.032] | +0.386 [0.292, 0.480] |
| `hi_ta`, W | +0.418 [0.258, 0.578] | −0.003 [−0.041, +0.035] | +0.002 [−0.038, +0.042] | +0.003 [−0.083, +0.089] | +0.415 [0.267, 0.564] |
| `t_both`, W | +0.475 [0.396, 0.554] | −0.015 [−0.039, +0.009] | +0.000 [−0.022, +0.022] | +0.010 [−0.029, +0.050] | +0.479 [0.394, 0.565] |
| `half`, W | +0.850 [0.785, 0.915] | +0.020 [−0.023, +0.063] | +0.006 [−0.016, +0.028] | +0.019 [−0.036, +0.075] | +0.805 [0.727, 0.882] |
| `arr_L2`, W | +0.899 [0.815, 0.982] | −0.018 [−0.075, +0.039] | −0.025 [−0.069, +0.018] | +0.046 [−0.059, +0.151] | +0.896 [0.782, 1.010] |
| E81's whole step, `tie_total`, W | +1.666 [1.593, 1.739] | +0.133 [0.087, 0.180] | +0.273 [0.233, 0.314] | +0.040 [0.002, 0.078] | +1.220 [1.099, 1.340] |

*The fit: floor + one + high over `dm_w1`, `dm_u1`, `dm_u2`, `dm_u4`, `dm_u5`, `dm_u7`, `dm_u8`, `dm_l08`, per pass (`posthoc-rails.txt`).*

So **about half of a one's price is on the NoC rail, about 0.3 pJ on the SRAM and minion rails, and about 1.3 pJ off every metered rail; high pins, pin toggles and `half` are on no metered rail.** NoC over zeros follows the ones alone: +0.493 to +0.518 W on `dm_l08`, `dm_a08`, `dm_a44`, `dp_c1` (all 256 ones, high pins 32 to 256), and +0.988 W on `dm_u8`. The lab has measured this before: E32's 129 [127–133] fJ per one per hop on the mesh rail (`docs/findings/03-experiments.md:946`, `05-claims.md:381`), which 1.60 pJ would make 12.4 hop-equivalents; no hop count was measured here. At E32's ratio of board to rail, 192/129, 2.4 of the 3.24 pJ would go with the mesh. That is arithmetic, not a measurement, and it says how much of the open 1.3 pJ may be delivery and the memory shires' logic rather than anything further out.

| over `dm_L2`, W [95 %] | board | NoC rail | SRAM rail | minion rail | off every metered rail |
|---|---:|---:|---:|---:|---:|
| period 3 | +0.495 [0.456, 0.535] | +0.094 [0.010, 0.177] | +0.187 [0.111, 0.263] | −0.025 [−0.165, +0.114] | +0.240 [0.191, 0.289] |
| period 4 | +0.152 [0.110, 0.193] | −0.007 [−0.053, +0.038] | +0.043 [0.009, 0.077] | +0.004 [−0.097, +0.104] | +0.112 [0.043, 0.182] |
| period 8 | +0.115 [−0.040, +0.271] | +0.033 [−0.040, +0.107] | +0.100 [0.051, 0.148] | −0.047 [−0.176, +0.082] | +0.029 [−0.156, +0.214] |
| period 16 | +0.304 [0.188, 0.421] | +0.067 [0.001, 0.134] | +0.113 [0.051, 0.175] | +0.011 [−0.148, +0.170] | +0.113 [−0.036, +0.263] |
| period 17 | +0.628 [0.585, 0.671] | +0.128 [0.059, 0.196] | +0.231 [0.184, 0.277] | −0.019 [−0.140, +0.103] | +0.288 [0.222, 0.353] |
| period 32 | +0.465 [0.419, 0.511] | +0.063 [−0.004, +0.130] | +0.124 [0.063, 0.184] | +0.003 [−0.126, +0.132] | +0.275 [0.219, 0.332] |
| period 256 | +0.602 [0.550, 0.654] | +0.134 [0.087, 0.181] | +0.228 [0.194, 0.262] | −0.044 [−0.175, +0.088] | +0.283 [0.202, 0.365] |
| 8,192 lines, `D` | +0.755 [0.670, 0.840] | +0.138 [0.058, 0.218] | +0.297 [0.239, 0.355] | +0.008 [−0.152, +0.167] | +0.312 [0.201, 0.424] |
| step, L8 − L4 | −0.037 [−0.183, +0.110] | +0.041 [0.006, 0.076] | +0.056 [0.029, 0.083] | −0.051 [−0.090, −0.011] | −0.083 [−0.228, +0.061] |
| step, L16 − L8 | +0.189 [0.016, 0.362] | +0.034 [0.002, 0.066] | +0.013 [−0.019, +0.045] | +0.058 [−0.011, +0.127] | +0.084 [−0.129, +0.297] |
| step, L16 − L4 | +0.153 [0.051, 0.254] | +0.075 [0.035, 0.115] | +0.069 [0.025, 0.114] | +0.008 [−0.089, +0.104] | +0.001 [−0.112, +0.113] |

SRAM and NoC carry 58 % of `D`, 59 % of `h16` and 24 % of E81's whole step. Each column has its own shape. SRAM's step sits between 4 and 8, not between 8 and 16. NoC's L16 − L8 is small and above zero. On the board L16 − L8 is +0.189 W [0.016, 0.362] (+0.198 and +0.200 at the sensitivities, each interval above zero; unfiltered +0.293 [−0.074, +0.660]). Off every metered rail `h4`, `h8` and `h16` are absent by the registered class, and `h17`, `h32`, `h256` and `D` are present. R11 would not pass there as written either: `h3`, +0.240 W [0.191, 0.289], is in the absent band and `h32` is 88 % of `D`, because the rule's absolute thresholds were sized for the board. So this does not rescue the channel reading. It shows that the board's ladder does not decide between the 8-way and the 16-way count.

### Scoring

| rule | reading | registered | verdict |
|---|---|---|---|
| **R1** session tie | `tie_total` +1.666, `tie_c2` +1.800, `tie_bern` +3.466, `tie_c1` +2.005 W | E81's 1.636, 1.866, 3.501 (±0.35), 2.046 (±0.40) | **PASS**, all four |
| **R2** high pins, same ones, no toggles (`hi_t0`) | +0.386 [0.293, 0.479], present | present and in [0.46, 1.84] | **UNRESOLVED**: present at about half the frozen model's +0.92 W |
| **R3** high pins, equal toggles (`hi_ta`) | +0.418 [0.258, 0.578], present | present and in [0.39, 1.58] | **PASS** (UNRESOLVED at both sensitivities: 0.380, 0.369 W) |
| **R4** the tent (`tent_S`) | +0.513 [0.312, 0.715], present | present and in [0.53, 2.10] | **UNRESOLVED**: present, 0.017 W under the band |
| **R5** whole bytes in random places | `r08_vs_c2` absent, `L2_vs_r08` +0.806 present | both | **PASS** (UNRESOLVED in the unfiltered arm) |
| **R6** same high pins, different ones | `tie27`, `tie18` present | both absent, or both present | **ones cost beyond the pins**, 3.18–3.48 pJ. The pure DBI model is refuted |
| **R7** encoded toggles (`t_enc`) | +0.469 [0.416, 0.523], present | absent | **FAIL**: encoded toggles pay, about 0.8 pJ each |
| **R8** raw toggles (`t_raw`) | −0.026 [−0.199, +0.148], absent | absent | **PASS** |
| **R9** the 32 B halves (`half`) | +0.850 [0.785, 0.915] | reported | **present** (E81's post-hoc term said +0.72 W; `w_hi_chan` said 0) |
| **R10** the floor (`floor_w1`) | +0.112 [0.040, 0.184] | reported | **absent** by the ±0.30 W rule (unresolved at the sensitivities: +0.207, +0.236). Its interval excludes zero: about 0.1 W remains, on the SRAM rail |
| **R11** the channel | `h16` present | `h4 h8 h16` absent, `h3 h17` present, `h32` 15–85 % of `D` | **FAIL** (UNRESOLVED at both sensitivities and in the unfiltered arm: `h16` +0.244, +0.225, +0.242, never absent). Its named reading, an 8-way path, is one candidate (reading 4) |
| **R12** closure | predicted `arr_L2` +0.588 (+0.390 high, +0.233 encoded, −0.035 raw), measured +0.899 W | within ±0.30 W | **FAIL**, by 0.011 W (0.42, 0.45 W short at the sensitivities) |
| **R13** the minion rail, which the registration calls the compute rail | `hi_t0` −0.012, `hi_ta` +0.003, `D` +0.008, `tie_total` +0.040 W | each within ±0.10 W | **PASS**, all four. It scores the minion rail only: the NoC and SRAM rails are 24 % of `tie_total` and 58 % of `D` |

**The registered overall reading is PARTIAL:** R3 and R5 pass, R2 and R4 are unresolved because the high-pin effect is present at about half the frozen amount, and it is not REFUTED. It reads PARTIAL at all three slopes and in the unfiltered arm. What the rule does not say is that the DBI *signature* is plain and the DBI *share* is about a quarter: both come from the same numbers.

**The frozen models.** Every model frozen before the data over-predicts this experiment's structured images, mostly by its floor. On the 28 items they err by 0.55–2.33 W rms (`w_tenc_chan` 0.553, `w_hi_chan` 0.705, `bits` 0.848, `w_traw_chan` 0.877, `dbi` 1.103, `dbi_chan` 2.332). Against every registered contrast (`corrections-check.txt` C10), `w_traw_chan` falls outside its interval on eight (`t_raw`, predicted +1.69 W; `t_both`, `hi_r`, `hi_r26`, `r08_vs_c2`, `L2_vs_r08`, `half`, `floor_w1`), `w_tenc_chan` on five (`t_enc`, predicted +1.29 W; `t_both`, `ones_u8`, `half`, `floor_w1`), the pure `dbi` on three (`tie27`, `tie18`, `floor_w1`) and `dbi_chan` on 16. `bits` falls outside on none, because its ±1.7 W intervals can hardly fail. `w_hi_chan` holds every pin contrast and fails on three: `ones_u8` (+2.17 against +2.92 ± 0.67), `half` and `floor_w1`. So the shape with ones, high pins and path changes was right, with a floor where wide-path toggles belong.

### The leakage footing and the unfiltered arm

| contrast | `auto`, dips removed: the registered primary | 0.2936 W/°C | 0.3803 W/°C | unfiltered, `auto` |
|---|---:|---:|---:|---:|
| `tie_total` | +1.666 [+1.593, +1.739] | +1.666 [+1.593, +1.739] | +1.666 [+1.593, +1.739] | +1.528 [+1.150, +1.905] |
| `hi_t0` | +0.386 [+0.293, +0.479] | +0.415 [+0.374, +0.457] | +0.424 [+0.378, +0.470] | +0.386 [+0.293, +0.479] |
| `hi_ta` | +0.418 [+0.258, +0.578] | +0.380 [+0.187, +0.574] | +0.369 [+0.134, +0.604] | +0.418 [+0.258, +0.578] |
| `hi_r` | +0.910 [+0.774, +1.045] | +0.953 [+0.822, +1.084] | +0.966 [+0.816, +1.116] | +0.948 [+0.713, +1.183] |
| `tent_S` | +0.513 [+0.312, +0.715] | +0.490 [+0.176, +0.804] | +0.483 [+0.107, +0.859] | +0.513 [+0.312, +0.715] |
| `t_enc` | +0.469 [+0.416, +0.523] | +0.501 [+0.350, +0.651] | +0.510 [+0.303, +0.718] | +0.469 [+0.416, +0.523] |
| `t_raw` | -0.026 [-0.199, +0.148] absent | +0.038 [-0.141, +0.217] absent | +0.057 [-0.149, +0.263] absent | -0.026 [-0.199, +0.148] absent |
| `t_both` | +0.475 [+0.396, +0.554] | +0.504 [+0.356, +0.652] | +0.513 [+0.308, +0.717] | +0.475 [+0.396, +0.554] |
| `tie27` | +1.195 [+1.048, +1.342] | +1.114 [+0.988, +1.241] | +1.090 [+0.939, +1.240] | +1.195 [+1.048, +1.342] |
| `tie45` | +0.262 [+0.191, +0.332] | +0.262 [+0.191, +0.332] | +0.262 [+0.191, +0.332] | +0.262 [+0.191, +0.332] |
| `tie18` | +1.727 [+1.620, +1.833] | +1.611 [+1.463, +1.759] | +1.576 [+1.392, +1.761] | +1.627 [+1.320, +1.934] |
| `ones_u8` | +2.174 [+2.093, +2.254] | +2.058 [+1.835, +2.282] | +2.023 [+1.744, +2.303] | +2.074 [+1.770, +2.378] |
| `half` | +0.850 [+0.785, +0.915] | +0.925 [+0.790, +1.060] | +0.948 [+0.771, +1.125] | +0.850 [+0.785, +0.915] |
| `floor_w1` | +0.112 [+0.040, +0.184] absent | +0.207 [-0.036, +0.450] unres. | +0.236 [-0.101, +0.572] unres. | -0.002 [-0.263, +0.259] absent |
| `arr_L2` | +0.899 [+0.815, +0.982] | +1.017 [+0.864, +1.170] | +1.053 [+0.845, +1.260] | +0.899 [+0.815, +0.982] |
| `r08_vs_c2` | +0.093 [-0.059, +0.244] absent | +0.107 [-0.062, +0.277] absent | +0.112 [-0.065, +0.288] absent | +0.055 [-0.197, +0.307] unres. |
| `L2_vs_r08` | +0.806 [+0.652, +0.959] | +0.910 [+0.736, +1.083] | +0.941 [+0.718, +1.164] | +0.844 [+0.587, +1.101] |
| `h1` | +0.041 [-0.024, +0.105] absent | +0.159 [+0.011, +0.308] unres. | +0.195 [-0.010, +0.400] unres. | +0.041 [-0.024, +0.105] absent |
| `h3` | +0.495 [+0.456, +0.535] | +0.377 [+0.207, +0.547] | +0.341 [+0.114, +0.569] | +0.367 [-0.014, +0.749] unres. |
| `h4` | +0.152 [+0.110, +0.193] absent | +0.033 [-0.141, +0.207] absent | -0.002 [-0.233, +0.229] absent | -0.025 [-0.537, +0.486] unres. |
| `h8` | +0.115 [-0.040, +0.271] absent | +0.046 [-0.101, +0.193] absent | +0.025 [-0.151, +0.202] absent | -0.051 [-0.500, +0.399] unres. |
| `h16` | +0.304 [+0.188, +0.421] | +0.244 [+0.059, +0.428] unres. | +0.225 [-0.049, +0.500] unres. | +0.242 [+0.110, +0.375] unres. |
| `h17` | +0.628 [+0.585, +0.671] | +0.509 [+0.333, +0.685] | +0.474 [+0.240, +0.707] | +0.508 [+0.209, +0.806] |
| `h32` | +0.465 [+0.419, +0.511] | +0.346 [+0.191, +0.502] | +0.311 [+0.098, +0.524] | +0.465 [+0.419, +0.511] |
| `h256` | +0.602 [+0.550, +0.654] | +0.516 [+0.355, +0.676] | +0.490 [+0.279, +0.701] | +0.429 [-0.037, +0.896] unres. |
| `D` | +0.755 [+0.670, +0.840] | +0.642 [+0.489, +0.796] | +0.609 [+0.398, +0.819] | +0.672 [+0.437, +0.907] |
| `bern_vs_L8192` | +0.012 [-0.090, +0.114] absent | +0.007 [-0.082, +0.095] absent | +0.005 [-0.080, +0.090] absent | -0.043 [-0.445, +0.360] unres. |

| rule | primary | 0.2936 W/°C | 0.3803 W/°C | unfiltered |
|---|---|---|---|---|
| R2 | UNRESOLVED | UNRESOLVED | UNRESOLVED | UNRESOLVED |
| R3 | PASS | UNRESOLVED | UNRESOLVED | PASS |
| R4 | UNRESOLVED | UNRESOLVED | UNRESOLVED | UNRESOLVED |
| R5 | PASS | PASS | PASS | UNRESOLVED |
| R6 | ones pay | ones pay | ones pay | ones pay |
| R7 | FAIL | FAIL | FAIL | FAIL |
| R8 | PASS | PASS | PASS | PASS |
| R9 | present | present | present | present |
| R10 | absent | unresolved | unresolved | absent |
| R11 | FAIL | UNRESOLVED | UNRESOLVED | UNRESOLVED |
| R12 | FAIL | FAIL | FAIL | FAIL |
| overall | PARTIAL | PARTIAL | PARTIAL | PARTIAL |

*From `dm.json`, `dm-leak0.2936.json`, `dm-leak0.3803.json`, `dm-unfiltered.json`, `headline.contrasts_W`.*

The windows warm at most 1.0 °C over their launch reading (`runs.csv`), and E81's `auto` estimator, 0.0046 W/°C here, barely corrects. At 0.3803 W/°C, the slope E71 measured on this card's idle, the prices of a high pin from the three contrasts draw together, 1.61, 1.64 and 1.61 pJ. Verdicts that move: R3 goes UNRESOLVED at both sensitivities (0.380, 0.369 W, under its 0.39 W band), R10 goes unresolved (its interval widens), and R11 goes UNRESOLVED because `h16`'s mean falls under 0.25 W. In the unfiltered arm R5 and R11 go UNRESOLVED. No verdict flips between PASS and FAIL. Dips: 112 samples in six passes, 21 inside a run's window (`dips.json`), which is why the filter was registered: without it the ladder's intervals are up to 12 times wider.

### What it costs per event (POST HOC, labelled: `tools/claims-v3/dm/posthoc_fit.py`, `posthoc-fit.txt`, `posthoc-fit.json`)

*Chosen after the registered reduction was read, from 28 candidate fits (14 extras, each with and without a floor, all printed). Seven prices on 28 items describe those items; they are not seven measurements. The registered contrasts above are the measurement. Its check is E75's and E81's 18 points, with a limit: five are byte-identical to fitted items (`dp_c1`, `dp_c2`, `dp_bern`, E75's k0 and k256), and the terms `half`, `k_chan` and `hi` came from earlier fits on those points. The clean part is the 13 points whose images it never fitted (12 images: `dp_random` and `mf_random` are one). It was not chosen by that column: `half` + `r128` is lower there, 0.130 W. `posthoc-fit.txt` prints "18 points it never saw"; that line stands as printed, and this corrects it.*

Fitted on E99 alone, per pass, **with no floor**, to **0.063 W rms**, and predicting E75's and E81's 18 points to 0.143 W rms: **0.160 W on the 13 whose images it never fitted**, 0.086 W on the five it did:

| count, per 64 B line | price, pJ [±95 %] | a reading, not measured |
|---|---:|---|
| `w` ones | **3.30** [±0.10] | off the pins: about half on the NoC rail, about 0.3 pJ on the SRAM and minion rails, about 1.3 pJ off every metered rail |
| `hi` pins driven high | **1.97** [±0.31] | on no metered rail. DC through the terminated pins fits: with the telemetry's `reg_mv.vddqlp`, 640 mV, half of it across a 40 Ω driver is 1.37 pJ a beat at the pad |
| `t_enc` toggles on the pins | **0.88** [±0.17] | on no metered rail: the pins' capacitance, or any encoded 16-bit stage |
| `half` bits differing between the 32 B halves | **2.53** [±0.21] | on no metered rail: a 256-bit path, one BL16 burst per word |
| `r64` raw toggles between consecutive 64-bit pieces | **2.22** [±0.13] | on no metered rail: a 64-bit path, four beats, one clock of the 933 MHz controller (`DfiFreqRatio_p0 = 1`, `memshire_ddr_init_functions.c:768`) |
| `k_shire` bits changed between reads of an 8-way path | **1.85** [±0.46] | one candidate; the rails split it (above) |
| `k_chan` the same for a 16-way path | **0.45** [±0.49] | not separated from zero here; off every metered rail it fits the ladder about as well as `k_shire` |

What it makes of the earlier steps, in watts:

| step | measured | account | ones | high pins | pin toggles | `half` + `r64` | path changes |
|---|---:|---:|---:|---:|---:|---:|---:|
| E81's arrangement | +0.996 | +0.897 | 0 | +0.426 | +0.258 | +0.214 | 0 |
| E81's period | +0.640 | +0.634 | 0 | −0.016 | +0.004 | −0.047 | +0.691 |
| E81's whole step | +1.636 | +1.531 | 0 | +0.410 | +0.263 | +0.167 | +0.691 |
| zeros to random floats (E75's 3.25 W chord) | +3.222 | +3.086 | **+1.115** (35 %) | +0.475 (15 %) | +0.265 (8 %) | +0.717 (22 %) | +0.514 (16 %) |

So **the 36.6 % E75's two prices explained is the ones (35 % here), and the 63 % they missed is the pins (23 %), raw toggles on wide paths (22 %) and path changes (16 %)**, with 4 % unaccounted. Of E81's 1.636 W, the high pins are 25 %, pin toggles 16 %, the wide raw path 10 % and path changes 42 %. On the ladder alone, on the board, an 8-way count fits the ten rungs better than a 16-way one (0.065 against 0.093 W rms), and with both, 1.54 pJ [±0.58] against 0.55 pJ [±0.61]; off every metered rail the two fit alike (0.037, 0.042 W). The ladder is not balanced in the account's own counts: `r64` spans 218.8 to 235 across the rungs, about 0.04 W at its price. The choice of widths is the weakest part: `half` + `r32` and `half` + `e64` fit nearly as well (0.076, 0.075 W), so 64 bits and raw against encoded are not settled. E81's post-hoc `beat16` account is refuted: raw toggles at 16-bit steps cost nothing while wider words stand still.

### Every item

| item | lines | w | high | t_enc | t_raw | k | half | k_chan | W over zeros [95 %] | pJ per line | rail | frozen `w_hi_chan` |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `dm_w1` | 1 | 1 | 1 | 1 | 1 | 0 | 1 | 0 | **0.112** [0.040, 0.184] | 95 | +0.008 | 1.09 |
| `dm_u1` | 1 | 64 | 64 | 0 | 0 | 0 | 0 | 0 | **0.447** [0.385, 0.509] | 381 | -0.003 | 1.54 |
| `dm_u2` | 1 | 128 | 128 | 0 | 0 | 0 | 0 | 0 | **0.818** [0.763, 0.873] | 697 | +0.042 | 2.00 |
| `dm_u4` | 1 | 256 | 256 | 0 | 0 | 0 | 0 | 0 | **1.541** [1.430, 1.652] | 1,314 | +0.053 | 2.92 |
| `dm_u5` | 1 | 320 | 256 | 0 | 0 | 0 | 0 | 0 | **1.803** [1.732, 1.874] | 1,537 | +0.063 | 3.12 |
| `dm_u7` | 1 | 448 | 128 | 0 | 0 | 0 | 0 | 0 | **2.013** [1.889, 2.137] | 1,716 | +0.099 | 2.98 |
| `dm_u8` | 1 | 512 | 64 | 0 | 0 | 0 | 0 | 0 | **2.174** [2.093, 2.254] | 1,853 | +0.101 | 2.92 |
| `dm_l08` | 1 | 256 | 32 | 0 | 0 | 0 | 0 | 0 | **1.155** [1.093, 1.217] | 985 | +0.065 | 2.00 |
| `dm_a08` | 1 | 256 | 32 | 62 | 496 | 0 | 0 | 0 | **1.129** [0.997, 1.262] | 963 | +0.067 | 2.00 |
| `dm_a26` | 1 | 256 | 160 | 62 | 496 | 0 | 0 | 0 | **1.435** [1.363, 1.507] | 1,223 | +0.047 | 2.53 |
| `dm_a35` | 1 | 256 | 224 | 62 | 496 | 0 | 0 | 0 | **1.547** [1.505, 1.589] | 1,319 | +0.070 | 2.79 |
| `dm_a44` | 1 | 256 | 256 | 496 | 496 | 0 | 0 | 0 | **2.016** [1.969, 2.064] | 1,719 | +0.063 | 2.92 |
| `dm_r08` | 2 | 256 | 32 | 31 | 248 | 256 | 128 | 0 | **1.893** [1.753, 2.034] | 1,614 | +0.110 | 2.00 |
| `dm_r26` | 2 | 256 | 160 | 224 | 248 | 256 | 128 | 0 | **2.601** [2.564, 2.638] | 2,218 | +0.111 | 2.53 |
| `dm_r44` | 2 | 256 | 256 | 248 | 248 | 256 | 128 | 0 | **2.803** [2.695, 2.910] | 2,389 | +0.100 | 2.92 |
| `dm_L1` | 1 | 256 | 211 | 258 | 248 | 0 | 128 | 0 | **2.658** [2.596, 2.720] | 2,266 | +0.079 | 2.74 |
| `dm_L2` | 2 | 256 | 211 | 258 | 248 | 256 | 128 | 0 | **2.699** [2.669, 2.729] | 2,301 | +0.149 | 2.74 |
| `dm_L3` | 3 | 256 | 211 | 258 | 248 | 256 | 128 | 171 | **3.194** [3.143, 3.245] | 2,723 | +0.124 | 3.18 |
| `dm_L4` | 4 | 256 | 211 | 258 | 248 | 256 | 128 | 0 | **2.851** [2.820, 2.881] | 2,430 | +0.152 | 2.74 |
| `dm_L8` | 8 | 256 | 211 | 258 | 248 | 256 | 128 | 0 | **2.814** [2.648, 2.980] | 2,399 | +0.102 | 2.74 |
| `dm_L16` | 16 | 256 | 211 | 258 | 248 | 256 | 128 | 0 | **3.003** [2.890, 3.117] | 2,560 | +0.160 | 2.74 |
| `dm_L17` | 17 | 256 | 211 | 258 | 248 | 256 | 128 | 241 | **3.326** [3.274, 3.379] | 2,836 | +0.130 | 3.37 |
| `dm_L32` | 32 | 256 | 211 | 258 | 248 | 256 | 128 | 128 | **3.164** [3.100, 3.227] | 2,697 | +0.152 | 3.07 |
| `dm_L256` | 256 | 256 | 211 | 258 | 248 | 256 | 128 | 240 | **3.301** [3.271, 3.330] | 2,814 | +0.105 | 3.36 |
| `dm_L8192` | 8192 | 256 | 211 | 258 | 248 | 256 | 128 | 255 | **3.454** [3.362, 3.546] | 2,945 | +0.157 | 3.40 |
| `dp_c1` | 1 | 256 | 32 | 2 | 16 | 0 | 256 | 0 | **2.005** [1.953, 2.058] | 1,710 | +0.084 | 2.00 |
| `dp_c2` | 2 | 256 | 32 | 5 | 40 | 256 | 128 | 0 | **1.800** [1.714, 1.887] | 1,535 | +0.103 | 2.00 |
| `dp_bern` | 8192 | 256 | 209 | 258 | 248 | 256 | 128 | 255 | **3.466** [3.393, 3.540] | 2,955 | +0.143 | 3.40 |

*W over zeros from `dm.json` `headline.items_over_zeros_W` (32.33 W absolute for `dp_zeros`); pJ per line at the measured 1.17294 × 10⁹ lines/s, which no pattern moves (1.17292–1.17296 × 10⁹, `headline.line_rate_by_item`); rail over zeros, raw, from `headline.rail_over_zeros_W`. Frozen is `w_hi_chan`'s prediction (`tools/claims-v3/dm/predictions.json` `items`).*

## What ran, and what was registered

| | registered (`tools/claims-v3/dm/`, `590f9b7e`) | happened |
|---|---|---|
| command | E75's DRAM command unchanged: `flw_pat --harts 1 --seconds 4 --window 240000000 --stride 64 --slice-bytes 131072 --region 131072` | the same; the dry run printed 29 enercat lines, `lines:` for periods 3, 8, 16, 17, 32, 256, 8192 and `file:` for the rest (`logs/e99-dry.log`) |
| binary | the host's `file:` takes 256 B, so a copy of `main.cpp` with one added operand, `lines:`, on `enercat-hl`'s compile and link lines and its kernel ELF | built 01:05:10 PDT, card idle, 5 s. **The unchanged `main.cpp` rebuilt byte-identical to E81's host** (`57ba5546…`, 3,570,816 B). The E99 host is `f6633f1c…` (`.text` `eacec93b…`); kernel code `a5743c3c…`, the same ELF (`logs/e99-build-hashes.txt`, every pass's `text.sha256`) |
| items | 29 DRAM items + `anchor_pi` first and last | all, every pass |
| harness | E75's `mf/block.sh`, `mf/queue_mf.sh`, `runitems.py`, E81's estimator, unchanged | all harness files hashed identical on the box and a desk machine before the first launch (`logs/e99-box.sha`) |
| passes | smoke 9901, then 9910 onward, six at most; 9910 the warm-up | smoke 01:06:17–01:08:00 (`anchor_pi`, `dm_L17`, `dp_bern`, every launch ok); passes 01:08:07–01:34:37, 3.99–4.30 min each; headline 9911–9915 |
| budget | at most 33 card-minutes; no pass starts after 27 min or 01:50 PDT | **26.7 card-minutes** (smoke 1.73 + passes 24.99); the stop rule never acted; card session 01:06:16–01:34:47 PDT |
| claim | one post in `#community-lab` after the registration and before the first launch, edited at the release | posted 01:05:58 PDT, message `1566362654862352475`; released 01:35 PDT by editing the same post (D2) |
| card state | nothing set; `ettelem config` read only, under the lock, `timeout 10`, at both ends | `tdp_w` 0, `temp_threshold_c` 65, 600 MHz, 523 mV, `max_power` at 01:06:16 and at 01:34:47 (`ident/`); nothing written. Every launch at a 58.0 °C reading after a 59 °C preheat; window means 58.0–59.0 °C; worst window median `took_ms` 22 ms |

## Departures, dated

- **D1 (1 Nov 2026, after the registered reduction) — a post-hoc account.** `tools/claims-v3/dm/posthoc_fit.py`, with `posthoc-fit.txt` and `posthoc-fit.json`, labelled above. Its first draft was written while the passes ran, before any pass was read; the version committed was rewritten after the registered reduction was read, and adds counts `make_dm.py` does not register (`r32`, `r64`, `r128`, `e32`, `e64`, `e128`). No registered file changed.
- **D2 (1 Nov 2026, 01:35:13–01:35:56 PDT) — the release post was doubled for 43 seconds.** `edit_msg.mjs` appends, and the lane handed it the whole line, so the post read the claim twice and then " — released". `edit_replace.mjs` restored the one registered line (read back: "using aifoundry3 for 1 h, until ~01:07 PST doc — released"). No word of the claim was lost, and the post's id stayed the same.
- **D3 (inherited, as E60–E81) — two device processes outside `timeout 10`.** `lib.sh`'s `die_c` in `block_begin`/`block_end` runs `ettelem sample --seconds 1` under `timeout 20`, and the telemetry sampler runs for the whole pass. Every enercat and sparsity launch ran under `timeout 10`.
- **Not departures, for the record.** E92 released this card at 00:55 PDT, 20 min before the brief expected, so the registration (01:03:40) came after it, not before; the card was idle from then to the claim, and `build_host.sh` compiled in that gap. No pass was read while the queue ran: the lane's waits read only `build/e99-dm.log` and `block.json`. The 4-way item's +0.152 W, inside the "absent" class, is reported as measured. The PHY lines the registration cites are the 933 MHz branch's (`:720-727`, `:787`); the other branches' copies read the same (`:39-46`, `:106` at 1,067 MHz), and all six `INIT4` writes carry `emr2 = 0xf1` (`:4330`, `:4337`, `:4398`, `:4405`, `:4464`, `:4471`).

## Corrections after verification (Sun 1 Nov 2026)

An independent verifier checked E99 after the data commit. It rebuilt the contrasts from the raw telemetry with its own code, in all four arms, and got the same values with intervals, and it found the registration, the scorer, the tally, the harness, the host build, the images and the DBI statement sound. It found two major and eight minor faults in what the prose builds on them. Each was checked against the committed data, and none is rejected. Each is corrected in place, at the desk: no card was touched, nothing was re-run, and no frozen or data file changed (`dm*.json`, `runs.csv`, `dips.json`, `reduce.*`, `posthoc-desk.*`, `posthoc-fit.*`, the raw passes, `gen/`, and the registered files in `tools/claims-v3/dm/`). The scored verdicts stand: `overall_dbi` PARTIAL in every arm, R7, R11 (primary arm) and R12 FAIL. [`corrections-check.py`](corrections-check.py) prints every number below from committed files, and [`corrections-check.txt`](corrections-check.txt) is its output, under the section named.

| # | what was wrong | what changed |
|---|---|---|
| C1 (major) | **"This experiment does not say where it is paid."** The committed telemetry records the NoC and SRAM rails, and the registered reducer read only the minion rail. `tie18` is +0.828 W [0.790, 0.865] on the NoC rail of the board's +1.727; fitted, a one is NoC 1.60 ± 0.08, SRAM 0.16 ± 0.08, minion 0.17 ± 0.06 pJ of 3.24 ± 0.25, so about 1.3 pJ is off every metered rail. "Off the compute rail" was loose too: `tie18`'s minion interval excludes zero | A labelled post-hoc script and table (`posthoc_rails.py`, `posthoc-rails.*`, § Where it is paid). Reading 3, the `w` row and What it changes 1 say where it goes, and "still open" narrows to the 1.3 pJ. Added beyond the report: the 1.3 pJ holds the three regulators' own loss, because the rails are output-side (E30), and the rails read about 7 % low |
| C2 (major) | **"Period 8 is free, period 16 is not, an 8-way path pays (most of it)", with the AXI port as the candidate.** R11's FAIL stands as scored, but its reading does not: `h8` is +0.100 W [0.051, 0.148] on the SRAM rail; SRAM and NoC carry 58 % of `D` and 59 % of `h16`; off every metered rail `h4`, `h8`, `h16` are absent, and an 8-way and a 16-way count fit alike (0.037, 0.042 W rms). "So an 8-way path pays most of it" in What it changes 1 had no post-hoc label | Reading 4, the `k_shire` and `k_chan` rows and What it changes 1. Period 8 is "+0.115 W [−0.040, +0.271], inside the rule's absent band; +0.100 [0.051, 0.148] on the SRAM rail". The 8-way reading is one candidate, with the split beside it, and the AXI port is not a finding |
| C3 | **"There is no floor", "an all-zero line is not a special case".** R10's class stands, but `floor_w1`'s interval excludes zero, at 19 times the bit's own price. Fitted, the floor is +0.102 W on the board and +0.097 W on the SRAM rail | "The 1 W floor is gone; about 0.1 W remains, on the SRAM rail", in the lead, the table, reading 5, R10, What it changes 3 and Step 1. On the board only the primary arm's interval excludes zero, and reading 5 says so |
| C4 | **"Off the compute rail" and the blog's "none of this reaches the compute rail" meant the minion rail only.** NoC +0.133 and SRAM +0.273 W are 24 % of `tie_total`, and 58 % of `D`. `tie_total`'s minion interval is [+0.002, +0.078] | R13 is named as the minion rail, all three rails are named, and the arrangement, on no metered rail, is said |
| C5 | **"And raw toggles nothing: 0.588 W", "65 %".** The parts are 0.390 + 0.233 − 0.035. High and encoded alone are 0.622 W and 69 %, and with raw at zero the miss is 0.276 W, inside ±0.30. So the frozen FAIL by 0.011 W rests on a raw price of −0.14 pJ [−0.42, +0.14] | Reading 2, R12's row and What it changes 1 give the three parts and say so. R12 stays FAIL, and it fails by more at the sensitivities (0.42, 0.45 W) |
| C6 | **"A fifth to a quarter".** That span was point estimates only. The prices' 95 % intervals, 1.04–2.57 pJ, give 0.22–0.53 W, 13–33 % of 1.636 W | "About a quarter (13–33 %)" |
| C7 | **"Each of those holds its other counts equal", for `half`.** `dp_c1` − `dm_l08` also moves `r32` +32, `r64` +64, `r128` +128, `t_raw` +16, `t_enc` +2, and `dp_c1` has all its ones in the first 32 B | The sentence names the exception. 2.83 pJ is an upper bound (the fit gives 2.53), and the rails clear the first-half risk |
| C8 | **"The 18 points it never saw."** Five are byte-identical to fitted items, two are one image, and the terms came from earlier fits on them. Rms is 0.160 W on the 13 whose images it never fitted, 0.086 W on the five. `half` + `r128` is lower out of sample (0.130 W). The ladder is not balanced in `r64` (218.8–235, about 0.04 W) | The account's preamble and closing paragraph say so. `posthoc-fit.txt` and the script's docstring stand as committed |
| C9 | **Sources left as "inferred" or "from memory", and one claim with no power.** See the dated notes below. `result.md` said `t_raw` absent is "consistent with" in-order lane mapping, and the registration's risk note implies it could test that: under DBI `dm_a08` and `dm_l08` differ by at most 62 DMI toggles, about 0.06 W, against an interval of ±0.17 W | The notes below, the `hi` and `r64` rows, and `result.md`. The registered file stays frozen |
| C10 | **Wording.** The lead carried neither PARTIAL nor the FAILs. "A line's change … costs nothing visible" against the SRAM rail's `dp_c2` − `dp_c1` +0.083 W. The frozen-models paragraph left out `w_hi_chan`'s third failure, `ones_u8`, and others. One note in Step 1 was repeated three times by the lane's README builder, and `hi_t0`'s upper price was rounded to 1.83 (it is 1.82). The blog sentences named no card or clock | The lead states the overall reading and the FAILs; the sentence, the paragraph, the note and the rounding are fixed; the blog sentences (`result.md`) name aifoundry3 card 0 at 600 MHz and stay inside what the verifier allows |

**Dated notes on the registration's sources, Sun 1 Nov 2026** (`tools/claims-v3/dm/README.md` stays frozen; paths under the lab clone's `external/`, each read):

- **Bits 8:6.** Not only inferred: `core-et/rtl/inc/memshire_defines.vh:21-22` defines `MEMSHIRE_SEL_ADDR_RANGE 8:6` and `MEMSHIRE_MCTL_SEL_ADDR_RANGE 9`. It is defined there and used nowhere else in the open RTL.
- **Mode register 3.** TI's SPRACU8B states that MR3[6] enables read DBI and MR3[7] write DBI for LPDDR4, which is what `emr2 = 0xf1` sets (read on the web, Sun 1 Nov 2026).
- **The rule at p > 4.** Its primary text remains unread: JESD209-4 is not in the repo, TI's AM69 manual was reported by a search summary to state it and returned 404 to two fetches, and AMD's UG1087 fields were not reachable. The watts support it: of five encoders over the eleven no-toggle and beat images, the standard rule fits at 0.033 W rms against 0.259 W for no inversion, and `tie45`, +0.262 W [0.191, 0.332], excludes inverting at p = 4 (+0.141), a DMI pin that is free (+0.144) and a reversed DMI level (+0.054) (`corrections-check.txt` C9, post hoc).
- **The pad arithmetic.** The telemetry's `reg_mv.vddqlp` is 640 mV: half of it across 40 Ω is 1.37 pJ per beat at the pad, closer to the measured 1.5–1.9 pJ than the 0.6 V this README first used. 40 Ω is mode register 3's drive field (RZQ/6, from memory of the standard); that the termination matches it is an assumption.
- **The controller.** `DFIMISC.phy_dbi_mode = 0` (`memshire_ddr_init_functions.c:4765`); `DfiFreqRatio_p0 = 1` (`:768`), which supports four beats per 933 MHz clock.
- **The byte order.** High-pin counts need no order at all; every toggle price (0.82 pJ) assumes the in-order mapping, and `t_raw` cannot test it (C9). This assumes too that each fetched line reached the pins; E75 says some hit the L3 (`tools/claims-v3/mf/README.md`), and the line rate, 75.07 GB/s against DRAM's own 76, is consistent with few. Neither is measured here.
- **What remains unread.** The card's DDR controller registers and mode registers, the BL2 binary (the card reports 0.22.0 by version number, no git hash), and the standard's own text.

## What it changes

1. **Section 11 item 12's mechanism question is narrowed, not closed.** The arrangement: read DBI behaves as live on this card, and high pins plus encoded toggles are 69 % of it by direct prices (65 % with the raw term), all off every metered rail. A one: about half on the NoC rail. The period: on board power the channel count alone does not set the ladder, and 58 % of `D` is on the SRAM and NoC rails. Still open: the 1.3 pJ of a one that is off every metered rail (how much is regulator loss, the memory shires' logic, the DRAM chips); which unmetered paths carry `half` and the 64-bit toggles (post hoc); and what sets the ladder's steps on each rail, the 8-way path being one candidate.
2. **E81's two candidate encodings are decided.** DBI-DC stands and the 16-bit-toggle account falls: raw toggles at 16-bit steps are free (`t_raw`) when inversion hides them.
3. **E75's price of a carried one is confirmed by a different design**: 3.18–3.48 pJ against its 3.255, on images with equal high pins and no toggles. **E75's "first ones cost the most" has a reading, post hoc:** the 1 W floor is gone, about 0.1 W remains on the SRAM rail, and the rest looks like wide-path toggles, which `dm_l08` (+1.155 W) does not have and which E75's contiguous images do.
4. **For a power model of real data on this memory** (kinds page section 11 item 6), the zeros-to-random step has now been written as ones, high pins, pin toggles, wide-path toggles and path changes. That is post hoc; a model that uses it should test it on real tiles.
5. **For the blog material, on aifoundry3 card 0 at 600 MHz.** At the same number of ones, a byte's pattern moves what the pins carry. Inversion makes 0xFF nearly as cheap on the pins as 0x00, and that behaves as real, but a 0xFF byte still costs about 8 × 3 pJ off the pins, about half of it on the NoC rail.

**What would settle the rest, not run here.** A width ladder, 32-, 64-, 128- and 256-bit alternations at equal ones and high pins, registered first, would find the raw path's width. A pin-by-pin tent would test that all pins are alike. Moving a period-16 image by a shire-sized offset would test the 8-way reading by another route. A ladder registered per rail, with thresholds sized for each rail, would score what this one reads post hoc.

## Files

| file | what it is |
|---|---|
| `passes/p9901` | the smoke, not reduced |
| `passes/p9910`–`p9915` | the six passes: `runs.jsonl`, `marks.jsonl`, `telemetry.jsonl.gz`, `configs.json`, `block.json`, `code.sha256`, `gen.sha256`, `text.sha256`, `manifest.txt`, `run.log` |
| `gen/` | `make_dm.py`'s output: `manifest.json`, `srcs/*.bin` (byte-identical to the box's: `gen.sha256` here and in every pass), `counts.json` |
| `dm.json` | the reduction, the registered primary arm: dips removed, `auto` slope. **The result** |
| `dm-leak0.2936.json`, `dm-leak0.3803.json` | the two labelled sensitivities, dips removed |
| `dm-unfiltered.json` | the same reducer on the passes as they came |
| `dips.json` | every board-meter dip, and where it falls |
| `runs.csv` | one row per run, primary arm: pass, item, launch reading, p_raw, p80, rail, rate, median `took_ms`, gate failures |
| `reduce.sh`, `reduce.txt` | the reduction commands and their printed output |
| `posthoc-desk.txt`, `posthoc-desk.json` | **post hoc, labelled**: step 1, below |
| `posthoc-fit.txt`, `posthoc-fit.json` | **post hoc, labelled**: the account above, and all 28 candidate fits |
| `posthoc-rails.txt`, `posthoc-rails.json` | **post hoc, labelled**: the NoC, SRAM and minion rails per item, contrast and ladder rung, and the fits on them |
| `corrections-check.py`, `corrections-check.txt` | the desk check behind § Corrections after verification |
| `ident/` | `ettelem config` at the start and the end of the card session, their times, `et-lab-manifest` |
| `logs/` | the queue log, the smoke log, the dry run, the setup's output, the build's hashes, the box's harness hashes |

Code: `tools/claims-v3/dm/` (the registration: `README.md`, `dm_enc.py`, `make_dm.py`, `make_host_src.py`, `build_host.sh`, `run_e99.sh`, `make_predictions_e99.py`, `predictions.json`, `reduce_dm.py`, `selftest_dm.py`; post hoc, labelled: `posthoc_desk.py`, `posthoc_fit.py`, `posthoc_rails.py`), with E75's `mf/block.sh`, `queue_mf.sh`, `make_mf.py`, E81's `dp/make_dp.py`, `reduce_dp.py`, `posthoc_dips.py` and the runner `runitems.py`, all unchanged.

## Reproducing it

    # on aifoundry3, in ~/aifoundry, with the images in build/dm-gen and the card idle
    bash tools/claims-v3/dm/run_e99.sh build
    bash tools/claims-v3/dm/run_e99.sh setup
    bash tools/claims-v3/dm/run_e99.sh smoke 9901
    bash tools/claims-v3/dm/run_e99.sh go 9910 6
    # on any machine with the lab repo and numpy
    python3 tools/claims-v3/dm/make_dm.py build/dm-gen --check --e81-gen docs/reports/data/2026-10-31-e81-dram-pattern/gen
    bash docs/reports/data/2026-11-01-e99-dram-mechanism/reduce.sh
    # the labelled post-hoc views; DIR holds random.bin and bern50.bin from E81's src_replica.cpp, built with GCC
    D=docs/reports/data/2026-11-01-e99-dram-mechanism
    python3 tools/claims-v3/dm/posthoc_desk.py --e75 docs/reports/data/2026-10-28-e75-memory-flip-ladder \
      --e81 docs/reports/data/2026-10-31-e81-dram-pattern --builtins DIR --out $D/posthoc-desk.json > $D/posthoc-desk.txt
    python3 tools/claims-v3/dm/posthoc_fit.py $D --e81 docs/reports/data/2026-10-31-e81-dram-pattern --builtins DIR \
      --out $D/posthoc-fit.json > $D/posthoc-fit.txt
    python3 tools/claims-v3/dm/posthoc_rails.py $D --out $D/posthoc-rails.json > $D/posthoc-rails.txt
    ( cd $D && python3 corrections-check.py > corrections-check.txt )

## Step 1, at the desk: POST HOC, labelled

*`tools/claims-v3/dm/posthoc_desk.py`, output `posthoc-desk.txt`, `posthoc-desk.json`. This is not registered and not scored. It was
written after E75's and E81's data were seen, and it fits those data. Its only role is to freeze predictions for images it was not
fitted on.*

**What was computed.** A line-level encoder (`tools/claims-v3/dm/dm_enc.py`: two byte lanes, 32 beats, the read DBI rule, the 16-way channel
interleave) applied to every committed E75 and E81 DRAM image: pins driven high after inversion, pin toggles between beats after and
before inversion, bits changed between lines, and bits changed between two reads of one channel. Then least-squares fits of 18 measured
points, watts over each experiment's own zeros anchor: E81's ten data items and E75's seven rungs and its random anchor.

**What came out.**

| model | rms over the 18 points | of E81's 1.636 W (`dp_bern − dp_c2`) | of the arrangement, 0.996 W | of the period, 0.640 W | floor over zeros |
|---|---:|---:|---:|---:|---:|
| counting bits: ones + changed bits + floor | 0.516 W | **0** (the same counts by design) | 0 | 0 | +1.07 W |
| **the simplest DBI model**: high pins + encoded pin toggles + floor | 0.266 W | **0.972 W, 59 %** | 1.048 W | −0.076 W | +1.72 W |
| no DBI: ones + raw pin toggles + floor | 0.231 W | 0.920 W, 56 % | 0.904 W | 0.015 W | +0.90 W |
| ones + high pins + floor | 0.198 W\* | 1.013 W, 62 %\* | 0.823 W\* | 0.190 W\* | +1.00 W\* |
| ones + high pins + a channel's line changes + floor | 0.140 W | 1.394 W, 85 % | 0.755 W | 0.639 W | +1.09 W |
| ones + raw toggles + a channel's line changes + floor | 0.164 W | 1.332 W, 81 % | 0.695 W | 0.636 W | +0.99 W |

*\* That row also carries encoded toggles, `bits+dbi` in `posthoc-desk.txt`, with a price of −15 pJ per high pin and +14 pJ per encoded toggle: collinear
counts, not prices.*

Four readings, each from `posthoc-desk.txt`:

1. **The high-pin count alone gets the arrangement and none of the period.** The simplest DBI model gives 59 % of the 1.636 W: the whole 0.996 W arrangement
   and −0.076 W of the 0.640 W period.
2. **Adding a channel's line changes gets the period** (0.639 of 0.640 W at 2.2 pJ per bit changed between two reads of one channel), so 85 % of the 1.636 W.
   The count was built on the reading that each channel carries every 16th line, and E81's own finding is in the fit, so this agreement is no test.
3. **These data cannot tell high pins from toggles.** Across the 18 points the high-pin count, the encoded toggles and the raw toggles correlate at 0.99–1.00, and a model with
   no DBI at all fits about as well. The simplest DBI model's own toggle price is negative (−2.37 pJ) for that reason.
4. **Of the 63 % that counting bits missed** (E75's two prices give 36.6 % of the 3.25 W chord), the largest part is a floor. In the ones + high pins + channel model, random floats'
   3.31 W over zeros divide as floor 1.09 W (33 %), ones 0.88 W (27 %), high pins 0.84 W (25 %) and channel changes 0.50 W (15 %). So the floor, the high pins and the channel changes are
   what counting bits missed. Nothing yet says what the floor is, or that it is more than the shape of the response near zero: E75's w128 image already costs 1.405 W over zeros for
   128 ones and 16 high pins. `dm_w1`, one bit in every line, tests it. *(It did, Sun 1 Nov 2026: the 1 W floor is gone; about 0.1 W remains, on the SRAM rail; § Results.)*

**Why a registered test.** Images built to hold these counts apart, the same ones with different high pins, the same high pins with different ones, and the same high pins and toggles with different periods, make
the candidates disagree by up to 1.7 W (`tools/claims-v3/dm/README.md` §3).
