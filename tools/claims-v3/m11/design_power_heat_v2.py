#!/usr/bin/env python3
"""Q142(h)'s fix pass: design_power_heat.py's faults fixed in a new file, for M11's heat registration's dated amendment A1
(tools/claims-v3/m11/REGISTRATION.md.dated-note-1.md). Design only: no fit, no hold, no card; it reads committed files and prints.

design_power_heat.py and its output (design-power-heat.txt and .json, lab commit 3c31a91d) stay as committed. This file checks
design_power_heat.py and its committed output against tools/claims-v3/m11/SHA256SUMS-m11 and its ten inputs against
tools/claims-v3/m11/SHA256SUMS, imports it unchanged, reproduces what it does not change, and adds:

  2'. the planned aifoundry3 session on an exact grid. The committed plan ran Q138(t)'s closed_loop on its 0.2 s grid, which
      rounds each piece of H_E's recorded pattern: 3.456 s on and 4.104 s off become 3.4 and 4.2 s (a modelled share of 0.4474
      against the recorded 0.4571, -2.1%); above 51.5 C, 2.965 and 5.015 s become 3.0 and 5.0 s (0.375 against 0.3716, +0.9%).
      Here every piece is a whole number of steps (0.008 s for the cool pattern, 0.005 s for the warm one; the code stops if a
      piece is not), and the hold marks are on the same grid. Each hold's P is read two ways: over describe's window, as the
      committed plan read it (it ends at the hold's last piece, its trailing gap included), and over the registered scoring window
      [b - 300 s, b), b the end of the hold's last process (REGISTRATION.md section 1). The second feeds every table below.
  3'. HM-LG's power at the exact plan, for aifoundry3's three designs, with the committed draws (the same seeded strings, so only
      P differs). aifoundry2's designs do not use the plan; their tables are the committed ones.
  4'. S7-W read as registered, with the fixed threshold sigma_c / sqrt(n_s), sigma_c = 0.0884 C (REGISTRATION.md section 7), at
      every simulated noise: the committed code divided its simulated sigma instead, so its 1.5-sigma S7-W rates are for a looser
      threshold than the registered one. Carried forms: a common gain, a common level (the committed draws), and the two-term
      form (new: amendment A1-4).
  4b'. HM-AG with BOTH's form, F(2(k - 1), n - 2k), on the same draws as the committed gain and level tests (it reproduces their
      shares exactly on the committed plan), with the matched false rates.
  4c. Amended section 6's whole path (A1-4) at the plan, on the committed HM-LG draws: what M11 carries per truth, and the x1.032
      arm's fate (replaced, retired or reported).
  5'. H_E's two readings (HM-E144, HM-HE) at the exact plan, with the committed draws.
  6. The precision for terms (c) and (d), as committed, with what one session's own h1 and k do to it.
  7. Post hoc previews from M10's committed outputs (A1-1): HC1's bias clause; card 1's session heat scales and heat rows; the nine
     pairs' ratios of M10's int8 term-a session scales (a preview of I8P's k, not k).

    python3 -E -B tools/claims-v3/m11/design_power_heat_v2.py . tools/claims-v3/m11/design-power-heat-v2.json > tools/claims-v3/m11/design-power-heat-v2.txt

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
OUT_JSON_V2 = sys.argv[2] if len(sys.argv) > 2 else None
sys.dont_write_bytecode = True
HERE = os.path.join(TOP, "tools", "claims-v3", "m11")
V1_REL = "tools/claims-v3/m11/design_power_heat.py"
V1_OUT_REL = "tools/claims-v3/m11/design-power-heat.json"
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


M11_OWN = hash_list("SHA256SUMS-m11")
for rel in (V1_REL, V1_OUT_REL):
    if sha(os.path.join(TOP, rel)) != M11_OWN.get(rel):
        P(f"STOP: {rel} differs from tools/claims-v3/m11/SHA256SUMS-m11")
        sys.exit(3)

sys.argv = [V1_REL, TOP]          # design_power_heat reads argv[1] (the top directory) at import; its main() is never called
sys.path.insert(0, HERE)
import design_power_heat as D  # noqa: E402  (the committed design code, unchanged)
import numpy as np  # noqa: E402

PE, HM, DPG = D.PE, D.HM, D.DPG
DRAWS = D.DRAWS
VERDICTS = D.VERDICTS
COOL_DT, WARM_DT = 0.008, 0.005     # whole steps for 3.456 / 4.104 s (cool) and 2.965 / 5.015 s (warm), 5.6 / 0.2 s and the rests
GAMMA_MIN, LEVEL_MIN = 0.010, 0.10  # REGISTRATION.md section 6
ROOMS = (49.5, 51.2, 51.5, 52.0, 53.0)
A3X2 = "A3 x2 (the plan: two aifoundry3 sessions, rooms 51.2 and 52.0 C)"
A3X1 = "A3 x1 (one aifoundry3 session, room 51.2 C)"
A3X3 = "A3 x3 (three aifoundry3 sessions)"
OUT = {"_note": "Q142(h)'s fix pass (dated amendment A1): design_power_heat.py's faults fixed in a new file; design only (no fit, "
                "no hold, no card); printed by design_power_heat_v2.py"}


# ---------------------------------------------------------------------------------------------- 2'. the plan on an exact grid
def grid_dt(room):
    """the cool pattern runs at rooms up to 51.5 C (design_power_heat.a3_holds), the warm one above"""
    return COOL_DT if room <= 51.5 else WARM_DT


def steps_of(d, dt):
    m = d / dt
    k = int(round(m))
    if abs(m - k) > 1e-6:
        P(f"STOP: a piece of {d!r} s is not a whole number of {dt} s steps")
        sys.exit(4)
    return k


def a3_schedule_on(holds, r0_min, rests_min, dt):
    """design_power_heat.a3_schedule_rests' schedule, the same pieces, with the marks counted in whole steps of dt (closed_loop
    rounds each piece to int(round(d / dt)) steps): t0 the start of the hold's first process, t1 the end of its last piece (its
    trailing gap included, describe's window), b the end of its last process (the registered window)"""
    pcs, marks, k = [], [], 0
    pcs.append((r0_min * 60.0, 0.0))
    k += steps_of(r0_min * 60.0, dt)
    for i, h in enumerate(holds):
        S = PE.S78[h["item"]]["mean"]
        dur = h["minutes"] * 60.0
        k0 = k
        if "duty" in h:
            cyc, on = h["duty"]["cycle_s"], h["duty"]["compute_s"]
            n = int(dur // cyc)
            for _ in range(n):
                pcs += [(on, S), (cyc - on, 0.0)]
            k_on, k_off = steps_of(on, dt), steps_of(cyc - on, dt)
            share = on / cyc
        else:
            n = int(dur // (PE.LAUNCH_S + PE.GAP_S))
            for _ in range(n):
                pcs += [(PE.LAUNCH_S, S), (PE.GAP_S, 0.0)]
            k_on, k_off = steps_of(PE.LAUNCH_S, dt), steps_of(PE.GAP_S, dt)
            share = PE.LAUNCH_S / (PE.LAUNCH_S + PE.GAP_S)
        k += n * (k_on + k_off)
        marks.append({"name": h["name"], "item": h["item"], "t0": k0 * dt, "t1": k * dt, "b": (k - k_off) * dt, "S_E78_W": S,
                      "share": share, "share_on_grid": k_on / (k_on + k_off), "pieces": n})
        pcs.append((rests_min[i] * 60.0, 0.0))
        k += steps_of(rests_min[i] * 60.0, dt)
    return pcs, marks, k * dt


KEYS = ("hold", "item", "share", "S_E78_W", "S_eff_W", "carried_in_C", "plateau_rise_C", "plateau_C_abs", "peak_C_abs",
        "plateau_board_rise_W")


def plan_exact(room):
    dt = grid_dt(room)
    pcs, marks, total = a3_schedule_on(D.a3_holds(room), D.A3_R0_MIN, D.A3_RESTS_MIN, dt)
    g, T, Pr = HM.closed_loop(pcs, PE.TAU, PE.R3, room, HM.law_a3, dt=dt)
    rows = []
    for mk in marks:
        d = PE.describe(g, T, Pr, mk, room)
        row = {k: d[k] for k in KEYS}
        m = (g >= mk["t0"] - HM.ANCHOR_S) & (g < mk["t0"])
        base = float(np.mean(T[m]))
        mb = (g >= mk["b"] - 300.0) & (g < mk["b"])
        row["P_C"] = round(float(np.mean(T[mb])) - base, 3)              # the registered window [b - 300 s, b)
        row["plateau_C_abs_b"] = round(float(np.mean(T[mb])), 2)
        row["share_on_grid"] = round(mk["share_on_grid"], 4)
        row["pieces"] = mk["pieces"]
        rows.append(row)
    return {"room_C": room, "dt_s": dt, "plan_minutes": round(total / 60.0, 2), "card_minutes": round(total / 60.0 + D.SMOKE_MIN_A3, 2),
            "holds": rows}


def grid_share_0p2(room):
    """the share closed_loop models on its 0.2 s grid for H_E's pattern at this room (q() of each piece)"""
    h = D.a3_holds(room)[0]["duty"]
    on, off = PE.q(h["compute_s"]), PE.q(h["cycle_s"] - h["compute_s"])
    return on / (on + off), h["compute_s"] / h["cycle_s"]


# ---------------------------------------------------------------------------------------------- 4'. S7-W as registered
def s7w_rates_c(design, truths, sigma, seed, carried, sigma_c):
    """design_power_heat.s7w_rates' draws (the same seeded strings), with the registered threshold sigma_c / sqrt(n_s) and a third
    carried form, 'both': the two-term model e = a + g P fitted by least squares on the other sessions' holds"""
    out = {}
    for lab, tr in truths:
        rng = random.Random(f"M11-S7W|{seed}|{carried}|{sigma:.4f}|{lab}")
        hit = 0
        for _ in range(DRAWS):
            hit += s7w_met(D.sim_sessions(design, tr, sigma, rng), carried, sigma_c)
        out[lab] = round(100.0 * hit / DRAWS, 1)
    return out


def s7w_met(groups, form, sigma_c):
    for k, pts in groups.items():
        other = [p for j, v in groups.items() if j != k for p in v]
        if form == "gain":
            gam = sum(e * p for p, e in other) / sum(p * p for p, e in other)
            new = [e - gam * p for p, e in pts]
        elif form == "level":
            lev = sum(e for _, e in other) / len(other)
            new = [e - lev for _, e in pts]
        else:
            a0, b0, _, _ = D.ls_fit(other)
            new = [e - a0 - b0 * p for p, e in pts]
        if D.rms(new) - D.rms([e for _, e in pts]) > sigma_c / math.sqrt(len(pts)):
            return True
    return False


# ---------------------------------------------------------------------------------------------- 4b'. HM-AG with BOTH's form
def ag_stats(groups, k, n):
    """the three HM-AG statistics on one draw, as design_power_heat.agree_rates computes the first two"""
    rss_b = rss_g = rss_l = 0.0
    allp = [p for v in groups.values() for p in v]
    gc = sum(e * p for p, e in allp) / sum(p * p for p, e in allp)
    lc = sum(e for _, e in allp) / len(allp)
    rss_cg = sum((e - gc * p) ** 2 for p, e in allp)
    rss_cl = sum((e - lc) ** 2 for _, e in allp)
    a1, b1, _, _ = D.ls_fit(allp)
    rss_cb = sum((e - a1 - b1 * p) ** 2 for p, e in allp)
    for pts in groups.values():
        a0, b0, _, _ = D.ls_fit(pts)
        rss_b += sum((e - a0 - b0 * p) ** 2 for p, e in pts)
        g0 = sum(e * p for p, e in pts) / sum(p * p for p, e in pts)
        rss_g += sum((e - g0 * p) ** 2 for p, e in pts)
        m0 = sum(e for _, e in pts) / len(pts)
        rss_l += sum((e - m0) ** 2 for _, e in pts)
    s2 = rss_b / (n - 2 * k)
    return {"gain": ((rss_cg - rss_g) / (k - 1)) / s2, "level": ((rss_cl - rss_l) / (k - 1)) / s2,
            "both": ((rss_cb - rss_b) / (2 * (k - 1))) / s2}


def agree_rates_v2(design, truths, sigma, seed):
    """design_power_heat.agree_rates' draws (the same seeded strings), adding BOTH's form against F(2(k - 1), n - 2k)"""
    k = len(design)
    n = sum(len(s) for s in design)
    crit = DPG.f_ppf(0.95, k - 1, n - 2 * k)
    crit_b = DPG.f_ppf(0.95, 2 * (k - 1), n - 2 * k)
    out = {}
    for lab, tr in truths:
        rng = random.Random(f"M11-AG|{seed}|{sigma:.4f}|{lab}")
        dg = dl = db = 0
        for _ in range(DRAWS):
            st = ag_stats(D.sim_sessions(design, tr, sigma, rng), k, n)
            dg += st["gain"] > crit
            dl += st["level"] > crit
            db += st["both"] > crit_b
        out[lab] = {"gains differ": round(100.0 * dg / DRAWS, 1), "levels differ": round(100.0 * dl / DRAWS, 1),
                    "both differ": round(100.0 * db / DRAWS, 1)}
    return out, crit, crit_b


# ---------------------------------------------------------------------------------------------- 4c. amended section 6's path
def t95(df):
    return math.sqrt(DPG.f_ppf(0.95, 1, df))


def fit_gain(pts):
    """gamma_c = sum e P / sum P^2 over the holds, its 95% interval at t(n - 1) (REGISTRATION.md section 6, GAIN)"""
    n = len(pts)
    spp = sum(p * p for p, _ in pts)
    g = sum(e * p for p, e in pts) / spp
    h = t95(n - 1) * math.sqrt(sum((e - g * p) ** 2 for p, e in pts) / (n - 1) / spp)
    return g, g - h, g + h


def fit_level(pts):
    """abar_c = the mean e over the holds, its 95% interval at t(n - 1) (section 6, LEVEL)"""
    n = len(pts)
    m = sum(e for _, e in pts) / n
    h = t95(n - 1) * math.sqrt(sum((e - m) ** 2 for _, e in pts) / (n - 1) / n)
    return m, m - h, m + h


def fit_both(pts):
    """e = abar_c + gamma_c P by least squares over the holds, each 95% interval at t(n - 2) (A1-4)"""
    n = len(pts)
    a, g, mx, sxx = D.ls_fit(pts)
    s2 = sum((e - a - g * p) ** 2 for p, e in pts) / (n - 2)
    t = t95(n - 2)
    ha, hg = t * math.sqrt(s2 * (1.0 / n + mx * mx / sxx)), t * math.sqrt(s2 / sxx)
    return (a, a - ha, a + ha), (g, g - hg, g + hg)


def passes(est, size):
    v, lo, hi = est
    return abs(v) >= size and (lo > 0.0 or hi < 0.0)


OUTCOMES = ("both enter", "gain enters", "gain enters (BOTH, refitted alone)", "level enters", "level enters (BOTH, refitted alone)",
            "nothing: the sessions differ", "nothing: its size or interval", "nothing: S7-W met", "nothing: NOT SEPARATED",
            "nothing: NOT SCORED", "nothing: one session (a candidate)")
FATES = ("replaced", "retired", "reported")


def decide(groups, res, k, n, crit, crit_b, sigma_c):
    """amended section 6 (A1-4) on one draw: (what M11 carries, the x1.032 arm's fate on aifoundry3)"""
    v = res["verdict"]
    if v == "NOT SCORED":
        return "nothing: NOT SCORED", "reported"
    if v == "NOT SEPARATED":
        return "nothing: NOT SEPARATED", ("retired" if res["null"] == "the sessions agree" else "reported")
    arm_if_none = "retired" if v == "LEVEL" else "reported"
    if k < 2:
        return "nothing: one session (a candidate)", arm_if_none
    allp = [p for g in groups.values() for p in g]
    st = ag_stats(groups, k, n)
    if v == "GAIN":
        if st["gain"] > crit:
            return "nothing: the sessions differ", "reported"
        if not passes(fit_gain(allp), GAMMA_MIN):
            return "nothing: its size or interval", "reported"
        if s7w_met(groups, "gain", sigma_c):
            return "nothing: S7-W met", "reported"
        return "gain enters", "replaced"
    if v == "LEVEL":
        if st["level"] > crit:
            return "nothing: the sessions differ", "retired"
        if not passes(fit_level(allp), LEVEL_MIN):
            return "nothing: its size or interval", "retired"
        if s7w_met(groups, "level", sigma_c):
            return "nothing: S7-W met", "retired"
        return "level enters", "retired"
    if st["both"] > crit_b:
        return "nothing: the sessions differ", "reported"
    ea, eg = fit_both(allp)
    pa, pg = passes(ea, LEVEL_MIN), passes(eg, GAMMA_MIN)
    if pa and pg:
        if s7w_met(groups, "both", sigma_c):
            return "nothing: S7-W met", "reported"
        return "both enter", "replaced"
    if pg:
        if not passes(fit_gain(allp), GAMMA_MIN):
            return "nothing: its size or interval", "reported"
        if s7w_met(groups, "gain", sigma_c):
            return "nothing: S7-W met", "reported"
        return "gain enters (BOTH, refitted alone)", "replaced"
    if pa:
        if not passes(fit_level(allp), LEVEL_MIN):
            return "nothing: its size or interval", "reported"
        if s7w_met(groups, "level", sigma_c):
            return "nothing: S7-W met", "reported"
        return "level enters (BOTH, refitted alone)", "reported"
    return "nothing: its size or interval", "reported"


def path_rates(design, truths, sigma, seed, sigma_c):
    """on design_power_heat.power_table's draws (the same seeded strings): HM-LG's verdict, then amended section 6"""
    k = len(design)
    n = sum(len(s) for s in design)
    crit = DPG.f_ppf(0.95, k - 1, n - 2 * k) if k >= 2 else None
    crit_b = DPG.f_ppf(0.95, 2 * (k - 1), n - 2 * k) if k >= 2 else None
    out = {}
    for lab, tr in truths:
        rng = random.Random(f"M11-HM-LG|{seed}|{sigma:.4f}|{lab}")
        cnt = {o: 0 for o in OUTCOMES}
        fate = {f: 0 for f in FATES}
        verd = {x: 0 for x in VERDICTS}
        for _ in range(DRAWS):
            groups = D.sim_sessions(design, tr, sigma, rng)
            res = DPG.lg_test(groups, min_tiles=D.MIN_HOLDS, min_span_w=D.MIN_SPAN_C, min_df=D.MIN_DF, detail=True)
            verd[res["verdict"]] += 1
            o, f = decide(groups, res, k, n, crit, crit_b, sigma_c)
            cnt[o] += 1
            fate[f] += 1
        out[lab] = {"verdicts": {x: round(100.0 * c / DRAWS, 1) for x, c in verd.items()},
                    "carries": {o: round(100.0 * c / DRAWS, 1) for o, c in cnt.items()},
                    "arm": {f: round(100.0 * c / DRAWS, 1) for f, c in fate.items()}}
    return out


# ---------------------------------------------------------------------------------------------- main
def truths_as_committed():
    """design_power_heat.main's truths, line for line (their labels seed the committed draws)"""
    s7 = json.load(open(os.path.join(D.M10D, "section7-m10.json")))["section7"]["d"]
    g3 = s7["clause_1_gamma_sign_differs_between_card_kinds"]["per_card_kind_gamma_all_holds"]["aifoundry3"]
    g2 = s7["clause_1_gamma_sign_differs_between_card_kinds"]["per_card_kind_gamma_all_holds"]["aifoundry2"]
    gc = s7["variants"]["common"]["gamma_all_holds"]["all"]
    return [("none", [(0.0, 0.0)]),
            (f"gain {100 * g3:.2f}% (M10's aifoundry3 gamma)", [(0.0, g3)]),
            (f"gain {100 * gc:.2f}% (the x1.032 arm)", [(0.0, gc)]),
            (f"gain {100 * g2:.2f}% (M10's aifoundry2 gamma)", [(0.0, g2)]),
            ("level 0.15 C", [(0.15, 0.0)]),
            ("level 0.27 C (E154's and E166's level alone)", [(0.27, 0.0)]),
            ("level 0.40 C (E166's two-term a)", [(0.395, 0.0)]),
            ("both: E154's two-term fit (-0.229 C + 5.72%)", [(-0.229, 0.0572)]),
            ("both: E166's two-term fit (+0.395 C - 1.43%)", [(0.395, -0.0143)]),
            ("mixed: E154's fit, then E166's", [(-0.229, 0.0572), (0.395, -0.0143)])]


def short(lab):
    return lab.split(" (")[0]


def main():
    committed = json.load(open(os.path.join(TOP, V1_OUT_REL)))
    rows, bad = D.check_inputs()
    P("M11's heat registration (Q142(h)), dated amendment A1: design_power_heat.py's faults fixed in a new file (design only: no fit, "
      "no hold, no card)")
    P()
    P(f"Checked first: {V1_REL} and its committed output {V1_OUT_REL} against tools/claims-v3/m11/SHA256SUMS-m11: OK")
    P("Inputs (sha256; 'OK' = as tools/claims-v3/m11/SHA256SUMS lists it):")
    for rel, s, st in rows:
        P(f"   {s}  {rel}  [{st}]")
    OUT["inputs"] = [{"path": rel, "sha256": s, "check": st} for rel, s, st in rows]
    OUT["checked_first"] = {V1_REL: M11_OWN[V1_REL], V1_OUT_REL: M11_OWN[V1_OUT_REL]}
    if bad:
        P("   STOP: an input differs from the registration's list: " + ", ".join(bad))
        sys.exit(3)
    checks = {}
    truths = truths_as_committed()
    checks["truth labels as committed"] = sorted(lab for lab, _ in truths) == sorted(committed["truths"])

    nz = D.noise()
    s3, s2 = nz["a3"]["sigma_C"], nz["a2"]["sigma_C"]
    checks["noise as committed"] = (round(s3, 10) == round(committed["noise"]["a3"]["sigma_C"], 10)
                                    and round(s2, 10) == round(committed["noise"]["a2"]["sigma_C"], 10))
    OUT["noise_sigma_C"] = {"aifoundry3": s3, "aifoundry2": s2, "aifoundry2_readout_floor": nz["a2"]["readout_floor_sigma_C"]}
    P()
    P(f"1. The noise (unchanged; design_power_heat.noise): aifoundry3 sigma_c {s3:.4f} C over {nz['a3']['n_residuals']} scaled residuals "
      f"(E144 mean, 2 holds: 1 degree of freedom; E154 two-term, 5: 3; E166 two-term, 4: 2; in all 6); aifoundry2 {s2:.4f} C over "
      f"{nz['a2']['n_residuals']}; readout floor {nz['a2']['readout_floor_sigma_C']:.4f} C")

    P()

    P("2'. The planned aifoundry3 session on an exact grid (each piece a whole number of steps; the marks on the same grid). "
      "P = the plateau rise over the anchor, over the registered window [b - 300 s, b), b the end of the hold's last process; "
      "P(t1) = over describe's window, as the committed plan read it; '0.2 s' = the committed plan (design_power_heat.plan_a3, reproduced)")
    plans_ex, plans_02 = {}, {}
    rep_plan = True
    for room in ROOMS:
        ex = plan_exact(room)
        o2 = D.plan_a3(room)
        plans_ex[str(room)], plans_02[str(room)] = ex, o2
        if str(room) in committed["plan_a3"]:
            rep_plan = rep_plan and (json.dumps(o2, sort_keys=True) == json.dumps(committed["plan_a3"][str(room)], sort_keys=True))
        s02, srec = grid_share_0p2(room)
        P(f"   room {room} C: grid {ex['dt_s']} s; plan {ex['plan_minutes']:.2f} min + smoke {D.SMOKE_MIN_A3} = {ex['card_minutes']:.2f} "
          f"card-minutes (0.2 s grid: {o2['card_minutes']:.2f}); H_E's share on the grid {ex['holds'][0]['share_on_grid']:.4f} against the "
          f"recorded {srec:.4f} (0.2 s grid: {s02:.4f}, {100 * (s02 / srec - 1):+.1f}%)")
        for h, h2 in zip(ex["holds"], o2["holds"]):
            P(f"     {h['hold']:3s} {h['item']:14s} carried-in {h['carried_in_C']:+.3f} C  P {h['P_C']:6.3f} C  P(t1) {h['plateau_rise_C']:6.3f}"
              f"  plateau {h['plateau_C_abs_b']:.2f}  peak {h['peak_C_abs']:.2f} C  | 0.2 s: P(t1) {h2['plateau_rise_C']:6.3f}, peak {h2['peak_C_abs']:.2f}")
    checks["0.2 s plan reproduces the committed plan_a3 at 49.5, 51.2, 52.0 and 53.0 C"] = rep_plan
    OUT["plan_a3_exact"] = plans_ex
    OUT["plan_a3_0p2_reproduced"] = plans_02
    worst = max(((r, plans_ex[str(r)]["holds"][0]["peak_C_abs"]) for r in ROOMS if r <= 53.0), key=lambda x: x[1])
    others = max(h["peak_C_abs"] for r in ROOMS for h in plans_ex[str(r)]["holds"][1:])
    OUT["peaks"] = {"H_E_highest": {"room_C": worst[0], "peak_C": worst[1]}, "others_highest_C": others}
    P(f"   highest planned in-launch peak (34-sensor mean) at an admitted room: H_E {worst[1]:.2f} C at {worst[0]} C; every other hold "
      f"at most {others:.2f} C (the hold line 72 C, the launch gate 70 C on the firmware's reading)")

    p3 = [h["P_C"] for h in plans_ex["51.2"]["holds"]]
    p3w = [h["P_C"] for h in plans_ex["52.0"]["holds"]]
    p3c = [h["plateau_rise_C"] for h in plans_02["51.2"]["holds"]]
    p3wc = [h["plateau_rise_C"] for h in plans_02["52.0"]["holds"]]
    designs = {A3X2: [p3, p3w], A3X1: [p3], A3X3: [p3, p3w, p3]}
    designs_c = {A3X2: [p3c, p3wc]}
    OUT["designs_exact_P_C"] = designs

    P()

    P(f"3'. HM-LG's power at the exact plan (the registered test, lg_test with >= {D.MIN_HOLDS} holds a session spanning >= "
      f"{D.MIN_SPAN_C} C of P, n - 2k >= {D.MIN_DF}; {DRAWS} draws a cell, the committed draws). Shares in %: " + " / ".join(VERDICTS)
      + "; [committed] = design-power-heat.json at the 0.2 s plan")
    OUT["power"] = {}
    for dname, des in designs.items():
        OUT["power"][dname] = {"P_C": des, "by_sigma": {}}
        P()
        P(f"   {dname}: P per session " + " | ".join(", ".join(f"{p:.2f}" for p in s) for s in des))
        for sg in (s3, 1.5 * s3):
            tab = D.power_table(des, truths, sg, dname)
            OUT["power"][dname]["by_sigma"][f"{sg:.4f}"] = tab
            com = committed["power"][dname]["by_sigma"][f"{sg:.4f}"]
            P(f"     sigma {sg:.4f} C:")
            for lab, v in tab.items():
                P(f"       {lab:48s} " + " / ".join(f"{v[x]:5.1f}" for x in VERDICTS)
                  + "   [committed " + " / ".join(f"{com[lab][x]:.1f}" for x in VERDICTS[:4]) + "]")

    P()

    P("4'. S7-W as registered: the held-out session's rms with the carried term minus without exceeds sigma_c / sqrt(n_s), sigma_c "
      f"{s3:.4f} C fixed (REGISTRATION.md section 7), at each simulated noise; share of draws in which any held-out session does, at "
      "the plan (A3 x2), the committed draws for a gain and a level; 'both' (A1-4) the two-term form fitted on the other sessions")
    OUT["s7w_registered_threshold"] = {}
    rep_s7 = True
    for plan_lab, des in (("exact plan", designs[A3X2]), ("0.2 s plan", designs_c[A3X2])):
        for carried in ("gain", "level", "both"):
            for sg in (s3, 1.5 * s3):
                r = s7w_rates_c(des, truths, sg, "A3x2", carried, s3)
                OUT["s7w_registered_threshold"][f"{plan_lab}|{carried}|{sg:.4f}"] = r
                if plan_lab == "0.2 s plan" and carried != "both" and abs(sg - s3) < 1e-12:
                    rep_s7 = rep_s7 and (r == committed["s7w"][f"{carried}|{sg:.4f}"])
                P(f"   {plan_lab}, carried {carried}, simulated sigma {sg:.4f} C: " + "; ".join(f"{short(lab)} {v:.1f}" for lab, v in r.items()))
    checks["S7-W at sigma_c on the 0.2 s plan reproduces the committed gain and level rates"] = rep_s7
    P("   (the committed 1.5-sigma rates divided the simulated 1.5 sigma, not sigma_c: design-power-heat.json s7w|*|0.1325)")

    P()

    P("4b'. HM-AG: do the plan's two aifoundry3 sessions share one gain / one level / one two-term form? Share of draws in which the "
      "F test says they differ (gain and level against F(k - 1, n - 2k), both against F(2(k - 1), n - 2k)), on the committed draws")
    OUT["agree_v2"] = {}
    rep_ag = True
    for plan_lab, des in (("0.2 s plan", designs_c[A3X2]), ("exact plan", designs[A3X2])):
        for sg in (s3, 1.5 * s3):
            ag, crit, crit_b = agree_rates_v2(des, truths, sg, "A3x2")
            OUT["agree_v2"][f"{plan_lab}|{sg:.4f}"] = {"F_point": crit, "F_point_both": crit_b, "rates": ag}
            if plan_lab == "0.2 s plan":
                com = committed["agree"][f"{sg:.4f}"]["rates"]
                rep_ag = rep_ag and all(ag[l]["gains differ"] == com[l]["gains differ"] and ag[l]["levels differ"] == com[l]["levels differ"]
                                        for l in com)
            P(f"   {plan_lab}, sigma {sg:.4f} C (F points {crit:.3f} and {crit_b:.3f}): " + "; ".join(
                f"{short(lab)} {v['gains differ']:.1f} / {v['levels differ']:.1f} / {v['both differ']:.1f}" for lab, v in ag.items()))
    checks["HM-AG on the 0.2 s plan reproduces the committed gain and level shares"] = rep_ag
    matched = {}
    for sg in (s3, 1.5 * s3):
        r = OUT["agree_v2"][f"exact plan|{sg:.4f}"]["rates"]
        g_m = [r[l]["gains differ"] for l, _ in truths if l == "none" or l.startswith("gain")]
        l_m = [r[l]["levels differ"] for l, _ in truths if l == "none" or l.startswith("level")]
        b_m = [r[l]["both differ"] for l, _ in truths if not l.startswith("mixed")]
        matched[f"{sg:.4f}"] = {"gain test under a shared gain or none": [min(g_m), max(g_m)],
                                "level test under a shared level or none": [min(l_m), max(l_m)],
                                "both test under any shared truth": [min(b_m), max(b_m)],
                                "power under the mixed truth (gain / level / both)": [r["mixed: E154's fit, then E166's"][x] for x in
                                                                                      ("gains differ", "levels differ", "both differ")]}
        P(f"   matched false rates at the exact plan, sigma {sg:.4f} C: " + "; ".join(f"{k} {v[0]:.1f}-{v[1]:.1f}" if len(v) == 2 else
                                                                               f"{k} " + " / ".join(f"{x:.1f}" for x in v)
                                                                               for k, v in matched[f"{sg:.4f}"].items()))
    OUT["agree_matched"] = matched

    P()

    P("4c. Amended section 6 (A1-4) at the plan (A3 x2, the exact plan), on the committed HM-LG draws: what M11 carries on aifoundry3, "
      "and the x1.032 arm's fate, in % of draws. S7-W at sigma_c fixed.")
    OUT["path"] = {}
    rep_path = True
    for sg in (s3, 1.5 * s3):
        pr = path_rates(designs[A3X2], truths, sg, A3X2, s3)
        OUT["path"][f"{sg:.4f}"] = pr
        P(f"   simulated sigma {sg:.4f} C:")
        for lab, v in pr.items():
            rep_path = rep_path and (v["verdicts"] == OUT["power"][A3X2]["by_sigma"][f"{sg:.4f}"][lab])
            car = "; ".join(f"{o} {x:.1f}" for o, x in v["carries"].items() if x > 0)
            P(f"     {short(lab):28s} carries: {car} | arm: " + " / ".join(f"{f} {v['arm'][f]:.1f}" for f in FATES))
    checks["the path's HM-LG verdicts equal the power table's (same draws)"] = rep_path

    P()

    P("5'. H_E in one aifoundry3 session at the exact plan (room 51.2 C): HM-E144 = |e/R| <= 1.5%; HM-HE = e(H_E) outside the 95% "
      "prediction interval of the two-term fit on the other four holds. Shares in %, the committed draws, with a hold-specific miss "
      "delta on H_E")
    he = D.he_rates(p3, 0, [(lab, tr) for lab, tr in truths if lab.split(" ")[0] in ("none", "gain", "level")], s3, "A3x1")
    OUT["he"] = he
    for k, v in he.items():
        c = committed["he"][k]
        P(f"   {k:62s} HM-E144 inside {v['HM-E144 inside 1.5%']:5.1f}   HM-HE departs {v['HM-HE departs']:5.1f}"
          f"   [committed {c['HM-E144 inside 1.5%']:.1f} / {c['HM-HE departs']:.1f}]")

    h = json.load(open(os.path.join(D.M10D, "heldout-m10.json")))
    c1 = h["heat_c1"]
    pc = c1["per_card"]["aifoundry1-c1"]
    i8 = h["power"]["int8"]["paired_bootstrap"]["B+a"]["per_card"]["c1"]
    sets = json.load(open(os.path.join(TOP, "tools", "claims-v3", "kinds", "blind8", "sets-blind8.json")))["sizes"]
    hw_c = 0.5 * (pc["hi95"] - pc["lo95"]) * math.sqrt(pc["n_kinds"] / sets["N1"])
    hw_i = 0.5 * (i8["hi95"] - i8["lo95"]) * math.sqrt(i8["n_kinds"] / sets["I1"])
    sc = c1["session_heat_scales_all_rows"]
    c1s = sorted((v, k.split("|")[0]) for k, v in sc.items() if k.endswith("aifoundry1-c1"))
    OUT["precision_c_d"] = {"c_half_width_at_N1_C": round(hw_c, 4), "d_half_width_at_I1_W": round(hw_i, 4), "N1": sets["N1"], "I1": sets["I1"],
                            "card1_session_heat_scales_sorted": c1s}
    P()
    P(f"6. Precision (as committed): (c) HC1-B's half-width at N1's {sets['N1']} tiles about {hw_c:.3f} C (M10's held-out d "
      f"{pc['d_rms_w']:+.4f} C over {pc['n_kinds']} kinds); (d) I8P-B's at I1's {sets['I1']} tiles about {hw_i:.4f} W. Both scale M10's pooled "
      "intervals: one session's effect scales with that session's own |h1 - 1| (or |k - 1|). Card 1's 16 session heat scales "
      "(heat_c1.session_heat_scales_all_rows), sorted: " + ", ".join(f"{s} {v:.3f}" for v, s in c1s))

    rows_by = c1["rows_by_session"]
    c1rows = {k.split("|")[0]: v for k, v in rows_by.items() if k.endswith("aifoundry1-c1")}
    pre = {"HC1_bias_without_C": c1["base_refit_loko"]["aifoundry1-c1"]["bias_c"],
           "HC1_bias_with_C": c1["with_session_heat_scale_loko"]["aifoundry1-c1"]["bias_c"],
           "HC1_rms_without_C": c1["base_refit_loko"]["aifoundry1-c1"]["rms_c"],
           "HC1_rms_with_C": c1["with_session_heat_scale_loko"]["aifoundry1-c1"]["rms_c"],
           "card1_sessions": len(c1rows), "card1_sessions_with_10_rows": sum(1 for v in c1rows.values() if v >= 10),
           "card1_rows": sum(c1rows.values()), "per_session_d_in_heldout_m10": False}
    ts = h["power"]["int8"]["session_scales_term_a_all_rows"]
    na = h["power"]["int8"]["session_scale_anchor_counts"]
    pairs = [("E82", "E78"), ("E91", "E86"), ("E131", "E95"), ("E93", "E121"), ("E108", "E122"), ("E94", "E123"), ("E142", "E141"),
             ("E157", "E153"), ("E164", "E163")]
    pv = []
    for s1, s0 in pairs:
        a, b = ts[f"{s1}|c1"], ts[f"{s0}|a3"]
        pv.append({"pair": f"{s1}/{s0}", "card1_scale": a, "a3_scale": b, "ratio": round(a / b, 5),
                   "anchors": [na[f"{s1}|c1"], na[f"{s0}|a3"]]})
    rs = sorted(x["ratio"] for x in pv)
    pre["I8P_preview_pairs"] = pv
    pre["I8P_preview_ratio_range"] = [rs[0], rs[-1]]
    pre["I8P_preview_ratio_median"] = rs[len(rs) // 2]
    OUT["posthoc_previews"] = pre
    P()
    P("7. Post hoc previews from M10's committed outputs (A1-1; not M11 readings):")
    P(f"   HC1's bias clause on committed rows: card 1's held-out heat bias {pre['HC1_bias_without_C']:+.4f} C without the session scale, "
      f"{pre['HC1_bias_with_C']:+.4f} C with it (rms {pre['HC1_rms_without_C']:.4f} -> {pre['HC1_rms_with_C']:.4f} C): the sign changes and "
      "the size falls, so 'does not change sign and grow in size' passes")
    P(f"   HC1's two-thirds clause: heldout-m10.json holds no per-session d; card 1 has {pre['card1_sessions']} sessions, "
      f"{pre['card1_sessions_with_10_rows']} with at least 10 heat rows ({pre['card1_rows']} rows)")
    P("   I8P's preview: the ratio of M10's int8 term-a session scales (power.int8.session_scales_term_a_all_rows; all rows, each "
      "session's median over its int8 anchors), card-1 session / its aifoundry3 pair, with each session's anchor count: "
      + "; ".join(f"{x['pair']} {x['card1_scale']:.5f} / {x['a3_scale']:.5f} = {x['ratio']:.4f} ({x['anchors'][0]}, {x['anchors'][1]})" for x in pv))
    P(f"   range {rs[0]:.4f}-{rs[-1]:.4f}, median {pre['I8P_preview_ratio_median']:.4f}. Not k: k takes each anchor's ratio and each fold's D-hat.")

    OUT["checks"] = checks
    P()
    P("Checks: " + "; ".join(f"{k}: {'yes' if v else 'NO'}" for k, v in checks.items()))
    if OUT_JSON_V2:
        json.dump(OUT, open(OUT_JSON_V2, "w"), indent=1, sort_keys=True)
        P()
        P(f"wrote {os.path.relpath(OUT_JSON_V2, TOP)}")
    if not all(checks.values()):
        sys.exit(5)


if __name__ == "__main__":
    main()
