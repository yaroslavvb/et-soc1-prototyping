#!/usr/bin/env python3
"""EXPERIMENT nocr: reduce the passes of one card and apply the registered decision rules (PREREG.md).

  python3 tools/claims-v3/nocr/reduce.py build/claims-v3/<card>/nocr [--passes 1,2,3] [--out summary.json]

Reads p<pass>/r31/{mesh,master}.jsonl with their .bin/.json/.u32 files and p<pass>/r32/r32-*.jsonl. Without
--passes it takes every pass whose block.json says ok, except the smoke (9). Within a pass it keeps only launches
the host reported ok, from processes whose clock read 600 MHz just before them (PREREG.md, "Data kept"). Prints the
theory table (each row keyed by its P number); --out also writes every number. No device access.
"""
import argparse
import json
import os
import re
import statistics as stt
import struct
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "workloads", "nocroute"))
import meshmap as mm  # noqa: E402

PARAMS = json.load(open(os.path.join(HERE, "params.json")))
D = PARAMS["decision"]
SC, MS, NOP, SELF, BAD = 1, 2, 3, 0xFF, 0xFFFFFFFF


def med(v):
    return stt.median(v) if v else None


def q10(v):
    """The 10th percentile (the nearest rank below): reported beside the medians, never decided on. The master's
    stats worker samples every shire's counters once a millisecond and can delay a call; the low quantile is the
    least disturbed."""
    if not v:
        return None
    w = sorted(v)
    return w[int(0.1 * (len(w) - 1))]


def ols(xs, ys):
    n = len(xs)
    if n < 3:
        return None
    mx, my = sum(xs) / n, sum(ys) / n
    sxx = sum((x - mx) ** 2 for x in xs)
    if sxx == 0:
        return None
    s = sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / sxx
    c = my - s * mx
    res = [y - (c + s * x) for x, y in zip(xs, ys)]
    ss = sum((y - my) ** 2 for y in ys)
    rms = (sum(r * r for r in res) / n) ** 0.5
    return {"const": c, "slope": s, "rms": rms, "max_abs_res": max(abs(r) for r in res),
            "r2": 1 - sum(r * r for r in res) / ss if ss else None, "n": n}


def check_marty():
    """The map copied into meshmap.py must equal workloads/nocbench/analyze.py's."""
    path = os.path.join(ROOT, "workloads", "nocbench", "analyze.py")
    if not os.path.exists(path):
        return None
    src = open(path).read()
    m = re.search(r"MARTY = (\{.*?\n\})", src, re.S)
    e = re.search(r"EMPTY = (\[.*?\])", src)
    return m and e and eval(m.group(1)) == mm.MARTY and eval(e.group(1)) == mm.EMPTY


def nocr_lines(path):
    out = []
    if os.path.exists(path):
        for line in open(path):
            if line.startswith("NOCR "):
                out.append(json.loads(line[5:]))
    return out


# ---------------------------------------------------------------- R31
def off_clock(pdir):
    """Processes whose clock, read just before them, was not the registered 600 MHz: their data are dropped."""
    out = set()
    path = os.path.join(pdir, "marks.jsonl")
    if os.path.exists(path):
        for line in open(path):
            m = json.loads(line)
            if m.get("ev") == "proc" and m.get("mhz") not in (None, PARAMS["r32"]["clock_mhz"]):
                out.add(m["name"])
    return out


