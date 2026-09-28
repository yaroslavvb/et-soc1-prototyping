#!/usr/bin/env python3
"""DV2 validation reducer (PREREG-VAL.md): the idle-governor items from read-only watch cycles on aifoundry2.

    reduce_val.py --data build/claims-v3/aifoundry2/dv2val [--out verdicts-dv2val.json]
        the verdicts of the registered items (PREREG-VAL section 3) from the VZ cycles (p9xxx)
    reduce_val.py --data build/claims-v3/aifoundry2/dv2 --dev [--out dev-idle.json]
        the same statistics on the development Z1 cycles (p1xxx): development data, labelled so; tests nothing
    reduce_val.py --self-test
        synthetic event streams with planted outcomes (H-mean vs H-max, a hidden episode, a busy-test governor)

Inputs per cycle directory: sp.bin (the SP's 4 KB trace ring, read before the cycle's sample), z2-residency.jsonl
(the raw throttle-state residencies, read before the sample), tel.jsonl (a 1 s 10 Hz sample with one statistics reset
at its start: temp_c.minshire = [mean, low, high] of the 34 minion-shire sensors, the same integer mean the governor
compares). The governor lines of every dump are merged (dedup by kind and SP timestamp). SP time maps to host time
through the DM request lines of the previous cycle's sample that survive in the next dump (MsgID 33 = the first request
of each ettelem sample, against its host t_ms).

Items (all on the idle card; a cycle or interval that holds a power_up / power_down / 'new OP' line, i.e. a kernel of
anybody, is excluded from every item):
  I1  (TH1, G1-I)  the governor's thermal state against the host mean and high: a clean OUT cycle with the high >= 66
                   separates (H-max says IN); a clean IN cycle with the mean <= 64 is an H-mean violation.
  I2  (TH3, Z1-a)  every ENTER prints 66 (thr + 1); every EXIT prints <= 65 (thr).
  I3  (TH7, G6-B)  every idle EXIT is followed, as the next governor line, by a PIDLE, within 0.30 s (SP).
  I4  (TH2, G3-Q)  every ENTER -> EXIT interval < 60 s lies within 0.015 s of k x P (P = 0.4053 s, k >= 0 integer).
  I5  (TH2)        ENTER lines on an idle card (the missing busy test): HEAD's thermal branch acts only while busy.
  I6  (TH8)        the THERMAL_DOWN residency counter: its change between two cycles equals the summed durations of the
                   episodes (ENTER -> EXIT) that ended between the two reads, less 1.33 ms per episode, within 5 ms.

NAT replication items (the frozen NAT-4 sessions, p6051-p6099; the per-run observables are dv2obs.py's, computed live
by dv2/block.sh into runs.jsonl; frozen numbers from prereg-val.json):
  G1-T (TH1) the first down-step's timing against the mean and the high (PREREG-DEV 1.1/1.4).
  G1-H (TH1) the hot hold: >= 1.0 s at 800 MHz after the high read >= 67 (thr + 2).
  G4   (TH5) per block L = ln(t800(PER16@12) / t800(INT16@12)) at S = 62, its 99% CI against L_pred +- b.
  G2-C/D/U (TH2, TH3) the host bands of PREREG-DEV 1.3; G3-L/I (TH4) launch -> 800 and kernel end -> 600.
"""
import glob
import gzip
import json
import math
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "dv2"))
import sptrace_events as SE  # noqa: E402

THR = 65
P_LOOP = 0.4053          # s per loop pass incl. its body (development: 0.8109/2, 0.8095/2, 1.2166/3)
TOL_Q = 0.015            # s
EP_OFF_MS = 1.33         # ms: ENTER line -> 'received throttle_state: 4' (the state is set after the line)
TOL_RES_MS = 5.0
QUIET_S = 30.0
GOV = ("thermal_down", "thermal_idle", "power_idle", "power_up", "power_down")
BUSY = ("power_up", "power_down")


def load_jsonl(p):
    out = []
    if not os.path.exists(p):
        return out
    op = gzip.open if p.endswith(".gz") else open
    with op(p, "rt") as f:
        for l in f:
            l = l.strip()
            if l.startswith("{"):
                try:
                    out.append(json.loads(l))
                except Exception:
                    pass
    return out


def cycles_of(data, dev):
    pat = "p1[0-9][0-9][0-9]" if dev else "p9[1-4][0-9][0-9]"
    out = []
    for d in sorted(glob.glob(os.path.join(data, pat))):
        b = {}
        try:
            b = json.load(open(os.path.join(d, "block.json")))
        except Exception:
            pass
        if b.get("status") != "ok":
            continue
        out.append(d)
    return out


def ring(path):
    try:
        return [e for e in SE.events(open(path, "rb").read()) if e.get("ts") is not None]
    except Exception:
        return []


