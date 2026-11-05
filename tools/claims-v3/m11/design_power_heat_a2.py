#!/usr/bin/env python3
"""Q142(a2): M11's dated amendment A2 (tools/claims-v3/m11/REGISTRATION.md.dated-note-A2.md), design only: the power of HM-CAL,
the in-session calibration reading of heat over minutes, at the registered hold design, on v2's committed draws. No fit of any M11
term, no hold, no card: it reads committed files and prints.

What HM-CAL is (A2-1): in each M11 hold session, the session's own level and gain of the frozen chain's miss given the watts,
e = a + g P, are fitted on its first two holds, H_E and Z (the calibration pair), and its later holds (L1, S, L2) are then predicted
by the chain plus that line and scored blind (given the watts) against the chain unscaled: D = rms(e - a - g P) - rms(e) over the
card kind's scored later holds, BETTER if D <= -sigma_c / sqrt(n_L), WORSE if D >= +sigma_c / sqrt(n_L), else NOT RESOLVED.

What it reads, each checked first (paths relative to the repository's top directory, argv[1]):
  tools/claims-v3/m11/SHA256SUMS-m11 and SHA256SUMS-a1, every file they list (REGISTRATION.md, registration.json and
  registration-a1.json, A1, design_power_heat.py and design_power_heat_v2.py with their committed outputs), and through
  design_power_heat.check_inputs the ten inputs SHA256SUMS lists; design_power_heat_v2 is imported unchanged (it imports
  design_power_heat unchanged, which imports design_power_groups.lg_test and Q138(t)'s frozen chain unchanged).
  The plan's P per hold: design-power-heat-v2.json > designs_exact_P_C (and, as a check, design_power_heat_v2.plan_exact re-run at
  51.2 and 52.0 C); aifoundry2's designs: design-power-heat.json > power > P_C.

The draws are v2's committed draws: for each design, noise and truth, random.Random("M11-HM-LG|<design>|<sigma>|<truth>") and
design_power_heat.sim_sessions, 5,000 draws a cell, exactly as design_power_heat.power_table and design_power_heat_v2.path_rates
draw them. The check line confirms it: on every cell of a committed truth, HM-LG's verdict shares equal the committed tables, and on
the plan the amended section-6 path (design_power_heat_v2.decide) gives the committed design-power-heat-v2.json > path shares.

What it prints (and writes as JSON to argv[2] when given):
  0. the checks of the hash lists and inputs;
  1. the noise and A2's thresholds;
  2. the plan's P (v2's exact plan), and the post hoc preview of the reading on the two committed aifoundry3 sessions with four or
     more holds (E154, E166; heldout-m10.json > heat_d_chain_gain.holds; disclosed, not a registered result);
  3. HM-CAL-A3 at the plan (two aifoundry3 sessions): verdict shares, the not-wanted clauses, what M11 carries with A2 beside A1-4's
     path, and the blind errors it delivers (the median and 5-95% range of the pooled rms over the later holds: the chain unscaled,
     the session's own calibration, the x1.032 arm, and A1-4's carried common term refitted on the other session);
  4. the reported arms: the pair's gain alone, the pair's level alone, and H_E's gain alone;
  5. what the reading does when its premise fails: a miss specific to H_E (+0.3 / +0.5 C) or to Z (+0.15 / +0.3 C), or a level
     that drifts through the session (+0.05 / +0.10 C per hold), each added to every session after the draw (the same noise draws);
  6. one and three aifoundry3 sessions;
  7. aifoundry2's masked design (registered beside, reported);
  8. the adoption rule of A2-6, read mechanically.

    python3 -E -B tools/claims-v3/m11/design_power_heat_a2.py . tools/claims-v3/m11/design-power-heat-a2.json > tools/claims-v3/m11/design-power-heat-a2.txt

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
OUT_JSON_A2 = sys.argv[2] if len(sys.argv) > 2 and not sys.argv[2].startswith("--") else None
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
for _name in ("SHA256SUMS-m11", "SHA256SUMS-a1"):
    _l = hash_list(_name)
    _bad = [rel for rel, s in _l.items() if sha(os.path.join(TOP, rel)) != s]
    LISTS[_name] = {"entries": len(_l), "differ": _bad}
    if _bad:
        P(f"STOP: {', '.join(_bad)} differ from tools/claims-v3/m11/{_name}")
        sys.exit(3)

_saved_argv = list(sys.argv)
sys.argv = [os.path.join(HERE, "design_power_heat_v2.py"), TOP]   # design_power_heat_v2 reads argv[1] at import; its main() never runs
sys.path.insert(0, HERE)
import design_power_heat_v2 as V2  # noqa: E402  (v2, unchanged; it checks v1 against SHA256SUMS-m11 and imports it unchanged)
sys.argv = _saved_argv

D, DPG = V2.D, V2.DPG
DRAWS = DEV_DRAWS or V2.DRAWS                       # 5,000: v2's committed draws
VERDICTS = V2.VERDICTS
A3X1, A3X2, A3X3 = V2.A3X1, V2.A3X2, V2.A3X3
A2X2 = "A2 x2 masked (two aifoundry2 sessions: Z_m, G1E, Z_m, G1E)"
A2X4 = "A2 x4 masked (four aifoundry2 sessions)"
V1_OUT_REL = "tools/claims-v3/m11/design-power-heat.json"
V2_OUT_REL = "tools/claims-v3/m11/design-power-heat-v2.json"

# ------------------------------------------------------------------------------------- A2-1: the reading HM-CAL, as registered
N_CAL = 2                 # the calibration pair: the session's first two holds by section 5's order (aifoundry3: H_E, Z)
MIN_PAIR_SPAN_C = 6.0     # the pair spans at least 6.0 C of P (HM-LG's span), else the session reads NOT SCORED
MIN_LATER = 2             # at least 2 scored later holds, else the session reads NOT SCORED
CAL_VERDICTS = ("BETTER", "NOT RESOLVED", "WORSE", "NOT SCORED")
FORMS = ("both", "gain", "level", "gain_HE")   # "both" is the primary (A2-1); the others are reported arms (A2-4)
COMMON_OUTCOMES = {"both enter": "both", "gain enters": "gain", "gain enters (BOTH, refitted alone)": "gain",
                   "level enters": "level", "level enters (BOTH, refitted alone)": "level"}
TQ_HE = {1: 12.706, 2: 4.303, 3: 3.182, 4: 2.776, 5: 2.571}   # design_power_heat.he_rates' t points (HM-HE, t at n_s - 3 df)


def rms(v):
    return math.sqrt(sum(x * x for x in v) / len(v))


def cal_line(cal, form):
    """the session's own (a, g) from its calibration pair cal = [(P, e) of H_E, (P, e) of Z]"""
    if form == "both":                      # the two-term line through the pair (its least-squares fit)
        (p1, e1), (p2, e2) = cal[0], cal[1]
        g = (e1 - e2) / (p1 - p2)
        return e2 - g * p2, g
    if form == "gain":                      # section 6's GAIN form on the pair: sum e P / sum P^2
        return 0.0, sum(e * p for p, e in cal) / sum(p * p for p, _ in cal)
    if form == "level":                     # section 6's LEVEL form on the pair: the mean e
        return sum(e for _, e in cal) / len(cal), 0.0
    p, e = cal[0]                           # gain_HE: H_E's gain alone, e(H_E) / P(H_E)
    return 0.0, e / p


