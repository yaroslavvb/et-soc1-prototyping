#!/usr/bin/env python3
"""Reduce the published DCGM traces of Gregersen/Patel/Choukse (SC24) to mean board watts.

Usage: python3 -I reduce_idp.py <repo_root> [gpu_dir ...]

The traces are DCGM `dmon`-style TSV: a '#Entity' header line, a units line, then one
row per 100 ms sample.  Column POWER is board watts.  The paper trims the first 500 ms
for warmup, so we drop the first 5 rows.
"""
import os
import sys
import statistics


def read_power(path, trim=5):
    vals = []
    try:
        with open(path, "r", errors="replace") as fh:
            lines = fh.read().splitlines()
    except OSError:
        return []
    if not lines:
        return []
    hdr = lines[0].split()
    try:
        col = hdr.index("POWER")
    except ValueError:
        return []
    # header line starts with '#Entity', so the data columns are offset by one token
    # ('#Entity' occupies index 0 and 'GPU 0' occupies two tokens on data rows).
    for ln in lines[2:]:
        f = ln.split()
        if len(f) < col + 2 or f[0] != "GPU":
            continue
        # data row: 'GPU' '0' then the values matching hdr[1:]
        idx = col - 1 + 2
        if idx >= len(f):
            continue
        try:
            vals.append(float(f[idx]))
        except ValueError:
            continue
    return vals[trim:] if len(vals) > trim else vals


def agg(paths):
    pooled = []
    for p in paths:
        pooled.extend(read_power(p))
    if not pooled:
        return None
    return (statistics.mean(pooled), len(pooled))


def files(root, *parts):
    d = os.path.join(root, *parts)
    if not os.path.isdir(d):
        return []
    return [os.path.join(d, f) for f in sorted(os.listdir(d)) if f.endswith(".tsv")]


def pick(root, sub, suffix):
    """All seeds of one parameter value: files named '<seed>_<suffix>.tsv'."""
    out = []
    for p in files(root, sub):
        b = os.path.basename(p)[:-4]
        if "_" in b and b.split("_", 1)[1] == suffix:
            out.append(p)
    return out


def main():
    repo = sys.argv[1]
    gpus = sys.argv[2:] or ["a100_expt_results"]
    for g in gpus:
        root = os.path.join(repo, g)
        if not os.path.isdir(root):
            continue
        print("=" * 78)
        print("GPU dir:", g)
        for f in ("idle", "zeros", "ones"):
            r = agg([os.path.join(root, "other_expt", f + ".tsv")])
            if r:
                print("  other_expt %-7s mean %7.2f W  (n=%d samples)" % (f, r[0], r[1]))
        for dt in ("fp32", "fp16", "fp16-t", "int8"):
            if not os.path.isdir(os.path.join(root, dt)):
                continue
            print("  --- %s ---" % dt)
            nbits = "8" if dt == "int8" else "16"
            maxmean = "64" if dt == "int8" else "16384"
            minmean = "1"
            cases = [
                ("baseline gaussian(0, 2^10)", files(root, dt, "baseline")),
                ("1-gaussian-stddev  min", pick(root, dt + "/1-gaussian-stddev",
                                                "0.0312" if dt != "int8" else "1.0")),
                ("1-gaussian-stddev  max", pick(root, dt + "/1-gaussian-stddev",
                                                "1024.0" if dt != "int8" else "64.0")),
                ("2-gaussian-mean    2^0", pick(root, dt + "/2-gaussian-mean", minmean)),
                ("2-gaussian-mean    max", pick(root, dt + "/2-gaussian-mean", maxmean)),
                ("3-unique  n=1 value", pick(root, dt + "/3-gaussian-unique", "1")),
                ("3-unique  n=512", pick(root, dt + "/3-gaussian-unique", "512")),
                ("4-bits  0 flipped", pick(root, dt + "/4-bits", "0")),
                ("4-bits  all flipped", pick(root, dt + "/4-bits", nbits)),
                ("5-bits-least  0", pick(root, dt + "/5-bits-least", "0")),
                ("5-bits-least  all", pick(root, dt + "/5-bits-least", nbits)),
                ("6-bits-most   0", pick(root, dt + "/6-bits-most", "0")),
                ("6-bits-most   all", pick(root, dt + "/6-bits-most", nbits)),
                ("8-sort-rows   0%", pick(root, dt + "/8-sort-rows", "0.0")),
                ("8-sort-rows   100%", pick(root, dt + "/8-sort-rows", "1.0")),
                ("9-sort-columns 0%", pick(root, dt + "/9-sort-columns", "0.0")),
                ("9-sort-columns 100%", pick(root, dt + "/9-sort-columns", "1.0")),
                ("10-sort-intra 0%", pick(root, dt + "/10-sort-intra", "0.0")),
                ("10-sort-intra 100%", pick(root, dt + "/10-sort-intra", "1.0")),
                ("11-sparsity   0%", pick(root, dt + "/11-sparsity", "0.0")),
                ("11-sparsity   50%", pick(root, dt + "/11-sparsity", "0.5")),
                ("11-sparsity   100%", pick(root, dt + "/11-sparsity", "1.0")),
                ("13-sort-no-transpose 100%", pick(root, dt + "/13-sort-no-transpose", "1.0")),
                ("14-bits-least-zeros 0", pick(root, dt + "/14-bits-least-zeros", "0")),
                ("14-bits-least-zeros all", pick(root, dt + "/14-bits-least-zeros", nbits)),
                ("15-bits-most-zeros 0", pick(root, dt + "/15-bits-most-zeros", "0")),
                ("15-bits-most-zeros all", pick(root, dt + "/15-bits-most-zeros", nbits)),
            ]
            for label, ps in cases:
                r = agg(ps)
                if r:
                    print("    %-27s mean %7.2f W  (%2d files, n=%d)"
                          % (label, r[0], len(ps), r[1]))
                else:
                    print("    %-27s --" % label)


if __name__ == "__main__":
    main()
