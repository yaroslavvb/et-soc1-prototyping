#!/usr/bin/env python3
"""E196's kit (Q185, lane kit-e196, Sun 15 Nov 2026, PST, before any E196 datum): THE CHECKER OF E196.md SECTION 8, run by step 13 after
the data commit, after the registered reduction (reduce_e196.py OUT --readback-none-ok, unchanged). It reads the reduction's JSON and the
session's own records, and writes each registered sanity check with its numbers beside the prices. A check that fails removes no datum
(E196.md section 8). NO SCORING: no forecast number is read or written here (the forecast is sealed: E196.md section 0).

  1 THE TIES: REPRODUCES when |E196's mean - the reference| <= E196's 95 % half-width + the reference's published half-width, else
    DIFFERS (both numbers); NOT COMPUTED with fewer than two kept passes (no standard error). The pairs and references are E196.md's
    (E78, E65, E109), written below as registered. tie_b_sign_D_W's DIFFERS is reported as the transfer's size, never a failure.
  2 THE MSK BIT ALONE: EQUAL when the 95 % interval of derived.msk_null_I.H.mFFFF_minus_I.H.full_pJ_per_op contains 0, else DIFFERS,
    with it and arms.I.H.mFFFF.D_W; both arms' mean cycles per op (kept runs) reported, "at unequal rate" when they differ by > 0.5.
  3 THE HELD LADDER'S MIDDLE STEPS: STRAIGHT when the 95 % interval of derived.held_ladder_middle_step_ratio contains 1.0, else BENT,
    with the two steps.
  4 THE READ-BACKS: PASS when every X14CHECK record of the session is ok, with the count (108 at the full plan: the smoke's premise runs 8,
    its two T1 processes 4, the 48 train processes 96), else FAIL naming each; the pass runs' read-backs "not made" (the lab's host).
  5 CYCLES PER OP: PASS when every kept run's mean cycles per op (launches 0 and after) and every train launch's rounds to 546.0 or 544.0
    at one decimal (within 0.05 cycles) as its mask gives; else REPORTED with each deviation.
  6 THE TRAINS' ANCHORS AND CARRY-OVER: AGREE when |trains.Tn.anchor_drift_W| <= 0.3 W, else DIFFER; the carry-over (E196.md 8.6): the
    reduction's own launch reading (its dip rule; kept board samples in [start + 170 ms, end], at least 2), per complete quad of each
    valid process L2 - L3; per unit (one SFFS and one FSSF process) the SFFS value less the FSSF value; mean over units with its 95 %
    interval (t over units): REPORTED.
  Also reported: samples off 600 MHz; runs set aside and why; passes kept (5 or more for a result that is not provisional); dips dropped;
  runs off the approach protocol; readback_gate's count against the session's unchanged-host runs; host outputs the runner could not read.
    python3 -I -B check_e196.py <session run dir> <x14-e196.json> [--out checks-e196.json]
Prints the checks and "CHECKS-E196: ..." last; exit 0 (any verdict), 2 on a usage error. Standard library only.
SPDX-License-Identifier: Apache-2.0
"""
import argparse
import bisect
import json
import math
import os
import statistics as st

T975 = {1: 12.706, 2: 4.303, 3: 3.182, 4: 2.776, 5: 2.571, 6: 2.447, 7: 2.365, 8: 2.306, 9: 2.262, 10: 2.228, 11: 2.201,
        12: 2.179, 13: 2.160, 14: 2.145, 15: 2.131, 16: 2.120, 17: 2.110, 18: 2.101, 19: 2.093, 20: 2.086}
# E196.md section 8.1, registered: (where in x14-e196.json, the reference's mean, its published 95 % half-width, the source)
TIES = [("derived.tie_zeros_S_W", 1.986, 0.059, "E78 fp32 zeros S over idle"),
        ("derived.tie_random_D_W", 24.725, 0.082, "E78 randn D"),
        ("derived.tie_ones_D_W", 8.257, 0.221, "E78 ones D"),
        ("derived.tie_sparse50_D_W", 7.302, 0.063, "E78 sparse50 D"),
        ("derived.tie_a_zero_D_W", 0.810, 0.065, "E78 a_zeros_b_randn D"),
        ("derived.tie_pi_S_W", 10.398, 0.080, "E78 built-in pi S over idle"),
        ("derived.tie_b_sign_D_W", 0.563, 0.024, "E65 bit 31 (a DIFFERS is the transfer's size, never a failure)"),
        ("arms.I.Z.m0000.S_W", 0.376, 0.089, "E109 fp32 loop, no micro-op issued (three passes, labelled there)")]


