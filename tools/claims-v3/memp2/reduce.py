#!/usr/bin/env python3
"""memp2 reduction: the decision code of prereg/PREREG.md (off-card; reads files only).

    reduce.py --check-pass <pass dir>          post-block check: writes <dir>/check.json, prints "<status> <note>"
    reduce.py --pass <pass dir>                that pass's metrics as JSON
    reduce.py --all --data <root> --out <dir>  every card under <root>/<card>/memp2/p<N>/: memp2.json + memp2.log
    reduce.py --self-test                      the dry simulators' four worlds through the whole chain

Items (PREREG.md has the predictions, bands and rules; the constants below are those):
  R33a  row conflicts with the L3 defeated: which address bits separate two rows' banks
  R33b  refresh phase per line: which address bits change the refresh domain (predicted: the controller)
  R33c  back-to-back pairs from conflict state: which bits share A's controller
  R36   a second TensorLoad of the same 16 lines: does the L2 keep TensorLoad lines
  R43   TensorLoad bandwidth by stride, spread and neighbourhoods: which cap theory survives (B against C and Cc;
        A and D are refuted by earlier data and reported only)
  E102  64 B scratchpad tensor loads at stride 64 / 128 / 256: bandwidth and energy (PLAN3 energy-manual-102; a
        replication of E46 on the same cards, reported, not a registered PLAN3 verdict)
A card's development passes (aifoundry1 card 1) give development results; verdicts come from validation passes
(aifoundry3, then aifoundry2), each card on its own; a theory survives if it holds on every validation card that
decided it.
"""
import argparse
import gzip
import json
import math
import os
import shutil
import statistics as st
import subprocess
import random
import sys
import tempfile

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "tools", "claims-v3", "cat"))
sys.path.insert(0, HERE)


def _numpy_path():
    """catlib needs numpy: aifoundry1 keeps it in <tree>/pylib, aifoundry3 in <tree>/.venv (lib.sh sets both up for a
    block; a direct `python3 reduce.py` gets them here)."""
    try:
        import numpy  # noqa: F401
        return
    except ImportError:
        pass
    pl = os.path.join(ROOT, "pylib")
    if os.path.isdir(os.path.join(pl, "numpy")):
        sys.path.insert(0, pl)
        return
    vp = os.path.join(ROOT, ".venv", "bin", "python3")
    if os.path.exists(vp) and os.path.abspath(sys.prefix) != os.path.join(ROOT, ".venv") and not os.environ.get("MEMP2_REEXEC"):
        os.environ["MEMP2_REEXEC"] = "1"
        os.execv(vp, [vp] + sys.argv)


_numpy_path()

# ---------------------------------------------------------------- registered constants (PREREG.md)
MAP_L50 = {"col": "hit", "row+6": "hit", "row+7": "hit", "row+8": "hit", "row+9": "hit", "row+10": "hit",
           "row+11": "hit", "row+12": "hit", "rowc+13": "conflict", "rowc+14": "conflict", "rowc+15": "conflict",
           "rowc+16": "conflict", "rowc+17": "conflict", "row19": "conflict", "row+25": "conflict"}
R33A_SPLIT = -10.5                 # d_c below: no conflict (row hit); at or above: conflict
R33A_STEP = (-27.0, -15.0)         # median d over row+10..12: tRP + tRCD, from MEM-P4 (-12 [-15,-9] and +9 [6,12])
R33A_MIN_TRIALS = 12
R33B_SAME, R33B_DIFF = 60.0, 150.0
R33B_MIN_STALLS, R33B_MIN_R = 8, 0.5
R33B_STALL = 40.0
R33B_FRAC_DIFF, R33B_FRAC_SAME = 0.5, 0.8   # a bit's pairs: "different" if >= half read different; "same" if >= 80%
                                            # read same and none different; else "unclear"
R33B_READINGS = {   # the registered refresh-domain readings: (bits that must read different, bits that must read same)
    "per-controller": ({"6", "7", "8", "9"}, {"10", "11", "12", "13", "18"}),     # predicted (L50: PA[9] the channel)
    "per-memory-shire": ({"6", "7", "8"}, {"9", "10", "11", "12", "13", "18"}),   # a memory shire's channels share a timer
}
R33B_PER_BANK = {"10", "11", "12"}   # "per-bank": PA[6-8] and the L50 bank bits all read different
R33C_SHARE_MIN = 5.0               # "shares A's controller": median Delta >= 5 cycles and the 95% lower bound > 3
R33C_SHARE_LB = 3.0
R33C_SEP_UB = 5.0                  # "another controller": the 95% upper bound < 5 (the alternative: Delta in [0, 3])
R33C_BOOT, R33C_SEED = 2000, 33
R33C_CTRL18 = (20.0, 60.0)
R33C_CTRL13 = (0.0, 10.0)
BAND_L2, BAND_L3 = (30.0, 75.0), (75.0, 260.0)   # raw TLOAD cycles (the analysis offset of 5 not subtracted)
R36_TL1 = (600.0, 1300.0)
R36_REFL2 = (120.0, 280.0)
R36_TL2_OVER_REFL2 = (0.8, 1.25)
R43_TOL_REL, R43_TOL_ABS = 0.12, 4.0
E102_BW = (0.60, 0.72)
E102_BW128 = (0.95, 1.05)
E102_T = (0.5, 1.5)
E102_MIN_REPS = 3

