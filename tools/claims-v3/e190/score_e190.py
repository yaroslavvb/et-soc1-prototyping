#!/usr/bin/env python3
"""E190 (Q169): the frozen scorer. It reads the kit's reduced data (the form below) and the frozen forecast, and refuses to run if the forecast's bytes
changed. Standard library only.

    python3 -I -B tools/claims-v3/e190/score_e190.py DATA.json [--out SCORED.json]
    python3 -I -B tools/claims-v3/e190/score_e190.py --selftest-stub OUT.json     five stub cases, each with its expected verdicts (exit 0 = PASS)
    python3 -I -B tools/claims-v3/e190/score_e190.py --selftest-e136 OUT.json     E136's and E146's committed g4k / D4 bursts scored against their own anchors

THE DATA (one JSON; the kit's reducer writes it from the session's records):
  {"experiment": "E190", "arms": {"A": ARM, "B": ARM}}; an arm missing or empty is NO DATA.
  ARM = {"smoke": {"checks": [..], "cycles_per_op": {fmt: x}}, "x600": {fmt: {"T600_us": x, "T800_us": x, "n600": n, "n800": n}},
         "cells": {"<fmt>.<burst|sus>": {"runs": [RUN, ...]}}}
  RUN = {"t_gemm_s": sum of wall_s / sum of passes over the run's counted launches (arm A: kernel clock >= 790 MHz; arm B: 590-610 MHz; launch >= 0;
         sustained: launches inside the last 40 s), "n_gemm": GEMMs counted, "p_work_w": median board W over the 10 Hz samples inside those launches,
         "p_rest_w": median board W over the last 5 s of rest before the run's first process, "die_start_c": the shires' mean then,
         "die_c": burst: the highest shires' mean in the work window; sustained: the mean over the last 40 s, "mhz": the mean minion clock over the
         samples inside the counted launches, "mhz_min": the lowest such sample, "checks": every check of C of the run ("exact" / "approx" / "wrong")}
THE MEASURED JOULES of a run: over idle J = (p_work - p_rest) t_gemm; with the card at rest J = p_work t_gemm. A cell is the mean of its runs.
THE RULES (E190.md section 6): R0 ties; S1 seconds in the band; S2 J over idle given the seconds within 10%; S3 J with the card at rest given the
seconds and rest within 5%; S4 J over idle in its frozen band; S5 arm A's burst die within 3 C of E136's law at the measured start; S6 the clock;
S7 arm B against arm A scaled by the clock; S8 where fp32 falls (a reading). A cell with no run is NO DATA: never a failure.
SPDX-License-Identifier: Apache-2.0
"""
import argparse
import copy
import hashlib
import json
import math
import os
import random
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, "..", "..", ".."))
FC_PATH = os.path.join(HERE, "forecast-e190.json")
FORECAST_SHA256 = "7875c153940067baab33e0f5d912eb8b5eb31476c67b519bb633dbf8283c7ace"
FMTS = ("fp32", "fp16", "int8")
BLOCKS = ("burst", "sus")
S2_REL, S3_REL, S5_C, S6_SUS_MHZ, S7_T_REL, S7_J_REL = 0.10, 0.05, 3.0, 30.0, 0.04, 0.15
HELD, NONE_MAX, OUTSIDE = 0.75, 0.25, (-0.5, 1.5)


def sha(path):
    return hashlib.sha256(open(path, "rb").read()).hexdigest()


def mean(v):
    v = [x for x in v if x is not None]
    return sum(v) / len(v) if v else None


def p_at(levels, f):
    """E136's p_at: the board level at a mean clock f between the frozen levels (600, 700, 800)"""
    P = {int(k): v for k, v in levels.items()}
    if f >= 800:
        return P[800]
    if f >= 700:
        return P[700] + (P[800] - P[700]) * (f - 700) / 100.0
    if f >= 600:
        return P[600] + (P[700] - P[600]) * (f - 600) / 100.0
    return P[600]


def W_point(fc, arm, t, block, mhz):
    """the frozen W over idle at the measured clock: forecast_e190.W_at, the registered given() formula's own code"""
    sys.path.insert(0, HERE)
    import forecast_e190 as FE
    return FE.W_at(fc, arm, t, block, mhz)


def inside(x, band):
    return band[0] <= x <= band[1]


