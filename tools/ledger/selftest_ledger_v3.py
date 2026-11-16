#!/usr/bin/env python3
"""Ledger v3's self-tests (Q193): the freeze, the pins, the round trip, the rule switches, rule 7 on pinned cards, the
level rule, the given-seconds function and the bands; and, added before the land for the adversarial verify's findings
(Q193 verify-ledger3): rule 1's a-set (finding 1), v3's own numbers pinned against an independent re-derivation
(finding 2), S2 as E189 registered it (finding 3), every pinned data list re-verified file by file (finding 5), and the
DRAM copy's byte-row bands at another clock (finding 7).

    /usr/bin/python3 -I -B tools/ledger/selftest_ledger_v3.py --out DIR   # DIR required: writes DIR/selftest-v3.json, .txt

Each check prints PASS or FAIL; the last line is SELFTEST PASS when every check passes. Desk only. Standard library only.
SPDX-License-Identifier: Apache-2.0
"""
import argparse
import hashlib
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(REPO, "tools", "counter"))
import ledger_v3 as V3  # noqa: E402
import freeze_ledger_v3 as FZ  # noqa: E402
import programs_ledger_v3 as PR  # noqa: E402
import readings_ledger_v3 as RD  # noqa: E402

DATA_DIR = RD.DATA_DIR
PLAIN = RD.PLAIN
# v3's own numbers, pinned (verify-ledger3 finding 2): POST HOC readings by E189's rules, per pass, as
# readings_ledger_v3.py makes them (e_t = the seconds' error, e_S1 = J over idle given the measured seconds; on E194 with
# rule 7). The values are an INDEPENDENT re-derivation from the step-5 design's equations by the Q193 verify lane (Mon 16
# Nov 2026, no code shared with v3 or v2, on the first freeze); v3 reproduced every one within 1.3e-6, and the re-freeze
# (mul and csrr at their own rows) moves them by under 1e-6. A model re-frozen with a wrong price fails here.
PIN_TOL = 1e-4
PINNED = {
    ("E189", "copy-zeros"): {"e_t": 0.000514992525, "e_S1": -0.0517538513},
    ("E189", "copy-random"): {"e_t": -0.000514992525, "e_S1": -0.0319357266},
    ("E189", "sha256"): {"e_t": -0.012705668, "e_S1": 0.00599849942},
    ("E189", "sort-sorted"): {"e_t": 0.012270024, "e_S1": 0.0239096768},
    ("E189", "sort-shuffled"): {"e_t": -0.011099892, "e_S1": -0.0203676663},
    ("E191s2", "copy-zeros"): {"e_t": -0.000108338594, "e_S1": 0.0416398969},
    ("E191s2", "copy-random"): {"e_t": 0.000108338594, "e_S1": -0.0306284685},
    ("E191s2", "sha256"): {"e_t": -0.0127024494, "e_S1": 0.0439636592},
    ("E191s2", "sort-sorted"): {"e_t": 0.012262884, "e_S1": 0.0244256602},
    ("E191s2", "sort-shuffled"): {"e_t": -0.0110894139, "e_S1": 0.0572620588},
    ("E194", "copy-zeros"): {"e_t": 0.000382499549, "e_S1_r7": 0.0420585653},
    ("E194", "copy-random"): {"e_t": 0.00152180346, "e_S1_r7": 0.0227903575},
    ("E194", "sha256"): {"e_t": -0.0127154571, "e_S1_r7": 0.0450296174},
    ("E194", "sort-sorted"): {"e_t": 0.0122470139, "e_S1_r7": -0.00199349201},
    ("E194", "sort-shuffled"): {"e_t": -0.0111025203, "e_S1_r7": 0.00280528727},
}


