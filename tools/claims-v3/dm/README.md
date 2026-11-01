# V3-DM: which mechanism carries the DRAM pattern effect (E99, Q132)

*Pre-registered Sun 1 Nov 2026 (week 44), about 01:00 PDT, on the Intel, by the Q132 workflow's lane `a3-e99-dram`. No card was
opened for this file. Frozen at the commit that adds it, before the Discord claim and before the first launch. Changes after
that go in Amendments, dated, before the data they touch. The desk result this rests on is post hoc and labelled so:
`docs/reports/data/2026-11-01-e99-dram-mechanism/README.md`.*

## The question

E81 (`docs/reports/data/2026-10-31-e81-dram-pattern/`) found that random bits cost 1.636 W more to read from DRAM than E75's
two-value image at the same changed-bit and one counts: +0.996 W for where the ones sit in a line, and +0.640 W for going from
a fixed 2-line cycle to 8,192 distinct lines, none of it before four distinct lines. It left the mechanism open (its "What it
changes" item 5), and the kinds page carries it as section 11 item 12.

**The hypothesis.** The memory runs read data-bus inversion, and reads are terminated to ground, so the cost goes with the pins
driven high after inversion, per byte about min(p, 9 − p) rather than the byte's p ones. Runs of ones are bytes 0x00 and 0xFF, which
cost almost nothing; scattered ones sit near p = 4, the worst case. And each of 16 channels carries every 16th line, so a period
that divides 16 looks constant to a channel. That would explain both halves of E81.

**Why E81's and E75's images cannot test it.** On their 18 measured points the high-pin count, the encoded toggle count and the raw
toggle count correlate at 0.99–1.00 (`posthoc-desk.txt`), so every encoding fits and none can be told from another.

## 1. What the public sources say, and what could not be checked

| fact | where (under the lab clone's `external/`) |
|---|---|
| eight memory shires, two 16-bit LPDDR4X controllers each: 16 channels | PRM §1.5; PRM overview "Sixteen 16-bit LPDDR4X controllers" |
| boot mode 933 MHz, ECC off, 16 GB, training on | `et-platform/device-bootloaders/src/ServiceProcessorBL2/driver/mem_controller.c:643-647` |
| the controller's read DBI, write DBI and data mask on: `DBICTL = 7` | `et-platform/etsoc-hal/src/memshire_ddr_init_functions.c:4522` |
| the DRAM's mode register: `emr2 = 0xf1` | same file `:4330`, `:4337`. For LPDDR4 this field is mode register 3, whose bits 6 and 7 enable read and write DBI (from memory of the controller's and the standard's documents, neither in the repo) |
| the PHY's `RdDbiEnabled = 1` in the 933 MHz branch | same file `:787` (`ms_init_ddr_phy_933_pre`) |
| the PHY terminates reads to ground only: `ODTStrenN = 0x38, ODTStrenP = 0` in the 933 MHz branch | same file `:720-727` |
| BL16: `MSTR.burst_rdwr = 8`, so a 64 B line is two 32 B bursts, 32 beats of two bytes | same file `:4536` |
| ECC configuration register written with `ecc_mode = 0` when ECC is off | same file, the `else` of `config_ecc` near `:4557` |
| bit 9 picks the controller, and the memory shire removes bits 9:6 from the address | `core-et/rtl/inc/esr_defines.vh:153-157` (`esr_ms_addr_mc_bit_sel = 9`, `esr_ms_addr_remove_bit_sel3..0 = 9, 8, 7, 6`) |
| with ECC off, each line in a channel sits in the next of eight banks | same `.c` file `:4639-4645` (`ADDRMAP1`, `ADDRMAP2`); the kernel's comment says the same (`workloads/enercat/kernel/enercat.c:163`, PA[12:10]) |
| no data scrambler setting | keyword search of that file: absence means not found |

**The rule itself** is the LPDDR4 standard's DBI-DC (JESD209-4, from memory, not in the repo): a byte with more than four ones is
sent inverted with its DMI pin high, so pins driven high per byte run 0 1 2 3 4 4 3 2 1 for p = 0…8.

**Not checked, and said so.** No DDR controller register was read on this card, and none will be in this run. The cards report BL2
0.22.0 (`docs/findings/14-card-behaviour.md`), the public line's version, but no card exposes a git hash and the binary was not
compared. That bits 8:6 pick the memory shire is inferred from the removal bits. The in-order mapping of a line's bytes onto two
lanes and 32 beats is assumed; swapping the lanes, or pins inside a lane, changes no count here. So the silicon itself is the test:
this experiment asks whether the card behaves as if those settings were live.

## 2. The design

E75's and E81's DRAM command, unchanged (`make_mf.args_for("dram", …)`): `enercat_host --pattern flw_pat --harts 1 --seconds 4
--window 240000000 --operands <op> --stride 64 --slice-bytes 131072 --region 131072`. E75's block and queue, E81's reduction
machinery. **One departure from E81's harness, registered here:** the host's `file:` operand takes exactly 256 B, four lines, so
the ladder needs a new operand, `lines:<path>` (`make_host_src.py` writes a copy of `main.cpp` with one added branch; the tree's
`main.cpp` stays as it is). `build_host.sh` compiles it with `enercat-hl`'s recorded compile and link lines, against its
`Constants.h`, so it launches `enercat-hl`'s kernel ELF unchanged, and first rebuilds the unchanged `main.cpp` to show those lines
reproduce E81's host `.text`. Every item, the 256 B ones too, runs on this one binary.

Counts per line, re-derived from the bytes by `make_dm.py --check` with `dm_enc.py` (`w` ones; `hi` pins driven high after inversion;
`t_enc`, `t_raw` pin toggles between beats after and before inversion; `k` bits changed between consecutive lines; `half` bits
differing between the line's 32 B halves; `k_chan` bits changed between two reads of one channel):

| item | what it is | lines | w | hi | t_enc | t_raw | k | half | k_chan |
|---|---|---:|---:|---:|---:|---:|---:|---:|---:|
| `dp_zeros` | E81's anchor | 1 | 0 | 0 | 0 | 0 | 0 | 0 | 0 |
| `dp_c1`, `dp_c2` | E81's bytes (E75's k0, k256) | 1, 2 | 256 | 32 | 2, 5 | 16, 40 | 0, 256 | 256, 128 | 0 |
| `dp_bern` | E81's random bits | 8,192 | 256 | 209 | 258 | 248 | 256 | 128 | 255 |
| `dm_w1` | one bit in every line | 1 | 1 | 1 | 1 | 1 | 0 | 1 | 0 |
| `dm_u1 u2 u4 u5 u7 u8` | **the tent**: every byte 0x01, 0x03, 0x0F, 0x1F, 0x7F, 0xFF | 1 | 64p | 64, 128, 256, 256, 128, 64 | 0 | 0 | 0 | 0 | 0 |
| `dm_l08` | lanes constant, one 0x00, one 0xFF | 1 | 256 | 32 | 0 | 0 | 0 | 0 | 0 |
| `dm_a08 a26 a35 a44` | each beat one byte value, alternating 00/FF, 03/FC, 07/F8, 0F/F0 | 1 | 256 | 32, 160, 224, 256 | 62, 62, 62, 496 | 496 | 0 | 0 | 0 |
| `dm_r08 r26 r44` | random bytes with p in {0,8}, {2,6}, {4} | 2 | 256 | 32, 160, 256 | 31, 224.5, 248 | 248 | 256 | 128 | 0 |
| `dm_L1 … dm_L8192` | **the ladder**: 1, 2, 3, 4, 8, 16, 17, 32, 256, 8192 distinct lines, one byte distribution (64 bytes with p = 1…7 in counts 2, 7, 14, 18, 14, 7, 2) | p | 256 | 211 | 258 | 248 | 256 (0 at p = 1) | 128 | 0 for p dividing 16; 171, 241, 128, 240, 255 at 3, 17, 32, 256, 8192 |

Exact to p = 17, and within 2 per line at 32, 256 and 8192 (2 toggles at the fitted price is 0.006 W). Consecutive lines of every
ladder image differ in exactly 256 bits, and the two lines each channel sees in `dm_L32` too. `k_chan` takes the two reads as
independent draws from the values at that channel's addresses, because the 1,024 harts run at different phases of an image; the same
line counts as no change, so it scales as 1 − 1/n for n values on the channel.

Per pass: `anchor_pi` first and last (E75's drift anchor), the 29 DRAM items once each, shuffled by `runitems.py`, two burn-in launches
before the first. **Smoke 9901** (`anchor_pi`, `dp_bern`, `dm_L17`, which exercises the new operand). **Passes 9910 onward; 9910 is the
registered warm-up, reported and never in the headline,** as in E81.

## 3. Frozen predictions (`predictions.json`)

Six models were fitted on E75's and E81's 18 measured points (posthoc, `make_predictions_e99.py`), and each predicts every new image with
an interval from those fits' residuals, in `predictions.json` `items`. The contrasts, watts, ± the 95 % prediction interval:

| contrast | what moves | `w_hi_chan` (ones + high pins + channel changes) | `dbi` (the brief's simplest: high pins + encoded toggles + floor) | `w_tenc_chan` (ones + encoded toggles + channel) | `w_traw_chan` (no DBI: ones + raw toggles + channel) | `bits` (ones + changes) |
|---|---|---:|---:|---:|---:|---:|
| `hi_t0` = u4 − l08 | w 256, no toggles; high 256 vs 32 | **+0.92 ± 0.54** | +2.12 ± 4.70 | 0.00 ± 0.50 | 0.00 ± 0.56 | 0.00 ± 1.70 |
| `hi_ta` = a35 − a08 | w 256, raw 496, encoded 62; high 224 vs 32 | **+0.79 ± 0.52** | +1.82 ± 4.05 | 0.00 ± 0.50 | 0.00 ± 0.56 | 0.00 ± 1.70 |
| `hi_r` = r44 − r08 | w 256, k 256, half 128, raw 248; high 256 vs 32 | **+0.92 ± 0.54** | +1.52 ± 1.69 | +0.65 ± 0.53 | 0.00 ± 0.56 | 0.00 ± 1.70 |
| `tent_S` = (u4 − u2) − (u7 − u5) | free of a linear price of ones | **+1.05 ± 0.73** | +2.42 ± 5.42 | 0.00 ± 0.70 | 0.00 ± 0.80 | 0.00 ± 2.41 |
| `tie27` = u7 − u2 | 128 high on both; 320 more ones | **+0.98 ± 0.75** | 0.00 ± 0.88 | +1.14 ± 0.78 | +1.14 ± 0.88 | +1.62 ± 2.65 |
| `tie45` = u5 − u4 | 256 high on both; 64 more ones | **+0.20 ± 0.50** | 0.00 ± 0.88 | +0.23 ± 0.51 | +0.23 ± 0.58 | +0.32 ± 1.75 |
| `tie18` = u8 − u1 | 64 high on both; 448 more ones | **+1.37 ± 0.95** | 0.00 ± 0.88 | +1.60 ± 0.97 | +1.60 ± 1.10 | +2.26 ± 3.31 |
| `t_enc` = a44 − a35 | raw same; encoded +434, high +32 | **+0.13 ± 0.48** | −0.90 ± 5.82 | +1.29 ± 0.61 | 0.00 ± 0.56 | 0.00 ± 1.70 |
| `t_raw` = a08 − l08 | high same; raw +496, encoded +62 | **0.00 ± 0.48** | −0.17 ± 1.27 | +0.18 ± 0.50 | +1.69 ± 0.78 | 0.00 ± 1.70 |
| `r08_vs_c2` | high same; raw 248 vs 40 | **0.00 ± 0.48** | −0.07 ± 0.96 | +0.08 ± 0.50 | +0.71 ± 0.61 | 0.00 ± 1.70 |
| `L2_vs_r08` | raw same; high 211 vs 32 | **+0.73 ± 0.52** | +1.06 ± 0.98 | +0.68 ± 0.53 | 0.00 ± 0.56 | 0.00 ± 1.70 |
| `floor_w1` = w1 − zeros | one bit | **+1.09 ± 0.68** | +1.73 ± 1.08 | +1.08 ± 0.70 | +0.99 ± 0.80 | +1.08 ± 2.45 |
| `h3 h4 h8 h16 h17 h32 h256 D` over `dm_L2` | the ladder | **+0.45, 0, 0, 0, +0.63, +0.33, +0.63, +0.67** (±0.48–0.57) | 0 (±0.88) | +0.41, 0, 0, 0, +0.58, +0.31, +0.58, +0.61 | +0.42, 0, 0, 0, +0.59, +0.31, +0.59, +0.62 | 0 (±1.70) |

The `dbi` column's wide intervals are the point of this experiment: its two prices cannot be separated on old images.

An effect is **present** when its mean is ≥ 0.25 W and its 95 % interval excludes 0, **absent** when its 95 % interval lies inside
±0.30 W, **unresolved** otherwise (E81's rule, unchanged).

### The registered verdicts (`reduce_dm.py`, `verdicts`)

| rule | test | PASS | FAIL | what the opposite means |
|---|---|---|---|---|
| **R1** session tie | `tie_total`, `tie_c2`, `tie_bern` within ±0.35 W of E81's 1.636, 1.866, 3.501; `tie_c1` within ±0.40 W of 2.046 | inside | outside | another session's memory; the rest is read as this session's |
| **R2** high pins, the same ones, no toggles | `hi_t0` | present and in [0.46, 1.84] W | absent | absent: pins driven high do not pay, whatever the firmware says |
| **R3** high pins, equal raw and equal encoded toggles | `hi_ta` | present and in [0.39, 1.58] W | absent | the same, in a stream that toggles |
| **R4** the tent's shape | `tent_S` | present and in [0.53, 2.10] W | absent | absent: the response to ones has no kink at p = 4–5, so read DBI does not show in the power |
| **R5** whole bytes in random places | `r08_vs_c2` absent and `L2_vs_r08` present | both | `L2_vs_r08` absent, or `r08_vs_c2` present | scatter pays even when every byte is 0x00 or 0xFF: not the high pins |
| **R6** the same pins high, different ones | `tie27`, `tie18` | both absent: pure DBI, ones cost nothing beyond the pins; both present: ones cost beyond the pins, at the price read from the ties | | a mix stays unresolved. This is the same-high-pin test: the `dbi` model must fail if they are present, and `w_hi_chan` if they are absent |
| **R7** encoded toggles | `t_enc` | absent (the pins' DC pays, not their toggles) | present | present: encoded toggles pay |
| **R8** raw toggles | `t_raw` | absent (raw toggles are not on the pins, read DBI hides them) | present | present: a path sees the raw bytes at 16-bit steps, or DBI is off |
| **R9** the 32 B halves | `half` | reported with its class | | E81's post-hoc account has a `half` term (2.4 pJ per bit, so +0.72 W); `w_hi_chan` has none |
| **R10** the floor | `floor_w1` | reported with its class | | present: a line with one bit pays the whole floor, and an all-zero line is a special case. Absent: the floor is the fits' convexity |
| **R11** the channel | the ladder | `D` present; `h4`, `h8`, `h16` absent; `h3`, `h17` present; `h32` between 15 % and 85 % of `D` | `h8` or `h16` present, or `h3` or `h17` absent | the step is not where the channel count says: named readings below |
| **R12** closure | prices from `hi_ta` (per high pin), `t_enc` (per encoded toggle, net of its 32 high pins) and `t_raw` (per raw toggle, net of its 62 encoded) predict `arr_L2` = L2 − c2 as 179 hi + 253 enc + 208 raw | within ±0.30 W of the measured `arr_L2` | outside | the structured images' prices do not add up to the arrangement on random lines |
| **R13** the compute rail | the raw minion rail on `hi_t0`, `hi_ta`, `D`, `tie_total` | each within ±0.10 W | outside | that much of the effect is in the compute side after all |

**The overall reading, by rule:** `overall_dbi` is CONFIRMED when R2, R3, R4 and R5 all PASS; REFUTED when R2 and R3 both FAIL; PARTIAL otherwise.

**R11's named readings, registered:** `h16` present with `h8` absent: a path of the 8-way interleave pays (memory shires, not channels).
`h32` absent with `h256` present: a path of about the 128-way interleave pays (the banks). `h32` and `h256` both absent with `h3` and `h17`
present: powers of two up to 256 are free, so the path is much deeper than the channels. `h4`, `h8`, `h16` present in a rising row: a cost that
grows with the number of distinct lines, not with what one channel sees, which refutes the reading outright.

## 4. Decision rules

1. **Estimator: E81's.** Per kept pass, each item's board power over [t0+1 s, t0+3 s), corrected to the launch reading with the leakage slope;
   every contrast a within-pass difference; the headline is the mean over headline passes with a two-sided t interval on their scatter (df = n − 1).
2. **Primary arm: the board meter's dips removed** by E82 A2's definition (`dp/posthoc_dips.py`: `board_w[i] < min(board_w[i-2], board_w[i+2]) − 4 W`),
   registered here because E81 found them after its data: 12 such samples in its windows, one verdict moved by them. The unfiltered arm is reported beside it,
   and any verdict that differs between the two is named.
3. **Run and pass gates: E81's.** One clock; voltage within 3 mV of the pass median; an on-protocol launch within 0.5 °C of 58 °C after a 59 °C preheat;
   the window's median `took_ms` ≤ 60 ms; an ok device record. `anchor_pi` drift above 0.3 W, or more than a third of a pass's DRAM runs failing a gate, sets the pass aside.
4. **Leakage:** E81's `auto` slope; 0.2936 and 0.3803 W/°C reported as sensitivities.
5. **Budget:** at most **33 card-minutes** in all, a smoke of about 2 min and up to six passes of about 5 min; no pass starts once the session's card clock has
   passed 27 min or the wall clock has passed 01:50 PDT (the next lane on this card), by touching `build/mf-STOP`; a pass that has started finishes. Fewer than three
   headline passes: every verdict UNRESOLVED.
6. **What it changes.** It answers section 11 item 12's mechanism question, or says which part of the reading is refuted. It moves no arithmetic ledger.

**Reported, not scored:** every item over zeros in W and pJ per line, every contrast, the per-one prices `tie27/320`, `tie45/64`, `tie18/448` and their agreement, `kink`, `hi_ta26`, `hi_r26`,
`t_both`, `ones_u8`, `u1_over_w1`, `h1`, `bern_vs_L8192`; the rail on every contrast and item; the line rate per item (a pattern that moved the rate would be seen here); the leakage
sensitivities; the warm-up pass.

## 5. How to run it (aifoundry3, in `~/aifoundry`)

    bash tools/claims-v3/dm/run_e99.sh build        # no card, but it loads the host: only with the card idle
    bash tools/claims-v3/dm/run_e99.sh setup        # image hashes, harness hashes, the dry run. No card.
    bash tools/claims-v3/dm/run_e99.sh smoke 9901   # one short block (about 1 min of card time)
    bash tools/claims-v3/dm/run_e99.sh go 9910 6    # the detached queue; log build/e99-dm.log
    bash tools/claims-v3/dm/run_e99.sh status

Stop between passes: `touch ~/aifoundry/build/mf-STOP`. Data in `build/claims-v3/aifoundry3/dm/p<pass>/`.

## 6. Risks, and what each one does to the result

- **Line-to-channel phase.** If a slice's base is not 1 KB aligned the channels rotate; each channel still sees one value for a period dividing 16, because every region starts a
  multiple of 16 lines from the slice's base (`SLICE_STRIDE` = 2,176 lines, bank offsets 16 lines). Period 17 is special: 2,176 lines is a multiple of 17, so harts' phases differ only by
  the bank offset, eight phases. Its channels still see all 17 values.
- **The lanes' mapping.** If bytes did not go alternately to two lanes, `dm_l08` would toggle and `dm_a08` might not, and `t_raw` would come out negative. That would read as a failed
  assumption, not as a price.
- **A byte value's pins.** Each tent image drives particular pins. All pins are assumed alike; a tent read pin by pin is not in this budget.
- **The first half of each line goes further.** `flw.ps` takes 32 B of each line into a register. Every image has about half its ones in that half, except `dp_c1` (all of them), `dm_w1` (its one), and what `half` tests.
- **The response to ones is concave near zero** (E75), so a tent without DBI is not quite a line; `tent_S` is taken over p = 2…7 to stay on its straight part, and E75's arm bounds the bend at about 0.1 W there.
- **The meter's dips:** rule 2. **The first pass off another lane's load:** the warm-up. **The meter starves on DRAM bursts:** E75 and E81's worst window median was 22 ms against the 60 ms gate.
- **Another user, or the demo service:** `mf/block.sh` stops on another user's device process or lock (an idle login does not block), holds `/run/lock/etsoc-shire0.lock`. Device launches run under `timeout 10`; `lib.sh`'s `die_c` and whole-pass sampler are its frozen design, as in every block since E60.
- **Nothing is set on the card:** no governor, TDP, threshold or clock write; `ettelem config` is read, read-only, under the lock with `timeout 10`, at both ends of the card session.

## Files

| file | what it is |
|---|---|
| `dm_enc.py` | the line-level encoder: bytes to high pins, encoded and raw toggles, per-path line changes |
| `make_dm.py` | the images and the commands; `--check` re-derives every count from the bytes on disk |
| `make_host_src.py`, `build_host.sh` | the `lines:` operand, added to a copy of `main.cpp`; the build, with the verify build beside it |
| `run_e99.sh` | `build` / `setup` / `dry` / `smoke` / `go` / `status`, through E75's `mf/block.sh` and `mf/queue_mf.sh` unchanged |
| `posthoc_desk.py` | **post hoc, labelled:** the counts of every E75 and E81 image and the fits on their watts |
| `make_predictions_e99.py`, `predictions.json` | the fits' predictions for every new image and contrast, and the bands; frozen with this commit |
| `reduce_dm.py`, `selftest_dm.py` | the registered reduction and verdicts, tested before the first pass on E81's passes relabelled (a pipeline test, not data) |

## Amendments

*(none yet)*
