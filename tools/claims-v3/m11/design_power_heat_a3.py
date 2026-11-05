#!/usr/bin/env python3
"""Q142(a2)'s fix pass: M11's dated amendment A3 (tools/claims-v3/m11/REGISTRATION.md.dated-note-A3.md), design only. The faults
an adversarial read of A2 (lab d3d97fe2) found in its power code are fixed in this new file, every cell of
design-power-heat-a2.json is re-run on v2's committed draws, and the premise rows A3 adds are computed. No fit of any M11 term,
no hold, no card: it reads committed files and prints.

Fixed here (design_power_heat_a2.py and its output stay as committed):
  - HM-HE's t point, which N2 reads: the exact 97.5% point of Student's t at n_s - 3 degrees of freedom
    (design_power_heat_v2.t95: 4.3027 at 2), as REGISTRATION.md section 3 registers it. design_power_heat.he_rates and
    design_power_heat_a2 used a table rounded to three decimals (4.303 at 2). Section 1 re-reads v2's one-session H_E readings
    at the exact point; section 3 re-reads N2 in every cell of A2.
  - The calibration pair by hold name (cal_by_name: H_E and Z on aifoundry3, Z_m and G1E on aifoundry2; the later holds by name
    too), where design_power_heat_a2.session_cal takes the first two SCORED holds. In the design every simulated hold is scored,
    so the two agree (checked on every session of every draw); with H_E not scored, session_cal would pair Z with L1 and read a
    session that A2-1 reads NOT SCORED (section 2's synthetic cases).
Added (A3-2, A3-5, A3-7):
  - the premise rows: H_E read by the chain as E144's H_H was (e(H_E) = its noise only, while the session's other holds keep
    their line), H_E-specific misses of -0.3 and -0.5 C, and an offset of the fp32 pair (H_E and Z) against the int8 later
    holds of +0.15 and -0.15 C, each added after the draw to v2's committed draws for the truth named (as A2's section 5);
  - HM-E144 (REGISTRATION.md section 3: |e(H_E)| / R(H_E) <= 0.015, REPEATS if inside in every session that ran H_E) beside
    HM-CAL in every aifoundry3 cell, jointly with HM-CAL's verdict and A2-3's outcome, and what it would do as a third
    not-wanted clause (reported only: A3 does not register it);
  - the share of A1-4's row "BOTH, and HM-AG's BOTH form says they differ" against "the sessions differ" over every verdict.

What it reads, each checked first (paths relative to the repository's top directory, argv[1]):
  tools/claims-v3/m11/SHA256SUMS-m11 (6), SHA256SUMS-a1 (9) and SHA256SUMS-a2 (7), every file they list; through
  design_power_heat.check_inputs the ten inputs SHA256SUMS lists. design_power_heat_a2 is imported unchanged (it imports
  design_power_heat_v2 unchanged, which imports design_power_heat unchanged). The committed outputs it compares against:
  design-power-heat-a2.json, design-power-heat-v2.json and design-power-heat.json.

    python3 -E -B tools/claims-v3/m11/design_power_heat_a3.py . tools/claims-v3/m11/design-power-heat-a3.json > tools/claims-v3/m11/design-power-heat-a3.txt

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
OUT_JSON_A3 = sys.argv[2] if len(sys.argv) > 2 and not sys.argv[2].startswith("--") else None
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
for _name in ("SHA256SUMS-m11", "SHA256SUMS-a1", "SHA256SUMS-a2"):
    _l = hash_list(_name)
    _bad = [rel for rel, s in _l.items() if sha(os.path.join(TOP, rel)) != s]
    LISTS[_name] = {"entries": len(_l), "differ": _bad}
    if _bad:
        P(f"STOP: {', '.join(_bad)} differ from tools/claims-v3/m11/{_name}")
        sys.exit(3)

_saved_argv = list(sys.argv)
sys.argv = [os.path.join(HERE, "design_power_heat_a2.py"), TOP]    # A2 reads argv at import; its main() never runs here
sys.path.insert(0, HERE)
import design_power_heat_a2 as A2  # noqa: E402  (A2, unchanged; it checks -m11 and -a1 and imports v2 and v1 unchanged)
sys.argv = _saved_argv

V2, D, DPG = A2.V2, A2.D, A2.DPG
DRAWS = DEV_DRAWS or A2.DRAWS                       # 5,000: v2's committed draws (A2 imported without --dev-draws)
A3X1, A3X2, A3X3, A2X2, A2X4 = A2.A3X1, A2.A3X2, A2.A3X3, A2.A2X2, A2.A2X4
A2_OUT_REL = "tools/claims-v3/m11/design-power-heat-a2.json"
ENTERS = "the calibration enters"
MIXED = "mixed: E154's fit, then E166's"

# ------------------------------------------------------------------------------------- A3-6: the pair and the later holds by name
NAMES = {"aifoundry3": ("H_E", "Z", "L1", "S", "L2"), "aifoundry2": ("Z_m", "G1E", "Z_m2", "G1E2")}
PAIR = {"aifoundry3": ("H_E", "Z"), "aifoundry2": ("Z_m", "G1E")}
LATER = {"aifoundry3": ("L1", "S", "L2"), "aifoundry2": ("Z_m2", "G1E2")}
E144_LINE = 0.015                                   # REGISTRATION.md section 3: HM-E144 is |e(H_E)| / R(H_E) <= 0.015


def cal_by_name(named, kind, form, sigma_c, pair_first=True):
    """A2-1 read by hold name (A3-6). named = {hold name: (P, e)} over the session's SCORED holds only (a hold not scored is
    absent); pair_first False when the session did not run its pair first (A2-7: a reordering). Returns (reading, None), the
    reading in design_power_heat_a2.session_cal's form, or (None, the reason the session reads NOT SCORED)."""
    p_name, z_name = PAIR[kind]
    if not pair_first:
        return None, "its pair was not run first (a reordering, A2-7)"
    for nm in (p_name, z_name):
        if nm not in named:
            return None, f"its pair hold {nm} is not scored"
    later = [named[nm] for nm in LATER[kind] if nm in named]
    if len(later) < A2.MIN_LATER:
        return None, f"{len(later)} later hold(s) scored, fewer than {A2.MIN_LATER}"
    (p1, e1), (p2, e2) = named[p_name], named[z_name]
    if abs(p1 - p2) < A2.MIN_PAIR_SPAN_C:
        return None, f"the pair spans under {A2.MIN_PAIR_SPAN_C} C of P"
    a, g = A2.cal_line([(p1, e1), (p2, e2)], form)
    eu = [e for _, e in later]
    ec = [e - a - g * p for p, e in later]
    d = A2.rms(ec) - A2.rms(eu)
    return {"a": a, "g": g, "n": len(later), "eu": eu, "ec": ec, "rms_u": A2.rms(eu), "rms_c": A2.rms(ec), "d": d,
            "worse_alone": d >= sigma_c / math.sqrt(len(later))}, None


