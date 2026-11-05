#!/usr/bin/env python3
"""Q142(h), M11's heat registration (tools/claims-v3/m11/REGISTRATION.md), design only: the power of HM-LG, the test of heat over
minutes as a session level against a gain, at the planned hold design, computed the way P8-LG's power was
(tools/claims-v3/m10/pool8/design_power_groups.py: the same two F tests through its own lg_test, unchanged; 5,000 draws a cell;
seeded strings), from the committed sessions' noise. No fit, no hold, no card, no device: it reads committed files and prints.

What it reads (paths relative to the repository's top directory, argv[1]); each file's sha256 is printed, and checked against
tools/claims-v3/m11/SHA256SUMS when that file names it:
  docs/reports/data/2026-11-04-q142m-m10/heldout-m10.json      heat_d_chain_gain.holds: per hold P_C (the frozen chain's rise given
                                                               the measured watts), e_C (measured - chain), M10's `fitted` flag
  docs/reports/data/2026-11-02-q138t-heat-model/cv-q138t.json  a2: E111's and E133's int8 holds, each day read by the chain fitted
                                                               on the other day (the only committed aifoundry2 sessions with two
                                                               holds of one kind in the 800 MHz regime)
  docs/reports/data/2026-11-02-q138t-heat-model/predict_e144.py, heat_q138t.py, model-q138t.json and
  docs/reports/data/2026-10-31-e78-kinds-energy-matrix/e78.json the frozen chain closed through E97's idle law, fed E78's switching
                                                               watts on the planned launch pattern: the planned rises, as Q138(t)
                                                               planned E144 (a3_schedule, closed_loop and describe, unchanged)
  docs/reports/data/2026-11-04-q142m-m10/section7-m10.json     the per-card-kind gamma and the common gamma (truths for the power)
  tools/claims-v3/m10/pool8/design_power_groups.py             lg_test (the registered P8-LG test) and f_ppf (exact F points)
  tools/claims-v3/kinds/blind8/predictions-pool8-aifoundry2.json  the frozen zeros burst board at 800 MHz (aifoundry2's planning)
  tools/claims-v3/kinds/blind8/sets-blind8.json                pool 8's set sizes (N1, I1), for section 6's precision

What it prints (and writes as JSON to argv[2] when given):
  1. the noise of one hold's chain miss within a session, by P8-LG's rule (design_power_groups.noise_from_reruns' rule, line for
     line: a two-term fit where a session holds at least 4 holds spanning more than 2 C of P, residuals scaled by sqrt(n/(n-2)); else
     the session's mean, residuals scaled by sqrt(n/(n-1)); a session of one hold adds nothing), per card kind;
  2. the planned aifoundry3 session from the frozen chain at rooms 49.5, 51.2, 52.0 and 53.0 C: each hold's planned rise P over its
     anchor, the carried-in tail, the in-launch peak, the card-minutes; and aifoundry2's planned rises from committed numbers;
  3. HM-LG's power: verdict shares (GAIN / LEVEL / BOTH / NOT SEPARATED / NOT SCORED) per design, truth and noise;
  4. the section-7 clause S7-W's rates (a held-out session reads worse with a carried term by more than its own noise);
  5. the E144-like hold's two readings (HM-E144, HM-HE) and their rates;
  6. the precision a pool-8 card-1 session gives terms (c) and (d), scaled from M10's committed paired intervals (approximate).

    python3 -E -B tools/claims-v3/m11/design_power_heat.py . tools/claims-v3/m11/design-power-heat.json > tools/claims-v3/m11/design-power-heat.txt

Python 3.9 with numpy 1.26 (numpy only through Q138(t)'s frozen chain; on the Intel numpy is in the user site, so -E, not -I).
SPDX-License-Identifier: Apache-2.0
"""
import hashlib
import json
import math
import os
import random
import sys

R = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else ".")
OUT_JSON = sys.argv[2] if len(sys.argv) > 2 else None
sys.dont_write_bytecode = True
Q138T = os.path.join(R, "docs", "reports", "data", "2026-11-02-q138t-heat-model")
M10D = os.path.join(R, "docs", "reports", "data", "2026-11-04-q142m-m10")
POOL8 = os.path.join(R, "tools", "claims-v3", "m10", "pool8")
HERE = os.path.join(R, "tools", "claims-v3", "m11")
sys.path.insert(0, POOL8)
sys.path.insert(0, Q138T)
import design_power_groups as DPG  # noqa: E402  (the registered P8-LG test, unchanged)
import predict_e144 as PE  # noqa: E402        (Q138(t)'s frozen planning code, unchanged)