# R43 theories: predicted bytes per shire-cycle per configuration (PREREG.md, "R43").
R43_CFGS = ["s64-n1", "s64-n2", "s64-n3", "s64-n4", "s256-n1", "s256-n2", "s256-n3", "s256-n4",
            "s1k-n1", "s1k-n2", "s1k-n3", "s1k-n4", "s256b-n1", "s256b-n4", "s1kb-n4", "s1ks-n4",
            "s256q-n4", "s1kq-n4", "l2-s64-n4", "l2-s256-n4"]
R43_THEORIES = ("A", "B", "C", "Cc", "D")
R43_REFUTED = {   # refuted by data taken before memp2: computed and reported, never a candidate
    "A": "scp.bw-own: all 1,024 minions stream 128 B per shire-cycle where A predicts 204.8 (s64-n4)",
    "D": "scp.bw-one-neigh: one neighbourhood per shire streams about 50 B per shire-cycle where D predicts 32 (s64-n1)"}


def banks_subs(st_, spread):
    """The banks and sub-banks a configuration's minions use together (bank PA[7:6], sub-bank PA[9:8],
    facts-scp scp.addr-row): stride 64 touches all 16 sub-banks in one load; 256 one bank's 4; 1 KB one sub-bank."""
    if st_ == 64:
        return 4, 16
    if spread == "same":
        return 1, (4 if st_ == 256 else 1)
    if spread == "onebank":
        return 1, 4
    if spread == "bank":
        return 4, (16 if st_ == 256 else 4)
    return 4, 16                                # sub


def _r43_theory(name):
    """{theory: value} for one configuration. B: every bank returns a line every other cycle (32 B/cycle) and so does
    every sub-bank; C: a 128 B/cycle crossbar with banks at the spec's 64 and sub-banks at 32; Cc: C, plus a convoy
    (head-of-line blocking) at 32 B/cycle when every minion starts in the same sub-bank and walks in lockstep (the
    one-bank "same" configurations); D: 32 B/cycle per neighbourhood, banks 64, sub-banks 32; A: sub-banks only (the
    spec's 32 each, no other cap). Each minion alone streams 6.4 B/cycle (tl.one: 1 KB per 160 cycles), so n
    neighbourhoods offer at most 51.2 n. Only the "onebank" configurations (s256q, s1kq: one bank, the minions'
    starts staggered over its four sub-banks) separate B (32) from Cc (64)."""
    tag, nb = name.rsplit("-n", 1)
    n = int(nb)
    tag = tag.replace("l2-", "")
    st_ = {"s64": 64, "s256": 256, "s1k": 1024, "s256b": 256, "s1kb": 1024, "s1ks": 1024, "s256q": 256, "s1kq": 1024}[tag]
    spread = {"s256b": "bank", "s1kb": "bank", "s1ks": "sub", "s256q": "onebank", "s1kq": "onebank"}.get(tag, "same")
    banks, subs = banks_subs(st_, spread)
    minion = 51.2 * n
    C = min(minion, 128.0, 64.0 * banks, 32.0 * subs)
    return {"A": min(minion, 32.0 * subs),
            "B": min(minion, 32.0 * banks, 32.0 * subs),
            "C": C,
            "Cc": min(C, 32.0) if (spread == "same" and st_ >= 256) else C,
            "D": min(minion, 32.0 * n, 64.0 * banks, 32.0 * subs)}


R43_PRED = {c: _r43_theory(c) for c in R43_CFGS}


# ---------------------------------------------------------------- reading
def jload(path, default=None):
    for p in (path, path + ".gz"):
        if os.path.exists(p):
            try:
                with (gzip.open(p, "rt") if p.endswith(".gz") else open(p)) as f:
                    return json.load(f)
            except (OSError, ValueError):
                return default
    return default


def u32(path):
    for p in (path, path + ".gz"):
        if os.path.exists(p):
            raw = gzip.open(p, "rb").read() if p.endswith(".gz") else open(p, "rb").read()
            return [int.from_bytes(raw[i:i + 4], "little") for i in range(0, len(raw) - 3, 4)]
    return None


def program(d, name):
    """(labels as tuples, values, meta) for mp/<name>, or None."""
    j = jload(os.path.join(d, "mp", name + ".json"))
    v = u32(os.path.join(d, "mp", name + ".u32"))
    if j is None or v is None:
        return None
    labels = [tuple(x) for x in j["labels"]]
    if len(labels) != len(v):
        return {"error": f"{name}: {len(v)} results for {len(labels)} labels"}
    return labels, v, j["meta"]


def med(xs):
    xs = [x for x in xs if x is not None]
    return float(st.median(xs)) if xs else None


def band(x, b):
    return x is not None and b[0] <= x <= b[1]


# ---------------------------------------------------------------- R33a
def m_rowalt(d):
    pr = program(d, "rowalt")
    if pr is None or isinstance(pr, dict):
        return pr
    labels, vals, meta = pr
    cell = {}
    for lab, v in zip(labels, vals):
        _, c, t, j, w = lab
        if j == 0:
            continue                       # the first access of a condition: row state unknown
        cell.setdefault((c, t, w), []).append(v)
    trials = sorted({k[1] for k in cell})
    out = {"trials": len(trials), "conds": {}}
    for c in meta["conds"]:
        dA, mA, mB = [], [], []
        for t in trials:
            a, r = cell.get((c, t, "A")), cell.get(("row", t, "A"))
            if a and r:
                dA.append(med(a) - med(r))
                mA.append(med(a))
            if cell.get((c, t, "B")):
                mB.append(med(cell[(c, t, "B")]))
        out["conds"][c] = {"d": dA, "median_A": med(mA), "median_B": med(mB)}
    return out


