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
    out = {"inputs": INPUTS, "literature": LIT, "wire": w3, "wire_sep24": w,
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
