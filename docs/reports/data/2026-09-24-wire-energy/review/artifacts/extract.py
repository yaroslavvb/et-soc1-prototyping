"""Per-burst extraction with artifact diagnostics (independent of analyze_wire.py, same windows where noted)."""
import json, collections, math, os, sys
import numpy as np
D = "/home/yaroslavvb/claude/et-soc1-prototyping/docs/reports/data/"
SETS = {"v1": ["2026-09-24-wire-aifoundry2", "2026-09-24-wire-aifoundry3"],
        "v2": ["2026-09-24-wire2-aifoundry2", "2026-09-24-wire2-aifoundry3"]}
A_LEAK_80, T_L = 23.257, 36.0
def leak_slope(T): return A_LEAK_80 / T_L * math.exp((T - 80.0) / T_L)
out = []
for st, dirs in SETS.items():
    for d in dirs:
        card = "aifoundry2" if "aifoundry2" in d else "aifoundry3"
        tel = [json.loads(l) for l in open(D + d + "/telemetry.jsonl") if l.startswith("{")]
        runs = [json.loads(l) for l in open(D + d + "/runs.jsonl")]
        marks = [json.loads(l) for l in open(D + d + "/marks.jsonl")]
        t = np.array([s["t_ms"] for s in tel]) / 1e3
        w = np.array([s["board_w"] for s in tel]); T = np.array([s["temp_c"]["minshire"][0] for s in tel])
        mhz = np.array([s["mhz"]["minion"] for s in tel]); mnoc = np.array([s["mhz"]["noc"] for s in tel])
        took = np.array([s.get("took_ms", 0) for s in tel])
        noc = np.array([s["sp"]["noc_w"][0] for s in tel]); sram = np.array([s["sp"]["sram_w"][0] for s in tel])
        mino = np.array([s["sp"]["minion_w"][0] for s in tel])
        nocmv = np.array([s["die_mv"]["noc"] for s in tel])
        busy_other = np.zeros(len(t), bool)
        fills = sorted((m["t_start_ms"] / 1e3, m["t_end_ms"] / 1e3, m["cfg"], m["pass"]) for m in marks)
        for m in marks:
            busy_other |= (t >= m["t_start_ms"] / 1e3 - 0.2) & (t <= m["t_end_ms"] / 1e3 + 0.6)
        g = collections.OrderedDict()
        for r in runs: g.setdefault((r["cfg"], r["pass"]), []).append(r)
        bl = sorted(((k, rs, min(r["t_start_ms"] for r in rs) / 1e3, max(r["t_end_ms"] for r in rs) / 1e3) for k, rs in g.items()), key=lambda b: b[2])
        for i, (k, rs, lo, hi) in enumerate(bl):
            prev_hi = bl[i - 1][3] if i else t[0]
            next_lo = bl[i + 1][2] if i + 1 < len(bl) else t[-1]
            busy = (t >= lo + 0.5) & (t <= hi)
            before = (t >= max(prev_hi + 2.0, lo - 3.5)) & (t <= lo - 0.3) & ~busy_other
            after = (t >= hi + 0.5) & (t <= min(next_lo - 0.3, hi + 3.8)) & ~busy_other
            rail_idle = (t >= max(prev_hi + 3.0, lo - 2.5)) & (t <= lo - 0.3) & ~busy_other
            rail_after = (t >= hi + 3.0) & (t <= min(next_lo - 0.3, hi + 3.8)) & ~busy_other
            tail = (t >= hi - 0.6) & (t <= hi)
            win = (t >= lo - 3.5) & (t <= hi + 3.8)
            fe = [f for f in fills if f[2] == k[0] and f[3] == k[1]]
            fill_end = fe[0][1] if fe else float("nan")
            by = sum(r["bytes"] for r in rs); wall = hi - lo
            ok = busy.sum() >= 5 and before.sum() >= 4
            def m_(x, mask): return float(x[mask].mean()) if mask.sum() else float("nan")
            idle_b = m_(w, before); idle_a = m_(w, after) if after.sum() >= 4 else float("nan")
            idle = idle_b if np.isnan(idle_a) else 0.5 * (idle_b + idle_a)
            Tb = m_(T, busy); Ti = float(np.concatenate([T[before], T[after]]).mean()) if after.sum() >= 4 else m_(T, before)
            over_raw = m_(w, busy) - idle
            leak = leak_slope(0.5 * (Tb + Ti)) * (Tb - Ti)
            rec = dict(set=st, card=card, cfg=k[0], pass_=k[1], order=i, lo=lo, hi=hi, wall=wall, bytes=by,
                       participants=rs[0]["participants"], shires=rs[0]["shires"], hop=rs[0].get("hop_distance", 0) or int(round(rs[0].get("mean_hops", 0))),
                       mean_hops=rs[0].get("mean_hops", 0), operands=rs[0]["operands"], bw=by / (sum(r["cycles_max"] for r in rs) / 0.6e9),
                       ok=bool(ok), n_busy=int(busy.sum()), n_before=int(before.sum()), n_after=int(after.sum()),
                       mhz_ok=bool((mhz[win] == 600).all()), noc_mhz_ok=bool((mnoc[win] == 400).all()),
                       took_med_busy=float(np.median(took[busy])) if busy.sum() else float("nan"), took_max_win=float(took[win].max()),
                       gap_max_win=float(np.diff(t[win]).max()) if win.sum() > 1 else float("nan"),
                       idle_b=idle_b, idle_a=idle_a, over_raw=over_raw, leak=leak, Tb=Tb, Ti=Ti, T_before=m_(T, before), T_after=m_(T, after),
                       fill_to_lo=lo - fill_end, prev_gap=lo - prev_hi,
                       noc_before=m_(noc, rail_idle), noc_tail=m_(noc, tail), noc_after=m_(noc, rail_after),
                       sram_before=m_(sram, rail_idle), sram_tail=m_(sram, tail), sram_after=m_(sram, rail_after),
                       min_before=m_(mino, rail_idle), min_tail=m_(mino, tail), min_after=m_(mino, rail_after),
                       nocmv_busy=m_(nocmv, busy), nocmv_idle=m_(nocmv, before),
                       n_tail=int(tail.sum()), n_rail_idle=int(rail_idle.sum()))
            k_ = 1e12 * wall / by
            rec["pJB_board"] = (over_raw - leak) * k_
            rec["pJB_board_raw"] = over_raw * k_
            rec["pJB_noc"] = (rec["noc_tail"] - rec["noc_before"]) / 0.94 * k_
            rec["pJB_sram"] = (rec["sram_tail"] - rec["sram_before"]) / 0.94 * k_
            rec["pJB_min"] = (rec["min_tail"] - rec["min_before"]) / 0.94 * k_
            rec["pJB_noc_driftcorr"] = (rec["noc_tail"] - rec["noc_before"] - 0.5 * (rec["noc_after"] - rec["noc_before"])) / 0.94 * k_
            out.append(rec)
json.dump(out, open(os.path.join(os.path.dirname(__file__), "bursts.json"), "w"))
print(len(out))
