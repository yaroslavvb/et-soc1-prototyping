#!/usr/bin/env python3
"""DV2's reducer (DESIGN §6, §9 T6; PREREG-DEV §1.3-§1.4, §3). Works on partial data; everything it writes from
development data is labelled "development".

  reduce_dv2.py --dev --data build/claims-v3/aifoundry2/dv2 [--out dv2-dev.json]
      Z1 (the watch timeline and its line predictions (a)-(d)), the smoke, C1m (L600 per block, 99% CIs, L_P), the NAT
      sessions (per-run observables, G1-T/G1-H counts, G2-C/D/U and G3-L/I host bands, ADD's P_U, G4's per-block L and
      L_P, L_pred and its band from §1.4, n_val), the DEV-n decisions (dev-log.jsonl), the global-state tables, every
      DEVIATION recorded. The output is development data: it tests nothing.
  reduce_dv2.py --self-test
      synthetic runs with planted effects: H-mean vs H-max timing, L = 0.24 / 0.48 / 0 against a band, a 0.40 s loop
      against one step per pass, the C1m ratio; checks the rules of PREREG-DEV §1.
"""
import glob
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from dv2lib import load_json, load_jsonl, sample_fields, median, DEFAULTS  # noqa: E402
import dv2obs  # noqa: E402

# t quantiles (0.995) for the 99% CI, df 1..30 (standard tables); beyond, the normal 2.576
T995 = {1: 63.657, 2: 9.925, 3: 5.841, 4: 4.604, 5: 4.032, 6: 3.707, 7: 3.499, 8: 3.355, 9: 3.250, 10: 3.169,
        11: 3.106, 12: 3.055, 13: 3.012, 14: 2.977, 15: 2.947, 16: 2.921, 17: 2.898, 18: 2.878, 19: 2.861, 20: 2.845,
        21: 2.831, 22: 2.819, 23: 2.807, 24: 2.797, 25: 2.787, 26: 2.779, 27: 2.771, 28: 2.763, 29: 2.756, 30: 2.750}


def t995(df):
    return T995.get(df, 2.576) if df >= 1 else None


def mean(v):
    v = [x for x in v if x is not None]
    return sum(v) / len(v) if v else None


def sd(v):
    v = [x for x in v if x is not None]
    if len(v) < 2:
        return None
    m = mean(v)
    return math.sqrt(sum((x - m) ** 2 for x in v) / (len(v) - 1))


def ci99(v):
    v = [x for x in v if x is not None]
    if len(v) < 2:
        return None
    m, s = mean(v), sd(v)
    h = t995(len(v) - 1) * s / math.sqrt(len(v))
    return [m - h, m + h]


# ----------------------------------------------------------------------------------------------- G4 (PREREG-DEV §1.4)
def l_pred(L600_per, L600_uni, P_U, P_x):
    """L_pred = ln((kU PU + Px) / (kU PU + kP Px)), kP = e^-L600(PER/INT), kU = e^-L600(UNI/INT)."""
    kP, kU = math.exp(-L600_per), math.exp(-L600_uni)
    return math.log((kU * P_U + P_x) / (kU * P_U + kP * P_x))


def g4_band(L600, Lp):
    return min(0.15, (L600 - Lp) / 2.0, Lp / 2.0)


def g4_rule(ci, Lp, b):
    """PASS if the 99% CI lies wholly inside [Lp - b, Lp + b]; FAIL if wholly outside on either side; else
    INSUFFICIENT. With b < 0.05: a sign test (PASS if the CI lies wholly above 0, FAIL if wholly within +-0.05)."""
    if ci is None:
        return "INSUFFICIENT"
    lo, hi = ci
    if b < 0.05:
        if lo > 0:
            return "PASS"
        if -0.05 <= lo and hi <= 0.05:
            return "FAIL"
        return "INSUFFICIENT"
    if Lp - b <= lo and hi <= Lp + b:
        return "PASS"
    if hi < Lp - b or lo > Lp + b:
        return "FAIL"
    return "INSUFFICIENT"


def n_val(sd_dev, b):
    if sd_dev is None or b is None or b <= 0:
        return None
    for n in range(8, 17):
        if t995(n - 1) * sd_dev / math.sqrt(n) <= b:
            return n
    return 16


