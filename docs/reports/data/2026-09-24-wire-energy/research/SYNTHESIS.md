# Heat per millimetre on the ET-SoC-1 mesh: inputs and conversion

> **Read this first (added after the 24 September review, `../review/VERDICT.md`).** This file is the research
> behind the report, written before the report's own runs. Its **measured numbers are superseded** by
> `../wire.json` and `../report.json`: section 0 and section 2 convert the 23 September (E27) catalogue, including
> its d = 8 point and a 0.445 toggle rate, and their "101–137 fJ at 0.9 V" and "the capacitance per mm of a
> repeated wire from 2003–2011" do not describe the 24 September result. Corrections to the inputs and quotes:
> the hop range is **3.64–3.74 mm** (the three readings are 3.735, 3.711 and 3.637); VLSI 2018's 20–40 fJ/bit-mm
> sentence says "in present day chips" (the 16 nm is the paper's setting, not that sentence's); CACM 2020 states
> the 100 fJ/bit-mm in a paragraph about 14 nm on-chip memory; and the AHA 2023 talk's conclusion slide sets the
> figure beside "Reduce V until it gets too slow (~0.5V)". Board power carries the regulator's loss, so only the
> mesh rail's numbers should be V²-scaled for a comparison with die-level wire figures.

All arithmetic in section 2 is in `scratchpad/wire-research/synthesis/convert.py`. Run it with `python3`. The scratchpad root is `/tmp/claude-1019/-home-yaroslavvb-claude/ed6d06d5-de26-4323-94f1-0dc808eafbda/scratchpad/wire-research/`. Repository paths are relative to `/home/yaroslavvb/claude/et-soc1-prototyping/`. Every value marked "estimate" is derived here and not stated by a vendor or author.

## 0. Bottom line

- **One mesh hop is about 3.72 mm, with a range of 3.64–3.74 mm.** This is an estimate: I measured the pitch in pixels on the published die plot and scaled it to 570 mm². The tiles are square to within 1% (x 3.73 mm, y 3.70 mm), so hop direction does not matter.
- **Data-dependent heat, measured at the NoC's own 0.485 V:**
  - **Per payload bit:**
    - Board power: 35 fJ per payload bit per mm (range 34–36). If the d = 8 point is dropped, it is 44 (41–48).
    - NoC rail alone: 26 fJ/bit·mm (26–27), or 30 (29–31) without d = 8.
  - **Per wire transition:** the 'random' data toggles 0.445 of its bits per flit. That makes 79 fJ per transition·mm on board power and 59 on the NoC rail. Without d = 8 it is 99 and 67.
- **Total heat per bit moved.** This adds the per-hop costs that do not depend on the data, and it counts random data only:
  - Board: 58 fJ/bit·mm, or 73 without d = 8.
  - NoC rail: 43 fJ/bit·mm, or 50 without d = 8.
- **Compared with Dally's "~100fJ/b-mm on-chip" taken literally:** at its own voltage the ET-SoC-1 mesh is 1.3–3.8 times below that figure.
- **Scaled to 0.9 V:**
  - Why 0.9 V: it is the voltage of the Keckler 2011 and 40 nm "energy shopping list" figures, which is most likely where Dally's number comes from. That is an inference; no source says so.
  - Result: the measured data-dependent energy becomes 101–137 fJ per random bit·mm, or 116–170 without d = 8. That matches Dally's 100 and Keckler's 121.
  - The effective switched capacitance is 0.50–0.67 pF/mm, or 0.57–0.84 without d = 8. Keckler's 40 nm figure implies 0.59 pF/mm and Ho's 0.18 µm measurement gives 0.61. So the ET-SoC-1 mesh, routers included, has about the capacitance per mm of a repeated wire from 2003–2011. Its advantage comes almost entirely from V² (3.44 times from 0.9 V to 0.485 V).
- **Largest uncertainties.** The pitch contributes only ±1.6%. The largest is the d = 8 point, a systematic 20–30%. Next is whether the costs are per hop or per unit time, which the current design cannot separate. After that come regulator loss and meter gain on board power (the data-dependent slope on the NoC rail is about 25% below the board-power one).

---

## 1. Input numbers

Status: **V** = verified by a second pass; **C** = corrected by the verifier (corrected value shown); **U** = not independently re-verified.

### 1a. Die and floorplan