HM = PE.hm
VERDICTS = DPG.VERDICTS                      # GAIN, LEVEL, BOTH, NOT SEPARATED, NOT SCORED
DRAWS = 5000
MIN_HOLDS, MIN_SPAN_C, MIN_DF = 4, 6.0, 3    # REGISTRATION.md section 3: a session counts with >= 4 scored holds spanning >= 6 C of P
OUT = {"_note": "Q142(h), M11's heat registration: design only (no fit, no hold, no card); printed by design_power_heat.py"}
P = print

INPUTS = [
    "docs/reports/data/2026-11-04-q142m-m10/heldout-m10.json",
    "docs/reports/data/2026-11-04-q142m-m10/section7-m10.json",
    "docs/reports/data/2026-11-02-q138t-heat-model/cv-q138t.json",
    "docs/reports/data/2026-11-02-q138t-heat-model/predict_e144.py",
    "docs/reports/data/2026-11-02-q138t-heat-model/heat_q138t.py",
    "docs/reports/data/2026-11-02-q138t-heat-model/model-q138t.json",
    "docs/reports/data/2026-10-31-e78-kinds-energy-matrix/e78.json",
    "tools/claims-v3/m10/pool8/design_power_groups.py",
    "tools/claims-v3/kinds/blind8/predictions-pool8-aifoundry2.json",
    "tools/claims-v3/kinds/blind8/sets-blind8.json",
]