def r31_records(pdir, p):
    """(pass, launch, caller, rep, kind, target, a, b, dt, rv) for every timed, non-warm call of a good caller."""
    recs, notes = [], []
    skip = off_clock(pdir)
    for jl in ("mesh.jsonl", "master.jsonl"):
        if f"r31-{jl.split('.')[0]}" in skip:
            notes.append(f"p{p} r31-{jl.split('.')[0]}: dropped, clock not 600 MHz")
            continue
        for L in nocr_lines(os.path.join(pdir, "r31", jl)):
            if L.get("test") != "mesh":
                continue
            name = L["name"]
            if not L.get("ok"):      # the registered rule: only launches the host reported ok
                notes.append(f"p{p} {name}: launch not ok: dropped")
                continue
            base = os.path.join(pdir, "r31", name)
            meta = json.load(open(base + ".json"))
            raw = open(base + ".bin", "rb").read()
            ents = struct.unpack(f"<{len(raw) // 8}Q", raw)
            n = len(ents)
            u = open(base + ".u32", "rb").read()
            res = struct.unpack(f"<{len(u) // 4}I", u)
            for pc in L["per_caller"]:
                if not pc.get("ok"):
                    notes.append(f"p{p} {name}: caller {pc['shire']} not ok (err {pc.get('err')})")
                    continue
                s, slot = pc["shire"], pc["slot"]
                for i, e in enumerate(ents):
                    if meta["rep"][i] < meta["warm_reps"]:
                        continue
                    dt, rv = res[(slot * n + i) * 2], res[(slot * n + i) * 2 + 1]
                    if dt == BAD:
                        continue
                    k, ident, a, b = e & 0xFF, (e >> 8) & 0xFF, (e >> 16) & 0xFF, (e >> 24) & 0xFF
                    tgt = s if ident == SELF else ident
                    recs.append((p, name, s, meta["rep"][i], k, tgt, a, b, dt, rv))
    return recs, notes


def group(recs, pred, stat=med):
    g = {}
    for r in recs:
        if pred(r):
            g.setdefault((r[2], r[5]), []).append(r[8])
    return {k: stat(v) for k, v in g.items()}


def place(ys, s, cells, free_const=True, const=None):
    """ys: {caller: cycles}. Rank candidate cells by rms of ys - (C + s * hops(caller, cell))."""
    out = []
    for cell in cells:
        hs = {c: mm.hops(mm.MARTY[c], cell) for c in ys}
        C = sum(ys[c] - s * hs[c] for c in ys) / len(ys) if free_const else const
        rms = (sum((ys[c] - C - s * hs[c]) ** 2 for c in ys) / len(ys)) ** 0.5
        out.append({"cell": list(cell), "const": C, "rms": rms})
    out.sort(key=lambda r: r["rms"])
    return out


