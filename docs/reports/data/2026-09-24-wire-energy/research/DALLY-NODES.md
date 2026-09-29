# Which process is Dally's ~100 fJ/b-mm for, and is a 2× gap expected? (Q63, 28 September 2026)

The owner asked on 28 September, from the heat-per-mm page's Talk tab: "For the per mm page, can you check with Bill
Dally what nanometer process he referred to, and then compare if the 2x discrepancy is expected, or come up with other
alternative explanations why there is a discrepancy." Dally cannot be asked, so this note collects what his own talks
and papers say. Four AI research agents searched 2001–2026 (talks, papers, slides, video captions); the author agent
checked every quote used here against a saved copy (PDF text, slide image or caption file). Third-party files are not
committed; each row gives its URL and page, slide or time. The arithmetic is `lit/dally_gap.py` (run it with the page's
`report.json`); the page's §7 subsection "Which process is Dally's figure for, and is a 2× gap expected?" shows the
table and the ranked explanations from the same data (`tools/ettelem/build_wire_report.py`, `LIT` and `WIRE_SCALING`).

Conventions: a random bit switches its wire half the time, each switch dissipating ½CV², so a random bit costs ¼CV²
per mm and the switched capacitance a figure implies is C = 4E/V². Energies move between voltages as V² at constant C
(full-swing CMOS). "Per bit" in a source can also mean per transition (½CV²) or a full charge per bit (CV²).

## 0. Answers

- **Which process: none, by design.** None of Dally's statements of the ~100 fJ/b-mm names a process, a voltage or how
  the bits are counted. The one the page quotes (AHA retreat 2023, slide 8; said aloud at Hot Chips the same week)
  repeats number for number the cost model of CACM 2020, and that paper says why the figure carries no process: "Logic
  and local memory energies scale linearly with technology—as the capacitance of the devices scales down while supply
  voltage is held constant. Communication energy remains roughly constant." Its arithmetic is "In 14 nm technology" and
  its local memory "in 14nm", so if one process must be named it is **14 nm (an inference from the matching numbers)**.
  At Hot Chips he said it with Horowitz's energy table on the screen ("45nm 0.9V" in Horowitz's own caption). The number
  is older than that model: 110 fJ/bit-mm at 32 nm and 0.6 V (DARPA exascale study, 2008, whose authors include Dally),
  about 100 on a slide labelled 28 nm (2010–2017; 391 per 64-bit word on its 2009 version), and 121 per random bit at
  40 nm and 0.9 V (Keckler, Dally et al., 2011).
- **What Dally says for a modern mesh.** In his NOCS 2022 keynote on networks-on-chip, for "a typical chip say five
  nanometer chip today", the slide gives the network's upper-layer wires "Energy ~50fJ/bit-mm" and he adds "going
  through the router is a fraction of this energy". His other figures for chips of their own day are 20–50 (2018–2023).
- **Is the 2× expected? Yes.** His own 5 nm NoC figure is half the rule; his group's scaling model (Villa et al., SC14,
  Table II) takes a fixed length of wire from 28 nm to 7 nm at ×0.46 (×0.60 from the nominal supply falling from 0.90 to
  0.70 V, ×0.76 the rest); of wires he says "it's only about 30% more efficient to send a 32-bit word over 10
  millimetres of wire" from 40 to 10 nm (2019) and "the wires have sort of a constant c" (2022). At this mesh's 0.485 V the rule predicts 22–29 fJ per bit·mm for a wire, his 5 nm figure 24 (if made at 0.70 V); the
  mesh rail measures 25–31 for the data and 37–53 in all. Piton (IBM 32 nm, 1.0 V) and Raw (IBM 0.15 µm, 1.8 V),
  measured with the data's switching controlled, scale to 24–26 and 24 for the data: from 0.15 µm to 7 nm a mesh hop
  switches about the same capacitance per mm (410–530 fF); what changes is the voltage.
- **Which 2×.** (a) The measurement as it stands, 37–53 against 100: most likely the one meant; expected. (b) Everything
  scaled to 0.9 V, 126–182: expected, since it scales clocking and contention as if they were wire. (c) Dally against
  himself (20–50 for chips of their day, ~200 for conventional full-swing wires in 2014–15, against 100): a factor of
  two either way inside his own figures, from what is counted (a bare 200 fF/mm wire against a 600 fF/mm repeated one)
  and how bits are counted (per random bit, per transition, or a full charge per bit).

## 1. Every statement found, in order

"Process" says whether the figure's own sentence, slide or table states it, or only the paper's or talk's setting (or
an inference). "Per random bit" converts the figure to fJ per random bit per mm at its own voltage, with the arithmetic.
Video quotes are YouTube auto-captions (their misspellings corrected in brackets); slide text was read from the PDF or,
where no PDF exists, from a video frame.

