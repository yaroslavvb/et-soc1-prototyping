#!/usr/bin/env python3
"""Q143(k): M11's dated amendment A4 (tools/claims-v3/m11/REGISTRATION.md.dated-note-A4.md), design only: HM-CAL-I8, the int8
pair's own line read on the later int8 hold, at the registered hold design, on v2's committed draws. No fit of any M11 term, no
hold, no card: it reads committed files and prints.

What HM-CAL-I8 is (A4-1): in each aifoundry3 M11 session, the line e = a + g P through the session's two int8 holds of distinct rise,
L1 (int8.full) and S (int8.neg_ones), is read on its later int8 hold L2 (int8.full), blind given the watts: e_c(L2) = e(L2) - a - g P(L2).
Pooled over the read sessions' L2 holds (n_L, 2 at the plan), D = rms(e_c) - rms(e) reads BETTER if D <= -sigma_c / sqrt(n_L), WORSE if
D >= +sigma_c / sqrt(n_L), else NOT RESOLVED. It never reads H_E or Z, so it stands where A2's pair (fp32, duty-cycled H_E) does not
share the int8 holds' line: REGISTRATION.md section 0.1's case, H_E read by the chain as E144's H_H was (A3-1, A3-2).

What it reads, each checked first (paths relative to the repository's top directory, argv[1]):
  tools/claims-v3/m11/SHA256SUMS-m11 (6), SHA256SUMS-a1 (9), SHA256SUMS-a2 (7) and SHA256SUMS-a3 (7), every file they list; through
  design_power_heat.check_inputs the ten inputs SHA256SUMS lists. design_power_heat_a3 is imported unchanged (it imports
  design_power_heat_a2, which imports design_power_heat_v2, which imports design_power_heat, each unchanged). The committed outputs it
  compares against: design-power-heat-a3.json, design-power-heat-a2.json and design-power-heat-v2.json.

The draws are v2's committed draws: random.Random("M11-HM-LG|<design>|<sigma>|<truth>") and design_power_heat.sim_sessions, 5,000
draws a cell, a premise failure added after the draw exactly as A2's section 5 and A3's section 6 add it. Its check line confirms it: on
every cell that A2 or A3 committed, HM-LG's verdicts, HM-CAL's verdicts, A2-3's outcome at the exact t point and HM-E144's REPEATS share
equal the committed figures.

What it prints (and writes as JSON to argv[2] when given):
  0. the checks of the hash lists and inputs;
  1. the plan's int8 pair, its span, L2's place w in it, and the floor if the premise holds;
  2. synthetic sessions for A4-1's read rule (the scorer's reference cases);
  3. at the plan (two aifoundry3 sessions), sigma_c and 1.5 sigma, every committed truth, the premise holding and section 0.1's case
     (H_E read by the chain): HM-CAL-I8's verdicts, N1-I8, its entry route's outcome beside A1-4's and A2's, and the rms over L2;
  4. A2's and A3's other premise rows (truth none, a 3.2% gain, E154's fit then E166's; sigma_c);
  5. one and three aifoundry3 sessions (sigma_c), the premise holding and section 0.1's case;
  6. the adoption rule of A4-6, read mechanically.

    python3 -E -B tools/claims-v3/m11/design_power_heat_a4.py . tools/claims-v3/m11/design-power-heat-a4.json > tools/claims-v3/m11/design-power-heat-a4.txt

Python 3.9 with numpy 1.26 (numpy through Q138(t)'s frozen chain; on the Intel numpy is in the user site, so -E, not -I).
SPDX-License-Identifier: Apache-2.0
"""
import hashlib
import json
import math
import os
import random
import sys

TOP = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else ".")
OUT_JSON_A4 = sys.argv[2] if len(sys.argv) > 2 and not sys.argv[2].startswith("--") else None
DEV_DRAWS = None
if "--dev-draws" in sys.argv:                       # development runs only (scratch); the committed run never passes it
    DEV_DRAWS = int(sys.argv[sys.argv.index("--dev-draws") + 1])
sys.dont_write_bytecode = True
HERE = os.path.join(TOP, "tools", "claims-v3", "m11")
P = print


