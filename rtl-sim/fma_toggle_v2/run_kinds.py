#!/usr/bin/env python3
"""Every kind of number through the real vector unit: toggles, clocked register bits, by stage, each behind a functional check.

    run_kinds.py --bin obj_vpu/Vtb --accum ./accum --settle ./settle_count --kinds <tools/claims-v3/kinds> --out counts-v2.json
                 [--types fp32,fp16,int8] [--only a,b] [--points launch|recount|n,n,..] [--jobs 8] [--ops 2]

For every kind, at each point of a launch (accumulators computed in software by accum.c and written into the register files by
back door), one warm op, then:

  coverage run  `--ops` measured ops: Verilator's toggle coverage by RTL file (`nets`, the old unit), the register counters.
                Afterwards C is compared with software at every word (C is the software state of n0 + warm + ops ops):
                `check_mismatch` must be 0, and for fp16 it counts the window model's named residue.
  VCD run       one whole op, counted by settle_count: names, settled, ids, `nets_hier` per NET (the recount's method, its merge
                learned on this run alone), and `nets_map` (the same merge, learned once on random data by train_maps.py and applied
                to every run), over the unit alone (.txfma. or .lane_tima.tima.) and over the whole VPU (.dut.), by stage.

Numbers are per TensorFMA op on one minion. The launch points are the midpoints of three equal thirds of a 0.5 s launch at
600 MHz (the host's repeatFor: workloads/sparsity/host/main.cpp:567): C is what it is at that time of a launch, and a time average
over the launch is the average over the three.

SPDX-License-Identifier: Apache-2.0
"""
import argparse
import collections
import json
import os
import re
import struct
import subprocess
import tempfile
from concurrent.futures import ThreadPoolExecutor

CPO = {"fp32": 546, "fp16": 546, "int8": 318}
MACS = {"fp32": 4096, "fp16": 8192, "int8": 16384}


def launch_points(typ):
    ops = 0.5 * 600e6 / CPO[typ]
    return [int(ops * f) for f in (1 / 6, 1 / 2, 5 / 6)]


def parse_cov(path):
    by_block, clock = collections.Counter(), 0
    for line in open(path, errors="replace"):
        if not line.startswith("C '"):
            continue
        key, count = line.rsplit("' ", 1)
        fields = dict(kv.split("\x02", 1) for kv in key[3:].split("\x01") if "\x02" in kv)
        f = os.path.basename(fields.get("f", "?"))
        name = fields.get("o", "")
        if f in ("tb_vpu.sv", "ff_acct.sv"):
            continue
        n = int(count)
        if re.search(r"clk|clock", name):
            clock += n
            continue
        by_block[f.replace(".v", "")] += n
    return by_block, clock


def settle(a, vcd, include, d, tag, mapf):
    js = os.path.join(d, f"s_{tag}.json")
    subprocess.run([a.settle, vcd, "--out", js, "--include", include, "--skip", "1", "--map", mapf], check=True, capture_output=True)
    s = json.load(open(js))
    t = s["total"]
    return {"sample_cycles": s["sample_cycles"], "name_settled": t["name_settled"], "name_raw": t["name_raw"], "ids": t["id_settled"],
            "nets_hier": t["hier_settled"], "n_hier": t["n_hier"], "nets_hier2": s["hier2_settled"], "n_hier2": s["n_hier2"],
            "nets_map": s["map_settled"], "n_map": s["n_map"], "nets_distinct": t["distinct_settled"], "xz": s["xz_values"],
            "by_stage": s["by_stage_map"], "by_stage_n": s["by_stage_n_map"], "by_stage_hier2": s["by_stage_hier"], "by_stage_hier1": s["by_stage_hier1"]}


def point(a, typ, kind, path, n0, warm, ops):
    """One accumulator point of one kind."""
    with tempfile.TemporaryDirectory(dir=a.tmp) as d:
        pts = [n0, n0 + warm + ops] if n0 else [warm + ops]
        subprocess.run([os.path.abspath(a.accum), typ, os.path.abspath(path)] + [str(p) for p in pts], check=True, cwd=d)
        c0 = open(os.path.join(d, f"accum_{n0}.bin"), "rb").read() if n0 else b"\0" * 1024
        c1 = struct.unpack("<256I", open(os.path.join(d, f"accum_{n0 + warm + ops}.bin"), "rb").read())
        raw = open(path, "rb").read()
        words = struct.unpack("<512I", raw) + struct.unpack("<256I", c0)
        hexf = os.path.join(d, "t.hex")
        with open(hexf, "w") as f:
            f.write("\n".join(f"{w:08x}" for w in words) + "\n")
        base = [a.bin, f"+tiles={hexf}", f"+fmt={typ}", f"+warm={warm}", f"+first={0 if n0 else 1}", f"+loadc={1 if n0 else 0}"]
        cov = os.path.join(d, "cov.dat")
        out = subprocess.run(base + [f"+ops={ops}", "+printc=1", f"+verilator+coverage+file+{cov}"], capture_output=True, text=True,
                             check=True).stdout
        acct, unit = None, None
        final = {}
        last = warm + ops
        for l in out.splitlines():
            if l.startswith("ACCT "):
                acct = json.loads(l[5:])
            elif l.startswith("ACCTU "):
                unit = [int(x) for x in l.split()[1:]]
            elif l.startswith("C "):
                _, op, i, j, v = l.split()
                if int(op) == last:
                    final[(int(i), int(j))] = int(v, 16)
        miss = sum(1 for i in range(16) for j in range(16) if final.get((i, j)) != c1[16 * i + j])
        by_block, clock = parse_cov(cov)
        n = acct["ops"]
        res = {"n0": n0, "check_words": 256, "check_mismatch": miss,
               "cycles": acct["cycles"] / n, "busy": acct["busy"] / n, "uops": acct["uops"] / n,
               "valid_slots": (acct["tima_valid"] if typ == "int8" else acct["txfma_valid"]) / n, "scp_reads": acct["scp_reads"] / n,
               "ff": {"all": {"clocked": acct["ff_clocked_bits"] / n, "toggles": acct["ff_toggles"] / n, "present": acct["ff_present_bits"] / n},
                      "txfma": {"clocked": unit[0] / n, "toggles": unit[1] / n, "present": unit[2] / n},
                      "tima": {"clocked": unit[3] / n, "toggles": unit[4] / n, "present": unit[5] / n},
                      "rest": {"clocked": unit[6] / n, "toggles": unit[7] / n, "present": unit[8] / n}},
               "nets_cov": sum(by_block.values()) / n, "clock_nets_cov": clock / n,
               "by_block_cov": {k: v / n for k, v in sorted(by_block.items(), key=lambda kv: -kv[1]) if v}}
        vcd = os.path.join(d, "t.vcd")
        subprocess.run(base + ["+ops=1", f"+dump={vcd}", "+dump_ops=1", f"+verilator+coverage+file+{cov}"], capture_output=True, text=True,
                       check=True)
        unit_inc = ".lane_tima.tima." if typ == "int8" else ".txfma."
        res["unit"] = settle(a, vcd, unit_inc, d, "unit", os.path.join(a.maps, "unit_int8.map" if typ == "int8" else "unit_float.map"))
        res["vpu"] = settle(a, vcd, ".dut.", d, "vpu", os.path.join(a.maps, "vpu.map"))
        os.remove(vcd)
    return res


