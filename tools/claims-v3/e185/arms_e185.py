#!/usr/bin/env python3
"""E185 (M11's session 3, heat over minutes), the registration's arms, desk only (the Intel): two arms beside M11's frozen chain, each
stated before it was computed on any session (E185.md section 1), fitted on the committed aifoundry3 heat sessions before E181 only,
and read held out on E181 with the gains frozen. Nothing here opens a device, a box or the network.

  ARM F   the frozen chain, M11's registered reading (REGISTRATION.md section 1): Q138(t)'s chain as Q139(e) froze it (TAU, R3),
          open loop on the measured board above Pref (the median board W over R0's last 120 s); per hold R = the plateau's mean
          [b - 300 s, b) of the 34-sensor die less its mean over the 120 s before the anchor end, P the same on the chain, e = R - P.
  ARM B   a plain board gain on the frozen chain: the prediction G_B x pred_F, anchored the same way, so P_B = G_B P_F. One gain,
          fitted by least squares through the origin on the training holds' (P_F, R).
  ARM Rl  a rail-driven chain: the same frozen chain driven by the measured rail excess dQ = Q - Q_ref, Q = sp.minion_w[0] +
          sp.sram_w[0] + sp.noc_w[0] (the three regulators the PMIC reads, as the service processor reports them), on the session's
          0.2 s grid (linear interpolation, as heat_q138t.grid), Q_ref the median of Q over R0's last 120 s (Pref's window); the
          prediction G_Rl x states(dQ, TAU) @ R3, anchored the same way, so P_Rl = G_Rl P_Rl1. One gain, fitted as G_B is.

  TRAINING  the 11 aifoundry3 holds M10's term (d) and M11 read before E181 (heldout-m10.json > heat_d_chain_gain > holds, fitted):
            E144 H_H, H_L (read by fit_q138t.score_hold's windows, as M10 read them); E154 H_M, K_S, K_Q, K_L, K_O and E166 K_S,
            K_Q, K_L, K_O_window (read by M11's scorer v1's read_hold_a3, as its self-test reproduces M10's rows). E89 and E97 are
            not used: the chain was fitted on them.
  NESTED    the frozen gains are fitted on all three training sessions; inside the training set each session is held out in turn
            (fitted on the other two, read on the third).
  HELD OUT  E181's five holds read with the frozen gains (stage e181). Beside it, labelled post hoc, each gain fitted on E181 alone.
  COOL-DOWN reported: the miss over [b + 120, b + 360) after a hold (relative to the hold's own anchor, as e is), where that window
            lies inside the rest after the hold and before the next hold's first process.
  TWO-PASS  A9's arm (a9_posthoc.two_pass, unchanged): every arm read again over the smoke pass and the measured pass together, the
            rail interpolated over both passes the same way; the gains refitted on the two-pass training holds; E181 read with them.

    /usr/bin/python3 -B tools/claims-v3/e185/arms_e185.py train <out.json>
    /usr/bin/python3 -B tools/claims-v3/e185/arms_e185.py e181 <train.json> <out.json> [<out.txt>]
Stage `train` reads no E181 file. Stage `e181` reads the train stage's frozen gains from its json and refuses if that json's gains do not
re-derive from the training rows it holds. Run from the lab clone's top. Python 3.9 with numpy 1.26 (the Intel's /usr/bin/python3;
numpy in the user site, so never -I). SPDX-License-Identifier: Apache-2.0
"""
import sys

sys.dont_write_bytecode = True
import hashlib  # noqa: E402
import json  # noqa: E402
import math  # noqa: E402
import os  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
TREE = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
M11 = os.path.join(TREE, "tools", "claims-v3", "m11")
sys.path.insert(0, M11)
import score_m11 as V1  # noqa: E402  (unchanged: it checks M11's lists and its pinned reader on import)
import a9_posthoc as A9  # noqa: E402  (unchanged: two_pass, A9-1)

