# Heat per millimetre

[← Findings index](README.md) · published as [Heat per millimetre](https://spacesheep.dev/@yaroslavvb/et-soc1-heat-per-mm) (A17) · numbers and
sources: [05-claims.md](05-claims.md)

**Question (Q41):** Dally's rule of thumb says on-chip communication costs "~100 fJ/b-mm". What does moving a bit
one millimetre cost on the ET-SoC-1's mesh, measured, and does the rule hold?

**Answer:** at the mesh's own 0.485 V, with no other traffic on its links, a random bit costs **36 fJ per mm on the
mesh rail** (25 of it depending on the data, 12 not) and **47 fJ on board power**, which also carries the
regulator's loss. On a loaded mesh, where flows share links, it is **50 and 73 fJ**: contention adds 40–45% on the
mesh rail and 55–65% on board power. What costs energy is not only bits that change between consecutive flits but **the
ones carried**: an all-ones stream, which never changes from flit to flit, costs 7–9% more per hop than random data.
Dally's figure states no voltage. Scaled to 0.9 V, the voltage of the 40 nm figure it most likely descends from
(an inference; no source says so), the mesh rail's data-dependent cost is 85–105 fJ per bit·mm, so the rule holds to
within its own vagueness; read at the "~0.5V" his 2023 talk sets beside it, the figure is 3–4 times what this mesh
spends on the data.

Evidence: [E31, E32](03-experiments.md); the literature and die geometry are [R14](01-resources.md). Published as
[A17](04-artifacts.md), after an adversarial review by a workflow of six AI agents whose corrections are applied
(`docs/reports/data/2026-09-24-wire-energy/review/`). A *hop* is one step between neighbouring stops of the mesh
network-on-chip; a *flit* is the unit the mesh moves as a whole, here at least one 64-byte line
([terms](README.md#terms)).

---

## How long is a hop

Esperanto publishes the die area (570 mm²) and a die plot. The tile period measured on the plot and scaled to that
area gives **3.73 mm in x and 3.70 mm in y**, so a hop is **3.72 mm** (3.64–3.74 over three readings of what the
area covers). "Per mm" throughout means per mm of mesh travel, one router plus one link per 3.72 mm; the metal
actually routed can only be longer, so per mm of wire the cost would be lower.

## The experiment

Hart 0 of every minion streams 1 KB tensor loads from the scratchpad of a shire exactly *d* hops away (*d* = 0 is
the shire's own and never touches the mesh). The energy per payload byte is fitted against *d*: **the slope is the
cost of one hop**. Every scratchpad is filled beforehand with a known image, checked byte for byte on the card, so
the bits on the links are chosen:

- bits independently 1 with probability *P* (two consecutive data flits then differ in a bit with probability
  2*P*(1−*P*) — a difference rate between flits, not necessarily the transition rate on the wires);
- blocks of N bytes alternately all-zero and all-one;
- the second run (E32): every line on the chip unique, *P* and 1−*P* exact complements, a frozen line (half ones,
  no two flits differ), and pairs chosen so that no two flows share a directed link.

Two meters: board power (bracketed by idle, leakage-corrected) and the service processor's reading of the mesh
(NoC) rail at 0.485 V and 400 MHz. Three passes in shuffled order on each of aifoundry2 and aifoundry3; 756 bursts,
six dropped because the meter was starved.

## What a hop costs, and what it depends on

The per-hop cost fits three terms on both cards and both meters, to 0.01 pJ/B per hop on the mesh rail and 0.04 on
board power:

  E_hop = s0 + a · 2P(1−P) + b · P

| Loaded mesh, second run | mesh rail, fJ per hop | fJ per mm | board, fJ per hop | fJ per mm |
|---|---|---|---|---|
| *a*: per bit that differs from the previous flit | 98 [92–103] | 26.4 | 151 [139–162] | 40.6 |
| *b*: per one carried | 129 [127–133] | 34.8 | 192 [180–205] | 51.6 |
| a random bit, data-dependent (½a + ½b) | 114 | 30.6 | 172 | 46.1 |
| a bit, independent of the data (*s0*) | 74 | 19.8 | 100 | 26.8 |

The first run, with a repeated image, gives the same coefficients (95 and 131 on the mesh rail). The complement
test agrees: *P* = ¾ against *P* = ¼ (equal differences, half a unit of ones) gives 132 fJ per one [125–138 over passes and cards].

**b > a does not by itself make a one costlier than a flip.** Ordinary logic whose output rests at 0 between
trains of flits produces exactly this model: each one rises and falls at the ends of a train, *a* = f·E_t and
*b* = 2(1−f)·E_t, where f is the fraction of flits followed directly by another. The fitted b/a gives f ≈ 0.6 and
E_t ≈ 163 fJ per transition per hop, about 370 fF/mm, ordinary wire capacitance. Precharged structures would also
give a cost per one. The practical point stands either way: **zeros are cheap to move, ones are not**; all-ones data
stored complemented would cost 36% of what it does now.

## Sharing a link costs energy

In the all-pairs traffic, link sharing grows with distance: 0, 22, 32, 55 and 72% of link-hops at 1, 2, 3, 4 and 6
hops (dimension-ordered routing on the recorded maps). Over the same one to four hops, the loaded mesh costs **119
against 91 fJ per bit per hop** for the data-dependent part and 76 against 43 for the rest, on the mesh rail. Each
reader's bandwidth is within 6% of what it gets on free links, so flits are not held long; straight x-only flows
that share links cost as much as the loaded mesh, which points to sharing rather than turns.

## Against the rule of thumb

| fJ per random bit·mm | data-dependent | in all |
|---|---|---|
| mesh rail, free links, 0.485 V | 25 | 36 |
| board power, free links | 33 | 47 |
| mesh rail, loaded | 31 | 50 |
| board power, loaded | 46 | 73 |
| mesh rail data scaled to 0.9 V (× 3.44) | 85–105 | |
| Dally 2023 / CACM 2020 | 100 (no voltage, no activity) | |
| Keckler et al. 2011, 40 nm, 0.9 V | 121 | |
| Dally 2018, "in present day chips" | 20–40 | |
| a plain repeated 7 nm wire, first principles, 0.485 V | 12–24 | |

At equal voltage the mesh rail's data cost, routers included, is 0.7–0.9 of Keckler's 40 nm figure. Wire
capacitance per mm barely changes between nodes, so that is roughly what one would expect; the mesh's advantage
over the 0.9 V literature is mostly V². Only mesh-rail numbers are V²-scaled: board power carries the regulator's loss.

## In practice

- A random byte costs **1.50–2.17 pJ per hop** on the loaded mesh (mesh rail to board, everything included).
- A 64-byte line carried between the two farthest shires (10 hops, about 37 mm of mesh travel, extrapolated from
  1–6) costs 1.0–1.4 nJ in hops, against 8.3 nJ to read it from DRAM by random-data tensor load (129 pJ/B, like for
  like with the 4.21 pJ/B own-scratchpad read): the whole hand-off, far scratchpad read and exit included, about
  1.8 nJ, is about 4.5× cheaper than DRAM on the same meter. Each hop adds about half of what reading the byte from
  the shire's own scratchpad costs (2.17 against 4.21 pJ/B, board power).
- In Dally's currency, a 32-bit operand crossing one hop costs 8.7 pJ of board power, about 1.6 lanes of `fadd.ps`
  on random data: one lane of a vector float add is worth about 0.6 of a hop, some 2.3 mm (230 times Dally's
  10 µm); a scalar `fadd.s` (25.5 pJ) is worth about three hops.

## Lanes and flits

Blocks of 16–128 bytes cost the same and 256-byte blocks cost more, as the shire's four mesh lanes predict (a line
goes to lane PA[7:6], so consecutive lines on one lane are 256 bytes apart), and a flit carries at least a 64-byte
line. The 256-byte excess is 69% of a full flip per hop on board power and 54% on the mesh rail, and it does not fall
as more links are shared; why it falls short is open.

## Things that bit us

- **Stray stores to physical address 0.** A new store mode missing from the host's memory-mode list sent tensor
  stores from shire 0 to PA 0 in two test launches. Nothing reported it; `enercat_host` now refuses a memory pattern
  with no slice. See [14-card-behaviour.md](14-card-behaviour.md).
- **The poisoned management queue.** Killing the sampler mid-request stopped the second run's first start on both
  cards. Drained with one `dev_mngt_service` call; `ettelem` now exits cleanly on SIGTERM.
- **The starved meter, second case.** On aifoundry2, loads between shires in the same column three hops apart took
  each telemetry read to 0.8–1.6 s; those six bursts are dropped.
- **Distance ranges.** The first draft compared the free-link set over 1–5 hops with the loaded set over 1–4; the
  review caught it, and both are now fitted over 1–4.

## Not established

- **Router against wire.** Every hop is one router plus one pitch of link; the data cannot split them. The x-only and
  y-only sets agree only to about 10% and differ in link sharing, so they do not test it.
- **Which circuit makes ones cost.** Resting-at-zero logic and precharged structures both fit; slowing the flows at a
  fixed distance would tell them apart.
- **The meters.** The mesh rail's gain has not been checked independently. Board-power coefficients move 4–9% with the
  leakage correction; the mesh-rail ones do not move.
- **The fixed part may be partly per second rather than per hop.** Bandwidth per reader falls with distance. At most a
  quarter of the free-link fixed part could be per second; the data-dependent part is immune.
- **Voltage scaling** assumes full-swing links at constant capacitance; whether the links are low-swing is not known.
- **Ten hops is an extrapolation** from one to six.

## Related

- [18-on-chip-relay.md](18-on-chip-relay.md): the relay whose hand-off this prices per hop.
- [19-observability-and-the-unmetered.md](19-observability-and-the-unmetered.md): the meter chain, and the first
  starved-meter case.
- [03-experiments.md](03-experiments.md), E27: the energy manual's first wire fit, which the 8-hop point pulls low.
- [14-card-behaviour.md](14-card-behaviour.md): the traps found during these runs.
