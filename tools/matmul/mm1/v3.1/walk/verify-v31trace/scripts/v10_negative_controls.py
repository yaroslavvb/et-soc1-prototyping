#!/usr/bin/env python3
"""verify-v31trace (Q217) v10: negative controls for this lane's own independent check (v04_independent.py), so its 'equal' is not vacuous:
(1) t3's rgm211 gemmLn trace against my model with the WRONG walk (mn), and t1's rgm136 gemmL trace against the nm walk: must differ;
(2) t5's gemmLnc trace against the cooperative model (coop 1): must differ (coop flag and tensor_coop);
(3) one perturbed copy of a hart's trace events (one B tile moved by one tile; one store dropped): the comparison must find it.
/usr/bin/python3 3.12.3, standard library; reads only."""
import gzip
import importlib.util
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location("v04", os.path.join(HERE, "v04_independent.py"))
V4 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(V4)
RUNS = "<W>/out/v31-trace/traces/runs"


def load(name):
    return json.load(gzip.open(os.path.join(RUNS, name, "summary.json.gz"), "rt"))


def bases(s, harts):
    mins = {"A": None, "B": None, "C": None}
    for h in harts:
        for e in s["harts"][str(h)]["events"]:
            p = {"LA": "A", "LB": "B", "S": "C"}.get(e[0])
            if p and (mins[p] is None or e[2] < mins[p]):
                mins[p] = e[2]
    return mins


def compare(name, walk, coop, MB, NB, KB, harts):
    s = load(name)
    b = bases(s, harts)
    eq = ndiff = 0
    for h in harts:
        mev, _ = V4.model(walk, coop, MB, NB, KB, h // 64, (h % 64) // 2)
        tt, _ = V4.trace_tuples(s["harts"][str(h)]["events"], b)
        eq += tt == mev
        ndiff += sum(1 for a, c in zip(tt, mev) if a != c) + abs(len(tt) - len(mev))
    return {"harts": len(harts), "equal": eq, "differing_positions": ndiff}


def main():
    out = {}
    h4 = [0, 18, 36, 54, 8, 26, 44, 62]           # hart 0 of minions 0, 9, 18, 27, 4, 13, 22, 31 in shire 0
    out["t3_vs_mn_walk"] = compare("t3-gemmLn-2x4x16-0xf", "mn", 1, 2, 4, 16, h4)
    out["t3_vs_nm_walk_control"] = compare("t3-gemmLn-2x4x16-0xf", "nm", 1, 2, 4, 16, h4)
    out["t1_vs_nm_walk"] = compare("t1-gemmL-2x4x16-0xf", "nm", 1, 2, 4, 16, h4)
    out["t5_gemmLnc_vs_coop_model"] = compare("t5-gemmLnc-2x4x16-0xf", "mn", 1, 2, 4, 16, h4)
    s = load("t7-gemmL-1x1x16-0xf-all")
    harts = [64 * sh + 2 * m for sh in range(4) for m in range(32)]
    b = bases(s, harts)
    ev = [list(e) for e in s["harts"]["0"]["events"]]
    mev, _ = V4.model("mn", 1, 1, 1, 16, 0, 0)
    i = next(i for i, e in enumerate(ev) if e[0] == "LB" and i > 300)
    ev2 = [list(e) for e in ev]
    ev2[i][2] += 1024
    tt, _ = V4.trace_tuples(ev2, b)
    out["perturb_one_B_tile"] = {"equal": tt == mev, "differing_positions": sum(1 for a, c in zip(tt, mev) if a != c)}
    j = next(k for k, e in enumerate(ev) if e[0] == "S")
    ev3 = ev[:j] + ev[j + 1:]
    tt3, _ = V4.trace_tuples(ev3, b)
    out["perturb_drop_first_store"] = {"equal": tt3 == mev, "len_trace": len(tt3), "len_model": len(mev)}
    json.dump(out, sys.stdout, indent=1)
    print()


if __name__ == "__main__":
    main()