SE, FT, PQ, S166, np = V1.SE, V1.FT, V1.PQ, V1.S166, V1.np
hm = S166.hm
D = os.path.join(TREE, "docs", "reports", "data")
COOL = (120.0, 360.0)              # the cool-down window after a hold's last process end, s
COOL_PARTS = ((60.0, 120.0), (120.0, 240.0), (240.0, 360.0))
TRAIN = (
    ("E144", D + "/2026-11-02-e144-heat-minutes/aifoundry3/e144/p14420", D + "/2026-11-02-e144-heat-minutes/aifoundry3/e144-smoke/p14401",
     ("H_H", "H_L")),
    ("E154", D + "/2026-11-03-e154-heat-e2e-aifoundry3/aifoundry3/e154/p15420", D + "/2026-11-03-e154-heat-e2e-aifoundry3/aifoundry3/e154-smoke/p15401",
     ("H_M", "K_S", "K_Q", "K_L", "K_O")),
    ("E166", D + "/2026-11-04-e166-heat-replicate-aifoundry3/aifoundry3/e166/p16620",
     D + "/2026-11-04-e166-heat-replicate-aifoundry3/aifoundry3/e166-smoke/p16601", ("K_S", "K_Q", "K_L", "K_O_window")),
)
E181 = ("E181", D + "/2026-11-06-e181-m11-session2-aifoundry3/aifoundry3/e181/p18120",
        D + "/2026-11-06-e181-m11-session2-aifoundry3/aifoundry3/e181-smoke/p18101", ("H_E", "Z", "L1", "S", "L2"))
LARGE = 6.0                        # a large rise: P_F at least 6 C (E181's H_E, L1, L2)
READ = []                          # every file read, with its sha256


def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def note(p):
    rel = os.path.relpath(p, TREE)
    if rel not in [x[0] for x in READ]:
        READ.append((rel, sha(p)))


def r4(x):
    return None if x is None or (isinstance(x, float) and not math.isfinite(x)) else round(float(x), 4)


def rms(v):
    v = [x for x in v if x is not None]
    return math.sqrt(sum(x * x for x in v) / len(v)) if v else None


# ------------------------------------------------------------------------------------------------ the rail on a session's grid
def rail_rows(paths):
    """(t_s, Q_W) from telemetry files: Q = minion + SRAM + NoC as sp.*_w[0]; NaN where any of the three is missing"""
    t, q = [], []
    for p in paths:
        note(p)
        for r in hm._rows(p):
            sp = r.get("sp") or {}
            try:
                v = float(sp["minion_w"][0]) + float(sp["sram_w"][0]) + float(sp["noc_w"][0])
            except (KeyError, TypeError, IndexError, ValueError):
                v = float("nan")
            t.append(r["t_ms"] / 1000.0)
            q.append(v)
    t, q = np.array(t, float), np.array(q, float)
    o = np.argsort(t, kind="stable")
    return t[o], q[o]


def rail_on_grid(paths, g):
    t, q = rail_rows(paths)
    ok = np.isfinite(q)
    return np.interp(g, t[ok], q[ok]), int(ok.sum()), int(len(q))


def window_mean(g, y, a, b):
    return SE.wmean(g, y, a, b)


def rise(g, y, anchor_end, b):
    """the registered rise of a series: its plateau mean [b - 300, b) less its mean over the 120 s before anchor_end"""
    return window_mean(g, y, b - 300.0, b) - window_mean(g, y, anchor_end - hm.ANCHOR_S, anchor_end)


