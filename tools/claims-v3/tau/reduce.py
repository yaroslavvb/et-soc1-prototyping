#!/usr/bin/env python3
"""TAU: the block's helper and its pre-registered decision code (README.md; PREREG.md; prereg.json).

    reduce.py env --card C --pass P --mode full|smoke   shell assignments for block.sh (refuses a card or pass it may not run)
    reduce.py wincheck TEL --kind K --stop-c 90          one window's telemetry: ok / hot (exit 3) / clock, starved, notemp, nosp, empty (1)
    reduce.py winrec --out DIR ...                       records one window (windows.jsonl, bursts.jsonl, runs.jsonl)
    reduce.py check-pass DIR                             the pass check at the end of a block (check.json; exit 0 = ok)
    reduce.py report DIR [DIR ...] [--out FILE]          the verdicts, over the full, ok passes of one card (prereg.json)
"""
import argparse, json, math, os, random, sys
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.dont_write_bytecode = True
sys.path.insert(0, HERE)
import taulib as tl  # noqa: E402
dc = tl.dc
KINDS = {"minion_w": ("M", "H"), "sram_w": ("D",), "noc_w": ("D",), "board_avg_w": ("M", "H", "D")}
RAILS = ("minion_w", "sram_w", "noc_w")
# which theory each item tests (PREREG.md); "context" items decide nothing
THEORY = {"P0": "context", "P1": "T2", "P2a": "T3", "P2b": "T3", "P2c": "T3", "P3": "T3", "P3b": "T3",
          "P4a": "T1", "P4b": "T1", "P4c": "T1", "P4d": "context",
          "P5a": "T4", "P5b": "T4", "P5c": "T4", "P5d": "T4", "P5e": "T4", "P6": "T4"}
EPS = 1e-9


def cfg():
    return json.load(open(os.path.join(HERE, "tau.json")))


def prereg():
    return json.load(open(os.path.join(HERE, "prereg.json")))


def schedule(c, mode, pass_):
    """The pass's windows: [rate, kind, secs, sampler seconds]. In a full pass the leading idle window stays first and
    the bursts are put in a seeded order (tau.json shuffle_seed + pass), so that the sampler rate and the burst kind
    are not tied to the position in the pass (the die warms through a pass)."""
    sched = [list(e) + [c["sampler_seconds"]] * (4 - len(e)) for e in c["schedules"][mode]]
    if c.get("shuffle", {}).get(mode):
        k = 0
        while k < len(sched) and sched[k][1] == "idle":
            k += 1
        rest = sched[k:]
        random.Random(c["shuffle_seed"] + pass_).shuffle(rest)
        sched = sched[:k] + rest
    return sched