def cell_stats(runs):
    ok = [r for r in runs if r.get("t_gemm_s") and r.get("p_work_w") is not None and r.get("p_rest_w") is not None]
    if not ok:
        return None
    jo = [(r["p_work_w"] - r["p_rest_w"]) * r["t_gemm_s"] for r in ok]
    jr = [r["p_work_w"] * r["t_gemm_s"] for r in ok]
    return {"n_runs": len(ok), "t": mean([r["t_gemm_s"] for r in ok]), "p_work": mean([r["p_work_w"] for r in ok]), "p_rest": mean([r["p_rest_w"] for r in ok]),
            "die_start": mean([r.get("die_start_c") for r in ok]), "die": mean([r.get("die_c") for r in ok]), "mhz": mean([r.get("mhz") for r in ok]),
            "mhz_min": min([r["mhz_min"] for r in ok if r.get("mhz_min") is not None], default=None),
            "j_over": mean(jo), "j_rest": mean(jr), "j_over_runs": jo, "j_rest_runs": jr,
            "checks": sorted({c for r in ok for c in r.get("checks", [])})}


def score(data, fc):
    out = {"cells": {}, "rules": {}, "headline": {}}
    arms = data.get("arms") or {}
    r0 = {"checks": [], "cycles": {}}
    for arm in ("A", "B"):
        A = arms.get(arm) or {}
        sm = A.get("smoke") or {}
        r0["checks"] += sm.get("checks", [])
        for t, cpo in (sm.get("cycles_per_op") or {}).items():
            f = 800.0 if arm == "A" else 600.0
            pt = fc["speed"][t][f"T{int(f)}_us"]["point"] * f
            r0["cycles"][f"{arm}.{t}"] = {"measured": cpo, "point": pt, "ratio": cpo / pt, "ok": 0.5 <= cpo / pt <= 2.5}
        for t in FMTS:
            for b in BLOCKS:
                key = f"{arm}.{t}.{b}"
                st = cell_stats(((A.get("cells") or {}).get(f"{t}.{b}") or {}).get("runs") or [])
                fcell = fc["cells"][key]
                if st is None:
                    out["cells"][key] = {"verdict": "NO DATA"}
                    continue
                r0["checks"] += st["checks"]
                W = W_point(fc, arm, t, b, st["mhz"])
                g_over, g_rest = W * st["t"], (st["p_rest"] + W) * st["t"]
                rec = {"n_runs": st["n_runs"], "measured": {k: st[k] for k in ("t", "p_work", "p_rest", "die_start", "die", "mhz", "mhz_min", "j_over", "j_rest")},
                       "frozen": {k: fcell[k]["point"] for k in ("t_gemm_s", "W_over", "P_rest_w", "J_over", "J_rest")},
                       "given": {"W_over": W, "j_over": g_over, "j_rest": g_rest},
                       "err": {"t": st["t"] / fcell["t_gemm_s"]["point"] - 1, "j_over_given": st["j_over"] / g_over - 1, "j_rest_given": st["j_rest"] / g_rest - 1,
                               "j_over_forecast": st["j_over"] / fcell["J_over"]["point"] - 1, "j_rest_forecast": st["j_rest"] / fcell["J_rest"]["point"] - 1}}
                rec["S1"] = "PASS" if inside(st["t"], fcell["t_gemm_s"]["band"]) else "FAIL"
                rec["S2"] = "PASS" if abs(rec["err"]["j_over_given"]) <= S2_REL else "FAIL"
                rec["S3"] = "PASS" if abs(rec["err"]["j_rest_given"]) <= S3_REL else "FAIL"
                rec["S4"] = "PASS" if inside(st["j_over"], fcell["J_over"]["band"]) else "FAIL"
                rec["S4_rest_reported"] = "INSIDE" if inside(st["j_rest"], fcell["J_rest"]["band"]) else "OUTSIDE"
                if arm == "A" and b == "burst" and st["die"] is not None and st["die_start"] is not None:
                    kb = fc["die_law_e136"]          # E136's frozen burst law, with the frozen W and the measured start and rest
                    pred = st["die_start"] + kb["k_burst_c_per_w"] * (st["p_rest"] + W - kb["P_idle_w"])
                    rec["S5"] = {"pred": pred, "err": st["die"] - pred, "verdict": "PASS" if abs(st["die"] - pred) <= S5_C else "FAIL"}
                if st["mhz"] is not None:
                    if arm == "A" and b == "burst":
                        rec["S6"] = "PASS" if st["mhz"] >= 790.0 else "FAIL"
                    elif arm == "A":
                        rec["S6"] = "PASS" if abs(st["mhz"] - fcell["mhz"]["point"]) <= S6_SUS_MHZ else "FAIL"
                    else:
                        lo = st["mhz_min"] if st["mhz_min"] is not None else st["mhz"]
                        rec["S6"] = "PASS" if (590.0 <= lo and st["mhz"] <= 610.0) else "FAIL"
                out["cells"][key] = rec
    r0_ok = bool(r0["checks"]) and all(c in ("exact", "approx") for c in r0["checks"]) and all(v["ok"] for v in r0["cycles"].values())
    out["rules"]["R0"] = {"verdict": "PASS" if r0_ok else ("NO DATA" if not r0["checks"] else "FAIL"), **r0,
                          "note": "a FAIL labels every other verdict"}
    for rule in ("S1", "S2", "S3", "S4", "S6"):
        v = {k: c[rule] for k, c in out["cells"].items() if rule in c}
        out["rules"][rule] = {"cells": v, "pass": sum(1 for x in v.values() if x == "PASS"), "scored": len(v),
                              "verdict": "NO DATA" if not v else ("PASS" if all(x == "PASS" for x in v.values()) else "FAIL")}
    v5 = {k: c["S5"]["verdict"] for k, c in out["cells"].items() if "S5" in c}
    out["rules"]["S5"] = {"cells": v5, "verdict": "NO DATA" if not v5 else ("PASS" if all(x == "PASS" for x in v5.values()) else "FAIL")}
    # S7: arm B against arm A scaled by the clock (bursts)
    s7 = {}
    for t in FMTS:
        a, b = out["cells"].get(f"A.{t}.burst", {}), out["cells"].get(f"B.{t}.burst", {})
        if "measured" not in a or "measured" not in b:
            s7[t] = {"verdict": "NO DATA"}
            continue
        x = ((arms.get("A") or {}).get("x600") or {}).get(t) or {}
        X = x["T600_us"] / x["T800_us"] if x.get("n600", 0) >= 2 and x.get("n800", 0) >= 5 else fc["speed"][t]["X"]
        tA = a["measured"]["t"] * (800.0 / a["measured"]["mhz"] if a["measured"]["mhz"] and a["measured"]["mhz"] < 790 else 1.0)
        jr = fc["cells"][f"A.{t}.burst"]["W_levels"]["600"] * fc["speed"][t]["t600_s"]["point"] / fc["cells"][f"A.{t}.burst"]["J_over"]["point"]
        et = b["measured"]["t"] / (tA * X) - 1
        ej = b["measured"]["j_over"] / (fc["constants"]["kappa_e37"] * a["measured"]["j_over"] * jr) - 1
        s7[t] = {"X_used": X, "X_from": "arm A's own 600 MHz launches" if x.get("n600", 0) >= 2 else "the frozen X", "j_ratio_600_800": jr,
                 "err_t": et, "err_j_over": ej, "verdict": "SAME" if (abs(et) <= S7_T_REL and abs(ej) <= S7_J_REL) else "DIFFERS"}
    scored = [v for v in s7.values() if v["verdict"] != "NO DATA"]
    same = sum(1 for v in scored if v["verdict"] == "SAME")
    out["rules"]["S7"] = {"formats": s7, "verdict": "NO DATA" if not scored else ("THE SAME SCALED" if same >= 2 and same >= len(scored) - 1 else "DIFFERS")}
    # S8: where fp32 falls on arm A
    a32, a16 = out["cells"].get("A.fp32.burst", {}), out["cells"].get("A.fp16.burst", {})
    if "measured" in a32 and "measured" in a16:
        q = a32["measured"]["t"] / fc["gemm"]["fp32"]["ops_per_minion"] / (a16["measured"]["t"] / fc["gemm"]["fp16"]["ops_per_minion"])
        qS = fc["speed"]["fp32"]["T800_us"]["point"] / fc["speed"]["fp16"]["T800_us"]["point"]
        qN = fc["speed"]["fp32"]["T800_us"]["anchor_measured"] / fc["speed"]["fp16"]["T800_us"]["anchor_measured"]
        h = (q - qN) / (qS - qN)
        rd = "OUTSIDE" if (h < OUTSIDE[0] or h > OUTSIDE[1]) else "STRICT" if h >= HELD else "NONE" if h <= NONE_MAX else "BETWEEN"
        out["rules"]["S8"] = {"q": q, "q_strict": qS, "q_none": qN, "h": h, "reading": rd}
    else:
        out["rules"]["S8"] = {"reading": "NO DATA"}
    # the ledger arm (REPORTED): card 1's bursts priced by the ledger v2 at their measured seconds and starting die
    led = {}
    try:
        sys.path.insert(0, HERE)
        import forecast_e190 as FE
        for t in FMTS:
            c = out["cells"].get(f"B.{t}.burst", {})
            if "measured" in c and c["measured"]["die_start"] is not None:
                g = FE.given_ledger(t, c["measured"]["t"], c["measured"]["die_start"], c["measured"]["p_rest"])
                led[t] = {"given": g, "err_j_over": c["measured"]["j_over"] / g["j_over"] - 1, "err_j_rest": c["measured"]["j_rest"] / g["j_rest"] - 1}
    except Exception as e:  # the ledger arm is reported only; its failure never changes a verdict
        led["error"] = repr(e)
    out["ledger_arm_reported"] = led
    for arm in ("A", "B"):
        for t in FMTS:
            c = out["cells"].get(f"{arm}.{t}.burst", {})
            if "measured" in c:
                out["headline"][f"{arm}.{t}"] = {"t_s": c["measured"]["t"], "j_over": c["measured"]["j_over"], "j_rest": c["measured"]["j_rest"],
                                                 "frozen_t_s": c["frozen"]["t_gemm_s"], "frozen_j_over": c["frozen"]["J_over"], "frozen_j_rest": c["frozen"]["J_rest"]}
    return out