def sha(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def hash_list(name):
    out = {}
    for line in open(os.path.join(HERE, name)):
        parts = line.split()
        if len(parts) == 2:
            out[parts[1]] = parts[0]
    return out


LISTS = {}
for _name in ("SHA256SUMS-m11", "SHA256SUMS-a1", "SHA256SUMS-a2", "SHA256SUMS-a3"):
    _l = hash_list(_name)
    _bad = [rel for rel, s in _l.items() if sha(os.path.join(TOP, rel)) != s]
    LISTS[_name] = {"entries": len(_l), "differ": _bad}
    if _bad:
        P(f"STOP: {', '.join(_bad)} differ from tools/claims-v3/m11/{_name}")
        sys.exit(3)

_saved_argv = list(sys.argv)
sys.argv = [os.path.join(HERE, "design_power_heat_a3.py"), TOP]    # A3 reads argv at import; its main() never runs here
sys.path.insert(0, HERE)
import design_power_heat_a3 as A3  # noqa: E402  (A3, unchanged; it checks -m11, -a1 and -a2 and imports A2, v2 and v1 unchanged)
sys.argv = _saved_argv

A2, V2, D, DPG = A3.A2, A3.V2, A3.D, A3.DPG
DRAWS = DEV_DRAWS or A3.DRAWS                       # 5,000: v2's committed draws (A3 imported without --dev-draws)
A3X1, A3X2, A3X3 = A3.A3X1, A3.A3X2, A3.A3X3
A3_OUT_REL = "tools/claims-v3/m11/design-power-heat-a3.json"
MIXED = A3.MIXED
ENTERS_A2 = A3.ENTERS                               # "the calibration enters" (A2-3)
NAMES = A3.NAMES["aifoundry3"]                      # H_E, Z, L1, S, L2 in section 5's order
HE_CHAIN = "H_E read by the chain (e(H_E) = noise only)"

# ------------------------------------------------------------------------------------- A4-1: HM-CAL-I8, as registered
I8_PAIR = ("L1", "S")      # the int8 pair: int8.full and int8.neg_ones on E97's natural chain, by hold name
I8_LATER = ("L2",)         # the later int8 hold, by hold name: one a session
I8_MIN_SPAN_C = 3.0        # the pair spans at least 3.0 C of P (A4-1: L2 is read inside the span, so its noise depends on w only)
I8_VERDICTS = ("BETTER", "NOT RESOLVED", "WORSE", "NOT SCORED")
ENTERS_I8 = "HM-CAL-I8 enters"
I8_OUTCOMES = ("A1-4's common term", "A2's calibration", ENTERS_I8, "nothing from A4: HM-E144 DOES NOT REPEAT",
               "nothing from A4: the int8 holds' misses read as noise (E4')",
               "nothing from A4: HM-LG reads no miss (NOT SCORED, or NOT SEPARATED with its null not rejected)",
               "nothing from A4: HM-CAL-I8 NOT RESOLVED", "nothing from A4: HM-CAL-I8 WORSE", "nothing from A4: HM-CAL-I8 NOT SCORED",
               "nothing from A4: N1-I8, a session worse on its own (a reported arm)", "nothing from A4: one session (a candidate)")


def rms(v):
    return math.sqrt(sum(x * x for x in v) / len(v))


def cal_i8_by_name(named, sigma_c, order_ok=True):
    """A4-1 read by hold name. named = {hold name: (P, e)} over the session's SCORED holds (a hold not scored is absent); order_ok
    False when L1 or S did not end before L2's first launch (the launch records' times). Returns (reading, None) or (None, the
    reason the session reads NOT SCORED)."""
    for nm in I8_PAIR + I8_LATER:
        if nm not in named:
            return None, f"{nm} is not scored"
    if not order_ok:
        return None, "L1 and S did not both end before L2's first launch"
    (p1, e1), (p2, e2), (p3, e3) = named["L1"], named["S"], named["L2"]
    span = abs(p1 - p2)
    if span < I8_MIN_SPAN_C:
        return None, f"the pair spans {span:.3f} C of P, under {I8_MIN_SPAN_C} C"
    lo, hi = min(p1, p2), max(p1, p2)
    if not lo <= p3 <= hi:
        return None, f"L2's P {p3:.3f} C lies outside the pair's span [{lo:.3f}, {hi:.3f}] C"
    g = (e1 - e2) / (p1 - p2)
    a = e2 - g * p2
    ec = e3 - a - g * p3
    d = abs(ec) - abs(e3)
    return {"a": a, "g": g, "w": (p3 - p2) / (p1 - p2), "span": span, "e1": e1, "e2": e2, "eu": e3, "ec": ec, "d": d,
            "worse_alone": d >= sigma_c / math.sqrt(1.0)}, None


def hm_cal_i8(sessions, sigma_c):
    """HM-CAL-I8 over a card kind's sessions: sessions = {key: (named, order_ok)}. The pooled D over the read sessions' L2 holds, its
    verdict at sigma_c / sqrt(n_L), and clause N1-I8"""
    per = {}
    for k, (named, ok) in sessions.items():
        r, why = cal_i8_by_name(named, sigma_c, ok)
        per[k] = r if r is not None else {"not_scored": why}
    read = {k: v for k, v in per.items() if "not_scored" not in v}
    if not read:
        return {"verdict": "NOT SCORED", "k": 0, "per": per}
    eu = [v["eu"] for v in read.values()]
    ec = [v["ec"] for v in read.values()]
    ru, rc = rms(eu), rms(ec)
    tau = sigma_c / math.sqrt(len(eu))
    dd = rc - ru
    verdict = "BETTER" if dd <= -tau else "WORSE" if dd >= tau else "NOT RESOLVED"
    return {"verdict": verdict, "k": len(read), "n_L": len(eu), "tau": tau, "D": dd, "rms_u": ru, "rms_c": rc, "per": per,
            "N1": any(v["worse_alone"] for v in read.values())}


def chi2_ppf(q, nu):
    """the q point of chi-square at nu degrees of freedom, by bisection on the regularized lower incomplete gamma (its series)"""
    def cdf(x):
        a, x2 = nu / 2.0, x / 2.0
        if x2 <= 0.0:
            return 0.0
        term = 1.0 / a
        tot = term
        for i in range(1, 2000):
            term *= x2 / (a + i)
            tot += term
            if term < tot * 1e-17:
                break
        return math.exp(a * math.log(x2) - x2 - math.lgamma(a)) * tot
    lo, hi = 0.0, 10.0 * nu + 100.0
    for _ in range(200):
        mid = 0.5 * (lo + hi)
        if cdf(mid) < q:
            lo = mid
        else:
            hi = mid
    return 0.5 * (lo + hi)


CHI2_95 = {3 * k: chi2_ppf(0.95, 3 * k) for k in (1, 2, 3)}


def misses_differ_first(lg):
    """E4 as first fixed (12:02:52 PST), printed beside, never the rule: HM-LG says the chain's misses differ from zero (GAIN, LEVEL or
    BOTH; or NOT SEPARATED with its null rejected)"""
    v = lg["verdict"]
    return v in ("GAIN", "LEVEL", "BOTH") or (v == "NOT SEPARATED" and lg.get("null") == "they differ, the form unresolved")


def int8_misses(i8, sigma_c):
    """E4' (registered, revision 1): the chain misses the int8 holds: X2 = sum over the read sessions' L1, S and L2 of (e / sigma_c)^2
    above chi-square's 95% point at 3k degrees of freedom (k read sessions). It reads no fp32 hold. (X2, the point, the verdict)"""
    read = [v for v in i8["per"].values() if "not_scored" not in v]
    if not read:
        return None, None, False
    x2 = sum((v["e1"] ** 2 + v["e2"] ** 2 + v["eu"] ** 2) / sigma_c ** 2 for v in read)
    pt = CHI2_95.get(3 * len(read)) or chi2_ppf(0.95, 3 * len(read))
    return x2, pt, x2 > pt


def i8_entry(a14_outcome, a2_outcome, repeats, lg, i8, sigma_c, first=False):
    """A4-3: what M11 carries for heat over minutes on aifoundry3, with A4 beside A1-4's path and A2-3 (the order: A1-4, A2, A4).
    first=True reads E4 as first fixed (HM-LG's reading), printed beside; the registered route reads E4' (int8_misses)."""
    if a14_outcome in A2.COMMON_OUTCOMES:
        return "A1-4's common term"
    if a2_outcome == ENTERS_A2:
        return "A2's calibration"
    if not repeats:
        return "nothing from A4: HM-E144 DOES NOT REPEAT"
    if first:
        if not misses_differ_first(lg):
            return "nothing from A4: HM-LG reads no miss (NOT SCORED, or NOT SEPARATED with its null not rejected)"
    elif not int8_misses(i8, sigma_c)[2]:
        return "nothing from A4: the int8 holds' misses read as noise (E4')"
    if i8["verdict"] != "BETTER":
        return "nothing from A4: HM-CAL-I8 " + i8["verdict"]
    if i8["N1"]:
        return "nothing from A4: N1-I8, a session worse on its own (a reported arm)"
    if i8["k"] < 2:
        return "nothing from A4: one session (a candidate)"
    return ENTERS_I8


def floor_i8(design, sigma_c):
    """the blind rms the calibrated L2 holds would read if the premise held exactly on the int8 holds: sigma_c * sqrt(mean over the
    sessions of 1 + (1 - w)^2 + w^2), w = (P_L2 - P_S) / (P_L1 - P_S), the two-point line's own noise carried to L2 (A2-2's formula)"""
    f = []
    for ps in design:
        nm = dict(zip(NAMES, ps))
        w = (nm["L2"] - nm["S"]) / (nm["L1"] - nm["S"])
        f.append(1.0 + (1.0 - w) ** 2 + w * w)
    return sigma_c * math.sqrt(sum(f) / len(f))


def he_chain_extra(design, tr):
    """A3's section-6 row: H_E read by the chain, e(H_E) its noise only (minus the truth's a + g P(H_E) in each session)"""
    return [[-(tr[i % len(tr)][0] + tr[i % len(tr)][1] * des_i[0]), 0, 0, 0, 0] for i, des_i in enumerate(design)]


# ------------------------------------------------------------------------------------- one cell
def run_cell_a4(design, truth, sigma, seed, sigma_c, gamma_arm, extra=None):
    """one cell on v2's committed draws: random.Random(f"M11-HM-LG|{seed}|{sigma:.4f}|{label}") and sim_sessions, DRAWS draws;
    extra None, one list per hold (added to every session) or one such list per session, added after the draw (A2 section 5, A3
    section 6). Returns the cell: A1-4's, A2's (at the exact t point) and HM-E144's readings, as A3 reads them, and A4's."""
    lab, tr = truth
    k = len(design)
    n = sum(len(s) for s in design)
    crit = DPG.f_ppf(0.95, k - 1, n - 2 * k) if k >= 2 else None
    crit_b = DPG.f_ppf(0.95, 2 * (k - 1), n - 2 * k) if k >= 2 else None
    rng = random.Random(f"M11-HM-LG|{seed}|{sigma:.4f}|{lab}")
    per_session_extra = extra is not None and len(extra) > 0 and isinstance(extra[0], (list, tuple))
    verd = {x: 0 for x in A2.VERDICTS}
    a14 = {o: 0 for o in V2.OUTCOMES}
    cal_v = {x: 0 for x in A2.CAL_VERDICTS}
    a2_out = {e: 0 for e in A2.ENTRIES}
    rep_all = 0
    i8_v = {x: 0 for x in I8_VERDICTS}
    i8_n1 = 0
    out_i8 = {o: 0 for o in I8_OUTCOMES}
    out_first = {o: 0 for o in I8_OUTCOMES}
    e4p = 0
    joint = {}
    r_u, r_c, r_a2, r_arm, d_i8 = [], [], [], [], []
    r_c_ent, r_u_ent, r_any_ent = [], [], []
    for _ in range(DRAWS):
        groups = D.sim_sessions(design, tr, sigma, rng)
        if extra is not None:
            if per_session_extra:
                groups = {i: [(p, e + x) for (p, e), x in zip(pts, extra[i])] for i, pts in groups.items()}
            else:
                groups = {i: [(p, e + x) for (p, e), x in zip(pts, extra)] for i, pts in groups.items()}
        res = DPG.lg_test(groups, min_tiles=D.MIN_HOLDS, min_span_w=D.MIN_SPAN_C, min_df=D.MIN_DF, detail=True)
        verd[res["verdict"]] += 1
        o, _ = V2.decide(groups, res, k, n, crit, crit_b, sigma_c)
        a14[o] += 1
        c = A2.hm_cal(groups, "both", sigma_c)
        cal_v[c["verdict"]] += 1
        deps_x = [A3.he_departs_exact(pts) for pts in groups.values()]
        he_dep_x = all(x for x in deps_x if x is not None) and any(x is not None for x in deps_x)
        e2 = A2.a2_entry(o, c, he_dep_x)
        a2_out[e2] += 1
        rep = all(abs(pts[0][1]) / (pts[0][0] + pts[0][1]) <= A3.E144_LINE for pts in groups.values())
        rep_all += rep
        i8 = hm_cal_i8({i: (dict(zip(NAMES, pts)), True) for i, pts in groups.items()}, sigma_c)
        i8_v[i8["verdict"]] += 1
        i8_n1 += bool(i8.get("N1"))
        oi = i8_entry(o, e2, rep, res, i8, sigma_c)
        out_i8[oi] += 1
        out_first[i8_entry(o, e2, rep, res, i8, sigma_c, first=True)] += 1
        e4p += bool(i8["verdict"] != "NOT SCORED" and int8_misses(i8, sigma_c)[2])
        jk = f"A2 {'enters' if e2 == ENTERS_A2 else 'does not enter'} | HM-E144 {'REPEATS' if rep else 'DOES NOT REPEAT'} | HM-CAL-I8 {i8['verdict']}"
        joint[jk] = joint.get(jk, 0) + 1
        if i8["verdict"] != "NOT SCORED":
            r_u.append(i8["rms_u"])
            r_c.append(i8["rms_c"])
            d_i8.append(i8["D"])
            l2 = [pts[4] for pts in groups.values()]
            r_arm.append(rms([e - gamma_arm * p for p, e in l2]))
            if c["verdict"] != "NOT SCORED":
                a2l2 = []
                for pts in groups.values():
                    (p1, e1), (p2, e2_) = pts[0], pts[1]
                    g = (e1 - e2_) / (p1 - p2)
                    a = e2_ - g * p2
                    a2l2.append(pts[4][1] - a - g * pts[4][0])
                r_a2.append(rms(a2l2))
            if oi == ENTERS_I8:
                r_c_ent.append(i8["rms_c"])
                r_u_ent.append(i8["rms_u"])
        if oi == ENTERS_I8:
            r_any_ent.append(i8["rms_c"])
        elif oi == "A2's calibration":
            r_any_ent.append(c["rms_c"])
    pct, summ = A2.pct, A2.summ
    return {"HM_LG_verdicts": {x: pct(v, DRAWS) for x, v in verd.items()},
            "A1_4_carries": {x: pct(v, DRAWS) for x, v in a14.items() if v},
            "HM_CAL_both": {x: pct(v, DRAWS) for x, v in cal_v.items()},
            "A2_3_outcome_exact_t": {x: pct(v, DRAWS) for x, v in a2_out.items() if v},
            "HM_E144_repeats": pct(rep_all, DRAWS),
            "HM_CAL_I8": {x: pct(v, DRAWS) for x, v in i8_v.items()},
            "N1_I8_met": pct(i8_n1, DRAWS),
            "with_A4_M11_carries": {x: pct(v, DRAWS) for x, v in out_i8.items() if v},
            "E4p_int8_misses_read": pct(e4p, DRAWS),
            "route_as_first_fixed_with_E4_HM_LG": {x: pct(v, DRAWS) for x, v in out_first.items() if v},
            "a_per_session_calibration_enters_as_first_fixed": pct(out_first["A2's calibration"] + out_first[ENTERS_I8], DRAWS),
            "a_per_session_calibration_enters": pct(out_i8["A2's calibration"] + out_i8[ENTERS_I8], DRAWS),
            "a_term_carried_A1_4_A2_or_A4": pct(out_i8["A1-4's common term"] + out_i8["A2's calibration"] + out_i8[ENTERS_I8], DRAWS),
            "joint_A2_HM_E144_HM_CAL_I8": {kk: pct(v, DRAWS) for kk, v in sorted(joint.items())},
            "rms_L2_C": {"chain_unscaled": summ(r_u), "I8_calibrated": summ(r_c), "A2_calibrated_on_L2": summ(r_a2),
                         "x1p032_arm": summ(r_arm), "I8_calibrated_when_it_enters": summ(r_c_ent),
                         "chain_unscaled_when_I8_enters": summ(r_u_ent),
                         "stated_error_when_a_per_session_calibration_enters": summ(r_any_ent)},
            "D_I8_C": summ(d_i8), "draws": DRAWS}


def line4(lab, cell):
    h = cell["HM_CAL_I8"]
    r = cell["rms_L2_C"]
    car = cell["with_A4_M11_carries"]
    s = (f"     {lab:52s} I8 " + " / ".join(f"{h[x]:5.1f}" for x in I8_VERDICTS[:3]) + f" | N1-I8 {cell['N1_I8_met']:4.1f}"
         + f" | E144 rep {cell['HM_E144_repeats']:5.1f} | A1-4 common {car.get(I8_OUTCOMES[0], 0.0):5.1f}  A2 enters "
         f"{car.get(I8_OUTCOMES[1], 0.0):5.1f}  I8 enters {car.get(ENTERS_I8, 0.0):5.1f}  (a per-session calibration "
         f"{cell['a_per_session_calibration_enters']:5.1f}; as first fixed {cell['a_per_session_calibration_enters_as_first_fixed']:5.1f})")
    if r["chain_unscaled"]:
        s += (f" | L2 rms: unscaled {r['chain_unscaled']['median']:.3f}  I8 {r['I8_calibrated']['median']:.3f} "
              f"[{r['I8_calibrated']['p05']:.3f}, {r['I8_calibrated']['p95']:.3f}]")
    if r["I8_calibrated_when_it_enters"]:
        s += (f"  when I8 enters {r['I8_calibrated_when_it_enters']['median']:.3f} (unscaled "
              f"{r['chain_unscaled_when_I8_enters']['median']:.3f})")
    return s


def same_cell(cell, a2form, a3x, tag):
    """the cell's A1-4 / A2 / HM-E144 readings against the committed A2 and A3 figures for the same draws; a list of differences"""
    dif = []
    if a2form is not None:
        if cell["HM_LG_verdicts"] != a2form["HM_LG_verdicts"]:
            dif.append(f"{tag}: HM-LG verdicts")
        if cell["HM_CAL_both"] != a2form["HM_CAL"]["both"]:
            dif.append(f"{tag}: HM-CAL verdicts")
        com = {o: x for o, x in a2form["A1_4_carries"].items()}
        if cell["A1_4_carries"] != com:
            dif.append(f"{tag}: A1-4's path")
    if a3x is not None:
        if cell["A2_3_outcome_exact_t"] != a3x["exact_t"]["with_A2_M11_carries"]:
            dif.append(f"{tag}: A2-3's outcome at the exact t point")
        if a3x.get("HM_E144") and cell["HM_E144_repeats"] != a3x["HM_E144"]["repeats_in_every_session"]:
            dif.append(f"{tag}: HM-E144 REPEATS")
    return dif


# ------------------------------------------------------------------------------------- main
def main():
    a3c = json.load(open(os.path.join(TOP, A3_OUT_REL)))
    a2c = json.load(open(os.path.join(TOP, A3.A2_OUT_REL)))
    v2 = json.load(open(os.path.join(TOP, A2.V2_OUT_REL)))
    OUT = {"_note": "Q143(k): M11's dated amendment A4, design only (no fit of any M11 term, no hold, no card); printed by "
                    "design_power_heat_a4.py", "draws": DRAWS, "dev_draws": DEV_DRAWS}
    checks = {}
    P("M11's heat registration (Q142(h)), dated amendment A4 (Q143(k)): HM-CAL-I8, the int8 pair's own line (L1 and S) read on the "
      "later int8 hold L2, on v2's committed draws (design only: no fit of any M11 term, no hold, no card)")
    if DEV_DRAWS:
        P(f"DEVELOPMENT RUN: {DEV_DRAWS} draws a cell (the first {DEV_DRAWS} of the committed draws); never committed")
    P()
    P("0. Checked first: " + "; ".join(f"tools/claims-v3/m11/{k} {v['entries']} of {v['entries']} OK" for k, v in LISTS.items()))
    rows, bad = D.check_inputs()
    for rel, s, st in rows:
        P(f"   {s}  {rel}  [{st}]")
    if bad:
        P("   STOP: an input differs from tools/claims-v3/m11/SHA256SUMS: " + ", ".join(bad))
        sys.exit(3)
    OUT["checked_first"] = {"lists": LISTS, "inputs": [{"path": rel, "sha256": s, "check": st} for rel, s, st in rows]}
    nz = D.noise()
    s3 = nz["a3"]["sigma_C"]
    checks["noise as committed (A2)"] = round(s3, 12) == round(a2c["noise_sigma_C"]["aifoundry3"], 12)
    truths = V2.truths_as_committed()
    TR = dict(truths)
    gamma_arm = a2c["x1p032_arm_gamma"]
    designs = {d: v2["designs_exact_P_C"][d] for d in (A3X2, A3X1, A3X3)}
    checks["the plan's P equals design-power-heat-a2.json's plan_P_C"] = designs == a2c["plan_P_C"]
    OUT["noise_sigma_C"] = s3
    OUT["plan_P_C"] = designs

    # 1. the plan's int8 pair
    P()
    tau2 = s3 / math.sqrt(2)
    fl = {d: round(floor_i8(designs[d], s3), 4) for d in (A3X2, A3X1, A3X3)}
    pair = []
    for ps in designs[A3X2]:
        nm = dict(zip(NAMES, ps))
        pair.append({"P_L1": nm["L1"], "P_S": nm["S"], "P_L2": nm["L2"], "span_C": round(nm["L1"] - nm["S"], 3),
                     "w": round((nm["L2"] - nm["S"]) / (nm["L1"] - nm["S"]), 4)})
    OUT["registered"] = {"pair": list(I8_PAIR), "later": list(I8_LATER), "min_pair_span_P_C": I8_MIN_SPAN_C,
                         "L2_inside_the_pair_span": True, "tau_at_the_plan_C": round(tau2, 4), "tau_one_session_C": round(s3, 4),
                         "N1_I8_line_C": round(s3, 4), "floor_if_the_premise_holds_C": fl, "plan_pair": pair}
    P(f"1. The int8 pair at the plan (v2's exact plan; per session L1, S, L2): " + " | ".join(
        f"P {x['P_L1']:.3f} / {x['P_S']:.3f} / {x['P_L2']:.3f} C, span {x['span_C']:.3f} C, w {x['w']:.4f}" for x in pair))
    P(f"   A4's thresholds: tau = sigma_c / sqrt(n_L) = {s3:.4f} / sqrt(2) = {tau2:.4f} C at the plan ({s3:.4f} C with one session read); "
      f"N1-I8 at sigma_c / sqrt(1) = {s3:.4f} C; the pair spans at least {I8_MIN_SPAN_C} C (the plan's {pair[0]['span_C']:.3f} and "
      f"{pair[1]['span_C']:.3f} C); L2 inside the pair's span (w {pair[0]['w']:.4f} and {pair[1]['w']:.4f})")
    P("   E4' (the int8 holds' own null test): X2 = sum of (e / sigma_c)^2 over the read sessions' L1, S and L2 against chi-square's 95% "
      "point: " + ", ".join(f"{nu} df {v:.4f}" for nu, v in sorted(CHI2_95.items())))
    OUT["registered"]["E4p_chi2_95_points"] = {str(nu): v for nu, v in CHI2_95.items()}
    P(f"   If the premise holds on the int8 holds, the calibrated L2 holds read about sigma_c x sqrt(mean(1 + (1 - w)^2 + w^2)): "
      f"{fl[A3X2]:.4f} C at the plan (one session {fl[A3X1]:.4f}, three {fl[A3X3]:.4f})")

    # 2. synthetic sessions: the read rule by name (the scorer's reference cases)
    P()
    ps = designs[A3X2][0]
    line_e = {nm: (p, -0.229 + 0.0572 * p) for nm, p in zip(NAMES, ps)}
    cases = [("every hold scored", list(NAMES), True, {}, "read"),
             ("H_E not scored (A2 reads NOT SCORED; A4 still reads)", ["Z", "L1", "S", "L2"], True, {}, "read"),
             ("L2 not scored", ["H_E", "Z", "L1", "S"], True, {}, "NOT SCORED"),
             ("S not scored", ["H_E", "Z", "L1", "L2"], True, {}, "NOT SCORED"),
             ("L1 not scored", ["H_E", "Z", "S", "L2"], True, {}, "NOT SCORED"),
             ("L2 run before S ended (a reordering)", list(NAMES), False, {}, "NOT SCORED"),
             ("the pair spans 2.9 C", list(NAMES), True, {"S": ps[2] - 2.9, "L2": ps[2] - 1.0}, "NOT SCORED"),
             ("L2's P above L1's (w > 1)", list(NAMES), True, {"L2": ps[2] + 0.4}, "NOT SCORED"),
             ("L2's P below S's (w < 0)", list(NAMES), True, {"L2": ps[3] - 0.4}, "NOT SCORED"),
             ("the pair spans exactly 3.0 C, L2 at its middle", list(NAMES), True, {"S": ps[2] - 3.0, "L2": ps[2] - 1.5}, "read")]
    syn, syn_ok = {}, True
    for name, order, ok, moved, want in cases:
        named = {}
        for nm in order:
            p = moved.get(nm, line_e[nm][0])
            named[nm] = (p, -0.229 + 0.0572 * p)
        r, why = cal_i8_by_name(named, s3, order_ok=ok)
        got = "read" if r else "NOT SCORED"
        syn_ok = syn_ok and got == want and (r is None or abs(r["ec"]) < 1e-12)
        syn[name] = {"scored": order, "order_ok": ok, "moved_P": moved, "want": want,
                     "got": ({"a_C": round(r["a"], 4), "g": round(r["g"], 5), "w": round(r["w"], 4), "ec_C": round(r["ec"], 12)} if r
                             else f"NOT SCORED: {why}")}
        P(f"     {name:52s} want {want:10s} got " + (f"read: a {r['a']:+.4f} C, g {100 * r['g']:+.3f}%, w {r['w']:.4f}, e_c {r['ec']:+.1e} C" if r
                                                    else f"NOT SCORED ({why})"))
    OUT["synthetic"] = syn
    checks["the read rule reads each synthetic session as A4-1 says (and the line is exact on a noiseless line)"] = syn_ok

    # 3. at the plan
    P()
    P(f"3. HM-CAL-I8 at the plan ({A3X2}), {DRAWS} draws a cell, v2's committed draws. Per truth: I8 BETTER / NOT RESOLVED / WORSE (%); "
      "N1-I8; HM-E144 REPEATS; what M11 carries (A1-4's common term, A2's calibration, HM-CAL-I8) and a per-session calibration in all; "
      "the rms over the L2 holds (C), median [5%, 95%]")
    OUT["plan"] = {}
    differs = []
    n_cmp = 0
    for sgk, sg in (("0.0884", s3), ("0.1325", 1.5 * s3)):
        OUT["plan"][sgk] = {}
        for case in ("premise holds", HE_CHAIN):
            P(f"   simulated sigma {sgk} C, {case}:")
            OUT["plan"][sgk][case] = {}
            for lab, tr in truths:
                ex = None if case == "premise holds" else he_chain_extra(designs[A3X2], tr)
                cell = run_cell_a4(designs[A3X2], (lab, tr), sg, A3X2, s3, gamma_arm, extra=ex)
                OUT["plan"][sgk][case][lab] = cell
                if not DEV_DRAWS:
                    if case == "premise holds":
                        d_ = same_cell(cell, a2c["plan"][sgk][lab], a3c["a2_cells"][f"plan|{sgk}|{lab}"]["a3"], f"plan|{sgk}|{lab}")
                        n_cmp += 1
                    elif sgk == "0.0884":
                        com = a3c["premise_a3"][f"{lab}|{HE_CHAIN}"]
                        d_ = same_cell(cell, com["a2_form"], com["a3"], f"premise_a3|{lab}|{HE_CHAIN}")
                        n_cmp += 1
                    else:
                        d_ = []
                    differs += d_
                P(line4(V2.short(lab), cell))

    # 4. the other premise rows
    P()
    P("4. A2's and A3's other premise rows at the plan, sigma_c (each added after the draw to v2's committed draws for the truth named)")
    OUT["premise_rows"] = {}
    rows_a2 = [("H_E", 0.3, [0.3, 0, 0, 0, 0]), ("H_E", 0.5, [0.5, 0, 0, 0, 0]), ("Z", 0.15, [0, 0.15, 0, 0, 0]),
               ("Z", 0.3, [0, 0.3, 0, 0, 0]), ("drift", 0.05, [0, 0.05, 0.10, 0.15, 0.20]), ("drift", 0.10, [0, 0.10, 0.20, 0.30, 0.40])]
    rows_a3 = [("H_E -0.30 C", [-0.3, 0, 0, 0, 0]), ("H_E -0.50 C", [-0.5, 0, 0, 0, 0]),
               ("fp32 pair +0.15 C (H_E and Z)", [0.15, 0.15, 0, 0, 0]), ("fp32 pair -0.15 C (H_E and Z)", [-0.15, -0.15, 0, 0, 0])]
    for lab, tr in truths:
        if not (lab == "none" or lab.startswith("gain 3.20") or lab.startswith("mixed")):
            continue
        for what, size, ex in rows_a2:
            tag = f"{what} {size:+.2f} C" + (" per hold" if what == "drift" else "")
            cell = run_cell_a4(designs[A3X2], (lab, tr), s3, A3X2, s3, gamma_arm, extra=ex)
            OUT["premise_rows"][f"{lab}|{tag}"] = cell
            if not DEV_DRAWS:
                differs += same_cell(cell, a2c["premise"][f"{lab}|{tag}"], a3c["a2_cells"][f"premise|{lab}|{tag}"]["a3"],
                                     f"premise|{lab}|{tag}")
                n_cmp += 1
            P(line4(f"{V2.short(lab)}, {tag}", cell))
        for tag, ex in rows_a3:
            cell = run_cell_a4(designs[A3X2], (lab, tr), s3, A3X2, s3, gamma_arm, extra=ex)
            OUT["premise_rows"][f"{lab}|{tag}"] = cell
            if not DEV_DRAWS:
                com = a3c["premise_a3"][f"{lab}|{tag}"]
                differs += same_cell(cell, com["a2_form"], com["a3"], f"premise_a3|{lab}|{tag}")
                n_cmp += 1
            P(line4(f"{V2.short(lab)}, {tag}", cell))

    # 5. one and three sessions
    P()
    P("5. One aifoundry3 session (74.7 card-minutes) and three, sigma_c, v2's committed draws for those designs")
    OUT["sessions"] = {}
    for dname in (A3X1, A3X3):
        OUT["sessions"][dname] = {}
        for case in ("premise holds", HE_CHAIN):
            P(f"   {dname}, {case}:")
            OUT["sessions"][dname][case] = {}
            for lab, tr in truths:
                ex = None if case == "premise holds" else he_chain_extra(designs[dname], tr)
                cell = run_cell_a4(designs[dname], (lab, tr), s3, dname, s3, gamma_arm, extra=ex)
                OUT["sessions"][dname][case][lab] = cell
                if not DEV_DRAWS and case == "premise holds":
                    differs += same_cell(cell, a2c["sessions"][dname][lab], a3c["a2_cells"][f"sessions|{dname}|{lab}"]["a3"],
                                         f"sessions|{dname}|{lab}")
                    n_cmp += 1
                P(line4(V2.short(lab), cell))
    if not DEV_DRAWS:
        checks[f"every cell A2 or A3 committed, re-read here ({n_cmp}), equals the committed figures (HM-LG, HM-CAL, A1-4's path, "
               "A2-3's outcome at the exact t point, HM-E144)"] = not differs
    OUT["committed_cells_compared"] = {"cells": n_cmp, "differences": differs}
    P()
    P(f"   committed cells compared: {n_cmp}; differences: {len(differs)}" + ("" if not differs else ": " + "; ".join(differs[:12])))

    # 6. the adoption rule
    P()
    P("6. The adoption rule (A4-6), read at the plan (two aifoundry3 sessions, sigma_c), stated before any output:")
    pl = OUT["plan"]["0.0884"]
    none_rows = ["H_E +0.30 C", "H_E +0.50 C", "Z +0.15 C", "Z +0.30 C", "H_E -0.30 C", "H_E -0.50 C", "fp32 pair +0.15 C (H_E and Z)",
                 "fp32 pair -0.15 C (H_E and Z)"]
    vals = {"(i)": pl["premise holds"]["none"]["with_A4_M11_carries"].get(ENTERS_I8, 0.0),
            "(ii)": pl[HE_CHAIN][MIXED]["a_per_session_calibration_enters"],
            "(iii)": {t: OUT["premise_rows"][f"none|{t}"]["with_A4_M11_carries"].get(ENTERS_I8, 0.0) for t in none_rows}}
    crit = {"(i) with no effect, HM-CAL-I8 enters in at most 5% of draws": vals["(i)"] <= 5.0,
            "(ii) in section 0.1's case on E154's fit then E166's, a per-session calibration (A2's or A4's) enters in at least 80%":
                vals["(ii)"] >= 80.0,
            "(iii) where the chain is right on the int8 holds and only the fp32 pair misses, HM-CAL-I8 enters in at most 5% in each row":
                all(v <= 5.0 for v in vals["(iii)"].values())}
    adopted = all(crit.values())
    first = {"(i)": pl["premise holds"]["none"]["route_as_first_fixed_with_E4_HM_LG"].get(ENTERS_I8, 0.0),
             "(ii)": pl[HE_CHAIN][MIXED]["a_per_session_calibration_enters_as_first_fixed"],
             "(iii)": {t: OUT["premise_rows"][f"none|{t}"]["route_as_first_fixed_with_E4_HM_LG"].get(ENTERS_I8, 0.0) for t in none_rows}}
    first_ok = first["(i)"] <= 5.0 and first["(ii)"] >= 80.0 and all(v <= 5.0 for v in first["(iii)"].values())
    OUT["adoption"] = {"criteria": crit, "values": vals, "adopted": adopted,
                       "route_as_first_fixed_E4_HM_LG": {"values": first, "would_be_adopted": first_ok}}
    for kk, v in crit.items():
        P(f"   {kk}: {'met' if v else 'NOT MET'}")
    P(f"   values: {json.dumps(vals)}")
    P(f"   A4's entry route is {'ADOPTED' if adopted else 'NOT ADOPTED: HM-CAL-I8 is a reported arm only'} at the registered design")
    P(f"   beside it, the route as first fixed (E4 = HM-LG's reading, revised once before this output): {json.dumps(first)}; "
      f"{'it would be adopted' if first_ok else 'it would not be adopted'}")

    OUT["checks"] = checks
    P()
    P("Checks: " + "; ".join(f"{kk}: {'yes' if v else 'NO'}" for kk, v in checks.items()))
    if OUT_JSON_A4:
        json.dump(OUT, open(OUT_JSON_A4, "w"), indent=1, sort_keys=True)
        P()
        P(f"wrote {os.path.relpath(OUT_JSON_A4, TOP)}")
    if not all(checks.values()):
        sys.exit(5)


if __name__ == "__main__":
    main()
