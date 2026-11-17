#!/usr/bin/env python3
"""data-e208r (Q205, Tue 17 Nov 2026): the session-repeat table for E208's added seventh session, POST HOC (made after the data, by the
lab's lane; no rule here was registered before any datum, and nothing here is a forecast or a score of one).

For each arm of the repeat (aifoundry2 card 0, the model session's repeat of session a2c0-S1, schedule a2c0-S1.json unchanged) against
the first a2c0-S1 (committed e99209a5) and beside a2c0-S2 (committed eed9624f, the same 71 arms in the reverse order), from the three
registered reductions (reduce_mms.py b9e32618, its outputs data-e208-<s>.json as committed or staged), in each session's primary view
(win, the 800 MHz launches 1.0-3.5 s into each process; per arm the reducer's own mean over its runs):
  cycles an op (cyc_op_max, the slowest minion; cyc_op_mean beside), seconds an op (T_op_us), W over idle (dP_w, the primary baseline
  rule), J over idle an op (J_op; J_op_corr, the reducer's die-start correction, beside), the kernel clock in the view (kclock_mhz) and
  at the governor's own mix (the burst view's kclock_mhz), and the die at start (die_start_c, the rest's last 5 s before each run).
Differences: relative (repeat / first - 1) for cycles, seconds, W, J; absolute for the clocks (MHz) and the die (C). Their spread over arms
(n, median, mean, sd, rms, min, max, and the share within 0.1%, 1% and 5%). Energy only where both sessions read the arm for energy
(the reducer's n_energy_runs >= 1 in both; capped and time runs carry none).
The within-session replicate spread: the anchor arm (4x8x8-int8-rnd, 9 runs in each session, first, between blocks and last), its
relative sd over the 9 runs per session, sqrt(2) x that (the spread expected of a difference of two single runs), and the anchor's own
session-to-session difference of means against its standard error; the null runs' sd of dP at zero signal (W). The comparison: the
repeat's rms relative difference over the single-run arms against sqrt(2) x the anchor's pooled relative sd; for W also in watts against
sqrt(2) x the null sd. Python's own modules only; reads only.

    /usr/bin/python3 -I -B repeat_e208r.py <repeat data json> <first S1 data json> <S2 data json> --md out.md --json out.json
"""
import argparse
import hashlib
import json
import math
import os
import statistics
import sys

METRICS = [  # key, label, kind (rel/abs), energy?
    ("cyc_op_max", "cycles an op (max over minions)", "rel", False),
    ("cyc_op_mean", "cycles an op (mean over minions)", "rel", False),
    ("T_op_us", "seconds an op (us)", "rel", False),
    ("dP_w", "W over idle", "rel", True),
    ("J_op", "J over idle an op (nJ)", "rel", True),
    ("J_op_corr", "J over idle an op, the session's own die correction (nJ)", "rel", True),
    ("dP_c50", "W over idle, die-corrected to 50 C at 0.48%/C (post hoc)", "rel", True),
    ("J_op_c50", "J over idle an op, die-corrected to 50 C at 0.48%/C (post hoc, nJ)", "rel", True),
    ("kclock_mhz", "kernel clock in the view (MHz)", "abs", False),
    ("kclock_burst_mhz", "kernel clock at the governor's mix (MHz)", "abs", False),
    ("die_start_c", "die at start (C)", "abs", False),
]
ANCHOR = "4x8x8-int8-rnd"
C50, S48 = 50.0, 0.0048  # post hoc common die reference and the registered default slope (E208.md section 7: 0.48 %/C on aifoundry2)


