#!/usr/bin/env python3
"""Q138(g): the simulator checked on small circuits whose glitch counts are known, and against Icarus Verilog.

Circuits (ASAP7 cells, annotated by annotate.py exactly as the netlists are):
  pulse_k   y = XOR2(x, BUF^k(x)), k = 0, 1, 2, 4, 8. Each toggle of x makes y pulse once (2 transitions) when the buffered copy
            arrives after y's own pending transition matures, else none (k = 0: both pins move together, no pulse ever).
  hazard_k  y = AND2(x, INV^k(x)), k = 1, 5 (odd). A static-0 hazard on every rising x, of width = the inverter chain's delay:
            swallowed by the AND's inertial delay for k = 1, passed (2 transitions) for k = 5; never on a falling x.
  rca8      an 8-bit ripple-carry adder (XOR2 sums, MAJ carries, 4 buffers on every carry hop so carries are much slower
            than sums): A 0x00 -> 0xFF with B = 0x01 makes every sum bit 1..7 rise as A arrives and fall when the carry does,
            and A 0xFF -> 0x00 the same in reverse: one pulse (2 transitions) per sum bit 1..7 on every edge of A; s0 and the
            carries move once per edge. Zero delay: s0 and c1..c8 move once per edge, s1..s7 never.
For each, the expectation from first principles is set beside the simulator's count, and the same circuit with the same
per-instance delays (pin-independent, the worst arc of each edge) runs in Icarus Verilog as `assign #(rise, fall)` cells,
an inertial continuous assignment, transitions counted from its VCD; the simulator runs that pin-independent model too.
"""
import json, os, pickle, random, subprocess, sys, tempfile
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from esim import Sim
OUT = sys.argv[1]
LIBD = sys.argv[2]
IVERILOG = sys.argv[3]
LIBS = sorted(os.path.join(LIBD, f) for f in os.listdir(LIBD) if f.endswith('.lib'))
os.makedirs(OUT, exist_ok=True)


def netlist(name, body, ins, outs):
    v = [f"module {name}({', '.join(ins + outs)});"]
    v += [f"  input {i};" for i in ins] + [f"  output {o};" for o in outs] + body + ["endmodule"]
    p = os.path.join(OUT, f"{name}.v")
    open(p, "w").write("\n".join(v) + "\n")
    return p


def annotate(path):
    m = path[:-2] + ".pkl"
    cmd = [sys.executable, os.path.join(HERE, "annotate.py"), "--netlist", path, "--out", m]
    for l in LIBS:
        cmd += ["--lib", l]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode:
        raise SystemExit(r.stderr)
    return pickle.load(open(m, "rb"))


def pin_independent(model):
    """the same model with every arc of a cell given the cell's worst delay for each output edge"""
    import copy
    m = copy.deepcopy(model)
    for g in m["gates"]:
        df = max(st[0] for row in g["dly"] for st in row)
        dr = max(st[1] for row in g["dly"] for st in row)
        g["dly"] = [[(df, dr) for _ in row] for row in g["dly"]]
    return m


def simulate(model, wave, period=1000.0):
    """wave: list of {input_name: value} per step (step i at i*period ps)."""
    sim = Sim(model)
    nid = {n: i for i, n in enumerate(model["nets"])}
    # settle the initial state at zero delay: evaluate gates in a fixed-point loop
    val = [0] * len(model["nets"])
    for n, v in wave[0].items():
        val[nid[n]] = v
    for _ in range(200):
        ch = False
        for g in model["gates"]:
            st = sum(val[x] << j for j, x in enumerate(g["ins"]))
            if val[g["out"]] != g["tt"][st]:
                val[g["out"]] = g["tt"][st]
                ch = True
        if not ch:
            break
    steps = [(float(i), {nid[n]: v for n, v in w.items()}) for i, w in enumerate(wave) if i > 0]
    tog, ztog, samples, late = sim.run(val, steps, period, 0.0, w0=0.0)
    # zero-delay: the settled value after each step vs the one before
    return {n: tog[nid[n]] for n in model["nets"]}, val


