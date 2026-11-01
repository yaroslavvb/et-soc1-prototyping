#!/usr/bin/env python3
"""Learn which RTL names are one net, once, on streams that separate nets: random data in every format, gated and ungated.

    train_maps.py --bin obj_vpu/Vtb --settle ./settle_count --kinds <tools/claims-v3/kinds> --out <dir>

Writes unit_float.map, unit_int8.map and vpu.map. A map belongs to the binary that made its VCDs: rebuild, retrain.
The rule is hier's (settle_count.cpp): names with one waveform are one net when one scope is an ancestor of the other. The recount applied
it to each run's own window, which is sound only when that window separates nets. It does not on a regular stream, and a designed
stream can collapse exactly the nets it exists to measure.

SPDX-License-Identifier: Apache-2.0
"""
import argparse
import os
import struct
import subprocess
import tempfile
from concurrent.futures import ThreadPoolExecutor

TRAIN = {"fp32": ["randn", "uniform01", "sparse50", "pow2", "smallint", "nn_like"],
         "fp16": ["randn", "uniform01", "sparse50", "wsparse50", "smallint", "nn_like"],
         "int8": ["full", "pos", "sparse50", "wsparse50", "ternary", "gauss_q"]}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--bin", required=True)
    ap.add_argument("--settle", required=True)
    ap.add_argument("--kinds", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--jobs", type=int, default=8)
    ap.add_argument("--tmp", default=None)
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)
    with tempfile.TemporaryDirectory(dir=a.tmp) as d:
        jobs = []
        for t, kinds in TRAIN.items():
            for k in kinds:
                jobs.append((t, k))

        def one(job):
            t, k = job
            raw = open(os.path.join(a.kinds, "tiles", t, k + ".bin"), "rb").read()
            words = struct.unpack("<512I", raw) + (0,) * 256
            h = os.path.join(d, f"{t}_{k}.hex")
            with open(h, "w") as f:
                f.write("\n".join(f"{w:08x}" for w in words) + "\n")
            v = os.path.join(d, f"{t}_{k}.vcd")
            # the launch's second op, from C = the first op: accumulators small and all formats' paths moving
            subprocess.run([a.bin, f"+tiles={h}", f"+fmt={t}", "+warm=1", "+first=1", "+ops=1", f"+dump={v}", "+dump_ops=1",
                            f"+verilator+coverage+file+{os.path.join(d, t + k + '.dat')}"], check=True, capture_output=True)
            return v

        with ThreadPoolExecutor(a.jobs) as ex:
            vcds = list(ex.map(one, jobs))
        fl = [v for v, (t, k) in zip(vcds, jobs) if t != "int8"]
        i8 = [v for v, (t, k) in zip(vcds, jobs) if t == "int8"]
        for name, inc, files in (("unit_float", ".txfma.", fl), ("unit_int8", ".lane_tima.tima.", i8), ("vpu", ".dut.", vcds)):
            r = subprocess.run([a.settle, "--train"] + files + ["--include", inc, "--skip", "1", "--write-map", os.path.join(a.out, name + ".map")],
                               capture_output=True, text=True, check=True)
            print(name, r.stderr.strip().splitlines()[-1])


if __name__ == "__main__":
    main()
