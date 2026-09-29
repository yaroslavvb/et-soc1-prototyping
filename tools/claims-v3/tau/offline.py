#!/usr/bin/env python3
"""TAU, offline: the rails' filter measured on committed data, and how well tools/ettelem/deconv.py undoes it.

    OMP_NUM_THREADS=1 nice -n 19 python3 tools/claims-v3/tau/offline.py [--quick] [--out tools/claims-v3/tau/offline.json]
    OMP_NUM_THREADS=1 nice -n 19 python3 tools/claims-v3/tau/offline.py --drift     # only the board_w drift table (P4d)

Data (no card): the 23 September catalogue and enercat sessions (aifoundry2, aifoundry3) and the version-3 full
catalogue (catfull, 25-26 September: aifoundry2, aifoundry3, aifoundry1's card 1), every burst with >= 4 s of idle
before it. Per card and channel (the three rails and the board's running average), bursts with a step above THR:
  1. the filter: tau and delay for two delay models, a fixed delay d (lag 0) and one SP pass plus d (lag 1);
  2. per-burst tau (lag 1, d held): its spread, so the block's precision can be predicted; rise and fall fitted
     apart; tau against step size (minion rail); tau per session;
  3. square recovery for each regularisation (none, a Gaussian of sigma, Tikhonov, total variation) against the raw
     reading and the published last-0.6 s / 0.94 split, on up to 300 bursts per channel (seeded): plateau, energy,
     edges, rise time, and the noise gain (the output's scatter away from the edges over the reading's scatter about
     the fitted model). The recovery uses each channel's own fitted tau and delay (two parameters over hundreds of
     bursts, so in-sample optimism is negligible); tau_by_session shows how far tau moves between sessions.
"""
import argparse, glob, json, os, sys, time
import numpy as np

sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import taulib as tl  # noqa: E402
dc = tl.dc

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
D = os.path.join(ROOT, "docs", "reports", "data")
V3 = os.path.join(D, "2026-09-25-claims-v3", "raw")
SESSIONS = {   # card -> {session: [dirs]}
    "aifoundry2": {"23sep": [f"{D}/2026-09-23-catalogue-aifoundry2", f"{D}/2026-09-23-enercat-aifoundry2"],
                   "v3": sorted(glob.glob(f"{V3}/aifoundry2/catfull/p[1-3][1-3]"))},
    "aifoundry3": {"23sep": [f"{D}/2026-09-23-catalogue-aifoundry3", f"{D}/2026-09-23-enercat-aifoundry3"],
                   "v3": sorted(glob.glob(f"{V3}/aifoundry3/catfull/p[1-3][1-3]"))},
    "aifoundry1-c1": {"v3": sorted(glob.glob(f"{V3}/aifoundry1-c1/catfull/p[1-3][1-3]"))},
}
THR = {"minion_w": 5.0, "sram_w": 1.5, "noc_w": 1.5, "board_avg_w": 5.0}
METHODS = ([("raw", 0), ("exact", 0)] + [("gauss", s) for s in (0.05, 0.1, 0.15, 0.2, 0.3, 0.5)]
           + [("tikhonov", l) for l in (0.01, 0.03, 0.1, 0.3, 1.0)] + [("tv", l) for l in (0.003, 0.01, 0.03, 0.1)])


def load_card(sessions):
    """Every session's directories, concatenated in time (sessions hours apart; windows never span a gap > 1 s)."""
    T, CH, B, SES = [], {k: [] for k in ("board_w",) + tl.CHANNELS}, [], []
    for name, dirs in sessions.items():
        for d in dirs:
            t, ch, bursts = tl.load_dir(d)
            T.append(t); [CH[k].append(ch[k]) for k in CH]
            B += [dict(b, session=name) for b in bursts]
    o = np.argsort(np.concatenate(T), kind="stable")
    t = np.concatenate(T)[o]; ch = {k: np.concatenate(v)[o] for k, v in CH.items()}
    return t, ch, sorted(B, key=lambda b: b["t_on"])


