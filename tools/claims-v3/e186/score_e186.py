#!/usr/bin/env python3
"""E186 (Q158, the kit): the scorer for E186.md section 5's rules, on one session's reductions. Nothing is fitted or tuned here. The lines
are forecast-e186.json's (through forecast_e186.lines_at, imported unchanged), the statistics and words e186_stats.py's (which imports
E182's e182_stats unchanged), the plan plan-e186.json's (each checked against the registration's hash list first). It writes scored-e186.json
in E182's scored.json form (its "trains" > <id> > the interval; "rules"; "verdicts"; "reported" > "kinds" > <key> > D_w), which note M1's
reader (arm_m1_read_e186.py) reads after it.

  score   python3 -B score_e186.py score --raw <raw copy> --ccheck <ccheck --out json> [--trains <trains-e186.json>]
              [--anchors <e186-anchors.json>] [--reduction <e186.json> --runs-csv <runs.csv>] [--since <epoch s>]
              [--json scored-e186.json] [--md results-e186.md] [--skip-c-gate]

Order, enforced: (1) the frozen inputs (exit 9); (2) every session that must carry a C log has a finished check (ccsessions_e186; exit 4,
nothing written; --skip-c-gate exists for the self-test only); (3) E186-C: every launch of every E186 kind, the trains' and their anchors'
included, judged PASS (by t_start_ms and t_end_ms against the check of C's verdicts); a train with a launch not PASS is NOT SCORED, and a
kind not all PASS leaves the fallback's level set; (4) the session's float scale s, M10's term a, read as E182's scorer reads it
(score_e178.session_scale, imported unchanged) over the float trains' anchors' reduction in FULL (E186.md section 4.2) or the fallback's
kinds passes; FAIL CLOSED: an exception, or no float anchor used, is "s not read" (the predictor's own "1 if none" is never taken as a
reading); (5) each train's lines at s and its measured rate (lines_at); (6) the rules; (7) the readings reported beside, never a verdict.

THE READINGS WHERE E186.md LEAVES A CHOICE (stated in KIT.md before any datum):
  the measured rate   a train's rate_per_s from reduce_e186.py trains (its own launch records); the candidates' rate when none;
  s not read          the four ladder trains (B15-B7, B23-B15, A15-A7, A23-A15) read NOT SCORED in every word built on a line (SIZE
                      against M12, SIZE against M10, WHICH, and their z in E186-M and its reported joint words), E186-GB and E186-GA read
                      NOT SCORED; their SIGN words stand; no other rule reads s;
  E186-M              the nine session trains other than H16 whose SIZE words are scored; the joint words over all ten are reported;
  E186-TR-N           the quads' residual sd pooled by family, int8 and float (fp16 and fp32 together, as power_e186.py pools them);
  E186-LV             the fallback's 15 kinds (each with two or more kept passes and every launch PASS) at the session's s and each
                      kind's measured rate: M10's level P10 x s x q (int8 s = 1); M12's float level P10 x s x q + its increment; M12's
                      int8 level its flip part x q + the rest, moved by the registered anchor D(int8.full, session) - 7.16439 W;
                      random.Random(18660)'s 2,000-draw bootstrap (m12_common.boot_rms_diff, through e186_stats).
Exit 0 when scored-e186.json is written, 4 (no finished check of C), 9 (a frozen input differs). /usr/bin/python3 (3.9, numpy for the
scale). SPDX-License-Identifier: Apache-2.0
"""
import argparse
import csv
import gzip
import hashlib
import json
import math
import os
import statistics
import sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
TOP = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, HERE)
import e186_stats as R  # noqa: E402
import e186_common as E  # noqa: E402
import forecast_e186 as FE  # noqa: E402  (lines_at only; build() is not called)
S = R.S

