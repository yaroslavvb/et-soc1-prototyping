#!/usr/bin/env python3
"""Alias classes of physical nets in a HIERARCHICAL Yosys gate netlist.

A physical wire that crosses a module boundary has one name per level of hierarchy. The extractor
(OpenSTA) keeps ONE of those names; a hierarchical simulation writes the others. Walking the
instance tree and unioning every (formal port, actual net) pair gives, for each physical net, the
set of names it can be found under -- which is what lets a per-net activity file be joined to a
per-net capacitance table without silently dropping half the design.
"""
import re, sys
from collections import defaultdict

MOD = re.compile(r'^module\s+(\\?\S+?)\s*\(', re.M)

def split_top(s):
    """Split a comma list at top level (ignore commas inside {} and [])."""
    out, depth, cur = [], 0, []
    for ch in s:
        if ch in '{[(':
            depth += 1
        elif ch in '}])':
            depth -= 1
        if ch == ',' and depth == 0:
            out.append(''.join(cur)); cur = []
        else:
            cur.append(ch)
    if cur:
        out.append(''.join(cur))
    return [x.strip() for x in out if x.strip()]

def unescape(n):
    n = n.strip()
    return n[1:].strip() if n.startswith('\\') else n

def parse_modules(path):
    txt = open(path, errors='replace').read()
    starts = [(m.start(), unescape(m.group(1))) for m in MOD.finditer(txt)]
    mods = {}
    for i, (pos, name) in enumerate(starts):
        end = txt.find('\nendmodule', pos)
        body = txt[pos:end if end > 0 else len(txt)]
        mods[name] = body
    return mods

INST = re.compile(
    r'(^|\n)\s*(\\?[A-Za-z_][^\s(;]*)\s+(\\\S+\s|[A-Za-z_][A-Za-z0-9_$\[\]\.]*)\s*\(', re.M)
CONN = re.compile(r'\.(\\?[A-Za-z0-9_\[\]]+)\s*\(\s*([^)]*?)\s*\)')

def instances(body):
    """[(module_or_cell, instname, {formal: actual_expr})] in one module body."""
    out = []
    for m in INST.finditer(body):
        mt, inst = unescape(m.group(2)), unescape(m.group(3))
        if mt in ('module', 'input', 'output', 'inout', 'wire', 'reg', 'assign', 'endmodule',
                  'parameter', 'localparam', 'always', 'initial', 'function', 'task'):
            continue
        start = m.end(); depth = 1; j = start
        while j < len(body) and depth > 0:
            c = body[j]
            if c == '(':
                depth += 1
            elif c == ')':
                depth -= 1
            j += 1
        seg = body[start:j-1]
        cs = {}
        for cm in CONN.finditer(seg):
            cs[unescape(cm.group(1))] = cm.group(2).strip()
        out.append((mt, inst, cs))
    return out

BITS = re.compile(r'^(\\?[^\s\[]+)\s*(?:\[(\d+)(?::(\d+))?\])?$')

def expand(expr, width_of=None):
    """A connection expression -> list of scalar net names, LSB first, or [] if not a plain net."""
    e = expr.strip()
    if e.startswith('{') or "'" in e or e in ('', "1'b0", "1'b1"):
        return []
    m = BITS.match(e)
    if not m:
        return []
    base = unescape(m.group(1))
    if m.group(2) is None:
        return [base]
    hi = int(m.group(2))
    lo = int(m.group(3)) if m.group(3) is not None else hi
    if m.group(3) is None:
        return [f"{base}[{hi}]"]
    step = -1 if hi >= lo else 1
    return [f"{base}[{i}]" for i in range(lo, hi + 1)]

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

