#!/usr/bin/env python3
"""E173 and E174 (Q142(kg)): what the two governed-burst scorers share, as registered in E173.md and E174.md before any data. Standard library;
the lines come from Q142(p)'s frozen predictor (predict_pool8_a2.py, through e173_common.a2p()), so this file holds no line of its own.

  * the bootstrap line at the scored n: predict_pool8.boot_range(ref, n, rule, stat) as frozen (A2-3 (a), (g)): seed 80,000 + the sum of the
    rule id's character codes, 20,000 draws, [vals[int(0.025 x 20000)], vals[int(0.975 x 20000) - 1]];
  * the paired engine (E173.md "The paired engine"): the same seed and index form over n tile indices drawn with replacement;
  * the fixed lines (A2-G, A2-Bg, A2-Bp, C0-B) and A2-R2's registered form (FAIL if any of G, Bg, Bp FAILs; PASS if all three PASS; else NOT
    SCORED: on pool 8 it can read FAIL through Bp, never PASS);
  * the session's zeros-anchor reads for burst(), from the three zeros anchors' counted bursts ONLY (anything else reaching them is refused);
  * the sessions that must carry a C log (E173.md, E174.md: smoke, stoptest-board and every BURST session the queue started that ran a work
    launch; stoptest-die runs none), read from the queue's record and the sessions' launches, and the check that every one has a check of C;
  * the run-to-order map: each session's protocol (named in its eNNN.json with its sha256) must be one of the kit's committed protocols, whose
    order entries must be the registered order's runs (label and pass at the registered index).
SPDX-License-Identifier: Apache-2.0
"""
import gzip
import json
import math
import os
import random

DRAWS = 20000


def rms(v):
    v = [float(x) for x in v if x is not None]
    return math.sqrt(sum(x * x for x in v) / len(v)) if v else None


def mean(v):
    v = [float(x) for x in v if x is not None]
    return sum(v) / len(v) if v else None


def r4(x, n=4):
    return None if x is None else round(x, n)


def seed_of(rule, A):
    return A.P().seed_of(rule)


def boot_rule(rule, errs, ref, minimum, A, stat="rms"):
    """a bootstrap rule at the scored n: PASS at or below the 97.5% point, else FAIL (A2-3 (a), (g)); NOT SCORED under the minimum"""
    n = len(errs)
    out = {"rule": rule, "n": n, "minimum": minimum, "stat": stat, "seed": seed_of(rule, A), "ref_n": len(ref), "ref_rms": r4(rms(ref))}
    if n < minimum or n == 0:
        out["verdict"] = f"NOT SCORED (n {n} < {minimum})"
        out["rms"], out["mean"] = r4(rms(errs)), r4(mean(errs))
        return out
    lo, hi = A.P().boot_range(ref, n, rule, stat)
    x = rms(errs) if stat == "rms" else mean(errs)
    out.update(rms=r4(rms(errs)), mean=r4(mean(errs)), range_95=[lo, hi], verdict="PASS" if x <= hi else "FAIL",
               below_the_2p5_point=bool(x < lo))
    return out


def paired(rule, a, b, minimum, A, draws=DRAWS):
    """E173.md's paired engine: the 95% interval of rms(a) - rms(b) over the set's tiles drawn with replacement; BETTER if its upper end < 0,
    WORSE if its lower end > 0, else NOT RESOLVED; NOT SCORED under the minimum"""
    n = len(a)
    out = {"rule": rule, "n": n, "minimum": minimum, "seed": seed_of(rule, A)}
    if n < minimum or n == 0 or n != len(b):
        out["verdict"] = f"NOT SCORED (n {n} < {minimum})" if n == len(b) else "NOT SCORED (unpaired)"
        return out
    rng = random.Random(seed_of(rule, A))
    vals = []
    for _ in range(draws):
        idx = [rng.randrange(n) for _ in range(n)]
        vals.append(rms([a[i] for i in idx]) - rms([b[i] for i in idx]))
    vals.sort()
    lo, hi = vals[int(0.025 * draws)], vals[int(0.975 * draws) - 1]
    out.update(point=r4(rms(a) - rms(b)), ci95=[r4(lo), r4(hi)], rms_a=r4(rms(a)), rms_b=r4(rms(b)),
               verdict="BETTER" if hi < 0 else ("WORSE" if lo > 0 else "NOT RESOLVED"))
    return out