def reduce_r31(recs):
    R = {}
    null_sc = group(recs, lambda r: r[4] == SC and r[7] == 7)
    null_ms = group(recs, lambda r: r[4] == MS and r[6] == 7)
    nop = [r[8] for r in recs if r[4] == NOP]
    sc0 = group(recs, lambda r: r[4] == SC and r[7] == 0 and r[5] < 32 and r[1].startswith("mesh"))
    sc3 = group(recs, lambda r: r[4] == SC and r[7] == 3 and r[5] < 32)
    ms0 = group(recs, lambda r: r[4] == MS and r[6] == 0)
    m32 = group(recs, lambda r: r[4] == SC and r[7] == 0 and r[5] == 32)
    R["counts"] = {"calls": len(recs), "sc_pmc0_pairs": len(sc0), "sc_pmc3_pairs": len(sc3), "ms_pairs": len(ms0),
                   "master_callers": len(m32)}
    R["nop_median"] = med(nop)
    # return values: the null calls return PMU_INCORRECT_COUNTER (0xffffffff in the low 32 bits); real reads do not
    nulls = [r[9] for r in recs if (r[4] == SC and r[7] == 7) or (r[4] == MS and r[6] == 7)]
    reads = [r[9] for r in recs if (r[4] == SC and r[7] == 0) or (r[4] == MS and r[6] == 0)]
    R["rv_check"] = {"null_all_incorrect_counter": all(v == BAD for v in nulls),
                     "reads_never_incorrect_counter": all(v != BAD for v in reads)}
    if null_sc:
        v = [null_sc[k] for k in null_sc]
        R["null_sc"] = {"median": med(v), "spread": max(v) - min(v), "per_caller": {str(k[0]): null_sc[k] for k in null_sc}}
    if null_ms:
        v = [null_ms[k] for k in null_ms]
        R["null_ms"] = {"median": med(v), "spread": max(v) - min(v)}
    # the caller's own bank (hop 0) may be reached without its router: it stays out of every per-hop fit and its
    # offset from the line is reported on its own
    pairs = sorted(k for k in sc0 if k[0] != k[1])
    xs = [mm.hops(c, t) for c, t in pairs]
    fit0 = ols(xs, [sc0[k] for k in pairs])
    R["fit_sc_pmc0"] = fit0
    selfs = [sc0[k] for k in sc0 if k[0] == k[1]]
    if fit0 and selfs:
        R["self_offset_cycles"] = med(selfs) - fit0["const"]
    sc0_q = group(recs, lambda r: r[4] == SC and r[7] == 0 and r[5] < 32 and r[1].startswith("mesh"), q10)
    R["fit_sc_pmc0_q10"] = ols([mm.hops(c, t) for c, t in pairs], [sc0_q[k] for k in pairs])
    p3 = sorted(k for k in sc3 if k[0] != k[1])
    R["fit_sc_pmc3"] = ols([mm.hops(c, t) for c, t in p3], [sc3[k] for k in p3])
    # The compiled firmware (objdump of MachineMinion.elf): pmc 0 = 2 loads + 2 stores, SC pmc 3 = 1 load + 1 store,
    # pmc 7 = none. So pmc 0 - pmc 3 and pmc 3 - null are each one load plus one store: their slopes must agree.
    both = [k for k in pairs if k in sc3]
    R["fit_pmc0_minus_pmc3"] = ols([mm.hops(c, t) for c, t in both], [sc0[k] - sc3[k] for k in both])
    if null_sc:
        wn = [k for k in p3 if (k[0], k[0]) in null_sc]
        R["fit_pmc3_minus_null"] = ols([mm.hops(c, t) for c, t in wn], [sc3[k] - null_sc[(k[0], k[0])] for k in wn])
    # the hub alternative: an additive caller + target model with no distance term
    if pairs:
        cs, ts = sorted({c for c, _ in pairs}), sorted({t for _, t in pairs})
        a = {c: 0.0 for c in cs}
        b = {t: med([sc0[(c, t)] for c in cs if (c, t) in sc0]) for t in ts}
        for _ in range(20):
            a = {c: med([sc0[(c, t)] - b[t] for t in ts if (c, t) in sc0]) for c in cs}
            b = {t: med([sc0[(c, t)] - a[c] for c in cs if (c, t) in sc0]) for t in ts}
        res = [sc0[(c, t)] - a[c] - b[t] for c, t in pairs]
        R["additive_rms"] = (sum(r * r for r in res) / len(res)) ** 0.5
    s = fit0["slope"] if fit0 else None
    # shire 32: the constant is free (its bank's ESRs may answer at another speed); only the 36 grid cells can be
    # told apart that way, and the master can only be in one of the four grey ones
    if m32 and s:
        ys = {c: m32[(c, 32)] for c, _ in m32}
        allc = place(ys, s, mm.GRID)
        grey = [r for r in allc if tuple(r["cell"]) in mm.EMPTY]
        free = ols([mm.hops(mm.MARTY[c], tuple(grey[0]["cell"])) for c in ys], [ys[c] for c in ys])
        R["master"] = {"grey_ranking": grey, "best_of_36": allc[:5], "free_slope_at_best": free,
                       "const_minus_compute_const": grey[0]["const"] - fit0["const"]}
    # memory shires: per memory shire with its own constant, then all eight with one common constant
    if ms0 and s:
        per = {}
        for m in range(8):
            ys = {c: ms0[(c, m)] for c, t in ms0 if t == m}
            if len(ys) >= 3:
                per[m] = {"ys": ys, "free": place(ys, s, mm.RING)}
        C = med([per[m]["free"][0]["const"] for m in per]) if per else None
        for _ in range(5):
            for m in per:
                per[m]["joint"] = place(per[m]["ys"], s, mm.RING, free_const=False, const=C)
            C = med([y - s * mm.hops(mm.MARTY[c], tuple(per[m]["joint"][0]["cell"]))
                     for m in per for c, y in per[m]["ys"].items()])
        R["ms_common_const"] = C
        R["ms"] = {str(m): {"joint_best": per[m]["joint"][:3], "free_best": per[m]["free"][:3],
                            "fw_cell": list(mm.FW_MS[m])} for m in per}
        xs2, ys2 = [], []
        for c, m in ms0:
            xs2.append(mm.hops(mm.MARTY[c], mm.FW_MS[m]))
            ys2.append(ms0[(c, m)])
        R["fit_ms_fw_cells"] = ols(xs2, ys2)
    return R


