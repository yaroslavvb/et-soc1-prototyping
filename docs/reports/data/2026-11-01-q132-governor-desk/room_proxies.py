#!/usr/bin/env python3
"""Q132(g): which reading follows the room? POST HOC, desk only, no card.

Nine days of the boxes' own 5 s history, taken to 5-minute medians, kept only where the card concerned has been idle for
30 minutes and its host's load is low, so that what moves is the room and not our own heat. Prints the correlation of
every reading with aifoundry2's idle die and idle watts, and the shared daily swing.

    room_proxies.py <hist-dir> [--weather open-meteo.json] [--out room-proxies.json] [--thin thin.csv] > room-proxies.txt
"""
import argparse
import glob
import json
import math
import os
import statistics as st
import time

os.environ["TZ"] = "America/Los_Angeles"
time.tzset()
BOXES = ("aifoundry1", "aifoundry2", "aifoundry3")
IDLE_W = {"a1c0": 22.0, "a1c1": 34.0, "a2c0": 26.0, "a3c0": 27.0}
STEP = 300


def load(hist):
    """{bin: {reading: [values]}} with a per-card idle flag worked out on the 5 s rows."""
    bins = {}
    for b in BOXES:
        tag = b.replace("aifoundry", "a")
        for f in sorted(glob.glob(os.path.join(hist, b, "*.jsonl"))):
            for ln in open(f):
                try:
                    r = json.loads(ln)
                except ValueError:
                    continue
                k = (r["t"] // 1000) // STEP
                d = bins.setdefault(k, {})
                T = r.get("temps") or {}
                for x in ("nvme", "nic", "cpu"):
                    if T.get(x) is not None:
                        d.setdefault(f"{tag}-{x}", []).append(T[x])
                d.setdefault(f"{tag}-load", []).append(r.get("load") or 0)
                for c in r.get("cards") or []:
                    name = f"{tag}c{c['n']}"
                    if c.get("die") is not None and c.get("w") is not None and not c.get("held"):
                        d.setdefault(f"{name}-die", []).append(c["die"])
                        d.setdefault(f"{name}-w", []).append(c["w"])
                    else:
                        d.setdefault(f"{name}-busy", []).append(1)
    return bins


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("hist")
    ap.add_argument("--weather")
    ap.add_argument("--out")
    ap.add_argument("--thin")
    a = ap.parse_args()
    bins = load(a.hist)
    keys = sorted(bins)
    series = {}
    for k in keys:
        row = {}
        for n, v in bins[k].items():
            row[n] = st.median(v)
        series[k] = row
    # idle flags: a card is idle in a bin if it has readings, no busy mark, and its watts are under the idle bar in this
    # bin and in the six before it (30 minutes)
    for c, bar in IDLE_W.items():
        run = 0
        for k in keys:
            r = series[k]
            ok = (f"{c}-w" in r and f"{c}-busy" not in r and r[f"{c}-w"] < bar)
            run = run + 1 if ok else 0
            r[f"{c}-idle"] = run >= 7
    # weather: the hourly outside air at the lab's latitude and longitude (Open-Meteo's model, not a station on the roof)
    wx = {}
    if a.weather:
        W = json.load(open(a.weather))["hourly"]
        for t, v in zip(W["time"], W["temperature_2m"]):
            wx[int(time.mktime(time.strptime(t, "%Y-%m-%dT%H:%M")))] = v

    def outside(ts):
        h0 = ts - ts % 3600
        if h0 in wx and h0 + 3600 in wx:
            return wx[h0] + (wx[h0 + 3600] - wx[h0]) * (ts - h0) / 3600.0
        return None

    for k in keys:
        o = outside(k * STEP)
        if o is not None:
            series[k]["outside-air"] = o
    # the rows where a2's card and the others are idle, and their hosts quiet
    target_rows = [k for k in keys if series[k].get("a2c0-idle") and series[k].get("a2-load", 9) < 2.0]
    print(f"5-minute bins: {len(keys)}; with aifoundry2's card idle 30 min and its host quiet: {len(target_rows)}")
    span = (keys[0] * STEP, keys[-1] * STEP)
    print("from", time.ctime(span[0]), "to", time.ctime(span[1]))

    def corr(xn, yn, rows, gate=None):
        xy = [(series[k][xn], series[k][yn]) for k in rows if xn in series[k] and yn in series[k] and (gate is None or gate(series[k]))]
        if len(xy) < 50:
            return None
        mx, my = st.mean(x for x, _ in xy), st.mean(y for _, y in xy)
        sx, sy = st.pstdev([x for x, _ in xy]), st.pstdev([y for _, y in xy])
        if sx == 0 or sy == 0:
            return None
        r = sum((x - mx) * (y - my) for x, y in xy) / len(xy) / sx / sy
        slope = r * sy / sx  # y per unit x
        res = [(y - my) - slope * (x - mx) for x, y in xy]
        return {"n": len(xy), "r": round(r, 3), "y_per_x": round(slope, 4), "rms_y": round(math.sqrt(sum(e * e for e in res) / len(res)), 4),
                "sd_x": round(sx, 3), "sd_y": round(sy, 3)}

    candidates = []
    for tag in ("a1", "a3", "a2"):
        for x in ("nvme", "nic", "cpu"):
            candidates.append((f"{tag}-{x}", lambda s, t=tag: s.get(f"{t}-load", 9) < 2.0))
    for c in ("a1c0", "a1c1", "a3c0"):
        candidates.append((f"{c}-w", lambda s, c0=c: s.get(f"{c0}-idle")))
        candidates.append((f"{c}-die", lambda s, c0=c: s.get(f"{c0}-idle")))
    candidates.append(("outside-air", None))
    out = {"note": "post hoc, desk only", "bins": len(keys), "target_rows": len(target_rows), "proxies": {}}
    print("\nEach reading against aifoundry2's idle WATTS (fine-grained, 0.01 W, follows the die through leakage) and idle DIE (1 C steps).")
    print(f"{'reading':14s} {'n':>5s} {'r(W)':>7s} {'W per unit':>10s} {'rms W':>7s} | {'r(die)':>7s} {'die per unit':>12s} {'rms die':>8s} | sd of reading")
    rows_out = []
    for name, gate in candidates:
        w = corr(name, "a2c0-w", target_rows, gate)
        d = corr(name, "a2c0-die", target_rows, gate)
        if not w or not d:
            continue
        rows_out.append((abs(w["r"]), name, w, d))
    rows_out.sort(key=lambda x: -x[0])
    for _, name, w, d in rows_out:
        print(f"{name:14s} {w['n']:5d} {w['r']:7.3f} {w['y_per_x']:10.4f} {w['rms_y']:7.3f} | {d['r']:7.3f} {d['y_per_x']:12.3f} {d['rms_y']:8.3f} | {w['sd_x']:.3f}")
        out["proxies"][name] = {"vs_a2_idle_w": w, "vs_a2_idle_die": d}
    # outside air, lagged: the room's daily peak trails the air's by hours
    lags = {}
    for lag_h in range(0, 13):
        pts = []
        for k in target_rows:
            o = outside(k * STEP - lag_h * 3600)
            if o is not None and "a2c0-w" in series[k]:
                pts.append((o, series[k]["a2c0-w"]))
        if len(pts) > 100:
            mx, my = st.mean(x for x, _ in pts), st.mean(y for _, y in pts)
            sx, sy = st.pstdev([x for x, _ in pts]), st.pstdev([y for _, y in pts])
            lags[lag_h] = round(sum((x - mx) * (y - my) for x, y in pts) / len(pts) / sx / sy, 3)
    print("\nOutside air (Open-Meteo's hourly model at the lab's latitude and longitude, not a station at the lab) against aifoundry2's idle W, with the air leading by L hours:")
    print("   " + "  ".join(f"L{k}: {v}" for k, v in lags.items()))
    out["outside_air_lag_r"] = lags
    # the thermometer: a2's idle W against its own die
    th = corr("a2c0-die", "a2c0-w", target_rows)
    print("\naifoundry2's idle watts against its own die:", th)
    out["a2_idle_w_vs_die"] = th
    for c in ("a1c0", "a1c1", "a3c0"):
        idle_rows = [k for k in keys if series[k].get(f"{c}-idle")]
        x = corr(f"{c}-die", f"{c}-w", idle_rows)
        print(f"{c} idle watts against its own die:", x)
        out[f"{c}_idle_w_vs_die"] = x
    # the daily shape: mean of each reading by hour of day over the idle rows of a2
    print("\nHour of day (PDT), means over the rows above: a2 idle die, a2 idle W, a3 idle W, a3 nvme, a3 nic, a2 nvme, a2 nic, outside air")
    hours = {}
    for k in target_rows:
        h = time.localtime(k * STEP).tm_hour
        hours.setdefault(h, []).append(series[k])
    for h in sorted(hours):
        v = hours[h]
        def m(n, gate=None):
            q = [s[n] for s in v if n in s and (gate is None or gate(s))]
            return round(st.mean(q), 2) if q else None
        print(f"{h:02d}: die {m('a2c0-die')} W {m('a2c0-w')} | a3 W {m('a3c0-w', lambda s: s.get('a3c0-idle'))} nvme {m('a3-nvme', lambda s: s.get('a3-load', 9) < 2)} nic {m('a3-nic', lambda s: s.get('a3-load', 9) < 2)} | a2 nvme {m('a2-nvme')} nic {m('a2-nic')} | air {m('outside-air')} | n {len(v)}")
    # the thinned committed copy: 5-minute medians of the readings, numbers only
    if a.thin:
        cols = ["a1-nvme", "a1-nic", "a1-cpu", "a1c0-die", "a1c0-w", "a1c1-die", "a1c1-w", "a2-nvme", "a2-nic", "a2-cpu", "a2c0-die", "a2c0-w",
                "a3-nvme", "a3-nic", "a3-cpu", "a3c0-die", "a3c0-w", "a1-load", "a2-load", "a3-load"]
        with open(a.thin, "w") as f:
            f.write("t_s," + ",".join(cols) + "\n")
            for k in keys:
                r = series[k]
                f.write(str(k * STEP) + "," + ",".join("" if c not in r else str(round(r[c], 2)) for c in cols) + "\n")
    if a.out:
        json.dump(out, open(a.out, "w"), indent=1)


if __name__ == "__main__":
    main()
