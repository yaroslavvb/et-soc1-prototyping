#!/usr/bin/env python3
# /// script
# requires-python = ">=3.9"
# dependencies = ["numpy"]
# ///
"""E94 self-test: E94's reduction and scoring run on SYNTHETIC card-1 passes with known answers, before any E94 data.

    python3 tools/claims-v3/kinds/selftest_e94.py <scratch dir> [--passes 3] [--seed 94]

It writes fake passes with E78's own generator (selftest_e78.make_pass) after installing E94's items and order, with card
1's configuration reads and card 1's meter dips injected, and scores worlds that must come out differently:
  (a) "law":   every draw at the committed tile's E82 value plus the gate law's frozen delta (the dense rules at Q130(n)'s):
               R3, R4a, R6, R7 (gate law) and R8 PASS, the tie PASS, and fp16.nn_like's row gets its CORRECTION;
  (b) "flat":  every draw reads its committed tile: no spread: R3 FAIL, R4a PASS, R6 and R7 FAIL, no row needs correcting;
  (c) "wild":  draws scattered at SD 1.5 W with no relation to the tile: R4a FAIL, R6 and R7 FAIL, R8 FAIL;
  (d) "off":   the committed tiles 4 W above where the law puts their draws: R1 FAIL (outside the spread) and CORRECTION;
and checks that three and two kept passes score and one does not. NOTHING HERE IS A MEASUREMENT; the output is never data.
Exit 0 if every check holds.
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
import e94_common as e94  # noqa: E402

e94.install()
import e78_common as ec  # noqa: E402
import selftest_e78 as st  # noqa: E402

FIRST = 9410


def truth(world, rng):
    reg = json.load(open(os.path.join(HERE, "predictions-e94.json")))
    nod = json.load(open(os.path.join(ROOT, reg["inputs_frozen"]["e82_nodips"]["path"])))
    D = {n: v["D"]["mean"] for n, v in nod["items"].items() if v.get("D") and v["D"].get("mean") is not None}
    gated = reg["rules"]["E94-R3"]["rules"]
    for n, t in reg["tiles"].items():
        c = t["rule_of"]
        if world == "flat":
            D[n] = D[c]
        elif world == "wild":
            D[n] = D[c] + float(rng.normal(0, 1.5))
        else:
            D[n] = t["D_pred_gate_law_card1_w"] if c in gated else t["D_pred_q130n_card1_w"]
    if world == "off":
        for c in reg["rules_of_number"]:
            if not reg["rules_of_number"][c]["committed_is_anchor"]:
                D[c] = D[c] + 4.0
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
    run([os.path.join(HERE, "reduce_e94.py"), *dirs, "--out", j, "--leak", "0.15", "--no-refit",
         "--txt", os.path.join(scratch, f"{world}.txt")])
    k = os.path.join(scratch, f"{world}-dipskept.json")
    run([os.path.join(HERE, "reduce_e94.py"), *dirs, "--keep-dips", "--out", k, "--leak", "0.15", "--no-refit"])
    s = os.path.join(scratch, f"{world}-scored.json")
    run([os.path.join(HERE, "score_e94.py"), "--e94", j, "--arm", f"dips_kept={k}", "--json", s,
         "--md", os.path.join(scratch, f"{world}-results.md")])
    return json.load(open(j)), json.load(open(s)), D, injected, dirs, reg


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("scratch")
    ap.add_argument("--passes", type=int, default=3)
    ap.add_argument("--seed", type=int, default=94)
    a = ap.parse_args()
    os.makedirs(a.scratch, exist_ok=True)
    checks = {}

    def v(R, rid):
        return R[rid]["verdict"]

    e, sc, D, inj, dirs, reg = run_world(a.scratch, "law", a.passes, a.seed)
    P = sc["primary"]
    R = P["rules"]
    worst = max(abs(e["items"][n]["D"]["mean"] - D[n]) for n in list(e94.E94_NAMES) + list(e94.COMPARE))
    checks.update({
        "law: dips injected and removed": (inj > 0 and sum(x["samples_removed"] for x in e["reducer"]["dip_samples_removed"].values()) >= inj, inj),
        "law: every pass kept": (len(e["passes"]) == a.passes, e["passes"]),
        "law: 76 runs a pass, all kept": (e["runs"] == 76 * a.passes and e["kept"] == e["runs"], f"{e['kept']}/{e['runs']}"),
        "law: config gate accepts card 1's 65/65": (not e["passes_config_flags"], e["passes_config_flags"]),
        "law: D recovered within 0.2 W": (worst <= 0.2, round(worst, 4)),
        "law: every dumped tile passes the sha256 gate": (not any("tile dump" in " ".join(f[3]) for f in e["failed"]), len(e["failed"])),
        "law: experiment is E94": (e.get("experiment") == "E94", e.get("experiment")),
        "law: R4a PASS": (v(R, "E94-R4a") == "PASS", R["E94-R4a"]),
        "law: R6 PASS": (v(R, "E94-R6") == "PASS", R["E94-R6"].get("rms_w")),
        "law: R7 gate law PASS": (v(R, "E94-R7:gate_law") == "PASS", R["E94-R7:gate_law"].get("ratio")),
        "law: R8 not FAIL": (v(R, "E94-R8") != "FAIL", R["E94-R8"].get("rms_w")),
        "law: S1 PASS": (v(R, "E94-S1") == "PASS", v(R, "E94-S1")),
        "law: fp16.nn_like CORRECTION": (P["corrections"]["fp16.nn_like"]["verdict"] == "CORRECTION", P["corrections"]["fp16.nn_like"].get("offset_w")),
        "law: fp32.randn NO CORRECTION": (P["corrections"]["fp32.randn"]["verdict"] == "NO CORRECTION", P["corrections"]["fp32.randn"].get("offset_w")),
        "law: tile component tracks the frozen draws (fp16.nn_like)": (
            0.2 < P["rules_of_number"]["fp16.nn_like"]["spread"]["tau_w"] < 1.2, P["rules_of_number"]["fp16.nn_like"]["spread"]["tau_w"]),
    })
    for nn, scored in ((2, True), (1, False)):
        j = os.path.join(a.scratch, f"thin{nn}.json")
        run([os.path.join(HERE, "reduce_e94.py"), *dirs[:nn], "--out", j, "--leak", "0.15", "--no-refit"])
        s = os.path.join(a.scratch, f"thin{nn}-scored.json")
        run([os.path.join(HERE, "score_e94.py"), "--e94", j, "--json", s])
        t = json.load(open(s))["primary"]
        if scored:
            checks[f"{nn} kept passes are scored"] = (t["rules"]["E94-R4a"]["verdict"] != "NOT SCORED", t["tally"])
        else:
            checks[f"{nn} kept pass: NOT SCORED"] = (set(t["tally"]) == {"NOT SCORED"}, t["tally"])
    j = os.path.join(a.scratch, "gatesoff.json")
    run([os.path.join(HERE, "reduce_e94.py"), *dirs, "--gates-off", "--out", j, "--leak", "0.15", "--no-refit"])
    checks["the gates-off arm runs and says so"] = ("opened" in json.load(open(j))["reducer"]["pass_gates"], "ok")

    e, sc, D, inj, dirs, reg = run_world(a.scratch, "flat", a.passes, a.seed + 1)
    P = sc["primary"]
    R = P["rules"]
    checks["flat: R4a PASS"] = (v(R, "E94-R4a") == "PASS", R["E94-R4a"].get("tau_ci95_w"))
    for rid in ("E94-R3:fp32.sparse50", "E94-R3:fp16.nn_like", "E94-R3:fp32.nn_like", "E94-R6", "E94-R7:gate_law"):
        checks[f"flat: {rid} FAIL"] = (v(R, rid) == "FAIL", v(R, rid))
    checks["flat: no row needs a correction"] = (not any(x["verdict"] == "CORRECTION" for x in P["corrections"].values()), {c: x["verdict"] for c, x in P["corrections"].items()})

    e, sc, D, inj, dirs, reg = run_world(a.scratch, "wild", a.passes, a.seed + 2)
    P = sc["primary"]
    R = P["rules"]
    for rid in ("E94-R4a", "E94-R6", "E94-R8"):
        checks[f"wild: {rid} FAIL"] = (v(R, rid) == "FAIL", (v(R, rid), R[rid].get("rms_w"), R[rid].get("tau_ci95_w")))
    checks["wild: R7 gate law not PASS"] = (v(R, "E94-R7:gate_law") != "PASS", v(R, "E94-R7:gate_law"))

    e, sc, D, inj, dirs, reg = run_world(a.scratch, "off", a.passes, a.seed + 3)
    P = sc["primary"]
    R = P["rules"]
    checks["off: fp16.uniform01 outside its spread, R1 FAIL"] = (v(R, "E94-R1:fp16.uniform01") == "FAIL", P["rules_of_number"]["fp16.uniform01"]["offset_w"])
    checks["off: fp16.uniform01 CORRECTION"] = (P["corrections"]["fp16.uniform01"]["verdict"] == "CORRECTION", P["corrections"]["fp16.uniform01"]["verdict"])
    checks["off: int8.sparse50 CORRECTION"] = (P["corrections"]["int8.sparse50"]["verdict"] == "CORRECTION", P["corrections"]["int8.sparse50"]["verdict"])
    ok_all = True
    for k, (ok, val) in checks.items():
        ok_all &= bool(ok)
        print(f"{'ok  ' if ok else 'FAIL'} {k}: {val}")
    print(f"{sum(1 for x in checks.values() if x[0])} of {len(checks)} checks")
    sys.exit(0 if ok_all else 1)


if __name__ == "__main__":
    main()