# ------------------------------------------------------------------ the self-tests
def run_from(cell, rng, scale_t=1.0, scale_w=1.0, noise=0.005):
    t = cell["t_gemm_s"]["point"] * scale_t * (1 + rng.uniform(-noise, noise))
    pr = cell["P_rest_w"]["point"] * (1 + rng.uniform(-noise, noise))
    W = cell["W_over"]["point"] * scale_w * (1 + rng.uniform(-noise, noise))
    return {"t_gemm_s": t, "n_gemm": 20, "p_work_w": pr + W, "p_rest_w": pr, "die_start_c": 50.0 if cell["mhz"]["point"] > 700 else 58.0,
            "die_c": cell["die_c"]["point"], "mhz": cell["mhz"]["point"], "mhz_min": cell["mhz"]["point"] - (2.0 if cell["mhz"]["point"] > 700 else 5.0),
            "checks": ["approx"]}


def stub(fc, case, seed=190):
    rng = random.Random(seed)
    data = {"experiment": "E190", "stub": case, "arms": {}}
    for arm in ("A", "B"):
        if case == "C" and arm == "B":
            continue
        A = {"smoke": {"checks": ["approx", "approx", "exact"],
                       "cycles_per_op": {t: fc["speed"][t][f"T{800 if arm == 'A' else 600}_us"]["point"] * (800 if arm == "A" else 600) * 1.01 for t in FMTS}},
             "x600": {t: {"T600_us": fc["speed"][t]["T600_us"]["point"], "T800_us": fc["speed"][t]["T800_us"]["point"], "n600": 4, "n800": 50} for t in FMTS},
             "cells": {}}
        if case == "E" and arm == "A":
            A["smoke"]["checks"][0] = "wrong"
        for t in FMTS:
            for b in BLOCKS:
                c = fc["cells"][f"{arm}.{t}.{b}"]
                st, sw = 1.0, 1.0
                if case == "B":
                    sw = 1.25
                if case == "D" and arm == "A" and t == "fp32":
                    st = fc["speed"]["fp32"]["T800_us"]["anchor_measured"] / fc["speed"]["fp32"]["T800_us"]["point"]
                if case == "D" and arm == "B" and t == "fp32":
                    st = fc["speed"]["fp32"]["T600_us"]["anchor_measured"] / fc["speed"]["fp32"]["T600_us"]["point"]
                n = 4 if b == "burst" else 2
                A["cells"][f"{t}.{b}"] = {"runs": [run_from(c, rng, st, sw) for _ in range(n)]}
        data["arms"][arm] = A
    return data


