#!/usr/bin/env python3
"""E135's reduction, registered with E135.md before the first measured call.

    python3 reduce_e135.py <run_dir> [--preds predictions-e135.json] [--json results.json] > reduce.txt

<run_dir> holds one run as `modal volume get e135-a100-kinds /<run_id>` writes it: <unit>/steps/NNN_<label>.json.gz,
<unit>/samples/NNN.jsonl.gz, <unit>/DONE. Units A and B are the measured ones; S is the smoke. Standard library only.

A window's rate is (groups whose midpoint falls in it) x calls per group x 2 n^3 / (their summed CUDA-event time).
A window's NVML values are the 100 ms samples whose midpoint ((t + tb) / 2) falls in it; its power is the energy
counter's slope over the window where the counter reads, else the mean of nvmlDeviceGetPowerUsage."""
import argparse
import glob
import gzip
import json
import math
import os
import statistics
import sys

BITS = {"idle": 0x1, "app_clocks": 0x2, "sw_power": 0x4, "hw_slowdown": 0x8, "sync_boost": 0x10,
        "sw_thermal": 0x20, "hw_thermal": 0x40, "hw_power_brake": 0x80, "display": 0x100}
THERMAL = ("hw_slowdown", "sw_thermal", "hw_thermal")
RANDOM_OF = {"bf16": "randn", "fp16": "randn", "tf32": "randn", "int8": "rand_full"}
CHART_NAME = {"randn": "Randn", "checker": "Checkerboard", "sparse75": "Sparse", "rand": "Rand", "ternary": "Ternary",
              "onebit": "One Bit", "pi": "All Pi", "twos": "Twos", "zeros": "Zeros"}
T95 = {1: 12.706, 2: 4.303, 3: 3.182, 4: 2.776, 5: 2.571, 6: 2.447, 7: 2.365}


def mean(x):
    return sum(x) / len(x) if x else None


def rnd(x, k=4):
    return None if x is None else round(x, k)


def summary(vals):
    v = [x for x in vals if x is not None]
    if not v:
        return {"n": 0}
    out = {"n": len(v), "mean": mean(v), "min": min(v), "max": max(v), "values": [rnd(x) for x in v]}
    if len(v) >= 2:
        sd = statistics.stdev(v)
        out["sd"] = sd
        out["t95_half"] = T95.get(len(v) - 1, 2.0) * sd / math.sqrt(len(v))
    return out


