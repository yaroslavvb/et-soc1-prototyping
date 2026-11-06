#!/usr/bin/env python3
"""Q145(a), post hoc: the anatomy's measured top lines - every place the energy of one simple operation goes, as far as the
lab's committed data reach, per card, adding up to the board energy the card's own meter reads.

    python3 -I docs/reports/data/2026-11-05-q145a-anatomy-top-lines/anatomy_q145a.py --repo . \
        --out docs/reports/data/2026-11-05-q145a-anatomy-top-lines/anatomy.json \
        --txt docs/reports/data/2026-11-05-q145a-anatomy-top-lines/anatomy.txt

POST HOC throughout: written on Thu 5 Nov 2026 after every datum it reads was committed. Nothing here is a prediction, a
fit that enters a model, or a verdict. Pure Python (no numpy), reads committed files only, writes only --out and --txt.

What it does:
  (A) The TensorFMA step (one TensorFMA instruction on one minion: fp32 4,096 MACs, fp16 8,192, int8 16,384) on the zeros
      anchor, a one-number tile and random data, from pool 8's sessions E171 (aifoundry3) and E172 (aifoundry1 card 1) on
      their registered footing, and the one-number kinds of E78 (aifoundry3) and E82 (card 1) on Q139(u)'s footing. The
      board and the minion rail are the committed reductions' own values, recomputed per run from the committed telemetry
      with reduce_e78.py's windows (validated against the committed reductions below). The SRAM and NoC rails are new
      here: the same windows and the same first-order deconvolution (tau 0.95 s, delay 0.2 s) applied to the telemetry's
      sp.sram_w[0] and sp.noc_w[0], raw (no leakage correction).
  (B) The vector unit (fadd.pi, fadd.ps, fmadd.ps on zeros, the constant 1.0f and random data, both harts of all 1,024
      minions) from the energy manual's catalogue (catalogue.json, 26 Sep 2026, three cards), split by rail as the
      catalogue reduced it.
  (C) Which lines differ between one-number fills: paired per-pass differences, with t intervals.
  (D) The vector arm's public facts: the operand-port bit flips of Esperanto's public TXFMA power virus
      (aifoundry-org/et-platform 836a4ab60, core-et b38a1a3) against the lab's random rotation (workloads/enercat), and the
      lab's random fmadd.ps board and minion-rail energy and issue rate (catalogue.json).

The two public repositories are read from the git-ignored external/ directory, as the RTL bench reads core-et: clone
github.com/aifoundry-org/et-platform at 836a4ab60 and github.com/openhwfoundation/core-et at b38a1a3 into external/ first
(the output records both files' sha256 and the operand words it parsed).
SPDX-License-Identifier: Apache-2.0
"""
import argparse
import bisect
import csv
import gzip
import hashlib
import json
import math
import os
import re
import statistics
import struct

E = 1.602176634e-19        # C, the elementary charge (exact, SI 2019)
V_IN = 12.0                # V, the card's nominal 12 V input (the board meter's supply; the telemetry carries no VMON)
TAU, DELAY_MS, C_RB = 0.95, 200.0, 0.81   # reduce_e78.py's frozen rail model (E79)
DIP_W = 4.0                # E82 amendment A2's dip rule
T95 = {1: 12.706, 2: 4.303, 3: 3.182, 4: 2.776, 5: 2.571, 6: 2.447, 7: 2.365, 8: 2.306, 9: 2.262, 10: 2.228}
MACS = {"fp32": 4096, "fp16": 8192, "int8": 16384}
CPO = {"fp32": 546.001, "fp16": 546.001, "int8": 318.0}
CLOCK_HZ, MINIONS = 600e6, 1024

D171 = "docs/reports/data/2026-11-05-e171-blind8-aifoundry3"
D172 = "docs/reports/data/2026-11-05-e172-blind8-card1"
D78 = "docs/reports/data/2026-10-31-e78-kinds-energy-matrix"
D82 = "docs/reports/data/2026-10-31-e82-kinds-aifoundry1"
DQ139U = "docs/reports/data/2026-11-03-q139u-footing"
DEM = "docs/reports/data/2026-09-23-energy-manual"
DE71 = "docs/reports/data/2026-10-27-e71-idle-slope-aifoundry3"
VIRUS = "external/et-platform/test-compute-kernels/src/vpu_txfma_power_virus/kernel.h"
CORE_PS = "external/core-et/dv/tests/minion_core/c_asm_tests/power_vpu/ps/kernel.h"

# The sessions: (label, card, data dir, reduction json, raw sub-dir, the footing's leakage slope key)
SESSIONS = [
    ("E171", "aifoundry3", D171, D171 + "/e171.json", D171 + "/aifoundry3/e171", "a3"),
    ("E172", "aifoundry1-c1", D172, D172 + "/e172.json", D172 + "/aifoundry1-c1/e172", "c1"),
    ("E78", "aifoundry3", D78, DQ139U + "/reduced/e78-footing.json", D78 + "/aifoundry3/kinds", "a3"),
    ("E82", "aifoundry1-c1", D82, DQ139U + "/reduced/e82-footing.json", D82 + "/aifoundry1-c1/kinds", "c1"),
]
ITEMS = {
    "E171": ["fp32.zeros", "anchor_pi", "fp32.randn", "fp16.zeros", "fp16.randn", "int8.zeros", "int8.full"],
    "E172": ["fp32.zeros", "anchor_pi", "fp32.randn", "fp16.zeros", "fp16.randn", "int8.zeros", "int8.full"],
    "E78": ["fp32.zeros", "fp32.ones", "fp32.neg_ones", "fp32.pi", "anchor_pi", "fp32.randn", "fp16.zeros", "fp16.ones",
            "fp16.neg_ones", "fp16.randn", "int8.zeros", "int8.ones", "int8.neg_ones", "int8.full"],
    "E82": ["fp32.zeros", "fp32.ones", "fp32.neg_ones", "fp32.pi", "anchor_pi", "fp32.randn", "fp16.zeros", "fp16.ones",
            "fp16.neg_ones", "fp16.randn", "int8.zeros", "int8.ones", "int8.neg_ones", "int8.full"],
}
ZERO = {"fp32": "fp32.zeros", "fp16": "fp16.zeros", "int8": "int8.zeros"}
PAIRS = [  # (a, b): a - b, same format, same pass
    ("E78", "fp32.pi", "anchor_pi", "the same bytes (0x40490FDB everywhere) from the file and the host's built-in: the resolution floor"),
    ("E78", "fp32.pi", "fp32.ones", "pi against 1.0, both file tiles in the segments"),
    ("E82", "fp32.pi", "fp32.ones", "pi against 1.0, both file tiles in the segments"),
    ("E78", "anchor_pi", "fp32.ones", "pi against 1.0, v = w"), ("E78", "fp32.ones", "fp32.neg_ones", "1.0 against -1.0"),
    ("E78", "fp16.ones", "fp16.neg_ones", "fp16 1.0 against -1.0"), ("E78", "int8.neg_ones", "int8.ones", "int8 -1 against 1"),
    ("E82", "fp32.pi", "anchor_pi", "the same bytes, file against built-in: the resolution floor"),
    ("E82", "anchor_pi", "fp32.ones", "pi against 1.0, v = w"), ("E82", "fp32.ones", "fp32.neg_ones", "1.0 against -1.0"),
    ("E82", "fp16.ones", "fp16.neg_ones", "fp16 1.0 against -1.0"), ("E82", "int8.neg_ones", "int8.ones", "int8 -1 against 1"),
]
# the energy manual's per-card idle laws, 01-at-rest.md (e-folding held at 36 C): P_idle(T) = P_fix + A e^((T-80)/36)
IDLE_LAW = {"aifoundry2": (12.6, 23.3), "aifoundry3": (12.3, 25.0), "aifoundry1-c1": (14.1, 34.8)}
IDLE_LAW_SRC = "docs/energy-manual/01-at-rest.md, 'The law' and its Confidence bullet (aifoundry2's 21 Sep fit; aifoundry3 and card 1 refitted to the 26 Sep version-3 idle cycles)"


# ---------------------------------------------------------------------------------------------------- small helpers
def sha(path):
    return hashlib.sha256(open(path, "rb").read()).hexdigest()


def load_jsonl(path):
    if not os.path.exists(path) and os.path.exists(path + ".gz"):
        path += ".gz"
    op = gzip.open if path.endswith(".gz") else open
    out = []
    with op(path, "rt") as f:
        for line in f:
            if line.startswith("{"):
                try:
                    out.append(json.loads(line))
                except ValueError:
                    pass
    return out


def stat(v):
    v = [float(x) for x in v if x is not None]
    n = len(v)
    if not n:
        return {"mean": None, "sd": None, "se": None, "n": 0, "ci95": None}
    m = sum(v) / n
    if n < 2:
        return {"mean": m, "sd": None, "se": None, "n": 1, "ci95": None}
    sd = statistics.stdev(v)
    se = sd / math.sqrt(n)
    return {"mean": m, "sd": sd, "se": se, "n": n, "ci95": se * T95.get(n - 1, 1.96)}


