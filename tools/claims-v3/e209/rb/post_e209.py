#!/usr/bin/env python3
"""E209 (Q202c, lane fix-e209, Tue 17 Nov 2026, before any E209 datum): step 13's check and readings beside the frozen scorer (E209.md,
amendment A1; verify-e209's findings 3, 5 and 6), never a verdict. Python's own modules; it imports the frozen scorer score_e209.py for its
h2h() and, in the self-test only, its own stand-in days.

    /usr/bin/python3 -I -B tools/claims-v3/e209/rb/post_e209.py labels RANBEFORE.json
    /usr/bin/python3 -I -B tools/claims-v3/e209/rb/post_e209.py after DATA.json SCORED.json --out POST.json
    /usr/bin/python3 -I -B tools/claims-v3/e209/rb/post_e209.py --selftest OUT.json

labels (A1 item 3): every entry of "ran_before_points" names a point of points-e209.json and every entry of "ran_before_cases" a time case
  of it: "LABELS OK" (exit 0); otherwise "LABELS REFUSED: ..." naming each entry that names nothing (exit 10), because the frozen scorer
  echoes such a label as applied and goes on scoring the point. The file's other keys (step 6n's dating) are not read.
after (A1 items 1 and 2), every figure REPORTED:
  NO DATA, NAMED: each point of points-e209.json that the frozen scorer leaves out of rules without naming it, unless labelled: no kept run
  (it did not run, or every run was set aside: the scorer's flags say why), kept runs but no time reading (no primary view: the governor held
  700 MHz, or 600-700 MHz, through the window), and a time reading but no energy reading (capped or thin: out of E1-E4, H4 and H6);
  THE DAY OFFSET (reading f): the mean of the day's kept anchor runs (role anchor; the primary view's dP_w and p_mean_w present, the run not
  capped, the view not thin) over the mean of E208's 27 anchor runs on this card read the same way, less 1, in W over idle, op time and the
  kernel clock; E208's runs from the three files rules-e209.json pins (MM1-v2's vendored a2c0-S1 and a2c0-S2, the a2c0-S1r data commit);
  H4n: H4 re-read with every measured J over idle (and W, at a watts point) divided by (1 + offset_W), with H4's ties, test and interval
  (score_e209.h2h, seed "E209|bootstrap|H4n"), printed on one line with H4's registered verdict; the cycle offsets beside H1-H3.
--selftest: the frozen scorer's own stand-in day A and variants of it (scored by score_e209.score, the predictors loaded as the scorer
  loads them), label files of step 6n's form, and E208's committed anchors; every answer stated before the run; "SELFTEST-POST-E209 <n> of
  <m> PASS" last.
Refuses (exit 4) unless points-e209.json, rules-e209.json, score_e209.py and E208's three anchor files are at their pinned sha256.
SPDX-License-Identifier: Apache-2.0
"""
import copy
import hashlib
import json
import math
import os
import statistics
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
E = os.path.normpath(os.path.join(HERE, ".."))
REPO = os.path.normpath(os.path.join(E, "..", "..", ".."))
SCORER_SHA = "e522919a5d399312e8e357e8aab22fc2c07e96f3e9f02e2ea2f3bd1a50e2e513"
POINTS_SHA = "cfdda741bcc8cbd8555ff21809f2897fae0f734b66727b108795cd138fb07261"
RULES_SHA = "0d7dfa791573cf00505143a0188dff7ad5e2ce6f95447c66fef89e9d5b8a62bb"
V2 = "tools/matmul/mm1/v2"
E208_ANCHOR_FILES = {"a2c0-S1": f"{V2}/inputs/e208/a2c0-S1__data-e208-a2c0-S1.json",
                     "a2c0-S2": f"{V2}/inputs/e208/a2c0-S2__data-e208-a2c0-S2.json",
                     "a2c0-S1r": "docs/reports/data/2026-11-17-e208-mmsweep-a2c0-S1r/data-e208-a2c0-S1r.json"}
