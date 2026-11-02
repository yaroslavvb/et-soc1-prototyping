#!/usr/bin/env python3
"""E129 (Q136): the desk self-test, run before the freeze (its output is selftest.txt beside this file). Committed data only; nothing touches a card.

    uv run --quiet tools/claims-v3/e129/selftest_e129.py [--full]         (--full adds C, the reducer on E124's raw passes: about a minute; numpy)

A  score_e129.py's formulas (E109's, copied) on E124's committed reduction reproduce score_e109.py's committed per-pass G, G_lane, G_op, G_rest, U and
   e_op (E124 scored.json) and E124's N (extras.json) to 1e-9, and score_e129.score() gives E124's registered R0-R3, Y1 and Y2 verdicts at its 4 passes
   (with R1 NOT-SCORED there: E129's R1 needs six).
B  The pass order: 14 runs in every pass 12910-12919, pi first and last, each of the six arms exactly once, each format's zeros once in each segment;
   deterministic; and the smoke items exist.
C  (--full) The reducer port: E124's four raw passes, cut to the runs of items E129 knows (scratch copies under build/e129-selftest/), reduced by
   E124's reduce_e124.py and by E129's reduce_e129.py: every shared item's D, S and rate agree to 1e-9; then cut again to E129's own pass (no random or
   fp16 anchors): the arms' D, S and rate are unchanged to 1e-9, and every pass is kept.
D  The set-aside rule (score_e129.choose) and the six-pass minimum on synthetic reductions.
E  V1's and V2's verdicts on synthetic reductions (N1 low, N1 near N, N1 near N/2).
F  check_e129.py --desk (HARNESS OK) and preflight_e129.sh (GO).
SPDX-License-Identifier: Apache-2.0
"""
import copy
import gzip
import json
import os
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(ROOT, "tools/claims-v3/kinds"))
import score_e129 as sc  # noqa: E402

E124D = os.path.join(ROOT, "docs/reports/data/2026-11-01-e124-int8-zeros-replicate")
P = json.load(open(os.path.join(HERE, "predictions-e129.json")))
OUT = []


def say(s=""):
    OUT.append(s)
    print(s)


def close(a, b, tol=1e-9):
    return a is not None and b is not None and abs(a - b) <= tol * max(1.0, abs(a), abs(b))


def test_a():
    d = json.load(open(os.path.join(E124D, "e124.json")))
    ref = json.load(open(os.path.join(E124D, "scored.json")))
    ex = json.load(open(os.path.join(E124D, "extras.json")))
    st = sc.per_pass_stats(d)
    bad, n = [], 0
    for p, s in st.items():
        r = ref["per_pass"][p]
        for k in ("G", "G_lane", "G_op", "G_rest"):
            n += 1
            if not close(s["gap"][k], r["gap"][k]):
                bad.append(f"{p} {k} {s['gap'][k]} != {r['gap'][k]}")
        for f in ("fp32", "int8"):
            for k in ("U", "e_op_pj", "O"):
                n += 1
                if not close(s[f][k], r[f][k]):
                    bad.append(f"{p} {f} {k}")
    nref = ex["added_rules"]["Y1"]["N"]["per_pass"]
    mine = [st[str(p)]["one_row"]["N"] for p in d["passes"]]
    for a, b in zip(mine, nref):
        n += 1
        if not close(a, b):
            bad.append(f"N {a} != {b}")
    out = sc.score(d, P)
    R = out["rules"]
    want = {"R0_answer": ref["rules"]["R0_answer"]["verdict"], "R2_lanes": ref["rules"]["R2_lanes"]["verdict"],
            "R3_per_time": ref["rules"]["R3_per_time"]["verdict"], "Y1_no_issue": ex["added_rules"]["Y1"]["verdict"],
            "Y2_per_op_ceiling": ex["added_rules"]["Y2"]["verdict"]}
    got = {k: R[k]["verdict"] for k in want}
    vb = [k for k in want if got[k] != want[k]]
    r1 = R["R1_ops"]["verdict"]
    ok = not bad and not vb and r1.startswith("NOT-SCORED") and close(R["R1_ops"]["G_op"]["half"], ref["rules"]["R1_ops"]["G_op"]["half"])
    say(f"A  formulas on E124's committed reduction: {n} per-pass values compared, {len(bad)} differ; verdicts {got} against E124's {want}; "
        f"R1 at 4 passes reads '{r1}' (E124's own R1: {ref['rules']['R1_ops']['verdict']}, half {ref['rules']['R1_ops']['G_op']['half']:.4f} W, "
        f"here {R['R1_ops']['G_op']['half']:.4f}): {'PASS' if ok else 'FAIL'}")
    for b in bad[:10]:
        say("   " + b)
    return ok


