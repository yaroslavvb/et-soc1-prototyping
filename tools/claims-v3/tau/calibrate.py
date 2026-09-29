#!/usr/bin/env python3
"""TAU: calibrate the decision code on simulated replicates (no card): set the bands so that a true theory fails on
at most 5% of replicates (per theory, per card) while the rival (a fixed latency) still fails T3 on at least 95%.

    calibrate.py match --card C [--reps 3]                 the noise_w (W) per channel that matches the offline residual
    calibrate.py run --card C --reps R --seed0 S [--noise X] [--fixed-delay D] --out FILE.jsonl
    calibrate.py bands --card C --in FILE.jsonl [--write]  bands from true-model replicates (into prereg.json "calibrated")
    calibrate.py score --card C --in FILE.jsonl [...]      per-theory fail rates under the current prereg.json

A replicate is three simulated full passes of the card (stubs/simulate.py: the same simulated card as the dry-run
stubs, with the passes' real numbers, so their seeded burst order is the real one), pooled and scored by reduce.py's
analyse() and verdicts(). Each item's statistic (its signed deviation from the prediction, or its value for a
one-sided item) is kept, so that score can re-apply any bands without re-fitting. Run it at nice 19, one process.

Bands (PREREG.md, "Calibration"): for theory T with n deciding items on the card, z = the normal quantile of
1 - 0.05 / (2 n) (two-sided items and ranges) or 1 - 0.05 / n (one-sided); an item's calibrated band is the larger of
its prior band and |mean| + z * sd_up (one-sided: mean + z * sd_up; a range: [mean - z sd_up, mean + z sd_up] joined
with the prior range), with sd_up the replicates' sd times 1 + 1.645 / sqrt(2 (R - 1)) (its one-sided 95% upper
bound), rounded outward to 0.001 (bands under 0.05) or 0.005. The pooled P3b is set only by the rival: it stays at half
the predicted shift (the midpoint between T3 and the rival) unless the true replicates need more, which is reported.
"""
import argparse, json, math, os, shutil, statistics, sys, tempfile
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.dont_write_bytecode = True
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, "stubs"))
import reduce as rd  # noqa: E402
import simulate as sim  # noqa: E402

PASSES = {"aifoundry1-c1": [1, 2, 3], "aifoundry3": [101, 102, 103], "aifoundry2": [201, 202, 203]}
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
WORK = os.path.join(ROOT, "build", "claims-v3-dry", "tau-calib")


def kind_of(v):
    return "range" if isinstance(v["band"], list) else ("one" if str(v["predicted"]).startswith("<=") else "two")


def replicate(card, seed, noise=1.0, fixed_delay=None, pr=None, noise_w=None):
    pr = pr or prior_prereg()
    os.makedirs(WORK, exist_ok=True)
    d = tempfile.mkdtemp(prefix=f"{card}-{seed}-", dir=WORK)
    try:
        dirs = sim.simulate(d, card, PASSES[card], seed=seed, noise=noise, fixed_delay=fixed_delay, noise_w=noise_w)
        res = rd.analyse(dirs, pr, card)
    finally:
        shutil.rmtree(d, ignore_errors=True)
    V = rd.verdicts(res, pr, card)
    fits = {ch: {r: res[ch][r]["one_pass" if rd.dc.LAG[ch] else "fixed_delay"] for r in res.get(ch, {})} for ch in rd.tl.CHANNELS}
    return {"card": card, "seed": seed, "noise": noise, "fixed_delay": fixed_delay, "noise_w": noise_w,
            "items": {v["item"]: {"stat": v["stat"], "got": v["got"], "kind": kind_of(v), "theory": v["theory"],
                                  "decides": v["decides"]} for v in V},
            "fits": fits, "sp_pass_s": res["sp_pass_s"], "board_drift_per_s": res["board_drift_per_s"]}


def prior_prereg():
    pr = rd.prereg(); pr["calibrated"] = {}
    return pr


