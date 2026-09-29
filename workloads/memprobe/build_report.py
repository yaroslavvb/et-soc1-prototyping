#!/usr/bin/env python3
"""Fill report_template.html with the numbers from analyze.py's summary.json and the energy manual's manual.json.

    build_report.py docs/reports/data/2026-09-19-memprobe-aifoundry2/summary.json \
        docs/reports/data/2026-09-23-energy-manual/manual.json docs/reports/2026-09-19-et-soc1-memory-anatomy.html \
        [--v3 docs/reports/data/2026-09-26-memprobe-3cards/cards.json]

The page script gets the data as D (__DATA__). Numbers that the prose quotes are filled in here, at build time,
from the same files (@@name@@ in the template), so they are in the page without JavaScript; any @@name@@ left
unfilled stops the build. --v3 (default: the path above) is the version-3 claims check's passes on
every card, reduced by `analyze.py --v3` (its docstring has the command); the page puts each card's latencies beside
the 19 September session's (D.v3) and quotes them in the prose (@@v3_...@@).

Every energy on the page (§1's explorer, §6, the DRAM figure at the top) is the energy manual's (its §4), read from
manual.json for every card it carries (in the chart toolkit's registry order); all of it is the version-3 check's,
at 600 MHz (since 28 September; until then §6 showed this page's 19 September runs, summary.json's power, which now
feeds only the note on how those first runs were measured):
    reruns.levels_pj_per_byte.<l2|l3|dram>             the levels: 1 KB tensor loads over a working set sized to each
    reruns.levels_by_contents_pj_per_byte.<d>.<scp>    level (the manual's §4.2), and the scratchpads by their contents
    catalogue.combined[<config>]                       the catalogue (§4.1, §4.3), pooled over passes and cards: the L1
                                                       (flw.ps), the L3 read through the mesh, DRAM tensor loads, rows
    catalogue.cards.<card>.summary[<config>]           each card's paths for §6's chart: energy per byte, and the power
                                                       over idle and on each metered rail (rails_over_w, over_idle_w)
    catalogue.cards.<card>.wire.<d>.slope_pj_per_byte_per_hop   the energy of a mesh hop (the fit over 1-8 hops)
    unmetered.<card>.coef                              the fit of the power on no metered rail (the manual's §4.5)
    v3.catalogue.dram_rows.<card>.<d>.anova_p          the version-3 test that no DRAM row pattern costs more
The prose's qualitative claims about these data are checked here, and the build stops if the data stop bearing them out.
"""
import argparse
import json
import os
import re
import statistics as st
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import gen_ops as g  # noqa: E402

V3_DEFAULT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "docs", "reports", "data",
                          "2026-09-26-memprobe-3cards", "cards.json")
# the chart toolkit's card registry order; the cards themselves come from the data (any number of them)
REGISTRY = ("aifoundry2", "aifoundry3", "aifoundry1-c1")
LABEL = {"aifoundry1-c1": "aifoundry1's card 1"}  # a card as the prose names it
WORDS = {1: "one", 2: "two", 3: "three", 4: "four", 5: "five", 6: "six", 7: "seven", 8: "eight", 9: "nine"}
MONTHS = ("January", "February", "March", "April", "May", "June", "July", "August", "September", "October",
          "November", "December")
VLOAD_BYTES = 32  # flw.ps loads eight 4-byte lanes; the catalogue gives its energy per instruction
DATA = ("zeros", "random")
RAILS = ("minion", "sram", "noc")  # the three metered rails; the rest of the board is board power less these
# §6's chart: the energy manual's catalogue paths that read each level (§4.1 and §4.3 of the manual), with zeros and
# with random data in the memory read; the page script names them (its PATHS)
PATHS = (("l1", "flw.ps/{}/h2"), ("scp", "tload/scp/{}"), ("l3", "dramrow/stride8K/{}"), ("hop1", "wire/hop1/{}"),
         ("hop3", "wire/hop3/{}"), ("hop6", "wire/hop6/{}"), ("dram", "tload/dram/{}"))


def cards_in(keys):
    """The cards among keys, in registry order, then any others in their own order."""
    keys = list(keys)
    return [c for c in REGISTRY if c in keys] + [k for k in keys if k not in REGISTRY]


