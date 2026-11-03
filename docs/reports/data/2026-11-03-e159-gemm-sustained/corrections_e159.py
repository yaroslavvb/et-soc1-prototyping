#!/usr/bin/env python3
"""E159, corrections after verification (Tue 3 Nov 2026, post hoc, labelled). Desk only: it reads committed files and opens no device.
It changes no registered number or verdict: results.json (reduce_e159.py's registered reduction) and posthoc.json are read, never written.

    /usr/bin/python3 corrections_e159.py > corrections.txt      (writes corrections.json)

Every number the README's dated notes and its "Corrections after verification" section quote is printed here:

  C1  H1 fp32 random's clock miss: what G3 says given the hold's first second, and where the window's samples under 800 MHz fall;
  C2  H1's first-second deficit against P0 and its cold start: the start dies of the bursts behind P0 (E136's, E146's), the board's slope
      on the die inside H1 at 800 MHz, and the part of the deficit a start-die term carries, two ways;
  C3  E159's blind rms beside Q139(q)'s nested figures, over its 56 GEMM-pattern runs and over its 14 large GEMMs;
  C4  the numbers on record before the run for H2 and H3 fp32 random (the frozen nominal clocks) beside the registered primary;
  C5  zeros: the sign of G3's board error, the registered attribution, and the error given the first second;
  C6  the session's sptrace copies and residency attempts, per-run and at session start and end;
  C7  the sessions' predictions_sha256_here and protocol hashes, and queue_e159.py's docstring for the board stop test.
"""
import gzip
import hashlib
import json
import os
import statistics as st
import subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
LAB = os.path.normpath(os.path.join(HERE, "..", "..", "..", ".."))
DATA = os.path.join(LAB, "docs", "reports", "data")
A2 = os.path.join(HERE, "aifoundry2")
RES = json.load(open(os.path.join(HERE, "results.json")))
PH = json.load(open(os.path.join(HERE, "posthoc.json")))
Q139Q = os.path.join(DATA, "2026-11-03-q139q-gemm-g3")
PRED = json.load(open(os.path.join(Q139Q, "predictions-e159.json")))
FIX = json.load(open(os.path.join(Q139Q, "posthoc-fix-g3.json")))
E136 = json.load(open(os.path.join(DATA, "2026-11-02-e136-large-gemm", "results.json")))
E146 = json.load(open(os.path.join(DATA, "2026-11-02-e146-gemm-stores", "results.json")))
ROWS = {r["cell"]: r for r in RES["rows"]}
H1 = "H1-fp32-randn"
ZEROS = ("H1-fp32-zeros", "H2-fp32-zeros", "H3-fp32-zeros")
SESSIONS = ("smoke", "stoptest-board", "stoptest-die", "s1")
OUT = {"what": "E159 corrections after verification, post hoc and labelled; no registered number or verdict changes", "date": "2026-11-03"}


def r3(x):
    return None if x is None else round(float(x), 3)


def ols(xs, ys):
    mx, my = st.mean(xs), st.mean(ys)
    b = sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / sum((x - mx) ** 2 for x in xs)
    return b, my - b * mx


def sha256(path):
    return hashlib.sha256(open(path, "rb").read()).hexdigest()


