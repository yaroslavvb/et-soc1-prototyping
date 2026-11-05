#!/usr/bin/env python3
"""Q143(k)'s fix pass: M11's dated amendment A5 (tools/claims-v3/m11/REGISTRATION.md.dated-note-A5.md), design only: whether the
sessions' pair lines agree, read beside every per-session calibration (A2's HM-CAL, A4's HM-CAL-I8), and the form an entry is stated in.
No fit of any M11 term, no hold, no card: it reads committed files and prints.

Why (the verifier of Q143(k)'s A4, its fault 1). A4's entry route enters as often when both sessions share one line as when they
differ (section 0.1's case: 80.6% under E154's line in both sessions, 58.7-75.9% under common gains, against 59.4% on the per-session
pattern), yet A4-3 (and A2's table before it) said an entry means "heat over minutes on aifoundry3 is set per session".

What A5 adds (A5-2, A5-3): for the k >= 2 sessions a calibration reads, the 2k pair points (P, e) (A2: H_E and Z; A4: L1 and S):
X2_AG = sum (e - a_hat - g_hat P)^2 / sigma_c^2, (a_hat, g_hat) the least-squares line through all 2k points, which equals the
sessions' (a, g) differences weighed by their known covariance sigma_c^2 (X^T X)^-1 (checked below). Under one common line and noise
sigma_c it is chi-square at 2(k - 1) degrees of freedom: DIFFER above its 95% point, else AGREE; NOT SCORED with k < 2. An entry is
stated "per session" only on DIFFER of the entering calibration's own reading; on AGREE it is "common to the sessions, or not
separated". The entry, its error, its scope and what M11 carries do not change (one way only).

What it reads, each checked first (paths relative to the repository's top directory, argv[1]): tools/claims-v3/m11/SHA256SUMS-a4 (6) and
every file it lists; design_power_heat_a4.py, imported unchanged, checks SHA256SUMS-m11, -a1, -a2 and -a3 and imports A3, A2, v2 and v1
unchanged (v1 checks the ten inputs SHA256SUMS lists). The draws are v2's committed draws: random.Random("M11-HM-LG|<design>|<sigma>|
<truth>") and design_power_heat.sim_sessions, 5,000 draws a cell, a premise failure added after the draw exactly as A4 adds it. Per draw
it calls A4's functions in A4's order (run_cell_a4's loop, line for line), so its check reads: every cell of design-power-heat-a4.json,
re-read here, equals the committed figures (HM-LG, A1-4's path, A2-3's outcome at the exact t point, HM-E144, HM-CAL-I8, N1-I8, E4',
A4-3's outcome).

What it prints (and writes as JSON to argv[2] when given):
  0. the checks of the hash lists and inputs;
  1. the agreement readings' points, and synthetic pairs (the covariance form against the least-squares form; noiseless lines);
  2. at the plan (two aifoundry3 sessions), sigma_c and 1.5 sigma, every committed truth, the premise holding and section 0.1's case:
     A2's and A4's entries split by form, the share that M11 would state "per session", each agreement reading's DIFFER share;
  3. A2's and A3's other premise rows (sigma_c);
  4. one and three aifoundry3 sessions (sigma_c);
  5. the verifier's kind and format rows (truth none: int8.full +0.15, +0.30, -0.30 C on L1 and L2 in both sessions; every int8 hold
     +0.30 C), with the control;
  6. the summary.

    python3 -E -B tools/claims-v3/m11/design_power_heat_a5.py . tools/claims-v3/m11/design-power-heat-a5.json > tools/claims-v3/m11/design-power-heat-a5.txt

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
OUT_JSON_A5 = sys.argv[2] if len(sys.argv) > 2 and not sys.argv[2].startswith("--") else None
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
for _name in ("SHA256SUMS-a4",):
    _l = hash_list(_name)
    _bad = [rel for rel, s in _l.items() if sha(os.path.join(TOP, rel)) != s]
    LISTS[_name] = {"entries": len(_l), "differ": _bad}
    if _bad:
        P(f"STOP: {', '.join(_bad)} differ from tools/claims-v3/m11/{_name}")
        sys.exit(3)

_saved_argv = list(sys.argv)
sys.argv = [os.path.join(HERE, "design_power_heat_a4.py"), TOP]    # A4 reads argv at import; its main() never runs here
sys.path.insert(0, HERE)
import design_power_heat_a4 as A4  # noqa: E402  (A4, unchanged; it checks -m11, -a1, -a2, -a3 and imports A3, A2, v2, v1 unchanged)
sys.argv = _saved_argv

A3, A2, V2, D, DPG = A4.A3, A4.A2, A4.V2, A4.D, A4.DPG
DRAWS = DEV_DRAWS or A4.DRAWS                       # 5,000: v2's committed draws (A4 imported without --dev-draws)
A3X1, A3X2, A3X3 = A4.A3X1, A4.A3X2, A4.A3X3
A4_OUT_REL = "tools/claims-v3/m11/design-power-heat-a4.json"
MIXED = A4.MIXED
HE_CHAIN = A4.HE_CHAIN
NAMES = A4.NAMES                                    # H_E, Z, L1, S, L2 in section 5's order
ENTERS_A2, ENTERS_I8 = A4.ENTERS_A2, A4.ENTERS_I8

# ------------------------------------------------------------------------------------- A5-2: the agreement readings, as registered
AG_VERDICTS = ("DIFFER", "AGREE", "NOT SCORED")
CHI2_AG = {2 * (k - 1): A4.chi2_ppf(0.95, 2 * (k - 1)) for k in (2, 3, 4)}
FORM_PER = "per session"
FORM_COMMON = "common to the sessions, or not separated"
FORMS = ("A2 enters, per session", "A2 enters, common or not separated", "A4 enters, per session", "A4 enters, common or not separated")


def lines_agree(pairs, sigma_c):
    """A5-2 on one card kind: pairs = {session: ((P1, e1), (P2, e2))}, the read sessions' two pair points each. X2_AG = the residual
    sum of squares of one least-squares line through all 2k points, over sigma_c^2; chi-square at 2(k - 1) df under one common line"""
    k = len(pairs)
    if k < 2:
        return {"verdict": "NOT SCORED", "k": k}
    pts = [pt for pr in pairs.values() for pt in pr]
    n = len(pts)
    mx = sum(p for p, _ in pts) / n
    my = sum(e for _, e in pts) / n
    sxx = sum((p - mx) ** 2 for p, _ in pts)
    g = sum((p - mx) * (e - my) for p, e in pts) / sxx
    a = my - g * mx
    x2 = sum((e - a - g * p) ** 2 for p, e in pts) / sigma_c ** 2
    df = 2 * (k - 1)
    pt = CHI2_AG.get(df) or A4.chi2_ppf(0.95, df)
    s2 = sigma_c ** 2
    return {"verdict": "DIFFER" if x2 > pt else "AGREE", "k": k, "X2": x2, "df": df, "point": pt, "pooled_a": a, "pooled_g": g,
            "pooled_cov": [[s2 * (1.0 / n + mx * mx / sxx), -s2 * mx / sxx], [-s2 * mx / sxx, s2 / sxx]]}


def lines_agree_cov_form(pairs, sigma_c):
    """the same X2 at k = 2 in A5-2's other form: (da, dg)^T (C1 + C2)^-1 (da, dg), C = sigma_c^2 (X^T X)^-1 for each session's two
    points (X = [[1, P1], [1, P2]]); the self-test's cross-check"""
    lines = []
    for (p1, e1), (p2, e2) in pairs.values():
        g = (e1 - e2) / (p1 - p2)
        a = e2 - g * p2
        det = (p1 - p2) ** 2
        c = [[sigma_c ** 2 * (p1 * p1 + p2 * p2) / det, -sigma_c ** 2 * (p1 + p2) / det],
             [-sigma_c ** 2 * (p1 + p2) / det, sigma_c ** 2 * 2.0 / det]]
        lines.append(((a, g), c))
    (a1, g1), c1 = lines[0]
    (a2, g2), c2 = lines[1]
    cc = [[c1[i][j] + c2[i][j] for j in range(2)] for i in range(2)]
    det = cc[0][0] * cc[1][1] - cc[0][1] * cc[1][0]
    ci = [[cc[1][1] / det, -cc[0][1] / det], [-cc[1][0] / det, cc[0][0] / det]]
    d = (a1 - a2, g1 - g2)
    return sum(d[i] * ci[i][j] * d[j] for i in range(2) for j in range(2))


