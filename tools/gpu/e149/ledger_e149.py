"""E149's spend ledger: GPU-seconds per call from the Volume's STARTED and DONE records, priced at the registered
rates, beside the metered cost from `modal billing report --for today --json` (saved to a file), by app.

    python ledger_e149.py <logs dir holding one folder per run> [<billing report json>] > ledger.json
"""
import glob
import json
import os
import sys

RATE = {"gpu_h": 2.10, "cpu_core_h": 0.0473, "mem_gib_h": 0.008}
CPU, MEM_GIB = 2.0, 8.0
PER_H = RATE["gpu_h"] + CPU * RATE["cpu_core_h"] + MEM_GIB * RATE["mem_gib_h"]


def main():
    logs = sys.argv[1]
    calls = []
    for d in sorted(glob.glob(os.path.join(logs, "*", "*"))):
        st, dn = os.path.join(d, "STARTED"), os.path.join(d, "DONE")
        if not os.path.exists(st):
            continue
        s = json.load(open(st))
        e = json.load(open(dn)) if os.path.exists(dn) else {}
        secs = e.get("elapsed_s")
        calls.append({"run": os.path.basename(os.path.dirname(d)), "unit": os.path.basename(d),
                      "fn_seconds": secs, "est_usd_fn": secs / 3600.0 * PER_H if secs else None,
                      "skipped": e.get("skipped"), "error": bool(e.get("error"))})
    out = {"rate_per_unit_h": PER_H, "calls": calls,
           "fn_seconds_total": sum(c["fn_seconds"] or 0 for c in calls),
           "est_usd_fn_total": sum(c["est_usd_fn"] or 0 for c in calls),
           "note": "fn_seconds runs from the function's first line to DONE; Modal also bills the container's start "
                   "(image load, CUDA init) and a short tail, which only the metered report shows"}
    if len(sys.argv) > 2:
        rep = json.load(open(sys.argv[2]))
        rows = [r for r in rep if "e149" in json.dumps(r)]
        tot = 0.0
        for r in rows:
            for k in ("cost", "Cost", "total", "amount"):
                if k in r:
                    try:
                        tot += float(str(r[k]).replace("$", ""))
                    except ValueError:
                        pass
                    break
        out["metered"] = {"rows": rows, "total_usd": tot}
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
