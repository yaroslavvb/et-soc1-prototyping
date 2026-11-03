#!/usr/bin/env python3
"""E136, post hoc (written after the session, labelled; no rule reads it): (1) the speed law re-footed on E126's c16s (C shared) for the fresh lines,
since the large GEMM stores each C tile once per KB x 32 ops, not once per 32 as every E119 arm does; (2) the session's rest reading; (3) card time and
the device commands sent, counted from the session's own records. Standard library only.

    python3 docs/reports/data/2026-11-02-e136-large-gemm/posthoc_e136.py > docs/reports/data/2026-11-02-e136-large-gemm/posthoc.txt
"""
import glob, gzip, json, os
HERE = os.path.dirname(os.path.abspath(__file__))
DATA = os.path.join(HERE, "..")
P = json.load(open(os.path.join(HERE, "..", "..", "..", "..", "tools/claims-v3/e136/predictions-e136.json")))
R = json.load(open(os.path.join(HERE, "results.json")))
F119 = json.load(open(os.path.join(DATA, "2026-11-01-e119-gemm-speed/results.json")))["per_arm"]
F126 = json.load(open(os.path.join(DATA, "2026-11-02-e126-gemm-arms/results.json")))["per_arm"]


def T(fits, arm, f):
    v = fits[arm]["fit"]
    return v["C"] / f + v["M"]


out = {}
print("(1) the speed law, T800 in us: as frozen (fresh lines at c16's cost) and re-footed on E126's c16s (C shared) for the fresh lines; measured")
for g in ("g4k", "g2k"):
    for t in ("fp32", "fp16", "int8"):
        nl, nf = P["lines"][g]["P1"]
        c1, c8 = T(F119, f"c1.{t}", 800), T(F119, f"c8s.{t}", 800)
        c16s = T(F126, f"c16s.{t}", 800)
        alt = c1 + nl / 128 * (c8 - c1) + nf / 128 * (c16s - c1)
        x6 = T(F119, f"c1.{t}", 600) + nl / 128 * (T(F119, f"c8s.{t}", 600) - T(F119, f"c1.{t}", 600)) + nf / 128 * (T(F126, f"c16s.{t}", 600) - T(F119, f"c1.{t}", 600))
        m = R["per_gemm"][f"{g}.{t}"]["T800"]
        fr = P["laws"][f"{g}.{t}"]["P1"]["T800_us"]
        out[f"{g}.{t}"] = {"frozen": fr, "c16s_footing": round(alt, 4), "measured": round(m, 4), "err_frozen": round(m / fr - 1, 4), "err_c16s": round(m / alt - 1, 4),
                           "X_c16s_footing": round(x6 / alt, 4), "X_measured": round(R["per_gemm"][f"{g}.{t}"]["X"], 4)}
        print(f"  {g}.{t}: frozen {fr:.4f} ({m / fr - 1:+.1%}); c16s footing {alt:.4f} ({m / alt - 1:+.1%}), X {x6 / alt:.3f}; measured {m:.4f}, X {R['per_gemm'][f'{g}.{t}']['X']:.3f}")
rest = None
for L in glob.glob(os.path.join(HERE, "aifoundry2/smoke/tel/*rest*.jsonl.gz")):
    ws = [json.loads(x)["board_w"] for x in gzip.open(L, "rt") if x.startswith("{")]
    dies = [json.loads(x)["temp_c"]["minshire"][0] for x in gzip.open(L, "rt") if x.startswith("{")]
    rest = {"board_w": round(sum(ws[-300:]) / len(ws[-300:]), 2), "die_c": round(sum(dies[-300:]) / len(dies[-300:]), 2), "n": len(ws[-300:])}
print("(2) the smoke's rest reading (last 30 s):", rest)
q = [json.loads(x) for x in open(os.path.join(HERE, "aifoundry2/queue.jsonl"))]
t0 = min(x["t_ms"] for x in q if x["kind"] == "session_start")
t1 = max(x["t_ms"] for x in q if x["kind"] == "session_end")
tel = 0
for p in glob.glob(os.path.join(HERE, "aifoundry2/*/tel/*.jsonl.gz")):
    tel += sum(1 for x in gzip.open(p, "rt") if x.startswith("{"))
runs = sum(1 for p in glob.glob(os.path.join(HERE, "aifoundry2/*/runs.jsonl")) for _ in open(p))
print(f"(3) card time, first session start to last session end: {(t1 - t0) / 60000:.2f} min; sampler lines {tel}; runs with an after-run config read {runs}")
out.update({"rest": rest, "card_min_sessions": round((t1 - t0) / 60000, 2), "sampler_lines": tel, "runs_incl_smoke": runs})
json.dump(out, open(os.path.join(HERE, "posthoc.json"), "w"), indent=1)