def c1():
    print("C1. H1 FP32 RANDOM'S CLOCK MISS (post hoc): G3, and G3 given the hold's first second, both say 800 MHz (the hold is unheld)")
    r = ROWS[H1]
    g, gp = r["pred"]["G3"], r["pred"]["G3_given_p800"]
    e, ep = r["err"]["G3"], r["err"]["G3_given_p800"]
    print(f"  measured {r['meas']['mhz']:.2f} MHz, {r['meas']['w']:.2f} W, {r['meas']['die']:.2f} C")
    print(f"  G3 (registered)          {g['mhz']:7.2f} MHz {g['w']:6.2f} W {g['die']:6.2f} C  error {e['mhz']:+7.2f} MHz {e['w']:+6.2f} W {e['die']:+6.2f} C")
    print(f"  G3 given the first second {gp['mhz']:6.2f} MHz {gp['w']:6.2f} W {gp['die']:6.2f} C  error {ep['mhz']:+7.2f} MHz {ep['w']:+6.2f} W {ep['die']:+6.2f} C")
    cw, dp = PH["clock_in_window"][H1], PH["dips"][H1]
    implied = 800.0 * cw["share_at_800"] + cw["mean_below_800"] * (1 - cw["share_at_800"])
    start = [s for s in dp["since_own_process_s"] if s < 1.0]
    mid = [s for s in dp["since_own_process_s"] if s >= 1.0]
    print(f"  the window: {cw['samples']} in-kernel samples, {100 * cw['share_at_800']:.1f}% at 800 MHz, the rest at {cw['mean_below_800']} MHz on average "
          f"(800 x {cw['share_at_800']} + {cw['mean_below_800']} x {1 - cw['share_at_800']:.3f} = {implied:.1f} MHz, the measured mean {cw['mean']})")
    print(f"  the hold: {dp['n_runs']} runs of samples under 800 MHz ({dp['samples_low']} of {dp['samples']}); {len(start)} start "
          f"{min(start):.2f}-{max(start):.2f} s into a process, {len(mid)} mid-process at {', '.join(f'{s:.2f}' for s in mid)} s")
    unheld = []
    for cell, x in ROWS.items():
        if abs(x["pred"]["G3"]["mhz"] - 800.0) < 0.1:
            c = PH["clock_in_window"][cell]
            unheld.append({"hold": cell, "G3_mhz": r3(x["pred"]["G3"]["mhz"]), "err_mhz": r3(x["err"]["G3"]["mhz"]),
                           "share_at_800": c["share_at_800"], "mean_below_800": c["mean_below_800"]})
    print("  every hold G3 calls unheld (800 MHz): its clock error is the window's samples under 800 MHz")
    for u in unheld:
        print(f"    {u['hold']:15s} G3 {u['G3_mhz']:7.2f} MHz  error {u['err_mhz']:+7.2f} MHz  {100 * u['share_at_800']:5.1f}% at 800 MHz")
    print(f"  attribution as registered: {r['attribution']['mhz']}  (the label stays)")
    OUT["C1"] = {"measured": r["meas"], "G3": g, "G3_err": e, "G3_given_p800": gp, "G3_given_p800_err": ep, "window": cw,
                 "dips": {"n_runs": dp["n_runs"], "since_own_process_s": dp["since_own_process_s"], "at_process_start": len(start),
                          "mid_process_s": mid}, "window_mean_from_shares": r3(implied), "unheld_holds": unheld,
                 "registered_attribution_mhz": r["attribution"]["mhz"]}
    print()


def burst_starts(res):
    return [s for c in res["cells"].values() for s in (c.get("burst_die_start") or []) if s is not None]


