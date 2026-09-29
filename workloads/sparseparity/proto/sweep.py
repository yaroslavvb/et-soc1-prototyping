"""sweep.py: the SP3 grid over the CPU prototypes (host CPU only; nothing here opens a card).

Runs ./spbits (C) and sp.py (numpy) over n in {32..512}, k in {2..5}, eta in {0..0.4} and appends one
JSON object per run to <out>/<task>.jsonl. Every run is a short chunk; before each chunk the driver runs
`et-who --check` (when it exists) and waits while anyone holds a card, so it stays out of the way of card
timing experiments on the same host. It stops when the CPU budget (children + self) is spent.

  python3 sweep.py ge|msearch|exh|gemm|gers|all --out DIR [--budget-s 5400] [--threads 4]

Use `nice -n 19` and keep --threads <= 4 on shared hosts.
"""
from __future__ import annotations

import argparse
import json
import math
import os
import resource
import shutil
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
NS = [32, 64, 128, 256, 512]
KS = [2, 3, 4, 5]
ETAS = [0.0, 0.1, 0.2, 0.3, 0.4]
SEEDS = list(range(1, 21))

# Single-thread exhaustive-scan cost per subset (ns) against W = ceil(m/64), measured on aifoundry1's
# i7-11700K (AVX-512 VPOPCNTQ); refined in the report from the exh runs themselves.
T_SUB_NS = [(1, 0.63), (4, 1.26), (16, 2.49), (32, 3.42), (64, 5.6), (128, 10.0)]
MS_PROBE_NS = 1.3  # extra ns per subset per probe in msearch


def t_sub_ns(W: int) -> float:
    pts = T_SUB_NS
    if W <= pts[0][0]:
        return pts[0][1]
    for (w0, t0), (w1, t1) in zip(pts, pts[1:]):
        if W <= w1:
            return t0 + (t1 - t0) * (W - w0) / (w1 - w0)
    (w0, t0), (w1, t1) = pts[-2], pts[-1]
    return t1 + (t1 - t0) * (W - w1) / (w1 - w0)


def cpu_used() -> float:
    a = resource.getrusage(resource.RUSAGE_SELF)
    b = resource.getrusage(resource.RUSAGE_CHILDREN)
    return a.ru_utime + a.ru_stime + b.ru_utime + b.ru_stime


class Runner:
    def __init__(self, out: str, budget_s: float, threads: int):
        self.out, self.budget, self.threads = out, budget_s, threads
        os.makedirs(out, exist_ok=True)
        self.have_etwho = shutil.which("et-who") is not None
        self.last_clear = 0.0  # time of the last clean et-who check
        self.log = open(os.path.join(out, "sweep.log"), "a")

    def say(self, *a):
        print(time.strftime("%H:%M:%S"), *a, file=self.log, flush=True)

    def guard(self, every_s: float = 15):
        """Wait while anyone holds an ET card on this host. Runs are short, so a chunk is any stretch of
        runs lasting under every_s seconds: re-check only when that much time has passed."""
        if not self.have_etwho or time.time() - self.last_clear < every_s:
            return
        waited = 0
        while True:
            r = subprocess.run(["et-who", "--check"], capture_output=True, text=True)
            if r.returncode == 0:
                if waited:
                    self.say(f"card free again after {waited} s")
                self.last_clear = time.time()
                return
            if waited == 0:
                self.say(f"pause: et-who --check rc={r.returncode}: {r.stdout.strip()[:200]}")
            time.sleep(30)
            waited += 30
            if waited > 4 * 3600:
                self.say("card held for 4 h; giving up")
                sys.exit(3)

    def over_budget(self) -> bool:
        return cpu_used() > self.budget

    def run(self, args: list[str], timeout: float = 1200) -> dict | None:
        self.guard()
        if self.over_budget():
            self.say("CPU budget spent; skipping", args)
            return None
        t0 = time.time()
        r = subprocess.run([os.path.join(HERE, args[0])] + args[1:], capture_output=True, text=True,
                           timeout=timeout)
        if r.returncode != 0:
            self.say("FAIL", args, r.stderr[-300:])
            return None
        d = json.loads(r.stdout.strip().splitlines()[-1])
        d["driver_wall_s"] = time.time() - t0
        return d

    def emit(self, task: str, d: dict):
        with open(os.path.join(self.out, f"{task}.jsonl"), "a") as f:
            f.write(json.dumps(d) + "\n")


