#!/usr/bin/env python3
"""E185 (M11's session 3, heat over minutes, aifoundry3 card 0 at 600 MHz pinned), the registration's design, desk only (the Intel): the
holds and their order from a seed, the plan at the rooms the start gate admits (M11's closed-loop planner, unchanged), each hold's frozen
forecast under the three arms, the peaks against E171's stops, the card-minutes, and every E185 rule's power by simulation from the
committed residues. Nothing here opens a device, a box or the network; nothing is fitted (the arms' gains are read from the arms' train
stage, committed beside this file).

  THE HOLDS   six, 10 minutes each: two fp32.randn holds in E144's H_H pattern (A6-3's room rule, unchanged), two int8.full and two
              int8.neg_ones holds on E97's natural chain (E78's four tiles, as E181 ran them). A 480 s rest after each fp32.randn and
              int8.full hold (the cool-down window [b + 120, b + 360) s, then the next hold's 120 s anchor), a 120 s rest after each
              int8.neg_ones hold. R0 is 5 minutes and the smoke E181's, so G0-A6 with A8-4 applies unchanged.
  THE ORDER   the six kinds shuffled by a Fisher-Yates walk whose draws are sha256 of "<seed>:<i>", the seed the first 16 hex digits of
              the sha256 of the 40-hex lab commit SEED_COMMIT (the lab's head when this design was written; a value it cannot choose), as
              an integer. Names by occurrence: H_E, H_E2; L1, L2; S, S2 (so M11's five-name reader finds H_E, L1, S and L2).
  THE READING M11's amendment A10 makes A9's arm (the chain over the smoke and the measured pass together) M11's registered reading
              from E185 on, so the gains, the ratios and the residue pools are the arms' two-pass ones; the one-pass constants beside.
  THE FORECASTS  P_F the plan's rise (the registered window); P_B = G_B P_F; P_Rl = G_Rl kappa_item P_F, kappa_item the committed ratio
              of the rail chain's rise to the board chain's rise for that item (P_Rl1 / P_F; the committed holds of the item, E181's among
              them); the cool-down window's rises the same way (kappa_cool from the committed cool-down windows of the item).
  THE POWER   every rule of E185.md section 6 on simulated sessions: R_h = P_truth,h + noise_h, the noise iid normal at M11's sigma_c
              (0.0884 C) and 1.5 sigma_c, or resampled from the truth arm's committed residues (its 11 training misses held out
              session by session, and its 5 E181 held-out misses), as they are and with their mean removed; 20,000 draws a cell.

    /usr/bin/python3 -B tools/claims-v3/e185/design_e185.py <arms train json> <arms e181 json> <out.json> [<out.txt>]
Run from the lab clone's top. Python 3.9 with numpy 1.26 (the Intel's /usr/bin/python3; numpy in the user site, so never -I).
SPDX-License-Identifier: Apache-2.0
"""
import sys

sys.dont_write_bytecode = True
import hashlib  # noqa: E402
import json  # noqa: E402
import math  # noqa: E402
import os  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
TREE = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(TREE, "tools", "claims-v3", "m11"))
import score_m11 as V1  # noqa: E402  (unchanged: it checks M11's lists on import; its V2, D, PE, HM and DPG are the committed design code)

V2, D, DPG, np = V1.V2, V1.D, V1.DPG, V1.np
PE, HM = D.PE, D.HM

