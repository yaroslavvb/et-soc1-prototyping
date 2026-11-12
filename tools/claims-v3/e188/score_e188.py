#!/usr/bin/env python3
"""E188 (Q165, the kit): the scorer for E188.md section 5's rules, on one session's reductions. Nothing is fitted or tuned here. The lines
are forecast-e188.json's (through forecast_e188.lines_at, imported unchanged), the statistics and words e188_stats.py's and e186_stats.py's
(which import E182's e182_stats unchanged), the plan plan-e188.json's (each checked against the registration's hash list first), so the
rules scored are the rules power_e188.py simulated (its own calls: size_band, which, zscore, joint, models_word, held_part, mean_of,
flat_q, per_bit, repeat). A port of E186's scorer (tools/claims-v3/e186/score_e186.py with its v2's pairing gate, run on 9 Nov 2026) to
E188's rules. It writes scored-e188.json in E186's form (its "trains" > <id> > the interval; "rules"; "verdicts"; "reported"), which the
october-forecast-model reader (arm_read_e188.py) reads after it, through its gate.

  score   python3 -B score_e188.py score --raw <raw copy> --ccheck <ccheck --out json> [--trains <trains-e188.json>]
              [--anchors <e188-anchors.json>] [--reduction <e188.json> --runs-csv <runs.csv>] [--since <epoch s>]
              [--json scored-e188.json] [--md results-e188.md] [--skip-c-gate]

Order, enforced: (1) the frozen inputs (exit 9); (2) every session that must carry a C log has a finished check (ccsessions_e188; exit 4,
nothing written; --skip-c-gate exists for the self-test only); (3) E188-C: every launch of every E188 kind, the trains', their anchors' and
the kinds passes' included, judged PASS (by t_start_ms and t_end_ms against the check of C's verdicts); a train with a launch not PASS is
NOT SCORED; (4) E188-SCHED, the pairing check (pairing_e188.py over every train block): a train whose launch records do not pair with the
registered schedule, type, tile and a C record of that tile's bytes is NOT SCORED; (5) the session's float scale s and each train's
measured rate; (6) each train's lines at s and its rate (lines_at); (7) the rules; (8) the readings reported beside, never a verdict.

THE READINGS WHERE E188.md LEAVES A CHOICE (stated in KIT.md section 4 before any datum):
  the scale s         E188.md section 4.2's order: the trains' own anchor runs (reduce_e188.py anchors: the seven fp32 trains' a0 and a1,
                      E78's reduction on E182's footing) through score_e178.session_scale; if they give none, the session's kinds passes'
                      reduction the same way (FULL's 18820/18821, or the fallback's); if neither gives one, s = 1 and every word built on a
                      line carries "s unread (1 used)". E188 does NOT fail closed on s (E188.md section 4.2: s moves no line by more than
                      |M10's line| x |s - 1|). "Gives none" is an exception in the reading or a reading that used no float anchor;
  the measured rate   a train's rate_per_s from reduce_e188.py trains (its own launch records) over forecast-e188.json's rate_fp32_per_s;
                      the candidates' rate (ratio 1) when none;
  E188-GB1            over the five one-bit B trains scored when all five are; with fewer, over those scored if at least three, else
                      NOT SCORED; a train counts as scored when its interval exists (C all PASS, paired, 8 units or more);
  E188-BPOS           over the scored one-bit B trains, at least three;
  E188-M              over every scored train (PAIR included), the 95% point at n scored trains;
  E188-TR-N           the quads' residual sd pooled over the scored trains (all fp32), against 0.03804 W;
  E188-LV             the fallback only (no train scored, two or more kept fallback passes): the fifteen kinds each with two or more kept
                      passes and every launch PASS, at the session's s and each kind's measured rate: M10's level P10 x s x q, M12's
                      P10 x s x q + its increment (forecast-e188.json kinds: M12_w - P10_w); random.Random(18860)'s 2,000-draw bootstrap
                      (m12_common.boot_rms_diff, through e186_stats); in FULL its arithmetic over the kinds pass's eight kinds is reported;
  the kinds passes    reported only, FULL's (18820/18821; the fallback's passes hold each kind once and read E188-LV instead): a kind's
                      per-segment contrast D(kind) - D(fp32.ones) over the kept segments of the kept passes, the
                      mean with t(0.975, n - 1) (E188.md section 5.4); the tie (the host's built-in pi, first and last in a pass): its
                      mean over a pass's two runs less fp32.ones' mean over the pass, and less the pi x pi tile's mean over the pass, the
                      mean over kept passes; BALL - AALL beside E182's T5 interval.
Exit 0 when scored-e188.json is written, 4 (no finished check of C), 9 (a frozen input differs, or a registered tile is off its sha256).
/usr/bin/python3 (3.9, numpy for the scale). SPDX-License-Identifier: Apache-2.0
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
import e188_stats as E8  # noqa: E402  (unchanged: imports e186_stats and e182_stats unchanged)
import e188_common as E  # noqa: E402
import forecast_e188 as FE  # noqa: E402  (lines_at only; forecast() is not called)
import pairing_e188 as PR  # noqa: E402
R = E8.R
S = E8.S

E178D = os.path.join(TOP, "tools", "claims-v3", "e178")
FROZEN_READ = ["tools/claims-v3/e188/forecast-e188.json", "tools/claims-v3/e188/power-e188.json", "tools/claims-v3/e188/plan-e188.json",
               "tools/claims-v3/e188/e188_stats.py", "tools/claims-v3/e188/forecast_e188.py", "tools/claims-v3/e188/E188.md",
               "tools/claims-v3/e188/kinds-e188.json"]
SESSION_ORDER = ("B05", "PAIR", "B19", "AALL", "B10", "B22", "B04")
B_ONE_BIT = ("B04", "B05", "B10", "B19", "B22")
TRN_SIG = 0.03804
MIN_KIND_PASSES = 2
EXIT_FROZEN, EXIT_NO_C = 9, 4


def rule_of(tid):
    return "E188-" + tid


RULES = ["E188-C", "E188-SCHED"] + [rule_of(t) for t in SESSION_ORDER] + ["E188-GB1", "E188-BPOS", "E188-GA23", "E188-M", "E188-TR-N",
                                                                           "E188-LV"]


class Refuse(Exception):
    def __init__(self, code, msg):
        super().__init__(msg)
        self.code = code


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def frozen_check():
    e = E.check_frozen()
    want = {}
    for line in open(os.path.join(TOP, "tools/claims-v3/e188/SHA256SUMS-e188-registration")):
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


def references():
    """E186-GB's and E186-GA's measured intervals, as the registration froze them (power-e188.json > e186_gb / e186_ga)"""
    pw = json.load(open(os.path.join(HERE, "power-e188.json")))
    return tuple(pw["e186_gb"]), tuple(pw["e186_ga"])


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
        for r in jl(os.path.join(raw, "e188", f"p{p}", "runs.jsonl")):
            if r.get("item"):
                add(r["item"], r, f"p{p}")
    for b, t in sorted(E.TRAINS.items()):
        d = os.path.join(raw, "e188", f"p{b}")
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
NONE_IV = {"n": 0, "lo": None, "hi": None, "mean": None, "se": None, "df": None, "hw": None}


def train_iv(tr, tid, ctr, pairing_failed):
    t = tr.get("trains", {}).get(tid)
    if t is None:
        return dict(NONE_IV, why="no train block")
    if not ctr.get(tid, {}).get("all_pass"):
        return dict(NONE_IV, why=f"E188-C: {ctr.get(tid)}")
    if tid in pairing_failed:
        f = pairing_failed[tid]
        return dict(NONE_IV, why=f"E188-SCHED (the pairing check): {f['why']}; {f['failures_by_check']}; " + "; ".join(f["first_failures"][:2]))
    iv = dict(t["estimate"])
    if iv.get("n", 0) < S.MIN_UNITS or iv.get("lo") is None:
        return dict(NONE_IV, n=iv.get("n", 0), mean=iv.get("mean"), why=f"{iv.get('n', 0)} units, fewer than {S.MIN_UNITS}")
    if iv.get("hw") is None:
        iv["hw"] = (iv["hi"] - iv["lo"]) / 2.0
    return iv


def read_scale(path):
    """the session's float scale: score_e178.session_scale over a reduction (E182's and E186's route); None when it gives none"""
    if not path or not os.path.exists(path):
        return None, "no reduction to read the scale from"
    try:
        sys.path.insert(0, E178D)
        import score_e178 as SE  # noqa: E402  (session_scale only, unchanged)
        sc, _ = SE.session_scale("aifoundry3", path)
    except Exception as ex:  # noqa: BLE001  (recorded: the next source is read)
        return None, f"the scale could not be read: {ex!r}"
    if not sc.get("anchors_used"):
        return None, f"the scale read no float anchor (the predictor's own 1 is not a reading): {sc}"
    return float(sc["s_float"]), sc