def done_keys(out: str, task: str, keys: tuple) -> set:
    p = os.path.join(out, f"{task}.jsonl")
    s = set()
    if os.path.exists(p):
        for line in open(p):
            d = json.loads(line)
            s.add(tuple(d.get(k) for k in keys))
    return s


# ---------------------------------------------------------------- tasks
def task_ge(R: Runner):
    """Noiseless GF(2) elimination: the first m at which the n x m system has rank n, 20 seeds."""
    have = done_keys(R.out, "ge", ("n", "k", "seed"))
    for n in NS:
        for k in KS:
            for s in SEEDS:
                if (n, k, s) in have:
                    continue
                d = R.run(["spbits", "ge", f"n={n}", f"k={k}", f"seed={s}", f"mmax={n + 96}"])
                if d:
                    R.emit("ge", d)


def probes_for(m: int, eta: float) -> list[int]:
    if eta == 0:
        return list(range(max(2, m - 12), m + 7))
    lo, hi, q = 0.55 * m, 1.45 * m, 16
    return sorted({max(2, round(lo * (hi / lo) ** (i / (q - 1)))) for i in range(q)})


def ms_cost_s(n: int, k: int, eta: float, probes: list[int]) -> float:
    N = math.comb(n, k)
    W = (max(probes) + 63) // 64
    return N * (t_sub_ns(W) + MS_PROBE_NS * len(probes)) * 1e-9


def task_msearch(R: Runner, max_point_cpu_s: float):
    """Smallest m with 20/20 seeds solved by the exhaustive estimator (secret = unique best subset)."""
    import sp

    have = done_keys(R.out, "msearch", ("n", "k", "eta", "seed", "round"))
    prev = {}  # records from an earlier (interrupted) invocation, per point and round
    p = os.path.join(R.out, "msearch.jsonl")
    if os.path.exists(p):
        for line in open(p):
            d = json.loads(line)
            prev.setdefault((d["n"], d["k"], d["eta"], d["round"]), []).append(d)
    for n in NS:
        for k in KS:
            for eta in ETAS:
                m_mod = sp.m99_model(n, k, eta)
                probes = probes_for(m_mod, eta)
                cost = 20 * ms_cost_s(n, k, eta, probes)
                if cost > max_point_cpu_s:
                    R.say(f"msearch skip n={n} k={k} eta={eta}: projected {cost:.0f} CPU s")
                    R.emit("msearch_skipped", dict(n=n, k=k, eta=eta, m_model=m_mod, projected_cpu_s=cost))
                    continue
                for rnd in range(3):  # widen the probe window if the threshold falls at an edge
                    recs = list(prev.get((n, k, eta, rnd), []))
                    for s in SEEDS:
                        if (n, k, eta, s, rnd) in have:
                            continue
                        d = R.run(["spbits", "msearch", f"n={n}", f"k={k}", f"eta={eta}", f"seed={s}",
                                   f"threads={R.threads}", "probes=" + ",".join(map(str, probes))])
                        if d:
                            d["round"] = rnd
                            d["m_model"] = m_mod
                            R.emit("msearch", d)
                            recs.append(d)
                    if not recs:
                        break
                    ok = [all(r["true_count"][p] < r["min_wrong"][p] for r in recs) for p in range(len(probes))]
                    if ok[0]:
                        probes = sorted({max(2, round(p * 0.6)) for p in probes} | set(probes))[:40]
                    elif not ok[-1]:
                        probes = sorted(set(probes) | {round(p * 1.6) for p in probes})[-40:]
                    else:
                        break


