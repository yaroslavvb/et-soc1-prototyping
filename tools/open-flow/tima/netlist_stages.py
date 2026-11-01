#!/usr/bin/env python3
"""One name per physical net, and a stage for each, in a yosys gate-level netlist of tima_top.

    netlist_stages.py --netlist tima_<arm>.v --lib a.lib ... --out tima_<arm>_staged.v --json stages_<arm>.json

Q133(a). Yosys writes a flattened netlist in which some nets carry two names (an `assign` alias, a vector and its part-
selects) and most carry abc's `_0123_`. A toggle count must see each physical net once, and the RTL bench's counter
(rtl-sim/fma_toggle_v2/settle_count.cpp) splits a count by stage from the signal's own name. So this rewrites the
netlist without changing a single connection:

  1. every alias is resolved (union-find over the assigns), and each net gets ONE scalar name; the module's ports keep
     their names and widths, so the netlist drops into the RTL in place of tima_top;
  2. each internal net is named for its stage, found from the netlist's own cones, in the RTL bench's convention for
     this unit (settle_count.cpp stage_of(), the `.lane_tima.tima.` branch):
       operand    f2_in_*      the A and B words into the F2 registers: the enable muxes, the sign logic, the
                               registers' outputs (and the ports f1_in1, f1_in2)
       multiplier f2_prod_*    everything between the F2 registers and the F3 product register: the four products and
                               their sum, the product register's enable mux, and its outputs (f3_prod_add_*)
       adder_norm f3_add_*     after the F3 register: C's zap gates, the sign extension and the 32-bit add (and f3_in3)
       result     f3_out       the output port only, as in the RTL
       control    ctl_*        the enables' and the signed flags' own logic, and anything feeding no data register
  3. every wire is declared with Verilator's public_flat_rw, so the simulator keeps each net as its own variable and a
     VCD gives each its own identifier: two nets that happen to compute the same value stay two nets.

The JSON lists every net with its stage, its driver cell and its fan-out, and the counts per stage.

SPDX-License-Identifier: Apache-2.0
"""
import argparse
import collections
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import liberty_models as LM  # noqa: E402


def lib_pins(paths):
    """cell -> ({pin: direction}, is_flop, is_latch)"""
    out = {}
    for p in paths:
        text = open(p).read()
        for name, body in LM.groups(text):
            pins = {}
            for pname, pbody in LM.subgroups(body, 'pin'):
                pins[pname] = LM.attr(LM.strip_nested(pbody), 'direction')
            out[name] = (pins, bool(LM.subgroups(body, 'ff')), bool(LM.subgroups(body, 'latch')))
    return out


ID = r'(?:\\\S+\s|[A-Za-z_][A-Za-z0-9_$]*)'


def norm_id(s):
    s = s.strip()
    return s[1:].strip() if s.startswith('\\') else s


def parse(path):
    text = open(path).read()
    m = re.search(r'\bmodule\s+(\w+)\s*\(([^)]*)\)\s*;', text)
    modname, body = m.group(1), text[m.end():text.rindex('endmodule')]
    widths, ports = {}, {}
    for d in re.finditer(r'^\s*(input|output|wire)\s*(\[(\d+):(\d+)\])?\s*(' + ID + r')\s*;', body, re.M):
        kind, msb, lsb, name = d.group(1), d.group(3), d.group(4), norm_id(d.group(5))
        w = (int(msb), int(lsb)) if msb is not None else None
        if kind in ('input', 'output'):
            ports[name] = (kind, w)
        widths.setdefault(name, w)
    cells = []
    for c in re.finditer(r'^\s*([A-Za-z0-9_]+)\s+(' + ID + r')\s*\((.*?)\);', body, re.M | re.S):
        typ, inst, conns = c.group(1), norm_id(c.group(2)), c.group(3)
        if typ in ('input', 'output', 'wire', 'assign', 'module'):
            continue
        pins = {}
        for pc in re.finditer(r'\.(\w+)\s*\(\s*(.*?)\s*\)\s*(?:,|$)', conns.strip(), re.S):
            pins[pc.group(1)] = pc.group(2).strip()
        cells.append((typ, inst, pins))
    assigns = []
    for a in re.finditer(r'^\s*assign\s+(.*?)\s*=\s*(.*?)\s*;\s*$', body, re.M):
        assigns.append((a.group(1), a.group(2)))
    return modname, ports, widths, cells, assigns


