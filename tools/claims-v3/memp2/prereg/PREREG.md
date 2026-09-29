# memp2: pre-registration (hub rungs 33, 36, 43 and energy-manual-102)

**Status: DRAFT, written 28 September 2026 before any memp2 data; revised the same night after an adversarial
review, still before any data (the changes are listed under "Changes before any data").** Development on aifoundry1
card 1 may change the design; every change after development data is listed under "Development notes" below before
the freeze. The freeze (`python3 tools/claims-v3/memp2/memp2lib.py freeze --binaries <a development PROBE pass's
binaries.json>`) writes `LOCK.sha256` over this file and every file the blocks run (the shared framework files
included) plus the sha256 of the development kernel's `.text` section (the three hosts' RISC-V toolchains give
identical `.text`), records this file's SHA-256 in `prereg/PREREG.sha256`, and prints the SHA-256 of `LOCK.sha256`
itself. It refuses if a `LOCK.sha256` exists. Every pass on a validation card, its smoke included, refuses to start
unless `MEMP2_LOCK_SHA256` equals that printed value and every entry of `LOCK.sha256` verifies on that host (the
built kernel's `.text` included). The record of the freeze is that one value. A failed prediction is reported as
failed.

## Cards and roles

| Card | Role | Passes |
|---|---|---|
| aifoundry1 card 1 (fw 1.2.0, 600 MHz fixed) | development: iterate here only; its results are development results, not verdicts | 901 smoke; 101, 102 PROBE; 201, 202 ENERGY |
| aifoundry3 (fw 1.3.1, pinned 600 MHz) | validation | 911 smoke; 111, 112 PROBE; 211, 212 ENERGY |
| aifoundry2 (fw 1.3.1, governor free) | third card, only after the DV2 validation ends (about 17:00 PDT 29 Sep), heated to 76 C first | 912 smoke; 113, 114 PROBE; 213, 214 ENERGY |

Before any card time the main session runs `tools/claims-v3/memp2/sysemu.sh` (every new kernel path in `sys_emu`,
on aifoundry1 after the build; not on aifoundry2 while DV2 runs). On each card the smoke (9xx) goes first: a ladder
from one minion of shire 0 through the four op programs and one whole shire to the chip, stopped at the first stage
with any failure; a PROBE or ENERGY pass refuses to start unless an ok smoke on the same card ran the same kernel
file. The blocks run in order through `series.sh`, not `queue.sh` (whose die reading between blocks opens the
management node outside the card lock).

Each card's items are decided on that card's own validation passes; a theory **survives** if it holds on every
validation card that decided it. The unit of replication is the trial (R33, R36: fresh lines each), the launch over
32 shires (R43) and the catalogue replicate (E102), pooled over the card's two blocks of each kind.

## Sources of the predictions

`docs/et-soc1-notes.md` ("One memory access, taken apart"); `docs/research/counters-and-dram.md` §(d) (the address
map, open-page policy); the chip diagram's facts L50 (inferred map), `tl.one`, `tl.all`,
`minion.tensor-cache-path`; the memory levels' `facts-scp.json` (`scp.banks`, `scp.pipe-stages`, `scp.bw-spec-port`,
`scp.bw-one-neigh`, `scp.bw-bank-stride`); V3's MEM-P4 (sequential same row -11, other row +10, back-to-back
conflict +36.9 cycles on aifoundry2), MEM-P5 (refresh every 2,325.4 cycles, stalls up to 208), LAT-S2 (a lone
minion's 16-line TensorLoad stream: 160.4 cycles from the L2, 160.1 from the scratchpad, 748-751 from DRAM); E28;
E36; E45 ("stride-256 was not run"); E46 (`scpline/*` on three cards: 923 / 923 / 614 GB/s; random 6.64 / 6.48 /
7.33 pJ/B, zeros 4.16 / 4.34 / 4.91 pJ/B pooled); the energy manual §2 (an awake minion about 2 mW).

## R33: the DRAM address map (hub rung 33, exp-dram-rows)

The inferred map (L50): PA[8:6] memory shire, PA[9] controller (channel), PA[12:10] bank, PA[17:13] column,
PA[18+] row; open-page. The anatomy's one-bit flips (19 Sep, MEM-P4) already split column bits (13-17: same row) from
row bits (18+: conflict), but a flipped bank bit costs nothing there, like PA[9] and PA[6-8], so which low bits pick
the bank and which the controller is still read from the programmed map. Three programs, one hart (hart 0, shire 0),
every timed load from DRAM (lines evicted to memory first and each touched once per condition: the L3 is defeated per
line; E28's way, a touched set above 32 MB, does not fit a one-hart latency probe).

**R33a, rowalt (bank against row).** A 16-column walk of one row (A_j = A + j << 13) alternates with B_j = A_j ^ mask.
Same bank, other row: every access is a row conflict (precharge + activate); another bank, controller or memory
shire: both rows stay open and every access after the first is a row hit. d_c = median over trials of
(median A latency in condition c - the same trial's `row`), accesses j >= 1.
- *Prediction (L50):* no conflict (d_c < -10.5) for `col` (same row) and `row+6` ... `row+12`; conflict (d_c >= -10.5)
  for `rowc+13` ... `rowc+17` (another row plus a column bit), `row19`, `row+25`. The bank-bit step, median d over
  `row+10..12`, in [-27, -15] cycles (tRP + tRCD: MEM-P4's -11 and +10 give -21).
- *Rule:* PASS if all 15 conditions classify as predicted and the step is in its band; else FAIL. At least 12 trials.
- *What it cannot do:* separate a bank bit from a controller bit (both give row hits). R33b and R33c do that.

**R33b, refphase (the refresh domain by refresh phase).** Lines A and B = A ^ (1 << k), k in {6..13, 18}, three pairs per bit
(each from its own A), loaded alternately at random phases (jitter up to 3,000 cycles), 300 loads per line, each
stamped. A load stalled by a refresh (latency > line median + 40) gives the refresh's end e = stamp + latency -
median/2 (the path corrected). Fold every line's e at one fitted period P (2,322-2,329 cycles; expect 2,325.4); each
line's phase is its circular mean; dphi = phase(A) - phase(B) (wrapped to +-P/2). A pair reads "same" if |dphi| <= 60,
"different" if >= 150, else "unclear"; "insufficient" with fewer than 8 stalls or a resultant below 0.5 on either line.
A bit is "different" if at least half its valid pairs read different, "same" if at least 80% read same and none
different, else "unclear".
What the method sees is the **refresh domain**: the set of lines that share one refresh schedule. The bits that read
"different" are the refresh-domain bits; they name the controller only if each controller has its own timer.
- *Theory (predicted, "per-controller"):* each controller refreshes all its banks on its own schedule (all-bank
  refresh: a 208-cycle stall at 3.88 us, not a per-bank one), so lines on one controller share the phase; if the
  controllers' schedules are not synchronised, lines on different controllers do not.
- *Registered alternatives:* "per-memory-shire": the two channels of a memory shire share one refresh timer (PA[6-8]
  different, PA[9] and every other bit same); "per-bank": each bank refreshes on its own phase (MEM-P5's period
  cannot exclude it: each bank still refreshes once per tREFI), so PA[6-8] and the L50 bank bits PA[10-12] read
  different; "lockstep": every controller at one phase (nothing reads different). Any other pattern is "other".
- *Prediction (L50, per-controller, unsynchronised):* PA[6], PA[7], PA[8] and PA[9] different; PA[10], PA[11],
  PA[12], PA[13] and PA[18] same.
- *Rule:* INSUFFICIENT if none of PA[6-8] reads different (lockstep refresh, or the method cannot see controllers);
  otherwise PASS if the pattern is "per-controller"; else FAIL, and the reading names the refresh-domain bits and
  which alternative they fit. A "same" for PA[9] ("per-memory-shire") does not by itself refute PA[9] as the channel
  bit: the reading says so and reports R33c's PA[9] delta beside it.

**R33c, rrd (sharing a controller, back to back).** Rows C = A ^ (1 << 19) and D = B ^ (1 << 19) are opened first, so
A and B both find another row open. `ab`: A issued, B one cycle later, timed to B's arrival; `b`: B alone from the same
state. Delta_k = median over trials of (ab - b), paired by trial.
- *Theory:* two accesses to one channel serialise their activates (tRRD >= 10 ns, about 6 cycles at 600 MHz) and the
  command bus; two controllers do not.
- *Registered alternative:* if PA[11] (or PA[12]) picked the channel, A and B would still share the memory shire and
  the L3 home shire; the second access could then still wait behind the first's 64 B response and the 1-cycle issue
  offset: Delta in [0, 3] cycles. A threshold at 3 cannot separate the two, so the rule asks for more than 3 with
  confidence and a point estimate at tRRD's scale.
- *Prediction:* controls Delta_18 (same bank, other row) in [20, 60] (MEM-P4 back-to-back +36.9) and Delta_13 (same
  row) in [0, 10]; PA[11] and PA[12] share A's controller: Delta about 6 each. PA[6-10] are reported only: they move
  the L3 home shire (PA[10:6]), so A and B take different mesh paths and reach the controller at different times.
- *Rule:* per bit, Delta = the median over the card's trials (both PROBE passes) with a percentile-bootstrap 95%
  interval (2,000 resamples, seed 33). "Shares" if Delta >= 5 and the lower bound > 3; "separate" if the upper bound
  < 5; else "unclear". INSUFFICIENT if a control's median is out of its band; else PASS if PA[11] and PA[12] both
  share; FAIL if either reads separate; else INSUFFICIENT.

## R36: does the L2 keep TensorLoad lines? (hub rung 36, exp-tensor-reload)

The same TensorLoad as E36's LAT-S2 probe (the sparsity kernel's encoding), timed singly in a memprobe program on
hart 0 of shire 0 (`OP_TTLOAD`: issue to TensorWait). `tl1`, `tl2`: one fresh 1 KB block (evicted to memory, so not in
the L2 or L3) TensorLoaded twice; `probe_tl`: then one scalar load of one of its lines. References on other fresh
blocks: `ref_l2` (lines placed in the L2 by scalar loads), `ref_l3` (evicted to the L3); the scalar ladder `sref_*`.
`tl1_1` / `probe1`: the same with one line. `probe_l3tl`: a scalar load after a TensorLoad of L3-resident lines.
- *Theory T36 (the energy manual; LAT-S2's "L2" stream, an 8 KB buffer touched only by TensorLoads, ran at the
  scratchpad's 160 cycles per load):* a TensorLoad that misses the L2 allocates its lines in the L2.
- *Prediction:* tl1 in [600, 1300] cycles; ref_l2 in [120, 280]; tl2 / ref_l2 in [0.8, 1.25], nearer ref_l2 than
  ref_l3 or tl1; probe_tl, probe1 and probe_l3tl in the L2 band (raw TLOAD cycles [30, 75); L3 [75, 260); DRAM
  above).
- `tensor_error` is recorded before the first tensor op (`terr0`: an earlier kernel may have left bits set), after
  each `dram2` trial and at the end; an error is a bit that was not set in `terr0`.
- *Rule:* INSUFFICIENT unless the scalar ladder reads L2, L3, DRAM in its bands and tensor_error gains no bit; PASS if tl2
  is nearest ref_l2 (log distance) and probe_tl and probe1 read L2; else FAIL, naming the alternative ("L3 only": tl2
  like ref_l3 and the probe L3; "neither": like tl1 and DRAM; "mixed"). The three bands are reported.
- *Not done:* the shire-cache counter check (SYSCALL_PMC_SC_SAMPLE) the rung mentions.

## R43: what caps a shire at 128 B per cycle? (hub rung 43, exp-cache-bottleneck)

`MP_TLOOP`: hart 0 of the minions of 1-4 neighbourhoods (minion masks 0xFF, 0xFFFF, 0xFFFFFF, 0xFFFFFFFF) of all 32
shires streams 16-line TensorLoads from its own region, two in flight, 20,000 loads, 3 launches (the L2 buffer: 4,
the first a warm-up, dropped). Stride inside a load 64 B (all 4 banks, 16 sub-banks), 256 B (one bank, its 4
sub-banks), 1 KB (one bank, one sub-bank); bank PA[7:6], sub-bank PA[9:8] (`scp.addr-row`). "same": every minion
starts in bank 0, sub-bank 0, so all walk the same sub-banks in lockstep; "bank": minion m starts (m mod 4) x 64 B
in; "sub": also ((m / 4) mod 4) x 256 B; "onebank" (`s256q`, `s1kq`): (m mod 4) x 256 B, so every minion stays in
bank 0 but the minions start on its four sub-banks in turn, out of lockstep. Scratchpad: 256 KB + m x 33 KB of the
own shire; `l2-*`: an 8 KB DRAM buffer per minion, which each minion first reads with scalar loads (so it is
L2-resident whatever R36 finds) and which stays in the L2. Value: median over shires and launches of bytes per
shire-cycle (all streaming minions' bytes over the slowest minion's cycles).

Theories (each minion alone streams 6.4 B/cycle, `tl.one`: n neighbourhoods offer at most 51.2 n):
- **B (predicted):** each bank returns a line every other cycle (32 B/cycle) and so does each sub-bank; four banks make
  the 128. The energy manual's single-line stride-256 read, every minion in one bank, streams 614 GB/s = 32.0 B per
  shire-cycle (E46), where a 64 B/cycle bank would have left it at the issue-bound 48 of strides 64 and 128.
- **C:** a shared response path of 128 B/cycle, banks at the specification's 64 B/cycle, sub-banks 32.
- **Cc:** C, plus a convoy: when every minion starts in the same sub-bank and walks the sub-banks in lockstep
  ("same" at stride 256 or 1 KB), head-of-line blocking holds the bank to one sub-bank's 32 B/cycle. Cc equals B on
  every configuration except the "onebank" ones, which break the lockstep: B 32, Cc 64. Without them a B that
  survives could be Cc.
- **D:** each neighbourhood's link delivers 32 B/cycle (the Fill FIFO's "one every other cycle"), banks 64, sub-banks 32.
- **A:** sub-banks only (32 B/cycle each, the specification), no other cap.
- **A and D are refuted by data taken before memp2** and stay in the table only as a check: `scp.bw-own` (all 1,024
  minions, stride 64) streams 128 B per shire-cycle where A predicts 204.8, and `scp.bw-one-neigh` (one
  neighbourhood per shire) about 50 where D predicts 32. **R43 is B against C and Cc.**

| Configuration | A | B | C | Cc | D |
|---|---|---|---|---|---|
| `s64-n1` | 51.2 | 51.2 | 51.2 | 51.2 | 32.0 |
| `s64-n2` | 102.4 | 102.4 | 102.4 | 102.4 | 64.0 |
| `s64-n3` | 153.6 | 128.0 | 128.0 | 128.0 | 96.0 |
| `s64-n4` | 204.8 | 128.0 | 128.0 | 128.0 | 128.0 |
| `s256-n1` | 51.2 | 32.0 | 51.2 | 32.0 | 32.0 |
| `s256-n2` | 102.4 | 32.0 | 64.0 | 32.0 | 64.0 |
| `s256-n3` | 128.0 | 32.0 | 64.0 | 32.0 | 64.0 |
| `s256-n4` | 128.0 | 32.0 | 64.0 | 32.0 | 64.0 |
| `s1k-n1` .. `s1k-n4` | 32.0 | 32.0 | 32.0 | 32.0 | 32.0 |
| `s256b-n1` | 51.2 | 51.2 | 51.2 | 51.2 | 32.0 |
| `s256b-n4` | 204.8 | 128.0 | 128.0 | 128.0 | 128.0 |
| `s1kb-n4` | 128.0 | 128.0 | 128.0 | 128.0 | 128.0 |
| `s1ks-n4` | 204.8 | 128.0 | 128.0 | 128.0 | 128.0 |
| **`s256q-n4`** | 128.0 | **32.0** | 64.0 | **64.0** | 64.0 |
| **`s1kq-n4`** | 128.0 | **32.0** | 64.0 | **64.0** | 64.0 |
| `l2-s64-n4` | 204.8 | 128.0 | 128.0 | 128.0 | 128.0 |
| `l2-s256-n4` | 128.0 | 32.0 | 64.0 | 32.0 | 64.0 |

- *Rule:* a theory survives if every configuration used is within max(12%, 4 B/cycle) of its value. The `l2-*`
  configurations are used only if R36 PASSes on the same card (they assume the L2 keeps the lines); otherwise they
  are reported beside the verdict. INSUFFICIENT if a launch failed, tensor_error gained a bit, or a configuration
  used has no data. The item PASSes if B survives (the "onebank" rows then rule out C and Cc: 32 against 64, beyond
  the tolerance); the reading lists every surviving theory (none, one or several) and marks A and D as refuted
  before memp2.

## E102: stride-256 scratchpad tensor loads (energy-manual-102; E45's caveat)

Not a registered PLAN3 verdict: V3-CAT dropped the stride-256 row from arm B. Reported here under memp2's own
predictions. **This is a replication, not a new prediction:** E46 already ran `scpline/stride256` on the same three
cards, and the bands below are centred on its results. From E46's pooled numbers: dE = 64 x (7.33 - 6.56) = +49 pJ
per 64 B on random data and 64 x (4.91 - 4.25) = +42 on zeros; with about 2 W of awake minions, dE_T102 = 2 W x 64 B x
(1 / (614 GB/s) - 1 / (923 GB/s)) = about 70 pJ per 64 B, so the T102 ratio is already about 0.70 (random) and 0.60 (zeros),
the latter 0.10 above the band's lower edge. E102 checks that E46 repeats under memp2's timing on each card. Each ENERGY block runs three replicates of `tools/claims-v3/cat/run_catalogue_t10.py` (unchanged, its
E45/E46 timing: 3 s bursts, 4.5 s gaps, the scratchpad prefilled with the operands) over `scpline/stride{64,128,256}/
{zeros,random}` and `spin/zeros/h1`, with `build/enercat` (the g3log-fixed build; never `build/enercat_v2`), the 10 Hz
sampler around each replicate, and catlib's registered burst rules (`catlib.py check`, `pass_bursts`).
- **E102-bw:** BW(256) / BW(64) in [0.60, 0.72] (E46: 0.665 on every card; T43-B's 32 / 48) and BW(128) / BW(64)
  in [0.95, 1.05], each operand set, mean over replicates. PASS / FAIL.
- **E102-e:** dE = 64 x (E256 - mean(E64, E128)) pJ per 64 B. PLAN3's CAT-f expected it within noise; E46 (nine
  passes, three cards) suggests +40-50 pJ per 64 B. Predicted: on random data the 99% t interval over a card's
  replicates excludes 0, positive (PASS); PLAN3's "within noise" is reported per operand set.
- **E102-T (theory T102, "time, not SRAM"):** a same-bank line costs the SRAM what any line costs; the extra per byte is
  the 1,024 waiting minions' awake power over the longer time per byte: dE_T102 = P(spin/zeros/h1 over idle) x 64 B x
  (1 / BW(256) - 1 / mean(BW(64), BW(128))), measured in the same replicates (about 2 W: about 70 pJ per 64 B).
  PASS if dE / dE_T102 is in [0.5, 1.5] on both operand sets.
- At least three complete replicates per card, else INSUFFICIENT.

## Changes before any data (28 September, after the adversarial review; no memp2 data existed)

- R43: the "onebank" configurations `s256q-n4` and `s1kq-n4` and the theory Cc added; A and D stated as refuted
  before memp2; the `l2-*` buffer read by scalar loads before timing, and the `l2-*` rows used only if R36 PASSes.
- R33b: worded as refresh-domain bits, with the alternatives "per-memory-shire", "per-bank" and "lockstep"
  registered; a "same" PA[9] no longer reads as a refutation of PA[9] as the channel.
- R33c: the alternative's Delta (0-3 cycles) registered; the rule now needs a median >= 5 with a bootstrap 95% lower
  bound > 3 (it was a median >= 3).
- R36 and R43: tensor_error recorded before the first tensor op; only bits added after it count.
- E102 labelled a replication of E46, with the ratios E46 already implies.
- The freeze binds `LOCK.sha256` (this file, the block files, the shared framework files, the kernel's `.text`) and
  refuses a second freeze; the value validation checks is the lock's own SHA-256. Smoke passes on validation cards
  need the lock too. The smoke became a four-stage ladder, a PROBE or ENERGY pass needs an ok smoke with the same
  kernel, a hung launch stops everything, and `sysemu.sh` runs before any card time.

## Safety and etiquette (enforced in block.sh)

`et-who --check`, lib's `others_present` and `ours_running` before a block; the card lock held by the block (lib
`block_begin`, `flock -n`, fd 9, closed in every child); every launch `timeout 10`; between launches: nobody else,
no STOP file, the die's minshire mean read (twice unreadable: stop); no start above 80 C (waits up to 300 s, no
launch); stop at a mean of 86 C (the hottest sensor ran at most 4 C above the mean in E53), write
`build/claims-v3/STOP`; during an energy replicate a watcher reads the live telemetry at 2 Hz and stops the runner at
86 C. A launch that does not finish (the host's own 6 s timeout and aborted stream, `timeout 10`'s rc 124 or 137, a
stream error, "HPSQ" in its output, or memprobe's exit 3) writes `build/claims-v3/STOP` and ends the block at once:
nothing more is launched on that card until someone looks (28 September: after such a hang every later launch
failed and only a card reset cleared it). aifoundry1: card 1 only (`ET_DEVICES=1`), card 0 never, the stock
`dev_mngt_service` never (the queue drain is skipped; it opens card 0's node too), so a management-node failure
there (no die temperature twice, a sampler that will not start or ignores SIGTERM) also writes STOP. aifoundry2:
refused while any DV2 queue or block process exists, and without `MEMP2_AFTER_DV2=1`. No reset, clock, TDP,
firmware or log-level command.

## Development notes (filled in before the freeze)

- (none yet)