SEED_COMMIT = "e0d319031847fc50e71d40244352cdb3ab167e7e"   # the lab's head when this design was written (Sat 7 Nov 2026, 19:09:23 PST)
KINDS = ["H", "H", "L", "L", "S", "S"]
ITEM = {"H": "fp32.randn", "L": "int8.full", "S": "int8.neg_ones"}
NAMES = {"H": ["H_E", "H_E2"], "L": ["L1", "L2"], "S": ["S", "S2"]}
REST_AFTER_MIN = {"H": 8.0, "L": 8.0, "S": 2.0}
R0_MIN = 5.0
HOLD_MIN = 10.0
COOL = (120.0, 360.0)
SIGMA_C = 0.0884                     # M11's sigma_c on aifoundry3 (REGISTRATION.md section 4)
ROOMS = (49.4, 50.3, 50.8, 51.5, 52.5, 53.0, 53.9)
FORECAST_ROOMS = (50.8, 52.5)        # E181's room (the cool pattern) and a warm-pattern room
DRAWS = 20000
SESSION_LINE_FW_C, SESSION_LINE_M34_C, SESSION_LINE_W = 70.0, 72.0, 65.0   # E171's stops (70 C firmware, 65 W), and E181's 72 C hold line
FW_BELOW_M34_C = 1.0                 # the firmware's whole degree reads about 1.0-1.3 C under the 34-sensor mean at H_E's peak (E181)
SMOKE_MIN = 1.4                      # the smoke with its stop tests (M11's planner's own figure, design_power_heat.SMOKE_MIN_A3)
CAP_MIN = 105.0
READING = "two_pass"                 # M11's amendment A10: A9's arm is M11's registered reading from E185 on
P = print
OUT = {}


def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def r4(x):
    return None if x is None or (isinstance(x, float) and not math.isfinite(x)) else round(float(x), 4)


# ------------------------------------------------------------------------------------------------ the order
def seed():
    return int(hashlib.sha256(SEED_COMMIT.encode()).hexdigest()[:16], 16)


def shuffle(items, s):
    a = list(items)
    for i in range(len(a) - 1, 0, -1):
        j = int(hashlib.sha256(f"{s}:{i}".encode()).hexdigest(), 16) % (i + 1)
        a[i], a[j] = a[j], a[i]
    return a


def named(order):
    seen = {"H": 0, "L": 0, "S": 0}
    out = []
    for k in order:
        out.append((k, NAMES[k][seen[k]]))
        seen[k] += 1
    return out


# ------------------------------------------------------------------------------------------------ the plan (M11's planner, unchanged)
def holds_at(room, seq):
    duty = {"cycle_s": 7.56, "compute_s": 3.456} if room <= 51.5 else {"cycle_s": 7.98, "compute_s": 2.965}   # design_power_heat.a3_holds
    hs = []
    for k, nm in seq:
        h = {"name": nm, "item": ITEM[k], "minutes": HOLD_MIN, "kind": k}
        if k == "H":
            h["duty"] = dict(duty)
        hs.append(h)
    return hs


def plan(room, seq, rests_min=None, r0_min=R0_MIN):
    hs = holds_at(room, seq)
    rests = rests_min or [REST_AFTER_MIN[h["kind"]] for h in hs]
    dt = V2.grid_dt(room)
    pcs, marks, total = V2.a3_schedule_on(hs, r0_min, rests, dt)
    g, T, Pr = HM.closed_loop(pcs, PE.TAU, PE.R3, room, HM.law_a3, dt=dt)
    rows = []
    for i, mk in enumerate(marks):
        base = float(np.mean(T[(g >= mk["t0"] - HM.ANCHOR_S) & (g < mk["t0"])]))
        mb = (g >= mk["b"] - 300.0) & (g < mk["b"])
        inh = (g >= mk["t0"]) & (g < mk["t1"])
        row = {"hold": mk["name"], "item": mk["item"], "kind": hs[i]["kind"], "start_min": round(mk["t0"] / 60.0, 3),
               "P_F_C": float(np.mean(T[mb])) - base, "carried_in_C": base - room, "plateau_C_abs": float(np.mean(T[mb])),
               "peak_m34_C_abs": float(np.max(T[inh])), "plateau_board_rise_W": float(np.mean(Pr[mb])), "rest_after_s": rests[i] * 60.0}
        c0, c1 = mk["b"] + COOL[0], mk["b"] + COOL[1]
        nxt = marks[i + 1]["t0"] if i + 1 < len(marks) else total
        if c1 <= nxt + 1e-6:
            row["cool_P_F_C"] = float(np.mean(T[(g >= c0) & (g < c1)])) - base
        rows.append(row)
    return {"room_C": room, "dt_s": dt, "plan_min": total / 60.0, "card_min": total / 60.0 + SMOKE_MIN, "holds": rows}