def v_r33a(ms):
    ms = [m for m in ms if m and "conds" in m]
    trials = sum(m["trials"] for m in ms)
    if trials < R33A_MIN_TRIALS:
        return {"outcome": "INSUFFICIENT", "reading": f"{trials} trials (< {R33A_MIN_TRIALS})"}
    per, miss = {}, []
    for c, want in MAP_L50.items():
        ds = [x for m in ms for x in m["conds"].get(c, {}).get("d", [])]
        dc = med(ds)
        got = None if dc is None else ("hit" if dc < R33A_SPLIT else "conflict")
        per[c] = {"d": None if dc is None else round(dc, 2), "class": got, "predicted": want, "n": len(ds)}
        if got != want:
            miss.append(c)
    step = med([per[c]["d"] for c in ("row+10", "row+11", "row+12") if per[c]["d"] is not None])
    ok_step = band(step, R33A_STEP)
    out = "PASS" if not miss and ok_step else "FAIL"
    return {"outcome": out, "per_cond": per, "step_bank_bits": step, "step_band": R33A_STEP,
            "misclassified": miss, "trials": trials,
            "reading": (f"{len(MAP_L50) - len(miss)}/{len(MAP_L50)} conditions as the L50 map predicts; "
                        f"bank-bit step {step:+.1f} cycles (band {R33A_STEP})" if step is not None else "no step")}


# ---------------------------------------------------------------- R33b
def _unwrap(stamps):
    out, off, prev = [], 0, None
    for s in stamps:
        if prev is not None and s + off < prev - (1 << 31):
            off += 1 << 32
        out.append(s + off)
        prev = s + off
    return out


def _resultant(es, P):
    c = sum(math.cos(2 * math.pi * e / P) for e in es) / len(es)
    s = sum(math.sin(2 * math.pi * e / P) for e in es) / len(es)
    return math.hypot(c, s), math.atan2(s, c) * P / (2 * math.pi)


def m_refphase(d):
    pr = program(d, "refphase")
    if pr is None or isinstance(pr, dict):
        return pr
    labels, vals, meta = pr
    series = {}
    stamp = {}
    for lab, v in zip(labels, vals):
        kind, k, r, i, w = lab
        if kind == "rp_t":
            stamp[(k, r, i)] = v
        else:
            series.setdefault((f"{k}/{r}", w), []).append((stamp[(k, r, i)], v))
    lines = {}
    for key, sv in series.items():
        ts = _unwrap([s for s, _ in sv])
        lats = [v for _, v in sv]
        lm = med(lats)
        es = [t + v - lm / 2 for t, v in zip(ts, lats) if v - lm > R33B_STALL]
        lines[key] = {"lat_med": lm, "e": es, "n": len(lats)}
    use = [x for x in lines.values() if len(x["e"]) >= R33B_MIN_STALLS]
    if not use:
        return {"P": None, "pairs": {}}

    def score(P):
        return sum(_resultant(x["e"], P)[0] for x in use)
    grid = [2322.0 + 0.01 * i for i in range(701)]
    P = max(grid, key=score)
    P = max([P - 0.02 + 0.001 * i for i in range(41)], key=score)
    pairs = {}
    for k in sorted({k for k, _ in lines}):   # "<bit>/<rep>"
        a, b = lines.get((k, "A")), lines.get((k, "B"))
        rec = {"stalls_A": len(a["e"]) if a else 0, "stalls_B": len(b["e"]) if b else 0}
        if a and b and len(a["e"]) >= R33B_MIN_STALLS and len(b["e"]) >= R33B_MIN_STALLS:
            RA, pA = _resultant(a["e"], P)
            RB, pB = _resultant(b["e"], P)
            dphi = (pA - pB + P / 2) % P - P / 2
            rec.update({"R_A": round(RA, 3), "R_B": round(RB, 3), "dphi": round(dphi, 1),
                        "lat_A": a["lat_med"], "lat_B": b["lat_med"]})
            if min(RA, RB) < R33B_MIN_R:
                rec["class"] = "insufficient"
            else:
                ad = abs(dphi)
                rec["class"] = "same" if ad <= R33B_SAME else ("different" if ad >= R33B_DIFF else "unclear")
        else:
            rec["class"] = "insufficient"
        pairs[k] = rec
    return {"P": round(P, 3), "pairs": pairs}


