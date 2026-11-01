#!/usr/bin/env python3
# /// script
# requires-python = ">=3.9"
# dependencies = ["numpy"]
# ///
"""E104 self-test: E104's reduction and scoring run on SYNTHETIC card-1 passes and a synthetic read-back with known answers, before any E104 data.

    python3 tools/claims-v3/kinds/selftest_e104.py <scratch dir> [--passes 3] [--seed 104]

It writes fake passes with E78's own generator (selftest_e78.make_pass) after installing E104's items and order, with card 1's configuration reads and card 1's meter dips injected, and scores two worlds that must come out differently:
  (a) "fault":  every tile at M4's frozen point, the read-back equal to accum.c's sums: R1 RTL, R2 PASS, R3 RTL, R4 RESULT-PATH, R7 PASS, S1 PASS, R8 PASS;
  (b) "frozen": fp16's u, h and m premiums at E92's reading (1.55x fp32's in both regimes, u_sub at 14/15 of h_sub), the read-back equal to fl(n S): R1 FROZEN, R4 FROZEN-READING, R5 and R6 1.55x HOLDS;
and checks that two kept passes score and one does not, that a read-back with one minion off reads UNREAD, not a verdict, that the manual's read-back reads MANUAL, and that a broken control leaves R1 unscored. NOTHING HERE IS A MEASUREMENT; the output is never data. Exit 0 if every check holds.
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
import e104_common as e104  # noqa: E402

e104.install()
import e78_common as ec  # noqa: E402
import selftest_e78 as st  # noqa: E402

FIRST = 10410


def truth(world):
    reg = json.load(open(os.path.join(HERE, "predictions-e104.json")))
    nod = json.load(open(os.path.join(ROOT, "docs/reports/data/2026-10-31-e82-kinds-aifoundry1/posthoc/e82-nodips.json")))
    D = {n: v["D"]["mean"] for n, v in nod["items"].items() if v.get("D") and v["D"].get("mean") is not None}
    for n, t in reg["tiles"].items():
        D[n] = t["pred"]["M"]
    if world == "frozen":
        # E92's reading: the fp16 premium is 1.55x fp32's whatever the sum does, and u_sub is h_sub at 14/15 of the alternations
        p32h = D["fp32.h_sub"] - D["fp32.h_add"]
        D["fp32.u_sub"] = D["fp32.h_add"] + 14 / 15 * p32h
        D["fp16.h_sub"] = D["fp16.h_add"] + 1.552 * p32h
        D["fp16.u_sub"] = D["fp16.h_add"] + 14 / 15 * 1.552 * p32h
        p32m = D["fp32.m_h_sub"] - D["fp32.w_h_add"]
        D["fp16.m_h_sub"] = D["fp16.w_h_add"] + 1.552 * p32m
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


def fake_readback(path, world, one_minion_off=False):
    spec = json.load(open(os.path.join(HERE, "e104", "e104.json")))
    with open(path, "w") as out:
        for tile, lens in spec["readback"].items():
            for n in lens:
                e = spec["tiles"][tile]["read"][str(n)]
                h = e[{"fault": "rtl_hex", "frozen": "fl_hex", "manual": "manual_hex"}[world]]
                g = {"a": {"minions": 1024, "first_minion": 0, "hex": h}}
                if one_minion_off and tile == "fp16.h_sub":
                    g = {"a": {"minions": 1023, "first_minion": 0, "hex": h}, "b": {"minions": 1, "first_minion": 7, "hex": "00" * 1024}}
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
    run([os.path.join(HERE, "reduce_e104.py"), *dirs, "--out", j, "--leak", "0.15", "--no-refit", "--txt", os.path.join(scratch, f"{world}.txt")])
    k = os.path.join(scratch, f"{world}-dipskept.json")
    run([os.path.join(HERE, "reduce_e104.py"), *dirs, "--keep-dips", "--out", k, "--leak", "0.15", "--no-refit"])
    rb = os.path.join(scratch, f"{world}-readback.jsonl")
    fake_readback(rb, world)
    s = os.path.join(scratch, f"{world}-scored.json")
    run([os.path.join(HERE, "score_e104.py"), "--e104", j, "--readback", rb, "--arm", f"dips_kept={k}", "--json", s, "--md", os.path.join(scratch, f"{world}-results.md")])
    return json.load(open(j)), json.load(open(s)), D, injected, dirs, reg


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("scratch")
    ap.add_argument("--passes", type=int, default=3)
    ap.add_argument("--seed", type=int, default=104)
    a = ap.parse_args()
    os.makedirs(a.scratch, exist_ok=True)
    checks = {}

    def v(R, rid):
        return R[rid]["verdict"]

    e, sc, D, inj, dirs, reg = run_world(a.scratch, "fault", a.passes, a.seed)
    R = sc["primary"]["rules"]
    worst = max(abs(e["items"][n]["D"]["mean"] - D[n]) for n in e104.E104_NAMES)
    checks.update({
        "fault: dips injected and removed": (inj > 0 and sum(x["samples_removed"] for x in e["reducer"]["dip_samples_removed"].values()) >= inj, inj),
        "fault: every pass kept": (len(e["passes"]) == a.passes, e["passes"]),
        "fault: every run kept": (e["runs"] == reg["plan"]["runs_per_pass"] * a.passes and e["kept"] == e["runs"], f"{e['kept']}/{e['runs']}"),
        "fault: config gate accepts card 1's 65/65": (not e["passes_config_flags"], e["passes_config_flags"]),
        "fault: D recovered within 0.3 W": (worst <= 0.3, round(worst, 4)),
        "fault: experiment is E104": (e.get("experiment") == "E104", e.get("experiment")),
        "fault: R1 RTL": (v(R, "E104-R1") == "RTL", R["E104-R1"]["verdict"]),
        "fault: R2 PASS": (v(R, "E104-R2") == "PASS", R["E104-R2"]["verdict"]),
        "fault: R3 RTL": (v(R, "E104-R3") == "RTL", R["E104-R3"]["verdict"]),
        "fault: R4 RESULT-PATH": (v(R, "E104-R4") == "RESULT-PATH", R["E104-R4"].get("mean_w")),
        "fault: R7 PASS": (v(R, "E104-R7") == "PASS", R["E104-R7"].get("rms_w")),
        "fault: R8 PASS": (v(R, "E104-R8") == "PASS", R["E104-R8"].get("mean_w")),
        "fault: S1 PASS": (v(R, "E104-S1") == "PASS", R["E104-S1"]["cells"]),
    })
    for nn, scored in ((2, True), (1, False)):
        j = os.path.join(a.scratch, f"thin{nn}.json")
        run([os.path.join(HERE, "reduce_e104.py"), *dirs[:nn], "--out", j, "--leak", "0.15", "--no-refit"])
        s = os.path.join(a.scratch, f"thin{nn}-scored.json")
        run([os.path.join(HERE, "score_e104.py"), "--e104", j, "--json", s])
        t = json.load(open(s))["primary"]
        if scored:
            checks[f"{nn} kept passes are scored"] = (t["rules"]["E104-R4"]["verdict"] != "NOT SCORED", t["tally"])
        else:
            checks[f"{nn} kept pass: power rules NOT SCORED"] = (t["rules"]["E104-R4"]["verdict"] == "NOT SCORED", t["tally"])
    rb = os.path.join(a.scratch, "off-readback.jsonl")
    fake_readback(rb, "fault", one_minion_off=True)
    s = os.path.join(a.scratch, "off-scored.json")
    run([os.path.join(HERE, "score_e104.py"), "--e104", os.path.join(a.scratch, "fault.json"), "--readback", rb, "--json", s])
    t = json.load(open(s))["primary"]["rules"]["E104-R1"]
    checks["one minion off: R1 is not a verdict"] = (t["verdict"] == "UNREAD", t)
    rb = os.path.join(a.scratch, "manual-readback.jsonl")
    fake_readback(rb, "manual")
    s = os.path.join(a.scratch, "manual-scored.json")
    run([os.path.join(HERE, "score_e104.py"), "--e104", os.path.join(a.scratch, "fault.json"), "--readback", rb, "--json", s])
    t = json.load(open(s))["primary"]["rules"]
    checks["manual's read-back: R1 MANUAL"] = (t["E104-R1"]["verdict"] == "MANUAL", t["E104-R1"]["verdict"])
    rb2 = os.path.join(a.scratch, "broken-readback.jsonl")
    lines = [json.loads(x) for x in open(rb)]
    for r in lines:
        if r["tile"] == "fp16.c_abs":
            r["groups"]["a"]["hex"] = "00" * 1024
    open(rb2, "w").write("\n".join(json.dumps(x) for x in lines) + "\n")
    s = os.path.join(a.scratch, "broken-scored.json")
    run([os.path.join(HERE, "score_e104.py"), "--e104", os.path.join(a.scratch, "fault.json"), "--readback", rb2, "--json", s])
    t = json.load(open(s))["primary"]["rules"]
    checks["a broken control: R1 NOT SCORED, R2 FAIL"] = (t["E104-R1"]["verdict"] == "NOT SCORED" and t["E104-R2"]["verdict"] == "FAIL", (t["E104-R1"]["verdict"], t["E104-R2"]["verdict"]))
    e, sc, D, inj, dirs, reg = run_world(a.scratch, "frozen", a.passes, a.seed + 1)
    R = sc["primary"]["rules"]
    checks["frozen: R1 FROZEN"] = (v(R, "E104-R1") == "FROZEN", R["E104-R1"]["verdict"])
    checks["frozen: R4 FROZEN-READING"] = (v(R, "E104-R4") == "FROZEN-READING", R["E104-R4"].get("mean_w"))
    checks["frozen: R5 1.55x HOLDS"] = (v(R, "E104-R5") == "1.55x HOLDS", R["E104-R5"].get("ratio"))
    checks["frozen: R6 1.55x HOLDS"] = (v(R, "E104-R6") == "1.55x HOLDS", R["E104-R6"].get("ratio"))
    ok_all = True
    for k, (ok, val) in checks.items():
        ok_all &= bool(ok)
        print(f"{'ok  ' if ok else 'FAIL'} {k}: {str(val)[:160]}")
    print(f"{sum(1 for x in checks.values() if x[0])} of {len(checks)} checks; {len(e104.E104_NAMES)} tiles")
    sys.exit(0 if ok_all else 1)


if __name__ == "__main__":
    main()
