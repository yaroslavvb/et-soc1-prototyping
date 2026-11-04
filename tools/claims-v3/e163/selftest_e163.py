#!/usr/bin/env python3
"""E163's self-tests of score_e163.py; nothing here is a measurement.

  --parent   the registered check (Q141's rule: each scorer is self-tested on its parent run's committed data): score_e163.py,
             configured as E153's registration (spec_from_e153 on tools/claims-v3/e153/predictions-e153.json: M8 primary, M7 and M6
             beside, pool 6's sets, the K1 re-run against E141, the card-scale rules), is run on E153's committed reductions, the
             desk's C check and the raw passes, exactly as E153's collector ran score_e153.py (the primary on Q139(u)'s footing with
             runs.csv, the seven arms beside), and every verdict and every number of E153's committed scored.json is compared with
             it, field by field (floats to 1e-12). PASS only if nothing differs.
  --worlds N simulated sessions on E163's frozen registration (predictions-e163.json), as selftest_e153.py did for E153: "as good"
             (every tile's D = M9's prediction + one draw from M9's nested aifoundry3 errors of its format, dT likewise), "twice as
             bad", and "float bias -0.3 W"; three passes, 0.05 W / 0.05 C pass noise, the bootstrap cut to 2,000 draws; the re-run
             tiles at their earlier D on the footing; and the C-check plumbing on stub files.

    python3 -B tools/claims-v3/e163/selftest_e163.py --parent > tools/claims-v3/e163/selftest-parent-e153.txt
    python3 -B tools/claims-v3/e163/selftest_e163.py --worlds 40 > tools/claims-v3/e163/selftest.txt
SPDX-License-Identifier: Apache-2.0
"""
import copy
import csv
import json
import math
import os
import random
import sys
import tempfile
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, HERE)
import score_e163 as S  # noqa: E402

E153D = os.path.join(ROOT, "docs", "reports", "data", "2026-11-03-e153-blind6-aifoundry3")
E153REG = os.path.join(ROOT, "tools", "claims-v3", "e153", "predictions-e153.json")
ARMS = (("session_own", "e153-session.json"), ("auto_dips_removed", "e153-auto-nodips.json"),
        ("kfrozen_dips_kept", "e153-kfrozen-dips.json"), ("leak0.1994", "e153-leak0.1994.json"),
        ("leak0.3803", "e153-leak0.3803.json"), ("leak0", "e153-leak0.json"), ("gates_off", "e153-gatesoff.json"))
SKIP_KEYS = {"rule", "reading", "why"}       # prose, reworded by the port; every number and verdict is compared


def compare(want, have, path, out):
    """Walk the committed structure; every leaf must be in the new one with the same value (floats to 1e-12)."""
    if isinstance(want, dict):
        if not isinstance(have, dict):
            out["diff"].append(f"{path}: committed a dict, new {type(have).__name__}")
            return
        for k, v in want.items():
            if k in SKIP_KEYS:
                continue
            if k not in have:
                out["diff"].append(f"{path}.{k}: missing in the new result")
                continue
            compare(v, have[k], f"{path}.{k}", out)
    elif isinstance(want, list):
        if not isinstance(have, list) or len(want) != len(have):
            out["diff"].append(f"{path}: list length {len(want)} != {len(have) if isinstance(have, list) else type(have).__name__}")
            return
        for i, (a, b) in enumerate(zip(want, have)):
            compare(a, b, f"{path}[{i}]", out)
    elif isinstance(want, float) or isinstance(have, float):
        out["n"] += 1
        try:
            ok = (want is None and have is None) or (math.isnan(float(want)) and math.isnan(float(have))) or \
                abs(float(want) - float(have)) <= 1e-12 * max(1.0, abs(float(want)))
        except (TypeError, ValueError):
            ok = False
        if not ok:
            out["diff"].append(f"{path}: committed {want!r}, new {have!r}")
    else:
        out["n"] += 1
        if want != have:
            out["diff"].append(f"{path}: committed {want!r}, new {have!r}")


