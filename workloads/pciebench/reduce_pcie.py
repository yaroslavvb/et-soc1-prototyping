#!/usr/bin/env python3
"""Reduce the PCIe runs (workloads/pciebench/run_pcie.sh) to per-card values with 99% intervals, and judge the
predictions stated before the runs (docs/reports/data/2026-09-27-pcie/PREREG.md).

    python3 workloads/pciebench/reduce_pcie.py docs/reports/data/2026-09-27-pcie/raw \
        --prereg docs/reports/data/2026-09-27-pcie/PREREG.md --out docs/reports/data/2026-09-27-pcie/pcie.json \
        --md docs/reports/data/2026-09-27-pcie/results.md

raw/<card>/r<k>/{info,bw,lat,launch,conc,hostcopy}.out: lines "PCIE {json}" (host/main.cpp). Runs r1.. are the
schedule; r0 and pilot* are pilots and are left out. The unit of replication is the run: a run's value for a cell
is the median of its repeats, a card's value is the mean over its runs with a 99% t-interval (PREREG.md).
Sizes are binary (1 MB = 2^20 B), bandwidths decimal (GB/s = 1e9 B/s).
"""
import argparse
import glob
import hashlib
import json
import math
import os
import re
import statistics as st
import sys

try:
    from scipy.stats import t as _t

    def tq(df):
        return float(_t.ppf(0.995, df))
except ImportError:  # the 0.995 quantile of Student's t, df 1..10
    _T = [63.657, 9.925, 5.841, 4.604, 4.032, 3.707, 3.499, 3.355, 3.250, 3.169]

    def tq(df):
        return _T[df - 1] if df <= 10 else 2.576

LINK_GBS = 16e9 * 8 * 128 / 130 / 8 / 1e9   # 15.75 GB/s per direction: Gen4 x8 after 128b/130b
CARDS = ["aifoundry2", "aifoundry3", "aifoundry1-c1"]
BIG = 256 << 20


def stat(vals, nd=4):
    """mean and 99% t-interval over runs; the runs' own values kept."""
    v = [x for x in vals if x is not None and not (isinstance(x, float) and math.isnan(x))]
    n = len(v)
    if n == 0:
        return None
    m = st.mean(v)
    if n > 1:
        h = tq(n - 1) * st.stdev(v) / math.sqrt(n)
    else:
        h = float("nan")
    r = lambda x: round(x, nd) if isinstance(x, float) and not math.isnan(x) else x
    return {"mean": r(m), "lo": r(m - h) if n > 1 else None, "hi": r(m + h) if n > 1 else None, "n": n,
            "runs": [r(float(x)) for x in v]}


def read_out(path):
    out = []
    if not os.path.exists(path):
        return out
    for line in open(path):
        if line.startswith("PCIE "):
            out.append(json.loads(line[5:]))
    return out


def med(v):
    return st.median(v) if v else None


def runs_of(raw, card):
    rs = []
    for d in glob.glob(os.path.join(raw, card, "r*")):
        m = re.fullmatch(r"r(\d+)", os.path.basename(d))
        if m and int(m.group(1)) >= 1 and os.path.exists(os.path.join(d, "run.json")):
            rs.append((int(m.group(1)), d))
    return sorted(rs)


def verdict_range(s, lo, hi):
    """PASS: the 99% interval inside [lo, hi]; FAIL: entirely outside; else INCONCLUSIVE."""
    if s is None or s["lo"] is None:
        return "NO DATA"
    if s["lo"] >= lo and s["hi"] <= hi:
        return "PASS"
    if s["hi"] < lo or s["lo"] > hi:
        return "FAIL"
    return "INCONCLUSIVE"


def verdict_positive(s):
    """a predicted positive difference: PASS when the interval excludes 0 above, FAIL when it excludes 0 below."""
    if s is None or s["lo"] is None:
        return "NO DATA"
    if s["lo"] > 0:
        return "PASS"
    if s["hi"] < 0:
        return "FAIL"
    return "INCONCLUSIVE"


