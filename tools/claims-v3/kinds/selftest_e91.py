#!/usr/bin/env python3
# /// script
# requires-python = ">=3.9"
# dependencies = ["numpy"]
# ///
"""E91 self-test: E91's reduction and scoring run on SYNTHETIC card-1 passes with known answers, before any E91 data.

    python3 tools/claims-v3/kinds/selftest_e91.py <scratch dir> [--passes 5] [--seed 91]

It writes fake passes with E78's own generator (selftest_e78.make_pass) after installing E86's items and order, so
every pass is E86's 32-run order, with card 1's configuration reads (TDP 65, threshold 65, 499 mV), and injects
card 1's meter artifact: pairs of board_w samples 8-14 W low inside run windows (E82 A2). Two worlds:
  (a) "shared": every E78 kind at E82's measured card-1 D, every real tile at E86's measured D / E82's per-type
      scale (the real tiles share the card scale): E91-X4 must PASS, X3 must FAIL (E82's band), R1 must PASS;
  (b) "unshared": the real tiles at E86's D x 1.03 (card 1 reading them 3% above aifoundry3): X4 must FAIL.
It runs reduce_e91.py (dips removed, the primary), its dips-kept arm and one leakage arm, then score_e91.py.
NOTHING HERE IS A MEASUREMENT; the output is never data. Exit 0 if every check holds.
"""
import argparse
import gzip
import json
import os
import shutil
import subprocess
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, HERE)
import e86_common as e86  # noqa: E402

e86.install()
import e78_common as ec  # noqa: E402
import selftest_e78 as st  # noqa: E402

FIRST = 9110


def truth(world):
    reg = json.load(open(os.path.join(HERE, "predictions-e91.json")))
    e82 = json.load(open(os.path.join(ROOT, reg["inputs_frozen"]["e82_reduction"]["path"])))
    e86r = json.load(open(os.path.join(ROOT, reg["inputs_frozen"]["e86_reduction"]["path"])))
    D = {n: v["D"]["mean"] for n, v in e82["items"].items() if v.get("D") and v["D"].get("mean") is not None}
    for n, t in reg["tiles"].items():
        d86 = e86r["items"][n]["D"]["mean"]
        D[n] = d86 / t["card_scale_e82"] if world == "shared" else d86 * 1.03
    return D, reg


def inject_dips(d, rng, n_pairs=4):
    """Pairs of board_w samples 8-14 W low, inside run windows [t0+1.1 s, t0+2.9 s) of random runs."""
    recs = [json.loads(l) for l in open(os.path.join(d, "runs.jsonl"))]
    first = {}
    for r in recs:
        if r.get("launch", 0) >= 0:
            k = (r["item"], r["pos"])
            first[k] = min(first.get(k, r["t_start_ms"]), r["t_start_ms"])
    keys = sorted(first)
    pick = [keys[i] for i in rng.choice(len(keys), size=min(n_pairs, len(keys)), replace=False)]
    p = os.path.join(d, "telemetry.jsonl.gz")
    rows = [json.loads(l) for l in gzip.open(p, "rt")]
    ts = np.array([r["t_ms"] for r in rows], float)
    n = 0
    for k in pick:
        t0 = first[k] + 1100 + rng.uniform(0, 1700)
        i = int(np.searchsorted(ts, t0))
        if 2 <= i < len(rows) - 3:
            depth = rng.uniform(8, 14)
            for j in (i, i + 1):
                rows[j]["board_w"] = round(rows[j]["board_w"] - depth, 2)
                n += 1
    with gzip.open(p, "wt") as f:
        for r in rows:
            f.write(json.dumps(r) + "\n")
    return n


def run(args):
    r = subprocess.run([sys.executable] + args, capture_output=True, text=True)
    if r.returncode:
        print(r.stdout[-2000:], r.stderr[-3000:])
        sys.exit(f"failed: {args[0]}")
    return r


