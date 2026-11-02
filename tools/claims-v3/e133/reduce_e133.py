#!/usr/bin/env python3
"""E133 (Q136): the registered reduction and scorer. Frozen with the pre-registration, before the claim and the first launch.

    python3 tools/claims-v3/e133/reduce_e133.py <DATA> [--out results.json] > reduce.txt
    python3 tools/claims-v3/e133/reduce_e133.py --regression [--out regression.json]   # the self-test on E98's and E111's committed data

<DATA> holds SMOKE/ W2/ END/ W1B/ END2/ [W3/] (run_e133.py sessions), queue.jsonl, phone.jsonl and history/<box>-<UTC date>.jsonl.gz,
the boxes' own 5 s records. Epoch ms throughout. Standard library only, plus E111's reduce_e111.py and, through it, E98's reduce_e98.py
and the lab's reduce_hpl.py and reduce_kspeed.py, all imported unchanged.

BEFORE ANYTHING IS SCORED, two regressions (the scorer refuses if either differs): (1) E111's score98() on E98's probes reproduces
E98's committed results.json, key for key (E111's own check); (2) the same code path that reads E133 reproduces E111's committed
results.json: Part A on E111's data dir with E111's predictions, and Part B's fits, verdicts and per-probe maps on E98's probes plus
E111's W1 and W2.

PART A, THE HOLDS AGAIN (E133-A1..A4 = E111-A1..A4, reduce_e111.part_a unchanged, on E133's data): H-I8, int8 neg_ones from rest (W1B;
idle before W1B's REST, after END2's) at 800 MHz, and H-F32, fp32 randn after E98's probe (W2; idle before W2's REST, after END's)
under the card's governor. A1 steady (fine-W slope over the last 600 s at 0.442 W/C, bar 0.02 C/min; the die when the clock is not
held); A2 c's range against the four bands; A3 c(H-F32)/c(H-I8) against [0.90, 1.11]; A4 the inlet proxies, beside. NEW:
  * E133-R1, the replicate: c(E133) / c(E111) per kind, its range from the two ranges' extremes (E111's committed A2 c_lo, c_hi),
    against [0.90, 1.11]: PASS (REPLICATES) inside, FAIL (DIFFERS) wholly outside, INCONCLUSIVE otherwise.
  * E133-R2, the room and the governor: H-F32's plateau share at 600 MHz: AT THE FLOOR if >= 0.90, AT THE TRIP otherwise. Predicted
    from W2's REST idle die (last 60 s): AT THE TRIP below 43.5 C, AT THE FLOOR from 43.5 C.
  * beside, never a verdict: each hold minute by minute (die, W, fine W, share at the clock), the wander (the range of the minute bins'
    die from minute 8 to the end) and c over every 5-minute window from minute 5; the peaks of every step (board W, die mean, the
    hottest sensor's reading).
PART B, THE DRIFT (E133-B0..B4 = E111-B0..B4, E98's scoring, reduce_e111.score98 unchanged) on the combined probes: E98's P1, P2, P3,
P6, P7, E111's W1 and W2 (read as E111 read them) and E133's W2 (and W3 if it ran), named E111-W1, E111-W2, E133-W2, E133-W3. NEW:
  * E133-B3c, a cool or warm probe against the night's baseline: E111-B3's reading (each probe's rest-die lead dx over the mean of P3,
    P6, P7, W-derived; its line lead and hold lead per C of dx; a 95% normal interval from E98's frozen per-probe scatter, hold 0.375 C
    and line 0.089 C, one probe against a mean of three), over every E133 probe with |dx| >= 0.5 C, cool or warm. The line on E98-R1's
    partition (against 0 and 0.25), the hold on E98-R2's (band 1.00-1.25, floor 0.25).
"""
import argparse
import copy
import hashlib
import json
import math
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "tools/claims-v3/e111"))
import reduce_e111 as X  # noqa: E402

E, R = X.E, X.R
rnd, mean = X.rnd, X.mean
E111D = os.path.join(ROOT, "docs/reports/data/2026-11-01-e111-heat-steady")
E98D = os.path.join(ROOT, "docs/reports/data/2026-11-01-e98-heat-path-drift")
P111_PATH = os.path.join(ROOT, "tools/claims-v3/e111/predictions-e111.json")
P98_PATH = os.path.join(ROOT, "tools/claims-v3/kspeed/e98/predictions.json")
STEPS = ("SMOKE", "W2", "END", "W1B", "END2", "W3")


