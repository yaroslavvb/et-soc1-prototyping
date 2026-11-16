#!/usr/bin/env python3
"""E196 (Q185, lane reg-e196): the proposal's arm tables against its arm file, cell by cell (a desk check of code).

    /usr/bin/python3 -I -B compare_arms_e196.py REQUEST.md ARMS.json [LIST.txt] [REDUCER.py RUN_BLOCK.py]

REQUEST.md section 2 holds three tables: the arm table (arm, tile, row mask, reference, role), the designed-counts table (rows,
micro-ops issued, multiply-adds issued, operand flips A / B, gated lane-micro-ops (fraction), live-lane flips A / B, accumulator
flips input / result, skipped runs an op, C rows zero / non-zero, and an emulator column) and the train table. ARMS.json is
make_x14.py's (src/arms.json, re-derived identically by --check). Every cell is compared but the emulator column, which is the
model session's emulator run (quoted, not re-derived here: no simulator on this desk). LIST.txt (optional) is make_x14.py
--list's output, compared line by line with ARMS.json. With the reducer and the runner, their arm names are checked to exist:
the ladders, the spread and mask-0 contrasts, the fields, the shares, the ties, the smoke arms, the anchor and the cut order.
Prints each mismatch and a verdict line: ARMS CHECK PASS or ARMS CHECK FAIL.
"""
import ast
import json
import re
import sys


def table_after(lines, header_start):
    """the rows (cells) of the markdown table whose header line starts with header_start"""
    for i, ln in enumerate(lines):
        if ln.startswith(header_start):
            rows = []
            for ln2 in lines[i + 2:]:
                if not ln2.startswith("|"):
                    break
                rows.append([c.strip() for c in ln2.strip().strip("|").split("|")])
            return rows
    raise SystemExit("no table starting with %r" % header_start)


def pair(s):
    a, b = [x.strip() for x in s.split("/")]
    return a, b


