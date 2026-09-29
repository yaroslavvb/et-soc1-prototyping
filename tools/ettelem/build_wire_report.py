#!/usr/bin/env python3
"""Assemble the heat-per-millimetre report's data: the wire analyses plus the sourced inputs they are compared with.

    build_wire_report.py --wire docs/reports/data/2026-09-24-wire-energy/wire.json \\
                         --wire3 docs/reports/data/2026-09-24-wire-energy/wire3.json \\
                         --out docs/reports/data/2026-09-24-wire-energy/report.json

The page's data come from two analyses, joined here:
  --wire   the 24 September runs (E31 --set v1, E32 --set v2; two cards, three passes each), analyze_wire.py over
           docs/reports/data/2026-09-24-wire{,2}-aifoundry{2,3}: report.json "wire_sep24". The page takes from it only
           what those runs alone measured: the two-term model over five bit densities and the frozen line (v1, v2), the
           first run's block patterns and x/y axes, and their drops and sensitivity.
  --wire3  the third run, the version-3 claims check's six passes on each of three cards (aifoundry2, aifoundry3,
           aifoundry1-c1), analyze_wire_v3.py over docs/reports/data/2026-09-25-claims-v3/raw: report.json "wire", the
           basis of every figure its 28 configurations give (the distance and contention charts, the free-link and
           loaded-mesh costs, the checks, the route calculator). The two are never pooled (analyze_wire_v3.py says why).
  --check  the check's verdicts for V3-WIRE (docs/reports/data/2026-09-25-claims-v3/results/wire.json, default):
           report.json "check_v3", each item's per-card mean and 99% interval and its outcome, which the page quotes for
           the claims the check tested.

The full chain, from the repository root:

    python3 workloads/enercat/analyze_wire.py docs/reports/data/2026-09-24-wire{,2}-aifoundry{2,3} \\
        --out docs/reports/data/2026-09-24-wire-energy/wire.json --pitch-x-mm 3.73 --pitch-y-mm 3.70
    python3 workloads/enercat/analyze_wire_v3.py docs/reports/data/2026-09-25-claims-v3/raw \\
        --out docs/reports/data/2026-09-24-wire-energy/wire3.json --pitch-x-mm 3.73 --pitch-y-mm 3.70
    python3 tools/ettelem/build_wire_report.py --wire docs/reports/data/2026-09-24-wire-energy/wire.json \\
        --wire3 docs/reports/data/2026-09-24-wire-energy/wire3.json --out docs/reports/data/2026-09-24-wire-energy/report.json
    python3 scripts/build-report.py heat-per-mm docs/reports/data/2026-09-24-wire-energy/report.json \\
        docs/reports/2026-09-24-heat-per-mm.html

Every constant below that is not measured here carries its source (docs/reports/data/2026-09-24-wire-energy/research/
SYNTHESIS.md has the quotes and pages). Nothing is fitted in this script. It reads the energy manual's manual.json, the
die geometry's pitch.json, the logical mesh map of workloads/nocbench/analyze.py and the raw runs' reader>target
maps (the 24 September runs' and the third run's, which must agree) by paths relative to the repository, so it runs
from any directory, and it stops with an error if one is missing.
"""
import argparse
import gzip
import importlib.util
import json
import math
import os

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
MANUAL = "docs/reports/data/2026-09-23-energy-manual/manual.json"
PITCH = "docs/reports/data/2026-09-24-wire-energy/research/geometry/pitch.json"
RAW = ["docs/reports/data/2026-09-24-wire-aifoundry2", "docs/reports/data/2026-09-24-wire-aifoundry3",
       "docs/reports/data/2026-09-24-wire2-aifoundry2", "docs/reports/data/2026-09-24-wire2-aifoundry3"]
MAP_SETS = ("wu/p0.5/hop", "wsep/p0.5/hop")   # the configurations whose reader>target maps the page draws
CHECK = "docs/reports/data/2026-09-25-claims-v3/results/wire.json"   # the three-card check's V3-WIRE verdicts


def need(rel, what):
    path = os.path.join(ROOT, rel)
    if not os.path.exists(path):
        raise SystemExit(f"build_wire_report: cannot read {what}: {path} is missing")
    return path

V_NOC = 0.485   # the NoC rail's set point on both cards (reg_mv.noc 485, die_mv.noc 484)

INPUTS = {
    "die_mm2": {"value": 570, "source": "Hot Chips 33, Esperanto (Ditzel), slide 20: 'Die-area: 570 mm2'; IEEE Micro 42(3) 2022 p.37"},
    "die_w_mm": {"value": 25.6, "range": [25.6, 25.8], "source": "estimate: pixels of the IEEE Micro 2022 Fig. 7 die plot scaled to 570 mm2 (research/geometry/pitch.py)"},
    "die_h_mm": {"value": 22.2, "range": [22.1, 22.2], "source": "same"},
    "pitch_x_mm": {"value": 3.73, "source": "same: 254.8 px tile period, outlines and autocorrelation agree"},
    "pitch_y_mm": {"value": 3.70, "source": "same: 252.7 px"},
    "hop_mm": {"value": 3.72, "range": [3.64, 3.74], "source": "about the mean of the two readings of the 570 mm2 (A 3.735, B 3.711 mm; sqrt(px*py) under each; research/SYNTHESIS.md 1a); 3.637 if the area includes the drawn frame"},
    "grid": {"value": "8 x 6 mesh stops: 34 minion shires, PCIe, I/O, 4 memory shires per side", "source": "ET Preliminary Datasheet Rev 1.0, ch. 4"},
    "noc_mhz": {"value": 400, "source": "telemetry mhz.noc; firmware main.c 'NOC frequency modes (400MHz)'"},
    "noc_v": {"value": V_NOC, "source": "telemetry reg_mv.noc 485 / die_mv.noc 484"},
    "port_bits": {"value": 512, "source": "core-et rtl/inc/axi_defines.vh:43 SC_MESH_MASTER_AXI_DATA_SIZE 512; one 64 B line per beat"},
    "lanes": {"value": 4, "source": "core-et-main shirecache_mesh_master.sv: lane by PA[7:6], so lines i and i+4 share a lane"},
}

