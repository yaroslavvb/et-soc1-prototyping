#!/usr/bin/env python3
# /// script
# requires-python = ">=3.9"
# dependencies = ["numpy"]
# ///
"""Q142(h2): M11's refit on the committed rows for (c) HC1, card 1's heat scale, and (d) I8P, card 1's paired-anchor int8 term,
exactly as tools/claims-v3/m11/REGISTRATION.md (lab 3c31a91d) sections 8, 9 and 10 and its dated amendment A1
(REGISTRATION.md.dated-note-1.md, f49b7ddd; A1-1 and A1-3) state them: each term's entry clauses and the not-wanted clauses that the
committed rows can read, decided by the registered rules as numbers. Held out, not blind; no E171-E174 data is read. M11's (a) (heat
over minutes) is not touched here: it is decided by M11's own hold sessions only.

    python3 -B refit_m11_cd.py --out <file.json> --txt <file.txt>

Every fit is M10's committed code, unchanged (docs/reports/data/2026-11-04-q142m-m10/fit_m10.py, imported after its 174 registered
inputs and M11's three lists pass):
  (c) fit_m10.heat_c1 on fit_m10.assemble's 959 rows: the 4.5 s law refitted in each leave-one-kind-out fold, each session's scale h
      the median over its random anchors (M10 REGISTRATION section 3a's) of dT_win / the law with the held-out kind's anchors left out,
      card 1's 448 heat rows judged. Its output is first checked against heldout-m10.json's committed heat_c1 block (every field but
      the end-to-end block, which needs the power fits). Then the three entry clauses:
        pooled: card 1's held-out rms with h minus without <= -0.010 C, its 95% paired bootstrap over kinds (2,000 draws, seed 142)
                below 0 (heat_c1's per_card block, M10's own boot);
        two thirds: the difference <= 0 in at least two thirds of card 1's sessions with at least 10 heat rows (3 x count >= 2 x n);
        bias: card 1's heat bias does not change sign and grow in size.
      HC1's not-wanted clauses are both blind (HC1-B WORSE; over-correction on a new card-1 session's N1): read_hc1b_i8pb.py reads
      them on E172.
  (d) fit_m10.Fit10 on the int8 family (M10's B: no session scale; prices and the card term refitted in each fold) with
      fit_m10.assemble_anchors' int8 anchors; its held-out errors are first checked against rows-m10.json's err_w[B]. k(s, r) per pair
      in each fold: the median, over the int8 random anchors run in both the card-1 session s and its paired aifoundry3 session r
      (by name, each name one tile: E78's built-in int8.full, pool 6's and pool 7's single committed files) and not of the held-out
      kind, of [D_s(a) / Dhat_s(a)] / [D_r(a) / Dhat_r(a)], Dhat the fold's prediction of the anchor (its rate x the fold's prices x
      its features, x the fold's card term in s); no anchor left: k = 1 (M10's rule). The rows: the nine pairs' card-1 int8 rows,
      each predicted k x M10's fold prediction; card 1's other int8 rows keep M10's. The entry clauses:
        pooled: over the paired sessions' card-1 int8 rows, held-out rms with k minus without <= -0.010 W, its 95% paired bootstrap
                over kinds (2,000 draws, seed 142) below 0;
        E164: E164's priority-1 int8 bias falls in size and keeps its sign;
        every card-1 int8 row: the rms rises by no more than 0.001 W.
      Not wanted (any of; read here where the committed rows can read it):
        over-correction: the bias changes sign and grows, on E164's int8 rows or over the paired sessions' card-1 int8 rows;
        the spread (A1-3): the sd of k over the nine pairs is no larger than the sd of k that drawing each anchor's D as
          D + se x N(0, 1) gives (2,000 draws, seed 142), in M10's own form (section7_m10.median_noise and spread_by_card: each pair's
          k drawn with every anchor's D in both sessions moved by its se, the model value held; the pairs' expected sd the rms
          of their sds; pairs with an anchor without an se left out of both and named). Met: a constant card term would do as
          well, so I8P is a reported arm; the constant, the card term x the median k over the pairs, is reported with its 95%
          interval (a bootstrap over the pairs, 2,000 draws, seed 142), never carried;
        I8P-B WORSE: blind, read by read_hc1b_i8pb.py on E172 with E171.
      "Each pair's k in its own fold": the prices cancel in k (one anchor tile has the same features in both sessions), so a pair's k
      in a fold is its all-rows k times the all-rows card term over the fold's, the same for every pair of the fold; the spread's
      verdict is therefore read on the all-rows fit (M10's own form reads its scales there), and the same reading in every fold is
      reported beside: identical to rounding wherever the fold reads every anchor, and named where the held-out kind (int8.full's) takes
      anchors away.
One way only (section 10): a not-wanted clause never brings in a term that failed its entry; a term that enters and meets one is a
reported arm, never the primary.

Standard library and numpy (fit_m10's). SPDX-License-Identifier: Apache-2.0
"""
import os

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS", "NUMEXPR_NUM_THREADS"):
    os.environ.setdefault(_v, "1")