def check_planner():
    """this file's plan(), on REGISTRATION.md section 5's design at 51.2 C, against design_power_heat_v2.plan_exact(51.2)'s P and peak"""
    seq = [("H", "H_E"), ("Z", "Z"), ("L", "L1"), ("S", "S"), ("L", "L2")]
    ITEM["Z"] = "fp32.zeros"
    try:
        mine = plan(51.2, seq, rests_min=D.A3_RESTS_MIN, r0_min=D.A3_R0_MIN)
    finally:
        del ITEM["Z"]
    ref = V2.plan_exact(51.2)
    bad = []
    for a, b in zip(mine["holds"], ref["holds"]):
        if abs(round(a["P_F_C"], 3) - b["P_C"]) > 0.0005 or abs(round(a["peak_m34_C_abs"], 2) - b["peak_C_abs"]) > 0.005:
            bad.append(f"{a['hold']}: P {a['P_F_C']:.3f} vs {b['P_C']}, peak {a['peak_m34_C_abs']:.2f} vs {b['peak_C_abs']}")
    return {"holds": len(ref["holds"]), "problems": bad, "same": not bad}


# ------------------------------------------------------------------------------------------------ the arms' constants
def reading(tr, e1, which):
    """the arms' stage outputs on one reading: "two_pass" (M11's reading from E185 on, by A10) or "one_pass" (the registered reading of
    E181 and before, reported beside)"""
    if which == "two_pass":
        t, e = tr["two_pass"], e1["two_pass"]
        return {"gains": t["gains"], "train_holds": t["holds"], "train_loso": t["loso"]["misses"], "e181_holds": e["holds"],
                "e181_held_out": e["held_out"]["misses"]}
    return {"gains": tr["gains"], "train_holds": tr["holds"], "train_loso": tr["loso"]["misses"], "e181_holds": e1["holds"],
            "e181_held_out": e1["held_out"]["misses"]}


def arms_constants(rd):
    G = {"G_B": rd["gains"]["G_B"], "G_Rl": rd["gains"]["G_Rl"]}
    k_rows, kc_rows = {}, {}
    for src, rows in (("train", rd["train_holds"]), ("E181", rd["e181_holds"])):
        for sid, hs in rows.items():
            for nm, h in hs.items():
                it = h["item"]
                if it not in ITEM.values() or not h.get("P_F_C"):
                    continue
                k_rows.setdefault(it, []).append({"session": sid, "hold": nm, "kappa": h["P_Rl1_C"] / h["P_F_C"]})
                if h.get("cool_window_s") and h.get("cool_P_F_C"):
                    kc_rows.setdefault(it, []).append({"session": sid, "hold": nm, "kappa_cool": h["cool_P_Rl1_C"] / h["cool_P_F_C"]})
    kappa = {it: sum(x["kappa"] for x in v) / len(v) for it, v in k_rows.items()}
    kappa_cool = {it: sum(x["kappa_cool"] for x in v) / len(v) for it, v in kc_rows.items()}
    for it in ITEM.values():
        kappa_cool.setdefault(it, kappa.get(it))
    return G, kappa, kappa_cool, k_rows, kc_rows


def residue_pools(rd):
    pools = {"F": [], "B": [], "Rl": []}
    for sid, hs in rd["train_loso"].items():
        for nm, d in hs.items():
            pools["F"].append(d["e_F_C"])
            pools["B"].append(d["e_B_C"])
            pools["Rl"].append(d["e_Rl_C"])
    for sid, hs in rd["e181_held_out"].items():
        for nm, d in hs.items():
            pools["F"].append(d["e_F_C"])
            pools["B"].append(d["e_B_C"])
            pools["Rl"].append(d["e_Rl_C"])
    return pools


# ------------------------------------------------------------------------------------------------ the rules (E185.md section 6)
def rms(v):
    return math.sqrt(sum(x * x for x in v) / len(v))


def rule_pair(ex, ey, tau):
    d = rms(ex) - rms(ey)
    return ("BETTER" if d <= -tau else "WORSE" if d >= tau else "NOT RESOLVED"), d


def rule_best(es, tau):
    r = {k: rms(v) for k, v in es.items()}
    best = min(r, key=r.get)
    ties = sorted(k for k in r if k != best and r[k] - r[best] < tau)
    return (best if not ties else "NOT SEPARATED (" + ", ".join(sorted([best] + ties)) + ")"), r


