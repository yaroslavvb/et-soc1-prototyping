# Hand it to the next shire

[← Findings index](README.md) · published as [Hand it to the next shire](https://spacesheep.dev/@yaroslavvb/et-soc1-on-chip-relay) (A14) · numbers
and sources: [05-claims.md](05-claims.md)

**Question (Q25, Q26):** is there a computation where shire-to-shire communication beats the standard
approach of putting the intermediate in main memory?

**Answer:** yes, and by a lot. A chain of stages that hands each stage's output to the next shire's
[scratchpad](README.md#terms) (the next shire in ID order, 3.5 mesh hops away on average) instead of writing it to
DRAM runs **12.3× faster** and uses **12× less energy per byte**, at the same watts. Keeping the output in the
shire's own scratchpad is **30.7×**. The advantage appears only once the working set outgrows the 32 MB L3.

Evidence: [E24, E25](03-experiments.md). Published as [A14](04-artifacts.md).

---

## The experiment

A slab of fp32 per shire. A stage reads every element, adds one, writes it out; the next stage reads what the
last wrote; a chip-wide barrier between stages. **The same kernel, the same barriers and the same arithmetic**
run three ways, and only the destination of a stage's output differs.

| Where a stage's output goes | GB/s | Against DRAM | pJ per byte | W over idle |
|---|---|---|---|---|
| DRAM, read back next stage | 48.4 | — | 104.8 | 4.34 |
| The next shire's scratchpad | 592.9 | **12.3×** | 8.9 | 4.42 |
| This shire's own scratchpad | 1,483.7 | **30.7×** | 4.3 | 5.30 |

1 MB per shire per stage, eight stages, 1,024 minions, 512 MB of reads and writes. aifoundry3 gives 12.4× and
31.2×. The table is the first run; re-measured three times per card with the die held warm (E29), the energies are
105.7 [99.5–111.0] pJ/B through DRAM, 8.6 [7.8–9.2] to the next shire and 3.99 [3.90–4.25] in the own scratchpad —
12× and 26×. They are in line with the energy manual's levels, re-measured at 600 MHz on both cards (E29):
122 [117–129] pJ/B from DRAM, 2.5 from the own scratchpad, 6.7 from another shire's. The 18 September
memory-hierarchy report printed 148 / 2.8 / 6.3, a mean of two runs taken at mixed clocks.

**All three draw the same power.** Within a watt of each other, while moving 49.7, 594 and 1,503 GB/s. That is
the cleanest way to say it: DRAM costs the same watts to move a thirtieth of the data.

## How we know the data really crossed a shire

Each shire starts its slab filled with its own number. After eight stages of adding one, a shire that kept its
own data holds 8. In the hand-off run **shire 0 holds 32**, which is 24 + 8, and 24 is the shire eight places
back round the ring. Every element of every run in this work is checked against that expectation, so a run
whose data had not actually moved would fail rather than quietly pass.

## The boundary that matters

The win is against DRAM, not against the memory hierarchy.

| Working set, one buffer chip-wide | DRAM GB/s | Next shire | Advantage |
|---|---|---|---|
| 2 MB | 281 | 274 | 1.0× |
| 8 MB | 409 | 517 | 1.3× |
| 16 MB | 379 | 545 | 1.4× |
| **32 MB** | **48** | **593** | **12.4×** |
| 64 MB | 48 | — | — |
| 256 MB | 53 | — | — |

Below the 32 MB L3 the DRAM route is not going to DRAM at all, and placing the data by hand buys almost
nothing. At 32 MB it falls off a cliff and stays down. **The advantage is not a property of the computation.
It is the L3 capacity.**

## How much arithmetic it takes to stop mattering

Repeating the add `w` times per element walks the workload up the roofline. The lead holds to about four adds
per element and then falls faster with each quadrupling:

| Adds per element | Own shire | Next shire |
|---|---|---|
| 1 | 30.7× | 12.2× |
| 8 | 20.5× | 10.0× |
| 32 | 9.0× | 6.2× |
| 128 | 2.7× | 2.4× |
| 256 | 1.6× | 1.5× |

Counting bytes moved (each element is read and written, so one add per element is 0.125 flops per byte moved),
256 adds per element is 32 flops per byte moved, or 64 per byte read. Rule of thumb for this vector-add kernel:
**on-chip placement pays several-fold up to a few flops per byte moved and is still 1.5× at 32 flops per byte
moved.** For the tensor unit, which does twice the `fadd.ps` rate, the ridge-points report puts the DRAM crossover
near 130 flops per byte read.

## How far the slab moves does not change the bandwidth

The ring runs in shire-ID order, and shire IDs do not follow the mesh: on the shire map of the on-chip communication
report, the next shire by ID is 1–10 mesh hops away (3.5 on average), and 2, 4, 8 and 16 IDs away average 4.5, 3.7,
1.6 and 2.1 hops.

| Shire IDs back round the ring | 1 | 2 | 4 | 8 | 16 |
|---|---|---|---|---|---|
| Mesh hops, mean (range) | 3.5 (1–10) | 4.5 (2–7) | 3.7 (1–8) | 1.6 (1–7) | 2.1 (1–6) |
| GB/s | 593 | 703 | 652 | 686 | 733 |

Across offsets whose mean distance runs from 1.6 to 4.5 hops the bandwidth stays between 593 and 733 GB/s and does
not follow the distance. Transfers are 32 KB per minion and deeply pipelined, so the 12-cycle round trip per hop
never appears. The practical consequence: **for bandwidth, a stage can be given to whichever shire suits.**

It does cost energy: on a loaded mesh each hop adds about 1.5–2.2 pJ per byte of random data
([20-heat-per-mm.md](20-heat-per-mm.md)), about half of a tensor load of that byte from the shire's own scratchpad
(4.2 pJ/B), which this bandwidth sweep does not see. The 8.6 pJ/B hand-off averages 3.5 hops, so a
stage placed on a physical neighbour should cost less; that was not measured.

## The mechanism, and why it is not a systolic array

The unit is the **shire**, not the minion. Its 2.5 MB scratchpad is addressable by every other shire (PRM
format 0, shire in address bits [29:23]), and a **tensor store bypasses the L1 and L2 caches**, so what one
shire writes another reads with no coherence problem at all. That is the whole mechanism.

The register-to-register path (`TensorSend`/`TensorRecv`) is the more obvious "systolic" choice and it is
immune to the shire-cache contention in [17-hot-line.md](17-hot-line.md), because it never touches the shire
cache. It was **not** used here, for a reason recorded in R12: the hardware keeps one partner-ready flag per
minion rather than one per partner, so a two-dimensional array where a cell receives from both north and west
**hangs a hart permanently and needs a power cycle**. One-dimensional rings and alternating phases are safe,
but the relay at shire granularity gets the same benefit over a path that cannot hang.

## Things that bit us

- **Offset 0 of a shire's scratchpad faults.** Start buffers 256 KB in.
- **A global atomic through the scratchpad self ID `0x7F` is a bus error.** From the owning shire an
  `amoaddg` leaves by the same port as everyone else's.
- **Never spin on a global atomic in a barrier.** The first version had each shire's leader poll one counter.
  Thirty-two pollers saturate that line's home shire cache and stop its own memory path, which is exactly
  [17-hot-line.md](17-hot-line.md); the barrier hung. The fix is the credit-release shape `nocbench` measures
  at about 5,000 cycles: one atomic per shire, nobody spinning.
- **This core traps on 64-bit integer-to-float conversion.** A `double` accumulator in a checksum is enough to
  kill the kernel. Sum bit patterns as integers.

## Not established

- **A working set larger than the 80 MB of scratchpad.** That is the case where the hand-off would be the
  *only* option rather than the faster one, and it needs flow control between shires that we did not build.
- **A real pipeline.** The arithmetic here is one vector add, chosen to make the measurement about movement.
- **A cheaper barrier.** A credit between neighbouring shires would do instead of a chip-wide barrier, and
  would help the on-chip media most, so the figures above understate them slightly.
- **Scaling with the number of shires is not measured.** A sweep that used fewer shires also shrank the working
  set back inside the L3, so it cannot be read as a scaling curve.
- **Whether handing to a physical neighbour lowers the 8.6 pJ/B.** Every hand-off here went to the next shire ID.

## Related

- [20-heat-per-mm.md](20-heat-per-mm.md): what each hop of the hand-off costs, per bit and per millimetre.
- [17-hot-line.md](17-hot-line.md): the contention that hung the relay's first barrier.
- [19-observability-and-the-unmetered.md](19-observability-and-the-unmetered.md): the E29 bars on this page's
  energies.
