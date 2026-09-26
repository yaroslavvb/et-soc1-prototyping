#!/usr/bin/env python3
"""Reduce one pass of the E5 load step (tools/ettelem/run_thermal.sh output: thermal-telemetry.jsonl,
thermal-phases.jsonl) to the numbers experiment X1 pre-registered, for either card.  Uses the page's own reducer
functions (tools/ettelem/summarize_power_session.py: series, gaps, fast) imported read-only, so a pass is reduced
exactly as the page reduces E5.  Run on the committed E5 directory it reproduces the page's figures (self-check).

    python3 -B x1_reduce.py DIR [--card a2|a3] > pass.json
    python3 -B x1_reduce.py --pool pass1.json pass2.json ...   # pass-level means, 99% t intervals

Per pass: clock check (drop the pass on a2 if any sample has mhz.minion != 600), busy slope board/minion against
the whole-degree die temperature (fit from 5 s after the matmul mark, all bins, as the page), the idle law's slope over
the same bins (a2 law; also the slope of the cool1 bins >= 8 s after the stop, reported but biased low: 0.41 W/C on E5), idle before
(idle0) and after (last 5 s of cool1) with temperatures, the unmetered remainder at idle/matmul/DRAM, the DRAM phase's
remainder, minion-rail and temperature change against the cool1 baseline, the DDR on-die reading (idle0, cool, DRAM,
matmul last 18 s), the minion on-die droop per W, the edge remainder at tau = 0 and filtered with the card's tau, and
the PMIC board average minus the board reading in steady state.
"""
import argparse, json, math, os, statistics as st, sys

# V3 copy: the tree root is three levels up from tools/claims-v3/mmb/ (the original pinned the aifoundry2 path).
REPO = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", ".."))
sys.dont_write_bytecode = True
sys.path.insert(0, os.path.join(REPO, "tools", "ettelem"))
import summarize_power_session as sps  # noqa: E402  (read-only use of series(), gaps(), fast())
import gzip  # noqa: E402
_load_plain = sps.load_jsonl


def _load_jsonl_gz(path):  # V3 copy: the blocks gzip their telemetry; read path or path.gz
    if not os.path.exists(path) and os.path.exists(path + ".gz"):
        with gzip.open(path + ".gz", "rt") as f:
            return [json.loads(l) for l in f if l.startswith("{")]
    return _load_plain(path)


sps.load_jsonl = _load_jsonl_gz

DV = json.load(open(os.path.join(REPO, "docs/reports/data/2026-09-22-dvfs-aifoundry2/dvfs.json")))["leak_model"]
law = lambda T: DV["P_fix"] + DV["A_at_80"] * math.exp((T - 80) / DV["T_L"])
TAU = {"a2": 1.148, "a3": 1.217}  # catalogue.json rail_filter
# V3 four cards: a card without a measured rail filter (aifoundry1's, codes a1c0/a1c1) is filtered with aifoundry2's tau;
# reduce.py reports that clause for those cards instead of deciding it. "valid" stays the registered a2-only rule: the
# callers apply the busy-sample clock rule (cardrules.py) to aifoundry1's cards.
tau_of = lambda card: TAU.get(card, TAU["a2"])
mean = lambda xs: sum(xs) / len(xs)


def lsq(xs, ys):
    mx, my = mean(xs), mean(ys)
    return sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / sum((x - mx) ** 2 for x in xs)


