#!/usr/bin/env python3
"""t7-0xf (Q221) s04: the check re-run on the scrubbed land summaries against the checks made on the original summaries: for each of the
10 runs, every key of check_v31.py's output compared (per hart: equal, walk and trace sha256, ok; shire streams; chip sharing; host
records; strays; log lines). Prints the keys that differ (expected: none) and a JSON summary to stdout.
    /usr/bin/python3 -I -B s04_compare_checks.py <recheck dir> <pairs.json: [[name, original check json], ...]>
Desk; standard library."""
import json
import sys


def diff(a, b, path, out):
    if type(a) is not type(b):
        out.append(path)
        return
    if isinstance(a, dict):
        for k in sorted(set(a) | set(b)):
            if k not in a or k not in b:
                out.append(path + "/" + str(k))
            else:
                diff(a[k], b[k], path + "/" + str(k), out)
    elif isinstance(a, list):
        if len(a) != len(b):
            out.append(path + "[len]")
        else:
            for i, (x, y) in enumerate(zip(a, b)):
                diff(x, y, "%s[%d]" % (path, i), out)
    elif a != b:
        out.append(path)


def main():
    rd = sys.argv[1]
    pairs = json.load(open(sys.argv[2]))
    res = {}
    for name, orig in pairs:
        a = json.load(open(orig))
        b = json.load(open("%s/check-%s.json" % (rd, name)))
        d = []
        diff(a, b, "", d)
        ph = b["per_hart"]
        res[name] = {"keys_differing": d[:20], "n_keys_differing": len(d), "verdict_orig": a["verdict"], "verdict_land": b["verdict"],
                     "harts_in_check": len(ph), "harts_ok": sum(1 for r in ph.values() if r["ok"]),
                     "working_exact": b["exact_harts"], "working_traced": b["working_harts_traced"]}
        print("%-28s orig %-6s land %-6s keys differing %d; harts %d ok %d; working exact %d of %d" % (
            name, a["verdict"], b["verdict"], len(d), len(ph), res[name]["harts_ok"], b["exact_harts"], b["working_harts_traced"]))
    json.dump(res, open(rd + "/compare-checks.json", "w"), indent=1)
    return 0 if all(v["n_keys_differing"] == 0 and v["verdict_land"] == "EXACT" for v in res.values()) else 1


if __name__ == "__main__":
    sys.exit(main())