def cmd_env(a):
    c = cfg()
    if a.card == "aifoundry1-c0":
        sys.exit("tau: aifoundry1 card 0 is never used")
    if a.card not in c["cards"]:
        sys.exit(f"tau: {a.card} is not a TAU card ({', '.join(c['cards'])})")
    cc = c["cards"][a.card]
    lo, hi = cc["passes"]
    if not lo <= a.pass_ <= hi:
        sys.exit(f"tau: pass {a.pass_} is not a {cc['role']} pass on {a.card} ({lo}-{hi})")
    if cc.get("needs_env") and os.environ.get(cc["needs_env"]) != "1" and not os.environ.get("V3_DRY"):
        sys.exit(f"tau: {a.card} runs only with {cc['needs_env']}=1 (after DV2 ends)")
    sched = schedule(c, a.mode, a.pass_)
    for rate, kind, secs, sws in sched:
        if rate not in (50, 100) or sws > c["timeout_s"] - 0.5 or sws * 1000 / rate < 20:
            sys.exit(f"tau: schedule entry {rate} {kind} {secs} {sws}: 50 or 100 ms, a sampler of at most "
                     f"{c['timeout_s'] - 0.5} s and at least 20 lines")
        if kind == "idle":
            continue
        need = c["pre_burst_s"] + c["setup_allow_s"] + secs + c["post_burst_min_s"]
        if kind not in c["bursts"] or need > sws or c["timeout_s"] - need < 0.3:
            sys.exit(f"tau: schedule entry {rate} {kind} {secs}: a burst must be M/H/D and leave pre + setup + burst + "
                     f"post ({need:.1f} s) inside the sampler's {sws} s, with >= 0.3 s for the sampler's start")
    q = lambda v: "'" + str(v).replace("'", "") + "'"
    out = [f"TAU_ROLE={q(cc['role'].split()[0])}", f"TAU_DEV={cc['device']}", f"TAU_EXP={'tau' if a.mode == 'full' else 'tau-smoke'}",
           f"T_TIMEOUT={c['timeout_s']}", f"T_FIRST_MAX={c['first_line_max_s']}", f"T_PRE={c['pre_burst_s']}",
           f"T_SETUP={c['setup_allow_s']}", f"T_POST={c['post_burst_min_s']}",
           f"T_ATTEMPTS={c['sampler_attempts']}", f"T_DRAIN_AFTER={c['drain_after_failed_starts']}",
           f"T_A1_STOP_FAILS={c['a1_stop_after_failed_starts']}", f"T_RETRY_WAIT={c['sampler_retry_wait_s']}",
           f"T_WALL_MAX={c['window_wall_max_s']}", f"T_BURST_TRIES={c['burst_tries']}", f"T_STOP_C={c['stop_c']}",
           f"T_START_MAX_C={c['start_max_c']}",
           "SCHED=(" + " ".join(q(f"{r} {k} {s} {w}") for r, k, s, w in sched) + ")",
           "TAU_ORDER=" + q(" ".join(f"{k}{s:g}@{r}" for r, k, s, w in sched if k != "idle")),
           "BURST_COMMON=(" + " ".join(q(x) for x in c["burst_common"]) + ")"]
    out += [f"BURST_{k}=(" + " ".join(q(x) for x in v) + ")" for k, v in c["bursts"].items()]
    print("\n".join(out))


def cmd_wincheck(a):
    """Never crashes on a malformed line: a window without every field it needs is a bad window, not an ok one."""
    try:
        rows = tl.jsonl(a.tel)
    except Exception as e:  # a torn line
        print(json.dumps({"n": 0, "status": "unreadable", "error": repr(e)[:200]})); sys.exit(1)
    r = {"n": len(rows)}
    if len(rows) < 20:
        r["status"] = "empty"; print(json.dumps(r)); sys.exit(1)
    def die(s):
        v = (s.get("temp_c") or {}).get("minshire")
        return v[0] if isinstance(v, list) and v and isinstance(v[0], (int, float)) else None
    c = [die(s) for s in rows]
    cv = [x for x in c if x is not None]
    mhz = [(s.get("mhz") or {}).get("minion") for s in rows]
    took = [s.get("took_ms", 0) or 0 for s in rows]
    nosp = sum(not all(isinstance((s.get("sp") or {}).get(k), list) for k in RAILS) or
               not isinstance((s.get("sp") or {}).get("board_avg_w"), (int, float)) or
               not isinstance(s.get("board_w"), (int, float)) or not isinstance(s.get("t_ms"), (int, float)) for s in rows)
    r.update(max_c=max(cv) if cv else None, die_mean=float(np.median(cv)) if cv else None, die_last=cv[-1] if cv else None,
             notemp=len(c) - len(cv), mhz_off=sum(m != 600 for m in mhz), took_med=float(np.median(took)), nosp=nosp)
    r["status"] = ("hot" if cv and max(cv) >= a.stop_c else "notemp" if r["notemp"] else "clock" if r["mhz_off"]
                   else "starved" if r["took_med"] > 60 else "nosp" if nosp else "ok")
    print(json.dumps(r))
    sys.exit({"ok": 0, "hot": 3}.get(r["status"], 1))


