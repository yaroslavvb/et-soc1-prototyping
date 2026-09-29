#!/usr/bin/env python3
"""make_page_data.py: the data of the page "Sparse parity on the ET-SoC-1", computed from the committed results.

    python3 docs/reports/data/2026-09-29-sparse-parity/make_page_data.py        # writes page.json beside this file
    NODE_PATH=$PWD/node_modules python3 scripts/build-report.py sparse-parity \
        docs/reports/data/2026-09-29-sparse-parity/page.json docs/reports/2026-09-29-sparse-parity.html

Host code only: it opens no card, runs no kernel and starts no sys_emu. It needs numpy (the SP3 prototype's report
helpers and tools/cycle_model.py import it) and runs in about two seconds. Every number the page shows comes from
this file's output; the page's prose quotes a few of them directly, and CHECKS at the end asserts that those still
match the data, so a change in a result file fails here instead of leaving the page wrong.

Where each block comes from (all paths from the repository's root):
  grid     workloads/sparseparity/proto/data/2026-09-28-aifoundry1/*.jsonl, SP3's CPU sweep on aifoundry1's host
           (28 September), through proto/report.py's own helpers: one core of SP3's AVX-512 bit scan at the 99%
           sample count, measured where timed, else a timed slice, else 4 threads x their speedup, else the fit.
  cpu      workloads/sparseparity/cpu/data/2026-09-29-aifoundry3-r/bench.jsonl, the CPU baselines after the reviews
           (aifoundry3's host, 29 September 03:52-04:07 PDT, median of 5), and
           workloads/sparseparity/data/2026-09-29-aifoundry3-sysemu-m5/cpu2s.jsonl, the CPU's two-stage screens at
           P(loss) < 1e-4 (10:03 PDT). 16 threads are extrapolated from 6 with tools/table_cpu.py's rule.
  ladder   the card runs on aifoundry3: data/2026-09-29-aifoundry3-card/ (M1, the probe, M2, M3; 04:15-04:30 PDT),
           data/2026-09-29-aifoundry3-card-m4/ (M4's A/B, 08:17-08:45 PDT) and
           data/2026-09-29-aifoundry3-m5-energy/ (M5 and energy, 11:29-11:40 PDT); the design's predictions from
           docs/research/sparse-parity/design_model.py (plan(), the M3 private and M4 cooperative models).
  energy   data/2026-09-29-aifoundry3-m5-energy/energy/*/energy.json and aifoundry3-1136-f5.json (the two halves
           of (256,5) combined), as tools/energy_reduce.py wrote them.
  cycles   workloads/sparseparity/tools/cycle_model.py (its FITTED constants and its `explain` computation) on
           M3's two all-shire runs.
"""
from __future__ import annotations

import importlib.util
import json
import math
import statistics as st
import sys
from pathlib import Path

sys.dont_write_bytecode = True   # it imports other directories' modules: leave no __pycache__ behind in them
HERE = Path(__file__).resolve().parent
REPO = HERE.parents[3]
W = REPO / "workloads/sparseparity"
PROTO = W / "proto"
PROTO_DATA = PROTO / "data/2026-09-28-aifoundry1"
CPU_R = W / "cpu/data/2026-09-29-aifoundry3-r"
CPU_FIRST = W / "cpu/data/2026-09-29-aifoundry3"
CPU2S = W / "data/2026-09-29-aifoundry3-sysemu-m5/cpu2s.jsonl"
CARD = W / "data/2026-09-29-aifoundry3-card"
RUNS = CARD / "runs"
M4 = W / "data/2026-09-29-aifoundry3-card-m4"
M5 = W / "data/2026-09-29-aifoundry3-m5-energy"
DESIGN = REPO / "docs/research/sparse-parity/design_model.py"
CYCLE = W / "tools/cycle_model.py"

F_HZ = 600e6
FLOOR_CYC = 512          # cycles per op when every minion of a shire streams 2 KB per op (E37: 511.94; 4 B/minion-cycle)
SHIRE_BPC = 128.0        # the shire's L2 bytes per cycle (E37; tools/cycle_model.py BW_SHIRE)
P_ASSUMED = (125.0, 251.0)


def rel(p: Path) -> str:
    return str(Path(p).resolve().relative_to(REPO))


def last_json(p: Path) -> dict:
    """The last line of a file that is a JSON object (the host prints logs, then one JSON line)."""
    lines = [ln for ln in Path(p).read_text(errors="replace").splitlines() if ln.startswith("{")]
    if not lines:
        raise SystemExit(f"no JSON line in {rel(p)}")
    return json.loads(lines[-1])


def jsonl(p: Path) -> list:
    return [json.loads(x) for x in Path(p).read_text().splitlines() if x.strip()]


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


def g3(x: float) -> str:
    """3 significant digits, trailing zeros kept (15.0, 1.50), no trailing point"""
    return format(x, "#.3g").rstrip(".")


def fmt_s(t: float) -> str:
    """seconds as the page writes them: 3 significant digits; µs, ms below 0.1 s, then s, then min"""
    if t < 1e-3:
        return f"{g3(t * 1e6)} µs"
    if t < 0.1:
        return f"{g3(t * 1e3)} ms"
    if t < 120:
        return f"{g3(t)} s"
    return f"{g3(t / 60)} min"


def x2(v: float) -> str:
    """a ratio with 2 significant digits (1.1, 7.8, 12)"""
    return f"{v:.2g}" if v < 10 else f"{v:.0f}"


def rng(a: float, b: float, unit: str = "×") -> str:
    lo, hi = x2(min(a, b)), x2(max(a, b))
    return (lo if lo == hi else f"{lo}–{hi}") + unit


def sci(v: float) -> str:
    """2 significant digits times a power of ten, in HTML (true minus in the exponent)"""
    e = int(math.floor(math.log10(abs(v))))
    return f"{v / 10 ** e:.2g}×10<sup>{str(e).replace('-', '−')}</sup>"


def floor_staged(j: dict) -> float:
    """The shire-bandwidth floor with the staged rows counted as well (tools/cycle_model.py shire_bytes, streamed A):
    2 KB per op plus 1 KB per row tile and sample slice, at 128 B per shire-cycle; DESIGN.md's Amendments quote it
    (72 ms / 300 ms for the one-stage L1 and L2)."""
    g, p = j["geometry"], j["plan"]
    return (p["ops"] * 2048.0 + g["row_tiles"] * g["S"] * 1024.0) / (SHIRE_BPC * (p["minions"] / 32) * F_HZ)


