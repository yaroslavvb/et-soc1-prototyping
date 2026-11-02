#!/usr/bin/env python3
# /// script
# requires-python = ">=3.9"
# dependencies = ["numpy"]
# ///
"""E128 self-test: E128's reduction and scoring run on SYNTHETIC card-1 passes and a synthetic read-back with known answers, before any E128 data, and
the device-command guard run against a stub. A port of tools/claims-v3/signloc/selftest_e108.py.

    python3 tools/claims-v3/e128/selftest_e128.py <scratch dir> [--passes 5] [--seed 128]

It writes fake passes with E78's own generator (selftest_e78.make_pass) after installing E128's items and order, with card 1's configuration reads and card
1's meter dips injected, and scores two worlds that must come out differently:
  (a) "located": the steps at E108's values; every held share 0.40; in fp32 and fp16 the accumulators differing carry 0.97 of B's rest in the matched
      triple and in E108's design (R3 MOST, R6 MOST, R7 MOST, R8 MOST), the sums changing 0.03 (R4, R9 ALMOST NONE), the designs alike (R5 ALIKE), the
      formats alike (R12 ALIKE); fp16's walking premium 1.552 x fp32's (R10 1.55x HOLDS; the pooled ratio P 1.55x HOLDS); R1, R2, S1 PASS;
  (b) "other": fp32's step 2 W off (R2 FAIL); in fp32 the matched held tile carries 0.20 of B's rest (R3 LITTLE) and the walk 0.80 (R4 SOME), E108's
      design 0.97 (R5 MATCHED LOWER); fp16's port 0.20 (R7 LITTLE), its matched held tile 0.50 (R8 ABOUT HALF) and walk 0.50 (R9 SOME); fp16's matched
      share 0.30 above fp32's (R12 FP16 HIGHER); fp16's walking premium equal to fp32's (R10 1.55x GOES); some cross-session rule FAILs.
It also checks that one tile's words off reads R1 FAIL, one minion off reads UNREAD, two kept passes score and one does not, and that ettelem_guard.sh
passes `config` and `sample --seconds --every-ms` and refuses `sample --reset-ms`, `loglevel`, `sptrace`, `temp` and extra words (exit 97), with the
reader replaced by a stub that only prints its arguments. NOTHING HERE IS A MEASUREMENT; the output is never data. Exit 0 if every check holds.
SPDX-License-Identifier: Apache-2.0
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
import e128_common as e128  # noqa: E402  (puts tools/claims-v3/kinds on sys.path)

e128.install()
import e78_common as ec  # noqa: E402
import selftest_e78 as st  # noqa: E402

FIRST = 12810
F, H = "fp32.", "fp16."


def truth(world):
    reg = json.load(open(os.path.join(HERE, "predictions-e128.json")))
    nod = json.load(open(os.path.join(ROOT, "docs/reports/data/2026-10-31-e82-kinds-aifoundry1/posthoc/e82-nodips.json")))
    D = {n: v["D"]["mean"] for n, v in nod["items"].items() if v.get("D") and v["D"].get("mean") is not None}
    for n, t in reg["tiles"].items():
        D[n] = t["pred"]["M"]
    step = dict(reg["rules"]["E128-R2"]["e108_w"])
    good = world == "located"
    if not good:
        step["fp32"] += 2.0
    for t in ("fp32", "fp16"):
        D[t + ".signs"] = D[t + ".ones"] + step[t]
        D[t + ".z_s"] = D[t + ".c_abs"] + 0.40 * step[t]
    rest = 3.0
    shares = {"fp32": {"z": 0.97, "m": 0.97 if good else 0.20}, "fp16": {"z": 0.97 if good else 0.20, "m": 0.97 if good else 0.50}}
    for t in ("fp32", "fp16"):
        p = t + "."
        D[p + "b_B_w"] = D[p + "z_s"] + rest
        D[p + "b_B_z"] = D[p + "z_s"] + shares[t]["z"] * rest
        D[p + "b_B_wm"] = D[p + "z_s"] + rest
        D[p + "b_B_zm"] = D[p + "z_s"] + shares[t]["m"] * rest
    D[F + "m_h_sub"] = D[F + "w_h_add"] + 2.0
    D[H + "m_h_sub"] = D[H + "w_h_add"] + (2.0 * 1.552 if good else 2.0)
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
    spec = json.load(open(os.path.join(HERE, "e128", "e128.json")))
    with open(path, "w") as out:
        for tile, lens in spec["readback"].items():
            for n in lens:
                h = spec["tiles"][tile]["read"][str(n)]["rtl_hex"]
                g = {"a": {"minions": 1024, "first_minion": 0, "hex": h}}
                if how == "one_minion_off" and tile == H + "b_B_wm":
                    g = {"a": {"minions": 1023, "first_minion": 0, "hex": h}, "b": {"minions": 1, "first_minion": 7, "hex": "00" * 1024}}
                if how == "words_off" and tile == F + "b_B_zm" and n == 1000:
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
    base = os.path.join(scratch, world, "e128")
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
    run([os.path.join(HERE, "reduce_e128.py"), *dirs, "--out", j, "--leak", "0.15", "--no-refit", "--txt", os.path.join(scratch, f"{world}.txt")])
    k = os.path.join(scratch, f"{world}-dipskept.json")
    run([os.path.join(HERE, "reduce_e128.py"), *dirs, "--keep-dips", "--out", k, "--leak", "0.15", "--no-refit"])
    rb = os.path.join(scratch, f"{world}-readback.jsonl")
    fake_readback(rb)
    s = os.path.join(scratch, f"{world}-scored.json")
    run([os.path.join(HERE, "score_e128.py"), "--e128", j, "--readback", rb, "--arm", f"dips_kept={k}", "--json", s, "--md", os.path.join(scratch, f"{world}-results.md")])
    return json.load(open(j)), json.load(open(s)), D, injected, dirs, reg


def guard_checks(scratch):
    """ettelem_guard.sh with its reader replaced by a stub that prints its arguments: what it passes, what it refuses (exit 97)."""
    g = os.path.join(scratch, "guard")
    os.makedirs(os.path.join(g, "build", "ettelem"), exist_ok=True)
    stub = os.path.join(g, "build", "ettelem", "ettelem")
    open(stub, "w").write("#!/bin/sh\necho \"STUB $*\"\n")
    os.chmod(stub, 0o755)
    src = open(os.path.join(HERE, "ettelem_guard.sh")).read()
    assert src.count("REAL=build/ettelem/ettelem") == 1
    gp = os.path.join(g, "ettelem_guard.sh")
    open(gp, "w").write(src)
    out = {}
    cases = [("config", 0, "STUB config"), ("sample --seconds 1 --every-ms 500", 0, "STUB sample --seconds 1 --every-ms 500"),
             ("sample --seconds 1800 --every-ms 100", 0, "STUB sample --seconds 1800 --every-ms 100"),
             ("sample --seconds 10 --every-ms 100 --reset-ms 1000", 97, ""), ("sample --reset-ms 1000", 97, ""), ("loglevel debug", 97, ""),
             ("loglevel info", 97, ""), ("sptrace x.bin", 97, ""), ("temp", 97, ""), ("temp --if-free", 97, ""), ("config extra", 97, ""), ("", 97, ""),
             ("sample --seconds", 97, ""), ("sample --seconds 1;reboot", 97, "")]
    for args, want_rc, want_out in cases:
        r = subprocess.run(["bash", gp] + args.split(), cwd=g, capture_output=True, text=True)
        ok = r.returncode == want_rc and (r.stdout.strip() == want_out if want_rc == 0 else "STUB" not in r.stdout)
        out[f"guard: '{args}' -> rc {want_rc}"] = (ok, f"rc {r.returncode} out {r.stdout.strip()[:60]!r}")
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("scratch")
    ap.add_argument("--passes", type=int, default=5)
    ap.add_argument("--seed", type=int, default=128)
    a = ap.parse_args()
    os.makedirs(a.scratch, exist_ok=True)
    checks = {}

    def v(R, rid):
        return R[rid]["verdict"]

    checks.update(guard_checks(a.scratch))
    e, sc, D, inj, dirs, reg = run_world(a.scratch, "located", a.passes, a.seed)
    R = sc["primary"]["rules"]
    names = list(e128.E128_NAMES) + list(e128.COMPARE)
    worst = max(abs(e["items"][n]["D"]["mean"] - D[n]) for n in names)
    want = {"E128-R1": "PASS", "E128-R2": "PASS", "E128-R3": "MOST", "E128-R4": "ALMOST NONE", "E128-R5": "ALIKE", "E128-R6": "MOST", "E128-R7": "MOST",
            "E128-R8": "MOST", "E128-R9": "ALMOST NONE", "E128-R10": "1.55x HOLDS", "E128-R12": "ALIKE", "E128-S1": "PASS", "E128-P": "1.55x HOLDS"}
    checks.update({
        "located: dips injected and removed": (inj > 0 and sum(x["samples_removed"] for x in e["reducer"]["dip_samples_removed"].values()) >= inj, inj),
        "located: every run kept": (e["runs"] == reg["plan"]["runs_per_pass"] * a.passes and e["kept"] == e["runs"], f"{e['kept']}/{e['runs']}"),
        "located: config gate accepts card 1's 65/65": (not e["passes_config_flags"], e["passes_config_flags"]),
        "located: D recovered within 0.3 W": (worst <= 0.3, round(worst, 4)),
        "located: experiment is E128": (e.get("experiment") == "E128", e.get("experiment")),
        "located: every X rule scored": (len(R["E128-X"]["rules"]) == len(reg["cross_session"]["rules"]) and all(x["verdict"] != "UNRESOLVED" for x in R["E128-X"]["rules"].values()), R["E128-X"]["tally"]),
        "located: no X rule FAILs": (R["E128-X"]["tally"].get("FAIL", 0) == 0, R["E128-X"]["tally"]),
        "located: R11 scores every tile, the new ones beside": (R["E128-R11"].get("n") == len(reg["tiles"]) and R["E128-R11"].get("new_n") == 6, {k: R["E128-R11"].get(k) for k in ("n", "new_n", "verdict")}),
    })
    for rid, w in want.items():
        checks[f"located: {rid} {w}"] = (v(R, rid) == w, R[rid].get("legs", R[rid].get("cells", R[rid]["verdict"])) if rid != "E128-P" else {k: R[rid][k] for k in ("mean", "ci95", "n")})
    for nn, scored in ((2, True), (1, False)):
        j = os.path.join(a.scratch, f"thin{nn}.json")
        run([os.path.join(HERE, "reduce_e128.py"), *dirs[:nn], "--out", j, "--leak", "0.15", "--no-refit"])
        s = os.path.join(a.scratch, f"thin{nn}-scored.json")
        run([os.path.join(HERE, "score_e128.py"), "--e128", j, "--json", s])
        t = json.load(open(s))["primary"]
        if scored:
            checks[f"{nn} kept passes are scored"] = (t["rules"]["E128-R3"]["verdict"] != "NOT SCORED" and t["rules"]["E128-X"]["verdict"] != "NOT SCORED", t["tally"])
        else:
            checks[f"{nn} kept pass: power, cross and pooled rules NOT SCORED"] = (all(t["rules"][r]["verdict"] == "NOT SCORED" for r in ("E128-R3", "E128-X", "E128-P")), t["tally"])
    for how, w in (("one_minion_off", "UNREAD"), ("words_off", "FAIL")):
        rb = os.path.join(a.scratch, f"{how}-readback.jsonl")
        fake_readback(rb, how)
        s = os.path.join(a.scratch, f"{how}-scored.json")
        run([os.path.join(HERE, "score_e128.py"), "--e128", os.path.join(a.scratch, "located.json"), "--readback", rb, "--json", s])
        t = json.load(open(s))["primary"]["rules"]["E128-R1"]
        checks[f"{how}: R1 {w}"] = (t["verdict"] == w, t["verdict"])
    e, sc, D, inj, dirs, reg = run_world(a.scratch, "other", a.passes, a.seed + 1)
    R = sc["primary"]["rules"]
    want = {"E128-R2": "FAIL", "E128-R3": "LITTLE", "E128-R4": "SOME", "E128-R5": "MATCHED LOWER", "E128-R7": "LITTLE", "E128-R8": "ABOUT HALF", "E128-R9": "SOME",
            "E128-R10": "1.55x GOES", "E128-R12": "FP16 HIGHER"}
    for rid, w in want.items():
        checks[f"other: {rid} {w}"] = (v(R, rid) == w, R[rid].get("legs", R[rid].get("cells", R[rid]["verdict"])))
    checks["other: some X rule FAILs"] = (R["E128-X"]["tally"].get("FAIL", 0) >= 1, R["E128-X"]["tally"])
    checks["other: the pooled ratio does not HOLD"] = (R["E128-P"]["verdict"] != "1.55x HOLDS", {k: R["E128-P"][k] for k in ("verdict", "mean", "ci95", "n")})
    ok_all = True
    for k, (ok, val) in checks.items():
        ok_all &= bool(ok)
        print(f"{'ok  ' if ok else 'FAIL'} {k}: {str(val)[:200]}")
    print(f"{sum(1 for x in checks.values() if x[0])} of {len(checks)} checks; {len(names)} tiles")
    sys.exit(0 if ok_all else 1)


if __name__ == "__main__":
    main()