def fixed_G(errs_mhz, minimum):
    n = len(errs_mhz)
    out = {"rule": "P8-A2-G", "n": n, "minimum": minimum, "line": "rms <= 4.0 MHz AND |mean| <= 2.0 MHz", "rms": r4(rms(errs_mhz)), "mean": r4(mean(errs_mhz))}
    if n < minimum or n == 0:
        out["verdict"] = f"NOT SCORED (n {n} < {minimum})"
        return out
    ok_r, ok_m = rms(errs_mhz) <= 4.0, abs(mean(errs_mhz)) <= 2.0
    out.update(rms_le_line=ok_r, mean_within_line=ok_m, verdict="PASS" if ok_r and ok_m else "FAIL")
    return out


def fixed_mean(rule, errs_w, minimum, line_w=0.5):
    n = len(errs_w)
    out = {"rule": rule, "n": n, "minimum": minimum, "line": f"|mean| <= {line_w} W", "rms": r4(rms(errs_w)), "mean": r4(mean(errs_w))}
    if n < minimum or n == 0:
        out["verdict"] = f"NOT SCORED (n {n} < {minimum})"
        return out
    ok = abs(mean(errs_w)) <= line_w
    out.update(mean_within_line=ok, verdict="PASS" if ok else "FAIL")
    return out


def fixed_mean_rms(rule, errs_w, minimum):
    """A2-Bp and C0-B: |mean| <= 0.5 W AND rms <= 1.0 W; a FAIL names the line that failed"""
    n = len(errs_w)
    out = {"rule": rule, "n": n, "minimum": minimum, "line": "|mean| <= 0.5 W AND rms <= 1.0 W", "rms": r4(rms(errs_w)), "mean": r4(mean(errs_w))}
    if n < minimum or n == 0:
        out["verdict"] = f"NOT SCORED (n {n} < {minimum})"
        return out
    ok_m, ok_r = abs(mean(errs_w)) <= 0.5, rms(errs_w) <= 1.0
    out.update(mean_within_line=ok_m, rms_le_line=ok_r)
    if ok_m and ok_r:
        out["verdict"] = "PASS"
    else:
        why = []
        if not ok_m:
            why.append("mean " + ("measured above predicted" if mean(errs_w) > 0 else "measured below predicted"))
        if not ok_r:
            why.append("rms over 1.0 W")
        out["verdict"] = "FAIL (" + "; ".join(why) + ")"
    return out


def r2(G, Bg, Bp):
    """A2-R2 as registered: PASS if G, Bg and Bp all PASS; FAIL if any FAILs; else NOT SCORED (dfe226f1 section 1: on pool 8 it can read FAIL
    through Bp, never PASS)"""
    vs = [x["verdict"] for x in (G, Bg, Bp)]
    if any(v.startswith("FAIL") for v in vs):
        v = "FAIL"
    elif all(v == "PASS" for v in vs):
        v = "PASS"
    else:
        v = "NOT SCORED"
    return {"rule": "P8-A2-R2", "components": {"P8-A2-G": vs[0], "P8-A2-Bg": vs[1], "P8-A2-Bp": vs[2]}, "verdict": v,
            "form": "PASS if G, Bg and Bp all PASS; FAIL if any FAILs; else NOT SCORED"}


def anchors_from(cells, zeros_labels):
    """the session's zeros-anchor reads as burst() takes them, from the zeros anchors' counted bursts only: {format: [{burst_w, burst_mhz,
    die_start}]}; None if none. zeros_labels = {format: label}; a cell whose label is not one of them never enters"""
    out, used = {}, []
    for t, lab in zeros_labels.items():
        c = cells.get(lab)
        if not c:
            continue
        rr = [{"burst_w": w, "burst_mhz": f, "die_start": T} for w, f, T in zip(c["burst_w_runs"], c["burst_mhz_runs"], c["die_start_runs"])
              if None not in (w, f, T)]
        if rr:
            out[t] = rr
            used.append(lab)
    return (out or None), used


def refuse_foreign_anchor(used, zeros_labels):
    """the registered refusal: only the three zeros anchors reach the primary's anchors input"""
    bad = sorted(set(used) - set(zeros_labels.values()))
    if bad:
        raise SystemExit(f"refused: a tile other than the zeros anchors would reach the primary's anchors input: {bad}")


# ------------------------------------------------------------------ the sessions that must carry a C log
def _read_jsonl(p):
    op = gzip.open if p.endswith(".gz") else open
    with op(p, "rt") as f:
        for ln in f:
            ln = ln.strip()
            if ln:
                try:
                    yield json.loads(ln)
                except ValueError:
                    continue


def _first(d, *names):
    for n in names:
        p = os.path.join(d, n)
        if os.path.exists(p):
            return p
    return None


def work_launches(sdir):
    p = _first(sdir, "launches.jsonl", "launches.jsonl.gz")
    if not p:
        return 0
    return sum(1 for r in _read_jsonl(p) if r.get("role") == "work")


def is_dry(sdir):
    p = os.path.join(sdir, "session.json")
    try:
        with open(p) as f:
            return bool(json.load(f).get("dry"))
    except (OSError, ValueError):
        return False