LIT = [
    {"who": "Dally, AHA retreat keynote 2023, slide 8", "what": "'Communication (~100fJ/b-mm on-chip)'", "fj_bit_mm": 100,
     "conditions": "no node, voltage or data activity stated; the talk's conclusion sets it beside 'Reduce V until it gets too slow (~0.5V)'", "v": None,
     "url": "https://aha.stanford.edu/sites/g/files/sbiybj20066/files/media/file/aha-retreat-2023_dally_keynote_en_eff_ai_hw_0.pdf"},
    {"who": "Dally, Turakhia, Han, CACM 2020", "what": "'This communication costs 100fJ/bit-mm'", "fj_bit_mm": 100,
     "conditions": "in a cost model whose arithmetic and local memory are 'in 14 nm'; no voltage or data activity stated", "v": None,
     "url": "https://www.doc.ic.ac.uk/~wl/teachlocal/arch/papers/cacm20dsa.pdf"},
    {"who": "Keckler, Dally et al., IEEE Micro 2011, Table 1", "what": "256 bits over 10 mm: 310 pJ", "fj_bit_mm": 121,
     "conditions": "40 nm, 0.9 V, random data (50% transitions)", "v": 0.9,
     "url": "https://www.cs.toronto.edu/~pekhimenko/courses/csc2224-f19/docs/GPU.pdf"},
    {"who": "Dally (Yale Patt 75, 2014; DLI 2017)", "what": "10 nm projection: 174 pJ per 256 bits over 10 mm", "fj_bit_mm": 68,
     "conditions": "10 nm, 0.7 V, random data", "v": 0.7, "url": "https://hps.ece.utexas.edu/yale75/dally_slides.pdf"},
    {"who": "Dally et al., VLSI Symposium 2018", "what": "'In present day chips ... between 20-40 fJ/bit-mm'", "fj_bit_mm": 30, "range": [20, 40],
     "conditions": "'in present day chips'; the paper is set in 16 nm; 'about 200fF/mm and independent of scaling'", "v": None,
     "url": "https://research.nvidia.com/sites/default/files/pubs/2018-06_Hardware-Enabled-Artificial-Intelligence/VLSI2018_HardwareAI.pdf.PDF"},
    {"who": "Dally, CACM 2022", "what": "'64 bits 40mm ... 77pJ'", "fj_bit_mm": 30, "conditions": "no node stated", "v": None,
     "url": "https://doi.org/10.1145/3548783"},
    {"who": "Ho, Stanford PhD 2003 (measured)", "what": "9.84 pJ/bit over 10 mm, full swing, every bit toggling", "fj_bit_mm": 492,
     "conditions": "0.18 um, 1.8 V; per random bit this is half", "v": 1.8, "per_transition": 984,
     "url": "https://vlsiweb.stanford.edu/people/alum/pdf/0303_Ho_Wires.pdf"},
]
# Dally's per-mm figures as the page's section 7 table gives them (research/DALLY-NODES.md has every quote with its
# page or slide): "dally" marks them; "label" names the row; "node" and "node_basis" say which process each is for and
# how that is known (stated with the figure, the label of its slide, the setting of its paper, or inferred);
# "c_ff_mm" is a capacitance the source itself gives, used in place of a voltage ("c_rep_ff_mm" with repeaters);
# "chart": False keeps an entry off the voltage chart, "table": False off the section 7 table (the data and
# research/DALLY-NODES.md keep it), "predict": False leaves its prediction blank (no voltage, and a node far from any
# his sources give one for); "v_label" is how the table shows a voltage that is not stated with the figure itself.
# The entries appended below are figures the chart does not draw.
DALLY_ROWS = {
    "Dally, AHA retreat keynote 2023, slide 8": {
        "label": "Dally, Hot Chips keynote and AHA retreat, 2023", "year": 2023, "node": "none stated",
        "node_basis": "its three numbers, 100 fJ/b-mm, 50 fJ/b for a small RAM and ~1 fJ/b for an add, are CACM 2020's 14 nm model",
        "shown": "\"Communication (~100fJ/b-mm on-chip)\"; spoken at Hot Chips: \"about ... 100 femtojoules per bit millimeter\""},
    "Dally, Turakhia, Han, CACM 2020": {
        "label": "Dally, Turakhia, Han, CACM 2020", "year": 2020, "node": "14 nm",
        "node_basis": "the cost model's: its arithmetic is \"In 14 nm technology\", its local memory \"in 14nm\"",
        "shown": "\"Communication between blocks on chip ... at a rate of 100fJ/bit-mm\"; logic and memory energies scale \"while supply voltage is held constant\", but \"Communication energy remains roughly constant\""},
    "Keckler, Dally et al., IEEE Micro 2011, Table 1": {
        "label": "Keckler, Dally et al., IEEE Micro 2011", "year": 2011, "node": "40 nm", "node_basis": "stated, Table 1",
        "per_transition": 240, "shown": "\"240 femtojoules (fJ) per bit per mm\" per transition; 310 pJ for 256 random bits over 10 mm"},
    "Dally (Yale Patt 75, 2014; DLI 2017)": {
        "label": "Dally, Yale Patt 75 (2014), again in 2017", "year": 2014, "node": "10 nm", "node_basis": "stated, a projection",
        "shown": "174 pJ for 256 bits over 10 mm"},
    "Dally et al., VLSI Symposium 2018": {
        "label": "Dally et al., VLSI Symposium 2018", "year": 2018, "node": "16 nm",
        "node_basis": "the paper's setting; the sentence says \"present day chips\"", "c_ff_mm": 200,
        "shown": "\"between 20-40 fJ/bit-mm\"; a wire's energy \"~ CV2\", C \"about 200fF/mm\""},
    "Dally, CACM 2022": {
        "label": "Dally, CACM 2022", "year": 2022, "node": "none stated", "node_basis": "\"today\"",
        "shown": "\"Moving the two 32-bit words ... 1mm takes 1.9pJ\"; 64 bits 40 mm corner to corner, 77 pJ"},
}
for _l in LIT:
    if _l["who"] in DALLY_ROWS:
        _l.update(DALLY_ROWS[_l["who"]], dally=True)