EXPECT = {
    "A": {"R0": "PASS", "S1": "PASS", "S2": "PASS", "S3": "PASS", "S4": "PASS", "S5": "PASS", "S6": "PASS", "S7": "THE SAME SCALED", "S8": "STRICT"},
    "B": {"R0": "PASS", "S1": "PASS", "S2": "FAIL", "S3": "FAIL", "S6": "PASS", "S7": "THE SAME SCALED", "S8": "STRICT"},
    "C": {"R0": "PASS", "S1": "PASS", "S2": "PASS", "S3": "PASS", "S7": "NO DATA", "S8": "STRICT", "B_cells": "NO DATA"},
    "D": {"R0": "PASS", "S1": "PASS", "S2": "PASS", "S3": "PASS", "S7": "THE SAME SCALED", "S8": "NONE"},
    "E": {"R0": "FAIL", "S1": "PASS"},
}


def verdicts(sc):
    v = {k: sc["rules"][k]["verdict"] for k in ("R0", "S1", "S2", "S3", "S4", "S5", "S6", "S7")}
    v["S8"] = sc["rules"]["S8"]["reading"]
    v["B_cells"] = "NO DATA" if all(sc["cells"][f"B.{t}.{b}"].get("verdict") == "NO DATA" for t in FMTS for b in BLOCKS) else "DATA"
    return v


