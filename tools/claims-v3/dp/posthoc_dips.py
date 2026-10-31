#!/usr/bin/env python3
"""E81 POST HOC, labelled (not registered, written after the registered reduction; it moves no registered verdict).

    python3 tools/claims-v3/dp/posthoc_dips.py <pass dir> [...] --work <scratch dir> --out dips.json

aifoundry3's board reading now and then lands on the 1-2 ms gap between two of a run's 0.4 s launches and the
service processor holds the low value for a pass (two 100 ms samples near idle in the middle of a run): the same
instrument artifact E82's amendment A2 described on aifoundry1 card 1 the same day. E81's registered estimator (the
mean over [t0+1 s, t0+3 s)) has no gate for it. This writes a copy of each pass with every dip sample removed from
the telemetry by E82's own definition,

    board_w[i] < min(board_w[i-2], board_w[i+2]) - 4.0 W,

and lists every dip with where it falls (inside a run's power window or not, and which item). Run the registered
reducer on the copies, every gate unchanged, for the labelled view: reduce_dp.py <work>/p81* ... --out
dp-posthoc-dips.json.
"""
import argparse
import gzip
import json
import os
import shutil


def load(path):
    out = []
    for line in gzip.open(path, "rt") if path.endswith(".gz") else open(path):
        if line.startswith("{"):
            try:
                out.append(json.loads(line))
            except ValueError:
                pass
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("dirs", nargs="+")
    ap.add_argument("--work", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--drop-w", type=float, default=4.0)
    a = ap.parse_args()
    report = {"rule": "board_w[i] < min(board_w[i-2], board_w[i+2]) - %.1f W (E82 amendment A2's definition)"
                      % a.drop_w, "passes": {}}
    for d in a.dirs:
        name = os.path.basename(os.path.normpath(d))
        o = os.path.join(a.work, name)
        os.makedirs(o, exist_ok=True)
        for f in os.listdir(d):
            if f != "telemetry.jsonl.gz" and os.path.isfile(os.path.join(d, f)):
                shutil.copy(os.path.join(d, f), o)
        tel = load(os.path.join(d, "telemetry.jsonl.gz"))
        P = [s["board_w"] for s in tel]
        dips = [i for i in range(2, len(P) - 2) if P[i] < min(P[i - 2], P[i + 2]) - a.drop_w]
        drop = set(dips)
        with open(os.path.join(o, "telemetry.jsonl"), "w") as fh:
            for i, s in enumerate(tel):
                if i not in drop:
                    fh.write(json.dumps(s) + "\n")
        runs = {}
        for line in open(os.path.join(d, "runs.jsonl")):
            r = json.loads(line)
            key = (r["item"], r.get("pos", 0))
            lo, hi = runs.get(key, (r["t_start_ms"], r["t_end_ms"]))
            runs[key] = (min(lo, r["t_start_ms"]), max(hi, r["t_end_ms"]))
        rows = []
        for i in dips:
            t = tel[i]["t_ms"]
            where = None
            for (item, pos), (t0, t1) in runs.items():
                if t0 <= t <= t1:
                    where = {"item": item, "pos": pos, "s_after_t0": round((t - t0) / 1000.0, 3),
                             "in_power_window": bool(t0 + 1000 <= t < t0 + 3000)}
            rows.append({"t_ms": t, "board_w": P[i], "neighbours_w": [P[i - 2], P[i + 2]], "run": where})
        report["passes"][name] = {"samples": len(P), "dips": len(dips),
                                  "dips_in_a_power_window": sum(1 for r in rows if r["run"] and
                                                                r["run"]["in_power_window"]),
                                  "list": rows}
        print("%s: %d samples, %d dips, %d inside a run's [1 s, 3 s) window: %s" % (
            name, len(P), len(dips), report["passes"][name]["dips_in_a_power_window"],
            ", ".join("%s@%.2fs" % (r["run"]["item"], r["run"]["s_after_t0"]) for r in rows
                      if r["run"] and r["run"]["in_power_window"])))
    json.dump(report, open(a.out, "w"), indent=1)


if __name__ == "__main__":
    main()