import argparse  # noqa: E402
import hashlib  # noqa: E402
import json  # noqa: E402
import math  # noqa: E402
import statistics  # noqa: E402
import sys  # noqa: E402
import warnings  # noqa: E402

sys.dont_write_bytecode = True
import numpy as np  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
TOP = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
M10D = os.path.join(TOP, "docs", "reports", "data", "2026-11-04-q142m-m10")
M11_LISTS = (("SHA256SUMS", 58), ("SHA256SUMS-m11", 6), ("SHA256SUMS-a1", 9))
PAIRS = (("E82", "E78"), ("E91", "E86"), ("E131", "E95"), ("E93", "E121"), ("E108", "E122"), ("E94", "E123"), ("E142", "E141"),
         ("E157", "E153"), ("E164", "E163"))
C1_CARD = "aifoundry1-c1"
SEED, NB = 142, 2000
LOG = []
sha = lambda p: hashlib.sha256(open(p, "rb").read()).hexdigest()  # noqa: E731


def log(s):
    print(s, flush=True)
    LOG.append(s)


def rms(v):
    v = [float(x) for x in v]
    return math.sqrt(sum(x * x for x in v) / len(v)) if v else None


def mean(v):
    v = [float(x) for x in v]
    return sum(v) / len(v) if v else None


def overcorrects(b0, b1):
    return bool(b0 * b1 < 0 and abs(b1) > abs(b0))


def check_m11_lists():
    got, bad = {}, []
    for name, n in M11_LISTS:
        lines = [ln.split(None, 1) for ln in open(os.path.join(HERE, name)) if ln.strip()]
        if len(lines) != n:
            bad.append(f"{name}: {len(lines)} lines")
        for h, p in lines:
            q = os.path.join(TOP, p.strip())
            if not os.path.isfile(q) or sha(q) != h:
                bad.append(f"{name}: {p.strip()}")
        got[name] = len(lines)
    if bad:
        raise SystemExit("M11 REFIT STOPPED: M11's frozen inputs differ: " + "; ".join(bad[:6]))
    return got


# ------------------------------------------------------------------------------------------------- (c) HC1
HC1_COMPARE = ("n_rows", "n_kinds", "n_sessions", "n_anchor_rows", "rows_by_session", "M7_law_as_frozen", "base_refit_loko",
               "with_session_heat_scale_loko", "refit_coef_all_rows", "M7_coef", "session_heat_scales_all_rows",
               "paired_bootstrap_sessscale_minus_base", "per_card", "enters", "rule")