def cmd_match(a):
    """Choose each channel's noise_w so that the simulated P4a residual (10 Hz, the pooled fit) equals the offline
    residual of that card and channel: r^2 = r0^2 + (s / A)^2, with r0 the simulator's own residual at no noise."""
    off = json.load(open(os.path.join(HERE, "offline.json")))["cards"][a.card]
    target = {ch: off[ch]["one_pass" if rd.dc.LAG[ch] else "fixed_delay"]["rel_rms"] for ch in rd.tl.CHANNELS}
    def resid(noise, nw=None):
        rs = [replicate(a.card, 900 + i, noise=noise, noise_w=nw) for i in range(a.reps)]
        return {ch: float(np.mean([r["fits"][ch]["100"]["rel_rms"] for r in rs])) for ch in rd.tl.CHANNELS}
    r0 = resid(0.0)
    step = {"minion_w": 20.5, "sram_w": 7.9, "noc_w": 7.9, "board_avg_w": 22.0}      # the channel's typical step (W)
    nw = {ch: round(step[ch] * math.sqrt(max(target[ch] ** 2 - r0[ch] ** 2, 0.0)), 4) for ch in rd.tl.CHANNELS}
    for it in range(a.iters):
        r1 = resid(1.0, nw)
        for ch in rd.tl.CHANNELS:
            ex = r1[ch] ** 2 - r0[ch] ** 2; want = target[ch] ** 2 - r0[ch] ** 2
            if ex > 1e-10 and want > 0:
                nw[ch] = round(nw[ch] * math.sqrt(want / ex), 4)
        print(json.dumps({"iter": it, "residual_at_noise": {k: round(v, 5) for k, v in r1.items()}}), file=sys.stderr)
    r1 = resid(1.0, nw)
    print(json.dumps({"card": a.card, "target_rel_rms": {k: round(v, 5) for k, v in target.items()},
                      "no_noise_rel_rms": {k: round(v, 5) for k, v in r0.items()},
                      "matched_rel_rms": {k: round(v, 5) for k, v in r1.items()}, "noise_w": nw}, indent=1))


def cmd_run(a):
    pr = prior_prereg()
    with open(a.out, "a") as f:
        for i in range(a.reps):
            r = replicate(a.card, a.seed0 + i, a.noise, a.fixed_delay, pr)
            f.write(json.dumps(r) + "\n"); f.flush()
            bad = [k for k, v in r["items"].items() if v["stat"] is None]
            print(f"{a.card} seed {a.seed0 + i} noise {a.noise} fd {a.fixed_delay}: {len(r['items'])} items"
                  + (f", NO-DATA {bad}" if bad else ""), file=sys.stderr, flush=True)


def load_reps(files, card):
    R = []
    for fn in files:
        for l in open(fn):
            r = json.loads(l)
            if r["card"] == card:
                R.append(r)
    return R


def nd_quantile(p):
    return statistics.NormalDist().inv_cdf(p)


def ceil_to(x, step):
    return round(math.ceil(x / step - 1e-9) * step, 4)


def floor_to(x, step):
    return round(math.floor(x / step + 1e-9) * step, 4)


def cmd_bands(a):
    pr = prior_prereg()
    R = [r for r in load_reps(a.inp, a.card) if r["fixed_delay"] is None]
    if len(R) < 10:
        sys.exit(f"calibrate bands: {len(R)} true-model replicates of {a.card}; need >= 10")
    V0 = rd.verdicts({}, pr, a.card)             # every expected item with its prior band (stats all NO-DATA)
    prior = {v["item"]: v["band"] for v in V0}
    kinds = {}
    for r in R:
        for k, v in r["items"].items():
            kinds[k] = v
    n_t = {}
    for k, v in kinds.items():
        if v["decides"]:
            n_t[v["theory"]] = n_t.get(v["theory"], 0) + 1
    out, notes = {}, {}
    nrep = len(R); infl = 1 + 1.645 / math.sqrt(2 * (nrep - 1))
    for k, v in kinds.items():
        if not v["decides"] and not k.startswith(("P2", "P3")):
            continue
        xs = [r["items"][k]["stat"] for r in R if r["items"].get(k, {}).get("stat") is not None]
        if len(xs) < 10:
            notes[k] = f"only {len(xs)} replicates with data"; continue
        m, sd = float(np.mean(xs)), float(np.std(xs, ddof=1)) * infl
        n = n_t.get(v["theory"], 1)
        p = prior.get(k)
        if v["kind"] == "range":
            z = nd_quantile(1 - 0.05 / (2 * n))
            lo, hi = p if p else (m, m)
            out[k] = [floor_to(min(lo, m - z * sd), 0.005), ceil_to(max(hi, m + z * sd), 0.005)]
        elif v["kind"] == "one":
            z = nd_quantile(1 - 0.05 / n)
            q = m + z * sd; step = 0.001 if (p or 0) < 0.05 else 0.005
            out[k] = max(p, ceil_to(q, step))
        else:
            z = nd_quantile(1 - 0.05 / (2 * n))
            q = abs(m) + z * sd; step = 0.001 if (p or 0) < 0.05 else 0.005
            if k.startswith("P3b"):
                notes[k] = f"true replicates need {q:.4f} (mean {m:+.4f}, sd {sd:.4f}); the band stays at the prior {p} (the midpoint)"
                out[k] = p
                continue
            out[k] = max(p, ceil_to(q, step))
        if out[k] != p:
            notes[k] = f"prior {p} -> {out[k]} (mean {m:+.4f}, sd_up {sd:.4f}, z {z:.2f}, n {n})"
    cal = {"bands": out, "replicates": nrep, "noise": sorted({r["noise"] for r in R}), "items_per_theory": n_t,
           "sd_inflation": round(infl, 3), "source": [os.path.relpath(f, ROOT) for f in a.inp], "widened": notes}
    print(json.dumps(cal, indent=1))
    if a.write:
        p = os.path.join(HERE, "prereg.json"); full = json.load(open(p))
        full.setdefault("calibrated", {})[a.card] = cal
        json.dump(full, open(p, "w"), indent=1); open(p, "a").write("\n")
        print(f"written into {os.path.relpath(p, ROOT)} calibrated.{a.card}", file=sys.stderr)


