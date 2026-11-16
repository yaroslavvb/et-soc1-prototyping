#!/usr/bin/env python3
"""E199 (reg-e199, Q190), a desk reading of code on E192's own data (REPORTED: it decides nothing and changes no rule): THE TRANSPORT
RULES applied to aifoundry3 against itself, split by passes. E192's committed session is reduced twice by E199's pipeline
(prefilter_e199.py, then E192's reduce_intbits.py, unchanged), once on passes 0-4 and once on passes 0 and 5-8 (pass 0 is each half's
set-aside warm-up, as the reducer takes the first pass of its input), so each half has 4 measured passes; then score_e199.py's rules
score half B against half A as the forecast, and half A against half B. One card and one session: whatever the rules read here is
how often they miss when nothing changes but the passes, at 4 passes a side (E199 has 8 a side, so its intervals are narrower).

    /usr/bin/python3 -I -B tools/claims-v3/e199/desk/split_e192.py <an empty work dir outside the repository> [--out <split.json>]

SPDX-License-Identifier: Apache-2.0
"""
import gzip
import importlib.util
import json
import os
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
E199 = os.path.dirname(HERE)
TOP = os.path.abspath(os.path.join(E199, "..", "..", ".."))
D = os.path.join(TOP, "docs/reports/data/2026-11-14-e192-intbits-aifoundry3")
RED = os.path.join(TOP, "tools/claims-v3/e192/proposal/src/reduce_intbits.py")
PRE = os.path.join(E199, "prefilter_e199.py")
HALVES = {"A": {0, 1, 2, 3, 4}, "B": {0, 5, 6, 7, 8}}


def load(name):
    spec = importlib.util.spec_from_file_location(name + "_split", os.path.join(E199, name + ".py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def main():
    work = sys.argv[1]
    out_json = sys.argv[sys.argv.index("--out") + 1] if "--out" in sys.argv else None
    if os.path.exists(work) and os.listdir(work):
        raise SystemExit("REFUSED: %s is not empty" % work)
    fc, sc = load("forecast_e199"), load("score_e199")
    forecast = json.load(open(os.path.join(E199, "forecast-e199.json")))
    with gzip.open(os.path.join(D, "run/telemetry.jsonl.gz"), "rb") as f:
        tel = f.read()
    red = {}
    for h, keep in HALVES.items():
        run = os.path.join(work, "run-" + h)
        os.makedirs(run)
        with open(os.path.join(D, "run/runs.jsonl")) as f, open(os.path.join(run, "runs.jsonl"), "w") as g:
            for line in f:
                if line.startswith("{") and json.loads(line).get("pass") in keep:
                    g.write(line)
        shutil.copyfile(os.path.join(D, "run/marks.jsonl"), os.path.join(run, "marks.jsonl"))
        with open(os.path.join(run, "telemetry.jsonl"), "wb") as g:
            g.write(tel)
        flt = run + "-filtered"
        r = subprocess.run([sys.executable, "-I", "-B", PRE, run, flt], capture_output=True, text=True)
        if r.returncode != 0:
            raise SystemExit("prefilter failed: %s %s" % (r.stdout, r.stderr))
        o = os.path.join(work, "intbits-%s.json" % h)
        r = subprocess.run([sys.executable, "-I", "-B", RED, flt, "--out", o], capture_output=True, text=True)
        if r.returncode != 0:
            raise SystemExit("reducer failed: %s %s" % (r.stdout, r.stderr))
        red[h] = json.load(open(o))
    rep = {"what": "THE TRANSPORT RULES on aifoundry3 against itself, split by passes (E192's committed session; desk reading, "
                   "REPORTED)", "halves": {h: sorted(k) for h, k in HALVES.items()}, "used": {}, "directions": {}}
    lines = []
    for h in ("A", "B"):
        rep["used"][h] = [p for p in red[h]["passes"] if list(p) != list(red[h]["warmup"])]
    for fh, ch in (("A", "B"), ("B", "A")):
        fams, reps = fc.families_from(red[fh])
        f2 = dict(forecast, families=fams, reported=reps)
        res = sc.score(f2, red[ch])
        rep["directions"]["%s as card 1 against %s as the forecast" % (ch, fh)] = {
            "verdicts": res["verdicts"],
            "families": {fid: {"decided": res["families"][fid]["decided"], "T1": res["families"][fid]["T1"],
                               "T2": res["families"][fid]["T2"], "s_hat": res["families"][fid]["scale"]["s_hat"],
                               "s_hat_se": res["families"][fid]["scale"]["s_hat_se"],
                               "s_star": res["families"][fid]["scale"]["s_star"],
                               "not_decided": [r["key"] + ": " + r["why"] for r in res["families"][fid]["prices"]
                                               if not r["decided"]],
                               "T1_misses": ["%s z %.2f" % (r["key"], r["z_d"]) for r in res["families"][fid]["prices"]
                                             if r["decided"] and not r["holds_T1"]]}
                         for fid in sc.FAMILY_IDS}}
        lines.append("half %s (passes %s) as card 1 against half %s (passes %s) as the forecast:" % (
            ch, rep["used"][ch], fh, rep["used"][fh]))
        lines += ["  " + x for x in sc.summary_lines(res)]
    rep["interpreter"] = sys.version.split()[0]
    lines.append("SPLIT-E192 READ (REPORTED; decides nothing)")
    if out_json:
        with open(out_json, "w") as f:
            f.write(json.dumps(rep, indent=1) + "\n")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
