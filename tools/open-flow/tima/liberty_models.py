#!/usr/bin/env python3
"""Verilator-friendly models of liberty cells, written from the liberty files' own `function`, `ff` and `latch` groups.

    liberty_models.py --lib a.lib --lib b.lib ... --out cells.v [--only CELL,CELL]

Q133(a). Each combinational output is ONE continuous assignment of the liberty function, so a cell adds no wire of its
own to a waveform: a gate-level net count is then a count of the nets between cells, which is what the netlist names.
(ASAP7's own Verilog models build cells from primitives with internal wires, and their sequential cells from UDPs the
zero-delay simulator refuses; tools/open-flow/txfma/asap7_seq_behav.v replaced two of them by hand.) A flip-flop is
`always @(posedge clocked_on) IQ <= next_state`, a latch `always @* if (enable) IQ = data_in`, as the liberty groups say.
Cells whose outputs use `state_function` (the integrated clock gates, on the open flow's dont-use list) are skipped.
The file opens with Verilator's tracing_off and coverage_off, so a VCD of a design that uses these cells holds the
netlist's nets and not the cells' ports again.

Liberty function syntax: ! (not, prefix), ' (not, postfix), * & or a space (and), + | (or), ^ (xor), parentheses, 0, 1.

SPDX-License-Identifier: Apache-2.0
"""
import argparse
import os
import re


def groups(text):
    """Yield (kind, name, body) for every top-level `cell (...) { ... }` group, by brace matching."""
    for m in re.finditer(r'\bcell\s*\(\s*"?([A-Za-z0-9_]+)"?\s*\)\s*\{', text):
        i, depth = m.end(), 1
        while depth:
            c = text[i]
            if c == '{':
                depth += 1
            elif c == '}':
                depth -= 1
            i += 1
        yield m.group(1), text[m.end():i - 1]


def subgroups(body, kind):
    """(args, body) of every `kind (args) { ... }` group directly or deeply inside body."""
    out = []
    for m in re.finditer(r'\b' + kind + r'\s*\(([^)]*)\)\s*\{', body):
        i, depth = m.end(), 1
        while depth:
            c = body[i]
            if c == '{':
                depth += 1
            elif c == '}':
                depth -= 1
            i += 1
        out.append((m.group(1).replace('"', '').strip(), body[m.end():i - 1]))
    return out


def attr(body, name):
    m = re.search(r'\b' + name + r'\s*:\s*"?([^";]*)"?\s*;', body)
    return m.group(1).strip() if m else None


def strip_nested(body):
    """The body with every nested { ... } group removed, so attributes read are the pin's own."""
    out, depth = [], 0
    for c in body:
        if c == '{':
            depth += 1
        elif c == '}':
            depth -= 1
        elif depth == 0:
            out.append(c)
    return ''.join(out)


TOK = re.compile(r"\s*([A-Za-z_][A-Za-z0-9_]*|[01]|[!'*&+|^()])")


def to_verilog(expr):
    """Translate a liberty boolean function to a Verilog expression (implicit AND by adjacency included)."""
    toks, pos = [], 0
    expr = expr.strip()
    while pos < len(expr):
        m = TOK.match(expr, pos)
        if not m:
            if expr[pos].isspace():
                pos += 1
                continue
            raise ValueError(f"cannot parse {expr!r} at {pos}")
        toks.append(m.group(1))
        pos = m.end()
    out = []
    prev_operand = False
    for t in toks:
        is_open_operand = t == '(' or t == '!' or re.match(r'[A-Za-z_01]', t)
        if prev_operand and is_open_operand:
            out.append('&')                       # adjacency is AND
        if t == '!':
            out.append('~')
            prev_operand = False
        elif t == "'":
            # postfix not: wrap the previous operand (a name, a constant or a parenthesised group)
            if out and out[-1] == ')':
                depth, k = 0, len(out) - 1
                while True:
                    if out[k] == ')':
                        depth += 1
                    elif out[k] == '(':
                        depth -= 1
                        if depth == 0:
                            break
                    k -= 1
                out[k:] = ['~('] + out[k:] + [')']
            else:
                out[-1] = '(~' + out[-1] + ')'
            prev_operand = True
        elif t in ('*', '&'):
            out.append('&')
            prev_operand = False
        elif t in ('+', '|'):
            out.append('|')
            prev_operand = False
        elif t == '^':
            out.append('^')
            prev_operand = False
        elif t == '(':
            out.append('(')
            prev_operand = False
        elif t == ')':
            out.append(')')
            prev_operand = True
        elif t in ('0', '1'):
            out.append("1'b" + t)
            prev_operand = True
        else:
            out.append(t)
            prev_operand = True
    return ' '.join(out)