def cal_pairs(groups, c):
    """HM-CAL's read sessions' pairs (the session's first two holds by section 5's order: H_E, Z)"""
    return {i: (pts[0], pts[1]) for i, pts in groups.items() if c["per"].get(i) is not None}


def i8_pairs(groups, i8):
    """HM-CAL-I8's read sessions' pairs (L1 and S by name)"""
    out = {}
    for i, pts in groups.items():
        v = i8["per"].get(i)
        if v is not None and "not_scored" not in v:
            nm = dict(zip(NAMES, pts))
            out[i] = (nm["L1"], nm["S"])
    return out


def entry_form(e2, oi, ag_cal, ag_i8):
    """A5-3: the form an entry is stated in, read from the ENTERING calibration's own agreement reading; None when none enters"""
    if e2 == ENTERS_A2:
        return "A2 enters, per session" if ag_cal["verdict"] == "DIFFER" else "A2 enters, common or not separated"
    if oi == ENTERS_I8:
        return "A4 enters, per session" if ag_i8["verdict"] == "DIFFER" else "A4 enters, common or not separated"
    return None


# ------------------------------------------------------------------------------------- one cell (A4's loop, line for line, plus A5)
def run_cell_a5(design, truth, sigma, seed, sigma_c, gamma_arm, extra=None):
    lab, tr = truth
    k = len(design)
    n = sum(len(s) for s in design)
    crit = DPG.f_ppf(0.95, k - 1, n - 2 * k) if k >= 2 else None
    crit_b = DPG.f_ppf(0.95, 2 * (k - 1), n - 2 * k) if k >= 2 else None
    rng = random.Random(f"M11-HM-LG|{seed}|{sigma:.4f}|{lab}")
    per_session_extra = extra is not None and len(extra) > 0 and isinstance(extra[0], (list, tuple))
    verd = {x: 0 for x in A2.VERDICTS}
    a14 = {o: 0 for o in V2.OUTCOMES}
    a2_out = {e: 0 for e in A2.ENTRIES}
    rep_all = 0
    i8_v = {x: 0 for x in A4.I8_VERDICTS}
    i8_n1 = 0
    out_i8 = {o: 0 for o in A4.I8_OUTCOMES}
    e4p = 0
    ag_c = {x: 0 for x in AG_VERDICTS}
    ag_8 = {x: 0 for x in AG_VERDICTS}
    forms = {f: 0 for f in FORMS}
    x2_i8, x2_cal = [], []
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
        deps_x = [A3.he_departs_exact(pts) for pts in groups.values()]
        he_dep_x = all(x for x in deps_x if x is not None) and any(x is not None for x in deps_x)
        e2 = A2.a2_entry(o, c, he_dep_x)
        a2_out[e2] += 1
        rep = all(abs(pts[0][1]) / (pts[0][0] + pts[0][1]) <= A3.E144_LINE for pts in groups.values())
        rep_all += rep
        i8 = A4.hm_cal_i8({i: (dict(zip(NAMES, pts)), True) for i, pts in groups.items()}, sigma_c)
        i8_v[i8["verdict"]] += 1
        i8_n1 += bool(i8.get("N1"))
        oi = A4.i8_entry(o, e2, rep, res, i8, sigma_c)
        out_i8[oi] += 1
        e4p += bool(i8["verdict"] != "NOT SCORED" and A4.int8_misses(i8, sigma_c)[2])
        # A5
        agc = lines_agree(cal_pairs(groups, c), sigma_c)
        ag8 = lines_agree(i8_pairs(groups, i8), sigma_c)
        ag_c[agc["verdict"]] += 1
        ag_8[ag8["verdict"]] += 1
        if "X2" in ag8:
            x2_i8.append(ag8["X2"])
        if "X2" in agc:
            x2_cal.append(agc["X2"])
        f = entry_form(e2, oi, agc, ag8)
        if f:
            forms[f] += 1
    pct, summ = A2.pct, A2.summ
    ent = sum(forms.values())
    per = forms["A2 enters, per session"] + forms["A4 enters, per session"]
    return {"a4_figures": {"HM_LG_verdicts": {x: pct(v, DRAWS) for x, v in verd.items()},
                           "A1_4_carries": {x: pct(v, DRAWS) for x, v in a14.items() if v},
                           "A2_3_outcome_exact_t": {x: pct(v, DRAWS) for x, v in a2_out.items() if v},
                           "HM_E144_repeats": pct(rep_all, DRAWS),
                           "HM_CAL_I8": {x: pct(v, DRAWS) for x, v in i8_v.items()},
                           "N1_I8_met": pct(i8_n1, DRAWS),
                           "with_A4_M11_carries": {x: pct(v, DRAWS) for x, v in out_i8.items() if v},
                           "E4p_int8_misses_read": pct(e4p, DRAWS),
                           "a_per_session_calibration_enters": pct(out_i8["A2's calibration"] + out_i8[ENTERS_I8], DRAWS)},
            "HM_CAL_AG": {x: pct(v, DRAWS) for x, v in ag_c.items()},
            "HM_I8_AG": {x: pct(v, DRAWS) for x, v in ag_8.items()},
            "X2_AG_median": {"HM_CAL_AG": summ(x2_cal), "HM_I8_AG": summ(x2_i8)},
            "entries_by_form": {f: pct(v, DRAWS) for f, v in forms.items()},
            "a_per_session_calibration_enters": pct(ent, DRAWS),
            "M11_states_per_session": pct(per, DRAWS),
            "M11_states_common_or_not_separated": pct(ent - per, DRAWS),
            "share_of_entries_stated_per_session": round(100.0 * per / ent, 1) if ent else None,
            "draws": DRAWS}