def rule_cool(d_list):
    """E185-C on one arm: the mean of d_h = (the cool-down window's miss) - (the plateau's miss) over the big holds with a cool window"""
    n = len(d_list)
    if n < 3:
        return "NOT SCORED", None, None
    m = sum(d_list) / n
    sd = math.sqrt(sum((x - m) ** 2 for x in d_list) / (n - 1))
    half = V2.t95(n - 1) * sd / math.sqrt(n)
    lo, hi = m - half, m + half
    if (hi < 0 or lo > 0) and abs(m) >= 0.05:
        return ("THE SHAPE MISSES (cooler than the chain)" if m < 0 else "THE SHAPE MISSES (warmer than the chain)"), m, (lo, hi)
    if lo >= -0.10 and hi <= 0.10:
        return "THE SHAPE HOLDS", m, (lo, hi)
    return "NOT RESOLVED", m, (lo, hi)


def simulate(fc, pools, G, rng):
    """fc: the frozen forecasts at the forecast room (holds with P_F, P_B, P_Rl). Returns each rule's verdict shares per truth and noise."""
    names = [h["hold"] for h in fc]
    PF = np.array([h["P_F_C"] for h in fc])
    PB = np.array([h["P_B_C"] for h in fc])
    PR = np.array([h["P_Rl_C"] for h in fc])
    n = len(names)
    tau = SIGMA_C / math.sqrt(n)
    truths = {"F": PF, "B": PB, "Rl": PR}
    pools_c = {k: [x - sum(v) / len(v) for x in v] for k, v in pools.items()}   # the same shapes with each arm's mean miss removed
    out = {"tau_C": tau, "n_holds": n, "cells": {}}
    for tname, Pt in truths.items():
        for noise in ("normal_sigma_c", "normal_1.5_sigma_c", "committed_residues", "committed_residues_centred"):
            cnt = {"RF": {}, "BF": {}, "RB": {}, "BEST": {}}
            for _ in range(DRAWS):
                if noise.startswith("committed_residues"):
                    pool = pools[tname] if noise == "committed_residues" else pools_c[tname]
                    eps = np.array([pool[i] for i in rng.integers(0, len(pool), n)])
                else:
                    s = SIGMA_C * (1.5 if noise.startswith("normal_1.5") else 1.0)
                    eps = rng.normal(0.0, s, n)
                R = Pt + eps
                eF, eB, eR = list(R - PF), list(R - PB), list(R - PR)
                for key, (a, b) in (("RF", (eR, eF)), ("BF", (eB, eF)), ("RB", (eR, eB))):
                    v, _ = rule_pair(a, b, tau)
                    cnt[key][v] = cnt[key].get(v, 0) + 1
                bv, _ = rule_best({"F": eF, "B": eB, "Rl": eR}, tau)
                cnt["BEST"][bv] = cnt["BEST"].get(bv, 0) + 1
            out["cells"][f"truth {tname} | {noise}"] = {k: {kk: round(100.0 * vv / DRAWS, 1) for kk, vv in sorted(v.items())}
                                                        for k, v in cnt.items()}
    return out


def simulate_cool(n_big, rng):
    """E185-C's shares: d_h iid normal(mu, s) over the big holds"""
    out = {}
    for s_lab, s in (("sigma_c", SIGMA_C), ("sigma_c/2", SIGMA_C / 2)):
        for mu in (0.0, -0.05, -0.10, +0.10):
            cnt = {}
            for _ in range(DRAWS):
                v, _, _ = rule_cool(list(rng.normal(mu, s, n_big)))
                cnt[v] = cnt.get(v, 0) + 1
            out[f"mu {mu:+.2f} C | {s_lab}"] = {k: round(100.0 * c / DRAWS, 1) for k, c in sorted(cnt.items())}
    return out