def v_r33b(ms):
    ms = [m for m in ms if m and "pairs" in m]
    if not ms:
        return {"outcome": "INSUFFICIENT", "reading": "no refphase data"}
    cls, frac = {}, {}
    for k in ("6", "7", "8", "9", "10", "11", "12", "13", "18"):
        got = [rec["class"] for m in ms for key, rec in m["pairs"].items()
               if key.split("/")[0] == k and rec["class"] != "insufficient"]
        if not got:
            cls[k] = "insufficient"
            continue
        fd, fs = got.count("different") / len(got), got.count("same") / len(got)
        frac[k] = {"n": len(got), "different": round(fd, 2), "same": round(fs, 2)}
        cls[k] = "different" if fd >= R33B_FRAC_DIFF else ("same" if fs >= R33B_FRAC_SAME and fd == 0 else "unclear")
    diff_ms = [k for k in ("6", "7", "8") if cls[k] == "different"]
    reading = "; ".join(f"PA[{k}] {cls[k]}" for k in cls)
    if not diff_ms:
        return {"outcome": "INSUFFICIENT", "classes": cls, "P": [m["P"] for m in ms],
                "reading": "no memory-shire bit (6-8) reads a different refresh phase: the controllers refresh in "
                           "lockstep or the method cannot see them; " + reading}
    domain = sorted((k for k in cls if cls[k] == "different"), key=int)
    alt = "other"
    for name, (dif, same) in R33B_READINGS.items():
        if all(cls[k] == "different" for k in dif) and all(cls[k] == "same" for k in same):
            alt = name
            break
    else:
        if all(cls[k] == "different" for k in {"6", "7", "8"} | R33B_PER_BANK):
            alt = "per-bank"
    note = {"per-controller": "the refresh domain is the controller, PA[9] among its bits, as L50 predicts",
            "per-memory-shire": ("one refresh timer per memory shire: PA[9] reads same, which does not by itself refute "
                                 "PA[9] as the channel bit (see R33c's PA[9] delta, reported)"),
            "per-bank": "each bank refreshes on its own phase: bank bits read different, so the phase cannot name the channel",
            "other": "no registered reading fits"}[alt]
    return {"outcome": "PASS" if alt == "per-controller" else "FAIL", "classes": cls, "fractions": frac,
            "P": [m["P"] for m in ms], "refresh_domain_bits": domain, "alternative": alt,
            "reading": f"refresh-domain bits PA[{','.join(domain)}]: {alt} ({note}); " + reading}


# ---------------------------------------------------------------- R33c
def m_rrd(d):
    pr = program(d, "rrd")
    if pr is None or isinstance(pr, dict):
        return pr
    labels, vals, meta = pr
    cell = {}
    for lab, v in zip(labels, vals):
        kind, k, t = lab
        cell[(kind, k, t)] = v
    out = {}
    for k in meta["bits"]:
        ts = sorted({t for (kind, kk, t) in cell if kk == k})
        diffs = [cell[("ab", k, t)] - cell[("b", k, t)] for t in ts if ("ab", k, t) in cell and ("b", k, t) in cell]
        out[str(k)] = {"diffs": diffs, "ab": med([cell.get(("ab", k, t)) for t in ts]),
                       "b": med([cell.get(("b", k, t)) for t in ts]), "a": med([cell.get(("a", k, t)) for t in ts])}
    return {"bits": out}


def boot_median_ci(xs, n=R33C_BOOT, seed=R33C_SEED, conf=0.95):
    """Percentile bootstrap interval of the median (seeded: the same data give the same interval)."""
    if len(xs) < 2:
        return None
    rng = random.Random(seed)
    k = len(xs)
    meds = sorted(st.median([xs[rng.randrange(k)] for _ in range(k)]) for _ in range(n))
    a = (1 - conf) / 2
    return [float(meds[int(a * n)]), float(meds[min(n - 1, int((1 - a) * n))])]


def r33c_class(d, ci):
    if d is None or ci is None:
        return "no data"
    if d >= R33C_SHARE_MIN and ci[0] > R33C_SHARE_LB:
        return "shares"
    if ci[1] < R33C_SEP_UB:
        return "separate"
    return "unclear"


def v_r33c(ms):
    ms = [m for m in ms if m and "bits" in m]
    if not ms:
        return {"outcome": "INSUFFICIENT", "reading": "no rrd data"}
    D, CI, cls = {}, {}, {}
    for k in ("6", "7", "8", "9", "10", "11", "12", "13", "18"):
        xs = [x for m in ms for x in m["bits"].get(k, {}).get("diffs", [])]
        D[k] = med(xs)
        CI[k] = boot_median_ci(xs)
        cls[k] = r33c_class(D[k], CI[k])
    ctrl = band(D["18"], R33C_CTRL18) and band(D["13"], R33C_CTRL13)
    reading = "; ".join(f"PA[{k}] {D[k]:+.1f} [{CI[k][0]:+.1f}, {CI[k][1]:+.1f}]" for k in D
                        if D[k] is not None and CI[k])
    if not ctrl:
        return {"outcome": "INSUFFICIENT", "delta": D, "ci95": CI, "reading": "a control is out of its band: " + reading}
    if cls["11"] == "shares" and cls["12"] == "shares":
        out = "PASS"
    elif "separate" in (cls["11"], cls["12"]):
        out = "FAIL"
    else:
        out = "INSUFFICIENT"
    return {"outcome": out, "delta": D, "ci95": CI, "class": cls, "reported_only": ["6", "7", "8", "9", "10"],
            "reading": f"PA[11] {cls['11']}, PA[12] {cls['12']}; " + reading}


# ---------------------------------------------------------------- R36
def m_treload(d):
    pr = program(d, "treload")
    if pr is None or isinstance(pr, dict):
        return pr
    labels, vals, meta = pr
    by = {}
    for lab, v in zip(labels, vals):
        by.setdefault(lab[0], []).append(v)
    out = {k: by.get(k, []) for k in ("tl1", "tl2", "ref_l2", "ref_l3", "probe_tl", "probe_l3tl", "tl1_1", "probe1",
                                      "sref_dram", "sref_l2", "sref_l3", "tnop")}
    e0 = (by.get("terr0") or [0])[0]         # before the first tensor op: an earlier kernel's bits do not count
    later = by.get("terr", []) + by.get("terr_end", [])
    out["terr0"] = e0
    out["terr_new"] = sum(1 for x in later if x & ~e0)
    return out


def level(x):
    if x is None:
        return None
    if BAND_L2[0] <= x < BAND_L2[1]:
        return "L2"
    if BAND_L3[0] <= x < BAND_L3[1]:
        return "L3"
    return "DRAM" if x >= BAND_L3[1] else "below-L2"


