#!/usr/bin/env python3
"""Assemble the heat-per-millimetre report's data: the wire analysis plus the sourced inputs it is compared with.

    build_wire_report.py --wire docs/reports/data/2026-09-24-wire-energy/wire.json \\
                         --out docs/reports/data/2026-09-24-wire-energy/report.json

Every constant below that is not measured here carries its source (docs/reports/data/2026-09-24-wire-energy/research/
SYNTHESIS.md has the quotes and pages). Nothing is fitted in this script.
"""
import argparse
import json
import math

V_NOC = 0.485   # the NoC rail's set point on both cards (reg_mv.noc 485, die_mv.noc 484)

INPUTS = {
    "die_mm2": {"value": 570, "source": "Hot Chips 33, Esperanto (Ditzel), slide 20: 'Die-area: 570 mm2'; IEEE Micro 42(3) 2022 p.37"},
    "die_w_mm": {"value": 25.6, "range": [25.6, 25.8], "source": "estimate: pixels of the IEEE Micro 2022 Fig. 7 die plot scaled to 570 mm2 (research/geometry/pitch.py)"},
    "die_h_mm": {"value": 22.2, "range": [22.1, 22.2], "source": "same"},
    "pitch_x_mm": {"value": 3.73, "source": "same: 254.8 px tile period, outlines and autocorrelation agree"},
    "pitch_y_mm": {"value": 3.70, "source": "same: 252.7 px"},
    "hop_mm": {"value": 3.72, "range": [3.64, 3.74], "source": "sqrt(px*py) under three readings of what the 570 mm2 covers: 3.735, 3.711, 3.637 mm (research/SYNTHESIS.md 1a)"},
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
     "conditions": "in a paragraph about 14 nm on-chip memory; no voltage or data activity stated", "v": None,
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
# A plain repeated 7 nm wire from first principles: C 200-400 fF/mm (ASAP7 0.166 fF/um x 1.34-1.87 for repeaters);
# half of C V^2 per transition; a random bit transitions half the time (research/lit/first-principles-estimate.md).
C_WIRE = (200e-15, 300e-15, 400e-15)


def wire_first_principles(v):
    per_tr = [0.5 * c * v * v * 1e15 for c in C_WIRE]   # fJ per transition per mm
    return {"per_transition_fj_mm": per_tr, "per_random_bit_fj_mm": [x / 2 for x in per_tr]}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--wire", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    w = json.load(open(a.wire))
    L = INPUTS["hop_mm"]["value"]
    Llo, Lhi = INPUTS["hop_mm"]["range"]
    out = {"inputs": INPUTS, "literature": LIT, "wire": w, "first_principles": {"at_0485": wire_first_principles(V_NOC), "at_09": wire_first_principles(0.9)}}
    # context from the energy manual (docs/reports/data/2026-09-23-energy-manual/manual.json), same cards and clock
    try:
        man = json.load(open("docs/reports/data/2026-09-23-energy-manual/manual.json"))
        cb, rr = man["catalogue"]["combined"], man["reruns"]
        out["context"] = {"dram_read_pj_per_byte": rr["levels_pj_per_byte"]["dram"]["mean"],
                          "tload_dram_random_pj_per_byte": cb["tload/dram/random"]["mean"],
                          "own_scratchpad_pj_per_byte": cb["tload/scp/random"]["mean"],
                          "fadd_ps_random_pj": cb["fadd.ps/random/h2"]["mean"], "fmadd_ps_random_pj": cb["fmadd.ps/random/h2"]["mean"],
                          "fadd_s_random_pj": cb["fadd.s/random/h2"]["mean"],
                          "add_random_pj": cb["add/random/h2"]["mean"],
                          "source": "docs/reports/data/2026-09-23-energy-manual/manual.json (catalogue.combined, reruns.levels_pj_per_byte)"}
    except Exception as e:
        out["context"] = {"error": str(e)}

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
    dj = w.get("disjoint_flows", {})
    for src, key in (("board", "pj_per_byte"), ("noc_rail", "noc_pj_per_byte")):
        e = dj.get(key, {}).get("wsep_d1_4")
        if not e or not e.get("random_minus_zeros_fj_per_bit_hop"):
            continue
        def mm2(pool):
            return {"mean": pool["mean"] / L, "lo": pool["lo"] / Lhi, "hi": pool["hi"] / Llo,
                    "per_card": {h: c["mean"] / L for h, c in pool["per_card"].items()}}
        d_, z_ = e["random_minus_zeros_fj_per_bit_hop"], e["zeros_fj_per_bit_hop"]
        head[f"uncontended/{src}"] = {
            "random_bit_data": mm2(d_), "fixed_per_bit": mm2(z_),
            "random_bit_total": {"mean": (d_["mean"] + z_["mean"]) / L, "lo": (d_["lo"] + z_["lo"]) / Lhi, "hi": (d_["hi"] + z_["hi"]) / Llo},
            "per_hop": {"random_bit_data": d_, "fixed_per_bit": z_},
            "loaded_same_d": {k: dj[key]["wu"][k] for k in ("random_minus_zeros_fj_per_bit_hop", "zeros_fj_per_bit_hop")},
        }
    out["headline"] = head
    # V^2 factors to the voltages Dally's figure might assume; the page scales the mesh rail's numbers only (board power
    # carries the regulator's loss, which is not switched capacitance on the die)
    out["scaled"] = {str(v): (v / V_NOC) ** 2 for v in (0.5, 0.7, 0.75, 0.8, 0.9)}
    json.dump(out, open(a.out, "w"), indent=1)
    for k, h in head.items():
        extra = f"per transition {h['per_transition']['mean']:5.1f}  per one {h['per_one']['mean']:5.1f}  " if "per_transition" in h else " " * 38
        print(f"{k:22s} {extra}random bit data {h['random_bit_data']['mean']:5.1f}  fixed {h['fixed_per_bit']['mean']:5.1f}  total {h['random_bit_total']['mean']:5.1f} fJ/bit.mm")


if __name__ == "__main__":
    main()