K1 = "P1 T-DIRECT (an ESR call costs a constant plus a term per mesh hop to the target)"
K2 = "P2 T-12 (one ESR load + one store: 12 cycles/hop if stores are posted, 24 if acknowledged)"
K3 = "P3 ESR-STORES (posted, or acknowledged; the latter not separable from 24-cycle loads)"
K4 = "P4 T-NULL (the null call costs the same from every shire)"
K5 = "P5 T-FW-MASTER (shire 32 at (0,3), the top grey cell)"
K6 = "P6 T-FW-MS (memory shires 0-3 at (1..4,-1), 4-7 at (1..4,6))"
K6b = "P6b memory shire 2 at (3,-1)"
K7 = "P7 T-SAME-SLOPE (memory-shire calls cost the same per hop, within 15%)"


def r31_verdicts(R):
    V = {}
    f = R.get("fit_sc_pmc0")
    if not f:
        return {"R31": "no data"}
    s = f["slope"]
    rms_max = max(D["r31_rms_max_cycles"], D["r31_rms_max_frac_of_slope"] * s)
    V[K1] = "survived" if f["r2"] is not None and f["r2"] >= D["r31_r2_min"] and f["rms"] <= rms_max else "refuted"
    ns = R.get("null_sc")
    if ns:
        V[K4] = "survived" if ns["spread"] <= D["r31_null_spread_max_cycles"] else "refuted"
    if V[K1] != "survived":
        # without a per-hop law the slopes and the places mean nothing: say so rather than refute them
        for k in (K2, K3, K5, K6, K6b, K7):
            V[k] = "not decided (T-DIRECT refuted)"
        V["hub-rms (additive caller + target model against the hop law)"] = (
            f"{R.get('additive_rms', float('nan')):.1f} vs {f['rms']:.1f}")
        return V
    a, b = R.get("fit_pmc0_minus_pmc3"), R.get("fit_pmc3_minus_null")
    if not a or not b:
        V[K2] = V[K3] = "not tested"
    else:
        tol = max(D["r31_pair_consistency"]["abs_cycles"], D["r31_pair_consistency"]["rel"] * abs(b["slope"]))
        same = abs(a["slope"] - b["slope"]) <= tol
        V["access-check (pmc 0 - pmc 3 and pmc 3 - null: one load + one store each in the compiled firmware)"] = (
            f"{'agree' if same else 'DIFFER'}: {a['slope']:.2f} and {b['slope']:.2f} cycles/hop (tolerance {tol:.2f})")
        if not same:
            why = (f"not decided (this card's firmware does not make the compiled code's accesses: pmc 0 - pmc 3 "
                   f"{a['slope']:.2f}/hop, pmc 3 - null {b['slope']:.2f}/hop)")
            V[K2] = V[K3] = why
        else:
            sp = b["slope"]
            lo_p, hi_p = D["r31_pair_slopes"]["posted"]
            lo_a, hi_a = D["r31_pair_slopes"]["acked"]
            posted, acked = lo_p <= sp <= hi_p, lo_a <= sp <= hi_a
            V[K2] = "survived" if posted or acked else "refuted"
            V[K3] = ("posted (a store adds no per-hop cost)" if posted else
                     "acked (a store waits for its round trip; or loads at 24/hop with posted stores)" if acked else
                     "neither")
    margin = D["r31_margin_frac_of_slope"] * s
    place_ok = D["r31_place_rms_max_frac_of_slope"] * s
    m = R.get("master")
    if m:
        g = m["grey_ranking"]
        ok = g[0]["rms"] <= max(place_ok, 6) and g[1]["rms"] - g[0]["rms"] >= margin
        cell = tuple(g[0]["cell"])
        V[K5] = "survived" if ok and cell == mm.FW_MASTER else "refuted" if ok else "not decided"
        V["master-placed"] = f"{cell} (rms {g[0]['rms']:.1f}, next {tuple(g[1]['cell'])} rms {g[1]['rms']:.1f})"
    ms = R.get("ms")
    if ms:
        placed, fw_all, all_ok, notes = {}, True, True, []
        for k, v in sorted(ms.items(), key=lambda kv: int(kv[0])):
            j = v["joint_best"]
            ok = j[0]["rms"] <= max(place_ok, 6) and j[1]["rms"] - j[0]["rms"] >= margin
            cell = tuple(j[0]["cell"])
            placed[k] = cell if ok else None
            all_ok &= ok
            fw_all &= ok and cell == tuple(v["fw_cell"])
            notes.append(f"ms{k}->{cell if ok else 'undecided'}")
        V[K6] = "survived" if fw_all else "refuted" if all_ok else "not decided"
        V["ms-placed"] = ", ".join(notes)
        if "2" in ms:
            V[K6b] = ("survived" if placed.get("2") == (3, -1) else "refuted" if placed.get("2") else "not decided")
        fm = R.get("fit_ms_fw_cells")
        if fm:
            V[K7] = "survived" if abs(fm["slope"] / s - 1) <= D["r31_ms_slope_rel_tol"] else "refuted"
    return V


