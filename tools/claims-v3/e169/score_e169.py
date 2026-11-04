#!/usr/bin/env python3
"""E169 (Q141(s)): the scorer. It applies REGISTRATION-A2.md's step rule (S1-S6) and Q140(q)'s B7 as registered (49575094) to E169's
reduction (reduce_e169.py), with E158's ties (D6), R0's check of C (D5), each model's level error, the formats printed if run (D4) and
the reported power reading (D12). Every constant is read from step-rule-e169.json (committed in 217c94a2) and the frozen
predictions-e169.json (e39d06da); both are checked by sha256 before anything is scored. Standard library only.

    python3 -B tools/claims-v3/e169/score_e169.py check                                  frozen inputs' sha256 (CHECK OK or refused)
    python3 -B tools/claims-v3/e169/score_e169.py <RUNDIR> [<RUNDIR> ...] [--out results.json] > score.txt

score() takes plain data (reduce_e169.reduce()'s dict), so selftest_e169.py runs it on rows it makes up.
SPDX-License-Identifier: Apache-2.0
"""
import argparse
import hashlib
import json
import math
import os
import sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
LAB = os.path.normpath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, HERE)
import reduce_e169 as RE  # noqa: E402

Q140Q = "docs/reports/data/2026-11-04-q140q-gemm-g4-stride"
FROZEN = {f"{Q140Q}/predictions-e169.json": "38ee500fa1e66107ef5c544688263b1e988fb5a675bdee05f9876df1432cf19f",
          f"{Q140Q}/stride_sm.py": "4b8b028dc09365b3a587a0808d7f13ccf22332962a9db139ff8d38f1cab8c65c",
          f"{Q140Q}/peaks_e169.py": "bf466124d12c75db3a151a87a7751fc8a142a58fbe12ee957b03c32262e5a88e",
          "tools/claims-v3/e169/step-rule-e169.json": "e76aa66b3911b681dc3b4056153efc6043f3f1b44a508700f378c159aef0e86f",
          "tools/claims-v3/e169/kit-e169.json": "28ef79aa7eb30c4e435ea564464057d5971dba0f9d5da6d52d90ffd8dccf98f0"}
MODELS = ("SM", "ISO", "STRICT")
SHAPES = ("P1", "P2", "P3", "N1", "N2", "N3")
POW2 = ("P1", "P2", "P3")
PAIRS = (("P1", "N1"), ("P2", "N2"), ("P3", "N3"))
TYPES = ("fp32", "fp16", "int8")
TIES = ("K4n7", "K4n8", "K6n5", "K6n4")
TIE_STEPS = (("K4n8", "K4n7"), ("K6n4", "K6n5"))