def session_cal(pts, form, sigma_c):
    """one session's HM-CAL reading: pts = its scored holds [(P, e)] in run order"""
    cal, later = pts[:N_CAL], pts[N_CAL:]
    if len(cal) < N_CAL or len(later) < MIN_LATER or abs(cal[0][0] - cal[1][0]) < MIN_PAIR_SPAN_C:
        return None
    a, g = cal_line(cal, form)
    eu = [e for _, e in later]
    ec = [e - a - g * p for p, e in later]
    du = rms(ec) - rms(eu)
    return {"a": a, "g": g, "n": len(later), "eu": eu, "ec": ec, "rms_u": rms(eu), "rms_c": rms(ec), "d": du,
            "worse_alone": du >= sigma_c / math.sqrt(len(later))}


def hm_cal(groups, form, sigma_c):
    """HM-CAL over a card kind's sessions: the pooled D over every read session's later holds, its verdict, and clause N1"""
    per = {k: session_cal(pts, form, sigma_c) for k, pts in groups.items()}
    read = {k: v for k, v in per.items() if v is not None}
    if not read:
        return {"verdict": "NOT SCORED", "k": 0, "per": per}
    eu = [x for v in read.values() for x in v["eu"]]
    ec = [x for v in read.values() for x in v["ec"]]
    ru, rc = rms(eu), rms(ec)
    tau = sigma_c / math.sqrt(len(eu))
    dd = rc - ru
    verdict = "BETTER" if dd <= -tau else "WORSE" if dd >= tau else "NOT RESOLVED"
    return {"verdict": verdict, "k": len(read), "n_L": len(eu), "tau": tau, "D": dd, "rms_u": ru, "rms_c": rc, "per": per,
            "N1": any(v["worse_alone"] for v in read.values())}