def read_csv(path):
    rows = []
    if not path or not os.path.exists(path):
        return rows
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


def segment_contrasts(rows, kept, kinds, ref="fp32.ones"):
    """E188.md section 5.4: a kind's per-segment contrast D(kind) - D(fp32.ones) over the kept segments of the kept passes, the mean with
    t(0.975, n - 1); a segment is kept when both runs have a D"""
    out = {}
    for k in kinds:
        diffs = []
        for p in kept:
            for s in range(E.SEGMENTS):
                a = [r["D"] for r in rows if r["pass"] == p and r["segment"] == s and r["item"] == k and r["D"] is not None]
                b = [r["D"] for r in rows if r["pass"] == p and r["segment"] == s and r["item"] == ref and r["D"] is not None]
                if a and b:
                    diffs.append(statistics.mean(a) - statistics.mean(b))
        out[k] = S.interval(diffs) if diffs else dict(NONE_IV)
        out[k]["segments"] = len(diffs)
    return out


def tie_contrasts(rows, kept):
    """the tie (the host's built-in pi, its two runs a pass) against fp32.ones and against the pi x pi tile, each pass's means; the mean
    over kept passes with t(0.975, n - 1) when two or more"""
    vs1, vsp = [], []
    for p in kept:
        t = [r["D"] for r in rows if r["pass"] == p and r["item"] == E.ec.TIE and r["D"] is not None]
        o = [r["D"] for r in rows if r["pass"] == p and r["item"] == "fp32.ones" and r["D"] is not None]
        pt = [r["D"] for r in rows if r["pass"] == p and r["item"] == "fp32.pi" and r["D"] is not None]
        if t and o:
            vs1.append(statistics.mean(t) - statistics.mean(o))
        if t and pt:
            vsp.append(statistics.mean(t) - statistics.mean(pt))
    return {"tie_minus_ones": S.interval(vs1) if vs1 else dict(NONE_IV), "tie_minus_pi_tile": S.interval(vsp) if vsp else dict(NONE_IV),
            "passes": len(vs1)}