# ----------------------------------------------------------------------------------------------- G1-T (§1.4)
def g1t(runs):
    sep = [r for r in runs if r.get("separating")]
    fm = [r for r in sep if r.get("fits_mean")]
    fx = [r for r in sep if r.get("fits_max")]
    blocks = {r.get("block") for r in sep}
    n = len(sep)
    if n >= 1 and len(fx) >= 0.5 * n:
        v = "FAIL"
    elif n >= 6 and len(blocks) >= 3 and len(fm) >= 0.8 * n and len(fx) <= 1:
        v = "PASS"
    else:
        v = "INSUFFICIENT"
    return {"separating": n, "blocks": len(blocks), "fit_mean": len(fm), "fit_max": len(fx), "rule_outcome_if_registered": v}


# ----------------------------------------------------------------------------------------------- host bands (§1.3)
def clock_changes(F):
    """[(t, from, to)] of the clock in a sample list."""
    out, prev = [], None
    for x in F:
        if x[5] is None:
            continue
        if prev is not None and x[5] != prev:
            out.append((x[0], prev, x[5]))
        prev = x[5]
    return out


def host_bands(tels):
    """G2-C climbs, G2-D descents, G2-U up-step readings from the runs' telemetry (development counts)."""
    climbs = {"n": 0, "le1": 0, "none": 0}
    desc = {"n": 0, "in_band": 0, "dwells_s": []}
    ups = {"n": 0, "le_thr1": 0, "le_thr": 0, "ge_thr2": 0}
    thr = DEFAULTS["thr"]
    for F in tels:
        ch = clock_changes(F)
        seq = [(x[0], x[5], x[1]) for x in F if x[5] is not None]
        for i, (t, a, b) in enumerate(ch):
            if a == 600 and b in (700, 800):
                # a climb: how many samples at 700 before 800
                j = next((k for k, s in enumerate(seq) if s[0] == t), None)
                n700 = 0
                if j is not None:
                    for s in seq[j:]:
                        if s[1] == 700:
                            n700 += 1
                        elif s[1] == 800:
                            climbs["n"] += 1
                            climbs["le1"] += n700 <= 1
                            climbs["none"] += n700 == 0
                            break
                        else:
                            break
            if a == 800 and b == 700 and i + 1 < len(ch) and ch[i + 1][1] == 700 and ch[i + 1][2] == 600:
                dw = (ch[i + 1][0] - t) / 1000.0
                desc["n"] += 1
                desc["dwells_s"].append(round(dw, 2))
                desc["in_band"] += 0.3 <= dw <= 0.7
            if b > a:
                prev = [s for s in seq if s[0] < t]
                if prev:
                    r = prev[-1][2]
                    ups["n"] += 1
                    ups["le_thr1"] += r <= thr + 1
                    ups["le_thr"] += r <= thr
                    ups["ge_thr2"] += r >= thr + 2
    return {"G2-C": climbs, "G2-D": {k: v for k, v in desc.items() if k != "dwells_s"} | {"dwell_median_s": median(desc["dwells_s"])},
            "G2-U": ups, "label": "development (host 10 Hz; bands of PREREG-DEV §1.3 apply to replication)"}


# ----------------------------------------------------------------------------------------------- Z1
def z1_lines(z1s):
    """Z1's line predictions (a) EXIT prints X <= thr, ENTER prints X = thr + 1 over the lines seen (dedup by ts)."""
    seen, a_ok, a_bad = set(), 0, []
    for z in z1s:
        for e in z.get("sp_governor", []):
            key = (e.get("kind"), e.get("ts"))
            if key in seen or e.get("ts") is None:
                continue
            seen.add(key)
            if e["kind"] == "thermal_down":
                ok = e.get("T") == (e.get("threshold") or 65) + 1
            elif e["kind"] == "thermal_idle":
                ok = e.get("T") is not None and e["T"] <= (e.get("threshold") or 65)
            else:
                continue
            if ok:
                a_ok += 1
            else:
                a_bad.append(e)
    return {"a_lines_ok": a_ok, "a_violations": a_bad[:10], "note": "(b)-(d) need the kernel intervals; reported in the pages pass"}


def residency_deltas(z1s):
    out = []
    prev = None
    for z in z1s:
        r = {k: (v or {}).get("cumulative_us") for k, v in (z.get("residency") or {}).items()}
        if prev is not None:
            out.append({"pass": z.get("pass"), "d_thermal_down_us": (r.get("4") or 0) - (prev.get("4") or 0),
                        "d_power_up_us": (r.get("2") or 0) - (prev.get("2") or 0)})
        prev = r
    return out


