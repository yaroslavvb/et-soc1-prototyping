# Heat per millimetre

[← Findings index](README.md) · published as [Heat per millimetre](https://spacesheep.dev/@yaroslavvb/et-soc1-heat-per-mm) (A17) · numbers and
sources: [05-claims.md](05-claims.md)

**Question (Q41):** Dally's rule of thumb says on-chip communication costs "~100 fJ/b-mm". What does moving a bit
one millimetre cost on the ET-SoC-1's mesh, measured, and does the rule hold?

**Answer:** at the mesh's own 0.485 V, with no other traffic on its links, a random bit costs **37 fJ per mm on the
mesh rail** (25 of it depending on the data, 12 not) and **47 fJ on board power**, which also carries the
regulator's loss. On a loaded mesh, where flows share links, it is **53 and 79 fJ**: like for like over one to four
hops, contention adds 49–61% on the mesh rail and 70–80% on board power (the range over the three cards). What costs
energy is not only bits that change between consecutive flits but **the ones carried**: an all-ones stream, which never
changes from flit to flit, costs 8–12% more per hop than random data on the mesh rail on all three cards (on board
power 5–9%, not resolved from zero on any card).
Dally's figure states no voltage. Scaled to 0.9 V, the voltage of the 40 nm figure it most likely descends from
(an inference; no source says so), the mesh rail's data-dependent cost is 85–107 fJ per bit·mm, so the rule holds to
within its own vagueness; read at the "~0.5V" his 2023 talk sets beside it, the figure is 3–4 times what this mesh
spends on the data. **Which process the figure is for, and whether the gap of about two below it is expected (Q63):**
no statement of it names a process; the one the page quotes is most likely CACM 2020's 14 nm cost model (an
inference), a number carried from 28–40 nm figures. The gap is expected: for a network-on-chip on "a typical chip say
five nanometer chip today" Dally himself gives "~50fJ/bit-mm" (NOCS keynote, 2022), half the rule; his group's own
scaling (SC14) takes a 28 nm wire to 7 nm at 0.46 of its energy, mostly through the lower voltage; and this mesh runs
below even 7 nm's nominal voltage. Piton (32 nm) and Raw (0.15 µm), measured the same way, scale to this mesh's cost
(below).

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
six dropped because the meter was starved. A third run, in the version-3 check of 26 September, repeated the random,
all-zeros and all-ones sets, free links and loaded mesh, in six passes on each of aifoundry2, aifoundry3 and aifoundry1
card 1 (`workloads/enercat/analyze_wire_v3.py`, `wire3.json`); every figure it covers comes from it, the three-term
model below from the second run.

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
hops (dimension-ordered routing on the recorded maps, x first, as the analysis assumed). E56 (29 September) measured
that read data travel y first; under y first the shares are 0, 22, 30, 55 and 78% (`wire.json`
`checks.link_sharing.<cfg>.shared_link_hop_fraction_yx`), and the page's route map draws y first since then. Over the same one to four hops, the loaded mesh costs **129
against 92 fJ per bit per hop** for the data-dependent part and 81 against 45 for the rest, on the mesh rail. Each
reader's bandwidth is within 6% of what it gets on free links, so flits are not held long; straight x-only flows
that share links cost as much as the loaded mesh, which points to sharing rather than turns.

## Against the rule of thumb

| fJ per random bit·mm | data-dependent | in all |
|---|---|---|
| mesh rail, free links, 0.485 V | 25 | 37 |
| board power, free links | 31 | 47 |
| mesh rail, loaded | 31 | 53 |
| board power, loaded | 49 | 79 |
| mesh rail data scaled to 0.9 V (× 3.44) | 85–107 | |
| Dally 2023 / CACM 2020 | 100 (no voltage, no activity) | |
| Keckler et al. 2011, 40 nm, 0.9 V | 121 | |
| Dally 2018, "in present day chips" | 20–40 | |
| a plain repeated 7 nm wire, first principles, 0.485 V | 12–24 | |

At equal voltage the mesh rail's data cost, routers included, is 0.7–0.9 of Keckler's 40 nm figure. Wire
capacitance per mm barely changes between nodes, so that is roughly what one would expect; the mesh's advantage
over the 0.9 V literature is mostly V². Only mesh-rail numbers are V²-scaled: board power carries the regulator's loss.

## Which process is Dally's figure for, and is a 2× gap expected? (Q63)