def score(a):
    out = {"_note": "Q165 score_e188.py: E188 on aifoundry3, E188.md section 5's rules", "run": "E188", "card": "aifoundry3",
           "scorer_sha256": sha(os.path.abspath(__file__)), "pairing_sha256": sha(os.path.join(HERE, "pairing_e188.py")),
           "frozen_inputs": frozen_check()}
    gb_ref, ga_ref = references()
    FC = json.load(open(os.path.join(HERE, "forecast-e188.json")))
    PL = json.load(open(os.path.join(HERE, "plan-e188.json")))
    if not a.skip_c_gate:
        import ccsessions_e188 as CS  # noqa: E402
        g = CS.check("E188", a.raw, a.ccheck, a.since)
        g = json.loads(json.dumps(g).replace(TOP + os.sep, ""))
        out["c_sessions"] = {k: g[k] for k in ("sessions", "stoptest", "ccdone", "ok") if k in g}
        if not g["ok"]:
            raise Refuse(EXIT_NO_C, "a session that must carry a C log has no finished check of C (E188.md section 6); every rule reads NOT "
                                    "SCORED and nothing is written:\n  " + "\n  ".join(g.get("lines", [])))
    res = json.load(open(a.reduction)) if a.reduction and os.path.exists(a.reduction) else {}
    kept = [int(p) for p in res.get("passes", [])] if res else []
    fams = sorted({E.pass_family(p) for p in kept})
    if len(fams) > 1:
        raise Refuse(EXIT_FROZEN, f"the kinds reduction holds both families of kinds pass ({kept}): one family a reduction")
    rows = read_csv(a.runs_csv)
    tr = json.load(open(a.trains)) if a.trains and os.path.exists(a.trains) else {"trains": {}}
    cst, ctr = c_status(a.raw, [a.ccheck, a.ccheck + ".gz"], kept)
    names = list(E.E188_NAMES)
    cfail = sorted(k for k in names if k in cst and not cst[k]["all_pass"])
    out["c_status"] = {"kinds": {k: cst[k] for k in sorted(cst) if k in names}, "trains": ctr, "kinds_not_all_pass": cfail}
    out["kept_passes"] = kept
    out["kept_pass_family"] = fams[0] if fams else None
    try:
        pr = PR.check_raw(a.raw, os.path.dirname(os.path.abspath(a.ccheck)))
    except SystemExit as ex:
        raise Refuse(EXIT_FROZEN, f"the pairing check refused: {ex}")
    pfailed = {tid: v for tid, v in pr["trains"].items() if not v["ok"]}
    out["pairing"] = pr
    plan = "FULL" if tr.get("trains") else ("PASSES" if kept and fams == ["fallback"] else "none")
    # (5) the scale (E188.md section 4.2): the trains' anchors, else the kinds passes, else s = 1 unread
    tries = []
    s_float = None
    if a.anchors:
        s_float, note = read_scale(a.anchors)
        tries.append({"from": "the trains' anchors (reduce_e188.py anchors)", "s": s_float, "note": note})
    if s_float is None and kept:
        s_float, note = read_scale(a.reduction)
        tries.append({"from": f"the session's kinds passes ({fams[0]})", "s": s_float, "note": note})
    s_read = s_float is not None
    s_use = s_float if s_read else 1.0
    out["scale"] = {"s_float": s_float, "s_used": s_use, "read": s_read, "tries": tries,
                    "word": None if s_read else "s unread (1 used)"}
    rules, rep = {}, {}
    rules["E188-C"] = {"verdict": "PASS" if not cfail and all(v["all_pass"] for v in ctr.values() if v["launches"]) else "FAIL",
                       "kinds_not_all_pass": cfail, "trains_not_all_pass": sorted(k for k, v in ctr.items() if v["launches"] and not v["all_pass"])}
    if pr["trains_checked"]:
        rules["E188-SCHED"] = {"verdict": "PASS" if pr["ok"] else "FAIL", "trains_checked": pr["trains_checked"],
                               "trains_not_paired": pr["trains_failed"],
                               "launches_paired": sum(v["launches_paired"] for v in pr["trains"].values()),
                               "launch_records": sum(v["launch_records"] for v in pr["trains"].values())}
    else:
        rules["E188-SCHED"] = {"verdict": "PASS", "trains_checked": [], "why": "no train block read (quote it so: vacuous)"}
    # (6) each train's interval and lines
    ids = [t["train"] for t in PL["trains"]]
    if tuple(ids) != SESSION_ORDER:
        raise Refuse(EXIT_FROZEN, f"plan-e188.json's trains {ids} are not E188.md section 6's {list(SESSION_ORDER)}")
    iv = {tid: train_iv(tr, tid, ctr, pfailed) for tid in ids}
    out["trains"] = {tid: dict(iv[tid]) for tid in ids}
    rate0 = FC["rate_fp32_per_s"]
    lines = {}
    for tid in ids:
        rm = (tr.get("trains", {}).get(tid) or {}).get("rate_per_s")
        q = rm / rate0 if isinstance(rm, (int, float)) and rm > 0 else 1.0
        lines[tid] = FE.lines_at(FC["trains"][tid], s_use, q)
        out["trains"][tid]["lines"] = lines[tid]
        out["trains"][tid]["rate_ratio"] = q
        out["trains"][tid]["rate_measured"] = isinstance(rm, (int, float)) and rm > 0
    # (7) the train rules
    z12, z10, held = {}, {}, {}
    for tid in ids:
        r = {"estimate": iv[tid]}
        v = iv[tid]
        if v.get("lo") is None:
            r.update(verdict="NOT SCORED", sign="NOT SCORED", size_M12="NOT SCORED", size_M10="NOT SCORED", which="NOT SCORED", why=v.get("why"))
            rules[rule_of(tid)] = r
            continue
        ln = lines[tid]
        r["sign"] = S.sign_of(v)
        r["lines_w"] = {"M12": ln["M12_w"], "M12_se": ln["M12_se_w"], "M10": ln["M10_w"]}
        r["size_M12"] = R.size_band(v, ln["M12_w"], ln["M12_se_w"])
        r["size_M10"] = R.size_band(v, ln["M10_w"], 0.0)
        r["which"] = R.which(r["size_M12"], r["size_M10"])
        if not s_read:
            r["s_word"] = "s unread (1 used)"
        r["verdict"] = r["which"]
        z12[tid] = R.zscore(v, ln["M12_w"], ln["M12_se_w"])
        z10[tid] = R.zscore(v, ln["M10_w"], 0.0)
        held[tid] = E8.held_part(v, ln["M10_w"])
        rules[rule_of(tid)] = r
    D = FC["derived"]
    sw = {} if s_read else {"s_word": "s unread (1 used)"}
    # E188-GB1
    bs = [t for t in B_ONE_BIT if t in held]
    if len(bs) >= 3:
        g1 = E8.mean_of([held[t] for t in bs])
        rules["E188-GB1"] = dict({"verdict": S.sign_of(g1), "gamma_B": g1, "trains": bs,
                                  "size_M12": R.size_band(g1, D["gamma_B_w"], D["gamma_B_se_w"]),
                                  "repeat_E186_GB": E8.repeat(g1, *gb_ref), "E186_GB": list(gb_ref),
                                  "M12_gamma_B_w": D["gamma_B_w"], "M12_gamma_B_se_w": D["gamma_B_se_w"],
                                  "M10_held_bit_w": D["M10_held_bit_w"], "size_M10_beside": R.size_band(g1, D["M10_held_bit_w"], 0.0)}, **sw)
    else:
        rules["E188-GB1"] = {"verdict": "NOT SCORED", "why": f"{len(bs)} one-bit B trains scored, fewer than three", "trains": bs}
    # E188-BPOS
    if len(bs) >= 3:
        fq = E8.flat_q([held[t] for t in bs])
        rules["E188-BPOS"] = dict({"verdict": fq["word"], "flat_q": fq, "trains": bs, "held_parts": {t: held[t] for t in bs}}, **sw)
    else:
        rules["E188-BPOS"] = {"verdict": "NOT SCORED", "why": f"{len(bs)} one-bit B trains scored, fewer than three"}
    # E188-GA23
    if "AALL" in held:
        ga = E8.per_bit(held["AALL"], 23)
        rules["E188-GA23"] = dict({"verdict": S.sign_of(ga), "gamma_A": ga, "size_M12": R.size_band(ga, D["gamma_A_w"], D["gamma_A_se_w"]),
                                   "repeat_E186_GA": E8.repeat(ga, *ga_ref), "E186_GA": list(ga_ref), "M12_gamma_A_w": D["gamma_A_w"],
                                   "M12_gamma_A_se_w": D["gamma_A_se_w"], "M10_held_bit_w": D["M10_held_bit_w"],
                                   "size_M10_beside": R.size_band(ga, D["M10_held_bit_w"], 0.0)}, **sw)
    else:
        rules["E188-GA23"] = {"verdict": "NOT SCORED", "why": "AALL not scored"}
    # E188-M
    sc_ids = [t for t in ids if t in z12]
    j12, j10 = R.joint([z12[t] for t in sc_ids]), R.joint([z10[t] for t in sc_ids])
    rules["E188-M"] = dict({"verdict": R.models_word(j12["word"], j10["word"]), "M12": j12, "M10": j10, "trains": sc_ids,
                            "trains_not_in": [t for t in ids if t not in sc_ids]}, **sw)
    six = [t for t in sc_ids if t != "PAIR"]
    rep["E188-M over the six trains other than PAIR (reported)"] = {
        "word": R.models_word(R.joint([z12[t] for t in six])["word"], R.joint([z10[t] for t in six])["word"]),
        "M12": R.joint([z12[t] for t in six]), "M10": R.joint([z10[t] for t in six]), "trains": six}
    # E188-TR-N
    ss, dfn = 0.0, 0
    for tid in sc_ids:
        rp = tr["trains"][tid]["reported"]
        if rp.get("quad_residual_df"):
            ss += rp["quad_residual_sd"] ** 2 * rp["quad_residual_df"]
            dfn += rp["quad_residual_df"]
    if dfn:
        ratio = math.sqrt(ss / dfn) / TRN_SIG
        rules["E188-TR-N"] = {"verdict": "AS FORECAST" if ratio <= 1.25 else ("WORSE" if ratio <= 2.0 else "FAILS"), "ratio": ratio,
                              "pooled_sd_w": math.sqrt(ss / dfn), "df": dfn, "forecast_sd_w": TRN_SIG, "trains": sc_ids}
    else:
        rules["E188-TR-N"] = {"verdict": "NOT SCORED", "why": "no train scored"}
    # the kinds passes: E188-LV in the fallback, the reported contrasts in FULL
    meas = measured(res, names, kept) if kept else {}
    rt = {k: (it.get("rate") or {}).get("mean") for k, it in (res.get("items") or {}).items()}
    lv_kinds = names if fams == ["fallback"] else list(E.PASS_KINDS)
    ok = [k for k in lv_kinds if k in meas and k not in cfail]
    e12, e10, per = [], [], {}
    for k in ok:
        kv = FC["kinds"][k]
        q = (rt.get(k) or rate0) / rate0
        m10 = kv["P10_w"] * s_use * q
        m12 = m10 + (kv["M12_w"] - kv["P10_w"])
        e12.append(meas[k]["mean"] - m12)
        e10.append(meas[k]["mean"] - m10)
        per[k] = {"D_w": meas[k]["mean"], "M12_w": m12, "M10_w": m10, "n": meas[k]["n"], "rate_ratio": q}
    lv = None
    if len(ok) >= 2:
        b = R.boot_rms_diff(e12, e10, draws=2000, seed=18860)
        lv = dict({"verdict": "M12 BETTER" if b["hi95"] < 0 else ("M12 WORSE" if b["lo95"] > 0 else "NOT RESOLVED"), "boot": b, "kinds": per}, **sw)
    if plan == "PASSES" and not sc_ids:
        rules["E188-LV"] = lv if lv else {"verdict": "NOT SCORED", "why": f"{len(ok)} kinds with two kept passes and every launch PASS",
                                          "kept_passes": kept}
    else:
        rules["E188-LV"] = {"verdict": "NOT SCORED", "why": "FULL: the trains are the reading (E188-LV is the fallback's rule)"}
        if lv:
            rep["E188-LV arithmetic over the kinds pass's eight kinds (reported only, E188.md section 5.5)"] = lv
    if kept:
        rep["kinds"] = {k: {"D_w": meas[k]["mean"], "sd_w": meas[k]["sd"], "n": meas[k]["n"], "c_kept": k not in cfail,
                            "rate_per_s": rt.get(k)} for k in meas}
    if kept and fams == ["full"]:                    # E188.md section 5.4: the contrasts are FULL's kinds passes' (section 6's)
        kpl = {v["key"]: (nm, v) for nm, v in FC["kinds_pass"].items()}
        sc_ = segment_contrasts(rows, kept, [k for k in lv_kinds if k != "fp32.ones"])
        rep["kinds_vs_ones"] = {k: dict(sc_[k], lines_w={"M12": kpl[k][1]["M12_w"], "M12_se": kpl[k][1]["M12_se_w"], "M10": kpl[k][1]["M10_w"]}
                                        if k in kpl else None) for k in sc_}
        rep["tie"] = tie_contrasts(rows, kept)
        if "fp32.e182_a1_b3fffffff" in sc_ and "fp32.e182_a3fffffff_b1" in sc_:
            ball, aall = sc_["fp32.e182_a1_b3fffffff"], sc_["fp32.e182_a3fffffff_b1"]
            if ball.get("mean") is not None and aall.get("mean") is not None:
                rep["BALL_minus_AALL_w"] = {"mean": ball["mean"] - aall["mean"], "beside_E182_T5": [0.2299, 0.2419],
                                            "note": "the difference of the two kinds' mean contrasts over fp32.ones (reported; E182's T5 interval beside)"}
    rep["trains"] = {tid: t.get("reported") for tid, t in tr.get("trains", {}).items()}
    if len([t for t in B_ONE_BIT if iv[t].get("lo") is not None]) >= 2:
        rep["raw Q of the one-bit B trains (estimates, no M10 offset)"] = E8.flat_q([iv[t] for t in B_ONE_BIT if iv[t].get("lo") is not None])
    if "AALL" in held and rules["E188-GB1"].get("gamma_B"):
        a_ = iv["AALL"]["mean"]
        rep["T5 across sessions (reported; cross-session arithmetic)"] = {
            "E182_T5_w": 0.2359, "E188_AALL_w": a_, "B_half_w": 0.2359 + a_,
            "beside_M10_BALL_plus_23_GB1_w": FC["kinds_pass"]["BALL (1.0, 0x3fffffff)"]["M10_w"] + 23 * rules["E188-GB1"]["gamma_B"]["mean"]}
    rep["lines_at_s1_and_candidate_rate"] = {tid: {"M12": FC["trains"][tid]["M12_w"], "M10": FC["trains"][tid]["M10_w"]} for tid in ids}
    out["rules"] = rules
    out["verdicts"] = {r: rules[r]["verdict"] for r in RULES if r in rules}
    out["reported"] = rep
    out["plan"] = plan
    return out