A4_KEYS = ("HM_LG_verdicts", "A1_4_carries", "A2_3_outcome_exact_t", "HM_E144_repeats", "HM_CAL_I8", "N1_I8_met", "with_A4_M11_carries",
           "E4p_int8_misses_read", "a_per_session_calibration_enters")


def same_as_a4(cell, com, tag):
    return [f"{tag}: {k}" for k in A4_KEYS if cell["a4_figures"][k] != com[k]]


def line5(lab, cell):
    f = cell["entries_by_form"]
    sh = cell["share_of_entries_stated_per_session"]
    return (f"     {lab:52s} enters {cell['a_per_session_calibration_enters']:5.1f} = A2 {f[FORMS[0]]:5.1f} per session + {f[FORMS[1]]:5.1f} "
            f"common | A4 {f[FORMS[2]]:5.1f} per session + {f[FORMS[3]]:5.1f} common | stated per session {cell['M11_states_per_session']:5.1f} "
            f"({'-' if sh is None else f'{sh:5.1f}'}% of entries) | DIFFER: CAL-AG {cell['HM_CAL_AG']['DIFFER']:5.1f}  I8-AG "
            f"{cell['HM_I8_AG']['DIFFER']:5.1f}")


# ------------------------------------------------------------------------------------- main
def main():
    a4c = json.load(open(os.path.join(TOP, A4_OUT_REL)))
    a2c = json.load(open(os.path.join(TOP, A3.A2_OUT_REL)))
    v2 = json.load(open(os.path.join(TOP, A2.V2_OUT_REL)))
    OUT = {"_note": "Q143(k)'s fix pass: M11's dated amendment A5, design only (no fit of any M11 term, no hold, no card); printed by "
                    "design_power_heat_a5.py", "draws": DRAWS, "dev_draws": DEV_DRAWS}
    checks = {}
    P("M11's heat registration (Q142(h)), dated amendment A5 (Q143(k)'s fix pass): do the sessions' pair lines agree? HM-CAL-AG and "
      "HM-I8-AG, and the form an entry is stated in, on v2's committed draws (design only: no fit of any M11 term, no hold, no card)")
    if DEV_DRAWS:
        P(f"DEVELOPMENT RUN: {DEV_DRAWS} draws a cell (the first {DEV_DRAWS} of the committed draws); never committed")
    P()
    P("0. Checked first: " + "; ".join(f"tools/claims-v3/m11/{k} {v['entries']} of {v['entries']} OK" for k, v in LISTS.items())
      + "; through design_power_heat_a4.py: " + "; ".join(f"{k} {v['entries']} of {v['entries']} OK" for k, v in A4.LISTS.items()))
    rows, bad = D.check_inputs()
    for rel, s, st in rows:
        P(f"   {s}  {rel}  [{st}]")
    if bad:
        P("   STOP: an input differs from tools/claims-v3/m11/SHA256SUMS: " + ", ".join(bad))
        sys.exit(3)
    OUT["checked_first"] = {"lists": LISTS, "via_a4": A4.LISTS, "inputs": [{"path": rel, "sha256": s, "check": st} for rel, s, st in rows]}
    s3 = D.noise()["a3"]["sigma_C"]
    checks["noise as committed (A2, A4)"] = round(s3, 12) == round(a2c["noise_sigma_C"]["aifoundry3"], 12) == round(a4c["noise_sigma_C"], 12)
    truths = V2.truths_as_committed()
    gamma_arm = a2c["x1p032_arm_gamma"]
    designs = {d: v2["designs_exact_P_C"][d] for d in (A3X2, A3X1, A3X3)}
    checks["the plan's P equals design-power-heat-a4.json's plan_P_C"] = designs == a4c["plan_P_C"]
    OUT["noise_sigma_C"] = s3
    OUT["plan_P_C"] = designs

    # 1. the points, and synthetic pairs
    P()
    P("1. The agreement readings (A5-2): X2_AG = RSS of one least-squares line through the read sessions' 2k pair points / sigma_c^2, "
      f"sigma_c {s3:.4f} C; DIFFER above chi-square's 95% point at 2(k - 1) df: " + ", ".join(f"{nu} df {v:.4f}" for nu, v in sorted(CHI2_AG.items())))
    OUT["registered"] = {"readings": {"HM_CAL_AG": "HM-CAL's read sessions, the pair H_E and Z", "HM_I8_AG": "HM-CAL-I8's read sessions, the pair L1 and S"},
                         "statistic": "X2_AG = sum over the 2k pair points of (e - a_hat - g_hat P)^2 / sigma_c^2, one least-squares line",
                         "df": "2(k - 1)", "chi2_95_points": {str(k): v for k, v in CHI2_AG.items()}, "sigma_c_C": s3,
                         "verdicts": {"DIFFER": "X2_AG > the point", "AGREE": "otherwise", "NOT SCORED": "k < 2"},
                         "form_clause": {"DIFFER": FORM_PER, "AGREE": FORM_COMMON}}
    rr = random.Random("M11-A5|synthetic pairs")
    worst = 0.0
    for _ in range(2000):
        prs = {s: ((rr.uniform(3.0, 15.0), rr.gauss(0, 0.2)), (rr.uniform(0.3, 2.9), rr.gauss(0, 0.2))) for s in (0, 1)}
        x_ls = lines_agree(prs, s3)["X2"]
        x_cv = lines_agree_cov_form(prs, s3)
        worst = max(worst, abs(x_ls - x_cv) / max(1.0, abs(x_cv)))
    ps1, ps2 = designs[A3X2]
    nm1, nm2 = dict(zip(NAMES, ps1)), dict(zip(NAMES, ps2))
    common = {0: ((nm1["L1"], -0.229 + 0.0572 * nm1["L1"]), (nm1["S"], -0.229 + 0.0572 * nm1["S"])),
              1: ((nm2["L1"], -0.229 + 0.0572 * nm2["L1"]), (nm2["S"], -0.229 + 0.0572 * nm2["S"]))}
    differ = {0: common[0], 1: ((nm2["L1"], 0.395 - 0.0143 * nm2["L1"]), (nm2["S"], 0.395 - 0.0143 * nm2["S"]))}
    rc, rd = lines_agree(common, s3), lines_agree(differ, s3)
    one = lines_agree({0: common[0]}, s3)
    syn_ok = worst < 1e-9 and rc["verdict"] == "AGREE" and rc["X2"] < 1e-18 and rd["verdict"] == "DIFFER" and one["verdict"] == "NOT SCORED"
    P(f"   the least-squares form against the covariance form, 2,000 random pairs of sessions: largest relative difference {worst:.1e}")
    P(f"   noiseless: E154's line in both sessions (the plan's L1 and S) X2 {rc['X2']:.1e}, {rc['verdict']}; E154's then E166's X2 "
      f"{rd['X2']:.3f}, {rd['verdict']} (its noncentrality, the per-session pattern's at the plan); one session {one['verdict']}")
    OUT["synthetic"] = {"ls_vs_cov_form_worst_relative": worst, "noiseless_common_X2": rc["X2"], "noiseless_E154_then_E166_X2": rd["X2"],
                        "noiseless_E154_then_E166_verdict": rd["verdict"], "one_session": one["verdict"]}
    checks["the two forms of X2_AG agree, and noiseless common / differing lines read AGREE / DIFFER"] = syn_ok

    # 2. at the plan
    differs = []
    n_cmp = 0
    P()
    P(f"2. At the plan ({A3X2}), {DRAWS} draws a cell, v2's committed draws. Per truth: a per-session calibration enters (A4's figure) "
      "= A2's entries by form + A4's entries by form; the share M11 would state 'per session'; each agreement reading's DIFFER share")
    OUT["plan"] = {}
    for sgk, sg in (("0.0884", s3), ("0.1325", 1.5 * s3)):
        OUT["plan"][sgk] = {}
        for case in ("premise holds", HE_CHAIN):
            P(f"   simulated sigma {sgk} C, {case}:")
            OUT["plan"][sgk][case] = {}
            for lab, tr in truths:
                ex = None if case == "premise holds" else A4.he_chain_extra(designs[A3X2], tr)
                cell = run_cell_a5(designs[A3X2], (lab, tr), sg, A3X2, s3, gamma_arm, extra=ex)
                OUT["plan"][sgk][case][lab] = cell
                if not DEV_DRAWS:
                    differs += same_as_a4(cell, a4c["plan"][sgk][case][lab], f"plan|{sgk}|{case}|{lab}")
                    n_cmp += 1
                P(line5(V2.short(lab), cell))

    # 3. the other premise rows
    P()
    P("3. A2's and A3's other premise rows at the plan, sigma_c (each added after the draw, as A4 adds it)")
    OUT["premise_rows"] = {}
    rows_a2 = [("H_E", 0.3, [0.3, 0, 0, 0, 0]), ("H_E", 0.5, [0.5, 0, 0, 0, 0]), ("Z", 0.15, [0, 0.15, 0, 0, 0]),
               ("Z", 0.3, [0, 0.3, 0, 0, 0]), ("drift", 0.05, [0, 0.05, 0.10, 0.15, 0.20]), ("drift", 0.10, [0, 0.10, 0.20, 0.30, 0.40])]
    rows_a3 = [("H_E -0.30 C", [-0.3, 0, 0, 0, 0]), ("H_E -0.50 C", [-0.5, 0, 0, 0, 0]),
               ("fp32 pair +0.15 C (H_E and Z)", [0.15, 0.15, 0, 0, 0]), ("fp32 pair -0.15 C (H_E and Z)", [-0.15, -0.15, 0, 0, 0])]
    for lab, tr in truths:
        if not (lab == "none" or lab.startswith("gain 3.20") or lab.startswith("mixed")):
            continue
        for tag, ex in [(f"{w} {s:+.2f} C" + (" per hold" if w == "drift" else ""), x) for w, s, x in rows_a2] + rows_a3:
            cell = run_cell_a5(designs[A3X2], (lab, tr), s3, A3X2, s3, gamma_arm, extra=ex)
            OUT["premise_rows"][f"{lab}|{tag}"] = cell
            if not DEV_DRAWS:
                differs += same_as_a4(cell, a4c["premise_rows"][f"{lab}|{tag}"], f"premise|{lab}|{tag}")
                n_cmp += 1
            P(line5(f"{V2.short(lab)}, {tag}", cell))

    # 4. one and three sessions
    P()
    P("4. One aifoundry3 session and three, sigma_c")
    OUT["sessions"] = {}
    for dname in (A3X1, A3X3):
        OUT["sessions"][dname] = {}
        for case in ("premise holds", HE_CHAIN):
            P(f"   {dname}, {case}:")
            OUT["sessions"][dname][case] = {}
            for lab, tr in truths:
                ex = None if case == "premise holds" else A4.he_chain_extra(designs[dname], tr)
                cell = run_cell_a5(designs[dname], (lab, tr), s3, dname, s3, gamma_arm, extra=ex)
                OUT["sessions"][dname][case][lab] = cell
                if not DEV_DRAWS:
                    differs += same_as_a4(cell, a4c["sessions"][dname][case][lab], f"sessions|{dname}|{case}|{lab}")
                    n_cmp += 1
                P(line5(V2.short(lab), cell))
    if not DEV_DRAWS:
        checks[f"every cell of design-power-heat-a4.json, re-read here ({n_cmp}), equals the committed figures"] = not differs
    OUT["a4_cells_compared"] = {"cells": n_cmp, "differences": differs}
    P()
    P(f"   cells of design-power-heat-a4.json compared: {n_cmp}; differences: {len(differs)}" + ("" if not differs else ": " + "; ".join(differs[:12])))

    # 5. the verifier's kind and format rows
    P()
    P("5. The kind and format rows (A5-5; the verifier's rows, truth none, sigma_c; the miss added to the named holds in both sessions)")
    tr = dict(truths)
    kind_rows = [("int8.full +0.15 C (L1 and L2, both sessions)", [0, 0, 0.15, 0, 0.15]),
                 ("int8.full +0.30 C (L1 and L2, both sessions)", [0, 0, 0.30, 0, 0.30]),
                 ("int8.full -0.30 C (L1 and L2, both sessions)", [0, 0, -0.30, 0, -0.30]),
                 ("every int8 hold +0.30 C (L1, S, L2: a format level)", [0, 0, 0.30, 0.30, 0.30]),
                 ("control: no extra (A4's committed 'none' cell)", [0, 0, 0, 0, 0])]
    OUT["kind_rows"] = {}
    for tag, ex in kind_rows:
        cell = run_cell_a5(designs[A3X2], ("none", tr["none"]), s3, A3X2, s3, gamma_arm, extra=ex)
        OUT["kind_rows"][tag] = cell
        P(line5(tag[:52], cell))
    ctl = OUT["kind_rows"]["control: no extra (A4's committed 'none' cell)"]
    if not DEV_DRAWS:
        checks["the control row equals A4's committed 'none' cell (premise holds, sigma_c)"] = not same_as_a4(
            ctl, a4c["plan"]["0.0884"]["premise holds"]["none"], "control")

    # 6. the summary
    pl = OUT["plan"]["0.0884"]
    common_labs = [lab for lab, _ in truths if not lab.startswith("mixed") and lab != "none"]
    summ = {"section_0_1_likeliest_pattern": {k: pl[HE_CHAIN][MIXED][k] for k in ("a_per_session_calibration_enters", "entries_by_form",
                                                                                     "M11_states_per_session", "M11_states_common_or_not_separated",
                                                                                     "share_of_entries_stated_per_session")},
            "premise_holds_likeliest_pattern": {k: pl["premise holds"][MIXED][k] for k in ("a_per_session_calibration_enters", "entries_by_form",
                                                                                           "M11_states_per_session", "share_of_entries_stated_per_session")},
            "section_0_1_common_rows_stated_per_session": {lab: pl[HE_CHAIN][lab]["M11_states_per_session"] for lab in common_labs},
            "section_0_1_common_rows_entering": {lab: pl[HE_CHAIN][lab]["a_per_session_calibration_enters"] for lab in common_labs},
            "premise_common_rows_stated_per_session": {lab: pl["premise holds"][lab]["M11_states_per_session"] for lab in common_labs},
            "kind_rows_stated_per_session": {t: c["M11_states_per_session"] for t, c in OUT["kind_rows"].items()},
            "kind_rows_entering": {t: c["a_per_session_calibration_enters"] for t, c in OUT["kind_rows"].items()},
            "one_session_I8_AG_not_scored": OUT["sessions"][A3X1][HE_CHAIN][MIXED]["HM_I8_AG"]["NOT SCORED"],
            "three_sessions_section_0_1_likeliest": {k: OUT["sessions"][A3X3][HE_CHAIN][MIXED][k] for k in (
                "a_per_session_calibration_enters", "M11_states_per_session", "share_of_entries_stated_per_session")},
            "1p5_sigma_section_0_1_likeliest": {k: OUT["plan"]["0.1325"][HE_CHAIN][MIXED][k] for k in (
                "a_per_session_calibration_enters", "M11_states_per_session", "share_of_entries_stated_per_session")},
            "1p5_sigma_section_0_1_common_rows_stated_per_session": {lab: OUT["plan"]["0.1325"][HE_CHAIN][lab]["M11_states_per_session"]
                                                                    for lab in common_labs}}
    OUT["summary"] = summ
    P()
    P("6. Summary (sigma_c unless named): " + json.dumps(summ))
    OUT["checks"] = checks
    P()
    P("Checks: " + "; ".join(f"{kk}: {'yes' if v else 'NO'}" for kk, v in checks.items()))
    if OUT_JSON_A5:
        json.dump(OUT, open(OUT_JSON_A5, "w"), indent=1, sort_keys=True)
        P()
        P(f"wrote {os.path.relpath(OUT_JSON_A5, TOP)}")
    if not all(checks.values()):
        sys.exit(5)


if __name__ == "__main__":
    main()