# ------------------------------------------------------------------------------------------------ one session
def load(sid, pdir, smoke, names, two_pass=False):
    """the session, the chain's predictions on board and rail, and each named hold's windows (anchor end, b, the next start)"""
    for f in ("marks.jsonl", "runs.jsonl", "telemetry.jsonl.gz"):
        if os.path.exists(os.path.join(pdir, f)):
            note(os.path.join(pdir, f))
    s1 = SE.a3_load([pdir])
    info = None
    if two_pass:
        note(os.path.join(smoke, "telemetry.jsonl.gz"))
        sess, info = A9.two_pass(pdir, smoke)
        if sess is None:
            return None, info
        tel_paths = [os.path.join(smoke, "telemetry.jsonl.gz"), os.path.join(pdir, "telemetry.jsonl.gz")]
    else:
        sess = s1
        tel_paths = [os.path.join(pdir, "telemetry.jsonl.gz")]
    g, T = sess["g"], sess["T"]
    Q, nq, nrows = rail_on_grid(tel_paths, g)
    r0 = s1["rests"][0]
    wq = (g >= r0["t1"] - hm.ANCHOR_S) & (g < r0["t1"])
    Qref = float(np.median(Q[wq]))
    pred_F = FT.predict_session(sess, PQ.TAU, PQ.R3)
    X = hm.states(Q - Qref, PQ.TAU)
    pred_R1 = X @ np.asarray(PQ.R3, float)
    # the windows, by the registered reader of each session
    wins = {}
    if sid == "E144":
        for h in s1["holds"]:
            if h["name"] in names:
                wins[h["name"]] = {"item": h.get("item"), "anchor_end": h["anchor_end"], "b": h["t1"], "t0": h["t0"], "reader": "fit_q138t.score_hold"}
    else:
        marks, recs, _ = S166.records(pdir)
        tel_t = S166.tel_times(pdir)
        pa = FT.predict_session(s1, PQ.TAU, PQ.R3)
        for nm in names:
            if nm == "K_O_window":
                hr = recs["K_OL"]
                b10 = V1.P166.window_10min({"procs": hr["procs"], "t0": hr["procs"][0][0]})
                row = V1.read_hold_a3(s1, recs, marks, tel_t, pa, "K_OL", b_override=b10)
            else:
                row = V1.read_hold_a3(s1, recs, marks, tel_t, pa, nm)
            wins[nm] = {"item": row.get("item"), "anchor_end": row["anchor_end"], "b": row["b_last_process_end"], "t0": row["t0_first_process"],
                        "reader": "score_m11.read_hold_a3", "registered_R": row.get("R_C"), "registered_e": row.get("e_C"),
                        "scored": row.get("scored")}
            if nm == "K_O_window":
                wins[nm]["inside_hold"] = "the window ends inside K_OL, which runs on: no cool-down"
    # the next hold's first process (or the pass's end) after each window
    starts = sorted([h["t0"] for h in s1["holds"]])
    for nm, w in wins.items():
        later = [x for x in starts if x > w["b"] + 1.0]
        w["next_start"] = min(later) if later else float(g[-1])
    return {"sid": sid, "g": g, "T": T, "dP": sess["dP"], "Pref": sess["Pref"], "Q": Q, "Qref": Qref, "pred_F": pred_F,
            "pred_R1": pred_R1, "wins": wins, "rail_rows": [nq, nrows], "two_pass": info}, None


def read_holds(S):
    g, T = S["g"], S["T"]
    out = {}
    for nm, w in S["wins"].items():
        a, b = w["anchor_end"], w["b"]
        R = rise(g, T, a, b)
        PF = rise(g, S["pred_F"], a, b)
        PR1 = rise(g, S["pred_R1"], a, b)
        dPp = window_mean(g, S["dP"], b - 300.0, b)
        dQp = window_mean(g, S["Q"] - S["Qref"], b - 300.0, b)
        row = {"item": w["item"], "reader": w["reader"], "R_C": R, "P_F_C": PF, "e_F_C": R - PF, "P_Rl1_C": PR1,
               "plateau_dP_W": dPp, "plateau_dQ_W": dQp, "rail_share": dQp / dPp if dPp else None,
               "registered_R_C": w.get("registered_R"), "registered_e_C": w.get("registered_e")}
        # the cool-down after the hold, where the whole window lies inside the rest after it
        c0, c1 = b + COOL[0], b + COOL[1]
        if w.get("inside_hold"):
            row["cool_window_s"] = None
            row["cool_why"] = w["inside_hold"]
        elif c1 <= w["next_start"] + 1e-6:
            base_T = window_mean(g, T, a - hm.ANCHOR_S, a)
            row["cool_window_s"] = [COOL[0], COOL[1]]
            row["cool_R_C"] = window_mean(g, T, c0, c1) - base_T
            row["cool_P_F_C"] = window_mean(g, S["pred_F"], c0, c1) - window_mean(g, S["pred_F"], a - hm.ANCHOR_S, a)
            row["cool_P_Rl1_C"] = window_mean(g, S["pred_R1"], c0, c1) - window_mean(g, S["pred_R1"], a - hm.ANCHOR_S, a)
            row["cool_parts"] = {}
            for (u, v) in COOL_PARTS:
                row["cool_parts"][f"{int(u)}-{int(v)}"] = {
                    "R_C": window_mean(g, T, b + u, b + v) - base_T,
                    "P_F_C": window_mean(g, S["pred_F"], b + u, b + v) - window_mean(g, S["pred_F"], a - hm.ANCHOR_S, a),
                    "P_Rl1_C": window_mean(g, S["pred_R1"], b + u, b + v) - window_mean(g, S["pred_R1"], a - hm.ANCHOR_S, a)}
        else:
            row["cool_window_s"] = None
            row["cool_why"] = f"the rest after it is {w['next_start'] - b:.0f} s (the window needs {COOL[1]:.0f} s)"
        out[nm] = row
    return out


