#!/usr/bin/env python3
"""E159 (Q139): the registered reduction. No card. It scores E159's holds with Q139(q)'s FROZEN scorer, unchanged, behind its hash check, and adds the
records the frozen rules name but the scorer does not compute (which holds are scored, the attribution, the checks of C, the safety record, card time).

    /usr/bin/python3 tools/claims-v3/e159/reduce_e159.py <RUNS dir: the queue's smoke/, stoptest-*/, s1/ (s2/ ...)> --out results.json > reduce.txt

  1. THE FREEZE. score_e159.check(): the 28 files the frozen scorer imports or opens equal their bytes at 91def7c4 (frozen-sha256.json). If not, exit 2
     and nothing is scored.
  2. WHICH HOLDS ARE SCORED (Q139(q)'s rules: "A hold cut by a stop or not run is not scored; the registered subset is the first six of the order"). A hold
     is a run of the session whose label is one of the nine frozen cells and whose processes are >= 2. It is COMPLETE when all of its planned processes
     (12) have a work launch record with rc 0, every one of its kernel records is ok (rgm136's check of C against the host's own reference), and no
     safety_trip mark falls between its first process's start and its last process's end. A hold that is not complete is CUT: listed, not scored.
  3. THE SCORE. Each session directory is scored on its own by e159_g3.score (the frozen code, its predictions file and G3's constants untouched), on a
     temporary copy of the session holding the same tel/ (a link), the same launch records (gzipped as the scorer reads them) and runs.jsonl with the cut
     holds left out. The rows of every session are pooled. The verdicts (Q139(q)'s, mechanical): per quantity (sustained clock within 15 MHz, board
     within 2 W, window die within 1 C, measured - predicted), G3 PASSES when every scored hold is inside, else FAILS with the count; the rms of every arm
     (G3; G3 at Q138(t)'s constants; the chain on the measured trace, die only; E136's law, the old arm; G3 given the hold's first second, a diagnostic
     with no verdict); G3 beats E136's law on a quantity when its rms is lower. Printed for every scored hold (the primary) and for the registered subset
     alone (the first six of the order).
  4. THE ATTRIBUTION (Q139(q)'s, registered): a G3 clock or board miss on a hold whose first-second power p800 is more than 4 W from P0(800) is P0's level;
     a die miss where the chain on the measured trace is inside 1 C is the power path, not heat (and a die miss with the chain outside 1 C is the heat path).
  5. R0, the ties: every check of C in every launch of every session (smoke, stop tests, holds) ok; a failure labels every verdict.
  6. THE SAFETY RECORD: per run the highest board sample, the highest die mean and hottest-sensor field, every safety_trip mark, every hold not admitted
     (skipped.jsonl) and every peak-lock mark; the stop-path tests' records (queue.jsonl stoptest_detail and stoptest_check); the TDP and threshold read
     after every run and in the queue's two snapshots; card time from the first card touch (snapshot-start) to the queue's end.
"""
import gzip
import json
import os
import shutil
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, "..", "..", ".."))
G3DIR = os.path.join(ROOT, "docs/reports/data/2026-11-03-q139q-gemm-g3")
sys.path.insert(0, G3DIR)
import score_e159 as SC  # noqa: E402  (Q139(q)'s wrapper: check() and the freeze manifest)

PRED = json.load(open(os.path.join(G3DIR, "predictions-e159.json")))
ORDER = list(PRED["design"]["order"])
SUBSET = list(PRED["design"]["registered_subset"])
N_PROC = int(PRED["design"]["hold"]["processes"])
RULE = {"mhz": 15.0, "w": 2.0, "die": 1.0}
P0_BAND_W = 4.0
ARMS = ("G3", "G3_q138t_constants", "E136_law", "chain_on_measured", "G3_given_p800")


def jl(path):
    out = []
    op = gzip.open if path.endswith(".gz") else open
    try:
        with op(path, "rt") as f:
            for ln in f:
                ln = ln.strip()
                if ln.startswith("{"):
                    try:
                        out.append(json.loads(ln))
                    except ValueError:
                        pass
    except OSError:
        pass
    return out


