#!/usr/bin/env python3
"""Score E118 against its frozen predictions (predictions.json), and nothing else.

    python3 tools/claims-v3/e118/score_e118.py --data <data dir> --gen <hl-gen dir> --e60pred <E60 predictions.json>
            --pred tools/claims-v3/e118/predictions.json --out <verdicts.json>

<data dir> holds aifoundry1-c0/e118/p<n> (the 600 MHz passes), aifoundry1-c0/e118c/p<n> (the 800 MHz control),
aifoundry1-c0/e118-smoke/p900 (the pinned smoke), aifoundry1-c0/e118back-smoke/p901 (the return burst), and the session
directory session/ (gov.jsonl, ring-*.bin). It runs reduce_e118.py itself (both halves at the registered --leak auto,
and the 600 MHz half at V1m's slopes on the passes kept at both) and writes results600.json / runs600.csv /
resultsC.json / runsC.csv / matched600-*.json beside <out>.

Estimators are E72's (score_e72.py): the h2 -> h8 secant with E60's formula
    lq_h2_h8 = (d_p80[lq_h8] - d_p80[lq_h2]) / ((32768 - 8192) * rate[lq_h8])
from the pass-averaged items (the published number) and per pass (its scatter gives the SE: the unit of replication
is the pass). G1's and G3's log halves come from the SP ring dumps (tools/claims-v3/dv2/sptrace_events.py), by
difference between consecutive dumps; a ring that wrapped between them leaves the half UNMEASURED, never PASS.
"""
import argparse
import csv
import glob
import gzip
import importlib.util
import json
import math
import os
import subprocess
import sys
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
CARD = os.environ.get("E118_CARD", "aifoundry1-c0")   # E118_CARD only for the self-check on E72's data
H2, H8 = 8192, 32768


def mean_se(v):
    v = [x for x in v if x is not None]
    if not v:
        return None, None, 0
    m = sum(v) / len(v)
    if len(v) < 2:
        return m, None, 1
    return m, math.sqrt(sum((x - m) ** 2 for x in v) / (len(v) - 1)) / math.sqrt(len(v)), len(v)


def inband(x, b):
    return x is not None and b[0] <= x <= b[1]


def verdict(x, band, alt=None):
    if x is None:
        return "UNMEASURED"
    if inband(x, band):
        return "INCONCLUSIVE" if alt and inband(x, alt) else "PASS"
    return "FAIL (the alternative's band)" if alt and inband(x, alt) else "FAIL"


def band(x, f=0.10):
    return [x * (1 - f), x * (1 + f)]


def reduce(dirs, leak, mode, out, csvp, gen, e60pred):
    cmd = [sys.executable, os.path.join(HERE, "reduce_e118.py"), *dirs, "--gen", gen, "--pred", e60pred,
           "--out", out, "--csv", csvp, "--leak", str(leak), mode]
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode != 0:
        raise SystemExit(f"reduce failed ({mode} {leak}): {r.stderr[-600:]}")
    return json.load(open(out))


def per_pass(csvp, set_aside):
    out = defaultdict(lambda: defaultdict(list))
    for r in csv.DictReader(open(csvp)):
        if r["card"] != CARD or r["fail"] not in ("[]", "") or int(r["pass"]) in set_aside:
            continue
        out[int(r["pass"])][r["item"]].append({"p80": float(r["p80"]), "rate": float(r["rate"]),
                                               "rail": float(r["rail"]) if r["rail"] not in ("", "None") else None})
    val = {}
    for p, items in out.items():
        val[p] = {it: {k: mean_se([x[k] for x in rr])[0] for k in ("p80", "rate", "rail")} for it, rr in items.items()}
    return val


def secant(items, key="d_p80"):
    a, b = items.get("lq_h8"), items.get("lq_h2")
    if not a or not b or a.get(key) is None or b.get(key) is None or not a.get("rate"):
        return None
    return (a[key] - b[key]) / ((H8 - H2) * a["rate"]) * 1e15