| # | Year, source | Verbatim | Where | Process | Supply | Counting; what | fJ per bit·mm (arithmetic) |
|---|---|---|---|---|---|---|---|
| 1 | 2002, Dally, HPCA 2002 panel "Computer architecture is all about interconnect" (4 Feb 2002); the same table in Stanford EE482C lecture 1 (4 Apr 2002, slide 17) and ISSCC 2005 "Low-Power Architecture" (slide 4, citing "Dally, HPCA, 2002") | "Power is a matter of distance (interconnect)": "Transfer 32b across chip (10mm)" "100pJ" (0.13um), "17pJ" (0.05um); "1300: 56: 1 in 2010"; slide 6: "Global on-chip interconnect ... Energy ∝ L2" | HPCA panel slides (Wayback: ceng.usc.edu/smart/presentations/hpca8/DallySlides.pdf) slide 5; http://cva.stanford.edu/classes/ee482s/slides/lect01_slides.pdf slide 17; http://cva.stanford.edu/people/dally/ISSCC2005.pdf slide 4 | stated: 0.13 µm; 0.05 µm the 2010 projection | none on the slides (Queue 2004, row 3: 1.2 V) | per 32-bit transfer; a global wire across the chip | 100 pJ / 32 / 10 mm = **313**; 17 pJ → 53 |
| 2 | 2003, Khailany, Dally, Rixner, Kapasi, Owens, Towles, "Exploring the VLSI Scalability of Stream Processors", HPCA 2003 | "the wire propagation energy per wire track (0.093 fJ in 0.18 micron technology)"; footnote 1: "Calculated from an assumed wire capacitance of 0.26 fF per micron including repeater capacitance [5] with a 25% 1-to-0 transition probability." | http://cva.stanford.edu/publications/2003/khailany_im_scalability.pdf p. 4, Table 1 | stated: 0.18 µm | none | ¼CV² (a 1-to-0 transition a quarter of the time: random data), wire + repeaters, 260 fF/mm | 65·V² fJ per bit·mm (211 at 1.8 V, an assumed voltage) |
| 3 | 2004, Dally, Kapasi, Khailany, Ahn, Das, "Stream Processors: Programmability with Efficiency", ACM Queue 2(1), Mar 2004 | Table 1 "Energy Per Operation (0.13µm, 1.2V)": "32-bit traverse 10mm wire 100 pJ" | http://cva.stanford.edu/publications/2004/spqueue.pdf p. 57 | stated: 0.13 µm | stated: 1.2 V | per 32-bit transfer; activity not stated | **313**: C 217 fF/mm if a full charge per bit (CV²), 869 if per random bit |
| 4 | 2007, Owens, Dally, Ho, Jayasimha, Keckler, Peh, "Research Challenges for On-Chip Interconnection Networks", IEEE Micro 27(5) | "In a 22-nm technology, a reasonably optimistic design point might integrate 256 cores on a 400mm2 die ... The chip, running at 0.7 V, could run at 7 GHz ... Optimistic wire technology projections estimate a latency using repeaters of 100 ps/mm and a power cost of 0.25 mW/Gbps/mm." "We calculate network channel power at peak throughput, assuming every single link is fully active at its peak bandwidth." "Even with lowered total activity factors of 25 percent, our network channel power is still unacceptably high." | https://www.ece.ucdavis.edu/~ocin06/owens-research-challenges-ocin-micro07.pdf p. 99 | stated: 22 nm (a design for 2015) | stated: 0.7 V | per bit at full activity (a full charge per bit; 25% as the lower case); mesh links with repeaters | **250**; C = 250 / 0.49 = 510 fF/mm; per random bit 62.5 at 0.7 V |
| 5 | 2008, Kogge et al., DARPA ExaScale Computing Study (authors include Dally and Keckler) | p. 128: "At full swing with today's technologies, these consume 110 fJ/bit/mm, and at reduced swing, 18 fJ/bit/mm"; p. 130: "At the 32 nm node, we estimate a line capacitance of 300 fF/mm. With a 0.6 V power supply, full swing signaling gives a signaling energy of 110 fJ/bit-mm"; p. 180 (§7.3): "110fJ/bit-mm, or 6.9pJ/word-mm for a 64-bit word"; p. 220: "On-chip signal lines have a capacitance of about 300fF/mm. With conventional full-swing speed-optimal repeaters, the repeater capacitance equals the line capacitance for a total of 600fF/mm. At the ITRS supply level of 0.9V, sending a bit on chip using conventional full-swing signaling requires about 0.5pJ/mm." (footnote: "The straw man of Section 7.3 assumes a less aggressive 20fJ/mm per bit.") | https://people.eecs.berkeley.edu/~yelick/papers/Exascale_final_report.pdf pp. 128, 130, 180, 220–221 (PDF pp. 147, 149, 199, 239–240) | stated: 32 nm (p. 130) | stated: 0.6 V (p. 130), 0.9 V (p. 220) | C V² per bit (300 × 0.6² = 108; 600 × 0.9² = 486); full swing, the line alone (p. 130) or with repeaters (p. 220) | **110** as stated; per random bit (¼CV²) 27 (0.6 V, line) or 122 (0.9 V, repeated) |
| 6 | 2009, Dally, SC09 keynote "The Future of GPU Computing" (18 Nov 2009) | slide 14: "Moving a word across die = 10FMAs / Moving a word off chip = 20FMAs"; "64b FPU 0.1mm2 50pJ/op 1.5GHz"; "64b 1mm Channel 25pJ/word"; "10mm 250pJ, 4cycles"; "64b Off-Chip Channel 1nJ/word"; "20mm" | https://www.nvidia.com/content/GTC/documents/SC09_Dally.pdf slide 14 | none (the 64b FPU at 50 pJ/op is the 40 nm DFMA of row 8) | none | per 64-bit word | 25 pJ / 64 / 1 mm = **391** |
| 7 | 2010, Dally, SC10 keynote "GPU Computing: To Exascale and Beyond" (Nov 2010); the same slide at ISCA 2010 (without widths), Salishan 2011 (slide 18), SC12 (slide 14), HiPEAC 2015 (slide 45, without the process label) and the January 2017 DLI Japan deck (slide 57, "28nm CMOS", https://images.nvidia.com/content/APAC/events/deep-learning-institute-jp/2017/pdf/keynote-nv-bill-dally.pdf) | "The High Cost of Data Movement / Fetching operands costs more than computing on them": "20mm", "64-bit DP 20pJ", "256-bit buses": "26 pJ", "256 pJ", "1 nJ"; "256-bit access 8 kB SRAM 50 pJ"; "Efficient off-chip link 500 pJ"; "DRAM Rd/Wr 16 nJ"; "28nm". ISCA 2010 speaker notes (slide 61): "Corner to corner (32mm) is 16FLOPs" | https://www.nvidia.com/content/PDF/sc_2010/theater/Dally_SC10.pdf slide 37; https://developer.download.nvidia.com/GTC/PDF/GTC2012/PresentationPDF/BillDally_NVIDIA_SC12.pdf slide 14; ISCA 2010 deck (Wayback: isca2010.inria.fr/media/slides/ISCA_Needle_A_0610.pptx) notes of slide 61 | the slide's label: 28 nm | none | per 256-bit transfer; the lengths from row 6 (1 mm, 10 mm) and the ISCA 2010 notes (32 mm) | 26 / 256 / 1 = 102; 256 / 256 / 10 = 100; 1000 / 256 / 32 = 122: **~100**. The same energies as row 6 with the width relabelled from 64 to 256 bits: the per-bit figure fell 4× in a year |
| 8 | 2011, Keckler, Dally, Khailany, Garland, Glasco, "GPUs and the Future of Parallel Computing", IEEE Micro 31(5) | Table 1: "Wire energy (per transition) 240 femtojoules (fJ) per bit per mm" (40 nm, "VDD (nominal) 0.9 V"), "150 fJ/bit/mm" (10 nm high frequency, 0.75 V), "115 fJ/bit/mm" (10 nm low voltage, 0.65 V); "Wire energy (256 bits, 10 mm) 310 pJ / 200 pJ / 150 pJ"; text: "10 mm away is six times greater at 310 pJ, assuming random data with a 50 percent transition probability"; "wire capacitance per mm remains approximately constant across process generations" | https://www.cs.toronto.edu/~pekhimenko/courses/csc2224-f19/docs/GPU.pdf p. 9 | stated: 40 nm; 10 nm projected for 2017 | stated: 0.9 / 0.75 / 0.65 V | per transition, and per random bit (50% transitions); a 10 mm global wire | **121** (310 pJ / 256 / 10); 78, 59 at 10 nm; ½CV² and ¼CV² of 600 fF/mm at 0.9 V are 243 and 121.5 |
| 9 | 2011, Gebhart, Johnson, Tarjan, Keckler, Dally, Lindholm, Skadron, "Energy-efficient Mechanisms for Managing Thread Context in Throughput Processors", ISCA 2011; the same parameters in MICRO 2011 and MICRO 2012 | Table 3: "Wire capacitance 300 fF/mm", "Voltage 0.9 Volts", "Wire Energy (32 bits) 1.9 pJ/mm"; text: "We model wire energy based on the methodology of [20] using the parameters listed in Table 3, resulting in energy consumption of 1.9pJ per mm for a 32-bit word." MICRO 2012: "Technology node 32 nm" | https://www.cs.utexas.edu/~skeckler/pubs/RF_ISCA_11.pdf pp. 6–7 | the setting: a 40 nm GPU (MICRO 2011: "a commercial 40 nm high-performance standard cell library"); 32 nm (MICRO 2012) | stated: 0.9 V | ¼CV² per random bit (¼ × 300 × 0.81 × 32 = 1.94 pJ); the wire alone | 1.9 pJ / 32 = **59** |
| 10 | 2014, Dally, Yale Patt 75 (Sep 2014); again in the January 2017 deck (slide 58) | slide 16 "Energy Shopping List": "Processor Technology 40 nm 10nm", "Vdd (nominal) 0.9 V 0.7 V", "Wire energy (256 bits, 10mm) 310 pJ 174 pJ", "Keckler [Micro 2011], Vogelsang [Micro 2010]"; slide 18: a plot "Energy per bit per mm (fJ)" against "Maximum Frequency (GHz)": FSI about 185 at 0.5 GHz to 300 at 1.65 GHz, "LSI (200 mV)" about 20, "LSI (400 mV)" about 50, CDI 57–123, SCI 27–60 (read off the plot) | https://hps.ece.utexas.edu/yale75/dally_slides.pdf slides 16, 18 | stated: 10 nm (projection); the plot none | stated: 0.7 V; the plot none | per 256 random bits (Keckler's convention); the plot's unstated | **68** (174 / 256 / 10) |
| 11 | 2014, Dally, talks at UBC (YouTube l1ImS3gbg08) and the HPCAC Stanford conference, Feb 2014 (insideHPC's video, YouTube _nnRNwgENss, 06:43–07:53), on the plot of row 10 | UBC, 23:17: "a long wire is still a long wire and it's still 200 femtofarads per millimeter even as you scale"; 25:03: "conventional signaling is the black line at the top here, it's called full swing interconnect, roughly 200 femtojoule per bit millimeter ... people have published things down into the 20 femtojoule per bit millimeter range" ("this chart is actually a chart out of a stanford phd thesis"); HPCAC: "the black dots at the top are the conventional using the power supply to Signal ... that tends to be 200 [femtojoules] per bit millimeter which is a figure of Merit here um your previous work um got down to the 20 to 30 [femtojoules] per bit millimeter but very slow" | https://www.youtube.com/watch?v=l1ImS3gbg08&t=1397 and &t=1503; https://www.youtube.com/watch?v=_nnRNwgENss&t=403 | none | none | per bit; full-swing repeated wires (the thesis's FSI curve) | **~200**: C V² with his 200 fF/mm at 1 V |
| 12 | 2014, Villa, Johnson, O'Connor, Bolotin, Nellans, Luitjens, Sakharnykh, Wang, Micikevicius, Scudiero, Keckler, Dally, "Scaling the Power Wall: A Path to Exascale", SC14 | p. 6: "Ho et al. demonstrated a 10x energy/bit reduction in 180nm by using low-swing differential signaling, ultimately reaching 100fJ/bit-mm at a 650mV transmitter voltage [35]. In contemporary technology, we expect that the voltage levels could be reduced further an obtain perhaps 30fJ/bit-mm. Such wires are ideal for processor level network-on-chip or long wires in DRAM chips."; p. 7, Table II "Technology scaling factors from 28nm to 7nm": "Ewire scaling factor" 1.0, 0.89, 0.75, 0.62, 0.46 (28, 20, 14, 10, 7 nm), "Nominal voltage" 0.90, 0.85, 0.75, 0.725, 0.70 V; text: "fixed-length wire energy (Ewire) scaling at between 0.75× and 0.9× per generation" | https://research.nvidia.com/sites/default/files/pubs/2014-11_Scaling-the-Power//villa.sc2014.pdf pp. 6–7 | stated per node | stated per node | a fixed length of wire; low swing | 100 (180 nm, low swing), "perhaps 30" |
| 13 | 2015, Das, Aamodt, Dally, "SLIP: Reducing Wire Energy in the Memory Hierarchy", ISCA 2015 | Table 1: "Technology node 45 nm", "Wire energy per transition 0.16 pJ/bit/mm", "Wire delay 0.3 ns/mm"; text: "we also simulated SLIP on a 22nm technology node using the same parameters as Table 1" | https://people.ece.ubc.ca/aamodt/publications/papers/das.isca2015.pdf Table 1 | stated: 45 nm (and 22 nm with the same parameters) | none | per transition | cache wires | 160 per transition, **80** per random bit |
| 14 | 2015, Dally, HiPEAC 2015 keynote "Challenges for Future Computing Systems" (Jan 2015) | slide 51 "Circuits: Ground Referenced Signaling": "Goal: reduce Energy/bit 200fJ/bit-mm → 20fJ/bit-mm"; "On-chip Signaling / Testsite on GM2xx GPU / <45fJ/bit-mm" | https://www.cs.colostate.edu/~cs575dl/Sp2015/Lectures/Dally2015.pdf slide 51 (also slide 66, "Circuits: 200 -> 20") | inferred: 28 nm (a GM2xx, Maxwell, test site) | none | per bit; conventional signaling as the baseline | **200** (baseline); <45 measured on the test site |
| 15 | 2015, Dally, interview at HiPEAC 2015 (YouTube LHrVlSxq6Ks, 01:13; auto-captions) | "we can improve signaling efficiency from 250 [femto]joule[s] per bit millimeter to about 20 [to] 50 [femto]joules per bit millimeter" | https://www.youtube.com/watch?v=LHrVlSxq6Ks&t=73 | none | none | per bit | conventional signaling, and the low-swing target | 250 → 20–50 |
| 16 | 2016, Wilson, …, Dally, ISSCC 2016 | title: "A 6.5-to-23.3fJ/b/mm Balanced Charge-Recycling Bus in 16nm FinFET CMOS at 1.7-to-2.6Gb/s/wire with Clock Forwarding and Low-Crosstalk Contraflow Wiring" | https://research.nvidia.com/publication/2016-02_65-233fjbmm-balanced-charge-recycling-bus-16nm-finfet-cmos-17-26gbswire-clock | stated: 16 nm | behind the paywall | per bit; charge recycling (half swing) | 6.5–23.3 |
| 17 | 2016, Mohammadi, Aamodt, Dally, "CG-OoO: Energy-Efficient Coarse-Grain Out-of-Order Execution", arXiv 1606.01607 | p. 7: "The energy per access used for wires is 0.08 pJ/b-mm at the 22nm technology node [45]. The simulator assumes all wires have 0.5 activity factor; so, every time the simulator drives a wire, its energy consumption is incremented by half of its per-access energy." | https://arxiv.org/pdf/1606.01607 p. 7 | stated: 22 nm | none | per access, applied at activity 0.5 | core wires | 80 per access, **40** per random bit |
| 18 | 2018, Dally, Gray, Poulton, Khailany, Wilson, Dennison, "Hardware-Enabled Artificial Intelligence", VLSI Symposium 2018 | p. 2: "Energy consumption in a CMOS-driven wire is ~ CV2, where C is the capacitance per unit length of a wire (about 200fF/mm and independent of scaling) and V is the supply voltage. In present day chips, energy efficiency for on-chip wires is between 20-40 fJ/bit-mm, and it will not improve, since supply voltages are scaling very slowly." "At 40fJ/bit-mm, this requires 26W." "Since the V2 term in the CMOS-driven wire energy consumption is Vsupply × Vsignal, we can get some benefit from low-swing signaling. In practice this may reduce energy/bit by ½" | https://research.nvidia.com/sites/default/files/pubs/2018-06_Hardware-Enabled-Artificial-Intelligence/VLSI2018_HardwareAI.pdf.PDF p. 2 | setting: 16 nm ("In 16nm logic, operating at 0.6V ..."); the sentence says "present day chips" | none for the wire | "~ CV2"; a bare CMOS wire, 200 fF/mm | **20–40**; ¼CV² with 200 fF/mm is 20–40 at 0.63–0.89 V |
| 19 | 2018, Turner, ..., Dally, Gray, "Ground-Referenced Signaling for Intra-Chip and Short-Reach Chip-to-Chip Interconnects", CICC 2018 | "An on-chip communication link was implemented in a 28nm CMOS process using low-swing GRS between re-timing stages (hops)"; "a 16Gb/s 170fJ/b/mm on-chip link"; Fig. 14(c): TX 75, RX 30, CLK 65, "* On-Chip Numbers in fJ/b/mm"; channel "R=130Ω/mm, C=305fF/mm" | https://research.nvidia.com/sites/default/files/pubs/2018-04_Ground-Referenced-Signaling-for/CICC2018_GRS_18-5.pdf pp. 1, 3, 6–7 | stated: 28 nm | not stated for the on-chip link | per bit | a low-swing serial link, transmitter, receiver and clocking included, retimed every 1.5 mm | 170 |
| 20 | 2019, Dally, MICRO 2019 keynote "The Future of Computing: Domain-Specific Accelerators" (15 Oct 2019) | slide 19 "Scaling of Communication": bars "DFMA 40nm", "DFMA 10nm", "Wire 40nm" (310 pJ), "Wire 10nm" (about 217 pJ, read off the bar); "Keckler et al. Micro 2011." | https://www.microarch.org/micro52/media/dally_keynote.pdf slide 19; spoken at Rice (2019, YouTube fnd05AeeFN4, 21:02): from 40 to 10 nm "it's four times as efficient to do the double precision floating multiplied accumulate, it's only about 30% more efficient to send a 32-bit word over 10 millimetres of wire in that same technology" | stated: 40 and 10 nm | none on the slide (the 2011 table: 0.9 V) | Keckler's 256 random bits over 10 mm | 121 (40 nm); about 85 (10 nm, read off) |
| 21 | 2020, Dally, Turakhia, Han, "Domain-Specific Hardware Accelerators", CACM 63(7) | p. 56, a cost model: "Arithmetic: In 14 nm technology, arithmetic costs range from 10fJ and 4 µm2 for an 8-bit add operation to 5pJ and 3600 µm2 for a double-precision floating-point multiply." "Local memory: Accessing a small (8KByte) local memory in 14nm costs 50fJ/bit ... This communication costs 100fJ/bit-mm". "Local Communication: Communication between blocks on chip has an energy cost that increases linearly with distance at a rate of 100fJ/bit-mm." "Logic and local memory energies scale linearly with technology—as the capacitance of the devices scales down while supply voltage is held constant. Communication energy remains roughly constant." (footnote b: "For recent technology nodes, scaling linear dimensions by 0.7× has given only a 0.8–0.9× reduction in logic energy") | https://www.doc.ic.ac.uk/~wl/teachlocal/arch/papers/cacm20dsa.pdf p. 56 | the model's: 14 nm (its arithmetic and memory items) | none | per bit; "communication between blocks on chip" | **100** |
| 22 | 2021–22, Dally, "Deep Learning Hardware" talks: IEEE Santa Clara Valley (Nov 2021), Orange County ACM (Mar 2022) | slides "Communication Circuits / 4x Energy Saving – 5-10fJ/bit-mm" and "Process / Numbers above are for 16nm (unless otherwise stated) / Denard scaling is dead, but capacitance does scale – Slower than linear / Expect a factor of 2-2.5x"; spoken (2022, 38:42–40:20): "getting down to on the order of five to ten [femto]joules per bit from around 40 or 50 [femtojoules] per bit today ... almost all the numbers i've given you up until now ... have been for 16 nanometers ... we still have to keep nominal one volt supplies almost everywhere"; spoken (2021, 40:21–40:49): "you could expect going down to five nanometers another factor of two to two and a half in energy" | https://www.youtube.com/watch?v=AGcv_PRKrPQ&t=2322 (2022); https://www.youtube.com/watch?v=2gsnGPaV4HY&t=2395 (2021) | the talk's: 16 nm | spoken: "nominal one volt supplies almost everywhere" | per bit (per mm on the slide); a CMOS wire, and charge recycling | **40–50**, 5–10 with charge recycling |
| 23 | 2022, Dally, Stanford HAI spring conference keynote (Apr 2022) | slide "Communication Circuits / 4x Energy Saving – 5-10fJ/bit-mm" (citing Wilson et al., ISSCC 2016) | https://www.youtube.com/watch?v=VRiTGeJpqrs&t=6582 | the cited paper's: 16 nm | none | charge recycling | 5–10 |
| 24 | 2022, Dally, "On the model of computation: point", CACM 65(9) | "A 32-bit add operation takes only 20fJ and 150ps. Moving the two 32-bit words to feed this operation 1mm takes 1.9pJ and 400ps. Moving the 64 bits 40mm from corner to corner on a 400mm2 chip takes 77pJ and 16ns." "Accessing a 256MB memory (approximately 100mm2) ... costs 58pJ ... of which 57.4pJ ... are due to communication—15mm each way, 30mm total." | https://doi.org/10.1145/3548783 | none ("today") | none | per bit | **30** (1.9 pJ / 64 / 1 mm = 29.7; 77 / 64 / 40 = 30.1; 57.4 / 64 / 30 = 29.9). The 1.9 pJ per mm is row 9's figure for one 32-bit word, here for two (an observation) |
| 25 | 2022, Dally, keynote at NOCS 2022 (Oct 2022) | slide at 14:10: "Wire pitch today / ~40nm on dense layers / ~80nm on upper layers / ~20 layers ... Signal velocity ~1mm/ns / Repeaters every 20µm / Energy ~50fJ/bit-mm"; spoken (14:04–15:52): "in a typical chip say five nanometer chip today ... we tend to use the upper layers for the [NoC] ... the energy is 50 femtojoules per bit millimeter that's a lot ... going through the router is a fraction of this energy, a fraction of the energy of crossing a tile"; slide at 33:35: "Circuits Matter / 10fJ/bit-mm, not 50" | https://www.youtube.com/watch?v=Nk3oQm9NxcY&t=848 | spoken: 5 nm | none (1 V and 0.5 V only as spoken examples later) | per bit; NoC wires on the upper layers, router excluded | **50** |
| 26 | 2023, Dally, Hot Chips 2023 keynote "Hardware for Deep Learning" (29 Aug 2023) | spoken (41:17–41:31), while slide 51 "Cost of Operations" was on the screen (its energies "from Mark Horowitz ... ISSCC 2014", whose caption reads "45nm 0.9V"; its areas "TSMC 45nm"): "that big memory is made up of a bunch of 8K byte memories. And everything else is communication energy, which is about, you know, 100 ... 100 femtojoules per bit millimeter"; earlier (19:38–19:42): "We're still doing most of our communication on chip doing full swing signaling" | https://www.youtube.com/watch?v=rsxCZAE8QNA&t=2477; slides https://hc2023.hotchips.org/assets/program/conference/day2/Keynote%202/Keynote-NVIDIA_Hardware-for-Deep-Learning.pdf | none (CACM 2020's model; a 45 nm table on screen) | none | per bit | **100** |
| 27 | 2023, Dally, Stanford AHA retreat keynote "Energy Efficiency and AI Hardware" (31 Aug 2023) | slide 7: "V: Reduce voltage - to the point it starts getting too slow • ~0.5V today • 2x vs 0.7v, 4x vs 1.0v"; slide 8: "E = ½CV² / C: Three components • Communication (~100fJ/b-mm on-chip) • Memory (~50fJ/b for small RAM) • Operations (~1fJ/b for add)"; slide 13: "An add is worth 10um of movement" (citing CACM 2022); slide 27: "Cost of an add (1fJ/bit) = Cost of going 10um."; slide 31: "48mm round trip on GPU die • 4.8pJ/b @ 100fJ/b-mm"; slide 45: "V² – Reduce V until it gets too slow (~0.5V)", "C – Communication (100fJ/b-mm), Memory (50fJ/b), Operations (Add - 1fJ/b)" | https://aha.stanford.edu/sites/g/files/sbiybj20066/files/media/file/aha-retreat-2023_dally_keynote_en_eff_ai_hw_0.pdf slides 7, 8, 13, 27, 31, 45 | none (slide 8's three numbers are CACM 2020's 14 nm model) | none (slide 7: "~0.5V today" as a target) | per bit | **100** (slide 13 implies ~30, slide 27 100) |
| 28 | 2023, Zhu, Rucker, Wang, Dally, "SatIn: Hardware for Boolean Satisfiability Inference", arXiv 2303.02588 | p. 10: "Each router takes 22.861 µm2 ... and consumes almost no power. The majority of network energy consumption comes from the interconnecting wires. With 32 nm technology, it takes about 0.2 pJ per millimeter to send one bit in a densely packed bus on M7, treating the layers above and below as ground planes (the conservative case) but ignoring fringing capacitance. The overall estimation of wire power is 1.85 W on a 16 by 16 network under the activity factor of 34% given by the simulation."; p. 8: "Synopsys 32 nm educational standard cell library ... nominal voltage of 1.05 V" | https://arxiv.org/pdf/2303.02588 pp. 8, 10 | stated: 32 nm | the design's nominal: 1.05 V | per bit sent, with an activity factor applied after; the wire alone (router "almost no power") | **200**: C V² with 181 fF/mm at 1.05 V; ¼ of it per random bit |
| 29 | 2023, Dally, Hot Interconnects 2023 keynote "Accelerator Clusters" (Aug 2023) | slide at 21:50, inside "GPU or Switch": "Logic ↔ Logic" "100Tb/s" "0.1pJ/b" "2mm" | https://www.youtube.com/watch?v=napEsaJ5hMU&t=1310 | none | none | per bit over a 2 mm on-chip link | **50** (0.1 pJ / 2 mm) |

Two other meshes measured on silicon with the data's switching controlled, used on the page beside Dally's figures:

| Source | Verbatim | Where | Process, supply | Per bit per mm (arithmetic) |
|---|---|---|---|---|
| McKeown et al., "Power and Energy Characterization of an Open Source 25-Core Manycore Processor" (Piton), HPCA 2018 | Fig. 12: "NSW (~3.58 pJ/hop)", "HSW (~11.16 pJ/hop)", "FSW (~16.68 pJ/hop)"; "Flit size is 64-bits"; "Half switching (HSW) flips half of the bits between consecutive payload flits"; "The center-to-center distance between tiles is 1.14452 mm in the X direction and 1.053 mm in the Y direction"; "The NoC routers consume a relatively small amount of energy (NSW case) in comparison to charging and discharging the NoC data lines"; baseline "when sending to tile0" | https://parallel.princeton.edu/papers/piton-power-hpca18.pdf pp. 7–8 | IBM 32 nm SOI, "Core Voltage (VDD) 1.00V" | data: (11.16 − 3.58) / 64 / 1.053–1.145 mm = 103–112 fJ (C 414–450 fF/mm), 24–26 at 0.485 V; none: 3.58 / 64 / same = 49–53, 11–12 at 0.485 V |
| Kim, Taylor, Miller, Wentzlaff, "Energy Characterization of a Tiled Architecture Processor with On-Chip Networks" (Raw), ISLPED 2003 | "an amortized cost of 85 pJ per 32-bit maximal-toggle word that is routed"; "the graphs do not include clock energy"; "All transmitted sequences maximize toggle rate"; "the inter-tile 4 mm wires"; "1.8V IBM SA-27E 0.15um" | https://groups.csail.mit.edu/cag/raw/documents/islped_raw_2003.pdf p. 3 | IBM 0.15 µm, 1.8 V | 85 pJ / 32 / 4 mm = 664 per full toggle; a random bit half: 332 (C 410 fF/mm), 24 at 0.485 V |

## 2. Which process: the reasoning

- **The figure the page quotes.** AHA 2023 slide 8 gives three numbers, and all three are CACM 2020's cost model:
  "~100fJ/b-mm" is its communication; "~50fJ/b for small RAM" is its "small (8KByte) local memory in 14nm costs
  50fJ/bit"; "~1fJ/b for add" is its "10fJ ... for an 8-bit add operation" "In 14 nm technology". At Hot Chips the same
  week he recited that model's memory ("a bunch of 8K byte memories ... everything else is communication energy ...
  100 femtojoules per bit millimeter"). So the figure is the 14 nm model's: an inference from matching numbers, since
  the communication sentence itself names no process. The same talks show other processes on other slides: "all 28nm"
  (AHA slide 11, Hot Chips slide 50) and Horowitz's 45 nm, 0.9 V energies (AHA slide 12; Hot Chips slide 51, on the
  screen while he said the 100).
