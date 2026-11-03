#!/usr/bin/env python3
# /// script
# requires-python = ">=3.9"
# dependencies = ["numpy"]
# ///
"""E152 self-test: E152's reduction and scoring run on SYNTHETIC aifoundry3 passes with known answers, before any E152 data.

    python3 tools/claims-v3/e152/selftest_e152.py <scratch dir> [--passes 6] [--seed 152]

It writes fake passes with E78's own generator (tools/claims-v3/kinds/selftest_e78.make_pass) after installing E152's items
and order, with E78's measured D for E78's kinds and the anchors (e78.json), reduces them as collect_e152.sh does (the
registered primary: dips removed, here at the generator's own leakage slope), scores them, and checks worlds that must come
out differently. Every ladder tile's D is a base (E127's q_steady plus half its Q5) plus a gate cost g(n):
  "linear":    g = p* x the flips above gd0 (E127's frozen price): R1 LINEAR, R2 CARRIES;
  "shared":    35% of C8* spent whenever any lane flips, the rest per flip: R1 NONLINEAR (concave);
  "convex":    g = C8* x (n / 8)^2: R1 NONLINEAR (convex);
  "half":      g = p*/2 x the flips: R1 LINEAR, R2 MISSES;
  "null":      no gate cost: R1 NOT SCORED (no top to the ladder), R2 MISSES;
  "dips":      the linear world with board-meter dips injected: the primary removes them, keeps every pass, R1 LINEAR;
and checks that three kept passes score and two do not, that the board-power stop in run_e152.py fires on a line at 65 W and
passes one at 64.9 W, and that run_e152.py refuses a stop-test line at or above 30 W. NOTHING HERE IS A MEASUREMENT; the
output is never data. Exit 0 if every check holds.
SPDX-License-Identifier: Apache-2.0
"""
import argparse
import gzip
import json
import os
import shutil
import subprocess
import sys
import tempfile
import types

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, HERE)
import e152_common as e152  # noqa: E402

e152.install()
import e78_common as ec  # noqa: E402
import selftest_e78 as st  # noqa: E402  (tools/claims-v3/kinds is on the path through e152_common)

FIRST = 15210


def truth(world):
    reg = json.load(open(os.path.join(HERE, "predictions-e152.json")))
    e78 = json.load(open(os.path.join(ROOT, "docs/reports/data/2026-10-31-e78-kinds-energy-matrix/e78.json")))
    D = {n: v["D"]["mean"] for n, v in e78["items"].items() if v.get("D") and v["D"].get("mean") is not None}
    for z in ec.ZERO.values():
        D[z] = 0.0
    RATE = reg["plan"]["rate_ops_per_s"]
    p = reg["price"]["p_fJ"] * 1e-15 * RATE           # W per (flip an op)
    C8s = reg["predictions"]["C8_star_w"]
    br = reg["predictions"]["bridge"]["E127_measured_D_w"]
    base = br["fp32.q_steady"] + reg["predictions"]["gd0_minus_q_steady_w"]
    for n, t in reg["tiles"].items():
        f = t["flips_above_gd0"] if t["family"] == "ladder" else None
        if t["family"] == "bridge":
            D[n] = br[n]
            continue
        k = t["lanes_switching"]
        if world in ("linear", "dips"):
            g = p * f
        elif world == "shared":
            g = (0.35 * C8s if k > 0 else 0.0) + 0.65 * p * f
        elif world == "convex":
            g = C8s * (k / 8.0) ** 2
        elif world == "half":
            g = 0.5 * p * f
        elif world == "null":
            g = 0.0
        else:
            raise SystemExit(world)
        D[n] = base + g
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


def run_world(scratch, world, passes, seed, dips=False):
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
    R = os.path.join(HERE, "reduce_e152.py")
    j = os.path.join(scratch, f"{world}.json")
    run([R, *dirs, "--drop-dips", "--out", j, "--leak", "0.15", "--no-refit", "--txt", os.path.join(scratch, f"{world}.txt")])
    s = os.path.join(scratch, f"{world}-scored.json")
    run([os.path.join(HERE, "score_e152.py"), "--e152", j, "--json", s, "--md", os.path.join(scratch, f"{world}-results.md")])
    return {"e": json.load(open(j)), "sc": json.load(open(s)), "D": D, "injected": injected, "dirs": dirs, "reg": reg}


def power_stop_checks():
    """run_e152.guard_board_power on a fake run_e78 module and a fake telemetry file: 64.9 W passes, 65.0 W stops."""
    import run_e152
    out = {}
    with tempfile.TemporaryDirectory() as td:
        tel = os.path.join(td, "tel.jsonl")
        for w, want_stop in ((64.9, False), (65.0, True)):
            open(tel, "w").write(json.dumps({"t_ms": 1, "board_w": w}) + "\n")
            fake = types.SimpleNamespace(EXIT_HOT=6, last_sample=lambda p: json.loads(open(p).read().splitlines()[-1]))
            g = run_e152.guard_board_power(fake, 65.0, out_dir=td)
            stopped, code = False, None
            try:
                g(tel)
            except SystemExit as e:
                stopped, code = True, e.code
            out[w] = (stopped == want_stop and (code == 6 if want_stop else True)
                      and (os.path.exists(os.path.join(td, "STOP")) == want_stop), code)
    return out