def selftest_stub(fc, out_path):
    res, ok = {}, True
    for case, exp in EXPECT.items():
        sc = score(stub(fc, case), fc)
        v = verdicts(sc)
        bad = {k: (v[k], e) for k, e in exp.items() if v[k] != e}
        res[case] = {"verdicts": v, "expected": exp, "mismatches": bad, "pass": not bad,
                     "what": {"A": "every cell at its frozen point (+-0.5%)", "B": "the watts 25% over the frozen point, the seconds at it",
                              "C": "arm B absent (NO DATA)", "D": "fp32 at its anchor's speed (the extra lines cost nothing), its watts at the point",
                              "E": "one smoke check of C wrong"}[case]}
        ok = ok and not bad
    rep = {"selftest": "stub", "interpreter": sys.executable, "version": sys.version.split()[0], "cases": res, "verdict": "PASS" if ok else "FAIL"}
    json.dump(rep, open(out_path, "w"), indent=1, sort_keys=True)
    print(f"selftest-stub ({sys.executable} {sys.version.split()[0]}): " + ", ".join(f"{c} {'PASS' if r['pass'] else 'FAIL ' + str(r['mismatches'])}" for c, r in res.items()))
    print(rep["verdict"])
    return ok


def selftest_e136(fc, out_path):
    """E136's g4k (fp32, fp16) and E146's D4 (int8) bursts, scored by this scorer against their own anchors: a forecast whose arm A burst cells are the
    anchors (T the anchor's measured T800 x its ops a pass; W the anchor's pooled measured W over idle; bands +-3% and +-2 W). The rest is the ledger's
    idle law at each run's start die, as the forecast's anchors read it. Every S1 must PASS and every S2 / S3 error be under 3%."""
    sys.path.insert(0, HERE)
    import forecast_e190 as FE
    ops = {"fp32": 16384, "fp16": 16384, "int8": 4 * 8 * 2 * 4 * 32}
    f2 = copy.deepcopy(fc)
    data = {"experiment": "E190-selftest-e136", "arms": {"A": {"smoke": {"checks": ["exact", "approx"], "cycles_per_op": {}}, "cells": {}}}}
    rows = {}
    for t in FMTS:
        an = FE.anchor(t)
        pl = fc["cells"][f"A.{t}.burst"]["power_law"]
        T8 = an["T800"]
        c = f2["cells"][f"A.{t}.burst"]
        tp = ops[t] * T8 * 1e-6
        c["t_gemm_s"] = {"point": tp, "band": [tp * 0.97, tp * 1.03]}
        Wm = pl["W_meas_anchor"]
        c["W_levels"] = {"600": Wm, "700": Wm, "800": Wm}
        c["W_over"] = {"point": Wm, "band": [Wm - 2, Wm + 2]}
        c["J_over"] = {"point": Wm * tp, "band": [(Wm - 2) * tp * 0.97, (Wm + 2) * tp * 1.03]}
        runs = []
        for b in pl["anchor_bursts"]:
            pr = FE.idle("aifoundry2", b["die_start_c"])
            runs.append({"t_gemm_s": tp, "n_gemm": 100, "p_work_w": b["burst_w"], "p_rest_w": pr, "die_start_c": b["die_start_c"], "die_c": None,
                         "mhz": 800.0, "mhz_min": 790.0, "checks": ["approx"]})
        data["arms"]["A"]["cells"][f"{t}.burst"] = {"runs": runs}
        rows[t] = {"anchor": an["name"], "runs": [(b["session"], b["burst_w"], b["die_start_c"]) for b in pl["anchor_bursts"]]}
    sc = score(data, f2)
    res = {}
    ok = True
    for t in FMTS:
        c = sc["cells"][f"A.{t}.burst"]
        good = c["S1"] == "PASS" and abs(c["err"]["j_over_given"]) < 0.03 and abs(c["err"]["j_rest_given"]) < 0.03
        Wm = f2["cells"][f"A.{t}.burst"]["W_over"]["point"]
        per_run = [{"session": r[0], "err_j_over_given": (r[1] - FE.idle("aifoundry2", r[2])) / Wm - 1,
                    "err_j_rest_given": r[1] / (FE.idle("aifoundry2", r[2]) + Wm) - 1} for r in rows[t]["runs"]]
        good = good and all(abs(x["err_j_over_given"]) <= S2_REL and abs(x["err_j_rest_given"]) <= S3_REL for x in per_run)
        res[t] = {"S1": c["S1"], "err_j_over_given": c["err"]["j_over_given"], "err_j_rest_given": c["err"]["j_rest_given"], "per_run": per_run,
                  "pass": good, **rows[t]}
        ok = ok and good
    rep = {"selftest": "e136", "interpreter": sys.executable, "version": sys.version.split()[0], "formats": res, "verdict": "PASS" if ok else "FAIL"}
    json.dump(rep, open(out_path, "w"), indent=1, sort_keys=True)
    print(f"selftest-e136 ({sys.executable} {sys.version.split()[0]}): " + "; ".join(
        f"{t} S1 {r['S1']}, cell J over idle given {r['err_j_over_given']:+.2%}, J at rest {r['err_j_rest_given']:+.2%}, per run "
        + ", ".join(f"{x['session']} {x['err_j_over_given']:+.2%} / {x['err_j_rest_given']:+.2%}" for x in r["per_run"]) for t, r in res.items()))
    print(rep["verdict"])
    return ok


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("data", nargs="?")
    ap.add_argument("--out")
    ap.add_argument("--selftest-stub")
    ap.add_argument("--selftest-e136")
    a = ap.parse_args()
    got = sha(FC_PATH)
    if FORECAST_SHA256 != "FROZEN-AT-REGISTRATION" and got != FORECAST_SHA256:
        print(f"REFUSED: forecast-e190.json sha256 {got} is not the registered {FORECAST_SHA256}")
        sys.exit(4)
    fc = json.load(open(FC_PATH))
    if a.selftest_stub:
        sys.exit(0 if selftest_stub(fc, a.selftest_stub) else 1)
    if a.selftest_e136:
        sys.exit(0 if selftest_e136(fc, a.selftest_e136) else 1)
    data = json.load(open(a.data))
    sc = score(data, fc)
    sc["forecast_sha256"] = got
    if a.out:
        json.dump(sc, open(a.out, "w"), indent=1, sort_keys=True)
    for k, v in sc["rules"].items():
        print(k, v.get("verdict", v.get("reading")))
    for k, v in sc["headline"].items():
        print(f"{k}: t {v['t_s']:.4f} s (frozen {v['frozen_t_s']:.4f}); J over idle {v['j_over']:.3f} (frozen {v['frozen_j_over']:.3f}); "
              f"J with the card at rest {v['j_rest']:.3f} (frozen {v['frozen_j_rest']:.3f})")


if __name__ == "__main__":
    main()
