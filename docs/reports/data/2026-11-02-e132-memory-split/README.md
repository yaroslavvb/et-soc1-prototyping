# E132 — the memory path's split: which interleave pays, and the encoded part (Q136)

*On the kinds page, [section 11, what is still open](https://spacesheep.dev/@yaroslavvb/horace-kinds-of-numbers#11-what-is-still-open),
**item 10, "The memory path"** (the list as it reads at `fbb682f9393b`), critic 10 of Q134's final critic: "images not periodic in the
line index; a registered test that separates the encoded part at the DDR die rail". This README answers it in part: § What it changes,
item 1.*

## Results

*Seven passes, `p13210`–`p13216`, Mon 2 Nov 2026 10:27:39–10:58:50 PST on aifoundry3 card 0, 600 MHz, `--harts 1` (1,024 harts), after a
smoke (`p13201`, 10:25:18–10:27:39, gate PASS). **33.8 card-minutes** (session 10:25:18–10:59:05) of the 40 allowed. Every pass
`block.json` `"status":"ok"`, 168 runs, **no run-gate failure**, no pass set aside (anchor drift 0.07–0.21 W). Pre-registered in
`34ec50b8` (`tools/claims-v3/e132/`, committed and pushed 10:22:37 PST) before the claim (10:25:07) and the first launch. Reduced with
`reduce.sh` (the registered `reduce_e132.py`, unchanged). Pass 13210 is the registered warm-up, so **the headline is six passes,
13211–13216** (df = 5). Every number below is from `e132.json` `headline` (the registered primary arm: the board meter's dips removed,
E81's `auto` leakage slope, here 0.0228 W/°C) unless it says otherwise. Intervals are 95 % t over the six passes.*

**The registered reading: R1, R2, R5 and R6 PASS; R3 and R4 are UNRESOLVED, each by a hair; no rule fails.** On this card a DRAM line's
cost depends on which other lines share its paths, and the address-bit images locate it: **a channel (the 16-way interleave) pays
+0.31 W [0.21, 0.41] when the lines it carries change from one to the next, off every metered rail (R2, EDGES, as predicted)**, and the
memory shire (8-way) pays +0.22 W [0.11, 0.33], half of it on the NoC rail. Inside a channel, bits 5–7 of the line index cost nothing
that resolves; everything at 256 ways and wider costs +0.25 W, 40 % of it on the SRAM rail. A hart's own in-order stream, isolated here
with every path's view held, costs +0.18 W for 504 bits a line. **The encoded part:** at equal raw toggles, 392 more encoded 64-bit toggles a line
cost +0.166 W [0.121, 0.210] beyond the pins at a high raw load and +0.118 W [−0.002, +0.237] at a low one, and they move the DDR die rail
(−0.77 mV), but R3's and R4's registered classes need one more condition each, which misses by 0.01 mV and 0.002 W.

> | what | isolated by | board W [95 %] | where it is paid | DDR die rail, mV |
> |---|---|---:|---|---:|
> | **a channel's line-to-line changes** (16-way, bit 4) | `R_4` = `ab_4` − `ab_3`, hart stream removed | **+0.310** [0.212, 0.408] | **off every metered rail** (the three rails −0.018 [−0.079, +0.043]; off +0.328) | **−0.64** [−0.99, −0.30], moves |
> | **a memory shire's** (8-way, bit 3) | `R_3` = `ab_3` − `ab_2` | **+0.220** [0.107, 0.334] | **NoC +0.113** [0.090, 0.136]; off +0.127 [−0.013, +0.267] | −0.36 [−0.70, −0.03], moves |
> | the 4-way and 2-way paths (bits 2, 1) | `R_2`, `R_1` | +0.083 [−0.003, +0.169], +0.138 [−0.011, +0.287] | SRAM +0.057 [0.029, 0.084], +0.040 [0.002, 0.079] | still |
> | the 1-way paths (bit 0) | `R_0` = `ab_0` − `dm_u4` | +0.035 [−0.123, +0.193] (raw `D_0` +0.223, mostly the hart stream) | SRAM +0.071 [0.017, 0.125] | still |
> | inside a channel (bits 5, 6, 7) | `R_5`, `R_6`, `R_7` | +0.013 [−0.040, +0.066], +0.001 [−0.055, +0.057], −0.094 [−0.207, +0.018] | SRAM +0.042 [0.032, 0.053] on `R_5` | still |
> | **256 ways and wider** (the not-periodic image over `ab_7`) | `R_hi` = `ab_rnd` − `ab_7` | **+0.249** [0.203, 0.294] | **SRAM +0.097** [0.080, 0.115], off +0.124, NoC +0.035 | −0.12 [−0.20, −0.04] |
> | **a hart's own stream**, 504 bits a line | `H` = `ab_x70` − `ab_7` | **+0.184** [0.120, 0.249] | SRAM +0.070, NoC +0.030, off +0.066 | −0.03 |
> | the whole ladder: two-value lines in no period, over constant ones | `R_all` = `ab_rnd` − `dm_u4` | **+0.955** [0.865, 1.045] | NoC +0.133, SRAM +0.321, off +0.467 | −1.00 |
> | **encoded toggles beyond the pins, raw 448** (+392 a line) | `E448` = (`vl_64` − `c3_64`) − pins | **+0.166** [0.121, 0.210] | off every metered rail | +0.01 (both items read about −1.1 mV) |
> | the same, **raw 56** (`eh_64` against its twin `el_64`) | `E56` | +0.118 [−0.002, +0.237] | off every metered rail | `RE64` **−0.77** [−1.02, −0.52], moves |
> | the same, raw 192, +168 encoded 64-bit toggles | `E192` | +0.139 [0.066, 0.213] | off | `RE128` −0.50 [−0.87, −0.13], moves |
> | **192 pins held high**, every toggle equal | `Hp` = C3 − W, both rungs | **+0.365** [0.318, 0.412]: **1.62 pJ** a pin | off every metered rail | `RH64` +0.00, `RH128` +0.04: still |

*From `e132.json` `headline.contrasts` (board, `noc`, `sram`, `minion`, `off`, `ddr_mv`) and `verdicts`. The rungs are hart-corrected
as registered (`R(x, y)` = (x − y) − (k_x − k_y)/504 · `H`); the uncorrected differences are `D_…` in the same file. Line rate
1.17294 × 10⁹ lines/s, which no image moved (1.17291–1.17296 × 10⁹, `headline.line_rate_by_item`).*

Six readings:

1. **A channel pays for changes between the lines it carries** (R2 PASS, EDGES). `ab_4` puts A and B half and half on every channel and
   `ab_3` gives each channel one value, with every finer path's view the same: the difference is +0.310 W [0.212, 0.408], against
   +0.204 W predicted from E110's prices with each path's line edge counted and +0.008 W if only the pins saw it. It is off every metered
   rail. Spread over 128 bits a line on a 256-bit path it is 2.06 pJ a bit (`R2_channel_rung.R_4.pJ_per_bit_on_a_256_bit_path`), nearer
   E110's within-line price of the half-line bits (2.38 pJ) than its line-edge price (1.15). E110's images repeated one line, so a path that
   carries one line after another never saw a change there; this one does, and E110's 256-bit price is not changed by it.
2. **The memory shire's rung is on the NoC rail; the channel's is not.** `R_3` reads +0.113 W [0.090, 0.136] on the NoC rail of its
   +0.220 W, and `R_4` −0.023 [−0.067, +0.020]. A memory shire's two channels meet on its way to the network (its NoC-side port), and lines
   from its two channels that differ toggle what they share there. **So the NoC rail's period step is the memory shire's interleave**:
   E99's "NoC's L16 − L8 is small and above zero" (`R_3` is that path, isolated).
3. **The SRAM rail pays at fine interleaves and at 256 ways and wider, not at the shire or the channel.** SRAM: `R_0` +0.071, `R_1`
   +0.040, `R_2` +0.057, `R_3` +0.020 [−0.009, +0.049], `R_4` +0.019 [−0.008, +0.045], `R_5` +0.042, `R_6` −0.008, `R_7` −0.018, `R_hi`
   **+0.097**, and the hart stream +0.070 W. E99's SRAM step "between 4 and 8" is `R_2`, and its large L8192 − L32 step (+0.173) is mostly
   `R_hi` (+0.097) with `R_5` (+0.042). Off the rails, the channel's `R_4` (+0.328) is the largest step, then `R_3` and `R_hi` (+0.124
   each). **R5 PASS**: on every rail where E99's mapped step and this run's rung both resolve, they agree (`R5_rail_steps.rails.*.against_E99`).
4. **The DDR die rail moves at the shire and channel rungs** (reported, not scored): `ab_3` reads −0.46 mV over zeros and every image
   from `ab_4` up −0.97 to −1.10 (`headline.over_zeros.ddr_mv`), so `R_3` −0.36 and `R_4` −0.64 mV move, and nothing finer than the shire
   does. *A reading, post hoc:* the memory shires' logic sees the line-to-line changes of its channels (E110 found the rail still on the
   half-line path and on 192 raw 64-bit toggles a line, so a path that only sees `R_4`'s 32 line-edge toggles a line on 64 bits would not
   move it; a register as wide as a line would).