def stoptest_line_refused():
    """run_e152.py with E152_STOPTEST=board and a 30 W line must refuse (exit 2) before it touches anything."""
    env = dict(os.environ, E152_STOPTEST="board", E152_STOPTEST_W="30")
    with tempfile.TemporaryDirectory() as td:
        r = subprocess.run([sys.executable, os.path.join(HERE, "run_e152.py"), td, "--list"], capture_output=True, text=True,
                           env=env)
    return r.returncode == 2 and "below 30 W" in r.stderr, (r.returncode, r.stderr.strip()[-120:])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("scratch")
    ap.add_argument("--passes", type=int, default=6)
    ap.add_argument("--seed", type=int, default=152)
    a = ap.parse_args()
    os.makedirs(a.scratch, exist_ok=True)
    checks = {}

    def v(R, rid):
        return R[rid]["verdict"]

    w = run_world(a.scratch, "linear", a.passes, a.seed)
    e, R = w["e"], w["sc"]["primary"]["rules"]
    worst = max(abs(e["items"][n]["D"]["mean"] - w["D"][n]) for n in e152.E152_NAMES
                if (e["items"].get(n) or {}).get("D", {}).get("mean") is not None)
    checks.update({
        "linear: every pass kept": (len(e["passes"]) == a.passes, e["passes"]),
        "linear: every run kept": (e["runs"] == w["reg"]["plan"]["runs_per_pass"] * a.passes and e["kept"] == e["runs"],
                                   f"{e['kept']}/{e['runs']}"),
        "linear: D recovered within 0.3 W": (worst <= 0.3, round(worst, 4)),
        "linear: experiment is E152": (e.get("experiment") == "E152", e.get("experiment")),
        "linear: R1 LINEAR": (v(R, "E152-R1") == "LINEAR", (v(R, "E152-R1"), R["E152-R1"].get("worst_abs_plus_h_w"))),
        "linear: R2 CARRIES": (v(R, "E152-R2") == "CARRIES", (v(R, "E152-R2"), R["E152-R2"].get("price_fJ"), R["E152-R2"].get("ci95_fJ"))),
        "linear: S1 PASS": (v(R, "E152-S1") == "PASS", {c: round(x["D"], 3) for c, x in R["E152-S1"]["cells"].items()}),
        "linear: S2 PASS": (v(R, "E152-S2") == "PASS", R["E152-S2"]["Q2_w"].get("mean")),
    })
    lin_dirs = w["dirs"]
    for world, want in (("shared", {"E152-R1": "NONLINEAR"}), ("convex", {"E152-R1": "NONLINEAR"}),
                        ("half", {"E152-R1": "LINEAR", "E152-R2": "MISSES"}),
                        ("null", {"E152-R1": "NOT SCORED", "E152-R2": "MISSES"})):
        w = run_world(a.scratch, world, a.passes, a.seed + len(world))
        R = w["sc"]["primary"]["rules"]
        for rid, want_v in want.items():
            checks[f"{world}: {rid} {want_v}"] = (v(R, rid) == want_v, (v(R, rid), R[rid].get("worst_abs_minus_h_w"),
                                                                        R[rid].get("price_fJ")))
        if world == "shared":
            checks["shared: concave"] = ("concave" in (R["E152-R1"].get("shape") or ""), R["E152-R1"].get("shape"))
        if world == "convex":
            checks["convex: convex"] = ("convex" in (R["E152-R1"].get("shape") or ""), R["E152-R1"].get("shape"))
    w = run_world(a.scratch, "dips", a.passes, a.seed + 9, dips=True)
    R = w["sc"]["primary"]["rules"]
    removed = sum(x["samples_removed"] for x in w["e"]["reducer"]["dip_samples_removed"].values())
    checks.update({
        "dips: injected, and the primary removes them": (w["injected"] > 0 and removed >= w["injected"], (w["injected"], removed)),
        "dips: the primary keeps every pass": (len(w["e"]["passes"]) == a.passes, w["e"]["passes"]),
        "dips: R1 LINEAR": (v(R, "E152-R1") == "LINEAR", v(R, "E152-R1")),
    })
    for nn, scored in ((3, True), (2, False)):
        j = os.path.join(a.scratch, f"thin{nn}.json")
        run([os.path.join(HERE, "reduce_e152.py"), *lin_dirs[:nn], "--drop-dips", "--out", j, "--leak", "0.15", "--no-refit"])
        s = os.path.join(a.scratch, f"thin{nn}-scored.json")
        run([os.path.join(HERE, "score_e152.py"), "--e152", j, "--json", s])
        t = json.load(open(s))["primary"]
        if scored:
            checks[f"{nn} kept passes are scored"] = (t["rules"]["E152-R2"]["verdict"] != "NOT SCORED", t["tally"])
        else:
            checks[f"{nn} kept passes: NOT SCORED"] = (set(t["tally"]) == {"NOT SCORED"}, t["tally"])
    for wv, (ok, code) in power_stop_checks().items():
        checks[f"board-power stop at {wv} W: {'stops (exit 6, STOP written)' if wv >= 65 else 'passes'}"] = (ok, code)
    checks["a stop-test line of 30 W is refused"] = stoptest_line_refused()
    ok_all = True
    for k, (ok, val) in checks.items():
        ok_all &= bool(ok)
        print(f"{'ok  ' if ok else 'FAIL'} {k}: {val}")
    print(f"{sum(1 for x in checks.values() if x[0])} of {len(checks)} checks; {len(e152.E152_NAMES)} tiles")
    sys.exit(0 if ok_all else 1)


if __name__ == "__main__":
    main()