def simulate_lg(fc, e181_pts, pools, rng, G):
    """M11's HM-LG at k = 2 (REGISTRATION.md section 3, lg_test unchanged): E181's registered (P, e) fixed, E185's simulated on the
    frozen chain's reading (e_F = R - P_F) under each truth, noise iid normal at sigma_c"""
    PF = np.array([h["P_F_C"] for h in fc])
    truths = {"none (the chain right)": PF, f"a gain of {100.0 * (G['G_B'] - 1.0):.2f}% (arm B's)": np.array([h["P_B_C"] for h in fc]),
              "the rail chain (arm Rl)": np.array([h["P_Rl_C"] for h in fc]), "a level of +0.27 C": PF + 0.27}
    out = {}
    for lab, Pt in truths.items():
        cnt = {}
        for _ in range(5000):
            R = Pt + rng.normal(0.0, SIGMA_C, len(PF))
            groups = {"E181": e181_pts, "E185": [(float(p), float(r - p)) for p, r in zip(PF, R)]}
            v = DPG.lg_test(groups, min_tiles=D.MIN_HOLDS, min_span_w=D.MIN_SPAN_C, min_df=D.MIN_DF)["verdict"]
            cnt[v] = cnt.get(v, 0) + 1
        out[lab] = {k: round(100.0 * c / 5000, 1) for k, c in sorted(cnt.items())}
    return out