def cmd_winrec(a):
    rec = {k: getattr(a, k) for k in ("win", "rate", "kind", "secs", "sampler_s", "try_", "fails", "t_launch", "t_first",
                                      "t_burst", "burst_rc", "launches", "status")}
    rec["start_ms"] = a.t_first - a.t_launch if a.t_first else None
    try:
        rec["check"] = json.loads(a.check) if (a.check or "").startswith("{") else (a.check or "")
    except ValueError:
        rec["check"] = a.check
    with open(os.path.join(a.out, "windows.jsonl"), "a") as f:
        f.write(json.dumps(rec) + "\n")
    lines = []
    if a.kind != "idle" and os.path.exists(a.burst_out):
        for l in open(a.burst_out):
            if l.startswith("ENERCAT {"):
                try:
                    lines.append(json.loads(l[8:]))
                except ValueError:
                    pass
    if lines:
        with open(os.path.join(a.out, "runs.jsonl"), "a") as f:
            for l in lines:
                f.write(json.dumps(dict(l, win=a.win, kind=a.kind)) + "\n")
        b = {"win": a.win, "kind": a.kind, "secs": a.secs, "rate_ms": a.rate, "t_on_ms": min(l["t_start_ms"] for l in lines),
             "t_off_ms": max(l["t_end_ms"] for l in lines), "launches": len(lines), "rc": a.burst_rc, "status": a.status}
        with open(os.path.join(a.out, "bursts.jsonl"), "a") as f:
            f.write(json.dumps(b) + "\n")
    st = rec["start_ms"]
    print(f"window {a.win}: {a.kind} {a.secs:g} s @ {a.rate} ms, sampler start {st if st is not None else '-'} ms "
          f"(try {a.try_}, {a.fails} failed), {len(lines)} launches, {a.status}")


def load(dirs):
    """The bursts of one or more pass directories of one card, on one pass grid. A burst whose window was not ok stays
    in the list (its power is real) but is marked, and never fitted."""
    T, CH, B = [], {}, []
    for d in dirs:
        t, ch, _ = tl.load_dir(d)
        T.append(t); [CH.setdefault(k, []).append(v) for k, v in ch.items()]
        for b in tl.jsonl(os.path.join(d, "bursts.jsonl")):
            B.append({"t_on": b["t_on_ms"] / 1e3, "t_off": b["t_off_ms"] / 1e3, "kind": b["kind"], "secs": b["secs"],
                      "rate_ms": b["rate_ms"], "ok": b["status"] == "ok", "pass_dir": os.path.basename(os.path.normpath(d))})
    t = np.concatenate(T); o = np.argsort(t, kind="stable")
    ch = {k: np.concatenate(v)[o] for k, v in CH.items()}
    idx, tp = dc.passes(t[o], ch)
    return tp, {k: v[idx] for k, v in ch.items()}, sorted(B, key=lambda b: b["t_on"])


def select(W, ch, rate, ok=True):
    keep = np.array([b["kind"] in KINDS[ch] and b["rate_ms"] == rate and (b["ok"] or not ok) for b in W["b"]])
    return tl.subset(W, keep) if keep.any() else None


def pass_period(tp, rate_windows):
    """The mean SP pass under each sampler rate: passes per second inside the windows of that rate."""
    out = {}
    for rate, spans in rate_windows.items():
        n = dur = 0
        for lo, hi in spans:
            k = np.flatnonzero((tp >= lo) & (tp <= hi))
            if len(k) > 5:
                n += len(k) - 1; dur += tp[k[-1]] - tp[k[0]]
        out[rate] = round(dur / n, 4) if n else None
    return out


