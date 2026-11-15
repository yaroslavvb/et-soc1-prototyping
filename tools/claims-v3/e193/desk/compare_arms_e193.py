#!/usr/bin/env python3
"""E193 desk check of code (registration, before any datum): the arms, cell by cell, in four places.

    python3 -I -B compare_arms_e193.py <request.md> <arms.tsv> <listing-A.txt> <listing-B.txt>

  R  request.md section 2's table (block, arm, what every worker does, host options), read from the file: its rows are
     found by their arm cells, and each arm's expected meaning below quotes the row's words it is checked against;
  T  arms.tsv (name, block, host options): the file the runner reads;
  D  the runner's own dry listings (run_x04.py --dry, session A = --blocks S,D,W,T and session B = --blocks C): every
     device call it would make, in its order;
  H  the host's reading of each call: the options parsed as host/main.cpp's parseSegments and run() parse them (a
     re-implementation here, line for line in what it keeps: segments split at --then, each over the first; window cut to
     whole periods; masks cut to 32 and 8 bits), so each arm's segments are compared by what the card is asked to do.
Checks: the arm names and blocks agree in R, T and D; R's host-option cell, its shorthand expanded by the rules written
below, equals T's options for every arm whose cell gives them in full; every arm's decoded segments (H) equal the meaning
R's row states; D's every call is the runner's defaults followed by T's options; runs a pass and passes; the trains are
A B B A with three launches a segment; the ladders of request.md section 2 are made of arms that exist.
Prints a report; exit 0 when every check holds, else 1.
"""
import collections
import re
import sys

req, tsv, la, lb = sys.argv[1:5]
bad = []


def check(cond, what):
    if not cond:
        bad.append(what)
    return cond


# ---- R: request.md section 2's table
text = open(req, encoding="utf-8").read()
sec = text.split("## 2. Arms and ladder steps", 1)[1].split("## 3.", 1)[0]
rows = []
for ln in sec.splitlines():
    if ln.startswith("| ") and not ln.startswith("| block") and not ln.startswith("|---"):
        cells = [c.strip() for c in ln.strip().strip("|").split("|")]
        rows.append(cells)
R = collections.OrderedDict()   # arm -> (block, what, options cell, row index)
for i, (block, arms, what, opts) in enumerate(rows):
    names = [a.strip() for a in arms.split(",")]
    stem = names[0].rsplit("_p", 1)[0] if "_p" in names[0] else None
    for n in names:
        if re.fullmatch(r"p\d+", n) and stem:
            n = stem + "_" + n
        R[n] = (block, what, opts.replace("`", ""), i)
print("R: request.md section 2: %d rows, %d arms (%s)" % (len(rows), len(R), ", ".join(R)))

# ---- T: arms.tsv
T = collections.OrderedDict()
for ln in open(tsv, encoding="utf-8"):
    if ln.strip() and not ln.startswith("#"):
        name, block, opts = ln.rstrip("\n").split("\t")
        T[name] = (block, opts)
print("T: arms.tsv: %d arms" % len(T))

# ---- D: the dry listings
DEF = "timeout -k 1 10 build/x04clock/host/x04clock_host --window 240000000 --seconds 4.0 --label "
D = collections.defaultdict(list)    # arm -> list of (session, pass, block, pos)
calls = {}
order = collections.defaultdict(list)
for sess, path in (("A", la), ("B", lb)):
    cur = None
    for ln in open(path, encoding="utf-8"):
        m = re.match(r"^DRY ET_DEVICES=(\d+) (.*)$", ln.rstrip("\n"))
        if m:
            check(m.group(1) == "0", "D: a call with ET_DEVICES=%s" % m.group(1))
            cmd = m.group(2)
            check(cmd.startswith(DEF), "D: a call without the runner's defaults: %s" % cmd[:80])
            rest = cmd[len(DEF):].split(" ", 1)
            arm, opts = rest[0], (rest[1] if len(rest) > 1 else "")
            calls.setdefault(arm, set()).add(opts)
            cur = arm
            continue
        m = re.match(r"^pass (\d+) block (\S+) (\S+): ", ln)
        if m:
            p, b, arm = int(m.group(1)), m.group(2), m.group(3)
            check(arm == cur, "D: listing out of step at %s" % ln.strip())
            order[(sess, p, b)].append(arm)
            D[arm].append((sess, p, b))