def all_cards(n):
    return "both cards" if n == 2 else f"all {WORDS.get(n, n)} cards"


def and_list(xs):
    xs = list(xs)
    return xs[0] if len(xs) == 1 else ", ".join(xs[:-1]) + " and " + xs[-1]


def pjb(x, like=None):
    """Energy per byte as the energy manual prints it: two decimals below 10 pJ/B, one from 10 (like: a range's
    bounds take their mean's precision)."""
    return f"{x:,.{2 if (x if like is None else like) < 10 else 1}f}"


def per_line(x):
    """Energy per 64-byte line from pJ per byte: pJ below 500, then nJ (two decimals below 1 nJ, one from it)."""
    e = 64 * x
    return f"{rnd(e):,} pJ" if e < 500 else f"{e / 1000:.{2 if e < 1000 else 1}f} nJ"


def entry(v, scale=1.0):
    """A manual entry {mean, lo, hi, n, per_card: {card: {mean, ...}}}, scaled, with each card's mean only."""
    return {"mean": v["mean"] * scale, "lo": v["lo"] * scale, "hi": v["hi"] * scale, "n": v["n"],
            "per_card": {c: v["per_card"][c]["mean"] * scale for c in cards_in(v["per_card"])}}


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


def v3_data(path):
    """Each card's version-3 passes (analyze.py --v3), per level and home shire: the median over the passes of each
    pass's median, and the passes' lowest and highest."""
    v3 = json.load(open(path))
    out = {}
    for card, c in v3["cards"].items():
        mm = lambda v: {"med": st.median(v), "min": min(v), "max": max(v)}  # noqa: E731
        out[card] = {"passes": c["passes"], "ladder": {k: mm(v) for k, v in c["ladder"].items()},
                     "l3": {s: dict(mm(x["med"]), hops=x["hops"]) for s, x in c["l3_by_slice"].items()},
                     "memByHome": {s: mm(v) for s, v in c.get("mem_by_home", {}).items()},
                     "dramMed": c["dram_med"], "modelErr": c["model_err"],
                     "within3": [sum(a for a, _ in c["within3"]), sum(n for _, n in c["within3"])],
                     # each pass's locked loop (§5's lock chart): its refresh period beside it
                     "locked": [dict(x, R=r) for x, r in zip(c["locked"], c["period"])]}
    return v3, out


