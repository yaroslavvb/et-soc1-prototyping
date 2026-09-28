#!/usr/bin/env python3
"""What would settle each inferred or dashed part of the chip diagram, and which of the hub's asks it maps to.

    python3 docs/reports/data/2026-09-27-chip-diagram/research/make_asks.py   # writes asks.json beside it

One entry per part: the components (and flows, flow:<k>) whose details panel shows it, the facts behind it, what is
inferred, what settles it (a document, an experiment or an interface), and the hub's improvement-ladder row it links
to (hub_anchor, a row id in docs/reports/sources/limits-of-observability.data.json .improvements). Written on
27 September 2026; the PCIe entry was marked settled once the link was timed (docs/reports/data/2026-09-27-pcie).
An entry's state: open (the default; the page heads it "Inferred"), nearly (most of it settled by a source in hand,
a part still open: "Nearly settled"), confirm (settled by a source in hand, a check on the cards would confirm it:
"To confirm"), settled ("Settled"; the older flag settled: True means the same).
"""
import json
import os
HUB = "https://spacesheep.dev/@yaroslavvb/et-soc1-limits-of-observability#"
FWM = "docs/reports/data/2026-09-27-chip-diagram/research/firmware_map.json"
fw = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "firmware_map.json")))
A = fw["comment_map_after_remap"]
assert A["pair_distances_equal"] == 496 and A["best_symmetry"]["shires_at_same_cell"] == 32 and fw["memshires"]["agree"] == 8
asks = [
 {"part": "die view: every die position (the logical map turned onto the die)",
  "comps": ["chip", "cshire"], "facts": ["mesh.orientation", "L33", "L34", "L37", "L24"],
  "what_is_inferred": "How the measured logical map sits on the die: logical x as die rows, y as die columns, memory shires 0-3 on the west, and the east-west sense (distances cannot tell a rotation from a mirror).",
  "what_settles_it": "Mostly settled by firmware source already in hand: the firmware's 'default Shire Virtual ID Map, based on the NOC spec' (noc_reconfigure.h:76-82), renamed by the boot firmware's NOC_Remap_Shires (main.c:284; 'No displacement' table noc_reconfigure.h:398-405, used when no shire is fused off), equals the measured map cell for cell with no rotation or mirror: 496 of 496 pair distances and 32 of 32 cells (" + FWM + "). So the diagram's die view L34 is exactly the NoC-spec drawing: memory shires 0-3 on the left (west), PCIe then I/O at the right (east) end of the top row, as PRM Fig. 1-3 and datasheet Fig. 2-6 also draw it. Fact L37 ('does NOT match') compared the map before the renaming and is superseded. Still open: whether the silicon has this handedness or the published die plot's (I/O then PCIe, the mirror); a floorplan with labelled mesh stops, a die plot with its orientation stated, or the package ball map settles it.",
  "ask": "document", "ask_detail": "top-level floorplan or an oriented, scaled die plot (AI Foundry); second source: the ET-SoC-1 Data Book / a final datasheet with the ball map",
  "hub_anchor": "ask-floorplan", "hub_url": HUB + "ask-floorplan", "also": ["ask-databook"], "state": "nearly"},
 {"part": "the four grey cells (master, spare, PCIe, I/O)",
  "comps": ["master", "pcie", "io"], "facts": ["L32", "L24", "L37", "chip.master-shire-id"],
  "what_is_inferred": "Which grey cell is the master shire (32), the spare (33), the PCIe shire and the I/O shire.",
  "what_settles_it": "Settled by the same firmware map (" + FWM + " grey_cells): logical (0,3) = shire 32, the master (top row, die column 4); (5,3) = shire 33, the spare (bottom row); (0,4) = the bridge map's 'pcie0'; (0,5) = 'io0' (noc_reconfigure.h:84-90). This is L32's alternative reading (PCIe west of I/O, as PRM Fig. 1-3). To confirm on the cards: time SYSCALL_PMC_SC_SAMPLE on shire 32 from each compute shire (a + b x hops picks the top or bottom cell). PCIe/I/O order rests on the two firmware comments and the PRM; the NoC spec would confirm it.",
  "ask": "experiment (confirm) / document (NoC spec)", "ask_detail": "exp-mesh-stops; the NOC spec that the firmware maps cite",
  "hub_anchor": "exp-mesh-stops", "hub_url": HUB + "exp-mesh-stops", "also": ["ask-noc-docs"], "state": "confirm"},
 {"part": "memory shire placement (memory shire 2 a tie)",
  "comps": ["memshire"], "facts": ["L40", "L42", "ms2-forced"],
  "what_is_inferred": "The memory shires' places come from a DRAM-latency fit on one card; memory shire 2's fit ties three places and is forced by elimination.",
  "what_settles_it": "The firmware map puts mc0-mc3 on the west at rows 1-4 and mc4-mc7 on the east at rows 1-4 (" + FWM + " memshires): the fit's places for the 7 memory shires it places on its own, provided the firmware's mcN is the memory shire selected by PA[8:6] = N. With those 7 in place memory shire 2 has one cell left in both, so the map confirms the frame, not memory shire 2 on its own. What settles it on the cards: time SYSCALL_PMC_MS_SAMPLE (ms 0-7) from each of the 32 compute shires; each call's cycles are a constant plus a per-hop term to that memory shire, with no L3-home leg (the confound behind the tie).",
  "ask": "experiment (confirm)", "ask_detail": "exp-mesh-stops",
  "hub_anchor": "exp-mesh-stops", "hub_url": HUB + "exp-mesh-stops", "also": [], "state": "confirm"},
 {"part": "the four LPDDR4X packages (which two memory shires share each)",
  "comps": ["dram"], "facts": ["dram.pkg-pairing", "L23"],
  "what_is_inferred": "The pairing of memory shires to LPDDR4X packages (drawn as neighbours: 0+1, 2+3, 4+5, 6+7).",
  "what_settles_it": "The dev card's schematic: ET-PCIe-Dev-Card-V3.pdf p.1 links 'Schematic 09/27/2022', 'Board File V3.2' and the V3 schematic changes, none in external/et-man. Its block diagram (pdf p.4) and datasheet Fig. 2-6 both draw each LPDDR4X beside two neighbouring memory shires but number neither; the datasheet (pdf p.30) says only two memory shires per 64-bit device. No experiment identifies the package from software.",
  "ask": "document", "ask_detail": "card schematic and board file (AI Foundry)",
  "hub_anchor": "ask-card-schematic", "hub_url": HUB + "ask-card-schematic", "also": []},
 {"part": "the mesh's routing order (every route the eleven flows draw)",
  "comps": ["mesh"], "facts": ["L104", "mesh.xy-assumption", "mesh.shortest-paths", "L105"],
  "what_is_inferred": "Whether a request turns x first or y first (the diagram draws x first; y first where x first crosses an empty corner); also the router-to-router flit width (L105 note).",
  "what_settles_it": "Documents: the NoC configuration's generated reference manual (noc/reference_manual/noc_reference_manual.htlm, named at core-et rtl/inc/debug_defines.vh:831-832), the Main NoC documentation linked from CORE-ET Minion Shire Description §3.3 (pdf p.11, link missing), and the 'NOC spec' (noc_reconfigure.h:76, 84). Experiment: tensor-load streams that share a link under x-first routing but not y-first (and the mirror), several readers per stream; a throughput drop in one set only gives the order. Interface: the routers' VC-status registers (noc_esr.h RIVCS/ROVCS), SP-only.",
  "ask": "document / experiment / interface", "ask_detail": "ask-noc-docs; exp-route-order; ask-noc-registers",
  "hub_anchor": "ask-noc-docs", "hub_url": HUB + "ask-noc-docs", "also": ["exp-route-order", "ask-noc-registers"]},
 {"part": "the way back of a DRAM load (Flow 1, Load -> DRAM)",
  "comps": ["flow:A", "mesh"], "facts": ["addr.load-model", "L45"],
  "what_is_inferred": "The reply's path: the diagram draws it from the memory shire through the L3 home to the requester.",
  "what_settles_it": "The leg order is documented in a manual already in the repo: CORE-ET Shire Cache Specification §3.2.2 'L3 REQ_Read' (pdf p.55): L3 reads that miss go out the to_sys mesh port, the data returns to the L3 as L3_Fill, then the reply goes to the requester, so memory shire -> L3 home -> requester is spec. Only each leg's route (x or y first) is open: the routing ask and the contention experiment.",
  "ask": "document (in repo) + experiment", "ask_detail": "cite the Shire Cache Specification; exp-route-order for the route of each leg",
  "hub_anchor": "exp-route-order", "hub_url": HUB + "exp-route-order", "also": ["ask-noc-docs"]},
 {"part": "the inside of a shire (banks, neighbourhoods, UC block, mesh stop)",
  "comps": ["banks", "xbar", "neigh", "uc", "meshstop", "l2", "l3", "scp"], "facts": ["L114"],
  "what_is_inferred": "Where the four neighbourhoods, four cache banks, the UC block and the mesh stop sit in the 3.7 mm tile (the drawing is a block diagram).",
  "what_settles_it": "A minion-shire floorplan from the physical-design team. CORE-ET Minion Shire Description Figure 1 (pdf p.5) is logical; only the neighbourhood has a floorplan (Neighborhood MAS Figure 2, pp.7-8, already used by L115). No practical experiment: one temperature sensor per shire, and the crossbar may equalise bank latencies.",
  "ask": "document", "ask_detail": "shire floorplan (AI Foundry)",
  "hub_anchor": "ask-shire-floorplan", "hub_url": HUB + "ask-shire-floorplan", "also": []},
 {"part": "die sizes and the tile pitch",
  "comps": ["chip"], "facts": ["chip.die-dims", "chip.hop-pitch", "L08"],
  "what_is_inferred": "Die width and height and the hop length are pixel estimates on one die plot scaled to 570 mm2.",
  "what_settles_it": "The floorplan's dimensions (or the Data Book): die W x H, tile pitch, memory-shire strip width. The datasheet's package drawing (Fig. 9-1) has no die outline.",
  "ask": "document", "ask_detail": "floorplan or Data Book",
  "hub_anchor": "ask-floorplan", "hub_url": HUB + "ask-floorplan", "also": ["ask-databook"]},
 {"part": "PCIe bandwidth (PCIe shire, Host, Flow 6)",
  "comps": ["pcie", "host", "flow:F"], "facts": ["pcie.h2d", "pcie.d2h", "pcie.staged", "pcie.launch"],
  "what_is_inferred": "Was: 15.75 GB/s per direction, the Gen4 x8 link figure, with host transfers never timed.",
  "what_settles_it": "Settled on 27 September: timed on three cards with workloads/pciebench, five runs per card against predictions stated before the runs (docs/reports/data/2026-09-27-pcie; the page Over the PCIe link). Not a team ask.",
  "ask": "done", "ask_detail": "workloads/pciebench, docs/reports/data/2026-09-27-pcie",
  "hub_anchor": None, "hub_url": None, "also": [], "settled": True},
 {"part": "the Host -> DRAM path (Flow 6: 'the path from the PCIe shire is not established')",
  "comps": ["flow:F", "pcie"], "facts": ["bw-pcie"],
  "what_is_inferred": "Whether the host's writes reach DRAM through the lines' L3 homes or straight to the memory shires.",
  "what_settles_it": "The PCIe shire's to-sys bridge has DRAM address-map entries for every shire's L3 slave (SHn_L3D) and for each memory shire (MC0..MC7_MEM) (etsoc-hal hwinc/noc_esr.h, BRIDGE_PS0_TOSYS ... MAP_MEM_DRAM; its to-L3 bridge only to L3 slaves), so the programmed ADBASE/ADMASK decide. Experiment: copy a buffer from the host, then time each line's first load in a kernel launched without flushL3: L3-hit latency = through the L3 homes, DRAM latency = to the memory shires. Or read the programmed values (SP-only) / the NoC documents.",
  "ask": "experiment / document", "ask_detail": "exp-pcie-path; ask-noc-docs",
  "hub_anchor": "exp-pcie-path", "hub_url": HUB + "exp-pcie-path", "also": ["ask-noc-docs", "ask-noc-registers"]},
 {"part": "the DRAM address map below the memory shire",
  "comps": ["memshire", "dram"], "facts": ["L50"],
  "what_is_inferred": "PA[9] channel, PA[12:10] bank, PA[34:18] row: decoded from firmware ADDRMAP values and a tool comment, not read back.",
  "what_settles_it": "Experiment: a row-conflict probe with the L3 defeated (latency step of one row cycle marks bank/row bits; same across PA[9] for the channel). Or a service-processor readback of each controller's ADDRMAP registers.",
  "ask": "experiment / interface", "ask_detail": "exp-dram-rows; ask-memshire",
  "hub_anchor": "exp-dram-rows", "hub_url": HUB + "exp-dram-rows", "also": ["ask-memshire"]},
 {"part": "the DRAM chip's share of a load (memory shire panel)",
  "comps": ["memshire"], "facts": ["lat-dram-chip"],
  "what_is_inferred": "About 25-28 of a DRAM load's cycles are the DRAM's own timing; the rest on-chip (timing registers set against the fit).",
  "what_settles_it": "A memory-shire description with its pipeline latencies (NoC bridge, uMCTL2 controller, PHY, clock crossings) or a readback of the programmed DRAMTMG registers; or, as an experiment, DRAM latency at a second DRAM clock (needs a build: mem_controller.c:643 fixes 933 MHz; 800 and 1066 modes exist).",
  "ask": "document / interface / experiment (firmware build)", "ask_detail": "ask-memshire",
  "hub_anchor": "ask-memshire", "hub_url": HUB + "ask-memshire", "also": []},
 {"part": "the tensor unit's cache path (tensor sequencer, L1 scratchpad)",
  "comps": ["tensor", "l1scp"], "facts": ["minion.tensor-cache-path"],
  "what_is_inferred": "Tensor loads skip the L1 but are cached in L2 and L3; tensor stores skip the L1 and L2 (energy manual; PRM confirms only the L1 bypass).",
  "what_settles_it": "Mostly documents already in the repo: CORE-ET Shire Cache Specification §3.5 'REQ_WriteAround' (pdf p.62): TensorStores issue writeArounds that bypass the L2 (coalesced in its buffer, written to the L3 or a remote scratchpad); Minion DCache Description: TensorLoad requests go out the L2 miss interface (pdf p.32) and fill the L1 scratchpad straight from the L2 interface (pdf p.41). Whether the L2 allocates tensor-load lines: a re-load timing test (second TensorLoad of the same lines at L2-hit cost) or shire-cache counters.",
  "ask": "document (in repo) + experiment", "ask_detail": "exp-tensor-reload (no team ask needed)",
  "hub_anchor": "exp-tensor-reload", "hub_url": HUB + "exp-tensor-reload", "also": []},
 {"part": "the UC block, the I/O shire and the shire's voltage regions (one-line descriptions)",
  "comps": ["uc", "io"], "facts": ["chip.io-shire"],
  "what_is_inferred": "Not inferred, but thinly sourced: the UC block and the I/O shire's Maxions are drawn from one line of text, and the sources disagree on the Maxions' cache (4 MB in the datasheet and the PRM, 1 MB in the Shire Cache Specification).",
  "what_settles_it": "The design documents the open drop cites but leaves out: Power Spec, UC Specification, Shire Bus Master Specification, PLL/DLL Initialization, MAS: Minion Shire Debug, Debug High-Level Specification, Debug Memory Map, Minion CSRs, DFT Specification, Maxion Shire MAS, Maxion Tile MAS.",
  "ask": "document", "ask_detail": "ask-design-docs",
  "hub_anchor": "ask-design-docs", "hub_url": HUB + "ask-design-docs", "also": []},
 {"part": "the host link's open questions (PCIe shire, Host, Flow 6)",
  "comps": ["pcie", "host", "flow:F"], "facts": ["pcie.conc", "pcie.d2h", "pcie.staged"],
  "what_is_inferred": "Not inferred but unexplained, from the PCIe page: why two host-to-card DMA commands at once move half as much as one, why card-to-host DMA dips at 32-64 MB per copy, and why aifoundry3's host copies memory at about half the others' rate.",
  "what_settles_it": "The PCIe DMA engine's documentation, or the settings the firmware programs (channel arbitration, read-request size, element splitting); root reads on the hosts (lspci -vvv for the payload and read-request sizes, dmidecode for the memory channels); and an experiment: the concurrency test swept over command sizes and element counts, and repeated on a host with the IOMMU in passthrough.",
  "ask": "document / lab admin / experiment", "ask_detail": "ask-pcie-dma; ask-lab-root; exp-pcie-concurrency",
  "hub_anchor": "exp-pcie-concurrency", "hub_url": HUB + "exp-pcie-concurrency", "also": ["ask-pcie-dma", "ask-lab-root"]},
]
open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "asks.json"), "w").write(json.dumps(asks, indent=1, ensure_ascii=False) + "\n")
print(len(asks), "asks")