# ---------------------------------------------------------------- R32
def r32_ratios(pdirs, sets):
    """rho per set, mode and pass: sum of the set's flows' bytes per cycle over the sum of the same flows alone,
    in the same repeat (process); the pass value is the median over its repeats."""
    by_name = {s["name"]: s for s in sets["sets"]}
    out = {}
    for p, pdir in pdirs:
        d = os.path.join(pdir, "r32")
        if not os.path.isdir(d):
            continue
        skip = off_clock(pdir)
        for fn in sorted(os.listdir(d)):
            m = re.match(r"r32-(read|write)-(\d+)\.jsonl$", fn)
            if not m or fn[:-6] in skip:
                continue
            mode, rep = m.group(1), int(m.group(2))
            solo, setv = {}, {}
            for L in nocr_lines(os.path.join(d, fn)):
                if L.get("test") != mode:
                    continue
                if not L.get("ok"):      # the registered rule: a launch the host reported not ok is dropped
                    out.setdefault(mode + "_dropped", []).append(f"p{p} {fn[:-6]} {L.get('label')}")
                    continue
                fl = {f"{f['src']}>{f['dst']}": f["bpc"] for f in L["flows"] if f["minions"] == 32 and not f["errs"]}
                kind, name = L["label"].split(":", 1)
                if kind == "solo":
                    solo.update(fl)
                else:
                    setv[name] = fl
            for name, fl in setv.items():
                if name not in by_name:
                    continue
                prs = by_name[name]["pairs"].split(",")
                if not all(q in fl and q in solo for q in prs):
                    continue
                rho = sum(fl[q] for q in prs) / sum(solo[q] for q in prs)
                e = out.setdefault(mode, {}).setdefault(name, {}).setdefault(p, {"reps": [], "gbs": [], "flows": []})
                e["reps"].append(rho)
                e["gbs"].append(sum(fl[q] for q in prs) * PARAMS["r32"]["clock_mhz"] / 1000)
                e["flows"].append({q: fl[q] / solo[q] for q in prs})
            for q, v in solo.items():
                out.setdefault(mode + "_solo_gbs", {}).setdefault(q, []).append(v * PARAMS["r32"]["clock_mhz"] / 1000)
    return out