class Series:
    """One telemetry channel on the pass's (dip-filtered) time base, with window means by bisection."""

    def __init__(self, t, x):
        self.t, self.x = t, x
        self.cum = [0.0]
        for v in x:
            self.cum.append(self.cum[-1] + v)

    def wmean(self, lo, hi):
        i, j = bisect.bisect_left(self.t, lo), bisect.bisect_left(self.t, hi)
        return ((self.cum[j] - self.cum[i]) / (j - i), j - i) if j > i else (None, 0)

    def deconv(self, lo, hi, tau=TAU, delay_ms=DELAY_MS):
        """reduce_e78.deconv: the mean of the rail's instantaneous power over [lo, hi) from its first-order-lagged reading."""
        a, b = lo + delay_ms, hi + delay_ms
        m, _ = self.wmean(a, b)
        ra, na = self.wmean(a - 150, a + 150)
        rb, nb = self.wmean(b - 150, b + 150)
        if m is None or not na or not nb:
            return None
        return m + tau * (rb - ra) / ((b - a) / 1000.0)


def pass_telemetry(path):
    rows = load_jsonl(path)
    B = [r.get("board_w") for r in rows]
    bad = set()
    for i in range(2, len(rows) - 2):          # E82 A2, once, as reduce_e171.py --drop-dips and Q139(u)'s footing F2
        if None not in (B[i], B[i - 2], B[i + 2]) and B[i] < min(B[i - 2], B[i + 2]) - DIP_W:
            bad.add(i)
    rows = [r for i, r in enumerate(rows) if i not in bad]
    t = [float(r["t_ms"]) for r in rows]
    ch = {
        "board": [float(r["board_w"]) for r in rows],
        "T": [float(r["temp_c"]["minshire"][0]) for r in rows],
        "minion": [float(r["sp"]["minion_w"][0]) for r in rows],
        "sram": [float(r["sp"]["sram_w"][0]) for r in rows],
        "noc": [float(r["sp"]["noc_w"][0]) for r in rows],
        "mv_minion": [float(r["die_mv"]["minion"]) for r in rows],
        "mv_sram": [float(r["die_mv"]["sram"]) for r in rows],
        "mv_noc": [float(r["die_mv"]["noc"]) for r in rows],
        "mv_ddr": [float(r["die_mv"]["ddr"]) for r in rows],
    }
    return {k: Series(t, v) for k, v in ch.items()}, len(bad)


def interp(pts, t):
    """reduce_e78.interp_zero: piecewise linear in time, flat beyond the first and last point."""
    if not pts:
        return None
    pts = sorted(pts)
    if len(pts) == 1 or t <= pts[0][0]:
        return pts[0][1]
    if t >= pts[-1][0]:
        return pts[-1][1]
    for (t1, v1), (t2, v2) in zip(pts, pts[1:]):
        if t1 <= t <= t2:
            return v1 + (v2 - v1) * (t - t1) / max(t2 - t1, 1e-9)
    return pts[-1][1]


def fnum(x):
    return None if x in (None, "", "None") else float(x)


# ---------------------------------------------------------------------------------------------------- (A) TensorFMA
def tensor_session(repo, label, card, ddir, red_path, raw, slope_key, k_footing):
    red = json.load(open(os.path.join(repo, red_path)))
    k = k_footing[slope_key]
    passes = [int(p) for p in red["passes"]]
    rows = list(csv.DictReader(open(os.path.join(repo, ddir, "runs.csv"))))
    want = set(ITEMS[label]) | set(ZERO.values())
    runs = []
    for r in rows:
        if int(r["pass"]) not in passes or r["item"] not in want:
            continue
        if str(r["fail"]).strip() not in ("0", "", "[]", "False"):
            continue
        runs.append(r)
    per = {}          # (pass, item) -> list of run dicts
    dips = {}
    for p in passes:
        ch, nd = pass_telemetry(os.path.join(repo, raw, f"p{p}", "telemetry.jsonl.gz"))
        dips[p] = nd
        rp = []
        for r in runs:
            if int(r["pass"]) != p:
                continue
            t0 = float(r["t0_ms"])
            lo, hi = t0 + 1000.0, t0 + 3000.0
            x = {"item": r["item"], "type": r["type"], "t0": t0, "start_c": fnum(r["start_c"]),
                 "idle_ok": r["idle_ok"] == "True", "rate": fnum(r["rate"])}
            x["p_raw"], x["n_win"] = ch["board"].wmean(lo, hi)
            x["t_win"] = ch["T"].wmean(lo, hi)[0]
            x["p_idle"], x["n_idle"] = ch["board"].wmean(t0 - 1200, t0 - 200)
            x["t_idle"] = ch["T"].wmean(t0 - 1200, t0 - 200)[0]
            for rail in ("minion", "sram", "noc"):
                x[rail + "_dec"] = ch[rail].deconv(lo, hi)
                x[rail + "_idle_dec"] = ch[rail].deconv(t0 - 1200, t0 - 200)
            # sensitivity: card 1's SRAM rail averages over about 0.54 s (E58), not 0.95 s
            x["sram054_dec"] = ch["sram"].deconv(lo, hi, tau=0.54)
            x["sram054_idle_dec"] = ch["sram"].deconv(t0 - 1200, t0 - 200, tau=0.54)
            for v in ("mv_minion", "mv_sram", "mv_noc", "mv_ddr"):
                x[v] = ch[v].wmean(lo, hi)[0]
                x[v + "_idle"] = ch[v].wmean(t0 - 1200, t0 - 200)[0]
            base = x["start_c"] if x["start_c"] is not None else x["t_win"]
            x["p80"] = x["p_raw"] - k * (x["t_win"] - base)
            x["idle80"] = None if x["p_idle"] is None else x["p_idle"] - k * (x["t_idle"] - base)
            x["rail80"] = x["minion_dec"] - C_RB * k * (x["t_win"] - base)
            x["rail_idle80"] = (None if x["minion_idle_dec"] is None or x["t_idle"] is None
                                else x["minion_idle_dec"] - C_RB * k * (x["t_idle"] - base))
            x["heat_w"] = None if x["t_idle"] is None else k * (x["t_win"] - x["t_idle"])   # the window's own heating, footing slope
            x["csv"] = {kk: fnum(r[kk]) for kk in ("p_raw", "p_idle", "rail_dec", "rail_idle_dec", "mv")}
            rp.append(x)
        z = {ty: sorted((x["t0"], x["p80"]) for x in rp if x["item"] == ZERO[ty]) for ty in ZERO}
        zr = {ty: sorted((x["t0"], x["rail80"]) for x in rp if x["item"] == ZERO[ty]) for ty in ZERO}
        zs = {ty: sorted((x["t0"], x["sram_dec"]) for x in rp if x["item"] == ZERO[ty] and x["sram_dec"] is not None) for ty in ZERO}
        zn = {ty: sorted((x["t0"], x["noc_dec"]) for x in rp if x["item"] == ZERO[ty] and x["noc_dec"] is not None) for ty in ZERO}
        z54 = {ty: sorted((x["t0"], x["sram054_dec"]) for x in rp if x["item"] == ZERO[ty] and x["sram054_dec"] is not None) for ty in ZERO}
        for x in rp:
            ty = x["type"]
            x["D"] = x["p80"] - interp(z[ty], x["t0"])
            x["S"] = x["p80"] - x["idle80"] if x["idle_ok"] else None
            x["Drail"] = x["rail80"] - interp(zr[ty], x["t0"])
            x["Srail"] = x["rail80"] - x["rail_idle80"] if x["idle_ok"] and x["rail_idle80"] is not None else None
            x["Dsram"] = None if x["sram_dec"] is None else x["sram_dec"] - interp(zs[ty], x["t0"])
            x["Ssram"] = (x["sram_dec"] - x["sram_idle_dec"]) if x["idle_ok"] and None not in (x["sram_dec"], x["sram_idle_dec"]) else None
            x["Dnoc"] = None if x["noc_dec"] is None else x["noc_dec"] - interp(zn[ty], x["t0"])
            x["Snoc"] = (x["noc_dec"] - x["noc_idle_dec"]) if x["idle_ok"] and None not in (x["noc_dec"], x["noc_idle_dec"]) else None
            x["Dsram054"] = None if x["sram054_dec"] is None else x["sram054_dec"] - interp(z54[ty], x["t0"])
            x["Ssram054"] = ((x["sram054_dec"] - x["sram054_idle_dec"]) if x["idle_ok"] and None not in (x["sram054_dec"], x["sram054_idle_dec"])
                             else None)
            x["ddr_droop_mv"] = None if None in (x["mv_ddr"], x["mv_ddr_idle"]) else x["mv_ddr_idle"] - x["mv_ddr"]
            per.setdefault((p, x["item"]), []).append(x)
    # per (pass, item) means, then across passes
    keys = ["p_raw", "p_idle", "idle80", "p80", "S", "D", "Srail", "Drail", "Ssram", "Dsram", "Snoc", "Dnoc", "heat_w",
            "minion_idle_dec", "sram_idle_dec", "noc_idle_dec", "t_win", "t_idle", "start_c", "rate",
            "mv_minion", "mv_sram", "mv_noc", "mv_ddr", "mv_ddr_idle", "Dsram054", "Ssram054", "ddr_droop_mv"]
    pp = {}
    for (p, it), xs in per.items():
        pp[(p, it)] = {kk: (sum(v for v in [x[kk] for x in xs] if v is not None) /
                            max(1, len([1 for x in xs if x[kk] is not None])) if any(x[kk] is not None for x in xs) else None)
                       for kk in keys}
        pp[(p, it)]["n_runs"] = len(xs)
    # validation against the committed reduction's per-pass values
    val = {"board_D_max_abs_w": 0.0, "board_S_max_abs_w": 0.0, "Drail_max_abs_w": 0.0, "Srail_max_abs_w": 0.0, "rate_max_rel": 0.0,
           "n_compared": 0, "csv_p_raw_max_abs_w": 0.0, "csv_rail_dec_max_abs_w": 0.0, "csv_mv_max_abs": 0.0}
    for (p, it), v in pp.items():
        c = red.get("per_pass", {}).get(str(p), {}).get(it)
        if not c:
            continue
        val["n_compared"] += 1
        for mine, theirs, kk in (("D", "D", "board_D_max_abs_w"), ("S", "S", "board_S_max_abs_w"), ("Drail", "Drail", "Drail_max_abs_w"),
                                 ("Srail", "Srail", "Srail_max_abs_w")):
            if v[mine] is not None and c.get(theirs) is not None:
                val[kk] = max(val[kk], abs(v[mine] - c[theirs]))
        if v["rate"] and c.get("rate"):
            val["rate_max_rel"] = max(val["rate_max_rel"], abs(v["rate"] / c["rate"] - 1))
    for xs in per.values():
        for x in xs:
            for mine, theirs, kk in (("p_raw", "p_raw", "csv_p_raw_max_abs_w"), ("minion_dec", "rail_dec", "csv_rail_dec_max_abs_w"),
                                     ("mv_minion", "mv", "csv_mv_max_abs")):
                if x[mine] is not None and x["csv"][theirs] is not None:
                    val[kk] = max(val[kk], abs(x[mine] - x["csv"][theirs]))
    items = {}
    for it in ITEMS[label]:
        ps = [p for p in passes if (p, it) in pp]
        items[it] = {kk: stat([pp[(p, it)][kk] for p in ps]) for kk in keys}
        items[it]["passes"] = ps
        items[it]["type"] = it.split(".")[0] if "." in it else "fp32"
        items[it]["committed"] = {kk: red["items"][it][kk] for kk in ("D", "S", "Drail", "Srail", "rate", "p80", "idle80", "dT_win")
                                  if it in red["items"] and kk in red["items"][it]}
    return {"label": label, "card": card, "reduction": red_path, "k_w_per_c": k, "c_rb": C_RB, "passes": passes,
            "dips_removed": dips, "items": items, "pp": {f"{p}|{it}": v for (p, it), v in pp.items()}, "validation": val}