def h1_slope():
    """The board's least-squares slope on the die reading inside H1, in-kernel samples at 800 MHz, two sample rules."""
    sd = os.path.join(A2, "s1")
    runs = [json.loads(x) for x in open(os.path.join(sd, "runs.jsonl"))]
    run = next(x for x in runs if x.get("label") == H1)
    L = [json.loads(x) for x in gzip.open(os.path.join(sd, "launches.jsonl.gz"), "rt")]
    ps = [p for p in L if p["run"] == run["run"] and p.get("role") == "work"]
    kw = [(k["t_start_ms"], k["t_end_ms"]) for p in ps for k in p.get("sparsity", []) if k.get("t_start_ms") and k.get("t_end_ms")]
    tel = [json.loads(x) for x in gzip.open(os.path.join(sd, "tel", run["run"] + ".jsonl.gz"), "rt") if x.startswith("{")]
    t0 = min(p["t_start_ms"] for p in ps)
    ink = [d for d in tel if d.get("board_w") is not None and d["mhz"]["minion"] == 800 and any(a <= d["t_ms"] <= b for a, b in kw)]
    rules = {
        "A (Q139(q) C1's rule: from 2 s after the hold's first process)": [d for d in ink if d["t_ms"] >= t0 + 2000],
        "B (the verifier's: each process's first 0.6 s left out)": [d for d in ink if any(p["t_start_ms"] + 600 <= d["t_ms"] <= p["t_end_ms"] for p in ps)],
    }
    out = {}
    for name, x in rules.items():
        T = [d["temp_c"]["minshire"][0] for d in x]
        P = [d["board_w"] for d in x]
        b, a = ols(T, P)
        out[name] = {"n": len(x), "die_min": min(T), "die_max": max(T), "slope_W_per_C": r3(b), "intercept": r3(a),
                     "board_first20_w": r3(st.mean(P[:20])), "board_last40_w": r3(st.mean(P[-40:]))}
    return out