def analyse(dirs, prereg=None, card=None):
    tp, y, bursts = load(dirs)
    W0 = tl.windows(tp, bursts, max_gap=8.0)          # the sampler restarts between windows (a failed start: ~6 s)
    res = {"passes": [os.path.basename(os.path.normpath(d)) for d in dirs], "bursts": len(bursts),
           "bursts_ok": sum(b["ok"] for b in bursts), "fitted": len(W0["on"])}
    spans = {}                     # inside a sampler window: from 2 s before each burst to 3 s after it
    for b in bursts:
        spans.setdefault(b["rate_ms"], []).append((b["t_on"] - 2.0, b["t_off"] + 3.0))
    res["sp_pass_s"] = pass_period(tp, spans)
    # the input's squareness: board_w's in-burst drift (per s, of the step) on the 20 W bursts (PREREG.md, P4d)
    dr = tl.board_drift(tp, y["board_w"], [b for b in bursts if b["ok"] and b["kind"] == "M"])
    res["board_drift_per_s"] = {"M": round(float(np.median(dr)), 4) if len(dr) else None, "n": int(len(dr))}
    ft = (prereg or {}).get("tau_s", {}).get(card, {})
    for ch in tl.CHANNELS:
        lag = dc.LAG[ch]; r = {}
        for rate in (100, 50):
            W = select(W0, ch, rate)
            if W is None:
                continue
            q = {"n": int(len(W["on"]))}
            q["fixed_delay"] = dict(zip(("tau_s", "d_s", "rel_rms"), tl.search(tp, y[ch], W, 0, ds=(-0.1, 0.6))))
            q["one_pass"] = dict(zip(("tau_s", "d_s", "rel_rms"), tl.search(tp, y[ch], W, 1, ds=(-0.2, 0.2))))
            m = q["one_pass"] if lag else q["fixed_delay"]
            te = dc.eff_times(tp, lag, m["d_s"])
            if rate == 100:
                q["rise_fall_tau_s"] = tl.split_fit(te, y[ch], W, m["tau_s"], stat=np.mean) if len(W["on"]) >= 3 else None
                pb = tl.per_burst_tau(te, y[ch], W)
                q["per_burst_tau"] = [round(float(v), 3) for v in pb]
                q["by_kind_tau"] = {k: round(float(np.median(pb[[b["kind"] == k for b in W["b"]]])), 3)
                                    for k in KINDS[ch] if any(b["kind"] == k for b in W["b"])}
                q["per_pass"] = {}
                for p in res["passes"]:
                    keep = np.array([b["pass_dir"] == p for b in W["b"]])
                    if keep.sum() >= 2:
                        q["per_pass"][p] = dict(zip(("tau_s", "d_s", "rel_rms"), tl.search(tp, y[ch], tl.subset(W, keep), lag, ds=(-0.2, 0.2) if lag else (-0.1, 0.6))))
                # the deconvolution with the FROZEN tau (prereg), not this block's fit: per burst length
                tau_f = ft.get(ch, m["tau_s"])
                A_free = tl.fit(te, y[ch], W, m["tau_s"])[0]
                q["deconv_frozen_tau_s"] = tau_f
                for name, mth, par in (("gauss0.1", "gauss", 0.1), ("tv0.03", "tv", 0.03)):
                    by = {}
                    for L in sorted({b["secs"] for b in W["b"]}):
                        keep = np.array([b["secs"] == L for b in W["b"]])
                        Ws = tl.subset(W, keep)
                        _, _, cf = tl.fit(dc.eff_times(tp, lag, 0.0), y[ch], Ws, tau_f)
                        rec = tl.recovery(tp, y[ch], Ws, cf, tau_f, lag, 0.0, mth, par)
                        rec["plateau_vs_free_fit"] = round(float(np.median((1 + np.array(rec_plateaus(tp, y[ch], Ws, cf, tau_f, lag, mth, par))) * cf[:, 2] / A_free[keep] - 1)), 4)
                        by[str(float(L))] = rec
                    q[f"recovery_{name}"] = by
                q["published_err"] = {}
                for L in sorted({b["secs"] for b in W["b"]}):
                    keep = np.array([b["secs"] == L for b in W["b"]])
                    Ws = tl.subset(W, keep)
                    z = np.zeros(int(keep.sum()))
                    q["published_err"][str(float(L))] = tl.published_plateau(tp, y[ch], Ws, np.c_[z, z, A_free[keep], z])
            r[str(rate)] = q
        res[ch] = r
    return res


def rec_plateaus(tp, y, W, cf, tau, lag, mth, par, grid=0.05):
    """Each burst's deconvolved plateau error (the recovery() measure, per burst), for the comparison with the free fit."""
    te_all = dc.eff_times(tp, lag, 0.0); out = []
    for i, c in enumerate(cf):
        a, b = W["on"][i], W["off"][i]
        idx = np.flatnonzero((te_all >= a - tl.LEAD) & (tp <= tp[W["idx"][i, -1]]))
        te = te_all[idx]
        x = dc.regularized(te, y[idx], tau, par, l1=True) if mth == "tv" else dc.inverse(te, y[idx], tau)
        g, x = dc.to_grid(te, x, grid, par if mth == "gauss" else 0.0)
        pl = (g >= a + 0.4) & (g < b - 0.4)
        out.append(float(np.mean(x[pl] - c[0] - c[1] * (g[pl] - a)) / c[2] - 1))
    return out