The owner asked on 28 September, from the page's Talk tab, which process Dally's figure refers to, and whether the
2× gap is expected or has other explanations. Dally cannot be asked, so the answer comes from his own talks and papers:
every statement found, with its quote, page or slide and URL, is in
`docs/reports/data/2026-09-24-wire-energy/research/DALLY-NODES.md`; `research/lit/dally_gap.py` prints the arithmetic
from the page's data, and the page's §7 has the table and the ranked explanations.

**No single process, by design, and for a network-on-chip on a modern process Dally himself gives half.** None of the
~100 fJ statements (CACM 2020; the 2023 Hot Chips and AHA talks) names a process, a voltage or how bits are counted.
CACM 2020 gives it twice inside a cost model whose arithmetic and local memory are "in 14 nm", says why it needs no
process ("Logic and local memory energies scale linearly with technology ... while supply voltage is held constant.
Communication energy remains roughly constant."), and the 2023 talks repeat that model's three numbers (100 fJ/b-mm,
50 fJ/b for a small RAM, ~1 fJ/b for an add); so if one process must be named it is 14 nm (an inference; at Hot Chips he
said it with Horowitz's table of 45 nm energies on the screen). The number is older: 110 fJ/bit-mm at 32 nm and 0.6 V in
the 2008 DARPA exascale study, whose authors include Dally (300 fF/mm, a full C V² per bit); 256-bit buses at 26 pJ,
256 pJ and 1 nJ on a slide labelled 28 nm (SC10 2010, SC12 2012, again to 2017; its 2009 version labels the bars
"64b 1mm Channel 25pJ/word" and "10mm 250pJ", and his 2010 notes call the longest "Corner to corner (32mm)": 100–122 fJ
per bit·mm, the same energies relabelled from a 64-bit word to a 256-bit bus); and 121 per random bit at 40 nm and 0.9 V
(Keckler, Dally et al. 2011). But in his 2022 keynote on networks-on-chip (NOCS), for "a typical chip say five nanometer chip
today", his slide puts the network's upper-layer wires at "~50fJ/bit-mm", and he says "going through the router is a
fraction of this energy". His other figures for chips of their own day run 20–50: 20–40 (VLSI 2018), "around 40 or 50"
at 16 nm with "nominal one volt supplies" (talks, 2021–22), 30 (CACM 2022), 50 (Hot Interconnects 2023: a 2 mm link at
0.1 pJ/b); and in 2015 his group's on-chip signaling work started from "200fJ/bit-mm".

| His figure | Process | Supply | fJ per bit·mm | Predicts here, per random bit·mm at 0.485 V |
|---|---|---|---|---|
| HPCA panel 2002, ACM Queue 2004 | 0.13 µm, stated | 1.2 V (Queue) | 313 (32 bits, 10 mm, 100 pJ) | 51 |
| Owens, Dally, Keckler et al., IEEE Micro 2007 | 22 nm, stated (for 2015) | 0.7 V | 250 (C V² per bit, links "fully active") | 30 (a quarter of a full charge) |
| DARPA exascale study 2008 | 32 nm, stated | 0.6 V | 110 (C V² per bit) | 18–35 (C V²/4 with its 300 fF/mm of wire, 600 with repeaters) |
| SC10, SC12 keynotes (2010, 2012; 2017) | 28 nm, the slide's label | — | ~100 | 29 / 48 / 94 if made at 0.9 / 0.7 / 0.5 V |
| Keckler, Dally et al., IEEE Micro 2011 | 40 nm, stated | 0.9 V | 121 (240 per transition) | 35 |
| same, 10 nm projections | 10 nm, stated | 0.75 / 0.65 V | 78 / 59 | 33 / 33 |
| Gebhart, Keckler, Dally et al., ISCA 2011 | 40 nm, the setting | 0.9 V | 59 (300 fF/mm, no repeaters) | 18 |
| Yale Patt 75 (2014; 2017) | 10 nm, stated | 0.7 V | 68 | 33 |
| HiPEAC keynote 2015 | 28 nm (inferred: a GM2xx test site) | — | 200 (a baseline) | 58 / 96 / 188 |
| VLSI Symposium 2018 | 16 nm, the paper's setting | — | 20–40 | 12 (C V²/4 with its 200 fF/mm) |
| CACM 2020 | 14 nm, the cost model's | — | 100 | 29 / 48 / 94 |
| Deep Learning Hardware talks 2021–22 | 16 nm, the slide | ~1 V, spoken | 40–50 | 9–12 |
| CACM 2022 | none ("today") | — | 30 | 9 / 14 / 28 |
| **NOCS keynote 2022** | **5 nm, spoken** | — | **~50 (NoC wires)** | 15 / 24 / 47 |
| Hot Chips and AHA retreat 2023 | none (the 14 nm model's numbers) | — | ~100 | 29 / 48 / 94 |
| Hot Interconnects 2023 | none | — | 50 | 15 / 24 / 47 |
| Zhu, Rucker, Wang, Dally (SatIn), 2023 | 32 nm, stated | 1.05 V | 200 (per bit sent; routers "almost no power") | 11 (a quarter of a full charge) |
| **This mesh, mesh rail** | 7 nm (TSMC) | 0.485 V | data 25–31; in all 37–53 | |

**Is a 2× gap expected? Yes, by Dally's own numbers, and most of it is voltage.** His 5 nm network-on-chip figure, 50,
is half his rule of thumb, and this 7 nm mesh at 0.485 V measures 37–53 in all, about that figure as stated. His
group's model (Villa, Keckler, Dally et al., SC14, Table II) takes a fixed length of wire from 28 nm to 7 nm at ×0.46 of
its energy, with nominal supplies from 0.90 V to 0.70 V (×0.60 of it voltage, ×0.76 the rest); of wires themselves he says "the
wires have sort of a constant c" (2022). Taken on to this mesh's 0.485 V, below 7 nm's
nominal, a wire costs 22–29 fJ per bit·mm by his rule (the 28 nm slide or the 14 nm model, scaled by SC14) and 24 by
his 5 nm figure if it was made at 0.70 V; the mesh rail measures 25–31 for the data and 37–53 in all, the rest being
routers, clocking and contention. It is not unusually frugal: the two other meshes measured on silicon with the data's
switching controlled scale to the same, Piton (IBM 32 nm SOI, 1.0 V, HPCA 2018) to 24–26 fJ per bit·mm for data
switching like random data plus 11–12 for none, Raw (IBM 0.15 µm, 1.8 V, ISLPED 2003) to 24; per mm of hop all three
switch about the same capacitance for the data (410, 414–450 and 420–530 fF). What the process changes is mostly the
voltage it runs at. Only a 100 per random bit made at the ~0.5 V the 2023 talk recommends would leave the mesh 1.8–2.6
times below the rule, and that would need 1,600 fF/mm, 8 times his 200.

**Which 2×.** (a) The measurement as it stands, 37–53 against 100 (0.37–0.53 of it): the one above, most likely the
one meant. (b) Everything scaled to 0.9 V, 126–182, up to 1.8 times 100: expected, since it scales clocking, flops,
headers and contention as if they were wire (the data alone at 0.9 V is 85–107). (c) Dally against himself, 20–50 for chips
of their own day and ~200 for conventional full-swing wires (2014–15 talks: "roughly 200 femtojoule per bit
millimeter"), against 100: a factor of two either way; 20–40 is C V²/4 of a bare
200 fF/mm wire (0.63–0.89 V by his own formula), while the 100 descends from tables of a repeated wire of 600 fF/mm (300
of wire, 300 of repeaters in the 2008 study, just what the 2011 table's 240 per transition and 121 per random bit at
0.9 V imply; an inference).

**Explanations, ranked with sizes** (the page's §7 table has how to test each):
1. supply voltage: ÷2.1–3.4 from the nominal 0.70–0.90 V his group gives 7–28 nm to 0.485 V (÷1.5–3.4 from the
   0.6–0.9 V his dated figures state);
2. how bits are counted: up to ÷4; for one 600 fF/mm wire at 0.9 V his group has written "about 0.5pJ/mm" per bit
   (C V², 2008), 240 per transition and 121 per random bit (2011); on this mesh a random bit costs 1.2 times a
   flit-to-flit difference, because ones cost too;
3. what a hop counts (routers, flops, clock, headers, the request): everything is 1.5–1.7 times the data part, and the
   data part 1.1–2.7 times a plain 7 nm wire's 12–24 fJ; the data-independent part is 33–41% of a hop (Piton: 32%;
   Dally, NOCS 2022: the router is "a fraction" of a tile's wire energy);
4. contention: +49–61% per mm, loaded against free links over 1–4 hops;
5. the meter: board power is 1.3–1.5 times the mesh rail (the regulator's loss);
6. ones carried: the per-one term is 57% of a random bit's data cost; all ones cost 8–12% more per hop than random;
7. wire kind, metal layer, swing: unknown here (top metal about 0.6 of the middle layers' capacitance; low swing ½–¾
   less);
8. routed length against the 3.72 mm pitch: can only lower the cost per mm of wire; size unknown;
9. the process node apart from its voltage: ×0.76 from 28 to 7 nm (SC14), ×0.93 from 40 to 10 nm (2011–14 tables); for
   logic he expects 2–2.5× from 16 to 5 nm (2021), for wires "sort of a constant c" (2022);
10. temperature: small.

Tests: a step of the mesh rail's voltage (firmware allows 485–600 mV; full swing at 0.6 V should cost ×1.53; it needs
the owner's approval, since it changes a shared card) separates voltage, and full from low swing; hops through a
1.74–1.80 mm memory-shire column against the 3.72 mm tiles separate per hop from per mm; the link circuit, metal stack
and floorplan are questions for Esperanto's documents.

## In practice

- A random byte costs **1.58–2.34 pJ per hop** on the loaded mesh (mesh rail to board, everything included).
- A 64-byte line carried between the two farthest shires (10 hops, about 37 mm of mesh travel, extrapolated from
  1–6) costs 1.0–1.5 nJ in hops, against 8.5 nJ to read it from DRAM by random-data tensor load (132.6 pJ/B, like for
  like with the 4.43 pJ/B own-scratchpad read; the energy manual's three-card values): the whole hand-off, far
  scratchpad read and exit included, about 2.0 nJ, is about 4.3× cheaper than DRAM on the same meter. Each hop adds
  about half of what reading the byte from the shire's own scratchpad costs (2.34 against 4.43 pJ/B, 53%, board power).
- In Dally's currency, a 32-bit operand crossing one hop costs 9.4 pJ of board power, about 1.8 lanes of `fadd.ps`
  on random data: one lane of a vector float add is worth about 0.5 of a hop, some 2.0 mm (200 times Dally's
  10 µm); a scalar `fadd.s` (26.3 pJ) is worth about three hops.

## Lanes and flits

Blocks of 16–128 bytes cost the same and 256-byte blocks cost more, as the shire's four mesh lanes predict (a line
goes to lane PA[7:6], so consecutive lines on one lane are 256 bytes apart), and a flit carries at least a 64-byte
line. On the mesh rail the 256-byte excess is 55% (aifoundry2) and 53% (aifoundry3) of a full flip per hop; on board
power 67% and 71%, not resolved from a full flip (the pooled 54% and 69% of the first write-up). It does not fall as
more links are shared (0.35 pJ/B per hop from one to three hops, 0.45 from three to six, on the mesh rail); why it
falls short of a full flip is open.

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
  y-only sets differ in link sharing as well as in direction, so they cannot separate router from wire either.
- **Which circuit makes ones cost.** Resting-at-zero logic and precharged structures both fit; slowing the flows at a
  fixed distance would tell them apart.
- **The meters.** The mesh rail's gain has not been checked independently. Board-power coefficients move 4–9% with the
  leakage correction; the mesh-rail ones do not move.
- **The fixed part may be partly per second rather than per hop.** Bandwidth per reader falls with distance. On the
  mesh rail at most 27% of the free-link fixed part and 18% of the loaded one could be per second. On board power,
  whose one-hop energy also holds the scratchpad read and the cores, the same bound for the link-disjoint part is 84%
  on aifoundry2, 93% on aifoundry3 and 104% on aifoundry1's card 1, poorly determined (upper 99% bounds 118–137%;
  E42), and 56% for the loaded one (98% and 58% in the first write-up), so it cannot rule out that most of the
  board's fixed part is per second. The data-dependent part is immune.
- **Voltage scaling** assumes full-swing links at constant capacitance; whether the links are low-swing is not known.
- **Ten hops is an extrapolation** from one to six.

## Related

- [18-on-chip-relay.md](18-on-chip-relay.md): the relay whose hand-off this prices per hop.
- [19-observability-and-the-unmetered.md](19-observability-and-the-unmetered.md): the meter chain, and the first
  starved-meter case.
- [03-experiments.md](03-experiments.md), E27: the energy manual's first wire fit, which the 8-hop point pulls low.
- [14-card-behaviour.md](14-card-behaviour.md): the traps found during these runs.