def tensor_ledger(sess, it, coef, law):
    """The partition of one TensorFMA op's board energy (the window's raw reading) into lines, and the cross-cuts."""
    m = {kk: (sess["items"][it][kk]["mean"]) for kk in sess["items"][it] if isinstance(sess["items"][it][kk], dict) and "mean" in sess["items"][it][kk]}
    ci = {kk: (sess["items"][it][kk]["ci95"]) for kk in sess["items"][it] if isinstance(sess["items"][it][kk], dict) and "ci95" in sess["items"][it][kk]}
    ty = sess["items"][it]["type"]
    rate = m["rate"]
    macs = MACS[ty]
    vm, vs, vn = m["mv_minion"] / 1000.0, m["mv_sram"] / 1000.0, m["mv_noc"] / 1000.0
    rest_board = m["p_idle"]                               # measured: the 1 s idle bracket before each run
    rest_rails = {"minion": m["minion_idle_dec"], "sram": m["sram_idle_dec"], "noc": m["noc_idle_dec"]}
    rest_off = rest_board - sum(rest_rails.values())
    S, D = m["S"], m["D"]
    awake = {"minion": m["Srail"] - m["Drail"], "sram": m["Ssram"] - m["Dsram"], "noc": m["Snoc"] - m["Dnoc"]}
    data = {"minion": m["Drail"], "sram": m["Dsram"], "noc": m["Dnoc"]}
    awake_off = (S - D) - sum(awake.values())
    data_off = D - sum(data.values())
    # the window's own heating: the board reads p_raw = p_idle + S + k (t_win - t_idle), exactly, per run
    heat = m["heat_w"]
    total = m["p_raw"]
    lines = []

    def add(key, name, w, volt, label, made_of, partition=True, w_ci=None):
        e = w / rate if w is not None else None
        lines.append({"key": key, "line": name, "W": w, "W_ci95": w_ci, "J_per_op": e,
                      "pJ_per_op": None if e is None else e * 1e12, "pJ_per_mac": None if e is None else e * 1e12 / macs,
                      "share_of_board": None if w is None else w / total, "volts": volt,
                      "charge_C_per_op": None if e is None or volt is None else e / volt,
                      "electrons_per_op": None if e is None or volt is None else e / volt / E,
                      "electrons_per_mac": None if e is None or volt is None else e / volt / E / macs,
                      "label": label, "made_of": made_of, "partition": partition})

    add("outside", "outside the card's measured envelope: the host's power supply and fans", None, None, "not measured",
        "the host's supply converting wall power to 12 V and the host's fans, which cool the card; no figure", partition=False)
    add("card_fan", "the card's own fan", 0.0, V_IN, "assumed none (recorded on aifoundry2 only)",
        "no fan on the card's rails: aifoundry2's card is passive (on-site record of 9 Oct 2026); the V3 card's public "
        "documentation lists no fan; its MAX6660 fan regulator is read only by a PMIC test path", partition=False)
    add("rest_offrail", "at rest, off the three metered rails (DRAM and its interface, PCIe and I/O, the IO shire, PLLs, "
        "always-on blocks, the regulators' own draw)", rest_off, V_IN, "measured (board less the three rails, at rest)",
        "the card at rest less what its minion, SRAM and NoC regulators deliver; not split further by any committed data")
    for rail, v in (("minion", vm), ("sram", vs), ("noc", vn)):
        add(f"rest_{rail}", f"at rest, the {rail} rail (the die's leakage and clocks at rest)", rest_rails[rail], v,
            "measured (that card's own regulator telemetry)",
            {"minion": "the 1,024 minions' leakage and their idle clock and always-on switching",
             "sram": "the shires' SRAM banks (L2, L3, scratchpad) at rest: mostly leakage",
             "noc": "the mesh at rest: its clock and leakage"}[rail])
    for rail, v in (("minion", vm), ("sram", vs), ("noc", vn)):
        add(f"awake_{rail}", f"awake on zeros, the {rail} rail (the zeros anchor over rest)", awake[rail], v,
            "measured (minion: the registered reduction; SRAM and NoC: post hoc, raw)",
            {"minion": "issuing TensorFMA, the tensor state machines, the scratchpad reads of zero words, the clocks of the "
                       "awake core; the lanes' clock is withheld on a zero operand word",
             "sram": "the SRAM rail's change with an awake TensorFMA on zeros (no L2 traffic in steady state)",
             "noc": "the mesh's change (no mesh traffic in steady state)"}[rail])
    add("awake_offrail", "awake on zeros, off-rail (the regulators' delivery loss on the awake rails, and off-rail logic in step)",
        awake_off, V_IN, "measured as a remainder (board less rails)", "the delivery loss on the awake watts, and whatever else is unmetered")
    for rail, v in (("minion", vm), ("sram", vs), ("noc", vn)):
        add(f"data_{rail}", f"the data-dependent part (over the zeros anchor), the {rail} rail", data[rail], v,
            "measured (minion: the registered reduction; SRAM and NoC: post hoc, raw)",
            {"minion": "the operand-dependent switching of the lanes: the multiplier and adder trees, the accumulator, the "
                       "operand and result buses, the lane clocks that run once a word is nonzero, the scratchpad's data "
                       "bits; inside it, the per-electron ledger is pending (Q144, the NDA tier)",
             "sram": "any data dependence on the SRAM rail (none expected for a resident tile)",
             "noc": "any data dependence on the mesh (none expected)"}[rail])
    add("data_offrail", "the data-dependent part, off-rail (the delivery loss on the data watts, and off-rail logic in step)",
        data_off, V_IN, "measured as a remainder (board less rails)", "mostly the regulators' delivery loss on the extra minion-rail watts")
    add("heat", "the window's own heating: the leakage the die adds as it warms during the 2 s window", heat, V_IN,
        f"modelled (the footing slope k = {sess['k_w_per_c']:.4f} W/C times the window's measured rise)",
        "leakage that grows with the run's own heating, t_win - t_idle; the registered reduction takes it off; E71's dedicated "
        "slope would put it about 1.85x higher on aifoundry3")
    part = [l for l in lines if l["partition"] and l["W"] is not None]
    s_sum = sum(l["W"] for l in part)
    # the cross-cuts (not added): the regulators' conversion loss by section 4.3's fit, the leakage at rest by the card's law,
    # the clock and always-on switching at rest as the rest of the rails at rest, and the per-electron line
    rails_above = {r: awake[r] + data[r] for r in awake}
    reg = coef["minion"] * rails_above["minion"] + coef["sram"] * rails_above["sram"] + coef["noc"] * rails_above["noc"]
    reg_data = coef["minion"] * data["minion"] + coef["sram"] * data["sram"] + coef["noc"] * data["noc"]
    p_fix, a80 = law
    Tl = m["t_idle"]
    leak = a80 * math.exp((Tl - 80.0) / 36.0)
    leak_lo, leak_hi = None, None
    cross = []

    def addx(key, name, w, volt, label, made_of):
        e = w / rate if w is not None else None
        cross.append({"key": key, "line": name, "W": w, "pJ_per_op": None if e is None else e * 1e12,
                      "pJ_per_mac": None if e is None else e * 1e12 / macs, "share_of_board": None if w is None else w / total,
                      "volts": volt, "electrons_per_op": None if e is None or volt is None else e / volt / E,
                      "label": label, "made_of": made_of, "partition": False})

    addx("regulators", "the regulators' conversion loss on the op's watts above rest (cross-cut of the two off-rail lines above rest)",
         reg, V_IN, "modelled (the energy manual's per-card delivery-loss fit, section 4.3; each 1% of rail-meter scale moves it about 1.2 points)",
         f"{coef['minion']:.3f} x minion + {coef['sram']:.3f} x SRAM + {coef['noc']:.3f} x NoC rail watts above rest")
    addx("regulators_data", "of which on the data-dependent watts", reg_data, V_IN, "modelled (section 4.3's fit)", "the same coefficients on the data part")
    addx("offrail_residual", "the off-rail remainder above rest less the fit's delivery loss (the books' named gap)",
         (awake_off + data_off) - reg, V_IN, "measured less modelled", "the fit's residual: off-rail logic, the window's off-rail heating, the meter's scale")
    addx("leak_rest", f"the die's leakage at rest, at the run's idle temperature ({Tl:.2f} C), by the card's idle law", leak, None,
         "modelled (the lab's own fitted law, " + IDLE_LAW_SRC + ")",
         f"P_idle(T) = {p_fix} W + {a80} W e^((T-80)/36); the law's leakage part at T; the idle data do not pin the split (e-folding 30-45 C)")
    slope_law = a80 / 36.0 * math.exp((Tl - 80.0) / 36.0)
    addx("leak_rest_range", "the same leakage if the e-folding were 30 or 45 C at the law's slope at T (the idle data do not pin it)",
         None, None, "modelled (range)", f"slope {slope_law:.4f} W/C at {Tl:.2f} C x 30..45 C = {30 * slope_law:.2f}..{45 * slope_law:.2f} W")
    cross[-1]["W_range"] = [30 * slope_law, 45 * slope_law]
    cross[-1]["slope_law_w_per_c"] = slope_law
    addx("clock_rest", "the clock and always-on switching at rest, as the at-rest board less the law's leakage", rest_board - leak, None,
         "measured less modelled", "every block's clocks, PLLs, I/O and DRAM refresh at rest, and the regulators' fixed draw")
    i_in = total / V_IN
    addx("sense_resistor", "of the off-rail at rest and above: the board meter's own 1 mOhm sense resistor, I^2 R at the input current",
         i_in * i_in * 0.001, V_IN, "modelled (public schematic: a 0.001 Ohm kelvin resistor on the 12 V input, et-man ET-PCIe-Dev-Card-V3)",
         f"{i_in:.2f} A at a nominal 12 V")
    addx("per_electron", "inside the switching rails: the per-electron ledger, pending (Q144, the NDA tier)", None, None,
         "pending", "transistor gate charge, wires, internal and short-circuit energy, glitches, the lane's clock tree: no number here "
         "beyond the rails' measured totals above")
    return {"item": it, "type": ty, "card": sess["card"], "session": sess["label"], "rate_ops_per_s": rate,
            "rate_nominal_ops_per_s": CLOCK_HZ * MINIONS / CPO[ty], "macs_per_op": macs, "board_W": total,
            "board_pJ_per_op": total / rate * 1e12, "board_pJ_per_mac": total / rate * 1e12 / macs,
            "board_ci95_W": ci.get("p_raw"), "above_rest_W": S, "data_W": D, "data_ci95_W": ci.get("D"),
            "sum_of_partition_W": s_sum, "books_gap_W": total - s_sum, "volts": {"minion": vm, "sram": vs, "noc": vn, "input_nominal": V_IN},
            "t_idle_c": Tl, "t_win_c": m["t_win"], "start_c": m["start_c"], "lines": lines, "cross_cuts": cross,
            "electrons_board_per_op_at_12V": total / rate / V_IN / E, "ddr_droop_mv": m.get("ddr_droop_mv"),
            "ddr_droop_mv_ci95": ci.get("ddr_droop_mv"),
            "sram_tau054": {"S": m.get("Ssram054"), "D": m.get("Dsram054")},
            "ci95_W": {kk: ci.get(kk) for kk in ("p_raw", "p_idle", "S", "D", "Srail", "Drail", "Ssram", "Dsram", "Snoc", "Dnoc",
                                                  "minion_idle_dec", "sram_idle_dec", "noc_idle_dec", "heat_w")}}


