#!/usr/bin/env python3
"""E65 block C: the hart ladder, as pre-registered in hb/README.md.

    python3 tools/claims-v3/hb/reduce_ladder.py <RUNDIR> [<RUNDIR> ...] --out ladder.json [--csv rungs.csv]

A RUNDIR is one run_hm.py session (session.json, launches.jsonl, phases.jsonl, tel.jsonl). Per rung, per lap:
board power = the MEDIAN of the 10 Hz samples in the last 4.0 s of its launch (E62-CAL's window, hm/posthoc/
cal_ladder.py); the de-leaked value subtracts the mean of the two bracketing IDLE phases' last-10 s medians. Both
lines (raw over the session's pre-idle, and de-leaked) are fitted by least squares on hart count with a free
intercept; the unit of replication is the lap, and the SE comes from the between-lap scatter of the per-lap fits.
Nothing here opens a device.
"""
import argparse
import json
import os
import statistics


def read_jsonl(path):
    out = []
    if not os.path.exists(path):
        return out
    for line in open(path):
        line = line.strip()
        if not line:
            continue
        try:
            out.append(json.loads(line))
        except ValueError:
            continue
    return out


def read_tel(path):
    """The sampler's samples as (host_ms, record), unwrapping run_hm.py's {host_ms, line} form."""
    tel = []
    for d in read_jsonl(path):
        if "line" in d and isinstance(d["line"], str):
            try:
                rec = json.loads(d["line"])
            except ValueError:
                continue
            t = d.get("host_ms") or rec.get("t_ms")
        else:
            rec, t = d, d.get("host_ms") or d.get("t_ms")
        if t is not None:
            tel.append((float(t), rec))
    tel.sort(key=lambda x: x[0])
    return tel


def field(rec, key):
    if key == "board_w":
        v = rec.get("board_w")
    elif key == "minion_w":
        v = (rec.get("sp") or {}).get("minion_w", [None])[0]
    elif key == "die_c":
        v = ((rec.get("temp_c") or {}).get("minshire") or [None])[0]
        if v is None:
            v = ((rec.get("sp") or {}).get("minion_c") or [None])[0]
    elif key == "mhz":
        v = (rec.get("mhz") or {}).get("minion")
        if v is None:
            v = ((rec.get("sp") or {}).get("minion_mhz") or [None])[0]
    else:
        v = None
    return float(v) if isinstance(v, (int, float)) and abs(v) < 1e4 else None


def med(tel, a, b, key):
    vals = [field(r, key) for t, r in tel if a <= t <= b]
    vals = [v for v in vals if v is not None]
    return (statistics.median(vals), len(vals)) if vals else (None, 0)


def fit_line(xs, ys):
    """Least squares y = a + b x. Returns (a, b, rms residual) or None."""
    n = len(xs)
    if n < 3:
        return None
    mx, my = sum(xs) / n, sum(ys) / n
    sxx = sum((x - mx) ** 2 for x in xs)
    if sxx <= 0:
        return None
    b = sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / sxx
    a = my - b * mx
    r = [y - (a + b * x) for x, y in zip(xs, ys)]
    return a, b, (sum(v * v for v in r) / n) ** 0.5


def mean_se(v):
    v = [x for x in v if x is not None]
    if not v:
        return None, None, 0
    if len(v) == 1:
        return v[0], None, 1
    return (statistics.mean(v), statistics.stdev(v) / len(v) ** 0.5, len(v))


