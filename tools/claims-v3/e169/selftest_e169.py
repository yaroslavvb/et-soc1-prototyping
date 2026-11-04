#!/usr/bin/env python3
"""E169 (Q141(s)): the scorer's self-test, run before the scorer's commit and before any E169 claim. Desk only: no card, no device.

    nice -n 10 python3 -B tools/claims-v3/e169/selftest_e169.py > tools/claims-v3/e169/selftest.txt

1. E158 -> E169 (the brief: "E158 -> E169"). reduce_e169.reduce(), with E158's block map, on E158's committed session
   (docs/reports/data/2026-11-03-e158-l3-retention/aifoundry2/s1) must reproduce E158's results.json exactly (per_shape, t800_by_pass,
   launches_800_by_pass, cycles_per_op_800_by_pass, cells, checks, peaks, skipped, config_after); E158's own registered score()
   (reduce_e158.py, imported unchanged) on that reduction must then reproduce E158's rules and errors exactly, which are its registered
   verdicts (R0 PASS, replicate PASS; R1 INCONSISTENT, SOFT; R2 NO SINGLE CURVE; R3 PASS x3, +0.41 / +0.26 / -0.76%; R4 NOT BETTER;
   R5 10 of 14; R6; R7). E169's R0 must read PASS on the same 98 runs.
2. The step machinery on E158's committed collapses: score_e169.pair_reading() on E158's per-pass T800 must give the step, interval and
   reading that steps_e169.py stored in step-rule-e169.json (committed_collapses_C3_post_hoc), and E169's tie rule on E158's own
   session must read TIED.
3. Known truths through score_e169.score(): the six shapes at SM's, ISO's and STRICT's frozen T800; half SM's step; the card's committed
   steps; a mixed card; a zone edge; too few passes; a pass with too few launches; a failed and a missing check of C; a tie off by 3%;
   the floor and an own sd above it; the formats printed; a shape not measured; the reported power at its own levels.
SPDX-License-Identifier: Apache-2.0
"""
import json
import math
import os
import sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
LAB = os.path.normpath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(LAB, "tools/claims-v3/e158"))
import reduce_e169 as RE  # noqa: E402
import score_e169 as SC  # noqa: E402

E158D = os.path.join(LAB, "docs/reports/data/2026-11-03-e158-l3-retention")
FAILS = []


def say(ok, what):
    print(("PASS " if ok else "FAIL ") + what)
    if not ok:
        FAILS.append(what)


def rt(x):
    return json.loads(json.dumps(x, default=lambda o: None))