def job(args):
    typ, kind, path, a, n0 = args
    try:
        return typ, kind, n0, point(a, typ, kind, path, n0, 1, a.ops)
    except Exception as e:
        if not a.keep_going:
            raise
        print(f"FAILED {typ}.{kind} n0={n0}: {e}", flush=True)
        return typ, kind, n0, None


def mean_rows(rows):
    def avg(obj_list):
        if isinstance(obj_list[0], dict):
            return {k: avg([o.get(k, 0) for o in obj_list]) for k in obj_list[0]}
        return sum(obj_list) / len(obj_list)
    keys = [k for k in rows[0] if k != "n0"]
    return {k: avg([r[k] for r in rows]) for k in keys}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--bin", required=True)
    ap.add_argument("--accum", required=True)
    ap.add_argument("--settle", required=True)
    ap.add_argument("--maps", required=True, help="directory of train_maps.py's unit_float.map, unit_int8.map, vpu.map")
    ap.add_argument("--kinds", required=True, help="tools/claims-v3/kinds")
    ap.add_argument("--extra-tiles", default="", help="type:name:path,... tiles outside kinds.json")
    ap.add_argument("--out", required=True)
    ap.add_argument("--types", default="fp32,fp16,int8")
    ap.add_argument("--only", default="")
    ap.add_argument("--points", default="launch")
    ap.add_argument("--ops", type=int, default=2)
    ap.add_argument("--jobs", type=int, default=8)
    ap.add_argument("--tmp", default=None)
    ap.add_argument("--keep-going", action="store_true", help="drop a tile whose run fails, and say so, instead of stopping")
    a = ap.parse_args()
    only = set(x for x in a.only.split(",") if x)
    work = []
    tiles = []
    for typ in a.types.split(","):
        d = os.path.join(a.kinds, "tiles", typ)
        for f in sorted(os.listdir(d)):
            if f.endswith(".bin") and (not only or f[:-4] in only):
                tiles.append((typ, f[:-4], os.path.join(d, f)))
    for x in a.extra_tiles.split(","):
        if x:
            t, n, p = x.split(":", 2)
            tiles.append((t, n, p))
    for typ, name, path in tiles:
        pts = launch_points(typ) if a.points == "launch" else [int(x) for x in a.points.split(",")]
        for n0 in pts:
            work.append((typ, name, path, a, n0))
    with ThreadPoolExecutor(a.jobs) as ex:
        done = list(ex.map(job, work))
    res = {"_bench": "rtl-sim/fma_toggle_v2 (vpu_top, -fno-dfg)", "_units": "per TensorFMA op on one minion", "_points": a.points, "rows": {}}
    for typ, name, path in tiles:
        rows = [r for t, k, _, r in done if t == typ and k == name]
        if any(r is None for r in rows):
            continue
        rows.sort(key=lambda r: r["n0"])
        res["rows"][f"{typ}.{name}"] = {"type": typ, "kind": name, "macs_per_op": MACS.get(typ), "points": rows, "mean": mean_rows(rows)}
        m = res["rows"][f"{typ}.{name}"]["mean"]
        print(f"{typ:5s} {name:18s} check_miss {m['check_mismatch']:6.1f} valid {m['valid_slots']:7.0f} cyc {m['cycles']:6.1f} "
              f"unit_hier {m['unit']['nets_hier']:10.0f} /MAC {m['unit']['nets_hier'] / MACS[typ]:8.1f} map {m['unit']['nets_map']:10.0f} vpu_hier {m['vpu']['nets_hier']:10.0f} vpu_map {m['vpu']['nets_map']:10.0f} "
              f"ff_clk_txfma {m['ff']['txfma']['clocked']:9.0f} ff_tog_txfma {m['ff']['txfma']['toggles']:9.0f} xz {m['unit']['xz']:.0f}", flush=True)
    json.dump(res, open(a.out, "w"), indent=1)


if __name__ == "__main__":
    main()