def secants(res, csvp):
    """(from pass-averaged items, per-pass mean, SE, n, rail per-pass mean, rail SE) of the h2 -> h8 secant."""
    C, g = res["cards"][CARD], res["gates"][CARD]
    aside = {x["pass"] for x in g.get("passes_set_aside", [])}
    s_items = secant(C["items"])
    pp, ppr = [], []
    for p, items in sorted(per_pass(csvp, aside).items()):
        z = items.get("lq_h0")
        if not z:
            continue
        d = {n: {"d_p80": items[n]["p80"] - z["p80"], "rate": items[n]["rate"],
                 "d_rail": items[n]["rail"] - z["rail"] if items[n]["rail"] is not None and z["rail"] is not None else None}
             for n in ("lq_h2", "lq_h8") if n in items}
        s = secant(d)
        if s is not None:
            pp.append(s)
        sr = secant(d, "d_rail")
        if sr is not None:
            ppr.append(sr)
    m, se, n = mean_se(pp)
    mr, ser, nr = mean_se(ppr)
    return {"items": s_items, "per_pass_mean": m, "se": se, "n": n, "per_pass": pp, "rail": mr, "rail_se": ser, "rail_n": nr}


def hist(path):
    for p in (path, path + ".gz"):
        if os.path.exists(p):
            op = gzip.open if p.endswith(".gz") else open
            h = defaultdict(int)
            for line in op(p, "rt"):
                if line.startswith("{"):
                    try:
                        h[int(json.loads(line)["mhz"]["minion"])] += 1
                    except (ValueError, KeyError, TypeError):
                        pass
            return dict(sorted(h.items()))
    return None