E178D = os.path.join(TOP, "tools", "claims-v3", "e178")
FROZEN_READ = ["tools/claims-v3/e186/forecast-e186.json", "tools/claims-v3/e186/power-e186.json", "tools/claims-v3/e186/plan-e186.json",
               "tools/claims-v3/e186/e186_stats.py", "tools/claims-v3/e186/forecast_e186.py", "tools/claims-v3/e186/E186.md"]
LADDERS = ("B15-B7", "B23-B15", "A15-A7", "A23-A15")
TRN_SIG = {"int8": 0.03485, "float": 0.03804}
MIN_KIND_PASSES = 2
EXIT_FROZEN, EXIT_NO_C = 9, 4
SESSION_ORDER = ("H16", "S23", "Q63-sign", "Q63-swap", "B15-B7", "B23-B15", "Q3-sign", "Q3-swap", "A15-A7", "A23-A15")


def rule_of(tid):
    """E186.md section 5.2's names: E186-H16, E186-S23, E186-Q63SIGN, E186-Q63SWAP, E186-B15B7, ..."""
    return "E186-" + tid.replace("-", "").upper()


RULES = ["E186-C"] + [rule_of(t) for t in SESSION_ORDER] + \
        ["E186-SPLIT3", "E186-SPLIT63", "E186-GB", "E186-GA", "E186-S23R", "E186-M", "E186-TR-N", "E186-LV"]


class Refuse(Exception):
    def __init__(self, code, msg):
        super().__init__(msg)
        self.code = code


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def frozen_check():
    e = E.check_frozen()
    want = {}
    for line in open(os.path.join(TOP, "tools/claims-v3/e186/SHA256SUMS-e186-registration")):
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
        for r in jl(os.path.join(raw, "e186", f"p{p}", "runs.jsonl")):
            if r.get("item"):
                add(r["item"], r, f"p{p}")
    for b, t in sorted(E.TRAINS.items()):
        d = os.path.join(raw, "e186", f"p{b}")
        bad = n = 0
        for r in jl(os.path.join(d, "train.jsonl")):
            k = t["first"] if r.get("train_kind") == "F" else t["second"]
            v = add(k, r, f"p{b}")
            n += 1
            bad += v != "PASS"
        for sub in ("a0", "a1"):
            for r in jl(os.path.join(d, sub, "runs.jsonl")):
                if r.get("item"):
                    v = add(r["item"], r, f"p{b}/{sub}")
                    n += 1
                    bad += v != "PASS"
        trains[t["train"]] = {"launches": n, "not_pass": bad, "all_pass": n > 0 and bad == 0}
    for s in per.values():
        s["all_pass"] = s["launches"] > 0 and s["PASS"] == s["launches"]
        s["where"] = sorted(s["where"])
    return per, trains


# ------------------------------------------------------------------------------------------------- the trains
def train_iv(tr, tid, ctr):
    t = tr.get("trains", {}).get(tid)
    if t is None:
        return {"n": 0, "lo": None, "hi": None, "mean": None, "se": None, "df": None, "hw": None, "why": "no train block"}
    if not ctr.get(tid, {}).get("all_pass"):
        return {"n": 0, "lo": None, "hi": None, "mean": None, "se": None, "df": None, "hw": None, "why": f"E186-C: {ctr.get(tid)}"}
    iv = dict(t["estimate"])
    if iv.get("n", 0) < S.MIN_UNITS or iv.get("lo") is None:
        return {"n": iv.get("n", 0), "lo": None, "hi": None, "mean": iv.get("mean"), "se": None, "df": None, "hw": None,
                "why": f"{iv.get('n', 0)} units, fewer than {S.MIN_UNITS}"}
    if iv.get("hw") is None:
        iv["hw"] = (iv["hi"] - iv["lo"]) / 2.0
    return iv