def launches_path(sd):
    for n in ("launches.jsonl.gz", "launches.jsonl"):
        if os.path.exists(os.path.join(sd, n)):
            return os.path.join(sd, n)
    return None


def tel_rows(sd, run):
    for ext in (".jsonl.gz", ".jsonl"):
        p = os.path.join(sd, "tel", run + ext)
        if os.path.exists(p):
            rows = []
            for d in jl(p):
                ms = (d.get("temp_c") or {}).get("minshire") or [None, None, None]
                rows.append((d.get("t_ms"), d.get("board_w"), ms[0], ms[2] if len(ms) > 2 else None, (d.get("mhz") or {}).get("minion")))
            return rows
    return []


def sessions(runs_dir):
    """the queue's session directories in order (s1, s2, ...); a refused start (sN.refusedK) holds no run"""
    out = []
    k = 1
    while os.path.isdir(os.path.join(runs_dir, f"s{k}")):
        out.append(os.path.join(runs_dir, f"s{k}"))
        k += 1
    return out


def holds_of(sd):
    """(complete, cut) holds of a session: each a dict with the run, the label and why it is cut"""
    runs = jl(os.path.join(sd, "runs.jsonl"))
    L = jl(launches_path(sd) or os.path.join(sd, "launches.jsonl"))
    trips = [m for m in jl(os.path.join(sd, "marks.jsonl")) if m.get("kind") == "safety_trip"]
    good, cut = [], []
    for r in runs:
        if r.get("label") not in PRED["cells"] or r.get("processes", 1) < 2:
            continue
        ps = [p for p in L if p.get("run") == r["run"] and p.get("role") == "work"]
        why = []
        want = int(r.get("processes") or N_PROC)
        if len(ps) < want:
            why.append(f"{len(ps)} of {want} processes recorded")
        if any(p.get("rc") != 0 for p in ps):
            why.append("a process rc not 0")
        recs = [k for p in ps for k in p.get("sparsity", [])]
        if not recs or not all(k.get("ok") for k in recs):
            why.append(f"kernel records {len(recs)}, not all ok (the check of C)")
        if ps:
            a, b = min(p["t_start_ms"] for p in ps), max(p["t_end_ms"] for p in ps)
            if any(a <= m.get("t_ms", 0) <= b for m in trips):
                why.append("a safety stop fired inside the hold")
        h = {"run": r["run"], "label": r["label"], "processes": len(ps), "planned": want, "gate": r.get("gate")}
        if why:
            h["why_cut"] = "; ".join(why)
            cut.append(h)
        else:
            good.append(h)
    return good, cut


def score_session(sd, keep_runs, E):
    """the frozen scorer on a temporary copy of the session with only the complete holds (and the runs it skips anyway)"""
    tmp = tempfile.mkdtemp(prefix="e159-reduce-", dir=os.environ.get("TMPDIR"))
    try:
        os.symlink(os.path.abspath(os.path.join(sd, "tel")), os.path.join(tmp, "tel"))
        lp = launches_path(sd)
        if lp.endswith(".gz"):
            os.symlink(os.path.abspath(lp), os.path.join(tmp, "launches.jsonl.gz"))
        else:
            with open(lp, "rb") as fi, gzip.open(os.path.join(tmp, "launches.jsonl.gz"), "wb") as fo:
                shutil.copyfileobj(fi, fo)
        with open(os.path.join(tmp, "runs.jsonl"), "w") as f:
            for r in jl(os.path.join(sd, "runs.jsonl")):
                if r.get("label") in PRED["cells"] and r.get("processes", 1) >= 2 and r["run"] not in keep_runs:
                    continue
                f.write(json.dumps(r) + "\n")
        res = E.score(tmp)
        return res
    finally:
        shutil.rmtree(tmp)