def one(rundir, win_s, idle_win_s):
    sess = json.load(open(os.path.join(rundir, "session.json")))
    proto = json.load(open(os.path.join(rundir, "protocol.json")))
    tel = read_tel(os.path.join(rundir, "tel.jsonl"))
    if not tel:
        tel = read_tel(os.path.join(rundir, "tel.jsonl.raw"))
    launches = [r for r in read_jsonl(os.path.join(rundir, "launches.jsonl")) if not r.get("dry")]
    phases = read_jsonl(os.path.join(rundir, "phases.jsonl"))
    values = (proto.get("heater") or {}).get("values")

    # the idle phases, by (cycle, phase index), with their last-idle_win_s median
    idles = {}
    for ph in phases:
        if not ph.get("idle"):
            continue
        b = ph.get("planned_end_ms")
        if b is None:
            continue
        m, n = med(tel, b - idle_win_s * 1000, b, "board_w")
        idles[(ph["cycle"], ph["phase"])] = {"W": m, "n": n, "t_end_ms": b,
                                             "die_c": med(tel, b - idle_win_s * 1000, b, "die_c")[0]}

    rungs = []
    for L in launches:
        if L.get("harts") in (None, 0) or L.get("rc") not in (0,) or L.get("short"):
            continue
        t1 = L["t_end_ms"]
        w, n = med(tel, t1 - win_s * 1000, t1, "board_w")
        if w is None or n < 10:
            continue
        before = idles.get((L["cycle"], L["phase"] - 1))
        after = idles.get((L["cycle"], L["phase"] + 1))
        br = [x["W"] for x in (before, after) if x and x["W"] is not None]
        rungs.append({
            "values": values, "cycle": L["cycle"], "phase": L["phase"], "set": L["set"],
            "harts": L["harts"], "mask": L.get("mask"), "n_samples": n,
            "board_w": w, "idle_bracket_w": (sum(br) / len(br)) if br else None, "n_bracket": len(br),
            "d_board_w": (w - sum(br) / len(br)) if br else None,
            "die_c": med(tel, t1 - win_s * 1000, t1, "die_c")[0],
            "mhz": med(tel, t1 - win_s * 1000, t1, "mhz")[0],
            "minion_w": med(tel, t1 - win_s * 1000, t1, "minion_w")[0],
        })

    # the session's own pre-idle, for the raw line
    pre = None
    if phases:
        first = min(ph.get("planned_start_ms") or 0 for ph in phases)
        pre = med(tel, first - 30000, first, "board_w")[0]

    per_lap = {}
    for r in rungs:
        per_lap.setdefault(r["cycle"], []).append(r)
    fits = {"raw": [], "deleaked": []}
    for c, rs in sorted(per_lap.items()):
        xs = [r["harts"] for r in rs]
        f = fit_line(xs, [r["board_w"] - (pre or 0) for r in rs])
        if f:
            fits["raw"].append({"cycle": c, "a_W": f[0], "b_W_per_hart": f[1], "rms_W": f[2], "n": len(xs)})
        ys = [r["d_board_w"] for r in rs if r["d_board_w"] is not None]
        xd = [r["harts"] for r in rs if r["d_board_w"] is not None]
        f = fit_line(xd, ys)
        if f:
            fits["deleaked"].append({"cycle": c, "a_W": f[0], "b_W_per_hart": f[1], "rms_W": f[2], "n": len(xd)})

    summary = {}
    for k, v in fits.items():
        a, ase, na = mean_se([x["a_W"] for x in v])
        b, bse, _ = mean_se([x["b_W_per_hart"] for x in v])
        rms, _, _ = mean_se([x["rms_W"] for x in v])
        summary[k] = {"intercept_W": a, "intercept_se_W": ase, "slope_W_per_hart": b,
                      "slope_se_W_per_hart": bse, "slope_mW_per_hart": b * 1000 if b is not None else None,
                      "slope_se_mW_per_hart": bse * 1000 if bse is not None else None,
                      "resid_rms_W": rms, "n_laps": na}
    # the pooled fit over every rung of every lap, as a check on the per-lap means
    allx = [r["harts"] for r in rungs if r["d_board_w"] is not None]
    ally = [r["d_board_w"] for r in rungs if r["d_board_w"] is not None]
    pooled = fit_line(allx, ally)
    return {"rundir": os.path.abspath(rundir), "values": values,
            "card": sess.get("host") or (proto.get("card")), "session": sess.get("session_id") or sess.get("id"),
            "pre_idle_board_w": pre, "n_rungs": len(rungs), "n_laps": len(per_lap),
            "per_rung_mean": {str(h): {k2: mean_se([r[k2] for r in rungs if r["harts"] == h])[0]
                                       for k2 in ("board_w", "d_board_w", "die_c", "mhz", "minion_w")}
                              for h in sorted({r["harts"] for r in rungs})},
            "fits_per_lap": fits, "fit": summary,
            "pooled_deleaked": ({"a_W": pooled[0], "b_W_per_hart": pooled[1], "rms_W": pooled[2],
                                 "n": len(allx)} if pooled else None),
            "rungs": rungs}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("rundirs", nargs="+")
    ap.add_argument("--out", required=True)
    ap.add_argument("--csv", default=None)
    ap.add_argument("--win-s", type=float, default=4.0)
    ap.add_argument("--idle-win-s", type=float, default=10.0)
    a = ap.parse_args()
    res = {"window_s": a.win_s, "idle_window_s": a.idle_win_s, "sessions": {}}
    for d in a.rundirs:
        r = one(d, a.win_s, a.idle_win_s)
        res["sessions"][r["values"] or os.path.basename(d)] = r
    s = res["sessions"]
    if "randn" in s and "zeros" in s:
        ar, az = s["randn"]["fit"]["deleaked"], s["zeros"]["fit"]["deleaked"]
        if ar["intercept_W"] is not None and az["intercept_W"] is not None:
            d = ar["intercept_W"] - az["intercept_W"]
            se = ((ar["intercept_se_W"] or 0) ** 2 + (az["intercept_se_W"] or 0) ** 2) ** 0.5
            res["C1"] = {"d_intercept_W": d, "se_W": se or None,
                         "verdict": ("not the data's switching (|d| < 0.5 W)" if abs(d) < 0.5 else
                                     ("part of it is the kernel's switching" if se and abs(d) > 3 * se
                                      else "undecided"))}
            res["C2"] = {"intercept_randn_W": ar["intercept_W"],
                         "verdict": ("scales with f.V^2 like switching" if 2.5 <= ar["intercept_W"] <= 3.8 else
                                     ("fixed across card and clock" if 5.0 <= ar["intercept_W"] <= 6.6
                                      else "neither band"))}
    with open(a.out, "w") as f:
        json.dump(res, f, indent=1)
        f.write("\n")
    if a.csv:
        import csv as _csv
        rows = [r for v in s.values() for r in v["rungs"]]
        if rows:
            with open(a.csv, "w", newline="") as f:
                w = _csv.DictWriter(f, fieldnames=list(rows[0].keys()))
                w.writeheader()
                w.writerows(rows)
    for k, v in s.items():
        for which in ("raw", "deleaked"):
            q = v["fit"].get(which, {})
            if q.get("intercept_W") is not None:
                print(f"{k:6s} {which:9s}: {q['intercept_W']:.2f} +- {q['intercept_se_W'] or 0:.2f} W + "
                      f"{q['slope_mW_per_hart']:.2f} +- {q['slope_se_mW_per_hart'] or 0:.2f} mW/hart "
                      f"(resid rms {q['resid_rms_W']:.3f} W, {q['n_laps']} laps)")
    for k in ("C1", "C2"):
        if k in res:
            print(f"{k}: {json.dumps(res[k])}")


if __name__ == "__main__":
    main()