def zero_delay_toggles(model, wave):
    nid = {n: i for i, n in enumerate(model["nets"])}
    val = [0] * len(model["nets"])
    prev = None
    z = [0] * len(model["nets"])
    for w in wave:
        for n, v in w.items():
            val[nid[n]] = v
        for _ in range(200):
            ch = False
            for g in model["gates"]:
                st = sum(val[x] << j for j, x in enumerate(g["ins"]))
                if val[g["out"]] != g["tt"][st]:
                    val[g["out"]] = g["tt"][st]
                    ch = True
            if not ch:
                break
        if prev is not None:
            for i in range(len(val)):
                z[i] += val[i] != prev[i]
        prev = list(val)
    return {n: z[nid[n]] for n in model["nets"]}


def iverilog_count(model, wave, name, period=1000):
    """Icarus Verilog: every cell as `assign #(rise, fall) out = f(ins)` with the model's (pin-independent) delays, in fs."""
    nets = model["nets"]
    ins = model["input_names"]
    v = ["`timescale 1fs/1fs", f"module dut_{name};"]
    for n in nets:
        v.append(f"  wire {safe(n)};")
    for n in ins:
        v.append(f"  reg r_{safe(n)}; assign {safe(n)} = r_{safe(n)};")
    for g in model["gates"]:
        df = g["dly"][0][0][0]
        dr = g["dly"][0][0][1]
        terms = []
        for st, bit in enumerate(g["tt"]):
            if bit:
                lits = [(safe(nets[x]) if (st >> j) & 1 else f"~{safe(nets[x])}") for j, x in enumerate(g["ins"])]
                terms.append("(" + " & ".join(lits) + ")")
        expr = " | ".join(terms) if terms else "1'b0"
        v.append(f"  assign #({int(round(dr * 1000))}, {int(round(df * 1000))}) {safe(nets[g['out']])} = {expr};")
    v.append("  integer i;")
    v.append("  initial begin")
    v.append(f'    $dumpfile("{os.path.join(OUT, name + "_iv.vcd")}"); $dumpvars(0, dut_{name});')
    for i, w in enumerate(wave):
        for n, val in w.items():
            v.append(f"    r_{safe(n)} = 1'b{val};")
        v.append(f"    #{period * 1000};")
    v.append("    $finish;")
    v.append("  end")
    v.append("endmodule")
    src = os.path.join(OUT, f"{name}_iv.v")
    open(src, "w").write("\n".join(v) + "\n")
    exe = os.path.join(OUT, f"{name}_iv.vvp")
    subprocess.run([IVERILOG, "-o", exe, src], check=True)
    vvp = os.path.join(os.path.dirname(IVERILOG), "vvp")
    subprocess.run([vvp, "-n", exe], check=True, capture_output=True, cwd=OUT)
    # count transitions after the first period (the initial settle) from the VCD
    ids, cnt, last = {}, {}, {}
    t = 0
    for line in open(os.path.join(OUT, name + "_iv.vcd")):
        s = line.strip()
        if s.startswith("$var"):
            p = s.split()
            ids[p[3]] = p[4]
        elif s.startswith("#"):
            t = int(s[1:])
        elif s and s[0] in "01xz" and s[1:] in ids:
            n = ids[s[1:]]
            if n in last and t >= period * 1000 and s[0] != last[n]:
                cnt[n] = cnt.get(n, 0) + 1
            last[n] = s[0]
    return {n: cnt.get(safe(n), 0) for n in nets}


def safe(n):
    return n.replace("[", "_").replace("]", "_")