def part1():
    import model_e158 as M          # E158's frozen model, imported unchanged
    import reduce_e158 as R8        # E158's registered reduction and score(), imported unchanged
    P158 = json.load(open(os.path.join(LAB, "tools/claims-v3/e158/predictions-e158.json")))
    R158 = json.load(open(os.path.join(E158D, "results.json")))
    red = RE.reduce([os.path.join(E158D, "aifoundry2/s1")], P158, RE.PASS_OF_BLOCK_E158)
    for k in ("per_shape", "t800_by_pass", "launches_800_by_pass", "cycles_per_op_800_by_pass", "cells", "checks", "peaks", "skipped", "config_after"):
        say(rt(red[k]) == R158[k], f"E158 -> E169: reduce_e169 on E158's committed session reproduces results.json {k} exactly")
    say(red["n_runs"] == R158["runs"] == 98, f"E158 -> E169: {red['n_runs']} runs, as E158's 98")
    desk = M.load_desk()
    ab, c1 = M.load_prices()
    e146 = json.load(open(R8.E146_RES))
    checks_ok = bool(red["checks"]) and all(x in ("exact", "approx") for x in red["checks"])
    V, ERR = R8.score(red["per_shape"], red["t800_by_pass_raw"], P158, desk, ab, c1, checks_ok, red["cells"], e146, R8.power_fn())
    say(rt(V) == R158["rules"], "E158 -> E169: E158's registered score() on the ported reduction reproduces results.json rules exactly")
    say(rt(ERR) == R158["errors"], "E158 -> E169: ... and results.json errors exactly")
    r3 = V["R3"]["per_format"]
    print(f"     E158's registered verdicts, reproduced: R0 {V['R0']['verdict']} (replicate {V['R0']['replicate_verdict']}); R1 {V['R1']['consistent']} {V['R1']['outside']}, "
          f"{V['R1']['against_strict_c']}; R2 {V['R2']['verdict']} (least rms {V['R2']['iso']['rms_share']:.3f}); R3 {V['R3']['verdict']} (ISO "
          + " / ".join(f"{100 * r3[t]['ISO']['rel']:+.2f}% {r3[t]['ISO']['verdict']}" for t in ("fp32", "fp16", "int8"))
          + f"); R4 {V['R4']['verdict']} (ISO {100 * V['R4']['iso_kb2']:.1f}% vs STRICT-C {100 * V['R4']['strict_c_kb2']:.1f}%); R5 {V['R5']['pass']} of {V['R5']['n']}; "
          f"R7 P0 {V['R7']['rms_P0']} W rms")
    want = (V["R0"]["verdict"] == "PASS" and V["R0"]["replicate_verdict"] == "PASS" and V["R1"]["consistent"] == "INCONSISTENT" and V["R1"]["outside"] == ["K4n8"]
            and V["R2"]["verdict"] == "NO SINGLE CURVE" and all(r3[t]["ISO"]["verdict"] == "PASS" for t in r3) and V["R4"]["verdict"] == "NOT BETTER"
            and (V["R5"]["pass"], V["R5"]["n"]) == (10, 14) and [round(100 * r3[t]["ISO"]["rel"], 2) for t in ("fp32", "fp16", "int8")] == [0.41, 0.26, -0.76])
    say(want, "E158 -> E169: the verdicts are E158's registered ones (R0 PASS; R1 INCONSISTENT [K4n8]; R2 NO SINGLE CURVE; R3 PASS x3 at +0.41 / +0.26 / -0.76%; R4 NOT BETTER; R5 10 of 14)")
    rr = SC.r0(red)
    say(rr["verdict"] == "PASS" and rr["runs"] == 98, f"E169's R0 on E158's 98 runs: {rr['verdict']} (every run checked, every check {red['checks']})")
    return red


def part2(red, rule):
    st = rule["committed_collapses_C3_post_hoc"]
    for a, b in (("D4", "D2"), ("K4n8", "K4n7"), ("K6n4", "K6n3"), ("K6n4", "K6n5")):
        ref = st[f"E158:{a}/{b}"]
        v = SC.pair_reading(red["t800_by_pass_raw"], red["launches_800_by_pass"], a, b, "fp32", ref["models"], rule)
        iv = ref["rule_interval_3_passes"]
        same = (v["n"] == 3 and abs(v["step"] - iv["step"]) < 2e-5 and abs(v["lo"] - iv["lo"]) < 2e-5 and abs(v["hi"] - iv["hi"]) < 2e-5
                and v["reading"].split(":")[0] == ref["reading_post_hoc"])
        say(same, f"E158 {a}/{b}: pair_reading {100 * v['step']:+.2f}% [{100 * v['lo']:+.2f}, {100 * v['hi']:+.2f}] -> {v['reading']} equals steps_e169.py's "
                  f"({100 * iv['step']:+.2f}% [{100 * iv['lo']:+.2f}, {100 * iv['hi']:+.2f}] -> {ref['reading_post_hoc']}); presence {v['presence']}, size {v['size']}")
    tt = SC.ties(red["per_shape"], red["t800_by_pass_raw"], red["launches_800_by_pass"], rule)
    say(tt["verdict"] == "TIED", f"E169's tie rule on E158's own session: {tt['verdict']} (steps " + ", ".join(f"{k} {x['diff_points']:+.3f} points" for k, x in tt["steps"].items()) + ")")