E208_REF_REPORTED = {"n": 27, "dP_w": 18.355041}      # fix-e209's own count (scripts/e208_anchor_ref.py, written apart): the self-test's answer


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def pins():
    bad = []
    for rel, want in ((os.path.join(E, "points-e209.json"), POINTS_SHA), (os.path.join(E, "rules-e209.json"), RULES_SHA),
                      (os.path.join(E, "score_e209.py"), SCORER_SHA)):
        if sha(rel) != want:
            bad.append(os.path.basename(rel))
    R = json.load(open(os.path.join(E, "rules-e209.json")))
    for rel in E208_ANCHOR_FILES.values():
        if R["inputs_sha256"].get(rel) is None or sha(os.path.join(REPO, rel)) != R["inputs_sha256"][rel]:
            bad.append(rel)
    if bad:
        print(f"refused: not at the pinned sha256: {bad} (exit 4)")
        sys.exit(4)
    return R


def scorer():
    if E not in sys.path:
        sys.path.insert(0, E)
    import score_e209 as S  # noqa: E402  (the frozen scorer, pinned above; nothing of it runs at import)
    return S


def points():
    P = json.load(open(os.path.join(E, "points-e209.json")))
    return P, [p["id"] for p in P["points"]], {p["id"]: p for p in P["points"]}


# ------------------------------------------------------------------ labels
def check_labels(path):
    """-> (ok, words)"""
    P, ids, _ = points()
    cases = set(P["time_cases"])
    try:
        L = json.load(open(path))
    except Exception as e:  # noqa: BLE001
        return False, f"LABELS REFUSED: {os.path.basename(path)} is not a JSON object ({type(e).__name__})"
    if not isinstance(L, dict):
        return False, "LABELS REFUSED: the labels file is not a JSON object"
    bad = []
    for key, known in (("ran_before_points", set(ids)), ("ran_before_cases", cases)):
        v = L.get(key) or []
        if not isinstance(v, list):
            bad.append(f"{key} is not a list")
            continue
        for x in v:
            if not isinstance(x, str) or x not in known:
                bad.append(f"{key} entry {x!r} names no {'point' if key == 'ran_before_points' else 'time case'} of points-e209.json")
    if bad:
        return False, "LABELS REFUSED: " + "; ".join(bad)
    n_p, n_c = len(L.get("ran_before_points") or []), len(L.get("ran_before_cases") or [])
    return True, f"LABELS OK: {n_p} point label(s), {n_c} time-case label(s), each naming a point or a time case of points-e209.json"


# ------------------------------------------------------------------ after the scorer
def kept_anchor(r):
    v = (r.get("views") or {}).get(r.get("primary_view")) or {}
    if r.get("role") == "anchor" and v.get("dP_w") is not None and v.get("p_mean_w") and not r.get("capped") and not v.get("thin"):
        return (float(v["dP_w"]), v.get("T_op_us"), v.get("kclock_mhz"))
    return None


def e208_anchors():
    out = []
    for rel in E208_ANCHOR_FILES.values():
        for r in json.load(open(os.path.join(REPO, rel)))["runs"]:
            a = kept_anchor(r)
            if a:
                out.append(a)
    return out


def day_offset(datas):
    day = [a for D in datas for r in (D.get("runs") or []) for a in [kept_anchor(r)] if a]
    ref = e208_anchors()
    o = {"day_anchor_runs_kept": len(day), "e208_anchor_runs": len(ref)}
    for k, name in ((0, "W_over_idle"), (1, "T_op_us"), (2, "kclock_mhz")):
        dv = [x[k] for x in day if x[k] is not None]
        rv = [x[k] for x in ref if x[k] is not None]
        o[name] = {"day_mean": statistics.mean(dv) if dv else None, "e208_mean": statistics.mean(rv) if rv else None,
                   "offset": (statistics.mean(dv) / statistics.mean(rv) - 1.0) if (dv and rv) else None,
                   "day_runs": dv}
    return o


