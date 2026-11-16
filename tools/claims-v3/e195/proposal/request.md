# Request 1114-x09-dramtoggle: memory traffic, ones against toggles, read and written

Family X09. Sat 14 Nov 2026, revised twice the same day (section 12). The forecast was frozen before any datum and is
sealed: only its sha256 is published, in the proposal. Source: `src/` (written from the public instruction set, the
open SDK's headers, the runtime's public interface, the public lab repo's `workloads/enercat` access patterns and its
`tools/claims-v3` runner, block library, E128 telemetry guard, device-command audit and E139 and E183 session kits;
`src/BUILD.md`).

## 1. Question

What does one 64 B line of memory traffic cost, with the data's ones and its toggles held apart, written as well as
read? Per line: the price of a data pin held high for a beat (termination at the receiving end), of a pin toggle (the
line's charge, the serialisers), of a raw one carried behind the pins (the mesh, the memory path's raw words), of a bit
changing on the memory path's 64-bit and 256-bit words and between the lines one channel carries; whether write
data-bus inversion is live (decided by toggles, not by termination); what share of each no metered rail sees; whether
each is a price per line (the same at half the line rate); and what a line of zeros, and a line that is not all zeros,
costs against controls whose cores do exactly the same thing. In pJ and in electrons per line, at the 12 V input and on
each metered rail.

The lab has priced the read side on this card with designed images (E75, E81, E99, E110, E132, E139; E156 on a second
card): a pin driven high 1.4-1.9 pJ a beat (E99's `u4 - l08`: 1.47 pJ), an encoded pin toggle about 0.8 pJ (E99's
`a44 - u4`), a carried one 3.2-3.3 pJ (half on the mesh rail, about 1.3 pJ off every rail), the 64-bit path 0.71 pJ and
the 256-bit path 2.38 pJ a bit, a channel's line-to-line changes +0.29-0.31 W, one bit a line +0.11 W over zeros (on the
cache-memory rail). Nothing with designed data has run on the write side: only the catalogue's tensor store of zeros,
one constant and random floats. This request builds on those runs and does not repeat them beyond what the tie needs:
it (i) re-runs E99's tent, lane, toggle, one-bit and random images on reads in the same session (the tie, and
same-session read prices for every write/read comparison), (ii) mirrors them for writes, with the write side's width and
channel images and E99's lane/beat pair as the write-inversion test, (iii) runs zeros, 0x0F and random lines at half the
line rate in both directions, with three no-traffic controls for the zero line.

A line of zeros is a special case: the shire cache keeps a zero state per line (the public lab repo's research page
`docs/reports/data/2026-09-27-chip-diagram/research/research-inside.md`, from the open shire-cache specification: a fill
or full-line write of an all-zero line sets the tag state's zero bit and does not write the data arrays, and a later read
does not read them). So every zeros arm skips the L2/L3 data arrays, and a line that is not all zeros pays a floor that
E99 measured at about 0.1 W on reads. This request reports the zero line and "any line" = the zero line plus that floor.

## 2. Arms

All arms: hart 0 of all 1,024 minions; each hart on its own slice of DRAM (reads 128 KB, writes 256 KB a hart: 128 and
256 MB in all, eight times the L3). Flat out = the catalogue's access loops: reads one 32 B `flw.ps` a line at a stride
of 64 through the L1 (`flw_pat`), writes one 512 B tensor store of f0..f15, eight stores then a wait (`tstore_raw`).
Paced = one access, then the cycle counter is read until the next slot: reads one line per 1,024 cycles a hart, writes
one 512 B store (8 lines) per 8,192 cycles a hart: 0.600e9 lines a second either way at 600 MHz, about half of flat out.
Minion m starts its slot grid (m x period)/1024 cycles into the launch, so the chip's accesses are spread evenly over
each period (not issued together after the launch barrier). Within a direction and a rate every arm runs the same
instructions on the same addresses; only the data differ.

Designed counts per line (`make_x09.py`, recomputed from the host's own bytes by `--check`; the lab's E99 conventions):
w raw ones; hi pins driven high after inversion (DC rule: min(p, 9 - p) per byte of p ones, inversion pin included);
t_enc pin toggles inside the line and tx_enc across its boundary, after inversion (raw: t_raw + tx_raw); p64 bits
changed between consecutive 8-byte pieces inside the line, x64 across; half bits differing between the 32 B halves, x256
across (second half to the next first half); k_chan bits changed between consecutive lines of one channel (two
independent draws from the lines that channel carries: a designed count, not a measured one).