def reduce_pass(d, card):
    tel = sps.load_jsonl(os.path.join(d, "thermal-telemetry.jsonl"))
    mk = sps.load_jsonl(os.path.join(d, "thermal-phases.jsonl"))
    t0 = mk[0]["t_ms"]; M = {m["phase"]: (m["t_ms"] - t0) / 1000 for m in mk}
    marks = [(m["phase"], (m["t_ms"] - t0) / 1000) for m in mk]
    S = sps.series(tel, t0); G = sps.gaps(tel, t0, marks)
    o = {"dir": d, "card": card, "mhz": sorted(set(r["mhz"]["minion"] for r in tel)),
         "valid": card != "a2" or all(r["mhz"]["minion"] == 600 for r in tel)}
    rest = lambda p: p["board"] - p["minion"] - p["sram"] - p["noc"]
    gapbin = lambda k: any(k <= g < k + 1 for g in G)
    neargap = lambda k, w: any(abs(math.floor(g) - k) <= w for g in G)
    TM, TC1, TD, TC2 = M["matmul"], M["cool1"], M["dram"], M["cool2"]
    I0 = [p for p in S if p["t"] + 1 <= TM]; CO = [p for p in S if p["t"] >= TD - 5 and p["t"] + 1 <= TD]
    F = [p for p in S if p["t"] >= TM + 5 and p["t"] + 1 <= TC1]
    T = [p["temp"] for p in F]
    o["busy_slope_board"] = round(lsq(T, [p["board"] for p in F]), 3)
    o["busy_slope_minion"] = round(lsq(T, [p["minion"] for p in F]), 3)
    o["law_slope_same_bins"] = round(lsq(T, [law(x) for x in T]), 3)
    o["busy_T_range"] = [min(T), max(T)]
    CD = [p for p in S if p["t"] >= TC1 + 8 and p["t"] + 1 <= TD]  # cool-down bins, the card's own idle slope
    o["own_idle_slope_cool1"] = round(lsq([p["temp"] for p in CD], [p["board"] for p in CD]), 3) if len({p["temp"] for p in CD}) > 1 else None
    o["idle_before"] = [round(mean([p["board"] for p in I0]), 3), round(mean([p["temp"] for p in I0]), 2)]
    o["idle_after"] = [round(mean([p["board"] for p in CO]), 3), round(mean([p["temp"] for p in CO]), 2)]
    o["idle_after_minus_before_w"] = round(o["idle_after"][0] - o["idle_before"][0], 3)
    o["idle_after_minus_before_law_w"] = round(law(o["idle_after"][1]) - law(o["idle_before"][1]), 3)
    o["cool_drop_40s_c"] = [p["temp"] for p in S if p["t"] == math.floor(TC1) - 1][0] - [p["temp"] for p in S if p["t"] == math.floor(TD) - 1][0]
    rm = [rest(p) for p in S if p["t"] >= TM + 5 and p["t"] + 1 <= TC1 and not neargap(p["t"], 1)]
    DR = [p for p in S if p["t"] >= TD + 1 and p["t"] + 1 <= TC2 and not neargap(p["t"], 1)]
    MMB = [p for p in S if p["t"] >= TM + 5 and p["t"] + 1 <= TC1 and not neargap(p["t"], 1)]
    o["rest_idle0"] = round(mean([rest(p) for p in I0]), 2); o["rest_cool"] = round(mean([rest(p) for p in CO]), 2)
    o["rest_matmul_range"] = [round(min(rm), 2), round(max(rm), 2)]
    o["rest_matmul_mean"] = round(mean(rm), 2)  # V3 copy: the steady matmul level for P7
    o["dram_rest_rise_w"] = round(mean([rest(p) for p in DR]) - o["rest_cool"], 2)
    o["dram_minion_rise_w"] = round(mean([p["minion"] for p in DR]) - mean([p["minion"] for p in CO]), 2)
    o["dram_dT_c"] = round(mean([p["temp"] for p in DR]) - mean([p["temp"] for p in CO]), 2)
    o["mm_minion_over_idle0_range"] = [round(min(p["minion"] for p in MMB) - mean([p["minion"] for p in I0]), 2),
                                       round(max(p["minion"] for p in MMB) - mean([p["minion"] for p in I0]), 2)]
    dI, tI, dC, tC = mean([p["die_ddr"] for p in I0]), mean([p["temp"] for p in I0]), mean([p["die_ddr"] for p in CO]), mean([p["temp"] for p in CO])
    k = (dC - dI) / (tC - tI) if tC != tI else 0.0
    DR3 = [p for p in S if p["t"] >= TD + 3 and p["t"] + 1 <= TC2]; MM18 = [p for p in S if p["t"] >= TC1 - 18 and p["t"] + 1 <= TC1]
    tr = lambda P: dC + k * (mean([p["temp"] for p in P]) - tC) - mean([p["die_ddr"] for p in P])
    o["ddr"] = {"idle0": round(dI, 2), "cool": round(dC, 2), "slope_mv_per_c": round(k, 3), "dram_below_trend": round(tr(DR3), 2),
                "dram_below_idle0": round(dI - mean([p["die_ddr"] for p in DR3]), 2), "mm_below_trend": round(tr(MM18), 2)}
    dw = mean([p["minion"] for p in MMB]) - mean([p["minion"] for p in I0])
    o["die_minion_droop_mv_per_w"] = round((mean([p["die_mnn"] for p in I0]) - mean([p["die_mnn"] for p in MMB])) / dw, 4)
    FA = sps.fast(tel, t0); FT = FA["t"]
    FI = [[i for i in range(len(FT)) if a <= FT[i] < z] for a, z in FA["windows"]]

    def rem(w, tau):
        y = tp = None; r = []
        for i in FI[w]:
            v = FA["board"][i]; y = v if (y is None or tau <= 0) else y + (1 - math.exp(-(FT[i] - tp) / tau)) * (v - y); tp = FT[i]
            r.append(y - FA["rails"][i])
        return r
    o["edge_tau0"] = {"start_max": round(max(rem(0, 0)), 2), "min_start_window": round(min(rem(0, 0)), 2), "min_stop_window": round(min(rem(1, 0)), 2)}
    o["edge_tau_card"] = [round(min(min(rem(w, tau_of(card))) for w in (0, 1)), 2), round(max(max(rem(w, tau_of(card))) for w in (0, 1)), 2)]
    o["edge_tau_used"] = tau_of(card)  # V3 four cards
    edges = [M[x] for x in M] + G
    tt = [(r["t_ms"] - t0) / 1000 for r in tel]
    dd = [r["sp"]["board_avg_w"] - r["board_w"] for r, x in zip(tel, tt) if min(abs(x - e) for e in edges) >= 3]
    o["board_avg_minus_board_steady_median"] = round(st.median(dd), 3)
    return o


