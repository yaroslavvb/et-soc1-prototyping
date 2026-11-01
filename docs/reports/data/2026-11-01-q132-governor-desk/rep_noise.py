#!/usr/bin/env python3
"""Q132(g): replicate noise of (die - k W) per kind within a session, and the sustained runs' shape by kind class. Desk only.

    rep_noise.py <repo> > rep-noise.txt
"""
import json
import math
import os
import statistics as st
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import die_lines as DL

K = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "die-lines.json")))["pooled_k_c_per_w"]


def main():
    data = os.path.join(sys.argv[1], "docs/reports/data")
    allrep = []
    print(f"(die - {K} W) for every kind with replicate runs in one session")
    table = {}
    for exp, box, card, res, dirs in DL.SESSIONS:
        R = json.load(open(os.path.join(data, res)))
        d = {}
        for r in R["runs"]:
            if not str(r.get("block", "")).startswith("SUS") or r.get("sus_w_mean") is None:
                continue
            if exp == "E64" and r.get("minions") not in (1024, None):
                continue
            kind = f"{r.get('type')}/{(r.get('values') or '').split('/')[-1].replace('.bin', '')}"
            d.setdefault(kind, []).append(r)
        table[exp] = d
        for kind, v in sorted(d.items()):
            if len(v) >= 2:
                vals = [x["sus_die_mean"] - K * x["sus_w_mean"] for x in v]
                allrep.append(max(vals) - min(vals))
                print(f"  {exp} {kind:22s} " + " ".join(f"{x:.2f}" for x in vals) + "  W " + " ".join(f"{x['sus_w_mean']:.1f}" for x in v) + "  die " + " ".join(f"{x['sus_die_mean']:.1f}" for x in v) + "  MHz " + " ".join(f"{x['sus_mhz_mean']:.0f}" for x in v))
    print("replicate ranges: median", round(st.median(allrep), 2), "max", round(max(allrep), 2), "n", len(allrep))
    print("\nAnchors present in E64, E80, E83, E87 (sessions on aifoundry2), mean W, die, MHz, die - k W")
    for kind in ("fp32/zeros", "fp16/zeros", "int8/zeros", "fp32/sparse90", "fp16/sparse90", "int8/neg_ones", "fp16/neg_ones", "fp32/neg_ones", "int8/sparse50", "int8/smallint", "int8/gauss_q", "int8/full", "int8/randn", "fp16/ones", "fp32/ones", "fp32/randn", "fp16/randn"):
        row = []
        for exp in ("E64", "E80", "E83", "E87"):
            v = table.get(exp, {}).get(kind)
            if v:
                row.append(f"{exp} {st.mean(x['sus_w_mean'] for x in v):.1f} W {st.mean(x['sus_die_mean'] for x in v):.1f} C {st.mean(x['sus_mhz_mean'] for x in v):.0f} MHz {st.mean(x['sus_die_mean'] - K * x['sus_w_mean'] for x in v):.2f}")
        print(f"  {kind:16s} " + " | ".join(row))


if __name__ == "__main__":
    main()