def c2():
    print("C2. H1'S FIRST-SECOND DEFICIT AND ITS COLD START (post hoc)")
    r = ROWS[H1]
    d = r["attribution"]["p800_minus_P0_800_w"]
    others = {c: x["die_start"] for c, x in ROWS.items() if c != H1}
    print(f"  H1 fp32 random: the session's first hold, after the 30 s rest; start die {r['die_start']} C; p800 {r['p800']:.3f} W against P0(800) "
          f"{r['P0_800']} W: {d:+.3f} W")
    print(f"  the other eight holds started at {min(others.values()):.0f}-{max(others.values()):.0f} C")
    s136, s146 = burst_starts(E136), burst_starts(E146)
    for name, s in (("E136 (P0's fit set)", s136), ("E146 (P0 scored)", s146)):
        print(f"  {name}: {len(s)} bursts, start die {min(s)}-{max(s)} C, median {st.median(s)}")
    r3c, r5c = E146["rules"]["R3"]["cells"], E146["rules"]["R5"]["power"]
    pairs = []
    for c, v in E146["cells"].items():
        p0 = (r3c.get(c) or r5c.get(c) or {}).get("P0_w")
        if p0 is None:
            continue
        for p, s in zip(v.get("burst_p800_w_runs") or [], v.get("burst_die_start") or []):
            if p is not None and s is not None:
                pairs.append({"cell": c, "start_c": s, "p800_minus_P0": round(p - p0, 2)})
    cold = [x for x in pairs if x["start_c"] < 50]
    worst = sorted(pairs, key=lambda x: x["p800_minus_P0"])[:4]

    def show(xs):
        return ", ".join("%+.2f W (%s, %s C)" % (x["p800_minus_P0"], x["cell"], x["start_c"]) for x in xs)

    print(f"  E146's {len(pairs)} bursts: the {len(cold)} that started below 50 C read {show(cold)}, mean "
          f"{st.mean(x['p800_minus_P0'] for x in cold):+.2f} W; but its largest deficits started warm: {show(worst)}")
    sl = h1_slope()
    for name, v in sl.items():
        meet = (r["P0_800"] - v["intercept"]) / v["slope_W_per_C"]
        v["die_where_line_meets_P0_800_c"] = r3(meet)
        print(f"  inside H1 at 800 MHz, rule {name}: n {v['n']}, die {v['die_min']}-{v['die_max']} C, board {v['board_first20_w']:.2f} -> "
              f"{v['board_last40_w']:.2f} W (first 20 / last 40 samples), slope {v['slope_W_per_C']:.3f} W/C; the line meets P0(800) at {meet:.1f} C")
    lk = FIX["leakage_slope_at_800MHz"]
    print(f"  beside it: Q139(q) C1's slope inside the four unheld GEMM-pattern runs at 800 MHz, median {lk['unheld_in_window']['median']} "
          f"({lk['unheld_in_window']['min']}-{lk['unheld_in_window']['max']}); Q138(t)'s idle law {lk['idle_slope_Q138t']} W/C")
    ks = sorted({lk["idle_slope_Q138t"]} | {v["slope_W_per_C"] for v in sl.values()})
    trefs = (st.median(s136), st.median(s146))
    way1 = [k * (t - r["die_start"]) for k in ks for t in trefs]
    way2 = []
    for v in sl.values():
        for t in trefs:
            remaining = r["P0_800"] - (v["intercept"] + v["slope_W_per_C"] * t)
            way2.append(-d - remaining)
    print(f"  the part of the {-d:.2f} W deficit a start-die term carries, P0's reference die taken as the median start of its bursts "
          f"({trefs[0]:.0f} C E136, {trefs[1]:.0f} C E146):")
    print(f"    way 1, H1's first second carried to that die at k = {', '.join(f'{k:.3f}' for k in ks)} W/C: {min(way1):.2f}-{max(way1):.2f} W")
    print(f"    way 2, H1's in-hold line read at that die, the rest to P0(800) is the level: {min(way2):.2f}-{max(way2):.2f} W")
    lo, hi = min(way1 + way2), max(way1 + way2)
    print(f"  so a start-die term carries about {lo:.1f}-{hi:.1f} W of it, and the line law and the L3 about {-d - hi:.1f}-{-d - lo:.1f} W")
    nom = PRED["cells"][H1]["nominal"]
    print(f"  for context, the frozen nominal G3 for H1 fp32 random: from a 57 C gate {nom['gate57']['G3']['mhz']} MHz (held), from a 46 C rest start "
          f"{nom['rest']['G3']['mhz']} MHz; the registered primary from the measured start: {r['pred']['G3']['mhz']:.2f} MHz")
    OUT["C2"] = {"H1_die_start": r["die_start"], "H1_p800": r3(r["p800"]), "P0_800": r["P0_800"], "p800_minus_P0_800": d,
                 "other_holds_start_c": [min(others.values()), max(others.values())],
                 "E136_burst_starts": {"n": len(s136), "min": min(s136), "max": max(s136), "median": st.median(s136)},
                 "E146_burst_starts": {"n": len(s146), "min": min(s146), "max": max(s146), "median": st.median(s146)},
                 "E146_cold_bursts": cold, "E146_largest_deficits": worst, "H1_slope_at_800MHz": sl,
                 "Q139q_C1_unheld_slopes": lk["unheld_in_window"], "Q138t_idle_slope": lk["idle_slope_Q138t"],
                 "start_die_share_w": {"way1_first_second": [r3(min(way1)), r3(max(way1))], "way2_in_hold_line": [r3(min(way2)), r3(max(way2))],
                                       "range": [r3(lo), r3(hi)], "rest_line_law_and_L3": [r3(-d - hi), r3(-d - lo)]},
                 "nominal_G3_mhz": {"gate57": nom["gate57"]["G3"]["mhz"], "rest_46C": nom["rest"]["G3"]["mhz"]}}
    print()


def c3():
    print("C3. E159 BLIND BESIDE Q139(q)'S NESTED FIGURES (Q139(q)'s posthoc-fix-g3.json subsets)")
    s = RES["all_scored"]["summary"]
    e159 = {q: s[f"G3.{q}"]["rms"] for q in ("mhz", "w", "die")}
    out = {"E159_G3_blind": e159}
    for key, name in (("all", "56 GEMM-pattern runs"), ("large_gemms_E136_E146", "14 large GEMMs (E136, E146)")):
        g = FIX["subsets"][key]["stats"]["G3_nested"]
        law = FIX["subsets"][key]["stats"]["E136_law"]
        v = {q: g[q]["rms"] for q in ("mhz", "w", "die")}
        ratio = {q: r3(e159[q] / v[q]) for q in v}
        print(f"  {name}: G3 nested {v['mhz']:.3f} MHz, {v['w']:.3f} W, {v['die']:.3f} C (E136's law {law['mhz']['rms']:.3f}, {law['w']['rms']:.3f}, "
              f"{law['die']['rms']:.3f}); E159 blind / nested: clock {ratio['mhz']}, board {ratio['w']}, die {ratio['die']}")
        out[key] = {"G3_nested": v, "E136_law": {q: law[q]["rms"] for q in ("mhz", "w", "die")}, "E159_over_nested": ratio}
    print(f"  E159 blind: {e159['mhz']} MHz, {e159['w']} W, {e159['die']} C")
    OUT["C3"] = out
    print()