def summarize(rows):
    """Q139(q)'s summary and verdict, recomputed from the scorer's own rows (the same arithmetic as e159_g3.score) for any subset of them"""
    import math
    summ = {}
    for a in ARMS:
        for q in RULE:
            e = [x["err"][a][q] for x in rows if a in x["err"] and q in x["err"][a]]
            if e:
                summ[f"{a}.{q}"] = {"n": len(e), "rms": round(math.sqrt(sum(v * v for v in e) / len(e)), 3), "mean": round(sum(e) / len(e), 3),
                                    "inside": int(sum(abs(v) <= RULE[q] for v in e))}
    verdict = {q: ("PASS" if rows and all(x["inside_G3"][q] for x in rows) else "FAIL") + f" ({sum(x['inside_G3'][q] for x in rows)} of {len(rows)})" for q in RULE}
    beats = {q: (summ.get(f"G3.{q}", {}).get("rms", 1e9) < summ.get(f"E136_law.{q}", {}).get("rms", -1)) for q in RULE}
    return {"summary": summ, "verdict_G3": verdict, "G3_rms_below_E136_law": beats}


def attribute(x):
    """Q139(q)'s attribution rule on one scored row"""
    out = {}
    p0 = None if x.get("p800") is None else x["p800"] - x["P0_800"]
    for q in ("mhz", "w"):
        if x["inside_G3"][q]:
            out[q] = "inside"
        elif p0 is not None and abs(p0) > P0_BAND_W:
            out[q] = f"P0's level (p800 - P0(800) = {p0:+.2f} W, outside 4 W)"
        else:
            out[q] = "not P0's level by the rule" + ("" if p0 is not None else " (no first second at 800 MHz)") + (f" (p800 - P0(800) = {p0:+.2f} W)" if p0 is not None else "")
    if x["inside_G3"]["die"]:
        out["die"] = "inside"
    else:
        ch = x["err"].get("chain_on_measured", {}).get("die")
        out["die"] = ("the power path, not heat" if ch is not None and abs(ch) <= RULE["die"] else "the heat path") + (f" (chain on the measured trace {ch:+.2f} C)" if ch is not None else "")
    out["p800_minus_P0_800_w"] = None if p0 is None else round(p0, 3)
    return out


def safety(runs_dir):
    out = {"runs": [], "trips": [], "not_admitted": [], "peak_lock": [], "end": {}, "stoptests": [], "config": []}
    names = [n for n in ("smoke", "stoptest-board", "stoptest-die") if os.path.isdir(os.path.join(runs_dir, n))] + [os.path.basename(s) for s in sessions(runs_dir)]
    for n in names:
        sd = os.path.join(runs_dir, n)
        try:
            out["end"][n] = json.load(open(os.path.join(sd, "end.json")))
        except (OSError, ValueError):
            out["end"][n] = None
        for m in jl(os.path.join(sd, "marks.jsonl")):
            if m.get("kind") == "safety_trip":
                out["trips"].append({"session": n, **m})
            if m.get("kind") == "e105_peak_lock":
                out["peak_lock"].append({"session": n, **m})
        for s in jl(os.path.join(sd, "skipped.jsonl")):
            out["not_admitted"].append({"session": n, **s})
        for r in jl(os.path.join(sd, "runs.jsonl")):
            rows = tel_rows(sd, r["run"])
            ws = [w for _, w, _, _, _ in rows if w is not None]
            dm = [d for _, _, d, _, _ in rows if d is not None]
            hs = [h for _, _, _, h, _ in rows if h is not None]
            c = (r.get("queries") or {}).get("config") or {}
            out["runs"].append({"session": n, "run": r["run"], "label": r.get("label"), "processes": r.get("processes"), "samples": len(rows),
                                "board_max_w": max(ws) if ws else None, "die_mean_max_c": max(dm) if dm else None, "hottest_field_max_c": max(hs) if hs else None,
                                "hottest_field_min_c": min(hs) if hs else None})
            out["config"].append({"session": n, "run": r["run"], "tdp_w": c.get("tdp_w"), "temp_threshold_c": c.get("temp_threshold_c"),
                                  "power_state_name": c.get("power_state_name"), "minion_mhz": c.get("minion_mhz")})
    q = jl(os.path.join(runs_dir, "queue.jsonl"))
    out["stoptests"] = [x for x in q if x.get("kind") in ("stoptest_detail", "stoptest_check", "smoke_check", "queue_halt")]
    snaps = {}
    for tag in ("start", "end"):
        try:
            snaps[tag] = json.load(open(os.path.join(runs_dir, f"snapshot-{tag}.json")))
        except (OSError, ValueError):
            snaps[tag] = None
    out["snapshots"] = {k: (None if v is None else {"t_ms": v.get("t_ms"), "config": v.get("config")}) for k, v in snaps.items()}
    qe = [x for x in q if x.get("kind") == "queue_end"]
    t0 = (snaps.get("start") or {}).get("t_ms")
    t1 = qe[-1].get("card_free_ms") if qe else None
    out["card_time"] = {"first_touch_ms": t0, "card_free_ms": t1, "minutes": None if (t0 is None or t1 is None) else round((t1 - t0) / 60000.0, 2)}
    ws = [r["board_max_w"] for r in out["runs"] if r["board_max_w"] is not None]
    dm = [r["die_mean_max_c"] for r in out["runs"] if r["die_mean_max_c"] is not None]
    hs = [r["hottest_field_max_c"] for r in out["runs"] if r["hottest_field_max_c"] is not None]
    out["peaks"] = {"board_max_w": max(ws) if ws else None, "die_mean_max_c": max(dm) if dm else None, "hottest_field_max_c": max(hs) if hs else None}
    tdps = {(c["tdp_w"], c["temp_threshold_c"]) for c in out["config"] if c["tdp_w"] is not None}
    out["config_read"] = sorted(tdps)
    return out