def test_b():
    import e129_common as e
    items = e.load_items()
    by = {it["name"]: it for it in items}
    bad = []
    orders = {}
    for p in e.PASSES:
        o = e.pass_order(items, "aifoundry1-c1", p)
        orders[p] = [r["item"] for r in o]
        names = [r["item"] for r in o]
        if len(o) != 14 or names[0] != "anchor_pi" or names[-1] != "anchor_pi":
            bad.append(f"{p}: {len(o)} runs, ends {names[0]}, {names[-1]}")
        for it in e.e129_pool():
            if names.count(it) != 1:
                bad.append(f"{p}: {it} x{names.count(it)}")
        for s in range(3):
            seg = [r["item"] for r in o if r["segment"] == s]
            for z in e.ANCHORS:
                if seg.count(z) != 1:
                    bad.append(f"{p} seg {s}: {z} x{seg.count(z)}")
        if e.pass_order(items, "aifoundry1-c1", p) != o:
            bad.append(f"{p}: not deterministic")
    distinct = len({tuple(v) for v in orders.values()})
    miss = [n for n in e.SMOKE_ITEMS if n not in by]
    vals = {n: by[n]["values"] for n in e.e129_pool()}
    want_vals = {"m0r1.fp32.zeros": "shape=1x16m0:file:tools/claims-v3/kinds/tiles/fp32/zeros.bin",
                 "m0.int8.zeros": "shape=16x16m0:file:tools/claims-v3/kinds/tiles/int8/zeros.bin",
                 "m0k8.fp32.zeros": "shape=16x8m0:file:tools/claims-v3/kinds/tiles/fp32/zeros.bin"}
    vbad = [k for k, v in want_vals.items() if vals[k] != v]
    ok = not bad and not miss and not vbad and distinct == len(orders)
    say(f"B  pass order: {len(orders)} passes x 14 runs, every arm once, each format's zeros once a segment, pi first and last, deterministic, "
        f"{distinct} distinct orders; smoke items {len(e.SMOKE_ITEMS)} known; --values strings as E109's grammar: {'PASS' if ok else 'FAIL'} {bad[:5]} {miss} {vbad}")
    return ok


def cut(src, dst, keep):
    """Copy a pass directory, keeping only the run marks and run records of items in `keep` (heater and burn-in marks stay)."""
    os.makedirs(dst, exist_ok=True)
    for f in os.listdir(src):
        s = os.path.join(src, f)
        if f in ("marks.jsonl", "runs.jsonl"):
            rows = [json.loads(x) for x in open(s) if x.strip()]
            rows = [r for r in rows if not (r.get("kind", "run") == "run" and r.get("item") not in keep)] if f == "marks.jsonl" else \
                   [r for r in rows if r.get("item") in keep]
            open(os.path.join(dst, f), "w").write("".join(json.dumps(r) + "\n" for r in rows))
        elif os.path.isdir(s):
            shutil.copytree(s, os.path.join(dst, f), dirs_exist_ok=True)
        else:
            shutil.copy2(s, os.path.join(dst, f))