def main():
    req, arms_p = sys.argv[1], sys.argv[2]
    lines = open(req).read().splitlines()
    m = json.load(open(arms_p))
    A = {x["name"]: x for x in m["arms"]}
    bad, n = [], 0

    def eq(what, got, want):
        nonlocal n
        n += 1
        if got != want:
            bad.append("%s: request %r, arms.json %r" % (what, got, want))

    t1 = table_after(lines, "| arm | tile | row mask | reference | role |")
    t2 = table_after(lines, "| arm | rows | micro-ops issued |")
    t3 = table_after(lines, "| train | F kind (--values) |")
    print("request tables: arms %d rows, counts %d rows, trains %d rows; arms.json: %d arms, %d trains" % (
        len(t1), len(t2), len(t3), len(A), len(m["trains"])))
    eq("arm names (arm table, in order)", [r[0] for r in t1], [x["name"] for x in m["arms"]])
    eq("arm names (counts table, in order)", [r[0] for r in t2], [x["name"] for x in m["arms"]])
    for name, tile, mask, ref, role in t1:
        a = A.get(name)
        if a is None:
            bad.append("arm %s not in arms.json" % name)
            continue
        want_tile = {"built-in pi": "builtin:pi"}.get(tile, tile)
        eq("%s tile" % name, want_tile, a["tile"])
        eq("%s row mask" % name, None if mask == "none" else mask, a["row_mask"])
        eq("%s reference" % name, None if ref == "-" else ref, a["ref"])
        eq("%s role" % name, role, a["role"])
        eq("%s in the passes" % name, not name.startswith("T."), a["in_passes"])
    cells = 0
    for r in t2:
        name, rows, uops, macs, flips, gated, live, acc, skipped, crows, emu = r
        c = A[name]["counts"]
        want_rows = 16 if A[name]["row_mask"] is None else bin(int(A[name]["row_mask"], 16)).count("1")
        eq("%s rows" % name, int(rows), want_rows)
        eq("%s micro-ops issued" % name, int(uops), c["issued_uops"])
        eq("%s multiply-adds issued" % name, int(macs), c["issued_macs"])
        fa, fb = pair(flips)
        eq("%s operand flips A" % name, int(fa), c["issued_a_all"])
        eq("%s operand flips B" % name, int(fb), c["issued_b_all"])
        g = re.match(r"(\d+) \(([0-9.]+)\)", gated)
        eq("%s gated lane-micro-ops" % name, int(g.group(1)), c["gated_lane_uops"])
        eq("%s gated fraction" % name, float(g.group(2)), round(c["gated_fraction"], 3))
        la, lb = pair(live)
        eq("%s live-lane flips A" % name, int(la), c["live_a_all"])
        eq("%s live-lane flips B" % name, int(lb), c["live_b_all"])
        ai, ar = pair(acc)
        eq("%s accumulator flips input (mid)" % name, int(ai), c["acc_mid_c_in_flips_est"])
        eq("%s accumulator flips result (mid)" % name, int(ar), c["acc_mid_result_flips_est"])
        eq("%s skipped runs an op" % name, int(skipped), c["skipped_runs_per_op"])
        z, l = pair(crows)
        eq("%s C rows zero" % name, None if z == "-" else z, A[name]["zero_rows"])
        eq("%s C rows non-zero" % name, None if l == "-" else l, A[name]["live_rows"])
        cells += 14
    print("counts table: %d cells compared (the emulator column quoted, not re-derived)" % cells)
    T = {t["name"]: t for t in m["trains"]}
    for name, F, S, procs, launches, what in t3:
        t = T.get(name)
        if t is None:
            bad.append("train %s not in arms.json" % name)
            continue
        fF, mF = re.match(r"(\S+) \((0x[0-9A-F]{4})\)", F).groups()
        fS, mS = re.match(r"(\S+) \((0x[0-9A-F]{4})\)", S).groups()
        eq("%s F kind" % name, fF, t["F"])
        eq("%s S kind" % name, fS, t["S"])
        eq("%s F row mask" % name, mF, A[t["F"]]["row_mask"])
        eq("%s S row mask" % name, mS, A[t["S"]]["row_mask"])
        eq("%s processes" % name, int(procs), t["processes"])
        eq("%s launches" % name, int(launches), t["launches"])
        eq("%s same tile both kinds" % name, A[t["F"]]["tile"], A[t["S"]]["tile"])
        eq("%s equal micro-ops both kinds" % name, A[t["F"]]["counts"]["issued_uops"], A[t["S"]]["counts"]["issued_uops"])
        eq("%s skipped runs F against S (the request's 'what differs')" % name,
           re.search(r"(\d+) against (\d+) skipped runs", what).groups() if "skipped runs" in what else None,
           (str(A[t["F"]]["counts"]["skipped_runs_per_op"]), str(A[t["S"]]["counts"]["skipped_runs_per_op"]))
           if "skipped runs" in what else None)
    for x in m["arms"]:
        if x["ref"] is not None:
            eq("%s's reference exists and runs in the passes" % x["name"], A.get(x["ref"], {}).get("in_passes"), True)
    if len(sys.argv) > 3 and sys.argv[3].endswith(".txt"):
        lst = [ln.split()[0] for ln in open(sys.argv[3]) if ln.strip()]
        eq("make_x14.py --list names", lst, [x["name"] for x in m["arms"]] + [t["name"] for t in m["trains"]])
    if len(sys.argv) > 5:
        red = open(sys.argv[4]).read()
        rb = open(sys.argv[5]).read()
        names = set(re.findall(r'"((?:I|F|Z|K|T)\.[A-Za-z0-9.]+)"', red)) | set(re.findall(r'"((?:I|F|Z|K|T)\.[A-Za-z0-9.]+)"', rb))
        missing = sorted(x for x in names if x not in A and not x.endswith("."))
        eq("arm names the reducer and the runner use, all in arms.json", missing, [])
        sm = ast.literal_eval(re.search(r"SMOKE_ARMS = (\[.*?\])", rb).group(1))
        eq("the smoke arms (run_block.py)", sm, ["I.H.m00FF", "I.R.m00FF", "Z.a0", "I.R.full"])
        eq("the anchor (run_block.py)", re.search(r'ANCHOR = "([^"]+)"', rb).group(1), "K.pi")
        print("names the reducer and the runner use: %d, all present: %s" % (len(names), not missing))
    for x in "F.Ae,Z.b50,I.H.mFFFF".split(","):
        eq("cut-order arm %s is a pass arm" % x, A.get(x, {}).get("in_passes"), True)
    for b in bad:
        print("  MISMATCH " + b)
    print("%d comparisons, %d mismatches" % (n, len(bad)))
    print("ARMS CHECK %s" % ("PASS" if not bad else "FAIL"))


if __name__ == "__main__":
    main()