def hm_he_departs(pts):
    """HM-HE (REGISTRATION.md section 3) on one session: e(H_E) outside the 95% prediction interval of the two-term fit on the
    session's other scored holds, t at n_s - 3 degrees of freedom (design_power_heat.he_rates' arithmetic)"""
    others = pts[1:]
    pe, ee = pts[0]
    df = len(others) - 2
    if df < 1:
        return None
    a0, b0, mx, sxx = D.ls_fit(others)
    s = math.sqrt(sum((e - a0 - b0 * p) ** 2 for p, e in others) / df)
    se = s * math.sqrt(1.0 + 1.0 / len(others) + (pe - mx) ** 2 / sxx)
    return abs(ee - (a0 + b0 * pe)) > TQ_HE[df] * se


def common_heldout(groups, form):
    """A1-4's carried common form refitted on the other sessions' holds (S7-W's fit), applied to each session's later holds"""
    out = []
    for k, pts in groups.items():
        other = [p for j, v in groups.items() if j != k for p in v]
        if form == "gain":
            a, g = 0.0, sum(e * p for p, e in other) / sum(p * p for p, e in other)
        elif form == "level":
            a, g = sum(e for _, e in other) / len(other), 0.0
        else:
            a, g, _, _ = D.ls_fit(other)
        out += [e - a - g * p for p, e in pts[N_CAL:]]
    return rms(out)


def floor_rms(design, sigma_c):
    """the blind rms the calibrated later holds would read if the premise held exactly (each hold's miss = the session's line
    plus independent noise sigma_c): sigma_c * sqrt(mean over the later holds of 1 + (1 - w)^2 + w^2), w = (P - P_Z) / (P_HE - P_Z),
    the two-point line's own noise carried to each later hold"""
    f = []
    for ps in design:
        (p1, p2), later = ps[:N_CAL], ps[N_CAL:]
        for p in later:
            w = (p - p2) / (p1 - p2)
            f.append(1.0 + (1.0 - w) ** 2 + w * w)
    return sigma_c * math.sqrt(sum(f) / len(f))


def a2_entry(a14_outcome, cal, he_dep):
    """A2-3: what M11 carries for heat over minutes on the card kind, with A2 beside A1-4's path"""
    if a14_outcome in COMMON_OUTCOMES:
        return "A1-4's common term (the calibration a reported arm)"
    if cal["verdict"] != "BETTER":
        return "nothing from A2: " + cal["verdict"]
    if cal["N1"]:
        return "nothing from A2: N1, a session worse on its own (a reported arm)"
    if he_dep:
        return "nothing from A2: N2, H_E departs in every session (a reported arm)"
    if cal["k"] < 2:
        return "nothing from A2: one session (a candidate)"
    return "the calibration enters"


ENTRIES = ("the calibration enters", "A1-4's common term (the calibration a reported arm)", "nothing from A2: NOT RESOLVED",
           "nothing from A2: WORSE", "nothing from A2: NOT SCORED", "nothing from A2: N1, a session worse on its own (a reported arm)",
           "nothing from A2: N2, H_E departs in every session (a reported arm)", "nothing from A2: one session (a candidate)")


def q(v, f):
    s = sorted(v)
    return s[min(len(s) - 1, int(f * len(s)))]


def pct(c, n):
    return round(100.0 * c / n, 1)


def summ(v):
    return {"median": round(q(v, 0.5), 4), "p05": round(q(v, 0.05), 4), "p95": round(q(v, 0.95), 4)} if v else None


