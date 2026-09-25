#!/usr/bin/env python3
"""Fill report_template.html with the numbers from analyze.py's summary.json and the energy manual's manual.json.

    build_report.py docs/reports/data/2026-09-19-memprobe-aifoundry2/summary.json \
        docs/reports/data/2026-09-23-energy-manual/manual.json docs/reports/2026-09-19-et-soc1-memory-anatomy.html

The page script gets the data as D (__DATA__). Numbers that the prose quotes are filled in here, at build time,
from the same files (@@name@@ in the template), so they are in the page without JavaScript; any @@name@@ left
unfilled stops the build. manual.json supplies the later, canonical energies per byte that the page's own
19 September energies are compared with.
"""
import json
import os
import re
import statistics as st
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gen_ops as g  # noqa: E402

LEVELS = ("l1", "l2", "l3", "dram")


def rnd(x):
    """Round half away from zero (Python's round() goes to even: 26.5 -> 26)."""
    return int(x + 0.5) if x >= 0 else -int(-x + 0.5)


def num(x, dp=0):
    return f"{x:,.{dp}f}" if dp else f"{rnd(x):,}"


def pct(x):
    return f"{rnd(100 * x)}%"


def span(a, b):
    a, b = rnd(a), rnd(b)
    return f"{a:,}" if a == b else f"{min(a, b):,}–{max(a, b):,}"


