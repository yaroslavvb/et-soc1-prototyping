#!/usr/bin/env python3
"""E64: the surface. Descriptive, from reduce_hpl.py's results (README.md, "The surface"; not a registered rule).

    python3 surface_hpl.py <results.json> --out <figures.json>

1. Each run's board power at 600, 700 and 800 MHz, referred to a 58 C die with E60's leakage slope on this card
   (0.442 W per C). The sampler's board value trails the clock by a pass or two
   (it refreshes once per SP pass and is read one pass late), so the board series is shifted by the lag L (0-3
   samples) that makes it most uniform within each clock, and a power at f is the median of the shifted values
   where the clock read f on this sample and the one before. Every run passes through all three points in its
   start ramp (600 -> 700 -> 800, a pass each), and the dithering runs many times over.
2. A linear model of those powers over every run: P_f = B_f + c_run * s_f, s_f = (V_f / 0.517)^2 * f / 600, with
   B_f the busy offset at each point and c_run the run's switching watts at 600 MHz and 0.517 V.
3. The governor as the trace shows it: once per pass it compares a running average of the card's power with the
   TDP and steps one point down if it is over, one up if it is under (no dead band); the average follows the
   instantaneous power with a time constant tau. tau and the pass are fitted to the LAD and MIN runs' measured
   mean clock after their start ramp (from 1.5 s), at the card's 65 W.
4. The thermal cap: the die's mean reading against the board's mean power over the last 40 s of each SUS run, a
   line; the power at which it reads 65.5 C is the sustained power the 65 C test allows on this card's cooling.
5. The surface: the simulated mean clock over the switching watts c (0 W, zeros, to 30 W, past random normal) and
   the TDP (30-90 W), on the busy offsets of a 58 C die, and the fp32 rate it gives (1,024 minions x 8,192 FLOP
   per 546 cycles x the clock).
"""
import argparse
import json
import math
import statistics as st

PTS = (600, 700, 800)
V = {600: 0.517, 700: 0.568, 800: 0.618}
S = {f: (V[f] / 0.517) ** 2 * f / 600.0 for f in PTS}
OPS = {"fp32": 8192, "fp16": 16384, "int8": 32768}
CYC = {"fp32": 546.0, "fp16": 546.0, "int8": 318.0}


def rate_t(typ, mhz, minions=1024):
    return minions * OPS[typ] / CYC[typ] * mhz * 1e6 / 1e12


LEAK_W_PER_C = 0.442   # aifoundry2's leakage slope at 800 MHz, E60 (docs/reports/data/2026-10-20-bitflip-ladder/reduce.txt)
T_REF = 58.0           # the die reading every power is referred to (E60 launched at 58 C)


def powers(m, ref=None):
    """{f: W} at each clock, lag-corrected, and the lag. With ref, every value is referred to a die reading of ref C
    with LEAK_W_PER_C (for the model's fit); without, it is the power the governor saw (for its calibration)."""
    tr = [x for x in m["trace"] if 0 <= x[0] <= m["work_s"] + 0.2 and x[2] is not None and x[3] in PTS
          and x[1] is not None]
    if len(tr) < 6:
        return None, None
    best = None
    for L in range(0, 4):
        groups = {f: [] for f in PTS}
        for i in range(1, len(tr) - L):
            if tr[i][3] == tr[i - 1][3]:
                corr = LEAK_W_PER_C * (tr[i + L][1] - ref) if ref is not None else 0.0
                groups[tr[i][3]].append(tr[i + L][2] - corr)
        disp = sum(st.pstdev(v) * len(v) for v in groups.values() if len(v) > 1)
        n = sum(len(v) for v in groups.values())
        score = disp / n if n else 1e9
        if best is None or score < best[0]:
            best = (score, L, groups)
    _, L, groups = best
    return {f: (round(st.median(v), 2) if v else None) for f, v in groups.items()}, L