def read_scale(path):
    """the session's float scale: score_e178.session_scale over a reduction (E182's route), FAIL CLOSED"""
    if not path or not os.path.exists(path):
        return None, "no reduction to read the scale from"
    try:
        sys.path.insert(0, E178D)
        import score_e178 as SE  # noqa: E402  (session_scale only, unchanged)
        sc, _ = SE.session_scale("aifoundry3", path)
    except Exception as ex:  # noqa: BLE001  (recorded: fail closed)
        return None, f"the scale could not be read: {ex!r}"
    if not sc.get("anchors_used"):
        return None, f"the scale read no float anchor (the predictor's own 1 is not a reading): {sc}"
    return float(sc["s_float"]), sc


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


def measured(res, kinds, passes):
    out = {}
    for k in kinds:
        vals = []
        for p in passes:
            r = res.get("per_pass", {}).get(str(p), {}).get(k)
            if r and r.get("D") is not None and not (isinstance(r["D"], float) and math.isnan(r["D"])):
                vals.append(float(r["D"]))
        if len(vals) >= MIN_KIND_PASSES:
            out[k] = {"mean": statistics.mean(vals), "sd": statistics.stdev(vals), "n": len(vals), "per_pass": vals}
    return out


def level_at(cj, m12, k, s_float, q, anchor_shift):
    """E186-LV's lines for one kind at the session's s and rate ratio q (E186.md section 5.5, by lines_at's rule for each part)"""
    v = cj["kinds"][k]
    p10 = v["P10_w"]
    if v["type"] == "int8":
        b = m12["int8"]["b"]
        fl = v["design_row"][1] * b[1] + v["design_row"][2] * b[2]
        return {"M12": fl * q + (v["M12_w"] - fl) + anchor_shift, "M10": p10 * q}
    return {"M12": p10 * s_float * q + (v["M12_w"] - p10), "M10": p10 * s_float * q}


