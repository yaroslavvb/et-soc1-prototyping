#!/usr/bin/env python3
"""E153's self-test on the frozen registration (predictions-e153.json); nothing here is a measurement. A port of the idea of
tools/claims-v3/e141/selftest_e141.py: simulated sessions in three worlds, scored with the registered scorer (score_e153.score), the
bootstrap cut to 2,000 draws for speed:
  as good      every tile's D = M8's prediction + one draw from M8's nested aifoundry3 errors of its format; dT likewise from the
               heat reference; three passes with 0.05 W / 0.05 C pass noise; K1's tiles at Q139(u)'s re-reduced E141 D + their se
  twice as bad the same with every error doubled
  float bias   as good, with -0.3 W on every float tile (M8 too high)
and the C-check plumbing on stub files: every launch PASS keeps every tile; one ROUNDING launch removes its tile from the scored set and
fails KC; a launch with no C record does too.

    python3 tools/claims-v3/e153/selftest_e153.py [--worlds 40] > tools/claims-v3/e153/selftest.txt
SPDX-License-Identifier: Apache-2.0
"""
import copy
import json
import os
import random
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import score_e153 as S  # noqa: E402


def fake(reg, rng, factor, float_bias, passes=(15310, 15311, 15312)):
    ref, href = reg["reference_errors"]["power_a3"], reg["reference_errors"]["heat_normal_a3"]
    per = {str(p): {} for p in passes}
    items = {}
    for t, P in reg["tiles"].items():
        f = P["type"]
        e = 0.0 if P["pool_anchor"] and "zeros" in t else factor * ref[f][rng.randrange(len(ref[f]))]
        if f != "int8" and not P["pool_anchor"]:
            e += float_bias
        h = factor * href[f][rng.randrange(len(href[f]))]
        D = P["M8"]["D_w"] + e
        dT = P["M8"]["dT_win_c"] + h
        for p in passes:
            per[str(p)][t] = {"D": D + rng.gauss(0, 0.05), "dT_win": dT + rng.gauss(0, 0.05), "S": D + 2.0}
    for t, K in reg["k1"].items():
        m = K["E141_footing"]["mean"]
        vals = [m + rng.gauss(0, 0.03) for _ in passes]
        for p, v in zip(passes, vals):
            per[str(p)][t] = {"D": v, "dT_win": 1.0, "S": v + 2.0}
        mu = sum(vals) / len(vals)
        sd = (sum((v - mu) ** 2 for v in vals) / (len(vals) - 1)) ** 0.5
        items[t] = {"D": {"mean": mu, "se": sd / len(vals) ** 0.5, "n": len(vals), "ci95": 4.303 * sd / len(vals) ** 0.5}}
    for a in ("fp32.randn", "fp16.randn", "int8.full"):
        for p in passes:
            per[str(p)][a] = {"D": 20.0}
    return {"passes": list(passes), "per_pass": per, "items": items, "leak": {"mode": "0.20563713796102187"}, "passes_set_aside": []}


def c_plumbing(reg):
    out = []
    with tempfile.TemporaryDirectory() as d:
        pd, cd = os.path.join(d, "passes"), os.path.join(d, "cc")
        os.makedirs(os.path.join(pd, "p15310"))
        os.makedirs(cd)
        names = list(reg["tiles"]) + list(reg["k1"])
        runs, launches = [], []
        for i, t in enumerate(names):
            for j in range(3):
                ts = 1000 * i + 10 * j
                runs.append({"item": t, "t_start_ms": ts, "t_end_ms": ts + 5})
                launches.append({"t_start_ms": ts, "t_end_ms": ts + 5, "verdict": "PASS"})
        with open(os.path.join(pd, "p15310", "runs.jsonl"), "w") as f:
            f.write("\n".join(json.dumps(r) for r in runs) + "\n")
        res = {"passes": [15310]}
        for case, mutate in (("all PASS", None), ("one ROUNDING", "ROUNDING"), ("one missing", "missing")):
            L = copy.deepcopy(launches)
            if mutate == "ROUNDING":
                L[4]["verdict"] = "ROUNDING"
            elif mutate == "missing":
                L.pop(7)
            json.dump({"launches": L}, open(os.path.join(cd, "ccheck-all.json"), "w"))
            st = S.c_status(reg, res, cd, pd)
            bad = sorted(t for t in reg["tiles"] if not st[t]["all_pass"])
            out.append(f"C plumbing, {case}: tiles not all PASS {bad}")
    return out


def main():
    worlds = int(sys.argv[sys.argv.index("--worlds") + 1]) if "--worlds" in sys.argv else 40
    reg = json.load(open(os.path.join(HERE, "predictions-e153.json")))
    reg["plan"]["bootstrap"]["draws"] = 2000
    print(f"E153 self-test: {worlds} simulated sessions a world, three passes, bootstrap 2,000 draws; nothing here is a measurement")
    for name, factor, fb in (("as good", 1.0, 0.0), ("twice as bad", 2.0, 0.0), ("float bias -0.3 W", 1.0, -0.3)):
        rng = random.Random("E153|selftest|" + name)
        tally = {}
        for _ in range(worlds):
            s = S.score(fake(reg, rng, factor, fb), reg)
            for rid, v in S.verdicts(s).items():
                tally.setdefault(rid, {}).setdefault(v, 0)
                tally[rid][v] += 1
        print(f"\n{name}:")
        for rid in sorted(tally):
            print(f"  {rid:14s} " + ", ".join(f"{k} {v}" for k, v in sorted(tally[rid].items())))
    print()
    for line in c_plumbing(reg):
        print(line)


if __name__ == "__main__":
    main()