def cmd_check(a):
    runs = tl.jsonl(os.path.join(a.dir, "bursts.jsonl"))
    wins = tl.jsonl(os.path.join(a.dir, "windows.jsonl"))
    kinds = {}
    for w in wins:
        if w["kind"] != "idle":
            k = kinds.setdefault(f"{w['kind']}@{w['rate']}", [0, 0]); k[1] += 1; k[0] += w["status"] == "ok"
    st = [w["start_ms"] for w in wins if w.get("start_ms") is not None]
    chk = {"windows": len(wins), "bursts_ok": sum(b["status"] == "ok" for b in runs), "by_kind": kinds,
           "sampler": {"starts_ok": len(st), "failed_starts": sum(w.get("fails", 0) for w in wins),
                       "late_starts": sum(w["status"] == "late_start" for w in wins),
                       "start_ms_median": float(np.median(st)) if st else None, "start_ms_max": max(st) if st else None},
           "die_c_start": next((w["check"].get("die_mean") for w in wins if isinstance(w.get("check"), dict)), None),
           "die_c_end": next((w["check"].get("die_last") for w in reversed(wins) if isinstance(w.get("check"), dict)), None)}
    ok = bool(kinds) and all(v[0] >= 1 for v in kinds.values())
    try:
        res = analyse([a.dir])
        fits = {}
        for ch in tl.CHANNELS:
            for rate in ("100", "50"):                   # the 10 Hz fit where there is one (a smoke has D at 20 Hz only)
                if rate in res.get(ch, {}):
                    fits[ch] = dict(res[ch][rate]["one_pass" if dc.LAG[ch] else "fixed_delay"], rate_ms=int(rate)); break
        chk["fits"] = fits; chk["sp_pass_s"] = res["sp_pass_s"]; chk["board_drift_per_s"] = res["board_drift_per_s"]
        chk["rel_rms_max"] = max(f["rel_rms"] for f in fits.values())
        ok = ok and len(fits) == len(tl.CHANNELS) and chk["rel_rms_max"] < 0.05 and all(0.3 < f["tau_s"] < 1.8 for f in fits.values())
    except Exception as e:     # a check that cannot fit says so; the data stay for the report
        chk["fit_error"] = repr(e); ok = False
    chk["status"] = "ok" if ok else "fail"
    json.dump(chk, open(os.path.join(a.dir, "check.json"), "w"), indent=1)
    t = chk.get("fits", {}); s = chk["sampler"]
    print(f"{chk['bursts_ok']} bursts ok; " + " ".join(f"{k} {v[0]}/{v[1]}" for k, v in kinds.items())
          + "; tau " + " ".join(f"{k.split('_')[0]} {v['tau_s']:.2f}" for k, v in t.items())
          + f"; sampler starts {s['starts_ok']} ok {s['failed_starts']} failed, median {s['start_ms_median']} ms max {s['start_ms_max']} ms"
          + f"; die {chk['die_c_start']}-{chk['die_c_end']} C; {chk['status']}")
    sys.exit(0 if ok else 1)


# ---------------------------------------------------------------------------------------------------------------
# The decision code

def expected_items(card, pr, c=None):
    """Every item the full schedule should produce on this card, in report order (a missing one is NO-DATA)."""
    c = c or cfg()
    full = [list(e) for e in c["schedules"]["full"]]
    secs = {ch: sorted({float(s) for r, k, s, *_ in full if k in KINDS[ch] and r == 100}) for ch in tl.CHANNELS}
    it = ["P0 SP pass under a 10 Hz sampler", "P0 SP pass under a 20 Hz sampler"]
    for ch in tl.CHANNELS:
        it += [f"P1 tau {ch}", f"P4a residual {ch}", f"P4b rise=fall {ch}"]
        it += [f"P2a one-pass extra d {ch}", f"P2b fixed d = pass {ch}", f"P3 20 Hz fixed d = 20 Hz pass {ch}"] if dc.LAG[ch] else [f"P2c board_avg d {ch}"]
        if ch == "minion_w":
            it += ["P4c tau M = H (step size)"]
        for L in secs[ch]:
            it += [f"P5{x} {n} {ch} {L}s" for x, n in (("a", "plateau"), ("b", "energy"), ("c", "edges"), ("d", "flat scatter"), ("e", "plateau vs free fit"))]
        rng = pr["published_err"].get(f"{card}:{ch}", pr["published_err"]["default"])
        it += [f"P6 published split {ch} {L}s" for L in secs[ch] if str(L) in rng]
    it += ["P3b d shift 20-10 Hz, mean of the rails", "P4d board_w in-burst drift (M bursts)"]
    return it