def v_r36(ms):
    ms = [m for m in ms if m and "tl1" in m]
    if not ms:
        return {"outcome": "INSUFFICIENT", "reading": "no treload data"}
    pool = {k: [x for m in ms for x in m[k]] for k in ms[0] if k not in ("terr0", "terr_new")}
    M = {k: med(v) for k, v in pool.items()}
    terr_new = sum(m.get("terr_new", 0) for m in ms)
    valid = (level(M["sref_l2"]) == "L2" and level(M["sref_l3"]) == "L3" and level(M["sref_dram"]) == "DRAM"
             and not terr_new)
    if not valid:
        return {"outcome": "INSUFFICIENT", "medians": M, "reading": "the scalar ladder or tensor_error failed its check"}

    def nearest(x):
        refs = {"L2": M["ref_l2"], "L3": M["ref_l3"], "DRAM": M["tl1"]}
        return min(refs, key=lambda r: abs(math.log(x / refs[r])) if refs[r] and x else 1e9)
    tl2 = nearest(M["tl2"])
    probes = {k: level(M[k]) for k in ("probe_tl", "probe1", "probe_l3tl")}
    keeps = tl2 == "L2" and probes["probe_tl"] == "L2" and probes["probe1"] == "L2"
    alt = ("L3 only" if tl2 == "L3" and probes["probe_tl"] == "L3" else
           "neither" if tl2 == "DRAM" and probes["probe_tl"] == "DRAM" else "mixed")
    bands = {"tl1": band(M["tl1"], R36_TL1), "ref_l2": band(M["ref_l2"], R36_REFL2),
             "tl2/ref_l2": band(M["tl2"] / M["ref_l2"] if M["ref_l2"] else None, R36_TL2_OVER_REFL2)}
    return {"outcome": "PASS" if keeps else "FAIL", "tl2_like": tl2, "probes": probes, "bands": bands,
            "medians": {k: round(v, 1) for k, v in M.items() if v is not None},
            "reading": (f"second TensorLoad {M['tl2']:.0f} cycles (like {tl2}; L2 ref {M['ref_l2']:.0f}, L3 ref "
                        f"{M['ref_l3']:.0f}, first {M['tl1']:.0f}); scalar probe after it {M['probe_tl']:.0f} ({probes['probe_tl']})"
                        + ("" if keeps else f"; alternative: {alt}"))}


# ---------------------------------------------------------------- R43
def m_tloop(d):
    tl = os.path.join(d, "tl")
    out = {}
    if not os.path.isdir(tl):
        return out
    for fn in sorted(os.listdir(tl)):
        if not fn.endswith(".out"):
            continue
        vals, bad, launches = [], 0, 0
        for line in open(os.path.join(tl, fn)):
            if not line.startswith("MEMPROBE {"):
                continue
            r = json.loads(line[9:])
            if r.get("test") != "tloop":
                continue
            launches += 1
            if not r.get("ok") or r.get("tensor_errors") or r.get("launch_ok") is False:
                bad += 1
                continue
            if r["where"] == "arena" and r["launch"] == 0:
                continue                   # the L2-resident buffer's warm-up launch
            vals += r["bytes_per_shire_cycle"]
        out[fn[:-4]] = {"values": vals, "launches": launches, "bad": bad, "median": med(vals)}
    return out


def v_r43(ms, r36="PASS"):
    """The l2-* configurations are warmed with scalar loads (MP_TL_WARM), but they still assume the L2 keeps the
    lines; unless R36 PASSes on the same card they are reported and left out of the survival test."""
    ms = [m for m in ms if m]
    use = [c for c in R43_CFGS if r36 == "PASS" or not c.startswith("l2-")]
    got = {}
    for c in R43_CFGS:
        vs = [x for m in ms for x in m.get(c, {}).get("values", [])]
        got[c] = med(vs)
    bad = sum(m.get(c, {}).get("bad", 0) for m in ms for c in m)
    if bad or any(got[c] is None for c in use):
        return {"outcome": "INSUFFICIENT", "measured": got, "bad_launches": bad,
                "reading": f"{bad} failed launches; {sum(got[c] is None for c in use)} configurations without data"}
    surv, misses = [], {}
    for th in R43_THEORIES:
        miss = []
        for c in use:
            p = R43_PRED[c][th]
            if abs(got[c] - p) > max(R43_TOL_REL * p, R43_TOL_ABS):
                miss.append(f"{c} {got[c]:.1f} vs {p:.1f}")
        misses[th] = miss
        if not miss:
            surv.append(th)
    live = [t for t in surv if t not in R43_REFUTED]
    l2_note = "" if len(use) == len(R43_CFGS) else f"; l2-* reported only (R36 {r36})"
    return {"outcome": "PASS" if "B" in surv else "FAIL", "survivors": surv, "live_survivors": live,
            "refuted_before_data": R43_REFUTED, "misses": misses, "configs_used": use,
            "measured": {c: (round(v, 2) if v is not None else None) for c, v in got.items()},
            "reading": (f"surviving theories: {', '.join(surv) or 'none'} (A and D were refuted before memp2); "
                        f"T43-B misses {len(misses['B'])}, Cc misses {len(misses['Cc'])}" + l2_note)}


