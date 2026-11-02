#!/usr/bin/env python3
"""Q136(c): the TIMA bench's per-stream counts made per-second at each card's measured op rates, and the no-issue excess's candidates priced at
the bench's own constants.

    python3 rtl-sim/tima_bench/price.py --counts counts.json --out-json priced.json --out-md priced.md        # from the repo root

Inputs (all committed): counts.json (run_streams.py); E109's reductions (e109-3pass.json, the post-hoc three passes; e109.json, the two kept) and
E124's (e124.json, the registered primary), whose per-pass `rate` is each item's measured chip-wide op rate; the bench's constants:
  M2   Q132(b) analysis.json > frozen_coef_fJ.vpu_map: floats k 1.871 fJ a merged-net toggle, a 1.092 fJ a clocked register bit; int8 3.735, 2.133
  M4   Q132(b) m4-bench-prediction.json > families.float: core nets 1.624, lane operand bus 7.533, other nets 2.222, clocked bits 1.066 fJ
  I3   the same file > families.int8: nets 3.092, lane operand bus 16.737, clocked bits 1.795 fJ
  card 1's scales from E82: M2 0.9711 (floats), 0.9736 (int8) (e94-e95-bench-prediction.json); M4 0.9711, I3 0.9738 (m4-bench-prediction.json)
The constants were fitted on E78's kinds as D over each format's zeros, so applying them to what runs on zeros is an extrapolation (Q132(b) s14 did
the same and said so). A latch bit written, a data-latch bit opened and an output-register bit of a macro read are priced as clocked register bits;
a storage bit that changes, an address or data line that toggles, as a net; the scratchpad's 256-bit read bus and TenB's read data as the lane
operand bus. Nothing in the bench prices a macro's own read access, a scratchpad SRAM read or the core: for those this prints the price per
event that would carry the measured excess alone (the break-even), beside the bench's price for the bits it can see.
Standard library only. SPDX-License-Identifier: Apache-2.0"""
import argparse
import json
import math
import os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
DD = os.path.join(ROOT, "docs", "reports", "data")
T95 = {1: 12.706, 2: 4.303, 3: 3.182, 4: 2.776, 5: 2.571}
MINIONS, CLOCK = 1024, 600e6

# the TIMA controls: vpu_tensorfma.v's registers on tima_clk_en = working && req_int8 (lines 841-929) and on working && req_int8 (630), the TIMA
# clock's delay line (133); vpu_lane.v's TIMA clock delay (188). Clocked only while int8 works.
TIMA_CTRL = {"shire/minion/vpu/vpu_tensorfma.v": {133, 630, 861, 862, 863, 864, 865, 866, 880, 881, 882, 883, 884, 885, 886, 915, 916, 917,
                                                   920, 927, 928, 929},
             "shire/minion/vpu/vpu_lane.v": {188}}
# the units' valid pipe (vpu_lane.v:498-499): RST_FF, so clocked every cycle in every format; priced with the controls, it cancels a second
TIMA_PIPE = {"shire/minion/vpu/vpu_lane.v": {498, 499}}
# int8's A path: TenTMP's control (vpu_tensorfma.v:940-946)
TENTMP_CTRL = {"shire/minion/vpu/vpu_tensorfma.v": {940, 941, 942, 943, 944, 945, 946}}


def group(lines, spec):
    c = t = p = 0.0
    for k, (w, cl, tg, pr) in lines.items():
        f, ln = k.rsplit(":", 1)
        if int(ln) in spec.get(f, ()):
            c += cl; t += tg; p += pr
    return {"clocked": c, "toggles": t, "present": p}