- **Its ancestors.** The number predates the 14 nm model: 110 fJ/bit-mm at 32 nm and 0.6 V (2008, C V² per bit); about
  100 on a slide labelled 28 nm (2010–2017); 121 per random bit at 40 nm and 0.9 V (2011). It has not moved with the
  process, which is what Dally's own statements about wires predict: capacitance per mm "remains approximately constant
  across process generations" (2011), "about 200fF/mm and independent of scaling" (2018), "the wires have sort of a
  constant c" (2022, spoken).
- **Chips of their own day.** When he gives a figure for a current chip, it is lower: 20–40 "in present day chips"
  (2018, a 16 nm paper), "around 40 or 50" (2021–22 talks, "numbers ... for 16nm", "nominal one volt supplies"), 30
  ("today", CACM 2022), ~50 for the upper-layer wires of a network-on-chip on "a typical chip say five nanometer chip
  today" (NOCS 2022) and 50 for a 2 mm on-chip link (Hot Interconnects 2023).
- **The voltage.** None of the ~100 statements gives one. The figures in its lineage that do are at 0.6–0.9 V, and
  Dally's group's own model gives 0.90 V as the nominal supply of 28 nm and 0.75 V of 14 nm (SC14, Table II). Read at
  the "~0.5V" the 2023 talk recommends (slide 7), the 100 would need 800–1,600 fF/mm, 4–8 times the 200 fF/mm he gives a
  wire; read at 0.8–1.0 V it needs 200–600 fF/mm, a bare or a repeated wire. So it is a nominal-voltage figure.