# ------------------------------------------------------------------------------------------------ main
def main():
    a = sys.argv[1:]
    if len(a) not in (3, 4):
        print(__doc__)
        return 2
    tr_p, e1_p, out_p = a[0], a[1], a[2]
    tr, e1 = json.load(open(tr_p)), json.load(open(e1_p))
    OUT["inputs"] = {os.path.relpath(os.path.abspath(p), TREE): sha(p) for p in (tr_p, e1_p)}
    if e1.get("train_json_sha256") != sha(tr_p):
        raise SystemExit("REFUSED: the E181 stage was not read with this train json")
    OUT["check_planner"] = chk = check_planner()
    P(f"planner check (section 5's design at 51.2 C against plan_exact): {'SAME' if chk['same'] else 'DIFFERS'} {chk['problems']}")
    s = seed()
    order = shuffle(KINDS, s)
    seq = named(order)
    OUT["order"] = {"seed_commit": SEED_COMMIT, "seed": s, "seed_hex": hex(s), "kinds_in": KINDS, "order": order,
                    "holds": [nm for _, nm in seq]}
    P(f"seed {hex(s)} from {SEED_COMMIT}: order {' '.join(nm for _, nm in seq)}")
    rd = reading(tr, e1, READING)
    G, kappa, kappa_cool, k_rows, kc_rows = arms_constants(rd)
    OUT["arms"] = {"reading": READING, "gains": G, "kappa": kappa, "kappa_cool": kappa_cool, "kappa_rows": k_rows, "kappa_cool_rows": kc_rows,
                   "label": "kappa: the committed ratio P_Rl1 / P_F per item (E181's holds among them, post hoc for E181); a planning constant"}
    G1, kappa1, kappa_cool1, _, _ = arms_constants(reading(tr, e1, "one_pass"))
    OUT["arms_one_pass_beside"] = {"gains": G1, "kappa": kappa1, "kappa_cool": kappa_cool1,
                                   "label": "the registered one-pass reading's constants, reported beside (never E185's)"}
    P(f"reading {READING}: gains G_B {G['G_B']:.5f}, G_Rl {G['G_Rl']:.5f}; kappa " + ", ".join(f"{k} {v:.4f}" for k, v in kappa.items())
      + f"  (one-pass beside: G_B {G1['G_B']:.5f}, G_Rl {G1['G_Rl']:.5f})")
    plans = {}
    for room in ROOMS:
        pl = plan(room, seq)
        for h in pl["holds"]:
            h["P_B_C"] = G["G_B"] * h["P_F_C"]
            h["P_Rl_C"] = G["G_Rl"] * kappa[h["item"]] * h["P_F_C"]
            if "cool_P_F_C" in h:
                h["cool_P_B_C"] = G["G_B"] * h["cool_P_F_C"]
                h["cool_P_Rl_C"] = G["G_Rl"] * kappa_cool[h["item"]] * h["cool_P_F_C"]
        mx = max(h["peak_m34_C_abs"] for h in pl["holds"])
        pl["max_peak_m34_C"] = mx
        pl["max_peak_fw_est_C"] = mx - FW_BELOW_M34_C
        pl["margin_to_72_m34_C"] = SESSION_LINE_M34_C - mx
        pl["margin_to_70_fw_est_C"] = SESSION_LINE_FW_C - (mx - FW_BELOW_M34_C)
        plans[f"{room:.1f}"] = {k: (r4(v) if isinstance(v, float) else v) for k, v in pl.items() if k != "holds"}
        plans[f"{room:.1f}"]["holds"] = [{k: (r4(v) if isinstance(v, float) else v) for k, v in h.items()} for h in pl["holds"]]
    OUT["plans"] = plans
    for room in ROOMS:
        pl = plans[f"{room:.1f}"]
        P(f"room {room:.1f} C: plan {pl['plan_min']:.2f} min, card {pl['card_min']:.2f} min; peak 34-mean {pl['max_peak_m34_C']:.2f} C "
          f"(firmware about {pl['max_peak_fw_est_C']:.1f}; margins {pl['margin_to_72_m34_C']:.2f} to 72 C mean, {pl['margin_to_70_fw_est_C']:.2f} to 70 C firmware)")
    for room in FORECAST_ROOMS:
        pl = plans[f"{room:.1f}"]
        P(f"FORECASTS at {room:.1f} C (C): hold, P_F, P_B, P_Rl; cool P_F/P_B/P_Rl; peak")
        for h in pl["holds"]:
            cool = "" if h.get("cool_P_F_C") is None else f"  cool {h['cool_P_F_C']:.3f}/{h['cool_P_B_C']:.3f}/{h['cool_P_Rl_C']:.3f}"
            P(f"  {h['hold']:5s} {h['item']:14s} {h['P_F_C']:7.3f} {h['P_B_C']:7.3f} {h['P_Rl_C']:7.3f}{cool}  peak {h['peak_m34_C_abs']:.2f}")
    OUT["differences_at_forecast_room"] = [{"hold": h["hold"], "item": h["item"], "P_B_less_P_F_C": r4(h["P_B_C"] - h["P_F_C"]),
                                            "P_Rl_less_P_F_C": r4(h["P_Rl_C"] - h["P_F_C"]), "P_Rl_less_P_B_C": r4(h["P_Rl_C"] - h["P_B_C"])}
                                           for h in plans[f"{FORECAST_ROOMS[0]:.1f}"]["holds"]]
    P("what separates them at %.1f C (C): " % FORECAST_ROOMS[0] + "; ".join(
        f"{d['hold']} B-F {d['P_B_less_P_F_C']:+.3f}, Rl-F {d['P_Rl_less_P_F_C']:+.3f}, Rl-B {d['P_Rl_less_P_B_C']:+.3f}"
        for d in OUT["differences_at_forecast_room"]))
    rng = np.random.default_rng(185)
    fc = plans[f"{FORECAST_ROOMS[0]:.1f}"]["holds"]
    pools = residue_pools(rd)
    OUT["residue_pools"] = {k: {"n": len(v), "mean_C": r4(sum(v) / len(v)), "rms_C": r4(rms(v))} for k, v in pools.items()}
    P("residue pools: " + json.dumps(OUT["residue_pools"]))
    OUT["power"] = simulate(fc, pools, G, rng)
    for cell, v in OUT["power"]["cells"].items():
        P(f"  {cell}: RF {v['RF']}  BF {v['BF']}  RB {v['RB']}  BEST {v['BEST']}")
    n_big = sum(1 for h in fc if h.get("cool_P_F_C") is not None)
    OUT["power_cool"] = {"n_big_with_window": n_big, "cells": simulate_cool(n_big, rng)}
    for cell, v in OUT["power_cool"]["cells"].items():
        P(f"  E185-C {cell}: {v}")
    e181_pts = [(h["P_F_C"], h["e_F_C"]) for h in rd["e181_held_out"]["E181"].values()]
    OUT["power_hm_lg_k2"] = simulate_lg(fc, e181_pts, pools, rng, G)
    for lab, v in OUT["power_hm_lg_k2"].items():
        P(f"  HM-LG at k = 2 (E181 + E185), {lab}: {v}")
    json.dump(OUT, open(out_p, "w"), indent=1, sort_keys=True)
    return 0 if chk["same"] else 1


if __name__ == "__main__":
    sys.exit(main())