def pairs_tensor(sessions):
    out = []
    for lab, a, b, what in PAIRS:
        s = sessions[lab]
        ps = [p for p in s["passes"] if f"{p}|{a}" in s["pp"] and f"{p}|{b}" in s["pp"]]
        row = {"session": lab, "card": s["card"], "a": a, "b": b, "what": what, "passes": ps}
        ty = a.split(".")[0] if "." in a else "fp32"
        rate = statistics.mean(s["pp"][f"{p}|{a}"]["rate"] for p in ps)
        for kk in ("D", "Drail", "Dsram", "Dnoc", "Dsram054"):
            row[kk] = stat([s["pp"][f"{p}|{a}"][kk] - s["pp"][f"{p}|{b}"][kk] for p in ps])
        row["Doff"] = stat([(s["pp"][f"{p}|{a}"]["D"] - s["pp"][f"{p}|{a}"]["Drail"] - s["pp"][f"{p}|{a}"]["Dsram"] - s["pp"][f"{p}|{a}"]["Dnoc"])
                            - (s["pp"][f"{p}|{b}"]["D"] - s["pp"][f"{p}|{b}"]["Drail"] - s["pp"][f"{p}|{b}"]["Dsram"] - s["pp"][f"{p}|{b}"]["Dnoc"])
                            for p in ps])
        row["pJ_per_op_of_1W"] = 1e12 / rate
        row["macs_per_op"] = MACS[ty]
        out.append(row)
    return out


# ---------------------------------------------------------------------------------------------------- (B) the vector unit
VCFG = ["fadd.pi/zeros/h2", "fadd.pi/const/h2", "fadd.pi/random/h2", "fadd.ps/zeros/h2", "fadd.ps/const/h2", "fadd.ps/random/h2",
        "fmadd.ps/zeros/h2", "fmadd.ps/const/h2", "fmadd.ps/random/h2", "fmadd.ps/random/h1", "nop/zeros/h2", "fence/zeros/h2"]
V_MINION_CAT = {"aifoundry2": 0.518, "aifoundry3": 0.523, "aifoundry1-c1": 0.499}   # 01-at-rest.md, 'The three cards'


