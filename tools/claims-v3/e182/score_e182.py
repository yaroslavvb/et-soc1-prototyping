#!/usr/bin/env python3
"""E182 (Q153, the kit): the scorer for E182.md section 5's rules, on one session's reductions. Nothing is fitted or tuned here. The
forecasts are forecast-e182.json's, the lines and seeds power-e182.json's and plan-e182.json's, the statistics e182_stats.py's (frozen in
58b88850; every one checked against the registration's hash list first).

  score   python3 -B score_e182.py score --reduction <primary e182.json> --runs-csv <primary runs.csv> --trains <trains-e182.json>
              --raw <raw copy> --ccheck <ccheck --out json> [--arm name=<reduction json>,<runs csv> ...] [--since <epoch s>]
              [--json scored.json] [--md results.md] [--skip-c-gate]

Order, enforced: (1) the frozen inputs (exit 9); (2) every session that must carry a C log has a finished check (ccsessions_e182; exit 4,
nothing written; --skip-c-gate exists for the self-test only); (3) E182-C: per kind, every launch of the kinds passes and of the trains
judged PASS (by t_start_ms and t_end_ms against the check of C's verdicts); a kind not all PASS leaves every scored set, and a train with
a launch not PASS is NOT SCORED; (4) the session's float scale s, M10's term a, as E178's scorer reads it (score_e178.session_scale,
imported unchanged: predict_pool8's scale over the reduction's fp32.randn and fp16.randn); int8 s = 1; (5) the scored lines: P, P + ACC
and E at s and the measured rate (each kind's in the kinds passes; a pair's mean for a train; the frozen rate when a kind has none);
(6) the rules; (7) the readings reported beside, never a verdict.

THE STATISTICS: E182.md sections 5.1-5.3 and e182_stats.py. Where the text leaves a choice (stated in KIT.md before any datum):
  E182-W-int8's P line   P's own OLS slope over the int8 kinds scored (7.043 fJ at all 20, power-e182.json's line);
  E182-R-int8's line     0.4421 at 20 kinds (power-e182.json rho_crit_int8_n20); at fewer, the 97.5% point of rho over 20,000 shuffles of
                         the measured D, random.Random(18205); 4 or fewer kinds NOT SCORED;
  E182-TR-H              the int8 trains' units' pooled residual sd (each unit minus its train's mean, df the units less the trains) and
                         the trains' median process period; n units in T minutes = T x 60 / (2 x the period);
  the arms               each reduction arm (E178's seven) reads E182-W-int8, E182-R-int8 and every kind's level, reported only.
Exit 0 when scored.json is written, 4 (no finished check of C), 9 (a frozen input differs). /usr/bin/python3 (3.9, numpy for the scale).
SPDX-License-Identifier: Apache-2.0
"""
import argparse
import csv
import gzip
import hashlib
import json
import math
import os
import random
import statistics
import sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
TOP = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, HERE)
import e182_stats as S  # noqa: E402
import e182_common as E  # noqa: E402

E178D = os.path.join(TOP, "tools", "claims-v3", "e178")
FROZEN_READ = ["tools/claims-v3/e182/forecast-e182.json", "tools/claims-v3/e182/power-e182.json", "tools/claims-v3/e182/plan-e182.json",
               "tools/claims-v3/e182/kinds-e182.json", "tools/claims-v3/e182/e182_stats.py", "tools/claims-v3/e182/E182.md",
               "tools/claims-v3/e182/noise/noise-e182.json"]
E178_H = (0.021651298383282183, 0.08476234575729945)     # E178-H-int8's registered interval (E182.md section 5.2)
E178_H32 = (-0.0459, 0.1505)
E178_H_RAW = (0.04208375609693428, 0.10719282210787372)  # E178's leak-0 arm, reported beside
DELTA_AB, DELTA_F = 0.002, 0.015
MIN_KIND_PASSES = 2
EXIT_FROZEN, EXIT_NO_C = 9, 4
RULES = ["E182-C", "E182-HT", "E182-A", "E182-B", "E182-SPLIT", "E182-X", "E182-F", "E182-H32T", "E182-TR-N", "E182-TR-H",
         "E182-W-int8", "E182-R-int8"]