| arm | access | image (every line) | w | hi | t_enc + tx_enc (raw) | p64 + x64 | half + x256 | k_chan | control |
|---|---|---|---|---|---|---|---|---|---|
| `rd.z` | read, flat | zeros | 0 | 0 | 0 | 0 | 0 | 0 | - |
| `rd.w1` | read, flat | byte 0 = 0x01, the rest zeros | 1 | 1 | 1 + 1 | 1 + 1 | 1 + 1 | 0 | `rd.z` |
| `rd.u2` | read, flat | every byte 0x03 | 128 | 128 | 0 | 0 | 0 | 0 | `rd.z` |
| `rd.u4` | read, flat | every byte 0x0F | 256 | 256 | 0 | 0 | 0 | 0 | `rd.z` |
| `rd.u7` | read, flat | every byte 0x7F | 448 | 128 | 0 | 0 | 0 | 0 | `rd.z` |
| `rd.u8` | read, flat | every byte 0xFF | 512 | 64 | 0 | 0 | 0 | 0 | `rd.z` |
| `rd.l08` | read, flat | bytes 00 FF 00 FF ... (lanes constant) | 256 | 32 | 0 | 0 | 0 | 0 | `rd.z` |
| `rd.a44` | read, flat | beats 0x0F, 0xF0 (bytes 0F 0F F0 F0 ...) | 256 | 256 | 496 + 16 | 0 | 0 | 0 | `rd.z` |
| `rd.rnd` | read, flat | random, every line distinct | 255.9 | 209.1 | 257.8 + 8.3 | 224.1 + 32 | 128.0 + 128.0 | 255.3 | `rd.z` |
| `wr.z` | write, flat | zeros | 0 | 0 | 0 | 0 | 0 | 0 | - |
| `wr.w1` | write, flat | byte 0 = 0x01, the rest zeros | 1 | 1 | 1 + 1 | 1 + 1 | 1 + 1 | 0 | `wr.z` |
| `wr.u2` | write, flat | every byte 0x03 | 128 | 128 | 0 | 0 | 0 | 0 | `wr.z` |
| `wr.u4` | write, flat | every byte 0x0F | 256 | 256 | 0 | 0 | 0 | 0 | `wr.z` |
| `wr.u7` | write, flat | every byte 0x7F | 448 | 128 | 0 | 0 | 0 | 0 | `wr.z` |
| `wr.u8` | write, flat | every byte 0xFF | 512 | 64 | 0 | 0 | 0 | 0 | `wr.z` |
| `wr.l08` | write, flat | bytes 00 FF 00 FF ... (lanes constant) | 256 | 32 (256 if not inverted) | 0 (0) | 0 | 0 | 0 | `wr.z` |
| `wr.a08` | write, flat | beats 0x0000, 0xFFFF (bytes 00 00 FF FF ...) | 256 | 32 (256) | 62 + 2 (496 + 16) | 0 | 0 | 0 | `wr.z` |
| `wr.a44` | write, flat | beats 0x0F, 0xF0 | 256 | 256 | 496 + 16 (the same) | 0 | 0 | 0 | `wr.z` |
| `wr.p64` | write, flat | 8-byte pieces 0x0F, 0xF0 | 256 | 256 | 112 + 16 | 448 + 64 | 0 | 0 | `wr.z` |
| `wr.h256` | write, flat | halves 0x0F, 0xF0 | 256 | 256 | 16 + 16 | 64 + 64 | 256 + 256 | 0 | `wr.z` |
| `wr.c44` | write, flat | 0x0F lines (even minions), 0xF0 lines (odd) | 256 | 256 | 0 + 8 | 0 + 32 | 0 + 128 | 256 | `wr.z` |
| `wr.rnd` | write, flat | random, each minion its own 512 B | 256.3 | 209.3 | 258.2 + 8.3 | 224.2 + 32 | 128.1 + 128.0 | 255.7 | `wr.z` |
| `rdh.z` | read, paced | zeros | 0 | 0 | 0 | 0 | 0 | 0 | `rdh.l1` |
| `rdh.u4` | read, paced | every byte 0x0F | 256 | 256 | 0 | 0 | 0 | 0 | `rdh.z` |
| `rdh.rnd` | read, paced | random | 255.9 | 209.1 | 257.8 + 8.3 | 224.1 + 32 | 128.0 + 128.0 | 255.3 | `rdh.z` |
| `rdh.l1` | paced read loop, one L1 line | (no memory traffic) | - | - | - | - | - | - | - |
| `wrh.z` | write, paced | zeros | 0 | 0 | 0 | 0 | 0 | 0 | `wrh.scp`, `wrh.nst` |
| `wrh.u4` | write, paced | every byte 0x0F | 256 | 256 | 0 | 0 | 0 | 0 | `wrh.z` |
| `wrh.rnd` | write, paced | random | 256.3 | 209.3 | 258.2 + 8.3 | 224.2 + 32 | 128.1 + 128.0 | 255.7 | `wrh.z` |
| `wrh.scp` | paced write loop into the own scratchpad | (no DRAM traffic) | - | - | - | - | - | - | - |
| `wrh.nst` | the paced write loop, its store replaced | (nothing stored) | - | - | - | - | - | - | - |

