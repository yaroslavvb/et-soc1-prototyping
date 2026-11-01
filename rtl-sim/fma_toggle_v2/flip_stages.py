#!/usr/bin/env python3
"""How many named RTL signal bits one operand-bit flip changes as it passes through txfma_top: two traced runs, diffed.

    flip_stages.py --bin obj_flip/Vtb [--a 40490fdb --b0 3f9e0651 --b1 3f9e0e51 --c 42c80000] [--out flip.json]

A bit counts if its settled value differs between the two runs in any cycle. Clocks excluded. The chip diagram's fact tfma.flip.stages
("1,946 named RTL signal bits", the lab's E60 case) was counted this way on 23 Oct 2026. By stage scope, as that fact splits it.
SPDX-License-Identifier: Apache-2.0
"""
import argparse, collections, json, os, re, subprocess, tempfile


def read_vcd(path):
    names, val, samples = {}, {}, []
    st = []
    t0 = None
    with open(path, errors="replace") as f:
        for line in f:
            l = line.strip()
            if l.startswith("$scope"):
                st.append(l.split()[2])
            elif l.startswith("$upscope"):
                st.pop()
            elif l.startswith("$var"):
                p = l.split()
                w, i, nm = int(p[2]), p[3], p[4]
                names.setdefault(i, []).append((".".join(st), nm, w))
            elif l.startswith("$enddef"):
                break
        times = {}
        cur = {}
        t = None
        for line in f:
            l = line.strip()
            if not l:
                continue
            c = l[0]
            if c == "#":
                if t is not None:
                    times[t] = dict(cur)
                t = int(l[1:])
            elif c in "01xz":
                cur[l[1:]] = 1 if c == "1" else 0
            elif c == "b":
                v, i = l.split()
                cur[i] = int(v[1:].replace("x", "0").replace("z", "0"), 2)
        if t is not None:
            times[t] = dict(cur)
    return names, times


def stage(scope):
    for s, tag in ((".txfma0_f0", "f0"), (".txfma0_f1", "f1"), (".txfma0_f2", "f2"), (".txfma0_f3", "f3"), (".txfma0_f4", "f4"),
                   (".txfma0_f5", "f5"), (".txfma0_f6", "f6"), (".txfmaexp0_top", "exp"), (".txfmactl0_top", "ctl"), (".txfmafrac0_top", "frac_top")):
        if s in scope:
            return tag
    return "top"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--bin", required=True)
    ap.add_argument("--a", default="40490fdb")
    ap.add_argument("--b0", default="3f9e0651")
    ap.add_argument("--b1", default="3f9e0e51")
    ap.add_argument("--c", default="42c80000")
    ap.add_argument("--out", default="")
    a = ap.parse_args()
    res = {}
    with tempfile.TemporaryDirectory() as d:
        runs = []
        for tag, b in (("b0", a.b0), ("b1", a.b1)):
            vcd = os.path.join(d, tag + ".vcd")
            o = subprocess.run([a.bin, f"+a={a.a}", f"+b={b}", f"+c={a.c}", f"+dump={vcd}"], capture_output=True, text=True, check=True).stdout
            res[tag + "_out"] = [l.split()[1] for l in o.splitlines() if l.startswith("OUT")][:1]
            runs.append(read_vcd(vcd))
    (n0, t0), (n1, t1) = runs
    # ids can differ between the two runs only if the builds differ; same binary, so same ids
    per_name = collections.Counter()
    per_id = 0
    bits_tot = collections.Counter()
    wall = collections.Counter()
    tree = 0
    booth = 0
    allts = sorted(set(t0) & set(t1))
    tt = allts[0] if allts else 0
    even = [x for x in allts if ((x - allts[0]) // max(1, allts[1] - allts[0])) % 2 == 0]
    diffmask = {}
    for x in even:
        c0, c1 = t0[x], t1[x]
        for i in c0:
            v0, v1 = c0.get(i, 0), c1.get(i, 0)
            if v0 != v1:
                diffmask[i] = diffmask.get(i, 0) | (v0 ^ v1)
    total = 0
    names_hit = 0
    for i, m in diffmask.items():
        n = bin(m).count("1")
        for scope, nm, w in n0.get(i, []):
            if re.search(r"clk|clock", nm, re.I):
                continue
            if ".dut" not in scope:
                continue
            total += n
            st = stage(scope)
            per_name[st] += n
            if ".wallace" in scope or "compressor" in scope or "txfma_csa" in scope:
                tree += n
            if "booth" in scope:
                booth += n
    res.update({"named_signal_bits": total, "by_stage": dict(per_name), "tree": tree, "booth": booth, "operands": vars(a).get("a")})
    print(json.dumps(res, indent=1))
    if a.out:
        json.dump(res, open(a.out, "w"), indent=1)


if __name__ == "__main__":
    main()