# ------------------------------------------------------------------------------------------------ fits
def gain(pairs):
    """least squares through the origin: R = G P"""
    sxx = sum(p * p for p, _ in pairs)
    return sum(p * r for p, r in pairs) / sxx if sxx > 0 else None


def fit_all(rows):
    """rows: {sid: {hold: row}} -> the two gains"""
    pb = [(h["P_F_C"], h["R_C"]) for s in rows.values() for h in s.values()]
    pr = [(h["P_Rl1_C"], h["R_C"]) for s in rows.values() for h in s.values()]
    return {"G_B": gain(pb), "G_Rl": gain(pr), "n_holds": len(pb)}


def misses(rows, G):
    out = {}
    for sid, hs in rows.items():
        out[sid] = {}
        for nm, h in hs.items():
            eB = h["R_C"] - G["G_B"] * h["P_F_C"]
            eR = h["R_C"] - G["G_Rl"] * h["P_Rl1_C"]
            d = {"e_F_C": r4(h["e_F_C"]), "e_B_C": r4(eB), "e_Rl_C": r4(eR), "P_F_C": r4(h["P_F_C"]), "P_B_C": r4(G["G_B"] * h["P_F_C"]),
                 "P_Rl_C": r4(G["G_Rl"] * h["P_Rl1_C"]), "R_C": r4(h["R_C"])}
            if h.get("cool_window_s"):
                d["cool_e_F_C"] = r4(h["cool_R_C"] - h["cool_P_F_C"])
                d["cool_e_B_C"] = r4(h["cool_R_C"] - G["G_B"] * h["cool_P_F_C"])
                d["cool_e_Rl_C"] = r4(h["cool_R_C"] - G["G_Rl"] * h["cool_P_Rl1_C"])
            out[sid][nm] = d
    return out


def summary_rms(ms, large_only=False):
    vals = {"F": [], "B": [], "Rl": []}
    for sid, hs in ms.items():
        for nm, d in hs.items():
            if large_only and (d["P_F_C"] is None or d["P_F_C"] < LARGE):
                continue
            vals["F"].append(d["e_F_C"])
            vals["B"].append(d["e_B_C"])
            vals["Rl"].append(d["e_Rl_C"])
    return {k: r4(rms(v)) for k, v in vals.items()} | {"n": len(vals["F"])}


def loso(rows):
    """each training session held out in turn: the gains fitted on the other two, read on it"""
    out, per = {}, {}
    for sid in rows:
        G = fit_all({k: v for k, v in rows.items() if k != sid})
        per[sid] = {"G_B": r4(G["G_B"]), "G_Rl": r4(G["G_Rl"])}
        out.update(misses({sid: rows[sid]}, G))
    return out, per


def clean(rows):
    out = {}
    for sid, hs in rows.items():
        out[sid] = {}
        for nm, h in hs.items():
            d = {}
            for k, v in h.items():
                if isinstance(v, float):
                    d[k] = r4(v)
                elif isinstance(v, dict):
                    d[k] = {kk: ({k3: r4(v3) for k3, v3 in vv.items()} if isinstance(vv, dict) else vv) for kk, vv in v.items()}
                else:
                    d[k] = v
            out[sid][nm] = d
    return out


def read_set(specs, two_pass=False):
    rows, info = {}, {}
    for sid, pdir, smoke, names in specs:
        S, why = load(sid, pdir, smoke, names, two_pass=two_pass)
        if S is None:
            info[sid] = {"NOT SCORED": why}
            continue
        rows[sid] = read_holds(S)
        info[sid] = {"Pref_W": r4(S["Pref"]), "Qref_W": r4(S["Qref"]), "rail_rows_readable_of_all": S["rail_rows"],
                     "two_pass": None if not two_pass else {k: (r4(v) if isinstance(v, float) else v) for k, v in S["two_pass"].items()}}
    return rows, info


def checks_registered(rows):
    """the registered reader's R and e (rounded to 3 decimals there) against this file's windows: within 0.001 C"""
    bad, n = [], 0
    for sid, hs in rows.items():
        for nm, h in hs.items():
            if h.get("registered_R_C") is None:
                continue
            n += 1
            if abs(h["R_C"] - h["registered_R_C"]) > 0.0011 or abs(h["e_F_C"] - h["registered_e_C"]) > 0.0011:
                bad.append(f"{sid} {nm}: R {h['R_C']:.4f} vs {h['registered_R_C']}, e {h['e_F_C']:.4f} vs {h['registered_e_C']}")
    return n, bad