# ------------------------------------------------------------------ part 3: made-up truths
NOISE = (0.0010, -0.0010, 0.0006, -0.0006, 0.0)


def fake(T, npass=5, noise=NOISE, checks="exact", fmt=None, low=None, ties=None, cells=None):
    """a reduction from known T800s (fp32 unless fmt): each shape's per-pass T800 its truth times (1 + noise[pass])"""
    tb, nl, per, rc = {}, {}, {}, []
    allT = dict(T)
    if ties is not None:
        allT.update(ties)
    for s, base in allT.items():
        t = "fp32"
        npss = 2 if s.startswith("K") else npass
        sign = 1 if s.startswith("P") else -1          # P shapes move one way and N shapes the other, so a step's log ratio carries twice the noise
        vals = []
        for j in range(1, npss + 1):
            v = base * (1 + sign * noise[(j - 1) % len(noise)])
            tb[f"{j}|{s}.{t}"] = v
            nl[f"{j}|{s}.{t}"] = 12
            vals.append(v)
        per[f"{s}.{t}"] = {"T800": sum(vals) / len(vals), "n800": 12 * npss}
        rc.append({"cell": f"{s}-{t}-zeros", "block": "A", "checks": [checks] if checks else []})
    if fmt:
        for (s, t), v in fmt.items():
            tb[f"1|{s}.{t}"] = v
            nl[f"1|{s}.{t}"] = 12
            per[f"{s}.{t}"] = {"T800": v, "n800": 12}
    if low:
        for key in low:
            nl[key] = 4
    return {"t800_by_pass_raw": tb, "launches_800_by_pass": nl, "per_shape": per, "run_checks": rc, "checks": [checks] if checks else [],
            "cells": cells or {}, "gates": [], "dry": False, "n_runs": len(rc), "sessions": ["made-up"], "skipped": [], "config_after": [], "peaks": {}}


def model_T(pred, m, t="fp32"):
    return {s: pred["shapes"][s][t][m]["T800"] for s in SC.SHAPES}


