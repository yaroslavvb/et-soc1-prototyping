#!/usr/bin/env python3
# /// script
# requires-python = ">=3.9"
# dependencies = ["numpy"]
# ///
"""Q145(a), the footing law: one leakage law per card at its idle operating point, shared by the power model's footing and the heat
chain's loop (FOOTING-LAW.md). This file builds the laws from committed files, gives a session's footing slope, and self-tests.

  build     python3 -B footing_law.py build <repo top> <footing-law.json>
            The law per card: a weighted quadratic in the firmware's whole-degree die reading (temp_c.minshire[0]) through the pooled
            per-degree mean board power of every committed dedicated idle cycle on that card at its idle clock and voltage (E66's rule F:
            samples at least 20 s after the cycle's cool_start, minion clock 600 MHz), weight = the samples in each degree; degrees with
            at least 100 samples, inside the band named per card. Its slope k_c(T) = 2 q0 T + q1, with a bootstrap over cycles (2,000
            draws, seed 145).
  k         python3 -B footing_law.py k <footing-law.json> <card> <runs.csv>
            A session's footing slope: k_c(T_mid), T_mid = the median, over the runs that pass every per-run gate (fail = 0), of
            (start_c + t_win) / 2 from the session's registered reduction's runs.csv (both columns are independent of k).
  selftest  python3 -B footing_law.py selftest <repo top>
            (1) every committed per-cycle band fit of E44 (aifoundry3), E66 and E71 is reproduced from its committed per-degree table by
            weighted least squares (whole-degree readings make that exact); (2) E44's aifoundry3 cycles re-read from their raw
            telemetry give sep-p1p3.json's tables; (3) the aifoundry3 law against E97's pooled law (the heat chain's) at 55-62 C.

Reads committed files only; nothing is fitted to any model's error. Of each cycle's marks it reads the cool_start mark alone.
SPDX-License-Identifier: Apache-2.0
"""
import csv
import gzip
import json
import os
import sys

import numpy as np

E71 = "docs/reports/data/2026-10-27-e71-idle-slope-aifoundry3"
E44 = "docs/reports/data/2026-09-25-claims-v3/raw"
E97 = (0.006175439291277969, -0.3665903970069978, 25.998917638611008)   # heat_q138t.py idle_law_a3 (E97's e97.json idle_law_pooled)
BANDS = [(58, 62), (56, 62), (58, 65), (56, 66), (54, 58), (51, 58)]
CARDS = {
    "aifoundry3": {"sources": [(E71 + "/sep-p1p3.json", None), (E71 + "/slopes.json", None)], "band": (52, 66),
                   "what": "E44 p1-p3 (25-26 Sep 2026) and E71 p21-p26 (27 Oct 2026), 600 MHz, 522-523 mV"},
    "aifoundry1c1": {"raw": [E44 + "/aifoundry1-c1/idle/p1", E44 + "/aifoundry1-c1/idle/p2", E44 + "/aifoundry1-c1/idle/p3"],
                     "band": (56, 70), "what": "E44 p1-p3 on aifoundry1 card 1 (25-26 Sep 2026), 600 MHz, 499 mV"},
    "aifoundry2": {"sources": [(E71 + "/aifoundry2-58-62.json", None)], "band": (49, 66),
                   "what": "E66 p13-p30 (26-27 Oct 2026), 600 MHz, 519 mV: aifoundry2's IDLE point only"},
}


def raw_cycle(p):
    cool = None
    for line in open(os.path.join(p, "marks.jsonl")):
        m = json.loads(line)
        if m.get("ev") == "cool_start":
            cool = m["t_ms"]
    T, W = [], []
    with gzip.open(os.path.join(p, "telemetry.jsonl.gz"), "rt") as f:
        for line in f:
            line = line.strip()
            if not (line.startswith("{") and line.endswith("}")):
                continue
            try:
                d = json.loads(line)
            except ValueError:
                continue
            t = d.get("t_ms")
            if t is None or cool is None or t < cool + 20000 or (d.get("mhz") or {}).get("minion") != 600:
                continue
            T.append(float(d["temp_c"]["minshire"][0]))
            W.append(float(d["board_w"]))
    T, W = np.array(T), np.array(W)
    return ({str(int(t)): float(W[T == t].mean()) for t in sorted(set(T.tolist()))},
            {str(int(t)): round(float((T == t).sum()) * 0.1, 1) for t in sorted(set(T.tolist()))})


def tables(top, rel):
    j = json.load(open(os.path.join(top, rel)))
    return [(r["per_degree_w"], r["per_degree_s"]) for _, r in sorted(j["passes"].items()) if r.get("usable")]


def _quad(tabs, lo, hi):
    acc = {}
    for pdw, pds in tabs:
        for t, w in pdw.items():
            ti = int(t)
            if lo <= ti <= hi:
                n = round(pds[t] / 0.1)
                s = acc.setdefault(ti, [0.0, 0])
                s[0] += w * n
                s[1] += n
    Ts = sorted(t for t in acc if acc[t][1] >= 100)
    if len(Ts) < 4:
        return None, None
    T = np.array(Ts, float)
    W = np.array([acc[t][0] / acc[t][1] for t in Ts])
    n = np.array([acc[t][1] for t in Ts], float)
    A = np.c_[T * T, T, np.ones_like(T)] * np.sqrt(n)[:, None]
    c, *_ = np.linalg.lstsq(A, W * np.sqrt(n), rcond=None)
    return c, (T, W, n)


