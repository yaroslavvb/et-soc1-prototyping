#!/usr/bin/env python3
"""How the aifoundry2 flip-counting model and idle law transfer to aifoundry3: transfer.json and leakage_crosscard.json.

    D=docs/reports/data/2026-09-21-horace-aifoundry2; A3=docs/reports/data/2026-09-22-horace-aifoundry3
    python3 tools/ettelem/transfer_cards.py --cards $A3/cards.json --session $A3 --model $D/model.json \
        --transfer $A3/transfer.json --leak $A3/leakage_crosscard.json

transfer.json, from compare_cards.py's per-pattern switching powers (m = the aifoundry2 model, a = aifoundry3):
  scale_card3    the least-squares scale (a.m)/(m.m)
  loo_scale_rms  for each pattern i, calibrate s_i = a_i/m_i on that pattern alone and take the rms of
                 a_j - s_i m_j over the other seven patterns
  median_rms     the median of those; worst_rms their largest (and the pattern it was calibrated on)
  worst          the largest single |a_j - s_i m_j| over every i != j (also written as worst_single, with the
                 pair it belongs to)

leakage_crosscard.json, the aifoundry2 idle law P_fix + A exp((T - 80)/T_L) from model.json against aifoundry3's
idle telemetry:
  idle_curve, mean_offset_W, rms_W   the rule these were first published with: 10 Hz samples at 600 MHz outside
                 [launch start - 1 s, launch end + 6 s] of every launch in runs.jsonl, binned on the whole-degree
                 minion-shire reading, bins of 20 samples or more; mean_offset_W is the unweighted mean over bins
                 ("the mean of the four bins"); the 50 C bin is the 22 samples before the session's first launch
  mean_offset_W_by_sample            the same bins weighted by their samples
  model_rule     the idle rule the law itself was fitted with (flip_thermal_model.py): 0.1 s grid, no launch
                 within 4.5 s, 600 MHz, the first 20 s skipped, the reading smoothed over 3 s, bins of 30 or more

The first-published fields reproduce the committed files byte for byte; the other fields are additions.
"""
import argparse
import gzip
import importlib.util
import json
import math
import os

import numpy as np


def transfer(cards):
    rows = cards["rows"]
    names = [r["values"] for r in rows]
    m = np.array([r["model_switching"] for r in rows])
    a = np.array([r["aifoundry3"]["switching"] for r in rows])
    loo, worst, pair = [], 0.0, None
    for i in range(len(m)):
        s = a[i] / m[i]
        oth = [j for j in range(len(m)) if j != i]
        e = a[oth] - s * m[oth]
        loo.append(float(np.sqrt(np.mean(e ** 2))))
        j = int(np.argmax(np.abs(e)))
        if float(np.abs(e).max()) > worst:
            worst, pair = float(np.abs(e).max()), (names[i], names[oth[j]])
    iw = int(np.argmax(loo))
    return {"loo_scale_rms": loo, "names": names, "median_rms": float(np.median(loo)), "worst": worst,
            "scale_card3": float(m @ a / (m @ m)),
            "worst_rms": loo[iw], "worst_rms_calibrated_on": names[iw],
            "worst_single": worst, "worst_single_calibrated_on": pair[0], "worst_single_predicting": pair[1],
            "ratio_a3_to_model": {"min": float((a / m).min()), "max": float((a / m).max())}}


def law(pw):
    return lambda T: pw["P_fix"] + pw["A_leak_at_80"] * math.exp((T - 80) / pw["T_L"])


def leak_published(session, pw):
    tp = os.path.join(session, "telemetry.jsonl")
    op = (lambda p: gzip.open(p + ".gz", "rt")) if os.path.exists(tp + ".gz") else open
    tel = [json.loads(l) for l in op(tp) if l.startswith("{")]
    runs = [json.loads(l) for l in open(os.path.join(session, "runs.jsonl")) if l.strip()]
    t = np.array([s["t_ms"] for s in tel]) / 1000
    w = np.array([s["board_w"] for s in tel])
    T = np.array([s["temp_c"]["minshire"][0] for s in tel])
    f = np.array([s["mhz"]["minion"] for s in tel])
    keep = f == 600
    for r in runs:
        keep &= ~((t >= r["t_start_ms"] / 1000 - 1) & (t <= r["t_end_ms"] / 1000 + 6))
    bins = {}
    for Tv, wv in zip(T[keep], w[keep]):
        bins.setdefault(int(Tv), []).append(wv)
    L = law(pw)
    curve = [{"T": k, "W": float(np.mean(v)), "card2_law_W": L(k), "n": len(v)} for k, v in sorted(bins.items()) if len(v) >= 20]
    off = [c["W"] - c["card2_law_W"] for c in curve]
    n = np.array([c["n"] for c in curve], float)
    return {"idle_curve": curve, "mean_offset_W": float(np.mean(off)), "rms_W": float(np.sqrt(np.mean(np.square(off)))),
            "mean_offset_W_by_sample": float(np.sum(n * np.array(off)) / n.sum()),
            "rule": "600 MHz samples outside [launch start - 1 s, launch end + 6 s], whole-degree bins with n >= 20; "
                    "mean_offset_W is the unweighted mean of the bins"}