def parent():
    t0 = time.time()
    reg = json.load(open(E153REG))
    spec = S.spec_from_e153(reg)
    prim = json.load(open(os.path.join(E153D, "e153.json")))
    arms = [(n, json.load(open(os.path.join(E153D, f)))) for n, f in ARMS]
    res = S.run(reg, prim, os.path.join(E153D, "runs.csv"), arms, os.path.join(E153D, "ccheck"), os.path.join(E153D, "aifoundry3", "e153"),
                spec=spec)
    want = json.load(open(os.path.join(E153D, "scored.json")))
    out = {"n": 0, "diff": []}
    compare(want["verdicts"], res["verdicts"], "verdicts", out)
    compare(want["arm_sensitive"], res["arm_sensitive"], "arm_sensitive", out)
    compare(want["c_status"], res["c_status"], "c_status", out)
    compare(want["primary"], res["primary"], "primary", out)
    for n, _ in ARMS:
        compare(want["arms"][n], res["arms"][n], f"arms.{n}", out)
        compare(S.verdicts(want["arms"][n], spec), S.verdicts(res["arms"][n], spec), f"arms.{n}.verdicts", out)
    L = ["E163 self-test on the parent run (score_e163.py configured as E153's registration, on E153's committed data); "
         "nothing here is a measurement", "",
         f"registration: tools/claims-v3/e153/predictions-e153.json (M8 primary, M7 and M6 beside; E153's sets, rules, seeds and K1)",
         f"data: docs/reports/data/2026-11-03-e153-blind6-aifoundry3/ (e153.json with runs.csv, the seven arms, ccheck/, aifoundry3/e153/)",
         f"compared: E153's committed scored.json, every verdict and number of its primary, its seven arms, c_status and arm_sensitive",
         "", "E153's registered verdicts (committed) and score_e163.py's (new):"]
    for k, v in want["verdicts"].items():
        L.append(f"  {k:18s} {v:14s} {res['verdicts'].get(k)}")
    L += ["", f"fields compared: {out['n']}; differing: {len(out['diff'])}"]
    L += [f"  DIFF {d}" for d in out["diff"][:40]]
    L.append(f"\nSELFTEST-PARENT {'PASS' if not out['diff'] else 'FAIL'}: {out['n']} fields, {len(out['diff'])} differ "
             f"({time.time() - t0:.0f} s)")
    print("\n".join(L))
    return 0 if not out["diff"] else 1


# ------------------------------------------------------------------------------------------------- simulated worlds (E163's freeze)
def fake(reg, rng, factor, float_bias, passes=(16310, 16311, 16312)):
    spec = reg["spec"]
    P = spec["primary"]
    ref, href = reg["reference_errors"]["power_a3"], reg["reference_errors"]["heat_normal_a3"]
    per = {str(p): {} for p in passes}
    items = {}
    for t, T in reg["tiles"].items():
        f = T["type"]
        e = 0.0 if T["pool_anchor"] and "zeros" in t else factor * ref[f][rng.randrange(len(ref[f]))]
        if f != "int8" and not T["pool_anchor"]:
            e += float_bias
        h = factor * href[f][rng.randrange(len(href[f]))]
        D = T[P]["D_w"] + e
        dT = T[P]["dT_win_c"] + h
        for p in passes:
            per[str(p)][t] = {"D": D + rng.gauss(0, 0.05), "dT_win": dT + rng.gauss(0, 0.05), "S": D + 2.0}
    for t, K in spec["reruns"]["tiles"].items():
        m = K["footing"]["mean"]
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
    spec = reg["spec"]
    with tempfile.TemporaryDirectory() as d:
        pd, cd = os.path.join(d, "passes"), os.path.join(d, "cc")
        os.makedirs(os.path.join(pd, "p16310"))
        os.makedirs(cd)
        names = list(reg["tiles"]) + list(spec["reruns"]["tiles"])
        runs, launches = [], []
        for i, t in enumerate(names):
            for j in range(3):
                ts = 1000 * i + 10 * j
                runs.append({"item": t, "t_start_ms": ts, "t_end_ms": ts + 5})
                launches.append({"t_start_ms": ts, "t_end_ms": ts + 5, "verdict": "PASS"})
        with open(os.path.join(pd, "p16310", "runs.jsonl"), "w") as f:
            f.write("\n".join(json.dumps(r) for r in runs) + "\n")
        res = {"passes": [16310]}
        for case, mutate in (("all PASS", None), ("one ROUNDING", "ROUNDING"), ("one missing", "missing")):
            L = copy.deepcopy(launches)
            if mutate == "ROUNDING":
                L[4]["verdict"] = "ROUNDING"
            elif mutate == "missing":
                L.pop(7)
            json.dump({"launches": L}, open(os.path.join(cd, "ccheck-all.json"), "w"))
            st = S.c_status(reg, res, cd, pd, spec)
            bad = sorted(t for t in names if not st[t]["all_pass"])
            out.append(f"C plumbing, {case}: tiles not all PASS {bad}")
    return out