def run_cell(design, truth, sigma, seed, sigma_c, gamma_arm, extra=None, he_index=0):
    """one cell on v2's committed draws: random.Random(f"M11-HM-LG|{seed}|{sigma:.4f}|{label}") and sim_sessions, DRAWS draws.
    extra, a list of one value per hold, is added to every session's misses after the draw (the same noise draws): a miss
    specific to H_E or to Z, or a level that drifts through the session. he_index 0: HM-HE is read on hold 0 (aifoundry3's H_E)."""
    lab, tr = truth
    k = len(design)
    n = sum(len(s) for s in design)
    crit = DPG.f_ppf(0.95, k - 1, n - 2 * k) if k >= 2 else None
    crit_b = DPG.f_ppf(0.95, 2 * (k - 1), n - 2 * k) if k >= 2 else None
    rng = random.Random(f"M11-HM-LG|{seed}|{sigma:.4f}|{lab}")
    verd = {x: 0 for x in VERDICTS}
    a14 = {o: 0 for o in V2.OUTCOMES}
    cal_v = {f: {x: 0 for x in CAL_VERDICTS} for f in FORMS}
    n1 = {f: 0 for f in FORMS}
    entry = {e: 0 for e in ENTRIES}
    he_all = 0
    better_clean = 0
    r_u, r_c, r_arm, r_ct, r_c_enter, d_c = [], [], [], [], [], []
    r_form = {f: [] for f in FORMS}
    joint = {}
    per_session_c = []
    for _ in range(DRAWS):
        groups = D.sim_sessions(design, tr, sigma, rng)
        if extra:
            groups = {i: [(p, e + x) for (p, e), x in zip(pts, extra)] for i, pts in groups.items()}
        res = DPG.lg_test(groups, min_tiles=D.MIN_HOLDS, min_span_w=D.MIN_SPAN_C, min_df=D.MIN_DF, detail=True)
        verd[res["verdict"]] += 1
        o, _ = V2.decide(groups, res, k, n, crit, crit_b, sigma_c)
        a14[o] += 1
        cals = {f: hm_cal(groups, f, sigma_c) for f in FORMS}
        for f in FORMS:
            cal_v[f][cals[f]["verdict"]] += 1
            n1[f] += bool(cals[f].get("N1"))
            if cals[f]["verdict"] != "NOT SCORED":
                r_form[f].append(cals[f]["rms_c"])
        if he_index == 0:                   # HM-HE is registered on aifoundry3's H_E (hold 0) only
            deps = [hm_he_departs(pts) for pts in groups.values()]
            he_dep = all(x for x in deps if x is not None) and any(x is not None for x in deps)
        else:
            he_dep = False
        he_all += he_dep
        c = cals["both"]
        better_clean += c["verdict"] == "BETTER" and not c["N1"] and not he_dep
        e = a2_entry(o, c, he_dep)
        entry[e] += 1
        key = ("A1-4 common" if o in COMMON_OUTCOMES else "A1-4 nothing") + " | HM-CAL " + c["verdict"]
        joint[key] = joint.get(key, 0) + 1
        if c["verdict"] != "NOT SCORED":
            r_u.append(c["rms_u"])
            r_c.append(c["rms_c"])
            d_c.append(c["D"])
            per_session_c += [v["rms_c"] for v in c["per"].values() if v is not None]
            later = [(p, ee) for pts in groups.values() for p, ee in pts[N_CAL:]]
            r_arm.append(rms([ee - gamma_arm * p for p, ee in later]))
            if o in COMMON_OUTCOMES and k >= 2:
                r_ct.append(common_heldout(groups, COMMON_OUTCOMES[o]))
            if e == "the calibration enters":
                r_c_enter.append(c["rms_c"])
    return {"HM_LG_verdicts": {x: pct(v, DRAWS) for x, v in verd.items()},
            "A1_4_carries": {o: pct(v, DRAWS) for o, v in a14.items() if v},
            "HM_CAL": {f: {x: pct(v, DRAWS) for x, v in cal_v[f].items()} for f in FORMS},
            "N1_met": {f: pct(v, DRAWS) for f, v in n1.items()},
            "N2_H_E_departs_every_session": pct(he_all, DRAWS),
            "HM_CAL_BETTER_no_clause_met": pct(better_clean, DRAWS),
            "with_A2_M11_carries": {e: pct(v, DRAWS) for e, v in entry.items() if v},
            "joint_A1_4_and_HM_CAL": {kk: pct(v, DRAWS) for kk, v in sorted(joint.items())},
            "rms_later_C": {"chain_unscaled": summ(r_u), "calibrated": summ(r_c), "x1p032_arm": summ(r_arm),
                            "common_term_held_out_when_carried": summ(r_ct), "calibrated_when_it_enters": summ(r_c_enter),
                            "calibrated_one_session": summ(per_session_c),
                            "by_form": {f: summ(v) for f, v in r_form.items()}},
            "D_C": summ(d_c), "draws": DRAWS}


def line(lab, cell, form="both"):
    h = cell["HM_CAL"][form]
    r = cell["rms_later_C"]
    car = cell["with_A2_M11_carries"]
    return (f"     {V2.short(lab):30s} HM-CAL " + " / ".join(f"{h[x]:5.1f}" for x in CAL_VERDICTS[:3])
            + f" | N1 {cell['N1_met'][form]:4.1f}  N2 {cell['N2_H_E_departs_every_session']:4.1f}"
            + f" | enters {car.get('the calibration enters', 0.0):5.1f}  A1-4 common {car.get(ENTRIES[1], 0.0):5.1f}"
            + f" | rms: unscaled {r['chain_unscaled']['median']:.3f}  calibrated {r['calibrated']['median']:.3f}"
            + f" [{r['calibrated']['p05']:.3f}, {r['calibrated']['p95']:.3f}]  arm {r['x1p032_arm']['median']:.3f}")


