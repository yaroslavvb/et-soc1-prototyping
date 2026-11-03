#!/usr/bin/env python3
"""Q138(g): a gate-level netlist annotated with cell delays from its liberty files (NLDM, the flow's TT corner).

    annotate.py --netlist tima_booth_tree_staged.v[.gz] --lib a.lib ... --out model.pkl [--wire-base 0.2 --wire-per-fo 0.1]
                [--ext-load <fF on each output port>] [--in-slew 10]

For every cell instance: its truth table (from the liberty `function`), and for every input pin and every input state after
the change, the delay to a rising and to a falling output, read from the timing group whose `when` holds in that state
(cell_rise / cell_fall, bilinear in input transition x output load). A flip-flop gets its CLK->Q rise and fall delays. Loads:
the fanout pins' liberty capacitance plus a wire load (wire-base + wire-per-fo x fanout, fF; no placement). Slews: propagated in
topological order from the flip-flops and the input ports (each net's transition = the largest its driver's arcs give).
"""
import argparse, gzip, math, os, pickle, re, sys
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "tima"))
from liberty_models import groups, subgroups, attr, strip_nested, to_verilog


class Bt(int):
    def __invert__(self): return Bt(1 - int(self))
    def __and__(self, o): return Bt(int(self) & int(o))
    def __or__(self, o): return Bt(int(self) | int(o))
    def __xor__(self, o): return Bt(int(self) ^ int(o))
    __rand__, __ror__, __rxor__ = __and__, __or__, __xor__


def compile_fn(expr):
    v = to_verilog(expr).replace("1'b0", "Bt(0)").replace("1'b1", "Bt(1)")
    code = compile(v, "<liberty>", "eval")
    return lambda env: int(eval(code, {"Bt": Bt}, env))


def floats(s):
    return [float(x) for x in s.replace('"', ' ').replace('\\', ' ').replace(',', ' ').split()]


def table(body, kind):
    g = subgroups(body, kind)
    if not g:
        return None
    _, b = g[0]
    i1 = floats(re.search(r'index_1\s*\(([^)]*)\)', b).group(1))
    i2 = floats(re.search(r'index_2\s*\(([^)]*)\)', b).group(1))
    vals = floats(re.search(r'values\s*\((.*?)\)\s*;', b, re.S).group(1))
    assert len(vals) == len(i1) * len(i2), (kind, len(vals))
    return (i1, i2, [vals[r * len(i2):(r + 1) * len(i2)] for r in range(len(i1))])


def interp1(xs, x):
    """index and weight for linear interpolation / extrapolation on a sorted axis"""
    if x <= xs[0]:
        j = 0
    elif x >= xs[-1]:
        j = len(xs) - 2
    else:
        j = max(k for k in range(len(xs) - 1) if xs[k] <= x)
    w = (x - xs[j]) / (xs[j + 1] - xs[j])
    return j, w


def lookup(t, slew, load):
    i1, i2, v = t
    j, wj = interp1(i1, slew)
    k, wk = interp1(i2, load)
    a = v[j][k] * (1 - wk) + v[j][k + 1] * wk
    b = v[j + 1][k] * (1 - wk) + v[j + 1][k + 1] * wk
    return a * (1 - wj) + b * wj


def parse_libs(paths, used):
    cells = {}
    for p in paths:
        text = open(p).read()
        for name, body in groups(text):
            if name not in used:
                continue
            pins = {}
            for pname, pbody in subgroups(body, 'pin'):
                own = strip_nested(pbody)
                d = attr(own, 'direction')
                cap = attr(own, 'capacitance')
                pin = {"dir": d, "cap": float(cap) if cap else 0.0, "function": attr(own, 'function'), "timing": []}
                if d == 'output':
                    for targs, tb in subgroups(pbody, 'timing'):
                        town = strip_nested(tb)
                        pin["timing"].append({"related": attr(town, 'related_pin'), "when": attr(town, 'when'),
                                              "type": attr(town, 'timing_type') or 'combinational',
                                              "cell_rise": table(tb, 'cell_rise'), "cell_fall": table(tb, 'cell_fall'),
                                              "rise_tr": table(tb, 'rise_transition'), "fall_tr": table(tb, 'fall_transition')})
                pins[pname] = pin
            ff = subgroups(body, 'ff')
            cells[name] = {"pins": pins, "ff": ({"q": ff[0][0].split(',')[0].strip(), "clk": attr(ff[0][1], 'clocked_on'),
                                                "next": attr(ff[0][1], 'next_state')} if ff else None)}
    missing = used - set(cells)
    assert not missing, missing
    return cells