def energy_data(man):
    """§1's explorer, §6 and the DRAM figure at the top: the energy manual's energies (manual.json, the fields the
    module docstring lists), as the page script's data (levels, paths, hop) and the numbers the prose quotes."""
    lv, lbc = man["reruns"]["levels_pj_per_byte"], man["reruns"]["levels_by_contents_pj_per_byte"]
    cb, cc = man["catalogue"]["combined"], man["catalogue"]["cards"]
    # every level's energy per byte, pooled over passes and cards, with each card's mean: the levels (§4.2; the
    # L2, L3 and DRAM read with their contents not set) and, with the contents known, the catalogue's (§4.1, §4.3)
    levels = {"l1": entry(cb["flw.ps/random/h2"], 1 / VLOAD_BYTES), "l1_zeros": entry(cb["flw.ps/zeros/h2"], 1 / VLOAD_BYTES),
              **{k: entry(lv[k]) for k in ("l2", "l3", "dram")},
              **{f"{k}_{d}": entry(lbc[d][src]) for k, src in (("scp", "scp-local"), ("rscp", "scp-remote")) for d in DATA},
              **{f"{k}_{d}": entry(cb[cfg.format(d)]) for k, cfg in (("l3", "dramrow/stride8K/{}"), ("dram", "tload/dram/{}"))
                 for d in DATA}}
    cards = cards_in(c for c in cc if all(c in v["per_card"] for v in levels.values()))
    # §6's chart: each card's paths, energy per byte, and power over idle on each metered rail (the rest is the board
    # less the three rails)
    paths = {}
    for key, cfg in PATHS:
        paths[key] = {"cards": {}}
        for c in cards:
            paths[key]["cards"][c] = {}
            for d in DATA:
                r = cc[c]["summary"][cfg.format(d)]
                if not r.get("all_600mhz"):
                    raise SystemExit(f"{c} {cfg.format(d)}: not every burst at 600 MHz")
                per_op = r.get("pj_per_byte") is None  # flw.ps: its energy per instruction, a 32-byte load
                paths[key]["cards"][c][d] = {
                    "pjb": r["pj_per_op"]["mean"] / VLOAD_BYTES if per_op else r["pj_per_byte"]["mean"],
                    "gbs": (r["ops_per_s"]["mean"] * VLOAD_BYTES if per_op else r["bytes_per_s"]["mean"]) / 1e9,
                    "w": r["over_idle_w"]["mean"], "rails": {k: r["rails_over_w"][f"{k}_w"]["mean"] for k in RAILS},
                    "n": r["passes"]}
                paths[key]["hops"] = r["hop_distance"]

    def sh(key, c, rail, d="random"):  # a rail's share of a path's power over idle ("rest": on no metered rail)
        r = paths[key]["cards"][c][d]
        return (r["w"] - sum(r["rails"].values())) / r["w"] if rail == "rest" else r["rails"][rail] / r["w"]

    def sp(key, rail, cs=None, d="random"):  # the span of a share over cards, in percent
        v = [100 * sh(key, c, rail, d) for c in (cs or cards)]
        return span(min(v), max(v)) + "%"

    # the energy of a mesh hop: the manual's straight line through another shire's scratchpad at 1-8 hops, per card
    wire = {c: cc[c]["wire"] for c in cards}
    hop = {d: {"mean": st.mean(wire[c][d]["slope_pj_per_byte_per_hop"] for c in cards),
               "per_card": {c: wire[c][d]["slope_pj_per_byte_per_hop"] for c in cards}} for d in DATA}
    fit_hops = sorted(p["hops"] for p in wire[cards[0]]["random"]["points"])
    unm = {c: man["unmetered"][c]["coef"] for c in cards}

    # ---- the prose's qualitative claims, checked on every card and operand set ----
    for c in cards:
        for d in DATA:
            m = lambda k: sh(k, c, "minion", d)  # noqa: E731
            n = lambda k: sh(k, c, "noc", d)  # noqa: E731
            if not (m("l1") > m("scp") > m("l3") > m("dram") and m("hop1") > m("hop3") > m("hop6")):
                raise SystemExit(f"{c} {d}: the cores' share no longer falls level by level")
            # "the mesh rail appears once the bytes cross the mesh and grows with each hop": a few percent at most
            # inside a shire, a fifth or more once the bytes cross the mesh
            if not (n("hop1") < n("hop3") < n("hop6") and max(n("l1"), n("scp")) < 0.05
                    and min(n("l3"), n("hop1")) > 0.2):
                raise SystemExit(f"{c} {d}: the mesh rail no longer appears only once the bytes cross the mesh")
            if max(RAILS + ("rest",), key=lambda k: sh("scp", c, k, d)) != "sram":
                raise SystemExit(f"{c} {d}: the SRAM rail no longer carries most of a scratchpad read")
            if max(RAILS + ("rest",), key=lambda k: sh("dram", c, k, d)) != "rest":
                raise SystemExit(f"{c} {d}: no metered rail no longer carries most of a DRAM read")
    # One card puts less of a scratchpad read on its SRAM rail and more on no metered rail, and the unmetered fit
    # shows why: on it the unmetered power follows the SRAM rail's (0.54 W per watt, where a regulator's delivery loss
    # is a few percent on the others). The prose names that card; stop if the data no longer single it out.
    odd = [c for c in cards if unm[c]["sram"] > 0.25]
    rest = [c for c in cards if c not in odd]
    if len(odd) != 1 or not rest or not (max(sh("scp", c, "sram") for c in odd) < min(sh("scp", c, "sram") for c in rest)
                                          and min(sh("scp", c, "rest") for c in odd) > max(sh("scp", c, "rest") for c in rest)):
        raise SystemExit(f"the scratchpad read's split no longer singles out one card by its SRAM coefficient: {unm}")
    dr = man["v3"]["catalogue"]["dram_rows"]
    if not all(dr[c][d]["anova_p"] > 0.01 for c in cards for d in DATA):
        raise SystemExit("a DRAM row pattern now differs from the others at 99% on some card; §6 says none does")

    T = {}
    L = levels
    T["man_n"] = WORDS.get(len(cards), str(len(cards)))
    T["man_mhz"] = num(man["operating_point"]["mhz"])
    _, mo, dd = (int(x) for x in man["v3"]["date"].split("-"))
    T["man_date"], T["man_date_short"] = f"{dd} {MONTHS[mo - 1]}", f"{dd} {MONTHS[mo - 1][:3]}"
    for k, name in (("l1", "e_l1"), ("l2", "e_l2"), ("l3", "e_l3"), ("dram", "e_dram"),
                    ("scp_zeros", "e_scp0"), ("scp_random", "e_scp1"), ("rscp_zeros", "e_rscp0"), ("rscp_random", "e_rscp1"),
                    ("dram_zeros", "e_dram0"), ("dram_random", "e_dram1")):
        T[name] = pjb(L[k]["mean"])
    for k in ("l2", "dram"):
        T[f"e_{k}_range"] = f"{pjb(L[k]['lo'], L[k]['mean'])}–{pjb(L[k]['hi'], L[k]['mean'])}"
    for k in ("l2", "l3", "dram"):
        T[f"e_{k}_line"] = per_line(L[k]["mean"])
    T["e_dram_cards"] = and_list(f"{pjb(L['dram']['per_card'][c])} on {LABEL.get(c, c)}" for c in cards)
    T["lv_passes"] = WORDS.get(L["l2"]["n"] // len(cards), str(L["l2"]["n"] // len(cards)))
    npass = {paths[k]["cards"][c][d]["n"] for k in paths for c in cards for d in DATA}
    T["cat_passes"] = WORDS.get(min(npass), str(min(npass))) if len(npass) == 1 else f"{min(npass)}–{max(npass)}"
    # the L2's arrays and the L1
    T["scp_sram"], T["scp_rest"] = sp("scp", "sram", rest), sp("scp", "rest", rest)
    T["scp_sram_odd"], T["scp_rest_odd"] = sp("scp", "sram", odd), sp("scp", "rest", odd)
    T["scp_cards"] = and_list(LABEL.get(c, c) for c in rest)
    T["odd_card"] = and_list(LABEL.get(c, c) for c in odd)
    T["unm_sram_odd"] = num(unm[odd[0]]["sram"], 2)
    T["unm_sram"] = "–".join(dict.fromkeys(f"{f(unm[c]['sram'] for c in rest):.2f}" for f in (min, max)))
    T["l1_min"], T["scp_min"] = sp("l1", "minion"), sp("scp", "minion")
    # the L3
    T["l3_x_l2"] = num(L["l3"]["mean"] / L["l2"]["mean"], 1)
    T["l3_sram"], T["l3_noc"] = sp("l3", "sram"), sp("l3", "noc")
    T["l3_cards"] = and_list(f"{pjb(L['l3_zeros']['per_card'][c], L['l3_random']['per_card'][c])} and {pjb(L['l3_random']['per_card'][c])}"
                             + (" pJ/B" if i == 0 else "") + f" on {LABEL.get(c, c)}" for i, c in enumerate(cards))
    rz = [L["l3_random"]["per_card"][c] / L["l3_zeros"]["per_card"][c] for c in cards]
    T["l3_rz"] = "–".join(dict.fromkeys(f"{f(rz):.1f}" for f in (min, max)))
    # a mesh hop
    T["hop_r"], T["hop_z"] = (pjb(hop[d]["mean"]) for d in ("random", "zeros"))
    for d, k in (("random", "r"), ("zeros", "z")):
        v = hop[d]["per_card"].values()
        T[f"hop_{k}_span"] = f"{pjb(min(v))}–{pjb(max(v))}"
        T[f"hop_{k}_line"] = num(64 * hop[d]["mean"])
    T["hop_fit"] = f"{fit_hops[0]}–{fit_hops[-1]}"
    hk = [k for k in paths if k.startswith("hop")]
    T["hop_list"] = and_list(str(paths[k]["hops"]) for k in hk)
    T["noc_hops"] = and_list(sp(k, "noc") for k in hk)
    # DRAM
    T["dram_noc"], T["dram_sram"], T["dram_min"] = sp("dram", "noc"), sp("dram", "sram"), sp("dram", "minion")
    T["unm_dram"] = and_list(num(unm[c]["dram_pj_per_byte"], 1) for c in cards) + " pJ per DRAM byte on " + and_list(
        LABEL.get(c, c) for c in cards)
    dl = [100 * unm[c]["minion"] for c in cards]  # the fit's minion coefficient: the regulators' delivery loss
    T["deliv_loss"] = span(min(dl), max(dl)) + "%"
    T["rows_harts"] = num(cc[cards[0]]["summary"]["dramrow2/seq/random"]["participants"])
    for p in ("seq", "rowhit", "rowmiss"):
        T[f"rows_{p}"] = pjb(cb[f"dramrow2/{p}/random"]["mean"])
    # the energy manual's DRAM tensor load (random data): share of its power over idle on no metered rail, per card
    off = [sh("dram", c, "rest") for c in cards]
    T["man_offrail"] = span(100 * min(off), 100 * max(off)) + "%"
    T["man_offrail_kpi"] = f"~{5 * rnd(20 * st.mean(off))}%"  # the KPI's round figure, to the nearest 5%
    T["man_offrail_cards"] = all_cards(len(off))
    data = {"levels": levels, "paths": paths, "cards": cards,
            "hop": {d: dict(hop[d], fit=[fit_hops[0], fit_hops[-1]]) for d in DATA}}
    return data, T


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("summary")
    ap.add_argument("manual")
    ap.add_argument("out")
    ap.add_argument("--v3", default=V3_DEFAULT, help="analyze.py --v3's cards.json")
    args = ap.parse_args()
    sys.argv[1:4] = [args.summary, args.manual, args.out]
    s = json.load(open(sys.argv[1]))
    man = json.load(open(sys.argv[2]))
    v3raw, v3 = v3_data(args.v3)
    ref, dec = s["refresh"], s["decomp"]
    en, T_en = energy_data(man)
    data = {
        "msPos": {int(k): v for k, v in dec["ms_pos"].items()},
        "msConst": dec["ms_const"],
        **en,
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
        "v3": v3,
        # §5's lock chart. The model has four inputs, all this session's refresh series (analyze.py refresh()): the
        # refresh period, the locked loop's open-row load, the activate a refresh adds (the closed- minus the open-row
        # cluster) and the longest wait for a refresh (the slowest load over the closed-row median).
        "lock": {"R": ref["period_cycles"], "open": ref["locked"]["open_med"], "act": ref["closed_minus_open"],
                 "wait": ref["max_wait"], "locked": ref["locked"]},
    }

    # ---- numbers quoted in the prose ----
    T = {}
    life = [x for x in ref["rowlife"] if x["gap"] < 2000]
    a = [sum(x[k] for x in life) for k in ("hit_no_refresh", "n_no_refresh", "hit_refresh", "n_refresh")]
    T.update(rows_hit=num(a[0]), rows_n=num(a[1]), rows_pct=pct(a[0] / a[1]),
             rows_ref_hit=num(a[2]), rows_ref_n=num(a[3]), rows_ref_pct=pct(a[2] / a[3]))
    T["op_cycles"] = num(round(ref["op_cycles"], -1))
    T["probe_ovh"] = num(round(2 * ref["op_cycles"], -1))
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
    # fence, no wait: how often each memory shire's load still found its row open, and how slow the others were
    nd = lm["nodelay:3"]
    share = {m: nd[str(m)]["fast"] / nd[str(m)]["n"] for m in range(8)}
    common, rare = (0, 1, 2, 4), (3, 5, 6, 7)  # the grouping the prose names; stop if the data no longer split so
    if min(share[m] for m in common) <= max(share[m] for m in rare):
        raise SystemExit(f"open-row shares no longer split into {common} and {rare}: {share}")
    for key, grp in (("nd_open_common", common), ("nd_open_rare", rare)):
        T[key] = f"{sum(nd[str(m)]['fast'] for m in grp)} of {sum(nd[str(m)]['n'] for m in grp)}"
    T["nd_slow_med"] = num(s["ladder_slow"]["nodelay:3"]["resid_med"])
    T["nf_resid"] = num(s["ladder_slow"]["nofence:3"]["resid_med"])  # every no-fence load over the §4 model, median
    T["nf_m0"] = num(lm["nofence:3"]["0"]["resid_med"])
    T["nf_far"] = span(lm["nofence:3"]["3"]["resid_med"], lm["nofence:3"]["7"]["resid_med"])
    ml = dec["model_err_loads"]
    T["loads_within3_pct"] = pct(ml["within3"] / ml["n"])
    T["loads_within3"], T["loads_n"] = num(ml["within3"]), num(ml["n"])
    T.update(T_en)  # §1's explorer, §6 and the DRAM figure at the top: the energy manual's (energy_data)
    # §6's note on the first measurement (19 September, aifoundry2): the host's board-power log against the rail
    # trace, run by run (two runs per pattern), the one number from those runs the page keeps, for what it says about
    # the meters
    exc = [(r["board_run"] - r["board_base"]) / (r["system_run"] - r["system_base"]) - 1
           for v in s["power"].values() for r in v["reps"]]
    T["host_excess"] = span(100 * min(exc), 100 * max(exc)) + "%"
    T["power_runs"] = num(len(exc))
    T["idle_slope"] = num(man["rest"]["lambda_80_w_per_c"], 2)  # the idle law's slope at 80 C (aifoundry2)
    T["idle_leak80"] = span(*man["rest"]["profile"]["A_leak_80_w"])  # its leakage at 80 C over the e-foldings that fit
    # the same law fitted to each other card's version-3 idle cycles (T_L held), its slope at 80 C
    pcr = man["rest"].get("per_card", {})
    T["idle_slope_cards"] = and_list(f"{num(pcr[c]['lambda_80_w_per_c'], 2)} W per °C on {LABEL.get(c, c)}" for c in cards_in(pcr))
    # the PMIC's running average: its time constant on each card (the energy manual's catalogue bursts)
    rf = man["catalogue"]["rail_filter"]
    T["man_tau"] = and_list(f"{rf[c]['tau_s']:.2f} s on {LABEL.get(c, c)}" for c in cards_in(rf))
    legs = [12 * (abs(g.MESH[h][0] - p[0]) + abs(g.MESH[h][1] - p[1])) for h in range(32) for p in [dec["ms_pos"][str(h & 7)]]]
    T["ms_leg"] = span(min(legs), max(legs))
    dev = max(abs(v["fast_med"] - v["model"]) for v in dec["mem_by_home"].values())
    T["home_dev_max"] = f"{num(dev)} cycle" + ("" if rnd(dev) == 1 else "s")

    # ---- the version-3 check on three cards (26 September), quoted in the prose ----
    C3 = v3raw["cards"]
    cards = list(C3)
    allp = lambda f: [x for c in cards for x in f(C3[c])]  # noqa: E731
    T["v3_n_passes"] = num(sum(len(C3[c]["passes"]) for c in cards))
    T["v3_shift"] = span(*[f(allp(lambda c: c["shift"])) for f in (min, max)])
    T["v3_dram_med"] = span(*[f(allp(lambda c: c["dram_med"])) for f in (min, max)])
    for key, name in (("ladder:1", "l2"), ("ladder:2", "l3"), ("ladder:3", "mem"),
                      ("nofence:3", "nofence"), ("tevict_dirty:3", "dirty")):
        T[f"v3_lad_{name}"] = span(*[f(allp(lambda c: c["ladder"][key])) for f in (min, max)])
    T["v3_ms_const"] = span(*[f(allp(lambda c: c["ms_const"])) for f in (min, max)])
    w3 = {c: v3[c]["within3"][0] / v3[c]["within3"][1] for c in cards}
    T["v3_within3"] = span(100 * min(w3.values()), 100 * max(w3.values())) + "%"
    label = {"aifoundry1-c1": "aifoundry1's card 1"}
    T["v3_within3_cards"] = ", ".join(f"{pct(w3[c])} on {label.get(c, c)}" for c in cards)
    rows = {c: C3[c]["rows"] for c in cards}
    T["v3_rows_pct"] = span(*[f(100 * r[0] / r[1] for r in rows.values()) for f in (min, max)]) + "%"
    T["v3_rows_ref_pct"] = span(*[f(100 * r[2] / r[3] for r in rows.values()) for f in (min, max)]) + "%"
    T["v3_closed_open"] = "–".join(f"{f(allp(lambda c: c['closed_minus_open'])):.1f}" for f in (min, max))
    lk = allp(lambda c: c["locked"])
    T["v3_locked_slow"] = "–".join(f"{f(100 * x['slow'] / x['n'] for x in lk):.1f}" for f in (min, max)) + "%"
    T["v3_locked_inref"] = f"{sum(x['in_refresh'] for x in lk):,} of {sum(x['slow'] for x in lk):,}"
    T["v3_locked_slow_med"] = span(min(x["slow_med"] for x in lk), max(x["slow_med"] for x in lk))
    T["v3_locked_max"] = num(max(x["max"] for x in lk))
    T["v3_op_cycles"] = span(*[f(allp(lambda c: c["op_cycles"])) for f in (min, max)])

    # ---- §5's lock: four turns of the locked loop whose loads find the row open fall short of the refresh period,
    # and the slow load (the first after each refresh) makes up the difference: slow - open = R - 4 x open turn ----
    lk19, R = ref["locked"], ref["period_cycles"]
    T["lock_p"], T["lock_open"], T["lock_slow"] = num(lk19["period_open_med"]), num(lk19["open_med"]), num(lk19["slow_med"])
    T["lock_4p"] = num(4 * lk19["period_open_med"])
    T["lock_short"] = num(R - 4 * lk19["period_open_med"], 1)
    T["lock_act"] = num(ref["closed_minus_open"], 1)
    T["lock_rest"] = num(lk19["slow_med"] - lk19["open_med"] - ref["closed_minus_open"])
    T["lock_max"] = num(lk19["max"])
    T["lock_every4"] = f"{lk19['every4']:,} of {lk19['gaps']:,}"
    v3l = [dict(x, R=r) for c in cards for x, r in zip(C3[c]["locked"], C3[c]["period"])]
    T["v3_lock_p"] = span(*[f(x["period_open_med"] for x in v3l) for f in (min, max)])
    T["v3_lock_short"] = span(*[f(x["R"] - 4 * x["period_open_med"] for x in v3l) for f in (min, max)])
    T["v3_lock_extra"] = span(*[f(x["slow_med"] - x["open_med"] for x in v3l) for f in (min, max)])
    T["v3_lock_every4"] = "–".join(f"{f(100 * x['every4'] / x['gaps'] for x in v3l):.1f}" for f in (min, max)) + "%"
    fit = max(abs((x["slow_med"] - x["open_med"]) - (x["R"] - 4 * x["period_open_med"])) for x in v3l + [dict(lk19, R=R)])
    if fit >= 1:  # the prose says the law holds within a cycle in every series
        raise SystemExit(f"slow - open no longer equals R - 4 x the open turn within a cycle: {fit}")
    T["lock_fit"] = num(fit, 1)

    tpl = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "report_template.html")).read()
    out = re.sub(r"@@(\w+)@@", lambda m: T[m.group(1)], tpl)
    left = re.findall(r"@@\w*@@", out)
    if left:
        raise SystemExit(f"unfilled: {left}")
    unused = [k for k in T if f"@@{k}@@" not in tpl]
    if unused:
        raise SystemExit(f"computed but not used in the template: {unused}")
    open(sys.argv[3], "w").write(out.replace("__DATA__", json.dumps(data, separators=(",", ":"))))
    print(f"wrote {sys.argv[3]}; the energy manual's levels on {T['man_n']} cards: L1 {T['e_l1']}, L2 {T['e_l2']}, "
          f"L3 {T['e_l3']}, DRAM {T['e_dram']} pJ/B")


if __name__ == "__main__":
    main()