def r32_verdict(rows, sets):
    """rows: {set name: pooled rho}. Returns (verdict, detail). Every family shares a link under both dimension
    orders, on replies (data) under one and on requests (control packets) under the other, so the order is read
    from the CONTRAST between the mirrored families: the one whose data share falls further (a control packet never
    costs more than the data it stands for, c <= 1)."""
    info = {s["name"]: s for s in sets["sets"]}
    hold = lambda n: rows.get(n) is not None and rows[n] >= D["r32_hold_min"]
    drop = lambda n: rows.get(n) is not None and rows[n] <= D["r32_drop_max"]
    fam = [n for n, s in info.items() if s["kind"] == "family" and n in rows]
    rowsets = [n for n in fam if info[n]["share_order"] == "xy"]
    colsets = [n for n in fam if info[n]["share_order"] == "yx"]
    negs = [n for n, s in info.items() if s["kind"] == "negative" and n in rows]
    poss = [n for n, s in info.items() if s["kind"] == "positive" and n in rows]
    k5 = lambda names: [n for n in names if info[n]["k"] == 5]
    if not fam or not negs:
        return "no data", {}
    row5, col5 = k5(rowsets), k5(colsets)
    cmin = D["r32_contrast_min"]
    det = {"negatives_hold": all(hold(n) for n in negs), "positives_drop": [n for n in poss if drop(n)],
           "row_sets_dropping": [n for n in rowsets if drop(n)], "col_sets_dropping": [n for n in colsets if drop(n)],
           "contrast_cols_over_rows": (min(rows[n] for n in col5) - max(rows[n] for n in row5)) if row5 and col5 else None}
    if not det["negatives_hold"]:
        return "invalid (a negative control fell: something other than shared links slows concurrent flows)", det
    con = det["contrast_cols_over_rows"]
    if row5 and all(drop(n) for n in row5) and (all(hold(n) for n in colsets) or (con is not None and con >= cmin)):
        v = "xy"
    elif col5 and all(drop(n) for n in col5) and (all(hold(n) for n in rowsets) or (con is not None and -con >= cmin)):
        v = "yx"
    elif all(hold(n) for n in fam + poss):
        v = "wide (no link saturated: the order is not identified)"
    elif any(drop(n) for n in row5) and any(drop(n) for n in col5):
        v = "not identified (both families fall alike: control packets as costly as data, or adaptive routing)"
    else:
        v = "ambiguous"
    # within a family place, rho should not rise with k
    mono = {}
    for s in sets["sets"]:
        if s["kind"] != "family":
            continue
        mono.setdefault(s["family"], []).append((s["k"], rows.get(s["name"])))
    det["monotone"] = {f: all(b[1] is None or a[1] is None or b[1] <= a[1] + D["r32_monotone_tol"]
                              for a, b in zip(sorted(v), sorted(v)[1:])) for f, v in mono.items()}
    return v, det


def set_demand(sets, name, solo):
    """The sum of a set's flows' solo GB/s (None if a flow has no solo value)."""
    s = next(x for x in sets["sets"] if x["name"] == name)
    v = [solo.get(q) for q in s["pairs"].split(",")]
    return None if any(x is None for x in v) else sum(v)


def reduce_r32(pdirs, sets):
    rat = r32_ratios(pdirs, sets)
    info = {s["name"]: s for s in sets["sets"]}
    R = {}
    for mode in ("read", "write"):
        per = rat.get(mode, {})
        pooled, table = {}, {}
        for name, bypass in per.items():
            pv = {p: med(e["reps"]) for p, e in bypass.items()}
            pooled[name] = med(list(pv.values()))
            table[name] = {"rho_pooled": pooled[name], "rho_per_pass": pv,
                           "set_gbs": med([g for e in bypass.values() for g in e["gbs"]])}
        v, det = r32_verdict(pooled, sets)
        solo = {q: med(g) for q, g in sorted(rat.get(mode + "_solo_gbs", {}).items())}
        R[mode] = {"verdict": v, "detail": det, "sets": table, "solo_gbs": solo,
                   "launches_dropped": rat.get(mode + "_dropped", [])}
        # The link's capacity: the median set GB/s of the sets that fell on a DATA-shared link (every flow of such a
        # set crosses it): the positive controls, and the family whose data share under the identified order; with
        # no order identified, every set that fell (with c = 1 both families fill their link alike).
        fell = [n for n in table if table[n]["rho_pooled"] is not None and table[n]["rho_pooled"] <= D["r32_drop_max"]]
        if v in ("xy", "yx"):
            fell = [n for n in fell if info[n]["kind"] == "positive" or info[n]["share_order"] == v]
        R[mode]["capacity_gbs_from_dropping_sets"] = med([table[n]["set_gbs"] for n in fell])
        R[mode]["k5_demand_gbs"] = {n: set_demand(sets, n, solo) for n in info
                                    if info[n]["kind"] == "family" and info[n]["k"] == 5}
    # A write verdict that says nothing filled ("wide", "ambiguous") counts only if the writes could fill a link: the
    # smallest k = 5 family set's summed solo write bandwidth at least 1.2 x the read-derived capacity (none: it does
    # not count). A write verdict in which sets fell ("xy", "yx", "not identified") shows that something filled, and
    # counts whatever the demand (the request network may be narrower than the reply network).
    w, r = R.get("write"), R.get("read")
    if w and r and w["verdict"] != "no data" and not w["verdict"].startswith("invalid"):
        cap = r["capacity_gbs_from_dropping_sets"]
        dems = [x for x in w["k5_demand_gbs"].values() if x is not None]
        need = D["r32w_power_min"] * cap if cap else None
        w["power"] = {"read_capacity_gbs": cap, "min_k5_write_demand_gbs": min(dems) if dems else None, "need_gbs": need}
        filled = w["verdict"] in ("xy", "yx") or w["verdict"].startswith("not identified")
        weak = not filled and ((not dems) or need is None or min(dems) < need)
        if weak:
            w["verdict_unguarded"] = w["verdict"]
            w["verdict"] = ("not decided (no read-derived link capacity, and no write set fell)"
                            if need is None and dems else
                            f"not decided (writes too weak to fill a link: smallest k=5 write demand "
                            f"{min(dems) if dems else float('nan'):.1f} GB/s, needed {need:.1f})"
                            if dems else "not decided (no write solo data)")
    return R