def alias_classes(path, top, max_depth=40):
    """Walk the instance tree from `top`; union each child-port name onto the parent net name."""
    mods = parse_modules(path)
    insts_of = {k: instances(v) for k, v in mods.items()}
    # port order / widths per module, from its declarations
    decls = {}
    for k, body in mods.items():
        d = {}
        for m in re.finditer(r'^\s*(input|output|inout)\s+(?:\[(\d+):(\d+)\]\s+)?(\\?[^\s;]+)\s*;',
                             body, re.M):
            hi, lo, nm = m.group(2), m.group(3), unescape(m.group(4))
            if hi is None:
                d[nm] = [nm]
            else:
                hi, lo = int(hi), int(lo)
                d[nm] = [f"{nm}[{i}]" for i in range(min(hi, lo), max(hi, lo) + 1)]
        decls[k] = d
    uf = UF()
    stack = [(top, "")]
    seen = 0
    while stack:
        mod, prefix = stack.pop()
        if mod not in insts_of:
            continue
        for mt, inst, cs in insts_of[mod]:
            if mt not in mods:          # a library cell
                continue
            child_pre = (prefix + "/" if prefix else "") + inst
            for formal, actual in cs.items():
                fbits = decls.get(mt, {}).get(formal)
                abits = expand(actual)
                if not fbits or not abits or len(fbits) != len(abits):
                    continue
                for fb, ab in zip(fbits, abits):
                    pn = ((prefix + "/") if prefix else "") + ab
                    cn = child_pre + "/" + fb
                    uf.union(pn, cn)
                    seen += 1
            stack.append((mt, child_pre))
    return uf, seen

if __name__ == "__main__":
    uf, seen = alias_classes(sys.argv[1], sys.argv[2])
    groups = defaultdict(list)
    for n in list(uf.p):
        groups[uf.find(n)].append(n)
    print("names", len(uf.p), "unions", seen, "classes", len(groups))
    big = sorted(groups.values(), key=len, reverse=True)[:3]
    for g in big:
        print(len(g), g[:6])


def flat_nets(path, top):
    """Every physical net of a hierarchical netlist, under its FLAT (top-relative) name.

    This is the set of nets that existed BEFORE place and route, so the extractor's net list
    minus this set is exactly what CTS and repair_design added.
    """
    mods = parse_modules(path)
    insts_of = {k: instances(v) for k, v in mods.items()}
    wires = {}
    for k, body in mods.items():
        ws = []
        for m in re.finditer(
                r'^\s*(?:input|output|inout|wire)\s+(?:\[(\d+):(\d+)\]\s+)?(\\?[^\s;]+)\s*;',
                body, re.M):
            hi, lo, nm = m.group(1), m.group(2), unescape(m.group(3))
            if hi is None:
                ws.append(nm)
            else:
                hi, lo = int(hi), int(lo)
                ws += [f"{nm}[{i}]" for i in range(min(hi, lo), max(hi, lo) + 1)]
        wires[k] = ws
    out = set()
    stack = [(top, "")]
    while stack:
        mod, prefix = stack.pop()
        p = (prefix + "/") if prefix else ""
        for w in wires.get(mod, ()):
            out.add(p + w)
        for mt, inst, cs in insts_of.get(mod, ()):
            if mt in mods:
                stack.append((mt, p + inst))
    return out


def bit_offsets(path, top):
    """{flat_bus_name: declared_lsb} for every vector in the hierarchy whose LSB is not 0.

    Verilator renumbers such a vector from 0 in its SAIF, so the extractor's `bus[32]` and the
    simulation's `bus[0]` are the SAME wire. Without this offset every bus the RTL declares as
    [63:32] (and there are many in this unit) silently fails to join.
    """
    mods = parse_modules(path)
    insts_of = {k: instances(v) for k, v in mods.items()}
    vec = {}
    for k, body in mods.items():
        d = {}
        for m in re.finditer(
                r'^\s*(?:input|output|inout|wire|reg)\s+\[(\d+):(\d+)\]\s+(\\?[^\s;]+)\s*;',
                body, re.M):
            hi, lo, nm = int(m.group(1)), int(m.group(2)), unescape(m.group(3))
            d[nm] = min(hi, lo)
        vec[k] = d
    out = {}
    stack = [(top, "")]
    while stack:
        mod, prefix = stack.pop()
        p = (prefix + "/") if prefix else ""
        for nm, lo in vec.get(mod, {}).items():
            if lo:
                out[p + nm] = lo
        for mt, inst, cs in insts_of.get(mod, ()):
            if mt in mods:
                stack.append((mt, p + inst))
    return out