def pinned_numbers(F3):
    """v3's readings of PINNED's numbers, and the largest absolute difference."""
    got, worst = {}, 0.0
    for day, card, f in (("E189", "aifoundry3", 600.0), ("E191s2", "aifoundry1-c1", 600.0), ("E194", "aifoundry2", 800.0)):
        progs = PR.blind_day_programs(card, f_mhz=f)
        meas = RD.M.read_day(day)
        for cfg in PLAIN:
            if day == "E194":
                no7 = RD.score(progs[cfg], F3, meas[cfg], rules=V3.ALL - {"r7"}, f_mhz=f)
                r7 = RD.score(progs[cfg], F3, meas[cfg], rules=V3.ALL, f_mhz=f)
                mine = {"e_t": no7["e_t"], "e_S1_r7": r7["e_S1"]}
            else:
                s = RD.score(progs[cfg], F3, meas[cfg], f_mhz=f)
                mine = {"e_t": s["e_t"], "e_S1": s["e_S1"]}
            for k, want in PINNED[(day, cfg)].items():
                d = abs(mine[k] - want)
                worst = max(worst, d)
                got[f"{day}/{cfg}/{k}"] = {"v3": mine[k], "pinned": want, "abs_diff": d}
    return got, worst


def verify_sums(sums_rel):
    """Re-hash every file a committed SHA256SUMS lists (paths relative to its own directory): the bad entries."""
    base = os.path.dirname(os.path.join(REPO, sums_rel))
    bad, n = [], 0
    for ln in open(os.path.join(REPO, sums_rel)):
        if not ln.strip():
            continue
        h, p = ln.rstrip("\n").split("  ", 1)
        n += 1
        fp = os.path.join(base, p)
        if not os.path.exists(fp) or hashlib.sha256(open(fp, "rb").read()).hexdigest() != h:
            bad.append(os.path.join(os.path.dirname(sums_rel), p))
    return bad, n


def e201_shapes(F3):
    """E201-shaped programs on aifoundry3 at 600 MHz (the design's six scored configurations and its two reported ones):
    the sorts' counts from the interpreter (participants 0-63, a sort's counts x the repetitions; the launch's fixed
    part left out), the copies' from copy_v32's pass (19 instructions a 256 B iteration, 17 a pass), the lines from the
    L1 model. For the rule-7 and level checks only: these are not E201's forecasts."""
    import ledger_interp as LI  # noqa: E402
    dis = LI.read_dis()
    out = {}
    for n, order, reps in ((16, "sorted", 89900), (16, "shuffled", 85600), (256, "sorted", 4100), (256, "shuffled", 3400),
                           (64, "shuffled", 16900), (512, "shuffled", 1800)):
        c = LI.sort_counts(n, order, range(0, 64, 8), dis=dis)["mean"]
        L = PR.lines_for("sort", keys=n, order=order)
        counts = {k: v * reps for k, v in c.items()}
        out[f"sort-{n}-{order}"] = V3.program(f"sort-{n}-{order}", "scalar", "aifoundry3", counts, 2048, units=reps,
                                              unit=f"sort of {n} keys",
                                              lines={k: L[k] * reps for k in ("fills", "read_fills", "write_fills",
                                                                              "dirty_evictions")},
                                              working_set_b_per_hart=12 * n, launches_a_burst=9)
    for name, part, passes in (("copy-l2-4m", 2048, 8900), ("copy-dram-256m", 131072, 56)):
        it = part // 256
        unit = {"mov.m.x": 1, "add": 1 + it, "sub": 1, "flw.ps": 8 * it, "fsw.ps": 8 * it, "addi": it + 1, "ld": 4,
                "li": 1, "sd": 1, "mv": 2, "@taken": it, "@not_taken": 3, "@jump": 2}
        L = PR.lines_for("copy", part=part)
        out[name] = V3.program(name, "copy", "aifoundry3", {k: v * passes for k, v in unit.items()}, 2048, units=passes,
                               unit=f"pass over {part} B a hart",
                               lines={k: L[k] * passes for k in ("fills", "read_fills", "write_fills", "dirty_evictions")},
                               working_set_b_per_hart=2 * part,
                               copy={"bytes": part * 2048 * passes, "data": "random", "part_bytes_per_hart": part,
                                     "passes": passes}, launches_a_burst=9)
    return out


