#!/usr/bin/env python3
"""E95: Q132(b)'s RTL bench predictions beside the measurement. Standard library only; run from this directory.

    python3 bench-check.py > bench-check.txt

Reads the two frozen files, byte for byte as of their commits, and this directory's reductions. It changes no verdict: the
bench's predictions are not among E95's registered claims. M2 is the bench's frozen primary (`models.vpu_map`, k per net toggle and a
per clocked bit, fitted on E78 alone, commit 2b7ece4a, 01:03:01 PST); M4 prices the lane operand bus apart (commit b995463e, 01:08:31 PST).
Q130(n)'s predictor (a) is beside them, on the same tiles, from predictions-real2.json. The bench and (a) are stated at E78's
primary leakage slope (0.1994 W/C), so the 0.1994 arm is the like-with-like column; E95's primary slope is its own.
"""
import json
import math
import os
import statistics

HERE = os.path.dirname(os.path.abspath(__file__))
M2 = json.load(open(os.path.join(HERE, "bench-prediction-2b7ece4a.json")))["models"]["vpu_map"]
M4 = json.load(open(os.path.join(HERE, "bench-prediction-m4-b995463e.json")))["e95_aifoundry3"]
M2T = M2["e95_aifoundry3"]
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
F = json.load(open(os.path.join(ROOT, "tools/claims-v3/kinds/real2/predictions-real2.json")))
REDS = {"primary (auto 0.2959, passes 9510 9511 9512 9514)": "e95.json", "the 0.1994 arm (passes 9511 9512 9514)": "e95-leak0.1994.json",
        "the dips-removed arm (auto 0.2989, five passes)": "dips-arm/e95-nodips.json"}
TYPES = ("fp32", "fp16", "int8")


def key(item):
    ty, k = item.split(".", 1)
    return f"{ty}/{k[3:]}" if k.startswith("r2_") else None


def rms(v):
    return math.sqrt(sum(x * x for x in v) / len(v)) if v else None


def rows(res):
    out = {}
    for it, m2 in M2T.items():
        D = res["items"].get(it, {}).get("D", {})
        if D.get("mean") is None:
            continue
        k = key(it)
        out[it] = {"D": D["mean"], "ci": D.get("ci95"), "n": D.get("n"), "m2": m2["D_w"], "m2lo": m2["lo95"], "m2hi": m2["hi95"], "m4": M4[it]["D_w"],
                   "m4lo": M4[it]["lo95"], "m4hi": M4[it]["hi95"], "a": F["tiles"][k]["a_aifoundry3_600mhz"]["D_w"] if k else None,
                   "blind": bool(m2.get("blind")), "type": m2["type"], "group": m2.get("group")}
    return out


def summary(R, label):
    print(f"\n## {label}\n")
    print("| set | tiles | M2 rms W | M2 mean error W | M2 inside 95% | M4 rms W | M4 mean error W | M4 inside 95% | (a) rms W | (a) mean error W |")
    print("|---|---|---|---|---|---|---|---|---|---|")
    sets = [("all blind", [v for v in R.values() if v["blind"]])]
    for ty in TYPES:
        sets.append((ty, [v for v in R.values() if v["blind"] and v["type"] == ty]))
    for g, name in (("Z", "ReLU tiles"), ("N", "no exact zeros"), ("C", "int8 calibrations")):
        sets.append((name, [v for v in R.values() if v["blind"] and v["group"] == g]))
    for name, vs in sets:
        e2 = [v["D"] - v["m2"] for v in vs]
        e4 = [v["D"] - v["m4"] for v in vs]
        ea = [v["D"] - v["a"] for v in vs if v["a"] is not None]
        print(f"| {name} | {len(vs)} | {rms(e2):.3f} | {statistics.fmean(e2):+.3f} | {sum(1 for v in vs if v['m2lo'] <= v['D'] <= v['m2hi'])} | {rms(e4):.3f} | {statistics.fmean(e4):+.3f} | "
              f"{sum(1 for v in vs if v['m4lo'] <= v['D'] <= v['m4hi'])} | {rms(ea):.3f} | {statistics.fmean(ea):+.3f} |")


def main():
    print("# E95 against Q132(b)'s frozen bench predictions (bench-check.py; D in W over the type's own zeros; nothing here is a verdict)")
    allr = {}
    for label, f in REDS.items():
        res = json.load(open(os.path.join(HERE, f)))
        R = rows(res)
        allr[label] = R
        summary(R, label)
    print("\n## Every tile, primary reduction\n")
    print("| tile | group | blind | D ± 95% | n | M2 [95%] | D − M2 | in | M4 [95%] | D − M4 | in | (a) | D − (a) |")
    print("|---|---|---|---|---|---|---|---|---|---|---|---|---|")
    R = allr[list(REDS)[0]]
    for it, v in sorted(R.items(), key=lambda kv: (kv[1]["type"], -kv[1]["D"])):
        aa = f"{v['a']:.2f} | {v['D'] - v['a']:+.2f}" if v["a"] is not None else "— | —"
        print(f"| `{it}` | {v['group']} | {'yes' if v['blind'] else 'no'} | {v['D']:.3f} ± {v['ci'] if v['ci'] is None else round(v['ci'], 3)} | {v['n']} | {v['m2']:.2f} [{v['m2lo']:.2f}, {v['m2hi']:.2f}] | {v['D'] - v['m2']:+.2f} | "
              f"{'yes' if v['m2lo'] <= v['D'] <= v['m2hi'] else 'no'} | {v['m4']:.2f} [{v['m4lo']:.2f}, {v['m4hi']:.2f}] | {v['D'] - v['m4']:+.2f} | {'yes' if v['m4lo'] <= v['D'] <= v['m4hi'] else 'no'} | {aa} |")
    print("\n## Offsets, M2's `e95_offsets` beside the measured paired difference\n")
    print("| tile | partner | M2 offset W [95%] | M4 offset W (its points) | measured W ± 95% (primary) | n | measured W ± 95% (dips-removed) | n |")
    print("|---|---|---|---|---|---|---|---|")
    primary = json.load(open(os.path.join(HERE, "scored.json")))
    dips = json.load(open(os.path.join(HERE, "dips-arm/scored-nodips.json")))
    for o in M2["e95_offsets"] if isinstance(M2["e95_offsets"], list) else M2["e95_offsets"].values():
        it = o.get("tile") or o.get("item")
        p = o.get("partner")
        a = primary["tiles"][it].get("a_prime") or {}
        d = dips["tiles"][it].get("a_prime") or {}
        ma, da = a.get("measured_w", {}), d.get("measured_w", {})
        off = o["offset_w"]
        lo, hi = off - o["half95_conservative"], off + o["half95_conservative"]
        print(f"| `{it}` | `{p}` | {off:+.2f} [{lo:+.2f}, {hi:+.2f}] | {M4[it]['D_w'] - M4[p]['D_w']:+.2f} | {ma.get('mean'):+.3f} ± {ma.get('ci95'):.3f} | {ma.get('n')} | {da.get('mean'):+.3f} ± {da.get('ci95'):.3f} | {da.get('n')} |")


if __name__ == "__main__":
    main()