def hc1(FM, rows, held):
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")            # the end-to-end block's empty slices (no held-out D is passed)
        c1, hr, eb, es = FM.heat_c1(rows, lambda s: None, {})
    ref = held["heat_c1"]
    same = {k: json.loads(json.dumps(c1[k])) == ref[k] for k in HC1_COMPARE}
    if not all(same.values()):
        raise SystemExit(f"M11 REFIT STOPPED: fit_m10.heat_c1 does not reproduce heldout-m10.json: {[k for k, v in same.items() if not v]}")
    cds = np.array([r["card"] for r in hr])
    m1 = cds == C1_CARD
    sess = sorted({r["sess"] for r in hr if r["card"] == C1_CARD})
    per = {}
    for s in sess:
        idx = np.array([r["sess"] == s for r in hr])
        n = int(idx.sum())
        d = rms(es[idx]) - rms(eb[idx])
        per[s] = {"n_rows": n, "rms_without_c": rms(eb[idx]), "rms_with_c": rms(es[idx]), "d_c": d,
                  "h_all_rows": ref["session_heat_scales_all_rows"].get(s), "judged": n >= 10, "d_le_0": bool(d <= 0)}
    judged = [s for s in sess if per[s]["judged"]]
    k = sum(1 for s in judged if per[s]["d_le_0"])
    pc = ref["per_card"][C1_CARD]
    b0, b1 = float(np.mean(eb[m1])), float(np.mean(es[m1]))
    cl = {"pooled": {"d_rms_c": pc["d_rms_w"], "lo95": pc["lo95"], "hi95": pc["hi95"], "n_kinds": pc["n_kinds"], "n_rows": pc["n_rows"],
                     "rule": "d <= -0.010 C and the 95% interval below 0", "passes": bool(pc["d_rms_w"] <= -0.010 and pc["hi95"] < 0)},
          "two_thirds": {"sessions_judged": len(judged), "d_le_0": k, "needed": math.ceil(2 * len(judged) / 3),
                         "sessions_left_out_under_10_rows": sorted(s for s in sess if not per[s]["judged"]),
                         "worse_with_h": sorted(s for s in judged if not per[s]["d_le_0"]),
                         "rule": "d <= 0 in at least two thirds of card 1's sessions with at least 10 heat rows (3 x count >= 2 x n)",
                         "passes": bool(3 * k >= 2 * len(judged))},
          "bias": {"bias_without_c": b0, "bias_with_c": b1, "sign_changes": bool(b0 * b1 < 0), "grows": bool(abs(b1) > abs(b0)),
                   "rule": "does not change sign and grow in size", "passes": not overcorrects(b0, b1)}}
    enters = all(v["passes"] for v in cl.values())
    a3 = cds == "aifoundry3"
    out = {"reproduces_heldout_m10_heat_c1": same, "rows": {"card1": int(m1.sum()), "aifoundry3": int(a3.sum()), "card1_sessions": len(sess)},
           "entry": cl, "enters": enters, "per_session_card1": per,
           "card1_rms": {"without_c": rms(eb[m1]), "with_c": rms(es[m1])},
           "card1_by_format": {t: {"without": ref["base_refit_loko"].get(f"{t}|{C1_CARD}"), "with": ref["with_session_heat_scale_loko"].get(f"{t}|{C1_CARD}")}
                               for t in ("fp32", "fp16", "int8")},
           "aifoundry3_reported_unscaled": {"n": int(a3.sum()), "rms_c": rms(eb[a3]), "bias_c": float(np.mean(eb[a3])),
                                            "with_a_session_scale_beside_rms_c": rms(es[a3]), "note": "aifoundry3 keeps h = 1 (section 8)"},
           "not_wanted": {"HC1-B WORSE": "blind: read_hc1b_i8pb.py on E172", "over-correction on a new card-1 session's N1":
                          "blind: read_hc1b_i8pb.py on E172's N1"},
           "frozen_form": {"card": "aifoundry1 card 1 only; aifoundry3 keeps h = 1",
                           "law": "m10.json heat_4p5s (H2_per_card_runlength), its coefficients unchanged: no refit",
                           "law_coef": json.load(open(os.path.join(M10D, "m10.json")))["heat_4p5s"]["coef"],
                           "m10_json_sha256": sha(os.path.join(M10D, "m10.json")),
                           "h1": "the median, over the session's random anchors (M10 REGISTRATION section 3a's set where the session ran them, "
                                 "plus pool 8's six scale-role anchors in a pool-8 session; never a check or a zeros anchor), of dT_win / "
                                 "the law at the anchor's measured S and run length; 1 if none",
                           "nothing_new_fitted": True}}
    return out


