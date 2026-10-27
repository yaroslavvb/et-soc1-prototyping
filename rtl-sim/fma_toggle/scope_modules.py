#!/usr/bin/env python3
"""Maps every VCD scope of the FMA trace to the RTL module it is an instance of.

    scope_modules.py <file.vcd> --rtl <core-et>/rtl --out scopes.tsv

A VCD names instances, not modules, so a toggle count split by scope cannot be compared with the
coverage counter's split by RTL file until each scope is resolved. This reads the module and
instantiation statements out of the Verilog itself and walks the VCD's scope tree from the top:
each scope component is either an instance the parent module declares (so its module is known) or a
generate block, which keeps the parent's module. Writes "<scope path>\t<module>" per line.

The instantiation scan only accepts a type that is itself a module declared under --rtl (or one of
ff_acct.sv's register models), so `always`, `assign`, task calls and macros cannot be mistaken for one.

SPDX-License-Identifier: Apache-2.0
"""
import argparse
import os
import re
import sys

MOD_RE = re.compile(r"^\s*module\s+([A-Za-z_]\w*)", re.M)
# <type> [#(params) | #param] <instance> ( ... — the parts may sit on separate lines.
INST_RE = re.compile(
    r"(?<![.\w])([A-Za-z_]\w*)\s*"
    r"(?:#\s*(?:\((?:[^()]|\([^()]*\))*\)|[0-9]+|[A-Za-z_]\w*)\s*)?"
    r"([A-Za-z_]\w*)\s*\(",
    re.S)
NOT_A_TYPE = {"if", "for", "while", "case", "casex", "casez", "always", "always_comb", "always_ff",
              "always_latch", "initial", "assign", "function", "task", "module", "endmodule", "begin",
              "end", "generate", "endgenerate", "return", "repeat", "forever", "wait", "do"}


def strip_comments(text):
    text = re.sub(r"/\*.*?\*/", "", text, flags=re.S)
    return re.sub(r"//[^\n]*", "", text)


def scan(rtl_dirs, extra_files):
    """-> {module: {instance_name: module_type}}, over every .v/.sv under rtl_dirs."""
    bodies = {}
    files = list(extra_files)
    for d in rtl_dirs:
        for root, _, names in os.walk(d):
            files += [os.path.join(root, n) for n in names if n.endswith((".v", ".sv"))]
    for path in files:
        try:
            text = strip_comments(open(path, errors="replace").read())
        except OSError:
            continue
        # split on module boundaries
        parts = re.split(r"^\s*module\s+", text, flags=re.M)[1:]
        for part in parts:
            m = re.match(r"([A-Za-z_]\w*)", part)
            if not m:
                continue
            body = re.split(r"^\s*endmodule", part, flags=re.M)[0]
            bodies.setdefault(m.group(1), body)
    known = set(bodies)
    insts = {}
    for mod, body in bodies.items():
        table = {}
        for typ, inst in INST_RE.findall(body):
            if typ in NOT_A_TYPE or typ not in known or inst in NOT_A_TYPE:
                continue
            table[inst] = typ
        insts[mod] = table
    return insts


def vcd_scopes(path):
    """-> list of scope paths, in declaration order."""
    out, stack = [], []
    with open(path, errors="replace") as fh:
        for raw in fh:
            line = raw.lstrip()          # Verilator indents the header by scope depth
            if line.startswith("$scope"):
                f = line.split()
                if len(f) >= 3:
                    stack.append(f[2])
                    out.append(".".join(stack))
            elif line.startswith("$upscope"):
                if stack:
                    stack.pop()
            elif line.startswith("$enddefinitions"):
                break
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("vcd")
    ap.add_argument("--rtl", required=True, help="core-et's rtl/ directory")
    ap.add_argument("--extra", nargs="*", default=[], help="extra Verilog files (ff_acct.sv, tb.sv)")
    ap.add_argument("--top", default="txfma_top", help="module of the outermost traced scope")
    ap.add_argument("--top-scope", default="txfma", help="instance name of the outermost traced scope")
    ap.add_argument("--out", required=True)
    a = ap.parse_args()

    insts = scan([a.rtl], a.extra)
    if a.top not in insts:
        sys.exit(f"module {a.top} not found under {a.rtl}")

    rows, unresolved = [], 0
    mod_of = {}
    for scope in vcd_scopes(a.vcd):
        parts = scope.split(".")
        # everything above the traced top (tb, lane[0], ...) carries no module of interest
        if a.top_scope not in parts:
            mod_of[scope] = "(tb)"
            rows.append((scope, "(tb)"))
            continue
        i = parts.index(a.top_scope)
        mod = a.top
        for p in parts[i + 1:]:
            base = re.sub(r"\[\d+\]$", "", p)
            nxt = insts.get(mod, {}).get(base)
            if nxt is None:
                nxt = insts.get(mod, {}).get(p)
            if nxt is not None:
                mod = nxt
            # else: a generate block or an unnamed scope, module unchanged
        mod_of[scope] = mod
        rows.append((scope, mod))
        if mod == a.top and len(parts) > i + 1:
            unresolved += 1

    with open(a.out, "w") as fh:
        for scope, mod in rows:
            fh.write(f"{scope}\t{mod}\n")
    seen = {}
    for _, m in rows:
        seen[m] = seen.get(m, 0) + 1
    print(f"{len(rows)} scopes, {len(seen)} modules", file=sys.stderr)
    for m, n in sorted(seen.items(), key=lambda kv: -kv[1])[:12]:
        print(f"  {m:34s} {n:7d}", file=sys.stderr)


if __name__ == "__main__":
    main()