def c50(x, die):
    """x re-referenced to a common die of 50 C at 0.48 %/C (post hoc): x / (1 + s (die - 50))"""
    if x is None or die is None:
        return None
    return x / (1.0 + S48 * (die - C50))


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def arm_vals(d, name):
    """the primary figures of one arm in one session, or None"""
    a = (d.get("arms") or {}).get(name)
    if a is None:
        return None
    pv = d["primary_view"]
    runs = [r for r in d["runs"] if r.get("arm") == name and r.get("role") != "null"]
    pvs = sorted({r.get("primary_view") or pv for r in runs})
    view = pvs[0] if len(pvs) == 1 else pv
    v = (a.get("views") or {}).get(view) or {}
    b = (a.get("views") or {}).get("burst") or {}
    ne = v.get("n_energy_runs") or 0
    out = {"role": a.get("role"), "form": a.get("form"), "n_runs": a.get("n_runs"), "capped_runs": a.get("capped_runs"),
           "view": view, "views_of_runs": pvs, "n_energy_runs": ne,
           "cyc_op_max": v.get("cyc_op_max"), "cyc_op_mean": v.get("cyc_op_mean"), "T_op_us": v.get("T_op_us"),
           "dP_w": v.get("dP_w") if ne else None, "J_op": (v.get("J_op") * 1e9 if ne and v.get("J_op") is not None else None),
           "J_op_corr": (v.get("J_op_corr") * 1e9 if ne and v.get("J_op_corr") is not None else None),
           "kclock_mhz": v.get("kclock_mhz"), "kclock_burst_mhz": b.get("kclock_mhz"), "die_start_c": a.get("die_start_c"),
           "checks": a.get("checks")}
    if a.get("n_runs") == 1:
        out["dP_c50"] = c50(out["dP_w"], out["die_start_c"])
        out["J_op_c50"] = c50(out["J_op"], out["die_start_c"])
    else:  # per run, then the mean over the runs read for energy
        rs = [r for r in runs if not r.get("capped")]
        vv = [((r.get("views") or {}).get(r.get("primary_view") or pv) or {}) for r in rs]
        dps = [c50(x.get("dP_w"), r.get("die_start_c")) for x, r in zip(vv, rs) if x.get("dP_w") is not None]
        jps = [c50(x.get("J_op") * 1e9, r.get("die_start_c")) for x, r in zip(vv, rs) if x.get("J_op") is not None]
        out["dP_c50"] = statistics.fmean(dps) if dps and ne else None
        out["J_op_c50"] = statistics.fmean(jps) if jps and ne else None
    return out


def diff(m, kind, x, y):
    if x is None or y is None:
        return None
    if kind == "rel":
        return (x / y - 1.0) if y else None
    return x - y


def spread(xs, names):
    pts = [(x, n) for x, n in zip(xs, names) if x is not None]
    if not pts:
        return {"n": 0}
    v = [p[0] for p in pts]
    lo, hi = min(pts), max(pts)
    s = {"n": len(v), "median": statistics.median(v), "mean": statistics.fmean(v),
         "sd": (statistics.stdev(v) if len(v) > 1 else None), "rms": math.sqrt(sum(x * x for x in v) / len(v)),
         "min": lo[0], "min_arm": lo[1], "max": hi[0], "max_arm": hi[1],
         "abs_median": statistics.median([abs(x) for x in v])}
    return s


def share_within(xs, t):
    v = [x for x in xs if x is not None]
    return (sum(1 for x in v if abs(x) <= t) / len(v)) if v else None


def anchors(d):
    pv = d["primary_view"]
    rows = []
    for r in d["runs"]:
        if r.get("role") != "anchor":
            continue
        v = (r.get("views") or {}).get(r.get("primary_view") or pv) or {}
        e = not r.get("capped")
        rows.append({"run": r["run"], "i": r.get("i"), "capped": r.get("capped"), "cyc_op_max": v.get("cyc_op_max"),
                     "cyc_op_mean": v.get("cyc_op_mean"), "T_op_us": v.get("T_op_us"),
                     "dP_w": v.get("dP_w") if e else None, "J_op": (v.get("J_op") * 1e9 if e and v.get("J_op") is not None else None),
                     "J_op_corr": (v.get("J_op_corr") * 1e9 if e and v.get("J_op_corr") is not None else None),
                     "kclock_mhz": v.get("kclock_mhz"), "die_start_c": r.get("die_start_c")})
        rows[-1]["dP_c50"] = c50(rows[-1]["dP_w"], rows[-1]["die_start_c"])
        rows[-1]["J_op_c50"] = c50(rows[-1]["J_op"], rows[-1]["die_start_c"])
    return rows


