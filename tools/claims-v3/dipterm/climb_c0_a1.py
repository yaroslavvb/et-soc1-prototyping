#!/usr/bin/env python3
"""Dated amendment A1, rule A1-5 (REGISTRATION.md.dated-note-4.md): card 0's climb (c7, c8) re-read from committed falls.

    python3 -I -B climb_c0_a1.py --lab <the lab tree> > climb-c0-a1.txt

For each idle-reset fall inside a process (Q132(g)'s kernel rule: a launch at 0.55-0.62 GHz straight after one at 0.79 GHz
or more, in a gap at least one heartbeat after the process's first launch) whose low episode recovers inside the process in
the 10 Hz telemetry:
  L6 = the first minion-clock reading above 600 MHz after the fall's first 600 MHz reading, less that first 600 reading;
  L7 = the first reading at 800 MHz or more at or after that reading above 600, less it.
Both are differences of two sampler readings, so the sampler's own delay cancels in each. The term's 600 MHz segment after a
fall is P + c7 and its 700 MHz segment c8 - c7 (REGISTRATION.md section 1), so
  c7 = median(L6) - P0 / 1000,   c8 = c7 + median(L7),
over card 0's committed sessions E114 (s1, 1 Nov) and E174 (s1, 5 Nov), pooled. The same reading of aifoundry2's sessions
E100, E173 and E175 is printed beside it as a check of the registered aifoundry2 values, which A1 does not change.

POST HOC: E174's falls enter the pooled values, so E174's re-score at them is in sample. Python 3 standard library only.
SPDX-License-Identifier: Apache-2.0
"""
import argparse
import gzip
import json
import os
import statistics as st
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import dipterm as DT  # noqa: E402  (the registered term, unchanged)

D = "docs/reports/data"
CARD0 = {"E114": "2026-11-01-e114-card0-replicates/s1", "E174": "2026-11-05-e174-blind8-card0/aifoundry1-c0/s1"}
A2 = {"E100": "2026-11-01-e100-idle-reset/s1", "E173": "2026-11-05-e173-blind8-aifoundry2/aifoundry2/s1",
      "E175": "2026-11-05-e175-governed-aifoundry2/aifoundry2/s1"}
FULL_GHZ, FALL_LO, FALL_HI = 0.79, 0.55, 0.62


def tel(path):
    """[(t_ms, minion MHz)] from a 10 Hz sampler file; a line that is not JSON (the sampler's own messages) is skipped."""
    for p in (path, path + ".gz"):
        if os.path.exists(p):
            break
    else:
        return []
    op = gzip.open if p.endswith(".gz") else open
    out = []
    with op(p, "rt") as f:
        for ln in f:
            ln = ln.strip()
            if not ln.startswith("{"):
                continue
            try:
                d = json.loads(ln)
            except ValueError:
                continue
            if "t_ms" in d:
                out.append((int(d["t_ms"]), (d.get("mhz") or {}).get("minion")))
    out.sort()
    return out


def lengths(lab, rel, card):
    sd = os.path.join(lab, D, rel)
    procs = DT.load_session(sd)
    P0 = DT.PERIOD_PRIOR_MS[card][0]
    rows = []
    for p in procs:
        L = p["launches"]
        t_s = L[0][1] + 0.5
        for i in range(1, len(L)):
            lo = L[i - 1][2] + 0.5
            if not (L[i - 1][3] >= FULL_GHZ and FALL_LO <= L[i][3] <= FALL_HI and lo >= t_s + P0 and L[i][1] >= L[i - 1][2]):
                continue
            s = tel(os.path.join(sd, "tel", p["run"] + ".jsonl"))
            a = next((t for t, f in s if t >= lo - 50 and f == 600), None)
            b7 = next((t for t, f in s if a is not None and t > a and f is not None and f > 600), None)
            b8 = next((t for t, f in s if b7 is not None and t >= b7 and f is not None and f >= 800), None)
            in_proc = b7 is not None and b7 <= L[-1][2]
            rows.append({"run": p["run"], "gap": i, "prev_ghz": L[i - 1][3], "ghz": L[i][3],
                         "L6_s": round((b7 - a) / 1000.0, 3) if (a is not None and b7 is not None) else None,
                         "L7_s": round((b8 - b7) / 1000.0, 3) if (b7 is not None and b8 is not None) else None,
                         "recovered_inside_process": in_proc})
    return rows


def summary(name, rows, card):
    P0 = DT.PERIOD_PRIOR_MS[card][0]
    l6 = [r["L6_s"] for r in rows if r["recovered_inside_process"] and r["L6_s"] is not None]
    l7 = [r["L7_s"] for r in rows if r["recovered_inside_process"] and r["L7_s"] is not None]
    out = {"falls": len(rows), "recovered": len(l6), "L6_s": l6, "L7_s": l7,
           "L6_median_s": round(st.median(l6), 3) if l6 else None, "L7_median_s": round(st.median(l7), 3) if l7 else None}
    if l6 and l7:
        c7 = st.median(l6) - P0 / 1000.0
        out["c7_s"] = round(c7, 3)
        out["c8_s"] = round(c7 + st.median(l7), 3)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--lab", required=True)
    a = ap.parse_args()
    lab = os.path.abspath(a.lab)
    res = {"rule": "A1-5: c7 = median(L6) - P0/1000, c8 = c7 + median(L7), over the falls that recover inside their process",
           "card0": {}, "aifoundry2_check": {}, "registered_CLIMB_S": DT.CLIMB_S}
    pooled = []
    for name, rel in CARD0.items():
        rows = lengths(lab, rel, "c0")
        pooled += rows
        res["card0"][name] = {"rows": rows, "summary": summary(name, rows, "c0")}
    res["card0"]["pooled_E114_E174"] = summary("pooled", pooled, "c0")
    a2 = []
    for name, rel in A2.items():
        rows = lengths(lab, rel, "a2")
        a2 += rows
        res["aifoundry2_check"][name] = {"rows": rows, "summary": summary(name, rows, "a2")}
    res["aifoundry2_check"]["pooled"] = summary("pooled", a2, "a2")
    print(json.dumps(res, indent=1, sort_keys=True))


if __name__ == "__main__":
    main()