def score(a):
    out = {"_note": "Q158 score_e186.py: E186 on aifoundry3, E186.md section 5's rules", "run": "E186", "card": "aifoundry3",
           "scorer_sha256": sha(os.path.abspath(__file__)), "frozen_inputs": frozen_check()}
    FC = json.load(open(os.path.join(HERE, "forecast-e186.json")))
    PL = json.load(open(os.path.join(HERE, "plan-e186.json")))
    if not a.skip_c_gate:
        import ccsessions_e186 as CS  # noqa: E402
        g = CS.check("E186", a.raw, a.ccheck, a.since)
        g = json.loads(json.dumps(g).replace(TOP + os.sep, ""))
        out["c_sessions"] = {k: g[k] for k in ("sessions", "stoptest", "ccdone", "ok") if k in g}
        if not g["ok"]:
            raise Refuse(EXIT_NO_C, "a session that must carry a C log has no finished check of C (E186.md section 7); every rule reads NOT "
                                    "SCORED and nothing is written:\n  " + "\n  ".join(g.get("lines", [])))
    res = json.load(open(a.reduction)) if a.reduction and os.path.exists(a.reduction) else {}
    kept = [int(p) for p in res.get("passes", [])] if res else []
    tr = json.load(open(a.trains)) if a.trains and os.path.exists(a.trains) else {"trains": {}}
    cst, ctr = c_status(a.raw, [a.ccheck, a.ccheck + ".gz"], kept)
    names = list(E.E186_NAMES)
    cfail = sorted(k for k in names if k in cst and not cst[k]["all_pass"])
    out["c_status"] = {"kinds": {k: cst[k] for k in sorted(cst) if k in names}, "trains": ctr, "kinds_not_all_pass": cfail}
    out["kept_passes"] = kept
    plan = "FULL" if tr.get("trains") else ("PASSES" if kept else "none")
    # (4) the scale: the float trains' anchors in FULL, the kinds passes in the fallback; fail closed
    if plan == "FULL":
        s_float, note = read_scale(a.anchors)
        src = "the float trains' anchors (reduce_e186.py anchors)"
    elif len(kept) >= 2:
        s_float, note = read_scale(a.reduction)
        src = "the fallback's kinds passes"
    else:
        s_float, note, src = None, "fewer than two kept kinds passes and no train", "none"
    out["scale"] = {"s_float": s_float, "read": s_float is not None, "from": src, "note": note}
    rules, rep = {}, {}
    rules["E186-C"] = {"verdict": "PASS" if not cfail and all(v["all_pass"] for v in ctr.values() if v["launches"]) else "FAIL",
                       "kinds_not_all_pass": cfail, "trains_not_all_pass": sorted(k for k, v in ctr.items() if v["launches"] and not v["all_pass"])}
    # (5) each session train's interval and lines
    ids = list(PL["session_trains"])
    if tuple(ids) != SESSION_ORDER:
        raise Refuse(EXIT_FROZEN, f"plan-e186.json's session trains {ids} are not E186.md section 5.2's {list(SESSION_ORDER)}")
    iv = {tid: train_iv(tr, tid, ctr) for tid in ids}
    out["trains"] = {tid: dict(iv[tid]) for tid in ids}
    rates = FC["rates_per_s"]
    lines, linewhy = {}, {}
    for tid in ids:
        t = FC["trains"][tid]
        rm = (tr.get("trains", {}).get(tid) or {}).get("rate_per_s")
        rate_used = rm if isinstance(rm, (int, float)) and rm > 0 else rates[t["type"]]
        if tid in LADDERS and s_float is None:
            lines[tid] = None
            linewhy[tid] = "s not read: the line carries P10's offset times s (fail closed, E186.md section 4.2)"
            continue
        lines[tid] = FE.lines_at(FC, tid, s_float if s_float is not None else 1.0, rate_used, rates[t["type"]])
        out["trains"][tid]["lines"] = {k: list(v) for k, v in lines[tid].items()}
        out["trains"][tid]["rate_used_per_s"] = rate_used
        out["trains"][tid]["rate_measured"] = isinstance(rm, (int, float)) and rm > 0
    # (6) the train rules
    z12, z10 = {}, {}
    for tid in ids:
        r = {"estimate": iv[tid]}
        v = iv[tid]
        if v.get("lo") is None:
            r.update(verdict="NOT SCORED", sign="NOT SCORED", size_M12="NOT SCORED", size_M10="NOT SCORED", which="NOT SCORED",
                     why=v.get("why"))
            rules[rule_of(tid)] = r
            continue
        r["sign"] = S.sign_of(v)
        if lines[tid] is None:
            r.update(size_M12="NOT SCORED", size_M10="NOT SCORED", which="NOT SCORED", why=linewhy[tid])
        else:
            l12, se12 = lines[tid]["M12"]
            l10, _ = lines[tid]["M10"]
            r["lines_w"] = {"M12": l12, "M12_se": se12, "M10": l10}
            r["size_M12"] = R.size_band(v, l12, se12)
            r["size_M10"] = R.size_band(v, l10, 0.0)
            r["which"] = R.which(r["size_M12"], r["size_M10"])
            z12[tid] = R.zscore(v, l12, se12)
            z10[tid] = R.zscore(v, l10, 0.0)
            if tid == "H16":
                ls, ses = lines[tid]["SCALED"]
                r["lines_w"]["SCALED"], r["lines_w"]["SCALED_se"] = ls, ses
                r["size_SCALED"] = R.size_band(v, ls, ses)
                r["H16"] = R.h16_word({"F16-SAME": r["size_M12"], "SCALED": r["size_SCALED"], "M10": r["size_M10"]})
        r["verdict"] = r.get("H16", r["which"]) if tid == "H16" else r["which"]
        rules[rule_of(tid)] = r
    # the rules read from the trains
    D = FC["derived"]
    for nm in ("SPLIT3", "SPLIT63"):
        d = D[nm]
        sw, sg = iv[d["swap"]], iv[d["sign"]]
        if sw.get("lo") is None or sg.get("lo") is None:
            rules[f"E186-{nm}"] = {"verdict": "NOT SCORED", "why": f"{d['swap']} or {d['sign']} not scored"}
            continue
        bA, bB = R.split_from(sw, sg, tuple(d["dh_swap_a_b_per_byte"]), tuple(d["dh_sign_a_b_per_byte"]))
        wa, wb = S.null_of(bA, d["band_w_per_bit"]), S.null_of(bB, d["band_w_per_bit"])
        rules[f"E186-{nm}"] = {"verdict": S.split_of(wa, wb), "beta_A": bA, "beta_B": bB, "side_A": wa, "side_B": wb,
                               "size_beta_A_M12": R.size_band(bA, d["M12_beta_A_w"], d["M12_beta_A_se_w"]),
                               "size_beta_B_M12": R.size_band(bB, d["M12_beta_B_w"], d["M12_beta_B_se_w"]),
                               "M12_beta_A_w": d["M12_beta_A_w"], "M12_beta_B_w": d["M12_beta_B_w"],
                               "M10_beta_A_w": d["M10_beta_A_w"], "M10_beta_B_w": d["M10_beta_B_w"], "band_w_per_bit": d["band_w_per_bit"]}
    for nm in ("GB", "GA"):
        d = D[nm]
        x, y = d["trains"]
        if s_float is None:
            rules[f"E186-{nm}"] = {"verdict": "NOT SCORED", "why": "s not read (fail closed, E186.md section 4.2)"}
            continue
        offs = [lines[x]["M10"][0] if lines.get(x) else None, lines[y]["M10"][0] if lines.get(y) else None]
        g = R.slope_from(iv[x], iv[y], tuple(o if o is not None else 0.0 for o in offs), d["bits_each"])
        if g.get("lo") is None:
            rules[f"E186-{nm}"] = {"verdict": "NOT SCORED", "why": f"neither {x} nor {y} scored"}
            continue
        rules[f"E186-{nm}"] = {"verdict": S.sign_of(g), "gamma": g, "size_M12": R.size_band(g, d["M12_gamma_w"], d["M12_gamma_se_w"]),
                               "size_M10": R.size_band(g, d["M10_gamma_w"], 0.0), "M12_gamma_w": d["M12_gamma_w"],
                               "M12_gamma_se_w": d["M12_gamma_se_w"], "P10_offsets_scored_w": offs, "side": d["side"]}
    d = D["S23R"]
    if iv["S23"].get("lo") is not None:
        sc23 = R.scaled(iv["S23"], d["factor"])
        rules["E186-S23R"] = {"verdict": S.agrees(sc23, d["T5"]["lo"], d["T5"]["hi"]), "s23_times_23_16": sc23, "T5": d["T5"]}
    else:
        rules["E186-S23R"] = {"verdict": "NOT SCORED", "why": "S23 not scored"}
    nine = [t for t in ids if t != "H16" and t in z12]
    j12, j10 = R.joint([z12[t] for t in nine]), R.joint([z10[t] for t in nine])
    rules["E186-M"] = {"verdict": R.models_word(j12["word"], j10["word"]), "M12": j12, "M10": j10, "trains": nine,
                       "trains_not_in": [t for t in ids if t != "H16" and t not in nine]}
    a12, a10 = R.joint([z12[t] for t in ids if t in z12]), R.joint([z10[t] for t in ids if t in z10])
    rep["E186-M over all ten (reported)"] = {"word": R.models_word(a12["word"], a10["word"]), "M12": a12, "M10": a10}
    for fam in ("int8", "float"):
        rep.setdefault("joint_by_family", {})[fam] = {
            "M12": R.joint([z12[t] for t in ids if t in z12 and (FC["trains"][t]["type"] == "int8") == (fam == "int8")]),
            "M10": R.joint([z10[t] for t in ids if t in z10 and (FC["trains"][t]["type"] == "int8") == (fam == "int8")])}
    # E186-TR-N, by family
    by_f = {}
    for tid, t in tr.get("trains", {}).items():
        if not ctr.get(tid, {}).get("all_pass"):
            continue
        rp = t["reported"]
        if rp.get("quad_residual_df"):
            fam = "int8" if t["type"] == "int8" else "float"
            ss, dfn = by_f.get(fam, (0.0, 0))
            by_f[fam] = (ss + rp["quad_residual_sd"] ** 2 * rp["quad_residual_df"], dfn + rp["quad_residual_df"])
    ratios = {f: {"pooled_sd_w": math.sqrt(ss / dfn), "df": dfn, "forecast_sd_w": TRN_SIG[f], "ratio": math.sqrt(ss / dfn) / TRN_SIG[f]}
              for f, (ss, dfn) in by_f.items()}
    if ratios:
        rr = max(v["ratio"] for v in ratios.values())
        rules["E186-TR-N"] = {"verdict": "AS FORECAST" if rr <= 1.25 else ("WORSE" if rr <= 2.0 else "FAILS"), "largest_ratio": rr, "by_family": ratios}
    else:
        rules["E186-TR-N"] = {"verdict": "NOT SCORED", "why": "no train scored"}
    # E186-LV, the fallback's levels (only when kinds passes ran)
    if len(kept) >= 2:
        cj = json.load(open(os.path.join(TOP, "tools/claims-v3/m12/candidates-m12-e186.json")))
        m12 = json.load(open(os.path.join(TOP, "tools/claims-v3/m12/m12.json")))
        meas = measured(res, names + ["int8.full"], kept)
        rt = {k: (it.get("rate") or {}).get("mean") for k, it in (res.get("items") or {}).items()}
        anc = meas.get("int8.full", {}).get("mean")
        shift = (anc - FC["int8_session_anchor"]["D_int8_full_E182_w"]) if anc is not None else None
        ok = [k for k in names if k in meas and k not in cfail]
        if shift is None or s_float is None or len(ok) < 2:
            rules["E186-LV"] = {"verdict": "NOT SCORED", "why": "the int8 anchor, s or two scored kinds missing", "anchor_shift_w": shift,
                                "s_read": s_float is not None, "kinds": ok}
        else:
            e12, e10, per = [], [], {}
            for k in ok:
                ty = FC["levels"][k]["type"]
                q = (rt.get(k) or rates[ty]) / rates[ty]
                ln = level_at(cj, m12, k, s_float, q, shift if ty == "int8" else 0.0)
                e12.append(meas[k]["mean"] - ln["M12"])
                e10.append(meas[k]["mean"] - ln["M10"])
                per[k] = {"D_w": meas[k]["mean"], "M12_w": ln["M12"], "M10_w": ln["M10"], "n": meas[k]["n"]}
            b = R.boot_rms_diff(e12, e10, draws=2000, seed=18660)
            rules["E186-LV"] = {"verdict": "M12 BETTER" if b["hi95"] < 0 else ("M12 WORSE" if b["lo95"] > 0 else "NOT RESOLVED"),
                                "boot": b, "anchor_shift_w": shift, "kinds": per}
        rep["kinds"] = {k: {"D_w": meas[k]["mean"], "sd_w": meas[k]["sd"], "n": meas[k]["n"], "c_kept": k not in cfail,
                            "rate_per_s": rt.get(k)} for k in meas if k in names}
    else:
        rules["E186-LV"] = {"verdict": "NOT SCORED", "why": f"{len(kept)} kept kinds passes (FULL runs none: the trains read no level)"}
    rep["trains"] = {tid: t.get("reported") for tid, t in tr.get("trains", {}).items()}
    rep["gamma_B_over_gamma_A"] = (rules["E186-GB"]["gamma"]["mean"] / rules["E186-GA"]["gamma"]["mean"]
                                   if rules["E186-GB"].get("gamma") and rules["E186-GA"].get("gamma") and rules["E186-GA"]["gamma"]["mean"]
                                   else None)
    rep["lines_at_s1_and_candidate_rates"] = {tid: {"M12": FC["trains"][tid]["M12_w"], "M10": FC["trains"][tid]["M10_w"]} for tid in ids}
    out["rules"] = rules
    out["verdicts"] = {r: rules[r]["verdict"] for r in RULES if r in rules}
    out["reported"] = rep
    out["plan"] = plan
    return out


