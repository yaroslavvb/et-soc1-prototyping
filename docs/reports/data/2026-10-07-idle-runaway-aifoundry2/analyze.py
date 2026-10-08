#!/usr/bin/env python3
"""analyze.py: every number and chart series of the 7 October page, read off records.jsonl.gz.

  python3 analyze.py            # prints the findings; writes analysis.json (build_report.py reads it)

The heat model is the 2 October one. It is refitted here from ../2026-10-02-idle-runaway-aifoundry2/records.jsonl
with that folder's fit.py method, so its constants are exact rather than rounded:
  leakage   P(T) = a + b*exp(c*T), fitted to every 2 October record;
  balance   C dT/dt = P - (T - Ta)/R, fitted to the first 45 minutes, which gives C and R.
Here R and C are kept, and the air temperature the card would need is read off each minute instead:
  Ta = T - R*(P - C*dT/dt)
with T and P the card's mean die temperature and board power, and dT/dt a least-squares slope over 6 minutes. It
is a model number, not a measurement: any loss of cooling at the card shows up as warmer "air". The R of
2 October is a fit to one run, and R and the air temperature are correlated in it."""
import datetime as dt
import gzip
import json
import math
import os
import statistics

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
PDT = dt.timezone(dt.timedelta(hours=-7))


def at(s):
    """'10-07 03:55' -> epoch seconds (PDT)"""
    m, rest = s.split("-", 1)
    d, hm = rest.split()
    h, mi = hm.split(":")
    return dt.datetime(2026, int(m), int(d), int(h), int(mi), tzinfo=PDT).timestamp()


def clock(t, sec=False):
    return dt.datetime.fromtimestamp(t, PDT).strftime("%H:%M:%S" if sec else "%H:%M")


def day(t):
    return dt.datetime.fromtimestamp(t, PDT).strftime("%a %-d %b")


# ---- the 2 October fit, by fit.py's method --------------------------------------------------------------------
def fit_oct2():
    rs = [json.loads(l) for l in open(os.path.join(HERE, "..", "2026-10-02-idle-runaway-aifoundry2", "records.jsonl"))]
    rs = [r for r in rs if r["cards"][0].get("die") is not None]
    t = np.array([r["t"] for r in rs]) / 1000.0
    t -= t[0]
    T = np.array([r["cards"][0]["die"] for r in rs], float)
    P = np.array([r["cards"][0]["w"] for r in rs], float)
    best = None
    for c in np.linspace(0.01, 0.12, 111):
        X = np.c_[np.ones_like(T), np.exp(c * T)]
        k, *_ = np.linalg.lstsq(X, P, rcond=None)
        e = ((X @ k - P) ** 2).sum()
        if best is None or e < best[0]:
            best = (e, c, k)
    e, c, (a, b) = best
    w = 12
    dT = np.full_like(T, np.nan)
    dT[w:-w] = (T[2 * w:] - T[:-2 * w]) / (t[2 * w:] - t[:-2 * w])
    ok = ~np.isnan(dT) & (t < 45 * 60)
    k, *_ = np.linalg.lstsq(np.c_[P[ok], T[ok], np.ones(ok.sum())], dT[ok], rcond=None)
    C = 1 / k[0]
    R = -1 / (k[1] * C)
    Ta = k[2] * R * C
    return dict(a=float(a), b=float(b), c=float(c), C=float(C), R=float(R), Ta=float(Ta), rms=float(math.sqrt(e / len(T))))


F = fit_oct2()


def law(T):
    return F["a"] + F["b"] * math.exp(F["c"] * T)


# The idle card's tipping point: where the leakage curve's slope equals the cooling's, R*P'(T) = 1. Above the air
# temperature that puts heating and cooling tangent there, an idle card has no steady temperature at all.
T_TIP = math.log(1 / (F["R"] * F["b"] * F["c"])) / F["c"]
AIR_CRIT = T_TIP - F["R"] * law(T_TIP)


def settle(ta):
    """The model's steady temperature for air at ta (the lower crossing), or None if there is none."""
    Ts = np.linspace(30, 160, 13001)
    n = np.array([law(x) for x in Ts]) - (Ts - ta) / F["R"]
    s = np.where(np.diff(np.sign(n)) < 0)[0]
    return float(Ts[s[0]]) if len(s) else None


# ---- the records -----------------------------------------------------------------------------------------------
recs = [json.loads(l) for l in gzip.open(os.path.join(HERE, "records.jsonl.gz"), "rt", encoding="utf-8")]
for r in recs:
    r["s"] = r["t"] / 1000.0