def request_cost(R, sets):
    """P13: c, the link load of a read's request as a fraction of its reply's, from the family whose REQUESTS share
    under the identified order: an estimate (reply-family set GB/s over request-family set GB/s) when its k = 5 sets
    fall too, an upper bound (read capacity over its k = 5 demand) when they hold."""
    r = R.get("read") or {}
    v = r.get("verdict")
    if v not in ("xy", "yx"):
        return "not decided (no reply order identified)", None
    info = {s["name"]: s for s in sets["sets"]}
    t = r["sets"]
    other = "yx" if v == "xy" else "xy"
    rep5 = [n for n in t if info[n]["kind"] == "family" and info[n]["k"] == 5 and info[n]["share_order"] == v]
    req5 = [n for n in t if info[n]["kind"] == "family" and info[n]["k"] == 5 and info[n]["share_order"] == other]
    if not rep5 or not req5:
        return "not decided (missing sets)", None
    rho = [t[n]["rho_pooled"] for n in req5]
    if all(x is not None and x <= D["r32_drop_max"] for x in rho):
        c = med([t[n]["set_gbs"] for n in rep5]) / med([t[n]["set_gbs"] for n in req5])
        return "survived", f"c = {c:.2f} (requests fill the reversed link)"
    cap = r.get("capacity_gbs_from_dropping_sets")
    dem = [r["k5_demand_gbs"].get(n) for n in req5]
    if all(x is not None and x >= D["r32_hold_min"] for x in rho) and cap and all(dem):
        return "not decided", f"c < {cap / min(dem):.2f} (the request family's k=5 sets hold)"
    return "not decided", "c between the rules (request family neither holds nor falls)"


def r32_verdicts(R, sets):
    V = {}
    rd, wr = R.get("read", {}).get("verdict"), R.get("write", {}).get("verdict")
    V["reads (the replies' order)"] = rd
    V["writes (the requests' order)"] = wr
    none = rd in (None, "no data") or rd.startswith("invalid")
    def tv(order):
        if none:
            return "not tested"
        return "survived" if rd == order else "refuted" if rd in ("xy", "yx") else "not decided"
    V["P8 T-XY (replies go x first, as every route on the chip diagram assumes, L104)"] = tv("xy")
    V["P9 T-YX (replies go y first)"] = tv("yx")
    V["P10 T-WIDE (no link saturates at up to 170 GB/s)"] = (
        "not tested" if none else "survived" if rd.startswith("wide") else "refuted")
    V["P11 T-ADAPT (minimal adaptive or mixed routing)"] = (
        "not tested" if none or rd.startswith("wide") else "refuted" if rd in ("xy", "yx") else "not decided")
    if rd in ("xy", "yx") and wr in ("xy", "yx"):
        V["P12 T-SAME-RULE (requests use the replies' order)"] = (
            "survived" if rd == wr else "refuted (opposite order: replies retrace requests)")
    else:
        V["P12 T-SAME-RULE (requests use the replies' order)"] = "not decided"
    v13, c = request_cost(R, sets)
    V["P13 T-REQ (a read's requests load the reversed links, c of a reply each)"] = v13
    if c:
        V["request-cost"] = c
    return V