# ---------------------------------------------------------------- E102
def m_energy(d, card):
    import catlib   # tools/claims-v3/cat/catlib.py, imported read-only
    reps = []
    for sub in sorted(os.listdir(d)):
        if not (sub.startswith("e") and os.path.isdir(os.path.join(d, sub))):
            continue
        kept, dropped, expected, info = catlib.pass_bursts(os.path.join(d, sub), card, ROOT)
        rec = {"dir": sub, "dropped": dropped, "cfgs": {}}
        for b in kept:
            rec["cfgs"][b["cfg"]] = {"pj_per_byte": b.get("pj_per_byte"), "pj_per_op": b.get("pj_per_op"),
                                     "bytes_per_s": b.get("bytes_per_s"), "over_idle_w": b.get("over_idle_w"),
                                     "die_c_busy": b.get("die_c_busy")}
        reps.append(rec)
    return {"reps": reps}


def _tci(xs, conf=0.99):
    import catlib
    n = len(xs)
    if n < 2:
        return None
    m, s = st.mean(xs), st.stdev(xs)
    h = catlib.t_crit(n - 1, conf) * s / math.sqrt(n)
    return [m - h, m + h]


def v_e102(ms):
    reps = [r for m in ms if m for r in m.get("reps", [])]
    rows = []
    for r in reps:
        c = r["cfgs"]
        need = [f"scpline/stride{s}/{o}" for s in (64, 128, 256) for o in ("zeros", "random")] + ["spin/zeros/h1"]
        if any(k not in c for k in need):
            continue
        row = {}
        for o in ("zeros", "random"):
            E = {s: c[f"scpline/stride{s}/{o}"]["pj_per_byte"] for s in (64, 128, 256)}
            B = {s: c[f"scpline/stride{s}/{o}"]["bytes_per_s"] for s in (64, 128, 256)}
            ref_bw = 0.5 * (B[64] + B[128])
            dE = 64 * (E[256] - 0.5 * (E[64] + E[128]))
            pred = c["spin/zeros/h1"]["over_idle_w"] * 64 * (1 / B[256] - 1 / ref_bw) * 1e12
            row[o] = {"bw_ratio": B[256] / B[64], "bw128": B[128] / B[64], "dE_per_64B": dE, "dE_T102": pred}
        rows.append(row)
    if len(rows) < E102_MIN_REPS:
        return {"outcome": "INSUFFICIENT", "reading": f"{len(rows)} complete replicates (< {E102_MIN_REPS})"}
    res = {}
    for o in ("zeros", "random"):
        bw = [r[o]["bw_ratio"] for r in rows]
        dE = [r[o]["dE_per_64B"] for r in rows]
        pr = [r[o]["dE_T102"] for r in rows]
        ci = _tci(dE)
        res[o] = {"bw_ratio": st.mean(bw), "bw128": st.mean(r[o]["bw128"] for r in rows), "dE_per_64B": st.mean(dE),
                  "dE_ci99": ci, "dE_T102": st.mean(pr), "T102_ratio": st.mean(dE) / st.mean(pr) if st.mean(pr) else None}
    bw_ok = all(band(res[o]["bw_ratio"], E102_BW) and band(res[o]["bw128"], E102_BW128) for o in res)
    resolved = {o: res[o]["dE_ci99"][0] > 0 or res[o]["dE_ci99"][1] < 0 for o in res}
    t_ok = all(band(res[o]["T102_ratio"], E102_T) for o in res)
    return {"outcome": {"E102-bw": "PASS" if bw_ok else "FAIL",
                        "E102-e": "PASS" if resolved["random"] and res["random"]["dE_per_64B"] > 0 else "FAIL",
                        "E102-T": "PASS" if t_ok else "FAIL"},
            "replicates": len(rows), "per_operands": res, "plan3_within_noise": {o: not resolved[o] for o in res},
            "registered_in_plan3": False, "replication_of": "E46 (scpline/* on the same three cards)",
            "reading": "; ".join(f"{o}: BW 256/64 {res[o]['bw_ratio']:.3f}, dE {res[o]['dE_per_64B']:+.1f} pJ/64B "
                                 f"[{res[o]['dE_ci99'][0]:+.1f}, {res[o]['dE_ci99'][1]:+.1f}], T102 {res[o]['dE_T102']:.1f}"
                                 for o in res)}


# ---------------------------------------------------------------- pass level
def pass_info(d):
    p = jload(os.path.join(d, "pass.json"), {}) or {}
    return p


def pass_metrics(d):
    p = pass_info(d)
    kind = p.get("kind")
    out = {"pass": p.get("pass"), "kind": kind, "role": p.get("role"), "card": p.get("card")}
    if kind in ("PROBE", "SMOKE"):
        out.update({"rowalt": m_rowalt(d), "refphase": m_refphase(d), "rrd": m_rrd(d), "treload": m_treload(d),
                    "tloop": m_tloop(d)})
    if kind in ("ENERGY", "SMOKE"):
        out["energy"] = m_energy(d, p.get("card"))
    return out