def vector_part(repo, coef, volts, law):
    cat = json.load(open(os.path.join(repo, DEM, "catalogue.json")))
    res = {"per_card": {}, "pairs": [], "rates": {}}
    for card in ("aifoundry3", "aifoundry1-c1", "aifoundry2"):
        bs = [b for b in cat["bursts"][card] if b["cfg"] in VCFG]
        out = {}
        for cfg in VCFG:
            rows = sorted((b for b in bs if b["cfg"] == cfg), key=lambda b: b["pass"])
            if not rows:
                continue
            perpass = []
            for b in rows:
                rate = b["ops"] / b["wall_s"]                       # the catalogue's pj_per_op convention (over x wall / ops)
                ro = b["rails_over"]
                off_over = b["over_idle_w"] - ro["minion_w"] - ro["sram_w"] - ro["noc_w"]
                rest_rails = b["minion_idle_w"] + b["sram_idle_w"] + b["noc_idle_w"]
                perpass.append({"pass": b["pass"], "rate": rate, "rate_device": b["ops_per_s"], "ipc_hart": b["ops_per_cycle_per_hart"],
                                "p_busy": b["p_busy_w"], "p_idle": b["p_idle_w"], "over": b["over_idle_w"], "leak_corr": b["leak_correction_w"],
                                "minion_over": ro["minion_w"], "sram_over": ro["sram_w"], "noc_over": ro["noc_w"], "off_over": off_over,
                                "minion_idle": b["minion_idle_w"], "sram_idle": b["sram_idle_w"], "noc_idle": b["noc_idle_w"],
                                "off_idle": b["p_idle_w"] - rest_rails, "die_busy": b["die_c_busy"], "die_idle": b["die_c_idle"],
                                "pj_per_op": b["pj_per_op"]})
            agg = {kk: stat([x[kk] for x in perpass]) for kk in perpass[0] if kk != "pass"}
            out[cfg] = {"passes": [x["pass"] for x in perpass], "perpass": perpass, "agg": agg}
        res["per_card"][card] = out
        # paired differences per pass: const - zeros, random - zeros, random - const
        for op in ("fadd.pi", "fadd.ps", "fmadd.ps"):
            for a, b in (("const", "zeros"), ("random", "zeros")):
                A, Bz = out.get(f"{op}/{a}/h2"), out.get(f"{op}/{b}/h2")
                if not A or not Bz:
                    continue
                pa = {x["pass"]: x for x in A["perpass"]}
                pb = {x["pass"]: x for x in Bz["perpass"]}
                ps = sorted(set(pa) & set(pb))
                row = {"card": card, "op": op, "a": a, "b": b, "passes": ps}
                for kk in ("over", "minion_over", "sram_over", "noc_over", "off_over", "leak_corr"):
                    row[kk + "_pJ"] = stat([(pa[p][kk] / pa[p]["rate"] - pb[p][kk] / pb[p]["rate"]) * 1e12 for p in ps])
                res["pairs"].append(row)
    # the catalogue's issue rates across every two-hart instruction (the rate ceiling)
    for card in ("aifoundry3", "aifoundry1-c1", "aifoundry2"):
        s = cat["cards"][card]["summary"]
        ipcs = sorted((cfg, v["ops_per_cycle_per_hart"]["mean"]) for cfg, v in s.items()
                      if v.get("unit") == "instruction" and cfg.endswith("/h2") and v.get("ops_per_cycle_per_hart", {}).get("mean"))
        vals = [v for _, v in ipcs]
        res["rates"][card] = {"n_patterns_h2": len(vals), "n_in_0.30_0.45": sum(1 for v in vals if 0.30 <= v <= 0.45),
                              "max": max(vals), "median": statistics.median(vals),
                              "nop_zeros_h2": s.get("nop/zeros/h2", {}).get("ops_per_cycle_per_hart", {}).get("mean"),
                              "fmadd_random_h2": s.get("fmadd.ps/random/h2", {}).get("ops_per_cycle_per_hart", {}).get("mean"),
                              "fmadd_random_h1": s.get("fmadd.ps/random/h1", {}).get("ops_per_cycle_per_hart", {}).get("mean"),
                              "top5": sorted(ipcs, key=lambda kv: -kv[1])[:5]}
    res["combined"] = {k: cat["combined"][k] for k in ("fadd.pi/zeros/h2", "fadd.pi/const/h2", "fadd.pi/random/h2", "fadd.ps/zeros/h2",
                                                       "fadd.ps/const/h2", "fadd.ps/random/h2", "fmadd.ps/zeros/h2", "fmadd.ps/const/h2",
                                                       "fmadd.ps/random/h2") if k in cat["combined"]}
    return res


def vector_ledger(card, cfg, agg, coef, volts, law):
    m = {kk: v["mean"] for kk, v in agg.items()}
    rate = m["rate"]
    total = m["p_busy"]
    vm = V_MINION_CAT[card]
    vs, vn = volts.get(card, {}).get("sram"), volts.get(card, {}).get("noc")
    lines = []

    def add(key, name, w, volt, label, made_of, partition=True):
        e = None if w is None else w / rate
        lines.append({"key": key, "line": name, "W": w, "pJ_per_op": None if e is None else e * 1e12,
                      "pJ_per_lane": None if e is None else e * 1e12 / 8, "share_of_board": None if w is None else w / total,
                      "volts": volt, "electrons_per_op": None if e is None or volt is None else e / volt / E,
                      "label": label, "made_of": made_of, "partition": partition})

    add("outside", "outside the card's measured envelope: the host's power supply and fans", None, None, "not measured", "no figure", False)
    add("card_fan", "the card's own fan", 0.0, V_IN, "assumed none (recorded on aifoundry2 only)", "a passive card", False)
    add("rest_offrail", "at rest, off the three metered rails", m["off_idle"], V_IN, "measured (board less rails, at rest)",
        "DRAM and its interface, PCIe and I/O, the IO shire, PLLs, always-on blocks, the regulators' own draw")
    add("rest_minion", "at rest, the minion rail", m["minion_idle"], vm, "measured (that card's own regulator telemetry)", "leakage, idle clocks")
    add("rest_sram", "at rest, the SRAM rail", m["sram_idle"], vs, "measured", "SRAM banks at rest")
    add("rest_noc", "at rest, the NoC rail", m["noc_idle"], vn, "measured", "the mesh at rest")
    add("heat", "the burst's own heating (the catalogue's leakage correction, 21 Sep law)", m["leak_corr"], V_IN,
        "modelled (23.257/36 e^((T-80)/36) W/C times the burst's measured rise)", "leakage that grows as the burst heats the die")
    add("above_minion", "above rest, the minion rail", m["minion_over"], vm, "measured (last 0.6 s, divided by 0.94 for the rail's filter)",
        "issue, register-file reads and writes, the lanes' adders and multipliers, the write-back, the core's clocks")
    add("above_sram", "above rest, the SRAM rail", m["sram_over"], vs, "measured (raw)", "none expected: register operands only")
    add("above_noc", "above rest, the NoC rail", m["noc_over"], vn, "measured (raw)", "none expected: no memory traffic")
    add("above_offrail", "above rest, off-rail (the delivery loss, and off-rail logic in step)", m["off_over"], V_IN,
        "measured as a remainder (board over rest less the three rails)", "mostly the regulators' delivery loss")
    part = [l for l in lines if l["partition"] and l["W"] is not None]
    s_sum = sum(l["W"] for l in part)
    reg = coef["minion"] * m["minion_over"] + coef["sram"] * m["sram_over"] + coef["noc"] * m["noc_over"]
    p_fix, a80 = law
    leak = a80 * math.exp((m["die_idle"] - 80.0) / 36.0)
    cross = [
        {"key": "regulators", "line": "the regulators' conversion loss above rest (cross-cut)", "W": reg, "pJ_per_op": reg / rate * 1e12,
         "share_of_board": reg / total, "label": "modelled (section 4.3's fit)", "partition": False},
        {"key": "offrail_residual", "line": "the off-rail remainder above rest less the fit (the named gap)", "W": m["off_over"] - reg,
         "pJ_per_op": (m["off_over"] - reg) / rate * 1e12, "share_of_board": (m["off_over"] - reg) / total, "label": "measured less modelled",
         "partition": False},
        {"key": "leak_rest", "line": f"the die's leakage at rest, at {m['die_idle']:.1f} C, by the card's idle law", "W": leak,
         "pJ_per_op": leak / rate * 1e12, "share_of_board": leak / total, "label": "modelled (" + IDLE_LAW_SRC + ")", "partition": False},
        {"key": "per_electron", "line": "inside the switching rails: the per-electron ledger, pending (Q144, the NDA tier)", "W": None,
         "label": "pending", "partition": False},
    ]
    return {"card": card, "cfg": cfg, "rate_ops_per_s_wall": rate, "rate_ops_per_s_device": m["rate_device"],
            "issue_per_hart_per_cycle": m["ipc_hart"], "board_W": total, "board_pJ_per_op": total / rate * 1e12,
            "over_pJ_per_op": m["over"] / rate * 1e12, "catalogue_pj_per_op": m["pj_per_op"], "sum_of_partition_W": s_sum,
            "books_gap_W": total - s_sum, "die_c_busy": m["die_busy"], "die_c_idle": m["die_idle"], "lines": lines, "cross_cuts": cross,
            "volts": {"minion": vm, "sram": vs, "noc": vn}}


# ---------------------------------------------------------------------------------------------------- (D) the virus
def popcount(x):
    return bin(x).count("1")


def parse_virus(path):
    src = open(path).read()
    setups = {}
    for name in ("vpu_pv_setup0", "vpu_pv_setup1"):
        i = src.index("void " + name + "()")
        j = src.index("}", src.index("vpu_pv_load_f31", i))
        body = src[i:j]
        arrs = {}
        for m in re.finditer(r"(fp\d|gold_ref_\d)\[8\]\s*=\s*\{([^}]*)\}", body):
            arrs[m.group(1)] = m.group(2)
        setups[name] = arrs
    return setups


def words_hex(s):
    return [int(w.strip(), 16) for w in s.split(",")]


def words_float(s):
    return [struct.unpack("<I", struct.pack("<f", float(w.strip())))[0] for w in s.split(",")]