5. **The encoded part pays on the board and moves the DDR die rail; the two registered verdicts stay UNRESOLVED.**
   - *R4, the board:* beyond the pins (98 more pin toggles at the in-session `V16`) and their 32 extra high pins (at the in-session `Hp`),
     392 more encoded 64-bit toggles a line cost **+0.166 W [0.121, 0.210]** at raw 448 (`E448`, 0.36 pJ a toggle; E110's `E64` at the same
     counts +0.185 [0.077, 0.293], by its registration's formula) and **+0.118 W [−0.002, +0.237]** at raw 56 (`E56`). E56's lower end is
     **0.002 W below zero**, so it is not *present* and R4 reads UNRESOLVED, not PAYS. `E192` (168 more at raw 192) is +0.139 [0.066, 0.213].
   - *R3, the DDR die rail:* `eh_64` (raw 56, encoded 448) moves the rail over zeros (−0.86 mV [−0.98, −0.73]), and its encoded-quiet twin
     `el_64` (raw 56, encoded 56) reads −0.09 mV [−0.31, +0.13]; `RE64` = `eh_64` − `el_64` **moves, −0.77 mV [−1.02, −0.52]**, and the raw
     control `wl_64` moves (−1.09). ENCODED needs `el_64` *still*: its interval's lower end is **0.01 mV past** the ±0.30 mV band, so R3 reads
     UNRESOLVED. Reported beside it: `RE128` = `vl_128` − `c3_128` moves (−0.50 mV), with `c3_128` still (−0.10) and `vl_128` moving (−0.60):
     E110's `V128`/`S128` split, now with the high pins held equal. **R6 PASS:** 192 pins held high leave the rail still (`RH64` +0.00,
     `RH128` +0.04 mV).