def check_pass(d):
    p = pass_info(d)
    notes, status = [], "ok"
    kind = p.get("kind")
    if kind in ("PROBE", "SMOKE"):
        for name in ("rowalt", "rrd", "refphase", "treload"):
            pr = program(d, name)
            if pr is None:
                status = "fail"; notes.append(f"{name}: no results")
            elif isinstance(pr, dict):
                status = "fail"; notes.append(pr["error"])
        tl = m_tloop(d)
        want = [json.loads(l)["name"] for l in open(os.path.join(d, "tl", "plan.jsonl"))] if os.path.exists(os.path.join(d, "tl", "plan.jsonl")) else []
        for n in want:
            r = tl.get(n)
            if not r or r["launches"] == 0:
                status = "fail"; notes.append(f"tloop {n}: no launch")
            elif r["bad"]:
                status = "fail"; notes.append(f"tloop {n}: {r['bad']} bad launches")
        tr = m_treload(d)
        if isinstance(tr, dict) and tr.get("terr_new"):
            status = "fail"; notes.append(f"tensor_error gained bits in treload ({tr['terr_new']} readings)")
    if kind in ("ENERGY", "SMOKE"):
        for sub in sorted(os.listdir(d)):
            cj = jload(os.path.join(d, sub, "check.json"))
            if sub.startswith("e") and os.path.isdir(os.path.join(d, sub)):
                if not cj:
                    status = "fail"; notes.append(f"{sub}: no check.json")
                elif cj.get("status") not in ("ok",):
                    status = "fail" if status == "ok" else status
                    notes.append(f"{sub}: {cj.get('status')} {cj.get('note', '')[:120]}")
    res = {"status": status, "notes": notes, "kind": kind}
    json.dump(res, open(os.path.join(d, "check.json"), "w"), indent=1)
    return status, "; ".join(notes) or f"{kind} pass complete"


# ---------------------------------------------------------------- all cards
def card_verdicts(passes):
    probes = [pm for pm in passes if pm["kind"] == "PROBE"]
    energy = [pm for pm in passes if pm["kind"] == "ENERGY"]
    r36 = v_r36([pm["treload"] for pm in probes])
    v = {"R33a": v_r33a([pm["rowalt"] for pm in probes]), "R33b": v_r33b([pm["refphase"] for pm in probes]),
         "R33c": v_r33c([pm["rrd"] for pm in probes]), "R36": r36,
         "R43": v_r43([pm["tloop"] for pm in probes], r36["outcome"]), "E102": v_e102([pm["energy"] for pm in energy])}
    return v


THEORIES = {"L50 bank/row split (R33a)": ("R33a", "PASS"),
            "Refresh domain = controller, PA[6-9] its bits (R33b)": ("R33b", "PASS"),
            "PA[11], PA[12] share the controller (R33c)": ("R33c", "PASS"),
            "T36: the L2 keeps TensorLoad lines": ("R36", "PASS"), "T43-B: 32 B/cycle per bank": ("R43", "PASS"),
            "E102-bw: the same bank costs a third of the bandwidth": ("E102", "E102-bw"),
            "E102-e: stride-256 energy per byte resolved above the others": ("E102", "E102-e"),
            "T102: the extra is the awake minions' time": ("E102", "E102-T")}


def all_cards(data, outdir):
    cards = {}
    for card in sorted(os.listdir(data)):
        root = os.path.join(data, card, "memp2")
        if not os.path.isdir(root):
            continue
        ps = []
        for p in sorted(os.listdir(root)):
            d = os.path.join(root, p)
            if not (p.startswith("p") and p[1:].isdigit()):
                continue                       # attempts set aside, smoke copies
            bj = jload(os.path.join(d, "block.json"), {}) or {}
            if bj.get("status") != "ok":
                continue
            pm = pass_metrics(d)
            if pm["role"] in ("development", "validation"):
                ps.append(pm)
        roles = sorted({pm["role"] for pm in ps})
        cards[card] = {"role": roles[0] if len(roles) == 1 else roles, "passes": [pm["pass"] for pm in ps],
                       "items": card_verdicts(ps)}
    theories = {}
    for th, (item, key) in THEORIES.items():
        per = {}
        for card, c in cards.items():
            o = c["items"][item]["outcome"]
            o = o.get(key) if isinstance(o, dict) else o
            per[card] = {"role": c["role"], "outcome": o}
        val = [x["outcome"] for x in per.values() if x["role"] == "validation" and x["outcome"] in ("PASS", "FAIL")]
        theories[th] = {"per_card": per,
                        "survives": (all(o == "PASS" for o in val) if val else None),
                        "decided_on": len(val)}
    res = {"cards": cards, "theories": theories}
    os.makedirs(outdir, exist_ok=True)
    json.dump(res, open(os.path.join(outdir, "memp2.json"), "w"), indent=1, default=str)
    with open(os.path.join(outdir, "memp2.log"), "w") as f:
        for card, c in cards.items():
            f.write(f"== {card} ({c['role']}, passes {c['passes']})\n")
            for item, v in c["items"].items():
                f.write(f"  {item}: {v['outcome']}  {v.get('reading', '')}\n")
        f.write("== theories (survive = PASS on every validation card that decided)\n")
        for th, t in theories.items():
            f.write(f"  {th}: {t['survives']} (decided on {t['decided_on']} validation card(s); "
                    + ", ".join(f"{k} {x['outcome']}" for k, x in t["per_card"].items()) + ")\n")
    print(open(os.path.join(outdir, "memp2.log")).read())
    return res