# ----------------------------------------------------------------------------------------------- the reduction
def reduce_dev(data):
    out = {"label": "DV2 development data (PREREG-DEV): nothing here tests a prediction", "data": data}
    z1s = []
    for f in sorted(glob.glob(os.path.join(data, "p1[0-9][0-9][0-9]", "z1.json"))):
        z = load_json(f)
        if z:
            z1s.append(z)
    out["Z1"] = {"cycles": len(z1s),
                 "timeline": [{"pass": z["pass"], "t_ms": z.get("t_ms"), "reading_c": z.get("reading_c"),
                               "threshold_c": z.get("threshold_c"), "cool": z.get("cool"), "mhz": z.get("mhz")} for z in z1s],
                 "cool_cycles": sum(1 for z in z1s if z.get("cool")),
                 "threshold_not_65": [z["pass"] for z in z1s if z.get("threshold_c") not in (65, None)],
                 "lines": z1_lines(z1s), "residency_deltas": residency_deltas(z1s)}
    sessions = []
    tels = []
    c1m = {"runs": []}
    nat_runs = []
    adds = []
    for sdir in sorted(glob.glob(os.path.join(data, "p[4-6][0-9][0-9][0-9]"))):
        s = load_json(os.path.join(sdir, "session.json"))
        if not s:
            continue
        s["dir"] = os.path.basename(sdir)
        s["global_state"] = load_jsonl(os.path.join(sdir, "global-state.jsonl"))
        sessions.append(s)
        for r in load_jsonl(os.path.join(sdir, "runs.jsonl")):
            idx = r.get("idx")
            tel = load_jsonl(os.path.join(sdir, "tel-%s.jsonl" % idx))
            F = sorted((sample_fields(x) for x in tel if x.get("t_ms") is not None), key=lambda x: x[0])
            if F:
                tels.append(F)
            o = r.get("obs") or {}
            if r.get("kind") == "C1M":
                c1m["runs"].append({"session": s["dir"], "idx": idx, "name": r["name"], "block": r.get("block"),
                                    "t_c_s": o.get("t_c_s"), "censored": o.get("censored_c"), "W_load": o.get("W_load"),
                                    "W_idle": o.get("W_idle"), "void": o.get("void") or ([] if r.get("edge_ok") else ["no edge"])})
            elif r.get("kind") in ("T", "RST"):
                nat_runs.append(dict(r, session=s["dir"], **{k: o.get(k) for k in ("separating", "fits_mean", "fits_max", "t_up", "t_down", "W_800", "W_idle", "g1h_max_over_thr")}))
            elif r.get("kind") == "ADD":
                adds.append({"session": s["dir"], "idx": idx, "P_U": o.get("P_up_W"), "W_800": o.get("W_800")})
    out["sessions"] = sessions
    # C1m: L600 per block
    blocks = {}
    for r in c1m["runs"]:
        if r["void"] or r["t_c_s"] is None:
            continue
        blocks.setdefault((r["session"], r["block"]), {})[r["name"]] = r
    Lp, Lu, LPp = [], [], []
    for k, b in sorted(blocks.items()):
        i, p, u = b.get("INT16@32"), b.get("PER16@32"), b.get("UNI32@16")
        if i and p:
            Lp.append(math.log(p["t_c_s"] / i["t_c_s"]))
            if i.get("W_load") and p.get("W_load") and i.get("W_idle") is not None and p.get("W_idle") is not None:
                wi, wp = i["W_load"] - i["W_idle"], p["W_load"] - p["W_idle"]
                if wi > 0 and wp > 0:
                    LPp.append(Lp[-1] + math.log(wp / wi))
        if i and u:
            Lu.append(math.log(u["t_c_s"] / i["t_c_s"]))
    c1m.update({"complete_blocks": len(blocks), "L600_PER_INT": mean(Lp), "L600_PER_INT_ci99": ci99(Lp), "n_PER": len(Lp),
                "L600_UNI_INT": mean(Lu), "L600_UNI_INT_ci99": ci99(Lu), "n_UNI": len(Lu), "L600_P_PER_INT": mean(LPp),
                "transfer_check": "reported against aifoundry3's 0.48 [0.41, 0.55] (not registered)"})
    out["C1m"] = c1m
    # NAT: G1, G4, ADD
    T = [r for r in nat_runs if r.get("kind") == "T"]
    out["G1"] = {"G1-T": g1t(T), "G1-H_max_over_thr": max((r["g1h_max_over_thr"] for r in T if r.get("g1h_max_over_thr") is not None), default=None),
                 "label": "development counts"}
    PU = mean([a["P_U"] for a in adds])
    out["ADD"] = {"runs": adds, "P_U_mean_W": PU}
    g4 = {}
    for r in T:
        nm = r.get("name", "")
        if nm.startswith("INT16@") or nm.startswith("PER16@"):
            g4.setdefault((r["session"], r["block"]), {})[nm[:5]] = r
    Ls, LPs, Px = [], [], []
    for k, b in sorted(g4.items()):
        i, p = b.get("INT16"), b.get("PER16")
        if not (i and p):
            continue
        ti, tp = i.get("trip_s"), p.get("trip_s")
        if ti is None and tp is None:
            continue                                  # both censored: the block is dropped
        ti = ti if ti is not None else (i.get("launch_s") or 7)
        tp = tp if tp is not None else (p.get("launch_s") or 7)
        L = math.log(tp / ti)
        Ls.append(L)
        if PU is not None and i.get("W_800") and p.get("W_800") and adds:
            add800 = mean([a["W_800"] for a in adds if a.get("W_800")])
            xi, xp = i["W_800"] - add800, p["W_800"] - add800
            if xi > 0 and xp > 0:
                LPs.append(L + math.log(xp / xi))
                Px += [xi, xp]
    g = {"blocks": len(Ls), "L_dev": mean(Ls), "L_dev_ci99": ci99(Ls), "L_P_dev": mean(LPs), "SD_dev": sd(Ls)}
    if c1m["L600_PER_INT"] is not None and c1m["L600_UNI_INT"] is not None and PU and Px:
        lp = l_pred(c1m["L600_PER_INT"], c1m["L600_UNI_INT"], PU, mean(Px))
        b = g4_band(c1m["L600_PER_INT"], lp)
        g.update({"L_pred": lp, "band": b, "n_val": n_val(g["SD_dev"], b), "inputs": "C1m (this card)"})
    elif PU and Px and len(Ls) >= 1:
        lp = l_pred(0.48, 0.34, PU, mean(Px))
        b = g4_band(0.48, lp)
        g.update({"L_pred": lp, "band": b, "n_val": n_val(g["SD_dev"], b), "inputs": "couplings from aifoundry3 (DEV-6 fallback)"})
    out["G4"] = g
    out["host_bands"] = host_bands(tels)
    out["dev_log"] = load_jsonl(os.path.join(data, "dev-log.jsonl"))
    out["alerts"] = [load_json(f) for f in glob.glob(os.path.join(data, "ALERT-*.json"))]
    readiness = {"T_blocks_ge4": g["blocks"] >= 4, "C1m_ge3_blocks": c1m["complete_blocks"] >= 3, "ADD_ge2": len(adds) >= 2,
                 "T1_verified_on_a_clock_change_ring": False, "T6_retrospective_reproduced": False}
    out["readiness_for_freeze"] = readiness
    return out