# ------------------------------------------------------------------------------------------------- loading
def load_unit(d):
    steps = []
    for p in sorted(glob.glob(os.path.join(d, "steps", "*.json.gz"))):
        with gzip.open(p, "rt", encoding="utf-8") as f:
            steps.append(json.load(f))
    samples, status = [], []
    for p in sorted(glob.glob(os.path.join(d, "samples", "*.jsonl.gz"))):
        with gzip.open(p, "rt", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                r = json.loads(line)
                (samples if "tb" in r else status).append(r)
    samples.sort(key=lambda r: r["t"])
    done = None
    if os.path.exists(os.path.join(d, "DONE")):
        done = json.load(open(os.path.join(d, "DONE")))
    static = next((s.get("static") for s in steps if s.get("op") == "static"), None) or {}
    idle0 = next((s for s in steps if s.get("op") == "idle" and s.get("label") == "idle0"), None)
    return {"steps": steps, "samples": samples, "status": status, "done": done, "static": static, "idle0": idle0}


def tmid(r):
    return 0.5 * (r["t"] + r["tb"])


def wstats(samples, lo, hi):
    S = [r for r in samples if lo <= tmid(r) < hi]
    out = {"n_samples": len(S)}
    if not S:
        return out

    def col(k):
        return [r[k] for r in S if r.get(k) is not None]
    sm = col("sm")
    if sm:
        out.update(sm_mean=mean(sm), sm_med=statistics.median(sm), sm_min=min(sm), sm_max=max(sm))
    mem = col("mem")
    out["mem_mean"] = mean(mem)
    p = col("p_mw")
    out["p_mean_w"] = mean(p) / 1000.0 if p else None
    pi = col("p_inst_mw")
    out["p_inst_mean_w"] = mean(pi) / 1000.0 if pi else None
    pa = col("p_avg_mw")
    out["p_avg_mean_w"] = mean(pa) / 1000.0 if pa else None
    E = [(tmid(r), r["e_mj"]) for r in S if r.get("e_mj") is not None]
    out["p_energy_w"] = ((E[-1][1] - E[0][1]) / 1000.0 / (E[-1][0] - E[0][0])) if len(E) >= 2 and E[-1][0] > E[0][0] else None
    out["power_w"] = out["p_energy_w"] if out["p_energy_w"] is not None else out["p_mean_w"]
    T = col("temp")
    if T:
        out.update(temp_first=T[0], temp_last=T[-1], temp_max=max(T), temp_mean=mean(T))
    tm = col("t_mem")
    out["tmem_max"] = max(tm) if tm else None
    pl = col("plim_mw")
    out["plim_w"] = statistics.median(pl) / 1000.0 if pl else None
    R = col("rsn")
    if R:
        out["frac"] = {k: sum(1 for x in R if x & b) / len(R) for k, b in BITS.items()}
        out["frac_thermal_max"] = max(out["frac"][k] for k in THERMAL)
        out["rsn_values"] = sorted(set(R))
    ps = col("pstate")
    out["pstates"] = sorted(set(ps))
    u = [r["util"][0] for r in S if r.get("util")]
    out["util_gpu_mean"] = mean(u)
    vp = col("viol_pow_ns")
    if len(vp) >= 2 and tmid(S[-1]) > tmid(S[0]):
        out["viol_pow_share"] = (vp[-1] - vp[0]) / 1e9 / (tmid(S[-1]) - tmid(S[0]))
    gaps = [S[i + 1]["t"] - S[i]["t"] for i in range(len(S) - 1)]
    out["sample_dt_mean"] = mean(gaps)
    out["read_ms_mean"] = mean([(r["tb"] - r["t"]) * 1000 for r in S])
    return out


# ------------------------------------------------------------------------------------------------- cells
def windows_of(st):
    b, s = st["burst_s"], st["sus_s"]
    return {"early": (0.0, 0.5), "burst": (0.0, b), "sus": (b, b + s), "late": (max(b, b + s - 15.0), b + s)}


def reduce_cell(rec, samples):
    run = rec["run"]
    t0, G = run["t0"], run["group"]
    F = rec["flop_per_mm"] * G
    cum = run["cum_ms"]
    starts = [0.0] + cum[:-1]
    out = {}
    for w, (a, b) in windows_of(rec["step"]).items():
        idx = [i for i in range(len(cum)) if a <= 0.5 * (starts[i] + cum[i]) / 1000.0 < b]
        if not idx:
            out[w] = None
            continue
        dur = sum(cum[i] - starts[i] for i in idx) / 1000.0
        tf = len(idx) * F / dur / 1e12
        per = [F / ((cum[i] - starts[i]) / 1000.0) / 1e12 for i in idx if cum[i] > starts[i]]
        st = wstats(samples, t0 + a, t0 + b)
        st.update(tflops=tf, n_groups=len(idx), dur_s=dur, tflops_group_sd=statistics.stdev(per) if len(per) > 1 else None)
        st["tflops_per_ghz"] = tf / (st["sm_mean"] / 1000.0) if st.get("sm_mean") else None
        st["pj_per_flop"] = st["power_w"] / tf if st.get("power_w") else None
        out[w] = st
    return out


def cell_key(unit, rec):
    s = rec["step"]
    return (unit, rec["cap"], s["size"], s["dtype"], s["kind"], s["pass"])


# ------------------------------------------------------------------------------------------------- protocol
def reduce_protocol(rec, samples):
    rows = rec["rows"]
    by = {}
    for r in rows:
        by.setdefault(r["kind"], []).append(r)
    out = {"kinds": {}}
    for k, rs in by.items():
        tf = sorted(r["tflops"] for r in rs)
        n = len(tf)
        med = tf[n // 2] if n % 2 else 0.5 * (tf[n // 2] + tf[n // 2 - 1])
        sms, pws, sw = [], [], []
        for r in rs:
            st = wstats(samples, r["t_a"], r["t_b"])
            if st.get("sm_mean"):
                sms.append(st["sm_mean"])
            if st.get("p_mean_w"):
                pws.append(st["p_mean_w"])
            if st.get("frac"):
                sw.append(st["frac"]["sw_power"])
        out["kinds"][k] = {"median_tflops": med, "tflops": [rnd(x, 3) for x in tf], "sm_mean": mean(sms),
                           "p_mean_w": mean(pws), "sw_power_share": mean(sw), "n": n}
    if "zeros" in out["kinds"] and "randn" in out["kinds"]:
        out["zeros_over_randn"] = out["kinds"]["zeros"]["median_tflops"] / out["kinds"]["randn"]["median_tflops"]
    out["t_a"] = rows[0]["t_a"] if rows else None
    out["t_b"] = rows[-1]["t_b"] if rows else None
    return out


# ------------------------------------------------------------------------------------------------- rules
def spearman(x, y):
    def ranks(v):
        order = sorted(range(len(v)), key=lambda i: v[i])
        r = [0.0] * len(v)
        i = 0
        while i < len(v):
            j = i
            while j + 1 < len(v) and v[order[j + 1]] == v[order[i]]:
                j += 1
            for k in range(i, j + 1):
                r[order[k]] = 0.5 * (i + j) + 1
            i = j + 1
        return r
    rx, ry = ranks(x), ranks(y)
    mx, my = mean(rx), mean(ry)
    num = sum((a - mx) * (b - my) for a, b in zip(rx, ry))
    den = math.sqrt(sum((a - mx) ** 2 for a in rx) * sum((b - my) ** 2 for b in ry))
    return num / den if den else None


def band(gH, LH, P0, L, n):
    r = (1.0 / gH) * ((L - P0) / (LH - P0)) ** (1.0 / n)
    return max(1.0, 1.0 / r)


def verdict(oks):
    """Per replicate (R1): HOLDS if every replicate meets it, FAILS if none does, else MIXED."""
    oks = [o for o in oks if o is not None]
    if not oks:
        return "N/A"
    if all(oks):
        return "HOLDS"
    if not any(oks):
        return "FAILS"
    return "MIXED"


def verdict_all(oks):
    """Every applicable item must meet it (R2-R10): HOLDS if all do, else FAILS."""
    oks = [o for o in oks if o is not None]
    if not oks:
        return "N/A"
    return "HOLDS" if all(oks) else "FAILS"


def score(units, preds):
    TH = preds["thresholds"]
    cells, protos, lowcaps = {}, {}, {}
    for u, U in units.items():
        for rec in U["steps"]:
            if rec.get("error"):
                continue
            if rec.get("op") == "cell":
                cells[cell_key(u, rec)] = {"rec": rec, "w": reduce_cell(rec, U["samples"])}
            elif rec.get("op") == "protocol":
                protos[(u, rec["cap"], rec["label"])] = reduce_protocol(rec, U["samples"])
            elif rec.get("op") == "lowcap":
                lowcaps[u] = rec

    def W(u, cap, size, dt, kind, p, w):
        c = cells.get((u, cap, size, dt, kind, p))
        return c["w"].get(w) if c else None

    def fmax(u):
        v = units[u]["static"].get("max_clock_sm")
        return v if isinstance(v, (int, float)) else None

    # the gap table
    gaps = []
    for (u, cap, size, dt, kind, p), c in sorted(cells.items()):
        if kind != "zeros":
            continue
        rk = RANDOM_OF[dt]
        for w in ("early", "burst", "sus", "late"):
            z, r = W(u, cap, size, dt, "zeros", p, w), W(u, cap, size, dt, rk, p, w)
            if not z or not r:
                continue
            gaps.append({"unit": u, "cap": cap, "size": size, "dtype": dt, "pass": p, "window": w,
                         "gap_rate": z["tflops"] / r["tflops"],
                         "gap_clock": (z["sm_mean"] / r["sm_mean"]) if z.get("sm_mean") and r.get("sm_mean") else None,
                         "sw_zeros": (z.get("frac") or {}).get("sw_power"), "sw_random": (r.get("frac") or {}).get("sw_power"),
                         "p_zeros": z.get("power_w"), "p_random": r.get("power_w"), "plim": r.get("plim_w")})

    def gsel(**kw):
        return [g for g in gaps if all(g.get(k) == v for k, v in kw.items())]

    rules = {}
    # R1 (P2): the ET-SoC-1 mechanism, bf16 sustained, default cap
    det = []
    for g in gsel(cap="default", size=8192, dtype="bf16", window="sus"):
        u, p = g["unit"], g["pass"]
        z, r = W(u, "default", 8192, "bf16", "zeros", p, "sus"), W(u, "default", 8192, "bf16", "randn", p, "sus")
        a = r["sm_mean"] <= TH["clock_below"] * z["sm_mean"]
        fr = r.get("frac") or {}
        b = fr.get("sw_power", 0) >= TH["capped_share"] and r.get("frac_thermal_max", 1) <= TH["thermal_share_max"]
        ratio = r["power_w"] / r["plim_w"] if r.get("power_w") and r.get("plim_w") else None
        c = ratio is not None and TH["power_at_cap_lo"] <= ratio <= TH["power_at_cap_hi"]
        det.append({"unit": u, "pass": p, "clock_ratio": rnd(r["sm_mean"] / z["sm_mean"]), "a_clock_below": a,
                    "sw_power_share": rnd(fr.get("sw_power")), "thermal_max": rnd(r.get("frac_thermal_max")),
                    "b_cap_not_thermal": b, "power_over_limit": rnd(ratio), "c_on_cap": c, "ok": a and b and c})
    rules["R1"] = {"verdict": verdict([d["ok"] for d in det]), "detail": det}

    # R2 (P3): speed follows the clock
    det = []
    groups = {}
    for (u, cap, size, dt, kind, p), c in cells.items():
        if size != 8192:
            continue
        for w in ("burst", "sus"):
            x = c["w"].get(w)
            if x and x.get("tflops_per_ghz"):
                groups.setdefault((u, cap, dt, w), []).append((kind, p, x["tflops_per_ghz"]))
    for key, v in sorted(groups.items()):
        if len(v) < 2:
            continue
        vals = [t for _, _, t in v]
        spread = max(vals) / min(vals)
        det.append({"unit": key[0], "cap": key[1], "dtype": key[2], "window": key[3], "n": len(v),
                    "spread": rnd(spread), "lo": min(v, key=lambda t: t[2])[:2], "hi": max(v, key=lambda t: t[2])[:2],
                    "ok": spread <= TH["speed_follows_clock_spread"]})
    rules["R2"] = {"verdict": verdict_all([d["ok"] for d in det]), "detail": det}

    # R3 (P4): the cap's dichotomy, every default-cap 8192 cell, sustained
    det = []
    for (u, cap, size, dt, kind, p), c in sorted(cells.items()):
        if cap != "default" or size != 8192:
            continue
        x = c["w"].get("sus")
        if not x or not x.get("plim_w") or not x.get("power_w"):
            continue
        fr = (x.get("frac") or {}).get("sw_power")
        ratio = x["power_w"] / x["plim_w"]
        f = fmax(u)
        clauses = []
        if ratio < TH["power_at_cap_lo"]:
            clauses.append(("under", (f is not None and x["sm_mean"] >= TH["clock_at_max"] * f) and (fr is not None and fr <= TH["uncapped_share"])))
        if fr is not None and fr >= TH["capped_share"]:
            clauses.append(("capped", ratio >= TH["power_at_cap_lo"]))
        if clauses:
            det.append({"unit": u, "dtype": dt, "kind": kind, "pass": p, "power_over_limit": rnd(ratio),
                        "sw_power_share": rnd(fr), "sm_mean": rnd(x["sm_mean"], 1), "f_max": f,
                        "clauses": clauses, "ok": all(ok for _, ok in clauses)})
    rules["R3"] = {"verdict": verdict_all([d["ok"] for d in det]), "detail": det}

    # R4 (P9): the gap where and only where the cap acts
    det = []
    for g in gaps:
        if g["size"] != 8192 or g["window"] not in ("burst", "sus") or g["sw_zeros"] is None or g["sw_random"] is None:
            continue
        if g["sw_random"] >= TH["capped_share"] and g["sw_zeros"] <= TH["uncapped_share"]:
            det.append(dict(g, case="random capped", ok=g["gap_rate"] >= TH["iff_gap_min"]))
        elif g["sw_random"] <= TH["uncapped_share"] and g["sw_zeros"] <= TH["uncapped_share"]:
            det.append(dict(g, case="neither capped", ok=abs(g["gap_rate"] - 1.0) <= TH["iff_no_gap"]))
    rules["R4"] = {"verdict": verdict_all([d["ok"] for d in det]), "detail": det}

    # R5 (P5): the lower cap
    lc = lowcaps.get("A")
    if not lc or not lc.get("applied"):
        why = "the lower-cap arm did not run" if not lc else f"not applied: nvidia-smi -pl rc {lc.get('set', {}).get('rc')}"
        rules["R5"] = {"verdict": "N/A", "why": why, "detail": lc and {k: lc.get(k) for k in ("target_w", "set", "restore")}}
    else:
        capl = f"{lc['target_w']:g}W"
        r2, z2 = W("A", capl, 8192, "bf16", "randn", 1, "sus"), W("A", capl, 8192, "bf16", "zeros", 1, "sus")
        r1, z1 = W("A", "default", 8192, "bf16", "randn", 1, "sus"), W("A", "default", 8192, "bf16", "zeros", 1, "sus")
        oks = []
        d = {"cap": capl}
        if r2:
            ratio = r2["power_w"] / lc["target_w"]
            d["a_power_over_new_cap"] = rnd(ratio)
            d["a_sw_power"] = rnd((r2.get("frac") or {}).get("sw_power"))
            d["a_ok"] = TH["power_at_cap_lo"] <= ratio <= TH["power_at_cap_hi"] and d["a_sw_power"] >= TH["capped_share"]
            oks.append(d["a_ok"])
        if r1 and z1 and r2 and z2:
            d["b_gap_default"] = rnd(z1["tflops"] / r1["tflops"])
            d["b_gap_low"] = rnd(z2["tflops"] / r2["tflops"])
            d["b_ok"] = d["b_gap_low"] > d["b_gap_default"]
            oks.append(d["b_ok"])
        cs = []
        for kind in ("zeros", "twos", "rand", "randn"):
            k1, k2 = W("A", "default", 8192, "bf16", kind, 1, "sus"), W("A", capl, 8192, "bf16", kind, 1, "sus")
            if k1 and k2 and k1.get("power_w") and k1["power_w"] < TH["power_at_cap_lo"] * lc["target_w"]:
                same = abs(k2["sm_mean"] / k1["sm_mean"] - 1.0) <= TH["lowcap_clock_same"]
                cs.append({"kind": kind, "p_default": rnd(k1["power_w"], 1), "clock_ratio": rnd(k2["sm_mean"] / k1["sm_mean"]), "ok": same})
                oks.append(same)
        d["c_kinds_under_new_cap"] = cs
        rules["R5"] = {"verdict": verdict_all(oks), "detail": d}

    # R6 (P6): the gap at our cap from Horace's at his
    mb = preds["model_band"]
    det = []
    for u in sorted(units):
        if u == "S":
            continue
        gs = [g["gap_rate"] for g in gsel(unit=u, cap="default", size=8192, dtype="bf16", window="sus")]
        L = None
        for g in gsel(unit=u, cap="default", size=8192, dtype="bf16", window="sus"):
            L = g["plim"]
        if not gs or not L:
            continue
        lo, mid, hi = (band(mb["gH"], mb["LH"], mb["P0"], L, n) for n in (1, 2, 3))
        m = mean(gs)
        det.append({"unit": u, "limit_w": rnd(L, 1), "gap_mean": rnd(m), "gaps": [rnd(x) for x in gs],
                    "band": [rnd(lo), rnd(hi)], "n2": rnd(mid), "ok": lo - 1e-9 <= m <= hi + 1e-9})
    sub = []
    if lc and lc.get("applied") and abs(lc["target_w"] - 330.0) < 0.5:
        lo, hi = TH["gist_at_330"]
        capl = f"{lc['target_w']:g}W"
        r2, z2 = W("A", capl, 8192, "bf16", "randn", 1, "sus"), W("A", capl, 8192, "bf16", "zeros", 1, "sus")
        if r2 and z2:
            g = z2["tflops"] / r2["tflops"]
            sub.append({"what": "cells at 330 W", "gap": rnd(g), "band": [lo, hi], "ok": lo <= g <= hi})
        pr = protos.get(("A", capl, "gist6"))
        if pr and pr.get("zeros_over_randn"):
            g = pr["zeros_over_randn"]
            sub.append({"what": "gist6 at 330 W", "gap": rnd(g), "band": [lo, hi], "ok": lo <= g <= hi})
    rules["R6"] = {"verdict": verdict_all([d["ok"] for d in det]), "detail": det,
                   "at_330": {"verdict": verdict_all([s["ok"] for s in sub]), "detail": sub}}

    # R7 (P7): burst and sustained gaps alike
    det = []
    for g in gsel(cap="default", size=8192, dtype="bf16", window="sus"):
        b = [x for x in gsel(unit=g["unit"], cap="default", size=8192, dtype="bf16", window="burst", **{"pass": g["pass"]})]
        if b:
            dlt = g["gap_rate"] - b[0]["gap_rate"]
            det.append({"unit": g["unit"], "pass": g["pass"], "burst": rnd(b[0]["gap_rate"]), "sus": rnd(g["gap_rate"]),
                        "sus_minus_burst": rnd(dlt), "ok": TH["burst_sus_lo"] <= dlt <= TH["burst_sus_hi"]})
    rules["R7"] = {"verdict": verdict_all([d["ok"] for d in det]), "detail": det}

    # R8 (P8): thermal reasons inactive
    det = []
    for (u, cap, size, dt, kind, p), c in sorted(cells.items()):
        x = c["w"].get("sus")
        if x and x.get("frac"):
            det.append({"unit": u, "cap": cap, "size": size, "dtype": dt, "kind": kind, "pass": p,
                        "thermal_max": rnd(x["frac_thermal_max"]), "temp_max": x.get("temp_max"),
                        "ok": x["frac_thermal_max"] <= TH["thermal_share_max"]})
    rules["R8"] = {"verdict": verdict_all([d["ok"] for d in det]), "n": len(det),
                   "failing": [d for d in det if not d["ok"]], "temp_max": max([d["temp_max"] for d in det if d["temp_max"] is not None], default=None)}

    # R9 (P10): the chart's ranking
    ch = preds["horace"]["chart"]
    ours = {}
    for kind in CHART_NAME:
        v = [W(u, "default", 8192, "bf16", kind, 1, "sus") for u in units if u != "S"]
        v = [x["tflops"] for x in v if x]
        if v:
            ours[kind] = mean(v)
    if len(ours) == 9:
        x = [ours[k] for k in CHART_NAME]
        y = [ch[CHART_NAME[k]] for k in CHART_NAME]
        spread = max(x) / min(x)
        rho = spearman(x, y)
        ok = None if spread < TH["chart_spread_min"] else (rho is not None and rho >= TH["chart_rho_min"])
        rules["R9"] = {"verdict": "N/A" if ok is None else ("HOLDS" if ok else "FAILS"), "rho": rnd(rho),
                       "spread": rnd(spread), "ours": {k: rnd(v, 2) for k, v in ours.items()}}
    else:
        rules["R9"] = {"verdict": "N/A", "why": f"{len(ours)} of 9 kinds"}

    # R10 (P11): Horace's protocol against the sustained cells
    det = []
    for u in sorted(units):
        pr = protos.get((u, "default", "gist6"))
        gs = gsel(unit=u, cap="default", size=8192, dtype="bf16", window="sus", **{"pass": 1})
        if pr and pr.get("zeros_over_randn") and gs:
            dlt = pr["zeros_over_randn"] - gs[0]["gap_rate"]
            det.append({"unit": u, "protocol": rnd(pr["zeros_over_randn"]), "cells_sus": rnd(gs[0]["gap_rate"]),
                        "diff": rnd(dlt), "ok": abs(dlt) <= TH["protocol_vs_cells"]})
    rules["R10"] = {"verdict": verdict_all([d["ok"] for d in det]), "detail": det}
    return cells, protos, lowcaps, gaps, rules


# ------------------------------------------------------------------------------------------------- report
def checks(units, cells):
    out = []
    for u, U in units.items():
        st = U["static"]
        out.append((f"{u}: GPU name", st.get("name"), "A100" in str(st.get("name"))))
        errs = [s.get("label") for s in U["steps"] if s.get("error")]
        out.append((f"{u}: steps with an error", errs, not errs))
        skipped = (U["done"] or {}).get("skipped", [])
        out.append((f"{u}: steps skipped on the budget", len(skipped), True))
        health = [s for s in U["status"] if s.get("status") in ("health", "end")]
        if health:
            out.append((f"{u}: NVML calls not supported", health[-1].get("dead"), True))
            out.append((f"{u}: NVML call errors", health[-1].get("errs"), True))
    for key, c in sorted(cells.items()):
        rec = c["rec"]
        if rec["step"]["kind"] == "zeros":
            out.append((f"{key}: zeros give C = 0", rec["check"]["C_absmax"], rec["check"]["C_absmax"] == 0.0))
        x = c["w"].get("sus")
        if x:
            exp = (windows_of(rec["step"])["sus"][1] - windows_of(rec["step"])["sus"][0]) / 0.1
            out.append((f"{key}: sustained samples / expected", f"{x['n_samples']}/{exp:.0f}", x["n_samples"] >= 0.9 * exp))
        w = rec["wait"]
        out.append((f"{key}: start {w['T_start']} C, target {w['target']}", w["reached"], True))
    return out


def fmt_cell_table(cells, units):
    lines = ["| unit | cap | n | format | kind | pass | start C | burst T/s | burst MHz | burst W | sus T/s | sus MHz | "
             "sus W | limit W | SW cap share | thermal max | die C end | HBM C max | pJ/FLOP sus |",
             "|" + "---|" * 19]
    for (u, cap, size, dt, kind, p), c in sorted(cells.items(), key=lambda kv: (kv[0][0], kv[0][1] != "default", kv[0][1], -kv[0][2], kv[0][3], kv[0][4], kv[0][5])):
        b, s = c["w"].get("burst") or {}, c["w"].get("sus") or {}

        def f(x, k=1):
            return "—" if x is None else f"{x:.{k}f}"
        lines.append(f"| {u} | {cap} | {size} | {dt} | {kind} | {p} | {c['rec']['wait']['T_start']} | {f(b.get('tflops'))} | "
                     f"{f(b.get('sm_mean'), 0)} | {f(b.get('power_w'))} | {f(s.get('tflops'))} | {f(s.get('sm_mean'), 0)} | "
                     f"{f(s.get('power_w'))} | {f(s.get('plim_w'), 0)} | {f((s.get('frac') or {}).get('sw_power'), 2)} | "
                     f"{f(s.get('frac_thermal_max'), 2)} | {s.get('temp_last', '—')} | {s.get('tmem_max', '—')} | "
                     f"{f(s.get('pj_per_flop'), 3)} |")
    return lines


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("run_dir")
    ap.add_argument("--preds", default=os.path.join(os.path.dirname(os.path.abspath(__file__)), "predictions-e135.json"))
    ap.add_argument("--json", default=None)
    ap.add_argument("--units", default=None, help="comma-separated, default every unit directory")
    a = ap.parse_args()
    preds = json.load(open(a.preds))
    names = a.units.split(",") if a.units else sorted(d for d in os.listdir(a.run_dir) if os.path.isdir(os.path.join(a.run_dir, d)))
    units = {u: load_unit(os.path.join(a.run_dir, u)) for u in names}
    cells, protos, lowcaps, gaps, rules = score(units, preds)
    P = print
    P(f"# E135 reduction of {os.path.basename(os.path.abspath(a.run_dir))}: units {', '.join(names)}")
    P("")
    for u, U in units.items():
        st = U["static"]
        P(f"unit {u}: {st.get('name')}, driver {st.get('driver')}, VBIOS {st.get('vbios')}, board {st.get('uuid_sha12')}, "
          f"limit default/enforced {st.get('power_default_mw')}/{st.get('power_enforced_mw')} mW, "
          f"constraints {st.get('power_constraints_mw')}, max SM/MEM {st.get('max_clock_sm')}/{st.get('max_clock_mem')} MHz, "
          f"app SM {st.get('app_clock_sm')}, slowdown {st.get('temp_threshold_slowdown')} C, gpu_max {st.get('temp_threshold_gpu_max')} C; "
          f"torch {st.get('torch')}, cuBLAS {(st.get('pip') or {}).get('nvidia-cublas-cu12')}")
        if U["idle0"]:
            i0 = U["idle0"]
            w = wstats(U["samples"], i0["t_a"], i0["t_b"])
            P(f"  idle0: {w.get('n_samples')} samples, {w.get('power_w') and round(w['power_w'], 1)} W, SM {w.get('sm_mean') and round(w['sm_mean'])} MHz, "
              f"die {w.get('temp_first')}->{w.get('temp_last')} C, target {i0.get('target_c')} C")
    P("")
    P("## Cells")
    P("")
    for ln in fmt_cell_table(cells, units):
        P(ln)
    P("")
    P("## Gaps: zeros over random (randn; int8 rand_full), the kernel's rate and the sampled clock")
    P("")
    P("| unit | cap | n | format | pass | window | rate | clock | SW cap zeros / random | W zeros / random |")
    P("|---|---|---|---|---|---|---|---|---|---|")
    for g in gaps:
        def f(x, k=3):
            return "—" if x is None else f"{x:.{k}f}"
        P(f"| {g['unit']} | {g['cap']} | {g['size']} | {g['dtype']} | {g['pass']} | {g['window']} | {f(g['gap_rate'])} | "
          f"{f(g['gap_clock'])} | {f(g['sw_zeros'], 2)} / {f(g['sw_random'], 2)} | {f(g['p_zeros'], 1)} / {f(g['p_random'], 1)} |")
    P("")
    P("## Replicates (every unit and pass)")
    P("")
    agg = {}
    for g in gaps:
        agg.setdefault((g["cap"], g["size"], g["dtype"], g["window"]), []).append(g["gap_rate"])
    rep = {}
    for k, v in sorted(agg.items()):
        s = summary(v)
        rep["|".join(map(str, k))] = s
        half = s.get("t95_half")
        P(f"{k}: n {s['n']}, mean {s['mean']:.4f}, range {s['min']:.4f}-{s['max']:.4f}" + (f", t95 ±{half:.4f}" if half else ""))
    P("")
    P("## Horace's protocol (mm_weird.py's do_bench, median of 10 shuffled trials)")
    P("")
    for (u, cap, label), pr in sorted(protos.items()):
        ks = " ".join(f"{k} {v['median_tflops']:.1f} ({v['sm_mean'] and round(v['sm_mean'])} MHz, {v['p_mean_w'] and round(v['p_mean_w'])} W)"
                      for k, v in pr["kinds"].items())
        P(f"{u} {cap} {label}: zeros/randn {pr.get('zeros_over_randn') and round(pr['zeros_over_randn'], 4)}; {ks}")
    P("")
    P("## The lower cap")
    P("")
    for u, lc in lowcaps.items():
        P(f"{u}: {lc.get('brief')}")
        P(f"   set: {json.dumps(lc.get('set'))[:600]}")
        P(f"   restore: {json.dumps(lc.get('restore'))[:600]}")
    P("")
    P("## Rules")
    P("")
    for k, v in rules.items():
        P(f"{k}: {v['verdict']}")
        P("   " + json.dumps({kk: vv for kk, vv in v.items() if kk != "verdict"}, default=str)[:3000])
    P("")
    P("## Checks")
    P("")
    for name, val, ok in checks(units, cells):
        P(f"{'ok  ' if ok else 'FAIL'} {name}: {val}")
    if a.json:
        out = {"experiment": "E135", "units": {u: {"static": {k: v for k, v in U["static"].items() if not k.startswith("nvidia-smi")},
                                                    "idle0": U["idle0"] and {k: U["idle0"].get(k) for k in ("t_idle_c", "target_c")},
                                                    "done": U["done"] and {k: U["done"].get(k) for k in ("elapsed_s", "skipped", "final_restore", "error")}}
                                                for u, U in units.items()},
               "cells": {"|".join(map(str, k)): {"wait": {kk: c["rec"]["wait"].get(kk) for kk in ("T_start", "target", "reached")},
                                                 "stats": c["rec"].get("stats"), "group": c["rec"].get("group"),
                                                 "windows": c["w"]} for k, c in cells.items()},
               "gaps": gaps, "replicates": rep, "protocols": {"|".join(k): v for k, v in protos.items()},
               "lowcap": {u: {k: lc.get(k) for k in ("default_w", "min_w", "max_w", "target_w", "set", "enforced_after_set_w",
                                                       "applied", "restore")} for u, lc in lowcaps.items()},
               "rules": rules}
        with open(a.json, "w") as f:
            json.dump(out, f, indent=1, default=str)


if __name__ == "__main__":
    main()