def prior_band(pr, card, item):
    """An item's prior band (prereg.json "bands", or its range), before any calibration."""
    B = pr["bands"]; w = item.split(); p = w[0]
    ch = next((x for x in w if x.endswith("_w")), None)
    a1s = (card, ch) == ("aifoundry1-c1", "sram_w")
    if p == "P6":
        rng = pr["published_err"].get(f"{card}:{ch}", pr["published_err"]["default"])
        return rng.get(w[-1][:-1])
    if p == "P3b":
        P = pr["pass_s"][card]
        return round((P["50"] - P["100"]) / 2, 3)          # the midpoint between T3 and the rival (no shift)
    if p == "P4d":
        return pr["board_drift_per_s"][card]
    return {"P0": B["pass"], "P1": B["tau_a1c1_sram"] if a1s else B["tau"],
            "P4a": B["rel_rms_a1c1_sram"] if a1s else B["rel_rms"], "P4b": B["rise_fall"], "P4c": B["m_vs_h"],
            "P2a": B["extra_d"], "P2b": B["d_vs_pass"], "P3": B["d_vs_pass"], "P2c": B["extra_d"],
            "P5a": B["plateau"], "P5b": B["energy"], "P5c": B["edge_s"], "P5d": B["rms_flat"], "P5e": B["plateau"]}[p]


def band_of(pr, card, item, prior=None):
    """The band an item is judged by: the calibrated one (prereg.json "calibrated") where given, else the prior."""
    b = pr.get("calibrated", {}).get(card, {}).get("bands", {}).get(item)
    return b if b is not None else (prior if prior is not None else prior_band(pr, card, item))


