#!/usr/bin/env python3
"""E183 (Q155): the forecasts, frozen before any kit file (E183.md section 4). Every arm's watts for every E183 kind above the fadd.ps
zeros and for every registered train (D(first) - D(second)), on aifoundry3 card 0 at 600 MHz pinned. Standard library only; reads
committed files only, each checked at its sha256 first; deterministic.

    /usr/bin/python3 -B forecast_e183.py --root <lab repo> [--out <dir>]     # writes forecast-e183.json and forecast-e183.txt
    /usr/bin/python3 -B forecast_e183.py --root <lab repo> --check           # re-makes both and compares them byte for byte

THE ARMS (E183.md section 4):
  P      E180's frozen primary (E180.md section 4; `4dc5035f`), unchanged: the energy catalogue's random-row price per named flip times
         the whole-minion bench's named flips. For a one-number fadd.ps kind the bench's named flips are 24.995 per 1-bit of the
         result and nothing else (E180.md section 3: every one of E180's 21 one-number kinds), so P is E180's ladder slope times the
         result's popcount, 0.1649149678 W a bit on aifoundry3; checked here against E180's own P for each of E180's kinds E183 reuses.
         M10 itself prices no vector add (E180.md section 9, item 3; dated note M1 section 3: "not applicable"): this is E180's P.
  BLIND  E180's measured price, E180-L (blind on 6 Nov; `c8a3a6ee`): +0.009692712 W per result 1-bit, 95% [+0.002733740,
         +0.016651685], applied to each kind's result 1-bits. It is the blind number for E183: no E183 datum exists.
  OPER   an operand-bit arm, POST HOC for its fit: the OLS slope of E180's D(kind) - D(fadd.ps zeros) on the operand word's popcount
         over E180's 21 one-number fadd.ps kinds, pass by pass, mean over the 6 kept passes with t(0.975, 5). E180's data supports it:
         its interval excludes 0 (the rule below). Applied to each kind's operand popcount pop_O = pop(v) (A's = B's).
  BOTH   E180-O's own two-term fit, POST HOC: D = a + b pop_R + c pop_O over the same kinds and passes (E180-O's c is this c); b and c
         applied together. Reported beside, as the split E180 could not resolve.
  NONE   no difference: 0 for every kind and train.
  OFM    october-forecast-model's arm through its committed reader (E180's dated notes M1 and M2, `arm_m1_e180.py`): M1 froze the model
         for E180's 4s and 5s alone and derives none for any other constant, so it covers T5 (5s - 4s, +0.0041665 W) and nothing else.
         Every other E183 kind and train has no october-forecast-model forecast (E183.md section 8).
The operand arm's rule ("if E180's data supports one"): OPER enters when the operand-only slope's 95% interval over E180's kept passes
lies above 0; else OPER is not an arm and only BOTH is reported. The rule was written after a first look at the fit (this lane's scratch),
so the arm's entry is post hoc, as its fit is.
SPDX-License-Identifier: Apache-2.0
"""
import argparse
import hashlib
import importlib.util
import json
import math
import os
import statistics as st
import sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
CARD = "aifoundry3"
E180D = "tools/claims-v3/e180"
E180DATA = "docs/reports/data/2026-11-06-e180-vector-add-aifoundry3"
# every input: committed, and pinned at the sha256 its own hash list gives
PINNED = {
    f"{E180D}/forecast-e180.json": None,     # SHA256SUMS-e180-registration (read from the list below)
    f"{E180D}/power_e180.py": None,          # SHA256SUMS-e180-registration
    f"{E180D}/arm_m1_e180.py": None,         # SHA256SUMS-e180-m2
    f"{E180D}/m1-october-forecast-model-e180.json": None,   # SHA256SUMS-e180-m1
    f"{E180DATA}/scored-e180.json": None,    # E180's data SHA256SUMS
    f"{E180DATA}/reduced-e180-v3.json": None,  # E180's data SHA256SUMS
    "tools/claims-v3/e183/kinds-e183.json": None,   # this registration (SHA256SUMS-e183-registration)
}
LISTS = {
    f"{E180D}/forecast-e180.json": (f"{E180D}/SHA256SUMS-e180-registration", "tools/claims-v3/e180/forecast-e180.json"),
    f"{E180D}/power_e180.py": (f"{E180D}/SHA256SUMS-e180-registration", "tools/claims-v3/e180/power_e180.py"),
    f"{E180D}/arm_m1_e180.py": (f"{E180D}/SHA256SUMS-e180-m2", "tools/claims-v3/e180/arm_m1_e180.py"),
    f"{E180D}/m1-october-forecast-model-e180.json": (f"{E180D}/SHA256SUMS-e180-m1", "tools/claims-v3/e180/m1-october-forecast-model-e180.json"),
    f"{E180DATA}/scored-e180.json": (f"{E180DATA}/SHA256SUMS", "scored-e180.json"),
    f"{E180DATA}/reduced-e180-v3.json": (f"{E180DATA}/SHA256SUMS", "reduced-e180-v3.json"),
}
ARMS = ("P", "BLIND", "OPER", "BOTH", "NONE")


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def listed(root, lst, name):
    """the sha256 a committed hash list gives for name (its entries are '<sha256>  <path>', the path as the list writes it)"""
    for line in open(os.path.join(root, lst)):
        parts = line.split()
        if len(parts) == 2 and parts[1].lstrip("./") == name.lstrip("./"):
            return parts[0]
    return None