def sha(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def check_inputs():
    listed = {}
    sums = os.path.join(HERE, "SHA256SUMS")
    if os.path.exists(sums):
        for line in open(sums):
            parts = line.split()
            if len(parts) == 2:
                listed[parts[1]] = parts[0]
    rows, bad = [], []
    for rel in INPUTS:
        s = sha(os.path.join(R, rel))
        st = "not listed"
        if rel in listed:
            st = "OK" if listed[rel] == s else "DIFFERS"
            if st == "DIFFERS":
                bad.append(rel)
        rows.append((rel, s, st))
    return rows, bad


# ---------------------------------------------------------------------------------------------- 1. the noise, by P8-LG's rule
def lg_rule_noise(sets):
    """design_power_groups.noise_from_reruns' rule, line for line, on {session: [(P, e), ...]}"""
    pooled, per = [], {}
    for name, pts in sorted(sets.items()):
        xs = [float(p[0]) for p in pts]
        ys = [float(p[1]) for p in pts]
        n = len(pts)
        if n >= 4 and max(xs) - min(xs) > 2.0:
            mx, my = sum(xs) / n, sum(ys) / n
            sxx = sum((x - mx) ** 2 for x in xs)
            b = sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / sxx if sxx > 0 else 0.0
            a = my - b * mx
            res = [(y - a - b * x) * math.sqrt(n / (n - 2)) for x, y in zip(xs, ys)]
            per[name] = {"n": n, "fit": "two-term", "a_C": round(a, 4), "g": round(b, 5), "span_P_C": round(max(xs) - min(xs), 3)}
        elif n >= 2:
            my = sum(ys) / n
            res = [(y - my) * math.sqrt(n / (n - 1)) for y in ys]
            per[name] = {"n": n, "fit": "mean", "mean_C": round(my, 4)}
        else:
            res = []
            per[name] = {"n": n, "fit": "one hold: adds nothing"}
        per[name]["scaled_residuals_C"] = [round(r, 4) for r in res]
        pooled += res
    sig = math.sqrt(sum(r * r for r in pooled) / len(pooled)) if pooled else float("nan")
    return sig, len(pooled), per


def noise():
    h = json.load(open(os.path.join(M10D, "heldout-m10.json")))["heat_d_chain_gain"]["holds"]
    a3, a2_frozen = {}, {}
    for x in h:
        if not x.get("fitted") or x.get("P_C") is None:
            continue
        (a3 if x["card_kind"] == "aifoundry3" else a2_frozen).setdefault(x["session"], []).append((x["P_C"], x["e_C"], x["hold"]))
    s3, n3, per3 = lg_rule_noise({k: [(p, e) for p, e, _ in v] for k, v in a3.items()})
    cv = json.load(open(os.path.join(Q138T, "cv-q138t.json")))["a2"]
    a2 = {}
    for arm in ("fit E111, predict E133", "fit E133, predict E111"):
        for r in cv[arm]["rows"]:
            if r["hold"].startswith("HOLD-00-int8"):
                ses = r["session"].split("-")[0]
                a2.setdefault(ses, []).append((r["rise_meas_C"] - r["plateau_err_C"], r["plateau_err_C"], r["session"], r["dur_s"]))
    s2, n2, per2 = lg_rule_noise({k: [(p, e) for p, e, _, _ in v] for k, v in a2.items()})
    s2_floor = math.sqrt(s3 * s3 + 1.0 / 12.0)
    return {"a3": {"sigma_C": s3, "n_residuals": n3, "per_session": per3,
                   "holds": {k: [{"hold": hd, "P_C": round(p, 3), "e_C": round(e, 4)} for p, e, hd in v] for k, v in a3.items()}},
            "a2": {"sigma_C": s2, "n_residuals": n2, "per_session": per2,
                   "holds": {k: [{"hold": s, "dur_s": round(d, 1), "P_C": round(p, 3), "e_C": round(e, 4)} for p, e, s, d in v]
                             for k, v in a2.items()},
                   "frozen_chain_single_holds": {k: [{"hold": hd, "P_C": round(p, 3), "e_C": round(e, 4)} for p, e, hd in v]
                                                 for k, v in a2_frozen.items()},
                   "readout_floor_sigma_C": s2_floor}}


# ---------------------------------------------------------------------------------------------- 2. the planned holds
A3_R0_MIN = 5.0
A3_RESTS_MIN = [6.0, 2.0, 6.0, 2.0, 2.5]        # after H_E, Z, L1, S, L2: six minutes after each large hold, so the small holds
SMOKE_MIN_A3 = 1.4                               # start on small tails; E154's and E166's smoke with its five stop tests


def a3_holds(room):
    """REGISTRATION.md section 4: H_E is E144's H_H (A1.1's recorded patterns and E144's warm-room rule), then Z, L1, S, L2"""
    duty = {"cycle_s": 7.56, "compute_s": 3.456} if room <= 51.5 else {"cycle_s": 7.98, "compute_s": 2.965}
    return [{"name": "H_E", "item": "fp32.randn", "duty": duty, "minutes": 10.0},
            {"name": "Z", "item": "fp32.zeros", "minutes": 10.0},
            {"name": "L1", "item": "int8.full", "minutes": 10.0},
            {"name": "S", "item": "int8.neg_ones", "minutes": 10.0},
            {"name": "L2", "item": "int8.full", "minutes": 10.0}]


def a3_schedule_rests(holds, r0_min, rests_min):
    """predict_e144.a3_schedule's code, line for line, with one rest length per gap (its own takes one 'between' length): E97's
    natural chain (PE.LAUNCH_S on, PE.GAP_S off) or a duty cycle, E78's S (PE.S78), the 0.2 s grid (PE.q)"""
    pcs, marks, t = [], [], 0.0
    pcs.append((r0_min * 60.0, 0.0))
    t += PE.q(r0_min * 60.0)
    for i, h in enumerate(holds):
        S = PE.S78[h["item"]]["mean"]
        dur = h["minutes"] * 60.0
        t0 = t
        if "duty" in h:
            cyc, on = h["duty"]["cycle_s"], h["duty"]["compute_s"]
            n = int(dur // cyc)
            for _ in range(n):
                pcs += [(on, S), (cyc - on, 0.0)]
            t += n * (PE.q(on) + PE.q(cyc - on))
        else:
            n = int(dur // (PE.LAUNCH_S + PE.GAP_S))
            for _ in range(n):
                pcs += [(PE.LAUNCH_S, S), (PE.GAP_S, 0.0)]
            t += n * (PE.q(PE.LAUNCH_S) + PE.q(PE.GAP_S))
        marks.append({"name": h["name"], "item": h["item"], "t0": t0, "t1": t, "S_E78_W": S,
                      "share": (h["duty"]["compute_s"] / h["duty"]["cycle_s"]) if "duty" in h else PE.LAUNCH_S / (PE.LAUNCH_S + PE.GAP_S)})
        pcs.append((rests_min[i] * 60.0, 0.0))
        t += PE.q(rests_min[i] * 60.0)
    return pcs, marks, t


def plan_a3(room):
    pcs, marks, total = a3_schedule_rests(a3_holds(room), A3_R0_MIN, A3_RESTS_MIN)
    g, T, Pr = HM.closed_loop(pcs, PE.TAU, PE.R3, room, HM.law_a3)
    rows = []
    for mk in marks:
        d = PE.describe(g, T, Pr, mk, room)
        rows.append({k: d[k] for k in ("hold", "item", "share", "S_E78_W", "S_eff_W", "carried_in_C", "plateau_rise_C",
                                       "plateau_C_abs", "peak_C_abs", "plateau_board_rise_W")})
    return {"room_C": room, "plan_minutes": round(total / 60.0, 2), "card_minutes": round(total / 60.0 + SMOKE_MIN_A3, 2),
            "holds": rows}


def plan_a2(heldout_holds):
    """aifoundry2's planned rises from committed numbers (no 800 MHz switching table exists for the small hold's mask):
    G1E = E144b's G1 (int8.neg_ones, 800 MHz, back to back), its committed P; Z_m = int8.neg_ones on every fourth minion shire
    (run_hpl.py's `mask` 0x11111111, 8 of 32 shires), planned as a quarter of G1E's rise; Z_f = int8.zeros on every shire,
    from pool 8's frozen aifoundry2 zeros prediction, for the design without a mask"""
    g1 = [x for x in heldout_holds if x["session"] == "E144b" and x["hold"] == "G1"][0]
    p_g1e = round(g1["P_C"], 2)
    pr = json.load(open(os.path.join(R, "tools", "claims-v3", "kinds", "blind8", "predictions-pool8-aifoundry2.json")))
    z = pr["tiles"]["int8.anchor7_zeros"]["M10"]["a2_fallback"]
    # the zeros burst board at 800 MHz, referred from its 54.38 C die start to a 47 C rest by its own frozen slope, over E144b's
    # G1 rest board referred the same way (E64's 0.442 W per C): the zeros level's board rise; the aifoundry2 chain's 0.663 C per W
    # closed through 0.442 W per C gives the plateau's rise per W of that step
    rest = 47.0
    zb = z["burst_board_w"] - z["d_board_per_c_die_start"] * (54.38 - rest)
    p_ref = 21.70 + 0.442 * (rest - 45.0)        # E111's P_ref 21.70 W at a 45.0 C rest (model-q138t.json S_eff_from_holds), E64's slope
    r2 = float(PE.R2.sum())
    p_zf = r2 * (zb - p_ref) / (1.0 - r2 * 0.442)
    return {"G1E_P_C": p_g1e, "Z_m_P_C": round(p_g1e / 4.0, 2), "Z_f_P_C": round(p_zf, 2),
            "zeros_board_at_rest_W": round(zb, 2), "P_ref_W": round(p_ref, 2), "rest_C": rest,
            "sources": {"G1E": "heldout-m10.json heat_d_chain_gain E144b G1 P_C (a 13-minute hold; a 10-minute hold's plateau window reads "
                               "about 1% less by the aifoundry2 chain's share at 300-600 s)",
                        "Z_m": "a quarter of G1E: 8 of 32 shires switching (an assumption, bracketed in the power table by 6 C)",
                        "Z_f": "predictions-pool8-aifoundry2.json tiles.int8.anchor7_zeros.M10.a2_fallback burst_board_w and "
                               "d_board_per_c_die_start, referred to a 47 C rest; P_ref from E111"}}


# ---------------------------------------------------------------------------------------------- 3-5. the tests, simulated
def lg(groups):
    return DPG.lg_test(groups, min_tiles=MIN_HOLDS, min_span_w=MIN_SPAN_C, min_df=MIN_DF)


def sim_sessions(design, truths, sigma, rng):
    """design: [[P per hold of session 1], [session 2], ...]; truths: [(a, g)] per session (repeated if shorter)"""
    groups = {}
    for i, ps in enumerate(design):
        a, g = truths[i % len(truths)]
        groups[i] = [(p, a + g * p + rng.gauss(0.0, sigma)) for p in ps]
    return groups


def power_table(design, truths, sigma, seed):
    out = {}
    for lab, tr in truths:
        rng = random.Random(f"M11-HM-LG|{seed}|{sigma:.4f}|{lab}")
        cnt = {v: 0 for v in VERDICTS}
        for _ in range(DRAWS):
            cnt[lg(sim_sessions(design, tr, sigma, rng))["verdict"]] += 1
        out[lab] = {v: round(100.0 * c / DRAWS, 1) for v, c in cnt.items()}
    return out


def ls_fit(pts):
    n = len(pts)
    xs = [p[0] for p in pts]
    ys = [p[1] for p in pts]
    mx, my = sum(xs) / n, sum(ys) / n
    sxx = sum((x - mx) ** 2 for x in xs)
    b = sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / sxx
    return my - b * mx, b, mx, sxx


def rms(v):
    return math.sqrt(sum(x * x for x in v) / len(v))


def s7w_rates(design, truths, sigma, seed, carried):
    """S7-W: each session held out in turn; the carried term fitted on the other sessions of the card kind (a common gain
    gamma = sum e P / sum P^2, or a common level = mean e); the held-out session reads worse if rms(e - term) - rms(e) over its
    holds exceeds sigma / sqrt(n_s), its own noise. Returns the share of draws in which any held-out session reads worse."""
    out = {}
    for lab, tr in truths:
        rng = random.Random(f"M11-S7W|{seed}|{carried}|{sigma:.4f}|{lab}")
        hit = 0
        for _ in range(DRAWS):
            groups = sim_sessions(design, tr, sigma, rng)
            worse = False
            for k, pts in groups.items():
                other = [p for j, v in groups.items() if j != k for p in v]
                if carried == "gain":
                    gam = sum(e * p for p, e in other) / sum(p * p for p, e in other)
                    new = [e - gam * p for p, e in pts]
                else:
                    lev = sum(e for _, e in other) / len(other)
                    new = [e - lev for _, e in pts]
                if rms(new) - rms([e for _, e in pts]) > sigma / math.sqrt(len(pts)):
                    worse = True
            hit += worse
        out[lab] = round(100.0 * hit / DRAWS, 1)
    return out


def agree_rates(design, truths, sigma, seed):
    """HM-AG (REGISTRATION.md section 3): do the card kind's sessions share one gain (or one level)? F = [(RSS_common - RSS_per
    session) / (k - 1)] / [RSS_B / (n - 2k)] against F(k - 1, n - 2k) at 5%, RSS_B the per-session two-term fit's. Shares of draws
    in which the sessions DIFFER (the F test rejects), for a common gain and a common level."""
    out = {}
    k = len(design)
    n = sum(len(s) for s in design)
    crit = DPG.f_ppf(0.95, k - 1, n - 2 * k)
    for lab, tr in truths:
        rng = random.Random(f"M11-AG|{seed}|{sigma:.4f}|{lab}")
        dg = dl = 0
        for _ in range(DRAWS):
            groups = sim_sessions(design, tr, sigma, rng)
            rss_b = rss_g = rss_l = 0.0
            allp = [p for v in groups.values() for p in v]
            gc = sum(e * p for p, e in allp) / sum(p * p for p, e in allp)
            lc = sum(e for _, e in allp) / len(allp)
            rss_cg = sum((e - gc * p) ** 2 for p, e in allp)
            rss_cl = sum((e - lc) ** 2 for _, e in allp)
            for pts in groups.values():
                a0, b0, _, _ = ls_fit(pts)
                rss_b += sum((e - a0 - b0 * p) ** 2 for p, e in pts)
                g0 = sum(e * p for p, e in pts) / sum(p * p for p, e in pts)
                rss_g += sum((e - g0 * p) ** 2 for p, e in pts)
                m0 = sum(e for _, e in pts) / len(pts)
                rss_l += sum((e - m0) ** 2 for _, e in pts)
            s2 = rss_b / (n - 2 * k)
            dg += ((rss_cg - rss_g) / (k - 1)) / s2 > crit
            dl += ((rss_cl - rss_l) / (k - 1)) / s2 > crit
        out[lab] = {"gains differ": round(100.0 * dg / DRAWS, 1), "levels differ": round(100.0 * dl / DRAWS, 1)}
    return out, crit


def he_rates(p_session, i_he, truths, sigma, seed, deltas=(0.0, 0.3, 0.5)):
    """HM-E144: |e(H_E)| / R(H_E) <= 0.015 (RK3-c's line). HM-HE: e(H_E) outside the 95% prediction interval of the two-term fit
    on the session's other holds (t at n - 3 df). Shares of draws, per truth and an added hold-specific miss delta on H_E."""
    tq = {1: 12.706, 2: 4.303, 3: 3.182, 4: 2.776, 5: 2.571}
    others = [p for j, p in enumerate(p_session) if j != i_he]
    pe_ = p_session[i_he]
    df = len(others) - 2
    out = {}
    for lab, tr in truths:
        a, g = tr[0]
        for dl in deltas:
            rng = random.Random(f"M11-HE|{seed}|{sigma:.4f}|{lab}|{dl}")
            inside = dep = 0
            for _ in range(DRAWS):
                eo = [(p, a + g * p + rng.gauss(0.0, sigma)) for p in others]
                ee = a + g * pe_ + dl + rng.gauss(0.0, sigma)
                inside += abs(ee) / (pe_ + ee) <= 0.015
                a0, b0, mx, sxx = ls_fit(eo)
                res = [e - a0 - b0 * p for p, e in eo]
                s = math.sqrt(sum(r * r for r in res) / df)
                se = s * math.sqrt(1.0 + 1.0 / len(eo) + (pe_ - mx) ** 2 / sxx)
                dep += abs(ee - (a0 + b0 * pe_)) > tq[df] * se
            out[f"{lab}|delta {dl:+.1f} C"] = {"HM-E144 inside 1.5%": round(100.0 * inside / DRAWS, 1),
                                               "HM-HE departs": round(100.0 * dep / DRAWS, 1)}
    return out


def main():
    rows, bad = check_inputs()
    P("M11's heat registration (Q142(h)): the power of HM-LG and its readings, design only (no fit, no hold, no card)")
    P("\nInputs (sha256; 'OK' = as tools/claims-v3/m11/SHA256SUMS lists it):")
    for rel, s, st in rows:
        P(f"   {s}  {rel}  [{st}]")
    OUT["inputs"] = [{"path": rel, "sha256": s, "check": st} for rel, s, st in rows]
    if bad:
        P("   STOP: an input differs from the registration's list: " + ", ".join(bad))
        sys.exit(3)

    nz = noise()
    OUT["noise"] = nz
    s3, s2, s2f = nz["a3"]["sigma_C"], nz["a2"]["sigma_C"], nz["a2"]["readout_floor_sigma_C"]
    P("\n1. The noise of one hold's chain miss within a session (P8-LG's rule: a two-term fit for a session of >= 4 holds spanning "
      "> 2 C of P, else the session's mean; residuals scaled to their degrees of freedom)")
    P(f"   aifoundry3 (E144, E154, E166; M10's fitted holds, K_OL_long left out as M10 left it): sigma {s3:.4f} C over "
      f"{nz['a3']['n_residuals']} scaled residuals")
    for k, v in nz["a3"]["per_session"].items():
        P(f"     {k}: {json.dumps({x: y for x, y in v.items() if x != 'scaled_residuals_C'})}")
    P(f"   aifoundry2 (E111's and E133's two int8 holds each, each day read by the chain fitted on the other day; cv-q138t.json a2): "
      f"sigma {s2:.4f} C over {nz['a2']['n_residuals']} scaled residuals")
    for k, v in nz["a2"]["holds"].items():
        P(f"     {k}: " + "; ".join(f"{x['hold']} {x['dur_s']:.0f} s, P {x['P_C']:.2f}, e {x['e_C']:+.3f}" for x in v))
    P(f"   aifoundry2's frozen-chain sessions hold one 800 MHz hold each (they add nothing to a within-session noise): "
      + "; ".join(f"{k} {v[0]['hold']} P {v[0]['P_C']:.2f} e {v[0]['e_C']:+.3f}" for k, v in nz["a2"]["frozen_chain_single_holds"].items()))
    P(f"   aifoundry2's readout floor (aifoundry3's sigma with a whole-degree anchor's uniform +-0.5 C added): {s2f:.4f} C")

    P("\n2. The planned holds")
    plans = {str(r): plan_a3(r) for r in (49.5, 51.2, 52.0, 53.0)}
    OUT["plan_a3"] = plans
    for r, pl in plans.items():
        P(f"   aifoundry3 at a {r} C room: plan {pl['plan_minutes']:.1f} min + smoke {SMOKE_MIN_A3} = {pl['card_minutes']:.1f} card-minutes")
        for hd in pl["holds"]:
            P(f"     {hd['hold']:3s} {hd['item']:14s} share {hd['share']:.4f}  S_eff {hd['S_eff_W']:6.3f} W  carried-in {hd['carried_in_C']:+.2f} C"
              f"  P (plateau rise over its anchor) {hd['plateau_rise_C']:6.3f} C  plateau {hd['plateau_C_abs']:.2f} C  peak {hd['peak_C_abs']:.2f} C")
    hold_list = json.load(open(os.path.join(M10D, "heldout-m10.json")))["heat_d_chain_gain"]["holds"]
    a2p = plan_a2(hold_list)
    OUT["plan_a2"] = a2p
    P(f"   aifoundry2: G1E (E144b's G1 again) P {a2p['G1E_P_C']:.2f} C; Z_m (int8.neg_ones on 8 of 32 shires) P {a2p['Z_m_P_C']:.2f} C; "
      f"Z_f (int8.zeros, every shire) P {a2p['Z_f_P_C']:.2f} C (zeros board {a2p['zeros_board_at_rest_W']:.2f} W at a "
      f"{a2p['rest_C']:.0f} C rest against P_ref {a2p['P_ref_W']:.2f} W)")

    p3 = [h["plateau_rise_C"] for h in plans["51.2"]["holds"]]
    p3w = [h["plateau_rise_C"] for h in plans["52.0"]["holds"]]
    g, zm, zf = a2p["G1E_P_C"], a2p["Z_m_P_C"], a2p["Z_f_P_C"]
    designs = {
        "A3 x2 (the plan: two aifoundry3 sessions, rooms 51.2 and 52.0 C)": [p3, p3w],
        "A3 x1 (one aifoundry3 session, room 51.2 C)": [p3],
        "A3 x3 (three aifoundry3 sessions)": [p3, p3w, p3],
        "A2 x2 masked (two aifoundry2 sessions: Z_m, G1E, Z_m, G1E)": [[zm, g, zm, g]] * 2,
        "A2 x2 masked, small hold at 6 C": [[6.0, g, 6.0, g]] * 2,
        "A2 x4 masked (four aifoundry2 sessions)": [[zm, g, zm, g]] * 4,
        "A2 x2 unmasked (Z_f, G1E, Z_f, G1E)": [[zf, g, zf, g]] * 2,
    }
    s7 = json.load(open(os.path.join(M10D, "section7-m10.json")))["section7"]["d"]
    g3 = s7["clause_1_gamma_sign_differs_between_card_kinds"]["per_card_kind_gamma_all_holds"]["aifoundry3"]
    g2 = s7["clause_1_gamma_sign_differs_between_card_kinds"]["per_card_kind_gamma_all_holds"]["aifoundry2"]
    gc = s7["variants"]["common"]["gamma_all_holds"]["all"]
    truths = [("none", [(0.0, 0.0)]),
              (f"gain {100 * g3:.2f}% (M10's aifoundry3 gamma)", [(0.0, g3)]),
              (f"gain {100 * gc:.2f}% (the x1.032 arm)", [(0.0, gc)]),
              (f"gain {100 * g2:.2f}% (M10's aifoundry2 gamma)", [(0.0, g2)]),
              ("level 0.15 C", [(0.15, 0.0)]),
              ("level 0.27 C (E154's and E166's level alone)", [(0.27, 0.0)]),
              ("level 0.40 C (E166's two-term a)", [(0.395, 0.0)]),
              ("both: E154's two-term fit (-0.229 C + 5.72%)", [(-0.229, 0.0572)]),
              ("both: E166's two-term fit (+0.395 C - 1.43%)", [(0.395, -0.0143)]),
              ("mixed: E154's fit, then E166's", [(-0.229, 0.0572), (0.395, -0.0143)])]
    OUT["truths"] = {lab: tr for lab, tr in truths}
    OUT["test"] = {"form": "design_power_groups.lg_test, groups = sessions, x = P (C), y = e (C)", "alpha": 0.05,
                   "min_holds_per_session": MIN_HOLDS, "min_span_P_C": MIN_SPAN_C, "min_df": MIN_DF, "draws": DRAWS}
    P(f"\n3. HM-LG's power: the registered test (lg_test with >= {MIN_HOLDS} holds a session spanning >= {MIN_SPAN_C} C of P, "
      f"n - 2k >= {MIN_DF}), {DRAWS} draws a cell. Shares in %: " + " / ".join(VERDICTS))
    pts = {(1, 3): None, (2, 6): None, (3, 9): None, (2, 4): None, (4, 8): None}
    P("   F points (5%): " + "; ".join(f"F({a},{b}) {DPG.f_ppf(0.95, a, b):.3f}" for a, b in pts))
    OUT["power"] = {}
    for dname, des in designs.items():
        sig_list = (s3, 1.5 * s3) if dname.startswith("A3") else (s2, s2f, 1.5 * s2)
        OUT["power"][dname] = {"P_C": des, "by_sigma": {}}
        P(f"\n   {dname}: P per session " + " | ".join(", ".join(f"{p:.2f}" for p in s) for s in des))
        for sg in sig_list:
            tab = power_table(des, [(lab, tr) for lab, tr in truths], sg, dname)
            OUT["power"][dname]["by_sigma"][f"{sg:.4f}"] = tab
            P(f"     sigma {sg:.4f} C:")
            for lab, v in tab.items():
                P(f"       {lab:48s} " + " / ".join(f"{v[x]:5.1f}" for x in VERDICTS))

    P("\n4. S7-W, a held-out session reads worse with the carried term by more than its own noise (sigma / sqrt(n_s)); share of draws in "
      "which any held-out session does, at the plan (A3 x2)")
    OUT["s7w"] = {}
    for carried in ("gain", "level"):
        for sg in (s3, 1.5 * s3):
            r = s7w_rates(designs["A3 x2 (the plan: two aifoundry3 sessions, rooms 51.2 and 52.0 C)"], [(lab, tr) for lab, tr in truths], sg, "A3x2", carried)
            OUT["s7w"][f"{carried}|{sg:.4f}"] = r
            P(f"   carried: a common {carried}, sigma {sg:.4f} C: " + "; ".join(f"{lab.split(' (')[0]} {v:.1f}" for lab, v in r.items()))
    P("\n4b. HM-AG, do the plan's two aifoundry3 sessions share one gain (one level)? Share of draws in which the F test says they differ")
    OUT["agree"] = {}
    for sg in (s3, 1.5 * s3):
        ag, crit = agree_rates(designs["A3 x2 (the plan: two aifoundry3 sessions, rooms 51.2 and 52.0 C)"], [(lab, tr) for lab, tr in truths], sg, "A3x2")
        OUT["agree"][f"{sg:.4f}"] = {"F_point": crit, "rates": ag}
        P(f"   sigma {sg:.4f} C (F point {crit:.3f}): " + "; ".join(f"{lab.split(' (')[0]} {v['gains differ']:.1f} / {v['levels differ']:.1f}"
                                                         for lab, v in ag.items()))

    P("\n5. The E144-like hold H_E in one aifoundry3 session (room 51.2 C): HM-E144 = |e/R| <= 1.5% (RK3-c's line); HM-HE = e(H_E) outside "
      "the 95% prediction interval of the two-term fit on the session's other four holds. Shares in %, with a hold-specific miss delta "
      "added to H_E")
    he = he_rates(p3, 0, [(lab, tr) for lab, tr in truths if lab.split(" ")[0] in ("none", "gain", "level")], s3, "A3x1")
    OUT["he"] = he
    for k, v in he.items():
        P(f"   {k:62s} HM-E144 inside {v['HM-E144 inside 1.5%']:5.1f}   HM-HE departs {v['HM-HE departs']:5.1f}")

    P("\n6. The precision a pool-8 card-1 session gives terms (c) and (d) (approximate: M10's committed paired intervals, their "
      "half-width scaled by sqrt(n_M10 / n_pool8) for the same per-kind spread)")
    h = json.load(open(os.path.join(M10D, "heldout-m10.json")))
    c1 = h["heat_c1"]["per_card"]["aifoundry1-c1"]
    i8 = h["power"]["int8"]["paired_bootstrap"]["B+a"]["per_card"]["c1"]
    sets = json.load(open(os.path.join(R, "tools", "claims-v3", "kinds", "blind8", "sets-blind8.json")))
    n1 = sets["sizes"].get("N1") if isinstance(sets.get("sizes"), dict) else None
    i1 = sets["sizes"].get("I1") if isinstance(sets.get("sizes"), dict) else None
    hw_c = 0.5 * (c1["hi95"] - c1["lo95"])
    hw_i = 0.5 * (i8["hi95"] - i8["lo95"])
    prec = {"c": {"M10_card1_d_rms_C": c1["d_rms_w"], "M10_interval": [c1["lo95"], c1["hi95"]], "M10_n_kinds": c1["n_kinds"],
                  "pool8_N1": n1, "half_width_at_N1_C": round(hw_c * math.sqrt(c1["n_kinds"] / n1), 4) if n1 else None},
            "d": {"M10_card1_int8_B+a_d_rms_W": i8["d_rms_w"], "M10_interval": [i8["lo95"], i8["hi95"]], "M10_n_kinds": i8["n_kinds"],
                  "pool8_I1": i1, "half_width_at_I1_W": round(hw_i * math.sqrt(i8["n_kinds"] / i1), 4) if i1 else None}}
    OUT["precision_c_d"] = prec
    P(f"   (c) card 1's session heat scale: M10's held-out d {c1['d_rms_w']:+.4f} C [{c1['lo95']:+.4f}, {c1['hi95']:+.4f}] over "
      f"{c1['n_kinds']} kinds; at pool 8's N1 of {n1} tiles the half-width is about {prec['c']['half_width_at_N1_C']} C")
    P(f"   (d) card 1's int8 (M10's term a on int8, card 1): d {i8['d_rms_w']:+.4f} W [{i8['lo95']:+.4f}, {i8['hi95']:+.4f}] over "
      f"{i8['n_kinds']} kinds; at pool 8's I1 of {i1} tiles the half-width is about {prec['d']['half_width_at_I1_W']} W")
    if OUT_JSON:
        json.dump(OUT, open(OUT_JSON, "w"), indent=1, sort_keys=True)
        P(f"\nwrote {os.path.relpath(OUT_JSON, R)}")


if __name__ == "__main__":
    main()
