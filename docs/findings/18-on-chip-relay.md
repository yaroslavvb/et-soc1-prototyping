# Hand it to the next shire

**Question (Q25, Q26):** is there a computation where shire-to-shire communication beats the standard
approach of putting the intermediate in main memory?

**Answer:** yes, and by a lot. A chain of stages that hands each stage's output to a neighbouring shire's
scratchpad instead of writing it to DRAM runs **12.3× faster** and uses **12× less energy per byte**, at the
same watts. Keeping the output in the shire's own scratchpad is **30.7×**. The advantage appears only once
the working set outgrows the 32 MB L3.

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
31.2×. The energy figures line up with the independent memory-hierarchy measurements (133 pJ/B for DRAM, 2.6
local scratchpad, 6.3 remote).

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

Repeating the add `w` times per element walks the workload up the roofline. The lead roughly halves for every
quadrupling of the work:

| Adds per element | Own shire | Next shire |
|---|---|---|
| 1 | 30.7× | 12.2× |
| 8 | 20.5× | 10.0× |
| 32 | 9.0× | 6.2× |
| 128 | 2.7× | 2.4× |
| 256 | 1.6× | 1.5× |

Rule of thumb: **on-chip placement is worth it below roughly ten flops per byte.** Above that the arithmetic
is the wall and it does not matter where the operands came from.

## Distance across the mesh is free

| Shires the slab moves per stage | 1 | 2 | 4 | 8 | 16 |
|---|---|---|---|---|---|
| GB/s | 593 | 703 | 652 | 686 | 734 |

Handing a slab sixteen shires away, across the width of the mesh, is not slower than handing it next door.
Transfers are 32 KB per minion and deeply pipelined, so the 12-cycle-per-hop latency never appears. The
practical consequence: **a stage can be given to whichever shire suits, not only to a neighbour.**

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
  *only* option rather than the faster one, and it needs flow control between neighbouring shires that we did
  not build.
- **A real pipeline.** The arithmetic here is one vector add, chosen to make the measurement about movement.
- **A cheaper barrier.** A credit between neighbouring shires would do instead of a chip-wide barrier, and
  would help the on-chip media most, so the figures above understate them slightly.
- **The `shires` sweep is confounded**: fewer shires also means a smaller working set, which puts it back
  inside the L3. Do not read it as a scaling curve.