def md(out):
    L = ["# E186 scored (score_e186.py)", "", f"plan read: {out['plan']}; the session's float scale s: {out['scale']['s_float']} "
         f"({'read from ' + out['scale']['from'] if out['scale']['read'] else 'NOT READ: fail closed'})", "",
         "| rule | verdict | reading |", "|---|---|---|"]
    for r in RULES:
        v = out["rules"].get(r, {})
        e = v.get("estimate", {})
        if "sign" in v and "estimate" in v:
            rd = (f"{e.get('mean'):+.4f} [{e.get('lo'):+.4f}, {e.get('hi'):+.4f}] W; SIGN {v.get('sign')}; SIZE M12 {v.get('size_M12')}, "
                  f"M10 {v.get('size_M10')}" + (f", SCALED {v.get('size_SCALED')}" if "size_SCALED" in v else "")
                  ) if e.get("lo") is not None else str(v.get("why", ""))
        elif r in ("E186-SPLIT3", "E186-SPLIT63") and "beta_A" in v:
            rd = (f"beta_A {v['beta_A']['mean']:+.5f} [{v['beta_A']['lo']:+.5f}, {v['beta_A']['hi']:+.5f}] ({v['side_A']}; SIZE M12 "
                  f"{v['size_beta_A_M12']}), beta_B {v['beta_B']['mean']:+.5f} [{v['beta_B']['lo']:+.5f}, {v['beta_B']['hi']:+.5f}] "
                  f"({v['side_B']}; SIZE M12 {v['size_beta_B_M12']}) W a bit a byte")
        elif r in ("E186-GB", "E186-GA") and "gamma" in v:
            g = v["gamma"]
            rd = f"{g['mean']:+.5f} [{g['lo']:+.5f}, {g['hi']:+.5f}] W a held bit; SIZE M12 {v['size_M12']}, M10 {v['size_M10']}"
        elif r == "E186-S23R" and "s23_times_23_16" in v:
            c = v["s23_times_23_16"]
            rd = f"S23 x 23/16 {c['mean']:+.4f} [{c['lo']:+.4f}, {c['hi']:+.4f}] W against T5 [{v['T5']['lo']:+.4f}, {v['T5']['hi']:+.4f}]"
        elif r == "E186-M":
            rd = (f"M12 Q {v['M12'].get('Q', float('nan')):.2f} ({v['M12']['word']}), M10 Q {v['M10'].get('Q', float('nan')):.2f} "
                  f"({v['M10']['word']}) over {v['M12'].get('n', 0)} trains" if v.get("M12", {}).get("n") else "no train scored")
        elif r == "E186-TR-N":
            rd = f"largest ratio {v.get('largest_ratio'):.3f}" if "largest_ratio" in v else v.get("why", "")
        elif r == "E186-LV":
            rd = (f"rms(D - M12) - rms(D - M10) {v['boot']['diff']:+.4f} [{v['boot']['lo95']:+.4f}, {v['boot']['hi95']:+.4f}] W"
                  if "boot" in v else v.get("why", ""))
        elif r == "E186-C":
            rd = f"kinds not all PASS {v.get('kinds_not_all_pass')}, trains {v.get('trains_not_all_pass')}"
        else:
            rd = str(v.get("why", ""))
        L.append(f"| {r} | {v.get('verdict', 'NOT SCORED')} | {rd} |")
    return "\n".join(L) + "\n"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=("score",))
    ap.add_argument("--reduction")
    ap.add_argument("--runs-csv")
    ap.add_argument("--trains")
    ap.add_argument("--anchors")
    ap.add_argument("--raw", required=True)
    ap.add_argument("--ccheck", required=True)
    ap.add_argument("--since", type=float)
    ap.add_argument("--json")
    ap.add_argument("--md")
    ap.add_argument("--skip-c-gate", action="store_true")
    a = ap.parse_args()
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