def h4n(S, R, P, scored, off, seed="E209|bootstrap|H4n"):
    """H4 re-read on J over idle (W at a watts point) divided by (1 + off): the scorer's rows_energy for H4, then its h2h"""
    rows = []
    for pid, x in scored.get("points", {}).items():
        if x.get("n_energy", 0) == 0:
            continue
        fam = P[pid]["family"]
        v2s, v1 = x.get("v2_e"), x.get("v1_e")
        ot = ((v1 or {}).get("J_given"), (v1 or {}).get("W_given")) if v1 else None
        if not v2s or not ot or ot[0] is None:
            rows.append({"id": pid, "d": None, "watts": x["watts"], "family": fam})
            continue
        if x["watts"]:
            mW = x["meas"]["W"] / (1.0 + off)
            rows.append({"id": pid, "d": abs(mW - ot[1]) - abs(mW - v2s["W_given"]), "watts": True, "family": fam})
        else:
            m = x["meas"]["J_over"] / (1.0 + off)
            a, b = S.ln_ratio(m, v2s["J_given"]), S.ln_ratio(m, ot[0])
            rows.append({"id": pid, "d": (abs(b) - abs(a)) if (a is not None and b is not None) else None, "watts": False, "family": fam})
    H = R["head_to_head"]
    return S.h2h(rows, H["tie_ln"]["joules"], H["tie_w"], "MM1-v1", "H4n", H["min_untied"], H["alpha"], H["rules"]["H4"]["decision"], seed)


def after(datas, scored, S=None, R=None):
    R = R or pins()
    S = S or scorer()
    P, ids, PP = points()
    F = scored.get("points", {})
    lab = set((scored.get("labels_applied") or {}).get("ran_before_points") or [])
    flags = scored.get("flags", {})
    nd = {"no_kept_run": [{"id": p, "why": (flags.get(p) or {}).get("set_aside") or ["no run of it in the data"]} for p in ids
                          if p not in F and p not in lab],
          "kept_runs_no_time_reading": [p for p in ids if p in F and F[p].get("n_time", 0) == 0],
          "time_reading_no_energy_reading": [p for p in ids if p in F and F[p].get("n_time", 0) > 0 and F[p].get("n_energy", 0) == 0]}
    off = day_offset(datas)
    ow = off["W_over_idle"]["offset"]
    hh = scored.get("head_to_head", {})
    out = {"experiment": "E209", "what": "step 13's readings beside the frozen scorer (E209.md A1): REPORTED, never verdicts",
           "labels_applied": scored.get("labels_applied"), "no_data_named": nd, "day_offset_reading_f": off,
           "H1_H3_registered": {h: (hh.get(h) or {}).get("verdict") for h in ("H1", "H2", "H3")},
           "H4_registered": (hh.get("H4") or {}).get("verdict")}
    out["H4n_REPORTED"] = h4n(S, R, PP, scored, ow) if ow is not None else {"verdict": "NO DATA (no kept anchor run: the day offset is not read)"}
    return out


def after_text(o):
    nd, off = o["no_data_named"], o["day_offset_reading_f"]
    pct = lambda x: "n/a" if x is None else f"{x * 100:+.3f}%"  # noqa: E731
    lines = ["E209 step 13 readings beside the frozen scorer (E209.md A1; REPORTED, never verdicts)",
             "NO DATA, named: no kept run: " + (", ".join(f"{x['id']} ({'; '.join(x['why'])})" for x in nd["no_kept_run"]) or "none")
             + "; kept runs but no time reading (no window view): " + (", ".join(nd["kept_runs_no_time_reading"]) or "none")
             + "; a time reading but no energy reading: " + (", ".join(nd["time_reading_no_energy_reading"]) or "none"),
             f"THE DAY OFFSET (reading f; {off['day_anchor_runs_kept']} kept anchor runs of the day against E208's {off['e208_anchor_runs']}): "
             f"W over idle {pct(off['W_over_idle']['offset'])}, op time {pct(off['T_op_us']['offset'])}, clock {pct(off['kclock_mhz']['offset'])}",
             f"H4 (registered) {o['H4_registered']}; offset_W {pct(off['W_over_idle']['offset'])}; H4n (REPORTED, J over idle / (1 + offset_W)) "
             f"{o['H4n_REPORTED'].get('verdict')}"
             + (f" (v2 closer {o['H4n_REPORTED']['v2_closer']}, v1 closer {o['H4n_REPORTED']['other_closer']}, ties {o['H4n_REPORTED']['ties']}; "
                f"mean d 95% {[round(v, 5) for v in o['H4n_REPORTED']['bootstrap_mean_d']['mean_95']]})"
                if o["H4n_REPORTED"].get("bootstrap_mean_d") else ""),
             f"H1-H3 (registered) {o['H1_H3_registered']}; beside them the op-time offset {pct(off['T_op_us']['offset'])} and the clock offset "
             f"{pct(off['kclock_mhz']['offset'])}"]
    return "\n".join(lines) + "\n"