def check_inputs(root):
    got, probs = {}, []
    for rel in PINNED:
        p = os.path.join(root, rel)
        h = sha(p)
        got[rel] = h
        if rel in LISTS:
            lst, name = LISTS[rel]
            want = listed(root, lst, name)
            if want != h:
                probs.append(f"{rel}: sha256 {h[:12]} is not its list's ({lst}: {str(want)[:12]})")
    return got, probs


def load_module(path, name):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def ols2_both(x1, x2, y):
    """(b, c) of y = a + b x1 + c x2 by the normal equations on centred data (power_e180.ols2's own algebra; it returns c alone)"""
    n = len(y)
    m1, m2, my = sum(x1) / n, sum(x2) / n, sum(y) / n
    a11 = sum((u - m1) ** 2 for u in x1)
    a22 = sum((v - m2) ** 2 for v in x2)
    a12 = sum((u - m1) * (v - m2) for u, v in zip(x1, x2))
    b1 = sum((u - m1) * (w - my) for u, w in zip(x1, y))
    b2 = sum((v - m2) * (w - my) for v, w in zip(x2, y))
    det = a11 * a22 - a12 * a12
    return (a22 * b1 - a12 * b2) / det, (a11 * b2 - a12 * b1) / det


def r(x, n=10):
    return None if x is None else round(x, n)