def run_world(scratch, world, passes, seed):
    rng = np.random.default_rng(seed)
    items = ec.load_items()
    D, reg = truth(world)
    base = os.path.join(scratch, world, "kinds")
    if os.path.isdir(base):
        shutil.rmtree(base)
    dirs, injected = [], {}
    for i in range(passes):
        p = FIRST + i
        d = os.path.join(base, f"p{p}")
        os.makedirs(d)
        st.make_pass(d, p, D, rng, items)
        cf = json.load(open(os.path.join(d, "configs.json")))
        cf["card"] = "aifoundry1-c1"
        json.dump(cf, open(os.path.join(d, "configs.json"), "w"))
        for nm in ("config_start", "config_end"):
            json.dump({"tdp_w": 65, "temp_threshold_c": 65, "power_state": 1, "power_state_name": "managed_power",
                       "minion_mhz": 600, "minion_mv": 499}, open(os.path.join(d, nm + ".json"), "w"))
        injected[str(p)] = inject_dips(d, rng)
        dirs.append(d)
    K = os.path.join(HERE)
    out = {}
    for arm, extra in (("primary", []), ("dipskept", ["--keep-dips"]), ("leak0.545", ["--leak", "0.545", "--no-refit"])):
        j = os.path.join(scratch, f"{world}-{arm}.json")
        run([os.path.join(K, "reduce_e91.py"), *dirs, "--out", j, *extra,
             "--txt", os.path.join(scratch, f"{world}-{arm}.txt")])
        out[arm] = j
    s = os.path.join(scratch, f"{world}-scored.json")
    run([os.path.join(K, "score_e91.py"), "--e91", out["primary"], "--arm", f"dips_kept={out['dipskept']}",
         "--arm", f"leak0.545={out['leak0.545']}", "--json", s, "--md", os.path.join(scratch, f"{world}-results.md")])
    return json.load(open(out["primary"])), json.load(open(out["dipskept"])), json.load(open(s)), D, reg, injected


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("scratch")
    ap.add_argument("--passes", type=int, default=5)
    ap.add_argument("--seed", type=int, default=91)
    a = ap.parse_args()
    os.makedirs(a.scratch, exist_ok=True)
    e, ek, sc, D, reg, inj = run_world(a.scratch, "shared", a.passes, a.seed)
    names = list(reg["tiles"]) + list(reg["e82_reference"])
    worst = max(abs(e["items"][n]["D"]["mean"] - D[n]) for n in names)
    worst_k = max(abs(ek["items"][n]["D"]["mean"] - D[n]) for n in names if ek["items"].get(n, {}).get("D", {}).get("mean") is not None) if ek["passes"] else None
    R = sc["rules"]
    removed = {k: v["samples_removed"] for k, v in (e["reducer"]["dip_samples_removed"] or {}).items()}
    checks = {
        "shared: dips injected (samples per pass)": (sum(inj.values()) > 0, inj),
        "shared: the primary removes them": (sum(removed.values()) >= sum(inj.values()), removed),
        "shared: primary keeps every pass": (len(e["passes"]) == a.passes, e["passes"]),
        "shared: config gate accepts card 1's 65/65": (not e["passes_config_flags"], e["passes_config_flags"]),
        "shared: 32 runs a pass, all kept": (e["runs"] == 32 * a.passes and e["kept"] == e["runs"], f"{e['kept']}/{e['runs']}"),
        "shared: D recovered within 0.15 W (primary)": (worst <= 0.15, round(worst, 4)),
        "shared: R1 PASS, 9 of 9 inside": (R["E91-R1"]["verdict"] == "PASS" and R["E91-R1"]["inside"] == 9, R["E91-R1"]["inside"]),
        "shared: R2 PASS": (R["E91-R2"]["verdict"] == "PASS", R["E91-R2"]["verdict"]),
        "shared: R5 PASS (the tie to E82's cells)": (R["E91-R5"]["verdict"] == "PASS", R["E91-R5"]["verdict"]),
        "shared: S1 PASS": (R["E91-S1"]["verdict"] == "PASS", R["E91-S1"]["inside"]),
        "shared: X4 PASS (real tiles share E82's scale)": (R["E91-X4"]["verdict"] == "PASS",
                                                           sc["cross_card"]["primary"]["x4"]["median_ratio"]),
        "shared: X3 FAIL (E82's band, scale 1.03)": (R["E91-X3"]["verdict"] == "FAIL",
                                                     sc["cross_card"]["primary"]["detail"]["x3"]["median_ratio"]),
        "shared: arms scored beside": (set(R["E91-R1"]["at_arms"]) == {"dips_kept", "leak0.545"}, R["E91-R1"]["at_arms"]),
    }
    e2, ek2, sc2, D2, _, inj2 = run_world(a.scratch, "unshared", a.passes, a.seed + 1)
    R2 = sc2["rules"]
    checks.update({
        "unshared: X4 FAIL": (R2["E91-X4"]["verdict"] == "FAIL", sc2["cross_card"]["primary"]["x4"]["median_ratio"]),
        "unshared: R1 still PASS (wide intervals)": (R2["E91-R1"]["verdict"] == "PASS", R2["E91-R1"]["inside"]),
    })
    ok_all = True
    for k, (ok, v) in checks.items():
        ok_all &= bool(ok)
        print(f"{'ok  ' if ok else 'FAIL'} {k}: {v}")
    print("informational (synthetic): dips-kept arm kept passes", ek["passes"], "set aside", ek.get("passes_set_aside"),
          "worst D error", None if worst_k is None else round(worst_k, 4))
    print("informational (synthetic): R3", {t: (round(v["rho"]["mean"], 4), v["verdict"]) for t, v in R["E91-R3"]["by_type"].items()},
          "R4", R["E91-R4"]["verdict"], "X1", R["E91-X1"]["verdict"], "X2a", R["E91-X2a"]["verdict"], "X2b", R["E91-X2b"]["verdict"])
    print("tallies on synthetic data (meaningless as a result):", sc["tally"], sc2["tally"])
    sys.exit(0 if ok_all else 1)


if __name__ == "__main__":
    main()
