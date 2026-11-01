# E110 — the memory path's width ladder (Q133)

*On the kinds page, [section 11, what is still open](https://spacesheep.dev/@yaroslavvb/horace-kinds-of-numbers#11-what-is-still-open),
**item 10, "The memory path"**, as it reads at `1fe8377a18af`: "Open: the 1.3 pJ of a one that is off every metered rail (how much is regulator
loss, the memory shires' logic, the DRAM chips); which unmetered paths carry the half-line bits and the 64-bit toggles, post hoc so far; what sets
the period ladder's steps on each rail. A width ladder registered first would find the raw path's width." This README answers it in part:
§ What it changes, item 1.*

## Results

*Seven passes, `p11010`–`p11016`, Sun 1 Nov 2026 13:58:24–14:27:00 PST on aifoundry3 card 0, 600 MHz, `--harts 1` (1,024 harts), after a smoke
(`p11001`, 13:56:25–13:58:24, gate PASS). **30.8 card-minutes** (13:56:25–14:27:15) of the 40 allowed. Every pass `block.json` `"status":"ok"`,
168 runs, **no run-gate failure**, no pass set aside (anchor drift 0.11–0.19 W). Pre-registered in `52b5fc46` (`tools/claims-v3/e110/`) before the
claim (13:56:14 PST) and the first launch. Reduced with `reduce.sh` (the registered `reduce_e110.py`, unchanged). Pass 11010 is the registered
warm-up, so **the headline is six passes, 11011–11016** (df = 5). Every number below is from `e110.json` `headline` (the registered primary arm:
the board meter's dips removed, E81's `auto` leakage slope, here 0.0159 W/°C) unless it says otherwise. Intervals are 95 % t over the six passes.
One coding error in the frozen reducer was found after the data (D1): it changes no verdict in any arm, and the encoded residuals quoted are the
registration's formula's. An independent verifier then found eight faults in how this was stated; the corrections (C1–C8, desk only: nothing
re-run, no measured number or verdict changed) are marked where they apply and listed in § Corrections after verification.*

**The registered reading: R1, R2, R3, R4 and R6 PASS; R5 FAILS.** On this card the raw data pay at two widths and no others: **64 bits, at
0.71 pJ [0.61, 0.82] a toggled bit,** and **256 bits, the line's two halves, at 2.38 pJ [2.24, 2.51] a bit beyond**, counting the edges
within a line (0.63 and 1.15 pJ if each path also toggles at the line's edge; C4, C7). Toggles at 16, 32 and 128 bits cost nothing that
resolves. Both are on no metered rail, and the 64-bit price is mostly on the decoded (raw) data: the DBI-encoded data's own share is inside the
registered absent band on the board, by 0.007 W under the registration's formula (R3 and R4 both pass within 0.01 W of a class boundary, C3),
and post hoc the DDR die rail says it is not zero (reading 4, C2). The 64-bit cost moves the memory shires' DDR die rail; the half-line cost,
twice as large, does not, which is where R5's frozen class (still, for the 64-bit rung) failed. **A one's off-rail price is 1.38 pJ as the
rails read, 1.25 at E99's rail settling; at most 0.39 pJ of it is the regulators' share (at most 0.25 at that settling), and at least the
remaining 1.0 pJ [0.75, 1.24], which no common settling factor changes, is something else** (C1). This run does not split it between the
memory shires' logic, the PHY's pads and the DRAM chips.

> | what | isolated by | W [95 %] | price | where it is paid |
> |---|---|---:|---:|---|
> | raw toggles between 16-bit beats | `S16` = `dm_a08` − `dm_l08` (496 a line, only the DMI pins move) | +0.004 [−0.058, +0.066] | **none** | |
> | raw toggles between 32-bit pieces | `S32` = `wl_32` − `dm_l08` (480 a line) | −0.037 [−0.128, +0.054] | **none** | |
> | **raw toggles between 64-bit pieces** | `S64` = `wl_64` − `dm_l08` (448 a line) | **+0.358** [0.297, 0.419] | **0.71 pJ** [0.61, 0.82] a toggled bit (C4) | off every metered rail (the three rails +0.013 [−0.006, +0.031]); the DDR die rail −1.01 mV |
> | 128-bit pieces, beyond the 64-bit path | `S128` = `wl_128` − `dm_l08` (r128 384, r64 192) | +0.135 [0.078, 0.191] | **none** (−0.04 pJ) | the 64-bit path alone gives 192 × 0.71 pJ = +0.160 W here |
> | **the half-line bits, beyond everything narrower** | `c256` = `S256` − `S128`/3 (256 a line) | **+0.713** [0.673, 0.754] | **2.38 pJ** [2.24, 2.51] a bit (1.15 if each path also toggles at the line's edge) | off every metered rail (+0.018 [−0.029, +0.065]); the DDR die rail +0.00 mV |
> | the 64-bit rung with the encoded data toggling too | `E64`, the registration's formula (D1) | +0.185 [0.077, 0.293] | | absent by E81's rule, its upper end 0.007 W inside the ±0.30 W band (C3): the 64-bit price is mostly the raw data's; the DDR die rail points to an encoded part (reading 4, C2) |
> | **a one at DRAM**, pins held equal, from 64 to 512 ones a line (C7) | `tie18` = `dm_u8` − `dm_u1` (448 ones) | +1.745 [1.703, 1.788] | **3.32 pJ** [3.24, 3.40] | NoC 1.61, SRAM 0.14, minion 0.18, **off 1.38** pJ as the rails read (about 7 % low: NoC 1.73, off 1.25 [1.10, 1.40] at E99's settling, C1); the DDR die rail −0.01 mV |
> | a one at E75's L2 level, no DRAM, from 64 to 512 ones a line | `l2_ones` = `l2_u8` − `l2_u1` (448 ones) | +2.226 [2.136, 2.317] | **0.81 pJ** [0.78, 0.85] | NoC 0.45, SRAM 0.16, minion 0.07, off 0.13 pJ: **16.3 %** [11.6, 21.1] off the rails (10.5 % [5.4, 15.6] at E99's settling, C1) |
> | the regulators' share of a DRAM one's off-rail price, an upper bound | R6: the rails' 1.94 pJ × f/(1 − f) | | **at most 0.39 pJ** [0.24, 0.53]; at most 0.25 [0.11, 0.39] at E99's settling (C1) | |
> | **what remains of a DRAM one off every metered rail** | R6: 1.38 − 0.39, pass by pass | | **at least 1.00 pJ** [0.75, 1.24], the same at any common rail settling (C1) | |

*Prices are per toggled bit on within-line edges, at the measured 1.17294 × 10⁹ lines/s (no pattern moved it: 1.17292–1.17298 × 10⁹), from the
registered triangular solve (`e110.json` `verdicts.prices_pJ_per_toggled_bit.W_within`): c_w = [S_w/n_w − S_{w/2}/n_{w/2}] / w / line rate, n_w = 31,
15, 7, 3, 1 block edges a line for w = 16 … 256; each price's interval is that solve done pass by pass (`corrections-check.txt` C4). A one's
prices are R6's (`verdicts.R6_one_off_rail`), each column over 448 ones and its level's line rate (L2: 6.0984 × 10⁹ lines/s): marginal prices,
from 64 to 512 ones a line, and the first ones over zeros cost more (C7). The rails read about 7 % low (C1).*

Seven readings:

1. **The raw path's width is 64 bits, and the half-line bits are a second path, 256 bits wide** (R2 PASS: onset at 64, as predicted; R4 PASS:
   RAW256). Toggling the raw data between 16-bit beats or 32-bit words costs nothing that resolves; between 64-bit words it costs 0.71 pJ
   [0.61, 0.82] a bit; 128-bit blocks add nothing beyond what the 64-bit path sees on that rung; and the two 32 B halves cost 2.38 pJ a bit
   beyond everything narrower. In watts on these images: 0.36 W for 448 toggles a line at 64 bits, 0.71 W for 256 at 256 bits. Every rung is off every metered rail
   (`verdicts.where`: the three rails' sum inside ±0.10 W on `S32`, `S64`, `S128`, `S256` and `c256`).
2. **E99's chosen account had the widths and the raw-ness right and the 64-bit price three times too high**: 0.71 pJ a toggled bit against its
   post-hoc 2.22. Every frozen two-path reading over-predicts `S64` (reading A: +1.18 W against +0.36), and the single 256-bit path, which has no
   64-bit term at all, fits the ladder best (`verdicts.models_rms_W`: H256 0.25 W rms, A 0.38, B 0.34, E 0.33). The half-line price, 2.38 pJ a
   bit, sits beside E99's 2.53. So E99's account carried part of something else in its r64 term on random lines; it was not refitted here.
3. **The 64-bit price is mostly on the decoded data** (R3 PASS: RAW). The V ladder, whose encoded data toggle exactly as its raw data do,
   costs at 64 bits what the W ladder does plus its pins: `E64` = +0.185 W [0.077, 0.293] by the registration's formula (+0.107 [−0.005, +0.220]
   by the frozen code, D1), absent by E81's rule in both, though by the registration's formula its upper end is only 0.007 W inside the ±0.30 W
   band (C3). Its interval excludes zero, and so do `E128`'s (+0.156 [0.110, 0.203]) and `E256`'s (+0.246 [0.168, 0.325]). All three shrink at
   the registered leakage sensitivities (`E64` +0.12 and +0.10 W, intervals over ±0.30), so on the board alone a smaller encoded-side cost, up to
   about half the raw one, is not separated from the leakage footing; but the DDR die rail, which the leakage correction does not touch, points
   the same way (reading 4, post hoc, C2). So the encoded side carries a smaller share of the 64-bit cost, not none. *Where the decoder sits
   (C6):* the open firmware writes `DFIMISC` = 0, `phy_dbi_mode = 0` among its fields, and turns read DBI on in the controller
   (`etsoc-hal/src/memshire_ddr_init_functions.c:4762-4765`; `DBICTL` `rd_dbi_en = 1` at `:4522`), and the controller's register description
   in the same repository reads "0 - DDRC implements DBI functionality. 1 - PHY implements DBI functionality"
   (`etsoc-hal/include/etsoc_hal/inc/DWC_ddr_umctl2.html:11740-11743`, et-platform at `836a4ab60`, read Sun 1 Nov 2026). So the controller,
   not the PHY, decodes read DBI, if the card runs that source as written: its own controller registers are not read (E99). The controller
   takes four beats, 64 bits, a 933 MHz clock (`DfiFreqRatio_p0 = 1`, `:768`, E99's source): a raw 64-bit path after the decoder fits. That
   is a reading, not measured.
4. **The 64-bit path moves the memory shires' DDR die rail; the half-line path does not** (R5 FAILS, on this). The DDR die rail (`die_mv.ddr`)
   dropped one millivolt step on `S64` (−1.01 [−1.03, −0.99]), as on `V64` (−0.99), the period step `D` (−0.89) and DRAM traffic itself (`cal`,
   DRAM zeros over L2 zeros, −3.36), and not on `S256` (−0.02), `Sc1` (−0.01), the pins' toggles `V16` (+0.01) or a one, `tie18` (−0.01). The
   frozen class for `S64` was *still*, from a desk reading of E99 that tied the rail to encoded toggles alone; `S64`'s encoded data move only in
   their DMI bits, so that reading's encoded-only claim is refuted, not its encoded part: decoded 64-bit toggles move the rail, and encoded ones
   do too (*post hoc, labelled*, C2). `V128` moves it, −0.59 mV [−0.94, −0.24], where `S128` reads still, −0.08 [−0.18, +0.01], at the same 192
   raw 64-bit toggles a line: `V128` adds 168 encoded 64-bit toggles, and pin toggles alone do not move the rail (`V16`, 496 of them, +0.01).
   The die rail's `E128` by the registration's formula is −0.51 mV [−0.87, −0.15]. Over the six W and V rungs at 64–256 bits the rail's class
   orders exactly by raw plus encoded 64-bit toggles a line: `V64` 896, `S64` 504 and `V128` 384 move; `S128` 216, `V256` 128 and `S256` 72
   stay still. Any weight on an encoded toggle above 0 and below 48 times a raw one gives that order; raw toggles alone tie `V128` with `S128`
   (`corrections-check.txt` C2). The die rail is a second instrument, read raw, and the board's leakage correction does not touch it.
   *Post hoc, labelled:* the rail reads in whole millivolts, and it responds
   monotonically to the rail's current; `S256` costs twice what `S64` does and reads still, so it draws less on the memory shires' logic than `S64`
   does: at most 0.42 W (`S64`'s upper end), leaving at least 0.28 W (`S256`'s lower end, 0.70, less 0.42), more than a third, outside it. The DRAM's own
   256-bit prefetch path (16n prefetch on a ×16 channel, one BL16 burst per 256 bits, raw because the DRAM inverts at its output) is the candidate.
   That is a reading, not measured. The registered bound on each *still* contrast's share in the logic (≤ 0.07 W) is not used: it assumes a linear
   reading, and `S128`, the same path at 0.14 W, read −0.08 mV where `S64` at 0.36 W read −1.01 (D2).
5. **A one's 1.3 pJ: at most about 0.4 pJ is the regulators' share (0.25 at E99's rail settling), and at least 1.0 pJ is more** (R6 PASS).
   These are marginal prices, from 64 to 512 ones a line with the high pins held equal at DRAM; the first ones over zeros cost more (`dm_u1`
   +0.555 W, `l2_u1` +0.830 W over their zeros; C7). At DRAM a one costs 3.32 pJ at the board [3.24, 3.40], 1.61 on the NoC rail, 0.14 on SRAM,
   0.18 on the minion rail and **1.38 off them** (E99: 3.24, 1.60, 0.16, 0.17, 1.32). From the L2, with no DRAM and no pins, a one costs 0.81 pJ,
   and 16.3 % of a step there is off the rails: an upper bound on the three regulators' own loss. At that fraction the 1.94 pJ a DRAM one draws
   on the rails costs at most 0.39 pJ [0.24, 0.53] in their regulators, and **1.00 pJ [0.75, 1.24] remains** off every metered rail (0.93 and
   0.91 pJ at the sensitivities, intervals above 0). **E99's caveat holds here too (C1):** a rail is the PMIC's running average, and over
   [t0+2 s, t0+4 s), the window E110 reads, it holds about 93.5 % of a settled step, so these rail prices are about 7 % low (E99, § Where it is
   paid). Divided by 0.935, a DRAM one is 1.73 pJ on the NoC rail and 1.25 pJ [1.10, 1.40] off the rails, the L2's fraction off the rails is
   10.5 % [5.4, 15.6], and the regulators' share is at most 0.25 pJ [0.11, 0.39]. The remainder does not move: X is the DRAM board price less
   the DRAM rails times the L2's board-to-rails ratio, so one factor on every rail cancels in it (`corrections-check.txt` C1). Since the share
   is an upper bound, X is a lower bound on what is not regulator loss. *Post hoc, labelled:* `tie18` reads still on the DDR die rail, so a one
   draws less on the memory shires' logic than `S64`'s toggles do: under 0.42 W, 0.80 pJ a one. So at point values at least about 0.2 pJ of the 1.0 pJ
   is the PHY's pads (not the pins' DC: their high count is held equal) or the DRAM chips, a bound too weak to resolve; this run does not split the
   1.0 pJ further.
6. **The period step lives in three places.** `D` (8,192 distinct lines over 2) is +0.733 W [0.655, 0.811]: NoC +0.130, SRAM +0.281, minion
   +0.038, off +0.284, and it moves the DDR die rail (−0.89 mV). So 56 % is on the NoC and SRAM rails as they read (E99, in the same window:
   58 %; about 60 % at E99's settling, C1), 5 % on the minion rail, and the part off the rails moves the memory shires' logic. Which interleave sets each rail's steps is not tested: E99's per-rail ladder cannot separate interleaves (registration § 6,
   `desk/e99_ladder_ways.txt`, post hoc).
7. **The session is E99's** (R1 PASS, all six): `S16` +0.004 (E99's `t_raw` −0.026), `Sc1` +0.791 (`half` +0.850), `V16` +0.481 (`t_both` +0.475),
   `tie18` +1.745 (+1.727), `D` +0.733 (+0.755), random bits over zeros +3.542 (+3.466) W. Where the ones sit in the line does not matter either:
   `phase` (`dp_c1` − `wl_256`, the ones in the first 32 B against the second) is +0.032 W [−0.038, +0.102], absent.

### Scoring

| rule | reading | registered | verdict |
|---|---|---|---|
| **R1** session tie | `S16` +0.004, `Sc1` +0.791, `V16` +0.481, `tie18` +1.745, `D` +0.733, `bern` +3.542 W | within ±0.30 (±0.35, ±0.40) of E99's −0.026, 0.850, 0.475, 1.727, 0.755, 3.466 | **PASS**, all six |
| **R2** the raw path's width | `S32` absent, `S64` present (+0.358), `S128` absent (+0.135), `S256` present | onset 64 (reading A) | **PASS**: onset 64. Readings with this onset: A, E, H64; their sizes miss (reading 2) |
| **R3** raw or encoded at 64 bits | `S64` present; `E64` +0.107 [−0.005, +0.220] (frozen code), +0.185 [0.077, 0.293] (the registration's formula, D1), absent in both; by the formula its upper end is 0.007 W inside the band, past which R3 reads UNRESOLVED (C3) | RAW | **PASS**: RAW (UNRESOLVED at both leakage sensitivities) |
| **R4** the half-line bits | `c256` +0.713 present; `E256` +0.235 (+0.246, D1) unresolved; by the formula its mean is 0.004 W under the 0.25 W presence line, at which R4 reads ENCODED256, a FAIL (C3); `phase` +0.032 absent | RAW256 | **PASS**: RAW256 |
| **R5** the DDR die rail | `V64` moves, **`S64` moves**, `S256` still, `Sc1` still, `tie18` still, `D` moves, `cal` moves | `S64` still, the rest as read | **FAIL**: `S64` moves (reading 4). `k_ddr` ≥ 0.81 mV/W [0.72, 0.90]; its bounds not used (D2) |
| **R6** a one off the rails | X = 1.00 pJ [0.75, 1.24]; f = 0.163 [0.116, 0.211]; regulators at most 0.39 pJ [0.24, 0.53] (at E99's rail settling f 0.105, at most 0.25 pJ; X unchanged, C1) | X's interval above 0 (predicted 0.99, f 0.16, 0.37) | **PASS** |
| *reported, not scored* the L2 one (`predictions.json` `prediction.l2`; no rule uses it) | `l2_ones` +2.226 W [2.136, 2.317]; 0.815 pJ [0.782, 0.848] a one | 3.28 W; 1.20 pJ | **missed**: the measurement is 32 % below it, and the frozen value is outside its interval (C5) |

*From `e110.json` `verdicts`; the registration's formula for `E_w` from `ew-readme-formula.txt` (D1); the margins and the L2 line from
`corrections-check.txt` C3 and C5. The registration's text does not derive the frozen L2 number. Post hoc, a price taken over zeros runs high
here, because the first ones cost more: `l2_u1` alone is +0.830 W over L2 zeros, 2.13 pJ a one, and E75's L2 rung of 256 ones over its zeros
gives 1.27 pJ a one, 3.46 W for 448 (C5).*

### The leakage footing and the unfiltered arm

| contrast | primary: `auto` (0.0159 W/°C), dips removed | 0.2936 W/°C | 0.3803 W/°C | unfiltered, `auto` |
|---|---:|---:|---:|---:|
| `S32` | −0.037 [−0.128, +0.054] absent | +0.028 [−0.185, +0.241] absent | +0.048 [−0.244, +0.340] unres. | −0.037 [−0.126, +0.053] absent |
| `S64` | +0.358 [+0.297, +0.419] | +0.374 [+0.193, +0.556] | +0.380 [+0.125, +0.634] | +0.324 [+0.190, +0.457] |
| `S128` | +0.135 [+0.078, +0.191] absent | +0.183 [+0.024, +0.341] unres. | +0.198 [−0.027, +0.422] unres. | +0.135 [+0.079, +0.191] absent |
| `S256` | +0.758 [+0.702, +0.814] | +0.825 [+0.689, +0.962] | +0.846 [+0.654, +1.039] | +0.759 [+0.703, +0.814] |
| `c256` | +0.713 [+0.673, +0.754] | +0.765 [+0.650, +0.879] | +0.780 [+0.622, +0.939] | +0.714 [+0.674, +0.754] |
| `E64`, the registration's formula | +0.185 [+0.077, +0.293] absent | +0.120 [−0.142, +0.381] unres. | +0.099 [−0.229, +0.428] unres. | +0.157 [+0.060, +0.253] absent |
| `phase` | +0.032 [−0.038, +0.102] absent | +0.044 [−0.084, +0.172] absent | +0.047 [−0.138, +0.232] absent | +0.032 [−0.037, +0.102] absent |
| R6's X, pJ | 1.00 [0.75, 1.24] | 0.93 [0.63, 1.24] | 0.91 [0.52, 1.31] | 1.00 [0.75, 1.24] |
| verdicts that move | | R3 UNRESOLVED | R2, R3 UNRESOLVED | none |

*From `e110.json`, `e110-leak0.2936.json`, `e110-leak0.3803.json`, `e110-unfiltered.json` and `ew-readme-formula.txt`.* No verdict flips
between PASS and FAIL. At the higher slopes the corrections themselves add scatter, so intervals widen and R2 (through `S32`) and R3 (through
`E64`) go unresolved. The windows warm 0.0–1.0 °C over their launch reading (`runs.csv`); every launch read 58.0 °C after a 59 °C preheat. Dips:
109 samples in seven passes, 7 inside a run's window (`dips.json`).

### Every item

| item | w | hi | t_enc | r64 | half | e64 | board W over its level's zeros [95 %] | NoC | SRAM | minion | off | DDR die rail, mV |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| `dm_l08` | 256 | 32 | 0 | 0 | 0 | 0 | **+1.281** [+1.178, +1.384] | +0.492 | +0.155 | +0.022 | +0.612 | −0.06 |
| `dm_a08` | 256 | 32 | 62 | 0 | 0 | 0 | **+1.285** [+1.172, +1.399] | +0.513 | +0.174 | −0.001 | +0.600 | −0.04 |
| `wl_32` | 256 | 32 | 30 | 0 | 0 | 0 | **+1.244** [+1.086, +1.403] | +0.504 | +0.159 | +0.028 | +0.554 | −0.09 |
| `wl_64` | 256 | 32 | 14 | 448 | 0 | 56 | **+1.639** [+1.541, +1.738] | +0.506 | +0.163 | +0.012 | +0.958 | −1.07 |
| `wl_128` | 256 | 32 | 6 | 192 | 0 | 24 | **+1.416** [+1.302, +1.529] | +0.514 | +0.177 | +0.003 | +0.723 | −0.14 |
| `wl_256` | 256 | 32 | 2 | 64 | 256 | 8 | **+2.040** [+1.948, +2.131] | +0.496 | +0.156 | +0.044 | +1.344 | −0.08 |
| `dp_c1` | 256 | 32 | 2 | 64 | 256 | 8 | **+2.072** [+1.967, +2.177] | +0.483 | +0.138 | +0.124 | +1.326 | −0.07 |
| `dm_u4` | 256 | 256 | 0 | 0 | 0 | 0 | **+1.624** [+1.530, +1.718] | +0.505 | +0.169 | +0.043 | +0.907 | −0.08 |
| `dm_a44` | 256 | 256 | 496 | 0 | 0 | 0 | **+2.105** [+1.982, +2.228] | +0.504 | +0.163 | +0.023 | +1.414 | −0.08 |
| `vl_32` | 256 | 256 | 240 | 0 | 0 | 0 | **+1.855** [+1.735, +1.976] | +0.490 | +0.152 | +0.063 | +1.150 | −0.09 |
| `vl_64` | 256 | 256 | 112 | 448 | 0 | 448 | **+2.275** [+2.095, +2.455] | +0.497 | +0.156 | +0.066 | +1.555 | −1.07 |
| `vl_128` | 256 | 256 | 48 | 192 | 0 | 192 | **+1.961** [+1.877, +2.045] | +0.504 | +0.164 | +0.040 | +1.253 | −0.67 |
| `vl_256` | 256 | 256 | 16 | 64 | 256 | 64 | **+2.644** [+2.521, +2.766] | +0.509 | +0.170 | +0.049 | +1.916 | −0.08 |
| `dm_u1` | 64 | 64 | 0 | 0 | 0 | 0 | **+0.555** [+0.448, +0.662] | +0.132 | +0.123 | −0.013 | +0.313 | −0.07 |
| `dm_u8` | 512 | 64 | 0 | 0 | 0 | 0 | **+2.300** [+2.179, +2.421] | +0.980 | +0.198 | +0.082 | +1.040 | −0.08 |
| `dm_L2` | 256 | 211 | 258 | 220 | 128 | 241 | **+2.831** [+2.676, +2.986] | +0.514 | +0.236 | +0.077 | +2.004 | −1.07 |
| `dm_L8192` | 256 | 211 | 258 | 225 | 128 | 235 | **+3.564** [+3.459, +3.668] | +0.644 | +0.517 | +0.115 | +2.287 | −1.96 |
| `dp_bern` | | | | | | | **+3.542** [+3.410, +3.673] | +0.654 | +0.519 | +0.115 | +2.253 | −1.94 |
| `l2_u1` | 64 | 64 | 0 | 0 | 0 | 0 | **+0.830** [+0.764, +0.897] | +0.145 | +0.450 | +0.075 | +0.161 | −0.32 |
| `l2_u8` | 512 | 64 | 0 | 0 | 0 | 0 | **+3.057** [+2.949, +3.165] | +1.379 | +0.885 | +0.266 | +0.527 | −0.38 |

*Over `dp_zeros` (32.21 W absolute) at DRAM and over `l2_zeros` (29.02 W) at L2, from `e110.json` `headline.over_zeros`; counts per line from
`gen/counts.json`. The rails are raw over [t0+2 s, t0+4 s), which holds about 93.5 % of a settled step, so every rail figure here reads about
7 % low, as E99's do (C1); "off" is the board less the three rails; the DDR die rail over the board's window.
The L2 items' DDR die-rail readings are noisy (intervals about ±0.45 mV).*

## What ran, and what was registered

| | registered (`tools/claims-v3/e110/`, `52b5fc46`) | happened |
|---|---|---|
| command | E75's and E99's DRAM command unchanged; E75's L2 command for the on-chip arm | the same; the dry run printed 22 `enercat_host` lines with the frozen arguments (`logs/e110-dry.log`) |
| binary | E99's host on the box, not rebuilt | `build/enercat-e99/host/enercat_host` `f6633f1c…`, `.text` `eacec93b…`, kernel code `a5743c3c…`: E99's (its `logs/e99-build-hashes.txt`) |
| images | 9 of E99's bytes, 10 new, and 3 commands with no image (`dp_zeros`, `dp_bern`, `l2_zeros`); `make_e110.py --check` | all 19 images checked on the Intel (`gen/counts.json`) and by hash on the box before the first launch; every pass's `gen.sha256` matches `gen/` |
| harness | E75's `mf/block.sh` and the runner, unchanged | `lib.sh`, `runitems.py`, `mf/block.sh`, `queue_mf.sh`, `text_hash.sh` hashed identical on the box and the Intel |
| session | one detached `session_e110.sh`: config, smoke 11001, gate, passes 11010–11016 under a deadline of start + 36 min, config | config 13:56:25; smoke 13:56:25–13:58:24, gate PASS; passes 13:58:24–14:27:00, 226–241 s each, all seven run; config 14:27:15 |
| budget | at most 40 card-minutes; no session after 18:00 PST | **30.8 card-minutes**; the deadline never acted |
| claim | one post in `#community-lab` after the registration, edited at the release | posted 13:56:14 PST, message `1566571599090552833`; released 14:27 PST by editing the same post (read back: "… until ~15:00 PST doc — released") |
| card state | nothing set; `ettelem config` read only, under the lock, `timeout 10`, at both ends | `tdp_w` 0, `temp_threshold_c` 65, 600 MHz, 523 mV, `max_power` at 13:56:25 and at 14:27:15 (`ident/`); nothing written; `et-who` before and after: no process holds a device node or card lock |

## Departures, dated

- **D1 (Sun 1 Nov 2026, after the registered reduction) — a coding error in the frozen reducer.** The registration defines the encoded
  wide-path residual as `E_w` = (`vl_w` − `dm_u4`) − (`wl_w` − `dm_l08`) − (n_w/31)·[(`dm_a44` − `dm_u4`) − (`dm_a08` − `dm_l08`)] (its README §§ 3–4;
  the frozen predictions use it), and `reduce_e110.py`'s contrast holds only `−k·dm_a44 + k·dm_a08` for the last term, dropping `+k·dm_u4 − k·dm_l08`.
  So the frozen code's `E_w` is lower by (n_w/31)(`dm_u4` − `dm_l08`), 0.08 W at 64 bits. The selftest checked five contrasts and the minion rail,
  not `E_w`. `tools/claims-v3/e110/amend_e110.py` (labelled, after the data) recomputes `E_w` by the registration's formula from the reducer's own
  per-pass items in every arm (`ew-readme-formula.txt`, `.json`): **no class used by a verdict changes, and R3 and R4 read the same in all four arms.**
  Under the registration's formula both pass by a hair (C3; `corrections-check.txt` C3): in the primary arm `E64`'s upper end, +0.293 W, is
  0.007 W inside the ±0.30 W absent band (past it R3 would read UNRESOLVED, as it does at both sensitivities), and `E256`'s mean, +0.246 W, is
  0.004 W under the 0.25 W presence threshold (at it, with its interval above zero, R4 would read ENCODED256 and fail). The frozen code's
  margins are 0.080 and 0.015 W, the unfiltered arm's 0.047 and 0.007 W by the formula.
  The README quotes the registration's formula's values, with the frozen code's beside them. No registered file changed.
- **D2 (same day, a reading) — R5's bound.** The registered upper bound on a *still* contrast's share in the memory shires' logic divides its
  interval's end by `k_ddr`, which assumes the die rail reads linearly. This run contradicts that: `S128` (0.14 W on the 64-bit path) read −0.08 mV
  and `S64` (0.36 W, the same path) −1.01. The bounds `e110.json` prints (`logic_share_at_most_W`, 0.06–0.07 W) are not used; reading 4 and 5's
  monotonic comparison, labelled post hoc, replaces them. R5's scored verdict, which uses classes only, stands.
- **D3 (inherited, as E60–E99) — two device processes outside `timeout 10`**: `lib.sh`'s `die_c` in `block_begin`/`block_end` (`ettelem sample
  --seconds 1` under `timeout 20`) and the telemetry sampler for the whole pass. Every enercat and sparsity launch ran under `timeout 10`.
- **Not departures, for the record.** The registration's commit came after the previous lane's release (13:14:48), with the card idle; no pass was
  read while the queue ran (the lane's waits read the queue's log and the session log only). The reducer ran twice on the same passes: once with
  its filtered copies in scratch, whose absolute path went into `e110.json`'s `dirs`, then with `WORK=build/e110-dipwork` as E99's `reduce.sh`
  does; the numbers are identical and the committed files are the second run's.

## What it changes

1. **Section 11 item 10 narrows.** *Which unmetered paths carry the half-line bits and the 64-bit toggles:* registered now, not post hoc. The
   64-bit toggles are a 64-bit path, paid mostly on the raw data, at 0.71 pJ [0.61, 0.82] a toggled bit, that moves the memory shires' DDR die
   rail (the controller after its DBI decoder fits: the open firmware sets the controller, not the PHY, to decode, C6); the half-line bits are a
   raw 256-bit path at 2.38 pJ a bit that does not, more than a third of it outside the memory shires' logic (post hoc; the DRAM's 256-bit
   prefetch is the candidate). Nothing pays at 16, 32 or 128 bits. *The raw path's width:* found, 64 and 256. *The 1.3 pJ of a one:* at most
   0.39 pJ is the regulators' share, an upper bound from an on-chip load, and at most 0.25 pJ at E99's 93.5 % rail settling (C1); at least
   1.0 pJ [0.75, 1.24] remains whatever the settling, and post hoc under 0.8 pJ of it can be the memory shires' logic. **Still open:** splitting
   that 1.0 pJ between the memory shires' logic, the PHY's pads and the DRAM chips; where the 256-bit path is (measured as not mostly in the
   memory shires' logic, not located); a small encoded-side cost at 64–256 bits (0.16–0.25 W: below the ±0.30 W band on the board and not
   separated there from the leakage footing, and the DDR die rail points the same way, post hoc, C2); and what sets each rail's period steps,
   which needs images that are not periodic in the line index (registration § 6).
2. **E99's post-hoc account** is confirmed in its widths and its raw-ness and corrected in one price: a raw 64-bit toggle costs 0.71 pJ, not
   2.22. Its fit to random lines therefore needs about 0.3 W from another term; it was not refitted.
3. **For a power model of real data on this memory** (item 6): the memory path's toggle terms, measured directly at last: 0.71 pJ [0.61, 0.82]
   per raw bit toggled between 64-bit words and 2.38 pJ [2.24, 2.51] per bit differing between a line's halves, on within-line edges (0.63 and
   1.15 pJ if each path's line edge counts too); a one at 3.32 pJ from DRAM and 0.81 pJ from the L2, marginal from 64 to 512 ones a line with the
   high pins held equal at DRAM (the first ones over zeros cost more; C7). Each is one card, 600 MHz, one session.
4. **E75's "L3" level read DRAM** (registration § 1, desk, post hoc): its DDR die rail, rails and board power match the DRAM level's item for
   item. Its L3 prices are DRAM prices; the records should say so where they cite them, among them `docs/findings/05-claims.md`'s memory-path
   row, which quotes E75's L3 bound (< 0.37 pJ a changed bit) as the L3's. [E101](../2026-11-01-e101-real-matmul/README.md) (Q132), which item 10
   cites for making the memory path a term, priced the path with E75's changed-bit prices (its README lines 58 and 224), but the ones it froze
   are the L2's 0.274 pJ and the L1's 0.0492 pJ (`tools/claims-v3/kinds/E101.md` line 67) and, for its DRAM arm `mmp64`, E75's DRAM chord
   (line 102). None is an L3 price, so this finding changes none of E101's frozen numbers (C8).
5. **For the blog material, on aifoundry3 card 0 at 600 MHz:** reading a 64-byte line from DRAM, the bits flip on two internal paths that you can
   measure by their width: a 64-bit one at 0.7 pJ a flipped bit and a 256-bit one at 2.4 pJ, counting flips inside a line (0.63 and 1.15 pJ if
   each path also flips between lines), while flips between 16- and 32-bit words cost nothing; and each extra stored one, from 64 to 512 in a
   line, costs 3.3 pJ to read, about half of it on the on-chip network and at least about 1 pJ of it outside every rail the card meters, beyond
   anything its regulators can lose (C1, C7).

## Corrections after verification (Sun 1 Nov 2026)

An independent verifier checked E110 after the data commit (`20d65965`). It re-ran `reduce.sh` on the committed passes and got `e110.json`,
both leakage arms, the unfiltered arm and `dips.json` back exactly, apart from the `dirs` paths. It re-derived every contrast, price, die-rail
contrast and R6 number from `runs.csv` with its own code. It found these sound: the registration before the claim and the first launch, the
registered files unchanged since, the box's raw data byte-identical to the committed copies, E99's binary, and the card conduct (nothing set,
the lock and timeouts held, one claim, released by an edit). Verdict: holds with fixes. It found eight minor faults, all in how E110 was
stated. Each is corrected above, desk only: no card was touched, nothing was re-run, and no registered file, reduction, measured number or
scored verdict changed (R1, R2, R3, R4 and R6 PASS; R5 FAILS). Numbers were added: the prices' own intervals, the rail figures at E99's
settling beside the readings, the class margins, the frozen L2 line and the die-rail observation. Every new number is printed by [`corrections-check.py`](corrections-check.py)
into [`corrections-check.txt`](corrections-check.txt) (standard library, post hoc, deciding nothing), under the fault's number.

| # | what was wrong | what changed |
|---|---|---|
| C1 | **E99's rail-settling caveat was left out.** A rail is the PMIC's running average; over [t0+2 s, t0+4 s), the window E110 reads, it holds about 93.5 % of a settled step, and E99 called its rail prices about 7 % low (its § Where it is paid). So a DRAM one's off-rail price and the regulators' share were high, and the share, an upper bound, was stated as a value ("about 0.39 pJ of it is the regulators' share") | The lead, the table, reading 5, the R6 row, the note under Every item and What it changes 1 and 5 give both readings: a DRAM one's off-rail price 1.38 pJ as read, 1.25 [1.10, 1.40] at E99's settling; the L2's off-rail fraction 16.3 % and 10.5 % [5.4, 15.6]; the regulators' share at most 0.39 pJ, and at most 0.25 [0.11, 0.39] at that settling. X, 1.00 pJ [0.75, 1.24], does not move, because one factor on every rail cancels in it, and it is a lower bound on what is not regulator loss. Reading 6 adds that `D`'s share on the NoC and SRAM rails is about 60 % at that settling (56 % as read, like E99's 58 %) |
| C2 | **The evidence for an encoded-side cost was understated.** Reading 4 called the desk reading refuted and left out `V128`'s die-rail reading; the lead and reading 3 put the 64-bit price on the decoded data with no hedge. `V128` moves the DDR die rail (−0.59 mV [−0.94, −0.24]) where `S128` reads still (−0.08 [−0.18, +0.01]) at the same 192 raw 64-bit toggles a line, and over the six rungs the rail orders exactly by raw plus encoded 64-bit toggles; the board's `E64`, `E128` and `E256` intervals sit above zero in the primary arm too | Reading 4: the desk reading's encoded-only claim is refuted, not its encoded part, with `V128`, the ordering and the die rail's `E128` (−0.51 mV [−0.87, −0.15]) as a labelled post-hoc observation. The lead, reading 3 and What it changes 1 say "mostly on the decoded data", and the encoded-side residual is below the ±0.30 W band on the board, with the die rail, which the leakage correction does not touch, pointing the same way |
| C3 | **R3's and R4's PASS sit just inside their class boundaries under the registration's formula**, and the text said only that no verdict changes | D1, the lead, reading 3, the table and the R3 and R4 rows give the margins: `E64`'s upper end, +0.293 W, is 0.007 W inside the ±0.30 W absent band (past it R3 would read UNRESOLVED), and `E256`'s mean, +0.246 W, is 0.004 W under the 0.25 W presence threshold (at it R4 would read ENCODED256 and fail); by the frozen code 0.080 and 0.015 W, in the unfiltered arm 0.047 and 0.007 W |
| C4 | **The 64-bit price had no interval of its own.** This README gave none, and the table cell handed on gave "0.57–0.80", `S64`'s interval scaled, not that of the estimator that gives the price, [`S64`/7 − `S32`/15]/64/line rate | The registered solve done pass by pass: 0.715 [0.611, 0.818] pJ, quoted as 0.71 [0.61, 0.82] in the lead, the table, reading 1 and What it changes 1 and 3. The half-line price's 2.38 [2.24, 2.51] is the same estimator pass by pass |
| C5 | **A frozen prediction was never reported**: `predictions.json` `prediction.l2`, the L2 one at 3.28 W and 1.20 pJ, which no rule uses | A "reported, not scored" row in Scoring: measured 2.226 W [2.136, 2.317] and 0.815 pJ [0.782, 0.848], missed, the measurement 32 % below it. The note under the table says the registration's text does not derive the number, and that a price over zeros runs high here (`l2_u1`, 64 ones, 2.13 pJ a one over L2 zeros; E75's L2 rung of 256 ones over zeros 1.27 pJ, 3.46 W for 448), post hoc |
| C6 | **Reading 3 rested on a source quoted from memory**: that `phy_dbi_mode = 0` puts DBI in the controller | Reading 3 cites what was read: the open firmware writes `DFIMISC` = 0 (`phy_dbi_mode = 0`) and `DBICTL` `rd_dbi_en = 1` (`etsoc-hal/src/memshire_ddr_init_functions.c:4762-4765`, `:4522`), and the controller's register description in the same repository reads "0 - DDRC implements DBI functionality" (`etsoc-hal/include/etsoc_hal/inc/DWC_ddr_umctl2.html:11740-11743`, et-platform `836a4ab60`). The card's own controller registers remain unread, as E99 says |
| C7 | **The blog lines left out their conditions.** The 2.4 pJ counts edges within a line only: 1.15 pJ, and 0.63 pJ for the 64-bit path, if each path also toggles at the line's edge. A one's 3.3 and 0.8 pJ are marginal prices from 64 to 512 ones a line, with the high pins held equal at DRAM, and the first ones over zeros cost more (`dm_u1` +0.555 W, `l2_u1` +0.830 W over their zeros) | The lead, the table and its note, reading 5 and What it changes 3 and 5 carry the conditions, and so do the blog lines handed on to the integration lanes |
| C8 | **The finding that E75's "L3" level read DRAM did not name E101**, which used E75's prices and which item 10 cites | What it changes 4 names E101: the prices it froze are E75's L2 and L1 changed-bit prices and its DRAM chord, none an L3 price, so the finding changes none of E101's frozen numbers. It also names the claims record's row that quotes E75's L3 bound as the L3's |

## Files

| file | what it is |
|---|---|
| `passes/p11001` | the smoke, not reduced |
| `passes/p11010`–`p11016` | the passes: `runs.jsonl`, `marks.jsonl`, `telemetry.jsonl.gz`, `configs.json`, `block.json`, `code.sha256`, `gen.sha256`, `text.sha256`, `manifest.txt`, `run.log` |
| `gen/` | `make_e110.py`'s output: `manifest.json`, `srcs/*.bin`, `counts.json`, `gen.sha256` |
| `e110.json` | the reduction, the registered primary arm: dips removed, `auto` slope. **The result** |
| `e110-leak0.2936.json`, `e110-leak0.3803.json` | the two registered sensitivities, dips removed |
| `e110-unfiltered.json` | the same reducer on the passes as they came |
| `ew-readme-formula.txt`, `ew-readme-formula.json` | **after the data, labelled (D1):** `E_w` by the registration's formula against the frozen code's, every arm |
| `corrections-check.py`, `corrections-check.txt` | added with the corrections after verification: every number they quote, from committed files (standard library, post hoc, deciding nothing) |
| `dips.json` | every board-meter dip, and where it falls |
| `runs.csv` | one row per run, primary arm: pass, item, level, launch reading, p_raw, p80, the three rails, off, the DDR die rail, rate, median `took_ms`, gate failures |
| `reduce.sh`, `reduce.txt` | the reduction commands and their printed output |
| `ident/` | `ettelem config` at the start and the end of the card session, and their times |
| `logs/` | the session log, the queue's output (each pass's runner log), the smoke's log, the dry run |

Code: `tools/claims-v3/e110/` (the registration, `52b5fc46`: `README.md`, `make_e110.py`, `make_predictions_e110.py`, `predictions.json`,
`reduce_e110.py`, `selftest_e110.py`, `session_e110.sh`, `queue_e110.sh`, `smoke_gate_e110.py`, `run_e110.sh`; post hoc, labelled: `desk/`; after the
data, labelled: `amend_e110.py`), with E75's `mf/block.sh`, E99's `dm/dm_enc.py`, E81's `dp/posthoc_dips.py` and the runner `runitems.py`, all
unchanged.

## Reproducing it

    # on aifoundry3, in ~/aifoundry, with tools/claims-v3/e110/ and build/e110-gen/ synced in, and the card idle
    bash tools/claims-v3/e110/run_e110.sh setup
    bash tools/claims-v3/e110/run_e110.sh go
    # on any machine with the lab repo and numpy
    python3 tools/claims-v3/e110/make_e110.py <dir> --e99-gen docs/reports/data/2026-11-01-e99-dram-mechanism/gen --check
    bash docs/reports/data/2026-11-01-e110-memory-width/reduce.sh
    python3 tools/claims-v3/e110/amend_e110.py docs/reports/data/2026-11-01-e110-memory-width > docs/reports/data/2026-11-01-e110-memory-width/ew-readme-formula.txt
    python3 docs/reports/data/2026-11-01-e110-memory-width/corrections-check.py > docs/reports/data/2026-11-01-e110-memory-width/corrections-check.txt
