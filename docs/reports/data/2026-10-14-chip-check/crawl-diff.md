## ask/0
die view: every die position (the logical map turned onto … the map before the renaming and is superseded. Still open: [-whether-] {+which east-west handedness+} the silicon has [-this handedness or the-] {+(the+} published die [-plot's (I/O-] {+plot is not the mirror: it keeps the PCIe and I/O cells at the east end and swaps them, I/O+} then PCIe, [-the mirror);-] {+fact L24);+} a floorplan with labelled mesh stops, a die plot with … and a final datasheet, with the chip's thermal ratings ↗

## ask/11
the DRAM chip's share of a load (memory shire panel) | About [-25-28-] {+28+} of a DRAM load's cycles are the DRAM's own timing; … The memory shire's description, or its programmed DDR registers ↗

## ask/12
the tensor unit's cache path (tensor sequencer, L1 scratchpad) nearly … L3; tensor stores skip the L1 and L2 (energy manual; {+the+} PRM [-confirms only-] {+states that loads bypass the L1, pdf p.275, and that stores bypass+} the L1 [-bypass).-] {+and the L2, pdf p.306 and p.309).+} The L2 part is measured (E57, 29 September): a second … tensor-loaded lines? A second TensorLoad of the same lines ↗

## electrons/0
An "off" transistor's [-channel,-] {+channel+} at any instant {+(the chip's average at 80 °C)+} | 0.002 electrons | model

## electrons/1
[-An "on" transistor's channel,-] {+One fin's channel when on,+} at the minion rail | 85-120 electrons | inference

## electrons/7
Leaking [-through an "off"-] {+per+} transistor, every second {+(the chip's average at 80 °C)+} | 10 billion electrons a second | model

## fact/L08
The 6-column shire grid spans about 22.2 mm, 86% of … millimetre | model | | docs/reports/data/2026-09-24-wire-energy/research/SYNTHESIS.md §1a row 'Shire-grid span'; [-docs/reports/2026-09-24-heat-per-mm.html:269-276-] {+docs/reports/2026-09-24-heat-per-mm.html:294-302+} (§2 text)

## fact/L103
A shire has 4 to_l3 master and 4 L3 slave lanes to the [-mesh;-] {+mesh. An L3 request takes+} the lane [-is chosen by PA[7:6],-] {+of the bank it will use at its home, PA[12:11] under the default swizzle,+} so {+all 16 lines of an aligned 1 KB load share one lane; only a remote-scratchpad request takes the lane PA[7:6] names, so its+} lines i and i+4 share a lane [-(a 1 KB load puts 4 of its 16 lines on each).-] {+(re-implementation RTL, to confirm in silicon).+} Heat per millimetre | documented | | docs/reports/data/2026-09-24-wire-energy/report.json [-inputs.lanes (core-et-main shirecache_mesh_master.sv:141-153);-] {+inputs.lanes; external/core-et-main/hw/ip/shirecache/rtl/shirecache_mesh_master.sv:127-153 (the port is the low bits of req_bank_id: the L3 swizzle's bank, or PA[7:6] for a remote scratchpad); external/core-et/docs/CORE-ET-Shire-Cache-Specification.pdf p.6 (L3 requests go to banks by PA[12:11]);+} docs/reports/data/2026-09-24-wire-energy/research/SYNTHESIS.md §1b 'Lanes' {+(which reads PA[7:6] for every request)+}

## fact/L105
Each {+minion, PCIe and I/O shire's+} mesh stop has 9 main-NoC routers (layers 0–8) plus one debug-NoC router; {+the NoC register map has 36 copies of layers 0–1 and 44 of layers 2–8, so the 8 memory shires' stops most likely have 7 (layers 2–8);+} routers have 8 ports (H, E, S, W, N, I, … rows 'Main-NoC layers', 'Router ports and VCs', 'Error protection' (etsoc_shire_other_esr.h:3877-3981; [-noc_esr.h)-] {+noc_esr.h); external/et-platform/etsoc-hal/include/hwinc/noc_esr.h:15498, 15628, 15758, 16538 (NOC_ESR_ROUTER_n_ARRAY_COUNT); external/et-man/ET Programmer's Reference Manual.pdf p.479 (PCIe shire NOC_INT_STAT 8:0)+}

## fact/L116
Inside a shire only the reduction-tree edges are fast: 68 … three cards. On-chip communication | measured | three cards | [-docs/reports/2026-09-18-et-soc1-on-chip-communication.html:735-742;-] {+docs/reports/2026-09-18-et-soc1-on-chip-communication.html:774-780;+} embedded nocbench-data primitives.tree_pairs, tree_hop (68.1), other_hop (114.1)

## fact/L120
One temperature sensor and one process detector in each minion {+shire, the PCIe+} shire and the I/O shire (36 [-each),-] {+each, as PRM Fig. 1-3 draws them; the RTL removed the PCIe shire's pair and the firmware reads 35: fact L121),+} 8 voltage-monitor blocks with up to 128 remote sense points, … Programmer's Reference Manual.pdf p.17 §1.6 and p.18 Figure 1-3, Table [-1-6-] {+1-6; external/core-et/rtl/inc/pvt_defines.vh:16-26 ('Pshire no longer has ts/pd (RTLMIN-3619)')+}

## fact/L121
35 sensors are read: TS0–TS31 for the compute shires (TSn … no sensor. Spatial temperature: a brief | documented | | [-docs/reports/2026-09-22-et-soc1-spatial-temperature-brief.html:786-] {+docs/reports/2026-09-22-et-soc1-spatial-temperature-brief.html:822+} (caption) and [-:789-790-] {+:827-828+}

## fact/L123
Per-shire on-die voltage at idle (34 minion shires): minion rail … mV. Power and temperature telemetry | measured | aifoundry2 | [-docs/findings/05-claims.md:41-] {+docs/findings/05-claims.md:49+} (docs/reports/data/2026-09-20-power-aifoundry2/per-shire-voltage-idle.json)

## fact/L24
Top-row order conflicts between sources: PRM Fig. 1-3 has PCIe … caption has I/O (purple, Maxion) fifth and PCIe (orange) sixth. [-The-] {+Both put the pair at the east end of the top row: the die plot swaps the+} two [-are-] {+cells (an east-west+} mirror [-images.-] {+would move them to the west end).+} Heat per millimetre | documented | | docs/reports/data/2026-09-24-wire-energy/research/SYNTHESIS.md §1a row 'Top-row order'; [-docs/reports/sources/heat-per-mm.script.js:102-] {+docs/reports/sources/heat-per-mm.script.js:103+} ('the two sources disagree on the order')

## fact/L31
The four grey cells of the logical map are (0,3), … is which was not measured. On-chip communication | measured | [-card not recorded-] {+three cards+} | [-workloads/nocbench/analyze.py:50-51,60-] {+workloads/nocbench/analyze.py:54-55, 64+} (EMPTY); [-docs/reports/2026-09-18-et-soc1-on-chip-communication.html:719; docs/reports/2026-09-22-et-soc1-spatial-temperature-brief.html:786-] {+docs/reports/2026-09-18-et-soc1-on-chip-communication.html:749; docs/reports/2026-09-22-et-soc1-spatial-temperature-brief.html:822+}

## fact/L32
Inferred identities: (0,4) and (0,5) are the I/O and PCIe … inference | | docs/reports/data/2026-09-24-wire-energy/research/SYNTHESIS.md §1a row 'Logical map vs die'; [-docs/reports/2026-09-22-et-soc1-spatial-temperature-brief.html:765-786-] {+docs/reports/2026-09-22-et-soc1-spatial-temperature-brief.html:800-822+} (cells labelled 'master or spare' and 'I/O or PCIe', 'inferred'); superseded 27 Sep by fw.grey-cells

## fact/L33
The logical map [-appears to be-] {+is+} the die [-turned-] {+view transposed (x and y swapped:+} a [-quarter:-] {+quarter turn plus a mirror):+} in map orientation the memory shires sit above and below … runs east–west (die columns). On-chip communication | inference | | [-docs/reports/2026-09-18-et-soc1-on-chip-communication.html:719; docs/reports/2026-09-19-et-soc1-memory-anatomy.html:780-783; docs/et-soc1-notes.md:104-105;-] {+docs/reports/2026-09-18-et-soc1-on-chip-communication.html:749; docs/reports/2026-09-19-et-soc1-memory-anatomy.html:812-815; docs/et-soc1-notes.md:117-118;+} docs/reports/data/2026-09-24-wire-energy/research/SYNTHESIS.md §1a row 'Logical map vs die'; settled 27 Sep by fw.map-match except the handedness (die.handedness)

## fact/L34
Die-orientation 8 × 6 view (north row first, west column … None. Heat per millimetre | inference | | derived from [-workloads/nocbench/analyze.py:52-60-] {+workloads/nocbench/analyze.py:56-64+} (MARTY) with the mapping of docs/reports/data/2026-09-24-wire-energy/research/SYNTHESIS.md §1a ('Logical x runs … = bottom row col 4') and the memory-shire fit of [-docs/reports/2026-09-19-et-soc1-memory-anatomy.html:864;-] {+docs/reports/2026-09-19-et-soc1-memory-anatomy.html:908;+} settled 27 Sep by fw.map-match except the handedness (die.handedness)

## fact/L40
Fitting DRAM latency with one shared constant plus 12 cycles … access | measured | aifoundry2 | docs/reports/data/2026-09-19-memprobe-aifoundry2/summary.json decomp.ms_pos, decomp.ms_fit_sqerr; workloads/memprobe/analyze.py:111-127; [-docs/reports/2026-09-19-et-soc1-memory-anatomy.html:862-865-] {+docs/reports/2026-09-19-et-soc1-memory-anatomy.html:906-909+}

## fact/L42
Memory shire 2's position is a tie-break: its four home … Anatomy of a memory access | measured | aifoundry2 | [-docs/reports/2026-09-19-et-soc1-memory-anatomy.html:778-780; docs/reports/2026-09-18-et-soc1-on-chip-communication.html:719-] {+docs/reports/2026-09-19-et-soc1-memory-anatomy.html:810-812; docs/reports/2026-09-18-et-soc1-on-chip-communication.html:749+}

## fact/L43
The memory shire that serves a line is picked by … of a memory access | measured | three cards | [-docs/reports/2026-09-19-et-soc1-memory-anatomy.html:834, 858-861;-] {+docs/reports/2026-09-19-et-soc1-memory-anatomy.html:873, 902-905;+} docs/research/counters-and-dram.md:66-69

## fact/L44
With the memory shires one hop outside the grid, the … home). Anatomy of a memory access | model | | [-docs/reports/2026-09-19-et-soc1-memory-anatomy.html:743-] {+docs/reports/2026-09-19-et-soc1-memory-anatomy.html:772+}

## fact/L45
Whole DRAM load: latency = 110 + 12·hops(requester → L3 … fitted, the model is within ±3 cycles for 97% of [-loads-] {+lines (each line's fastest of three loads)+} on aifoundry2, 93% on aifoundry3 and 94% on aifoundry1's card [-1.-] {+1; on the 19 September fitting run, 83% of single loads were within ±3 cycles (aifoundry2).+} Anatomy of a memory access | measured | three cards | [-docs/reports/2026-09-19-et-soc1-memory-anatomy.html:866-873-] {+docs/reports/2026-09-19-et-soc1-memory-anatomy.html:910-917+}

## fact/L46
Of the 91-cycle memory-shire constant (152 ns), the DRAM chip accounts for about [-25–28-] {+28+} cycles (activate tRCD 11 cycles = 18 ns, 19.3 ns read latency, [-one or-] {+the+} two 4.3 ns [-bursts);-] {+bursts of a 64-byte line); the rest,+} at most [-~63–66-] {+~63+} cycles [-(~105–110 ns) are-] {+(~105 ns), is the L3 home's miss handling (about 12 cycles by the spec: an L3 miss is 42 shire clocks against 30 for a hit) and+} the memory [-shire itself:-] {+shire:+} controller queue, PHY and the crossings between the 933 MHz DDR clock and the mesh. Anatomy of a memory access | model | | [-docs/reports/2026-09-19-et-soc1-memory-anatomy.html:888-893-] {+docs/reports/2026-09-19-et-soc1-memory-anatomy.html:937-942; external/core-et/docs/CORE-ET-Shire-Cache-Specification.pdf p.11 Table 1 (L3 read hit 30 shire clocks, L3 read miss 42 plus the NoC and memory)+}

## fact/L70
TensorSend 32 B round trip between shires = 150 + … three cards. On-chip communication | measured | three cards | [-docs/reports/2026-09-18-et-soc1-on-chip-communication.html:725-] {+docs/reports/2026-09-18-et-soc1-on-chip-communication.html:764+} and embedded nocbench-data v3.cards.<card>.matrices['matrix-pingpong'].b; [-docs/findings/05-claims.md:412-] {+docs/findings/05-claims.md:446+}

## fact/L71
Intercept of the between-shire round trip: 150 cycles (the fixed cost of leaving and re-entering shires). On-chip communication | measured | three cards | [-docs/reports/2026-09-18-et-soc1-on-chip-communication.html:725; docs/findings/05-claims.md:412-] {+docs/reports/2026-09-18-et-soc1-on-chip-communication.html:764; docs/findings/05-claims.md:446+} (149.96–150.08 over passes)

## fact/L72
Each mesh hop adds 20 ns round trip: 12 minion … 496 pairs. On-chip communication | measured | three cards | [-docs/reports/2026-09-18-et-soc1-on-chip-communication.html:709-] {+docs/reports/2026-09-18-et-soc1-on-chip-communication.html:739+} (KPI); [-docs/reports/2026-09-19-et-soc1-memory-anatomy.html:841-844; docs/et-soc1-notes.md:90-91-] {+docs/reports/2026-09-19-et-soc1-memory-anatomy.html:880-883; docs/et-soc1-notes.md:98-99+}

## fact/L79
Where the requester sits matters: L3 (4 MB working set) … three cards. Memory hierarchy | measured | three cards | [-docs/findings/05-claims.md:410-] {+docs/findings/05-claims.md:444+} (V3R/lat.json LAT-M2)

## fact/L80
Why: the mean distance to the 32 L3 slices is … here from workloads/nocbench/analyze.py MARTY (hops) and the 12 cycles/hop of [-docs/reports/2026-09-19-et-soc1-memory-anatomy.html:837-] {+docs/reports/2026-09-19-et-soc1-memory-anatomy.html:876+}

## fact/L86
Ring energy slope per mean hop by card: aifoundry2 1.78 … intervals, 6 passes each); no pair of cards differs; pooled [-1.75 (the page gives ±50%).-] {+1.75, 1.40–2.10 at 99% over the 18 passes (±20%).+} On-chip communication | measured | three cards | [-docs/findings/05-claims.md:450-] {+docs/findings/05-claims.md:489+} (V3R/rl.json [-RL-a)-] {+RL-a); docs/reports/2026-09-18-et-soc1-on-chip-communication.html:923 (pooled 1.75, 1.40–2.10 at 99% over the 18 passes)+}

## fact/L87
Inside a shire, messaging costs 0.7–2.2 pJ per byte with … shire boundary. On-chip communication | measured | three cards | [-docs/reports/2026-09-18-et-soc1-on-chip-communication.html:703-] {+docs/reports/2026-09-18-et-soc1-on-chip-communication.html:733+} (lede), [-:711-] {+:741+} (KPI), [-:783-] {+:831+}

## fact/L88
A random bit moved 1 mm over free links at … fJ. Heat per millimetre | measured | three cards | [-docs/findings/05-claims.md:341, 444-] {+docs/findings/05-claims.md:362, 482+} (V3R/wire.json WIRE-P1-16/P11a, P11b); docs/reports/data/2026-09-24-wire-energy/report.json headline

## fact/L91
The shire boundary is a bandwidth cliff: with every minion … 600 MHz. On-chip communication | measured | three cards | [-docs/reports/2026-09-18-et-soc1-on-chip-communication.html:703, 775, 816;-] {+docs/reports/2026-09-18-et-soc1-on-chip-communication.html:733, 822, 866;+} embedded nocbench-data scp_remote_gbps_600

## fact/L93
Handing a result to the next shire instead of through … on-chip relay vs DRAM | measured | three cards | [-docs/findings/05-claims.md:451-] {+docs/findings/05-claims.md:490+} (V3R/rl.json)

## fact/L94
In the relay, which shire receives the slab moves bandwidth … by ID (3.5 hops on average, longest hand-off 10) to [-733-] {+734+} GB/s at 16 shire IDs (2.1, longest 6); bandwidth falls … the next shire: on-chip relay vs DRAM | measured | [-aifoundry2, aifoundry3-] {+three cards+} | [-docs/findings/05-claims.md:254 (DATAO/onchip.json distance[])-] {+docs/reports/data/2026-09-22-onchip-aifoundry2/onchip.json distance[].by_card (version 3, three cards); docs/findings/05-claims.md:266 (the 22 Sep session: 733)+}

## fact/addr.load-model
Measured load-to-use model from any requesting shire at 600 MHz: … of a memory access | measured | three cards | [-docs/et-soc1-notes.md:164-166;-] {+docs/et-soc1-notes.md:177-179;+} anatomy page §1 'Trace one load' and headline tiles; [-docs/findings/05-claims.md:403-404-] {+docs/findings/05-claims.md:434-435+} (V3 check: L3 within ±4 cycles for 99.4-99.97% of lines, DRAM within ±3 for 93-97%)

## fact/ar.tree
The allreduce benchmark's tree: at level h, a minion whose … | | workloads/nocbench/kernel/nocbench.c:279-288 (tree: TensorReduce for levels 0..top, TensorBroadcast back), [-:516-521-] {+:516-522+} ('Minion m receives at levels below ctz(m) and sends at … receives at every level'); fact neigh.fln-edges for the tree edges

## fact/board.meters
The PMIC meters the 12 V input and three regulators … aifoundry3). Limits of observability | measured | three cards | [-docs/findings/05-claims.md:330, 438-] {+docs/findings/05-claims.md:349, 476+} (docs/reports/data/2026-09-25-claims-v3/results/tel.json TEL-P1); docs/research/power-telemetry.md:39-56

## fact/bw-dram
DRAM streaming: 76 GB/s for the whole chip (0.124 B … (bpc 0.1235, gbps 75.9), .spec (gbps 119.5; datasheet max 136.5); [-docs/findings/05-claims.md:370-] {+docs/findings/05-claims.md:398+}

## fact/bw-l2
L2 cache, 1 KB tensor loads by every minion: 2.45 … aifoundry3 | ridge-data: levels[l2].measured (bpc 3.999, gbps 2,452), .spec.bpc 8.0; [-docs/findings/05-claims.md:370-] {+docs/findings/05-claims.md:398+}

## fact/card.dip
The card has DIP switches to set all its boot options. | documented | | Esperanto, "PCIe Dev Card (V3)", ET-PCIe-Dev-Card-V3.pdf (github.com/aifoundry-org/et-man), p. [-1-] {+3+} (features) and [-p. 3-] {+pp. 7-10+} (DIP [-switches)-] {+Switches)+}

## fact/chip-minions
Kernels run on 1,024 minions (32 compute shires x 32) … 600 MHz. Limits of observability | measured | aifoundry2 | [-docs/findings/05-claims.md:30-] {+docs/findings/05-claims.md:38+}

## fact/chip.advertised-range
Advertised operating range: 300-800 MHz and about 40 W for … low power? | documented | | external/et-man/ET Introduction.pdf, pdf p.2; [-docs/findings/01-resources.md:101-103-] {+docs/findings/01-resources.md:121-122+} (R6)

## fact/chip.die-area
Die area 570 mm². Heat per millimetre | documented | | [-docs/findings/05-claims.md:513; docs/findings/01-resources.md:234-] {+docs/findings/05-claims.md:832; docs/findings/01-resources.md:266+} (R14: Hot Chips 33 slide 20; IEEE Micro 42(3) p.37)

## fact/chip.die-revision
The datasheet's package marking example gives die revision A0; the … Preliminary Datasheet Rev 1.0.pdf, pdf p.34 (Table 10-1); docs/reports/data/2026-09-22-cards/driver_config.json `arch_rev`; [-docs/et-soc1-notes.md:342-] {+docs/et-soc1-notes.md:364+}

## fact/chip.harts
Software sees 2,048 harts on the 32 compute shires: hartid … 6, neighbourhood = (hartid mod 64) >> 4, minion = {+(hartid mod 64) >> 1 (the firmware's get_minion_id(),+} hartid >> 1, {+numbers the minions chip-wide),+} thread = hartid & 1). On-chip communication | documented | | docs/et-soc1-notes.md:22; external/et-platform/et-common-libs/include/etsoc/isa/hart.h:50,62,74,86

## fact/chip.hop-pitch
Shire tile pitch 3.73 mm east-west and 3.70 mm north-south, … over three readings). Heat per millimetre | inference | | [-docs/findings/05-claims.md:340;-] {+docs/findings/05-claims.md:361;+} docs/reports/data/2026-09-24-wire-energy/report.json `inputs.hop_mm`

## fact/chip.process
TSMC 7 nm, over 24 billion transistors, 89 mask layers … 2022). Why is it low power? | documented | | [-docs/findings/05-claims.md:513; docs/findings/01-resources.md:91-104-] {+docs/findings/05-claims.md:832; docs/findings/01-resources.md:110-123+} (R6)

## fact/clock.minion-opps
Operating points the firmware uses: 600 MHz at 517 mV, … (aifoundry3 is pinned at 600 MHz, not measured here) | [-docs/findings/05-claims.md:28-29, 171-] {+docs/findings/05-claims.md:36-37, 182+} (docs/reports/data/2026-09-21-horace-aifoundry2/cold1/telemetry.jsonl.gz `mhz.minion`, `die_mv.minion`)

## fact/die.handedness
The die view follows the firmware's NoC-spec drawing and the … east end of the top row. The published die plot [-draws-] {+(IEEE Micro 2022 Fig. 7, MPR Dec 2020 Fig. 1) also puts the PCIe and I/O cells at the east end of the top row, in the other order,+} I/O then [-PCIe, its-] {+PCIe (fact L24), and labels no memory shire: it is not the+} mirror [-image;-] {+image. Its own orientation is not stated, and+} no document in the open drop says which handedness the … docs/reports/data/2026-09-27-chip-diagram/research/firmware_map.json; fact L24 (PRM Fig. 1-3 against the die plot)

## fact/dope.donor-acceptor
Dopants work by valence: phosphorus or arsenic (5 outer electrons) … about 50 meV, about twice kT at room temperature, so [-dopants-] {+dopant atoms alone in silicon sites+} are almost all ionised. chu.berkeley.edu | textbook | | C. Hu, Modern Semiconductor Devices for Integrated Circuits (Pearson 2010), ch. 1 (author's free chapter)

## fact/dram.capacity
32 GB of LPDDR4X on [-these V3 cards (Micron part):-] {+aifoundry2 and aifoundry3,+} 2 GB per [-channel;-] {+channel, and 16 GB on aifoundry1 card 1, 1 GB per channel, as the firmware reads the DRAM's density at boot and the runtime reports it. The vendor's document names its 32 GB V3 card a Micron part; which maker's parts the lab cards carry is not recorded. The datasheet gives+} the chip [-supports-] {+4 GB (2 Gb per channel) at full bandwidth up to 32 GB (16 Gb per channel); the PRM gives products+} 8 to 32 [-GB.-] {+GB, the range mprot's dram_size field addresses.+} Memory hierarchy | [-documented-] {+measured+} | {+three cards+} | {+docs/reports/data/2026-09-27-pcie/raw/<card>/r1/info.err ('DRAM size (B)'); external/et-platform/device-bootloaders/src/ServiceProcessorBL2/driver/mem_controller.c:389-420 (the MR8 density sets ddr_mem_size); external/et-platform/device-minion-runtime/src/MasterMinion/src/config/mm_config.c:74-92 (the host's share of it);+} external/et-man/ET-PCIe-Dev-Card-V3.pdf, pdf [-p.1;-] {+p.1 ('32GB (Micron part) v3 card Bringup Planning');+} docs/research/counters-and-dram.md:289; external/et-man/ET Programmer's Reference Manual.pdf, pdf p.342 and p.552; external/et-man/ET Preliminary Datasheet Rev 1.0.pdf, pdf p.30

## fact/dram.leg
Past the L3, the DRAM leg costs 91 + 12 × hops(home shire, memory shire) cycles; about [-25-] {+28+} of the 91 are the DRAM chip (activate 11, read {+latency+} and [-burst 14)-] {+two bursts 17)+} and {+at most+} about [-66-] {+63 the L3 home's miss handling and+} the memory shire. Only [-25-28-] {+about 28+} of a ~300-cycle DRAM load are the DRAM's own timing. Anatomy of a memory access | measured | three cards | [-docs/et-soc1-notes.md:166;-] {+docs/et-soc1-notes.md:179;+} docs/reports/data/2026-09-19-memprobe-aifoundry2/summary.json `decomp.ms_const`; cards.json `ms_const` (90-91 on three cards); [-docs/findings/05-claims.md:404-] {+docs/findings/05-claims.md:435+}

## fact/dram.memshire-select
The memory shire serving a line is PA[8:6] (so it … [8:6]'); confirmed by the memory shires' read counters (syscall 10), [-docs/et-soc1-notes.md:166-] {+docs/et-soc1-notes.md:179+}

## fact/dram.placeholder
The 128,000 MB/s DRAM bandwidth the runtime reports is a … a measurement. Memory hierarchy | documented | | external/et-platform/device-bootloaders/src/ServiceProcessorBL2/include/mem_controller.h:37 (DDR_BANDWIDTH); [-docs/findings/05-claims.md:499;-] {+docs/findings/05-claims.md:818-819;+} driver_config.json `ddr_mb_s`

## fact/dram.rate-card
The firmware hard-codes the 933 MHz DDR configuration on every … Anatomy of a memory access | measured | aifoundry2 | [-external/et-platform/device-bootloaders/src/ServiceProcessorBL2/driver/mem_controller.c:41-42,-] {+external/et-platform/device-bootloaders/src/ServiceProcessorBL2/driver/mem_controller.c:643-649 (configure_memshire: .frequency = DDR_FREQUENCY_933MHZ, '//TODO: decide ddr_mode'); 41-42,+} 114-116, [-225-228;-] {+225-228 (the 933 MHz PLL mode and controller config);+} docs/research/counters-and-dram.md:291-292; docs/reports/data/2026-09-20-power-aifoundry2/horace-telemetry.jsonl (and horace2-, thermal-telemetry.jsonl: 3,681 samples, 20 Sep), field `mhz.ddr`

## fact/dram.rate-datasheet
Datasheet rate: 4,266 MT/s, printed as 133 GB/s; 16 × … | external/et-man/ET Preliminary Datasheet Rev 1.0.pdf, pdf p.4 (§1); docs/et-soc1-notes.md:20; [-docs/findings/05-claims.md:514-] {+docs/findings/05-claims.md:833+}

## fact/dram.row-bits
Inside a channel: bank PA[12:10], column PA[17:13] (plus PA[5:1] within … Anatomy of a memory access | measured | aifoundry2 | [-docs/et-soc1-notes.md:167;-] {+docs/et-soc1-notes.md:180;+} docs/research/counters-and-dram.md:289, 362-370

## fact/dram.unmetered
About 70% of a DRAM byte's energy lands on no … of a memory access | measured | three cards | [-docs/findings/05-claims.md:308;-] {+docs/findings/05-claims.md:323;+} anatomy page headline tiles

## fact/e-awake
An awake minion (addi loop) costs about 2 mW (1.87 … cards. The energy manual | measured | three cards | [-docs/energy-manual/02-awake.md:9-] {+docs/energy-manual/02-awake.md:9-10+}

## fact/e-fexp-ps
Transcendental fexp.ps (8 lanes): 155.4 pJ [147.3-162.4] on random data at a quarter the issue rate; flog.ps 218 pJ. No hardware {+float or vector+} divide or square root: they [-trap.-] {+trap (the scalar integer div and rem run, at 141-157 pJ).+} The energy manual | measured | three cards | [-docs/energy-manual/03-instructions.md:22-] {+docs/energy-manual/03-instructions.md:22; docs/energy-manual/03-instructions.md:25, 33 (every float and vector divide and square root traps; 141-157 pJ for the 64-bit divides and remainders)+}

## fact/e-l1-fill
Filling one 64 B line from the scratchpad into the … line). The energy manual | model | three cards | [-docs/energy-manual/04a-fine-grain.md:42-] {+docs/energy-manual/04a-fine-grain.md:44+}

## fact/el.kt
Thermal energy kT is 25.9 meV at room temperature (30.4 … electrons; the dopants' 50 meV is only 2 kT, so [-they are all-] {+nearly every dopant atom alone in a silicon site is+} ionised. physics.nist.gov | model | | NIST k and e (CODATA 2022)

## fact/et.cdyn-measured
Measured switched capacitance per minion: 0.168 nF on random fp32 … on zeros), against the 0.04 nF target. | measured | [-card not recorded-] {+aifoundry2+} | repository: docs/research/why-low-power.md "What this card measures"

## fact/et.cdyn-target
Esperanto's target: 10 mW per minion at 1 GHz and 0.425 V, [-i.e.-] {+with+} 0.04 nF switched per cycle (vs 2.2 nF for a 3 GHz x86 [-core).-] {+core); 0.04 nF at 0.425 V and 1 GHz is 7.2 mW, the slide's formula adding leakage for the rest.+} hc33.hotchips.org | documented | | D. Ditzel et al. (Esperanto), … Esperanto's ET-SoC-1 Chip", Hot Chips 33 slides, 24 Aug 2021

## fact/et.leakage
Leakage on aifoundry2 at 80 °C: 20-29 W, 55-80% of … per °C (fit: 23.3 W x exp((T-80)/36)). | measured | [-card not recorded-] {+aifoundry2+} | repository: docs/findings/16-dvfs-and-leakage.md (Kanter table row "Leakage is typically 5-30%"); docs/research/why-low-power.md "What this card measures"

## fact/et.per-shire-v
Per-shire minion-rail voltage at idle: 513-522 mV across the 34 minion shires. | measured | [-card not recorded-] {+aifoundry2+} | repository: chip facts L123 [-(docs/findings/05-claims.md:41)-] {+(docs/findings/05-claims.md:49)+}

## fact/et.tr-per-minion
At most about [-15-] {+15.6+} million transistors per minion: what is left after the shire … | inference | | arithmetic on et.transistors and chip.sram-total (repository)

## fact/et.v-minion
Minion rail: 0.517 V at 600 MHz on die (0.568 V at 700, 0.618 V at 800); firmware limits 0.40-0.62 V. | measured | [-card not recorded-] {+aifoundry2+} | repository: [-docs/findings/16-dvfs-and-leakage.md:20; docs/findings/05-claims.md:26-27, 41-] {+docs/findings/16-dvfs-and-leakage.md:39; docs/findings/05-claims.md:34-35, 49; docs/research/power-telemetry.md:189 (the firmware limits)+}

## fact/et.v-noc
Mesh rail: 0.485 V set point, 0.483-0.486 V on die. | measured | [-card not recorded-] {+aifoundry2+} | repository: chip facts mesh.voltage, L101

## fact/et.v-other
Other rails on die: DDR (memory shires) 0.76-0.77 V, Maxion … (the card's VDDQLP, the LPDDR4X's I/O VDDQ). | measured | [-card not recorded-] {+aifoundry2+} | repository: chip facts volt.other; memory levels dram.pwr.rails (the rails' names)

## fact/et.v-sram
SRAM rail (shire-cache arrays): 0.703-0.707 V on die; firmware limits 0.66-0.85 V. | measured | [-card not recorded-] {+aifoundry2+} | repository: chip facts volt.sram; memory-levels l2:l2.voltage.idle, l2:l2.voltage.limits

## fact/gate.metals
Gate metals: since the first high-k gates (45 nm), the … gate and filled with W or Al; their work functions [-(about-] {+set the threshold: about+} 4.1 and 4.85 [-eV) set-] {+eV in+} the [-threshold.-] {+planar 45 nm gates, while a FinFET, its channel undoped, needs about 4.4 and 4.85 eV.+} doi.org | textbook | | C. Zhao and J. Xiang, "Atomic Layer Deposition (ALD) of Metal Gates for CMOS", Applied Sciences 9 (2019) 2388

## fact/gs-add
Scatter-add alternatives, updates/s and nJ per update: gather + add … amoaddg.w on a chip table 2.79 G/s at 1.12 nJ. {+Memory hierarchy+} | measured | three cards | docs/reports/data/2026-09-25-claims-v3/results/gs.json: items["GS-ADD"].rows[] (updates_per_s, nj_per_update, pooled over 9 passes)

## fact/gs-card
Card to card, gathers and scatters: elements/s identical (median ratio 1.000); pJ per element aifoundry3/aifoundry2 0.965, aifoundry1-c1/aifoundry2 1.085 (median over 100 configurations). {+Memory hierarchy+} | measured | three cards | docs/reports/data/2026-09-25-claims-v3/results/gs.json: items["GS-CARD"].ratios

## fact/gs-dram
Random gathers from DRAM (256 KB per hart) move whole … stream, on every card (PASS): 1.19 G useful 4-byte elements/s. {+Memory hierarchy+} | measured | three cards | docs/reports/data/2026-09-25-claims-v3/results/gs.json: items["GS-DRAM"].per_card.<card>.line_bytes_per_s

## fact/gs-g-dram-256K
Gather (fgw.ps, 32-bit elements) from DRAM (256 KB table per … a3 9,320, a1c1 10,298); 8,232 cycles per instruction per hart. {+Memory hierarchy+} | measured | three cards | docs/reports/data/2026-09-25-claims-v3/results/gs.json: items["GS-RATE"].pooled["gs/E/fgw.ps/dram-256K/rand/random/h2/mff/n1024"] (elements_per_s, pj_per_element over 9 passes); .per_card.<card>["gs/E/fgw.ps/dram-256K/rand/random/h2/mff/n1024"].cpi_med

## fact/gs-g-dram-4K
Gather (fgw.ps, 32-bit elements) from L2 (4 KB table per … a3 333.1, a1c1 387.1); 359.3 cycles per instruction per hart. {+Memory hierarchy+} | measured | three cards | docs/reports/data/2026-09-25-claims-v3/results/gs.json: items["GS-RATE"].pooled["gs/E/fgw.ps/dram-4K/rand/random/h2/mff/n1024"] (elements_per_s, pj_per_element over 9 passes); .per_card.<card>["gs/E/fgw.ps/dram-4K/rand/random/h2/mff/n1024"].cpi_med

## fact/gs-g-dram-512B
Gather (fgw.ps, 32-bit elements) from L1 (512 B table per … a3 12.46, a1c1 12.28); 21.78 cycles per instruction per hart. {+Memory hierarchy+} | measured | three cards | docs/reports/data/2026-09-25-claims-v3/results/gs.json: items["GS-RATE"].pooled["gs/E/fgw.ps/dram-512B/rand/random/h2/mff/n1024"] (elements_per_s, pj_per_element over 9 passes); .per_card.<card>["gs/E/fgw.ps/dram-512B/rand/random/h2/mff/n1024"].cpi_med

## fact/gs-g-rscp-16K
Gather (fgw.ps, 32-bit elements) from scratchpad 2 hops away (16 … a3 847.2, a1c1 973.4); 969.0 cycles per instruction per hart. {+Memory hierarchy+} | measured | three cards | docs/reports/data/2026-09-25-claims-v3/results/gs.json: items["GS-RATE"].pooled["gs/E/fgw.ps/rscp-16K/rand/random/h2/mff/n1024"] (elements_per_s, pj_per_element over 9 passes); .per_card.<card>["gs/E/fgw.ps/rscp-16K/rand/random/h2/mff/n1024"].cpi_med

## fact/gs-g-scp-16K
Gather (fgw.ps, 32-bit elements) from own scratchpad (16 KB per … a3 344.6, a1c1 399.3); 359.3 cycles per instruction per hart. {+Memory hierarchy+} | measured | three cards | docs/reports/data/2026-09-25-claims-v3/results/gs.json: items["GS-RATE"].pooled["gs/E/fgw.ps/scp-16K/rand/random/h2/mff/n1024"] (elements_per_s, pj_per_element over 9 passes); .per_card.<card>["gs/E/fgw.ps/scp-16K/rand/random/h2/mff/n1024"].cpi_med

## fact/gs-l1
A 32-bit gather of 8 lanes from L1 (fgw.ps, random, … per instruction per minion on every card (registered 7-12: PASS). {+Memory hierarchy+} | measured | three cards | docs/reports/data/2026-09-25-claims-v3/results/gs.json: items["GS-L1"].per_card.<card>.cpi_minion

## fact/gs-mh
Gathers from L2 and the own scratchpad saturate at 27.36 … (registered 0.5-2x: PASS); a second hart adds nothing (h2/h1 1.0005). {+Memory hierarchy+} | measured | three cards | docs/reports/data/2026-09-25-claims-v3/results/gs.json: items["GS-MH"].per_card.<card>.l2 / .scp, .bound_elements_per_s, .h2_over_h1_l2

## fact/gs-s-dram-256K
Scatter (fscw.ps, 32-bit elements) into DRAM (256 KB table per … 0.400 G elements/s, about 5% under the measured aggregate rate. {+Memory hierarchy+} | measured | three cards | docs/reports/data/2026-09-25-claims-v3/results/gs.json: items["GS-RATE"].pooled["gs/E/fscw.ps/dram-256K/rand/random/h2/mff/n1024"] (elements_per_s, pj_per_element over 9 passes); .per_card.<card>["gs/E/fscw.ps/dram-256K/rand/random/h2/mff/n1024"].cpi_med; .pooled[same key].cpi_med (mean 24,584)

## fact/gs-s-dram-4K
Scatter (fscw.ps, 32-bit elements) into L2 (4 KB table per … a3 679.1, a1c1 813.5); 417.6 cycles per instruction per hart. {+Memory hierarchy+} | measured | three cards | docs/reports/data/2026-09-25-claims-v3/results/gs.json: items["GS-RATE"].pooled["gs/E/fscw.ps/dram-4K/rand/random/h2/mff/n1024"] (elements_per_s, pj_per_element over 9 passes); .per_card.<card>["gs/E/fscw.ps/dram-4K/rand/random/h2/mff/n1024"].cpi_med

## fact/gs-s-dram-512B
Scatter (fscw.ps, 32-bit elements) into L1 (512 B table per … a3 14.60, a1c1 14.76); 21.78 cycles per instruction per hart. {+Memory hierarchy+} | measured | three cards | docs/reports/data/2026-09-25-claims-v3/results/gs.json: items["GS-RATE"].pooled["gs/E/fscw.ps/dram-512B/rand/random/h2/mff/n1024"] (elements_per_s, pj_per_element over 9 passes); .per_card.<card>["gs/E/fscw.ps/dram-512B/rand/random/h2/mff/n1024"].cpi_med

## fact/gs-s-rscp-16K
Scatter (fscw.ps, 32-bit elements) into scratchpad 2 hops away (16 … a3 1,865, a1c1 2,125); 958.3 cycles per instruction per hart. {+Memory hierarchy+} | measured | three cards | docs/reports/data/2026-09-25-claims-v3/results/gs.json: items["GS-RATE"].pooled["gs/E/fscw.ps/rscp-16K/rand/random/h2/mff/n1024"] (elements_per_s, pj_per_element over 9 passes); .per_card.<card>["gs/E/fscw.ps/rscp-16K/rand/random/h2/mff/n1024"].cpi_med

## fact/gs-s-scp-16K
Scatter (fscw.ps, 32-bit elements) into own scratchpad (16 KB per … a3 643.8, a1c1 757.0); 417.5 cycles per instruction per hart. {+Memory hierarchy+} | measured | three cards | docs/reports/data/2026-09-25-claims-v3/results/gs.json: items["GS-RATE"].pooled["gs/E/fscw.ps/scp-16K/rand/random/h2/mff/n1024"] (elements_per_s, pj_per_element over 9 passes); .per_card.<card>["gs/E/fscw.ps/scp-16K/rand/random/h2/mff/n1024"].cpi_med

## fact/gs-uc
GS-UC failed on all three cards: an L1-bypassing gather (fgwl.ps, … one (registered prediction 1.6-2.4x): the second hart adds about 3%. {+Memory hierarchy+} | measured | three cards | docs/reports/data/2026-09-25-claims-v3/results/gs.json: items["GS-UC"].per_card.<card>.h2_over_h1 (1.0299-1.0303), outcome FAIL

## fact/heat.race
From a launch at 80.9-81.7 °C to the [-firmware's-] 90 °C [-cap-] {+at which the run script stopped each run (run_horace_long.sh, not a firmware limit)+} on aifoundry2, the same matmul on all 1,024 minions: random … .reason (cap: reached 90 °C; time: the run ended first), [-.t_before-] {+.t_before; tools/ettelem/run_horace_long.sh:8-9, 18, 69 (cap=${5:-90}: at the cap the script touches the host's stop file)+}

## fact/host.intel14
Intel's 14 nm process, the host processors', is a FinFET process too: {+as first made (2014),+} fins 42 nm apart, gates 70 nm apart and the finest wires 52 nm apart (TSMC N7: 30, 57 and 40 [-nm).-] {+nm); its 14nm++ revision (2017), used for Intel's 14 nm desktop processors from Coffee Lake on, spaces the gates 84 nm apart.+} | outside source | | S. Natarajan et al., "A … µm² SRAM cell size", IEDM 2014; out.host.5 (the hosts' 14 [-nm)-] {+nm); Intel, Technology and Manufacturing Day (March 2017): 14nm++ relaxes the gate pitch from 70 to 84 nm (as reported by The Motley Fool, "Intel Corporation Outs 14-Nanometer++ Technology", 2017, and AnandTech's Coffee Lake review, Oct 2017)+}

## fact/hot-cost
One contended global atomic (amoaddg.w on one line, 1,024 minions): … hot line stops a shire | measured | aifoundry2 | [-docs/findings/05-claims.md:221; docs/findings/05-claims.md:222-] {+docs/findings/05-claims.md:233; docs/findings/05-claims.md:234+}

## fact/hot-edge
The switch is sharp: 21 remote requesters leave the host … line stops a shire | measured | three cards | [-docs/findings/05-claims.md:415;-] {+docs/findings/05-claims.md:450;+} docs/reports/2026-09-22-hot-line.html section 3

## fact/hot-energy
Energy per atomic: 19.8 nJ [16.9-23.6] contended against 1.16 nJ … | measured | aifoundry2, aifoundry3 | manual.json: reruns.hotline_nj_per_op.contended / .spread; [-docs/findings/05-claims.md:322-] {+docs/findings/05-claims.md:341+}

## fact/in.core.irf.1
intpipe_rf instantiates rf_latch_2r_1w with WIDTH = 64 (XREG_SIZE) and ENTRIES = 2 threads x 32: a latch register file, 2 read [-ports-] {+ports, a dedicated read port for x31+} and 1 write port. | documented | | [-external/core-et/rtl/shire/minion/intpipe/intpipe_rf.v:43-50-] {+external/core-et/rtl/shire/minion/intpipe/intpipe_rf.v:43-61 (rd_par, the x31 port); external/core-et/docs/FE-Intpipe-Description.pdf, pdf p.13 (§3.2.1: "three for reading and one for writing")+}

## fact/in.core.irf.2
[-64-] {+62+} x 64 = [-4,096-] {+3,968+} storage latches per [-minion;-] {+minion (x0 of each thread is wired to 0);+} at about 10 transistors each, some [-41,000-] {+40,000+} transistors before the read multiplexers. | inference | | arithmetic on intpipe_rf.v {+(ZERO wires entries 0 and 32 to zero, with no latch: external/core-et/rtl/libs/rf_latches/rf_latch_2r_1w.v:158-159)+} and the latch count of l1:g.latch-cell; the 10 transistors per latch are assumed, so the total is inferred

## fact/in.io.pvt.1
36 process detectors and 36 temperature sensors (one each per minion {+shire, the PCIe+} shire and the I/O [-shire)-] {+shire, as the manual's Figure 1-3 draws them)+} and 8 voltage-monitor blocks of up to 16 sense points (128 in all), read through five PVT controllers. (The [-manual's own count does not add up: 34 minion shires-] {+RTL removed the PCIe shire's pair, "Pshire no longer has ts/pd (RTLMIN-3619)", core-et rtl/inc/pvt_defines.vh:16-26,+} and the [-I/O shire make 35, and it does not say where the 36th sensor sits.)-] {+firmware reads 35: fact L121.)+} | documented | | external/et-man/ET Programmer's Reference Manual.pdf, pdf p.17-18 (§1.6, {+Figure 1-3,+} Table 1-6: "36 sensors. 1 PD in each [-minion/IO-Shire")-] {+minion/IO-Shire"); external/core-et/rtl/inc/pvt_defines.vh:16-26+}

## fact/in.lib.adder.1
Parallel-prefix adders [-(Kogge-Stone, Sklansky, Brent-Kung)-] compute [-carries-] {+every carry in a tree of generate/propagate cells: Kogge-Stone and Sklansky+} in log2(N) {+levels, Brent-Kung in 2 log2(N) - 1+} levels [-of generate/propagate cells.-] {+with fewer cells and wires.+} | textbook | | N. Weste and D. Harris, CMOS VLSI Design, 4th ed. (Addison-Wesley 2011), ch. 11 (addition)

## fact/in.lib.booth.1
txfma_booth_ppg_32r4_norm decodes each 3-bit group into one of five selections (0, +1, +2, -2, -1). | documented | | [-external/core-et/rtl/shire/minion/vpu/txfma_7s/txfma_booth_ppg_32r4_norm.v:13-25-] {+external/core-et/rtl/shire/minion/vpu/txfma_7s/txfma_booth_ppg_32r4_norm.v:13-32+}

## fact/in.lib.fin.2
TSMC 10 nm (Apple A11): fin width ~6 nm, functional … and 10-nm", AVS Joint Users Group, July 2018 (JTG718-4), slides [-11-] {+12, 15, 16+} and [-17-18:-] {+18: Intel 10 nm fin height 46-53 nm, width ~7 nm at half height (12), minimum Lg 18 nm (15);+} TSMC 10 {+nm, Apple A10X, minimum Lg ~25+} nm [-(Apple A11)-] {+(16); TSMC 10 nm, Apple A11,+} fin pitch ~33 nm, fin width ~6 nm, functional gate height ~44 nm, gate width ~95 [-nm; Intel 10-] nm [-fin height 46-53 nm, width ~7 nm at half height, Lg 18 nm;-] {+(18);+} https://nccavs-usergroups.avs.org/wp-content/uploads/JTG2018/JTG718-4-James-Siliconics.pdf

## fact/in.lib.finfet.3
N7 high-density cells are 240 nm tall; high-performance cells 300 nm. | [-inference-] {+outside source+} | | WikiChip Fuse, {+D. Schor,+} "TSMC 7nm HD and HP Cells, 2nd Gen 7nm, And The Snapdragon 855 DTCO", [-https://fuse.wikichip.org/?p=2408 (HD cell-] {+16 Jun 2019, https://fuse.wikichip.org/?p=2408, read via the Internet Archive capture of 13 Nov 2019 ("Those cells are+} 240 nm {+and 300 nm+} tall [-=-] {+respectively"; HD+} 6 tracks of 40 nm, HP [-300 nm;-] {+7.5;+} about 91.2 MTr/mm2 HD, 65 [-HP); values as the search summary reported them, the page itself refused the connection on 30 Sep 2026-] {+HP)+}

## fact/in.lib.gate.2
Comparable generations: TSMC 10 nm minimum Lg about 25 nm; … and 10-nm", AVS Joint Users Group, July 2018 (JTG718-4), slides [-11-] {+12, 15, 16+} and [-17-18:-] {+18: Intel 10 nm fin height 46-53 nm, width ~7 nm at half height (12), minimum Lg 18 nm (15);+} TSMC 10 {+nm, Apple A10X, minimum Lg ~25+} nm [-(Apple A11)-] {+(16); TSMC 10 nm, Apple A11,+} fin pitch ~33 nm, fin width ~6 nm, functional gate height ~44 nm, gate width ~95 [-nm; Intel 10-] nm [-fin height 46-53 nm, width ~7 nm at half height, Lg 18 nm;-] {+(18);+} https://nccavs-usergroups.avs.org/wp-content/uploads/JTG2018/JTG718-4-James-Siliconics.pdf

## fact/in.lib.inverter.2
TSMC N7 high-density cells are 240 nm tall (6 tracks of 40 nm); high-performance cells 300 nm. | [-inference-] {+outside source+} | | WikiChip Fuse, {+D. Schor,+} "TSMC 7nm HD and HP Cells, 2nd Gen 7nm, And The Snapdragon 855 DTCO", [-https://fuse.wikichip.org/?p=2408 (HD cell-] {+16 Jun 2019, https://fuse.wikichip.org/?p=2408, read via the Internet Archive capture of 13 Nov 2019 ("Those cells are+} 240 nm {+and 300 nm+} tall [-=-] {+respectively"; HD+} 6 tracks of 40 nm, HP [-300 nm;-] {+7.5;+} about 91.2 MTr/mm2 HD, 65 [-HP); values as the search summary reported them, the page itself refused the connection on 30 Sep 2026-] {+HP)+}

## fact/in.lib.si.3
Across a 6 nm fin whose sidewalls are (110) planes … atoms. | inference | | arithmetic on the lattice parameter, [-the inferred-] {+N7's+} 6 nm fin {+(n7.fin-width, WikiChip Fuse)+} and the assumed (110) sidewalls: inferred

## fact/in.mesh.link.4
Measured on the mesh rail, routers included: [-0.50-0.84-] {+about 0.42-0.53+} pF of switched capacitance per mm of [-travel,-] {+travel (25-31 fJ of data-dependent energy per random bit and mm, free links to a loaded mesh, as C = 4E/V² at 0.485 V),+} against 0.2-0.4 pF/mm estimated for a plain 7 nm repeated … efficiency comes from its 0.485 V. | model | | [-docs/reports/data/2026-09-24-wire-energy/research/SYNTHESIS.md lines 38, 170, 255-] {+docs/reports/data/2026-09-24-wire-energy/report.json headline["uncontended/noc_rail"] and ["loaded/noc_rail"] .random_bit_data; docs/reports/data/2026-09-24-wire-energy/research/lit/dally_gap.py (C = 4E/V²: 420 and 530 fF/mm); docs/findings/05-claims.md:381, 384 (the 23 Sep figures of research/SYNTHESIS.md §2c, 0.50-0.57 pF/mm on the mesh rail and 0.67-0.84 on board power, are superseded)+}

## fact/in.shire.clock.3
Programmable clock delay [-lines:-] {+lines on the four neighbourhood clocks and the two DLL feedback clocks (the shire clock itself cannot be delayed), set by one ESR (clk_dly_ctl): 100 ps coarse steps up to 1,500 ps plus+} 25 ps {+fine+} steps {+up to 75 ps+} (first specified [-at-] {+as+} 100 [-ps),-] {+ps steps+} up to 1 [-ns, set by ESR, one per DLL feedback path.-] {+ns; the cells built have 115 ps and 30 ps taps).+} | documented | | external/core-et/docs/Minion Shire DLL Delay Control.pdf, pdf p.4 [-(§2)-] {+(§2), p.6 (§3.1), p.8-9 (§3.2.1)+}

## fact/in.shire.neigh.xing.2
(new)
```
The neighbourhood clock is the shire clock shifted by 180 degrees, made by the DLL from the same source, so the two domains meet at a semi-synchronous interface: ET-Link requests and responses cross in semi-synchronous FIFOs, which take advantage of the two clocks being one clock shifted by a constant 180 degrees. | documented |  | external/core-et/docs/CORE-ET-Neigborhood-MAS.pdf, pdf p.39-40 (§6.1, §6.1.1 and its table of crossings)
```

## fact/in.shire.neigh.xing.3
(new)
```
Four bank FIFOs and a UC FIFO, three entries each, end the request datapath; a 512-bit request takes two consecutive entries, and its halves are re-joined into one 512-bit ET-Link request at the FIFO's output, in the HV region. | documented |  | external/core-et/docs/CORE-ET-Neigborhood-MAS.pdf, pdf p.18-19 (§4.3.4-4.3.5)
```

## fact/in.shire.neigh.xing.4
(new)
```
The cell library's semi-synchronous VC FIFO, written on the low-voltage side and read on the high-voltage side (vcfifo_wr_lov_ss), works only at a 1:1 clock ratio with the two clocks offset by a DLL, for "guaranteed signal hand-off between edges without any meta-stability"; its minimum latency is 1.5 cycles. | documented |  | external/core-et/rtl/libs/mems_and_fifos/vcfifo_wr_lov_ss.v:7-19
```

## fact/in.tensor.tenb.2
[-Modules-] {+TenB is+} vpu_tensorb_rf, [-vpu_tensora_rf, vpu_tensortmp_rf.-] {+instantiated in each of a lane's two vpu_lane_tima units (4 entries of 32 bits each: 256 B per minion); vpu_tensora_rf (TenA, the A buffer) and vpu_tensortmp_rf sit in vpu_ctrl.+} | documented | | [-external/core-et/rtl/shire/minion/vpu/-] {+external/core-et/rtl/shire/minion/vpu/vpu_lane_tima.v:42, vpu_lane.v:408-421, vpu_ctrl.v:1806, 1832, vpu_tensorb_rf.v:27-29; external/core-et/rtl/inc/minion_defines.vh:191, 349; external/core-et/rtl/inc/vpu_defines.vh:210+}

## fact/in.vpu.lane.fma.6
[-A-] {+In the flip model (the TXFMA RTL replayed on the operands aifoundry2 ran), a+} random-data 16x16x16 tile clocks 2.5 million register bits and toggles … clock is withheld when an operand word is zero. | [-measured-] {+model+} | [-card not recorded-] | [-docs/energy-manual/03-instructions.md:53-65 (flip model fitted on aifoundry2)-] {+docs/energy-manual/03-instructions.md:55, 65; docs/findings/10-data-dependent-power.md:73 (E11); docs/findings/11-thermal-model.md:17 (counted in RTL)+}

## fact/l2.latency
L2 hit (and own-shire scratchpad hit): 47 cycles load-to-use, 78 … 39 cycles. Memory hierarchy | measured | three cards | [-docs/findings/05-claims.md:366, 409-] {+docs/findings/05-claims.md:394, 443+} (docs/reports/data/2026-09-25-claims-v3/results/lat.json LAT-M1)

## fact/l2.read-buffer
Each L2 bank has an 8-line read buffer (2 KB … without touching the SRAM. Memory hierarchy | documented | | [-docs/et-soc1-notes.md:72;-] {+docs/et-soc1-notes.md:73;+} external/core-et/docs/CORE-ET-Shire-Cache-Specification.pdf, pdf p.9

## fact/l3.home
A line's L3 home shire is PA[10:6]: consecutive 64-byte lines … but 2 within ±4 cycles of 110 + 12·hops(requester, PA[10:6]) [-(docs/et-soc1-notes.md:165)-] {+(docs/et-soc1-notes.md:178)+}

## fact/l3.latency
L3 hit: 110 + 12 cycles per mesh hop between … of a memory access | measured | three cards | [-docs/findings/05-claims.md:367, 403, 410-] {+docs/findings/05-claims.md:395, 434, 444+} (docs/reports/data/2026-09-25-claims-v3/results/mem.json MEM-P1; lat.json LAT-M2)

## fact/lat-dram
DRAM load from a pointer chase: 287-297 cycles at 600 … Memory hierarchy | measured | three cards | lat.json: items[LAT-M2].per_card.<card>.passes[].DRAM; [-docs/findings/05-claims.md:410-] {+docs/findings/05-claims.md:444+}

## fact/lat-dram-chip
Of a DRAM load's ~300 cycles only about [-25-28-] {+28+} are the DRAM chip's own timing (activate tRCD 18 ns, 19.3 ns read latency, [-one or-] {+the+} two 4.3 ns [-bursts);-] {+bursts of a 64-byte line);+} the rest is paths on the chip. Anatomy of a … cycles (152 ns), the DRAM chip itself accounts for about [-25-28")-] {+28")+}

## fact/lat-dram-refresh
LPDDR4X refresh every 2,325 cycles (3.88 us) on every card; … access | measured | three cards | mem.json: [item=MEM-P5].per_card.<card>.tests.P5_refresh_period, .P5_max_extra; [-docs/findings/05-claims.md:407-] {+docs/findings/05-claims.md:438+}

## fact/lat-dram-rowconflict
Two loads to the same bank but different rows, issued … memory access | measured | three cards | mem.json: [item=MEM-P4].per_card.<card>.tests.P4_row_conflict_extra; [-docs/findings/05-claims.md:406-] {+docs/findings/05-claims.md:437+}

## fact/lat-l1
L1 data cache hit: 5.25 cycles load-to-use (8.8 ns at … Memory hierarchy | measured | three cards | docs/reports/data/2026-09-25-claims-v3/results/lat.json: items[LAT-M1].per_card.<card>.passes[].L1; [-docs/findings/05-claims.md:409-] {+docs/findings/05-claims.md:443+}

## fact/lat-l2
L2 cache hit (and the shire's own scratchpad): 47 cycles … | measured | three cards | lat.json: items[LAT-M1].per_card.<card>.passes[].L2 (46.998-47.024), .hart1; [-docs/findings/05-claims.md:409-] {+docs/findings/05-claims.md:443+}

## fact/lat-l3-avg
L3 hit from a pointer chase, averaged over all 32 … Memory hierarchy | measured | three cards | lat.json: items[LAT-M2].per_card.<card>.passes[].L3; [-docs/findings/05-claims.md:410-] {+docs/findings/05-claims.md:444+}

## fact/lat-l3-hop
L3 hit against distance to the line's home shire: 110.5 … | measured | three cards | docs/reports/data/2026-09-25-claims-v3/results/mem.json: [item=MEM-P1].per_card.<card>.tests.P1_l3_slope / P1_l3_intercept; [-docs/findings/05-claims.md:403-] {+docs/findings/05-claims.md:434+}

## fact/lat-rb
L2 read buffer (8 clean lines per bank x 4 … hierarchy | measured | three cards | lat.json: items[LAT-M1].per_card.<card>.passes[].RB (35.998-36.006); [-docs/findings/05-claims.md:409-] {+docs/findings/05-claims.md:443+}

## fact/lat-scp-own
The shire's own L2 scratchpad: 47 cycles (78 ns), the … L2 cache. Memory hierarchy | measured | three cards | [-docs/findings/05-claims.md:366-] {+docs/findings/05-claims.md:394+}

## fact/lat-scp-remote
Another shire's scratchpad: 99.84 + 12.00 cycles per mesh hop … | three cards | lat.json: items[LAT-M3].per_card.<card>.passes[] (row0_slope 11.998-12.002, frac_within_1 1.0); [-docs/findings/05-claims.md:411-] {+docs/findings/05-claims.md:445+}

## fact/mem.global-atomic
A global atomic (amoaddg) is performed at the shire cache … line stops a shire | measured | aifoundry2, aifoundry3 | [-docs/findings/05-claims.md:221, 223;-] {+docs/findings/05-claims.md:233, 235;+} docs/findings/17-hot-line.md:10-16

## fact/mesh-bit-mm-free
A random bit per mm on free links, mesh rail … cards | report.json: headline["uncontended/noc_rail"].random_bit_total / .random_bit_data, headline["uncontended/board"].random_bit_total; per card (V3) [-docs/findings/05-claims.md:444-] {+docs/findings/05-claims.md:482+}

## fact/mesh-hop-lat
Each mesh hop adds 12 cycles round trip at 600 … every card. On-chip communication | measured | three cards | [-docs/findings/05-claims.md:403; docs/findings/05-claims.md:411; docs/findings/05-claims.md:412-] {+docs/findings/05-claims.md:434; docs/findings/05-claims.md:445; docs/findings/05-claims.md:446+}

## fact/mesh-hop-ring
TensorSend across the mesh: 9.2 pJ/B to leave the shire … On-chip communication | model | three cards | docs/reports/data/2026-09-25-claims-v3/results/rl.json: items[RL-a].pooled_mean; [-docs/findings/05-claims.md:450;-] {+docs/findings/05-claims.md:489;+} docs/energy-manual/05-bytes-between-cores.md:31

## fact/mesh.1kb-knee
With 1 KB messages a round trip adds 12 cycles … in flight. On-chip communication | measured | three cards | [-docs/findings/05-claims.md:382, 412-] {+docs/findings/05-claims.md:411, 446+} (docs/reports/data/2026-09-25-claims-v3/results/lat.json LAT-N2 `c32_slope_to5`, `c32_slope_beyond5`)

## fact/mesh.empty-cells
Four cells of the 6 × 6 map hold no … master, spare, PCIe and I/O shires and route traffic too; [-which cell is which is not established.-] {+the firmware's maps name them (fact fw.grey-cells): (0,3) the master, shire 32; (5,3) the spare, 33; (0,4) the PCIe shire; (0,5) the I/O shire.+} On-chip communication | measured | three cards | [-workloads/nocbench/analyze.py:60-] {+workloads/nocbench/analyze.py:64+} (`EMPTY`); on-chip communication page §'Where the shires [-are'-] {+are'; the cells named 27 Sep by fw.grey-cells+}

## fact/mesh.logical-map
Measured position of each compute shire on the 6 × … 7 31. On-chip communication | measured | three cards | [-workloads/nocbench/analyze.py:52-60-] {+workloads/nocbench/analyze.py:56-64+} (`MARTY`, `EMPTY`); [-docs/findings/05-claims.md:383, 412-] {+docs/findings/05-claims.md:412, 446+} (map recovered from latency alone in 12 of 12 search restarts on every card)

## fact/mesh.no-counters
[-There are no-] {+No+} NoC performance counters {+are documented+} in the [-PRM,-] {+PRM or used by+} the [-firmware or core-et; mesh-] {+firmware's code, and core-et has none; the firmware's generated register header does define transaction counters in every NoC bridge: two address- and command-filtered counters in each master bridge (*_m_am_cntr0/1 with ccmd0/1 and caddr, beside registers named latnum0/1 whose use it does not give) and one command-filtered counter in each slave bridge (*_s_as_cntr), undocumented, on the service processor's register bus and not tried here. Mesh+} transit is inferred from latency differences. Limits of observability | documented | | [-docs/research/counters-and-dram.md:272-279-] {+docs/research/counters-and-dram.md:272-279; external/et-platform/etsoc-hal/include/hwinc/noc_esr.h:552, 564, 1710 (bridge counters); docs/reports/sources/limits-of-observability.data.json rung 27 (ask-noc-registers)+}

## fact/mesh.orientation
The logical map [-appears to be-] {+is+} the die [-turned-] {+view transposed (x and y swapped:+} a [-quarter:-] {+quarter turn plus a mirror):+} in map orientation the memory shires sit above and below … columns. Anatomy of a memory access | inference | | [-docs/et-soc1-notes.md:102-105;-] {+docs/et-soc1-notes.md:115-118;+} anatomy page §1 'Trace one load'; settled 27 Sep by fw.map-match except the handedness (die.handedness)

## fact/mesh.port-width
The shire cache's mesh master port is 512 bits wide (one 64-byte line per beat); a shire has four mesh lanes and [-a-] {+an L3+} line goes to {+the+} lane [-PA[7:6], so consecutive lines on one-] {+of its home bank, PA[12:11] (a remote-scratchpad line to+} lane [-are 256 bytes apart;-] {+PA[7:6]); the heat-per-mm analysis treats+} a flit [-carries-] {+as+} at least one 64-byte [-line.-] {+line (the NoC's flit size is not documented).+} Heat per millimetre | documented | | external/core-et/rtl/inc/axi_defines.vh:43 (`SC_MESH_MASTER_AXI_DATA_SIZE 512`); [-docs/findings/01-resources.md:238-239-] {+external/core-et-main/hw/ip/shirecache/rtl/shirecache_mesh_master.sv:132-153 (the lane: req_bank_id = remote scratchpad ? PA[7:6] : the L3 bank from shirecache_pipe_l3_swizzle_get); external/core-et/docs/CORE-ET-Shire-Cache-Specification.pdf, pdf p.27 (Table 8, swizzle0: the L3 bank is PA[12:11]); docs/findings/01-resources.md:270-271+} (R14); [-docs/findings/20-heat-per-mm.md:117-122-] {+docs/findings/20-heat-per-mm.md:219-223+}

## fact/mesh.shortest-paths
Round trips fit a + b × Manhattan distance on … (fact L104). On-chip communication | measured | three cards | [-docs/findings/05-claims.md:381, 412;-] {+docs/findings/05-claims.md:410, 446;+} on-chip communication page §'What the numbers say'; anatomy page §1 … request was not measured'); the order: fact L104 (E56, docs/reports/data/2026-09-29-nocr)

## fact/mesh.voltage
NoC rail: set point 485 mV, 484-485 mV on die … (and horace2-, thermal-telemetry.jsonl: 3,681 samples, 20 Sep), fields `reg_mv.noc`, `die_mv.noc`; [-docs/findings/05-claims.md:41-] {+docs/findings/05-claims.md:49+}

## fact/mesh.xy-assumption
The heat-per-mm analysis assumes dimension-ordered XY routing on the logical … traffic. Heat per millimetre | inference | | workloads/enercat/analyze_wire.py:38, 149-176; [-docs/findings/05-claims.md:348-] {+docs/findings/05-claims.md:369+} (WIRE `checks.link_sharing`); settled 29 Sep by fact L104 (E56)

## fact/minion.combine-free
Combining on receive (fp32/int32 add, max, min) adds 0 cycles to a round trip. On-chip communication | measured | three cards | [-docs/et-soc1-notes.md:114;-] {+docs/et-soc1-notes.md:127;+} on-chip communication page table

## fact/minion.l1-firmware
The firmware puts every minion's L1 in scratchpad mode before … ways × 64 B). Memory hierarchy | documented | | [-docs/et-soc1-notes.md:84-86;-] {+docs/et-soc1-notes.md:90-92;+} docs/research/counters-and-dram.md:446-447 (fw MachineMinion/src/syscall.c:348-420)

## fact/minion.l1d
Each minion has a private 4 KB L1 data cache: … p.1 (slide 2); external/et-man/ET Preliminary Datasheet Rev 1.0.pdf, pdf p.9 [-(§2.1.1.5)-] {+(§2.1.1.5); external/et-man/ET Programmer's Reference Manual.pdf, pdf p.243 (§8: an eviction writes a dirty line back); external/core-et/docs/Minion DCache Description.pdf, pdf p.33 (§3.5: "Evict operations (REQ_Write): always 512b")+}

## fact/minion.no-divide
No hardware {+float or vector+} divide or square root in [-U-mode:-] {+U-mode (the scalar integer div and rem run):+} fdiv.ps and fsqrt.ps trap, as do sine, reciprocal square root, {+conversion between fp32 and+} 64-bit [-float conversion-] {+integers (fcvt.l.s, fcvt.s.l)+} and reading the cycle CSR; 161 of the instructions tried execute in U-mode, 13 trap. The energy manual | measured | aifoundry2, aifoundry3 | [-docs/findings/05-claims.md:278, 296 (workloads/enercat/enercat_modes.json)-] {+docs/findings/05-claims.md:290, 310 (workloads/enercat/enercat_modes.json); docs/energy-manual/03a-every-instruction.md:7 (the 13 that trap), 52-55 (div, divu, rem, remu retire in U-mode); external/et-man/ET Programmer's Reference Manual.pdf, pdf p.36 (§3.5: the float and vector divides and square roots, frsq.ps, fsin.ps and the conversions between fp32 and 64-bit integers trap to M-mode emulation)+}

## fact/minion.one-ready-bit
The hardware keeps one peer-to-peer ready bit per minion, not one per partner: {+if+} a minion [-receiving from-] {+that TensorSends to+} two [-TensorSend-] partners [-at once hangs-] {+gets both their readies before it has used the first, one is lost, and that receiver and+} its [-hart permanently-] {+sender hang for good+} (the card then needs a reset). On-chip communication | documented | | [-docs/et-soc1-notes.md:124-128-] {+docs/et-soc1-notes.md:137-141+} (core-et dcache_reduce.v `partner_ready_peer`); [-docs/findings/05-claims.md:257-] {+docs/findings/05-claims.md:269+}

## fact/minion.sleep-unused
The minion's sleep and isolation ports (nsleepin, iso_enable, nsleepout) are … | documented | | external/core-et/docs/Minion Description.pdf, pdf p.7 (interfaces table); [-docs/findings/05-claims.md:177-179-] {+docs/findings/05-claims.md:189-191+}

## fact/minion.tensor-shape
A TensorFMA computes C[M][N] += A[M][K] · B[K][N] with M, … / (bytes per element): A from the L1 scratchpad, B {+from the L1 scratchpad or+} streamed through [-TenB,-] {+TenB by a paired TensorLoadB,+} C accumulated in hart 0's vector registers (int8 in TenC). … | documented | | external/et-man/ET Programmer's Reference Manual.pdf, pdf p.264 [-(§9); docs/et-soc1-notes.md:292-294-] {+(§9), p.277 (TensorLoadB) and p.291 (TensorFMA32, TENB); docs/et-soc1-notes.md:314-316+}

## fact/minion.tensorfma-546
With A and B both in the L1 scratchpad a … pattern. The Horace experiment | measured | three cards | [-docs/findings/05-claims.md:31-32, 414-] {+docs/findings/05-claims.md:39-40, 449+} (docs/reports/data/2026-09-25-claims-v3/results/lat.json LAT-S1)

## fact/minion.tensorsend
TensorSend moves COUNT consecutive vector registers (32 B each, up … Reference Manual.pdf, pdf p.272 and p.311-314; on-chip communication page (headline); [-docs/findings/05-claims.md:380-381-] {+docs/findings/05-claims.md:409-410+}

## fact/minion.vec-peak
The tensor instructions run on the vector unit's own lanes: … pdf p.11 (§2: TXFMA and two TIMA units per lane); [-scripts/ridge-points.py:46, 51-] {+scripts/ridge-points.py:49, 54+} (fp32 TensorFMA and vec32 fmadd.ps, per_cycle 16 each)

## fact/minion.vector-rate
A simple vector-FMA loop reaches only about 1.5 lane-FMAs per … tensor unit's 9.5. Sparse compute | measured | aifoundry3 | [-docs/et-soc1-notes.md:152-153, 274;-] {+docs/et-soc1-notes.md:165-166, 296;+} ridge-points page §'The compute ceilings'

## fact/ml:dram:dram.ctl.ports
Each controller has two AXI ports with aging on: port … | external/et-platform/etsoc-hal/src/memshire_ddr_init_functions.c:4670-4680 (PCFGR_0 0x100f, PCFGR_1 0x1008, PCFGW_0 0x100f, PCFGW_1 0x1008); [-external/core-et/rtl/inc/memshire_defines.vh:95-] {+external/core-et/rtl/inc/memshire_defines.vh:94-95+} (`MEMSHIRE_WRITE_CNT_SIZE`, 'one per priority'); external/core-et/rtl/inc/memshire_types.vh (ddrc_esr_ctl_t: u0/u1 csysreq_hi/lo); external/core-et/docs/CORE-ET-Shire-Cache-Specification.pdf pdf p.97 §4.1 (esr_sc_axi_qos: AXI_QOS_MEM_HIGH_PRIORITY / _LOW_PRIORITY)

## fact/ml:dram:dram.ctl.power-down
No power-down and no self-refresh: the firmware disables both 'for … its clocks running. | documented | | external/et-platform/etsoc-hal/src/memshire_ddr_init_functions.c:5459 (PWRCTL 0x0), [-:4738;-] {+:4732-4736;+} docs/research/counters-and-dram.md:331

## fact/ml:dram:dram.org.capacity
32 GB of LPDDR4X on [-the V3 cards (a Micron part):-] {+aifoundry2 and aifoundry3:+} 2 GB, i.e. 16 Gbit, per channel; {+aifoundry1 card 1 has 16 GB, 8 Gbit per channel (the sizes+} the {+firmware reads from MR8 at boot, as the driver reports them). The+} chip supports up to 32 GB 'using LPDDR4X at 16 Gbits per channel'. {+The vendor names its 32 GB V3 card a Micron part; which maker's parts the lab cards carry is not recorded.+} | [-documented-] {+measured+} | {+three cards+} | {+docs/reports/data/2026-09-27-pcie/raw/<card>/r1/info.err ('DRAM size (B)': 34265366528 on aifoundry2 and aifoundry3, 17085497344 on aifoundry1-c1: 32 and 16 GiB less the 90 MiB the device keeps); external/et-platform/device-bootloaders/src/ServiceProcessorBL2/driver/mem_controller.c:389-420 (the MR8 density sets the size);+} external/et-man/ET-PCIe-Dev-Card-V3.pdf pdf p.1 ('32GB (Micron part) v3 card'); external/et-man/ET Preliminary Datasheet Rev 1.0.pdf pdf p.30 [-§7.1; external/et-platform/device-bootloaders/src/ServiceProcessorBL2/driver/mem_controller.c:389-398 (MR8 density decode to 32 GB)-] {+§7.1+}

## fact/ml:dram:dram.org.geometry
[-Each-] {+On the 32 GB cards (aifoundry2, aifoundry3) each+} channel is one rank of 8 banks x 131,072 rows … 8 x 131,072 x 2 KB = 2 GB, matching [-the capacity.-] {+their capacity (aifoundry1 card 1's 1 GB channels are a smaller die).+} One activate therefore senses 16,384 bits into one bank's sense … Gb-per-channel LPDDR4 die (8 banks, R0-R16, C0-C9, 2 KB page)

## fact/ml:dram:dram.org.part
The exact LPDDR4X part [-(Micron-] {+(its maker and+} part number), its die density, the number of dies per … part it is 0x10 for 32gb and 0x18 for 64gb')

## fact/ml:dram:dram.topo.floorplan
(new)
```
On the die the memory shires and their LPDDR4X PHYs form a strip about 1.76 mm wide down each side (1.74 and 1.80 mm); the 6-column shire grid between them spans about 22.2 mm. Heat per millimetre | model |  | docs/reports/data/2026-09-27-chip-diagram/facts.json facts['L08'], facts['L09'] (from docs/reports/data/2026-09-24-wire-energy/report.json inputs.memshire_w_mm)
```

## fact/ml:dram:gen.jedec-match
The programmed timings are close to JEDEC LPDDR4's limits for a 16 Gb-per-channel die at 3,733 [-MT/s,-] {+MT/s (JESD209-4's tables+} as [-recalled from JESD209-4 and-] {+a Micron LPDDR4/LPDDR4X datasheet reproduces them,+} not [-checked against-] the [-standard:-] {+standard itself):+} tRCD and tRPpb 18 ns minimum, tRAS 42 ns, tRRD 10 ns, tFAW 40 [-ns, tRFCab 280-] ns; RL 36 (with read DBI) and WL 16 are the [-fixed-] read and write latencies for this rate, and tREFI 3.875 us is just under the 3.904 us maximum interval. {+The refresh is the exception on the 32 GB cards: JEDEC's tRFCab for 12-16 Gb per channel is 380 ns, and the programmed 280.7 ns is about 100 ns shorter, which needs a part rated better than JEDEC, such as Micron's 16 Gb single-channel LPDDR4X die (280 ns); the cards' exact part is not known (dram.org.part).+} | textbook | | GENERIC comparison: JEDEC JESD209-4 {+tables as reproduced in Micron's 200b x16/x32 LPDDR4/LPDDR4X datasheet (MT53E1G32D2 family) Rev. F 12/2020, Table 111 (tRFCab 130/180/280/380 ns for 2/3-4/6-8/12-16 Gb per channel), Table 3 (16 Gb single-channel die 280 ns, 'improved+} values [-recalled, not checked against-] {+from JEDEC') and Table 196; density: external/et-platform/device-bootloaders/src/ServiceProcessorBL2/utils/mem_controller_utils.c:993-999 and include/mem_controller.h:137 (MR8 density code 6,+} the [-standard (no ET source);-] {+firmware's 32 GB setting, which the driver reports on aifoundry2 and aifoundry3: dram.org.capacity);+} ET values from dram.ctl.*

## fact/ml:l1:g.latch-read
A latch-array read is logic: the registered address drives a decoder or a mux tree (128:1 per output bit, e.g. seven 2:1 {+levels, or three 4:1+} levels [-or four 4:1 levels),-] {+and one 2:1),+} and only the nodes whose value changes spend energy, so … data. | textbook | | textbook standard-cell memory design (GENERIC)

## fact/ml:l1:l1.bw
L1 bandwidth: 14.5 TB/s over the chip with 32-byte vector … manual | measured | three cards | docs/energy-manual/04-bytes-memory.md:11 (14,488 GB/s); [-docs/findings/05-claims.md:380-] {+docs/findings/05-claims.md:398+} (6.2 TB/s)

## fact/ml:l1:l1.firmware-mode
The firmware sets D1Split and ScpEnable before every launch, so … a 3 KB scratchpad. Memory hierarchy | documented | | [-docs/et-soc1-notes.md:84-86;-] {+docs/et-soc1-notes.md:90-92;+} docs/research/counters-and-dram.md:447 (fw MachineMinion/src/syscall.c:348-420)

## fact/ml:l1:l1.latency
L1 hit: 5.25 cycles load-to-use in a dependent pointer chase … Memory hierarchy | measured | three cards | docs/reports/data/2026-09-25-claims-v3/results/lat.json: items[LAT-M1].per_card.<card>.passes[].L1; [-docs/findings/05-claims.md:421-] {+docs/findings/05-claims.md:443+}

## fact/ml:l1:l1.transistors
Estimate: at 8-12 transistors per latch bit, the data array … | l1.bits x GENERIC transistors per bit; chip total from [-docs/findings/01-resources.md:101-] {+docs/findings/01-resources.md:121+}

## fact/ml:l1:l1.voltage
The latch arrays switch at the minion-rail voltage: 0.517 V … mV. DVFS and leakage | measured | aifoundry2, aifoundry3 | [-docs/findings/16-dvfs-and-leakage.md:20;-] {+docs/findings/16-dvfs-and-leakage.md:39;+} docs/research/power-telemetry.md:44 (ET-PCIe-Dev-Card-V3), :189-190 (bl2_pmic_controller.h:165-244)

## fact/ml:l2:l2.bw.measured
With 1 KB tensor loads on every minion the L2 … (2.46 TB/s). Memory hierarchy | measured | three cards | [-docs/findings/05-claims.md:380, 546; docs/findings/15-earlier-findings.md:98-] {+docs/findings/05-claims.md:398, 805; docs/findings/15-earlier-findings.md:112+}

## fact/ml:l2:l2.clock
(new)
```
The shire cache runs on shire_clock from the shire's PLL. The neighbourhoods (minions) run on the same clock shifted by 180 degrees (a DLL), and the errata note that every area of a minion shire except the NoC uses the same clock. So one shire-cache cycle is one minion cycle. | documented |  | external/core-et/docs/CORE-ET Minion Shire Description.pdf, pdf p.12 Table 2; external/core-et/docs/CORE-ET-Neigborhood-MAS.pdf, pdf p.39 Table 6; external/et-man/ET-SoC Errata.pdf, pdf p.42
```

## fact/ml:l2:l2.data-ram
Data RAM: each sub-bank is four 144-bit-wide panels, each holding … bits); a sub-bank's data RAM is 4,096 rows addressed by [-{way, set}.-] {+{set, way} (set-major, as the re-implementation's RTL has it; the Erbium header fixes only the width, way + set bits).+} | documented | | external/core-et/docs/CORE-ET-Shire-Cache-Specification.pdf (v1.1), pdf p.48 §2.14.5 and pdf p.48-49 §2.14.6.2; [-external/core-et/rtl/inc/shire_cache_defines.vh:250-255-] {+external/core-et/rtl/inc/shire_cache_defines.vh:250-255; external/core-et-main/hw/ip/shirecache/rtl/shirecache_pipe_sub_bank.sv:1613+}

## fact/ml:l2:l2.e.scalar
One random flw from the L2 (a line per load) … back. The energy manual | measured | three cards | [-docs/findings/05-claims.md:509;-] {+docs/findings/05-claims.md:535;+} docs/energy-manual/04-bytes-memory.md:55

## fact/ml:l2:l2.ecc
All shire-cache RAMs have SECDED ECC (single-error correct, double-error detect): … | external/core-et/docs/CORE-ET-Shire-Cache-Specification.pdf (v1.1), pdf p.9, pdf p.48-49 §2.14.6.2, pdf p.99; [-docs/findings/15-earlier-findings.md:65-66-] {+docs/findings/15-earlier-findings.md:75-76+}

## fact/ml:l2:l2.lat.measured
Load-to-use latency by pointer chase at 600 MHz: read-buffer hit … and 46.998-47.024. Memory hierarchy | measured | three cards | [-docs/findings/05-claims.md:421;-] {+docs/findings/05-claims.md:443;+} docs/reports/data/2026-09-25-claims-v3/results/lat.json items[LAT-M1].per_card.<card>.passes[] (RB, L2, hart1)

## fact/ml:l2:l2.lat.overhead
Measured minus spec is 26 cycles for both (47 - … | | derived from external/core-et/docs/CORE-ET-Shire-Cache-Specification.pdf (v1.1), pdf p.11 Table 1, [-docs/findings/05-claims.md:421-] {+docs/findings/05-claims.md:443+} and external/core-et/docs/CORE-ET-Neigborhood-MAS.pdf, pdf p.20-21

## fact/ml:l2:l2.leak
SRAM-rail power at idle: 2.00 W for the chip (about … cards. DVFS and leakage | measured | three cards | [-docs/findings/05-claims.md:184, 473; docs/findings/16-dvfs-and-leakage.md:141;-] {+docs/findings/05-claims.md:195, 499; docs/findings/16-dvfs-and-leakage.md:189;+} docs/energy-manual/04a-fine-grain.md:110 ('Measured: 1.70 W at 67 °C') and its table (67 °C 1.698 W, 82 °C 2.726 W)

## fact/ml:l2:l2.path.widths
The neighbourhood's request datapath is 256 bits wide (a 512-bit write takes two [-cycles-] {+cycles, crosses the bank FIFO as two 256-bit entries+} and is re-joined [-before the bank FIFO);-] {+into one 512-bit ET-Link request at its output);+} its response datapath and the ET-Link into each bank are … §4.3.5, p.20 §4.4, p.22-23 §4.4.3; external/core-et/docs/CORE-ET-Shire-Cache-Specification.pdf (v1.1), pdf p.10 §1.1

## fact/ml:l2:l2.rbuf.enabled
The RBUF is on by default (esr_sc_l2_rbuf_enable = esr_sc_scp_rbuf_enable = 1 in the {+reset value of the+} RTL's [-ESR init),-] {+sc_pipe_ctl register),+} and the cards show it: a 36-cycle plateau for working … three cards. Memory hierarchy | model | three cards | [-external/core-et/rtl/shire/esr/esr_cache_bank.v:311-312;-] {+external/core-et/rtl/inc/esr_defines.vh:66 (ESR_SC_PIPE_CTL_RESET_VAL), applied by external/core-et/rtl/shire/esr/esr_cache_bank_auto.v:215;+} docs/reports/data/2026-09-25-claims-v3/results/lat.json items[LAT-M1] (knees between 512/768 B and 2/4 KB)

## fact/ml:l2:l2.voltage.idle
Measured on-die SRAM-rail voltage per shire at idle: 703-707 mV … 483-486 mV). The ET-SoC-1, interactively | measured | aifoundry2 | [-docs/findings/05-claims.md:41-] {+docs/findings/05-claims.md:49+} (docs/reports/data/2026-09-20-power-aifoundry2/per-shire-voltage-idle.json)

## fact/ml:l3:g.crossing
GENERIC. A voltage and clock crossing: a level shifter (cross-coupled … and a 2-flip-flop synchroniser (as the spec's VCFIFO uses) samples [-it-] {+the FIFO's gray-coded counts+} in the receiving clock, costing 2-3 receiving-clock cycles. | textbook | | textbook; the 2 stages are et-spec (external/core-et/docs/CORE-ET-Shire-Cache-Specification.pdf pdf p.11)

## fact/ml:l3:g.wire-energy
GENERIC. A wire's switching energy is about C x V^2 … zeros; repeaters add to it. | textbook | | textbook; [-docs/reports/data/2026-09-24-wire-energy/research/SYNTHESIS.md:135-147-] {+docs/reports/data/2026-09-24-wire-energy/research/SYNTHESIS.md:142-154+} (literature table)

## fact/ml:l3:l3.clock
The shire cache runs on shire_clock, the same clock as … Errata.pdf pdf p.42; clk__noc 400 MHz: telemetry mhz.noc (docs/reports/data/2026-09-20-power-aifoundry2/horace-telemetry.jsonl) and [-SYNTHESIS.md:72-] {+SYNTHESIS.md:79+}

## fact/ml:l3:l3.flits
A read request is about 75-85 bits (AXI AR); the … carries the line. Heat per millimetre | documented | | [-docs/reports/data/2026-09-24-wire-energy/research/SYNTHESIS.md:64, 77-] {+docs/reports/data/2026-09-24-wire-energy/research/SYNTHESIS.md:71, 84+} (external/core-et/rtl/inc/axi_defines.vh:39, 43, 61, 69)

## fact/ml:l3:l3.hop
Each mesh hop adds 12 cycles to the round trip … TensorSend (12.02). On-chip communication | measured | three cards | [-docs/findings/05-claims.md:415, 423, 392; workloads/memprobe/report_template.html:881-884-] {+docs/findings/05-claims.md:434, 445, 446; workloads/memprobe/report_template.html:879-883+}

## fact/ml:l3:l3.hop-noc-cycles
20 ns per hop round trip is 10 ns, or … Heat per millimetre | model | | l3.hop with l3.clock; [-docs/reports/data/2026-09-24-wire-energy/research/SYNTHESIS.md:76-] {+docs/reports/data/2026-09-24-wire-energy/research/SYNTHESIS.md:83+}

## fact/ml:l3:l3.hv-region
The Shire Channel, which holds the shire cache, the UC … Description.pdf pdf p.10 §3.1 and pdf p.18 §5; external/core-et/rtl/libs/mems_and_fifos/vcfifo_nsip_brdg2rtr.v:9 (via [-docs/reports/data/2026-09-24-wire-energy/research/SYNTHESIS.md:74)-] {+docs/reports/data/2026-09-24-wire-energy/research/SYNTHESIS.md:81)+}

## fact/ml:l3:l3.leakage
The SRAM rail at idle is 1.70 W at 67 … its table (67 °C 1.698 W, 82 °C 2.726 W); [-docs/findings/05-claims.md:473-] {+docs/findings/05-claims.md:499+}

## fact/ml:l3:l3.mesh-rail
The mesh (routers, links, NetSpeed bridges) runs at 485 mV … cards. Heat per millimetre | measured | three cards | [-SYNTHESIS.md:72-74-] {+SYNTHESIS.md:79-81+} (telemetry reg_mv.noc, die_mv.noc, mhz.noc)

## fact/ml:l3:l3.ports
Each shire meets the mesh with 4 L3-slave ports (incoming … for the L3 mesh and one for the SYS mesh'); [-external/core-et-main/hw/ip/shirecache/rtl/shirecache_pkg.sv:138-139-] {+external/core-et-main/hw/ip/shirecache/rtl/shirecache_pkg.sv:138-140+}

## fact/ml:l3:l3.route
Routes are minimal (latency is linear in Manhattan distance over … the drop. On-chip communication | measured | three cards | [-docs/findings/05-claims.md:392; docs/reports/data/2026-09-24-wire-energy/research/SYNTHESIS.md:66-68, 75;-] {+docs/findings/05-claims.md:446; docs/reports/data/2026-09-24-wire-energy/research/SYNTHESIS.md:73-75, 82;+} the order: docs/reports/data/2026-09-29-nocr (E56), the chip tour's fact L104

## fact/ml:l3:l3.sram-rail
The SRAM rail sits at 705 mV (703-707 mV on … (483-486 mV). Power and temperature | measured | aifoundry2 | [-docs/findings/05-claims.md:41-] {+docs/findings/05-claims.md:49+} (docs/reports/data/2026-09-20-power-aifoundry2/per-shire-voltage-idle.json); telemetry fields reg_mv.sram, die_mv.sram

## fact/ml:l3:l3.wire-energy
A random bit costs [-36.2-] {+36.7+} fJ per mm on the mesh rail over free links [-(46.7-] {+(47.4+} on board [-power).-] {+power; three cards).+} A 64 B reply over one 3.72 mm hop is then about [-69-] {+70+} pJ on the mesh rail (1.1 pJ/B per hop); on … 43 on zeros (l3.energy-per-load). Heat per millimetre | model | [-aifoundry2, aifoundry3-] {+three cards+} | [-docs/findings/05-claims.md:350, 457-] {+docs/findings/05-claims.md:362, 482+} (docs/reports/data/2026-09-24-wire-energy/report.json headline['uncontended/noc_rail']); hop length [-docs/findings/05-claims.md:349-] {+docs/findings/05-claims.md:361+}

## fact/ml:l3:u.noc-hop
UNKNOWN. The router pipeline per hop (4 NoC cycles each … until 29 September, is measured (l3.route). | unknown | | [-docs/reports/data/2026-09-24-wire-energy/research/SYNTHESIS.md:66-68, 75-76;-] {+docs/reports/data/2026-09-24-wire-energy/research/SYNTHESIS.md:73-75, 82-83;+} the order: docs/reports/data/2026-09-29-nocr (E56)

## fact/ml:scp:scp.atomic
A global atomic on a scratchpad word is performed by … external/core-et/docs/CORE-ET-Shire-Cache-Specification.pdf p.17 (L3 slave REQ_Atomic, local SCP), p.36, p.40 §2.9; [-docs/findings/05-claims.md:232; docs/findings/17-hot-line.md:35-38;-] {+docs/findings/05-claims.md:243; docs/findings/17-hot-line.md:36-39;+} lat.json [item=LAT-H]

## fact/ml:scp:scp.lat-remote
Another shire's scratchpad: 99.84 + 12.00 cycles per mesh hop … three cards. Memory hierarchy | measured | three cards | [-docs/findings/05-claims.md:423;-] {+docs/findings/05-claims.md:445;+} lat.json items[LAT-M3].per_card.<card>.passes[] (row0_slope 11.998-12.002, frac_within_1 1.0)

## fact/ml:scp:scp.leak
The SRAM rail at idle (all 128 MB of L2, … The energy manual | measured | three cards | docs/energy-manual/04a-fine-grain.md:104-115; [-docs/findings/05-claims.md:312, :473-] {+docs/findings/05-claims.md:324, :499+}

## fact/ml:scp:scp.panel-count
Per shire 64 data panels (4 banks x 4 sub-banks x 4), each 589,824 bits; 37.7 Mbit per shire including ECC [-(32-] {+(33.55+} Mbit data + [-4-] {+4.19+} Mbit ECC); 2,048 data panels over the 32 compute shires. | model | | external/core-et/docs/CORE-ET-Shire-Cache-Specification.pdf p.9, p.48, p.51

## fact/mm-board-w
Board power during the fp32 L2 matmul that runs at … run (138-189). Matmul efficiency | model | three cards | [-docs/findings/05-claims.md:418-] {+docs/findings/05-claims.md:453+} (E37, MMB-c: docs/reports/data/2026-09-25-claims-v3/results/mmb.json .items[item=MMB-c].per_card.<card>["fp32-tensor-L2"].board_w, .idle_before_w, .mean, .die_c_mean) and [-:419-] {+:454+} (MMB-d, GFLOP/s per W)

## fact/mm-peak
Tensor peak per minion-cycle: 16 fp32 / 32 fp16 / … MHz. Ridge points | documented | | ridge-data: peaks.<fp32|fp16|int8>.per_cycle, chip_600; [-docs/findings/05-claims.md:485-] {+docs/findings/05-claims.md:804+}

## fact/mm-perw
Board GFLOP/s per [-W,-] {+W (GOP/s per W for int8),+} L2 matmul fp32 / fp16 / int8: aifoundry2 161 / … die temperature). Matmul efficiency | measured | three cards | [-docs/findings/05-claims.md:419-] {+docs/findings/05-claims.md:454+}

## fact/mm-rate
Tensor matmul, tiles in L2, all 1,024 minions at 600 … Matmul efficiency | measured | three cards | docs/reports/data/2026-09-25-claims-v3/results/mmb.json: items[MMB-b].per_card.<card>.<mode>.tflops_pass_values; [-docs/findings/05-claims.md:417-] {+docs/findings/05-claims.md:452+}

## fact/mm.dram
The same benchmark with 64 private tiles per minion, so that every load comes from [-DRAM: 15,042-15,663-] {+DRAM, on the three cards: 16,132-16,278+} cycles per op [-and-] {+on the slowest minion, whose finish sets the+} 0.309-0.312 TFLOP/s {+(15,042-15,663+} on the [-three cards,-] {+average minion),+} about 30 times slower than with the tiles in the L2. Matmul efficiency | measured | three cards | docs/reports/data/2026-09-25-claims-v3/results/mmb.json: [-[item=MMB-a].per_card.<card>."fp32-tensor-DRAM".cycles_per_op_mean_based,-] {+[item=MMB-a].per_card.<card>."fp32-tensor-DRAM".cycles_per_op_max_based, .cycles_per_op_mean_based,+} .info_tflops_range; {+tools/claims-v3/mmb/reduce.py:311-312, 325-326, 432-446; launchers/mmbench/mmbench.cpp:281-282, 288-290, 302-304 (cycles_max is the slowest minion, cycles_mean the average over the minions, tflops the FLOP over the launch's wall time);+} tools/claims-v3/mmb/mmbench_power_v3.py:65

## fact/ms-fit-3cards
Left as fitted on aifoundry2 on 19 September (constant 91 … DRAM latency model is within ±3 cycles for 93-97% of [-loads-] {+lines (each line's fastest of three loads)+} on all three cards: aifoundry2 97.0%, aifoundry3 92.9%, aifoundry1-c1 94.4% (5 passes each). Anatomy of a memory access | measured | three cards | [-docs/findings/05-claims.md:404-] {+docs/findings/05-claims.md:435+} (E35, MEM-P2: docs/reports/data/2026-09-25-claims-v3/results/mem.json [item=MEM-P2].per_card.<card>.tests.P2_dram_within3_frac)

## fact/ms2-forced
Memory shire 2's fit ties (3, -1), (5, -1) and … is the only place left. | model | | L42 [-(docs/reports/2026-09-19-et-soc1-memory-anatomy.html:778-780);-] {+(docs/reports/2026-09-19-et-soc1-memory-anatomy.html:810-812);+} external/et-man/ET Preliminary Datasheet Rev 1.0.pdf, pdf p.21 (§4: 'the corners of the grid are not occupied')

## fact/n7.cells
Standard cells are 240 nm tall (high density, 6 tracks, … (high performance, 7.5 tracks, 10 fin pitches, 64 nm gate [-pitch); a 360 nm 9-track variant also exists.-] {+pitch).+} fuse.wikichip.org | outside source | | D. Schor, "TSMC 7nm … read via the Internet Archive capture of 13 Nov 2019

## fact/n7.weff
One fin gives about 110 nm of channel width: the … | C. Hu, ch. 7 (the rule) with n7.fin-height and [-n7.fin-width-] {+n7.fin-width; the comparison with N16: WikiChip, "7 nm lithography process" (comparison table and TSMC section); read via the Internet Archive capture of 16 Jun 2025+}

## fact/out.card.1
6.6 x 4.4 in (167.6 x 111.8 mm); a PCIe … documented | | Esperanto, "PCIe Dev Card (V3)", ET-PCIe-Dev-Card-V3.pdf (github.com/aifoundry-org/et-man), [-pp. 1 and-] {+p.+} 3

## fact/out.card.10
Also on the board: 64 GB of eMMC flash (a … | | Esperanto, "PCIe Dev Card (V3)", ET-PCIe-Dev-Card-V3.pdf (github.com/aifoundry-org/et-man), pp. [-1-3-] {+2-3+}

## fact/out.card.2
On all four lab cards the link runs at 16 … docs/reports/data/2026-09-27-pcie/hosts.txt (the link speed and width of all four cards); [-docs/findings/05-claims.md:550-552-] {+docs/findings/05-claims.md:552-554+} (E50: the DMA rates, on three cards)

## fact/out.card.3
Four LPDDR4X memory packages, 256 bits wide in all (16 … docs/reports/data/2026-09-27-chip-diagram/facts.json (L47, dram.channels); Esperanto, "PCIe Dev Card (V3)", ET-PCIe-Dev-Card-V3.pdf (github.com/aifoundry-org/et-man), [-p.-] {+pp.+} 1 {+(the "32GB (Micron part) v3 card" link) and 3 (features)+}

## fact/out.card.4
Peak memory rate on these cards: 256 bits x 3,733 … the datasheet's 4,266 MT/s would give 136.5 GB/s. Tensor loads {+stream 76 GB/s+} from [-memory have been measured at 75 GB/s.-] {+this memory, 64% of the 119.5 GB/s peak (fact bw-dram).+} | model | | docs/reports/data/2026-09-27-chip-diagram/facts.json (dram.rate-card: the firmware hard-codes 3,733 MT/s on every card; dram.peak-card; L47: the datasheet's 4,266 Mb/s per [-pin); docs/findings/05-claims.md:155 (E15)-] {+pin; bw-dram: 75.9 GB/s); docs/findings/05-claims.md:398 (row "Bandwidth at 600 MHz, 1,024 minions": E33, E29, E43)+}

## fact/out.card.6
Power arrives as 12 V at the card [-edge: at most-] {+edge; the vendor's power tree budgets+} 7.3 A, 88 W. [-The-] {+Under load the+} highest draw on record is 87.8 W; {+an idle card whose cooling failed drew 134 W before it dropped off the PCIe bus (aifoundry2, 2, 7 and 8 Oct 2026). With working cooling+} the cards idle at about [-19-36-] {+19-50+} W, depending on the card and its [-temperature.-] {+temperature (aifoundry1 card 1 idles highest: 42.7 W at 73 °C, 50 W at 80 °C).+} | documented | | Esperanto, "PCIe Dev Card (V3)", ET-PCIe-Dev-Card-V3.pdf (github.com/aifoundry-org/et-man), p. 5 (power tree); [-docs/findings/14-card-behaviour.md:138, 339-] {+docs/findings/14-card-behaviour.md:158 (87.8 W), :382 (idle), :252-253 and :625-627 (134 W); docs/reports/data/2026-10-02-idle-runaway-aifoundry2/records.jsonl (133.8 W board power); docs/energy-manual/01-at-rest.md:25, 33 (aifoundry1 card 1, board 42.71 W at 73 °C); docs/reports/data/2026-09-25-claims-v3/results/abla.json (all_cards.idle_clock.aifoundry1-c1.idle_w, 50.15 W); docs/reports/2026-09-18-et-soc1-matmul-efficiency.html:727 ("also at 80 °C but idling at 50 W")+}

## fact/out.card.7
The cores run at about 0.52 V at 600 MHz, … | | Esperanto, "PCIe Dev Card (V3)", ET-PCIe-Dev-Card-V3.pdf (github.com/aifoundry-org/et-man), p. [-1-] {+5+} (key voltage regulators) and p. 2 (photo); docs/findings/05-claims.md:34 (E9)

## fact/out.card.8
An Analog Devices LTM4680 module (up to 60 A) supplies … | | Esperanto, "PCIe Dev Card (V3)", ET-PCIe-Dev-Card-V3.pdf (github.com/aifoundry-org/et-man), pp. [-1, 4-] {+4-7+}

## fact/out.host.1
The lab's three hosts: aifoundry1, an Intel Core i7-11700K (8 … single memory channel. | measured | card not recorded | [-docs/findings/14-card-behaviour.md:348;-] {+docs/findings/14-card-behaviour.md:391;+} the et-lab-manifest records

## fact/out.host.2
[-aifoundry2's motherboard is a-] {+All three hosts' motherboards are+} Gigabyte Z590 AORUS [-MASTER, an ATX board of-] {+MASTER boards, ATX,+} 30.5 x 24.4 [-cm. The other two hosts'-] {+cm; aifoundry1 and aifoundry2 run+} BIOS [-versions (F5, F6) follow Gigabyte's naming, but their board models are not recorded.-] {+F5, aifoundry3 F6.+} | [-inference-] {+documented+} | | the [-host's-] {+hosts'+} DMI [-table (/sys/devices/virtual/dmi/id,-] {+tables (all three+} read {+in the lab's root audit of 25 Sep 2026, recorded in the lab-problems report, H20; aifoundry2's again on+} 30 Sep {+and 14 Oct+} 2026); Gigabyte, Z590 AORUS MASTER specifications (gigabyte.com); [-docs/findings/14-card-behaviour.md:348-] {+docs/findings/14-card-behaviour.md:391 (BIOS), :541 (aifoundry3's board), :563 (aifoundry2's board)+}

## fact/out.host.5
The host CPUs are made in Intel's 14 nm process; … turbo (its PL2), the i5-11600 at 65 W base. The [-whole-] ET [-card, at most-] {+card's+} 88 [-W, draws-] {+W budget is+} less than the bigger CPU's base [-power,-] {+power+} and about a third of its turbo peak. | documented … techreviewer.com; Esperanto, "PCIe Dev Card (V3)", ET-PCIe-Dev-Card-V3.pdf (github.com/aifoundry-org/et-man), p. 5

## fact/out.host.6
The host copies memory at 17.4 / 9.2 / 21.4 … link: 5.2-7.8 GB/s. | measured | card not recorded | [-docs/findings/05-claims.md:553-] {+docs/findings/05-claims.md:555+} (E50)

## fact/out.package.8
Light crosses the die (25.6 mm) in 0.085 ns, about … 2019): c = 299 792 458 m/s exactly; the clock: [-docs/findings/14-card-behaviour.md:338-] {+docs/findings/14-card-behaviour.md:381+}

## fact/p.atom.10
With more than 24 billion transistors and about 257,000 atoms … all the silicon that actually switches. | inference | | [-process.json beside this file:-] {+docs/reports/data/2026-10-01-ladder/research/process.json:+} TSMC N7's fin, 6 nm wide and 52 nm tall … billion transistors (Esperanto, Hot Chips 33 and IEEE Micro 2022)

## fact/p.atom.9
A FinFET channel of about 6 x 16.5 x 52 … in from the heavily doped source. | inference | | [-process.json beside this file:-] {+docs/reports/data/2026-10-01-ladder/research/process.json:+} TSMC N7's fin, 6 nm wide and 52 nm tall … and carrier concentration" (www.ioffe.ru/SVA/NSM/Semicond/Si/), compiled from Sze, Shur and others

## fact/p.core.4
An electron in an atom is not a little ball on an orbit: the shells are clouds of probability, and the radii here are [-where-] each [-cloud is densest.-] {+shell's most likely distance from the nucleus.+} | textbook | | S. M. Sze and K. K. … ed. (Wiley, 2007), ch. 1 (crystal, bands, donors and acceptors)

## fact/p.dopant.2
Those energies are only about 2 kT at room temperature (2 kT = 52 meV), so nearly every dopant atom {+alone in a silicon site+} has given up (or taken) its electron. | textbook | … constants, physics.nist.gov/cuu/Constants (each constant's values page, read 1 Oct 2026)

## fact/p.dopant.7
[-The same-] {+TSMC's FinFET+} patent [-dopes the wells under-] {+(US 11,107,923) implants its wells, in+} the fins {+or the substrate,+} at {+up to 10^18 per cm3 for n-wells (10^16 to 10^18) and up to 10^20 for p-wells (10^17 to 10^20). At a bulk FinFET's usual fin doping,+} 10^16 to 10^18 per [-cm3. At those levels-] {+cm3,+} a 6 x 16.5 x 52 nm channel would hold … 2019), description (a patent's embodiments, not a statement about N7); [-the chip diagram's own tree (docs/reports/data/2026-09-27-chip-diagram/research/inside.json: lib.channel, lib.si);-] {+X. Zhang, "Simulation-based Study of Super-steep Retrograde Doped Bulk FinFET Technology and 6T-SRAM Yield", UC Berkeley EECS Technical Report UCB/EECS-2016-3, 5 Jan 2016 (www2.eecs.berkeley.edu/Pubs/TechRpts/2016/EECS-2016-3.pdf); docs/reports/data/2026-10-01-ladder/research/process.json: TSMC N7's fin, 6 nm wide and 52 nm tall (WikiChip Fuse), and effective gate length, 16.5 nm (Dick James on TSMC's IEDM 2016 paper);+} S. M. Sze and K. K. Ng, Physics of Semiconductor Devices, 3rd ed. (Wiley, 2007), ch. 1 (crystal, bands, donors and acceptors)

## fact/p.electron.4
The electron is round: its electric dipole moment is below 4.1 x 10^-30 e cm (PDG 2026), so {+the centre of+} its charge sits within 4.1 x 10^-32 m of its centre {+of mass+} (dipole moment divided by its charge). {+That limits its shape, not its size.+} | model | | Particle Data Group, F. Takahashi et al., Int. J. Mod. Phys. A 41, 2630011 (2026), summary table: leptons (pdg.lbl.gov/2026/tables/rpp2026-sum-leptons.pdf)

## fact/p.nucleon.8
Each silicon-28 atom holds 42 up and 42 down quarks … 41, 2630011 (2026), summary table: N baryons (p, n) (pdg.lbl.gov/2026/tables/rpp2026-sum-baryons.pdf); [-the chip diagram's own tree (docs/reports/data/2026-09-27-chip-diagram/research/inside.json: lib.channel, lib.si)-] {+docs/reports/data/2026-10-01-ladder/research/process.json: TSMC N7's fin, 6 nm wide and 52 nm tall (WikiChip Fuse), and effective gate length, 16.5 nm (Dick James on TSMC's IEDM 2016 paper)+}

## fact/p.nucleus.5
Its density is about [-2.3-] {+1.7+} x 10^17 kg per [-m3:-] {+m3 as a uniform sphere 8.06 fm across, or 2.3 x 10^17 at the textbook rule's radius of 3.64 fm:+} a teaspoon (5 mL) of nuclear matter would weigh about [-1.1-] {+a+} billion tonnes. | model | | IAEA Nuclear Data Section, … as widely quoted; the book not read for this page)

## fact/p.nucleus.8
That is about a million times the energy of [-the-] {+an+} outer [-electrons-] {+electron+} (8.15 eV) [-or of-] {+and nearly four million times+} a chemical bond (about 2.3 eV): why chemistry, and electronics, … as widely quoted; the book not read for this page)

## fact/p.planck.3
The quark's radius limit is 3 x 10^16 times the Planck [-length:-] {+length; even the electron's smaller limit, 2 x 10^-20 m, is 1 x 10^15 times it:+} some [-16-] {+15+} powers of ten that no experiment has probed. | model … scattering at HERA", Phys. Lett. B 757, 468 (2016), arXiv:1604.01280; {+G. Gabrielse group (Northwestern Center for Fundamental Physics), "Limit on Electron Substructure", cfp.physics.northwestern.edu/gabrielse-group/electron-substructure.html, citing D. Bourilkov, Phys. Rev. D 64, 071701(R) (2001) for the LEP contact-interaction limit;+} NIST, 2022 CODATA recommended values of the fundamental physical constants, physics.nist.gov/cuu/Constants (each constant's values page, read 1 Oct 2026)

## fact/p.quark.3
Masses (MS-bar at 2 GeV): up 2.16 +/- 0.07 [-MeV,-] {+MeV/c^2,+} down 4.70 +/- 0.07 [-MeV.-] {+MeV/c^2.+} Two ups and a down add to 9.0 [-MeV:-] {+MeV/c^2:+} 1% of the proton's 938.3 [-MeV.-] {+MeV/c^2.+} | model | | Particle Data Group, F. Takahashi et … 41, 2630011 (2026), summary table: N baryons (p, n) (pdg.lbl.gov/2026/tables/rpp2026-sum-baryons.pdf)

## fact/p.quark.4
A lattice-QCD breakdown of the proton's [-mass:-] {+mass (MS-bar at 2 GeV):+} the [-quarks'-] masses [-(through-] {+of all+} the {+quarks in it, the sea of short-lived quark-antiquark pairs (strange ones too) as well as the three, give 9% (the+} quark [-condensate, u, d and s) give 9%,-] {+condensate term);+} the quarks' energy of motion 33%, the gluon field's energy … energy momentum tensor", Phys. Rev. Lett. 121, 212001 (2018), arXiv:1808.08677

## fact/p.quark.6
Gluons carry the strong force between quarks; they are massless in theory (a mass of a few [-MeV-] {+MeV/c^2+} is not excluded) and come in eight colour states. | … Amsler, V. Crede et al., rev. Aug 2025), sec. 15.1-15.2

## fact/p.quark.7
Colour is believed to be permanently confined: only colourless combinations [-(three quarks,-] {+exist on their own, usually three quarks+} or a quark and an [-antiquark) exist on their own.-] {+antiquark; some observed states are classed as four or five quarks.+} | outside source | | Particle Data Group (2026), review 15, Quark Model (C. Amsler, V. Crede et al., rev. Aug 2025), sec. 15.1-15.2

## fact/pcie.link
Host link: PCIe Gen4 x8 on an x16 card edge; … Preliminary Datasheet Rev 1.0.pdf, pdf p.4 (§1); external/et-man/ET-PCIe-Dev-Card-V3.pdf, pdf p.3; [-docs/findings/05-claims.md:489;-] {+docs/findings/05-claims.md:808;+} docs/reports/data/2026-09-27-pcie/pcie.json (27 Sep)

## fact/power.idle
Idle card after 20.6 h with no workload: 31.79 W … DVFS loop and its leakage | measured | aifoundry2 | [-docs/findings/05-claims.md:181, 183-] {+docs/findings/05-claims.md:193, 195+} (docs/reports/data/2026-09-22-dvfs-aifoundry2/idle_20h.jsonl.gz)

## fact/relay-13x
Handing a slab to the next shire through its scratchpad … three cards | docs/reports/data/2026-09-25-claims-v3/results/rl.json: items[RL-d, part=relay DRAM / next shire].per_card.<card>.ratio_geo_mean; [-docs/findings/05-claims.md:451-] {+docs/findings/05-claims.md:490+}

## fact/relay-bw
Relay bandwidth (8 stages, 1,024 [-minions):-] {+minions; bytes read plus bytes written):+} 47.7 GB/s through DRAM, 592.5 GB/s to the next shire … aifoundry2 pass means (the other cards within 1.5%) | docs/reports/data/2026-09-22-onchip-aifoundry2/onchip.json: [-headline.<card>.<dram|hop|scp>.gb_s; docs/findings/05-claims.md:241-] {+headline.<card>.<dram|hop|scp>.gb_s, size[].by_card.<card>.hop_over_dram; workloads/onchip/kernel/onchip.c:344 (bytes = stages x chunk x 2); docs/findings/05-claims.md:451+}

## fact/relay-energy
Relay energy per byte [-(write + read):-] {+moved, each byte counted once when written and once when read:+} through DRAM 116.2 pJ/B [104.5-135.3], to the next {+shire, which reads the previous+} shire's [-scratchpad-] {+scratchpad,+} 8.9 [7.6-10.2], in the own scratchpad 4.3 [-[3.8-5.1].-] {+[3.8-5.1]; a hand-off writes every byte once and reads it once, so a byte handed to the next shire costs 17.8 pJ (232 through DRAM).+} Hand it to the next shire: on-chip relay vs DRAM | measured | three cards | manual.json: reruns.relay_pj_per_byte.<dram|hop|scp>; [-docs/energy-manual/05-bytes-between-cores.md:27-] {+docs/energy-manual/05-bytes-between-cores.md:26-28; workloads/onchip/kernel/onchip.c:344 (bytes = stages x chunk x 2: each byte counted when written and when read); tools/ettelem/analyze_reruns.py:184-188 (energy over those bytes)+}

## fact/relay-watts
The three relay media draw within a watt of each … shire: on-chip relay vs DRAM | measured | aifoundry2 | [-docs/findings/05-claims.md:250-] {+docs/findings/05-claims.md:262+}

## fact/relay.speedup
A multi-stage pipeline that [-hands-] {+has the next shire read+} each stage's output [-to-] {+from+} the [-next-] {+producing+} shire's scratchpad runs about 12.4× faster than one that goes … on-chip relay vs DRAM | measured | three cards | [-docs/findings/05-claims.md:416, 451;-] {+docs/findings/05-claims.md:451, 490;+} docs/reports/data/2026-09-23-energy-manual/reruns.json `relay_pj_per_byte`

## fact/ridge.levels
Ridge points at 600 MHz (fp32 FLOP per byte fetched): … PCIe ridge is 780-789. Ridge points | model | | [-docs/findings/05-claims.md:486-489;-] {+docs/findings/05-claims.md:805-808;+} the measured-DMA ridge computed in build_facts.py: 1,024 minions x 16 FLOP x 600 MHz (facts chip-minions, minion.vec-peak, op-600) over docs/reports/data/2026-09-27-pcie/pcie.json bw.<card>.h2d.dma[bytes=268435456].gbs.mean

## fact/scp.format0
Scratchpad address, format 0 (bit 30 = 0): 0x80000000 + … Manual.pdf, pdf p.486 (§15.3); external/core-et/docs/CORE-ET-Shire-Cache-Specification.pdf, pdf p.10, p.24 (§1.4.1.3); external/et-platform/et-common-libs/include/system/layout.h:71-76; [-docs/et-soc1-notes.md:88-] {+docs/et-soc1-notes.md:96-97+}

## fact/scp.offset0
Offset 0 of a shire's scratchpad faults; a global atomic … shire: on-chip relay vs DRAM | measured | aifoundry2 | [-docs/findings/05-claims.md:231, 256-] {+docs/findings/05-claims.md:243, 268+}

## fact/shire.l2-bw-spec
Spec L2 bandwidth: four banks × 64 B = 256 … minions at 600 MHz. Ridge points | model | | [-docs/findings/05-claims.md:486; docs/et-soc1-notes.md:249;-] {+docs/findings/05-claims.md:805; docs/et-soc1-notes.md:269;+} external/core-et/docs/CORE-ET-Shire-Cache-Specification.pdf, pdf p.11 ('Read Bandwidth')

## fact/shire.voltage-domains
A shire spans several voltage domains separated by level shifters and FIFOs: minions on the low-voltage minion rail, the {+shire cache's+} SRAM arrays [-(shire cache, and-] {+on+} the {+SRAM rail, the L1+} I-cache data [-memory, placed-] {+memory+} in the [-shire channel-] {+Shire Channel+} because it must run at high [-voltage) on the SRAM rail,-] {+voltage (the description names no rail for it),+} the mesh stop on the NoC rail. Why is it … Description.pdf, pdf p.4, p.10 (§3.1) and p.18 (§5); docs/research/why-low-power.md:23-28 (R6)

## fact/si.mobility
In pure silicon electrons move about 3 times more easily than holes (mobility up to 1,400 vs 450 cm²/V·s); {+in a transistor's channel+} electrons saturate at about 8e6 cm/s, so crossing a 16.5 … properties of Silicon (Si)" (read via the mirror at www-f9.ijs.si) {+(the mobilities); C. Hu, Modern Semiconductor Devices for Integrated Circuits (Pearson 2010), ch. 6 (the saturation velocity in a transistor channel, 8 x 10^6 cm/s)+}

## fact/si.planes-width
Across a 6 nm fin there are about 31 planes … 52 nm fin about 383 planes (96 unit cells). | [-model-] {+inference+} | | arithmetic on si.lattice, n7.fin-width, n7.leff, n7.fin-height

## fact/size.core.irf
Integer register file: about 40 µm across, the width of the view that frames it. [-4,096-] {+3,968+} latch bits at roughly 0.15-0.2 um2 each (an HD latch, … inference | | the deep zoom's scale ladder (research/inside.json, size)

## fact/size.mesh
[-The-] {+One+} mesh [-(network on chip):-] {+hop:+} about [-22.2-] {+3.72+} mm across, the width of the view that frames it. {+one hop: one tile pitch (chip.hop-pitch);+} the {+whole mesh spans the die, its+} 6-column shire grid [-spans-] about 22.2 mm [-(L08); with the memory shires the mesh spans the die-] {+(L08)+} | [-model-] {+inference+} | | the deep zoom's scale ladder (research/inside.json, size)

## fact/size.shire.neigh.xing
(new)
```
Bank FIFOs: the voltage and clock crossing: about 50 µm across, the width of the view that frames it. order of magnitude: five output FIFOs (four for the banks, one for the UC block) of three 256-bit entries, with level shifters at the edge | inference |  | the deep zoom's scale ladder (research/inside.json, size)
```

## fact/size.shire.uc.fcc
[-Fast credit counters:-] {+Credit increments (CREDINC0-3):+} about 50 µm across, the width of the view that frames it. order of magnitude: [-4 counters-] {+the CREDINC decode (the counters, two+} per [-minion-] {+hart, sit in each minion)+} | inference | | the deep zoom's scale ladder (research/inside.json, size)

## fact/size.tensor
Tensor sequencer: about 100 µm across, the width of the view that frames it. order of magnitude: state [-machines-] {+machines; TenB+} and [-two 1 KiB buffers-] {+TenC, drawn here as the tensor extension's state, sit in the lanes' TIMA units in the RTL+} | inference | | the deep zoom's scale ladder (research/inside.json, size)

## fact/sram-idle
SRAM rail at idle (leakage of the L2/L3/scratchpad arrays): 1.60 … aifoundry3. The energy manual | measured | aifoundry2, aifoundry3 | [-docs/findings/05-claims.md:309; docs/findings/05-claims.md:459-] {+docs/findings/05-claims.md:324; docs/findings/05-claims.md:499+}

## fact/sync-allreduce1024
Hardware allreduce of 32 B over all 1,024 minions: 1,393 … On-chip communication | measured | three cards | lat.json: items[LAT-N4].per_card.<card>.passes[].allreduce_1024; [-docs/findings/05-claims.md:413-] {+docs/findings/05-claims.md:447+}

## fact/sync-allreduce32
Hardware allreduce (TensorReduce + TensorBroadcast) of 32 B over a … On-chip communication | measured | three cards | lat.json: items[LAT-N1].per_card.<card>.passes[].allreduce32; [-docs/findings/05-claims.md:413-] {+docs/findings/05-claims.md:447+}

## fact/sync-chip-barrier
Chip-wide barrier built from FLB, global atomics and credits: 4,976-4,991 … On-chip communication | measured | three cards | lat.json: items[LAT-N4].per_card.<card>.passes[].chip_barrier; [-docs/findings/05-claims.md:413-] {+docs/findings/05-claims.md:447+}

## fact/sync-shire-barrier
Shire barrier (fast local barrier + credits, 32 minions, all … On-chip communication | measured | three cards | lat.json: items[LAT-N1].per_card.<card>.passes[].shire_barrier; [-docs/findings/05-claims.md:413-] {+docs/findings/05-claims.md:447+}

## fact/tb.booth
Radix-4 (modified) Booth recoding looks at overlapping triples of multiplier … each bit of a partial product is a multiplexer choosing [-x(j)-] {+x(j), x(j-1)+} or [-x(j-1),-] {+0,+} followed by an XOR with the sign. | textbook | … and Systems Perspective, 4th ed. (Addison-Wesley, 2011), ch. 11 (multiplication)

## fact/tb.fifo
A first-in, first-out queue is a small memory addressed by a write pointer and a read pointer, two [-counters; comparing-] {+counters. Equal pointers mean empty or full; one way to tell them apart is a pointer one bit wider than+} the [-pointers tells a full-] {+address: equal in every bit, the+} queue [-from an empty one.-] {+is empty; equal but for that extra bit, it is full.+} | textbook | | N. Weste and D. Harris, CMOS … Systems Perspective, 4th ed. (Addison-Wesley, 2011), ch. 12 (serial-access memories: [-queues)-] {+queues); C. E. Cummings, "Simulation and Synthesis Techniques for Asynchronous FIFO Design", SNUG San Jose 2002, §2.2 (p. 3): the extra pointer bit+}

## fact/tb.icg
An integrated clock gate [-latches-] {+passes+} the enable {+through a latch that is transparent+} while the clock is [-high-] {+low and holds it while the clock is high,+} and ANDs [-it-] {+the held enable+} with the clock: a block whose enable is low gets … 2011), ch. 10 (sequential circuits) and ch. 5 (power: clock [-gating)-] {+gating); external/core-et/rtl/libs/rf_latches/et_clk_gate.v:22-29 (core-et's clock gate, Erbium branch: the enable is loaded while clk is low; enclk = clk && en_1p)+}

## fact/tb.powerfet
A power MOSFET is thousands of small cells in parallel: in a trench-gate [-device, current flows-] {+device conducting with its drain positive, electrons flow+} vertically, from the source on top, down a channel along … doped drift layer to the heavily doped substrate, the drain, [-underneath;-] {+underneath, and the current flows up;+} its on-resistance is milliohms and it blocks tens of volts. … Semiconductor Devices, 2nd ed. (Springer, 2019), ch. 6 (power MOSFETs)

## fact/tb.prefix
A parallel-prefix adder computes for each bit a generate g … cells (G = Gi + Pi·Gj, P = Pi·Pj) of {+as few as+} log2 n levels, and forms each sum bit as p … Arithmetic Algorithms, 2nd ed. (A K Peters, 2002), ch. 5

## fact/temp-sensors
35 temperature sensors on the die (34 minion shires + … temperature: a brief | documented | | docs/reports/2026-09-22-et-soc1-spatial-temperature-brief.html headline tiles; [-docs/findings/05-claims.md:331-] {+docs/findings/05-claims.md:350+}

## fact/ts-credit
Credit-counter (FCC) round trip: 140.2 + 14.43 cycles per hop … (200 ns). On-chip communication | measured | three cards | [-docs/findings/05-claims.md:412-] {+docs/findings/05-claims.md:446+}

## fact/ts-e-pair
Messaging energy, 1 KB TensorSend: 0.69 pJ/B between the two … On-chip communication | measured | three cards | manual.json: reruns.rings_pj_per_byte.<pair|neigh|shire|xshire*>; [-docs/energy-manual/05-bytes-between-cores.md:9-] {+docs/energy-manual/05-bytes-between-cores.md:9-17+}

## fact/ts-rt-fln
TensorSend round trip, 32 B register to register inside a … other pair. On-chip communication | measured | three cards | [-docs/findings/05-claims.md:380;-] {+docs/findings/05-claims.md:409;+} docs/reports/2026-09-18-et-soc1-on-chip-communication.html "Inside a shire, only the tree edges are fast"

## fact/ts-rt-mesh
TensorSend round trip between shires, 32 B: 150 + 12.02 … | measured | three cards | lat.json: items[LAT-N2].per_card.<card>.passes[].pingpong_fit, .c32_slope_to5, .c32_slope_beyond5; [-docs/findings/05-claims.md:412-] {+docs/findings/05-claims.md:446+}

## fact/volt.minion
Minion rail: set point 520 mV, 516-518 mV on die … Power and temperature telemetry | measured | aifoundry2, aifoundry3 | [-docs/findings/05-claims.md:26-27, 41;-] {+docs/findings/05-claims.md:34-35, 49;+} docs/research/power-telemetry.md:186-190

## fact/volt.sram
SRAM rail (shire-cache arrays): set point 705 mV, 703-707 mV … (and horace2-, thermal-telemetry.jsonl: 3,681 samples, 20 Sep), fields `reg_mv.sram`, `die_mv.sram`; [-docs/findings/05-claims.md:41-] {+docs/findings/05-claims.md:49+}

## flow/A/0
FLOW 1 · LOAD TO DRAM
Hart 0 of … and on to a memory shire: about 299 cycles, about [-25–28-] {+28+} of them in the DRAM chip.
1
L1 … all.

 Replay
More detail and the sources {+

Hart 0 of minion 0 (neighbourhood 0) in shire 0 loads one 64-byte line that no cache holds. Its physical address picks every stop:

 0x80_1234_5340: L2 bank PA[7:6] = 1 · L3 home PA[10:6] = shire 13 · memory shire PA[8:6] = 5 · channel PA[9] = 1 · DRAM bank PA[12:10] = 4

 Requester shire
0
1
2
3
4
5
6
7
8
9
10
11
12
13
14
15
16
17
18
19
20
21
22
23
24
25
26
27
28
29
30
31
New address
Leg What happens cycles pJ/B
L1 miss (a hit: 5.25) 0.75
L2 bank 1 miss (a hit: 47) 3.1
L3 home, shire 13 4 hops: a hit would be 110 + 12×4 158 15
memory shire 5 4 hops on: + 91 + 12×4 297
LPDDR4X, channel 1 bank 4: about 28 cycles are the DRAM chip (inferred) 115
back to shire 0 back through the L3 home: the model's total; typical, measured: 299 297
Inferred or open here, and what would settle it (1)

 Nearly settled: the way back of a DRAM load (Flow 1, Load -> DRAM)

 The reply's path: the diagram draws it from the memory shire through the L3 home to the requester, each leg y first.

 What settles it, and what is left: The leg order is documented in a manual already in the repo: CORE-ET Shire Cache Specification §3.2.2 'L3 REQ_Read' (pdf p.55): L3 reads that miss go out the to_sys mesh port, the data returns to the L3 as L3_Fill, then the reply goes to the requester, so memory shire -> L3 home -> requester is spec. Each leg's route: a reply goes y first (E56, 29 September, fact L104), so the drawing takes each leg back along its request's links. What is left: E56's streams ran between compute shires' scratchpads, so that a memory shire's and an L3 home's replies follow the same rule is inferred.

 On the hub: rung 32: A link-contention test for the mesh's routing order ↗ · rung 21: The NoC's reference manual and specification ↗

 Measured and explained in Anatomy of a memory access ↗.

 The facts this flow uses (25): point at one for its source

 Path of a cacheable load: an L1 miss sends Read_L2 over ET-Link to the local bank chosen by PA[7:6]; an L2 miss sends Read_L3 over the to_l3 mesh interface to the home shire's L3 slave chosen by PA[10:6] (data returns straight to the neighbourhood, before the fill); an L3 miss goes over to_sys to the memory shire chosen by PA[8:6], whose controller does activate/read/precharge.
documented
Anatomy of a memory access ↗
addr.load-path
Measured load-to-use model from any requesting shire at 600 MHz: L1 5; L2 47-48; L3 110 + 12·hops(requester, home = PA[10:6]); DRAM 110 + 12·hops(requester, home) + 91 + 12·hops(home, memory shire = PA[8:6]). The mesh round trip is paid twice on a DRAM load: to the L3 home, then on to the memory shire.
measured
three cards
Anatomy of a memory access ↗
addr.load-model
Whole DRAM load: latency = 110 + 12·hops(requester → L3 home) + 91 + 12·hops(L3 home → memory shire). Left as fitted, the model is within ±3 cycles for 97% of lines (each line's fastest of three loads) on aifoundry2, 93% on aifoundry3 and 94% on aifoundry1's card 1; on the 19 September fitting run, 83% of single loads were within ±3 cycles (aifoundry2).
measured
three cards
Anatomy of a memory access ↗
L45
L2 address decode: offset PA[5:0], bank PA[7:6], sub-bank PA[9:8], set from PA[10] up (L2 set bits are PA[19:10] on ET-SoC-1).
documented
Anatomy of a memory access ↗
l2.decode
A line's L3 home shire is PA[10:6]: consecutive 64-byte lines rotate over the 32 compute shires' L3 slices (default 'swizzle0'; the firmware leaves the swizzle register at reset).
measured
three cards
Anatomy of a memory access ↗
l3.home
The memory shire serving a line is PA[8:6] (so it is always the L3 home shire's low three bits) and the controller/channel within it is PA[9]: consecutive 64 B lines rotate over the 8 memory shires, the two channels alternate every 512 B.
measured
aifoundry2
Anatomy of a memory access ↗
dram.memshire-select
The memory shire that serves a line is picked by physical-address bits 8:6 and its L3 home shire by bits 10:6, so memory shire m serves the lines of home shires m, m+8, m+16 and m+24. Hardware read counters confirmed the memory-shire bits for 64 of 64 lines (and in all 15 passes of the three-card check).
measured
three cards
Anatomy of a memory access ↗
L43
Inside a channel: bank PA[12:10], column PA[17:13] (plus PA[5:1] within the line), row PA[18] and up (PA[34:18]); 8 banks, 2 KB page, one rank per channel.
measured
aifoundry2
Anatomy of a memory access ↗
dram.row-bits
DRAM address map: PA[9] selects the controller (channel) within the memory shire, PA[12:10] the DRAM bank (8 banks), PA[34:18] the row; the page policy is open-page. Measured on 29 September (E57): another row in the same bank is a row conflict, and a row that also differs in any of PA[6-12] (the memory shire, the controller, the bank) reads as a row hit, 20 cycles faster, on aifoundry1-c1 and aifoundry3 (15 of 15 conditions); on aifoundry3 and aifoundry2 PA[6-9] set the refresh phase and PA[10-13] and PA[18] do not, so each controller refreshes on its own. On aifoundry2, run the same way as a third card, 14 of 15 conditions came out so: two lines that differ only in PA[17], a column bit in this map, read as a row conflict there.
measured
aifoundry3, aifoundry1 card 1
no published page yet
L50
L1 data cache hit: 5.25 cycles load-to-use (8.8 ns at 600 MHz); the same on three cards (per-pass ranges 5.247-5.259).
measured
three cards
Memory hierarchy ↗
lat-l1
L2 cache hit (and the shire's own scratchpad): 47 cycles (78 ns); hart 1 pays 3 more (39 read buffer, 50 L2).
measured
three cards
Memory hierarchy ↗
lat-l2
L3 hit: 110 + 12 cycles per mesh hop between the requesting shire and the line's home shire (fitted 110.5 + 11.99 on three cards); 159-169 cycles (265-282 ns) on average depending on the requesting shire.
measured
three cards
Anatomy of a memory access ↗
l3.latency
Past the L3, the DRAM leg costs 91 + 12 × hops(home shire, memory shire) cycles; about 28 of the 91 are the DRAM chip (activate 11, read latency and two bursts 17) and at most about 63 the L3 home's miss handling and the memory shire. Only about 28 of a ~300-cycle DRAM load are the DRAM's own timing.
measured
three cards
Anatomy of a memory access ↗
dram.leg
A typical DRAM load, timed one at a time: 299 cycles (500 ns), the median of 4,500 loads from shire 0 to random lines; 299 in each of 15 passes on three cards.
measured
three cards
Anatomy of a memory access ↗
lat-dram-typical
DRAM load from a pointer chase: 287-297 cycles at 600 MHz (479-495 ns): 296.6-297.1 from shires 0 and 31, 287.2-288.8 from 7 and 24; about 490 ns, a fifth more than an A100's HBM (405 ns).
measured
three cards
Memory hierarchy ↗
lat-dram
Of the 91-cycle memory-shire constant (152 ns), the DRAM chip accounts for about 28 cycles (activate tRCD 11 cycles = 18 ns, 19.3 ns read latency, the two 4.3 ns bursts of a 64-byte line); the rest, at most ~63 cycles (~105 ns), is the L3 home's miss handling (about 12 cycles by the spec: an L3 miss is 42 shire clocks against 30 for a hit) and the memory shire: controller queue, PHY and the crossings between the 933 MHz DDR clock and the mesh.
model
Anatomy of a memory access ↗
L46
Of a DRAM load's ~300 cycles only about 28 are the DRAM chip's own timing (activate tRCD 18 ns, 19.3 ns read latency, the two 4.3 ns bursts of a 64-byte line); the rest is paths on the chip.
inference
Anatomy of a memory access ↗
lat-dram-chip
L1 hit (memhier loop): 0.75 pJ/B [0.62-0.88] above idle, 1 KB tensor loads (L1: 32 B vector loads) by every minion at 600 MHz; per card a2 0.77, a3 0.75, a1c1 0.72.
measured
three cards
The energy manual ↗
e-l1
L2 cache: 3.11 pJ/B [1.42-4.99] above idle, 1 KB tensor loads (L1: 32 B vector loads) by every minion at 600 MHz; per card a2 2.64, a3 2.83, a1c1 3.86.
measured
three cards
The energy manual ↗
e-l2
L3 (over the mesh): 14.7 pJ/B [7.1-20.5] above idle, 1 KB tensor loads (L1: 32 B vector loads) by every minion at 600 MHz; per card a2 12.3, a3 13.5, a1c1 18.4.
measured
three cards
The energy manual ↗
e-l3
DRAM: 114.6 pJ/B [89.0-141.3] above idle, 1 KB tensor loads (L1: 32 B vector loads) by every minion at 600 MHz; per card a2 111.5, a3 105.6, a1c1 126.6.
measured
three cards
The energy manual ↗
e-dram
Each mesh hop adds 12 cycles round trip at 600 MHz (20 ns): L3 11.99, remote scratchpad 12.00, TensorSend 12.01-12.02 cycles per hop on every card.
measured
three cards
On-chip communication ↗
mesh-hop-lat
The mesh routes in dimension order, and a request and its reply take opposite orders: a request goes x first, then y, and a reply y first, then x, on the logical map, so a reply retraces its request's route backwards. Measured on 29 September (E56) with sets of streams between shires chosen so that their streams share one directed link under one order and none under the other: 1 KB tensor loads, whose data travel as replies, fell to 0.54-0.77 of their bandwidth alone when they shared a link under y first and held at 1.00 when they shared one under x first; tensor stores, whose data travel as requests, showed the mirror (0.52-0.76 against 1.00). A shared link carried about 92 GB/s. The same on aifoundry1 card 1 (development), aifoundry3 (the frozen validation) and aifoundry2 (the same frozen test, run as a third card on the evening of 29 September), three passes each.
measured
three cards
no published page yet
L104
Fitted memory-shire positions on the logical map: memory shires 0-3 one step off the top edge at x = 1-4 (y = -1), 4-7 one step off the bottom edge at x = 1-4 (y = 6). Memory shire 2's position is a tie-break (x = 3 or 5 above the grid, or (6,0), fit equally).
measured
aifoundry2
Anatomy of a memory access ↗
mesh.memshire-positions
An L3 read from another shire enters the home shire's cache through its L3 slave port and moves down the pipeline as L3_Read and L3_Fill: a miss goes out the to_sys mesh port to memory, the data comes back as the L3 fill, and the home answers the requester. The order memory shire, L3 home, requester is the specification's; which way each leg turns on the mesh is not documented.
documented
no published page yet
sc.l3-miss+}

## flow/A/1
FLOW 1 · LOAD TO DRAM
Hart 0 of … and on to a memory shire: about 299 cycles, about [-25–28-] {+28+} of them in the DRAM chip.
1
L1 … all.

 Replay
More detail and the sources {+

Hart 0 of minion 0 (neighbourhood 0) in shire 0 loads one 64-byte line that no cache holds. Its physical address picks every stop:

 0x80_1234_5340: L2 bank PA[7:6] = 1 · L3 home PA[10:6] = shire 13 · memory shire PA[8:6] = 5 · channel PA[9] = 1 · DRAM bank PA[12:10] = 4

 Requester shire
0
1
2
3
4
5
6
7
8
9
10
11
12
13
14
15
16
17
18
19
20
21
22
23
24
25
26
27
28
29
30
31
New address
Leg What happens cycles pJ/B
L1 miss (a hit: 5.25) 0.75
L2 bank 1 miss (a hit: 47) 3.1
L3 home, shire 13 4 hops: a hit would be 110 + 12×4 158 15
memory shire 5 4 hops on: + 91 + 12×4 297
LPDDR4X, channel 1 bank 4: about 28 cycles are the DRAM chip (inferred) 115
back to shire 0 back through the L3 home: the model's total; typical, measured: 299 297
Inferred or open here, and what would settle it (1)

 Nearly settled: the way back of a DRAM load (Flow 1, Load -> DRAM)

 The reply's path: the diagram draws it from the memory shire through the L3 home to the requester, each leg y first.

 What settles it, and what is left: The leg order is documented in a manual already in the repo: CORE-ET Shire Cache Specification §3.2.2 'L3 REQ_Read' (pdf p.55): L3 reads that miss go out the to_sys mesh port, the data returns to the L3 as L3_Fill, then the reply goes to the requester, so memory shire -> L3 home -> requester is spec. Each leg's route: a reply goes y first (E56, 29 September, fact L104), so the drawing takes each leg back along its request's links. What is left: E56's streams ran between compute shires' scratchpads, so that a memory shire's and an L3 home's replies follow the same rule is inferred.

 On the hub: rung 32: A link-contention test for the mesh's routing order ↗ · rung 21: The NoC's reference manual and specification ↗

 Measured and explained in Anatomy of a memory access ↗.

 The facts this flow uses (25): point at one for its source

 Path of a cacheable load: an L1 miss sends Read_L2 over ET-Link to the local bank chosen by PA[7:6]; an L2 miss sends Read_L3 over the to_l3 mesh interface to the home shire's L3 slave chosen by PA[10:6] (data returns straight to the neighbourhood, before the fill); an L3 miss goes over to_sys to the memory shire chosen by PA[8:6], whose controller does activate/read/precharge.
documented
Anatomy of a memory access ↗
addr.load-path
Measured load-to-use model from any requesting shire at 600 MHz: L1 5; L2 47-48; L3 110 + 12·hops(requester, home = PA[10:6]); DRAM 110 + 12·hops(requester, home) + 91 + 12·hops(home, memory shire = PA[8:6]). The mesh round trip is paid twice on a DRAM load: to the L3 home, then on to the memory shire.
measured
three cards
Anatomy of a memory access ↗
addr.load-model
Whole DRAM load: latency = 110 + 12·hops(requester → L3 home) + 91 + 12·hops(L3 home → memory shire). Left as fitted, the model is within ±3 cycles for 97% of lines (each line's fastest of three loads) on aifoundry2, 93% on aifoundry3 and 94% on aifoundry1's card 1; on the 19 September fitting run, 83% of single loads were within ±3 cycles (aifoundry2).
measured
three cards
Anatomy of a memory access ↗
L45
L2 address decode: offset PA[5:0], bank PA[7:6], sub-bank PA[9:8], set from PA[10] up (L2 set bits are PA[19:10] on ET-SoC-1).
documented
Anatomy of a memory access ↗
l2.decode
A line's L3 home shire is PA[10:6]: consecutive 64-byte lines rotate over the 32 compute shires' L3 slices (default 'swizzle0'; the firmware leaves the swizzle register at reset).
measured
three cards
Anatomy of a memory access ↗
l3.home
The memory shire serving a line is PA[8:6] (so it is always the L3 home shire's low three bits) and the controller/channel within it is PA[9]: consecutive 64 B lines rotate over the 8 memory shires, the two channels alternate every 512 B.
measured
aifoundry2
Anatomy of a memory access ↗
dram.memshire-select
The memory shire that serves a line is picked by physical-address bits 8:6 and its L3 home shire by bits 10:6, so memory shire m serves the lines of home shires m, m+8, m+16 and m+24. Hardware read counters confirmed the memory-shire bits for 64 of 64 lines (and in all 15 passes of the three-card check).
measured
three cards
Anatomy of a memory access ↗
L43
Inside a channel: bank PA[12:10], column PA[17:13] (plus PA[5:1] within the line), row PA[18] and up (PA[34:18]); 8 banks, 2 KB page, one rank per channel.
measured
aifoundry2
Anatomy of a memory access ↗
dram.row-bits
DRAM address map: PA[9] selects the controller (channel) within the memory shire, PA[12:10] the DRAM bank (8 banks), PA[34:18] the row; the page policy is open-page. Measured on 29 September (E57): another row in the same bank is a row conflict, and a row that also differs in any of PA[6-12] (the memory shire, the controller, the bank) reads as a row hit, 20 cycles faster, on aifoundry1-c1 and aifoundry3 (15 of 15 conditions); on aifoundry3 and aifoundry2 PA[6-9] set the refresh phase and PA[10-13] and PA[18] do not, so each controller refreshes on its own. On aifoundry2, run the same way as a third card, 14 of 15 conditions came out so: two lines that differ only in PA[17], a column bit in this map, read as a row conflict there.
measured
aifoundry3, aifoundry1 card 1
no published page yet
L50
L1 data cache hit: 5.25 cycles load-to-use (8.8 ns at 600 MHz); the same on three cards (per-pass ranges 5.247-5.259).
measured
three cards
Memory hierarchy ↗
lat-l1
L2 cache hit (and the shire's own scratchpad): 47 cycles (78 ns); hart 1 pays 3 more (39 read buffer, 50 L2).
measured
three cards
Memory hierarchy ↗
lat-l2
L3 hit: 110 + 12 cycles per mesh hop between the requesting shire and the line's home shire (fitted 110.5 + 11.99 on three cards); 159-169 cycles (265-282 ns) on average depending on the requesting shire.
measured
three cards
Anatomy of a memory access ↗
l3.latency
Past the L3, the DRAM leg costs 91 + 12 × hops(home shire, memory shire) cycles; about 28 of the 91 are the DRAM chip (activate 11, read latency and two bursts 17) and at most about 63 the L3 home's miss handling and the memory shire. Only about 28 of a ~300-cycle DRAM load are the DRAM's own timing.
measured
three cards
Anatomy of a memory access ↗
dram.leg
A typical DRAM load, timed one at a time: 299 cycles (500 ns), the median of 4,500 loads from shire 0 to random lines; 299 in each of 15 passes on three cards.
measured
three cards
Anatomy of a memory access ↗
lat-dram-typical
DRAM load from a pointer chase: 287-297 cycles at 600 MHz (479-495 ns): 296.6-297.1 from shires 0 and 31, 287.2-288.8 from 7 and 24; about 490 ns, a fifth more than an A100's HBM (405 ns).
measured
three cards
Memory hierarchy ↗
lat-dram
Of the 91-cycle memory-shire constant (152 ns), the DRAM chip accounts for about 28 cycles (activate tRCD 11 cycles = 18 ns, 19.3 ns read latency, the two 4.3 ns bursts of a 64-byte line); the rest, at most ~63 cycles (~105 ns), is the L3 home's miss handling (about 12 cycles by the spec: an L3 miss is 42 shire clocks against 30 for a hit) and the memory shire: controller queue, PHY and the crossings between the 933 MHz DDR clock and the mesh.
model
Anatomy of a memory access ↗
L46
Of a DRAM load's ~300 cycles only about 28 are the DRAM chip's own timing (activate tRCD 18 ns, 19.3 ns read latency, the two 4.3 ns bursts of a 64-byte line); the rest is paths on the chip.
inference
Anatomy of a memory access ↗
lat-dram-chip
L1 hit (memhier loop): 0.75 pJ/B [0.62-0.88] above idle, 1 KB tensor loads (L1: 32 B vector loads) by every minion at 600 MHz; per card a2 0.77, a3 0.75, a1c1 0.72.
measured
three cards
The energy manual ↗
e-l1
L2 cache: 3.11 pJ/B [1.42-4.99] above idle, 1 KB tensor loads (L1: 32 B vector loads) by every minion at 600 MHz; per card a2 2.64, a3 2.83, a1c1 3.86.
measured
three cards
The energy manual ↗
e-l2
L3 (over the mesh): 14.7 pJ/B [7.1-20.5] above idle, 1 KB tensor loads (L1: 32 B vector loads) by every minion at 600 MHz; per card a2 12.3, a3 13.5, a1c1 18.4.
measured
three cards
The energy manual ↗
e-l3
DRAM: 114.6 pJ/B [89.0-141.3] above idle, 1 KB tensor loads (L1: 32 B vector loads) by every minion at 600 MHz; per card a2 111.5, a3 105.6, a1c1 126.6.
measured
three cards
The energy manual ↗
e-dram
Each mesh hop adds 12 cycles round trip at 600 MHz (20 ns): L3 11.99, remote scratchpad 12.00, TensorSend 12.01-12.02 cycles per hop on every card.
measured
three cards
On-chip communication ↗
mesh-hop-lat
The mesh routes in dimension order, and a request and its reply take opposite orders: a request goes x first, then y, and a reply y first, then x, on the logical map, so a reply retraces its request's route backwards. Measured on 29 September (E56) with sets of streams between shires chosen so that their streams share one directed link under one order and none under the other: 1 KB tensor loads, whose data travel as replies, fell to 0.54-0.77 of their bandwidth alone when they shared a link under y first and held at 1.00 when they shared one under x first; tensor stores, whose data travel as requests, showed the mirror (0.52-0.76 against 1.00). A shared link carried about 92 GB/s. The same on aifoundry1 card 1 (development), aifoundry3 (the frozen validation) and aifoundry2 (the same frozen test, run as a third card on the evening of 29 September), three passes each.
measured
three cards
no published page yet
L104
Fitted memory-shire positions on the logical map: memory shires 0-3 one step off the top edge at x = 1-4 (y = -1), 4-7 one step off the bottom edge at x = 1-4 (y = 6). Memory shire 2's position is a tie-break (x = 3 or 5 above the grid, or (6,0), fit equally).
measured
aifoundry2
Anatomy of a memory access ↗
mesh.memshire-positions
An L3 read from another shire enters the home shire's cache through its L3 slave port and moves down the pipeline as L3_Read and L3_Fill: a miss goes out the to_sys mesh port to memory, the data comes back as the L3 fill, and the home answers the requester. The order memory shire, L3 home, requester is the specification's; which way each leg turns on the mesh is not documented.
documented
no published page yet
sc.l3-miss+}

## flow/A/2
FLOW 1 · LOAD TO DRAM
Over ET-Link to … and on to a memory shire: about 299 cycles, about [-25–28-] {+28+} of them in the DRAM chip.
1
L1 … all.

 Replay
More detail and the sources {+

Hart 0 of minion 0 (neighbourhood 0) in shire 0 loads one 64-byte line that no cache holds. Its physical address picks every stop:

 0x80_1234_5340: L2 bank PA[7:6] = 1 · L3 home PA[10:6] = shire 13 · memory shire PA[8:6] = 5 · channel PA[9] = 1 · DRAM bank PA[12:10] = 4

 Requester shire
0
1
2
3
4
5
6
7
8
9
10
11
12
13
14
15
16
17
18
19
20
21
22
23
24
25
26
27
28
29
30
31
New address
Leg What happens cycles pJ/B
L1 miss (a hit: 5.25) 0.75
L2 bank 1 miss (a hit: 47) 3.1
L3 home, shire 13 4 hops: a hit would be 110 + 12×4 158 15
memory shire 5 4 hops on: + 91 + 12×4 297
LPDDR4X, channel 1 bank 4: about 28 cycles are the DRAM chip (inferred) 115
back to shire 0 back through the L3 home: the model's total; typical, measured: 299 297
Inferred or open here, and what would settle it (1)

 Nearly settled: the way back of a DRAM load (Flow 1, Load -> DRAM)

 The reply's path: the diagram draws it from the memory shire through the L3 home to the requester, each leg y first.

 What settles it, and what is left: The leg order is documented in a manual already in the repo: CORE-ET Shire Cache Specification §3.2.2 'L3 REQ_Read' (pdf p.55): L3 reads that miss go out the to_sys mesh port, the data returns to the L3 as L3_Fill, then the reply goes to the requester, so memory shire -> L3 home -> requester is spec. Each leg's route: a reply goes y first (E56, 29 September, fact L104), so the drawing takes each leg back along its request's links. What is left: E56's streams ran between compute shires' scratchpads, so that a memory shire's and an L3 home's replies follow the same rule is inferred.

 On the hub: rung 32: A link-contention test for the mesh's routing order ↗ · rung 21: The NoC's reference manual and specification ↗

 Measured and explained in Anatomy of a memory access ↗.

 The facts this flow uses (25): point at one for its source

 Path of a cacheable load: an L1 miss sends Read_L2 over ET-Link to the local bank chosen by PA[7:6]; an L2 miss sends Read_L3 over the to_l3 mesh interface to the home shire's L3 slave chosen by PA[10:6] (data returns straight to the neighbourhood, before the fill); an L3 miss goes over to_sys to the memory shire chosen by PA[8:6], whose controller does activate/read/precharge.
documented
Anatomy of a memory access ↗
addr.load-path
Measured load-to-use model from any requesting shire at 600 MHz: L1 5; L2 47-48; L3 110 + 12·hops(requester, home = PA[10:6]); DRAM 110 + 12·hops(requester, home) + 91 + 12·hops(home, memory shire = PA[8:6]). The mesh round trip is paid twice on a DRAM load: to the L3 home, then on to the memory shire.
measured
three cards
Anatomy of a memory access ↗
addr.load-model
Whole DRAM load: latency = 110 + 12·hops(requester → L3 home) + 91 + 12·hops(L3 home → memory shire). Left as fitted, the model is within ±3 cycles for 97% of lines (each line's fastest of three loads) on aifoundry2, 93% on aifoundry3 and 94% on aifoundry1's card 1; on the 19 September fitting run, 83% of single loads were within ±3 cycles (aifoundry2).
measured
three cards
Anatomy of a memory access ↗
L45
L2 address decode: offset PA[5:0], bank PA[7:6], sub-bank PA[9:8], set from PA[10] up (L2 set bits are PA[19:10] on ET-SoC-1).
documented
Anatomy of a memory access ↗
l2.decode
A line's L3 home shire is PA[10:6]: consecutive 64-byte lines rotate over the 32 compute shires' L3 slices (default 'swizzle0'; the firmware leaves the swizzle register at reset).
measured
three cards
Anatomy of a memory access ↗
l3.home
The memory shire serving a line is PA[8:6] (so it is always the L3 home shire's low three bits) and the controller/channel within it is PA[9]: consecutive 64 B lines rotate over the 8 memory shires, the two channels alternate every 512 B.
measured
aifoundry2
Anatomy of a memory access ↗
dram.memshire-select
The memory shire that serves a line is picked by physical-address bits 8:6 and its L3 home shire by bits 10:6, so memory shire m serves the lines of home shires m, m+8, m+16 and m+24. Hardware read counters confirmed the memory-shire bits for 64 of 64 lines (and in all 15 passes of the three-card check).
measured
three cards
Anatomy of a memory access ↗
L43
Inside a channel: bank PA[12:10], column PA[17:13] (plus PA[5:1] within the line), row PA[18] and up (PA[34:18]); 8 banks, 2 KB page, one rank per channel.
measured
aifoundry2
Anatomy of a memory access ↗
dram.row-bits
DRAM address map: PA[9] selects the controller (channel) within the memory shire, PA[12:10] the DRAM bank (8 banks), PA[34:18] the row; the page policy is open-page. Measured on 29 September (E57): another row in the same bank is a row conflict, and a row that also differs in any of PA[6-12] (the memory shire, the controller, the bank) reads as a row hit, 20 cycles faster, on aifoundry1-c1 and aifoundry3 (15 of 15 conditions); on aifoundry3 and aifoundry2 PA[6-9] set the refresh phase and PA[10-13] and PA[18] do not, so each controller refreshes on its own. On aifoundry2, run the same way as a third card, 14 of 15 conditions came out so: two lines that differ only in PA[17], a column bit in this map, read as a row conflict there.
measured
aifoundry3, aifoundry1 card 1
no published page yet
L50
L1 data cache hit: 5.25 cycles load-to-use (8.8 ns at 600 MHz); the same on three cards (per-pass ranges 5.247-5.259).
measured
three cards
Memory hierarchy ↗
lat-l1
L2 cache hit (and the shire's own scratchpad): 47 cycles (78 ns); hart 1 pays 3 more (39 read buffer, 50 L2).
measured
three cards
Memory hierarchy ↗
lat-l2
L3 hit: 110 + 12 cycles per mesh hop between the requesting shire and the line's home shire (fitted 110.5 + 11.99 on three cards); 159-169 cycles (265-282 ns) on average depending on the requesting shire.
measured
three cards
Anatomy of a memory access ↗
l3.latency
Past the L3, the DRAM leg costs 91 + 12 × hops(home shire, memory shire) cycles; about 28 of the 91 are the DRAM chip (activate 11, read latency and two bursts 17) and at most about 63 the L3 home's miss handling and the memory shire. Only about 28 of a ~300-cycle DRAM load are the DRAM's own timing.
measured
three cards
Anatomy of a memory access ↗
dram.leg
A typical DRAM load, timed one at a time: 299 cycles (500 ns), the median of 4,500 loads from shire 0 to random lines; 299 in each of 15 passes on three cards.
measured
three cards
Anatomy of a memory access ↗
lat-dram-typical
DRAM load from a pointer chase: 287-297 cycles at 600 MHz (479-495 ns): 296.6-297.1 from shires 0 and 31, 287.2-288.8 from 7 and 24; about 490 ns, a fifth more than an A100's HBM (405 ns).
measured
three cards
Memory hierarchy ↗
lat-dram
Of the 91-cycle memory-shire constant (152 ns), the DRAM chip accounts for about 28 cycles (activate tRCD 11 cycles = 18 ns, 19.3 ns read latency, the two 4.3 ns bursts of a 64-byte line); the rest, at most ~63 cycles (~105 ns), is the L3 home's miss handling (about 12 cycles by the spec: an L3 miss is 42 shire clocks against 30 for a hit) and the memory shire: controller queue, PHY and the crossings between the 933 MHz DDR clock and the mesh.
model
Anatomy of a memory access ↗
L46
Of a DRAM load's ~300 cycles only about 28 are the DRAM chip's own timing (activate tRCD 18 ns, 19.3 ns read latency, the two 4.3 ns bursts of a 64-byte line); the rest is paths on the chip.
inference
Anatomy of a memory access ↗
lat-dram-chip
L1 hit (memhier loop): 0.75 pJ/B [0.62-0.88] above idle, 1 KB tensor loads (L1: 32 B vector loads) by every minion at 600 MHz; per card a2 0.77, a3 0.75, a1c1 0.72.
measured
three cards
The energy manual ↗
e-l1
L2 cache: 3.11 pJ/B [1.42-4.99] above idle, 1 KB tensor loads (L1: 32 B vector loads) by every minion at 600 MHz; per card a2 2.64, a3 2.83, a1c1 3.86.
measured
three cards
The energy manual ↗
e-l2
L3 (over the mesh): 14.7 pJ/B [7.1-20.5] above idle, 1 KB tensor loads (L1: 32 B vector loads) by every minion at 600 MHz; per card a2 12.3, a3 13.5, a1c1 18.4.
measured
three cards
The energy manual ↗
e-l3
DRAM: 114.6 pJ/B [89.0-141.3] above idle, 1 KB tensor loads (L1: 32 B vector loads) by every minion at 600 MHz; per card a2 111.5, a3 105.6, a1c1 126.6.
measured
three cards
The energy manual ↗
e-dram
Each mesh hop adds 12 cycles round trip at 600 MHz (20 ns): L3 11.99, remote scratchpad 12.00, TensorSend 12.01-12.02 cycles per hop on every card.
measured
three cards
On-chip communication ↗
mesh-hop-lat
The mesh routes in dimension order, and a request and its reply take opposite orders: a request goes x first, then y, and a reply y first, then x, on the logical map, so a reply retraces its request's route backwards. Measured on 29 September (E56) with sets of streams between shires chosen so that their streams share one directed link under one order and none under the other: 1 KB tensor loads, whose data travel as replies, fell to 0.54-0.77 of their bandwidth alone when they shared a link under y first and held at 1.00 when they shared one under x first; tensor stores, whose data travel as requests, showed the mirror (0.52-0.76 against 1.00). A shared link carried about 92 GB/s. The same on aifoundry1 card 1 (development), aifoundry3 (the frozen validation) and aifoundry2 (the same frozen test, run as a third card on the evening of 29 September), three passes each.
measured
three cards
no published page yet
L104
Fitted memory-shire positions on the logical map: memory shires 0-3 one step off the top edge at x = 1-4 (y = -1), 4-7 one step off the bottom edge at x = 1-4 (y = 6). Memory shire 2's position is a tie-break (x = 3 or 5 above the grid, or (6,0), fit equally).
measured
aifoundry2
Anatomy of a memory access ↗
mesh.memshire-positions
An L3 read from another shire enters the home shire's cache through its L3 slave port and moves down the pipeline as L3_Read and L3_Fill: a miss goes out the to_sys mesh port to memory, the data comes back as the L3 fill, and the home answers the requester. The order memory shire, L3 home, requester is the specification's; which way each leg turns on the mesh is not documented.
documented
no published page yet
sc.l3-miss+}

## flow/A/3
FLOW 1 · LOAD TO DRAM
Over the mesh … and on to a memory shire: about 299 cycles, about [-25–28-] {+28+} of them in the DRAM chip.
1
L1 … all.

 Replay
More detail and the sources {+

Hart 0 of minion 0 (neighbourhood 0) in shire 0 loads one 64-byte line that no cache holds. Its physical address picks every stop:

 0x80_1234_5340: L2 bank PA[7:6] = 1 · L3 home PA[10:6] = shire 13 · memory shire PA[8:6] = 5 · channel PA[9] = 1 · DRAM bank PA[12:10] = 4

 Requester shire
0
1
2
3
4
5
6
7
8
9
10
11
12
13
14
15
16
17
18
19
20
21
22
23
24
25
26
27
28
29
30
31
New address
Leg What happens cycles pJ/B
L1 miss (a hit: 5.25) 0.75
L2 bank 1 miss (a hit: 47) 3.1
L3 home, shire 13 4 hops: a hit would be 110 + 12×4 158 15
memory shire 5 4 hops on: + 91 + 12×4 297
LPDDR4X, channel 1 bank 4: about 28 cycles are the DRAM chip (inferred) 115
back to shire 0 back through the L3 home: the model's total; typical, measured: 299 297
Inferred or open here, and what would settle it (1)

 Nearly settled: the way back of a DRAM load (Flow 1, Load -> DRAM)

 The reply's path: the diagram draws it from the memory shire through the L3 home to the requester, each leg y first.

 What settles it, and what is left: The leg order is documented in a manual already in the repo: CORE-ET Shire Cache Specification §3.2.2 'L3 REQ_Read' (pdf p.55): L3 reads that miss go out the to_sys mesh port, the data returns to the L3 as L3_Fill, then the reply goes to the requester, so memory shire -> L3 home -> requester is spec. Each leg's route: a reply goes y first (E56, 29 September, fact L104), so the drawing takes each leg back along its request's links. What is left: E56's streams ran between compute shires' scratchpads, so that a memory shire's and an L3 home's replies follow the same rule is inferred.

 On the hub: rung 32: A link-contention test for the mesh's routing order ↗ · rung 21: The NoC's reference manual and specification ↗

 Measured and explained in Anatomy of a memory access ↗.

 The facts this flow uses (25): point at one for its source

 Path of a cacheable load: an L1 miss sends Read_L2 over ET-Link to the local bank chosen by PA[7:6]; an L2 miss sends Read_L3 over the to_l3 mesh interface to the home shire's L3 slave chosen by PA[10:6] (data returns straight to the neighbourhood, before the fill); an L3 miss goes over to_sys to the memory shire chosen by PA[8:6], whose controller does activate/read/precharge.
documented
Anatomy of a memory access ↗
addr.load-path
Measured load-to-use model from any requesting shire at 600 MHz: L1 5; L2 47-48; L3 110 + 12·hops(requester, home = PA[10:6]); DRAM 110 + 12·hops(requester, home) + 91 + 12·hops(home, memory shire = PA[8:6]). The mesh round trip is paid twice on a DRAM load: to the L3 home, then on to the memory shire.
measured
three cards
Anatomy of a memory access ↗
addr.load-model
Whole DRAM load: latency = 110 + 12·hops(requester → L3 home) + 91 + 12·hops(L3 home → memory shire). Left as fitted, the model is within ±3 cycles for 97% of lines (each line's fastest of three loads) on aifoundry2, 93% on aifoundry3 and 94% on aifoundry1's card 1; on the 19 September fitting run, 83% of single loads were within ±3 cycles (aifoundry2).
measured
three cards
Anatomy of a memory access ↗
L45
L2 address decode: offset PA[5:0], bank PA[7:6], sub-bank PA[9:8], set from PA[10] up (L2 set bits are PA[19:10] on ET-SoC-1).
documented
Anatomy of a memory access ↗
l2.decode
A line's L3 home shire is PA[10:6]: consecutive 64-byte lines rotate over the 32 compute shires' L3 slices (default 'swizzle0'; the firmware leaves the swizzle register at reset).
measured
three cards
Anatomy of a memory access ↗
l3.home
The memory shire serving a line is PA[8:6] (so it is always the L3 home shire's low three bits) and the controller/channel within it is PA[9]: consecutive 64 B lines rotate over the 8 memory shires, the two channels alternate every 512 B.
measured
aifoundry2
Anatomy of a memory access ↗
dram.memshire-select
The memory shire that serves a line is picked by physical-address bits 8:6 and its L3 home shire by bits 10:6, so memory shire m serves the lines of home shires m, m+8, m+16 and m+24. Hardware read counters confirmed the memory-shire bits for 64 of 64 lines (and in all 15 passes of the three-card check).
measured
three cards
Anatomy of a memory access ↗
L43
Inside a channel: bank PA[12:10], column PA[17:13] (plus PA[5:1] within the line), row PA[18] and up (PA[34:18]); 8 banks, 2 KB page, one rank per channel.
measured
aifoundry2
Anatomy of a memory access ↗
dram.row-bits
DRAM address map: PA[9] selects the controller (channel) within the memory shire, PA[12:10] the DRAM bank (8 banks), PA[34:18] the row; the page policy is open-page. Measured on 29 September (E57): another row in the same bank is a row conflict, and a row that also differs in any of PA[6-12] (the memory shire, the controller, the bank) reads as a row hit, 20 cycles faster, on aifoundry1-c1 and aifoundry3 (15 of 15 conditions); on aifoundry3 and aifoundry2 PA[6-9] set the refresh phase and PA[10-13] and PA[18] do not, so each controller refreshes on its own. On aifoundry2, run the same way as a third card, 14 of 15 conditions came out so: two lines that differ only in PA[17], a column bit in this map, read as a row conflict there.
measured
aifoundry3, aifoundry1 card 1
no published page yet
L50
L1 data cache hit: 5.25 cycles load-to-use (8.8 ns at 600 MHz); the same on three cards (per-pass ranges 5.247-5.259).
measured
three cards
Memory hierarchy ↗
lat-l1
L2 cache hit (and the shire's own scratchpad): 47 cycles (78 ns); hart 1 pays 3 more (39 read buffer, 50 L2).
measured
three cards
Memory hierarchy ↗
lat-l2
L3 hit: 110 + 12 cycles per mesh hop between the requesting shire and the line's home shire (fitted 110.5 + 11.99 on three cards); 159-169 cycles (265-282 ns) on average depending on the requesting shire.
measured
three cards
Anatomy of a memory access ↗
l3.latency
Past the L3, the DRAM leg costs 91 + 12 × hops(home shire, memory shire) cycles; about 28 of the 91 are the DRAM chip (activate 11, read latency and two bursts 17) and at most about 63 the L3 home's miss handling and the memory shire. Only about 28 of a ~300-cycle DRAM load are the DRAM's own timing.
measured
three cards
Anatomy of a memory access ↗
dram.leg
A typical DRAM load, timed one at a time: 299 cycles (500 ns), the median of 4,500 loads from shire 0 to random lines; 299 in each of 15 passes on three cards.
measured
three cards
Anatomy of a memory access ↗
lat-dram-typical
DRAM load from a pointer chase: 287-297 cycles at 600 MHz (479-495 ns): 296.6-297.1 from shires 0 and 31, 287.2-288.8 from 7 and 24; about 490 ns, a fifth more than an A100's HBM (405 ns).
measured
three cards
Memory hierarchy ↗
lat-dram
Of the 91-cycle memory-shire constant (152 ns), the DRAM chip accounts for about 28 cycles (activate tRCD 11 cycles = 18 ns, 19.3 ns read latency, the two 4.3 ns bursts of a 64-byte line); the rest, at most ~63 cycles (~105 ns), is the L3 home's miss handling (about 12 cycles by the spec: an L3 miss is 42 shire clocks against 30 for a hit) and the memory shire: controller queue, PHY and the crossings between the 933 MHz DDR clock and the mesh.
model
Anatomy of a memory access ↗
L46
Of a DRAM load's ~300 cycles only about 28 are the DRAM chip's own timing (activate tRCD 18 ns, 19.3 ns read latency, the two 4.3 ns bursts of a 64-byte line); the rest is paths on the chip.
inference
Anatomy of a memory access ↗
lat-dram-chip
L1 hit (memhier loop): 0.75 pJ/B [0.62-0.88] above idle, 1 KB tensor loads (L1: 32 B vector loads) by every minion at 600 MHz; per card a2 0.77, a3 0.75, a1c1 0.72.
measured
three cards
The energy manual ↗
e-l1
L2 cache: 3.11 pJ/B [1.42-4.99] above idle, 1 KB tensor loads (L1: 32 B vector loads) by every minion at 600 MHz; per card a2 2.64, a3 2.83, a1c1 3.86.
measured
three cards
The energy manual ↗
e-l2
L3 (over the mesh): 14.7 pJ/B [7.1-20.5] above idle, 1 KB tensor loads (L1: 32 B vector loads) by every minion at 600 MHz; per card a2 12.3, a3 13.5, a1c1 18.4.
measured
three cards
The energy manual ↗
e-l3
DRAM: 114.6 pJ/B [89.0-141.3] above idle, 1 KB tensor loads (L1: 32 B vector loads) by every minion at 600 MHz; per card a2 111.5, a3 105.6, a1c1 126.6.
measured
three cards
The energy manual ↗
e-dram
Each mesh hop adds 12 cycles round trip at 600 MHz (20 ns): L3 11.99, remote scratchpad 12.00, TensorSend 12.01-12.02 cycles per hop on every card.
measured
three cards
On-chip communication ↗
mesh-hop-lat
The mesh routes in dimension order, and a request and its reply take opposite orders: a request goes x first, then y, and a reply y first, then x, on the logical map, so a reply retraces its request's route backwards. Measured on 29 September (E56) with sets of streams between shires chosen so that their streams share one directed link under one order and none under the other: 1 KB tensor loads, whose data travel as replies, fell to 0.54-0.77 of their bandwidth alone when they shared a link under y first and held at 1.00 when they shared one under x first; tensor stores, whose data travel as requests, showed the mirror (0.52-0.76 against 1.00). A shared link carried about 92 GB/s. The same on aifoundry1 card 1 (development), aifoundry3 (the frozen validation) and aifoundry2 (the same frozen test, run as a third card on the evening of 29 September), three passes each.
measured
three cards
no published page yet
L104
Fitted memory-shire positions on the logical map: memory shires 0-3 one step off the top edge at x = 1-4 (y = -1), 4-7 one step off the bottom edge at x = 1-4 (y = 6). Memory shire 2's position is a tie-break (x = 3 or 5 above the grid, or (6,0), fit equally).
measured
aifoundry2
Anatomy of a memory access ↗
mesh.memshire-positions
An L3 read from another shire enters the home shire's cache through its L3 slave port and moves down the pipeline as L3_Read and L3_Fill: a miss goes out the to_sys mesh port to memory, the data comes back as the L3 fill, and the home answers the requester. The order memory shire, L3 home, requester is the specification's; which way each leg turns on the mesh is not documented.
documented
no published page yet
sc.l3-miss+}

## flow/A/4
FLOW 1 · LOAD TO DRAM
On to memory … and on to a memory shire: about 299 cycles, about [-25–28-] {+28+} of them in the DRAM chip.
1
L1 … all.

 Replay
More detail and the sources {+

Hart 0 of minion 0 (neighbourhood 0) in shire 0 loads one 64-byte line that no cache holds. Its physical address picks every stop:

 0x80_1234_5340: L2 bank PA[7:6] = 1 · L3 home PA[10:6] = shire 13 · memory shire PA[8:6] = 5 · channel PA[9] = 1 · DRAM bank PA[12:10] = 4

 Requester shire
0
1
2
3
4
5
6
7
8
9
10
11
12
13
14
15
16
17
18
19
20
21
22
23
24
25
26
27
28
29
30
31
New address
Leg What happens cycles pJ/B
L1 miss (a hit: 5.25) 0.75
L2 bank 1 miss (a hit: 47) 3.1
L3 home, shire 13 4 hops: a hit would be 110 + 12×4 158 15
memory shire 5 4 hops on: + 91 + 12×4 297
LPDDR4X, channel 1 bank 4: about 28 cycles are the DRAM chip (inferred) 115
back to shire 0 back through the L3 home: the model's total; typical, measured: 299 297
Inferred or open here, and what would settle it (1)

 Nearly settled: the way back of a DRAM load (Flow 1, Load -> DRAM)

 The reply's path: the diagram draws it from the memory shire through the L3 home to the requester, each leg y first.

 What settles it, and what is left: The leg order is documented in a manual already in the repo: CORE-ET Shire Cache Specification §3.2.2 'L3 REQ_Read' (pdf p.55): L3 reads that miss go out the to_sys mesh port, the data returns to the L3 as L3_Fill, then the reply goes to the requester, so memory shire -> L3 home -> requester is spec. Each leg's route: a reply goes y first (E56, 29 September, fact L104), so the drawing takes each leg back along its request's links. What is left: E56's streams ran between compute shires' scratchpads, so that a memory shire's and an L3 home's replies follow the same rule is inferred.

 On the hub: rung 32: A link-contention test for the mesh's routing order ↗ · rung 21: The NoC's reference manual and specification ↗

 Measured and explained in Anatomy of a memory access ↗.

 The facts this flow uses (25): point at one for its source

 Path of a cacheable load: an L1 miss sends Read_L2 over ET-Link to the local bank chosen by PA[7:6]; an L2 miss sends Read_L3 over the to_l3 mesh interface to the home shire's L3 slave chosen by PA[10:6] (data returns straight to the neighbourhood, before the fill); an L3 miss goes over to_sys to the memory shire chosen by PA[8:6], whose controller does activate/read/precharge.
documented
Anatomy of a memory access ↗
addr.load-path
Measured load-to-use model from any requesting shire at 600 MHz: L1 5; L2 47-48; L3 110 + 12·hops(requester, home = PA[10:6]); DRAM 110 + 12·hops(requester, home) + 91 + 12·hops(home, memory shire = PA[8:6]). The mesh round trip is paid twice on a DRAM load: to the L3 home, then on to the memory shire.
measured
three cards
Anatomy of a memory access ↗
addr.load-model
Whole DRAM load: latency = 110 + 12·hops(requester → L3 home) + 91 + 12·hops(L3 home → memory shire). Left as fitted, the model is within ±3 cycles for 97% of lines (each line's fastest of three loads) on aifoundry2, 93% on aifoundry3 and 94% on aifoundry1's card 1; on the 19 September fitting run, 83% of single loads were within ±3 cycles (aifoundry2).
measured
three cards
Anatomy of a memory access ↗
L45
L2 address decode: offset PA[5:0], bank PA[7:6], sub-bank PA[9:8], set from PA[10] up (L2 set bits are PA[19:10] on ET-SoC-1).
documented
Anatomy of a memory access ↗
l2.decode
A line's L3 home shire is PA[10:6]: consecutive 64-byte lines rotate over the 32 compute shires' L3 slices (default 'swizzle0'; the firmware leaves the swizzle register at reset).
measured
three cards
Anatomy of a memory access ↗
l3.home
The memory shire serving a line is PA[8:6] (so it is always the L3 home shire's low three bits) and the controller/channel within it is PA[9]: consecutive 64 B lines rotate over the 8 memory shires, the two channels alternate every 512 B.
measured
aifoundry2
Anatomy of a memory access ↗
dram.memshire-select
The memory shire that serves a line is picked by physical-address bits 8:6 and its L3 home shire by bits 10:6, so memory shire m serves the lines of home shires m, m+8, m+16 and m+24. Hardware read counters confirmed the memory-shire bits for 64 of 64 lines (and in all 15 passes of the three-card check).
measured
three cards
Anatomy of a memory access ↗
L43
Inside a channel: bank PA[12:10], column PA[17:13] (plus PA[5:1] within the line), row PA[18] and up (PA[34:18]); 8 banks, 2 KB page, one rank per channel.
measured
aifoundry2
Anatomy of a memory access ↗
dram.row-bits
DRAM address map: PA[9] selects the controller (channel) within the memory shire, PA[12:10] the DRAM bank (8 banks), PA[34:18] the row; the page policy is open-page. Measured on 29 September (E57): another row in the same bank is a row conflict, and a row that also differs in any of PA[6-12] (the memory shire, the controller, the bank) reads as a row hit, 20 cycles faster, on aifoundry1-c1 and aifoundry3 (15 of 15 conditions); on aifoundry3 and aifoundry2 PA[6-9] set the refresh phase and PA[10-13] and PA[18] do not, so each controller refreshes on its own. On aifoundry2, run the same way as a third card, 14 of 15 conditions came out so: two lines that differ only in PA[17], a column bit in this map, read as a row conflict there.
measured
aifoundry3, aifoundry1 card 1
no published page yet
L50
L1 data cache hit: 5.25 cycles load-to-use (8.8 ns at 600 MHz); the same on three cards (per-pass ranges 5.247-5.259).
measured
three cards
Memory hierarchy ↗
lat-l1
L2 cache hit (and the shire's own scratchpad): 47 cycles (78 ns); hart 1 pays 3 more (39 read buffer, 50 L2).
measured
three cards
Memory hierarchy ↗
lat-l2
L3 hit: 110 + 12 cycles per mesh hop between the requesting shire and the line's home shire (fitted 110.5 + 11.99 on three cards); 159-169 cycles (265-282 ns) on average depending on the requesting shire.
measured
three cards
Anatomy of a memory access ↗
l3.latency
Past the L3, the DRAM leg costs 91 + 12 × hops(home shire, memory shire) cycles; about 28 of the 91 are the DRAM chip (activate 11, read latency and two bursts 17) and at most about 63 the L3 home's miss handling and the memory shire. Only about 28 of a ~300-cycle DRAM load are the DRAM's own timing.
measured
three cards
Anatomy of a memory access ↗
dram.leg
A typical DRAM load, timed one at a time: 299 cycles (500 ns), the median of 4,500 loads from shire 0 to random lines; 299 in each of 15 passes on three cards.
measured
three cards
Anatomy of a memory access ↗
lat-dram-typical
DRAM load from a pointer chase: 287-297 cycles at 600 MHz (479-495 ns): 296.6-297.1 from shires 0 and 31, 287.2-288.8 from 7 and 24; about 490 ns, a fifth more than an A100's HBM (405 ns).
measured
three cards
Memory hierarchy ↗
lat-dram
Of the 91-cycle memory-shire constant (152 ns), the DRAM chip accounts for about 28 cycles (activate tRCD 11 cycles = 18 ns, 19.3 ns read latency, the two 4.3 ns bursts of a 64-byte line); the rest, at most ~63 cycles (~105 ns), is the L3 home's miss handling (about 12 cycles by the spec: an L3 miss is 42 shire clocks against 30 for a hit) and the memory shire: controller queue, PHY and the crossings between the 933 MHz DDR clock and the mesh.
model
Anatomy of a memory access ↗
L46
Of a DRAM load's ~300 cycles only about 28 are the DRAM chip's own timing (activate tRCD 18 ns, 19.3 ns read latency, the two 4.3 ns bursts of a 64-byte line); the rest is paths on the chip.
inference
Anatomy of a memory access ↗
lat-dram-chip
L1 hit (memhier loop): 0.75 pJ/B [0.62-0.88] above idle, 1 KB tensor loads (L1: 32 B vector loads) by every minion at 600 MHz; per card a2 0.77, a3 0.75, a1c1 0.72.
measured
three cards
The energy manual ↗
e-l1
L2 cache: 3.11 pJ/B [1.42-4.99] above idle, 1 KB tensor loads (L1: 32 B vector loads) by every minion at 600 MHz; per card a2 2.64, a3 2.83, a1c1 3.86.
measured
three cards
The energy manual ↗
e-l2
L3 (over the mesh): 14.7 pJ/B [7.1-20.5] above idle, 1 KB tensor loads (L1: 32 B vector loads) by every minion at 600 MHz; per card a2 12.3, a3 13.5, a1c1 18.4.
measured
three cards
The energy manual ↗
e-l3
DRAM: 114.6 pJ/B [89.0-141.3] above idle, 1 KB tensor loads (L1: 32 B vector loads) by every minion at 600 MHz; per card a2 111.5, a3 105.6, a1c1 126.6.
measured
three cards
The energy manual ↗
e-dram
Each mesh hop adds 12 cycles round trip at 600 MHz (20 ns): L3 11.99, remote scratchpad 12.00, TensorSend 12.01-12.02 cycles per hop on every card.
measured
three cards
On-chip communication ↗
mesh-hop-lat
The mesh routes in dimension order, and a request and its reply take opposite orders: a request goes x first, then y, and a reply y first, then x, on the logical map, so a reply retraces its request's route backwards. Measured on 29 September (E56) with sets of streams between shires chosen so that their streams share one directed link under one order and none under the other: 1 KB tensor loads, whose data travel as replies, fell to 0.54-0.77 of their bandwidth alone when they shared a link under y first and held at 1.00 when they shared one under x first; tensor stores, whose data travel as requests, showed the mirror (0.52-0.76 against 1.00). A shared link carried about 92 GB/s. The same on aifoundry1 card 1 (development), aifoundry3 (the frozen validation) and aifoundry2 (the same frozen test, run as a third card on the evening of 29 September), three passes each.
measured
three cards
no published page yet
L104
Fitted memory-shire positions on the logical map: memory shires 0-3 one step off the top edge at x = 1-4 (y = -1), 4-7 one step off the bottom edge at x = 1-4 (y = 6). Memory shire 2's position is a tie-break (x = 3 or 5 above the grid, or (6,0), fit equally).
measured
aifoundry2
Anatomy of a memory access ↗
mesh.memshire-positions
An L3 read from another shire enters the home shire's cache through its L3 slave port and moves down the pipeline as L3_Read and L3_Fill: a miss goes out the to_sys mesh port to memory, the data comes back as the L3 fill, and the home answers the requester. The order memory shire, L3 home, requester is the specification's; which way each leg turns on the mesh is not documented.
documented
no published page yet
sc.l3-miss+}

## flow/A/5
FLOW 1 · LOAD TO DRAM
Channel 1 (PA[9]), bank 4 (PA[12:10]): about [-25–28-] {+28+} cycles of the load are the DRAM chip itself
… and on to a memory shire: about 299 cycles, about [-25–28-] {+28+} of them in the DRAM chip.
1
L1 … all.

 Replay
More detail and the sources {+

Hart 0 of minion 0 (neighbourhood 0) in shire 0 loads one 64-byte line that no cache holds. Its physical address picks every stop:

 0x80_1234_5340: L2 bank PA[7:6] = 1 · L3 home PA[10:6] = shire 13 · memory shire PA[8:6] = 5 · channel PA[9] = 1 · DRAM bank PA[12:10] = 4

 Requester shire
0
1
2
3
4
5
6
7
8
9
10
11
12
13
14
15
16
17
18
19
20
21
22
23
24
25
26
27
28
29
30
31
New address
Leg What happens cycles pJ/B
L1 miss (a hit: 5.25) 0.75
L2 bank 1 miss (a hit: 47) 3.1
L3 home, shire 13 4 hops: a hit would be 110 + 12×4 158 15
memory shire 5 4 hops on: + 91 + 12×4 297
LPDDR4X, channel 1 bank 4: about 28 cycles are the DRAM chip (inferred) 115
back to shire 0 back through the L3 home: the model's total; typical, measured: 299 297
Inferred or open here, and what would settle it (1)

 Nearly settled: the way back of a DRAM load (Flow 1, Load -> DRAM)

 The reply's path: the diagram draws it from the memory shire through the L3 home to the requester, each leg y first.

 What settles it, and what is left: The leg order is documented in a manual already in the repo: CORE-ET Shire Cache Specification §3.2.2 'L3 REQ_Read' (pdf p.55): L3 reads that miss go out the to_sys mesh port, the data returns to the L3 as L3_Fill, then the reply goes to the requester, so memory shire -> L3 home -> requester is spec. Each leg's route: a reply goes y first (E56, 29 September, fact L104), so the drawing takes each leg back along its request's links. What is left: E56's streams ran between compute shires' scratchpads, so that a memory shire's and an L3 home's replies follow the same rule is inferred.

 On the hub: rung 32: A link-contention test for the mesh's routing order ↗ · rung 21: The NoC's reference manual and specification ↗

 Measured and explained in Anatomy of a memory access ↗.

 The facts this flow uses (25): point at one for its source

 Path of a cacheable load: an L1 miss sends Read_L2 over ET-Link to the local bank chosen by PA[7:6]; an L2 miss sends Read_L3 over the to_l3 mesh interface to the home shire's L3 slave chosen by PA[10:6] (data returns straight to the neighbourhood, before the fill); an L3 miss goes over to_sys to the memory shire chosen by PA[8:6], whose controller does activate/read/precharge.
documented
Anatomy of a memory access ↗
addr.load-path
Measured load-to-use model from any requesting shire at 600 MHz: L1 5; L2 47-48; L3 110 + 12·hops(requester, home = PA[10:6]); DRAM 110 + 12·hops(requester, home) + 91 + 12·hops(home, memory shire = PA[8:6]). The mesh round trip is paid twice on a DRAM load: to the L3 home, then on to the memory shire.
measured
three cards
Anatomy of a memory access ↗
addr.load-model
Whole DRAM load: latency = 110 + 12·hops(requester → L3 home) + 91 + 12·hops(L3 home → memory shire). Left as fitted, the model is within ±3 cycles for 97% of lines (each line's fastest of three loads) on aifoundry2, 93% on aifoundry3 and 94% on aifoundry1's card 1; on the 19 September fitting run, 83% of single loads were within ±3 cycles (aifoundry2).
measured
three cards
Anatomy of a memory access ↗
L45
L2 address decode: offset PA[5:0], bank PA[7:6], sub-bank PA[9:8], set from PA[10] up (L2 set bits are PA[19:10] on ET-SoC-1).
documented
Anatomy of a memory access ↗
l2.decode
A line's L3 home shire is PA[10:6]: consecutive 64-byte lines rotate over the 32 compute shires' L3 slices (default 'swizzle0'; the firmware leaves the swizzle register at reset).
measured
three cards
Anatomy of a memory access ↗
l3.home
The memory shire serving a line is PA[8:6] (so it is always the L3 home shire's low three bits) and the controller/channel within it is PA[9]: consecutive 64 B lines rotate over the 8 memory shires, the two channels alternate every 512 B.
measured
aifoundry2
Anatomy of a memory access ↗
dram.memshire-select
The memory shire that serves a line is picked by physical-address bits 8:6 and its L3 home shire by bits 10:6, so memory shire m serves the lines of home shires m, m+8, m+16 and m+24. Hardware read counters confirmed the memory-shire bits for 64 of 64 lines (and in all 15 passes of the three-card check).
measured
three cards
Anatomy of a memory access ↗
L43
Inside a channel: bank PA[12:10], column PA[17:13] (plus PA[5:1] within the line), row PA[18] and up (PA[34:18]); 8 banks, 2 KB page, one rank per channel.
measured
aifoundry2
Anatomy of a memory access ↗
dram.row-bits
DRAM address map: PA[9] selects the controller (channel) within the memory shire, PA[12:10] the DRAM bank (8 banks), PA[34:18] the row; the page policy is open-page. Measured on 29 September (E57): another row in the same bank is a row conflict, and a row that also differs in any of PA[6-12] (the memory shire, the controller, the bank) reads as a row hit, 20 cycles faster, on aifoundry1-c1 and aifoundry3 (15 of 15 conditions); on aifoundry3 and aifoundry2 PA[6-9] set the refresh phase and PA[10-13] and PA[18] do not, so each controller refreshes on its own. On aifoundry2, run the same way as a third card, 14 of 15 conditions came out so: two lines that differ only in PA[17], a column bit in this map, read as a row conflict there.
measured
aifoundry3, aifoundry1 card 1
no published page yet
L50
L1 data cache hit: 5.25 cycles load-to-use (8.8 ns at 600 MHz); the same on three cards (per-pass ranges 5.247-5.259).
measured
three cards
Memory hierarchy ↗
lat-l1
L2 cache hit (and the shire's own scratchpad): 47 cycles (78 ns); hart 1 pays 3 more (39 read buffer, 50 L2).
measured
three cards
Memory hierarchy ↗
lat-l2
L3 hit: 110 + 12 cycles per mesh hop between the requesting shire and the line's home shire (fitted 110.5 + 11.99 on three cards); 159-169 cycles (265-282 ns) on average depending on the requesting shire.
measured
three cards
Anatomy of a memory access ↗
l3.latency
Past the L3, the DRAM leg costs 91 + 12 × hops(home shire, memory shire) cycles; about 28 of the 91 are the DRAM chip (activate 11, read latency and two bursts 17) and at most about 63 the L3 home's miss handling and the memory shire. Only about 28 of a ~300-cycle DRAM load are the DRAM's own timing.
measured
three cards
Anatomy of a memory access ↗
dram.leg
A typical DRAM load, timed one at a time: 299 cycles (500 ns), the median of 4,500 loads from shire 0 to random lines; 299 in each of 15 passes on three cards.
measured
three cards
Anatomy of a memory access ↗
lat-dram-typical
DRAM load from a pointer chase: 287-297 cycles at 600 MHz (479-495 ns): 296.6-297.1 from shires 0 and 31, 287.2-288.8 from 7 and 24; about 490 ns, a fifth more than an A100's HBM (405 ns).
measured
three cards
Memory hierarchy ↗
lat-dram
Of the 91-cycle memory-shire constant (152 ns), the DRAM chip accounts for about 28 cycles (activate tRCD 11 cycles = 18 ns, 19.3 ns read latency, the two 4.3 ns bursts of a 64-byte line); the rest, at most ~63 cycles (~105 ns), is the L3 home's miss handling (about 12 cycles by the spec: an L3 miss is 42 shire clocks against 30 for a hit) and the memory shire: controller queue, PHY and the crossings between the 933 MHz DDR clock and the mesh.
model
Anatomy of a memory access ↗
L46
Of a DRAM load's ~300 cycles only about 28 are the DRAM chip's own timing (activate tRCD 18 ns, 19.3 ns read latency, the two 4.3 ns bursts of a 64-byte line); the rest is paths on the chip.
inference
Anatomy of a memory access ↗
lat-dram-chip
L1 hit (memhier loop): 0.75 pJ/B [0.62-0.88] above idle, 1 KB tensor loads (L1: 32 B vector loads) by every minion at 600 MHz; per card a2 0.77, a3 0.75, a1c1 0.72.
measured
three cards
The energy manual ↗
e-l1
L2 cache: 3.11 pJ/B [1.42-4.99] above idle, 1 KB tensor loads (L1: 32 B vector loads) by every minion at 600 MHz; per card a2 2.64, a3 2.83, a1c1 3.86.
measured
three cards
The energy manual ↗
e-l2
L3 (over the mesh): 14.7 pJ/B [7.1-20.5] above idle, 1 KB tensor loads (L1: 32 B vector loads) by every minion at 600 MHz; per card a2 12.3, a3 13.5, a1c1 18.4.
measured
three cards
The energy manual ↗
e-l3
DRAM: 114.6 pJ/B [89.0-141.3] above idle, 1 KB tensor loads (L1: 32 B vector loads) by every minion at 600 MHz; per card a2 111.5, a3 105.6, a1c1 126.6.
measured
three cards
The energy manual ↗
e-dram
Each mesh hop adds 12 cycles round trip at 600 MHz (20 ns): L3 11.99, remote scratchpad 12.00, TensorSend 12.01-12.02 cycles per hop on every card.
measured
three cards
On-chip communication ↗
mesh-hop-lat
The mesh routes in dimension order, and a request and its reply take opposite orders: a request goes x first, then y, and a reply y first, then x, on the logical map, so a reply retraces its request's route backwards. Measured on 29 September (E56) with sets of streams between shires chosen so that their streams share one directed link under one order and none under the other: 1 KB tensor loads, whose data travel as replies, fell to 0.54-0.77 of their bandwidth alone when they shared a link under y first and held at 1.00 when they shared one under x first; tensor stores, whose data travel as requests, showed the mirror (0.52-0.76 against 1.00). A shared link carried about 92 GB/s. The same on aifoundry1 card 1 (development), aifoundry3 (the frozen validation) and aifoundry2 (the same frozen test, run as a third card on the evening of 29 September), three passes each.
measured
three cards
no published page yet
L104
Fitted memory-shire positions on the logical map: memory shires 0-3 one step off the top edge at x = 1-4 (y = -1), 4-7 one step off the bottom edge at x = 1-4 (y = 6). Memory shire 2's position is a tie-break (x = 3 or 5 above the grid, or (6,0), fit equally).
measured
aifoundry2
Anatomy of a memory access ↗
mesh.memshire-positions
An L3 read from another shire enters the home shire's cache through its L3 slave port and moves down the pipeline as L3_Read and L3_Fill: a miss goes out the to_sys mesh port to memory, the data comes back as the L3 fill, and the home answers the requester. The order memory shire, L3 home, requester is the specification's; which way each leg turns on the mesh is not documented.
documented
no published page yet
sc.l3-miss+}

## flow/B/0
FLOW 2 · LATENCY LADDER
L2 read buffer: 36 … 299 typ.
Replay
More detail and the sources {+

The same load from shire 0, hitting at each level in turn. The L3 home and the scratchpad are 4 hops away in shire 13; memory shire 5 is 4 hops further. Bars are minion cycles at 600 MHz.

 Level pJ/B chip-wide
L1 0.75 14.5 TB/s
L2 read buffer
L2 3.1 (1.4–5.0) 2.45 TB/s
own scratchpad 2.25–4.40 2.46 TB/s
another shire's scratchpad, 2.1 hops mean 5.10–11.8 0.96 TB/s
L3, home 13 15 (7–21) 0.98 TB/s
DRAM 115 (89–141) 76 GB/s

 Another shire's scratchpad was measured with every shire reading the one 16 IDs away, 2.1 hops on average, not at the 4 hops of the ladder. L1 bandwidth is the energy manual's unrolled loop (the memory-hierarchy probe's loop reaches 6.2 TB/s). Energies are above idle, with their range over passes in brackets.

 Measured and explained in The energy manual ↗.

 The facts this flow uses (26): point at one for its source

 L1 data cache hit: 5.25 cycles load-to-use (8.8 ns at 600 MHz); the same on three cards (per-pass ranges 5.247-5.259).
measured
three cards
Memory hierarchy ↗
lat-l1
L2 read buffer (8 clean lines per bank x 4 banks = 2 KB per shire): 36 cycles (60 ns), 11 fewer than the L2 array.
measured
three cards
Memory hierarchy ↗
lat-rb
L2 cache hit (and the shire's own scratchpad): 47 cycles (78 ns); hart 1 pays 3 more (39 read buffer, 50 L2).
measured
three cards
Memory hierarchy ↗
lat-l2
The shire's own L2 scratchpad: 47 cycles (78 ns), the same SRAM, latency and bandwidth as the L2 cache.
measured
three cards
Memory hierarchy ↗
lat-scp-own
Another shire's scratchpad: 99.84 + 12.00 cycles per mesh hop at 600 MHz (112-220 cycles, 186-366 ns over 1-10 hops); all 124 points within 1 cycle, a->b equals b->a within 0.032 cycles.
measured
three cards
Memory hierarchy ↗
lat-scp-remote
L3 hit against distance to the line's home shire: 110.5 + 11.99 cycles per mesh hop (from shire 0), within 4 cycles for 99.4-100% of lines on each card.
measured
three cards
Anatomy of a memory access ↗
lat-l3-hop
L3 hit: 110 + 12 cycles per mesh hop between the requesting shire and the line's home shire (fitted 110.5 + 11.99 on three cards); 159-169 cycles (265-282 ns) on average depending on the requesting shire.
measured
three cards
Anatomy of a memory access ↗
l3.latency
L3 hit from a pointer chase, averaged over all 32 slices: 159-169 cycles at 600 MHz (265-282 ns), by requesting shire: 168.8-168.9 (shire 0), 160.6-160.7 (7), 159.1-159.2 (24), 168.8-168.9 (31).
measured
three cards
Memory hierarchy ↗
lat-l3-avg
Past the L3, the DRAM leg costs 91 + 12 × hops(home shire, memory shire) cycles; about 28 of the 91 are the DRAM chip (activate 11, read latency and two bursts 17) and at most about 63 the L3 home's miss handling and the memory shire. Only about 28 of a ~300-cycle DRAM load are the DRAM's own timing.
measured
three cards
Anatomy of a memory access ↗
dram.leg
A typical DRAM load, timed one at a time: 299 cycles (500 ns), the median of 4,500 loads from shire 0 to random lines; 299 in each of 15 passes on three cards.
measured
three cards
Anatomy of a memory access ↗
lat-dram-typical
DRAM load from a pointer chase: 287-297 cycles at 600 MHz (479-495 ns): 296.6-297.1 from shires 0 and 31, 287.2-288.8 from 7 and 24; about 490 ns, a fifth more than an A100's HBM (405 ns).
measured
three cards
Memory hierarchy ↗
lat-dram
L1 hits, 32 B vector loads by both harts: 14.5 TB/s chip-wide (23.6 B per minion-cycle) in the energy manual's unrolled loop; the memory-hierarchy probe's loop reaches 6.2 TB/s (10 B per minion-cycle). Spec: 32 B per cycle.
measured
three cards (14.5 TB/s); 6.2 TB/s on aifoundry2, aifoundry3
Ridge points ↗
bw-l1
L2 cache, 1 KB tensor loads by every minion: 2.45 TB/s chip-wide, 4.0 B per minion-cycle (128 B per shire-cycle), half the four banks' 256 B per shire-cycle spec.
measured
aifoundry2, aifoundry3
Ridge points ↗
bw-l2
Own-shire scratchpad: 2.46 TB/s chip-wide, 4.0 B per minion-cycle, same as the L2. Tensor stores into it reach 1.23 TB/s (half the read rate).
measured
aifoundry2, aifoundry3 (the read rate); the store rate on three cards
Ridge points ↗
bw-scp-own
Another shire's scratchpad (each shire reading the one 16 IDs away, 2.1 hops on average): 0.96 TB/s chip-wide, 1.56 B per minion-cycle.
measured
aifoundry2, aifoundry3
Ridge points ↗
bw-scp-remote
L3, every minion streaming: 0.98 TB/s chip-wide, 1.6 B per minion-cycle; spec (assumed one 64 B beat per NoC cycle per shire port) 3.3 TB/s, 5.33 B per minion-cycle.
measured
aifoundry2, aifoundry3
Ridge points ↗
bw-l3
DRAM streaming: 76 GB/s for the whole chip (0.124 B per minion-cycle), about 64% of the 119 GB/s that 16 x 16-bit channels carry at 3,733 MT/s; about a twentieth of an A100.
measured
aifoundry2, aifoundry3
Ridge points ↗
bw-dram
L1 hit (memhier loop): 0.75 pJ/B [0.62-0.88] above idle, 1 KB tensor loads (L1: 32 B vector loads) by every minion at 600 MHz; per card a2 0.77, a3 0.75, a1c1 0.72.
measured
three cards
The energy manual ↗
e-l1
L2 cache: 3.11 pJ/B [1.42-4.99] above idle, 1 KB tensor loads (L1: 32 B vector loads) by every minion at 600 MHz; per card a2 2.64, a3 2.83, a1c1 3.86.
measured
three cards
The energy manual ↗
e-l2
Own scratchpad filled with zeros: 2.25 pJ/B [2.06-2.61] above idle, 1 KB tensor loads (L1: 32 B vector loads) by every minion at 600 MHz; per card a2 2.11, a3 2.10, a1c1 2.55.
measured
three cards
The energy manual ↗
e-scp-own-zeros
Own scratchpad filled with random data: 4.40 pJ/B [3.94-5.08] above idle, 1 KB tensor loads (L1: 32 B vector loads) by every minion at 600 MHz; per card a2 4.13, a3 4.04, a1c1 5.03.
measured
three cards
The energy manual ↗
e-scp-own-rand
Scratchpad 16 shire IDs away (2.1 hops mean) filled with zeros: 5.10 pJ/B [4.40-6.45] above idle, 1 KB tensor loads (L1: 32 B vector loads) by every minion at 600 MHz; per card a2 5.04, a3 4.55, a1c1 5.71.
measured
three cards
The energy manual ↗
e-scp-remote-zeros
Scratchpad 16 shire IDs away (2.1 hops mean) filled with random data: 11.8 pJ/B [9.5-14.4] above idle, 1 KB tensor loads (L1: 32 B vector loads) by every minion at 600 MHz; per card a2 11.1, a3 10.8, a1c1 13.6.
measured
three cards
The energy manual ↗
e-scp-remote-rand
L3 (over the mesh): 14.7 pJ/B [7.1-20.5] above idle, 1 KB tensor loads (L1: 32 B vector loads) by every minion at 600 MHz; per card a2 12.3, a3 13.5, a1c1 18.4.
measured
three cards
The energy manual ↗
e-l3
DRAM: 114.6 pJ/B [89.0-141.3] above idle, 1 KB tensor loads (L1: 32 B vector loads) by every minion at 600 MHz; per card a2 111.5, a3 105.6, a1c1 126.6.
measured
three cards
The energy manual ↗
e-dram
The mesh routes in dimension order, and a request and its reply take opposite orders: a request goes x first, then y, and a reply y first, then x, on the logical map, so a reply retraces its request's route backwards. Measured on 29 September (E56) with sets of streams between shires chosen so that their streams share one directed link under one order and none under the other: 1 KB tensor loads, whose data travel as replies, fell to 0.54-0.77 of their bandwidth alone when they shared a link under y first and held at 1.00 when they shared one under x first; tensor stores, whose data travel as requests, showed the mirror (0.52-0.76 against 1.00). A shared link carried about 92 GB/s. The same on aifoundry1 card 1 (development), aifoundry3 (the frozen validation) and aifoundry2 (the same frozen test, run as a third card on the evening of 29 September), three passes each.
measured
three cards
no published page yet
L104+}

## flow/B/1
FLOW 2 · LATENCY LADDER
L1 hit: 5.25 cycles, … 299 typ.
Replay
More detail and the sources {+

The same load from shire 0, hitting at each level in turn. The L3 home and the scratchpad are 4 hops away in shire 13; memory shire 5 is 4 hops further. Bars are minion cycles at 600 MHz.

 Level pJ/B chip-wide
L1 0.75 14.5 TB/s
L2 read buffer
L2 3.1 (1.4–5.0) 2.45 TB/s
own scratchpad 2.25–4.40 2.46 TB/s
another shire's scratchpad, 2.1 hops mean 5.10–11.8 0.96 TB/s
L3, home 13 15 (7–21) 0.98 TB/s
DRAM 115 (89–141) 76 GB/s

 Another shire's scratchpad was measured with every shire reading the one 16 IDs away, 2.1 hops on average, not at the 4 hops of the ladder. L1 bandwidth is the energy manual's unrolled loop (the memory-hierarchy probe's loop reaches 6.2 TB/s). Energies are above idle, with their range over passes in brackets.

 Measured and explained in The energy manual ↗.

 The facts this flow uses (26): point at one for its source

 L1 data cache hit: 5.25 cycles load-to-use (8.8 ns at 600 MHz); the same on three cards (per-pass ranges 5.247-5.259).
measured
three cards
Memory hierarchy ↗
lat-l1
L2 read buffer (8 clean lines per bank x 4 banks = 2 KB per shire): 36 cycles (60 ns), 11 fewer than the L2 array.
measured
three cards
Memory hierarchy ↗
lat-rb
L2 cache hit (and the shire's own scratchpad): 47 cycles (78 ns); hart 1 pays 3 more (39 read buffer, 50 L2).
measured
three cards
Memory hierarchy ↗
lat-l2
The shire's own L2 scratchpad: 47 cycles (78 ns), the same SRAM, latency and bandwidth as the L2 cache.
measured
three cards
Memory hierarchy ↗
lat-scp-own
Another shire's scratchpad: 99.84 + 12.00 cycles per mesh hop at 600 MHz (112-220 cycles, 186-366 ns over 1-10 hops); all 124 points within 1 cycle, a->b equals b->a within 0.032 cycles.
measured
three cards
Memory hierarchy ↗
lat-scp-remote
L3 hit against distance to the line's home shire: 110.5 + 11.99 cycles per mesh hop (from shire 0), within 4 cycles for 99.4-100% of lines on each card.
measured
three cards
Anatomy of a memory access ↗
lat-l3-hop
L3 hit: 110 + 12 cycles per mesh hop between the requesting shire and the line's home shire (fitted 110.5 + 11.99 on three cards); 159-169 cycles (265-282 ns) on average depending on the requesting shire.
measured
three cards
Anatomy of a memory access ↗
l3.latency
L3 hit from a pointer chase, averaged over all 32 slices: 159-169 cycles at 600 MHz (265-282 ns), by requesting shire: 168.8-168.9 (shire 0), 160.6-160.7 (7), 159.1-159.2 (24), 168.8-168.9 (31).
measured
three cards
Memory hierarchy ↗
lat-l3-avg
Past the L3, the DRAM leg costs 91 + 12 × hops(home shire, memory shire) cycles; about 28 of the 91 are the DRAM chip (activate 11, read latency and two bursts 17) and at most about 63 the L3 home's miss handling and the memory shire. Only about 28 of a ~300-cycle DRAM load are the DRAM's own timing.
measured
three cards
Anatomy of a memory access ↗
dram.leg
A typical DRAM load, timed one at a time: 299 cycles (500 ns), the median of 4,500 loads from shire 0 to random lines; 299 in each of 15 passes on three cards.
measured
three cards
Anatomy of a memory access ↗
lat-dram-typical
DRAM load from a pointer chase: 287-297 cycles at 600 MHz (479-495 ns): 296.6-297.1 from shires 0 and 31, 287.2-288.8 from 7 and 24; about 490 ns, a fifth more than an A100's HBM (405 ns).
measured
three cards
Memory hierarchy ↗
lat-dram
L1 hits, 32 B vector loads by both harts: 14.5 TB/s chip-wide (23.6 B per minion-cycle) in the energy manual's unrolled loop; the memory-hierarchy probe's loop reaches 6.2 TB/s (10 B per minion-cycle). Spec: 32 B per cycle.
measured
three cards (14.5 TB/s); 6.2 TB/s on aifoundry2, aifoundry3
Ridge points ↗
bw-l1
L2 cache, 1 KB tensor loads by every minion: 2.45 TB/s chip-wide, 4.0 B per minion-cycle (128 B per shire-cycle), half the four banks' 256 B per shire-cycle spec.
measured
aifoundry2, aifoundry3
Ridge points ↗
bw-l2
Own-shire scratchpad: 2.46 TB/s chip-wide, 4.0 B per minion-cycle, same as the L2. Tensor stores into it reach 1.23 TB/s (half the read rate).
measured
aifoundry2, aifoundry3 (the read rate); the store rate on three cards
Ridge points ↗
bw-scp-own
Another shire's scratchpad (each shire reading the one 16 IDs away, 2.1 hops on average): 0.96 TB/s chip-wide, 1.56 B per minion-cycle.
measured
aifoundry2, aifoundry3
Ridge points ↗
bw-scp-remote
L3, every minion streaming: 0.98 TB/s chip-wide, 1.6 B per minion-cycle; spec (assumed one 64 B beat per NoC cycle per shire port) 3.3 TB/s, 5.33 B per minion-cycle.
measured
aifoundry2, aifoundry3
Ridge points ↗
bw-l3
DRAM streaming: 76 GB/s for the whole chip (0.124 B per minion-cycle), about 64% of the 119 GB/s that 16 x 16-bit channels carry at 3,733 MT/s; about a twentieth of an A100.
measured
aifoundry2, aifoundry3
Ridge points ↗
bw-dram
L1 hit (memhier loop): 0.75 pJ/B [0.62-0.88] above idle, 1 KB tensor loads (L1: 32 B vector loads) by every minion at 600 MHz; per card a2 0.77, a3 0.75, a1c1 0.72.
measured
three cards
The energy manual ↗
e-l1
L2 cache: 3.11 pJ/B [1.42-4.99] above idle, 1 KB tensor loads (L1: 32 B vector loads) by every minion at 600 MHz; per card a2 2.64, a3 2.83, a1c1 3.86.
measured
three cards
The energy manual ↗
e-l2
Own scratchpad filled with zeros: 2.25 pJ/B [2.06-2.61] above idle, 1 KB tensor loads (L1: 32 B vector loads) by every minion at 600 MHz; per card a2 2.11, a3 2.10, a1c1 2.55.
measured
three cards
The energy manual ↗
e-scp-own-zeros
Own scratchpad filled with random data: 4.40 pJ/B [3.94-5.08] above idle, 1 KB tensor loads (L1: 32 B vector loads) by every minion at 600 MHz; per card a2 4.13, a3 4.04, a1c1 5.03.
measured
three cards
The energy manual ↗
e-scp-own-rand
Scratchpad 16 shire IDs away (2.1 hops mean) filled with zeros: 5.10 pJ/B [4.40-6.45] above idle, 1 KB tensor loads (L1: 32 B vector loads) by every minion at 600 MHz; per card a2 5.04, a3 4.55, a1c1 5.71.
measured
three cards
The energy manual ↗
e-scp-remote-zeros
Scratchpad 16 shire IDs away (2.1 hops mean) filled with random data: 11.8 pJ/B [9.5-14.4] above idle, 1 KB tensor loads (L1: 32 B vector loads) by every minion at 600 MHz; per card a2 11.1, a3 10.8, a1c1 13.6.
measured
three cards
The energy manual ↗
e-scp-remote-rand
L3 (over the mesh): 14.7 pJ/B [7.1-20.5] above idle, 1 KB tensor loads (L1: 32 B vector loads) by every minion at 600 MHz; per card a2 12.3, a3 13.5, a1c1 18.4.
measured
three cards
The energy manual ↗
e-l3
DRAM: 114.6 pJ/B [89.0-141.3] above idle, 1 KB tensor loads (L1: 32 B vector loads) by every minion at 600 MHz; per card a2 111.5, a3 105.6, a1c1 126.6.
measured
three cards
The energy manual ↗
e-dram
The mesh routes in dimension order, and a request and its reply take opposite orders: a request goes x first, then y, and a reply y first, then x, on the logical map, so a reply retraces its request's route backwards. Measured on 29 September (E56) with sets of streams between shires chosen so that their streams share one directed link under one order and none under the other: 1 KB tensor loads, whose data travel as replies, fell to 0.54-0.77 of their bandwidth alone when they shared a link under y first and held at 1.00 when they shared one under x first; tensor stores, whose data travel as requests, showed the mirror (0.52-0.76 against 1.00). A shared link carried about 92 GB/s. The same on aifoundry1 card 1 (development), aifoundry3 (the frozen validation) and aifoundry2 (the same frozen test, run as a third card on the evening of 29 September), three passes each.
measured
three cards
no published page yet
L104+}

## flow/B/2
FLOW 2 · LATENCY LADDER
L2 read buffer: 36 … 299 typ.
Replay
More detail and the sources {+

The same load from shire 0, hitting at each level in turn. The L3 home and the scratchpad are 4 hops away in shire 13; memory shire 5 is 4 hops further. Bars are minion cycles at 600 MHz.

 Level pJ/B chip-wide
L1 0.75 14.5 TB/s
L2 read buffer
L2 3.1 (1.4–5.0) 2.45 TB/s
own scratchpad 2.25–4.40 2.46 TB/s
another shire's scratchpad, 2.1 hops mean 5.10–11.8 0.96 TB/s
L3, home 13 15 (7–21) 0.98 TB/s
DRAM 115 (89–141) 76 GB/s

 Another shire's scratchpad was measured with every shire reading the one 16 IDs away, 2.1 hops on average, not at the 4 hops of the ladder. L1 bandwidth is the energy manual's unrolled loop (the memory-hierarchy probe's loop reaches 6.2 TB/s). Energies are above idle, with their range over passes in brackets.

 Measured and explained in The energy manual ↗.

 The facts this flow uses (26): point at one for its source

 L1 data cache hit: 5.25 cycles load-to-use (8.8 ns at 600 MHz); the same on three cards (per-pass ranges 5.247-5.259).
measured
three cards
Memory hierarchy ↗
lat-l1
L2 read buffer (8 clean lines per bank x 4 banks = 2 KB per shire): 36 cycles (60 ns), 11 fewer than the L2 array.
measured
three cards
Memory hierarchy ↗
lat-rb
L2 cache hit (and the shire's own scratchpad): 47 cycles (78 ns); hart 1 pays 3 more (39 read buffer, 50 L2).
measured
three cards
Memory hierarchy ↗
lat-l2
The shire's own L2 scratchpad: 47 cycles (78 ns), the same SRAM, latency and bandwidth as the L2 cache.
measured
three cards
Memory hierarchy ↗
lat-scp-own
Another shire's scratchpad: 99.84 + 12.00 cycles per mesh hop at 600 MHz (112-220 cycles, 186-366 ns over 1-10 hops); all 124 points within 1 cycle, a->b equals b->a within 0.032 cycles.
measured
three cards
Memory hierarchy ↗
lat-scp-remote
L3 hit against distance to the line's home shire: 110.5 + 11.99 cycles per mesh hop (from shire 0), within 4 cycles for 99.4-100% of lines on each card.
measured
three cards
Anatomy of a memory access ↗
lat-l3-hop
L3 hit: 110 + 12 cycles per mesh hop between the requesting shire and the line's home shire (fitted 110.5 + 11.99 on three cards); 159-169 cycles (265-282 ns) on average depending on the requesting shire.
measured
three cards
Anatomy of a memory access ↗
l3.latency
L3 hit from a pointer chase, averaged over all 32 slices: 159-169 cycles at 600 MHz (265-282 ns), by requesting shire: 168.8-168.9 (shire 0), 160.6-160.7 (7), 159.1-159.2 (24), 168.8-168.9 (31).
measured
three cards
Memory hierarchy ↗
lat-l3-avg
Past the L3, the DRAM leg costs 91 + 12 × hops(home shire, memory shire) cycles; about 28 of the 91 are the DRAM chip (activate 11, read latency and two bursts 17) and at most about 63 the L3 home's miss handling and the memory shire. Only about 28 of a ~300-cycle DRAM load are the DRAM's own timing.
measured
three cards
Anatomy of a memory access ↗
dram.leg
A typical DRAM load, timed one at a time: 299 cycles (500 ns), the median of 4,500 loads from shire 0 to random lines; 299 in each of 15 passes on three cards.
measured
three cards
Anatomy of a memory access ↗
lat-dram-typical
DRAM load from a pointer chase: 287-297 cycles at 600 MHz (479-495 ns): 296.6-297.1 from shires 0 and 31, 287.2-288.8 from 7 and 24; about 490 ns, a fifth more than an A100's HBM (405 ns).
measured
three cards
Memory hierarchy ↗
lat-dram
L1 hits, 32 B vector loads by both harts: 14.5 TB/s chip-wide (23.6 B per minion-cycle) in the energy manual's unrolled loop; the memory-hierarchy probe's loop reaches 6.2 TB/s (10 B per minion-cycle). Spec: 32 B per cycle.
measured
three cards (14.5 TB/s); 6.2 TB/s on aifoundry2, aifoundry3
Ridge points ↗
bw-l1
L2 cache, 1 KB tensor loads by every minion: 2.45 TB/s chip-wide, 4.0 B per minion-cycle (128 B per shire-cycle), half the four banks' 256 B per shire-cycle spec.
measured
aifoundry2, aifoundry3
Ridge points ↗
bw-l2
Own-shire scratchpad: 2.46 TB/s chip-wide, 4.0 B per minion-cycle, same as the L2. Tensor stores into it reach 1.23 TB/s (half the read rate).
measured
aifoundry2, aifoundry3 (the read rate); the store rate on three cards
Ridge points ↗
bw-scp-own
Another shire's scratchpad (each shire reading the one 16 IDs away, 2.1 hops on average): 0.96 TB/s chip-wide, 1.56 B per minion-cycle.
measured
aifoundry2, aifoundry3
Ridge points ↗
bw-scp-remote
L3, every minion streaming: 0.98 TB/s chip-wide, 1.6 B per minion-cycle; spec (assumed one 64 B beat per NoC cycle per shire port) 3.3 TB/s, 5.33 B per minion-cycle.
measured
aifoundry2, aifoundry3
Ridge points ↗
bw-l3
DRAM streaming: 76 GB/s for the whole chip (0.124 B per minion-cycle), about 64% of the 119 GB/s that 16 x 16-bit channels carry at 3,733 MT/s; about a twentieth of an A100.
measured
aifoundry2, aifoundry3
Ridge points ↗
bw-dram
L1 hit (memhier loop): 0.75 pJ/B [0.62-0.88] above idle, 1 KB tensor loads (L1: 32 B vector loads) by every minion at 600 MHz; per card a2 0.77, a3 0.75, a1c1 0.72.
measured
three cards
The energy manual ↗
e-l1
L2 cache: 3.11 pJ/B [1.42-4.99] above idle, 1 KB tensor loads (L1: 32 B vector loads) by every minion at 600 MHz; per card a2 2.64, a3 2.83, a1c1 3.86.
measured
three cards
The energy manual ↗
e-l2
Own scratchpad filled with zeros: 2.25 pJ/B [2.06-2.61] above idle, 1 KB tensor loads (L1: 32 B vector loads) by every minion at 600 MHz; per card a2 2.11, a3 2.10, a1c1 2.55.
measured
three cards
The energy manual ↗
e-scp-own-zeros
Own scratchpad filled with random data: 4.40 pJ/B [3.94-5.08] above idle, 1 KB tensor loads (L1: 32 B vector loads) by every minion at 600 MHz; per card a2 4.13, a3 4.04, a1c1 5.03.
measured
three cards
The energy manual ↗
e-scp-own-rand
Scratchpad 16 shire IDs away (2.1 hops mean) filled with zeros: 5.10 pJ/B [4.40-6.45] above idle, 1 KB tensor loads (L1: 32 B vector loads) by every minion at 600 MHz; per card a2 5.04, a3 4.55, a1c1 5.71.
measured
three cards
The energy manual ↗
e-scp-remote-zeros
Scratchpad 16 shire IDs away (2.1 hops mean) filled with random data: 11.8 pJ/B [9.5-14.4] above idle, 1 KB tensor loads (L1: 32 B vector loads) by every minion at 600 MHz; per card a2 11.1, a3 10.8, a1c1 13.6.
measured
three cards
The energy manual ↗
e-scp-remote-rand
L3 (over the mesh): 14.7 pJ/B [7.1-20.5] above idle, 1 KB tensor loads (L1: 32 B vector loads) by every minion at 600 MHz; per card a2 12.3, a3 13.5, a1c1 18.4.
measured
three cards
The energy manual ↗
e-l3
DRAM: 114.6 pJ/B [89.0-141.3] above idle, 1 KB tensor loads (L1: 32 B vector loads) by every minion at 600 MHz; per card a2 111.5, a3 105.6, a1c1 126.6.
measured
three cards
The energy manual ↗
e-dram
The mesh routes in dimension order, and a request and its reply take opposite orders: a request goes x first, then y, and a reply y first, then x, on the logical map, so a reply retraces its request's route backwards. Measured on 29 September (E56) with sets of streams between shires chosen so that their streams share one directed link under one order and none under the other: 1 KB tensor loads, whose data travel as replies, fell to 0.54-0.77 of their bandwidth alone when they shared a link under y first and held at 1.00 when they shared one under x first; tensor stores, whose data travel as requests, showed the mirror (0.52-0.76 against 1.00). A shared link carried about 92 GB/s. The same on aifoundry1 card 1 (development), aifoundry3 (the frozen validation) and aifoundry2 (the same frozen test, run as a third card on the evening of 29 September), three passes each.
measured
three cards
no published page yet
L104+}

## flow/B/3
FLOW 2 · LATENCY LADDER
L2 hit: 47 cycles, … 299 typ.
Replay
More detail and the sources {+

The same load from shire 0, hitting at each level in turn. The L3 home and the scratchpad are 4 hops away in shire 13; memory shire 5 is 4 hops further. Bars are minion cycles at 600 MHz.

 Level pJ/B chip-wide
L1 0.75 14.5 TB/s
L2 read buffer
L2 3.1 (1.4–5.0) 2.45 TB/s
own scratchpad 2.25–4.40 2.46 TB/s
another shire's scratchpad, 2.1 hops mean 5.10–11.8 0.96 TB/s
L3, home 13 15 (7–21) 0.98 TB/s
DRAM 115 (89–141) 76 GB/s

 Another shire's scratchpad was measured with every shire reading the one 16 IDs away, 2.1 hops on average, not at the 4 hops of the ladder. L1 bandwidth is the energy manual's unrolled loop (the memory-hierarchy probe's loop reaches 6.2 TB/s). Energies are above idle, with their range over passes in brackets.

 Measured and explained in The energy manual ↗.

 The facts this flow uses (26): point at one for its source

 L1 data cache hit: 5.25 cycles load-to-use (8.8 ns at 600 MHz); the same on three cards (per-pass ranges 5.247-5.259).
measured
three cards
Memory hierarchy ↗
lat-l1
L2 read buffer (8 clean lines per bank x 4 banks = 2 KB per shire): 36 cycles (60 ns), 11 fewer than the L2 array.
measured
three cards
Memory hierarchy ↗
lat-rb
L2 cache hit (and the shire's own scratchpad): 47 cycles (78 ns); hart 1 pays 3 more (39 read buffer, 50 L2).
measured
three cards
Memory hierarchy ↗
lat-l2
The shire's own L2 scratchpad: 47 cycles (78 ns), the same SRAM, latency and bandwidth as the L2 cache.
measured
three cards
Memory hierarchy ↗
lat-scp-own
Another shire's scratchpad: 99.84 + 12.00 cycles per mesh hop at 600 MHz (112-220 cycles, 186-366 ns over 1-10 hops); all 124 points within 1 cycle, a->b equals b->a within 0.032 cycles.
measured
three cards
Memory hierarchy ↗
lat-scp-remote
L3 hit against distance to the line's home shire: 110.5 + 11.99 cycles per mesh hop (from shire 0), within 4 cycles for 99.4-100% of lines on each card.
measured
three cards
Anatomy of a memory access ↗
lat-l3-hop
L3 hit: 110 + 12 cycles per mesh hop between the requesting shire and the line's home shire (fitted 110.5 + 11.99 on three cards); 159-169 cycles (265-282 ns) on average depending on the requesting shire.
measured
three cards
Anatomy of a memory access ↗
l3.latency
L3 hit from a pointer chase, averaged over all 32 slices: 159-169 cycles at 600 MHz (265-282 ns), by requesting shire: 168.8-168.9 (shire 0), 160.6-160.7 (7), 159.1-159.2 (24), 168.8-168.9 (31).
measured
three cards
Memory hierarchy ↗
lat-l3-avg
Past the L3, the DRAM leg costs 91 + 12 × hops(home shire, memory shire) cycles; about 28 of the 91 are the DRAM chip (activate 11, read latency and two bursts 17) and at most about 63 the L3 home's miss handling and the memory shire. Only about 28 of a ~300-cycle DRAM load are the DRAM's own timing.
measured
three cards
Anatomy of a memory access ↗
dram.leg
A typical DRAM load, timed one at a time: 299 cycles (500 ns), the median of 4,500 loads from shire 0 to random lines; 299 in each of 15 passes on three cards.
measured
three cards
Anatomy of a memory access ↗
lat-dram-typical
DRAM load from a pointer chase: 287-297 cycles at 600 MHz (479-495 ns): 296.6-297.1 from shires 0 and 31, 287.2-288.8 from 7 and 24; about 490 ns, a fifth more than an A100's HBM (405 ns).
measured
three cards
Memory hierarchy ↗
lat-dram
L1 hits, 32 B vector loads by both harts: 14.5 TB/s chip-wide (23.6 B per minion-cycle) in the energy manual's unrolled loop; the memory-hierarchy probe's loop reaches 6.2 TB/s (10 B per minion-cycle). Spec: 32 B per cycle.
measured
three cards (14.5 TB/s); 6.2 TB/s on aifoundry2, aifoundry3
Ridge points ↗
bw-l1
L2 cache, 1 KB tensor loads by every minion: 2.45 TB/s chip-wide, 4.0 B per minion-cycle (128 B per shire-cycle), half the four banks' 256 B per shire-cycle spec.
measured
aifoundry2, aifoundry3
Ridge points ↗
bw-l2
Own-shire scratchpad: 2.46 TB/s chip-wide, 4.0 B per minion-cycle, same as the L2. Tensor stores into it reach 1.23 TB/s (half the read rate).
measured
aifoundry2, aifoundry3 (the read rate); the store rate on three cards
Ridge points ↗
bw-scp-own
Another shire's scratchpad (each shire reading the one 16 IDs away, 2.1 hops on average): 0.96 TB/s chip-wide, 1.56 B per minion-cycle.
measured
aifoundry2, aifoundry3
Ridge points ↗
bw-scp-remote
L3, every minion streaming: 0.98 TB/s chip-wide, 1.6 B per minion-cycle; spec (assumed one 64 B beat per NoC cycle per shire port) 3.3 TB/s, 5.33 B per minion-cycle.
measured
aifoundry2, aifoundry3
Ridge points ↗
bw-l3
DRAM streaming: 76 GB/s for the whole chip (0.124 B per minion-cycle), about 64% of the 119 GB/s that 16 x 16-bit channels carry at 3,733 MT/s; about a twentieth of an A100.
measured
aifoundry2, aifoundry3
Ridge points ↗
bw-dram
L1 hit (memhier loop): 0.75 pJ/B [0.62-0.88] above idle, 1 KB tensor loads (L1: 32 B vector loads) by every minion at 600 MHz; per card a2 0.77, a3 0.75, a1c1 0.72.
measured
three cards
The energy manual ↗
e-l1
L2 cache: 3.11 pJ/B [1.42-4.99] above idle, 1 KB tensor loads (L1: 32 B vector loads) by every minion at 600 MHz; per card a2 2.64, a3 2.83, a1c1 3.86.
measured
three cards
The energy manual ↗
e-l2
Own scratchpad filled with zeros: 2.25 pJ/B [2.06-2.61] above idle, 1 KB tensor loads (L1: 32 B vector loads) by every minion at 600 MHz; per card a2 2.11, a3 2.10, a1c1 2.55.
measured
three cards
The energy manual ↗
e-scp-own-zeros
Own scratchpad filled with random data: 4.40 pJ/B [3.94-5.08] above idle, 1 KB tensor loads (L1: 32 B vector loads) by every minion at 600 MHz; per card a2 4.13, a3 4.04, a1c1 5.03.
measured
three cards
The energy manual ↗
e-scp-own-rand
Scratchpad 16 shire IDs away (2.1 hops mean) filled with zeros: 5.10 pJ/B [4.40-6.45] above idle, 1 KB tensor loads (L1: 32 B vector loads) by every minion at 600 MHz; per card a2 5.04, a3 4.55, a1c1 5.71.
measured
three cards
The energy manual ↗
e-scp-remote-zeros
Scratchpad 16 shire IDs away (2.1 hops mean) filled with random data: 11.8 pJ/B [9.5-14.4] above idle, 1 KB tensor loads (L1: 32 B vector loads) by every minion at 600 MHz; per card a2 11.1, a3 10.8, a1c1 13.6.
measured
three cards
The energy manual ↗
e-scp-remote-rand
L3 (over the mesh): 14.7 pJ/B [7.1-20.5] above idle, 1 KB tensor loads (L1: 32 B vector loads) by every minion at 600 MHz; per card a2 12.3, a3 13.5, a1c1 18.4.
measured
three cards
The energy manual ↗
e-l3
DRAM: 114.6 pJ/B [89.0-141.3] above idle, 1 KB tensor loads (L1: 32 B vector loads) by every minion at 600 MHz; per card a2 111.5, a3 105.6, a1c1 126.6.
measured
three cards
The energy manual ↗
e-dram
The mesh routes in dimension order, and a request and its reply take opposite orders: a request goes x first, then y, and a reply y first, then x, on the logical map, so a reply retraces its request's route backwards. Measured on 29 September (E56) with sets of streams between shires chosen so that their streams share one directed link under one order and none under the other: 1 KB tensor loads, whose data travel as replies, fell to 0.54-0.77 of their bandwidth alone when they shared a link under y first and held at 1.00 when they shared one under x first; tensor stores, whose data travel as requests, showed the mirror (0.52-0.76 against 1.00). A shared link carried about 92 GB/s. The same on aifoundry1 card 1 (development), aifoundry3 (the frozen validation) and aifoundry2 (the same frozen test, run as a third card on the evening of 29 September), three passes each.
measured
three cards
no published page yet
L104+}

## flow/B/4
FLOW 2 · LATENCY LADDER
The shire's own scratchpad: … 299 typ.
Replay
More detail and the sources {+

The same load from shire 0, hitting at each level in turn. The L3 home and the scratchpad are 4 hops away in shire 13; memory shire 5 is 4 hops further. Bars are minion cycles at 600 MHz.

 Level pJ/B chip-wide
L1 0.75 14.5 TB/s
L2 read buffer
L2 3.1 (1.4–5.0) 2.45 TB/s
own scratchpad 2.25–4.40 2.46 TB/s
another shire's scratchpad, 2.1 hops mean 5.10–11.8 0.96 TB/s
L3, home 13 15 (7–21) 0.98 TB/s
DRAM 115 (89–141) 76 GB/s

 Another shire's scratchpad was measured with every shire reading the one 16 IDs away, 2.1 hops on average, not at the 4 hops of the ladder. L1 bandwidth is the energy manual's unrolled loop (the memory-hierarchy probe's loop reaches 6.2 TB/s). Energies are above idle, with their range over passes in brackets.

 Measured and explained in The energy manual ↗.

 The facts this flow uses (26): point at one for its source

 L1 data cache hit: 5.25 cycles load-to-use (8.8 ns at 600 MHz); the same on three cards (per-pass ranges 5.247-5.259).
measured
three cards
Memory hierarchy ↗
lat-l1
L2 read buffer (8 clean lines per bank x 4 banks = 2 KB per shire): 36 cycles (60 ns), 11 fewer than the L2 array.
measured
three cards
Memory hierarchy ↗
lat-rb
L2 cache hit (and the shire's own scratchpad): 47 cycles (78 ns); hart 1 pays 3 more (39 read buffer, 50 L2).
measured
three cards
Memory hierarchy ↗
lat-l2
The shire's own L2 scratchpad: 47 cycles (78 ns), the same SRAM, latency and bandwidth as the L2 cache.
measured
three cards
Memory hierarchy ↗
lat-scp-own
Another shire's scratchpad: 99.84 + 12.00 cycles per mesh hop at 600 MHz (112-220 cycles, 186-366 ns over 1-10 hops); all 124 points within 1 cycle, a->b equals b->a within 0.032 cycles.
measured
three cards
Memory hierarchy ↗
lat-scp-remote
L3 hit against distance to the line's home shire: 110.5 + 11.99 cycles per mesh hop (from shire 0), within 4 cycles for 99.4-100% of lines on each card.
measured
three cards
Anatomy of a memory access ↗
lat-l3-hop
L3 hit: 110 + 12 cycles per mesh hop between the requesting shire and the line's home shire (fitted 110.5 + 11.99 on three cards); 159-169 cycles (265-282 ns) on average depending on the requesting shire.
measured
three cards
Anatomy of a memory access ↗
l3.latency
L3 hit from a pointer chase, averaged over all 32 slices: 159-169 cycles at 600 MHz (265-282 ns), by requesting shire: 168.8-168.9 (shire 0), 160.6-160.7 (7), 159.1-159.2 (24), 168.8-168.9 (31).
measured
three cards
Memory hierarchy ↗
lat-l3-avg
Past the L3, the DRAM leg costs 91 + 12 × hops(home shire, memory shire) cycles; about 28 of the 91 are the DRAM chip (activate 11, read latency and two bursts 17) and at most about 63 the L3 home's miss handling and the memory shire. Only about 28 of a ~300-cycle DRAM load are the DRAM's own timing.
measured
three cards
Anatomy of a memory access ↗
dram.leg
A typical DRAM load, timed one at a time: 299 cycles (500 ns), the median of 4,500 loads from shire 0 to random lines; 299 in each of 15 passes on three cards.
measured
three cards
Anatomy of a memory access ↗
lat-dram-typical
DRAM load from a pointer chase: 287-297 cycles at 600 MHz (479-495 ns): 296.6-297.1 from shires 0 and 31, 287.2-288.8 from 7 and 24; about 490 ns, a fifth more than an A100's HBM (405 ns).
measured
three cards
Memory hierarchy ↗
lat-dram
L1 hits, 32 B vector loads by both harts: 14.5 TB/s chip-wide (23.6 B per minion-cycle) in the energy manual's unrolled loop; the memory-hierarchy probe's loop reaches 6.2 TB/s (10 B per minion-cycle). Spec: 32 B per cycle.
measured
three cards (14.5 TB/s); 6.2 TB/s on aifoundry2, aifoundry3
Ridge points ↗
bw-l1
L2 cache, 1 KB tensor loads by every minion: 2.45 TB/s chip-wide, 4.0 B per minion-cycle (128 B per shire-cycle), half the four banks' 256 B per shire-cycle spec.
measured
aifoundry2, aifoundry3
Ridge points ↗
bw-l2
Own-shire scratchpad: 2.46 TB/s chip-wide, 4.0 B per minion-cycle, same as the L2. Tensor stores into it reach 1.23 TB/s (half the read rate).
measured
aifoundry2, aifoundry3 (the read rate); the store rate on three cards
Ridge points ↗
bw-scp-own
Another shire's scratchpad (each shire reading the one 16 IDs away, 2.1 hops on average): 0.96 TB/s chip-wide, 1.56 B per minion-cycle.
measured
aifoundry2, aifoundry3
Ridge points ↗
bw-scp-remote
L3, every minion streaming: 0.98 TB/s chip-wide, 1.6 B per minion-cycle; spec (assumed one 64 B beat per NoC cycle per shire port) 3.3 TB/s, 5.33 B per minion-cycle.
measured
aifoundry2, aifoundry3
Ridge points ↗
bw-l3
DRAM streaming: 76 GB/s for the whole chip (0.124 B per minion-cycle), about 64% of the 119 GB/s that 16 x 16-bit channels carry at 3,733 MT/s; about a twentieth of an A100.
measured
aifoundry2, aifoundry3
Ridge points ↗
bw-dram
L1 hit (memhier loop): 0.75 pJ/B [0.62-0.88] above idle, 1 KB tensor loads (L1: 32 B vector loads) by every minion at 600 MHz; per card a2 0.77, a3 0.75, a1c1 0.72.
measured
three cards
The energy manual ↗
e-l1
L2 cache: 3.11 pJ/B [1.42-4.99] above idle, 1 KB tensor loads (L1: 32 B vector loads) by every minion at 600 MHz; per card a2 2.64, a3 2.83, a1c1 3.86.
measured
three cards
The energy manual ↗
e-l2
Own scratchpad filled with zeros: 2.25 pJ/B [2.06-2.61] above idle, 1 KB tensor loads (L1: 32 B vector loads) by every minion at 600 MHz; per card a2 2.11, a3 2.10, a1c1 2.55.
measured
three cards
The energy manual ↗
e-scp-own-zeros
Own scratchpad filled with random data: 4.40 pJ/B [3.94-5.08] above idle, 1 KB tensor loads (L1: 32 B vector loads) by every minion at 600 MHz; per card a2 4.13, a3 4.04, a1c1 5.03.
measured
three cards
The energy manual ↗
e-scp-own-rand
Scratchpad 16 shire IDs away (2.1 hops mean) filled with zeros: 5.10 pJ/B [4.40-6.45] above idle, 1 KB tensor loads (L1: 32 B vector loads) by every minion at 600 MHz; per card a2 5.04, a3 4.55, a1c1 5.71.
measured
three cards
The energy manual ↗
e-scp-remote-zeros
Scratchpad 16 shire IDs away (2.1 hops mean) filled with random data: 11.8 pJ/B [9.5-14.4] above idle, 1 KB tensor loads (L1: 32 B vector loads) by every minion at 600 MHz; per card a2 11.1, a3 10.8, a1c1 13.6.
measured
three cards
The energy manual ↗
e-scp-remote-rand
L3 (over the mesh): 14.7 pJ/B [7.1-20.5] above idle, 1 KB tensor loads (L1: 32 B vector loads) by every minion at 600 MHz; per card a2 12.3, a3 13.5, a1c1 18.4.
measured
three cards
The energy manual ↗
e-l3
DRAM: 114.6 pJ/B [89.0-141.3] above idle, 1 KB tensor loads (L1: 32 B vector loads) by every minion at 600 MHz; per card a2 111.5, a3 105.6, a1c1 126.6.
measured
three cards
The energy manual ↗
e-dram
The mesh routes in dimension order, and a request and its reply take opposite orders: a request goes x first, then y, and a reply y first, then x, on the logical map, so a reply retraces its request's route backwards. Measured on 29 September (E56) with sets of streams between shires chosen so that their streams share one directed link under one order and none under the other: 1 KB tensor loads, whose data travel as replies, fell to 0.54-0.77 of their bandwidth alone when they shared a link under y first and held at 1.00 when they shared one under x first; tensor stores, whose data travel as requests, showed the mirror (0.52-0.76 against 1.00). A shared link carried about 92 GB/s. The same on aifoundry1 card 1 (development), aifoundry3 (the frozen validation) and aifoundry2 (the same frozen test, run as a third card on the evening of 29 September), three passes each.
measured
three cards
no published page yet
L104+}

## flow/B/5
FLOW 2 · LATENCY LADDER
Shire 13's scratchpad, 4 … 299 typ.
Replay
More detail and the sources {+

The same load from shire 0, hitting at each level in turn. The L3 home and the scratchpad are 4 hops away in shire 13; memory shire 5 is 4 hops further. Bars are minion cycles at 600 MHz.

 Level pJ/B chip-wide
L1 0.75 14.5 TB/s
L2 read buffer
L2 3.1 (1.4–5.0) 2.45 TB/s
own scratchpad 2.25–4.40 2.46 TB/s
another shire's scratchpad, 2.1 hops mean 5.10–11.8 0.96 TB/s
L3, home 13 15 (7–21) 0.98 TB/s
DRAM 115 (89–141) 76 GB/s

 Another shire's scratchpad was measured with every shire reading the one 16 IDs away, 2.1 hops on average, not at the 4 hops of the ladder. L1 bandwidth is the energy manual's unrolled loop (the memory-hierarchy probe's loop reaches 6.2 TB/s). Energies are above idle, with their range over passes in brackets.

 Measured and explained in The energy manual ↗.

 The facts this flow uses (26): point at one for its source

 L1 data cache hit: 5.25 cycles load-to-use (8.8 ns at 600 MHz); the same on three cards (per-pass ranges 5.247-5.259).
measured
three cards
Memory hierarchy ↗
lat-l1
L2 read buffer (8 clean lines per bank x 4 banks = 2 KB per shire): 36 cycles (60 ns), 11 fewer than the L2 array.
measured
three cards
Memory hierarchy ↗
lat-rb
L2 cache hit (and the shire's own scratchpad): 47 cycles (78 ns); hart 1 pays 3 more (39 read buffer, 50 L2).
measured
three cards
Memory hierarchy ↗
lat-l2
The shire's own L2 scratchpad: 47 cycles (78 ns), the same SRAM, latency and bandwidth as the L2 cache.
measured
three cards
Memory hierarchy ↗
lat-scp-own
Another shire's scratchpad: 99.84 + 12.00 cycles per mesh hop at 600 MHz (112-220 cycles, 186-366 ns over 1-10 hops); all 124 points within 1 cycle, a->b equals b->a within 0.032 cycles.
measured
three cards
Memory hierarchy ↗
lat-scp-remote
L3 hit against distance to the line's home shire: 110.5 + 11.99 cycles per mesh hop (from shire 0), within 4 cycles for 99.4-100% of lines on each card.
measured
three cards
Anatomy of a memory access ↗
lat-l3-hop
L3 hit: 110 + 12 cycles per mesh hop between the requesting shire and the line's home shire (fitted 110.5 + 11.99 on three cards); 159-169 cycles (265-282 ns) on average depending on the requesting shire.
measured
three cards
Anatomy of a memory access ↗
l3.latency
L3 hit from a pointer chase, averaged over all 32 slices: 159-169 cycles at 600 MHz (265-282 ns), by requesting shire: 168.8-168.9 (shire 0), 160.6-160.7 (7), 159.1-159.2 (24), 168.8-168.9 (31).
measured
three cards
Memory hierarchy ↗
lat-l3-avg
Past the L3, the DRAM leg costs 91 + 12 × hops(home shire, memory shire) cycles; about 28 of the 91 are the DRAM chip (activate 11, read latency and two bursts 17) and at most about 63 the L3 home's miss handling and the memory shire. Only about 28 of a ~300-cycle DRAM load are the DRAM's own timing.
measured
three cards
Anatomy of a memory access ↗
dram.leg
A typical DRAM load, timed one at a time: 299 cycles (500 ns), the median of 4,500 loads from shire 0 to random lines; 299 in each of 15 passes on three cards.
measured
three cards
Anatomy of a memory access ↗
lat-dram-typical
DRAM load from a pointer chase: 287-297 cycles at 600 MHz (479-495 ns): 296.6-297.1 from shires 0 and 31, 287.2-288.8 from 7 and 24; about 490 ns, a fifth more than an A100's HBM (405 ns).
measured
three cards
Memory hierarchy ↗
lat-dram
L1 hits, 32 B vector loads by both harts: 14.5 TB/s chip-wide (23.6 B per minion-cycle) in the energy manual's unrolled loop; the memory-hierarchy probe's loop reaches 6.2 TB/s (10 B per minion-cycle). Spec: 32 B per cycle.
measured
three cards (14.5 TB/s); 6.2 TB/s on aifoundry2, aifoundry3
Ridge points ↗
bw-l1
L2 cache, 1 KB tensor loads by every minion: 2.45 TB/s chip-wide, 4.0 B per minion-cycle (128 B per shire-cycle), half the four banks' 256 B per shire-cycle spec.
measured
aifoundry2, aifoundry3
Ridge points ↗
bw-l2
Own-shire scratchpad: 2.46 TB/s chip-wide, 4.0 B per minion-cycle, same as the L2. Tensor stores into it reach 1.23 TB/s (half the read rate).
measured
aifoundry2, aifoundry3 (the read rate); the store rate on three cards
Ridge points ↗
bw-scp-own
Another shire's scratchpad (each shire reading the one 16 IDs away, 2.1 hops on average): 0.96 TB/s chip-wide, 1.56 B per minion-cycle.
measured
aifoundry2, aifoundry3
Ridge points ↗
bw-scp-remote
L3, every minion streaming: 0.98 TB/s chip-wide, 1.6 B per minion-cycle; spec (assumed one 64 B beat per NoC cycle per shire port) 3.3 TB/s, 5.33 B per minion-cycle.
measured
aifoundry2, aifoundry3
Ridge points ↗
bw-l3
DRAM streaming: 76 GB/s for the whole chip (0.124 B per minion-cycle), about 64% of the 119 GB/s that 16 x 16-bit channels carry at 3,733 MT/s; about a twentieth of an A100.
measured
aifoundry2, aifoundry3
Ridge points ↗
bw-dram
L1 hit (memhier loop): 0.75 pJ/B [0.62-0.88] above idle, 1 KB tensor loads (L1: 32 B vector loads) by every minion at 600 MHz; per card a2 0.77, a3 0.75, a1c1 0.72.
measured
three cards
The energy manual ↗
e-l1
L2 cache: 3.11 pJ/B [1.42-4.99] above idle, 1 KB tensor loads (L1: 32 B vector loads) by every minion at 600 MHz; per card a2 2.64, a3 2.83, a1c1 3.86.
measured
three cards
The energy manual ↗
e-l2
Own scratchpad filled with zeros: 2.25 pJ/B [2.06-2.61] above idle, 1 KB tensor loads (L1: 32 B vector loads) by every minion at 600 MHz; per card a2 2.11, a3 2.10, a1c1 2.55.
measured
three cards
The energy manual ↗
e-scp-own-zeros
Own scratchpad filled with random data: 4.40 pJ/B [3.94-5.08] above idle, 1 KB tensor loads (L1: 32 B vector loads) by every minion at 600 MHz; per card a2 4.13, a3 4.04, a1c1 5.03.
measured
three cards
The energy manual ↗
e-scp-own-rand
Scratchpad 16 shire IDs away (2.1 hops mean) filled with zeros: 5.10 pJ/B [4.40-6.45] above idle, 1 KB tensor loads (L1: 32 B vector loads) by every minion at 600 MHz; per card a2 5.04, a3 4.55, a1c1 5.71.
measured
three cards
The energy manual ↗
e-scp-remote-zeros
Scratchpad 16 shire IDs away (2.1 hops mean) filled with random data: 11.8 pJ/B [9.5-14.4] above idle, 1 KB tensor loads (L1: 32 B vector loads) by every minion at 600 MHz; per card a2 11.1, a3 10.8, a1c1 13.6.
measured
three cards
The energy manual ↗
e-scp-remote-rand
L3 (over the mesh): 14.7 pJ/B [7.1-20.5] above idle, 1 KB tensor loads (L1: 32 B vector loads) by every minion at 600 MHz; per card a2 12.3, a3 13.5, a1c1 18.4.
measured
three cards
The energy manual ↗
e-l3
DRAM: 114.6 pJ/B [89.0-141.3] above idle, 1 KB tensor loads (L1: 32 B vector loads) by every minion at 600 MHz; per card a2 111.5, a3 105.6, a1c1 126.6.
measured
three cards
The energy manual ↗
e-dram
The mesh routes in dimension order, and a request and its reply take opposite orders: a request goes x first, then y, and a reply y first, then x, on the logical map, so a reply retraces its request's route backwards. Measured on 29 September (E56) with sets of streams between shires chosen so that their streams share one directed link under one order and none under the other: 1 KB tensor loads, whose data travel as replies, fell to 0.54-0.77 of their bandwidth alone when they shared a link under y first and held at 1.00 when they shared one under x first; tensor stores, whose data travel as requests, showed the mirror (0.52-0.76 against 1.00). A shared link carried about 92 GB/s. The same on aifoundry1 card 1 (development), aifoundry3 (the frozen validation) and aifoundry2 (the same frozen test, run as a third card on the evening of 29 September), three passes each.
measured
three cards
no published page yet
L104+}

## flow/B/6
FLOW 2 · LATENCY LADDER
L3 hit in home … 299 typ.
Replay
More detail and the sources {+

The same load from shire 0, hitting at each level in turn. The L3 home and the scratchpad are 4 hops away in shire 13; memory shire 5 is 4 hops further. Bars are minion cycles at 600 MHz.

 Level pJ/B chip-wide
L1 0.75 14.5 TB/s
L2 read buffer
L2 3.1 (1.4–5.0) 2.45 TB/s
own scratchpad 2.25–4.40 2.46 TB/s
another shire's scratchpad, 2.1 hops mean 5.10–11.8 0.96 TB/s
L3, home 13 15 (7–21) 0.98 TB/s
DRAM 115 (89–141) 76 GB/s

 Another shire's scratchpad was measured with every shire reading the one 16 IDs away, 2.1 hops on average, not at the 4 hops of the ladder. L1 bandwidth is the energy manual's unrolled loop (the memory-hierarchy probe's loop reaches 6.2 TB/s). Energies are above idle, with their range over passes in brackets.

 Measured and explained in The energy manual ↗.

 The facts this flow uses (26): point at one for its source

 L1 data cache hit: 5.25 cycles load-to-use (8.8 ns at 600 MHz); the same on three cards (per-pass ranges 5.247-5.259).
measured
three cards
Memory hierarchy ↗
lat-l1
L2 read buffer (8 clean lines per bank x 4 banks = 2 KB per shire): 36 cycles (60 ns), 11 fewer than the L2 array.
measured
three cards
Memory hierarchy ↗
lat-rb
L2 cache hit (and the shire's own scratchpad): 47 cycles (78 ns); hart 1 pays 3 more (39 read buffer, 50 L2).
measured
three cards
Memory hierarchy ↗
lat-l2
The shire's own L2 scratchpad: 47 cycles (78 ns), the same SRAM, latency and bandwidth as the L2 cache.
measured
three cards
Memory hierarchy ↗
lat-scp-own
Another shire's scratchpad: 99.84 + 12.00 cycles per mesh hop at 600 MHz (112-220 cycles, 186-366 ns over 1-10 hops); all 124 points within 1 cycle, a->b equals b->a within 0.032 cycles.
measured
three cards
Memory hierarchy ↗
lat-scp-remote
L3 hit against distance to the line's home shire: 110.5 + 11.99 cycles per mesh hop (from shire 0), within 4 cycles for 99.4-100% of lines on each card.
measured
three cards
Anatomy of a memory access ↗
lat-l3-hop
L3 hit: 110 + 12 cycles per mesh hop between the requesting shire and the line's home shire (fitted 110.5 + 11.99 on three cards); 159-169 cycles (265-282 ns) on average depending on the requesting shire.
measured
three cards
Anatomy of a memory access ↗
l3.latency
L3 hit from a pointer chase, averaged over all 32 slices: 159-169 cycles at 600 MHz (265-282 ns), by requesting shire: 168.8-168.9 (shire 0), 160.6-160.7 (7), 159.1-159.2 (24), 168.8-168.9 (31).
measured
three cards
Memory hierarchy ↗
lat-l3-avg
Past the L3, the DRAM leg costs 91 + 12 × hops(home shire, memory shire) cycles; about 28 of the 91 are the DRAM chip (activate 11, read latency and two bursts 17) and at most about 63 the L3 home's miss handling and the memory shire. Only about 28 of a ~300-cycle DRAM load are the DRAM's own timing.
measured
three cards
Anatomy of a memory access ↗
dram.leg
A typical DRAM load, timed one at a time: 299 cycles (500 ns), the median of 4,500 loads from shire 0 to random lines; 299 in each of 15 passes on three cards.
measured
three cards
Anatomy of a memory access ↗
lat-dram-typical
DRAM load from a pointer chase: 287-297 cycles at 600 MHz (479-495 ns): 296.6-297.1 from shires 0 and 31, 287.2-288.8 from 7 and 24; about 490 ns, a fifth more than an A100's HBM (405 ns).
measured
three cards
Memory hierarchy ↗
lat-dram
L1 hits, 32 B vector loads by both harts: 14.5 TB/s chip-wide (23.6 B per minion-cycle) in the energy manual's unrolled loop; the memory-hierarchy probe's loop reaches 6.2 TB/s (10 B per minion-cycle). Spec: 32 B per cycle.
measured
three cards (14.5 TB/s); 6.2 TB/s on aifoundry2, aifoundry3
Ridge points ↗
bw-l1
L2 cache, 1 KB tensor loads by every minion: 2.45 TB/s chip-wide, 4.0 B per minion-cycle (128 B per shire-cycle), half the four banks' 256 B per shire-cycle spec.
measured
aifoundry2, aifoundry3
Ridge points ↗
bw-l2
Own-shire scratchpad: 2.46 TB/s chip-wide, 4.0 B per minion-cycle, same as the L2. Tensor stores into it reach 1.23 TB/s (half the read rate).
measured
aifoundry2, aifoundry3 (the read rate); the store rate on three cards
Ridge points ↗
bw-scp-own
Another shire's scratchpad (each shire reading the one 16 IDs away, 2.1 hops on average): 0.96 TB/s chip-wide, 1.56 B per minion-cycle.
measured
aifoundry2, aifoundry3
Ridge points ↗
bw-scp-remote
L3, every minion streaming: 0.98 TB/s chip-wide, 1.6 B per minion-cycle; spec (assumed one 64 B beat per NoC cycle per shire port) 3.3 TB/s, 5.33 B per minion-cycle.
measured
aifoundry2, aifoundry3
Ridge points ↗
bw-l3
DRAM streaming: 76 GB/s for the whole chip (0.124 B per minion-cycle), about 64% of the 119 GB/s that 16 x 16-bit channels carry at 3,733 MT/s; about a twentieth of an A100.
measured
aifoundry2, aifoundry3
Ridge points ↗
bw-dram
L1 hit (memhier loop): 0.75 pJ/B [0.62-0.88] above idle, 1 KB tensor loads (L1: 32 B vector loads) by every minion at 600 MHz; per card a2 0.77, a3 0.75, a1c1 0.72.
measured
three cards
The energy manual ↗
e-l1
L2 cache: 3.11 pJ/B [1.42-4.99] above idle, 1 KB tensor loads (L1: 32 B vector loads) by every minion at 600 MHz; per card a2 2.64, a3 2.83, a1c1 3.86.
measured
three cards
The energy manual ↗
e-l2
Own scratchpad filled with zeros: 2.25 pJ/B [2.06-2.61] above idle, 1 KB tensor loads (L1: 32 B vector loads) by every minion at 600 MHz; per card a2 2.11, a3 2.10, a1c1 2.55.
measured
three cards
The energy manual ↗
e-scp-own-zeros
Own scratchpad filled with random data: 4.40 pJ/B [3.94-5.08] above idle, 1 KB tensor loads (L1: 32 B vector loads) by every minion at 600 MHz; per card a2 4.13, a3 4.04, a1c1 5.03.
measured
three cards
The energy manual ↗
e-scp-own-rand
Scratchpad 16 shire IDs away (2.1 hops mean) filled with zeros: 5.10 pJ/B [4.40-6.45] above idle, 1 KB tensor loads (L1: 32 B vector loads) by every minion at 600 MHz; per card a2 5.04, a3 4.55, a1c1 5.71.
measured
three cards
The energy manual ↗
e-scp-remote-zeros
Scratchpad 16 shire IDs away (2.1 hops mean) filled with random data: 11.8 pJ/B [9.5-14.4] above idle, 1 KB tensor loads (L1: 32 B vector loads) by every minion at 600 MHz; per card a2 11.1, a3 10.8, a1c1 13.6.
measured
three cards
The energy manual ↗
e-scp-remote-rand
L3 (over the mesh): 14.7 pJ/B [7.1-20.5] above idle, 1 KB tensor loads (L1: 32 B vector loads) by every minion at 600 MHz; per card a2 12.3, a3 13.5, a1c1 18.4.
measured
three cards
The energy manual ↗
e-l3
DRAM: 114.6 pJ/B [89.0-141.3] above idle, 1 KB tensor loads (L1: 32 B vector loads) by every minion at 600 MHz; per card a2 111.5, a3 105.6, a1c1 126.6.
measured
three cards
The energy manual ↗
e-dram
The mesh routes in dimension order, and a request and its reply take opposite orders: a request goes x first, then y, and a reply y first, then x, on the logical map, so a reply retraces its request's route backwards. Measured on 29 September (E56) with sets of streams between shires chosen so that their streams share one directed link under one order and none under the other: 1 KB tensor loads, whose data travel as replies, fell to 0.54-0.77 of their bandwidth alone when they shared a link under y first and held at 1.00 when they shared one under x first; tensor stores, whose data travel as requests, showed the mirror (0.52-0.76 against 1.00). A shared link carried about 92 GB/s. The same on aifoundry1 card 1 (development), aifoundry3 (the frozen validation) and aifoundry2 (the same frozen test, run as a third card on the evening of 29 September), three passes each.
measured
three cards
no published page yet
L104+}

## flow/C/0
FLOW 3 · TENSORSEND
Shire 0 → shire 24: … the round trip.

 More detail and the sources {+

A hart sends 32 B of vector registers to a minion in another shire and waits for the reply. The round trip is 150 cycles to leave and re-enter the shires plus 12.02 per hop, on all three cards. The energy, measured with 1 KB messages, is 9.2 pJ/B to leave the shire plus 1.75 pJ/B per mean hop.

 From → to hops cycles ns
shire 0 → 24 1 162 270
shire 0 → 13 4 198 330
shire 0 → 31 10 270 450
shire 8 → 23 8 246 410

 Inside a shire the same round trip is 68 cycles on a tree edge and 114–115 cycles otherwise. The reply is the partner's own TensorSend back, drawn like the first as a request, x first: the mesh takes a request x first and a load's reply y first (measured on three cards); whether a TensorSend travels as a request was not tested.

 Measured and explained in On-chip communication ↗.

 The facts this flow uses (13): point at one for its source

 TensorSend round trip between shires, 32 B: 150 + 12.02 cycles per mesh hop (250 ns + 20 ns/hop), worst residual 1.1-1.4 cycles over all 496 shire pairs; 1 KB messages add 12 cycles per hop to 5 hops and 36 beyond.
measured
three cards
On-chip communication ↗
ts-rt-mesh
TensorSend 32 B round trip between shires = 150 + 12.02 × (Manhattan hops) cycles at 600 MHz, worst residual 1.1–1.4 cycles over all 496 pairs, on each of three cards.
measured
three cards
On-chip communication ↗
L70
Intercept of the between-shire round trip: 150 cycles (the fixed cost of leaving and re-entering shires).
measured
three cards
On-chip communication ↗
L71
Each mesh hop adds 20 ns round trip: 12 minion cycles at 600 MHz, 16 at 800; a hop is 20 ns at either clock. In time, 250 ns + 20 ns per hop across shires, r² 0.9999 over 496 pairs.
measured
three cards
On-chip communication ↗
L72
TensorSend moves COUNT consecutive vector registers (32 B each, up to 127, wrapping past f31: about 4 KB) from the issuing hart into hart 0 of a target minion anywhere on the chip; the receiver's TensorRecv can add, max or min the data into its registers at no extra cost.
documented
On-chip communication ↗
minion.tensorsend
TensorSend across the mesh: 9.2 pJ/B to leave the shire plus 1.75 pJ/B per mean hop (three cards pooled; a2 9.1 + 1.8, a3 8.0 + 1.7, a1c1 10.4 + 1.7); no card's per-hop cost differs from another's.
model
three cards
On-chip communication ↗
mesh-hop-ring
Ring energy slope per mean hop by card: aifoundry2 1.78 [1.31–2.25], aifoundry3 1.73 [0.48–2.97], aifoundry1 card 1 1.74 [0.95–2.53] pJ/B (99% intervals, 6 passes each); no pair of cards differs; pooled 1.75, 1.40–2.10 at 99% over the 18 passes (±20%).
measured
three cards
On-chip communication ↗
L86
Inside a shire, messaging costs 0.7–2.2 pJ per byte with 1 KB messages, busy cores included; a byte costs 6–26× more once it crosses the shire boundary.
measured
three cards
On-chip communication ↗
L87
TensorSend between shires: 87-156 GB/s chip-wide over six shire-to-shire ring patterns (0.25 B per minion-cycle at best): 7-34x less message bandwidth than inside a shire.
measured
aifoundry2
On-chip communication ↗
bw-tsend-mesh
One TensorSend link, 1 KB messages: 5.3 GB/s on the fast local network, 2.9 through the shire crossbar, 2.7 over one mesh hop, 1.8 over 10 hops (the three cards agree to the digits).
measured
three cards
On-chip communication ↗
bw-tsend-link
With 1 KB messages a round trip adds 12 cycles per hop up to 5 hops and 36 cycles (27-36) per hop beyond, as if the sender had a limited number of packets in flight.
measured
three cards
On-chip communication ↗
mesh.1kb-knee
The hardware keeps one peer-to-peer ready bit per minion, not one per partner: if a minion that TensorSends to two partners gets both their readies before it has used the first, one is lost, and that receiver and its sender hang for good (the card then needs a reset).
documented
On-chip communication ↗
minion.one-ready-bit
The mesh routes in dimension order, and a request and its reply take opposite orders: a request goes x first, then y, and a reply y first, then x, on the logical map, so a reply retraces its request's route backwards. Measured on 29 September (E56) with sets of streams between shires chosen so that their streams share one directed link under one order and none under the other: 1 KB tensor loads, whose data travel as replies, fell to 0.54-0.77 of their bandwidth alone when they shared a link under y first and held at 1.00 when they shared one under x first; tensor stores, whose data travel as requests, showed the mirror (0.52-0.76 against 1.00). A shared link carried about 92 GB/s. The same on aifoundry1 card 1 (development), aifoundry3 (the frozen validation) and aifoundry2 (the same frozen test, run as a third card on the evening of 29 September), three passes each.
measured
three cards
no published page yet
L104+}

## flow/C/1
FLOW 3 · TENSORSEND
Shire 0 → shire 24: … the round trip.

 More detail and the sources {+

A hart sends 32 B of vector registers to a minion in another shire and waits for the reply. The round trip is 150 cycles to leave and re-enter the shires plus 12.02 per hop, on all three cards. The energy, measured with 1 KB messages, is 9.2 pJ/B to leave the shire plus 1.75 pJ/B per mean hop.

 From → to hops cycles ns
shire 0 → 24 1 162 270
shire 0 → 13 4 198 330
shire 0 → 31 10 270 450
shire 8 → 23 8 246 410

 Inside a shire the same round trip is 68 cycles on a tree edge and 114–115 cycles otherwise. The reply is the partner's own TensorSend back, drawn like the first as a request, x first: the mesh takes a request x first and a load's reply y first (measured on three cards); whether a TensorSend travels as a request was not tested.

 Measured and explained in On-chip communication ↗.

 The facts this flow uses (13): point at one for its source

 TensorSend round trip between shires, 32 B: 150 + 12.02 cycles per mesh hop (250 ns + 20 ns/hop), worst residual 1.1-1.4 cycles over all 496 shire pairs; 1 KB messages add 12 cycles per hop to 5 hops and 36 beyond.
measured
three cards
On-chip communication ↗
ts-rt-mesh
TensorSend 32 B round trip between shires = 150 + 12.02 × (Manhattan hops) cycles at 600 MHz, worst residual 1.1–1.4 cycles over all 496 pairs, on each of three cards.
measured
three cards
On-chip communication ↗
L70
Intercept of the between-shire round trip: 150 cycles (the fixed cost of leaving and re-entering shires).
measured
three cards
On-chip communication ↗
L71
Each mesh hop adds 20 ns round trip: 12 minion cycles at 600 MHz, 16 at 800; a hop is 20 ns at either clock. In time, 250 ns + 20 ns per hop across shires, r² 0.9999 over 496 pairs.
measured
three cards
On-chip communication ↗
L72
TensorSend moves COUNT consecutive vector registers (32 B each, up to 127, wrapping past f31: about 4 KB) from the issuing hart into hart 0 of a target minion anywhere on the chip; the receiver's TensorRecv can add, max or min the data into its registers at no extra cost.
documented
On-chip communication ↗
minion.tensorsend
TensorSend across the mesh: 9.2 pJ/B to leave the shire plus 1.75 pJ/B per mean hop (three cards pooled; a2 9.1 + 1.8, a3 8.0 + 1.7, a1c1 10.4 + 1.7); no card's per-hop cost differs from another's.
model
three cards
On-chip communication ↗
mesh-hop-ring
Ring energy slope per mean hop by card: aifoundry2 1.78 [1.31–2.25], aifoundry3 1.73 [0.48–2.97], aifoundry1 card 1 1.74 [0.95–2.53] pJ/B (99% intervals, 6 passes each); no pair of cards differs; pooled 1.75, 1.40–2.10 at 99% over the 18 passes (±20%).
measured
three cards
On-chip communication ↗
L86
Inside a shire, messaging costs 0.7–2.2 pJ per byte with 1 KB messages, busy cores included; a byte costs 6–26× more once it crosses the shire boundary.
measured
three cards
On-chip communication ↗
L87
TensorSend between shires: 87-156 GB/s chip-wide over six shire-to-shire ring patterns (0.25 B per minion-cycle at best): 7-34x less message bandwidth than inside a shire.
measured
aifoundry2
On-chip communication ↗
bw-tsend-mesh
One TensorSend link, 1 KB messages: 5.3 GB/s on the fast local network, 2.9 through the shire crossbar, 2.7 over one mesh hop, 1.8 over 10 hops (the three cards agree to the digits).
measured
three cards
On-chip communication ↗
bw-tsend-link
With 1 KB messages a round trip adds 12 cycles per hop up to 5 hops and 36 cycles (27-36) per hop beyond, as if the sender had a limited number of packets in flight.
measured
three cards
On-chip communication ↗
mesh.1kb-knee
The hardware keeps one peer-to-peer ready bit per minion, not one per partner: if a minion that TensorSends to two partners gets both their readies before it has used the first, one is lost, and that receiver and its sender hang for good (the card then needs a reset).
documented
On-chip communication ↗
minion.one-ready-bit
The mesh routes in dimension order, and a request and its reply take opposite orders: a request goes x first, then y, and a reply y first, then x, on the logical map, so a reply retraces its request's route backwards. Measured on 29 September (E56) with sets of streams between shires chosen so that their streams share one directed link under one order and none under the other: 1 KB tensor loads, whose data travel as replies, fell to 0.54-0.77 of their bandwidth alone when they shared a link under y first and held at 1.00 when they shared one under x first; tensor stores, whose data travel as requests, showed the mirror (0.52-0.76 against 1.00). A shared link carried about 92 GB/s. The same on aifoundry1 card 1 (development), aifoundry3 (the frozen validation) and aifoundry2 (the same frozen test, run as a third card on the evening of 29 September), three passes each.
measured
three cards
no published page yet
L104+}

## flow/C/2
FLOW 3 · TENSORSEND
Shire 0 → shire 13: … the round trip.

 More detail and the sources {+

A hart sends 32 B of vector registers to a minion in another shire and waits for the reply. The round trip is 150 cycles to leave and re-enter the shires plus 12.02 per hop, on all three cards. The energy, measured with 1 KB messages, is 9.2 pJ/B to leave the shire plus 1.75 pJ/B per mean hop.

 From → to hops cycles ns
shire 0 → 24 1 162 270
shire 0 → 13 4 198 330
shire 0 → 31 10 270 450
shire 8 → 23 8 246 410

 Inside a shire the same round trip is 68 cycles on a tree edge and 114–115 cycles otherwise. The reply is the partner's own TensorSend back, drawn like the first as a request, x first: the mesh takes a request x first and a load's reply y first (measured on three cards); whether a TensorSend travels as a request was not tested.

 Measured and explained in On-chip communication ↗.

 The facts this flow uses (13): point at one for its source

 TensorSend round trip between shires, 32 B: 150 + 12.02 cycles per mesh hop (250 ns + 20 ns/hop), worst residual 1.1-1.4 cycles over all 496 shire pairs; 1 KB messages add 12 cycles per hop to 5 hops and 36 beyond.
measured
three cards
On-chip communication ↗
ts-rt-mesh
TensorSend 32 B round trip between shires = 150 + 12.02 × (Manhattan hops) cycles at 600 MHz, worst residual 1.1–1.4 cycles over all 496 pairs, on each of three cards.
measured
three cards
On-chip communication ↗
L70
Intercept of the between-shire round trip: 150 cycles (the fixed cost of leaving and re-entering shires).
measured
three cards
On-chip communication ↗
L71
Each mesh hop adds 20 ns round trip: 12 minion cycles at 600 MHz, 16 at 800; a hop is 20 ns at either clock. In time, 250 ns + 20 ns per hop across shires, r² 0.9999 over 496 pairs.
measured
three cards
On-chip communication ↗
L72
TensorSend moves COUNT consecutive vector registers (32 B each, up to 127, wrapping past f31: about 4 KB) from the issuing hart into hart 0 of a target minion anywhere on the chip; the receiver's TensorRecv can add, max or min the data into its registers at no extra cost.
documented
On-chip communication ↗
minion.tensorsend
TensorSend across the mesh: 9.2 pJ/B to leave the shire plus 1.75 pJ/B per mean hop (three cards pooled; a2 9.1 + 1.8, a3 8.0 + 1.7, a1c1 10.4 + 1.7); no card's per-hop cost differs from another's.
model
three cards
On-chip communication ↗
mesh-hop-ring
Ring energy slope per mean hop by card: aifoundry2 1.78 [1.31–2.25], aifoundry3 1.73 [0.48–2.97], aifoundry1 card 1 1.74 [0.95–2.53] pJ/B (99% intervals, 6 passes each); no pair of cards differs; pooled 1.75, 1.40–2.10 at 99% over the 18 passes (±20%).
measured
three cards
On-chip communication ↗
L86
Inside a shire, messaging costs 0.7–2.2 pJ per byte with 1 KB messages, busy cores included; a byte costs 6–26× more once it crosses the shire boundary.
measured
three cards
On-chip communication ↗
L87
TensorSend between shires: 87-156 GB/s chip-wide over six shire-to-shire ring patterns (0.25 B per minion-cycle at best): 7-34x less message bandwidth than inside a shire.
measured
aifoundry2
On-chip communication ↗
bw-tsend-mesh
One TensorSend link, 1 KB messages: 5.3 GB/s on the fast local network, 2.9 through the shire crossbar, 2.7 over one mesh hop, 1.8 over 10 hops (the three cards agree to the digits).
measured
three cards
On-chip communication ↗
bw-tsend-link
With 1 KB messages a round trip adds 12 cycles per hop up to 5 hops and 36 cycles (27-36) per hop beyond, as if the sender had a limited number of packets in flight.
measured
three cards
On-chip communication ↗
mesh.1kb-knee
The hardware keeps one peer-to-peer ready bit per minion, not one per partner: if a minion that TensorSends to two partners gets both their readies before it has used the first, one is lost, and that receiver and its sender hang for good (the card then needs a reset).
documented
On-chip communication ↗
minion.one-ready-bit
The mesh routes in dimension order, and a request and its reply take opposite orders: a request goes x first, then y, and a reply y first, then x, on the logical map, so a reply retraces its request's route backwards. Measured on 29 September (E56) with sets of streams between shires chosen so that their streams share one directed link under one order and none under the other: 1 KB tensor loads, whose data travel as replies, fell to 0.54-0.77 of their bandwidth alone when they shared a link under y first and held at 1.00 when they shared one under x first; tensor stores, whose data travel as requests, showed the mirror (0.52-0.76 against 1.00). A shared link carried about 92 GB/s. The same on aifoundry1 card 1 (development), aifoundry3 (the frozen validation) and aifoundry2 (the same frozen test, run as a third card on the evening of 29 September), three passes each.
measured
three cards
no published page yet
L104+}

## flow/C/3
FLOW 3 · TENSORSEND
Shire 0 → shire 31: … the round trip.

 More detail and the sources {+

A hart sends 32 B of vector registers to a minion in another shire and waits for the reply. The round trip is 150 cycles to leave and re-enter the shires plus 12.02 per hop, on all three cards. The energy, measured with 1 KB messages, is 9.2 pJ/B to leave the shire plus 1.75 pJ/B per mean hop.

 From → to hops cycles ns
shire 0 → 24 1 162 270
shire 0 → 13 4 198 330
shire 0 → 31 10 270 450
shire 8 → 23 8 246 410

 Inside a shire the same round trip is 68 cycles on a tree edge and 114–115 cycles otherwise. The reply is the partner's own TensorSend back, drawn like the first as a request, x first: the mesh takes a request x first and a load's reply y first (measured on three cards); whether a TensorSend travels as a request was not tested.

 Measured and explained in On-chip communication ↗.

 The facts this flow uses (13): point at one for its source

 TensorSend round trip between shires, 32 B: 150 + 12.02 cycles per mesh hop (250 ns + 20 ns/hop), worst residual 1.1-1.4 cycles over all 496 shire pairs; 1 KB messages add 12 cycles per hop to 5 hops and 36 beyond.
measured
three cards
On-chip communication ↗
ts-rt-mesh
TensorSend 32 B round trip between shires = 150 + 12.02 × (Manhattan hops) cycles at 600 MHz, worst residual 1.1–1.4 cycles over all 496 pairs, on each of three cards.
measured
three cards
On-chip communication ↗
L70
Intercept of the between-shire round trip: 150 cycles (the fixed cost of leaving and re-entering shires).
measured
three cards
On-chip communication ↗
L71
Each mesh hop adds 20 ns round trip: 12 minion cycles at 600 MHz, 16 at 800; a hop is 20 ns at either clock. In time, 250 ns + 20 ns per hop across shires, r² 0.9999 over 496 pairs.
measured
three cards
On-chip communication ↗
L72
TensorSend moves COUNT consecutive vector registers (32 B each, up to 127, wrapping past f31: about 4 KB) from the issuing hart into hart 0 of a target minion anywhere on the chip; the receiver's TensorRecv can add, max or min the data into its registers at no extra cost.
documented
On-chip communication ↗
minion.tensorsend
TensorSend across the mesh: 9.2 pJ/B to leave the shire plus 1.75 pJ/B per mean hop (three cards pooled; a2 9.1 + 1.8, a3 8.0 + 1.7, a1c1 10.4 + 1.7); no card's per-hop cost differs from another's.
model
three cards
On-chip communication ↗
mesh-hop-ring
Ring energy slope per mean hop by card: aifoundry2 1.78 [1.31–2.25], aifoundry3 1.73 [0.48–2.97], aifoundry1 card 1 1.74 [0.95–2.53] pJ/B (99% intervals, 6 passes each); no pair of cards differs; pooled 1.75, 1.40–2.10 at 99% over the 18 passes (±20%).
measured
three cards
On-chip communication ↗
L86
Inside a shire, messaging costs 0.7–2.2 pJ per byte with 1 KB messages, busy cores included; a byte costs 6–26× more once it crosses the shire boundary.
measured
three cards
On-chip communication ↗
L87
TensorSend between shires: 87-156 GB/s chip-wide over six shire-to-shire ring patterns (0.25 B per minion-cycle at best): 7-34x less message bandwidth than inside a shire.
measured
aifoundry2
On-chip communication ↗
bw-tsend-mesh
One TensorSend link, 1 KB messages: 5.3 GB/s on the fast local network, 2.9 through the shire crossbar, 2.7 over one mesh hop, 1.8 over 10 hops (the three cards agree to the digits).
measured
three cards
On-chip communication ↗
bw-tsend-link
With 1 KB messages a round trip adds 12 cycles per hop up to 5 hops and 36 cycles (27-36) per hop beyond, as if the sender had a limited number of packets in flight.
measured
three cards
On-chip communication ↗
mesh.1kb-knee
The hardware keeps one peer-to-peer ready bit per minion, not one per partner: if a minion that TensorSends to two partners gets both their readies before it has used the first, one is lost, and that receiver and its sender hang for good (the card then needs a reset).
documented
On-chip communication ↗
minion.one-ready-bit
The mesh routes in dimension order, and a request and its reply take opposite orders: a request goes x first, then y, and a reply y first, then x, on the logical map, so a reply retraces its request's route backwards. Measured on 29 September (E56) with sets of streams between shires chosen so that their streams share one directed link under one order and none under the other: 1 KB tensor loads, whose data travel as replies, fell to 0.54-0.77 of their bandwidth alone when they shared a link under y first and held at 1.00 when they shared one under x first; tensor stores, whose data travel as requests, showed the mirror (0.52-0.76 against 1.00). A shared link carried about 92 GB/s. The same on aifoundry1 card 1 (development), aifoundry3 (the frozen validation) and aifoundry2 (the same frozen test, run as a third card on the evening of 29 September), three passes each.
measured
three cards
no published page yet
L104+}

## flow/D/0
FLOW 4 · RELAY
Two ways to hand a block of results to the next shire: {+it reads them+} straight [-into its-] {+from this shire's+} scratchpad, or {+they go+} out to DRAM and back
Handing a result to the next shire costs 8.9 pJ per byte {+moved+} against 116.2 through DRAM: about a thirteenth of the energy, … results from one stage of a computation to the next: [-straight into-] the next {+shire reads them straight from this+} shire's memory, or {+they go+} out to the memory chips and back. Straight across is much cheaper.

 Energy per byte [-(write + read)-] {+moved (each write and each read counted)+}

 through DRAM
116.2 pJ/B
to the … in the own scratchpad
4.3 pJ/B

 Bandwidth, {+reads plus writes,+} 8 stages on 1,024 minions

 through DRAM
… scratchpad
1487 GB/s
More detail and the sources {+

A pipeline stage hands its output to the next stage. Through DRAM it writes its output out and reads it back at the next stage, each line through its L3 home and memory shire (one line is drawn, homed in shire 16, served by memory shire 0); on chip it writes its output into its own scratchpad and the next shire reads it from there, so the data cross the mesh as load replies (shire 0 to shire 1 here, 3 hops).

 Next shire against DRAM: 12.9×, 13.0× and 13.1× less energy per byte on the three cards, and 12.4× the bandwidth. The dots on the die are drawn at those relative rates.

 Measured and explained in Hand it to the next shire: on-chip relay vs DRAM ↗.

 The facts this flow uses (13): point at one for its source

 Relay energy per byte moved, each byte counted once when written and once when read: through DRAM 116.2 pJ/B [104.5-135.3], to the next shire, which reads the previous shire's scratchpad, 8.9 [7.6-10.2], in the own scratchpad 4.3 [3.8-5.1]; a hand-off writes every byte once and reads it once, so a byte handed to the next shire costs 17.8 pJ (232 through DRAM).
measured
three cards
Hand it to the next shire: on-chip relay vs DRAM ↗
relay-energy
Handing a slab to the next shire through its scratchpad costs 12.9x, 13.0x and 13.1x less energy per byte than the DRAM round trip (aifoundry2, aifoundry3, aifoundry1-c1): about a thirteenth, the same on every card at 99%.
measured
three cards
Hand it to the next shire: on-chip relay vs DRAM ↗
relay-13x
Relay bandwidth (8 stages, 1,024 minions; bytes read plus bytes written): 47.7 GB/s through DRAM, 592.5 GB/s to the next shire (12.4x), 1487 GB/s in the own scratchpad (aifoundry2 pass means; the other cards within 1.5%).
measured
aifoundry2 pass means (the other cards within 1.5%)
Hand it to the next shire: on-chip relay vs DRAM ↗
relay-bw
A multi-stage pipeline that has the next shire read each stage's output from the producing shire's scratchpad runs about 12.4× faster than one that goes through DRAM (31× keeping it in the own scratchpad), at 116 / 8.9 / 4.3 pJ per byte moved (DRAM / next shire / own).
measured
three cards
Hand it to the next shire: on-chip relay vs DRAM ↗
relay.speedup
Handing a result to the next shire instead of through DRAM: aifoundry2 111.3 vs 8.61 pJ/B, aifoundry3 107.5 vs 8.27, aifoundry1 card 1 129.9 vs 9.89; DRAM ÷ next shire 12.9–13.1× on every card; own scratchpad 4.05–4.86 pJ/B.
measured
three cards
Hand it to the next shire: on-chip relay vs DRAM ↗
L93
In the relay, which shire receives the slab moves bandwidth by up to a quarter: 593 GB/s to the next shire by ID (3.5 hops on average, longest hand-off 10) to 734 GB/s at 16 shire IDs (2.1, longest 6); bandwidth falls with the longest hand-off (r = −0.99), about 3,200–3,300 cycles of stage time per hop of it.
measured
three cards
Hand it to the next shire: on-chip relay vs DRAM ↗
L94
The three relay media draw within a watt of each other over idle (4.34 / 4.42 / 5.30 W for DRAM / next shire / own): the relay's energy saving is time, not power.
measured
aifoundry2
Hand it to the next shire: on-chip relay vs DRAM ↗
relay-watts
DRAM is 30x the energy of the shire's own scratchpad per byte read, and 17x per byte written.
model
three cards
The energy manual ↗
e-dram-vs-scp
Path of a cacheable load: an L1 miss sends Read_L2 over ET-Link to the local bank chosen by PA[7:6]; an L2 miss sends Read_L3 over the to_l3 mesh interface to the home shire's L3 slave chosen by PA[10:6] (data returns straight to the neighbourhood, before the fill); an L3 miss goes over to_sys to the memory shire chosen by PA[8:6], whose controller does activate/read/precharge.
documented
Anatomy of a memory access ↗
addr.load-path
Tensor loads skip the L1 but are cached in the L2 and L3; tensor stores skip the L1 and the L2.
inference
The energy manual ↗
minion.tensor-cache-path
A line's L3 home shire is PA[10:6]: consecutive 64-byte lines rotate over the 32 compute shires' L3 slices (default 'swizzle0'; the firmware leaves the swizzle register at reset).
measured
three cards
Anatomy of a memory access ↗
l3.home
The memory shire serving a line is PA[8:6] (so it is always the L3 home shire's low three bits) and the controller/channel within it is PA[9]: consecutive 64 B lines rotate over the 8 memory shires, the two channels alternate every 512 B.
measured
aifoundry2
Anatomy of a memory access ↗
dram.memshire-select
The mesh routes in dimension order, and a request and its reply take opposite orders: a request goes x first, then y, and a reply y first, then x, on the logical map, so a reply retraces its request's route backwards. Measured on 29 September (E56) with sets of streams between shires chosen so that their streams share one directed link under one order and none under the other: 1 KB tensor loads, whose data travel as replies, fell to 0.54-0.77 of their bandwidth alone when they shared a link under y first and held at 1.00 when they shared one under x first; tensor stores, whose data travel as requests, showed the mirror (0.52-0.76 against 1.00). A shared link carried about 92 GB/s. The same on aifoundry1 card 1 (development), aifoundry3 (the frozen validation) and aifoundry2 (the same frozen test, run as a third card on the evening of 29 September), three passes each.
measured
three cards
no published page yet
L104+}

## flow/D/1
FLOW 4 · RELAY
Two ways to hand a block of results to the next shire: {+it reads them+} straight [-into its-] {+from this shire's+} scratchpad, or {+they go+} out to DRAM and back
Handing a result to the next shire costs 8.9 pJ per byte {+moved+} against 116.2 through DRAM: about a thirteenth of the energy, … results from one stage of a computation to the next: [-straight into-] the next {+shire reads them straight from this+} shire's memory, or {+they go+} out to the memory chips and back. Straight across is much cheaper.

 Energy per byte [-(write + read)-] {+moved (each write and each read counted)+}

 through DRAM
116.2 pJ/B
to the … in the own scratchpad
4.3 pJ/B

 Bandwidth, {+reads plus writes,+} 8 stages on 1,024 minions

 through DRAM
… scratchpad
1487 GB/s
More detail and the sources {+

A pipeline stage hands its output to the next stage. Through DRAM it writes its output out and reads it back at the next stage, each line through its L3 home and memory shire (one line is drawn, homed in shire 16, served by memory shire 0); on chip it writes its output into its own scratchpad and the next shire reads it from there, so the data cross the mesh as load replies (shire 0 to shire 1 here, 3 hops).

 Next shire against DRAM: 12.9×, 13.0× and 13.1× less energy per byte on the three cards, and 12.4× the bandwidth. The dots on the die are drawn at those relative rates.

 Measured and explained in Hand it to the next shire: on-chip relay vs DRAM ↗.

 The facts this flow uses (13): point at one for its source

 Relay energy per byte moved, each byte counted once when written and once when read: through DRAM 116.2 pJ/B [104.5-135.3], to the next shire, which reads the previous shire's scratchpad, 8.9 [7.6-10.2], in the own scratchpad 4.3 [3.8-5.1]; a hand-off writes every byte once and reads it once, so a byte handed to the next shire costs 17.8 pJ (232 through DRAM).
measured
three cards
Hand it to the next shire: on-chip relay vs DRAM ↗
relay-energy
Handing a slab to the next shire through its scratchpad costs 12.9x, 13.0x and 13.1x less energy per byte than the DRAM round trip (aifoundry2, aifoundry3, aifoundry1-c1): about a thirteenth, the same on every card at 99%.
measured
three cards
Hand it to the next shire: on-chip relay vs DRAM ↗
relay-13x
Relay bandwidth (8 stages, 1,024 minions; bytes read plus bytes written): 47.7 GB/s through DRAM, 592.5 GB/s to the next shire (12.4x), 1487 GB/s in the own scratchpad (aifoundry2 pass means; the other cards within 1.5%).
measured
aifoundry2 pass means (the other cards within 1.5%)
Hand it to the next shire: on-chip relay vs DRAM ↗
relay-bw
A multi-stage pipeline that has the next shire read each stage's output from the producing shire's scratchpad runs about 12.4× faster than one that goes through DRAM (31× keeping it in the own scratchpad), at 116 / 8.9 / 4.3 pJ per byte moved (DRAM / next shire / own).
measured
three cards
Hand it to the next shire: on-chip relay vs DRAM ↗
relay.speedup
Handing a result to the next shire instead of through DRAM: aifoundry2 111.3 vs 8.61 pJ/B, aifoundry3 107.5 vs 8.27, aifoundry1 card 1 129.9 vs 9.89; DRAM ÷ next shire 12.9–13.1× on every card; own scratchpad 4.05–4.86 pJ/B.
measured
three cards
Hand it to the next shire: on-chip relay vs DRAM ↗
L93
In the relay, which shire receives the slab moves bandwidth by up to a quarter: 593 GB/s to the next shire by ID (3.5 hops on average, longest hand-off 10) to 734 GB/s at 16 shire IDs (2.1, longest 6); bandwidth falls with the longest hand-off (r = −0.99), about 3,200–3,300 cycles of stage time per hop of it.
measured
three cards
Hand it to the next shire: on-chip relay vs DRAM ↗
L94
The three relay media draw within a watt of each other over idle (4.34 / 4.42 / 5.30 W for DRAM / next shire / own): the relay's energy saving is time, not power.
measured
aifoundry2
Hand it to the next shire: on-chip relay vs DRAM ↗
relay-watts
DRAM is 30x the energy of the shire's own scratchpad per byte read, and 17x per byte written.
model
three cards
The energy manual ↗
e-dram-vs-scp
Path of a cacheable load: an L1 miss sends Read_L2 over ET-Link to the local bank chosen by PA[7:6]; an L2 miss sends Read_L3 over the to_l3 mesh interface to the home shire's L3 slave chosen by PA[10:6] (data returns straight to the neighbourhood, before the fill); an L3 miss goes over to_sys to the memory shire chosen by PA[8:6], whose controller does activate/read/precharge.
documented
Anatomy of a memory access ↗
addr.load-path
Tensor loads skip the L1 but are cached in the L2 and L3; tensor stores skip the L1 and the L2.
inference
The energy manual ↗
minion.tensor-cache-path
A line's L3 home shire is PA[10:6]: consecutive 64-byte lines rotate over the 32 compute shires' L3 slices (default 'swizzle0'; the firmware leaves the swizzle register at reset).
measured
three cards
Anatomy of a memory access ↗
l3.home
The memory shire serving a line is PA[8:6] (so it is always the L3 home shire's low three bits) and the controller/channel within it is PA[9]: consecutive 64 B lines rotate over the 8 memory shires, the two channels alternate every 512 B.
measured
aifoundry2
Anatomy of a memory access ↗
dram.memshire-select
The mesh routes in dimension order, and a request and its reply take opposite orders: a request goes x first, then y, and a reply y first, then x, on the logical map, so a reply retraces its request's route backwards. Measured on 29 September (E56) with sets of streams between shires chosen so that their streams share one directed link under one order and none under the other: 1 KB tensor loads, whose data travel as replies, fell to 0.54-0.77 of their bandwidth alone when they shared a link under y first and held at 1.00 when they shared one under x first; tensor stores, whose data travel as requests, showed the mirror (0.52-0.76 against 1.00). A shared link carried about 92 GB/s. The same on aifoundry1 card 1 (development), aifoundry3 (the frozen validation) and aifoundry2 (the same frozen test, run as a third card on the evening of 29 September), three passes each.
measured
three cards
no published page yet
L104+}

## flow/D/2
FLOW 4 · RELAY
Through DRAM: 116.2 [-pJ/B-] {+pJ per byte moved+} at 47.7 [-GB/s,-] {+GB/s of reads and writes,+} every line to its L3 home and memory shire and back
Handing a result to the next shire costs 8.9 pJ per byte {+moved+} against 116.2 through DRAM: about a thirteenth of the energy, … results from one stage of a computation to the next: [-straight into-] the next {+shire reads them straight from this+} shire's memory, or {+they go+} out to the memory chips and back. Straight across is much cheaper.

 Energy per byte [-(write + read)-] {+moved (each write and each read counted)+}

 through DRAM
116.2 pJ/B
to the … in the own scratchpad
4.3 pJ/B

 Bandwidth, {+reads plus writes,+} 8 stages on 1,024 minions

 through DRAM
… scratchpad
1487 GB/s
More detail and the sources {+

A pipeline stage hands its output to the next stage. Through DRAM it writes its output out and reads it back at the next stage, each line through its L3 home and memory shire (one line is drawn, homed in shire 16, served by memory shire 0); on chip it writes its output into its own scratchpad and the next shire reads it from there, so the data cross the mesh as load replies (shire 0 to shire 1 here, 3 hops).

 Next shire against DRAM: 12.9×, 13.0× and 13.1× less energy per byte on the three cards, and 12.4× the bandwidth. The dots on the die are drawn at those relative rates.

 Measured and explained in Hand it to the next shire: on-chip relay vs DRAM ↗.

 The facts this flow uses (13): point at one for its source

 Relay energy per byte moved, each byte counted once when written and once when read: through DRAM 116.2 pJ/B [104.5-135.3], to the next shire, which reads the previous shire's scratchpad, 8.9 [7.6-10.2], in the own scratchpad 4.3 [3.8-5.1]; a hand-off writes every byte once and reads it once, so a byte handed to the next shire costs 17.8 pJ (232 through DRAM).
measured
three cards
Hand it to the next shire: on-chip relay vs DRAM ↗
relay-energy
Handing a slab to the next shire through its scratchpad costs 12.9x, 13.0x and 13.1x less energy per byte than the DRAM round trip (aifoundry2, aifoundry3, aifoundry1-c1): about a thirteenth, the same on every card at 99%.
measured
three cards
Hand it to the next shire: on-chip relay vs DRAM ↗
relay-13x
Relay bandwidth (8 stages, 1,024 minions; bytes read plus bytes written): 47.7 GB/s through DRAM, 592.5 GB/s to the next shire (12.4x), 1487 GB/s in the own scratchpad (aifoundry2 pass means; the other cards within 1.5%).
measured
aifoundry2 pass means (the other cards within 1.5%)
Hand it to the next shire: on-chip relay vs DRAM ↗
relay-bw
A multi-stage pipeline that has the next shire read each stage's output from the producing shire's scratchpad runs about 12.4× faster than one that goes through DRAM (31× keeping it in the own scratchpad), at 116 / 8.9 / 4.3 pJ per byte moved (DRAM / next shire / own).
measured
three cards
Hand it to the next shire: on-chip relay vs DRAM ↗
relay.speedup
Handing a result to the next shire instead of through DRAM: aifoundry2 111.3 vs 8.61 pJ/B, aifoundry3 107.5 vs 8.27, aifoundry1 card 1 129.9 vs 9.89; DRAM ÷ next shire 12.9–13.1× on every card; own scratchpad 4.05–4.86 pJ/B.
measured
three cards
Hand it to the next shire: on-chip relay vs DRAM ↗
L93
In the relay, which shire receives the slab moves bandwidth by up to a quarter: 593 GB/s to the next shire by ID (3.5 hops on average, longest hand-off 10) to 734 GB/s at 16 shire IDs (2.1, longest 6); bandwidth falls with the longest hand-off (r = −0.99), about 3,200–3,300 cycles of stage time per hop of it.
measured
three cards
Hand it to the next shire: on-chip relay vs DRAM ↗
L94
The three relay media draw within a watt of each other over idle (4.34 / 4.42 / 5.30 W for DRAM / next shire / own): the relay's energy saving is time, not power.
measured
aifoundry2
Hand it to the next shire: on-chip relay vs DRAM ↗
relay-watts
DRAM is 30x the energy of the shire's own scratchpad per byte read, and 17x per byte written.
model
three cards
The energy manual ↗
e-dram-vs-scp
Path of a cacheable load: an L1 miss sends Read_L2 over ET-Link to the local bank chosen by PA[7:6]; an L2 miss sends Read_L3 over the to_l3 mesh interface to the home shire's L3 slave chosen by PA[10:6] (data returns straight to the neighbourhood, before the fill); an L3 miss goes over to_sys to the memory shire chosen by PA[8:6], whose controller does activate/read/precharge.
documented
Anatomy of a memory access ↗
addr.load-path
Tensor loads skip the L1 but are cached in the L2 and L3; tensor stores skip the L1 and the L2.
inference
The energy manual ↗
minion.tensor-cache-path
A line's L3 home shire is PA[10:6]: consecutive 64-byte lines rotate over the 32 compute shires' L3 slices (default 'swizzle0'; the firmware leaves the swizzle register at reset).
measured
three cards
Anatomy of a memory access ↗
l3.home
The memory shire serving a line is PA[8:6] (so it is always the L3 home shire's low three bits) and the controller/channel within it is PA[9]: consecutive 64 B lines rotate over the 8 memory shires, the two channels alternate every 512 B.
measured
aifoundry2
Anatomy of a memory access ↗
dram.memshire-select
The mesh routes in dimension order, and a request and its reply take opposite orders: a request goes x first, then y, and a reply y first, then x, on the logical map, so a reply retraces its request's route backwards. Measured on 29 September (E56) with sets of streams between shires chosen so that their streams share one directed link under one order and none under the other: 1 KB tensor loads, whose data travel as replies, fell to 0.54-0.77 of their bandwidth alone when they shared a link under y first and held at 1.00 when they shared one under x first; tensor stores, whose data travel as requests, showed the mirror (0.52-0.76 against 1.00). A shared link carried about 92 GB/s. The same on aifoundry1 card 1 (development), aifoundry3 (the frozen validation) and aifoundry2 (the same frozen test, run as a third card on the evening of 29 September), three passes each.
measured
three cards
no published page yet
L104+}

## flow/D/3
FLOW 4 · RELAY
To the next shire: 8.9 [-pJ/B-] {+pJ per byte moved+} at 592.5 [-GB/s,-] {+GB/s of reads and writes, read+} straight [-into its-] {+from the previous shire's+} scratchpad
Handing a result to the next shire costs 8.9 pJ per byte {+moved+} against 116.2 through DRAM: about a thirteenth of the energy, … results from one stage of a computation to the next: [-straight into-] the next {+shire reads them straight from this+} shire's memory, or {+they go+} out to the memory chips and back. Straight across is much cheaper.

 Energy per byte [-(write + read)-] {+moved (each write and each read counted)+}

 through DRAM
116.2 pJ/B
to the … in the own scratchpad
4.3 pJ/B

 Bandwidth, {+reads plus writes,+} 8 stages on 1,024 minions

 through DRAM
… scratchpad
1487 GB/s
More detail and the sources {+

A pipeline stage hands its output to the next stage. Through DRAM it writes its output out and reads it back at the next stage, each line through its L3 home and memory shire (one line is drawn, homed in shire 16, served by memory shire 0); on chip it writes its output into its own scratchpad and the next shire reads it from there, so the data cross the mesh as load replies (shire 0 to shire 1 here, 3 hops).

 Next shire against DRAM: 12.9×, 13.0× and 13.1× less energy per byte on the three cards, and 12.4× the bandwidth. The dots on the die are drawn at those relative rates.

 Measured and explained in Hand it to the next shire: on-chip relay vs DRAM ↗.

 The facts this flow uses (13): point at one for its source

 Relay energy per byte moved, each byte counted once when written and once when read: through DRAM 116.2 pJ/B [104.5-135.3], to the next shire, which reads the previous shire's scratchpad, 8.9 [7.6-10.2], in the own scratchpad 4.3 [3.8-5.1]; a hand-off writes every byte once and reads it once, so a byte handed to the next shire costs 17.8 pJ (232 through DRAM).
measured
three cards
Hand it to the next shire: on-chip relay vs DRAM ↗
relay-energy
Handing a slab to the next shire through its scratchpad costs 12.9x, 13.0x and 13.1x less energy per byte than the DRAM round trip (aifoundry2, aifoundry3, aifoundry1-c1): about a thirteenth, the same on every card at 99%.
measured
three cards
Hand it to the next shire: on-chip relay vs DRAM ↗
relay-13x
Relay bandwidth (8 stages, 1,024 minions; bytes read plus bytes written): 47.7 GB/s through DRAM, 592.5 GB/s to the next shire (12.4x), 1487 GB/s in the own scratchpad (aifoundry2 pass means; the other cards within 1.5%).
measured
aifoundry2 pass means (the other cards within 1.5%)
Hand it to the next shire: on-chip relay vs DRAM ↗
relay-bw
A multi-stage pipeline that has the next shire read each stage's output from the producing shire's scratchpad runs about 12.4× faster than one that goes through DRAM (31× keeping it in the own scratchpad), at 116 / 8.9 / 4.3 pJ per byte moved (DRAM / next shire / own).
measured
three cards
Hand it to the next shire: on-chip relay vs DRAM ↗
relay.speedup
Handing a result to the next shire instead of through DRAM: aifoundry2 111.3 vs 8.61 pJ/B, aifoundry3 107.5 vs 8.27, aifoundry1 card 1 129.9 vs 9.89; DRAM ÷ next shire 12.9–13.1× on every card; own scratchpad 4.05–4.86 pJ/B.
measured
three cards
Hand it to the next shire: on-chip relay vs DRAM ↗
L93
In the relay, which shire receives the slab moves bandwidth by up to a quarter: 593 GB/s to the next shire by ID (3.5 hops on average, longest hand-off 10) to 734 GB/s at 16 shire IDs (2.1, longest 6); bandwidth falls with the longest hand-off (r = −0.99), about 3,200–3,300 cycles of stage time per hop of it.
measured
three cards
Hand it to the next shire: on-chip relay vs DRAM ↗
L94
The three relay media draw within a watt of each other over idle (4.34 / 4.42 / 5.30 W for DRAM / next shire / own): the relay's energy saving is time, not power.
measured
aifoundry2
Hand it to the next shire: on-chip relay vs DRAM ↗
relay-watts
DRAM is 30x the energy of the shire's own scratchpad per byte read, and 17x per byte written.
model
three cards
The energy manual ↗
e-dram-vs-scp
Path of a cacheable load: an L1 miss sends Read_L2 over ET-Link to the local bank chosen by PA[7:6]; an L2 miss sends Read_L3 over the to_l3 mesh interface to the home shire's L3 slave chosen by PA[10:6] (data returns straight to the neighbourhood, before the fill); an L3 miss goes over to_sys to the memory shire chosen by PA[8:6], whose controller does activate/read/precharge.
documented
Anatomy of a memory access ↗
addr.load-path
Tensor loads skip the L1 but are cached in the L2 and L3; tensor stores skip the L1 and the L2.
inference
The energy manual ↗
minion.tensor-cache-path
A line's L3 home shire is PA[10:6]: consecutive 64-byte lines rotate over the 32 compute shires' L3 slices (default 'swizzle0'; the firmware leaves the swizzle register at reset).
measured
three cards
Anatomy of a memory access ↗
l3.home
The memory shire serving a line is PA[8:6] (so it is always the L3 home shire's low three bits) and the controller/channel within it is PA[9]: consecutive 64 B lines rotate over the 8 memory shires, the two channels alternate every 512 B.
measured
aifoundry2
Anatomy of a memory access ↗
dram.memshire-select
The mesh routes in dimension order, and a request and its reply take opposite orders: a request goes x first, then y, and a reply y first, then x, on the logical map, so a reply retraces its request's route backwards. Measured on 29 September (E56) with sets of streams between shires chosen so that their streams share one directed link under one order and none under the other: 1 KB tensor loads, whose data travel as replies, fell to 0.54-0.77 of their bandwidth alone when they shared a link under y first and held at 1.00 when they shared one under x first; tensor stores, whose data travel as requests, showed the mirror (0.52-0.76 against 1.00). A shared link carried about 92 GB/s. The same on aifoundry1 card 1 (development), aifoundry3 (the frozen validation) and aifoundry2 (the same frozen test, run as a third card on the evening of 29 September), three passes each.
measured
three cards
no published page yet
L104+}

## flow/E/0
FLOW 5 · GATHERS
Gathers from L1: 21.78 cycles … 2 hops
DRAM
More detail and the sources {+

Both harts of 1,024 minions run the 32-bit gather of 8 lanes (fgw.ps) on scattered lines of a table that fits one level: each visit's 64 elements fall on the 64 lines of one 4 KB tile, the tiles walked in scrambled order. The lanes run at the measured cycles per instruction and count the instructions each has done; the bars are on a log scale, against the leader.

 Table in G el./s pJ/element cycles/instr.
L1 452 12.76 21.78
L2 27.4 354.5 359.3
own scratchpad 27.4 367.8 359.3
scratchpad 2 hops 10.2 903.1 969.0
DRAM 1.19 9,830 8,232

 These are E48's results, measured on 26 September on all three cards; they are on the memory-hierarchy page and in the energy manual (§4.4).

 Measured and explained in Memory hierarchy ↗.

 The facts this flow uses (17): point at one for its source

 Gather (fgw.ps, 32-bit elements) from L1 (512 B table per hart), random lines: 452 G elements/s chip-wide, 12.76 pJ per element [11.89-14.57] (per card: a2 13.54, a3 12.46, a1c1 12.28); 21.78 cycles per instruction per hart.
measured
three cards
Memory hierarchy ↗
gs-g-dram-512B
Gather (fgw.ps, 32-bit elements) from L2 (4 KB table per hart), random lines: 27.4 G elements/s chip-wide, 354.5 pJ per element [329.9-391.6] (per card: a2 343.2, a3 333.1, a1c1 387.1); 359.3 cycles per instruction per hart.
measured
three cards
Memory hierarchy ↗
gs-g-dram-4K
Gather (fgw.ps, 32-bit elements) from own scratchpad (16 KB per hart), random lines: 27.4 G elements/s chip-wide, 367.8 pJ per element [344.3-399.6] (per card: a2 359.6, a3 344.6, a1c1 399.3); 359.3 cycles per instruction per hart.
measured
three cards
Memory hierarchy ↗
gs-g-scp-16K
Gather (fgw.ps, 32-bit elements) from scratchpad 2 hops away (16 KB per hart), random lines: 10.2 G elements/s chip-wide, 903.1 pJ per element [843.1-1,010] (per card: a2 888.7, a3 847.2, a1c1 973.4); 969.0 cycles per instruction per hart.
measured
three cards
Memory hierarchy ↗
gs-g-rscp-16K
Gather (fgw.ps, 32-bit elements) from DRAM (256 KB table per hart), random lines: 1.19 G elements/s chip-wide, 9,830 pJ per element [9,215-10,343] (per card: a2 9,873, a3 9,320, a1c1 10,298); 8,232 cycles per instruction per hart.
measured
three cards
Memory hierarchy ↗
gs-g-dram-256K
Scatter (fscw.ps, 32-bit elements) into L1 (512 B table per hart), random lines: 452 G elements/s chip-wide, 14.69 pJ per element [13.87-15.50] (per card: a2 14.71, a3 14.60, a1c1 14.76); 21.78 cycles per instruction per hart.
measured
three cards
Memory hierarchy ↗
gs-s-dram-512B
Scatter (fscw.ps, 32-bit elements) into L2 (4 KB table per hart), random lines: 23.5 G elements/s chip-wide, 731.5 pJ per element [676.9-813.9] (per card: a2 701.9, a3 679.1, a1c1 813.5); 417.6 cycles per instruction per hart.
measured
three cards
Memory hierarchy ↗
gs-s-dram-4K
Scatter (fscw.ps, 32-bit elements) into own scratchpad (16 KB per hart), random lines: 23.5 G elements/s chip-wide, 690.5 pJ per element [641.9-762.5] (per card: a2 670.6, a3 643.8, a1c1 757.0); 417.5 cycles per instruction per hart.
measured
three cards
Memory hierarchy ↗
gs-s-scp-16K
Scatter (fscw.ps, 32-bit elements) into scratchpad 2 hops away (16 KB per hart), random lines: 10.2 G elements/s chip-wide, 1,983 pJ per element [1,861-2,187] (per card: a2 1,960, a3 1,865, a1c1 2,125); 958.3 cycles per instruction per hart.
measured
three cards
Memory hierarchy ↗
gs-s-rscp-16K
Scatter (fscw.ps, 32-bit elements) into DRAM (256 KB table per hart), random lines: 0.422 G elements/s chip-wide, 23,770 pJ per element [22,209-25,281] (per card: a2 23,640, a3 22,530, a1c1 25,139); 24,584 cycles per instruction per hart (median, pooled over the 9 passes; per card 24,599 on aifoundry2 and aifoundry3, 24,554 on aifoundry1-c1). 2,048 harts × 8 elements at 600 MHz over that is 0.400 G elements/s, about 5% under the measured aggregate rate.
measured
three cards
Memory hierarchy ↗
gs-s-dram-256K
Gathers from L2 and the own scratchpad saturate at 27.36 G elements/s chip-wide on every card, 1.15x the two-miss-handler bound of 23.86 G/s (registered 0.5-2x: PASS); a second hart adds nothing (h2/h1 1.0005).
measured
three cards
Memory hierarchy ↗
gs-mh
Random gathers from DRAM (256 KB per hart) move whole lines at 76.4 GB/s of line traffic, the chip's 76 GB/s DRAM stream, on every card (PASS): 1.19 G useful 4-byte elements/s.
measured
three cards
Memory hierarchy ↗
gs-dram
A 32-bit gather of 8 lanes from L1 (fgw.ps, random, 512 B per hart) takes 10.89 cycles per instruction per minion on every card (registered 7-12: PASS).
measured
three cards
Memory hierarchy ↗
gs-l1
GS-UC failed on all three cards: an L1-bypassing gather (fgwl.ps, random lines from L2, one minion) runs only 1.03x faster with both harts than with one (registered prediction 1.6-2.4x): the second hart adds about 3%.
measured
three cards
Memory hierarchy ↗
gs-uc
Scatter-add alternatives, updates/s and nJ per update: gather + add + scatter in L1 139 G/s at 36 pJ; in DRAM 0.42 G/s at 22.2 nJ; packed atomic famoaddl.pi on a shire table 12.7 G/s at 0.39 nJ; amoaddg.w on a chip table 2.79 G/s at 1.12 nJ.
measured
three cards
Memory hierarchy ↗
gs-add
Card to card, gathers and scatters: elements/s identical (median ratio 1.000); pJ per element aifoundry3/aifoundry2 0.965, aifoundry1-c1/aifoundry2 1.085 (median over 100 configurations).
measured
three cards
Memory hierarchy ↗
gs-card
The mesh routes in dimension order, and a request and its reply take opposite orders: a request goes x first, then y, and a reply y first, then x, on the logical map, so a reply retraces its request's route backwards. Measured on 29 September (E56) with sets of streams between shires chosen so that their streams share one directed link under one order and none under the other: 1 KB tensor loads, whose data travel as replies, fell to 0.54-0.77 of their bandwidth alone when they shared a link under y first and held at 1.00 when they shared one under x first; tensor stores, whose data travel as requests, showed the mirror (0.52-0.76 against 1.00). A shared link carried about 92 GB/s. The same on aifoundry1 card 1 (development), aifoundry3 (the frozen validation) and aifoundry2 (the same frozen test, run as a third card on the evening of 29 September), three passes each.
measured
three cards
no published page yet
L104+}

## flow/E/1
FLOW 5 · GATHERS
Gathers from L1: 21.78 cycles … 2 hops
DRAM
More detail and the sources {+

Both harts of 1,024 minions run the 32-bit gather of 8 lanes (fgw.ps) on scattered lines of a table that fits one level: each visit's 64 elements fall on the 64 lines of one 4 KB tile, the tiles walked in scrambled order. The lanes run at the measured cycles per instruction and count the instructions each has done; the bars are on a log scale, against the leader.

 Table in G el./s pJ/element cycles/instr.
L1 452 12.76 21.78
L2 27.4 354.5 359.3
own scratchpad 27.4 367.8 359.3
scratchpad 2 hops 10.2 903.1 969.0
DRAM 1.19 9,830 8,232

 These are E48's results, measured on 26 September on all three cards; they are on the memory-hierarchy page and in the energy manual (§4.4).

 Measured and explained in Memory hierarchy ↗.

 The facts this flow uses (17): point at one for its source

 Gather (fgw.ps, 32-bit elements) from L1 (512 B table per hart), random lines: 452 G elements/s chip-wide, 12.76 pJ per element [11.89-14.57] (per card: a2 13.54, a3 12.46, a1c1 12.28); 21.78 cycles per instruction per hart.
measured
three cards
Memory hierarchy ↗
gs-g-dram-512B
Gather (fgw.ps, 32-bit elements) from L2 (4 KB table per hart), random lines: 27.4 G elements/s chip-wide, 354.5 pJ per element [329.9-391.6] (per card: a2 343.2, a3 333.1, a1c1 387.1); 359.3 cycles per instruction per hart.
measured
three cards
Memory hierarchy ↗
gs-g-dram-4K
Gather (fgw.ps, 32-bit elements) from own scratchpad (16 KB per hart), random lines: 27.4 G elements/s chip-wide, 367.8 pJ per element [344.3-399.6] (per card: a2 359.6, a3 344.6, a1c1 399.3); 359.3 cycles per instruction per hart.
measured
three cards
Memory hierarchy ↗
gs-g-scp-16K
Gather (fgw.ps, 32-bit elements) from scratchpad 2 hops away (16 KB per hart), random lines: 10.2 G elements/s chip-wide, 903.1 pJ per element [843.1-1,010] (per card: a2 888.7, a3 847.2, a1c1 973.4); 969.0 cycles per instruction per hart.
measured
three cards
Memory hierarchy ↗
gs-g-rscp-16K
Gather (fgw.ps, 32-bit elements) from DRAM (256 KB table per hart), random lines: 1.19 G elements/s chip-wide, 9,830 pJ per element [9,215-10,343] (per card: a2 9,873, a3 9,320, a1c1 10,298); 8,232 cycles per instruction per hart.
measured
three cards
Memory hierarchy ↗
gs-g-dram-256K
Scatter (fscw.ps, 32-bit elements) into L1 (512 B table per hart), random lines: 452 G elements/s chip-wide, 14.69 pJ per element [13.87-15.50] (per card: a2 14.71, a3 14.60, a1c1 14.76); 21.78 cycles per instruction per hart.
measured
three cards
Memory hierarchy ↗
gs-s-dram-512B
Scatter (fscw.ps, 32-bit elements) into L2 (4 KB table per hart), random lines: 23.5 G elements/s chip-wide, 731.5 pJ per element [676.9-813.9] (per card: a2 701.9, a3 679.1, a1c1 813.5); 417.6 cycles per instruction per hart.
measured
three cards
Memory hierarchy ↗
gs-s-dram-4K
Scatter (fscw.ps, 32-bit elements) into own scratchpad (16 KB per hart), random lines: 23.5 G elements/s chip-wide, 690.5 pJ per element [641.9-762.5] (per card: a2 670.6, a3 643.8, a1c1 757.0); 417.5 cycles per instruction per hart.
measured
three cards
Memory hierarchy ↗
gs-s-scp-16K
Scatter (fscw.ps, 32-bit elements) into scratchpad 2 hops away (16 KB per hart), random lines: 10.2 G elements/s chip-wide, 1,983 pJ per element [1,861-2,187] (per card: a2 1,960, a3 1,865, a1c1 2,125); 958.3 cycles per instruction per hart.
measured
three cards
Memory hierarchy ↗
gs-s-rscp-16K
Scatter (fscw.ps, 32-bit elements) into DRAM (256 KB table per hart), random lines: 0.422 G elements/s chip-wide, 23,770 pJ per element [22,209-25,281] (per card: a2 23,640, a3 22,530, a1c1 25,139); 24,584 cycles per instruction per hart (median, pooled over the 9 passes; per card 24,599 on aifoundry2 and aifoundry3, 24,554 on aifoundry1-c1). 2,048 harts × 8 elements at 600 MHz over that is 0.400 G elements/s, about 5% under the measured aggregate rate.
measured
three cards
Memory hierarchy ↗
gs-s-dram-256K
Gathers from L2 and the own scratchpad saturate at 27.36 G elements/s chip-wide on every card, 1.15x the two-miss-handler bound of 23.86 G/s (registered 0.5-2x: PASS); a second hart adds nothing (h2/h1 1.0005).
measured
three cards
Memory hierarchy ↗
gs-mh
Random gathers from DRAM (256 KB per hart) move whole lines at 76.4 GB/s of line traffic, the chip's 76 GB/s DRAM stream, on every card (PASS): 1.19 G useful 4-byte elements/s.
measured
three cards
Memory hierarchy ↗
gs-dram
A 32-bit gather of 8 lanes from L1 (fgw.ps, random, 512 B per hart) takes 10.89 cycles per instruction per minion on every card (registered 7-12: PASS).
measured
three cards
Memory hierarchy ↗
gs-l1
GS-UC failed on all three cards: an L1-bypassing gather (fgwl.ps, random lines from L2, one minion) runs only 1.03x faster with both harts than with one (registered prediction 1.6-2.4x): the second hart adds about 3%.
measured
three cards
Memory hierarchy ↗
gs-uc
Scatter-add alternatives, updates/s and nJ per update: gather + add + scatter in L1 139 G/s at 36 pJ; in DRAM 0.42 G/s at 22.2 nJ; packed atomic famoaddl.pi on a shire table 12.7 G/s at 0.39 nJ; amoaddg.w on a chip table 2.79 G/s at 1.12 nJ.
measured
three cards
Memory hierarchy ↗
gs-add
Card to card, gathers and scatters: elements/s identical (median ratio 1.000); pJ per element aifoundry3/aifoundry2 0.965, aifoundry1-c1/aifoundry2 1.085 (median over 100 configurations).
measured
three cards
Memory hierarchy ↗
gs-card
The mesh routes in dimension order, and a request and its reply take opposite orders: a request goes x first, then y, and a reply y first, then x, on the logical map, so a reply retraces its request's route backwards. Measured on 29 September (E56) with sets of streams between shires chosen so that their streams share one directed link under one order and none under the other: 1 KB tensor loads, whose data travel as replies, fell to 0.54-0.77 of their bandwidth alone when they shared a link under y first and held at 1.00 when they shared one under x first; tensor stores, whose data travel as requests, showed the mirror (0.52-0.76 against 1.00). A shared link carried about 92 GB/s. The same on aifoundry1 card 1 (development), aifoundry3 (the frozen validation) and aifoundry2 (the same frozen test, run as a third card on the evening of 29 September), three passes each.
measured
three cards
no published page yet
L104+}

## flow/E/2
FLOW 5 · GATHERS
Gathers from L2: 359.3 cycles … 2 hops
DRAM
More detail and the sources {+

Both harts of 1,024 minions run the 32-bit gather of 8 lanes (fgw.ps) on scattered lines of a table that fits one level: each visit's 64 elements fall on the 64 lines of one 4 KB tile, the tiles walked in scrambled order. The lanes run at the measured cycles per instruction and count the instructions each has done; the bars are on a log scale, against the leader.

 Table in G el./s pJ/element cycles/instr.
L1 452 12.76 21.78
L2 27.4 354.5 359.3
own scratchpad 27.4 367.8 359.3
scratchpad 2 hops 10.2 903.1 969.0
DRAM 1.19 9,830 8,232

 These are E48's results, measured on 26 September on all three cards; they are on the memory-hierarchy page and in the energy manual (§4.4).

 Measured and explained in Memory hierarchy ↗.

 The facts this flow uses (17): point at one for its source

 Gather (fgw.ps, 32-bit elements) from L1 (512 B table per hart), random lines: 452 G elements/s chip-wide, 12.76 pJ per element [11.89-14.57] (per card: a2 13.54, a3 12.46, a1c1 12.28); 21.78 cycles per instruction per hart.
measured
three cards
Memory hierarchy ↗
gs-g-dram-512B
Gather (fgw.ps, 32-bit elements) from L2 (4 KB table per hart), random lines: 27.4 G elements/s chip-wide, 354.5 pJ per element [329.9-391.6] (per card: a2 343.2, a3 333.1, a1c1 387.1); 359.3 cycles per instruction per hart.
measured
three cards
Memory hierarchy ↗
gs-g-dram-4K
Gather (fgw.ps, 32-bit elements) from own scratchpad (16 KB per hart), random lines: 27.4 G elements/s chip-wide, 367.8 pJ per element [344.3-399.6] (per card: a2 359.6, a3 344.6, a1c1 399.3); 359.3 cycles per instruction per hart.
measured
three cards
Memory hierarchy ↗
gs-g-scp-16K
Gather (fgw.ps, 32-bit elements) from scratchpad 2 hops away (16 KB per hart), random lines: 10.2 G elements/s chip-wide, 903.1 pJ per element [843.1-1,010] (per card: a2 888.7, a3 847.2, a1c1 973.4); 969.0 cycles per instruction per hart.
measured
three cards
Memory hierarchy ↗
gs-g-rscp-16K
Gather (fgw.ps, 32-bit elements) from DRAM (256 KB table per hart), random lines: 1.19 G elements/s chip-wide, 9,830 pJ per element [9,215-10,343] (per card: a2 9,873, a3 9,320, a1c1 10,298); 8,232 cycles per instruction per hart.
measured
three cards
Memory hierarchy ↗
gs-g-dram-256K
Scatter (fscw.ps, 32-bit elements) into L1 (512 B table per hart), random lines: 452 G elements/s chip-wide, 14.69 pJ per element [13.87-15.50] (per card: a2 14.71, a3 14.60, a1c1 14.76); 21.78 cycles per instruction per hart.
measured
three cards
Memory hierarchy ↗
gs-s-dram-512B
Scatter (fscw.ps, 32-bit elements) into L2 (4 KB table per hart), random lines: 23.5 G elements/s chip-wide, 731.5 pJ per element [676.9-813.9] (per card: a2 701.9, a3 679.1, a1c1 813.5); 417.6 cycles per instruction per hart.
measured
three cards
Memory hierarchy ↗
gs-s-dram-4K
Scatter (fscw.ps, 32-bit elements) into own scratchpad (16 KB per hart), random lines: 23.5 G elements/s chip-wide, 690.5 pJ per element [641.9-762.5] (per card: a2 670.6, a3 643.8, a1c1 757.0); 417.5 cycles per instruction per hart.
measured
three cards
Memory hierarchy ↗
gs-s-scp-16K
Scatter (fscw.ps, 32-bit elements) into scratchpad 2 hops away (16 KB per hart), random lines: 10.2 G elements/s chip-wide, 1,983 pJ per element [1,861-2,187] (per card: a2 1,960, a3 1,865, a1c1 2,125); 958.3 cycles per instruction per hart.
measured
three cards
Memory hierarchy ↗
gs-s-rscp-16K
Scatter (fscw.ps, 32-bit elements) into DRAM (256 KB table per hart), random lines: 0.422 G elements/s chip-wide, 23,770 pJ per element [22,209-25,281] (per card: a2 23,640, a3 22,530, a1c1 25,139); 24,584 cycles per instruction per hart (median, pooled over the 9 passes; per card 24,599 on aifoundry2 and aifoundry3, 24,554 on aifoundry1-c1). 2,048 harts × 8 elements at 600 MHz over that is 0.400 G elements/s, about 5% under the measured aggregate rate.
measured
three cards
Memory hierarchy ↗
gs-s-dram-256K
Gathers from L2 and the own scratchpad saturate at 27.36 G elements/s chip-wide on every card, 1.15x the two-miss-handler bound of 23.86 G/s (registered 0.5-2x: PASS); a second hart adds nothing (h2/h1 1.0005).
measured
three cards
Memory hierarchy ↗
gs-mh
Random gathers from DRAM (256 KB per hart) move whole lines at 76.4 GB/s of line traffic, the chip's 76 GB/s DRAM stream, on every card (PASS): 1.19 G useful 4-byte elements/s.
measured
three cards
Memory hierarchy ↗
gs-dram
A 32-bit gather of 8 lanes from L1 (fgw.ps, random, 512 B per hart) takes 10.89 cycles per instruction per minion on every card (registered 7-12: PASS).
measured
three cards
Memory hierarchy ↗
gs-l1
GS-UC failed on all three cards: an L1-bypassing gather (fgwl.ps, random lines from L2, one minion) runs only 1.03x faster with both harts than with one (registered prediction 1.6-2.4x): the second hart adds about 3%.
measured
three cards
Memory hierarchy ↗
gs-uc
Scatter-add alternatives, updates/s and nJ per update: gather + add + scatter in L1 139 G/s at 36 pJ; in DRAM 0.42 G/s at 22.2 nJ; packed atomic famoaddl.pi on a shire table 12.7 G/s at 0.39 nJ; amoaddg.w on a chip table 2.79 G/s at 1.12 nJ.
measured
three cards
Memory hierarchy ↗
gs-add
Card to card, gathers and scatters: elements/s identical (median ratio 1.000); pJ per element aifoundry3/aifoundry2 0.965, aifoundry1-c1/aifoundry2 1.085 (median over 100 configurations).
measured
three cards
Memory hierarchy ↗
gs-card
The mesh routes in dimension order, and a request and its reply take opposite orders: a request goes x first, then y, and a reply y first, then x, on the logical map, so a reply retraces its request's route backwards. Measured on 29 September (E56) with sets of streams between shires chosen so that their streams share one directed link under one order and none under the other: 1 KB tensor loads, whose data travel as replies, fell to 0.54-0.77 of their bandwidth alone when they shared a link under y first and held at 1.00 when they shared one under x first; tensor stores, whose data travel as requests, showed the mirror (0.52-0.76 against 1.00). A shared link carried about 92 GB/s. The same on aifoundry1 card 1 (development), aifoundry3 (the frozen validation) and aifoundry2 (the same frozen test, run as a third card on the evening of 29 September), three passes each.
measured
three cards
no published page yet
L104+}

## flow/E/3
FLOW 5 · GATHERS
Gathers from own scratchpad: 359.3 … 2 hops
DRAM
More detail and the sources {+

Both harts of 1,024 minions run the 32-bit gather of 8 lanes (fgw.ps) on scattered lines of a table that fits one level: each visit's 64 elements fall on the 64 lines of one 4 KB tile, the tiles walked in scrambled order. The lanes run at the measured cycles per instruction and count the instructions each has done; the bars are on a log scale, against the leader.

 Table in G el./s pJ/element cycles/instr.
L1 452 12.76 21.78
L2 27.4 354.5 359.3
own scratchpad 27.4 367.8 359.3
scratchpad 2 hops 10.2 903.1 969.0
DRAM 1.19 9,830 8,232

 These are E48's results, measured on 26 September on all three cards; they are on the memory-hierarchy page and in the energy manual (§4.4).

 Measured and explained in Memory hierarchy ↗.

 The facts this flow uses (17): point at one for its source

 Gather (fgw.ps, 32-bit elements) from L1 (512 B table per hart), random lines: 452 G elements/s chip-wide, 12.76 pJ per element [11.89-14.57] (per card: a2 13.54, a3 12.46, a1c1 12.28); 21.78 cycles per instruction per hart.
measured
three cards
Memory hierarchy ↗
gs-g-dram-512B
Gather (fgw.ps, 32-bit elements) from L2 (4 KB table per hart), random lines: 27.4 G elements/s chip-wide, 354.5 pJ per element [329.9-391.6] (per card: a2 343.2, a3 333.1, a1c1 387.1); 359.3 cycles per instruction per hart.
measured
three cards
Memory hierarchy ↗
gs-g-dram-4K
Gather (fgw.ps, 32-bit elements) from own scratchpad (16 KB per hart), random lines: 27.4 G elements/s chip-wide, 367.8 pJ per element [344.3-399.6] (per card: a2 359.6, a3 344.6, a1c1 399.3); 359.3 cycles per instruction per hart.
measured
three cards
Memory hierarchy ↗
gs-g-scp-16K
Gather (fgw.ps, 32-bit elements) from scratchpad 2 hops away (16 KB per hart), random lines: 10.2 G elements/s chip-wide, 903.1 pJ per element [843.1-1,010] (per card: a2 888.7, a3 847.2, a1c1 973.4); 969.0 cycles per instruction per hart.
measured
three cards
Memory hierarchy ↗
gs-g-rscp-16K
Gather (fgw.ps, 32-bit elements) from DRAM (256 KB table per hart), random lines: 1.19 G elements/s chip-wide, 9,830 pJ per element [9,215-10,343] (per card: a2 9,873, a3 9,320, a1c1 10,298); 8,232 cycles per instruction per hart.
measured
three cards
Memory hierarchy ↗
gs-g-dram-256K
Scatter (fscw.ps, 32-bit elements) into L1 (512 B table per hart), random lines: 452 G elements/s chip-wide, 14.69 pJ per element [13.87-15.50] (per card: a2 14.71, a3 14.60, a1c1 14.76); 21.78 cycles per instruction per hart.
measured
three cards
Memory hierarchy ↗
gs-s-dram-512B
Scatter (fscw.ps, 32-bit elements) into L2 (4 KB table per hart), random lines: 23.5 G elements/s chip-wide, 731.5 pJ per element [676.9-813.9] (per card: a2 701.9, a3 679.1, a1c1 813.5); 417.6 cycles per instruction per hart.
measured
three cards
Memory hierarchy ↗
gs-s-dram-4K
Scatter (fscw.ps, 32-bit elements) into own scratchpad (16 KB per hart), random lines: 23.5 G elements/s chip-wide, 690.5 pJ per element [641.9-762.5] (per card: a2 670.6, a3 643.8, a1c1 757.0); 417.5 cycles per instruction per hart.
measured
three cards
Memory hierarchy ↗
gs-s-scp-16K
Scatter (fscw.ps, 32-bit elements) into scratchpad 2 hops away (16 KB per hart), random lines: 10.2 G elements/s chip-wide, 1,983 pJ per element [1,861-2,187] (per card: a2 1,960, a3 1,865, a1c1 2,125); 958.3 cycles per instruction per hart.
measured
three cards
Memory hierarchy ↗
gs-s-rscp-16K
Scatter (fscw.ps, 32-bit elements) into DRAM (256 KB table per hart), random lines: 0.422 G elements/s chip-wide, 23,770 pJ per element [22,209-25,281] (per card: a2 23,640, a3 22,530, a1c1 25,139); 24,584 cycles per instruction per hart (median, pooled over the 9 passes; per card 24,599 on aifoundry2 and aifoundry3, 24,554 on aifoundry1-c1). 2,048 harts × 8 elements at 600 MHz over that is 0.400 G elements/s, about 5% under the measured aggregate rate.
measured
three cards
Memory hierarchy ↗
gs-s-dram-256K
Gathers from L2 and the own scratchpad saturate at 27.36 G elements/s chip-wide on every card, 1.15x the two-miss-handler bound of 23.86 G/s (registered 0.5-2x: PASS); a second hart adds nothing (h2/h1 1.0005).
measured
three cards
Memory hierarchy ↗
gs-mh
Random gathers from DRAM (256 KB per hart) move whole lines at 76.4 GB/s of line traffic, the chip's 76 GB/s DRAM stream, on every card (PASS): 1.19 G useful 4-byte elements/s.
measured
three cards
Memory hierarchy ↗
gs-dram
A 32-bit gather of 8 lanes from L1 (fgw.ps, random, 512 B per hart) takes 10.89 cycles per instruction per minion on every card (registered 7-12: PASS).
measured
three cards
Memory hierarchy ↗
gs-l1
GS-UC failed on all three cards: an L1-bypassing gather (fgwl.ps, random lines from L2, one minion) runs only 1.03x faster with both harts than with one (registered prediction 1.6-2.4x): the second hart adds about 3%.
measured
three cards
Memory hierarchy ↗
gs-uc
Scatter-add alternatives, updates/s and nJ per update: gather + add + scatter in L1 139 G/s at 36 pJ; in DRAM 0.42 G/s at 22.2 nJ; packed atomic famoaddl.pi on a shire table 12.7 G/s at 0.39 nJ; amoaddg.w on a chip table 2.79 G/s at 1.12 nJ.
measured
three cards
Memory hierarchy ↗
gs-add
Card to card, gathers and scatters: elements/s identical (median ratio 1.000); pJ per element aifoundry3/aifoundry2 0.965, aifoundry1-c1/aifoundry2 1.085 (median over 100 configurations).
measured
three cards
Memory hierarchy ↗
gs-card
The mesh routes in dimension order, and a request and its reply take opposite orders: a request goes x first, then y, and a reply y first, then x, on the logical map, so a reply retraces its request's route backwards. Measured on 29 September (E56) with sets of streams between shires chosen so that their streams share one directed link under one order and none under the other: 1 KB tensor loads, whose data travel as replies, fell to 0.54-0.77 of their bandwidth alone when they shared a link under y first and held at 1.00 when they shared one under x first; tensor stores, whose data travel as requests, showed the mirror (0.52-0.76 against 1.00). A shared link carried about 92 GB/s. The same on aifoundry1 card 1 (development), aifoundry3 (the frozen validation) and aifoundry2 (the same frozen test, run as a third card on the evening of 29 September), three passes each.
measured
three cards
no published page yet
L104+}

## flow/E/4
FLOW 5 · GATHERS
Gathers from scratchpad 2 hops: … cycles each
DRAM
More detail and the sources {+

Both harts of 1,024 minions run the 32-bit gather of 8 lanes (fgw.ps) on scattered lines of a table that fits one level: each visit's 64 elements fall on the 64 lines of one 4 KB tile, the tiles walked in scrambled order. The lanes run at the measured cycles per instruction and count the instructions each has done; the bars are on a log scale, against the leader.

 Table in G el./s pJ/element cycles/instr.
L1 452 12.76 21.78
L2 27.4 354.5 359.3
own scratchpad 27.4 367.8 359.3
scratchpad 2 hops 10.2 903.1 969.0
DRAM 1.19 9,830 8,232

 These are E48's results, measured on 26 September on all three cards; they are on the memory-hierarchy page and in the energy manual (§4.4).

 Measured and explained in Memory hierarchy ↗.

 The facts this flow uses (17): point at one for its source

 Gather (fgw.ps, 32-bit elements) from L1 (512 B table per hart), random lines: 452 G elements/s chip-wide, 12.76 pJ per element [11.89-14.57] (per card: a2 13.54, a3 12.46, a1c1 12.28); 21.78 cycles per instruction per hart.
measured
three cards
Memory hierarchy ↗
gs-g-dram-512B
Gather (fgw.ps, 32-bit elements) from L2 (4 KB table per hart), random lines: 27.4 G elements/s chip-wide, 354.5 pJ per element [329.9-391.6] (per card: a2 343.2, a3 333.1, a1c1 387.1); 359.3 cycles per instruction per hart.
measured
three cards
Memory hierarchy ↗
gs-g-dram-4K
Gather (fgw.ps, 32-bit elements) from own scratchpad (16 KB per hart), random lines: 27.4 G elements/s chip-wide, 367.8 pJ per element [344.3-399.6] (per card: a2 359.6, a3 344.6, a1c1 399.3); 359.3 cycles per instruction per hart.
measured
three cards
Memory hierarchy ↗
gs-g-scp-16K
Gather (fgw.ps, 32-bit elements) from scratchpad 2 hops away (16 KB per hart), random lines: 10.2 G elements/s chip-wide, 903.1 pJ per element [843.1-1,010] (per card: a2 888.7, a3 847.2, a1c1 973.4); 969.0 cycles per instruction per hart.
measured
three cards
Memory hierarchy ↗
gs-g-rscp-16K
Gather (fgw.ps, 32-bit elements) from DRAM (256 KB table per hart), random lines: 1.19 G elements/s chip-wide, 9,830 pJ per element [9,215-10,343] (per card: a2 9,873, a3 9,320, a1c1 10,298); 8,232 cycles per instruction per hart.
measured
three cards
Memory hierarchy ↗
gs-g-dram-256K
Scatter (fscw.ps, 32-bit elements) into L1 (512 B table per hart), random lines: 452 G elements/s chip-wide, 14.69 pJ per element [13.87-15.50] (per card: a2 14.71, a3 14.60, a1c1 14.76); 21.78 cycles per instruction per hart.
measured
three cards
Memory hierarchy ↗
gs-s-dram-512B
Scatter (fscw.ps, 32-bit elements) into L2 (4 KB table per hart), random lines: 23.5 G elements/s chip-wide, 731.5 pJ per element [676.9-813.9] (per card: a2 701.9, a3 679.1, a1c1 813.5); 417.6 cycles per instruction per hart.
measured
three cards
Memory hierarchy ↗
gs-s-dram-4K
Scatter (fscw.ps, 32-bit elements) into own scratchpad (16 KB per hart), random lines: 23.5 G elements/s chip-wide, 690.5 pJ per element [641.9-762.5] (per card: a2 670.6, a3 643.8, a1c1 757.0); 417.5 cycles per instruction per hart.
measured
three cards
Memory hierarchy ↗
gs-s-scp-16K
Scatter (fscw.ps, 32-bit elements) into scratchpad 2 hops away (16 KB per hart), random lines: 10.2 G elements/s chip-wide, 1,983 pJ per element [1,861-2,187] (per card: a2 1,960, a3 1,865, a1c1 2,125); 958.3 cycles per instruction per hart.
measured
three cards
Memory hierarchy ↗
gs-s-rscp-16K
Scatter (fscw.ps, 32-bit elements) into DRAM (256 KB table per hart), random lines: 0.422 G elements/s chip-wide, 23,770 pJ per element [22,209-25,281] (per card: a2 23,640, a3 22,530, a1c1 25,139); 24,584 cycles per instruction per hart (median, pooled over the 9 passes; per card 24,599 on aifoundry2 and aifoundry3, 24,554 on aifoundry1-c1). 2,048 harts × 8 elements at 600 MHz over that is 0.400 G elements/s, about 5% under the measured aggregate rate.
measured
three cards
Memory hierarchy ↗
gs-s-dram-256K
Gathers from L2 and the own scratchpad saturate at 27.36 G elements/s chip-wide on every card, 1.15x the two-miss-handler bound of 23.86 G/s (registered 0.5-2x: PASS); a second hart adds nothing (h2/h1 1.0005).
measured
three cards
Memory hierarchy ↗
gs-mh
Random gathers from DRAM (256 KB per hart) move whole lines at 76.4 GB/s of line traffic, the chip's 76 GB/s DRAM stream, on every card (PASS): 1.19 G useful 4-byte elements/s.
measured
three cards
Memory hierarchy ↗
gs-dram
A 32-bit gather of 8 lanes from L1 (fgw.ps, random, 512 B per hart) takes 10.89 cycles per instruction per minion on every card (registered 7-12: PASS).
measured
three cards
Memory hierarchy ↗
gs-l1
GS-UC failed on all three cards: an L1-bypassing gather (fgwl.ps, random lines from L2, one minion) runs only 1.03x faster with both harts than with one (registered prediction 1.6-2.4x): the second hart adds about 3%.
measured
three cards
Memory hierarchy ↗
gs-uc
Scatter-add alternatives, updates/s and nJ per update: gather + add + scatter in L1 139 G/s at 36 pJ; in DRAM 0.42 G/s at 22.2 nJ; packed atomic famoaddl.pi on a shire table 12.7 G/s at 0.39 nJ; amoaddg.w on a chip table 2.79 G/s at 1.12 nJ.
measured
three cards
Memory hierarchy ↗
gs-add
Card to card, gathers and scatters: elements/s identical (median ratio 1.000); pJ per element aifoundry3/aifoundry2 0.965, aifoundry1-c1/aifoundry2 1.085 (median over 100 configurations).
measured
three cards
Memory hierarchy ↗
gs-card
The mesh routes in dimension order, and a request and its reply take opposite orders: a request goes x first, then y, and a reply y first, then x, on the logical map, so a reply retraces its request's route backwards. Measured on 29 September (E56) with sets of streams between shires chosen so that their streams share one directed link under one order and none under the other: 1 KB tensor loads, whose data travel as replies, fell to 0.54-0.77 of their bandwidth alone when they shared a link under y first and held at 1.00 when they shared one under x first; tensor stores, whose data travel as requests, showed the mirror (0.52-0.76 against 1.00). A shared link carried about 92 GB/s. The same on aifoundry1 card 1 (development), aifoundry3 (the frozen validation) and aifoundry2 (the same frozen test, run as a third card on the evening of 29 September), three passes each.
measured
three cards
no published page yet
L104+}

## flow/E/5
FLOW 5 · GATHERS
Gathers from DRAM: 8,232 cycles …
8,232 cycles each
More detail and the sources {+

Both harts of 1,024 minions run the 32-bit gather of 8 lanes (fgw.ps) on scattered lines of a table that fits one level: each visit's 64 elements fall on the 64 lines of one 4 KB tile, the tiles walked in scrambled order. The lanes run at the measured cycles per instruction and count the instructions each has done; the bars are on a log scale, against the leader.

 Table in G el./s pJ/element cycles/instr.
L1 452 12.76 21.78
L2 27.4 354.5 359.3
own scratchpad 27.4 367.8 359.3
scratchpad 2 hops 10.2 903.1 969.0
DRAM 1.19 9,830 8,232

 These are E48's results, measured on 26 September on all three cards; they are on the memory-hierarchy page and in the energy manual (§4.4).

 Measured and explained in Memory hierarchy ↗.

 The facts this flow uses (17): point at one for its source

 Gather (fgw.ps, 32-bit elements) from L1 (512 B table per hart), random lines: 452 G elements/s chip-wide, 12.76 pJ per element [11.89-14.57] (per card: a2 13.54, a3 12.46, a1c1 12.28); 21.78 cycles per instruction per hart.
measured
three cards
Memory hierarchy ↗
gs-g-dram-512B
Gather (fgw.ps, 32-bit elements) from L2 (4 KB table per hart), random lines: 27.4 G elements/s chip-wide, 354.5 pJ per element [329.9-391.6] (per card: a2 343.2, a3 333.1, a1c1 387.1); 359.3 cycles per instruction per hart.
measured
three cards
Memory hierarchy ↗
gs-g-dram-4K
Gather (fgw.ps, 32-bit elements) from own scratchpad (16 KB per hart), random lines: 27.4 G elements/s chip-wide, 367.8 pJ per element [344.3-399.6] (per card: a2 359.6, a3 344.6, a1c1 399.3); 359.3 cycles per instruction per hart.
measured
three cards
Memory hierarchy ↗
gs-g-scp-16K
Gather (fgw.ps, 32-bit elements) from scratchpad 2 hops away (16 KB per hart), random lines: 10.2 G elements/s chip-wide, 903.1 pJ per element [843.1-1,010] (per card: a2 888.7, a3 847.2, a1c1 973.4); 969.0 cycles per instruction per hart.
measured
three cards
Memory hierarchy ↗
gs-g-rscp-16K
Gather (fgw.ps, 32-bit elements) from DRAM (256 KB table per hart), random lines: 1.19 G elements/s chip-wide, 9,830 pJ per element [9,215-10,343] (per card: a2 9,873, a3 9,320, a1c1 10,298); 8,232 cycles per instruction per hart.
measured
three cards
Memory hierarchy ↗
gs-g-dram-256K
Scatter (fscw.ps, 32-bit elements) into L1 (512 B table per hart), random lines: 452 G elements/s chip-wide, 14.69 pJ per element [13.87-15.50] (per card: a2 14.71, a3 14.60, a1c1 14.76); 21.78 cycles per instruction per hart.
measured
three cards
Memory hierarchy ↗
gs-s-dram-512B
Scatter (fscw.ps, 32-bit elements) into L2 (4 KB table per hart), random lines: 23.5 G elements/s chip-wide, 731.5 pJ per element [676.9-813.9] (per card: a2 701.9, a3 679.1, a1c1 813.5); 417.6 cycles per instruction per hart.
measured
three cards
Memory hierarchy ↗
gs-s-dram-4K
Scatter (fscw.ps, 32-bit elements) into own scratchpad (16 KB per hart), random lines: 23.5 G elements/s chip-wide, 690.5 pJ per element [641.9-762.5] (per card: a2 670.6, a3 643.8, a1c1 757.0); 417.5 cycles per instruction per hart.
measured
three cards
Memory hierarchy ↗
gs-s-scp-16K
Scatter (fscw.ps, 32-bit elements) into scratchpad 2 hops away (16 KB per hart), random lines: 10.2 G elements/s chip-wide, 1,983 pJ per element [1,861-2,187] (per card: a2 1,960, a3 1,865, a1c1 2,125); 958.3 cycles per instruction per hart.
measured
three cards
Memory hierarchy ↗
gs-s-rscp-16K
Scatter (fscw.ps, 32-bit elements) into DRAM (256 KB table per hart), random lines: 0.422 G elements/s chip-wide, 23,770 pJ per element [22,209-25,281] (per card: a2 23,640, a3 22,530, a1c1 25,139); 24,584 cycles per instruction per hart (median, pooled over the 9 passes; per card 24,599 on aifoundry2 and aifoundry3, 24,554 on aifoundry1-c1). 2,048 harts × 8 elements at 600 MHz over that is 0.400 G elements/s, about 5% under the measured aggregate rate.
measured
three cards
Memory hierarchy ↗
gs-s-dram-256K
Gathers from L2 and the own scratchpad saturate at 27.36 G elements/s chip-wide on every card, 1.15x the two-miss-handler bound of 23.86 G/s (registered 0.5-2x: PASS); a second hart adds nothing (h2/h1 1.0005).
measured
three cards
Memory hierarchy ↗
gs-mh
Random gathers from DRAM (256 KB per hart) move whole lines at 76.4 GB/s of line traffic, the chip's 76 GB/s DRAM stream, on every card (PASS): 1.19 G useful 4-byte elements/s.
measured
three cards
Memory hierarchy ↗
gs-dram
A 32-bit gather of 8 lanes from L1 (fgw.ps, random, 512 B per hart) takes 10.89 cycles per instruction per minion on every card (registered 7-12: PASS).
measured
three cards
Memory hierarchy ↗
gs-l1
GS-UC failed on all three cards: an L1-bypassing gather (fgwl.ps, random lines from L2, one minion) runs only 1.03x faster with both harts than with one (registered prediction 1.6-2.4x): the second hart adds about 3%.
measured
three cards
Memory hierarchy ↗
gs-uc
Scatter-add alternatives, updates/s and nJ per update: gather + add + scatter in L1 139 G/s at 36 pJ; in DRAM 0.42 G/s at 22.2 nJ; packed atomic famoaddl.pi on a shire table 12.7 G/s at 0.39 nJ; amoaddg.w on a chip table 2.79 G/s at 1.12 nJ.
measured
three cards
Memory hierarchy ↗
gs-add
Card to card, gathers and scatters: elements/s identical (median ratio 1.000); pJ per element aifoundry3/aifoundry2 0.965, aifoundry1-c1/aifoundry2 1.085 (median over 100 configurations).
measured
three cards
Memory hierarchy ↗
gs-card
The mesh routes in dimension order, and a request and its reply take opposite orders: a request goes x first, then y, and a reply y first, then x, on the logical map, so a reply retraces its request's route backwards. Measured on 29 September (E56) with sets of streams between shires chosen so that their streams share one directed link under one order and none under the other: 1 KB tensor loads, whose data travel as replies, fell to 0.54-0.77 of their bandwidth alone when they shared a link under y first and held at 1.00 when they shared one under x first; tensor stores, whose data travel as requests, showed the mirror (0.52-0.76 against 1.00). A shared link carried about 92 GB/s. The same on aifoundry1 card 1 (development), aifoundry3 (the frozen validation) and aifoundry2 (the same frozen test, run as a third card on the evening of 29 September), three passes each.
measured
three cards
no published page yet
L104+}

## flow/F/0
FLOW 6 · HOST AND PCIE
The host link: … each part takes.

 More detail and the sources {+

The host writes a kernel's buffers into device DRAM through the PCIe shire (device allocations are DRAM addresses from 0x80_0000_0000), then posts the launch to the master shire, whose firmware starts it on the compute shires. Timed on three cards on 27 September, five runs each, against predictions written before the runs.

 Leg What happens
the link trained at 16.0 GT/s x8 on every card: 15.75 GB/s per direction
DMA 12.46–12.60 GB/s to the card, 10.41–10.54 GB/s back: 79–80% and 66–67% of the link
staged a program's copies: 7.15 / 5.20 / 7.79 GB/s (host memcpy 17.4 / 9.2 / 21.4 GB/s first, then the DMA)
into DRAM each line through its L3 home (PA[10:6]), which keeps it: 99.5% of a copied buffer's lines then read at L3 latency (E55); the L3's write-back to the 8 memory shires (PA[8:6]) not timed
launch an empty kernel on 32 shires: 103.6 / 103.7 / 104.1 µs each when queued, the card's own cost; one launch waited for takes 566 / 556 / 565 µs, the extra 452–463 µs mostly the runtime's 500 µs idle poll
small copies a lone 4 KB copy: 377 / 379 / 411 µs, the runtime's polling (50 µs in flight, 500 µs idle)

 Values are per card: aifoundry2 / aifoundry3 / aifoundry1 card 1, where three are given.

 Inferred or open here, and what would settle it (2)

 Settled: PCIe bandwidth (PCIe shire, Host, Flow 6)

 Was: 15.75 GB/s per direction, the Gen4 x8 link figure, with host transfers never timed.

 How: Settled on 27 September: timed on three cards with workloads/pciebench, five runs per card against predictions stated before the runs (docs/reports/data/2026-09-27-pcie; the page Over the PCIe link). Not a team ask.

 Nearly settled: the Host -> DRAM path (Flow 6, 'Into DRAM')

 Measured on 29 September (E55, fact pcie.write-l3): the host's writes go through their lines' L3 homes, which allocate the lines. After a staged 4 MB copy 99.5% of the lines read at L3 latency on aifoundry3 (99.6% on aifoundry2, 99.9% on aifoundry1 card 1), whether the L3 held the buffer before or not, and no value read was stale. Still inferred, and drawn dashed: the L3's later write-back of those lines to the memory shires and DRAM.

 What settles it, and what is left: Settled by experiment: copy a buffer from the host, then time each line's first load in a kernel launched without the L3 flush; L3-hit latency means through the L3 homes (tools/claims-v3/pcie2/PREREG.md, frozen before the validation; docs/reports/data/2026-09-29-pcie2). What is left: why the bridge sends the writes there. The PCIe shire's to-sys bridge has DRAM address-map entries for every shire's L3 slave (SHn_L3D) and for each memory shire (MC0..MC7_MEM) (etsoc-hal hwinc/noc_esr.h, BRIDGE_PS0_TOSYS ... MAP_MEM_DRAM), so the programmed ADBASE/ADMASK decide: read them (SP-only) or the NoC documents.

 On the hub: rung 34: First touch after a host copy: does the host write through the L3? ↗ · rung 21: The NoC's reference manual and specification ↗ · rung 27: A way to read the NoC's router and bridge registers ↗

 Inferred: the host link's open questions (PCIe shire, Host, Flow 6)

 Not inferred but unexplained, from the PCIe page: why two host-to-card DMA commands of one stream at once move half as much as one, and why card-to-host DMA dips at 32-64 MB per copy. E55 (29 September) found where the loss is: two commands in flight in one stream move 0.488 of one at 2 x 64 MB on aifoundry3, one command in each of two streams 1.012 (T35-S; 0.496 and 1.014 on aifoundry2), and a shared read engine, the IOMMU, a fixed cost per overlap, a slow onset and a loss per element were refuted on all three cards tested. aifoundry3's host copies memory at about half the others' rate because it runs one memory channel (docs/reports/data/2026-09-27-pcie/hosts.txt).

 What would settle it: What serves one stream's two commands in turn: the runtime's source for a stream's DMA queue, or the master minion's DMA worker in the firmware; the PCIe DMA engine's documentation, or the settings the firmware programs (channel arbitration, read-request size, element splitting), for the card-to-host dip; the lab admin's reads on the hosts (lspci -vvv for the payload and read-request sizes).

 On the hub: rung 35: Why two host-to-card DMA commands halve the rate: a command-size sweep, and the IOMMU in passthrough ↗ · rung 29: The PCIe DMA engine's documentation and the settings the firmware gives it ↗ · rung 30: Two readings on the lab hosts that need root ↗

 Measured and explained in Over the PCIe link ↗.

 The facts this flow uses (20): point at one for its source

 The link trained at 16.0 GT/s x8 on all three cards in every run (sysfs current_link_speed and current_link_width): PCIe Gen4 x8, 15.75 GB/s per direction after 128b/130b coding.
measured
three cards
Over the PCIe link ↗
pcie.negotiated
Host to device, DMA only (the runtime's host-side copy replaced by a no-op, the analogue of pinned memory), 256 MB per copy: 12.47 [12.39, 12.55] GB/s on aifoundry2, 12.60 [12.55, 12.65] GB/s on aifoundry3, 12.46 [12.41, 12.50] GB/s on aifoundry1-c1 (mean of 5 runs [99% interval]): 12.46-12.60 GB/s, 79-80% of the link's 15.75 GB/s.
measured
three cards
Over the PCIe link ↗
pcie.h2d
Device to host, DMA only, 256 MB per copy: 10.54 [10.43, 10.64] GB/s on aifoundry2, 10.41 [10.30, 10.52] GB/s on aifoundry3, 10.41 [10.38, 10.45] GB/s on aifoundry1-c1: 10.41-10.54 GB/s, 66-67% of the link figure, slower than host to device. The fastest device-to-host size is 16 MB on aifoundry2 (11.75 GB/s), 16 MB on aifoundry3 (10.99 GB/s), 16 MB on aifoundry1-c1 (10.69 GB/s).
measured
three cards
Over the PCIe link ↗
pcie.d2h
The path a program takes, the runtime's staged copy (a host memcpy into a CMA bounce buffer, then the DMA), 256 MB: host to device 7.15 / 5.20 / 7.79 GB/s (5.20-7.79), device to host 6.53 / 4.78 / 6.97 GB/s (aifoundry2 / aifoundry3 / aifoundry1-c1). The hosts' own memcpy runs at 17.4 / 9.2 / 21.4 GB/s, and each staged rate is 98-100% of 1/(1/DMA + 1/memcpy): the runtime copies and then transfers, one after the other, so a slow host memcpy (aifoundry3's) cuts the staged rate on the same link to 0.67-0.73 of the other hosts' (host to device).
measured
three cards
Over the PCIe link ↗
pcie.staged
A DMA-only host-to-device copy reaches half its 256 MB rate at 2.0 / 2.1 / 2.2 MB per copy (aifoundry2 / aifoundry3 / aifoundry1-c1; n½, from the mean over five runs of log2 of the size): smaller copies are dominated by the per-command time.
measured
three cards
Over the PCIe link ↗
pcie.nhalf
A 4 KB copy issued after a random 0-1 ms gap takes 377 / 379 / 411 µs on average (377-411 µs; aifoundry2 / aifoundry3 / aifoundry1-c1; the mean over the four copy variants), while 200 queued 4 KB copies take 38 / 13 / 30 µs each (host to device, staged) and a wait on an idle stream 2.6 / 0.4 / 2.3 µs. The time of a lone small copy is the runtime's response polling, not the link.
measured
three cards
Over the PCIe link ↗
pcie.small
The runtime's response thread polls the device's completion queue, sleeping 50 µs between polls while commands are in flight and 500 µs when none are.
documented
Over the PCIe link ↗
pcie.poll
An empty kernel on all 32 compute shires, launched and waited for: 566 / 556 / 565 µs (556-566 µs) from launch to completion (aifoundry2 / aifoundry3 / aifoundry1-c1); 100 launches queued back to back: 103.6 / 103.7 / 104.1 µs each (103.6-104.1 µs) on 32 shires and 91.2 / 92.2 / 92.4 on one shire. The card's own cost is the queued figure: a lone launch waited for adds 463 / 452 / 461 µs (452-463 µs, each run's difference), most of the runtime's 500 µs idle poll (fact pcie.poll), and a one-shire lone launch takes the same 566 / 556 / 565 µs.
measured
three cards
Over the PCIe link ↗
pcie.launch
Two host-to-device commands in flight on one stream move 6.09 / 6.09 / 6.03 GB/s (aifoundry2 / aifoundry3 / aifoundry1-c1), half the 12.39 / 12.48 / 12.28 GB/s of one command at a time (two streams with both of each stream's commands in flight, four in all: 5.96 / 6.00 / 5.96 GB/s in total; with one command in flight in each of two streams nothing is lost, 1.012 of one at a time on aifoundry3, 1.014 on aifoundry2 and 1.019 on aifoundry1-c1, E55); both directions at once, one command each at a time, move 16.97 / 16.89 / 16.92 GB/s together (2 × 64 MB per stream, DMA only).
measured
three cards
Over the PCIe link ↗
pcie.conc
A host-to-card copy goes through each line's L3 home, which allocates the line: after a staged 4 MB copy, 99.5% of the lines read at L3 latency on aifoundry3 (99.6% on aifoundry2, 99.9% on aifoundry1-c1), whether the L3 held the buffer before or not, and every value read was the last one written. A kernel's first touch of a freshly copied buffer hits the L3, not DRAM (tested for a 4 MB buffer).
measured
three cards
Over the PCIe link ↗
pcie.write-l3
A line's L3 home shire is PA[10:6]: consecutive 64-byte lines rotate over the 32 compute shires' L3 slices (default 'swizzle0'; the firmware leaves the swizzle register at reset).
measured
three cards
Anatomy of a memory access ↗
l3.home
Host link: PCIe Gen4 x8, 15.75 GB/s per direction before protocol overhead; the transfers were timed on three cards on 27 September (facts pcie.h2d and pcie.d2h give the measured rates).
documented
Ridge points ↗
bw-pcie
The PCIe shire contains two independent dual-mode PCIe controllers and an 8-lane PCIe Gen4 PHY, factory-configured as an endpoint; the dev card exposes a Gen4 x8 host interface.
documented
Ridge points ↗
chip.pcie-shire
40-bit physical address space (1 TB): I/O 0x00_0000_0000 (1 GB), service processor 0x00_4000_0000 (1 GB), scratchpad 0x00_8000_0000 (2 GB), ESRs 0x01_0000_0000 (4 GB), PCIe 0x40_0000_0000 (256 GB), DRAM 0x80_0000_0000 (512 GB).
documented
no published page yet
addr.regions
The DRAM region starts at 0x80_0000_0000; minions reach only the 'Low' view (M-mode low 8 MB, OS low to 0x80_FFFF_FFFF, memory low 0x81_0000_0000-0x87_FFFF_FFFF, 28 GB); device allocations come back as 0x80_xxxx_xxxx addresses.
documented
no published page yet
addr.dram-region
The memory shire serving a line is PA[8:6] (so it is always the L3 home shire's low three bits) and the controller/channel within it is PA[9]: consecutive 64 B lines rotate over the 8 memory shires, the two channels alternate every 512 B.
measured
aifoundry2
Anatomy of a memory access ↗
dram.memshire-select
In the firmware's maps the four cells that hold no compute shire are: logical (0, 3), shire 32, the master; (5, 3), shire 33, the spare; (0, 4), the PCIe shire ('pcie0' in the bridge map); and (0, 5), the I/O shire ('io0'). On this die view that puts the master in the north cell and the spare in the south one, with PCIe then I/O east of the master.
documented
no published page yet
fw.grey-cells
The master shire (which runs the master-minion firmware and schedules kernels) is shire 32 in the firmware; its 2.5 MB scratchpad at 0x9000_0000 holds the firmware's host-interface buffers.
documented
Limits of observability ↗
chip.master-shire-id
The driver reports compute shire mask 0xffffffff (shires 0-31) and sync (master) shire 32 on every card.
measured
three cards
The DVFS loop and its leakage ↗
chip.cm-shire-mask
The mesh routes in dimension order, and a request and its reply take opposite orders: a request goes x first, then y, and a reply y first, then x, on the logical map, so a reply retraces its request's route backwards. Measured on 29 September (E56) with sets of streams between shires chosen so that their streams share one directed link under one order and none under the other: 1 KB tensor loads, whose data travel as replies, fell to 0.54-0.77 of their bandwidth alone when they shared a link under y first and held at 1.00 when they shared one under x first; tensor stores, whose data travel as requests, showed the mirror (0.52-0.76 against 1.00). A shared link carried about 92 GB/s. The same on aifoundry1 card 1 (development), aifoundry3 (the frozen validation) and aifoundry2 (the same frozen test, run as a third card on the evening of 29 September), three passes each.
measured
three cards
no published page yet
L104+}

## flow/F/1
FLOW 6 · HOST AND PCIE
The host link: … each part takes.

 More detail and the sources {+

The host writes a kernel's buffers into device DRAM through the PCIe shire (device allocations are DRAM addresses from 0x80_0000_0000), then posts the launch to the master shire, whose firmware starts it on the compute shires. Timed on three cards on 27 September, five runs each, against predictions written before the runs.

 Leg What happens
the link trained at 16.0 GT/s x8 on every card: 15.75 GB/s per direction
DMA 12.46–12.60 GB/s to the card, 10.41–10.54 GB/s back: 79–80% and 66–67% of the link
staged a program's copies: 7.15 / 5.20 / 7.79 GB/s (host memcpy 17.4 / 9.2 / 21.4 GB/s first, then the DMA)
into DRAM each line through its L3 home (PA[10:6]), which keeps it: 99.5% of a copied buffer's lines then read at L3 latency (E55); the L3's write-back to the 8 memory shires (PA[8:6]) not timed
launch an empty kernel on 32 shires: 103.6 / 103.7 / 104.1 µs each when queued, the card's own cost; one launch waited for takes 566 / 556 / 565 µs, the extra 452–463 µs mostly the runtime's 500 µs idle poll
small copies a lone 4 KB copy: 377 / 379 / 411 µs, the runtime's polling (50 µs in flight, 500 µs idle)

 Values are per card: aifoundry2 / aifoundry3 / aifoundry1 card 1, where three are given.

 Inferred or open here, and what would settle it (2)

 Settled: PCIe bandwidth (PCIe shire, Host, Flow 6)

 Was: 15.75 GB/s per direction, the Gen4 x8 link figure, with host transfers never timed.

 How: Settled on 27 September: timed on three cards with workloads/pciebench, five runs per card against predictions stated before the runs (docs/reports/data/2026-09-27-pcie; the page Over the PCIe link). Not a team ask.

 Nearly settled: the Host -> DRAM path (Flow 6, 'Into DRAM')

 Measured on 29 September (E55, fact pcie.write-l3): the host's writes go through their lines' L3 homes, which allocate the lines. After a staged 4 MB copy 99.5% of the lines read at L3 latency on aifoundry3 (99.6% on aifoundry2, 99.9% on aifoundry1 card 1), whether the L3 held the buffer before or not, and no value read was stale. Still inferred, and drawn dashed: the L3's later write-back of those lines to the memory shires and DRAM.

 What settles it, and what is left: Settled by experiment: copy a buffer from the host, then time each line's first load in a kernel launched without the L3 flush; L3-hit latency means through the L3 homes (tools/claims-v3/pcie2/PREREG.md, frozen before the validation; docs/reports/data/2026-09-29-pcie2). What is left: why the bridge sends the writes there. The PCIe shire's to-sys bridge has DRAM address-map entries for every shire's L3 slave (SHn_L3D) and for each memory shire (MC0..MC7_MEM) (etsoc-hal hwinc/noc_esr.h, BRIDGE_PS0_TOSYS ... MAP_MEM_DRAM), so the programmed ADBASE/ADMASK decide: read them (SP-only) or the NoC documents.

 On the hub: rung 34: First touch after a host copy: does the host write through the L3? ↗ · rung 21: The NoC's reference manual and specification ↗ · rung 27: A way to read the NoC's router and bridge registers ↗

 Inferred: the host link's open questions (PCIe shire, Host, Flow 6)

 Not inferred but unexplained, from the PCIe page: why two host-to-card DMA commands of one stream at once move half as much as one, and why card-to-host DMA dips at 32-64 MB per copy. E55 (29 September) found where the loss is: two commands in flight in one stream move 0.488 of one at 2 x 64 MB on aifoundry3, one command in each of two streams 1.012 (T35-S; 0.496 and 1.014 on aifoundry2), and a shared read engine, the IOMMU, a fixed cost per overlap, a slow onset and a loss per element were refuted on all three cards tested. aifoundry3's host copies memory at about half the others' rate because it runs one memory channel (docs/reports/data/2026-09-27-pcie/hosts.txt).

 What would settle it: What serves one stream's two commands in turn: the runtime's source for a stream's DMA queue, or the master minion's DMA worker in the firmware; the PCIe DMA engine's documentation, or the settings the firmware programs (channel arbitration, read-request size, element splitting), for the card-to-host dip; the lab admin's reads on the hosts (lspci -vvv for the payload and read-request sizes).

 On the hub: rung 35: Why two host-to-card DMA commands halve the rate: a command-size sweep, and the IOMMU in passthrough ↗ · rung 29: The PCIe DMA engine's documentation and the settings the firmware gives it ↗ · rung 30: Two readings on the lab hosts that need root ↗

 Measured and explained in Over the PCIe link ↗.

 The facts this flow uses (20): point at one for its source

 The link trained at 16.0 GT/s x8 on all three cards in every run (sysfs current_link_speed and current_link_width): PCIe Gen4 x8, 15.75 GB/s per direction after 128b/130b coding.
measured
three cards
Over the PCIe link ↗
pcie.negotiated
Host to device, DMA only (the runtime's host-side copy replaced by a no-op, the analogue of pinned memory), 256 MB per copy: 12.47 [12.39, 12.55] GB/s on aifoundry2, 12.60 [12.55, 12.65] GB/s on aifoundry3, 12.46 [12.41, 12.50] GB/s on aifoundry1-c1 (mean of 5 runs [99% interval]): 12.46-12.60 GB/s, 79-80% of the link's 15.75 GB/s.
measured
three cards
Over the PCIe link ↗
pcie.h2d
Device to host, DMA only, 256 MB per copy: 10.54 [10.43, 10.64] GB/s on aifoundry2, 10.41 [10.30, 10.52] GB/s on aifoundry3, 10.41 [10.38, 10.45] GB/s on aifoundry1-c1: 10.41-10.54 GB/s, 66-67% of the link figure, slower than host to device. The fastest device-to-host size is 16 MB on aifoundry2 (11.75 GB/s), 16 MB on aifoundry3 (10.99 GB/s), 16 MB on aifoundry1-c1 (10.69 GB/s).
measured
three cards
Over the PCIe link ↗
pcie.d2h
The path a program takes, the runtime's staged copy (a host memcpy into a CMA bounce buffer, then the DMA), 256 MB: host to device 7.15 / 5.20 / 7.79 GB/s (5.20-7.79), device to host 6.53 / 4.78 / 6.97 GB/s (aifoundry2 / aifoundry3 / aifoundry1-c1). The hosts' own memcpy runs at 17.4 / 9.2 / 21.4 GB/s, and each staged rate is 98-100% of 1/(1/DMA + 1/memcpy): the runtime copies and then transfers, one after the other, so a slow host memcpy (aifoundry3's) cuts the staged rate on the same link to 0.67-0.73 of the other hosts' (host to device).
measured
three cards
Over the PCIe link ↗
pcie.staged
A DMA-only host-to-device copy reaches half its 256 MB rate at 2.0 / 2.1 / 2.2 MB per copy (aifoundry2 / aifoundry3 / aifoundry1-c1; n½, from the mean over five runs of log2 of the size): smaller copies are dominated by the per-command time.
measured
three cards
Over the PCIe link ↗
pcie.nhalf
A 4 KB copy issued after a random 0-1 ms gap takes 377 / 379 / 411 µs on average (377-411 µs; aifoundry2 / aifoundry3 / aifoundry1-c1; the mean over the four copy variants), while 200 queued 4 KB copies take 38 / 13 / 30 µs each (host to device, staged) and a wait on an idle stream 2.6 / 0.4 / 2.3 µs. The time of a lone small copy is the runtime's response polling, not the link.
measured
three cards
Over the PCIe link ↗
pcie.small
The runtime's response thread polls the device's completion queue, sleeping 50 µs between polls while commands are in flight and 500 µs when none are.
documented
Over the PCIe link ↗
pcie.poll
An empty kernel on all 32 compute shires, launched and waited for: 566 / 556 / 565 µs (556-566 µs) from launch to completion (aifoundry2 / aifoundry3 / aifoundry1-c1); 100 launches queued back to back: 103.6 / 103.7 / 104.1 µs each (103.6-104.1 µs) on 32 shires and 91.2 / 92.2 / 92.4 on one shire. The card's own cost is the queued figure: a lone launch waited for adds 463 / 452 / 461 µs (452-463 µs, each run's difference), most of the runtime's 500 µs idle poll (fact pcie.poll), and a one-shire lone launch takes the same 566 / 556 / 565 µs.
measured
three cards
Over the PCIe link ↗
pcie.launch
Two host-to-device commands in flight on one stream move 6.09 / 6.09 / 6.03 GB/s (aifoundry2 / aifoundry3 / aifoundry1-c1), half the 12.39 / 12.48 / 12.28 GB/s of one command at a time (two streams with both of each stream's commands in flight, four in all: 5.96 / 6.00 / 5.96 GB/s in total; with one command in flight in each of two streams nothing is lost, 1.012 of one at a time on aifoundry3, 1.014 on aifoundry2 and 1.019 on aifoundry1-c1, E55); both directions at once, one command each at a time, move 16.97 / 16.89 / 16.92 GB/s together (2 × 64 MB per stream, DMA only).
measured
three cards
Over the PCIe link ↗
pcie.conc
A host-to-card copy goes through each line's L3 home, which allocates the line: after a staged 4 MB copy, 99.5% of the lines read at L3 latency on aifoundry3 (99.6% on aifoundry2, 99.9% on aifoundry1-c1), whether the L3 held the buffer before or not, and every value read was the last one written. A kernel's first touch of a freshly copied buffer hits the L3, not DRAM (tested for a 4 MB buffer).
measured
three cards
Over the PCIe link ↗
pcie.write-l3
A line's L3 home shire is PA[10:6]: consecutive 64-byte lines rotate over the 32 compute shires' L3 slices (default 'swizzle0'; the firmware leaves the swizzle register at reset).
measured
three cards
Anatomy of a memory access ↗
l3.home
Host link: PCIe Gen4 x8, 15.75 GB/s per direction before protocol overhead; the transfers were timed on three cards on 27 September (facts pcie.h2d and pcie.d2h give the measured rates).
documented
Ridge points ↗
bw-pcie
The PCIe shire contains two independent dual-mode PCIe controllers and an 8-lane PCIe Gen4 PHY, factory-configured as an endpoint; the dev card exposes a Gen4 x8 host interface.
documented
Ridge points ↗
chip.pcie-shire
40-bit physical address space (1 TB): I/O 0x00_0000_0000 (1 GB), service processor 0x00_4000_0000 (1 GB), scratchpad 0x00_8000_0000 (2 GB), ESRs 0x01_0000_0000 (4 GB), PCIe 0x40_0000_0000 (256 GB), DRAM 0x80_0000_0000 (512 GB).
documented
no published page yet
addr.regions
The DRAM region starts at 0x80_0000_0000; minions reach only the 'Low' view (M-mode low 8 MB, OS low to 0x80_FFFF_FFFF, memory low 0x81_0000_0000-0x87_FFFF_FFFF, 28 GB); device allocations come back as 0x80_xxxx_xxxx addresses.
documented
no published page yet
addr.dram-region
The memory shire serving a line is PA[8:6] (so it is always the L3 home shire's low three bits) and the controller/channel within it is PA[9]: consecutive 64 B lines rotate over the 8 memory shires, the two channels alternate every 512 B.
measured
aifoundry2
Anatomy of a memory access ↗
dram.memshire-select
In the firmware's maps the four cells that hold no compute shire are: logical (0, 3), shire 32, the master; (5, 3), shire 33, the spare; (0, 4), the PCIe shire ('pcie0' in the bridge map); and (0, 5), the I/O shire ('io0'). On this die view that puts the master in the north cell and the spare in the south one, with PCIe then I/O east of the master.
documented
no published page yet
fw.grey-cells
The master shire (which runs the master-minion firmware and schedules kernels) is shire 32 in the firmware; its 2.5 MB scratchpad at 0x9000_0000 holds the firmware's host-interface buffers.
documented
Limits of observability ↗
chip.master-shire-id
The driver reports compute shire mask 0xffffffff (shires 0-31) and sync (master) shire 32 on every card.
measured
three cards
The DVFS loop and its leakage ↗
chip.cm-shire-mask
The mesh routes in dimension order, and a request and its reply take opposite orders: a request goes x first, then y, and a reply y first, then x, on the logical map, so a reply retraces its request's route backwards. Measured on 29 September (E56) with sets of streams between shires chosen so that their streams share one directed link under one order and none under the other: 1 KB tensor loads, whose data travel as replies, fell to 0.54-0.77 of their bandwidth alone when they shared a link under y first and held at 1.00 when they shared one under x first; tensor stores, whose data travel as requests, showed the mirror (0.52-0.76 against 1.00). A shared link carried about 92 GB/s. The same on aifoundry1 card 1 (development), aifoundry3 (the frozen validation) and aifoundry2 (the same frozen test, run as a third card on the evening of 29 September), three passes each.
measured
three cards
no published page yet
L104+}

## flow/F/2
FLOW 6 · HOST AND PCIE
DMA alone: 12.46–12.60 … each part takes.

 More detail and the sources {+

The host writes a kernel's buffers into device DRAM through the PCIe shire (device allocations are DRAM addresses from 0x80_0000_0000), then posts the launch to the master shire, whose firmware starts it on the compute shires. Timed on three cards on 27 September, five runs each, against predictions written before the runs.

 Leg What happens
the link trained at 16.0 GT/s x8 on every card: 15.75 GB/s per direction
DMA 12.46–12.60 GB/s to the card, 10.41–10.54 GB/s back: 79–80% and 66–67% of the link
staged a program's copies: 7.15 / 5.20 / 7.79 GB/s (host memcpy 17.4 / 9.2 / 21.4 GB/s first, then the DMA)
into DRAM each line through its L3 home (PA[10:6]), which keeps it: 99.5% of a copied buffer's lines then read at L3 latency (E55); the L3's write-back to the 8 memory shires (PA[8:6]) not timed
launch an empty kernel on 32 shires: 103.6 / 103.7 / 104.1 µs each when queued, the card's own cost; one launch waited for takes 566 / 556 / 565 µs, the extra 452–463 µs mostly the runtime's 500 µs idle poll
small copies a lone 4 KB copy: 377 / 379 / 411 µs, the runtime's polling (50 µs in flight, 500 µs idle)

 Values are per card: aifoundry2 / aifoundry3 / aifoundry1 card 1, where three are given.

 Inferred or open here, and what would settle it (2)

 Settled: PCIe bandwidth (PCIe shire, Host, Flow 6)

 Was: 15.75 GB/s per direction, the Gen4 x8 link figure, with host transfers never timed.

 How: Settled on 27 September: timed on three cards with workloads/pciebench, five runs per card against predictions stated before the runs (docs/reports/data/2026-09-27-pcie; the page Over the PCIe link). Not a team ask.

 Nearly settled: the Host -> DRAM path (Flow 6, 'Into DRAM')

 Measured on 29 September (E55, fact pcie.write-l3): the host's writes go through their lines' L3 homes, which allocate the lines. After a staged 4 MB copy 99.5% of the lines read at L3 latency on aifoundry3 (99.6% on aifoundry2, 99.9% on aifoundry1 card 1), whether the L3 held the buffer before or not, and no value read was stale. Still inferred, and drawn dashed: the L3's later write-back of those lines to the memory shires and DRAM.

 What settles it, and what is left: Settled by experiment: copy a buffer from the host, then time each line's first load in a kernel launched without the L3 flush; L3-hit latency means through the L3 homes (tools/claims-v3/pcie2/PREREG.md, frozen before the validation; docs/reports/data/2026-09-29-pcie2). What is left: why the bridge sends the writes there. The PCIe shire's to-sys bridge has DRAM address-map entries for every shire's L3 slave (SHn_L3D) and for each memory shire (MC0..MC7_MEM) (etsoc-hal hwinc/noc_esr.h, BRIDGE_PS0_TOSYS ... MAP_MEM_DRAM), so the programmed ADBASE/ADMASK decide: read them (SP-only) or the NoC documents.

 On the hub: rung 34: First touch after a host copy: does the host write through the L3? ↗ · rung 21: The NoC's reference manual and specification ↗ · rung 27: A way to read the NoC's router and bridge registers ↗

 Inferred: the host link's open questions (PCIe shire, Host, Flow 6)

 Not inferred but unexplained, from the PCIe page: why two host-to-card DMA commands of one stream at once move half as much as one, and why card-to-host DMA dips at 32-64 MB per copy. E55 (29 September) found where the loss is: two commands in flight in one stream move 0.488 of one at 2 x 64 MB on aifoundry3, one command in each of two streams 1.012 (T35-S; 0.496 and 1.014 on aifoundry2), and a shared read engine, the IOMMU, a fixed cost per overlap, a slow onset and a loss per element were refuted on all three cards tested. aifoundry3's host copies memory at about half the others' rate because it runs one memory channel (docs/reports/data/2026-09-27-pcie/hosts.txt).

 What would settle it: What serves one stream's two commands in turn: the runtime's source for a stream's DMA queue, or the master minion's DMA worker in the firmware; the PCIe DMA engine's documentation, or the settings the firmware programs (channel arbitration, read-request size, element splitting), for the card-to-host dip; the lab admin's reads on the hosts (lspci -vvv for the payload and read-request sizes).

 On the hub: rung 35: Why two host-to-card DMA commands halve the rate: a command-size sweep, and the IOMMU in passthrough ↗ · rung 29: The PCIe DMA engine's documentation and the settings the firmware gives it ↗ · rung 30: Two readings on the lab hosts that need root ↗

 Measured and explained in Over the PCIe link ↗.

 The facts this flow uses (20): point at one for its source

 The link trained at 16.0 GT/s x8 on all three cards in every run (sysfs current_link_speed and current_link_width): PCIe Gen4 x8, 15.75 GB/s per direction after 128b/130b coding.
measured
three cards
Over the PCIe link ↗
pcie.negotiated
Host to device, DMA only (the runtime's host-side copy replaced by a no-op, the analogue of pinned memory), 256 MB per copy: 12.47 [12.39, 12.55] GB/s on aifoundry2, 12.60 [12.55, 12.65] GB/s on aifoundry3, 12.46 [12.41, 12.50] GB/s on aifoundry1-c1 (mean of 5 runs [99% interval]): 12.46-12.60 GB/s, 79-80% of the link's 15.75 GB/s.
measured
three cards
Over the PCIe link ↗
pcie.h2d
Device to host, DMA only, 256 MB per copy: 10.54 [10.43, 10.64] GB/s on aifoundry2, 10.41 [10.30, 10.52] GB/s on aifoundry3, 10.41 [10.38, 10.45] GB/s on aifoundry1-c1: 10.41-10.54 GB/s, 66-67% of the link figure, slower than host to device. The fastest device-to-host size is 16 MB on aifoundry2 (11.75 GB/s), 16 MB on aifoundry3 (10.99 GB/s), 16 MB on aifoundry1-c1 (10.69 GB/s).
measured
three cards
Over the PCIe link ↗
pcie.d2h
The path a program takes, the runtime's staged copy (a host memcpy into a CMA bounce buffer, then the DMA), 256 MB: host to device 7.15 / 5.20 / 7.79 GB/s (5.20-7.79), device to host 6.53 / 4.78 / 6.97 GB/s (aifoundry2 / aifoundry3 / aifoundry1-c1). The hosts' own memcpy runs at 17.4 / 9.2 / 21.4 GB/s, and each staged rate is 98-100% of 1/(1/DMA + 1/memcpy): the runtime copies and then transfers, one after the other, so a slow host memcpy (aifoundry3's) cuts the staged rate on the same link to 0.67-0.73 of the other hosts' (host to device).
measured
three cards
Over the PCIe link ↗
pcie.staged
A DMA-only host-to-device copy reaches half its 256 MB rate at 2.0 / 2.1 / 2.2 MB per copy (aifoundry2 / aifoundry3 / aifoundry1-c1; n½, from the mean over five runs of log2 of the size): smaller copies are dominated by the per-command time.
measured
three cards
Over the PCIe link ↗
pcie.nhalf
A 4 KB copy issued after a random 0-1 ms gap takes 377 / 379 / 411 µs on average (377-411 µs; aifoundry2 / aifoundry3 / aifoundry1-c1; the mean over the four copy variants), while 200 queued 4 KB copies take 38 / 13 / 30 µs each (host to device, staged) and a wait on an idle stream 2.6 / 0.4 / 2.3 µs. The time of a lone small copy is the runtime's response polling, not the link.
measured
three cards
Over the PCIe link ↗
pcie.small
The runtime's response thread polls the device's completion queue, sleeping 50 µs between polls while commands are in flight and 500 µs when none are.
documented
Over the PCIe link ↗
pcie.poll
An empty kernel on all 32 compute shires, launched and waited for: 566 / 556 / 565 µs (556-566 µs) from launch to completion (aifoundry2 / aifoundry3 / aifoundry1-c1); 100 launches queued back to back: 103.6 / 103.7 / 104.1 µs each (103.6-104.1 µs) on 32 shires and 91.2 / 92.2 / 92.4 on one shire. The card's own cost is the queued figure: a lone launch waited for adds 463 / 452 / 461 µs (452-463 µs, each run's difference), most of the runtime's 500 µs idle poll (fact pcie.poll), and a one-shire lone launch takes the same 566 / 556 / 565 µs.
measured
three cards
Over the PCIe link ↗
pcie.launch
Two host-to-device commands in flight on one stream move 6.09 / 6.09 / 6.03 GB/s (aifoundry2 / aifoundry3 / aifoundry1-c1), half the 12.39 / 12.48 / 12.28 GB/s of one command at a time (two streams with both of each stream's commands in flight, four in all: 5.96 / 6.00 / 5.96 GB/s in total; with one command in flight in each of two streams nothing is lost, 1.012 of one at a time on aifoundry3, 1.014 on aifoundry2 and 1.019 on aifoundry1-c1, E55); both directions at once, one command each at a time, move 16.97 / 16.89 / 16.92 GB/s together (2 × 64 MB per stream, DMA only).
measured
three cards
Over the PCIe link ↗
pcie.conc
A host-to-card copy goes through each line's L3 home, which allocates the line: after a staged 4 MB copy, 99.5% of the lines read at L3 latency on aifoundry3 (99.6% on aifoundry2, 99.9% on aifoundry1-c1), whether the L3 held the buffer before or not, and every value read was the last one written. A kernel's first touch of a freshly copied buffer hits the L3, not DRAM (tested for a 4 MB buffer).
measured
three cards
Over the PCIe link ↗
pcie.write-l3
A line's L3 home shire is PA[10:6]: consecutive 64-byte lines rotate over the 32 compute shires' L3 slices (default 'swizzle0'; the firmware leaves the swizzle register at reset).
measured
three cards
Anatomy of a memory access ↗
l3.home
Host link: PCIe Gen4 x8, 15.75 GB/s per direction before protocol overhead; the transfers were timed on three cards on 27 September (facts pcie.h2d and pcie.d2h give the measured rates).
documented
Ridge points ↗
bw-pcie
The PCIe shire contains two independent dual-mode PCIe controllers and an 8-lane PCIe Gen4 PHY, factory-configured as an endpoint; the dev card exposes a Gen4 x8 host interface.
documented
Ridge points ↗
chip.pcie-shire
40-bit physical address space (1 TB): I/O 0x00_0000_0000 (1 GB), service processor 0x00_4000_0000 (1 GB), scratchpad 0x00_8000_0000 (2 GB), ESRs 0x01_0000_0000 (4 GB), PCIe 0x40_0000_0000 (256 GB), DRAM 0x80_0000_0000 (512 GB).
documented
no published page yet
addr.regions
The DRAM region starts at 0x80_0000_0000; minions reach only the 'Low' view (M-mode low 8 MB, OS low to 0x80_FFFF_FFFF, memory low 0x81_0000_0000-0x87_FFFF_FFFF, 28 GB); device allocations come back as 0x80_xxxx_xxxx addresses.
documented
no published page yet
addr.dram-region
The memory shire serving a line is PA[8:6] (so it is always the L3 home shire's low three bits) and the controller/channel within it is PA[9]: consecutive 64 B lines rotate over the 8 memory shires, the two channels alternate every 512 B.
measured
aifoundry2
Anatomy of a memory access ↗
dram.memshire-select
In the firmware's maps the four cells that hold no compute shire are: logical (0, 3), shire 32, the master; (5, 3), shire 33, the spare; (0, 4), the PCIe shire ('pcie0' in the bridge map); and (0, 5), the I/O shire ('io0'). On this die view that puts the master in the north cell and the spare in the south one, with PCIe then I/O east of the master.
documented
no published page yet
fw.grey-cells
The master shire (which runs the master-minion firmware and schedules kernels) is shire 32 in the firmware; its 2.5 MB scratchpad at 0x9000_0000 holds the firmware's host-interface buffers.
documented
Limits of observability ↗
chip.master-shire-id
The driver reports compute shire mask 0xffffffff (shires 0-31) and sync (master) shire 32 on every card.
measured
three cards
The DVFS loop and its leakage ↗
chip.cm-shire-mask
The mesh routes in dimension order, and a request and its reply take opposite orders: a request goes x first, then y, and a reply y first, then x, on the logical map, so a reply retraces its request's route backwards. Measured on 29 September (E56) with sets of streams between shires chosen so that their streams share one directed link under one order and none under the other: 1 KB tensor loads, whose data travel as replies, fell to 0.54-0.77 of their bandwidth alone when they shared a link under y first and held at 1.00 when they shared one under x first; tensor stores, whose data travel as requests, showed the mirror (0.52-0.76 against 1.00). A shared link carried about 92 GB/s. The same on aifoundry1 card 1 (development), aifoundry3 (the frozen validation) and aifoundry2 (the same frozen test, run as a third card on the evening of 29 September), three passes each.
measured
three cards
no published page yet
L104+}

## flow/F/3
FLOW 6 · HOST AND PCIE
A program's copy … each part takes.

 More detail and the sources {+

The host writes a kernel's buffers into device DRAM through the PCIe shire (device allocations are DRAM addresses from 0x80_0000_0000), then posts the launch to the master shire, whose firmware starts it on the compute shires. Timed on three cards on 27 September, five runs each, against predictions written before the runs.

 Leg What happens
the link trained at 16.0 GT/s x8 on every card: 15.75 GB/s per direction
DMA 12.46–12.60 GB/s to the card, 10.41–10.54 GB/s back: 79–80% and 66–67% of the link
staged a program's copies: 7.15 / 5.20 / 7.79 GB/s (host memcpy 17.4 / 9.2 / 21.4 GB/s first, then the DMA)
into DRAM each line through its L3 home (PA[10:6]), which keeps it: 99.5% of a copied buffer's lines then read at L3 latency (E55); the L3's write-back to the 8 memory shires (PA[8:6]) not timed
launch an empty kernel on 32 shires: 103.6 / 103.7 / 104.1 µs each when queued, the card's own cost; one launch waited for takes 566 / 556 / 565 µs, the extra 452–463 µs mostly the runtime's 500 µs idle poll
small copies a lone 4 KB copy: 377 / 379 / 411 µs, the runtime's polling (50 µs in flight, 500 µs idle)

 Values are per card: aifoundry2 / aifoundry3 / aifoundry1 card 1, where three are given.

 Inferred or open here, and what would settle it (2)

 Settled: PCIe bandwidth (PCIe shire, Host, Flow 6)

 Was: 15.75 GB/s per direction, the Gen4 x8 link figure, with host transfers never timed.

 How: Settled on 27 September: timed on three cards with workloads/pciebench, five runs per card against predictions stated before the runs (docs/reports/data/2026-09-27-pcie; the page Over the PCIe link). Not a team ask.

 Nearly settled: the Host -> DRAM path (Flow 6, 'Into DRAM')

 Measured on 29 September (E55, fact pcie.write-l3): the host's writes go through their lines' L3 homes, which allocate the lines. After a staged 4 MB copy 99.5% of the lines read at L3 latency on aifoundry3 (99.6% on aifoundry2, 99.9% on aifoundry1 card 1), whether the L3 held the buffer before or not, and no value read was stale. Still inferred, and drawn dashed: the L3's later write-back of those lines to the memory shires and DRAM.

 What settles it, and what is left: Settled by experiment: copy a buffer from the host, then time each line's first load in a kernel launched without the L3 flush; L3-hit latency means through the L3 homes (tools/claims-v3/pcie2/PREREG.md, frozen before the validation; docs/reports/data/2026-09-29-pcie2). What is left: why the bridge sends the writes there. The PCIe shire's to-sys bridge has DRAM address-map entries for every shire's L3 slave (SHn_L3D) and for each memory shire (MC0..MC7_MEM) (etsoc-hal hwinc/noc_esr.h, BRIDGE_PS0_TOSYS ... MAP_MEM_DRAM), so the programmed ADBASE/ADMASK decide: read them (SP-only) or the NoC documents.

 On the hub: rung 34: First touch after a host copy: does the host write through the L3? ↗ · rung 21: The NoC's reference manual and specification ↗ · rung 27: A way to read the NoC's router and bridge registers ↗

 Inferred: the host link's open questions (PCIe shire, Host, Flow 6)

 Not inferred but unexplained, from the PCIe page: why two host-to-card DMA commands of one stream at once move half as much as one, and why card-to-host DMA dips at 32-64 MB per copy. E55 (29 September) found where the loss is: two commands in flight in one stream move 0.488 of one at 2 x 64 MB on aifoundry3, one command in each of two streams 1.012 (T35-S; 0.496 and 1.014 on aifoundry2), and a shared read engine, the IOMMU, a fixed cost per overlap, a slow onset and a loss per element were refuted on all three cards tested. aifoundry3's host copies memory at about half the others' rate because it runs one memory channel (docs/reports/data/2026-09-27-pcie/hosts.txt).

 What would settle it: What serves one stream's two commands in turn: the runtime's source for a stream's DMA queue, or the master minion's DMA worker in the firmware; the PCIe DMA engine's documentation, or the settings the firmware programs (channel arbitration, read-request size, element splitting), for the card-to-host dip; the lab admin's reads on the hosts (lspci -vvv for the payload and read-request sizes).

 On the hub: rung 35: Why two host-to-card DMA commands halve the rate: a command-size sweep, and the IOMMU in passthrough ↗ · rung 29: The PCIe DMA engine's documentation and the settings the firmware gives it ↗ · rung 30: Two readings on the lab hosts that need root ↗

 Measured and explained in Over the PCIe link ↗.

 The facts this flow uses (20): point at one for its source

 The link trained at 16.0 GT/s x8 on all three cards in every run (sysfs current_link_speed and current_link_width): PCIe Gen4 x8, 15.75 GB/s per direction after 128b/130b coding.
measured
three cards
Over the PCIe link ↗
pcie.negotiated
Host to device, DMA only (the runtime's host-side copy replaced by a no-op, the analogue of pinned memory), 256 MB per copy: 12.47 [12.39, 12.55] GB/s on aifoundry2, 12.60 [12.55, 12.65] GB/s on aifoundry3, 12.46 [12.41, 12.50] GB/s on aifoundry1-c1 (mean of 5 runs [99% interval]): 12.46-12.60 GB/s, 79-80% of the link's 15.75 GB/s.
measured
three cards
Over the PCIe link ↗
pcie.h2d
Device to host, DMA only, 256 MB per copy: 10.54 [10.43, 10.64] GB/s on aifoundry2, 10.41 [10.30, 10.52] GB/s on aifoundry3, 10.41 [10.38, 10.45] GB/s on aifoundry1-c1: 10.41-10.54 GB/s, 66-67% of the link figure, slower than host to device. The fastest device-to-host size is 16 MB on aifoundry2 (11.75 GB/s), 16 MB on aifoundry3 (10.99 GB/s), 16 MB on aifoundry1-c1 (10.69 GB/s).
measured
three cards
Over the PCIe link ↗
pcie.d2h
The path a program takes, the runtime's staged copy (a host memcpy into a CMA bounce buffer, then the DMA), 256 MB: host to device 7.15 / 5.20 / 7.79 GB/s (5.20-7.79), device to host 6.53 / 4.78 / 6.97 GB/s (aifoundry2 / aifoundry3 / aifoundry1-c1). The hosts' own memcpy runs at 17.4 / 9.2 / 21.4 GB/s, and each staged rate is 98-100% of 1/(1/DMA + 1/memcpy): the runtime copies and then transfers, one after the other, so a slow host memcpy (aifoundry3's) cuts the staged rate on the same link to 0.67-0.73 of the other hosts' (host to device).
measured
three cards
Over the PCIe link ↗
pcie.staged
A DMA-only host-to-device copy reaches half its 256 MB rate at 2.0 / 2.1 / 2.2 MB per copy (aifoundry2 / aifoundry3 / aifoundry1-c1; n½, from the mean over five runs of log2 of the size): smaller copies are dominated by the per-command time.
measured
three cards
Over the PCIe link ↗
pcie.nhalf
A 4 KB copy issued after a random 0-1 ms gap takes 377 / 379 / 411 µs on average (377-411 µs; aifoundry2 / aifoundry3 / aifoundry1-c1; the mean over the four copy variants), while 200 queued 4 KB copies take 38 / 13 / 30 µs each (host to device, staged) and a wait on an idle stream 2.6 / 0.4 / 2.3 µs. The time of a lone small copy is the runtime's response polling, not the link.
measured
three cards
Over the PCIe link ↗
pcie.small
The runtime's response thread polls the device's completion queue, sleeping 50 µs between polls while commands are in flight and 500 µs when none are.
documented
Over the PCIe link ↗
pcie.poll
An empty kernel on all 32 compute shires, launched and waited for: 566 / 556 / 565 µs (556-566 µs) from launch to completion (aifoundry2 / aifoundry3 / aifoundry1-c1); 100 launches queued back to back: 103.6 / 103.7 / 104.1 µs each (103.6-104.1 µs) on 32 shires and 91.2 / 92.2 / 92.4 on one shire. The card's own cost is the queued figure: a lone launch waited for adds 463 / 452 / 461 µs (452-463 µs, each run's difference), most of the runtime's 500 µs idle poll (fact pcie.poll), and a one-shire lone launch takes the same 566 / 556 / 565 µs.
measured
three cards
Over the PCIe link ↗
pcie.launch
Two host-to-device commands in flight on one stream move 6.09 / 6.09 / 6.03 GB/s (aifoundry2 / aifoundry3 / aifoundry1-c1), half the 12.39 / 12.48 / 12.28 GB/s of one command at a time (two streams with both of each stream's commands in flight, four in all: 5.96 / 6.00 / 5.96 GB/s in total; with one command in flight in each of two streams nothing is lost, 1.012 of one at a time on aifoundry3, 1.014 on aifoundry2 and 1.019 on aifoundry1-c1, E55); both directions at once, one command each at a time, move 16.97 / 16.89 / 16.92 GB/s together (2 × 64 MB per stream, DMA only).
measured
three cards
Over the PCIe link ↗
pcie.conc
A host-to-card copy goes through each line's L3 home, which allocates the line: after a staged 4 MB copy, 99.5% of the lines read at L3 latency on aifoundry3 (99.6% on aifoundry2, 99.9% on aifoundry1-c1), whether the L3 held the buffer before or not, and every value read was the last one written. A kernel's first touch of a freshly copied buffer hits the L3, not DRAM (tested for a 4 MB buffer).
measured
three cards
Over the PCIe link ↗
pcie.write-l3
A line's L3 home shire is PA[10:6]: consecutive 64-byte lines rotate over the 32 compute shires' L3 slices (default 'swizzle0'; the firmware leaves the swizzle register at reset).
measured
three cards
Anatomy of a memory access ↗
l3.home
Host link: PCIe Gen4 x8, 15.75 GB/s per direction before protocol overhead; the transfers were timed on three cards on 27 September (facts pcie.h2d and pcie.d2h give the measured rates).
documented
Ridge points ↗
bw-pcie
The PCIe shire contains two independent dual-mode PCIe controllers and an 8-lane PCIe Gen4 PHY, factory-configured as an endpoint; the dev card exposes a Gen4 x8 host interface.
documented
Ridge points ↗
chip.pcie-shire
40-bit physical address space (1 TB): I/O 0x00_0000_0000 (1 GB), service processor 0x00_4000_0000 (1 GB), scratchpad 0x00_8000_0000 (2 GB), ESRs 0x01_0000_0000 (4 GB), PCIe 0x40_0000_0000 (256 GB), DRAM 0x80_0000_0000 (512 GB).
documented
no published page yet
addr.regions
The DRAM region starts at 0x80_0000_0000; minions reach only the 'Low' view (M-mode low 8 MB, OS low to 0x80_FFFF_FFFF, memory low 0x81_0000_0000-0x87_FFFF_FFFF, 28 GB); device allocations come back as 0x80_xxxx_xxxx addresses.
documented
no published page yet
addr.dram-region
The memory shire serving a line is PA[8:6] (so it is always the L3 home shire's low three bits) and the controller/channel within it is PA[9]: consecutive 64 B lines rotate over the 8 memory shires, the two channels alternate every 512 B.
measured
aifoundry2
Anatomy of a memory access ↗
dram.memshire-select
In the firmware's maps the four cells that hold no compute shire are: logical (0, 3), shire 32, the master; (5, 3), shire 33, the spare; (0, 4), the PCIe shire ('pcie0' in the bridge map); and (0, 5), the I/O shire ('io0'). On this die view that puts the master in the north cell and the spare in the south one, with PCIe then I/O east of the master.
documented
no published page yet
fw.grey-cells
The master shire (which runs the master-minion firmware and schedules kernels) is shire 32 in the firmware; its 2.5 MB scratchpad at 0x9000_0000 holds the firmware's host-interface buffers.
documented
Limits of observability ↗
chip.master-shire-id
The driver reports compute shire mask 0xffffffff (shires 0-31) and sync (master) shire 32 on every card.
measured
three cards
The DVFS loop and its leakage ↗
chip.cm-shire-mask
The mesh routes in dimension order, and a request and its reply take opposite orders: a request goes x first, then y, and a reply y first, then x, on the logical map, so a reply retraces its request's route backwards. Measured on 29 September (E56) with sets of streams between shires chosen so that their streams share one directed link under one order and none under the other: 1 KB tensor loads, whose data travel as replies, fell to 0.54-0.77 of their bandwidth alone when they shared a link under y first and held at 1.00 when they shared one under x first; tensor stores, whose data travel as requests, showed the mirror (0.52-0.76 against 1.00). A shared link carried about 92 GB/s. The same on aifoundry1 card 1 (development), aifoundry3 (the frozen validation) and aifoundry2 (the same frozen test, run as a third card on the evening of 29 September), three passes each.
measured
three cards
no published page yet
L104+}

## flow/F/4
FLOW 6 · HOST AND PCIE
Each line of … each part takes.

 More detail and the sources {+

The host writes a kernel's buffers into device DRAM through the PCIe shire (device allocations are DRAM addresses from 0x80_0000_0000), then posts the launch to the master shire, whose firmware starts it on the compute shires. Timed on three cards on 27 September, five runs each, against predictions written before the runs.

 Leg What happens
the link trained at 16.0 GT/s x8 on every card: 15.75 GB/s per direction
DMA 12.46–12.60 GB/s to the card, 10.41–10.54 GB/s back: 79–80% and 66–67% of the link
staged a program's copies: 7.15 / 5.20 / 7.79 GB/s (host memcpy 17.4 / 9.2 / 21.4 GB/s first, then the DMA)
into DRAM each line through its L3 home (PA[10:6]), which keeps it: 99.5% of a copied buffer's lines then read at L3 latency (E55); the L3's write-back to the 8 memory shires (PA[8:6]) not timed
launch an empty kernel on 32 shires: 103.6 / 103.7 / 104.1 µs each when queued, the card's own cost; one launch waited for takes 566 / 556 / 565 µs, the extra 452–463 µs mostly the runtime's 500 µs idle poll
small copies a lone 4 KB copy: 377 / 379 / 411 µs, the runtime's polling (50 µs in flight, 500 µs idle)

 Values are per card: aifoundry2 / aifoundry3 / aifoundry1 card 1, where three are given.

 Inferred or open here, and what would settle it (2)

 Settled: PCIe bandwidth (PCIe shire, Host, Flow 6)

 Was: 15.75 GB/s per direction, the Gen4 x8 link figure, with host transfers never timed.

 How: Settled on 27 September: timed on three cards with workloads/pciebench, five runs per card against predictions stated before the runs (docs/reports/data/2026-09-27-pcie; the page Over the PCIe link). Not a team ask.

 Nearly settled: the Host -> DRAM path (Flow 6, 'Into DRAM')

 Measured on 29 September (E55, fact pcie.write-l3): the host's writes go through their lines' L3 homes, which allocate the lines. After a staged 4 MB copy 99.5% of the lines read at L3 latency on aifoundry3 (99.6% on aifoundry2, 99.9% on aifoundry1 card 1), whether the L3 held the buffer before or not, and no value read was stale. Still inferred, and drawn dashed: the L3's later write-back of those lines to the memory shires and DRAM.

 What settles it, and what is left: Settled by experiment: copy a buffer from the host, then time each line's first load in a kernel launched without the L3 flush; L3-hit latency means through the L3 homes (tools/claims-v3/pcie2/PREREG.md, frozen before the validation; docs/reports/data/2026-09-29-pcie2). What is left: why the bridge sends the writes there. The PCIe shire's to-sys bridge has DRAM address-map entries for every shire's L3 slave (SHn_L3D) and for each memory shire (MC0..MC7_MEM) (etsoc-hal hwinc/noc_esr.h, BRIDGE_PS0_TOSYS ... MAP_MEM_DRAM), so the programmed ADBASE/ADMASK decide: read them (SP-only) or the NoC documents.

 On the hub: rung 34: First touch after a host copy: does the host write through the L3? ↗ · rung 21: The NoC's reference manual and specification ↗ · rung 27: A way to read the NoC's router and bridge registers ↗

 Inferred: the host link's open questions (PCIe shire, Host, Flow 6)

 Not inferred but unexplained, from the PCIe page: why two host-to-card DMA commands of one stream at once move half as much as one, and why card-to-host DMA dips at 32-64 MB per copy. E55 (29 September) found where the loss is: two commands in flight in one stream move 0.488 of one at 2 x 64 MB on aifoundry3, one command in each of two streams 1.012 (T35-S; 0.496 and 1.014 on aifoundry2), and a shared read engine, the IOMMU, a fixed cost per overlap, a slow onset and a loss per element were refuted on all three cards tested. aifoundry3's host copies memory at about half the others' rate because it runs one memory channel (docs/reports/data/2026-09-27-pcie/hosts.txt).

 What would settle it: What serves one stream's two commands in turn: the runtime's source for a stream's DMA queue, or the master minion's DMA worker in the firmware; the PCIe DMA engine's documentation, or the settings the firmware programs (channel arbitration, read-request size, element splitting), for the card-to-host dip; the lab admin's reads on the hosts (lspci -vvv for the payload and read-request sizes).

 On the hub: rung 35: Why two host-to-card DMA commands halve the rate: a command-size sweep, and the IOMMU in passthrough ↗ · rung 29: The PCIe DMA engine's documentation and the settings the firmware gives it ↗ · rung 30: Two readings on the lab hosts that need root ↗

 Measured and explained in Over the PCIe link ↗.

 The facts this flow uses (20): point at one for its source

 The link trained at 16.0 GT/s x8 on all three cards in every run (sysfs current_link_speed and current_link_width): PCIe Gen4 x8, 15.75 GB/s per direction after 128b/130b coding.
measured
three cards
Over the PCIe link ↗
pcie.negotiated
Host to device, DMA only (the runtime's host-side copy replaced by a no-op, the analogue of pinned memory), 256 MB per copy: 12.47 [12.39, 12.55] GB/s on aifoundry2, 12.60 [12.55, 12.65] GB/s on aifoundry3, 12.46 [12.41, 12.50] GB/s on aifoundry1-c1 (mean of 5 runs [99% interval]): 12.46-12.60 GB/s, 79-80% of the link's 15.75 GB/s.
measured
three cards
Over the PCIe link ↗
pcie.h2d
Device to host, DMA only, 256 MB per copy: 10.54 [10.43, 10.64] GB/s on aifoundry2, 10.41 [10.30, 10.52] GB/s on aifoundry3, 10.41 [10.38, 10.45] GB/s on aifoundry1-c1: 10.41-10.54 GB/s, 66-67% of the link figure, slower than host to device. The fastest device-to-host size is 16 MB on aifoundry2 (11.75 GB/s), 16 MB on aifoundry3 (10.99 GB/s), 16 MB on aifoundry1-c1 (10.69 GB/s).
measured
three cards
Over the PCIe link ↗
pcie.d2h
The path a program takes, the runtime's staged copy (a host memcpy into a CMA bounce buffer, then the DMA), 256 MB: host to device 7.15 / 5.20 / 7.79 GB/s (5.20-7.79), device to host 6.53 / 4.78 / 6.97 GB/s (aifoundry2 / aifoundry3 / aifoundry1-c1). The hosts' own memcpy runs at 17.4 / 9.2 / 21.4 GB/s, and each staged rate is 98-100% of 1/(1/DMA + 1/memcpy): the runtime copies and then transfers, one after the other, so a slow host memcpy (aifoundry3's) cuts the staged rate on the same link to 0.67-0.73 of the other hosts' (host to device).
measured
three cards
Over the PCIe link ↗
pcie.staged
A DMA-only host-to-device copy reaches half its 256 MB rate at 2.0 / 2.1 / 2.2 MB per copy (aifoundry2 / aifoundry3 / aifoundry1-c1; n½, from the mean over five runs of log2 of the size): smaller copies are dominated by the per-command time.
measured
three cards
Over the PCIe link ↗
pcie.nhalf
A 4 KB copy issued after a random 0-1 ms gap takes 377 / 379 / 411 µs on average (377-411 µs; aifoundry2 / aifoundry3 / aifoundry1-c1; the mean over the four copy variants), while 200 queued 4 KB copies take 38 / 13 / 30 µs each (host to device, staged) and a wait on an idle stream 2.6 / 0.4 / 2.3 µs. The time of a lone small copy is the runtime's response polling, not the link.
measured
three cards
Over the PCIe link ↗
pcie.small
The runtime's response thread polls the device's completion queue, sleeping 50 µs between polls while commands are in flight and 500 µs when none are.
documented
Over the PCIe link ↗
pcie.poll
An empty kernel on all 32 compute shires, launched and waited for: 566 / 556 / 565 µs (556-566 µs) from launch to completion (aifoundry2 / aifoundry3 / aifoundry1-c1); 100 launches queued back to back: 103.6 / 103.7 / 104.1 µs each (103.6-104.1 µs) on 32 shires and 91.2 / 92.2 / 92.4 on one shire. The card's own cost is the queued figure: a lone launch waited for adds 463 / 452 / 461 µs (452-463 µs, each run's difference), most of the runtime's 500 µs idle poll (fact pcie.poll), and a one-shire lone launch takes the same 566 / 556 / 565 µs.
measured
three cards
Over the PCIe link ↗
pcie.launch
Two host-to-device commands in flight on one stream move 6.09 / 6.09 / 6.03 GB/s (aifoundry2 / aifoundry3 / aifoundry1-c1), half the 12.39 / 12.48 / 12.28 GB/s of one command at a time (two streams with both of each stream's commands in flight, four in all: 5.96 / 6.00 / 5.96 GB/s in total; with one command in flight in each of two streams nothing is lost, 1.012 of one at a time on aifoundry3, 1.014 on aifoundry2 and 1.019 on aifoundry1-c1, E55); both directions at once, one command each at a time, move 16.97 / 16.89 / 16.92 GB/s together (2 × 64 MB per stream, DMA only).
measured
three cards
Over the PCIe link ↗
pcie.conc
A host-to-card copy goes through each line's L3 home, which allocates the line: after a staged 4 MB copy, 99.5% of the lines read at L3 latency on aifoundry3 (99.6% on aifoundry2, 99.9% on aifoundry1-c1), whether the L3 held the buffer before or not, and every value read was the last one written. A kernel's first touch of a freshly copied buffer hits the L3, not DRAM (tested for a 4 MB buffer).
measured
three cards
Over the PCIe link ↗
pcie.write-l3
A line's L3 home shire is PA[10:6]: consecutive 64-byte lines rotate over the 32 compute shires' L3 slices (default 'swizzle0'; the firmware leaves the swizzle register at reset).
measured
three cards
Anatomy of a memory access ↗
l3.home
Host link: PCIe Gen4 x8, 15.75 GB/s per direction before protocol overhead; the transfers were timed on three cards on 27 September (facts pcie.h2d and pcie.d2h give the measured rates).
documented
Ridge points ↗
bw-pcie
The PCIe shire contains two independent dual-mode PCIe controllers and an 8-lane PCIe Gen4 PHY, factory-configured as an endpoint; the dev card exposes a Gen4 x8 host interface.
documented
Ridge points ↗
chip.pcie-shire
40-bit physical address space (1 TB): I/O 0x00_0000_0000 (1 GB), service processor 0x00_4000_0000 (1 GB), scratchpad 0x00_8000_0000 (2 GB), ESRs 0x01_0000_0000 (4 GB), PCIe 0x40_0000_0000 (256 GB), DRAM 0x80_0000_0000 (512 GB).
documented
no published page yet
addr.regions
The DRAM region starts at 0x80_0000_0000; minions reach only the 'Low' view (M-mode low 8 MB, OS low to 0x80_FFFF_FFFF, memory low 0x81_0000_0000-0x87_FFFF_FFFF, 28 GB); device allocations come back as 0x80_xxxx_xxxx addresses.
documented
no published page yet
addr.dram-region
The memory shire serving a line is PA[8:6] (so it is always the L3 home shire's low three bits) and the controller/channel within it is PA[9]: consecutive 64 B lines rotate over the 8 memory shires, the two channels alternate every 512 B.
measured
aifoundry2
Anatomy of a memory access ↗
dram.memshire-select
In the firmware's maps the four cells that hold no compute shire are: logical (0, 3), shire 32, the master; (5, 3), shire 33, the spare; (0, 4), the PCIe shire ('pcie0' in the bridge map); and (0, 5), the I/O shire ('io0'). On this die view that puts the master in the north cell and the spare in the south one, with PCIe then I/O east of the master.
documented
no published page yet
fw.grey-cells
The master shire (which runs the master-minion firmware and schedules kernels) is shire 32 in the firmware; its 2.5 MB scratchpad at 0x9000_0000 holds the firmware's host-interface buffers.
documented
Limits of observability ↗
chip.master-shire-id
The driver reports compute shire mask 0xffffffff (shires 0-31) and sync (master) shire 32 on every card.
measured
three cards
The DVFS loop and its leakage ↗
chip.cm-shire-mask
The mesh routes in dimension order, and a request and its reply take opposite orders: a request goes x first, then y, and a reply y first, then x, on the logical map, so a reply retraces its request's route backwards. Measured on 29 September (E56) with sets of streams between shires chosen so that their streams share one directed link under one order and none under the other: 1 KB tensor loads, whose data travel as replies, fell to 0.54-0.77 of their bandwidth alone when they shared a link under y first and held at 1.00 when they shared one under x first; tensor stores, whose data travel as requests, showed the mirror (0.52-0.76 against 1.00). A shared link carried about 92 GB/s. The same on aifoundry1 card 1 (development), aifoundry3 (the frozen validation) and aifoundry2 (the same frozen test, run as a third card on the evening of 29 September), three passes each.
measured
three cards
no published page yet
L104+}

## flow/F/5
FLOW 6 · HOST AND PCIE
The master shire … each part takes.

 More detail and the sources {+

The host writes a kernel's buffers into device DRAM through the PCIe shire (device allocations are DRAM addresses from 0x80_0000_0000), then posts the launch to the master shire, whose firmware starts it on the compute shires. Timed on three cards on 27 September, five runs each, against predictions written before the runs.

 Leg What happens
the link trained at 16.0 GT/s x8 on every card: 15.75 GB/s per direction
DMA 12.46–12.60 GB/s to the card, 10.41–10.54 GB/s back: 79–80% and 66–67% of the link
staged a program's copies: 7.15 / 5.20 / 7.79 GB/s (host memcpy 17.4 / 9.2 / 21.4 GB/s first, then the DMA)
into DRAM each line through its L3 home (PA[10:6]), which keeps it: 99.5% of a copied buffer's lines then read at L3 latency (E55); the L3's write-back to the 8 memory shires (PA[8:6]) not timed
launch an empty kernel on 32 shires: 103.6 / 103.7 / 104.1 µs each when queued, the card's own cost; one launch waited for takes 566 / 556 / 565 µs, the extra 452–463 µs mostly the runtime's 500 µs idle poll
small copies a lone 4 KB copy: 377 / 379 / 411 µs, the runtime's polling (50 µs in flight, 500 µs idle)

 Values are per card: aifoundry2 / aifoundry3 / aifoundry1 card 1, where three are given.

 Inferred or open here, and what would settle it (2)

 Settled: PCIe bandwidth (PCIe shire, Host, Flow 6)

 Was: 15.75 GB/s per direction, the Gen4 x8 link figure, with host transfers never timed.

 How: Settled on 27 September: timed on three cards with workloads/pciebench, five runs per card against predictions stated before the runs (docs/reports/data/2026-09-27-pcie; the page Over the PCIe link). Not a team ask.

 Nearly settled: the Host -> DRAM path (Flow 6, 'Into DRAM')

 Measured on 29 September (E55, fact pcie.write-l3): the host's writes go through their lines' L3 homes, which allocate the lines. After a staged 4 MB copy 99.5% of the lines read at L3 latency on aifoundry3 (99.6% on aifoundry2, 99.9% on aifoundry1 card 1), whether the L3 held the buffer before or not, and no value read was stale. Still inferred, and drawn dashed: the L3's later write-back of those lines to the memory shires and DRAM.

 What settles it, and what is left: Settled by experiment: copy a buffer from the host, then time each line's first load in a kernel launched without the L3 flush; L3-hit latency means through the L3 homes (tools/claims-v3/pcie2/PREREG.md, frozen before the validation; docs/reports/data/2026-09-29-pcie2). What is left: why the bridge sends the writes there. The PCIe shire's to-sys bridge has DRAM address-map entries for every shire's L3 slave (SHn_L3D) and for each memory shire (MC0..MC7_MEM) (etsoc-hal hwinc/noc_esr.h, BRIDGE_PS0_TOSYS ... MAP_MEM_DRAM), so the programmed ADBASE/ADMASK decide: read them (SP-only) or the NoC documents.

 On the hub: rung 34: First touch after a host copy: does the host write through the L3? ↗ · rung 21: The NoC's reference manual and specification ↗ · rung 27: A way to read the NoC's router and bridge registers ↗

 Inferred: the host link's open questions (PCIe shire, Host, Flow 6)

 Not inferred but unexplained, from the PCIe page: why two host-to-card DMA commands of one stream at once move half as much as one, and why card-to-host DMA dips at 32-64 MB per copy. E55 (29 September) found where the loss is: two commands in flight in one stream move 0.488 of one at 2 x 64 MB on aifoundry3, one command in each of two streams 1.012 (T35-S; 0.496 and 1.014 on aifoundry2), and a shared read engine, the IOMMU, a fixed cost per overlap, a slow onset and a loss per element were refuted on all three cards tested. aifoundry3's host copies memory at about half the others' rate because it runs one memory channel (docs/reports/data/2026-09-27-pcie/hosts.txt).

 What would settle it: What serves one stream's two commands in turn: the runtime's source for a stream's DMA queue, or the master minion's DMA worker in the firmware; the PCIe DMA engine's documentation, or the settings the firmware programs (channel arbitration, read-request size, element splitting), for the card-to-host dip; the lab admin's reads on the hosts (lspci -vvv for the payload and read-request sizes).

 On the hub: rung 35: Why two host-to-card DMA commands halve the rate: a command-size sweep, and the IOMMU in passthrough ↗ · rung 29: The PCIe DMA engine's documentation and the settings the firmware gives it ↗ · rung 30: Two readings on the lab hosts that need root ↗

 Measured and explained in Over the PCIe link ↗.

 The facts this flow uses (20): point at one for its source

 The link trained at 16.0 GT/s x8 on all three cards in every run (sysfs current_link_speed and current_link_width): PCIe Gen4 x8, 15.75 GB/s per direction after 128b/130b coding.
measured
three cards
Over the PCIe link ↗
pcie.negotiated
Host to device, DMA only (the runtime's host-side copy replaced by a no-op, the analogue of pinned memory), 256 MB per copy: 12.47 [12.39, 12.55] GB/s on aifoundry2, 12.60 [12.55, 12.65] GB/s on aifoundry3, 12.46 [12.41, 12.50] GB/s on aifoundry1-c1 (mean of 5 runs [99% interval]): 12.46-12.60 GB/s, 79-80% of the link's 15.75 GB/s.
measured
three cards
Over the PCIe link ↗
pcie.h2d
Device to host, DMA only, 256 MB per copy: 10.54 [10.43, 10.64] GB/s on aifoundry2, 10.41 [10.30, 10.52] GB/s on aifoundry3, 10.41 [10.38, 10.45] GB/s on aifoundry1-c1: 10.41-10.54 GB/s, 66-67% of the link figure, slower than host to device. The fastest device-to-host size is 16 MB on aifoundry2 (11.75 GB/s), 16 MB on aifoundry3 (10.99 GB/s), 16 MB on aifoundry1-c1 (10.69 GB/s).
measured
three cards
Over the PCIe link ↗
pcie.d2h
The path a program takes, the runtime's staged copy (a host memcpy into a CMA bounce buffer, then the DMA), 256 MB: host to device 7.15 / 5.20 / 7.79 GB/s (5.20-7.79), device to host 6.53 / 4.78 / 6.97 GB/s (aifoundry2 / aifoundry3 / aifoundry1-c1). The hosts' own memcpy runs at 17.4 / 9.2 / 21.4 GB/s, and each staged rate is 98-100% of 1/(1/DMA + 1/memcpy): the runtime copies and then transfers, one after the other, so a slow host memcpy (aifoundry3's) cuts the staged rate on the same link to 0.67-0.73 of the other hosts' (host to device).
measured
three cards
Over the PCIe link ↗
pcie.staged
A DMA-only host-to-device copy reaches half its 256 MB rate at 2.0 / 2.1 / 2.2 MB per copy (aifoundry2 / aifoundry3 / aifoundry1-c1; n½, from the mean over five runs of log2 of the size): smaller copies are dominated by the per-command time.
measured
three cards
Over the PCIe link ↗
pcie.nhalf
A 4 KB copy issued after a random 0-1 ms gap takes 377 / 379 / 411 µs on average (377-411 µs; aifoundry2 / aifoundry3 / aifoundry1-c1; the mean over the four copy variants), while 200 queued 4 KB copies take 38 / 13 / 30 µs each (host to device, staged) and a wait on an idle stream 2.6 / 0.4 / 2.3 µs. The time of a lone small copy is the runtime's response polling, not the link.
measured
three cards
Over the PCIe link ↗
pcie.small
The runtime's response thread polls the device's completion queue, sleeping 50 µs between polls while commands are in flight and 500 µs when none are.
documented
Over the PCIe link ↗
pcie.poll
An empty kernel on all 32 compute shires, launched and waited for: 566 / 556 / 565 µs (556-566 µs) from launch to completion (aifoundry2 / aifoundry3 / aifoundry1-c1); 100 launches queued back to back: 103.6 / 103.7 / 104.1 µs each (103.6-104.1 µs) on 32 shires and 91.2 / 92.2 / 92.4 on one shire. The card's own cost is the queued figure: a lone launch waited for adds 463 / 452 / 461 µs (452-463 µs, each run's difference), most of the runtime's 500 µs idle poll (fact pcie.poll), and a one-shire lone launch takes the same 566 / 556 / 565 µs.
measured
three cards
Over the PCIe link ↗
pcie.launch
Two host-to-device commands in flight on one stream move 6.09 / 6.09 / 6.03 GB/s (aifoundry2 / aifoundry3 / aifoundry1-c1), half the 12.39 / 12.48 / 12.28 GB/s of one command at a time (two streams with both of each stream's commands in flight, four in all: 5.96 / 6.00 / 5.96 GB/s in total; with one command in flight in each of two streams nothing is lost, 1.012 of one at a time on aifoundry3, 1.014 on aifoundry2 and 1.019 on aifoundry1-c1, E55); both directions at once, one command each at a time, move 16.97 / 16.89 / 16.92 GB/s together (2 × 64 MB per stream, DMA only).
measured
three cards
Over the PCIe link ↗
pcie.conc
A host-to-card copy goes through each line's L3 home, which allocates the line: after a staged 4 MB copy, 99.5% of the lines read at L3 latency on aifoundry3 (99.6% on aifoundry2, 99.9% on aifoundry1-c1), whether the L3 held the buffer before or not, and every value read was the last one written. A kernel's first touch of a freshly copied buffer hits the L3, not DRAM (tested for a 4 MB buffer).
measured
three cards
Over the PCIe link ↗
pcie.write-l3
A line's L3 home shire is PA[10:6]: consecutive 64-byte lines rotate over the 32 compute shires' L3 slices (default 'swizzle0'; the firmware leaves the swizzle register at reset).
measured
three cards
Anatomy of a memory access ↗
l3.home
Host link: PCIe Gen4 x8, 15.75 GB/s per direction before protocol overhead; the transfers were timed on three cards on 27 September (facts pcie.h2d and pcie.d2h give the measured rates).
documented
Ridge points ↗
bw-pcie
The PCIe shire contains two independent dual-mode PCIe controllers and an 8-lane PCIe Gen4 PHY, factory-configured as an endpoint; the dev card exposes a Gen4 x8 host interface.
documented
Ridge points ↗
chip.pcie-shire
40-bit physical address space (1 TB): I/O 0x00_0000_0000 (1 GB), service processor 0x00_4000_0000 (1 GB), scratchpad 0x00_8000_0000 (2 GB), ESRs 0x01_0000_0000 (4 GB), PCIe 0x40_0000_0000 (256 GB), DRAM 0x80_0000_0000 (512 GB).
documented
no published page yet
addr.regions
The DRAM region starts at 0x80_0000_0000; minions reach only the 'Low' view (M-mode low 8 MB, OS low to 0x80_FFFF_FFFF, memory low 0x81_0000_0000-0x87_FFFF_FFFF, 28 GB); device allocations come back as 0x80_xxxx_xxxx addresses.
documented
no published page yet
addr.dram-region
The memory shire serving a line is PA[8:6] (so it is always the L3 home shire's low three bits) and the controller/channel within it is PA[9]: consecutive 64 B lines rotate over the 8 memory shires, the two channels alternate every 512 B.
measured
aifoundry2
Anatomy of a memory access ↗
dram.memshire-select
In the firmware's maps the four cells that hold no compute shire are: logical (0, 3), shire 32, the master; (5, 3), shire 33, the spare; (0, 4), the PCIe shire ('pcie0' in the bridge map); and (0, 5), the I/O shire ('io0'). On this die view that puts the master in the north cell and the spare in the south one, with PCIe then I/O east of the master.
documented
no published page yet
fw.grey-cells
The master shire (which runs the master-minion firmware and schedules kernels) is shire 32 in the firmware; its 2.5 MB scratchpad at 0x9000_0000 holds the firmware's host-interface buffers.
documented
Limits of observability ↗
chip.master-shire-id
The driver reports compute shire mask 0xffffffff (shires 0-31) and sync (master) shire 32 on every card.
measured
three cards
The DVFS loop and its leakage ↗
chip.cm-shire-mask
The mesh routes in dimension order, and a request and its reply take opposite orders: a request goes x first, then y, and a reply y first, then x, on the logical map, so a reply retraces its request's route backwards. Measured on 29 September (E56) with sets of streams between shires chosen so that their streams share one directed link under one order and none under the other: 1 KB tensor loads, whose data travel as replies, fell to 0.54-0.77 of their bandwidth alone when they shared a link under y first and held at 1.00 when they shared one under x first; tensor stores, whose data travel as requests, showed the mirror (0.52-0.76 against 1.00). A shared link carried about 92 GB/s. The same on aifoundry1 card 1 (development), aifoundry3 (the frozen validation) and aifoundry2 (the same frozen test, run as a third card on the evening of 29 September), three passes each.
measured
three cards
no published page yet
L104+}

## flow/G/0
FLOW 7 · MATMUL
Hart 0 issues TensorLoad: 16 … on every minion.

 More detail and the sources {+

One 16×16×16 fp32 step of a matmul, as the benchmark that sustains 9.51 TFLOP/s runs it on every minion: hart 0 loads a tile of A (16 lines, 1 KB) into the L1 scratchpad, streams B through TenB, and issues TensorFMA, which the vector unit's lanes run. The next A loads while the FMA runs.

 Leg What happens cycles
TensorLoad A 16 lines from the L2, three cards 160.4
B through TenB streamed with a paired load, into TenB
TensorFMA with B in TenB (546 cycles with B in the L1 scratchpad) 529.05–529.09
the next A loaded during the FMA: an op takes no longer than the FMA 529.001
32 minions each loads from the shire's L2; the cycles with all 1,024 loading 256.0
1,024 minions 9.51 TFLOP/s fp32, against a peak of 9.83 TFLOP/s
fed from DRAM 0.309–0.312 TFLOP/s; a load with all loading: 7,994–8,037 cycles; per op: 16,132–16,278

 Whether the loads hide behind the FMA was measured by the benchmark's own rate: it reloads A before every FMA and still runs at the FMA's speed. A version that waits for each load was never run.

 Measured and explained in The Horace experiment ↗.

 The facts this flow uses (17): point at one for its source

 TensorLoad reads up to 16 rows of 64 contiguous bytes (64 B aligned, row stride in x31) from memory into consecutive L1-scratchpad lines, bypassing the L1 data cache; a mask can skip rows.
documented
Sparse compute ↗
minion.tensorload
One minion's TensorLoad of 16 lines (1 KB) into its L1 scratchpad: 160.4 cycles from the L2 and 160.1 from the own scratchpad, on all three cards; 4 lines from the L2 take 41.9 cycles. From DRAM, 16 lines take 748-751 cycles on passes 2 and 3 and 1,132-1,133 on the first pass.
measured
three cards
The Horace experiment ↗
tl.one
All 1,024 minions tensor-loading at once: 256.0 cycles per 16-line load from the L2, and 7,994-8,037 cycles from DRAM (aifoundry2 / aifoundry3 / aifoundry1-c1: 8,037 / 7,994 / 8,021), where the memory shires set the pace.
measured
three cards
The Horace experiment ↗
tl.all
With A and B both in the L1 scratchpad a 16×16×16 fp32 TensorFMA takes 546 cycles (fp16 546, int8 318), identical for every data pattern.
measured
three cards
The Horace experiment ↗
minion.tensorfma-546
A 16×16×16 fp32 TensorFMA with B streamed through TenB instead of held in the L1 scratchpad: 529.05-529.09 cycles on all three cards (A in the L1 scratchpad).
measured
three cards
The Horace experiment ↗
tfma.tenb
The matmul benchmark loads a new A (16 lines from the shire's L2 into one of two L1-scratchpad buffers) and streams B through TenB before every TensorFMA, issuing the next op's loads while the current FMA runs, and it takes 529.001 cycles per op on all three cards: no more than the TensorFMA alone with B through TenB (529.05-529.09 cycles), so the next A's load of about 160 cycles is hidden behind the FMA.
model
three cards
Matmul efficiency ↗
mm.reload
Only hart 0 of a minion may issue tensor instructions; hart 1 may only issue TensorLoadL2Scp, TensorWait and tensor_coop accesses.
documented
Limits of observability ↗
minion.tensor-hart0
The tensor instructions run on the vector unit's own lanes: each of the 8 lanes holds the FMA (TxFMA) and the two int8 multiply-add (IMA/TIMA) units, and state machines in the VPU sequence the multi-cycle tensor operations on them. An 8-lane fmadd.ps does 16 FLOP per cycle, the same fp32 peak as TensorFMA.
documented
Ridge points ↗
minion.vec-peak
Tensor peak per minion-cycle: 16 fp32 / 32 fp16 / 128 int8 ops; 9.83 TFLOP/s, 19.7 TFLOP/s and 78.6 TOP/s on 1,024 minions at 600 MHz.
documented
Ridge points ↗
mm-peak
Tensor matmul, tiles in L2, all 1,024 minions at 600 MHz: 9.51 TFLOP/s fp32, 19.02 fp16, 71.77 TOP/s int8, the same on each card (91-97% of the 9.83 / 19.66 / 78.6 peak); 529 cycles per fp32/fp16 op, 280.35 per int8 op.
measured
three cards
Matmul efficiency ↗
mm-rate
Cooperative TensorLoad: identical tensor-load requests from minions (across the neighbourhoods of a shire) are synchronised and coalesced into one memory request; cooperative TensorStore combines pairs or quads of minions writing one line.
documented
no published page yet
neigh.coop-tload
Tensor loads skip the L1 but are cached in the L2 and L3; tensor stores skip the L1 and the L2.
inference
The energy manual ↗
minion.tensor-cache-path
The same benchmark with 64 private tiles per minion, so that every load comes from DRAM, on the three cards: 16,132-16,278 cycles per op on the slowest minion, whose finish sets the 0.309-0.312 TFLOP/s (15,042-15,663 on the average minion), about 30 times slower than with the tiles in the L2.
measured
three cards
Matmul efficiency ↗
mm.dram
Tensor load from the own scratchpad (catalogue): 2.12 pJ/B on zeros, 4.43 on random data; tensor store into it 4.65 / 8.58: a scratchpad write is twice a read.
measured
three cards
The energy manual ↗
e-scp-tload
Tensor load from DRAM (catalogue, both data sets): 94.6 pJ/B [86.2-105.7] on zeros, 132.6 [117.9-145.4] on random data; tensor store to DRAM 94.4 / 141.9. Even DRAM is data-dependent.
measured
three cards
The energy manual ↗
e-dram-tload
TensorFMA fp32 random: 5.782 pJ per multiply-add [5.347-6.133] above idle, all 1,024 minions; per card a2 5.920, a3 5.369, a1c1 6.058.
measured
three cards
The energy manual ↗
e-tfma-fp32
The mesh routes in dimension order, and a request and its reply take opposite orders: a request goes x first, then y, and a reply y first, then x, on the logical map, so a reply retraces its request's route backwards. Measured on 29 September (E56) with sets of streams between shires chosen so that their streams share one directed link under one order and none under the other: 1 KB tensor loads, whose data travel as replies, fell to 0.54-0.77 of their bandwidth alone when they shared a link under y first and held at 1.00 when they shared one under x first; tensor stores, whose data travel as requests, showed the mirror (0.52-0.76 against 1.00). A shared link carried about 92 GB/s. The same on aifoundry1 card 1 (development), aifoundry3 (the frozen validation) and aifoundry2 (the same frozen test, run as a third card on the evening of 29 September), three passes each.
measured
three cards
no published page yet
L104+}

## flow/G/1
FLOW 7 · MATMUL
Hart 0 issues TensorLoad: 16 … on every minion.

 More detail and the sources {+

One 16×16×16 fp32 step of a matmul, as the benchmark that sustains 9.51 TFLOP/s runs it on every minion: hart 0 loads a tile of A (16 lines, 1 KB) into the L1 scratchpad, streams B through TenB, and issues TensorFMA, which the vector unit's lanes run. The next A loads while the FMA runs.

 Leg What happens cycles
TensorLoad A 16 lines from the L2, three cards 160.4
B through TenB streamed with a paired load, into TenB
TensorFMA with B in TenB (546 cycles with B in the L1 scratchpad) 529.05–529.09
the next A loaded during the FMA: an op takes no longer than the FMA 529.001
32 minions each loads from the shire's L2; the cycles with all 1,024 loading 256.0
1,024 minions 9.51 TFLOP/s fp32, against a peak of 9.83 TFLOP/s
fed from DRAM 0.309–0.312 TFLOP/s; a load with all loading: 7,994–8,037 cycles; per op: 16,132–16,278

 Whether the loads hide behind the FMA was measured by the benchmark's own rate: it reloads A before every FMA and still runs at the FMA's speed. A version that waits for each load was never run.

 Measured and explained in The Horace experiment ↗.

 The facts this flow uses (17): point at one for its source

 TensorLoad reads up to 16 rows of 64 contiguous bytes (64 B aligned, row stride in x31) from memory into consecutive L1-scratchpad lines, bypassing the L1 data cache; a mask can skip rows.
documented
Sparse compute ↗
minion.tensorload
One minion's TensorLoad of 16 lines (1 KB) into its L1 scratchpad: 160.4 cycles from the L2 and 160.1 from the own scratchpad, on all three cards; 4 lines from the L2 take 41.9 cycles. From DRAM, 16 lines take 748-751 cycles on passes 2 and 3 and 1,132-1,133 on the first pass.
measured
three cards
The Horace experiment ↗
tl.one
All 1,024 minions tensor-loading at once: 256.0 cycles per 16-line load from the L2, and 7,994-8,037 cycles from DRAM (aifoundry2 / aifoundry3 / aifoundry1-c1: 8,037 / 7,994 / 8,021), where the memory shires set the pace.
measured
three cards
The Horace experiment ↗
tl.all
With A and B both in the L1 scratchpad a 16×16×16 fp32 TensorFMA takes 546 cycles (fp16 546, int8 318), identical for every data pattern.
measured
three cards
The Horace experiment ↗
minion.tensorfma-546
A 16×16×16 fp32 TensorFMA with B streamed through TenB instead of held in the L1 scratchpad: 529.05-529.09 cycles on all three cards (A in the L1 scratchpad).
measured
three cards
The Horace experiment ↗
tfma.tenb
The matmul benchmark loads a new A (16 lines from the shire's L2 into one of two L1-scratchpad buffers) and streams B through TenB before every TensorFMA, issuing the next op's loads while the current FMA runs, and it takes 529.001 cycles per op on all three cards: no more than the TensorFMA alone with B through TenB (529.05-529.09 cycles), so the next A's load of about 160 cycles is hidden behind the FMA.
model
three cards
Matmul efficiency ↗
mm.reload
Only hart 0 of a minion may issue tensor instructions; hart 1 may only issue TensorLoadL2Scp, TensorWait and tensor_coop accesses.
documented
Limits of observability ↗
minion.tensor-hart0
The tensor instructions run on the vector unit's own lanes: each of the 8 lanes holds the FMA (TxFMA) and the two int8 multiply-add (IMA/TIMA) units, and state machines in the VPU sequence the multi-cycle tensor operations on them. An 8-lane fmadd.ps does 16 FLOP per cycle, the same fp32 peak as TensorFMA.
documented
Ridge points ↗
minion.vec-peak
Tensor peak per minion-cycle: 16 fp32 / 32 fp16 / 128 int8 ops; 9.83 TFLOP/s, 19.7 TFLOP/s and 78.6 TOP/s on 1,024 minions at 600 MHz.
documented
Ridge points ↗
mm-peak
Tensor matmul, tiles in L2, all 1,024 minions at 600 MHz: 9.51 TFLOP/s fp32, 19.02 fp16, 71.77 TOP/s int8, the same on each card (91-97% of the 9.83 / 19.66 / 78.6 peak); 529 cycles per fp32/fp16 op, 280.35 per int8 op.
measured
three cards
Matmul efficiency ↗
mm-rate
Cooperative TensorLoad: identical tensor-load requests from minions (across the neighbourhoods of a shire) are synchronised and coalesced into one memory request; cooperative TensorStore combines pairs or quads of minions writing one line.
documented
no published page yet
neigh.coop-tload
Tensor loads skip the L1 but are cached in the L2 and L3; tensor stores skip the L1 and the L2.
inference
The energy manual ↗
minion.tensor-cache-path
The same benchmark with 64 private tiles per minion, so that every load comes from DRAM, on the three cards: 16,132-16,278 cycles per op on the slowest minion, whose finish sets the 0.309-0.312 TFLOP/s (15,042-15,663 on the average minion), about 30 times slower than with the tiles in the L2.
measured
three cards
Matmul efficiency ↗
mm.dram
Tensor load from the own scratchpad (catalogue): 2.12 pJ/B on zeros, 4.43 on random data; tensor store into it 4.65 / 8.58: a scratchpad write is twice a read.
measured
three cards
The energy manual ↗
e-scp-tload
Tensor load from DRAM (catalogue, both data sets): 94.6 pJ/B [86.2-105.7] on zeros, 132.6 [117.9-145.4] on random data; tensor store to DRAM 94.4 / 141.9. Even DRAM is data-dependent.
measured
three cards
The energy manual ↗
e-dram-tload
TensorFMA fp32 random: 5.782 pJ per multiply-add [5.347-6.133] above idle, all 1,024 minions; per card a2 5.920, a3 5.369, a1c1 6.058.
measured
three cards
The energy manual ↗
e-tfma-fp32
The mesh routes in dimension order, and a request and its reply take opposite orders: a request goes x first, then y, and a reply y first, then x, on the logical map, so a reply retraces its request's route backwards. Measured on 29 September (E56) with sets of streams between shires chosen so that their streams share one directed link under one order and none under the other: 1 KB tensor loads, whose data travel as replies, fell to 0.54-0.77 of their bandwidth alone when they shared a link under y first and held at 1.00 when they shared one under x first; tensor stores, whose data travel as requests, showed the mirror (0.52-0.76 against 1.00). A shared link carried about 92 GB/s. The same on aifoundry1 card 1 (development), aifoundry3 (the frozen validation) and aifoundry2 (the same frozen test, run as a third card on the evening of 29 September), three passes each.
measured
three cards
no published page yet
L104+}

## flow/G/2
FLOW 7 · MATMUL
A paired TensorLoad streams the … on every minion.

 More detail and the sources {+

One 16×16×16 fp32 step of a matmul, as the benchmark that sustains 9.51 TFLOP/s runs it on every minion: hart 0 loads a tile of A (16 lines, 1 KB) into the L1 scratchpad, streams B through TenB, and issues TensorFMA, which the vector unit's lanes run. The next A loads while the FMA runs.

 Leg What happens cycles
TensorLoad A 16 lines from the L2, three cards 160.4
B through TenB streamed with a paired load, into TenB
TensorFMA with B in TenB (546 cycles with B in the L1 scratchpad) 529.05–529.09
the next A loaded during the FMA: an op takes no longer than the FMA 529.001
32 minions each loads from the shire's L2; the cycles with all 1,024 loading 256.0
1,024 minions 9.51 TFLOP/s fp32, against a peak of 9.83 TFLOP/s
fed from DRAM 0.309–0.312 TFLOP/s; a load with all loading: 7,994–8,037 cycles; per op: 16,132–16,278

 Whether the loads hide behind the FMA was measured by the benchmark's own rate: it reloads A before every FMA and still runs at the FMA's speed. A version that waits for each load was never run.

 Measured and explained in The Horace experiment ↗.

 The facts this flow uses (17): point at one for its source

 TensorLoad reads up to 16 rows of 64 contiguous bytes (64 B aligned, row stride in x31) from memory into consecutive L1-scratchpad lines, bypassing the L1 data cache; a mask can skip rows.
documented
Sparse compute ↗
minion.tensorload
One minion's TensorLoad of 16 lines (1 KB) into its L1 scratchpad: 160.4 cycles from the L2 and 160.1 from the own scratchpad, on all three cards; 4 lines from the L2 take 41.9 cycles. From DRAM, 16 lines take 748-751 cycles on passes 2 and 3 and 1,132-1,133 on the first pass.
measured
three cards
The Horace experiment ↗
tl.one
All 1,024 minions tensor-loading at once: 256.0 cycles per 16-line load from the L2, and 7,994-8,037 cycles from DRAM (aifoundry2 / aifoundry3 / aifoundry1-c1: 8,037 / 7,994 / 8,021), where the memory shires set the pace.
measured
three cards
The Horace experiment ↗
tl.all
With A and B both in the L1 scratchpad a 16×16×16 fp32 TensorFMA takes 546 cycles (fp16 546, int8 318), identical for every data pattern.
measured
three cards
The Horace experiment ↗
minion.tensorfma-546
A 16×16×16 fp32 TensorFMA with B streamed through TenB instead of held in the L1 scratchpad: 529.05-529.09 cycles on all three cards (A in the L1 scratchpad).
measured
three cards
The Horace experiment ↗
tfma.tenb
The matmul benchmark loads a new A (16 lines from the shire's L2 into one of two L1-scratchpad buffers) and streams B through TenB before every TensorFMA, issuing the next op's loads while the current FMA runs, and it takes 529.001 cycles per op on all three cards: no more than the TensorFMA alone with B through TenB (529.05-529.09 cycles), so the next A's load of about 160 cycles is hidden behind the FMA.
model
three cards
Matmul efficiency ↗
mm.reload
Only hart 0 of a minion may issue tensor instructions; hart 1 may only issue TensorLoadL2Scp, TensorWait and tensor_coop accesses.
documented
Limits of observability ↗
minion.tensor-hart0
The tensor instructions run on the vector unit's own lanes: each of the 8 lanes holds the FMA (TxFMA) and the two int8 multiply-add (IMA/TIMA) units, and state machines in the VPU sequence the multi-cycle tensor operations on them. An 8-lane fmadd.ps does 16 FLOP per cycle, the same fp32 peak as TensorFMA.
documented
Ridge points ↗
minion.vec-peak
Tensor peak per minion-cycle: 16 fp32 / 32 fp16 / 128 int8 ops; 9.83 TFLOP/s, 19.7 TFLOP/s and 78.6 TOP/s on 1,024 minions at 600 MHz.
documented
Ridge points ↗
mm-peak
Tensor matmul, tiles in L2, all 1,024 minions at 600 MHz: 9.51 TFLOP/s fp32, 19.02 fp16, 71.77 TOP/s int8, the same on each card (91-97% of the 9.83 / 19.66 / 78.6 peak); 529 cycles per fp32/fp16 op, 280.35 per int8 op.
measured
three cards
Matmul efficiency ↗
mm-rate
Cooperative TensorLoad: identical tensor-load requests from minions (across the neighbourhoods of a shire) are synchronised and coalesced into one memory request; cooperative TensorStore combines pairs or quads of minions writing one line.
documented
no published page yet
neigh.coop-tload
Tensor loads skip the L1 but are cached in the L2 and L3; tensor stores skip the L1 and the L2.
inference
The energy manual ↗
minion.tensor-cache-path
The same benchmark with 64 private tiles per minion, so that every load comes from DRAM, on the three cards: 16,132-16,278 cycles per op on the slowest minion, whose finish sets the 0.309-0.312 TFLOP/s (15,042-15,663 on the average minion), about 30 times slower than with the tiles in the L2.
measured
three cards
Matmul efficiency ↗
mm.dram
Tensor load from the own scratchpad (catalogue): 2.12 pJ/B on zeros, 4.43 on random data; tensor store into it 4.65 / 8.58: a scratchpad write is twice a read.
measured
three cards
The energy manual ↗
e-scp-tload
Tensor load from DRAM (catalogue, both data sets): 94.6 pJ/B [86.2-105.7] on zeros, 132.6 [117.9-145.4] on random data; tensor store to DRAM 94.4 / 141.9. Even DRAM is data-dependent.
measured
three cards
The energy manual ↗
e-dram-tload
TensorFMA fp32 random: 5.782 pJ per multiply-add [5.347-6.133] above idle, all 1,024 minions; per card a2 5.920, a3 5.369, a1c1 6.058.
measured
three cards
The energy manual ↗
e-tfma-fp32
The mesh routes in dimension order, and a request and its reply take opposite orders: a request goes x first, then y, and a reply y first, then x, on the logical map, so a reply retraces its request's route backwards. Measured on 29 September (E56) with sets of streams between shires chosen so that their streams share one directed link under one order and none under the other: 1 KB tensor loads, whose data travel as replies, fell to 0.54-0.77 of their bandwidth alone when they shared a link under y first and held at 1.00 when they shared one under x first; tensor stores, whose data travel as requests, showed the mirror (0.52-0.76 against 1.00). A shared link carried about 92 GB/s. The same on aifoundry1 card 1 (development), aifoundry3 (the frozen validation) and aifoundry2 (the same frozen test, run as a third card on the evening of 29 September), three passes each.
measured
three cards
no published page yet
L104+}

## flow/G/3
FLOW 7 · MATMUL
TensorFMA: the sequencer runs C … on every minion.

 More detail and the sources {+

One 16×16×16 fp32 step of a matmul, as the benchmark that sustains 9.51 TFLOP/s runs it on every minion: hart 0 loads a tile of A (16 lines, 1 KB) into the L1 scratchpad, streams B through TenB, and issues TensorFMA, which the vector unit's lanes run. The next A loads while the FMA runs.

 Leg What happens cycles
TensorLoad A 16 lines from the L2, three cards 160.4
B through TenB streamed with a paired load, into TenB
TensorFMA with B in TenB (546 cycles with B in the L1 scratchpad) 529.05–529.09
the next A loaded during the FMA: an op takes no longer than the FMA 529.001
32 minions each loads from the shire's L2; the cycles with all 1,024 loading 256.0
1,024 minions 9.51 TFLOP/s fp32, against a peak of 9.83 TFLOP/s
fed from DRAM 0.309–0.312 TFLOP/s; a load with all loading: 7,994–8,037 cycles; per op: 16,132–16,278

 Whether the loads hide behind the FMA was measured by the benchmark's own rate: it reloads A before every FMA and still runs at the FMA's speed. A version that waits for each load was never run.

 Measured and explained in The Horace experiment ↗.

 The facts this flow uses (17): point at one for its source

 TensorLoad reads up to 16 rows of 64 contiguous bytes (64 B aligned, row stride in x31) from memory into consecutive L1-scratchpad lines, bypassing the L1 data cache; a mask can skip rows.
documented
Sparse compute ↗
minion.tensorload
One minion's TensorLoad of 16 lines (1 KB) into its L1 scratchpad: 160.4 cycles from the L2 and 160.1 from the own scratchpad, on all three cards; 4 lines from the L2 take 41.9 cycles. From DRAM, 16 lines take 748-751 cycles on passes 2 and 3 and 1,132-1,133 on the first pass.
measured
three cards
The Horace experiment ↗
tl.one
All 1,024 minions tensor-loading at once: 256.0 cycles per 16-line load from the L2, and 7,994-8,037 cycles from DRAM (aifoundry2 / aifoundry3 / aifoundry1-c1: 8,037 / 7,994 / 8,021), where the memory shires set the pace.
measured
three cards
The Horace experiment ↗
tl.all
With A and B both in the L1 scratchpad a 16×16×16 fp32 TensorFMA takes 546 cycles (fp16 546, int8 318), identical for every data pattern.
measured
three cards
The Horace experiment ↗
minion.tensorfma-546
A 16×16×16 fp32 TensorFMA with B streamed through TenB instead of held in the L1 scratchpad: 529.05-529.09 cycles on all three cards (A in the L1 scratchpad).
measured
three cards
The Horace experiment ↗
tfma.tenb
The matmul benchmark loads a new A (16 lines from the shire's L2 into one of two L1-scratchpad buffers) and streams B through TenB before every TensorFMA, issuing the next op's loads while the current FMA runs, and it takes 529.001 cycles per op on all three cards: no more than the TensorFMA alone with B through TenB (529.05-529.09 cycles), so the next A's load of about 160 cycles is hidden behind the FMA.
model
three cards
Matmul efficiency ↗
mm.reload
Only hart 0 of a minion may issue tensor instructions; hart 1 may only issue TensorLoadL2Scp, TensorWait and tensor_coop accesses.
documented
Limits of observability ↗
minion.tensor-hart0
The tensor instructions run on the vector unit's own lanes: each of the 8 lanes holds the FMA (TxFMA) and the two int8 multiply-add (IMA/TIMA) units, and state machines in the VPU sequence the multi-cycle tensor operations on them. An 8-lane fmadd.ps does 16 FLOP per cycle, the same fp32 peak as TensorFMA.
documented
Ridge points ↗
minion.vec-peak
Tensor peak per minion-cycle: 16 fp32 / 32 fp16 / 128 int8 ops; 9.83 TFLOP/s, 19.7 TFLOP/s and 78.6 TOP/s on 1,024 minions at 600 MHz.
documented
Ridge points ↗
mm-peak
Tensor matmul, tiles in L2, all 1,024 minions at 600 MHz: 9.51 TFLOP/s fp32, 19.02 fp16, 71.77 TOP/s int8, the same on each card (91-97% of the 9.83 / 19.66 / 78.6 peak); 529 cycles per fp32/fp16 op, 280.35 per int8 op.
measured
three cards
Matmul efficiency ↗
mm-rate
Cooperative TensorLoad: identical tensor-load requests from minions (across the neighbourhoods of a shire) are synchronised and coalesced into one memory request; cooperative TensorStore combines pairs or quads of minions writing one line.
documented
no published page yet
neigh.coop-tload
Tensor loads skip the L1 but are cached in the L2 and L3; tensor stores skip the L1 and the L2.
inference
The energy manual ↗
minion.tensor-cache-path
The same benchmark with 64 private tiles per minion, so that every load comes from DRAM, on the three cards: 16,132-16,278 cycles per op on the slowest minion, whose finish sets the 0.309-0.312 TFLOP/s (15,042-15,663 on the average minion), about 30 times slower than with the tiles in the L2.
measured
three cards
Matmul efficiency ↗
mm.dram
Tensor load from the own scratchpad (catalogue): 2.12 pJ/B on zeros, 4.43 on random data; tensor store into it 4.65 / 8.58: a scratchpad write is twice a read.
measured
three cards
The energy manual ↗
e-scp-tload
Tensor load from DRAM (catalogue, both data sets): 94.6 pJ/B [86.2-105.7] on zeros, 132.6 [117.9-145.4] on random data; tensor store to DRAM 94.4 / 141.9. Even DRAM is data-dependent.
measured
three cards
The energy manual ↗
e-dram-tload
TensorFMA fp32 random: 5.782 pJ per multiply-add [5.347-6.133] above idle, all 1,024 minions; per card a2 5.920, a3 5.369, a1c1 6.058.
measured
three cards
The energy manual ↗
e-tfma-fp32
The mesh routes in dimension order, and a request and its reply take opposite orders: a request goes x first, then y, and a reply y first, then x, on the logical map, so a reply retraces its request's route backwards. Measured on 29 September (E56) with sets of streams between shires chosen so that their streams share one directed link under one order and none under the other: 1 KB tensor loads, whose data travel as replies, fell to 0.54-0.77 of their bandwidth alone when they shared a link under y first and held at 1.00 when they shared one under x first; tensor stores, whose data travel as requests, showed the mirror (0.52-0.76 against 1.00). A shared link carried about 92 GB/s. The same on aifoundry1 card 1 (development), aifoundry3 (the frozen validation) and aifoundry2 (the same frozen test, run as a third card on the evening of 29 September), three passes each.
measured
three cards
no published page yet
L104+}

## flow/G/4
FLOW 7 · MATMUL
The next A loads into … on every minion.

 More detail and the sources {+

One 16×16×16 fp32 step of a matmul, as the benchmark that sustains 9.51 TFLOP/s runs it on every minion: hart 0 loads a tile of A (16 lines, 1 KB) into the L1 scratchpad, streams B through TenB, and issues TensorFMA, which the vector unit's lanes run. The next A loads while the FMA runs.

 Leg What happens cycles
TensorLoad A 16 lines from the L2, three cards 160.4
B through TenB streamed with a paired load, into TenB
TensorFMA with B in TenB (546 cycles with B in the L1 scratchpad) 529.05–529.09
the next A loaded during the FMA: an op takes no longer than the FMA 529.001
32 minions each loads from the shire's L2; the cycles with all 1,024 loading 256.0
1,024 minions 9.51 TFLOP/s fp32, against a peak of 9.83 TFLOP/s
fed from DRAM 0.309–0.312 TFLOP/s; a load with all loading: 7,994–8,037 cycles; per op: 16,132–16,278

 Whether the loads hide behind the FMA was measured by the benchmark's own rate: it reloads A before every FMA and still runs at the FMA's speed. A version that waits for each load was never run.

 Measured and explained in The Horace experiment ↗.

 The facts this flow uses (17): point at one for its source

 TensorLoad reads up to 16 rows of 64 contiguous bytes (64 B aligned, row stride in x31) from memory into consecutive L1-scratchpad lines, bypassing the L1 data cache; a mask can skip rows.
documented
Sparse compute ↗
minion.tensorload
One minion's TensorLoad of 16 lines (1 KB) into its L1 scratchpad: 160.4 cycles from the L2 and 160.1 from the own scratchpad, on all three cards; 4 lines from the L2 take 41.9 cycles. From DRAM, 16 lines take 748-751 cycles on passes 2 and 3 and 1,132-1,133 on the first pass.
measured
three cards
The Horace experiment ↗
tl.one
All 1,024 minions tensor-loading at once: 256.0 cycles per 16-line load from the L2, and 7,994-8,037 cycles from DRAM (aifoundry2 / aifoundry3 / aifoundry1-c1: 8,037 / 7,994 / 8,021), where the memory shires set the pace.
measured
three cards
The Horace experiment ↗
tl.all
With A and B both in the L1 scratchpad a 16×16×16 fp32 TensorFMA takes 546 cycles (fp16 546, int8 318), identical for every data pattern.
measured
three cards
The Horace experiment ↗
minion.tensorfma-546
A 16×16×16 fp32 TensorFMA with B streamed through TenB instead of held in the L1 scratchpad: 529.05-529.09 cycles on all three cards (A in the L1 scratchpad).
measured
three cards
The Horace experiment ↗
tfma.tenb
The matmul benchmark loads a new A (16 lines from the shire's L2 into one of two L1-scratchpad buffers) and streams B through TenB before every TensorFMA, issuing the next op's loads while the current FMA runs, and it takes 529.001 cycles per op on all three cards: no more than the TensorFMA alone with B through TenB (529.05-529.09 cycles), so the next A's load of about 160 cycles is hidden behind the FMA.
model
three cards
Matmul efficiency ↗
mm.reload
Only hart 0 of a minion may issue tensor instructions; hart 1 may only issue TensorLoadL2Scp, TensorWait and tensor_coop accesses.
documented
Limits of observability ↗
minion.tensor-hart0
The tensor instructions run on the vector unit's own lanes: each of the 8 lanes holds the FMA (TxFMA) and the two int8 multiply-add (IMA/TIMA) units, and state machines in the VPU sequence the multi-cycle tensor operations on them. An 8-lane fmadd.ps does 16 FLOP per cycle, the same fp32 peak as TensorFMA.
documented
Ridge points ↗
minion.vec-peak
Tensor peak per minion-cycle: 16 fp32 / 32 fp16 / 128 int8 ops; 9.83 TFLOP/s, 19.7 TFLOP/s and 78.6 TOP/s on 1,024 minions at 600 MHz.
documented
Ridge points ↗
mm-peak
Tensor matmul, tiles in L2, all 1,024 minions at 600 MHz: 9.51 TFLOP/s fp32, 19.02 fp16, 71.77 TOP/s int8, the same on each card (91-97% of the 9.83 / 19.66 / 78.6 peak); 529 cycles per fp32/fp16 op, 280.35 per int8 op.
measured
three cards
Matmul efficiency ↗
mm-rate
Cooperative TensorLoad: identical tensor-load requests from minions (across the neighbourhoods of a shire) are synchronised and coalesced into one memory request; cooperative TensorStore combines pairs or quads of minions writing one line.
documented
no published page yet
neigh.coop-tload
Tensor loads skip the L1 but are cached in the L2 and L3; tensor stores skip the L1 and the L2.
inference
The energy manual ↗
minion.tensor-cache-path
The same benchmark with 64 private tiles per minion, so that every load comes from DRAM, on the three cards: 16,132-16,278 cycles per op on the slowest minion, whose finish sets the 0.309-0.312 TFLOP/s (15,042-15,663 on the average minion), about 30 times slower than with the tiles in the L2.
measured
three cards
Matmul efficiency ↗
mm.dram
Tensor load from the own scratchpad (catalogue): 2.12 pJ/B on zeros, 4.43 on random data; tensor store into it 4.65 / 8.58: a scratchpad write is twice a read.
measured
three cards
The energy manual ↗
e-scp-tload
Tensor load from DRAM (catalogue, both data sets): 94.6 pJ/B [86.2-105.7] on zeros, 132.6 [117.9-145.4] on random data; tensor store to DRAM 94.4 / 141.9. Even DRAM is data-dependent.
measured
three cards
The energy manual ↗
e-dram-tload
TensorFMA fp32 random: 5.782 pJ per multiply-add [5.347-6.133] above idle, all 1,024 minions; per card a2 5.920, a3 5.369, a1c1 6.058.
measured
three cards
The energy manual ↗
e-tfma-fp32
The mesh routes in dimension order, and a request and its reply take opposite orders: a request goes x first, then y, and a reply y first, then x, on the logical map, so a reply retraces its request's route backwards. Measured on 29 September (E56) with sets of streams between shires chosen so that their streams share one directed link under one order and none under the other: 1 KB tensor loads, whose data travel as replies, fell to 0.54-0.77 of their bandwidth alone when they shared a link under y first and held at 1.00 when they shared one under x first; tensor stores, whose data travel as requests, showed the mirror (0.52-0.76 against 1.00). A shared link carried about 92 GB/s. The same on aifoundry1 card 1 (development), aifoundry3 (the frozen validation) and aifoundry2 (the same frozen test, run as a third card on the evening of 29 September), three passes each.
measured
three cards
no published page yet
L104+}

## flow/G/5
FLOW 7 · MATMUL
Every minion of the shire … on every minion.

 More detail and the sources {+

One 16×16×16 fp32 step of a matmul, as the benchmark that sustains 9.51 TFLOP/s runs it on every minion: hart 0 loads a tile of A (16 lines, 1 KB) into the L1 scratchpad, streams B through TenB, and issues TensorFMA, which the vector unit's lanes run. The next A loads while the FMA runs.

 Leg What happens cycles
TensorLoad A 16 lines from the L2, three cards 160.4
B through TenB streamed with a paired load, into TenB
TensorFMA with B in TenB (546 cycles with B in the L1 scratchpad) 529.05–529.09
the next A loaded during the FMA: an op takes no longer than the FMA 529.001
32 minions each loads from the shire's L2; the cycles with all 1,024 loading 256.0
1,024 minions 9.51 TFLOP/s fp32, against a peak of 9.83 TFLOP/s
fed from DRAM 0.309–0.312 TFLOP/s; a load with all loading: 7,994–8,037 cycles; per op: 16,132–16,278

 Whether the loads hide behind the FMA was measured by the benchmark's own rate: it reloads A before every FMA and still runs at the FMA's speed. A version that waits for each load was never run.

 Measured and explained in The Horace experiment ↗.

 The facts this flow uses (17): point at one for its source

 TensorLoad reads up to 16 rows of 64 contiguous bytes (64 B aligned, row stride in x31) from memory into consecutive L1-scratchpad lines, bypassing the L1 data cache; a mask can skip rows.
documented
Sparse compute ↗
minion.tensorload
One minion's TensorLoad of 16 lines (1 KB) into its L1 scratchpad: 160.4 cycles from the L2 and 160.1 from the own scratchpad, on all three cards; 4 lines from the L2 take 41.9 cycles. From DRAM, 16 lines take 748-751 cycles on passes 2 and 3 and 1,132-1,133 on the first pass.
measured
three cards
The Horace experiment ↗
tl.one
All 1,024 minions tensor-loading at once: 256.0 cycles per 16-line load from the L2, and 7,994-8,037 cycles from DRAM (aifoundry2 / aifoundry3 / aifoundry1-c1: 8,037 / 7,994 / 8,021), where the memory shires set the pace.
measured
three cards
The Horace experiment ↗
tl.all
With A and B both in the L1 scratchpad a 16×16×16 fp32 TensorFMA takes 546 cycles (fp16 546, int8 318), identical for every data pattern.
measured
three cards
The Horace experiment ↗
minion.tensorfma-546
A 16×16×16 fp32 TensorFMA with B streamed through TenB instead of held in the L1 scratchpad: 529.05-529.09 cycles on all three cards (A in the L1 scratchpad).
measured
three cards
The Horace experiment ↗
tfma.tenb
The matmul benchmark loads a new A (16 lines from the shire's L2 into one of two L1-scratchpad buffers) and streams B through TenB before every TensorFMA, issuing the next op's loads while the current FMA runs, and it takes 529.001 cycles per op on all three cards: no more than the TensorFMA alone with B through TenB (529.05-529.09 cycles), so the next A's load of about 160 cycles is hidden behind the FMA.
model
three cards
Matmul efficiency ↗
mm.reload
Only hart 0 of a minion may issue tensor instructions; hart 1 may only issue TensorLoadL2Scp, TensorWait and tensor_coop accesses.
documented
Limits of observability ↗
minion.tensor-hart0
The tensor instructions run on the vector unit's own lanes: each of the 8 lanes holds the FMA (TxFMA) and the two int8 multiply-add (IMA/TIMA) units, and state machines in the VPU sequence the multi-cycle tensor operations on them. An 8-lane fmadd.ps does 16 FLOP per cycle, the same fp32 peak as TensorFMA.
documented
Ridge points ↗
minion.vec-peak
Tensor peak per minion-cycle: 16 fp32 / 32 fp16 / 128 int8 ops; 9.83 TFLOP/s, 19.7 TFLOP/s and 78.6 TOP/s on 1,024 minions at 600 MHz.
documented
Ridge points ↗
mm-peak
Tensor matmul, tiles in L2, all 1,024 minions at 600 MHz: 9.51 TFLOP/s fp32, 19.02 fp16, 71.77 TOP/s int8, the same on each card (91-97% of the 9.83 / 19.66 / 78.6 peak); 529 cycles per fp32/fp16 op, 280.35 per int8 op.
measured
three cards
Matmul efficiency ↗
mm-rate
Cooperative TensorLoad: identical tensor-load requests from minions (across the neighbourhoods of a shire) are synchronised and coalesced into one memory request; cooperative TensorStore combines pairs or quads of minions writing one line.
documented
no published page yet
neigh.coop-tload
Tensor loads skip the L1 but are cached in the L2 and L3; tensor stores skip the L1 and the L2.
inference
The energy manual ↗
minion.tensor-cache-path
The same benchmark with 64 private tiles per minion, so that every load comes from DRAM, on the three cards: 16,132-16,278 cycles per op on the slowest minion, whose finish sets the 0.309-0.312 TFLOP/s (15,042-15,663 on the average minion), about 30 times slower than with the tiles in the L2.
measured
three cards
Matmul efficiency ↗
mm.dram
Tensor load from the own scratchpad (catalogue): 2.12 pJ/B on zeros, 4.43 on random data; tensor store into it 4.65 / 8.58: a scratchpad write is twice a read.
measured
three cards
The energy manual ↗
e-scp-tload
Tensor load from DRAM (catalogue, both data sets): 94.6 pJ/B [86.2-105.7] on zeros, 132.6 [117.9-145.4] on random data; tensor store to DRAM 94.4 / 141.9. Even DRAM is data-dependent.
measured
three cards
The energy manual ↗
e-dram-tload
TensorFMA fp32 random: 5.782 pJ per multiply-add [5.347-6.133] above idle, all 1,024 minions; per card a2 5.920, a3 5.369, a1c1 6.058.
measured
three cards
The energy manual ↗
e-tfma-fp32
The mesh routes in dimension order, and a request and its reply take opposite orders: a request goes x first, then y, and a reply y first, then x, on the logical map, so a reply retraces its request's route backwards. Measured on 29 September (E56) with sets of streams between shires chosen so that their streams share one directed link under one order and none under the other: 1 KB tensor loads, whose data travel as replies, fell to 0.54-0.77 of their bandwidth alone when they shared a link under y first and held at 1.00 when they shared one under x first; tensor stores, whose data travel as requests, showed the mirror (0.52-0.76 against 1.00). A shared link carried about 92 GB/s. The same on aifoundry1 card 1 (development), aifoundry3 (the frozen validation) and aifoundry2 (the same frozen test, run as a third card on the evening of 29 September), three passes each.
measured
three cards
no published page yet
L104+}

## flow/G/6
FLOW 7 · MATMUL
All 1,024 minions: 9.51 TFLOP/s … on every minion.

 More detail and the sources {+

One 16×16×16 fp32 step of a matmul, as the benchmark that sustains 9.51 TFLOP/s runs it on every minion: hart 0 loads a tile of A (16 lines, 1 KB) into the L1 scratchpad, streams B through TenB, and issues TensorFMA, which the vector unit's lanes run. The next A loads while the FMA runs.

 Leg What happens cycles
TensorLoad A 16 lines from the L2, three cards 160.4
B through TenB streamed with a paired load, into TenB
TensorFMA with B in TenB (546 cycles with B in the L1 scratchpad) 529.05–529.09
the next A loaded during the FMA: an op takes no longer than the FMA 529.001
32 minions each loads from the shire's L2; the cycles with all 1,024 loading 256.0
1,024 minions 9.51 TFLOP/s fp32, against a peak of 9.83 TFLOP/s
fed from DRAM 0.309–0.312 TFLOP/s; a load with all loading: 7,994–8,037 cycles; per op: 16,132–16,278

 Whether the loads hide behind the FMA was measured by the benchmark's own rate: it reloads A before every FMA and still runs at the FMA's speed. A version that waits for each load was never run.

 Measured and explained in The Horace experiment ↗.

 The facts this flow uses (17): point at one for its source

 TensorLoad reads up to 16 rows of 64 contiguous bytes (64 B aligned, row stride in x31) from memory into consecutive L1-scratchpad lines, bypassing the L1 data cache; a mask can skip rows.
documented
Sparse compute ↗
minion.tensorload
One minion's TensorLoad of 16 lines (1 KB) into its L1 scratchpad: 160.4 cycles from the L2 and 160.1 from the own scratchpad, on all three cards; 4 lines from the L2 take 41.9 cycles. From DRAM, 16 lines take 748-751 cycles on passes 2 and 3 and 1,132-1,133 on the first pass.
measured
three cards
The Horace experiment ↗
tl.one
All 1,024 minions tensor-loading at once: 256.0 cycles per 16-line load from the L2, and 7,994-8,037 cycles from DRAM (aifoundry2 / aifoundry3 / aifoundry1-c1: 8,037 / 7,994 / 8,021), where the memory shires set the pace.
measured
three cards
The Horace experiment ↗
tl.all
With A and B both in the L1 scratchpad a 16×16×16 fp32 TensorFMA takes 546 cycles (fp16 546, int8 318), identical for every data pattern.
measured
three cards
The Horace experiment ↗
minion.tensorfma-546
A 16×16×16 fp32 TensorFMA with B streamed through TenB instead of held in the L1 scratchpad: 529.05-529.09 cycles on all three cards (A in the L1 scratchpad).
measured
three cards
The Horace experiment ↗
tfma.tenb
The matmul benchmark loads a new A (16 lines from the shire's L2 into one of two L1-scratchpad buffers) and streams B through TenB before every TensorFMA, issuing the next op's loads while the current FMA runs, and it takes 529.001 cycles per op on all three cards: no more than the TensorFMA alone with B through TenB (529.05-529.09 cycles), so the next A's load of about 160 cycles is hidden behind the FMA.
model
three cards
Matmul efficiency ↗
mm.reload
Only hart 0 of a minion may issue tensor instructions; hart 1 may only issue TensorLoadL2Scp, TensorWait and tensor_coop accesses.
documented
Limits of observability ↗
minion.tensor-hart0
The tensor instructions run on the vector unit's own lanes: each of the 8 lanes holds the FMA (TxFMA) and the two int8 multiply-add (IMA/TIMA) units, and state machines in the VPU sequence the multi-cycle tensor operations on them. An 8-lane fmadd.ps does 16 FLOP per cycle, the same fp32 peak as TensorFMA.
documented
Ridge points ↗
minion.vec-peak
Tensor peak per minion-cycle: 16 fp32 / 32 fp16 / 128 int8 ops; 9.83 TFLOP/s, 19.7 TFLOP/s and 78.6 TOP/s on 1,024 minions at 600 MHz.
documented
Ridge points ↗
mm-peak
Tensor matmul, tiles in L2, all 1,024 minions at 600 MHz: 9.51 TFLOP/s fp32, 19.02 fp16, 71.77 TOP/s int8, the same on each card (91-97% of the 9.83 / 19.66 / 78.6 peak); 529 cycles per fp32/fp16 op, 280.35 per int8 op.
measured
three cards
Matmul efficiency ↗
mm-rate
Cooperative TensorLoad: identical tensor-load requests from minions (across the neighbourhoods of a shire) are synchronised and coalesced into one memory request; cooperative TensorStore combines pairs or quads of minions writing one line.
documented
no published page yet
neigh.coop-tload
Tensor loads skip the L1 but are cached in the L2 and L3; tensor stores skip the L1 and the L2.
inference
The energy manual ↗
minion.tensor-cache-path
The same benchmark with 64 private tiles per minion, so that every load comes from DRAM, on the three cards: 16,132-16,278 cycles per op on the slowest minion, whose finish sets the 0.309-0.312 TFLOP/s (15,042-15,663 on the average minion), about 30 times slower than with the tiles in the L2.
measured
three cards
Matmul efficiency ↗
mm.dram
Tensor load from the own scratchpad (catalogue): 2.12 pJ/B on zeros, 4.43 on random data; tensor store into it 4.65 / 8.58: a scratchpad write is twice a read.
measured
three cards
The energy manual ↗
e-scp-tload
Tensor load from DRAM (catalogue, both data sets): 94.6 pJ/B [86.2-105.7] on zeros, 132.6 [117.9-145.4] on random data; tensor store to DRAM 94.4 / 141.9. Even DRAM is data-dependent.
measured
three cards
The energy manual ↗
e-dram-tload
TensorFMA fp32 random: 5.782 pJ per multiply-add [5.347-6.133] above idle, all 1,024 minions; per card a2 5.920, a3 5.369, a1c1 6.058.
measured
three cards
The energy manual ↗
e-tfma-fp32
The mesh routes in dimension order, and a request and its reply take opposite orders: a request goes x first, then y, and a reply y first, then x, on the logical map, so a reply retraces its request's route backwards. Measured on 29 September (E56) with sets of streams between shires chosen so that their streams share one directed link under one order and none under the other: 1 KB tensor loads, whose data travel as replies, fell to 0.54-0.77 of their bandwidth alone when they shared a link under y first and held at 1.00 when they shared one under x first; tensor stores, whose data travel as requests, showed the mirror (0.52-0.76 against 1.00). A shared link carried about 92 GB/s. The same on aifoundry1 card 1 (development), aifoundry3 (the frozen validation) and aifoundry2 (the same frozen test, run as a third card on the evening of 29 September), three passes each.
measured
three cards
no published page yet
L104+}

## flow/H/0
FLOW 8 · DATA → WATTS
Zeros: 38.29 W …
The same matmul, 9.18 TFLOP/s timed from the host [-(9.51-] {+(546 cycles per op+} on the [-device),-] {+device, A and B in the L1 scratchpad),+} draws 38.29 W on zeros and 63.40 W on random … more bits flip.

 More detail and the sources {+

The Horace runs of the TensorFMA matmul: the same clock, the same instructions and the same 9.18 TFLOP/s on every data set; only the operands change. (That rate is timed from the host over the whole run, launches included. On the device each op takes 546 cycles, with A and B held in the L1 scratchpad; the benchmark of flow 7 streams B through TenB, 529.001 cycles per op, and counts 9.51 TFLOP/s.) The board draws what the flipping bits cost, and the heat follows. The watts are the board's at the launch temperature: its reading in the run's first seconds less the leakage the run's own heating had added.

 Leg What happens
zeros 38.29 W at the board (aifoundry2, at the launch temperature)
ones 46.73 W
random 63.40 W, from 36.3 W idle
why bits that flip: 5.8 pJ per fp32 multiply-add on random data, 0.273 on zeros, above idle
three cards above zeros: ones 8.1–9.0 W, random 23.9–26.7 W
the heat race from 80.9–81.7 °C to 90 °C: random 19.1–26.3 s, ones 107.1–166.9 s, zeros never (602 s runs)
fewer minions random data on 768 minions: 35.4 s; on 128: never

 The watts and the heat race are aifoundry2's (the heat race on one card only); the differences above zeros are on all three cards. A hotter die also leaks more: 0.65 W per °C at 80 °C.

 Measured and explained in The Horace experiment ↗.

 The facts this flow uses (13): point at one for its source

 The Horace runs of the fp32 matmul, 9.18 TFLOP/s on every data set (timed from the host over the whole run, its launches included), launched at 80.6-81.0 °C on aifoundry2: 38.29 W on zeros, 46.73 W on ones and 63.40 W on random data, the board's power at the launch temperature: its reading in seconds 1-3 of the run (38.29, 47.56 and 65.80 W) less the leakage that the run's own heating had added by then, at the fitted leakage slope. Idle before each run: 36.3 W.
model
aifoundry2
The Horace experiment ↗
mm.w-data
The same matmul on the three cards (ABL-T8, watts above zeros at the board): ones 8.52 [7.70, 9.34], 8.09 [7.33, 8.86], 9.00 [7.33, 10.66] W and random data 25.33 [24.49, 26.17], 23.91 [23.51, 24.30], 26.66 [24.85, 28.48] W (aifoundry2 / aifoundry3 / aifoundry1-c1; 99% intervals): ones cost 8.1-9.0 W more than zeros and random data 23.9-26.7 W more. The registered test passed on aifoundry2 and aifoundry3; aifoundry1-c1 is reported against aifoundry2's registered values.
measured
three cards
The Horace experiment ↗
mm.w-3cards
TensorFMA fp32 random: 5.782 pJ per multiply-add [5.347-6.133] above idle, all 1,024 minions; per card a2 5.920, a3 5.369, a1c1 6.058.
measured
three cards
The energy manual ↗
e-tfma-fp32
TensorFMA fp32 zeros: 0.273 pJ per multiply-add [0.141-0.445] above idle, all 1,024 minions; per card a2 0.403, a3 0.163, a1c1 0.251.
measured
three cards
The energy manual ↗
e-tfma-fp32-zeros
From a launch at 80.9-81.7 °C to the 90 °C at which the run script stopped each run (run_horace_long.sh, not a firmware limit) on aifoundry2, the same matmul on all 1,024 minions: random data 19.1-26.3 s (4 runs), ones 107.1-166.9 s (3 runs); zeros never reached the cap in 602 s (3 runs).
measured
aifoundry2
The Horace experiment ↗
heat.race
Random data on fewer minions, the same launch and cap on aifoundry2: 768 minions 35.4 s, 512 minions 84.1 s, 384 minions 118.9 s, 256 minions 276.3-314.9 s, 128 never (602 s).
measured
aifoundry2
The Horace experiment ↗
heat.fewer
At 80 °C the card's idle power rises 0.65 W per °C (the fitted leakage law's slope, aifoundry2): a hotter die leaks more, which heats it further.
model
aifoundry2
The Horace experiment ↗
heat.leak
Board power during the fp32 L2 matmul that runs at 9.51 TFLOP/s, idle before the run plus the watts over idle: aifoundry2 33.3 + 25.7 = 59.0 W (die 80 °C), aifoundry3 26.0 + 24.4 = 50.4 W (62 °C), aifoundry1-c1 41.83 + 27.25 = 69.1 W (75-76 °C): 50.4-69.1 W across the three cards (die 62-80 °C). 9.51 TFLOP/s over these is the 161, 189 and 138 GFLOP/s per W of the same run (138-189).
model
three cards
Matmul efficiency ↗
mm-board-w
Idle card after 20.6 h with no workload: 31.79 W at 73 °C, of which minion rail 11.05 W, SRAM 2.00 W, mesh 3.64 W and 15.10 W on no sensor.
measured
aifoundry2
The DVFS loop and its leakage ↗
power.idle
The PMIC meters the 12 V input and three regulators (minion, NoC, SRAM); DDR, VDDQ, VDDQLP, PCIe logic, PCIe and Maxion rails have set points only. The service processor forwards a new value about every 133 ms (aifoundry2; 224 ms quiet pass on aifoundry3).
measured
three cards
Limits of observability ↗
board.meters
Tensor matmul, tiles in L2, all 1,024 minions at 600 MHz: 9.51 TFLOP/s fp32, 19.02 fp16, 71.77 TOP/s int8, the same on each card (91-97% of the 9.83 / 19.66 / 78.6 peak); 529 cycles per fp32/fp16 op, 280.35 per int8 op.
measured
three cards
Matmul efficiency ↗
mm-rate
With A and B both in the L1 scratchpad a 16×16×16 fp32 TensorFMA takes 546 cycles (fp16 546, int8 318), identical for every data pattern.
measured
three cards
The Horace experiment ↗
minion.tensorfma-546
The matmul benchmark loads a new A (16 lines from the shire's L2 into one of two L1-scratchpad buffers) and streams B through TenB before every TensorFMA, issuing the next op's loads while the current FMA runs, and it takes 529.001 cycles per op on all three cards: no more than the TensorFMA alone with B through TenB (529.05-529.09 cycles), so the next A's load of about 160 cycles is hidden behind the FMA.
model
three cards
Matmul efficiency ↗
mm.reload+}

## flow/H/1
FLOW 8 · DATA → WATTS
Zeros: 38.29 W …
The same matmul, 9.18 TFLOP/s timed from the host [-(9.51-] {+(546 cycles per op+} on the [-device),-] {+device, A and B in the L1 scratchpad),+} draws 38.29 W on zeros and 63.40 W on random … more bits flip.

 More detail and the sources {+

The Horace runs of the TensorFMA matmul: the same clock, the same instructions and the same 9.18 TFLOP/s on every data set; only the operands change. (That rate is timed from the host over the whole run, launches included. On the device each op takes 546 cycles, with A and B held in the L1 scratchpad; the benchmark of flow 7 streams B through TenB, 529.001 cycles per op, and counts 9.51 TFLOP/s.) The board draws what the flipping bits cost, and the heat follows. The watts are the board's at the launch temperature: its reading in the run's first seconds less the leakage the run's own heating had added.

 Leg What happens
zeros 38.29 W at the board (aifoundry2, at the launch temperature)
ones 46.73 W
random 63.40 W, from 36.3 W idle
why bits that flip: 5.8 pJ per fp32 multiply-add on random data, 0.273 on zeros, above idle
three cards above zeros: ones 8.1–9.0 W, random 23.9–26.7 W
the heat race from 80.9–81.7 °C to 90 °C: random 19.1–26.3 s, ones 107.1–166.9 s, zeros never (602 s runs)
fewer minions random data on 768 minions: 35.4 s; on 128: never

 The watts and the heat race are aifoundry2's (the heat race on one card only); the differences above zeros are on all three cards. A hotter die also leaks more: 0.65 W per °C at 80 °C.

 Measured and explained in The Horace experiment ↗.

 The facts this flow uses (13): point at one for its source

 The Horace runs of the fp32 matmul, 9.18 TFLOP/s on every data set (timed from the host over the whole run, its launches included), launched at 80.6-81.0 °C on aifoundry2: 38.29 W on zeros, 46.73 W on ones and 63.40 W on random data, the board's power at the launch temperature: its reading in seconds 1-3 of the run (38.29, 47.56 and 65.80 W) less the leakage that the run's own heating had added by then, at the fitted leakage slope. Idle before each run: 36.3 W.
model
aifoundry2
The Horace experiment ↗
mm.w-data
The same matmul on the three cards (ABL-T8, watts above zeros at the board): ones 8.52 [7.70, 9.34], 8.09 [7.33, 8.86], 9.00 [7.33, 10.66] W and random data 25.33 [24.49, 26.17], 23.91 [23.51, 24.30], 26.66 [24.85, 28.48] W (aifoundry2 / aifoundry3 / aifoundry1-c1; 99% intervals): ones cost 8.1-9.0 W more than zeros and random data 23.9-26.7 W more. The registered test passed on aifoundry2 and aifoundry3; aifoundry1-c1 is reported against aifoundry2's registered values.
measured
three cards
The Horace experiment ↗
mm.w-3cards
TensorFMA fp32 random: 5.782 pJ per multiply-add [5.347-6.133] above idle, all 1,024 minions; per card a2 5.920, a3 5.369, a1c1 6.058.
measured
three cards
The energy manual ↗
e-tfma-fp32
TensorFMA fp32 zeros: 0.273 pJ per multiply-add [0.141-0.445] above idle, all 1,024 minions; per card a2 0.403, a3 0.163, a1c1 0.251.
measured
three cards
The energy manual ↗
e-tfma-fp32-zeros
From a launch at 80.9-81.7 °C to the 90 °C at which the run script stopped each run (run_horace_long.sh, not a firmware limit) on aifoundry2, the same matmul on all 1,024 minions: random data 19.1-26.3 s (4 runs), ones 107.1-166.9 s (3 runs); zeros never reached the cap in 602 s (3 runs).
measured
aifoundry2
The Horace experiment ↗
heat.race
Random data on fewer minions, the same launch and cap on aifoundry2: 768 minions 35.4 s, 512 minions 84.1 s, 384 minions 118.9 s, 256 minions 276.3-314.9 s, 128 never (602 s).
measured
aifoundry2
The Horace experiment ↗
heat.fewer
At 80 °C the card's idle power rises 0.65 W per °C (the fitted leakage law's slope, aifoundry2): a hotter die leaks more, which heats it further.
model
aifoundry2
The Horace experiment ↗
heat.leak
Board power during the fp32 L2 matmul that runs at 9.51 TFLOP/s, idle before the run plus the watts over idle: aifoundry2 33.3 + 25.7 = 59.0 W (die 80 °C), aifoundry3 26.0 + 24.4 = 50.4 W (62 °C), aifoundry1-c1 41.83 + 27.25 = 69.1 W (75-76 °C): 50.4-69.1 W across the three cards (die 62-80 °C). 9.51 TFLOP/s over these is the 161, 189 and 138 GFLOP/s per W of the same run (138-189).
model
three cards
Matmul efficiency ↗
mm-board-w
Idle card after 20.6 h with no workload: 31.79 W at 73 °C, of which minion rail 11.05 W, SRAM 2.00 W, mesh 3.64 W and 15.10 W on no sensor.
measured
aifoundry2
The DVFS loop and its leakage ↗
power.idle
The PMIC meters the 12 V input and three regulators (minion, NoC, SRAM); DDR, VDDQ, VDDQLP, PCIe logic, PCIe and Maxion rails have set points only. The service processor forwards a new value about every 133 ms (aifoundry2; 224 ms quiet pass on aifoundry3).
measured
three cards
Limits of observability ↗
board.meters
Tensor matmul, tiles in L2, all 1,024 minions at 600 MHz: 9.51 TFLOP/s fp32, 19.02 fp16, 71.77 TOP/s int8, the same on each card (91-97% of the 9.83 / 19.66 / 78.6 peak); 529 cycles per fp32/fp16 op, 280.35 per int8 op.
measured
three cards
Matmul efficiency ↗
mm-rate
With A and B both in the L1 scratchpad a 16×16×16 fp32 TensorFMA takes 546 cycles (fp16 546, int8 318), identical for every data pattern.
measured
three cards
The Horace experiment ↗
minion.tensorfma-546
The matmul benchmark loads a new A (16 lines from the shire's L2 into one of two L1-scratchpad buffers) and streams B through TenB before every TensorFMA, issuing the next op's loads while the current FMA runs, and it takes 529.001 cycles per op on all three cards: no more than the TensorFMA alone with B through TenB (529.05-529.09 cycles), so the next A's load of about 160 cycles is hidden behind the FMA.
model
three cards
Matmul efficiency ↗
mm.reload+}

## flow/H/2
FLOW 8 · DATA → WATTS
Ones: 46.73 W, the same 9.18 TFLOP/s
The same matmul, 9.18 TFLOP/s timed from the host [-(9.51-] {+(546 cycles per op+} on the [-device),-] {+device, A and B in the L1 scratchpad),+} draws 38.29 W on zeros and 63.40 W on random … more bits flip.

 More detail and the sources {+

The Horace runs of the TensorFMA matmul: the same clock, the same instructions and the same 9.18 TFLOP/s on every data set; only the operands change. (That rate is timed from the host over the whole run, launches included. On the device each op takes 546 cycles, with A and B held in the L1 scratchpad; the benchmark of flow 7 streams B through TenB, 529.001 cycles per op, and counts 9.51 TFLOP/s.) The board draws what the flipping bits cost, and the heat follows. The watts are the board's at the launch temperature: its reading in the run's first seconds less the leakage the run's own heating had added.

 Leg What happens
zeros 38.29 W at the board (aifoundry2, at the launch temperature)
ones 46.73 W
random 63.40 W, from 36.3 W idle
why bits that flip: 5.8 pJ per fp32 multiply-add on random data, 0.273 on zeros, above idle
three cards above zeros: ones 8.1–9.0 W, random 23.9–26.7 W
the heat race from 80.9–81.7 °C to 90 °C: random 19.1–26.3 s, ones 107.1–166.9 s, zeros never (602 s runs)
fewer minions random data on 768 minions: 35.4 s; on 128: never

 The watts and the heat race are aifoundry2's (the heat race on one card only); the differences above zeros are on all three cards. A hotter die also leaks more: 0.65 W per °C at 80 °C.

 Measured and explained in The Horace experiment ↗.

 The facts this flow uses (13): point at one for its source

 The Horace runs of the fp32 matmul, 9.18 TFLOP/s on every data set (timed from the host over the whole run, its launches included), launched at 80.6-81.0 °C on aifoundry2: 38.29 W on zeros, 46.73 W on ones and 63.40 W on random data, the board's power at the launch temperature: its reading in seconds 1-3 of the run (38.29, 47.56 and 65.80 W) less the leakage that the run's own heating had added by then, at the fitted leakage slope. Idle before each run: 36.3 W.
model
aifoundry2
The Horace experiment ↗
mm.w-data
The same matmul on the three cards (ABL-T8, watts above zeros at the board): ones 8.52 [7.70, 9.34], 8.09 [7.33, 8.86], 9.00 [7.33, 10.66] W and random data 25.33 [24.49, 26.17], 23.91 [23.51, 24.30], 26.66 [24.85, 28.48] W (aifoundry2 / aifoundry3 / aifoundry1-c1; 99% intervals): ones cost 8.1-9.0 W more than zeros and random data 23.9-26.7 W more. The registered test passed on aifoundry2 and aifoundry3; aifoundry1-c1 is reported against aifoundry2's registered values.
measured
three cards
The Horace experiment ↗
mm.w-3cards
TensorFMA fp32 random: 5.782 pJ per multiply-add [5.347-6.133] above idle, all 1,024 minions; per card a2 5.920, a3 5.369, a1c1 6.058.
measured
three cards
The energy manual ↗
e-tfma-fp32
TensorFMA fp32 zeros: 0.273 pJ per multiply-add [0.141-0.445] above idle, all 1,024 minions; per card a2 0.403, a3 0.163, a1c1 0.251.
measured
three cards
The energy manual ↗
e-tfma-fp32-zeros
From a launch at 80.9-81.7 °C to the 90 °C at which the run script stopped each run (run_horace_long.sh, not a firmware limit) on aifoundry2, the same matmul on all 1,024 minions: random data 19.1-26.3 s (4 runs), ones 107.1-166.9 s (3 runs); zeros never reached the cap in 602 s (3 runs).
measured
aifoundry2
The Horace experiment ↗
heat.race
Random data on fewer minions, the same launch and cap on aifoundry2: 768 minions 35.4 s, 512 minions 84.1 s, 384 minions 118.9 s, 256 minions 276.3-314.9 s, 128 never (602 s).
measured
aifoundry2
The Horace experiment ↗
heat.fewer
At 80 °C the card's idle power rises 0.65 W per °C (the fitted leakage law's slope, aifoundry2): a hotter die leaks more, which heats it further.
model
aifoundry2
The Horace experiment ↗
heat.leak
Board power during the fp32 L2 matmul that runs at 9.51 TFLOP/s, idle before the run plus the watts over idle: aifoundry2 33.3 + 25.7 = 59.0 W (die 80 °C), aifoundry3 26.0 + 24.4 = 50.4 W (62 °C), aifoundry1-c1 41.83 + 27.25 = 69.1 W (75-76 °C): 50.4-69.1 W across the three cards (die 62-80 °C). 9.51 TFLOP/s over these is the 161, 189 and 138 GFLOP/s per W of the same run (138-189).
model
three cards
Matmul efficiency ↗
mm-board-w
Idle card after 20.6 h with no workload: 31.79 W at 73 °C, of which minion rail 11.05 W, SRAM 2.00 W, mesh 3.64 W and 15.10 W on no sensor.
measured
aifoundry2
The DVFS loop and its leakage ↗
power.idle
The PMIC meters the 12 V input and three regulators (minion, NoC, SRAM); DDR, VDDQ, VDDQLP, PCIe logic, PCIe and Maxion rails have set points only. The service processor forwards a new value about every 133 ms (aifoundry2; 224 ms quiet pass on aifoundry3).
measured
three cards
Limits of observability ↗
board.meters
Tensor matmul, tiles in L2, all 1,024 minions at 600 MHz: 9.51 TFLOP/s fp32, 19.02 fp16, 71.77 TOP/s int8, the same on each card (91-97% of the 9.83 / 19.66 / 78.6 peak); 529 cycles per fp32/fp16 op, 280.35 per int8 op.
measured
three cards
Matmul efficiency ↗
mm-rate
With A and B both in the L1 scratchpad a 16×16×16 fp32 TensorFMA takes 546 cycles (fp16 546, int8 318), identical for every data pattern.
measured
three cards
The Horace experiment ↗
minion.tensorfma-546
The matmul benchmark loads a new A (16 lines from the shire's L2 into one of two L1-scratchpad buffers) and streams B through TenB before every TensorFMA, issuing the next op's loads while the current FMA runs, and it takes 529.001 cycles per op on all three cards: no more than the TensorFMA alone with B through TenB (529.05-529.09 cycles), so the next A's load of about 160 cycles is hidden behind the FMA.
model
three cards
Matmul efficiency ↗
mm.reload+}

## flow/H/3
FLOW 8 · DATA → WATTS
Random data: 63.40 …
The same matmul, 9.18 TFLOP/s timed from the host [-(9.51-] {+(546 cycles per op+} on the [-device),-] {+device, A and B in the L1 scratchpad),+} draws 38.29 W on zeros and 63.40 W on random … more bits flip.

 More detail and the sources {+

The Horace runs of the TensorFMA matmul: the same clock, the same instructions and the same 9.18 TFLOP/s on every data set; only the operands change. (That rate is timed from the host over the whole run, launches included. On the device each op takes 546 cycles, with A and B held in the L1 scratchpad; the benchmark of flow 7 streams B through TenB, 529.001 cycles per op, and counts 9.51 TFLOP/s.) The board draws what the flipping bits cost, and the heat follows. The watts are the board's at the launch temperature: its reading in the run's first seconds less the leakage the run's own heating had added.

 Leg What happens
zeros 38.29 W at the board (aifoundry2, at the launch temperature)
ones 46.73 W
random 63.40 W, from 36.3 W idle
why bits that flip: 5.8 pJ per fp32 multiply-add on random data, 0.273 on zeros, above idle
three cards above zeros: ones 8.1–9.0 W, random 23.9–26.7 W
the heat race from 80.9–81.7 °C to 90 °C: random 19.1–26.3 s, ones 107.1–166.9 s, zeros never (602 s runs)
fewer minions random data on 768 minions: 35.4 s; on 128: never

 The watts and the heat race are aifoundry2's (the heat race on one card only); the differences above zeros are on all three cards. A hotter die also leaks more: 0.65 W per °C at 80 °C.

 Measured and explained in The Horace experiment ↗.

 The facts this flow uses (13): point at one for its source

 The Horace runs of the fp32 matmul, 9.18 TFLOP/s on every data set (timed from the host over the whole run, its launches included), launched at 80.6-81.0 °C on aifoundry2: 38.29 W on zeros, 46.73 W on ones and 63.40 W on random data, the board's power at the launch temperature: its reading in seconds 1-3 of the run (38.29, 47.56 and 65.80 W) less the leakage that the run's own heating had added by then, at the fitted leakage slope. Idle before each run: 36.3 W.
model
aifoundry2
The Horace experiment ↗
mm.w-data
The same matmul on the three cards (ABL-T8, watts above zeros at the board): ones 8.52 [7.70, 9.34], 8.09 [7.33, 8.86], 9.00 [7.33, 10.66] W and random data 25.33 [24.49, 26.17], 23.91 [23.51, 24.30], 26.66 [24.85, 28.48] W (aifoundry2 / aifoundry3 / aifoundry1-c1; 99% intervals): ones cost 8.1-9.0 W more than zeros and random data 23.9-26.7 W more. The registered test passed on aifoundry2 and aifoundry3; aifoundry1-c1 is reported against aifoundry2's registered values.
measured
three cards
The Horace experiment ↗
mm.w-3cards
TensorFMA fp32 random: 5.782 pJ per multiply-add [5.347-6.133] above idle, all 1,024 minions; per card a2 5.920, a3 5.369, a1c1 6.058.
measured
three cards
The energy manual ↗
e-tfma-fp32
TensorFMA fp32 zeros: 0.273 pJ per multiply-add [0.141-0.445] above idle, all 1,024 minions; per card a2 0.403, a3 0.163, a1c1 0.251.
measured
three cards
The energy manual ↗
e-tfma-fp32-zeros
From a launch at 80.9-81.7 °C to the 90 °C at which the run script stopped each run (run_horace_long.sh, not a firmware limit) on aifoundry2, the same matmul on all 1,024 minions: random data 19.1-26.3 s (4 runs), ones 107.1-166.9 s (3 runs); zeros never reached the cap in 602 s (3 runs).
measured
aifoundry2
The Horace experiment ↗
heat.race
Random data on fewer minions, the same launch and cap on aifoundry2: 768 minions 35.4 s, 512 minions 84.1 s, 384 minions 118.9 s, 256 minions 276.3-314.9 s, 128 never (602 s).
measured
aifoundry2
The Horace experiment ↗
heat.fewer
At 80 °C the card's idle power rises 0.65 W per °C (the fitted leakage law's slope, aifoundry2): a hotter die leaks more, which heats it further.
model
aifoundry2
The Horace experiment ↗
heat.leak
Board power during the fp32 L2 matmul that runs at 9.51 TFLOP/s, idle before the run plus the watts over idle: aifoundry2 33.3 + 25.7 = 59.0 W (die 80 °C), aifoundry3 26.0 + 24.4 = 50.4 W (62 °C), aifoundry1-c1 41.83 + 27.25 = 69.1 W (75-76 °C): 50.4-69.1 W across the three cards (die 62-80 °C). 9.51 TFLOP/s over these is the 161, 189 and 138 GFLOP/s per W of the same run (138-189).
model
three cards
Matmul efficiency ↗
mm-board-w
Idle card after 20.6 h with no workload: 31.79 W at 73 °C, of which minion rail 11.05 W, SRAM 2.00 W, mesh 3.64 W and 15.10 W on no sensor.
measured
aifoundry2
The DVFS loop and its leakage ↗
power.idle
The PMIC meters the 12 V input and three regulators (minion, NoC, SRAM); DDR, VDDQ, VDDQLP, PCIe logic, PCIe and Maxion rails have set points only. The service processor forwards a new value about every 133 ms (aifoundry2; 224 ms quiet pass on aifoundry3).
measured
three cards
Limits of observability ↗
board.meters
Tensor matmul, tiles in L2, all 1,024 minions at 600 MHz: 9.51 TFLOP/s fp32, 19.02 fp16, 71.77 TOP/s int8, the same on each card (91-97% of the 9.83 / 19.66 / 78.6 peak); 529 cycles per fp32/fp16 op, 280.35 per int8 op.
measured
three cards
Matmul efficiency ↗
mm-rate
With A and B both in the L1 scratchpad a 16×16×16 fp32 TensorFMA takes 546 cycles (fp16 546, int8 318), identical for every data pattern.
measured
three cards
The Horace experiment ↗
minion.tensorfma-546
The matmul benchmark loads a new A (16 lines from the shire's L2 into one of two L1-scratchpad buffers) and streams B through TenB before every TensorFMA, issuing the next op's loads while the current FMA runs, and it takes 529.001 cycles per op on all three cards: no more than the TensorFMA alone with B through TenB (529.05-529.09 cycles), so the next A's load of about 160 cycles is hidden behind the FMA.
model
three cards
Matmul efficiency ↗
mm.reload+}

## flow/H/4
FLOW 8 · DATA → WATTS
Why: what costs …
The same matmul, 9.18 TFLOP/s timed from the host [-(9.51-] {+(546 cycles per op+} on the [-device),-] {+device, A and B in the L1 scratchpad),+} draws 38.29 W on zeros and 63.40 W on random … more bits flip.

 More detail and the sources {+

The Horace runs of the TensorFMA matmul: the same clock, the same instructions and the same 9.18 TFLOP/s on every data set; only the operands change. (That rate is timed from the host over the whole run, launches included. On the device each op takes 546 cycles, with A and B held in the L1 scratchpad; the benchmark of flow 7 streams B through TenB, 529.001 cycles per op, and counts 9.51 TFLOP/s.) The board draws what the flipping bits cost, and the heat follows. The watts are the board's at the launch temperature: its reading in the run's first seconds less the leakage the run's own heating had added.

 Leg What happens
zeros 38.29 W at the board (aifoundry2, at the launch temperature)
ones 46.73 W
random 63.40 W, from 36.3 W idle
why bits that flip: 5.8 pJ per fp32 multiply-add on random data, 0.273 on zeros, above idle
three cards above zeros: ones 8.1–9.0 W, random 23.9–26.7 W
the heat race from 80.9–81.7 °C to 90 °C: random 19.1–26.3 s, ones 107.1–166.9 s, zeros never (602 s runs)
fewer minions random data on 768 minions: 35.4 s; on 128: never

 The watts and the heat race are aifoundry2's (the heat race on one card only); the differences above zeros are on all three cards. A hotter die also leaks more: 0.65 W per °C at 80 °C.

 Measured and explained in The Horace experiment ↗.

 The facts this flow uses (13): point at one for its source

 The Horace runs of the fp32 matmul, 9.18 TFLOP/s on every data set (timed from the host over the whole run, its launches included), launched at 80.6-81.0 °C on aifoundry2: 38.29 W on zeros, 46.73 W on ones and 63.40 W on random data, the board's power at the launch temperature: its reading in seconds 1-3 of the run (38.29, 47.56 and 65.80 W) less the leakage that the run's own heating had added by then, at the fitted leakage slope. Idle before each run: 36.3 W.
model
aifoundry2
The Horace experiment ↗
mm.w-data
The same matmul on the three cards (ABL-T8, watts above zeros at the board): ones 8.52 [7.70, 9.34], 8.09 [7.33, 8.86], 9.00 [7.33, 10.66] W and random data 25.33 [24.49, 26.17], 23.91 [23.51, 24.30], 26.66 [24.85, 28.48] W (aifoundry2 / aifoundry3 / aifoundry1-c1; 99% intervals): ones cost 8.1-9.0 W more than zeros and random data 23.9-26.7 W more. The registered test passed on aifoundry2 and aifoundry3; aifoundry1-c1 is reported against aifoundry2's registered values.
measured
three cards
The Horace experiment ↗
mm.w-3cards
TensorFMA fp32 random: 5.782 pJ per multiply-add [5.347-6.133] above idle, all 1,024 minions; per card a2 5.920, a3 5.369, a1c1 6.058.
measured
three cards
The energy manual ↗
e-tfma-fp32
TensorFMA fp32 zeros: 0.273 pJ per multiply-add [0.141-0.445] above idle, all 1,024 minions; per card a2 0.403, a3 0.163, a1c1 0.251.
measured
three cards
The energy manual ↗
e-tfma-fp32-zeros
From a launch at 80.9-81.7 °C to the 90 °C at which the run script stopped each run (run_horace_long.sh, not a firmware limit) on aifoundry2, the same matmul on all 1,024 minions: random data 19.1-26.3 s (4 runs), ones 107.1-166.9 s (3 runs); zeros never reached the cap in 602 s (3 runs).
measured
aifoundry2
The Horace experiment ↗
heat.race
Random data on fewer minions, the same launch and cap on aifoundry2: 768 minions 35.4 s, 512 minions 84.1 s, 384 minions 118.9 s, 256 minions 276.3-314.9 s, 128 never (602 s).
measured
aifoundry2
The Horace experiment ↗
heat.fewer
At 80 °C the card's idle power rises 0.65 W per °C (the fitted leakage law's slope, aifoundry2): a hotter die leaks more, which heats it further.
model
aifoundry2
The Horace experiment ↗
heat.leak
Board power during the fp32 L2 matmul that runs at 9.51 TFLOP/s, idle before the run plus the watts over idle: aifoundry2 33.3 + 25.7 = 59.0 W (die 80 °C), aifoundry3 26.0 + 24.4 = 50.4 W (62 °C), aifoundry1-c1 41.83 + 27.25 = 69.1 W (75-76 °C): 50.4-69.1 W across the three cards (die 62-80 °C). 9.51 TFLOP/s over these is the 161, 189 and 138 GFLOP/s per W of the same run (138-189).
model
three cards
Matmul efficiency ↗
mm-board-w
Idle card after 20.6 h with no workload: 31.79 W at 73 °C, of which minion rail 11.05 W, SRAM 2.00 W, mesh 3.64 W and 15.10 W on no sensor.
measured
aifoundry2
The DVFS loop and its leakage ↗
power.idle
The PMIC meters the 12 V input and three regulators (minion, NoC, SRAM); DDR, VDDQ, VDDQLP, PCIe logic, PCIe and Maxion rails have set points only. The service processor forwards a new value about every 133 ms (aifoundry2; 224 ms quiet pass on aifoundry3).
measured
three cards
Limits of observability ↗
board.meters
Tensor matmul, tiles in L2, all 1,024 minions at 600 MHz: 9.51 TFLOP/s fp32, 19.02 fp16, 71.77 TOP/s int8, the same on each card (91-97% of the 9.83 / 19.66 / 78.6 peak); 529 cycles per fp32/fp16 op, 280.35 per int8 op.
measured
three cards
Matmul efficiency ↗
mm-rate
With A and B both in the L1 scratchpad a 16×16×16 fp32 TensorFMA takes 546 cycles (fp16 546, int8 318), identical for every data pattern.
measured
three cards
The Horace experiment ↗
minion.tensorfma-546
The matmul benchmark loads a new A (16 lines from the shire's L2 into one of two L1-scratchpad buffers) and streams B through TenB before every TensorFMA, issuing the next op's loads while the current FMA runs, and it takes 529.001 cycles per op on all three cards: no more than the TensorFMA alone with B through TenB (529.05-529.09 cycles), so the next A's load of about 160 cycles is hidden behind the FMA.
model
three cards
Matmul efficiency ↗
mm.reload+}

## flow/H/5
FLOW 8 · DATA → WATTS
On all three …
The same matmul, 9.18 TFLOP/s timed from the host [-(9.51-] {+(546 cycles per op+} on the [-device),-] {+device, A and B in the L1 scratchpad),+} draws 38.29 W on zeros and 63.40 W on random … more bits flip.

 More detail and the sources {+

The Horace runs of the TensorFMA matmul: the same clock, the same instructions and the same 9.18 TFLOP/s on every data set; only the operands change. (That rate is timed from the host over the whole run, launches included. On the device each op takes 546 cycles, with A and B held in the L1 scratchpad; the benchmark of flow 7 streams B through TenB, 529.001 cycles per op, and counts 9.51 TFLOP/s.) The board draws what the flipping bits cost, and the heat follows. The watts are the board's at the launch temperature: its reading in the run's first seconds less the leakage the run's own heating had added.

 Leg What happens
zeros 38.29 W at the board (aifoundry2, at the launch temperature)
ones 46.73 W
random 63.40 W, from 36.3 W idle
why bits that flip: 5.8 pJ per fp32 multiply-add on random data, 0.273 on zeros, above idle
three cards above zeros: ones 8.1–9.0 W, random 23.9–26.7 W
the heat race from 80.9–81.7 °C to 90 °C: random 19.1–26.3 s, ones 107.1–166.9 s, zeros never (602 s runs)
fewer minions random data on 768 minions: 35.4 s; on 128: never

 The watts and the heat race are aifoundry2's (the heat race on one card only); the differences above zeros are on all three cards. A hotter die also leaks more: 0.65 W per °C at 80 °C.

 Measured and explained in The Horace experiment ↗.

 The facts this flow uses (13): point at one for its source

 The Horace runs of the fp32 matmul, 9.18 TFLOP/s on every data set (timed from the host over the whole run, its launches included), launched at 80.6-81.0 °C on aifoundry2: 38.29 W on zeros, 46.73 W on ones and 63.40 W on random data, the board's power at the launch temperature: its reading in seconds 1-3 of the run (38.29, 47.56 and 65.80 W) less the leakage that the run's own heating had added by then, at the fitted leakage slope. Idle before each run: 36.3 W.
model
aifoundry2
The Horace experiment ↗
mm.w-data
The same matmul on the three cards (ABL-T8, watts above zeros at the board): ones 8.52 [7.70, 9.34], 8.09 [7.33, 8.86], 9.00 [7.33, 10.66] W and random data 25.33 [24.49, 26.17], 23.91 [23.51, 24.30], 26.66 [24.85, 28.48] W (aifoundry2 / aifoundry3 / aifoundry1-c1; 99% intervals): ones cost 8.1-9.0 W more than zeros and random data 23.9-26.7 W more. The registered test passed on aifoundry2 and aifoundry3; aifoundry1-c1 is reported against aifoundry2's registered values.
measured
three cards
The Horace experiment ↗
mm.w-3cards
TensorFMA fp32 random: 5.782 pJ per multiply-add [5.347-6.133] above idle, all 1,024 minions; per card a2 5.920, a3 5.369, a1c1 6.058.
measured
three cards
The energy manual ↗
e-tfma-fp32
TensorFMA fp32 zeros: 0.273 pJ per multiply-add [0.141-0.445] above idle, all 1,024 minions; per card a2 0.403, a3 0.163, a1c1 0.251.
measured
three cards
The energy manual ↗
e-tfma-fp32-zeros
From a launch at 80.9-81.7 °C to the 90 °C at which the run script stopped each run (run_horace_long.sh, not a firmware limit) on aifoundry2, the same matmul on all 1,024 minions: random data 19.1-26.3 s (4 runs), ones 107.1-166.9 s (3 runs); zeros never reached the cap in 602 s (3 runs).
measured
aifoundry2
The Horace experiment ↗
heat.race
Random data on fewer minions, the same launch and cap on aifoundry2: 768 minions 35.4 s, 512 minions 84.1 s, 384 minions 118.9 s, 256 minions 276.3-314.9 s, 128 never (602 s).
measured
aifoundry2
The Horace experiment ↗
heat.fewer
At 80 °C the card's idle power rises 0.65 W per °C (the fitted leakage law's slope, aifoundry2): a hotter die leaks more, which heats it further.
model
aifoundry2
The Horace experiment ↗
heat.leak
Board power during the fp32 L2 matmul that runs at 9.51 TFLOP/s, idle before the run plus the watts over idle: aifoundry2 33.3 + 25.7 = 59.0 W (die 80 °C), aifoundry3 26.0 + 24.4 = 50.4 W (62 °C), aifoundry1-c1 41.83 + 27.25 = 69.1 W (75-76 °C): 50.4-69.1 W across the three cards (die 62-80 °C). 9.51 TFLOP/s over these is the 161, 189 and 138 GFLOP/s per W of the same run (138-189).
model
three cards
Matmul efficiency ↗
mm-board-w
Idle card after 20.6 h with no workload: 31.79 W at 73 °C, of which minion rail 11.05 W, SRAM 2.00 W, mesh 3.64 W and 15.10 W on no sensor.
measured
aifoundry2
The DVFS loop and its leakage ↗
power.idle
The PMIC meters the 12 V input and three regulators (minion, NoC, SRAM); DDR, VDDQ, VDDQLP, PCIe logic, PCIe and Maxion rails have set points only. The service processor forwards a new value about every 133 ms (aifoundry2; 224 ms quiet pass on aifoundry3).
measured
three cards
Limits of observability ↗
board.meters
Tensor matmul, tiles in L2, all 1,024 minions at 600 MHz: 9.51 TFLOP/s fp32, 19.02 fp16, 71.77 TOP/s int8, the same on each card (91-97% of the 9.83 / 19.66 / 78.6 peak); 529 cycles per fp32/fp16 op, 280.35 per int8 op.
measured
three cards
Matmul efficiency ↗
mm-rate
With A and B both in the L1 scratchpad a 16×16×16 fp32 TensorFMA takes 546 cycles (fp16 546, int8 318), identical for every data pattern.
measured
three cards
The Horace experiment ↗
minion.tensorfma-546
The matmul benchmark loads a new A (16 lines from the shire's L2 into one of two L1-scratchpad buffers) and streams B through TenB before every TensorFMA, issuing the next op's loads while the current FMA runs, and it takes 529.001 cycles per op on all three cards: no more than the TensorFMA alone with B through TenB (529.05-529.09 cycles), so the next A's load of about 160 cycles is hidden behind the FMA.
model
three cards
Matmul efficiency ↗
mm.reload+}

## flow/H/6
FLOW 8 · DATA → WATTS
The heat race …
The same matmul, 9.18 TFLOP/s timed from the host [-(9.51-] {+(546 cycles per op+} on the [-device),-] {+device, A and B in the L1 scratchpad),+} draws 38.29 W on zeros and 63.40 W on random … more bits flip.

 More detail and the sources {+

The Horace runs of the TensorFMA matmul: the same clock, the same instructions and the same 9.18 TFLOP/s on every data set; only the operands change. (That rate is timed from the host over the whole run, launches included. On the device each op takes 546 cycles, with A and B held in the L1 scratchpad; the benchmark of flow 7 streams B through TenB, 529.001 cycles per op, and counts 9.51 TFLOP/s.) The board draws what the flipping bits cost, and the heat follows. The watts are the board's at the launch temperature: its reading in the run's first seconds less the leakage the run's own heating had added.

 Leg What happens
zeros 38.29 W at the board (aifoundry2, at the launch temperature)
ones 46.73 W
random 63.40 W, from 36.3 W idle
why bits that flip: 5.8 pJ per fp32 multiply-add on random data, 0.273 on zeros, above idle
three cards above zeros: ones 8.1–9.0 W, random 23.9–26.7 W
the heat race from 80.9–81.7 °C to 90 °C: random 19.1–26.3 s, ones 107.1–166.9 s, zeros never (602 s runs)
fewer minions random data on 768 minions: 35.4 s; on 128: never

 The watts and the heat race are aifoundry2's (the heat race on one card only); the differences above zeros are on all three cards. A hotter die also leaks more: 0.65 W per °C at 80 °C.

 Measured and explained in The Horace experiment ↗.

 The facts this flow uses (13): point at one for its source

 The Horace runs of the fp32 matmul, 9.18 TFLOP/s on every data set (timed from the host over the whole run, its launches included), launched at 80.6-81.0 °C on aifoundry2: 38.29 W on zeros, 46.73 W on ones and 63.40 W on random data, the board's power at the launch temperature: its reading in seconds 1-3 of the run (38.29, 47.56 and 65.80 W) less the leakage that the run's own heating had added by then, at the fitted leakage slope. Idle before each run: 36.3 W.
model
aifoundry2
The Horace experiment ↗
mm.w-data
The same matmul on the three cards (ABL-T8, watts above zeros at the board): ones 8.52 [7.70, 9.34], 8.09 [7.33, 8.86], 9.00 [7.33, 10.66] W and random data 25.33 [24.49, 26.17], 23.91 [23.51, 24.30], 26.66 [24.85, 28.48] W (aifoundry2 / aifoundry3 / aifoundry1-c1; 99% intervals): ones cost 8.1-9.0 W more than zeros and random data 23.9-26.7 W more. The registered test passed on aifoundry2 and aifoundry3; aifoundry1-c1 is reported against aifoundry2's registered values.
measured
three cards
The Horace experiment ↗
mm.w-3cards
TensorFMA fp32 random: 5.782 pJ per multiply-add [5.347-6.133] above idle, all 1,024 minions; per card a2 5.920, a3 5.369, a1c1 6.058.
measured
three cards
The energy manual ↗
e-tfma-fp32
TensorFMA fp32 zeros: 0.273 pJ per multiply-add [0.141-0.445] above idle, all 1,024 minions; per card a2 0.403, a3 0.163, a1c1 0.251.
measured
three cards
The energy manual ↗
e-tfma-fp32-zeros
From a launch at 80.9-81.7 °C to the 90 °C at which the run script stopped each run (run_horace_long.sh, not a firmware limit) on aifoundry2, the same matmul on all 1,024 minions: random data 19.1-26.3 s (4 runs), ones 107.1-166.9 s (3 runs); zeros never reached the cap in 602 s (3 runs).
measured
aifoundry2
The Horace experiment ↗
heat.race
Random data on fewer minions, the same launch and cap on aifoundry2: 768 minions 35.4 s, 512 minions 84.1 s, 384 minions 118.9 s, 256 minions 276.3-314.9 s, 128 never (602 s).
measured
aifoundry2
The Horace experiment ↗
heat.fewer
At 80 °C the card's idle power rises 0.65 W per °C (the fitted leakage law's slope, aifoundry2): a hotter die leaks more, which heats it further.
model
aifoundry2
The Horace experiment ↗
heat.leak
Board power during the fp32 L2 matmul that runs at 9.51 TFLOP/s, idle before the run plus the watts over idle: aifoundry2 33.3 + 25.7 = 59.0 W (die 80 °C), aifoundry3 26.0 + 24.4 = 50.4 W (62 °C), aifoundry1-c1 41.83 + 27.25 = 69.1 W (75-76 °C): 50.4-69.1 W across the three cards (die 62-80 °C). 9.51 TFLOP/s over these is the 161, 189 and 138 GFLOP/s per W of the same run (138-189).
model
three cards
Matmul efficiency ↗
mm-board-w
Idle card after 20.6 h with no workload: 31.79 W at 73 °C, of which minion rail 11.05 W, SRAM 2.00 W, mesh 3.64 W and 15.10 W on no sensor.
measured
aifoundry2
The DVFS loop and its leakage ↗
power.idle
The PMIC meters the 12 V input and three regulators (minion, NoC, SRAM); DDR, VDDQ, VDDQLP, PCIe logic, PCIe and Maxion rails have set points only. The service processor forwards a new value about every 133 ms (aifoundry2; 224 ms quiet pass on aifoundry3).
measured
three cards
Limits of observability ↗
board.meters
Tensor matmul, tiles in L2, all 1,024 minions at 600 MHz: 9.51 TFLOP/s fp32, 19.02 fp16, 71.77 TOP/s int8, the same on each card (91-97% of the 9.83 / 19.66 / 78.6 peak); 529 cycles per fp32/fp16 op, 280.35 per int8 op.
measured
three cards
Matmul efficiency ↗
mm-rate
With A and B both in the L1 scratchpad a 16×16×16 fp32 TensorFMA takes 546 cycles (fp16 546, int8 318), identical for every data pattern.
measured
three cards
The Horace experiment ↗
minion.tensorfma-546
The matmul benchmark loads a new A (16 lines from the shire's L2 into one of two L1-scratchpad buffers) and streams B through TenB before every TensorFMA, issuing the next op's loads while the current FMA runs, and it takes 529.001 cycles per op on all three cards: no more than the TensorFMA alone with B through TenB (529.05-529.09 cycles), so the next A's load of about 160 cycles is hidden behind the FMA.
model
three cards
Matmul efficiency ↗
mm.reload+}

## flow/I/0
FLOW 9 · HOT LINE
Every minion hammers one … can be starved.

 More detail and the sources {+

One global atomic that every minion hammers lives in one line of one bank of shire 0. The atomic is shared fairly; what suffers is the host shire's own traffic through that bank.

 Leg What happens
one line the bank retires one atomic every 10.00 cycles, about 60 M/s for the chip
fair shares the host shire gets 1.004 / 1.004 / 1.004 of an even share, the lowest shire 0.998 / 0.998 / 0.999
the host alone the host's minions read their own scratchpad
21 requesters 21 minions of one other shire hammer a word in the host: the host keeps 95.6 / 95.7 / 95.6% of its rate
22 requesters the host stops: 0.02%
spread it over 32 lines, one per shire: 0.31 cycles per atomic, 1,919 M/s, 32×; 19.8 nJ against 1.16 nJ each, 17×

 Values are aifoundry2 / aifoundry3 / aifoundry1 card 1 where three are given.

 Measured and explained in One hot line stops a shire ↗.

 The facts this flow uses (8): point at one for its source

 All 32 shires hammering one global atomic homed in shire 0 (32 minions each): every shire gets an even share, the host shire 1.004 / 1.004 / 1.004 of it (1.004) and the lowest 0.998 / 0.998 / 0.999 (0.998-0.999; aifoundry2 / aifoundry3 / aifoundry1-c1), at 10.00 cycles per atomic.
measured
three cards
One hot line stops a shire ↗
hot.fair
One contended global atomic (amoaddg.w on one line, 1,024 minions): the bank retires one every 10.00 cycles, about 60 M/s for the whole chip; spread over 32 lines, one per shire, 0.31 cycles and 1,919 M/s: 32x.
measured
aifoundry2
One hot line stops a shire ↗
hot-cost
The host shire's minions read their own scratchpad while the same number of minions in one other shire hammer one scratchpad word in the host shire: with 21 of each the host keeps 95.6 / 95.7 / 95.6% of its rate alone (aifoundry2 / aifoundry3 / aifoundry1-c1, mean of 3 passes; 95.5-95.7% over every pass), and with 22, 23 or 24 it stops: 0.02% on every card. An uncontended remote atomic takes 216.2 / 216.3 / 216.6 cycles round trip.
measured
three cards
One hot line stops a shire ↗
hot.cliff
The switch is sharp: 21 remote requesters leave the host at 95.5-95.7% of its rate, 22 stop it (0.02%). Rule: the bank is not saturated while N x 10 cycles < P + t_round_trip (216 cycles).
measured
three cards
One hot line stops a shire ↗
hot-edge
Energy per atomic: 19.8 nJ [16.9-23.6] contended against 1.16 nJ [1.01-1.37] spread over 32 lines: 17x.
measured
aifoundry2, aifoundry3
One hot line stops a shire ↗
hot-energy
A global atomic (amoaddg) is performed at the shire cache that homes the line. One contended line serialises at 10.00 cycles per atomic (about 60 M/s for the chip) and stops the host shire's own memory path; an uncontended remote global atomic round trip is 216 cycles.
measured
aifoundry2, aifoundry3
One hot line stops a shire ↗
mem.global-atomic
The memory shire that serves a line is picked by physical-address bits 8:6 and its L3 home shire by bits 10:6, so memory shire m serves the lines of home shires m, m+8, m+16 and m+24. Hardware read counters confirmed the memory-shire bits for 64 of 64 lines (and in all 15 passes of the three-card check).
measured
three cards
Anatomy of a memory access ↗
L43
A line's L3 home shire is PA[10:6]: consecutive 64-byte lines rotate over the 32 compute shires' L3 slices (default 'swizzle0'; the firmware leaves the swizzle register at reset).
measured
three cards
Anatomy of a memory access ↗
l3.home+}

## flow/I/1
FLOW 9 · HOT LINE
Every minion hammers one … can be starved.

 More detail and the sources {+

One global atomic that every minion hammers lives in one line of one bank of shire 0. The atomic is shared fairly; what suffers is the host shire's own traffic through that bank.

 Leg What happens
one line the bank retires one atomic every 10.00 cycles, about 60 M/s for the chip
fair shares the host shire gets 1.004 / 1.004 / 1.004 of an even share, the lowest shire 0.998 / 0.998 / 0.999
the host alone the host's minions read their own scratchpad
21 requesters 21 minions of one other shire hammer a word in the host: the host keeps 95.6 / 95.7 / 95.6% of its rate
22 requesters the host stops: 0.02%
spread it over 32 lines, one per shire: 0.31 cycles per atomic, 1,919 M/s, 32×; 19.8 nJ against 1.16 nJ each, 17×

 Values are aifoundry2 / aifoundry3 / aifoundry1 card 1 where three are given.

 Measured and explained in One hot line stops a shire ↗.

 The facts this flow uses (8): point at one for its source

 All 32 shires hammering one global atomic homed in shire 0 (32 minions each): every shire gets an even share, the host shire 1.004 / 1.004 / 1.004 of it (1.004) and the lowest 0.998 / 0.998 / 0.999 (0.998-0.999; aifoundry2 / aifoundry3 / aifoundry1-c1), at 10.00 cycles per atomic.
measured
three cards
One hot line stops a shire ↗
hot.fair
One contended global atomic (amoaddg.w on one line, 1,024 minions): the bank retires one every 10.00 cycles, about 60 M/s for the whole chip; spread over 32 lines, one per shire, 0.31 cycles and 1,919 M/s: 32x.
measured
aifoundry2
One hot line stops a shire ↗
hot-cost
The host shire's minions read their own scratchpad while the same number of minions in one other shire hammer one scratchpad word in the host shire: with 21 of each the host keeps 95.6 / 95.7 / 95.6% of its rate alone (aifoundry2 / aifoundry3 / aifoundry1-c1, mean of 3 passes; 95.5-95.7% over every pass), and with 22, 23 or 24 it stops: 0.02% on every card. An uncontended remote atomic takes 216.2 / 216.3 / 216.6 cycles round trip.
measured
three cards
One hot line stops a shire ↗
hot.cliff
The switch is sharp: 21 remote requesters leave the host at 95.5-95.7% of its rate, 22 stop it (0.02%). Rule: the bank is not saturated while N x 10 cycles < P + t_round_trip (216 cycles).
measured
three cards
One hot line stops a shire ↗
hot-edge
Energy per atomic: 19.8 nJ [16.9-23.6] contended against 1.16 nJ [1.01-1.37] spread over 32 lines: 17x.
measured
aifoundry2, aifoundry3
One hot line stops a shire ↗
hot-energy
A global atomic (amoaddg) is performed at the shire cache that homes the line. One contended line serialises at 10.00 cycles per atomic (about 60 M/s for the chip) and stops the host shire's own memory path; an uncontended remote global atomic round trip is 216 cycles.
measured
aifoundry2, aifoundry3
One hot line stops a shire ↗
mem.global-atomic
The memory shire that serves a line is picked by physical-address bits 8:6 and its L3 home shire by bits 10:6, so memory shire m serves the lines of home shires m, m+8, m+16 and m+24. Hardware read counters confirmed the memory-shire bits for 64 of 64 lines (and in all 15 passes of the three-card check).
measured
three cards
Anatomy of a memory access ↗
L43
A line's L3 home shire is PA[10:6]: consecutive 64-byte lines rotate over the 32 compute shires' L3 slices (default 'swizzle0'; the firmware leaves the swizzle register at reset).
measured
three cards
Anatomy of a memory access ↗
l3.home+}

## flow/I/2
FLOW 9 · HOT LINE
The atomic is fair: … can be starved.

 More detail and the sources {+

One global atomic that every minion hammers lives in one line of one bank of shire 0. The atomic is shared fairly; what suffers is the host shire's own traffic through that bank.

 Leg What happens
one line the bank retires one atomic every 10.00 cycles, about 60 M/s for the chip
fair shares the host shire gets 1.004 / 1.004 / 1.004 of an even share, the lowest shire 0.998 / 0.998 / 0.999
the host alone the host's minions read their own scratchpad
21 requesters 21 minions of one other shire hammer a word in the host: the host keeps 95.6 / 95.7 / 95.6% of its rate
22 requesters the host stops: 0.02%
spread it over 32 lines, one per shire: 0.31 cycles per atomic, 1,919 M/s, 32×; 19.8 nJ against 1.16 nJ each, 17×

 Values are aifoundry2 / aifoundry3 / aifoundry1 card 1 where three are given.

 Measured and explained in One hot line stops a shire ↗.

 The facts this flow uses (8): point at one for its source

 All 32 shires hammering one global atomic homed in shire 0 (32 minions each): every shire gets an even share, the host shire 1.004 / 1.004 / 1.004 of it (1.004) and the lowest 0.998 / 0.998 / 0.999 (0.998-0.999; aifoundry2 / aifoundry3 / aifoundry1-c1), at 10.00 cycles per atomic.
measured
three cards
One hot line stops a shire ↗
hot.fair
One contended global atomic (amoaddg.w on one line, 1,024 minions): the bank retires one every 10.00 cycles, about 60 M/s for the whole chip; spread over 32 lines, one per shire, 0.31 cycles and 1,919 M/s: 32x.
measured
aifoundry2
One hot line stops a shire ↗
hot-cost
The host shire's minions read their own scratchpad while the same number of minions in one other shire hammer one scratchpad word in the host shire: with 21 of each the host keeps 95.6 / 95.7 / 95.6% of its rate alone (aifoundry2 / aifoundry3 / aifoundry1-c1, mean of 3 passes; 95.5-95.7% over every pass), and with 22, 23 or 24 it stops: 0.02% on every card. An uncontended remote atomic takes 216.2 / 216.3 / 216.6 cycles round trip.
measured
three cards
One hot line stops a shire ↗
hot.cliff
The switch is sharp: 21 remote requesters leave the host at 95.5-95.7% of its rate, 22 stop it (0.02%). Rule: the bank is not saturated while N x 10 cycles < P + t_round_trip (216 cycles).
measured
three cards
One hot line stops a shire ↗
hot-edge
Energy per atomic: 19.8 nJ [16.9-23.6] contended against 1.16 nJ [1.01-1.37] spread over 32 lines: 17x.
measured
aifoundry2, aifoundry3
One hot line stops a shire ↗
hot-energy
A global atomic (amoaddg) is performed at the shire cache that homes the line. One contended line serialises at 10.00 cycles per atomic (about 60 M/s for the chip) and stops the host shire's own memory path; an uncontended remote global atomic round trip is 216 cycles.
measured
aifoundry2, aifoundry3
One hot line stops a shire ↗
mem.global-atomic
The memory shire that serves a line is picked by physical-address bits 8:6 and its L3 home shire by bits 10:6, so memory shire m serves the lines of home shires m, m+8, m+16 and m+24. Hardware read counters confirmed the memory-shire bits for 64 of 64 lines (and in all 15 passes of the three-card check).
measured
three cards
Anatomy of a memory access ↗
L43
A line's L3 home shire is PA[10:6]: consecutive 64-byte lines rotate over the 32 compute shires' L3 slices (default 'swizzle0'; the firmware leaves the swizzle register at reset).
measured
three cards
Anatomy of a memory access ↗
l3.home+}

## flow/I/3
FLOW 9 · HOT LINE
Inside shire 0: its … can be starved.

 More detail and the sources {+

One global atomic that every minion hammers lives in one line of one bank of shire 0. The atomic is shared fairly; what suffers is the host shire's own traffic through that bank.

 Leg What happens
one line the bank retires one atomic every 10.00 cycles, about 60 M/s for the chip
fair shares the host shire gets 1.004 / 1.004 / 1.004 of an even share, the lowest shire 0.998 / 0.998 / 0.999
the host alone the host's minions read their own scratchpad
21 requesters 21 minions of one other shire hammer a word in the host: the host keeps 95.6 / 95.7 / 95.6% of its rate
22 requesters the host stops: 0.02%
spread it over 32 lines, one per shire: 0.31 cycles per atomic, 1,919 M/s, 32×; 19.8 nJ against 1.16 nJ each, 17×

 Values are aifoundry2 / aifoundry3 / aifoundry1 card 1 where three are given.

 Measured and explained in One hot line stops a shire ↗.

 The facts this flow uses (8): point at one for its source

 All 32 shires hammering one global atomic homed in shire 0 (32 minions each): every shire gets an even share, the host shire 1.004 / 1.004 / 1.004 of it (1.004) and the lowest 0.998 / 0.998 / 0.999 (0.998-0.999; aifoundry2 / aifoundry3 / aifoundry1-c1), at 10.00 cycles per atomic.
measured
three cards
One hot line stops a shire ↗
hot.fair
One contended global atomic (amoaddg.w on one line, 1,024 minions): the bank retires one every 10.00 cycles, about 60 M/s for the whole chip; spread over 32 lines, one per shire, 0.31 cycles and 1,919 M/s: 32x.
measured
aifoundry2
One hot line stops a shire ↗
hot-cost
The host shire's minions read their own scratchpad while the same number of minions in one other shire hammer one scratchpad word in the host shire: with 21 of each the host keeps 95.6 / 95.7 / 95.6% of its rate alone (aifoundry2 / aifoundry3 / aifoundry1-c1, mean of 3 passes; 95.5-95.7% over every pass), and with 22, 23 or 24 it stops: 0.02% on every card. An uncontended remote atomic takes 216.2 / 216.3 / 216.6 cycles round trip.
measured
three cards
One hot line stops a shire ↗
hot.cliff
The switch is sharp: 21 remote requesters leave the host at 95.5-95.7% of its rate, 22 stop it (0.02%). Rule: the bank is not saturated while N x 10 cycles < P + t_round_trip (216 cycles).
measured
three cards
One hot line stops a shire ↗
hot-edge
Energy per atomic: 19.8 nJ [16.9-23.6] contended against 1.16 nJ [1.01-1.37] spread over 32 lines: 17x.
measured
aifoundry2, aifoundry3
One hot line stops a shire ↗
hot-energy
A global atomic (amoaddg) is performed at the shire cache that homes the line. One contended line serialises at 10.00 cycles per atomic (about 60 M/s for the chip) and stops the host shire's own memory path; an uncontended remote global atomic round trip is 216 cycles.
measured
aifoundry2, aifoundry3
One hot line stops a shire ↗
mem.global-atomic
The memory shire that serves a line is picked by physical-address bits 8:6 and its L3 home shire by bits 10:6, so memory shire m serves the lines of home shires m, m+8, m+16 and m+24. Hardware read counters confirmed the memory-shire bits for 64 of 64 lines (and in all 15 passes of the three-card check).
measured
three cards
Anatomy of a memory access ↗
L43
A line's L3 home shire is PA[10:6]: consecutive 64-byte lines rotate over the 32 compute shires' L3 slices (default 'swizzle0'; the firmware leaves the swizzle register at reset).
measured
three cards
Anatomy of a memory access ↗
l3.home+}

## flow/I/4
FLOW 9 · HOT LINE
21 minions in one … can be starved.

 More detail and the sources {+

One global atomic that every minion hammers lives in one line of one bank of shire 0. The atomic is shared fairly; what suffers is the host shire's own traffic through that bank.

 Leg What happens
one line the bank retires one atomic every 10.00 cycles, about 60 M/s for the chip
fair shares the host shire gets 1.004 / 1.004 / 1.004 of an even share, the lowest shire 0.998 / 0.998 / 0.999
the host alone the host's minions read their own scratchpad
21 requesters 21 minions of one other shire hammer a word in the host: the host keeps 95.6 / 95.7 / 95.6% of its rate
22 requesters the host stops: 0.02%
spread it over 32 lines, one per shire: 0.31 cycles per atomic, 1,919 M/s, 32×; 19.8 nJ against 1.16 nJ each, 17×

 Values are aifoundry2 / aifoundry3 / aifoundry1 card 1 where three are given.

 Measured and explained in One hot line stops a shire ↗.

 The facts this flow uses (8): point at one for its source

 All 32 shires hammering one global atomic homed in shire 0 (32 minions each): every shire gets an even share, the host shire 1.004 / 1.004 / 1.004 of it (1.004) and the lowest 0.998 / 0.998 / 0.999 (0.998-0.999; aifoundry2 / aifoundry3 / aifoundry1-c1), at 10.00 cycles per atomic.
measured
three cards
One hot line stops a shire ↗
hot.fair
One contended global atomic (amoaddg.w on one line, 1,024 minions): the bank retires one every 10.00 cycles, about 60 M/s for the whole chip; spread over 32 lines, one per shire, 0.31 cycles and 1,919 M/s: 32x.
measured
aifoundry2
One hot line stops a shire ↗
hot-cost
The host shire's minions read their own scratchpad while the same number of minions in one other shire hammer one scratchpad word in the host shire: with 21 of each the host keeps 95.6 / 95.7 / 95.6% of its rate alone (aifoundry2 / aifoundry3 / aifoundry1-c1, mean of 3 passes; 95.5-95.7% over every pass), and with 22, 23 or 24 it stops: 0.02% on every card. An uncontended remote atomic takes 216.2 / 216.3 / 216.6 cycles round trip.
measured
three cards
One hot line stops a shire ↗
hot.cliff
The switch is sharp: 21 remote requesters leave the host at 95.5-95.7% of its rate, 22 stop it (0.02%). Rule: the bank is not saturated while N x 10 cycles < P + t_round_trip (216 cycles).
measured
three cards
One hot line stops a shire ↗
hot-edge
Energy per atomic: 19.8 nJ [16.9-23.6] contended against 1.16 nJ [1.01-1.37] spread over 32 lines: 17x.
measured
aifoundry2, aifoundry3
One hot line stops a shire ↗
hot-energy
A global atomic (amoaddg) is performed at the shire cache that homes the line. One contended line serialises at 10.00 cycles per atomic (about 60 M/s for the chip) and stops the host shire's own memory path; an uncontended remote global atomic round trip is 216 cycles.
measured
aifoundry2, aifoundry3
One hot line stops a shire ↗
mem.global-atomic
The memory shire that serves a line is picked by physical-address bits 8:6 and its L3 home shire by bits 10:6, so memory shire m serves the lines of home shires m, m+8, m+16 and m+24. Hardware read counters confirmed the memory-shire bits for 64 of 64 lines (and in all 15 passes of the three-card check).
measured
three cards
Anatomy of a memory access ↗
L43
A line's L3 home shire is PA[10:6]: consecutive 64-byte lines rotate over the 32 compute shires' L3 slices (default 'swizzle0'; the firmware leaves the swizzle register at reset).
measured
three cards
Anatomy of a memory access ↗
l3.home+}

## flow/I/5
FLOW 9 · HOT LINE
22 requesters: the bank's … can be starved.

 More detail and the sources {+

One global atomic that every minion hammers lives in one line of one bank of shire 0. The atomic is shared fairly; what suffers is the host shire's own traffic through that bank.

 Leg What happens
one line the bank retires one atomic every 10.00 cycles, about 60 M/s for the chip
fair shares the host shire gets 1.004 / 1.004 / 1.004 of an even share, the lowest shire 0.998 / 0.998 / 0.999
the host alone the host's minions read their own scratchpad
21 requesters 21 minions of one other shire hammer a word in the host: the host keeps 95.6 / 95.7 / 95.6% of its rate
22 requesters the host stops: 0.02%
spread it over 32 lines, one per shire: 0.31 cycles per atomic, 1,919 M/s, 32×; 19.8 nJ against 1.16 nJ each, 17×

 Values are aifoundry2 / aifoundry3 / aifoundry1 card 1 where three are given.

 Measured and explained in One hot line stops a shire ↗.

 The facts this flow uses (8): point at one for its source

 All 32 shires hammering one global atomic homed in shire 0 (32 minions each): every shire gets an even share, the host shire 1.004 / 1.004 / 1.004 of it (1.004) and the lowest 0.998 / 0.998 / 0.999 (0.998-0.999; aifoundry2 / aifoundry3 / aifoundry1-c1), at 10.00 cycles per atomic.
measured
three cards
One hot line stops a shire ↗
hot.fair
One contended global atomic (amoaddg.w on one line, 1,024 minions): the bank retires one every 10.00 cycles, about 60 M/s for the whole chip; spread over 32 lines, one per shire, 0.31 cycles and 1,919 M/s: 32x.
measured
aifoundry2
One hot line stops a shire ↗
hot-cost
The host shire's minions read their own scratchpad while the same number of minions in one other shire hammer one scratchpad word in the host shire: with 21 of each the host keeps 95.6 / 95.7 / 95.6% of its rate alone (aifoundry2 / aifoundry3 / aifoundry1-c1, mean of 3 passes; 95.5-95.7% over every pass), and with 22, 23 or 24 it stops: 0.02% on every card. An uncontended remote atomic takes 216.2 / 216.3 / 216.6 cycles round trip.
measured
three cards
One hot line stops a shire ↗
hot.cliff
The switch is sharp: 21 remote requesters leave the host at 95.5-95.7% of its rate, 22 stop it (0.02%). Rule: the bank is not saturated while N x 10 cycles < P + t_round_trip (216 cycles).
measured
three cards
One hot line stops a shire ↗
hot-edge
Energy per atomic: 19.8 nJ [16.9-23.6] contended against 1.16 nJ [1.01-1.37] spread over 32 lines: 17x.
measured
aifoundry2, aifoundry3
One hot line stops a shire ↗
hot-energy
A global atomic (amoaddg) is performed at the shire cache that homes the line. One contended line serialises at 10.00 cycles per atomic (about 60 M/s for the chip) and stops the host shire's own memory path; an uncontended remote global atomic round trip is 216 cycles.
measured
aifoundry2, aifoundry3
One hot line stops a shire ↗
mem.global-atomic
The memory shire that serves a line is picked by physical-address bits 8:6 and its L3 home shire by bits 10:6, so memory shire m serves the lines of home shires m, m+8, m+16 and m+24. Hardware read counters confirmed the memory-shire bits for 64 of 64 lines (and in all 15 passes of the three-card check).
measured
three cards
Anatomy of a memory access ↗
L43
A line's L3 home shire is PA[10:6]: consecutive 64-byte lines rotate over the 32 compute shires' L3 slices (default 'swizzle0'; the firmware leaves the swizzle register at reset).
measured
three cards
Anatomy of a memory access ↗
l3.home+}

## flow/J/0
FLOW 0 · ALLREDUCE
Levels 0-2, inside each neighbourhood … and back down.

 More detail and the sources {+

TensorReduce climbs a tree of ten levels and TensorBroadcast brings the result back down: at level h a minion whose ID has bit h as its lowest set bit sends to the minion with that bit cleared. Levels 0-2 follow the fast network's edges inside a neighbourhood, 3-4 cross the shire's crossbar, and 5-9 cross the mesh between shires, rooted at shire 0.

 Leg What happens
levels 0-2 the fast network's tree edges: 68–71 cycles per level
levels 3-4 through the crossbar: 117 cycles per level
levels 5-9 over the mesh: 164–234 cycles per level
back down TensorBroadcast: all 1,024 minions have the sum after 1,393 cycles (2.3 µs)
against a barrier a chip barrier from global atomics and credits: 4,998–5,013 cycles (about 8.3 µs)

 One shire's 32 minions reduce in 444 cycles; the per-level costs are from the on-chip communication page's ladder. The tree is the benchmark's (nocbench); its mesh legs are drawn as requests, x first (the order was measured for loads and stores; whether the tree's messages travel as requests was not tested).

 Measured and explained in On-chip communication ↗.

 The facts this flow uses (11): point at one for its source

 The allreduce benchmark's tree: at level h, a minion whose ID has bit h as its lowest set bit sends its partial sum to the minion with that bit cleared (TensorReduce), levels 0 to 9, and the result comes back down the same tree (TensorBroadcast). Levels 0-2 join a neighbourhood's 8 minions along the fast network's edges, levels 3-4 its 4 neighbourhoods, levels 5-9 the 32 shires, rooted at minion 0 of shire 0.
documented
On-chip communication ↗
ar.tree
The fast local messaging network links minions within a neighbourhood only along the reduction tree: 0-1, 0-2, 0-4, 2-3, 4-5, 4-6, 6-7.
documented
On-chip communication ↗
neigh.fln-edges
Each allreduce tree level adds about one round trip: 68-71 cycles on the fast network (levels 0-2), 117 through the crossbar (levels 3-4) and 164-234 over the mesh (levels 5-9).
measured
three cards
On-chip communication ↗
sync.tree-levels
Hardware allreduce (TensorReduce + TensorBroadcast) of 32 B over a shire's 32 minions: 444 cycles (0.74 us), 444.06-444.31 on all three cards.
measured
three cards
On-chip communication ↗
sync-allreduce32
Hardware allreduce of 32 B over all 1,024 minions: 1,393 cycles (2.3 us), 1,392.6-1,393.4 on the three cards; an A100 grid.sync() alone is 1.1-1.2 us.
measured
three cards
On-chip communication ↗
sync-allreduce1024
Shire barrier (fast local barrier + credits, 32 minions, all 32 shires at once): 233 cycles (388 ns); 232.5-232.7 on the three cards.
measured
three cards
On-chip communication ↗
sync-shire-barrier
Chip-wide barrier built from FLB, global atomics and credits: 4,976-4,991 cycles with one minion per shire, 4,998-5,013 with all 1,024 (about 8.3 us); the allreduce tree does it in 2.3 us.
measured
three cards
On-chip communication ↗
sync-chip-barrier
Fast local barrier: 32 barrier counters per shire, 8 bits wide (enough for all 64 harts), joined atomically with one CSR write (0x820) from user mode.
documented
On-chip communication ↗
sync.flb
Fast credit counters: two per hart (four per minion); any hart in any shire adds credits by writing a 64-bit mask to a shire's CREDINC0-3 ESRs; reading an empty counter blocks until a credit arrives.
documented
On-chip communication ↗
sync.fcc
TensorSend round trip, 32 B register to register inside a shire: 68 cycles (113 ns) on the 7 fast-network tree edges of each neighbourhood, 114-115 cycles (190 ns) for every other pair.
measured
three cards
On-chip communication ↗
ts-rt-fln
The mesh routes in dimension order, and a request and its reply take opposite orders: a request goes x first, then y, and a reply y first, then x, on the logical map, so a reply retraces its request's route backwards. Measured on 29 September (E56) with sets of streams between shires chosen so that their streams share one directed link under one order and none under the other: 1 KB tensor loads, whose data travel as replies, fell to 0.54-0.77 of their bandwidth alone when they shared a link under y first and held at 1.00 when they shared one under x first; tensor stores, whose data travel as requests, showed the mirror (0.52-0.76 against 1.00). A shared link carried about 92 GB/s. The same on aifoundry1 card 1 (development), aifoundry3 (the frozen validation) and aifoundry2 (the same frozen test, run as a third card on the evening of 29 September), three passes each.
measured
three cards
no published page yet
L104+}

## flow/J/1
FLOW 0 · ALLREDUCE
Levels 0-2, inside each neighbourhood … and back down.

 More detail and the sources {+

TensorReduce climbs a tree of ten levels and TensorBroadcast brings the result back down: at level h a minion whose ID has bit h as its lowest set bit sends to the minion with that bit cleared. Levels 0-2 follow the fast network's edges inside a neighbourhood, 3-4 cross the shire's crossbar, and 5-9 cross the mesh between shires, rooted at shire 0.

 Leg What happens
levels 0-2 the fast network's tree edges: 68–71 cycles per level
levels 3-4 through the crossbar: 117 cycles per level
levels 5-9 over the mesh: 164–234 cycles per level
back down TensorBroadcast: all 1,024 minions have the sum after 1,393 cycles (2.3 µs)
against a barrier a chip barrier from global atomics and credits: 4,998–5,013 cycles (about 8.3 µs)

 One shire's 32 minions reduce in 444 cycles; the per-level costs are from the on-chip communication page's ladder. The tree is the benchmark's (nocbench); its mesh legs are drawn as requests, x first (the order was measured for loads and stores; whether the tree's messages travel as requests was not tested).

 Measured and explained in On-chip communication ↗.

 The facts this flow uses (11): point at one for its source

 The allreduce benchmark's tree: at level h, a minion whose ID has bit h as its lowest set bit sends its partial sum to the minion with that bit cleared (TensorReduce), levels 0 to 9, and the result comes back down the same tree (TensorBroadcast). Levels 0-2 join a neighbourhood's 8 minions along the fast network's edges, levels 3-4 its 4 neighbourhoods, levels 5-9 the 32 shires, rooted at minion 0 of shire 0.
documented
On-chip communication ↗
ar.tree
The fast local messaging network links minions within a neighbourhood only along the reduction tree: 0-1, 0-2, 0-4, 2-3, 4-5, 4-6, 6-7.
documented
On-chip communication ↗
neigh.fln-edges
Each allreduce tree level adds about one round trip: 68-71 cycles on the fast network (levels 0-2), 117 through the crossbar (levels 3-4) and 164-234 over the mesh (levels 5-9).
measured
three cards
On-chip communication ↗
sync.tree-levels
Hardware allreduce (TensorReduce + TensorBroadcast) of 32 B over a shire's 32 minions: 444 cycles (0.74 us), 444.06-444.31 on all three cards.
measured
three cards
On-chip communication ↗
sync-allreduce32
Hardware allreduce of 32 B over all 1,024 minions: 1,393 cycles (2.3 us), 1,392.6-1,393.4 on the three cards; an A100 grid.sync() alone is 1.1-1.2 us.
measured
three cards
On-chip communication ↗
sync-allreduce1024
Shire barrier (fast local barrier + credits, 32 minions, all 32 shires at once): 233 cycles (388 ns); 232.5-232.7 on the three cards.
measured
three cards
On-chip communication ↗
sync-shire-barrier
Chip-wide barrier built from FLB, global atomics and credits: 4,976-4,991 cycles with one minion per shire, 4,998-5,013 with all 1,024 (about 8.3 us); the allreduce tree does it in 2.3 us.
measured
three cards
On-chip communication ↗
sync-chip-barrier
Fast local barrier: 32 barrier counters per shire, 8 bits wide (enough for all 64 harts), joined atomically with one CSR write (0x820) from user mode.
documented
On-chip communication ↗
sync.flb
Fast credit counters: two per hart (four per minion); any hart in any shire adds credits by writing a 64-bit mask to a shire's CREDINC0-3 ESRs; reading an empty counter blocks until a credit arrives.
documented
On-chip communication ↗
sync.fcc
TensorSend round trip, 32 B register to register inside a shire: 68 cycles (113 ns) on the 7 fast-network tree edges of each neighbourhood, 114-115 cycles (190 ns) for every other pair.
measured
three cards
On-chip communication ↗
ts-rt-fln
The mesh routes in dimension order, and a request and its reply take opposite orders: a request goes x first, then y, and a reply y first, then x, on the logical map, so a reply retraces its request's route backwards. Measured on 29 September (E56) with sets of streams between shires chosen so that their streams share one directed link under one order and none under the other: 1 KB tensor loads, whose data travel as replies, fell to 0.54-0.77 of their bandwidth alone when they shared a link under y first and held at 1.00 when they shared one under x first; tensor stores, whose data travel as requests, showed the mirror (0.52-0.76 against 1.00). A shared link carried about 92 GB/s. The same on aifoundry1 card 1 (development), aifoundry3 (the frozen validation) and aifoundry2 (the same frozen test, run as a third card on the evening of 29 September), three passes each.
measured
three cards
no published page yet
L104+}

## flow/J/2
FLOW 0 · ALLREDUCE
Levels 3-4, across the crossbar: … and back down.

 More detail and the sources {+

TensorReduce climbs a tree of ten levels and TensorBroadcast brings the result back down: at level h a minion whose ID has bit h as its lowest set bit sends to the minion with that bit cleared. Levels 0-2 follow the fast network's edges inside a neighbourhood, 3-4 cross the shire's crossbar, and 5-9 cross the mesh between shires, rooted at shire 0.

 Leg What happens
levels 0-2 the fast network's tree edges: 68–71 cycles per level
levels 3-4 through the crossbar: 117 cycles per level
levels 5-9 over the mesh: 164–234 cycles per level
back down TensorBroadcast: all 1,024 minions have the sum after 1,393 cycles (2.3 µs)
against a barrier a chip barrier from global atomics and credits: 4,998–5,013 cycles (about 8.3 µs)

 One shire's 32 minions reduce in 444 cycles; the per-level costs are from the on-chip communication page's ladder. The tree is the benchmark's (nocbench); its mesh legs are drawn as requests, x first (the order was measured for loads and stores; whether the tree's messages travel as requests was not tested).

 Measured and explained in On-chip communication ↗.

 The facts this flow uses (11): point at one for its source

 The allreduce benchmark's tree: at level h, a minion whose ID has bit h as its lowest set bit sends its partial sum to the minion with that bit cleared (TensorReduce), levels 0 to 9, and the result comes back down the same tree (TensorBroadcast). Levels 0-2 join a neighbourhood's 8 minions along the fast network's edges, levels 3-4 its 4 neighbourhoods, levels 5-9 the 32 shires, rooted at minion 0 of shire 0.
documented
On-chip communication ↗
ar.tree
The fast local messaging network links minions within a neighbourhood only along the reduction tree: 0-1, 0-2, 0-4, 2-3, 4-5, 4-6, 6-7.
documented
On-chip communication ↗
neigh.fln-edges
Each allreduce tree level adds about one round trip: 68-71 cycles on the fast network (levels 0-2), 117 through the crossbar (levels 3-4) and 164-234 over the mesh (levels 5-9).
measured
three cards
On-chip communication ↗
sync.tree-levels
Hardware allreduce (TensorReduce + TensorBroadcast) of 32 B over a shire's 32 minions: 444 cycles (0.74 us), 444.06-444.31 on all three cards.
measured
three cards
On-chip communication ↗
sync-allreduce32
Hardware allreduce of 32 B over all 1,024 minions: 1,393 cycles (2.3 us), 1,392.6-1,393.4 on the three cards; an A100 grid.sync() alone is 1.1-1.2 us.
measured
three cards
On-chip communication ↗
sync-allreduce1024
Shire barrier (fast local barrier + credits, 32 minions, all 32 shires at once): 233 cycles (388 ns); 232.5-232.7 on the three cards.
measured
three cards
On-chip communication ↗
sync-shire-barrier
Chip-wide barrier built from FLB, global atomics and credits: 4,976-4,991 cycles with one minion per shire, 4,998-5,013 with all 1,024 (about 8.3 us); the allreduce tree does it in 2.3 us.
measured
three cards
On-chip communication ↗
sync-chip-barrier
Fast local barrier: 32 barrier counters per shire, 8 bits wide (enough for all 64 harts), joined atomically with one CSR write (0x820) from user mode.
documented
On-chip communication ↗
sync.flb
Fast credit counters: two per hart (four per minion); any hart in any shire adds credits by writing a 64-bit mask to a shire's CREDINC0-3 ESRs; reading an empty counter blocks until a credit arrives.
documented
On-chip communication ↗
sync.fcc
TensorSend round trip, 32 B register to register inside a shire: 68 cycles (113 ns) on the 7 fast-network tree edges of each neighbourhood, 114-115 cycles (190 ns) for every other pair.
measured
three cards
On-chip communication ↗
ts-rt-fln
The mesh routes in dimension order, and a request and its reply take opposite orders: a request goes x first, then y, and a reply y first, then x, on the logical map, so a reply retraces its request's route backwards. Measured on 29 September (E56) with sets of streams between shires chosen so that their streams share one directed link under one order and none under the other: 1 KB tensor loads, whose data travel as replies, fell to 0.54-0.77 of their bandwidth alone when they shared a link under y first and held at 1.00 when they shared one under x first; tensor stores, whose data travel as requests, showed the mirror (0.52-0.76 against 1.00). A shared link carried about 92 GB/s. The same on aifoundry1 card 1 (development), aifoundry3 (the frozen validation) and aifoundry2 (the same frozen test, run as a third card on the evening of 29 September), three passes each.
measured
three cards
no published page yet
L104+}

## flow/J/3
FLOW 0 · ALLREDUCE
Levels 5-9, over the mesh: … and back down.

 More detail and the sources {+

TensorReduce climbs a tree of ten levels and TensorBroadcast brings the result back down: at level h a minion whose ID has bit h as its lowest set bit sends to the minion with that bit cleared. Levels 0-2 follow the fast network's edges inside a neighbourhood, 3-4 cross the shire's crossbar, and 5-9 cross the mesh between shires, rooted at shire 0.

 Leg What happens
levels 0-2 the fast network's tree edges: 68–71 cycles per level
levels 3-4 through the crossbar: 117 cycles per level
levels 5-9 over the mesh: 164–234 cycles per level
back down TensorBroadcast: all 1,024 minions have the sum after 1,393 cycles (2.3 µs)
against a barrier a chip barrier from global atomics and credits: 4,998–5,013 cycles (about 8.3 µs)

 One shire's 32 minions reduce in 444 cycles; the per-level costs are from the on-chip communication page's ladder. The tree is the benchmark's (nocbench); its mesh legs are drawn as requests, x first (the order was measured for loads and stores; whether the tree's messages travel as requests was not tested).

 Measured and explained in On-chip communication ↗.

 The facts this flow uses (11): point at one for its source

 The allreduce benchmark's tree: at level h, a minion whose ID has bit h as its lowest set bit sends its partial sum to the minion with that bit cleared (TensorReduce), levels 0 to 9, and the result comes back down the same tree (TensorBroadcast). Levels 0-2 join a neighbourhood's 8 minions along the fast network's edges, levels 3-4 its 4 neighbourhoods, levels 5-9 the 32 shires, rooted at minion 0 of shire 0.
documented
On-chip communication ↗
ar.tree
The fast local messaging network links minions within a neighbourhood only along the reduction tree: 0-1, 0-2, 0-4, 2-3, 4-5, 4-6, 6-7.
documented
On-chip communication ↗
neigh.fln-edges
Each allreduce tree level adds about one round trip: 68-71 cycles on the fast network (levels 0-2), 117 through the crossbar (levels 3-4) and 164-234 over the mesh (levels 5-9).
measured
three cards
On-chip communication ↗
sync.tree-levels
Hardware allreduce (TensorReduce + TensorBroadcast) of 32 B over a shire's 32 minions: 444 cycles (0.74 us), 444.06-444.31 on all three cards.
measured
three cards
On-chip communication ↗
sync-allreduce32
Hardware allreduce of 32 B over all 1,024 minions: 1,393 cycles (2.3 us), 1,392.6-1,393.4 on the three cards; an A100 grid.sync() alone is 1.1-1.2 us.
measured
three cards
On-chip communication ↗
sync-allreduce1024
Shire barrier (fast local barrier + credits, 32 minions, all 32 shires at once): 233 cycles (388 ns); 232.5-232.7 on the three cards.
measured
three cards
On-chip communication ↗
sync-shire-barrier
Chip-wide barrier built from FLB, global atomics and credits: 4,976-4,991 cycles with one minion per shire, 4,998-5,013 with all 1,024 (about 8.3 us); the allreduce tree does it in 2.3 us.
measured
three cards
On-chip communication ↗
sync-chip-barrier
Fast local barrier: 32 barrier counters per shire, 8 bits wide (enough for all 64 harts), joined atomically with one CSR write (0x820) from user mode.
documented
On-chip communication ↗
sync.flb
Fast credit counters: two per hart (four per minion); any hart in any shire adds credits by writing a 64-bit mask to a shire's CREDINC0-3 ESRs; reading an empty counter blocks until a credit arrives.
documented
On-chip communication ↗
sync.fcc
TensorSend round trip, 32 B register to register inside a shire: 68 cycles (113 ns) on the 7 fast-network tree edges of each neighbourhood, 114-115 cycles (190 ns) for every other pair.
measured
three cards
On-chip communication ↗
ts-rt-fln
The mesh routes in dimension order, and a request and its reply take opposite orders: a request goes x first, then y, and a reply y first, then x, on the logical map, so a reply retraces its request's route backwards. Measured on 29 September (E56) with sets of streams between shires chosen so that their streams share one directed link under one order and none under the other: 1 KB tensor loads, whose data travel as replies, fell to 0.54-0.77 of their bandwidth alone when they shared a link under y first and held at 1.00 when they shared one under x first; tensor stores, whose data travel as requests, showed the mirror (0.52-0.76 against 1.00). A shared link carried about 92 GB/s. The same on aifoundry1 card 1 (development), aifoundry3 (the frozen validation) and aifoundry2 (the same frozen test, run as a third card on the evening of 29 September), three passes each.
measured
three cards
no published page yet
L104+}

## flow/J/4
FLOW 0 · ALLREDUCE
TensorBroadcast takes the sum back … and back down.

 More detail and the sources {+

TensorReduce climbs a tree of ten levels and TensorBroadcast brings the result back down: at level h a minion whose ID has bit h as its lowest set bit sends to the minion with that bit cleared. Levels 0-2 follow the fast network's edges inside a neighbourhood, 3-4 cross the shire's crossbar, and 5-9 cross the mesh between shires, rooted at shire 0.

 Leg What happens
levels 0-2 the fast network's tree edges: 68–71 cycles per level
levels 3-4 through the crossbar: 117 cycles per level
levels 5-9 over the mesh: 164–234 cycles per level
back down TensorBroadcast: all 1,024 minions have the sum after 1,393 cycles (2.3 µs)
against a barrier a chip barrier from global atomics and credits: 4,998–5,013 cycles (about 8.3 µs)

 One shire's 32 minions reduce in 444 cycles; the per-level costs are from the on-chip communication page's ladder. The tree is the benchmark's (nocbench); its mesh legs are drawn as requests, x first (the order was measured for loads and stores; whether the tree's messages travel as requests was not tested).

 Measured and explained in On-chip communication ↗.

 The facts this flow uses (11): point at one for its source

 The allreduce benchmark's tree: at level h, a minion whose ID has bit h as its lowest set bit sends its partial sum to the minion with that bit cleared (TensorReduce), levels 0 to 9, and the result comes back down the same tree (TensorBroadcast). Levels 0-2 join a neighbourhood's 8 minions along the fast network's edges, levels 3-4 its 4 neighbourhoods, levels 5-9 the 32 shires, rooted at minion 0 of shire 0.
documented
On-chip communication ↗
ar.tree
The fast local messaging network links minions within a neighbourhood only along the reduction tree: 0-1, 0-2, 0-4, 2-3, 4-5, 4-6, 6-7.
documented
On-chip communication ↗
neigh.fln-edges
Each allreduce tree level adds about one round trip: 68-71 cycles on the fast network (levels 0-2), 117 through the crossbar (levels 3-4) and 164-234 over the mesh (levels 5-9).
measured
three cards
On-chip communication ↗
sync.tree-levels
Hardware allreduce (TensorReduce + TensorBroadcast) of 32 B over a shire's 32 minions: 444 cycles (0.74 us), 444.06-444.31 on all three cards.
measured
three cards
On-chip communication ↗
sync-allreduce32
Hardware allreduce of 32 B over all 1,024 minions: 1,393 cycles (2.3 us), 1,392.6-1,393.4 on the three cards; an A100 grid.sync() alone is 1.1-1.2 us.
measured
three cards
On-chip communication ↗
sync-allreduce1024
Shire barrier (fast local barrier + credits, 32 minions, all 32 shires at once): 233 cycles (388 ns); 232.5-232.7 on the three cards.
measured
three cards
On-chip communication ↗
sync-shire-barrier
Chip-wide barrier built from FLB, global atomics and credits: 4,976-4,991 cycles with one minion per shire, 4,998-5,013 with all 1,024 (about 8.3 us); the allreduce tree does it in 2.3 us.
measured
three cards
On-chip communication ↗
sync-chip-barrier
Fast local barrier: 32 barrier counters per shire, 8 bits wide (enough for all 64 harts), joined atomically with one CSR write (0x820) from user mode.
documented
On-chip communication ↗
sync.flb
Fast credit counters: two per hart (four per minion); any hart in any shire adds credits by writing a 64-bit mask to a shire's CREDINC0-3 ESRs; reading an empty counter blocks until a credit arrives.
documented
On-chip communication ↗
sync.fcc
TensorSend round trip, 32 B register to register inside a shire: 68 cycles (113 ns) on the 7 fast-network tree edges of each neighbourhood, 114-115 cycles (190 ns) for every other pair.
measured
three cards
On-chip communication ↗
ts-rt-fln
The mesh routes in dimension order, and a request and its reply take opposite orders: a request goes x first, then y, and a reply y first, then x, on the logical map, so a reply retraces its request's route backwards. Measured on 29 September (E56) with sets of streams between shires chosen so that their streams share one directed link under one order and none under the other: 1 KB tensor loads, whose data travel as replies, fell to 0.54-0.77 of their bandwidth alone when they shared a link under y first and held at 1.00 when they shared one under x first; tensor stores, whose data travel as requests, showed the mirror (0.52-0.76 against 1.00). A shared link carried about 92 GB/s. The same on aifoundry1 card 1 (development), aifoundry3 (the frozen validation) and aifoundry2 (the same frozen test, run as a third card on the evening of 29 September), three passes each.
measured
three cards
no published page yet
L104+}

## flow/K/0
FLOW B · BROADCAST
The value sits in hart … what each costs.

 More detail and the sources {+

How one value, 32 B or 1 KB, gets from minion 0 of shire 0 to all 1,024 minions, and what each way costs. The chip offers four: the hardware tree (TensorBroadcast), a relay from shire to shire, one line in memory that every minion loads, and the multicast every kernel launch already makes.

 Leg What happens
the value hart 0's 32 vector registers of 32 bytes: 32 B fills one, 1 KB all of them; only hart 0 issues tensor instructions
tree: mesh TensorBroadcast down the allreduce's tree, levels 9 to 5 between shires: 164–234 cycles a level, up and down
tree: shire levels 4 and 3 through the crossbar, 117 cycles a level; 2 to 0 on the tree edges, 68–71 cycles; in every shire at once
tree, timed with the reduction, 32 B: 444 cycles (0.74 µs) over 32 minions, 1,393 cycles (2.3 µs) over 1,024; 1 KB: 1,354 cycles (2.26 µs) and 3,236–3,244 cycles (5.4 µs)
relay or DRAM a hand-off to the next shire 17.8 pJ per byte, its write and its read (8.9 pJ/B moved), about a thirteenth of a DRAM round trip; every shire reading DRAM 115 pJ/B each, the chip's 76 GB/s shared
one line every minion loads one line from its L3 home: one load 110 + 12 cycles a hop; one request per shire at a time; 15 pJ/B over the mesh
at its home the line's bank: an atomic every 10.00 cycles; 31 requesters, one a shire, left the home's reader at 100%; 22 from one shire hammering it stop the home's loads (0.02%)
the launch one 64-byte message, one ESR broadcast, every hart reads it, one atomic a shire: an empty kernel 103.6–104.1 µs queued on 32 shires, 91.2 / 92.2 / 92.4 on one
compared to all 1,024: the tree 2.3 µs (32 B) or 5.4 µs (1 KB); a chip barrier alone 8.3 µs; a queued launch 103.6–104.1 µs

 Not measured: the tree's broadcast half on its own (it was timed only with the reduction) and the tree's energy (fact bc.half); how long a relay takes to reach every shire (the relay moved 1 MB slabs down a pipeline); every minion loading one line at once (the hot-line runs used atomics); the launch's multicast apart from the rest of a launch, and its energy (fact bc.launch-31).

 The mesh takes a request x first and a reply y first (measured for loads and stores): the reads' requests are drawn x first, and the data they bring back, the relay's hand-offs among them, y first, and the tree's messages as requests, x first. The interrupt that starts a launch is drawn at each shire, not along a route: its path over the mesh is not documented.

 Measured and explained in On-chip communication ↗.

 The facts this flow uses (31): point at one for its source

 Each lane's register file holds 64 × 32-bit entries (32 per thread), so each hart has 32 vector registers of 32 bytes; 8 mask registers of 8 bits.
documented
On-chip communication ↗
minion.vpu-regs
Only hart 0 of a minion may issue tensor instructions; hart 1 may only issue TensorLoadL2Scp, TensorWait and tensor_coop accesses.
documented
Limits of observability ↗
minion.tensor-hart0
TensorBroadcast sends COUNT vector registers of 32 bytes down a fully balanced binary tree: at node height HEIGHT a hart whose mhartid is a multiple of 2^(HEIGHT+2) sends to hart mhartid + 2^(HEIGHT+1), and with FUNCT = MOVE every hart ends with the root's value. N harts take log2 N steps, HEIGHT from log2(N) - 1 down to 0, and each step waits for both of its harts, their vector registers stalled until the data has moved. Hart 0 of minion m is hart 2m, so a broadcast from minion 0 to all 1,024 minions takes ten steps, the first to minion 512, minion 0 of shire 16.
documented
On-chip communication ↗
bc.tensorbroadcast
The allreduce benchmark's tree: at level h, a minion whose ID has bit h as its lowest set bit sends its partial sum to the minion with that bit cleared (TensorReduce), levels 0 to 9, and the result comes back down the same tree (TensorBroadcast). Levels 0-2 join a neighbourhood's 8 minions along the fast network's edges, levels 3-4 its 4 neighbourhoods, levels 5-9 the 32 shires, rooted at minion 0 of shire 0.
documented
On-chip communication ↗
ar.tree
The fast local messaging network links minions within a neighbourhood only along the reduction tree: 0-1, 0-2, 0-4, 2-3, 4-5, 4-6, 6-7.
documented
On-chip communication ↗
neigh.fln-edges
Each allreduce tree level adds about one round trip: 68-71 cycles on the fast network (levels 0-2), 117 through the crossbar (levels 3-4) and 164-234 over the mesh (levels 5-9).
measured
three cards
On-chip communication ↗
sync.tree-levels
Hardware allreduce (TensorReduce + TensorBroadcast) of 32 B over a shire's 32 minions: 444 cycles (0.74 us), 444.06-444.31 on all three cards.
measured
three cards
On-chip communication ↗
sync-allreduce32
Hardware allreduce of 32 B over all 1,024 minions: 1,393 cycles (2.3 us), 1,392.6-1,393.4 on the three cards; an A100 grid.sync() alone is 1.1-1.2 us.
measured
three cards
On-chip communication ↗
sync-allreduce1024
The same hardware allreduce with 1 KB (32 vector registers) instead of 32 B: 1,354 cycles over a shire's 32 minions (1,354.05-1,354.16 in every pass on the three cards, 2.26 µs) and 3,236-3,244 cycles over all 1,024 minions (each card's median over three passes: aifoundry2 3,236.33, aifoundry3 3,243.35, aifoundry1-c1 3,244.27; 5.4 µs at 600 MHz), against 444 and 1,393 cycles for 32 B.
measured
three cards
On-chip communication ↗
bc.allreduce-1kb
The broadcast half of the tree was never timed on its own: nocbench times TensorReduce up the tree and TensorBroadcast back down as one operation, one cycle count around both, so the broadcast is part of the allreduce's 444 cycles over 32 minions and 1,393 over 1,024 (32 B). Neither half's energy was measured: the energy manual's synchronisation table gives none for the tree.
model
On-chip communication ↗
bc.half
Messaging energy, 1 KB TensorSend: 0.69 pJ/B between the two minions of a pair, 2.16 around a neighbourhood, 2.22 around a shire, 12.5-18.3 across the mesh (busy cores included).
measured
three cards
On-chip communication ↗
ts-e-pair
Relay energy per byte moved, each byte counted once when written and once when read: through DRAM 116.2 pJ/B [104.5-135.3], to the next shire, which reads the previous shire's scratchpad, 8.9 [7.6-10.2], in the own scratchpad 4.3 [3.8-5.1]; a hand-off writes every byte once and reads it once, so a byte handed to the next shire costs 17.8 pJ (232 through DRAM).
measured
three cards
Hand it to the next shire: on-chip relay vs DRAM ↗
relay-energy
Handing a slab to the next shire through its scratchpad costs 12.9x, 13.0x and 13.1x less energy per byte than the DRAM round trip (aifoundry2, aifoundry3, aifoundry1-c1): about a thirteenth, the same on every card at 99%.
measured
three cards
Hand it to the next shire: on-chip relay vs DRAM ↗
relay-13x
Relay bandwidth (8 stages, 1,024 minions; bytes read plus bytes written): 47.7 GB/s through DRAM, 592.5 GB/s to the next shire (12.4x), 1487 GB/s in the own scratchpad (aifoundry2 pass means; the other cards within 1.5%).
measured
aifoundry2 pass means (the other cards within 1.5%)
Hand it to the next shire: on-chip relay vs DRAM ↗
relay-bw
DRAM: 114.6 pJ/B [89.0-141.3] above idle, 1 KB tensor loads (L1: 32 B vector loads) by every minion at 600 MHz; per card a2 111.5, a3 105.6, a1c1 126.6.
measured
three cards
The energy manual ↗
e-dram
DRAM streaming: 76 GB/s for the whole chip (0.124 B per minion-cycle), about 64% of the 119 GB/s that 16 x 16-bit channels carry at 3,733 MT/s; about a twentieth of an A100.
measured
aifoundry2, aifoundry3
Ridge points ↗
bw-dram
A line's L3 home shire is PA[10:6]: consecutive 64-byte lines rotate over the 32 compute shires' L3 slices (default 'swizzle0'; the firmware leaves the swizzle register at reset).
measured
three cards
Anatomy of a memory access ↗
l3.home
L3 hit: 110 + 12 cycles per mesh hop between the requesting shire and the line's home shire (fitted 110.5 + 11.99 on three cards); 159-169 cycles (265-282 ns) on average depending on the requesting shire.
measured
three cards
Anatomy of a memory access ↗
l3.latency
Inside a shire, requests to one line are kept in order, and 'Two requests to the mesh will never have the same address outstanding': when every minion of a shire loads one line homed in another shire, the shire has at most one request for it on the mesh at a time. The L2's 8-entry read buffer is there for 'multiple readers of the same cache line', its hits 'serviced once per clock'; L3 reads at the home do not use it.
documented
no published page yet
bc.one-request
L3 (over the mesh): 14.7 pJ/B [7.1-20.5] above idle, 1 KB tensor loads (L1: 32 B vector loads) by every minion at 600 MHz; per card a2 12.3, a3 13.5, a1c1 18.4.
measured
three cards
The energy manual ↗
e-l3
One contended global atomic (amoaddg.w on one line, 1,024 minions): the bank retires one every 10.00 cycles, about 60 M/s for the whole chip; spread over 32 lines, one per shire, 0.31 cycles and 1,919 M/s: 32x.
measured
aifoundry2
One hot line stops a shire ↗
hot-cost
31 minions, one in each other shire, hammering one global atomic homed in shire 0 kept its bank retiring one every 10.00 cycles, while shire 0's one minion reading its own scratchpad kept 100% of its rate alone, in three passes on each of the three cards (the prediction was 1% or less). Whether they would stop a shire whose 32 minions all read was not tested. Each shire's leader polling one counter hung the relay's first barrier (one development run).
measured
three cards
One hot line stops a shire ↗
bc.pollers
The host shire's minions read their own scratchpad while the same number of minions in one other shire hammer one scratchpad word in the host shire: with 21 of each the host keeps 95.6 / 95.7 / 95.6% of its rate alone (aifoundry2 / aifoundry3 / aifoundry1-c1, mean of 3 passes; 95.5-95.7% over every pass), and with 22, 23 or 24 it stops: 0.02% on every card. An uncontended remote atomic takes 216.2 / 216.3 / 216.6 cycles round trip.
measured
three cards
One hot line stops a shire ↗
hot.cliff
A global atomic (amoaddg) is performed at the shire cache that homes the line. One contended line serialises at 10.00 cycles per atomic (about 60 M/s for the chip) and stops the host shire's own memory path; an uncontended remote global atomic round trip is 216 cycles.
measured
aifoundry2, aifoundry3
One hot line stops a shire ↗
mem.global-atomic
ESR broadcast: one request writes the same system register in every shire of a mask (32 bits for the compute shires, 8 for the memory shires): software writes the value to the broadcast data register, then the target register and the masks to a broadcast request register. A shire's IPI_TRIGGER register takes a 64-bit mask of its harts and interrupts each hart whose bit is set; the firmware's broadcast system call writes the first two.
documented
no published page yet
bc.esr-ipi
Every kernel launch is a broadcast. The master shire's firmware copies the 64-byte launch message into a buffer in its own scratchpad and evicts it to the L2, raises the interrupt on all 64 harts of every shire in the kernel's mask with one ESR broadcast, and polls a shire mask beside the buffer: each hart evicts its stale L1 copy and reads the message, and the last of a shire's 64 harts clears that shire's bit with a global atomic AND. The launch goes on once every bit is clear.
documented
no published page yet
bc.launch-multicast
Queued back to back, an empty kernel costs the card 103.6 / 103.7 / 104.1 µs on all 32 shires and 91.2 / 92.2 / 92.4 µs on one (aifoundry2 / aifoundry3 / aifoundry1-c1): the other 31 shires add 12.4 / 11.4 / 11.6 µs (11.4-12.4 µs), the rest the same for one shire or 32. Which part of that is the launch's multicast (the interrupt, every hart reading the message, the shires' acknowledging atomics) and which the kernel's own start and finish was not measured.
model
three cards
Over the PCIe link ↗
bc.launch-31
An empty kernel on all 32 compute shires, launched and waited for: 566 / 556 / 565 µs (556-566 µs) from launch to completion (aifoundry2 / aifoundry3 / aifoundry1-c1); 100 launches queued back to back: 103.6 / 103.7 / 104.1 µs each (103.6-104.1 µs) on 32 shires and 91.2 / 92.2 / 92.4 on one shire. The card's own cost is the queued figure: a lone launch waited for adds 463 / 452 / 461 µs (452-463 µs, each run's difference), most of the runtime's 500 µs idle poll (fact pcie.poll), and a one-shire lone launch takes the same 566 / 556 / 565 µs.
measured
three cards
Over the PCIe link ↗
pcie.launch
The runtime's response thread polls the device's completion queue, sleeping 50 µs between polls while commands are in flight and 500 µs when none are.
documented
Over the PCIe link ↗
pcie.poll
Chip-wide barrier built from FLB, global atomics and credits: 4,976-4,991 cycles with one minion per shire, 4,998-5,013 with all 1,024 (about 8.3 us); the allreduce tree does it in 2.3 us.
measured
three cards
On-chip communication ↗
sync-chip-barrier
The mesh routes in dimension order, and a request and its reply take opposite orders: a request goes x first, then y, and a reply y first, then x, on the logical map, so a reply retraces its request's route backwards. Measured on 29 September (E56) with sets of streams between shires chosen so that their streams share one directed link under one order and none under the other: 1 KB tensor loads, whose data travel as replies, fell to 0.54-0.77 of their bandwidth alone when they shared a link under y first and held at 1.00 when they shared one under x first; tensor stores, whose data travel as requests, showed the mirror (0.52-0.76 against 1.00). A shared link carried about 92 GB/s. The same on aifoundry1 card 1 (development), aifoundry3 (the frozen validation) and aifoundry2 (the same frozen test, run as a third card on the evening of 29 September), three passes each.
measured
three cards
no published page yet
L104+}

## flow/K/1
FLOW B · BROADCAST
The value sits in hart … what each costs.

 More detail and the sources {+

How one value, 32 B or 1 KB, gets from minion 0 of shire 0 to all 1,024 minions, and what each way costs. The chip offers four: the hardware tree (TensorBroadcast), a relay from shire to shire, one line in memory that every minion loads, and the multicast every kernel launch already makes.

 Leg What happens
the value hart 0's 32 vector registers of 32 bytes: 32 B fills one, 1 KB all of them; only hart 0 issues tensor instructions
tree: mesh TensorBroadcast down the allreduce's tree, levels 9 to 5 between shires: 164–234 cycles a level, up and down
tree: shire levels 4 and 3 through the crossbar, 117 cycles a level; 2 to 0 on the tree edges, 68–71 cycles; in every shire at once
tree, timed with the reduction, 32 B: 444 cycles (0.74 µs) over 32 minions, 1,393 cycles (2.3 µs) over 1,024; 1 KB: 1,354 cycles (2.26 µs) and 3,236–3,244 cycles (5.4 µs)
relay or DRAM a hand-off to the next shire 17.8 pJ per byte, its write and its read (8.9 pJ/B moved), about a thirteenth of a DRAM round trip; every shire reading DRAM 115 pJ/B each, the chip's 76 GB/s shared
one line every minion loads one line from its L3 home: one load 110 + 12 cycles a hop; one request per shire at a time; 15 pJ/B over the mesh
at its home the line's bank: an atomic every 10.00 cycles; 31 requesters, one a shire, left the home's reader at 100%; 22 from one shire hammering it stop the home's loads (0.02%)
the launch one 64-byte message, one ESR broadcast, every hart reads it, one atomic a shire: an empty kernel 103.6–104.1 µs queued on 32 shires, 91.2 / 92.2 / 92.4 on one
compared to all 1,024: the tree 2.3 µs (32 B) or 5.4 µs (1 KB); a chip barrier alone 8.3 µs; a queued launch 103.6–104.1 µs

 Not measured: the tree's broadcast half on its own (it was timed only with the reduction) and the tree's energy (fact bc.half); how long a relay takes to reach every shire (the relay moved 1 MB slabs down a pipeline); every minion loading one line at once (the hot-line runs used atomics); the launch's multicast apart from the rest of a launch, and its energy (fact bc.launch-31).

 The mesh takes a request x first and a reply y first (measured for loads and stores): the reads' requests are drawn x first, and the data they bring back, the relay's hand-offs among them, y first, and the tree's messages as requests, x first. The interrupt that starts a launch is drawn at each shire, not along a route: its path over the mesh is not documented.

 Measured and explained in On-chip communication ↗.

 The facts this flow uses (31): point at one for its source

 Each lane's register file holds 64 × 32-bit entries (32 per thread), so each hart has 32 vector registers of 32 bytes; 8 mask registers of 8 bits.
documented
On-chip communication ↗
minion.vpu-regs
Only hart 0 of a minion may issue tensor instructions; hart 1 may only issue TensorLoadL2Scp, TensorWait and tensor_coop accesses.
documented
Limits of observability ↗
minion.tensor-hart0
TensorBroadcast sends COUNT vector registers of 32 bytes down a fully balanced binary tree: at node height HEIGHT a hart whose mhartid is a multiple of 2^(HEIGHT+2) sends to hart mhartid + 2^(HEIGHT+1), and with FUNCT = MOVE every hart ends with the root's value. N harts take log2 N steps, HEIGHT from log2(N) - 1 down to 0, and each step waits for both of its harts, their vector registers stalled until the data has moved. Hart 0 of minion m is hart 2m, so a broadcast from minion 0 to all 1,024 minions takes ten steps, the first to minion 512, minion 0 of shire 16.
documented
On-chip communication ↗
bc.tensorbroadcast
The allreduce benchmark's tree: at level h, a minion whose ID has bit h as its lowest set bit sends its partial sum to the minion with that bit cleared (TensorReduce), levels 0 to 9, and the result comes back down the same tree (TensorBroadcast). Levels 0-2 join a neighbourhood's 8 minions along the fast network's edges, levels 3-4 its 4 neighbourhoods, levels 5-9 the 32 shires, rooted at minion 0 of shire 0.
documented
On-chip communication ↗
ar.tree
The fast local messaging network links minions within a neighbourhood only along the reduction tree: 0-1, 0-2, 0-4, 2-3, 4-5, 4-6, 6-7.
documented
On-chip communication ↗
neigh.fln-edges
Each allreduce tree level adds about one round trip: 68-71 cycles on the fast network (levels 0-2), 117 through the crossbar (levels 3-4) and 164-234 over the mesh (levels 5-9).
measured
three cards
On-chip communication ↗
sync.tree-levels
Hardware allreduce (TensorReduce + TensorBroadcast) of 32 B over a shire's 32 minions: 444 cycles (0.74 us), 444.06-444.31 on all three cards.
measured
three cards
On-chip communication ↗
sync-allreduce32
Hardware allreduce of 32 B over all 1,024 minions: 1,393 cycles (2.3 us), 1,392.6-1,393.4 on the three cards; an A100 grid.sync() alone is 1.1-1.2 us.
measured
three cards
On-chip communication ↗
sync-allreduce1024
The same hardware allreduce with 1 KB (32 vector registers) instead of 32 B: 1,354 cycles over a shire's 32 minions (1,354.05-1,354.16 in every pass on the three cards, 2.26 µs) and 3,236-3,244 cycles over all 1,024 minions (each card's median over three passes: aifoundry2 3,236.33, aifoundry3 3,243.35, aifoundry1-c1 3,244.27; 5.4 µs at 600 MHz), against 444 and 1,393 cycles for 32 B.
measured
three cards
On-chip communication ↗
bc.allreduce-1kb
The broadcast half of the tree was never timed on its own: nocbench times TensorReduce up the tree and TensorBroadcast back down as one operation, one cycle count around both, so the broadcast is part of the allreduce's 444 cycles over 32 minions and 1,393 over 1,024 (32 B). Neither half's energy was measured: the energy manual's synchronisation table gives none for the tree.
model
On-chip communication ↗
bc.half
Messaging energy, 1 KB TensorSend: 0.69 pJ/B between the two minions of a pair, 2.16 around a neighbourhood, 2.22 around a shire, 12.5-18.3 across the mesh (busy cores included).
measured
three cards
On-chip communication ↗
ts-e-pair
Relay energy per byte moved, each byte counted once when written and once when read: through DRAM 116.2 pJ/B [104.5-135.3], to the next shire, which reads the previous shire's scratchpad, 8.9 [7.6-10.2], in the own scratchpad 4.3 [3.8-5.1]; a hand-off writes every byte once and reads it once, so a byte handed to the next shire costs 17.8 pJ (232 through DRAM).
measured
three cards
Hand it to the next shire: on-chip relay vs DRAM ↗
relay-energy
Handing a slab to the next shire through its scratchpad costs 12.9x, 13.0x and 13.1x less energy per byte than the DRAM round trip (aifoundry2, aifoundry3, aifoundry1-c1): about a thirteenth, the same on every card at 99%.
measured
three cards
Hand it to the next shire: on-chip relay vs DRAM ↗
relay-13x
Relay bandwidth (8 stages, 1,024 minions; bytes read plus bytes written): 47.7 GB/s through DRAM, 592.5 GB/s to the next shire (12.4x), 1487 GB/s in the own scratchpad (aifoundry2 pass means; the other cards within 1.5%).
measured
aifoundry2 pass means (the other cards within 1.5%)
Hand it to the next shire: on-chip relay vs DRAM ↗
relay-bw
DRAM: 114.6 pJ/B [89.0-141.3] above idle, 1 KB tensor loads (L1: 32 B vector loads) by every minion at 600 MHz; per card a2 111.5, a3 105.6, a1c1 126.6.
measured
three cards
The energy manual ↗
e-dram
DRAM streaming: 76 GB/s for the whole chip (0.124 B per minion-cycle), about 64% of the 119 GB/s that 16 x 16-bit channels carry at 3,733 MT/s; about a twentieth of an A100.
measured
aifoundry2, aifoundry3
Ridge points ↗
bw-dram
A line's L3 home shire is PA[10:6]: consecutive 64-byte lines rotate over the 32 compute shires' L3 slices (default 'swizzle0'; the firmware leaves the swizzle register at reset).
measured
three cards
Anatomy of a memory access ↗
l3.home
L3 hit: 110 + 12 cycles per mesh hop between the requesting shire and the line's home shire (fitted 110.5 + 11.99 on three cards); 159-169 cycles (265-282 ns) on average depending on the requesting shire.
measured
three cards
Anatomy of a memory access ↗
l3.latency
Inside a shire, requests to one line are kept in order, and 'Two requests to the mesh will never have the same address outstanding': when every minion of a shire loads one line homed in another shire, the shire has at most one request for it on the mesh at a time. The L2's 8-entry read buffer is there for 'multiple readers of the same cache line', its hits 'serviced once per clock'; L3 reads at the home do not use it.
documented
no published page yet
bc.one-request
L3 (over the mesh): 14.7 pJ/B [7.1-20.5] above idle, 1 KB tensor loads (L1: 32 B vector loads) by every minion at 600 MHz; per card a2 12.3, a3 13.5, a1c1 18.4.
measured
three cards
The energy manual ↗
e-l3
One contended global atomic (amoaddg.w on one line, 1,024 minions): the bank retires one every 10.00 cycles, about 60 M/s for the whole chip; spread over 32 lines, one per shire, 0.31 cycles and 1,919 M/s: 32x.
measured
aifoundry2
One hot line stops a shire ↗
hot-cost
31 minions, one in each other shire, hammering one global atomic homed in shire 0 kept its bank retiring one every 10.00 cycles, while shire 0's one minion reading its own scratchpad kept 100% of its rate alone, in three passes on each of the three cards (the prediction was 1% or less). Whether they would stop a shire whose 32 minions all read was not tested. Each shire's leader polling one counter hung the relay's first barrier (one development run).
measured
three cards
One hot line stops a shire ↗
bc.pollers
The host shire's minions read their own scratchpad while the same number of minions in one other shire hammer one scratchpad word in the host shire: with 21 of each the host keeps 95.6 / 95.7 / 95.6% of its rate alone (aifoundry2 / aifoundry3 / aifoundry1-c1, mean of 3 passes; 95.5-95.7% over every pass), and with 22, 23 or 24 it stops: 0.02% on every card. An uncontended remote atomic takes 216.2 / 216.3 / 216.6 cycles round trip.
measured
three cards
One hot line stops a shire ↗
hot.cliff
A global atomic (amoaddg) is performed at the shire cache that homes the line. One contended line serialises at 10.00 cycles per atomic (about 60 M/s for the chip) and stops the host shire's own memory path; an uncontended remote global atomic round trip is 216 cycles.
measured
aifoundry2, aifoundry3
One hot line stops a shire ↗
mem.global-atomic
ESR broadcast: one request writes the same system register in every shire of a mask (32 bits for the compute shires, 8 for the memory shires): software writes the value to the broadcast data register, then the target register and the masks to a broadcast request register. A shire's IPI_TRIGGER register takes a 64-bit mask of its harts and interrupts each hart whose bit is set; the firmware's broadcast system call writes the first two.
documented
no published page yet
bc.esr-ipi
Every kernel launch is a broadcast. The master shire's firmware copies the 64-byte launch message into a buffer in its own scratchpad and evicts it to the L2, raises the interrupt on all 64 harts of every shire in the kernel's mask with one ESR broadcast, and polls a shire mask beside the buffer: each hart evicts its stale L1 copy and reads the message, and the last of a shire's 64 harts clears that shire's bit with a global atomic AND. The launch goes on once every bit is clear.
documented
no published page yet
bc.launch-multicast
Queued back to back, an empty kernel costs the card 103.6 / 103.7 / 104.1 µs on all 32 shires and 91.2 / 92.2 / 92.4 µs on one (aifoundry2 / aifoundry3 / aifoundry1-c1): the other 31 shires add 12.4 / 11.4 / 11.6 µs (11.4-12.4 µs), the rest the same for one shire or 32. Which part of that is the launch's multicast (the interrupt, every hart reading the message, the shires' acknowledging atomics) and which the kernel's own start and finish was not measured.
model
three cards
Over the PCIe link ↗
bc.launch-31
An empty kernel on all 32 compute shires, launched and waited for: 566 / 556 / 565 µs (556-566 µs) from launch to completion (aifoundry2 / aifoundry3 / aifoundry1-c1); 100 launches queued back to back: 103.6 / 103.7 / 104.1 µs each (103.6-104.1 µs) on 32 shires and 91.2 / 92.2 / 92.4 on one shire. The card's own cost is the queued figure: a lone launch waited for adds 463 / 452 / 461 µs (452-463 µs, each run's difference), most of the runtime's 500 µs idle poll (fact pcie.poll), and a one-shire lone launch takes the same 566 / 556 / 565 µs.
measured
three cards
Over the PCIe link ↗
pcie.launch
The runtime's response thread polls the device's completion queue, sleeping 50 µs between polls while commands are in flight and 500 µs when none are.
documented
Over the PCIe link ↗
pcie.poll
Chip-wide barrier built from FLB, global atomics and credits: 4,976-4,991 cycles with one minion per shire, 4,998-5,013 with all 1,024 (about 8.3 us); the allreduce tree does it in 2.3 us.
measured
three cards
On-chip communication ↗
sync-chip-barrier
The mesh routes in dimension order, and a request and its reply take opposite orders: a request goes x first, then y, and a reply y first, then x, on the logical map, so a reply retraces its request's route backwards. Measured on 29 September (E56) with sets of streams between shires chosen so that their streams share one directed link under one order and none under the other: 1 KB tensor loads, whose data travel as replies, fell to 0.54-0.77 of their bandwidth alone when they shared a link under y first and held at 1.00 when they shared one under x first; tensor stores, whose data travel as requests, showed the mirror (0.52-0.76 against 1.00). A shared link carried about 92 GB/s. The same on aifoundry1 card 1 (development), aifoundry3 (the frozen validation) and aifoundry2 (the same frozen test, run as a third card on the evening of 29 September), three passes each.
measured
three cards
no published page yet
L104+}

## flow/K/2
FLOW B · BROADCAST
TensorBroadcast down the allreduce's tree: … what each costs.

 More detail and the sources {+

How one value, 32 B or 1 KB, gets from minion 0 of shire 0 to all 1,024 minions, and what each way costs. The chip offers four: the hardware tree (TensorBroadcast), a relay from shire to shire, one line in memory that every minion loads, and the multicast every kernel launch already makes.

 Leg What happens
the value hart 0's 32 vector registers of 32 bytes: 32 B fills one, 1 KB all of them; only hart 0 issues tensor instructions
tree: mesh TensorBroadcast down the allreduce's tree, levels 9 to 5 between shires: 164–234 cycles a level, up and down
tree: shire levels 4 and 3 through the crossbar, 117 cycles a level; 2 to 0 on the tree edges, 68–71 cycles; in every shire at once
tree, timed with the reduction, 32 B: 444 cycles (0.74 µs) over 32 minions, 1,393 cycles (2.3 µs) over 1,024; 1 KB: 1,354 cycles (2.26 µs) and 3,236–3,244 cycles (5.4 µs)
relay or DRAM a hand-off to the next shire 17.8 pJ per byte, its write and its read (8.9 pJ/B moved), about a thirteenth of a DRAM round trip; every shire reading DRAM 115 pJ/B each, the chip's 76 GB/s shared
one line every minion loads one line from its L3 home: one load 110 + 12 cycles a hop; one request per shire at a time; 15 pJ/B over the mesh
at its home the line's bank: an atomic every 10.00 cycles; 31 requesters, one a shire, left the home's reader at 100%; 22 from one shire hammering it stop the home's loads (0.02%)
the launch one 64-byte message, one ESR broadcast, every hart reads it, one atomic a shire: an empty kernel 103.6–104.1 µs queued on 32 shires, 91.2 / 92.2 / 92.4 on one
compared to all 1,024: the tree 2.3 µs (32 B) or 5.4 µs (1 KB); a chip barrier alone 8.3 µs; a queued launch 103.6–104.1 µs

 Not measured: the tree's broadcast half on its own (it was timed only with the reduction) and the tree's energy (fact bc.half); how long a relay takes to reach every shire (the relay moved 1 MB slabs down a pipeline); every minion loading one line at once (the hot-line runs used atomics); the launch's multicast apart from the rest of a launch, and its energy (fact bc.launch-31).

 The mesh takes a request x first and a reply y first (measured for loads and stores): the reads' requests are drawn x first, and the data they bring back, the relay's hand-offs among them, y first, and the tree's messages as requests, x first. The interrupt that starts a launch is drawn at each shire, not along a route: its path over the mesh is not documented.

 Measured and explained in On-chip communication ↗.

 The facts this flow uses (31): point at one for its source

 Each lane's register file holds 64 × 32-bit entries (32 per thread), so each hart has 32 vector registers of 32 bytes; 8 mask registers of 8 bits.
documented
On-chip communication ↗
minion.vpu-regs
Only hart 0 of a minion may issue tensor instructions; hart 1 may only issue TensorLoadL2Scp, TensorWait and tensor_coop accesses.
documented
Limits of observability ↗
minion.tensor-hart0
TensorBroadcast sends COUNT vector registers of 32 bytes down a fully balanced binary tree: at node height HEIGHT a hart whose mhartid is a multiple of 2^(HEIGHT+2) sends to hart mhartid + 2^(HEIGHT+1), and with FUNCT = MOVE every hart ends with the root's value. N harts take log2 N steps, HEIGHT from log2(N) - 1 down to 0, and each step waits for both of its harts, their vector registers stalled until the data has moved. Hart 0 of minion m is hart 2m, so a broadcast from minion 0 to all 1,024 minions takes ten steps, the first to minion 512, minion 0 of shire 16.
documented
On-chip communication ↗
bc.tensorbroadcast
The allreduce benchmark's tree: at level h, a minion whose ID has bit h as its lowest set bit sends its partial sum to the minion with that bit cleared (TensorReduce), levels 0 to 9, and the result comes back down the same tree (TensorBroadcast). Levels 0-2 join a neighbourhood's 8 minions along the fast network's edges, levels 3-4 its 4 neighbourhoods, levels 5-9 the 32 shires, rooted at minion 0 of shire 0.
documented
On-chip communication ↗
ar.tree
The fast local messaging network links minions within a neighbourhood only along the reduction tree: 0-1, 0-2, 0-4, 2-3, 4-5, 4-6, 6-7.
documented
On-chip communication ↗
neigh.fln-edges
Each allreduce tree level adds about one round trip: 68-71 cycles on the fast network (levels 0-2), 117 through the crossbar (levels 3-4) and 164-234 over the mesh (levels 5-9).
measured
three cards
On-chip communication ↗
sync.tree-levels
Hardware allreduce (TensorReduce + TensorBroadcast) of 32 B over a shire's 32 minions: 444 cycles (0.74 us), 444.06-444.31 on all three cards.
measured
three cards
On-chip communication ↗
sync-allreduce32
Hardware allreduce of 32 B over all 1,024 minions: 1,393 cycles (2.3 us), 1,392.6-1,393.4 on the three cards; an A100 grid.sync() alone is 1.1-1.2 us.
measured
three cards
On-chip communication ↗
sync-allreduce1024
The same hardware allreduce with 1 KB (32 vector registers) instead of 32 B: 1,354 cycles over a shire's 32 minions (1,354.05-1,354.16 in every pass on the three cards, 2.26 µs) and 3,236-3,244 cycles over all 1,024 minions (each card's median over three passes: aifoundry2 3,236.33, aifoundry3 3,243.35, aifoundry1-c1 3,244.27; 5.4 µs at 600 MHz), against 444 and 1,393 cycles for 32 B.
measured
three cards
On-chip communication ↗
bc.allreduce-1kb
The broadcast half of the tree was never timed on its own: nocbench times TensorReduce up the tree and TensorBroadcast back down as one operation, one cycle count around both, so the broadcast is part of the allreduce's 444 cycles over 32 minions and 1,393 over 1,024 (32 B). Neither half's energy was measured: the energy manual's synchronisation table gives none for the tree.
model
On-chip communication ↗
bc.half
Messaging energy, 1 KB TensorSend: 0.69 pJ/B between the two minions of a pair, 2.16 around a neighbourhood, 2.22 around a shire, 12.5-18.3 across the mesh (busy cores included).
measured
three cards
On-chip communication ↗
ts-e-pair
Relay energy per byte moved, each byte counted once when written and once when read: through DRAM 116.2 pJ/B [104.5-135.3], to the next shire, which reads the previous shire's scratchpad, 8.9 [7.6-10.2], in the own scratchpad 4.3 [3.8-5.1]; a hand-off writes every byte once and reads it once, so a byte handed to the next shire costs 17.8 pJ (232 through DRAM).
measured
three cards
Hand it to the next shire: on-chip relay vs DRAM ↗
relay-energy
Handing a slab to the next shire through its scratchpad costs 12.9x, 13.0x and 13.1x less energy per byte than the DRAM round trip (aifoundry2, aifoundry3, aifoundry1-c1): about a thirteenth, the same on every card at 99%.
measured
three cards
Hand it to the next shire: on-chip relay vs DRAM ↗
relay-13x
Relay bandwidth (8 stages, 1,024 minions; bytes read plus bytes written): 47.7 GB/s through DRAM, 592.5 GB/s to the next shire (12.4x), 1487 GB/s in the own scratchpad (aifoundry2 pass means; the other cards within 1.5%).
measured
aifoundry2 pass means (the other cards within 1.5%)
Hand it to the next shire: on-chip relay vs DRAM ↗
relay-bw
DRAM: 114.6 pJ/B [89.0-141.3] above idle, 1 KB tensor loads (L1: 32 B vector loads) by every minion at 600 MHz; per card a2 111.5, a3 105.6, a1c1 126.6.
measured
three cards
The energy manual ↗
e-dram
DRAM streaming: 76 GB/s for the whole chip (0.124 B per minion-cycle), about 64% of the 119 GB/s that 16 x 16-bit channels carry at 3,733 MT/s; about a twentieth of an A100.
measured
aifoundry2, aifoundry3
Ridge points ↗
bw-dram
A line's L3 home shire is PA[10:6]: consecutive 64-byte lines rotate over the 32 compute shires' L3 slices (default 'swizzle0'; the firmware leaves the swizzle register at reset).
measured
three cards
Anatomy of a memory access ↗
l3.home
L3 hit: 110 + 12 cycles per mesh hop between the requesting shire and the line's home shire (fitted 110.5 + 11.99 on three cards); 159-169 cycles (265-282 ns) on average depending on the requesting shire.
measured
three cards
Anatomy of a memory access ↗
l3.latency
Inside a shire, requests to one line are kept in order, and 'Two requests to the mesh will never have the same address outstanding': when every minion of a shire loads one line homed in another shire, the shire has at most one request for it on the mesh at a time. The L2's 8-entry read buffer is there for 'multiple readers of the same cache line', its hits 'serviced once per clock'; L3 reads at the home do not use it.
documented
no published page yet
bc.one-request
L3 (over the mesh): 14.7 pJ/B [7.1-20.5] above idle, 1 KB tensor loads (L1: 32 B vector loads) by every minion at 600 MHz; per card a2 12.3, a3 13.5, a1c1 18.4.
measured
three cards
The energy manual ↗
e-l3
One contended global atomic (amoaddg.w on one line, 1,024 minions): the bank retires one every 10.00 cycles, about 60 M/s for the whole chip; spread over 32 lines, one per shire, 0.31 cycles and 1,919 M/s: 32x.
measured
aifoundry2
One hot line stops a shire ↗
hot-cost
31 minions, one in each other shire, hammering one global atomic homed in shire 0 kept its bank retiring one every 10.00 cycles, while shire 0's one minion reading its own scratchpad kept 100% of its rate alone, in three passes on each of the three cards (the prediction was 1% or less). Whether they would stop a shire whose 32 minions all read was not tested. Each shire's leader polling one counter hung the relay's first barrier (one development run).
measured
three cards
One hot line stops a shire ↗
bc.pollers
The host shire's minions read their own scratchpad while the same number of minions in one other shire hammer one scratchpad word in the host shire: with 21 of each the host keeps 95.6 / 95.7 / 95.6% of its rate alone (aifoundry2 / aifoundry3 / aifoundry1-c1, mean of 3 passes; 95.5-95.7% over every pass), and with 22, 23 or 24 it stops: 0.02% on every card. An uncontended remote atomic takes 216.2 / 216.3 / 216.6 cycles round trip.
measured
three cards
One hot line stops a shire ↗
hot.cliff
A global atomic (amoaddg) is performed at the shire cache that homes the line. One contended line serialises at 10.00 cycles per atomic (about 60 M/s for the chip) and stops the host shire's own memory path; an uncontended remote global atomic round trip is 216 cycles.
measured
aifoundry2, aifoundry3
One hot line stops a shire ↗
mem.global-atomic
ESR broadcast: one request writes the same system register in every shire of a mask (32 bits for the compute shires, 8 for the memory shires): software writes the value to the broadcast data register, then the target register and the masks to a broadcast request register. A shire's IPI_TRIGGER register takes a 64-bit mask of its harts and interrupts each hart whose bit is set; the firmware's broadcast system call writes the first two.
documented
no published page yet
bc.esr-ipi
Every kernel launch is a broadcast. The master shire's firmware copies the 64-byte launch message into a buffer in its own scratchpad and evicts it to the L2, raises the interrupt on all 64 harts of every shire in the kernel's mask with one ESR broadcast, and polls a shire mask beside the buffer: each hart evicts its stale L1 copy and reads the message, and the last of a shire's 64 harts clears that shire's bit with a global atomic AND. The launch goes on once every bit is clear.
documented
no published page yet
bc.launch-multicast
Queued back to back, an empty kernel costs the card 103.6 / 103.7 / 104.1 µs on all 32 shires and 91.2 / 92.2 / 92.4 µs on one (aifoundry2 / aifoundry3 / aifoundry1-c1): the other 31 shires add 12.4 / 11.4 / 11.6 µs (11.4-12.4 µs), the rest the same for one shire or 32. Which part of that is the launch's multicast (the interrupt, every hart reading the message, the shires' acknowledging atomics) and which the kernel's own start and finish was not measured.
model
three cards
Over the PCIe link ↗
bc.launch-31
An empty kernel on all 32 compute shires, launched and waited for: 566 / 556 / 565 µs (556-566 µs) from launch to completion (aifoundry2 / aifoundry3 / aifoundry1-c1); 100 launches queued back to back: 103.6 / 103.7 / 104.1 µs each (103.6-104.1 µs) on 32 shires and 91.2 / 92.2 / 92.4 on one shire. The card's own cost is the queued figure: a lone launch waited for adds 463 / 452 / 461 µs (452-463 µs, each run's difference), most of the runtime's 500 µs idle poll (fact pcie.poll), and a one-shire lone launch takes the same 566 / 556 / 565 µs.
measured
three cards
Over the PCIe link ↗
pcie.launch
The runtime's response thread polls the device's completion queue, sleeping 50 µs between polls while commands are in flight and 500 µs when none are.
documented
Over the PCIe link ↗
pcie.poll
Chip-wide barrier built from FLB, global atomics and credits: 4,976-4,991 cycles with one minion per shire, 4,998-5,013 with all 1,024 (about 8.3 us); the allreduce tree does it in 2.3 us.
measured
three cards
On-chip communication ↗
sync-chip-barrier
The mesh routes in dimension order, and a request and its reply take opposite orders: a request goes x first, then y, and a reply y first, then x, on the logical map, so a reply retraces its request's route backwards. Measured on 29 September (E56) with sets of streams between shires chosen so that their streams share one directed link under one order and none under the other: 1 KB tensor loads, whose data travel as replies, fell to 0.54-0.77 of their bandwidth alone when they shared a link under y first and held at 1.00 when they shared one under x first; tensor stores, whose data travel as requests, showed the mirror (0.52-0.76 against 1.00). A shared link carried about 92 GB/s. The same on aifoundry1 card 1 (development), aifoundry3 (the frozen validation) and aifoundry2 (the same frozen test, run as a third card on the evening of 29 September), three passes each.
measured
three cards
no published page yet
L104+}

## flow/K/3
FLOW B · BROADCAST
In every shire at once: … what each costs.

 More detail and the sources {+

How one value, 32 B or 1 KB, gets from minion 0 of shire 0 to all 1,024 minions, and what each way costs. The chip offers four: the hardware tree (TensorBroadcast), a relay from shire to shire, one line in memory that every minion loads, and the multicast every kernel launch already makes.

 Leg What happens
the value hart 0's 32 vector registers of 32 bytes: 32 B fills one, 1 KB all of them; only hart 0 issues tensor instructions
tree: mesh TensorBroadcast down the allreduce's tree, levels 9 to 5 between shires: 164–234 cycles a level, up and down
tree: shire levels 4 and 3 through the crossbar, 117 cycles a level; 2 to 0 on the tree edges, 68–71 cycles; in every shire at once
tree, timed with the reduction, 32 B: 444 cycles (0.74 µs) over 32 minions, 1,393 cycles (2.3 µs) over 1,024; 1 KB: 1,354 cycles (2.26 µs) and 3,236–3,244 cycles (5.4 µs)
relay or DRAM a hand-off to the next shire 17.8 pJ per byte, its write and its read (8.9 pJ/B moved), about a thirteenth of a DRAM round trip; every shire reading DRAM 115 pJ/B each, the chip's 76 GB/s shared
one line every minion loads one line from its L3 home: one load 110 + 12 cycles a hop; one request per shire at a time; 15 pJ/B over the mesh
at its home the line's bank: an atomic every 10.00 cycles; 31 requesters, one a shire, left the home's reader at 100%; 22 from one shire hammering it stop the home's loads (0.02%)
the launch one 64-byte message, one ESR broadcast, every hart reads it, one atomic a shire: an empty kernel 103.6–104.1 µs queued on 32 shires, 91.2 / 92.2 / 92.4 on one
compared to all 1,024: the tree 2.3 µs (32 B) or 5.4 µs (1 KB); a chip barrier alone 8.3 µs; a queued launch 103.6–104.1 µs

 Not measured: the tree's broadcast half on its own (it was timed only with the reduction) and the tree's energy (fact bc.half); how long a relay takes to reach every shire (the relay moved 1 MB slabs down a pipeline); every minion loading one line at once (the hot-line runs used atomics); the launch's multicast apart from the rest of a launch, and its energy (fact bc.launch-31).

 The mesh takes a request x first and a reply y first (measured for loads and stores): the reads' requests are drawn x first, and the data they bring back, the relay's hand-offs among them, y first, and the tree's messages as requests, x first. The interrupt that starts a launch is drawn at each shire, not along a route: its path over the mesh is not documented.

 Measured and explained in On-chip communication ↗.

 The facts this flow uses (31): point at one for its source

 Each lane's register file holds 64 × 32-bit entries (32 per thread), so each hart has 32 vector registers of 32 bytes; 8 mask registers of 8 bits.
documented
On-chip communication ↗
minion.vpu-regs
Only hart 0 of a minion may issue tensor instructions; hart 1 may only issue TensorLoadL2Scp, TensorWait and tensor_coop accesses.
documented
Limits of observability ↗
minion.tensor-hart0
TensorBroadcast sends COUNT vector registers of 32 bytes down a fully balanced binary tree: at node height HEIGHT a hart whose mhartid is a multiple of 2^(HEIGHT+2) sends to hart mhartid + 2^(HEIGHT+1), and with FUNCT = MOVE every hart ends with the root's value. N harts take log2 N steps, HEIGHT from log2(N) - 1 down to 0, and each step waits for both of its harts, their vector registers stalled until the data has moved. Hart 0 of minion m is hart 2m, so a broadcast from minion 0 to all 1,024 minions takes ten steps, the first to minion 512, minion 0 of shire 16.
documented
On-chip communication ↗
bc.tensorbroadcast
The allreduce benchmark's tree: at level h, a minion whose ID has bit h as its lowest set bit sends its partial sum to the minion with that bit cleared (TensorReduce), levels 0 to 9, and the result comes back down the same tree (TensorBroadcast). Levels 0-2 join a neighbourhood's 8 minions along the fast network's edges, levels 3-4 its 4 neighbourhoods, levels 5-9 the 32 shires, rooted at minion 0 of shire 0.
documented
On-chip communication ↗
ar.tree
The fast local messaging network links minions within a neighbourhood only along the reduction tree: 0-1, 0-2, 0-4, 2-3, 4-5, 4-6, 6-7.
documented
On-chip communication ↗
neigh.fln-edges
Each allreduce tree level adds about one round trip: 68-71 cycles on the fast network (levels 0-2), 117 through the crossbar (levels 3-4) and 164-234 over the mesh (levels 5-9).
measured
three cards
On-chip communication ↗
sync.tree-levels
Hardware allreduce (TensorReduce + TensorBroadcast) of 32 B over a shire's 32 minions: 444 cycles (0.74 us), 444.06-444.31 on all three cards.
measured
three cards
On-chip communication ↗
sync-allreduce32
Hardware allreduce of 32 B over all 1,024 minions: 1,393 cycles (2.3 us), 1,392.6-1,393.4 on the three cards; an A100 grid.sync() alone is 1.1-1.2 us.
measured
three cards
On-chip communication ↗
sync-allreduce1024
The same hardware allreduce with 1 KB (32 vector registers) instead of 32 B: 1,354 cycles over a shire's 32 minions (1,354.05-1,354.16 in every pass on the three cards, 2.26 µs) and 3,236-3,244 cycles over all 1,024 minions (each card's median over three passes: aifoundry2 3,236.33, aifoundry3 3,243.35, aifoundry1-c1 3,244.27; 5.4 µs at 600 MHz), against 444 and 1,393 cycles for 32 B.
measured
three cards
On-chip communication ↗
bc.allreduce-1kb
The broadcast half of the tree was never timed on its own: nocbench times TensorReduce up the tree and TensorBroadcast back down as one operation, one cycle count around both, so the broadcast is part of the allreduce's 444 cycles over 32 minions and 1,393 over 1,024 (32 B). Neither half's energy was measured: the energy manual's synchronisation table gives none for the tree.
model
On-chip communication ↗
bc.half
Messaging energy, 1 KB TensorSend: 0.69 pJ/B between the two minions of a pair, 2.16 around a neighbourhood, 2.22 around a shire, 12.5-18.3 across the mesh (busy cores included).
measured
three cards
On-chip communication ↗
ts-e-pair
Relay energy per byte moved, each byte counted once when written and once when read: through DRAM 116.2 pJ/B [104.5-135.3], to the next shire, which reads the previous shire's scratchpad, 8.9 [7.6-10.2], in the own scratchpad 4.3 [3.8-5.1]; a hand-off writes every byte once and reads it once, so a byte handed to the next shire costs 17.8 pJ (232 through DRAM).
measured
three cards
Hand it to the next shire: on-chip relay vs DRAM ↗
relay-energy
Handing a slab to the next shire through its scratchpad costs 12.9x, 13.0x and 13.1x less energy per byte than the DRAM round trip (aifoundry2, aifoundry3, aifoundry1-c1): about a thirteenth, the same on every card at 99%.
measured
three cards
Hand it to the next shire: on-chip relay vs DRAM ↗
relay-13x
Relay bandwidth (8 stages, 1,024 minions; bytes read plus bytes written): 47.7 GB/s through DRAM, 592.5 GB/s to the next shire (12.4x), 1487 GB/s in the own scratchpad (aifoundry2 pass means; the other cards within 1.5%).
measured
aifoundry2 pass means (the other cards within 1.5%)
Hand it to the next shire: on-chip relay vs DRAM ↗
relay-bw
DRAM: 114.6 pJ/B [89.0-141.3] above idle, 1 KB tensor loads (L1: 32 B vector loads) by every minion at 600 MHz; per card a2 111.5, a3 105.6, a1c1 126.6.
measured
three cards
The energy manual ↗
e-dram
DRAM streaming: 76 GB/s for the whole chip (0.124 B per minion-cycle), about 64% of the 119 GB/s that 16 x 16-bit channels carry at 3,733 MT/s; about a twentieth of an A100.
measured
aifoundry2, aifoundry3
Ridge points ↗
bw-dram
A line's L3 home shire is PA[10:6]: consecutive 64-byte lines rotate over the 32 compute shires' L3 slices (default 'swizzle0'; the firmware leaves the swizzle register at reset).
measured
three cards
Anatomy of a memory access ↗
l3.home
L3 hit: 110 + 12 cycles per mesh hop between the requesting shire and the line's home shire (fitted 110.5 + 11.99 on three cards); 159-169 cycles (265-282 ns) on average depending on the requesting shire.
measured
three cards
Anatomy of a memory access ↗
l3.latency
Inside a shire, requests to one line are kept in order, and 'Two requests to the mesh will never have the same address outstanding': when every minion of a shire loads one line homed in another shire, the shire has at most one request for it on the mesh at a time. The L2's 8-entry read buffer is there for 'multiple readers of the same cache line', its hits 'serviced once per clock'; L3 reads at the home do not use it.
documented
no published page yet
bc.one-request
L3 (over the mesh): 14.7 pJ/B [7.1-20.5] above idle, 1 KB tensor loads (L1: 32 B vector loads) by every minion at 600 MHz; per card a2 12.3, a3 13.5, a1c1 18.4.
measured
three cards
The energy manual ↗
e-l3
One contended global atomic (amoaddg.w on one line, 1,024 minions): the bank retires one every 10.00 cycles, about 60 M/s for the whole chip; spread over 32 lines, one per shire, 0.31 cycles and 1,919 M/s: 32x.
measured
aifoundry2
One hot line stops a shire ↗
hot-cost
31 minions, one in each other shire, hammering one global atomic homed in shire 0 kept its bank retiring one every 10.00 cycles, while shire 0's one minion reading its own scratchpad kept 100% of its rate alone, in three passes on each of the three cards (the prediction was 1% or less). Whether they would stop a shire whose 32 minions all read was not tested. Each shire's leader polling one counter hung the relay's first barrier (one development run).
measured
three cards
One hot line stops a shire ↗
bc.pollers
The host shire's minions read their own scratchpad while the same number of minions in one other shire hammer one scratchpad word in the host shire: with 21 of each the host keeps 95.6 / 95.7 / 95.6% of its rate alone (aifoundry2 / aifoundry3 / aifoundry1-c1, mean of 3 passes; 95.5-95.7% over every pass), and with 22, 23 or 24 it stops: 0.02% on every card. An uncontended remote atomic takes 216.2 / 216.3 / 216.6 cycles round trip.
measured
three cards
One hot line stops a shire ↗
hot.cliff
A global atomic (amoaddg) is performed at the shire cache that homes the line. One contended line serialises at 10.00 cycles per atomic (about 60 M/s for the chip) and stops the host shire's own memory path; an uncontended remote global atomic round trip is 216 cycles.
measured
aifoundry2, aifoundry3
One hot line stops a shire ↗
mem.global-atomic
ESR broadcast: one request writes the same system register in every shire of a mask (32 bits for the compute shires, 8 for the memory shires): software writes the value to the broadcast data register, then the target register and the masks to a broadcast request register. A shire's IPI_TRIGGER register takes a 64-bit mask of its harts and interrupts each hart whose bit is set; the firmware's broadcast system call writes the first two.
documented
no published page yet
bc.esr-ipi
Every kernel launch is a broadcast. The master shire's firmware copies the 64-byte launch message into a buffer in its own scratchpad and evicts it to the L2, raises the interrupt on all 64 harts of every shire in the kernel's mask with one ESR broadcast, and polls a shire mask beside the buffer: each hart evicts its stale L1 copy and reads the message, and the last of a shire's 64 harts clears that shire's bit with a global atomic AND. The launch goes on once every bit is clear.
documented
no published page yet
bc.launch-multicast
Queued back to back, an empty kernel costs the card 103.6 / 103.7 / 104.1 µs on all 32 shires and 91.2 / 92.2 / 92.4 µs on one (aifoundry2 / aifoundry3 / aifoundry1-c1): the other 31 shires add 12.4 / 11.4 / 11.6 µs (11.4-12.4 µs), the rest the same for one shire or 32. Which part of that is the launch's multicast (the interrupt, every hart reading the message, the shires' acknowledging atomics) and which the kernel's own start and finish was not measured.
model
three cards
Over the PCIe link ↗
bc.launch-31
An empty kernel on all 32 compute shires, launched and waited for: 566 / 556 / 565 µs (556-566 µs) from launch to completion (aifoundry2 / aifoundry3 / aifoundry1-c1); 100 launches queued back to back: 103.6 / 103.7 / 104.1 µs each (103.6-104.1 µs) on 32 shires and 91.2 / 92.2 / 92.4 on one shire. The card's own cost is the queued figure: a lone launch waited for adds 463 / 452 / 461 µs (452-463 µs, each run's difference), most of the runtime's 500 µs idle poll (fact pcie.poll), and a one-shire lone launch takes the same 566 / 556 / 565 µs.
measured
three cards
Over the PCIe link ↗
pcie.launch
The runtime's response thread polls the device's completion queue, sleeping 50 µs between polls while commands are in flight and 500 µs when none are.
documented
Over the PCIe link ↗
pcie.poll
Chip-wide barrier built from FLB, global atomics and credits: 4,976-4,991 cycles with one minion per shire, 4,998-5,013 with all 1,024 (about 8.3 us); the allreduce tree does it in 2.3 us.
measured
three cards
On-chip communication ↗
sync-chip-barrier
The mesh routes in dimension order, and a request and its reply take opposite orders: a request goes x first, then y, and a reply y first, then x, on the logical map, so a reply retraces its request's route backwards. Measured on 29 September (E56) with sets of streams between shires chosen so that their streams share one directed link under one order and none under the other: 1 KB tensor loads, whose data travel as replies, fell to 0.54-0.77 of their bandwidth alone when they shared a link under y first and held at 1.00 when they shared one under x first; tensor stores, whose data travel as requests, showed the mirror (0.52-0.76 against 1.00). A shared link carried about 92 GB/s. The same on aifoundry1 card 1 (development), aifoundry3 (the frozen validation) and aifoundry2 (the same frozen test, run as a third card on the evening of 29 September), three passes each.
measured
three cards
no published page yet
L104+}

## flow/K/4
FLOW B · BROADCAST
Timed with the reduction, on … what each costs.

 More detail and the sources {+

How one value, 32 B or 1 KB, gets from minion 0 of shire 0 to all 1,024 minions, and what each way costs. The chip offers four: the hardware tree (TensorBroadcast), a relay from shire to shire, one line in memory that every minion loads, and the multicast every kernel launch already makes.

 Leg What happens
the value hart 0's 32 vector registers of 32 bytes: 32 B fills one, 1 KB all of them; only hart 0 issues tensor instructions
tree: mesh TensorBroadcast down the allreduce's tree, levels 9 to 5 between shires: 164–234 cycles a level, up and down
tree: shire levels 4 and 3 through the crossbar, 117 cycles a level; 2 to 0 on the tree edges, 68–71 cycles; in every shire at once
tree, timed with the reduction, 32 B: 444 cycles (0.74 µs) over 32 minions, 1,393 cycles (2.3 µs) over 1,024; 1 KB: 1,354 cycles (2.26 µs) and 3,236–3,244 cycles (5.4 µs)
relay or DRAM a hand-off to the next shire 17.8 pJ per byte, its write and its read (8.9 pJ/B moved), about a thirteenth of a DRAM round trip; every shire reading DRAM 115 pJ/B each, the chip's 76 GB/s shared
one line every minion loads one line from its L3 home: one load 110 + 12 cycles a hop; one request per shire at a time; 15 pJ/B over the mesh
at its home the line's bank: an atomic every 10.00 cycles; 31 requesters, one a shire, left the home's reader at 100%; 22 from one shire hammering it stop the home's loads (0.02%)
the launch one 64-byte message, one ESR broadcast, every hart reads it, one atomic a shire: an empty kernel 103.6–104.1 µs queued on 32 shires, 91.2 / 92.2 / 92.4 on one
compared to all 1,024: the tree 2.3 µs (32 B) or 5.4 µs (1 KB); a chip barrier alone 8.3 µs; a queued launch 103.6–104.1 µs

 Not measured: the tree's broadcast half on its own (it was timed only with the reduction) and the tree's energy (fact bc.half); how long a relay takes to reach every shire (the relay moved 1 MB slabs down a pipeline); every minion loading one line at once (the hot-line runs used atomics); the launch's multicast apart from the rest of a launch, and its energy (fact bc.launch-31).

 The mesh takes a request x first and a reply y first (measured for loads and stores): the reads' requests are drawn x first, and the data they bring back, the relay's hand-offs among them, y first, and the tree's messages as requests, x first. The interrupt that starts a launch is drawn at each shire, not along a route: its path over the mesh is not documented.

 Measured and explained in On-chip communication ↗.

 The facts this flow uses (31): point at one for its source

 Each lane's register file holds 64 × 32-bit entries (32 per thread), so each hart has 32 vector registers of 32 bytes; 8 mask registers of 8 bits.
documented
On-chip communication ↗
minion.vpu-regs
Only hart 0 of a minion may issue tensor instructions; hart 1 may only issue TensorLoadL2Scp, TensorWait and tensor_coop accesses.
documented
Limits of observability ↗
minion.tensor-hart0
TensorBroadcast sends COUNT vector registers of 32 bytes down a fully balanced binary tree: at node height HEIGHT a hart whose mhartid is a multiple of 2^(HEIGHT+2) sends to hart mhartid + 2^(HEIGHT+1), and with FUNCT = MOVE every hart ends with the root's value. N harts take log2 N steps, HEIGHT from log2(N) - 1 down to 0, and each step waits for both of its harts, their vector registers stalled until the data has moved. Hart 0 of minion m is hart 2m, so a broadcast from minion 0 to all 1,024 minions takes ten steps, the first to minion 512, minion 0 of shire 16.
documented
On-chip communication ↗
bc.tensorbroadcast
The allreduce benchmark's tree: at level h, a minion whose ID has bit h as its lowest set bit sends its partial sum to the minion with that bit cleared (TensorReduce), levels 0 to 9, and the result comes back down the same tree (TensorBroadcast). Levels 0-2 join a neighbourhood's 8 minions along the fast network's edges, levels 3-4 its 4 neighbourhoods, levels 5-9 the 32 shires, rooted at minion 0 of shire 0.
documented
On-chip communication ↗
ar.tree
The fast local messaging network links minions within a neighbourhood only along the reduction tree: 0-1, 0-2, 0-4, 2-3, 4-5, 4-6, 6-7.
documented
On-chip communication ↗
neigh.fln-edges
Each allreduce tree level adds about one round trip: 68-71 cycles on the fast network (levels 0-2), 117 through the crossbar (levels 3-4) and 164-234 over the mesh (levels 5-9).
measured
three cards
On-chip communication ↗
sync.tree-levels
Hardware allreduce (TensorReduce + TensorBroadcast) of 32 B over a shire's 32 minions: 444 cycles (0.74 us), 444.06-444.31 on all three cards.
measured
three cards
On-chip communication ↗
sync-allreduce32
Hardware allreduce of 32 B over all 1,024 minions: 1,393 cycles (2.3 us), 1,392.6-1,393.4 on the three cards; an A100 grid.sync() alone is 1.1-1.2 us.
measured
three cards
On-chip communication ↗
sync-allreduce1024
The same hardware allreduce with 1 KB (32 vector registers) instead of 32 B: 1,354 cycles over a shire's 32 minions (1,354.05-1,354.16 in every pass on the three cards, 2.26 µs) and 3,236-3,244 cycles over all 1,024 minions (each card's median over three passes: aifoundry2 3,236.33, aifoundry3 3,243.35, aifoundry1-c1 3,244.27; 5.4 µs at 600 MHz), against 444 and 1,393 cycles for 32 B.
measured
three cards
On-chip communication ↗
bc.allreduce-1kb
The broadcast half of the tree was never timed on its own: nocbench times TensorReduce up the tree and TensorBroadcast back down as one operation, one cycle count around both, so the broadcast is part of the allreduce's 444 cycles over 32 minions and 1,393 over 1,024 (32 B). Neither half's energy was measured: the energy manual's synchronisation table gives none for the tree.
model
On-chip communication ↗
bc.half
Messaging energy, 1 KB TensorSend: 0.69 pJ/B between the two minions of a pair, 2.16 around a neighbourhood, 2.22 around a shire, 12.5-18.3 across the mesh (busy cores included).
measured
three cards
On-chip communication ↗
ts-e-pair
Relay energy per byte moved, each byte counted once when written and once when read: through DRAM 116.2 pJ/B [104.5-135.3], to the next shire, which reads the previous shire's scratchpad, 8.9 [7.6-10.2], in the own scratchpad 4.3 [3.8-5.1]; a hand-off writes every byte once and reads it once, so a byte handed to the next shire costs 17.8 pJ (232 through DRAM).
measured
three cards
Hand it to the next shire: on-chip relay vs DRAM ↗
relay-energy
Handing a slab to the next shire through its scratchpad costs 12.9x, 13.0x and 13.1x less energy per byte than the DRAM round trip (aifoundry2, aifoundry3, aifoundry1-c1): about a thirteenth, the same on every card at 99%.
measured
three cards
Hand it to the next shire: on-chip relay vs DRAM ↗
relay-13x
Relay bandwidth (8 stages, 1,024 minions; bytes read plus bytes written): 47.7 GB/s through DRAM, 592.5 GB/s to the next shire (12.4x), 1487 GB/s in the own scratchpad (aifoundry2 pass means; the other cards within 1.5%).
measured
aifoundry2 pass means (the other cards within 1.5%)
Hand it to the next shire: on-chip relay vs DRAM ↗
relay-bw
DRAM: 114.6 pJ/B [89.0-141.3] above idle, 1 KB tensor loads (L1: 32 B vector loads) by every minion at 600 MHz; per card a2 111.5, a3 105.6, a1c1 126.6.
measured
three cards
The energy manual ↗
e-dram
DRAM streaming: 76 GB/s for the whole chip (0.124 B per minion-cycle), about 64% of the 119 GB/s that 16 x 16-bit channels carry at 3,733 MT/s; about a twentieth of an A100.
measured
aifoundry2, aifoundry3
Ridge points ↗
bw-dram
A line's L3 home shire is PA[10:6]: consecutive 64-byte lines rotate over the 32 compute shires' L3 slices (default 'swizzle0'; the firmware leaves the swizzle register at reset).
measured
three cards
Anatomy of a memory access ↗
l3.home
L3 hit: 110 + 12 cycles per mesh hop between the requesting shire and the line's home shire (fitted 110.5 + 11.99 on three cards); 159-169 cycles (265-282 ns) on average depending on the requesting shire.
measured
three cards
Anatomy of a memory access ↗
l3.latency
Inside a shire, requests to one line are kept in order, and 'Two requests to the mesh will never have the same address outstanding': when every minion of a shire loads one line homed in another shire, the shire has at most one request for it on the mesh at a time. The L2's 8-entry read buffer is there for 'multiple readers of the same cache line', its hits 'serviced once per clock'; L3 reads at the home do not use it.
documented
no published page yet
bc.one-request
L3 (over the mesh): 14.7 pJ/B [7.1-20.5] above idle, 1 KB tensor loads (L1: 32 B vector loads) by every minion at 600 MHz; per card a2 12.3, a3 13.5, a1c1 18.4.
measured
three cards
The energy manual ↗
e-l3
One contended global atomic (amoaddg.w on one line, 1,024 minions): the bank retires one every 10.00 cycles, about 60 M/s for the whole chip; spread over 32 lines, one per shire, 0.31 cycles and 1,919 M/s: 32x.
measured
aifoundry2
One hot line stops a shire ↗
hot-cost
31 minions, one in each other shire, hammering one global atomic homed in shire 0 kept its bank retiring one every 10.00 cycles, while shire 0's one minion reading its own scratchpad kept 100% of its rate alone, in three passes on each of the three cards (the prediction was 1% or less). Whether they would stop a shire whose 32 minions all read was not tested. Each shire's leader polling one counter hung the relay's first barrier (one development run).
measured
three cards
One hot line stops a shire ↗
bc.pollers
The host shire's minions read their own scratchpad while the same number of minions in one other shire hammer one scratchpad word in the host shire: with 21 of each the host keeps 95.6 / 95.7 / 95.6% of its rate alone (aifoundry2 / aifoundry3 / aifoundry1-c1, mean of 3 passes; 95.5-95.7% over every pass), and with 22, 23 or 24 it stops: 0.02% on every card. An uncontended remote atomic takes 216.2 / 216.3 / 216.6 cycles round trip.
measured
three cards
One hot line stops a shire ↗
hot.cliff
A global atomic (amoaddg) is performed at the shire cache that homes the line. One contended line serialises at 10.00 cycles per atomic (about 60 M/s for the chip) and stops the host shire's own memory path; an uncontended remote global atomic round trip is 216 cycles.
measured
aifoundry2, aifoundry3
One hot line stops a shire ↗
mem.global-atomic
ESR broadcast: one request writes the same system register in every shire of a mask (32 bits for the compute shires, 8 for the memory shires): software writes the value to the broadcast data register, then the target register and the masks to a broadcast request register. A shire's IPI_TRIGGER register takes a 64-bit mask of its harts and interrupts each hart whose bit is set; the firmware's broadcast system call writes the first two.
documented
no published page yet
bc.esr-ipi
Every kernel launch is a broadcast. The master shire's firmware copies the 64-byte launch message into a buffer in its own scratchpad and evicts it to the L2, raises the interrupt on all 64 harts of every shire in the kernel's mask with one ESR broadcast, and polls a shire mask beside the buffer: each hart evicts its stale L1 copy and reads the message, and the last of a shire's 64 harts clears that shire's bit with a global atomic AND. The launch goes on once every bit is clear.
documented
no published page yet
bc.launch-multicast
Queued back to back, an empty kernel costs the card 103.6 / 103.7 / 104.1 µs on all 32 shires and 91.2 / 92.2 / 92.4 µs on one (aifoundry2 / aifoundry3 / aifoundry1-c1): the other 31 shires add 12.4 / 11.4 / 11.6 µs (11.4-12.4 µs), the rest the same for one shire or 32. Which part of that is the launch's multicast (the interrupt, every hart reading the message, the shires' acknowledging atomics) and which the kernel's own start and finish was not measured.
model
three cards
Over the PCIe link ↗
bc.launch-31
An empty kernel on all 32 compute shires, launched and waited for: 566 / 556 / 565 µs (556-566 µs) from launch to completion (aifoundry2 / aifoundry3 / aifoundry1-c1); 100 launches queued back to back: 103.6 / 103.7 / 104.1 µs each (103.6-104.1 µs) on 32 shires and 91.2 / 92.2 / 92.4 on one shire. The card's own cost is the queued figure: a lone launch waited for adds 463 / 452 / 461 µs (452-463 µs, each run's difference), most of the runtime's 500 µs idle poll (fact pcie.poll), and a one-shire lone launch takes the same 566 / 556 / 565 µs.
measured
three cards
Over the PCIe link ↗
pcie.launch
The runtime's response thread polls the device's completion queue, sleeping 50 µs between polls while commands are in flight and 500 µs when none are.
documented
Over the PCIe link ↗
pcie.poll
Chip-wide barrier built from FLB, global atomics and credits: 4,976-4,991 cycles with one minion per shire, 4,998-5,013 with all 1,024 (about 8.3 us); the allreduce tree does it in 2.3 us.
measured
three cards
On-chip communication ↗
sync-chip-barrier
The mesh routes in dimension order, and a request and its reply take opposite orders: a request goes x first, then y, and a reply y first, then x, on the logical map, so a reply retraces its request's route backwards. Measured on 29 September (E56) with sets of streams between shires chosen so that their streams share one directed link under one order and none under the other: 1 KB tensor loads, whose data travel as replies, fell to 0.54-0.77 of their bandwidth alone when they shared a link under y first and held at 1.00 when they shared one under x first; tensor stores, whose data travel as requests, showed the mirror (0.52-0.76 against 1.00). A shared link carried about 92 GB/s. The same on aifoundry1 card 1 (development), aifoundry3 (the frozen validation) and aifoundry2 (the same frozen test, run as a third card on the evening of 29 September), three passes each.
measured
three cards
no published page yet
L104+}

## flow/K/5
FLOW B · BROADCAST
A buffer in memory, handed shire to shire: each hand-off costs [-8.9 pJ/B.-] {+17.8 pJ per byte, its write and its read (8.9 pJ/B moved).+} If every shire reads its own copy from DRAM instead, … what each costs.

 More detail and the sources {+

How one value, 32 B or 1 KB, gets from minion 0 of shire 0 to all 1,024 minions, and what each way costs. The chip offers four: the hardware tree (TensorBroadcast), a relay from shire to shire, one line in memory that every minion loads, and the multicast every kernel launch already makes.

 Leg What happens
the value hart 0's 32 vector registers of 32 bytes: 32 B fills one, 1 KB all of them; only hart 0 issues tensor instructions
tree: mesh TensorBroadcast down the allreduce's tree, levels 9 to 5 between shires: 164–234 cycles a level, up and down
tree: shire levels 4 and 3 through the crossbar, 117 cycles a level; 2 to 0 on the tree edges, 68–71 cycles; in every shire at once
tree, timed with the reduction, 32 B: 444 cycles (0.74 µs) over 32 minions, 1,393 cycles (2.3 µs) over 1,024; 1 KB: 1,354 cycles (2.26 µs) and 3,236–3,244 cycles (5.4 µs)
relay or DRAM a hand-off to the next shire 17.8 pJ per byte, its write and its read (8.9 pJ/B moved), about a thirteenth of a DRAM round trip; every shire reading DRAM 115 pJ/B each, the chip's 76 GB/s shared
one line every minion loads one line from its L3 home: one load 110 + 12 cycles a hop; one request per shire at a time; 15 pJ/B over the mesh
at its home the line's bank: an atomic every 10.00 cycles; 31 requesters, one a shire, left the home's reader at 100%; 22 from one shire hammering it stop the home's loads (0.02%)
the launch one 64-byte message, one ESR broadcast, every hart reads it, one atomic a shire: an empty kernel 103.6–104.1 µs queued on 32 shires, 91.2 / 92.2 / 92.4 on one
compared to all 1,024: the tree 2.3 µs (32 B) or 5.4 µs (1 KB); a chip barrier alone 8.3 µs; a queued launch 103.6–104.1 µs

 Not measured: the tree's broadcast half on its own (it was timed only with the reduction) and the tree's energy (fact bc.half); how long a relay takes to reach every shire (the relay moved 1 MB slabs down a pipeline); every minion loading one line at once (the hot-line runs used atomics); the launch's multicast apart from the rest of a launch, and its energy (fact bc.launch-31).

 The mesh takes a request x first and a reply y first (measured for loads and stores): the reads' requests are drawn x first, and the data they bring back, the relay's hand-offs among them, y first, and the tree's messages as requests, x first. The interrupt that starts a launch is drawn at each shire, not along a route: its path over the mesh is not documented.

 Measured and explained in On-chip communication ↗.

 The facts this flow uses (31): point at one for its source

 Each lane's register file holds 64 × 32-bit entries (32 per thread), so each hart has 32 vector registers of 32 bytes; 8 mask registers of 8 bits.
documented
On-chip communication ↗
minion.vpu-regs
Only hart 0 of a minion may issue tensor instructions; hart 1 may only issue TensorLoadL2Scp, TensorWait and tensor_coop accesses.
documented
Limits of observability ↗
minion.tensor-hart0
TensorBroadcast sends COUNT vector registers of 32 bytes down a fully balanced binary tree: at node height HEIGHT a hart whose mhartid is a multiple of 2^(HEIGHT+2) sends to hart mhartid + 2^(HEIGHT+1), and with FUNCT = MOVE every hart ends with the root's value. N harts take log2 N steps, HEIGHT from log2(N) - 1 down to 0, and each step waits for both of its harts, their vector registers stalled until the data has moved. Hart 0 of minion m is hart 2m, so a broadcast from minion 0 to all 1,024 minions takes ten steps, the first to minion 512, minion 0 of shire 16.
documented
On-chip communication ↗
bc.tensorbroadcast
The allreduce benchmark's tree: at level h, a minion whose ID has bit h as its lowest set bit sends its partial sum to the minion with that bit cleared (TensorReduce), levels 0 to 9, and the result comes back down the same tree (TensorBroadcast). Levels 0-2 join a neighbourhood's 8 minions along the fast network's edges, levels 3-4 its 4 neighbourhoods, levels 5-9 the 32 shires, rooted at minion 0 of shire 0.
documented
On-chip communication ↗
ar.tree
The fast local messaging network links minions within a neighbourhood only along the reduction tree: 0-1, 0-2, 0-4, 2-3, 4-5, 4-6, 6-7.
documented
On-chip communication ↗
neigh.fln-edges
Each allreduce tree level adds about one round trip: 68-71 cycles on the fast network (levels 0-2), 117 through the crossbar (levels 3-4) and 164-234 over the mesh (levels 5-9).
measured
three cards
On-chip communication ↗
sync.tree-levels
Hardware allreduce (TensorReduce + TensorBroadcast) of 32 B over a shire's 32 minions: 444 cycles (0.74 us), 444.06-444.31 on all three cards.
measured
three cards
On-chip communication ↗
sync-allreduce32
Hardware allreduce of 32 B over all 1,024 minions: 1,393 cycles (2.3 us), 1,392.6-1,393.4 on the three cards; an A100 grid.sync() alone is 1.1-1.2 us.
measured
three cards
On-chip communication ↗
sync-allreduce1024
The same hardware allreduce with 1 KB (32 vector registers) instead of 32 B: 1,354 cycles over a shire's 32 minions (1,354.05-1,354.16 in every pass on the three cards, 2.26 µs) and 3,236-3,244 cycles over all 1,024 minions (each card's median over three passes: aifoundry2 3,236.33, aifoundry3 3,243.35, aifoundry1-c1 3,244.27; 5.4 µs at 600 MHz), against 444 and 1,393 cycles for 32 B.
measured
three cards
On-chip communication ↗
bc.allreduce-1kb
The broadcast half of the tree was never timed on its own: nocbench times TensorReduce up the tree and TensorBroadcast back down as one operation, one cycle count around both, so the broadcast is part of the allreduce's 444 cycles over 32 minions and 1,393 over 1,024 (32 B). Neither half's energy was measured: the energy manual's synchronisation table gives none for the tree.
model
On-chip communication ↗
bc.half
Messaging energy, 1 KB TensorSend: 0.69 pJ/B between the two minions of a pair, 2.16 around a neighbourhood, 2.22 around a shire, 12.5-18.3 across the mesh (busy cores included).
measured
three cards
On-chip communication ↗
ts-e-pair
Relay energy per byte moved, each byte counted once when written and once when read: through DRAM 116.2 pJ/B [104.5-135.3], to the next shire, which reads the previous shire's scratchpad, 8.9 [7.6-10.2], in the own scratchpad 4.3 [3.8-5.1]; a hand-off writes every byte once and reads it once, so a byte handed to the next shire costs 17.8 pJ (232 through DRAM).
measured
three cards
Hand it to the next shire: on-chip relay vs DRAM ↗
relay-energy
Handing a slab to the next shire through its scratchpad costs 12.9x, 13.0x and 13.1x less energy per byte than the DRAM round trip (aifoundry2, aifoundry3, aifoundry1-c1): about a thirteenth, the same on every card at 99%.
measured
three cards
Hand it to the next shire: on-chip relay vs DRAM ↗
relay-13x
Relay bandwidth (8 stages, 1,024 minions; bytes read plus bytes written): 47.7 GB/s through DRAM, 592.5 GB/s to the next shire (12.4x), 1487 GB/s in the own scratchpad (aifoundry2 pass means; the other cards within 1.5%).
measured
aifoundry2 pass means (the other cards within 1.5%)
Hand it to the next shire: on-chip relay vs DRAM ↗
relay-bw
DRAM: 114.6 pJ/B [89.0-141.3] above idle, 1 KB tensor loads (L1: 32 B vector loads) by every minion at 600 MHz; per card a2 111.5, a3 105.6, a1c1 126.6.
measured
three cards
The energy manual ↗
e-dram
DRAM streaming: 76 GB/s for the whole chip (0.124 B per minion-cycle), about 64% of the 119 GB/s that 16 x 16-bit channels carry at 3,733 MT/s; about a twentieth of an A100.
measured
aifoundry2, aifoundry3
Ridge points ↗
bw-dram
A line's L3 home shire is PA[10:6]: consecutive 64-byte lines rotate over the 32 compute shires' L3 slices (default 'swizzle0'; the firmware leaves the swizzle register at reset).
measured
three cards
Anatomy of a memory access ↗
l3.home
L3 hit: 110 + 12 cycles per mesh hop between the requesting shire and the line's home shire (fitted 110.5 + 11.99 on three cards); 159-169 cycles (265-282 ns) on average depending on the requesting shire.
measured
three cards
Anatomy of a memory access ↗
l3.latency
Inside a shire, requests to one line are kept in order, and 'Two requests to the mesh will never have the same address outstanding': when every minion of a shire loads one line homed in another shire, the shire has at most one request for it on the mesh at a time. The L2's 8-entry read buffer is there for 'multiple readers of the same cache line', its hits 'serviced once per clock'; L3 reads at the home do not use it.
documented
no published page yet
bc.one-request
L3 (over the mesh): 14.7 pJ/B [7.1-20.5] above idle, 1 KB tensor loads (L1: 32 B vector loads) by every minion at 600 MHz; per card a2 12.3, a3 13.5, a1c1 18.4.
measured
three cards
The energy manual ↗
e-l3
One contended global atomic (amoaddg.w on one line, 1,024 minions): the bank retires one every 10.00 cycles, about 60 M/s for the whole chip; spread over 32 lines, one per shire, 0.31 cycles and 1,919 M/s: 32x.
measured
aifoundry2
One hot line stops a shire ↗
hot-cost
31 minions, one in each other shire, hammering one global atomic homed in shire 0 kept its bank retiring one every 10.00 cycles, while shire 0's one minion reading its own scratchpad kept 100% of its rate alone, in three passes on each of the three cards (the prediction was 1% or less). Whether they would stop a shire whose 32 minions all read was not tested. Each shire's leader polling one counter hung the relay's first barrier (one development run).
measured
three cards
One hot line stops a shire ↗
bc.pollers
The host shire's minions read their own scratchpad while the same number of minions in one other shire hammer one scratchpad word in the host shire: with 21 of each the host keeps 95.6 / 95.7 / 95.6% of its rate alone (aifoundry2 / aifoundry3 / aifoundry1-c1, mean of 3 passes; 95.5-95.7% over every pass), and with 22, 23 or 24 it stops: 0.02% on every card. An uncontended remote atomic takes 216.2 / 216.3 / 216.6 cycles round trip.
measured
three cards
One hot line stops a shire ↗
hot.cliff
A global atomic (amoaddg) is performed at the shire cache that homes the line. One contended line serialises at 10.00 cycles per atomic (about 60 M/s for the chip) and stops the host shire's own memory path; an uncontended remote global atomic round trip is 216 cycles.
measured
aifoundry2, aifoundry3
One hot line stops a shire ↗
mem.global-atomic
ESR broadcast: one request writes the same system register in every shire of a mask (32 bits for the compute shires, 8 for the memory shires): software writes the value to the broadcast data register, then the target register and the masks to a broadcast request register. A shire's IPI_TRIGGER register takes a 64-bit mask of its harts and interrupts each hart whose bit is set; the firmware's broadcast system call writes the first two.
documented
no published page yet
bc.esr-ipi
Every kernel launch is a broadcast. The master shire's firmware copies the 64-byte launch message into a buffer in its own scratchpad and evicts it to the L2, raises the interrupt on all 64 harts of every shire in the kernel's mask with one ESR broadcast, and polls a shire mask beside the buffer: each hart evicts its stale L1 copy and reads the message, and the last of a shire's 64 harts clears that shire's bit with a global atomic AND. The launch goes on once every bit is clear.
documented
no published page yet
bc.launch-multicast
Queued back to back, an empty kernel costs the card 103.6 / 103.7 / 104.1 µs on all 32 shires and 91.2 / 92.2 / 92.4 µs on one (aifoundry2 / aifoundry3 / aifoundry1-c1): the other 31 shires add 12.4 / 11.4 / 11.6 µs (11.4-12.4 µs), the rest the same for one shire or 32. Which part of that is the launch's multicast (the interrupt, every hart reading the message, the shires' acknowledging atomics) and which the kernel's own start and finish was not measured.
model
three cards
Over the PCIe link ↗
bc.launch-31
An empty kernel on all 32 compute shires, launched and waited for: 566 / 556 / 565 µs (556-566 µs) from launch to completion (aifoundry2 / aifoundry3 / aifoundry1-c1); 100 launches queued back to back: 103.6 / 103.7 / 104.1 µs each (103.6-104.1 µs) on 32 shires and 91.2 / 92.2 / 92.4 on one shire. The card's own cost is the queued figure: a lone launch waited for adds 463 / 452 / 461 µs (452-463 µs, each run's difference), most of the runtime's 500 µs idle poll (fact pcie.poll), and a one-shire lone launch takes the same 566 / 556 / 565 µs.
measured
three cards
Over the PCIe link ↗
pcie.launch
The runtime's response thread polls the device's completion queue, sleeping 50 µs between polls while commands are in flight and 500 µs when none are.
documented
Over the PCIe link ↗
pcie.poll
Chip-wide barrier built from FLB, global atomics and credits: 4,976-4,991 cycles with one minion per shire, 4,998-5,013 with all 1,024 (about 8.3 us); the allreduce tree does it in 2.3 us.
measured
three cards
On-chip communication ↗
sync-chip-barrier
The mesh routes in dimension order, and a request and its reply take opposite orders: a request goes x first, then y, and a reply y first, then x, on the logical map, so a reply retraces its request's route backwards. Measured on 29 September (E56) with sets of streams between shires chosen so that their streams share one directed link under one order and none under the other: 1 KB tensor loads, whose data travel as replies, fell to 0.54-0.77 of their bandwidth alone when they shared a link under y first and held at 1.00 when they shared one under x first; tensor stores, whose data travel as requests, showed the mirror (0.52-0.76 against 1.00). A shared link carried about 92 GB/s. The same on aifoundry1 card 1 (development), aifoundry3 (the frozen validation) and aifoundry2 (the same frozen test, run as a third card on the evening of 29 September), three passes each.
measured
three cards
no published page yet
L104+}

## flow/K/6
FLOW B · BROADCAST
One line that every minion … what each costs.

 More detail and the sources {+

How one value, 32 B or 1 KB, gets from minion 0 of shire 0 to all 1,024 minions, and what each way costs. The chip offers four: the hardware tree (TensorBroadcast), a relay from shire to shire, one line in memory that every minion loads, and the multicast every kernel launch already makes.

 Leg What happens
the value hart 0's 32 vector registers of 32 bytes: 32 B fills one, 1 KB all of them; only hart 0 issues tensor instructions
tree: mesh TensorBroadcast down the allreduce's tree, levels 9 to 5 between shires: 164–234 cycles a level, up and down
tree: shire levels 4 and 3 through the crossbar, 117 cycles a level; 2 to 0 on the tree edges, 68–71 cycles; in every shire at once
tree, timed with the reduction, 32 B: 444 cycles (0.74 µs) over 32 minions, 1,393 cycles (2.3 µs) over 1,024; 1 KB: 1,354 cycles (2.26 µs) and 3,236–3,244 cycles (5.4 µs)
relay or DRAM a hand-off to the next shire 17.8 pJ per byte, its write and its read (8.9 pJ/B moved), about a thirteenth of a DRAM round trip; every shire reading DRAM 115 pJ/B each, the chip's 76 GB/s shared
one line every minion loads one line from its L3 home: one load 110 + 12 cycles a hop; one request per shire at a time; 15 pJ/B over the mesh
at its home the line's bank: an atomic every 10.00 cycles; 31 requesters, one a shire, left the home's reader at 100%; 22 from one shire hammering it stop the home's loads (0.02%)
the launch one 64-byte message, one ESR broadcast, every hart reads it, one atomic a shire: an empty kernel 103.6–104.1 µs queued on 32 shires, 91.2 / 92.2 / 92.4 on one
compared to all 1,024: the tree 2.3 µs (32 B) or 5.4 µs (1 KB); a chip barrier alone 8.3 µs; a queued launch 103.6–104.1 µs

 Not measured: the tree's broadcast half on its own (it was timed only with the reduction) and the tree's energy (fact bc.half); how long a relay takes to reach every shire (the relay moved 1 MB slabs down a pipeline); every minion loading one line at once (the hot-line runs used atomics); the launch's multicast apart from the rest of a launch, and its energy (fact bc.launch-31).

 The mesh takes a request x first and a reply y first (measured for loads and stores): the reads' requests are drawn x first, and the data they bring back, the relay's hand-offs among them, y first, and the tree's messages as requests, x first. The interrupt that starts a launch is drawn at each shire, not along a route: its path over the mesh is not documented.

 Measured and explained in On-chip communication ↗.

 The facts this flow uses (31): point at one for its source

 Each lane's register file holds 64 × 32-bit entries (32 per thread), so each hart has 32 vector registers of 32 bytes; 8 mask registers of 8 bits.
documented
On-chip communication ↗
minion.vpu-regs
Only hart 0 of a minion may issue tensor instructions; hart 1 may only issue TensorLoadL2Scp, TensorWait and tensor_coop accesses.
documented
Limits of observability ↗
minion.tensor-hart0
TensorBroadcast sends COUNT vector registers of 32 bytes down a fully balanced binary tree: at node height HEIGHT a hart whose mhartid is a multiple of 2^(HEIGHT+2) sends to hart mhartid + 2^(HEIGHT+1), and with FUNCT = MOVE every hart ends with the root's value. N harts take log2 N steps, HEIGHT from log2(N) - 1 down to 0, and each step waits for both of its harts, their vector registers stalled until the data has moved. Hart 0 of minion m is hart 2m, so a broadcast from minion 0 to all 1,024 minions takes ten steps, the first to minion 512, minion 0 of shire 16.
documented
On-chip communication ↗
bc.tensorbroadcast
The allreduce benchmark's tree: at level h, a minion whose ID has bit h as its lowest set bit sends its partial sum to the minion with that bit cleared (TensorReduce), levels 0 to 9, and the result comes back down the same tree (TensorBroadcast). Levels 0-2 join a neighbourhood's 8 minions along the fast network's edges, levels 3-4 its 4 neighbourhoods, levels 5-9 the 32 shires, rooted at minion 0 of shire 0.
documented
On-chip communication ↗
ar.tree
The fast local messaging network links minions within a neighbourhood only along the reduction tree: 0-1, 0-2, 0-4, 2-3, 4-5, 4-6, 6-7.
documented
On-chip communication ↗
neigh.fln-edges
Each allreduce tree level adds about one round trip: 68-71 cycles on the fast network (levels 0-2), 117 through the crossbar (levels 3-4) and 164-234 over the mesh (levels 5-9).
measured
three cards
On-chip communication ↗
sync.tree-levels
Hardware allreduce (TensorReduce + TensorBroadcast) of 32 B over a shire's 32 minions: 444 cycles (0.74 us), 444.06-444.31 on all three cards.
measured
three cards
On-chip communication ↗
sync-allreduce32
Hardware allreduce of 32 B over all 1,024 minions: 1,393 cycles (2.3 us), 1,392.6-1,393.4 on the three cards; an A100 grid.sync() alone is 1.1-1.2 us.
measured
three cards
On-chip communication ↗
sync-allreduce1024
The same hardware allreduce with 1 KB (32 vector registers) instead of 32 B: 1,354 cycles over a shire's 32 minions (1,354.05-1,354.16 in every pass on the three cards, 2.26 µs) and 3,236-3,244 cycles over all 1,024 minions (each card's median over three passes: aifoundry2 3,236.33, aifoundry3 3,243.35, aifoundry1-c1 3,244.27; 5.4 µs at 600 MHz), against 444 and 1,393 cycles for 32 B.
measured
three cards
On-chip communication ↗
bc.allreduce-1kb
The broadcast half of the tree was never timed on its own: nocbench times TensorReduce up the tree and TensorBroadcast back down as one operation, one cycle count around both, so the broadcast is part of the allreduce's 444 cycles over 32 minions and 1,393 over 1,024 (32 B). Neither half's energy was measured: the energy manual's synchronisation table gives none for the tree.
model
On-chip communication ↗
bc.half
Messaging energy, 1 KB TensorSend: 0.69 pJ/B between the two minions of a pair, 2.16 around a neighbourhood, 2.22 around a shire, 12.5-18.3 across the mesh (busy cores included).
measured
three cards
On-chip communication ↗
ts-e-pair
Relay energy per byte moved, each byte counted once when written and once when read: through DRAM 116.2 pJ/B [104.5-135.3], to the next shire, which reads the previous shire's scratchpad, 8.9 [7.6-10.2], in the own scratchpad 4.3 [3.8-5.1]; a hand-off writes every byte once and reads it once, so a byte handed to the next shire costs 17.8 pJ (232 through DRAM).
measured
three cards
Hand it to the next shire: on-chip relay vs DRAM ↗
relay-energy
Handing a slab to the next shire through its scratchpad costs 12.9x, 13.0x and 13.1x less energy per byte than the DRAM round trip (aifoundry2, aifoundry3, aifoundry1-c1): about a thirteenth, the same on every card at 99%.
measured
three cards
Hand it to the next shire: on-chip relay vs DRAM ↗
relay-13x
Relay bandwidth (8 stages, 1,024 minions; bytes read plus bytes written): 47.7 GB/s through DRAM, 592.5 GB/s to the next shire (12.4x), 1487 GB/s in the own scratchpad (aifoundry2 pass means; the other cards within 1.5%).
measured
aifoundry2 pass means (the other cards within 1.5%)
Hand it to the next shire: on-chip relay vs DRAM ↗
relay-bw
DRAM: 114.6 pJ/B [89.0-141.3] above idle, 1 KB tensor loads (L1: 32 B vector loads) by every minion at 600 MHz; per card a2 111.5, a3 105.6, a1c1 126.6.
measured
three cards
The energy manual ↗
e-dram
DRAM streaming: 76 GB/s for the whole chip (0.124 B per minion-cycle), about 64% of the 119 GB/s that 16 x 16-bit channels carry at 3,733 MT/s; about a twentieth of an A100.
measured
aifoundry2, aifoundry3
Ridge points ↗
bw-dram
A line's L3 home shire is PA[10:6]: consecutive 64-byte lines rotate over the 32 compute shires' L3 slices (default 'swizzle0'; the firmware leaves the swizzle register at reset).
measured
three cards
Anatomy of a memory access ↗
l3.home
L3 hit: 110 + 12 cycles per mesh hop between the requesting shire and the line's home shire (fitted 110.5 + 11.99 on three cards); 159-169 cycles (265-282 ns) on average depending on the requesting shire.
measured
three cards
Anatomy of a memory access ↗
l3.latency
Inside a shire, requests to one line are kept in order, and 'Two requests to the mesh will never have the same address outstanding': when every minion of a shire loads one line homed in another shire, the shire has at most one request for it on the mesh at a time. The L2's 8-entry read buffer is there for 'multiple readers of the same cache line', its hits 'serviced once per clock'; L3 reads at the home do not use it.
documented
no published page yet
bc.one-request
L3 (over the mesh): 14.7 pJ/B [7.1-20.5] above idle, 1 KB tensor loads (L1: 32 B vector loads) by every minion at 600 MHz; per card a2 12.3, a3 13.5, a1c1 18.4.
measured
three cards
The energy manual ↗
e-l3
One contended global atomic (amoaddg.w on one line, 1,024 minions): the bank retires one every 10.00 cycles, about 60 M/s for the whole chip; spread over 32 lines, one per shire, 0.31 cycles and 1,919 M/s: 32x.
measured
aifoundry2
One hot line stops a shire ↗
hot-cost
31 minions, one in each other shire, hammering one global atomic homed in shire 0 kept its bank retiring one every 10.00 cycles, while shire 0's one minion reading its own scratchpad kept 100% of its rate alone, in three passes on each of the three cards (the prediction was 1% or less). Whether they would stop a shire whose 32 minions all read was not tested. Each shire's leader polling one counter hung the relay's first barrier (one development run).
measured
three cards
One hot line stops a shire ↗
bc.pollers
The host shire's minions read their own scratchpad while the same number of minions in one other shire hammer one scratchpad word in the host shire: with 21 of each the host keeps 95.6 / 95.7 / 95.6% of its rate alone (aifoundry2 / aifoundry3 / aifoundry1-c1, mean of 3 passes; 95.5-95.7% over every pass), and with 22, 23 or 24 it stops: 0.02% on every card. An uncontended remote atomic takes 216.2 / 216.3 / 216.6 cycles round trip.
measured
three cards
One hot line stops a shire ↗
hot.cliff
A global atomic (amoaddg) is performed at the shire cache that homes the line. One contended line serialises at 10.00 cycles per atomic (about 60 M/s for the chip) and stops the host shire's own memory path; an uncontended remote global atomic round trip is 216 cycles.
measured
aifoundry2, aifoundry3
One hot line stops a shire ↗
mem.global-atomic
ESR broadcast: one request writes the same system register in every shire of a mask (32 bits for the compute shires, 8 for the memory shires): software writes the value to the broadcast data register, then the target register and the masks to a broadcast request register. A shire's IPI_TRIGGER register takes a 64-bit mask of its harts and interrupts each hart whose bit is set; the firmware's broadcast system call writes the first two.
documented
no published page yet
bc.esr-ipi
Every kernel launch is a broadcast. The master shire's firmware copies the 64-byte launch message into a buffer in its own scratchpad and evicts it to the L2, raises the interrupt on all 64 harts of every shire in the kernel's mask with one ESR broadcast, and polls a shire mask beside the buffer: each hart evicts its stale L1 copy and reads the message, and the last of a shire's 64 harts clears that shire's bit with a global atomic AND. The launch goes on once every bit is clear.
documented
no published page yet
bc.launch-multicast
Queued back to back, an empty kernel costs the card 103.6 / 103.7 / 104.1 µs on all 32 shires and 91.2 / 92.2 / 92.4 µs on one (aifoundry2 / aifoundry3 / aifoundry1-c1): the other 31 shires add 12.4 / 11.4 / 11.6 µs (11.4-12.4 µs), the rest the same for one shire or 32. Which part of that is the launch's multicast (the interrupt, every hart reading the message, the shires' acknowledging atomics) and which the kernel's own start and finish was not measured.
model
three cards
Over the PCIe link ↗
bc.launch-31
An empty kernel on all 32 compute shires, launched and waited for: 566 / 556 / 565 µs (556-566 µs) from launch to completion (aifoundry2 / aifoundry3 / aifoundry1-c1); 100 launches queued back to back: 103.6 / 103.7 / 104.1 µs each (103.6-104.1 µs) on 32 shires and 91.2 / 92.2 / 92.4 on one shire. The card's own cost is the queued figure: a lone launch waited for adds 463 / 452 / 461 µs (452-463 µs, each run's difference), most of the runtime's 500 µs idle poll (fact pcie.poll), and a one-shire lone launch takes the same 566 / 556 / 565 µs.
measured
three cards
Over the PCIe link ↗
pcie.launch
The runtime's response thread polls the device's completion queue, sleeping 50 µs between polls while commands are in flight and 500 µs when none are.
documented
Over the PCIe link ↗
pcie.poll
Chip-wide barrier built from FLB, global atomics and credits: 4,976-4,991 cycles with one minion per shire, 4,998-5,013 with all 1,024 (about 8.3 us); the allreduce tree does it in 2.3 us.
measured
three cards
On-chip communication ↗
sync-chip-barrier
The mesh routes in dimension order, and a request and its reply take opposite orders: a request goes x first, then y, and a reply y first, then x, on the logical map, so a reply retraces its request's route backwards. Measured on 29 September (E56) with sets of streams between shires chosen so that their streams share one directed link under one order and none under the other: 1 KB tensor loads, whose data travel as replies, fell to 0.54-0.77 of their bandwidth alone when they shared a link under y first and held at 1.00 when they shared one under x first; tensor stores, whose data travel as requests, showed the mirror (0.52-0.76 against 1.00). A shared link carried about 92 GB/s. The same on aifoundry1 card 1 (development), aifoundry3 (the frozen validation) and aifoundry2 (the same frozen test, run as a third card on the evening of 29 September), three passes each.
measured
three cards
no published page yet
L104+}

## flow/K/7
FLOW B · BROADCAST
At the home, the line's … what each costs.

 More detail and the sources {+

How one value, 32 B or 1 KB, gets from minion 0 of shire 0 to all 1,024 minions, and what each way costs. The chip offers four: the hardware tree (TensorBroadcast), a relay from shire to shire, one line in memory that every minion loads, and the multicast every kernel launch already makes.

 Leg What happens
the value hart 0's 32 vector registers of 32 bytes: 32 B fills one, 1 KB all of them; only hart 0 issues tensor instructions
tree: mesh TensorBroadcast down the allreduce's tree, levels 9 to 5 between shires: 164–234 cycles a level, up and down
tree: shire levels 4 and 3 through the crossbar, 117 cycles a level; 2 to 0 on the tree edges, 68–71 cycles; in every shire at once
tree, timed with the reduction, 32 B: 444 cycles (0.74 µs) over 32 minions, 1,393 cycles (2.3 µs) over 1,024; 1 KB: 1,354 cycles (2.26 µs) and 3,236–3,244 cycles (5.4 µs)
relay or DRAM a hand-off to the next shire 17.8 pJ per byte, its write and its read (8.9 pJ/B moved), about a thirteenth of a DRAM round trip; every shire reading DRAM 115 pJ/B each, the chip's 76 GB/s shared
one line every minion loads one line from its L3 home: one load 110 + 12 cycles a hop; one request per shire at a time; 15 pJ/B over the mesh
at its home the line's bank: an atomic every 10.00 cycles; 31 requesters, one a shire, left the home's reader at 100%; 22 from one shire hammering it stop the home's loads (0.02%)
the launch one 64-byte message, one ESR broadcast, every hart reads it, one atomic a shire: an empty kernel 103.6–104.1 µs queued on 32 shires, 91.2 / 92.2 / 92.4 on one
compared to all 1,024: the tree 2.3 µs (32 B) or 5.4 µs (1 KB); a chip barrier alone 8.3 µs; a queued launch 103.6–104.1 µs

 Not measured: the tree's broadcast half on its own (it was timed only with the reduction) and the tree's energy (fact bc.half); how long a relay takes to reach every shire (the relay moved 1 MB slabs down a pipeline); every minion loading one line at once (the hot-line runs used atomics); the launch's multicast apart from the rest of a launch, and its energy (fact bc.launch-31).

 The mesh takes a request x first and a reply y first (measured for loads and stores): the reads' requests are drawn x first, and the data they bring back, the relay's hand-offs among them, y first, and the tree's messages as requests, x first. The interrupt that starts a launch is drawn at each shire, not along a route: its path over the mesh is not documented.

 Measured and explained in On-chip communication ↗.

 The facts this flow uses (31): point at one for its source

 Each lane's register file holds 64 × 32-bit entries (32 per thread), so each hart has 32 vector registers of 32 bytes; 8 mask registers of 8 bits.
documented
On-chip communication ↗
minion.vpu-regs
Only hart 0 of a minion may issue tensor instructions; hart 1 may only issue TensorLoadL2Scp, TensorWait and tensor_coop accesses.
documented
Limits of observability ↗
minion.tensor-hart0
TensorBroadcast sends COUNT vector registers of 32 bytes down a fully balanced binary tree: at node height HEIGHT a hart whose mhartid is a multiple of 2^(HEIGHT+2) sends to hart mhartid + 2^(HEIGHT+1), and with FUNCT = MOVE every hart ends with the root's value. N harts take log2 N steps, HEIGHT from log2(N) - 1 down to 0, and each step waits for both of its harts, their vector registers stalled until the data has moved. Hart 0 of minion m is hart 2m, so a broadcast from minion 0 to all 1,024 minions takes ten steps, the first to minion 512, minion 0 of shire 16.
documented
On-chip communication ↗
bc.tensorbroadcast
The allreduce benchmark's tree: at level h, a minion whose ID has bit h as its lowest set bit sends its partial sum to the minion with that bit cleared (TensorReduce), levels 0 to 9, and the result comes back down the same tree (TensorBroadcast). Levels 0-2 join a neighbourhood's 8 minions along the fast network's edges, levels 3-4 its 4 neighbourhoods, levels 5-9 the 32 shires, rooted at minion 0 of shire 0.
documented
On-chip communication ↗
ar.tree
The fast local messaging network links minions within a neighbourhood only along the reduction tree: 0-1, 0-2, 0-4, 2-3, 4-5, 4-6, 6-7.
documented
On-chip communication ↗
neigh.fln-edges
Each allreduce tree level adds about one round trip: 68-71 cycles on the fast network (levels 0-2), 117 through the crossbar (levels 3-4) and 164-234 over the mesh (levels 5-9).
measured
three cards
On-chip communication ↗
sync.tree-levels
Hardware allreduce (TensorReduce + TensorBroadcast) of 32 B over a shire's 32 minions: 444 cycles (0.74 us), 444.06-444.31 on all three cards.
measured
three cards
On-chip communication ↗
sync-allreduce32
Hardware allreduce of 32 B over all 1,024 minions: 1,393 cycles (2.3 us), 1,392.6-1,393.4 on the three cards; an A100 grid.sync() alone is 1.1-1.2 us.
measured
three cards
On-chip communication ↗
sync-allreduce1024
The same hardware allreduce with 1 KB (32 vector registers) instead of 32 B: 1,354 cycles over a shire's 32 minions (1,354.05-1,354.16 in every pass on the three cards, 2.26 µs) and 3,236-3,244 cycles over all 1,024 minions (each card's median over three passes: aifoundry2 3,236.33, aifoundry3 3,243.35, aifoundry1-c1 3,244.27; 5.4 µs at 600 MHz), against 444 and 1,393 cycles for 32 B.
measured
three cards
On-chip communication ↗
bc.allreduce-1kb
The broadcast half of the tree was never timed on its own: nocbench times TensorReduce up the tree and TensorBroadcast back down as one operation, one cycle count around both, so the broadcast is part of the allreduce's 444 cycles over 32 minions and 1,393 over 1,024 (32 B). Neither half's energy was measured: the energy manual's synchronisation table gives none for the tree.
model
On-chip communication ↗
bc.half
Messaging energy, 1 KB TensorSend: 0.69 pJ/B between the two minions of a pair, 2.16 around a neighbourhood, 2.22 around a shire, 12.5-18.3 across the mesh (busy cores included).
measured
three cards
On-chip communication ↗
ts-e-pair
Relay energy per byte moved, each byte counted once when written and once when read: through DRAM 116.2 pJ/B [104.5-135.3], to the next shire, which reads the previous shire's scratchpad, 8.9 [7.6-10.2], in the own scratchpad 4.3 [3.8-5.1]; a hand-off writes every byte once and reads it once, so a byte handed to the next shire costs 17.8 pJ (232 through DRAM).
measured
three cards
Hand it to the next shire: on-chip relay vs DRAM ↗
relay-energy
Handing a slab to the next shire through its scratchpad costs 12.9x, 13.0x and 13.1x less energy per byte than the DRAM round trip (aifoundry2, aifoundry3, aifoundry1-c1): about a thirteenth, the same on every card at 99%.
measured
three cards
Hand it to the next shire: on-chip relay vs DRAM ↗
relay-13x
Relay bandwidth (8 stages, 1,024 minions; bytes read plus bytes written): 47.7 GB/s through DRAM, 592.5 GB/s to the next shire (12.4x), 1487 GB/s in the own scratchpad (aifoundry2 pass means; the other cards within 1.5%).
measured
aifoundry2 pass means (the other cards within 1.5%)
Hand it to the next shire: on-chip relay vs DRAM ↗
relay-bw
DRAM: 114.6 pJ/B [89.0-141.3] above idle, 1 KB tensor loads (L1: 32 B vector loads) by every minion at 600 MHz; per card a2 111.5, a3 105.6, a1c1 126.6.
measured
three cards
The energy manual ↗
e-dram
DRAM streaming: 76 GB/s for the whole chip (0.124 B per minion-cycle), about 64% of the 119 GB/s that 16 x 16-bit channels carry at 3,733 MT/s; about a twentieth of an A100.
measured
aifoundry2, aifoundry3
Ridge points ↗
bw-dram
A line's L3 home shire is PA[10:6]: consecutive 64-byte lines rotate over the 32 compute shires' L3 slices (default 'swizzle0'; the firmware leaves the swizzle register at reset).
measured
three cards
Anatomy of a memory access ↗
l3.home
L3 hit: 110 + 12 cycles per mesh hop between the requesting shire and the line's home shire (fitted 110.5 + 11.99 on three cards); 159-169 cycles (265-282 ns) on average depending on the requesting shire.
measured
three cards
Anatomy of a memory access ↗
l3.latency
Inside a shire, requests to one line are kept in order, and 'Two requests to the mesh will never have the same address outstanding': when every minion of a shire loads one line homed in another shire, the shire has at most one request for it on the mesh at a time. The L2's 8-entry read buffer is there for 'multiple readers of the same cache line', its hits 'serviced once per clock'; L3 reads at the home do not use it.
documented
no published page yet
bc.one-request
L3 (over the mesh): 14.7 pJ/B [7.1-20.5] above idle, 1 KB tensor loads (L1: 32 B vector loads) by every minion at 600 MHz; per card a2 12.3, a3 13.5, a1c1 18.4.
measured
three cards
The energy manual ↗
e-l3
One contended global atomic (amoaddg.w on one line, 1,024 minions): the bank retires one every 10.00 cycles, about 60 M/s for the whole chip; spread over 32 lines, one per shire, 0.31 cycles and 1,919 M/s: 32x.
measured
aifoundry2
One hot line stops a shire ↗
hot-cost
31 minions, one in each other shire, hammering one global atomic homed in shire 0 kept its bank retiring one every 10.00 cycles, while shire 0's one minion reading its own scratchpad kept 100% of its rate alone, in three passes on each of the three cards (the prediction was 1% or less). Whether they would stop a shire whose 32 minions all read was not tested. Each shire's leader polling one counter hung the relay's first barrier (one development run).
measured
three cards
One hot line stops a shire ↗
bc.pollers
The host shire's minions read their own scratchpad while the same number of minions in one other shire hammer one scratchpad word in the host shire: with 21 of each the host keeps 95.6 / 95.7 / 95.6% of its rate alone (aifoundry2 / aifoundry3 / aifoundry1-c1, mean of 3 passes; 95.5-95.7% over every pass), and with 22, 23 or 24 it stops: 0.02% on every card. An uncontended remote atomic takes 216.2 / 216.3 / 216.6 cycles round trip.
measured
three cards
One hot line stops a shire ↗
hot.cliff
A global atomic (amoaddg) is performed at the shire cache that homes the line. One contended line serialises at 10.00 cycles per atomic (about 60 M/s for the chip) and stops the host shire's own memory path; an uncontended remote global atomic round trip is 216 cycles.
measured
aifoundry2, aifoundry3
One hot line stops a shire ↗
mem.global-atomic
ESR broadcast: one request writes the same system register in every shire of a mask (32 bits for the compute shires, 8 for the memory shires): software writes the value to the broadcast data register, then the target register and the masks to a broadcast request register. A shire's IPI_TRIGGER register takes a 64-bit mask of its harts and interrupts each hart whose bit is set; the firmware's broadcast system call writes the first two.
documented
no published page yet
bc.esr-ipi
Every kernel launch is a broadcast. The master shire's firmware copies the 64-byte launch message into a buffer in its own scratchpad and evicts it to the L2, raises the interrupt on all 64 harts of every shire in the kernel's mask with one ESR broadcast, and polls a shire mask beside the buffer: each hart evicts its stale L1 copy and reads the message, and the last of a shire's 64 harts clears that shire's bit with a global atomic AND. The launch goes on once every bit is clear.
documented
no published page yet
bc.launch-multicast
Queued back to back, an empty kernel costs the card 103.6 / 103.7 / 104.1 µs on all 32 shires and 91.2 / 92.2 / 92.4 µs on one (aifoundry2 / aifoundry3 / aifoundry1-c1): the other 31 shires add 12.4 / 11.4 / 11.6 µs (11.4-12.4 µs), the rest the same for one shire or 32. Which part of that is the launch's multicast (the interrupt, every hart reading the message, the shires' acknowledging atomics) and which the kernel's own start and finish was not measured.
model
three cards
Over the PCIe link ↗
bc.launch-31
An empty kernel on all 32 compute shires, launched and waited for: 566 / 556 / 565 µs (556-566 µs) from launch to completion (aifoundry2 / aifoundry3 / aifoundry1-c1); 100 launches queued back to back: 103.6 / 103.7 / 104.1 µs each (103.6-104.1 µs) on 32 shires and 91.2 / 92.2 / 92.4 on one shire. The card's own cost is the queued figure: a lone launch waited for adds 463 / 452 / 461 µs (452-463 µs, each run's difference), most of the runtime's 500 µs idle poll (fact pcie.poll), and a one-shire lone launch takes the same 566 / 556 / 565 µs.
measured
three cards
Over the PCIe link ↗
pcie.launch
The runtime's response thread polls the device's completion queue, sleeping 50 µs between polls while commands are in flight and 500 µs when none are.
documented
Over the PCIe link ↗
pcie.poll
Chip-wide barrier built from FLB, global atomics and credits: 4,976-4,991 cycles with one minion per shire, 4,998-5,013 with all 1,024 (about 8.3 us); the allreduce tree does it in 2.3 us.
measured
three cards
On-chip communication ↗
sync-chip-barrier
The mesh routes in dimension order, and a request and its reply take opposite orders: a request goes x first, then y, and a reply y first, then x, on the logical map, so a reply retraces its request's route backwards. Measured on 29 September (E56) with sets of streams between shires chosen so that their streams share one directed link under one order and none under the other: 1 KB tensor loads, whose data travel as replies, fell to 0.54-0.77 of their bandwidth alone when they shared a link under y first and held at 1.00 when they shared one under x first; tensor stores, whose data travel as requests, showed the mirror (0.52-0.76 against 1.00). A shared link carried about 92 GB/s. The same on aifoundry1 card 1 (development), aifoundry3 (the frozen validation) and aifoundry2 (the same frozen test, run as a third card on the evening of 29 September), three passes each.
measured
three cards
no published page yet
L104+}

## flow/K/8
FLOW B · BROADCAST
Every kernel launch is a … what each costs.

 More detail and the sources {+

How one value, 32 B or 1 KB, gets from minion 0 of shire 0 to all 1,024 minions, and what each way costs. The chip offers four: the hardware tree (TensorBroadcast), a relay from shire to shire, one line in memory that every minion loads, and the multicast every kernel launch already makes.

 Leg What happens
the value hart 0's 32 vector registers of 32 bytes: 32 B fills one, 1 KB all of them; only hart 0 issues tensor instructions
tree: mesh TensorBroadcast down the allreduce's tree, levels 9 to 5 between shires: 164–234 cycles a level, up and down
tree: shire levels 4 and 3 through the crossbar, 117 cycles a level; 2 to 0 on the tree edges, 68–71 cycles; in every shire at once
tree, timed with the reduction, 32 B: 444 cycles (0.74 µs) over 32 minions, 1,393 cycles (2.3 µs) over 1,024; 1 KB: 1,354 cycles (2.26 µs) and 3,236–3,244 cycles (5.4 µs)
relay or DRAM a hand-off to the next shire 17.8 pJ per byte, its write and its read (8.9 pJ/B moved), about a thirteenth of a DRAM round trip; every shire reading DRAM 115 pJ/B each, the chip's 76 GB/s shared
one line every minion loads one line from its L3 home: one load 110 + 12 cycles a hop; one request per shire at a time; 15 pJ/B over the mesh
at its home the line's bank: an atomic every 10.00 cycles; 31 requesters, one a shire, left the home's reader at 100%; 22 from one shire hammering it stop the home's loads (0.02%)
the launch one 64-byte message, one ESR broadcast, every hart reads it, one atomic a shire: an empty kernel 103.6–104.1 µs queued on 32 shires, 91.2 / 92.2 / 92.4 on one
compared to all 1,024: the tree 2.3 µs (32 B) or 5.4 µs (1 KB); a chip barrier alone 8.3 µs; a queued launch 103.6–104.1 µs

 Not measured: the tree's broadcast half on its own (it was timed only with the reduction) and the tree's energy (fact bc.half); how long a relay takes to reach every shire (the relay moved 1 MB slabs down a pipeline); every minion loading one line at once (the hot-line runs used atomics); the launch's multicast apart from the rest of a launch, and its energy (fact bc.launch-31).

 The mesh takes a request x first and a reply y first (measured for loads and stores): the reads' requests are drawn x first, and the data they bring back, the relay's hand-offs among them, y first, and the tree's messages as requests, x first. The interrupt that starts a launch is drawn at each shire, not along a route: its path over the mesh is not documented.

 Measured and explained in On-chip communication ↗.

 The facts this flow uses (31): point at one for its source

 Each lane's register file holds 64 × 32-bit entries (32 per thread), so each hart has 32 vector registers of 32 bytes; 8 mask registers of 8 bits.
documented
On-chip communication ↗
minion.vpu-regs
Only hart 0 of a minion may issue tensor instructions; hart 1 may only issue TensorLoadL2Scp, TensorWait and tensor_coop accesses.
documented
Limits of observability ↗
minion.tensor-hart0
TensorBroadcast sends COUNT vector registers of 32 bytes down a fully balanced binary tree: at node height HEIGHT a hart whose mhartid is a multiple of 2^(HEIGHT+2) sends to hart mhartid + 2^(HEIGHT+1), and with FUNCT = MOVE every hart ends with the root's value. N harts take log2 N steps, HEIGHT from log2(N) - 1 down to 0, and each step waits for both of its harts, their vector registers stalled until the data has moved. Hart 0 of minion m is hart 2m, so a broadcast from minion 0 to all 1,024 minions takes ten steps, the first to minion 512, minion 0 of shire 16.
documented
On-chip communication ↗
bc.tensorbroadcast
The allreduce benchmark's tree: at level h, a minion whose ID has bit h as its lowest set bit sends its partial sum to the minion with that bit cleared (TensorReduce), levels 0 to 9, and the result comes back down the same tree (TensorBroadcast). Levels 0-2 join a neighbourhood's 8 minions along the fast network's edges, levels 3-4 its 4 neighbourhoods, levels 5-9 the 32 shires, rooted at minion 0 of shire 0.
documented
On-chip communication ↗
ar.tree
The fast local messaging network links minions within a neighbourhood only along the reduction tree: 0-1, 0-2, 0-4, 2-3, 4-5, 4-6, 6-7.
documented
On-chip communication ↗
neigh.fln-edges
Each allreduce tree level adds about one round trip: 68-71 cycles on the fast network (levels 0-2), 117 through the crossbar (levels 3-4) and 164-234 over the mesh (levels 5-9).
measured
three cards
On-chip communication ↗
sync.tree-levels
Hardware allreduce (TensorReduce + TensorBroadcast) of 32 B over a shire's 32 minions: 444 cycles (0.74 us), 444.06-444.31 on all three cards.
measured
three cards
On-chip communication ↗
sync-allreduce32
Hardware allreduce of 32 B over all 1,024 minions: 1,393 cycles (2.3 us), 1,392.6-1,393.4 on the three cards; an A100 grid.sync() alone is 1.1-1.2 us.
measured
three cards
On-chip communication ↗
sync-allreduce1024
The same hardware allreduce with 1 KB (32 vector registers) instead of 32 B: 1,354 cycles over a shire's 32 minions (1,354.05-1,354.16 in every pass on the three cards, 2.26 µs) and 3,236-3,244 cycles over all 1,024 minions (each card's median over three passes: aifoundry2 3,236.33, aifoundry3 3,243.35, aifoundry1-c1 3,244.27; 5.4 µs at 600 MHz), against 444 and 1,393 cycles for 32 B.
measured
three cards
On-chip communication ↗
bc.allreduce-1kb
The broadcast half of the tree was never timed on its own: nocbench times TensorReduce up the tree and TensorBroadcast back down as one operation, one cycle count around both, so the broadcast is part of the allreduce's 444 cycles over 32 minions and 1,393 over 1,024 (32 B). Neither half's energy was measured: the energy manual's synchronisation table gives none for the tree.
model
On-chip communication ↗
bc.half
Messaging energy, 1 KB TensorSend: 0.69 pJ/B between the two minions of a pair, 2.16 around a neighbourhood, 2.22 around a shire, 12.5-18.3 across the mesh (busy cores included).
measured
three cards
On-chip communication ↗
ts-e-pair
Relay energy per byte moved, each byte counted once when written and once when read: through DRAM 116.2 pJ/B [104.5-135.3], to the next shire, which reads the previous shire's scratchpad, 8.9 [7.6-10.2], in the own scratchpad 4.3 [3.8-5.1]; a hand-off writes every byte once and reads it once, so a byte handed to the next shire costs 17.8 pJ (232 through DRAM).
measured
three cards
Hand it to the next shire: on-chip relay vs DRAM ↗
relay-energy
Handing a slab to the next shire through its scratchpad costs 12.9x, 13.0x and 13.1x less energy per byte than the DRAM round trip (aifoundry2, aifoundry3, aifoundry1-c1): about a thirteenth, the same on every card at 99%.
measured
three cards
Hand it to the next shire: on-chip relay vs DRAM ↗
relay-13x
Relay bandwidth (8 stages, 1,024 minions; bytes read plus bytes written): 47.7 GB/s through DRAM, 592.5 GB/s to the next shire (12.4x), 1487 GB/s in the own scratchpad (aifoundry2 pass means; the other cards within 1.5%).
measured
aifoundry2 pass means (the other cards within 1.5%)
Hand it to the next shire: on-chip relay vs DRAM ↗
relay-bw
DRAM: 114.6 pJ/B [89.0-141.3] above idle, 1 KB tensor loads (L1: 32 B vector loads) by every minion at 600 MHz; per card a2 111.5, a3 105.6, a1c1 126.6.
measured
three cards
The energy manual ↗
e-dram
DRAM streaming: 76 GB/s for the whole chip (0.124 B per minion-cycle), about 64% of the 119 GB/s that 16 x 16-bit channels carry at 3,733 MT/s; about a twentieth of an A100.
measured
aifoundry2, aifoundry3
Ridge points ↗
bw-dram
A line's L3 home shire is PA[10:6]: consecutive 64-byte lines rotate over the 32 compute shires' L3 slices (default 'swizzle0'; the firmware leaves the swizzle register at reset).
measured
three cards
Anatomy of a memory access ↗
l3.home
L3 hit: 110 + 12 cycles per mesh hop between the requesting shire and the line's home shire (fitted 110.5 + 11.99 on three cards); 159-169 cycles (265-282 ns) on average depending on the requesting shire.
measured
three cards
Anatomy of a memory access ↗
l3.latency
Inside a shire, requests to one line are kept in order, and 'Two requests to the mesh will never have the same address outstanding': when every minion of a shire loads one line homed in another shire, the shire has at most one request for it on the mesh at a time. The L2's 8-entry read buffer is there for 'multiple readers of the same cache line', its hits 'serviced once per clock'; L3 reads at the home do not use it.
documented
no published page yet
bc.one-request
L3 (over the mesh): 14.7 pJ/B [7.1-20.5] above idle, 1 KB tensor loads (L1: 32 B vector loads) by every minion at 600 MHz; per card a2 12.3, a3 13.5, a1c1 18.4.
measured
three cards
The energy manual ↗
e-l3
One contended global atomic (amoaddg.w on one line, 1,024 minions): the bank retires one every 10.00 cycles, about 60 M/s for the whole chip; spread over 32 lines, one per shire, 0.31 cycles and 1,919 M/s: 32x.
measured
aifoundry2
One hot line stops a shire ↗
hot-cost
31 minions, one in each other shire, hammering one global atomic homed in shire 0 kept its bank retiring one every 10.00 cycles, while shire 0's one minion reading its own scratchpad kept 100% of its rate alone, in three passes on each of the three cards (the prediction was 1% or less). Whether they would stop a shire whose 32 minions all read was not tested. Each shire's leader polling one counter hung the relay's first barrier (one development run).
measured
three cards
One hot line stops a shire ↗
bc.pollers
The host shire's minions read their own scratchpad while the same number of minions in one other shire hammer one scratchpad word in the host shire: with 21 of each the host keeps 95.6 / 95.7 / 95.6% of its rate alone (aifoundry2 / aifoundry3 / aifoundry1-c1, mean of 3 passes; 95.5-95.7% over every pass), and with 22, 23 or 24 it stops: 0.02% on every card. An uncontended remote atomic takes 216.2 / 216.3 / 216.6 cycles round trip.
measured
three cards
One hot line stops a shire ↗
hot.cliff
A global atomic (amoaddg) is performed at the shire cache that homes the line. One contended line serialises at 10.00 cycles per atomic (about 60 M/s for the chip) and stops the host shire's own memory path; an uncontended remote global atomic round trip is 216 cycles.
measured
aifoundry2, aifoundry3
One hot line stops a shire ↗
mem.global-atomic
ESR broadcast: one request writes the same system register in every shire of a mask (32 bits for the compute shires, 8 for the memory shires): software writes the value to the broadcast data register, then the target register and the masks to a broadcast request register. A shire's IPI_TRIGGER register takes a 64-bit mask of its harts and interrupts each hart whose bit is set; the firmware's broadcast system call writes the first two.
documented
no published page yet
bc.esr-ipi
Every kernel launch is a broadcast. The master shire's firmware copies the 64-byte launch message into a buffer in its own scratchpad and evicts it to the L2, raises the interrupt on all 64 harts of every shire in the kernel's mask with one ESR broadcast, and polls a shire mask beside the buffer: each hart evicts its stale L1 copy and reads the message, and the last of a shire's 64 harts clears that shire's bit with a global atomic AND. The launch goes on once every bit is clear.
documented
no published page yet
bc.launch-multicast
Queued back to back, an empty kernel costs the card 103.6 / 103.7 / 104.1 µs on all 32 shires and 91.2 / 92.2 / 92.4 µs on one (aifoundry2 / aifoundry3 / aifoundry1-c1): the other 31 shires add 12.4 / 11.4 / 11.6 µs (11.4-12.4 µs), the rest the same for one shire or 32. Which part of that is the launch's multicast (the interrupt, every hart reading the message, the shires' acknowledging atomics) and which the kernel's own start and finish was not measured.
model
three cards
Over the PCIe link ↗
bc.launch-31
An empty kernel on all 32 compute shires, launched and waited for: 566 / 556 / 565 µs (556-566 µs) from launch to completion (aifoundry2 / aifoundry3 / aifoundry1-c1); 100 launches queued back to back: 103.6 / 103.7 / 104.1 µs each (103.6-104.1 µs) on 32 shires and 91.2 / 92.2 / 92.4 on one shire. The card's own cost is the queued figure: a lone launch waited for adds 463 / 452 / 461 µs (452-463 µs, each run's difference), most of the runtime's 500 µs idle poll (fact pcie.poll), and a one-shire lone launch takes the same 566 / 556 / 565 µs.
measured
three cards
Over the PCIe link ↗
pcie.launch
The runtime's response thread polls the device's completion queue, sleeping 50 µs between polls while commands are in flight and 500 µs when none are.
documented
Over the PCIe link ↗
pcie.poll
Chip-wide barrier built from FLB, global atomics and credits: 4,976-4,991 cycles with one minion per shire, 4,998-5,013 with all 1,024 (about 8.3 us); the allreduce tree does it in 2.3 us.
measured
three cards
On-chip communication ↗
sync-chip-barrier
The mesh routes in dimension order, and a request and its reply take opposite orders: a request goes x first, then y, and a reply y first, then x, on the logical map, so a reply retraces its request's route backwards. Measured on 29 September (E56) with sets of streams between shires chosen so that their streams share one directed link under one order and none under the other: 1 KB tensor loads, whose data travel as replies, fell to 0.54-0.77 of their bandwidth alone when they shared a link under y first and held at 1.00 when they shared one under x first; tensor stores, whose data travel as requests, showed the mirror (0.52-0.76 against 1.00). A shared link carried about 92 GB/s. The same on aifoundry1 card 1 (development), aifoundry3 (the frozen validation) and aifoundry2 (the same frozen test, run as a third card on the evening of 29 September), three passes each.
measured
three cards
no published page yet
L104+}

## scale/card/here
YOU ARE HERE · 16.8 cm · 10⁻¹ m
… the datasheet's 4,266 MT/s would give 136.5 GB/s. Tensor loads {+stream 76 GB/s+} from [-memory have been measured at 75 GB/s.-] {+this memory, 64% of the 119.5 GB/s peak (fact bw-dram).+}
model
out.card.4
Each memory package is about … out.card.5
Power arrives as 12 V at the card [-edge: at most-] {+edge; the vendor's power tree budgets+} 7.3 A, 88 W. [-The-] {+Under load the+} highest draw on record is 87.8 W; {+an idle card whose cooling failed drew 134 W before it dropped off the PCIe bus (aifoundry2, 2, 7 and 8 Oct 2026). With working cooling+} the cards idle at about [-19-36-] {+19-50+} W, depending on the card and its [-temperature.-] {+temperature (aifoundry1 card 1 idles highest: 42.7 W at 73 °C, 50 W at 80 °C).+}
documented
out.card.6
The cores run at about … of a 600 MHz clock tick.
inference
out.card.12

## scale/card/part/edge
The PCIe card edge. Space for details; Enter zooms in. … out.card.2
Power arrives as 12 V at the card [-edge: at most-] {+edge; the vendor's power tree budgets+} 7.3 A, 88 W. [-The-] {+Under load the+} highest draw on record is 87.8 W; {+an idle card whose cooling failed drew 134 W before it dropped off the PCIe bus (aifoundry2, 2, 7 and 8 Oct 2026). With working cooling+} the cards idle at about [-19-36-] {+19-50+} W, depending on the card and its [-temperature.-] {+temperature (aifoundry1 card 1 idles highest: 42.7 W at 73 °C, 50 W at 80 °C).+}
documented
out.card.6

## scale/card/part/lpddr
LPDDR4X memory package U11. Space for details; Enter zooms in. … the datasheet's 4,266 MT/s would give 136.5 GB/s. Tensor loads {+stream 76 GB/s+} from [-memory have been measured at 75 GB/s.-] {+this memory, 64% of the 119.5 GB/s peak (fact bw-dram).+}
model
out.card.4
Each memory package is about … lab cards carry is not recorded.
inference
out.card.5

## scale/card/part/lpddr#2
LPDDR4X memory package U20. Space for details; Enter zooms in. … the datasheet's 4,266 MT/s would give 136.5 GB/s. Tensor loads {+stream 76 GB/s+} from [-memory have been measured at 75 GB/s.-] {+this memory, 64% of the 119.5 GB/s peak (fact bw-dram).+}
model
out.card.4
Each memory package is about … lab cards carry is not recorded.
inference
out.card.5

## scale/card/part/lpddr#3
LPDDR4X memory package U12. Space for details; Enter zooms in. … the datasheet's 4,266 MT/s would give 136.5 GB/s. Tensor loads {+stream 76 GB/s+} from [-memory have been measured at 75 GB/s.-] {+this memory, 64% of the 119.5 GB/s peak (fact bw-dram).+}
model
out.card.4
Each memory package is about … lab cards carry is not recorded.
inference
out.card.5

## scale/card/part/lpddr#4
LPDDR4X memory package U21. Space for details; Enter zooms in. … the datasheet's 4,266 MT/s would give 136.5 GB/s. Tensor loads {+stream 76 GB/s+} from [-memory have been measured at 75 GB/s.-] {+this memory, 64% of the 119.5 GB/s peak (fact bw-dram).+}
model
out.card.4
Each memory package is about … lab cards carry is not recorded.
inference
out.card.5

## scale/card/part/vrm
The core regulator and its four inductors. Space for details; … out.card.7
Power arrives as 12 V at the card [-edge: at most-] {+edge; the vendor's power tree budgets+} 7.3 A, 88 W. [-The-] {+Under load the+} highest draw on record is 87.8 W; {+an idle card whose cooling failed drew 134 W before it dropped off the PCIe bus (aifoundry2, 2, 7 and 8 Oct 2026). With working cooling+} the cards idle at about [-19-36-] {+19-50+} W, depending on the card and its [-temperature.-] {+temperature (aifoundry1 card 1 idles highest: 42.7 W at 73 °C, 50 W at 80 °C).+}
documented
out.card.6

## scale/core/part/core.irf
Integer register file, documented. Space for details; Enter zooms in. … entries of 64 bits, built from latches, with two read [-ports-] {+ports, a third that reads only x31,+} and one write port.

 Zoom in:
The … 2 threads x 32: a latch register file, 2 read [-ports-] {+ports, a dedicated read port for x31+} and 1 write port.
documented
Erbium RTL
in.core.irf.1
[-64-] {+62+} x 64 = [-4,096-] {+3,968+} storage latches per [-minion;-] {+minion (x0 of each thread is wired to 0);+} at about 10 transistors each, some [-41,000-] {+40,000+} transistors before the read multiplexers.
inference
in.core.irf.2

## scale/core/part/lib.adder
Adder, documented. Space for details; Enter zooms in.
CORE … not waiting for a carry to ripple through 64 positions: {+the fastest+} prefix adders compute all the carries in about six levels … point at one for its source

 Parallel-prefix adders [-(Kogge-Stone, Sklansky, Brent-Kung)-] compute [-carries-] {+every carry in a tree of generate/propagate cells: Kogge-Stone and Sklansky+} in log2(N) {+levels, Brent-Kung in 2 log2(N) - 1+} levels [-of generate/propagate cells.-] {+with fewer cells and wires.+}
textbook
in.lib.adder.1
A parallel-prefix adder computes for … cells (G = Gi + Pi·Gj, P = Pi·Pj) of {+as few as+} log2 n levels, and forms each sum bit as p … cell driving at most two others.
textbook
tb.kogge

## scale/core/part/lib.booth
Booth encoder, documented. Space for details; Enter zooms in.
… each bit of a partial product is a multiplexer choosing [-x(j)-] {+x(j), x(j-1)+} or [-x(j-1),-] {+0,+} followed by an XOR with the sign.
textbook
… give -X, and 111 gives 0.
textbook
tb.booth.table

## scale/core/part/lib.icg
Clock gate, documented. Space for details; Enter zooms in.
… phase.
textbook
ml:l1:g.latch-write
An integrated clock gate [-latches-] {+passes+} the enable {+through a latch that is transparent+} while the clock is [-high-] {+low and holds it while the clock is high,+} and ANDs [-it-] {+the held enable+} with the clock: a block whose enable is low gets … and clock wires do not switch.
textbook
tb.icg

## scale/core/part/lib.latch
Latch, documented. Space for details; Enter zooms in.
CORE … V at 800); firmware limits 0.40-0.62 V.
measured
[-card not recorded-] {+aifoundry2+}
et.v-minion

## scale/core/part/lib.mux2
Two-way multiplexer, documented. Space for details; Enter zooms in.
… a mux tree (128:1 per output bit, e.g. seven 2:1 {+levels, or three 4:1+} levels [-or four 4:1 levels),-] {+and one 2:1),+} and only the nodes whose value changes spend energy, so read energy depends on the data.
textbook
ml:l1:g.latch-read

## scale/die.metal/part/fets
the transistors (fins and gates), documented. Space for details; Enter … of. A voltage on the gate decides whether current flows: {+in an n-type transistor,+} at 0 V the path along the fin is shut; … pulls a thin sheet of electrons into the fin, and [-current flows-] {+they flow+} from source to [-drain.-] {+drain (the current, by convention, from drain to source).+} The gate drapes over the fins on three sides.
… (high performance, 7.5 tracks, 10 fin pitches, 64 nm gate [-pitch); a 360 nm 9-track variant also exists.-] {+pitch).+}
outside source
fuse.wikichip.org ↗
n7.cells
N7 … V at 800); firmware limits 0.40-0.62 V.
measured
[-card not recorded-] {+aifoundry2+}
et.v-minion
At the minion rail's 0.517 V each … per °C (fit: 23.3 W x exp((T-80)/36)).
measured
[-card not recorded-] {+aifoundry2+}
et.leakage
By that fit, leakage doubles every 25 … same drive.
outside source
semiwiki.com ↗
n7.hpc

## scale/die/here
YOU ARE HERE · ≈ 26 mm · 10⁻² m … the map before the renaming and is superseded. Still open: [-whether-] {+which east-west handedness+} the silicon has [-this handedness or the-] {+(the+} published die [-plot's (I/O-] {+plot is not the mirror: it keeps the PCIe and I/O cells at the east end and swaps them, I/O+} then PCIe, [-the mirror);-] {+fact L24);+} a floorplan with labelled mesh stops, a die plot with …
Matmul efficiency ↗
mm-board-w
Board GFLOP/s per [-W,-] {+W (GOP/s per W for int8),+} L2 matmul fp32 / fp16 / int8: aifoundry2 161 / … east end of the top row. The published die plot [-draws-] {+(IEEE Micro 2022 Fig. 7, MPR Dec 2020 Fig. 1) also puts the PCIe and I/O cells at the east end of the top row, in the other order,+} I/O then [-PCIe, its-] {+PCIe (fact L24), and labels no memory shire: it is not the+} mirror [-image;-] {+image. Its own orientation is not stated, and+} no document in the open drop says which handedness the … L37).
model
no published page yet
fw.map-match

## scale/die/part/chip
The ET-SoC-1 die. Space for details; Enter zooms in.
… the map before the renaming and is superseded. Still open: [-whether-] {+which east-west handedness+} the silicon has [-this handedness or the-] {+(the+} published die [-plot's (I/O-] {+plot is not the mirror: it keeps the PCIe and I/O cells at the east end and swaps them, I/O+} then PCIe, [-the mirror);-] {+fact L24);+} a floorplan with labelled mesh stops, a die plot with …
Matmul efficiency ↗
mm-board-w
Board GFLOP/s per [-W,-] {+W (GOP/s per W for int8),+} L2 matmul fp32 / fp16 / int8: aifoundry2 161 / … east end of the top row. The published die plot [-draws-] {+(IEEE Micro 2022 Fig. 7, MPR Dec 2020 Fig. 1) also puts the PCIe and I/O cells at the east end of the top row, in the other order,+} I/O then [-PCIe, its-] {+PCIe (fact L24), and labels no memory shire: it is not the+} mirror [-image;-] {+image. Its own orientation is not stated, and+} no document in the open drop says which handedness the … L37).
model
no published page yet
fw.map-match

## scale/die/part/cshire
Shire 0, compute shire. Space for details; Enter zooms in. … the map before the renaming and is superseded. Still open: [-whether-] {+which east-west handedness+} the silicon has [-this handedness or the-] {+(the+} published die [-plot's (I/O-] {+plot is not the mirror: it keeps the PCIe and I/O cells at the east end and swaps them, I/O+} then PCIe, [-the mirror);-] {+fact L24);+} a floorplan with labelled mesh stops, a die plot with …
documented
Spatial temperature: a brief ↗
L121

## scale/die/part/cshire#10
Shire 9, compute shire. Space for details; Enter zooms in. … the map before the renaming and is superseded. Still open: [-whether-] {+which east-west handedness+} the silicon has [-this handedness or the-] {+(the+} published die [-plot's (I/O-] {+plot is not the mirror: it keeps the PCIe and I/O cells at the east end and swaps them, I/O+} then PCIe, [-the mirror);-] {+fact L24);+} a floorplan with labelled mesh stops, a die plot with …
documented
Spatial temperature: a brief ↗
L121

## scale/die/part/cshire#11
Shire 1, compute shire. Space for details; Enter zooms in. … the map before the renaming and is superseded. Still open: [-whether-] {+which east-west handedness+} the silicon has [-this handedness or the-] {+(the+} published die [-plot's (I/O-] {+plot is not the mirror: it keeps the PCIe and I/O cells at the east end and swaps them, I/O+} then PCIe, [-the mirror);-] {+fact L24);+} a floorplan with labelled mesh stops, a die plot with …
documented
Spatial temperature: a brief ↗
L121

## scale/die/part/cshire#12
Shire 13, compute shire. Space for details; Enter zooms in. … the map before the renaming and is superseded. Still open: [-whether-] {+which east-west handedness+} the silicon has [-this handedness or the-] {+(the+} published die [-plot's (I/O-] {+plot is not the mirror: it keeps the PCIe and I/O cells at the east end and swaps them, I/O+} then PCIe, [-the mirror);-] {+fact L24);+} a floorplan with labelled mesh stops, a die plot with …
documented
Spatial temperature: a brief ↗
L121

## scale/die/part/cshire#13
Shire 21, compute shire. Space for details; Enter zooms in. … the map before the renaming and is superseded. Still open: [-whether-] {+which east-west handedness+} the silicon has [-this handedness or the-] {+(the+} published die [-plot's (I/O-] {+plot is not the mirror: it keeps the PCIe and I/O cells at the east end and swaps them, I/O+} then PCIe, [-the mirror);-] {+fact L24);+} a floorplan with labelled mesh stops, a die plot with …
documented
Spatial temperature: a brief ↗
L121

## scale/die/part/cshire#14
Shire 29, compute shire. Space for details; Enter zooms in. … the map before the renaming and is superseded. Still open: [-whether-] {+which east-west handedness+} the silicon has [-this handedness or the-] {+(the+} published die [-plot's (I/O-] {+plot is not the mirror: it keeps the PCIe and I/O cells at the east end and swaps them, I/O+} then PCIe, [-the mirror);-] {+fact L24);+} a floorplan with labelled mesh stops, a die plot with …
documented
Spatial temperature: a brief ↗
L121

## scale/die/part/cshire#15
Shire 5, compute shire. Space for details; Enter zooms in. … the map before the renaming and is superseded. Still open: [-whether-] {+which east-west handedness+} the silicon has [-this handedness or the-] {+(the+} published die [-plot's (I/O-] {+plot is not the mirror: it keeps the PCIe and I/O cells at the east end and swaps them, I/O+} then PCIe, [-the mirror);-] {+fact L24);+} a floorplan with labelled mesh stops, a die plot with …
documented
Spatial temperature: a brief ↗
L121

## scale/die/part/cshire#16
Shire 25, compute shire. Space for details; Enter zooms in. … the map before the renaming and is superseded. Still open: [-whether-] {+which east-west handedness+} the silicon has [-this handedness or the-] {+(the+} published die [-plot's (I/O-] {+plot is not the mirror: it keeps the PCIe and I/O cells at the east end and swaps them, I/O+} then PCIe, [-the mirror);-] {+fact L24);+} a floorplan with labelled mesh stops, a die plot with …
documented
Spatial temperature: a brief ↗
L121

## scale/die/part/cshire#17
Shire 17, compute shire. Space for details; Enter zooms in. … the map before the renaming and is superseded. Still open: [-whether-] {+which east-west handedness+} the silicon has [-this handedness or the-] {+(the+} published die [-plot's (I/O-] {+plot is not the mirror: it keeps the PCIe and I/O cells at the east end and swaps them, I/O+} then PCIe, [-the mirror);-] {+fact L24);+} a floorplan with labelled mesh stops, a die plot with …
documented
Spatial temperature: a brief ↗
L121

## scale/die/part/cshire#18
Shire 14, compute shire. Space for details; Enter zooms in. … the map before the renaming and is superseded. Still open: [-whether-] {+which east-west handedness+} the silicon has [-this handedness or the-] {+(the+} published die [-plot's (I/O-] {+plot is not the mirror: it keeps the PCIe and I/O cells at the east end and swaps them, I/O+} then PCIe, [-the mirror);-] {+fact L24);+} a floorplan with labelled mesh stops, a die plot with …
documented
Spatial temperature: a brief ↗
L121

## scale/die/part/cshire#19
Shire 22, compute shire. Space for details; Enter zooms in. … the map before the renaming and is superseded. Still open: [-whether-] {+which east-west handedness+} the silicon has [-this handedness or the-] {+(the+} published die [-plot's (I/O-] {+plot is not the mirror: it keeps the PCIe and I/O cells at the east end and swaps them, I/O+} then PCIe, [-the mirror);-] {+fact L24);+} a floorplan with labelled mesh stops, a die plot with …
documented
Spatial temperature: a brief ↗
L121

## scale/die/part/cshire#2
Shire 8, compute shire. Space for details; Enter zooms in. … the map before the renaming and is superseded. Still open: [-whether-] {+which east-west handedness+} the silicon has [-this handedness or the-] {+(the+} published die [-plot's (I/O-] {+plot is not the mirror: it keeps the PCIe and I/O cells at the east end and swaps them, I/O+} then PCIe, [-the mirror);-] {+fact L24);+} a floorplan with labelled mesh stops, a die plot with …
documented
Spatial temperature: a brief ↗
L121

## scale/die/part/cshire#20
Shire 30, compute shire. Space for details; Enter zooms in. … the map before the renaming and is superseded. Still open: [-whether-] {+which east-west handedness+} the silicon has [-this handedness or the-] {+(the+} published die [-plot's (I/O-] {+plot is not the mirror: it keeps the PCIe and I/O cells at the east end and swaps them, I/O+} then PCIe, [-the mirror);-] {+fact L24);+} a floorplan with labelled mesh stops, a die plot with …
documented
Spatial temperature: a brief ↗
L121

## scale/die/part/cshire#21
Shire 6, compute shire. Space for details; Enter zooms in. … the map before the renaming and is superseded. Still open: [-whether-] {+which east-west handedness+} the silicon has [-this handedness or the-] {+(the+} published die [-plot's (I/O-] {+plot is not the mirror: it keeps the PCIe and I/O cells at the east end and swaps them, I/O+} then PCIe, [-the mirror);-] {+fact L24);+} a floorplan with labelled mesh stops, a die plot with …
documented
Spatial temperature: a brief ↗
L121

## scale/die/part/cshire#22
Shire 2, compute shire. Space for details; Enter zooms in. … the map before the renaming and is superseded. Still open: [-whether-] {+which east-west handedness+} the silicon has [-this handedness or the-] {+(the+} published die [-plot's (I/O-] {+plot is not the mirror: it keeps the PCIe and I/O cells at the east end and swaps them, I/O+} then PCIe, [-the mirror);-] {+fact L24);+} a floorplan with labelled mesh stops, a die plot with …
documented
Spatial temperature: a brief ↗
L121

## scale/die/part/cshire#23
Shire 10, compute shire. Space for details; Enter zooms in. … the map before the renaming and is superseded. Still open: [-whether-] {+which east-west handedness+} the silicon has [-this handedness or the-] {+(the+} published die [-plot's (I/O-] {+plot is not the mirror: it keeps the PCIe and I/O cells at the east end and swaps them, I/O+} then PCIe, [-the mirror);-] {+fact L24);+} a floorplan with labelled mesh stops, a die plot with …
documented
Spatial temperature: a brief ↗
L121

## scale/die/part/cshire#24
Shire 18, compute shire. Space for details; Enter zooms in. … the map before the renaming and is superseded. Still open: [-whether-] {+which east-west handedness+} the silicon has [-this handedness or the-] {+(the+} published die [-plot's (I/O-] {+plot is not the mirror: it keeps the PCIe and I/O cells at the east end and swaps them, I/O+} then PCIe, [-the mirror);-] {+fact L24);+} a floorplan with labelled mesh stops, a die plot with …
documented
Spatial temperature: a brief ↗
L121

## scale/die/part/cshire#25
Shire 26, compute shire. Space for details; Enter zooms in. … the map before the renaming and is superseded. Still open: [-whether-] {+which east-west handedness+} the silicon has [-this handedness or the-] {+(the+} published die [-plot's (I/O-] {+plot is not the mirror: it keeps the PCIe and I/O cells at the east end and swaps them, I/O+} then PCIe, [-the mirror);-] {+fact L24);+} a floorplan with labelled mesh stops, a die plot with …
documented
Spatial temperature: a brief ↗
L121

## scale/die/part/cshire#26
Shire 15, compute shire. Space for details; Enter zooms in. … the map before the renaming and is superseded. Still open: [-whether-] {+which east-west handedness+} the silicon has [-this handedness or the-] {+(the+} published die [-plot's (I/O-] {+plot is not the mirror: it keeps the PCIe and I/O cells at the east end and swaps them, I/O+} then PCIe, [-the mirror);-] {+fact L24);+} a floorplan with labelled mesh stops, a die plot with …
documented
Spatial temperature: a brief ↗
L121

## scale/die/part/cshire#27
Shire 7, compute shire. Space for details; Enter zooms in. … the map before the renaming and is superseded. Still open: [-whether-] {+which east-west handedness+} the silicon has [-this handedness or the-] {+(the+} published die [-plot's (I/O-] {+plot is not the mirror: it keeps the PCIe and I/O cells at the east end and swaps them, I/O+} then PCIe, [-the mirror);-] {+fact L24);+} a floorplan with labelled mesh stops, a die plot with …
documented
Spatial temperature: a brief ↗
L121

## scale/die/part/cshire#28
Shire 11, compute shire. Space for details; Enter zooms in. … the map before the renaming and is superseded. Still open: [-whether-] {+which east-west handedness+} the silicon has [-this handedness or the-] {+(the+} published die [-plot's (I/O-] {+plot is not the mirror: it keeps the PCIe and I/O cells at the east end and swaps them, I/O+} then PCIe, [-the mirror);-] {+fact L24);+} a floorplan with labelled mesh stops, a die plot with …
documented
Spatial temperature: a brief ↗
L121

## scale/die/part/cshire#29
Shire 19, compute shire. Space for details; Enter zooms in. … the map before the renaming and is superseded. Still open: [-whether-] {+which east-west handedness+} the silicon has [-this handedness or the-] {+(the+} published die [-plot's (I/O-] {+plot is not the mirror: it keeps the PCIe and I/O cells at the east end and swaps them, I/O+} then PCIe, [-the mirror);-] {+fact L24);+} a floorplan with labelled mesh stops, a die plot with …
documented
Spatial temperature: a brief ↗
L121

## scale/die/part/cshire#3
Shire 3, compute shire. Space for details; Enter zooms in. … the map before the renaming and is superseded. Still open: [-whether-] {+which east-west handedness+} the silicon has [-this handedness or the-] {+(the+} published die [-plot's (I/O-] {+plot is not the mirror: it keeps the PCIe and I/O cells at the east end and swaps them, I/O+} then PCIe, [-the mirror);-] {+fact L24);+} a floorplan with labelled mesh stops, a die plot with …
documented
Spatial temperature: a brief ↗
L121

## scale/die/part/cshire#30
Shire 27, compute shire. Space for details; Enter zooms in. … the map before the renaming and is superseded. Still open: [-whether-] {+which east-west handedness+} the silicon has [-this handedness or the-] {+(the+} published die [-plot's (I/O-] {+plot is not the mirror: it keeps the PCIe and I/O cells at the east end and swaps them, I/O+} then PCIe, [-the mirror);-] {+fact L24);+} a floorplan with labelled mesh stops, a die plot with …
documented
Spatial temperature: a brief ↗
L121

## scale/die/part/cshire#31
Shire 23, compute shire. Space for details; Enter zooms in. … the map before the renaming and is superseded. Still open: [-whether-] {+which east-west handedness+} the silicon has [-this handedness or the-] {+(the+} published die [-plot's (I/O-] {+plot is not the mirror: it keeps the PCIe and I/O cells at the east end and swaps them, I/O+} then PCIe, [-the mirror);-] {+fact L24);+} a floorplan with labelled mesh stops, a die plot with …
documented
Spatial temperature: a brief ↗
L121

## scale/die/part/cshire#32
Shire 31, compute shire. Space for details; Enter zooms in. … the map before the renaming and is superseded. Still open: [-whether-] {+which east-west handedness+} the silicon has [-this handedness or the-] {+(the+} published die [-plot's (I/O-] {+plot is not the mirror: it keeps the PCIe and I/O cells at the east end and swaps them, I/O+} then PCIe, [-the mirror);-] {+fact L24);+} a floorplan with labelled mesh stops, a die plot with …
documented
Spatial temperature: a brief ↗
L121

## scale/die/part/cshire#4
Shire 24, compute shire. Space for details; Enter zooms in. … the map before the renaming and is superseded. Still open: [-whether-] {+which east-west handedness+} the silicon has [-this handedness or the-] {+(the+} published die [-plot's (I/O-] {+plot is not the mirror: it keeps the PCIe and I/O cells at the east end and swaps them, I/O+} then PCIe, [-the mirror);-] {+fact L24);+} a floorplan with labelled mesh stops, a die plot with …
documented
Spatial temperature: a brief ↗
L121

## scale/die/part/cshire#5
Shire 16, compute shire. Space for details; Enter zooms in. … the map before the renaming and is superseded. Still open: [-whether-] {+which east-west handedness+} the silicon has [-this handedness or the-] {+(the+} published die [-plot's (I/O-] {+plot is not the mirror: it keeps the PCIe and I/O cells at the east end and swaps them, I/O+} then PCIe, [-the mirror);-] {+fact L24);+} a floorplan with labelled mesh stops, a die plot with …
documented
Spatial temperature: a brief ↗
L121

## scale/die/part/cshire#6
Shire 4, compute shire. Space for details; Enter zooms in. … the map before the renaming and is superseded. Still open: [-whether-] {+which east-west handedness+} the silicon has [-this handedness or the-] {+(the+} published die [-plot's (I/O-] {+plot is not the mirror: it keeps the PCIe and I/O cells at the east end and swaps them, I/O+} then PCIe, [-the mirror);-] {+fact L24);+} a floorplan with labelled mesh stops, a die plot with …
documented
Spatial temperature: a brief ↗
L121

## scale/die/part/cshire#7
Shire 12, compute shire. Space for details; Enter zooms in. … the map before the renaming and is superseded. Still open: [-whether-] {+which east-west handedness+} the silicon has [-this handedness or the-] {+(the+} published die [-plot's (I/O-] {+plot is not the mirror: it keeps the PCIe and I/O cells at the east end and swaps them, I/O+} then PCIe, [-the mirror);-] {+fact L24);+} a floorplan with labelled mesh stops, a die plot with …
documented
Spatial temperature: a brief ↗
L121

## scale/die/part/cshire#8
Shire 20, compute shire. Space for details; Enter zooms in. … the map before the renaming and is superseded. Still open: [-whether-] {+which east-west handedness+} the silicon has [-this handedness or the-] {+(the+} published die [-plot's (I/O-] {+plot is not the mirror: it keeps the PCIe and I/O cells at the east end and swaps them, I/O+} then PCIe, [-the mirror);-] {+fact L24);+} a floorplan with labelled mesh stops, a die plot with …
documented
Spatial temperature: a brief ↗
L121

## scale/die/part/cshire#9
Shire 28, compute shire. Space for details; Enter zooms in. … the map before the renaming and is superseded. Still open: [-whether-] {+which east-west handedness+} the silicon has [-this handedness or the-] {+(the+} published die [-plot's (I/O-] {+plot is not the mirror: it keeps the PCIe and I/O cells at the east end and swaps them, I/O+} then PCIe, [-the mirror);-] {+fact L24);+} a floorplan with labelled mesh stops, a die plot with …
documented
Spatial temperature: a brief ↗
L121

## scale/die/part/dram
LPDDR4X package, drawn beside memory shires 0 and 1 (pairing …

 16 channels of 16 bits, 32 GB on [-these cards,-] {+aifoundry2 and aifoundry3 (16 GB on aifoundry1 card 1),+} run at 3,733 MT/s: 119 GB/s peak, and the chip … above idle (89–141 over passes)
32 GB
on [-the card-] {+aifoundry2 and aifoundry3+}
Inferred or open here, and what would settle it … hierarchy ↗
dram.channels
32 GB of LPDDR4X on [-these V3 cards (Micron part):-] {+aifoundry2 and aifoundry3,+} 2 GB per [-channel;-] {+channel, and 16 GB on aifoundry1 card 1, 1 GB per channel, as the firmware reads the DRAM's density at boot and the runtime reports it. The vendor's document names its 32 GB V3 card a Micron part; which maker's parts the lab cards carry is not recorded. The datasheet gives+} the chip [-supports-] {+4 GB (2 Gb per channel) at full bandwidth up to 32 GB (16 Gb per channel); the PRM gives products+} 8 to 32 [-GB.-] {+GB, the range mprot's dram_size field addresses.+}
[-documented-] {+measured
three cards+}
Memory hierarchy ↗
dram.capacity
Datasheet rate: 4,266 … lat-dram-typical
Of a DRAM load's ~300 cycles only about [-25-28-] {+28+} are the DRAM chip's own timing (activate tRCD 18 ns, 19.3 ns read latency, [-one or-] {+the+} two 4.3 ns [-bursts);-] {+bursts of a 64-byte line);+} the rest is paths on the chip.
inference
… shires.
documented
no published page yet
L23

## scale/die/part/dram#2
LPDDR4X package, drawn beside memory shires 2 and 3 (pairing …

 16 channels of 16 bits, 32 GB on [-these cards,-] {+aifoundry2 and aifoundry3 (16 GB on aifoundry1 card 1),+} run at 3,733 MT/s: 119 GB/s peak, and the chip … above idle (89–141 over passes)
32 GB
on [-the card-] {+aifoundry2 and aifoundry3+}
Inferred or open here, and what would settle it … hierarchy ↗
dram.channels
32 GB of LPDDR4X on [-these V3 cards (Micron part):-] {+aifoundry2 and aifoundry3,+} 2 GB per [-channel;-] {+channel, and 16 GB on aifoundry1 card 1, 1 GB per channel, as the firmware reads the DRAM's density at boot and the runtime reports it. The vendor's document names its 32 GB V3 card a Micron part; which maker's parts the lab cards carry is not recorded. The datasheet gives+} the chip [-supports-] {+4 GB (2 Gb per channel) at full bandwidth up to 32 GB (16 Gb per channel); the PRM gives products+} 8 to 32 [-GB.-] {+GB, the range mprot's dram_size field addresses.+}
[-documented-] {+measured
three cards+}
Memory hierarchy ↗
dram.capacity
Datasheet rate: 4,266 … lat-dram-typical
Of a DRAM load's ~300 cycles only about [-25-28-] {+28+} are the DRAM chip's own timing (activate tRCD 18 ns, 19.3 ns read latency, [-one or-] {+the+} two 4.3 ns [-bursts);-] {+bursts of a 64-byte line);+} the rest is paths on the chip.
inference
… shires.
documented
no published page yet
L23

## scale/die/part/dram#3
LPDDR4X package, drawn beside memory shires 4 and 5 (pairing …

 16 channels of 16 bits, 32 GB on [-these cards,-] {+aifoundry2 and aifoundry3 (16 GB on aifoundry1 card 1),+} run at 3,733 MT/s: 119 GB/s peak, and the chip … above idle (89–141 over passes)
32 GB
on [-the card-] {+aifoundry2 and aifoundry3+}
Inferred or open here, and what would settle it … hierarchy ↗
dram.channels
32 GB of LPDDR4X on [-these V3 cards (Micron part):-] {+aifoundry2 and aifoundry3,+} 2 GB per [-channel;-] {+channel, and 16 GB on aifoundry1 card 1, 1 GB per channel, as the firmware reads the DRAM's density at boot and the runtime reports it. The vendor's document names its 32 GB V3 card a Micron part; which maker's parts the lab cards carry is not recorded. The datasheet gives+} the chip [-supports-] {+4 GB (2 Gb per channel) at full bandwidth up to 32 GB (16 Gb per channel); the PRM gives products+} 8 to 32 [-GB.-] {+GB, the range mprot's dram_size field addresses.+}
[-documented-] {+measured
three cards+}
Memory hierarchy ↗
dram.capacity
Datasheet rate: 4,266 … lat-dram-typical
Of a DRAM load's ~300 cycles only about [-25-28-] {+28+} are the DRAM chip's own timing (activate tRCD 18 ns, 19.3 ns read latency, [-one or-] {+the+} two 4.3 ns [-bursts);-] {+bursts of a 64-byte line);+} the rest is paths on the chip.
inference
… shires.
documented
no published page yet
L23

## scale/die/part/dram#4
LPDDR4X package, drawn beside memory shires 6 and 7 (pairing …

 16 channels of 16 bits, 32 GB on [-these cards,-] {+aifoundry2 and aifoundry3 (16 GB on aifoundry1 card 1),+} run at 3,733 MT/s: 119 GB/s peak, and the chip … above idle (89–141 over passes)
32 GB
on [-the card-] {+aifoundry2 and aifoundry3+}
Inferred or open here, and what would settle it … hierarchy ↗
dram.channels
32 GB of LPDDR4X on [-these V3 cards (Micron part):-] {+aifoundry2 and aifoundry3,+} 2 GB per [-channel;-] {+channel, and 16 GB on aifoundry1 card 1, 1 GB per channel, as the firmware reads the DRAM's density at boot and the runtime reports it. The vendor's document names its 32 GB V3 card a Micron part; which maker's parts the lab cards carry is not recorded. The datasheet gives+} the chip [-supports-] {+4 GB (2 Gb per channel) at full bandwidth up to 32 GB (16 Gb per channel); the PRM gives products+} 8 to 32 [-GB.-] {+GB, the range mprot's dram_size field addresses.+}
[-documented-] {+measured
three cards+}
Memory hierarchy ↗
dram.capacity
Datasheet rate: 4,266 … lat-dram-typical
Of a DRAM load's ~300 cycles only about [-25-28-] {+28+} are the DRAM chip's own timing (activate tRCD 18 ns, 19.3 ns read latency, [-one or-] {+the+} two 4.3 ns [-bursts);-] {+bursts of a 64-byte line);+} the rest is paths on the chip.
inference
… shires.
documented
no published page yet
L23

## scale/die/part/host
The host and the PCIe link. Space for details; Enter … the map before the renaming and is superseded. Still open: [-whether-] {+which east-west handedness+} the silicon has [-this handedness or the-] {+(the+} published die [-plot's (I/O-] {+plot is not the mirror: it keeps the PCIe and I/O cells at the east end and swaps them, I/O+} then PCIe, [-the mirror);-] {+fact L24);+} a floorplan with labelled mesh stops, a die plot with …
Matmul efficiency ↗
mm-board-w
Board GFLOP/s per [-W,-] {+W (GOP/s per W for int8),+} L2 matmul fp32 / fp16 / int8: aifoundry2 161 / … east end of the top row. The published die plot [-draws-] {+(IEEE Micro 2022 Fig. 7, MPR Dec 2020 Fig. 1) also puts the PCIe and I/O cells at the east end of the top row, in the other order,+} I/O then [-PCIe, its-] {+PCIe (fact L24), and labels no memory shire: it is not the+} mirror [-image;-] {+image. Its own orientation is not stated, and+} no document in the open drop says which handedness the … L37).
model
no published page yet
fw.map-match

## scale/die/part/inferred
What the drawing infers, and what would settle it: details … inferred: the LPDDR4X pairing (dashed), the die's east-west handedness, the [-routes' turning order,-] {+routes of all packets but the two kinds timed on 29 September (a load's reply and a store's data, between scratchpads),+} the inside of a shire, and the sizes. Each item … the map before the renaming and is superseded. Still open: [-whether-] {+which east-west handedness+} the silicon has [-this handedness or the-] {+(the+} published die [-plot's (I/O-] {+plot is not the mirror: it keeps the PCIe and I/O cells at the east end and swaps them, I/O+} then PCIe, [-the mirror);-] {+fact L24);+} a floorplan with labelled mesh stops, a die plot with … share of a load (memory shire panel)

 About [-25-28-] {+28+} of a DRAM load's cycles are the DRAM's own timing; … L3; tensor stores skip the L1 and L2 (energy manual; {+the+} PRM [-confirms only-] {+states that loads bypass the L1, pdf p.275, and that stores bypass+} the L1 [-bypass).-] {+and the L2, pdf p.306 and p.309).+} The L2 part is measured (E57, 29 September): a second … Two readings on the lab hosts that need root ↗

## scale/die/part/io
I/O shire. Space for details; Enter zooms in.
I/O … caption has I/O (purple, Maxion) fifth and PCIe (orange) sixth. [-The-] {+Both put the pair at the east end of the top row: the die plot swaps the+} two [-are-] {+cells (an east-west+} mirror [-images.-] {+would move them to the west end).+}
documented
Heat per millimetre ↗
L24
… east end of the top row. The published die plot [-draws-] {+(IEEE Micro 2022 Fig. 7, MPR Dec 2020 Fig. 1) also puts the PCIe and I/O cells at the east end of the top row, in the other order,+} I/O then [-PCIe, its-] {+PCIe (fact L24), and labels no memory shire: it is not the+} mirror [-image;-] {+image. Its own orientation is not stated, and+} no document in the open drop says which handedness the silicon has.
inference
no published page yet
die.handedness

## scale/die/part/master
Master shire, shire 32, from the firmware's map. Space for … too; which is which was not measured.
measured
[-card not recorded-] {+three cards+}
On-chip communication ↗
L31
Inferred identities: (0,4) … east end of the top row. The published die plot [-draws-] {+(IEEE Micro 2022 Fig. 7, MPR Dec 2020 Fig. 1) also puts the PCIe and I/O cells at the east end of the top row, in the other order,+} I/O then [-PCIe, its-] {+PCIe (fact L24), and labels no memory shire: it is not the+} mirror [-image;-] {+image. Its own orientation is not stated, and+} no document in the open drop says which handedness the silicon has.
inference
no published page yet
die.handedness

## scale/die/part/master#2
Spare shire, shire 33, from the firmware's map. Space for … too; which is which was not measured.
measured
[-card not recorded-] {+three cards+}
On-chip communication ↗
L31
Inferred identities: (0,4) … east end of the top row. The published die plot [-draws-] {+(IEEE Micro 2022 Fig. 7, MPR Dec 2020 Fig. 1) also puts the PCIe and I/O cells at the east end of the top row, in the other order,+} I/O then [-PCIe, its-] {+PCIe (fact L24), and labels no memory shire: it is not the+} mirror [-image;-] {+image. Its own orientation is not stated, and+} no document in the open drop says which handedness the silicon has.
inference
no published page yet
die.handedness

## scale/die/part/memshire
Memory shire 0. Space for details; Enter zooms in.
… fitted, the model is within ±3 cycles for 93–97% of [-loads-] {+lines+} on all three cards.

 91 + 12
cycles past the L3, per hop from the home shire
93–97%
of [-loads-] {+lines+} within ±3 cycles, three cards
about [-25–28-] {+28+}
cycles of them the DRAM chip (inferred)
Inferred … share of a load (memory shire panel)

 About [-25-28-] {+28+} of a DRAM load's cycles are the DRAM's own timing; … DRAM latency model is within ±3 cycles for 93-97% of [-loads-] {+lines (each line's fastest of three loads)+} on all three cards: aifoundry2 97.0%, aifoundry3 92.9%, aifoundry1-c1 94.4% … memory-shire constant (152 ns), the DRAM chip accounts for about [-25–28-] {+28+} cycles (activate tRCD 11 cycles = 18 ns, 19.3 ns read latency, [-one or-] {+the+} two 4.3 ns [-bursts);-] {+bursts of a 64-byte line); the rest,+} at most [-~63–66-] {+~63+} cycles [-(~105–110 ns) are-] {+(~105 ns), is the L3 home's miss handling (about 12 cycles by the spec: an L3 miss is 42 shire clocks against 30 for a hit) and+} the memory [-shire itself:-] {+shire:+} controller queue, PHY and the crossings between the 933 MHz … independently.
documented
no published page yet
fw.memshires

## scale/die/part/memshire#2
Memory shire 4. Space for details; Enter zooms in.
… fitted, the model is within ±3 cycles for 93–97% of [-loads-] {+lines+} on all three cards.

 91 + 12
cycles past the L3, per hop from the home shire
93–97%
of [-loads-] {+lines+} within ±3 cycles, three cards
about [-25–28-] {+28+}
cycles of them the DRAM chip (inferred)
Inferred … share of a load (memory shire panel)

 About [-25-28-] {+28+} of a DRAM load's cycles are the DRAM's own timing; … DRAM latency model is within ±3 cycles for 93-97% of [-loads-] {+lines (each line's fastest of three loads)+} on all three cards: aifoundry2 97.0%, aifoundry3 92.9%, aifoundry1-c1 94.4% … memory-shire constant (152 ns), the DRAM chip accounts for about [-25–28-] {+28+} cycles (activate tRCD 11 cycles = 18 ns, 19.3 ns read latency, [-one or-] {+the+} two 4.3 ns [-bursts);-] {+bursts of a 64-byte line); the rest,+} at most [-~63–66-] {+~63+} cycles [-(~105–110 ns) are-] {+(~105 ns), is the L3 home's miss handling (about 12 cycles by the spec: an L3 miss is 42 shire clocks against 30 for a hit) and+} the memory [-shire itself:-] {+shire:+} controller queue, PHY and the crossings between the 933 MHz … independently.
documented
no published page yet
fw.memshires

## scale/die/part/memshire#3
Memory shire 1. Space for details; Enter zooms in.
… fitted, the model is within ±3 cycles for 93–97% of [-loads-] {+lines+} on all three cards.

 91 + 12
cycles past the L3, per hop from the home shire
93–97%
of [-loads-] {+lines+} within ±3 cycles, three cards
about [-25–28-] {+28+}
cycles of them the DRAM chip (inferred)
Inferred … share of a load (memory shire panel)

 About [-25-28-] {+28+} of a DRAM load's cycles are the DRAM's own timing; … DRAM latency model is within ±3 cycles for 93-97% of [-loads-] {+lines (each line's fastest of three loads)+} on all three cards: aifoundry2 97.0%, aifoundry3 92.9%, aifoundry1-c1 94.4% … memory-shire constant (152 ns), the DRAM chip accounts for about [-25–28-] {+28+} cycles (activate tRCD 11 cycles = 18 ns, 19.3 ns read latency, [-one or-] {+the+} two 4.3 ns [-bursts);-] {+bursts of a 64-byte line); the rest,+} at most [-~63–66-] {+~63+} cycles [-(~105–110 ns) are-] {+(~105 ns), is the L3 home's miss handling (about 12 cycles by the spec: an L3 miss is 42 shire clocks against 30 for a hit) and+} the memory [-shire itself:-] {+shire:+} controller queue, PHY and the crossings between the 933 MHz … independently.
documented
no published page yet
fw.memshires

## scale/die/part/memshire#4
Memory shire 5. Space for details; Enter zooms in.
… fitted, the model is within ±3 cycles for 93–97% of [-loads-] {+lines+} on all three cards.

 91 + 12
cycles past the L3, per hop from the home shire
93–97%
of [-loads-] {+lines+} within ±3 cycles, three cards
about [-25–28-] {+28+}
cycles of them the DRAM chip (inferred)
Inferred … share of a load (memory shire panel)

 About [-25-28-] {+28+} of a DRAM load's cycles are the DRAM's own timing; … DRAM latency model is within ±3 cycles for 93-97% of [-loads-] {+lines (each line's fastest of three loads)+} on all three cards: aifoundry2 97.0%, aifoundry3 92.9%, aifoundry1-c1 94.4% … memory-shire constant (152 ns), the DRAM chip accounts for about [-25–28-] {+28+} cycles (activate tRCD 11 cycles = 18 ns, 19.3 ns read latency, [-one or-] {+the+} two 4.3 ns [-bursts);-] {+bursts of a 64-byte line); the rest,+} at most [-~63–66-] {+~63+} cycles [-(~105–110 ns) are-] {+(~105 ns), is the L3 home's miss handling (about 12 cycles by the spec: an L3 miss is 42 shire clocks against 30 for a hit) and+} the memory [-shire itself:-] {+shire:+} controller queue, PHY and the crossings between the 933 MHz … independently.
documented
no published page yet
fw.memshires

## scale/die/part/memshire#5
Memory shire 2. Space for details; Enter zooms in.
… fitted, the model is within ±3 cycles for 93–97% of [-loads-] {+lines+} on all three cards. The fit alone ties three places … per hop from the home shire
93–97%
of [-loads-] {+lines+} within ±3 cycles, three cards
about [-25–28-] {+28+}
cycles of them the DRAM chip (inferred)
Inferred … share of a load (memory shire panel)

 About [-25-28-] {+28+} of a DRAM load's cycles are the DRAM's own timing; … DRAM latency model is within ±3 cycles for 93-97% of [-loads-] {+lines (each line's fastest of three loads)+} on all three cards: aifoundry2 97.0%, aifoundry3 92.9%, aifoundry1-c1 94.4% … memory-shire constant (152 ns), the DRAM chip accounts for about [-25–28-] {+28+} cycles (activate tRCD 11 cycles = 18 ns, 19.3 ns read latency, [-one or-] {+the+} two 4.3 ns [-bursts);-] {+bursts of a 64-byte line); the rest,+} at most [-~63–66-] {+~63+} cycles [-(~105–110 ns) are-] {+(~105 ns), is the L3 home's miss handling (about 12 cycles by the spec: an L3 miss is 42 shire clocks against 30 for a hit) and+} the memory [-shire itself:-] {+shire:+} controller queue, PHY and the crossings between the 933 MHz … independently.
documented
no published page yet
fw.memshires

## scale/die/part/memshire#6
Memory shire 6. Space for details; Enter zooms in.
… fitted, the model is within ±3 cycles for 93–97% of [-loads-] {+lines+} on all three cards.

 91 + 12
cycles past the L3, per hop from the home shire
93–97%
of [-loads-] {+lines+} within ±3 cycles, three cards
about [-25–28-] {+28+}
cycles of them the DRAM chip (inferred)
Inferred … share of a load (memory shire panel)

 About [-25-28-] {+28+} of a DRAM load's cycles are the DRAM's own timing; … DRAM latency model is within ±3 cycles for 93-97% of [-loads-] {+lines (each line's fastest of three loads)+} on all three cards: aifoundry2 97.0%, aifoundry3 92.9%, aifoundry1-c1 94.4% … memory-shire constant (152 ns), the DRAM chip accounts for about [-25–28-] {+28+} cycles (activate tRCD 11 cycles = 18 ns, 19.3 ns read latency, [-one or-] {+the+} two 4.3 ns [-bursts);-] {+bursts of a 64-byte line); the rest,+} at most [-~63–66-] {+~63+} cycles [-(~105–110 ns) are-] {+(~105 ns), is the L3 home's miss handling (about 12 cycles by the spec: an L3 miss is 42 shire clocks against 30 for a hit) and+} the memory [-shire itself:-] {+shire:+} controller queue, PHY and the crossings between the 933 MHz … independently.
documented
no published page yet
fw.memshires

## scale/die/part/memshire#7
Memory shire 3. Space for details; Enter zooms in.
… fitted, the model is within ±3 cycles for 93–97% of [-loads-] {+lines+} on all three cards.

 91 + 12
cycles past the L3, per hop from the home shire
93–97%
of [-loads-] {+lines+} within ±3 cycles, three cards
about [-25–28-] {+28+}
cycles of them the DRAM chip (inferred)
Inferred … share of a load (memory shire panel)

 About [-25-28-] {+28+} of a DRAM load's cycles are the DRAM's own timing; … DRAM latency model is within ±3 cycles for 93-97% of [-loads-] {+lines (each line's fastest of three loads)+} on all three cards: aifoundry2 97.0%, aifoundry3 92.9%, aifoundry1-c1 94.4% … memory-shire constant (152 ns), the DRAM chip accounts for about [-25–28-] {+28+} cycles (activate tRCD 11 cycles = 18 ns, 19.3 ns read latency, [-one or-] {+the+} two 4.3 ns [-bursts);-] {+bursts of a 64-byte line); the rest,+} at most [-~63–66-] {+~63+} cycles [-(~105–110 ns) are-] {+(~105 ns), is the L3 home's miss handling (about 12 cycles by the spec: an L3 miss is 42 shire clocks against 30 for a hit) and+} the memory [-shire itself:-] {+shire:+} controller queue, PHY and the crossings between the 933 MHz … independently.
documented
no published page yet
fw.memshires

## scale/die/part/memshire#8
Memory shire 7. Space for details; Enter zooms in.
… fitted, the model is within ±3 cycles for 93–97% of [-loads-] {+lines+} on all three cards.

 91 + 12
cycles past the L3, per hop from the home shire
93–97%
of [-loads-] {+lines+} within ±3 cycles, three cards
about [-25–28-] {+28+}
cycles of them the DRAM chip (inferred)
Inferred … share of a load (memory shire panel)

 About [-25-28-] {+28+} of a DRAM load's cycles are the DRAM's own timing; … DRAM latency model is within ±3 cycles for 93-97% of [-loads-] {+lines (each line's fastest of three loads)+} on all three cards: aifoundry2 97.0%, aifoundry3 92.9%, aifoundry1-c1 94.4% … memory-shire constant (152 ns), the DRAM chip accounts for about [-25–28-] {+28+} cycles (activate tRCD 11 cycles = 18 ns, 19.3 ns read latency, [-one or-] {+the+} two 4.3 ns [-bursts);-] {+bursts of a 64-byte line); the rest,+} at most [-~63–66-] {+~63+} cycles [-(~105–110 ns) are-] {+(~105 ns), is the L3 home's miss handling (about 12 cycles by the spec: an L3 miss is 42 shire clocks against 30 for a hit) and+} the memory [-shire itself:-] {+shire:+} controller queue, PHY and the crossings between the 933 MHz … independently.
documented
no published page yet
fw.memshires

## scale/die/part/mesh
The mesh. Space for details; Enter zooms in.
NETWORK … aifoundry2. Routes are shortest paths in dimension order, measured on [-two-] {+three+} cards on 29 September: a request goes x first, then … master, spare, PCIe and I/O shires and route traffic too; [-which cell is which is not established.-] {+the firmware's maps name them (fact fw.grey-cells): (0,3) the master, shire 32; (5,3) the spare, 33; (0,4) the PCIe shire; (0,5) the I/O shire.+}
measured
three cards
On-chip communication ↗
mesh.empty-cells
The logical map [-appears to be-] {+is+} the die [-turned-] {+view transposed (x and y swapped:+} a [-quarter:-] {+quarter turn plus a mirror):+} in map orientation the memory shires sit above and below … documented
Heat per millimetre ↗
L102
Each {+minion, PCIe and I/O shire's+} mesh stop has 9 main-NoC routers (layers 0–8) plus one debug-NoC router; {+the NoC register map has 36 copies of layers 0–1 and 44 of layers 2–8, so the 8 memory shires' stops most likely have 7 (layers 2–8);+} routers have 8 ports (H, E, S, W, N, I, …
three cards
On-chip communication ↗
L91
[-There are no-] {+No+} NoC performance counters {+are documented+} in the [-PRM,-] {+PRM or used by+} the [-firmware or core-et; mesh-] {+firmware's code, and core-et has none; the firmware's generated register header does define transaction counters in every NoC bridge: two address- and command-filtered counters in each master bridge (*_m_am_cntr0/1 with ccmd0/1 and caddr, beside registers named latnum0/1 whose use it does not give) and one command-filtered counter in each slave bridge (*_s_as_cntr), undocumented, on the service processor's register bus and not tried here. Mesh+} transit is inferred from latency differences.
documented
Limits … east end of the top row. The published die plot [-draws-] {+(IEEE Micro 2022 Fig. 7, MPR Dec 2020 Fig. 1) also puts the PCIe and I/O cells at the east end of the top row, in the other order,+} I/O then [-PCIe, its-] {+PCIe (fact L24), and labels no memory shire: it is not the+} mirror [-image;-] {+image. Its own orientation is not stated, and+} no document in the open drop says which handedness the silicon has.
inference
no published page yet
die.handedness

## scale/die/part/pcie
PCIe shire. Space for details; Enter zooms in.
PCIE … caption has I/O (purple, Maxion) fifth and PCIe (orange) sixth. [-The-] {+Both put the pair at the east end of the top row: the die plot swaps the+} two [-are-] {+cells (an east-west+} mirror [-images.-] {+would move them to the west end).+}
documented
Heat per millimetre ↗
L24
… east end of the top row. The published die plot [-draws-] {+(IEEE Micro 2022 Fig. 7, MPR Dec 2020 Fig. 1) also puts the PCIe and I/O cells at the east end of the top row, in the other order,+} I/O then [-PCIe, its-] {+PCIe (fact L24), and labels no memory shire: it is not the+} mirror [-image;-] {+image. Its own orientation is not stated, and+} no document in the open drop says which handedness the … shire'.
documented
no published page yet
L25

## scale/dram/here
YOU ARE HERE · ≈ 12 mm · 10⁻² m … hierarchy ↗
dram.channels
32 GB of LPDDR4X on [-these V3 cards (Micron part):-] {+aifoundry2 and aifoundry3,+} 2 GB per [-channel;-] {+channel, and 16 GB on aifoundry1 card 1, 1 GB per channel, as the firmware reads the DRAM's density at boot and the runtime reports it. The vendor's document names its 32 GB V3 card a Micron part; which maker's parts the lab cards carry is not recorded. The datasheet gives+} the chip [-supports-] {+4 GB (2 Gb per channel) at full bandwidth up to 32 GB (16 Gb per channel); the PRM gives products+} 8 to 32 [-GB.-] {+GB, the range mprot's dram_size field addresses.+}
[-documented-] {+measured
three cards+}
Memory hierarchy ↗
dram.capacity
The firmware hard-codes … published page yet
dram.pkg-pairing
The exact LPDDR4X part [-(Micron-] {+(its maker and+} part number), its die density, the number of dies per … but no log has been captured.
unknown
ml:dram:dram.org.part

## scale/dram/part/tl
The command and data timeline of a load to a … refresh every 3.875 µs, lasting 280.7 ns. Compared with JEDEC [-LPDDR4-] {+LPDDR4's tables+} as [-recalled, not checked against the standard-] {+a Micron datasheet reproduces them+} (generic): the timings are close to its limits for this [-density and-] rate, tREFI {+is+} just under its 3.904 µs [-maximum,-] {+maximum+} and RL and WL are the [-fixed-] values for the [-rate.-] {+rate, except the all-bank refresh on the 32 GB cards: JEDEC asks 380 ns at 16 Gb per channel, and the 280.7 ns programmed needs a die rated faster, as Micron rates its 16 Gb single-channel die.+}

## scale/host/here
YOU ARE HERE · ≈ 45 cm · 10⁻¹ m … channel.
measured
card not recorded
out.host.1
[-aifoundry2's motherboard is a-] {+All three hosts' motherboards are+} Gigabyte Z590 AORUS [-MASTER, an ATX board of-] {+MASTER boards, ATX,+} 30.5 x 24.4 [-cm. The other two hosts'-] {+cm; aifoundry1 and aifoundry2 run+} BIOS [-versions (F5, F6) follow Gigabyte's naming, but their board models are not recorded.-] {+F5, aifoundry3 F6.+}
[-inference-] {+documented+}
out.host.2
aifoundry1 holds two ET cards, the other … turbo (its PL2), the i5-11600 at 65 W base. The [-whole-] ET [-card, at most-] {+card's+} 88 [-W, draws-] {+W budget is+} less than the bigger CPU's base [-power,-] {+power+} and about a third of its turbo peak.
documented … high and 140 mm deep.
outside source
out.host.8

## scale/host/part/board
The motherboard. Space for details; Enter zooms in.
HOST …
An Intel desktop processor under a tower cooler. The [-whole-] ET [-card, at most-] {+card’s+} 88 [-W, draws-] {+W budget is+} less than the bigger host processor’s 125 W base power; … turbo (its PL2), the i5-11600 at 65 W base. The [-whole-] ET [-card, at most-] {+card's+} 88 [-W, draws-] {+W budget is+} less than the bigger CPU's base [-power,-] {+power+} and about a third of its turbo peak.
documented … nm process, the host processors', is a FinFET process too: {+as first made (2014),+} fins 42 nm apart, gates 70 nm apart and the finest wires 52 nm apart (TSMC N7: 30, 57 and 40 [-nm).-] {+nm); its 14nm++ revision (2017), used for Intel's 14 nm desktop processors from Coffee Lake on, spaces the gates 84 nm apart.+}
outside source
host.intel14

## scale/host/part/cpu
The processor and its cooler. Space for details; Enter zooms …
An Intel desktop processor under a tower cooler. The [-whole-] ET [-card, at most-] {+card’s+} 88 [-W, draws-] {+W budget is+} less than the bigger host processor’s 125 W base power; … turbo (its PL2), the i5-11600 at 65 W base. The [-whole-] ET [-card, at most-] {+card's+} 88 [-W, draws-] {+W budget is+} less than the bigger CPU's base [-power,-] {+power+} and about a third of its turbo peak.
documented … nm process, the host processors', is a FinFET process too: {+as first made (2014),+} fins 42 nm apart, gates 70 nm apart and the finest wires 52 nm apart (TSMC N7: 30, 57 and 40 [-nm).-] {+nm); its 14nm++ revision (2017), used for Intel's 14 nm desktop processors from Coffee Lake on, spaces the gates 84 nm apart.+}
outside source
host.intel14

## scale/host/part/tocard
The ET card: zoom in. Space for details; Enter zooms … facts (2): point at one for its source

 [-aifoundry2's motherboard is a-] {+All three hosts' motherboards are+} Gigabyte Z590 AORUS [-MASTER, an ATX board of-] {+MASTER boards, ATX,+} 30.5 x 24.4 [-cm. The other two hosts'-] {+cm; aifoundry1 and aifoundry2 run+} BIOS [-versions (F5, F6) follow Gigabyte's naming, but their board models are not recorded.-] {+F5, aifoundry3 F6.+}
[-inference-] {+documented+}
out.host.2
Each card's 8-lane PCIe 4.0 link goes … which has 20 PCIe 4.0 lanes.
inference
out.host.4

## scale/io/part/io.pvt
PVT controllers, documented. Space for details; Enter zooms in.
… process detectors and 36 temperature sensors (one each per minion {+shire, the PCIe+} shire and the I/O [-shire)-] {+shire, as the manual's Figure 1-3 draws them)+} and 8 voltage-monitor blocks of up to 16 sense points (128 in all), read through five PVT controllers. (The [-manual's own count does not add up: 34 minion shires-] {+RTL removed the PCIe shire's pair, "Pshire no longer has ts/pd (RTLMIN-3619)", core-et rtl/inc/pvt_defines.vh:16-26,+} and the [-I/O shire make 35, and it does not say where the 36th sensor sits.)-] {+firmware reads 35: fact L121.)+}
documented
in.io.pvt.1
35 temperature sensors on the …
documented
Spatial temperature: a brief ↗
temp-sensors

## scale/l1d.row/here
YOU ARE HERE · ≈ 32 µm · 10⁻⁵ m … a mux tree (128:1 per output bit, e.g. seven 2:1 {+levels, or three 4:1+} levels [-or four 4:1 levels),-] {+and one 2:1),+} and only the nodes whose value changes spend energy, so … holds steady for the whole phase.
textbook
ml:l1:g.latch-write

## scale/laniakea/part/to-localgroup
the Local Group: zoom in. Space for details; Enter zooms … (134 in one count), most of them faint dwarf galaxies; [-counted that way-] {+judged by density matching and the potential surface of its parent structure, the Local Sheet,+} the group is about 5.1 Mpc (17 million light-years) across. … which is part of Laniakea.
outside source
out.localgroup.6

## scale/lib.adder/here
YOU ARE HERE · ≈ 30 µm · 10⁻⁵ m … not waiting for a carry to ripple through 64 positions: {+the fastest+} prefix adders compute all the carries in about six levels … point at one for its source

 Parallel-prefix adders [-(Kogge-Stone, Sklansky, Brent-Kung)-] compute [-carries-] {+every carry in a tree of generate/propagate cells: Kogge-Stone and Sklansky+} in log2(N) {+levels, Brent-Kung in 2 log2(N) - 1+} levels [-of generate/propagate cells.-] {+with fewer cells and wires.+}
textbook
in.lib.adder.1
A parallel-prefix adder computes for … cells (G = Gi + Pi·Gj, P = Pi·Pj) of {+as few as+} log2 n levels, and forms each sum bit as p … cell driving at most two others.
textbook
tb.kogge

## scale/lib.adder/part/pfx1
Carry level 1: each carry cell joins its column with … cells (G = Gi + Pi·Gj, P = Pi·Pj) of {+as few as+} log2 n levels, and forms each sum bit as p … cell driving at most two others.
textbook
tb.kogge

## scale/lib.adder/part/pfx2
Carry level 2: each carry cell joins its column with … cells (G = Gi + Pi·Gj, P = Pi·Pj) of {+as few as+} log2 n levels, and forms each sum bit as p … cell driving at most two others.
textbook
tb.kogge

## scale/lib.adder/part/pfx4
Carry level 3: each carry cell joins its column with … cells (G = Gi + Pi·Gj, P = Pi·Pj) of {+as few as+} log2 n levels, and forms each sum bit as p … cell driving at most two others.
textbook
tb.kogge

## scale/lib.adder/part/pg
Generate and propagate: per bit, g = a·b and p … An XOR and a NAND with an inverter per bit. {+Bit 0 also takes the carry in: g0 = a0·b0 + p0·cin (the textbook enters the carry in as one more column on the right, with G = cin and P = 0), so every carry the tree computes includes it.+}

 Zoom in:
The XOR / XNOR gate … cells (G = Gi + Pi·Gj, P = Pi·Pj) of {+as few as+} log2 n levels, and forms each sum bit as p … all n bits one after another.
textbook
tb.prefix

## scale/lib.adder/part/sum
The sums: each bit is p ⊕ the carry from … The sum bits

 Each sum bit is its {+own+} propagate p {+(the thin line from its g p box, past the tree)+} XOR the carry coming in from all the bits to … cells (G = Gi + Pi·Gj, P = Pi·Pj) of {+as few as+} log2 n levels, and forms each sum bit as p … all n bits one after another.
textbook
tb.prefix

## scale/lib.aoi21/here
YOU ARE HERE · ≈ 300 nm · 10⁻⁷ m … cells (G = Gi + Pi·Gj, P = Pi·Pj) of {+as few as+} log2 n levels, and forms each sum bit as p … frames it (an order of magnitude).
inference
size.lib.aoi21

## scale/lib.aoi21/part/gtable
The truth table. Space for details; Enter zooms in.
… cells (G = Gi + Pi·Gj, P = Pi·Pj) of {+as few as+} log2 n levels, and forms each sum bit as p … frames it (an order of magnitude).
inference
size.lib.aoi21

## scale/lib.aoi21/part/onefet
One transistor, generic. Space for details; Enter zooms in.
… of. A voltage on the gate decides whether current flows: {+in an n-type transistor,+} at 0 V the path along the fin is shut; … pulls a thin sheet of electrons into the fin, and [-current flows-] {+they flow+} from source to [-drain.-] {+drain (the current, by convention, from drain to source).+} The gate drapes over the fins on three sides.
… (high performance, 7.5 tracks, 10 fin pitches, 64 nm gate [-pitch); a 360 nm 9-track variant also exists.-] {+pitch).+}
outside source
fuse.wikichip.org ↗
n7.cells
N7 … V at 800); firmware limits 0.40-0.62 V.
measured
[-card not recorded-] {+aifoundry2+}
et.v-minion
At the minion rail's 0.517 V each … per °C (fit: 23.3 W x exp((T-80)/36)).
measured
[-card not recorded-] {+aifoundry2+}
et.leakage
By that fit, leakage doubles every 25 … same drive.
outside source
semiwiki.com ↗
n7.hpc

## scale/lib.booth/here
YOU ARE HERE · ≈ 500 nm · 10⁻⁷ m … each bit of a partial product is a multiplexer choosing [-x(j)-] {+x(j), x(j-1)+} or [-x(j-1),-] {+0,+} followed by an XOR with the sign.
textbook
… give -X, and 111 gives 0.
textbook
tb.booth.table

## scale/lib.booth/part/enc
The encoders: each looks at three overlapping bits of the … each bit of a partial product is a multiplexer choosing [-x(j)-] {+x(j), x(j-1)+} or [-x(j-1),-] {+0,+} followed by an XOR with the sign.
textbook
… give -X, and 111 gives 0.
textbook
tb.booth.table

## scale/lib.booth/part/neg
The negation: per bit, an XOR inverts the bit when … each bit of a partial product is a multiplexer choosing [-x(j)-] {+x(j), x(j-1)+} or [-x(j-1),-] {+0,+} followed by an XOR with the sign.
textbook
tb.booth

## scale/lib.booth/part/sel
The row's selectors: per bit, a [-2:1-] multiplexer picks [-X or-] {+X,+} 2X (X shifted one [-place).-] {+place) or 0.+} Space for details; Enter zooms in.
BOOTH ENCODER · PART

 The selectors

 For each bit of the row a [-2:1-] multiplexer picks bit j of X (for ±X) or bit j-1 (for ±2X: X shifted one [-place),-] {+place). The encoder raises one of its two select lines,+} or neither [-(for 0).-] {+for a 0 row, and then the bit is 0: an AND-OR gate, not a plain 2:1 multiplexer, which always passes one of its inputs.+}

 Zoom in:
The two-way multiplexer (double-click)
… each bit of a partial product is a multiplexer choosing [-x(j)-] {+x(j), x(j-1)+} or [-x(j-1),-] {+0,+} followed by an XOR with the sign.
textbook
tb.booth

## scale/lib.channel/here
YOU ARE HERE · 16.5 nm · 10⁻⁸ m
… 52 nm fin about 383 planes (96 unit cells).
[-model-] {+inference+}
si.planes-width
When a single fin is on at … easily than holes (mobility up to 1,400 vs 450 cm²/V·s); {+in a transistor's channel+} electrons saturate at about 8e6 cm/s, so crossing a 16.5 … from the heavily doped source.
inference
p.atom.9
[-The same-] {+TSMC's FinFET+} patent [-dopes the wells under-] {+(US 11,107,923) implants its wells, in+} the fins {+or the substrate,+} at {+up to 10^18 per cm3 for n-wells (10^16 to 10^18) and up to 10^20 for p-wells (10^17 to 10^20). At a bulk FinFET's usual fin doping,+} 10^16 to 10^18 per [-cm3. At those levels-] {+cm3,+} a 6 x 16.5 x 52 nm channel would hold … all the silicon that actually switches.
inference
p.atom.10

## scale/lib.channel/part/chan
The channel under the gate. Space for details; Enter zooms … 52 nm fin about 383 planes (96 unit cells).
[-model-] {+inference+}
si.planes-width
When a single fin is on at … easily than holes (mobility up to 1,400 vs 450 cm²/V·s); {+in a transistor's channel+} electrons saturate at about 8e6 cm/s, so crossing a 16.5 … from the heavily doped source.
inference
p.atom.9
[-The same-] {+TSMC's FinFET+} patent [-dopes the wells under-] {+(US 11,107,923) implants its wells, in+} the fins {+or the substrate,+} at {+up to 10^18 per cm3 for n-wells (10^16 to 10^18) and up to 10^20 for p-wells (10^17 to 10^20). At a bulk FinFET's usual fin doping,+} 10^16 to 10^18 per [-cm3. At those levels-] {+cm3,+} a 6 x 16.5 x 52 nm channel would hold … all the silicon that actually switches.
inference
p.atom.10

## scale/lib.channel/part/dopant
A phosphorus atom of the source. Space for details; Enter … (2 kT = 52 meV), so nearly every dopant atom {+alone in a silicon site+} has given up (or taken) its electron.
textbook
… is the stated goal.
outside source
p.dopant.6
[-The same-] {+TSMC's FinFET+} patent [-dopes the wells under-] {+(US 11,107,923) implants its wells, in+} the fins {+or the substrate,+} at {+up to 10^18 per cm3 for n-wells (10^16 to 10^18) and up to 10^20 for p-wells (10^17 to 10^20). At a bulk FinFET's usual fin doping,+} 10^16 to 10^18 per [-cm3. At those levels-] {+cm3,+} a 6 x 16.5 x 52 nm channel would hold … about 50 meV, about twice kT at room temperature, so [-dopants-] {+dopant atoms alone in silicon sites+} are almost all ionised.
textbook
chu.berkeley.edu ↗
… electrons; the dopants' 50 meV is only 2 kT, so [-they are all-] {+nearly every dopant atom alone in a silicon site is+} ionised.
model
physics.nist.gov ↗
el.kt

## scale/lib.channel/part/lattice
A patch of the silicon crystal. Space for details; Enter … 52 nm fin about 383 planes (96 unit cells).
[-model-] {+inference+}
si.planes-width
Silicon's band gap is 1.12 eV at … electrons; the dopants' 50 meV is only 2 kT, so [-they are all-] {+nearly every dopant atom alone in a silicon site is+} ionised.
model
physics.nist.gov ↗
el.kt
Pure … about 50 meV, about twice kT at room temperature, so [-dopants-] {+dopant atoms alone in silicon sites+} are almost all ionised.
textbook
chu.berkeley.edu ↗
… easily than holes (mobility up to 1,400 vs 450 cm²/V·s); {+in a transistor's channel+} electrons saturate at about 8e6 cm/s, so crossing a 16.5 … standard atomic weight is 28.084-28.086.
outside source
p.atom.6

## scale/lib.channel/part/sd
The source and the drain. Space for details; Enter zooms … 52 nm fin about 383 planes (96 unit cells).
[-model-] {+inference+}
si.planes-width
When a single fin is on at … easily than holes (mobility up to 1,400 vs 450 cm²/V·s); {+in a transistor's channel+} electrons saturate at about 8e6 cm/s, so crossing a 16.5 … from the heavily doped source.
inference
p.atom.9
[-The same-] {+TSMC's FinFET+} patent [-dopes the wells under-] {+(US 11,107,923) implants its wells, in+} the fins {+or the substrate,+} at {+up to 10^18 per cm3 for n-wells (10^16 to 10^18) and up to 10^20 for p-wells (10^17 to 10^20). At a bulk FinFET's usual fin doping,+} 10^16 to 10^18 per [-cm3. At those levels-] {+cm3,+} a 6 x 16.5 x 52 nm channel would hold … all the silicon that actually switches.
inference
p.atom.10

## scale/lib.cmp42/part/fa1
full adder 1, [-documented.-] {+generic.+} Space for details; Enter zooms in.
4:2 COMPRESSOR · … adder": 24 plus two output inverters).
textbook
in.lib.fa.1

## scale/lib.cmp42/part/fa2
full adder 2, [-documented.-] {+generic.+} Space for details; Enter zooms in.
4:2 COMPRESSOR · … adder": 24 plus two output inverters).
textbook
in.lib.fa.1

## scale/lib.decoder/part/drv
The row drivers: wide inverters that raise the selected line. … (6 tracks of 40 nm); high-performance cells 300 nm.
[-inference-] {+outside source+}
in.lib.inverter.2
A MOSFET is a voltage-controlled switch: the … (high performance, 7.5 tracks, 10 fin pitches, 64 nm gate [-pitch); a 360 nm 9-track variant also exists.-] {+pitch).+}
outside source
fuse.wikichip.org ↗
n7.cells
A … and parallel transistors in one stage.
textbook
tb.gates

## scale/lib.decoder/part/inv
The inverters: each address bit and its complement. Space for … (6 tracks of 40 nm); high-performance cells 300 nm.
[-inference-] {+outside source+}
in.lib.inverter.2
A MOSFET is a voltage-controlled switch: the … (high performance, 7.5 tracks, 10 fin pitches, 64 nm gate [-pitch); a 360 nm 9-track variant also exists.-] {+pitch).+}
outside source
fuse.wikichip.org ↗
n7.cells
A … and parallel transistors in one stage.
textbook
tb.gates

## scale/lib.dramcell/here
YOU ARE HERE · ≈ 100 nm · 10⁻⁷ m … (the card's VDDQLP, the LPDDR4X's I/O VDDQ).
measured
[-card not recorded-] {+aifoundry2+}
et.v-other

## scale/lib.ecc/part/enc
The check bits: each an XOR tree over the [-data-] {+other+} bits marked in its row. Space for details; Enter zooms in.
ECC · PART

 The parity-check matrix

 Each row [-is-] {+makes+} one check [-bit:-] {+bit,+} the XOR of the [-data-] {+other+} bits marked in [-it.-] {+it: data bits in the first four rows; in the fifth, the overall parity, all eight data bits and the first four check bits.+} Every [-data-] bit is in a different combination of rows, so a … check bits, a (72, 64) code.
textbook
tb.ecc

## scale/lib.ecc/part/syn
syndrome, generic. Space for details; Enter zooms in.
ECC … and XORed with the stored ones: all zeros means no [-error;-] {+error detected;+} otherwise the pattern names the bit.

 Zoom in: … check bits, a (72, 64) code.
textbook
tb.ecc

## scale/lib.fa/part/xor1
XOR gate 1, [-documented.-] {+generic.+} Space for details; Enter zooms in.
FULL ADDER · … source to drain.
textbook
chu.berkeley.edu ↗
el.switch

## scale/lib.fifo/here
YOU ARE HERE · ≈ 20 µm · 10⁻⁵ m … addressed by a write pointer and a read pointer, two [-counters; comparing-] {+counters. Equal pointers mean empty or full; one way to tell them apart is a pointer one bit wider than+} the [-pointers tells a full-] {+address: equal in every bit, the+} queue [-from an empty one.-] {+is empty; equal but for that extra bit, it is full.+}
textbook
tb.fifo
Queue (first in, first out): … frames it (an order of magnitude).
inference
size.lib.fifo

## scale/lib.fifo/part/cmp
Full and empty: the two pointers compared. Space for details; Enter zooms in.
QUEUE · PART

 [-Equality comparator-] {+Full or empty+}

 [-Says whether-] {+Equal pointers mean the queue is empty or full. Each pointer counts one bit beyond the address, so the+} two [-numbers are equal:-] {+can be told apart: equal in every bit, the queue is empty; equal but for that extra bit, the writer has gone round once more than the reader and the queue is full. An equality comparator on the address bits and+} an [-XNOR gate per bit, then a tree of gates that is 1 only if every bit agreed. A cache uses one per way to find its hit.-] {+XOR on the extra bits decide it.+}

 Zoom in:
The equality comparator (double-click)
More detail and the sources

 The facts [-(2):-] {+(1):+} point at one for its source

 [-An equality comparator XNORs each pair of bits-] {+A first-in, first-out queue is a small memory addressed by a write pointer+} and [-combines-] {+a read pointer, two counters. Equal pointers mean empty or full; one way to tell them apart is a pointer one bit wider than+} the [-results-] {+address: equal+} in [-a tree of NAND and NOR gates:-] {+every bit,+} the [-output-] {+queue+} is [-1 only when every pair agrees.-] {+empty; equal but for that extra bit, it is full.+}
textbook
[-tb.compare
Equality comparator: about 2 µm across, the width of the view that frames it (an order of magnitude).
inference
size.lib.cmpeq-] {+tb.fifo+}

## scale/lib.fin/here
YOU ARE HERE · 52 nm · 10⁻⁸ m
… gate and filled with W or Al; their work functions [-(about-] {+set the threshold: about+} 4.1 and 4.85 [-eV) set-] {+eV in+} the [-threshold.-] {+planar 45 nm gates, while a FinFET, its channel undoped, needs about 4.4 and 4.85 eV.+}
textbook
doi.org ↗
gate.metals
In a … metal layers.
outside source
nccavs-usergroups.avs.org ↗
cmp.gf7

## scale/lib.fin/part/fin0
A fin. Space for details; Enter zooms in.
FIN … gate and filled with W or Al; their work functions [-(about-] {+set the threshold: about+} 4.1 and 4.85 [-eV) set-] {+eV in+} the [-threshold.-] {+planar 45 nm gates, while a FinFET, its channel undoped, needs about 4.4 and 4.85 eV.+}
textbook
doi.org ↗
gate.metals
In a … metal layers.
outside source
nccavs-usergroups.avs.org ↗
cmp.gf7

## scale/lib.fin/part/fin2
A fin. Space for details; Enter zooms in.
FIN … gate and filled with W or Al; their work functions [-(about-] {+set the threshold: about+} 4.1 and 4.85 [-eV) set-] {+eV in+} the [-threshold.-] {+planar 45 nm gates, while a FinFET, its channel undoped, needs about 4.4 and 4.85 eV.+}
textbook
doi.org ↗
gate.metals
In a … metal layers.
outside source
nccavs-usergroups.avs.org ↗
cmp.gf7

## scale/lib.fin/part/gatestack
The gate stack: metal on a thin high-k oxide, over … 52 nm fin about 383 planes (96 unit cells).
[-model-] {+inference+}
si.planes-width
When a single fin is on at … easily than holes (mobility up to 1,400 vs 450 cm²/V·s); {+in a transistor's channel+} electrons saturate at about 8e6 cm/s, so crossing a 16.5 … from the heavily doped source.
inference
p.atom.9
[-The same-] {+TSMC's FinFET+} patent [-dopes the wells under-] {+(US 11,107,923) implants its wells, in+} the fins {+or the substrate,+} at {+up to 10^18 per cm3 for n-wells (10^16 to 10^18) and up to 10^20 for p-wells (10^17 to 10^20). At a bulk FinFET's usual fin doping,+} 10^16 to 10^18 per [-cm3. At those levels-] {+cm3,+} a 6 x 16.5 x 52 nm channel would hold … all the silicon that actually switches.
inference
p.atom.10

## scale/lib.fin/part/thefin
The fin under the gate: the channel. Space for details; … 52 nm fin about 383 planes (96 unit cells).
[-model-] {+inference+}
si.planes-width
When a single fin is on at … easily than holes (mobility up to 1,400 vs 450 cm²/V·s); {+in a transistor's channel+} electrons saturate at about 8e6 cm/s, so crossing a 16.5 … from the heavily doped source.
inference
p.atom.9
[-The same-] {+TSMC's FinFET+} patent [-dopes the wells under-] {+(US 11,107,923) implants its wells, in+} the fins {+or the substrate,+} at {+up to 10^18 per cm3 for n-wells (10^16 to 10^18) and up to 10^20 for p-wells (10^17 to 10^20). At a bulk FinFET's usual fin doping,+} 10^16 to 10^18 per [-cm3. At those levels-] {+cm3,+} a 6 x 16.5 x 52 nm channel would hold … all the silicon that actually switches.
inference
p.atom.10

## scale/lib.finfet/here
YOU ARE HERE · 57 nm · 10⁻⁸ m
… of. A voltage on the gate decides whether current flows: {+in an n-type transistor,+} at 0 V the path along the fin is shut; … pulls a thin sheet of electrons into the fin, and [-current flows-] {+they flow+} from source to [-drain.-] {+drain (the current, by convention, from drain to source).+} The gate drapes over the fins on three sides.
… (high performance, 7.5 tracks, 10 fin pitches, 64 nm gate [-pitch); a 360 nm 9-track variant also exists.-] {+pitch).+}
outside source
fuse.wikichip.org ↗
n7.cells
N7 … V at 800); firmware limits 0.40-0.62 V.
measured
[-card not recorded-] {+aifoundry2+}
et.v-minion
At the minion rail's 0.517 V each … per °C (fit: 23.3 W x exp((T-80)/36)).
measured
[-card not recorded-] {+aifoundry2+}
et.leakage
By that fit, leakage doubles every 25 … same drive.
outside source
semiwiki.com ↗
n7.hpc

## scale/lib.finfet/part/cell
One standard cell row: 240 nm tall. Space for details; … (high performance, 7.5 tracks, 10 fin pitches, 64 nm gate [-pitch); a 360 nm 9-track variant also exists.-] {+pitch).+}
outside source
fuse.wikichip.org ↗
n7.cells
In … about 65).
outside source
fuse.wikichip.org ↗
n7.density-hd

## scale/lib.finfet/part/contacts
Source and drain contacts. Space for details; Enter zooms in. … (high performance, 7.5 tracks, 10 fin pitches, 64 nm gate [-pitch); a 360 nm 9-track variant also exists.-] {+pitch).+}
outside source
fuse.wikichip.org ↗
n7.cells
In … about 65).
outside source
fuse.wikichip.org ↗
n7.density-hd

## scale/lib.finfet/part/devring
One {+n-type+} transistor: a gate over two fins. Space for details; Enter zooms in.
FINFET · PART

 One {+n-type+} transistor

 Explore this in 3D ↗

 … of. A voltage on the gate decides whether current flows: {+in an n-type transistor,+} at 0 V the path along the fin is shut; … pulls a thin sheet of electrons into the fin, and [-current flows-] {+they flow+} from source to [-drain.-] {+drain (the current, by convention, from drain to source).+} The gate drapes over the fins on three sides.
… (high performance, 7.5 tracks, 10 fin pitches, 64 nm gate [-pitch); a 360 nm 9-track variant also exists.-] {+pitch).+}
outside source
fuse.wikichip.org ↗
n7.cells
N7 … V at 800); firmware limits 0.40-0.62 V.
measured
[-card not recorded-] {+aifoundry2+}
et.v-minion
At the minion rail's 0.517 V each … per °C (fit: 23.3 W x exp((T-80)/36)).
measured
[-card not recorded-] {+aifoundry2+}
et.leakage
By that fit, leakage doubles every 25 … same drive.
outside source
semiwiki.com ↗
n7.hpc

## scale/lib.finfet/part/fins
The fins: walls of silicon the current runs along. Space … (high performance, 7.5 tracks, 10 fin pitches, 64 nm gate [-pitch); a 360 nm 9-track variant also exists.-] {+pitch).+}
outside source
fuse.wikichip.org ↗
n7.cells
In … about 65).
outside source
fuse.wikichip.org ↗
n7.density-hd

## scale/lib.finfet/part/gates
The gates: lines of metal over the fins. Space for … (high performance, 7.5 tracks, 10 fin pitches, 64 nm gate [-pitch); a 360 nm 9-track variant also exists.-] {+pitch).+}
outside source
fuse.wikichip.org ↗
n7.cells
In … about 65).
outside source
fuse.wikichip.org ↗
n7.density-hd

## scale/lib.flipflop/part/master
master latch, [-documented.-] {+generic.+} Space for details; Enter zooms in.
FLIP-FLOP · PART … V at 800); firmware limits 0.40-0.62 V.
measured
[-card not recorded-] {+aifoundry2+}
et.v-minion

## scale/lib.flipflop/part/slave
slave latch, [-documented.-] {+generic.+} Space for details; Enter zooms in.
FLIP-FLOP · PART … V at 800); firmware limits 0.40-0.62 V.
measured
[-card not recorded-] {+aifoundry2+}
et.v-minion

## scale/lib.icg/here
YOU ARE HERE · ≈ 600 nm · 10⁻⁷ m … phase.
textbook
ml:l1:g.latch-write
An integrated clock gate [-latches-] {+passes+} the enable {+through a latch that is transparent+} while the clock is [-high-] {+low and holds it while the clock is high,+} and ANDs [-it-] {+the held enable+} with the clock: a block whose enable is low gets … and clock wires do not switch.
textbook
tb.icg

## scale/lib.icg/part/and
The AND gate: the clock passes only while the enable … one for its source

 An integrated clock gate [-latches-] {+passes+} the enable {+through a latch that is transparent+} while the clock is [-high-] {+low and holds it while the clock is high,+} and ANDs [-it-] {+the held enable+} with the clock: a block whose enable is low gets … and clock wires do not switch.
textbook
tb.icg

## scale/lib.icg/part/latch
latch, generic. Space for details; Enter zooms in.
CLOCK … one for its source

 An integrated clock gate [-latches-] {+passes+} the enable {+through a latch that is transparent+} while the clock is [-high-] {+low and holds it while the clock is high,+} and ANDs [-it-] {+the held enable+} with the clock: a block whose enable is low gets … and clock wires do not switch.
textbook
tb.icg

## scale/lib.inverter/here
YOU ARE HERE · ≈ 240 nm · 10⁻⁷ m … (6 tracks of 40 nm); high-performance cells 300 nm.
[-inference-] {+outside source+}
in.lib.inverter.2
A MOSFET is a voltage-controlled switch: the … (high performance, 7.5 tracks, 10 fin pitches, 64 nm gate [-pitch); a 360 nm 9-track variant also exists.-] {+pitch).+}
outside source
fuse.wikichip.org ↗
n7.cells
A … and parallel transistors in one stage.
textbook
tb.gates

## scale/lib.inverter/part/gtable
The truth table. Space for details; Enter zooms in.
… (6 tracks of 40 nm); high-performance cells 300 nm.
[-inference-] {+outside source+}
in.lib.inverter.2
A MOSFET is a voltage-controlled switch: the … (high performance, 7.5 tracks, 10 fin pitches, 64 nm gate [-pitch); a 360 nm 9-track variant also exists.-] {+pitch).+}
outside source
fuse.wikichip.org ↗
n7.cells
A … and parallel transistors in one stage.
textbook
tb.gates

## scale/lib.inverter/part/onefet
One transistor, [-documented.-] {+generic.+} Space for details; Enter zooms in.
INVERTER · PART … of. A voltage on the gate decides whether current flows: {+in an n-type transistor,+} at 0 V the path along the fin is shut; … pulls a thin sheet of electrons into the fin, and [-current flows-] {+they flow+} from source to [-drain.-] {+drain (the current, by convention, from drain to source).+} The gate drapes over the fins on three sides.
… (high performance, 7.5 tracks, 10 fin pitches, 64 nm gate [-pitch); a 360 nm 9-track variant also exists.-] {+pitch).+}
outside source
fuse.wikichip.org ↗
n7.cells
N7 … V at 800); firmware limits 0.40-0.62 V.
measured
[-card not recorded-] {+aifoundry2+}
et.v-minion
At the minion rail's 0.517 V each … per °C (fit: 23.3 W x exp((T-80)/36)).
measured
[-card not recorded-] {+aifoundry2+}
et.leakage
By that fit, leakage doubles every 25 … same drive.
outside source
semiwiki.com ↗
n7.hpc

## scale/lib.latch/here
YOU ARE HERE · ≈ 500 nm · 10⁻⁷ m … V at 800); firmware limits 0.40-0.62 V.
measured
[-card not recorded-] {+aifoundry2+}
et.v-minion

## scale/lib.logic/part/aoi
An AND-OR-INVERT gate. Space for details; Enter zooms in.
… cells (G = Gi + Pi·Gj, P = Pi·Pj) of {+as few as+} log2 n levels, and forms each sum bit as p … frames it (an order of magnitude).
inference
size.lib.aoi21

## scale/lib.logic/part/icg
The clock gate: the flip-flops get a clock edge only … phase.
textbook
ml:l1:g.latch-write
An integrated clock gate [-latches-] {+passes+} the enable {+through a latch that is transparent+} while the clock is [-high-] {+low and holds it while the clock is high,+} and ANDs [-it-] {+the held enable+} with the clock: a block whose enable is low gets … and clock wires do not switch.
textbook
tb.icg

## scale/lib.logic/part/inv
An inverter. Space for details; Enter zooms in.
LOGIC … (6 tracks of 40 nm); high-performance cells 300 nm.
[-inference-] {+outside source+}
in.lib.inverter.2
A MOSFET is a voltage-controlled switch: the … (high performance, 7.5 tracks, 10 fin pitches, 64 nm gate [-pitch); a 360 nm 9-track variant also exists.-] {+pitch).+}
outside source
fuse.wikichip.org ↗
n7.cells
A … and parallel transistors in one stage.
textbook
tb.gates

## scale/lib.logic/part/mux
A 2:1 multiplexer. Space for details; Enter zooms in.
… a mux tree (128:1 per output bit, e.g. seven 2:1 {+levels, or three 4:1+} levels [-or four 4:1 levels),-] {+and one 2:1),+} and only the nodes whose value changes spend energy, so read energy depends on the data.
textbook
ml:l1:g.latch-read

## scale/lib.mux2/here
YOU ARE HERE · ≈ 300 nm · 10⁻⁷ m … a mux tree (128:1 per output bit, e.g. seven 2:1 {+levels, or three 4:1+} levels [-or four 4:1 levels),-] {+and one 2:1),+} and only the nodes whose value changes spend energy, so read energy depends on the data.
textbook
ml:l1:g.latch-read

## scale/lib.mux2/part/mtable
What the multiplexer does. Space for details; Enter zooms in. … a mux tree (128:1 per output bit, e.g. seven 2:1 {+levels, or three 4:1+} levels [-or four 4:1 levels),-] {+and one 2:1),+} and only the nodes whose value changes spend energy, so read energy depends on the data.
textbook
ml:l1:g.latch-read

## scale/lib.mux2/part/onefet
One transistor, [-documented.-] {+generic.+} Space for details; Enter zooms in.
TWO-WAY MULTIPLEXER · … of. A voltage on the gate decides whether current flows: {+in an n-type transistor,+} at 0 V the path along the fin is shut; … pulls a thin sheet of electrons into the fin, and [-current flows-] {+they flow+} from source to [-drain.-] {+drain (the current, by convention, from drain to source).+} The gate drapes over the fins on three sides.
… (high performance, 7.5 tracks, 10 fin pitches, 64 nm gate [-pitch); a 360 nm 9-track variant also exists.-] {+pitch).+}
outside source
fuse.wikichip.org ↗
n7.cells
N7 … V at 800); firmware limits 0.40-0.62 V.
measured
[-card not recorded-] {+aifoundry2+}
et.v-minion
At the minion rail's 0.517 V each … per °C (fit: 23.3 W x exp((T-80)/36)).
measured
[-card not recorded-] {+aifoundry2+}
et.leakage
By that fit, leakage doubles every 25 … same drive.
outside source
semiwiki.com ↗
n7.hpc

## scale/lib.nand2/part/onefet
One transistor, [-documented.-] {+generic.+} Space for details; Enter zooms in.
NAND GATE · … of. A voltage on the gate decides whether current flows: {+in an n-type transistor,+} at 0 V the path along the fin is shut; … pulls a thin sheet of electrons into the fin, and [-current flows-] {+they flow+} from source to [-drain.-] {+drain (the current, by convention, from drain to source).+} The gate drapes over the fins on three sides.
… (high performance, 7.5 tracks, 10 fin pitches, 64 nm gate [-pitch); a 360 nm 9-track variant also exists.-] {+pitch).+}
outside source
fuse.wikichip.org ↗
n7.cells
N7 … V at 800); firmware limits 0.40-0.62 V.
measured
[-card not recorded-] {+aifoundry2+}
et.v-minion
At the minion rail's 0.517 V each … per °C (fit: 23.3 W x exp((T-80)/36)).
measured
[-card not recorded-] {+aifoundry2+}
et.leakage
By that fit, leakage doubles every 25 … same drive.
outside source
semiwiki.com ↗
n7.hpc

## scale/lib.nor2/part/onefet
One transistor, generic. Space for details; Enter zooms in.
… of. A voltage on the gate decides whether current flows: {+in an n-type transistor,+} at 0 V the path along the fin is shut; … pulls a thin sheet of electrons into the fin, and [-current flows-] {+they flow+} from source to [-drain.-] {+drain (the current, by convention, from drain to source).+} The gate drapes over the fins on three sides.
… (high performance, 7.5 tracks, 10 fin pitches, 64 nm gate [-pitch); a 360 nm 9-track variant also exists.-] {+pitch).+}
outside source
fuse.wikichip.org ↗
n7.cells
N7 … V at 800); firmware limits 0.40-0.62 V.
measured
[-card not recorded-] {+aifoundry2+}
et.v-minion
At the minion rail's 0.517 V each … per °C (fit: 23.3 W x exp((T-80)/36)).
measured
[-card not recorded-] {+aifoundry2+}
et.leakage
By that fit, leakage doubles every 25 … same drive.
outside source
semiwiki.com ↗
n7.hpc

## scale/lib.powerfet/here
YOU ARE HERE · ≈ 5 µm · 10⁻⁶ m … tens of amps: thousands of small transistor cells side by [-side, each passing current-] {+side; in each, electrons flow+} straight down through the silicon from [-its-] {+the+} source on top to the drain [-underneath.-] {+underneath, so the current flows up.+}

 Zoom into:
The silicon crystal (+)
… is thousands of small cells in parallel: in a trench-gate [-device, current flows-] {+device conducting with its drain positive, electrons flow+} vertically, from the source on top, down a channel along … doped drift layer to the heavily doped substrate, the drain, [-underneath;-] {+underneath, and the current flows up;+} its on-resistance is milliohms and it blocks tens of volts. … about 50 meV, about twice kT at room temperature, so [-dopants-] {+dopant atoms alone in silicon sites+} are almost all ionised.
textbook
chu.berkeley.edu ↗
… of the view that frames it.
inference
size.lib.powerfet

## scale/lib.powerfet/part/cell
One cell: a trench gate with a channel on each … is thousands of small cells in parallel: in a trench-gate [-device, current flows-] {+device conducting with its drain positive, electrons flow+} vertically, from the source on top, down a channel along … doped drift layer to the heavily doped substrate, the drain, [-underneath;-] {+underneath, and the current flows up;+} its on-resistance is milliohms and it blocks tens of volts.
textbook
tb.powerfet

## scale/lib.powerfet/part/source
The source: n-type silicon, packed with donor atoms. Space for … is thousands of small cells in parallel: in a trench-gate [-device, current flows-] {+device conducting with its drain positive, electrons flow+} vertically, from the source on top, down a channel along … doped drift layer to the heavily doped substrate, the drain, [-underneath;-] {+underneath, and the current flows up;+} its on-resistance is milliohms and it blocks tens of volts. … about 50 meV, about twice kT at room temperature, so [-dopants-] {+dopant atoms alone in silicon sites+} are almost all ionised.
textbook
chu.berkeley.edu ↗
dope.donor-acceptor

## scale/lib.regfile/part/cells
The storage: one latch per bit, 64 here. Space for … V at 800); firmware limits 0.40-0.62 V.
measured
[-card not recorded-] {+aifoundry2+}
et.v-minion

## scale/lib.regfile/part/icg
The row clock gates: only the written row's latches see … phase.
textbook
ml:l1:g.latch-write
An integrated clock gate [-latches-] {+passes+} the enable {+through a latch that is transparent+} while the clock is [-high-] {+low and holds it while the clock is high,+} and ANDs [-it-] {+the held enable+} with the clock: a block whose enable is low gets … and clock wires do not switch.
textbook
tb.icg

## scale/lib.regfile/part/rmux
The read multiplexers: per bit, a tree of 2:1 multiplexers … a mux tree (128:1 per output bit, e.g. seven 2:1 {+levels, or three 4:1+} levels [-or four 4:1 levels),-] {+and one 2:1),+} and only the nodes whose value changes spend energy, so read energy depends on the data.
textbook
ml:l1:g.latch-read

## scale/lib.rom/here
YOU ARE HERE · ≈ 20 µm · 10⁻⁵ m … The vector unit's transcendental functions read their coefficients from small {+fixed+} tables {+too, but the Minion's VPU specification describes them as look-up tables in the RTL ("ROMs (LUT latch-based)", "ROMs (RTL LUTs)"), not an array+} like [-this.-] {+this one.+}

 Zoom into:
The FinFET transistor (+)
… frames it (an order of magnitude).
inference
size.lib.rom

## scale/lib.rom/part/cells
The cells: a transistor where the stored bit is 1, … of. A voltage on the gate decides whether current flows: {+in an n-type transistor,+} at 0 V the path along the fin is shut; … pulls a thin sheet of electrons into the fin, and [-current flows-] {+they flow+} from source to [-drain.-] {+drain (the current, by convention, from drain to source).+} The gate drapes over the fins on three sides.
… (high performance, 7.5 tracks, 10 fin pitches, 64 nm gate [-pitch); a 360 nm 9-track variant also exists.-] {+pitch).+}
outside source
fuse.wikichip.org ↗
n7.cells
N7 … V at 800); firmware limits 0.40-0.62 V.
measured
[-card not recorded-] {+aifoundry2+}
et.v-minion
At the minion rail's 0.517 V each … per °C (fit: 23.3 W x exp((T-80)/36)).
measured
[-card not recorded-] {+aifoundry2+}
et.leakage
By that fit, leakage doubles every 25 … same drive.
outside source
semiwiki.com ↗
n7.hpc

## scale/lib.rom/part/out
The outputs: an inverter per bitline gives the bit. Space … (6 tracks of 40 nm); high-performance cells 300 nm.
[-inference-] {+outside source+}
in.lib.inverter.2
A MOSFET is a voltage-controlled switch: the … (high performance, 7.5 tracks, 10 fin pitches, 64 nm gate [-pitch); a 360 nm 9-track variant also exists.-] {+pitch).+}
outside source
fuse.wikichip.org ↗
n7.cells
A … and parallel transistors in one stage.
textbook
tb.gates

## scale/lib.rom/part/pre
The precharge: a PMOS per bitline pulls it high before … of. A voltage on the gate decides whether current flows: {+in an n-type transistor,+} at 0 V the path along the fin is shut; … pulls a thin sheet of electrons into the fin, and [-current flows-] {+they flow+} from source to [-drain.-] {+drain (the current, by convention, from drain to source).+} The gate drapes over the fins on three sides.
… (high performance, 7.5 tracks, 10 fin pitches, 64 nm gate [-pitch); a 360 nm 9-track variant also exists.-] {+pitch).+}
outside source
fuse.wikichip.org ↗
n7.cells
N7 … V at 800); firmware limits 0.40-0.62 V.
measured
[-card not recorded-] {+aifoundry2+}
et.v-minion
At the minion rail's 0.517 V each … per °C (fit: 23.3 W x exp((T-80)/36)).
measured
[-card not recorded-] {+aifoundry2+}
et.leakage
By that fit, leakage doubles every 25 … same drive.
outside source
semiwiki.com ↗
n7.hpc

## scale/lib.round/part/incr
The incrementer: add one at the last kept place. Space … cells (G = Gi + Pi·Gj, P = Pi·Pj) of {+as few as+} log2 n levels, and forms each sum bit as p … all n bits one after another.
textbook
tb.prefix

## scale/lib.si/here
YOU ARE HERE · 0.543 nm · 10⁻¹⁰ m
… 52 nm fin about 383 planes (96 unit cells).
[-model-] {+inference+}
si.planes-width
Silicon's band gap is 1.12 eV at … electrons; the dopants' 50 meV is only 2 kT, so [-they are all-] {+nearly every dopant atom alone in a silicon site is+} ionised.
model
physics.nist.gov ↗
el.kt
Pure … about 50 meV, about twice kT at room temperature, so [-dopants-] {+dopant atoms alone in silicon sites+} are almost all ionised.
textbook
chu.berkeley.edu ↗
… easily than holes (mobility up to 1,400 vs 450 cm²/V·s); {+in a transistor's channel+} electrons saturate at about 8e6 cm/s, so crossing a 16.5 … standard atomic weight is 28.084-28.086.
outside source
p.atom.6

## scale/lib.si/part/atoms
The atoms. Space for details; Enter zooms in.
SILICON … 52 nm fin about 383 planes (96 unit cells).
[-model-] {+inference+}
si.planes-width
Silicon's band gap is 1.12 eV at … electrons; the dopants' 50 meV is only 2 kT, so [-they are all-] {+nearly every dopant atom alone in a silicon site is+} ionised.
model
physics.nist.gov ↗
el.kt
Pure … about 50 meV, about twice kT at room temperature, so [-dopants-] {+dopant atoms alone in silicon sites+} are almost all ionised.
textbook
chu.berkeley.edu ↗
… easily than holes (mobility up to 1,400 vs 450 cm²/V·s); {+in a transistor's channel+} electrons saturate at about 8e6 cm/s, so crossing a 16.5 … standard atomic weight is 28.084-28.086.
outside source
p.atom.6

## scale/lib.si/part/bonds
The bonds: each atom joined to four neighbours at the … 52 nm fin about 383 planes (96 unit cells).
[-model-] {+inference+}
si.planes-width
Silicon's band gap is 1.12 eV at … electrons; the dopants' 50 meV is only 2 kT, so [-they are all-] {+nearly every dopant atom alone in a silicon site is+} ionised.
model
physics.nist.gov ↗
el.kt
Pure … about 50 meV, about twice kT at room temperature, so [-dopants-] {+dopant atoms alone in silicon sites+} are almost all ionised.
textbook
chu.berkeley.edu ↗
… easily than holes (mobility up to 1,400 vs 450 cm²/V·s); {+in a transistor's channel+} electrons saturate at about 8e6 cm/s, so crossing a 16.5 … standard atomic weight is 28.084-28.086.
outside source
p.atom.6

## scale/lib.si/part/cube
The cubic cell: 8 atoms’ worth, in a cube 0.543 … 52 nm fin about 383 planes (96 unit cells).
[-model-] {+inference+}
si.planes-width
Silicon's band gap is 1.12 eV at … electrons; the dopants' 50 meV is only 2 kT, so [-they are all-] {+nearly every dopant atom alone in a silicon site is+} ionised.
model
physics.nist.gov ↗
el.kt
Pure … about 50 meV, about twice kT at room temperature, so [-dopants-] {+dopant atoms alone in silicon sites+} are almost all ionised.
textbook
chu.berkeley.edu ↗
… easily than holes (mobility up to 1,400 vs 450 cm²/V·s); {+in a transistor's channel+} electrons saturate at about 8e6 cm/s, so crossing a 16.5 … standard atomic weight is 28.084-28.086.
outside source
p.atom.6

## scale/lib.si/part/gap
The band gap. Space for details; Enter zooms in.
… electrons; the dopants' 50 meV is only 2 kT, so [-they are all-] {+nearly every dopant atom alone in a silicon site is+} ionised.
model
physics.nist.gov ↗
el.kt
Pure … and drain.
outside source
ioffe.ru ↗
si.ni

## scale/lib.si/part/oneatom
One silicon atom. Space for details; Enter zooms in.
… shells are clouds of probability, and the radii here are [-where-] each [-cloud is densest.-] {+shell's most likely distance from the nucleus.+}
textbook
p.core.4
A silicon atom: 14 protons … 3.1% Si-30.
outside source
physics.nist.gov ↗
si.atom

## scale/lib.sram6t/here
YOU ARE HERE · ≈ 240 nm · 10⁻⁷ m … V on die; firmware limits 0.66-0.85 V.
measured
[-card not recorded-] {+aifoundry2+}
et.v-sram
Esperanto designed its own low-voltage memory cells … latch arrays.)
outside source
fuse.wikichip.org ↗
et.custom-sram

## scale/lib.sram6t/part/cell
The storage cell: two cross-coupled inverters and two access NMOS; … of. A voltage on the gate decides whether current flows: {+in an n-type transistor,+} at 0 V the path along the fin is shut; … pulls a thin sheet of electrons into the fin, and [-current flows-] {+they flow+} from source to [-drain.-] {+drain (the current, by convention, from drain to source).+} The gate drapes over the fins on three sides.
… shire's arrays hold about 243 million cell transistors (an estimate).

## scale/lib.sram6t/part/half
A neighbouring column on the same wordline: its cell also … of. A voltage on the gate decides whether current flows: {+in an n-type transistor,+} at 0 V the path along the fin is shut; … pulls a thin sheet of electrons into the fin, and [-current flows-] {+they flow+} from source to [-drain.-] {+drain (the current, by convention, from drain to source).+} The gate drapes over the fins on three sides.
… 4:1 mux, four bitline pairs swing for every bit delivered.

## scale/lib.sram6t/part/mux
Column mux: NMOS pass gates connect the selected bitline pair … of. A voltage on the gate decides whether current flows: {+in an n-type transistor,+} at 0 V the path along the fin is shut; … pulls a thin sheet of electrons into the fin, and [-current flows-] {+they flow+} from source to [-drain.-] {+drain (the current, by convention, from drain to source).+} The gate drapes over the fins on three sides.
… for every bit read; whether m4 means 4:1 is asked.

## scale/lib.sram6t/part/olat
Output latch: holds the resolved bit for the macro output; generic. Space for details; Enter zooms in.
L2 · CELL

 [-Sense amplifier-] {+Output latch and write drivers+}

 A bit of memory made of logic: two … detail and the sources

 generic textbook

 [-A cross-coupled-] {+Once the sense amplifier has resolved, a+} latch [-with an NMOS tail: when SAE fires it resolves-] {+holds each bit for+} the [-small difference between-] {+macro's 144-bit output until+} the [-bitlines-] {+next read; on a write, drivers pull one bitline of each written column low+} to [-full swing. Read-margin settings delay SAE so more swing develops, slower and safer at low voltage-] {+flip the cell+} (textbook).

## scale/lib.sram6t/part/pre
Bitline precharge and equaliser: two PMOS pull BL and BLB … of. A voltage on the gate decides whether current flows: {+in an n-type transistor,+} at 0 V the path along the fin is shut; … pulls a thin sheet of electrons into the fin, and [-current flows-] {+they flow+} from source to [-drain.-] {+drain (the current, by convention, from drain to source).+} The gate drapes over the fins on three sides.
… the discharged bitline, most of a read's array energy (textbook).

## scale/lib.sram6t/part/sa
Sense amplifier: a cross-coupled latch with an NMOS tail, fired … of. A voltage on the gate decides whether current flows: {+in an n-type transistor,+} at 0 V the path along the fin is shut; … pulls a thin sheet of electrons into the fin, and [-current flows-] {+they flow+} from source to [-drain.-] {+drain (the current, by convention, from drain to source).+} The gate drapes over the fins on three sides.
… more swing develops, slower and safer at low voltage (textbook).

## scale/lib.sram6t/part/wd
Write drivers: pull one bitline of the pair to ground; … of. A voltage on the gate decides whether current flows: {+in an n-type transistor,+} at 0 V the path along the fin is shut; … pulls a thin sheet of electrons into the fin, and [-current flows-] {+they flow+} from source to [-drain.-] {+drain (the current, by convention, from drain to source).+} The gate drapes over the fins on three sides.
… more swing develops, slower and safer at low voltage (textbook).

## scale/lib.xbar/part/inq
The input queues: requests wait here for their turn. Space … addressed by a write pointer and a read pointer, two [-counters; comparing-] {+counters. Equal pointers mean empty or full; one way to tell them apart is a pointer one bit wider than+} the [-pointers tells a full-] {+address: equal in every bit, the+} queue [-from an empty one.-] {+is empty; equal but for that extra bit, it is full.+}
textbook
tb.fifo
Queue (first in, first out): … frames it (an order of magnitude).
inference
size.lib.fifo

## scale/lib.xor/part/onefet
One transistor, [-documented.-] {+generic.+} Space for details; Enter zooms in.
XOR GATE · … of. A voltage on the gate decides whether current flows: {+in an n-type transistor,+} at 0 V the path along the fin is shut; … pulls a thin sheet of electrons into the fin, and [-current flows-] {+they flow+} from source to [-drain.-] {+drain (the current, by convention, from drain to source).+} The gate drapes over the fins on three sides.
… (high performance, 7.5 tracks, 10 fin pitches, 64 nm gate [-pitch); a 360 nm 9-track variant also exists.-] {+pitch).+}
outside source
fuse.wikichip.org ↗
n7.cells
N7 … V at 800); firmware limits 0.40-0.62 V.
measured
[-card not recorded-] {+aifoundry2+}
et.v-minion
At the minion rail's 0.517 V each … per °C (fit: 23.3 W x exp((T-80)/36)).
measured
[-card not recorded-] {+aifoundry2+}
et.leakage
By that fit, leakage doubles every 25 … same drive.
outside source
semiwiki.com ↗
n7.hpc

## scale/lib.xor/part/xinv
Two inverters make A’ and B’: four more transistors. Space … (6 tracks of 40 nm); high-performance cells 300 nm.
[-inference-] {+outside source+}
in.lib.inverter.2
A MOSFET is a voltage-controlled switch: the … (high performance, 7.5 tracks, 10 fin pitches, 64 nm gate [-pitch); a 360 nm 9-track variant also exists.-] {+pitch).+}
outside source
fuse.wikichip.org ↗
n7.cells
A … and parallel transistors in one stage.
textbook
tb.gates

## scale/localgroup/here
YOU ARE HERE · 10 million ly · 10²² m … (134 in one count), most of them faint dwarf galaxies; [-counted that way-] {+judged by density matching and the potential surface of its parent structure, the Local Sheet,+} the group is about 5.1 Mpc (17 million light-years) across. … which is part of Laniakea.
outside source
out.localgroup.6

## scale/memshire.phy.dq/part/ioE
where the energy goes, documented. Space for details; Enter zooms … of. A voltage on the gate decides whether current flows: {+in an n-type transistor,+} at 0 V the path along the fin is shut; … pulls a thin sheet of electrons into the fin, and [-current flows-] {+they flow+} from source to [-drain.-] {+drain (the current, by convention, from drain to source).+} The gate drapes over the fins on three sides.
… load does, and a store through the L1 341.5 pJ/B.

## scale/memshire/here
YOU ARE HERE · ≈ 3.7 mm · 10⁻³ m … memory-shire constant (152 ns), the DRAM chip accounts for about [-25–28-] {+28+} cycles (activate tRCD 11 cycles = 18 ns, 19.3 ns read latency, [-one or-] {+the+} two 4.3 ns [-bursts);-] {+bursts of a 64-byte line); the rest,+} at most [-~63–66-] {+~63+} cycles [-(~105–110 ns) are-] {+(~105 ns), is the L3 home's miss handling (about 12 cycles by the spec: an L3 miss is 42 shire clocks against 30 for a hit) and+} the memory [-shire itself:-] {+shire:+} controller queue, PHY and the crossings between the 933 MHz … 91 + 12 × hops(home shire, memory shire) cycles; about [-25-] {+28+} of the 91 are the DRAM chip (activate 11, read {+latency+} and [-burst 14)-] {+two bursts 17)+} and {+at most+} about [-66-] {+63 the L3 home's miss handling and+} the memory shire. Only [-25-28-] {+about 28+} of a ~300-cycle DRAM load are the DRAM's own timing. … (the card's VDDQLP, the LPDDR4X's I/O VDDQ).
measured
[-card not recorded-] {+aifoundry2+}
et.v-other

## scale/memshire/part/atomic
atomic unit, documented. Space for details; Enter zooms in.
… not waiting for a carry to ripple through 64 positions: {+the fastest+} prefix adders compute all the carries in about six levels … data): the datasheet lists LPDDR4X support for global atomic operations.

## scale/memshire/part/die
The LPDDR4X channel 0: a 16-bit die in a package … unknown · asked the part

 2 GB per [-channel:-] {+channel on aifoundry2 and aifoundry3:+} 8 banks × 131,072 rows × 2 KB pages. Whether … die or two byte-mode dies, the die's density and the [-Micron part-] {+part's maker and+} number are not in any source; the firmware reads them from mode registers at every boot but no log has been captured.

## scale/memshire/part/die#2
The LPDDR4X channel 1: a 16-bit die in a package … unknown · asked the part

 2 GB per [-channel:-] {+channel on aifoundry2 and aifoundry3:+} 8 banks × 131,072 rows × 2 KB pages. Whether … die or two byte-mode dies, the die's density and the [-Micron part-] {+part's maker and+} number are not in any source; the firmware reads them from mode registers at every boot but no log has been captured.

## scale/memshire/part/xing
crossing, documented. Space for details; Enter zooms in.
DRAM · MEMORY SHIRE

 The clock crossing

 [-The shire's cache runs at 0.705 V on its own clock,-] {+Where requests wait their turn: a small register file, a counter that points where+} the [-network at 0.485 V-] {+next one is written, another where the next one is read,+} and [-400 MHz. Every bit-] {+a compare+} that [-crosses is shifted in voltage and re-timed through two flip-flops into the other clock, so it cannot be caught half-changed.-] {+says full or empty.+}

 Zoom in:
The [-voltage and clock crossing-] {+queue (first in, first out)+} (double-click)
More detail and the sources

 documented … the memory shire's cycles is part of what is asked.

## scale/mesh.link.wire/part/bitE
energy per bit, documented. Space for details; Enter zooms in. … mm of wire, broken by repeaters. A random bit costs [-36.2-] {+36.7+} fJ per mm on the mesh rail, so a 64-byte reply over one hop is [-69-] {+70+} pJ on the mesh rail (derived); measured on board power, … do not toggle the wires: they cost several times less.

## scale/mesh.link.wire/part/ls
The level shifter: a cross-coupled PMOS pair on the high … of. A voltage on the gate decides whether current flows: {+in an n-type transistor,+} at 0 V the path along the fin is shut; … pulls a thin sheet of electrons into the fin, and [-current flows-] {+they flow+} from source to [-drain.-] {+drain (the current, by convention, from drain to source).+} The gate drapes over the fins on three sides.
… it as a buffer; the physical cell is not documented.

## scale/mesh.link.wire/part/sync
then a [-2-flop synchroniser,-] {+VC FIFO,+} documented. Space for details; Enter zooms in.
L3 · [-TRANSISTORS-] {+CROSSING+}

 The [-level shifter-] {+VC FIFO into the shire clock+}

 Two latches back to back: the value changes … bit) (double-click)
More detail and the sources

 {+documented spec+} generic textbook [-documented that it is there-]

 The [-reply arrives at the mesh rail's swing, 485 mV, and must drive the Shire Channel's logic, whose rail is asked (its SRAM arrays sit on 705 mV). A cross-coupled PMOS pair-] {+reply's words are written into a small FIFO+} on the [-high rail over an NMOS pair driven by-] {+mesh's clock and read out on+} the [-signal-] {+shire clock; only the FIFO's write+} and [-its complement: the input pulls one side down and the pair snaps the other up to the high rail. The ET RTL models-] {+read counts pass through two-flip-flop synchronisers (the Shire Cache Specification's VCFIFO "uses 2-stage synchronizers"), so a word is read only once+} it [-as a buffer; the physical cell-] is [-not documented.-] {+completely written.+}

## scale/mesh/here
YOU ARE HERE · ≈ 3.7 mm · 10⁻³ m …
More detail and the sources

 Its size: {+one hop: one tile pitch (chip.hop-pitch);+} the {+whole mesh spans the die, its+} 6-column shire grid [-spans-] about 22.2 mm [-(L08); with the memory shires the mesh spans the die-] {+(L08)+}

 The facts (8): point at one for its … V set point, 0.483-0.486 V on die.
measured
[-card not recorded-] {+aifoundry2+}
et.v-noc

## scale/mesh/part/hopE
a 64 B reply over one hop, documented. Space for … mm of wire, broken by repeaters. A random bit costs [-36.2-] {+36.7+} fJ per mm on the mesh rail, so a 64-byte reply over one hop is [-69-] {+70+} pJ on the mesh rail (derived); measured on board power, … do not toggle the wires: they cost several times less.

## scale/mesh/part/link
One mesh link: a bundle of wires broken by repeaters, … mm of wire, broken by repeaters. A random bit costs [-36.2-] {+36.7+} fJ per mm on the mesh rail, so a 64-byte reply over one hop is [-69-] {+70+} pJ on the mesh rail (derived); measured on board power, … do not toggle the wires: they cost several times less.

## scale/mesh/part/more
… hops, generic. Space for details; Enter zooms in.
… mm of wire, broken by repeaters. A random bit costs [-36.2-] {+36.7+} fJ per mm on the mesh rail, so a 64-byte reply over one hop is [-69-] {+70+} pJ on the mesh rail (derived); measured on board power, … do not toggle the wires: they cost several times less.

## scale/mesh/part/nochop
unknown: the router pipeline per hop, unknown (asked). Space for … crosses the router's internal switch to which output each cycle. [-Each-] {+A minion shire's+} mesh stop has nine of them stacked as separate [-networks,-] {+networks (a memory shire's most likely seven),+} plus one for debug.

 Zoom in:
The … replies, the flit width and the order of the dimensions.

## scale/mesh/part/router
router (one of 9 layers), generic. Space for details; Enter … crosses the router's internal switch to which output each cycle. [-Each-] {+A minion shire's+} mesh stop has nine of them stacked as separate [-networks,-] {+networks (a memory shire's most likely seven),+} plus one for debug.

 Zoom in:
The … layers, ports unknown · asked its pipeline

 Each {+minion shire's+} mesh stop has 9 main-NoC routers (layers 0–8) and a … September: a request goes x first, its reply y first.

## scale/mesh/part/router2
next router, generic. Space for details; Enter zooms in.
… crosses the router's internal switch to which output each cycle. [-Each-] {+A minion shire's+} mesh stop has nine of them stacked as separate [-networks,-] {+networks (a memory shire's most likely seven),+} plus one for debug.

 Zoom in:
The … layers, ports unknown · asked its pipeline

 Each {+minion shire's+} mesh stop has 9 main-NoC routers (layers 0–8) and a … September: a request goes x first, its reply y first.

## scale/mesh/part/vcdown
VC FIFO, documented. Space for details; Enter zooms in.
…
Into the mesh: a VC FIFO

 The [-shire's-] {+shire+} cache runs [-at-] {+on the shire clock, its arrays on the+} 0.705 V [-on-] {+SRAM rail (the rail of+} its [-own clock,-] {+logic is not documented);+} the network {+runs+} at 0.485 V and 400 MHz. Every bit [-that crosses-] is [-shifted-] {+level-shifted as it crosses; each word waits+} in [-voltage-] {+a small FIFO whose write+} and [-re-timed-] {+read counts, not the data, pass+} through [-two flip-flops-] {+two-flip-flop synchronisers+} into the other clock, so {+a word is read only once+} it [-cannot be caught half-changed.-] {+is completely written.+}

 Zoom in:
The voltage and clock crossing … change the swing; the synchroniser costs 2–3 receiving-clock cycles (textbook).

## scale/minion/here
YOU ARE HERE · ≈ 500 µm · 10⁻⁴ m … 6, neighbourhood = (hartid mod 64) >> 4, minion = {+(hartid mod 64) >> 1 (the firmware's get_minion_id(),+} hartid >> 1, {+numbers the minions chip-wide),+} thread = hartid & 1).
documented
On-chip communication …
The energy manual ↗
e-fadd
No hardware {+float or vector+} divide or square root in [-U-mode:-] {+U-mode (the scalar integer div and rem run):+} fdiv.ps and fsqrt.ps trap, as do sine, reciprocal square root, {+conversion between fp32 and+} 64-bit [-float conversion-] {+integers (fcvt.l.s, fcvt.s.l)+} and reading the cycle CSR; 161 of the instructions tried …
The DVFS loop and its leakage ↗
minion.sleep-unused

## scale/minion/part/etlink
ET-Link port. Space for details; Enter zooms in.
MINION … hold go out here.

 Zoom in:
The [-voltage and clock crossing-] {+bank FIFOs+} (double-click)
Also:
The crossing into the shire’s clock … documented
Anatomy of a memory access ↗
shire.crossbar

## scale/minion/part/fln
Fast local network. Space for details; Enter zooms in.
… one peer-to-peer ready bit per minion, not one per partner: {+if+} a minion [-receiving from-] {+that TensorSends to+} two [-TensorSend-] partners [-at once hangs-] {+gets both their readies before it has used the first, one is lost, and that receiver and+} its [-hart permanently-] {+sender hang for good+} (the card then needs a reset).
documented
On-chip … measured
three cards
On-chip communication ↗
sync.tree-levels

## scale/minion/part/hart
Hart 0. Space for details; Enter zooms in.
MINION … 6, neighbourhood = (hartid mod 64) >> 4, minion = {+(hartid mod 64) >> 1 (the firmware's get_minion_id(),+} hartid >> 1, {+numbers the minions chip-wide),+} thread = hartid & 1).
documented
On-chip communication … measured
three cards
Memory hierarchy ↗
l2.latency

## scale/minion/part/hart#2
Hart 1. Space for details; Enter zooms in.
MINION … 6, neighbourhood = (hartid mod 64) >> 4, minion = {+(hartid mod 64) >> 1 (the firmware's get_minion_id(),+} hartid >> 1, {+numbers the minions chip-wide),+} thread = hartid & 1).
documented
On-chip communication … measured
three cards
Memory hierarchy ↗
l2.latency

## scale/minion/part/l1d
L1 data cache. Space for details; Enter zooms in.
… L3; tensor stores skip the L1 and L2 (energy manual; {+the+} PRM [-confirms only-] {+states that loads bypass the L1, pdf p.275, and that stores bypass+} the L1 [-bypass).-] {+and the L2, pdf p.306 and p.309).+} The L2 part is measured (E57, 29 September): a second … / (bytes per element): A from the L1 scratchpad, B {+from the L1 scratchpad or+} streamed through [-TenB,-] {+TenB by a paired TensorLoadB,+} C accumulated in hart 0's vector registers (int8 in TenC). …
three cards
The energy manual ↗
e-scp-tload

## scale/minion/part/l1scp
L1 tensor scratchpad. Space for details; Enter zooms in.
… L3; tensor stores skip the L1 and L2 (energy manual; {+the+} PRM [-confirms only-] {+states that loads bypass the L1, pdf p.275, and that stores bypass+} the L1 [-bypass).-] {+and the L2, pdf p.306 and p.309).+} The L2 part is measured (E57, 29 September): a second … / (bytes per element): A from the L1 scratchpad, B {+from the L1 scratchpad or+} streamed through [-TenB,-] {+TenB by a paired TensorLoadB,+} C accumulated in hart 0's vector registers (int8 in TenC). …
three cards
The energy manual ↗
e-scp-tload

## scale/minion/part/minion
The minion core. Space for details; Enter zooms in.
… 6, neighbourhood = (hartid mod 64) >> 4, minion = {+(hartid mod 64) >> 1 (the firmware's get_minion_id(),+} hartid >> 1, {+numbers the minions chip-wide),+} thread = hartid & 1).
documented
On-chip communication …
The energy manual ↗
e-fadd
No hardware {+float or vector+} divide or square root in [-U-mode:-] {+U-mode (the scalar integer div and rem run):+} fdiv.ps and fsqrt.ps trap, as do sine, reciprocal square root, {+conversion between fp32 and+} 64-bit [-float conversion-] {+integers (fcvt.l.s, fcvt.s.l)+} and reading the cycle CSR; 161 of the instructions tried …
The DVFS loop and its leakage ↗
minion.sleep-unused

## scale/minion/part/tensor
Tensor sequencer. Space for details; Enter zooms in.
MINION … L3; tensor stores skip the L1 and L2 (energy manual; {+the+} PRM [-confirms only-] {+states that loads bypass the L1, pdf p.275, and that stores bypass+} the L1 [-bypass).-] {+and the L2, pdf p.306 and p.309).+} The L2 part is measured (E57, 29 September): a second … / (bytes per element): A from the L1 scratchpad, B {+from the L1 scratchpad or+} streamed through [-TenB,-] {+TenB by a paired TensorLoadB,+} C accumulated in hart 0's vector registers (int8 in TenC). … The energy manual ↗
e-tfma-fp32-zeros
Board GFLOP/s per [-W,-] {+W (GOP/s per W for int8),+} L2 matmul fp32 / fp16 / int8: aifoundry2 161 / … 0x830.
documented
no published page yet
minion.tensor-csrs

## scale/minion/part/vpu
Vector unit. Space for details; Enter zooms in.
MINION … a quarter the issue rate; flog.ps 218 pJ. No hardware {+float or vector+} divide or square root: they [-trap.-] {+trap (the scalar integer div and rem run, at 141-157 pJ).+}
measured
three cards
The energy manual ↗ …
measured
aifoundry3
Sparse compute ↗
minion.vector-rate

## scale/p.atom/here
YOU ARE HERE · 0.235 nm · 10⁻¹⁰ m
… shells are clouds of probability, and the radii here are [-where-] each [-cloud is densest.-] {+shell's most likely distance from the nucleus.+}
textbook
p.core.4
A silicon atom: 14 protons … 3.1% Si-30.
outside source
physics.nist.gov ↗
si.atom

## scale/p.atom/part/bonds
The four bonds to the neighbouring atoms. Space for details; … narrower than the atom, but 99.97% of its mass. Nothing [-in-] a chip {+does+} ever [-touches-] {+changes+} it.

 Zoom in:
The silicon-28 nucleus (double-click) … 0.027%.
model
p.nucleus.4
Its density is about [-2.3-] {+1.7+} x 10^17 kg per [-m3:-] {+m3 as a uniform sphere 8.06 fm across, or 2.3 x 10^17 at the textbook rule's radius of 3.64 fm:+} a teaspoon (5 mL) of nuclear matter would weigh about [-1.1-] {+a+} billion tonnes.
model
p.nucleus.5
If the nucleus …
That is about a million times the energy of [-the-] {+an+} outer [-electrons-] {+electron+} (8.15 eV) [-or of-] {+and nearly four million times+} a chemical bond (about 2.3 eV): why chemistry, and electronics, … its nucleus (about 8.1 fm across).
model
p.atom.11

## scale/p.atom/part/nucleus
The nucleus: a speck at the middle. Space for details; … narrower than the atom, but 99.97% of its mass. Nothing [-in-] a chip {+does+} ever [-touches-] {+changes+} it.

 Zoom in:
The silicon-28 nucleus (double-click) … 0.027%.
model
p.nucleus.4
Its density is about [-2.3-] {+1.7+} x 10^17 kg per [-m3:-] {+m3 as a uniform sphere 8.06 fm across, or 2.3 x 10^17 at the textbook rule's radius of 3.64 fm:+} a teaspoon (5 mL) of nuclear matter would weigh about [-1.1-] {+a+} billion tonnes.
model
p.nucleus.5
If the nucleus …
That is about a million times the energy of [-the-] {+an+} outer [-electrons-] {+electron+} (8.15 eV) [-or of-] {+and nearly four million times+} a chemical bond (about 2.3 eV): why chemistry, and electronics, … its nucleus (about 8.1 fm across).
model
p.atom.11

## scale/p.atom/part/oneelectron
One electron. Space for details; Enter zooms in.
ATOM … is below 4.1 x 10^-30 e cm (PDG 2026), so {+the centre of+} its charge sits within 4.1 x 10^-32 m of its centre {+of mass+} (dipole moment divided by its charge). {+That limits its shape, not its size.+}
model
p.electron.4
The 'classical electron radius', 2.818 … 6,242 electrons.
outside source
physics.nist.gov ↗
el.electron

## scale/p.atom/part/shells
The inner ten electrons: two shells held tight. Space for … narrower than the atom, but 99.97% of its mass. Nothing [-in-] a chip {+does+} ever [-touches-] {+changes+} it.

 Zoom in:
The silicon-28 nucleus (double-click) … 0.027%.
model
p.nucleus.4
Its density is about [-2.3-] {+1.7+} x 10^17 kg per [-m3:-] {+m3 as a uniform sphere 8.06 fm across, or 2.3 x 10^17 at the textbook rule's radius of 3.64 fm:+} a teaspoon (5 mL) of nuclear matter would weigh about [-1.1-] {+a+} billion tonnes.
model
p.nucleus.5
If the nucleus …
That is about a million times the energy of [-the-] {+an+} outer [-electrons-] {+electron+} (8.15 eV) [-or of-] {+and nearly four million times+} a chemical bond (about 2.3 eV): why chemistry, and electronics, … its nucleus (about 8.1 fm across).
model
p.atom.11

## scale/p.atom/part/valence
The four outer electrons, in the bonds. Space for details; … narrower than the atom, but 99.97% of its mass. Nothing [-in-] a chip {+does+} ever [-touches-] {+changes+} it.

 Zoom in:
The silicon-28 nucleus (double-click) … 0.027%.
model
p.nucleus.4
Its density is about [-2.3-] {+1.7+} x 10^17 kg per [-m3:-] {+m3 as a uniform sphere 8.06 fm across, or 2.3 x 10^17 at the textbook rule's radius of 3.64 fm:+} a teaspoon (5 mL) of nuclear matter would weigh about [-1.1-] {+a+} billion tonnes.
model
p.nucleus.5
If the nucleus …
That is about a million times the energy of [-the-] {+an+} outer [-electrons-] {+electron+} (8.15 eV) [-or of-] {+and nearly four million times+} a chemical bond (about 2.3 eV): why chemistry, and electronics, … its nucleus (about 8.1 fm across).
model
p.atom.11

## scale/p.dopant/here
YOU ARE HERE · 0.235 nm · 10⁻¹⁰ m
… (2 kT = 52 meV), so nearly every dopant atom {+alone in a silicon site+} has given up (or taken) its electron.
textbook
… is the stated goal.
outside source
p.dopant.6
[-The same-] {+TSMC's FinFET+} patent [-dopes the wells under-] {+(US 11,107,923) implants its wells, in+} the fins {+or the substrate,+} at {+up to 10^18 per cm3 for n-wells (10^16 to 10^18) and up to 10^20 for p-wells (10^17 to 10^20). At a bulk FinFET's usual fin doping,+} 10^16 to 10^18 per [-cm3. At those levels-] {+cm3,+} a 6 x 16.5 x 52 nm channel would hold … about 50 meV, about twice kT at room temperature, so [-dopants-] {+dopant atoms alone in silicon sites+} are almost all ionised.
textbook
chu.berkeley.edu ↗
… electrons; the dopants' 50 meV is only 2 kT, so [-they are all-] {+nearly every dopant atom alone in a silicon site is+} ionised.
model
physics.nist.gov ↗
el.kt

## scale/p.dopant/part/fifth
The fifth electron: loosely held, free at room temperature. Space … about 50 meV, about twice kT at room temperature, so [-dopants-] {+dopant atoms alone in silicon sites+} are almost all ionised.
textbook
chu.berkeley.edu ↗
dope.donor-acceptor

## scale/p.dopant/part/lattice
The silicon around it. Space for details; Enter zooms in. … about 50 meV, about twice kT at room temperature, so [-dopants-] {+dopant atoms alone in silicon sites+} are almost all ionised.
textbook
chu.berkeley.edu ↗
dope.donor-acceptor

## scale/p.dopant/part/phos
The phosphorus atom: five outer electrons, four in bonds. Space … about 50 meV, about twice kT at room temperature, so [-dopants-] {+dopant atoms alone in silicon sites+} are almost all ionised.
textbook
chu.berkeley.edu ↗
dope.donor-acceptor

## scale/p.electron/here
YOU ARE HERE · < 2 × 10⁻²⁰ m · … is below 4.1 x 10^-30 e cm (PDG 2026), so {+the centre of+} its charge sits within 4.1 x 10^-32 m of its centre {+of mass+} (dipole moment divided by its charge). {+That limits its shape, not its size.+}
model
p.electron.4
The 'classical electron radius', 2.818 … 6,242 electrons.
outside source
physics.nist.gov ↗
el.electron

## scale/p.electron/part/bound
The limit: if it has a size, it is smaller … is below 4.1 x 10^-30 e cm (PDG 2026), so {+the centre of+} its charge sits within 4.1 x 10^-32 m of its centre {+of mass+} (dipole moment divided by its charge). {+That limits its shape, not its size.+}
model
p.electron.4
The 'classical electron radius', 2.818 … 6,242 electrons.
outside source
physics.nist.gov ↗
el.electron

## scale/p.electron/part/point
the electron: a point. Space for details; Enter zooms in. … is below 4.1 x 10^-30 e cm (PDG 2026), so {+the centre of+} its charge sits within 4.1 x 10^-32 m of its centre {+of mass+} (dipole moment divided by its charge). {+That limits its shape, not its size.+}
model
p.electron.4
The 'classical electron radius', 2.818 … 6,242 electrons.
outside source
physics.nist.gov ↗
el.electron

## scale/p.nucleon/part/field
The gluon field: most of the proton's mass. Space for … · PART

 The gluon field

 The {+three+} quarks' own masses [-are-] {+add up to+} about 1% of the proton's. The rest is energy: the …
Masses (MS-bar at 2 GeV): up 2.16 +/- 0.07 [-MeV,-] {+MeV/c^2,+} down 4.70 +/- 0.07 [-MeV.-] {+MeV/c^2.+} Two ups and a down add to 9.0 [-MeV:-] {+MeV/c^2:+} 1% of the proton's 938.3 [-MeV.-] {+MeV/c^2.+}
model
p.quark.3
A lattice-QCD breakdown of the proton's [-mass:-] {+mass (MS-bar at 2 GeV):+} the [-quarks'-] masses [-(through-] {+of all+} the {+quarks in it, the sea of short-lived quark-antiquark pairs (strange ones too) as well as the three, give 9% (the+} quark [-condensate, u, d and s) give 9%,-] {+condensate term);+} the quarks' energy of motion 33%, the gluon field's energy … they are massless in theory (a mass of a few [-MeV-] {+MeV/c^2+} is not excluded) and come in eight colour states.
… is energy rather than quark mass.
inference
p.quark.8

## scale/p.nucleon/part/onequark
One quark. Space for details; Enter zooms in.
PROTON … a quark has a size, it is smaller than this, [-under-] {+which is about+} a two-thousandth of the proton. Quarks are never found alone; …
Masses (MS-bar at 2 GeV): up 2.16 +/- 0.07 [-MeV,-] {+MeV/c^2,+} down 4.70 +/- 0.07 [-MeV.-] {+MeV/c^2.+} Two ups and a down add to 9.0 [-MeV:-] {+MeV/c^2:+} 1% of the proton's 938.3 [-MeV.-] {+MeV/c^2.+}
model
p.quark.3
A lattice-QCD breakdown of the proton's [-mass:-] {+mass (MS-bar at 2 GeV):+} the [-quarks'-] masses [-(through-] {+of all+} the {+quarks in it, the sea of short-lived quark-antiquark pairs (strange ones too) as well as the three, give 9% (the+} quark [-condensate, u, d and s) give 9%,-] {+condensate term);+} the quarks' energy of motion 33%, the gluon field's energy … they are massless in theory (a mass of a few [-MeV-] {+MeV/c^2+} is not excluded) and come in eight colour states.
… Colour is believed to be permanently confined: only colourless combinations [-(three quarks,-] {+exist on their own, usually three quarks+} or a quark and an [-antiquark) exist on their own.-] {+antiquark; some observed states are classed as four or five quarks.+}
outside source
p.quark.7
Squeezing quarks into 0.84 … is energy rather than quark mass.
inference
p.quark.8

## scale/p.nucleon/part/quarks
Two up quarks and a down quark. Space for details; … · PART

 The gluon field

 The {+three+} quarks' own masses [-are-] {+add up to+} about 1% of the proton's. The rest is energy: the …
Masses (MS-bar at 2 GeV): up 2.16 +/- 0.07 [-MeV,-] {+MeV/c^2,+} down 4.70 +/- 0.07 [-MeV.-] {+MeV/c^2.+} Two ups and a down add to 9.0 [-MeV:-] {+MeV/c^2:+} 1% of the proton's 938.3 [-MeV.-] {+MeV/c^2.+}
model
p.quark.3
A lattice-QCD breakdown of the proton's [-mass:-] {+mass (MS-bar at 2 GeV):+} the [-quarks'-] masses [-(through-] {+of all+} the {+quarks in it, the sea of short-lived quark-antiquark pairs (strange ones too) as well as the three, give 9% (the+} quark [-condensate, u, d and s) give 9%,-] {+condensate term);+} the quarks' energy of motion 33%, the gluon field's energy … they are massless in theory (a mass of a few [-MeV-] {+MeV/c^2+} is not excluded) and come in eight colour states.
… is energy rather than quark mass.
inference
p.quark.8

## scale/p.nucleus/here
YOU ARE HERE · 8.06 fm · 10⁻¹⁵ m
… narrower than the atom, but 99.97% of its mass. Nothing [-in-] a chip {+does+} ever [-touches-] {+changes+} it.

 Zoom into:
A proton (+)
… 0.027%.
model
p.nucleus.4
Its density is about [-2.3-] {+1.7+} x 10^17 kg per [-m3:-] {+m3 as a uniform sphere 8.06 fm across, or 2.3 x 10^17 at the textbook rule's radius of 3.64 fm:+} a teaspoon (5 mL) of nuclear matter would weigh about [-1.1-] {+a+} billion tonnes.
model
p.nucleus.5
If the nucleus …
That is about a million times the energy of [-the-] {+an+} outer [-electrons-] {+electron+} (8.15 eV) [-or of-] {+and nearly four million times+} a chemical bond (about 2.3 eV): why chemistry, and electronics, … its nucleus (about 8.1 fm across).
model
p.atom.11

## scale/p.nucleus/part/nucleons
Fourteen protons and fourteen neutrons. Space for details; Enter zooms … narrower than the atom, but 99.97% of its mass. Nothing [-in-] a chip {+does+} ever [-touches-] {+changes+} it.

 Zoom in:
A proton (double-click)
…
outside source
p.nucleus.1
Its density is about [-2.3-] {+1.7+} x 10^17 kg per [-m3:-] {+m3 as a uniform sphere 8.06 fm across, or 2.3 x 10^17 at the textbook rule's radius of 3.64 fm:+} a teaspoon (5 mL) of nuclear matter would weigh about [-1.1-] {+a+} billion tonnes.
model
p.nucleus.5
Binding energy 8.448 …
That is about a million times the energy of [-the-] {+an+} outer [-electrons-] {+electron+} (8.15 eV) [-or of-] {+and nearly four million times+} a chemical bond (about 2.3 eV): why chemistry, and electronics, never change a nucleus.
model
p.nucleus.8

## scale/p.planck/here
YOU ARE HERE · 1.62 × 10⁻³⁵ m

 … nobody has yet; whether anything can be smaller is unknown. [-Between-] {+Below+} the [-quark's limit and here-] {+electron's limit, 2 x 10^-20 m,+} lie [-16-] {+some 15+} powers of ten that no experiment has reached.

 … quark's radius limit is 3 x 10^16 times the Planck [-length:-] {+length; even the electron's smaller limit, 2 x 10^-20 m, is 1 x 10^15 times it:+} some [-16-] {+15+} powers of ten that no experiment has probed.
model … diameter is 61.7 powers of ten.
model
p.planck.5

## scale/p.planck/part/ruler
A ruler of sizes, from a proton down to the … nobody has yet; whether anything can be smaller is unknown. [-Between-] {+Below+} the [-quark's limit and here-] {+electron's limit, 2 x 10^-20 m,+} lie [-16-] {+some 15+} powers of ten that no experiment has reached.

 … quark's radius limit is 3 x 10^16 times the Planck [-length:-] {+length; even the electron's smaller limit, 2 x 10^-20 m, is 1 x 10^15 times it:+} some [-16-] {+15+} powers of ten that no experiment has probed.
model … diameter is 61.7 powers of ten.
model
p.planck.5

## scale/p.planck/part/unexplored
[-Sixteen-] {+Fifteen+} powers of ten that no experiment has reached: details
PLANCK LENGTH · PART

 Unexplored

 Between the {+electron's limit, the+} smallest [-limit any experiment has set-] {+on this ruler,+} and the Planck length lie some [-sixteen-] {+fifteen+} powers of ten: nobody knows what is there.

 …
More detail and the sources

 The facts [-(2):-] {+(3):+} point at one for its source

 The quark's radius limit is 3 x 10^16 times the Planck [-length:-] {+length; even the electron's smaller limit, 2 x 10^-20 m, is 1 x 10^15 times it:+} some [-16-] {+15+} powers of ten that no experiment has probed.
model … minimal length, and none is confirmed.
speculative
p.planck.4 {+
 A radius limit below 2 x 10^-20 m, from contact-interaction searches at LEP at the 10 TeV scale.
outside source
p.electron.2+}

## scale/p.quark/here
YOU ARE HERE · < 4.3 × 10⁻¹⁹ m · … a quark has a size, it is smaller than this, [-under-] {+which is about+} a two-thousandth of the proton. Quarks are never found alone; …
Masses (MS-bar at 2 GeV): up 2.16 +/- 0.07 [-MeV,-] {+MeV/c^2,+} down 4.70 +/- 0.07 [-MeV.-] {+MeV/c^2.+} Two ups and a down add to 9.0 [-MeV:-] {+MeV/c^2:+} 1% of the proton's 938.3 [-MeV.-] {+MeV/c^2.+}
model
p.quark.3
A lattice-QCD breakdown of the proton's [-mass:-] {+mass (MS-bar at 2 GeV):+} the [-quarks'-] masses [-(through-] {+of all+} the {+quarks in it, the sea of short-lived quark-antiquark pairs (strange ones too) as well as the three, give 9% (the+} quark [-condensate, u, d and s) give 9%,-] {+condensate term);+} the quarks' energy of motion 33%, the gluon field's energy … they are massless in theory (a mass of a few [-MeV-] {+MeV/c^2+} is not excluded) and come in eight colour states.
… Colour is believed to be permanently confined: only colourless combinations [-(three quarks,-] {+exist on their own, usually three quarks+} or a quark and an [-antiquark) exist on their own.-] {+antiquark; some observed states are classed as four or five quarks.+}
outside source
p.quark.7
Squeezing quarks into 0.84 … is energy rather than quark mass.
inference
p.quark.8

## scale/p.quark/part/bound
The limit: if it has a size, it is smaller … a quark has a size, it is smaller than this, [-under-] {+which is about+} a two-thousandth of the proton. Quarks are never found alone; …
Masses (MS-bar at 2 GeV): up 2.16 +/- 0.07 [-MeV,-] {+MeV/c^2,+} down 4.70 +/- 0.07 [-MeV.-] {+MeV/c^2.+} Two ups and a down add to 9.0 [-MeV:-] {+MeV/c^2:+} 1% of the proton's 938.3 [-MeV.-] {+MeV/c^2.+}
model
p.quark.3
A lattice-QCD breakdown of the proton's [-mass:-] {+mass (MS-bar at 2 GeV):+} the [-quarks'-] masses [-(through-] {+of all+} the {+quarks in it, the sea of short-lived quark-antiquark pairs (strange ones too) as well as the three, give 9% (the+} quark [-condensate, u, d and s) give 9%,-] {+condensate term);+} the quarks' energy of motion 33%, the gluon field's energy … they are massless in theory (a mass of a few [-MeV-] {+MeV/c^2+} is not excluded) and come in eight colour states.
… Colour is believed to be permanently confined: only colourless combinations [-(three quarks,-] {+exist on their own, usually three quarks+} or a quark and an [-antiquark) exist on their own.-] {+antiquark; some observed states are classed as four or five quarks.+}
outside source
p.quark.7
Squeezing quarks into 0.84 … is energy rather than quark mass.
inference
p.quark.8

## scale/p.quark/part/point
the quark: a point. Space for details; Enter zooms in. … a quark has a size, it is smaller than this, [-under-] {+which is about+} a two-thousandth of the proton. Quarks are never found alone; …
Masses (MS-bar at 2 GeV): up 2.16 +/- 0.07 [-MeV,-] {+MeV/c^2,+} down 4.70 +/- 0.07 [-MeV.-] {+MeV/c^2.+} Two ups and a down add to 9.0 [-MeV:-] {+MeV/c^2:+} 1% of the proton's 938.3 [-MeV.-] {+MeV/c^2.+}
model
p.quark.3
A lattice-QCD breakdown of the proton's [-mass:-] {+mass (MS-bar at 2 GeV):+} the [-quarks'-] masses [-(through-] {+of all+} the {+quarks in it, the sea of short-lived quark-antiquark pairs (strange ones too) as well as the three, give 9% (the+} quark [-condensate, u, d and s) give 9%,-] {+condensate term);+} the quarks' energy of motion 33%, the gluon field's energy … they are massless in theory (a mass of a few [-MeV-] {+MeV/c^2+} is not excluded) and come in eight colour states.
… Colour is believed to be permanently confined: only colourless combinations [-(three quarks,-] {+exist on their own, usually three quarks+} or a quark and an [-antiquark) exist on their own.-] {+antiquark; some observed states are classed as four or five quarks.+}
outside source
p.quark.7
Squeezing quarks into 0.84 … is energy rather than quark mass.
inference
p.quark.8

## scale/package/part/body
The package and its lid. Space for details; Enter zooms … per °C (fit: 23.3 W x exp((T-80)/36)).
measured
[-card not recorded-] {+aifoundry2+}
et.leakage
By that fit, leakage doubles every 25 … saves so much.
textbook
chu.berkeley.edu ↗
el.dynamic

## scale/package/part/todie
The die under the lid: zoom in. Space for details; … per °C (fit: 23.3 W x exp((T-80)/36)).
measured
[-card not recorded-] {+aifoundry2+}
et.leakage
By that fit, leakage doubles every 25 … saves so much.
textbook
chu.berkeley.edu ↗
el.dynamic

## scale/rack/part/tohost
One of the rack’s machines: zoom in. Space for details; … channel.
measured
card not recorded
out.host.1
[-aifoundry2's motherboard is a-] {+All three hosts' motherboards are+} Gigabyte Z590 AORUS [-MASTER, an ATX board of-] {+MASTER boards, ATX,+} 30.5 x 24.4 [-cm. The other two hosts'-] {+cm; aifoundry1 and aifoundry2 run+} BIOS [-versions (F5, F6) follow Gigabyte's naming, but their board models are not recorded.-] {+F5, aifoundry3 F6.+}
[-inference-] {+documented+}
out.host.2
aifoundry1 holds two ET cards, the other … turbo (its PL2), the i5-11600 at 65 W base. The [-whole-] ET [-card, at most-] {+card's+} 88 [-W, draws-] {+W budget is+} less than the bigger CPU's base [-power,-] {+power+} and about a third of its turbo peak.
documented … high and 140 mm deep.
outside source
out.host.8

## scale/shire.bank/part/atomic
atomic unit, documented. Space for details; Enter zooms in.
… not waiting for a carry to ripple through 64 positions: {+the fastest+} prefix adders compute all the carries in about six levels … busy from the read through the operation to the write.

## scale/shire.bank/part/rbuf
read buffer, documented. Space for details; Enter zooms in.
… are installed on L2 and scratchpad read hits and served [-"without-] {+without+} touching the RAM panels, [-as these memory panels are slow-] {+which the specification calls "slow+} and power hungry". It is on by default and the … a read-buffer hit
47 cycles
from the panels

## scale/shire.bank/part/tol3
to_l3 master → the mesh (a miss), documented. Space for … clock and voltage through a VC FIFO with 2-stage synchronisers. [-The L3 tab-] {+Flow 1+} follows it.

## scale/shire.meshstop.router/here
YOU ARE HERE · ≈ 200 µm · 10⁻⁴ m … crosses the router's internal switch to which output each cycle. [-Each-] {+A minion shire's+} mesh stop has nine of them stacked as separate [-networks,-] {+networks (a memory shire's most likely seven),+} plus one for debug.

 Zoom into:
The … (5): point at one for its source

 Each {+minion, PCIe and I/O shire's+} mesh stop has 9 main-NoC routers (layers 0–8) plus one debug-NoC router; {+the NoC register map has 36 copies of layers 0–1 and 44 of layers 2–8, so the 8 memory shires' stops most likely have 7 (layers 2–8);+} routers have 8 ports (H, E, S, W, N, I, … card not recorded
no published page yet
L92

## scale/shire.meshstop.router/part/lib.mux2
Two-way multiplexer, documented. Space for details; Enter zooms in.
… a mux tree (128:1 per output bit, e.g. seven 2:1 {+levels, or three 4:1+} levels [-or four 4:1 levels),-] {+and one 2:1),+} and only the nodes whose value changes spend energy, so read energy depends on the data.
textbook
ml:l1:g.latch-read

## scale/shire.meshstop.router/part/shire.meshstop.router.buf
Input buffers, documented. Space for details; Enter zooms in.
… (3): point at one for its source

 Each {+minion, PCIe and I/O shire's+} mesh stop has 9 main-NoC routers (layers 0–8) plus one debug-NoC router; {+the NoC register map has 36 copies of layers 0–1 and 44 of layers 2–8, so the 8 memory shires' stops most likely have 7 (layers 2–8);+} routers have 8 ports (H, E, S, W, N, I, … (inverter pairs) every few hundred microns.
textbook
ml:l3:g.router

## scale/shire.meshstop.xing/here
YOU ARE HERE · ≈ 50 µm · 10⁻⁵ m

 Voltage and clock crossing (VCFIFO)

 The [-shire's-] {+shire+} cache runs [-at-] {+on the shire clock, its arrays on the+} 0.705 V [-on-] {+SRAM rail (the rail of+} its [-own clock,-] {+logic is not documented);+} the network {+runs+} at 0.485 V and 400 MHz. Every bit [-that crosses-] is [-shifted-] {+level-shifted as it crosses; each word waits+} in [-voltage-] {+a small FIFO whose write+} and [-re-timed-] {+read counts, not the data, pass+} through [-two flip-flops-] {+two-flip-flop synchronisers+} into the other clock, so {+a word is read only once+} it [-cannot be caught half-changed.-] {+is completely written.+}

 Zoom into:
The [-FinFET transistor-] {+inverter (NOT gate)+} (+)
The [-inverter (NOT gate)-] {+FinFET transistor+}
The flip-flop (register bit)
↑ Zoom out to [-minion 0 of neighbourhood 0-] {+the mesh stop+} (Backspace)
More detail and the sources

 Its … facts (5): point at one for its source

 [-The neighbourhood's per-bank output-] {+Each shire meets the mesh with 4 L3-slave ports (incoming L3 and remote-scratchpad requests, 512 bits, one request per cycle each), 4 to_l3 master ports and 1 to_sys master port (to memory). AXI channels cross into the NoC through voltage-changing+} FIFOs [-double as the clock- and voltage-crossing elements: semi-synchronous VC FIFOs from the cell library,-] with [-level shifters built in at the HV/LV boundary. Their storage cells always sit in the HV region 'as performance and access time improve with the voltage'. Responses cross back through a VC FIFO at the neighbourhood's input.-] {+2-stage synchronizers.+}
documented
[-ml:l2:l2.vc-fifo-] {+spec v1.1
Heat per millimetre ↗
ml:l3:l3.ports+}
The Shire Channel, which holds the shire cache, the … and a 2-flip-flop synchroniser (as the spec's VCFIFO uses) samples [-it-] {+the FIFO's gray-coded counts+} in the receiving clock, costing 2-3 receiving-clock cycles.
textbook … measured
three cards
Memory hierarchy ↗
ml:scp:scp.lat-remote

## scale/shire.meshstop.xing/part/bitE
(new)
```
energy per bit, documented. Space for details; Enter zooms in.
L3 · MESH HOP

A link

The simplest logic gate: one p-type transistor pulls the output up when the input is 0, one n-type pulls it down when the input is 1. Output is always the opposite of the input.

Zoom in:
The inverter (NOT gate) (double-click)
More detail and the sources

documented the energy, the length generic repeaters

One hop is about 3.72 mm of wire, broken by repeaters. A random bit costs 36.7 fJ per mm on the mesh rail, so a 64-byte reply over one hop is 70 pJ on the mesh rail (derived); measured on board power, a hop adds 115 pJ per line on random data and 43 on zeros. Zeros do not toggle the wires: they cost several times less.
```

## scale/shire.meshstop.xing/part/fifo
(gone)
```
The neighbourhood's bank FIFO: a VC FIFO whose cells sit in the HV region, with level shifters at the edge; documented. Space for details; Enter zooms in.
L2 · SHIRE

Bank FIFOs: the crossing

Two latches back to back: the value changes only at the clock's rising edge. Pipelines are chains of logic between rows of flip-flops.

Zoom in:
The flip-flop (register bit) (double-click)
More detail and the sources

documented the crossing exists generic the circuit

The neighbourhood's per-bank output FIFOs double as the clock and voltage crossing: semi-synchronous VC FIFOs from the cell library, with level shifters built in at the LV/HV edge; their cells sit in the HV region "as performance and access time improve with the voltage". Responses cross back through a VC FIFO at the neighbourhood's input.
```

## scale/shire.meshstop.xing/part/ls
The level shifter: a cross-coupled PMOS pair on the high rail over an NMOS differential pair; generic. Space for details; Enter zooms in.
[-L2-] {+L3+} · [-CROSSING-] {+TRANSISTORS+}

 The level shifter

 The switch everything is made of. A voltage on the gate decides whether current flows: {+in an n-type transistor,+} at 0 V the path along the fin is shut; … pulls a thin sheet of electrons into the fin, and [-current flows-] {+they flow+} from source to [-drain.-] {+drain (the current, by convention, from drain to source).+} The gate drapes over the fins on three sides.
…
generic textbook documented that it is there

 {+The reply arrives at the mesh rail's swing, 485 mV, and must drive the Shire Channel's logic, whose rail is asked (its SRAM arrays sit on 705 mV).+} A [-request bit leaves the minion rail at 0.517 V and enters the HV region. A low-to-high shifter is typically a-] cross-coupled PMOS pair on the high rail {+over an NMOS pair+} driven by [-an NMOS differential pair:-] {+the signal and its complement:+} the input pulls one side down and the [-PMOS-] pair snaps the other {+up+} to the high [-rail (textbook).-] {+rail.+} The ET RTL models it as a buffer; the physical cell [-and the HV logic's rail are-] {+is+} not documented.

## scale/shire.meshstop.xing/part/lsin
(new)
```
The input inverter, on the mesh rail; generic. Space for details; Enter zooms in.
L3 · TRANSISTORS

The level shifter

The simplest logic gate: one p-type transistor pulls the output up when the input is 0, one n-type pulls it down when the input is 1. Output is always the opposite of the input.

Zoom in:
The inverter (NOT gate) (double-click)
More detail and the sources

generic textbook documented that it is there

The reply arrives at the mesh rail's swing, 485 mV, and must drive the Shire Channel's logic, whose rail is asked (its SRAM arrays sit on 705 mV). A cross-coupled PMOS pair on the high rail over an NMOS pair driven by the signal and its complement: the input pulls one side down and the pair snaps the other up to the high rail. The ET RTL models it as a buffer; the physical cell is not documented.
```

## scale/shire.meshstop.xing/part/lvin
(gone)
```
The input inverter, on the minion rail; generic. Space for details; Enter zooms in.
L2 · CROSSING

The level shifter

The simplest logic gate: one p-type transistor pulls the output up when the input is 0, one n-type pulls it down when the input is 1. Output is always the opposite of the input.

Zoom in:
The inverter (NOT gate) (double-click)
More detail and the sources

generic textbook documented that it is there

A request bit leaves the minion rail at 0.517 V and enters the HV region. A low-to-high shifter is typically a cross-coupled PMOS pair on the high rail driven by an NMOS differential pair: the input pulls one side down and the PMOS pair snaps the other to the high rail (textbook). The ET RTL models it as a buffer; the physical cell and the HV logic's rail are not documented.
```

## scale/shire.meshstop.xing/part/rep1
(new)
```
Repeater, first inverter: a CMOS inverter, a PMOS and an NMOS; generic. Space for details; Enter zooms in.
L3 · TRANSISTORS

A repeater

The simplest logic gate: one p-type transistor pulls the output up when the input is 0, one n-type pulls it down when the input is 1. Output is always the opposite of the input.

Zoom in:
The inverter (NOT gate) (double-click)
More detail and the sources

generic textbook

Long wires are broken every few hundred microns by inverters. When the data goes 0 → 1, a PMOS charges the next stretch of wire from the mesh rail (485 mV); a 0 after a 0 moves nothing. That is why random data costs several times zeros on the mesh.
```

## scale/shire.meshstop.xing/part/rep2
(new)
```
Repeater, next inverter: a CMOS inverter, a PMOS and an NMOS; generic. Space for details; Enter zooms in.
L3 · TRANSISTORS

A repeater

The simplest logic gate: one p-type transistor pulls the output up when the input is 0, one n-type pulls it down when the input is 1. Output is always the opposite of the input.

Zoom in:
The inverter (NOT gate) (double-click)
More detail and the sources

generic textbook

Long wires are broken every few hundred microns by inverters. When the data goes 0 → 1, a PMOS charges the next stretch of wire from the mesh rail (485 mV); a 0 after a 0 moves nothing. That is why random data costs several times zeros on the mesh.
```

## scale/shire.meshstop.xing/part/sync
[-A two-flip-flop synchroniser in the receiving clock; generic circuit.-] {+then a VC FIFO, documented.+} Space for details; Enter zooms in.
[-L2-] {+L3+} · CROSSING

 The [-level shifter-] {+VC FIFO into the shire clock+}

 [-The switch everything is made of. A voltage on-] {+Two latches back to back:+} the [-gate decides whether current flows: at 0 V the path along the fin is shut;-] {+value changes only+} at the [-supply rail (0.517 V on a minion) the gate's field pulls a thin sheet-] {+clock's rising edge. Pipelines are chains+} of [-electrons into the fin, and current flows from source to drain. The gate drapes over the fins on three sides.-] {+logic between rows of flip-flops.+}

 Zoom in:
The [-FinFET transistor-] {+flip-flop (register bit)+} (double-click)
More detail and the sources

 {+documented spec+} generic textbook [-documented that-] {+

The reply's words are written into a small FIFO on the mesh's clock and read out on the shire clock; only the FIFO's write and read counts pass through two-flip-flop synchronisers (the Shire Cache Specification's VCFIFO "uses 2-stage synchronizers"), so a word is read only once+} it is [-there

 A request bit leaves the minion rail at 0.517 V and enters the HV region. A low-to-high shifter is typically a cross-coupled PMOS pair on the high rail driven by an NMOS differential pair: the input pulls one side down and the PMOS pair snaps the other to the high rail (textbook). The ET RTL models it as a buffer; the physical cell and the HV logic's rail are not documented.-] {+completely written.+}

## scale/shire.meshstop.xing/part/wireC
(new)
```
The wire between two repeaters: its capacitance must be charged on every 0-to-1 transition; generic. Space for details; Enter zooms in.
L3 · TRANSISTORS

A repeater

The chip's finest wires are copper, about 20 nm wide and 40 nm apart, wrapped in a thin cobalt liner so that copper atoms do not wander; cobalt contacts take them down to the transistors.

Zoom in:
The copper wiring, in section (double-click)
More detail and the sources

generic textbook

Long wires are broken every few hundred microns by inverters. When the data goes 0 → 1, a PMOS charges the next stretch of wire from the mesh rail (485 mV); a 0 after a 0 moves nothing. That is why random data costs several times zeros on the mesh.
```

## scale/shire.meshstop/here
YOU ARE HERE · ≈ 500 µm · 10⁻⁴ m … three cards
On-chip communication ↗
mesh.single-attach
Each {+minion, PCIe and I/O shire's+} mesh stop has 9 main-NoC routers (layers 0–8) plus one debug-NoC router; {+the NoC register map has 36 copies of layers 0–1 and 44 of layers 2–8, so the 8 memory shires' stops most likely have 7 (layers 2–8);+} routers have 8 ports (H, E, S, W, N, I, … 4 to_l3 master and 4 L3 slave lanes to the [-mesh;-] {+mesh. An L3 request takes+} the lane [-is chosen by PA[7:6],-] {+of the bank it will use at its home, PA[12:11] under the default swizzle,+} so {+all 16 lines of an aligned 1 KB load share one lane; only a remote-scratchpad request takes the lane PA[7:6] names, so its+} lines i and i+4 share a lane [-(a 1 KB load puts 4 of its 16 lines on each).-] {+(re-implementation RTL, to confirm in silicon).+}
documented {+
 re-implementation RTL+}
Heat per millimetre ↗
L103
Every shire's … by its boot service)
Memory hierarchy ↗
mesh.clock

## scale/shire.meshstop/part/lib.mux2
Two-way multiplexer, documented. Space for details; Enter zooms in.
… a mux tree (128:1 per output bit, e.g. seven 2:1 {+levels, or three 4:1+} levels [-or four 4:1 levels),-] {+and one 2:1),+} and only the nodes whose value changes spend energy, so read energy depends on the data.
textbook
ml:l1:g.latch-read

## scale/shire.meshstop/part/shire.meshstop.router
Router, documented. Space for details; Enter zooms in.
MESH … crosses the router's internal switch to which output each cycle. [-Each-] {+A minion shire's+} mesh stop has nine of them stacked as separate [-networks,-] {+networks (a memory shire's most likely seven),+} plus one for debug.

 Zoom in:
The … (5): point at one for its source

 Each {+minion, PCIe and I/O shire's+} mesh stop has 9 main-NoC routers (layers 0–8) plus one debug-NoC router; {+the NoC register map has 36 copies of layers 0–1 and 44 of layers 2–8, so the 8 memory shires' stops most likely have 7 (layers 2–8);+} routers have 8 ports (H, E, S, W, N, I, … card not recorded
no published page yet
L92

## scale/shire.meshstop/part/shire.meshstop.xing
Voltage and clock crossing, documented. Space for details; Enter zooms …

 Voltage and clock crossing (VCFIFO)

 The [-shire's-] {+shire+} cache runs [-at-] {+on the shire clock, its arrays on the+} 0.705 V [-on-] {+SRAM rail (the rail of+} its [-own clock,-] {+logic is not documented);+} the network {+runs+} at 0.485 V and 400 MHz. Every bit [-that crosses-] is [-shifted-] {+level-shifted as it crosses; each word waits+} in [-voltage-] {+a small FIFO whose write+} and [-re-timed-] {+read counts, not the data, pass+} through [-two flip-flops-] {+two-flip-flop synchronisers+} into the other clock, so {+a word is read only once+} it [-cannot be caught half-changed.-] {+is completely written.+}

 Zoom in:
The voltage and clock crossing … facts (5): point at one for its source

 [-The neighbourhood's per-bank output-] {+Each shire meets the mesh with 4 L3-slave ports (incoming L3 and remote-scratchpad requests, 512 bits, one request per cycle each), 4 to_l3 master ports and 1 to_sys master port (to memory). AXI channels cross into the NoC through voltage-changing+} FIFOs [-double as the clock- and voltage-crossing elements: semi-synchronous VC FIFOs from the cell library,-] with [-level shifters built in at the HV/LV boundary. Their storage cells always sit in the HV region 'as performance and access time improve with the voltage'. Responses cross back through a VC FIFO at the neighbourhood's input.-] {+2-stage synchronizers.+}
documented
[-ml:l2:l2.vc-fifo-] {+spec v1.1
Heat per millimetre ↗
ml:l3:l3.ports+}
The Shire Channel, which holds the shire cache, the … and a 2-flip-flop synchroniser (as the spec's VCFIFO uses) samples [-it-] {+the FIFO's gray-coded counts+} in the receiving clock, costing 2-3 receiving-clock cycles.
textbook … measured
three cards
Memory hierarchy ↗
ml:scp:scp.lat-remote

## scale/shire.neigh.xing/here
(new)
```
YOU ARE HERE · ≈ 50 µm · 10⁻⁵ m

Bank FIFOs: the voltage and clock crossing

The neighbourhood's bank FIFOs are the crossing: semi-synchronous VC FIFOs whose cells sit in the HV region, with level shifters at the edge. The neighbourhood's clock is the shire clock shifted half a cycle by the DLL, so a word is handed over on a known edge and needs no synchroniser.

Zoom into:
The FinFET transistor (+)
The inverter (NOT gate)
The flip-flop (register bit)
↑ Zoom out to minion 0 of neighbourhood 0 (Backspace)
More detail and the sources

Its size: order of magnitude: five output FIFOs (four for the banks, one for the UC block) of three 256-bit entries, with level shifters at the edge

Erbium RTL Some facts here come from core-et’s RTL on its Erbium branch: the same Minion core lineage as the ET-SoC-1, in a later configuration; that the silicon matches it is not confirmed.

The facts (4): point at one for its source

The neighbourhood's per-bank output FIFOs double as the clock- and voltage-crossing elements: semi-synchronous VC FIFOs from the cell library, with level shifters built in at the HV/LV boundary. Their storage cells always sit in the HV region 'as performance and access time improve with the voltage'. Responses cross back through a VC FIFO at the neighbourhood's input.
documented
ml:l2:l2.vc-fifo
The neighbourhood clock is the shire clock shifted by 180 degrees, made by the DLL from the same source, so the two domains meet at a semi-synchronous interface: ET-Link requests and responses cross in semi-synchronous FIFOs, which take advantage of the two clocks being one clock shifted by a constant 180 degrees.
documented
in.shire.neigh.xing.2
Four bank FIFOs and a UC FIFO, three entries each, end the request datapath; a 512-bit request takes two consecutive entries, and its halves are re-joined into one 512-bit ET-Link request at the FIFO's output, in the HV region.
documented
in.shire.neigh.xing.3
The cell library's semi-synchronous VC FIFO, written on the low-voltage side and read on the high-voltage side (vcfifo_wr_lov_ss), works only at a 1:1 clock ratio with the two clocks offset by a DLL, for "guaranteed signal hand-off between edges without any meta-stability"; its minimum latency is 1.5 cycles.
documented
Erbium RTL
in.shire.neigh.xing.4
```

## scale/shire.neigh.xing/part/fifo
(new)
```
The neighbourhood's bank FIFO: a VC FIFO whose cells sit in the HV region, with level shifters at the edge; documented. Space for details; Enter zooms in.
L2 · SHIRE

Bank FIFOs: the crossing

Two latches back to back: the value changes only at the clock's rising edge. Pipelines are chains of logic between rows of flip-flops.

Zoom in:
The flip-flop (register bit) (double-click)
More detail and the sources

documented the crossing exists generic the circuit

The neighbourhood's per-bank output FIFOs double as the clock and voltage crossing: semi-synchronous VC FIFOs from the cell library, with level shifters built in at the LV/HV edge; their cells sit in the HV region "as performance and access time improve with the voltage". Responses cross back through a VC FIFO at the neighbourhood's input.
```

## scale/shire.neigh.xing/part/ls
(new)
```
The level shifter: a cross-coupled PMOS pair on the high rail over an NMOS differential pair; generic. Space for details; Enter zooms in.
L2 · CROSSING

The level shifter

The switch everything is made of. A voltage on the gate decides whether current flows: in an n-type transistor, at 0 V the path along the fin is shut; at the supply rail (0.517 V on a minion) the gate's field pulls a thin sheet of electrons into the fin, and they flow from source to drain (the current, by convention, from drain to source). The gate drapes over the fins on three sides.

Zoom in:
The FinFET transistor (double-click)
More detail and the sources

generic textbook documented that it is there

A request bit leaves the minion rail at 0.517 V and enters the HV region. A low-to-high shifter is typically a cross-coupled PMOS pair on the high rail driven by an NMOS differential pair: the input pulls one side down and the PMOS pair snaps the other to the high rail (textbook). The ET RTL models it as a buffer; the physical cell and the HV logic's rail are not documented.
```

## scale/shire.neigh.xing/part/lvin
(new)
```
The input inverter, on the minion rail; generic. Space for details; Enter zooms in.
L2 · CROSSING

The level shifter

The simplest logic gate: one p-type transistor pulls the output up when the input is 0, one n-type pulls it down when the input is 1. Output is always the opposite of the input.

Zoom in:
The inverter (NOT gate) (double-click)
More detail and the sources

generic textbook documented that it is there

A request bit leaves the minion rail at 0.517 V and enters the HV region. A low-to-high shifter is typically a cross-coupled PMOS pair on the high rail driven by an NMOS differential pair: the input pulls one side down and the PMOS pair snaps the other to the high rail (textbook). The ET RTL models it as a buffer; the physical cell and the HV logic's rail are not documented.
```

## scale/shire.neigh.xing/part/sync
(new)
```
A hand-off register on the shire clock: the two clocks are one clock 180° apart, so no synchroniser; documented. Space for details; Enter zooms in.
L2 · CROSSING

The hand-off register

Two latches back to back: the value changes only at the clock's rising edge. Pipelines are chains of logic between rows of flip-flops.

Zoom in:
The flip-flop (register bit) (double-click)
More detail and the sources

documented semi-synchronous generic the circuit

The neighbourhood clock is the shire clock shifted 180° by the DLL: one clock, two phases. So the bank FIFO is semi-synchronous: a word written on the neighbourhood clock is taken on a known edge of the shire clock by an ordinary register, with no synchroniser and no chance of being caught half-changed.
```

## scale/shire.neigh/part/lib.adder
Adder, documented. Space for details; Enter zooms in.
NEIGHBOURHOOD … not waiting for a carry to ripple through 64 positions: {+the fastest+} prefix adders compute all the carries in about six levels … point at one for its source

 Parallel-prefix adders [-(Kogge-Stone, Sklansky, Brent-Kung)-] compute [-carries-] {+every carry in a tree of generate/propagate cells: Kogge-Stone and Sklansky+} in log2(N) {+levels, Brent-Kung in 2 log2(N) - 1+} levels [-of generate/propagate cells.-] {+with fewer cells and wires.+}
textbook
in.lib.adder.1
A parallel-prefix adder computes for … cells (G = Gi + Pi·Gj, P = Pi·Pj) of {+as few as+} log2 n levels, and forms each sum bit as p … cell driving at most two others.
textbook
tb.kogge

## scale/shire.neigh/part/lib.sram6t
6T cell, documented. Space for details; Enter zooms in.
… V on die; firmware limits 0.66-0.85 V.
measured
[-card not recorded-] {+aifoundry2+}
et.v-sram
Esperanto designed its own low-voltage memory cells … latch arrays.)
outside source
fuse.wikichip.org ↗
et.custom-sram

## scale/shire.neigh/part/minion
M0, documented. Space for details; Enter zooms in.
NEIGHBOURHOOD … 6, neighbourhood = (hartid mod 64) >> 4, minion = {+(hartid mod 64) >> 1 (the firmware's get_minion_id(),+} hartid >> 1, {+numbers the minions chip-wide),+} thread = hartid & 1).
documented
On-chip communication … V at 800); firmware limits 0.40-0.62 V.
measured
[-card not recorded-] {+aifoundry2+}
et.v-minion
At the minion rail's 0.517 V each … 10 mW per minion at 1 GHz and 0.425 V, [-i.e.-] {+with+} 0.04 nF switched per cycle (vs 2.2 nF for a 3 GHz x86 [-core).-] {+core); 0.04 nF at 0.425 V and 1 GHz is 7.2 mW, the slide's formula adding leakage for the rest.+}
documented
hc33.hotchips.org ↗
et.cdyn-target
Measured switched … on zeros), against the 0.04 nF target.
measured
[-card not recorded-] {+aifoundry2+}
et.cdyn-measured
Each cycle of a minion on random … (45 pJ).
model
et.electrons-per-cycle
At most about [-15-] {+15.6+} million transistors per minion: what is left after the shire … run 600-800 MHz.
documented
hc33.hotchips.org ↗
et.range

## scale/shire.neigh/part/minion#2
M1, documented. Space for details; Enter zooms in.
NEIGHBOURHOOD … 6, neighbourhood = (hartid mod 64) >> 4, minion = {+(hartid mod 64) >> 1 (the firmware's get_minion_id(),+} hartid >> 1, {+numbers the minions chip-wide),+} thread = hartid & 1).
documented
On-chip communication … V at 800); firmware limits 0.40-0.62 V.
measured
[-card not recorded-] {+aifoundry2+}
et.v-minion
At the minion rail's 0.517 V each … 10 mW per minion at 1 GHz and 0.425 V, [-i.e.-] {+with+} 0.04 nF switched per cycle (vs 2.2 nF for a 3 GHz x86 [-core).-] {+core); 0.04 nF at 0.425 V and 1 GHz is 7.2 mW, the slide's formula adding leakage for the rest.+}
documented
hc33.hotchips.org ↗
et.cdyn-target
Measured switched … on zeros), against the 0.04 nF target.
measured
[-card not recorded-] {+aifoundry2+}
et.cdyn-measured
Each cycle of a minion on random … (45 pJ).
model
et.electrons-per-cycle
At most about [-15-] {+15.6+} million transistors per minion: what is left after the shire … run 600-800 MHz.
documented
hc33.hotchips.org ↗
et.range

## scale/shire.neigh/part/minion#3
M2, documented. Space for details; Enter zooms in.
NEIGHBOURHOOD … 6, neighbourhood = (hartid mod 64) >> 4, minion = {+(hartid mod 64) >> 1 (the firmware's get_minion_id(),+} hartid >> 1, {+numbers the minions chip-wide),+} thread = hartid & 1).
documented
On-chip communication … V at 800); firmware limits 0.40-0.62 V.
measured
[-card not recorded-] {+aifoundry2+}
et.v-minion
At the minion rail's 0.517 V each … 10 mW per minion at 1 GHz and 0.425 V, [-i.e.-] {+with+} 0.04 nF switched per cycle (vs 2.2 nF for a 3 GHz x86 [-core).-] {+core); 0.04 nF at 0.425 V and 1 GHz is 7.2 mW, the slide's formula adding leakage for the rest.+}
documented
hc33.hotchips.org ↗
et.cdyn-target
Measured switched … on zeros), against the 0.04 nF target.
measured
[-card not recorded-] {+aifoundry2+}
et.cdyn-measured
Each cycle of a minion on random … (45 pJ).
model
et.electrons-per-cycle
At most about [-15-] {+15.6+} million transistors per minion: what is left after the shire … run 600-800 MHz.
documented
hc33.hotchips.org ↗
et.range

## scale/shire.neigh/part/minion#4
M3, documented. Space for details; Enter zooms in.
NEIGHBOURHOOD … 6, neighbourhood = (hartid mod 64) >> 4, minion = {+(hartid mod 64) >> 1 (the firmware's get_minion_id(),+} hartid >> 1, {+numbers the minions chip-wide),+} thread = hartid & 1).
documented
On-chip communication … V at 800); firmware limits 0.40-0.62 V.
measured
[-card not recorded-] {+aifoundry2+}
et.v-minion
At the minion rail's 0.517 V each … 10 mW per minion at 1 GHz and 0.425 V, [-i.e.-] {+with+} 0.04 nF switched per cycle (vs 2.2 nF for a 3 GHz x86 [-core).-] {+core); 0.04 nF at 0.425 V and 1 GHz is 7.2 mW, the slide's formula adding leakage for the rest.+}
documented
hc33.hotchips.org ↗
et.cdyn-target
Measured switched … on zeros), against the 0.04 nF target.
measured
[-card not recorded-] {+aifoundry2+}
et.cdyn-measured
Each cycle of a minion on random … (45 pJ).
model
et.electrons-per-cycle
At most about [-15-] {+15.6+} million transistors per minion: what is left after the shire … run 600-800 MHz.
documented
hc33.hotchips.org ↗
et.range

## scale/shire.neigh/part/minion#5
M4, documented. Space for details; Enter zooms in.
NEIGHBOURHOOD … 6, neighbourhood = (hartid mod 64) >> 4, minion = {+(hartid mod 64) >> 1 (the firmware's get_minion_id(),+} hartid >> 1, {+numbers the minions chip-wide),+} thread = hartid & 1).
documented
On-chip communication … V at 800); firmware limits 0.40-0.62 V.
measured
[-card not recorded-] {+aifoundry2+}
et.v-minion
At the minion rail's 0.517 V each … 10 mW per minion at 1 GHz and 0.425 V, [-i.e.-] {+with+} 0.04 nF switched per cycle (vs 2.2 nF for a 3 GHz x86 [-core).-] {+core); 0.04 nF at 0.425 V and 1 GHz is 7.2 mW, the slide's formula adding leakage for the rest.+}
documented
hc33.hotchips.org ↗
et.cdyn-target
Measured switched … on zeros), against the 0.04 nF target.
measured
[-card not recorded-] {+aifoundry2+}
et.cdyn-measured
Each cycle of a minion on random … (45 pJ).
model
et.electrons-per-cycle
At most about [-15-] {+15.6+} million transistors per minion: what is left after the shire … run 600-800 MHz.
documented
hc33.hotchips.org ↗
et.range

## scale/shire.neigh/part/minion#6
M5, documented. Space for details; Enter zooms in.
NEIGHBOURHOOD … 6, neighbourhood = (hartid mod 64) >> 4, minion = {+(hartid mod 64) >> 1 (the firmware's get_minion_id(),+} hartid >> 1, {+numbers the minions chip-wide),+} thread = hartid & 1).
documented
On-chip communication … V at 800); firmware limits 0.40-0.62 V.
measured
[-card not recorded-] {+aifoundry2+}
et.v-minion
At the minion rail's 0.517 V each … 10 mW per minion at 1 GHz and 0.425 V, [-i.e.-] {+with+} 0.04 nF switched per cycle (vs 2.2 nF for a 3 GHz x86 [-core).-] {+core); 0.04 nF at 0.425 V and 1 GHz is 7.2 mW, the slide's formula adding leakage for the rest.+}
documented
hc33.hotchips.org ↗
et.cdyn-target
Measured switched … on zeros), against the 0.04 nF target.
measured
[-card not recorded-] {+aifoundry2+}
et.cdyn-measured
Each cycle of a minion on random … (45 pJ).
model
et.electrons-per-cycle
At most about [-15-] {+15.6+} million transistors per minion: what is left after the shire … run 600-800 MHz.
documented
hc33.hotchips.org ↗
et.range

## scale/shire.neigh/part/minion#7
M6, documented. Space for details; Enter zooms in.
NEIGHBOURHOOD … 6, neighbourhood = (hartid mod 64) >> 4, minion = {+(hartid mod 64) >> 1 (the firmware's get_minion_id(),+} hartid >> 1, {+numbers the minions chip-wide),+} thread = hartid & 1).
documented
On-chip communication … V at 800); firmware limits 0.40-0.62 V.
measured
[-card not recorded-] {+aifoundry2+}
et.v-minion
At the minion rail's 0.517 V each … 10 mW per minion at 1 GHz and 0.425 V, [-i.e.-] {+with+} 0.04 nF switched per cycle (vs 2.2 nF for a 3 GHz x86 [-core).-] {+core); 0.04 nF at 0.425 V and 1 GHz is 7.2 mW, the slide's formula adding leakage for the rest.+}
documented
hc33.hotchips.org ↗
et.cdyn-target
Measured switched … on zeros), against the 0.04 nF target.
measured
[-card not recorded-] {+aifoundry2+}
et.cdyn-measured
Each cycle of a minion on random … (45 pJ).
model
et.electrons-per-cycle
At most about [-15-] {+15.6+} million transistors per minion: what is left after the shire … run 600-800 MHz.
documented
hc33.hotchips.org ↗
et.range

## scale/shire.neigh/part/minion#8
M7, documented. Space for details; Enter zooms in.
NEIGHBOURHOOD … 6, neighbourhood = (hartid mod 64) >> 4, minion = {+(hartid mod 64) >> 1 (the firmware's get_minion_id(),+} hartid >> 1, {+numbers the minions chip-wide),+} thread = hartid & 1).
documented
On-chip communication … V at 800); firmware limits 0.40-0.62 V.
measured
[-card not recorded-] {+aifoundry2+}
et.v-minion
At the minion rail's 0.517 V each … 10 mW per minion at 1 GHz and 0.425 V, [-i.e.-] {+with+} 0.04 nF switched per cycle (vs 2.2 nF for a 3 GHz x86 [-core).-] {+core); 0.04 nF at 0.425 V and 1 GHz is 7.2 mW, the slide's formula adding leakage for the rest.+}
documented
hc33.hotchips.org ↗
et.cdyn-target
Measured switched … on zeros), against the 0.04 nF target.
measured
[-card not recorded-] {+aifoundry2+}
et.cdyn-measured
Each cycle of a minion on random … (45 pJ).
model
et.electrons-per-cycle
At most about [-15-] {+15.6+} million transistors per minion: what is left after the shire … run 600-800 MHz.
documented
hc33.hotchips.org ↗
et.range

## scale/shire.neigh/part/shire.neigh.req
Request path to the banks, documented. Space for details; Enter … datapath is 256 bits wide (a 512-bit write takes two [-cycles-] {+cycles, crosses the bank FIFO as two 256-bit entries+} and is re-joined [-before the bank FIFO);-] {+into one 512-bit ET-Link request at its output);+} its response datapath and the ET-Link into each bank are … cycles).
documented
no published page yet
shire.neigh-link

## scale/shire.neigh/part/shire.neigh.xing
(new)
```
Bank FIFOs, documented. Space for details; Enter zooms in.
NEIGHBOURHOOD 0 · PART

Bank FIFOs: the voltage and clock crossing

The neighbourhood's bank FIFOs are the crossing: semi-synchronous VC FIFOs whose cells sit in the HV region, with level shifters at the edge. The neighbourhood's clock is the shire clock shifted half a cycle by the DLL, so a word is handed over on a known edge and needs no synchroniser.

Zoom in:
The bank FIFOs (double-click)
More detail and the sources

The facts (4): point at one for its source

The neighbourhood's per-bank output FIFOs double as the clock- and voltage-crossing elements: semi-synchronous VC FIFOs from the cell library, with level shifters built in at the HV/LV boundary. Their storage cells always sit in the HV region 'as performance and access time improve with the voltage'. Responses cross back through a VC FIFO at the neighbourhood's input.
documented
ml:l2:l2.vc-fifo
The neighbourhood clock is the shire clock shifted by 180 degrees, made by the DLL from the same source, so the two domains meet at a semi-synchronous interface: ET-Link requests and responses cross in semi-synchronous FIFOs, which take advantage of the two clocks being one clock shifted by a constant 180 degrees.
documented
in.shire.neigh.xing.2
Four bank FIFOs and a UC FIFO, three entries each, end the request datapath; a 512-bit request takes two consecutive entries, and its halves are re-joined into one 512-bit ET-Link request at the FIFO's output, in the HV region.
documented
in.shire.neigh.xing.3
The cell library's semi-synchronous VC FIFO, written on the low-voltage side and read on the high-voltage side (vcfifo_wr_lov_ss), works only at a 1:1 clock ratio with the two clocks offset by a DLL, for "guaranteed signal hand-off between edges without any meta-stability"; its minimum latency is 1.5 cycles.
documented
Erbium RTL
in.shire.neigh.xing.4
```

## scale/shire.panel/here
YOU ARE HERE · ≈ 150 µm · 10⁻⁴ m … bits); a sub-bank's data RAM is 4,096 rows addressed by [-{way, set}.-] {+{set, way} (set-major, as the re-implementation's RTL has it; the Erbium header fixes only the width, way + set bits).+}
documented
spec v1.1
ml:l2:l2.data-ram
The tag-state, … 4), each 589,824 bits; 37.7 Mbit per shire including ECC [-(32-] {+(33.55+} Mbit data + [-4-] {+4.19+} Mbit ECC); 2,048 data panels over the 32 compute shires. … ones taped out.
unknown
spec v1.1
ml:l2:l2.storage-question

## scale/shire.panel/part/olat
out latch · write drivers; generic. Space for details; Enter zooms in.
L2 · CELL

 [-Sense amplifier-] {+Output latch and write drivers+}

 A bit of memory made of logic: two … detail and the sources

 generic textbook

 [-A cross-coupled-] {+Once the sense amplifier has resolved, a+} latch [-with an NMOS tail: when SAE fires it resolves-] {+holds each bit for+} the [-small difference between-] {+macro's 144-bit output until+} the [-bitlines-] {+next read; on a write, drivers pull one bitline of each written column low+} to [-full swing. Read-margin settings delay SAE so more swing develops, slower and safer at low voltage-] {+flip the cell+} (textbook).

## scale/shire.subbank/part/rowaddr
row [-2,642,-] {+{set, way},+} documented. Space for details; Enter zooms in.
L2 · … which puts the L2 in rows 2,560–3,071 of each panel; {+no ET document fixes+} the [-L2 file writes "{way, set}", a conflict listed under the diagram).-] {+order).+}

## scale/shire.uc/here
YOU ARE HERE · ≈ 200 µm · 10⁻⁴ m … coordination: barrier counters (everyone waits until all have arrived), credit [-counters,-] {+increments,+} interrupts between cores, and atomic operations that do not go …
One hot line stops a shire ↗
hot-cost

## scale/shire.uc/part/lib.adder
Adder, documented. Space for details; Enter zooms in.
UC … not waiting for a carry to ripple through 64 positions: {+the fastest+} prefix adders compute all the carries in about six levels … point at one for its source

 Parallel-prefix adders [-(Kogge-Stone, Sklansky, Brent-Kung)-] compute [-carries-] {+every carry in a tree of generate/propagate cells: Kogge-Stone and Sklansky+} in log2(N) {+levels, Brent-Kung in 2 log2(N) - 1+} levels [-of generate/propagate cells.-] {+with fewer cells and wires.+}
textbook
in.lib.adder.1
A parallel-prefix adder computes for … cells (G = Gi + Pi·Gj, P = Pi·Pj) of {+as few as+} log2 n levels, and forms each sum bit as p … cell driving at most two others.
textbook
tb.kogge

## scale/shire.uc/part/shire.uc.fcc
[-Fast credit counters,-] {+Credit increments,+} documented. Space for details; Enter zooms in.
UC BLOCK · PART

 [-Fast credit counters-] {+Credit increments (CREDINC0-3)+}

 [-Per-thread counters-] {+Four registers (CREDINC0-3)+} that [-other threads-] {+any thread+} can [-add credits to;-] {+write with+} a {+mask of minions; each write adds a credit to the chosen harts' counters, which sit in the minions themselves (two per hart). A+} thread that reads its counter takes a credit, or waits until one arrives. [-A cheap way to say "your data is ready".-]

 Zoom in:
The [-counter-] {+decoder+} (double-click)
More detail and the sources

 The … no credit blocks until one arrives.
documented
in.shire.uc.fcc.1

## scale/shire.xbar/part/lib.mux2
Two-way multiplexer, documented. Space for details; Enter zooms in.
… a mux tree (128:1 per output bit, e.g. seven 2:1 {+levels, or three 4:1+} levels [-or four 4:1 levels),-] {+and one 2:1),+} and only the nodes whose value changes spend energy, so read energy depends on the data.
textbook
ml:l1:g.latch-read

## scale/shire/here
YOU ARE HERE · ≈ 3.7 mm · 10⁻³ m … the map before the renaming and is superseded. Still open: [-whether-] {+which east-west handedness+} the silicon has [-this handedness or the-] {+(the+} published die [-plot's (I/O-] {+plot is not the mirror: it keeps the PCIe and I/O cells at the east end and swaps them, I/O+} then PCIe, [-the mirror);-] {+fact L24);+} a floorplan with labelled mesh stops, a die plot with …
documented
Spatial temperature: a brief ↗
L121

## scale/shire/part/meshstop
Mesh stop. Space for details; Enter zooms in.
SHIRE … A shire has 4 to_l3 master and 4 L3 slave [-lanes; a line takes lane PA[7:6],-] {+lanes,+} and the port is 512 bits wide. {+An L3 request takes the lane of its home bank, PA[12:11] under the default swizzle, and a remote-scratchpad request lane PA[7:6] (re-implementation RTL, to confirm).+}

 12 cycles
per hop, round trip
… 4 to_l3 master and 4 L3 slave lanes to the [-mesh;-] {+mesh. An L3 request takes+} the lane [-is chosen by PA[7:6],-] {+of the bank it will use at its home, PA[12:11] under the default swizzle,+} so {+all 16 lines of an aligned 1 KB load share one lane; only a remote-scratchpad request takes the lane PA[7:6] names, so its+} lines i and i+4 share a lane [-(a 1 KB load puts 4 of its 16 lines on each).-] {+(re-implementation RTL, to confirm in silicon).+}
documented {+
 re-implementation RTL+}
Heat per millimetre ↗
L103
The shire … line per beat); a shire has four mesh lanes and [-a-] {+an L3+} line goes to {+the+} lane [-PA[7:6], so consecutive lines on one-] {+of its home bank, PA[12:11] (a remote-scratchpad line to+} lane [-are 256 bytes apart;-] {+PA[7:6]); the heat-per-mm analysis treats+} a flit [-carries-] {+as+} at least one 64-byte [-line.-] {+line (the NoC's flit size is not documented).+}
documented
Heat per millimetre ↗
mesh.port-width
… measured
three cards
On-chip communication ↗
L91

## scale/shire/part/minion
Minion 0 of neighbourhood 0. Space for details; Enter zooms … 6, neighbourhood = (hartid mod 64) >> 4, minion = {+(hartid mod 64) >> 1 (the firmware's get_minion_id(),+} hartid >> 1, {+numbers the minions chip-wide),+} thread = hartid & 1).
documented
On-chip communication …
The energy manual ↗
e-fadd
No hardware {+float or vector+} divide or square root in [-U-mode:-] {+U-mode (the scalar integer div and rem run):+} fdiv.ps and fsqrt.ps trap, as do sine, reciprocal square root, {+conversion between fp32 and+} 64-bit [-float conversion-] {+integers (fcvt.l.s, fcvt.s.l)+} and reading the cycle CSR; 161 of the instructions tried …
The DVFS loop and its leakage ↗
minion.sleep-unused

## scale/shire/part/minion#10
Minion 1 of neighbourhood 1. Space for details; Enter zooms … 6, neighbourhood = (hartid mod 64) >> 4, minion = {+(hartid mod 64) >> 1 (the firmware's get_minion_id(),+} hartid >> 1, {+numbers the minions chip-wide),+} thread = hartid & 1).
documented
On-chip communication …
The energy manual ↗
e-fadd
No hardware {+float or vector+} divide or square root in [-U-mode:-] {+U-mode (the scalar integer div and rem run):+} fdiv.ps and fsqrt.ps trap, as do sine, reciprocal square root, {+conversion between fp32 and+} 64-bit [-float conversion-] {+integers (fcvt.l.s, fcvt.s.l)+} and reading the cycle CSR; 161 of the instructions tried …
The DVFS loop and its leakage ↗
minion.sleep-unused

## scale/shire/part/minion#11
Minion 2 of neighbourhood 1. Space for details; Enter zooms … 6, neighbourhood = (hartid mod 64) >> 4, minion = {+(hartid mod 64) >> 1 (the firmware's get_minion_id(),+} hartid >> 1, {+numbers the minions chip-wide),+} thread = hartid & 1).
documented
On-chip communication …
The energy manual ↗
e-fadd
No hardware {+float or vector+} divide or square root in [-U-mode:-] {+U-mode (the scalar integer div and rem run):+} fdiv.ps and fsqrt.ps trap, as do sine, reciprocal square root, {+conversion between fp32 and+} 64-bit [-float conversion-] {+integers (fcvt.l.s, fcvt.s.l)+} and reading the cycle CSR; 161 of the instructions tried …
The DVFS loop and its leakage ↗
minion.sleep-unused

## scale/shire/part/minion#12
Minion 3 of neighbourhood 1. Space for details; Enter zooms … 6, neighbourhood = (hartid mod 64) >> 4, minion = {+(hartid mod 64) >> 1 (the firmware's get_minion_id(),+} hartid >> 1, {+numbers the minions chip-wide),+} thread = hartid & 1).
documented
On-chip communication …
The energy manual ↗
e-fadd
No hardware {+float or vector+} divide or square root in [-U-mode:-] {+U-mode (the scalar integer div and rem run):+} fdiv.ps and fsqrt.ps trap, as do sine, reciprocal square root, {+conversion between fp32 and+} 64-bit [-float conversion-] {+integers (fcvt.l.s, fcvt.s.l)+} and reading the cycle CSR; 161 of the instructions tried …
The DVFS loop and its leakage ↗
minion.sleep-unused

## scale/shire/part/minion#13
Minion 4 of neighbourhood 1. Space for details; Enter zooms … 6, neighbourhood = (hartid mod 64) >> 4, minion = {+(hartid mod 64) >> 1 (the firmware's get_minion_id(),+} hartid >> 1, {+numbers the minions chip-wide),+} thread = hartid & 1).
documented
On-chip communication …
The energy manual ↗
e-fadd
No hardware {+float or vector+} divide or square root in [-U-mode:-] {+U-mode (the scalar integer div and rem run):+} fdiv.ps and fsqrt.ps trap, as do sine, reciprocal square root, {+conversion between fp32 and+} 64-bit [-float conversion-] {+integers (fcvt.l.s, fcvt.s.l)+} and reading the cycle CSR; 161 of the instructions tried …
The DVFS loop and its leakage ↗
minion.sleep-unused

## scale/shire/part/minion#14
Minion 5 of neighbourhood 1. Space for details; Enter zooms … 6, neighbourhood = (hartid mod 64) >> 4, minion = {+(hartid mod 64) >> 1 (the firmware's get_minion_id(),+} hartid >> 1, {+numbers the minions chip-wide),+} thread = hartid & 1).
documented
On-chip communication …
The energy manual ↗
e-fadd
No hardware {+float or vector+} divide or square root in [-U-mode:-] {+U-mode (the scalar integer div and rem run):+} fdiv.ps and fsqrt.ps trap, as do sine, reciprocal square root, {+conversion between fp32 and+} 64-bit [-float conversion-] {+integers (fcvt.l.s, fcvt.s.l)+} and reading the cycle CSR; 161 of the instructions tried …
The DVFS loop and its leakage ↗
minion.sleep-unused

## scale/shire/part/minion#15
Minion 6 of neighbourhood 1. Space for details; Enter zooms … 6, neighbourhood = (hartid mod 64) >> 4, minion = {+(hartid mod 64) >> 1 (the firmware's get_minion_id(),+} hartid >> 1, {+numbers the minions chip-wide),+} thread = hartid & 1).
documented
On-chip communication …
The energy manual ↗
e-fadd
No hardware {+float or vector+} divide or square root in [-U-mode:-] {+U-mode (the scalar integer div and rem run):+} fdiv.ps and fsqrt.ps trap, as do sine, reciprocal square root, {+conversion between fp32 and+} 64-bit [-float conversion-] {+integers (fcvt.l.s, fcvt.s.l)+} and reading the cycle CSR; 161 of the instructions tried …
The DVFS loop and its leakage ↗
minion.sleep-unused

## scale/shire/part/minion#16
Minion 7 of neighbourhood 1. Space for details; Enter zooms … 6, neighbourhood = (hartid mod 64) >> 4, minion = {+(hartid mod 64) >> 1 (the firmware's get_minion_id(),+} hartid >> 1, {+numbers the minions chip-wide),+} thread = hartid & 1).
documented
On-chip communication …
The energy manual ↗
e-fadd
No hardware {+float or vector+} divide or square root in [-U-mode:-] {+U-mode (the scalar integer div and rem run):+} fdiv.ps and fsqrt.ps trap, as do sine, reciprocal square root, {+conversion between fp32 and+} 64-bit [-float conversion-] {+integers (fcvt.l.s, fcvt.s.l)+} and reading the cycle CSR; 161 of the instructions tried …
The DVFS loop and its leakage ↗
minion.sleep-unused

## scale/shire/part/minion#17
Minion 0 of neighbourhood 2. Space for details; Enter zooms … 6, neighbourhood = (hartid mod 64) >> 4, minion = {+(hartid mod 64) >> 1 (the firmware's get_minion_id(),+} hartid >> 1, {+numbers the minions chip-wide),+} thread = hartid & 1).
documented
On-chip communication …
The energy manual ↗
e-fadd
No hardware {+float or vector+} divide or square root in [-U-mode:-] {+U-mode (the scalar integer div and rem run):+} fdiv.ps and fsqrt.ps trap, as do sine, reciprocal square root, {+conversion between fp32 and+} 64-bit [-float conversion-] {+integers (fcvt.l.s, fcvt.s.l)+} and reading the cycle CSR; 161 of the instructions tried …
The DVFS loop and its leakage ↗
minion.sleep-unused

## scale/shire/part/minion#18
Minion 1 of neighbourhood 2. Space for details; Enter zooms … 6, neighbourhood = (hartid mod 64) >> 4, minion = {+(hartid mod 64) >> 1 (the firmware's get_minion_id(),+} hartid >> 1, {+numbers the minions chip-wide),+} thread = hartid & 1).
documented
On-chip communication …
The energy manual ↗
e-fadd
No hardware {+float or vector+} divide or square root in [-U-mode:-] {+U-mode (the scalar integer div and rem run):+} fdiv.ps and fsqrt.ps trap, as do sine, reciprocal square root, {+conversion between fp32 and+} 64-bit [-float conversion-] {+integers (fcvt.l.s, fcvt.s.l)+} and reading the cycle CSR; 161 of the instructions tried …
The DVFS loop and its leakage ↗
minion.sleep-unused

## scale/shire/part/minion#19
Minion 2 of neighbourhood 2. Space for details; Enter zooms … 6, neighbourhood = (hartid mod 64) >> 4, minion = {+(hartid mod 64) >> 1 (the firmware's get_minion_id(),+} hartid >> 1, {+numbers the minions chip-wide),+} thread = hartid & 1).
documented
On-chip communication …
The energy manual ↗
e-fadd
No hardware {+float or vector+} divide or square root in [-U-mode:-] {+U-mode (the scalar integer div and rem run):+} fdiv.ps and fsqrt.ps trap, as do sine, reciprocal square root, {+conversion between fp32 and+} 64-bit [-float conversion-] {+integers (fcvt.l.s, fcvt.s.l)+} and reading the cycle CSR; 161 of the instructions tried …
The DVFS loop and its leakage ↗
minion.sleep-unused

## scale/shire/part/minion#2
Minion 1 of neighbourhood 0. Space for details; Enter zooms … 6, neighbourhood = (hartid mod 64) >> 4, minion = {+(hartid mod 64) >> 1 (the firmware's get_minion_id(),+} hartid >> 1, {+numbers the minions chip-wide),+} thread = hartid & 1).
documented
On-chip communication …
The energy manual ↗
e-fadd
No hardware {+float or vector+} divide or square root in [-U-mode:-] {+U-mode (the scalar integer div and rem run):+} fdiv.ps and fsqrt.ps trap, as do sine, reciprocal square root, {+conversion between fp32 and+} 64-bit [-float conversion-] {+integers (fcvt.l.s, fcvt.s.l)+} and reading the cycle CSR; 161 of the instructions tried …
The DVFS loop and its leakage ↗
minion.sleep-unused

## scale/shire/part/minion#20
Minion 3 of neighbourhood 2. Space for details; Enter zooms … 6, neighbourhood = (hartid mod 64) >> 4, minion = {+(hartid mod 64) >> 1 (the firmware's get_minion_id(),+} hartid >> 1, {+numbers the minions chip-wide),+} thread = hartid & 1).
documented
On-chip communication …
The energy manual ↗
e-fadd
No hardware {+float or vector+} divide or square root in [-U-mode:-] {+U-mode (the scalar integer div and rem run):+} fdiv.ps and fsqrt.ps trap, as do sine, reciprocal square root, {+conversion between fp32 and+} 64-bit [-float conversion-] {+integers (fcvt.l.s, fcvt.s.l)+} and reading the cycle CSR; 161 of the instructions tried …
The DVFS loop and its leakage ↗
minion.sleep-unused

## scale/shire/part/minion#21
Minion 4 of neighbourhood 2. Space for details; Enter zooms … 6, neighbourhood = (hartid mod 64) >> 4, minion = {+(hartid mod 64) >> 1 (the firmware's get_minion_id(),+} hartid >> 1, {+numbers the minions chip-wide),+} thread = hartid & 1).
documented
On-chip communication …
The energy manual ↗
e-fadd
No hardware {+float or vector+} divide or square root in [-U-mode:-] {+U-mode (the scalar integer div and rem run):+} fdiv.ps and fsqrt.ps trap, as do sine, reciprocal square root, {+conversion between fp32 and+} 64-bit [-float conversion-] {+integers (fcvt.l.s, fcvt.s.l)+} and reading the cycle CSR; 161 of the instructions tried …
The DVFS loop and its leakage ↗
minion.sleep-unused

## scale/shire/part/minion#22
Minion 5 of neighbourhood 2. Space for details; Enter zooms … 6, neighbourhood = (hartid mod 64) >> 4, minion = {+(hartid mod 64) >> 1 (the firmware's get_minion_id(),+} hartid >> 1, {+numbers the minions chip-wide),+} thread = hartid & 1).
documented
On-chip communication …
The energy manual ↗
e-fadd
No hardware {+float or vector+} divide or square root in [-U-mode:-] {+U-mode (the scalar integer div and rem run):+} fdiv.ps and fsqrt.ps trap, as do sine, reciprocal square root, {+conversion between fp32 and+} 64-bit [-float conversion-] {+integers (fcvt.l.s, fcvt.s.l)+} and reading the cycle CSR; 161 of the instructions tried …
The DVFS loop and its leakage ↗
minion.sleep-unused

## scale/shire/part/minion#23
Minion 6 of neighbourhood 2. Space for details; Enter zooms … 6, neighbourhood = (hartid mod 64) >> 4, minion = {+(hartid mod 64) >> 1 (the firmware's get_minion_id(),+} hartid >> 1, {+numbers the minions chip-wide),+} thread = hartid & 1).
documented
On-chip communication …
The energy manual ↗
e-fadd
No hardware {+float or vector+} divide or square root in [-U-mode:-] {+U-mode (the scalar integer div and rem run):+} fdiv.ps and fsqrt.ps trap, as do sine, reciprocal square root, {+conversion between fp32 and+} 64-bit [-float conversion-] {+integers (fcvt.l.s, fcvt.s.l)+} and reading the cycle CSR; 161 of the instructions tried …
The DVFS loop and its leakage ↗
minion.sleep-unused

## scale/shire/part/minion#24
Minion 7 of neighbourhood 2. Space for details; Enter zooms … 6, neighbourhood = (hartid mod 64) >> 4, minion = {+(hartid mod 64) >> 1 (the firmware's get_minion_id(),+} hartid >> 1, {+numbers the minions chip-wide),+} thread = hartid & 1).
documented
On-chip communication …
The energy manual ↗
e-fadd
No hardware {+float or vector+} divide or square root in [-U-mode:-] {+U-mode (the scalar integer div and rem run):+} fdiv.ps and fsqrt.ps trap, as do sine, reciprocal square root, {+conversion between fp32 and+} 64-bit [-float conversion-] {+integers (fcvt.l.s, fcvt.s.l)+} and reading the cycle CSR; 161 of the instructions tried …
The DVFS loop and its leakage ↗
minion.sleep-unused

## scale/shire/part/minion#25
Minion 0 of neighbourhood 3. Space for details; Enter zooms … 6, neighbourhood = (hartid mod 64) >> 4, minion = {+(hartid mod 64) >> 1 (the firmware's get_minion_id(),+} hartid >> 1, {+numbers the minions chip-wide),+} thread = hartid & 1).
documented
On-chip communication …
The energy manual ↗
e-fadd
No hardware {+float or vector+} divide or square root in [-U-mode:-] {+U-mode (the scalar integer div and rem run):+} fdiv.ps and fsqrt.ps trap, as do sine, reciprocal square root, {+conversion between fp32 and+} 64-bit [-float conversion-] {+integers (fcvt.l.s, fcvt.s.l)+} and reading the cycle CSR; 161 of the instructions tried …
The DVFS loop and its leakage ↗
minion.sleep-unused

## scale/shire/part/minion#26
Minion 1 of neighbourhood 3. Space for details; Enter zooms … 6, neighbourhood = (hartid mod 64) >> 4, minion = {+(hartid mod 64) >> 1 (the firmware's get_minion_id(),+} hartid >> 1, {+numbers the minions chip-wide),+} thread = hartid & 1).
documented
On-chip communication …
The energy manual ↗
e-fadd
No hardware {+float or vector+} divide or square root in [-U-mode:-] {+U-mode (the scalar integer div and rem run):+} fdiv.ps and fsqrt.ps trap, as do sine, reciprocal square root, {+conversion between fp32 and+} 64-bit [-float conversion-] {+integers (fcvt.l.s, fcvt.s.l)+} and reading the cycle CSR; 161 of the instructions tried …
The DVFS loop and its leakage ↗
minion.sleep-unused

## scale/shire/part/minion#27
Minion 2 of neighbourhood 3. Space for details; Enter zooms … 6, neighbourhood = (hartid mod 64) >> 4, minion = {+(hartid mod 64) >> 1 (the firmware's get_minion_id(),+} hartid >> 1, {+numbers the minions chip-wide),+} thread = hartid & 1).
documented
On-chip communication …
The energy manual ↗
e-fadd
No hardware {+float or vector+} divide or square root in [-U-mode:-] {+U-mode (the scalar integer div and rem run):+} fdiv.ps and fsqrt.ps trap, as do sine, reciprocal square root, {+conversion between fp32 and+} 64-bit [-float conversion-] {+integers (fcvt.l.s, fcvt.s.l)+} and reading the cycle CSR; 161 of the instructions tried …
The DVFS loop and its leakage ↗
minion.sleep-unused

## scale/shire/part/minion#28
Minion 3 of neighbourhood 3. Space for details; Enter zooms … 6, neighbourhood = (hartid mod 64) >> 4, minion = {+(hartid mod 64) >> 1 (the firmware's get_minion_id(),+} hartid >> 1, {+numbers the minions chip-wide),+} thread = hartid & 1).
documented
On-chip communication …
The energy manual ↗
e-fadd
No hardware {+float or vector+} divide or square root in [-U-mode:-] {+U-mode (the scalar integer div and rem run):+} fdiv.ps and fsqrt.ps trap, as do sine, reciprocal square root, {+conversion between fp32 and+} 64-bit [-float conversion-] {+integers (fcvt.l.s, fcvt.s.l)+} and reading the cycle CSR; 161 of the instructions tried …
The DVFS loop and its leakage ↗
minion.sleep-unused

## scale/shire/part/minion#29
Minion 4 of neighbourhood 3. Space for details; Enter zooms … 6, neighbourhood = (hartid mod 64) >> 4, minion = {+(hartid mod 64) >> 1 (the firmware's get_minion_id(),+} hartid >> 1, {+numbers the minions chip-wide),+} thread = hartid & 1).
documented
On-chip communication …
The energy manual ↗
e-fadd
No hardware {+float or vector+} divide or square root in [-U-mode:-] {+U-mode (the scalar integer div and rem run):+} fdiv.ps and fsqrt.ps trap, as do sine, reciprocal square root, {+conversion between fp32 and+} 64-bit [-float conversion-] {+integers (fcvt.l.s, fcvt.s.l)+} and reading the cycle CSR; 161 of the instructions tried …
The DVFS loop and its leakage ↗
minion.sleep-unused

## scale/shire/part/minion#3
Minion 2 of neighbourhood 0. Space for details; Enter zooms … 6, neighbourhood = (hartid mod 64) >> 4, minion = {+(hartid mod 64) >> 1 (the firmware's get_minion_id(),+} hartid >> 1, {+numbers the minions chip-wide),+} thread = hartid & 1).
documented
On-chip communication …
The energy manual ↗
e-fadd
No hardware {+float or vector+} divide or square root in [-U-mode:-] {+U-mode (the scalar integer div and rem run):+} fdiv.ps and fsqrt.ps trap, as do sine, reciprocal square root, {+conversion between fp32 and+} 64-bit [-float conversion-] {+integers (fcvt.l.s, fcvt.s.l)+} and reading the cycle CSR; 161 of the instructions tried …
The DVFS loop and its leakage ↗
minion.sleep-unused

## scale/shire/part/minion#30
Minion 5 of neighbourhood 3. Space for details; Enter zooms … 6, neighbourhood = (hartid mod 64) >> 4, minion = {+(hartid mod 64) >> 1 (the firmware's get_minion_id(),+} hartid >> 1, {+numbers the minions chip-wide),+} thread = hartid & 1).
documented
On-chip communication …
The energy manual ↗
e-fadd
No hardware {+float or vector+} divide or square root in [-U-mode:-] {+U-mode (the scalar integer div and rem run):+} fdiv.ps and fsqrt.ps trap, as do sine, reciprocal square root, {+conversion between fp32 and+} 64-bit [-float conversion-] {+integers (fcvt.l.s, fcvt.s.l)+} and reading the cycle CSR; 161 of the instructions tried …
The DVFS loop and its leakage ↗
minion.sleep-unused

## scale/shire/part/minion#31
Minion 6 of neighbourhood 3. Space for details; Enter zooms … 6, neighbourhood = (hartid mod 64) >> 4, minion = {+(hartid mod 64) >> 1 (the firmware's get_minion_id(),+} hartid >> 1, {+numbers the minions chip-wide),+} thread = hartid & 1).
documented
On-chip communication …
The energy manual ↗
e-fadd
No hardware {+float or vector+} divide or square root in [-U-mode:-] {+U-mode (the scalar integer div and rem run):+} fdiv.ps and fsqrt.ps trap, as do sine, reciprocal square root, {+conversion between fp32 and+} 64-bit [-float conversion-] {+integers (fcvt.l.s, fcvt.s.l)+} and reading the cycle CSR; 161 of the instructions tried …
The DVFS loop and its leakage ↗
minion.sleep-unused

## scale/shire/part/minion#32
Minion 7 of neighbourhood 3. Space for details; Enter zooms … 6, neighbourhood = (hartid mod 64) >> 4, minion = {+(hartid mod 64) >> 1 (the firmware's get_minion_id(),+} hartid >> 1, {+numbers the minions chip-wide),+} thread = hartid & 1).
documented
On-chip communication …
The energy manual ↗
e-fadd
No hardware {+float or vector+} divide or square root in [-U-mode:-] {+U-mode (the scalar integer div and rem run):+} fdiv.ps and fsqrt.ps trap, as do sine, reciprocal square root, {+conversion between fp32 and+} 64-bit [-float conversion-] {+integers (fcvt.l.s, fcvt.s.l)+} and reading the cycle CSR; 161 of the instructions tried …
The DVFS loop and its leakage ↗
minion.sleep-unused

## scale/shire/part/minion#4
Minion 3 of neighbourhood 0. Space for details; Enter zooms … 6, neighbourhood = (hartid mod 64) >> 4, minion = {+(hartid mod 64) >> 1 (the firmware's get_minion_id(),+} hartid >> 1, {+numbers the minions chip-wide),+} thread = hartid & 1).
documented
On-chip communication …
The energy manual ↗
e-fadd
No hardware {+float or vector+} divide or square root in [-U-mode:-] {+U-mode (the scalar integer div and rem run):+} fdiv.ps and fsqrt.ps trap, as do sine, reciprocal square root, {+conversion between fp32 and+} 64-bit [-float conversion-] {+integers (fcvt.l.s, fcvt.s.l)+} and reading the cycle CSR; 161 of the instructions tried …
The DVFS loop and its leakage ↗
minion.sleep-unused

## scale/shire/part/minion#5
Minion 4 of neighbourhood 0. Space for details; Enter zooms … 6, neighbourhood = (hartid mod 64) >> 4, minion = {+(hartid mod 64) >> 1 (the firmware's get_minion_id(),+} hartid >> 1, {+numbers the minions chip-wide),+} thread = hartid & 1).
documented
On-chip communication …
The energy manual ↗
e-fadd
No hardware {+float or vector+} divide or square root in [-U-mode:-] {+U-mode (the scalar integer div and rem run):+} fdiv.ps and fsqrt.ps trap, as do sine, reciprocal square root, {+conversion between fp32 and+} 64-bit [-float conversion-] {+integers (fcvt.l.s, fcvt.s.l)+} and reading the cycle CSR; 161 of the instructions tried …
The DVFS loop and its leakage ↗
minion.sleep-unused

## scale/shire/part/minion#6
Minion 5 of neighbourhood 0. Space for details; Enter zooms … 6, neighbourhood = (hartid mod 64) >> 4, minion = {+(hartid mod 64) >> 1 (the firmware's get_minion_id(),+} hartid >> 1, {+numbers the minions chip-wide),+} thread = hartid & 1).
documented
On-chip communication …
The energy manual ↗
e-fadd
No hardware {+float or vector+} divide or square root in [-U-mode:-] {+U-mode (the scalar integer div and rem run):+} fdiv.ps and fsqrt.ps trap, as do sine, reciprocal square root, {+conversion between fp32 and+} 64-bit [-float conversion-] {+integers (fcvt.l.s, fcvt.s.l)+} and reading the cycle CSR; 161 of the instructions tried …
The DVFS loop and its leakage ↗
minion.sleep-unused

## scale/shire/part/minion#7
Minion 6 of neighbourhood 0. Space for details; Enter zooms … 6, neighbourhood = (hartid mod 64) >> 4, minion = {+(hartid mod 64) >> 1 (the firmware's get_minion_id(),+} hartid >> 1, {+numbers the minions chip-wide),+} thread = hartid & 1).
documented
On-chip communication …
The energy manual ↗
e-fadd
No hardware {+float or vector+} divide or square root in [-U-mode:-] {+U-mode (the scalar integer div and rem run):+} fdiv.ps and fsqrt.ps trap, as do sine, reciprocal square root, {+conversion between fp32 and+} 64-bit [-float conversion-] {+integers (fcvt.l.s, fcvt.s.l)+} and reading the cycle CSR; 161 of the instructions tried …
The DVFS loop and its leakage ↗
minion.sleep-unused

## scale/shire/part/minion#8
Minion 7 of neighbourhood 0. Space for details; Enter zooms … 6, neighbourhood = (hartid mod 64) >> 4, minion = {+(hartid mod 64) >> 1 (the firmware's get_minion_id(),+} hartid >> 1, {+numbers the minions chip-wide),+} thread = hartid & 1).
documented
On-chip communication …
The energy manual ↗
e-fadd
No hardware {+float or vector+} divide or square root in [-U-mode:-] {+U-mode (the scalar integer div and rem run):+} fdiv.ps and fsqrt.ps trap, as do sine, reciprocal square root, {+conversion between fp32 and+} 64-bit [-float conversion-] {+integers (fcvt.l.s, fcvt.s.l)+} and reading the cycle CSR; 161 of the instructions tried …
The DVFS loop and its leakage ↗
minion.sleep-unused

## scale/shire/part/minion#9
Minion 0 of neighbourhood 1. Space for details; Enter zooms … 6, neighbourhood = (hartid mod 64) >> 4, minion = {+(hartid mod 64) >> 1 (the firmware's get_minion_id(),+} hartid >> 1, {+numbers the minions chip-wide),+} thread = hartid & 1).
documented
On-chip communication …
The energy manual ↗
e-fadd
No hardware {+float or vector+} divide or square root in [-U-mode:-] {+U-mode (the scalar integer div and rem run):+} fdiv.ps and fsqrt.ps trap, as do sine, reciprocal square root, {+conversion between fp32 and+} 64-bit [-float conversion-] {+integers (fcvt.l.s, fcvt.s.l)+} and reading the cycle CSR; 161 of the instructions tried …
The DVFS loop and its leakage ↗
minion.sleep-unused

## scale/solar/here
YOU ARE HERE · 9 billion km · 10¹² m … to reach Earth and about 4.2 h to reach Neptune. [-In-] {+On 18+} November 2026 Voyager 1, the farthest spacecraft, [-will be-] {+is+} a full light-day [-away.-] {+from Earth.+}

 Zoom into:
Earth and the Moon (+) … and the answer another day.
outside source
out.solar.3

## scale/solar/part/to-moon
Earth, 8.32 min of light from the Sun: zoom in. … to reach Earth and about 4.2 h to reach Neptune. [-In-] {+On 18+} November 2026 Voyager 1, the farthest spacecraft, [-will be-] {+is+} a full light-day [-away.-] {+from Earth.+}

 No closer drawing of The Sun and its … reaches it in 4.17 h.
outside source
out.solar.2

## scale/solar/part/voyager
Voyager 1: details
SOLAR SYSTEM · [-PART-] {+SPACECRAFT

 Voyager 1+}

 The [-Sun and its planets

 Sunlight takes 8.3 min to reach Earth and about 4.2 h to reach Neptune. In-] {+farthest spacecraft: on 18+} November 2026 [-Voyager 1,-] {+it is one light-day from Earth, so a command takes a day to arrive and+} the [-farthest spacecraft, will be a full light-day away.-] {+answer another day.+}

 No closer drawing of [-The Sun and its planets.-] {+Voyager 1.+}

 More detail and the sources

 The facts [-(2):-] {+(1):+} point at one for its source

 {+Voyager 1 reaches one light-day from+} Earth [-orbits at 1 au, 8.32 min from-] {+(25.9 billion km, 173 au) on 18 November 2026: a command sent then takes a day to arrive and+} the [-Sun at the speed of light.
model
out.solar.1
Neptune's semimajor axis: 30.07 au (4,498 million km); sunlight reaches it in 4.17 h.-] {+answer another day.+}
outside source
[-out.solar.2-] {+out.solar.3+}

## scale/stars/part/to-solar
the Sun: zoom in. Space for details; Enter zooms in. … to reach Earth and about 4.2 h to reach Neptune. [-In-] {+On 18+} November 2026 Voyager 1, the farthest spacecraft, [-will be-] {+is+} a full light-day [-away.-] {+from Earth.+}

 Zoom in:
The Solar System (double-click)
… and the answer another day.
outside source
out.solar.3

## scale/studio45/part/cnc
The CNC router's bed: details
STUDIO 45 · DOWNSTAIRS … × 8 ft CNC router among them. The lab is {+most likely+} above it.

 No closer drawing of The wood … a street-level warehouse and courtyard.
outside source
s45.3

## scale/studio45/part/shop
The wood shop: details
STUDIO 45 · DOWNSTAIRS
… × 8 ft CNC router among them. The lab is {+most likely+} above it.

 No closer drawing of The wood … a street-level warehouse and courtyard.
outside source
s45.3

## scale/studio45/part/torack
The rack: zoom in. Space for details; Enter zooms in.
STUDIO 45 · PART

 The rack

 {+Where in the room it stands is not recorded: its place here is assumed.+} A wire shelving rack holding about ten open-frame machines on … chip's clock ticks at 600 MHz.
model
out.rack.5

## scale/studio45/part/warehouse
The warehouse: details
STUDIO 45 · DOWNSTAIRS

 … its big events are held. Its stair climbs to the [-lab's end.-] {+upper floor at the shop end, most likely the lab.+}

 No closer drawing of The warehouse.

 … a street-level warehouse and courtyard.
outside source
s45.3

## scale/tensor/here
YOU ARE HERE · ≈ 100 µm · 10⁻⁴ m … the sources

 Its size: order of magnitude: state [-machines-] {+machines; TenB+} and [-two 1 KiB buffers-] {+TenC, drawn here as the tensor extension's state, sit in the lanes' TIMA units in the RTL+}

 The facts (5): point at one for its … / (bytes per element): A from the L1 scratchpad, B {+from the L1 scratchpad or+} streamed through [-TenB,-] {+TenB by a paired TensorLoadB,+} C accumulated in hart 0's vector registers (int8 in TenC). …
three cards
The energy manual ↗
e-tfma-fp32

## scale/tensor/part/lib.adder
Adder, documented. Space for details; Enter zooms in.
TENSOR … not waiting for a carry to ripple through 64 positions: {+the fastest+} prefix adders compute all the carries in about six levels … point at one for its source

 Parallel-prefix adders [-(Kogge-Stone, Sklansky, Brent-Kung)-] compute [-carries-] {+every carry in a tree of generate/propagate cells: Kogge-Stone and Sklansky+} in log2(N) {+levels, Brent-Kung in 2 log2(N) - 1+} levels [-of generate/propagate cells.-] {+with fewer cells and wires.+}
textbook
in.lib.adder.1
A parallel-prefix adder computes for … cells (G = Gi + Pi·Gj, P = Pi·Pj) of {+as few as+} log2 n levels, and forms each sum bit as p … cell driving at most two others.
textbook
tb.kogge

## scale/tensor/part/lib.latch
Latch, documented. Space for details; Enter zooms in.
TENSOR … V at 800); firmware limits 0.40-0.62 V.
measured
[-card not recorded-] {+aifoundry2+}
et.v-minion

## scale/tensor/part/tensor.tenb
TenB, documented. Space for details; Enter zooms in.
TENSOR …

 Where the B matrix streams in from the [-cache on its way to the lanes;-] {+cache, kept in each lane's two TIMA units;+} the programmer sees 16 registers of 64 bytes, the hardware …
documented
no published page yet
minion.tenb-tenc
[-Modules-] {+TenB is+} vpu_tensorb_rf, [-vpu_tensora_rf, vpu_tensortmp_rf.-] {+instantiated in each of a lane's two vpu_lane_tima units (4 entries of 32 bits each: 256 B per minion); vpu_tensora_rf (TenA, the A buffer) and vpu_tensortmp_rf sit in vpu_ctrl.+}
documented
Erbium RTL
in.tensor.tenb.2

## scale/tensor/part/tensor.tenc
TenC, documented. Space for details; Enter zooms in.
TENSOR UNIT · PART

 TenC (int32 accumulators)

 Sixteen 64-byte [-registers-] {+registers, kept in each lane's two TIMA units,+} that hold the running 32-bit sums of an integer matrix … Macro model vpu_tensorc_rf_buffer_array.
documented
Erbium RTL
in.tensor.tenc.2

## scale/universe/here
YOU ARE HERE · 92.4 billion ly · 10²⁶ m

 The observable universe [-

↻ You came round the ring of sizes: past the observable universe, back to the smallest things, and in as an atom of this chip. Up climbs from here through , on up to the chip and round again.

 ↻ Back to the ring of sizes-]

 Everything whose light has had time to reach … than the chip's 25.6 mm die.
model
out.universe.4

## scale/vpu.lane.fma/here
YOU ARE HERE · ≈ 60 µm · 10⁻⁵ m …
aifoundry2
The Horace experiment ↗
e-flip-model
[-A-] {+In the flip model (the TXFMA RTL replayed on the operands aifoundry2 ran), a+} random-data 16x16x16 tile clocks 2.5 million register bits and toggles … clock is withheld when an operand word is zero.
[-measured
card not recorded-] {+model+}
in.vpu.lane.fma.6
A fused multiply-add computes a x b … normalising shift and a rounding increment.
textbook
tb.fma

## scale/vpu.lane.fma/part/fmazero
A zero operand: the lane’s clock is withheld. Space for …
aifoundry2
The Horace experiment ↗
e-flip-model
[-A-] {+In the flip model (the TXFMA RTL replayed on the operands aifoundry2 ran), a+} random-data 16x16x16 tile clocks 2.5 million register bits and toggles … clock is withheld when an operand word is zero.
[-measured
card not recorded-] {+model+}
in.vpu.lane.fma.6
A fused multiply-add computes a x b … normalising shift and a rounding increment.
textbook
tb.fma

## scale/vpu.lane/part/lib.adder
Adder, documented. Space for details; Enter zooms in.
LANE … not waiting for a carry to ripple through 64 positions: {+the fastest+} prefix adders compute all the carries in about six levels … point at one for its source

 Parallel-prefix adders [-(Kogge-Stone, Sklansky, Brent-Kung)-] compute [-carries-] {+every carry in a tree of generate/propagate cells: Kogge-Stone and Sklansky+} in log2(N) {+levels, Brent-Kung in 2 log2(N) - 1+} levels [-of generate/propagate cells.-] {+with fewer cells and wires.+}
textbook
in.lib.adder.1
A parallel-prefix adder computes for … cells (G = Gi + Pi·Gj, P = Pi·Pj) of {+as few as+} log2 n levels, and forms each sum bit as p … cell driving at most two others.
textbook
tb.kogge

## scale/vpu.lane/part/lib.booth
Booth encoder, documented. Space for details; Enter zooms in.
… each bit of a partial product is a multiplexer choosing [-x(j)-] {+x(j), x(j-1)+} or [-x(j-1),-] {+0,+} followed by an XOR with the sign.
textbook
… give -X, and 111 gives 0.
textbook
tb.booth.table

## scale/vpu.lane/part/lib.latch
Latch, documented. Space for details; Enter zooms in.
LANE … V at 800); firmware limits 0.40-0.62 V.
measured
[-card not recorded-] {+aifoundry2+}
et.v-minion

## scale/vpu.lane/part/lib.mux2
Two-way multiplexer, documented. Space for details; Enter zooms in.
… a mux tree (128:1 per output bit, e.g. seven 2:1 {+levels, or three 4:1+} levels [-or four 4:1 levels),-] {+and one 2:1),+} and only the nodes whose value changes spend energy, so read energy depends on the data.
textbook
ml:l1:g.latch-read

## scale/vpu.lane/part/vpu.lane.fma
Fused multiply-add unit, documented. Space for details; Enter zooms in. …
aifoundry2
The Horace experiment ↗
e-flip-model
[-A-] {+In the flip model (the TXFMA RTL replayed on the operands aifoundry2 ran), a+} random-data 16x16x16 tile clocks 2.5 million register bits and toggles … clock is withheld when an operand word is zero.
[-measured
card not recorded-] {+model+}
in.vpu.lane.fma.6
A fused multiply-add computes a x b … normalising shift and a rounding increment.
textbook
tb.fma

## scale/vpu.lane/part/vpu.lane.trans
Transcendental unit, documented. Space for details; Enter zooms in.
…
documented
Erbium RTL
in.vpu.lane.trans.2
No hardware {+float or vector+} divide or square root in [-U-mode:-] {+U-mode (the scalar integer div and rem run):+} fdiv.ps and fsqrt.ps trap, as do sine, reciprocal square root, {+conversion between fp32 and+} 64-bit [-float conversion-] {+integers (fcvt.l.s, fcvt.s.l)+} and reading the cycle CSR; 161 of the instructions tried …
aifoundry2, aifoundry3
The energy manual ↗
minion.no-divide

## scale/vpu/part/lib.mux2
Two-way multiplexer, documented. Space for details; Enter zooms in.
… a mux tree (128:1 per output bit, e.g. seven 2:1 {+levels, or three 4:1+} levels [-or four 4:1 levels),-] {+and one 2:1),+} and only the nodes whose value changes spend energy, so read energy depends on the data.
textbook
ml:l1:g.latch-read

## static/bodytext
Skip to playback
Skip to zoom out
Skip … cards), the zoom 30 September, down to the quarks 1 [-October-] {+October, the 3D views 14 October, checked against the manuals, the RTL, the firmware and the lab's data the same day+} · every number is a fact with a source: a … each number with its kind and source (point at it); {+every one is+} an [-estimate-] {+estimate, its kind+} says [-"about"-] {+model or inference,+} and its assumptions are in its source.

 What Electrons Kind
An "off" transistor's [-channel,-] {+channel+} at any instant {+(the chip's average at 80 °C)+} 0.002 electrons model
[-An "on" transistor's channel,-] {+One fin's channel when on,+} at the minion rail 85-120 electrons inference
An SRAM … on random fp32 matmul 540 million electrons model
Leaking [-through an "off"-] {+per+} transistor, every second {+(the chip's average at 80 °C)+} 10 billion electrons a second model

 The camera … the memory, PCIe and I/O shires drawn as pills.
{+13–14 October: − and + keep their place in the Up bar; the readout keeps one look while the camera moves, and moves are smoother; the wiring, the FinFET, the fin and the channel link to their 3D views (Turn the chip's smallest structures in 3D, above, and "Explore this in 3D" in their panels).
14 October, later: a check of every fact, panel, flow and drawing against the manuals, the core-et documents, the RTL, the firmware and the lab's data, with another agent's review folded in: 97 statements, numbers, kinds and drawings corrected (among them the relay drawn as the next shire reading the last one's scratchpad, its energy per byte moved; the published die plot no mirror of the die view, and the map transposed onto the die; an L3 line's mesh lane its home bank's, PA[12:11]; the shire's two clock crossings drawn apart; a DRAM load's DRAM-chip share about 28 cycles; aifoundry1 card 1's 16 GB of DRAM; the card's 88 W a budget, not a ceiling), the teaching circuits' broken connections joined, 181 line citations brought up to date, and the tour's last slide counting the facts as the table does. 
+} Related reports#
Over the PCIe link — the host … and the asks.

 ← All ET-SoC-1 measurement reports

## static/honest
The page rests on 304 facts: [-162-] {+163+} measured, [-107-] {+106+} from the specification (the datasheet, the Programmer's Reference Manual, the … derived from others and 11 inferred. Of the measured facts, [-122-] {+125+} hold on all three lab cards (aifoundry2, aifoundry3 and aifoundry1 card 1), [-13-] {+12+} on two and 25 on one, mostly aifoundry2; [-2 name-] {+1 names+} no card. Every table here is at 600 MHz, where … and into its parts (30 September and 1 October) adds [-696-] {+702+} facts of its own: 52 measured, [-186-] {+190+} documented, 75 model, 177 inference, [-92-] {+94+} outside source, 96 textbook, 1 the owner’s word, 1 speculative, … compared the map before the renaming, is superseded). Still open: [-whether-] {+which east-west handedness+} the silicon [-has this handedness or-] {+has;+} the published die [-plot's, its mirror-] {+plot is not this view's mirror: it keeps the PCIe and I/O cells at the east end and swaps them+} (die.handedness, L24).The four cells without a compute shire: the firmware's … one card, aifoundry2 (L40), within ±3 cycles for 93–97% of [-loads-] {+lines+} on all three cards (ms-fit-3cards). The firmware's map puts the … commands collide only inside one stream (pcie.conc).Gathers and scatters (E48) [-were reduced-] {+are+} on {+the memory-hierarchy page and in the energy manual since+} 27 [-September and have no published page yet;-] {+September;+} the heat race of flow 8 is one card's (aifoundry2).What … east end of the top row. The published die plot [-draws-] {+(IEEE Micro 2022 Fig. 7, MPR Dec 2020 Fig. 1) also puts the PCIe and I/O cells at the east end of the top row, in the other order,+} I/O then [-PCIe, its-] {+PCIe (fact L24), and labels no memory shire: it is not the+} mirror [-image;-] {+image. Its own orientation is not stated, and+} no document in the open drop says which handedness the … die placement. (dram.pkg-pairing)Of a DRAM load's ~300 cycles only about [-25-28-] {+28+} are the DRAM chip's own timing (activate tRCD 18 ns, 19.3 ns read latency, [-one or-] {+the+} two 4.3 ns [-bursts);-] {+bursts of a 64-byte line);+} the rest is paths on the chip. (lat-dram-chip)Inferred before and … 1 and decided nothing on aifoundry3 or aifoundry2.)The logical map [-appears to be-] {+is+} the die [-turned-] {+view transposed (x and y swapped:+} a [-quarter:-] {+quarter turn plus a mirror):+} in map orientation the memory shires sit above and below … in every pair distance with no rotation or mirror (fact [-fw.map-match);-] {+fw.map-match), so mapping (x, y) to (die row x, die column y) is a transpose (a quarter turn plus a mirror);+} which handedness the silicon has is open (fact die.handedness). Distances … still a tie-break of the fit (L42, ms2-forced).)The logical map [-appears to be-] {+is+} the die [-turned-] {+view transposed (x and y swapped:+} a [-quarter:-] {+quarter turn plus a mirror):+} in map orientation the memory shires sit above and below … (mesh.orientation: Settled 27 Sep except the east-west handedness (facts fw.map-match, [-die.handedness).)The-] {+die.handedness): mapping (x, y) to (die row x, die column y) is a transpose (a quarter turn plus a mirror).)The+} heat-per-mm analysis assumes dimension-ordered XY routing on the logical map … keeps them and whether tensor stores skip the L2 (the {+PRM, pdf p.306 and p.309, and the+} Shire Cache [-Specification says-] {+Specification, pdf p.62, say+} they do).)

## static/summary
The chip. The ET-SoC-1 has 1,093 RISC-V cores on a … hop; a typical DRAM load takes 299, of which about [-25–28-] {+28+} are the DRAM chip. (2) The ladder adds the read … plus 12.02 per hop, round trip. (4) The relay: 8.9 [-pJ/B-] {+pJ per byte moved (each write and each read counted)+} to the next shire against 116.2 through DRAM (12.9×, 13.0× … a relay hands a buffer from shire to shire at [-8.9 pJ/B-] {+17.8 pJ per byte+} a hand-off, {+its write and its read,+} where every shire reading its own copy from DRAM pays … 103.6–104.1 µs for an empty kernel queued on 32 shires.

## tour/10
TOUR 10 / 17 · FLOW 4 · RELAY
Two ways to hand a block of results to the next shire: {+it reads them+} straight [-into its-] {+from this shire's+} scratchpad, or {+they go+} out to DRAM and back
Handing a result to the next shire costs 8.9 pJ per byte {+moved+} against 116.2 through DRAM: about a thirteenth of the energy, … results from one stage of a computation to the next: [-straight into-] the next {+shire reads them straight from this+} shire's memory, or {+they go+} out to the memory chips and back. Straight across is much cheaper.

## tour/14
TOUR 14 / 17 · FLOW 8 · DATA → …
The same matmul, 9.18 TFLOP/s timed from the host [-(9.51-] {+(546 cycles per op+} on the [-device),-] {+device, A and B in the L1 scratchpad),+} draws 38.29 W on zeros and 63.40 W on random … data draws more power than zeros, because more bits flip.

## tour/17
TOUR 17 / 17 · SUMMARY
Every number on this diagram has a source: [-1117-] {+1006+} facts, [-214-] {+215+} of them [-measured on the lab's cards, 293-] {+measured, 296+} from the [-specification, 136 derived-] {+documents, 99 derived, 188 inferred+} and [-196 inferred.-] {+208 of other kinds (outside sources, textbooks, open questions).+}
Each inferred part says what would settle it; the … does, or pick a flow above to watch data move.

## tour/4
TOUR 4 / 17 · MEMORY
Eight memory shires … DRAM latencies on aifoundry2, within ±3 cycles for 93–97% of [-loads-] {+lines+} on all three cards; the firmware's map agrees on the … costly to reach compared with the memory on the chip.

## tour/7
TOUR 7 / 17 · FLOW 1 · LOAD TO … and on to a memory shire: about 299 cycles, about [-25–28-] {+28+} of them in the DRAM chip.
--panel--
FLOW … and brings the data back: about 299 cycles in all.