# ----------------------------------------------------------------------------------------------- self-test
def _synth_tel(path, t0, K, t_up, t_hi, t_m, t_down, mean0=62, loop_s=0.4, end_s=12.0):
    """10 Hz samples: the high reaches K at t_hi, the mean at t_m; the clock 600 -> 800 at t_up, 800 -> 700 at t_down,
    700 -> 600 after loop_s."""
    with open(path, "w") as f:
        t = t0 - 3000
        while t <= t0 + end_s * 1000:
            mhz = 600
            if t_up is not None and t >= t_up:
                mhz = 800
            if t_down is not None and t >= t_down:
                mhz = 700 if t < t_down + loop_s * 1000 else 600
            m = mean0 if t < t0 else min(K + 1, mean0 + (K - mean0) * (t - t0) / max(1, (t_m - t0)))
            hi = (mean0 + 2) if t < t0 else min(K + 4, (mean0 + 2) + (K - mean0 - 2) * (t - t0) / max(1, (t_hi - t0)))
            f.write(json.dumps({"t_ms": int(t), "since_reset_ms": int(t - t0 + 3000), "board_w": 40.0 if mhz == 800 else 32.0,
                                "temp_c": {"minshire": [int(m), int(m) - 3, int(hi)]}, "mhz": {"minion": mhz}}) + "\n")
            t += 100