def rel_sd(v):
    v = [x for x in v if x is not None]
    if len(v) < 2:
        return None
    return statistics.stdev(v) / statistics.fmean(v)


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("repeat")
    ap.add_argument("first")
    ap.add_argument("s2")
    ap.add_argument("--md", required=True)
    ap.add_argument("--json", required=True)
    a = ap.parse_args(argv)
    R, F, T = (json.load(open(p)) for p in (a.repeat, a.first, a.s2))
    names = sorted(R["arms"])
    rows = []
    for n in names:
        r, f, t = arm_vals(R, n), arm_vals(F, n), arm_vals(T, n)
        row = {"arm": n, "repeat": r, "first": f, "s2": t, "d_rep_first": {}, "d_s2_first": {}, "d_rep_s2": {}}
        for m, _, kind, _e in METRICS:
            row["d_rep_first"][m] = diff(m, kind, r and r[m], f and f[m])
            row["d_s2_first"][m] = diff(m, kind, t and t[m], f and f[m])
            row["d_rep_s2"][m] = diff(m, kind, r and r[m], t and t[m])
        rows.append(row)
    single = [x for x in rows if (x["repeat"] or {}).get("n_runs") == 1 and (x["first"] or {}).get("n_runs") == 1]
    summ = {}
    for which in ("d_rep_first", "d_s2_first", "d_rep_s2"):
        summ[which] = {}
        for m, _, kind, _e in METRICS:
            xs = [x[which][m] for x in rows]
            ns = [x["arm"] for x in rows]
            s = spread(xs, ns)
            s1 = spread([x[which][m] for x in single], [x["arm"] for x in single])
            if kind == "rel":
                s.update({"within_0.1pct": share_within(xs, 0.001), "within_1pct": share_within(xs, 0.01),
                          "within_5pct": share_within(xs, 0.05)})
            summ[which][m] = {"all_arms": s, "single_run_arms": s1}
    # W over idle in watts (absolute), repeat - first, single-run arms read for energy in both
    dW = [((x["repeat"] or {}).get("dP_w") - (x["first"] or {}).get("dP_w"))
          if (x["repeat"] or {}).get("dP_w") is not None and (x["first"] or {}).get("dP_w") is not None else None for x in single]
    dW_s2 = [((x["s2"] or {}).get("dP_w") - (x["first"] or {}).get("dP_w"))
             if (x["s2"] or {}).get("dP_w") is not None and (x["first"] or {}).get("dP_w") is not None else None for x in single]
    summ["dW_watts_rep_first_single"] = spread(dW, [x["arm"] for x in single])
    summ["dW_watts_s2_first_single"] = spread(dW_s2, [x["arm"] for x in single])
    # within-session replicates: the anchor
    anc = {"repeat": anchors(R), "first": anchors(F), "s2": anchors(T)}
    within = {}
    for m, _, kind, _e in METRICS:
        if m == "kclock_burst_mhz":
            continue
        per = {}
        for s, rws in anc.items():
            v = [x[m] for x in rws if x[m] is not None]
            if not v:
                continue
            per[s] = {"n": len(v), "mean": statistics.fmean(v), "sd": (statistics.stdev(v) if len(v) > 1 else None),
                      "rel_sd": (rel_sd(v) if kind == "rel" else None), "min": min(v), "max": max(v)}
        within[m] = per
        if kind == "rel" and "repeat" in per and "first" in per and per["repeat"]["sd"] and per["first"]["sd"]:
            pooled = math.sqrt((per["repeat"]["rel_sd"] ** 2 + per["first"]["rel_sd"] ** 2) / 2.0)
            se = math.sqrt(per["repeat"]["sd"] ** 2 / per["repeat"]["n"] + per["first"]["sd"] ** 2 / per["first"]["n"])
            dm = per["repeat"]["mean"] - per["first"]["mean"]
            rep = summ["d_rep_first"][m]["single_run_arms"]
            within[m]["pooled_rel_sd_rep_first"] = pooled
            within[m]["sqrt2_pooled_rel_sd"] = math.sqrt(2.0) * pooled
            within[m]["anchor_mean_diff"] = dm
            within[m]["anchor_mean_diff_rel"] = dm / per["first"]["mean"]
            within[m]["anchor_mean_diff_se"] = se
            within[m]["anchor_mean_diff_z"] = (dm / se) if se else None
            within[m]["repeat_rms_over_sqrt2_within"] = (rep.get("rms") / (math.sqrt(2.0) * pooled)) if rep.get("n") and pooled else None
    nulls = {s: d.get("nulls") for s, d in (("repeat", R), ("first", F), ("s2", T))}
    key = "win.dP_line"
    nsd = [nulls[s].get(key, {}).get("sd") for s in ("repeat", "first") if nulls[s] and nulls[s].get(key)]
    null_pooled = math.sqrt(sum(x * x for x in nsd) / len(nsd)) if nsd else None
    summ["null_sd_w_pooled_rep_first"] = null_pooled
    summ["dW_rms_over_sqrt2_null"] = (summ["dW_watts_rep_first_single"].get("rms") / (math.sqrt(2.0) * null_pooled)
                                      if null_pooled and summ["dW_watts_rep_first_single"].get("n") else None)
    out = {"what": "data-e208r's session-repeat table for E208's added seventh session (POST HOC; desk arithmetic of the registered "
                   "reductions; no forecast, no score)",
           "inputs": {"repeat": {"file": os.path.basename(a.repeat), "sha256": sha(a.repeat), "session": R.get("session")},
                      "first": {"file": os.path.basename(a.first), "sha256": sha(a.first), "session": F.get("session")},
                      "s2": {"file": os.path.basename(a.s2), "sha256": sha(a.s2), "session": T.get("session")}},
           "primary_view": [R["primary_view"], F["primary_view"], T["primary_view"]],
           "die": {"repeat": {"ref": R.get("die_ref_c"), "slope": R.get("die_slope")},
                   "first": {"ref": F.get("die_ref_c"), "slope": F.get("die_slope")},
                   "s2": {"ref": T.get("die_ref_c"), "slope": T.get("die_slope")}},
           "n_arms": len(rows), "n_single_run_arms": len(single), "rows": rows, "summary": summ, "anchors": anc,
           "within": within, "nulls": nulls, "python": sys.version.split()[0], "interpreter": sys.executable}
    with open(a.json, "w") as f:
        json.dump(out, f, indent=1)
    write_md(a.md, out)
    print(f"arms {len(rows)}; single-run arms {len(single)}")
    for m, lab, kind, _e in METRICS:
        s = summ["d_rep_first"][m]["single_run_arms"]
        if not s.get("n"):
            continue
        f = (lambda x: f"{100 * x:+.3f}%") if kind == "rel" else (lambda x: f"{x:+.3f}")
        print(f"repeat vs first, {lab}: n {s['n']}, median {f(s['median'])}, rms {f(s['rms']).lstrip('+')}, "
              f"range {f(s['min'])} ({s['min_arm']}) to {f(s['max'])} ({s['max_arm']})")
    return 0


