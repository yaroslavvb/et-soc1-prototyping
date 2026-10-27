#!/usr/bin/env python3
"""Parse an OpenROAD write_verilog flat gate netlist: wires, ports, instances, connections."""
import re, sys, json

CELL = re.compile(r'^\s*([A-Za-z][A-Za-z0-9_]*_ASAP7_75t_[A-Z]+)\s+(\\?\S+?)\s*\(')
IDENT = r'(?:\\[^\s]+\s|[A-Za-z_][A-Za-z0-9_$]*)'

def parse(path):
    txt = open(path, errors="replace").read()
    # ports / wires
    ports = {}
    wires = []
    decl = re.compile(r'^\s*(input|output|inout|wire)\s+(?:\[(\d+):(\d+)\]\s+)?(\\?[^\s;]+)\s*;', re.M)
    for m in decl.finditer(txt):
        kind, hi, lo, name = m.group(1), m.group(2), m.group(3), m.group(4)
        name = name.rstrip()
        if name.startswith('\\'):
            name = name[1:]
        if hi is None:
            names = [name]
        else:
            hi, lo = int(hi), int(lo)
            step = 1 if hi >= lo else -1
            names = [f"{name}[{i}]" for i in range(lo, hi + step, 1)] if hi >= lo else [f"{name}[{i}]" for i in range(hi, lo + 1)]
        if kind in ("input", "output", "inout"):
            for n in names:
                ports[n] = kind
        else:
            wires.extend(names)
    # instances: celltype name ( .PIN(net), ... );
    insts = []
    i = 0
    lines = txt.split('\n')
    # join statements: find "CELLTYPE inst (" then read to the matching ");"
    body = txt
    pat = re.compile(r'(^|\n)\s*([A-Za-z][A-Za-z0-9_]*_ASAP7_75t_[A-Z]+)\s+((?:\\[^\s]+)|(?:[A-Za-z_][A-Za-z0-9_$\[\]\.]*))\s*\(', re.M)
    conn = re.compile(r'\.([A-Za-z0-9_]+)\s*\(\s*((?:\\[^\s)]+\s?)|(?:[^)]*?))\s*\)')
    for m in pat.finditer(body):
        ct, inst = m.group(2), m.group(3)
        if inst.startswith('\\'):
            inst = inst[1:]
        start = m.end()
        depth = 1
        j = start
        while j < len(body) and depth > 0:
            c = body[j]
            if c == '(':
                depth += 1
            elif c == ')':
                depth -= 1
            j += 1
        seg = body[start:j-1]
        cs = {}
        for cm in conn.finditer(seg):
            pin = cm.group(1)
            net = cm.group(2).strip()
            if net.startswith('\\'):
                net = net[1:].strip()
            cs[pin] = net
        insts.append((ct, inst, cs))
    return ports, wires, insts

if __name__ == "__main__":
    ports, wires, insts = parse(sys.argv[1])
    print("ports", len(ports), "wires", len(wires), "insts", len(insts))
    from collections import defaultdict
    pins = defaultdict(set)
    for ct, inst, cs in insts:
        pins[ct] |= set(cs)
    out = {ct: sorted(p) for ct, p in sorted(pins.items())}
    print(json.dumps(out, indent=0)[:4000])