class Refuse(Exception):
    def __init__(self, code, msg):
        super().__init__(msg)
        self.code = code


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def frozen_check():
    e = E.check_frozen()
    want = {}
    for line in open(os.path.join(TOP, "tools/claims-v3/e182/SHA256SUMS-e182-registration")):
        if line.strip():
            h, q = line.split(None, 1)
            want[q.strip().lstrip("*")] = h
    bad = [e] if e else []
    for rel in FROZEN_READ:
        have = sha(os.path.join(TOP, rel))
        if want.get(rel) != have:
            bad.append(f"{rel}: sha256 {have[:12]} is not the registered {str(want.get(rel))[:12]}")
    if bad:
        raise Refuse(EXIT_FROZEN, "a frozen input differs from the registration's hash list: " + "; ".join(bad))
    return {rel: want[rel] for rel in FROZEN_READ}


def jl(path):
    if not os.path.exists(path):
        return []
    op = gzip.open if path.endswith(".gz") else open
    with op(path, "rt") as f:
        return [json.loads(x) for x in f if x.strip().startswith("{")]


def read_csv(path):
    rows = []
    for r in csv.DictReader(open(path)):
        try:
            D = float(r["D"]) if r.get("D") not in ("", None) else None
        except ValueError:
            D = None
        if D is not None and math.isnan(D):
            D = None
        rows.append({"pass": int(r["pass"]), "segment": int(r["segment"]), "item": r["item"], "pos": int(r["pos"]), "D": D})
    return rows


# ------------------------------------------------------------------------------------------------- the check of C, per kind and train
def c_status(raw, ccheck_files, kept_passes):
    verdict = {}
    for f in ccheck_files:
        if not os.path.exists(f):
            continue
        op = gzip.open if f.endswith(".gz") else open
        with op(f, "rt") as fh:
            for v in json.load(fh)["launches"]:
                verdict[(v.get("t_start_ms"), v.get("t_end_ms"))] = v["verdict"]
    per, trains = {}, {}

    def add(item, r, where):
        s = per.setdefault(item, {"launches": 0, "PASS": 0, "missing": 0, "other": {}, "where": set()})
        s["launches"] += 1
        s["where"].add(where)
        v = verdict.get((r.get("t_start_ms"), r.get("t_end_ms")))
        if v is None:
            s["missing"] += 1
        elif v == "PASS":
            s["PASS"] += 1
        else:
            s["other"][v] = s["other"].get(v, 0) + 1
        return v
    for p in kept_passes:
        for r in jl(os.path.join(raw, "e182", f"p{p}", "runs.jsonl")):
            if r.get("item"):
                add(r["item"], r, f"p{p}")
    for b, t in sorted(E.TRAINS.items()):
        d = os.path.join(raw, "e182", f"p{b}")
        bad = 0
        n = 0
        for r in jl(os.path.join(d, "train.jsonl")):
            k = t["first"] if r.get("train_kind") == "F" else t["second"]
            v = add(k, r, f"p{b}")
            n += 1
            bad += v != "PASS"
        for sub in ("a0", "a1"):
            for r in jl(os.path.join(d, sub, "runs.jsonl")):
                if r.get("item"):
                    add(r["item"], r, f"p{b}/{sub}")
        trains[t["train"]] = {"launches": n, "not_pass": bad, "all_pass": n > 0 and bad == 0}
    for s in per.values():
        s["all_pass"] = s["launches"] > 0 and s["PASS"] == s["launches"]
        s["where"] = sorted(s["where"])
    return per, trains


# ------------------------------------------------------------------------------------------------- the kinds passes
def measured(res, kinds, passes):
    out, short = {}, []
    for k in kinds:
        vals = []
        for p in passes:
            r = res.get("per_pass", {}).get(str(p), {}).get(k)
            if r and r.get("D") is not None and not (isinstance(r["D"], float) and math.isnan(r["D"])):
                vals.append(float(r["D"]))
        if len(vals) >= MIN_KIND_PASSES:
            out[k] = {"mean": statistics.mean(vals), "sd": statistics.stdev(vals), "n": len(vals), "per_pass": vals}
        else:
            short.append(k)
    return out, short


