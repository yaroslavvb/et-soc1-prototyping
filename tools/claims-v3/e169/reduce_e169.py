#!/usr/bin/env python3
"""E169 (Q141(s)): the registered reduction, E158's reduce_e158.py ported. It holds no rule; score_e169.py scores what reduce() returns.
Standard library only.

  * per run and per cell: E126's collect(), imported unchanged (E119's per-run loop: reduce_hpl.run_metrics, reduce_kspeed.burst_extra,
    reduce_e83.a1_view), exactly as E158's reducer calls it;
  * per shape and format, every pass pooled: E119's clock_x (T800 the mean T of the launches at or above 790 MHz), through collect();
  * per pass: E158's per_pass(), its code unchanged but for its block map, which is an argument here: E169's blocks are A (pass 1), B (2),
    C (3), D (4), E (5) and F (the formats, pass 1 of fp16 and of int8); E158's were A, B and E (1), C (2), F (3). The mean T and the
    cycles per op over the work launches at or above 790 MHz, and their count, per (pass, shape.format);
  * per run, the cool gate's record (reached or not) and the checks of C, read from runs.jsonl and collect()'s runs.

selftest_e169.py runs reduce() with E158's block map on E158's committed session and checks that it reproduces E158's results.json
(per_shape, t800_by_pass, launches_800_by_pass, cells, checks) exactly, before E158's own score() reproduces E158's registered verdicts.

    (imported by score_e169.py and selftest_e169.py)
SPDX-License-Identifier: Apache-2.0
"""
import gzip
import json
import os
import sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
LAB = os.path.normpath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(LAB, "tools/claims-v3/e126"))
import reduce_e126 as R126  # noqa: E402  (E126's registered reducer: collect, tel_peaks; E119's clock_x)

PASS_OF_BLOCK_E169 = {"A": 1, "B": 2, "C": 3, "D": 4, "E": 5, "F": 1}
PASS_OF_BLOCK_E158 = {"A": 1, "B": 1, "C": 2, "E": 1, "F": 3}


def per_pass(rundirs, pass_of_block):
    """E158's per_pass (reduce_e158.py), unchanged but for the block map: per (pass, shape.format) the mean T (us) and cycles per op
    (cycles_max / iters) over the work launches at or above 790 MHz, every kind pooled, and their count"""
    T, CY = {}, {}
    for rd in rundirs:
        rp = os.path.join(rd, "runs.jsonl")
        lp = os.path.join(rd, "launches.jsonl")
        if not os.path.exists(rp):
            continue
        runs = {}
        for ln in open(rp):
            r = json.loads(ln)
            runs[r["run"]] = r
        op = open
        if not os.path.exists(lp):
            lp, op = lp + ".gz", gzip.open
        if not os.path.exists(lp):
            continue
        with op(lp, "rt") as f:
            for ln in f:
                L = json.loads(ln)
                r = runs.get(L.get("run"))
                if r is None or L.get("role") != "work" or r["block"] not in pass_of_block:
                    continue
                ps = pass_of_block[r["block"]]
                parts = r["label"].split("-")
                key = f"{ps}|{parts[0]}.{parts[1]}"
                for k in L.get("sparsity", []):
                    if k.get("test") == "fma" and k.get("launch", 0) >= 0 and k.get("ok") and k.get("wall_s", 0) >= 0.1 and k.get("iters"):
                        fr = k.get("cycles_max", 0) / k["wall_s"] / 1e6
                        if fr >= 790:
                            T.setdefault(key, []).append(k["wall_s"] / k["iters"] * 1e6)
                            CY.setdefault(key, []).append(k.get("cycles_max", 0) / k["iters"])
    return ({k: sum(v) / len(v) for k, v in T.items()}, {k: sum(v) / len(v) for k, v in CY.items()}, {k: len(v) for k, v in T.items()})


def gates(rundirs):
    """per run of the session (not the smoke): its block, label, and whether its cool gate was reached"""
    out = []
    for rd in rundirs:
        rp = os.path.join(rd, "runs.jsonl")
        if not os.path.exists(rp):
            continue
        for ln in open(rp):
            r = json.loads(ln)
            if r.get("block") == "SMOKE":
                continue
            g = r.get("gate") or {}
            out.append({"session": os.path.basename(os.path.normpath(rd)), "run": r.get("run"), "block": r.get("block"), "label": r.get("label"),
                        "gate_mode": g.get("mode"), "gate_reached": g.get("reached"), "gate_held_s": g.get("held_s")})
    return out


def reduce(rundirs, P, pass_of_block=None):
    """P: a dict with E126's collect() keys (relation.B, admission) and clock_x's (rules.R2_clock_buys): kit-e169.json for E169,
    predictions-e158.json for the self-test. Returns the reduction as plain data."""
    pob = PASS_OF_BLOCK_E169 if pass_of_block is None else pass_of_block
    runs, cells, per, t800, checks, skipped = R126.collect(rundirs, P)
    passes, cyc, nl = per_pass(rundirs, pob)
    cyc_by = {}
    for k, v in cyc.items():
        ps, key = k.split("|")
        cyc_by.setdefault(key, {})[f"pass{ps}"] = round(v, 1)
    return {"sessions": [os.path.basename(os.path.normpath(x)) for x in rundirs], "runs": runs, "n_runs": len(runs), "skipped": skipped,
            "per_shape": per, "t800_us": t800, "t800_by_pass": {k: round(v, 5) for k, v in passes.items()}, "t800_by_pass_raw": passes,
            "cycles_per_op_800_by_pass": cyc_by, "launches_800_by_pass": nl, "cells": cells, "checks": checks,
            "run_checks": [{"cell": m.get("cell"), "block": m.get("block_orig"), "session": m.get("session"), "checks": m.get("checks")} for m in runs],
            "gates": gates(rundirs), "peaks": R126.tel_peaks(rundirs),
            "config_after": sorted({json.dumps({k: (m["config_after"] or {}).get(k) for k in ("tdp_w", "temp_threshold_c")}) for m in runs if m.get("config_after")}),
            "dry": any(m["dry"] for m in runs), "pass_of_block": pob}