def build(root):
    inputs, probs = check_inputs(root)
    if probs:
        raise SystemExit("an input differs from its committed hash list:\n  " + "\n  ".join(probs))
    pw = load_module(os.path.join(root, E180D, "power_e180.py"), "power_e180")
    arm = load_module(os.path.join(root, E180D, "arm_m1_e180.py"), "arm_m1_e180")
    fc = json.load(open(os.path.join(root, E180D, "forecast-e180.json")))
    sc = json.load(open(os.path.join(root, E180DATA, "scored-e180.json")))
    red = json.load(open(os.path.join(root, E180DATA, "reduced-e180-v3.json")))
    m1 = json.load(open(os.path.join(root, E180D, "m1-october-forecast-model-e180.json")))
    kd = json.load(open(os.path.join(root, "tools/claims-v3/e183/kinds-e183.json")))
    K180 = fc["kinds"]
    # ---- P: E180's ladder slope, and E180's own P per reused kind as the check
    slope_P = fc["ladder"]["slope_W_per_bit"]["P"]
    slope_C = fc["ladder"]["slope_W_per_bit"]["C"]
    slope_E = fc["ladder"]["slope_W_per_bit"]["E"]
    p_checks = {}
    for nm, k in kd["kinds"].items():
        if nm in K180:
            mine = slope_P * k["result_popcount"]
            theirs = K180[nm]["W"][CARD]["P"]
            p_checks[nm] = {"e180_P_W": theirs, "slope_times_popcount_W": r(mine, 12), "abs_diff_W": abs(mine - theirs)}
            if abs(mine - theirs) > 2e-9:
                raise SystemExit(f"P for {nm}: E180's {theirs} differs from slope x popcount {mine}")
    # ---- BLIND: E180-L, blind on 6 Nov
    L = sc["rules"]["E180-L"]
    blind = {"mean": L["mean"], "lo": L["lo"], "hi": L["hi"], "x_by_pass": L["x"], "verdict_e180": L["verdict"]}
    # ---- the post hoc fits on E180's committed reduction (the 21 one-number fadd.ps kinds, the 6 kept passes)
    ladder = fc["ladder"]["kinds"]
    xres = [K180[n]["result_popcount"] for n in ladder]
    xop = [K180[n]["operand_popcount"] for n in ladder]
    passes = sorted(red["passes"])
    if passes != sc["kept_passes"]:
        raise SystemExit("the reduction's passes are not the scorer's kept passes")
    s_res, s_op, b2, c2 = [], [], [], []
    for p in passes:
        D = red["passes"][p]["D"]
        y = [D[n] - D["fadd.ps/zeros"] for n in ladder]
        s_res.append(pw.ols(xres, y))
        s_op.append(pw.ols(xop, y))
        bb, cc = ols2_both(xres, xop, y)
        if abs(cc - pw.ols2(xres, xop, y)) > 1e-12:
            raise SystemExit("the two-term c differs from power_e180.ols2's")
        b2.append(bb)
        c2.append(cc)
    def iv(xs):
        m, lo, hi = pw.interval(xs)
        return {"mean": m, "lo": lo, "hi": hi, "x_by_pass": xs}
    fit_res, fit_op, fit_b, fit_c = iv(s_res), iv(s_op), iv(b2), iv(c2)
    for got, want, what in ((fit_res["mean"], L["mean"], "E180-L"), (fit_c["mean"], sc["rules"]["E180-O"]["mean"], "E180-O")):
        if abs(got - want) > 1e-12:
            raise SystemExit(f"the re-made {what} {got} differs from the committed {want}")
    # each one-term fit's residual rms over the kinds' means (the mean over the kept passes of D(kind) - D(zeros)), n - 2 df
    kmean = [st.mean(red["passes"][p]["D"][n] - red["passes"][p]["D"]["fadd.ps/zeros"] for p in passes) for n in ladder]
    rms = {}
    for tag, xs in (("result_only", xres), ("operand_only", xop)):
        sl = pw.ols(xs, kmean)
        a0 = st.mean(kmean) - sl * st.mean(xs)
        rms[tag] = math.sqrt(sum((y - a0 - sl * x) ** 2 for x, y in zip(xs, kmean)) / (len(xs) - 2))
    mx, my = st.mean(xres), st.mean(xop)
    corr = (sum((a - mx) * (b - my) for a, b in zip(xres, xop)) /
            math.sqrt(sum((a - mx) ** 2 for a in xres) * sum((b - my) ** 2 for b in xop)))
    oper_enters = fit_op["lo"] > 0
    # ---- OFM: the committed reader's frozen values (its own check first)
    arm.check_pinned()          # the reader's own check of its pinned inputs and of M1's values (raises if either differs)
    arm_ok = "check_pinned passed"
    ofm_5m4 = arm.M1_EXPECT_W["5s_minus_4s"]
    if abs(m1["arm"]["model_above_zeros_fJ"]["5s_minus_4s"] * 1e-15 * arm.M1_EXPECT_RATE - ofm_5m4) > 1e-12:
        raise SystemExit("M1's 5s - 4s in fJ at M1's rate is not the reader's pinned watts")
    ofm = {"T5": ofm_5m4, "fadd.ps/f_4": arm.M1_EXPECT_W["4s"], "fadd.ps/f_5": arm.M1_EXPECT_W["5s"]}

    def lines(pr, po):
        """an arm's (b, c) per result bit and per operand bit"""
        return pr, po

    coef = {"P": (slope_P, 0.0), "BLIND": (blind["mean"], 0.0), "OPER": (0.0, fit_op["mean"]),
            "BOTH": (fit_b["mean"], fit_c["mean"]), "NONE": (0.0, 0.0)}
    kinds = {}
    for nm, k in kd["kinds"].items():
        pR, pO = k["result_popcount"], k["operand_popcount"]
        W = {a: coef[a][0] * pR + coef[a][1] * pO for a in ARMS}
        rec = {"word": k["word"], "result_word": k["result_word"], "result_popcount": pR, "operand_popcount": pO,
               "W": {a: r(v) for a, v in W.items()},
               "BLIND_band_W": [r(blind["lo"] * pR), r(blind["hi"] * pR)], "C_W": r(slope_C * pR), "E_W": r(slope_E * pR),
               "OFM_W": r(ofm.get(nm)), "note": "watts above the fadd.ps zeros; BOTH's intercept a is left out (a difference cancels it)"}
        kinds[nm] = rec
    trains = {}
    for t in kd["trains"]:
        dR, dO = t["dR"], t["dO"]
        W = {a: coef[a][0] * dR + coef[a][1] * dO for a in ARMS}
        trains[t["train"]] = {"pair": t["pair"], "first": t["first"], "second": t["second"], "dR": dR, "dO": dO,
                              "W": {a: r(v) for a, v in W.items()},
                              "BLIND_band_W": sorted([r(blind["lo"] * dR), r(blind["hi"] * dR)]),
                              "OPER_band_W": sorted([r(fit_op["lo"] * dO), r(fit_op["hi"] * dO)]),
                              "C_W": r(slope_C * dR), "E_W": r(slope_E * dR), "OFM_W": r(ofm.get(t["train"]))}
    # what each arm says the two prices (E183-B's b per result bit, E183-C's c per operand bit) read
    prices = {a: {"b_W_per_result_bit": r(coef[a][0]), "c_W_per_operand_bit": r(coef[a][1])} for a in ARMS}
    out = {"_what": "E183's frozen forecasts (forecast_e183.py; E183.md section 4): watts above the fadd.ps zeros for every kind and "
                    "D(first) - D(second) for every train, on aifoundry3 card 0 at 600 MHz pinned",
           "card": CARD, "inputs_sha256": inputs, "arms": list(ARMS),
           "labels": {"P": "registered in E180 (4dc5035f), frozen; E180's primary, not M10 (M10 prices no vector add)",
                      "BLIND": "E180's measured price E180-L (blind on 6 Nov 2026, c8a3a6ee): the blind number for E183",
                      "OPER": "post hoc for its fit (E180's committed reduction, read after E180's data); a forecast for E183",
                      "BOTH": "post hoc for its fit (E180-O's two-term regression); reported beside",
                      "NONE": "no difference", "OFM": "october-forecast-model (E180's dated note M1, its reader arm_m1_e180.py): T5 only"},
           "P_slope_W_per_result_bit": slope_P, "C_slope_W_per_result_bit": slope_C, "E_slope_W_per_result_bit": slope_E,
           "P_check_against_e180": p_checks, "BLIND": blind,
           "posthoc_fits_e180": {"kinds": ladder, "corr_result_operand_popcounts": corr, "result_only": fit_res,
                                 "operand_only": fit_op, "two_term_b": fit_b, "two_term_c": fit_c,
                                 "rms_W_on_kind_means": {"what": "each one-term OLS fit to the 21 kinds' mean D above zeros, its "
                                                         "residual rms (n - 2 df)", **rms},
                                 "rule_oper_enters": "the operand-only slope's 95% interval lies above 0", "oper_enters": oper_enters},
           "OFM": {"freeze_line": m1["freeze_line_e180"], "covers": ["T5 (5s - 4s)", "fadd.ps/f_4 and fadd.ps/f_5 above zeros"],
                   "values_W": ofm, "reader_check": arm_ok, "rate": arm.M1_EXPECT_RATE},
           "prices": prices, "kinds": kinds, "trains": trains}
    if not oper_enters:
        out["prices"].pop("OPER")
    return out