def bits_of(expr, widths):
    """Expand a reference (name, name[k], name[a:b], {..}, constant) into bit keys, MSB first."""
    expr = expr.strip()
    if expr.startswith('{'):
        inner = expr[1:-1]
        parts, depth, cur = [], 0, ''
        for ch in inner:
            if ch == '{':
                depth += 1
            if ch == '}':
                depth -= 1
            if ch == ',' and depth == 0:
                parts.append(cur)
                cur = ''
            else:
                cur += ch
        parts.append(cur)
        out = []
        for p in parts:
            out += bits_of(p, widths)
        return out
    m = re.fullmatch(r"(\d+)'b([01]+)", expr)
    if m:
        return ['1\'b' + b for b in m.group(2)]
    m = re.fullmatch(r'(' + ID + r')\s*(\[(\d+)(?::(\d+))?\])?', expr + ' ' if expr.startswith('\\') else expr)
    if not m:
        m = re.fullmatch(r'(\\\S+)\s*(\[(\d+)(?::(\d+))?\])?', expr)
    name = norm_id(m.group(1))
    if m.group(2) is None:
        w = widths.get(name)
        if w is None:
            return [name]
        hi, lo = w
        rng = range(hi, lo - 1, -1) if hi >= lo else range(hi, lo + 1)
        return [f"{name}[{i}]" for i in rng]
    hi = int(m.group(3))
    lo = int(m.group(4)) if m.group(4) is not None else hi
    rng = range(hi, lo - 1, -1) if hi >= lo else range(hi, lo + 1)
    return [f"{name}[{i}]" for i in rng]


class UF:
    def __init__(self):
        self.p = {}

    def find(self, x):
        self.p.setdefault(x, x)
        while self.p[x] != x:
            self.p[x] = self.p[self.p[x]]
            x = self.p[x]
        return x

    def union(self, a, b):
        ra, rb = self.find(a), self.find(b)
        if ra != rb:
            self.p[rb] = ra


