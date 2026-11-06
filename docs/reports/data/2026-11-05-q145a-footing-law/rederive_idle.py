#!/usr/bin/env python3
"""heat-q145a, Part 1: the dedicated idle-cycle slopes re-derived by independent code (post hoc; reads committed files only).

Two routes, both written here, importing nothing from the lab repo:
 (1) raw: E44's nine September cycles (aifoundry3, aifoundry2, aifoundry1 card 1) from their committed 10 Hz telemetry, with
     E66's identification rule F (a sample counts if it is at least 20 s after the cycle's cool_start mark and the minion clock
     reads 600 MHz); board_w on temp_c.minshire[0]; one straight line per cycle per band; the band is inclusive of both ends
     (whole degrees, as the firmware reports them).
 (2) tables: E44 (aifoundry3), E66 (aifoundry2, 18 cycles) and E71 (aifoundry3, 6 cycles) from the committed per-degree tables
     (dwell in s at 10 Hz and mean board W per whole degree). Because the die reading is a whole degree, ordinary least squares
     over the samples equals weighted least squares over the per-degree means with weight = sample count, so this reproduces the
     committed per-cycle fits from the tables alone, independently of idle_slope.py.
Also: a smooth law per card from the pooled per-degree means (quadratic, weighted), and its slope at 55-62 C.
The marks' "login" field is never read or printed (it can carry another lab user's login).

    python3 -B rederive_idle.py <lab repo top> <out.json>
"""
import gzip
import json
import os
import sys

import numpy as np

BANDS = [(58, 62), (56, 62), (58, 65), (56, 66), (54, 58), (51, 58)]


def wls(T, W, n):
    T, W, n = np.asarray(T, float), np.asarray(W, float), np.asarray(n, float)
    A = np.c_[T, np.ones_like(T)] * np.sqrt(n)[:, None]
    coef, *_ = np.linalg.lstsq(A, W * np.sqrt(n), rcond=None)
    return float(coef[0]), float(coef[1])


def band_fit_samples(T, W, lo, hi):
    m = (T >= lo) & (T <= hi)
    if m.sum() < 50 or len(set(T[m].tolist())) < 3:
        return {"ok": False, "n": int(m.sum())}
    k, b = np.polyfit(T[m], W[m], 1)
    return {"ok": True, "slope": float(k), "n": int(m.sum()), "span": float(T[m].max() - T[m].min())}


def band_fit_table(pdw, pds, lo, hi):
    Ts = sorted(int(t) for t in pdw)
    sel = [t for t in Ts if lo <= t <= hi]
    n = [round(pds[str(t)] / 0.1) for t in sel]
    if sum(n) < 50 or len(sel) < 3:
        return {"ok": False, "n": int(sum(n))}
    k, b = wls(sel, [pdw[str(t)] for t in sel], n)
    return {"ok": True, "slope": k, "n": int(sum(n)), "span": float(max(sel) - min(sel))}


def raw_cycle(p):
    cool = None
    for line in open(os.path.join(p, "marks.jsonl")):
        m = json.loads(line)
        if m.get("ev") == "cool_start":
            cool = m["t_ms"]
    rows = []
    with gzip.open(os.path.join(p, "telemetry.jsonl.gz"), "rt") as f:
        for line in f:
            line = line.strip()
            if not (line.startswith("{") and line.endswith("}")):
                continue
            try:
                d = json.loads(line)
            except ValueError:
                continue
            t = d.get("t_ms")
            if t is None or cool is None or t < cool + 20000:
                continue
            if (d.get("mhz") or {}).get("minion") != 600:
                continue
            rows.append((float(d["temp_c"]["minshire"][0]), float(d["board_w"]), float(d["die_mv"]["minion"])))
    a = np.array(rows)
    return a


def median_stats(v):
    v = np.array([x for x in v if x is not None], float)
    if not len(v):
        return None
    return {"median": float(np.median(v)), "mean": float(v.mean()), "sd": float(v.std(ddof=1)) if len(v) > 1 else None,
            "min": float(v.min()), "max": float(v.max()), "n": int(len(v))}


def law_from_tables(tabs, lo=50, hi=66):
    """pooled per-degree means over cycles (each cycle's degree mean weighted by its count), quadratic weighted fit"""
    acc = {}
    for pdw, pds in tabs:
        for t, w in pdw.items():
            ti = int(t)
            if lo <= ti <= hi:
                n = round(pds[t] / 0.1)
                s = acc.setdefault(ti, [0.0, 0])
                s[0] += w * n
                s[1] += n
    Ts = sorted(t for t in acc if acc[t][1] >= 100)
    W = [acc[t][0] / acc[t][1] for t in Ts]
    n = [acc[t][1] for t in Ts]
    T = np.array(Ts, float)
    A = np.c_[T * T, T, np.ones_like(T)] * np.sqrt(np.array(n, float))[:, None]
    c, *_ = np.linalg.lstsq(A, np.array(W) * np.sqrt(np.array(n, float)), rcond=None)
    slope = {str(x): float(2 * c[0] * x + c[1]) for x in (52, 55, 56, 57, 58, 59, 60, 61, 62)}
    resid = np.array(W) - (c[0] * T * T + c[1] * T + c[2])
    return {"quad": [float(x) for x in c], "T_range": [int(T.min()), int(T.max())], "degrees": len(Ts),
            "rms_w": float(np.sqrt(np.mean(resid ** 2))), "slope_at": slope}


