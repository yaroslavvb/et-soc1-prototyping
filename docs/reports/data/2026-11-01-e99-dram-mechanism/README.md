# E99 — which mechanism carries the DRAM pattern effect (Q132)

## Results

*Six passes, `p9910`–`p9915`, Sun 1 Nov 2026 01:08:07–01:34:37 PDT on aifoundry3 card 0, 600 MHz, `--harts 1` (1,024 harts), 29 DRAM items and the
drift anchor per pass, after a smoke (`p9901`, 01:06:17). **26.7 card-minutes** of the registered 33. Every pass `block.json` `"status":"ok"`, 186
runs, **no run-gate failure**, no pass set aside (drift 0.07–0.17 W). Pre-registered in `590f9b7e` (01:03:40 PDT), before the claim (01:05:58) and the first
launch. Reduced with `reduce.sh` (the registered `tools/claims-v3/dm/reduce_dm.py`, unchanged). Pass 9910 is the registered warm-up, so **the headline is five
passes, 9911–9915** (df = 4). Every number below is from `dm.json` `headline` (the registered primary arm: the board meter's dips removed) unless it says otherwise.
Intervals are 95 % t over the five headline passes at the registered `auto` leakage slope (0.0046 W/°C); the two registered sensitivities are in
§ [The leakage footing and the unfiltered arm](#the-leakage-footing-and-the-unfiltered-arm).*

**The firmware's read data-bus inversion is live in the watts, and pins driven high do pay. But they carry a fifth to a quarter of the pattern effect, not all of it.**
The largest price is not on the pins at all, the "floor" that every earlier fit needed does not exist, and a period that divides 16 is not free.

> | what | isolated by (same everything else) | W [95 %] | price | at 0.2936 / 0.3803 W/°C |
> |---|---|---:|---:|---:|
> | **a one bit**, with the pins held equal | `tie27`: 448 ones against 128, 128 high pins each, no toggle | +1.195 [1.048, 1.342] | **3.18** [2.79, 3.58] pJ per one | 2.97 / 2.90 |
> | | `tie18`: 512 against 64, 64 high pins each | +1.727 [1.620, 1.833] | **3.29** [3.08, 3.49] | 3.07 / 3.00 |
> | | `tie45`: 320 against 256, 256 high pins each: the rule's tie | +0.262 [0.191, 0.332] | **3.48** [2.55, 4.42] | 3.48 / 3.48 |
> | **a pin driven high**, per beat | `hi_t0`: the same 256 ones, no toggle, 256 high pins against 32 | +0.386 [0.293, 0.479] | **1.47** [1.12, 1.83] pJ | 1.58 / 1.61 |
> | | `hi_ta`: the same ones, raw and encoded toggles, 224 against 32 | +0.418 [0.258, 0.578] | **1.86** [1.15, 2.57] | 1.69 / 1.64 |
> | | `tent_S`: free of any linear price of ones | +0.513 [0.312, 0.715] | **1.71** [1.04, 2.38] | 1.63 / 1.61 |
> | **a pin toggle** after inversion | `t_both`: 0x0F/0xF0 beats against constant 0x0F, the same 256 high pins | +0.475 [0.396, 0.554] | **0.82** [0.68, 0.95] pJ | 0.87 / 0.88 |
> | **a raw toggle that inversion hides** | `t_raw`: 0x00/0xFF beats against constant lanes: raw +496, only the DMI pin moves | −0.026 [−0.199, +0.148] | **none** (absent) | absent at both |
> | **a bit that differs between a line's 32 B halves** | `half`: `dp_c1` against `dm_l08`, the same ones and high pins | +0.850 [0.785, 0.915] | **2.83** [2.61, 3.05] pJ | 3.08 / 3.16 |
> | **one bit in every line**, over an all-zero line | `floor_w1` | +0.112 [0.040, 0.184] | absent: **no floor** | unresolved (+0.21, +0.24) |

Each of those holds its other counts equal by construction (`gen/counts.json`, `tools/claims-v3/dm/make_dm.py --check`). Five readings:

1. **Read DBI is live on this card.** Nothing was read from the card's memory controller, so this is what the card does. The same +496 raw toggles per line cost nothing when the bytes
   alternate 0x00/0xFF (`t_raw`), which inversion turns into one moving DMI pin, and +0.475 W when they alternate 0x0F/0xF0 (`t_both`), which it cannot hide: **+0.501 W** [0.327, 0.675] between the two
   (+0.466 and +0.456 W at the sensitivities, each interval above 0; per-pass differences of `dm.json` `per_pass`). At the same ones and the same raw toggles, the watts climb with the high pins: 1.129, 1.435, 1.547 W
   at 32, 160, 224 high (`dm_a08`, `dm_a26`, `dm_a35`). Whole bytes of ones in random places cost what runs cost, +0.093 W [−0.059, +0.244] over `dp_c2`, while the same raw toggles from scattered bits cost +0.806 W more
   (`L2_vs_r08`). And the tent has its kink: on constant bytes the step is 4.82 pJ per added one below p = 4, 3.48 across the tie, 1.40 above p = 5 (table below). The mean of the outer two, 3.11, is about the ties' price of a one, and half their difference, 1.71 pJ, is the pin's.
2. **High pins carry a fifth to a quarter of it.** Of E81's 1.636 W (+1.666 W here), the 177 high pins that random bits add come to 0.31–0.39 W at the prices above. On the arrangement alone (`arr_L2`, +0.899 W), the direct prices give +0.390 W for its 179 high pins and +0.233 W for its 253 encoded toggles,
   and raw toggles nothing: 0.588 W, 0.311 W short, and **R12 fails**, just outside its ±0.30 W band (by more at the two sensitivities). High pins and encoded toggles are 65 % of the arrangement; the rest needs a path this design did not isolate (post-hoc account, below).
3. **The largest price is a raw one, and it is not on the pins.** All-0xFF bytes hold every data pin low and still cost +2.174 W over zeros (`ones_u8`). Three independent pairs at equal high pins give 3.18, 3.29 and 3.48 pJ per one, and **E75's 3.255 pJ** [2.97, 3.55], from contiguous images, sits among them. So E75's price
   was right and it is not a pin's. It is off the compute rail too (`tie18`: rail +0.103 W of the board's +1.727). This experiment does not say where it is paid: the DRAM's internal read path, the PHY and controller, the memory shire and the mesh all carry raw ones.
4. **The channel reading fails: a period that divides 16 is not free, and most of the step sits at an 8-way path.** Period 8 is free, period 16 is not. That is R11's registered named reading: a path of the 8-way interleave pays. The public datasheet names one candidate, each memory shire's 512-bit AXI port (§7.1.1.1), which carries every 8th line if bits 8:6 pick the shire, as the removal bits imply. The channel's own share is not separated from zero (post hoc, below).
5. **There is no floor.** All six models frozen before the data needed +0.99 to +1.72 W for any non-zero line, and `floor_w1` reads +0.112 W. An all-zero line is not a special case. The "floor" was toggling on wide paths, which every E75 and E81 image had: `dm_l08` carries the same 256 ones and 32 high pins as E75's images, with every 16-bit word alike, and costs +1.155 W against their +1.77–2.35 W (`posthoc-fit.txt`).

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
| **16** | **1** | **2** | **+0.304** [0.188, 0.421] | **present** | **40 %** | **0: refuted** |
| 17 | 17 | 17 | +0.628 [0.585, 0.671] | present | 83 % | 94 % |
| 32 | 2 | 4 | +0.465 [0.419, 0.511] | present | 62 % | 50 % |
| 256 | 16 | 32 | +0.602 [0.550, 0.654] | present | 80 % | 94 % |
| 8,192 (`D`) | 512 | 1,024 | +0.755 [0.670, 0.840] | present | 100 % | 100 % (E81: +0.640) |

*`h4`'s interval excludes 0 at this slope; it reads +0.033 and −0.002 W at the sensitivities. `dp_bern` − `dm_L8192` = +0.012 W [−0.090, +0.114]: E81's random bits and these lines of one byte distribution cost the same, so the ±11-bit spread E81's note ¹ worried about moves nothing.
A line's change in one hart's stream costs nothing visible (`h1`), as E75's k-arm said.*

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
| **R10** the floor (`floor_w1`) | +0.112 [0.040, 0.184] | reported | **absent** (unresolved at the sensitivities: +0.207, +0.236) |
| **R11** the channel | `h16` present | `h4 h8 h16` absent, `h3 h17` present, `h32` 15–85 % of `D` | **FAIL** (UNRESOLVED at both sensitivities and in the unfiltered arm: `h16` +0.244, +0.225, +0.242, never absent) |
| **R12** closure | predicted `arr_L2` +0.588, measured +0.899 W | within ±0.30 W | **FAIL**, by 0.011 W (0.42, 0.45 W short at the sensitivities) |
| **R13** the compute rail | `hi_t0` −0.012, `hi_ta` +0.003, `D` +0.008, `tie_total` +0.040 W | each within ±0.10 W | **PASS**, all four |

**The registered overall reading is PARTIAL:** R3 and R5 pass, R2 and R4 are unresolved because the high-pin effect is present at about half the frozen amount, and it is not REFUTED. It reads PARTIAL at all three slopes and in the unfiltered arm. What the rule does not say is that the DBI *signature* is plain and the DBI *share* is small: both come from the same numbers.

**The frozen models.** Every model frozen before the data over-predicts this experiment's structured images, by its floor. On the 28 items they err by 0.55–2.33 W rms (`w_tenc_chan` 0.553, `w_hi_chan` 0.705, `bits` 0.848, `w_traw_chan` 0.877, `dbi` 1.103, `dbi_chan` 2.332). The ones with no pin DC or with raw toggles lose on the contrasts: `w_traw_chan` falls outside its interval on `t_raw` (predicted +1.69 W), `hi_r`, `r08_vs_c2` and `L2_vs_r08`; `w_tenc_chan` on `t_enc` (predicted +1.29 W); the pure `dbi` on `tie27`, `tie18`. Of the models whose intervals can fail, only `w_hi_chan` holds every pin contrast, and it fails on `floor_w1` and `half`. So the shape with ones, high pins and path changes was right, with a floor where wide-path toggles belong.

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

*Chosen after the registered reduction was read, from 28 candidate fits (14 extras, each with and without a floor, all printed). Seven prices on 28 items describe those items; they are not seven measurements. The registered contrasts above are the measurement. Its check is the 18 points of E75 and E81 that it never saw.*

Fitted on E99 alone, per pass, **with no floor**, to **0.063 W rms**, and predicting **E75's and E81's 18 points to 0.143 W rms**:

| count, per 64 B line | price, pJ [±95 %] | a reading, not measured |
|---|---:|---|
| `w` ones | **3.30** [±0.10] | somewhere off the pins and the compute rail |
| `hi` pins driven high | **1.97** [±0.31] | DC through the terminated pins (the arithmetic from LPDDR4X's 0.6 V and a 40 Ω driver against a like termination gives about 1 pJ a beat at the pad, from memory of the standard) |
| `t_enc` toggles on the pins | **0.88** [±0.17] | the pins' capacitance |
| `half` bits differing between the 32 B halves | **2.53** [±0.21] | a 256-bit path, one BL16 burst per word |
| `r64` raw toggles between consecutive 64-bit pieces | **2.22** [±0.13] | a 64-bit path, four beats, one clock of the 933 MHz controller if 933 × 4 = 3,733 MT/s |
| `k_shire` bits changed between reads of an 8-way path | **1.85** [±0.46] | line-wide paths of a memory shire |
| `k_chan` the same for a 16-way path | **0.45** [±0.49] | not separated from zero |

What it makes of the earlier steps, in watts:

| step | measured | account | ones | high pins | pin toggles | `half` + `r64` | path changes |
|---|---:|---:|---:|---:|---:|---:|---:|
| E81's arrangement | +0.996 | +0.897 | 0 | +0.426 | +0.258 | +0.214 | 0 |
| E81's period | +0.640 | +0.634 | 0 | −0.016 | +0.004 | −0.047 | +0.691 |
| E81's whole step | +1.636 | +1.531 | 0 | +0.410 | +0.263 | +0.167 | +0.691 |
| zeros to random floats (E75's 3.25 W chord) | +3.222 | +3.086 | **+1.115** (35 %) | +0.475 (15 %) | +0.265 (8 %) | +0.717 (22 %) | +0.514 (16 %) |

So **the 36.6 % E75's two prices explained is the ones (35 % here), and the 63 % they missed is the pins (23 %), raw toggles on wide paths (22 %) and path changes (16 %)**, with 4 % unaccounted. Of E81's 1.636 W, the high pins are 25 %, pin toggles 16 %, the wide raw path 10 % and path changes 42 %. On the ladder alone, an 8-way count fits the ten rungs better than a 16-way one (0.065 against 0.093 W rms), and with both, 1.54 pJ [±0.58] against 0.55 pJ [±0.61]. The choice of widths is the weakest part: `half` + `r32` and `half` + `e64` fit nearly as well (0.076, 0.075 W), so 64 bits and raw against encoded are not settled. E81's post-hoc `beat16` account is refuted: raw toggles at 16-bit steps cost nothing while wider words stand still.

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
| harness | E75's `mf/block.sh`, `mf/queue_mf.sh`, `runitems.py`, E81's estimator, unchanged | all harness files hashed identical on the box and the Intel before the first launch (`logs/e99-box.sha`) |
| passes | smoke 9901, then 9910 onward, six at most; 9910 the warm-up | smoke 01:06:17–01:08:00 (`anchor_pi`, `dm_L17`, `dp_bern`, every launch ok); passes 01:08:07–01:34:37, 3.99–4.30 min each; headline 9911–9915 |
| budget | at most 33 card-minutes; no pass starts after 27 min or 01:50 PDT | **26.7 card-minutes** (smoke 1.73 + passes 24.99); the stop rule never acted; card session 01:06:16–01:34:47 PDT |
| claim | one post in `#community-lab` after the registration and before the first launch, edited at the release | posted 01:05:58 PDT, message `1566362654862352475`; released 01:35 PDT by editing the same post (D2) |
| card state | nothing set; `ettelem config` read only, under the lock, `timeout 10`, at both ends | `tdp_w` 0, `temp_threshold_c` 65, 600 MHz, 523 mV, `max_power` at 01:06:16 and at 01:34:47 (`ident/`); nothing written. Every launch at a 58.0 °C reading after a 59 °C preheat; window means 58.0–59.0 °C; worst window median `took_ms` 22 ms |

## Departures, dated

- **D1 (1 Nov 2026, after the registered reduction) — a post-hoc account.** `tools/claims-v3/dm/posthoc_fit.py`, with `posthoc-fit.txt` and `posthoc-fit.json`, labelled above. Its first draft was written while the passes ran, before any pass was read; the version committed was rewritten after the registered reduction was read, and adds counts `make_dm.py` does not register (`r32`, `r64`, `r128`, `e32`, `e64`, `e128`). No registered file changed.
- **D2 (1 Nov 2026, 01:35:13–01:35:56 PDT) — the release post was doubled for 43 seconds.** `edit_msg.mjs` appends, and the lane handed it the whole line, so the post read the claim twice and then " — released". `edit_replace.mjs` restored the one registered line (read back: "using aifoundry3 for 1 h, until ~01:07 PST doc — released"). No word of the claim was lost, and the post's id stayed the same.
- **D3 (inherited, as E60–E81) — two device processes outside `timeout 10`.** `lib.sh`'s `die_c` in `block_begin`/`block_end` runs `ettelem sample --seconds 1` under `timeout 20`, and the telemetry sampler runs for the whole pass. Every enercat and sparsity launch ran under `timeout 10`.
- **Not departures, for the record.** E92 released this card at 00:55 PDT, 20 min before the brief expected, so the registration (01:03:40) came after it, not before; the card was idle from then to the claim, and `build_host.sh` compiled in that gap. No pass was read while the queue ran: the lane's waits read only `build/e99-dm.log` and `block.json`. The 4-way item's +0.152 W, inside the "absent" class, is reported as measured. The PHY lines the registration cites are the 933 MHz branch's (`:720-727`, `:787`); the other branches' copies read the same (`:39-46`, `:106` at 1,067 MHz), and all six `INIT4` writes carry `emr2 = 0xf1` (`:4330`, `:4337`, `:4398`, `:4405`, `:4464`, `:4471`).

## What it changes

1. **Section 11 item 12's mechanism question is narrowed, not closed.** The arrangement: read DBI is live on the silicon, and high pins plus encoded toggles are 65 % of it by direct prices. The period: the steps do not follow the channel count; period 16 costs, so an 8-way path pays most of it. Still open: where a one pays its 3.3 pJ; which wide paths carry `half` and the 64-bit toggles (post hoc); and that the 8-way path is the memory shire's AXI port, which is inferred.
2. **E81's two candidate encodings are decided.** DBI-DC stands and the 16-bit-toggle account falls: raw toggles at 16-bit steps are free (`t_raw`) when inversion hides them.
3. **E75's price of a carried one is confirmed by a different design**: 3.18–3.48 pJ against its 3.255, on images with equal high pins and no toggles. **E75's "first ones cost the most" is explained:** there is no floor, only wide-path toggles, which `dm_l08` (+1.155 W) does not have and which its contiguous images do.
4. **For a power model of real data on this memory** (kinds page section 11 item 6), the zeros-to-random step has now been written as ones, high pins, pin toggles, wide-path toggles and path changes. That is post hoc; a model that uses it should test it on real tiles.
5. **For the blog material.** At the same number of ones, a byte's pattern moves what the pins carry. Inversion makes 0xFF nearly as cheap on the pins as 0x00, and that is real, but a 0xFF byte still costs about 8 × 3.3 pJ off the pins.

**What would settle the rest, not run here.** A width ladder, 32-, 64-, 128- and 256-bit alternations at equal ones and high pins, registered first, would find the raw path's width. A pin-by-pin tent would test that all pins are alike. Moving a period-16 image by a shire-sized offset would test the 8-way reading by another route.

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
| `ident/` | `ettelem config` at the start and the end of the card session, their times, `et-lab-manifest` |
| `logs/` | the queue log, the smoke log, the dry run, the setup's output, the build's hashes, the box's harness hashes |

Code: `tools/claims-v3/dm/` (the registration: `README.md`, `dm_enc.py`, `make_dm.py`, `make_host_src.py`, `build_host.sh`, `run_e99.sh`, `make_predictions_e99.py`, `predictions.json`, `reduce_dm.py`, `selftest_dm.py`; post hoc, labelled: `posthoc_desk.py`, `posthoc_fit.py`), with E75's `mf/block.sh`, `queue_mf.sh`, `make_mf.py`, E81's `dp/make_dp.py`, `reduce_dp.py`, `posthoc_dips.py` and the runner `runitems.py`, all unchanged.

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
   128 ones and 16 high pins. `dm_w1`, one bit in every line, tests it. *(It did, Sun 1 Nov 2026, 01:35 PDT: there is no floor; § Results.)* *(It did, Sun 1 Nov 2026, 01:35 PDT: there is no floor; § Results.)*

**Why a registered test.** Images built to hold these counts apart, the same ones with different high pins, the same high pins with different ones, and the same high pins and toggles with different periods, make
the candidates disagree by up to 1.7 W (`tools/claims-v3/dm/README.md` §3).


