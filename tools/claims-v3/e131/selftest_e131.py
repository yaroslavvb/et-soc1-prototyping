#!/usr/bin/env python3
"""E131's self-test (Q136), run at the desk before the registration commit. Nothing it prints is E131 data: parts C-D read E112b's committed
passes of the same pass on this card (published 1 Nov), as E129's self-test read E124's, to test the code and the set-aside rule.

    /usr/bin/python3 tools/claims-v3/e131/selftest_e131.py [--full] > tools/claims-v3/e131/selftest.txt

  A. The stops: run_e131.guard_stops on a stand-in run_e78 module: 67.9 W with every shire at 71.9 C passes the line through; 68.0 W, or one
     shire at 72.0 C, writes STOP and exits with EXIT_HOT (6).
  B. The set-aside rule's parts on stand-in reductions: classify() on every reason reduce_e78 writes; readings() restores a tie-only pass whole
     (S2), a one-format pass for the other two formats (S3), never a pass with failed runs, a config flag, three failing formats or no relaxed
     values; the per-format rule makes a claim NOT SCORED when a format it reads has fewer than 3 passes.
  C. (--full) The port: reduce_e131.py with E112b's options (leakage auto, refit on) on E112b's three committed passes reproduces E112b's
     committed reduction, b-e95-card1/e112b.json: the same kept passes and set-asides, and every per-pass D, S and p80 to 1e-9.
  D. (--full) E131's pipeline on E112b's passes: the primary at 0.2414 W/C, the relaxed reduction (every per-pass value of the passes both keep
     equal to 1e-12, the premise of S2 and S3), and score_e131.py: which reading carries, what it restores, and every verdict (labelled: E112b's
     data, already published, never E131's).
  E. check_e131.py --desk reads HARNESS OK, and preflight_e131.sh reads GO.
SPDX-License-Identifier: Apache-2.0
"""
import json
import os
import subprocess
import sys
import tempfile
import types

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(ROOT, "tools", "claims-v3", "kinds"))
RAW112 = os.path.join(ROOT, "docs/reports/data/2026-11-01-e112-real-replicates/aifoundry1-c1/kinds")
E112B = os.path.join(ROOT, "docs/reports/data/2026-11-01-e112-real-replicates/b-e95-card1/e112b.json")
PYN = "/usr/bin/python3"
fails = []


def check(name, cond, detail=""):
    print(f"{'PASS' if cond else 'FAIL'} {name}{': ' + detail if detail else ''}")
    if not cond:
        fails.append(name)


def part_a():
    import run_e131
    with tempfile.TemporaryDirectory() as d:
        m = types.SimpleNamespace(EXIT_HOT=6)
        lines = {"ok": {"board_w": 67.9, "temp_c": {"minshire": [71.9, 60.0], "pmic": 60}},
                 "board": {"board_w": 68.0, "temp_c": {"minshire": [60.0], "pmic": 60}},
                 "die": {"board_w": 50.0, "temp_c": {"minshire": [55.0, 72.0], "pmic": 60}}}
        for k, s in lines.items():
            m.last_sample = (lambda s_: (lambda path: s_))(s)
            g = run_e131.guard_stops(m, 68.0, 72.0, d)
            try:
                r = g("x")
                code = None
            except SystemExit as e:
                r, code = None, e.code
            stop = os.path.exists(os.path.join(d, "STOP"))
            if k == "ok":
                check("A stops: 67.9 W and 71.9 C pass", r is s and code is None and not stop)
            else:
                check(f"A stops: {k} line writes STOP and exits 6", code == 6 and stop, open(os.path.join(d, "STOP")).read().strip()
                      if stop else "no STOP")
                os.remove(os.path.join(d, "STOP"))


