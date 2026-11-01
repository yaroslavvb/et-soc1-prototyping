#!/usr/bin/env python3
"""E99 POST HOC, labelled: not registered and not scored. Written after the registered reduction was read, and chosen after seeing it.

    python3 tools/claims-v3/dm/posthoc_fit.py <E99 data dir> --e81 <E81 data dir> --builtins <dir with random.bin, bern50.bin>
        [--out posthoc-fit.json]

Registered contrasts in E99 price a one, a high pin and an encoded toggle directly, and they refute the floor of every fit frozen
before the data. This asks a different question of the same watts: what is the smallest account of all 28 data items, and does it
carry to E75's and E81's images, which it never saw?

Counts, per 64 B line, in the bytes' own order (dm_enc.py, plus the raw and encoded toggles between consecutive W-bit pieces inside a
line, W = 32, 64, 128, here): w, hi, t_enc, half (the 256-bit pieces), r32, r64, r128, e32, e64, e128, and the path counts k_shire, k_chan
(bits changed between two reads of an 8-way and a 16-way path), k_bank (128-way).

The search: a base of w, hi, t_enc, k_shire, k_chan, and 14 extras, each with and without a floor, printed in full. The account chosen
is the base + half + r64 with no floor: a floor adds nothing to it (+0.05 W, 0.061 against 0.063 W rms), half + r64 + e64 fits a little better
(0.052 W) with one more price that separates less, and both extras have a reading on a physical path (64 bits: four beats, one controller clock at
933 MHz; 256 bits: one BL16 burst). Fitted per headline pass, so each price has a t interval. A fit of seven prices to 28 items is a description, with
its out-of-sample check on 18 other points beside it.
"""
import argparse
import hashlib
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "mf"))
from dm_enc import ENC, POP, counts, lines_of  # noqa: E402
from make_mf import image, two_values  # noqa: E402

T975 = {1: 12.706, 2: 4.303, 3: 3.182, 4: 2.776, 5: 2.571, 6: 2.447, 7: 2.365, 8: 2.306}
BASE = ["w", "hi", "t_enc", "k_shire", "k_chan"]
EXTRAS = [[], ["half"], ["r32"], ["r64"], ["r128"], ["e32"], ["e64"], ["e128"], ["half", "r32"], ["half", "r64"], ["half", "r128"],
          ["half", "e64"], ["r64", "e64"], ["half", "r64", "e64"]]
CHOSEN = BASE + ["half", "r64"]