def same_reading(x, y):
    if x is None or y is None:
        return x is None and y is None
    return all(x[k] == y[k] for k in ("a", "g", "n", "eu", "ec", "rms_u", "rms_c", "d", "worse_alone"))


# ------------------------------------------------------------------------------------- A3-7 (c): HM-HE at the exact t point
T_EXACT = {df: V2.t95(df) for df in (1, 2, 3, 4, 5)}   # Student's t, 97.5% point, from design_power_groups.f_ppf (exact)


def he_departs_exact(pts):
    """HM-HE (REGISTRATION.md section 3) on one session, pts in run order with H_E first: e(H_E) outside the 95% prediction
    interval of the two-term fit on the session's other scored holds, t at n_s - 3 degrees of freedom, the EXACT point.
    design_power_heat_a2.hm_he_departs's arithmetic otherwise, line for line."""
    others = pts[1:]
    pe, ee = pts[0]
    df = len(others) - 2
    if df < 1:
        return None
    a0, b0, mx, sxx = D.ls_fit(others)
    s = math.sqrt(sum((e - a0 - b0 * p) ** 2 for p, e in others) / df)
    se = s * math.sqrt(1.0 + 1.0 / len(others) + (pe - mx) ** 2 / sxx)
    return abs(ee - (a0 + b0 * pe)) > T_EXACT[df] * se


def he_rates_both(p_session, i_he, truths, sigma, seed, deltas=(0.0, 0.3, 0.5)):
    """design_power_heat.he_rates's draws and arithmetic, line for line, with HM-HE read at the rounded point it used (to check
    the committed figures) and at the exact point"""
    others = [p for j, p in enumerate(p_session) if j != i_he]
    pe_ = p_session[i_he]
    df = len(others) - 2
    out = {}
    for lab, tr in truths:
        a, g = tr[0]
        for dl in deltas:
            rng = random.Random(f"M11-HE|{seed}|{sigma:.4f}|{lab}|{dl}")
            inside = dep_r = dep_x = 0
            for _ in range(DRAWS):
                eo = [(p, a + g * p + rng.gauss(0.0, sigma)) for p in others]
                ee = a + g * pe_ + dl + rng.gauss(0.0, sigma)
                inside += abs(ee) / (pe_ + ee) <= E144_LINE
                a0, b0, mx, sxx = D.ls_fit(eo)
                res = [e - a0 - b0 * p for p, e in eo]
                s = math.sqrt(sum(r * r for r in res) / df)
                se = s * math.sqrt(1.0 + 1.0 / len(eo) + (pe_ - mx) ** 2 / sxx)
                dev = abs(ee - (a0 + b0 * pe_))
                dep_r += dev > A2.TQ_HE[df] * se
                dep_x += dev > T_EXACT[df] * se
            out[f"{lab}|delta {dl:+.1f} C"] = {"HM-E144 inside 1.5%": round(100.0 * inside / DRAWS, 1),
                                               "HM-HE departs, the rounded point (as committed)": round(100.0 * dep_r / DRAWS, 1),
                                               "HM-HE departs, the exact point": round(100.0 * dep_x / DRAWS, 1)}
    return out


