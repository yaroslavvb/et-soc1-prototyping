"""E150's spend ledger: GPU-seconds per call from the Volume's STARTED and DONE records, priced at the registered
rates for the call's GPU type, beside the metered cost from `modal billing report --for today --json` (saved to a
file), app e150-second-gpu only.

    python ledger_e150.py <logs dir holding one folder per run> [<billing report json>] > ledger.json
"""
import glob
import json
import os
import sys

RATE = {"gpu_h": {"L4": 0.80, "A10G": 1.10}, "cpu_core_h": 0.0473, "mem_gib_h": 0.008}
CPU, MEM_GIB = 2.0, 8.0


def per_h(gpu):
    return RATE["gpu_h"][gpu] + CPU * RATE["cpu_core_h"] + MEM_GIB * RATE["mem_gib_h"]


def gpu_of(unit_dir):
    for p in sorted(glob.glob(os.path.join(unit_dir, "steps", "*static*.json.gz"))):
        import gzip
        with gzip.open(p, "rt") as f:
            name = json.load(f).get("static", {}).get("name", "")
        if "L4" in name:
            return "L4"
        if "A10G" in name:
            return "A10G"
    base = os.path.basename(unit_dir)
    return "L4" if base.endswith("L4") else ("A10G" if base.endswith("A10G") else None)


def main():
    logs = sys.argv[1]
    calls = []
    for d in sorted(glob.glob(os.path.join(logs, "*", "*"))):
        st, dn = os.path.join(d, "STARTED"), os.path.join(d, "DONE")
        if not os.path.exists(st):
            continue
        e = json.load(open(dn)) if os.path.exists(dn) else {}
        secs = e.get("elapsed_s")
        g = gpu_of(d)
        calls.append({"run": os.path.basename(os.path.dirname(d)), "unit": os.path.basename(d), "gpu": g,
                      "fn_seconds": secs, "est_usd_fn": secs / 3600.0 * per_h(g) if (secs and g) else None,
                      "skipped": e.get("skipped"), "error": bool(e.get("error"))})
    out = {"rate_per_unit_h": {g: per_h(g) for g in RATE["gpu_h"]}, "calls": calls,
           "fn_seconds_total": sum(c["fn_seconds"] or 0 for c in calls),
           "est_usd_fn_total": sum(c["est_usd_fn"] or 0 for c in calls),
           "note": "fn_seconds runs from the function's first line to DONE; Modal also bills the container's start "
                   "(image load, CUDA init) and a short tail, which only the metered report shows"}
    if len(sys.argv) > 2:
        rep = json.load(open(sys.argv[2]))
        rows = [r for r in rep if "e150" in json.dumps(r)]
        out["metered"] = {"rows": rows, "total_usd": sum(float(r.get("cost") or 0) for r in rows)}
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