def main(argv):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--out", required=True,
                    help="the directory to write the two files into (required: a run never rewrites the committed data "
                         "directory unless it is named here)")
    a = ap.parse_args(argv)
    res = []

    def check(name, ok, detail=""):
        res.append({"check": name, "pass": bool(ok), "detail": detail})
        print(f"{'PASS' if ok else 'FAIL'} {name}" + (f": {detail}" if detail else ""))

    # 1. the pins and the freeze
    try:
        V3.check_pins()
        check("the v2 inputs v3 imports are byte for byte as pinned (ledger_v2.py, ledger_estimate.py, frozen-v2.json, "
              "catalogue.json)", True)
    except SystemExit as e:
        check("the v2 inputs v3 imports are byte for byte as pinned", False, str(e))
    F3 = V3.load_frozen()
    h = V3.sha256_file(V3.FROZEN_V3)
    line = open(os.path.join(HERE, "frozen-v3.json.sha256")).read().split()[0]
    check("frozen-v3.json's sha256 is its freeze line (frozen-v3.json.sha256)", h == line, h)
    readme = os.path.join(DATA_DIR, "README.md")
    if os.path.exists(readme):
        check("the data README carries the freeze line", h in open(readme).read(), h)
    body = FZ.dump(FZ.build(F3["frozen_pst"]))
    check("frozen-v3.json recomputed from its committed sources is the same, byte for byte",
          body == open(V3.FROZEN_V3).read())
    bad = [p for p, s in F3["parents_sha256"].items() if V3.sha256_file(os.path.join(REPO, p)) != s]
    check("every parent the freeze names is unchanged", not bad, ", ".join(bad))
    sums = sorted(p for p in F3["parents_sha256"] if os.path.basename(p) == "SHA256SUMS")
    bad, n = [], 0
    for p in sums:
        b, k = verify_sums(p)
        bad += b
        n += k
    need = ["docs/reports/data/2026-11-12-q166-progs/kernel/ledger.dis.gz", "workloads/ledger/ledger_desk.py"] + \
           [os.path.join(RD.M.DATA, RD.M.DAYS[d]["dir"], "SHA256SUMS") for d in RD.M.DAYS]
    miss = [p for p in need if p not in F3["parents_sha256"]]
    check("the freeze pins what a new configuration's counts and lines are made from (the kernel's disassembly, "
          "ledger_desk.py) and every measured day it reads; every pinned SHA256SUMS still matches every file it lists",
          not bad and not miss, f"{len(sums)} lists, {n} files re-hashed; differ {bad[:5]}; not pinned {miss}")
    # 2. the L1 model's and the interpreter's own test
    import test_l1_model as T  # noqa: E402
    rc = T.main([])
    check("tools/counter/test_l1_model.py", rc == 0)
    # 3. the round trip
    rt = RD.roundtrip(F3)
    check("v3 with all seven rules off is v2: E189's, E191's and E194's frozen forecasts and scorers",
          rt["verdict"] == "ROUND TRIP PASS", f"{rt['checked']} numbers, worst relative difference {rt['worst_rel_diff']:.2e}; "
                                              f"failed {rt['failed']}")
    # 4. the rule switches touch only what they should (E189's programs, aifoundry3)
    progs = PR.blind_day_programs("aifoundry3")
    pc1 = PR.blind_day_programs("aifoundry1-c1")

    def P(prog, rules, **kw):
        return V3.predict(prog, F3, rules=rules, **kw)
    v2 = {k: P(p, V3.NONE) for k, p in progs.items()}
    for r, what in (("r1", "seconds of the scalar programs only"), ("r2", "the copies' seconds only"),
                    ("r3", "the scalar programs' J over idle only"), ("r4", "the copies' J over idle only"),
                    ("r5", "J with the card at rest only")):
        one = {k: P(p, frozenset([r])) for k, p in progs.items()}
        d_t = [k for k in PLAIN if one[k]["seconds"]["point"] != v2[k]["seconds"]["point"]]
        d_j = [k for k in PLAIN if one[k]["j_over_idle"] != v2[k]["j_over_idle"]]
        d_r = [k for k in PLAIN if one[k]["j_total"] != v2[k]["j_total"]]
        want = {"r1": (list(RD.SCALAR), [], list(RD.SCALAR)), "r2": (list(RD.COPIES), [], list(RD.COPIES)),
                "r3": ([], list(RD.SCALAR), list(RD.SCALAR)), "r4": ([], list(RD.COPIES), list(RD.COPIES)),
                "r5": ([], [], list(PLAIN))}[r]
        check(f"v2 + {r} alone changes {what}", (d_t, d_j, d_r) == want,
              f"seconds {d_t}, J over idle {d_j}, J at rest {d_r}")
    v3 = {k: P(p, V3.ALL) for k, p in progs.items()}
    no6 = {k: P(p, V3.ALL - {"r6"}) for k, p in progs.items()}
    check("rule 6 changes nothing on aifoundry3 (its own column is aifoundry3's)",
          all(no6[k]["j_total"] == v3[k]["j_total"] and no6[k]["seconds"]["point"] == v3[k]["seconds"]["point"]
              for k in PLAIN))
    c6 = {k: (P(p, V3.ALL)["j_over_idle"], P(p, V3.ALL - {"r6"})["j_over_idle"]) for k, p in pc1.items()}
    check("rule 6 changes card 1's line and copy prices (rules 3 and 4 read card 1's column)",
          all(c6[k][0] != c6[k][1] for k in PLAIN), {k: [round(x, 4) for x in v] for k, v in c6.items()})
    # 5. rule 7 is zero on every pinned-card load
    zero = []
    for nm, pp in (("E189 aifoundry3", progs), ("E191 card 1", pc1), ("E201 shapes, aifoundry3", e201_shapes(F3))):
        for k, p in pp.items():
            with7, without = P(p, V3.ALL), P(p, V3.ALL - {"r7"})
            zero.append(not with7["rule7"]["applies"] and with7["j_over_idle"] == without["j_over_idle"]
                        and with7["j_total"] == without["j_total"])
    e59 = json.load(open(os.path.join(REPO, RD.FORECAST["E189"])))["configs"]["sparse-parity"]["primary"]["load"]
    q, q0 = V3.predict_v2load(e59, F3, rules=V3.ALL, launches_a_burst=9), V3.predict_v2load(e59, F3, rules=V3.ALL - {"r7"})
    zero.append(not q["rule7"]["applies"] and q["j_over_idle"] == q0["j_over_idle"])
    import loads_ledger_v2 as LL  # noqa: E402  (E59's loads as the ledger v2 built them: aifoundry3, 600 MHz)
    lv, le, F2 = V3.mods()
    for e in LL.e59_loads(F2):
        for vn, ld in e["variants"].items():
            q, q0 = V3.predict_v2load(ld, F3, rules=V3.ALL, launches_a_burst=9), V3.predict_v2load(ld, F3, rules=V3.ALL - {"r7"})
            zero.append(not q["rule7"]["applies"] and q["j_over_idle"] == q0["j_over_idle"] and q["j_total"] == q0["j_total"])
    check("rule 7 is zero for every pinned-card load (E189's and E191's programs, E201's shapes, sparse parity at 600 MHz, "
          "E59's loads)", all(zero), f"{sum(zero)} of {len(zero)} loads")
    a2 = PR.blind_day_programs("aifoundry2", f_mhz=800.0)
    on = [P(p, V3.ALL, f_mhz=800.0)["rule7"]["applies"] for p in a2.values()]
    check("rule 7 applies on aifoundry2 at 800 MHz (a registered busy-base relation, above its 600 MHz idle point)", all(on))
    # 6. the level rule
    shapes = e201_shapes(F3)
    lev = {k: V3.level_of(F3, p)[0] for k, p in list(shapes.items()) + list(progs.items())}
    want = {"sort-16-sorted": "L1", "sort-16-shuffled": "L1", "sort-256-sorted": "L2", "sort-256-shuffled": "L2",
            "sort-64-shuffled": "L2", "sort-512-shuffled": "L2", "copy-l2-4m": "L2", "copy-dram-256m": "DRAM",
            "copy-zeros": "DRAM", "copy-random": "DRAM", "sha256": "L2", "sort-sorted": "L2", "sort-shuffled": "L2"}
    check("the level rule: L1 for the 16-key sorts, L2 for the 512-key sorts (not refused) and the 4 MiB copy, DRAM for "
          "the 256 MiB and 1 GiB copies", lev == want, json.dumps(lev, sort_keys=True))
    check("no blind-day or E201-shaped program is outside v3",
          not any(P(p, V3.ALL)["outside_v3"] for p in list(shapes.values()) + list(progs.values())))
    # 7. given() at the forecast's own seconds and die reproduces predict()
    gp = []
    for k, p in progs.items():
        f = v3[k]
        g = V3.given(p, F3, f["seconds"]["point"], f["wall_s"], f["die_start_c"], rules=V3.ALL)
        gp.append(abs(g["j_over_idle"] / f["j_over_idle"] - 1) < 1e-12 and abs(g["j_total"] / f["j_total"] - 1) < 1e-12)
    check("given() at a forecast's own seconds, wall seconds and die reproduces its J over idle and J at rest", all(gp))
    # 8. bands hold their points
    bd = []
    for pp in (progs, pc1, shapes):
        for k, p in pp.items():
            f = P(p, V3.ALL)
            bd.append(f["seconds"]["band"][0] <= f["seconds"]["point"] <= f["seconds"]["band"][1]
                      and f["j_over_idle_band"][0] <= f["j_over_idle"] <= f["j_over_idle_band"][1]
                      and f["j_total_band"][0] <= f["j_total"] <= f["j_total_band"][1])
    check("every band holds its point (seconds, J over idle, J at rest)", all(bd), f"{sum(bd)} of {len(bd)}")
    # the DRAM copy's byte rows at another clock (verify-ledger3 finding 7): points unscaled, bands' high ends x (V/V600)^2
    a2c = PR.blind_day_programs("aifoundry2", f_mhz=800.0)
    rr = []
    for k in RD.COPIES:
        t6, t8 = P(a2c[k], V3.ALL, f_mhz=600.0)["terms"], P(a2c[k], V3.ALL, f_mhz=800.0)["terms"]
        f8 = V3.v2_factor("aifoundry2", 800.0)
        for term in ("bytes: DRAM read", "bytes: DRAM write-back"):
            rr.append(t6[term]["j"] == t8[term]["j"] and t6[term]["band"][0] == t8[term]["band"][0]
                      and abs(t8[term]["band"][1] / t6[term]["band"][1] - f8) < 1e-12)
    check("rule 4's byte rows at another clock: the points unscaled, the bands' high ends x (V/V600)^2 as rule 3's "
          "(aifoundry2's copies at 800 against 600 MHz)", all(rr) and f8 > 1.0, f"{sum(rr)} of {len(rr)}; (V800/V600)^2 {f8:.4f}")
    # 9. sparse parity: v3 = v2 but for rules 5 and 7
    s0, s5 = V3.predict_v2load(e59, F3, rules=V3.NONE), V3.predict_v2load(e59, F3, rules=V3.ALL - {"r5"})
    check("sparse parity: v3 without rule 5 is v2 on a pinned card", s0["j_over_idle"] == s5["j_over_idle"]
          and s0["j_total"] == s5["j_total"])
    # 10. verify5's exclusivity arithmetic
    th = {x: (1 + x) / (1 - x) for x in (0.05, 0.10, 0.15)}
    check("two forecasts can both pass within th iff their ratio is at most (1+th)/(1-th): 1.105, 1.222, 1.353",
          [round(th[x], 3) for x in (0.05, 0.10, 0.15)] == [1.105, 1.222, 1.353]
          and V3.both_can_pass(1.0, 1.2, 0.10) and not V3.both_can_pass(1.0, 1.25, 0.10))
    # 11. rule 1's a-set (verify-ledger3 finding 1): one-cycle rows only; mul and csrr at their own rows
    C = F3["constants"]
    aset = C["a_set_mnemonics"]["value"]
    a_ = C["a_hart_cycles"]["value"]
    dl = C["loop_delta_hart_cycles"]["value"]
    lv, le, F2 = V3.mods()
    cat3 = V3.catalogue("aifoundry3")
    x = {m: 1.0 / cat3.rate(le.ALIAS.get(m, m), "random") - dl for m in aset + ["mul", "csrr"]}
    loop = V3.program("mul-loop", "scalar", "aifoundry3", {"add": 900.0, "mul": 50.0, "@not_taken": 49.0, "@taken": 1.0},
                      2048)
    T, other = V3.t_hart_v3(F3, loop, loop["counts"])
    want = a_ * 949.0 + 50.0 * x["mul"] + C["c_br_hart_cycles"]["value"] * 1.0
    check("rule 1's a-set holds only one-cycle rows (each within 0.5 hart-cycles of a after delta); mul and csrr issue at "
          "their own rows (a 1,000-instruction loop with 50 mul: 949 a + 50 x_mul + c_br)",
          all(abs(x[m] - a_) < 0.5 for m in aset) and "mul" not in aset and "csrr" not in aset
          and abs(T - want) < 1e-9 and set(other) == {"mul"},
          f"widest inside {max((round(abs(x[m] - a_), 4), m) for m in aset)}; x_mul {x['mul']:.4f}, x_csrr "
          f"{x['csrr']:.4f}; the loop {T:.4f} hart-cycles against {want:.4f} (+{100 * (T / (a_ * 999 + 1 * C['c_br_hart_cycles']['value']) - 1):.0f}% "
          f"on mul at a)")
    # 12. v3's own numbers pinned against an independent re-derivation (verify-ledger3 finding 2)
    got, worst = pinned_numbers(F3)
    check(f"v3's numbers pinned: {len(got)} POST HOC readings (in sample on E189 and E191's second session, E194 with rule "
          f"7) equal an independent re-derivation within {PIN_TOL:g}", worst <= PIN_TOL,
          f"worst absolute difference {worst:.2e}")
    # 13. S2 as E189 registered it (verify-ledger3 finding 3): the band AND 15%
    unit = [RD.ok_s2({"S2_ratio": 1.0, "S2_in_band": True}), RD.ok_s2({"S2_ratio": 1.0, "S2_in_band": False}),
            RD.ok_s2({"S2_ratio": 1.2, "S2_in_band": True}), RD.ok_s2({"S2_ratio": 1.0})]
    six = {}
    for d, card in (("E189", "aifoundry3"), ("E191s2", "aifoundry1-c1")):
        rows, _, _ = RD.day_rows(d, F3, card)
        rows["sparse-parity"] = RD.spp_row(d, F3)
        vv = RD.verdicts(list(rows.values()))
        six[d] = (vv["S2"]["pass"], vv["S2"]["of"], vv["S2-15"]["pass"])
    check("S2 is E189's registered test (score_e189.py ok_S2: the mean t_k inside the two-sided band and within 15%): "
          "unit cases, and the in-sample six on both cards", unit == [True, False, False, None]
          and all(v == (6, 6, 6) for v in six.values()), f"unit {unit}; (S2, of, S2-15) {six}")
    fails = [r["check"] for r in res if not r["pass"]]
    verdict = "SELFTEST PASS" if not fails else "SELFTEST FAIL"
    print(f"{verdict}: {len(res) - len(fails)} of {len(res)}")
    os.makedirs(a.out, exist_ok=True)
    json.dump({"checks": res, "verdict": verdict, "frozen_v3_sha256": h, "interpreter": "/usr/bin/python3 " + sys.version.split()[0]},
              open(os.path.join(a.out, "selftest-v3.json"), "w"), indent=1, sort_keys=True)
    open(os.path.join(a.out, "selftest-v3.txt"), "w").write(
        "\n".join(f"{'PASS' if r['pass'] else 'FAIL'} {r['check']}" + (f": {r['detail']}" if r["detail"] else "")
                  for r in res) + f"\n{verdict}: {len(res) - len(fails)} of {len(res)}\n")
    return 0 if not fails else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