def virus_part(repo):
    ep = parse_virus(os.path.join(repo, VIRUS))
    out = {"source": VIRUS, "sha256": sha(os.path.join(repo, VIRUS)), "harts": {}}
    # setup0 runs on thread 0, setup1 on thread 1 of every minion; f1,f2,f3 <- fp0,fp1,fp2 and f28,f29,f30 <- fp3,fp4,fp5;
    # the loop alternates fmadd.ps f(even), f1, f2, f3 and fmadd.ps f(odd), f28, f29, f30 on each hart
    trip = {}
    for name, hart in (("vpu_pv_setup0", 0), ("vpu_pv_setup1", 1)):
        a = ep[name]
        t1 = [words_hex(a["fp0"]), words_hex(a["fp1"]), words_hex(a["fp2"])]
        t2 = [words_hex(a["fp3"]), words_hex(a["fp4"]), words_hex(a["fp5"])]
        trip[hart] = (t1, t2)
        per_port = [sum(popcount(x ^ y) for x, y in zip(t1[k], t2[k])) for k in range(3)]
        exps = sorted({(w >> 23) & 0xFF for tr in (t1, t2) for port in tr for w in port})
        out["harts"][hart] = {"setup": name, "flips_per_instruction_alternating": sum(per_port), "per_port": per_port,
                              "exponent_bytes": [hex(e) for e in exps],
                              "popcount_mean_per_word": statistics.mean(popcount(w) for tr in (t1, t2) for port in tr for w in port),
                              "operand_words": {"f1_f2_f3": [[f"0x{w:08x}" for w in port] for port in t1],
                                                "f28_f29_f30": [[f"0x{w:08x}" for w in port] for port in t2]}}
    # if the two harts' instructions interleave one for one at the unit's operand ports: h0 A, h1 A, h0 B, h1 B, ...
    seq = [trip[0][0], trip[1][0], trip[0][1], trip[1][1]]
    inter = [sum(popcount(x ^ y) for k in range(3) for x, y in zip(seq[i][k], seq[(i + 1) % 4][k])) for i in range(4)]
    out["interleaved_one_for_one"] = {"flips_per_instruction": inter, "mean": statistics.mean(inter)}
    # core-et's own copy of the loop (decimal literals for the operands)
    try:
        cs = open(os.path.join(repo, CORE_PS)).read()
        same = True
        for name in ("vpu_pv_setup0", "vpu_pv_setup1"):
            i = cs.index("void " + name + "()")
            j = cs.index("}", cs.index("vpu_pv_load_f31", i))
            body = cs[i:j]
            for fp in ("fp0", "fp1", "fp2", "fp3", "fp4", "fp5"):
                m = re.search(fp + r"\[8\]\s*=\s*\{([^}]*)\}", body)
                if words_float(m.group(1)) != words_hex(ep[name][fp]):
                    same = False
        out["core_et_ps"] = {"source": CORE_PS, "sha256": sha(os.path.join(repo, CORE_PS)), "operands_equal_et_platform_words": same}
    except (OSError, ValueError, AttributeError) as ex:
        out["core_et_ps"] = {"error": repr(ex)}
    # the lab's random rotation (workloads/enercat VMABLOCK): every operand port sees a fresh random vector each instruction;
    # the words are floats uniform in [0.5, 2): sign 0, exponent 0x7E or 0x7F (P 1/3, 2/3), 23 uniform mantissa bits
    p_exp_diff = 2 * (1 / 3) * (2 / 3)
    per_word = 23 * 0.5 + p_exp_diff * 1
    out["lab_random_rotation"] = {"expected_flips_per_word": per_word, "expected_flips_per_instruction": 3 * 8 * per_word,
                                  "model": "independent words uniform in [0.5, 2) (enercat host main.cpp sources(): std::uniform_real_distribution<float>(0.5f, 2.0f)); "
                                           "the eight-instruction block rotates f0..f7 so no port reads the same register twice running (kernel/enercat.c VMABLOCK)"}
    # the constant column: every source word 1.0f, so no operand bit changes
    out["lab_constant"] = {"flips_per_instruction": 0}
    return out


def extras(repo, vec):
    """The minion rail's share of pool 8's switching, the vector pairs pooled over cards, card ratios after V^2, issue rates."""
    out = {"rail_share": {}, "vector_pooled": [], "vector_card_v2": {}, "issue_random_h2": {}}
    for lab, path in (("E171", D171 + "/e171.json"), ("E172", D172 + "/e172.json")):
        it = json.load(open(os.path.join(repo, path)))["items"]
        rd = sorted(v["Drail"]["mean"] / v["D"]["mean"] for v in it.values() if v.get("D", {}).get("mean") and v["D"]["mean"] > 2.0
                    and v.get("Drail", {}).get("mean") is not None)
        rs = sorted(v["Srail"]["mean"] / v["S"]["mean"] for v in it.values() if v.get("S", {}).get("mean") and v["D"]["mean"] and v["D"]["mean"] > 2.0
                    and v.get("Srail", {}).get("mean") is not None)
        out["rail_share"][lab] = {"n_items_D_over_2W": len(rd), "Drail_over_D": {"min": rd[0], "median": statistics.median(rd), "max": rd[-1]},
                                  "Srail_over_S": {"min": rs[0], "median": statistics.median(rs), "max": rs[-1]}}
    for op in ("fadd.pi", "fadd.ps", "fmadd.ps"):
        for a, b in (("const", "zeros"), ("random", "zeros")):
            rows = [p for p in vec["pairs"] if p["op"] == op and p["a"] == a and p["b"] == b]
            row = {"op": op, "a": a, "b": b, "cards": [p["card"] for p in rows]}
            for kk in ("over_pJ", "minion_over_pJ", "sram_over_pJ", "noc_over_pJ", "off_over_pJ"):
                ms = [p[kk]["mean"] for p in rows]
                sds = [p[kk]["sd"] for p in rows]
                ns = [p[kk]["n"] for p in rows]
                n = sum(ns)
                mean = sum(m_ * n_ for m_, n_ in zip(ms, ns)) / n
                df = sum(n_ - 1 for n_ in ns)
                sp = math.sqrt(sum((n_ - 1) * s_ * s_ for s_, n_ in zip(sds, ns)) / df)
                # card-blocked: each card's own mean removed, so the pooled within-card sd and its df
                se = sp / math.sqrt(n)
                row[kk] = {"mean": mean, "pooled_sd": sp, "n": n, "df": df, "ci95": se * T95.get(df, 1.96),
                           "card_means": ms}
            out["vector_pooled"].append(row)
    pc = vec["per_card"]
    for cfg in ("fmadd.ps/random/h2", "fadd.ps/random/h2", "fadd.pi/random/h2"):
        e = {c: pc[c][cfg]["agg"]["minion_over"]["mean"] / pc[c][cfg]["agg"]["rate"]["mean"] for c in pc if cfg in pc[c]}
        b = {c: pc[c][cfg]["agg"]["over"]["mean"] / pc[c][cfg]["agg"]["rate"]["mean"] for c in pc if cfg in pc[c]}
        v = V_MINION_CAT
        out["vector_card_v2"][cfg] = {
            "minion_pJ": {c: x * 1e12 for c, x in e.items()}, "board_over_pJ": {c: x * 1e12 for c, x in b.items()},
            "card1_over_a3_minion_raw": e["aifoundry1-c1"] / e["aifoundry3"],
            "card1_over_a3_minion_after_V2": (e["aifoundry1-c1"] / v["aifoundry1-c1"] ** 2) / (e["aifoundry3"] / v["aifoundry3"] ** 2),
            "a2_over_a3_minion_after_V2": (e["aifoundry2"] / v["aifoundry2"] ** 2) / (e["aifoundry3"] / v["aifoundry3"] ** 2),
            "board_over_minion": {c: b[c] / e[c] for c in e}}
    cat = json.load(open(os.path.join(repo, DEM, "catalogue.json")))
    for card in ("aifoundry3", "aifoundry1-c1", "aifoundry2"):
        s = cat["cards"][card]["summary"]
        vals = sorted((v["ops_per_cycle_per_hart"]["mean"], cfg) for cfg, v in s.items()
                      if cfg.endswith("/random/h2") and v.get("unit") == "instruction" and v.get("ops_per_cycle_per_hart", {}).get("mean"))
        x = [a_ for a_, _ in vals]
        out["issue_random_h2"][card] = {"n": len(x), "n_0.30_0.45": sum(1 for a_ in x if 0.30 <= a_ <= 0.45), "max": vals[-1],
                                        "median": statistics.median(x), "n_above_fmadd": sum(1 for a_ in x if a_ > s["fmadd.ps/random/h2"]["ops_per_cycle_per_hart"]["mean"])}
    return out