T995 = {1: 63.657, 2: 9.925, 3: 5.841, 4: 4.604, 5: 4.032, 6: 3.707, 7: 3.499, 8: 3.355, 9: 3.25, 11: 3.106}


def pool(files):
    P = [json.load(open(f)) for f in files]
    P = [p for p in P if p["valid"]]
    out = {"passes": len(P)}
    for key in ("busy_slope_board", "busy_slope_minion", "idle_after_minus_before_w", "dram_rest_rise_w", "dram_minion_rise_w",
                "die_minion_droop_mv_per_w", "board_avg_minus_board_steady_median"):
        xs = [p[key] for p in P]
        if len(xs) >= 2:
            m, se = mean(xs), st.stdev(xs) / math.sqrt(len(xs))
            out[key] = {"mean": round(m, 4), "ci99": [round(m - T995[len(xs) - 1] * se, 4), round(m + T995[len(xs) - 1] * se, 4)], "values": xs}
    # busy minus idle slope: a2 against the idle law over the same bins. Not computed for a3: its only idle slope in a
    # pass is from the cool1 bins, which reads low (0.41 W/C on E5 where the law gives ~0.7): the whole-degree mean lags
    # a die that is relaxing its gradient; a3 needs a separate long idle cool-down (X1 extension).
    xs = [p["busy_slope_board"] - p["law_slope_same_bins"] for p in P if p["card"] == "a2"]
    if len(xs) >= 2:
        m, se = mean(xs), st.stdev(xs) / math.sqrt(len(xs))
        out["busy_minus_idle_slope"] = {"mean": round(m, 4), "ci99": [round(m - T995[len(xs) - 1] * se, 4), round(m + T995[len(xs) - 1] * se, 4)], "values": xs}
    xs = [p["ddr"]["dram_below_trend"] for p in P]
    if len(xs) >= 2:
        m, se = mean(xs), st.stdev(xs) / math.sqrt(len(xs))
        out["ddr_dram_below_trend"] = {"mean": round(m, 3), "ci99": [round(m - T995[len(xs) - 1] * se, 3), round(m + T995[len(xs) - 1] * se, 3)]}
    return out


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("dir", nargs="?")
    ap.add_argument("--card", default="a2", help="a2 | a3 | a1c0 | a1c1 (cardrules.short)")
    ap.add_argument("--pool", nargs="+")
    a = ap.parse_args()
    json.dump(pool(a.pool) if a.pool else reduce_pass(a.dir, a.card), sys.stdout, indent=1)
