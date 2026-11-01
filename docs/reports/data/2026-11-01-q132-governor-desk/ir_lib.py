#!/usr/bin/env python3
"""Q132(g): the governor's one-second idle reset, read from committed data. Shared loaders. POST HOC, desk only, no card.

A SESSION here is one run directory of tools/claims-v3/hpl/run_hpl.py's lineage: runs.jsonl, launches.jsonl(.gz) with each
process's kernels under `sparsity`, tel/<run>.jsonl(.gz) at 10 Hz, sp/<run>.bin (the service processor's trace ring after
every run). No third-party modules.
"""
import gzip
import json
import math
import os
import statistics as st
import sys

CYCLES_800 = 0.8e9
CYCLES_600 = 0.6e9
OVERHEAD_S = 0.00048   # a launch's wall minus cycles/800 MHz, measured below (launch_overhead)

SESSIONS = {
    "E64": ("aifoundry2", 0, ["2026-10-23-e64-horace-power-limit/s1", "2026-10-23-e64-horace-power-limit/s2"]),
    "E69": ("aifoundry2", 0, ["2026-10-27-e69-governor-knob/s1", "2026-10-27-e69-governor-knob/s2", "2026-10-27-e69-governor-knob/s3"]),
    "E80": ("aifoundry2", 0, ["2026-10-31-e80-kinds-speed/s1"]),
    "E83": ("aifoundry2", 0, ["2026-10-31-e83-kinds-speed-rest/s1"]),
    "E87": ("aifoundry2", 0, ["2026-10-31-e87-real-tensors-speed/s1"]),
    "E84": ("aifoundry1", 0, ["2026-10-31-e84-speed-aifoundry1-card0/s1"]),
}


def jl(path):
    out = []
    if not os.path.exists(path) and os.path.exists(path + ".gz"):
        lines = gzip.open(path + ".gz", "rt")
    elif os.path.exists(path):
        lines = open(path)
    else:
        return out
    for ln in lines:
        ln = ln.strip()
        if ln.startswith("{"):
            try:
                out.append(json.loads(ln))
            except ValueError:
                pass
    return out


def tel(path):
    """[(t_ms, die, die_high, board_w, mhz, took_ms, since_reset_ms)] from a 10 Hz sampler file."""
    s = []
    for d in jl(path):
        try:
            ms = d.get("temp_c", {}).get("minshire") or [None, None, None]
            s.append((int(d["t_ms"]), ms[0], ms[2] if len(ms) > 2 else None, d.get("board_w"), d.get("mhz", {}).get("minion"),
                      d.get("took_ms"), d.get("since_reset_ms")))
        except (KeyError, TypeError, ValueError, AttributeError):
            pass
    s.sort()
    return s


def load_rundir(repo, rel):
    """One session directory: its runs in order, each with processes (kernels) and telemetry; and all ring entries."""
    sys.path.insert(0, os.path.join(repo, "tools/claims-v3/hpl"))
    sys.path.insert(0, os.path.join(repo, "tools/claims-v3/dv2"))
    import sptrace_full as spf
    d = os.path.join(repo, "docs/reports/data", rel)
    runs = jl(os.path.join(d, "runs.jsonl"))
    launches = jl(os.path.join(d, "launches.jsonl"))
    by_run = {}
    for L in launches:
        by_run.setdefault(L.get("run"), []).append(L)
    out = []
    ring = {}
    cover = []
    prev = None
    start_bin = os.path.join(d, "sp", "start.bin")
    if os.path.exists(start_bin):
        prev = spf.scan(open(start_bin, "rb").read()) or []
    for r in runs:
        name = r["run"]
        p = os.path.join(d, "sp", name + ".bin")
        cur = spf.scan(open(p, "rb").read()) if os.path.exists(p) else None
        new = []
        if cur is not None:
            new = spf.since(prev, cur) if prev is not None else list(cur)
            prev = cur
            for e in cur:
                ring.setdefault((e["ts"], e["kind"]), e)
        procs = []
        for L in sorted(by_run.get(name, []), key=lambda x: x.get("t_start_ms", 0)):
            if L.get("role") != "work":
                continue
            ks = [k for k in L.get("sparsity", []) if k.get("t_start_ms") and k.get("wall_s")]
            procs.append({"proc": L.get("proc"), "t0": L.get("t_start_ms"), "t1": L.get("t_end_ms"), "kernels": ks, "rc": L.get("rc")})
        T = tel(os.path.join(d, "tel", name + ".jsonl"))
        out.append({"run": name, "block": r.get("block"), "type": r.get("type"), "values": r.get("values"), "label": r.get("label"),
                    "minions": r.get("minions"), "seconds": r.get("seconds"), "gate": r.get("gate"), "procs": procs, "tel": T,
                    "ring_new": new, "t_first": r.get("t_first_ms"), "t_last": r.get("t_last_ms"), "session": rel})
    return {"rel": rel, "runs": out, "ring": sorted(ring.values(), key=lambda e: e["ts"])}