def checks_m10(rows):
    """M10's committed per-hold rows (heldout-m10.json > heat_d_chain_gain > holds): e within 0.001 C (R as M11's v1 self-test reads it)"""
    p = os.path.join(D, "2026-11-04-q142m-m10", "heldout-m10.json")
    note(p)
    hl = json.load(open(p))["heat_d_chain_gain"]["holds"]
    want = {(x["session"], x["hold"]): x for x in hl if x.get("fitted") and x["card_kind"] == "aifoundry3"}
    got, bad = {}, []
    for (sid, nm), w in sorted(want.items()):
        h = rows.get(sid, {}).get(nm)
        if h is None:
            bad.append(f"{sid} {nm}: not read")
            continue
        de, dR = abs(h["e_F_C"] - w["e_C"]), abs(h["R_C"] - w["R_C"])
        got[f"{sid}|{nm}"] = {"de_C": r4(de), "dR_C": r4(dR)}
        if de > 0.001:
            bad.append(f"{sid} {nm}: e {h['e_F_C']:.4f} vs M10's {w['e_C']:.4f}")
    return {"n": len(got), "e_within_0p001": not bad, "holds": got}, bad


# ------------------------------------------------------------------------------------------------ stages
def stage_train(out):
    res = {"stage": "train", "label": "fitted on the training sessions (E144, E154, E166); reads no E181 file", "cool_window_s": list(COOL)}
    rows, info = read_set(TRAIN)
    n_reg, bad_reg = checks_registered(rows)
    m10, bad_m10 = checks_m10(rows)
    G = fit_all(rows)
    lo, per = loso(rows)
    res.update({"sessions": info, "holds": clean(rows), "checks": {"registered_reader_holds": n_reg, "registered_reader_problems": bad_reg,
                                                                    "m10_rows": m10, "m10_problems": bad_m10},
                "gains": {"G_B": G["G_B"], "G_Rl": G["G_Rl"], "n_holds": G["n_holds"]},
                "in_sample": {"misses": misses(rows, G), "rms": summary_rms(misses(rows, G)), "rms_large": summary_rms(misses(rows, G), True)},
                "loso": {"gains_per_fold": per, "misses": lo, "rms": summary_rms(lo), "rms_large": summary_rms(lo, True)}})
    rows2, info2 = read_set(TRAIN, two_pass=True)
    G2 = fit_all(rows2)
    lo2, per2 = loso(rows2)
    res["two_pass"] = {"label": "A9's arm: every arm over the smoke and the measured pass together", "sessions": info2, "holds": clean(rows2),
                       "gains": {"G_B": G2["G_B"], "G_Rl": G2["G_Rl"], "n_holds": G2["n_holds"]},
                       "in_sample": {"rms": summary_rms(misses(rows2, G2)), "misses": misses(rows2, G2)},
                       "loso": {"gains_per_fold": per2, "rms": summary_rms(lo2), "rms_large": summary_rms(lo2, True), "misses": lo2}}
    res["files_read"] = [{"path": p, "sha256": h} for p, h in READ]
    json.dump(res, open(out, "w"), indent=1, sort_keys=True)
    print(f"train: G_B {G['G_B']:.5f}  G_Rl {G['G_Rl']:.5f}  (two-pass {G2['G_B']:.5f} / {G2['G_Rl']:.5f}); registered reader "
          f"{n_reg} holds, {len(bad_reg)} problems; M10 rows {m10['n']}, {len(bad_m10)} problems")
    for p in bad_reg + bad_m10:
        print("  PROBLEM", p)
    return 0 if not (bad_reg or bad_m10) else 1