def candidates(po):
    """Per op, the counted quantities of each candidate, from one stream's per-op record."""
    A, X = po["arrays"], po["x"]
    z = {k: 0.0 for k in ("writes", "bits_written", "changed", "dl_open", "dl_bits", "dl_changed", "reads", "reads_newaddr", "bits_read",
                          "raddr_tog", "rdata_tog", "shadow_changed")}
    tenb, tenc, tena, tmp, lrf = (A.get(c, z) for c in ("tenb", "tenc", "tena", "tentmp", "lane_rf"))
    tc, tp, tt = group(po["lines"], TIMA_CTRL), group(po["lines"], TIMA_PIPE), group(po["lines"], TENTMP_CTRL)
    return {
        "tenb": {"writes": tenb["writes"], "latch_bits": tenb["bits_written"], "dl_bits": tenb["dl_bits"],
                 "changed": tenb["changed"] + tenb["dl_changed"], "raddr_tog": tenb["raddr_tog"], "rdata_tog": tenb["rdata_tog"],
                 "shadow_changed": tenb["shadow_changed"], "storage_changed": tenb["changed"]},
        "tenc": {"reads": tenc["reads"], "reads_newaddr": tenc["reads_newaddr"], "bits_read": tenc["bits_read"], "raddr_tog": tenc["raddr_tog"],
                 "rdata_tog": tenc["rdata_tog"], "writes": tenc["writes"], "bits_written": tenc["bits_written"], "changed": tenc["changed"]},
        "tima_ctrl": {"clocked": tc["clocked"] + tp["clocked"], "toggles": tc["toggles"] + tp["toggles"], "edges": tc["present"] + tp["present"],
                      "int8_enabled_clocked": tc["clocked"], "int8_enabled_toggles": tc["toggles"], "valid_pipe_clocked": tp["clocked"],
                      "gate_enables": X["gate_tima"]},
        "scp": {"rd32": X["scp_rd32"], "rd64": X["scp_rd64"], "rd256": X["scp_rd256"], "reads": X["scp_rd32"] + X["scp_rd64"] + X["scp_rd256"],
                "bits_requested": 32 * X["scp_rd32"] + 64 * X["scp_rd64"] + 256 * X["scp_rd256"], "data_tog": X["scp_data_tog"],
                "req_tog": X["scp_req_tog"], "tentmp_writes": tmp["writes"], "tentmp_bits": tmp["bits_written"] + tmp["dl_bits"],
                "tentmp_net": tmp["changed"] + tmp["dl_changed"] + tmp["raddr_tog"] + tmp["rdata_tog"] + X["tentmp_wd_tog"],
                "tentmp_ctrl_clocked": tt["clocked"], "tentmp_ctrl_toggles": tt["toggles"], "tena_writes": tena["writes"],
                "tena_bits": tena["bits_written"] + tena["dl_bits"], "tena_net": tena["changed"] + tena["dl_changed"] + tena["raddr_tog"] + tena["rdata_tog"] + X["tena_wd_tog"],
                "tenb_wbus_tog": X["tenb_wd_tog"]},
        "lane_rf": {"reads": lrf["reads"], "writes": lrf["writes"], "bits_read": lrf["bits_read"], "bits_written": lrf["bits_written"],
                    "net": lrf["changed"] + lrf["raddr_tog"] + lrf["rdata_tog"]},
        "registers": {"clocked": po["ff_clocked_bits"], "edges": po["ff_present_bits"], "toggles": po["ff_toggles"]},
        "cycles": po["cycles"], "uops": po["uops"], "tima_ren3_cycles": X["tima_ren3"], "tima_clk_en_cycles": X["tima_clk_en"], "working_cycles": X["working"],
    }


def terms(c):
    """The candidate's counts sorted into the bench's three kinds of term: clocked bits, nets, operand-bus nets (an op)."""
    return {
        "tenb": {"clocked": c["tenb"]["latch_bits"] + c["tenb"]["dl_bits"], "nets": c["tenb"]["changed"] + c["tenb"]["raddr_tog"], "bus": c["tenb"]["rdata_tog"]},
        "tenc": {"clocked": c["tenc"]["bits_read"] + c["tenc"]["bits_written"], "nets": c["tenc"]["raddr_tog"] + c["tenc"]["rdata_tog"] + c["tenc"]["changed"], "bus": 0.0},
        "tima_ctrl": {"clocked": c["tima_ctrl"]["clocked"], "nets": c["tima_ctrl"]["toggles"], "bus": 0.0},
        "scp": {"clocked": c["scp"]["tentmp_bits"] + c["scp"]["tentmp_ctrl_clocked"] + c["scp"]["tena_bits"],
                "nets": c["scp"]["req_tog"] + c["scp"]["tentmp_net"] + c["scp"]["tentmp_ctrl_toggles"] + c["scp"]["tena_net"],
                "bus": c["scp"]["data_tog"]},
    }