# ------------------------------------------------------------------------------------- the post hoc preview (A2-0)
def preview_committed(sigma_c):
    """HM-CAL's arithmetic on the committed aifoundry3 sessions with four or more fitted holds (heldout-m10.json, run order as
    listed): the first two holds as the calibration pair when they span >= 6 C of P, and, beside it, every pair spanning >= 6 C
    with the session's other holds scored. Post hoc: these sessions ran other kinds in another order; no rule reads them."""
    hl = json.load(open(os.path.join(D.M10D, "heldout-m10.json")))["heat_d_chain_gain"]["holds"]
    ses = {}
    for x in hl:
        if x.get("fitted") and x.get("P_C") is not None and x["card_kind"] == "aifoundry3":
            ses.setdefault(x["session"], []).append((x["hold"], x["P_C"], x["e_C"]))
    out = {}
    for s, hs in sorted(ses.items()):
        if len(hs) < 4:
            continue
        pts = [(p, e) for _, p, e in hs]
        first = session_cal(pts, "both", sigma_c)
        pairs = []
        for i in range(len(hs)):
            for j in range(i + 1, len(hs)):
                if abs(hs[i][1] - hs[j][1]) < MIN_PAIR_SPAN_C:
                    continue
                rest = [(p, e) for m, (_, p, e) in enumerate(hs) if m not in (i, j)]
                r = session_cal([(hs[i][1], hs[i][2]), (hs[j][1], hs[j][2])] + rest, "both", sigma_c)
                pairs.append({"pair": [hs[i][0], hs[j][0]], "a_C": round(r["a"], 4), "g": round(r["g"], 5),
                              "rms_u_C": round(r["rms_u"], 4), "rms_c_C": round(r["rms_c"], 4), "d_C": round(r["d"], 4),
                              "n_scored": r["n"]})
        out[s] = {"holds": [{"hold": h, "P_C": round(p, 3), "e_C": round(e, 4)} for h, p, e in hs],
                  "first_pair": ([hs[0][0], hs[1][0]], round(abs(hs[0][1] - hs[1][1]), 3)),
                  "first_pair_reading": None if first is None else
                  {"a_C": round(first["a"], 4), "g": round(first["g"], 5), "rms_u_C": round(first["rms_u"], 4),
                   "rms_c_C": round(first["rms_c"], 4), "d_C": round(first["d"], 4), "n_scored": first["n"],
                   "threshold_one_session_C": round(sigma_c / math.sqrt(first["n"]), 4)},
                  "every_pair_spanning_6C": pairs}
    return out