def c4():
    print("C4. THE POST'S FIRST SENTENCE: what was on record before the run, and what the registered primary computed after it")
    out = {}
    for cell in ("H2-fp32-randn", "H3-fp32-randn"):
        r = ROWS[cell]
        nom = PRED["cells"][cell]["nominal"]
        out[cell] = {"measured_mhz": r3(r["meas"]["mhz"]), "primary_mhz": r3(r["pred"]["G3"]["mhz"]),
                     "nominal_gate57_mhz": nom["gate57"]["G3"]["mhz"], "nominal_rest46_mhz": nom["rest"]["G3"]["mhz"], "die_start": r["die_start"]}
        print(f"  {cell}: measured {r['meas']['mhz']:.1f} MHz; frozen nominal G3 {nom['gate57']['G3']['mhz']} MHz from a 57 C gate "
              f"({nom['rest']['G3']['mhz']} from a 46 C start); the registered primary, from the hold's measured start ({r['die_start']} C) and anchor, "
              f"{r['pred']['G3']['mhz']:.1f} MHz")
    v = RES["all_scored"]["verdict_G3"]
    print(f"  as registered: clock {v['mhz']}, board {v['w']}, die {v['die']} (bands 15 MHz, 2 W, 1 C)")
    out["verdict_G3"] = v
    OUT["C4"] = out
    print()


def c5():
    print("C5. ZEROS (measured - predicted; a negative error means G3 reads high)")
    out = {}
    for cell in ZEROS:
        r = ROWS[cell]
        out[cell] = {"G3_w_err": r3(r["err"]["G3"]["w"]), "p800_minus_P0_800": r["attribution"]["p800_minus_P0_800_w"],
                     "attribution_w": r["attribution"]["w"], "G3_given_p800_w_err": r3(r["err"]["G3_given_p800"]["w"]),
                     "G3_die_err": r3(r["err"]["G3"]["die"]), "chain_die_err": r3(r["err"]["chain_on_measured"]["die"])}
        print(f"  {cell}: G3 board error {r['err']['G3']['w']:+.3f} W (G3 high); p800 - P0(800) {r['attribution']['p800_minus_P0_800_w']:+.3f} W -> "
              f"'{r['attribution']['w']}'; given the first second {r['err']['G3_given_p800']['w']:+.3f} W; die error {r['err']['G3']['die']:+.3f} C, "
              f"the chain on the measured trace {r['err']['chain_on_measured']['die']:+.3f} C")
    OUT["C5"] = out
    print()