INST = re.compile(r'^\s*([A-Za-z0-9_]+)\s+([A-Za-z0-9_\\\[\]\.$]+)\s*\((.*)\)\s*;\s*$')
CONN = re.compile(r'\.([A-Za-z0-9_]+)\s*\(\s*([^()\s]+)\s*\)')


def parse_netlist(path):
    op = gzip.open if path.endswith('.gz') else open
    text = op(path, 'rt').read()
    ports = {"input": [], "output": []}
    insts = []
    for line in text.splitlines():
        s = line.strip()
        m = re.match(r'^(input|output)\s*(\[(\d+):(\d+)\])?\s*([A-Za-z0-9_]+)\s*;', s)
        if m:
            d, _, hi, lo, n = m.groups()
            if hi is None:
                ports[d].append(n)
            else:
                ports[d] += [f"{n}[{i}]" for i in range(int(lo), int(hi) + 1)]
            continue
        if s.startswith(('module', 'endmodule', 'wire', '//', 'assign')) or not s:
            if s.startswith('assign'):
                raise SystemExit(f"unexpected assign: {s}")
            continue
        m = INST.match(s)
        if m:
            insts.append((m.group(1), m.group(2), dict(CONN.findall(m.group(3)))))
    return ports, insts


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--netlist', required=True)
    ap.add_argument('--lib', action='append', required=True)
    ap.add_argument('--out', required=True)
    ap.add_argument('--wire-base', type=float, default=0.2)
    ap.add_argument('--wire-per-fo', type=float, default=0.1)
    ap.add_argument('--ext-load', type=float, default=-1, help='fF on each output port; default = one DFFHQx4 D pin + wire')
    ap.add_argument('--in-slew', type=float, default=-1, help='ps; default = the flip-flops own output transition')
    ap.add_argument('--delay-scale', type=float, default=1.0)
    a = ap.parse_args()
    ports, insts = parse_netlist(a.netlist)
    used = set(c for c, _, _ in insts)
    cells = parse_libs(a.lib, used | {"DFFHQx4_ASAP7_75t_R"})
    # nets
    driver, fanout = {}, {}
    for n in ports["input"]:
        driver[n] = ("port", None)
    for idx, (c, name, conn) in enumerate(insts):
        for pin, net in conn.items():
            d = cells[c]["pins"][pin]["dir"]
            if d == 'output':
                assert net not in driver, f"two drivers {net}"
                driver[net] = ("cell", idx, pin)
            else:
                fanout.setdefault(net, []).append((idx, pin))
    dpin = cells["DFFHQx4_ASAP7_75t_R"]["pins"]["D"]["cap"]
    ext = a.ext_load if a.ext_load >= 0 else dpin + a.wire_base + a.wire_per_fo
    load = {}
    for net in driver:
        fo = fanout.get(net, [])
        c = sum(cells[insts[i][0]]["pins"][p]["cap"] for i, p in fo) + a.wire_base + a.wire_per_fo * len(fo)
        if net in ports["output"]:
            c += ext
        load[net] = c
    # topological order of combinational cells
    is_ff = [cells[c]["ff"] is not None for c, _, _ in insts]
    slew = {}
    # flip-flop outputs first: CLK->Q transition at load, clock slew assumed 10 ps
    CLK_SLEW = 10.0
    ffq_slew = []
    for idx, (c, name, conn) in enumerate(insts):
        if is_ff[idx]:
            q = cells[c]["ff"]["q"]
            outpin = [p for p, pin in cells[c]["pins"].items() if pin["dir"] == 'output'][0]
            tg = [t for t in cells[c]["pins"][outpin]["timing"] if t["type"] == 'rising_edge'][0]
            net = conn[outpin]
            s = max(lookup(tg["rise_tr"], CLK_SLEW, load[net]), lookup(tg["fall_tr"], CLK_SLEW, load[net]))
            slew[net] = s
            ffq_slew.append(s)
    in_slew = a.in_slew if a.in_slew >= 0 else (sum(ffq_slew) / len(ffq_slew) if ffq_slew else 20.0)
    for n in ports["input"]:
        slew[n] = in_slew
    # Kahn's order
    pending = {}
    for idx, (c, name, conn) in enumerate(insts):
        if not is_ff[idx]:
            pending[idx] = sum(1 for p, net in conn.items() if cells[c]["pins"][p]["dir"] == 'input')
    ready = [idx for idx in pending if all((cells[insts[idx][0]]["pins"][p]["dir"] != 'input') or (net in slew)
                                         for p, net in insts[idx][2].items())]
    done = set()
    order = []
    import collections
    q = collections.deque(ready)
    queued = set(ready)
    while q:
        idx = q.popleft()
        c, name, conn = insts[idx]
        ins = [p for p, pin in cells[c]["pins"].items() if pin["dir"] == 'input']
        if not all(conn[p] in slew for p in ins):
            continue
        outs = [p for p, pin in cells[c]["pins"].items() if pin["dir"] == 'output']
        for op_ in outs:
            net = conn[op_]
            s = 0.0
            for t in cells[c]["pins"][op_]["timing"]:
                rs = slew[conn[t["related"]]]
                s = max(s, lookup(t["rise_tr"], rs, load[net]), lookup(t["fall_tr"], rs, load[net]))
            slew[net] = s
            for (j, p) in fanout.get(net, []):
                if j in pending and j not in queued:
                    cj = insts[j]
                    insj = [pp for pp, pin in cells[cj[0]]["pins"].items() if pin["dir"] == 'input']
                    if all(cj[2][pp] in slew for pp in insj):
                        q.append(j)
                        queued.add(j)
        order.append(idx)
        done.add(idx)
    nff = sum(is_ff)
    assert len(done) == len(insts) - nff, (len(done), len(insts), nff)
    # build the model
    nets = sorted(driver)
    nid = {n: i for i, n in enumerate(nets)}
    gates, ffs = [], []
    for idx, (c, name, conn) in enumerate(insts):
        cell = cells[c]
        ins = [p for p, pin in cell["pins"].items() if pin["dir"] == 'input']
        outs = [p for p, pin in cell["pins"].items() if pin["dir"] == 'output']
        if is_ff[idx]:
            outpin = outs[0]
            tg = [t for t in cell["pins"][outpin]["timing"] if t["type"] == 'rising_edge'][0]
            net = conn[outpin]
            d_r = lookup(tg["cell_rise"], CLK_SLEW, load[net]) * a.delay_scale
            d_f = lookup(tg["cell_fall"], CLK_SLEW, load[net]) * a.delay_scale
            assert cell["ff"]["next"].strip() == "D" and cell["ff"]["clk"].strip() == "CLK", cell["ff"]
            ffs.append({"name": name, "cell": c, "d": nid[conn["D"]], "clk": nid[conn["CLK"]], "q": nid[net], "dly": (d_f, d_r)})
            continue
        for op_ in outs:
            fn = compile_fn(cell["pins"][op_]["function"])
            n = len(ins)
            tt = []
            for k in range(1 << n):
                env = {p: Bt((k >> i) & 1) for i, p in enumerate(ins)}
                tt.append(fn(env))
            net = conn[op_]
            dly = []   # dly[pin][state] = (fall, rise)
            for i, p in enumerate(ins):
                tgs = [t for t in cell["pins"][op_]["timing"] if t["related"] == p]
                assert tgs, (c, p)
                rs = slew[conn[p]]
                row = []
                for k in range(1 << n):
                    env = {pp: Bt((k >> j) & 1) for j, pp in enumerate(ins)}
                    match = [t for t in tgs if t["when"] and compile_fn(t["when"])(env)]
                    if not match:
                        match = [t for t in tgs if not t["when"]] or tgs
                    fr = [lookup(t["cell_fall"], rs, load[net]) for t in match if t["cell_fall"]]
                    rr = [lookup(t["cell_rise"], rs, load[net]) for t in match if t["cell_rise"]]
                    row.append(((sum(fr) / len(fr)) * a.delay_scale if fr else None,
                                (sum(rr) / len(rr)) * a.delay_scale if rr else None))
                # an arc missing one edge (unate arcs list both; keep a fallback to the other edge's mean)
                allf = [x[0] for x in row if x[0] is not None]
                allr = [x[1] for x in row if x[1] is not None]
                row = [(x[0] if x[0] is not None else (sum(allf) / len(allf) if allf else sum(allr) / len(allr)),
                        x[1] if x[1] is not None else (sum(allr) / len(allr) if allr else sum(allf) / len(allf))) for x in row]
                dly.append(row)
            gates.append({"name": name, "cell": c, "ins": [nid[conn[p]] for p in ins], "pins": ins, "out": nid[net], "tt": tt, "dly": dly})
    model = {"nets": nets, "inputs": [nid[n] for n in ports["input"]], "outputs": [nid[n] for n in ports["output"]],
             "input_names": ports["input"], "output_names": ports["output"], "gates": gates, "ffs": ffs,
             "load": [load[n] for n in nets], "slew": [slew.get(n, 0.0) for n in nets],
             "params": {"wire_base": a.wire_base, "wire_per_fo": a.wire_per_fo, "ext_load": ext, "in_slew": in_slew,
                        "clk_slew": CLK_SLEW, "delay_scale": a.delay_scale, "netlist": os.path.basename(a.netlist),
                        "libs": [os.path.basename(x) for x in a.lib]}}
    # static settle time: longest path from FFs/inputs, worst arc
    arr = {}
    for f in ffs:
        arr[f["q"]] = max(f["dly"])
    for n in model["inputs"]:
        arr.setdefault(n, 0.0)
    gate_of_out = {g["out"]: g for g in gates}
    gi = {insts[i][1]: i for i in range(len(insts))}
    for idx in order:
        name = insts[idx][1]
        for g in [g for g in gates if g["name"] == name] if False else []:
            pass
    by_name = {}
    for g in gates:
        by_name.setdefault(g["name"], []).append(g)
    for idx in order:
        for g in by_name.get(insts[idx][1], []):
            arr[g["out"]] = max(arr[g["ins"][i]] + max(max(x) for x in g["dly"][i]) for i in range(len(g["ins"])))
    model["static_arrival_ps_max"] = max(arr.values())
    model["static_arrival_ps_to_ffD_max"] = max([arr[f["d"]] for f in ffs] or [0.0])
    pickle.dump(model, open(a.out, "wb"))
    dd = [x for g in gates for row in g["dly"] for st in row for x in st]
    print(f"{os.path.basename(a.netlist)}: {len(gates)} gates, {len(ffs)} ffs, {len(nets)} nets; delay ps min {min(dd):.1f} "
          f"median {sorted(dd)[len(dd)//2]:.1f} max {max(dd):.1f}; clk->q {min([min(f['dly']) for f in ffs] or [0]):.1f}-"
          f"{max([max(f['dly']) for f in ffs] or [0]):.1f}; in_slew {in_slew:.1f}; longest path {model['static_arrival_ps_max']:.0f} ps "
          f"(to a flip-flop D {model['static_arrival_ps_to_ffD_max']:.0f})")


if __name__ == '__main__':
    main()