# ---------------------------------------------------------------------------------------------------- main
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", default=".")
    ap.add_argument("--out", required=True)
    ap.add_argument("--txt", required=True)
    ap.add_argument("--md", required=True)
    a = ap.parse_args()
    repo = a.repo
    foot = json.load(open(os.path.join(repo, DQ139U, "footing.json")))
    k_footing = {"a3": foot["slopes"]["a3"]["k_w_per_c"], "c1": foot["slopes"]["c1"]["k_w_per_c"]}
    fit = json.load(open(os.path.join(repo, DEM, "unmetered_fit.json")))
    coef = {c: fit[c]["coef"] for c in ("aifoundry2", "aifoundry3", "aifoundry1-c1")}
    e71 = json.load(open(os.path.join(repo, DE71, "slopes.json")))
    e71_5862 = statistics.median(p["fits"]["58-62"]["slope_w_per_c"] for p in e71["passes"].values() if p["fits"].get("58-62", {}).get("ok"))
    sessions = {}
    for lab, card, ddir, red, raw, sk in SESSIONS:
        sessions[lab] = tensor_session(repo, lab, card, ddir, red, raw, sk, k_footing)
    # each card's SRAM and NoC voltages, from its own pool-8 telemetry (median over the kept runs' windows)
    volts = {}
    for lab in ("E171", "E172"):
        s = sessions[lab]
        volts[s["card"]] = {"sram": statistics.median(v["mv_sram"] for v in s["pp"].values()) / 1000.0,
                            "noc": statistics.median(v["mv_noc"] for v in s["pp"].values()) / 1000.0,
                            "minion": statistics.median(v["mv_minion"] for v in s["pp"].values()) / 1000.0}
    volts["aifoundry2"] = {"sram": 0.700, "noc": 0.485, "minion": 0.518, "note": "regulator set points (reg_mv) and the energy manual's 518 mV; no aifoundry2 pool-8 telemetry is read here"}
    tensor = {}
    for lab in ("E171", "E172", "E78", "E82"):
        s = sessions[lab]
        tensor[lab] = {it: tensor_ledger(s, it, coef[s["card"]], IDLE_LAW[s["card"]]) for it in ITEMS[lab]}
    pairs = pairs_tensor(sessions)
    vec = vector_part(repo, coef, volts, IDLE_LAW)
    vled = {card: {cfg: vector_ledger(card, cfg, d["agg"], coef[card], volts, IDLE_LAW[card]) for cfg, d in vec["per_card"][card].items()}
            for card in vec["per_card"]}
    virus = virus_part(repo)
    # card comparison after each card's own V^2 (aifoundry3 against card 1)
    v2 = {}
    for it in ITEMS["E171"]:
        a3, c1 = tensor["E171"][it], tensor["E172"][it]
        r = {}
        for key in ("data_minion", "data_offrail"):
            la = next(l for l in a3["lines"] if l["key"] == key)
            lc = next(l for l in c1["lines"] if l["key"] == key)
            if la["W"] and lc["W"] and abs(la["W"]) > 0.3:
                ratio = (lc["pJ_per_op"] / lc["volts"] ** 2) / (la["pJ_per_op"] / la["volts"] ** 2) if lc["volts"] != V_IN else lc["pJ_per_op"] / la["pJ_per_op"]
                r[key] = {"card1_over_a3_raw": lc["pJ_per_op"] / la["pJ_per_op"], "card1_over_a3_after_V2": ratio}
        r["board_data"] = {"card1_over_a3_raw": (c1["data_W"] / c1["rate_ops_per_s"]) / (a3["data_W"] / a3["rate_ops_per_s"]) if a3["data_W"] and abs(a3["data_W"]) > 0.3 else None,
                           "card1_over_a3_after_minion_V2": ((c1["data_W"] / c1["rate_ops_per_s"]) / c1["volts"]["minion"] ** 2) /
                                                            ((a3["data_W"] / a3["rate_ops_per_s"]) / a3["volts"]["minion"] ** 2) if a3["data_W"] and abs(a3["data_W"]) > 0.3 else None}
        v2[it] = r
    res = {"what": "Q145(a), post hoc: the anatomy's measured top lines (CONTEXT section 43; MAP section 4 steps 6 and 5)",
           "posthoc": True, "e_charge_C": E, "v_in_nominal": V_IN, "k_footing_w_per_c": k_footing,
           "e71_slope_58_62_w_per_c_median": e71_5862, "idle_law": IDLE_LAW, "delivery_fit_coef": coef, "volts": volts,
           "sessions": {lab: {kk: v for kk, v in s.items() if kk != "pp"} for lab, s in sessions.items()},
           "tensor_ledgers": tensor, "tensor_pairs": pairs, "card_v2": v2,
           "vector": {"pairs": vec["pairs"], "rates": vec["rates"], "combined": vec["combined"],
                      "per_card": {c: {cfg: d["agg"] for cfg, d in v.items()} for c, v in vec["per_card"].items()}},
           "vector_ledgers": vled, "virus": virus, "extras": extras(repo, vec),
           "inputs_sha256": {p: sha(os.path.join(repo, p)) for p in sorted({
               D171 + "/e171.json", D171 + "/runs.csv", D172 + "/e172.json", D172 + "/runs.csv", D78 + "/runs.csv", D82 + "/runs.csv",
               DQ139U + "/reduced/e78-footing.json", DQ139U + "/reduced/e82-footing.json", DQ139U + "/footing.json",
               DEM + "/catalogue.json", DEM + "/unmetered_fit.json", DE71 + "/slopes.json", VIRUS, CORE_PS})}}
    with open(a.out, "w") as f:
        json.dump(res, f, indent=1, sort_keys=True, default=lambda o: None)
        f.write("\n")
    with open(a.txt, "w") as f:
        f.write(render(res))
    with open(a.md, "w") as f:
        f.write(render_md(res))


def pct(x):
    return "-" if x is None else f"{100 * x:.2f}%"


def sci(x):
    if x is None:
        return "-"
    if x == 0:
        return "0"
    e = int(math.floor(math.log10(abs(x))))
    return f"{x / 10 ** e:.2f}e{e}"


def render_md(res):
    L = ["# Q145(a) anatomy tables (post hoc; written by `anatomy_q145a.py`, every figure from committed files)", "",
         "Each TensorFMA table is one TensorFMA instruction on one minion (fp32 4,096 MACs, fp16 8,192, int8 16,384), at the measured "
         "rate of that session's kept passes; each vector table is one instruction of both harts' loop (8 lanes). Lines marked `+` add up "
         "to the board's window reading; lines marked `x` are cross-cuts (a split of lines above, not added). Charge is energy over the "
         "line's voltage; electrons are charge over e. Off-rail lines are counted at the card's nominal 12 V input.", ""]
    for lab in ("E171", "E172", "E78", "E82"):
        for it, led in res["tensor_ledgers"][lab].items():
            L.append(f"## TensorFMA `{it}`, {led['card']} ({lab}, {len(res['sessions'][lab]['items'][it]['passes'])} passes)")
            L.append("")
            L.append(f"Board in the window {led['board_W']:.3f} W (95% {fmt(led['ci95_W']['p_raw'])}); {led['rate_ops_per_s'] / 1e9:.4f}e9 ops/s measured "
                     f"(nominal {led['rate_nominal_ops_per_s'] / 1e9:.4f}e9 from {CPO[led['type']]} cycles an op); **{led['board_pJ_per_op'] / 1000:.2f} nJ an op, "
                     f"{led['board_pJ_per_mac']:.3f} pJ a MAC** with rest included; {led['electrons_board_per_op_at_12V']:.3g} electrons an op from the 12 V input; "
                     f"idle bracket at {led['t_idle_c']:.2f} C, window at {led['t_win_c']:.2f} C. Sum of the `+` lines {led['sum_of_partition_W']:.3f} W.")
            L.append("")
            L.append("| | line | W | pJ / op | pJ / MAC | share of board | V | electrons / op | label |")
            L.append("|---|---|---:|---:|---:|---:|---:|---:|---|")
            for l in led["lines"] + led["cross_cuts"]:
                w = l["W"]
                if l["key"] == "leak_rest_range":
                    wr = l.get("W_range")
                    L.append(f"| x | {l['line']} | {wr[0]:.2f}-{wr[1]:.2f} | | | | | | {l['label']} |")
                    continue
                L.append(f"| {'+' if l['partition'] else 'x'} | {l['line']} | {fmt(w)} | {fmt(l['pJ_per_op'], 1)} | {fmt(l.get('pJ_per_mac'), 4)} | "
                         f"{pct(l['share_of_board'])} | {fmt(l.get('volts'), 3)} | {sci(l.get('electrons_per_op'))} | {l['label']} |")
            L.append("")
    L.append("## One-number pairs on the TensorFMA (a - b, the same pass, W; mean and 95% t half-width over passes)")
    L.append("")
    L.append("| session | card | a - b | n | board D | minion rail | SRAM rail | NoC rail | off-rail | what |")
    L.append("|---|---|---|---:|---:|---:|---:|---:|---:|---|")
    for p in res["tensor_pairs"]:
        L.append(f"| {p['session']} | {p['card']} | `{p['a']}` - `{p['b']}` | {len(p['passes'])} | {fmt(p['D']['mean'])} ± {fmt(p['D']['ci95'])} | "
                 f"{fmt(p['Drail']['mean'])} ± {fmt(p['Drail']['ci95'])} | {fmt(p['Dsram']['mean'])} ± {fmt(p['Dsram']['ci95'])} | "
                 f"{fmt(p['Dnoc']['mean'])} ± {fmt(p['Dnoc']['ci95'])} | {fmt(p['Doff']['mean'])} ± {fmt(p['Doff']['ci95'])} | {p['what']} |")
    L.append("")
    for card, d in res["vector_ledgers"].items():
        for cfg, led in d.items():
            L.append(f"## Vector `{cfg}`, {card} (catalogue, 3 passes)")
            L.append("")
            L.append(f"{led['rate_ops_per_s_wall'] / 1e9:.2f}e9 instructions/s (wall; {led['rate_ops_per_s_device'] / 1e9:.2f}e9 device), "
                     f"{led['issue_per_hart_per_cycle']:.4f} per hart-cycle; board {led['board_W']:.3f} W = **{led['board_pJ_per_op']:.1f} pJ an instruction** "
                     f"with rest included, {led['over_pJ_per_op']:.2f} pJ above rest; die {led['die_c_idle']:.1f} -> {led['die_c_busy']:.1f} C.")
            L.append("")
            L.append("| | line | W | pJ / instr | pJ / lane | share of board | V | electrons / instr | label |")
            L.append("|---|---|---:|---:|---:|---:|---:|---:|---|")
            for l in led["lines"] + led["cross_cuts"]:
                L.append(f"| {'+' if l['partition'] else 'x'} | {l['line']} | {fmt(l['W'])} | {fmt(l.get('pJ_per_op'), 2)} | {fmt(l.get('pJ_per_lane'), 3)} | "
                         f"{pct(l.get('share_of_board'))} | {fmt(l.get('volts'), 3)} | {sci(l.get('electrons_per_op'))} | {l['label']} |")
            L.append("")
    L.append("## Vector pairs (pJ an instruction above rest; per card n 3; pooled card-blocked df 6)")
    L.append("")
    L.append("| op | a - b | card | board | minion | SRAM | NoC | off-rail |")
    L.append("|---|---|---|---:|---:|---:|---:|---:|")
    for p in res["vector"]["pairs"]:
        L.append(f"| {p['op']} | {p['a']} - {p['b']} | {p['card']} | " + " | ".join(f"{fmt(p[kk]['mean'], 2)} ± {fmt(p[kk]['ci95'], 2)}"
                 for kk in ("over_pJ", "minion_over_pJ", "sram_over_pJ", "noc_over_pJ", "off_over_pJ")) + " |")
    for r in res["extras"]["vector_pooled"]:
        L.append(f"| {r['op']} | {r['a']} - {r['b']} | pooled | " + " | ".join(f"**{fmt(r[kk]['mean'], 2)} ± {fmt(r[kk]['ci95'], 2)}**"
                 for kk in ("over_pJ", "minion_over_pJ", "sram_over_pJ", "noc_over_pJ", "off_over_pJ")) + " |")
    L.append("")
    return "\n".join(L) + "\n"


