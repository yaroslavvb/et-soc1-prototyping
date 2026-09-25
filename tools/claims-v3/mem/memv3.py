#!/usr/bin/env python3
"""V3-MEM helpers, shared by block.sh (checks at the end of a pass) and reduce.py (the pre-registered decisions).

No device access: this only reads files a pass left behind. CLI (block.sh calls these from the tree root):

    memv3.py finish --out PASS_DIR --card CARD          # drop.json for the pass (printed)
    memv3.py kept --root DATA_ROOT/mem --card CARD      # "<kept X1 passes> <kept wake-up probes>"
    memv3.py wake-needed --root DATA_ROOT/mem --card CARD --pass K   # 1 if pass K must run the wake-up probe
    memv3.py smoke --out SMOKE_DIR --card CARD          # parse check of a --smoke block (printed)

A pass directory holds, per program, <name>.u32 (memprobe_host) and <name>.json or <name>.json.gz (gen_ops labels),
telemetry.jsonl[.gz] (10 Hz sampler through the X1/X2 programs), memprobe.log (MEMPROBE lines), req<S>/ (anat-X2) and,
in wake-up passes, wake/ (wakeup program + pre.jsonl / post.jsonl 1 s samples).
"""
import argparse
import collections
import gzip
import json
import os
import re
import statistics as st
import struct
import sys

CARDS = ("aifoundry2", "aifoundry3")
X1_PROGS = ["t_raw", "t_glitch", "t_rawodd", "ladder", "decomp", "l3map", "msmap", "bits", "refresh", "refresh_jit",
            "pagetimeout"]
TIMER_PROGS = ["t_raw", "t_glitch", "t_rawodd"]
REQUESTERS = (7, 24, 31)
REQ_PROGS = ["ladder", "decomp"]
X1_TARGET = 5          # passes per card (plan: 5 per card; re-run dropped passes until >= 3 kept, target 5)
WAKE_NEEDED = 3        # wake-up probe passes per card (plan: passes 1-3)
M32 = 1 << 32


# ---------------------------------------------------------------- files
def _open(path):
    return gzip.open(path, "rt") if path.endswith(".gz") else open(path)


def find(d, stem):
    """<d>/<stem> or <d>/<stem>.gz, whichever exists."""
    for p in (os.path.join(d, stem), os.path.join(d, stem + ".gz")):
        if os.path.exists(p):
            return p
    return None


def read_json(path):
    with _open(path) as f:
        return json.load(f)


def read_jsonl(path):
    out = []
    if not path or not os.path.exists(path):
        return out
    with _open(path) as f:
        for line in f:
            line = line.strip()
            if line.startswith("{"):
                try:
                    out.append(json.loads(line))
                except ValueError:
                    pass
    return out