# ------------------------------------------------------------------ self-test
def selftest(outp):
    import tempfile
    R = pins()
    S = scorer()
    P, ids, PP = points()
    rows, res = [], {}

    def row(words, ok, detail=""):
        rows.append(bool(ok))
        print(f"{'PASS' if ok else 'FAIL'} {words}" + (f" [{detail}]" if detail != "" else ""), flush=True)
        res[words.split(" ")[0]] = {"ok": bool(ok), "detail": str(detail)[:300]}

    tmp = tempfile.mkdtemp(prefix="post-e209-")

    def lab(obj, name):
        p = os.path.join(tmp, name)
        open(p, "w").write(obj if isinstance(obj, str) else json.dumps(obj))
        return check_labels(p)
    ok, w = lab({"ran_before_points": ["e01"], "ran_before_cases": ["gemmL1x3x2|int8|0xffffffff"], "after_freeze_REPORTED": [],
                 "searched_REPORTED": "step 6n's dating"}, "l1.json")
    row("L1 labels of step 6n's form naming e01 and its time case: LABELS OK", ok and w.startswith("LABELS OK"), w)
    ok, w = lab({"ran_before_points": ["e1"], "ran_before_cases": []}, "l2.json")
    row("L2 a point label 'e1' (a typo for e01): LABELS REFUSED naming it", not ok and "'e1'" in w, w)
    ok, w = lab({"ran_before_points": [], "ran_before_cases": ["gemmL1x3x2|int8|0xFFFFFFFF"]}, "l3.json")
    row("L3 a case label spelled 0xFFFFFFFF: LABELS REFUSED naming it", not ok and "0xFFFFFFFF" in w, w)
    ok, w = lab({"ran_before_points": [], "ran_before_cases": []}, "l4.json")
    row("L4 empty labels: LABELS OK, nothing to pass", ok and "0 point label(s), 0 time-case label(s)" in w, w)
    ok, w = lab({"ran_before_points": "e01"}, "l5.json")
    row("L5 a point label given as a string, not a list: LABELS REFUSED", not ok and "not a list" in w, w)
    ok, w = lab("{not json", "l6.json")
    row("L6 a labels file that is not JSON: LABELS REFUSED", not ok and "not a JSON object" in w, w)
    # the frozen scorer's own day A, scored as the scorer scores it (the predictors loaded as it loads them)
    FZ = S.load_frozen()
    A = S.standin_data(FZ, "A")
    got = S.score(copy.deepcopy(A), FZ, {"ran_before_points": ["e1"], "ran_before_cases": []})
    row("L7 why the check: the frozen scorer given 'e1' echoes it as applied and still scores e01",
        got["labels_applied"]["ran_before_points"] == ["e1"] and "e01" in got["points"], got["labels_applied"])
    # day A with energy-read anchors (p_mean_w added: the stand-in's anchors carry dP_w 18.4 W, T_op 2.18 us, 799.1 MHz)
    A2 = copy.deepcopy(A)
    for r in A2[0]["runs"]:
        if r.get("role") == "anchor":
            r["views"]["win"]["p_mean_w"] = 41.6
    sA = S.score(copy.deepcopy(A2), FZ)
    ref = e208_anchors()
    rw = statistics.mean(x[0] for x in ref)
    row("D1 E208's anchor runs on this card read as rules_e209.py reads them: 27 runs, W over idle mean 18.355041 W (fix-e209's own count)",
        len(ref) == E208_REF_REPORTED["n"] and abs(rw - E208_REF_REPORTED["dP_w"]) < 5e-7, f"{len(ref)} runs, {rw:.6f} W")
    o = after(A2, sA, S, R)
    want = 18.4 / rw - 1.0
    got_o = o["day_offset_reading_f"]["W_over_idle"]["offset"]
    row("D2 day A's five anchors at 18.4 W: offset_W = 18.4 / E208's mean - 1 (stated before the run), op time and clock offsets beside",
        o["day_offset_reading_f"]["day_anchor_runs_kept"] == 5 and got_o is not None and abs(got_o - want) < 1e-12
        and o["day_offset_reading_f"]["T_op_us"]["offset"] is not None, f"{got_o * 100:+.4f}% (stated {want * 100:+.4f}%)")
    seed_h4 = h4n(S, R, PP, sA, 0.0, seed="E209|bootstrap|H4")
    h4 = sA["head_to_head"]["H4"]
    row("D3 at offset 0 and H4's own seed, H4n is the scorer's H4 exactly (cells, counts, verdict, interval): the rows are the scorer's",
        seed_h4["cells"] == h4["cells"] and seed_h4["verdict"] == h4["verdict"] and seed_h4["bootstrap_mean_d"] == h4["bootstrap_mean_d"]
        and (seed_h4["v2_closer"], seed_h4["other_closer"], seed_h4["ties"]) == (h4["v2_closer"], h4["other_closer"], h4["ties"]),
        f"{h4['verdict']}: {h4['v2_closer']}/{h4['other_closer']}/{h4['ties']}")
    row("D4 day A: no point named NO DATA (every point has a time and an energy reading)",
        o["no_data_named"] == {"no_kept_run": [], "kept_runs_no_time_reading": [], "time_reading_no_energy_reading": []}, o["no_data_named"])
    # the day's level moved: every measured W and J over idle of day A times 1.02, and the anchors at E208's mean times 1.02: the scorer's
    # H4 then reads the measurement 2% high; H4n takes the 2% back out and reads day A's own H4 cells
    A3 = copy.deepcopy(A2)
    for r in A3[0]["runs"]:
        v = r["views"].get(r.get("primary_view")) or {}
        if r.get("role") == "anchor":
            v["dP_w"] = rw * 1.02
        elif r.get("role") == "arm" and v.get("dP_w") is not None:
            for k in ("dP_w", "J_pass_over"):
                v[k] = v[k] * 1.02
            v["p_mean_w"] = v["p_mean_w"] + v["dP_w"] / 1.02 * 0.02
            v["J_pass_with"] = v["p_mean_w"] * v["t_pass_s"]
    s3 = S.score(copy.deepcopy(A3), FZ)
    o3 = after(A3, s3, S, R)
    w3 = o3["day_offset_reading_f"]["W_over_idle"]["offset"]
    n3 = o3["H4n_REPORTED"]
    same = sum(1 for k, v in n3["cells"].items() if h4["cells"].get(k) == v)
    row("D5 every W and J over idle 2% over day A, the anchors at E208's mean x 1.02: offset_W = +2%; H4n's cells are day A's H4 cells at "
        "every point, while the scorer's H4 reads the raised day", abs(w3 - 0.02) < 1e-12 and same == len(h4["cells"])
        and n3["verdict"] == h4["verdict"], f"offset {w3 * 100:+.3f}%; H4 {s3['head_to_head']['H4']['verdict']} "
        f"({s3['head_to_head']['H4']['v2_closer']}/{s3['head_to_head']['H4']['other_closer']}/{s3['head_to_head']['H4']['ties']}); "
        f"H4n {n3['verdict']} ({n3['v2_closer']}/{n3['other_closer']}/{n3['ties']}); {same} of {len(h4['cells'])} cells as day A's")
    # a point whose only kept run has no window view (held at 700 MHz): verify-e209's attack S3
    A4 = copy.deepcopy(A2)
    for r in A4[0]["runs"]:
        if r.get("arm") == "e02":
            r["views"] = {"burst": r["views"].get("burst", {"kclock_mhz": 700.0})}
            r["frac_800_after_step"] = 0.0
            r["capped"] = True
    s4 = S.score(copy.deepcopy(A4), FZ)
    o4 = after(A4, s4, S, R)
    in_rules = any("e02" in (s4["rules"][k].get("cells") or {}) for k in s4["rules"]) or \
        any(tc for tc, c in s4["cases"].items() if "e02" in c["members"])
    row("N1 e02's run with no window view: the scorer names it in no rule; step 13 names it NO DATA (kept runs, no time reading)",
        not in_rules and o4["no_data_named"]["kept_runs_no_time_reading"] == ["e02"], o4["no_data_named"])
    A5 = copy.deepcopy(A2)
    A5[0]["runs"] = [r for r in A5[0]["runs"] if r.get("arm") != "e03"]
    for r in A5[0]["runs"]:
        if r.get("arm") == "e04":
            r["shires"] = "0xffff0000"
    s5 = S.score(copy.deepcopy(A5), FZ)
    o5 = after(A5, s5, S, R)
    nk = {x["id"]: x["why"] for x in o5["no_data_named"]["no_kept_run"]}
    row("N2 e03 never in the data and e04's only run set aside (another mask): both named NO DATA, no kept run, with the scorer's reason",
        sorted(nk) == ["e03", "e04"] and any("mask" in w for w in nk["e04"]), nk)
    A6 = copy.deepcopy(A2)
    for r in A6[0]["runs"]:
        if r.get("arm") == "e10":
            r["capped"] = True
    s6 = S.score(copy.deepcopy(A6), FZ)
    o6 = after(A6, s6, S, R)
    row("N3 e10 capped (its time read, no energy): named, a time reading but no energy reading",
        o6["no_data_named"]["time_reading_no_energy_reading"] == ["e10"], o6["no_data_named"])
    sQ = S.score(copy.deepcopy(A2), FZ, {"ran_before_points": ["e01"], "ran_before_cases": []})
    oQ = after(A2, sQ, S, R)
    row("N4 e01 labelled 'ran before': out of the NO DATA lists (the label names it)", all("e01" not in str(v) for v in oQ["no_data_named"].values()),
        oQ["no_data_named"])
    A7 = copy.deepcopy(A)
    s7 = S.score(copy.deepcopy(A7), FZ)
    o7 = after(A7, s7, S, R)
    row("N5 anchors with no energy reading (the stand-in's own: no p_mean_w): the day offset not read, H4n NO DATA, said so",
        o7["day_offset_reading_f"]["W_over_idle"]["offset"] is None and o7["H4n_REPORTED"]["verdict"].startswith("NO DATA"), o7["H4n_REPORTED"]["verdict"])
    txt = after_text(o3)
    row("T1 the printed lines: H4's registered verdict, offset_W and H4n on one line", any(ln.startswith("H4 (registered)") and "offset_W" in ln
        and "H4n" in ln for ln in txt.splitlines()), txt.splitlines()[3][:160])
    res["_summary"] = f"SELFTEST-POST-E209 {sum(rows)} of {len(rows)} {'PASS' if all(rows) else 'FAIL'}"
    json.dump(res, open(outp, "w"), indent=1, sort_keys=True)
    print(res["_summary"])
    return 0 if all(rows) else 1


def main(argv):
    if argv[:1] == ["labels"] and len(argv) == 2:
        pins()
        ok, w = check_labels(argv[1])
        print(w)
        return 0 if ok else 10
    if argv[:1] == ["after"] and len(argv) == 5 and argv[3] == "--out":
        R = pins()
        o = after([json.load(open(argv[1]))], json.load(open(argv[2])), scorer(), R)
        json.dump(o, open(argv[4], "w"), indent=1, sort_keys=True)
        sys.stdout.write(after_text(o))
        return 0
    if argv[:1] == ["--selftest"] and len(argv) == 2:
        return selftest(argv[1])
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