def generic(a, modname, ports, cellconns, classes, rep, net, driver, readers, nets, sources, is_port, flops, latches, port_aliases):
    """--generic: one public scalar name per net; clock-network nets named clk_n<k>; no stages."""
    memo = {}

    def reaches_clk(n):
        if n in memo:
            return memo[n]
        memo[n] = False
        hit = False
        for ci, pin in readers.get(n, []):
            typ, inst, conns, pdir, flop, latch = cellconns[ci]
            if flop or latch:
                if pin == 'CLK':
                    hit = True
            else:
                for p2, b in conns.items():
                    if pdir.get(p2) == 'output' and reaches_clk(net(b)):
                        hit = True
            if hit:
                break
        memo[n] = hit
        return hit

    clock_ports = [p for p in ports if p.lower() in ('clock', 'clk')]
    newname, k, nclk = {}, 0, 0
    for n in sorted(nets, key=lambda x: x):
        chosen = rep[n][1] if n in rep else None
        if chosen is not None:
            newname[n] = chosen
            continue
        src = sources(n)
        if any(('in:' + c) in src for c in clock_ports) and reaches_clk(n):
            newname[n] = f"clk_n{nclk}"
            nclk += 1
        else:
            newname[n] = f"n{k}"
            k += 1

    def ref(b):
        return b if b.startswith("1'b") else newname[net(b)]

    lines = [f"// {modname} as gates: {os.path.basename(a.netlist)} rewritten by tools/open-flow/tima/netlist_stages.py --generic.",
             "// The same cells and the same connections; one scalar name per net; clock-network nets named clk_n*; every wire public.",
             f"module {modname}({', '.join(ports)});"]
    for p, (kind, w) in ports.items():
        lines.append(f"  {kind} {'[%d:%d] ' % w if w else ''}{p};")
    for n in sorted(nets, key=lambda x: newname[x]):
        if rep[n][1] is None:
            lines.append(f"  wire {newname[n]} /*verilator public_flat_rw*/;")
    for typ, inst, conns, pdir, flop, latch in cellconns:
        pins = ', '.join(f".{pin}({ref(b)})" for pin, b in conns.items())
        lines.append(f"  {typ} {('g_' + inst.strip('_')) if inst.startswith('_') else inst} ({pins});")
    for m, c in port_aliases:
        lines.append(f"  assign {m} = {c};")
    for b, (kind, p) in is_port.items():
        if kind == 'output' and net(b) not in driver:
            raise SystemExit(f"output {b} has no driver")
    lines.append("endmodule")
    open(a.out, 'w').write('\n'.join(lines) + '\n')
    summary = {"netlist": os.path.basename(a.netlist), "mode": "generic", "cells": len(cellconns), "flops": len(flops),
               "latches": len(latches), "nets": len(nets), "clock_network_nets": nclk, "data_nets": k,
               "aliases_resolved": sum(len(v) - 1 for v in classes.values()), "output_port_aliases": len(port_aliases)}
    json.dump(summary, open(a.json, 'w'), indent=1)
    print(f"{os.path.basename(a.netlist)}: {len(cellconns)} cells, {len(flops)} flops, {len(latches)} latches, {len(nets)} nets "
          f"({nclk} on the clock network), {summary['aliases_resolved']} alias names resolved")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--netlist', required=True)
    ap.add_argument('--lib', action='append', required=True)
    ap.add_argument('--out', required=True)
    ap.add_argument('--json', required=True)
    ap.add_argument('--generic', action='store_true',
                    help='any netlist (txfma_top): resolve aliases and make every wire public, name internal nets n<k>, and the nets '
                         'of the clock network (combinational from the clock port to a flop or latch clock pin) clk_n<k>, so the '
                         'counter drops them as it drops the RTL clock names; no stage split, latches allowed')
    a = ap.parse_args()
    libs = lib_pins(a.lib)
    modname, ports, widths, cells, assigns = parse(a.netlist)

    port_bits = []
    for p, (kind, w) in ports.items():
        port_bits += [(b, kind, p) for b in bits_of(p, widths)]
    is_port = {b: (kind, p) for b, kind, p in port_bits}

    uf = UF()
    for lhs, rhs in assigns:
        lb, rb = bits_of(lhs, widths), bits_of(rhs, widths)
        if len(lb) != len(rb):
            raise SystemExit(f"assign width mismatch: {lhs} = {rhs}")
        for x, y in zip(lb, rb):
            uf.union(x, y)

    # every bit any cell touches, and the canonical member of its alias class
    cellconns = []
    for typ, inst, pins in cells:
        if typ not in libs:
            raise SystemExit(f"cell type {typ} not in the liberty files")
        pdir, flop, latch = libs[typ]
        conns = {}
        for pin, ref in pins.items():
            b = bits_of(ref, widths)
            if len(b) != 1:
                raise SystemExit(f"{inst}.{pin} connects {len(b)} bits")
            conns[pin] = b[0]
        cellconns.append((typ, inst, conns, pdir, flop, latch))
    classes = collections.defaultdict(list)
    allbits = set(b for _, _, c, _, _, _ in cellconns for b in c.values()) | set(is_port) | set(uf.p)
    for b in allbits:
        if b.startswith("1'b"):
            continue
        classes[uf.find(b)].append(b)

    def canon_key(members):
        ps = [m for m in members if m in is_port]
        return ps

    rep = {}
    port_aliases = []          # (extra output port bit, the port bit that names its net): written as assigns
    for head, members in classes.items():
        ps = canon_key(members)
        outs = sorted(m for m in ps if is_port[m][0] == 'output')
        ins = [m for m in ps if is_port[m][0] == 'input']
        if len(ins) > 1:
            raise SystemExit(f"two input ports on one net: {members}")
        chosen = (ins or outs or [None])[0]
        for m in outs:
            if m != chosen:
                port_aliases.append((m, chosen))
        for m in members:
            rep[m] = (head, chosen)

    def net(b):
        if b.startswith("1'b"):
            return b
        return rep[b][0]

    # drivers and readers per net
    driver, readers = {}, collections.defaultdict(list)
    for i, (typ, inst, conns, pdir, flop, latch) in enumerate(cellconns):
        for pin, b in conns.items():
            n = net(b)
            if pdir.get(pin) == 'output':
                if n in driver:
                    raise SystemExit(f"net {n} has two drivers")
                driver[n] = (i, pin)
            elif pdir.get(pin) == 'input':
                readers[n].append((i, pin))
    for b, (kind, p) in is_port.items():
        n = net(b)
        if kind == 'input':
            driver[n] = ('port', p)
    nets = set(net(b) for b in allbits if not b.startswith("1'b"))

    # sources: input ports and flop outputs reached backwards through combinational cells
    memo_src = {}

    def sources(n, stack=()):
        if n in memo_src:
            return memo_src[n]
        d = driver.get(n)
        if d is None:
            s = frozenset(['const'])
        elif d[0] == 'port':
            s = frozenset(['in:' + d[1]])
        else:
            typ, inst, conns, pdir, flop, latch = cellconns[d[0]]
            if flop or latch:
                s = frozenset(['ff:' + inst])
            else:
                acc = set()
                for pin, b in conns.items():
                    if pdir.get(pin) == 'input' and not b.startswith("1'b"):
                        acc |= sources(net(b), stack + (n,))
                s = frozenset(acc)
        memo_src[n] = s
        return s

    sys.setrecursionlimit(1000000)
    flops = [i for i, c in enumerate(cellconns) if c[4]]
    latches = [i for i, c in enumerate(cellconns) if c[5]]
    if a.generic:
        generic(a, modname, ports, cellconns, classes, rep, net, driver, readers, nets, sources, is_port, flops, latches, port_aliases)
        return
    if latches:
        raise SystemExit(f"{len(latches)} latches: this classifier knows flip-flops only")
    # classify each flop by what its D input comes from
    ff_group = {}
    for i in flops:
        typ, inst, conns, pdir, flop, latch = cellconns[i]
        dsrc = set(x for x in sources(net(conns['D'])) if x != 'ff:' + inst)
        ins = set(x[3:] for x in dsrc if x.startswith('in:'))
        ffs = set(x[3:] for x in dsrc if x.startswith('ff:'))
        if not ffs and ins & {'f1_in1', 'f1_in2'}:
            ff_group[inst] = 'F2_A' if 'f1_in1' in ins and 'f1_in2' not in ins else ('F2_B' if 'f1_in2' in ins and 'f1_in1' not in ins else 'F2_AB')
        elif not ffs and ins == {'f2_zap_opd3'}:
            ff_group[inst] = 'F3_ZAP'
        elif ffs:
            ff_group[inst] = 'F3_PROD'
        else:
            ff_group[inst] = 'FF_OTHER:' + ','.join(sorted(ins))
    for i in flops:
        inst = cellconns[i][1]
        if ff_group[inst] == 'F3_PROD':
            typ, _, conns, _, _, _ = cellconns[i]
            up = set(ff_group.get(x[3:], '?') for x in sources(net(conns['D'])) if x.startswith('ff:') and x[3:] != inst)
            if not up <= {'F2_A', 'F2_B', 'F2_AB'}:
                ff_group[inst] = 'FF_OTHER:after ' + ','.join(sorted(up))

    # sinks: flop D pins (by group) and output ports reached forwards
    memo_snk = {}
    order = []

    def sinks(n):
        if n in memo_snk:
            return memo_snk[n]
        acc = set()
        b0 = [m for m in classes.get(n, [n])]
        if any(m in is_port and is_port[m][0] == 'output' for m in b0):
            acc.add('OUT')
        for ci, pin in readers.get(n, []):
            typ, inst, conns, pdir, flop, latch = cellconns[ci]
            if flop:
                acc.add(('D:' if pin == 'D' else pin + ':') + ff_group[inst])
            else:
                for p2, b in conns.items():
                    if pdir.get(p2) == 'output':
                        acc |= sinks(net(b))
        memo_snk[n] = frozenset(acc)
        return memo_snk[n]

    def stage(n):
        d = driver.get(n)
        if d is not None and d[0] != 'port' and cellconns[d[0]][4]:
            g = ff_group[cellconns[d[0]][1]]
            return {'F2_A': 'operand', 'F2_B': 'operand', 'F2_AB': 'operand', 'F3_PROD': 'multiplier', 'F3_ZAP': 'adder_norm'}.get(g, 'control')
        snk, src = sinks(n), sources(n)
        src_ff = set(ff_group.get(x[3:], '?') for x in src if x.startswith('ff:'))
        src_in = set(x[3:] for x in src if x.startswith('in:'))
        if 'OUT' in snk:
            return 'adder_norm'
        if any(s.startswith('D:F3_PROD') for s in snk) and src_ff & {'F2_A', 'F2_B', 'F2_AB'}:
            return 'multiplier'
        if any(s.startswith('D:F2_') for s in snk) and (src_in & {'f1_in1', 'f1_in2'} or src_ff & {'F2_A', 'F2_B', 'F2_AB'}):
            return 'operand'
        return 'control'

    prefix = {'operand': 'f2_in_g', 'multiplier': 'f2_prod_g', 'adder_norm': 'f3_add_g', 'control': 'ctl_g'}
    newname, stage_of, info = {}, {}, {}
    k = collections.Counter()
    for n in sorted(nets, key=lambda x: (rep[x][1] is None, x)):
        chosen = rep[n][1] if n in rep else None
        st = stage(n)
        d = driver.get(n)
        if chosen is not None:
            nm = chosen                                          # a port bit keeps its name
            kind, p = is_port[chosen]
            st = {'f1_in1': 'operand', 'f1_in2': 'operand', 'f3_in3': 'adder_norm', 'f3_out': 'result'}.get(p, 'control')
        elif d is not None and d[0] != 'port' and cellconns[d[0]][4]:
            g = ff_group[cellconns[d[0]][1]]
            base = {'F2_A': 'f2_in1_q', 'F2_B': 'f2_in2_q', 'F2_AB': 'f2_in_q', 'F3_PROD': 'f3_prod_add_q', 'F3_ZAP': 'f3_zap_q'}.get(g, 'ctl_ffq')
            nm = f"{base}{k[base]}"
            k[base] += 1
        else:
            nm = f"{prefix[st]}{k[st]}"
            k[st] += 1
        newname[n] = nm
        stage_of[n] = st
        info[nm] = {"stage": st, "driver": (cellconns[d[0]][0] if d and d[0] != 'port' else (('port ' + d[1]) if d else 'none')),
                    "fanout": len(readers.get(n, [])), "aliases": sorted(classes.get(n, [n]))}

    def ref(b):
        if b.startswith("1'b"):
            return b
        return newname[net(b)]

    lines = [f"// tima_top as gates: {os.path.basename(a.netlist)} rewritten by tools/open-flow/tima/netlist_stages.py.",
             "// The same cells and the same connections; one scalar name per net, named for its stage; every wire public.",
             f"module {modname}({', '.join(ports)});"]
    for p, (kind, w) in ports.items():
        lines.append(f"  {kind} {'[%d:%d] ' % w if w else ''}{p};")
    for n in sorted(nets, key=lambda x: newname[x]):
        nm = newname[n]
        if rep[n][1] is None:
            lines.append(f"  wire {nm} /*verilator public_flat_rw*/;")
    # an output port bit whose class has no driver cell but an input port is impossible (checked above)
    for typ, inst, conns, pdir, flop, latch in cellconns:
        pins = ', '.join(f".{pin}({ref(b)})" for pin, b in conns.items())
        lines.append(f"  {typ} {('g_' + inst.strip('_')) if inst.startswith('_') else inst} ({pins});")
    for m, c in port_aliases:
        lines.append(f"  assign {m} = {c};")
    for b, (kind, p) in is_port.items():
        if kind == 'output' and net(b) not in driver:
            raise SystemExit(f"output {b} has no driver")
    lines.append("endmodule")
    open(a.out, 'w').write('\n'.join(lines) + '\n')

    per = collections.Counter(stage_of.values())
    groups = collections.Counter(ff_group.values())
    summary = {"netlist": os.path.basename(a.netlist), "cells": len(cellconns), "flops": len(flops), "nets": len(nets),
               "nets_by_stage": dict(per), "flop_groups": dict(groups), "aliases_resolved": sum(len(v) - 1 for v in classes.values()), "output_port_aliases": len(port_aliases),
               "nets_detail": info}
    json.dump(summary, open(a.json, 'w'), indent=1)
    print(f"{os.path.basename(a.netlist)}: {len(cellconns)} cells, {len(flops)} flops {dict(groups)}, {len(nets)} nets "
          f"{dict(per)}, {summary['aliases_resolved']} alias names resolved")


if __name__ == '__main__':
    main()