def worlds(n):
    reg = json.load(open(os.path.join(HERE, "predictions-e163.json")))
    reg["spec"]["bootstrap"]["draws"] = 2000
    print(f"E163 self-test: {n} simulated sessions a world on predictions-e163.json, three passes, bootstrap 2,000 draws; "
          "nothing here is a measurement")
    for name, factor, fb in (("as good", 1.0, 0.0), ("twice as bad", 2.0, 0.0), ("float bias -0.3 W", 1.0, -0.3)):
        rng = random.Random("E163|selftest|" + name)
        tally = {}
        for _ in range(n):
            s = S.score(fake(reg, rng, factor, fb), reg)
            for rid, v in S.verdicts(s, reg["spec"]).items():
                tally.setdefault(rid, {}).setdefault(v, 0)
                tally[rid][v] += 1
        print(f"\n{name}:")
        for rid in sorted(tally):
            print(f"  {rid:16s} " + ", ".join(f"{k} {v}" for k, v in sorted(tally[rid].items())))
    print()
    for line in c_plumbing(reg):
        print(line)
    eb = reg["spec"]["e151_block"]
    e = S.score_e151_block(reg, None, None)
    print(f"E151 block with no block reduced: {eb['id']} {e[eb['id']]['verdict']}")
    for line in e151_repeat(reg):
        print(line)
    print(render(reg))
    return 0


def e151_repeat(reg):
    """The E151 block's scoring path end to end: E151's own committed reduction (runs.csv, e151.json), its B blocks renumbered
    15110-15119 -> 16350-16359 (E163's), scored as an E163 block must read as an exact repeat of E151's reference (every
    difference 0, KE-D and KE-W PASS; KE-C NOT SCORED, no C check given)."""
    eb = reg["spec"]["e151_block"]
    src = os.path.join(ROOT, "docs", "reports", "data", "2026-11-03-e151-int8-b-aifoundry3")
    ren = {str(p): str(p + 1240) for p in range(15110, 15120)}
    out = []
    with tempfile.TemporaryDirectory() as d:
        rows = list(csv.DictReader(open(os.path.join(src, "runs.csv"))))
        with open(os.path.join(d, "runs.csv"), "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
            w.writeheader()
            for r in rows:
                p = str(int(float(r["pass"])))
                if p in ren:
                    r = dict(r, **{"pass": ren[p]})
                w.writerow(r)
        red = json.load(open(os.path.join(src, "e151.json")))
        mp = lambda x: int(ren.get(str(x), x))  # noqa: E731
        red["passes"] = [mp(p) for p in red.get("passes", [])]
        for k in ("passes_set_aside", "passes_config_flags"):
            red[k] = [dict(x, **{"pass": mp(x["pass"])}) for x in red.get(k, [])]
        json.dump(red, open(os.path.join(d, "e151.json"), "w"))
        e = S.score_e151_block(reg, os.path.join(d, "runs.csv"), os.path.join(d, "e151.json"))
    diffs = [abs(r["diff_w"]) for r in e["tiles"].values() if "diff_w" in r]
    out.append(f"E151 block, E151's own blocks renumbered and scored as E163's: blocks kept {e['blocks_kept']}; "
               f"{eb['id']}-D {e[eb['id'] + '-D']['verdict']}, {eb['id']}-W {e[eb['id'] + '-W']['verdict']}, "
               f"{eb['id']}-C {e[eb['id'] + '-C']['verdict']}; largest |difference| {max(diffs) if diffs else None} W over {len(diffs)} tiles")
    return out


def render(reg):
    """One simulated session through run() and markdown(), as the collector calls them: the page renders."""
    rng = random.Random("E163|selftest|render")
    res = S.run(reg, fake(reg, rng, 1.0, 0.0), arm_files=[("same", fake(reg, random.Random("E163|selftest|render"), 1.0, 0.0))])
    md = S.markdown(res, reg, reg["spec"])
    return f"results page from one simulated session: {len(md.splitlines())} lines, verdicts {len(res['verdicts'])}, " \
           f"RANK1 {res['verdicts'].get('E163-RANK1')}"


if __name__ == "__main__":
    if "--parent" in sys.argv:
        sys.exit(parent())
    sys.exit(worlds(int(sys.argv[sys.argv.index("--worlds") + 1]) if "--worlds" in sys.argv else 40))