def part3(rule, pred, kit):
    S = pred["shapes"]
    E158T = rule["ties_e158"]["T800"]
    hyp = rule["hypotheses"]

    def run(T, **kw):
        kw.setdefault("ties", E158T)
        return SC.score(fake(T, **kw), rule, pred, kit)

    v = run(model_T(pred, "SM"))
    say(v["verdict"] == "INDEX STEP AS SM", f"SM's truth: {v['verdict']}")
    say(v["B7"]["fp32"]["point_verdict"] == "PASS" and v["B7"]["fp32"]["resolved_count"] == 3, f"SM's truth: B7 point {v['B7']['fp32']['point_verdict']}, resolved {v['B7']['fp32']['resolved_count']} of 3")
    say(v["ties"]["verdict"] == "TIED" and v["R0"]["verdict"] == "PASS" and not v["labels"], f"SM's truth: ties {v['ties']['verdict']}, R0 {v['R0']['verdict']}, labels {v['labels']}")
    say(v["steps"]["P2/N2"]["reading"] == "SUPPORTS SM, ISO", f"SM's truth: P2/N2 (not counted) reads '{v['steps']['P2/N2']['reading']}' (SM's and ISO's zones overlap)")
    v = run(model_T(pred, "ISO"))
    say(v["verdict"] == "NO STEP", f"ISO's truth: {v['verdict']}")
    say(v["B7"]["fp32"]["point_verdict"].startswith("FAIL") and v["B7"]["fp32"]["resolved_count"] == 0, f"ISO's truth: B7 point {v['B7']['fp32']['point_verdict']}, resolved {v['B7']['fp32']['resolved_count']} of 3")
    hw = v["steps"]["P1/N1"]["half_width_points"]
    say(v["steps"]["P1/N1"]["floor_used"] and abs(hw - 0.417) < 0.002, f"the floor: P1/N1's half-width {hw} points over 5 passes of small noise (sigma0's 0.417)")
    v = run(model_T(pred, "STRICT"))
    say(v["verdict"] == "NO STEP" and v["steps"]["P2/N2"]["reading"] == "SUPPORTS STRICT", f"STRICT's truth: {v['verdict']}; P2/N2 '{v['steps']['P2/N2']['reading']}'")
    iso = model_T(pred, "ISO")
    half = dict(iso)
    for P, N in SC.PAIRS:
        half[P] = iso[N] * (1 + 0.5 * hyp[f"{P}/{N}"]["fp32"]["steps"]["SM"])
    v = run(half)
    say(v["verdict"] == "A STRIDE STEP SM DOES NOT SIZE", f"half SM's step on ISO's level: {v['verdict']} (P1/N1 {v['steps']['P1/N1']['reading']})")
    card = dict(iso)
    card["P1"], card["P3"] = iso["N1"] * 1.2889, iso["N3"] * 1.1486
    v = run(card)
    say(v["verdict"] == "A STRIDE STEP SM DOES NOT SIZE" and v["steps"]["P1/N1"]["size"] == "NOT SM" and v["steps"]["P3/N3"]["size"] == "NOT SM",
        f"the card's committed steps (+28.9% on P1/N1, +14.9% on P3/N3): {v['verdict']}; shares of SM's step {v['steps']['P1/N1']['share_of_SM_step']['share']} and {v['steps']['P3/N3']['share_of_SM_step']['share']}")
    mix = dict(iso)
    mix["P1"] = iso["N1"] * (1 + hyp["P1/N1"]["fp32"]["steps"]["SM"])
    v = run(mix)
    say(v["verdict"] == "MIXED", f"P1/N1 at SM's step, P3/N3 none: {v['verdict']}")
    edge = dict(iso)
    edge["P1"] = iso["N1"] * (1 + hyp["P1/N1"]["fp32"]["steps"]["SM"] - 0.030)
    edge["P3"] = iso["N3"] * (1 + hyp["P3/N3"]["fp32"]["steps"]["SM"])
    v = run(edge)
    say(v["steps"]["P1/N1"]["size"] == "UNRESOLVED" and v["verdict"] == "A STRIDE STEP, ITS SIZE UNRESOLVED", f"P1/N1 on SM's zone's edge: size {v['steps']['P1/N1']['size']}; {v['verdict']}")
    pr = dict(iso)
    pr["P1"] = iso["N1"] * 1.030
    pr["P3"] = iso["N3"] * (1 + hyp["P3/N3"]["fp32"]["steps"]["SM"])
    v = run(pr)
    say(v["steps"]["P1/N1"]["presence"] == "UNRESOLVED" and v["verdict"] == "UNRESOLVED", f"P1/N1 at +3.0% (the no-step zone's edge): presence {v['steps']['P1/N1']['presence']}; {v['verdict']}")
    v = run(model_T(pred, "SM"), npass=2)
    say(v["verdict"] == "NO VERDICT" and v["steps"]["P1/N1"]["reading"] == "NO READING", f"two passes: {v['verdict']} ({v['steps']['P1/N1']['why']})")
    v = run(model_T(pred, "SM"), low=["2|P1.fp32"])
    say(v["steps"]["P1/N1"]["n"] == 4 and v["steps"]["P1/N1"]["per_pass"]["pass2"]["counted"] is False and v["verdict"] == "INDEX STEP AS SM",
        f"a pass whose P1 burst had 4 launches at >= 790 MHz is not counted: P1/N1 over {v['steps']['P1/N1']['n']} passes; {v['verdict']}")
    v = run(model_T(pred, "SM"), checks="wrong")
    say(v["R0"]["verdict"] == "FAIL" and "R0 FAIL" in v["labels"] and v["verdict"] == "INDEX STEP AS SM", f"a wrong check of C: R0 {v['R0']['verdict']}, labels {v['labels']}, the verdict still printed ({v['verdict']})")
    v = run(model_T(pred, "SM"), checks=None)
    say(v["R0"]["verdict"] == "FAIL", f"runs with no check of C: R0 {v['R0']['verdict']} ({len(v['R0']['bad'])} runs named)")
    off = dict(E158T)
    off["K4n8"] = E158T["K4n8"] * 1.03
    v = run(model_T(pred, "SM"), ties=off)
    say(v["ties"]["verdict"].startswith("NOT TIED") and "session not tied to E158" in v["labels"], f"K4n8 3% off E158: {v['ties']['verdict']}; labels {v['labels']}")
    v = run(model_T(pred, "SM"), noise=(0.012, -0.012, 0.008, -0.008, 0.0))
    x = v["steps"]["P1/N1"]
    say(not x["floor_used"] and x["sd_used"] > rule["rule"]["sigma0_ln_step"], f"passes scattered 1%: the passes' own sd {100 * x['sd_ln']:.3f}% is used (floor {100 * rule['rule']['sigma0_ln_step']:.3f}%), half-width {x['half_width_points']} points; {x['reading']}")
    fm = {(s, "fp16"): S[s]["fp16"]["SM"]["T800"] for s in SC.SHAPES}
    v = run(model_T(pred, "SM"), fmt=fm)
    f1 = v["formats_printed"].get("P1/N1.fp16")
    say(f1 is not None and f1["scored"] is False and f1["nearest_model"] == "SM" and v["B7"]["fp16"]["point_verdict"] == "PASS" and v["B7"]["fp16"]["scored"] is False,
        f"fp16 printed if run: P1/N1.fp16 {100 * f1['mean_step']:+.2f}%, nearest {f1['nearest_model']}, not scored; B7 fp16 point {v['B7']['fp16']['point_verdict']} (printed)")
    some = model_T(pred, "SM")
    del some["N2"]
    v = run(some)
    say(v["B7"]["fp32"]["point_verdict"].startswith("FAIL") and "not measured" in v["B7"]["fp32"]["point_verdict"] and v["steps"]["P2/N2"]["reading"] == "NO READING"
        and v["verdict"] == "INDEX STEP AS SM", f"N2 not measured: B7 point {v['B7']['fp32']['point_verdict']}; P2/N2 {v['steps']['P2/N2']['reading']}; {v['verdict']}")
    W = rule["power_reported"]
    cells = {f"{s}-fp32-zeros": {"burst_p800_w_runs": [W["P0_800_fp32_zeros_w"][s] + W["beta"] * W["delta_fallback_w"]["fp32"]] * 5, "burst_die_start": [W["T_ref_c"]] * 5} for s in SC.SHAPES}
    v = run(model_T(pred, "SM"), cells=cells)
    pw = v["power_reported"]["fp32"]
    say(abs(pw["rms"]["err_TZ"]) < 1e-9 and abs(pw["rms"]["err_TZ_TD"]) < 1e-9 and abs(pw["mean"]["err_P0"] - W["beta"] * W["delta_fallback_w"]["fp32"]) < 1e-3,
        f"power at P0 + beta delta from T_ref: err_TZ {pw['rms']['err_TZ']}, err_TZ_TD {pw['rms']['err_TZ_TD']}, p800 - P0 mean {pw['mean']['err_P0']} W (beta delta {W['beta'] * W['delta_fallback_w']['fp32']:.3f})")


def main():
    say(SC.check_frozen() is None, f"the scorer's frozen inputs match their committed bytes ({len(SC.FROZEN)} files: predictions-e169.json, stride_sm.py, peaks_e169.py, step-rule-e169.json, kit-e169.json)")
    rule, pred, kit = SC.load()
    print("\n1. E158 -> E169: the ported reduction and E158's registered verdicts")
    red = part1()
    print("\n2. The step machinery on E158's committed collapses, and the tie rule on E158's own session")
    part2(red, rule)
    print("\n3. Known truths through score_e169.score()")
    part3(rule, pred, kit)
    print("\nALL PASS" if not FAILS else f"\n{len(FAILS)} FAILED")
    return 0 if not FAILS else 1


if __name__ == "__main__":
    sys.exit(main())