def verdicts(res, pr, card):
    """Every registered prediction (PREREG.md) against the pooled passes of one card: PASS / FAIL / NO-DATA. Each item
    carries its statistic (stat: the signed deviation from the prediction, or the value for a one-sided item), its band,
    its theory, and whether it decides that theory on this card."""
    V = {}
    t3_here = card in pr.get("t3_decides", [])
    def rec(item, got, pred, stat, ok, band):
        th = THEORY[item.split()[0]]
        V[item] = {"item": item, "theory": th, "decides": th != "context" and (th != "T3" or t3_here),
                   "verdict": "NO-DATA" if ok is None else ("PASS" if ok else "FAIL"), "got": got, "predicted": pred,
                   "stat": stat, "band": band}
    def two(item, got, center, ndig=4):
        b = band_of(pr, card, item)
        s = None if got is None else round(got - center, ndig)
        rec(item, got, f"{round(center, 4)} +- {b}", s, None if s is None else abs(s) <= b + EPS, b)
    def one(item, got):
        b = band_of(pr, card, item)
        rec(item, got, f"<= {b}", got, None if got is None else round(got, 4) <= b + EPS, b)
    def rng(item, got):
        lo, hi = band_of(pr, card, item)
        rec(item, got, [lo, hi], got, None if got is None else lo - EPS <= round(got, 4) <= hi + EPS, [lo, hi])

    tau0, P = pr["tau_s"][card], pr["pass_s"][card]
    xd = pr.get("extra_d_s", {}).get(card, {})
    Pm = {str(k): v for k, v in res.get("sp_pass_s", {}).items()}
    for rate in ("100", "50"):
        two(f"P0 SP pass under a {1000 // int(rate)} Hz sampler", Pm.get(rate), P[rate])
    P = {r: (Pm.get(r) or P[r]) for r in ("100", "50")}      # the delays are tested against the pass this block measured
    shifts = []
    for ch in tl.CHANNELS:
        q = res.get(ch, {}).get("100"); lag = dc.LAG[ch]
        m = (q or {}).get("one_pass" if lag else "fixed_delay")
        two(f"P1 tau {ch}", m and m["tau_s"], tau0[ch])
        one(f"P4a residual {ch}", m and round(m["rel_rms"], 4))
        rf = (q or {}).get("rise_fall_tau_s")
        b = band_of(pr, card, f"P4b rise=fall {ch}")
        s = None if not rf else round(rf[0] - rf[1], 4)
        rec(f"P4b rise=fall {ch}", rf, f"|rise - fall| <= {b}", s, None if s is None else abs(s) <= b + EPS, b)
        if lag:
            fd = (q or {}).get("fixed_delay")
            x = xd.get(ch, 0.0)
            two(f"P2a one-pass extra d {ch}", m and m["d_s"], x)
            two(f"P2b fixed d = pass {ch}", fd and fd["d_s"], P["100"] + x)
            q5 = res.get(ch, {}).get("50", {}).get("fixed_delay")
            two(f"P3 20 Hz fixed d = 20 Hz pass {ch}", q5 and q5["d_s"], P["50"] + x)
            if q5 and fd:
                shifts.append(q5["d_s"] - fd["d_s"])
        else:
            fd = (q or {}).get("fixed_delay")
            two(f"P2c board_avg d {ch}", fd and fd["d_s"], 0.0)
        if ch == "minion_w" and q and len(q.get("by_kind_tau", {})) == 2:
            mh = q["by_kind_tau"]
            b = band_of(pr, card, "P4c tau M = H (step size)")
            s = round(mh["M"] - mh["H"], 4)
            rec("P4c tau M = H (step size)", mh, f"|M - H| <= {b}", s, abs(s) <= b + EPS, b)
        for L, r5 in ((q or {}).get("recovery_gauss0.1") or {}).items():
            two(f"P5a plateau {ch} {L}s", r5.get("plateau"), 0.0)
            two(f"P5b energy {ch} {L}s", r5.get("energy"), 0.0)
            e = None if "edge_on_s" not in r5 or "edge_off_s" not in r5 else round(max(abs(r5["edge_on_s"]), abs(r5["edge_off_s"])), 4)
            one(f"P5c edges {ch} {L}s", e)
            one(f"P5d flat scatter {ch} {L}s", r5.get("rms_flat"))
            two(f"P5e plateau vs free fit {ch} {L}s", r5.get("plateau_vs_free_fit"), 0.0)
        pe = (q or {}).get("published_err") or {}
        ranges = pr["published_err"].get(f"{card}:{ch}", pr["published_err"]["default"])
        for L, v in pe.items():
            if L in ranges and v is not None:
                rng(f"P6 published split {ch} {L}s", v)
    # T3 against the rival, pooled over the three rails: the rival (a fixed latency) predicts no shift at all
    dP = P["50"] - P["100"]
    b = band_of(pr, card, "P3b d shift 20-10 Hz, mean of the rails")
    sh = round(float(np.mean(shifts)), 4) if len(shifts) == len(RAILS) else None
    rec("P3b d shift 20-10 Hz, mean of the rails", sh, f"{round(dP, 3)} +- {b}", None if sh is None else round(sh - dP, 4),
        None if sh is None else abs(sh - dP) <= b + EPS, b)
    lo, hi = band_of(pr, card, "P4d board_w in-burst drift (M bursts)")
    dr = res.get("board_drift_per_s", {}).get("M")
    rec("P4d board_w in-burst drift (M bursts)", dr, [lo, hi], dr, None if dr is None else lo <= dr <= hi, [lo, hi])
    out = []
    for it in expected_items(card, pr):
        out.append(V.pop(it) if it in V else {"item": it, "theory": THEORY[it.split()[0]],
                                               "decides": THEORY[it.split()[0]] != "context" and (THEORY[it.split()[0]] != "T3" or t3_here),
                                               "verdict": "NO-DATA", "got": None, "predicted": None, "stat": None,
                                               "band": band_of(pr, card, it)})
    out += list(V.values())                           # an item the schedule does not predict (reported, never lost)
    return out


