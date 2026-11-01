#!/usr/bin/env python3
# /// script
# requires-python = ">=3.9"
# dependencies = ["numpy"]
# ///
"""E106 self-test: E106's reduction and scoring run on SYNTHETIC card-1 passes and a synthetic read-back with known answers, before any E106 data.

    python3 tools/claims-v3/kinds/selftest_e106.py <scratch dir> [--passes 4] [--seed 106]

It writes fake passes with E78's own generator (selftest_e78.make_pass) after installing E106's items and order, with card 1's configuration reads and card 1's meter dips injected, and scores two worlds that must come out differently:
  (a) "half": every tile at values set so each held share is 0.50: R1 PASS, R2 PASS, R3, R4 and R5 ABOUT HALF, R6 ALIKE, S1 PASS;
  (b) "most": fp16's held tiles at 0.92 of the step, as E92's reading had it, and its step 5 W, fp32's held share 0.20 of its step: R3 LITTLE, R4 and R5 MOST, R6 DIFFER; a step 2 W off in fp32: R2 FAIL.
It also checks that one tile's words off reads R1 FAIL, one minion off reads UNREAD, two kept passes score and one does not. NOTHING HERE IS A MEASUREMENT; the output is never data. Exit 0 if every check holds.
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
import e106_common as e106  # noqa: E402

e106.install()
import e78_common as ec  # noqa: E402
import selftest_e78 as st  # noqa: E402

FIRST = 10610


def truth(world):
    reg = json.load(open(os.path.join(HERE, "predictions-e106.json")))
    nod = json.load(open(os.path.join(ROOT, "docs/reports/data/2026-10-31-e82-kinds-aifoundry1/posthoc/e82-nodips.json")))
    D = {n: v["D"]["mean"] for n, v in nod["items"].items() if v.get("D") and v["D"].get("mean") is not None}
    for n, t in reg["tiles"].items():
        D[n] = t["pred"]["M"]
    car = reg["rules"]["E106-R2"]["carried_w"]
    for t in ("fp32", "fp16"):
        D[f"{t}.signs"] = D[f"{t}.ones"] + car[t]
    if world == "half":
        D["fp32.s_abs"] = D["fp32.c_abs"] + 0.5 * car["fp32"]
        D["fp16.z_ss"] = D["fp16.c_abs"] + 0.5 * car["fp16"]
        D["fp16.x_s"] = D["fp16.x_c"] + 0.5 * car["fp16"]
    else:
        D["fp32.signs"] = D["fp32.ones"] + car["fp32"] + 2.0
        D["fp32.s_abs"] = D["fp32.c_abs"] + 0.2 * (car["fp32"] + 2.0)
        D["fp16.z_ss"] = D["fp16.c_abs"] + 0.92 * car["fp16"]
        D["fp16.x_s"] = D["fp16.x_c"] + 0.92 * car["fp16"]
    return D, reg


def inject_dips(d, rng, n_pairs=4):
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


def fake_readback(path, how="good"):
    spec = json.load(open(os.path.join(HERE, "e106", "e106.json")))
    with open(path, "w") as out:
        for tile, lens in spec["readback"].items():
            for n in lens:
                h = spec["tiles"][tile]["read"][str(n)]["rtl_hex"]
                g = {"a": {"minions": 1024, "first_minion": 0, "hex": h}}
                if how == "one_minion_off" and tile == "fp16.x_s":
                    g = {"a": {"minions": 1023, "first_minion": 0, "hex": h}, "b": {"minions": 1, "first_minion": 7, "hex": "00" * 1024}}
                if how == "words_off" and tile == "fp16.x_s" and n == 1000:
                    g = {"a": {"minions": 1024, "first_minion": 0, "hex": "00" * 1024}}
                out.write(json.dumps({"tile": tile, "n": n, "rc": 0, "sparsity": {"ok": True, "iters": n, "cycles_per_op": 546.0}, "distinct_c": len(g), "groups": g}) + "\n")


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
            json.dump({"tdp_w": 65, "temp_threshold_c": 65, "power_state": 1, "power_state_name": "managed_power", "minion_mhz": 600, "minion_mv": 499}, open(os.path.join(d, nm + ".json"), "w"))
        injected += inject_dips(d, rng)
        dirs.append(d)
    j = os.path.join(scratch, f"{world}.json")
    run([os.path.join(HERE, "reduce_e106.py"), *dirs, "--out", j, "--leak", "0.15", "--no-refit", "--txt", os.path.join(scratch, f"{world}.txt")])
    k = os.path.join(scratch, f"{world}-dipskept.json")
    run([os.path.join(HERE, "reduce_e106.py"), *dirs, "--keep-dips", "--out", k, "--leak", "0.15", "--no-refit"])
    rb = os.path.join(scratch, f"{world}-readback.jsonl")
    fake_readback(rb)
    s = os.path.join(scratch, f"{world}-scored.json")
    run([os.path.join(HERE, "score_e106.py"), "--e106", j, "--readback", rb, "--arm", f"dips_kept={k}", "--json", s, "--md", os.path.join(scratch, f"{world}-results.md")])
    return json.load(open(j)), json.load(open(s)), D, injected, dirs, reg


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("scratch")
    ap.add_argument("--passes", type=int, default=4)
    ap.add_argument("--seed", type=int, default=106)
    a = ap.parse_args()
    os.makedirs(a.scratch, exist_ok=True)
    checks = {}

    def v(R, rid):
        return R[rid]["verdict"]

    e, sc, D, inj, dirs, reg = run_world(a.scratch, "half", a.passes, a.seed)
    R = sc["primary"]["rules"]
    names = list(e106.E106_NAMES) + list(e106.COMPARE)
    worst = max(abs(e["items"][n]["D"]["mean"] - D[n]) for n in names)
    checks.update({
        "half: dips injected and removed": (inj > 0 and sum(x["samples_removed"] for x in e["reducer"]["dip_samples_removed"].values()) >= inj, inj),
        "half: every run kept": (e["runs"] == reg["plan"]["runs_per_pass"] * a.passes and e["kept"] == e["runs"], f"{e['kept']}/{e['runs']}"),
        "half: config gate accepts card 1's 65/65": (not e["passes_config_flags"], e["passes_config_flags"]),
        "half: D recovered within 0.3 W": (worst <= 0.3, round(worst, 4)),
        "half: experiment is E106": (e.get("experiment") == "E106", e.get("experiment")),
        "half: R1 PASS": (v(R, "E106-R1") == "PASS", R["E106-R1"]["verdict"]),
        "half: R2 PASS": (v(R, "E106-R2") == "PASS", R["E106-R2"]["cells"]),
        "half: R3 ABOUT HALF": (v(R, "E106-R3") == "ABOUT HALF", R["E106-R3"].get("share")),
        "half: R4 ABOUT HALF": (v(R, "E106-R4") == "ABOUT HALF", R["E106-R4"].get("share")),
        "half: R5 ABOUT HALF": (v(R, "E106-R5") == "ABOUT HALF", R["E106-R5"].get("share")),
        "half: R6 ALIKE": (v(R, "E106-R6") == "ALIKE", R["E106-R6"].get("difference")),
        "half: S1 PASS": (v(R, "E106-S1") == "PASS", R["E106-S1"]["cells"]),
    })
    for nn, scored in ((2, True), (1, False)):
        j = os.path.join(a.scratch, f"thin{nn}.json")
        run([os.path.join(HERE, "reduce_e106.py"), *dirs[:nn], "--out", j, "--leak", "0.15", "--no-refit"])
        s = os.path.join(a.scratch, f"thin{nn}-scored.json")
        run([os.path.join(HERE, "score_e106.py"), "--e106", j, "--json", s])
        t = json.load(open(s))["primary"]
        if scored:
            checks[f"{nn} kept passes are scored"] = (t["rules"]["E106-R4"]["verdict"] != "NOT SCORED", t["tally"])
        else:
            checks[f"{nn} kept pass: power rules NOT SCORED"] = (t["rules"]["E106-R4"]["verdict"] == "NOT SCORED", t["tally"])
    for how, want in (("one_minion_off", "UNREAD"), ("words_off", "FAIL")):
        rb = os.path.join(a.scratch, f"{how}-readback.jsonl")
        fake_readback(rb, how)
        s = os.path.join(a.scratch, f"{how}-scored.json")
        run([os.path.join(HERE, "score_e106.py"), "--e106", os.path.join(a.scratch, "half.json"), "--readback", rb, "--json", s])
        t = json.load(open(s))["primary"]["rules"]["E106-R1"]
        checks[f"{how}: R1 {want}"] = (t["verdict"] == want, t["verdict"])
    e, sc, D, inj, dirs, reg = run_world(a.scratch, "most", a.passes, a.seed + 1)
    R = sc["primary"]["rules"]
    checks["most: R2 FAIL"] = (v(R, "E106-R2") == "FAIL", R["E106-R2"]["cells"])
    checks["most: R3 LITTLE"] = (v(R, "E106-R3") == "LITTLE", R["E106-R3"].get("share"))
    checks["most: R4 MOST"] = (v(R, "E106-R4") == "MOST", R["E106-R4"].get("share"))
    checks["most: R5 MOST"] = (v(R, "E106-R5") == "MOST", R["E106-R5"].get("share"))
    checks["most: R6 DIFFER"] = (v(R, "E106-R6") == "DIFFER", R["E106-R6"].get("difference"))
    ok_all = True
    for k, (ok, val) in checks.items():
        ok_all &= bool(ok)
        print(f"{'ok  ' if ok else 'FAIL'} {k}: {str(val)[:160]}")
    print(f"{sum(1 for x in checks.values() if x[0])} of {len(checks)} checks; {len(names)} tiles")
    sys.exit(0 if ok_all else 1)


if __name__ == "__main__":
    main()