def constants():
    a = json.load(open(os.path.join(DD, "2026-11-01-q132-rtl-bench", "analysis.json")))
    m4 = json.load(open(os.path.join(DD, "2026-11-01-q132-rtl-bench", "m4-bench-prediction.json")))["families"]
    e9495 = json.load(open(os.path.join(DD, "2026-11-01-q132-rtl-bench", "e94-e95-bench-prediction.json")))["models"]["vpu_map"]
    f2, i2 = a["frozen_coef_fJ"]["vpu_map"]["float"], a["frozen_coef_fJ"]["vpu_map"]["int8"]
    sc = e9495["card1_scale_from_e82"]
    fm, im = m4["float"]["coef_fJ"], m4["int8"]["coef_fJ"]
    return {
        "M2 floats": {"clocked": f2["dclk"], "nets": f2["dnetsm_vpu"], "bus": f2["dnetsm_vpu"], "card1": sc["float"],
                      "source": "q132 analysis.json > frozen_coef_fJ.vpu_map.float; card 1: e94-e95-bench-prediction.json > models.vpu_map.card1_scale_from_e82.float"},
        "M2 int8": {"clocked": i2["dclk"], "nets": i2["dnetsm_vpu"], "bus": i2["dnetsm_vpu"], "card1": sc["int8"],
                    "source": "q132 analysis.json > frozen_coef_fJ.vpu_map.int8; card 1: the same file's .int8"},
        "M4 floats": {"clocked": fm[3], "nets": fm[2], "bus": fm[1], "card1": m4["float"]["card1_scale_from_e82"],
                      "source": "q132 m4-bench-prediction.json > families.float.coef_fJ (other nets, lane operand bus, clocked bits)"},
        "I3 int8": {"clocked": im[2], "nets": im[0], "bus": im[1], "card1": m4["int8"]["card1_scale_from_e82"],
                    "source": "q132 m4-bench-prediction.json > families.int8.coef_fJ"},
    }


def ci(v):
    n = len(v)
    m = sum(v) / n
    if n < 2:
        return {"mean": m, "half": None, "n": n}
    sd = math.sqrt(sum((x - m) ** 2 for x in v) / (n - 1))
    return {"mean": m, "half": T95[n - 1] * sd / math.sqrt(n), "n": n}


def rates(path):
    d = json.load(open(path))
    per = d["per_pass"]
    out = {}
    for p, e in per.items():
        for item, r in e.items():
            out.setdefault(item, []).append(r["rate"])
    return {k: sum(v) / len(v) for k, v in out.items()}, d


def n_contrast(d):
    """N = S(m0.int8.zeros) - S(m0.fp32.zeros), per kept pass, mean and 95% interval (posthoc_check_e109.reading's S_m0_gap)."""
    v = [e["m0.int8.zeros"]["S"] - e["m0.fp32.zeros"]["S"] for e in d["per_pass"].values()]
    return ci(v)


def scale(x, f):
    return {k: (scale(v, f) if isinstance(v, dict) else (v * f if isinstance(v, (int, float)) else v)) for k, v in x.items()}


def sub(a, b):
    return {k: (sub(a[k], b[k]) if isinstance(a[k], dict) else a[k] - b[k]) for k in a}