def pct(x, nd=2):
    return "-" if x is None else f"{100 * x:+.{nd}f}%"


def num(x, nd=2):
    return "-" if x is None else f"{x:.{nd}f}"


def sgn(x, nd=2):
    return "-" if x is None else f"{x:+.{nd}f}"


def write_md(p, o):
    L = []
    A = L.append
    i = o["inputs"]
    A("# E208 session-repeat table: the repeat of a2c0-S1 against the first a2c0-S1, with a2c0-S2 beside (POST HOC)")
    A("")
    A("*Made by the lab's lane data-e208r (round Q205) after the data, from the three registered reductions (`reduce_mms.py` "
      "`b9e32618...`): **post hoc** desk arithmetic of measured records. No rule here was registered before any datum; nothing here is a "
      "forecast or a score of one. Each session's primary view `win` (the 800 MHz launches 1.0-3.5 s into each process; per arm the "
      "reducer's mean over its runs). Relative differences are repeat / first - 1; the clocks and the die in MHz and C. Energy only where "
      "both sessions read the arm for energy (capped and `time` runs carry none). `/usr/bin/python3` 3.12.3.*")
    A("")
    A("Inputs (sha256): the repeat `" + i["repeat"]["file"] + "` `" + i["repeat"]["sha256"][:16] + "...` (session `"
      + str(i["repeat"]["session"]) + "`); the first S1 `" + i["first"]["file"] + "` `" + i["first"]["sha256"][:16]
      + "...` (`" + str(i["first"]["session"]) + "`, commit e99209a5); S2 `" + i["s2"]["file"] + "` `" + i["s2"]["sha256"][:16]
      + "...` (`" + str(i["s2"]["session"]) + "`, commit eed9624f).")
    A("")
    A("## Headline: how well the session repeats (single-run arms; repeat against the first S1)")
    A("")
    A("| quantity | arms | median | rms | range (arm) | within 1% | S2 against S1: median, rms | within-session (anchor, 9 runs): sqrt(2) x rel sd | rms / that |")
    A("|---|---|---|---|---|---|---|---|---|")
    S = o["summary"]
    for m, lab, kind, _e in METRICS:
        s = S["d_rep_first"][m]["single_run_arms"]
        t = S["d_s2_first"][m]["single_run_arms"]
        if not s.get("n"):
            continue
        w = o["within"].get(m) or {}
        if kind == "rel":
            A(f"| {lab} | {s['n']} | {pct(s['median'], 3)} | {pct(s['rms'], 3).lstrip('+')} | {pct(s['min'], 2)} ({s['min_arm']}) to "
              f"{pct(s['max'], 2)} ({s['max_arm']}) | {100 * (S['d_rep_first'][m]['all_arms'].get('within_1pct') or 0):.0f}% (all arms) | "
              f"{pct(t.get('median'), 3)}, {pct(t.get('rms'), 3).lstrip('+')} | "
              f"{pct(w.get('sqrt2_pooled_rel_sd'), 3).lstrip('+')} | {num(w.get('repeat_rms_over_sqrt2_within'), 2)} |")
        else:
            A(f"| {lab} | {s['n']} | {sgn(s['median'], 2)} | {num(s['rms'], 2)} | {sgn(s['min'], 2)} ({s['min_arm']}) to "
              f"{sgn(s['max'], 2)} ({s['max_arm']}) | - | {sgn(t.get('median'), 2)}, {num(t.get('rms'), 2)} | - | - |")
    dW = S["dW_watts_rep_first_single"]
    dW2 = S["dW_watts_s2_first_single"]
    A("")
    A(f"W over idle in watts (repeat - first, single-run arms read for energy in both): n {dW.get('n')}, median {sgn(dW.get('median'), 3)} W, "
      f"rms {num(dW.get('rms'), 3)} W, range {sgn(dW.get('min'), 3)} ({dW.get('min_arm')}) to {sgn(dW.get('max'), 3)} ({dW.get('max_arm')}); "
      f"S2 - first: median {sgn(dW2.get('median'), 3)} W, rms {num(dW2.get('rms'), 3)} W. The null runs' sd of dP at zero signal "
      f"(`win.dP_line`, pooled over the repeat and the first S1): {num(S.get('null_sd_w_pooled_rep_first'), 3)} W; the repeat's rms in "
      f"watts over sqrt(2) x that: {num(S.get('dW_rms_over_sqrt2_null'), 2)}.")
    A("")
    A("## The anchor, run by run (4x8x8-int8-rnd: first, between blocks and last in each session)")
    A("")
    A("| session | runs | T_op us: mean (rel sd) | cycles max: mean (rel sd) | W over idle: mean (rel sd) | nJ an op: mean (rel sd) | nJ die-corrected to 50 C: mean (rel sd) | die at start C: mean (min-max) |")
    A("|---|---|---|---|---|---|---|---|")
    W_ = o["within"]
    for s, lab in (("first", "first S1"), ("repeat", "repeat"), ("s2", "S2")):
        def cell(m, nd):
            d = (W_.get(m) or {}).get(s)
            if not d:
                return "-"
            return f"{d['mean']:.{nd}f} ({100 * d['rel_sd']:.3f}%)" if d.get("rel_sd") is not None else f"{d['mean']:.{nd}f}"
        dd = (W_.get("die_start_c") or {}).get(s) or {}
        A(f"| {lab} | {len(o['anchors'][s])} | {cell('T_op_us', 4)} | {cell('cyc_op_max', 1)} | {cell('dP_w', 3)} | {cell('J_op', 3)} | "
          f"{cell('J_op_c50', 3)} | {num(dd.get('mean'), 2)} ({num(dd.get('min'), 0)}-{num(dd.get('max'), 0)}) |")
    A("")
    A("The anchor's own session-to-session difference (repeat mean - first mean, against its standard error from the two sessions' 9 runs):")
    A("")
    for m, lab, kind, _e in METRICS:
        w = W_.get(m) or {}
        if w.get("anchor_mean_diff") is None:
            continue
        A(f"- {lab}: {pct(w['anchor_mean_diff_rel'], 3)} (z {num(w.get('anchor_mean_diff_z'), 2)})")
    A("")
    A("Run by run (position in the session; the repeat beside the first):")
    A("")
    A("| # | first: run | first T_op us | first W | first nJ | first die C | repeat T_op us | repeat W | repeat nJ | repeat die C |")
    A("|---|---|---|---|---|---|---|---|---|---|")
    for k, (x, y) in enumerate(zip(o["anchors"]["first"], o["anchors"]["repeat"]), 1):
        A(f"| {k} | {x['run']} | {num(x['T_op_us'], 4)} | {num(x['dP_w'], 3)} | {num(x['J_op'], 3)} | {num(x['die_start_c'], 0)} | "
          f"{num(y['T_op_us'], 4)} | {num(y['dP_w'], 3)} | {num(y['J_op'], 3)} | {num(y['die_start_c'], 0)} |")
    A("")
    A("## Every arm (primary view; the repeat, the first S1, and their difference; S2 and its difference from the first beside)")
    A("")
    A("| arm | role | n (rep/first/S2) | cycles max: rep / first (d) | us an op: rep / first (d) | W over idle: rep / first (d) | nJ an op: rep / first (d) | nJ die-corr. to 50 C: d (own corr.: d) | MHz view: rep / first | MHz governor mix: rep / first | die start C: rep / first (d) | S2: cycles (d), us an op (d), W (d), nJ (d) |")
    A("|---|---|---|---|---|---|---|---|---|---|---|---|")
    for x in o["rows"]:
        r, f, t = x["repeat"] or {}, x["first"] or {}, x["s2"] or {}
        d, e = x["d_rep_first"], x["d_s2_first"]
        A(f"| {x['arm']} | {r.get('role')} | {r.get('n_runs')}/{f.get('n_runs')}/{t.get('n_runs') if t else '-'} | "
          f"{num(r.get('cyc_op_max'), 1)} / {num(f.get('cyc_op_max'), 1)} ({pct(d['cyc_op_max'], 3)}) | "
          f"{num(r.get('T_op_us'), 4)} / {num(f.get('T_op_us'), 4)} ({pct(d['T_op_us'], 3)}) | "
          f"{num(r.get('dP_w'), 2)} / {num(f.get('dP_w'), 2)} ({pct(d['dP_w'], 2)}) | "
          f"{num(r.get('J_op'), 2)} / {num(f.get('J_op'), 2)} ({pct(d['J_op'], 2)}) | {pct(d['J_op_c50'], 2)} ({pct(d['J_op_corr'], 2)}) | "
          f"{num(r.get('kclock_mhz'), 1)} / {num(f.get('kclock_mhz'), 1)} | {num(r.get('kclock_burst_mhz'), 1)} / {num(f.get('kclock_burst_mhz'), 1)} | "
          f"{num(r.get('die_start_c'), 1)} / {num(f.get('die_start_c'), 1)} ({sgn(d['die_start_c'], 1)}) | "
          f"{num(t.get('cyc_op_max'), 1)} ({pct(e['cyc_op_max'], 3)}), {num(t.get('T_op_us'), 4)} ({pct(e['T_op_us'], 3)}), "
          f"{num(t.get('dP_w'), 2)} ({pct(e['dP_w'], 2)}), {num(t.get('J_op'), 2)} ({pct(e['J_op'], 2)}) |")
    A("")
    A("## Notes (post hoc)")
    A("")
    A("- **Roles:** `arm` runs are read for time and energy; `time` runs for time only (never for energy, by the reducer's rule); the "
      "anchor runs 9 times a session. A **capped** run (fewer than 80% of its launches after 1.0 s in the 800 MHz band) is not read for "
      "energy; `capped_runs` per arm is in the JSON.")
    A("- **The within-session spread** here is the anchor's alone (one arm, high signal, 9 runs spread over the session); a low-signal arm's "
      "W over idle varies more in relative terms, which the null runs' sd in watts bounds from below.")
    A("- **S2** ran the same 71 arms in the reverse order (blocks and each unit's kinds reversed) between the first S1 and the repeat (19:14-"
      "19:53 PST Mon 16 Nov): its differences mix the order with the session.")
    A("- **The die corrections:** `J_op_corr` is each session's own registered correction (`dP / (1 + s (die_start - die_ref))`, "
      "with the session's own slope and reference: the repeat's and the first S1's references and slopes are in the JSON's `die`), so "
      "its differences carry the two references' difference; the post hoc `_c50` columns put both sessions on one reference, 50 C at "
      "the registered default 0.48 %/C, so their differences are the measured ones less the die starts' difference at that slope.")
    A("- **What a model can be scored to:** a model that knew each arm's value exactly would still differ from one session's reading by "
      "the session-to-session spread; for a single-run arm read once, about rms/sqrt(2) of the repeat-first rms above, if the two sessions "
      "are equally noisy and independent.")
    with open(p, "w") as fh:
        fh.write("\n".join(L) + "\n")


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
