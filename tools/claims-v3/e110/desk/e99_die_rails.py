"""E110 desk view, POST HOC on E99's committed passes, labelled: every die_mv field and the DDR, VDDQ and VDDQLP regulator readings per item,
within-pass differences over a reference item, mean and 95 % t over the passes given, the board meter's dips removed, window [t0+2 s, t0+4 s)
as E99's posthoc_rails. Written to see what the DDR die rail does on E99's images; it freezes E110's R5 classes, nothing else.

    cd docs/reports/data/2026-11-01-e99-dram-mechanism/passes
    python3 ../../../../../tools/claims-v3/e110/desk/e99_die_rails.py dp_zeros p9911 p9912 p9913 p9914 p9915 > .../desk/e99_die_rails.txt"""
import gzip, json, os, sys, collections, math
import numpy as np
ref = sys.argv[1]
dirs = sys.argv[2:]
T = {1: 12.706, 2: 4.303, 3: 3.182, 4: 2.776, 5: 2.571, 6: 2.447}
per = collections.defaultdict(dict)
fields = None
for d in dirs:
    tel = [json.loads(l) for l in gzip.open(os.path.join(d, "telemetry.jsonl.gz"), "rt") if l.startswith("{")]
    P = [s["board_w"] for s in tel]
    drop = {i for i in range(2, len(P) - 2) if P[i] < min(P[i - 2], P[i + 2]) - 4.0}
    tel = [s for i, s in enumerate(tel) if i not in drop]
    t = np.array([s["t_ms"] for s in tel], float)
    F = {}
    for k in ("die_mv", "reg_mv"):
        for f in tel[0][k]:
            F[k + "." + f] = np.array([s[k][f] for s in tel], float)
    F["board"] = np.array([s["board_w"] for s in tel], float)
    for r in ("noc_w", "sram_w", "minion_w"):
        F[r] = np.array([s["sp"][r][0] for s in tel], float)
    fields = list(F)
    first, last = {}, {}
    for l in open(os.path.join(d, "runs.jsonl")):
        r = json.loads(l)
        k = (r["block"], r["item"], r.get("pos", 0), r.get("attempt", 1))
        first[k] = min(first.get(k, 1e30), r["t_start_ms"]); last[k] = max(last.get(k, 0), r["t_end_ms"])
    acc = collections.defaultdict(lambda: collections.defaultdict(list))
    for k in first:
        lo = first[k] + 2000
        w = (t >= lo) & (t < min(lo + 2000, last[k]))
        if w.sum() < 3: continue
        for f, A in F.items():
            acc[k[1]][f].append(float(A[w].mean()))
    for it in acc:
        per[d][it] = {f: float(np.mean(v)) for f, v in acc[it].items()}
items = sorted(set.intersection(*[set(per[d]) for d in dirs]))
show = [f for f in fields if f.startswith("die_mv") or f in ("reg_mv.ddr", "reg_mv.vddq", "reg_mv.vddqlp", "board", "noc_w", "sram_w")]
print("over %s; %d passes; fields %s" % (ref, len(dirs), show))
for it in items:
    row = []
    for f in show:
        v = [per[d][it][f] - per[d][ref][f] for d in dirs]
        m = float(np.mean(v)); n = len(v)
        h = T.get(n - 1, 2.0) * float(np.std(v, ddof=1)) / math.sqrt(n) if n > 1 else float("nan")
        row.append("%s=%+.2f±%.2f" % (f.replace("die_mv.", "d.").replace("reg_mv.", "r."), m, h))
    print("%-12s " % it + " ".join(row))
