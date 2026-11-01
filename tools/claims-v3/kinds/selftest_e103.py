#!/usr/bin/env python3
# /// script
# requires-python = ">=3.9"
# dependencies = ["numpy"]
# ///
"""E103 self-test: E103's reduction and scoring run on SYNTHETIC card-1 passes with known answers, before any E103 data.

    python3 tools/claims-v3/kinds/selftest_e103.py <scratch dir> [--passes 3] [--seed 103]

It writes fake passes with E78's own generator (selftest_e78.make_pass) after installing E103's items and order, with card 1's configuration reads and card 1's
meter dips injected, and scores worlds that must come out differently:
  (a) "model": every tile at M4's or I3's frozen point: R1, R2, R4, R5 and R7 PASS, the tie PASS, the A side GONE, gated PASS;
  (b) "null":  every tile at Q130(n)'s point: R1 FAIL, R2 FAIL;
  (c) "aside": the model, with the A-side tiles' switching 20% low and the gated float tiles 0.6 W high: R8 PERSISTS, R9 FAIL;
and checks that two kept passes score and one does not. NOTHING HERE IS A MEASUREMENT; the output is never data. Exit 0 if every check holds.
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
import e103_common as e103  # noqa: E402

e103.install()
import e78_common as ec  # noqa: E402
import selftest_e78 as st  # noqa: E402

FIRST = 10310


def truth(world, rng):
    reg = json.load(open(os.path.join(HERE, "predictions-e103.json")))
    nod = json.load(open(os.path.join(ROOT, reg["inputs_frozen"]["e82_nodips"]["path"])))
    D = {n: v["D"]["mean"] for n, v in nod["items"].items() if v.get("D") and v["D"].get("mean") is not None}
    for n, t in reg["tiles"].items():
        p = t["pred"]
        if world == "null":
            D[n] = p["q130n"]
        else:
            D[n] = p["M"]
        if world == "aside":
            if t["kind"].startswith(("h_a_", "o_a_")):
                D[n] = p["terms_w"][-1] + 0.80 * (p["M"] - p["terms_w"][-1])
            elif t["type"] != "int8" and p["gate"] >= 0.10:
                D[n] = p["M"] + 0.6
    return D, reg


def inject_dips(d, rng, n_pairs=4):
    """Pairs of board_w samples 8-14 W low, inside run windows of random runs (selftest_e91's card-1 meter artifact)."""
    recs = [json.loads(line) for line in open(os.path.join(d, "runs.jsonl"))]
    first = {}
    for r in recs:
        if r.get("launch", 0) >= 0:
            k = (r["item"], r["pos"])
            first[k] = min(first.get(k, r["t_start_ms"]), r["t_start_ms"])
    keys = sorted(first)
    pick = [keys[i] for i in rng.choice(len(keys), size=min(n_pairs, len(keys)), replace=False)]
    p = os.path.join(d, "telemetry.jsonl.gz")
    rows = [json.loads(line) for line in gzip.open(p, "rt")]
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
    D, reg = truth(world, rng)
    base = os.path.join(scratch, world, "kinds")
    if os.path.isdir(base):
        shutil.rmtree(base)
    dirs = []
    injected = 0
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
        injected += inject_dips(d, rng)
        dirs.append(d)
    j = os.path.join(scratch, f"{world}.json")
    run([os.path.join(HERE, "reduce_e103.py"), *dirs, "--out", j, "--leak", "0.15", "--no-refit", "--txt", os.path.join(scratch, f"{world}.txt")])
    k = os.path.join(scratch, f"{world}-dipskept.json")
    run([os.path.join(HERE, "reduce_e103.py"), *dirs, "--keep-dips", "--out", k, "--leak", "0.15", "--no-refit"])
    s = os.path.join(scratch, f"{world}-scored.json")
    run([os.path.join(HERE, "score_e103.py"), "--e103", j, "--arm", f"dips_kept={k}", "--json", s, "--md", os.path.join(scratch, f"{world}-results.md")])
    return json.load(open(j)), json.load(open(s)), D, injected, dirs, reg


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("scratch")
    ap.add_argument("--passes", type=int, default=3)
    ap.add_argument("--seed", type=int, default=103)
    a = ap.parse_args()
    os.makedirs(a.scratch, exist_ok=True)
    checks = {}

    def v(R, rid):
        return R[rid]["verdict"]

    e, sc, D, inj, dirs, reg = run_world(a.scratch, "model", a.passes, a.seed)
    R = sc["primary"]["rules"]
    n_tiles = len(e103.E103_NAMES)
    worst = max(abs(e["items"][n]["D"]["mean"] - D[n]) for n in e103.E103_NAMES)
    checks.update({
        "model: dips injected and removed": (inj > 0 and sum(x["samples_removed"] for x in e["reducer"]["dip_samples_removed"].values()) >= inj, inj),
        "model: every pass kept": (len(e["passes"]) == a.passes, e["passes"]),
        "model: every run kept": (e["runs"] == reg["plan"]["runs_per_pass"] * a.passes and e["kept"] == e["runs"], f"{e['kept']}/{e['runs']}"),
        "model: config gate accepts card 1's 65/65": (not e["passes_config_flags"], e["passes_config_flags"]),
        "model: D recovered within 0.3 W": (worst <= 0.3, round(worst, 4)),
        "model: experiment is E103": (e.get("experiment") == "E103", e.get("experiment")),
        "model: R1 PASS": (v(R, "E103-R1") == "PASS", R["E103-R1"].get("rms_w")),
        "model: R2 PASS": (v(R, "E103-R2") == "PASS", R["E103-R2"].get("gap_w")),
        "model: R3 PASS": (v(R, "E103-R3") == "PASS", R["E103-R3"].get("gap_w")),
        "model: R4 PASS": (v(R, "E103-R4") == "PASS", R["E103-R4"].get("rms_w")),
        "model: R7 PASS": (v(R, "E103-R7") == "PASS", R["E103-R7"].get("fraction")),
        "model: R8 GONE": (v(R, "E103-R8") == "GONE", R["E103-R8"].get("mean_measured_over_predicted")),
        "model: R9 PASS": (v(R, "E103-R9") == "PASS", R["E103-R9"].get("mean_measured_minus_predicted_w")),
        "model: S1 PASS": (v(R, "E103-S1") == "PASS", R["E103-S1"]["cells"]),
    })
    for nn, scored in ((2, True), (1, False)):
        j = os.path.join(a.scratch, f"thin{nn}.json")
        run([os.path.join(HERE, "reduce_e103.py"), *dirs[:nn], "--out", j, "--leak", "0.15", "--no-refit"])
        s = os.path.join(a.scratch, f"thin{nn}-scored.json")
        run([os.path.join(HERE, "score_e103.py"), "--e103", j, "--json", s])
        t = json.load(open(s))["primary"]
        if scored:
            checks[f"{nn} kept passes are scored"] = (t["rules"]["E103-R1"]["verdict"] != "NOT SCORED", t["tally"])
        else:
            checks[f"{nn} kept pass: NOT SCORED"] = (set(t["tally"]) == {"NOT SCORED"}, t["tally"])
    e, sc, D, inj, dirs, reg = run_world(a.scratch, "null", a.passes, a.seed + 1)
    R = sc["primary"]["rules"]
    checks["null: R1 FAIL"] = (v(R, "E103-R1") == "FAIL", R["E103-R1"].get("rms_w"))
    checks["null: R2 FAIL"] = (v(R, "E103-R2") == "FAIL", R["E103-R2"].get("gap_w"))
    e, sc, D, inj, dirs, reg = run_world(a.scratch, "aside", a.passes, a.seed + 2)
    R = sc["primary"]["rules"]
    checks["aside: R8 PERSISTS"] = (v(R, "E103-R8") == "PERSISTS", R["E103-R8"].get("mean_measured_over_predicted"))
    checks["aside: R9 FAIL"] = (v(R, "E103-R9") == "FAIL", R["E103-R9"].get("mean_measured_minus_predicted_w"))
    ok_all = True
    for k, (ok, val) in checks.items():
        ok_all &= bool(ok)
        print(f"{'ok  ' if ok else 'FAIL'} {k}: {val}")
    print(f"{sum(1 for x in checks.values() if x[0])} of {len(checks)} checks; {n_tiles} tiles")
    sys.exit(0 if ok_all else 1)


if __name__ == "__main__":
    main()