The read images are E99's bytes (`dm_w1`, `dm_u2`, `dm_u4`, `dm_u7`, `dm_u8`, `dm_l08`, `dm_a44`, and random lines), so
the read arms tie the session to E99 item by item. The write ladder: `u4 -> a44 -> p64 -> h256` adds pin toggles, then
the 64-bit words, then the 256-bit words; `c44` is the channel step; the tent `w1, u2, u4, u7, u8, l08` separates ones
from high pins. **Write inversion** is decided by E99's lane/beat pair, written: `l08` and `a08` have equal ones and
equal high pins whether inversion is on or off, and differ by 64 encoded pin toggles if it is live (the two inversion
pins alone toggle) or 512 if it is not; `a44 - u4` is 512 toggles either way, so
`Q = (a08 - l08) - (a44 - u4)/2` is -192 toggle prices if inversion is live and +256 if not, whatever a written pin or
toggle costs. On the chip every word of 32 bits or more is constant in both images. With inversion live, `u4 - l08` is
224 high pins at equal ones with no toggle anywhere: the price of a high pin-beat, the same estimator in both
directions. `K = (u8 - u7) - (u4 - u2)/2` (-128 high-pin prices if inverted) is a second estimate. The paced zeros arms
against `rdh.l1` (an L1 hit in the same loop) and against `wrh.scp` (the same store into the minion's scratchpad) and
`wrh.nst` (the same loop, instruction for instruction, with the tensor store replaced by a write of zero to the
floating-point flags: nothing stored) give the zero line at a rate where every core polls the clock in all arms. The
scratchpad store writes its array (the zero state is a cache tag-state bit; whether the scratchpad also skips zero
rows is open), so `wrh.z - wrh.scp` and `wrh.z - wrh.nst` bracket the write zero line, and
`wrh.scp - wrh.nst` is the scratchpad store itself.

`x09mem_host --list` prints the table; `--item NAME` runs an arm; `--mode --image --period` runs any other.

## 3. Cores, harts, card, clock

Hart 0 of all 32 x 32 minions (only hart 0 may issue tensor stores; the reads match it, as E75-E99 ran `flw_pat` with
one hart). **The card E75-E139 ran on (pinned at 600 MHz by its boot service, lock `shire0`)**, the lab's reference
card for these memory runs. One card only: the host refuses to run on a host with more than one card node. No change
of voltage, frequency, firmware, governor or fan; no root.

## 4. What is measured, and how

The public lab repo's runner, unchanged, and its block library with the changes its own E180 and E183 blocks make
(`src/block_x09.sh` is `tools/claims-v3/mf/block.sh` with this host and manifest, every telemetry call through the
lab's E128 guard and the block library's drain of the management queue refused: `src/lib_x09.sh`; `src/session_x09.sh`
its E139 session and queue with the E183 session's gates; the lab session's own kit may replace both): per pass one
block under the card lock, with its own sampler (10 Hz: board, the three rails with volts, the DDR die reading, clock,
die sensors), started and stopped with SIGTERM by the block (the library kills a sampler that ignores it for 30 s; no
drain follows); per run the approach (heater bursts to 59 C, launch at 58 C), one device process under `timeout 10`,
0.4 s launches back to back for 4 s; per pass two burn-in runs, the drift anchor `anchor_pi` first and last, the 31
items shuffled by `card|seed|pass`.

**Reduction, registered before any datum** (`src/reduce_x09.py`, its sha256 registered with the forecast's; its
self-test on synthetic data `src/selftest_x09.py` PASSES: the pipeline, and every verdict's reach under its null and its
alternative at the lab's own pass-to-pass scatter): E75-E99's estimator. Board power over seconds 1-3 of the run, dips removed (a sample more than
4 W below both samples two away: E82 A2), corrected to the launch reading with the `auto` leakage slope. Rails over
seconds 2-4, raw, within-pass differences divided by 0.94. Rate: lines (or accesses, for the controls) completed inside
the board window, by overlap. Run gates: one clock in every window sample, the launch on protocol, every launch record ok
and reporting 1,024 participants, minion-rail volts within 3 mV of the pass median, the window's median sampler time at
most 60 ms; a pass with anchor drift above 0.3 W or a third of its runs failing a gate is set aside. Every contrast a
within-pass difference; mean over the headline passes with a two-sided t interval; a price computed pass by pass, then
the same; a ratio of two prices from the ratio of their means with a delta-method interval over the passes (the
covariance within a pass included). Off the metered rails = board less the three rails, and less the rails' in-step
losses (the lab's fitted 0.181, 0.043, 0.294 for this card). Electrons per line = energy / (e V): at 12 V for the board,
at each rail's voltage for that rail. The reduction is run four times in one call: the primary (dips removed, `auto`),
0.2936 and 0.3803 W/C (dips removed) and unfiltered (`auto`); every verdict that differs from the primary is named.

**Prices, pass by pass, in one convention** (registered): a pin toggle is every encoded toggle on the pins, inside the
line and across its boundary; the wide paths are priced on changes inside the line only; the changes at a line's edge on
those paths belong to the channel step. The figures with both edges charged are reported beside.
- high pin-beat: `u4 - l08` over 224 (both directions); also from K over -128, and the tent's joint fit (reported);
- one: `u7 - u2` over 320 (equal pins if inverted; both directions); also the 2x2 solve with `u4 - u2` (reported);
- pin toggle: `a44 - u4` over 512 (also over 496, inside the line only), on the board and off the rails;
- the floor of a line that is not zero: `w1 - z` less one one, one pin and two toggles (both directions);
- writes: the 64-bit path `(p64 - u4 - 128 toggles) / 448`; the 256-bit path `(h256 - u4 - 32 toggles - 64 64-bit
  bits) / 256`, on the board and off the metered rails (the h256 image's 32 B store rows alternate on the chip); the
  channel step `(c44 - u4 - 8 toggles) / 256` per designed k_chan bit, all of it, off the rails and on the mesh rail;
- write inversion: `Q` (W) and `(a08 - l08) / (a44 - u4)` (0.125 if live, 1.0 if not);
- random lines less floor, ones, pins and toggles (and, written, the paths and the channel step);
- the zero lines: `rdh.z - rdh.l1`, `wrh.z - wrh.scp`, `wrh.z - wrh.nst`, a line; any line = each plus the floor;
- the rate ratio: pJ a line paced over flat, for 0x0F and random lines, both directions;
- write over read for every price and image both directions have.

## 5. Rates, joules per event, and the signal budget

Rates: flat reads 1.173e9 lines a second (E99's `flw_pat` on this card, measured); flat writes about 1.19e9 (the
catalogue's tensor store, 76 GB/s); paced 0.600e9 (set by the clock); measured per run. At 1.17e9 lines a second
1 pJ a line is 1.2 mW; at 0.6e9, 0.6 mW.

Sizing (not the forecast: the lab's own read prices on these images, the write side assumed to cost what the read side
costs), and the 95 % half-width at **7 headline passes** from E99's measured pass-to-pass scatter of the same shape (the
same card, harness and estimator; two-item contrasts 0.064-0.12 W a pass):

| statistic | sizing | 95 % half-width, 7 passes | decides |
|---|---|---|---|
| `u7 - u2` (320 ones, equal pins) | +1.21 W | 0.11 W | the one (R3) |
| `u4 - l08` (224 high pins, equal ones) | +0.39 W | 0.07 W | the pin (R1b, R2) |
| `a44 - u4` (512 toggles) | +0.48 W | 0.06 W | the toggle (R4), Q's scale |
| `Q = (a08 - l08) - (a44 - u4)/2` | -0.18 W if inversion is live, +0.24 W if not | 0.13 W | R1 |
| `a08 - l08` (64 or 512 toggles) | +0.06 W live, +0.48 W not | 0.13 W | (Q's leg) |
| `K = (u8 - u7) - (u4 - u2)/2` | -0.20 W | 0.05 W | R1's second path, a second pin |
| `w1 - z` (the floor) | +0.11 W | 0.05 W | the floor, any line |
| `u8 - u7` | +0.16 W | 0.05 W | (reported) |
| `p64 - u4` | +0.50 W (+0.12 W of it toggles) | 0.07 W | R5 |
| `h256 - u4` | +0.81 W (about +0.08 W if the 256-bit path is the read side's own) | 0.08 W | R6 |
| `c44 - u4` | +0.31 W | 0.07 W | R7 |
| paced `u4`, random over paced zeros | +0.79, +1.77 W | 0.08, 0.05 W | R8b, R8 |
| paced zero lines over their controls | about +3 W | 0.07 W | R9, R10 |
| `wrh.scp - wrh.nst` (the scratchpad store) | at most +0.18 W (the catalogue's 298 pJ a line with its loop) | 0.07 W | (reported) |

Power of the registered verdicts at the sizing: the chance of the verdict its scenario implies, first with E99's
measured scatter of each shape (a normal approximation), then the share of the self-test's synthetic sessions (a more
conservative model: items independent at 0.056 W flat and 0.063 W paced, 100 sessions a scenario): R1 LIVE about 1.0 (0.87 by Q alone; K's path catches the rest) / 1.00, OFF 0.99 / 1.00;
R1b TERMINATED and SMALL about 1.0 / 1.00; R2 SAME 0.57 / 0.52 (the pin ratio is the weakest: about +-0.26); R3 SAME
0.99 / 1.00; R4 SAME 0.95 / 0.82; R5 PAYS about 1.0 / 1.00, FREE 0.94 / 0.97; R6 BOTH about 1.0 / 1.00, READS ONLY 0.88
/ 0.86; R7 PAYS about 1.0 / 1.00, FREE 0.89 / 0.85; R8 PER LINE, each random leg, about 1.0 / 0.63-0.74, RATE-DEPENDENT
(1.25 times) about 1.0 / 0.98-1.00; R8b PER LINE (0x0F, +-20 %) 0.92. Every arm lifts the card 2-11 W over rest (about
37 W at most); the heater's bursts reach about 54 W.

## 6. Denominators

Per hart: cycles (`hpmcounter3`), loop iterations, accesses, polls while waiting for a slot and late slots (paced);
lines by construction (one a load, eight a store). Per neighbourhood (one record each): thread-0 instructions retired
(`hpmcounter4`) and L1 miss requests (`hpmcounter6`) before and after the loop. The memory shires' mesh read and write
request counters (the open SDK's `SYSCALL_PMC_MS_SAMPLE`, the firmware's default setup: reads and writes from all
sources), sampled by hart 0 of shire 0 before and after its loop. The clock from the sampler. The registered checks of
these (section 7, C1-C6) are computed by the reducer.

**In the open emulator** (the open system emulator, the same kernel ELF and host source with the emulator's device layer, shire
0, minions 0 and 1, one launch per arm; reads over a 4 KB region, writes over the card's 256 KB so that no line is
stored twice in an emulated launch, which the emulator's coherence checker refuses as a coalescing-buffer rewrite before a
drain; windows 20,000 cycles flat reads, 2,000 flat writes, 100,000 paced). The emulator models no caches and no timing:
its cycles are not the card's, its counters for misses and memory shires read 0. Checks: every read fill read back
exact; every write's stored bytes equal the minion's image over the extent written, and memory beyond it untouched
(CRC of hart 0's slice); no late slot. Instructions per access by construction (`check_elf.py`): flat read loop 33 an
iteration of 8 loads (4.1 a line), flat write loop 43 an iteration of 8 stores (5.4 a store), the paced store loop and
the store-free loop 29 each (equal but for the access), the paced read loop 24, then polls of the cycle counter.

| arm | harts | iterations a hart | accesses a hart | lines a hart | cycles | late slots | data check |
|---|---|---|---|---|---|---|---|
| `rd.z` | 2 | 604 | 4832 | 4832 | 20023 | 0 | fill read back exact |
| `rd.w1` | 2 | 604 | 4832 | 4832 | 20023 | 0 | fill read back exact |
| `rd.u2` | 2 | 604 | 4832 | 4832 | 20023 | 0 | fill read back exact |
| `rd.u4` | 2 | 604 | 4832 | 4832 | 20023 | 0 | fill read back exact |
| `rd.u7` | 2 | 604 | 4832 | 4832 | 20023 | 0 | fill read back exact |
| `rd.u8` | 2 | 604 | 4832 | 4832 | 20023 | 0 | fill read back exact |
| `rd.l08` | 2 | 604 | 4832 | 4832 | 20023 | 0 | fill read back exact |
| `rd.a44` | 2 | 604 | 4832 | 4832 | 20023 | 0 | fill read back exact |
| `rd.rnd` | 2 | 604 | 4832 | 4832 | 20023 | 0 | fill read back exact |
| `wr.z` | 2 | 46 | 368 | 2944 | 2020 | 0 | 188416 B stored = image, rest untouched |
| `wr.w1` | 2 | 46 | 368 | 2944 | 2020 | 0 | 188416 B stored = image, rest untouched |
| `wr.u2` | 2 | 46 | 368 | 2944 | 2020 | 0 | 188416 B stored = image, rest untouched |
| `wr.u4` | 2 | 46 | 368 | 2944 | 2020 | 0 | 188416 B stored = image, rest untouched |
| `wr.u7` | 2 | 46 | 368 | 2944 | 2020 | 0 | 188416 B stored = image, rest untouched |
| `wr.u8` | 2 | 46 | 368 | 2944 | 2020 | 0 | 188416 B stored = image, rest untouched |
| `wr.l08` | 2 | 46 | 368 | 2944 | 2020 | 0 | 188416 B stored = image, rest untouched |
| `wr.a08` | 2 | 46 | 368 | 2944 | 2020 | 0 | 188416 B stored = image, rest untouched |
| `wr.a44` | 2 | 46 | 368 | 2944 | 2020 | 0 | 188416 B stored = image, rest untouched |
| `wr.p64` | 2 | 46 | 368 | 2944 | 2020 | 0 | 188416 B stored = image, rest untouched |
| `wr.h256` | 2 | 46 | 368 | 2944 | 2020 | 0 | 188416 B stored = image, rest untouched |
| `wr.c44` | 2 | 46 | 368 | 2944 | 2020 | 0 | 188416 B stored = image, rest untouched |
| `wr.rnd` | 2 | 46 | 368 | 2944 | 2020 | 0 | 188416 B stored = image, rest untouched |
| `rdh.z` | 2 | 98 | 98 | 98 | 100371 | 0 | fill read back exact |
| `rdh.u4` | 2 | 98 | 98 | 98 | 100371 | 0 | fill read back exact |
| `rdh.rnd` | 2 | 98 | 98 | 98 | 100371 | 0 | fill read back exact |
| `rdh.l1` | 2 | 98 | 98 | 0 | 100370 | 0 | fill read back exact |
| `wrh.z` | 2 | 13 | 13 | 104 | 106522 | 0 | 6656 B stored = image, rest untouched |
| `wrh.u4` | 2 | 13 | 13 | 104 | 106522 | 0 | 6656 B stored = image, rest untouched |
| `wrh.rnd` | 2 | 13 | 13 | 104 | 106522 | 0 | 6656 B stored = image, rest untouched |
| `wrh.scp` | 2 | 13 | 13 | 0 | 106522 | 0 | scratchpad (no slice) |
| `wrh.nst` | 2 | 13 | 13 | 0 | 106523 | 0 | stores nothing (no slice) |

The three paced write arms `wrh.z`, `wrh.scp` and `wrh.nst` polled the cycle counter 26,557 times in their 26
slots and retired 209,276-209,281 thread-0 instructions: the same loop but for the access, as C2 checks on the card.

## 7. Rules, registered before any datum (`reduce_x09.py`)

Every verdict is read from an interval (95 %, t over the headline passes); with fewer than 5 headline passes every scored
verdict is UNRESOLVED.

| rule | test | reading |
|---|---|---|
| R0 tie | `rd.u2`, `rd.u4`, `rd.u7`, `rd.u8`, `rd.l08`, `rd.a44`, `rd.rnd` over `rd.z`, pJ a line, within +-12 % of E99's 697, 1314, 1716, 1853, 985, 1719, 2955 | TIED, else NOT TIED (the session's read prices then stand beside E99's); `rd.w1` reported against E99's 95 pJ |
| R1 write inversion | Q = (a08 - l08) - (a44 - u4)/2 | LIVE: interval below 0; OFF: above 0; else LIVE (tent) if K's interval lies below -0.10 W (labelled: a response to ones bent enough could mimic it); else UNRESOLVED |
| R1b written high pin | `(u4 - l08)/224`, given R1 LIVE | TERMINATED: low end at or above 0.7 pJ (about half the read side's 1.47); SMALL: high end below 0.7; else UNRESOLVED; NOT SEPARABLE if R1 is OFF (ones and pins then coincide on the write images: one + pin priced) |
| R2 high pin | write / read pin price, given R1 LIVE | SAME: interval inside 0.7-1.4; WRITE HIGHER: above; WRITE LOWER: below; else UNRESOLVED |
| R3 one | write / read price of a one, given R1 LIVE | SAME inside 0.75-1.33; HIGHER / LOWER outside; else UNRESOLVED |
| R4 toggle | write / read price of a pin toggle | SAME inside 0.7-1.4; HIGHER / LOWER outside; else UNRESOLVED |
| R5 64-bit path, writes | the 64-bit price beyond the pin toggles, pJ a bit | PAYS: low end above 0.25; FREE: interval inside +-0.25; else UNRESOLVED |
| R6 256-bit path, writes | the 256-bit price beyond the toggles and the 64-bit path, off the metered rails | BOTH DIRECTIONS: low end >= 1.0 pJ; READS ONLY: high end < 0.4 pJ; else UNRESOLVED |
| R7 channel, writes | the price a designed k_chan bit beyond the pin toggles | PAYS: low end above 0.40 pJ; FREE: inside +-0.40; else UNRESOLVED. k_chan = 256 is the independent-draws count over minions: each minion's own stream is constant, so the real count depends on how the memory path interleaves different minions' lines (strict alternation would give up to 512, batching per source less than 256): the price carries that factor |
| R8 rate (random lines) | pJ a line paced / flat, both directions | PER LINE: interval inside 0.9-1.1; RATE-DEPENDENT: entirely outside; else UNRESOLVED; a leg whose paced arm has more than 1 % late slots is UNRESOLVED |
| R8b rate (0x0F) | the same for 0x0F lines | PER LINE inside 0.8-1.2; RATE-DEPENDENT entirely outside; else UNRESOLVED (reported) |
| R9 zero line, reads | `rdh.z - rdh.l1`, a line; any line = it plus the read floor | reported |
| R10 zero line, writes | `wrh.z - wrh.scp` and `wrh.z - wrh.nst`, a line (the bracket); any line = each plus the write floor; `wrh.scp - wrh.nst` | reported |
| R11 closure | random lines less floor, ones, pins and toggles (written: and the paths and the channel) | reported |
| R12 locator | the DDR die reading on `p64 - u4`, `h256 - u4`, `a44 - u4` (both), `a08 - l08`, `c44 - u4`, random lines (both), `u7 - u2` (both) | E110's classes: moves (mean <= -0.30 mV and interval below 0), still (inside +-0.30 mV), else unresolved; reported |

**Sanity checks** (registered; each PASS, FAIL with the arms it names, or NO DATA): C1 thread-0 instructions an access
equal across the flat arms of a direction (within 0.5 % of its zeros arm); C2 polls a slot equal across the paced arms of
a direction, controls included (within 2 %: a core that waited on a miss would poll less); C3 late slots at most 1 % of a
paced arm's slots; C4 the line rate of every memory arm within 0.5 % of its zeros arm (a slower arm is named); C5 L1
misses one a load on the read arms (0.95-1.05), none on the writes and on `rdh.l1` (at most 0.01 an access); C6 the
memory shires' counts: reads 0.9-1.1 a line and writes at most 0.05 a line on the read arms, writes 0.9-1.1 a line and
reads at most 0.05 a line on the write arms (no read before a full-line store). If the counters are not read
(`--no-ms`), C6 is NO DATA and every write price is labelled as assuming that a full-line store reaches memory once,
unread. A FAIL does not remove data; the verdicts it touches are read with it.

**Scored against the sealed forecast** (frozen before any datum and never published; its sha256 is in the proposal):
`reduce_x09.py --forecast <the forecast>` reports, for each price the forecast names, which of its two methods'
5-95 % bands holds the measured mean (one, the other, both, neither).

## 8. The session

The lab session runs it in its own tree, with its own kit or `src/session_x09.sh` (a port of its E139 session and
queue, with its E183 session's gates); or the operator runs it, in a window the lab session names, from a folder of its
own laid out as the lab's tree (`src/BUILD.md`: this `src/` at `tools/claims-v3/x09/`, beside copies of the lab's
public `lib.sh`, `runitems.py`, `text_hash.sh`, `dmcmd_audit.py` and `e128/ettelem_guard.sh`, with the reader and the
heater built there). Either way everything is written under that tree's `build/`, and the block and the session refuse
unless `X9_ROOT` is that tree's absolute path. The generator `make_x09.py` needs numpy: run it at a desk and copy `build/x09-gen`
(generic counts; the same bytes under numpy 1.26 and 2.5), or in the tree's environment (`lib.sh` adds it); the reducer
runs at a desk.

1. Build in the tree (`src/BUILD.md`): `cmake`, `check_elf.py` OK, `x09mem_host --list`, `make_x09.py build/x09-gen
   --host ... --check` OK. Look: `et-who`, `who`, `uptime`, `et-usage --since 30m`; `preflight_x09.sh` (the lab's
   device-command audit on every file the session runs) reads GO; `X9_ROOT=<tree> V3_DRY=1 bash block_x09.sh 910`
   prints every device call and opens nothing.
2. The session refuses before any device opens without the window of the day's go (`X9_LATEST_START`, after which no
   session starts, and `X9_DEADLINE`), with a `USER` that is not this login, with a stop file present, or unless the
   device-command preflight reads GO.
3. `et-who` and a read of `ettelem config` through the lab's E128 guard (read only, under the card lock, `timeout 10`,
   and only while `et-who --check` reads the card free), at both ends of the session.
4. The board-power watcher (`watch_x09.py`, telemetry files only): a stop when the board reads 70 W or more on three
   samples in a row (it writes the pass's STOP file and the session's, `build/x09-STOP`, which every item's host also
   watches: no launch starts once it exists). The runner's die stop at 70 C (`X9_MAX_C`, set to 70). No block starts
   while the watcher is not running; the queue stops before a pass on `build/x09-STOP` or `build/claims-v3/STOP`.
5. **Smoke pass 901**: `anchor_pi`, `x9_rd_rnd`, `x9_wr_u4` (a flat write: writes are new on this meter), `x9_wrh_rnd`
   (paced), `x9_wrh_nst` (the store-free loop), about 1.5 card-minutes. **Gate** (`smoke_gate_x09.py`, E110's gate and
   three of this request's run gates): `block.json` ok; every item launched with ok records and lines moved; every
   launch with 1,024 participants; the memory shires' counters read on the memory arms (not asked of items the runner
   ran with `--no-ms`); the median sampler time over each run at most 60 ms; every telemetry sample with the three rails
   and the DDR die reading. A failed gate runs no pass.
6. **Passes 910-917**, one block each, 15 s apart; 910 is the registered warm-up and never in the headline (the
   reducer's `--warmup 910`). No pass starts once the session has run 38 minutes, or when the longest pass so far (360 s
   until one has run) and 60 s for the close would end after `X9_DEADLINE`; a pass in flight is never cut; a pass that
   fails ends the queue. A pass the reducer sets aside is not replaced. Fewer than 5 headline passes: every scored
   verdict UNRESOLVED.
7. Data: the block library writes each pass under the tree's `build/claims-v3/<card>/x09/p<pass>/` (`runs.jsonl`,
   `marks.jsonl`, `run.log`, `telemetry.jsonl.gz`, `configs.json`, `manifest.txt`, `gen.sha256`; `text.sha256`: the
   host, the heater and the kernel ELF the host launches, file and disassembly; `code.sha256`: every source file of the
   run, the manifest and the binaries); one sampler a pass, never two at once. The record goes to the public repo as the
   lab's own runs do (source, protocol, raw meter data; nothing else).

## 9. Box and card constraints; what must not be done

- Nothing opens a card node until the card is free (the block's holder check, against this login, and the lock; the
  host's own one-card check before opening, which refuses on a host with more than one card node; the session's config
  reads only while `et-who --check` reads the card free). The sampler is stopped with SIGTERM (the block library kills
  one that ignores it for 30 s). No management command is sent beyond the E128 guard's reads (`ettelem config`,
  `ettelem sample --seconds --every-ms`): the block library's drain of the management queue is refused.
- Each device process under `timeout 10`; the host starts no launch unless it would end inside its 8.5 s budget (one
  that hangs is cut by its 3 s stream wait, or at the latest by the timeout).
- Live stops: die mean at or above 70 C (the runner); board at or above 70 W on three readings in a row (`watch_x09.py`;
  the heater's highest bursts are about 54 W on this card).
- No change of voltage, clock, firmware, governor, fan; no `et-reset`, no root, no other user's process. The memory
  shires' counters are read through the documented user-mode system call (which stops, reads and restarts a counter);
  `--no-ms` drops it (C6 is then NO DATA).
- Never in the lab session's other trees or build folders (`X9_ROOT` names the one tree written to); no host compute
  beside the run; no simulation on the lab box.
- The session itself checks the login, the device-command audit (GO) and the window it is given. To be supplied by the
  lab session, as for its own runs: the rest rule on this card, the day's go and its window, and the check that the
  files run are the ones registered. Every holder check in this kit passes this login's own processes, and the operator
  and the lab session work under one login: only the agreed window keeps the two sessions apart.

## 10. Card time

35 device processes a pass (31 items, the anchor twice, two burn-ins). At the measured per-process times of the
comparable runs on this card with this harness (E99 7.6 s, E139 8.3 s, E110 about 9 s, E132 about 9.8 s, approach
included) a pass is 4.4-5.7 minutes, 5.1 with the 15 s gap at E139's pace. Smoke and the config reads about 2 minutes;
8 passes (1 warm-up and 7 headline) about 41 minutes: **about 43 card-minutes (40-44)**, never more than 45 (the
38-minute stop: at E132's pace it ends after 7 passes, 6 headline), and never past the window's deadline. Wall time
1-2 h. A shorter variant, if card time is scarce: passes 910-915 (5 headline), about 33 card-minutes.

## 11. Status and open points

- Builds with the open SDK (kernel and host; `src/` card-only); `check_elf.py` OK (five loops); `make_x09.py --check`
  OK on all 31 arms from the host's own bytes; the emulator has run every arm (section 6); the reducer's self-test
  PASSES (both parts); the session kit passes a desk test on a stand-in tree (section 12); the device-command preflight
  reads GO; the name scan of `src/` prints HITS 0; the forecast is frozen.
- Every image is generic (byte values, run lengths, a parity mix, random lines); the counts follow the public
  standard's inversion rule.
- Whether the memory shires' counters are read is the lab session's call: `make_x09.py --no-ms` makes a manifest whose
  items all run without them (the smoke gate then does not ask for them; C6 is NO DATA).
- Optional, if card time allows (not in the budget): a 32-bit-piece write image (`--mode wr --image alt:0f:f0:4`, a
  0/256/512 toggle ladder); a read channel step in the same session (`--mode rd --image par:0f:f0`: by bit 4 of the line
  index, E132's address rung).

## 12. Revision log

- **Revision 1** (Sat 14 Nov): 24 arms; the forecast frozen.
- **Revision 2** (the same day, before any datum; the forecast frozen again, the hash in the proposal): the
  write-inversion test by toggles (`wr.l08`, `wr.a08`); the pin from `u4 - l08` on both sides (`rd.l08`) and K on both
  (`rd.u8`); the floor (`rd.w1`, `wr.w1`) and "any line"; the store-free write control (`wrh.nst`); the paced arms'
  slots spread over each period; intervals behind every verdict; one price convention; the sanity checks in the
  reducer; the session (section 8); the one-card check without any device-selection variable.
- **Revision 3** (the same day, after a line-by-line read of revision 2's source; before any datum). The arms, the
  host, the kernel and the forecast are unchanged (the host and kernel ELF rebuild byte for byte; the emulator reran all
  31 arms with the counts of section 6). Changed, in the kit:
  - Device commands: every telemetry call goes through the lab's E128 guard and the block library's drain of the
    management queue is refused, as in the lab's E180 v2 and E183 v3 blocks (`src/lib_x09.sh`); the block's preflight
    requires the guard and the reader; the session's config reads go through the guard. Before, a sampler that failed
    to start twice, or ignored SIGTERM for 30 s, led the library to send its drain.
  - The holder test compares each holder with this login (`id -un`), never with `USER`: with `USER` unset it read no
    holder line. An unset `USER` is set to the login; a `USER` naming anyone else refuses.
  - The board-power watcher no longer ends when a pass's telemetry file goes between its listing and its read (a
    stress test killed the old one), logs any other error and goes on; the session starts no block while it is not
    running.
  - Each pass records the kernel ELF the host launches (file and disassembly, `text.sha256`) and every source file of
    the run, `host/` and `kernel/` included (`code.sha256`).
  - `--no-ms` through the kit: `make_x09.py --no-ms`, and the smoke gate reads each item's arguments from the runner's
    `configs.json`.
  - A clock window: `X9_LATEST_START` and `X9_DEADLINE` are required; the smoke and every pass start only if they end
    before the deadline.
  - The session's config reads only while `et-who --check` reads the card free.
  - The tree: `lib.sh` is taken only from beside the folder (no fallback to another tree), and the block and the
    session run only when `X9_ROOT`, an absolute path, names the tree they write into.
  - Also: the device-command preflight in the session (`src/preflight_x09.sh`: the lab's audit, GO); a stop file left
    from before refuses the session; every item gives the host the session's stop file; the generator's files no longer
    depend on numpy's version (the same bytes under numpy 1.26 and 2.5); `check_elf.py` also reads the tensor-store CSR
    by number; wording in the header and sections 2, 4, 6, 7, 8, 9, 10 and 11.
  - Desk-tested on a stand-in lab tree (copies of the lab's public files, a stand-in reader, no device): every change
    above, the block's dry run, and the session's refusals, deadline, dead-watcher stop and config reads.
  - Not taken: counting the host's 3 s stream wait in its launch budget. A 4 s run would then end early whenever
    opening the card took more than 0.5 s; the 10 s timeout stays the backstop.