def text(d):
    L = ["E183 forecasts (forecast_e183.py), aifoundry3 card 0, 600 MHz pinned. W above the fadd.ps zeros (kinds) and D(first) - D(second)",
         "(trains). P: E180's frozen primary. BLIND: E180-L, +0.009693 W a result 1-bit [+0.002734, +0.016652]. OPER: operand-only, post",
         "hoc fit on E180. BOTH: E180-O's two-term fit, post hoc. OFM: october-forecast-model, T5 only.", ""]
    f = d["posthoc_fits_e180"]
    L.append(f"E180's 21 kinds: corr(pop_R, pop_O) {f['corr_result_operand_popcounts']:.4f}")
    for k in ("result_only", "operand_only", "two_term_b", "two_term_c"):
        v = f[k]
        L.append(f"  {k:<13} {v['mean']:+.6f} W a bit [{v['lo']:+.6f}, {v['hi']:+.6f}]")
    L.append(f"  one-term fits' residual rms over the kinds' means: result-only {f['rms_W_on_kind_means']['result_only']:.4f} W, "
             f"operand-only {f['rms_W_on_kind_means']['operand_only']:.4f} W")
    L.append(f"  OPER enters (its interval above 0): {f['oper_enters']}")
    L.append("")
    L.append(f"{'train':<6}{'pair':<5}{'first':<16}{'second':<16}{'dR':>4}{'dO':>4}{'P':>10}{'BLIND':>10}{'band':>22}{'OPER':>10}"
             f"{'BOTH':>10}{'OFM':>10}")
    for t, v in d["trains"].items():
        W = v["W"]
        band = f"[{v['BLIND_band_W'][0]:+.4f}, {v['BLIND_band_W'][1]:+.4f}]"
        ofm = f"{v['OFM_W']:+.5f}" if v["OFM_W"] is not None else "-"
        L.append(f"{t:<6}{v['pair']:<5}{v['first'][8:]:<16}{v['second'][8:]:<16}{v['dR']:>+4d}{v['dO']:>+4d}{W['P']:>+10.4f}"
                 f"{W['BLIND']:>+10.4f}{band:>22}{W['OPER']:>+10.4f}{W['BOTH']:>+10.4f}{ofm:>10}")
    L.append("")
    L.append(f"{'kind':<16}{'word':<12}{'pop_O':>6}{'pop_R':>6}{'P':>10}{'BLIND':>10}{'OPER':>10}{'BOTH':>10}{'OFM':>10}")
    for n, v in d["kinds"].items():
        W = v["W"]
        ofm = f"{v['OFM_W']:+.5f}" if v["OFM_W"] is not None else "-"
        L.append(f"{n[8:]:<16}{v['word']:<12}{v['operand_popcount']:>6d}{v['result_popcount']:>6d}{W['P']:>+10.4f}{W['BLIND']:>+10.4f}"
                 f"{W['OPER']:>+10.4f}{W['BOTH']:>+10.4f}{ofm:>10}")
    L.append("")
    L.append("What each arm says E183-B (b, W per result bit) and E183-C (c, W per operand bit) read:")
    for a, v in d["prices"].items():
        L.append(f"  {a:<6} b {v['b_W_per_result_bit']:+.6f}   c {v['c_W_per_operand_bit']:+.6f}")
    return "\n".join(L) + "\n"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", required=True)
    ap.add_argument("--out", default=None)
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args()
    root = os.path.abspath(a.root)
    d = build(root)
    js = json.dumps(d, indent=1, sort_keys=True) + "\n"
    tx = text(d)
    out = a.out or HERE
    if a.check:
        ok = (open(os.path.join(HERE, "forecast-e183.json")).read() == js and open(os.path.join(HERE, "forecast-e183.txt")).read() == tx)
        print("CHECK PASS" if ok else "CHECK FAIL")
        sys.exit(0 if ok else 1)
    open(os.path.join(out, "forecast-e183.json"), "w").write(js)
    open(os.path.join(out, "forecast-e183.txt"), "w").write(tx)
    sys.stdout.write(tx)


if __name__ == "__main__":
    main()
