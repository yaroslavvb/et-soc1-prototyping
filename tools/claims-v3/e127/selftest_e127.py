#!/usr/bin/env python3
# /// script
# requires-python = ">=3.9"
# dependencies = ["numpy"]
# ///
"""E127 self-test: E127's reduction and scoring run on SYNTHETIC aifoundry3 passes with known answers, before any E127 data.

    python3 tools/claims-v3/e127/selftest_e127.py <scratch dir> [--passes 4] [--seed 127]

It writes fake passes with E78's own generator (tools/claims-v3/kinds/selftest_e78.make_pass) after installing E127's items
and order, with E78's measured D for E78's kinds and the anchors (e78.json), reduces them as collect_e127.sh does (the
registered primary: dips removed, here at the generator's own leakage slope), scores them, and checks worlds that must come
out differently:
  "model":  every E127 tile at M5's frozen point: R1 FAIL (no miss to replicate), R2-R5 NOT SCORED;
  "gate":   E115's miss as a cost of the gate's dynamics alone: every tile whose lanes are held off all launch (q_steady,
            q_steady_hi, q_blk, g_blanes_steady, fp16 q_steady and g_blanes_steady) 0.74 W below M5, every tile whose lanes
            flip each cycle (q_alt, q_chk, g_blanes_alt, g_blanes_chk, fp16 q_alt, q_chk, g_blanes_alt) 0.48 W above:
            R1 PASS, R2 GATE, R3 GATE, R4 PER-LANE, R4q PER-LANE, R5 SHORT, R6 PASS;
  "data":   the same miss on the random tiles only, every quiet tile at M5: R1 PASS, R2 DATA, R3 DATA, R4 PER-LANE, R4q and
            R5 NOT SCORED;
  "alloff": the miss goes with all eight lanes off together: the tiles with all-off micro-ops (q_alt, q_blk, g_blanes_alt,
            fp16 q_alt and g_blanes_alt) 0.48 W above M5, the steady and checkerboard tiles 0.74 W below: R1 PASS, R2 GATE,
            R4 ALL-OFF, R4q ALL-OFF, R5 LONG;
  "dips":   the gate world with board-meter dips injected: the primary removes them, keeps every pass, R1 PASS, R2 GATE;
and checks that three kept passes score and two do not, and that the board-power stop in run_e127.py fires on a line at
65 W and passes one at 64.9 W. NOTHING HERE IS A MEASUREMENT; the output is never data. Exit 0 if every check holds.
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
import e127_common as e127  # noqa: E402

e127.install()
import e78_common as ec  # noqa: E402
import selftest_e78 as st  # noqa: E402  (tools/claims-v3/kinds is on the path through e127_common)

FIRST = 12710
HELD = {"fp32.q_steady", "fp32.q_steady_hi", "fp32.q_blk", "fp32.g_blanes_steady", "fp16.q_steady", "fp16.g_blanes_steady"}
FLIP = {"fp32.q_alt", "fp32.q_chk", "fp32.g_blanes_alt", "fp32.g_blanes_chk", "fp16.q_alt", "fp16.q_chk", "fp16.g_blanes_alt"}
ALLOFF = {"fp32.q_alt", "fp32.q_blk", "fp32.g_blanes_alt", "fp16.q_alt", "fp16.g_blanes_alt"}


def truth(world):
    reg = json.load(open(os.path.join(HERE, "predictions-e127.json")))
    e78 = json.load(open(os.path.join(ROOT, "docs/reports/data/2026-10-31-e78-kinds-energy-matrix/e78.json")))
    D = {n: v["D"]["mean"] for n, v in e78["items"].items() if v.get("D") and v["D"].get("mean") is not None}
    for z in ec.ZERO.values():
        D[z] = 0.0
    for n, t in reg["tiles"].items():
        d = t["M5"]["D_w"]
        quiet = t["family"] == "quiet"
        if world in ("gate", "dips") or (world == "data" and not quiet):
            d += -0.74 if n in HELD else (0.48 if n in FLIP else 0.0)
        elif world == "alloff":
            d += 0.48 if n in ALLOFF else -0.74
        D[n] = max(0.02, d)
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
    R = os.path.join(HERE, "reduce_e127.py")
    j = os.path.join(scratch, f"{world}.json")
    run([R, *dirs, "--drop-dips", "--out", j, "--leak", "0.15", "--no-refit", "--txt", os.path.join(scratch, f"{world}.txt")])
    s = os.path.join(scratch, f"{world}-scored.json")
    run([os.path.join(HERE, "score_e127.py"), "--e127", j, "--json", s, "--md", os.path.join(scratch, f"{world}-results.md")])
    return {"e": json.load(open(j)), "sc": json.load(open(s)), "D": D, "injected": injected, "dirs": dirs, "reg": reg}


def power_stop_checks():
    """run_e127.guard_board_power on a fake run_e78 module and a fake telemetry file: 64.9 W passes, 65.0 W stops."""
    import run_e127
    out = {}
    with tempfile.TemporaryDirectory() as td:
        tel = os.path.join(td, "tel.jsonl")
        for w, want_stop in ((64.9, False), (65.0, True)):
            open(tel, "w").write(json.dumps({"t_ms": 1, "board_w": w}) + "\n")
            fake = types.SimpleNamespace(EXIT_HOT=6, last_sample=lambda p: json.loads(open(p).read().splitlines()[-1]))
            g = run_e127.guard_board_power(fake, 65.0, out_dir=td)
            stopped, code = False, None
            try:
                g(tel)
            except SystemExit as e:
                stopped, code = True, e.code
            out[w] = (stopped == want_stop and (code == 6 if want_stop else True)
                      and (os.path.exists(os.path.join(td, "STOP")) == want_stop), code)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("scratch")
    ap.add_argument("--passes", type=int, default=4)
    ap.add_argument("--seed", type=int, default=127)
    a = ap.parse_args()
    os.makedirs(a.scratch, exist_ok=True)
    checks = {}

    def v(R, rid):
        return R[rid]["verdict"]

    w = run_world(a.scratch, "model", a.passes, a.seed)
    e, R = w["e"], w["sc"]["primary"]["rules"]
    worst = max(abs(e["items"][n]["D"]["mean"] - w["D"][n]) for n in e127.E127_NAMES if (e["items"].get(n) or {}).get("D", {}).get("mean") is not None)
    q5m = w["reg"]["contrasts"]["Q5: fp32.q_steady_hi - fp32.q_steady"]["M5"]["D_w"]
    checks.update({
        "model: every pass kept": (len(e["passes"]) == a.passes, e["passes"]),
        "model: every run kept": (e["runs"] == w["reg"]["plan"]["runs_per_pass"] * a.passes and e["kept"] == e["runs"], f"{e['kept']}/{e['runs']}"),
        "model: D recovered within 0.3 W": (worst <= 0.3, round(worst, 4)),
        "model: experiment is E127": (e.get("experiment") == "E127", e.get("experiment")),
        "model: R1 FAIL (no miss to replicate)": (v(R, "E127-R1") == "FAIL", R["E127-R1"].get("measured_w")),
        "model: R2 NOT SCORED": (v(R, "E127-R2") == "NOT SCORED", v(R, "E127-R2")),
        "model: R4 NOT SCORED": (v(R, "E127-R4") == "NOT SCORED", v(R, "E127-R4")),
        "model: R6 as M5's lane-position point says": (v(R, "E127-R6") == ("PASS" if abs(q5m) < 0.15 else v(R, "E127-R6")), (v(R, "E127-R6"), round(q5m, 3))),
        "model: S1 PASS": (v(R, "E127-S1") == "PASS", {c: round(x["D"], 3) for c, x in R["E127-S1"]["cells"].items()}),
    })
    model_dirs = w["dirs"]
    r6_want = "PASS" if abs(q5m) < 0.15 else None   # a lane-position point M5 itself puts near the line is not checked
    for world, want in (("gate", {"E127-R1": "PASS", "E127-R2": "GATE", "E127-R3": "GATE", "E127-R4": "PER-LANE",
                                  "E127-R4q": "PER-LANE", "E127-R5": "SHORT", **({"E127-R6": r6_want} if r6_want else {})}),
                        ("data", {"E127-R1": "PASS", "E127-R2": "DATA", "E127-R3": "DATA", "E127-R4": "PER-LANE",
                                  "E127-R4q": "NOT SCORED", "E127-R5": "NOT SCORED"}),
                        ("alloff", {"E127-R1": "PASS", "E127-R2": "GATE", "E127-R4": "ALL-OFF", "E127-R4q": "ALL-OFF",
                                    "E127-R5": "LONG"})):
        w = run_world(a.scratch, world, a.passes, a.seed + len(world))
        R = w["sc"]["primary"]["rules"]
        for rid, want_v in want.items():
            checks[f"{world}: {rid} {want_v}"] = (v(R, rid) == want_v, (v(R, rid), R[rid].get("excess_w"), R[rid].get("line_w")))
    w = run_world(a.scratch, "dips", a.passes, a.seed + 9, dips=True)
    R = w["sc"]["primary"]["rules"]
    removed = sum(x["samples_removed"] for x in w["e"]["reducer"]["dip_samples_removed"].values())
    checks.update({
        "dips: injected, and the primary removes them": (w["injected"] > 0 and removed >= w["injected"], (w["injected"], removed)),
        "dips: the primary keeps every pass": (len(w["e"]["passes"]) == a.passes, w["e"]["passes"]),
        "dips: R1 PASS, R2 GATE": (v(R, "E127-R1") == "PASS" and v(R, "E127-R2") == "GATE", (v(R, "E127-R1"), v(R, "E127-R2"))),
    })
    for nn, scored in ((3, True), (2, False)):
        j = os.path.join(a.scratch, f"thin{nn}.json")
        run([os.path.join(HERE, "reduce_e127.py"), *model_dirs[:nn], "--drop-dips", "--out", j, "--leak", "0.15", "--no-refit"])
        s = os.path.join(a.scratch, f"thin{nn}-scored.json")
        run([os.path.join(HERE, "score_e127.py"), "--e127", j, "--json", s])
        t = json.load(open(s))["primary"]
        if scored:
            checks[f"{nn} kept passes are scored"] = (t["rules"]["E127-R1"]["verdict"] != "NOT SCORED", t["tally"])
        else:
            checks[f"{nn} kept passes: NOT SCORED"] = (set(t["tally"]) == {"NOT SCORED"}, t["tally"])
    for wv, (ok, code) in power_stop_checks().items():
        checks[f"board-power stop at {wv} W: {'stops (exit 6, STOP written)' if wv >= 65 else 'passes'}"] = (ok, code)
    ok_all = True
    for k, (ok, val) in checks.items():
        ok_all &= bool(ok)
        print(f"{'ok  ' if ok else 'FAIL'} {k}: {val}")
    print(f"{sum(1 for x in checks.values() if x[0])} of {len(checks)} checks; {len(e127.E127_NAMES)} tiles")
    sys.exit(0 if ok_all else 1)


if __name__ == "__main__":
    main()