def m99_empirical(out: str) -> dict:
    """(n, k, eta) -> smallest probe m at which all seeds succeed and stay successful."""
    p = os.path.join(out, "msearch.jsonl")
    res = {}
    if not os.path.exists(p):
        return res
    by = {}
    for line in open(p):
        d = json.loads(line)
        for m, t, w in zip(d["probes"], d["true_count"], d["min_wrong"]):
            by.setdefault((d["n"], d["k"], d["eta"]), {}).setdefault(m, {})[d["seed"]] = t < w
    for key, per_m in by.items():
        ms = sorted(per_m)
        best = None
        for m in reversed(ms):
            if len(per_m[m]) >= 20 and all(per_m[m].values()):
                best = m
            elif len(per_m[m]) >= 20:
                break
        if best is not None:
            res[key] = best
    return res


def task_exh(R: Runner, cap_single_s: float, cap_threaded_cpu_s: float):
    """Wall time of the exhaustive scan at the 99% sample count, 1 thread and R.threads threads."""
    import sp

    memp = m99_empirical(R.out)
    have = done_keys(R.out, "exh", ("n", "k", "eta", "threads", "seed"))
    for n in NS:
        for k in KS:
            for eta in ETAS:
                m = memp.get((n, k, eta)) or sp.m99_model(n, k, eta)
                W = (m + 63) // 64
                t1 = math.comb(n, k) * t_sub_ns(W) * 1e-9
                plan = []
                if t1 <= cap_single_s:
                    seeds = [1, 2, 3] if t1 < 2 else [1]
                    plan += [(1, s) for s in seeds]
                if t1 <= cap_threaded_cpu_s and t1 > 0.05:
                    plan += [(R.threads, 1)]
                if not plan:
                    R.emit("exh_skipped", dict(n=n, k=k, eta=eta, m=m, projected_single_s=t1))
                    continue
                for th, s in plan:
                    if (n, k, eta, th, s) in have:
                        continue
                    d = R.run(["spbits", "exh", f"n={n}", f"k={k}", f"eta={eta}", f"m={m}", f"seed={s}",
                               f"threads={th}"], timeout=max(600, 3 * t1))
                    if d:
                        d["m_source"] = "empirical" if (n, k, eta) in memp else "model"
                        R.emit("exh", d)


def task_exh_v3(R: Runner):
    """The same scan built for AVX2 + scalar POPCNT (no vector popcount), a few points."""
    have = done_keys(R.out, "exh_v3", ("n", "k", "eta"))
    import sp

    memp = m99_empirical(R.out)
    for n, k in [(128, 3), (128, 4), (256, 4), (512, 3)]:
        for eta in ETAS:
            if (n, k, eta) in have:
                continue
            m = memp.get((n, k, eta)) or sp.m99_model(n, k, eta)
            d = R.run(["spbits_v3", "exh", f"n={n}", f"k={k}", f"eta={eta}", f"m={m}", "seed=1", "threads=1"])
            if d:
                R.emit("exh_v3", d)


GEMM_MAC_PER_S = 5e10  # single-thread float32 OpenBLAS, planning value; the report refits it


def task_gemm(R: Runner, cap_s: float):
    """numpy float32 GEMM form of the same search, single thread, one seed at the 99% sample count."""
    import sp

    memp = m99_empirical(R.out)
    have = done_keys(R.out, "gemm", ("n", "k", "eta", "seed"))
    for n in NS:
        for k in KS:
            for eta in ETAS:
                m = memp.get((n, k, eta)) or sp.m99_model(n, k, eta)
                macs = sp.gemm_macs(n, k, m)
                proj = macs / GEMM_MAC_PER_S
                if proj > cap_s:
                    R.emit("gemm_skipped", dict(n=n, k=k, eta=eta, m=m, macs=macs, projected_s=proj))
                    continue
                if (n, k, eta, 1) in have:
                    continue
                R.guard()
                if R.over_budget():
                    return
                I = sp.gen(n, k, eta, m, 1)
                r = sp.gemm_solve(I)
                r.update(n=n, k=k, eta=eta, m=m, seed=1, threads=int(os.environ.get("OPENBLAS_NUM_THREADS", 0)),
                         found=list(r["found"]) if r.get("found") else None, secret=list(I.secret))
                R.emit("gemm", r)