## 3. What each figure predicts for this mesh at 0.485 V

From `lit/dally_gap.py` on the page's `report.json` (all fJ per random bit per mm; the measured values are the
three-card check's, mesh rail, free links to loaded mesh).

| Figure | Moved to 0.485 V by | Predicts | Switched C it implies |
|---|---|---|---|
| 2002–04, 0.13 µm, 1.2 V, 313 (activity not stated) | V² from 1.2 V | 51 | 869 (217 if a full charge per bit) |
| Owens et al. 2007, 22 nm, 0.7 V, 250 at full activity | ¼ of a full charge, V² from 0.7 V | 30 | 510 (as a full charge) |
| Keckler et al. 2011, 40 nm, 0.9 V, 121 | V² from its 0.9 V | 35 | 598 fF/mm |
| the same table, 10 nm, 0.75 / 0.65 V, 78 / 59 | V² from its voltage | 33 / 33 | 555 / 555 |
| Gebhart et al. 2011, 300 fF/mm, 0.9 V, 59 | ¼CV² with its own C | 18 | 300 (stated) |
| Yale Patt 75, 10 nm, 0.7 V, 68 | V² from 0.7 V | 33 | 555 |
| DARPA 2008, 32 nm, 300 fF/mm (600 with repeaters) | ¼CV² with its own C | 18–35 | 300–600 (stated) |
| VLSI 2018, 200 fF/mm | ¼CV² with its own C | 12 | 200 (stated) |
| Talks 2021–22, 40–50 at 16 nm and "nominal one volt" | V² from 1.0 V | 9–12 | 160–200 |
| SatIn 2023, 32 nm, 1.05 V, 200 per bit sent | ¼ of a full charge, V² from 1.05 V | 11 | 181 (as a full charge) |
| Das et al. 2015, 45 nm, 160 per transition; Mohammadi et al. 2016, 22 nm, 80 per access | no voltage given | — | — |
| ~100 (SC10/SC12 28 nm; CACM 2020 14 nm; 2023) | V² from 0.9 / 0.7 / 0.5 V | 29 / 48 / 94 | 494 / 816 / 1600 |
| ~100 at 28 or 14 nm, scaled to 7 nm by SC14, then V² from 0.70 V | SC14 Table II | 22 / 29 | — |
| NOCS 2022, 5 nm NoC, ~50 | V² from 0.9 / 0.7 / 0.5 V | 15 / 24 / 47 | 247 / 408 / 800 |
| HiPEAC 2015 baseline, 200 | V² from 0.9 / 0.7 / 0.5 V | 58 / 96 / 188 | 988 / 1633 / 3200 |
| CACM 2022, 30 | V² from 0.9 / 0.7 / 0.5 V | 9 / 14 / 28 | 148 / 245 / 480 |
| **Measured: data-dependent** | | **25–31** | **420–530** |
| **Measured: everything** | | **37–53** | **624–901** |
| Piton (HPCA 2018), data switching like random, and none | V² from 1.0 V | 24–26 and 11–12 | 414–450 |
| Raw (ISLPED 2003), half a full toggle | V² from 1.8 V | 24 | 410 |