card = [(r["s"], r["cards"][0]) for r in recs if r.get("cards") and r["cards"][0].get("die") is not None]
cs = np.array([s for s, _ in card])
cT = np.array([c["die"] for _, c in card], float)
cP = np.array([c["w"] for _, c in card], float)
held_s = [r["s"] for r in recs for c in r.get("cards", []) if c.get("held")]
first_s, first_c = card[0]
last_s, last_c = card[-1]
gone = next(r for r in recs if r["s"] > last_s and not (r.get("cards") and r["cards"][0].get("die") is not None))
noted_down = next((r for r in recs if r.get("cards") and r["cards"][0].get("ok") is False), None)


def window(a, b):
    m = (cs >= at(a)) & (cs < at(b))
    return cT[m], cP[m]


# ---- per minute ------------------------------------------------------------------------------------------------
minutes = []
m0 = int(first_s // 60) * 60
host = [(r["s"], r["temps"]) for r in recs if r.get("temps")]
hs = np.array([s for s, _ in host])
for m in range(m0, int(last_s // 60) * 60 + 60, 60):
    sel = (cs >= m) & (cs < m + 60)
    if not sel.any():
        continue
    win = (cs >= m + 30 - 180) & (cs < m + 30 + 180)
    x = cs[win] - (m + 30)
    slope = float(np.polyfit(x, cT[win], 1)[0]) if win.sum() >= 24 else float("nan")  # degrees per second
    Tm, Pm = float(cT[win].mean()), float(cP[win].mean())
    air = Tm - F["R"] * (Pm - F["C"] * slope)
    hsel = (hs >= m) & (hs < m + 60)
    ht = [host[i][1] for i in np.where(hsel)[0]]
    minutes.append(dict(
        s=m, die=float(np.median(cT[sel])), w=float(np.median(cP[sel])), air=air, slope=slope * 60,
        resid=float(np.mean([p - law(t) for t, p in zip(cT[sel], cP[sel])])),
        nvme=statistics.fmean(h["nvme"] for h in ht) if ht else None,
        nic=statistics.fmean(h["nic"] for h in ht) if ht else None,
        cpu=min(h["cpu"] for h in ht) if ht else None))
# the model's air, smoothed for the chart: a running median over 9 minutes
airs = [mm["air"] for mm in minutes]
for i, mm in enumerate(minutes):
    mm["air9"] = statistics.median(airs[max(0, i - 4): i + 5])


def mins(a, b):
    return [mm for mm in minutes if at(a) <= mm["s"] < at(b)]


def rng(xs, nd=0):
    return [round(min(xs), nd), round(max(xs), nd)]


def mean(xs):
    return statistics.fmean(xs)


# ---- the findings ----------------------------------------------------------------------------------------------
eve_T, eve_P = window("10-06 17:00", "10-07 03:50")
night = mins("10-07 00:00", "10-07 03:50")
morning = mins("10-07 05:00", "10-07 11:30")
evening = mins("10-06 17:00", "10-06 23:59")
late = mins("10-07 15:00", "10-07 16:15")
base_air = mean([mm["air"] for mm in night])
# the step: the first minute after 03:30 whose smoothed air is 3 degrees above the night's
step = next(mm for mm in minutes if mm["s"] >= at("10-07 03:30") and mm["air9"] > base_air + 3)
pre = mins("10-07 03:00", "10-07 03:50")
post = mins("10-07 04:00", "10-07 04:50")
at0450 = next(mm for mm in minutes if mm["s"] >= at("10-07 04:50"))
at0354 = next(mm for mm in minutes if mm["s"] >= at("10-07 03:54"))
second = mins("10-07 13:50", "10-07 14:20")
second_after = mins("10-07 14:40", "10-07 15:10")
half = {}
for mm in minutes:
    k = mm["s"] // 1800 * 1800
    half.setdefault(k, []).append(mm["resid"])
half_means = [(k, mean(v)) for k, v in sorted(half.items()) if k < at("10-07 16:30")]
worst_half = max(half_means, key=lambda kv: abs(kv[1]))


def crossing(level, after="10-07 12:00"):
    i = next(i for i in range(len(cs)) if cs[i] >= at(after) and cT[i] >= level)
    return dict(t=clock(cs[i], True), die=int(cT[i]), w=round(float(cP[i]), 1))


cross = {lv: crossing(lv) for lv in (85, 90, 100, 110, 120, 130)}
n = dict(
    fit={k: round(v, 4) for k, v in F.items()},
    tip_T=round(T_TIP, 1), tip_P=round(law(T_TIP), 1), air_crit=round(AIR_CRIT, 1),
    settle={str(a): (round(settle(a), 1) if settle(a) else None) for a in (39, 42, 46, 48, 50, 51)},
    back=dict(day=day(first_s), t=clock(first_s, True), die=first_c["die"], w=first_c["w"]),
    last=dict(day=day(last_s), t=clock(last_s, True), die=last_c["die"], max=last_c["max"], w=last_c["w"],
              ok=last_c.get("ok")),
    gone=clock(gone["s"], True),
    first_not_ok=clock(noted_down["s"], True) if noted_down else None,
    hours_up=round((last_s - first_s) / 3600, 2),
    held_records=len(held_s), held_first=clock(min(held_s), True), held_last=clock(max(held_s), True),
    held_after_tests=sum(1 for s in held_s if s >= at("10-06 17:00")), records=len(recs), card_records=len(card),
    evening=dict(die=rng(eve_T), w=rng(eve_P, 1)),
    air=dict(evening=rng([mm["air"] for mm in evening], 1), night=round(base_air, 1),
             night_rng=rng([mm["air9"] for mm in night], 1),
             morning=round(mean([mm["air"] for mm in morning]), 1),
             morning_rng=rng([mm["air9"] for mm in morning], 1),
             late=round(mean([mm["air"] for mm in late]), 1), late_rng=rng([mm["air9"] for mm in late], 1),
             before_second=round(mean([mm["air"] for mm in second]), 1),
             after_second=round(mean([mm["air"] for mm in second_after]), 1)),
    step=dict(t=clock(step["s"]), die_0354=at0354["die"], die_0450=at0450["die"], w_0354=round(at0354["w"], 1),
              w_0450=round(at0450["w"], 1)),
    host=dict(pre={k: round(mean([mm[k] for mm in pre]), 1) for k in ("nvme", "nic", "cpu")},
              post={k: round(mean([mm[k] for mm in post]), 1) for k in ("nvme", "nic", "cpu")},
              cpu_util_0330_0430=round(mean([r["cpu"] for r in recs if at("10-07 03:30") <= r["s"] < at("10-07 04:30")]), 2)),
    morning_die=rng([mm["die"] for mm in morning]),
    resid=dict(worst_half_hour=round(worst_half[1], 2), at=clock(worst_half[0]),
               rms_all=round(float(np.sqrt(np.mean([(p - law(t)) ** 2 for t, p in zip(cT, cP)]))), 2)),
    cross=cross,
)

# chart series: one point a minute (x = minutes since the first reading). The model's air stops at 16:30: in the last
# quarter hour the die climbs too fast for a slope over 6 minutes, and the card's own 50-130 W warms what is around it.
AIR_END = at("10-07 16:30")
# ... and starts at 17:00 on 6 Oct: until 16:35 the fix's load tests ran on the card, and its power was not leakage alone
AIR_START = at("10-06 17:00")
# 2 October's last reading, for the comparison
o2 = [json.loads(l) for l in open(os.path.join(HERE, "..", "2026-10-02-idle-runaway-aifoundry2", "records.jsonl"))]
o2 = [r for r in o2 if r["cards"][0].get("die") is not None][-1]
n["oct2_last"] = dict(t=clock(o2["t"] / 1000, True), die=o2["cards"][0]["die"], max=o2["cards"][0]["max"],
                      w=o2["cards"][0]["w"])
# the host's sensors, smoothed like the model's air, as changes from their own night level (chart 2)
for key in ("nvme", "nic"):
    vals = [mm[key] for mm in minutes]
    for i, mm in enumerate(minutes):
        win = [v for v in vals[max(0, i - 4): i + 5] if v is not None]
        mm[key + "9"] = statistics.median(win) if win else None
night_lvl = {k: mean([mm[k + "9"] for mm in night]) for k in ("air", "nvme", "nic")}
n["night_level"] = {k: round(v, 1) for k, v in night_lvl.items()}
# chart 3: the card's power at each whole degree of its die, against the 2 October law
bins = {}
for T, P in zip(cT, cP):
    bins.setdefault(int(T), []).append(P)
scatter = [dict(T=T, w=round(statistics.median(v), 2), n=len(v), law=round(law(T), 2)) for T, v in sorted(bins.items())]
n["scatter_worst"] = max((abs(b["w"] - b["law"]), b["T"]) for b in scatter if b["n"] >= 12)
# the table view: hour by hour
hours = []
for h0 in range(int(first_s // 3600) * 3600, int(last_s // 3600) * 3600 + 3600, 3600):
    mm = [x for x in minutes if h0 <= x["s"] < h0 + 3600]
    if not mm:
        continue
    T_, P_ = window(dt.datetime.fromtimestamp(h0, PDT).strftime("%m-%d %H:%M"),
                    dt.datetime.fromtimestamp(h0 + 3600, PDT).strftime("%m-%d %H:%M"))
    airs_h = [x["air"] for x in mm if x["s"] < AIR_END]
    hours.append(dict(d=day(h0), h=clock(h0), die=rng(T_), w=rng(P_, 1),
                      air=round(mean(airs_h), 1) if airs_h else None,
                      nvme=round(mean([x["nvme"] for x in mm if x["nvme"] is not None]), 1),
                      nic=round(mean([x["nic"] for x in mm if x["nic"] is not None]), 1), minutes=len(mm)))
series = [dict(x=round((mm["s"] - first_s) / 60, 2), t=clock(mm["s"]), d=day(mm["s"]), die=round(mm["die"], 1),
               w=round(mm["w"], 2), air=round(mm["air9"], 2) if mm["s"] < AIR_END else None, nvme=round(mm["nvme"], 2) if mm["nvme"] else None,
               nic=round(mm["nic"], 2) if mm["nic"] else None, law=round(law(mm["die"]), 2),
               d_air=round(mm["air9"] - night_lvl["air"], 2) if AIR_START <= mm["s"] < AIR_END else None,
               d_nvme=round(mm["nvme9"] - night_lvl["nvme"], 2) if mm["nvme9"] is not None and mm["s"] >= AIR_START else None,
               d_nic=round(mm["nic9"] - night_lvl["nic"], 2) if mm["nic9"] is not None and mm["s"] >= AIR_START else None) for mm in minutes]
# the last readings at full rate, so the chart ends on the card's last reading rather than a minute's median
tail = [dict(x=round((s - first_s) / 60, 3), t=clock(s, True), d=day(s), die=float(T), w=float(P))
        for s, T, P in zip(cs, cT, cP) if s >= at("10-07 16:40")]
raw = [(mm["s"], mm["air"]) for mm in minutes if mm["s"] >= at("10-07 14:00")]
sec = next(s0 for i, (s0, _) in enumerate(raw) if statistics.fmean(v for _, v in raw[i:i + 6]) >= n["air"]["before_second"] + 1.5)
n["second"] = dict(t=clock(sec), x=round((sec - first_s) / 60, 2),
                   die=next(mm["die"] for mm in minutes if mm["s"] == sec))
json.dump(dict(numbers=n, series=series, tail=tail, scatter=scatter, hours=hours, first_s=first_s), open(os.path.join(HERE, "analysis.json"), "w"),
          ensure_ascii=False, separators=(",", ":"))

print(f"2 Oct fit: P(T) = {F['a']:.2f} + {F['b']:.4f} exp({F['c']:.4f} T) W (rms {F['rms']:.2f}); "
      f"C {F['C']:.0f} J/C, R {F['R']:.3f} C/W, air {F['Ta']:.1f} C")
print(f"tipping point {T_TIP:.1f} C at {law(T_TIP):.1f} W; no steady temperature with air above {AIR_CRIT:.1f} C")
print("model settles:", n["settle"])
print(f"records {len(recs)}, card readings {len(card)}, held {len(held_s)} ({n['held_first']}-{n['held_last']} on 6 Oct), "
      f"held after 6 Oct 17:00: {n['held_after_tests']}")
print(f"back on the bus {n['back']}; last reading {n['last']}; no reading from {n['gone']}; first not-ok {n['first_not_ok']}")
print(f"on the bus {n['hours_up']} h")
print(f"6 Oct 17:00 - 7 Oct 03:50: die {n['evening']['die']} C, {n['evening']['w']} W")
print("air at the card (model):", n["air"])
print("the step:", n["step"], " host before/after:", n["host"])
print("morning die:", n["morning_die"])
print("power minus the 2 Oct law:", n["resid"])
print("crossings:", n["cross"])
print("2 Oct last:", n["oct2_last"], " night levels:", n["night_level"], " worst degree bin:", n["scatter_worst"])
print("second loss of cooling:", n["second"])
print(f"{len(hours)} hours in the table, {len(series)} minutes in the charts, {len(scatter)} degree bins")