# ------------------------------------------------------------------------------------- main
def main():
    v1 = json.load(open(os.path.join(TOP, V1_OUT_REL)))
    v2 = json.load(open(os.path.join(TOP, V2_OUT_REL)))
    OUT = {"_note": "Q142(a2): M11's dated amendment A2, design only (no fit of any M11 term, no hold, no card); printed by "
                    "design_power_heat_a2.py", "draws": DRAWS, "dev_draws": DEV_DRAWS}
    checks = {}
    P("M11's heat registration (Q142(h)), dated amendment A2 (Q142(a2)): the power of HM-CAL, the in-session calibration reading of "
      "heat over minutes, on v2's committed draws (design only: no fit of any M11 term, no hold, no card)")
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
    s3, s2 = nz["a3"]["sigma_C"], nz["a2"]["sigma_C"]
    s2f = nz["a2"]["readout_floor_sigma_C"]
    checks["noise as committed (v2)"] = (round(s3, 12) == round(v2["noise_sigma_C"]["aifoundry3"], 12)
                                         and round(s2, 12) == round(v2["noise_sigma_C"]["aifoundry2"], 12))
    truths = V2.truths_as_committed()
    checks["truth labels as committed (v2)"] = sorted(l for l, _ in truths) == sorted(v1["truths"])
    s7 = json.load(open(os.path.join(D.M10D, "section7-m10.json")))["section7"]["d"]
    gamma_arm = s7["variants"]["common"]["gamma_all_holds"]["all"]
    OUT["noise_sigma_C"] = {"aifoundry3": s3, "aifoundry2": s2, "aifoundry2_readout_floor": s2f}
    OUT["x1p032_arm_gamma"] = gamma_arm
    P()
    P(f"1. The noise (design_power_heat.noise, unchanged): aifoundry3 sigma_c {s3:.4f} C (6 degrees of freedom), aifoundry2 "
      f"{s2:.4f} C. A2's thresholds: HM-CAL tau = sigma_c / sqrt(n_L) over the pooled scored later holds (at the plan n_L 6: "
      f"{s3 / math.sqrt(6):.4f} C on aifoundry3); N1, a session worse on its own, d >= sigma_c / sqrt(n_s) ({s3 / math.sqrt(3):.4f} C "
      f"for 3 later holds). The x1.032 arm's gamma {gamma_arm:.5f} (section7-m10.json, the common gamma)")

    des_ex = v2["designs_exact_P_C"]
    rep = True
    for room, idx in (("51.2", 0), ("52.0", 1)):
        pl = V2.plan_exact(float(room))
        rep = rep and [h["P_C"] for h in pl["holds"]] == des_ex[A3X2][idx]
    checks["v2's exact plan re-run at 51.2 and 52.0 C equals design-power-heat-v2.json's designs_exact_P_C"] = rep
    designs = {A3X2: des_ex[A3X2], A3X1: des_ex[A3X1], A3X3: des_ex[A3X3]}
    OUT["plan_P_C"] = designs
    P()
    P("2. The plan's P per hold (v2's exact plan; H_E, Z, L1, S, L2): " + " | ".join(", ".join(f"{p:.3f}" for p in s) for s in designs[A3X2])
      + f"; the calibration pair H_E and Z spans {designs[A3X2][0][0] - designs[A3X2][0][1]:.2f} and "
        f"{designs[A3X2][1][0] - designs[A3X2][1][1]:.2f} C of P; the scored later holds L1, S, L2")
    fl = {d: round(floor_rms(designs[d], s3), 4) for d in (A3X2, A3X1, A3X3)}
    OUT["registered"] = {"calibration_pair": "the session's first two holds by section 5's order: H_E, then Z (aifoundry3); Z_m, then G1E "
                                            "(aifoundry2)", "later_holds": "the session's other scored holds (aifoundry3: L1, S, L2)",
                         "n_cal": N_CAL, "min_pair_span_P_C": MIN_PAIR_SPAN_C, "min_later_holds": MIN_LATER, "primary_form": "both",
                         "arms": list(FORMS[1:]), "tau_at_the_plan_C": round(s3 / math.sqrt(6), 4),
                         "N1_line_three_later_holds_C": round(s3 / math.sqrt(3), 4), "floor_if_the_premise_holds_C": fl}
    P(f"   If the premise holds exactly, the calibrated later holds read about sigma_c x sqrt(mean(1 + v)): {fl[A3X2]:.4f} C at the plan "
      f"(one session {fl[A3X1]:.4f}, three {fl[A3X3]:.4f}), v the two-point line's own noise carried to each later hold")
    pv = preview_committed(s3)
    OUT["posthoc_preview_committed_sessions"] = pv
    P("   Post hoc preview (A2-0; heldout-m10.json's fitted aifoundry3 holds, in the order listed; not a registered result):")
    for s, v in pv.items():
        fp = v["first_pair_reading"]
        P(f"     {s}: holds " + "; ".join(f"{h['hold']} P {h['P_C']:.2f} e {h['e_C']:+.3f}" for h in v["holds"]))
        P(f"       first pair {v['first_pair'][0][0]}+{v['first_pair'][0][1]} spans {v['first_pair'][1]:.2f} C: "
          + ("NOT SCORED (under 6 C)" if fp is None else
             f"a {fp['a_C']:+.3f} C, g {100 * fp['g']:+.2f}%; later rms unscaled {fp['rms_u_C']:.3f}, calibrated {fp['rms_c_C']:.3f}, "
             f"d {fp['d_C']:+.3f} C (one session's line {fp['threshold_one_session_C']:.3f} over {fp['n_scored']} holds)"))
        ds = [x["d_C"] for x in v["every_pair_spanning_6C"]]
        if ds:
            P(f"       every pair spanning 6 C ({len(ds)}): d from {min(ds):+.3f} to {max(ds):+.3f} C, " +
              f"{sum(1 for x in ds if x < 0)} of {len(ds)} below 0: " +
              "; ".join(f"{'+'.join(x['pair'])} {x['d_C']:+.3f}" for x in v["every_pair_spanning_6C"]))

    P()
    P(f"3. HM-CAL-A3 at the plan ({A3X2}), {DRAWS} draws a cell, v2's committed draws. Per truth: HM-CAL BETTER / NOT RESOLVED / "
      "WORSE (%); N1 and N2 met (%); with A2, M11 carries the calibration ('enters') or A1-4's common term (%); the pooled rms over "
      "the later holds (C), median [5%, 95%] for the calibration")
    OUT["plan"] = {}
    rep_path = True
    rep_lg = True
    for sg in (s3, 1.5 * s3):
        cells = {}
        P(f"   simulated sigma {sg:.4f} C (thresholds at sigma_c {s3:.4f} C):")
        for lab, tr in truths:
            cell = run_cell(designs[A3X2], (lab, tr), sg, A3X2, s3, gamma_arm)
            cells[lab] = cell
            if not DEV_DRAWS:
                com = v2["path"][f"{sg:.4f}"][lab]
                rep_path = rep_path and all(abs(cell["A1_4_carries"].get(o, 0.0) - x) < 1e-9 for o, x in com["carries"].items())
                rep_lg = rep_lg and cell["HM_LG_verdicts"] == v2["power"][A3X2]["by_sigma"][f"{sg:.4f}"][lab]
            P(line(lab, cell))
        OUT["plan"][f"{sg:.4f}"] = cells
    if not DEV_DRAWS:
        checks["HM-LG's verdicts at the plan equal design-power-heat-v2.json's power table (v2's draws)"] = rep_lg
        checks["A1-4's path at the plan equals design-power-heat-v2.json's path (v2's draws and decide)"] = rep_path
    mixed = "mixed: E154's fit, then E166's"
    m = OUT["plan"][f"{s3:.4f}"][mixed]
    P(f"   joint, on E154's fit then E166's (sigma_c): " + "; ".join(f"{k} {v:.1f}" for k, v in m["joint_A1_4_and_HM_CAL"].items()))
    P(f"   rms over the later holds there: unscaled {m['rms_later_C']['chain_unscaled']}, calibrated {m['rms_later_C']['calibrated']}, "
      f"x1.032 arm {m['rms_later_C']['x1p032_arm']}; one session's own calibrated rms {m['rms_later_C']['calibrated_one_session']}")
    P("   where A1-4 carries a common term, that term refitted on the other session, over the same later holds (median C), against the "
      "calibration's: " + "; ".join(
          f"{V2.short(lab)} {c['rms_later_C']['common_term_held_out_when_carried']['median']:.3f} / {c['rms_later_C']['calibrated']['median']:.3f}"
          for lab, c in OUT["plan"][f"{s3:.4f}"].items() if c["rms_later_C"]["common_term_held_out_when_carried"] and lab != "none"))

    P()
    P("4. The reported arms at the plan (sigma_c; the same draws and later holds): the pair's GAIN alone (sum e P / sum P^2 over H_E "
      "and Z), the pair's LEVEL alone (the mean e), and H_E's gain alone (e / P of H_E). HM-CAL BETTER / NOT RESOLVED / WORSE (%)")
    for lab, _ in truths:
        cell = OUT["plan"][f"{s3:.4f}"][lab]
        P(f"     {V2.short(lab):30s} " + " | ".join(f"{f}: " + " / ".join(f"{cell['HM_CAL'][f][x]:5.1f}" for x in CAL_VERDICTS[:3])
                                              + f" (rms {cell['rms_later_C']['by_form'][f]['median']:.3f})" for f in FORMS))

    P()
    P("5. What the reading does when its premise fails, at the plan, sigma_c: a miss specific to H_E or to Z (delta added to that "
      "hold's e in every session), or a level that drifts through the session (c per hold: 0, c, 2c, 3c, 4c for H_E, Z, L1, S, L2), "
      "each added after the draw to v2's committed draws for the truth named")
    OUT["premise"] = {}
    extras = [("H_E", 0.3, [0.3, 0, 0, 0, 0]), ("H_E", 0.5, [0.5, 0, 0, 0, 0]), ("Z", 0.15, [0, 0.15, 0, 0, 0]),
              ("Z", 0.3, [0, 0.3, 0, 0, 0]), ("drift", 0.05, [0, 0.05, 0.10, 0.15, 0.20]), ("drift", 0.10, [0, 0.10, 0.20, 0.30, 0.40])]
    for lab, tr in truths:
        if not (lab == "none" or lab.startswith("gain 3.20") or lab.startswith("mixed")):
            continue
        for what, size, ex in extras:
            cell = run_cell(designs[A3X2], (lab, tr), s3, A3X2, s3, gamma_arm, extra=ex)
            tag = f"{what} {size:+.2f} C" + (" per hold" if what == "drift" else "")
            OUT["premise"][f"{lab}|{tag}"] = cell
            P(line(f"{V2.short(lab)}, {tag}", cell))

    P()
    P("6. One aifoundry3 session (the least, 74.7 card-minutes) and three, sigma_c, v2's committed draws for those designs")
    OUT["sessions"] = {}
    rep_13 = True
    for dname in (A3X1, A3X3):
        P(f"   {dname}:")
        OUT["sessions"][dname] = {}
        for lab, tr in truths:
            cell = run_cell(designs[dname], (lab, tr), s3, dname, s3, gamma_arm)
            OUT["sessions"][dname][lab] = cell
            if not DEV_DRAWS:
                rep_13 = rep_13 and cell["HM_LG_verdicts"] == v2["power"][dname]["by_sigma"][f"{s3:.4f}"][lab]
            P(line(lab, cell))
    if not DEV_DRAWS:
        checks["HM-LG's verdicts for one and three sessions equal design-power-heat-v2.json's (v2's draws)"] = rep_13

    P()
    P("7. aifoundry2's masked design (registered beside, reported): the pair Z_m and G1E, the later Z_m2 and G1E2; sigma_c "
      f"{s2:.4f} C; v1's committed draws for these designs (design-power-heat.json)")
    OUT["aifoundry2"] = {}
    rep_a2 = True
    for dname in (A2X2, A2X4):
        des = v1["power"][dname]["P_C"]
        OUT["aifoundry2"][dname] = {"P_C": des, "by_sigma": {}}
        for sg in ((s2, s2f, 1.5 * s2) if dname == A2X2 else (s2,)):
            P(f"   {dname}, simulated sigma {sg:.4f} C:")
            cells = {}
            for lab, tr in truths:
                if lab not in ("none", "mixed: E154's fit, then E166's") and not lab.startswith("gain 4.52") and not lab.startswith("level 0.40"):
                    continue
                cell = run_cell(des, (lab, tr), sg, dname, s2, gamma_arm, he_index=None)
                cells[lab] = cell
                if not DEV_DRAWS:
                    rep_a2 = rep_a2 and cell["HM_LG_verdicts"] == v1["power"][dname]["by_sigma"][f"{sg:.4f}"][lab]
                P(line(lab, cell))
            OUT["aifoundry2"][dname]["by_sigma"][f"{sg:.4f}"] = cells
    if not DEV_DRAWS:
        checks["HM-LG's verdicts on aifoundry2's designs equal design-power-heat.json's (v1's draws)"] = rep_a2

    P()
    P("8. The adoption rule (A2-6), read at the plan (two aifoundry3 sessions, sigma_c), stated before this output:")
    pl = OUT["plan"][f"{s3:.4f}"]
    patt = ["both: E154's two-term fit (-0.229 C + 5.72%)", "both: E166's two-term fit (+0.395 C - 1.43%)", mixed]
    crit = {
        "(i) HM-CAL-A3 BETTER at most 5% with no effect": pl["none"]["HM_CAL"]["both"]["BETTER"] <= 5.0,
        "(ii) BETTER with no clause met (N1, N2) in at least 80% under each committed pattern":
            all(pl[l]["HM_CAL_BETTER_no_clause_met"] >= 80.0 for l in patt),
        "(iii) under E154's fit then E166's, the calibration enters in at least 80%":
            pl[mixed]["with_A2_M11_carries"].get("the calibration enters", 0.0) >= 80.0,
        "(iv) the calibration enters at most 5% with no effect":
            pl["none"]["with_A2_M11_carries"].get("the calibration enters", 0.0) <= 5.0,
    }
    vals = {
        "(i)": pl["none"]["HM_CAL"]["both"]["BETTER"],
        "(ii)": {l: pl[l]["HM_CAL_BETTER_no_clause_met"] for l in patt},
        "(iii)": pl[mixed]["with_A2_M11_carries"].get("the calibration enters", 0.0),
        "(iv)": pl["none"]["with_A2_M11_carries"].get("the calibration enters", 0.0),
    }
    adopted = all(crit.values())
    OUT["adoption"] = {"criteria": crit, "values": vals, "adopted": adopted}
    for k, v in crit.items():
        P(f"   {k}: {'met' if v else 'NOT MET'}")
    P(f"   values: {json.dumps(vals)}")
    P(f"   A2 is {'ADOPTED' if adopted else 'NOT ADOPTED'} at the registered design (two aifoundry3 sessions of 74.7 card-minutes)")

    OUT["checks"] = checks
    P()
    P("Checks: " + "; ".join(f"{k}: {'yes' if v else 'NO'}" for k, v in checks.items()))
    if OUT_JSON_A2:
        json.dump(OUT, open(OUT_JSON_A2, "w"), indent=1, sort_keys=True)
        P()
        P(f"wrote {os.path.relpath(OUT_JSON_A2, TOP)}")
    if not all(checks.values()):
        sys.exit(5)


if __name__ == "__main__":
    main()