6. **The session is E110's** (R1 PASS, all six within ±0.30 W): `S64` +0.301 (E110 +0.358), `S128` +0.157 (+0.135), `V16` +0.503 (+0.481),
   `V64` +0.669 (+0.651), `V128` +0.339 (+0.337), every byte 0x0F over zeros +1.535 (+1.624) W. A pin held high costs 1.62 pJ [1.41, 1.83]
   (`Hp` / 192 / line rate; E99's `hi_t0` 1.47 [1.12, 1.82]).

### Scoring

| rule | reading | registered | verdict |
|---|---|---|---|
| **R1** session tie | `S64` +0.301, `S128` +0.157, `V16` +0.503, `V64` +0.669, `V128` +0.339, `U4z` +1.535 W | within ±0.30 of E110's +0.358, +0.135, +0.481, +0.651, +0.337, +1.624 | **PASS**, all six |
| **R2** a channel's path, line to line | `R_4` +0.310 [0.212, 0.408] W, present; the three rails −0.018 [−0.079, +0.043] | EDGES (+0.204 W) | **PASS**: EDGES |
| **R3** the encoded part, DDR die rail | `wl_64z` moves (−1.09), `eh_64z` moves (−0.86), `RE64` moves (−0.77 [−1.02, −0.52]), **`el_64z` unresolved (−0.09 [−0.31, +0.13])** | ENCODED (`el_64z` still) | **UNRESOLVED**: `el_64z`'s interval is 0.01 mV past the still band; every other class is as predicted |
| **R4** the encoded part, board | `E448` +0.166 [0.121, 0.210] present; **`E56` +0.118 [−0.002, +0.237] unresolved** | PAYS (+0.185 W each) | **UNRESOLVED**: `E56`'s lower end is 0.002 W below 0 |
| **R5** each rail's steps against E99's | board, NoC, SRAM, off: no rung that resolves in both disagrees (board `R_3`, `R_4`, `R_wide`; NoC `R_3`; SRAM `R_1`, `R_2`, `R_wide`; off `R_4`); minion: none resolves | no contradiction | **PASS** (minion UNRESOLVED) |
| **R6** pins held high, DDR die rail | `RH64` +0.00 [−0.03, +0.03], `RH128` +0.04 [−0.07, +0.15] mV, still | still | **PASS** |

*From `e132.json` `verdicts`. The same six verdicts in every arm: both leakage sensitivities and the unfiltered arm (below).*

### The leakage footing and the unfiltered arm

| contrast | primary: `auto` (0.0228 W/°C), dips removed | 0.2936 W/°C | 0.3803 W/°C | unfiltered, `auto` |
|---|---:|---:|---:|---:|
| `R_3` | +0.220 [+0.107, +0.334] | +0.237 [+0.114, +0.360] | +0.242 [+0.067, +0.417] | +0.409 [−0.125, +0.944] |
| `R_4` | +0.310 [+0.212, +0.408] | +0.333 [+0.221, +0.445] | +0.340 [+0.197, +0.483] | +0.279 [+0.206, +0.352] |
| `R_hi` | +0.249 [+0.203, +0.294] | +0.157 [+0.097, +0.217] | +0.128 [+0.040, +0.216] | +0.199 [+0.029, +0.370] |
| `H` | +0.184 [+0.120, +0.249] | +0.155 [+0.017, +0.293] | +0.146 [−0.051, +0.342] | +0.193 [+0.117, +0.270] |
| `E448` | +0.166 [+0.121, +0.210] | +0.165 [+0.007, +0.322] | +0.164 [−0.053, +0.381] | +0.166 [+0.124, +0.208] |
| `E56` | +0.118 [−0.002, +0.237] | +0.144 [−0.051, +0.339] | +0.152 [−0.088, +0.392] | +0.123 [−0.026, +0.272] |
| `Hp` | +0.365 [+0.318, +0.412] | +0.418 [+0.284, +0.552] | +0.435 [+0.266, +0.604] | +0.323 [+0.171, +0.475] |
| verdicts that move | | none | none | none |

*From `e132.json`, `e132-leak0.2936.json`, `e132-leak0.3803.json`, `e132-unfiltered.json` (its own `auto` slope, 0.0237 W/°C).* No
verdict moves in any arm. At the higher slopes the corrections add scatter and the encoded residuals' intervals widen past zero; `R_hi`
and `H` shrink, because the not-periodic image and the stream image warm their windows most (`ab_rnd` +1.0 °C over its launch reading,
`ab_x70` +0.72, `ab_7` +0.61; `runs.csv`, headline passes). Without the dip filter `R_3`'s interval is five times wider: two dip samples
fell in `ab_2`'s window in pass 13211 (`reduce.txt`). The DDR die rail is untouched by
the leakage correction. Every launch read 58.0 °C after a 59–60 °C preheat (`runs.csv`). Dips: 166 samples in seven passes, 23 inside a
run's window (`dips.json`, `reduce.txt`).

### Every address-bit image over zeros

| item | sees changes | `k` | board W [95 %] | NoC | SRAM | minion | off | DDR die rail, mV |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| `dm_u4` | none | 0 | **+1.535** [+1.442, +1.628] | +0.490 | +0.139 | +0.071 | +0.835 | −0.08 |
| `ab_0` | 1-way | 512 | **+1.758** [+1.591, +1.924] | +0.516 | +0.282 | +0.148 | +0.811 | −0.10 |
| `ab_1` | 2-way and finer | 256 | **+1.802** [+1.709, +1.895] | +0.520 | +0.287 | +0.104 | +0.891 | −0.10 |
| `ab_2` | 4-way | 128 | **+1.838** [+1.727, +1.950] | +0.514 | +0.326 | +0.147 | +0.852 | −0.10 |
| `ab_3` | 8-way (memory shire) | 64 | **+2.035** [+1.940, +2.130] | +0.623 | +0.336 | +0.105 | +0.970 | −0.46 |
| `ab_4` | 16-way (channel) | 32 | **+2.334** [+2.258, +2.409] | +0.598 | +0.351 | +0.091 | +1.294 | −1.10 |
| `ab_5` | 32-way | 16 | **+2.341** [+2.269, +2.412] | +0.593 | +0.391 | +0.076 | +1.281 | −1.08 |
| `ab_6` | 64-way | 8 | **+2.339** [+2.248, +2.429] | +0.575 | +0.382 | +0.121 | +1.260 | −1.05 |
| `ab_7` | 128-way | 4 | **+2.243** [+2.132, +2.354] | +0.588 | +0.364 | +0.113 | +1.178 | −0.97 |
| `ab_x70` | 128-way (as `ab_7`) | 508 | **+2.427** [+2.348, +2.507] | +0.618 | +0.434 | +0.131 | +1.244 | −1.00 |
| `ab_rnd` | every way, not periodic | 258 | **+2.584** [+2.505, +2.664] | +0.638 | +0.496 | +0.114 | +1.336 | −1.10 |

*Over `dp_zeros` (absolute in `headline.items_W`), from `headline.over_zeros`; `k` = bits a hart's in-order stream changes a line
(`gen/counts.json` `k_stream`). The rails are raw over [t0+2 s, t0+4 s), which holds about 93.5 % of a settled step (E99, E110 C1), so every
rail figure reads about 7 % low; "off" is the board less the three rails.*

## What ran, and what was registered

| | registered (`tools/claims-v3/e132/`, `34ec50b8`) | happened |
|---|---|---|
| command | E110's DRAM command unchanged | the same; the dry run printed 22 `enercat_host` lines with the frozen arguments (`logs/e132-dry.log`) |
| binary | E99's host on the box, not rebuilt | `build/enercat-e99/host/enercat_host` `f6633f1c…`, `.text` `eacec93b…`, kernel code `a5743c3c…`: E99's and E110's |
| images | 7 of E110's bytes and 15 new; `make_e132.py --check` | all 22 checked on the Intel (`gen/counts.json`, 0 bad) and by hash on the box before the first launch (`sha256sum -c`, rc 0); every pass's `gen.sha256` from the same tree |
| harness | E75's `mf/block.sh`, `runitems.py`, `lib.sh`, E110's smoke gate, unchanged | the six shared files hashed identical on the box and the Intel (`logs/e132-setup.log`) |
| session | one detached `session_e132.sh`: config, smoke 13201, gate, passes 13210–13216 under a deadline of start + 36 min, config | config 10:25:18; smoke 10:25:18–10:27:39, gate PASS; passes 10:27:39–10:58:50, 239–268 s each, all seven run; config 10:59:05 |
| budget | at most 40 card-minutes; no session after 15:00 PST, all ends by 16:00 | **33.8 card-minutes**; the deadline (11:01:18) never acted |
| claim | the day's one card post, rewritten to add this card's clause after the registration, and to drop it at the release | message `1566837317765963987`: rewritten 10:25:07 PST from "…aifoundry1 card 1 … ; using aifoundry2 for 3 h, until ~13:20 PST [doc]" to add "; using aifoundry3 for 1 h, until ~11:25 PST [doc](<…horace-kinds-of-numbers>)" (dry run, `--save`, read back); rewritten 10:59:47 PST to drop it, the aifoundry2 clause kept (read back: "using aifoundry2 for 3 h, until ~13:20 PST doc") |
| card state | nothing set; `ettelem config` read only, under the lock, `timeout 10`, at both ends | `tdp_w` 0, `temp_threshold_c` 65, `max_power`, 600 MHz, 523 mV at 10:25:18 and at 10:59:05 (`ident/`); nothing written; `et-who` before and after: no process holds a device node or card lock |
| device commands | nine reads, no write (§ Device commands sent) | the same code ran; no `--reset-ms`, no firmware-revisions query, no residency read, no set |

## Device commands sent

*His rule of Mon 2 Nov 2026 (Q136). Classified from et-platform `836a4ab` (BL2 0.22.0's public source) through Q136(w)'s table, before the
first launch: the registration's [§ 5](../../../../tools/claims-v3/e132/README.md#5-device-commands-sent), unchanged, and the preflight
checker's output `tools/claims-v3/e132/dmcmd-audit.txt` (GO, no allow-list).* aifoundry3 runs a non-public thermal build of 0.22.0, so
each class is `836a4ab`'s handler, which that build may not share (Q136(w) result 1).

| # | command | sent by | class |
|---|---|---|---|
| 1 | `DM_CMD_GET_MODULE_STATIC_TDP_LEVEL` | `ettelem config`, twice (10:25:18, 10:59:05) | READ (copies SP RAM; `thermal_pwr_mgmt.c:613`) |
| 2 | `DM_CMD_GET_MODULE_TEMPERATURE_THRESHOLDS` | `ettelem config` | READ (`:665`) |
| 3 | `DM_CMD_GET_MODULE_POWER_STATE` | `ettelem config` | READ (`:551`) |
| 4 | `DM_CMD_GET_ASIC_FREQUENCIES` | `ettelem config`; `ettelem sample` | READ (PLL registers; `perf_mgmt.c:276`) |
| 5 | `DM_CMD_GET_ASIC_VOLTAGE` | `ettelem config`; `ettelem sample` | READ — two PMIC voltage-register reads, allowed by his rule of 2 Nov (`:1142` → `pmic_controller.c:1473`) |
| 6 | `DM_CMD_GET_MODULE_POWER` | `ettelem sample`; `lib.sh` `drain_mgmt` only after a sampler failure (none happened) | READ (`:984`) |
| 7 | `DM_CMD_GET_SP_STATS` | `ettelem sample` | READ (copies SP RAM, resets nothing; `performance.c:404`) |
| 8 | `DM_CMD_GET_MODULE_CURRENT_TEMPERATURE` | `ettelem sample`; `lib.sh` `die_c` | READ (`:732`) |
| 9 | `DM_CMD_GET_MODULE_VOLTAGE` | `ettelem sample` at 10 Hz (the DDR die rail is read from it) | READ — nine PMIC voltage-register reads, allowed by his rule of 2 Nov (`:1010` → `pmic_controller.c:1473`) |

**Not sent:** the statistics reset (`DM_CMD_SET_STATS_RUN_CONTROL`: `mf/block.sh:71` starts the sampler with the output file and the
duration only); `DM_CMD_GET_MODULE_FIRMWARE_REVISIONS`; any residency read; any `DM_CMD_SET_*`; no governor, TDP, threshold or clock set,
no reset, power cycle, PCIe, driver, firmware or OTA work. The host programs (`enercat_host`, `sparsity_host`) open the ops node only.
`et-lab-manifest`, run once a pass, reads sysfs and files and never opens a device node (its own header, read on the box).

## Departures, dated

- **D1 (Mon 2 Nov 2026, before the claim) — a wrong time in the frozen header.** The registration's first line says "about 10:35 PST"; it
  was committed and pushed at 10:22:37 PST (`34ec50b8`), before the claim (10:25:07) and the first launch (10:25:18). The frozen file is
  left as committed.
- **D2 (inherited, as E60–E110) — two device processes outside `timeout 10`**: `lib.sh`'s `die_c` in `block_begin`/`block_end` (`ettelem
  sample --seconds 1` under `timeout 20`) and the telemetry sampler for the whole pass. Every enercat and sparsity launch ran under
  `timeout 10`.
- **Not departures, for the record.** aifoundry3 had idle logins of other lab users throughout (an idle login does not block there, E60's
  D1 and the owner's ruling of 1 Nov); `block.sh`'s check found no other user's device process or lock. aifoundry3's Tailscale check went
  unapproved from 09:56:04 to 10:05:53 PST (three probes, each killed at 15 s); nothing had started. No pass was read while the queue ran
  (the lane's waits read the session log and the queue's log only). The reducer's filtered copies are in `build/e132-dipwork`, not
  committed, as E110's.

## What it changes

1. **Section 11 item 10 narrows.** *What sets each rail's period steps:* registered now, by interleave, not by period. The NoC rail's
   step is the memory shire's (8-way) interleave, +0.113 W of `R_3`'s +0.220; the off-rail step is the channel's (16-way), +0.328 W, with
   the memory shires' logic moving (the DDR die rail, −0.64 mV); the SRAM rail's steps are at the 1-, 2- and 4-way paths (+0.04 to +0.07 W
   each), at 32 ways (+0.042) and at 256 ways and wider (+0.097), plus a hart's own stream (+0.070). Bits 5–7 inside a channel cost
   nothing that resolves on the board. *A channel's line-to-line changes* cost +0.31 W [0.21, 0.41], registered (R2). *The encoded part:*
   it pays (+0.166 W [0.121, 0.210] beyond the pins at a high raw load, E110's 0.16–0.25 W now measured with the pins' high count held)
   and it moves the DDR die rail on its own (`RE64` −0.77 mV at raw 56), but both registered verdicts are UNRESOLVED by margins of 0.002 W
   and 0.01 mV. **Still open:** splitting the 1.0 pJ of a one between the memory shires' logic, the PHY's pads and the DRAM chips; where
   the 256-bit path sits (a channel's line-to-line path is now measured, not placed); the encoded part's registered verdicts (a replicate
   with more passes would decide both); and E99's account (a refit, desk).
2. **For a power model of real data on this memory** (item 6): a DRAM line's energy depends on its neighbours on three paths, each now
   with a measured size on this card at 600 MHz for lines that differ in all their bits half the time: a channel's stream (+0.31 W), a
   memory shire's (+0.22 W) and paths at 256 ways and wider (+0.25 W), with a hart's own stream (+0.18 W for 504 bits a line). A model
   that prices only the ones and the flips inside each line misses all of them: for these lines they sum to `R_all`, +0.955 W [0.865, 1.045].
3. **E110's line-edge question is answered for a channel, not for its 256-bit path.** E110 could not tell whether its 256-bit path toggles
   at the line's edge (1.15 pJ a bit if it does, 2.38 if not). Something on each channel does pay for line-to-line changes, at about 2 pJ a
   bit if it is a 256-bit path; E110's images never changed between lines, so its prices stand as measured.
4. **For the blog material, on aifoundry3 card 0 at 600 MHz:** reading DRAM costs more when lines that travel the same internal path
   differ from one another. On this card a memory channel's stream costs about 0.3 W more when its consecutive lines differ in all their
   bits half the time, a memory shire's about 0.2 W (half of it on the network), and a core's own stream about 0.2 W, beyond what the ones
   and the flips inside each line cost; together, with the paths wider than 128 lines, about 1 W at full read bandwidth. The memory
   interface's own encoding (read DBI) adds about 0.17 W for 392 more flips a line on its encoded side.

## Files

| file | what it is |
|---|---|
| `passes/p13201` | the smoke, not reduced |
| `passes/p13210`–`p13216` | the passes: `runs.jsonl`, `marks.jsonl`, `telemetry.jsonl.gz`, `configs.json`, `block.json`, `code.sha256`, `gen.sha256`, `text.sha256`, `manifest.txt`, `run.log` |
| `gen/` | `make_e132.py`'s output: `manifest.json`, `srcs/*.bin`, `counts.json`, `gen.sha256` |
| `e132.json` | the reduction, the registered primary arm: dips removed, `auto` slope. **The result** |
| `e132-leak0.2936.json`, `e132-leak0.3803.json` | the two registered sensitivities, dips removed |
| `e132-unfiltered.json` | the same reducer on the passes as they came |
| `dips.json` | every board-meter dip, and where it falls |
| `runs.csv` | one row per run, primary arm: pass, item, launch reading, p_raw, p80, the three rails, off, the DDR die rail, rate, median `took_ms`, gate failures |
| `reduce.sh`, `reduce.txt` | the reduction commands and their printed output |
| `ident/` | `ettelem config` at the start and the end of the card session, and their times |
| `logs/` | the session log, the queue's output (each pass's runner log), the smoke's log, the dry run |

Code: `tools/claims-v3/e132/` (the registration, `34ec50b8`), with E75's `mf/block.sh`, E110's `reduce_e110.py` (its windows) and
`smoke_gate_e110.py`, E99's `dm/dm_enc.py`, E81's `dp/posthoc_dips.py` and the runner `runitems.py`, all unchanged.

## Reproducing it

    # on aifoundry3, in ~/aifoundry, with tools/claims-v3/e132/ and build/e132-gen/ synced in, and the card idle
    bash tools/claims-v3/e132/run_e132.sh setup
    bash tools/claims-v3/e132/run_e132.sh go
    # on any machine with the lab repo and numpy
    python3 tools/claims-v3/e132/make_e132.py <dir> --e110-gen docs/reports/data/2026-11-01-e110-memory-width/gen --check
    bash docs/reports/data/2026-11-02-e132-memory-split/reduce.sh