def part_b():
    import score_e131 as s
    import score_e95 as s95
    c = s.classify
    check("B classify tie", c(["anchor_pi drifts +0.700 W"]) == (False, True, set()))
    check("B classify zeros line", c(["fp32.zeros departs -0.253 W from its straight line"]) == (False, False, {"fp32"}))
    check("B classify spans", c(["fp16.randn spans 1.283 W", "int8.zeros spans 0.700 W"]) == (False, False, {"fp16", "int8"}))
    check("B classify failed runs", c(["3 runs failed a gate"])[0] is True)

    def red(passes, sa, cfg=()):
        names = ["fp32.zeros", "fp32.randn", "fp16.zeros", "fp16.randn", "int8.zeros", "int8.full", "anchor_pi", "fp32.r2_vgg16_fc2"]
        items = {n: {"type": n.split(".")[0] if "." in n else "fp32", "macs_per_op": 4096} for n in names}
        pp = {str(p): {n: {"D": 1.0 + p % 7, "S": 2.0, "p80": 30.0, "rate": 1e9} for n in names} for p in passes}
        return {"passes": passes, "per_pass": pp, "items": items, "passes_set_aside": [{"pass": p, "why": w} for p, w in sa],
                "passes_config_flags": [{"pass": p} for p in cfg]}
    Q = red([1, 2, 3, 4, 5, 6, 7], [])
    P = red([1, 2], [(3, ["anchor_pi drifts +0.700 W"]), (4, ["fp32.zeros departs -0.253 W from its straight line"]),
                     (5, ["3 runs failed a gate", "fp16.randn spans 1.1 W"]), (6, ["fp32.zeros spans 0.7 W", "fp16.randn spans 1.2 W",
                                                                                  "int8.full spans 1.1 W"]),
                     (7, ["int8.zeros spans 0.7 W"]), (8, ["fp16.randn spans 1.2 W"])], cfg=[7])
    for p in ("1", "2"):
        Q["per_pass"][p] = P["per_pass"][p]
    rd, rs = s.readings(P, Q, s95.mc)
    check("B S2 restores the tie-only pass whole", [x["pass"] for x in rs["S2"]] == [3] and rd["S2"]["passes"] == [1, 2, 3])
    check("B S3 restores the one-format pass for the other two", [x["pass"] for x in rs["S3"]] == [4]
          and rs["S3"][0]["formats_restored"] == ["fp16", "int8"] and rd["S3"]["passes"] == [1, 2, 3, 4]
          and "fp32.zeros" not in rd["S3"]["per_pass"]["4"] and "fp16.randn" in rd["S3"]["per_pass"]["4"])
    check("B never: failed runs (5), three formats (6), a config flag (7), no relaxed values (8)",
          not ({5, 6, 7, 8} & set(rd["S3"]["passes"])))
    check("B carrying reading", s.carrying(rd, 3) == "S2" and s.carrying({"S1": {"passes": [1]}, "S2": {"passes": [1]},
                                                                            "S3": {"passes": [1, 2]}}, 3) is None)
    n = s.per_type_passes(rd["S3"])
    check("B passes by format in S3", n == {"fp32": 3, "fp16": 4, "int8": 4}, str(n))
    sc = {"claims": {"C9": {"verdict": "PASS"}, "C6": {"verdict": "PASS"}}}
    R = {"passes": [1, 2, 3], "per_pass": {"1": {"fp32.randn": {}, "int8.full": {}}, "2": {"fp32.randn": {}, "int8.full": {}},
                                           "3": {"int8.full": {}}}}
    s.type_rule(sc, R, {"C9": ["fp32"], "C6": ["int8"]}, 3)
    check("B the per-format rule", sc["claims"]["C9"]["verdict"] == "NOT SCORED" and sc["claims"]["C9"]["verdict_before_format_rule"] == "PASS"
          and sc["claims"]["C6"]["verdict"] == "PASS")


def run(cmd):
    r = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True)
    return r.returncode, r.stdout, r.stderr