def stage_e181(train_json, out, out_txt=None):
    tr = json.load(open(train_json))
    # the frozen gains must re-derive from the training rows the json holds (no hand edit)
    for key, rows_key in (("gains", "holds"),):
        pb = [(h["P_F_C"], h["R_C"]) for s in tr[rows_key].values() for h in s.values()]
        pr = [(h["P_Rl1_C"], h["R_C"]) for s in tr[rows_key].values() for h in s.values()]
        gb, gr = gain(pb), gain(pr)
        if abs(gb - tr[key]["G_B"]) > 2e-4 or abs(gr - tr[key]["G_Rl"]) > 2e-4:
            raise SystemExit("REFUSED: the train json's gains do not re-derive from its rows")
    G = {"G_B": tr["gains"]["G_B"], "G_Rl": tr["gains"]["G_Rl"]}
    G2 = {"G_B": tr["two_pass"]["gains"]["G_B"], "G_Rl": tr["two_pass"]["gains"]["G_Rl"]}
    res = {"stage": "e181", "label": "E181 read held out with the train stage's frozen gains; the post hoc fits beside, labelled",
           "train_json_sha256": sha(train_json), "gains_frozen": G, "gains_frozen_two_pass": G2}
    rows, info = read_set((E181,))
    n_reg, bad_reg = checks_registered(rows)
    ho = misses(rows, G)
    res.update({"session": info, "holds": clean(rows), "checks": {"registered_reader_holds": n_reg, "problems": bad_reg},
                "held_out": {"misses": ho, "rms": summary_rms(ho), "rms_large": summary_rms(ho, True)}})
    Gp = fit_all(rows)
    ph = misses(rows, Gp)
    res["post_hoc"] = {"label": "POST HOC: each gain fitted on E181's five holds alone", "gains": {"G_B": Gp["G_B"], "G_Rl": Gp["G_Rl"]},
                       "misses": ph, "rms": summary_rms(ph), "rms_large": summary_rms(ph, True)}
    rows2, info2 = read_set((E181,), two_pass=True)
    ho2 = misses(rows2, G2)
    Gp2 = fit_all(rows2)
    res["two_pass"] = {"label": "A9's arm: every arm over the smoke and the measured pass together; gains from the two-pass training",
                       "session": info2, "holds": clean(rows2), "held_out": {"misses": ho2, "rms": summary_rms(ho2), "rms_large": summary_rms(ho2, True)},
                       "post_hoc": {"gains": {"G_B": Gp2["G_B"], "G_Rl": Gp2["G_Rl"]}, "rms": summary_rms(misses(rows2, Gp2)),
                                    "rms_large": summary_rms(misses(rows2, Gp2), True)}}
    res["files_read"] = [{"path": p, "sha256": h} for p, h in READ]
    json.dump(res, open(out, "w"), indent=1, sort_keys=True)
    lines = [f"E181 held out, frozen gains G_B {G['G_B']:.4f}, G_Rl {G['G_Rl']:.4f} (registered reader: {n_reg} holds, {len(bad_reg)} problems)",
             "hold   R       P_F     e_F     P_B     e_B     P_Rl    e_Rl    share   cool e_F/e_B/e_Rl"]
    for nm, d in ho["E181"].items():
        h = rows["E181"][nm]
        cool = "" if d.get("cool_e_F_C") is None else f"{d['cool_e_F_C']:+.3f}/{d['cool_e_B_C']:+.3f}/{d['cool_e_Rl_C']:+.3f}"
        lines.append(f"{nm:5s} {d['R_C']:7.3f} {d['P_F_C']:7.3f} {d['e_F_C']:+7.3f} {d['P_B_C']:7.3f} {d['e_B_C']:+7.3f} "
                     f"{d['P_Rl_C']:7.3f} {d['e_Rl_C']:+7.3f} {h['rail_share']:7.3f}   {cool}")
    lines.append(f"rms over 5: {res['held_out']['rms']}; over the large rises: {res['held_out']['rms_large']}")
    lines.append(f"POST HOC (E181 alone): G_B {Gp['G_B']:.4f}, G_Rl {Gp['G_Rl']:.4f}; rms {res['post_hoc']['rms']}; large {res['post_hoc']['rms_large']}")
    lines.append(f"two-pass held out: rms {res['two_pass']['held_out']['rms']}; large {res['two_pass']['held_out']['rms_large']}")
    for p in bad_reg:
        lines.append("PROBLEM " + p)
    txt = "\n".join(lines)
    print(txt)
    if out_txt:
        open(out_txt, "w").write(txt + "\n")
    return 0 if not bad_reg else 1


def main():
    a = sys.argv[1:]
    if a and a[0] == "train" and len(a) == 2:
        return stage_train(a[1])
    if a and a[0] == "e181" and len(a) in (3, 4):
        return stage_e181(a[1], a[2], a[3] if len(a) == 4 else None)
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main())