def main():
    if len(sys.argv) != 4:
        raise SystemExit(__doc__)
    s = json.load(open(sys.argv[1]))
    man = json.load(open(sys.argv[2]))
    energy = {}
    for k, v in s["power"].items():
        w, r = v["watts"], v["rate"]
        pj = lambda x: x / r * 1e12  # noqa: E731
        rest = w["system"] - w["minion"] - w["sram"] - w["noc"]
        energy[k] = {"minion": pj(w["minion"]), "sram": pj(w["sram"]), "noc": pj(w["noc"]), "rest": pj(rest),
                     "sp_total": pj(w["system"]), "host_total": pj(w["board"]), "rate": r,
                     "cpl": v["cycles_per_load"], "cpl_slow": v["cycles_per_load_slowest"],
                     "watts": {"minion": w["minion"], "sram": w["sram"], "noc": w["noc"], "rest": rest}}
    far = st.mean(s["far_hops"])
    ref, dec = s["refresh"], s["decomp"]
    lv = man["reruns"]["levels_pj_per_byte"]
    cat = man["catalogue"]["combined"]  # 1 KB tensor loads from DRAM with the data known (catalogue keys "op/level/data")
    manual = {k: {x: lv[k][x] for x in ("mean", "lo", "hi", "n")} for k in LEVELS}
    manual["dram_zeros"], manual["dram_random"] = cat["tload/dram/zeros"]["mean"], cat["tload/dram/random"]["mean"]
    data = {
        "msPos": {int(k): v for k, v in dec["ms_pos"].items()},
        "msConst": dec["ms_const"],
        "energy": energy,
        "hopPj": (energy["l3far"]["sp_total"] - energy["l3near"]["sp_total"]) / far,
        "ladder": s["ladder"],
        "l3": dec["l3_by_slice"],
        "modelErr": dec["model_err_hist"],
        "memByHome": dec["mem_by_home"],
        "memHist": dec["mem_hist"],
        "memMed": dec["mem"]["med"],
        "memN": sum(n for _, n in dec["mem_hist"]),
        "msmap": s["msmap"],
        "bits": s["bits"],
        "refresh": {"curve": ref["curve"], "period_cycles": ref["period_cycles"]},
        "rowlife": ref["rowlife"],
        "hitPhase": ref["hit_by_phase"],
        "inRefresh": ref["in_refresh"],
        "opCycles": ref["op_cycles"],
        "pto": s["pagetimeout"],
        "timer": s["timer"],
        "manual": manual,
    }

    # ---- numbers quoted in the prose ----
    T = {}
    life = [x for x in ref["rowlife"] if x["gap"] < 2000]
    a = [sum(x[k] for x in life) for k in ("hit_no_refresh", "n_no_refresh", "hit_refresh", "n_refresh")]
    T.update(rows_hit=num(a[0]), rows_n=num(a[1]), rows_pct=pct(a[0] / a[1]),
             rows_ref_hit=num(a[2]), rows_ref_n=num(a[3]), rows_ref_pct=pct(a[2] / a[3]))
    T["op_cycles"] = num(round(ref["op_cycles"], -1))
    T["probe_ovh"] = num(round(2 * ref["op_cycles"], -1))
    T["loop_outside"] = num(round(4 * ref["op_cycles"], -1))
    T["in_refresh_pct"] = pct(ref["in_refresh"])
    pto = {p["delay"]: p for p in s["pagetimeout"]}
    for d in (0, 1000, 1500):
        T[f"model{d}"] = pct(pto[d]["refresh_model_loop"])
        T[f"meas{d}"] = pct(pto[d]["hit"])
    ns = {pto[d]["n"] for d in (0, 1000, 1500)}
    T["pairs_n"] = num(min(ns)) if len(ns) == 1 else f"{min(ns)}–{max(ns)}"
    nall = [p["n"] for p in s["pagetimeout"]]
    T["pairs_n_all"] = span(min(nall), max(nall))
    late = [p for p in s["pagetimeout"] if p["delay"] >= 3000]
    T["late_hits"] = f"{sum(p['hits'] for p in late)} of {sum(p['n'] for p in late):,}"
    T["late_from"], T["late_to"] = num(late[0]["delay"]), num(late[-1]["delay"])
    b = s["bits"]
    T["bits_row"] = num(st.median(b[str(k)]["b_minus_b0_med"] for k in range(18, 30)))
    T["bits_col"] = num(-st.median(b[str(k)]["b_minus_b0_med"] for k in range(13, 18)))
    lm = s["ladder_by_ms"]
    far_ms = [lm["nodelay:3"][str(m)]["resid_med"] for m in (3, 5, 7)]
    T["nd_slow"] = span(min(far_ms), max(far_ms))
    T["nf_m0"] = num(lm["nofence:3"]["0"]["resid_med"])
    T["nf_far"] = span(lm["nofence:3"]["3"]["resid_med"], lm["nofence:3"]["7"]["resid_med"])
    ml = dec["model_err_loads"]
    T["loads_within3_pct"] = pct(ml["within3"] / ml["n"])
    T["loads_within3"], T["loads_n"] = num(ml["within3"]), num(ml["n"])
    e = energy["dram_seq"]
    for part in ("rest", "noc", "sram", "minion"):
        T[f"dram_{part}_pct"] = pct(e[part] / e["sp_total"])
    T["dram_nj"] = num(e["sp_total"] / 1000, 1)
    T["dram_host_nj"] = num(e["host_total"] / 1000, 1)
    T["here_pjb"] = num(e["sp_total"] / 64)
    T["here_host_pjb"] = num(e["host_total"] / 64)
    md = manual["dram"]
    T["man_dram"], T["man_dram_lo"], T["man_dram_hi"] = num(md["mean"]), num(md["lo"]), num(md["hi"])
    T["man_dram_line_nj"] = num(md["mean"] * 64 / 1000, 1)
    T["man_zeros"], T["man_random"] = num(manual["dram_zeros"]), num(manual["dram_random"])
    T["hop_pjb"] = num(data["hopPj"] / 64, 1)
    legs = [12 * (abs(g.MESH[h][0] - p[0]) + abs(g.MESH[h][1] - p[1])) for h in range(32) for p in [dec["ms_pos"][str(h & 7)]]]
    T["ms_leg"] = span(min(legs), max(legs))
    dev = max(abs(v["fast_med"] - v["model"]) for v in dec["mem_by_home"].values())
    T["home_dev_max"] = f"{num(dev)} cycle" + ("" if rnd(dev) == 1 else "s")

    tpl = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "report_template.html")).read()
    out = re.sub(r"@@(\w+)@@", lambda m: T[m.group(1)], tpl)
    left = re.findall(r"@@\w*@@", out)
    if left:
        raise SystemExit(f"unfilled: {left}")
    unused = [k for k in T if f"@@{k}@@" not in tpl]
    if unused:
        raise SystemExit(f"computed but not used in the template: {unused}")
    open(sys.argv[3], "w").write(out.replace("__DATA__", json.dumps(data, separators=(",", ":"))))
    print(f"wrote {sys.argv[3]}; hop energy {data['hopPj']:.1f} pJ over {far:.3f} hops")


if __name__ == "__main__":
    main()