def kept_at(m1: int, eta: float, target: float = 1e-4) -> tuple:
    """The highest tau1 (of m1's parity) that keeps the secret with P(loss) < target, and the share of the candidates
    it passes (a candidate's c1 under the null is m1 - 2 Bin(m1, 1/2)); design_model.py screen_at's arithmetic."""
    for tau in range(m1, -m1 - 1, -2):
        if p_loss(m1, tau, eta) < target:
            return tau, binom_cdf((m1 - tau) // 2, m1, 0.5)
    raise ValueError("no tau1")


def binom_cdf(d: int, m: int, p: float) -> float:
    """P(Bin(m, p) <= d), in log space (design_model.py's)."""
    if d < 0:
        return 0.0
    if d >= m:
        return 1.0
    lp, lq = math.log(p), math.log(1 - p)
    return min(1.0, sum(math.exp(math.lgamma(m + 1) - math.lgamma(i + 1) - math.lgamma(m - i + 1) + i * lp + (m - i) * lq)
                        for i in range(d + 1)))


def p_loss(m1: int, tau: int, eta: float) -> float:
    """The secret's c1 = m1 - 2 * Bin(m1, eta) falls under tau1."""
    return 1.0 - binom_cdf((m1 - tau) // 2, m1, eta)


INST = [  # id, label, (n, k, eta, m), the energy run's directory
    ("L1", "L1", (512, 4, 0.3, 448), "aifoundry3-1136-l1"),
    ("L2", "L2", (512, 4, 0.4, 1850), "aifoundry3-1136-l2"),
    ("F5", "(256,5)", (256, 5, 0.4, 1925), None),
]


# ---------------------------------------------------------------------------------------------------- grid (SP3)
def grid_block() -> dict:
    sys.path.insert(0, str(PROTO))
    report = load_module("sp_report", PROTO / "report.py")
    sp = sys.modules.get("sp") or __import__("sp")
    D = str(PROTO_DATA)
    ms, exh, ge = report.load(D, "msearch"), report.load(D, "exh"), report.load(D, "ge")
    slices = {(d["n"], d["k"], d["eta"]): d for d in report.load(D, "exh_slice")}
    memp, _ = report.m99_emp(ms)
    fit = report.Fit(exh)
    ex1, ex4 = {}, {}
    for d in exh:
        (ex1 if d["threads"] == 1 else ex4).setdefault((d["n"], d["k"], d["eta"]), []).append(d)
    sp4 = [st.median(x["wall_s"] for x in ex1[k]) / st.median(x["wall_s"] for x in ex4[k])
           for k in ex4 if k in ex1 and st.median(x["wall_s"] for x in ex1[k]) > 0.2]
    sp4m = st.median(sp4)

    def t1_info(n, k, e, m):  # report.py main()'s t1_info, verbatim in effect
        key = (n, k, e)
        if key in ex1:
            return st.median(x["wall_s"] for x in ex1[key]), "measured"
        if key in slices and slices[key]["m"] == m:
            d = slices[key]
            return math.comb(n, k) * d["wall_s"] / d["subsets"], f"timed 1/{d['slice']} slice"
        if key in ex4:
            return st.median(x["wall_s"] for x in ex4[key]) * sp4m, f"4 threads × {sp4m:.2f}"
        return fit.t1(n, k, m), "per-subset fit"

    pts = []
    for n in (128, 256, 512):
        for k in (3, 4, 5):
            for e in report.ETAS:
                me = memp.get((n, k, e))
                m = me or sp.m99_model(n, k, e)
                t, src = t1_info(n, k, e, m)
                C = math.comb(n, k)
                pts.append(dict(n=n, k=k, eta=e, m=m, msrc="measured" if me else "model", cand=C, W=C * m,
                                t=round(t, 7), tsrc=src))
    ges = []
    for n in (128, 256, 512):
        rs = [d for d in ge if d["n"] == n]
        ges.append(dict(n=n, s=st.median(d["wall_s"] for d in rs if d["k"] == 3),
                        extra_max=max(d["m_full_rank"] - n for d in rs), runs=len(rs), ok=sum(d["ok"] for d in rs)))
    return dict(ns=[128, 256, 512], ks=[3, 4, 5], etas=report.ETAS, pts=pts, ge=ges, sp4=round(sp4m, 2),
                show={"L1": [512, 4, 0.3], "L2": [512, 4, 0.4], "F5": [256, 5, 0.4]},
                timing_runs=len(exh), timing_ok=sum(d["ok"] for d in exh),
                src=rel(PROTO_DATA))


# ---------------------------------------------------------------------------------------------------- CPU
def cpu_block() -> dict:
    bench = jsonl(CPU_R / "bench.jsonl")
    first = jsonl(CPU_FIRST / "bench.jsonl")
    cpu2s = jsonl(CPU2S)

    def row(rows, label, th, place="cores"):
        c = [r for r in rows if r["label"] == label and r.get("threads") == th and r["place"] == place]
        return c[-1] if c else None

    def tsolve(r):  # table_cpu.py times() + stage2(): median per full solve
        return r.get("wall_med_s", r["wall_s"]) / r.get("fraction", 1) + r.get("stage2_s", 0.0) / r.get("fraction", 1)

    def t16(t6, t4=None, U=None):  # table_cpu.py: fast = t6 * 6/8 / max(U, 1); slow = t6 / (1 + (8/6 - 1) min(eff46, 1))
        fast = t6 * 6 / 8 / max(U or 1.0, 1.0)
        slow = t6 / (1 + (8 / 6 - 1) * min((t4 / t6) / 1.5, 1.0)) if t4 else fast * 1.03
        return [fast, slow]

    out = {}
    lab = {"L1": "L1", "L2": "L2", "F5": "F5"}
    for iid, _, (n, k, eta, m), _ in INST:
        r1, r4, r6 = (row(bench, f"vexh {lab[iid]}", t) for t in (1, 4, 6))
        f1 = row(first, f"vexh {lab[iid]}", 1)
        smt = row(bench, f"vexh {lab[iid]}", 2, "smt2")
        U = tsolve(r1) / tsolve(smt) if smt else None
        o = dict(one_core=tsolve(r1), one_core_first=tsolve(f1), t6_scan=tsolve(r6),
                 t16_scan=t16(tsolve(r6), tsolve(r4), U), mhz_1t=r1.get("mhz_mean"), smt_u=U)
        if iid == "L1":
            mm = [r for r in bench if r["label"] == "mitm L1" and r["threads"] == 6]
            e6 = st.mean(r["expected_s_full"] for r in mm)
            o.update(best6=e6, best6_method="meet in the middle with a random halving of the features "
                     f"(expected time, mean over {len(mm)} seeds)", best6_short="meet in the middle",
                     best6_ploss=0.0, best16=[e6 * 6 / 8, e6 * 6 / 8 * 1.03], best_seeds_ok=sum(r["ok"] for r in mm))
            s = [r for r in cpu2s if r["n"] == n and r["k"] == k and r["eta"] == eta and r["m"] == 320][-1]
            o["two_stage6"] = dict(m1=320, tau=s["tau"], s=tsolve(s), ploss=p_loss(320, s["tau"], eta))
        else:
            s = [r for r in cpu2s if r["n"] == n and r["k"] == k and r["eta"] == eta and r["m"] == 1152][-1]
            ref4, ref6 = (row(bench, f"vexh {lab[iid]} two-stage m1=1024", t) for t in (4, 6))
            f16 = [x / tsolve(ref6) for x in t16(tsolve(ref6), tsolve(ref4))]
            b = tsolve(s)
            o.update(best6=b, best6_method=f"its own two-stage screen: the AVX-512 scan at m1 = 1,152, τ1 = {s['tau']}, "
                     "survivors rescored on all m", best6_short="two-stage AVX-512 scan",
                     best6_ploss=p_loss(1152, s["tau"], eta), best16=[b * f for f in f16],
                     screen1024=dict(s=tsolve(ref6), ploss=p_loss(1024, 104, eta)))
        out[iid] = o
    return dict(per=out, host="i7-11700K (8 cores, 16 threads, AVX-512 VPOPCNTQ), aifoundry3's host",
                src=[rel(CPU_R / "bench.jsonl"), rel(CPU2S)])


# ---------------------------------------------------------------------------------------------------- card runs
def run(p: Path) -> dict:
    j = last_json(p)
    k = j["kernel"]
    return dict(file=rel(p), status=j["status"], launch=sum(j["launch_s"]), cyc_op=k["cycles_per_op_busiest"],
                imb=k["cycles_max"] / k["cycles_median"], ops=j["plan"]["ops"], minions=j["plan"]["minions"],
                model=j["plan"].get("model_s"), solved=j["result"]["solved"], sum_c=j["checks"]["sum_c"],
                sum_c2=j["checks"]["sum_c2"], oracle=j["checks"]["oracle"], mhz=k.get("clock_mhz_est"),
                ts=j.get("two_stage"), j=j)


def card_block(design) -> dict:
    g = sorted(p for p in RUNS.glob("aifoundry3-*") if not p.name.endswith("-dry"))
    m1dir, probedir, m2dir = g[0], g[1], g[2]
    # M1: one minion
    m1 = {nm: run(m1dir / f"{nm}.json") for nm in ("m1-c0-scalar", "m1-c0-tensor", "m1-neg-drop", "m1-neg-dup",
                                                 "m1-neg-mask", "m1-tie", "m1-c1", "m1-l1-timing", "m1-l1",
                                                 "m1-l2-timing", "m1-l2")}
    seeds = [run(m1dir / f"m1-c1-32-seed{i}.json") for i in range(1, 21)]
    probes = [run(p) for p in sorted(probedir.glob("probe-*.json"))]
    knee = [dict(p=p, cyc_op=run(m2dir / f"m2-knee-p{p}-timing.json")["cyc_op"]) for p in (1, 2, 4, 8, 16, 32)]
    m2full = run(m2dir / "m2-l1-full.json")
    nowait = run(m2dir / "m2-l2-q0-nowait.json")
    m3 = {"L1": run(RUNS / "m3-manual-0420/l1.log"), "L2": run(RUNS / "m3-manual-0420/l2.log")}
    # M4's A/B
    ab = {}
    for iid, key in (("L1", "l1"), ("L2", "l2")):
        ab[iid] = {v: run(M4 / f"m4/m4-32s-{key}-{v}.json") for v in ("m1", "a", "b", "c", "m4", "m4d")}
    f5 = {v: [run(M4 / f"m4/m4-32s-f5-h{h}-{v}.json") for h in (0, 1)] for v in ("m1", "m4", "m4d")}
    f5["b"] = [run(M4 / f"f5-b/h{h}.log") for h in (0, 1)]
    ab["F5"] = {v: dict(launch=sum(x["launch"] for x in hs), cyc_op=max(x["cyc_op"] for x in hs),
                        cyc_op_halves=[x["cyc_op"] for x in hs], files=[x["file"] for x in hs],
                        solved=any(x["solved"] for x in hs), runs=[dict(mhz=x["mhz"]) for x in hs])
                for v, hs in f5.items()}
    # M5
    m5 = {nm: run(M5 / f"m5/{nm}.json") for nm in ("m5-1s-small", "m5-ovf", "m5-negmask", "m5-negtau", "m5-lostlog",
                                                   "m5-l1-b", "m5-l1-s320", "m5-l1-res192", "m5-l2-b", "m5-l2-s1152",
                                                   "m5-f5-s1152")}
    ver = {nm: last_json(M5 / f"m5/{nm}.verify.json")["checks"]["oracle"]
           for nm in ("m5-l1-s320", "m5-l1-res192", "m5-l2-s1152", "m5-f5-s1152")}
    two = {"L1": m5["m5-l1-s320"], "L2": m5["m5-l2-s1152"], "F5": m5["m5-f5-s1152"]}

    ms = [dict(id="M2", label="M2", sub="one shire (32 minions)"),
          dict(id="M3", label="M3", sub="1,024 minions, M1's kernel"),
          dict(id="M4", label="M4", sub="fitted plan + incremental rows (b)"),
          dict(id="M5", label="M5", sub="two-stage screen")]
    series = {
        "L1": [dict(ms="M2", s=m2full["launch"], note="all of L1 on one shire, M1's kernel", file=m2full["file"]),
               dict(ms="M3", s=m3["L1"]["launch"], note="first all-shire run, M1's kernel and planner", file=m3["L1"]["file"]),
               dict(ms="M4", s=ab["L1"]["b"]["launch"], note="variant b: the fitted planner and incremental row generation",
                    file=ab["L1"]["b"]["file"]),
               dict(ms="M5", s=two["L1"]["ts"]["solve_s"], note="two-stage: launch + survivor readback + host stage 2",
                    file=two["L1"]["file"])],
        "L2": [dict(ms="M3", s=m3["L2"]["launch"], note="first all-shire run, M1's kernel and planner", file=m3["L2"]["file"]),
               dict(ms="M4", s=ab["L2"]["b"]["launch"], note="variant b: the fitted planner and incremental row generation",
                    file=ab["L2"]["b"]["file"]),
               dict(ms="M5", s=two["L2"]["ts"]["solve_s"], note="two-stage: launch + survivor readback + host stage 2",
                    file=two["L2"]["file"])],
        "F5": [dict(ms="M3", s=ab["F5"]["m1"]["launch"],
                    note="M1's kernel and planner on 1,024 minions, in two halves (run in M4's A/B, 08:17-08:45 PDT)",
                    file=", ".join(ab["F5"]["m1"]["files"])),
               dict(ms="M4", s=ab["F5"]["b"]["launch"], note="variant b, in two halves (one process each, under 10 s)",
                    file=", ".join(ab["F5"]["b"]["files"])),
               dict(ms="M5", s=two["F5"]["ts"]["solve_s"], note="two-stage, whole, one process", file=two["F5"]["file"])],
    }
    return dict(m1=m1, seeds=seeds, probes=probes, knee=knee, m2full=m2full, nowait=nowait, m3=m3, ab=ab, m5=m5,
                ver=ver, two=two, ms=ms, series=series)


def design_block() -> dict:
    dm = load_module("design_model", DESIGN)
    out = {}
    for iid, _, (n, k, eta, m), _ in INST:
        out[iid] = dict(M3=dm.plan(n, k, m, "private")["t"], M4=dm.plan(n, k, m, "coop")["t"])
    return out


# ---------------------------------------------------------------------------------------------------- energy
def energy_block() -> list:
    rows = []
    for iid, _, inst, d in INST:
        if d:
            e = json.loads((M5 / "energy" / d / "energy.json").read_text())
            rails = {k: e["rails"][k + "_w"]["j_per_solve"] for k in ("minion", "sram", "noc")}
            rails["unmetered"] = e["rails"]["unmetered"]["j_per_solve"]
            cpu = e["cpu"]
            rows.append(dict(id=iid, solves=e["solves"], solves_per_s=e["solves_per_s"],
                             kernel_s=e["launch_s_mean"], board_w=e["board"]["catalogue"]["busy_w"],
                             idle_w=e["board"]["catalogue"]["idle_w"], j_over=e["board"]["j_per_solve"],
                             j_total=e["board"]["j_per_solve_total"], j_catalogue=e["board"]["catalogue"]["j_per_solve"],
                             die=[e["die_c"]["before"], e["die_c"]["busy"]], mhz=e["meter"]["minion_mhz_busy"],
                             host=cpu["host_package_j"], cpu_j=cpu["cpu_6t_best_j"], cpu_s=cpu["cpu_6t_best_s"],
                             cpu_method=cpu["cpu_6t_best"], ratio_board=cpu["cpu_over_card_board"],
                             ratio_host=cpu["cpu_over_card_and_host"], rails_j=rails,
                             host_busy=e["host_share"]["busy_cores_mean"],
                             file=rel(M5 / "energy" / d / "energy.json")))
        else:
            c = json.loads((M5 / "energy/aifoundry3-1136-f5.json").read_text())
            parts = [json.loads((M5 / "energy" / Path(p).name / "energy.json").read_text()) for p in c["parts"]]
            cpu = c["cpu"]
            rows.append(dict(id=iid, solves=[p["solves"] for p in parts], solves_per_s=1 / c["wall_s_per_solve"],
                             kernel_s=c["kernel_s_per_solve"],
                             board_w=[p["board"]["catalogue"]["busy_w"] for p in parts],
                             idle_w=st.mean(p["board"]["catalogue"]["idle_w"] for p in parts),
                             j_over=c["board"]["j_per_solve"], j_total=c["board"]["j_per_solve_total"],
                             j_catalogue=c["board_catalogue"]["j_per_solve"],
                             die=[min(p["die_c"]["before"] for p in parts), max(c["die_c_busy"])],
                             mhz=sorted({x for p in parts for x in p["meter"]["minion_mhz_busy"]}),
                             host=cpu["host_package_j"], cpu_j=cpu["cpu_6t_best_j"], cpu_s=cpu["cpu_6t_best_s"],
                             cpu_method=cpu["cpu_6t_best"], ratio_board=cpu["cpu_over_card_board"],
                             ratio_host=cpu["cpu_over_card_and_host"],
                             # combine's rails are J per solve over idle despite their "_w" keys: they sum to the headline
                             rails_j={"minion": c["rails"]["minion_w"], "sram": c["rails"]["sram_w"],
                                      "noc": c["rails"]["noc_w"], "unmetered": c["rails"]["unmetered"]},
                             host_busy=max(p["host_share"]["busy_cores_mean"] for p in parts),
                             file=rel(M5 / "energy/aifoundry3-1136-f5.json")))
    return rows


# ---------------------------------------------------------------------------------------------------- cycles
def cycles_block() -> dict:
    cm = load_module("cycle_model", CYCLE)
    P = cm.constants()
    runs = cm.load_runs(Path(cm.DATA), include=lambda nm: nm in ("m3-l1", "m3-l2"))
    out = []
    for r in sorted(runs, key=lambda x: x.name):
        C = [m["cycles"] for m in r.minions]
        ops = [m["ops"] for m in r.minions]
        order = sorted(range(len(C)), key=lambda i: C[i])
        cop = P["C_OP_" + r.path]
        tot = dict(ops=0.0, bw=0.0, drain=0.0, epi=0.0, tile=0.0, smt=0.0, wait=0.0, copy=0.0, cyc=0.0)
        for mn in r.minions:
            b = cm.breakdown(r, mn, P)
            for k_, v in (("ops", b["tensor_ops_solo"]), ("bw", b["bw_contention"]), ("drain", b["drain"]),
                          ("epi", b["epilogue"]), ("tile", b["tile_overhead"]), ("smt", b["smt"]), ("wait", b["wait"]),
                          ("copy", b["copy"]), ("cyc", b["cycles"])):
                tot[k_] += v
        n_ops = sum(ops)

        def parts(d, nops):
            return dict(op=d["ops"] / nops, epi=d["epi"] / nops, smt=max(0.0, d["smt"]) / nops, wait=d["wait"] / nops,
                        other=(d["bw"] + d["drain"] + d["tile"] + d["copy"]) / nops)
        bi = order[-1]
        b = cm.breakdown(r, r.minions[bi], P)
        busy = dict(ops=b["tensor_ops_solo"], bw=b["bw_contention"], drain=b["drain"], epi=b["epilogue"],
                    tile=b["tile_overhead"], smt=b["smt"], wait=b["wait"], copy=b["copy"])
        mean_c = st.mean(C)
        out.append(dict(run=r.name, S=r.S, mean=parts(tot, n_ops), mean_total=tot["cyc"] / n_ops,
                        busiest=parts(busy, b["ops"]), busiest_model_total=b["cycles"] / b["ops"],
                        busiest_meas=b["meas"] / b["ops"], busiest_tiles=b["T"],
                        median_tiles=r.minions[order[len(order) // 2]]["T"],
                        imbalance=max(C) / mean_c, overhead=mean_c / (st.mean(ops) * cop), opcost=cop / 270,
                        gap=max(C) / (st.mean(ops) * 270), launch_ms=max(C) / F_HZ * 1e3))
    return dict(runs=out, fitted=dict(E_OUT=P["E_OUT"], C_OP_str=P["C_OP_str"], G_TILE=P["G_TILE"],
                                       G_SLICE=P["G_SLICE"], G_K=P["G_K"]),
                src=rel(CYCLE), fit_rms="1.8%")


# ---------------------------------------------------------------------------------------------------- assemble
def main():
    grid = grid_block()
    cpu = cpu_block()
    design = design_block()
    card = card_block(design)
    energy = energy_block()
    cyc = cycles_block()
    per = cpu["per"]
    two = card["two"]
    ab = card["ab"]

    inst = []
    for iid, lab, (n, k, eta, m), _ in INST:
        j = two[iid]["j"]
        inst.append(dict(id=iid, label=lab, full=f"{lab} ({n}, {k}, {eta}, {m:,})" if iid != "F5" else f"({n}, {k}, {eta}, {m:,})",
                         n=n, k=k, eta=eta, m=m, cand=math.comb(n, k), secret=j["instance"]["secret"],
                         W=math.comb(n, k) * m))

    # headline ratios
    card_t = {i: two[i]["ts"]["solve_s"] for i in per}
    r1 = {i: per[i]["one_core"] / card_t[i] for i in per}
    r6 = {i: per[i]["best6"] / card_t[i] for i in per}
    r16 = {i: [x / card_t[i] for x in per[i]["best16"]] for i in per}
    r6_b = {i: per[i]["best6"] / ab[i]["b"]["launch"] for i in per}
    e_board = [x for e in energy for x in e["ratio_board"]]
    e_host = [x for e in energy for x in e["ratio_host"]]

    ladder = dict(ms=card["ms"], series=card["series"], design=design,
                  cpu1={i: per[i]["one_core"] for i in per},
                  cpu6={i: dict(s=per[i]["best6"], method=per[i]["best6_short"], ploss=per[i]["best6_ploss"]) for i in per})

    m4ab = []
    for iid in ("L1", "L2", "F5"):
        m4ab.append(dict(id=iid, vals={v: ab[iid][v]["launch"] for v in ab[iid]},
                         cyc={v: ab[iid][v]["cyc_op"] for v in ab[iid]}))

    m5rows = []
    for iid in ("L1", "L2", "F5"):
        r = two[iid]
        ts, pl = r["ts"], r["ts"]["plan"]
        one = ab[iid]["b"]["launch"]   # variant b in M4's A/B; M5's session reran it at L1 and L2 (one_stage_rerun)
        rerun = {"L1": card["m5"]["m5-l1-b"]["launch"], "L2": card["m5"]["m5-l2-b"]["launch"]}.get(iid)
        m5rows.append(dict(id=iid, m1=pl["m1"], tau1=pl["tau1"], ploss=pl["p_loss"], found=ts["found"],
                           expected=pl["expected_survivors"], launch=ts["launch_s"], readback=ts["readback_s"],
                           stage2=ts["stage2_s"], solve=ts["solve_s"], model=ts["model_solve_s"], log_mb=pl["log_mb"],
                           survived=ts["secret_survived"], solved=ts["solved"], cyc_op=r["cyc_op"],
                           offline=card["ver"][{"L1": "m5-l1-s320", "L2": "m5-l2-s1152", "F5": "m5-f5-s1152"}[iid]],
                           one_stage=one, one_stage_rerun=rerun, cpu6=per[iid]["best6"], file=r["file"],
                           floor=r["ops"] * FLOOR_CYC / (r["minions"] * F_HZ)))
    res = card["m5"]["m5-l1-res192"]
    controls = [dict(step=nm, status=card["m5"][nm]["status"], expect=exp, what=what) for nm, exp, what in (
        ("m5-ovf", "FAIL", "every survivor log too small: the overflow is flagged and the run fails"),
        ("m5-negmask", "FAIL", "one tile's staircase shifted: both closed forms fail"),
        ("m5-negtau", "FAIL", "the kernel screens at τ1 + 2: the survivor oracle disagrees on every minion"),
        ("m5-lostlog", "FAIL", "the kernel logs into a spare area: the poisoned log fails the entries and stage 2"))]
    m1c = card["m1"]
    neg = [m1c[k]["status"] for k in ("m1-neg-drop", "m1-neg-dup", "m1-neg-mask")]
    seeds_ok = sum(1 for s in card["seeds"] if s["status"] == "PASS")
    seeds_solved = sum(1 for s in card["seeds"] if s["solved"])
    probes_ok = sum(1 for p in card["probes"] if p["status"] == "PASS")

    ladder_rows = []
    for iid in ("L1", "L2", "F5"):
        for p in card["series"][iid]:
            ladder_rows.append(dict(id=iid, ms=p["ms"], s=p["s"], note=p["note"], file=p["file"]))

    later = []
    for lab, r in (("M3, L1 (M1's kernel)", card["m3"]["L1"]), ("M3, L2 (M1's kernel)", card["m3"]["L2"]),
                   ("M4 b, L1", ab["L1"]["b"]), ("M4 b, L2", ab["L2"]["b"]),
                   ("M5 two-stage, L1 (m1 = 320)", two["L1"]), ("M5 two-stage, L2 (m1 = 1,152)", two["L2"]),
                   ("M5 two-stage, (256,5) (m1 = 1,152)", two["F5"])):
        later.append(dict(label=lab, cyc_op=r["cyc_op"], imb=r["imb"], launch=r["launch"],
                          floor=r["ops"] * FLOOR_CYC / (r["minions"] * F_HZ)))
    later.insert(4, dict(label="M4 b, (256,5), second half", cyc_op=ab["F5"]["b"]["cyc_op_halves"][1], imb=None,
                         launch=None, floor=None))

    L1, L2, F5 = (per[i] for i in ("L1", "L2", "F5"))
    mhz_runs = [r["mhz"] for r in (card["m3"]["L1"], card["m3"]["L2"], ab["L1"]["b"], ab["L2"]["b"], two["L1"], two["L2"],
                                   two["F5"])] + [x["mhz"] for x in ab["F5"]["b"]["runs"]]
    E = {e["id"]: e for e in energy}
    c3 = {r["run"]: r for r in cyc["runs"]}
    v = {
        # the answer
        "l1Solve": fmt_s(card_t["L1"]), "l2Solve": fmt_s(card_t["L2"]), "f5Solve": fmt_s(card_t["F5"]),
        "r1": rng(*(lambda xs: (min(xs), max(xs)))(list(r1.values()))),
        "r6": rng(*(lambda xs: (min(xs), max(xs)))(list(r6.values()))),
        "r16": rng(min(min(x) for x in r16.values()), max(max(x) for x in r16.values())),
        "rE": rng(min(e_board), max(e_board)), "rEhost": rng(min(e_host), max(e_host)),
        "eAll": f"{E['L1']['j_total']:.1f} · {E['L2']['j_total']:.1f} · {E['F5']['j_total']:.0f} J",
        "m3toM5": rng(*(lambda xs: (min(xs), max(xs)))([next(p["s"] for p in card["series"][i] if p["ms"] == "M3") / card_t[i]
                                                         for i in ("L1", "L2", "F5")])),
        "eL1": f"{E['L1']['j_total']:.1f} J", "eL2": f"{E['L2']['j_total']:.1f} J", "eF5": f"{E['F5']['j_total']:.0f} J",
        "m3L1": f"{card['m3']['L1']['launch']:.4f} s", "m3L2": f"{card['m3']['L2']['launch']:.4f} s",
        "cand": f"{sci(math.comb(512, 4))}–{sci(math.comb(256, 5))}",
        "geMs": fmt_s(grid["ge"][-1]["s"]),
        "l2cpu1": fmt_s(L2["one_core"]), "l2cpu6": fmt_s(L2["best6"]),
        "l2r1": x2(r1["L2"]) + "×", "l2r6": x2(r6["L2"]) + "×",
        "l2Found": f"{two['L2']['ts']['found']:,}",
        "dPredM3": f"{fmt_s(design['L1']['M3'])} and {fmt_s(design['L2']['M3'])}",
        "m3OverPred": f"{card['m3']['L1']['launch'] / design['L1']['M3']:.1f}×",
        "stepsOk": "", "nowait": card["nowait"]["status"],
        "seeds": f"{seeds_ok} of {len(card['seeds'])}", "seedsSolved": f"{seeds_solved}",
        "probes": f"{probes_ok} of {len(card['probes'])}",
        "knee": ", ".join(f"{k['cyc_op']:.0f}" for k in card["knee"]),
        "m1cycOff": f"{m1c['m1-l1-timing']['cyc_op']:.0f} and {m1c['m1-l2-timing']['cyc_op']:.0f}",
        "m1cycOn": f"{m1c['m1-l1']['cyc_op']:.0f} and {m1c['m1-l2']['cyc_op']:.0f}",
        "m2L1": fmt_s(card["m2full"]["launch"]), "m2imb": f"{card['m2full']['imb']:.2f}",
        "m3gapL1": f"{c3['m3-l1']['gap']:.2f}", "m3gapL2": f"{c3['m3-l2']['gap']:.2f}",
        "m3imbL1": f"{c3['m3-l1']['imbalance']:.2f}", "m3imbL2": f"{c3['m3-l2']['imbalance']:.2f}",
        "m3ovhL1": f"{c3['m3-l1']['overhead']:.2f}", "m3ovhL2": f"{c3['m3-l2']['overhead']:.2f}",
        "m3opc": f"{c3['m3-l1']['opcost']:.2f}", "cOp": f"{cyc['fitted']['C_OP_str']:.0f}",
        "eOut": f"{cyc['fitted']['E_OUT']:,.0f}",
        "waitL2": f"{c3['m3-l2']['mean']['wait']:.0f}", "waitL2b": f"{c3['m3-l2']['busiest']['wait']:,.0f}",
        "epiL1": f"{c3['m3-l1']['mean']['epi']:.0f}",
        "tilesBusy": f"{c3['m3-l1']['busiest_tiles']:,}", "tilesMed": f"{c3['m3-l1']['median_tiles']:,}",
        "abL1": f"{ab['L1']['m1']['launch']:.3f} → {ab['L1']['a']['launch']:.3f} → {ab['L1']['b']['launch']:.3f} s",
        "abL2": f"{ab['L2']['m1']['launch']:.3f} → {ab['L2']['a']['launch']:.3f} → {ab['L2']['b']['launch']:.3f} s",
        "cL1": f"{ab['L1']['c']['launch']:.3f} s", "cL2": f"{ab['L2']['c']['launch']:.3f} s",
        "cModelL1": f"{ab['L1']['c']['launch'] / ab['L1']['c']['j']['plan']['model_s']:.1f}",
        "cModelL2": f"{ab['L2']['c']['launch'] / ab['L2']['c']['j']['plan']['model_s']:.1f}",
        "f5h1cyc": f"{ab['F5']['b']['cyc_op_halves'][1]:,.0f}",
        "floorL2": fmt_s(m5rows[1]["floor"]), "floorL2one": fmt_s(ab["L2"]["b"]["ops"] * FLOOR_CYC / (1024 * F_HZ)),
        "floorF5": fmt_s(m5rows[2]["floor"]),
        "floorL2oneSt": fmt_s(floor_staged(ab["L2"]["b"]["j"])), "floorL1oneSt": fmt_s(floor_staged(ab["L1"]["b"]["j"])),
        "stagedPct": rng(*(lambda xs: (min(xs), max(xs)))([100 * (floor_staged(ab[i]["b"]["j"]) / (ab[i]["b"]["ops"] * FLOOR_CYC
                                                                / (1024 * F_HZ)) - 1) for i in ("L1", "L2")]), "%"),
        "l2two_cyc": f"{two['L2']['cyc_op']:.0f}", "l2launch": fmt_s(two["L2"]["launch"]), "f5two_cyc": f"{two['F5']['cyc_op']:.0f}",
        "resSolve": fmt_s(res["ts"]["solve_s"]), "resFound": sci(res["ts"]["found"]),
        "resLaunch": fmt_s(res["ts"]["launch_s"]), "l1twoLaunch": fmt_s(two["L1"]["ts"]["launch_s"]),
        "resCyc": f"{res['cyc_op']:,.0f}",
        "resKept": rng(*(lambda xs: (min(xs), max(xs)))([100 * kept_at(m1_, 0.4)[1] for m1_ in (192, 320)]), "%"),
        "resPloss": sci(res["ts"]["plan"]["p_loss"]), "resStage2": fmt_s(res["ts"]["stage2_s"]),
        "l1two_s": fmt_s(card_t["L1"]), "l1one_s": fmt_s(ab["L1"]["b"]["launch"]),
        "l2one": fmt_s(ab["L2"]["b"]["launch"]), "f5one": fmt_s(ab["F5"]["b"]["launch"]),
        "l2two_ratio": x2(ab["L2"]["b"]["launch"] / card_t["L2"]) + "×",
        "f5two_ratio": x2(ab["F5"]["b"]["launch"] / card_t["F5"]) + "×",
        "b6": rng(min(r6_b.values()), max(r6_b.values())),
        "cpuFirst": ", ".join(fmt_s(per[i]["one_core_first"]) for i in ("L1", "L2", "F5")),
        "cpuNow": ", ".join(fmt_s(per[i]["one_core"]) for i in ("L1", "L2", "F5")),
        "cpu1": ", ".join(fmt_s(per[i]["one_core"]) for i in ("L1", "L2", "F5")),
        "cpu6": ", ".join(fmt_s(per[i]["best6"]) for i in ("L1", "L2", "F5")),
        "cpu6scan": ", ".join(fmt_s(per[i]["t6_scan"]) for i in ("L1", "L2", "F5")),
        "cardAll": ", ".join(fmt_s(card_t[i]) for i in ("L1", "L2", "F5")),
        "screen1024": f"{fmt_s(L2['screen1024']['s'])} and {fmt_s(F5['screen1024']['s'])}",
        "screen1024loss": sci(L2["screen1024"]["ploss"]),
        "l1two6": fmt_s(L1["two_stage6"]["s"]),
        "idleW": f"{st.mean(e['idle_w'] for e in energy):.0f} W",
        "burstW": f"{min(min(e['board_w']) if isinstance(e['board_w'], list) else e['board_w'] for e in energy):.1f}–"
                  f"{max(max(e['board_w']) if isinstance(e['board_w'], list) else e['board_w'] for e in energy):.1f} W",
        "dieRise": f"{min(e['die'][0] for e in energy):.0f}–{max(e['die'][1] for e in energy):.0f} °C",
        "hostJ": f"{E['L1']['host'][0]:.1f}–{E['F5']['host'][1]:.0f} J",
        "gridSrc": grid["src"],
        "m3OverPredR": rng(card["m3"]["L1"]["launch"] / design["L1"]["M3"], card["m3"]["L2"]["launch"] / design["L2"]["M3"]),
        "hostBusy": rng(min(e["host_busy"] for e in energy), max(e["host_busy"] for e in energy), ""),
        "mhzRange": f"{min(mhz_runs):.0f}–{max(mhz_runs):.0f} MHz",
        "foundRatio": f"{min(r['found'] / r['expected'] for r in m5rows):.3f}–{max(r['found'] / r['expected'] for r in m5rows):.3f}×",
        "sp4": f"{grid['sp4']:.2f}",
        "smtU": f"{min(per[i]['smt_u'] for i in per):.2f}–{max(per[i]['smt_u'] for i in per):.2f}×",
    }
    # the numbers the body's prose quotes directly: fail here if a result file changes under them
    CHECKS = [
        ("L2 two-stage solve 0.323 s", abs(card_t["L2"] - 0.3226) < 0.001),
        ("(256,5) two-stage solve 1.52 s", abs(card_t["F5"] - 1.522) < 0.002),
        ("L1 two-stage solve 0.131 s", abs(card_t["L1"] - 0.1314) < 0.001),
        ("M3 L1 0.204 s, L2 0.807 s", abs(card["m3"]["L1"]["launch"] - 0.204) < 0.001
         and abs(card["m3"]["L2"]["launch"] - 0.806) < 0.002),
        ("variant b L1 0.130, L2 0.429, (256,5) 2.55 s", abs(ab["L1"]["b"]["launch"] - 0.130) < 0.001
         and abs(ab["L2"]["b"]["launch"] - 0.429) < 0.001 and abs(ab["F5"]["b"]["launch"] - 2.547) < 0.005),
        ("energy 5.0 / 16.6 / 89 J with idle", abs(E["L1"]["j_total"] - 5.0) < 0.05
         and abs(E["L2"]["j_total"] - 16.6) < 0.05 and abs(E["F5"]["j_total"] - 89.1) < 0.1),
        ("CPU 6T best 0.148 / 0.508 / 1.769 s", abs(L1["best6"] - 0.148) < 0.0006 and abs(L2["best6"] - 0.508) < 0.001
         and abs(F5["best6"] - 1.769) < 0.001),
        ("P(loss) 8.8e-5 at L1, 8.9e-5 at L2 and (256,5)", round(m5rows[0]["ploss"], 6) == 8.8e-05
         and round(m5rows[1]["ploss"], 6) == 8.9e-05 and round(m5rows[2]["ploss"], 6) == 8.9e-05),
        ("L2 has 1,381,776 row tiles and 32 column tiles", two["L2"]["j"]["geometry"]["row_tiles"] == 1381776
         and two["L2"]["j"]["geometry"]["nJ"] == 32),
        ("the plan has 4,096 blocks on 1,024 minions, 2,560 KB of scratchpad per shire",
         all(r["j"]["plan"]["blocks"] == 4096 and r["j"]["plan"]["minions"] == 1024
             and r["j"]["plan"]["scp_kb_device"] == 2560 for r in two.values())),
        ("the device open is about 0.18 s", all(abs(r["j"]["open_s"] - 0.18) < 0.015 for r in two.values())),
        ("the M3 gap to 270 cycles is 5.67x / 5.40x", abs(c3["m3-l1"]["gap"] - 5.67) < 0.01
         and abs(c3["m3-l2"]["gap"] - 5.40) < 0.01),
        ("P(loss) of the screens under 1e-4", all(r["ploss"] < 1e-4 for r in m5rows)
         and L2["best6_ploss"] < 1e-4 and F5["best6_ploss"] < 1e-4),
        ("every M5 two-stage run found the secret", all(r["solved"] and r["survived"] for r in m5rows)),
        ("the offline full oracle passed on all 1,024 minions",
         all(x.startswith("exact, all 1024") for x in card["ver"].values())),
        ("the controls failed as designed", all(c["status"] == c["expect"] for c in controls) and neg == ["FAIL"] * 3),
        ("the epilogue fit is 1,606 cycles per output tile", round(cyc["fitted"]["E_OUT"]) == 1606),
        ("the design's first M3 prediction 73 ms / 301 ms",
         abs(design["L1"]["M3"] - 0.073) < 0.001 and abs(design["L2"]["M3"] - 0.301) < 0.002),
        ("C(512,4) = 2.83e9, C(256,5) = 8.81e9", math.comb(512, 4) == 2829877120 and math.comb(256, 5) == 8809549056),
        ("GF(2) elimination at n = 512 in about 1.3 ms", abs(grid["ge"][-1]["s"] - 0.00126) < 0.0001),
        ("the (256,5) rails sum to its headline (J per solve)",
         abs(sum(E["F5"]["rails_j"].values()) - E["F5"]["j_over"]) < 0.05),
        ("aifoundry3's card at 600 MHz", all(abs(r["j"]["kernel"]["clock_mhz_est"] - 600) < 5 for r in two.values())),
        ("one minion: 428 and 411 cycles per op without the epilogue, 677 and 471 with it",
         [round(m1c[k]["cyc_op"]) for k in ("m1-l1-timing", "m1-l2-timing", "m1-l1", "m1-l2")] == [428, 411, 677, 471]),
        ("the resident screen: launch 0.127 s against 0.125 s streamed, 1,996 cycles per op, 6.7e6 survivors",
         abs(res["ts"]["launch_s"] - 0.1265) < 0.0005 and abs(two["L1"]["ts"]["launch_s"] - 0.1250) < 0.0005
         and round(res["cyc_op"]) == 1996 and abs(res["ts"]["found"] - 6.73e6) < 1e4),
        ("at eta 0.4 a screen at P(loss) < 1e-4 passes 83% (m1 192) and 57% (m1 320) of the candidates",
         kept_at(192, 0.4)[0] == -12 and kept_at(320, 0.4)[0] == -2 and round(100 * kept_at(192, 0.4)[1]) == 83
         and round(100 * kept_at(320, 0.4)[1]) == 57),
        ("L2's one-stage floor 0.283 s from the ops alone, 0.300 s with the staged rows; L1's 68 and 72 ms",
         abs(ab["L2"]["b"]["ops"] * FLOOR_CYC / (1024 * F_HZ) - 0.2831) < 0.0005
         and abs(floor_staged(ab["L2"]["b"]["j"]) - 0.2998) < 0.0005 and abs(floor_staged(ab["L1"]["b"]["j"]) - 0.0724) < 0.0005),
        ("one core's SMT uplift 0.94-1.09", abs(min(per[i]["smt_u"] for i in per) - 0.942) < 0.001
         and abs(max(per[i]["smt_u"] for i in per) - 1.090) < 0.001),
        ("M3's L1 busiest minion 1.64x the median, L2's 1.56x", abs(card["m3"]["L1"]["imb"] - 1.635) < 0.001
         and abs(card["m3"]["L2"]["imb"] - 1.564) < 0.001),
    ]
    bad = [name for name, ok in CHECKS if not ok]
    if bad:
        raise SystemExit("the page's prose no longer matches the data: " + "; ".join(bad))
    del v["stepsOk"]

    def strip(r):
        return {k: val for k, val in r.items() if k != "j"}

    data = dict(
        generated_by=rel(Path(__file__)),
        inst=inst, v=v, grid=grid, ladder=ladder, ladder_rows=ladder_rows, m4ab=m4ab, m5=m5rows,
        controls=controls, res192=dict(m1=res["ts"]["plan"]["m1"], tau1=res["ts"]["plan"]["tau1"],
                                      ploss=res["ts"]["plan"]["p_loss"], found=res["ts"]["found"],
                                      solve=res["ts"]["solve_s"], launch=res["ts"]["launch_s"],
                                      stage2=res["ts"]["stage2_s"]),
        cpu=dict(per=per, host=cpu["host"], src=cpu["src"], r1=r1, r6=r6, r16=r16, r6_b=r6_b),
        energy=energy, cycles=cyc, later=later,
        m1=[dict(step=k, **{kk: vv for kk, vv in strip(r).items() if kk in ("status", "launch", "cyc_op", "solved", "sum_c", "oracle", "file")})
            for k, r in card["m1"].items()],
        knee=card["knee"],
        checks=[name for name, _ in CHECKS],
    )
    out = HERE / "page.json"
    out.write_text(json.dumps(data, indent=1, default=float) + "\n")
    print(f"wrote {rel(out)}: {out.stat().st_size:,} bytes; {len(CHECKS)} prose checks pass")
    print("card:", v["cardAll"], "| one core:", v["cpu1"], "| 6T best:", v["cpu6"])
    print("ratios: one core", v["r1"], "| 6T", v["r6"], "| 16T extrapolated", v["r16"], "| energy", v["rE"],
          "(with host", v["rEhost"] + ")")


if __name__ == "__main__":
    main()
