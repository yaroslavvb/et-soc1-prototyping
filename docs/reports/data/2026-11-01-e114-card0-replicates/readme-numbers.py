#!/usr/bin/env python3
"""E114 (Q133): every number the data README quotes, printed from the committed files (results.json from the registered
reduction, the session's runs.jsonl, marks.jsonl, end.json, the ident reads, predictions-e114.json). Desk only, written
after the data; it decides nothing.

    python3 readme-numbers.py > readme-numbers.txt      # in docs/reports/data/2026-11-01-e114-card0-replicates/
"""
import glob
import hashlib
import json
import math
import os
import statistics as st
import time

D = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(D, "..", "..", "..", ".."))
res = json.load(open(os.path.join(D, "results.json")))
P = json.load(open(os.path.join(ROOT, "tools/claims-v3/e114/predictions-e114.json")))


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()[:12]


def hms(ms):
    return time.strftime("%H:%M:%S", time.localtime(ms / 1000.0))


print("E114 readme numbers (desk, after the data; decides nothing). Times are the Intel's local clock (PST).")
print(f"results.json sha256 {sha(os.path.join(D, 'results.json'))}, reduce.txt sha256 {sha(os.path.join(D, 'reduce.txt'))}, "
      f"predictions-e114.json sha256 {sha(os.path.join(ROOT, 'tools/claims-v3/e114/predictions-e114.json'))}")

print("\n== A. The session")
sess = json.load(open(os.path.join(D, "s1", "session.json")))
end = json.load(open(os.path.join(D, "s1", "end.json")))
runs = [json.loads(l) for l in open(os.path.join(D, "s1", "runs.jsonl"))]
marks = [json.loads(l) for l in open(os.path.join(D, "s1", "marks.jsonl"))]
print(f"session start {hms(sess['t_start_ms'])}, end {hms(end['t_end_ms'])}, exit {end['exit']} ({end['reason']}), "
      f"card_min {end['card_min']}, runs {len(runs)} of {len(sess['runs_planned'])}")
kinds = {}
for m in marks:
    kinds[m["kind"]] = kinds.get(m["kind"], 0) + 1
print("marks by kind:", json.dumps(kinds))
stops = [m["detail"] for m in marks if m["kind"] == "sampler_stop"]
print(f"sampler stops: {len(stops)}, ending 'rc 0': {sum(1 for x in stops if x.endswith('rc 0'))}")
E84D = os.path.join(D, "..", "2026-10-31-e84-speed-aifoundry1-card0")
for name, rd in (("E114 smoke", os.path.join(D, "smoke")), ("E84 smoke", os.path.join(E84D, "smoke")),
                 ("E114 first run", os.path.join(D, "s1")), ("E84 first run", os.path.join(E84D, "s1"))):
    rr = [json.loads(l) for l in open(os.path.join(rd, "runs.jsonl"))]
    rr = rr if "smoke" in name else rr[:1]
    print(f"{name}: die at the gate {[r['gate']['reading'][0] for r in rr]} C, board {[r['gate']['reading'][2] for r in rr]} W")
holds = [r["gate"]["held_s"] for r in runs]
gates = [r["gate"]["reading"][0] for r in runs]
print(f"cooling gates: held {min(holds)}-{max(holds)} s, die at the gate {min(gates)}-{max(gates)} C, all reached: "
      f"{all(r['gate']['reached'] for r in runs)}")
starts = [r["t_first_ms"] for r in runs]
gaps = [round((b - a) / 1000.0, 1) for a, b in zip(starts, starts[1:])]
print(f"run start to next run start: {min(gaps)}-{max(gaps)} s (median {st.median(gaps)})")
nl = sum(len(r["launches"]) for r in runs)
print(f"launch processes: {nl}, rc 0: {sum(1 for r in runs for L in r['launches'] if L['rc'] == 0)}")
cfgs = sorted({json.dumps({k: (r.get('queries') or {}).get('config', {}).get(k) for k in ('tdp_w', 'temp_threshold_c')})
               for r in runs})
print("ettelem config after every run:", cfgs)
q = [json.loads(l) for l in open(os.path.join(D, "s1", "queries.jsonl"))]
for x in q:
    c = x.get("config") or {}
    print(f"  session {x.get('tag')} read: tdp {c.get('tdp_w')} W, threshold {c.get('temp_threshold_c')} C, "
          f"{c.get('minion_mhz')} MHz, {c.get('minion_mv')} mV")