def prog(d, name):
    """(meta, labels, u32 values) of one program's output, or None if either file is missing."""
    j, u = find(d, name + ".json"), os.path.join(d, name + ".u32")
    if not j or not os.path.exists(u):
        return None
    m = read_json(j)
    raw = open(u, "rb").read()
    vals = struct.unpack(f"<{len(raw) // 4}I", raw[: len(raw) // 4 * 4])
    return m.get("meta", {}), [tuple(x) if isinstance(x, list) else x for x in m["labels"]], vals


def complete(d, name):
    """(ok, reason): the program's results exist and there is one u32 per label."""
    j, u = find(d, name + ".json"), os.path.join(d, name + ".u32")
    if not j:
        return False, "no labels"
    if not os.path.exists(u):
        return False, "no results"
    n = len(read_json(j)["labels"])
    size = os.path.getsize(u)
    if size != 4 * n:
        return False, f"{size // 4} results for {n} labels"
    return True, "ok"


def signed(v):
    return v - M32 if v >= 1 << 31 else v


# ---------------------------------------------------------------- clock / drop rules
def clock(samples):
    """The drop rule reads the samples that carry a clock: a sample whose frequency request failed (ettelem prints no
    "mhz" then) is a gap, not a sample off 600 MHz. all600: at least one clock reading, and every reading is 600."""
    mhz = collections.Counter()
    no_clock = 0
    for s in samples:
        v = (s.get("mhz") or {}).get("minion")
        if v is None:
            no_clock += 1
        else:
            mhz[str(v)] += 1
    return {"n": len(samples), "n_no_clock": no_clock, "mhz_minion": dict(mhz),
            "all600": bool(mhz) and set(mhz) == {"600"},
            "die_c": [s["temp_c"]["minshire"][0] for s in (samples[:1] + samples[-1:])
                      if isinstance(s.get("temp_c"), dict) and s["temp_c"].get("minshire")]}


def block_status(pdir):
    p = os.path.join(pdir, "block.json")
    if not os.path.exists(p):
        return None
    try:
        return read_json(p)
    except ValueError:
        return None


def memprobe_lines(pdir):
    out = []
    for f in ("info.log", "memprobe.log"):
        p = os.path.join(pdir, f)
        if os.path.exists(p):
            for line in open(p, errors="replace"):
                if line.startswith("MEMPROBE "):
                    try:
                        out.append(json.loads(line[9:]))
                    except ValueError:
                        pass
    return out


def pass_status(pdir, card):
    """Everything the drop rules need, from the files alone (the reducer never trusts drop.json)."""
    progs = {n: complete(pdir, n) for n in X1_PROGS}
    x1_complete = all(ok for ok, _ in progs.values())
    tel = read_jsonl(find(pdir, "telemetry.jsonl"))
    clk = clock(tel)
    if card == "aifoundry2":
        # plan: drop an aifoundry2 pass only on telemetry: any sample with mhz.minion != 600, or no telemetry
        keep_clock = clk["all600"]
        why = "" if keep_clock else ("no telemetry" if not clk["n"] else "no clock reading" if not clk["mhz_minion"]
                                     else f"mhz.minion {clk['mhz_minion']}")
    else:
        keep_clock, why = True, ""   # aifoundry3 is pinned at 600 MHz; its clock is recorded, not a drop rule
    missing = [f"{n}: {r}" for n, (ok, r) in progs.items() if not ok]
    req = {}
    for s in REQUESTERS:
        rd = os.path.join(pdir, f"req{s}")
        rr = {n: complete(rd, n) for n in REQ_PROGS}
        req[s] = all(ok for ok, _ in rr.values())
    lines = memprobe_lines(pdir)
    bases = sorted({l.get("arena_base") for l in lines if l.get("arena_base")})
    wake = None
    wd = os.path.join(pdir, "wake")
    if os.path.isdir(wd) and find(wd, "wakeup.json"):
        wok, wwhy = complete(wd, "wakeup")
        pre, post = clock(read_jsonl(find(wd, "pre.jsonl"))), clock(read_jsonl(find(wd, "post.jsonl")))
        if card == "aifoundry2":
            wkeep = wok and pre["all600"] and post["all600"]
            wreason = "" if wkeep else (wwhy if not wok else f"pre {pre['mhz_minion']} post {post['mhz_minion']}")
        else:
            wkeep, wreason = wok, ("" if wok else wwhy)
        wake = {"complete": wok, "keep": wkeep, "reason": wreason, "pre": pre, "post": post}
    return {"x1_complete": x1_complete, "missing": missing, "telemetry": clk,
            "x1_keep": x1_complete and keep_clock, "x1_reason": "; ".join(filter(None, [why] + missing)),
            "req_complete": req, "arena_bases": bases,
            "arena_aligned": (all(int(b, 16) % (1 << 30) == 0 for b in bases) if bases else None),
            "wake": wake}


def pass_dirs(root):
    """[(k, dir)] of p<k> under root (DATA_ROOT/mem), in pass order; attempts moved aside by the queue are skipped."""
    out = []
    if os.path.isdir(root):
        for n in os.listdir(root):
            m = re.fullmatch(r"p(\d+)", n)
            if m and os.path.isdir(os.path.join(root, n)):
                out.append((int(m.group(1)), os.path.join(root, n)))
    return sorted(out)


def kept_counts(root, card, before=None):
    nx = nw = 0
    for k, d in pass_dirs(root):
        if before is not None and k >= before:
            continue
        b = block_status(d)
        if not b or b.get("status") != "ok":
            continue
        s = pass_status(d, card)
        nx += s["x1_keep"]
        nw += bool(s["wake"] and s["wake"]["keep"])
    return nx, nw


def attempted(root, j):
    """Pass j has been tried: its folder exists (any status) or the queue moved an attempt of it aside."""
    if os.path.isdir(os.path.join(root, f"p{j}")):
        return True
    return os.path.isdir(root) and any(n.startswith(f"p{j}.attempt-") for n in os.listdir(root))


def wake_needed(root, card, k):
    """Passes 1-3 always run the probe (as registered). A later pass runs it only while the card has fewer than 3 kept
    probes, counting passes 1-3 that were never tried as future probes (so a pass run out of order does not add one).
    A pass 1-3 that failed, or that the queue gave up on, is not a future probe: the queue does not run it again."""
    if k <= WAKE_NEEDED:
        return True
    _, nw = kept_counts(root, card, before=k)
    pending = sum(1 for j in range(1, WAKE_NEEDED + 1) if j != k and not attempted(root, j))
    return nw + pending < WAKE_NEEDED


# ---------------------------------------------------------------- the cycle counter (E-hub-2: MEM-R1, R2, R3)
U = list(range(-1, 128))   # e = the largest low-7-bit value that reads 128 short; -1 = no short window at all
DIFF_OK = {10, 138, M32 - 118}


def _pred(e, l0, l1):
    return (10 + 128 * (int(l0 <= e) - int(l1 <= e))) % M32


def _consistent(combos):
    return [e for e in U if all(_pred(e, l0, l1) == d for (l0, l1, d) in combos)]


def _rng(es):
    if es is None:
        return None
    if not es:
        return "none"
    es = sorted(es)
    runs, a, b = [], es[0], es[0]
    for x in es[1:]:
        if x == b + 1:
            b = x
        else:
            runs.append((a, b)); a = b = x
    runs.append((a, b))
    return ",".join(str(a) if a == b else f"{a}..{b}" for a, b in runs)


def raw_readout(labs, vals, registered_lows):
    """A raw-pair program (t_raw, t_rawodd). A raw read whose low 7 bits are <= e comes back 128 short, and its low
    bits are unchanged, so each pair (first read at low bits L0, second at L1, difference d) is consistent with the
    windows e for which 10 + 128*([L0 <= e] - [L1 <= e]) == d. The registered readout uses only the pairs whose first
    read is at registered_lows (t_raw: 0, 10; t_rawodd: 0, 1, 10, 11); R1 uses every pair."""
    pr = collections.defaultdict(dict)
    for l, v in zip(labs, vals):
        if isinstance(l, tuple) and len(l) >= 3 and l[0] == "raw" and l[2] in ("t0", "t1"):
            pr[l[1]][l[2]] = v
    pairs = [(x["t0"], x["t1"]) for _, x in sorted(pr.items()) if "t0" in x and "t1" in x]
    diffs = collections.Counter((b - a) % M32 for a, b in pairs)
    combos = {((a & 127), (b & 127), (b - a) % M32) for a, b in pairs}
    all_set = _consistent(combos)
    # The registered readout (R2) reads e only from pairs that the window model can produce (10, 138, -118); a pair
    # outside those is an R1 exception, not a reading of e. A readout that no single e fits is not a reading either
    # (R1 reports it): it must not count as a distinct e for R2.
    reg = {c for c in combos if c[0] in registered_lows and c[2] in DIFF_OK}
    reached = sorted({a & 127 for a, _ in pairs})
    reg_reached = sorted({c[0] for c in reg})
    readout = _consistent(reg) if reg else None
    readout_empty = readout == []
    if readout_empty:
        readout = None
    bad = {signed(k): n for k, n in diffs.items() if k not in DIFF_OK}
    r1 = (not bad) and bool(all_set) and bool(set(all_set) & {9, 10, 11})
    return {"pairs": len(pairs), "diffs": {str(signed(k)): n for k, n in sorted(diffs.items())},
            "bad_diffs": {str(k): n for k, n in bad.items()}, "e_all_pairs": _rng(all_set),
            "e_readout": "none fits" if readout_empty else _rng(readout), "readout_set": readout,
            "registered_phases_reached": reg_reached, "phases_reached": len(reached),
            "odd_phases_reached": sum(1 for x in reached if x % 2), "r1_ok": r1,
            "r1_why": ("" if r1 else "differences outside 10/138/-118" if bad else
                       "no single window 0..e fits every pair" if not all_set else
                       f"window e in {_rng(all_set)}, outside 9-11")}


def _mode(xs):
    c = collections.Counter(xs)
    return max(c, key=lambda k: (c[k], -k))


def glitch_readout(labs, vals):
    """t_glitch: stamps (corrected with fixcyc's threshold 11) and timed no-ops (corrected intervals, 10 when right).
    Registered test: no +-128 errors -> e = 10; the -128 cluster 10 cycles after the +128 cluster (in stamp phase)
    -> 9; 10 cycles before -> 11; anything else is an exception (R1). R3: 1-3% of intervals off by 128 when e is 9 or
    11 (0 when e = 10)."""
    s = [v for l, v in zip(labs, vals) if l[0] == "s"]
    n = [signed(v) for l, v in zip(labs, vals) if l[0] == "n"]
    plus = [a & 127 for a, x in zip(s, n) if x == 138]
    minus = [a & 127 for a, x in zip(s, n) if x == -118]
    odd = collections.Counter(x for x in n if x not in (10, 138, -118))
    N = len(n)
    out = {"intervals": N, "plus128": len(plus), "minus128": len(minus),
           "other_values": {str(k): v for k, v in sorted(odd.items())}}
    e, why = None, ""
    if odd:
        why = "intervals other than 10/138/-118"
    elif not plus and not minus:
        e = 10
    elif plus and minus:
        mp, mm = _mode(plus), _mode(minus)
        delta = (mm - mp) % 128
        out.update({"plus_phase": mp, "minus_phase": mm, "delta": delta,
                    "plus_within1": sum(1 for x in plus if min((x - mp) % 128, (mp - x) % 128) <= 1) / len(plus),
                    "minus_within1": sum(1 for x in minus if min((x - mm) % 128, (mm - x) % 128) <= 1) / len(minus)})
        e = 9 if delta == 10 else 11 if delta == 118 else None
        why = "" if e is not None else f"clusters {delta} phases apart (not +-10)"
    else:
        why = "only one sign of error"
    frac = (len(plus) + len(minus)) / N if N else None
    out["off128_frac"] = frac
    out["e"] = e
    out["readout_set"] = [e] if e is not None else None
    out["e_readout"] = str(e) if e is not None else None
    out["r1_ok"] = e in (9, 10, 11)
    out["r1_why"] = why
    if e == 10:
        r3 = len(plus) + len(minus) == 0
    elif e in (9, 11):
        r3 = frac is not None and 0.01 <= frac <= 0.03
    else:
        r3 = False
    out["r3_ok"] = r3
    return out


def timer_readouts(pdir):
    out = {}
    for name, lows in (("t_raw", {0, 10}), ("t_rawodd", {0, 1, 10, 11})):
        p = prog(pdir, name)
        out[name] = raw_readout(p[1], p[2], lows) if p else None
    p = prog(pdir, "t_glitch")
    out["t_glitch"] = glitch_readout(p[1], p[2]) if p else None
    return out


# ---------------------------------------------------------------- the wake-up probe (EXP-dvfs-1: MEM-W)
LEVELS = {-1: "L1-in-place", 0: "L1", 1: "L2", 2: "L3", 3: "DRAM"}
L1_REF_22SEP = 17   # raw L1 hit of the 22 Sep wake-up run: the frame the P3 bands (59-62, 48-51) were written in
BIG = 16000000


def dram_class(x):
    if 8 <= x <= 15:
        return "slow"
    if -7 <= x <= 7:
        return "fast"
    if abs(x) > 30:
        return "outlier"
    return "other"


def wake_values(wdir):
    p = prog(wdir, "wakeup")
    meta, labs, vals = p
    lat = {}
    for l, v in zip(labs, vals):
        if l[0] == "wake":
            lat[(l[1], l[2], l[3])] = signed(v)
    delays, reps = meta["delays"], meta["reps"]
    R = range(reps)
    l1 = [v for (lev, _, _), v in lat.items() if lev in (-1, 0)]
    ref = st.median(l1)
    shift = ref - L1_REF_22SEP
    out = {"reps": reps, "delays": delays, "l1_raw_median": ref, "shift_to_22sep_frame": shift}
    if reps != 20 or BIG not in delays or 0 not in delays:
        out["evaluable"] = False
        return out
    out["evaluable"] = True
    diff = lambda lev, d: [lat[(lev, d, r)] - lat[(lev, 0, r)] for r in R]  # noqa: E731
    idle = [d for d in delays if d]
    # P1: L1 and L1-in-place: paired difference exactly 0 at every idle in >= 19 of 20 lines; exceptions exactly +-128
    p1 = {}
    for lev in (-1, 0):
        zero = sum(1 for r in R if all(lat[(lev, d, r)] - lat[(lev, 0, r)] == 0 for d in idle))
        nz = [lat[(lev, d, r)] - lat[(lev, 0, r)] for r in R for d in idle if lat[(lev, d, r)] != lat[(lev, 0, r)]]
        p1[LEVELS[lev]] = {"lines_all_zero": zero, "exceptions_pm128": all(abs(x) == 128 for x in nz),
                           "nonzero_values": sorted(set(nz))}
    out["P1"] = {"levels": p1, "holds": all(v["lines_all_zero"] >= 19 and v["exceptions_pm128"] for v in p1.values())}
    # P2: L3 median paired difference at 16M cycles within +-2
    m3 = st.median(diff(2, BIG))
    out["P2"] = {"median_diff_16M": m3, "holds": abs(m3) <= 2}
    # P3: L2 (re-referenced to the 22 Sep frame): no-idle 59-62 and every idle >= 1,000 cycles 48-51 in >= 18 of 20
    # lines; at the 300-cycle delay the median is within 1 cycle of the 16M median (the settling explanation)
    ok_lines = 0
    for r in R:
        a = lat[(1, 0, r)] - shift
        b = [lat[(1, d, r)] - shift for d in delays if d >= 1000]
        ok_lines += 59 <= a <= 62 and all(48 <= x <= 51 for x in b)
    p3 = {"lines_ok": ok_lines, "noidle_median": st.median(lat[(1, 0, r)] - shift for r in R),
          "idle16M_median": st.median(lat[(1, BIG, r)] - shift for r in R), "holds_a": ok_lines >= 18}
    if 300 in delays:
        m300 = st.median(lat[(1, 300, r)] for r in R)
        m16 = st.median(lat[(1, BIG, r)] for r in R)
        p3.update({"d300_median": m300 - shift, "holds_b": abs(m300 - m16) <= 1})
    else:
        p3["holds_b"] = None
    out["P3"] = p3
    # P4: DRAM paired differences at 16M: 40-85% at +8..+15, the rest within +-7 (at most 2 beyond +-30);
    # classes at 1,000 and 16M kept for the pooled agreement (>= 80% same class, per card)
    d16 = diff(3, BIG)
    cls16 = [dram_class(x) for x in d16]
    c = collections.Counter(cls16)
    slow = c["slow"] / reps
    out["P4"] = {"diffs_16M": d16, "classes_16M": dict(c), "slow_frac": slow,
                 "holds": 0.40 <= slow <= 0.85 and c["other"] == 0 and c["outlier"] <= 2}
    if 1000 in delays:
        cls1k = [dram_class(x) for x in diff(3, 1000)]
        out["P4"]["same_class_1000_16M"] = [a == b for a, b in zip(cls1k, cls16)]
    # P5, the claim itself: no level with a shift >= +5 cycles common to >= 18 of 20 lines at 16M cycles
    counts = {LEVELS[lev]: sum(1 for x in diff(lev, BIG) if x >= 5) for lev in LEVELS}
    out["P5"] = {"lines_ge5_by_level": counts, "holds": all(v < 18 for v in counts.values())}
    return out


# ---------------------------------------------------------------- CLI
def cmd_finish(a):
    s = pass_status(a.out, a.card)
    runs = read_jsonl(os.path.join(a.out, "runs.jsonl"))
    failed = [f"{r['dir']}/{r['name']} rc {r['rc']}" for r in runs if r.get("rc") != 0]
    notok = [f"{l.get('name')} ok false" for l in memprobe_lines(a.out) if l.get("test") == "program" and not l.get("ok")]
    s["program_failures"] = failed + notok
    s["card"] = a.card
    print(json.dumps(s, indent=1))


def cmd_kept(a):
    nx, nw = kept_counts(a.root, a.card)
    print(nx, nw)


def cmd_wake_needed(a):
    print(1 if wake_needed(a.root, a.card, a.k) else 0)


def cmd_smoke(a):
    """Every component of a pass, in the smallest form: outputs present and parseable, sampler lines with a clock,
    the arena base, the three counter readouts, a program run from shire 7, and the wake-up probe."""
    d, res = a.out, {"card": a.card}
    res["arena_bases"] = sorted({l.get("arena_base") for l in memprobe_lines(d) if l.get("arena_base")})
    res["programs"] = {}
    for sub, names in (("", ["t_raw", "t_glitch", "t_rawodd"]), ("req7", REQ_PROGS), ("wake", ["wakeup"])):
        for n in names:
            ok, why = complete(os.path.join(d, sub), n)
            res["programs"][(sub + "/" if sub else "") + n] = why
    res["telemetry"] = clock(read_jsonl(find(d, "telemetry.jsonl")))
    res["wake_pre"] = clock(read_jsonl(find(os.path.join(d, "wake"), "pre.jsonl")))
    res["wake_post"] = clock(read_jsonl(find(os.path.join(d, "wake"), "post.jsonl")))
    try:
        t = timer_readouts(d)
        res["timer"] = {k: (v and {x: v.get(x) for x in ("e_readout", "e_all_pairs", "diffs", "odd_phases_reached",
                                                          "plus128", "minus128", "r1_ok", "r1_why")}) for k, v in t.items()}
    except Exception as e:  # noqa: BLE001
        res["timer"] = f"error: {e!r}"
    lines = [l for l in memprobe_lines(d) if l.get("test") == "program"]
    res["req7_hart"] = sorted({l.get("hart") for l in lines if "req7" in l.get("out", "")})
    try:
        m, labs, vals = prog(os.path.join(d, "req7"), "decomp")
        res["req7_decomp_median_raw"] = {k: st.median(signed(v) for l, v in zip(labs, vals) if l[0] == k)
                                         for k in ("l2", "l3", "mem")}
    except Exception as e:  # noqa: BLE001
        res["req7_decomp_median_raw"] = f"error: {e!r}"
    try:
        m, labs, vals = prog(os.path.join(d, "wake"), "wakeup")
        res["wake_median_raw_by_level"] = {LEVELS[lev]: st.median(signed(v) for l, v in zip(labs, vals)
                                                                  if l[0] == "wake" and l[1] == lev) for lev in LEVELS}
    except Exception as e:  # noqa: BLE001
        res["wake_median_raw_by_level"] = f"error: {e!r}"
    problems = [k for k, v in res["programs"].items() if v != "ok"]
    if not res["arena_bases"] or any(int(b, 16) % (1 << 30) for b in res["arena_bases"]):
        problems.append("arena base missing or not 1 GB aligned")
    if not res["telemetry"]["n"]:
        problems.append("no sampler lines")
    if not (res["wake_pre"]["n"] and res["wake_post"]["n"]):
        problems.append("no pre/post sample")
    if res["req7_hart"] != [448]:
        problems.append("req7 did not run on hart 448")
    if not isinstance(res.get("timer"), dict) or any(v is None for v in res["timer"].values()):
        problems.append("timer readouts incomplete")
    res["problems"] = problems
    res["ok"] = not problems
    print(json.dumps(res, indent=1, default=str))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sp = ap.add_subparsers(dest="cmd", required=True)
    p = sp.add_parser("finish"); p.add_argument("--out", required=True); p.add_argument("--card", required=True)
    p.set_defaults(f=cmd_finish)
    p = sp.add_parser("kept"); p.add_argument("--root", required=True); p.add_argument("--card", required=True)
    p.set_defaults(f=cmd_kept)
    p = sp.add_parser("wake-needed"); p.add_argument("--root", required=True); p.add_argument("--card", required=True)
    p.add_argument("--pass", dest="k", type=int, required=True); p.set_defaults(f=cmd_wake_needed)
    p = sp.add_parser("smoke"); p.add_argument("--out", required=True); p.add_argument("--card", required=True)
    p.set_defaults(f=cmd_smoke)
    a = ap.parse_args()
    a.f(a)


if __name__ == "__main__":
    sys.exit(main())
