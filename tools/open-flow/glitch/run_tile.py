#!/usr/bin/env python3
"""Q138(g): one tile's 16 tima_top instances (bench stimulus from batch_vcd.py) through esim with one annotated model.

    run_tile.py --model models/<arm>.pkl --stim stim/<arm>__<tile>__<n0>.pkl.gz --out <json> [--t-in 66] [--period 833.5]
                [--skew-ps 0 --skew-seed 1] [--no-check]

Validation in every run without --no-check: the simulator's settled value of every net just before every rising clock edge is
compared with the bench's own zero-delay VCD value at that moment (Verilator, the same netlist); mismatches are counted and
reported. A run with --no-check still writes mismatch 0, so the record's "checked" says whether the comparison ran (added
after verification, 2 Nov 2026; the runs committed before it got the flag from their launch commands, README C2).
"""
import argparse, gzip, json, os, pickle, random, sys, time
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from esim import Sim

STAGES = (("f2_prod", "multiplier"), ("f2_in", "operand"), ("f3_add", "adder"), ("ctl", "control"), ("f3_prod", "multiplier_reg"),
          ("f3_out", "result"), ("f3_zap", "adder"))
PORTS_IN = ("clock", "f1_mul_en", "f1_in1", "f1_in2", "f1_in1_signed", "f1_in2_signed", "f3_in3", "f2_zap_opd3", "f2_tima_en")