def jround(x):
    return json.loads(json.dumps(x, sort_keys=True, default=str))


# ------------------------------------------------------------------------------------------------ probes
def e98_probes(P111, P98):
    H98 = E.History(E98D)
    q98 = R.jl(os.path.join(E98D, "queue.jsonl"))
    out = []
    for name in P111["partB"]["e98_probes"]:
        pr = E.read_probe(os.path.join(E98D, name), name, H98, P98, [q for q in q98 if q.get("probe") == name])
        pr["queue"] = [q for q in q98 if q.get("probe") == name]
        out.append(pr)
    return out


def e111_probes(P98, prefix=""):
    """E111's W1 and W2 exactly as reduce_e111.main() read them (W1's hold on its first 39 processes)."""
    H = E.History(E111D)
    q = R.jl(os.path.join(E111D, "queue.jsonl"))
    out = []
    for name in ("W1", "W2"):
        pdir = os.path.join(E111D, name)
        pr = E.read_probe(pdir, name, H, P98, [])
        if name == "W1":
            pr["hold_full_last120"] = pr.get("hold")
            pr["hold"] = X.hold39(pdir, P98)
        pr["queue"] = [x for x in q if x.get("step") == name]
        if prefix:
            pr["probe"] = prefix + name
        out.append(pr)
    return out


def e133_probes(data, H, P98, qrecs):
    out = []
    for name in ("W2", "W3"):
        pdir = os.path.join(data, name)
        if not os.path.exists(os.path.join(pdir, "runs.jsonl")):
            continue
        pr = E.read_probe(pdir, "E133-" + name, H, P98, [])
        pr["probe"] = "E133-" + name
        pr["queue"] = [x for x in qrecs if x.get("step") == name]
        out.append(pr)
    return out


def b3c(sall, baseline, names, P133):
    """E133-B3c: reduce_e111.b3's reading for every named probe with |dx| >= the bar, cool or warm (the side named)."""
    pb = P133["partB"]
    m = sall["_maps"]
    px, line, hold = m["px"], m["line"], m["hold_die"]
    base = [b for b in baseline if b in px]
    bar = pb["b3c"]["min_abs_lead_c"]
    out = {"baseline": base, "per_probe": {}, "min_abs_lead_c": bar}
    if len(base) < 2:
        out["verdict_hold"] = out["verdict_line"] = "UNDER-RESOLVED"
        return out
    bx = mean([px[b] for b in base])
    bl = mean([line.get(b) for b in base])
    bh = mean([hold.get(b) for b in base])
    out["baseline_values"] = {"rest_die_w_derived": rnd(bx, 3), "line": rnd(bl, 3), "hold_die": rnd(bh, 3)}
    sh, sl = [], []
    for w in names:
        if w not in px:
            out["per_probe"][w] = {"note": "not counted"}
            continue
        dx = px[w] - bx
        rec = {"dx_c": rnd(dx, 3), "line_lead": rnd(line[w] - bl, 3) if line.get(w) is not None else None,
               "hold_lead": rnd(hold[w] - bh, 3) if hold.get(w) is not None else None,
               "side": "warm" if dx >= bar else ("cool" if dx <= -bar else "neither")}
        if abs(dx) >= bar:
            if rec["line_lead"] is not None:
                rec["line_per_c"] = rnd(rec["line_lead"] / dx, 3)
                sl.append((rec["line_lead"] / dx, dx))
            if rec["hold_lead"] is not None:
                rec["hold_per_c"] = rnd(rec["hold_lead"] / dx, 3)
                sh.append((rec["hold_lead"] / dx, dx))
        out["per_probe"][w] = rec
    nb = len(base)
    T = pb["e98_targets"]
    for key, vals, sig in (("hold", sh, pb["b3_noise_per_probe_c"]["hold"]), ("line", sl, pb["b3_noise_per_probe_c"]["line"])):
        if not vals:
            out[f"verdict_{key}"] = "UNDER-RESOLVED"
            continue
        mu = mean([v for v, _ in vals])
        se = math.sqrt(sum((sig * math.sqrt(1 + 1.0 / nb) / dx) ** 2 for _, dx in vals)) / len(vals)
        f = {"slope": rnd(mu, 4), "lo": rnd(mu - 1.96 * se, 4), "hi": rnd(mu + 1.96 * se, 4), "se": rnd(se, 4), "n": len(vals)}
        out[key] = f
        out[f"verdict_{key}"] = E.verdict_band(f, T["hold_band"], T["hold_floor"]) if key == "hold" else E.verdict_target(f, T["line_slope"])
    return out