def rates(res):
    out = {}
    for k, it in (res.get("items") or {}).items():
        r = (it.get("rate") or {}).get("mean")
        if isinstance(r, (int, float)):
            out[k] = float(r)
    return out


def couple_xs(rows, passes, a, b):
    """per kept pass: the mean over segments with both runs kept of D(a) - D(b) (E178's couple statistic), and the order term's parts"""
    out, order = {}, []
    for p in passes:
        diffs = []
        for s in (0, 1, 2):
            ra = [r for r in rows if r["pass"] == p and r["segment"] == s and r["item"] == a and r["D"] is not None]
            rb = [r for r in rows if r["pass"] == p and r["segment"] == s and r["item"] == b and r["D"] is not None]
            if ra and rb:
                diffs.append(statistics.mean(r["D"] for r in ra) - statistics.mean(r["D"] for r in rb))
                x, y = ra[0], rb[0]
                first, second = (x, y) if x["pos"] < y["pos"] else (y, x)
                order.append({"pass": p, "segment": s, "first_is_a": first is x, "d_first_minus_second": first["D"] - second["D"]})
        if diffs:
            out[p] = {"x": statistics.mean(diffs), "couples": len(diffs), "segment_diffs": diffs}
    return out, order


def slope_rule(D, flips, rate, kinds, lines):
    n = len(kinds)
    if n < 4:
        return {"verdict": "NOT SCORED", "why": f"{n} int8 kinds, fewer than 4", "n": n}
    b, se, a0 = S.ols([flips[k] for k in kinds], [D[k] for k in kinds])
    R = statistics.mean(rate[k] for k in kinds)
    hw = S.t975(n - 2) * se
    iv = {"lo": (b - hw) / R * 1e15, "hi": (b + hw) / R * 1e15}
    out = {"slope_fJ_per_flip": b / R * 1e15, "lo95_fJ": iv["lo"], "hi95_fJ": iv["hi"], "n": n, "mean_rate_per_s": R, "intercept_w": a0,
           "t": S.t975(n - 2), "kinds": kinds}
    for nm, ln in lines.items():
        out[f"size_{nm}"] = S.size_of(iv, ln)
        out[f"line_{nm}_fJ"] = ln
    out["verdict"] = out.get("size_E", "NOT SCORED")
    return out


def rho_rule(P, D, kinds, line20):
    n = len(kinds)
    if n <= 4:
        return {"verdict": "NOT SCORED", "why": f"{n} int8 kinds", "n": n}
    x, y = [P[k] for k in kinds], [D[k] for k in kinds]
    rho = S.spearman(x, y)
    if n == 20:
        crit, src = line20, "registered: power-e182.json rho_crit_int8_n20"
    else:
        rng = random.Random(18205)
        null = []
        for _ in range(20000):
            yy = list(y)
            rng.shuffle(yy)
            null.append(S.spearman(x, yy))
        null.sort()
        crit, src = null[int(0.975 * 20000)], f"the 97.5% point of 20,000 shuffles at n = {n} (random.Random(18205))"
    return {"verdict": "PASS" if rho >= crit else "FAIL", "rho": rho, "line": crit, "line_source": src, "n": n, "kinds": kinds}


# ------------------------------------------------------------------------------------------------- the trains
def train_iv(tr, name, cst):
    t = tr.get("trains", {}).get(name)
    if t is None:
        return {"n": 0, "lo": None, "hi": None, "mean": None, "se": None, "df": None, "why": "no train block"}
    if not cst.get(name, {}).get("all_pass"):
        return {"n": 0, "lo": None, "hi": None, "mean": None, "se": None, "df": None, "why": f"E182-C: {cst.get(name)}"}
    iv = dict(t["estimate"])
    if iv.get("n", 0) < S.MIN_UNITS or iv.get("lo") is None:
        return {"n": iv.get("n", 0), "lo": None, "hi": None, "mean": iv.get("mean"), "se": None, "df": None,
                "why": f"{iv.get('n', 0)} units, fewer than {S.MIN_UNITS}"}
    return iv