def test_c():
    import e129_common as e
    scratch = os.path.join(ROOT, "build", "e129-selftest")
    if os.path.isdir(scratch):
        shutil.rmtree(scratch)
    raw = os.path.join(E124D, "aifoundry1-c1", "e124")
    passes = sorted(x for x in os.listdir(raw) if x.startswith("p124"))
    known = {it["name"] for it in e.load_items()}
    own = set(e.e129_pool()) | set(e.ANCHORS) | {"anchor_pi"}
    d1, d2 = [], []
    for p in passes:
        cut(os.path.join(raw, p), os.path.join(scratch, "known", p), known)
        cut(os.path.join(raw, p), os.path.join(scratch, "own", p), own)
        d1.append(os.path.join(scratch, "known", p))
        d2.append(os.path.join(scratch, "own", p))
    uv = ["uv", "run", "--quiet"]
    r124 = subprocess.run(uv + [os.path.join(ROOT, "tools/claims-v3/e124/reduce_e124.py")] + d1 + ["--leak", "0.2414", "--no-refit", "--out",
                          os.path.join(scratch, "r124.json")], capture_output=True, text=True, cwd=ROOT)
    r129 = subprocess.run(uv + [os.path.join(HERE, "reduce_e129.py")] + d1 + ["--leak", "0.2414", "--no-refit", "--out",
                          os.path.join(scratch, "r129.json")], capture_output=True, text=True, cwd=ROOT)
    r129o = subprocess.run(uv + [os.path.join(HERE, "reduce_e129.py")] + d2 + ["--leak", "0.2414", "--no-refit", "--out",
                           os.path.join(scratch, "r129own.json")], capture_output=True, text=True, cwd=ROOT)
    if r124.returncode or r129.returncode or r129o.returncode:
        say(f"C  reducer port: a reduction failed: {r124.returncode} {r124.stderr[-300:]} | {r129.returncode} {r129.stderr[-300:]} | "
            f"{r129o.returncode} {r129o.stderr[-300:]}: FAIL")
        return False
    a = json.load(open(os.path.join(scratch, "r124.json")))
    b = json.load(open(os.path.join(scratch, "r129.json")))
    c = json.load(open(os.path.join(scratch, "r129own.json")))
    bad, n, bad2, n2 = [], 0, [], 0
    for p in a["per_pass"]:
        for it, va in a["per_pass"][p].items():
            vb = b["per_pass"].get(p, {}).get(it)
            if vb is None:
                bad.append(f"{p} {it} missing in E129's")
                continue
            for k in ("D", "S", "rate"):
                n += 1
                if not (va.get(k) is None and vb.get(k) is None) and not close(va.get(k), vb.get(k)):
                    bad.append(f"{p} {it} {k} {va.get(k)} != {vb.get(k)}")
            if it in own:
                vc = c["per_pass"].get(p, {}).get(it)
                for k in ("D", "S", "rate"):
                    n2 += 1
                    if vc is None or not close(va.get(k), vc.get(k)):
                        bad2.append(f"{p} {it} {k} {va.get(k)} != {None if vc is None else vc.get(k)}")
    kept = (a["passes"], b["passes"], c["passes"])
    ok = not bad and not bad2 and kept[0] == kept[1] == kept[2] and len(kept[0]) == 4
    say(f"C  reducer port on E124's raw passes cut to E129's known items: {n} values of {len(a['per_pass'])} passes compared, {len(bad)} differ "
        f"(reduce_e124 vs reduce_e129); cut to E129's own pass (no random or fp16 anchors): {n2} values, {len(bad2)} differ; passes kept "
        f"{[len(k) for k in kept]}: {'PASS' if ok else 'FAIL'}")
    for x in (bad + bad2)[:10]:
        say("   " + x)
    return ok