def ring_delta(sess, a, b):
    spec = importlib.util.spec_from_file_location("spe", os.path.join(ROOT, "tools/claims-v3/dv2/sptrace_events.py"))
    spe = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(spe)
    pa, pb = os.path.join(sess, f"ring-{a}.bin"), os.path.join(sess, f"ring-{b}.bin")
    if not (os.path.exists(pa) and os.path.exists(pb)):
        return {"measured": False, "why": "a dump is missing"}
    ba, bb = open(pa, "rb").read(), open(pb, "rb").read()
    if spe.ring_entries(ba) is None or spe.ring_entries(bb) is None:
        return {"measured": False, "why": "a dump is not a ring"}
    ea, eb = spe.events(ba), spe.events(bb)
    covered = spe.overlap(ea, eb)
    new = spe.since(ea, eb)
    kinds = defaultdict(int)
    for e in new:
        kinds[e["kind"]] += 1
    return {"measured": covered, "covered": covered, "new_entries": len(new), "kinds": dict(kinds),
            "power_up": [e["text"] for e in new if e["kind"] == "power_up"][:6],
            "governor_lines": [e["text"] for e in new if e["kind"] in spe.GOVERNOR][:12]}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", required=True)
    ap.add_argument("--gen", required=True)
    ap.add_argument("--e60pred", required=True)
    ap.add_argument("--pred", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    P = json.load(open(a.pred))
    R = P["rules"]
    od = os.path.dirname(os.path.abspath(a.out))
    D6 = sorted(glob.glob(os.path.join(a.data, CARD, "e118", "p[0-9]*")), key=lambda d: int(d.rsplit("p", 1)[1]))
    D6 = [d for d in D6 if os.path.exists(os.path.join(d, "block.json")) and '"ok"' in open(os.path.join(d, "block.json")).read()]
    DC = sorted(glob.glob(os.path.join(a.data, CARD, "e118c", "p[0-9]*")), key=lambda d: int(d.rsplit("p", 1)[1]))
    DC = [d for d in DC if os.path.exists(os.path.join(d, "block.json")) and '"ok"' in open(os.path.join(d, "block.json")).read()]
    out = {"experiment": "E118", "passes_600": [os.path.basename(d) for d in D6], "passes_control": [os.path.basename(d) for d in DC],
           "rules": {}}
    rules = out["rules"]
    v800 = P["voltages"]["v800_sp"]
    s6 = None
    if D6:
        res6 = reduce(D6, "auto", "--pinned", os.path.join(od, "results600.json"), os.path.join(od, "runs600.csv"), a.gen, a.e60pred)
        C6, g6 = res6["cards"][CARD], res6["gates"][CARD]
        s6 = secants(res6, os.path.join(od, "runs600.csv"))
        v600 = C6["v_mean"]
        kept_passes = C6["passes"]
        out["measured_600"] = {"clock_mhz": g6["clock_mhz"], "v_mean": v600, "passes_kept": kept_passes,
                               "runs": g6["runs"], "kept": g6["kept"], "leak_W_per_C": g6["leak_W_per_C"],
                               "passes_set_aside": g6["passes_set_aside"], "failed_runs": g6["failed"], "secant": s6}
        scored = len(kept_passes) >= 3
        r_meas = (v600 / v800) ** 2
        # V1, registered
        x = s6["per_pass_mean"]
        rules["V1"] = {"predicted": R["V1"]["predicted"], "band": R["V1"]["band"], "alternative_band": R["V1"]["alternative_band"],
                       "measured": x, "se": s6["se"], "n_passes": s6["n"], "from_pass_averaged_items": s6["items"],
                       "verdict": verdict(x, R["V1"]["band"], R["V1"]["alternative_band"]) if scored else "NOT SCORED (fewer than 3 kept passes)",
                       "re_evaluated_at_measured_v600": {"predicted": P["reference"]["e60_card0_800MHz"]["lq_fJ_per_designed_bit"] * r_meas,
                                                         "band": band(P["reference"]["e60_card0_800MHz"]["lq_fJ_per_designed_bit"] * r_meas)}}
        # V1m, primary: matched slopes on the passes kept at both
        slopes = R["V1m"]["slopes_W_per_C"]
        first = {k: reduce(D6, k, "--pinned", os.path.join(od, f"m600-k{k}.json"), os.path.join(od, f"m600-k{k}.csv"), a.gen, a.e60pred) for k in slopes}
        inter = sorted(set.intersection(*[set(first[k]["cards"][CARD]["passes"]) for k in slopes]))
        fixed = [d for d in D6 if int(d.rsplit("p", 1)[1]) in inter]
        mrows, hits = {}, 0
        for k in slopes:
            res = reduce(fixed, k, "--pinned", os.path.join(od, f"matched600-k{k}.json"), os.path.join(od, f"matched600-k{k}.csv"), a.gen, a.e60pred)
            sk = secants(res, os.path.join(od, f"matched600-k{k}.csv"))
            e60 = R["V1m"]["e60_matched"][str(k)]["secant_fJ"]
            pred = e60 * r_meas
            b = band(pred)
            ok = inband(sk["per_pass_mean"], b)
            hits += ok
            mrows[str(k)] = {"e118_secant": sk["per_pass_mean"], "e118_se": sk["se"], "e118_from_items": sk["items"],
                             "n": sk["n"], "e60_secant": e60, "predicted_at_measured_v": pred, "band": b,
                             "frozen_predicted": R["V1m"]["predicted"][str(k)], "frozen_band": R["V1m"]["band"][str(k)],
                             "ratio": sk["per_pass_mean"] / e60 if sk["per_pass_mean"] else None,
                             "n_exponent": (math.log(sk["per_pass_mean"] / e60) / math.log(v600 / v800)) if sk["per_pass_mean"] else None,
                             "verdict": "PASS" if ok else "FAIL"}
        rules["V1m"] = {"slopes": slopes, "e118_fixed_passes": inter, "rows": mrows,
                        "verdict": ("NOT SCORED (fewer than 3 kept passes)" if len(inter) < 3 else
                                    "PASS" if hits == len(slopes) else "PARTIAL" if hits else "FAIL")}
        rules["V2"] = {"predicted": R["V2"]["predicted"], "band": R["V2"]["band"], "measured": s6["rail"], "se": s6["rail_se"],
                       "verdict": verdict(s6["rail"], R["V2"]["band"]) if scored else "NOT SCORED"}
        w = {k: C6["items"][k]["d_p80"] for k in ("lq_h2", "lq_h8") if k in C6["items"]}
        v3 = {k: {"predicted": R["V3"]["predicted_W"][k], "measured": w.get(k),
                  "verdict": verdict(w.get(k), band(R["V3"]["predicted_W"][k]))} for k in ("lq_h2", "lq_h8")}
        rules["V3"] = {"rungs": v3, "verdict": ("NOT SCORED" if not scored else
                                                "PASS" if all(r["verdict"] == "PASS" for r in v3.values()) else "FAIL")}
        lqf = C6.get("lq", {}).get("designed", {}).get("fJ")
        lbf = C6.get("lb", {}).get("designed", {}).get("fJ")
        bend = lqf / s6["items"] if lqf and s6["items"] else None
        rules["V4"] = {"predicted": R["V4"]["predicted"], "band": R["V4"]["band"], "measured": bend, "lq_full_fJ": lqf,
                       "verdict": verdict(bend, R["V4"]["band"]) if scored else "NOT SCORED"}
        lbq = lbf / lqf if lqf and lbf else None
        rules["V5"] = {"predicted": R["V5"]["predicted"], "band": R["V5"]["band"], "measured": lbq, "lb_full_fJ": lbf,
                       "verdict": verdict(lbq, R["V5"]["band"]) if scored else "NOT SCORED"}
        try:
            ton = C6["lb"]["first_flip_W"]["W"] / C6["lq"]["first_flip_W"]["W"]
        except (KeyError, TypeError, ZeroDivisionError):
            ton = None
        rules["V6"] = {"predicted": R["V6"]["predicted"], "band": R["V6"]["band"], "measured": ton,
                       "verdict": verdict(ton, R["V6"]["band"]) if scored else "NOT SCORED"}
        rules["G2"] = {"predicted": R["G2"]["predicted"], "band": R["G2"]["band"], "measured": v600,
                       "verdict": verdict(v600, R["G2"]["band"])}
    # C1 and V1s from the control
    sc = None
    if DC:
        resc = reduce(DC, "auto", "--free", os.path.join(od, "resultsC.json"), os.path.join(od, "runsC.csv"), a.gen, a.e60pred)
        Cc, gc = resc["cards"][CARD], resc["gates"][CARD]
        sc = secants(resc, os.path.join(od, "runsC.csv"))
        out["measured_control"] = {"clock_mhz": gc["clock_mhz"], "v_mean": Cc["v_mean"], "passes_kept": Cc["passes"],
                                   "runs": gc["runs"], "kept": gc["kept"], "leak_W_per_C": gc["leak_W_per_C"],
                                   "failed_runs": gc["failed"], "passes_set_aside": gc["passes_set_aside"], "secant": sc}
        wc = {k: Cc["items"][k]["d_p80"] for k in ("lq_h2", "lq_h8") if k in Cc["items"]}
        c1 = {k: {"predicted": R["C1"]["predicted_W"][k], "measured": wc.get(k), "se": Cc["items"].get(k, {}).get("d_p80_se"),
                  "verdict": verdict(wc.get(k), band(R["C1"]["predicted_W"][k]))} for k in ("lq_h2", "lq_h8")}
        rules["C1"] = {"rungs": c1, "clock_mhz": gc["clock_mhz"],
                       "verdict": ("NOT SCORED (fewer than 2 kept control passes)" if len(Cc["passes"]) < 2 else
                                   "PASS" if all(r["verdict"] == "PASS" for r in c1.values()) else "FAIL")}
        if s6 and sc and sc["per_pass_mean"]:
            vr = (out["measured_600"]["v_mean"] / Cc["v_mean"]) ** 2
            rules["V1s"] = {"note": "reported, not scored", "e118_600": s6["per_pass_mean"], "e118_800_control": sc["per_pass_mean"],
                            "control_se": sc["se"], "ratio": s6["per_pass_mean"] / sc["per_pass_mean"], "v2_ratio": vr,
                            "f_v2_ratio": 0.75 * vr,
                            "n_exponent": math.log(s6["per_pass_mean"] / sc["per_pass_mean"]) / math.log(out["measured_600"]["v_mean"] / Cc["v_mean"])}
    else:
        rules["C1"] = {"verdict": "UNMEASURED (no control pass)"}
    # G1, G3 from the evidence
    sess = os.path.join(a.data, "session")
    smoke = hist(os.path.join(a.data, CARD, "e118-smoke", "p900", "telemetry.jsonl"))
    allpin = defaultdict(int)
    for d in glob.glob(os.path.join(a.data, CARD, "e118", "p[0-9]*")) + glob.glob(os.path.join(a.data, CARD, "e118probe", "p*")):
        h = hist(os.path.join(d, "telemetry.jsonl")) or {}
        for k, v in h.items():
            allpin[k] += v
    r01 = ring_delta(sess, "before-pin", "after-pinned")
    clock_ok = bool(smoke) and set(smoke) == {600} and set(allpin) == {600}
    log_half = ("UNMEASURED" if not r01.get("measured") else "PASS" if not r01["power_up"] and not r01["kinds"].get("power_up") else "FAIL")
    rules["G1"] = {"smoke_clocks": smoke, "pinned_pass_clocks": dict(allpin), "clock_half": "PASS" if clock_ok else "FAIL",
                   "ring_before_pin_to_after_pinned": r01, "log_half": log_half,
                   "verdict": "PASS" if clock_ok and log_half == "PASS" else ("PARTIAL" if clock_ok else "FAIL")}
    gov = [json.loads(l) for l in open(os.path.join(sess, "gov.jsonl"))] if os.path.exists(os.path.join(sess, "gov.jsonl")) else []
    rest = [e for e in gov if e.get("event") == "restore"]
    rb = [e for e in gov if e.get("event") == "readback" and e.get("tag") == "after-restore"]
    restore_ok = bool(rest) and rest[-1].get("ok") and bool(rb) and (rb[-1].get("config") or {}).get("tdp_w") == 65 \
        and (rb[-1].get("config") or {}).get("temp_threshold_c") == 65
    burst = hist(os.path.join(a.data, CARD, "e118back-smoke", "p901", "telemetry.jsonl"))
    step_ok = bool(burst) and max(burst) >= 700
    r12 = ring_delta(sess, "after-pinned", "after-back")
    ev_half = "UNMEASURED" if not r12.get("measured") else ("PASS" if r12["kinds"].get("power_up", 0) >= 1 else "FAIL")
    rules["G3"] = {"restore_and_readback": "PASS" if restore_ok else "FAIL", "restore_event": rest[-1] if rest else None,
                   "readback_after_restore": rb[-1] if rb else None, "burst_clocks": burst,
                   "step_half": "PASS" if step_ok else "FAIL", "ring_after_pinned_to_after_back": r12, "event_half": ev_half,
                   "verdict": "PASS" if restore_ok and step_ok and ev_half == "PASS" else
                              ("PARTIAL" if restore_ok and step_ok else "FAIL")}
    order = ["V1m", "V1", "V2", "V3", "V4", "V5", "V6", "C1", "G1", "G2", "G3"]
    out["summary"] = {k: rules[k]["verdict"] for k in order if k in rules}
    json.dump(out, open(a.out, "w"), indent=1)
    print(json.dumps(out["summary"], indent=1))


if __name__ == "__main__":
    main()