# ------------------------------------------------------------------------------------------------- (d) I8P
def i8p(FM, rows, held):
    m9 = FM.load(os.path.join(FM.M9D, "m9.json"))
    zeros, zr = FM.M7.zeros_counts(), FM.M9.zeros_rows()
    anchors, chk6 = FM.assemble_anchors(rows, zeros, zr)
    fr = [r for r in rows if FM.fam_of(r["type"]) == "int8"]
    terms = m9["families"]["int8"]["terms"]
    anc = {s: [x for x in v if FM.fam_of(x["type"]) == "int8"] for s, v in anchors.items()}
    ft = FM.Fit10(fr, terms, anc, False)
    e, p, betas, scs, cs = ft.loko()
    fall = ft.fit(None)
    # the reproduction: M10's committed held-out errors (6 decimals), its card term and prices
    ref = {(r["exp"], r["key"]): r["err_w"]["B"] for r in json.load(open(os.path.join(M10D, "rows-m10.json"))) if r["type"] == "int8"}
    worst = max(abs(float(e[i]) - ref[(r["exp"], r["key"])]) for i, r in enumerate(fr))
    m10 = json.load(open(os.path.join(M10D, "m10.json")))["families"]["int8"]
    # M10's committed prices were fitted on another machine's numpy: equal to a relative 1e-9 (predict_m10's self-test bound), not bit for bit
    coef_rel = max(abs(float(v) - w) / abs(w) for v, w in zip(fall["b"] / ft.sc, m10["coef_J"]))
    coef_same = coef_rel <= 1e-9
    c_same = abs(float(fall["c"]) - m10["card1_scale"]) / m10["card1_scale"] <= 1e-9
    if worst > 5.1e-7 or not coef_same or not c_same or len(fr) != held["power"]["int8"]["n_rows"]:
        raise SystemExit(f"M11 REFIT STOPPED: Fit10 on the int8 rows does not reproduce M10's B ({worst}, {coef_same}, {c_same})")
    # anchors per session: name -> (D, scaled features x rate, kind id, se)
    sx = {s: i for i, s in enumerate(ft.sessions)}
    A = {}
    for si_, xa, D, ak, name in ft.anc:
        sess = ft.sessions[si_]
        se = ((FM.footing_items(sess.split("|")[0]) or {}).get(name) or {}).get("D", {})
        se = se.get("se") if isinstance(se, dict) else None
        A.setdefault(sess, {})[name] = {"D": float(D), "xa": xa, "ak": int(ak), "se": (float(se) if se is not None else None),
                                        "c1": bool(ft.sess_c1[si_])}

    def dhat(a, b, c):
        return float(a["xa"] @ b) * (c if a["c1"] else 1.0)

    def k_of(sig, rho, b, c, k_out=None):
        q = {}
        for n in sorted(set(A.get(sig, {})) & set(A.get(rho, {}))):
            a, r = A[sig][n], A[rho][n]
            if k_out is not None and (a["ak"] == k_out or r["ak"] == k_out):
                continue
            ds, dr = dhat(a, b, c), dhat(r, b, c)
            if ds > 0 and dr > 0:
                q[n] = (a["D"] / ds) / (r["D"] / dr)
        return (statistics.median(q.values()) if q else None), q

    pairs = [(f"{s}|c1", f"{r}|a3") for s, r in PAIRS]
    for sig, rho in pairs:
        if sig not in sx or rho not in sx:
            raise SystemExit(f"M11 REFIT STOPPED: {sig} or {rho} is not a session of the int8 fit")
    pair_of = {sig: rho for sig, rho in pairs}
    kid = ft.kid
    # every fold's k per pair
    kf = {}
    for k in range(ft.K):
        for sig, rho in pairs:
            kk, q = k_of(sig, rho, betas[k], cs[k], k)
            kf[(k, sig)] = (kk, q)
    D = np.array([r["D"] for r in fr])
    c1 = np.array([r["card"] == "c1" for r in fr])
    paired = np.array([r["card"] == "c1" and r["sess"] in pair_of for r in fr])
    kr = np.ones(len(fr))
    for i, r in enumerate(fr):
        if paired[i]:
            v = kf[(int(kid[i]), r["sess"])][0]
            kr[i] = 1.0 if v is None else v
    e1 = np.where(paired, D - kr * p, e)
    ex = np.array([r["exp"] for r in fr])
    pri = np.array([r.get("priority") == 1 for r in fr])
    m164 = c1 & (ex == "E164")
    m164p = m164 & pri
    bt = FM.boot(kid[paired], e1[paired], e[paired])
    b0, b1 = float(np.mean(e[m164p])), float(np.mean(e1[m164p]))
    all0, all1 = rms(e[c1]), rms(e1[c1])
    cl = {"pooled": {"d_rms_w": bt["d_rms_w"], "lo95": bt["lo95"], "hi95": bt["hi95"], "n_kinds": bt["n_kinds"], "n_rows": bt["n_rows"],
                     "rms_without_w": rms(e[paired]), "rms_with_w": rms(e1[paired]),
                     "rule": "d <= -0.010 W and the 95% interval below 0", "passes": bool(bt["d_rms_w"] <= -0.010 and bt["hi95"] < 0)},
          "E164_priority1_bias": {"n": int(m164p.sum()), "bias_without_w": b0, "bias_with_w": b1,
                                  "rule": "falls in size and keeps its sign", "passes": bool(abs(b1) < abs(b0) and b0 * b1 > 0)},
          "every_card1_int8_row": {"n": int(c1.sum()), "rms_without_w": all0, "rms_with_w": all1, "rise_w": all1 - all0,
                                   "rule": "the rms rises by no more than 0.001 W", "passes": bool(all1 - all0 <= 0.001)}}
    enters = all(v["passes"] for v in cl.values())
    # not wanted (i): over-correction on E164's int8 rows or over the paired sessions' card-1 int8 rows
    oc = {}
    for lab, msk in (("E164's int8 rows", m164), ("the paired sessions' card-1 int8 rows", paired)):
        a0, a1 = float(np.mean(e[msk])), float(np.mean(e1[msk]))
        oc[lab] = {"n": int(msk.sum()), "bias_without_w": a0, "bias_with_w": a1, "overcorrects": overcorrects(a0, a1)}
    # the all-rows k per pair (the spread's reading) and its noise, M10's own form (section7_m10.median_noise / spread_by_card)
    allk = {}
    for sig, rho in pairs:
        kk, q = k_of(sig, rho, fall["b"], fall["c"])
        allk[sig] = (kk, q)

    def spread(kmap, folds_c=None, k_out=None):
        rng = np.random.default_rng(SEED)
        res = {}
        for sig, rho in pairs:
            kk, q = kmap[sig]
            if kk is None:
                res[sig] = {"k": None, "anchors": [], "why": "no anchor left"}
                continue
            names = sorted(q)
            b, c = folds_c if folds_c else (fall["b"], fall["c"])
            ys = np.array([A[sig][n]["D"] for n in names])
            yr = np.array([A[rho][n]["D"] for n in names])
            ss = np.array([A[sig][n]["se"] if A[sig][n]["se"] is not None else np.nan for n in names])
            sr = np.array([A[rho][n]["se"] if A[rho][n]["se"] is not None else np.nan for n in names])
            hs = np.array([dhat(A[sig][n], b, c) for n in names])
            hrr = np.array([dhat(A[rho][n], b, c) for n in names])
            zs = rng.standard_normal((NB, len(names)))
            zr_ = rng.standard_normal((NB, len(names)))
            qd = ((ys[None, :] + ss[None, :] * zs) / hs[None, :]) / ((yr[None, :] + sr[None, :] * zr_) / hrr[None, :])
            kd = np.median(qd, axis=1)
            res[sig] = {"k": kk, "anchors": names, "sd_from_own_errors": float(np.std(kd, ddof=1)),
                        "se_missing": int(np.sum(np.isnan(ss)) + np.sum(np.isnan(sr)))}
        ok = [s for s, v in res.items() if v.get("k") is not None and not v["se_missing"]]
        obs = float(np.std([res[s]["k"] for s in ok], ddof=1)) if len(ok) >= 2 else None
        noise = float(math.sqrt(np.mean([res[s]["sd_from_own_errors"] ** 2 for s in ok]))) if ok else None
        every = [v["k"] for v in res.values() if v.get("k") is not None]
        return {"pairs_read": len(ok), "observed_sd": obs, "sd_expected_from_own_errors": noise,
                "ratio": (obs / noise) if (obs is not None and noise) else None,
                "met": bool(obs is not None and noise is not None and obs <= noise),
                "left_out_no_se": sorted(s for s, v in res.items() if v.get("k") is not None and v["se_missing"]),
                "left_out_no_anchor": sorted(s for s, v in res.items() if v.get("k") is None),
                "observed_sd_every_pair": float(np.std(every, ddof=1)) if len(every) >= 2 else None, "pairs": res}
    sp = spread(allk)
    # the same reading in every fold (k with the fold's prices and card term, the held-out kind's anchors not read)
    fold_read = {}
    for k in range(ft.K):
        km = {sig: kf[(k, sig)] for sig, _ in pairs}
        r = spread(km, (betas[k], cs[k]))
        fold_read[ft.kinds[k]] = (r["ratio"], r["met"], r["pairs_read"], r["left_out_no_anchor"])
    full = {kn: v for kn, v in fold_read.items() if not v[3]}
    short = {kn: v for kn, v in fold_read.items() if v[3]}
    ratios = [v[0] for v in full.values() if v[0] is not None]
    # the constant that would do: the card term x the median k over the pairs, bootstrap over the pairs
    ks = np.array([allk[s][0] for s, _ in pairs], float)
    rng = np.random.default_rng(SEED)
    meds = [float(np.median(ks[rng.integers(0, len(ks), len(ks))])) for _ in range(NB)]
    lo, hi = (float(x) for x in np.quantile(meds, [0.025, 0.975]))
    cterm = float(fall["c"])
    preview = json.load(open(os.path.join(HERE, "registration-a1.json")))["d_card1_paired_anchor_int8_I8P"]["preview_posthoc"]["pairs"]
    per_pair = {}
    for (s, r_), (sig, rho) in zip(PAIRS, pairs):
        msk = c1 & (np.array([q["sess"] for q in fr]) == sig)
        kk, q = allk[sig]
        fk = [kf[(k, sig)][0] for k in range(ft.K) if kf[(k, sig)][0] is not None]
        per_pair[f"{s}/{r_}"] = {"anchors": sorted(q), "q": q, "k_all_rows": kk, "k_fold_range": [min(fk), max(fk)] if fk else None,
                                 "k_preview_A1_1": preview.get(f"{s}/{r_}"), "card1_int8_rows": int(msk.sum()),
                                 "rms_without_w": rms(e[msk]) if msk.any() else None, "rms_with_w": rms(e1[msk]) if msk.any() else None,
                                 "bias_without_w": float(np.mean(e[msk])) if msk.any() else None,
                                 "bias_with_w": float(np.mean(e1[msk])) if msk.any() else None}
    nw = {"overcorrects": {"readings": oc, "met": any(v["overcorrects"] for v in oc.values())},
          "spread_A1_3": dict({k_: v for k_, v in sp.items() if k_ != "pairs"}, pairs={s: {k_: v for k_, v in d.items()} for s, d in sp["pairs"].items()},
                              rule="the sd of k over the nine pairs no larger than the sd drawing each anchor's D as D + se x N(0, 1) gives (2,000 draws, seed 142): met means a constant card term would do as well",
                              every_fold={"folds_reading_every_anchor": len(full), "ratio_range": [min(ratios), max(ratios)] if ratios else None,
                                          "verdicts": sorted({v[1] for v in full.values()}),
                                          "folds_taking_anchors_away": {kn: {"ratio": v[0], "met": v[1], "pairs_read": v[2], "pairs_without_anchor": v[3]}
                                                                        for kn, v in short.items()}}),
          "I8P-B WORSE": "blind: read_hc1b_i8pb.py on E172 with E171"}
    nw["met_on_committed_rows"] = bool(nw["overcorrects"]["met"] or nw["spread_A1_3"]["met"])
    const = {"card_term": cterm, "median_k": float(np.median(ks)), "median_k_95": [lo, hi], "constant": cterm * float(np.median(ks)),
             "constant_95": [cterm * lo, cterm * hi], "median_k_interval_excludes_1": bool(hi < 1 or lo > 1),
             "note": "reported beside, never carried (A1-3): a candidate for the next registration"}
    return {"reproduces_M10_B": {"max_abs_err_vs_rows_m10_w": worst, "coef_max_rel_diff": coef_rel, "coef_within_1e-9": coef_same,
                                 "card_term_rel_diff": abs(float(fall["c"]) - m10["card1_scale"]) / m10["card1_scale"], "card_term_within_1e-9": c_same,
                                 "rows": len(fr), "kinds": ft.K},
            "pool6_anchor_chain_check": chk6, "anchors_by_session": {s: sorted(v) for s, v in A.items() if s in pair_of or s in pair_of.values()},
            "rows": {"card1_int8": int(c1.sum()), "paired": int(paired.sum()), "E164_int8": int(m164.sum()), "E164_priority1_int8": int(m164p.sum()),
                     "card1_int8_unpaired_sessions": sorted({r["exp"] for i, r in enumerate(fr) if c1[i] and not paired[i]})},
            "entry": cl, "enters": enters, "not_wanted": nw, "constant_beside": const, "per_pair": per_pair,
            "frozen_form": {"card": "aifoundry1 card 1, paired sessions only; other card-1 int8 rows keep M10's prediction",
                            "k": "median over the int8 random anchors run in both sessions (by bytes) of [D_s/Dhat_s]/[D_r/Dhat_r], Dhat = M10's int8 B at "
                                 "each session's measured rate (card term on card 1); the check anchor never in k; 1 if no anchor",
                            "card_term": cterm, "m10_int8_coef_J": m10["coef_J"], "nothing_new_fitted": True}}


