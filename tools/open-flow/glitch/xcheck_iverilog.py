#!/usr/bin/env python3
"""Q138(g): the event engine against Icarus Verilog on a whole netlist: one tima_top instance, one tile's bench stimulus.

    xcheck_iverilog.py --model models/<arm>.pkl --stim stim/<arm>__<tile>__<n0>.pkl.gz --inst 0 --iverilog <path> --out <dir>

Both simulate the pin-independent version of the model (each cell's worst arc delay per output edge, which an `assign #(rise,
fall)` can express): esim through run_tile's own stimulus construction, Icarus Verilog with every cell an inertial continuous
assignment and every flip-flop `always @(posedge clock) q <= D` behind an `assign #(rise, fall)`. Transitions are counted per net
in the same window (from the bench's settled sample 1 on) and compared net by net.
"""
import argparse, copy, gzip, json, os, pickle, subprocess, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from esim import Sim


def safe(n):
    return "n_" + n.replace("[", "_").replace("]", "_")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", required=True)
    ap.add_argument("--stim", required=True)
    ap.add_argument("--inst", type=int, default=0)
    ap.add_argument("--iverilog", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--period", type=float, default=1e12 / 600e6 / 2)
    ap.add_argument("--verilog-style", action="store_true")
    ap.add_argument("--t-in", type=float, default=-1)
    ap.add_argument("--udp", action="store_true", help="each cell a user-defined primitive (one table lookup, no zero-time "
                    "transients inside the cell) instead of a sum-of-products continuous assignment")
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    m = copy.deepcopy(pickle.load(open(a.model, "rb")))
    for g in m["gates"]:
        df = max(st[0] for row in g["dly"] for st in row)
        dr = max(st[1] for row in g["dly"] for st in row)
        g["dly"] = [[(df, dr) for _ in row] for row in g["dly"]]
    st = pickle.load(gzip.open(a.stim, "rb"))
    nets = m["nets"]
    nid = {n: i for i, n in enumerate(nets)}
    p = sorted(st["insts"])[a.inst]
    ch = st["insts"][p]
    series = {}
    for name, lst in ch.items():
        if name in nid:
            series[nid[name]] = lst
        else:
            w = 0
            while f"{name}[{w}]" in nid:
                w += 1
            for i in range(w):
                series[nid[f"{name}[{i}]"]] = [(t, (v >> i) & 1) for t, v in lst]
    times = st["times"]
    T0 = times[0]
    init = [0] * len(nets)
    for n, lst in series.items():
        init[n] = lst[0][1]
    in_ids = set(m["inputs"])
    steps = {}
    for n in in_ids:
        prev = init[n]
        for t, v in series[n][1:]:
            if v != prev:
                steps.setdefault(t, {})[n] = v
                prev = v
    step_list = [((t - T0) / 1000.0, steps[t]) for t in sorted(steps)]
    even = [t for t in times if ((t - T0) // 1000) % 2 == 0]
    w0 = (even[1] - T0) / 1000.0 * a.period
    t_in = a.t_in if a.t_in >= 0 else min(min(f["dly"]) for f in m["ffs"])
    sim = Sim(m)
    tog, ztog, samples, late = sim.run(init, step_list, a.period, t_in, w0=w0, verilog_style=a.verilog_style)
    clk = list(sim.clk_nets)[0]
    # Icarus: absolute event list in fs
    FS = 1000
    ev = []
    for (ti, chg) in step_list:
        T = ti * a.period
        for n, v in chg.items():
            ev.append((round(T * FS) if n == clk else round((T + t_in) * FS), n, v))
    ev.sort(key=lambda x: (x[0], x[1] != clk))
    v = ["`timescale 1fs/1fs"]
    if a.udp:
        seen = {}
        for g in m["gates"]:
            key = (g["cell"], len(g["ins"]))
            if key in seen:
                continue
            nm = "u_" + g["cell"]
            seen[key] = nm
            ins_ = [f"i{j}" for j in range(len(g["ins"]))]
            v.append(f"primitive {nm}(y, {', '.join(ins_)});")
            v.append("  output y;")
            v.append(f"  input {', '.join(ins_)};")
            v.append("  table")
            for st_, bit in enumerate(g["tt"]):
                v.append("    " + " ".join(str((st_ >> j) & 1) for j in range(len(g["ins"]))) + f" : {bit};")
            v.append("  endtable")
            v.append("endprimitive")
    v += ["module xc;"]
    for n in nets:
        v.append(f"  wire {safe(n)};")
    for n in sorted(in_ids):
        v.append(f"  reg r_{safe(nets[n])} = 1'b{init[n]}; assign {safe(nets[n])} = r_{safe(nets[n])};")
    for gi_, g in enumerate(m["gates"]):
        df, dr = g["dly"][0][0]
        if a.udp:
            v.append(f"  u_{g['cell']} #({round(dr * FS)}, {round(df * FS)}) c{gi_} ({safe(nets[g['out']])}, "
                     + ", ".join(safe(nets[x]) for x in g["ins"]) + ");")
            continue
        terms = []
        for s, bit in enumerate(g["tt"]):
            if bit:
                lits = [(safe(nets[x]) if (s >> j) & 1 else f"~{safe(nets[x])}") for j, x in enumerate(g["ins"])]
                terms.append("(" + " & ".join(lits) + ")")
        expr = " | ".join(terms) if terms else "1'b0"
        v.append(f"  assign #({round(dr * FS)}, {round(df * FS)}) {safe(nets[g['out']])} = {expr};")
    for i, f in enumerate(m["ffs"]):
        df, dr = f["dly"]
        v.append(f"  reg q{i} = 1'b{init[f['q']]}; always @(posedge {safe(nets[f['clk']])}) q{i} <= {safe(nets[f['d']])};")
        v.append(f"  assign #({round(dr * FS)}, {round(df * FS)}) {safe(nets[f['q']])} = q{i};")
    v.append("  initial begin")
    v.append(f'    $dumpfile("{a.out}/xc.vcd"); $dumpvars(0, xc);')
    tcur = 0
    for (t, n, val) in ev:
        if t > tcur:
            v.append(f"    #{t - tcur};")
            tcur = t
        v.append(f"    r_{safe(nets[n])} = 1'b{val};")
    v.append(f"    #{round(3 * a.period * FS)}; $finish;")
    v.append("  end")
    v.append("endmodule")
    src = f"{a.out}/xc.v"
    open(src, "w").write("\n".join(v) + "\n")
    subprocess.run([a.iverilog, "-o", f"{a.out}/xc.vvp", src], check=True)
    subprocess.run([os.path.join(os.path.dirname(a.iverilog), "vvp"), "-n", f"{a.out}/xc.vvp"], check=True, capture_output=True)
    ids, cnt, last = {}, {}, {}
    t = 0
    W0 = w0 * FS
    for line in open(f"{a.out}/xc.vcd"):
        s = line.strip()
        if s.startswith("$var"):
            q = s.split()
            ids.setdefault(q[3], []).append(q[4])
        elif s.startswith("#"):
            t = int(s[1:])
        elif s and s[0] in "01xz" and s[1:] in ids:
            for nm in ids[s[1:]]:
                if nm in last and s[0] != last[nm] and t >= W0:
                    cnt[nm] = cnt.get(nm, 0) + 1
                last[nm] = s[0]
    iv = {n: cnt.get(safe(n), 0) for n in nets}
    internal = [i for i in range(len(nets)) if i not in in_ids]
    diff = [(nets[i], tog[i], iv[nets[i]]) for i in internal if tog[i] != iv[nets[i]]]
    res = {"udp": a.udp, "t_in_ps": t_in, "verilog_style": a.verilog_style, "model": os.path.basename(a.model), "stim": os.path.basename(a.stim), "instance": p, "nets_internal": len(internal),
           "esim_total": sum(tog[i] for i in internal), "iverilog_total": sum(iv[nets[i]] for i in internal),
           "zero_delay_preedge_total": sum(ztog[i] for i in internal), "nets_differing": len(diff), "first_differences": diff[:20],
           "late": late}
    json.dump(res, open(f"{a.out}/xcheck{'_udp' if a.udp else ''}{'_vstyle' if a.verilog_style else ''}{'_tin%.1f' % t_in if a.t_in >= 0 else ''}.json", "w"), indent=1)
    os.remove(f"{a.out}/xc.vcd")
    print(json.dumps({k: res[k] for k in res if k != "first_differences"}), res["first_differences"][:5])


if __name__ == "__main__":
    main()