def word(iv, f):
    return f(iv) if iv.get("lo") is not None else "NOT SCORED"


def score(a):
    out = {"_note": "Q153 score_e182.py: E182 on aifoundry3, E182.md section 5's rules", "run": "E182", "card": "aifoundry3",
           "scorer_sha256": sha(os.path.abspath(__file__)), "frozen_inputs": frozen_check()}
    F = json.load(open(os.path.join(HERE, "forecast-e182.json")))
    PW = json.load(open(os.path.join(HERE, "power-e182.json")))
    NZ = json.load(open(os.path.join(HERE, "noise", "noise-e182.json")))
    PL = json.load(open(os.path.join(HERE, "plan-e182.json")))
    if not a.skip_c_gate:
        import ccsessions_e182 as CS  # noqa: E402
        g = CS.check("E182", a.raw, a.ccheck, a.since)
        g = json.loads(json.dumps(g).replace(TOP + os.sep, ""))
        out["c_sessions"] = {k: g[k] for k in ("sessions", "stoptest", "ccdone", "ok") if k in g}
        if not g["ok"]:
            raise Refuse(EXIT_NO_C, "a session that must carry a C log has no finished check of C (E182.md section 7); every rule reads NOT "
                                    "SCORED and nothing is written:\n  " + "\n  ".join(g.get("lines", [])))
    res = json.load(open(a.reduction)) if a.reduction and os.path.exists(a.reduction) else {}
    kept = [int(p) for p in res.get("passes", [])] if res else []
    rows = read_csv(a.runs_csv) if a.runs_csv and os.path.exists(a.runs_csv) else []
    tr = json.load(open(a.trains)) if a.trains and os.path.exists(a.trains) else {"trains": {}}
    cst, ctr = c_status(a.raw, [a.ccheck, a.ccheck + ".gz"], kept)
    names = list(E.E182_NAMES)
    cfail = sorted(k for k in names if k in cst and not cst[k]["all_pass"])
    out["c_status"] = {"kinds": {k: {q: v for q, v in cst[k].items()} for k in sorted(cst) if k in names}, "trains": ctr,
                       "kinds_not_all_pass": cfail}
    out["kept_passes"] = kept
    # (4) the scale
    s_float, scale_note = 1.0, "no kinds reduction: s = 1"
    if res and len(kept) >= 2:
        try:
            sys.path.insert(0, E178D)
            import score_e178 as SE  # noqa: E402  (session_scale only, unchanged)
            sc, _ = SE.session_scale("aifoundry3", a.reduction)
            s_float, scale_note = sc["s_float"], sc
        except Exception as ex:  # noqa: BLE001  (recorded; the int8 rules need no scale)
            scale_note = f"the scale could not be read: {ex!r}; s = 1"
    out["scale"] = {"s_float": s_float, "note": scale_note}
    rt = rates(res)
    ks = F["kinds"]
    frozen_rate = F["rate"]

    def scaled(k, fld):
        t = ks[k]["type"]
        s = s_float if t != "int8" else 1.0
        return ks[k][fld]["a3"] * s * (rt.get(k, frozen_rate[t]) / frozen_rate[t])
    lines = {k: {arm: scaled(k, fld) for arm, fld in (("P", "P_w"), ("PACC", "PACC_w"), ("E", "E_w"))} for k in names}
    pr = F["pairs"]

    def dline(pid, arm):
        return lines[pr[pid]["first"]][arm] - lines[pr[pid]["second"]][arm]
    rules, rep = {}, {}
    rules["E182-C"] = {"verdict": "PASS" if not cfail and all(v["all_pass"] for v in ctr.values() if v["launches"]) else "FAIL",
                       "kinds_not_all_pass": cfail, "trains_not_all_pass": sorted(k for k, v in ctr.items() if v["launches"] and not v["all_pass"])}
    # (6) the trains
    iv = {pid: train_iv(tr, pid, ctr) for pid in ("T1", "T2", "T3", "T4", "T5", "T6")}
    out["trains"] = {pid: {k: v for k, v in iv[pid].items()} for pid in iv}

    def pair_rule(pid, ref):
        i = iv[pid]
        r = {"estimate": i, "lines_w": {arm: dline(pid, arm) for arm in ("P", "PACC", "E")}}
        if i.get("lo") is None:
            r.update(verdict="NOT SCORED", why=i.get("why"))
            return r
        r.update(verdict=S.sign_of(i), sign=S.sign_of(i), size_P=S.size_of(i, r["lines_w"]["P"]), size_PACC=S.size_of(i, r["lines_w"]["PACC"]),
                 size_E=S.size_of(i, r["lines_w"]["E"]), repeat=S.agrees(i, *ref))
        return r
    rules["E182-HT"] = pair_rule("T1", E178_H)
    rep["E182-HT beside: the train against E178-H-int8's raw-footing interval"] = S.agrees(iv["T1"], *E178_H_RAW) if iv["T1"].get("lo") is not None else "NOT SCORED"
    rules["E182-H32T"] = pair_rule("T6", E178_H32)
    A = S.combine(iv["T3"], iv["T2"], 1, -1, 14) if iv["T3"].get("lo") is not None and iv["T2"].get("lo") is not None else {"lo": None}
    B = S.combine(iv["T3"], iv["T2"], 1, 1, 14) if iv["T3"].get("lo") is not None and iv["T2"].get("lo") is not None else {"lo": None}
    hb = {arm: (lines["int8.neg_ones"][arm] - lines["int8.ones"][arm] + lines["int8.e182_a1_bm1"][arm] - lines["int8.e182_am1_b1"][arm]) / 14
          for arm in ("P", "PACC", "E")}
    wa = S.null_of(A, DELTA_AB) if A.get("lo") is not None else "NOT SCORED"
    wb = S.null_of(B, DELTA_AB) if B.get("lo") is not None else "NOT SCORED"
    rules["E182-A"] = {"verdict": wa, "beta_A": A, "band_w_per_bit": DELTA_AB, "forecast_every_arm": 0.0}
    rules["E182-B"] = {"verdict": wb, "beta_B": B, "band_w_per_bit": DELTA_AB, "lines_w_per_bit": hb,
                       **({"size_P": S.size_of(B, hb["P"]), "size_PACC": S.size_of(B, hb["PACC"]), "size_E": S.size_of(B, hb["E"])}
                          if B.get("lo") is not None else {})}
    rules["E182-SPLIT"] = {"verdict": S.split_of(wa, wb) if "NOT SCORED" not in (wa, wb) else "NOT SCORED", "forecast": "B-ONLY",
                           "ratio_beta_A_over_beta_B": (A["mean"] / B["mean"]) if A.get("mean") and B.get("mean") else None}
    if iv["T4"].get("lo") is not None and iv["T2"].get("lo") is not None:
        cc = S.combine(iv["T4"], iv["T2"], 7, -1, 7)
        rules["E182-X"] = {"verdict": "CONSISTENT" if cc["lo"] <= 0 <= cc["hi"] else "INCONSISTENT", "t4_minus_t2_over_7": cc,
                           "t4_sign": S.sign_of(iv["T4"]), "t4": iv["T4"], "lines_t4_w": {arm: dline("T4", arm) for arm in ("P", "PACC", "E")}}
    else:
        rules["E182-X"] = {"verdict": "NOT SCORED", "why": "T4 or T2 not scored"}
    rules["E182-F"] = ({"verdict": S.null_of(iv["T5"], DELTA_F), "estimate": iv["T5"], "band_w": DELTA_F, "forecast_every_arm": 0.0}
                       if iv["T5"].get("lo") is not None else {"verdict": "NOT SCORED", "why": iv["T5"].get("why")})
    # E182-TR
    sig = {"int8": NZ["sigma_q_w"]["int8"], "fp32": NZ["sigma_q_w"]["float"]}
    ratios, by_t = {}, {}
    for pid, t in tr.get("trains", {}).items():
        if not ctr.get(pid, {}).get("all_pass"):
            continue
        rp = t["reported"]
        if rp.get("quad_residual_df"):
            ss, dfn = by_t.get(t["type"], (0.0, 0))
            by_t[t["type"]] = (ss + rp["quad_residual_sd"] ** 2 * rp["quad_residual_df"], dfn + rp["quad_residual_df"])
    for ty, (ss, dfn) in by_t.items():
        ratios[ty] = {"pooled_sd_w": math.sqrt(ss / dfn), "df": dfn, "forecast_sd_w": sig[ty], "ratio": math.sqrt(ss / dfn) / sig[ty]}
    if ratios:
        r = max(v["ratio"] for v in ratios.values())
        rules["E182-TR-N"] = {"verdict": "AS FORECAST" if r <= 1.25 else ("WORSE" if r <= 2.0 else "FAILS"), "largest_ratio": r, "by_type": ratios}
    else:
        rules["E182-TR-N"] = {"verdict": "NOT SCORED", "why": "no train scored"}
    us, nt, per = [], 0, []
    for pid in ("T1", "T2", "T3", "T4"):
        t = tr.get("trains", {}).get(pid)
        if t and ctr.get(pid, {}).get("all_pass") and len(t["units"]) >= S.MIN_UNITS:
            m = statistics.mean(t["units"])
            us += [x - m for x in t["units"]]
            nt += 1
            if t["reported"].get("process_period_s_median"):
                per.append(t["reported"]["process_period_s_median"])
    if nt and per and len(us) - nt > 1:
        su = math.sqrt(sum(x * x for x in us) / (len(us) - nt))
        period = statistics.median(per)
        hw = {}
        for T in (30, 40):
            nu = T * 60 / (2 * period)
            hw[T] = S.t975(nu - 1) * su / math.sqrt(nu)
        v = "BETTER" if hw[30] < 0.003 and hw[40] < 0.003 else ("HOLDS" if hw[30] <= 0.006 else "FAILS")
        rules["E182-TR-H"] = {"verdict": v, "units_sd_w": su, "process_period_s": period, "halfwidth_30_min_w": hw[30], "halfwidth_40_min_w": hw[40],
                              "trains": nt}
    else:
        rules["E182-TR-H"] = {"verdict": "NOT SCORED", "why": "no int8 train scored"}
    # (6) the kinds passes
    i8 = [k for k in names if ks[k]["type"] == "int8"]
    if len(kept) >= 2:
        meas, short = measured(res, names, kept)
        ok8 = [k for k in i8 if k in meas and k not in cfail]
        Dm = {k: meas[k]["mean"] for k in meas}
        flips = {k: ks[k]["flips_i"]["launch_mean"]["total"] for k in names}
        rate8 = {k: rt.get(k, frozen_rate["int8"]) for k in i8}
        P8 = {k: lines[k]["P"] for k in i8}
        pline = S.ols([flips[k] for k in ok8], [P8[k] for k in ok8])[0] / statistics.mean(rate8[k] for k in ok8) * 1e15 if len(ok8) >= 4 else None
        rules["E182-W-int8"] = slope_rule(Dm, flips, rate8, ok8, {"E": F["arm_E_lines"]["int8"]["price_fJ_per_flip"], "P": pline})
        rules["E182-R-int8"] = rho_rule(P8, Dm, ok8, PW["rho_crit_int8_n20"])
        rep["short_kinds"] = short
        rep["kinds"] = {k: {"D_w": meas[k]["mean"], "sd_w": meas[k]["sd"], "n": meas[k]["n"], "P_w": lines[k]["P"], "PACC_w": lines[k]["PACC"],
                            "E_w": lines[k]["E"], "D_minus_P_w": meas[k]["mean"] - lines[k]["P"], "c_kept": k not in cfail,
                            "rate_per_s": rt.get(k)} for k in meas if k in names}
        # E182-Q, the quartet fit per pass
        sys.path.insert(0, HERE)
        import forecast_e182 as FE  # noqa: E402  (quartet_design and solve)
        qk = [k for k in F["quartet_keys"] if k not in cfail]
        fa, fb = [], []
        if len(qk) == len(F["quartet_keys"]):
            X, _ = FE.quartet_design([ks[k] for k in qk])
            for p in kept:
                y = [res["per_pass"].get(str(p), {}).get(k, {}).get("D") for k in qk]
                if all(isinstance(v, (int, float)) for v in y):
                    co = FE.solve(X, y)
                    fa.append(co[-2])
                    fb.append(co[-1])
        rep["E182-Q"] = {"beta_A": S.interval(fa), "beta_B": S.interval(fb), "passes": len(fa)}
        # E182-K and the order term, per pair
        rep["E182-K"], rep["order_term"] = {}, {}
        for pid, f, s in PL["pairs"]:
            xs, order = couple_xs(rows, kept, f, s)
            v = [xs[p]["x"] for p in sorted(xs)]
            kv = S.interval(v) if len(v) >= 2 else {"n": len(v)}
            ti = iv[pid]
            diff = (S.combine(ti, kv, 1, -1, 1) if ti.get("lo") is not None and kv.get("se") else None)
            rep["E182-K"][pid] = {"kinds_pass": kv, "train": ti, "train_minus_kinds_pass": diff}
            if order:
                d = [o["d_first_minus_second"] for o in order]
                rep["order_term"][pid] = {"tau": S.interval(d), "couples": len(d)}
    else:
        for r in ("E182-W-int8", "E182-R-int8"):
            rules[r] = {"verdict": "NOT SCORED", "why": f"{len(kept)} kept kinds passes, fewer than 2"}
    for name, spec in (a.arm or {}).items():
        try:
            ra = json.load(open(spec[0]))
            kp = [int(p) for p in ra.get("passes", [])]
            ma, _ = measured(ra, names, kp)
            ok8 = [k for k in i8 if k in ma and k not in cfail]
            if len(kp) < 2:
                rep.setdefault("arms", {})[name] = {"kept_passes": kp, "verdicts": "NOT SCORED (fewer than 2 kept passes)"}
                continue
            P8a = {k: lines[k]["P"] for k in i8}
            wl = {"E": F["arm_E_lines"]["int8"]["price_fJ_per_flip"]}
            if len(ok8) >= 4:
                wl["P"] = S.ols([ks[k]["flips_i"]["launch_mean"]["total"] for k in ok8], [P8a[k] for k in ok8])[0] / statistics.mean(
                    rt.get(k, frozen_rate["int8"]) for k in ok8) * 1e15
            rep.setdefault("arms", {})[name] = {
                "kept_passes": kp,
                "E182-W-int8": slope_rule({k: ma[k]["mean"] for k in ma}, {k: ks[k]["flips_i"]["launch_mean"]["total"] for k in names},
                                          {k: rt.get(k, frozen_rate["int8"]) for k in i8}, ok8, wl),
                "E182-R-int8": rho_rule(P8a, {k: ma[k]["mean"] for k in ma}, ok8, PW["rho_crit_int8_n20"]),
                "levels": {k: {"D_w": ma[k]["mean"], "n": ma[k]["n"], "D_minus_P_w": ma[k]["mean"] - lines[k]["P"]} for k in ma if k in names}}
        except (OSError, ValueError, KeyError) as ex:
            rep.setdefault("arms", {})[name] = f"unreadable: {type(ex).__name__}"
    rep["trains"] = {pid: t.get("reported") for pid, t in tr.get("trains", {}).items()}
    out["rules"] = rules
    out["verdicts"] = {r: rules[r]["verdict"] for r in RULES if r in rules}
    out["reported"] = rep
    out["plan"] = os.environ.get("E182_PLAN_READ", "as collected")
    return out