def price(t, K, card_scale=1.0):
    """W from per-second term counts at one constant set (fJ)."""
    return {cand: card_scale * 1e-15 * (v["clocked"] * K["clocked"] + v["nets"] * K["nets"] + v["bus"] * K["bus"]) for cand, v in t.items()}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--counts", required=True)
    ap.add_argument("--out-json", required=True)
    ap.add_argument("--out-md", required=True)
    a = ap.parse_args()
    C = json.load(open(a.counts))
    S = {s["name"]: s for s in C["streams"] if s["set"] in ("design", "context", "arms", "context_arms")}
    K = constants()
    exps = {
        "E109, aifoundry3 card 0 (three passes, post hoc)": os.path.join(DD, "2026-11-01-e109-int8-zeros", "e109-3pass.json"),
        "E109, aifoundry3 card 0 (two kept passes)": os.path.join(DD, "2026-11-01-e109-int8-zeros", "e109.json"),
        "E124, aifoundry1 card 1 (registered, four passes)": os.path.join(DD, "2026-11-01-e124-int8-zeros-replicate", "e124.json"),
    }
    # duty: measured ops/s over the clock's ops/s at the card's cycles per op, on the plain items
    res = {"what": __doc__.split("\n")[0], "constants": K, "experiments": {}}
    per_op = {n: candidates(s["per_op"]) for n, s in S.items()}
    res["per_op"] = per_op
    for ename, path in exps.items():
        R, d = rates(path)
        duty = [R[i] / (MINIONS * CLOCK / c) for i, c in (("fp32.zeros", 546.001), ("int8.zeros", 318.001), ("m0.int8.zeros", 318.001))]
        duty = sum(duty) / len(duty)
        is_card1 = "card 1" in ename
        per_s = {}
        for n, s in S.items():
            item = n[4:] if n.startswith("pre.") else n
            if item in R:
                rate, how = R[item], "measured"
            else:
                rate, how = MINIONS * CLOCK * duty / s["period"], f"predicted: 1024 x 600 MHz x duty {duty:.4f} / {s['period']} cycles"
            per_s[n] = {"rate": rate, "rate_how": how, "counts": scale(per_op[n], rate), "terms": scale(terms(per_op[n]), rate)}
        N = n_contrast(d)
        # the scratchpad at one price: if all of fp32's no-issue S were reads (or bits requested), the most one could cost, and what int8's
        # extra reads (bits) a second would then buy; per kept pass, as posthoc_check_e109.reading computes the per-read ceiling
        cr, cb, xr, xb = [], [], [], []
        for p, e in d["per_pass"].items():
            f, i = e["m0.fp32.zeros"], e["m0.int8.zeros"]
            rf, ri = per_op["m0.fp32.zeros"]["scp"]["reads"] * f["rate"], per_op["m0.int8.zeros"]["scp"]["reads"] * i["rate"]
            bf, bi = per_op["m0.fp32.zeros"]["scp"]["bits_requested"] * f["rate"], per_op["m0.int8.zeros"]["scp"]["bits_requested"] * i["rate"]
            cr.append(f["S"] / rf * 1e12); cb.append(f["S"] / bf * 1e15)
            xr.append((ri - rf) * f["S"] / rf); xb.append((bi - bf) * f["S"] / bf)
        scp_ceiling = {"per_read_pj": ci(cr), "per_bit_fj": ci(cb), "int8_extra_reads_w": ci(xr), "int8_extra_bits_w": ci(xb)}
        contrasts = {}
        for cname, x, y in (("N, from reset (the bench's own runs)", "m0.int8.zeros", "m0.fp32.zeros"),
                            ("N, fp32 after an int8 run (the card's order)", "m0.int8.zeros", "pre.m0.fp32.zeros"),
                            ("zeros' gap G, from reset", "int8.zeros", "fp32.zeros"),
                            ("zeros' gap G, fp32 after an int8 run", "int8.zeros", "pre.fp32.zeros"),
                            ("desk-only arm: N with one A row (TenC read at one address), from reset", "m0r1.int8.zeros", "m0r1.fp32.zeros"),
                            ("desk-only arm: N with one A row, fp32 after an int8 run", "m0r1.int8.zeros", "pre.m0r1.fp32.zeros"),
                            ("desk-only arm: N with eight A rows, fp32 after an int8 run", "m0r8.int8.zeros", "pre.m0r8.fp32.zeros"),
                            ("desk-only arm: N with K = 1, fp32 after an int8 run", "m0k1.int8.zeros", "pre.m0k1.fp32.zeros")):
            dt = sub(per_s[x]["terms"], per_s[y]["terms"])
            dc = sub(per_s[x]["counts"], per_s[y]["counts"])
            pr = {}
            for kn, kv in K.items():
                w = price(dt, kv, kv["card1"] if is_card1 else 1.0)
                pr[kn] = {**w, "sum": sum(w.values())}
            contrasts[cname] = {"x": x, "y": y, "d_counts_per_s": dc, "d_terms_per_s": dt, "priced_w": pr}
        # break-even: what one event of each candidate would have to cost to carry N alone (the measured mean)
        Nm = N["mean"]
        be = {}
        dN = contrasts["N, from reset (the bench's own runs)"]["d_counts_per_s"]
        dNc = contrasts["N, fp32 after an int8 run (the card's order)"]["d_counts_per_s"]
        for lab, val in (("a TenC read (one 32-bit word, one unit), from reset", dN["tenc"]["reads"]),
                         ("a TenC read at a new address, from reset", dN["tenc"]["reads_newaddr"]),
                         ("a TenC read, fp32 after an int8 run", dNc["tenc"]["reads"]),
                         ("a TenC read at a new address, fp32 after an int8 run", dNc["tenc"]["reads_newaddr"]),
                         ("a TenB write (one 32-bit entry)", dN["tenb"]["writes"]),
                         ("a TIMA control bit clocked", dN["tima_ctrl"]["clocked"]),
                         ("a scratchpad read (any size)", dN["scp"]["reads"]),
                         ("a scratchpad bit requested", dN["scp"]["bits_requested"]),
                         ("a 64-bit A read into TenTMP (int8 only)", dN["scp"]["rd64"]),
                         ("a cycle of one minion's FSM working in int8 (tima_clk_en high)", dN["tima_clk_en_cycles"])):
            be[lab] = {"d_per_s": val, "fj_each_to_carry_N": (Nm / val * 1e15) if val > 0 else None}
        res["experiments"][ename] = {"duty": duty, "N_measured_w": N, "per_s": per_s, "contrasts": contrasts, "break_even": be,
                                     "scratchpad_at_one_price": scp_ceiling}
    json.dump(res, open(a.out_json, "w"), indent=1)
    write_md(res, a.out_md)
    print(open(a.out_md).read()[:6000])