def _f(x, fmt="+.4f"):
    return format(x, fmt) if isinstance(x, (int, float)) else str(x)


def md(out):
    L = ["# E188 scored (score_e188.py)", "",
         f"plan read: {out['plan']}; the session's float scale s: {out['scale']['s_float']} "
         f"({'read' if out['scale']['read'] else 's unread (1 used)'}); kept kinds passes {out['kept_passes']}", "",
         "| rule | verdict | reading |", "|---|---|---|"]
    for r in RULES:
        v = out["rules"].get(r, {})
        e = v.get("estimate", {})
        if "sign" in v and "estimate" in v:
            rd = (f"{_f(e.get('mean'))} [{_f(e.get('lo'))}, {_f(e.get('hi'))}] W; SIGN {v.get('sign')}; SIZE M12 {v.get('size_M12')} "
                  f"(line {_f(v['lines_w']['M12'])}), M10 {v.get('size_M10')} (line {_f(v['lines_w']['M10'])})") if e.get("lo") is not None else str(v.get("why", ""))
        elif r == "E188-GB1" and "gamma_B" in v:
            g = v["gamma_B"]
            rd = (f"{_f(g['mean'], '+.5f')} [{_f(g['lo'], '+.5f')}, {_f(g['hi'], '+.5f')}] W a held B bit over {v['trains']}; SIZE M12 "
                  f"{v['size_M12']}; REPEAT {v['repeat_E186_GB']}")
        elif r == "E188-GA23" and "gamma_A" in v:
            g = v["gamma_A"]
            rd = (f"{_f(g['mean'], '+.5f')} [{_f(g['lo'], '+.5f')}, {_f(g['hi'], '+.5f')}] W a held A bit (AALL / 23); SIZE M12 "
                  f"{v['size_M12']}; REPEAT {v['repeat_E186_GA']}")
        elif r == "E188-BPOS" and "flat_q" in v:
            rd = f"Q {v['flat_q']['Q']:.2f} against {v['flat_q']['chi2_95']:.2f} at {v['flat_q']['df']} df"
        elif r == "E188-M":
            rd = (f"M12 Q {v['M12'].get('Q', float('nan')):.2f} ({v['M12']['word']}), M10 Q {v['M10'].get('Q', float('nan')):.2f} "
                  f"({v['M10']['word']}) over {v['M12'].get('n', 0)} trains" if v.get("M12", {}).get("n") else "no train scored")
        elif r == "E188-TR-N":
            rd = f"ratio {v.get('ratio'):.3f}" if "ratio" in v else v.get("why", "")
        elif r == "E188-LV":
            rd = (f"rms(D - M12) - rms(D - M10) {v['boot']['diff']:+.4f} [{v['boot']['lo95']:+.4f}, {v['boot']['hi95']:+.4f}] W"
                  if "boot" in v else v.get("why", ""))
        elif r == "E188-C":
            rd = f"kinds not all PASS {v.get('kinds_not_all_pass')}, trains {v.get('trains_not_all_pass')}"
        elif r == "E188-SCHED":
            rd = (f"{v.get('launches_paired')} of {v.get('launch_records')} launch records paired; not paired {v.get('trains_not_paired')}"
                  if v.get("trains_checked") else v.get("why", ""))
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
