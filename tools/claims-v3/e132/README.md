# E132: the memory path's split, by address-bit images and an encoded-quiet twin (Q136)

*Pre-registered Mon 2 Nov 2026 (week 45), about 10:35 PST, on the Intel, by the Q136 workflow's lane `a3-e132-memory-split`. No card was
opened for this file. Frozen at the commit that adds it, before the day's card post names aifoundry3 and before the first launch. Changes
after that go in Amendments, dated, before the data they touch.*

*It answers the kinds page's [section 11, what is still open](https://spacesheep.dev/@yaroslavvb/horace-kinds-of-numbers#11-what-is-still-open),
**item 10, "The memory path"** (the list as it reads at `fbb682f9393b`), critic 10 of Q134's final critic: "images not periodic in the line
index; a registered test that separates the encoded part at the DDR die rail". Open there, after
[E110](../../../docs/reports/data/2026-11-01-e110-memory-width/README.md): what sets each rail's period steps, a 0.16–0.25 W encoded-side
residual, and where the 256-bit path is.*

## The question

E110 found that on aifoundry3 card 0 the raw data pay at two widths, a 64-bit path (0.71 pJ a toggled bit, within a line) and a 256-bit path
(2.38 pJ a bit within a line, or 1.15 pJ if each path also toggles at the line's edge, which its images could not tell apart). It left
three things this run takes up, on the same card, command and binary:

1. **Which interleave sets each rail's period steps** (E110 § 6). E99's period ladder repeats P random lines; going from P to 2P lines
   gives the P-way path its first changes but also raises every finer path's count, so fitted per rail the two best interleaves differ by
   0.4 % (NoC), 2.6 % (SRAM) and 9 % (off) in rms (`tools/claims-v3/e110/desk/e99_ladder_ways.txt`, post hoc). **Address-bit images**
   separate them: each line is one of two complementary lines, chosen by one bit of its line index, so consecutive rungs change one
   interleave's view and hold every other path's count exactly. One image is **not periodic** inside the 8,192-line image at all (a fixed
   shuffle), and one isolates a hart's own in-order stream.
2. **Does a channel's path pay for changes between the lines it carries?** (R2.) The channel rung (the 16-way path, bit 4) is the test
   of E110's line-edge question: with each path's line-to-line edge counted, its prices predict +0.20 W there; within-line only, +0.01.
3. **The encoded part.** E110's die-rail ordering put raw and encoded 64-bit toggles on one count, post hoc (its reading 4); on the board an
   encoded residual of 0.16–0.25 W sat below its ±0.30 W band (C2, C3). Here an **encoded-quiet twin** holds every raw count and the ones
   equal and moves only the encoded toggles: on the DDR die rail (R3) and on the board (R4). A third family (C3, below) moves only the
   pins driven high, at equal toggles, which the board's encoded residual needs removed (R6).

## 1. The design

**Command:** E110's DRAM command, unchanged (`enercat_host --pattern flw_pat --harts 1 --seconds 4 --window 240000000 --operands <op>
--stride 64 --slice-bytes 131072 --region 131072`): 1,024 harts each fetch one 64 B line per load from 128 MB in all. **Binary:** E99's
host on the box, `build/enercat-e99/host/enercat_host` (`f6633f1c…`; `file:` takes 256 B, `lines:` any whole number of 64 B lines up to
512 KB), not rebuilt. The host fills its whole buffer with the image repeated (`main.cpp` `fill[i] = src[i % src.size()]`), so line g of
the buffer holds image line g mod n; a constant offset of the buffer in the address map only rotates the line index, which moves no count
below. **Harness:** E75's `mf/block.sh`, the runner `runitems.py`, `lib.sh` and E110's smoke gate, unchanged (`MF_GEN=build/e132-gen`,
`MF_EXPN=e132`). E132's own files are the images, the session and queue scripts with their deadline, and the reducer.

**Items** (`make_e132.py`; every count re-derived from the bytes by `make_e132.py --check`, with E99's encoder `dm/dm_enc.py` and E110's
`features`). Seven images are E110's bytes and commands, checked against its `gen.sha256`. Counts per 64 B line: `w` ones, `hi` pins driven
high after read DBI, `t_enc`/`t_raw` pin toggles between beats after/before inversion, `rW`/`eW` raw/encoded toggles between consecutive
W-bit pieces inside a line; `k` the bits a hart's in-order stream changes a line; `dN` what a path carrying every N-th line sees between
two reads (`dm_enc.path_distance`):

| family | item | what it is | w | hi | t_enc | r64 | e64 | k | sees changes |
|---|---|---|---:|---:|---:|---:|---:|---:|---|
| A (address bits) | `dm_u4` | every line A = 0x0F × 64 (E99's bytes) | 256 | 256 | 0 | 0 | 0 | 0 | none |
| | `ab_0` … `ab_7` | line g is B = 0xF0 × 64 when bit b of g is set | 256 | 256 | 0 | 0 | 0 | 512/2^b | paths of 2^b ways and finer: d = 256 |
| | `ab_x70` | B when bit 7 XOR bit 0 of g is set | 256 | 256 | 0 | 0 | 0 | 508 | as `ab_7` |
| | `ab_rnd` | A or B by a fixed shuffle, 4,096 each (seed 13201), 8,192 lines | 256 | 256 | 0 | 0 | 0 | 257.8 | every path, d ≈ 239–257 |
| E (encoded part) | `wl_64`, `wl_128` | E110's W rungs: blocks of 0x00 / 0xFF | 256 | 32 | 14, 6 | 448, 192 | 56, 24 | 0 | none |
| | `c3_64`, `c3_128` | blocks of 0x07 / 0xF8 (0xF8 is sent as 0x07 with DMI high) | 256 | 224 | 14, 6 | 448, 192 | 56, 24 | 0 | none |
| | `vl_64`, `vl_128` | E110's V rungs: blocks of 0x0F / 0xF0 | 256 | 256 | 112, 48 | 448, 192 | 448, 192 | 0 | none |
| | `eh_64` | 64-bit blocks of 0x0F / 0x1F (0x1F is sent as 0xE0, DMI high) | 288 | 256 | 112 | **56** | **448** | 0 | none |
| | `el_64` | its twin: lane 0 0x0F / 0x0E, lane 1 0x1F / 0x3F | 288 | 224 | 14 | **56** | **56** | 0 | none |
| | `dm_l08` | lanes constant 0x00 / 0xFF (E99's bytes; W's base) | 256 | 32 | 0 | 0 | 0 | 0 | none |
| | `dm_a44` | beats alternate 0x0F0F / 0xF0F0 (E99's bytes): 496 pin toggles | 256 | 256 | 496 | 0 | 0 | 0 | none |
| anchors | `anchor_pi` (first and last), `dp_zeros` | E75's drift anchor; E81's zeros command | | | | | | | |

*Family A:* A and B are complements, each with 256 ones and 256 pins high and nothing toggling inside a line at any width, so a path that
sees both sees 256 bits change on average between two reads, as a path seeing E99's random lines does. In `ab_b` a path carrying every
2^n-th line sees A and B half and half when n ≤ b and one value when n > b, so **`ab_b` − `ab_{b−1}` changes the 2^b-way path's view
(0 → 256) and holds every finer and coarser path's count exactly** (`make_e132.py --check` prints every `dN`). The memory shire (address
bits 8:6, `core-et/rtl/inc/memshire_defines.vh:21`) is the 8-way path, bit 3 of the line index; a channel (bit 9, E99) the 16-way path,
bit 4; bits 5–7 are inside a channel. Only a hart's own in-order stream also differs between rungs (`k` halves at each), and `ab_x70` −
`ab_7` measures it: every path's view is `ab_7`'s, and the stream changes 504 more bits a line.

*Family E:* `c3` has every toggle count of `w` (raw and encoded, every width) and 192 more pins high. `vl` has `c3`'s raw counts and
moves the encoded data with them (+392 encoded 64-bit toggles at the 64-bit rung, +168 at the 128-bit rung), with 32 more pins high.
`eh_64` and `el_64` have the same ones (288) and the same raw toggles at every width (56 at 64 bits); `eh_64` moves 448 encoded 64-bit
toggles, `el_64` 56, with 32 more pins high. **`eh_64` is `wl_64`'s mirror: raw 56 / encoded 448 against raw 448 / encoded 56.**

**Per pass:** `anchor_pi` first and last, the 22 memory items once each in the runner's shuffled order, two burn-in launches: 24 runs,
about 3.8 min (E110's 24 runs took 226–241 s). **Smoke 13201** (`anchor_pi`, `ab_4`, `ab_rnd`, `eh_64`, `c3_128`: a 256-line `lines:`
image, the 512 KB one and two new one-line images) and E110's smoke gate. **Passes 13210–13216; 13210 is the registered warm-up, reported
and never in the headline,** as in E81, E99 and E110.

## 2. Contrasts (`reduce_e132.py` `build_contrasts`)

- **Rungs, hart stream removed (the registered primary):** `R(x, y)` = (x − y) − (k_x − k_y)/(k_ab_x70 − k_ab_7) · (`ab_x70` − `ab_7`).
  `R_0` = R(`ab_0`, `dm_u4`) (the 1-way paths), `R_b` = R(`ab_b`, `ab_{b−1}`) for b = 1 … 7 (the 2^b-way path), `R_hi` = R(`ab_rnd`,
  `ab_7`) (256 ways and wider), `R_wide` = R(`ab_rnd`, `ab_4`) (32 ways and wider: E99's L8192 − L32), `R_all` = R(`ab_rnd`, `dm_u4`).
  The uncorrected differences are reported as `D_…`. `H` = `ab_x70` − `ab_7`.
- **The encoded part:** `Hp` = ½[(`c3_64` − `wl_64`) + (`c3_128` − `wl_128`)] (192 pins high); the pairs `P56` = `eh_64` − `el_64`,
  `P448` = `vl_64` − `c3_64`, `P192` = `vl_128` − `c3_128`; the **encoded wide-path residuals** `E56` = `P56` − (98/496)·`V16` −
  (32/192)·`Hp`, `E448` = `P448` − (98/496)·`V16` − (32/192)·`Hp`, `E192` = `P192` − (42/496)·`V16` − (32/192)·`Hp`, with `V16` =
  `dm_a44` − `dm_u4` (496 pin toggles: E110's way of removing the pins' share, with the pins' extra high count removed too).
- **Ties:** `S64` = `wl_64` − `dm_l08`, `S128` = `wl_128` − `dm_l08`, `V16`, `V64` = `vl_64` − `dm_u4`, `V128` = `vl_128` − `dm_u4`,
  `U4z` = `dm_u4` − `dp_zeros`. Every item over `dp_zeros` (`<item>z`).

## 3. Frozen predictions (`predictions.json`, `predictions.txt`, written by `make_predictions_e132.py` from committed E110 and E99 files)

| rule | quantity | frozen value | source |
|---|---|---|---|
| R1 | `S64`, `S128`, `V16`, `V64`, `V128`, `U4z` | +0.358, +0.135, +0.481, +0.651, +0.337, +1.624 W | E110 `e110.json` headline |
| R2 | `R_4` on the board | **EDGES, +0.204 W** (128 bits a line on a 256-bit path at 1.151 pJ, 32 on a 64-bit path at 0.627, 8 pin toggles at 0.827); NO-EDGES would read +0.008 | E110's line-edge prices |
| R2 | where `R_4` is paid | off every metered rail | E99: L32 − L16 off +0.162, NoC −0.004, SRAM +0.011 W |
| R3 | DDR die rail | **ENCODED**: `eh_64z` moves, `el_64z` still, `RE64` (= `P56`) moves; `wl_64z` moves (the raw control) | E110 reading 4 (post hoc): the rail orders by raw + encoded 64-bit toggles; `eh_64` 56 + 448 = `wl_64`'s 448 + 56 |
| R4 | `E56`, `E448` | **PAYS**: +0.185 W each (`E192` +0.156) | E110's `E64`, `E128` by its registration's formula (`ew-readme-formula.json`) |
| R5 | per rail, the classes of `R_1` … `R_4`, `R_wide` | E99's steps mapped rung by rung (`predictions.txt`); e.g. SRAM: `R_1`, `R_2` present, `R_wide` present; NoC: `R_2`, `R_3` present; off: `R_1`, `R_4` present | `desk/e99_ladder_ways.txt` (post hoc there) |
| R6 | `RH64`, `RH128` on the DDR die rail | still | E110: `dm_u4` and `dm_l08` both still over zeros (256 against 32 pins high) |
| reported | `Hp`, a pin held high | +0.331 W, 1.47 pJ | E99's `hi_t0` |

## 4. Decision rules (`reduce_e132.py`, `verdicts`)

**Classes.** Board and the off column: *present* at a mean ≥ 0.10 W with the 95 % interval above 0, *negative* at ≤ −0.10 W with it below
0, *absent* when the interval lies inside ±0.10 W, *unresolved* otherwise. The NoC, SRAM and minion rails: the same at 0.03 W (thresholds
sized for each rail, as E99 asked). The encoded residuals (R4): *present* when the interval lies above 0, *absent* inside ±0.10 W. The
DDR die rail (`die_mv.ddr`): *moves* at a mean ≤ −0.30 mV with the interval below 0, *still* inside ±0.30 mV (E110's rule).

| rule | test | reading / verdict |
|---|---|---|
| **R1** session tie | `S64`, `S128`, `V16`, `V64`, `V128`, `U4z` each within ±0.30 W of E110's | PASS if all within; FAIL otherwise (the rest is read as this session's) |
| **R2** a channel's path pays for line-to-line changes | `R_4` on the board | EDGES (present), NO-EDGES (absent), UNRESOLVED. **Predicted EDGES.** PASS if EDGES. Reported: its rails' sum, off, DDR rail, and its price per bit if all on a 256-bit path |
| **R3** the encoded part at the DDR die rail | classes of `wl_64z`, `eh_64z`, `el_64z`, `RE64` | UNRESOLVED if `wl_64z` does not move (the raw control); OTHER if `el_64z` moves; ENCODED if `RE64` moves and `el_64z` is still; RAW if `eh_64z`, `el_64z` and `RE64` are all still; else UNRESOLVED. **Predicted ENCODED.** PASS if ENCODED, FAIL if RAW or OTHER. Reported: `RE128` (= `P192`), every `<item>z` |
| **R4** the encoded part on the board | `E56`, `E448` | PAYS (both present), NONE (both absent), AT-HIGH-RAW-ONLY / AT-LOW-RAW-ONLY (one present, one absent), else UNRESOLVED. **Predicted PAYS.** PASS if PAYS. Reported: `E192`, the pairs, pJ per encoded toggle |
| **R5** which interleave sets each rail's steps | per rail (board, NoC, SRAM, minion, off), the classes of `R_1` … `R_4`, `R_wide` against E99's mapped classes | per rail FAIL if a rung resolved in both disagrees, PASS if at least one resolves in both and none disagrees, else UNRESOLVED; overall FAIL if any rail fails, PASS if none fails and one passes. Reported: every rung on every rail, `R_0`, `R_5` … `R_7`, `R_hi`, `R_all`, `H`, the largest rung per rail |
| **R6** pins held high on the DDR die rail | `RH64`, `RH128` | PASS if both still; FAIL if either moves or rises; else UNRESOLVED. Reported: `Hp`'s board price |

**Fewer than three headline passes: every verdict UNRESOLVED.** **Reported, not scored:** every item over zeros on the board, each rail,
off and the DDR die rail; where each effect is paid (the three rails' sum: *on no metered rail* inside ±0.10 W); the line rate per item;
the warm-up pass; the leakage sensitivities (0.2936 and 0.3803 W/°C) and the unfiltered arm.

**The estimator, gates and arms: E110's, unchanged.** Per kept pass, each item's board power over [t0+1 s, t0+3 s), corrected to the
launch reading with E81's `auto` leakage slope; the three rails raw over [t0+2 s, t0+4 s), never past the run; the DDR die rail over the
board's window; every contrast a within-pass difference; the headline the mean over headline passes with a two-sided t interval on their
scatter. Run gates: one clock, voltage within 3 mV of the pass median, a launch within 0.5 °C of 58 °C after a 59 °C preheat, the window's
median `took_ms` ≤ 60 ms, an ok record, the rails present. A pass is set aside at an `anchor_pi` drift above 0.3 W or more than a third of
its memory runs failing a gate. **Primary arm: the board meter's dip samples removed** (`dp/posthoc_dips.py`, as E99 and E110 registered
it); the unfiltered arm beside it, and any verdict that differs is named.

**Budget and stops:** at most **40 card-minutes** (the brief's), as one detached session (`session_e132.sh`): the opening `ettelem config`,
the smoke, the gate, passes 13210–13216 (`queue_e132.sh`), the closing `ettelem config`. A pass starts only if, at the longest pass so far
(first estimate 240 s), it ends before the session's start + 36 min; a pass in flight is never cut. `build/e132-STOP` stops the queue
before its next pass. No session starts after 15:00 PST; everything ends by 16:00 PST. Expected: seven passes in about 29 card-minutes.
The runs are E110's DRAM loads, 32–36 W on the board with the die at 58–59 °C (E110: every launch read 58.0 °C after a 59 °C preheat);
`runitems.py` stops heating at 78 °C, far from any PMIC limit, and nothing here drives the card toward one.

## 5. Device commands sent

*His rule of Mon 2 Nov 2026 (Q136): every device-management command a run's harness, sampler, host program and helpers send, classified
from the firmware source of the running build, READ or WRITE; the only write allowed in Q136 is the statistics reset, and **E132 sends no
write at all**.* aifoundry3 reports release 1.4.0, BL1 and BL2 0.22.0, PMIC 1.5.0; the source read is et-platform at `836a4ab`, the
version-matched public revision, through Q136(w)'s table (`tools/claims-v3/dmcmd_table.json`). aifoundry3 runs a non-public thermal build
of 0.22.0 (Q136(w) result 1), so each class below is `836a4ab`'s handler, which that build may not share: the residual every aifoundry3
lane carries. Paths are under `device-bootloaders/src/ServiceProcessorBL2/`. The sending code is E110's, unchanged (`lib.sh`, the same
`ettelem` binary, `mf/block.sh`'s one sampler call) plus `session_e132.sh`'s two config reads:

| # | command | sent by | firmware path at `836a4ab` | what it touches | class |
|---|---|---|---|---|---|
| 1 | `DM_CMD_GET_MODULE_STATIC_TDP_LEVEL` | `ettelem config` (the session's start and end) | `services/thermal_pwr_mgmt.c:613` | copies SP RAM | **READ** |
| 2 | `DM_CMD_GET_MODULE_TEMPERATURE_THRESHOLDS` | `ettelem config` | `thermal_pwr_mgmt.c:665` | copies SP RAM | **READ** |
| 3 | `DM_CMD_GET_MODULE_POWER_STATE` | `ettelem config` | `thermal_pwr_mgmt.c:551` | copies SP RAM | **READ** |
| 4 | `DM_CMD_GET_ASIC_FREQUENCIES` | `ettelem config`; `ettelem sample` | `services/perf_mgmt.c:276` → `driver/io_pll.c:932` | PLL register reads | **READ** |
| 5 | `DM_CMD_GET_ASIC_VOLTAGE` | `ettelem config`; `ettelem sample` | `thermal_pwr_mgmt.c:1142` → `driver/pmic_controller.c:1473`, `:254` `i2c_read` | PVT reads and two PMIC voltage-register reads | **READ** — PMIC voltage reads, allowed by his rule of 2 Nov |
| 6 | `DM_CMD_GET_MODULE_POWER` | `ettelem sample`; `lib.sh` `drain_mgmt` (`dev_mngt_service -m DM_CMD_GET_MODULE_POWER`) only after a sampler fails to start twice or ignores SIGTERM for 30 s | `thermal_pwr_mgmt.c:984` | copies SP RAM | **READ** |
| 7 | `DM_CMD_GET_SP_STATS` | `ettelem sample` | `services/performance.c:404` → `thermal_pwr_mgmt.c:2780` | copies SP RAM; resets nothing | **READ** |
| 8 | `DM_CMD_GET_MODULE_CURRENT_TEMPERATURE` | `ettelem sample`; `lib.sh` `die_c` (1 s at each block's start and end) | `thermal_pwr_mgmt.c:732` | PVT reads, cached in SP RAM | **READ** |
| 9 | `DM_CMD_GET_MODULE_VOLTAGE` | `ettelem sample` (10 Hz, the whole pass; the DDR die rail is read from it) | `thermal_pwr_mgmt.c:1010` → `pmic_controller.c:1473` | nine PMIC voltage-register reads | **READ** — PMIC voltage reads, allowed by his rule of 2 Nov |

**Never sent by E132** (each checked in the code that runs): `DM_CMD_SET_STATS_RUN_CONTROL`, the statistics reset (`ettelem` sends it
only with `--reset-ms`; `mf/block.sh:71` calls `start_sampler "$OUT/telemetry.jsonl" $((MAXS + 900))` and nothing else, and no E132 file
names `--reset-ms`); `DM_CMD_GET_MODULE_FIRMWARE_REVISIONS` (it writes the PMIC's firmware-management register; nothing here calls it);
any residency read; any `DM_CMD_SET_*`; no governor, TDP, threshold or clock set; no reset, power cycle, PCIe, driver, firmware or OTA
work. **The host programs** open the ops node only (`workloads/enercat/host/main.cpp:147` and `workloads/sparsity/host/main.cpp:172`,
`createPcieDeviceLayer(true, false)`): their commands go to the master minion's runtime (their own kernel, operand and result buffers, the
launch), none a management command. Helpers that open no device node: `et-who` / `et-holders`, `et-lab-manifest`, `flock`, `timeout`,
`ps`, `who`.

**The preflight checker**, Q136(w)'s `tools/claims-v3/dmcmd_audit.py` as committed in `32e9c109` (sha256 `f29e91ca…`, table `50168632…`),
on `tools/claims-v3/e132/`, `lib.sh`, `mf/block.sh`, `runitems.py`, `text_hash.sh` and E110's `smoke_gate_e110.py`, `reduce_e110.py`,
`make_e110.py`: the nine reads above at 26 send sites, PMIC access on `GET_ASIC_VOLTAGE` and `GET_MODULE_VOLTAGE` only (reads), and one
**conditional** write it cannot rule out from text, `STATS_RESET` at `lib.sh:154` (`start_sampler` forwards `"$@"`). Cleared by reading
the call (above), recorded as a reviewed `--except`; with it and no allow-list the checker returns **GO** (`dmcmd-audit.txt`).

## 6. How to run it (aifoundry3, in `~/aifoundry`)

    # on the Intel: images, then sync the tools and the images to the box
    python3 tools/claims-v3/e132/make_e132.py <gen> --e110-gen docs/reports/data/2026-11-01-e110-memory-width/gen --check
    rsync tools/claims-v3/e132/ aifoundry3:aifoundry/tools/claims-v3/e132/; rsync <gen>/ aifoundry3:aifoundry/build/e132-gen/
    # on the box
    bash tools/claims-v3/e132/run_e132.sh setup     # hashes, the dry run; no card
    bash tools/claims-v3/e132/run_e132.sh go        # the detached session: config, smoke, gate, passes, config (CARD RUN)
    bash tools/claims-v3/e132/run_e132.sh status
    # back on the Intel, with numpy (the primary arm, as E110's reduce.sh)
    python3 tools/claims-v3/dp/posthoc_dips.py <passes>/p1321? --work <work> --out dips.json
    python3 tools/claims-v3/e132/reduce_e132.py <work>/p1321? --gen <gen> --pred tools/claims-v3/e132/predictions.json --out e132.json --csv runs.csv

Data on the box: `build/claims-v3/aifoundry3/e132/p<pass>/`, session log `build/e132/`.

## 7. What E132 does not do, and why

- **The PHY and pads against the DRAM chips**, and the 1.0 pJ of a one that is neither: no meter reaches them. The address-bit rungs
  locate a cost by interleave (memory shire, channel, inside a channel), not by part; R2 says whether a channel's path sees line-to-line
  changes, which the DRAM's 256-bit prefetch path does if it carries the channel's bursts back to back, but so would the PHY's.
- **A refit of E99's account** (critic 10's third item) is desk work and is not registered here.
- **Bits 8 and up, one at a time.** `R_hi` takes everything at 256 ways and wider together.

## 8. Risks, and what each does to the result

- **A hart's stream.** Every rung also halves how often a hart's own stream changes (`k`); `H` measures that and the primary rungs remove
  it linearly. E99's nearest reading, `dp_c2` − `dp_c1` (256 bits a line changing in a hart's stream, and in the 1-way paths with it), is +0.083 W on
  the SRAM rail, so the correction matters most for `R_0`–`R_2`.
- **The independent-draw reading.** `dN` assumes that two reads of one path are independent draws of its lines, as E99's counts do: harts
  start at different places in their slices and drift apart within microseconds. If many harts read in step, a path would see fewer changes
  than `dN`; the rungs' classes do not depend on it, the prices do.
- **The DDR die rail is read in whole millivolts** and acts like a threshold: R3 and R6 score classes only, and an encoded weight about half
  a raw one would put `eh_64` near the threshold (`eh_64` reads 56 + 448x on E110's ordering, against a threshold between 216 and 384 at
  x = 1). A RAW reading therefore bounds the encoded weight; it does not prove it zero.
- **`el_64` carries four byte values** and so no exact no-toggle base; it is used only against `eh_64`, with which it shares every raw count
  and the ones. `eh_64` and `el_64` carry 288 ones, the other items 256.
- **Pins held high** differ by 32 between each encoded pair; `Hp` removes them at its measured price, and on the die rail R6 checks they do
  not move it.
- **Another user, the demo service, the meter's dips, the first pass:** as E110 (block.sh stops on another user's device process or lock on
  this card; an idle login does not block, as in E60's D1; the dip filter; the warm-up pass).

## Files

| file | what it is |
|---|---|
| `make_e132.py` | the images, the commands, every count; `--check` re-derives them from the bytes and checks E110's seven against its `gen.sha256` |
| `make_predictions_e132.py`, `predictions.json`, `predictions.txt` | the frozen predictions, bands and decision constants, from committed E110 and E99 files |
| `reduce_e132.py` | the registered reduction and verdicts |
| `selftest_e132.py`, `selftest.txt` | a pipeline test before any pass: E110's passes relabelled; it must reproduce E110's reducer on the runs both read (0 bad) |
| `session_e132.sh`, `queue_e132.sh`, `run_e132.sh` | the card session, the queue with its deadline, the setup and status stages |
| `dmcmd-audit.txt` | the preflight checker's output on E132's run-time files (GO) |
| `gen.sha256` | the images' hashes as generated on the Intel (the box checks its copy against it) |

## Amendments

*(none yet)*