def c6():
    print("C6. THE SESSION'S SPTRACE COPIES AND RESIDENCY ATTEMPTS (all READ or NOT SENT; no WRITE)")
    recs = []
    for s in SESSIONS:
        rp = os.path.join(A2, s, "runs.jsonl")
        if os.path.exists(rp):
            for x in open(rp):
                q = json.loads(x).get("queries") or {}
                recs.append((s, "per run", q))
        qp = os.path.join(A2, s, "queries.jsonl")
        if os.path.exists(qp):
            for x in open(qp):
                q = json.loads(x)
                recs.append((s, f"session {q.get('tag')}", q))
    per_run = [x for x in recs if x[1] == "per run"]
    sess = [x for x in recs if x[1] != "per run"]
    spt0 = sum(1 for _, _, q in recs if q.get("sptrace_rc") == 0)
    res2 = sum(1 for _, _, q in recs if q.get("residency_rc") == 2 and not q.get("residency"))
    cfg0 = sum(1 for _, _, q in recs if q.get("config_rc") == 0)
    by = {}
    for s, k, _ in sess:
        by[s] = by.get(s, 0) + 1
    print(f"  records: {len(per_run)} per run (smoke and s1) + {len(sess)} at session start and end ({by}) = {len(recs)}")
    print(f"  sptrace rc 0: {spt0}; residency rc 2 with no output (refused before the device opens, nothing sent): {res2}; config rc 0: {cfg0}")
    OUT["C6"] = {"per_run": len(per_run), "session_start_end": len(sess), "by_session": by, "total": len(recs),
                 "sptrace_rc0": spt0, "residency_rc2_empty": res2, "config_rc0": cfg0}
    print()


def git_sha(rev, rel):
    try:
        b = subprocess.run(["git", "-C", LAB, "show", f"{rev}:{rel}"], capture_output=True, timeout=30, check=True).stdout
        return hashlib.sha256(b).hexdigest()
    except (OSError, subprocess.SubprocessError):
        return None


def c7():
    print("C7. THE RECORDS: the predictions file's hash on the box, and the board stop test's docstring")
    out = {"sessions": {}}
    for s in SESSIONS:
        e = json.load(open(os.path.join(A2, s, "e159.json")))
        rel = "tools/claims-v3/e159/" + e["protocol"]
        at = git_sha("d8badb73", rel)
        out["sessions"][s] = {"predictions_sha256_here": e["predictions_sha256_here"], "predictions_sha256_registered": e["predictions_sha256_registered"],
                              "protocol": e["protocol"], "protocol_sha256": e["protocol_sha256"], "protocol_sha256_at_d8badb73": at}
        print(f"  {s:15s} predictions_sha256_here {e['predictions_sha256_here']}; registered {e['predictions_sha256_registered'][:12]}...; "
              f"{e['protocol']} {e['protocol_sha256'][:12]}... = d8badb73's: {at == e['protocol_sha256'] if at else 'git not available'}")
    pf = os.path.join(Q139Q, "predictions-e159.json")
    here = sha256(pf)
    out["predictions_sha256_on_the_intel"] = here
    out["predictions_sha256_in_results"] = RES["predictions_sha256"]
    print(f"  predictions-e159.json on the Intel, where the scorer ran: {here[:12]}...; results.json's predictions_sha256 "
          f"{RES['predictions_sha256'][:12]}...; equal: {here == RES['predictions_sha256']}")
    q = open(os.path.join(LAB, "tools", "claims-v3", "e159", "queue_e159.py")).read().splitlines()
    hit = [(i + 1, x.strip()) for i, x in enumerate(q) if "burst of D8" in x]
    pb = json.load(open(os.path.join(LAB, "tools", "claims-v3", "e159", "protocol-stoptest-board.json")))
    ran = [x["label"] for b in pb["blocks"] for x in b["runs"]]
    tel = sorted(os.listdir(os.path.join(A2, "stoptest-board", "tel")))
    for ln, x in hit:
        print(f"  queue_e159.py line {ln}: {x}")
    print(f"  protocol-stoptest-board.json runs {ran}; stoptest-board/tel: {tel}")
    out["docstring"] = {"lines": hit, "protocol_runs": ran, "tel_files": tel}
    OUT["C7"] = out
    print()


if __name__ == "__main__":
    print("E159 CORRECTIONS AFTER VERIFICATION (post hoc, labelled). Errors are measured - predicted. No registered number or verdict changes.\n")
    c1()
    c2()
    c3()
    c4()
    c5()
    c6()
    c7()
    json.dump(OUT, open(os.path.join(HERE, "corrections.json"), "w"), indent=1)