def main():
    top, out = sys.argv[1], sys.argv[2]
    D = os.path.join(top, "docs/reports/data")
    res = {"what": __doc__.strip().splitlines()[0], "raw_e44": {}, "tables": {}, "laws": {}}
    # (1) raw E44, three cards
    e44 = os.path.join(D, "2026-09-25-claims-v3/raw")
    raw_tabs = {}
    for card in ("aifoundry3", "aifoundry2", "aifoundry1-c1"):
        cyc = {}
        tabs = []
        for p in ("p1", "p2", "p3"):
            a = raw_cycle(os.path.join(e44, card, "idle", p))
            T, W, mv = a[:, 0], a[:, 1], a[:, 2]
            fits = {f"{lo}-{hi}": band_fit_samples(T, W, lo, hi) for lo, hi in BANDS}
            pdw = {str(int(t)): float(W[T == t].mean()) for t in sorted(set(T.tolist()))}
            pds = {str(int(t)): round(float((T == t).sum()) * 0.1, 1) for t in sorted(set(T.tolist()))}
            tabs.append((pdw, pds))
            cyc[p] = {"n": int(len(T)), "T_min": float(T.min()), "T_max": float(T.max()), "minion_mv_mean": float(mv.mean()),
                      "fits": fits}
        raw_tabs[card] = tabs
        summ = {}
        for lo, hi in BANDS:
            ks = [cyc[p]["fits"][f"{lo}-{hi}"].get("slope") for p in cyc if cyc[p]["fits"][f"{lo}-{hi}"]["ok"]]
            summ[f"{lo}-{hi}"] = median_stats(ks)
        res["raw_e44"][card] = {"cycles": cyc, "bands": summ}
    # (2) the committed per-degree tables
    srcs = {"E44_aifoundry3_sep": "2026-10-27-e71-idle-slope-aifoundry3/sep-p1p3.json",
            "E71_aifoundry3": "2026-10-27-e71-idle-slope-aifoundry3/slopes.json",
            "E66_aifoundry2": "2026-10-27-e71-idle-slope-aifoundry3/aifoundry2-58-62.json"}
    tabs_by = {}
    for name, rel in srcs.items():
        j = json.load(open(os.path.join(D, rel)))
        per = {}
        tabs = []
        maxdiff = 0.0
        for p, rec in sorted(j["passes"].items()):
            if not rec.get("usable"):
                continue
            pdw, pds = rec["per_degree_w"], rec["per_degree_s"]
            tabs.append((pdw, pds))
            fits = {}
            for lo, hi in BANDS:
                f = band_fit_table(pdw, pds, lo, hi)
                c = rec["fits"].get(f"{lo}-{hi}", {})
                if f["ok"] and c.get("ok"):
                    f["committed"] = c["slope_w_per_c"]
                    f["diff"] = f["slope"] - c["slope_w_per_c"]
                    maxdiff = max(maxdiff, abs(f["diff"]))
                fits[f"{lo}-{hi}"] = f
            per[p] = fits
        summ = {}
        for lo, hi in BANDS:
            ks = [per[p][f"{lo}-{hi}"].get("slope") for p in per if per[p][f"{lo}-{hi}"]["ok"]]
            summ[f"{lo}-{hi}"] = median_stats(ks)
        res["tables"][name] = {"source": rel, "cycles": len(per), "bands": summ, "max_abs_diff_vs_committed_fit": maxdiff}
        tabs_by[name] = tabs
    # laws per card and source
    res["laws"]["aifoundry3_E71"] = law_from_tables(tabs_by["E71_aifoundry3"])
    res["laws"]["aifoundry3_E44"] = law_from_tables(tabs_by["E44_aifoundry3_sep"])
    res["laws"]["aifoundry2_E66"] = law_from_tables(tabs_by["E66_aifoundry2"])
    res["laws"]["aifoundry1-c1_E44"] = law_from_tables(raw_tabs["aifoundry1-c1"], lo=56, hi=70)
    res["laws"]["aifoundry2_E44"] = law_from_tables(raw_tabs["aifoundry2"], lo=50, hi=70)
    # E97's committed law (from heat_q138t.py's constants) for comparison
    a, b = 0.006175439291277969, -0.3665903970069978
    res["laws"]["aifoundry3_E97_committed"] = {"slope_at": {str(x): 2 * a * x + b for x in (52, 55, 56, 57, 58, 59, 60, 61, 62)}}
    json.dump(res, open(out, "w"), indent=1, sort_keys=True)
    # short printout
    for card, r in res["raw_e44"].items():
        print("raw E44", card, {k: (round(v["median"], 4) if v else None) for k, v in r["bands"].items()},
              "mV", round(np.mean([c["minion_mv_mean"] for c in r["cycles"].values()]), 1),
              "T", min(c["T_min"] for c in r["cycles"].values()), max(c["T_max"] for c in r["cycles"].values()))
    for name, r in res["tables"].items():
        print("table", name, r["cycles"], {k: (round(v["median"], 4) if v else None) for k, v in r["bands"].items()},
              "maxdiff", r["max_abs_diff_vs_committed_fit"])
    for name, r in res["laws"].items():
        print("law", name, {k: round(v, 4) for k, v in r["slope_at"].items()}, r.get("T_range"), r.get("rms_w"))


if __name__ == "__main__":
    main()