def kind_of(run):
    v = (run.get("values") or "").split("/")[-1].replace(".bin", "")
    return f"{run.get('type')}/{v}"


def g_eff(k):
    """The kernel's mean clock in GHz: its own cycles over its wall time less the launch overhead."""
    w = k["wall_s"] - OVERHEAD_S
    return k["cycles_max"] / w / 1e9 if w > 0 else None


def x_ms(k):
    """If kernel k ran at 800 MHz and then at 600 MHz: how long it ran at 800 MHz, in ms."""
    w = k["wall_s"] - OVERHEAD_S
    return (k["cycles_max"] - CYCLES_600 * w) / (CYCLES_800 - CYCLES_600) * 1000.0


def fit_line(xy):
    n = len(xy)
    mx, my = sum(x for x, _ in xy) / n, sum(y for _, y in xy) / n
    sxx = sum((x - mx) ** 2 for x, _ in xy)
    if sxx == 0:
        return my, 0.0, None
    b = sum((x - mx) * (y - my) for x, y in xy) / sxx
    a = my - b * mx
    res = [y - (a + b * x) for x, y in xy]
    return a, b, math.sqrt(sum(r * r for r in res) / n)


def lattice_R(ts_us, q_us):
    c = sum(math.cos(2 * math.pi * (t % q_us) / q_us) for t in ts_us)
    s = sum(math.sin(2 * math.pi * (t % q_us) / q_us) for t in ts_us)
    return math.hypot(c, s) / len(ts_us), math.atan2(s, c)


def fit_lattice(ts_us, q0=1_000_000.0, span=2000.0):
    """The period (us) near q0 that puts the most markers on one phase, by a coarse then fine scan; then least squares."""
    best = None
    coarse = span / 200
    for i in range(-200, 201):
        q = q0 + i * coarse
        r, ph = lattice_R(ts_us, q)
        if best is None or r > best[0]:
            best = (r, q)
    q = best[1]
    for step in (coarse / 10, coarse / 100):
        bb = None
        for j in range(-20, 21):
            qq = q + j * step
            r, ph = lattice_R(ts_us, qq)
            if bb is None or r > bb[0]:
                bb = (r, qq)
        q = bb[1]
    r, ph = lattice_R(ts_us, q)
    p = ph / (2 * math.pi) * q
    pts = [(round((t - p) / q), t) for t in ts_us]
    # least squares, robust: twice, dropping points more than 40 ms off
    for _ in range(3):
        good = [(k, t) for k, t in pts if abs(t - (p + q * k)) < 40000]
        if len(good) >= 2 and len({k for k, _ in good}) >= 2:
            a, b, _rms = fit_line(good)
            p, q = a, b
            pts = [(round((t - p) / q), t) for t in ts_us]
    res = [t - (p + q * k) for k, t in pts]
    return {"p_us": p, "q_us": q, "R": r, "res_us": res, "k": [k for k, _ in pts]}


def fisher_one_sided(a, b, c, d):
    """P(X >= a) for the 2x2 table [[a, b], [c, d]] with margins fixed."""
    n = a + b + c + d
    r1, c1 = a + b, a + c
    def hyp(x):
        return math.comb(c1, x) * math.comb(n - c1, r1 - x) / math.comb(n, r1)
    return sum(hyp(x) for x in range(a, min(r1, c1) + 1))


def poisson_ci(n, z=1.96):
    """A simple 95% interval for a Poisson count (Garwood by bisection on the tail sums)."""
    def tail_low(mu):  # P(X >= n)
        return 1 - sum(math.exp(-mu) * mu ** i / math.factorial(i) for i in range(n))
    def tail_hi(mu):  # P(X <= n)
        return sum(math.exp(-mu) * mu ** i / math.factorial(i) for i in range(n + 1))
    lo = 0.0
    if n > 0:
        a, b = 0.0, n + 1.0
        for _ in range(60):
            m = (a + b) / 2
            if tail_low(m) < 0.025:
                a = m
            else:
                b = m
        lo = a
    a, b = n + 0.0, n + 20.0 + 5 * math.sqrt(n + 1)
    for _ in range(60):
        m = (a + b) / 2
        if tail_hi(m) > 0.025:
            a = m
        else:
            b = m
    return lo, a


def launch_overhead(run_list):
    """The median of wall - cycles/800 MHz over kernels plainly at 800 MHz (ghz >= 0.795)."""
    v = []
    for r in run_list:
        for p in r["procs"]:
            for k in p["kernels"]:
                if k.get("launch", -1) >= 0 and k.get("ghz", 0) >= 0.795 and k["wall_s"] > 0.1:
                    v.append(k["wall_s"] - k["cycles_max"] / CYCLES_800)
    return st.median(v) if v else None
