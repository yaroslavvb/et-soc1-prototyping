#!/usr/bin/env python3
# /// script
# requires-python = ">=3.9"
# dependencies = ["numpy"]
# ///
"""E93 self-test: E93's reduction and scoring run on SYNTHETIC card-1 passes with known answers, before any E93 data.

    python3 tools/claims-v3/kinds/selftest_e93.py <scratch dir> [--passes 4] [--seed 93]

It writes fake passes with E78's own generator (selftest_e78.make_pass) after installing E93's items and order, with card
1's configuration reads and card 1's meter dips injected, and scores four worlds that must come out differently:
  (a) "rtl":     every prediction true at its point: every rule and the session tie PASS, reading (l, l+8);
  (b) "a4":      -0 and denormals gated like real zeros, int8 pairs by (2l, 2l+1), one nonzero A byte gates, the masked tile
                 equals the clean one: R1, R3, R6a, R6b, R6c, R7, R8 FAIL, reading (2l, 2l+1);
  (c) "noflush": the gate as registered but the multiplier sees denormal fractions, and the Booth asymmetry absent: R4, R5
                 FAIL, R1 and R3 still PASS;
  (d) "flat":    int8's three arrangements alike: R6a, R6b FAIL, R6c PASS, reading "neither";
and checks that three kept passes score and two do not.
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
import e93_common as e93  # noqa: E402

e93.install()
import e78_common as ec  # noqa: E402
import selftest_e78 as st  # noqa: E402

FIRST = 9310


def truth(world):
    reg = json.load(open(os.path.join(HERE, "predictions-e93.json")))
    e82 = json.load(open(os.path.join(ROOT, reg["inputs_frozen"]["e82_reduction"]["path"])))
    D = {n: v["D"]["mean"] for n, v in e82["items"].items() if v.get("D") and v["D"].get("mean") is not None}
    for n, t in reg["tiles"].items():
        D[n] = t["point_w"]
    if world == "a4":
        for n in ("fp32.nz_both", "fp32.dn1_both", "fp32.dnr_both", "fp16.nz_both", "fp16.dnr_both"):
            D[n] = 0.05
        D["fp32.a_nz_b_randn"] = D["fp32.a_dnr_b_randn"] = D["fp32.a_zeros_b_randn"]
        D["fp32.a_randn_b_nz"] = D["fp32.a_randn_b_dnr"] = D["fp32.a_randn_b_zeros"]
        D["fp16.a_nz_b_randn"] = D["fp16.a_dnr_b_randn"] = D["fp16.a_zeros_b_randn"]
        D["fp16.a_randn_b_nz"] = D["fp16.a_randn_b_zeros"]
        p, q = D["int8.b_pairs_rtl"], D["int8.b_pairs_alt"]
        D["int8.b_pairs_rtl"], D["int8.b_pairs_alt"], D["int8.b_unpaired"] = q, p, q
        D["int8.a_3of4_b_full"] = D["int8.a_zeros_b_full"]
        D["fp32.sparse50_mask"] = D["fp32.sparse50"]
    if world == "noflush":
        for n in ("fp32.dnr_both", "fp32.a_dnr_b_randn", "fp16.dnr_both", "fp16.a_dnr_b_randn"):
            D[n] = reg["tiles"][n]["if_not_flushed_w"]
        D["fp32.a_randn_b_nz"] = D["fp32.a_nz_b_randn"]
    if world == "flat":
        D["int8.b_pairs_alt"] = D["int8.b_unpaired"] = D["int8.b_pairs_rtl"]
    return D, reg


def inject_dips(d, rng, n_pairs=4):
    """Pairs of board_w samples 8-14 W low, inside run windows of random runs (selftest_e91's card-1 meter artifact)."""
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
    run([os.path.join(HERE, "reduce_e93.py"), *dirs, "--out", j, "--leak", "0.15", "--no-refit",
         "--txt", os.path.join(scratch, f"{world}.txt")])
    k = os.path.join(scratch, f"{world}-dipskept.json")
    run([os.path.join(HERE, "reduce_e93.py"), *dirs, "--keep-dips", "--out", k, "--leak", "0.15", "--no-refit"])
    s = os.path.join(scratch, f"{world}-scored.json")
    run([os.path.join(HERE, "score_e93.py"), "--e93", j, "--arm", f"dips_kept={k}", "--json", s,
         "--md", os.path.join(scratch, f"{world}-results.md")])
    return json.load(open(j)), json.load(open(s)), D, injected, dirs


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("scratch")
    ap.add_argument("--passes", type=int, default=4)
    ap.add_argument("--seed", type=int, default=93)
    a = ap.parse_args()
    os.makedirs(a.scratch, exist_ok=True)
    checks = {}
    e, sc, D, inj, dirs = run_world(a.scratch, "rtl", a.passes, a.seed)
    P = sc["primary"]
    R = P["rules"]
    worst = max(abs(e["items"][n]["D"]["mean"] - D[n]) for n in list(e93.E93_NAMES) + list(e93.COMPARE))
    checks.update({
        "rtl: dips injected and removed": (inj > 0 and sum(v["samples_removed"] for v in e["reducer"]["dip_samples_removed"].values()) >= inj, inj),
        "rtl: every pass kept": (len(e["passes"]) == a.passes, e["passes"]),
        "rtl: 40 runs a pass, all kept": (e["runs"] == 40 * a.passes and e["kept"] == e["runs"], f"{e['kept']}/{e['runs']}"),
        "rtl: config gate accepts card 1's 65/65": (not e["passes_config_flags"], e["passes_config_flags"]),
        "rtl: D recovered within 0.15 W": (worst <= 0.15, round(worst, 4)),
        "rtl: every rule PASS": (all(v["verdict"] == "PASS" for v in R.values()), {k: v["verdict"] for k, v in R.items() if v["verdict"] != "PASS"}),
        "rtl: reading (l, l+8)": (P["pairing_reading"].startswith("rtl"), P["pairing_reading"]),
        "rtl: session tie PASS": (P["tie"]["verdict"] == "PASS", P["tie"]["verdict"]),
        "rtl: every tile inside its band": (all(v["verdict"] == "PASS" for v in P["tiles"].values()), {k: v["verdict"] for k, v in P["tiles"].items() if v["verdict"] != "PASS"}),
    })
    for nn in (3, 2):
        j = os.path.join(a.scratch, f"thin{nn}.json")
        run([os.path.join(HERE, "reduce_e93.py"), *dirs[:nn], "--out", j, "--leak", "0.15", "--no-refit"])
        s = os.path.join(a.scratch, f"thin{nn}-scored.json")
        run([os.path.join(HERE, "score_e93.py"), "--e93", j, "--json", s])
        t = json.load(open(s))["primary"]
        if nn == 3:
            checks["three kept passes are scored"] = (t["rules"]["R1-fp32-both"]["verdict"] == "PASS", t["tally"])
        else:
            checks["two kept passes: NOT SCORED"] = (set(t["tally"]) == {"NOT SCORED"}, t["tally"])
    e, sc, D, inj, dirs = run_world(a.scratch, "a4", a.passes, a.seed + 1)
    P = sc["primary"]
    R = P["rules"]
    for rid in ("R1-fp32-both", "R1-fp32-a", "R1-fp16-both", "R1-fp16-a", "R3-fp32-one", "R3-fp32-both", "R3-fp32-a",
                "R3-fp16-both", "R3-fp16-a", "R6a", "R6b", "R6c", "R7", "R8"):
        checks[f"a4: {rid} FAIL"] = (R[rid]["verdict"] == "FAIL", R[rid]["verdict"])
    checks["a4: reading (2l, 2l+1)"] = (P["pairing_reading"].startswith("alt"), P["pairing_reading"])
    e, sc, D, inj, dirs = run_world(a.scratch, "noflush", a.passes, a.seed + 2)
    R = sc["primary"]["rules"]
    for rid in ("R4-fp32-both", "R4-fp32-a", "R4-fp16-both", "R4-fp16-a", "R5-fp32"):
        checks[f"noflush: {rid} FAIL"] = (R[rid]["verdict"] == "FAIL", (R[rid]["verdict"], round(R[rid]["contrast"]["mean"], 3)))
    for rid in ("R1-fp32-both", "R3-fp32-both", "R6b"):
        checks[f"noflush: {rid} still PASS"] = (R[rid]["verdict"] == "PASS", R[rid]["verdict"])
    e, sc, D, inj, dirs = run_world(a.scratch, "flat", a.passes, a.seed + 3)
    P = sc["primary"]
    R = P["rules"]
    for rid, want in (("R6a", "FAIL"), ("R6b", "FAIL"), ("R6c", "PASS")):
        checks[f"flat: {rid} {want}"] = (R[rid]["verdict"] == want, (R[rid]["verdict"], round(R[rid]["contrast"]["mean"], 3), round(R[rid]["contrast"]["ci95"], 3)))
    checks["flat: reading neither"] = (P["pairing_reading"].startswith("neither"), P["pairing_reading"])
    ok_all = True
    for k, (ok, v) in checks.items():
        ok_all &= bool(ok)
        print(f"{'ok  ' if ok else 'FAIL'} {k}: {v}")
    print(f"{sum(1 for x in checks.values() if x[0])} of {len(checks)} checks")
    sys.exit(0 if ok_all else 1)


if __name__ == "__main__":
    main()