def _synth_heater(path, t0, dur_s):
    with open(path, "w") as f:
        f.write("SPARSITY " + json.dumps({"launch": -1, "t_start_ms": t0, "t_end_ms": t0 + 30}) + "\n")
        f.write("SPARSITY " + json.dumps({"launch": 0, "t_start_ms": t0 + 30, "t_end_ms": t0 + int(dur_s * 1000)}) + "\n")


def selftest():
    import tempfile
    d = tempfile.mkdtemp()
    ok = 0
    # G1-T: planted H-mean (the step follows the mean) and H-max (the step follows the high)
    for truth in ("mean", "max"):
        runs = []
        for k in range(8):
            t0 = 1_000_000 + k * 100000
            t_up, t_hi, t_m = t0 + 700, t0 + 1500, t0 + 4500
            t_down = (t_m + 200) if truth == "mean" else (t_hi + 200)
            tp, hp = os.path.join(d, "t%d.jsonl" % k), os.path.join(d, "h%d.out" % k)
            _synth_tel(tp, t0, 66, t_up, t_hi, t_m, t_down)
            _synth_heater(hp, t0, 7.0)
            o = dv2obs.runobs(tp, hp, K=66)
            o["block"] = k // 2 + 1
            runs.append(o)
        g = g1t(runs)
        want = "PASS" if truth == "mean" else "FAIL"
        assert g["rule_outcome_if_registered"] == want, (truth, g)
    ok += 1
    # G4: planted L = 0.24 (diluted: PASS), 0.48 (undiluted: FAIL above), 0 (none: FAIL below)
    L600, Lu, PU, Px = 0.48, 0.34, 6.9, 6.3
    lp = l_pred(L600, Lu, PU, Px)
    b = g4_band(L600, lp)
    assert 0.2 < lp < 0.3, lp
    import random
    rng = random.Random(7)
    for L, want in ((lp, "PASS"), (0.48, "FAIL"), (0.0, "FAIL")):
        vals = [L + rng.gauss(0, 0.05) for _ in range(16)]
        got = g4_rule(ci99(vals), lp, b)
        assert got == want, (L, got, ci99(vals), lp, b)
    assert g4_rule(ci99([lp + x for x in (-0.3, 0.3, -0.2, 0.25)]), lp, b) == "INSUFFICIENT"
    assert n_val(0.05, b) == 8 and n_val(1.0, b) == 16
    ok += 1
    # G2-D: a 0.40 s loop gives dwells in [0.3, 0.7]; one step per pass (0.15 s) does not
    for loop_s, want in ((0.4, 1), (0.15, 0)):
        tp = os.path.join(d, "loop.jsonl")
        _synth_tel(tp, 5_000_000, 66, 5_000_700, 5_001_500, 5_004_500, 5_004_700, loop_s=loop_s)
        F = sorted((sample_fields(x) for x in load_jsonl(tp)), key=lambda x: x[0])
        hb = host_bands([F])
        assert hb["G2-D"]["n"] == 1 and hb["G2-D"]["in_band"] == want, (loop_s, hb)
    ok += 1
    # C1m: L600 from planted t_c ratios
    Lp = [math.log(5.0 * math.exp(0.48) / 5.0) for _ in range(4)]
    assert abs(mean(Lp) - 0.48) < 1e-9
    ok += 1
    print("reduce_dv2 selftest: %d groups passed (G1-T planted H-mean -> PASS, H-max -> FAIL; G4 L_pred %.3f band %.3f: "
          "diluted PASS, undiluted and none FAIL; G2-D 0.40 s loop in band, 0.15 s not)" % (ok, lp, b))
    return 0


def main(argv):
    if "--self-test" in argv:
        return selftest()
    if "--dev" in argv:
        data = argv[argv.index("--data") + 1]
        out = argv[argv.index("--out") + 1] if "--out" in argv else os.path.join(data, "dv2-dev.json")
        r = reduce_dev(data)
        json.dump(r, open(out, "w"), indent=1, default=str)
        print("wrote %s: Z1 %d cycles (%d cool), %d sessions, C1m %d runs / %d blocks, G4 %d blocks, ADD %d" % (
            out, r["Z1"]["cycles"], r["Z1"]["cool_cycles"], len(r["sessions"]), len(r["C1m"]["runs"]),
            r["C1m"]["complete_blocks"], r["G4"]["blocks"], len(r["ADD"]["runs"])))
        return 0
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