def gers_plan(n: int, k: int, eta: float, extra: int = 8) -> tuple[int, float, float]:
    """Choose ncols minimising the expected elimination work; returns (ncols, expected trials, work units)."""
    best = None
    for nc in range(k + 1, n + 1):
        p_cols = math.comb(n - k, nc - k) / math.comb(n, nc)
        p_clean = (1 - eta) ** (nc + extra)
        trials = 1 / (p_cols * p_clean * 0.7)
        work = trials * (nc * (nc + extra) + nc * nc * (nc + extra) / 64 / 2)
        if best is None or work < best[2]:
            best = (nc, trials, work)
    return best


def task_gers(R: Runner, cap_s: float):
    """Noisy labels: Gaussian elimination on random sample (and feature) subsets."""
    import sp

    have = done_keys(R.out, "gers", ("n", "k", "eta", "seed"))
    for n in NS:
        for k in KS:
            for eta in [0.1, 0.2, 0.3]:
                nc, trials, work = gers_plan(n, k, eta)
                proj = work * 4.5e-9  # ~4.5 ns per work unit, from test runs on aifoundry2
                if proj > cap_s:
                    R.emit("gers_skipped", dict(n=n, k=k, eta=eta, ncols=nc, exp_trials=trials, projected_s=proj))
                    continue
                # pool: large enough that the verification (disagreements below the midpoint of eta*m and
                # m/2) also rejects every wrong weight-k candidate among thousands: twice the exhaustive m99
                m = max(256, 4 * (nc + 8), 2 * sp.m99_model(n, k, eta))
                for s in range(1, 6):
                    if (n, k, eta, s) in have:
                        continue
                    d = R.run(["spbits", "gers", f"n={n}", f"k={k}", f"eta={eta}", f"m={m}", f"seed={s}",
                               f"ncols={nc}", "extra=8", f"maxsec={cap_s}", "maxtrials=2000000000"])
                    if d:
                        d.update(exp_trials=trials, projected_s=proj)
                        R.emit("gers", d)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("task", choices=["ge", "msearch", "exh", "exh_v3", "gemm", "gers", "all"])
    ap.add_argument("--out", required=True)
    ap.add_argument("--budget-s", type=float, default=5400, help="CPU seconds (all threads) for this invocation")
    ap.add_argument("--threads", type=int, default=4)
    ap.add_argument("--ms-point-cpu-s", type=float, default=150)
    ap.add_argument("--exh-single-cap-s", type=float, default=60)
    ap.add_argument("--exh-threaded-cap-cpu-s", type=float, default=240)
    ap.add_argument("--gemm-cap-s", type=float, default=30)
    ap.add_argument("--gers-cap-s", type=float, default=20)
    a = ap.parse_args()
    a.threads = min(a.threads, 4)
    R = Runner(a.out, a.budget_s, a.threads)
    R.say("start", a.task, vars(a))
    tasks = ["ge", "msearch", "exh", "exh_v3", "gers", "gemm"] if a.task == "all" else [a.task]
    for t in tasks:
        R.say("task", t, f"cpu so far {cpu_used():.0f} s")
        if t == "ge":
            task_ge(R)
        elif t == "msearch":
            task_msearch(R, a.ms_point_cpu_s)
        elif t == "exh":
            task_exh(R, a.exh_single_cap_s, a.exh_threaded_cap_cpu_s)
        elif t == "exh_v3":
            task_exh_v3(R)
        elif t == "gemm":
            task_gemm(R, a.gemm_cap_s)
        elif t == "gers":
            task_gers(R, a.gers_cap_s)
    R.say("done", f"cpu {cpu_used():.0f} s")


if __name__ == "__main__":
    sys.path.insert(0, HERE)
    main()