def main():
    results = {}
    rnd = random.Random(20261102)
    # pulse_k
    for k in (0, 1, 2, 4, 8):
        body = []
        prev = "x"
        for j in range(k):
            body.append(f"  BUFx2_ASAP7_75t_R b{j} (.A({prev}), .Y(d{j}));")
            prev = f"d{j}"
        body.append(f"  XOR2xp5_ASAP7_75t_R gx (.A(x), .B({prev}), .Y(y));")
        p = netlist(f"pulse_{k}", body, ["x"], ["y"])
        m = annotate(p)
        wave = [{"x": i % 2} for i in range(21)]          # 20 toggles of x
        tg, _ = simulate(m, wave)
        gx = [g for g in m["gates"] if g["name"] == "gx"][0]
        chain = [0.0, 0.0]   # chain delay for a rising and a falling x
        for j in range(k):
            gb = [g for g in m["gates"] if g["name"] == f"b{j}"][0]
            chain[0] += gb["dly"][0][1][1]
            chain[1] += gb["dly"][0][0][0]
        # first pin to move is A (x); y's pending transition from pin A matures at dA; the copy arrives at the chain delay
        exp = 0
        for i in range(1, 21):
            xr = i % 2
            stA = (xr) | ((1 - xr) << 1)        # after x moves, B still the old x
            yv = gx["tt"][stA]
            dA = gx["dly"][0][stA][yv]
            arr = chain[0] if xr else chain[1]
            if k > 0 and arr > dA:
                exp += 2
        mp = pin_independent(m)
        tgp, _ = simulate(mp, wave)
        iv = iverilog_count(mp, wave, f"pulse_{k}")
        results[f"pulse_{k}"] = {"x_toggles": 20, "expected_y": exp, "sim_y": tg["y"], "sim_pin_independent_y": tgp["y"],
                                 "iverilog_y": iv["y"], "zero_delay_y": 0,
                                 "xor_pinA_delay_ps": [round(gx["dly"][0][1][1], 2), round(gx["dly"][0][2][0], 2)],
                                 "chain_ps": [round(c, 2) for c in chain]}
    # hazard_k
    for k in (1, 5):
        body = []
        prev = "x"
        for j in range(k):
            body.append(f"  INVx1_ASAP7_75t_R i{j} (.A({prev}), .Y(n{j}));")
            prev = f"n{j}"
        body.append(f"  AND2x2_ASAP7_75t_R ga (.A(x), .B({prev}), .Y(y));")
        p = netlist(f"hazard_{k}", body, ["x"], ["y"])
        m = annotate(p)
        wave = [{"x": i % 2} for i in range(21)]
        tg, _ = simulate(m, wave)
        ga = [g for g in m["gates"] if g["name"] == "ga"][0]
        chain = 0.0
        for j in range(k):
            gi = [g for g in m["gates"] if g["name"] == f"i{j}"][0]
            # rising x: inverters alternate fall, rise, ...
            st = 1 if j % 2 == 0 else 0
            chain += gi["dly"][0][st][1 - st]
        dA = ga["dly"][0][3][1]                      # x rises with B still 1: y rises after dA
        exp = sum(2 for i in range(1, 21) if i % 2 == 1 and chain > dA)
        mp = pin_independent(m)
        tgp, _ = simulate(mp, wave)
        iv = iverilog_count(mp, wave, f"hazard_{k}")
        results[f"hazard_{k}"] = {"x_rises": 10, "expected_y": exp, "sim_y": tg["y"], "sim_pin_independent_y": tgp["y"],
                                  "iverilog_y": iv["y"], "zero_delay_y": 0, "and_delay_ps": round(dA, 2),
                                  "inverter_chain_ps": round(chain, 2)}
    # rca8 with slow carries
    body = []
    for i in range(8):
        cin = "cz" if i == 0 else f"cb{i}_3"
        body.append(f"  XOR2xp5_ASAP7_75t_R p{i} (.A(a{i}), .B(b{i}), .Y(pp{i}));")
        body.append(f"  XOR2xp5_ASAP7_75t_R s{i} (.A(pp{i}), .B({cin}), .Y(s{i}_o));")
        body.append(f"  MAJx2_ASAP7_75t_R m{i} (.A(a{i}), .B(b{i}), .C({cin}), .Y(c{i + 1}));")
        prev = f"c{i + 1}"
        for j in range(4):
            body.append(f"  BUFx2_ASAP7_75t_R cb{i + 1}_{j} (.A({prev}), .Y(cb{i + 1}_{j}));")
            prev = f"cb{i + 1}_{j}"
    ins = [f"a{i}" for i in range(8)] + [f"b{i}" for i in range(8)] + ["cz"]
    p = netlist("rca8", body, ins, [f"s{i}_o" for i in range(8)] + ["cb8_3"])
    m = annotate(p)
    w0 = {**{f"a{i}": 0 for i in range(8)}, **{f"b{i}": (1 if i == 0 else 0) for i in range(8)}, "cz": 0}
    w1 = {**{f"a{i}": 1 for i in range(8)}}
    w2 = {**{f"a{i}": 0 for i in range(8)}}
    wave = [w0, w1, w2, w1, w2]                         # two rises and two falls of A
    tg, _ = simulate(m, wave)
    zd = zero_delay_toggles(m, wave)
    mp = pin_independent(m)
    tgp, _ = simulate(mp, wave)
    iv = iverilog_count(mp, wave, "rca8")
    sums = [f"s{i}_o" for i in range(8)]
    exp_sum = {s: (4 if s == "s0_o" else 8) for s in sums}
    results["rca8"] = {"expected_sum_transitions_per_edge_of_A": {"s0": 1, "s1..s7": 2}, "rises": 2, "falls": 2,
                       "expected_sum": exp_sum, "sim_equals_expected": all(tg[s] == exp_sum[s] for s in sums),
                       "sim_sum": {s: tg[s] for s in sums}, "zero_delay_sum": {s: zd[s] for s in sums},
                       "sim_pin_independent_sum": {s: tgp[s] for s in sums}, "iverilog_sum": {s: iv[s] for s in sums},
                       "sim_total": sum(tg.values()), "iverilog_total": sum(iv[n] for n in m["nets"] if n not in ins),
                       "sim_pi_total": sum(tgp[n] for n in m["nets"] if n not in ins)}
    # random stimulus on rca8: the event engine against Icarus Verilog, net by net
    wave = [w0]
    for i in range(60):
        w = {f"a{j}": rnd.randint(0, 1) for j in range(8)}
        w.update({f"b{j}": rnd.randint(0, 1) for j in range(8)})
        wave.append(w)
    tgp, _ = simulate(mp, wave)
    iv = iverilog_count(mp, wave, "rca8_random")
    nonin = [n for n in m["nets"] if n not in ins]
    diff = {n: (tgp[n], iv[n]) for n in nonin if tgp[n] != iv[n]}
    results["rca8_random_vs_iverilog"] = {"steps": 60, "sim_total": sum(tgp[n] for n in nonin), "iverilog_total": sum(iv[n] for n in nonin),
                                          "nets_differing": len(diff), "differences": diff,
                                          "zero_delay_total": sum(zero_delay_toggles(m, wave)[n] for n in nonin)}
    for k, x in results.items():
        if k.startswith(("pulse", "hazard")):
            x["sim_equals_expected"] = x["sim_y"] == x["expected_y"]
            x["pin_independent_sim_equals_iverilog"] = x["sim_pin_independent_y"] == x["iverilog_y"]
    results["rca8"]["pin_independent_sim_equals_iverilog"] = results["rca8"]["sim_pin_independent_sum"] == results["rca8"]["iverilog_sum"]
    json.dump(results, open(os.path.join(OUT, "validate.json"), "w"), indent=1)
    for k, v in results.items():
        print(k, json.dumps(v)[:400])


if __name__ == "__main__":
    main()
