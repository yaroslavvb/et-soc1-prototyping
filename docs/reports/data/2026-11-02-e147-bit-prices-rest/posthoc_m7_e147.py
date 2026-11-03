#!/usr/bin/env python3
# /// script
# requires-python = ">=3.9"
# dependencies = ["numpy"]
# ///
"""E147, after verification (Mon 2 Nov 2026; post hoc, labelled, unregistered, no verdict): M7's steps at E147's items.

M7 (Q138(m), frozen at lab 3a210f2b, 19:21:05 PST, before E147's registration c41c3905 at 20:12:58 PST) was not named in
E147's registration, so this score was computed after E147's data (b2348e11). Nothing is refitted or tuned: Q138(m)'s
predict_blind5.py, unchanged since 3a210f2b, prices E147's 73 committed tiles on aifoundry3 with m7.json, m6.json and m5.json
as frozen.

    python3 docs/reports/data/2026-11-02-e147-bit-prices-rest/posthoc_m7_e147.py [--pool <dir>]
        a python with numpy, as predict_blind5.py's header asks; --pool defaults to build/e147-m7-pool (git ignores build/)

1. The pool: <pool>/blind5.json lists E147's 73 tiles (tools/claims-v3/e147/e147/e147-tiles.json; each file by its path
   relative to the pool, sha256 as registered), and <pool>/counts-e147-merged.json holds the fixed RTL bench's counts of them:
   E147's (bench/counts-e147.json) plus E134's for the three tiles E147 reused without re-counting (a67q, bj_16, bp_16),
   merged the way tools/claims-v3/e147/predict_m6_e147.py merges them.
2. predict_blind5.py <pool> aifoundry3 --counts <merged> --out posthoc/predict_blind5/ writes each tile's D (board W over
   fp32 zeros at 600 MHz on aifoundry3) by M7, M6 and M5.
3. A step is D(item) - D(its own zero) (predictions-e147.json > items > zero). The measured step is scored.json > primary >
   prices > <item> > W > mean. Before anything is scored, M6's and M5's steps from these D's are checked against E147's
   registered frozen steps (predictions-e147.json > items > pred_W) to 0.001 W; the script stops if they differ.
4. Over E147's registered lists (predictions-e147.json > lists): rms and bias of measured - model (W); the exponent's
   measured / model sums; per flip (fJ), each model's step at M6's own registered fJ per W for that item
   (m6_fJ_per_flip / pred_W.m6, the same flips and rate) against scored.json's fJ; the swings and word contrasts as
   make_predictions_e147.py forms them (all-in - 4096/3968 x balanced on B, 2048/1920 on A; W67 - W79); and, descriptive
   only, M7's band without its coefficient term (band_k x its nested rms for fp32 on aifoundry3).
Writes posthoc/m7-e147.json and posthoc/m7-e147.txt.
SPDX-License-Identifier: Apache-2.0
"""
import argparse
import hashlib
import json
import math
import os
import statistics
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
E147 = os.path.join(ROOT, "tools", "claims-v3", "e147")
Q138M = os.path.join(ROOT, "docs", "reports", "data", "2026-11-02-q138m-model")
E134_COUNTS = os.path.join(ROOT, "docs", "reports", "data", "2026-11-02-e134-bit-prices-more", "bench", "counts-e134.json")
SCALE = {"B": 4096 / 3968, "A": 2048 / 1920}
MODELS = ("M7", "M6", "M5")
REL = lambda p: os.path.relpath(p, ROOT)  # noqa: E731


def fsha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def bare(n):
    return n.split(".", 1)[1] if n.startswith("fp32.") else n


