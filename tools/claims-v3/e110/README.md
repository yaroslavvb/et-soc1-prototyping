# E110: the memory path's width ladder (Q133)

*Pre-registered Sun 1 Nov 2026 (week 44), about 14:00 PST, on the Intel, by the Q133 workflow's lane `a3-e110-memory-width`. No card was opened
for this file. Frozen at the commit that adds it, before the Discord claim and before the first launch. Changes after that go in
Amendments, dated, before the data they touch.*

*It answers the kinds page's [section 11, what is still open](https://spacesheep.dev/@yaroslavvb/horace-kinds-of-numbers#11-what-is-still-open),
**item 10, "The memory path"**, as it reads at `1fe8377a18af`: "Open: the 1.3 pJ of a one that is off every metered rail (how much is regulator
loss, the memory shires' logic, the DRAM chips); which unmetered paths carry the half-line bits and the 64-bit toggles, post hoc so far; what sets
the period ladder's steps on each rail. A width ladder registered first would find the raw path's width."*

## The question

[E99](../../../docs/reports/data/2026-11-01-e99-dram-mechanism/README.md) decided read data-bus inversion (DBI) on aifoundry3 card 0 and priced
a one, a pin driven high and a pin toggle. It left the rest to a post-hoc account: random data's step over zeros needs, beyond those, a cost for
bits that differ between a line's two 32 B halves (`half`, 2.53 pJ a bit) and for raw toggles between consecutive 64-bit pieces (`r64`, 2.22 pJ),
both on no metered rail. It said itself that the widths are its weakest part: `half` + `r32` and `half` + `e64` (the 64-bit toggles of the
DBI-*encoded* data) fit nearly as well, "so 64 bits and raw against encoded are not settled", and it named the test: "A width ladder, 32-, 64-,
128- and 256-bit alternations at equal ones and high pins, registered first, would find the raw path's width."

E110 asks four things, on the same card and command:

1. **Which path widths pay for raw toggles?** (R2, the W ladder.)
2. **Is the 64-bit price on the raw data or on the DBI-encoded data?** (R3, the V ladder against the W ladder.) The controller decodes DBI
   (`DFIMISC.phy_dbi_mode = 0`, `etsoc-hal/src/memshire_ddr_init_functions.c:4765`, which E99 cites), so the PHY side carries encoded data
   and everything after the decoder carries raw data. The DRAM's own array and prefetch path carry raw data too: it inverts at its output.
3. **Is the half-line cost a raw 256-bit path beyond the narrower ones?** (R4.)
4. **Where are these, and a one's 1.3 pJ, paid?** On the metered rails, in the memory shires' logic (read through the DDR die rail, R5), or
   elsewhere; and how much of a one's off-rail price an on-chip load's regulator share explains (R6).

The period ladder's steps per rail are **not** registered here; § 6 says why.

## 1. Three desk readings that shape the design (POST HOC, labelled; `desk/`)

Each was computed at the desk from committed telemetry before this file was frozen. None is a result; each only sets an arm or a frozen class.

- **E75's "L3" level reads DRAM.** On every item its die-rail voltage, its three rails and its board power match the DRAM level's: the DDR die
  rail reads 763.0 mV on both zeros items against 766.0-766.8 at L1 and L2 (`desk/e75_levels.txt`), and the 256-ones image costs +2.03 W over
  zeros at both levels (E75's `runs.csv`, p80 means: 34.327 − 32.297 and 34.234 − 32.199 W). So E110's on-chip arm uses E75's L2 level (8 KB per hart), which reads 766 mV.
- **On E75's L2 level, about 16 % of a data-dependent step is off the three metered rails** (k0 over zeros: board +1.978 W, NoC +0.739, SRAM
  +0.694, minion +0.228, off +0.317; `desk/e75_levels.txt`). An on-chip load touches no unmetered rail on purpose, so that fraction is an upper
  bound on the three regulators' own loss. R6 measures it again in this session.