def fit_linear(rows):
    """P_f = B_f + c_run * s_f over [(run, f, W)]: alternate the two least-squares steps (closed form each)."""
    runs = sorted({r for r, _, _ in rows})
    B = {f: 30.0 for f in PTS}
    c = {r: 10.0 for r in runs}
    for _ in range(200):
        for r in runs:
            pts = [(f, w) for rr, f, w in rows if rr == r]
            num = sum(S[f] * (w - B[f]) for f, w in pts)
            den = sum(S[f] ** 2 for f, w in pts)
            c[r] = num / den if den else 0.0
        for f in PTS:
            res = [w - c[r] * S[f] for r, ff, w in rows if ff == f]
            if res:
                B[f] = sum(res) / len(res)
    err = [w - (B[f] + c[r] * S[f]) for r, f, w in rows]
    return B, c, (sum(e * e for e in err) / len(err)) ** 0.5


def simulate(p, tdp, tau, dt, t_end=6.5, t_from=1.5, start_avg=24.0, ramp_at=0.4):
    """The governor on powers p {f: W}: the mean clock from t_from to t_end."""
    k = PTS.index(600)
    avg = start_avg
    t = 0.0
    acc = n = 0.0
    climbing = True
    while t < t_end:
        if t >= ramp_at:
            if climbing:
                if avg > tdp:
                    climbing = False
                elif k < 2:
                    k += 1
                else:
                    climbing = False
            else:
                if avg > tdp and k > 0:
                    k -= 1
                elif avg < tdp and k < 2:
                    k += 1
        f = PTS[k]
        a = 1 - math.exp(-dt / tau)
        avg += (p[f] - avg) * a
        if t >= t_from:
            acc += f
            n += 1
        t += dt
    return acc / n if n else None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("results")
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    R = json.load(open(a.results))
    runs = R["runs"]
    per, rows = {}, []
    for m in runs:
        if not m.get("trace"):
            continue
        pw, L = powers(m)
        pref, _ = powers(m, ref=T_REF)
        steady = [x[3] for x in m["trace"] if 1.5 <= x[0] <= m["work_s"] and x[3] in PTS]
        first8 = [x[3] for x in m["trace"] if 1.5 <= x[0] <= min(8.0, m["work_s"]) and x[3] in PTS]
        per[m["run"]] = {"p": pw, "p_ref": pref, "lag": L,
                         "mhz_steady": round(st.mean(steady), 1) if steady else None,
                         "first8_mhz": round(st.mean(first8), 1) if first8 else None}
        if pref and m["block"] in ("LAD", "MIN", "SUS", "SMOKE"):
            for f in PTS:
                if pref.get(f) is not None:
                    rows.append((m["run"], f, pref[f]))
    out = {"runs": [], "fit": None, "governor": None, "check": [], "surface": None, "thermal": None}
    for m in runs:
        rec = {k: m.get(k) for k in ("run", "block", "label", "type", "values", "minions", "rep", "p800_w", "mhz_mean",
                                      "ghz_eff", "rate_t", "die_start", "die_max", "events", "first_down_kind",
                                      "sus_rate_t", "sus_rate_wall_t", "sus_ghz_eff", "sus_mhz_mean", "sus_die_mean",
                                      "sus_w_mean", "sus_last", "mhz_600", "mhz_700", "mhz_800", "sus_bins", "gate",
                                      "sus_first_66_s", "sus_tel_hot_share", "sus_ring_from_s")}
        rec.update(per.get(m["run"], {}))
        out["runs"].append(rec)
    if rows:
        B, c, rms = fit_linear(rows)
        out["fit"] = {"B": B, "s": S, "rms_w": rms, "n": len(rows), "c": {k: round(v, 3) for k, v in c.items()}}
        cal = [m for m in runs if m["block"] in ("LAD", "MIN") and per.get(m["run"], {}).get("mhz_steady")]
        best = None
        for tau in [0.4 + 0.1 * i for i in range(27)]:
            for dt in (0.13, 0.16, 0.2, 0.24):
                err = []
                for m in cal:
                    pr = per[m["run"]]["p"]
                    if not pr or None in pr.values():
                        continue
                    sim = simulate(pr, 65.0, tau, dt, t_end=m["work_s"])
                    err.append(sim - per[m["run"]]["mhz_steady"])
                if err:
                    e = (sum(x * x for x in err) / len(err)) ** 0.5
                    if best is None or e < best[0]:
                        best = (e, tau, dt)
        if best:
            e, tau, dt = best
            out["governor"] = {"tau_s": round(tau, 2), "pass_s": dt, "rms_mhz": round(e, 1), "n": len(cal)}
            for m in cal:
                pr = per[m["run"]]["p"]
                if not pr or None in pr.values():
                    continue
                out["check"].append({"run": m["run"], "label": m["label"], "p": pr,
                                     "sim": round(simulate(pr, 65.0, tau, dt, t_end=m["work_s"]), 1),
                                     "meas": per[m["run"]]["mhz_steady"]})
            cs = [round(1.0 * i, 1) for i in range(0, 31)]
            tdps = list(range(30, 92, 2))
            grid = []
            for tdp in tdps:
                row = []
                for cc in cs:
                    p = {f: B[f] + cc * S[f] for f in PTS}
                    row.append(round(simulate(p, float(tdp), tau, dt, t_end=12.0, t_from=4.0), 1))
                grid.append(row)
            out["surface"] = {"c_w": cs, "tdp_w": tdps, "mhz": grid,
                              "p800_of_c": [round(B[800] + cc * S[800], 1) for cc in cs],
                              "note": "governor model at the fitted tau and pass; busy offsets B_f of these runs"}
            # the speed each measured kind of number would hold under other power levels (the model, cool die):
            # one row per (type, operands) with a fitted switching term, its own three measured powers where they exist
            caps = [35, 45, 55, 65, 75, 85]
            groups = {}
            for m in runs:
                if m["block"] in ("LAD", "SUS") and m.get("minions") == 1024 and m["run"] in c:
                    groups.setdefault((m["type"], m["values"]), []).append(m)
            table = []
            for (typ, vals), ms in groups.items():
                cc = st.mean(c[m["run"]] for m in ms)
                # each point from the runs' own referred powers; the line only where none was measured
                p, src = {}, {}
                for f in PTS:
                    meas = [per[m["run"]]["p_ref"][f] for m in ms
                            if per.get(m["run"], {}).get("p_ref") and per[m["run"]]["p_ref"].get(f) is not None]
                    p[f] = st.mean(meas) if meas else B[f] + cc * S[f]
                    src[f] = "measured" if meas else "model"
                row = {"type": typ, "values": vals, "c_w": round(cc, 2), "runs": len(ms),
                       "p_w": {f: round(p[f], 1) for f in PTS}, "p_src": src, "mhz": {}, "rate": {}}
                for cap in caps:
                    mhz = simulate(p, float(cap), tau, dt, t_end=12.0, t_from=4.0)
                    row["mhz"][cap] = round(mhz, 0)
                    row["rate"][cap] = round(rate_t(typ, mhz), 2)
                table.append(row)
            out["cap_table"] = {"caps_w": caps, "rows": table}
    sus = [m for m in runs if m["block"] == "SUS" and m.get("sus_w_mean") and m.get("sus_die_mean")]
    if len(sus) >= 3:
        xs = [m["sus_w_mean"] for m in sus]
        ys = [m["sus_die_mean"] for m in sus]
        mx, my = st.mean(xs), st.mean(ys)
        sxx = sum((x - mx) ** 2 for x in xs)
        if sxx > 0:
            k = sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / sxx
            a0 = my - k * mx
            out["thermal"] = {"k_c_per_w": round(k, 4), "a_c": round(a0, 2),
                              "cap_w_at_65_5": round((65.5 - a0) / k, 1) if k > 0 else None,
                              "points": [[m["run"], m["sus_w_mean"], m["sus_die_mean"]] for m in sus]}
    json.dump(out, open(a.out, "w"), indent=1)
    if out["fit"]:
        print("B", {f: round(v, 2) for f, v in out["fit"]["B"].items()}, "rms", round(out["fit"]["rms_w"], 2),
              "n", out["fit"]["n"])
    print("governor", out["governor"])
    for c in out["check"]:
        print(f"  {c['label']:26s} p {c['p']}  sim {c['sim']:6.1f}  meas {c['meas']}")
    print("thermal", out["thermal"])
    return 0


if __name__ == "__main__":
    main()