def build_pool(pool):
    spec = json.load(open(os.path.join(E147, "e147", "e147-tiles.json")))["tiles"]
    os.makedirs(pool, exist_ok=True)
    man = {"_note": "E147 post hoc (posthoc_m7_e147.py): E147's 73 registered tiles as a predict_blind5.py pool", "tiles": []}
    for name, t in sorted(spec.items()):
        man["tiles"].append({"name": name, "type": "fp32", "file": os.path.relpath(os.path.join(E147, "e147", t["file"]), pool),
                             "sha256": {"whole": t["sha256"]}, "priority": None, "case": None})
    json.dump(man, open(os.path.join(pool, "blind5.json"), "w"), indent=1)
    c147 = json.load(open(os.path.join(HERE, "bench", "counts-e147.json")))["rows"]
    c134 = json.load(open(E134_COUNTS))["rows"]
    rows, taken = dict(c147), []
    for n in spec:
        if n in rows or bare(n) in rows:
            continue
        r = c134.get(n) or c134.get(bare(n))
        if r is None:
            raise SystemExit(f"no bench count for {n} in E147's or E134's counts")
        rows[n] = r
        taken.append(n)
    cpath = os.path.join(pool, "counts-e147-merged.json")
    json.dump({"rows": rows}, open(cpath, "w"))
    return len(spec), sorted(taken), cpath


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pool", default=os.path.join(ROOT, "build", "e147-m7-pool"))
    a = ap.parse_args()
    pool = os.path.abspath(a.pool)
    n_tiles, taken, cpath = build_pool(pool)
    pdir = os.path.join(HERE, "posthoc", "predict_blind5")
    pb5 = os.path.join(Q138M, "predict_blind5.py")
    r = subprocess.run([sys.executable, pb5, pool, "aifoundry3", "--counts", cpath, "--out", pdir],
                       stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    if r.returncode != 0:
        raise SystemExit(f"predict_blind5.py exit {r.returncode}:\n{r.stderr}")
    pred = json.load(open(os.path.join(pdir, "predictions-aifoundry3.json")))
    bad = [n for n, t in pred["tiles"].items() if "error" in t or t.get("sha256_matches_manifest") is not True]
    if bad:
        raise SystemExit(f"tiles without a price or with a hash that differs from the registration: {bad}")
    reg = json.load(open(os.path.join(E147, "predictions-e147.json")))
    sc = json.load(open(os.path.join(HERE, "scored.json")))["primary"]
    prices = sc["prices"]
    D = {n: {m: t[m]["D_w"] for m in MODELS} for n, t in pred["tiles"].items()}

    def step(m, item):
        return D[item][m] - D[reg["items"][item]["zero"]][m]

    worst = {"M6": 0.0, "M5": 0.0}
    for item, it in reg["items"].items():
        for m, k in (("M6", "m6"), ("M5", "m5")):
            worst[m] = max(worst[m], abs(step(m, item) - it["pred_W"][k]))
    if max(worst.values()) > 0.001:
        raise SystemExit(f"M6/M5 steps from predict_blind5.py differ from E147's registered frozen steps: {worst}")

    items, raw = {}, {}  # items: rounded, for the output file; raw: unrounded, for every statistic
    for item, it in reg["items"].items():
        b = bare(item)
        p = prices[b]
        conv = it["m6_fJ_per_flip"] / it["pred_W"]["m6"]
        q = {"measured_w": p["W"]["mean"], "measured_fJ": p["fJ"]["mean"]}
        rec = {"zero": bare(it["zero"]), "measured_w": round(p["W"]["mean"], 4), "measured_fJ": round(p["fJ"]["mean"], 2),
               "fJ_per_w": round(conv, 4)}
        for m in MODELS:
            s = step(m, item)
            q[f"{m}_step_w"], q[f"{m}_err_w"], q[f"{m}_fJ"] = s, p["W"]["mean"] - s, s * conv
            rec[f"{m}_step_w"] = round(s, 4)
            rec[f"{m}_err_w"] = round(p["W"]["mean"] - s, 4)
            rec[f"{m}_fJ"] = round(s * conv, 2)
        items[b], raw[b] = rec, q

    def stats(names, m):
        e = [raw[n][f"{m}_err_w"] for n in names]
        return {"n": len(e), "rms_w": round(math.sqrt(sum(x * x for x in e) / len(e)), 5), "bias_w": round(sum(e) / len(e), 5)}

    lists = {}
    for lst, names in reg["lists"].items():
        names = [bare(n) for n in names]
        lists[lst] = {m: stats(names, m) for m in MODELS}
    ex = [bare(n) for n in reg["lists"]["exponent_new"]]
    new = [bare(n) for n in reg["lists"]["new_items"]]
    ratio = {m: round(sum(raw[n]["measured_w"] for n in ex) / sum(raw[n][f"{m}_step_w"] for n in ex), 4) for m in MODELS}
    per_flip = {}
    for m in MODELS:
        e = [raw[n]["measured_fJ"] - raw[n][f"{m}_fJ"] for n in new]
        rel = [abs(x) / raw[n]["measured_fJ"] for x, n in zip(e, new)]
        per_flip[m] = {"rms_fJ": round(math.sqrt(sum(x * x for x in e) / len(e)), 1), "bias_fJ": round(sum(e) / len(e), 1),
                       "median_abs_share_of_measured": round(statistics.median(rel), 4)}
    m7 = json.load(open(os.path.join(Q138M, "m7.json")))
    fam = m7["families"]["float"]
    k = fam["band_k"]
    pool_rms = fam["interval_pool_by_format_card"]["fp32|a3"]["rms_w"]
    hw = k * pool_rms
    inside = sum(1 for n in new if abs(raw[n]["M7_err_w"]) <= hw)
    largest = sorted(((n, round(raw[n]["M7_err_w"], 4)) for n in new), key=lambda x: -abs(x[1]))[:8]

    contrasts = {}
    cw = sc["statistics"]["contrasts_W"]
    for name, c in reg["contrasts_pred_W"].items():
        if name.startswith("A_word_"):
            lay, j = name.split("_")[2], name.split("_")[3]
            a_, b_ = (f"a67j_{j}", f"aj_{j}") if lay == "allin" else (f"a67p_{j}", f"ap_{j}")
            pm = {m: raw[a_][f"{m}_step_w"] - raw[b_][f"{m}_step_w"] for m in MODELS}
        else:
            side, j = name.split("_")[0], name.split("_")[2]
            aj, ap_ = ("aj", "ap") if side == "A" else ("bj", "bp")
            pm = {m: raw[f"{aj}_{j}"][f"{m}_step_w"] - SCALE[side] * raw[f"{ap_}_{j}"][f"{m}_step_w"] for m in MODELS}
        meas = cw.get(name, {}).get("mean")
        row = {"measured_w": None if meas is None else round(meas, 4)}
        for m in MODELS:
            row[f"{m}_w"] = round(pm[m], 4)
            row[f"measured_over_{m}"] = None if meas is None or abs(pm[m]) < 1e-9 else round(meas / pm[m], 3)
        row["registered_M6_w"] = c.get("m6")
        contrasts[name] = row
    worst_c = max(abs(contrasts[n]["M6_w"] - contrasts[n]["registered_M6_w"]) for n in contrasts)

    out = {"_note": ("E147, after verification, Mon 2 Nov 2026: M7's frozen steps at E147's items, computed after the data "
                     "(post hoc, labelled, unregistered, no verdict). M7 = Q138(m), frozen at 3a210f2b (19:21:05 PST), before "
                     "E147's registration c41c3905 (20:12:58 PST), which named M6 and M5 only. Nothing refitted or tuned."),
           "inputs": {REL(p): fsha(p) for p in (os.path.join(Q138M, "m7.json"), pb5, os.path.join(Q138M, "fit_m7.py"),
                                                os.path.join(E147, "predictions-e147.json"), os.path.join(HERE, "scored.json"),
                                                os.path.join(E147, "e147", "e147-tiles.json"),
                                                os.path.join(HERE, "bench", "counts-e147.json"), E134_COUNTS)},
           "pool": {"tiles": n_tiles, "counts_from_E134": taken, "manifest_sha256": pred["manifest_sha256"],
                    "counts_sha256": pred["counts_sha256"]},
           "m7_float_form": {"form": fam.get("form") or fam.get("chosen_form"), "terms": fam["terms"]},
           "consistency_worst_abs_w": {"M6_steps_vs_registered": round(worst["M6"], 5), "M5_steps_vs_registered": round(worst["M5"], 5),
                                       "M6_contrasts_vs_registered": round(worst_c, 5)},
           "lists": lists, "exponent_measured_over_model": ratio, "per_flip_new_items": per_flip,
           "m7_band_without_coef_term": {"band_k": k, "pool_fp32_a3_rms_w": pool_rms, "half_width_w": round(hw, 4),
                                         "inside_of_68": inside, "what": "descriptive only: band_k x M7's nested rms for fp32 on "
                                         "aifoundry3, the analogue of the 1.96 x 0.2448 = 0.480 W row band E147 reports for M6"},
           "m7_largest_misses_w": [[n, e] for n, e in largest], "contrasts": contrasts, "items": items}
    os.makedirs(os.path.join(HERE, "posthoc"), exist_ok=True)
    json.dump(out, open(os.path.join(HERE, "posthoc", "m7-e147.json"), "w"), indent=1, sort_keys=True)

    L = ["# E147 post hoc (after verification, Mon 2 Nov 2026): M7's frozen steps at E147's items, unregistered, no verdict", "",
         "M7 = Q138(m) at 3a210f2b (19:21:05 PST), before E147's registration c41c3905 (20:12:58 PST); predict_blind5.py on "
         "aifoundry3, nothing refitted. Measured from scored.json > primary > prices; a step is D(item) - D(own zero).", "",
         f"consistency: M6's and M5's steps from predict_blind5.py against E147's registered frozen steps, worst "
         f"{worst['M6']:.5f} / {worst['M5']:.5f} W; M6's contrasts {worst_c:.5f} W", "",
         f"M7's float form {out['m7_float_form']['form']}: terms {', '.join(fam['terms'])}", "",
         "| list | n | M7 rms (bias), W | M6 rms (bias), W | M5 rms (bias), W |", "|---|---:|---|---|---|"]
    for lst in reg["lists"]:
        s = lists[lst]
        L.append(f"| {lst} | {s['M7']['n']} | " + " | ".join(f"{s[m]['rms_w']:.3f} ({s[m]['bias_w']:+.3f})" for m in MODELS) + " |")
    L += ["", "exponent_new, measured / model (sums of the 20 steps): " + ", ".join(f"{m} {ratio[m]:.3f}" for m in MODELS),
          "per flip over the 68 new items (fJ): " + "; ".join(
              f"{m} rms {per_flip[m]['rms_fJ']:.0f}, bias {per_flip[m]['bias_fJ']:+.0f}, median |error| "
              f"{100 * per_flip[m]['median_abs_share_of_measured']:.0f}% of the measured price" for m in MODELS),
          f"M7's band without its coefficient term, {k:.3f} x {pool_rms:.4f} = +-{hw:.3f} W: {inside} of 68 inside (descriptive)",
          "M7's largest misses (measured - M7, W): " + ", ".join(f"{n} {e:+.3f}" for n, e in largest), "",
          "| contrast | measured, W | M7 | M6 | M5 | measured / M7 | measured / M6 |", "|---|---:|---:|---:|---:|---:|---:|"]
    for name, c in contrasts.items():
        mm = "—" if c["measured_w"] is None else f"{c['measured_w']:+.3f}"
        f = lambda v: "—" if v is None else f"{v:.2f}"  # noqa: E731
        L.append(f"| {name} | {mm} | {c['M7_w']:+.3f} | {c['M6_w']:+.3f} | {c['M5_w']:+.3f} | {f(c['measured_over_M7'])} | {f(c['measured_over_M6'])} |")
    open(os.path.join(HERE, "posthoc", "m7-e147.txt"), "w").write("\n".join(L) + "\n")
    print("\n".join(L))


if __name__ == "__main__":
    main()