def decide(c, d):
    """section 10's table and its 'one way only'"""
    out = {}
    out["c_HC1"] = ("ENTERS: M11 carries h1 on card 1 as its primary 4.5 s heat, unless E172's blind clauses (HC1-B WORSE, or h1 over-correcting "
                    "on E172's N1) are met; then a reported arm, never the primary" if c["enters"] else
                    "DOES NOT ENTER: M11's card-1 4.5 s heat stays M10's law; HC1-B is still read on E172 and reported, and cannot bring it in")
    if not d["enters"]:
        out["d_I8P"] = "DOES NOT ENTER: M11's card-1 int8 stays M10's (card term 0.9616); I8P-B is still read on E172 with E171 and reported, and cannot bring it in"
    elif d["not_wanted"]["met_on_committed_rows"]:
        out["d_I8P"] = "ENTERS, NOT WANTED on the committed rows: a reported arm, never the primary"
    else:
        out["d_I8P"] = "ENTERS: M11 carries k on card 1's paired sessions, unless I8P-B reads WORSE on E172 with E171; then a reported arm"
    return out


def main(argv):
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True)
    ap.add_argument("--txt", required=True)
    a = ap.parse_args(argv)
    lists = check_m11_lists()
    sys.path.insert(0, M10D)
    import fit_m10 as FM  # noqa: E402  (M10's registered fit, unchanged; nothing is refitted that M10 did not fit)
    n174 = FM.check_inputs()
    log(f"M11 refit (c) and (d): M11's lists {lists}; M10's {n174} registered inputs pass")
    rows, missing = FM.assemble()
    if len(rows) != 959:
        raise SystemExit(f"M11 REFIT STOPPED: {len(rows)} rows, not 959")
    held = json.load(open(os.path.join(M10D, "heldout-m10.json")))
    c = hc1(FM, rows, held)
    cl = c["entry"]
    log(f"(c) HC1: reproduces heldout-m10.json's heat_c1 ({sum(c['reproduces_heldout_m10_heat_c1'].values())} of {len(HC1_COMPARE)} fields); "
        f"card 1 {c['rows']['card1']} rows in {c['rows']['card1_sessions']} sessions")
    log(f"    pooled d {cl['pooled']['d_rms_c']:+.6f} C [{cl['pooled']['lo95']:+.6f}, {cl['pooled']['hi95']:+.6f}]: "
        f"{'PASS' if cl['pooled']['passes'] else 'FAIL'}")
    log(f"    two thirds: d <= 0 in {cl['two_thirds']['d_le_0']} of {cl['two_thirds']['sessions_judged']} sessions with >= 10 rows "
        f"(needed {cl['two_thirds']['needed']}; worse with h: {cl['two_thirds']['worse_with_h']}): {'PASS' if cl['two_thirds']['passes'] else 'FAIL'}")
    log(f"    bias {cl['bias']['bias_without_c']:+.6f} -> {cl['bias']['bias_with_c']:+.6f} C: {'PASS' if cl['bias']['passes'] else 'FAIL'}")
    for s, v in c["per_session_card1"].items():
        log(f"      {s:22s} n {v['n_rows']:3d}  rms {v['rms_without_c']:.4f} -> {v['rms_with_c']:.4f}  d {v['d_c']:+.4f}  h {v['h_all_rows']}"
            f"{'' if v['judged'] else '  (fewer than 10 rows: not judged)'}")
    log(f"    HC1 {'ENTERS' if c['enters'] else 'DOES NOT ENTER'}")
    d = i8p(FM, rows, held)
    e = d["entry"]
    log(f"(d) I8P: M10's B reproduced (max |err - rows-m10| {d['reproduces_M10_B']['max_abs_err_vs_rows_m10_w']:.2e} W; prices and card term "
        f"within 1e-9: {d['reproduces_M10_B']['coef_max_rel_diff']:.1e}, {d['reproduces_M10_B']['card_term_rel_diff']:.1e}); rows {d['rows']}")
    log(f"    pooled d {e['pooled']['d_rms_w']:+.6f} W [{e['pooled']['lo95']:+.6f}, {e['pooled']['hi95']:+.6f}] over {e['pooled']['n_rows']} rows: "
        f"{'PASS' if e['pooled']['passes'] else 'FAIL'}")
    log(f"    E164 priority-1 bias {e['E164_priority1_bias']['bias_without_w']:+.6f} -> {e['E164_priority1_bias']['bias_with_w']:+.6f} W: "
        f"{'PASS' if e['E164_priority1_bias']['passes'] else 'FAIL'}")
    log(f"    every card-1 int8 row: rms {e['every_card1_int8_row']['rms_without_w']:.6f} -> {e['every_card1_int8_row']['rms_with_w']:.6f} W "
        f"(rise {e['every_card1_int8_row']['rise_w']:+.6f}): {'PASS' if e['every_card1_int8_row']['passes'] else 'FAIL'}")
    log(f"    I8P {'ENTERS' if d['enters'] else 'DOES NOT ENTER'}")
    nw = d["not_wanted"]
    for lab, v in nw["overcorrects"]["readings"].items():
        log(f"    not wanted, over-correction on {lab}: bias {v['bias_without_w']:+.6f} -> {v['bias_with_w']:+.6f} W: {v['overcorrects']}")
    s = nw["spread_A1_3"]
    log(f"    not wanted, the spread (A1-3): observed sd of k {s['observed_sd']:.6f} over {s['pairs_read']} pairs against {s['sd_expected_from_own_errors']:.6f} "
        f"from the anchors' own errors (ratio {s['ratio']:.3f}): met {s['met']}; left out (no se) {s['left_out_no_se']}")
    ef = s["every_fold"]
    log(f"      every fold reading every anchor ({ef['folds_reading_every_anchor']}): ratio {ef['ratio_range'][0]:.6f}-{ef['ratio_range'][1]:.6f}, "
        f"verdicts {ef['verdicts']}; folds taking anchors away: {json.dumps(ef['folds_taking_anchors_away'])[:400]}")
    for pk, v in d["per_pair"].items():
        log(f"      {pk:10s} k {v['k_all_rows']:.5f} (folds {v['k_fold_range'][0]:.5f}-{v['k_fold_range'][1]:.5f}; preview {v['k_preview_A1_1']}) "
            f"anchors {v['anchors']} rows {v['card1_int8_rows']}")
    cs_ = d["constant_beside"]
    log(f"    beside: the constant {cs_['card_term']:.6f} x median k {cs_['median_k']:.5f} = {cs_['constant']:.5f} "
        f"[{cs_['constant_95'][0]:.5f}, {cs_['constant_95'][1]:.5f}]; the median k's interval excludes 1: {cs_['median_k_interval_excludes_1']}")
    dec = decide(c, d)
    log(f"DECIDED (c) {dec['c_HC1']}")
    log(f"DECIDED (d) {dec['d_I8P']}")
    out = {"_note": "Q142(h2) refit_m11_cd.py: M11's (c) HC1 and (d) I8P on the committed rows, entry and not-wanted clauses as REGISTRATION.md "
                    "sections 8-10 and A1 (A1-1, A1-3) register them; held out, not blind; no E171-E174 data read",
           "refit_sha256": sha(os.path.abspath(__file__)), "m11_lists": lists, "m10_registered_inputs": n174,
           "fit_m10_sha256": sha(os.path.join(M10D, "fit_m10.py")), "seed": SEED, "draws": NB,
           "c_HC1": c, "d_I8P": d, "decided": dec}
    open(a.out, "w").write(json.dumps(out, indent=1, sort_keys=True, default=str).replace(TOP + os.sep, "") + "\n")
    open(a.txt, "w").write("\n".join(LOG) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