def theories(V, pr, card):
    """Each theory on this card: survives (every deciding item passes), falsified, incomplete (NO-DATA among its deciding
    items), untested (T1 failed, but the input was less square than in the offline data where T1 held: P4d above
    the card's offline range), or reported only (T3 off aifoundry3)."""
    out = {}
    drift = next((v for v in V if v["item"].startswith("P4d")), None)
    for th in ("T1", "T2", "T3", "T4"):
        items = [v for v in V if v["theory"] == th]
        dec = [v for v in items if v["decides"]]
        fails = [v["item"] for v in dec if v["verdict"] == "FAIL"]
        nod = [v["item"] for v in dec if v["verdict"] == "NO-DATA"]
        if not dec:
            st = "reported only (decided on " + ", ".join(pr.get("t3_decides", [])) + ")"
        elif fails:
            st = "falsified"
            if th == "T1" and drift and drift["got"] is not None and drift["got"] > drift["band"][1]:
                st = "untested (P4d: the bursts were less square than offline)"
        elif nod:
            st = "incomplete"
        else:
            st = "survives"
        out[th] = {"status": st, "items": len(dec), "fail": fails, "no_data": nod,
                   "reported_fail": [v["item"] for v in items if not v["decides"] and v["verdict"] == "FAIL"]}
    return out


def pass_status(d):
    try:
        b = json.load(open(os.path.join(d, "block.json")))
    except (OSError, ValueError):
        return None, "no block.json"
    bad = [f"status {b.get('status')}"] if b.get("status") != "ok" else []
    bad += [f"mode {b.get('mode')}"] if b.get("mode") != "full" else []
    return b, "; ".join(bad)


def cmd_report(a):
    pr = prereg()
    blocks, flagged = [], {}
    for d in a.dirs:
        b, why = pass_status(d)
        blocks.append(b)
        if why:
            flagged[d] = why
    if flagged and not a.allow_partial:
        sys.exit("tau report: not a full, ok pass: " + "; ".join(f"{d}: {w}" for d, w in flagged.items())
                 + " (re-run the pass, or --allow-partial to score it anyway, flagged)")
    cards = {b["card"] for b in blocks if b}
    card = a.card or (cards.pop() if len(cards) == 1 else None)
    if not card or (a.card and cards - {a.card}):
        sys.exit(f"tau report: the passes are from {sorted(cards)}; give one card's passes (and --card)")
    res = analyse(a.dirs, pr, card)
    res["card"] = card
    res["verdicts"] = verdicts(res, pr, card)
    res["theories"] = theories(res["verdicts"], pr, card)
    n = {v: sum(x["verdict"] == v for x in res["verdicts"]) for v in ("PASS", "FAIL", "NO-DATA")}
    res["summary"] = n
    if flagged:
        res["partial"] = flagged
    if a.out:
        json.dump(res, open(a.out, "w"), indent=1)
    for x in res["verdicts"]:
        tag = "" if x["decides"] else "  (reported)"
        print(f"{x['verdict']:8s} {x['item']:44s} got {x['got']}  predicted {x['predicted']}{tag}")
    for th, v in res["theories"].items():
        print(f"{th}: {v['status']}" + (f" ({', '.join(v['fail'])})" if v["fail"] else ""))
    print(f"{card}: {n}" + (f"  PARTIAL: {flagged}" if flagged else ""))


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sp = ap.add_subparsers(dest="cmd", required=True)
    e = sp.add_parser("env"); e.add_argument("--card", required=True); e.add_argument("--pass", dest="pass_", type=int, required=True)
    e.add_argument("--mode", default="full", choices=("full", "smoke"))
    w = sp.add_parser("wincheck"); w.add_argument("tel"); w.add_argument("--kind"); w.add_argument("--stop-c", type=float, default=90)
    r = sp.add_parser("winrec"); r.add_argument("--out", required=True)
    for k, t in (("win", int), ("rate", int), ("kind", str), ("secs", float), ("sampler-s", float), ("try", int), ("fails", int),
                 ("t-launch", int), ("t-first", int), ("t-burst", int), ("burst-rc", str), ("launches", int), ("status", str),
                 ("check", str), ("burst-out", str)):
        r.add_argument("--" + k, type=t, dest=k.replace("-", "_") + ("_" if k == "try" else ""), default=0 if t is int else None)
    c = sp.add_parser("check-pass"); c.add_argument("dir")
    p = sp.add_parser("report"); p.add_argument("dirs", nargs="+"); p.add_argument("--out"); p.add_argument("--card")
    p.add_argument("--allow-partial", action="store_true", help="score passes that are not full and ok (flagged in the output)")
    a = ap.parse_args()
    {"env": cmd_env, "wincheck": cmd_wincheck, "winrec": cmd_winrec, "check-pass": cmd_check, "report": cmd_report}[a.cmd](a)


if __name__ == "__main__":
    main()