| Quantity | Value | Source (path / URL, quote or page) | Confidence | Status |
|---|---|---|---|---|
| Die area | **570 mm²** | Hot Chips 33 slide 20, https://hc33.hotchips.org/assets/program/conference/day2/HC2021.Esperanto.Dave_Ditzel.presentation.v1submitted.pdf: "Die-area: 570 mm2 ... 89 Mask Layers". IEEE Micro 42(3) 2022 p.37, https://www.esperanto.ai/wp-content/uploads/2022/05/Dave-IEEE-Micro.pdf: "It has a die area of 570 mm2 and uses 89 mask layers." | high | V |
| Die width × height | **≈25.6 × 22.2 mm** (other reading 25.8 × 22.1; overall 25.6–25.8 × 22.1–22.2) | Estimate. Pixel measurement of the IEEE Micro 2022 Fig. 7 die plot, scaled to 570 mm² (`geometry/pitch.json`, `verify_geom/remeasure.py`). No public or local source gives the die width and height. The verifier prefers case B (die bottom at the frame's outer edge): the vertical margins are then symmetric (24/24 px) and the bottom-row tile outlines stay inside the die. | medium | C (was 25.8 × 22.1) |
| Package | 45.0 × 45.0 mm (lid 44.8), 2494 balls, >30,000 bumps | `external/et-man/ET Preliminary Datasheet Rev 1.0.pdf` p.33 Fig. 9-1 (no die outline); HC33 slide 20: "Package: 45x45mm with 2494 balls to PCB, over 30,000 bumps to die" | high | V |
| Mesh grid | 8 × 6 grid, 44 mesh stops: 34 minion shires, PCIe, I/O, and 4 memory shires on each of the W and E sides; corners empty | `external/et-man/txt/ET Preliminary Datasheet Rev 1.0.txt` lines 1058–1066: "The NoC is organized as an 8 x 6 grid ... there are 44 total mesh stops." | high | V |
| Tile pitch x (E–W) | **3.73 mm** (3.75 under case A) | Estimate. 254.7–254.8 px, measured both on the blue tile outlines and by 5-period autocorrelation (`geometry/pitch.py`, `verify_geom/remeasure.py`) | medium | C |
| Tile pitch y (N–S) | **3.70 mm** (3.72 under case A) | Estimate. 252.6–252.8 px, same method | medium | C |
| Mean hop length √(px·py) | **3.72 mm, range 3.64–3.74** | Estimate. √(570 / (6.883 × 5.94…6.02)): case A 3.735, case B 3.711, case C 3.637 (570 mm² including the drawn frame); ±1% if 570 is rounded. The mean does not change if the image was stretched unevenly. | medium | C (the 3.78 upper bound came from a reticle argument that does not hold: a 26 × 33 mm exposure field limits only the short side) |
| Pitch x / pitch y | 1.008 | Micro22 outlines and autocorrelation 254.78 / 252.71 | high | V |
| Shire-grid span | 6 columns ≈ 22.2 mm (86% of width); memory-shire + LPDDR4x PHY strips 1.74 and 1.80 mm; rows fill the height (margins 0–0.35 mm) | Estimate from the tile outlines at x ≈ 139.5–1649.5 px | medium | C (the original 22.5 + 2 × 1.77 = 26.0 mm exceeded the die width) |
| Minion-shire cell area | ≈13.8–13.95 mm²; the 34 shires take ≈468–474 mm² (82–83% of the die) | Estimate | medium | V |
| Naive pitches (wrong) | width / 8 = 3.2 mm (14% low); √570 / 6 = 3.98 mm (7% high) | Arithmetic | high | V |
| Three copies of the die plot | IEEE Micro 2022 Fig. 7, MPR Dec 2020 Fig. 1, HC33 slide 20 | These are resizes of one Esperanto image. They agree with each other, which shows consistent resizing but does not confirm the aspect ratio. | — | C |
| Logical map vs die | Logical x runs N–S and y runs E–W. The empty cells are (0,3) = top row col 4, (0,4)/(0,5) = I/O and PCIe, and (5,3) = bottom row col 4. | Inference from `workloads/nocbench/analyze.py:37` `EMPTY=[(0,3),(0,4),(0,5),(5,3)]`, `workloads/memprobe/gen_ops.py:251–258`, and Chang's topology figure https://clehaxze.tw/gemlog/2026/04-27-tnvestigating-the-et-soc-1-noc.gmi. It does not matter here because px ≈ py. | medium | V |
| Top-row order | PRM Fig. 1-3 (p.18): PCIe in col 5, I/O in col 6. Die plot with MPR caption: I/O (purple, Maxion) in col 5, PCIe (orange) in col 6. | The two sources are mirror images of each other. | low | C (conflict) |
| Minion-to-memory-shire hop | ≈2.8 mm if mesh stops sit at cell centres | Guess: (3.75 + 1.77) / 2 | low | unsupported |

### 1b. NoC: width, clock, voltage, routing

| Quantity | Value | Source | Confidence | Status |
|---|---|---|---|---|
| AXI data width at every shire NoC port | **512 bits**, one 64 B line per beat, single-beat only | `external/core-et/rtl/inc/axi_defines.vh:43` "`` `define SC_MESH_MASTER_AXI_DATA_SIZE 512 ``", `:61` "`AXLEN 8'b0`". `external/core-et/docs/CORE-ET-Shire-Cache-Specification.pdf` §8.4.1: "Fixed AxLEN==0 ... no multi-line bursts supported". | high | V (spot-checked) |
| Memory-shire NoC port | 512-bit, 32 GB/s peak (= 64 B × 500 MHz design clock) | Datasheet txt lines 1368–1373: "The NoC delivers a maximum bandwidth of 32 GByte/s ... This port has a 512-bit data path" | high | V (spot-checked) |
| Flit width on router-to-router links | **Unknown.** Estimate: 512 data bits per layer | Inferred from the 32 GB/s port at clk__noc 500 MHz (CORE-ET Minion Shire Description Table 2; `core-et/rtl/inc/soctop_defines.vh:11`). The NetSpeed reference manual named at `debug_defines.vh:831` is not in the repo. | low | U |
| Main-NoC layers | 9 routers per mesh stop (0–8) plus 1 debug-NoC router; very likely 9 physical networks | `external/et-platform/etsoc-hal/include/hwinc/etsoc_shire_other_esr.h:3877–3981`; PRM txt:14244 "8:0: Main data NOC rounter 8:0"; `noc_esr.h:329011` (router-ID LAYER field) | medium | U |
| Router ports and VCs | 8 ports (H, E, S, W, N, I, J, K), 4 VC slots each | `noc_esr.h:324550–324826` | medium | U |
| Lanes | 4 to_l3 master and 4 L3 slave lanes per shire. Lane is chosen by PA[7:6], so a 1 KB load puts 4 of its 16 lines on each lane. | `core-et-main/hw/ip/shirecache/rtl/shirecache_mesh_master.sv:141–153` (clean-room RTL) | medium | U |
| Measured data per link direction | ≥46.8 GB/s per reader at d = 1, over a link it uses alone: **≥117 B per 400 MHz cycle (≥936 data bits)**. That is more than one 512-bit layer (25.6 GB/s), and the link is not saturated. | `docs/reports/data/2026-09-23-energy-manual/catalogue.json` wire/hop1 (1497.6 GB/s over 32 readers) | high (as a lower bound) | U |
| Published link width | "Those links appear to be 1,024b wide each" (WikiChip: two unidirectional links per direction); "one link in each direction, each delivering 128GB/s at 1.0GHz" (MPR) | https://web.archive.org/web/2022/https://fuse.wikichip.org/news/4911/ ; https://esperanto.ai/wp-content/uploads/2021/01/Esperanto-Minions-Excel-at-AI.pdf | low | V (the quotes are right; the two sources conflict) |
| NoC clock | **400 MHz** (design point 500 MHz) | `external/et-platform/device-bootloaders/src/ServiceProcessorBL2/common/main.c:90` "NOC frequency modes (400MHz)"; telemetry `mhz.noc` = 400 | high | V (spot-checked) |
| NoC voltage | **0.485 V** set, 0.484 V at the die (V² = 0.2352) | `docs/reports/data/2026-09-22-hotline-aifoundry2/telemetry.jsonl.gz`: `reg_mv.noc` 485, `die_mv.noc` 484. Firmware allows 485–600 mV for 300–500 MHz: `.../ServiceProcessorBL2/services/thermal_pwr_mgmt.c:80,106,134–135`. | high | V (spot-checked) |
| Voltage domain | Routers, links and NetSpeed bridges are on the low-voltage NoC rail. The shire-cache side of each crossing is high-voltage, probably the SRAM rail. | IEEE Micro 2022: "on-chip mesh interconnect operated on its own low-voltage domain"; `core-et/rtl/libs/mems_and_fifos/vcfifo_nsip_brdg2rtr.v:9` "The router interface is at low voltage domain" | medium | U |
| Routing | **Minimal.** Latency = a + b × Manhattan distance, r² 0.9999 over 496 pairs, so a pair d apart crosses d links each way. Dimension order is unknown; Chang infers XY. | `docs/reports/2026-09-18-et-soc1-on-chip-communication.html`; Chang (URL above) | high (minimal) / low (XY) | U |
| Per-hop latency | 20 ns round trip ≈ 4 NoC cycles each way at 400 MHz. Chang reports 3 cycles per direction (clock unstated); not reconciled. | Same report; `docs/findings/15-earlier-findings.md` | high | U |
| Bits per 64 B line | Response: 512 data + RID/RRESP/RLAST (524–534 total) + a NetSpeed header of unknown width. Request: about 75–85 bits, travelling the opposite way over the same d links (about 14% of AXI bits). | `core-et/rtl/inc/axi_defines.vh:39,69`; `axi_types.vh` | medium | U |
| Error protection | Parity on route info, packet, sideband and data; no ECC | `noc_esr.h:329212–329248` | medium | U |
| Idle NoC-rail power in E27 | 4.29 W (aifoundry2), 2.29 W (aifoundry3) | catalogue.json `noc_idle_w` median | high | U |

### 1c. Measurement inputs (E27, energy manual 4.3)

Setup: 1 KB tensor loads from the scratchpad of a shire exactly d hops away, d = 1–6 and 8, every shire reading, at most 2 readers per target, on two cards. Sources: `docs/energy-manual/04a-fine-grain.md` lines 9–26 and 132, and the rail refits in `critique/railfit.py` / `railfit.json` on `catalogue.json`.

| Slope (pJ per payload byte per hop) | All d: aifoundry2 / aifoundry3 | d ≤ 6: aifoundry2 / aifoundry3 |
|---|---|---|
| Board, zeros | 0.748 / 0.641 (manual: 0.70 [0.64–0.75]) | 0.887 / 0.841 |
| Board, random | 1.805 / 1.668 (manual: 1.74 [1.67–1.81]) | 2.277 / 2.078 |
| **Board, random − zeros** | **1.058 / 1.028** (manual: 1.05 [1.03–1.06] = 131 fJ/bit/hop [129–133]) | **1.390 / 1.237** |
| NoC rail, zeros | 0.498 / 0.484 | 0.610 / 0.589 |
| NoC rail, random | 1.287 / 1.261 (manual line 132: 1.287, intercept 1.50) | 1.506 / 1.468 |
| **NoC rail, random − zeros** | **0.789 / 0.777** | **0.895 / 0.879** |
| SRAM rail, random − zeros | 0.017 / 0.027 | 0.053 / 0.052 |
| Minion rail, random − zeros | 0.056 / 0.039 | 0.022 / −0.007 |
| Unmetered (board − rails), random − zeros | 0.197 / 0.185 (about 25% of the NoC-rail difference) | 0.420 / 0.313 |

Notes on the slopes:
- The dally verifier said the repo did not report a zero-data slope for the NoC rail. The critique's refit of `catalogue.json` supplies one (0.48–0.50 pJ/B/hop), so the data-dependent part of the mesh-rail slope is known: 0.78–0.79 pJ/B/hop.
- The leakage correction removes 0.03–0.08 pJ/B/hop from the board difference.

| Other measurement input | Value | Source | Confidence |
|---|---|---|---|
| Toggle rate of the 'random' prefill, one flow in address order, 64 B flits | **0.445 toggles per payload bit per flit** (32 B: 0.433; 128 B: 0.470; chunks from two different flows: 0.471) | `critique/toggles.py`, `toggles.json`. The image was rebuilt from a verbatim copy of `sources()` in `workloads/enercat/host/main.cpp` (`critique/gen_sources.cpp`). | high for the reconstructed image |
| Toggle rate if a minion's two in-flight 1 KB loads interleave line by line | 0.213 (the image repeats every 512 B, so the lines are identical) | `toggles.json` `lockstep_pair_W64` | medium |
| Per-wire activity | sign bit 0 (always 0); exponent bits 30–24: 0.278; bit 23: 0.458; mantissa: 0.498. Ones density 0.506. | `toggles.json` | high |
| Bandwidth per reader shire vs d = 1, 2, 3, 4, 5, 6, 8 | 46.8, 41.8, 37.4, 32.8, 30.9, 26.7, 25.5 GB/s (identical on both cards; zeros and random agree to within 0.02%). Correlation of d with 1/bandwidth: 0.985. | `catalogue.json` | high |
| Readers vs d | 32 (d = 1–5), 31 (d = 6), 16 (d = 8); mean hops exactly d | `catalogue.json` | high |
| Link sharing vs d (XY routing) | Share of link-hops on shared links: 0, 22, 32, 55, 72, 72, 64% for d = 1, 2, 3, 4, 5, 6, 8. Up to 4 flows share one link. | `critique/linkload.py` | medium |
| d = 8 anomaly | Board random − zeros per byte goes from 12.17 to 11.99 pJ/B (aifoundry2) and from 10.84 to 11.83 (aifoundry3) between d = 6 and d = 8. Two more hops should add about 2.1–2.8. 55–58% of d = 8 link-hops are on edge rows or columns, against 23–36% at other d. | `railfit.py`, `empty_cells.py` | high (data) / medium (geometry) |
| Cost of leaving the shire | Difference intercept 3.9–4.8 pJ/B vs 2.28 pJ/B for the local path, so about 1.6–2.5 pJ/B (equivalent to 1.2–2.4 hops) | `railfit.py`; `catalogue.json` tload/scp | medium |

### 1d. Dally's figure, verbatim, and its conditions

Source: W. Dally, "Energy Efficiency and AI Hardware", Stanford AHA Retreat, 31 Aug 2023, https://aha.stanford.edu/sites/g/files/sbiybj20066/files/media/file/aha-retreat-2023_dally_keynote_en_eff_ai_hw_0.pdf (local copy `lit/dally_aha2023.pdf`; text lines cited from `lit/dally_aha2023.txt`). The re-download is identical.

| Slide | Verbatim | Status |
|---|---|---|
| 8 | "E = ½CV²  C: Three components • **Communication (~100fJ/b-mm on-chip)** • Memory (~50fJ/b for small RAM) • Operations (~1fJ/b for add)" (txt line 130) | V |
| 45 (Conclusion) | "V² – Reduce V until it gets too slow (~0.5V)" / "C – Communication (100fJ/b-mm), Memory (50fJ/b), Operations (Add - 1fJ/b)" (txt lines 712, 715) | V |
| 7 | "~0.5V today • 2x vs 0.7v, 4x vs 1.0v" (a pure V² rule) | V |
| 27 | "Cost of an add (1fJ/bit) = Cost of going 10um." (= 100 fJ/mm) | V |
| 13 | "An add is worth 10um of movement", citing Dally CACM 2022. In that paper the same equivalence works out to about 30 fJ/b·mm, so slides 13 and 27 disagree. | V (inconsistency found by the verifier) |
| 31 | "48mm round trip on GPU die • 4.8pJ/b @ 100fJ/b-mm • 16mm round trip on DRAM die • 1.6pJ/b • Part of 5pJ/b access" (applied to a modern HBM-class GPU, with no voltage given) | V |
| 11 / 12 | The only process-node labels in the talk: "all 28nm" (16b int add 32 fJ; OOO CPU instruction 250 pJ) and "Energy numbers from 45nm process" | V |

**Conditions:**
- **None stated.** The talk gives no process node, voltage or data activity for the 100 fJ/b-mm, and the unit is per bit moved, not per transition.
- Slide 45 puts the figure next to "~0.5V" but does not say it applies at that voltage.
- The figure could also be read as a system-level budget for communication between blocks, including flops and clocking. The CACM 2020 wording is "Communication between blocks on chip".

### 1e. Other literature values and their conditions

| Source | Value | Conditions | Confidence | Status |
|---|---|---|---|---|
| Keckler, Dally et al., IEEE Micro 31(5) 2011, Table 1 and p.9, https://www.cs.toronto.edu/~pekhimenko/courses/csc2224-f19/docs/GPU.pdf | "Wire energy (per transition) 240 femtojoules (fJ) per bit per mm"; "Wire energy (256 bits, 10 mm) 310 pJ", which is **121 fJ per random bit·mm** | 40 nm, 0.9 V, 2010; "assuming random data with a 50 percent transition probability"; "wire capacitance per mm remains approximately constant across process generations". The meaning of "per transition" is ambiguous: C is 0.30 pF/mm if it means CV², or 0.59 if CV²/2. | high | V |
| Same, 10 nm projections | 150 fJ/bit/mm at 0.75 V (200 pJ); 115 at 0.65 V (150 pJ) | Projections using CV² scaling | high | V |
| Dally, Yale Patt 75 (2014) slide 16, https://hps.ece.utexas.edu/yale75/dally_slides.pdf; Jan 2017 DLI deck slide 58 | 40 nm, 0.9 V: 310 pJ (121 fJ/b·mm); **10 nm, 0.7 V: 174 pJ = 68 fJ/b·mm** | Per 256 random bits over 10 mm; cites Keckler 2011 | high | V |
| Same deck, slide 18 (read off the plot) | Full swing about 185 fJ/bit/mm at low f, rising to about 300 at 1.65 GHz. Low swing about 20 (200 mV) and about 50 (400 mV), rising to 38 and 73 at maximum f. CDI 57–123, SCI 27–60. | No node, voltage or activity stated | medium | V |
| Dally SC12, slide 14, https://developer.download.nvidia.com/GTC/PDF/GTC2012/PresentationPDF/BillDally_NVIDIA_SC12.pdf | 256-bit buses 26 pJ / 256 pJ / 1 nJ on a "20mm", "28nm" die. Using the drawn lengths (about 1.2, 6.8 and 31 mm), that is **82–147 fJ/b·mm**. | No voltage or activity stated. The "~100" comes from the energies themselves, not the drawing. | medium | C (the 1/10/40 mm lengths are not in the drawing) |
| Same, slide 16 ("efficient signaling") | 3 / 30 / 100 pJ, about 9–17 fJ/b·mm | Same caveats | medium | V |
| Dally et al., VLSI Symp. 2018, https://research.nvidia.com/sites/default/files/pubs/2018-06_Hardware-Enabled-Artificial-Intelligence/VLSI2018_HardwareAI.pdf.PDF | "~ CV2, where C ... about 200fF/mm and independent of scaling ... energy efficiency for on-chip wires is between **20-40 fJ/bit-mm**" | "a typical 16 nm technology". If this is random data (CV²/4 per bit), it implies V ≈ 0.63–0.89 V. The paper also says the low-swing V² term "is Vsupply × Vsignal". | high | V |
| Dally, Turakhia, Han, CACM 63(7) 2020 p.56, https://www.doc.ic.ac.uk/~wl/teachlocal/arch/papers/cacm20dsa.pdf | "This communication costs **100fJ/bit-mm**"; memory cost 50 + 0.022√S fJ, which is a round trip at 100 fJ/bit·mm | Main-text paragraph that starts in 14 nm; the 100 fJ/bit·mm sentence has no node of its own | high | C (main text, not a sidebar) |
| Dally, CACM 65(9) 2022, "On the model of computation: point", DOI 10.1145/3548783 | "Moving the two 32-bit words ... 1mm takes 1.9pJ"; "64 bits 40mm ... 77pJ", both **≈30 fJ/b·mm** | No node stated. Checked against the local copy only; the mirror and cacm.acm.org were unreachable. | high | V (local copy) |
| Horowitz, ISSCC 2014, Fig. 1.1.9, https://gwern.net/doc/cs/hardware/2014-horowitz-2.pdf | "Rough energy costs for various operations in 45nm 0.9V": 32b add 0.1 pJ, 8 KB cache 10 pJ, DRAM 1.3–2.6 nJ | **No per-mm wire figure** | high | V |
| R. Ho, Stanford PhD 2003, sec. 6.2, https://vlsiweb.stanford.edu/people/alum/pdf/0303_Ho_Wires.pdf | Measured full-swing repeated bus: "9.84pJ/bit over the 10mm link at Vdd = 1.8V" with 0101 toggling, which is **0.98 pJ per transition·mm, C_eff 0.61 pF/mm**. Low swing about 0.8 pJ/bit. | TSMC 0.18 µm, 1.8 V | high | V |
| Ho 2003, Table 4.2 | Repeated-wire energy is 1.87 × C_w·L·V² at delay-optimal sizing and 1.34 × at energy-delay-optimal sizing | Normalised 0.18 µm-era model; transfers only roughly to 7 nm | high | V |
| Ho 2003, Table 2.6 | 0.25–0.29 fF/µm projected at 13–25 nm | Worst case (Miller factor 2) | medium | V |
| Turner et al., CICC 2018 (NVIDIA GRS), https://research.nvidia.com/sites/default/files/pubs/2018-04_Ground-Referenced-Signaling-for/CICC2018_GRS_18-5.pdf | "a 16Gb/s 170fJ/b/mm on-chip link"; channel "R=130Ω/mm, C=305fF/mm" | 28 nm, low swing, retimed every 1.5 mm; includes TX/RX and clocking; 0.5 µm-wide top metal | high | V |
| Wilson et al., ISSCC 2016 (NVIDIA) | 6.5–23.3 fJ/b/mm charge-recycling bus | 16 nm FinFET; from the title only | low | V (title) |
| NVIDIA JSSC 58(4) 2023, https://research.nvidia.com/publication/2023-04_0297-pjbit-504-gbswire-inverter-based-short-reach-simultaneous-bi-directional | 0.297 pJ/bit over a 1.2 mm on-chip channel | 5 nm, 750 mV; transceiver-dominated, so not a per-mm wire cost | medium | V |
| FlooNoC, IEEE TVLSI 33(4) 2025, https://arxiv.org/pdf/2409.17606 | 0.15 pJ/B/hop at 0.8 V: "the routers only consume 596 pJ" for one neighbour 4 kB transfer | GF 12 nm, post-layout; tiles 0.75 × 1.5 mm. **This does not convert to fJ/b·mm**: links are not separated, the data pattern is not given, and a transfer crosses two router stages. | medium | C |
| ASAP7 predictive 7 nm PDK, https://raw.githubusercontent.com/The-OpenROAD-Project/OpenROAD-flow-scripts/master/flow/platforms/asap7/setRC.tcl | Wire C per layer: M2 0.175, M3 0.156, M4 0.178, M5 0.164, M6 0.187, M7 0.163, M8 0.104, M9 0.093 fF/µm; signal average 0.166 | Predictive, not TSMC N7. Pitches 36/48/64/80 nm (https://pages.hmc.edu/harris/research/asap7.pdf Table II). | medium | V |
| D. Harris, "Interconnect RC" lecture, https://pages.hmc.edu/harris/class/hal/lect4.pdf | "most wires have about 0.2 fF/µm of total capacitance" | 1997 lecture | high | V |
| LessWrong post "~100 fJ/bit/mm ... at 1V" | — | A blogger's own derivation; **not a source** for Dally's conditions | — | excluded |

I found no measured fJ/bit/mm figure for a plain repeated wire in 7 nm or 5 nm.

### 1f. First-principles estimate at 0.485 V (all estimates)

| Quantity | Value | Basis |
|---|---|---|
| Heat per transition, either direction | ½CV² | Half of the CV² drawn on a 0→1 transition is dissipated then, and half on the following 1→0 |
| Total switched C of a repeated 7 nm wire | **200–400 fF/mm, central 300** | ASAP7 0.166 fF/µm × 1.34 = 222 up to 0.2 fF/µm × 1.87 = 374. On top metal (ASAP7 M8/M9 0.093–0.104) it could be as low as about 125 fF/mm. |
| Per transition·mm (½CV²) | **35 fJ (24–47)** | 0.5 × 300 fF × 0.2352 V² |
| Supply energy per 0→1 per mm (CV²) | 71 fJ (47–94) | |
| Per random bit·mm (q = 0.5, i.e. CV²/4) | **17.6 fJ (12–24)** | |
| Per payload bit·mm at the actual q = 0.445 | 15.7 fJ (10.5–20.9) | |
| Per transition per 3.72 mm hop (wire only) | 131 fJ (88–175) | |
| V² scaling factors to 0.485 V | 0.941 from 0.5 V; 0.557 from 0.65; 0.480 from 0.7; 0.418 from 0.75; 0.368 from 0.8; 0.290 from 0.9 | Same C, full-swing CMOS only. For low-swing links energy goes as V_supply × V_swing. |
| Dally's 100 fJ/b·mm moved to 0.485 V | 94 if it was quoted at 0.5 V; 42 at 0.75; 37 at 0.8; 29 at 0.9 | The quoting voltage is not stated in any source |
| Capacitance implied by 100 fJ/b·mm | At 0.5 V: 0.8 pF/mm (one transition per bit) to 1.6 pF/mm (random data), 4–8 times a wire's 0.2. At 0.9 V with random data: 0.49 pF/mm, close to Keckler at 40 nm. | Inference: the rule of thumb is most likely a 28–40 nm, ~0.9 V number that was never rescaled. No source says this. |
| Keckler 40 nm moved to 0.485 V | 69.7 fJ per transition·mm; 35.1 per random bit·mm | 240 × 0.290; 121 × 0.290 |

---

## 2. Converting the E27 measurement

### 2a. Conventions

- Per payload bit per hop: E_b = slope [pJ/B/hop] × 1000 / 8.
- Per mm: E_b / L, where L = 3.72 mm (3.64–3.74). A hop is assumed to be one tile pitch of travel.
- Per transition: E_b / q, where q = 0.445 toggles per payload bit per flit (0.433–0.471). This applies only to the **random − zeros differences**, because zeros toggle no payload wires.
- Effective switched capacitance: C = 2 E_trans / V², with V = 0.485 V.
- "Per random bit" means q = 0.5, the convention behind Keckler and Dally's 310 pJ figure: E_rb = 0.5 × E_trans.
- Scaling to V0: multiply by (V0 / 0.485)².
- In the tables, "pitch-only" ranges vary only L. "Full" ranges also span the two cards and, for per-transition values, the range of q.

### 2b. Per bit per mm at the chip's own 0.485 V

| Quantity | pJ/B/hop [cards] | fJ/bit/hop | **fJ/bit·mm** | pitch-only | full | d ≤ 6: pJ/B/hop → fJ/bit·mm [full] |
|---|---|---|---|---|---|---|
| **Board, random − zeros** (data-dependent) | 1.05 [1.03–1.06] | 131 [128–132] | **35.3** | 34.9–36.1 | 34.2–36.3 | 1.31 [1.24–1.39] → **44.0** [41.1–47.7] |
| Board, zeros (data-independent per-hop cost) | 0.70 [0.64–0.75] | 87.5 [80–94] | **23.5** | 23.3–24.0 | 21.3–25.7 | 0.86 [0.84–0.89] → 28.9 [28.0–30.5] |
| Board, random (total heat per bit moved) | 1.74 [1.67–1.81] | 218 [208–226] | **58.5** | 57.8–59.8 | 55.5–62.0 | 2.18 [2.08–2.28] → 73.3 [69.1–78.2] |
| **NoC rail, random** (total, on the die's mesh supply) | 1.29 [1.26–1.29] | 161 [158–161] | **43.3** | 42.9–44.3 | 41.9–44.2 | 1.49 [1.47–1.51] → 50.1 [48.8–51.7] |
| **NoC rail, random − zeros** | 0.78 [0.78–0.79] | 97.5 [97–99] | **26.2** | 25.9–26.8 | 25.8–27.1 | 0.89 [0.88–0.90] → 29.9 [29.2–30.7] |
| NoC rail, zeros | 0.49 [0.48–0.50] | 61 [60–62] | 16.5 | 16.3–16.8 | 16.1–17.1 | 0.60 [0.59–0.61] → 20.2 [19.6–20.9] |

The "zeros" and "total" rows are per payload bit moved, not per toggle. They include clocking, arbitration, buffering and the request packets. Because bandwidth per reader falls by 45% from d = 1 to d = 8 (section 2e), part of them may be cost per unit time rather than cost per hop.

### 2c. Per transition per mm, and effective capacitance (data-dependent rows only)

| Quantity | fJ per transition per hop | **fJ per transition·mm** | pitch-only | full | C_eff per hop | C_eff per mm |
|---|---|---|---|---|---|---|
| Board, random − zeros, all d | 295 | **79.3** | 78.4–81.0 | 72.6–83.9 | 2.51 pF | 674 fF/mm |
| Board, random − zeros, d ≤ 6 | 368 | **98.9** | 97.9–101.1 | 87.3–110.2 | 3.13 pF | 841 fF/mm |
| NoC rail, random − zeros, all d | 219 | **58.9** | 58.3–60.2 | 54.8–62.6 | 1.86 pF | 501 fF/mm |
| NoC rail, random − zeros, d ≤ 6 | 250 | **67.2** | 66.5–68.7 | 62.0–71.0 | 2.13 pF | 571 fF/mm |
| *Plain 7 nm repeated wire (estimate, 1f)* | *131 (88–175)* | *35 (24–47)* | | | *1.1 (0.7–1.5) pF* | *300 (200–400)* |

What the comparison shows:
- The measured energy is **1.7–1.9 times** the central plain-wire estimate on the NoC rail (1.2–3.0 across all ranges) and **2.2–2.8 times** on board power (1.5–4.7).
- The excess per hop is roughly 45–280 fJ per transition, depending on which measurement and which wire-capacitance estimate is used. It is consistent with router datapath energy: pipeline flops (about 4 NoC cycles per hop), crossbar and buffers. A routed wire longer than the pitch would also add to it.
- These data cannot separate router energy from wire energy, because every hop has the same length (x and y pitch differ by only 0.8%).
- If a minion's two in-flight loads actually run in lockstep (q = 0.213), every per-transition figure above roughly doubles: 166 fJ/transition·mm on board power, 123 on the NoC rail.

### 2d. Scaled to the voltages Dally's figure might assume

Dally states no voltage. The candidates are:
- 0.5 V, which slide 45 puts next to the figure;
- about 0.8 V, the usual nominal voltage at 14/16 nm, the context of CACM 2020 and VLSI 2018. The 0.8 V is my assumption, not a sourced value;
- 0.9 V, the voltage of the Keckler 2011 and 40 nm "shopping list" figures, which the arithmetic matches best.

Only the NoC-rail share of the energy should strictly be V²-scaled. On board power, the metered SRAM and minion rails together contribute 0.05–0.08 pJ/B/hop of the difference, 7% or less. The unmetered part, about 25%, is most likely regulator loss, which scales with NoC-rail power.

| V0 | Factor | Board diff, per transition·mm | **Board diff, per random bit·mm** | NoC-rail diff, per transition·mm | **NoC-rail diff, per random bit·mm** | Dally (as stated) | Keckler 2011 at 0.9 V |
|---|---|---|---|---|---|---|---|
| 0.485 (measured) | 1.000 | 79 [73–84] | **40** [36–42] | 59 [55–63] | **29** [27–31] | | |
| 0.5 (slide 45) | 1.063 | 84 [77–89] | **42** [39–45] | 63 [58–67] | **31** [29–33] | 100 | |
| 0.75 | 2.391 | 190 [174–201] | 95 [87–100] | 141 [131–150] | 70 [66–75] | 100 | |
| 0.8 (assumed 14/16 nm nominal) | 2.721 | 216 [197–228] | 108 [99–114] | 160 [149–170] | 80 [75–85] | 100 | |
| **0.9 (Keckler lineage)** | 3.444 | 273 [250–289] | **137** [125–144] | 203 [189–215] | **101** [94–108] | **100** | 240 per transition; **121** per random bit |

For d ≤ 6, the same columns are:
- at 0.5 V: board 105 / 53, NoC rail 71 / 36;
- at 0.9 V: board 341 / **170** and NoC rail 231 / **116** fJ per transition·mm / per random bit·mm.

Total NoC-rail heat per random bit·mm, including the data-independent part: 46 at 0.5 V and 149 at 0.9 V (all d), or 53 and 172 for d ≤ 6. This assumes the clock and flop energy also goes as V² at a fixed per-hop count.

### 2e. Comparison, and the caveats that go with it

**Comparisons:**
- **At the chip's own voltage:** Dally's 100 fJ/b·mm as stated is 1.3–3.8 times above ET-SoC-1's measured heat per bit·mm. The data-dependent part is 26–44 fJ/b·mm and the total 43–77.
- **Back-scaled, like for like:**
  - Moved to 0.485 V, Dally's figure gives 29 (from 0.9 V) to 94 (from 0.5 V).
  - The measured data-dependent energy per random bit, 29–40 fJ/b·mm (or 31–55 for d ≤ 6), matches the 0.8–0.9 V reading (29–37). It is well below the 0.5 V reading (94).
  - Keckler's 40 nm numbers moved to 0.485 V (69.7 per transition·mm, 35 per random bit·mm) fall inside the measured range (59–99 per transition·mm, 29–50 per random bit·mm).
- **Capacitance:** 0.50–0.84 pF per mm of mesh travel, routers included. Keckler at 40 nm implies 0.59 pF/mm (CV²/2 convention) and Ho measured 0.61 pF/mm at 0.18 µm. A plain 7 nm wire is 0.2–0.4.

**Caveats, most important first:**
1. **The d = 8 point changes the slope by +20–30%, far more than the pitch (±1.6%).** It has half as many readers, 55–58% of its link-hops on edge rows or columns, and 7–9 of its 16 flows cross non-compute stops. Report both the all-d and d ≤ 6 values.
2. **Per-hop and per-time costs are confounded.** Bandwidth per reader falls from 46.8 to 25.5 GB/s as d grows (correlation 0.985), and link sharing grows from 0% to 72%. The random − zeros difference cancels costs per unit time only if they do not depend on the data; the zeros and total rows do not cancel them.
3. **Board power includes regulator loss and possible meter gain error.** The unmetered part of the difference is 0.19–0.20 pJ/B/hop for all d, but 0.31–0.42 for d ≤ 6, so it is not a constant efficiency. The NoC rail excludes regulator loss, but its gain has not been checked. For heat on the die itself, the NoC-rail rows are the better estimate, provided the meter is accurate.
4. **"Per mm" means per mm of mesh travel,** counting one router and one pitch per hop. It is an upper bound on the energy of the wire alone. This matches how Dally uses the number on slide 31 (a whole-die round trip), but not his "E = ½CV²" framing on slide 8.
5. **The toggle rate rests on the reconstructed image and on sys_emu's row order** (row n from f_n, srcinc = STEP+1). If silicon follows the PRM formula k = FREG + 2nSTEP instead, the 'random' image hardly toggles within a flow, and the per-transition figures would be wrong. Interleaving could also halve q (0.213).
6. **V² scaling assumes full-swing CMOS at constant capacitance.** Whether the links are low-swing is unknown.
7. **The pitch is an estimate from a die plot,** with no vendor dimension. It assumes the metal between routers is one pitch long.

---

## 3. Experiment design changes recommended by the critique

1. **Make every flit's data independent.** Fill the whole 32 KB slot with unique contents instead of repeating a 512 B image 64 times. Then a minion's two in-flight loads, and two readers of the same target, no longer carry identical lines. Also allow only one reader per target.
2. **Sweep bit density.** Use `bern:p` for p in {0, 0.02, 0.05, …, 0.5, …, 1}, and make `bern:(1−p)` the exact bitwise complement of `bern:p`. Fit E = a·2p(1−p) + b·p per d:
   - a is the cost of a toggle on wires that hold their value;
   - b is a level-dependent cost (return-to-zero wires, or headers on the data wires);
   - comparing p = 1 with p = 0 is the key test;
   - the small values of p expose parity bits, which toggle about half the time for any 0 < p < 1.
3. **Use `alt:N` as a flit-width probe only for N ≤ 32 B.** For those N every line is identical and the toggle rate is W/N (or 0), whatever the interleaving. For N ≥ 64 the result depends on interleaving and on how many parallel networks there are. Add a **"frozen random line"** pattern, the same random 64 B line everywhere: it has 50% ones but zero toggles if W ≥ 64 B, which also controls for data-dependent energy in the scratchpad and L1.
4. **Use the same number of flows at every d, on non-overlapping links.** For example, one eastbound and one westbound flow per full row. Then participation and contention no longer rise with d.
5. **Throttle every flow to the same bytes/s,** below the worst case of about 0.8 GB/s per minion, and vary the number of flows N independently of d. Fit rail power = end cost·B + hop cost·B·d + toggle cost·B·d·q + level cost·B·d·p + per-flow time cost·N.
6. **Log the bytes each shire moves.** Per-flow bandwidth is not recorded today; only aggregates are.
7. **Verify the scratchpad image on silicon.** `--dump-slice` currently skips scratchpad runs. Run it with `--pattern tstore --operands random` to settle the row-order question (sys_emu or PRM).
8. **Make the NoC rail the primary meter and check its gain** against board power, to resolve the 25–47% unmetered excess.
9. **Run on the cooler card (aifoundry3),** where leakage scatters less (the hot card scatters 0.4–1.1 pJ/B point to point).
10. **Measure link capacity:** one flow alone, and two flows forced onto one link. This settles the flit width or number of layers behind the ≥117 B/cycle observation.
11. **Regress on each configuration's physical path length in mm,** using the x/y pitches and the lengths of edge and non-compute stops, rather than on d. Treat or investigate d = 8 separately.
12. **Fix or drop the planned `--hop-axis` x-only and y-only runs.** They inherit the old confounds: readers x 32, 32, 28, 16, 6 and y 32, 29, 28, 20, 10 for d = 1–5, and up to 69–76% of link-hops shared. The geometry work adds a derived point: the x and y pitches differ by only 0.8%, so the axis split **cannot** separate router energy from wire energy on this die. Hops of different physical length would be needed, such as a memory-shire column (≈1.7–1.8 mm wide) or the off-grid I/O and PCIe blocks. Whether mesh stops there sit at different spacings is unknown.
13. **Report the cost of leaving the shire separately.** It is 1.6–2.5 pJ/B, equal to 1.2–2.4 hops.
14. **Change the NoC voltage or clock.** Energy goes as V², while costs per unit time go as f, so this would be the cleanest way to separate them. It needs a settings change on the shared lab cards, and the user would have to approve it first.

---

## 4. Open questions

1. **What conditions sit behind Dally's 100 fJ/b·mm?**
   - No node, voltage or data activity is stated in AHA 2023, CACM 2020 or SC12.
   - The reading that it is a ~0.9 V, 28–40 nm random-data number never rescaled is an inference. The alternative is a system-level budget that includes flops and clocking.
   - Dally's own later figures are 20–40 fJ/bit·mm (VLSI 2018, 16 nm) and ≈30 (CACM 2022), and slides 13 and 27 of the same talk disagree (≈30 against 100).
2. **Keckler's "per transition": CV² or CV²/2?** This gives a factor-of-2 ambiguity in the implied capacitance (0.30 or 0.59 pF/mm) and so in the capacitance comparison of 2e.
3. **Flit width and number of layers.** A single link at d = 1 delivers ≥117 B per 400 MHz cycle, more than one 512-bit layer. WikiChip reports 1024 b and two links per direction; MPR reports one. The NetSpeed configuration is not in the repo.
4. **Do idle data wires hold their value, return to zero, or carry headers?** This decides whether the energy follows 2p(1−p) or p, and so how payload bits convert to transitions.
5. **Which row order does silicon use** for tensor-store row n (sys_emu or the PRM formula)? It determines whether q = 0.445 is right at all.
6. **Why does d = 8 add almost nothing over d = 6?** The candidates are edge or non-compute links of different length, less contention, fewer readers, and noise in the unmetered term.
7. **Does energy per flit-hop depend on contention** (buffer writes, arbitration)? The current design cannot tell, because link sharing rises with d.
8. **How accurate is the NoC-rail meter,** and what does the unmetered excess consist of? It is 25% of the NoC-rail difference for all d and 36–47% for d ≤ 6, so it is not a fixed regulator efficiency.
9. **The physical geometry of the links:**
   - Where do the routers sit within each shire, and is the metal between routers longer than one pitch?
   - How long are the links at the I/O, PCIe, master and memory-shire stops?
   - Does the 570 mm² include the seal ring or the frame drawn in the die plot? That changes the pitch by up to 2.6%.
10. **Routing:** is it XY, YX or adaptive? Is the aifoundry3 map identical to aifoundry2's (Chang reports missing links on his card)?
11. **Link circuit:** are the links full-swing or low-swing, on which metal layer, and with what repeater sizing? The 7 nm capacitance used here comes from the ASAP7 predictive PDK, not TSMC N7.
12. **Is the high-voltage side of each NoC crossing the SP-metered SRAM rail?** This decides where the AXI-to-NoC conversion energy lands.
13. **Per-hop latency:** 20 ns round trip (about 4 NoC cycles each way) here, against Chang's 3 cycles per direction. His clock and map differ from ours.
14. **What limits a single flow at d = 1:** the link, the target's cache slave port, or the reader's mesh stop?

---

Files: this synthesis, `scratchpad/wire-research/SYNTHESIS.md`; the conversion arithmetic, `scratchpad/wire-research/synthesis/convert.py`. Upstream work is in `lit/` (literature and `wire_calc.py`), `geometry/` and `verify_geom/` (pitch), `noc/` (NoC microarchitecture) and `critique/` (`toggles.py`, `railfit.py`, `linkload.py`, `confounds.py`, `empty_cells.py`).
