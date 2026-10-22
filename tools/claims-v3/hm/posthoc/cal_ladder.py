"""E62-CAL: the power ladder (median of the 10 Hz samples in the last 4 s of each rung) and the registered session
gate (the camera's frame-mean rise over the UNI32 rung plus the following idle, against the pre-session idle).
Usage: cal_ladder.py <RED> <out.json>"""
import json
import statistics
import sys

import numpy as np

red, out = sys.argv[1], sys.argv[2]
sess = json.load(open(f"{red}/session.json"))
t0 = sess["t_start_ms"]
launches = [json.loads(l) for l in open(f"{red}/launches.jsonl")]
phases = [json.loads(l) for l in open(f"{red}/phases.jsonl")]
tel = []
for l in open(f"{red}/tel.jsonl"):
    try:
        d = json.loads(l)
    except ValueError:
        continue
    if "line" in d and isinstance(d["line"], str):
        try:
            d = dict(json.loads(d["line"]), host_ms=d.get("host_ms"))
        except ValueError:
            continue
    tel.append(d)
tt = np.array([d.get("host_ms") or d["t_ms"] for d in tel], dtype=float)


def window(a, b, key):
    idx = np.where((tt >= a) & (tt <= b))[0]
    vals = []
    for i in idx:
        d = tel[i]
        if key == "board_w":
            v = d.get("board_w")
        elif key == "minion_w":
            v = (d.get("sp") or {}).get("minion_w", [None])[0]
        elif key == "die_c":
            v = (d.get("temp_c") or {}).get("minshire", [None])[0]
        elif key == "mhz":
            v = (d.get("mhz") or {}).get("minion")
        else:
            v = None
        if isinstance(v, (int, float)) and v < 1000:
            vals.append(float(v))
    return vals


idle0 = window(t0, t0 + 170_000, "board_w")
idle_w = statistics.median(idle0) if idle0 else None
rows = []
for r in launches:
    if r["block"] != "E62-CAL":
        continue
    a, b = r["t_end_ms"] - 4000, r["t_end_ms"]
    bw, mw, dc, mz = (window(a, b, k) for k in ("board_w", "minion_w", "die_c", "mhz"))
    rows.append({
        "n": r["n"], "set": r["set"], "harts": r["harts"], "per_shire": r["per_shire"], "mask": r["mask"],
        "board_w_med": round(statistics.median(bw), 2) if bw else None,
        "switched_w": round(statistics.median(bw) - idle_w, 2) if bw and idle_w else None,
        "minion_w_med": round(statistics.median(mw), 2) if mw else None,
        "die_c_med": statistics.median(dc) if dc else None,
        "mhz": sorted(set(mz)), "n_samples": len(bw), "wall_s": r["wall_s"],
    })
# the session gate: frame mean over [UNI32 start, end of the following IDLE] against the pre-session idle
z = np.load(f"{red}/frames.npz")
ts, mk = z["t_s"], z["mk"]
fm = mk.reshape(len(ts), -1).mean(axis=1)
uni = next(r for r in launches if r["block"] == "E62-CAL" and r["set"] == "UNI32")
idle_ph = next(p for p in phases if p["block"] == "E62-CAL" and p.get("idle"))
a = (uni["t_start_ms"] - t0) / 1000.0
b = (idle_ph["planned_end_ms"] - t0) / 1000.0
pre = (ts > 10) & (ts < 170)
win = (ts >= a) & (ts <= b)
base = float(np.median(fm[pre]))
peak = float(np.max(fm[win]) - base)
med_after = float(np.median(fm[(ts >= a + 8.5) & (ts <= b)]) - base)
res = {"idle_board_w": round(idle_w, 2) if idle_w else None, "ladder": rows,
       "gate": {"window_s": [round(a, 1), round(b, 1)], "baseline_mk": round(base, 1),
                "frame_mean_peak_rise_mk": round(peak, 1), "frame_mean_median_rise_mk": round(med_after, 1),
                "registered_threshold_mk": 300, "passes": peak >= 300}}
json.dump(res, open(out, "w"), indent=1)
print(f"idle board {idle_w:.2f} W")
print(f"{'set':8s} {'harts':>5s} {'per':>3s} {'board W':>8s} {'switch W':>8s} {'minion W':>8s} {'die C':>5s} MHz")
for r in rows:
    print(f"{r['set']:8s} {r['harts']:5d} {r['per_shire']:3d} {r['board_w_med']:8.2f} {r['switched_w']:8.2f} "
          f"{(r['minion_w_med'] or 0):8.2f} {r['die_c_med']!s:>5s} {r['mhz']}")
print("gate:", res["gate"])