LIT += [
    {"who": "Kogge et al. (Dally and Keckler among the authors), DARPA Exascale Computing Study 2008, p. 130",
     "what": "'At the 32 nm node, we estimate a line capacitance of 300 fF/mm. With a 0.6 V power supply, full swing signaling gives a signaling energy of 110 fJ/bit-mm'",
     "fj_bit_mm": 110, "v": 0.6, "c_ff_mm": 300, "c_rep_ff_mm": 600,
     "conditions": "32 nm, 0.6 V, 300 fF/mm: C V^2, a full charge of the wire for every bit. p. 220: 'the repeater capacitance "
                   "equals the line capacitance for a total of 600fF/mm. At the ITRS supply level of 0.9V, sending a bit on chip "
                   "using conventional full-swing signaling requires about 0.5pJ/mm' (C V^2 again)",
     "url": "https://people.eecs.berkeley.edu/~yelick/papers/Exascale_final_report.pdf",
     "label": "DARPA exascale study (Kogge et al., with Dally and Keckler), 2008", "year": 2008, "node": "32 nm", "node_basis": "stated",
     "shown": "\"At the 32 nm node ... 300 fF/mm. With a 0.6 V power supply, full swing signaling gives a signaling energy of 110 fJ/bit-mm\" (p. 130); with repeaters \"a total of 600fF/mm\", \"about 0.5pJ/mm\" at 0.9 V (p. 220): C V² per bit",
     "counting": "C V² per bit", "dally": True, "chart": False},
    {"who": "Dally, SC10 keynote 2010, slide 37 (again Salishan 2011, SC12 slide 14, HiPEAC 2015, 2017)", "what": "256-bit buses: 26 pJ, 256 pJ and 1 nJ on a 20 mm die",
     "fj_bit_mm": 100, "approx": True, "v": None,
     "conditions": "the slide is labelled 28nm; no voltage or activity; its 2009 version labels the bars '64b 1mm Channel 25pJ/word' "
                   "and '10mm 250pJ', and the 2010 speaker notes call the longest 'Corner to corner (32mm)': 102, 100 and 122 fJ per bit-mm",
     "url": "https://www.nvidia.com/content/PDF/sc_2010/theater/Dally_SC10.pdf",
     "label": "Dally, SC10 and SC12 keynotes (2010, 2012), again to 2017", "year": 2010, "node": "28 nm", "node_basis": "the slide's label",
     "shown": "256-bit buses at 26 pJ, 256 pJ and 1 nJ on a 20 mm die; the 2009 version labels the first two \"64b 1mm Channel 25pJ/word\" and \"10mm 250pJ\", his 2010 notes the longest \"Corner to corner (32mm)\"",
     "dally": True, "chart": False},
    {"who": "Dally, SC09 keynote 'The Future of GPU Computing', slide 14", "what": "'64b 1mm Channel 25pJ/word', '10mm 250pJ, 4cycles', 'Moving a word across die = 10FMAs'",
     "fj_bit_mm": 391, "v": None, "conditions": "no node or voltage; a 64-bit word; the same energies are 256-bit buses on the 2010 slide",
     "url": "https://www.nvidia.com/content/GTC/documents/SC09_Dally.pdf",
     "label": "Dally, SC09 keynote, 2009", "year": 2009, "node": "none stated", "node_basis": "its 64b FPU at 50 pJ/op is the 40 nm DFMA of 2011",
     "shown": "\"64b 1mm Channel 25pJ/word\", \"10mm 250pJ, 4cycles\", \"Moving a word across die = 10FMAs\"", "dally": True, "chart": False, "table": False},
    {"who": "Dally, HPCA 2002 panel, slide 5 (again Stanford EE482C 2002, Queue 2004 Table 1, ISSCC 2005 slide 4)",
     "what": "'Transfer 32b across chip (10mm)': '100pJ' (0.13um), '17pJ' (0.05um); Queue 2004: '32-bit traverse 10mm wire 100 pJ', 'Energy Per Operation (0.13µm, 1.2V)'",
     "fj_bit_mm": 313, "v": 1.2,
     "conditions": "0.13 um, 1.2 V (Queue 2004); 17 pJ (53 fJ per bit per mm) projected for 0.05 um in 2010; activity not stated",
     "url": "http://cva.stanford.edu/publications/2004/spqueue.pdf",
     "label": "Dally, HPCA panel (2002), again ACM Queue 2004", "year": 2002, "node": "0.13 µm", "node_basis": "stated; 53 projected for 0.05 µm",
     "shown": "\"Transfer 32b across chip (10mm)\": \"100pJ\" at 0.13um (2002), \"17pJ\" at 0.05um; \"32-bit traverse 10mm wire 100 pJ\" in \"Energy Per Operation (0.13µm, 1.2V)\" (Queue 2004)",
     "dally": True, "chart": False},
    {"who": "Owens, Dally, Ho, Jayasimha, Keckler, Peh, 'Research Challenges for On-Chip Interconnection Networks', IEEE Micro 2007, p. 99",
     "what": "'In a 22-nm technology ... The chip, running at 0.7 V ... Optimistic wire technology projections estimate ... a power cost of 0.25 mW/Gbps/mm'",
     "fj_bit_mm": 250, "v": 0.7, "counting": "C V² per bit",
     "conditions": "a 2015 CMP's mesh links; 'assuming every single link is fully active at its peak bandwidth', with 25% as the lower activity",
     "url": "https://www.ece.ucdavis.edu/~ocin06/owens-research-challenges-ocin-micro07.pdf",
     "label": "Owens, Dally, Keckler et al., IEEE Micro 2007", "year": 2007, "node": "22 nm", "node_basis": "stated, a projection for 2015",
     "shown": "mesh links of a 22 nm chip \"running at 0.7 V\": \"a power cost of 0.25 mW/Gbps/mm\", every link \"fully active\" (an \"optimistic\" projection)",
     "dally": True, "chart": False},
    {"who": "Gebhart, Johnson, Tarjan, Keckler, Dally, Lindholm, Skadron, ISCA 2011, Table 3 (again MICRO 2011, MICRO 2012)",
     "what": "'Wire capacitance 300 fF/mm', 'Voltage 0.9 Volts', 'Wire Energy (32 bits) 1.9 pJ/mm'", "fj_bit_mm": 59.4, "v": 0.9, "c_ff_mm": 300,
     "conditions": "wire only, random data: 1/4 x 300 fF x 0.81 V^2 x 32 = 1.94 pJ; the setting is a 40 nm (MICRO 2011) or 32 nm (MICRO 2012) GPU",
     "url": "https://www.cs.utexas.edu/~skeckler/pubs/RF_ISCA_11.pdf",
     "label": "Gebhart, Keckler, Dally et al., ISCA 2011", "year": 2011, "node": "40 nm", "node_basis": "the setting: MICRO 2011 \"a commercial 40 nm\" library; 32 nm in 2012",
     "shown": "\"Wire capacitance 300 fF/mm\", \"Voltage 0.9 Volts\", \"Wire Energy (32 bits) 1.9 pJ/mm\"", "dally": True, "chart": False},
    {"who": "Khailany, Dally, Rixner, Kapasi, Owens, Towles, HPCA 2003, Table 1 and footnote 1", "what": "'the wire propagation energy per wire track (0.093 fJ in 0.18 micron technology)'",
     "fj_bit_mm": 65, "v": None, "c_ff_mm": 260,
     "conditions": "'Calculated from an assumed wire capacitance of 0.26 fF per micron including repeater capacitance with a 25% 1-to-0 transition probability': 1/4 C V^2, 65 V^2 fJ per bit-mm; no voltage",
     "url": "http://cva.stanford.edu/publications/2003/khailany_im_scalability.pdf",
     "label": "Khailany, Dally et al., HPCA 2003", "year": 2003, "node": "0.18 µm", "node_basis": "stated",
     "shown": "\"0.26 fF per micron including repeater capacitance with a 25% 1-to-0 transition probability\"", "dally": True, "chart": False, "table": False},
    {"who": "Dally, HiPEAC 2015 keynote, slide 51", "what": "'Goal: reduce Energy/bit 200fJ/bit-mm → 20fJ/bit-mm'", "fj_bit_mm": 200, "v": None,
     "conditions": "the baseline of NVIDIA's on-chip signaling work; a test site on a GM2xx GPU measured '<45fJ/bit-mm'",
     "url": "https://www.cs.colostate.edu/~cs575dl/Sp2015/Lectures/Dally2015.pdf",
     "label": "Dally, HiPEAC keynote, 2015", "year": 2015, "node": "28 nm", "node_basis": "inferred: its test site is on a GM2xx (Maxwell) GPU",
     "shown": "\"Goal: reduce Energy/bit 200fJ/bit-mm → 20fJ/bit-mm\"; a test site on a GM2xx GPU \"<45fJ/bit-mm\"", "dally": True, "chart": False, "table": False},
    {"who": "Dally, 'Deep Learning Hardware' talks: IEEE Santa Clara Valley, Nov 2021, 39:55-40:49; Orange County ACM, Mar 2022, 38:42-40:20",
     "what": "spoken: 'from around 40 or 50 [fJ] per bit today' (slide: '4x Energy Saving – 5-10fJ/bit-mm')", "fj_bit_mm": 45, "range": [40, 50],
     "v": 1.0, "v_label": "~1 V, spoken", "conditions": "slide: 'Numbers above are for 16nm'; spoken: 'we still have to keep nominal one volt supplies almost everywhere'",
     "url": "https://www.youtube.com/watch?v=AGcv_PRKrPQ&t=2322",
     "label": "Dally, Deep Learning Hardware talks, 2021–22", "year": 2022, "node": "16 nm", "node_basis": "slide: \"Numbers above are for 16nm\"",
     "shown": "spoken: \"from around 40 or 50 [fJ] per bit today\" (slide: \"4x Energy Saving – 5-10fJ/bit-mm\"), \"nominal one volt supplies almost everywhere\"; for logic, to 5 nm \"another factor of two to two and a half in energy\"",
     "dally": True, "chart": False},
    {"who": "Dally, NOCS 2022 keynote (slide at 14:10, spoken at 15:48)", "what": "'Energy ~50fJ/bit-mm' for NoC wires on a 5 nm chip", "fj_bit_mm": 50, "v": None,
     "conditions": "spoken: 'in a typical chip say five nanometer chip today ... we tend to use the upper layers for the NoC ... the energy is 50 femtojoules per bit millimeter ... going through the router is a fraction of this energy'",
     "url": "https://www.youtube.com/watch?v=Nk3oQm9NxcY&t=848",
     "label": "Dally, keynote on networks-on-chip (NOCS), 2022", "year": 2022, "node": "5 nm", "node_basis": "spoken: \"a typical chip say five nanometer chip today\"",
     "shown": "slide \"Wire pitch today ... ~80nm on upper layers ... Energy ~50fJ/bit-mm\"; spoken: \"the energy is 50 femtojoules per bit millimeter ... going through the router is a fraction of this energy\"",
     "dally": True, "chart": False, "noc": True},
    {"who": "Zhu, Rucker, Wang, Dally, 'SatIn: Hardware for Boolean Satisfiability Inference', arXiv 2303.02588 (2023), p. 10",
     "what": "'With 32 nm technology, it takes about 0.2 pJ per millimeter to send one bit in a densely packed bus on M7'",
     "fj_bit_mm": 200, "v": 1.05, "counting": "C V² per bit sent",
     "conditions": "32 nm, the design's 'nominal voltage of 1.05 V' (p. 8); wire only: 'Each router ... consumes almost no power'; "
                   "the network's power then applies 'the activity factor of 34%'",
     "url": "https://arxiv.org/pdf/2303.02588",
     "label": "Zhu, Rucker, Wang, Dally, SatIn (arXiv 2023)", "year": 2023, "node": "32 nm", "node_basis": "stated",
     "shown": "\"With 32 nm technology, it takes about 0.2 pJ per millimeter to send one bit in a densely packed bus on M7\"; the design's \"nominal voltage of 1.05 V\"; a router \"consumes almost no power\"",
     "dally": True, "chart": False},
    {"who": "Dally, Hot Interconnects 2023 keynote, slide at 21:50", "what": "on-chip logic to logic, 2 mm: '100Tb/s, 0.1pJ/b'",
     "fj_bit_mm": 50, "v": None, "conditions": "a 2 mm link inside a GPU or switch die; no node, voltage or activity stated",
     "url": "https://www.youtube.com/watch?v=napEsaJ5hMU&t=1310",
     "label": "Dally, Hot Interconnects keynote, 2023", "year": 2023, "node": "none stated", "node_basis": "a GPU or switch die",
     "shown": "logic to logic on the die, 2 mm: \"100Tb/s, 0.1pJ/b\"", "dally": True, "chart": False, "table": False},
    # two other meshes measured on silicon with the data's bit switching controlled ("mesh": the page's section 7b
    # scales them to this mesh's voltage as C V^2); "hop_mm" is the tile pitch range, per flit/word figures as printed
    {"who": "McKeown et al., Piton, HPCA 2018, Fig. 12 (measured)", "mesh": True, "chart": False,
     "what": "NoC energy per 64-bit flit per hop: 'NSW (~3.58 pJ/hop)', 'HSW (~11.16 pJ/hop)', 'FSW (~16.68 pJ/hop)'",
     "flit_bits": 64, "pj_flit_hop": {"none": 3.58, "half": 11.16, "full": 16.68}, "hop_mm": [1.053, 1.14452], "v": 1.0,
     "fj_bit_mm": round((11.16 - 3.58) / 64 * 1000 / ((1.053 + 1.14452) / 2), 1),
     "node": "IBM 32 nm SOI", "year": 2018,
     "conditions": "VDD 1.00 V, 500 MHz; half switching (HSW) flips half the bits between flits, the rate of random data; "
                   "per-hop slope over a zero-hop baseline; tile pitch 1.14452 mm (x), 1.053 mm (y)",
     "url": "https://parallel.princeton.edu/papers/piton-power-hpca18.pdf"},
    {"who": "Kim, Taylor, Miller, Wentzlaff, Raw, ISLPED 2003 (measured)", "mesh": True, "chart": False,
     "what": "'an amortized cost of 85 pJ per 32-bit maximal-toggle word that is routed'", "word_bits": 32,
     "pj_word_hop_full_toggle": 85, "hop_mm": [4, 4], "v": 1.8, "fj_bit_mm": round(85 / 32 * 1000 / 2 / 4, 1),
     "node": "IBM 0.15 um (SA-27E)", "year": 2003,
     "conditions": "1.8 V, 100 MHz; every bit toggling; 'the graphs do not include clock energy'; 4 mm inter-tile wires; "
                   "a random bit toggles half the time, so half of it",
     "url": "https://groups.csail.mit.edu/cag/raw/documents/islped_raw_2003.pdf"},
    {"who": "Keckler, Dally et al., IEEE Micro 2011, Table 1 (10 nm, high frequency)", "what": "256 bits over 10 mm: 200 pJ", "fj_bit_mm": 78.1,
     "conditions": "10 nm projection for 2017, 0.75 V, random data", "v": 0.75, "per_transition": 150,
     "url": "https://www.cs.toronto.edu/~pekhimenko/courses/csc2224-f19/docs/GPU.pdf",
     "label": "Keckler, Dally et al., 2011: 10 nm, high frequency", "year": 2011, "node": "10 nm", "node_basis": "stated, a projection",
     "shown": "150 fJ/bit/mm per transition; 200 pJ for 256 random bits over 10 mm", "dally": True, "chart": False, "table": False},
    {"who": "Keckler, Dally et al., IEEE Micro 2011, Table 1 (10 nm, low voltage)", "what": "256 bits over 10 mm: 150 pJ", "fj_bit_mm": 58.6,
     "conditions": "10 nm projection for 2017, 0.65 V, random data", "v": 0.65, "per_transition": 115,
     "url": "https://www.cs.toronto.edu/~pekhimenko/courses/csc2224-f19/docs/GPU.pdf",
     "label": "Keckler, Dally et al., 2011: 10 nm, low voltage", "year": 2011, "node": "10 nm", "node_basis": "stated, a projection",
     "shown": "115 fJ/bit/mm per transition; 150 pJ for 256 random bits over 10 mm", "dally": True, "chart": False, "table": False},
]
# How Dally's group scales a fixed length of on-chip wire from 28 nm to 7 nm, and the supplies it takes for each node:
# Villa, Johnson, O'Connor, ..., Keckler and Dally, "Scaling the Power Wall: A Path to Exascale", SC14, Table II
# ("Technology scaling factors from 28nm to 7nm"; the text: "fixed-length wire energy (Ewire) scaling at between 0.75x
# and 0.9x per generation"). The page splits each factor into its voltage part, (V_node / V_28)^2, and the rest.
WIRE_SCALING = {
    "source": "Villa et al. (with Keckler and Dally), SC14, Table II, p. 7",
    "url": "https://research.nvidia.com/sites/default/files/pubs/2014-11_Scaling-the-Power//villa.sc2014.pdf",
    "nodes": ["28nm", "20nm", "14nm", "10nm", "7nm"],
    "ewire": [1.0, 0.89, 0.75, 0.62, 0.46],
    "v_nominal": [0.90, 0.85, 0.75, 0.725, 0.70],
    "v_low": [0.85, 0.80, 0.70, 0.675, 0.65],
}
# A plain repeated 7 nm wire from first principles: C 200-400 fF/mm (ASAP7 0.166 fF/um x 1.34-1.87 for repeaters);
# half of C V^2 per transition; a random bit transitions half the time (research/lit/first-principles-estimate.md).
C_WIRE = (200e-15, 300e-15, 400e-15)