def stage(name):
    base = name.split("[")[0]
    if base in PORTS_IN:
        return "port_in"
    for p, s in STAGES:
        if base.startswith(p):
            return s
    return "other"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True)
    ap.add_argument("--stim", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--t-in", type=float, default=-1, help="ps after the edge at which the input ports move; default = the "
                    "model's smallest CLK->Q")
    ap.add_argument("--period", type=float, default=1e12 / 600e6 / 2, help="ps per bench timestamp (half a 600 MHz cycle)")
    ap.add_argument("--skew-ps", type=float, default=0.0)
    ap.add_argument("--skew-seed", type=int, default=1)
    ap.add_argument("--no-check", action="store_true")
    ap.add_argument("--verilog-style", action="store_true", help="a pending transaction is replaced by a later one of the same value")
    a = ap.parse_args()
    m = pickle.load(open(a.model, "rb"))
    st = pickle.load(gzip.open(a.stim, "rb"))
    sim = Sim(m)
    nets = m["nets"]
    nid = {n: i for i, n in enumerate(nets)}
    t_in = a.t_in if a.t_in >= 0 else min(min(f["dly"]) for f in m["ffs"])
    in_ids = set(m["inputs"])
    stg = [stage(n) for n in nets]
    res = {"model": os.path.basename(a.model), "stim": os.path.basename(a.stim), "t_in_ps": t_in, "period_ps": a.period,
           "skew_ps": a.skew_ps, "verilog_style": a.verilog_style, "checked": not a.no_check, "params": m["params"], "instances": {}}
    t0 = time.time()
    tot = {"timed": 0, "zero": 0, "mismatch": 0, "late": 0}
    for p in sorted(st["insts"]):
        ch = st["insts"][p]
        # expand vectors into bits
        series = {}
        for name, lst in ch.items():
            if name in nid:
                series[nid[name]] = lst
            else:
                # vector: name[i]
                w = 0
                while f"{name}[{w}]" in nid:
                    w += 1
                if w == 0:
                    continue
                for i in range(w):
                    series[nid[f"{name}[{i}]"]] = [(t, (v >> i) & 1) for t, v in lst]
        missing = [nets[i] for i in range(len(nets)) if i not in series]
        assert not missing, missing[:5]
        times = st["times"]
        T0 = times[0]
        init = [0] * len(nets)
        for n, lst in series.items():
            assert lst[0][0] == T0
            init[n] = lst[0][1]
        # port steps
        steps = {}
        for n in in_ids:
            prev = init[n]
            for t, v in series[n][1:]:
                if v != prev:
                    steps.setdefault(t, {})[n] = v
                    prev = v
        step_list = [((t - T0) / 1000.0, steps[t]) for t in sorted(steps)]
        # expected settled values just before each rising edge (bench VCD)
        clk = [n for n in sim.clk_nets][0]
        edges = [t for t, v in series[clk][1:] if v == 1]
        exp_mis = [0]
        if not a.no_check:
            # value of every net at the last change strictly before each edge
            ptr = {n: 0 for n in series}
            exp_at = []
            for e in edges:
                vals = [0] * len(nets)
                for n, lst in series.items():
                    k = ptr[n]
                    while k + 1 < len(lst) and lst[k + 1][0] < e:
                        k += 1
                    ptr[n] = k
                    vals[n] = lst[k][1]
                exp_at.append(vals)

            def check(i, val):
                ex = exp_at[i]
                for n in range(len(nets)):
                    if val[n] != ex[n]:
                        exp_mis[0] += 1
        else:
            check = None
        skew = None
        if a.skew_ps > 0:
            rnd = random.Random(f"{a.skew_seed}|{p}")
            skew = [rnd.uniform(0, a.skew_ps) for _ in nets]
        # the bench's window: settled samples at the even timestamps (settle_count --phase even --skip 1), counted from sample 1
        even = [t for t in times if ((t - T0) // 1000) % 2 == 0]
        w0_bench = even[1]
        tog, ztog, samples, late = sim.run(init, step_list, a.period, t_in, skew=skew, check=check,
                                           w0=(w0_bench - T0) / 1000.0 * a.period, verilog_style=a.verilog_style)
        # zero-delay toggles the bench's way, from the bench VCD itself: bit changes between consecutive even-timestamp samples
        bz = [0] * len(nets)
        for n, lst in series.items():
            k, prev, cnt = 0, None, 0
            for e in even[1:]:
                while k + 1 < len(lst) and lst[k + 1][0] <= e:
                    k += 1
                v = lst[k][1]
                if prev is not None and v != prev:
                    cnt += 1
                prev = v
            bz[n] = cnt
        by = {}
        for n in range(len(nets)):
            s = stg[n]
            d = by.setdefault(s, {"timed": 0, "zero": 0, "nets": 0})
            d["timed"] += tog[n]
            d["zero"] += bz[n]
            d["nets"] += 1
        inst = {"samples": samples, "edges": len(edges), "late_ff_samples": late, "mismatch": exp_mis[0], "window_ps": sim.window,
                "timed": sum(tog[n] for n in range(len(nets)) if n not in in_ids),
                "zero": sum(bz[n] for n in range(len(nets)) if n not in in_ids),
                "zero_preedge": sum(ztog[n] for n in range(len(nets)) if n not in in_ids),
                "zero_ports_in_bench": sum(bz[n] for n in in_ids),
                "timed_ports_in": sum(tog[n] for n in in_ids), "zero_ports_in": sum(ztog[n] for n in in_ids), "by_stage": by,
                "per_net_excess_top": sorted(((tog[n] - bz[n], nets[n]) for n in range(len(nets)) if tog[n] - ztog[n] > 0),
                                             reverse=True)[:8],
                "per_net": {"timed": tog, "zero": bz}}
        res["instances"][p] = inst
        tot["timed"] += inst["timed"]
        tot["zero"] += inst["zero"]
        tot["mismatch"] += inst["mismatch"]
        tot["late"] += late
    res["total"] = tot
    agg = {}
    for p, inst in res["instances"].items():
        for s, d in inst["by_stage"].items():
            g = agg.setdefault(s, {"timed": 0, "zero": 0})
            g["timed"] += d["timed"]
            g["zero"] += d["zero"]
    res["by_stage"] = agg
    res["seconds"] = time.time() - t0
    json.dump(res, open(a.out, "w"), indent=1)
    print(f"{os.path.basename(a.stim)}: timed {tot['timed']} zero {tot['zero']} ratio {tot['timed']/max(1,tot['zero']):.3f} "
          f"mismatch {tot['mismatch']} late {tot['late']} {res['seconds']:.1f}s")


if __name__ == "__main__":
    main()