def half_size(curve, big):
    """n1/2 in log2(bytes): where the curve (size -> GB/s, ascending sizes) last rises through half its value at `big`,
    interpolated in log2(size)."""
    sizes = sorted(curve)
    half = curve[big] / 2
    i = len(sizes) - 1
    while i > 0 and curve[sizes[i - 1]] >= half:
        i -= 1
    if i == 0:
        return math.log2(sizes[0])
    s0, s1 = sizes[i - 1], sizes[i]
    b0, b1 = curve[s0], curve[s1]
    frac = (half - b0) / (b1 - b0) if b1 != b0 else 1.0
    return math.log2(s0) + frac * (math.log2(s1) - math.log2(s0))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("raw")
    ap.add_argument("--prereg")
    ap.add_argument("--out", required=True)
    ap.add_argument("--md")
    a = ap.parse_args()

    D = {"meta": {"link_gbs": round(LINK_GBS, 4), "link": "PCIe Gen4 (16 GT/s) x8, 128b/130b",
                  "units": "sizes binary (1 MB = 2^20 B); bandwidth GB/s = 1e9 B/s; times in microseconds",
                  "stat": "a run's value is the median of its repeats; a card's value is the mean over runs with a 99% t-interval"},
         "cards": [], "hosts": {}, "bw": {}, "hostcopy": {}, "lat": {}, "launch": {}, "conc": {}, "hist": {}}
    if a.prereg:
        D["meta"]["prereg_sha256"] = hashlib.sha256(open(a.prereg, "rb").read()).hexdigest()
    per_run = {}   # card -> list of per-run dicts, for the predictions
    for card in CARDS:
        rs = runs_of(a.raw, card)
        if not rs:
            continue
        D["cards"].append(card)
        R = []
        host = {"runs": [k for k, _ in rs], "run_times_ms": [], "open_ms": [], "die_c": [], "minion_mhz": [],
                "verify": [], "stream_errors": 0, "exit_codes": {}}
        bw = {}        # (dir, copy) -> size -> [run values GB/s]
        bwfloor = {}
        hc = {}
        lat_rt, lat_fast, lat_sp, lat_pipe, lat_idle = {}, {}, {}, {}, []
        hist_rt, hist_sp = [0] * 40, [0] * 40   # 20 us bins, 0-800 us, pooled 4 KB samples (the last bin holds >= 780)
        ln_single, ln_b2b, ln_first, ln_load, ln_spread = {}, {}, [], [], {}
        conc = {}
        for k, d in rs:
            run = json.load(open(os.path.join(d, "run.json")))
            host["run_times_ms"].append([run["t0_ms"], run["t1_ms"]])
            host["exit_codes"][str(k)] = run["exit"]
            pair = []
            for f in ("pre.json", "post.json"):
                try:
                    tl = json.loads(open(os.path.join(d, f)).read().strip().splitlines()[-1])
                    host["die_c"].append(tl["temp_c"]["minshire"][0])
                    host["minion_mhz"].append(tl["mhz"]["minion"])
                    pair.append(tl["temp_c"]["minshire"][0])
                except Exception:
                    pair.append(None)
            host.setdefault("die_c_by_run", {})[str(k)] = pair
            rv = {"run": k}
            info = read_out(os.path.join(d, "info.out"))
            for x in info:
                if x["test"] == "info":
                    host["dma_max_elem_bytes"] = x["dma_max_elem_bytes"]
                    host["dma_max_elem_count"] = x["dma_max_elem_count"]
                    host["boot_mhz"] = x["frequency_mhz"]
                    host["host_threads"] = x["host_threads"]
                    mine = [l for l in x["link"] if l["cma_allocated"] != "0 MB"]
                    if mine:
                        host["bdf"] = mine[0]["bdf"]
                        host["link_speed"] = mine[0]["speed"]
                        host["link_width"] = int(mine[0]["width"])
                        host["cma"] = mine[0]["cma_allocated"]
            for t in ("info", "bw", "lat", "launch", "conc"):
                for x in read_out(os.path.join(d, t + ".out")):
                    if x["test"] == "open":
                        host["open_ms"].append(x["open_ns"] / 1e6)
                    host["stream_errors"] += x.get("stream_errors", 0)
                    if x["test"] == "verify":
                        host["verify"].append(x["equal"])
                    if x["test"] == "done":
                        host["elapsed_s_max"] = round(max(host.get("elapsed_s_max", 0), x["elapsed_s"]), 3)
                    if x["test"] == "error":
                        host.setdefault("errors", []).append(x)
            # bandwidth sweep
            for x in read_out(os.path.join(d, "bw.out")):
                if x["test"] != "bw" or "ns" not in x:
                    continue
                key = (x["dir"], x["copy"])
                gbs = x["bytes"] / med(x["ns"])
                sorted_ns = sorted(x["ns"])
                p10 = sorted_ns[max(0, int(round(0.1 * (len(sorted_ns) - 1))))]
                bw.setdefault(key, {}).setdefault(x["bytes"], []).append(gbs)
                bwfloor.setdefault(key, {}).setdefault(x["bytes"], []).append(x["bytes"] / p10)
                rv.setdefault("bw", {}).setdefault(key, {})[x["bytes"]] = gbs
            for x in read_out(os.path.join(d, "hostcopy.out")):
                hc.setdefault(x["bytes"], []).append(x["bytes"] / med(x["ns"]))
            # latency
            for x in read_out(os.path.join(d, "lat.out")):
                if x["test"] != "lat":
                    continue
                us = [v / 1e3 for v in x["ns"]]
                if x["kind"] == "idle_wait":
                    lat_idle.append(med(us))
                elif x["kind"] == "round_trip":
                    key = f'{x["dir"]}_{x["copy"]}_{x["bytes"]}'
                    lat_rt.setdefault(key, []).append(med(us))
                    lat_fast.setdefault(key, []).append(sum(u < 300 for u in us) / len(us))
                    rv.setdefault("rt", {})[key] = med(us)
                    if x["bytes"] == 4096:
                        for u in us:
                            hist_rt[min(39, int(u // 20))] += 1
                elif x["kind"] == "sporadic":
                    key = f'{x["dir"]}_{x["copy"]}'
                    lat_sp.setdefault(key, {"med": [], "mean": [], "fast": []})
                    lat_sp[key]["med"].append(med(us))
                    lat_sp[key]["mean"].append(st.mean(us))
                    lat_sp[key]["fast"].append(sum(u < 300 for u in us) / len(us))
                    for u in us:
                        hist_sp[min(39, int(u // 20))] += 1
                elif x["kind"] == "pipelined":
                    key = f'{x["dir"]}_{x["copy"]}'
                    lat_pipe.setdefault(key, []).append(med(us) / x["count"])
            # launches
            single, b2b = {}, {}
            for x in read_out(os.path.join(d, "launch.out")):
                if x["test"] != "launch":
                    continue
                if x["kind"] == "load_and_first":
                    ln_first.append(x["first_ns"] / 1e3)
                    ln_load.append(x["load_ns"] / 1e3)
                elif x["kind"] == "empty":
                    single.setdefault(x["shires"], []).extend(v / 1e3 for v in x["ns"])
                    b2b.setdefault(x["shires"], []).extend(v / 1e3 / x["b2b_count"] for v in x["b2b_ns"])
            for sh in single:
                v = sorted(single[sh])
                ln_spread.setdefault(sh, []).append(v[int(0.9 * (len(v) - 1))] - v[int(0.1 * (len(v) - 1))])
                ln_single.setdefault(sh, []).append(med(single[sh]))
                ln_b2b.setdefault(sh, []).append(med(b2b[sh]))
                rv.setdefault("single", {})[sh] = med(single[sh])
                rv.setdefault("b2b", {})[sh] = med(b2b[sh])
            # concurrency: the median over the run's trials
            cc = {}
            for x in read_out(os.path.join(d, "conc.out")):
                if x["test"] != "conc" or "wall_ns" not in x:
                    continue
                key = (x["copy"], x["cfg"])
                cc.setdefault(key, {"agg": [], "legs": []})
                cc[key]["agg"].append(x["legs"] * x["bytes_per_leg"] / x["wall_ns"])
                cc[key]["legs"].append([x["bytes_per_leg"] / v for v in x["leg_ns"]])
            for key, v in cc.items():
                agg = med(v["agg"])
                legs = [med([t[i] for t in v["legs"]]) for i in range(len(v["legs"][0]))]
                conc.setdefault(key, {"agg": [], "legs": []})
                conc[key]["agg"].append(agg)
                conc[key]["legs"].append(legs)
                rv.setdefault("conc", {})[key] = agg
            R.append(rv)
        per_run[card] = R
        D["hosts"][card] = host
        D["bw"][card] = {}
        for (dr, cp), curve in sorted(bw.items()):
            D["bw"][card].setdefault(dr, {})[cp] = [
                {"bytes": s, "gbs": stat(curve[s]), "floor_gbs": stat(bwfloor[(dr, cp)][s])} for s in sorted(curve)]
        D["hostcopy"][card] = [{"bytes": s, "gbs": stat(hc[s])} for s in sorted(hc)]
        D["lat"][card] = {
            "idle_wait_us": stat(lat_idle),
            "round_trip": {k: {"median_us": stat(v), "fast_share": stat(lat_fast[k])} for k, v in sorted(lat_rt.items())},
            "sporadic": {k: {"median_us": stat(v["med"]), "mean_us": stat(v["mean"]), "fast_share": stat(v["fast"])}
                         for k, v in sorted(lat_sp.items())},
            "pipelined_us_per_copy": {k: stat(v) for k, v in sorted(lat_pipe.items())},
        }
        D["hist"][card] = {"bin_us": 20, "round_trip_4k": hist_rt, "sporadic_4k": hist_sp}
        D["launch"][card] = {
            "single_us": {str(k): stat(v) for k, v in sorted(ln_single.items())},
            "b2b_us": {str(k): stat(v) for k, v in sorted(ln_b2b.items())},
            "single_p10_p90_spread_us": {str(k): stat(v) for k, v in sorted(ln_spread.items())},
            "first_us": stat(ln_first), "load_us": stat(ln_load)}
        D["conc"][card] = {}
        for (cp, cfg), v in sorted(conc.items()):
            nl = len(v["legs"][0])
            D["conc"][card].setdefault(cp, {})[cfg] = {
                "agg_gbs": stat(v["agg"]), "legs_gbs": [stat([t[i] for t in v["legs"]]) for i in range(nl)]}

    # derived per-run quantities and the predictions
    P = []

    def add(pid, text, pred, per_card_stat, judge):
        pc = {}
        for c in D["cards"]:
            s = per_card_stat(c)
            pc[c] = {"value": s, "verdict": judge(s)}
        P.append({"id": pid, "text": text, "prediction": pred, "per_card": pc})

    def bwrun(c, dr, cp, size=BIG):
        return [r["bw"][(dr, cp)][size] for r in per_run[c]]

    add("P1", "H2D bandwidth, dma, 256 MB (GB/s)", "9.0-14.2 GB/s",
        lambda c: stat(bwrun(c, "h2d", "dma")), lambda s: verdict_range(s, 9.0, 14.2))
    add("P2", "D2H bandwidth, dma, 256 MB (GB/s)", "9.0-14.2 GB/s",
        lambda c: stat(bwrun(c, "d2h", "dma")), lambda s: verdict_range(s, 9.0, 14.2))
    add("P3", "D2H minus H2D, dma, 256 MB (GB/s)", "D2H > H2D (difference > 0)",
        lambda c: stat([b - a for a, b in zip(bwrun(c, "h2d", "dma"), bwrun(c, "d2h", "dma"))]), verdict_positive)
    add("P4a", "staged / dma, H2D, 256 MB", "0.50-0.95",
        lambda c: stat([s / d for s, d in zip(bwrun(c, "h2d", "staged"), bwrun(c, "h2d", "dma"))]),
        lambda s: verdict_range(s, 0.50, 0.95))
    add("P4b", "staged / dma, D2H, 256 MB", "0.50-0.95",
        lambda c: stat([s / d for s, d in zip(bwrun(c, "d2h", "staged"), bwrun(c, "d2h", "dma"))]),
        lambda s: verdict_range(s, 0.50, 0.95))
    half = {c: {k: [half_size(r["bw"][k], BIG) for r in per_run[c]] for k in per_run[c][0]["bw"]} for c in D["cards"]}
    add("P5", "n1/2, H2D dma: log2(bytes) where the bandwidth reaches half its 256 MB value", "128 KB-4 MB (log2 17-22)",
        lambda c: stat(half[c][("h2d", "dma")]), lambda s: verdict_range(s, 17.0, 22.0))
    add("P6", "round trip, 4 KB, staged H2D, back to back (us)", "60-700 us",
        lambda c: stat([r["rt"]["h2d_staged_4096"] for r in per_run[c]]), lambda s: verdict_range(s, 60, 700))
    add("P7", "round trip, 4 KB minus 64 B, staged H2D (us)", "|difference| < 25 us",
        lambda c: stat([r["rt"]["h2d_staged_4096"] - r["rt"]["h2d_staged_64"] for r in per_run[c]]),
        lambda s: verdict_range(s, -25, 25))
    add("P8", "empty kernel, 32 shires, launch to completion (us)", "80-1,000 us",
        lambda c: stat([r["single"][32] for r in per_run[c]]), lambda s: verdict_range(s, 80, 1000))

    def p9(s_c):
        return s_c
    add("P9a", "empty kernel, 32 shires, back to back, per launch (us)", "5-300 us",
        lambda c: stat([r["b2b"][32] for r in per_run[c]]), lambda s: verdict_range(s, 5, 300))
    add("P9b", "launch to completion minus back-to-back per launch, 32 shires (us)", "> 0 (back to back is faster)",
        lambda c: stat([r["single"][32] - r["b2b"][32] for r in per_run[c]]), verdict_positive)
    add("P10", "back to back per launch, 32 shires minus 1 shire (us)", "> 0",
        lambda c: stat([r["b2b"][32] - r["b2b"][1] for r in per_run[c]]), verdict_positive)
    add("P11", "H2D+D2H at once / the faster single direction, dma, 2 x 64 MB per stream", ">= 1.5",
        lambda c: stat([r["conc"][("dma", "h2d+d2h")] / max(r["conc"][("dma", "h2d")], r["conc"][("dma", "d2h")])
                        for r in per_run[c]]),
        lambda s: ("NO DATA" if s is None or s["lo"] is None else
                   "PASS" if s["lo"] >= 1.5 else "FAIL" if s["hi"] < 1.5 else "INCONCLUSIVE"))
    add("P12", "two H2D streams / one H2D stream, dma, 2 x 64 MB per stream", "<= 1.25",
        lambda c: stat([r["conc"][("dma", "2xh2d")] / r["conc"][("dma", "h2d")] for r in per_run[c]]),
        lambda s: ("NO DATA" if s is None or s["lo"] is None else
                   "PASS" if s["hi"] <= 1.25 else "FAIL" if s["lo"] > 1.25 else "INCONCLUSIVE"))
    # P13: across cards, on the card means
    p13 = {}
    for dr in ("h2d", "d2h"):
        means = {c: st.mean(bwrun(c, dr, "dma")) for c in D["cards"]}
        g = st.mean(means.values())
        dev = {c: round(means[c] / g - 1, 4) for c in means}
        p13[dr] = {"card_means": {c: round(v, 4) for c, v in means.items()}, "grand_mean": round(g, 4),
                   "rel_dev": dev, "verdict": "PASS" if all(abs(v) <= 0.10 for v in dev.values()) else "FAIL"}
    P.append({"id": "P13", "text": "the three cards' dma 256 MB bandwidth, each direction, within 10% of their mean",
              "prediction": "within 10%", "across_cards": p13})
    D["predictions"] = P
    D["n_half_log2"] = {c: {f"{k[0]}_{k[1]}": stat(v) for k, v in half[c].items()} for c in D["cards"]}
    # ratios the page quotes, per run (not predicted: added after the pilot showed two H2D commands in flight
    # moving less than one; the /ser configurations carry a barrier on every transfer)
    D["derived"] = {}
    for c in D["cards"]:
        rr = per_run[c]
        g = lambda cp, cfg: [r["conc"][(cp, cfg)] for r in rr]
        D["derived"][c] = {
            "h2d_two_in_flight_over_one": stat([a / b for a, b in zip(g("dma", "h2d"), g("dma", "h2d/ser"))]),
            "d2h_two_in_flight_over_one": stat([a / b for a, b in zip(g("dma", "d2h"), g("dma", "d2h/ser"))]),
            "duplex_ser_over_faster_ser": stat([a / max(b, cc) for a, b, cc in
                                                zip(g("dma", "h2d+d2h/ser"), g("dma", "h2d/ser"), g("dma", "d2h/ser"))]),
            "peak_dma_gbs": {dr: max(((e["bytes"], e["gbs"]["mean"]) for e in D["bw"][c][dr]["dma"]), key=lambda t: t[1])
                             for dr in ("h2d", "d2h")},
        }
    json.dump(D, open(a.out, "w"), indent=1)
    print("wrote", a.out)

    if a.md:
        L = ["# PCIe link and launch path: results against the predictions", "",
             f"Generated by `workloads/pciebench/reduce_pcie.py` from `raw/`. PREREG.md sha256 `{D['meta'].get('prereg_sha256', '?')}`.",
             "Per card: the mean over runs [99% interval] (n runs). PASS: the interval lies inside the predicted range "
             "(or excludes 0 on the predicted side); FAIL: entirely outside (or excludes 0 on the other side); "
             "otherwise INCONCLUSIVE.", "",
             "| ID | Quantity | Prediction | " + " | ".join(D["cards"]) + " |",
             "|---|---|---|" + "---|" * len(D["cards"])]
        fmt = lambda s: "-" if s is None else (f"{s['mean']:.4g} [{s['lo']:.4g}, {s['hi']:.4g}] (n={s['n']})"
                                                if s["lo"] is not None else f"{s['mean']:.4g} (n={s['n']})")
        for p in P:
            if "per_card" in p:
                cells = [f"{p['per_card'][c]['verdict']}: {fmt(p['per_card'][c]['value'])}" for c in D["cards"]]
            else:
                cells = []
                for c in D["cards"]:
                    cells.append("; ".join(f"{dr} {p['across_cards'][dr]['card_means'][c]:.3f} GB/s "
                                           f"({100 * p['across_cards'][dr]['rel_dev'][c]:+.1f}%)" for dr in ("h2d", "d2h")))
                cells[0] = f"h2d {p['across_cards']['h2d']['verdict']}, d2h {p['across_cards']['d2h']['verdict']}: " + cells[0]
            L.append(f"| {p['id']} | {p['text']} | {p['prediction']} | " + " | ".join(cells) + " |")
        L += ["", "P5 is judged on log2(bytes): 17 = 128 KB, 22 = 4 MB."]
        open(a.md, "w").write("\n".join(L) + "\n")
        print("wrote", a.md)


if __name__ == "__main__":
    main()