def synth(n, N_pp, N1_pp, G=0.55, gop=0.05, gop_sd=0.1, cycles=(62.0, 62.0)):
    """A reduce_e129-shaped dict with n passes: per-pass S and D chosen to give these N, N1, G and G_op."""
    per = {}
    for i in range(n):
        p = str(12910 + i)
        j = (i % 3) - 1
        e_f = 80e-12 + 0.0 * j
        g_op_i = gop + gop_sd * j
        e_i = (g_op_i + e_f * 1.12e9) / 1.92e9
        per[p] = {"fp32.zeros": {"S": 1.66, "D": 0.0, "rate": 1.12e9}, "int8.zeros": {"S": 1.66 + G, "D": 0.0, "rate": 1.92e9},
                  "m0.fp32.zeros": {"S": 0.20, "D": -1.46, "rate": 1.12e9}, "m0.int8.zeros": {"S": 0.20 + N_pp[i], "D": -0.40, "rate": 1.92e9},
                  "m0k8.fp32.zeros": {"S": 0.27, "D": -1.46 + e_f * 1.06e9, "rate": 2.18e9},
                  "m0k8.int8.zeros": {"S": 1.86, "D": -0.40 + e_i * 1.76e9, "rate": 3.68e9},
                  "m0r1.fp32.zeros": {"S": 1.0, "D": 0.5, "rate": 9.9e9}, "m0r1.int8.zeros": {"S": 1.0 + N1_pp[i], "D": 0.5, "rate": 9.9e9}}
    items = {"m0r1.fp32.zeros": {"cycles_per_op": cycles[0], "D": {"mean": 0.5}}, "m0r1.int8.zeros": {"cycles_per_op": cycles[1], "D": {"mean": 0.5}},
             "m0.fp32.zeros": {"cycles_per_op": 544.001, "D": {"mean": -1.46}}, "m0.int8.zeros": {"cycles_per_op": 318.001, "D": {"mean": -0.40}},
             "m0k8.fp32.zeros": {"cycles_per_op": 280.001, "D": {"mean": -1.37}}, "m0k8.int8.zeros": {"cycles_per_op": 166.0, "D": {"mean": -0.25}},
             "anchor_pi": {"cycles_per_op": 546.001, "D": {"mean": 8.1}}}
    return {"passes": list(per), "per_pass": per, "items": items}


def test_d():
    bad = []
    six = synth(6, [1.5] * 6, [0.1] * 6)
    five = synth(5, [1.5] * 5, [0.1] * 5)
    w, _ = sc.choose(six, five, P)
    if w != "primary":
        bad.append("6 kept: not primary")
    w, d = sc.choose(five, six, P)
    if not w.startswith("relaxed") or len(d["passes"]) != 6:
        bad.append("5 vs 6: not relaxed")
    w, d = sc.choose(five, copy.deepcopy(five), P)
    if w != "primary":
        bad.append("5 vs 5: not primary")
    r5 = sc.score(five, P)["rules"]["R1_ops"]["verdict"]
    r6 = sc.score(six, P)["rules"]["R1_ops"]["verdict"]
    two = sc.score(synth(2, [1.5, 1.6], [0.1, 0.2]), P)["rules"]
    if not r5.startswith("NOT-SCORED") or r6.startswith("NOT-SCORED") or "R1_ops" in two or two["V1_one_row"]["verdict"] != "NOT-SCORED":
        bad.append(f"minimums: 5 -> {r5}, 6 -> {r6}, 2 -> {sorted(two)}")
    ok = not bad
    say(f"D  set-aside rule and minimums: 6 kept -> primary; 5 kept, relaxed 6 -> relaxed; 5 and 5 -> primary; R1 at 5 passes '{r5}', at 6 '{r6}'; "
        f"nothing scored at 2: {'PASS' if ok else 'FAIL'} {bad}")
    return ok