def leak_model_rule(session, pw):
    """flip_thermal_model.py's own idle rule, on its own session loader."""
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "flip_thermal_model.py")
    spec = importlib.util.spec_from_file_location("flip_thermal_model", path)
    ftm = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(ftm)
    s = ftm.load_session(session, {})

    def smooth(x, half=15):   # as flip_thermal_model.py: the reading averaged over 3 s
        pad = np.concatenate([np.full(half, x[0]), x, np.full(half, x[-1])])
        return np.convolve(pad, np.ones(2 * half + 1) / (2 * half + 1), mode="valid")
    busy = np.convolve((s["act"] > 0).astype(float), np.ones(91), mode="same") > 0   # within 4.5 s of any launch
    ok = ~busy & (s["mhz"] == 600)
    ok[:int(20 / ftm.DT)] = False
    bins = {}
    for Tv, Pv in zip(np.round(smooth(s["T"])[ok]), s["P"][ok]):
        bins.setdefault(int(Tv), []).append(Pv)
    L = law(pw)
    curve = [{"T": k, "W": float(np.mean(v)), "card2_law_W": L(k), "n": len(v)} for k, v in sorted(bins.items()) if len(v) >= 30]
    off = [c["W"] - c["card2_law_W"] for c in curve]
    return {"idle_curve": curve, "mean_offset_W": float(np.mean(off)), "rms_W": float(np.sqrt(np.mean(np.square(off)))),
            "rule": "flip_thermal_model.py's idle rule: 0.1 s grid, no launch within 4.5 s, 600 MHz, first 20 s skipped, "
                    "reading smoothed over 3 s, bins with n >= 30; unweighted mean of the bins"}


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--cards", required=True, help="compare_cards.py output (aifoundry3/cards.json)")
    ap.add_argument("--session", required=True, help="the aifoundry3 strict session directory")
    ap.add_argument("--model", required=True, help="the aifoundry2 model.json (its power block is the idle law)")
    ap.add_argument("--transfer", required=True)
    ap.add_argument("--leak", required=True)
    a = ap.parse_args()
    tr = transfer(json.load(open(a.cards)))
    pw = json.load(open(a.model))["power"]
    lk = leak_published(a.session, pw)
    lk["model_rule"] = leak_model_rule(a.session, pw)
    json.dump(tr, open(a.transfer, "w"), indent=1)
    json.dump(lk, open(a.leak, "w"), indent=1)
    print(f"transfer: scale {tr['scale_card3']:.4f}; calibrated on one pattern, rms over the other seven: median "
          f"{tr['median_rms']:.2f} W, worst {tr['worst_rms']:.2f} W (on {tr['worst_rms_calibrated_on']}); largest single "
          f"error {tr['worst_single']:.2f} W ({tr['worst_single_predicting']} from {tr['worst_single_calibrated_on']}); "
          f"a3/model {tr['ratio_a3_to_model']['min']:.3f}-{tr['ratio_a3_to_model']['max']:.3f}")
    print("idle law on aifoundry3 (published rule): " + ", ".join(f"{c['T']} C {c['W'] - c['card2_law_W']:+.3f} W (n={c['n']})" for c in lk["idle_curve"])
          + f"; mean of the bins {lk['mean_offset_W']:+.3f} W, by sample {lk['mean_offset_W_by_sample']:+.3f} W")
    mr = lk["model_rule"]
    print("idle law on aifoundry3 (the model's own rule): " + ", ".join(f"{c['T']} C {c['W'] - c['card2_law_W']:+.3f} W (n={c['n']})" for c in mr["idle_curve"])
          + f"; mean {mr['mean_offset_W']:+.3f} W")


if __name__ == "__main__":
    main()