def required_c_logs(qdir, listed=("smoke", "stoptest-board", "s1")):
    """the sessions of a queue's record that must carry a C log: every listed one and every BURST resume s2-s6 the queue started that ran a work
    launch (stoptest-die runs none). Returns (required, report): required = [session names]; report = what was read, per session"""
    started = []
    qp = _first(qdir, "queue.jsonl", "queue.jsonl.gz")
    if qp:
        for r in _read_jsonl(qp):
            if r.get("kind") == "session_start" and r.get("name"):
                started.append(r["name"])
    names = list(dict.fromkeys(started + [n for n in listed if os.path.isdir(os.path.join(qdir, n))]))
    req, rep = [], {}

    def burst_session(n):
        return len(n) > 1 and n[0] == "s" and n[1:].isdigit()
    for n in names:
        sd = os.path.join(qdir, n)
        if not os.path.isdir(sd):
            rep[n] = "started in the queue's record, no directory"
            if n in listed or burst_session(n):
                req.append(n)
            continue
        wl = work_launches(sd)
        dry = is_dry(sd)
        has = bool(_first(sd, "c-log.jsonl", "c-log.jsonl.gz"))
        rep[n] = {"work_launches": wl, "dry": dry, "c_log": has}
        if dry:
            continue
        if n == "stoptest-die":
            if wl:
                rep[n]["note"] = "stoptest-die ran a work launch: it must carry a C log too"
                req.append(n)
            continue
        if (n in listed or burst_session(n)) and wl > 0:
            req.append(n)
    return req, rep


def check_c_coverage(qdir, ccheck_files, listed):
    """the registered refusal: every required session has a check of C given (by its collector's name, ccheck-<session>.json[.gz]); returns
    (ok, missing, required, report)"""
    req, rep = required_c_logs(qdir, listed)
    given = {}
    for p in ccheck_files or []:
        b = os.path.basename(p)
        for suf in (".json.gz", ".json"):
            if b.startswith("ccheck-") and b.endswith(suf):
                given[b[len("ccheck-"):-len(suf)]] = p
    missing = [n for n in req if n not in given]
    return (not missing), missing, req, rep


# ------------------------------------------------------------------ each session's protocol and the run-to-order map
def protocol_map(kit_dir, rundir, exp_json, orders, protocols):
    """the session's protocol, named in <rundir>/<exp_json> with its sha256, must be one of `protocols` (the kit's committed files) and hash as
    recorded; its BURST block's order_entries must be the runs of the order it names (order_source: the registered "order", or the dry twin's
    "dry_order", both in the predictions file) at their index there. Returns ({run idx: order entry}, the protocol's name)"""
    p = os.path.join(rundir, exp_json)
    try:
        with open(p) as f:
            rec = json.load(f)
        name, sha = rec["protocol"], rec["protocol_sha256"]
    except (OSError, ValueError, KeyError):
        raise SystemExit(f"refused: {rundir} has no readable {exp_json} naming its protocol and its sha256")
    if name not in protocols:
        raise SystemExit(f"refused: {rundir} ran {name}, not one of the kit's protocols {sorted(protocols)}")
    pp = os.path.join(kit_dir, name)
    import hashlib
    with open(pp, "rb") as f:
        got = hashlib.sha256(f.read()).hexdigest()
    if got != sha:
        raise SystemExit(f"refused: {rundir}'s protocol {name} was {sha[:12]}, the kit's file is {got[:12]}")
    with open(pp) as f:
        proto = json.load(f)
    entries = proto.get("order_entries")
    src = proto.get("order_source")
    if not isinstance(entries, list) or src not in orders:
        raise SystemExit(f"refused: {name} has no order_entries, or an order_source ({src}) the predictions do not hold")
    reg = {o["idx"]: o for o in orders[src]}
    out = {}
    for i, e in enumerate(entries):
        if e.get("idx") != i:
            raise SystemExit(f"refused: {name}'s order entry {i} has idx {e.get('idx')}")
        o = reg.get(e.get("registered_idx"))
        if o is None or o["label"] != e["label"] or o["pass"] != e["pass"]:
            raise SystemExit(f"refused: {name}'s entry {i} ({e.get('label')}, pass {e.get('pass')}) is not the {src}'s run {e.get('registered_idx')}")
        out[i] = e
    return out, name


def pass_of_map(m):
    def f(r):
        i = r.get("idx")
        e = m.get(i) if isinstance(i, int) else None
        if e is None or e["label"] != r.get("label"):
            raise SystemExit(f"refused: run {r.get('run')} (idx {i}, label {r.get('label')}) is not its protocol's run at that idx")
        return e["pass"]
    return f