def features(blob):
    L = lines_of(blob)
    f = counts(L)
    out = {k: f[k] for k in ("w", "hi", "t_enc", "t_raw", "half", "k", "k_chan", "k_shire", "k_bank")}
    e9 = ((ENC[L][..., None] >> np.arange(9)) & 1).astype(np.uint8)
    for W in (32, 64, 128):
        nb = W // 8
        P = L.reshape(L.shape[0], 64 // nb, nb)
        out["r%d" % W] = float(POP[P[:, 1:] ^ P[:, :-1]].sum(axis=(1, 2)).mean())
        Q = e9.reshape(L.shape[0], 64 // nb, nb, 9)
        out["e%d" % W] = float((Q[:, 1:] != Q[:, :-1]).sum(axis=(1, 2, 3)).mean())
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("data")
    ap.add_argument("--e81", required=True)
    ap.add_argument("--builtins", required=True)
    ap.add_argument("--out")
    a = ap.parse_args()
    d = json.load(open(os.path.join(a.data, "dm.json")))
    e = json.load(open(os.path.join(a.e81, "dp.json")))
    desk = json.load(open(os.path.join(a.data, "posthoc-desk.json")))
    bern = open(os.path.join(a.builtins, "bern50.bin"), "rb").read()
    rnd = open(os.path.join(a.builtins, "random.bin"), "rb").read()
    if hashlib.sha256(bern).hexdigest() != e["counts"]["dp_bern"]["sha256"] or hashlib.sha256(rnd).hexdigest() != e["counts"]["dp_random"]["sha256"]:
        raise SystemExit("the built-in images are not the ones E81's counts.json describes")

    F = {}
    for n in d["headline"]["items_W"]:
        if n == "dp_zeros":
            continue
        F["e99:" + n] = features(bern if n == "dp_bern" else open(os.path.join(a.data, "gen", "srcs", n + ".bin"), "rb").read())
    for n in ("dp_c1", "dp_s1", "dp_c2", "dp_s2", "dp_c4", "dp_s4", "dp_c2r", "dp_s2r"):
        F["e81:" + n] = features(open(os.path.join(a.e81, "gen", "srcs", n + ".bin"), "rb").read())
    F["e81:dp_random"] = features(rnd)
    F["e81:dp_bern"] = F["e99:dp_bern"]
    for k in (0, 128, 256, 384, 512):
        F["e75:mf_k%d" % k] = features(image(512, 4, *two_values(512, 4, k, 256)))
    for w in (128, 384):
        F["e75:mf_w%d" % w] = features(image(512, 4, *two_values(512, 4, 256, w)))
    F["e75:mf_random"] = F["e81:dp_random"]

    y = {("e99:" + n): d["headline"]["items_over_zeros_W"][n]["mean"] for n in d["headline"]["items_W"] if n != "dp_zeros"}
    for n in ("dp_c1", "dp_s1", "dp_c2", "dp_s2", "dp_c4", "dp_s4", "dp_c2r", "dp_s2r", "dp_random", "dp_bern"):
        y["e81:" + n] = e["headline"]["items_over_zeros_W"][n]["mean"]
    for k, v in desk["measured_W_over_zeros"].items():
        if k.startswith("mf_"):
            y["e75:" + k] = v
    lr = d["headline"]["lines_per_s"]
    pj = lambda v: v / lr * 1e12
    names = list(y)
    new = [n for n in names if n.startswith("e99:")]
    old = [n for n in names if not n.startswith("e99:")]
    Yn = np.array([y[n] for n in new])
    Yo = np.array([y[n] for n in old])

    def design(ns, terms, floor):
        return np.vstack(([np.ones(len(ns))] if floor else []) + [[F[n][t] for n in ns] for t in terms]).T

    print("E99 POST HOC: every image's counts, sorted by watts over its own zeros")
    cols = ["w", "hi", "t_enc", "t_raw", "r32", "r64", "r128", "half", "e64", "k_shire", "k_chan", "k_bank"]
    print("%-14s %6s " % ("image", "W") + " ".join("%6s" % c for c in cols))
    for n in sorted(names, key=lambda k: y[k]):
        print("%-14s %6.3f " % (n, y[n]) + " ".join("%6.0f" % F[n][c] for c in cols))

    res = {"note": "POST HOC, labelled", "counts": F, "measured_W_over_zeros": y, "line_rate_per_s": lr, "search": {}}
    print("\nThe search, fitted on E99's %d data items only: rms there, and rms on E75's and E81's %d points it never saw" % (len(new), len(old)))
    for ex in EXTRAS:
        for floor in (False, True):
            terms = BASE + ex
            X = design(new, terms, floor)
            coef, *_ = np.linalg.lstsq(X, Yn, rcond=None)
            r = Yn - X @ coef
            ro = Yo - design(old, terms, floor) @ coef
            rms, rmso = float(np.sqrt(np.mean(r ** 2))), float(np.sqrt(np.mean(ro ** 2)))
            cs = coef[1:] if floor else coef
            key = "+".join(ex or ["base"]) + ("+floor" if floor else "")
            print("%-22s rms %.3f | others %.3f | %s%s" % (key, rms, rmso, ("floor %+.2f W " % coef[0]) if floor else "",
                                                          " ".join("%s %.2f" % (t, pj(v)) for t, v in zip(terms, cs))))
            res["search"][key] = {"rms_W": rms, "rms_out_of_sample_W": rmso, "floor_W": float(coef[0]) if floor else None,
                                  "prices_pJ": {t: float(pj(v)) for t, v in zip(terms, cs)}}

    # the chosen account, per headline pass
    passes = [str(p) for p in d["passes_headline"]]
    X = design(new, CHOSEN, False)
    per = []
    for p in passes:
        row = d["per_pass"][p]["items_W"]
        Y = np.array([row[n[4:]] - row["dp_zeros"] for n in new])
        per.append(np.linalg.lstsq(X, Y, rcond=None)[0])
    per = np.array(per)
    coef = per.mean(axis=0)
    half = T975[len(passes) - 1] * per.std(axis=0, ddof=1) / np.sqrt(len(passes))
    r = Yn - X @ coef
    ro = Yo - design(old, CHOSEN, False) @ coef
    print("\nThe account chosen (no floor), fitted per headline pass %s:" % passes)
    for t, v, h in zip(CHOSEN, coef, half):
        print("  %-8s %6.2f pJ per count [+-%.2f]" % (t, pj(v), pj(h)))
    print("  rms %.3f W on E99's items, %.3f W out of sample on E75's and E81's" % (np.sqrt(np.mean(r ** 2)), np.sqrt(np.mean(ro ** 2))))
    print("  residuals on E99:", " ".join("%s %+.2f" % (new[i][4:].replace("dm_", "").replace("dp_", "*"), r[i]) for i in np.argsort(-np.abs(r))))
    print("  residuals on the others:", " ".join("%s %+.2f" % (old[i].replace("dp_", "").replace("mf_", "m"), ro[i]) for i in np.argsort(-np.abs(ro))))
    res["chosen"] = {"terms": CHOSEN, "prices_pJ": {t: float(pj(v)) for t, v in zip(CHOSEN, coef)},
                     "prices_half_pJ": {t: float(pj(h)) for t, h in zip(CHOSEN, half)},
                     "rms_W": float(np.sqrt(np.mean(r ** 2))), "rms_out_of_sample_W": float(np.sqrt(np.mean(ro ** 2))),
                     "residuals_W": {n: float(v) for n, v in zip(new, r)}, "residuals_old_W": {n: float(v) for n, v in zip(old, ro)}}

    def parts(n):
        return {t: float(v * F[n][t]) for t, v in zip(CHOSEN, coef)}

    print("\nWhat the chosen account makes of E81's and E75's steps (W):")
    a_, b_, c_ = "e81:dp_c2", "e81:dp_s2", "e81:dp_bern"
    res["steps"] = {}
    for label, plus, minus, meas in (("E81's arrangement, s2 - c2", b_, a_, y[b_] - y[a_]), ("E81's period, bern - s2", c_, b_, y[c_] - y[b_]),
                                     ("E81's whole step, bern - c2", c_, a_, y[c_] - y[a_]), ("zeros to random floats", "e81:dp_random", None, y["e81:dp_random"])):
        P = parts(plus)
        M = parts(minus) if minus else {t: 0.0 for t in CHOSEN}
        D = {t: P[t] - M[t] for t in CHOSEN}
        print("  %-30s measured %+.3f, account %+.3f: %s" % (label, meas, sum(D.values()), " ".join("%s %+.3f" % kv for kv in D.items())))
        res["steps"][label] = {"measured_W": meas, "account_W": sum(D.values()), "parts_W": D}

    # the ladder alone: ten rungs that differ only in what the paths see
    ladder = [n for n in new if n.startswith("e99:dm_L")]
    res["ladder"] = {}
    print("\nThe ladder alone, per pass, floor + path counts (labelled, as above):")
    for terms in (["k_chan"], ["k_shire"], ["k_shire", "k_chan"], ["k_shire", "k_chan", "k_bank"]):
        X = design(ladder, terms, True)
        per = []
        for p in passes:
            row = d["per_pass"][p]["items_W"]
            Y = np.array([row[n[4:]] - row["dp_zeros"] for n in ladder])
            per.append(np.linalg.lstsq(X, Y, rcond=None)[0])
        per = np.array(per)
        c = per.mean(axis=0)
        h = T975[len(passes) - 1] * per.std(axis=0, ddof=1) / np.sqrt(len(passes))
        Ym = np.array([y[n] for n in ladder])
        rr = Ym - X @ c
        print("  %-26s rms %.3f W | floor %.3f W | %s" % ("+".join(terms), np.sqrt(np.mean(rr ** 2)), c[0],
                                                         " ".join("%s %.2f pJ [+-%.2f]" % (t, pj(v), pj(q)) for t, v, q in zip(terms, c[1:], h[1:]))))
        res["ladder"]["+".join(terms)] = {"rms_W": float(np.sqrt(np.mean(rr ** 2))), "floor_W": float(c[0]),
                                          "prices_pJ": {t: float(pj(v)) for t, v in zip(terms, c[1:])},
                                          "prices_half_pJ": {t: float(pj(q)) for t, q in zip(terms, h[1:])}}
    if a.out:
        json.dump(res, open(a.out, "w"), indent=1, sort_keys=True)


if __name__ == "__main__":
    main()