- **On E99's images the DDR die rail moves with toggles of the encoded data on paths wider than a beat, and not with ones, pins, beat toggles
  or the half-line bits** (`desk/e99_die_rails.txt`, over zeros, five passes). It reads −1.0 to −2.0 mV on every image whose encoded data change
  between 64-bit pieces (the period ladder, `dm_r26`, `dm_r44`, `dp_bern`: `e64` 192-252 a line), and within 0.1 mV of zeros on every image whose
  encoded data change between 64-bit pieces in their DMI bits at most (`e64` ≤ 26: the tent `dm_u1`-`dm_u8`, `dm_l08`, the beat images `dm_a08`-`dm_a44` with up to 496 pin toggles,
  `dm_r08`, and `dp_c1`, E99's `half` image, +0.85 W on the board). The voltage is read in whole millivolts, so this is a class, not a scale.
  It is why the V ladder and R5 are here: if it holds, the 64-bit cost is on the encoded side, in the memory shires, which E99's chosen
  account (raw) says it is not.

## 2. The design

**Command:** E75's and E99's DRAM command, unchanged (`enercat_host --pattern flw_pat --harts 1 --seconds 4 --window 240000000 --operands <op>
--stride 64 --slice-bytes 131072 --region 131072`): 1,024 harts each fetch one 64 B line per load from 128 MB in all. The on-chip arm is E75's L2
command (`--slice-bytes 8192 --region 8192`). **Binary:** E99's host on the box, `build/enercat-e99/host/enercat_host` (its `file:` and
`lines:` operands, E81's `enercat-hl` kernel ELF), unchanged and not rebuilt; `run_e110.sh setup` prints its hash beside E99's
(`docs/reports/data/2026-11-01-e99-dram-mechanism/logs/e99-build-hashes.txt`). **Harness:** E75's `mf/block.sh` and E99's runner, unchanged
(`MF_GEN=build/e110-gen`, `MF_EXPN=e110`); E110's own files are the images, the session and queue scripts with their deadline, the smoke gate and
the reducer.

**Items** (`make_e110.py`; every count re-derived from the bytes by `make_e110.py --check`, with E99's encoder `dm/dm_enc.py`). Nine images are
E99's own bytes and commands, checked against its `gen.sha256`. Per 64 B line: `w` ones, `hi` pins driven high after inversion, `t_enc`/`t_raw`
pin toggles between beats after/before inversion, `rW`/`eW` raw/encoded toggles between consecutive W-bit pieces inside a line (E99's post-hoc
definitions, written out in `make_e110.py`), `half` = `r256`:

| family | item | what it is | w | hi | t_enc | t_raw | r32 | r64 | r128 | half | e64 |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| W (raw) | `dm_l08` | lanes constant, 0x00 and 0xFF (E99) | 256 | 32 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| | `dm_a08` | 16-bit beats alternate 0x0000/0xFFFF (E99) | 256 | 32 | 62 | 496 | 0 | 0 | 0 | 0 | 0 |
| | `wl_32` | 32-bit blocks alternate all-0x00/all-0xFF | 256 | 32 | 30 | 240 | 480 | 0 | 0 | 0 | 0 |
| | `wl_64` | 64-bit blocks | 256 | 32 | 14 | 112 | 224 | 448 | 0 | 0 | 56 |
| | `wl_128` | 128-bit blocks | 256 | 32 | 6 | 48 | 96 | 192 | 384 | 0 | 24 |
| | `wl_256` | the 32 B halves, 0x00 then 0xFF | 256 | 32 | 2 | 16 | 32 | 64 | 128 | 256 | 8 |
| | `dp_c1` | the 32 B halves, 0xFF then 0x00 (E81, E99's `half`) | 256 | 32 | 2 | 16 | 32 | 64 | 128 | 256 | 8 |
| V (raw = encoded) | `dm_u4` | every byte 0x0F (E99) | 256 | 256 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| | `dm_a44` | beats alternate 0x0F0F/0xF0F0 (E99) | 256 | 256 | 496 | 496 | 0 | 0 | 0 | 0 | 0 |
| | `vl_32` `vl_64` `vl_128` `vl_256` | the W rungs with 0x0F/0xF0 | 256 | 256 | 240, 112, 48, 16 | = t_enc | as W | as W | as W | as W | 0, 448, 192, 64 |
| T (ones) | `dm_u1`, `dm_u8` | every byte 0x01, 0xFF at DRAM (E99) | 64, 512 | 64 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| | `l2_u1`, `l2_u8`, `l2_zeros` | the same bytes, and zeros, at E75's L2 level | 64, 512, 0 | | | | | | | | |
| P | `dm_L2`, `dm_L8192` | the two ends of E99's period ladder (E99) | 256 | 211 | 258 | 248 | 240, 241 | 220, 225 | 198, 192 | 128 | 241, 235 |
| anchors | `anchor_pi`, `dp_zeros`, `dp_bern` | E75's drift anchor first and last; E81's zeros and random bits | | | | | | | | | |

Every W line has 256 ones and 32 pins high; after inversion all its data pins are low, so its raw bits toggle at the block edges and its encoded
data stand still except one DMI bit per byte at each edge. Every V line has 256 ones and 256 pins high and no byte inverted (p = 4), so its
encoded data toggle exactly as its raw data do. All W/V/T lines repeat one line (`k` = 0, no path change), so nothing of the period ladder is in
them. For a rung of width w a W-bit piece with W ≤ w toggles all its W bits at each of the line's 512/w − 1 edges (31, 15, 7, 3, 1 for w = 16 …
256), and a W-bit piece with W > w never toggles, so **a path of width W sees toggles only on rungs w ≥ W: the first rung that costs is the
narrowest path that pays.** The one-line images go through `file:` repeated to 256 B, as E99's did; `dm_L8192` through `lines:`.

**Per pass:** `anchor_pi` first and last, the 22 memory items once each in the runner's shuffled order, two burn-in launches: 24 runs, about
3.5 min. **Smoke 11001** (`anchor_pi`, `wl_64`, `vl_64`, `l2_u8`: both new families and the L2 level) and its gate (`smoke_gate_e110.py`: block
ok, every item launched with ok records and lines moved, every telemetry sample carrying the three rails and `die_mv.ddr`). **Passes 11010-11016;
11010 is the registered warm-up, reported and never in the headline,** as in E81 and E99.

## 3. Frozen predictions (`predictions.json`, `predictions.txt`)

Each reading's prices are E99's post-hoc fits as committed (`posthoc-fit.txt`, "The search"), used only to freeze what each predicts for images
it never saw; the H rows are one raw path of that width, sized to E99's measured `half` (+0.850 W). W over each family's baseline (`S` = W rung
over `dm_l08`, `V` = V rung over `dm_u4`), and `E64` = the encoded wide-path residual (below):

| reading | S32 | S64 | S128 | S256 | V64 | V128 | E64 | c256 | raw onset |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| **A** `half` + `r64` (E99's chosen account) | +0.03 | **+1.18** | +0.51 | +0.93 | +1.28 | +0.55 | 0.00 | +0.76 | **64** |
| B `half` + `e64` (encoded 64) | +0.03 | +0.14 | +0.06 | +1.05 | +1.14 | +0.49 | **+0.90** | +1.03 | 256 |
| C `half` + `r32` | **+0.98** | +0.46 | +0.20 | +1.00 | +0.57 | +0.24 | 0.00 | +0.93 | 32 |
| D `half` + `r128` | +0.04 | +0.02 | **+0.75** | +1.12 | +0.15 | +0.81 | 0.00 | +0.87 | 128 |
| E `half` + `r64` + `e64` | +0.03 | +0.85 | +0.36 | +0.92 | +1.36 | +0.58 | +0.41 | +0.80 | 64 |
| F `half` alone | +0.05 | +0.02 | +0.01 | +1.41 | +0.18 | +0.08 | 0.00 | +1.41 | 256 |
| H64, one raw 64-bit path | +0.03 | +5.95 | +2.55 | +0.85 | +6.04 | +2.59 | 0.00 | 0.00 | 64 |
| H256, one raw 256-bit path | +0.03 | +0.01 | +0.01 | +0.85 | +0.11 | +0.05 | 0.00 | +0.85 | 256 |

(`predictions.txt` has every row and column, H32 and H128 included.) The readings disagree by 0.4-1.2 W on S32, S64, S128 and E64, against E99's
typical ±0.10 W interval, so the ladder decides among them.

## 4. Decision rules (`reduce_e110.py`, `verdicts`)

**Classes** (E81's rule, unchanged, every board contrast): *present* when the mean is ≥ 0.25 W and the 95 % interval excludes 0; *absent* when
the interval lies inside ±0.30 W; *unresolved* otherwise. For the DDR die rail (`die_mv.ddr`, mV): *moves* at a mean ≤ −0.30 mV with the
interval below 0, *still* when the interval lies inside ±0.30 mV.

| rule | test | reading / verdict |
|---|---|---|
| **R1** session tie | byte-identical E99 contrasts: `S16` (E99 `t_raw` −0.026), `Sc1` (`half` +0.850), `V16` (`t_both` +0.475), `D` (+0.755) within ±0.30 W; `tie18` (+1.727) within ±0.35; `bern` over zeros (+3.466) within ±0.40 | PASS if all within; FAIL otherwise (another session's memory: the rest is read as this session's) |
| **R2** the raw path's width | the W ladder `S32`, `S64`, `S128`, `S256` | the onset is the first rung from 32 up that is present with every rung below it (from 32) absent; NONE if no rung is present; UNRESOLVED if an unresolved rung comes first. **Predicted: 64** (reading A). PASS if 64, FAIL if another resolved onset |
| **R3** raw or encoded at 64 bits | `S64`, and `E64` = (`vl_64` − `dm_u4`) − (`wl_64` − `dm_l08`) − (7/31)·[(`dm_a44` − `dm_u4`) − (`dm_a08` − `dm_l08`)]: the V ladder over the W ladder with the pins' share, measured at rung 16 and scaled by the edges, removed | RAW (`S64` present, `E64` absent), ENCODED (`E64` present, `S64` absent), BOTH, NEITHER, or UNRESOLVED. **Predicted: RAW** (reading A). PASS if RAW. `E32`, `E128`, `E256` reported with their classes |
| **R4** the half-line bits | `c256` = `S256` − `S128`/3 (the 256-bit path beyond everything narrower, on within-line edges); `E256`; `phase` = `dp_c1` − `wl_256` | RAW256 if `c256` is present and `E256` is not; NO256 if `c256` is absent; ENCODED256 if `E256` is present. **Predicted: RAW256**. PASS if RAW256. `phase` reported (predicted absent: where the ones sit in the line does not matter) |
| **R5** the memory shires' logic (DDR die rail) | the class of `die_mv.ddr` on `V64`, `S64`, `S256`, `Sc1`, `tie18`, `D` and `cal` (= `dp_zeros` − `l2_zeros`) | **Predicted** (§ 1's desk reading): `V64` moves, `S64` still, `S256` still, `Sc1` still, `tie18` still, `D` moves, `cal` moves. PASS if every class is as predicted; FAIL if a resolved class differs; UNRESOLVED otherwise. For each *still* contrast, an upper bound on its share in the memory shires' logic: the interval's larger end over `k_ddr` = −ddr(`cal`)/off(`cal`), mV per W, which is a lower bound on the rail's sensitivity because part of `cal`'s off-rail watts are the DRAM chips and the pads |
| **R6** a one's 1.3 pJ | per pass, the price of a one at DRAM from `tie18` and at L2 from `l2_ones` (`l2_u8` − `l2_u1`), each column over 448 ones and its own level's line rate; `f` = off/board at L2; the regulators' share `R` = (NoC + SRAM + minion at DRAM) · f/(1 − f); the remainder `X` = off at DRAM − `R` | PASS (a one pays off the metered rails beyond the regulators' share) if `X`'s interval is above 0; FAIL (the on-chip off-rail fraction accounts for it) if `X`'s interval lies inside ±0.30 pJ; UNRESOLVED otherwise. **Predicted:** `X` ≈ 0.99 pJ, `f` ≈ 0.16, `R` ≈ 0.37 pJ (E99's rails, § 1's L2 reading) |

**Reported, not scored:** every item over its level's zeros on the board, each rail, off and the DDR die rail; every contrast in every column;
where each ladder effect is paid (the three rails' sum: *on no metered rail* when its interval lies inside ±0.10 W); prices per toggled bit from
the triangular solve of each ladder, on within-line edges and on edges that count each path's line-to-line edge (`c_w` = [S_w/n_w − S_{w/2}/n_{w/2}]
/ w / line rate); `c256_cyc`; every frozen reading's rms over the ladder contrasts (`models_rms_W`); the line rate per item and per level; the
warm-up pass; the leakage sensitivities; the unfiltered arm.

**The estimator, gates and arms: E99's, unchanged.** Per kept pass, each item's board power over [t0+1 s, t0+3 s), corrected to the launch reading
with E81's `auto` leakage slope (0.2936 and 0.3803 W/°C reported as sensitivities); the three rails raw over [t0+2 s, t0+4 s), never past the
run, as `reduce_hl` reads the minion rail; the DDR die rail over the board's window; every contrast a within-pass difference; the headline the mean
over headline passes with a two-sided t interval on their scatter (df = n − 1). Run gates: one clock, voltage within 3 mV of the pass median, an
on-protocol launch within 0.5 °C of 58 °C after a 59 °C preheat, the window's median `took_ms` ≤ 60 ms, an ok record, the rails present. A pass is
set aside at an `anchor_pi` drift above 0.3 W or more than a third of its memory runs failing a gate. **Primary arm: the board meter's dip samples
removed** (`dp/posthoc_dips.py`'s definition, as E99 registered it); the unfiltered arm beside it, and any verdict that differs is named. **Fewer
than three headline passes: every verdict UNRESOLVED.**

**Budget and stops:** at most **40 card-minutes** (the brief's), as one detached session (`session_e110.sh`): the opening `ettelem config`, the smoke
(about 1.5 min), the gate, passes 11010-11016 (`queue_e110.sh`), the closing `ettelem config`. A pass starts only if, at the longest pass so far
(first estimate 240 s), it ends before the session's start + 36 min; a pass in flight is never cut. `build/e110-STOP` stops the queue before its
next pass. No session starts after 18:00 PST; everything ends by 19:00 PST. Expected: seven passes in about 28 card-minutes.

## 5. How to run it (aifoundry3, in `~/aifoundry`)

    # on the Intel: images, then sync the tools and the images to the box
    python3 tools/claims-v3/e110/make_e110.py <gen> --e99-gen docs/reports/data/2026-11-01-e99-dram-mechanism/gen --check
    rsync tools/claims-v3/e110/ aifoundry3:aifoundry/tools/claims-v3/e110/; rsync <gen>/ aifoundry3:aifoundry/build/e110-gen/
    # on the box
    bash tools/claims-v3/e110/run_e110.sh setup     # hashes, the dry run; no card
    bash tools/claims-v3/e110/run_e110.sh go        # the detached session: config, smoke, gate, passes, config (CARD RUN)
    bash tools/claims-v3/e110/run_e110.sh status
    # back on the Intel, with numpy (the primary arm, as E99's reduce.sh)
    python3 tools/claims-v3/dp/posthoc_dips.py <passes>/p1101? --work <work> --out dips.json
    python3 tools/claims-v3/e110/reduce_e110.py <work>/p1101? --gen <gen> --pred tools/claims-v3/e110/predictions.json --out e110.json --csv runs.csv

Data on the box: `build/claims-v3/aifoundry3/e110/p<pass>/`, session log `build/e110/`.

## 6. What E110 does not do, and why

- **The period ladder's steps per rail.** E99's per-rail ladder cannot say which interleave sets each rail's steps: fitted per rail with one
  line-change count per interleave, the two best interleaves differ by 0.4 % (NoC), 2.6 % (SRAM) and 9 % (off) in rms (`desk/e99_ladder_ways.txt`,
  post hoc), because the paths' interleaves are nested and a periodic image moves them together. Registering the same rungs again would score
  the same non-separation. E110 keeps the ladder's two ends (`D`) for R1 and R5 only: whether the period step moves the memory shires' logic.
  Separating interleaves needs images that are not periodic in the line index; that design is not made here.
- **The DRAM chips against the PHY and pads.** No meter reaches either. R5 bounds the memory shires' logic, and R6 the regulators' share; what
  remains after both is "the PHY, the pads and the DRAM chips", not split.

## 7. Risks, and what each does to the result

- **The DMI pins move in the W ladder** (62, 30, 14, 6, 2 toggles a line on rungs 16 … 256): at E99's 0.82-0.88 pJ that is 0.06 W at most,
  inside every band, and E99 measured `S16` itself at −0.026 W. R3 removes the pins' share with rung 16's own measurement.
- **Line-to-line edges.** A path that carries one line after another sees one more edge a line on every rung that toggles it (the last block of a
  line against the first of the next). Onsets do not depend on it; prices do, by up to ×2 at 256 bits. Both counts are reported; within-line is
  primary, as E99's `half` was.
- **Byte order on the pins.** In-order lanes are assumed, as in E99; the W and V counts at 32 bits and wider do not depend on the lane mapping.
- **The first half of each line goes further** (`flw.ps` loads 32 B of each line). Every W/V rung below 256 has equal ones in both halves; at
  256 bits `phase` measures it, and E99's rails cleared it.
- **The DDR die rail is read in whole millivolts.** R5 scores classes only, and its bound uses a lower bound on the sensitivity, so it errs wide.
- **The L2 level's rail mix is not DRAM's** (more SRAM, less NoC), and an on-chip load may touch something unmetered. R6's `f` is an upper bound
  on the regulators' loss for that mix, not each regulator's own efficiency.
- **Another user, the demo service, the meter's dips, the first pass:** as E99 (block.sh stops on another user's device process or lock; the dip
  filter; the warm-up pass).
- **Nothing is set on the card:** no governor, TDP, threshold or clock write, no `--reset-ms`, no PMIC command; `ettelem config` is read, read-only,
  under the lock with `timeout 10`, at both ends of the session.

## Files

| file | what it is |
|---|---|
| `make_e110.py` | the images, the commands, every count; `--check` re-derives them from the bytes and checks E99's nine against its `gen.sha256` |
| `make_predictions_e110.py`, `predictions.json`, `predictions.txt` | every reading's frozen predictions, the bands and the decision constants |
| `reduce_e110.py` | the registered reduction and verdicts |
| `selftest_e110.py` | a pipeline test before any pass: E99's passes relabelled; it must reproduce E99's reducer on the runs both read (`selftest.txt`) |
| `session_e110.sh`, `queue_e110.sh`, `smoke_gate_e110.py`, `run_e110.sh` | the card session, the queue with its deadline, the smoke gate, the setup and status stages |
| `desk/` | **post hoc, labelled:** `e75_levels.*`, `e99_die_rails.*`, `e99_ladder_ways.*`, the three desk readings of § 1 and § 6 |

## Amendments

*(none yet)*