def f(x, k=2):
    return "—" if x is None else f"{x:,.{k}f}"


def g(x):
    return f"{x:.3g}"


def pm(c, k=3, unit=""):
    return f"{c['mean']:+.{k}f}" + ("" if c["half"] is None else f" ± {c['half']:.{k}f}") + unit


ROWS = [("cycles", lambda c: c["cycles"]), ("micro-ops", lambda c: c["uops"]),
        ("TenB writes", lambda c: c["tenb"]["writes"]), ("TenB latch bits written", lambda c: c["tenb"]["latch_bits"]),
        ("TenB data-latch bits opened", lambda c: c["tenb"]["dl_bits"]), ("TenB nets (storage, address, data)", lambda c: c["tenb"]["changed"] + c["tenb"]["raddr_tog"] + c["tenb"]["rdata_tog"]),
        ("TenC reads", lambda c: c["tenc"]["reads"]), ("TenC reads at a new address", lambda c: c["tenc"]["reads_newaddr"]),
        ("TenC bits read", lambda c: c["tenc"]["bits_read"]), ("TenC nets (address, data, storage)", lambda c: c["tenc"]["raddr_tog"] + c["tenc"]["rdata_tog"] + c["tenc"]["changed"]),
        ("TIMA controls, bits clocked (int8 enables)", lambda c: c["tima_ctrl"]["int8_enabled_clocked"]),
        ("TIMA valid pipe, bits clocked", lambda c: c["tima_ctrl"]["valid_pipe_clocked"]),
        ("TIMA controls, bits changed", lambda c: c["tima_ctrl"]["toggles"]), ("TIMA clock-gate enables (8 lanes)", lambda c: c["tima_ctrl"]["gate_enables"]),
        ("scratchpad reads, 32-bit", lambda c: c["scp"]["rd32"]), ("scratchpad reads, 64-bit (A into TenTMP)", lambda c: c["scp"]["rd64"]),
        ("scratchpad reads, 256-bit (B)", lambda c: c["scp"]["rd256"]), ("scratchpad bits requested", lambda c: c["scp"]["bits_requested"]),
        ("scratchpad read-bus bits changed", lambda c: c["scp"]["data_tog"]), ("TenA writes", lambda c: c["scp"]["tena_writes"]),
        ("TenTMP writes", lambda c: c["scp"]["tentmp_writes"]), ("register bits clocked (all)", lambda c: c["registers"]["clocked"]),
        ("register-bit clock edges (all)", lambda c: c["registers"]["edges"])]


def stream_table(L, names, per_op, scale_of=None, unit="an op"):
    L.append("| " + f"{unit} | " + " | ".join(f"`{n}`" for n in names) + " |")
    L.append("|---|" + "---:|" * len(names))
    for lab, fn in ROWS:
        if scale_of is not None and lab == "cycles":
            continue
        vals = [fn(per_op[n]) * (1 if scale_of is None else scale_of[n]) for n in names]
        L.append(f"| {lab} | " + " | ".join(f"{v:,.1f}" if scale_of is None else g(v) for v in vals) + " |")
    L.append("")