def jl(p):
    out = []
    if os.path.exists(p):
        for ln in open(p, errors="ignore"):
            ln = ln.strip()
            if ln.startswith("{") and ln.endswith("}"):
                try:
                    out.append(json.loads(ln))
                except ValueError:
                    pass
    return out


def dig(d, path):
    cur = d
    for k in path.split(".", 1)[0:1] + ([path.split(".", 1)[1]] if "." in path else []):
        if not isinstance(cur, dict):
            return None
        cur = cur.get(k)
    return cur


def get(res, key):
    """derived.<name> or arms.<arm>.<field> (arm names hold dots)"""
    if key.startswith("derived."):
        return res.get("derived", {}).get(key[len("derived."):])
    if key.startswith("arms."):
        rest = key[len("arms."):]
        arm, field = rest.rsplit(".", 1)
        return res.get("arms", {}).get(arm, {}).get(field)
    return None


def half(s):
    if not isinstance(s, dict) or "ci95" not in s:
        return None
    return (s["ci95"][1] - s["ci95"][0]) / 2.0


def expected_cycles(mask):
    return 546.0 if mask in (None, "none") or int(mask, 16) & 0xFFFF == 0xFFFF else 544.0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("run")
    ap.add_argument("x14")
    ap.add_argument("--out", default=None)
    a = ap.parse_args()
    res = json.load(open(a.x14))
    gen = os.path.join(a.run, "gen", "arms.json")
    table = {x["name"]: x for x in json.load(open(gen))["arms"]}
    runs, trecs, checks, marks = (jl(os.path.join(a.run, f)) for f in ("runs.jsonl", "train.jsonl", "checks.jsonl", "marks.jsonl"))
    tel = jl(os.path.join(a.run, "telemetry.jsonl"))
    out = {"checker": "check_e196.py (kit-e196), E196.md section 8", "checks": [], "reported": {}}
    words = []
    # 1 the ties
    ties, nrep, ncomp = [], 0, 0
    for key, ref, rh, src in TIES:
        s = get(res, key)
        h = half(s)
        if not isinstance(s, dict) or h is None:
            ties.append({"pair": key, "reference": ref, "reference_half_width": rh, "source": src, "reading": "NOT COMPUTED",
                         "e196": s})
            continue
        ncomp += 1
        rd = "REPRODUCES" if abs(s["mean"] - ref) <= h + rh else "DIFFERS"
        nrep += rd == "REPRODUCES"
        ties.append({"pair": key, "e196_mean": s["mean"], "e196_half_width": h, "reference": ref, "reference_half_width": rh,
                     "source": src, "reading": rd, "difference": s["mean"] - ref})
    out["checks"].append({"n": 1, "name": "the ties", "pairs": ties})
    words.append("1 %d of %d REPRODUCE (%d not computed)" % (nrep, ncomp, len(TIES) - ncomp))
    # kept runs and their cycles (the reduction's own sets: its kept passes, its set-aside runs)
    kept = {p["pass"] for p in res.get("passes", []) if p.get("kept")}
    aside = {(r.get("pass"), r.get("seq")) for r in res.get("set_aside", [])}
    byrun = {}
    for r in runs:
        if r.get("role") in ("arm", "anchor_first", "anchor_last") and r.get("pass") in kept and (r["pass"], r["seq"]) not in aside:
            byrun.setdefault((r["pass"], r["seq"]), []).append(r)
    cpo = {}
    for k, rs in byrun.items():
        v = [x["cycles_per_op"] for x in rs if x.get("launch", 0) >= 0] or [x["cycles_per_op"] for x in rs]
        cpo[k] = (rs[0]["arm"], sum(v) / len(v))
    # 2 the MSK bit alone
    m = get(res, "derived.msk_null_I.H.mFFFF_minus_I.H.full_pJ_per_op")
    c_f = [v for (arm, v) in cpo.values() if arm == "I.H.mFFFF"]
    c_u = [v for (arm, v) in cpo.values() if arm == "I.H.full"]
    mc = (sum(c_f) / len(c_f) if c_f else None, sum(c_u) / len(c_u) if c_u else None)
    if isinstance(m, dict) and "ci95" in m:
        rd = "EQUAL" if m["ci95"][0] <= 0.0 <= m["ci95"][1] else "DIFFERS"
    else:
        rd = "NOT COMPUTED"
    unequal = None not in mc and abs(mc[0] - mc[1]) > 0.5
    out["checks"].append({"n": 2, "name": "the MSK bit alone", "reading": rd, "msk_null_pJ_per_op": m,
                          "I.H.mFFFF_D_W": get(res, "arms.I.H.mFFFF.D_W"), "cycles_per_op_mFFFF_full": mc,
                          "at_unequal_rate": unequal})
    words.append("2 %s%s" % (rd, " (at unequal rate)" if unequal else ""))
    # 3 the held ladder's middle steps
    r3 = get(res, "derived.held_ladder_middle_step_ratio")
    if isinstance(r3, dict) and "ci95" in r3:
        rd = "STRAIGHT" if r3["ci95"][0] <= 1.0 <= r3["ci95"][1] else "BENT"
    else:
        rd = "NOT COMPUTED"
    out["checks"].append({"n": 3, "name": "the held ladder's middle steps", "reading": rd, "ratio": r3,
                          "step_4_to_8": get(res, "derived.ladder_H_step_I.H.m000F_to_I.H.m00FF_W"),
                          "step_8_to_12": get(res, "derived.ladder_H_step_I.H.m00FF_to_I.H.m0FFF_W")})
    words.append("3 %s" % rd)
    # 4 the read-backs
    bad4 = [{"arm": c.get("arm"), "train": c.get("train"), "process": c.get("process"), "after_launch": c.get("after_launch"),
             "zero_rows_bad": c.get("zero_rows_bad"), "live_rows_zero": c.get("live_rows_zero")} for c in checks if not c.get("ok")]
    rd = "PASS" if checks and not bad4 else "FAIL"
    out["checks"].append({"n": 4, "name": "the read-backs", "reading": rd, "x14check_records": len(checks), "not_ok": bad4,
                          "at_full_plan": 108, "pass_runs": "not made (the lab's unchanged host reads no C back on file tiles)"})
    words.append("4 %s (%d of %d ok; 108 at the full plan)" % (rd, len(checks) - len(bad4), len(checks)))
    # 5 cycles per op
    dev = []
    for (p, seq), (arm, v) in sorted(cpo.items()):
        w = expected_cycles(table[arm]["row_mask"])
        if abs(v - w) > 0.05:
            dev.append({"pass": p, "seq": seq, "arm": arm, "cycles_per_op": v, "expected": w})
    ntl = 0
    for r in trecs:
        if r.get("role") != "train":
            continue
        ntl += 1
        w = expected_cycles(r.get("row_mask"))
        if abs(r["cycles_per_op"] - w) > 0.05:
            dev.append({"train": r.get("train"), "process": r.get("process"), "launch": r.get("launch"), "cycles_per_op": r["cycles_per_op"],
                        "expected": w})
    rd = "PASS" if (cpo or ntl) and not dev else ("REPORTED" if dev else "NOT COMPUTED")
    out["checks"].append({"n": 5, "name": "cycles per op", "reading": rd, "kept_runs": len(cpo), "train_launches": ntl,
                          "deviations": dev[:200], "n_deviations": len(dev)})
    words.append("5 %s (%d kept runs, %d train launches, %d deviations)" % (rd, len(cpo), ntl, len(dev)))
    # 6 the trains' anchors and carry-over (with the reduction's own launch reading)
    tel.sort(key=lambda s: s.get("t_ms", 0))
    bw = [s.get("board_w") for s in tel]
    keep = []
    for i, s in enumerate(tel):
        w = bw[i]
        if not isinstance(w, (int, float)):
            continue
        if 2 <= i < len(tel) - 2 and isinstance(bw[i - 2], (int, float)) and isinstance(bw[i + 2], (int, float)) \
                and w < min(bw[i - 2], bw[i + 2]) - 4.0:
            continue
        keep.append(s)
    T = [s["t_ms"] / 1000.0 for s in keep]

    def window(t0, t1):
        return keep[bisect.bisect_left(T, t0):bisect.bisect_left(T, t1)]
    stop_t = []
    sp = os.path.join(a.run, "STOP")
    if os.path.exists(sp):
        try:
            stop_t.append(json.loads(open(sp).readline())["t_ms"] / 1000.0)
        except (ValueError, KeyError, TypeError):
            stop_t.append(os.path.getmtime(sp))
    six = []
    for name in ("T1", "T2"):
        tr = res.get("trains", {}).get(name, {})
        drift = tr.get("anchor_drift_W")
        agree = None if drift is None else ("AGREE" if abs(drift) <= 0.3 else "DIFFER")
        procs = {}
        for r in trecs:
            if r.get("train") == name and r.get("role") == "train":
                procs.setdefault(r["process"], []).append(r)
        tchk = {}
        for c in checks:
            if c.get("train") == name and c.get("role") == "train":
                tchk.setdefault(c["process"], []).append(c)
        cval = {}
        for k, rs in sorted(procs.items()):
            rs.sort(key=lambda r: r["launch"])
            order = rs[0].get("order")
            want = [order[0], order[0]] + [order[(n - 1) % 4] for n in range(1, len(rs) - 1)]
            t0, t1 = rs[0]["t_start_ms"] / 1000.0, rs[-1]["t_end_ms"] / 1000.0
            cs = tchk.get(k, [])
            if [r["kind"] for r in rs] != want or not all(r.get("ok") for r in rs) or len(cs) < 2 or \
                    not all(c.get("ok") for c in cs) or any(t0 <= x <= t1 + 1.0 for x in stop_t):
                continue
            L = {}
            for r in rs:
                if r["launch"] < 1:
                    continue
                w = [s["board_w"] for s in window(r["t_start_ms"] / 1000.0 + 0.17, r["t_end_ms"] / 1000.0 + 1e-6)]
                if len(w) >= 2:
                    L[r["launch"]] = sum(w) / len(w)
            qs = [L[4 * q + 2] - L[4 * q + 3] for q in range(3) if all((4 * q + j) in L for j in (1, 2, 3, 4))]
            if qs:
                cval[k] = (order, sum(qs) / len(qs))
        units = []
        for j in range(0, max(list(procs) + [0]) + 1, 2):
            if j in cval and j + 1 in cval and cval[j][0] == "SFFS" and cval[j + 1][0] == "FSSF":
                units.append(cval[j][1] - cval[j + 1][1])
        if len(units) >= 2:
            mu = sum(units) / len(units)
            se = st.stdev(units) / math.sqrt(len(units))
            t = T975.get(len(units) - 1, 2.0)
            carry = {"mean_W": mu, "ci95_W": [mu - t * se, mu + t * se], "units": len(units)}
        else:
            carry = {"units": len(units), "reading": "NOT COMPUTED"}
        six.append({"train": name, "anchor_drift_W": drift, "reading": agree or "NOT COMPUTED", "carry_over_L2_minus_L3": carry,
                    "carry_over_reading": "REPORTED"})
    out["checks"].append({"n": 6, "name": "the trains' anchors and carry-over", "trains": six})
    words.append("6 %s" % " ".join("%s %s" % (x["train"], x["reading"]) for x in six))
    # also reported
    off = sum(1 for s in tel if int(s.get("mhz", {}).get("minion", 0)) != 600)
    aside_why = {}
    for r in res.get("set_aside", []):
        for g in r.get("gates_failed", []):
            aside_why[g.split(" ")[0] + " " + (g.split(" ")[1] if " " in g else "")] = aside_why.get(g.split(" ")[0] + " " + (g.split(" ")[1] if " " in g else ""), 0) + 1
    offp = sum(1 for r in runs if r.get("role") in ("arm", "anchor_first", "anchor_last") and r.get("launch") == -1
               and not r.get("approach", {}).get("on_protocol", True))
    lab_runs = len({(r["pass"], r["seq"]) for r in runs if r.get("readback") == "none" and r.get("role") in
                    ("arm", "anchor_first", "anchor_last", "train_anchor_first", "train_anchor_last")})
    unread = [m.get("what") for m in marks if m.get("kind") == "host_lines" and m.get("written") is False]
    rtl = sum(len(m.get("runtime_lines") or []) for m in marks if m.get("kind") == "host_lines")
    out["reported"] = {"samples_off_600_MHz": off, "samples": len(tel), "runs_set_aside": len(res.get("set_aside", [])),
                       "set_aside_reasons": aside_why, "passes_kept": sorted(kept), "passes_kept_n": len(kept),
                       "provisional": len(kept) < 5, "dips_dropped": res.get("dips_dropped"), "runs_off_protocol": offp,
                       "readback_gate_exempt": (res.get("readback_gate") or {}).get("exempt_runs"),
                       "unchanged_host_runs_in_records": lab_runs, "unreadable_host_outputs": unread,
                       "runtime_lines_dropped": rtl}
    words.append("reported: %d passes kept%s; %d runs set aside; %d dips; %d samples off 600 MHz; readback_gate %s of %d "
                 "unchanged-host runs; %d unreadable host outputs" % (
                     len(kept), " (provisional)" if len(kept) < 5 else "", len(res.get("set_aside", [])),
                     res.get("dips_dropped") or 0, off, out["reported"]["readback_gate_exempt"], lab_runs, len(unread)))
    js = json.dumps(out, indent=1)
    if a.out:
        open(a.out, "w").write(js + "\n")
    for c in out["checks"]:
        print("check %d (%s): %s" % (c["n"], c["name"], c.get("reading") or ", ".join(
            "%s %s" % (x.get("pair", x.get("train")), x.get("reading")) for x in c.get("pairs", c.get("trains", [])))))
    print("CHECKS-E196: " + "; ".join(words))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