def part_cd():
    dirs = [os.path.join(RAW112, f"p{p}") for p in (11250, 11251, 11252)]
    with tempfile.TemporaryDirectory() as t:
        o_auto, o_p, o_q = (os.path.join(t, x) for x in ("auto.json", "p.json", "q.json"))
        rc, out, err = run([PYN, "tools/claims-v3/e131/reduce_e131.py", *dirs, "--out", o_auto])
        check("C reduce_e131 with E112b's options runs", rc == 0, err[-300:])
        A, B = json.load(open(o_auto)), json.load(open(E112B))
        check("C the same kept passes and set-asides as E112b", A["passes"] == B["passes"] and A["passes_set_aside"] == B["passes_set_aside"],
              f"{A['passes']} {A['passes_set_aside']}")
        worst, n = 0.0, 0
        for p, it in B["per_pass"].items():
            for name, e in it.items():
                for k in ("D", "S", "p80"):
                    if e.get(k) is not None:
                        worst = max(worst, abs(A["per_pass"][p][name][k] - e[k]))
                        n += 1
        check("C every per-pass D, S, p80 equals E112b's committed reduction", worst <= 1e-9, f"{n} values, max |diff| {worst:.2e}; "
              f"leak {A['leak']['k_w_per_c']:.6f} vs {B['leak']['k_w_per_c']:.6f}")
        rc, out, err = run([PYN, "tools/claims-v3/e131/reduce_e131.py", *dirs, "--leak", "0.2414", "--out", o_p])
        rc2, out2, err2 = run([PYN, "tools/claims-v3/e131/reduce_e131.py", *dirs, "--relax-anchors", "--leak", "0.2414", "--out", o_q])
        P, Q = json.load(open(o_p)), json.load(open(o_q))
        print(f"D primary at 0.2414 W/C: passes {P['passes']}, set aside {P['passes_set_aside']}; relaxed: passes {Q['passes']}, "
              f"set aside {Q['passes_set_aside']}; relaxed gates {Q['reducer']['gates']}")
        worst, n = 0.0, 0
        for p in set(P["passes"]) & set(Q["passes"]):
            for name, e in P["per_pass"][str(p)].items():
                for k, v in e.items():
                    if isinstance(v, (int, float)):
                        worst = max(worst, abs(Q["per_pass"][str(p)][name][k] - v))
                        n += 1
        check("D the relaxed reduction's per-pass values equal the primary's on the passes both keep", worst <= 1e-12,
              f"{n} values, max |diff| {worst:.2e}")
        o_a = os.path.join(t, "arm-auto.json")
        run([PYN, "tools/claims-v3/e131/reduce_e131.py", *dirs, "--leak", "auto", "--no-refit", "--out", o_a])
        rc, out, err = run([sys.executable, "tools/claims-v3/e131/score_e131.py", "--primary", o_p, "--relaxed", o_q, "--arm",
                            f"auto={o_a}", "--json", os.path.join(t, "sc.json"), "--md", os.path.join(t, "r.md")])
        check("D score_e131 runs", rc == 0, (err or out)[-400:])
        if rc == 0:
            sc = json.load(open(os.path.join(t, "sc.json")))
            sa = sc["set_aside"]
            print(f"D (E112b's data, labelled, not E131's): carrying reading {sa['carrying_reading']}; restored S2 {sa['restored']['S2']}, "
                  f"S3 {sa['restored']['S3']}")
            for nm, r in sa["readings"].items():
                print(f"D   reading {nm}: passes {r['passes']}, by format {r['passes_by_format']}, claims {r['claims']}, cross {r['cross_card']}")
            print(f"D   arm auto (E112b's own primary options, two passes): {sc['arms']['auto']['claims']}")


def part_e():
    rc, out, err = run([sys.executable, "tools/claims-v3/e131/check_e131.py", "--desk"])
    check("E check_e131.py --desk", rc == 0 and "HARNESS OK" in out, (out + err).strip()[-300:])
    rc, out, err = run(["bash", "tools/claims-v3/e131/preflight_e131.sh", "-q"])
    check("E preflight_e131.sh reads GO", rc == 0, (out + err).strip().splitlines()[0] if (out + err).strip() else "")


def main():
    part_a()
    part_b()
    if "--full" in sys.argv:
        part_cd()
    part_e()
    print("SELFTEST", "PASS" if not fails else f"FAIL {fails}")
    sys.exit(1 if fails else 0)


if __name__ == "__main__":
    main()