# ---------------------------------------------------------------- self-test
def self_test():
    """The four dry worlds through gen_ops2 -> memp2lib dry-probe/dry-energy -> the pass metrics -> the verdicts."""
    import memp2lib
    sys.path.insert(0, os.path.join(ROOT, "workloads", "memprobe"))
    import gen_ops2
    tmp = tempfile.mkdtemp(prefix="memp2-selftest-")
    fails = []
    allpass = {"R33a": "PASS", "R33b": "PASS", "R33c": "PASS", "R36": "PASS", "R43": "PASS",
               "E102": {"E102-bw": "PASS", "E102-e": "PASS", "E102-T": "PASS"}}
    expect = {"predicted": allpass,
              "alt": {"R33a": "PASS", "R33b": "FAIL", "R33c": "FAIL", "R36": "FAIL", "R43": "FAIL",
                      "E102": {"E102-bw": "PASS", "E102-e": "FAIL", "E102-T": "FAIL"}},
              "lockstep": dict(allpass, R33b="INSUFFICIENT"),
              "alt2": dict(allpass, R33b="FAIL", R43="FAIL")}
    # beyond the outcome: the reading each alternative world must produce (item, field, value)
    detail = {"predicted": [("R33b", "alternative", "per-controller"), ("R43", "survivors", ["B"]),
                            ("R33c", "class", {"11": "shares", "12": "shares"})],
              "alt": [("R33b", "alternative", "other"), ("R43", "survivors", ["D"]),
                      ("R43", "configs_used", [c for c in R43_CFGS if not c.startswith("l2-")]),
                      ("R33c", "class", {"11": "separate", "12": "shares"})],
              "alt2": [("R33b", "alternative", "per-memory-shire"), ("R43", "survivors", ["Cc"])]}
    # the rules' constants and the PREREG table agree on the discriminating configurations
    for c, want in (("s1kq-n4", {"A": 128.0, "B": 32.0, "C": 64.0, "Cc": 64.0, "D": 64.0}),
                    ("s256q-n4", {"A": 128.0, "B": 32.0, "C": 64.0, "Cc": 64.0, "D": 64.0}),
                    ("s256-n4", {"A": 128.0, "B": 32.0, "C": 64.0, "Cc": 32.0, "D": 64.0})):
        if any(abs(R43_PRED[c][k] - v) > 1e-9 for k, v in want.items()):
            fails.append(f"R43_PRED[{c}] = {R43_PRED[c]}, expected {want}")
    for world in ("predicted", "alt", "lockstep", "alt2"):
        card = "aifoundry3"
        base = os.path.join(tmp, world, card, "memp2")
        for pas, kind in ((111, "PROBE"), (112, "PROBE"), (211, "ENERGY")):
            d = os.path.join(base, f"p{pas}")
            os.makedirs(os.path.join(d, "mp"), exist_ok=True)
            os.makedirs(os.path.join(d, "tl"), exist_ok=True)
            json.dump({"pass": pas, "kind": kind, "role": "validation", "card": card}, open(os.path.join(d, "pass.json"), "w"))
            json.dump({"status": "ok"}, open(os.path.join(d, "block.json"), "w"))
            if kind == "PROBE":
                gen_ops2.rowalt(os.path.join(d, "mp"), 12, pas * 10 + 1)
                gen_ops2.rrd(os.path.join(d, "mp"), 24, pas * 10 + 2)
                gen_ops2.refphase(os.path.join(d, "mp"), 300, 3000, pas * 10 + 3)
                gen_ops2.treload(os.path.join(d, "mp"), 12, pas * 10 + 4)
                with open(os.path.join(d, "tl", "plan.jsonl"), "w") as f:
                    for c in memp2lib.tloop_configs(pas):
                        f.write(json.dumps(c) + "\n")
                memp2lib.dry_probe(d, world, seed=pas)
            else:
                for r in (1, 2, 3):
                    e = os.path.join(d, f"e{r}")
                    os.makedirs(e, exist_ok=True)
                    sys.path.insert(0, os.path.join(ROOT, "workloads", "enercat"))
                    import run_catalogue
                    cfgs = [c for c in run_catalogue.configs() if c["cfg"].startswith("scpline/") or c["cfg"] == "spin/zeros/h1"]
                    json.dump({"host": card, "cfgs": cfgs}, open(os.path.join(e, "configs.json"), "w"))
                    memp2lib.dry_energy(e, world, seed=pas * 10 + r)
                    import catlib
                    catlib.check(e, card, ROOT)       # block.sh runs the same check after each runner pass
            st_, note = check_pass(d)
            if st_ != "ok":
                fails.append(f"{world} p{pas} check: {st_} {note}")
        res = all_cards(os.path.join(tmp, world), os.path.join(tmp, world, "out"))
        items = res["cards"][card]["items"]
        for it, want in expect[world].items():
            got = items[it]["outcome"]
            if got != want:
                fails.append(f"{world} {it}: got {got}, expected {want} ({items[it].get('reading', '')})")
        for it, field, want in detail.get(world, []):
            got = items[it].get(field)
            if isinstance(want, dict):
                got = {k: (got or {}).get(k) for k in want}
            if got != want:
                fails.append(f"{world} {it}.{field}: got {got}, expected {want}")
    shutil.rmtree(tmp, ignore_errors=True)
    if fails:
        print("SELF-TEST FAIL\n  " + "\n  ".join(fails))
        return 1
    print("SELF-TEST PASS: all four dry worlds give the expected outcome and reading on every item")
    return 0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check-pass")
    ap.add_argument("--pass", dest="pas")
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--data")
    ap.add_argument("--out")
    ap.add_argument("--self-test", action="store_true")
    a = ap.parse_args()
    if a.check_pass:
        s, n = check_pass(a.check_pass)
        print(f"{s} {n}")
        return 0 if s == "ok" else 1
    if a.pas:
        print(json.dumps(pass_metrics(a.pas), indent=1, default=str)[:20000])
        return 0
    if a.all:
        all_cards(a.data, a.out)
        return 0
    if a.self_test:
        return self_test()
    ap.print_help()
    return 2


if __name__ == "__main__":
    sys.exit(main())
