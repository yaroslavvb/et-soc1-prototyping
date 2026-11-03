"""E162's spend ledger: function-seconds per call from the Volume's STARTED and DONE records, priced at the registered
rates by each unit's GPU type (from its plan), beside the metered cost from `modal billing report --json` files (the
app's rows only).

    python ledger_e162.py <logs dir holding one folder per run> [<billing report json> ...] > ledger.json
"""
import glob
import json
import os
import sys

RATE = {"A100": 2.10, "L40S": 1.95, "cpu_core_h": 0.0473, "mem_gib_h": 0.008}   # read Tue 3 Nov 2026 04:05:39 PST
CPU, MEM_GIB = 2.0, 8.0


def per_h(gpu):
    return RATE[gpu] + CPU * RATE["cpu_core_h"] + MEM_GIB * RATE["mem_gib_h"]


def main():
    logs = sys.argv[1]
    calls = []
    for d in sorted(glob.glob(os.path.join(logs, "*", "*"))):
        st, dn, pl = (os.path.join(d, x) for x in ("STARTED", "DONE", "plan.json"))
        if not os.path.exists(st):
            continue
        s = json.load(open(st))
        e = json.load(open(dn)) if os.path.exists(dn) else {}
        gpu = json.load(open(pl)).get("gpu") if os.path.exists(pl) else None
        secs = e.get("elapsed_s")
        calls.append({"run": os.path.basename(os.path.dirname(d)), "unit": os.path.basename(d), "gpu": gpu,
                      "t_started": s.get("t"), "fn_seconds": secs,
                      "est_usd_fn": secs / 3600.0 * per_h(gpu) if (secs and gpu) else None,
                      "refused": e.get("refused"), "skipped": e.get("skipped"), "error": bool(e.get("error"))})
    out = {"rate_per_unit_h": {g: per_h(g) for g in ("A100", "L40S")}, "calls": calls,
           "fn_seconds_total": sum(c["fn_seconds"] or 0 for c in calls),
           "est_usd_fn_total": sum(c["est_usd_fn"] or 0 for c in calls),
           "note": "fn_seconds runs from the function's first line to DONE; Modal also bills the container's start "
                   "(image load, CUDA init) and a short tail, which only the metered report shows"}
    seen = {}
    for p in sys.argv[2:]:
        for r in json.load(open(p)):
            if str(r.get("description", "")).startswith("e162"):
                seen[(r["object_id"], r["interval_start"])] = r
    if len(sys.argv) > 2:
        out["metered"] = {"rows": list(seen.values()), "total_usd": sum(float(r["cost"]) for r in seen.values())}
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