# ------------------------------------------------------------------------------------- one cell, A2's and A3's readings
def run_cell_a3(design, kind, truth, sigma, seed, sigma_c, gamma_arm, extra=None):
    """one cell on v2's committed draws: random.Random(f"M11-HM-LG|{seed}|{sigma:.4f}|{label}") and sim_sessions, DRAWS draws.
    extra: None; a list of one value per hold, added to every session's misses after the draw (A2's section 5); or a list of
    such lists, one per session. Returns (a2_view, a3_view): a2_view is design_power_heat_a2.run_cell's output, computed line for
    line on the same draws (it must equal the committed cell); a3_view holds what A3 adds."""
    lab, tr = truth
    k = len(design)
    n = sum(len(s) for s in design)
    crit = DPG.f_ppf(0.95, k - 1, n - 2 * k) if k >= 2 else None
    crit_b = DPG.f_ppf(0.95, 2 * (k - 1), n - 2 * k) if k >= 2 else None
    rng = random.Random(f"M11-HM-LG|{seed}|{sigma:.4f}|{lab}")
    he_on = kind == "aifoundry3"                     # HM-HE, N2 and HM-E144 are registered on aifoundry3's H_E only
    names = NAMES[kind]
    per_session_extra = extra is not None and len(extra) > 0 and isinstance(extra[0], (list, tuple))
    # design_power_heat_a2.run_cell's accumulators
    verd = {x: 0 for x in A2.VERDICTS}
    a14 = {o: 0 for o in V2.OUTCOMES}
    cal_v = {f: {x: 0 for x in A2.CAL_VERDICTS} for f in A2.FORMS}
    n1 = {f: 0 for f in A2.FORMS}
    entry = {e: 0 for e in A2.ENTRIES}
    he_all = 0
    better_clean = 0
    r_u, r_c, r_arm, r_ct, r_c_enter, d_c = [], [], [], [], [], []
    r_form = {f: [] for f in A2.FORMS}
    joint = {}
    per_session_c = []
    # A3's
    he_all_x = better_clean_x = 0
    entry_x = {e: 0 for e in A2.ENTRIES}
    rep_all = rep_enter = enters_n3 = better_clean_n3 = 0
    joint_rep = {}
    both_differ = differ_any = 0
    checked = mismatch = 0
    r_c_ent_x, r_u_ent_x, r_c_ent_rep, r_u_ent_rep = [], [], [], []
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
        both_differ += res["verdict"] == "BOTH" and o == "nothing: the sessions differ"
        differ_any += o == "nothing: the sessions differ"
        cals = {f: A2.hm_cal(groups, f, sigma_c) for f in A2.FORMS}
        for f in A2.FORMS:
            cal_v[f][cals[f]["verdict"]] += 1
            n1[f] += bool(cals[f].get("N1"))
            if cals[f]["verdict"] != "NOT SCORED":
                r_form[f].append(cals[f]["rms_c"])
        if he_on:
            deps = [A2.hm_he_departs(pts) for pts in groups.values()]
            he_dep = all(x for x in deps if x is not None) and any(x is not None for x in deps)
            deps_x = [he_departs_exact(pts) for pts in groups.values()]
            he_dep_x = all(x for x in deps_x if x is not None) and any(x is not None for x in deps_x)
            rep = all(abs(pts[0][1]) / (pts[0][0] + pts[0][1]) <= E144_LINE for pts in groups.values())
        else:
            he_dep = he_dep_x = False
            rep = None
        he_all += he_dep
        he_all_x += he_dep_x
        c = cals["both"]
        better_clean += c["verdict"] == "BETTER" and not c["N1"] and not he_dep
        better_clean_x += c["verdict"] == "BETTER" and not c["N1"] and not he_dep_x
        e = A2.a2_entry(o, c, he_dep)
        entry[e] += 1
        ex = A2.a2_entry(o, c, he_dep_x)
        entry_x[ex] += 1
        key = ("A1-4 common" if o in A2.COMMON_OUTCOMES else "A1-4 nothing") + " | HM-CAL " + c["verdict"]
        joint[key] = joint.get(key, 0) + 1
        if rep is not None:
            rep_all += rep
            jk = ("HM-E144 REPEATS" if rep else "HM-E144 DOES NOT REPEAT") + " | HM-CAL " + c["verdict"]
            joint_rep[jk] = joint_rep.get(jk, 0) + 1
            rep_enter += rep and ex == ENTERS
            enters_n3 += (not rep) and ex == ENTERS
            better_clean_n3 += c["verdict"] == "BETTER" and not c["N1"] and not he_dep_x and not rep
        for i, pts in groups.items():                # A3-6: the pair by name agrees with session_cal when every hold scores
            rb, _ = cal_by_name(dict(zip(names, pts)), kind, "both", sigma_c)
            checked += 1
            mismatch += not same_reading(A2.session_cal(pts, "both", sigma_c), rb)
        if c["verdict"] != "NOT SCORED":
            r_u.append(c["rms_u"])
            r_c.append(c["rms_c"])
            d_c.append(c["D"])
            per_session_c += [v["rms_c"] for v in c["per"].values() if v is not None]
            later = [(p, ee) for pts in groups.values() for p, ee in pts[A2.N_CAL:]]
            r_arm.append(A2.rms([ee - gamma_arm * p for p, ee in later]))
            if o in A2.COMMON_OUTCOMES and k >= 2:
                r_ct.append(A2.common_heldout(groups, A2.COMMON_OUTCOMES[o]))
            if e == ENTERS:
                r_c_enter.append(c["rms_c"])
            if ex == ENTERS:
                r_c_ent_x.append(c["rms_c"])
                r_u_ent_x.append(c["rms_u"])
                if rep:
                    r_c_ent_rep.append(c["rms_c"])
                    r_u_ent_rep.append(c["rms_u"])
    pct, summ = A2.pct, A2.summ
    a2_view = {"HM_LG_verdicts": {x: pct(v, DRAWS) for x, v in verd.items()},
               "A1_4_carries": {o: pct(v, DRAWS) for o, v in a14.items() if v},
               "HM_CAL": {f: {x: pct(v, DRAWS) for x, v in cal_v[f].items()} for f in A2.FORMS},
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
    a3_view = {"exact_t": {"N2_H_E_departs_every_session": pct(he_all_x, DRAWS) if he_on else None,
                           "HM_CAL_BETTER_no_clause_met": pct(better_clean_x, DRAWS),
                           "with_A2_M11_carries": {e: pct(v, DRAWS) for e, v in entry_x.items() if v},
                           "rms_later_C_when_it_enters": {"calibrated": summ(r_c_ent_x), "chain_unscaled": summ(r_u_ent_x)}},
               "HM_E144": None if not he_on else {
                   "repeats_in_every_session": pct(rep_all, DRAWS),
                   "joint_with_HM_CAL": {kk: pct(v, DRAWS) for kk, v in sorted(joint_rep.items())},
                   "repeats_and_the_calibration_enters": pct(rep_enter, DRAWS),
                   "rms_later_C_when_it_repeats_and_enters": {"calibrated": summ(r_c_ent_rep), "chain_unscaled": summ(r_u_ent_rep)},
                   "if_it_were_a_third_clause_N3": {"the calibration enters": pct(enters_n3, DRAWS),
                                                    "BETTER_no_clause_met": pct(better_clean_n3, DRAWS)}},
               "A1_4_BOTH_and_the_sessions_differ": pct(both_differ, DRAWS),
               "A1_4_the_sessions_differ_any_verdict": pct(differ_any, DRAWS),
               "pair_by_name": {"sessions_checked": checked, "differ_from_session_cal": mismatch},
               "draws": DRAWS}
    return a2_view, a3_view


def short(lab):
    return V2.short(lab)


def line3(lab, a2v, a3v):
    h = a2v["HM_CAL"]["both"]
    r = a2v["rms_later_C"]
    x = a3v["exact_t"]
    ent = x["with_A2_M11_carries"]
    rr = x["rms_later_C_when_it_enters"]
    he = a3v["HM_E144"]
    s = (f"     {lab:46s} HM-CAL " + " / ".join(f"{h[v]:5.1f}" for v in A2.CAL_VERDICTS[:3])
         + f" | N1 {a2v['N1_met']['both']:4.1f}  N2 {x['N2_H_E_departs_every_session'] if x['N2_H_E_departs_every_session'] is not None else 0.0:4.1f}"
         + (f"  E144 rep {he['repeats_in_every_session']:5.1f}" if he else "")
         + f" | enters {ent.get(ENTERS, 0.0):5.1f}  A1-4 common {ent.get(A2.ENTRIES[1], 0.0):5.1f}"
         + f" | rms: unscaled {r['chain_unscaled']['median']:.3f}  calibrated {r['calibrated']['median']:.3f}"
         + f" [{r['calibrated']['p05']:.3f}, {r['calibrated']['p95']:.3f}]")
    if rr["calibrated"]:
        s += f"  when it enters {rr['calibrated']['median']:.3f} (unscaled {rr['chain_unscaled']['median']:.3f})"
    return s


# ------------------------------------------------------------------------------------- main
def main():
    a2c = json.load(open(os.path.join(TOP, A2_OUT_REL)))
    v1 = json.load(open(os.path.join(TOP, A2.V1_OUT_REL)))
    v2 = json.load(open(os.path.join(TOP, A2.V2_OUT_REL)))
    OUT = {"_note": "Q142(a2)'s fix pass: M11's dated amendment A3, design only (no fit of any M11 term, no hold, no card); printed "
                    "by design_power_heat_a3.py", "draws": DRAWS, "dev_draws": DEV_DRAWS}
    checks = {}
    P("M11's heat registration (Q142(h)), dated amendment A3 (Q142(a2)'s fix pass): A2's power code faults fixed in a new file, A2's "
      "cells re-run on v2's committed draws, and the premise rows A3 adds (design only: no fit of any M11 term, no hold, no card)")
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
    checks["noise as committed (A2)"] = (round(s3, 12) == round(a2c["noise_sigma_C"]["aifoundry3"], 12)
                                         and round(s2, 12) == round(a2c["noise_sigma_C"]["aifoundry2"], 12))
    truths = V2.truths_as_committed()
    checks["truth labels as committed (v1)"] = sorted(l for l, _ in truths) == sorted(v1["truths"])
    gamma_arm = a2c["x1p032_arm_gamma"]
    designs = {d: v2["designs_exact_P_C"][d] for d in (A3X2, A3X1, A3X3)}
    checks["the plan's P equals design-power-heat-a2.json's plan_P_C"] = designs == a2c["plan_P_C"]
    TR = dict(truths)

    # 1. the exact t point
    P()
    P("1. HM-HE's t point (REGISTRATION.md section 3: t at n_s - 3 degrees of freedom). The exact 97.5% points, "
      "design_power_heat_v2.t95: " + ", ".join(f"{df} df {T_EXACT[df]:.5f}" for df in sorted(T_EXACT))
      + "; the committed table: " + ", ".join(f"{df} df {A2.TQ_HE[df]}" for df in sorted(A2.TQ_HE))
      + ". Every M11 session of five holds reads HM-HE at 2 df.")
    OUT["t_points"] = {"exact": {str(df): T_EXACT[df] for df in T_EXACT}, "committed_table": {str(df): v for df, v in A2.TQ_HE.items()}}
    p3 = designs[A3X1][0]
    he = he_rates_both(p3, 0, [(lab, tr) for lab, tr in truths if lab.split(" ")[0] in ("none", "gain", "level")], s3, "A3x1")
    OUT["he_one_session_v2_section5"] = he
    rep_he = True
    P("   H_E in one aifoundry3 session at the exact plan (room 51.2 C), design-power-heat-v2's section 5' re-run on its committed draws: "
      "HM-E144 inside 1.5%; HM-HE departs at the committed (rounded) point and at the exact point (%)")
    for kk, v in he.items():
        c = v2["he"][kk]
        same = (c["HM-E144 inside 1.5%"] == v["HM-E144 inside 1.5%"]
                and c["HM-HE departs"] == v["HM-HE departs, the rounded point (as committed)"])
        rep_he = rep_he and same
        P(f"     {kk:62s} inside {v['HM-E144 inside 1.5%']:5.1f}  departs {v['HM-HE departs, the rounded point (as committed)']:5.1f}"
          f" -> exact {v['HM-HE departs, the exact point']:5.1f}" + ("" if same else "   [DIFFERS FROM THE COMMITTED v2]")
          + ("   <- changes" if v["HM-HE departs, the exact point"] != v["HM-HE departs, the rounded point (as committed)"] else ""))
    if not DEV_DRAWS:
        checks["v2's one-session H_E readings re-run at the committed point equal design-power-heat-v2.json's he"] = rep_he

    # 2. the pair by name: synthetic sessions
    P()
    P("2. The pair by hold name (A3-6). Synthetic sessions on the plan's first session (P " + ", ".join(f"{p:.3f}" for p in designs[A3X2][0])
      + " C), every miss on E154's two-term line e = -0.229 C + 5.72% of P (no noise); design_power_heat_a2.session_cal on the "
        "scored holds in run order, against cal_by_name")
    ps = designs[A3X2][0]
    named_all = {nm: (p, -0.229 + 0.0572 * p) for nm, p in zip(NAMES["aifoundry3"], ps)}
    cases = [("every hold scored", list(NAMES["aifoundry3"]), True),
             ("H_E not scored", ["Z", "L1", "S", "L2"], True),
             ("Z not scored", ["H_E", "L1", "S", "L2"], True),
             ("S not scored", ["H_E", "Z", "L1", "L2"], True),
             ("L1 and S not scored", ["H_E", "Z", "L2"], True),
             ("the pair run in the other order (Z, then H_E)", ["Z", "H_E", "L1", "S", "L2"], False)]
    syn = {}
    want = {"every hold scored": "read", "H_E not scored": "NOT SCORED", "Z not scored": "NOT SCORED", "S not scored": "read",
            "L1 and S not scored": "NOT SCORED", "the pair run in the other order (Z, then H_E)": "NOT SCORED"}
    syn_ok = True
    for name, order, first in cases:
        pts = [named_all[nm] for nm in order]
        old = A2.session_cal(pts, "both", s3)
        new, why = cal_by_name({nm: named_all[nm] for nm in order}, "aifoundry3", "both", s3, pair_first=first)

        def desc(r, pair):
            if r is None:
                return None
            return {"pair": pair, "later": r["n"], "a_C": round(r["a"], 4), "g": round(r["g"], 5), "rms_c_C": round(r["rms_c"], 4)}
        syn[name] = {"scored_in_run_order": order,
                     "session_cal": desc(old, order[:2]) if old else "NOT SCORED",
                     "cal_by_name": desc(new, list(PAIR["aifoundry3"])) if new else f"NOT SCORED: {why}"}
        got = "read" if new else "NOT SCORED"
        syn_ok = syn_ok and got == want[name]
        P(f"     {name:48s} session_cal: " + (f"reads pair {order[0]}+{order[1]} (span {abs(named_all[order[0]][0] - named_all[order[1]][0]):.2f} C), "
                                              f"{old['n']} later holds" if old else "NOT SCORED")
          + " | by name: " + (f"reads pair H_E+Z, {new['n']} later holds" if new else f"NOT SCORED ({why})"))
    OUT["pair_by_name_synthetic"] = syn
    checks["the pair by name reads each synthetic session as A2-1 says"] = syn_ok

    # 3. A2's cells re-run
    P()
    P(f"3. Every cell of design-power-heat-a2.json re-run on v2's committed draws ({DRAWS} a cell), with design_power_heat_a2's own "
      "functions: the cell as A2's code computes it must equal the committed cell; beside it, N2 at the exact t point and what "
      "follows from it (the calibration's entry, BETTER with no clause met)")
    cells = []        # (path, design, kind, truth, sigma, seed, extra, committed)
    for sgk, sg in (("0.0884", s3), ("0.1325", 1.5 * s3)):
        for lab, tr in truths:
            cells.append((("plan", sgk, lab), designs[A3X2], "aifoundry3", (lab, tr), sg, A3X2, None, a2c["plan"][sgk][lab]))
    extras_a2 = [("H_E", 0.3, [0.3, 0, 0, 0, 0]), ("H_E", 0.5, [0.5, 0, 0, 0, 0]), ("Z", 0.15, [0, 0.15, 0, 0, 0]),
                 ("Z", 0.3, [0, 0.3, 0, 0, 0]), ("drift", 0.05, [0, 0.05, 0.10, 0.15, 0.20]), ("drift", 0.10, [0, 0.10, 0.20, 0.30, 0.40])]
    for lab, tr in truths:
        if not (lab == "none" or lab.startswith("gain 3.20") or lab.startswith("mixed")):
            continue
        for what, size, ex in extras_a2:
            tag = f"{what} {size:+.2f} C" + (" per hold" if what == "drift" else "")
            cells.append((("premise", f"{lab}|{tag}"), designs[A3X2], "aifoundry3", (lab, tr), s3, A3X2, ex, a2c["premise"][f"{lab}|{tag}"]))
    for dname in (A3X1, A3X3):
        for lab, tr in truths:
            cells.append((("sessions", dname, lab), designs[dname], "aifoundry3", (lab, tr), s3, dname, None, a2c["sessions"][dname][lab]))
    for dname in (A2X2, A2X4):
        des = v1["power"][dname]["P_C"]
        for sg in ((s2, s2f, 1.5 * s2) if dname == A2X2 else (s2,)):
            for lab, tr in truths:
                if lab not in ("none", MIXED) and not lab.startswith("gain 4.52") and not lab.startswith("level 0.40"):
                    continue
                cells.append((("aifoundry2", dname, f"{sg:.4f}", lab), des, "aifoundry2", (lab, tr), sg, dname, None,
                              a2c["aifoundry2"][dname]["by_sigma"][f"{sg:.4f}"][lab]))
    OUT["a2_cells"] = {}
    n_eq = 0
    n_name = n_name_bad = 0
    differs = []
    for path, des, kind, truth, sg, seed, ex, com in cells:
        a2v, a3v = run_cell_a3(des, kind, truth, sg, seed, s3 if kind == "aifoundry3" else s2, gamma_arm, extra=ex)
        eq = json.loads(json.dumps(a2v)) == com
        n_eq += eq
        n_name += a3v["pair_by_name"]["sessions_checked"]
        n_name_bad += a3v["pair_by_name"]["differ_from_session_cal"]
        OUT["a2_cells"]["|".join(path)] = {"equals_the_committed_cell": eq, "a3": a3v}
        x = a3v["exact_t"]
        dif = []
        if kind == "aifoundry3":
            if x["N2_H_E_departs_every_session"] != a2v["N2_H_E_departs_every_session"]:
                dif.append(f"N2 {a2v['N2_H_E_departs_every_session']:.1f} -> {x['N2_H_E_departs_every_session']:.1f}")
            if x["HM_CAL_BETTER_no_clause_met"] != a2v["HM_CAL_BETTER_no_clause_met"]:
                dif.append(f"BETTER with no clause met {a2v['HM_CAL_BETTER_no_clause_met']:.1f} -> {x['HM_CAL_BETTER_no_clause_met']:.1f}")
            if x["with_A2_M11_carries"] != a2v["with_A2_M11_carries"]:
                dif.append("A2-3's outcome " + json.dumps({k: (a2v["with_A2_M11_carries"].get(k, 0.0), v) for k, v in x["with_A2_M11_carries"].items()
                                                           if a2v["with_A2_M11_carries"].get(k, 0.0) != v}))
        if dif:
            differs.append(("|".join(path), dif))
        if not eq:
            P(f"   NOT EQUAL to the committed cell: {'|'.join(path)}")
    P(f"   {n_eq} of {len(cells)} cells equal the committed design-power-heat-a2.json cell for cell (as A2's code computes them)")
    P(f"   the pair by name against session_cal, every session of every draw: {n_name} sessions, {n_name_bad} differ")
    P(f"   at the exact t point, the cells whose figures change ({len(differs)}):")
    for pth, dif in differs:
        P(f"     {pth}: " + "; ".join(dif))
    if not differs:
        P("     none")
    OUT["a2_cells_summary"] = {"cells": len(cells), "equal": n_eq, "pair_by_name_sessions": n_name, "pair_by_name_differ": n_name_bad,
                               "exact_t_changes": [{"cell": p, "changes": d} for p, d in differs]}
    if not DEV_DRAWS:
        checks["every cell of design-power-heat-a2.json re-run with A2's functions equals the committed cell"] = n_eq == len(cells)
    checks["the pair by name equals session_cal on every simulated session (every hold scored)"] = n_name_bad == 0

    # the adoption rule at the exact t point
    pl = {lab: OUT["a2_cells"][f"plan|0.0884|{lab}"]["a3"]["exact_t"] for lab, _ in truths}
    patt = ["both: E154's two-term fit (-0.229 C + 5.72%)", "both: E166's two-term fit (+0.395 C - 1.43%)", MIXED]
    adopt_x = {"(i)": a2c["plan"]["0.0884"]["none"]["HM_CAL"]["both"]["BETTER"],
               "(ii)": {l: pl[l]["HM_CAL_BETTER_no_clause_met"] for l in patt},
               "(iii)": pl[MIXED]["with_A2_M11_carries"].get(ENTERS, 0.0),
               "(iv)": pl["none"]["with_A2_M11_carries"].get(ENTERS, 0.0)}
    adopted_x = adopt_x["(i)"] <= 5.0 and all(v >= 80.0 for v in adopt_x["(ii)"].values()) and adopt_x["(iii)"] >= 80.0 and adopt_x["(iv)"] <= 5.0
    OUT["adoption_exact_t"] = {"values": adopt_x, "adopted": adopted_x, "committed_values": a2c["adoption"]["values"]}
    P(f"   A2-6's adoption rule at the exact t point: {json.dumps(adopt_x)}; {'ADOPTED' if adopted_x else 'NOT ADOPTED'} "
      f"(committed: {json.dumps(a2c['adoption']['values'])})")

    # 4. the BOTH-and-differ row
    P()
    P("4. A1-4's path on the plan, E154's fit then E166's: the row 'BOTH, and HM-AG's BOTH form says they differ' against 'the sessions "
      "differ' over every HM-LG verdict (%), the path's own draws")
    OUT["both_and_differ"] = {}
    for sgk in ("0.0884", "0.1325"):
        a3v = OUT["a2_cells"][f"plan|{sgk}|{MIXED}"]["a3"]
        OUT["both_and_differ"][sgk] = {"BOTH_and_the_sessions_differ": a3v["A1_4_BOTH_and_the_sessions_differ"],
                                       "the_sessions_differ_any_verdict": a3v["A1_4_the_sessions_differ_any_verdict"],
                                       "committed_v2_path_the_sessions_differ": v2["path"][sgk][MIXED]["carries"].get("nothing: the sessions differ")}
        P(f"   simulated sigma {sgk} C: BOTH and they differ {a3v['A1_4_BOTH_and_the_sessions_differ']:.1f}; the sessions differ, any verdict "
          f"{a3v['A1_4_the_sessions_differ_any_verdict']:.1f} (design-power-heat-v2.json's path: "
          f"{v2['path'][sgk][MIXED]['carries'].get('nothing: the sessions differ')})")
    if not DEV_DRAWS:
        checks["'the sessions differ' over every verdict equals design-power-heat-v2.json's path"] = all(
            OUT["both_and_differ"][s]["the_sessions_differ_any_verdict"] == OUT["both_and_differ"][s]["committed_v2_path_the_sessions_differ"]
            for s in OUT["both_and_differ"])

    # 5. HM-E144 beside HM-CAL at the plan
    P()
    P("5. HM-E144 beside HM-CAL at the plan (two aifoundry3 sessions, the committed draws): REPEATS = |e(H_E)| / R(H_E) <= 1.5% in "
      "every session; jointly with HM-CAL's verdict and the calibration's entry (exact t); and what it would do as a third "
      "not-wanted clause N3 (reported only)")
    OUT["hm_e144_at_the_plan"] = {}
    for sgk in ("0.0884", "0.1325"):
        P(f"   simulated sigma {sgk} C:")
        OUT["hm_e144_at_the_plan"][sgk] = {}
        for lab, _ in truths:
            a3v = OUT["a2_cells"][f"plan|{sgk}|{lab}"]["a3"]
            he3 = a3v["HM_E144"]
            ent = a3v["exact_t"]["with_A2_M11_carries"].get(ENTERS, 0.0)
            OUT["hm_e144_at_the_plan"][sgk][lab] = he3
            jb = he3["joint_with_HM_CAL"]
            P(f"     {short(lab):30s} REPEATS {he3['repeats_in_every_session']:5.1f} | with BETTER {jb.get('HM-E144 REPEATS | HM-CAL BETTER', 0.0):5.1f}"
              f"  NOT RESOLVED {jb.get('HM-E144 REPEATS | HM-CAL NOT RESOLVED', 0.0):5.1f}  WORSE {jb.get('HM-E144 REPEATS | HM-CAL WORSE', 0.0):5.1f}"
              f" | REPEATS and enters {he3['repeats_and_the_calibration_enters']:5.1f} of enters {ent:5.1f}"
              f" | as N3: enters {he3['if_it_were_a_third_clause_N3']['the calibration enters']:5.1f}, BETTER no clause "
              f"{he3['if_it_were_a_third_clause_N3']['BETTER_no_clause_met']:5.1f}")
    pn = {lab: OUT["hm_e144_at_the_plan"]["0.0884"][lab]["if_it_were_a_third_clause_N3"] for lab, _ in truths}
    n3_adopt = {"(ii)": {l: pn[l]["BETTER_no_clause_met"] for l in patt}, "(iii)": pn[MIXED]["the calibration enters"],
                "(iv)": pn["none"]["the calibration enters"]}
    OUT["n3_what_if_adoption"] = n3_adopt
    P(f"   A2-6's (ii)-(iv) if N3 were a clause (sigma_c): {json.dumps(n3_adopt)}")

    # 6. the premise rows A3 adds
    P()
    P("6. The premise rows A3 adds (the plan, sigma_c, each added after the draw to v2's committed draws for the truth named): H_E read "
      "by the chain as E144's H_H was (e(H_E) = its noise only: minus the truth's a + g P(H_E) in each session), H_E-specific misses "
      "of -0.3 and -0.5 C, and the fp32 pair (H_E and Z) offset by +0.15 and -0.15 C against the int8 later holds. Per row: HM-CAL "
      "BETTER / NOT RESOLVED / WORSE; N1; N2 (exact t); HM-E144 REPEATS; the calibration enters and A1-4's common term (exact t); "
      "the pooled rms over the later holds, median [5%, 95%], and when the calibration enters (calibrated, and unscaled in those draws)")
    OUT["premise_a3"] = {}
    new_rows = []
    for lab, tr in truths:
        ex = [[-(tr[i % len(tr)][0] + tr[i % len(tr)][1] * des_i[0]), 0, 0, 0, 0] for i, des_i in enumerate(designs[A3X2])]
        new_rows.append((lab, "H_E read by the chain (e(H_E) = noise only)", ex))
    for lab, tr in truths:
        if not (lab == "none" or lab.startswith("gain 3.20") or lab.startswith("mixed")):
            continue
        new_rows += [(lab, "H_E -0.30 C", [-0.3, 0, 0, 0, 0]), (lab, "H_E -0.50 C", [-0.5, 0, 0, 0, 0]),
                     (lab, "fp32 pair +0.15 C (H_E and Z)", [0.15, 0.15, 0, 0, 0]),
                     (lab, "fp32 pair -0.15 C (H_E and Z)", [-0.15, -0.15, 0, 0, 0])]
    for lab, tag, ex in new_rows:
        a2v, a3v = run_cell_a3(designs[A3X2], "aifoundry3", (lab, TR[lab]), s3, A3X2, s3, gamma_arm, extra=ex)
        OUT["premise_a3"][f"{lab}|{tag}"] = {"extra_per_session": ex if isinstance(ex[0], list) else [ex, ex], "a2_form": a2v, "a3": a3v}
        if a3v["pair_by_name"]["differ_from_session_cal"]:
            checks["the pair by name equals session_cal on every simulated session (every hold scored)"] = False
        P(line3(f"{short(lab)}, {tag}", a2v, a3v))

    OUT["checks"] = checks
    P()
    P("Checks: " + "; ".join(f"{k}: {'yes' if v else 'NO'}" for k, v in checks.items()))
    if OUT_JSON_A3:
        json.dump(OUT, open(OUT_JSON_A3, "w"), indent=1, sort_keys=True)
        P()
        P(f"wrote {os.path.relpath(OUT_JSON_A3, TOP)}")
    if not all(checks.values()):
        sys.exit(5)


if __name__ == "__main__":
    main()