def part_b(p98, p111, p133, P98, P133):
    sall = X.score98(p98 + p111 + p133, P98)
    B = {"B0_gate": sall["R0"]["gate"], "R0": sall["R0"], "B1": sall["R1"]["verdict"], "B1_fit": sall["R1"]["fit"],
         "B2": sall["R2"]["verdict"], "B2_fit": sall["R2"]["fit"], "BV": sall["V"],
         "B4_mhz": sall["S4"]["verdict_mhz"], "B4_w": sall["S4"]["verdict_w"], "B4": sall["S4"],
         "S1": sall["S1"], "S2": sall["S2"], "S3": sall["S3"], "arms": sall["arms"], "proxies": sall["proxies"],
         "probes_counted": sall["probes_counted"], "probes_line": sall["probes_line"], "probes_hold": sall["probes_hold"],
         "per_probe_line": sall["R1"]["per_probe"], "per_probe_hold": sall["R2"]["per_probe"], "rest_die": sall["_maps"]["px"]}
    B["B3c"] = b3c(sall, P133["partB"]["baseline_probes"], [p["probe"] for p in p133], P133)
    return B


# ------------------------------------------------------------------------------------------------ part A, beside
def minutes(data, spec, pa):
    """Beside: one hold minute by minute on the scorer's own in-kernel samples and fine-W mask; the wander; c by 5-min window."""
    pdir = os.path.join(data, spec["step"])
    if not os.path.exists(os.path.join(pdir, "runs.jsonl")):
        return None
    r, procs, ws = X.work_samples(pdir, spec["run"])
    if not ws:
        return None
    clock = spec["clock_mhz"]
    mask, _ = X.fine_mask(ws, procs, clock)
    t0 = min(p["t_start_ms"] for p in procs)
    bins = {}
    for x, m in zip(ws, mask):
        k = int((x["t"] - t0) // 60000)
        b = bins.setdefault(k, {"die": [], "w": [], "fine": [], "at": 0, "n": 0})
        b["n"] += 1
        if x["die"] is not None:
            b["die"].append(x["die"])
        if x["w"] is not None:
            b["w"].append(x["w"])
        if m:
            b["fine"].append(x["w"])
        if x["mhz"] == clock:
            b["at"] += 1
    rows = [{"min": k, "die": rnd(mean(b["die"]), 3), "w": rnd(mean(b["w"]), 3), "fine_w": rnd(mean(b["fine"]), 3) if b["fine"] else None,
             "share_clock": rnd(b["at"] / b["n"], 3), "n": b["n"]} for k, b in sorted(bins.items())]
    late = [x["die"] for x in rows if x["min"] >= 8 and x["die"] is not None and x["n"] >= 300]
    wander = {"from_min": 8, "lo": rnd(min(late), 3), "hi": rnd(max(late), 3), "range_c": rnd(max(late) - min(late), 3)} if late else None
    return {"rows": rows, "wander": wander, "t_first_ms": t0}


def c_by_window(data, spec, pa, idle):
    pdir = os.path.join(data, spec["step"])
    r, procs, ws = X.work_samples(pdir, spec["run"])
    if not ws or not idle:
        return None
    clock = spec["clock_mhz"]
    mask, _ = X.fine_mask(ws, procs, clock)
    t0 = min(p["t_start_ms"] for p in procs)
    t1 = max(p["t_end_ms"] for p in procs)
    out = []
    s = 5
    while t0 + (s + 5) * 60000 <= t1 + 1:
        w = X.win_stats(ws, mask, t0 + s * 60000, t0 + (s + 5) * 60000, clock, pa["fine_min_share"])
        if w and w["w"] - idle["w"] > 0:
            out.append({"start_min": s, "c": rnd((w["die"] - idle["die"]) / (w["w"] - idle["w"]), 4), "die": rnd(w["die"], 3), "w": rnd(w["w"], 3)})
        s += 1
    return out


def peaks(data):
    out = {}
    for s in STEPS:
        pdir = os.path.join(data, s)
        try:
            sess, runs, launches, q0 = R.load_session(pdir)
        except (OSError, ValueError):
            continue
        mw = md = mh = None
        n_over = {"85": 0, "80": 0}
        for r in runs:
            for d in R.jl(os.path.join(pdir, r["tel"])):
                try:
                    ms = (d.get("temp_c") or {}).get("minshire") or [None, None, None]
                    w, die, hot = d.get("board_w"), ms[0], (ms[2] if len(ms) > 2 else None)
                except (TypeError, AttributeError, IndexError):
                    continue
                if isinstance(w, (int, float)):
                    mw = w if mw is None else max(mw, w)
                    n_over["85"] += w > 85
                    n_over["80"] += w > 80
                if isinstance(die, (int, float)):
                    md = die if md is None else max(md, die)
                if isinstance(hot, (int, float)):
                    mh = hot if mh is None else max(mh, hot)
        out[s] = {"board_w_max": mw, "die_mean_max": md, "hottest_max": mh, "samples_over_85w": n_over["85"], "samples_over_80w": n_over["80"]}
    return out


def r1(A, P133):
    rp = P133["partA"]["replicate"]
    band = rp["band"]
    out = {}
    for h in ("H-I8", "H-F32"):
        a2 = (A.get(h) or {}).get("A2") or {}
        e = rp["e111"][h]
        if a2.get("c_lo") is None:
            out[h] = {"verdict": "NOT_SCORED"}
            continue
        ratio = a2["c"] / e["c"]
        lo, hi = a2["c_lo"] / e["c_hi"], a2["c_hi"] / e["c_lo"]
        out[h] = {"c_e133": a2["c"], "c_e111": e["c"], "ratio": rnd(ratio, 4), "lo": rnd(lo, 4), "hi": rnd(hi, 4), "band": band,
                  "verdict": X.band_verdict(lo, hi, band)}
    return out


def r2(A, P133):
    rc = P133["partA"]["room_clock"]
    h = A.get("H-F32") or {}
    plat = h.get("plateau") or {}
    idle = (A.get("idles") or {}).get("W2") or {}
    if not plat or idle.get("die") is None:
        return {"verdict": "NOT_SCORED"}
    share = plat.get("share_clock")
    v = "AT THE FLOOR" if share is not None and share >= P133["partA"]["clock_share_min"] else "AT THE TRIP"
    pred = "AT THE TRIP" if idle["die"] < rc["threshold_idle_c"] else "AT THE FLOOR"
    return {"share_at_600": share, "plateau_mhz": plat.get("mhz"), "plateau_die": plat.get("die"), "plateau_w": plat.get("w"),
            "w2_rest_idle_die": idle["die"], "predicted": pred, "verdict": v, "as_predicted": v == pred}


# ------------------------------------------------------------------------------------------------ regression
def regression(P98, P111):
    out = {}
    p98 = e98_probes(P111, P98)
    s98 = X.score98(p98, P98)
    bad = X.regression_check(s98, json.load(open(os.path.join(E98D, "results.json"))))
    out["e98"] = {"keys_differing": bad, "ok": not bad}
    committed = json.load(open(os.path.join(E111D, "results.json")))
    sall = X.score98(p98 + e111_probes(P98), P98)
    mine = {"B0_gate": sall["R0"]["gate"], "B1": sall["R1"]["verdict"], "B1_fit": sall["R1"]["fit"], "B2": sall["R2"]["verdict"],
            "B2_fit": sall["R2"]["fit"], "BV": sall["V"], "B4": sall["S4"], "per_probe_line": sall["R1"]["per_probe"],
            "per_probe_hold": sall["R2"]["per_probe"], "rest_die": sall["_maps"]["px"], "probes_counted": sall["probes_counted"]}
    badb = [k for k, v in mine.items() if json.dumps(jround(v), sort_keys=True) != json.dumps(jround(committed["B"][k]), sort_keys=True)]
    out["e111_partB"] = {"keys_differing": badb, "ok": not badb}
    A = X.part_a(E111D, P111, E.History(E111D), R.jl(os.path.join(E111D, "phone.jsonl")))
    bada = [k for k in sorted(set(A) | set(committed["A"])) if json.dumps(jround(A.get(k)), sort_keys=True) != json.dumps(jround(committed["A"].get(k)), sort_keys=True)]
    out["e111_partA"] = {"keys_differing": bada, "ok": not bada}
    out["ok"] = all(v["ok"] for v in out.values() if isinstance(v, dict))
    return out, p98


# ------------------------------------------------------------------------------------------------ main
def tally(res, P133):
    pa, pb = P133["partA"]["predicted"], P133["partB"]["predicted"]
    v = []
    for h in ("H-I8", "H-F32"):
        x = res["A"].get(h) or {}
        v.append((f"E133-A1 {h}", (x.get("A1") or {}).get("verdict", "NOT_SCORED"), pa[h]["verdicts"]["A1"]))
        a2 = x.get("A2") or {}
        for bname, key in (("prior_aifoundry2", "A2_prior"), ("lab_model_sept", "A2_lab"), ("e97_aifoundry3_plateau", "A2_e97"), ("line_76s", "A2_line")):
            v.append((f"E133-A2 {h} {bname}", a2.get(bname, "NOT_SCORED"), pa[h]["verdicts"][key]))
    v.append(("E133-A3", res["A"]["A3"]["verdict"], pa["H-F32"]["verdicts"]["A3"]))
    for h in ("H-I8", "H-F32"):
        v.append((f"E133-R1 {h}", res["R1"][h]["verdict"], pa[h]["verdicts"]["R1"]))
    v.append(("E133-R2", res["R2"]["verdict"], res["R2"].get("predicted", "NOT_SCORED")))
    B = res["B"]
    v += [("E133-B0", B["B0_gate"], pb["B0"]), ("E133-B1", B["B1"], pb["B1"]), ("E133-B2", B["B2"], pb["B2"]), ("E133-BV", B["BV"], pb["BV"]),
          ("E133-B3c line", B["B3c"].get("verdict_line"), P133["partB"]["b3c"]["predicted"]["line_verdict"]),
          ("E133-B3c hold", B["B3c"].get("verdict_hold"), P133["partB"]["b3c"]["predicted"]["hold_verdict"]),
          ("E133-B4 MHz", B["B4_mhz"], pb["B4"]), ("E133-B4 W", B["B4_w"], pb["B4"])]
    rows = []
    for name, got, pred in v:
        side = "no side predicted" if str(pred).startswith("no side") else ("as predicted" if got == pred else "NOT as predicted")
        rows.append({"rule": name, "verdict": got, "predicted": pred, "against": side})
    t = {}
    for r in rows:
        t[r["verdict"]] = t.get(r["verdict"], 0) + 1
    return rows, t


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("data", nargs="?")
    ap.add_argument("--out")
    ap.add_argument("--pred", default=os.path.join(HERE, "predictions-e133.json"))
    ap.add_argument("--regression", action="store_true")
    a = ap.parse_args()
    P133 = json.load(open(a.pred))
    P111 = json.load(open(P111_PATH))
    P98 = json.load(open(P98_PATH))
    reg, p98 = regression(P98, P111)
    print("E133: E111's two holds again on aifoundry2 in the morning's room, and the morning probe; its own governor, nothing set")
    print("REGRESSION (before anything is scored):", json.dumps(reg))
    if a.regression or not reg["ok"]:
        if not reg["ok"]:
            print("REFUSED: the regression does not reproduce the committed results")
        if a.out:
            json.dump({"regression": reg}, open(a.out, "w"), indent=1, sort_keys=True)
        return 0 if reg["ok"] else 2
    res = {"experiment": "E133", "predictions_sha256": hashlib.sha256(open(a.pred, "rb").read()).hexdigest(), "regression": reg}
    H = E.History(a.data)
    phone = R.jl(os.path.join(a.data, "phone.jsonl"))
    qrecs = R.jl(os.path.join(a.data, "queue.jsonl"))
    # ---- part A
    A = X.part_a(a.data, P133, H, phone)
    res["A"] = A
    res["R1"] = r1(A, P133)
    res["R2"] = r2(A, P133)
    res["beside"] = {}
    for h, spec in P133["partA"]["holds"].items():
        ib, ia = (A.get("idles") or {}).get(spec["idle_before"]), (A.get("idles") or {}).get(spec["idle_after"])
        im = {"die": (ib["die"] + ia["die"]) / 2.0, "w": (ib["w"] + ia["w"]) / 2.0} if ib and ia else ib
        res["beside"][h] = {"minutes": minutes(a.data, spec, P133["partA"]), "c_by_5min_window": c_by_window(a.data, spec, P133["partA"], im)}
    res["peaks"] = peaks(a.data)
    # ---- part B
    p111 = e111_probes(P98, prefix="E111-")
    p133 = e133_probes(a.data, H, P98, qrecs)
    res["B"] = part_b(p98, p111, p133, P98, P133)
    res["probes_e133"] = p133
    # ---- the session
    res["queue"] = [q for q in qrecs if q.get("kind") in ("queue_start", "start", "end", "skip", "queue_end")]
    res["verdict_rows"], res["tally"] = tally(res, P133)
    # ---- print
    print("\nVERDICTS")
    for r in res["verdict_rows"]:
        print(f"  {r['rule']:40s} {str(r['verdict']):18s} predicted {str(r['predicted'])[:60]:60s} {r['against']}")
    print("  tally", json.dumps(res["tally"]))
    print("\nPART A, the holds")
    print("  idles", json.dumps(A["idles"]))
    for h in ("H-I8", "H-F32"):
        x = A.get(h, {})
        print(f"  {h}: {json.dumps({k: x.get(k) for k in ('kind', 'clock_mhz', 'processes_run', 'processes_planned', 'minutes', 'dips', 'complete', 'clock_held')})}")
        for k in ("plateau", "previous", "A1", "A2", "asymptote", "A4"):
            print(f"     {k} {json.dumps(x.get(k))}")
        bs = res["beside"][h]
        if bs["minutes"]:
            print(f"     wander (minute bins from minute 8) {json.dumps(bs['minutes']['wander'])}")
            for row in bs["minutes"]["rows"]:
                print(f"       min {row['min']:2d}  die {row['die']}  W {row['w']}  fine {row['fine_w']}  share {row['share_clock']}  n {row['n']}")
        if bs["c_by_5min_window"]:
            print("     c by 5-min window: " + ", ".join(f"{z['start_min']}: {z['c']}" for z in bs["c_by_5min_window"]))
    print("  A3", json.dumps(A["A3"]))
    print("  R1", json.dumps(res["R1"]))
    print("  R2", json.dumps(res["R2"]))
    print("  peaks", json.dumps(res["peaks"]))
    print("\nPART B, the drift")
    B = res["B"]
    for k in ("B0_gate", "R0", "B1", "B1_fit", "B2", "B2_fit", "BV", "B3c", "B4"):
        print(f"  {k}: {json.dumps(B[k])}")
    print("  rest die (W-derived)", json.dumps({k: rnd(v, 3) for k, v in B["rest_die"].items()}))
    print("  line per probe", json.dumps(B["per_probe_line"]), "\n  hold per probe", json.dumps(B["per_probe_hold"]))
    for pr in p133:
        print(f"  {pr['probe']}: rest W {pr.get('rest_w')} ({pr.get('rest_source')}), rest20 {json.dumps(pr.get('rest20'))}, rest60 {json.dumps(pr.get('rest60'))}")
        for i in sorted(pr["runs"]):
            r = pr["runs"][i]
            print(f"     {i} {r['kind']:14s} W {r['w']:.2f} die {r['die']:.2f} line {r['line']:.2f} MHz {r['mhz']:.0f} fine {r.get('fine_w')} gate {r['gate']}")
        print(f"     hold {json.dumps(pr.get('hold'))[:600]}")
    if a.out:
        json.dump(res, open(a.out, "w"), indent=1, sort_keys=True, default=str)
    return 0


if __name__ == "__main__":
    sys.exit(main())