def law(tabs, lo, hi):
    c, (T, W, n) = _quad(tabs, lo, hi)
    rng = np.random.default_rng(145)
    at = (55, 56, 57, 58, 59, 60, 61, 62)
    bs = {x: [] for x in at}
    for _ in range(2000):
        cc, _ = _quad([tabs[i] for i in rng.integers(0, len(tabs), len(tabs))], lo, hi)
        if cc is not None:
            for x in at:
                bs[x].append(2 * cc[0] * x + cc[1])
    resid = W - (c[0] * T * T + c[1] * T + c[2])
    return {"quad_w": [float(x) for x in c], "degrees": [int(T.min()), int(T.max())], "cycles": len(tabs),
            "rms_w": float(np.sqrt(np.mean(resid ** 2))), "slope_w_per_c": {str(x): float(2 * c[0] * x + c[1]) for x in at},
            "slope_ci95": {str(x): [float(np.percentile(v, 2.5)), float(np.percentile(v, 97.5))] for x, v in bs.items()}}


def card_tables(top, card):
    spec = CARDS[card]
    tabs = []
    for rel, _ in spec.get("sources", []):
        tabs += tables(top, rel)
    for rel in spec.get("raw", []):
        tabs.append(raw_cycle(os.path.join(top, rel)))
    return tabs


def build(top, out):
    res = {"what": "Q145(a) footing law: per card, the quasi-static idle law (FOOTING-LAW.md FL1)", "laws": {}}
    for card, spec in CARDS.items():
        L = law(card_tables(top, card), *spec["band"])
        L["sources"] = spec["what"]
        L["band_degrees"] = list(spec["band"])
        res["laws"][card] = L
    res["E97_slope_w_per_c"] = {str(x): 2 * E97[0] * x + E97[1] for x in (55, 56, 57, 58, 59, 60, 61, 62)}
    res["aifoundry3_minus_E97"] = {x: res["laws"]["aifoundry3"]["slope_w_per_c"][x] - v for x, v in res["E97_slope_w_per_c"].items()}
    json.dump(res, open(out, "w"), indent=1, sort_keys=True)
    for c, L in res["laws"].items():
        print(c, L["cycles"], "cycles", L["degrees"], "slope 58/59/60:", [round(L["slope_w_per_c"][x], 4) for x in ("58", "59", "60")])
    print("aifoundry3 - E97 over 55-62:", [round(v, 4) for v in res["aifoundry3_minus_E97"].values()])


def k_session(law_json, card, runs_csv):
    q = json.load(open(law_json))["laws"][card]["quad_w"]
    v = []
    for r in csv.DictReader(open(runs_csv)):
        if (r.get("fail") or "0") not in ("0", "", "[]"):
            continue
        try:
            v.append((float(r["start_c"]) + float(r["t_win"])) / 2.0)
        except (TypeError, ValueError):
            pass
    tm = float(np.median(v))
    return {"card": card, "runs": len(v), "T_mid": tm, "k_w_per_c": 2 * q[0] * tm + q[1]}


def _wls(sel, W, n):
    A = np.c_[sel, np.ones(len(sel))] * np.sqrt(n)[:, None]
    c, *_ = np.linalg.lstsq(A, np.asarray(W) * np.sqrt(n), rcond=None)
    return float(c[0])


def selftest(top):
    worst, nfit = 0.0, 0
    for rel in (E71 + "/sep-p1p3.json", E71 + "/slopes.json", E71 + "/aifoundry2-58-62.json"):
        j = json.load(open(os.path.join(top, rel)))
        for p, r in j["passes"].items():
            if not r.get("usable"):
                continue
            for lo, hi in BANDS:
                f = r["fits"].get(f"{lo}-{hi}", {})
                if not f.get("ok"):
                    continue
                sel = [t for t in sorted(int(x) for x in r["per_degree_w"]) if lo <= t <= hi]
                n = np.array([round(r["per_degree_s"][str(t)] / 0.1) for t in sel], float)
                k = _wls(np.array(sel, float), [r["per_degree_w"][str(t)] for t in sel], n)
                worst = max(worst, abs(k - f["slope_w_per_c"]))
                nfit += 1
    raw_worst = 0.0
    sep = json.load(open(os.path.join(top, E71 + "/sep-p1p3.json")))["passes"]
    for p in ("p1", "p2", "p3"):
        pdw, pds = raw_cycle(os.path.join(top, E44, "aifoundry3/idle", p))
        for t, w in pdw.items():
            raw_worst = max(raw_worst, abs(w - sep[p]["per_degree_w"][t]), abs(pds[t] - sep[p]["per_degree_s"][t]))
    L = law(card_tables(top, "aifoundry3"), *CARDS["aifoundry3"]["band"])
    d97 = max(abs(L["slope_w_per_c"][str(x)] - (2 * E97[0] * x + E97[1])) for x in range(55, 63))
    ok = worst < 1e-9 and raw_worst < 1e-9 and d97 <= 0.01
    print(f"SELFTEST {'PASS' if ok else 'FAIL'}: {nfit} committed band fits reproduced from their tables (worst {worst:.1e} W/C); "
          f"E44's aifoundry3 raw cycles against sep-p1p3.json's tables (worst {raw_worst:.1e}); the aifoundry3 law against E97's over 55-62 C "
          f"(worst {d97:.4f} W/C, line 0.01)")
    return 0 if ok else 1


def main(argv):
    if len(argv) >= 3 and argv[1] == "build":
        build(argv[2], argv[3])
        return 0
    if len(argv) >= 5 and argv[1] == "k":
        print(json.dumps(k_session(argv[2], argv[3], argv[4])))
        return 0
    if len(argv) >= 3 and argv[1] == "selftest":
        return selftest(argv[2])
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))