def checks_of_c(runs_dir):
    """R0: every kernel record ok in every launch of every session"""
    n, bad = 0, []
    names = [n_ for n_ in ("smoke", "stoptest-board", "stoptest-die") if os.path.isdir(os.path.join(runs_dir, n_))] + [os.path.basename(s) for s in sessions(runs_dir)]
    for s in names:
        sd = os.path.join(runs_dir, s)
        for p in jl(launches_path(sd) or os.path.join(sd, "launches.jsonl")):
            if p.get("role") != "work":
                continue
            for k in p.get("sparsity", []):
                n += 1
                if not k.get("ok"):
                    bad.append({"session": s, "run": p.get("run"), "result": k.get("result"), "test": k.get("test")})
    return {"kernel_records": n, "not_ok": bad, "verdict": "PASS" if n and not bad else ("FAIL" if bad else "NO RECORDS")}


def reduce(runs_dir, outp=None, check=True):
    if check:
        SC.check()
    sys.path.insert(0, G3DIR)
    import e159_g3 as E
    rows, cut, complete = [], [], []
    per_session = {}
    for sd in sessions(runs_dir):
        good, bad = holds_of(sd)
        cut += [{"session": os.path.basename(sd), **h} for h in bad]
        complete += [{"session": os.path.basename(sd), **h} for h in good]
        if not good:
            continue
        print(f"== the frozen scorer on {os.path.basename(sd)} ({len(good)} complete holds; {len(bad)} cut)")
        res = score_session(sd, {h["run"] for h in good}, E)
        per_session[os.path.basename(sd)] = {"verdict_G3": res["verdict_G3"], "G3_rms_below_E136_law": res["G3_rms_below_E136_law"], "n": len(res["rows"])}
        for x in res["rows"]:
            x["session"] = os.path.basename(sd)
            rows.append(x)
    order = {c: i for i, c in enumerate(ORDER)}
    rows.sort(key=lambda x: order.get(x["cell"], 99))
    for x in rows:
        x["attribution"] = attribute(x)
    allv = summarize(rows)
    sub_rows = [x for x in rows if x["cell"] in SUBSET]
    subv = summarize(sub_rows)
    subv["holds"] = [x["cell"] for x in sub_rows]
    subv["complete"] = all(c in subv["holds"] for c in SUBSET)
    r0 = checks_of_c(runs_dir)
    sf = safety(runs_dir)
    out = {"experiment": "E159", "request": "Q139", "freeze": SC.FREEZE, "predictions_sha256": SC.sha(os.path.join(G3DIR, "predictions-e159.json")),
           "rule": RULE, "rows": rows, "cut": cut, "complete": complete, "all_scored": allv, "registered_subset": subv, "per_session": per_session,
           "R0_checks_of_C": r0, "labelled": r0["verdict"] != "PASS", "safety": sf}
    print()
    print("E159 reduction (registered): Q139(q)'s frozen scorer behind its hash check, cut holds left out, the attribution, R0, the safety record")
    print(f"complete holds scored: {[x['cell'] for x in rows]}; cut: {[(c['label'], c['why_cut']) for c in cut]}")
    hdr = f"{'hold':16s} {'measured MHz/W/C':>22s} | {'G3':>20s} | {'G3 err':>18s} | in | {'E136 law':>20s} | {'chain die':>9s} | {'p800-P0':>7s}"
    print(hdr)
    for x in rows:
        m, g, e, lw = x["meas"], x["pred"]["G3"], x["err"]["G3"], x["pred"]["E136_law"]
        ins = "".join("y" if x["inside_G3"][q] else "n" for q in ("mhz", "w", "die"))
        ch = x["pred"]["chain_on_measured"]["die"]
        p0 = x["attribution"]["p800_minus_P0_800_w"]
        print(f"{x['cell']:16s} {m['mhz']:6.1f} {m['w']:6.2f} {m['die']:6.2f} | {g['mhz']:6.1f} {g['w']:6.2f} {g['die']:6.2f} | {e['mhz']:+6.1f} {e['w']:+5.2f} {e['die']:+5.2f} | "
              f"{ins} | {lw['mhz']:6.1f} {lw['w']:6.2f} {lw['die']:6.2f} | {ch:9.2f} | {('%+7.2f' % p0) if p0 is not None else '      -'}")
    for x in rows:
        a = x["attribution"]
        if any(a[q] != "inside" for q in ("mhz", "w", "die")):
            print(f"  attribution {x['cell']}: clock {a['mhz']}; board {a['w']}; die {a['die']}")
    for tag, v in (("ALL SCORED HOLDS (the primary)", allv), ("THE REGISTERED SUBSET (the first six)", subv)):
        print(f"{tag}: G3 {json.dumps(v['verdict_G3'])}; G3 rms below E136's law {json.dumps(v['G3_rms_below_E136_law'])}")
        for a in ARMS:
            s = "; ".join(f"{q} {v['summary'][f'{a}.{q}']['rms']} rms ({v['summary'][f'{a}.{q}']['mean']:+} mean, {v['summary'][f'{a}.{q}']['inside']} of {v['summary'][f'{a}.{q}']['n']} inside)"
                          for q in RULE if f"{a}.{q}" in v["summary"])
            if s:
                print(f"   {a:20s} {s}")
    print(f"R0 (checks of C): {r0['verdict']} ({r0['kernel_records']} kernel records, {len(r0['not_ok'])} not ok){' -- EVERY VERDICT LABELLED' if out['labelled'] else ''}")
    print(f"safety: peaks {sf['peaks']}; trips {[(t['session'], t.get('detail')) for t in sf['trips']]}; not admitted {[(s['label'], s['why']) for s in sf['not_admitted']]}; "
          f"peak locks {len(sf['peak_lock'])}; config read (TDP W, threshold C) {sf['config_read']}; card time {sf['card_time']}")
    if outp:
        json.dump(out, open(outp, "w"), indent=1)
    return out


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return 2
    outp = sys.argv[sys.argv.index("--out") + 1] if "--out" in sys.argv else None
    reduce(os.path.abspath(sys.argv[1]), outp, check="--no-check" not in sys.argv)
    return 0


if __name__ == "__main__":
    sys.exit(main())