def reduce_dir(data, passes, sets):
    """Every number and every verdict for the passes [(pass, dir)] of one card."""
    recs, notes = [], []
    for p, d in passes:
        r, n = r31_records(d, p)
        recs += r
        notes += n
    R31 = reduce_r31(recs)
    R32 = reduce_r32(passes, sets)
    V = {**r31_verdicts(R31), **r32_verdicts(R32, sets)}
    return {"data": data, "passes": [p for p, _ in passes], "map_equals_nocbench": bool(check_marty()),
            "notes": notes, "r31": R31, "r32": R32, "theories": V}


# ---------------------------------------------------------------- main
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("data", help="build/claims-v3/<card>/nocr")
    ap.add_argument("--passes", default="")
    ap.add_argument("--out")
    ap.add_argument("--include-smoke", action="store_true")
    g = ap.parse_args()
    passes = []
    for dn in sorted(os.listdir(g.data)):
        m = re.match(r"p(\d+)$", dn)
        if not m:
            continue
        p = int(m.group(1))
        if g.passes and p not in [int(x) for x in g.passes.split(",")]:
            continue
        if not g.passes:
            if p == 9 and not g.include_smoke:
                continue
            bj = os.path.join(g.data, dn, "block.json")
            if not os.path.exists(bj) or json.load(open(bj)).get("status") != "ok":
                continue
        passes.append((p, os.path.join(g.data, dn)))
    if not passes:
        print("no passes to reduce", file=sys.stderr)
        return 1
    sets = json.load(open(os.path.join(HERE, "sets.json")))
    out = reduce_dir(g.data, passes, sets)
    R31, R32, V, notes = out["r31"], out["r32"], out["theories"], out["notes"]
    print(f"nocr: {g.data}, passes {[p for p, _ in passes]}; map equals nocbench's: {out['map_equals_nocbench']}")
    f = R31.get("fit_sc_pmc0")
    if f:
        print(f"R31 SC pmc0 over {f['n']} shire pairs: {f['const']:.1f} + {f['slope']:.2f} x hops cycles, "
              f"rms {f['rms']:.2f}, r2 {f['r2']:.4f}; additive (hub) model rms {R31.get('additive_rms', float('nan')):.2f}")
    for k in ("fit_sc_pmc0_q10", "fit_pmc0_minus_pmc3", "fit_pmc3_minus_null", "fit_ms_fw_cells"):
        if R31.get(k):
            print(f"    {k}: slope {R31[k]['slope']:.2f}/hop, const {R31[k]['const']:.1f}, rms {R31[k]['rms']:.2f}")
    for mode in ("read", "write"):
        r = R32.get(mode)
        if not r:
            continue
        print(f"R32 {mode}: {r['verdict']}; capacity from falling sets {r['capacity_gbs_from_dropping_sets']}"
              + (f"; power {r['power']}" if r.get("power") else "")
              + (f"; launches dropped (not ok): {r['launches_dropped']}" if r.get("launches_dropped") else ""))
        for name, t in sorted(r["sets"].items()):
            rp = t["rho_pooled"]
            if rp is None:
                continue
            print(f"    {name:7s} rho {rp:.3f}  {t['set_gbs']:.1f} GB/s  per pass "
                  + " ".join(f"{v:.3f}" for v in t["rho_per_pass"].values()))
    print("theories:")
    for k, v in V.items():
        print(f"  {k}: {v}")
    for n in notes[:10]:
        print("  note:", n)
    if g.out:
        json.dump(out, open(g.out, "w"), indent=1, default=str)
    return 0


if __name__ == "__main__":
    sys.exit(main())