def card_report(card, sessions, quick):
    t, ch, bursts = load_card(sessions)
    idx, tp = dc.passes(t, ch)
    W0 = tl.windows(tp, bursts)
    g = np.diff(tp); g = g[g < 1.0]                     # the mean SP pass, gaps between sessions excluded
    rep = {"bursts": len(bursts), "windows": len(W0["on"]), "sp_pass_s": round(float(g.mean()), 4)}
    rng = np.random.default_rng(1)
    for k in tl.CHANNELS:
        y = ch[k][idx]
        lag = dc.LAG[k]
        A, _, _ = tl.fit(dc.eff_times(tp, lag, 0.0), y, W0, 1.05)
        W = tl.subset(W0, A > THR[k])
        r = {"n": int(len(W["on"])), "thr_w": THR[k]}
        r["fixed_delay"] = dict(zip(("tau_s", "d_s", "rel_rms"), tl.search(tp, y, W, 0)))
        r["one_pass"] = dict(zip(("tau_s", "d_s", "rel_rms"), tl.search(tp, y, W, 1, ds=(-0.10, 0.10))))
        m = r["one_pass"] if lag else r["fixed_delay"]
        tau, d = m["tau_s"], m["d_s"]
        te = dc.eff_times(tp, lag, d)
        pb = tl.per_burst_tau(te, y, W)
        q = np.percentile(pb, [10, 25, 50, 75, 90])
        r["per_burst_tau"] = {"p10_25_50_75_90": [round(float(v), 3) for v in q], "sd": round(float(pb.std()), 3),
                              "robust_sd": round(float((q[3] - q[1]) / 1.349), 3)}
        r["rise_fall_tau_s"] = tl.split_fit(te, y, W, tau)
        A, rel2, coefs = tl.fit(te, y, W, tau)
        r["step_w_median"] = round(float(np.median(A)), 2)
        if k == "minion_w":
            r["tau_by_step"] = {f"{lo:g}-{hi:g} W": [round(float(np.median(pb[(A >= lo) & (A < hi)])), 3), int(((A >= lo) & (A < hi)).sum())]
                                for lo, hi in ((5, 10), (10, 15), (15, 30)) if ((A >= lo) & (A < hi)).sum() >= 10}
        r["tau_by_session"] = {}
        for s in sessions:
            keep = np.array([b["session"] == s for b in W["b"]])
            if keep.sum() >= 10:
                Ws = tl.subset(W, keep)
                r["tau_by_session"][s] = dict(zip(("tau_s", "d_s", "rel_rms"), tl.search(tp, y, Ws, lag, ds=(-0.10, 0.10) if lag else (0.0, 0.4))))
        # recovery on at most 300 bursts (seeded), the fit's own tau and d
        sel = np.zeros(len(W["on"]), bool); sel[rng.choice(len(sel), min(len(sel), 120 if quick else 300), replace=False)] = True
        Wr, cr = tl.subset(W, sel), coefs[sel]
        r["recovery"] = {f"{mth}:{p:g}": tl.recovery(tp, y, Wr, cr, tau, lag, d, mth, p) for mth, p in METHODS
                         if not (quick and mth in ("tikhonov", "tv") and p not in (0.1, 0.01))}
        r["published_plateau_err"] = tl.published_plateau(tp, y, Wr, cr)
        cands = {m_: v for m_, v in r["recovery"].items() if not m_.startswith("raw")}
        r["best"] = min(cands, key=lambda m_: cands[m_]["rms"])
        rep[k] = r
        print(f"{card} {k}: n={r['n']} fixed {r['fixed_delay']} one-pass {r['one_pass']} per-burst {r['per_burst_tau']} "
              f"rise/fall {r['rise_fall_tau_s']} best {r['best']} {cands[r['best']]}", flush=True)
    return rep


def drift_table(card, sessions, lo=15.0, hi=40.0):
    """board_w's in-burst drift (taulib.board_drift, per s, of the step) on the bursts with a board step of lo-hi W
    and >= 4 s of idle before them: the input's squareness under which T1 held offline (PREREG.md, P4d)."""
    t, ch, bursts = load_card(sessions)
    idx, tp = dc.passes(t, ch)
    bw = ch["board_w"][idx]
    keep = []
    for i, b in enumerate(bursts):
        if i and b["t_on"] - bursts[i - 1]["t_off"] < 4.0:
            continue
        pl = (tp >= b["t_on"] + 0.5) & (tp <= b["t_off"]); idle = (tp >= b["t_on"] - 2.0) & (tp < b["t_on"] - 0.2)
        if pl.sum() >= 6 and idle.sum() >= 3 and lo <= bw[pl].mean() - bw[idle].mean() < hi:
            keep.append(b)
    dr = tl.board_drift(tp, bw, keep)
    q = np.percentile(dr, [10, 25, 50, 75, 90]) if len(dr) else []
    return {"n": int(len(dr)), "step_w": [lo, hi], "p10_25_50_75_90": [round(float(v), 4) for v in q]}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default=os.path.join(os.path.dirname(os.path.abspath(__file__)), "offline.json"))
    ap.add_argument("--quick", action="store_true", help="fewer bursts and regularisations in the recovery table")
    ap.add_argument("--cards", default=",".join(SESSIONS))
    ap.add_argument("--drift", action="store_true", help="print only the board_w in-burst drift per card (P4d) as JSON")
    a = ap.parse_args()
    if a.drift:
        print(json.dumps({c: drift_table(c, SESSIONS[c]) for c in a.cards.split(",")}, indent=1)); return
    t0 = time.time()
    out = {"generated_by": "tools/claims-v3/tau/offline.py", "quick": a.quick,
           "sources": {c: {s: [os.path.relpath(d, ROOT) for d in v] for s, v in SESSIONS[c].items()} for c in SESSIONS},
           "cards": {}}
    for c in a.cards.split(","):
        out["cards"][c] = card_report(c, SESSIONS[c], a.quick)
    out["seconds"] = round(time.time() - t0, 1)
    json.dump(out, open(a.out, "w"), indent=1)
    print(f"wrote {a.out} in {out['seconds']} s")


if __name__ == "__main__":
    main()