def model(name, body):
    pins = []
    for pname, pbody in subgroups(body, 'pin'):
        own = strip_nested(pbody)
        pins.append((pname, attr(own, 'direction'), attr(own, 'function'), attr(own, 'state_function')))
    if any(sf for _, _, _, sf in pins):
        return None, 'state_function'
    ins = [p for p, d, _, _ in pins if d == 'input']
    outs = [(p, f) for p, d, f, _ in pins if d == 'output']
    if not outs:
        return None, 'no output'
    lines = [f"module {name} ({', '.join(ins + [p for p, _ in outs])});"]
    if ins:
        lines.append(f"  input {', '.join(ins)};")
    lines.append(f"  output {', '.join(p for p, _ in outs)};")
    ffs, lats = subgroups(body, 'ff'), subgroups(body, 'latch')
    for args, g in ffs:
        q, qn = [x.strip() for x in args.split(',')]
        clk, nxt = attr(g, 'clocked_on'), attr(g, 'next_state')
        clr, pre = attr(g, 'clear'), attr(g, 'preset')
        lines.append(f"  reg {q};")
        lines.append(f"  wire {qn} = ~{q};")
        clk_v = to_verilog(clk)
        if re.fullmatch(r'[A-Za-z_][A-Za-z0-9_]*', clk_v.strip()):
            edge = f"posedge {clk_v.strip()}"
        elif re.fullmatch(r'~ *[A-Za-z_][A-Za-z0-9_]*', clk_v.strip()):
            edge = f"negedge {clk_v.strip().lstrip('~').strip()}"
        else:
            return None, f'clock {clk!r}'
        if clr or pre:
            # asynchronous clear / preset, active as the liberty expression says
            lines.append("  always @* begin")
            if clr:
                lines.append(f"    if ({to_verilog(clr)}) {q} = 1'b0;")
            if pre:
                lines.append(f"    if ({to_verilog(pre)}) {q} = 1'b1;")
            lines.append("  end")
        lines.append(f"  always @({edge}) {q} <= {to_verilog(nxt)};")
    for args, g in lats:
        q, qn = [x.strip() for x in args.split(',')]
        en, din = attr(g, 'enable'), attr(g, 'data_in')
        lines.append(f"  reg {q};")
        lines.append(f"  wire {qn} = ~{q};")
        lines.append(f"  always @* if ({to_verilog(en)}) {q} = {to_verilog(din)};")
    for p, f in outs:
        if f is None:
            return None, f'output {p} has no function'
        lines.append(f"  assign {p} = {to_verilog(f)};")
    lines.append("endmodule")
    return '\n'.join(lines), None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--lib', action='append', required=True)
    ap.add_argument('--out', required=True)
    ap.add_argument('--only', default='')
    a = ap.parse_args()
    only = set(x for x in a.only.split(',') if x)
    mods, skipped = [], []
    for lib in a.lib:
        text = open(lib).read()
        for name, body in groups(text):
            if only and name not in only:
                continue
            v, why = model(name, body)
            if v:
                mods.append(v)
            else:
                skipped.append(f"{name}: {why}")
    with open(a.out, 'w') as f:
        f.write("// Written by tools/open-flow/tima/liberty_models.py from the liberty files' own functions. Do not edit.\n")
        f.write("// " + ", ".join(os.path.basename(x) for x in a.lib) + "\n")
        f.write("/*verilator tracing_off*/\n/*verilator coverage_off*/\n`timescale 1ns/1ps\n\n")
        f.write('\n\n'.join(mods) + '\n')
    print(f"{len(mods)} cells written to {a.out}; {len(skipped)} skipped")
    for s in skipped:
        print("  skipped", s)


if __name__ == '__main__':
    main()
