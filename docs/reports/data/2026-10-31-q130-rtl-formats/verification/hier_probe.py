#!/usr/bin/env python3
"""Measure the names-per-merged-net factor of the unit each format uses, with the toggle recount's own tools.

    hier_probe.py --trace-bin <obj_dir_trace/Vtrace> --tools rtl-sim/fma_toggle --settle <settle_count>
                  --rtl external/core-et/rtl --tile <kinds tile .bin> --type fp32|fp16|int8 --kind <name>
                  --workdir <scratch dir> --out <result.json> [--window 255]

This is the recipe behind hier-measured.json (README section 0). The verification of Sat 31 Oct 2026 ran it
from its own scratch copy; this copy only takes the paths as arguments. Build first, from
rtl-sim/fma_toggle_formats with dump-window.patch applied: `make obj_dir_trace/Vtrace settle_count` (with the
Makefile's VERILATOR / CXXOVERRIDE settings). Then, per kind:

  1. run the traced bench in run_kinds.py's protocol (+ops=4 +warm=1 +mul=1, +gap=34 or 62) with a VCD window
     of --window cycles from the first measured cycle;
  2. map VCD scopes to RTL modules with rtl-sim/fma_toggle/scope_modules.py (--top txfma_top --top-scope txfma,
     or --top tima_top --top-scope tima for int8) and count settled per-merged-net toggles with settle_count
     (--phase even --skip 1, plus --include .tima for int8), exactly as rtl-sim/fma_toggle/recount.py calls them;
  3. read Verilator's raw toggle coverage of the same window, unit blocks only (run_kinds.py's parse_cov rule),
     and report factor = raw coverage / settled merged-net toggles.
"""
import argparse
import collections
import json
import os
import re
import struct
import subprocess
import sys


def main():
    ap = argparse.ArgumentParser()
    for k in ("--trace-bin", "--tools", "--settle", "--rtl", "--tile", "--type", "--kind", "--workdir", "--out"):
        ap.add_argument(k, required=True)
    ap.add_argument("--window", type=int, default=255)
    a = ap.parse_args()
    typ = a.type
    d = os.path.join(a.workdir, f"hier_{typ}_{a.kind}")
    os.makedirs(d, exist_ok=True)
    hexf, vcd, cov = (os.path.join(d, n) for n in ("t.hex", "w.vcd", "cov.dat"))
    raw = open(a.tile, "rb").read()
    with open(hexf, "w") as f:
        for w in struct.unpack("<512I", raw):
            f.write(f"{w:08x}\n")
        for _ in range(256):
            f.write("00000000\n")
    gap = 62 if typ == "int8" else 34
    out = subprocess.run([a.trace_bin, f"+tiles={hexf}", "+ops=4", "+warm=1", "+mul=1", f"+gap={gap}",
                          f"+fmt={typ}", f"+dump={vcd}", f"+dump_uops={a.window}",
                          f"+verilator+coverage+file+{cov}"], capture_output=True, text=True, check=True).stdout
    acct = json.loads(next(l for l in out.splitlines() if l.startswith("ACCT"))[5:])
    tsv = os.path.join(d, "scopes.tsv")
    top = ["--top", "tima_top", "--top-scope", "tima"] if typ == "int8" else ["--top", "txfma_top", "--top-scope", "txfma"]
    subprocess.run([sys.executable, "-I", os.path.join(a.tools, "scope_modules.py"), vcd, "--rtl", a.rtl,
                    "--out", tsv] + top, check=True, capture_output=True, text=True)
    js = os.path.join(d, "settle.json")
    incl = ["--include", ".tima"] if typ == "int8" else []
    subprocess.run([a.settle, vcd, "--modmap", tsv, "--out", js, "--phase", "even", "--skip", "1"] + incl,
                   check=True, capture_output=True, text=True)
    sc = json.load(open(js))

    by_block = collections.Counter()
    for line in open(cov, errors="replace"):
        if not line.startswith("C '"):
            continue
        key, count = line.rsplit("' ", 1)
        fields = dict(kv.split("\x02", 1) for kv in key[3:].split("\x01") if "\x02" in kv)
        fname = os.path.basename(fields.get("f", "?"))
        if fname in ("tb.sv", "tb_fmt.sv", "ff_acct.sv") or re.search(r"clk|clock", fields.get("o", "")):
            continue
        by_block[fname.replace(".v", "")] += int(count)

    def in_unit(m):
        m = m or ""
        if typ == "int8":
            return m.startswith("tima")
        return (not m.startswith("tima")) and m not in ("tb", "ff", "en_ff", "rst_ff", "rst_en_ff", "") \
            and not m.startswith("$")

    res = {"type": typ, "kind": a.kind, "window_cycles": a.window, "acct": acct,
           "coverage_raw_unit": sum(v for k, v in by_block.items() if in_unit(k)),
           "coverage_raw_by_block": {k: v for k, v in by_block.items() if in_unit(k)}}
    tot = collections.Counter()
    for m, row in sc["by_module"].items():
        if in_unit(m):
            for fld, val in row.items():
                if isinstance(val, (int, float)):
                    tot[fld] += val
    res["unit_totals"] = dict(tot)
    if tot.get("hier_settled"):
        res["factor_coverage_raw_over_hier"] = res["coverage_raw_unit"] / tot["hier_settled"]
        res["factor_name_settled_over_hier"] = tot["name_settled"] / tot["hier_settled"]
    json.dump(res, open(a.out, "w"), indent=1)
    print(json.dumps({k: v for k, v in res.items() if k != "coverage_raw_by_block"}, indent=1))


if __name__ == "__main__":
    main()
