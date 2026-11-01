#!/usr/bin/env python3
# /// script
# requires-python = ">=3.9"
# dependencies = ["numpy"]
# ///
"""E115 self-test: E115's reduction and scoring run on SYNTHETIC aifoundry3 passes with known answers, before any E115 data.

    python3 tools/claims-v3/e115/selftest_e115.py <scratch dir> [--passes 3] [--seed 115]

It writes fake passes with E78's own generator (tools/claims-v3/kinds/selftest_e78.make_pass) after installing E115's items
and order, with E78's measured D for E78's kinds and the anchors (e78.json), and scores worlds
that must come out differently:
  (a) "model": every pool tile at M5's frozen a3 point: R1, R2, R3, R4 PASS, every contrast INSIDE, S1 PASS, R5 not
      M4 BETTER;
  (a') "dips": the same world with meter dips injected (pairs of board samples 8-14 W low inside runs): the primary may
      set passes aside, as E86, E92 and E95 did on this card; the dips arm removes every injected sample, keeps every
      pass and scores R1 PASS; the gates-off arm keeps every pass;
  (b) "m4":    every tile at M4's frozen point: R5 not M5 BETTER;
  (c) "off":   the open cases broken - the plus tiles of the sign contrasts (s_bridge, s_drift12, s_wpair0) and the
      exponent-spread tiles with a random word gate (fp32 and fp16 x_logu_s50) 0.9 W above M5, m_bpair_eq 1.2 W above
      (so the memory-path contrast reads BELOW), the int8 tiles 0.9 W below: R1 FAIL, R2 FAIL, R3 FAIL, R4 FAIL, the
      memory pair BELOW. (A first draft moved both tiles of every sign contrast together, which a contrast cancels by
      design: R4 then read PASS, 6 of 7, correctly; the world was changed, not the rule.)
and checks that two kept passes score and one does not. NOTHING HERE IS A MEASUREMENT; the output is never data. Exit 0
if every check holds.
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
import e115_common as e115  # noqa: E402

e115.install()
import e78_common as ec  # noqa: E402
import selftest_e78 as st  # noqa: E402  (tools/claims-v3/kinds is on the path through e115_common)

FIRST = 11510


def truth(world):
    reg = json.load(open(os.path.join(HERE, "predictions-e115.json")))
    e78 = json.load(open(os.path.join(ROOT, "docs/reports/data/2026-10-31-e78-kinds-energy-matrix/e78.json")))
    D = {n: v["D"]["mean"] for n, v in e78["items"].items() if v.get("D") and v["D"].get("mean") is not None}
    for z in ec.ZERO.values():
        D[z] = 0.0
    for n, t in reg["tiles"].items():
        D[n] = t["M4"]["D_w"] if world == "m4" else t["M5"]["D_w"]
        if world == "off":
            if n in ("fp32.s_bridge", "fp32.s_drift12", "fp16.s_wpair0", "fp32.x_logu_s50", "fp16.x_logu_s50"):
                D[n] += 0.9
            elif n == "fp32.m_bpair_eq":
                D[n] += 1.2
            elif t["type"] == "int8":
                D[n] = max(0.05, D[n] - 0.9)
    return D, reg


def inject_dips(d, rng, n_pairs=3):
    """Pairs of board_w samples 8-14 W low inside run windows of random runs (the meter artifact E82 A2 removes)."""
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


def run_world(scratch, world, passes, seed, dips=False, arms=False):
    rng = np.random.default_rng(seed)
    items = ec.load_items()
    D, reg = truth(world)
    base = os.path.join(scratch, world, "kinds")
    if os.path.isdir(base):
        shutil.rmtree(base)
    dirs, injected = [], 0
    for i in range(passes):
        p = FIRST + i
        d = os.path.join(base, f"p{p}")
        os.makedirs(d)
        st.make_pass(d, p, D, rng, items)
        if dips:
            injected += inject_dips(d, rng)
        dirs.append(d)
    R = os.path.join(HERE, "reduce_e115.py")
    j = os.path.join(scratch, f"{world}.json")
    run([R, *dirs, "--out", j, "--leak", "0.15", "--no-refit", "--txt", os.path.join(scratch, f"{world}.txt")])
    armv = []
    if arms:
        k = os.path.join(scratch, f"{world}-nodips.json")
        run([R, *dirs, "--drop-dips", "--out", k, "--leak", "0.15", "--no-refit"])
        g = os.path.join(scratch, f"{world}-gatesoff.json")
        run([R, *dirs, "--gates-off", "--out", g, "--leak", "0.15", "--no-refit"])
        armv = ["--arm", f"dips_removed={k}", "--arm", f"gates_off={g}"]
    s = os.path.join(scratch, f"{world}-scored.json")
    run([os.path.join(HERE, "score_e115.py"), "--e115", j, *armv, "--json", s, "--md", os.path.join(scratch, f"{world}-results.md")])
    out = {"e": json.load(open(j)), "sc": json.load(open(s)), "D": D, "injected": injected, "dirs": dirs, "reg": reg}
    if arms:
        out["nodips"] = json.load(open(os.path.join(scratch, f"{world}-nodips.json")))
        out["gatesoff"] = json.load(open(os.path.join(scratch, f"{world}-gatesoff.json")))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("scratch")
    ap.add_argument("--passes", type=int, default=3)
    ap.add_argument("--seed", type=int, default=115)
    a = ap.parse_args()
    os.makedirs(a.scratch, exist_ok=True)
    checks = {}

    def v(R, rid):
        return R[rid]["verdict"]

    w = run_world(a.scratch, "model", a.passes, a.seed)
    e, R = w["e"], w["sc"]["primary"]["rules"]
    worst = max(abs(e["items"][n]["D"]["mean"] - w["D"][n]) for n in e115.E115_NAMES if e["items"].get(n, {}).get("D", {}).get("mean") is not None) \
        if e.get("items") else 99.0
    c4 = R["E115-R4"].get("contrasts", {})
    checks.update({
        "model: every pass kept": (len(e["passes"]) == a.passes, e["passes"]),
        "model: every run kept": (e["runs"] == w["reg"]["plan"]["runs_per_pass"] * a.passes and e["kept"] == e["runs"], f"{e['kept']}/{e['runs']}"),
        "model: D recovered within 0.3 W": (worst <= 0.3, round(worst, 4)),
        "model: experiment is E115": (e.get("experiment") == "E115", e.get("experiment")),
        "model: R1 PASS": (v(R, "E115-R1") == "PASS", (R["E115-R1"].get("rms_w"), R["E115-R1"].get("interval", {}).get("hi95"))),
        "model: R2 PASS": (v(R, "E115-R2") == "PASS", R["E115-R2"].get("rms_w")),
        "model: R3 PASS": (v(R, "E115-R3") == "PASS", R["E115-R3"].get("fraction")),
        "model: R4 PASS, every contrast inside": (v(R, "E115-R4") == "PASS" and all(x["verdict"] == "INSIDE" for x in c4.values()), R["E115-R4"].get("fraction")),
        "model: R5 not M4 BETTER": (v(R, "E115-R5") != "M4 BETTER", R["E115-R5"].get("gap_w")),
        "model: S1 PASS": (v(R, "E115-S1") == "PASS", {c: round(x["D"], 3) for c, x in R["E115-S1"]["cells"].items()}),
        "model: the anchor footing scores": (w["sc"]["anchor_footing"]["rules"]["E115-R1"]["verdict"] in ("PASS", "FAIL"), w["sc"]["anchor_footing"]["rules"]["E115-R1"].get("rms_w")),
        "model: F0r reported": ("per_format_term" in w["sc"]["primary"].get("reported", {}), w["sc"]["primary"].get("reported", {}).get("per_format_term", {}).get("gap_w")),
    })
    model_dirs = w["dirs"]
    w = run_world(a.scratch, "dips", a.passes, a.seed + 3, dips=True, arms=True)
    Rd = w["sc"]["arms"]["dips_removed"]["rules"]
    checks.update({
        "dips: injected, and the dips arm removes them": (w["injected"] > 0 and sum(x["samples_removed"] for x in w["nodips"]["reducer"]["dip_samples_removed"].values()) >= w["injected"], w["injected"]),
        "dips: the dips arm keeps every pass": (len(w["nodips"]["passes"]) == a.passes, w["nodips"]["passes"]),
        "dips: the dips arm scores R1 PASS": (Rd["E115-R1"]["verdict"] == "PASS", Rd["E115-R1"].get("rms_w")),
        "dips: the gates-off arm keeps every pass": (len(w["gatesoff"]["passes"]) == a.passes, w["gatesoff"]["passes"]),
        "dips: the primary's set-aside passes are reported (not a check of the model)": (True, [x["pass"] for x in w["e"].get("passes_set_aside", [])]),
    })
    for nn, scored in ((2, True), (1, False)):
        j = os.path.join(a.scratch, f"thin{nn}.json")
        run([os.path.join(HERE, "reduce_e115.py"), *model_dirs[:nn], "--out", j, "--leak", "0.15", "--no-refit"])
        s = os.path.join(a.scratch, f"thin{nn}-scored.json")
        run([os.path.join(HERE, "score_e115.py"), "--e115", j, "--json", s])
        t = json.load(open(s))["primary"]
        if scored:
            checks[f"{nn} kept passes are scored"] = (t["rules"]["E115-R1"]["verdict"] != "NOT SCORED", t["tally"])
        else:
            checks[f"{nn} kept pass: NOT SCORED"] = (set(t["tally"]) == {"NOT SCORED"}, t["tally"])
    w = run_world(a.scratch, "m4", a.passes, a.seed + 1)
    R = w["sc"]["primary"]["rules"]
    checks["m4: R5 not M5 BETTER"] = (v(R, "E115-R5") != "M5 BETTER", (v(R, "E115-R5"), R["E115-R5"].get("gap_w")))
    w = run_world(a.scratch, "off", a.passes, a.seed + 2)
    R = w["sc"]["primary"]["rules"]
    mem = R["E115-R4"].get("contrasts", {}).get("fp32.m_blines_eq - fp32.m_bpair_eq", {"verdict": "missing", "measured_w": float("nan")})
    checks.update({
        "off: R1 FAIL": (v(R, "E115-R1") == "FAIL", (R["E115-R1"].get("rms_w"), R["E115-R1"].get("interval", {}).get("hi95"))),
        "off: R2 FAIL": (v(R, "E115-R2") == "FAIL", R["E115-R2"].get("rms_w")),
        "off: R3 FAIL": (v(R, "E115-R3") == "FAIL", R["E115-R3"].get("fraction")),
        "off: R4 FAIL": (v(R, "E115-R4") == "FAIL", R["E115-R4"].get("fraction")),
        "off: the memory pair reads BELOW": (mem["verdict"] == "BELOW", (round(mem["measured_w"], 3), mem.get("reading"))),
    })
    ok_all = True
    for k, (ok, val) in checks.items():
        ok_all &= bool(ok)
        print(f"{'ok  ' if ok else 'FAIL'} {k}: {val}")
    print(f"{sum(1 for x in checks.values() if x[0])} of {len(checks)} checks; {len(e115.E115_NAMES)} tiles")
    sys.exit(0 if ok_all else 1)


if __name__ == "__main__":
    main()