def write_md(res, path):
    L = ["# Q136(c) priced: the no-issue excess's candidates at the bench's constants", "",
         "Generated by `rtl-sim/tima_bench/price.py` from `counts.json`; every number below is in `priced.json`. Counts are per TensorFMA op on one",
         "minion (the bench), or a second chip-wide (an op's count times the item's measured op rate). The RTL is core-et's, the Erbium branch:",
         "a later revision of the ET-SoC-1's lineage, not the ET-SoC-1's own.", ""]
    po = res["per_op"]
    design = ["fp32.zeros", "m0.fp32.zeros", "k8.fp32.zeros", "r8.fp32.zeros", "m0k8.fp32.zeros", "int8.zeros", "m0.int8.zeros", "k8.int8.zeros",
              "r8.int8.zeros", "m0k8.int8.zeros", "fp32.a_zeros_b_randn", "m0.fp32.a_zeros_b_randn", "fp32.a_nz_b_randn", "m0.fp32.a_nz_b_randn",
              "anchor_pi", "fp32.randn", "fp16.zeros", "fp16.randn", "int8.full"]
    context = [n for n in po if n.startswith("pre.")]
    arms = [n for n in po if n not in design and n not in context]
    L.append("## 1. Per op, E109's and E124's design (each at the card's cycles per op)")
    L.append("")
    for chunk in (design[:5], design[5:10], design[10:15], design[15:]):
        stream_table(L, chunk, po)
    L.append("## 2. Per op, the fp32 streams run after an int8 run (the card's order)")
    L.append("")
    stream_table(L, context, po)
    L.append("## 3. Per op, desk-only arms (no card has run them; period = the bench's own cycles + 7.75)")
    L.append("")
    for chunk in (arms[:4], arms[4:]):
        stream_table(L, chunk, po)
    E = res["experiments"]
    for ename, e in E.items():
        N = e["N_measured_w"]
        L.append(f"## {ename}")
        L.append("")
        L.append(f"Measured N = S(m0.int8.zeros) − S(m0.fp32.zeros) = **{pm(N)} W** (95%, {N['n']} passes); duty {e['duty']:.4f}.")
        L.append("")
        rate = {n: e["per_s"][n]["rate"] for n in design}
        L.append("### A second, chip-wide, at this experiment's measured op rates")
        L.append("")
        L.append("| item | " + " | ".join(f"`{n}`" for n in design[:10]) + " |")
        L.append("|---|" + "---:|" * 10)
        L.append("| ops a second | " + " | ".join(f"{rate[n]:.4g}" for n in design[:10]) + " |")
        L.append("")
        stream_table(L, design[:10], po, scale_of=rate, unit="a second")
        for cname, c in e["contrasts"].items():
            L.append(f"### {cname}: `{c['x']}` − `{c['y']}`, priced (W)")
            L.append("")
            L.append("| constants | TenB arrays | TenC read port | TIMA controls | scratchpad reads, TenA, TenTMP | sum |")
            L.append("|---|---:|---:|---:|---:|---:|")
            for kn, w in c["priced_w"].items():
                L.append(f"| {kn} | {w['tenb']:+.3f} | {w['tenc']:+.3f} | {w['tima_ctrl']:+.3f} | {w['scp']:+.3f} | **{w['sum']:+.3f}** |")
            L.append("")
        sc = e["scratchpad_at_one_price"]
        L.append("### The scratchpad at one price (if all of fp32's no-issue S were its reads, or its bits)")
        L.append("")
        L.append(f"- at most {pm(sc['per_read_pj'], 2)} pJ a read; int8's extra reads a second then buy {pm(sc['int8_extra_reads_w'])} W")
        L.append(f"- at most {pm(sc['per_bit_fj'], 1)} fJ a bit requested; int8's extra bits a second then buy {pm(sc['int8_extra_bits_w'])} W")
        L.append("")
        L.append("### Break-even: what one event would have to cost to carry the measured N alone")
        L.append("")
        L.append("| event | Δ a second (int8 − fp32, chip-wide) | fJ each |")
        L.append("|---|---:|---:|")
        for lab, b in e["break_even"].items():
            L.append(f"| {lab} | {b['d_per_s']:.3e} | {f(b['fj_each_to_carry_N'], 1)} |")
        L.append("")
    open(path, "w").write("\n".join(L) + "\n")


if __name__ == "__main__":
    main()