def test_e():
    bad = []
    lo = sc.score(synth(6, [1.50, 1.55, 1.60, 1.45, 1.52, 1.58], [0.10, 0.15, 0.05, 0.12, 0.08, 0.11]), P)["rules"]
    hi = sc.score(synth(6, [1.50, 1.55, 1.60, 1.45, 1.52, 1.58], [1.40, 1.45, 1.38, 1.50, 1.42, 1.47]), P)["rules"]
    mid = sc.score(synth(6, [1.50, 1.55, 1.60, 1.45, 1.52, 1.58], [0.60, 0.95, 0.70, 0.90, 0.65, 0.85]), P)["rules"]
    diff = sc.score(synth(6, [1.5] * 6, [0.1, 0.12, 0.11, 0.1, 0.13, 0.1], cycles=(62.0, 66.5)), P)["rules"]
    if lo["V1_one_row"]["verdict"] != "PER-ROW" or hi["V1_one_row"]["verdict"] != "PER-CYCLE" or mid["V1_one_row"]["verdict"] != "INCONCLUSIVE":
        bad.append(f"V1: {lo['V1_one_row']['verdict']} {hi['V1_one_row']['verdict']} {mid['V1_one_row']['verdict']}")
    v2lo = [v["verdict"] for v in lo["V2_readings"].values()]
    v2hi = [v["verdict"] for v in hi["V2_readings"].values()]
    if v2lo != ["CONSISTENT", "N1 BELOW", "N1 BELOW", "N1 BELOW"] or v2hi[0] != "N1 ABOVE" or v2hi[1] != "N1 ABOVE" or v2hi[3] != "CONSISTENT":
        bad.append(f"V2: {v2lo} {v2hi}")
    if diff["V0_equal_rate"]["verdict"] != "RATES-DIFFER" or not diff["V1_one_row"]["label"] or lo["V0_equal_rate"]["verdict"] != "EQUAL-RATE":
        bad.append("V0")
    if lo["R6_cycles"]["m0r1.int8.zeros"]["verdict"] != "PASS" or diff["R6_cycles"]["m0r1.int8.zeros"]["verdict"] != "FAIL":
        bad.append("R6")
    ok = not bad
    say(f"E  V0-V2 on synthetic passes: N1 near 0.1 W -> {lo['V1_one_row']['verdict']}, near N -> {hi['V1_one_row']['verdict']}, near N/2 -> "
        f"{mid['V1_one_row']['verdict']}; V2 (N1 near 0.1) {v2lo}, (N1 near N) {v2hi}; cycles 62.0/66.5 -> V0 {diff['V0_equal_rate']['verdict']}, R6 "
        f"{diff['R6_cycles']['m0r1.int8.zeros']['verdict']}: {'PASS' if ok else 'FAIL'} {bad}")
    return ok


def test_f():
    a = subprocess.run([sys.executable, os.path.join(HERE, "check_e129.py"), "--desk"], capture_output=True, text=True, cwd=ROOT)
    b = subprocess.run(["bash", os.path.join(HERE, "preflight_e129.sh"), "-q"], capture_output=True, text=True, cwd=ROOT)
    bo = (b.stdout + b.stderr).strip()                 # dmcmd_audit -q prints its verdict on stderr
    ok = a.returncode == 0 and "HARNESS OK" in a.stdout and b.returncode == 0 and "dmcmd_audit: GO" in bo and "NO-GO" not in bo
    say(f"F  {a.stdout.strip()} | {bo.splitlines()[0] if bo else ''} (rc {b.returncode}): {'PASS' if ok else 'FAIL'}")
    return ok


def main():
    full = "--full" in sys.argv
    say("E129 self-test (selftest_e129.py" + (" --full" if full else "") + "), committed data only")
    res = {"A": test_a(), "B": test_b()}
    if full:
        res["C"] = test_c()
    res.update({"D": test_d(), "E": test_e(), "F": test_f()})
    say("SELFTEST " + ("PASS" if all(res.values()) else "FAIL") + " " + json.dumps(res))
    open(os.path.join(HERE, "selftest.txt"), "w").write("\n".join(OUT) + "\n")
    sys.exit(0 if all(res.values()) else 1)


if __name__ == "__main__":
    main()