The voltage at which 100 fJ is a random bit on a wire of 200 fF/mm (Dally 2018) to 598 fF/mm (the 2011 table): 0.82–1.41
V; per transition (½CV²): 0.58–1.00 V; as a full charge per bit (CV², the 2008 study's count): 0.41–0.71 V. At 0.5 V
the 100 needs 800 fF/mm per transition or 1,600 per random bit, 4–8 times his 200.

## 4. The three readings of "the 2×"

(a) **The measurement as it stands**: 37–53 fJ per bit·mm on the mesh rail (47–79 on board power) against 100: 0.37–0.53
of it on the mesh rail. The lede and the §7 text put these side by side, so this is most likely the one meant. It is
expected (section 0): Dally's own 5 nm NoC figure is 50, his group's scaling takes 28 nm to 7 nm at ×0.46, and this
mesh runs at 0.485 V, below 7 nm's nominal 0.70 V.

(b) **Everything scaled to 0.9 V**: 126–182, 1.3–1.8 times 100. Expected: scaling the data-independent part (clock,
flops, headers, the request) and contention as CV² treats them as wire; the data-dependent part alone at 0.9 V is
85–107, about 100 and 0.7–0.9 of Keckler's 121.

(c) **Dally against himself**: 20–40 (VLSI 2018), 40–50 (the 2021–22 talks), 30 (CACM 2022), 50 (NOCS 2022, Hot
Interconnects 2023), and ~200 for conventional full-swing wires (the 2014 talks, "roughly 200 femtojoule per bit
millimeter"; HiPEAC 2015, "200fJ/bit-mm → 20fJ/bit-mm"), against 100. His group's models of 2015–16 used 80 per random
bit at 45 nm (Das et al.: 0.16 pJ/bit/mm per transition) and 40 at 22 nm (Mohammadi et al.: 0.08 pJ/b-mm per access at
activity 0.5), and the same year as Keckler's 121 his group's register-file papers used 59 (300 fF/mm, no repeaters,
0.9 V). VLSI 2018's 20–40 is ¼CV² of his bare 200 fF/mm
wire at 0.63–0.89 V; the 100 descends from tables of a repeated wire of 600 fF/mm (the 2008 study: 300 of line, "the
repeater capacitance equals the line capacitance"; Keckler's 240 per transition and 121 per random bit at 0.9 V are
½CV² and ¼CV² of exactly that); and the same 600 fF/mm at 0.9 V is "about 0.5pJ/mm" per bit in 2008 (CV²). The spread
is what is counted (a bare wire or a repeated one) and how (per random bit, per transition, per full charge); an
inference, since no statement says which.

## 5. Alternative explanations, ranked, with sizes and tests

"Explains it" means the explanation moves this mesh below a nominal-voltage wire figure; "against it" means it moves the
mesh above one. Sizes are from the page's data (report.json) or the sources above; `lit/dally_gap.py` prints them.

| # | Explanation | Size | Effect | How to test |
|---|---|---|---|---|
| 1 | Supply voltage (CV²) | ÷2.1–3.4 from the nominal 0.70–0.90 V SC14 gives 7–28 nm to 0.485 V; ÷1.5–6.1 from the 0.6–1.2 V of his figures that have one; the ~50 and ~100 give none | explains it | Step the NoC rail (firmware allows 485–600 mV for 300–500 MHz; `thermal_pwr_mgmt.c`, SYNTHESIS §1b): a full-swing wire at 0.6 V costs ×1.53. A setting change on a shared card: owner's approval first |
| 2 | How the bits are counted | up to ÷4: one 600 fF/mm wire at 0.9 V is "about 0.5pJ/mm" per bit (CV², 2008), 240 per transition and 121 per random bit (2011); here a random bit costs ×1.2 a flit-to-flit difference because ones cost (a 26.4, b 34.8 fJ/mm) | explains it if the 100 counts more than a random bit | Measured here (the page's §5); for the 100, no source says |
| 3 | What a hop counts (routers, flops, clock, headers, the request) | everything ×1.5–1.7 the data part; the data part ×1.1–2.7 a plain 7 nm wire's 12–24 fJ; the data-independent part is 33–41% of a hop (Piton: 32%; Dally, NOCS 2022: the router "a fraction" of a tile's wire energy) | against it | Hops of another length (a memory-shire column, 1.74–1.80 mm, against 3.72 mm tiles); the router netlist and floorplan |
| 4 | Contention | +49–61% per mm, loaded against free links over 1–4 hops (mesh rail, by card) | against it, on a loaded mesh | Measured (§6 of the page) |
| 5 | The meter | board power ×1.3–1.5 the mesh rail (regulator loss); board coefficients move 4–9% with the leakage correction | against it, on board power | Calibrate the mesh-rail reading against a known load |
| 6 | Ones carried, and the encoding | the per-one term is 57% of a random bit's data cost; all ones +8–12% per hop over random | against it | Measured (§5); a complemented encoding |
| 7 | Wire kind, metal layer, swing | top metal ~0.6 of the middle layers' capacitance (ASAP7 0.093–0.104 against 0.156–0.187 fF/µm), and Dally puts NoCs on the upper layers (NOCS 2022); low swing ½ (VLSI 2018) to ¾ (charge recycling, 4×) less | unknown here | The link circuit and metal stack (Esperanto, NetSpeed); on the cards, the voltage step (full swing ∝ V², a fixed swing ∝ V) |
| 8 | Routed length against the 3.72 mm pitch | the metal can only be longer, so per mm of wire the cost is lower; size unknown | explains it, per mm of wire | The floorplan; hops of another length |
| 9 | The process node apart from its voltage | ×0.76 from 28 to 7 nm (SC14 less its voltage), ×0.93 from 40 to 10 nm (the 2011–14 tables); for wires, "only about 30% more efficient" from 40 to 10 nm, voltage included (2019), and "sort of a constant c" (2022); for logic he expects "another factor of two to two and a half in energy" from 16 to 5 nm (2021) | explains a little | Documents |
| 10 | Temperature | switching energy does not depend on it; the mesh rail carries no leakage correction (about 2%) | small | The same configurations on a cool and a warm die |

Also weighed and set aside: the NoC clock (400 MHz) changes no energy per switch, only the data-independent part's
per-second share (the page's §10 bounds it); flit headers and parity add a few per cent per payload bit; activity is
0.5 for the random data used (P = ½, every line unique in the second and third runs).

## 6. Corrections to the earlier notes and the page

- **SYNTHESIS.md §1d ("None stated")** stands for the ~100 statements, but the node context is richer: CACM 2020 gives the
  100 twice, in a cost model whose arithmetic is "In 14 nm technology" and local memory "in 14nm" (not a single
  paragraph); the 2023 figure matches that model's three numbers; at Hot Chips 2023 it was spoken while Horowitz's
  45 nm, 0.9 V table was on screen.
- **SYNTHESIS.md §1e, Keckler's "per transition"**: CV² or ½CV²? The 2008 exascale study (Dally and Keckler among the
  authors) gives a repeated wire of 600 fF/mm, and ½CV² of it at 0.9 V is 243, the 240 of the 2011 table; ¼CV² is 121.5,
  its 121 per random bit. So the 2011 table counts ½CV² per transition of a 600 fF/mm wire (an inference from exact
  agreement), resolving SYNTHESIS open question 2.
- **SYNTHESIS.md §1e, SC12** ("No voltage or activity stated", "82–147 fJ/b·mm" from the drawn lengths): the same slide is
  in the SC10 keynote (Nov 2010), Salishan 2011 and the Jan 2017 deck, labelled "28nm" (HiPEAC 2015's copy has no
  label). Its lengths are sourced, not only drawn: the 2009 version labels the bars "64b 1mm Channel 25pJ/word" and
  "10mm 250pJ" (row 6) and the 2010 speaker notes call the longest "Corner to corner (32mm)" (row 7), which gives
  100–122 fJ per bit·mm; the 2009 energies were per 64-bit word (391).
- **SYNTHESIS.md §1e, VLSI 2018**: the quote is right; the sentence before it gives the physics ("Energy consumption in
  a CMOS-driven wire is ~ CV2, where C is the capacitance per unit length of a wire (about 200fF/mm and independent of
  scaling) and V is the supply voltage").
- **SYNTHESIS.md §4 open question 1** ("No node ... stated in AHA 2023, CACM 2020 or SC12"): SC12's slide is labelled
  28 nm; CACM 2020's model is 14 nm; AHA 2023 states none but repeats the 14 nm model.
- **The page, §1**: "CACM 2020 states it in a paragraph about 14 nm on-chip memory" is now "states it twice, in a cost
  model whose arithmetic and local memory are 'in 14 nm'"; the Hot Chips spoken statement, the 2008 study, the 28 nm
  slide and the NOCS 2022 figure are added. The lede now says the gap of about two is expected and mostly voltage.
- **SYNTHESIS.md §1d, AHA slides 13 and 27** (≈30 and 100): slide 13's "10um" comes from CACM 2022 (a 20 fJ 32-bit add
  against 64 operand bits moved, 30 fJ/b·mm), slide 27's from a 1 fJ/bit add at 100 fJ/b·mm. CACM 2022's 1.9 pJ per mm
  for two 32-bit words is the 1.9 pJ his group's 2011 papers give for one (row 9), so the 30 may be that model with the
  width doubled (an observation, not a source's statement).
- **docs/findings/20-heat-per-mm.md**: its answer gave contention as 45–55% (mesh rail) and 65–75% (board), from an
  earlier reduction; the page computes 49–61% and 70–80% like for like over one to four hops, per card. Corrected.

## 7. Searched, not found

- **A process or voltage for the ~100 in Dally's own words.** Not in CACM 2020, the AHA 2023 slides, the Hot Chips 2023
  slides or its spoken passage, the SC10/SC12/2017 slides, or any transcript found (GTC 2024–2026, Hot Chips 2023,
  NOCS 2022, HAI 2022, the 2021–22 talks, Hot Interconnects 2023).
- **The bus lengths of the SC10 slide written on that slide**: not there; they come from its 2009 version (row 6) and
  the 2010 speaker notes (row 7).
- **2001–2013** (agent search through Wayback listings of CVA, NVIDIA, LANL, USC, UC Davis and the ISCA 2010 site; the
  web-search quota ran out, so talks posted elsewhere may be missing): Dally & Towles, DAC 2001 (no number; low swing
  "reduce[s] power by an order of magnitude compared to 1.0V full swing signaling in our 0.1µm process"); the Dally &
  Towles (2004) and Dally & Poulton (1998) books (the online copies are access-restricted; EE273 lecture 8 of 2001 gives
  only "Aluminum (0.35µm technology) ... C = 160fF/mm"); IITC 1999; ARVLSI 1999 and DAC 2000; IEEE Computer 2008
  "Efficient Embedded Computing", Balfour's CAL 2008/2009 papers and 2010 thesis (no per-mm energy); the DAC 2009
  keynote slides; Nickolls & Dally, IEEE Micro 2010 (closed); the IPDPS 2011 keynote slides (the Salishan 2011 deck was
  used instead); Keckler's MICRO 2011 keynote slides; Dally GTC keynotes 2010–2013 (none in the archived lists); the
  ORNL 2008, Salishan 2005 and OCIN 2006 talks (no per-mm figure); the Merrimac SC03 paper.
- **Measured NoC energies** (agent 4): the full texts of Intel's 22 nm (Chen et al., JSSC 2015), Teraflops and SCC
  router papers (abstracts only); an on-chip NoC energy per bit per hop in NVIDIA's RC18/Simba papers (JSSC 2020, MICRO
  2019, CACM 2021: none given); Celerity (link width only); a router/link split for FlooNoC; any silicon-measured NoC
  energy at 7 or 5 nm (the ETH 7 nm figure is post-layout); TSMC N7/N5 capacitance per mm and IRDS interconnect tables.
- **The ET-SoC-1's own link circuit**: its width, full or low swing, metal layers, the router's place in a tile and the
  routed link length are in none of the Hot Chips 33 slides, the IEEE Micro 2022 paper, the datasheet, the programmer's
  reference manual, WikiChip, the NetSpeed release of 2018 or the dev-card document.
- **2014–2019** (agent 2; the web-search budget was spent, so it searched through OpenAlex, the NVIDIA research site, the
  Wayback CDX API and YouTube captions): the NIPS 2015 tutorial (120 slides: only per-word energies, 640/50/5 pJ, and the
  45 nm table); no Dally deck in the GTC 2014–2019 archives (the SC16 booth talk is a video only); no Dally talk at Hot
  Chips 2014–2019; no ISSCC plenary or ISC 2015 keynote; captions of SysML 2018, ScaledML 2019, GTC Israel 2018, GTC DC
  2016, Michigan 2018, Berkeley 2016, Caltech 2019 (per-word figures only; the DARPA ERI 2018 talk: "these are from 45
  nanometer numbers ... roughly divided by four to get to current sort of twelve FinFET numbers", about logic and
  memory); no per-mm on-chip figure in Chatterjee HPCA 2017, Poulton JSSC 2019, Wilson ISSCC 2018, Darwin ASPLOS 2018,
  EIE, SCNN, RC18/Simba (JSSC 2020, MICRO 2019, VLSI 2019, Hot Chips 2019: "At 0.72 V, each link of the NoC achieves
  70-Gb/s bandwidth", "10 ns/Hop", no energy per hop), MAGNet, or the ASCAC 2014 report. Fine-Grained DRAM (MICRO 2017)
  gives "2.24 pJ/bit" over roughly 9.9 mm of DRAM-die and base-die path, TSVs and precharged lines included (about 226
  fJ/bit·mm, derived). Not accessible: the full text of Wilson et al., ISSCC 2016 (so its full-swing baseline, voltage and
  activity are unverified), Das TACO 2015, the Dally–Balfour ICS 2014 retrospective, Han–Dally DAC 2018.
- **The GRS test site's figures disagree**: "<45fJ/bit-mm" (HiPEAC 2015, slide 51) against 170 fJ/b/mm with transmitter,
  receiver and clock (CICC 2018, row 19); the 45 probably leaves out clocking and the receiver, or is a target (an
  inference).
- **2020–2026** (agent 3; its web-search budget ran out early, so phrase searches for "fJ/b-mm", "0.1 pJ/bit/mm",
  "per bit per millimeter" and "10 microns" were not run): decks with no per-mm figure: Hot Chips 2023 (58 slides),
  CRA 2024 (63), DARPA ERI 2023 (34; op energies "from 45nm process"), GTC 2023 S52291 (69; package links only), the AHA
  2022 chiplet panel (5); video frames and captions with no per-mm figure: Berkeley Dec 2022 (of the 45 nm table: "45
  nanometer numbers but proportionally they're still about right"), UW Nov 2023, Cornell Dec 2023, Georgia Tech Apr 2024,
  Berkeley 2025 (two), NUS 2026, GTC 2024–2026 (a 200 fJ/bit in GTC 2025 is an interposer link), GTC China 2020, DAC
  2021, the conversations with LeCun, Dean and Fei-Fei Li, podcasts; not retrievable: GTC 2022 S42013 (login), GTC 2021
  S33090, MLSys 2021, IEEE Micro 2021 "Evolution of the GPU" (paywalled), and **IEDM 2024, Hu ... Dally, "Co-Optimization
  of GPU AI Chip ..."** (paywalled; its Fig. 7, "Energy cost for various compute functions across chip", from a 5 nm
  design, is the strongest unread lead); news (IEEE Spectrum, The Next Platform, HPCwire, SemiEngineering, EE Times, NVIDIA
  blogs, WIRED, TechCrunch, ZDNet): no on-chip per-mm figure from Dally.
- **Voltages spoken near wire figures are examples**, not conditions: "say ground is zero volts and vdds is one volt"
  (HAI 2022), 1 V and 0.5 V (NOCS 2022, 36:01), "0.8 V ... signal 0.4 V" (Hot Chips 2023 Q&A, 1:03:40), "around 0.5 is a
  pretty good voltage" (Hot Chips 2023 Q&A, 1:04:24, about logic). The one voltage tied to a process is "nominal one
  volt supplies almost everywhere" for his 16 nm numbers (2022).

## Files

- This note; `lit/dally_gap.py` (the arithmetic, from `../report.json`).
- The page's data: `tools/ettelem/build_wire_report.py` (`LIT` entries marked `dally` and `mesh`, and `WIRE_SCALING`),
  `../report.json` (`literature`, `wire_scaling`); the page: `docs/reports/sources/heat-per-mm.{body.html,script.js}`,
  §7, and `docs/reports/2026-09-24-heat-per-mm.html`.
- The findings: `docs/findings/20-heat-per-mm.md`, "Which process is Dally's figure for"; the request: Q63 in
  `docs/findings/02-requests.md`; the sources: R14 in `docs/findings/01-resources.md`.
- The earlier research, whose Dally rows this note verifies and extends: `SYNTHESIS.md` §1d–1e.