for f in sorted(glob.glob(os.path.join(D, "ident", "*.out"))):
    txt = open(f).read()
    cfgl = [l for l in txt.splitlines() if l.startswith('{"tdp_w"')]
    first = txt.splitlines()[0] if txt else ""
    print(f"  {os.path.basename(f)}: first line {first!r}; config lines {cfgl}")

print("\n== B. The cells (results.json cells)")
for k, c in res["cells"].items():
    print(f"{k}: n {c['n']}, runs {c['runs']}")
    for qn in ("rate", "mhz", "mhz_nonramp", "w", "die"):
        s = c[qn]
        extra = f", E84 {s.get('e84')}, E84 - mean {s.get('e84_minus_mean')}, inside pi95 {s.get('e84_inside_pi95')}" \
            if "e84" in s else ""
        print(f"   {qn:12s} mean {s.get('mean')} sd {s.get('sd')} ci95 {s.get('ci95')} pi95 {s.get('pi95')} "
              f"runs {s.get('runs')}{extra}")
    print(f"   limits {c['limits']} (E84 {c['e84']['limit']}); ramp share {c['ramp_share']} (E84 {c['e84']['ramp_share']}); "
          f"die max {c['die_max']} (E84 {c['e84']['die_max']}); die at the gate {c['gate_reading_c']}; "
          f"idle W {c['idle_w']}; PMIC average {c['sus_avg_w']}")
    for cc in c["sus_counts"]:
        print(f"   counts {cc}")
    r = c["rate"]
    if r.get("mean") and r.get("ci95") is not None:
        print(f"   rate ci95 as a share of the mean: {100 * r['ci95'] / r['mean']:.2f}%; E84 off the mean by "
              f"{100 * (r['e84'] - r['mean']) / r['mean']:+.2f}%")

print("\n== C. The ratios (results.json rho) and the rules")
T2 = 4.303  # t(0.975, 2), three pairs
for f, s in res["rho"].items():
    print(f"rho {f}: {s.get('mean')} +- {s.get('ci95')} [{s.get('lo')}, {s.get('hi')}], pairs "
          f"{[(x['pass'], x['ratio'], x['mhz_zeros_minus_heavy']) for x in s['pairs']]}, ratio of means "
          f"{s.get('ratio_of_means')}, E84 {s['e84']}")
    rs = [x["ratio"] for x in s["pairs"]]
    if len(rs) == 3:
        m, sd = st.mean(rs), st.stdev(rs)
        h = T2 * sd * math.sqrt(1 + 1 / 3)
        print(f"   95% prediction interval for one pass pair: {m - h:.4f} to {m + h:.4f}; E84's single pair {s['e84']} "
              f"{'inside' if abs(s['e84'] - m) <= h else 'OUTSIDE'}")
for name, r in res["rules"].items():
    if name == "E114-S1":
        for f, x in r.items():
            print(f"{name} {f}: {json.dumps(x)}")
    else:
        print(f"{name}: {r.get('verdict')} | {json.dumps({k: v for k, v in r.items() if k not in ('rows',)})[:700]}")
        if name == "E114-R1":
            for row in r["rows"]:
                print(f"   {row}")

print("\n== D. aifoundry2 beside (predictions-e114.json aifoundry2_pool, from E80/E83/E87/E96 results.json)")
for f, A in P["aifoundry2_pool"].items():
    print(f"{f}: zeros {A['zeros_mean']} sd {A['zeros_sd']} n {A['n_zeros']}; heavy {A['heavy_mean']} sd {A['heavy_sd']} "
          f"n {A['n_heavy']}; ratio of means {A['ratio_of_means']}")
print("card 0 minus aifoundry2 in rate, the four ratio kinds:")
for f, A in P["aifoundry2_pool"].items():
    z, h = res["cells"][f"{f}/zeros"]["rate"]["mean"], res["cells"][("fp16/randn" if f == "fp16" else "int8/full")]["rate"]["mean"]
    print(f"  {f} zeros {z} vs {A['zeros_mean']} ({100 * (z / A['zeros_mean'] - 1):+.2f}%); heavy {h} vs "
          f"{A['heavy_mean']} ({100 * (h / A['heavy_mean'] - 1):+.2f}%)")

print("\n== E. Heat path (context): each run's die minus E84's die line at its board W")
dl = res["context"]["die_vs_e84_line"]
print(json.dumps({k: v for k, v in dl.items()}))