def wire_first_principles(v):
    per_tr = [0.5 * c * v * v * 1e15 for c in C_WIRE]   # fJ per transition per mm
    return {"per_transition_fj_mm": per_tr, "per_random_bit_fj_mm": [x / 2 for x in per_tr]}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--wire", required=True, help="the 24 September runs' analysis (analyze_wire.py over E31 and E32)")
    ap.add_argument("--wire3", required=True, help="the third run's analysis (analyze_wire_v3.py over the three-card check)")
    ap.add_argument("--check", default=CHECK, help="the check's V3-WIRE verdicts (results/wire.json)")
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    w = json.load(open(a.wire))     # 24 September: E31 + E32, aifoundry2 and aifoundry3
    w3 = json.load(open(a.wire3))   # the third run: six passes on each of three cards
    # the memory-shire + PHY strip: reading B of pitch.json (the scale the die width and pitch use); the range is the
    # two strips' widths measured to the tile outlines (research/SYNTHESIS.md 1a)
    pitch = json.load(open(need(PITCH, "the die geometry")))
    INPUTS["memshire_w_mm"] = {"value": round(pitch["scale_from_570mm2"]["B_symmetric_bottom"]["memshire_col_w_mm"], 2), "range": [1.74, 1.80],
                               "source": "research/geometry/pitch.json scale_from_570mm2.B_symmetric_bottom.memshire_col_w_mm; "
                                         "range: the two strips to the tile outlines, 1.74 and 1.80 mm (research/SYNTHESIS.md 1a)"}
    # the runner's logical map of the 32 compute shires (x, y) and the four empty positions of the 6 x 6 grid, from
    # the nocbench analysis that the on-chip reports share (the same map as run_wire.py's MESH)
    spec = importlib.util.spec_from_file_location("nocbench_analyze", need("workloads/nocbench/analyze.py", "the mesh map"))
    nb = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(nb)
    INPUTS["mesh_xy"] = {"value": {str(k): list(v) for k, v in sorted(nb.MARTY.items())}, "empty": [list(e) for e in nb.EMPTY],
                         "source": "workloads/nocbench/analyze.py MARTY and EMPTY (marty1885's shire coordinates; run_wire.py MESH is the same map)"}
    L = INPUTS["hop_mm"]["value"]
    Llo, Lhi = INPUTS["hop_mm"]["range"]
    out = {"inputs": INPUTS, "literature": LIT, "wire_scaling": WIRE_SCALING, "wire": w3, "wire_sep24": w,
           "first_principles": {"at_0485": wire_first_principles(V_NOC), "at_09": wire_first_principles(0.9)}}
    # context from the energy manual (docs/reports/data/2026-09-23-energy-manual/manual.json), same cards and clock
    try:
        man = json.load(open(need(MANUAL, "the energy manual context")))
        cb, rr = man["catalogue"]["combined"], man["reruns"]
        out["context"] = {"dram_read_pj_per_byte": rr["levels_pj_per_byte"]["dram"]["mean"],
                          "tload_dram_random_pj_per_byte": cb["tload/dram/random"]["mean"],
                          "own_scratchpad_pj_per_byte": cb["tload/scp/random"]["mean"],
                          "fadd_ps_random_pj": cb["fadd.ps/random/h2"]["mean"], "fmadd_ps_random_pj": cb["fmadd.ps/random/h2"]["mean"],
                          "fadd_s_random_pj": cb["fadd.s/random/h2"]["mean"],
                          "add_random_pj": cb["add/random/h2"]["mean"],
                          "source": "docs/reports/data/2026-09-23-energy-manual/manual.json (catalogue.combined, reruns.levels_pj_per_byte)"}
        # the fitted delivery loss of the minion rail per card (the unmetered attribution, fit_unmetered.py; the hub's
        # section 4.2 quotes the same coefficients): the page's "board against rail" caveat
        um = man.get("unmetered") or {}
        loss = {c: um[c]["coef"]["minion"] for c in um if isinstance(um[c], dict) and "coef" in um[c]}
        if loss:
            out["context"]["minion_delivery_loss"] = loss
            out["context"]["minion_delivery_loss_source"] = ("docs/reports/data/2026-09-23-energy-manual/manual.json "
                                                             "unmetered.<card>.coef.minion (tools/ettelem/fit_unmetered.py)")
    except KeyError as e:
        raise SystemExit(f"build_wire_report: cannot read the energy manual context: {MANUAL} has no {e}")

    # the reader>target map of each drawn configuration, from the raw runs of both analyses (identical over runs,
    # passes and cards: checked here), written into both analyses' link_sharing
    maps = {}
    runs = [gzip.open(need(d + "/runs.jsonl.gz", "the raw runs"), "rt") for d in RAW]
    src3 = w3.get("source", {}).get("raw")
    if not src3:
        raise SystemExit("build_wire_report: the third run's analysis names no raw directory (source.raw)")
    for h, c in sorted(w3.get("cards", {}).items()):
        runs += [open(need(f"{src3}/{h}/wire/p{p}/runs.jsonl", "the third run's raw runs")) for p in c["passes_used"]]
    for f in runs:
        for line in f:
            if not line.startswith("{"):
                continue
            r = json.loads(line)
            if r.get("cfg", "").startswith(MAP_SETS) and r.get("target_map"):
                maps.setdefault(r["cfg"], set()).add(r["target_map"])
    for cfg, m in sorted(maps.items()):
        if len(m) != 1:
            raise SystemExit(f"build_wire_report: {cfg} has {len(m)} different reader>target maps")
        tm = m.pop()
        for ww in (w, w3):
            if cfg in ww["checks"]["link_sharing"]:
                ww["checks"]["link_sharing"][cfg]["target_map"] = tm

    # headline numbers per millimetre, per set and meter, with the pitch range folded into the bar
    head = {}
    for st in ("v1", "v2"):
        for src in ("board", "noc_rail"):
            m = w["model"].get(st, {}).get(src)
            if not m or not m.get("toggle_fj_per_bit_transition_hop"):
                continue
            def mm(pool):
                return {"mean": pool["mean"] / L, "lo": pool["lo"] / Lhi, "hi": pool["hi"] / Llo,
                        "per_card": {h: c["mean"] / L for h, c in pool["per_card"].items()}}
            s0 = m["s0_pj_per_byte_hop"]
            s0_bit = {k: s0[k] / 8 * 1000 for k in ("mean", "lo", "hi")} | {"per_card": {h: {"mean": c["mean"] / 8 * 1000, "se": c["se"] / 8 * 1000, "n": c["n"]} for h, c in s0["per_card"].items()}}
            head[f"{st}/{src}"] = {
                "per_transition": mm(m["toggle_fj_per_bit_transition_hop"]),
                "per_one": mm(m["ones_fj_per_one_bit_hop"]),
                "random_bit_data": mm(m["random_bit_fj_per_bit_hop"]),
                "fixed_per_bit": mm(s0_bit),
                "random_bit_total": {"mean": (m["random_bit_fj_per_bit_hop"]["mean"] + s0_bit["mean"]) / L,
                                     "lo": (m["random_bit_fj_per_bit_hop"]["lo"] + s0_bit["lo"]) / Lhi,
                                     "hi": (m["random_bit_fj_per_bit_hop"]["hi"] + s0_bit["hi"]) / Llo},
                "per_hop": {"per_transition": m["toggle_fj_per_bit_transition_hop"], "per_one": m["ones_fj_per_one_bit_hop"],
                            "random_bit_data": m["random_bit_fj_per_bit_hop"], "fixed_per_bit": s0_bit},
                "rms_pj_per_byte_hop": m["rms_pj_per_byte_hop"]["mean"],
            }
    # uncontended: the link-disjoint pairs (wsep) over d = 1-4, the same distances as the loaded set it is compared with
    # (wsep_d1_4; d = 5 has 14 reader shires and depresses board power), random (P = 1/2) against zeros; only these two
    # densities were run disjoint, so the ones/transition split comes from the loaded runs
    # (from the third run, as are the loaded-mesh figures below)
    dj = w3.get("disjoint_flows", {})

    def mm2(pool):
        return {"mean": pool["mean"] / L, "lo": pool["lo"] / Lhi, "hi": pool["hi"] / Llo,
                "per_card": {h: c["mean"] / L for h, c in pool["per_card"].items()}}
    for src, key in (("board", "pj_per_byte"), ("noc_rail", "noc_pj_per_byte")):
        e = dj.get(key, {}).get("wsep_d1_4")
        if not e or not e.get("random_minus_zeros_fj_per_bit_hop"):
            continue
        d_, z_, r_ = e["random_minus_zeros_fj_per_bit_hop"], e["zeros_fj_per_bit_hop"], e["random_fj_per_bit_hop"]
        head[f"uncontended/{src}"] = {
            "random_bit_data": mm2(d_), "fixed_per_bit": mm2(z_),
            # the total per card is the random-data slope itself (per pass), which is what the check tested (P11a/b)
            "random_bit_total": {"mean": (d_["mean"] + z_["mean"]) / L, "lo": (d_["lo"] + z_["lo"]) / Lhi, "hi": (d_["hi"] + z_["hi"]) / Llo,
                                 "per_card": {h: c["mean"] / L for h, c in r_["per_card"].items()}},
            "per_hop": {"random_bit_data": d_, "fixed_per_bit": z_, "random_bit_total": r_},
            "loaded_same_d": {k: dj[key]["wu"][k] for k in ("random_minus_zeros_fj_per_bit_hop", "zeros_fj_per_bit_hop")},
        }
    # loaded: the all-pairs set over 1, 2, 3, 4 and 6 hops (the third run's "loaded" block), random against zeros,
    # measured directly per card and pass; the ones/differences split of this cost is the 24 September model's (v1, v2)
    for src, key in (("board", "pj_per_byte"), ("noc_rail", "noc_pj_per_byte")):
        e = w3.get("loaded", {}).get(key)
        if not e or not e.get("random_minus_zeros_fj_per_bit_hop"):
            continue
        d_, z_, r_ = e["random_minus_zeros_fj_per_bit_hop"], e["zeros_fj_per_bit_hop"], e["random_fj_per_bit_hop"]
        head[f"loaded/{src}"] = {
            "random_bit_data": mm2(d_), "fixed_per_bit": mm2(z_),
            "random_bit_total": {"mean": (d_["mean"] + z_["mean"]) / L, "lo": (d_["lo"] + z_["lo"]) / Lhi, "hi": (d_["hi"] + z_["hi"]) / Llo,
                                 "per_card": {h: c["mean"] / L for h, c in r_["per_card"].items()}},
            "per_hop": {"random_bit_data": d_, "fixed_per_bit": z_, "random_bit_total": r_, "all_ones": e["ones_fj_per_bit_hop"]},
            "hops": e.get("hops"),
        }
    out["headline"] = head
    # the three-card check's verdicts for the claims it tested: per card mean and 99% interval, outcome, where it holds
    chk = json.load(open(need(a.check, "the three-card check's V3-WIRE results")))
    keep = ("n", "mean", "lo99", "hi99", "status")
    out["check_v3"] = {"source": a.check, "reduced_at": chk.get("reduced_at"), "cards": chk.get("all_cards"), "items": {}}
    for it in chk["items"]:
        ac = it.get("all_cards", {})
        out["check_v3"]["items"][it["item"].split("/")[-1]] = {
            "claims": it.get("claims"), "what": it.get("what"), "outcome": it.get("outcome"), "null": it.get("null"),
            "predicted": it.get("predicted"),
            "all_cards": {k: ac.get(k) for k in ("outcome", "holds_on", "sign_only_on", "fails_on", "insufficient_on") if k in ac},
            "per_card": {h: {k: c[k] for k in keep if k in c} for h, c in it.get("per_card", {}).items()}}
    # V^2 factors to the voltages Dally's figure might assume; the page scales the mesh rail's numbers only (board power
    # carries the regulator's loss, which is not switched capacitance on the die)
    out["scaled"] = {str(v): (v / V_NOC) ** 2 for v in (0.5, 0.7, 0.75, 0.8, 0.9)}
    json.dump(out, open(a.out, "w"), indent=1)
    for k, h in head.items():
        if "random_bit_data" not in h:
            continue
        extra = f"per transition {h['per_transition']['mean']:5.1f}  per one {h['per_one']['mean']:5.1f}  " if "per_transition" in h else " " * 38
        print(f"{k:22s} {extra}random bit data {h['random_bit_data']['mean']:5.1f}  fixed {h['fixed_per_bit']['mean']:5.1f}  total {h['random_bit_total']['mean']:5.1f} fJ/bit.mm")


if __name__ == "__main__":
    main()
