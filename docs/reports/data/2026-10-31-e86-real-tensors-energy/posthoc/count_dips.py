import gzip, json, sys, os, glob
for d in sys.argv[1:]:
    p = os.path.join(d, "telemetry.jsonl.gz")
    tel = [json.loads(l) for l in gzip.open(p, "rt") if l.startswith("{")]
    B = [s["board_w"] for s in tel]
    t = [s["t_ms"] for s in tel]
    dips = [i for i in range(2, len(B) - 2) if B[i] < min(B[i - 2], B[i + 2]) - 4.0]
    recs = [json.loads(l) for l in open(os.path.join(d, "runs.jsonl"))]
    marks = [json.loads(l) for l in open(os.path.join(d, "marks.jsonl"))]
    t0s = {}
    for r in recs:
        k = (r["item"], r.get("pos"))
        t0s[k] = min(t0s.get(k, 1e18), r["t_start_ms"])
    inwin = sum(1 for i in dips if any(a + 1000 <= t[i] < a + 3000 for a in t0s.values()))
    dur = (t[-1] - t[0]) / 60000
    print(f"{os.path.basename(d)}: samples {len(B)}, {dur:.1f} min, dips {len(dips)}, in power windows {inwin}, runs {len(t0s)}")
