#!/usr/bin/env python3
# /// script
# requires-python = ">=3.9"
# dependencies = ["numpy"]
# ///
"""E108 self-test: E108's reduction and scoring run on SYNTHETIC card-1 passes and a synthetic read-back with known answers, before any E108 data. A port of
tools/claims-v3/kinds/selftest_e106.py.

    python3 tools/claims-v3/signloc/selftest_e108.py <scratch dir> [--passes 4] [--seed 108]

It writes fake passes with E78's own generator (selftest_e78.make_pass) after installing E108's items and order, with card 1's configuration reads and card
1's meter dips injected, and scores two worlds that must come out differently:
  (a) "located": the steps at E106's values; every held share 0.40 in both formats (R3 ALIKE, R4 ALIKE); A's held cost = rho x B's (R5 PRICED ALIKE);
      A's signs add nothing to B's, held or walking (R6 NOTHING MEASURABLE twice); held accumulators that differ as s_walk's do carry 0.80 of the rest
      (R7 MOST), and so do held zero-product accumulators at b_B_w's sums of B's rest (R12 MOST); the ladder rises by 0.6 W a step (R8 RISES / RISES); the alternation walking at half its held price (R9 FALLS); fp16's walking premium
      1.552 x fp32's (R10 1.55x HOLDS); R1, R2, S1 PASS;
  (b) "other": fp16's zero-product share 0.20 above fp32's (R3 FP16 HIGHER); fp32's absorbed share 0.20 above its zero one (R4 ABSORBED HIGHER); A 1.5 W
      dearer than rho x B (R5 A DEARER); A's signs add 1.5 W held and walking (R6 ADDS / ADDS); the held accumulators carry 0.10 of the rest (R7 LITTLE, R12 LITTLE);
      the ladder flat (R8 ALIKE / ALIKE); the alternation's price the same walking (R9 HOLDS); fp16's walking premium equal to fp32's (R10 1.55x GOES);
      fp32's step 2 W off (R2 FAIL).
It also checks that one tile's words off reads R1 FAIL, one minion off reads UNREAD, two kept passes score and one does not. NOTHING HERE IS A MEASUREMENT;
the output is never data. Exit 0 if every check holds.
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
import e108_common as e108  # noqa: E402  (puts tools/claims-v3/kinds on sys.path)

e108.install()
import e78_common as ec  # noqa: E402
import selftest_e78 as st  # noqa: E402

FIRST = 10810
F, H = "fp32.", "fp16."


def truth(world):
    reg = json.load(open(os.path.join(HERE, "predictions-e108.json")))
    nod = json.load(open(os.path.join(ROOT, "docs/reports/data/2026-10-31-e82-kinds-aifoundry1/posthoc/e82-nodips.json")))
    D = {n: v["D"]["mean"] for n, v in nod["items"].items() if v.get("D") and v["D"].get("mean") is not None}
    for n, t in reg["tiles"].items():
        D[n] = t["pred"]["M"]
    step = dict(reg["rules"]["E108-R2"]["e106_w"])
    rho = reg["alternations_rho_A_over_B_held"]
    if world == "other":
        step["fp32"] += 2.0
    for t in ("fp32", "fp16"):
        D[t + ".signs"] = D[t + ".ones"] + step[t]
    good = world == "located"
    sz32, sz16 = 0.40, (0.40 if good else 0.60)
    D[F + "z_s"] = D[F + "c_abs"] + sz32 * step["fp32"]
    D[H + "z_s"] = D[H + "c_abs"] + sz16 * step["fp16"]
    D[H + "z_ss"] = D[H + "c_abs"] + 0.42 * step["fp16"]
    D[F + "b_B_f"] = D[F + "c_abs"] + 0.40 * step["fp32"]          # s_abs equals it in "located", so fp32's two held shares are equal there
    D[F + "b_A_f"] = D[F + "c_abs"] + rho * (D[F + "b_B_f"] - D[F + "c_abs"]) + (0.0 if good else 1.5)
    if good:
        D[F + "s_abs"] = D[F + "b_B_f"]
    else:
        D[F + "s_abs"] = D[F + "b_B_f"] + 1.5
    D[F + "b_B_w"] = D[F + "b_B_f"] + 2.4
    D[F + "b_B_z"] = D[F + "z_s"] + (0.80 if good else 0.10) * (D[F + "b_B_w"] - D[F + "z_s"])
    D[F + "b_A_w"] = D[F + "b_A_f"] + 1.2
    D[F + "s_walk"] = D[F + "b_B_w"] + (0.0 if good else 1.5)
    rest = D[F + "s_walk"] - D[F + "s_abs"]
    if good:
        D[F + "c_mx_f"] = D[F + "s_abs"] + 0.80 * rest
        D[F + "c_ex_f"] = D[F + "c_mx_f"] - 0.6
        D[F + "c_sg_f"] = D[F + "c_ex_f"] - 0.6
    else:
        D[F + "c_mx_f"] = D[F + "s_abs"] + 0.10 * rest
        D[F + "c_ex_f"] = D[F + "c_mx_f"]
        D[F + "c_sg_f"] = D[F + "c_mx_f"]
    D[F + "h_sub"] = D[F + "h_add"] + 4.0
    D[F + "m_h_sub"] = D[F + "w_h_add"] + (2.0 if good else 4.0)
    D[H + "m_h_sub"] = D[H + "w_h_add"] + (2.0 * 1.552 if good else 4.0)
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
    spec = json.load(open(os.path.join(HERE, "e108", "e108.json")))
    with open(path, "w") as out:
        for tile, lens in spec["readback"].items():
            for n in lens:
                h = spec["tiles"][tile]["read"][str(n)]["rtl_hex"]
                g = {"a": {"minions": 1024, "first_minion": 0, "hex": h}}
                if how == "one_minion_off" and tile == F + "c_mx_f":
                    g = {"a": {"minions": 1023, "first_minion": 0, "hex": h}, "b": {"minions": 1, "first_minion": 7, "hex": "00" * 1024}}
                if how == "words_off" and tile == F + "b_B_w" and n == 1000:
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
    base = os.path.join(scratch, world, "signloc")
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
    run([os.path.join(HERE, "reduce_e108.py"), *dirs, "--out", j, "--leak", "0.15", "--no-refit", "--txt", os.path.join(scratch, f"{world}.txt")])
    k = os.path.join(scratch, f"{world}-dipskept.json")
    run([os.path.join(HERE, "reduce_e108.py"), *dirs, "--keep-dips", "--out", k, "--leak", "0.15", "--no-refit"])
    rb = os.path.join(scratch, f"{world}-readback.jsonl")
    fake_readback(rb)
    s = os.path.join(scratch, f"{world}-scored.json")
    run([os.path.join(HERE, "score_e108.py"), "--e108", j, "--readback", rb, "--arm", f"dips_kept={k}", "--json", s, "--md", os.path.join(scratch, f"{world}-results.md")])
    return json.load(open(j)), json.load(open(s)), D, injected, dirs, reg


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("scratch")
    ap.add_argument("--passes", type=int, default=4)
    ap.add_argument("--seed", type=int, default=108)
    a = ap.parse_args()
    os.makedirs(a.scratch, exist_ok=True)
    checks = {}

    def v(R, rid):
        return R[rid]["verdict"]

    e, sc, D, inj, dirs, reg = run_world(a.scratch, "located", a.passes, a.seed)
    R = sc["primary"]["rules"]
    names = list(e108.E108_NAMES) + list(e108.COMPARE)
    worst = max(abs(e["items"][n]["D"]["mean"] - D[n]) for n in names)
    want = {"E108-R1": "PASS", "E108-R2": "PASS", "E108-R3": "ALIKE", "E108-R4": "ALIKE", "E108-R5": "PRICED ALIKE", "E108-R6": "NOTHING MEASURABLE / NOTHING MEASURABLE",
            "E108-R7": "MOST", "E108-R12": "MOST", "E108-R8": "RISES / RISES", "E108-R9": "FALLS", "E108-R10": "1.55x HOLDS", "E108-S1": "PASS"}
    checks.update({
        "located: dips injected and removed": (inj > 0 and sum(x["samples_removed"] for x in e["reducer"]["dip_samples_removed"].values()) >= inj, inj),
        "located: every run kept": (e["runs"] == reg["plan"]["runs_per_pass"] * a.passes and e["kept"] == e["runs"], f"{e['kept']}/{e['runs']}"),
        "located: config gate accepts card 1's 65/65": (not e["passes_config_flags"], e["passes_config_flags"]),
        "located: D recovered within 0.3 W": (worst <= 0.3, round(worst, 4)),
        "located: experiment is E108": (e.get("experiment") == "E108", e.get("experiment")),
    })
    for rid, w in want.items():
        checks[f"located: {rid} {w}"] = (v(R, rid) == w, R[rid].get("legs", R[rid].get("cells", R[rid]["verdict"])))
    for nn, scored in ((2, True), (1, False)):
        j = os.path.join(a.scratch, f"thin{nn}.json")
        run([os.path.join(HERE, "reduce_e108.py"), *dirs[:nn], "--out", j, "--leak", "0.15", "--no-refit"])
        s = os.path.join(a.scratch, f"thin{nn}-scored.json")
        run([os.path.join(HERE, "score_e108.py"), "--e108", j, "--json", s])
        t = json.load(open(s))["primary"]
        if scored:
            checks[f"{nn} kept passes are scored"] = (t["rules"]["E108-R7"]["verdict"] != "NOT SCORED", t["tally"])
        else:
            checks[f"{nn} kept pass: power rules NOT SCORED"] = (t["rules"]["E108-R7"]["verdict"] == "NOT SCORED", t["tally"])
    for how, w in (("one_minion_off", "UNREAD"), ("words_off", "FAIL")):
        rb = os.path.join(a.scratch, f"{how}-readback.jsonl")
        fake_readback(rb, how)
        s = os.path.join(a.scratch, f"{how}-scored.json")
        run([os.path.join(HERE, "score_e108.py"), "--e108", os.path.join(a.scratch, "located.json"), "--readback", rb, "--json", s])
        t = json.load(open(s))["primary"]["rules"]["E108-R1"]
        checks[f"{how}: R1 {w}"] = (t["verdict"] == w, t["verdict"])
    e, sc, D, inj, dirs, reg = run_world(a.scratch, "other", a.passes, a.seed + 1)
    R = sc["primary"]["rules"]
    want = {"E108-R2": "FAIL", "E108-R3": "FP16 HIGHER", "E108-R4": "ABSORBED HIGHER", "E108-R5": "A DEARER", "E108-R6": "ADDS / ADDS", "E108-R7": "LITTLE", "E108-R12": "LITTLE",
            "E108-R8": "ALIKE / ALIKE", "E108-R9": "HOLDS", "E108-R10": "1.55x GOES"}
    for rid, w in want.items():
        checks[f"other: {rid} {w}"] = (v(R, rid) == w, R[rid].get("legs", R[rid].get("cells", R[rid]["verdict"])))
    ok_all = True
    for k, (ok, val) in checks.items():
        ok_all &= bool(ok)
        print(f"{'ok  ' if ok else 'FAIL'} {k}: {str(val)[:200]}")
    print(f"{sum(1 for x in checks.values() if x[0])} of {len(checks)} checks; {len(names)} tiles")
    sys.exit(0 if ok_all else 1)


if __name__ == "__main__":
    main()