def sha256(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def check_frozen():
    """None if every frozen input is byte-identical to its committed form, else the list of those that are not"""
    bad = [rel for rel, h in FROZEN.items() if not os.path.isfile(os.path.join(LAB, rel)) or sha256(os.path.join(LAB, rel)) != h]
    return bad or None


def load():
    bad = check_frozen()
    if bad:
        raise SystemExit(f"refused: frozen inputs differ from their committed bytes: {bad}")
    rule = json.load(open(os.path.join(LAB, "tools/claims-v3/e169/step-rule-e169.json")))
    pred = json.load(open(os.path.join(LAB, f"{Q140Q}/predictions-e169.json")))
    kit = json.load(open(os.path.join(LAB, "tools/claims-v3/e169/kit-e169.json")))
    return rule, pred, kit


def r(x, n=5):
    return None if x is None else round(x, n)


def rms(xs):
    xs = [x for x in xs if x is not None]
    return None if not xs else math.sqrt(sum(x * x for x in xs) / len(xs))


# ------------------------------------------------------------------ S1-S3: one pair
def pair_reading(passes, nl, P, N, t, steps, rule):
    """passes['<pass>|<shape>.<type>'] the per-pass T800 (us), nl the launch counts at >= 790 MHz; steps {model: frozen step}.
    REGISTRATION-A2.md S1-S4: the step, its 95% interval, the zone reading, and on a decisive pair its presence and size."""
    R = rule["rule"]
    band = R["band_points"] / 100.0
    sigma0 = R["sigma0_ln_step"]
    t975 = {int(k): v for k, v in R["t975"].items()}
    logs, each = [], {}
    for j in sorted({int(k.split("|")[0]) for k in passes}):
        a, b = passes.get(f"{j}|{P}.{t}"), passes.get(f"{j}|{N}.{t}")
        if a is None and b is None:
            continue
        na, nb = nl.get(f"{j}|{P}.{t}", 0), nl.get(f"{j}|{N}.{t}", 0)
        ok = a is not None and b is not None and na >= R["n_min_launches_800"] and nb >= R["n_min_launches_800"]
        each[f"pass{j}"] = {"T800_P": r(a), "T800_N": r(b), "launches_P": na, "launches_N": nb, "step": None if (a is None or b is None) else r(a / b - 1), "counted": ok}
        if ok:
            logs.append(math.log(a / b))
    n = len(logs)
    out = {"P": P, "N": N, "type": t, "n": n, "per_pass": each, "models": {m: r(steps[m]) for m in MODELS}}
    if n < R["n_min_passes"]:
        out.update({"reading": "NO READING", "why": f"{n} pass(es) counted, {R['n_min_passes']} needed", "presence": None, "size": None})
        return out
    m = sum(logs) / n
    sd = math.sqrt(sum((x - m) ** 2 for x in logs) / (n - 1))
    s_used = max(sd, sigma0)
    h = t975[n - 1] * s_used / math.sqrt(n)
    step, lo, hi = math.exp(m) - 1, math.exp(m - h) - 1, math.exp(m + h) - 1
    zones = {k: (steps[k] - band, steps[k] + band) for k in MODELS}
    inside = [k for k in MODELS if lo >= zones[k][0] and hi <= zones[k][1]]
    outside_all = all(hi < zones[k][0] or lo > zones[k][1] for k in MODELS)
    if inside:
        reading = "SUPPORTS " + ", ".join(inside)
    elif outside_all:
        order = sorted(MODELS, key=lambda k: steps[k])
        below = [k for k in order if zones[k][1] < lo]
        above = [k for k in order if zones[k][0] > hi]
        if not below:
            where = f"below every zone ({order[0]}'s lowest)"
        elif not above:
            where = f"beyond every zone (above {below[-1]}'s)"
        else:
            where = f"between {below[-1]}'s zone and {above[0]}'s"
        reading = "NONE OF THE THREE: " + where
    else:
        crossed = [k for k in MODELS if not (lo >= zones[k][0] and hi <= zones[k][1]) and not (hi < zones[k][0] or lo > zones[k][1])]
        reading = "UNRESOLVED: crosses the edge of " + ", ".join(f"{k}'s zone" for k in crossed)
    none_hi = max(steps["ISO"], steps["STRICT"]) + band
    absent = all(lo >= zones[k][0] and hi <= zones[k][1] for k in ("ISO", "STRICT"))
    presence = "PRESENT" if lo > none_hi else ("ABSENT" if absent else "UNRESOLVED")
    smz = zones["SM"]
    size = "SM" if (lo >= smz[0] and hi <= smz[1]) else ("NOT SM" if (hi < smz[0] or lo > smz[1]) else "UNRESOLVED")
    out.update({"step": r(step), "lo": r(lo), "hi": r(hi), "half_width_points": r(100 * (hi - lo) / 2, 3), "sd_ln": r(sd, 6), "sd_used": r(s_used, 6),
                "floor_used": sd < sigma0, "t": t975[n - 1], "zones": {k: [r(v[0]), r(v[1])] for k, v in zones.items()}, "reading": reading,
                "presence": presence, "size": size,
                "share_of_SM_step": None if steps["SM"] == 0 else {"share": r(step / steps["SM"], 3), "lo": r(lo / steps["SM"], 3), "hi": r(hi / steps["SM"], 3)}})
    return out


def verdict(read, decisive):
    """REGISTRATION-A2.md S4: the verdict on the L3's 8 MB index, from the decisive pairs' presence and size"""
    d = [read[k] for k in decisive]
    if any(x["reading"] == "NO READING" for x in d):
        return "NO VERDICT"
    pres = [x["presence"] for x in d]
    size = [x["size"] for x in d]
    if all(p == "PRESENT" for p in pres):
        if all(s == "SM" for s in size):
            return "INDEX STEP AS SM"
        if any(s == "NOT SM" for s in size):
            return "A STRIDE STEP SM DOES NOT SIZE"
        return "A STRIDE STEP, ITS SIZE UNRESOLVED"
    if all(p == "ABSENT" for p in pres):
        return "NO STEP"
    if sorted(pres) == ["ABSENT", "PRESENT"]:
        return "MIXED"
    return "UNRESOLVED"


# ------------------------------------------------------------------ the rest of the rules
def T8(per, s, t):
    v = per.get(f"{s}.{t}") or {}
    return v.get("T800")


def b7(per, pred, rule):
    """B7 exactly as 49575094 registered it (REGISTRATION-A2.md § B7), fp32 scored, fp16 and int8 printed"""
    B = rule["b7_as_registered"]
    S = pred["shapes"]
    out = {}
    for t in TYPES:
        pt, rs = {}, {}
        for s in SHAPES:
            m = T8(per, s, t)
            sm, iso = S[s][t]["SM"]["T800"], S[s][t]["ISO"]["T800"]
            pt[s] = {"T800": r(m), "SM": sm, "rel": None if m is None else r(m / sm - 1, 4), "ok": None if m is None else abs(m / sm - 1) <= B["point_rel"]}
            if s in POW2:
                sep = abs(sm / iso - 1) >= B["resolved_min_sm_iso_rel"]
                closer = None if m is None else abs(m - sm) < abs(m - iso)
                rs[s] = {"T800": r(m), "SM": sm, "ISO": iso, "sm_iso_rel": r(sm / iso - 1, 4), "separated": sep, "closer_to_SM": closer,
                         "resolved": None if m is None else (sep and closer)}
        measured = [v for v in pt.values() if v["ok"] is not None]
        out[t] = {"point": pt, "point_verdict": None if not measured else ("PASS" if len(measured) == len(SHAPES) and all(v["ok"] for v in measured)
                                                                         else f"FAIL ({sum(not v['ok'] for v in measured)} of {len(measured)} outside 3%"
                                                                              + ("" if len(measured) == len(SHAPES) else f"; {len(SHAPES) - len(measured)} not measured") + ")"),
                  "resolved": rs, "resolved_count": sum(1 for v in rs.values() if v["resolved"]), "resolved_of": sum(1 for v in rs.values() if v["resolved"] is not None),
                  "scored": t == "fp32"}
    return out


def levels(per, pred):
    """each frozen model's level error, measured / predicted - 1, per shape, and its rms over the six (per format)"""
    S = pred["shapes"]
    out = {}
    for t in TYPES:
        rows = {s: {m: None if T8(per, s, t) is None else r(T8(per, s, t) / S[s][t][m]["T800"] - 1, 4) for m in MODELS} for s in SHAPES}
        out[t] = {"per_shape": rows, "rms": {m: r(rms([rows[s][m] for s in SHAPES]), 4) for m in MODELS},
                  "n": sum(1 for s in SHAPES if T8(per, s, t) is not None)}
    return out


def ties(per, passes, nl, rule):
    """D6: TIE-T (each tie's pooled T800 within 2% of E158's) and TIE-S (each committed step within 2 points of E158's)"""
    E = rule["ties_e158"]
    tt, ts = {}, {}
    for s in TIES:
        m = T8(per, s, "fp32")
        ref = E["T800"][s]
        tt[s] = {"T800": r(m), "e158": ref, "rel": None if m is None else r(m / ref - 1, 4), "ok": None if m is None else abs(m / ref - 1) <= E["t800_rel_bar"]}
    for a, b in TIE_STEPS:
        logs = []
        for j in sorted({int(k.split("|")[0]) for k in passes}):
            x, y = passes.get(f"{j}|{a}.fp32"), passes.get(f"{j}|{b}.fp32")
            if x is not None and y is not None and nl.get(f"{j}|{a}.fp32", 0) >= rule["rule"]["n_min_launches_800"] and nl.get(f"{j}|{b}.fp32", 0) >= rule["rule"]["n_min_launches_800"]:
                logs.append(math.log(x / y))
        ref = E["steps"][f"{a}/{b}"]
        st = None if not logs else math.exp(sum(logs) / len(logs)) - 1
        ts[f"{a}/{b}"] = {"step": r(st), "e158": ref, "passes": len(logs), "diff_points": None if st is None else r(100 * (st - ref), 3),
                          "ok": None if st is None else abs(st - ref) <= E["step_bar_points"] / 100.0}
    oks = [v["ok"] for v in list(tt.values()) + list(ts.values())]
    v = "NOT RUN" if all(o is None for o in oks) else ("TIED" if all(o is True for o in oks) else
                                                       "NOT TIED (" + ", ".join(k for k, x in list(tt.items()) + list(ts.items()) if x["ok"] is not True) + ")")
    return {"t800": tt, "steps": ts, "verdict": v}


def r0(red):
    """D5 / S6: every session run holds at least one check of C, and every check is exact or approx"""
    bad = []
    for x in red.get("run_checks", []):
        cs = [c for c in (x.get("checks") or []) if c is not None]
        if not cs:
            bad.append(f"{x.get('cell')} ({x.get('block')}): no check")
        elif not all(c in ("exact", "approx") for c in cs):
            bad.append(f"{x.get('cell')} ({x.get('block')}): {sorted(set(cs))}")
    n = len(red.get("run_checks", []))
    return {"runs": n, "checks": red.get("checks"), "bad": bad, "verdict": "FAIL" if (bad or not n) else "PASS"}


def power(red, rule, kit):
    """D12, reported: each shape's first-second board at 800 MHz against P0, P0 + beta delta, and P0 + beta delta + k_D (T_start - T_ref)"""
    W = rule["power_reported"]
    out = {}
    for t in TYPES:
        rows = {}
        for s in SHAPES:
            c = (red.get("cells") or {}).get(f"{s}-{t}-zeros")
            if not c:
                continue
            p8 = [x for x in (c.get("burst_p800_w_runs") or []) if x is not None]
            ds = [x for x in (c.get("burst_die_start") or []) if x is not None]
            if not p8:
                continue
            P0 = W["P0_800_fp32_zeros_w"][s] if t == "fp32" else kit["cells"][f"{s}-{t}-zeros"]["P0_w"]["800"]
            z = P0 + W["beta"] * W["delta_fallback_w"][t]
            m8 = sum(p8) / len(p8)
            Ts = None if not ds else sum(ds) / len(ds)
            rows[s] = {"p800_w": r(m8, 3), "n": len(p8), "die_start_c": r(Ts, 2), "P0": P0, "err_P0": r(m8 - P0, 3), "err_TZ": r(m8 - z, 3),
                       "err_TZ_TD": None if Ts is None else r(m8 - z - W["k_D"] * (Ts - W["T_ref_c"]), 3)}
        if rows:
            out[t] = {"rows": rows, "rms": {k: r(rms([v[k] for v in rows.values()]), 3) for k in ("err_P0", "err_TZ", "err_TZ_TD")},
                      "mean": {k: r(sum(v[k] for v in rows.values() if v[k] is not None) / max(1, sum(1 for v in rows.values() if v[k] is not None)), 3)
                               for k in ("err_P0", "err_TZ", "err_TZ_TD")}}
    return out


def score(red, rule, pred, kit):
    passes, nl, per = red["t800_by_pass_raw"], red["launches_800_by_pass"], red["per_shape"]
    R = rule["rule"]
    res = {"R0": r0(red)}
    steps, fmts = {}, {}
    for P, N in PAIRS:
        key = f"{P}/{N}"
        h = rule["hypotheses"][key]
        steps[key] = pair_reading(passes, nl, P, N, "fp32", h["fp32"]["steps"], rule)
        steps[key]["decisive"] = key in R["decisive_pairs"]
        a, b = T8(per, P, "fp32"), T8(per, N, "fp32")
        steps[key]["pooled_ratio_step"] = None if a is None or b is None else r(a / b - 1)
        steps[key]["arms"] = {m: h["fp32"]["steps"][m] for m in ("ALIGNED", "A_STRICT")}
        for t in ("fp16", "int8"):
            pt = {}
            for j in sorted({int(k.split("|")[0]) for k in passes}):
                a, b = passes.get(f"{j}|{P}.{t}"), passes.get(f"{j}|{N}.{t}")
                if a is not None and b is not None:
                    pt[f"pass{j}"] = r(a / b - 1)
            if pt:
                fm = h[t]["steps"]
                v = list(pt.values())
                mean_step = sum(v) / len(v)
                fmts[f"{key}.{t}"] = {"steps_by_pass": pt, "mean_step": r(mean_step), "models": {m: fm[m] for m in MODELS},
                                      "nearest_model": min(MODELS, key=lambda m: abs(fm[m] - mean_step)), "scored": False}
    res["steps"] = steps
    res["verdict"] = verdict(steps, R["decisive_pairs"])
    res["formats_printed"] = fmts
    res["B7"] = b7(per, pred, rule)
    res["levels"] = levels(per, pred)
    res["ties"] = ties(per, passes, nl, rule)
    res["power_reported"] = power(red, rule, kit)
    lab = []
    if res["R0"]["verdict"] != "PASS":
        lab.append("R0 FAIL")
    if res["ties"]["verdict"].startswith("NOT TIED"):
        lab.append("session not tied to E158")
    if red.get("dry"):
        lab.append("DRY (the toy card: not a reading)")
    res["labels"] = lab
    res["gates_not_reached"] = [g for g in red.get("gates", []) if g.get("gate_mode") == "cool" and g.get("gate_reached") is False]
    return res


def report(res, red):
    L = []
    p = L.append
    lab = f" [{'; '.join(res['labels'])}]" if res["labels"] else ""
    p(f"E169: {red['n_runs']} runs in {red['sessions']}; refused by the admission rule: {len(red['skipped'])}; config after every run {red['config_after']}; "
      f"peaks {red['peaks']}; cool gates not reached: {len(res['gates_not_reached'])}{lab}")
    p(f"R0 the check of C: {res['R0']['verdict']} ({res['R0']['runs']} runs; results {res['R0']['checks']}){'; ' + '; '.join(res['R0']['bad']) if res['R0']['bad'] else ''}")
    p(f"\nTHE STEP RULE (REGISTRATION-A2.md S1-S4), fp32: T800(P) / T800(N) - 1, 95% interval from the passes (floor sigma0 0.336%), zones +-3.0 points{lab}")
    for k, v in res["steps"].items():
        tag = "decisive" if v["decisive"] else "reported, not counted"
        if v["reading"] == "NO READING":
            p(f"  {k} ({tag}): NO READING ({v['why']})")
            continue
        m = v["models"]
        p(f"  {k} ({tag}): {100 * v['step']:+.2f}% [{100 * v['lo']:+.2f}, {100 * v['hi']:+.2f}] over {v['n']} passes (sd {100 * v['sd_ln']:.3f}%{', the floor used' if v['floor_used'] else ''}); "
          f"SM {100 * m['SM']:+.2f}  ISO {100 * m['ISO']:+.2f}  STRICT {100 * m['STRICT']:+.2f} -> {v['reading']}"
          + (f"; presence {v['presence']}, size {v['size']}" if v["decisive"] else "")
          + (f"; share of SM's step {v['share_of_SM_step']['share']:.2f} [{v['share_of_SM_step']['lo']:.2f}, {v['share_of_SM_step']['hi']:.2f}]" if v.get("share_of_SM_step") else ""))
        p("      per pass: " + ", ".join(f"{j} {100 * x['step']:+.2f}%{'' if x['counted'] else ' (not counted)'}" for j, x in v["per_pass"].items() if x["step"] is not None)
          + ("" if v.get("pooled_ratio_step") is None else f"; pooled T800 ratio {100 * v['pooled_ratio_step']:+.2f}%")
          + "; arms (B3, reported) " + ", ".join(f"{m} {100 * x:+.2f}%" for m, x in v["arms"].items()))
    p(f"VERDICT on the L3's 8 MB index (P1/N1 and P3/N3): {res['verdict']}{lab}")
    if res["formats_printed"]:
        p("formats, printed if run (one pass each, no reading): " + "; ".join(f"{k} {100 * v['mean_step']:+.2f}% (SM {100 * v['models']['SM']:+.2f}, ISO {100 * v['models']['ISO']:+.2f}, "
                                                                            f"STRICT {100 * v['models']['STRICT']:+.2f}; nearest {v['nearest_model']})" for k, v in res["formats_printed"].items()))
    p("\nB7 AS REGISTERED (49575094): SM's frozen T800 within 3% on every shape; resolved on P1-P3 (|SM - ISO| / ISO >= 3% and the measured T800 closer to SM)")
    for t, v in res["B7"].items():
        if v["point_verdict"] is None:
            continue
        p(f"  {t}{'' if v['scored'] else ' (printed)'}: point {v['point_verdict']}: " + ", ".join(f"{s} {100 * x['rel']:+.1f}%" for s, x in v["point"].items() if x["rel"] is not None)
          + f"; resolved {v['resolved_count']} of {v['resolved_of']}: " + ", ".join(f"{s} {'yes' if x['resolved'] else 'no'}" for s, x in v["resolved"].items() if x["resolved"] is not None))
    p("levels, measured / frozen - 1 (rms over the measured shapes): " + "; ".join(f"{t}: " + ", ".join(f"{m} {100 * x:.1f}%" for m, x in v["rms"].items() if x is not None)
                                                                                 for t, v in res["levels"].items() if v["n"]))
    tt = res["ties"]
    p(f"\nTIES to E158 (D6): {tt['verdict']}; T800 " + ", ".join(f"{s} {100 * x['rel']:+.2f}%" for s, x in tt["t800"].items() if x["rel"] is not None)
      + "; steps " + ", ".join(f"{k} {100 * x['step']:+.2f}% (E158 {100 * x['e158']:+.2f}%, {x['diff_points']:+.2f} points, {x['passes']} passes)" for k, x in tt["steps"].items() if x["step"] is not None))
    for t, v in res["power_reported"].items():
        p(f"POWER, reported (D12), {t}: p800 - P0 rms {v['rms']['err_P0']} W (mean {v['mean']['err_P0']:+}); - (P0 + beta delta) {v['rms']['err_TZ']} W ({v['mean']['err_TZ']:+}); "
          f"- (P0 + beta delta + 0.47 (T_start - T_ref)) {v['rms']['err_TZ_TD']} W ({v['mean']['err_TZ_TD']:+}); n {len(v['rows'])} shapes")
    return "\n".join(L)


def main():
    if len(sys.argv) > 1 and sys.argv[1] == "check":
        bad = check_frozen()
        print("CHECK OK (%d files)" % len(FROZEN) if not bad else f"CHECK FAILED: {bad}")
        return 0 if not bad else 1
    ap = argparse.ArgumentParser()
    ap.add_argument("rundirs", nargs="+")
    ap.add_argument("--out")
    a = ap.parse_args()
    rule, pred, kit = load()
    red = RE.reduce(a.rundirs, kit)
    res = score(red, rule, pred, kit)
    if a.out:
        keep = {k: v for k, v in red.items() if k not in ("runs", "t800_by_pass_raw")}
        json.dump({"experiment": "E169", "request": "Q141(s)'s kit; scored by score_e169.py", "reduction": keep, "scores": res}, open(a.out, "w"), indent=1, default=lambda o: None)
    print(report(res, red))
    return 0


if __name__ == "__main__":
    sys.exit(main())
