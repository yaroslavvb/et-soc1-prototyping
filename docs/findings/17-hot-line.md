# One hot line stops a shire

[← Findings index](README.md) · published as [One hot line stops a shire](https://spacesheep.dev/@yaroslavvb/et-soc1-hot-line) (A13) · numbers and
sources: [05-claims.md](05-claims.md)

**Question (Q24):** Ivan reported in Discord that with all 32 shires hammering one global atomic counter in
shire 0's scratchpad, *"shire 0 got 6% of its fair share and finished only after the other 31"*. Is the shire
cache short-changing whoever owns the line?

**Answer:** no. The atomic is shared to within half a percent (every shire between 0.998 and 1.004 of an even
split), including with the host shire. But the host shire loses its **own** memory path completely, for as long as
the hammering lasts.

Evidence: [E22, E23](03-experiments.md). Published as [A13](04-artifacts.md). A [shire](README.md#terms) is 32
minions and their shared 4 MB of SRAM; a global atomic (`amoaddg`) is performed at the shire cache that homes the
line, which is also where that shire's own loads and stores are served.

---

## What reproduces, and what does not

| Ivan's observation | What we measure |
|---|---|
| ~60 M atomics/s in aggregate | **Confirmed.** 10.00 cycles per atomic, about 60 M/s, on both cards |
| the 31 non-owning shires split it evenly | **Confirmed.** Standard deviation of share 0.001 |
| shire 0 got 6% of its fair share | **Not reproduced.** Host shire's share is **1.004** of an even split |
| shire 0 finished after the other 31 | **Not reproduced** for the atomic; but see below, which is worse |

Moving the line's home to shire 7, 15 or 31 changes nothing, so shire 0 is not special. The only case where
shares spread out is the opposite of starvation: with one minion per shire the bank is still saturated (600,061
atomics in 6,000,000 cycles, 10.0 cycles each), but each shire has only one request queued, so the mesh round trip
decides. Shares fall step by step with hop distance, and the host shire, which crosses no mesh links, comes
**first** (1.20 against 0.85 for the farthest, ten hops away).

**Why the atomic cannot be unfair.** A global atomic addressed through the scratchpad self ID `0x7F` raises a
kernel bus error — the local path does not carry one. From the host shire an `amoaddg` therefore leaves
through the same L3-slave port as everyone else's, and the arbitration rule that ranks L3-slave requests above
neighbourhood requests never applies to it.

## What actually starves

Give the host shire's 32 minions ordinary work instead — 64 B-strided loads over a private slice of memory —
while the other 31 shires hammer a line that lives in that same shire cache:

| Host shire is reading | Hot line is in | Alone | While hammered | Fraction |
|---|---|---|---|---|
| its own scratchpad | scratchpad of the same shire | 1,688,306 | 384 | 0.023% |
| its own scratchpad | L3 slice of the same shire | 1,688,300 | 208 | 0.012% |
| DRAM | scratchpad of the same shire | 821,182 | 384 | 0.047% |
| DRAM | L3 slice of the same shire | 822,066 | 192 | 0.023% |

**These are stops, not slow-downs.** The host shire's count is the same number for windows of 5, 10, 40 and
100 ms — 384 operations while the mesh retires six million atomics. Twelve loads per minion get through during
the ramp-up and then nothing. Thirty-two minions, a thirty-second of the chip, sit in a load that does not
return, and nothing reports an error.

## The threshold is a cliff, and one other shire clears it

| Minions of one other shire hammering | Cycles per remote atomic | Host shire's own throughput |
|---|---|---|
| 1 | 216.2 | 110.7% |
| 8 | 27.0 | 99.0% |
| 16 | 13.4 | 99.6% |
| 20 | 10.7 | 98.9% |
| **24** | **10.0** | **0.02%** |
| 32 | 10.0 | 0.02% |

There is no gradual degradation. A shire cache retires one global atomic every 10 cycles; while the remote
demand stays under that, the host shire is untouched, and the moment it reaches it the host gets nothing. 24
concurrent remote requesters is under one shire's worth of minions.

## The vendor wrote this down

Two errata in the ET-SoC errata document (R1), both marked **Postponed**:

- **4.1, `RTLMIN-6207`, "Neigh request hangs if shire cache full of l3_slave requests to same SCP address."**
  *"The shire cache prioritizes l3_slave requests over neighborhood requests. If there are too many l3
  requests there may be no resources for neighborhood requests. `l3_yield_priority` allows priority and
  resources to be given to neighborhood requests. However, if the neighborhood and the mesh are both accessing
  the same SCP request it is possible for the neighborhood request to continually be squashed and the request
  could still not progress even with `l3_yield_priority` set to non-zero."*
  Impact: *"Low. It would have to be a pretty consistent and repeating pattern."*
  Workaround: *"Slow down the polling rate from other shires."*
- **4.2, `RTLMIN-6214`, "L3_yield priority does not have sub-bank granularity."** The yield can be satisfied by
  a neighbourhood request to a different sub-bank while the one it needs stays busy.

That bears on both questions worth sending back. **Would setting `l3_yield` restore the host?** Not certainly.
Erratum 4.1 says it does not when the host and the mesh want the same address. The case measured here is different
addresses, which is what the yield was built for. But erratum 4.2 says the yield has no sub-bank granularity, so a
host request to the sub-bank the hot line saturates can still be skipped indefinitely, and each host minion's stream
reaches that sub-bank sooner or later. It was not tested. **Does it hold for a DRAM-backed line rather than
scratchpad?** Yes, and slightly worse: 192
operations instead of 384. The erratum's title says "SCP address" but the behaviour is not specific to the
scratchpad.

`l3_yield` was **not** set here: it is a shire-cache configuration register on a shared lab card, and the errata
suggest it would not fully help.

## The workaround, priced

| Cycles a remote waits between atomics | Host shire | The 31 hammering shires |
|---|---|---|
| 0 to 8,000 | 0.03% | 100% |
| 10,000 | 54% | 96% |
| 12,000 | 85% | 80% |
| 16,000 | 95% | 61% |
| 100,000 | 98% | 10% |

Nothing below 10,000 cycles helps at all, because below that the bank is still saturated. At the knee the
trade is cheap: the first thing pacing removes is queueing, not throughput.

## Energy

| Case | Rate | Board W over idle | nJ per operation |
|---|---|---|---|
| one DRAM line, 1,024 minions | 60 M/s | 1.41 | 23.6 |
| 32 DRAM lines, 1,024 minions | 1,919 M/s | 2.63 | 1.4 |
| host shire reading, nobody hammering | 180 M/s | 0.07 | 0.4 |

The table is the first run (22 September, aifoundry2). Re-run for the energy manual (E29), three passes per card
with the die held warm: contended 19.8 [16.9–23.6] nJ, spread 1.16 [1.01–1.37] nJ, n = 7 — still 17×, and about
1.2 W over idle for the stalled chip. Quote those. The reading-only row's 0.07 W is inside the idle baseline's
±0.2 W, so its 0.4 nJ is an order of magnitude, not a measurement.

A contended line costs **17× the energy per operation**. A thousand minions stalled on it cost about 1.2–1.4 W
over idle, which says plainly that waiting is cheap and what contention destroys is throughput, not power.

## Rules this gives you

- **One global atomic per shire, never per minion.** At 32 participants the serialisation is 320 cycles
  against a chip-wide barrier measured at 4,997 cycles — 6%, invisible. At 1,024 it is 10,240 cycles, twice
  the whole barrier, and it takes the hosting shire down with it.
- **Keep hot shared lines out of shires that compute.** The cost is not paid by the code touching the line.
  It is paid by whatever else lives in that shire, and it is total.
- **Below 20 concurrent remote requesters, or pace to 10,000 cycles.** Either keeps the bank unsaturated.
- **Spread rather than share.** One line per shire is the same instruction at 32× the rate and a seventeenth
  of the energy per operation.

## Not established

- **Why Ivan's number was 6%** rather than either 100% or 0.02%. Our reading is that his shire 0 did something
  local as well as the atomic — a poll, a flag read, the "am I last?" check a barrier makes — and that the
  local part is what starved. His code was not run.
- **Whether `l3_yield` would help a case the errata do not cover.** Not tested; not our register to set.
- **Whether a hot line makes its shire measurably hotter.** The card's thermal telemetry is one chip-wide
  mean, so this instrument cannot answer it. See [14-card-behaviour.md](14-card-behaviour.md).

## Related

- [19-observability-and-the-unmetered.md](19-observability-and-the-unmetered.md): the E29 bars on this page's
  energies, and the meter traps found on the way.
- [18-on-chip-relay.md](18-on-chip-relay.md): the barrier that hung on exactly this effect, and how the relay avoids it.
- [01-resources.md](01-resources.md): R11 (Ivan's result) and R12 (the brief that first analysed it, now corrected in
  place).