def collect(dirs, extra_dumps=()):
    """events (merged, SP-time order), per-cycle data, offsets."""
    ev, newop = {}, {}
    rings = {}
    for d in dirs:
        rings[d] = ring(os.path.join(d, "sp.bin"))
    for f in extra_dumps:
        rings[f] = ring(f)
    for R in rings.values():
        for e in R:
            if e["kind"] in GOV or e["kind"] == "received":
                ev.setdefault((e["kind"], e["ts"]), e)
            if "new OP" in e.get("text", ""):
                newop.setdefault(e["ts"], e)
    E = sorted(ev.values(), key=lambda e: e["ts"])
    offs = []
    for i in range(1, len(dirs)):
        tel = load_jsonl(os.path.join(dirs[i - 1], "tel.jsonl"))
        R = rings[dirs[i]]
        m33 = [R[j - 1]["ts"] for j in range(1, len(R)) if "MsgID:33" in R[j]["text"] and "Received DM" in R[j - 1]["text"]]
        if tel and m33:
            k = min(len(m33), len(tel))
            o = sorted(tel[-k + j]["t_ms"] / 1e3 - m33[-k + j] / 1e6 for j in range(k))
            if (o[-1] - o[0]) * 1e3 <= 5.0:          # a dump whose DM lines are another sampler's (a session between) is no fit
                offs.append((m33[-1] / 1e6, o[len(o) // 2], (o[-1] - o[0]) * 1e3))
    if os.environ.get("DV2V_FORCE_COARSE"):       # test hook: behave as if the ring held no DM request lines
        offs = []
    if not offs and not os.environ.get("DV2V_NO_COARSE"):
        # no DM request lines (the ring at WARNING or lower, e.g. after an SP reset): the coarse fit from the uptime
        # reads (DM 30, whole minutes): each read at host time h with M minutes puts the offset in (h - 60 M - 60,
        # h - 60 M]; the intersection over all cycles is the offset window, its half-width the uncertainty
        lo, hi = -1e18, 1e18
        for d in dirs:
            for u in load_jsonl(os.path.join(d, "z2-uptime.jsonl")):
                if u.get("rc") == 0 and u.get("t_ms") and u.get("mins") is not None:
                    M = (u["day"] * 24 + u["hours"]) * 60 + u["mins"]
                    h = u["t_ms"] / 1e3
                    lo, hi = max(lo, h - 60 * M - 60), min(hi, h - 60 * M)
        if hi >= lo > -1e17:
            offs.append((0.0, (lo + hi) / 2.0, (hi - lo) / 2.0 * 1e3, "coarse"))
    return E, sorted(newop), offs


def host_of(ts_us, offs):
    """SP us -> host s, with the offset of the nearest fit (the SP clock drifts ~10 ppm)."""
    if not offs:
        return None
    s = ts_us / 1e6
    best = min(offs, key=lambda o: abs(o[0] - s))
    return s + best[1]


def session_windows(data):
    """Host-time windows [t0, t1] (s) of every heating pass of ours in the data root (p4xxx-p6xxx block.json), padded
    by 30 s: the ring at INFO under their samplers loses lines, so their intervals are excluded as busy."""
    W = []
    for f in glob.glob(os.path.join(data, "p[4-6][0-9][0-9][0-9]", "block.json")):
        try:
            b = json.load(open(f))
        except Exception:
            continue
        if b.get("status") == "skipped" or not b.get("t0_ms") or not b.get("t1_ms"):
            continue
        W.append((b["t0_ms"] / 1e3 - 30.0, b["t1_ms"] / 1e3 + 30.0))
    return sorted(W)


def analyse(dirs, extra_dumps=(), windows=()):
    E, newop, offs = collect(dirs, extra_dumps)
    busy_ts = sorted([e["ts"] for e in E if e["kind"] in BUSY] + list(newop))
    # our own heating passes, in SP time (the nearest offset fit)
    Uw = max((o[2] for o in offs), default=0.0) / 1e3 if offs else 0.0
    for a, b in windows:
        if offs:
            o = min(offs, key=lambda x: abs(x[0] + x[1] - a))[1]
            a, b = a - Uw, b + Uw
            t = a
            while t <= b:
                busy_ts.append(int((t - o) * 1e6))
                t += 2.0
    busy_ts.sort()
    U = max((o[2] for o in offs), default=0.0) / 1e3 if offs else 0.0      # the offset uncertainty, s
    quiet = QUIET_S + U
    thr = [e for e in E if e["kind"] in ("thermal_down", "thermal_idle")]
    # episodes and sequences
    eps, i3, i4, i5 = [], [], [], []
    for i, e in enumerate(E):
        nxt = [x for x in E[i + 1:] if x["kind"] in GOV]
        if e["kind"] == "thermal_idle":
            p = nxt[0] if nxt else None
            if p is not None:
                i3.append({"ts": e["ts"], "next": p["kind"], "dt_s": round((p["ts"] - e["ts"]) / 1e6, 4)})
        if e["kind"] == "thermal_down":
            x = next((x for x in nxt if x["kind"] in ("thermal_idle", "thermal_down")), None)
            if x is not None and x["kind"] == "thermal_idle":
                eps.append((e["ts"], x["ts"]))
                d = (x["ts"] - e["ts"]) / 1e6
                if d < 60:
                    k = int(round(d / P_LOOP))
                    i4.append({"ts": e["ts"], "d_s": round(d, 4), "k": k, "resid_s": round(d - k * P_LOOP, 4)})
            prev = [x for x in E[:i] if x["kind"] in GOV]
            pv = prev[-1] if prev else None
            if pv is not None and pv["kind"] in ("power_idle", "thermal_idle"):
                i5.append({"ts": e["ts"], "prev": pv["kind"], "dt_s": round((e["ts"] - pv["ts"]) / 1e6, 4)})
    def busy_between(a, b):
        return any(a <= t <= b for t in busy_ts)
    # per-cycle state and host readings (I1), the residency counter (I6)
    thr_h = [(host_of(e["ts"], offs), e["kind"], e["ts"]) for e in thr]
    cyc = []
    for zi, d in enumerate(dirs):
        tel = [t for t in load_jsonl(os.path.join(d, "tel.jsonl")) if (t.get("temp_c") or {}).get("minshire")]
        res = {r.get("state"): r for r in load_jsonl(os.path.join(d, "z2-residency.jsonl"))}
        c = {"cycle": os.path.basename(d)}
        r4 = res.get(4) or {}
        c["res4_us"], c["res4_t"] = r4.get("cumulative_us"), (r4.get("t_ms") or 0) / 1e3 or None
        if tel and offs:
            t0, t1 = tel[0]["t_ms"] / 1e3, tel[-1]["t_ms"] / 1e3
            ms = sorted(t["temp_c"]["minshire"][0] for t in tel)
            hs = [t["temp_c"]["minshire"][2] for t in tel]
            before = [x for x in thr_h if x[0] is not None and x[0] < t0]
            after = [x for x in thr_h if x[0] is not None and x[0] > t1]
            # a heating pass of ours after the last idle event leaves the state unknown (its ring lines are lost)
            if before and any(before[-1][0] < w1 and w0 < t0 for w0, w1 in windows):
                before = []
            c.update({"host": time.strftime("%H:%M:%S", time.localtime(t0)), "t0": t0, "t1": t1,
                      "m": ms[len(ms) // 2], "h_min": min(hs), "lo": min(t["temp_c"]["minshire"][1] for t in tel),
                      "state": None if not before else ("IN" if before[-1][1] == "thermal_down" else "OUT"),
                      "quiet_before_s": round(t0 - before[-1][0], 1) if before else None,
                      "quiet_after_s": round(after[0][0] - t1, 1) if after else None})
        cyc.append(c)
    i6 = []
    for a, b in zip(cyc, cyc[1:]):
        if a.get("res4_us") is None or b.get("res4_us") is None or not offs:
            continue
        lo_sp = (a["res4_t"] - offs[0][1]) * 1e6 if a.get("res4_t") else None
        hi_sp = (b["res4_t"] - offs[0][1]) * 1e6 if b.get("res4_t") else None
        if lo_sp is None or hi_sp is None:
            continue
        # the nearest offset for each end
        lo_sp = (a["res4_t"] - min(offs, key=lambda o: abs(o[0] + o[1] - a["res4_t"]))[1]) * 1e6
        hi_sp = (b["res4_t"] - min(offs, key=lambda o: abs(o[0] + o[1] - b["res4_t"]))[1]) * 1e6
        inn = [(s, e) for s, e in eps if lo_sp < e <= hi_sp]
        amb = any(abs(e - lo_sp) <= (U + 1.0) * 1e6 or abs(e - hi_sp) <= (U + 1.0) * 1e6 for s, e in eps)
        straddle = [(s, e) for s, e in eps if s <= lo_sp < e]
        dcum = (b["res4_us"] - a["res4_us"]) / 1e3
        expect = sum((e - s) for s, e in inn) / 1e3 - EP_OFF_MS * len(inn)
        i6.append({"from": a["cycle"], "to": b["cycle"], "n_ep": len(inn), "d_cum_ms": round(dcum, 2),
                   "expect_ms": round(expect, 2), "diff_ms": round(dcum - expect, 2), "straddle": len(straddle),
                   "busy": busy_between(lo_sp, hi_sp) or amb, "ambiguous": amb})
    hidden = {x["to"]: x for x in i6}
    for zi, c in enumerate(cyc):
        nxt = cyc[zi + 1]["cycle"] if zi + 1 < len(cyc) else None
        h = hidden.get(nxt) if nxt else None
        c["hidden_ms"] = h["diff_ms"] if h else None
        c["busy_near"] = bool(h and h["busy"])
        clean = (c.get("state") is not None and (c.get("quiet_before_s") or 0) >= quiet
                 and (c.get("quiet_after_s") is None or c["quiet_after_s"] >= quiet)
                 and c["hidden_ms"] is not None and abs(c["hidden_ms"]) <= TOL_RES_MS and not c["busy_near"])
        c["clean"] = clean
        c["class"] = ("not-clean" if not clean else
                      "HMAX-SEP" if c["state"] == "OUT" and c["h_min"] >= THR + 1 else
                      "HMEAN-VIOL" if c["state"] == "IN" and c["m"] <= THR - 1 else "both")
        c["strong"] = bool(clean and c["state"] == "OUT" and c["h_min"] >= THR + 2)
    return {"events": E, "thr": thr, "eps": eps, "i3": i3, "i4": i4, "i5": i5, "i6": i6, "cycles": cyc,
            "offsets": offs, "busy_ts": busy_ts, "newop": len(newop), "offset_uncertainty_s": U,
            "offset_kind": "coarse (uptime minutes)" if offs and len(offs[0]) > 3 else ("DM request lines" if offs else None)}


def verdicts(A):
    """PREREG-VAL section 3's rules. PASS / FAIL / INSUFFICIENT per item, with the counts."""
    busy = A["busy_ts"]
    def idle(ts, win_s=5.0):
        return not any(abs(t - ts) <= win_s * 1e6 for t in busy)
    out = {}
    # I1
    C = [c for c in A["cycles"] if c.get("clean")]
    sep = [c for c in C if c["class"] == "HMAX-SEP"]
    viol = [c for c in C if c["class"] == "HMEAN-VIOL"]
    stretches = set()
    for c in sep:   # an OUT stretch: the last thermal event before the cycle identifies it
        stretches.add(round(c["t0"] - c["quiet_before_s"], 0))
    disc = len(sep) + len(viol)
    if len(stretches) >= 3 and len(sep) >= 5 and len(viol) == 0:
        v = "PASS"
    elif disc and (len(viol) >= 2 and len(viol) >= 0.5 * disc):
        v = "FAIL"
    else:
        v = "INSUFFICIENT"
    out["I1"] = {"verdict": v, "clean_cycles": len(C), "hmax_sep": len(sep), "out_stretches": len(stretches),
                 "strong_h67": sum(1 for c in sep if c["strong"]), "hmean_viol": len(viol),
                 "rule": "PASS: >= 5 clean OUT cycles with high >= 66 over >= 3 OUT stretches and no clean IN cycle "
                         "with mean <= 64; FAIL: >= 2 such IN cycles and they are >= 50% of the discriminating cycles"}
    # I2
    ent = [e for e in A["thr"] if e["kind"] == "thermal_down" and idle(e["ts"])]
    ext = [e for e in A["thr"] if e["kind"] == "thermal_idle" and idle(e["ts"])]
    bad = [e for e in ent if e.get("T") != THR + 1] + [e for e in ext if e.get("T") is None or e["T"] > THR]
    out["I2"] = {"verdict": "FAIL" if bad else ("PASS" if len(ent) >= 10 and len(ext) >= 10 else "INSUFFICIENT"),
                 "enter": len(ent), "exit": len(ext), "bad": len(bad),
                 "rule": "PASS: >= 10 idle ENTERs and >= 10 idle EXITs, every ENTER prints 66, every EXIT <= 65; FAIL: any other"}
    # I3
    x3 = [x for x in A["i3"] if idle(x["ts"])]
    notp = [x for x in x3 if x["next"] != "power_idle"]
    late = [x for x in x3 if x["next"] == "power_idle" and x["dt_s"] > 0.30]
    if notp or (x3 and len(late) > 0.1 * len(x3)):
        v = "FAIL"
    elif len(x3) >= 10 and len(late) <= 0.1 * len(x3):
        v = "PASS"
    else:
        v = "INSUFFICIENT"
    out["I3"] = {"verdict": v, "exits": len(x3), "next_not_pidle": len(notp), "later_than_0.30s": len(late),
                 "rule": "PASS: >= 10 idle EXITs, each followed by a PIDLE as the next governor line, >= 90% within "
                         "0.30 s; FAIL: any other next line, or > 10% later than 0.30 s"}
    # I4
    x4 = [x for x in A["i4"] if idle(x["ts"])]
    k1 = [x for x in x4 if x["k"] >= 1]
    off = [x for x in x4 if abs(x["resid_s"]) > TOL_Q]
    if x4 and len(off) > 0.1 * len(x4):
        v = "FAIL"
    elif len(k1) >= 5 and not off:
        v = "PASS"
    else:
        v = "INSUFFICIENT"
    out["I4"] = {"verdict": v, "intervals": len(x4), "k_ge_1": len(k1), "off_grid": len(off),
                 "resid_s": sorted(x["resid_s"] for x in x4),
                 "rule": "PASS: >= 5 ENTER->EXIT intervals with k >= 1 and every interval within 0.015 s of k x 0.4053 s; "
                         "FAIL: > 10% off that grid"}
    # I5
    x5 = [x for x in A["i5"] if idle(x["ts"], 30.0)]
    warm = 0
    cyc = A["cycles"]
    for a, b in zip(cyc, cyc[1:]):
        if a.get("m") is not None and b.get("m") is not None and a["m"] <= THR - 1 and b["m"] >= THR + 1:
            warm += 1
    v = "PASS" if len(x5) >= 3 else ("FAIL" if warm >= 3 and not x5 else "INSUFFICIENT")
    out["I5"] = {"verdict": v, "idle_enters": len(x5), "warming_passes_seen": warm,
                 "rule": "PASS: >= 3 ENTERs whose previous governor line is a PIDLE or an EXIT, with no power_up, "
                         "power_down or 'new OP' line within 30 s; FAIL: none while >= 3 cycle pairs show the mean "
                         "rising from <= 64 to >= 66"}
    # I6
    x6 = [x for x in A["i6"] if not x["busy"] and x["n_ep"] >= 1]
    bad6 = [x for x in x6 if abs(x["diff_ms"]) > TOL_RES_MS]
    if x6 and len(bad6) > 0:
        v = "FAIL" if any(abs(x["diff_ms"]) > 50 for x in bad6) or len(bad6) > 0.1 * len(x6) else "INSUFFICIENT"
    else:
        v = "PASS" if len(x6) >= 3 else "INSUFFICIENT"
    out["I6"] = {"verdict": v, "intervals": len(x6), "outside_5ms": len(bad6),
                 "diffs_ms": [x["diff_ms"] for x in x6],
                 "rule": "PASS: >= 3 idle intervals with >= 1 completed episode, every one within 5 ms; FAIL: any "
                         "more than 50 ms off, or > 10% outside 5 ms"}
    return out


# ------------------------------------------------------------------------------------------------ NAT items
def t995(df):
    T = {1: 63.657, 2: 9.925, 3: 5.841, 4: 4.604, 5: 4.032, 6: 3.707, 7: 3.499, 8: 3.355, 9: 3.250, 10: 3.169,
         11: 3.106, 12: 3.055, 13: 3.012, 14: 2.977, 15: 2.947, 16: 2.921, 17: 2.898, 18: 2.878, 19: 2.861, 20: 2.845}
    return T.get(df, 2.576)


def nat_sessions(data, dev):
    pat = "p60[0-4][0-9]" if dev else "p60[5-9][0-9]"
    out = []
    for d in sorted(glob.glob(os.path.join(data, pat))):
        try:
            s = json.load(open(os.path.join(d, "session.json")))
        except Exception:
            continue
        if s.get("kind") == "NAT" and s.get("branch") == "NAT-4":
            out.append(d)
    return out


def nat_runs(dirs):
    R = []
    for d in dirs:
        for r in load_jsonl(os.path.join(d, "runs.jsonl")):
            r["_session"] = os.path.basename(d)
            R.append(r)
    return R


def run_valid(r):
    o = r.get("obs") or {}
    return (r.get("rc") == 0 and not (o.get("void")) and r.get("edge_ok") and not r.get("stop")
            and str(r.get("reset_check") or "").startswith("ONE"))


def g_items(dirs, P):
    import re
    sys.path.insert(0, os.path.join(HERE, "..", "dv2"))
    import reduce_dv2 as RD
    from dv2lib import sample_fields
    R = nat_runs(dirs)
    T = [r for r in R if r.get("kind") == "T" and run_valid(r)]
    out = {}
    # G1-T
    g = RD.g1t([dict(r, **{k: (r.get("obs") or {}).get(k) for k in ("separating", "fits_mean", "fits_max")},
                     block=(r["_session"], r.get("block"))) for r in T])
    out["G1-T"] = {"verdict": g["rule_outcome_if_registered"], **{k: v for k, v in g.items() if k != "rule_outcome_if_registered"},
                   "rule": "PASS: >= 6 separating runs over >= 3 blocks, >= 80% fit H-mean, <= 1 fits H-max; FAIL: >= 50% fit H-max"}
    # G1-H
    hold = [r for r in T if ((r.get("obs") or {}).get("g1h_max_over_thr") or 0) >= 2]
    hot = [r for r in T if (r.get("obs") or {}).get("t_hi2") is not None]
    hb = {(r["_session"], r.get("block")) for r in hold}
    if len(hold) >= 3 and len(hb) >= 2:
        v = "PASS"
    elif len(hot) >= 6 and not hold:
        v = "FAIL"
    else:
        v = "INSUFFICIENT"
    out["G1-H"] = {"verdict": v, "holds": len(hold), "blocks": len(hb), "runs_with_high_ge_67_at_800": len(hot),
                   "max_over_thr": max(((r.get("obs") or {}).get("g1h_max_over_thr") or 0 for r in T), default=None),
                   "rule": "PASS: >= 3 runs over >= 2 blocks hold 800 MHz >= 1.0 s after a sample at 800 with the high >= 67; "
                           "FAIL: >= 6 runs reach a high >= 67 at 800 MHz and none holds"}
    # G4
    blocks = {}
    for r in T:
        nm = (r.get("name") or "")
        if r.get("S") != P.get("g4_S") or nm[:5] not in ("INT16", "PER16") or not nm.endswith("@%d" % P.get("g4_per", 12)):
            continue
        blocks.setdefault((r["_session"], r.get("block")), {})[nm[:5]] = r
    Ls, LPs, cens = [], [], 0
    for k, b in sorted(blocks.items()):
        i, p = b.get("INT16"), b.get("PER16")
        if not (i and p):
            continue
        oi, op = i.get("obs") or {}, p.get("obs") or {}
        def t800(o):
            if o.get("trip_s") is not None:
                return o["trip_s"], False
            if o.get("t_up") is not None and o.get("t_end_ms") is not None:
                return (o["t_end_ms"] - o["t_up"]) / 1000.0, True
            return None, True
        ti, ci_ = t800(oi)
        tp, cp = t800(op)
        if ti is None or tp is None or (ci_ and cp) or ti <= 0 or tp <= 0:
            continue
        cens += ci_ + cp
        L = math.log(tp / ti)
        Ls.append(L)
        if oi.get("W_800") and op.get("W_800") and P.get("add_W800"):
            xi, xp = oi["W_800"] - P["add_W800"], op["W_800"] - P["add_W800"]
            if xi > 0 and xp > 0:
                LPs.append(L + math.log(xp / xi))
    n = len(Ls)
    ci = None
    if n >= 2:
        m = sum(Ls) / n
        sdv = math.sqrt(sum((x - m) ** 2 for x in Ls) / (n - 1))
        h = t995(n - 1) * sdv / math.sqrt(n)
        ci = [m - h, m + h]
    Lp, b = P.get("L_pred"), P.get("b")
    if ci is None or Lp is None or n < int(P.get("g4_min_blocks", 8)):
        v = "INSUFFICIENT"
    elif Lp - b <= ci[0] and ci[1] <= Lp + b:
        v = "PASS"
    elif ci[1] < Lp - b or ci[0] > Lp + b:
        v = "FAIL"
    else:
        v = "INSUFFICIENT"
    if ci is None or n < int(P.get("g4s_min_blocks", 6)):
        vs = "INSUFFICIENT"
    elif ci[0] > 0:
        vs = "PASS"
    elif -0.05 <= ci[0] and ci[1] <= 0.05:
        vs = "FAIL"
    else:
        vs = "INSUFFICIENT"
    out["G4-S"] = {"verdict": vs, "blocks": n, "L_mean": (sum(Ls) / n) if n else None, "ci99": ci,
                   "rule": "PASS: the 99%% CI of the block-mean L lies wholly above 0 (>= %s blocks); FAIL: wholly within +-0.05" % P.get("g4s_min_blocks", 6)}
    if not P.get("g4_registered", False):
        v = "NOT REGISTERED"
    out["G4"] = {"verdict": v, "blocks": n, "censored_runs": cens, "L_mean": (sum(Ls) / n) if n else None, "ci99": ci,
                 "L_P_mean": (sum(LPs) / len(LPs)) if LPs else None, "L_pred": Lp, "band": b,
                 "rule": "PASS: the 99%% CI of the block-mean L lies inside L_pred +- b (>= %s blocks); FAIL: wholly outside" % P.get("g4_min_blocks", 8)}
    # G2 host bands over every valid run's telemetry
    tels = []
    for r in R:
        d = [x for x in dirs if os.path.basename(x) == r["_session"]][0]
        f = os.path.join(d, "tel-%s.jsonl" % r.get("idx"))
        tel = load_jsonl(f) or load_jsonl(f + ".gz")
        F = sorted((sample_fields(x) for x in tel if x.get("t_ms") is not None), key=lambda x: x[0])
        if F:
            tels.append(F)
    hb2 = RD.host_bands(tels)
    C, D, U = hb2["G2-C"], hb2["G2-D"], hb2["G2-U"]
    def vv(n_, ok, need=20):
        return "INSUFFICIENT" if n_ < need else ("PASS" if ok else "FAIL")
    out["G2-C"] = {"verdict": vv(C["n"], C["n"] and C["le1"] >= 0.95 * C["n"] and C["none"] >= 0.25 * C["n"]), **C,
                   "rule": ">= 20 climbs; >= 95% show 700 in <= 1 sample and >= 25% none"}
    out["G2-D"] = {"verdict": vv(D["n"], D["n"] and D["in_band"] >= 0.9 * D["n"]), **{k: v for k, v in D.items()},
                   "rule": ">= 20 descents 800->700->600; the 700 dwell in [0.3, 0.7] s in >= 90%"}
    out["G2-U"] = {"verdict": vv(U["n"], U["n"] and U["le_thr1"] == U["n"] and U["le_thr"] >= 0.8 * U["n"] and U["ge_thr2"] == 0), **U,
                   "rule": ">= 20 up-steps; the preceding reading <= 66 in 100%, <= 65 in >= 80%, never >= 67"}
    # G3-L: launch -> first 800 (measured launches of valid T/ADD runs); G3-I: kernel end -> 600 with no episode running
    lat = sorted(round(((r.get("obs") or {})["t_up"] - (r.get("obs") or {})["t0_ms"]) / 1000.0, 2) for r in R
                 if r.get("kind") in ("T", "ADD") and run_valid(r) and (r.get("obs") or {}).get("t_up") and (r.get("obs") or {}).get("t0_ms"))
    med = lat[len(lat) // 2] if lat else None
    out["G3-L"] = {"verdict": "INSUFFICIENT" if len(lat) < 10 else ("PASS" if 0.4 <= med <= 1.0 and lat[-1] <= 2.2 else "FAIL"),
                   "n": len(lat), "median_s": med, "max_s": lat[-1] if lat else None,
                   "rule": ">= 10 launches; median in [0.4, 1.0] s and all <= 2.2 s"}
    idl = []
    for r in R:
        o = r.get("obs") or {}
        if r.get("kind") in ("T", "ADD") and run_valid(r) and o.get("t_up") and o.get("trip_s") is None:
            m = re.search(r"600 MHz ([0-9.]+) s after the kernel end", str(r.get("post") or ""))
            if m:
                idl.append(float(m.group(1)))
    out["G3-I"] = {"verdict": "INSUFFICIENT" if len(idl) < 10 else ("PASS" if all(0 <= x <= 1.6 for x in idl) else "FAIL"),
                   "n": len(idl), "max_s": max(idl) if idl else None,
                   "rule": ">= 10 runs ending at 800 MHz with no trip; every kernel end -> 600 in [0, 1.6] s"}
    return out


def theory_summary(V):
    th = {"TH1-busy": ["G1-T", "G1-H"], "TH1-idle": ["I1"], "TH2": ["I4", "I5", "G2-C", "G2-D"], "TH3": ["I2", "G2-U"],
          "TH4": ["G3-L", "G3-I"], "TH5": ["G4"], "Q2": ["G4-S"], "TH7": ["I3"], "TH8": ["I6"]}
    out = {}
    for t, items in th.items():
        vs = [V[i]["verdict"] for i in items if i in V and V[i]["verdict"] != "NOT REGISTERED"]
        if not vs:
            out[t] = "not registered"
            continue
        out[t] = "fell" if "FAIL" in vs else ("survived" if all(v == "PASS" for v in vs) else "untested (INSUFFICIENT)")
    return out


def run(data, dev, out_path):
    dirs = cycles_of(data, dev)
    A = analyse(dirs, windows=session_windows(data))
    V = verdicts(A)
    P = (json.load(open(os.path.join(HERE, "prereg-val.json"))) if os.path.exists(os.path.join(HERE, "prereg-val.json")) else {}).get("g4", {})
    nd = nat_sessions(data, dev)
    if nd:
        V.update(g_items(nd, P))
    res = {"label": ("DV2 development idle statistics (Z1 cycles): development data, tests nothing" if dev else
                     "DV2 validation verdicts (PREREG-VAL, aifoundry2 replication, VZ cycles)"),
           "data": data, "cycles": len(dirs), "offset_fits": len(A["offsets"]), "offset_kind": A["offset_kind"],
           "offset_uncertainty_s": A["offset_uncertainty_s"],
           "offset_spread_ms_max": max((o[2] for o in A["offsets"]), default=None),
           "items": V, "theories": theory_summary(V),
           "per_cycle": [{k: v for k, v in c.items() if k not in ("t0", "t1", "res4_t")} for c in A["cycles"]],
           "residency": A["i6"], "enter_exit": A["i4"], "exit_next": A["i3"], "idle_enters": A["i5"],
           "t": time.strftime("%Y-%m-%dT%H:%M:%S")}
    if out_path:
        json.dump(res, open(out_path, "w"), indent=1)
    return res


# ------------------------------------------------------------------------------------------------ self-test
def selftest():
    ok = True
    def chk(name, cond):
        nonlocal ok
        print(("PASS  " if cond else "FAIL  ") + name)
        ok &= bool(cond)
    # a synthetic analysis object (the rules only)
    def mk(cyc, i3=(), i4=(), i5=(), i6=(), thr=(), busy=()):
        return {"cycles": list(cyc), "i3": list(i3), "i4": list(i4), "i5": list(i5), "i6": list(i6),
                "thr": list(thr), "busy_ts": list(busy)}
    def c(state, m, h, t0, qb=100.0):
        return {"clean": True, "state": state, "m": m, "h_min": h, "t0": t0, "quiet_before_s": qb,
                "class": "HMAX-SEP" if state == "OUT" and h >= 66 else "HMEAN-VIOL" if state == "IN" and m <= 64 else "both",
                "strong": state == "OUT" and h >= 67}
    hmean = [c("OUT", 64, 66, 10000 * (k // 2) + 100 + k, qb=100 + k) for k in range(6)] + [c("IN", 68, 70, 90000)]
    V = verdicts(mk(hmean))
    chk("I1: H-mean world (OUT cycles at high 66, 3 stretches) -> PASS", V["I1"]["verdict"] == "PASS")
    hmax = [c("IN", 64, 66, 1000 * k) for k in range(4)] + [c("OUT", 63, 65, 9000)]
    V = verdicts(mk(hmax))
    chk("I1: H-max world (IN cycles at mean 64) -> FAIL", V["I1"]["verdict"] == "FAIL")
    V = verdicts(mk([c("OUT", 62, 64, 1)]))
    chk("I1: nothing discriminating -> INSUFFICIENT", V["I1"]["verdict"] == "INSUFFICIENT")
    thr = [{"kind": "thermal_down", "T": 66, "ts": 10 ** 9 + i} for i in range(10)] + \
          [{"kind": "thermal_idle", "T": 65, "ts": 2 * 10 ** 9 + i} for i in range(10)]
    chk("I2: 66/65 lines -> PASS", verdicts(mk([], thr=thr))["I2"]["verdict"] == "PASS")
    chk("I2: an ENTER printing 67 -> FAIL",
        verdicts(mk([], thr=thr + [{"kind": "thermal_down", "T": 67, "ts": 3 * 10 ** 9}]))["I2"]["verdict"] == "FAIL")
    i3 = [{"ts": 10 ** 9 * k, "next": "power_idle", "dt_s": 0.13} for k in range(10)]
    chk("I3: EXIT -> PIDLE 0.13 s -> PASS", verdicts(mk([], i3=i3))["I3"]["verdict"] == "PASS")
    chk("I3: an EXIT followed by a PUP -> FAIL",
        verdicts(mk([], i3=i3 + [{"ts": 1, "next": "power_up", "dt_s": 0.1}]))["I3"]["verdict"] == "FAIL")
    loop = [{"ts": 10 ** 9 * k, "d_s": 0.8106, "k": 2, "resid_s": 0.0} for k in range(5)]
    chk("I4: a 0.405 s loop -> PASS", verdicts(mk([], i4=loop))["I4"]["verdict"] == "PASS")
    perpass = []
    for k in range(10):
        d = 0.156 * (k + 1)
        kk = int(round(d / P_LOOP))
        perpass.append({"ts": 10 ** 9 * k, "d_s": d, "k": kk, "resid_s": round(d - kk * P_LOOP, 4)})
    chk("I4: one step per 0.156 s pass (HEAD-like) -> FAIL", verdicts(mk([], i4=perpass))["I4"]["verdict"] == "FAIL")
    chk("I5: idle ENTERs -> PASS", verdicts(mk([], i5=[{"ts": 10 ** 9 * k} for k in range(3)]))["I5"]["verdict"] == "PASS")
    warm = [{"m": 63}, {"m": 67}] * 3
    chk("I5: a busy-test governor (no idle ENTER over 3 warmings) -> FAIL",
        verdicts(mk(warm))["I5"]["verdict"] == "FAIL")
    i6 = [{"busy": False, "n_ep": 2, "straddle": 0, "diff_ms": 0.1} for _ in range(3)]
    chk("I6: counter = episodes -> PASS", verdicts(mk([], i6=i6))["I6"]["verdict"] == "PASS")
    chk("I6: a hidden 400 ms episode -> FAIL",
        verdicts(mk([], i6=i6 + [{"busy": False, "n_ep": 1, "straddle": 0, "diff_ms": 400.0}]))["I6"]["verdict"] == "FAIL")
    print("self-test:", "all passed" if ok else "FAILED")
    return 0 if ok else 1


def main(argv):
    if "--self-test" in argv:
        return selftest()
    data = argv[argv.index("--data") + 1]
    dev = "--dev" in argv
    out = argv[argv.index("--out") + 1] if "--out" in argv else os.path.join(data, "dev-idle.json" if dev else "verdicts-dv2val.json")
    res = run(data, dev, out)
    print(res["label"])
    print("cycles %d, offset fits %d (max spread %s ms)" % (res["cycles"], res["offset_fits"], res["offset_spread_ms_max"]))
    for k, v in res["items"].items():
        print("  %s %-12s %s" % (k, v["verdict"], {a: b for a, b in v.items() if a not in ("verdict", "rule", "resid_s", "diffs_ms")}))
    print("theories:", res["theories"])
    print("->", out)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