nA = sum(len(v) for k, v in order.items() if k[0] == "A")
nB = sum(len(v) for k, v in order.items() if k[0] == "B")
passesA = len({k[1] for k in order if k[0] == "A"})
passesB = len({k[1] for k in order if k[0] == "B"})
print("D: session A %d runs over %d passes (%d a pass); session B %d runs over %d passes (%d a pass)" % (
    nA, passesA, nA // max(passesA, 1), nB, passesB, nB // max(passesB, 1)))
check(nA == 26 * 9 and passesA == 9, "D: session A is not 26 runs a pass x 9")
check(nB == 15 * 9 and passesB == 9, "D: session B is not 15 runs a pass x 9")

# ---- names and blocks in R, T, D
print("\n" "1. names and blocks (R / T / D):")
names = list(T)
check(set(R) == set(T), "names differ between R and T: %s" % sorted(set(R) ^ set(T)))
check(set(D) == set(T), "names differ between D and T: %s" % sorted(set(D) ^ set(T)))
for n in names:
    rb = R.get(n, ("?",))[0]
    tb = T[n][0]
    db = sorted({b for _, _, b in D.get(n, [])})
    same = (rb == tb) and (db == [tb] or (tb == "anchor" and set(db) <= {"S", "D", "W", "T", "C"}))
    check(same, "block of %s: R %s, T %s, D %s" % (n, rb, tb, db))
    print("  %-18s R %-6s T %-6s D %-10s %s" % (n, rb, tb, ",".join(db), "OK" if same else "DIFF"))
print("  arms: %d, of which the anchor 1, trains %d; the other arms %d" % (
    len(T), sum(1 for n in T if T[n][0] == "T"), sum(1 for n in T if T[n][0] not in ("anchor", "T"))))
check(len(T) == 35 and sum(1 for n in T if T[n][0] == "T") == 6, "not 34 arms plus the anchor with six trains")

# ---- D's calls are exactly T's options
print("\n" "2. every dry call = the runner's defaults + arms.tsv's options:")
k = 0
for n in names:
    ok = calls.get(n) == {T[n][1]}
    k += ok
    check(ok, "D's calls for %s are not arms.tsv's options" % n)
print("  %d of %d arms" % (k, len(names)))


# ---- H: the host's reading
def parse(args):
    """host/main.cpp parseSegments + run(): a list of segment dicts as the kernel gets them."""
    parts = [[]]
    for w in args:
        if w == "--then":
            parts.append([])
        else:
            parts[-1].append(w)
    base = dict(arm="spin", cls="none", t1="same", every=1, mask=0xff, shires=0xffffffff, minions=0xfffffffe,
                window=240000000, period=65536, duty=50, cluster=0, hs=6000000, seg=0, seconds=3.0)
    keys = {"--arm": "arm", "--cls": "cls", "--t1": "t1", "--every": "every", "--mask": "mask", "--shires": "shires",
            "--minions": "minions", "--window": "window", "--period": "period", "--duty-pct": "duty",
            "--hs-limit": "hs", "--seg-launches": "seg", "--seconds": "seconds", "--label": "label"}

    def apply(o, ws):
        o = dict(o)
        i = 0
        while i < len(ws):
            w = ws[i]
            if w == "--cluster":
                o["cluster"] = 1
                i += 1
                continue
            v = ws[i + 1]
            kk = keys[w]
            o[kk] = v if kk in ("arm", "cls", "t1", "label") else (float(v) if kk == "seconds" else int(v, 0))
            i += 2
        return o
    b = apply(base, parts[0])
    segs = [b] + [apply(b, p) for p in parts[1:]]
    out = []
    for o in segs:
        win = o["window"] // o["period"] * o["period"]
        # the host cuts the window to whole credit periods in every arm (main.cpp run(): a.window = window / period *
        # period), so a "0.4 s" launch is 239,992,832 cycles at the default period: launch seconds are compared to 3 places
        # (dated, before this file was committed: the checker's first run compared them exactly and so flagged the 8 arms
        # whose expected meaning names a launch length; corrected here; no proposal file changed)
        out.append(dict(arm=o["arm"], cls=o["cls"], t1=o["t1"], every=o["every"], lanes=bin(o["mask"] & 0xff).count("1"),
                        mask=o["mask"] & 0xff, shires=bin(o["shires"] & 0xffffffff).count("1"),
                        minions=o["minions"] & 0xfffffffe, workers=bin(o["minions"] & 0xfffffffe).count("1"),
                        harts=0 if o["arm"] == "tk" else (1 if o["t1"] == "off" else 2), launch_s=round(win / 6.0e8, 3),
                        window=win, period=o["period"], duty=o["duty"], cluster=o["cluster"], seg=o["seg"]))
    return out


def nbhd(mask):
    """minions by neighbourhood (8 minions each): counts for neighbourhoods 0..3."""
    return [bin((mask >> (8 * q)) & 0xff).count("1") for q in range(4)]


SPIN2 = dict(arm="spin", t1="same", harts=2, shires=32, workers=31, launch_s=0.4)
# The meaning each row of request.md section 2 states, transcribed; each entry quotes the words it is checked against.
E = {
    "spin2": ("both harts: 512-slot no-op sled", [SPIN2]),
    "tk_s2": ("return at once (firmware's credit wait); 2, 11, 21, 32 shires launched", [dict(arm="tk", t1="off", harts=0, shires=2, launch_s=0.4)]),
    "tk_s11": ("(the same row)", [dict(arm="tk", t1="off", harts=0, shires=11, launch_s=0.4)]),
    "tk_s21": ("(the same row)", [dict(arm="tk", t1="off", harts=0, shires=21, launch_s=0.4)]),
    "tk": ("(the same row)", [dict(arm="tk", t1="off", harts=0, shires=32, launch_s=0.4)]),
    "tk_l100": ("as `tk`, launches of 0.1 and 0.2 s", [dict(arm="tk", t1="off", harts=0, shires=32, launch_s=0.1)]),
    "tk_l200": ("(the same row)", [dict(arm="tk", t1="off", harts=0, shires=32, launch_s=0.2)]),
    "wait2": ("both harts in a user credit wait (one credit per 65,536 cycles): duty 0", [dict(arm="wait", t1="same", harts=2, period=65536, shires=32, workers=31, launch_s=0.4)]),
    "duty33": ("per 65,536-cycle period: credit wait, then the 64-slot sled for 33 / 67 / 100 %", [dict(arm="duty", t1="same", harts=2, period=65536, duty=33, workers=31)]),
    "duty67": ("(the same row)", [dict(arm="duty", t1="same", harts=2, period=65536, duty=67, workers=31)]),
    "duty100": ("(the same row)", [dict(arm="duty", t1="same", harts=2, period=65536, duty=100, workers=31)]),
    "duty33f": ("as duty33 with 4,096- and 1,024-cycle periods", [dict(arm="duty", t1="same", harts=2, period=4096, duty=33, workers=31)]),
    "duty33k": ("(the same row)", [dict(arm="duty", t1="same", harts=2, period=1024, duty=33, workers=31)]),
    "w7": ("spin2 on 7, 15, 23 workers a shire (minions 8 up: neighbourhoods 1, 2, 3 first)", [dict(arm="spin", t1="same", harts=2, workers=7, minions=0x7f00)]),
    "w15": ("(the same row)", [dict(arm="spin", t1="same", harts=2, workers=15, minions=0x7fff00)]),
    "w23": ("(the same row)", [dict(arm="spin", t1="same", harts=2, workers=23, minions=0x7fffff00)]),
    "tr_tk_spin1": ("A: `tk`; B: hart 0 no-ops, hart 1 returns", [dict(arm="tk", t1="off"), dict(arm="spin", t1="off", harts=1)]),
    "tr_spin1_spin2": ("A: one hart of no-ops; B: two", [dict(arm="spin", t1="off", harts=1), dict(arm="spin", t1="same", harts=2)]),
    "tr_tk_stall2": ("A: `tk`; B: both harts, dependent 64-bit `div` chain on zeros", [dict(arm="tk", t1="off"), dict(arm="stall", t1="same", harts=2)]),
    "tr_faddps_fadds": ("A: `fadd.ps` every slot; B: `fadd.s` every slot", [dict(arm="mix", cls="fadd_ps", every=1, lanes=8), dict(arm="mix", cls="fadd_s", every=1)]),
    "tr_packed_spread": ("A: 8 workers in neighbourhood 1; B: 8 spread 3/3/2 over 1-3 (both harts no-ops)", [dict(arm="spin", harts=2, workers=8, minions=0xff00), dict(arm="spin", harts=2, workers=8, minions=0x03070700)]),
    "tr_spread_cluster": ("A: `fadd.ps` one in every 8 slots; B: the same 64 `fadd.ps` in a row, then 448 no-ops", [dict(arm="mix", cls="fadd_ps", every=8, cluster=0), dict(arm="mix", cls="fadd_ps", every=8, cluster=1)]),
}
for P in (1, 2, 4, 8, 16):
    E["faddps_p%d" % P] = ("both harts: one `fadd.ps` in every P slots, no-ops between", [dict(arm="mix", cls="fadd_ps", every=P, t1="same", harts=2, lanes=8, cluster=0, workers=31, shires=32)])
for P in (1, 2, 4, 8):
    E["fsgnjs_p%d" % P] = ("the same with `fsgnj.s`", [dict(arm="mix", cls="fsgnj_s", every=P, t1="same", harts=2, cluster=0, workers=31)])
E["fadds_p16"] = ("the same with `fadd.s`, P = 16", [dict(arm="mix", cls="fadd_s", every=16, t1="same", harts=2, workers=31)])
for nm, m, lanes in (("faddpsm1_p1", 0x01, 1), ("faddpsm2_p1", 0x03, 2), ("faddpsm4_p1", 0x0f, 4)):
    E[nm] = ("`fadd.ps` every slot with `m0` = 0x01, 0x03, 0x0f", [dict(arm="mix", cls="fadd_ps", every=1, mask=m, lanes=lanes, t1="same", harts=2)])

print("\n" "3. what every worker does: R's words against the host's reading of T's options (H):")
k = 0
for n in names:
    words, want = E[n]
    rq = R.get(n)
    quoted = rq is not None and (words == "(the same row)" or words.replace("`", "") in rq[1].replace("`", ""))
    check(quoted, "%s: the transcribed words are not request.md's row" % n)
    segs = parse(T[n][1].split())
    ok = True
    if T[n][0] == "T":
        A, Bs = segs[0], segs[1]
        ok &= len(segs) == 4 and segs[3] == A and segs[2] == Bs and A["seg"] == 3
        for got, w in ((A, want[0]), (Bs, want[1])):
            ok &= all(got[kk] == vv for kk, vv in w.items())
        detail = "A %s/%s %dh, B %s/%s %dh; segments %d, %d launches each, A B B A: %s" % (
            A["arm"], A["cls"], A["harts"], Bs["arm"], Bs["cls"], Bs["harts"], len(segs), A["seg"],
            segs[3] == A and segs[2] == Bs)
    else:
        s = segs[0]
        ok &= len(segs) == 1 and all(s[kk] == vv for kk, vv in want[0].items())
        detail = "%s cls %s P %d lanes %d t1 %s harts %d shires %d workers/shire %d (by nbhd %s) window %d cycles (%.3f s) period %d duty %d cluster %d" % (
            s["arm"], s["cls"], s["every"], s["lanes"], s["t1"], s["harts"], s["shires"], s["workers"], nbhd(s["minions"]),
            s["window"], s["launch_s"], s["period"], s["duty"], s["cluster"])
    k += ok and quoted
    check(ok, "%s: decoded %s" % (n, detail))
    print("  %-18s %s  %s" % (n, "OK  " if ok else "DIFF", detail))
print("  %d of %d arms as request.md's row says" % (k, len(names)))

# ---- R's host-option cells, expanded, against T
print("\n" "4. request.md's host-option cells, the shorthand expanded, against arms.tsv:")
# The expansion rules: 'X [--o a / b / c]' gives the row's first names X --o a, X --o b, X --o c and its last name X;
# 'X --o a / b / c' gives one alternative a name, in order; a leading '...' is the options of the arm the row's words name
# with "as" ("as `tk`", "as duty33"); a C row's '--cls c' (or '--mask') replaces those words of the first C row's options,
# P from the arm's name. (Dated, before this file was committed: the checker's first run read '...' as the row above's first
# arm, which gave tk_l100 and tk_l200 tk_s2's --shires; the row says "as `tk`". Corrected here; no proposal file changed.)
exp = {}
first_c = None
for i, (block, arms, what, opts) in enumerate(rows):
    o = opts.replace("`", "").strip()
    ns = [n for n, v in R.items() if v[3] == i]
    if block == "T":
        continue
    if o.startswith("..."):
        m_as = re.search(r"\bas `?([A-Za-z0-9_]+)`?", what)
        o = exp[m_as.group(1)] + o[3:]
    m = re.match(r"^(.*?)\s*\[(--\S+) (.*)\]$", o)
    if m:
        alts = [a.strip() for a in m.group(3).split("/")]
        for n, a in zip(ns, alts + [None]):
            exp[n] = m.group(1) + (" %s %s" % (m.group(2), a) if a else "")
    else:
        m = re.match(r"^(.*?)(--\S+) (\S+(?: / \S+)+)$", o)
        if m and block != "C":
            alts = [a.strip() for a in m.group(3).split("/")]
            for n, a in zip(ns, alts):
                exp[n] = m.group(1) + m.group(2) + " " + a
        elif block == "C":
            if first_c is None:
                first_c = o
            for n in ns:
                P = n.rsplit("_p", 1)[1]
                base = first_c.replace("--every P", "--every " + P)
                if o.startswith("--cls") and o != first_c:
                    base = re.sub(r"--cls \S+", o, base)
                if o == "--mask":
                    mk = {"faddpsm1_p1": "0x01", "faddpsm2_p1": "0x03", "faddpsm4_p1": "0x0f"}[n]
                    base = base.replace(" --t1", " --mask %s --t1" % mk)
                exp[n] = base
        else:
            for n in ns:
                exp[n] = o
k = 0
for n in names:
    if n not in exp:
        print("  %-18s (a train: its cell gives part of the options; checked by meaning in 3)" % n)
        continue
    a = parse(exp[n].split())
    b = parse(T[n][1].split())
    same = a == b
    k += same
    check(same, "%s: request.md's options '%s' differ from arms.tsv's '%s'" % (n, exp[n], T[n][1]))
    print("  %-18s %s  R: %s" % (n, "SAME" if same else "DIFF", exp[n]))
print("  %d of %d arms with a full cell: the same request to the card" % (k, len(exp)))

# ---- ladders (request.md section 2, after the table) exist
print("\n" "5. the ladders of request.md section 2 are made of arms that exist:")
LAD = {"tk over shires": ["tk_s2", "tk_s11", "tk_s21", "tk"], "tk over launch length": ["tk_l100", "tk_l200", "tk"],
       "duty": ["wait2", "duty33", "duty67", "duty100"], "workers": ["w7", "w15", "w23", "spin2"],
       "fadd.ps density": ["spin2", "faddps_p16", "faddps_p8", "faddps_p4", "faddps_p2", "faddps_p1"],
       "fsgnj.s density": ["spin2", "fsgnjs_p8", "fsgnjs_p4", "fsgnjs_p2", "fsgnjs_p1"],
       "mask lanes": ["faddpsm1_p1", "faddpsm2_p1", "faddpsm4_p1", "faddps_p1"]}
for lad, ns in LAD.items():
    ok = all(n in T for n in ns)
    check(ok, "ladder %s names a missing arm" % lad)
    print("  %-22s %s  %s" % (lad, "OK" if ok else "MISSING", ", ".join(ns)))

# ---- the order, written out
print("\n" "6. the order the runner draws (seed 1113: random.Random(1113 * 100 + pass * 10 + block index)), from the dry listings:")
for (sess, p, b), arms in sorted(order.items(), key=lambda kv: (kv[0][0], kv[0][1], "SDWTC".index(kv[0][2]))):
    print("  session %s pass %d block %s: %s" % (sess, p, b, " ".join(arms)))

print("\nARMS CHECK %s (%d problems)" % ("PASS" if not bad else "FAIL", len(bad)))
for b_ in bad:
    print("  PROBLEM: " + b_)
sys.exit(0 if not bad else 1)