def fmt(x, nd=3):
    if x is None:
        return "-"
    if abs(x) >= 1e5 or (abs(x) < 1e-3 and x != 0):
        return f"{x:.3e}"
    return f"{x:.{nd}f}"


def render(res):
    L = ["Q145(a), post hoc: the anatomy's measured top lines. Every figure is read from committed files; nothing is blind.", ""]
    L.append("VALIDATION (my per-run recompute against the committed reductions):")
    for lab, s in res["sessions"].items():
        v = s["validation"]
        L.append(f"  {lab} {s['card']} k {s['k_w_per_c']:.4f}: compared {v['n_compared']} pass-items; |dD| <= {v['board_D_max_abs_w']:.2e} W, "
                 f"|dS| <= {v['board_S_max_abs_w']:.2e}, |dDrail| <= {v['Drail_max_abs_w']:.2e}, |dSrail| <= {v['Srail_max_abs_w']:.2e}, "
                 f"rate rel <= {v['rate_max_rel']:.1e}; runs.csv p_raw <= {v['csv_p_raw_max_abs_w']:.2e}, rail_dec <= {v['csv_rail_dec_max_abs_w']:.2e}, "
                 f"mv <= {v['csv_mv_max_abs']:.2e}; dips removed {s['dips_removed']}")
    L.append("")
    for lab in ("E171", "E172", "E78", "E82"):
        for it, led in res["tensor_ledgers"][lab].items():
            L.append(f"== TensorFMA {it} on {led['card']} ({lab}): {fmt(led['rate_ops_per_s'] / 1e9, 4)}e9 ops/s measured "
                     f"(nominal {fmt(led['rate_nominal_ops_per_s'] / 1e9, 4)}e9), board {fmt(led['board_W'])} W = {fmt(led['board_pJ_per_op'] / 1000, 3)} nJ/op = "
                     f"{fmt(led['board_pJ_per_mac'])} pJ/MAC; idle T {fmt(led['t_idle_c'], 2)} C; sum of lines {fmt(led['sum_of_partition_W'])} W (gap {fmt(led['books_gap_W'], 6)})")
            for l in led["lines"] + led["cross_cuts"]:
                L.append(f"   {'  ' if l['partition'] else 'x '}{l['key']:<17} W {fmt(l['W']):>8}  pJ/op {fmt(l['pJ_per_op'], 1):>9}  pJ/MAC {fmt(l.get('pJ_per_mac'), 4):>8}  "
                         f"share {fmt(None if l['share_of_board'] is None else 100 * l['share_of_board'], 2):>6}%  e-/op {fmt(l.get('electrons_per_op')):>10}  [{l['label']}]")
            L.append("")
    L.append("ONE-NUMBER PAIRS (a - b, per pass, mean +- 95% t; W):")
    for p in res["tensor_pairs"]:
        L.append(f"  {p['session']} {p['card']} {p['a']} - {p['b']} (n {len(p['passes'])}): board D {fmt(p['D']['mean'])} +- {fmt(p['D']['ci95'])}; "
                 f"minion {fmt(p['Drail']['mean'])} +- {fmt(p['Drail']['ci95'])}; SRAM {fmt(p['Dsram']['mean'])} +- {fmt(p['Dsram']['ci95'])}; "
                 f"NoC {fmt(p['Dnoc']['mean'])} +- {fmt(p['Dnoc']['ci95'])}; off-rail {fmt(p['Doff']['mean'])} +- {fmt(p['Doff']['ci95'])}  ({p['what']})")
    L.append("")
    L.append("VECTOR UNIT (catalogue, per card, mean of 3 passes):")
    for card, d in res["vector_ledgers"].items():
        for cfg, led in d.items():
            L.append(f"== {cfg} on {card}: {fmt(led['rate_ops_per_s_wall'] / 1e9, 2)}e9 instr/s (wall), {fmt(led['issue_per_hart_per_cycle'], 4)} per hart-cycle; "
                     f"board {fmt(led['board_W'])} W = {fmt(led['board_pJ_per_op'], 1)} pJ/op; over rest {fmt(led['over_pJ_per_op'], 2)} pJ (catalogue {fmt(led['catalogue_pj_per_op'], 2)}); "
                     f"die {fmt(led['die_c_idle'], 1)} -> {fmt(led['die_c_busy'], 1)} C; gap {fmt(led['books_gap_W'], 6)}")
            for l in led["lines"] + led["cross_cuts"]:
                L.append(f"   {'  ' if l['partition'] else 'x '}{l['key']:<17} W {fmt(l['W']):>8}  pJ/op {fmt(l.get('pJ_per_op'), 2):>8}  share "
                         f"{fmt(None if l.get('share_of_board') is None else 100 * l['share_of_board'], 2):>6}%  e-/op {fmt(l.get('electrons_per_op')):>10}  [{l['label']}]")
    L.append("")
    L.append("VECTOR PAIRS (per pass, pJ per instruction, mean +- 95% t):")
    for p in res["vector"]["pairs"]:
        L.append(f"  {p['card']} {p['op']} {p['a']} - {p['b']} (n {len(p['passes'])}): board over {fmt(p['over_pJ']['mean'], 2)} +- {fmt(p['over_pJ']['ci95'], 2)}; "
                 f"minion {fmt(p['minion_over_pJ']['mean'], 2)} +- {fmt(p['minion_over_pJ']['ci95'], 2)}; SRAM {fmt(p['sram_over_pJ']['mean'], 2)} +- {fmt(p['sram_over_pJ']['ci95'], 2)}; "
                 f"NoC {fmt(p['noc_over_pJ']['mean'], 2)} +- {fmt(p['noc_over_pJ']['ci95'], 2)}; off-rail {fmt(p['off_over_pJ']['mean'], 2)} +- {fmt(p['off_over_pJ']['ci95'], 2)}")
    L.append("")
    L.append("ISSUE RATES (catalogue, two-hart instruction patterns): " + json.dumps(res["vector"]["rates"], default=str))
    L.append("")
    L.append("VIRUS (public): " + json.dumps(res["virus"], default=str))
    L.append("")
    L.append("CARD 1 / aifoundry3 after each card's own V^2: " + json.dumps(res["card_v2"]))
    L.append("")
    ex = res["extras"]
    L.append("RAIL SHARE over pool 8's items with D > 2 W: " + json.dumps(ex["rail_share"]))
    L.append("VECTOR PAIRS POOLED over the three cards (card-blocked, pJ per instruction):")
    for r in ex["vector_pooled"]:
        L.append(f"  {r['op']} {r['a']} - {r['b']}: " + "; ".join(f"{kk[:-3]} {fmt(r[kk]['mean'], 2)} +- {fmt(r[kk]['ci95'], 2)} (df {r[kk]['df']}, cards "
                 + ", ".join(fmt(x, 2) for x in r[kk]['card_means']) + ")" for kk in ("over_pJ", "minion_over_pJ", "sram_over_pJ", "noc_over_pJ", "off_over_pJ")))
    L.append("VECTOR CARD RATIOS: " + json.dumps(ex["vector_card_v2"]))
    L.append("ISSUE RATES, random two-hart rows: " + json.dumps(ex["issue_random_h2"]))
    L.append("")
    L.append("DDR DROOP (idle less window, mV) and SRAM at tau 0.54 s (S, D in W), per TensorFMA ledger:")
    for lab in ("E171", "E172", "E78", "E82"):
        for it, led in res["tensor_ledgers"][lab].items():
            L.append(f"  {lab} {it}: ddr droop {fmt(led['ddr_droop_mv'])} +- {fmt(led['ddr_droop_mv_ci95'])} mV; SRAM tau0.54 S {fmt(led['sram_tau054']['S'])} D {fmt(led['sram_tau054']['D'])}")
    return "\n".join(L) + "\n"


if __name__ == "__main__":
    main()