def judge(r, pr, card):
    """A replicate's verdicts under pr's bands, from its stored statistics (no re-fit)."""
    out = {}
    for k, v in r["items"].items():
        s = v["stat"]
        b = rd.band_of(pr, card, k)
        if s is None or b is None:
            ok = None
        elif v["kind"] == "range":
            ok = b[0] - 1e-9 <= round(s, 4) <= b[1] + 1e-9
        elif v["kind"] == "one":
            ok = round(s, 4) <= b + 1e-9
        else:
            ok = abs(round(s, 4)) <= b + 1e-9
        out[k] = {"item": k, "theory": v["theory"], "decides": v["decides"], "got": v["got"], "stat": s, "band": b,
                  "verdict": "NO-DATA" if ok is None else ("PASS" if ok else "FAIL")}
    return list(out.values())


def cmd_score(a):
    pr = rd.prereg()
    if a.prior:
        pr["calibrated"] = {}
    groups = {}
    for r in load_reps(a.inp, a.card):
        groups.setdefault((r["noise"], r["fixed_delay"]), []).append(r)
    table = []
    for (noise, fd), R in sorted(groups.items(), key=lambda kv: (kv[0][1] is not None, kv[0][0])):
        th_fail = {t: 0 for t in ("T1", "T2", "T3", "T4")}; items = {}
        for r in R:
            V = judge(r, pr, a.card)
            T = rd.theories(V, pr, a.card)
            for t, s in T.items():
                th_fail[t] += s["status"].startswith(("falsified", "untested"))
            for v in V:
                if v["verdict"] == "FAIL":
                    items[v["item"]] = items.get(v["item"], 0) + 1
            if fd is not None:        # the rival: does T3 fail on the pooled P3b by itself?
                items["(P3b alone)"] = items.get("(P3b alone)", 0) + any(v["verdict"] == "FAIL" and v["item"].startswith("P3b") for v in V)
        row = {"model": "true" if fd is None else f"rival fixed {fd} s", "noise": noise, "replicates": len(R),
               "theory_fail_rate": {t: round(n / len(R), 3) for t, n in th_fail.items()},
               "item_fails": dict(sorted(items.items(), key=lambda kv: -kv[1]))}
        table.append(row)
        print(json.dumps(row))
    if a.out:                                 # one file for every card: each score call replaces its card's entry
        full = json.load(open(a.out)) if os.path.exists(a.out) else {}
        full["about"] = ("TAU calibration (calibrate.py score): per card, the rate at which each theory fails on "
                         "simulated replicates (three pooled full passes each) under the bands of prereg.json, for the "
                         "true model at noise k (the residual k times the card's offline one) and for the rival (the "
                         "rails a fixed 0.263 s late); item_fails counts the failing items. Replicates: "
                         "build/claims-v3-dry/tau-calib/*.jsonl (regenerated from the seeds in 'sources').")
        full.setdefault("cards", {})[a.card + (" (prior bands)" if a.prior else "")] = {
            "bands": "prior" if a.prior else "calibrated", "sources": [os.path.relpath(f, ROOT) for f in a.inp],
            "seeds": {os.path.basename(f): (lambda ss: f"{min(ss)}-{max(ss)} ({len(ss)})")(sorted({r["seed"] for r in load_reps([f], a.card)}))
                      for f in a.inp if load_reps([f], a.card)},
            "rows": table}
        json.dump(full, open(a.out, "w"), indent=1); open(a.out, "a").write("\n")


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sp = ap.add_subparsers(dest="cmd", required=True)
    m = sp.add_parser("match"); m.add_argument("--card", required=True); m.add_argument("--reps", type=int, default=3)
    m.add_argument("--iters", type=int, default=2)
    r = sp.add_parser("run"); r.add_argument("--card", required=True); r.add_argument("--reps", type=int, required=True)
    r.add_argument("--seed0", type=int, required=True); r.add_argument("--noise", type=float, default=1.0)
    r.add_argument("--fixed-delay", type=float); r.add_argument("--out", required=True)
    b = sp.add_parser("bands"); b.add_argument("--card", required=True); b.add_argument("--in", dest="inp", nargs="+", required=True)
    b.add_argument("--write", action="store_true")
    s = sp.add_parser("score"); s.add_argument("--card", required=True); s.add_argument("--in", dest="inp", nargs="+", required=True)
    s.add_argument("--prior", action="store_true", help="score with the prior bands instead of the calibrated ones")
    s.add_argument("--out")
    a = ap.parse_args()
    {"match": cmd_match, "run": cmd_run, "bands": cmd_bands, "score": cmd_score}[a.cmd](a)


if __name__ == "__main__":
    main()