def md(out):
    L = ["# E182 scored (score_e182.py)", "", "| rule | verdict | reading |", "|---|---|---|"]
    for r in RULES:
        v = out["rules"].get(r, {})
        if r in ("E182-HT", "E182-H32T"):
            e = v.get("estimate", {})
            rd = (f"{e.get('mean'):+.4f} [{e.get('lo'):+.4f}, {e.get('hi'):+.4f}] W; SIZE P {v.get('size_P')}, P+ACC {v.get('size_PACC')}, "
                  f"E {v.get('size_E')}; REPEAT {v.get('repeat')}") if e.get("lo") is not None else v.get("why", "")
        elif r in ("E182-A", "E182-B"):
            b = v.get("beta_A" if r == "E182-A" else "beta_B", {})
            rd = (f"{b.get('mean'):+.5f} [{b.get('lo'):+.5f}, {b.get('hi'):+.5f}] W a bit a byte" + (
                  f"; SIZE P {v.get('size_P')}, E {v.get('size_E')}" if r == "E182-B" else "")) if b.get("lo") is not None else ""
        elif r == "E182-F":
            e = v.get("estimate", {})
            rd = f"{e.get('mean'):+.4f} [{e.get('lo'):+.4f}, {e.get('hi'):+.4f}] W" if e.get("lo") is not None else v.get("why", "")
        elif r == "E182-W-int8":
            rd = (f"{v.get('slope_fJ_per_flip'):.3f} fJ a flip [{v.get('lo95_fJ'):.3f}, {v.get('hi95_fJ'):.3f}]; against E {v.get('size_E')}, "
                  f"against P {v.get('size_P')}") if "slope_fJ_per_flip" in v else v.get("why", "")
        elif r == "E182-R-int8":
            rd = f"rho {v.get('rho'):+.3f} against {v.get('line'):.4f}" if "rho" in v else v.get("why", "")
        elif r == "E182-TR-N":
            rd = f"largest ratio {v.get('largest_ratio'):.3f}" if "largest_ratio" in v else v.get("why", "")
        elif r == "E182-TR-H":
            rd = (f"projected 30 / 40 min half-widths {v.get('halfwidth_30_min_w'):.4f} / {v.get('halfwidth_40_min_w'):.4f} W"
                  if "halfwidth_30_min_w" in v else v.get("why", ""))
        elif r == "E182-X":
            c = v.get("t4_minus_t2_over_7", {})
            rd = f"T4 - T2/7 {c.get('mean'):+.4f} [{c.get('lo'):+.4f}, {c.get('hi'):+.4f}] W; T4 {v.get('t4_sign')}" if c.get("lo") is not None else v.get("why", "")
        elif r == "E182-SPLIT":
            rd = f"forecast B-ONLY; beta_A / beta_B {v.get('ratio_beta_A_over_beta_B')}"
        else:
            rd = f"kinds not all PASS {v.get('kinds_not_all_pass')}, trains {v.get('trains_not_all_pass')}"
        L.append(f"| {r} | {v.get('verdict', 'NOT SCORED')} | {rd} |")
    return "\n".join(L) + "\n"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=("score",))
    ap.add_argument("--reduction")
    ap.add_argument("--runs-csv")
    ap.add_argument("--trains")
    ap.add_argument("--raw", required=True)
    ap.add_argument("--ccheck", required=True)
    ap.add_argument("--arm", action="append", default=[])
    ap.add_argument("--since", type=float)
    ap.add_argument("--json")
    ap.add_argument("--md")
    ap.add_argument("--skip-c-gate", action="store_true")
    a = ap.parse_args()
    a.arm = {x.split("=", 1)[0]: x.split("=", 1)[1].split(",") for x in a.arm}
    try:
        out = score(a)
    except Refuse as e:
        print(f"REFUSED ({e.code}): {e}", file=sys.stderr)
        sys.exit(e.code)
    js = json.dumps(out, indent=1, sort_keys=True, default=lambda o: sorted(o) if isinstance(o, set) else None) + "\n"
    if a.json:
        open(a.json, "w").write(js)
    if a.md:
        open(a.md, "w").write(md(out))
    print(json.dumps(out["verdicts"], indent=1))


if __name__ == "__main__":
    main()
