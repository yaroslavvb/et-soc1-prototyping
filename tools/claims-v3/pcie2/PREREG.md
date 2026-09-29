# PCIE2: theories and predictions, stated before any data (hub rungs 34 and 35)

Written on 28 September 2026, about 22:00 PDT, and revised about 23:00 (Revision 1, below), before any pcie2
process ran on any card. The only data used are the 27 September PCIe runs (E50: `docs/reports/data/2026-09-27-pcie/`,
`pcie.json`, five runs on each of three cards), the memory latencies of E36 (`docs/et-soc1-notes.md`, "One memory
access, taken apart"; `docs/findings/05-claims.md`), and the et-platform sources in `external/` (read, not run). `reduce.py` judges exactly the table below
(`reduce.py --print-predictions`); if the two ever differ, the code's table is the one that was frozen with this file.

**Status: draft for development.** Development (aifoundry1's card 1) may fix the code; a change to any prediction
before the freeze is written under "Amendments before the freeze" with its reason and the development numbers that
prompted it. `freeze.sh` then writes `TEXT.sha256` (the kernels' `.text`), `LOCK.sha256` and `PREREG.sha256`; after
that nothing here changes, and `block.sh` refuses validation passes unless the lock verifies, the probe was built from
the locked sources and its kernels have the frozen `.text`.

## What is measured

- **R35 (rung 35).** On 27 September two host-to-card (H2D) DMA commands in flight on one stream moved 0.49x the
  aggregate rate of one at a time (the barrier on each copy), on all three cards: 0.492 [0.489, 0.494] on
  aifoundry2, 0.488 [0.484, 0.491] on aifoundry3, 0.491 [0.489, 0.494] on aifoundry1's card 1 (`pcie.json`
  `derived.<card>.h2d_two_in_flight_over_one`, 2 x 64 MB per stream, DMA-only). Device-to-host (D2H) did not
  collapse (1.08-1.11), and four H2D in flight on two streams moved as much as two (0.98-0.99, P12). This experiment
  times 2 commands of N = 1, 4, 16 and 64 MB per stream, DMA-only (the API's no-op bounce copy), in five
  configurations per process: `h2d` and `d2h` (both commands of one stream in flight), `h2d/ser` and `d2h/ser` (the
  barrier on each: one in flight), and `2xh2d/ser` (two streams, one command of each in flight: two in flight from two
  streams). The plain call sends each copy as one DMA element; `--elements 8` sends it as a list of 8 equal elements
  (64 MB also as a 1-element list, the list path's control).
- **R34 (rung 34).** Where does a host write land: in its line's L3 home, or in a memory shire? A 4 MB buffer is
  written by the normal (staged) copy, then one hart (shire 0) times the first load of 4,096 of its lines, one at a
  time, in a kernel launched without the L3 flush; the same lines are timed again at once (an L2 hit). Per
  repetition (five per pass), seven launches on all 32 shires, none of the timed ones with the flush: write P1; a
  flush launch (the L3 flush, timing nothing); `dram_ref` (every line from DRAM); `l3_ref` (the lines dram_ref left in
  the L3); write P2; `h2d_warm` (the L3 held P1's lines when the host wrote P2); a flush launch; write P3; `h2d_cold`
  (the L3 held none of the buffer); `l3_ref2` (control). Every first-touch value is checked against the pattern
  written last and the one before it.

## Facts read from the sources (28 September; read, not measured)

- The runtime sends a copy of up to 128 MB x 8 as one command, split into elements of at most 128 MB
  (`MemcpyH2DAction.cpp`): each copy here is one command, one element unless `--elements` makes a list.
- The master minion's DMA worker gives each command its own channel (4 read, 4 write) and puts all of a command's
  elements on that channel's linked list (`dmaw.c`, `dma_config_read_add_data_node(..., read_chan_id, xfer_index)`);
  the driver only enables the read and write engines and programs no channel weights (`pcie_dma.c`).
- All three hosts run the IOMMU translated (`DMA-FQ`, `hosts.txt`).
- The service processor's BL2 enables, in the PCIe shire's NoC bridge, the address-map entries `MAIN0_TOL3` for
  512 GB + 8 MB to 516 GB (the DRAM alias of the runtime's device addresses, e.g. `0x8040000000`) and `MAIN0_TOSYS`
  for 768 GB + 8 MB to 772 GB, by clearing their disable bits, which are set at reset (`reconfig_noc_pshire`,
  `pcie_configuration.c`; `noc_reconfig_pshire.c`; `ns_noc_io_pcie_soc_ip.h`).
- The shire cache is write-back and write-allocate for both L2 and L3, and an L3-slave write "writes L3 in this bank"
  (Shire Cache Specification, 1.1 and 1.3).
- The firmware evicts the DMA engine's own linked list only to the L3 before ringing the doorbell (`pcie_dma.c`,
  `ETSOC_MEM_EVICT(..., to_L3)`), which only works if the engine's reads of DRAM are served through the L3; and every
  workload reads its kernel's results with a D2H DMA after the post-kernel L2 evict has left them dirty in the L3
  (`kernel.c`, `syscall.c` `post_kernel_cleanup`), and gets correct data.
- A launch with the L3 flush makes hart 0 of every shire in its mask evict its L3 slice before the kernel starts
  (`kernel.c` `KERNEL_LAUNCH_FLAGS_EVICT_L3_BEFORE_LAUNCH`; `syscall.c` `evict_l3`): a 32-shire launch empties them all.
  Each slice's evict waits until its banks are idle, but there is no barrier after the evicts, so within that launch
  one shire can start while another's slice is still being evicted. The timed launches therefore never carry the
  flush: a launch of its own does, and it completes only after every slice's evict has.

## Theories

**R35: why do two H2D commands in flight move half as much as one?**

- **T35-A, a fixed cost per overlapping command.** Something costs a fixed time each time two commands overlap. Then
  the time lost to the overlap does not grow with the size: 27 September's loss at 2 x 64 MB is
  2 x 64 MiB x (1/6.09 - 1/12.39) s/GB = 11.2 ms, and the same 11.2 ms at 1 MB would give h(1) = 0.46/(0.46 + 11.2)
  = 0.04 and h(4) = 0.08; and the lost time sits in the intercept of wall = a + bytes/R, so the rate ratio
  R(h2d)/R(h2d/ser) stays near 1 (>= 0.85).
- **T35-B, a shared DMA read engine** that moves half the bytes while two of its channels are active (e.g. requests
  interleaved by channel that drain the read pipeline). **T35-C, the IOMMU**, whose translation of two concurrent
  read streams halves their rate. Both say: a rate, B2 = 6.09 GB/s, whenever two H2D commands overlap, whichever
  streams they come from. With one command at B1 = 12.39 GB/s (`h2d/ser`, 27 Sep), a fixed part F of 0.1-0.5 ms per
  trial, and a device-side fixed part c of 0-0.25 ms per command that the barrier pays in turn and two commands in
  flight overlap (the bw curve: one 1 MB H2D DMA takes 222-273 us, of which 85 us is the transfer; a 64 MB one
  5.63-5.70 ms), h(n) = (F + 2c + 2n/B1)/(F + c + 2n/B2): 0.61-1.11 at 1 MB, 0.53-0.79 at 4 MB, 0.50-0.59 at 16 MB,
  0.49-0.52 at 64 MB. At small sizes the fixed costs dominate, so h(1) says little about the rate; the rate itself is
  the slope of the wall time against the bytes, which F and c do not touch: over 1-64 MB, wall = a + bytes/R per
  configuration, and R(h2d)/R(h2d/ser) = B2/B1 = 0.49 at any F and c. Splitting a command into 8 elements changes
  nothing (they run one after another on its channel). **This experiment cannot separate B from C**: that needs one
  host rebooted with `iommu=pt`, which is not planned now (under C the halving would vanish there, under B it would
  stay).
- **T35-E, a slow onset**: the loss sets in only after a long overlap (a queue or credit pool that fills). Then small
  pairs lose nothing: h(1) >= 0.95, h(4) >= 0.85. (Its rate ratio over 1-64 MB is about 0.52, like B/C's: h(4)
  separates them.)
- **T35-X, elements, not commands**: the engine overlaps a command's elements, and that overlap is what loses. Then
  one command of 8 elements, alone, moves about half as much as one of 1 element: e1 <= 0.65.
- **T35-S, one stream only**: only two commands of the same stream collide (e.g. a runtime or worker effect per
  stream). Then two streams with one command each in flight lose nothing: s2 >= 0.90.

We expect T35-B or T35-C (D2H, whose writes the IOMMU also translates, does not collapse, which weakly favours B).

**R34: where does a host write land?**

- **T34-A, through the line's L3 home, which allocates it** (favoured by the sources above): the first touch after a
  write is an L3 hit whether or not the L3 held the line (h2d_warm and h2d_cold L3-like), and every value is new.
- **T34-B, through the L3 home, which updates a line it holds and allocates none**: h2d_warm L3-like, h2d_cold
  DRAM-like, values new.
- **T34-C, to the memory shires, and the L3's copy is invalidated**: both DRAM-like, values new.
- **T34-D, to the memory shires, and the L3 keeps its stale copy**: h2d_warm reads the old pattern (stale), at L3
  latency; h2d_cold DRAM-like. (A kernel reading a buffer that a host copy has just overwritten would then read old
  data; no workload here is known to have read old data after a copy, which argues weakly against D.)

Latency references (E36, three cards, 26 Sep): an L3 hit costs 110 + 12 x hops from the requester to the line's
home (PA[10:6]), DRAM another 91 + 12 x hops from the home to the memory shire (PA[8:6]), plus 11-38 cycles of row
state; an L2 hit 47-48; the probe's raw intervals carry about 5 cycles of counter reads (memprobe subtracts them).
From shire 0 to the 32 homes the hops average about 3-4, so an L3 first touch should read about 150-170 cycles and a
DRAM one about 280-320 (memhier: L3 159-169, DRAM 287-297 at 600 MHz).

## Predictions

A pass's value, per quantity (`reduce.py` docstring): R35 ratios are ratios of the medians over a process's trials
of each configuration's aggregate rate; R34 medians pool a pass's lines; an R34 fraction is, per repetition, the
share of lines whose first touch is closer to the same line's `l3_ref` value than to its `dram_ref` value (lines whose
two references differ by less than 40 cycles, or that carry a wrapped interval, are left out), averaged over the
repetitions; a repetition in which fewer than half its lines are kept (their two references 40 cycles or more
apart) is left out of the fractions, and counted. The latency medians (P34-1 to P34-4, absolute cycle counts) are
taken only from passes in which every telemetry sample read the minion clock at 600 MHz. `h(n)` =
aggregate(`h2d`)/aggregate(`h2d/ser`) at 2 x n MB, plain call; `d(n)` the same for D2H;
`s2` = aggregate(`2xh2d/ser`)/aggregate(`h2d/ser`), 64 MB; `e1` = aggregate(`h2d/ser`, 8 elements)/aggregate(`h2d/ser`,
1-element list), 64 MB; `e2` = h(64) with 8 elements; `lc` = aggregate(`h2d/ser`, 1-element list)/aggregate(`h2d/ser`,
plain), 64 MB; `rr` = R(`h2d`)/R(`h2d/ser`), plain call, where R is the slope's inverse in a least-squares line
wall = a + bytes/R through the median wall times at 1, 4, 16 and 64 MB.

| ID | Quantity | Prediction | From |
|---|---|---|---|
| P35-1 | h(64) | 0.44-0.54 | the 27 Sep replication (0.488-0.492) |
| P35-2 | h(16) | 0.44-0.62 | T35-B/C: 0.50-0.59 |
| P35-3 | h(4) | 0.50-0.80 | T35-B/C: 0.53-0.79 |
| P35-4 | h(1) | 0.55-1.15 | T35-B/C: 0.61-1.11 (fixed costs dominate; not a condition of any B/C verdict) |
| P35-5a-c | d(1), d(4), d(16) | >= 0.95 | 27 Sep: D2H two in flight gained at 64 MB; overlap only hides fixed costs at smaller sizes |
| P35-5d | d(64) | 1.00-1.20 | 27 Sep: 1.08-1.11 |
| P35-6 | s2 | 0.44-0.60 | T35-B/C: any two H2D commands in flight |
| P35-7 | e1 | 0.93-1.07 | a command's elements run in turn on its channel (`dmaw.c`) |
| P35-8 | e2 | 0.44-0.56 | as P35-1 |
| P35-9 | lc | 0.95-1.05 | the list path's control |
| P35-10 | rr, the rate ratio from the fit over 1-64 MB | 0.44-0.54 | T35-B/C: B2/B1 = 0.49, whatever the fixed costs |
| P34-1 | dram_ref median (cycles) | 250-380 | E36: about 280-320 |
| P34-2 | l3_ref median (cycles) | 135-195 | E36: about 150-170 |
| P34-3 | dram_ref - l3_ref per line, median | 80-220 | E36: 91 + 12 x hops + row state |
| P34-4 | second-touch median (an L2 hit) | 35-65 | E36: 47-48 |
| P34-5 | share of lines with references < 40 cycles apart | <= 0.05 | the counter glitch (about 1 interval in 70) and refresh stalls |
| P34-6 | l3_ref2, share L3-like (control) | >= 0.90 | the lines h2d_cold's kernel just read are in the L3 |
| P34-7 | h2d_warm, share L3-like | >= 0.90 | T34-A |
| P34-8 | h2d_cold, share L3-like | >= 0.90 | T34-A |
| P34-9 | first-touch values that are not the last pattern written, all arms | 0 in every pass | T34-A |

Theory conditions (a theory is refuted on a card when any of its conditions fails, survives when all pass, and is
open otherwise):

| Theory | Conditions |
|---|---|
| T35-A | h(1) <= 0.20; h(4) <= 0.35; h(64) 0.44-0.54; rr >= 0.85 |
| T35-B/C | rr 0.44-0.54; h(64) 0.44-0.54; h(16) 0.44-0.62; h(4) 0.50-0.80; s2 0.44-0.60; e1 0.93-1.07; e2 0.44-0.56 |
| T35-E | h(1) >= 0.95; h(4) >= 0.85 |
| T35-X | e1 <= 0.65 |
| T35-S | s2 >= 0.90 |
| T34-A | h2d_warm >= 0.90 L3-like; h2d_cold >= 0.90 L3-like; bad values 0 |
| T34-B | h2d_warm >= 0.90; h2d_cold <= 0.10; bad values 0 |
| T34-C | h2d_warm <= 0.10; h2d_cold <= 0.10; bad values 0 |
| T34-D | h2d_warm stale share >= 0.90; h2d_cold <= 0.10 |

**The R34 instrument's controls.** The T34 theories are judged on a card only when P34-1, P34-2, P34-3, P34-5 and
P34-6 all PASS there (the flush launch sends the lines to DRAM, the L3 keeps what a kernel read, the two references
are apart, few lines are ambiguous). Otherwise every T34 theory is **invalid** on that card, whatever its conditions
say: an instrument that cannot tell DRAM from the L3 cannot say where a host write went.

Also reported, not judged: the time lost to the overlap at each size (`lost_ms<n>`, the T35-A signature in ms), the
fit's intercept gap a(h2d) - a(h2d/ser) (`icpt_gap_ms`: about 11 ms under T35-A, small under B/C), s2 at 1-16 MB,
h(n) with 8 elements at every size, the stale share of h2d_warm, the repetitions dropped, and every configuration's
rate.

## The rule

The unit of replication is the pass. A card's value is the mean of its passes' values with a 99% t-interval (five
passes: t = 4.604). PASS: the interval lies inside the predicted range (for a bound, on its predicted side); FAIL: it
lies wholly outside; otherwise INCONCLUSIVE. A count predicted zero passes only if it is zero in every pass. Each
prediction and theory is judged per card. A pass whose `block.json` is not `ok` or whose check fails (a process that
did not exit 0, a missing trial or arm, a stream error, a die at 90 C) is left out and listed, and so is a
validation pass that did not run frozen on this file (its `pass.json` must say `"frozen": true` and carry the
sha256 in `PREREG.sha256`) and any `V3_DRY` pass. A failed prediction is reported as failed.

## Cards and passes

- Development: aifoundry1's card 1 (firmware 1.2.0, 600 MHz fixed), the smoke (pass 901) and passes 101-103.
  Development values are reported as development and never judged against this table.
- Validation, after the freeze: aifoundry3 (firmware 1.3.1, pinned at 600 MHz), passes 1-5, five minutes apart,
  run by `run_passes.sh` (which stops at the first pass that fails); then aifoundry2 (firmware 1.3.1, its governor
  free: record the clock) as a third card, only after the DV2 validation ends (about 17:00 PDT, 29 September),
  passes 1-5.
- Card time: about 25 s per pass; development under 5 minutes, validation under 5 minutes per card.

## Amendments before the freeze

**Revision 1 (28 September, about 23:00 PDT; no data: no pcie2 process had run on any card).** From the review of
the draft, before development:

- R34's protocol: `dram_ref` is no longer launched with the L3 flush; a flush launch that times nothing comes
  before it (each slice's evict runs after the pre-launch sync with no barrier after it, so a flushed timed launch
  could start timing while other slices were still evicting and read some lines at L3 latency).
- R34's rules: the T34 theories are judged only when the instrument's controls (P34-1, -2, -3, -5, -6) all pass; a
  repetition with fewer than half its lines kept is left out of the fractions; P34-1 to P34-4 come only from passes
  whose samples all read 600 MHz (aifoundry2's governor is free).
- R35: h(1) is no longer a T35-B/C condition, and its range is 0.55-1.15 (was 0.55-1.00); h(4) 0.50-0.80 (was
  0.50-0.75) and h(16) 0.44-0.62 (was 0.44-0.60): with a device-side fixed cost per command that the barrier pays in
  turn and two commands in flight overlap, B/C gives h(1) up to 1.11 and h(4) up to 0.79 (above). The new P35-10,
  the rate ratio from the fit over 1-64 MB, is B/C's rate itself (0.44-0.54), and T35-A gains rr >= 0.85.
- Validation passes count only if they ran frozen on this file; V3_DRY passes never count.

### Development result (aifoundry1's card 1, passes 101-103, 28 September 23:48-23:55 PDT), before the freeze

Nothing above is changed by it; it is recorded so that the validation reads against it. Two H2D commands in flight
in one stream moved 0.493 (64 MB), 0.529 (16 MB) and 0.568 (4 MB) of one (P35-1..3 PASS; the rate ratio P35-10
0.487), and splitting a command into 8 elements changed nothing (P35-7, P35-8 PASS); but one H2D command in each of
two streams moved 1.019 of one (P35-6 FAIL against 0.44-0.60). So T35-A, T35-BC, T35-E and T35-X were refuted and
**T35-S (only two commands of one stream collide) survived**: the loss is in how one stream serves two commands, not in
a shared read engine or the IOMMU. D2H at 64 MB: 1.096 (P35-5d PASS); D2H at 1-16 MB INCONCLUSIVE (0.89-0.90, wide).
R34: every control passed; after a host write 99.9% of lines read at L3 latency whether the L3 held them before or
not, with no wrong value (P34-7, -8, -9 PASS): **T34-A survived**, T34-B, -C and -D refuted. The validation tests
every theory as registered above.
