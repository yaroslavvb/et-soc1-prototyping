#!/usr/bin/env python3
"""Q130(c) amendment A1 — what the verification of the frozen model found, computed WITHOUT touching the freeze.

    /usr/bin/python3 amend_a1.py --out amendment-a1.json > amendment-a1.txt

Written Sat 31 Oct 2026 (week 44) on the Intel, after verify-desk-model's verdict "does not hold" and BEFORE any
E78 or E80 data exists.  Numpy only; about a minute.

THE FREEZE IS NOT CHANGED.  predictions.json (sha256 c5a66cb6...6320a2c, commit 2bbe03dd) and model.py stay
byte-identical: this file asserts the sha, imports model.py's own functions (features, price_lists, phi,
solve_winf, Model, host_tiles, gate_mask, issue_streams, live_slots, sign_bits) and re-uses them.  Every number it
writes is one of three things, and amendment-a1.json says which:

  CHECK   the frozen model, unchanged, run on operands it was never run on (E65's 32 bit rungs, E67's abit_31
          and anchors, E70's 23 ladder rungs and its nrd tiles, all as the hosts DUMPED them), or on its own
          scoring rows with labels corrected;
  ARM     the same model recalibrated with ONE input changed, as the frozen text declared a sensitivity arm
          would be (E70's own W-infinity, E70's actual nrd tiles, E71's leakage slope, gamma 0 and 2) or as the
          verification asked (a zero product carries no sign) -- never a new freeze;
  SCORE   a registered rule whose data already existed at the freeze (R5 and the "FOR E79" shape claim against
          E79's lists, pushed 5 min before it), scored now as a post-data comparison.

Before any arm is used, the replica of the frozen calibration is asserted to reproduce predictions.json: every
kind's switching W under both gating arms, and its ci95, to the file's own rounding.
"""
import sys

sys.dont_write_bytecode = True                       # nothing is written into the repo by the imports

import argparse  # noqa: E402
import glob  # noqa: E402
import hashlib  # noqa: E402
import json  # noqa: E402
import math  # noqa: E402
import os  # noqa: E402
import statistics as st  # noqa: E402

import numpy as np  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", "..", "..", ".."))
DATA = os.path.join(REPO, "docs", "reports", "data")
sys.path.insert(0, HERE)
import model as M  # noqa: E402   the frozen Q130C-M1, imported and never edited

sys.path.insert(0, os.path.join(REPO, "tools", "claims-v3", "hpl"))
import surface_hpl_t as ST  # noqa: E402

FREEZE_SHA = "c5a66cb6d5f07a35d783d7db4be0f94a69482cf123defd2eccfda04fb6320a2c"
FREEZE_COMMIT = "2bbe03dd"
E64D = os.path.join(DATA, "2026-10-23-e64-horace-power-limit")
E65D = os.path.join(DATA, "2026-10-26-e65-bit-prices-hart-ladder")
E67D = os.path.join(DATA, "2026-10-27-e67-a-side-bit-prices")
E70D = os.path.join(DATA, "2026-10-27-e70-saturation-ladder")
E79D = os.path.join(DATA, "2026-10-31-e79-fp16-int8-bit-prices")
T1F = os.path.join(DATA, "2026-10-27-q129-governor-temperature", "figures-t1.json")
INVF = os.path.join(DATA, "2026-10-31-q130-kinds-inventory", "inventory.json")
KDIR = os.path.join(REPO, "tools", "claims-v3", "kinds")
BASE = {"fp32": "randn", "fp16": "randn", "int8": "full"}
TYPES = ("fp32", "fp16", "int8")
E71_K = 0.3803


def rel(p):
    return os.path.relpath(p, REPO)


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def r(x, n=3):
    return None if x is None else round(float(x), n)


# ───────────────────────────────────────────────────────────── operands
def kind_tile(K, t, kind):
    return M.words_of(open(os.path.join(KDIR, K["kinds"][t][kind]["file"]), "rb").read())


def dumped(expdir, name, passes, sub="hl"):
    """Every dumped copy of one item's tiles over the given passes: [(pass, sha, (aw, bw))]."""
    out = []
    for p in passes:
        for f in sorted(glob.glob(os.path.join(expdir, "aifoundry3", sub, "p%d" % p, "tiles", "%s.b%d.bin" % (name, p)))):
            raw = open(f, "rb").read()
            out.append((p, hashlib.sha256(raw).hexdigest(), M.words_of(raw)))
    return out


def one_dumped(expdir, name, passes, sub="hl"):
    d = dumped(expdir, name, passes, sub)
    shas = sorted(set(x[1] for x in d))
    assert d, (expdir, name)
    return d[0][2], {"passes": [x[0] for x in d], "distinct_sha256": len(shas), "sha256": shas[0]}


# ───────────────────────────────────────────────────────────── the product-sign rate, both definitions
def elem_nonzero(w, t):
    """(..., E) True where an element's MAGNITUDE is nonzero (fp: every bit but the sign; int8: the byte)."""
    E, _ = M.TYPES[t]
    ew = 32 // E
    mag = ((1 << ew) - 1) >> 1 if t != "int8" else (1 << ew) - 1
    return np.stack([((np.asarray(w, dtype=np.uint64) >> np.uint64(e * ew)) & np.uint64(mag)) != 0
                     for e in range(E)], axis=-1)


def feats(aw, bw, t, arm, zero_unsigned=False):
    """model.features(); with zero_unsigned the sign of a ZERO product is taken as 0 (+), which is exactly an
    int8 product's two's-complement sign bit, and for fp a product with no magnitude to swing."""
    fa, fb, q, g, bus = M.features(aw, bw, t, arm)
    if not zero_unsigned:
        return fa, fb, q, g, bus
    a_seq, b_seq = M.issue_streams(aw, bw, t)
    live = M.live_slots(M.gate_mask(a_seq, b_seq, t), t).astype(np.int64)
    wgt = np.ones_like(live) if arm == "bus" else live
    sa, sb = M.sign_bits(a_seq, t)[:, None, :], M.sign_bits(b_seq, t)
    p = np.where(elem_nonzero(a_seq, t)[:, None, :] & elem_nonzero(b_seq, t), sa ^ sb, 0)
    dp = (p != np.roll(p, -1, axis=0)).astype(np.int64)
    return fa, fb, float((dp * wgt[:, :, None]).sum()) / M.SLOT_CYCLES, g, bus


# ───────────────────────────────────────────────────────────── the frozen calibration, replicated
def e64_step(t, kind):
    return (st.mean(M.E64_C[(t, kind)]) - st.mean(M.E64_C[(t, "zeros")])) * M.XFER


class Prices:
    """Swap the fp32 price lists model.price_lists() reads (the E71 arm), and always put them back."""

    def __init__(self, b=None, a=None):
        self.b, self.a = b, a

    def __enter__(self):
        self.saved = (list(M.E65_B), list(M.E67_A))
        if self.b is not None:
            M.E65_B[:] = self.b
        if self.a is not None:
            M.E67_A[:] = self.a
        return self

    def __exit__(self, *exc):
        M.E65_B[:], M.E67_A[:] = self.saved
        return False


def sums32(f):
    wa32, wb32 = M.price_lists("fp32")
    fa, fb, q, g, _ = f
    return float(np.dot(fa, wa32)), float(np.dot(fb, wb32)), q, g


def calib_fp32(HK, arm, nrd_a=M.NRD_A, nrd_b=M.NRD_B, u32=M.U_FP32, fit_lam=False, fixed_w=None, nrd_tiles=None,
               flip_target=M.ZR["flip_w"]):
    """model.py main() step 2, line for line, with the inputs it hard-codes as arguments."""
    mean = {k: [st.mean(x) for x in zip(*[sums32(f) for f in HK[k][arm]])] for k in HK}
    if nrd_tiles:
        sA_r, _, q_a, _ = sums32(nrd_tiles["a"][arm])
        _, sB_r, q_b, _ = sums32(nrd_tiles["b"][arm])
    else:
        sA_r, _, q_a, _ = mean["a_randn_b_ones"]
        _, sB_r, q_b, _ = mean["a_ones_b_randn"]
    sA_n, sB_n, q_n, _ = mean["randn"]
    sA_s, sB_s, q_s, _ = mean["signs"]
    tgt = e64_step("fp32", "signs")
    sigma, lam = 6.0, 0.0
    for _ in range(4000 if fit_lam else 400):
        if fixed_w:
            wa, wb = fixed_w
        else:
            wa, wb = M.solve_winf(sA_r, nrd_a - sigma * q_a), M.solve_winf(sB_r, nrd_b - sigma * q_b)
        if wa is None or wb is None:
            return None
        pas, pbs = M.phi(sA_s, wa), M.phi(sB_s, wb)
        new = (tgt - u32 - (pas + pbs - lam * min(pas, pbs))) / q_s
        if fit_lam:
            pa, pb = M.phi(sA_n, wa), M.phi(sB_n, wb)
            new_lam = (pa + pb + new * q_n - flip_target) / min(pa, pb)
            if abs(new - sigma) < 1e-12 and abs(new_lam - lam) < 1e-12:
                sigma, lam = new, new_lam
                break
            sigma, lam = 0.5 * sigma + 0.5 * new, 0.5 * lam + 0.5 * new_lam
            continue
        if abs(new - sigma) < 1e-10:
            sigma = new
            break
        sigma = 0.5 * sigma + 0.5 * new
    pa, pb = M.phi(sA_n, wa), M.phi(sB_n, wb)
    return {"wa_inf_w": wa, "wb_inf_w": wb, "sigma_w": sigma, "lam": lam, "u_fp32_w": u32,
            "nrd_a_w": nrd_a, "nrd_b_w": nrd_b,
            "q": {"nrd_a": q_a, "nrd_b": q_b, "randn": q_n, "signs": q_s},
            "randn_flip_check_w": pa + pb - lam * min(pa, pb) + sigma * q_n, "randn_flip_target_w": flip_target,
            "randn_flip_without_sign_term_w": None}


def calib_fmt(c, t, arm, U, tiles_feat):
    """model.py main() step 4: U_T from E64's (ones - zeros), alpha_T by bisection on E64's randn."""
    target = e64_step(t, "randn")
    Mx = M.Model(c["wa_inf_w"], c["wb_inf_w"], 0.0, c["sigma_w"], U, arm)
    f = tiles_feat[(t, BASE[t])][arm]
    lo, hi = 1e-4, 80.0
    for _ in range(300):
        mid = (lo + hi) / 2
        if Mx.dw(*f[:4], t, mid)["dw_w"] < target:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2


def full_model(HK, KF, arm_primary, **kw):
    """The whole frozen pipeline with one input changed: both gating arms, alpha per format, all 51 kinds."""
    zu = kw.pop("zero_unsigned", False)
    hk = HK["zu" if zu else "std"]
    kf = KF["zu" if zu else "std"]
    u32 = kw.get("u32", M.U_FP32)
    U = {"fp32": u32, "fp16": e64_step("fp16", "ones"), "int8": e64_step("int8", "ones")}
    out = {}
    for arm in ("gate", "bus"):
        c = calib_fp32(hk, arm, **kw)
        if c is None:
            out[arm] = None
            continue
        alpha = {"fp32": 1.0}
        for t in ("fp16", "int8"):
            alpha[t] = calib_fmt(c, t, arm, U, kf)
        Mx = M.Model(c["wa_inf_w"], c["wb_inf_w"], 0.0, c["sigma_w"], U, arm)
        pred = {}
        for (t, kind), f in sorted(kf.items()):
            p = Mx.dw(*f[arm][:4], t, alpha[t])
            pred["%s/%s" % (t, kind)] = {"dw_w": p["dw_w"], "flip_w": p["flip_w"], "sign_w": p["sign_w"],
                                         "ungate_w": p["ungate_w"], "S_A_w": p["S_A_w"], "S_B_w": p["S_B_w"],
                                         "q": f[arm][2], "g": f[arm][3]}
        out[arm] = {"cal": c, "alpha": alpha, "U": U, "model": Mx, "pred": pred}
    out["primary"] = arm_primary
    return out


# ───────────────────────────────────────────────────────────── the frozen interval rule, replicated
def interval_err(p, t, kind, alpha, U, K, ref, law_term=None, insample=None):
    """model.py main() lines 652-660.  law_term(p, t, scale, g) replaces E70's 0.232 W term when given."""
    if insample is None:
        insample = (t, kind) in M.CAL_KINDS
    band = (0.0 if insample else M.REL_BAND[t]) * (p["flip_w"] + p["sign_w"])
    scale = 1.0 if t == "fp32" else M.R_T[t] * alpha[t]
    g = p["g"]
    e_law = M.E70_LAW_RMS_W * scale * (1 - g)
    if law_term is not None:
        e_law = law_term(p, t, scale, g, e_law)
    e_u = (M.U_FP32_SE if t == "fp32" else M.TARGET_SE[t]) * (1 - g)
    e_tgt = M.TARGET_SE[t] * min(1.0, (p["flip_w"] + p["sign_w"]) / max(1e-9, ref[t]))
    gsd = 0.0
    if kind is not None:
        rep = K["kinds"][t][kind].get("replicates") or {}
        gr = rep.get("gated_lane_frac") if isinstance(rep, dict) else None
        if isinstance(gr, dict) and isinstance(gr.get("sd"), (int, float)):
            gsd = float(gr["sd"])
    return (band ** 2 + e_law ** 2 + e_u ** 2 + e_tgt ** 2 + (U[t] * gsd) ** 2 + M.FLOOR_SE_W ** 2) ** 0.5


def spearman(x, y):
    def ranks(v):
        o = sorted(range(len(v)), key=lambda i: v[i])
        rk = [0.0] * len(v)
        i = 0
        while i < len(o):
            j = i
            while j + 1 < len(o) and v[o[j + 1]] == v[o[i]]:
                j += 1
            for k in range(i, j + 1):
                rk[o[k]] = (i + j) / 2.0
            i = j + 1
        return rk
    a, b = ranks(x), ranks(y)
    ma, mb = st.mean(a), st.mean(b)
    num = sum((p - ma) * (q - mb) for p, q in zip(a, b))
    den = (sum((p - ma) ** 2 for p in a) * sum((q - mb) ** 2 for q in b)) ** 0.5
    return num / den if den else None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="amendment-a1.json")
    ap.add_argument("--draws", type=int, default=24)
    a = ap.parse_args()
    pj = os.path.join(HERE, "predictions.json")
    assert sha(pj) == FREEZE_SHA, "predictions.json is not the freeze"
    P = json.load(open(pj))
    K = json.load(open(os.path.join(KDIR, "kinds.json")))
    O = {"amendment": "A1", "model_id": M.MODEL_ID, "lane": "Q130(c)", "date": "2026-10-31",
         "freeze": {"predictions_json_sha256": FREEZE_SHA, "commit": FREEZE_COMMIT,
                    "model_py_sha256": sha(os.path.join(HERE, "model.py")),
                    "statement": ("predictions.json and model.py are unchanged; every number below is a CHECK, an "
                                  "ARM or a post-data SCORE, as labelled.  The frozen numbers stay scoreable.")}}

    # ── 0. the operands: every kind, both arms, both sign definitions; the E64 host stand-ins likewise
    KF = {"std": {}, "zu": {}}
    for t in TYPES:
        for kind in K["kinds"][t]:
            aw, bw = kind_tile(K, t, kind)
            for d, zu in (("std", False), ("zu", True)):
                KF[d][(t, kind)] = {arm: feats(aw, bw, t, arm, zu) for arm in ("gate", "bus")}
    HKIND = ("zeros", "ones", "randn", "sparse75", "signs", "pow2", "mant", "uniform", "a_randn_b_ones",
             "a_ones_b_randn")
    HK = {"std": {}, "zu": {}}
    for kind in HKIND:
        draws = [M.host_tiles(kind, np.random.default_rng(20261031 + 7919 * i)) for i in range(a.draws)]
        for d, zu in (("std", False), ("zu", True)):
            HK[d][kind] = {arm: [feats(aw, bw, "fp32", arm, zu) for aw, bw in draws] for arm in ("gate", "bus")}

    # ── 1. the replica reproduces the freeze (asserted before anything is built on it)
    FZ = full_model(HK, KF, "gate")
    g, b = FZ["gate"], FZ["bus"]
    fc = P["calibration"]["fp32"]
    assert abs(g["cal"]["wa_inf_w"] - fc["wa_inf_w"]) < 1e-4 and abs(g["cal"]["wb_inf_w"] - fc["wb_inf_w"]) < 1e-4
    assert abs(g["cal"]["sigma_w"] - fc["sigma_w"]) < 1e-4
    for t in ("fp16", "int8"):
        assert abs(g["alpha"][t] - P["calibration"]["per_format"][t]["alpha"]) < 1e-4
    ref = {t: g["pred"]["%s/%s" % (t, BASE[t])]["flip_w"] + g["pred"]["%s/%s" % (t, BASE[t])]["sign_w"] for t in TYPES}
    worst = {"dw": 0.0, "alt": 0.0, "ci95": 0.0}
    for key, fr in P["predictions"].items():
        t, kind = key.split("/")
        worst["dw"] = max(worst["dw"], abs(round(g["pred"][key]["dw_w"], 3) - fr["switching_w_600mhz_a3"]))
        worst["alt"] = max(worst["alt"], abs(round(b["pred"][key]["dw_w"], 3) - fr["switching_w_alt_gating_arm"]))
        e = interval_err(g["pred"][key], t, kind, g["alpha"], g["U"], K, ref)
        dw = g["pred"][key]["dw_w"]
        worst["ci95"] = max(worst["ci95"], abs(round(dw + 2 * e, 3) - fr["switching_w_ci95"][1]))
    assert max(worst.values()) <= 0.0011, worst
    O["replica_check"] = {"max_abs_diff_against_predictions_json": {k: r(v, 4) for k, v in worst.items()},
                          "what": ("this file's replica of the frozen calibration, run on the frozen inputs, "
                                   "against every kind's switching W (both arms) and ci95 upper edge in "
                                   "predictions.json; the file rounds to 3 dp")}
    WA, WB, SIG = g["cal"]["wa_inf_w"], g["cal"]["wb_inf_w"], g["cal"]["sigma_w"]
    MOD32 = M.Model(WA, WB, 0.0, SIG, {"fp32": M.U_FP32}, "gate")

    def over_zero(rung, zero, t="fp32"):
        """The frozen model's step of one item over its own zero item (U cancels when both are ungated)."""
        fr_, fz_ = M.features(*rung, t, "gate"), M.features(*zero, t, "gate")
        pr, pz = MOD32.dw(*fr_[:4], t, 1.0), MOD32.dw(*fz_[:4], t, 1.0)
        return {"g": r(fr_[3], 4), "q": r(fr_[2], 4), "S_A_w": r(pr["S_A_w"]), "S_B_w": r(pr["S_B_w"]),
                "flip_w": r(pr["flip_w"] - pz["flip_w"]), "sign_w": r(pr["sign_w"] - pz["sign_w"]),
                "model_w": pr["dw_w"] - pz["dw_w"]}

    # ── 2. fault 1: the product-sign term against the model's OWN price-list rungs, as the hosts dumped them
    h65 = json.load(open(os.path.join(E65D, "hl.json")))["cards"]["aifoundry3"]
    h67 = json.load(open(os.path.join(E67D, "hl.json")))["cards"]["aifoundry3"]
    s70 = json.load(open(os.path.join(E70D, "scored.json")))
    P65, P67, P70 = h65["passes"], h67["passes"], s70["passes_kept"]
    lq0, lq0_id = one_dumped(E65D, "lq_h0", P65)
    rows = []
    for j in range(32):
        tile, tid = one_dumped(E65D, "bit_%d" % j, P65)
        it = h65["items"]["bit_%d" % j]
        x = over_zero(tile, lq0)
        rows.append(dict(item="E65 bit_%d" % j, side="B", measured_w=r(it["d_p80"]), se_w=r(it["d_p80_se"]),
                         model_w=r(x["model_w"]), ratio=r(x["model_w"] / it["d_p80"], 2), tiles=tid, **{k: v for k, v in x.items() if k != "model_w"}))
    aq0, _ = one_dumped(E67D, "aq_h0", P67)
    for j in range(32):
        tile, tid = one_dumped(E67D, "abit_%d" % j, P67)
        it = h67["items"]["abit_%d" % j]
        x = over_zero(tile, aq0)
        rows.append(dict(item="E67 abit_%d" % j, side="A", measured_w=r(it["d_p80"]), se_w=r(it["d_p80_se"]),
                         model_w=r(x["model_w"]), ratio=r(x["model_w"] / it["d_p80"], 2), tiles=tid, **{k: v for k, v in x.items() if k != "model_w"}))
    lq0_70, _ = one_dumped(E70D, "lq_h0", P70)
    aq0_70, _ = one_dumped(E70D, "aq_h0", P70)
    for nm, zero, meas, se in (("nrd_a", aq0_70, M.NRD_A, M.NRD_A_SE), ("nrd_b", lq0_70, M.NRD_B, M.NRD_B_SE)):
        tile, tid = one_dumped(E70D, nm, P70)
        x = over_zero(tile, zero)
        rows.append(dict(item="E70 %s" % nm, side=nm[-1].upper(), measured_w=meas, se_w=se, model_w=r(x["model_w"]),
                         ratio=r(x["model_w"] / meas, 2), tiles=tid, **{k: v for k, v in x.items() if k != "model_w"}))
    sign_rows = [x for x in rows if x["q"] and x["q"] > 0]
    nos = [x for x in rows if not x["q"] and x["item"].startswith(("E65", "E67"))]
    O["check_sign_term_on_price_list_rungs"] = {
        "kind": "CHECK", "fault": 1,
        "rows": rows,
        "rungs_with_a_sign_change": [{k: x[k] for k in ("item", "q", "measured_w", "se_w", "model_w", "ratio")} for x in sign_rows],
        "rms_w_rungs_without_a_sign_change": r((sum((x["model_w"] - x["measured_w"]) ** 2 for x in nos) / len(nos)) ** 0.5),
        "n_rungs_without_a_sign_change": len(nos),
        "reading": ("E65's bit_31 and E67's abit_31 are the only price-list rungs on which the PRODUCT's sign changes "
                    "(B alternates +base/-base across the column halves against A = 1.0, so q = 1.000; A alternates "
                    "by row against B = 1.0, so q = 0.500).  They cost 0.563 and 0.561 W; the frozen model, "
                    "unchanged, says %.2f and %.2f W.  The premise that those lists never moved the product's "
                    "sign is false, and the term is not a product-sign price." % (
                        [x for x in rows if x["item"] == "E65 bit_31"][0]["model_w"],
                        [x for x in rows if x["item"] == "E67 abit_31"][0]["model_w"]))}

    # E67's anchors on the operands the host dumped (anchor_randn is a fresh libstdc++ draw every pass)
    z67 = one_dumped(E67D, "anchor_zeros", P67)[0]
    an = {}
    for nm in ("anchor_ones", "anchor_pi", "anchor_randn"):
        d = dumped(E67D, nm, P67)
        vals = []
        for _, _, tile in d:
            fr_ = M.features(*tile, "fp32", "gate")
            pr = MOD32.dw(*fr_[:4], "fp32", 1.0)
            vals.append((pr["dw_w"], pr["flip_w"] + pr["sign_w"], pr["flip_w"], pr["sign_w"], fr_[2]))
        meas = h67["anchors"][nm]["p80"] - h67["anchors"]["anchor_zeros"]["p80"]
        an[nm] = {"n_tiles": len(d), "distinct_sha256": len(set(x[1] for x in d)),
                  "model_over_anchor_zeros_w": r(st.mean(v[0] for v in vals)),
                  "model_sd_over_tiles_w": r(st.pstdev([v[0] for v in vals])) if len(vals) > 1 else 0.0,
                  "model_flip_plus_sign_w": r(st.mean(v[1] for v in vals)),
                  "model_flip_w": r(st.mean(v[2] for v in vals)), "model_sign_w": r(st.mean(v[3] for v in vals)),
                  "q": r(st.mean(v[4] for v in vals), 4),
                  "e67_measured_over_anchor_zeros_w": r(meas),
                  "resid_w": r(st.mean(v[0] for v in vals) - meas)}
    O["check_e67_anchors_on_dumped_operands"] = {
        "kind": "CHECK", "faults": [3, 7, 10],
        "anchors": an,
        "what": ("E67's anchor_ones / anchor_pi / anchor_randn steps over anchor_zeros (E67 hl.json anchors p80), "
                 "against the frozen model run on the tiles each kept pass dumped.  These are the SAME operand kinds "
                 "as kinds.json fp32/ones, fp32/pi and fp32/randn, measured on E78's card and clock BEFORE the freeze.")}

    # ── 3. fault 2: the saturating law at the model's own W, on E70's own ladder (dumped tiles)
    lad = []
    for fam in ("lq", "ls", "alq"):
        for x in s70[fam]:
            tile, tid = one_dumped(E70D, x["item"], P70)
            zero = aq0_70 if fam == "alq" else lq0_70
            y = over_zero(tile, zero)
            winf70 = M.WINF_A_E70 if fam == "alq" else M.WINF_B_E70
            lad.append({"item": x["item"], "family": fam, "h": x["h"], "measured_w": r(x["dW"]), "se_w": r(x["se"], 4),
                        "S_additive_e70_w": r(x["S_additive_W"]), "S_this_model_w": y["S_A_w"] if fam == "alq" else y["S_B_w"],
                        "q": y["q"], "model_w": r(y["model_w"]), "resid_w": r(y["model_w"] - x["dW"]),
                        "e70_law_w": r(M.phi(x["S_additive_W"], winf70)),
                        "e70_law_resid_w": r(M.phi(x["S_additive_W"], winf70) - x["dW"]),
                        "in_e70_fit_set": (fam == "ls") or (fam == "lq" and x["h"] <= 16)})

    def rms(v):
        return (sum(z ** 2 for z in v) / len(v)) ** 0.5 if v else None
    fitset = [x for x in lad if x["in_e70_fit_set"]]
    bside16 = [x for x in lad if x["family"] in ("lq", "ls")]
    aside = [x for x in lad if x["family"] == "alq"]
    RMS_B = rms([x["resid_w"] for x in fitset])
    RMS_A = rms([x["resid_w"] for x in aside])
    O["check_law_on_e70_ladder"] = {
        "kind": "CHECK", "fault": 2, "rungs": lad,
        "model_wb_w": r(WB), "model_wa_w": r(WA),
        "rms_model_b_fit_set_15_w": r(RMS_B), "rms_model_b_16_with_lq_h23_w": r(rms([x["resid_w"] for x in bside16])),
        "rms_model_a_alq_7_w": r(RMS_A),
        "rms_e70_law_b_fit_set_15_w": r(rms([x["e70_law_resid_w"] for x in fitset])),
        "rms_e70_law_a_alq_7_w": r(rms([x["e70_law_resid_w"] for x in aside])),
        "e70_registered": {"R_S_refit_W": s70["D2"]["R_S_refit_W"], "A_fit_rms_W": s70["A_ceiling"]["fit_rms_W"],
                           "A_form_verdict": s70["A_ceiling"]["form_verdict"]},
        "frozen_interval_used_w": M.E70_LAW_RMS_W,
        "reading": ("every rung here is mantissa-only (q = 0), so the model's value is its bit term alone; with "
                    "WB = %.3f W that term can never exceed %.2f W, and E70 measured lq_h23 at 12.145 W and ls_h16 "
                    "at 9.749 W.  The law at the model's own W misses E70's 15-rung fit set by %.3f W rms, not the "
                    "0.232 W every frozen interval borrows" % (WB, WB, RMS_B))}

    # ── 4. fault 3: lambda on randn, re-fitted; and what the sign term does to the one-sided over-add
    lamfit = calib_fp32(HK["std"], "gate", fit_lam=True)
    nos_sig = {}
    mean = {k: [st.mean(x) for x in zip(*[sums32(f) for f in HK["std"][k]["gate"]])] for k in HK["std"]}
    wa0, wb0 = M.solve_winf(mean["a_randn_b_ones"][0], M.NRD_A), M.solve_winf(mean["a_ones_b_randn"][1], M.NRD_B)
    nos_sig["randn_flip_pred_without_sign_term_w"] = r(M.phi(mean["randn"][0], wa0) + M.phi(mean["randn"][1], wb0))
    O["check_randn_was_selected_on"] = {
        "kind": "CHECK", "fault": 3,
        "lam_declared_zero": {"randn_flip_pred_w": r(g["cal"]["randn_flip_check_w"]), "target_w": M.ZR["flip_w"],
                              "resid_w": r(g["cal"]["randn_flip_check_w"] - M.ZR["flip_w"])},
        "lam_fitted_on_randn": {"lam": r(lamfit["lam"], 4), "wa_inf_w": r(lamfit["wa_inf_w"], 4),
                                "wb_inf_w": r(lamfit["wb_inf_w"], 4), "sigma_w": r(lamfit["sigma_w"], 4),
                                "randn_flip_pred_w": r(lamfit["randn_flip_check_w"], 4)},
        "one_sided_steps_sum_w": r(M.NRD_A + M.NRD_B), "split_flip_term_w": M.ZR["flip_w"],
        "over_add_w": r(M.NRD_A + M.NRD_B - M.ZR["flip_w"]),
        **nos_sig,
        "q": {k: r(v, 4) for k, v in g["cal"]["q"].items()},
        "reading": ("model.py says it fitted the overlap on randn in a first pass (-0.03) and then declared it zero; "
                    "refitting reproduces lambda = %.4f with a residual of 0.  So randn chose the model's form and "
                    "is not an out-of-sample check.  What survives: E70's one-sided steps over-add the split's flip "
                    "term by %.2f W (%.3f + %.3f against %.3f), and the random-sign term fitted on `signs` takes up "
                    "all but %.2f W of that." % (lamfit["lam"], M.NRD_A + M.NRD_B - M.ZR["flip_w"], M.NRD_A, M.NRD_B,
                                                 M.ZR["flip_w"], abs(g["cal"]["randn_flip_check_w"] - M.ZR["flip_w"])))}

    # ── 5. faults 7 and 9: the E64 scoring rows with their labels corrected, and the interval rule applied to them
    labels = {"zeros": "basis (both terms vanish by definition)", "signs": "fitted (sigma)",
              "randn": "selected-on (lambda fitted on the split and dropped)",
              "sparse75": "arm-selected (chose the gate arm)",
              "a_randn_b_ones": "by construction U + E70 nrd_a (only the card transfer is tested)",
              "a_ones_b_randn": "by construction U + E70 nrd_b (only the card transfer is tested)",
              "ones": "clean", "pow2": "clean", "mant": "clean", "uniform": "clean"}
    frows = []
    for kind in HKIND:
        vals, errs = [], []
        for f in HK["std"][kind]["gate"]:
            p = g["model"].dw(*f[:4], "fp32", 1.0)
            p["g"] = f[3]
            vals.append(p["dw_w"])
            errs.append(interval_err(p, "fp32", None, g["alpha"], g["U"], K, ref, insample=(kind == "signs")))
        meas = e64_step("fp32", kind)
        pm, em, dsd = st.mean(vals), st.mean(errs), st.pstdev(vals)
        frows.append({"kind": kind, "label": labels[kind], "pred_w": r(pm), "draw_sd_w": r(dsd), "e64_w": r(meas),
                      "resid_w": r(pm - meas), "rel": r((pm - meas) / meas, 3) if meas > 0.5 else None,
                      "one_sigma_w": r(em), "z": r((pm - meas) / em, 2) if kind != "zeros" else None,
                      "inside_95": abs(pm - meas) <= 2 * em,
                      "z_with_draw_sd": r((pm - meas) / (em ** 2 + dsd ** 2) ** 0.5, 2) if kind != "zeros" else None})
    clean = [x for x in frows if x["label"] == "clean"]
    O["check_e64_rows_relabelled"] = {
        "kind": "CHECK", "faults": [7, 9], "rows": frows,
        "clean_four": [x["kind"] for x in clean],
        "clean_four_rms_w": r(rms([x["resid_w"] for x in clean])),
        "clean_four_rel": [x["rel"] for x in clean],
        "published_eight_rms_w": P["calibration"]["fp32_out_of_sample"]["rms_w"],
        "outside_own_95": [x["kind"] for x in frows if x["kind"] != "zeros" and not x["inside_95"]],
        "rel_band_note": ("REL_BAND fp32 = 12% was set with the out-of-sample residuals in view (model.py's own text: "
                          "'its own measured out-of-sample median miss is 6%, max 34%'), so it is not an independent "
                          "error estimate")}

    # ── 6. the arms
    e71b = json.load(open(os.path.join(E65D, "leak-sensitivity-e71.json")))["blocks_ab"]["bits_fJ"]
    e71a = json.load(open(os.path.join(E67D, "leak-sensitivity-e71.json")))
    e71a_bits = e71a["a_bits_fJ"]
    rb = [e71b[str(j)]["at_measured_slope"] / e71b[str(j)]["published"] for j in range(32)]
    ra = [e71a_bits[str(j)]["at_measured_slope"] / e71a_bits[str(j)]["published"] for j in range(32)]
    ks, nra, nrb = [], [], []
    for f in ("hl-leak0.2.json", "hl-leak0.3.json", "hl-leak0.4.json"):
        L = s70["leak_sensitivity"][f]
        ks.append(L["leak_W_per_C"])
        nra.append(L["rungs"]["nrd_a"])
        nrb.append(L["rungs"]["nrd_b"])
    sa_ = np.polyfit(ks, nra, 1)[0]
    sb_ = np.polyfit(ks, nrb, 1)[0]
    k70 = s70["leak_W_per_C"]
    nrd_a71, nrd_b71 = M.NRD_A + sa_ * (E71_K - k70), M.NRD_B + sb_ * (E71_K - k70)
    inv = json.load(open(INVF))["zeros_random_split"]["slope_sensitivity_W"]
    u71 = inv["ungating_at_k_0.3803"]
    war = e71a["whole_operand_additivity"]
    flip71 = M.ZR["flip_w"] * war["at_measured_slope"]["both_random_W"] / war["published"]["both_random_W"]
    nrd_tiles = {}
    for nm, side in (("nrd_a", "a"), ("nrd_b", "b")):
        tile, _ = one_dumped(E70D, nm, P70)
        nrd_tiles[side] = {arm: M.features(*tile, "fp32", arm) for arm in ("gate", "bus")}
    arms = {}
    arms["zero_products_unsigned"] = (full_model(HK, KF, "gate", zero_unsigned=True),
                                      "a zero product's sign is 0 (int8's two's-complement product; fp: no magnitude)")
    arms["e70_actual_nrd_tiles"] = (full_model(HK, KF, "gate", nrd_tiles=nrd_tiles),
                                    "WA, WB calibrated on E70's DUMPED nrd_a / nrd_b tiles instead of the host stand-ins")
    arms["e70_winf"] = (full_model(HK, KF, "gate", fixed_w=(M.WINF_A_E70, M.WINF_B_E70)),
                        "WA, WB fixed at E70's own fitted 6.37 / 10.52 W; sigma re-fitted on `signs`")
    with Prices(b=[M.E65_B[j] * rb[j] for j in range(32)], a=[M.E67_A[j] * ra[j] for j in range(32)]):
        assert abs(M.price_lists("fp32")[1][22] * 4096 - M.E65_B[22]) < 1e-12 and M.E65_B[22] != 4.63
        arms["e71_slope"] = (full_model(HK, KF, "gate", nrd_a=nrd_a71, nrd_b=nrd_b71, u32=u71, flip_target=flip71),
                             "every aifoundry3 input at E71's measured 0.3803 W/C: E65/E67 prices x their own "
                             "leak-sensitivity ratios, E70 nrd from its fixed-slope reductions, U from Q130(a)")
    keys = sorted(P["predictions"])

    E71_LISTS = ([M.E65_B[j] * rb[j] for j in range(32)], [M.E67_A[j] * ra[j] for j in range(32)])

    def arm_summary(name, A, what):
        gg, bb = A["gate"], A["bus"]
        d = {"kind": "ARM", "what": what,
             "calibration": {"wa_inf_w": r(gg["cal"]["wa_inf_w"], 4), "wb_inf_w": r(gg["cal"]["wb_inf_w"], 4),
                             "sigma_w": r(gg["cal"]["sigma_w"], 4), "u_fp32_w": r(gg["cal"]["u_fp32_w"], 4),
                             "nrd_a_w": r(gg["cal"]["nrd_a_w"], 4), "nrd_b_w": r(gg["cal"]["nrd_b_w"], 4),
                             "alpha_fp16": r(gg["alpha"]["fp16"], 4), "alpha_int8": r(gg["alpha"]["int8"], 4),
                             "randn_flip_check_w": r(gg["cal"]["randn_flip_check_w"]),
                             "randn_flip_target_w": r(gg["cal"]["randn_flip_target_w"])},
             "switching_w": {k: r(gg["pred"][k]["dw_w"]) for k in keys},
             "switching_w_bus_arm": {k: r(bb["pred"][k]["dw_w"]) for k in keys} if bb else None,
             "delta_vs_frozen_w": {k: r(gg["pred"][k]["dw_w"] - P["predictions"][k]["switching_w_600mhz_a3"]) for k in keys}}
        dd = list(d["delta_vs_frozen_w"].items())
        d["largest_moves_w"] = sorted(dd, key=lambda kv: -abs(kv[1]))[:8]
        nr = {}
        for nm, side in (("nrd_a", "a"), ("nrd_b", "b")):
            fz = nrd_tiles[side]["gate"]
            pz = M.Model(gg["cal"]["wa_inf_w"], gg["cal"]["wb_inf_w"], 0.0, gg["cal"]["sigma_w"], {"fp32": 0.0}, "gate")
            with Prices(*(E71_LISTS if name == "e71_slope" else (None, None))):
                v = pz.dw(*fz[:4], "fp32", 1.0)
            nr[nm] = {"model_on_e70_dumped_tile_w": r(v["flip_w"] + v["sign_w"]),
                      "measured_w": r(gg["cal"]["nrd_%s_w" % side])}
        d["e70_nrd_tiles"] = nr
        return d
    O["arms"] = {nm: arm_summary(nm, A, w) for nm, (A, w) in arms.items()}
    fr_sum = arm_summary("frozen", FZ, "the freeze itself, through this file's replica")
    O["arms"]["frozen_replica"] = {k: fr_sum[k] for k in ("calibration", "e70_nrd_tiles")}

    # the A1 interval: the law term at the model's own W (fault 2), never narrower than the frozen one
    def law_a1(p, t, scale, gl, e_frozen):
        sa_on, sb_on = p["S_A_w"] > 1e-9, p["S_B_w"] > 1e-9
        if not (sa_on or sb_on):
            return e_frozen
        return ((RMS_A if sa_on else 0.0) ** 2 + (RMS_B if sb_on else 0.0) ** 2) ** 0.5 * scale * (1 - gl)
    ci_a1 = {}
    for key in keys:
        t, kind = key.split("/")
        e = interval_err(g["pred"][key], t, kind, g["alpha"], g["U"], K, ref, law_term=law_a1)
        dw = g["pred"][key]["dw_w"]
        ci_a1[key] = [r(max(0.0, dw - 2 * e)), r(dw + 2 * e)]
    O["interval_a1"] = {
        "kind": "ARM", "fault": 2,
        "rule": ("the frozen interval with ONE term replaced: E70's 0.232 W law rms becomes the law's rms at the "
                 "model's own W on E70's ladder, %.3f W per active B side (15-rung fit set) and %.3f W per active A "
                 "side (7 alq rungs), in quadrature, times the format's beta and the live fraction; a kind with no "
                 "flips keeps the frozen term.  No A1 interval is narrower than its frozen one." % (RMS_B, RMS_A)),
        "rms_b_w": r(RMS_B), "rms_a_w": r(RMS_A), "switching_w_ci95_a1": ci_a1}

    # ── 7. the zero-product accounting (fault 4): R3's clauses and R9's bus-arm cells, both definitions
    ZU = arms["zero_products_unsigned"][0]
    r3 = {}
    for t in ("fp16", "int8"):
        fz_ = P["predictions"]["%s/sparse50" % t]["switching_w_600mhz_a3"] - P["predictions"]["%s/wsparse50" % t]["switching_w_600mhz_a3"]
        zu_ = ZU["gate"]["pred"]["%s/sparse50" % t]["dw_w"] - ZU["gate"]["pred"]["%s/wsparse50" % t]["dw_w"]
        r3[t] = {"frozen_w": r(fz_), "zero_products_unsigned_w": r(zu_), "registered_threshold_w": 2.0}
    r9 = {}
    for key in ("fp32/a_randn_b_zeros", "fp32/a_zeros_b_randn", "fp16/a_randn_b_zeros", "fp16/a_zeros_b_randn",
                "int8/a_full_b_zeros", "int8/a_zeros_b_full", "fp32/sparse50", "fp32/sparse90", "fp16/wsparse50"):
        fb_ = b["pred"][key]
        zb_ = ZU["bus"]["pred"][key]
        r9[key] = {"gate_arm_w": P["predictions"][key]["switching_w_600mhz_a3"],
                   "bus_arm_frozen_w": P["predictions"][key]["switching_w_alt_gating_arm"],
                   "bus_arm_frozen_sign_term_w": r(fb_["sign_w"]), "bus_arm_frozen_q": r(fb_["q"], 4),
                   "bus_arm_zero_products_unsigned_w": r(zb_["dw_w"]),
                   "gate_arm_zero_products_unsigned_w": r(ZU["gate"]["pred"][key]["dw_w"])}
    moved = sorted(((k, ZU["gate"]["pred"][k]["dw_w"] - P["predictions"][k]["switching_w_600mhz_a3"],
                     KF["std"][tuple(k.split("/"))]["gate"][2], KF["zu"][tuple(k.split("/"))]["gate"][2]) for k in keys),
                   key=lambda x: -abs(x[1]))
    O["zero_products"] = {
        "kind": "ARM", "fault": 4,
        "definition": ("frozen: q counts sign(a) XOR sign(b) for every element, zero products included.  A1 arm: a "
                       "product with a zero magnitude has sign 0, exactly an int8 product's two's-complement sign bit; "
                       "alpha_fp16 / alpha_int8 and the bus arm re-calibrated under the same rule (fp32's calibration "
                       "kinds hold no zeros, so WA, WB and sigma do not move)"),
        "alpha": {"fp16": r(ZU["gate"]["alpha"]["fp16"], 4), "int8": r(ZU["gate"]["alpha"]["int8"], 4)},
        "R3": r3, "R9_cells": r9,
        "largest_moves_gate_arm": [{"kind": k, "delta_w": r(d), "q_frozen": r(q0, 4), "q_a1": r(q1, 4)} for k, d, q0, q1 in moved[:12]]}

    # ── 8. gamma 0 and 2 (the declared sustained arms), on the frozen switching W
    runs = json.load(open(os.path.join(E64D, "results.json")))["runs"]
    gam = {}
    meas9 = P["checks"]["speed_on_e64_own_c"]["measured_sustained_mhz"]
    for gm in (0.0, 2.0, 3.0):
        gt = ST.build(runs, gm)

        def sus_of(c_a2):
            pm = ST.p_maker(gt["B"], c_a2, gm)
            return ST.simulate(pm, 65.0, gt["governor"]["tau_s"], gt["governor"]["pass_s"], t_end=80.0, t_from=40.0,
                               T0=M.T_REF, therm=gt["die_line"], tau_th=gt["tau_th"]["tau_th_s"], trip=M.T_TRIP)
        per = {}
        for key in keys:
            t = key.split("/")[0]
            c_a2 = st.mean(M.E64_C[(t, "zeros")]) + g["pred"][key]["dw_w"] / M.XFER   # unrounded, as model.py
            per[key] = r(sus_of(c_a2)["mhz"], 0)
        own = []
        for cell, mm in meas9.items():
            t, k = cell.split("/")
            own.append(sus_of(st.mean(M.E64_C[(t, k)]))["mhz"] - mm)
        gam["%.0f" % gm] = {"sustained_mhz": per, "in_sample_rms_on_e64_own_c_mhz": r(rms(own), 2)}
    for gm in ("0", "2"):
        gam[gm]["delta_vs_gamma3_mhz"] = {k: r(gam[gm]["sustained_mhz"][k] - gam["3"]["sustained_mhz"][k], 0) for k in keys}
        gam[gm]["max_abs_delta_mhz"] = max(abs(v) for v in gam[gm]["delta_vs_gamma3_mhz"].values())
    bad3 = {k: (gam["3"]["sustained_mhz"][k], P["predictions"][k]["sustained_mhz"]) for k in keys
            if gam["3"]["sustained_mhz"][k] != P["predictions"][k]["sustained_mhz"]}
    assert not bad3, ("gamma 3 replica", bad3)
    t1 = json.load(open(T1F))["variants"]
    O["gamma_arms"] = {
        "kind": "ARM", "faults": [11, 15], "arms": {k: gam[k] for k in ("0", "2")},
        "gamma3_replica_equals_freeze": True,
        "in_sample_rms_on_e64_own_c_mhz": {k: gam[k]["in_sample_rms_on_e64_own_c_mhz"] for k in gam},
        "e64_t1_out_of_sample": {k: {"sustained_oos_rms_mhz": t1[k]["sustained_oos_rms_mhz"],
                                     "sustained_informative_oos_rms_mhz": t1[k]["sustained_informative_oos_rms_mhz"],
                                     "n_informative": t1[k]["sustained_n_informative_cells"]}
                                 for k in ("0.0", "2.0", "3.0")},
        "source_oos": rel(T1F)}

    # ── 9. R5 and the E79 shape claim, scored now against E79's published lists (post-data)
    s79 = json.load(open(os.path.join(E79D, "scored.json")))
    e65fJ = {j: e71b[str(j)]["published"] for j in range(32)}
    e67fJ = {j: e71a_bits[str(j)]["published"] for j in range(32)}
    P79 = s79["passes"]
    MODT = {t: M.Model(WA, WB, 0.0, SIG, g["U"], "gate") for t in TYPES}
    r5 = {}
    for lst, t, side, footing in (("fp16_b", "fp16", "b", "jg (E65's construction)"),
                                  ("fp16_a", "fp16", "a", "A side (E67's construction)"),
                                  ("int8_a", "int8", "a", "A side (E67's construction)"),
                                  ("int8_b_kg", "int8", "b", "kg (balanced accumulators, NOT E65's footing; a bound at E71's slope, E79 Result 4)"),
                                  ("int8_b", "int8", "b", "jg (does not alternate in int8, E79 A4)")):
        wa, wb = M.price_lists(t)                 # alpha = 1, r_T included
        rowsr = []
        for kk, x in sorted(s79["prices"][lst].items(), key=lambda kv: int(kv[0])):
            j = int(kk)
            tile, tid = one_dumped(E79D, x["item"], P79, sub="hlp")
            zero, zid = one_dumped(E79D, x["zero"], P79, sub="hlp")
            fr_, fz_ = M.features(*tile, t, "gate"), M.features(*zero, t, "gate")
            s_lin = (float(np.dot(fr_[0], wa) + np.dot(fr_[1], wb)) - float(np.dot(fz_[0], wa) + np.dot(fz_[1], wb)))
            pf = MODT[t].dw(*fr_[:4], t, P["calibration"]["per_format"][t]["alpha"])
            pz = MODT[t].dw(*fz_[:4], t, P["calibration"]["per_format"][t]["alpha"])
            fp32_fJ = (e65fJ if side == "b" else e67fJ)[j]
            rowsr.append({"bit": j, "field": x["field"], "item": x["item"], "zero": x["zero"],
                          "e79_dW_w": x["dW"], "model_S_lin_alpha1_w": s_lin,
                          "alpha": x["dW"] / s_lin if s_lin > 0 else None,
                          "model_frozen_dW_w": pf["dw_w"] - pz["dw_w"], "q": fr_[2],
                          "e79_fJ": x["fJ"], "fp32_same_index_fJ": fp32_fJ,
                          "tiles_distinct_sha256": tid["distinct_sha256"]})
        mag = [x for x in rowsr if x["field"] in ("mant", "mag")]
        dear = max(mag, key=lambda x: x["bit"])
        msb = [x for x in rowsr if x["field"] in ("sign", "msb")][0]

        def ratio(v):
            den = sum(x["model_S_lin_alpha1_w"] for x in v)
            return r(sum(x["e79_dW_w"] for x in v) / den) if den > 1e-9 else None
        r5[lst] = {"type": t, "side": side, "footing": footing,
                   "model_counts_flips": sum(x["model_S_lin_alpha1_w"] for x in rowsr) > 1e-9,
                   "alpha_ratio_of_sums_all": ratio(rowsr),
                   "alpha_ratio_of_sums_significand": ratio(mag),
                   "alpha_at_top_significand_bit": r(dear["alpha"]),
                   "frozen_alpha": P["calibration"]["per_format"][t]["alpha"],
                   "frozen_model_rms_w": r(rms([x["model_frozen_dW_w"] - x["e79_dW_w"] for x in rowsr])),
                   "significand_spearman_e79": r(spearman([x["bit"] for x in mag], [x["e79_fJ"] for x in mag]), 3),
                   "significand_spearman_model": r(spearman([x["bit"] for x in mag], [x["model_S_lin_alpha1_w"] for x in mag]), 3),
                   "msb_or_sign": {"e79_fJ": r(msb["e79_fJ"], 1),
                                   "e79_rank_of_n": 1 + sorted([x["e79_fJ"] for x in rowsr], reverse=True).index(msb["e79_fJ"]),
                                   "model_rank_of_n": 1 + sorted([x["model_S_lin_alpha1_w"] for x in rowsr], reverse=True).index(msb["model_S_lin_alpha1_w"]),
                                   "n": len(rowsr)},
                   "narrow_dearer_than_fp32_same_index": "%d of %d" % (sum(1 for x in mag if x["e79_fJ"] > x["fp32_same_index_fJ"]), len(mag)),
                   "rows": [{k: (r(v, 6) if isinstance(v, float) else v) for k, v in x.items()} for x in rowsr]}
    O["score_r5_post_data"] = {
        "kind": "SCORE", "fault": 5,
        "timing": {"e79_lists_commit": "8d2fe956", "e79_pushed_pdt": "10:34:38", "freeze_commit": FREEZE_COMMIT,
                   "freeze_pushed_pdt": "10:39:42"},
        "definition": ("alpha re-solved = E79's measured step for each rung over its own zero, divided by the model's "
                       "LINEAR operand sum at alpha = 1 (model.price_lists: fp32's list by field role times r_T) on "
                       "the SAME operands -- E79's dumped tiles run through model.features, so the model's own flip "
                       "counting applies to both sides and no counting convention (E79's per-lane or per-unit int8 A "
                       "footing) enters.  Reported as a ratio of sums over the whole list and over the significand, "
                       "and at the top significand bit; the law's curvature is left out, as a per-bit price has none.  "
                       "R5 asked for alpha in [0.5, 2.0] and never said which list, so every published list is scored"),
        "lists": r5,
        "registered_band": [0.5, 2.0]}

    # ── 10. U against E79's paired constant-to-zeros step (post-data)
    sw = s79["switching"]
    O["score_u_post_data"] = {
        "kind": "SCORE", "fault": 5,
        "fp16": {"model_u_w": P["calibration"]["u_per_format"]["fp16_w"], "model_u_se_w": r(M.TARGET_SE["fp16"]),
                 "e79_const_minus_zeros_w": r(-sw["fp16"]["zeros_minus_h0_W"]), "e79_ci95_w": r(sw["fp16"]["zeros_minus_h0_ci95"])},
        "int8": {"model_u_w": P["calibration"]["u_per_format"]["int8_w"], "model_u_se_w": r(M.TARGET_SE["int8"]),
                 "e79_const_minus_zeros_w": r(-sw["int8"]["zeros_minus_h0_W"]), "e79_ci95_w": r(sw["int8"]["zeros_minus_h0_ci95"])},
        "fp32_u_w": M.U_FP32,
        "ratio_fp32_over_int8": {"model": r(M.U_FP32 / P["calibration"]["u_per_format"]["int8_w"], 1),
                                 "with_e79_int8": r(M.U_FP32 / -sw["int8"]["zeros_minus_h0_W"], 2),
                                 "e79_fp16_over_int8": r(sw["fp16"]["zeros_minus_h0_W"] / sw["int8"]["zeros_minus_h0_W"], 2)},
        "what": ("E79's paired zeros - h0 step (no idle bracket, its amendment A7) measures exactly the model's U on "
                 "E78's own card and clock: h16q / h8q are constant nonzero operands (no flips, no sign change).  It "
                 "was public 5 min before the freeze.  Every constant kind (ones, neg_ones) is predicted at U.")}

    # ── 11. the small numbers (faults 12-16)
    def union_note(t, kind):
        rec = K["kinds"][t][kind]["stats"]
        return {"gated_lane_frac": rec["gated_lane_frac"], "a_zero_word_frac": rec["a"]["zero_word_frac"],
                "b_zero_word_frac": rec["b"]["zero_word_frac"]}
    terms = {t: {"max_operand_bits_w": max((v["term_operand_bits_w"], k) for k, v in P["predictions"].items() if v["type"] == t),
                 "max_product_sign_w": max((v["term_product_sign_w"], k) for k, v in P["predictions"].items() if v["type"] == t)}
             for t in TYPES}
    e64rz = st.mean(M.E64_C[("fp32", "randn")]) - st.mean(M.E64_C[("fp32", "zeros")])
    comp = {"e64_ones_minus_zeros_x_xfer_w": r(e64_step("fp32", "ones")), "u_w": M.U_FP32,
            "e64_a_step_x_xfer_w": r((st.mean(M.E64_C[("fp32", "a_randn_b_ones")]) - st.mean(M.E64_C[("fp32", "ones")])) * M.XFER),
            "e70_nrd_a_w": M.NRD_A,
            "e64_b_step_x_xfer_w": r((st.mean(M.E64_C[("fp32", "a_ones_b_randn")]) - st.mean(M.E64_C[("fp32", "ones")])) * M.XFER),
            "e70_nrd_b_w": M.NRD_B, "e64_ones_runs_c_w": M.E64_C[("fp32", "ones")]}
    O["numbers"] = {
        "kind": "CHECK", "faults": [12, 13, 14, 16],
        "gate_union": {"rule": ("gated = A word zero OR (fp32/fp16) B word zero / (int8) B pair (l, l+8) both zero: "
                                "at independent element sparsity p about 2p - p^2 (fp32), 2p^2 - p^4 (fp16), "
                                "p^4 + p^8 - p^12 (int8)"),
                       "closed_form_at_p_0.5": {"fp32": 0.75, "fp16": 0.4375, "int8": round(0.5 ** 4 + 0.5 ** 8 - 0.5 ** 12, 4)},
                       "kinds_json_sparse50": {t: union_note(t, "sparse50") for t in TYPES}},
        "op_rate_gop_s": {"fp32": r(M.OP_RATE_600 / 1e9, 4), "fp16": r(M.OP_RATE_600 / 1e9, 4),
                          "int8": r(M.OP_RATE_600 * 546.0 / 318.0 / 1e9, 4),
                          "rule": "E70's measured 1.1208 Gop/s at 546 cycles an op, times 546/318 for int8 (model.py line 661)"},
        "card_transfer": {"e64_fp32_randn_minus_zeros_a2_w": r(e64rz, 4), "x_xfer_w": r(e64rz * M.XFER, 4),
                          "e67_anchor_step_w": M.ZR["step_w"], "abs_diff_w": r(abs(e64rz * M.XFER - M.ZR["step_w"]), 4),
                          "frozen_text_24_661_is_unsourced": True,
                          "components": comp,
                          "dates": {"e64": "2026-10-23", "e70": "2026-10-27", "days_apart": 4}},
        "term_maxima": {t: {"operand_bits_w": [r(terms[t]["max_operand_bits_w"][0]), terms[t]["max_operand_bits_w"][1]],
                            "product_sign_w": [r(terms[t]["max_product_sign_w"][0]), terms[t]["max_product_sign_w"][1]]} for t in TYPES},
        "fp32_spread": {"randn_w": P["predictions"]["fp32/randn"]["switching_w_600mhz_a3"],
                        "sparse90_w": P["predictions"]["fp32/sparse90"]["switching_w_600mhz_a3"],
                        "ratio": r(P["predictions"]["fp32/randn"]["switching_w_600mhz_a3"] / P["predictions"]["fp32/sparse90"]["switching_w_600mhz_a3"], 1)},
        "sign_bit_rank_e65": {"bit_31_w": M.E65_B[31], "rank_dearest_first": 1 + sorted(M.E65_B, reverse=True).index(M.E65_B[31]),
                              "rank_cheapest_first": 1 + sorted(M.E65_B).index(M.E65_B[31]),
                              "cheaper_positions": [j for j in range(32) if M.E65_B[j] < M.E65_B[31]],
                              "cheapest": [int(np.argmin(M.E65_B)), min(M.E65_B)],
                              "e65_registered": "A3 FAIL: sign is rank 10 of 32 (the four cheapest are bits [6, 2, 5, 3])"}}

    # ── 12. the amended rules, the scoring sets, and the erratum for the frozen text
    oos = {"fp32": [k for k in keys if k.startswith("fp32/") and k not in ("fp32/zeros", "fp32/pi", "fp32/randn")],
           "fp16": [k for k in keys if k.startswith("fp16/") and (("fp16", k.split("/")[1]) not in M.CAL_KINDS)],
           "int8": [k for k in keys if k.startswith("int8/") and (("int8", k.split("/")[1]) not in M.CAL_KINDS)]}
    O["scoring_sets_a1"] = {
        "R1_R2_out_of_sample_kinds": oos, "n": {t: len(v) for t, v in oos.items()},
        "excluded": {"fp32/zeros": "basis", "fp32/pi": "in sample (E70 anchor_pi is one of U's three levels)",
                     "fp32/randn": "selected-on (lambda)", "fp16/zeros": "basis", "fp16/ones": "calibration (U)",
                     "fp16/randn": "calibration (alpha)", "int8/zeros": "basis", "int8/ones": "calibration (U)",
                     "int8/full": "calibration (alpha)"},
        "flagged_not_blind": {"fp32/ones": "E67 measured these operands (anchor_ones) on aifoundry3 at 600 MHz before the "
                                           "freeze; the model was not fitted on it (U uses lq_h0, aq_h0, anchor_pi)"}}
    json.dump(O, open(os.path.join(HERE, a.out), "w"), indent=1, sort_keys=False, default=float)

    # ── the human report
    pr = print
    pr("Q130(c) amendment A1 — checks, arms and post-data scores on the frozen model (freeze %s, sha %s…)" % (FREEZE_COMMIT, FREEZE_SHA[:12]))
    pr("replica of the frozen calibration against predictions.json, max |d|: %s" % O["replica_check"]["max_abs_diff_against_predictions_json"])
    pr("\n1. the sign term on the model's own price-list rungs (dumped tiles; gate arm, frozen numbers)")
    for x in O["check_sign_term_on_price_list_rungs"]["rungs_with_a_sign_change"]:
        pr("   %-12s q %.3f  measured %.3f +- %.3f W   model %.3f W   (%.1fx)" % (x["item"], x["q"], x["measured_w"], x["se_w"], x["model_w"], x["ratio"]))
    pr("   rungs with no sign change: rms %.3f W over %d" % (O["check_sign_term_on_price_list_rungs"]["rms_w_rungs_without_a_sign_change"],
                                                         O["check_sign_term_on_price_list_rungs"]["n_rungs_without_a_sign_change"]))
    pr("   E67 anchors on dumped operands (model over anchor_zeros vs E67):")
    for nm, x in an.items():
        pr("     %-13s tiles %d (%d distinct)  model %.3f (flip %.3f, sign %.3f, q %.3f)  E67 %.3f  resid %+.3f" % (
            nm, x["n_tiles"], x["distinct_sha256"], x["model_over_anchor_zeros_w"], x["model_flip_w"], x["model_sign_w"], x["q"],
            x["e67_measured_over_anchor_zeros_w"], x["resid_w"]))
    L = O["check_law_on_e70_ladder"]
    pr("\n2. the law at the model's own W (WB %.3f, WA %.3f) on E70's ladder: rms B 15-rung %.3f W, with lq_h23 %.3f W; A 7-rung %.3f W"
       % (WB, WA, L["rms_model_b_fit_set_15_w"], L["rms_model_b_16_with_lq_h23_w"], L["rms_model_a_alq_7_w"]))
    pr("   E70's own law on the same sets: B %.3f W (E70: %.3f), A %.3f W (E70: %.3f)" % (
        L["rms_e70_law_b_fit_set_15_w"], s70["D2"]["R_S_refit_W"], L["rms_e70_law_a_alq_7_w"], s70["A_ceiling"]["fit_rms_W"]))
    for x in sorted(lad, key=lambda z: z["resid_w"])[:5]:
        pr("   %-8s measured %6.3f  model %6.3f  resid %+6.3f  (E70 law %6.3f)" % (x["item"], x["measured_w"], x["model_w"], x["resid_w"], x["e70_law_w"]))
    R = O["check_randn_was_selected_on"]
    pr("\n3. randn: lambda re-fitted %.4f (resid 0); declared 0 leaves %+.3f W; one-sided steps over-add by %.3f W; without the sign term %.3f W"
       % (R["lam_fitted_on_randn"]["lam"], R["lam_declared_zero"]["resid_w"], R["over_add_w"], R["randn_flip_pred_without_sign_term_w"]))
    E = O["check_e64_rows_relabelled"]
    pr("\n4. E64 rows relabelled; clean four %s rms %.3f W (published eight %.3f); outside own 95%%: %s" % (
        E["clean_four"], E["clean_four_rms_w"], E["published_eight_rms_w"], E["outside_own_95"]))
    for x in frows:
        pr("   %-15s %-62s pred %6.2f  E64 %6.2f  resid %+6.2f  1s %.2f  z %s" % (x["kind"], x["label"][:62], x["pred_w"], x["e64_w"], x["resid_w"], x["one_sigma_w"], x["z"]))
    pr("\n5. arms (gate arm; WA, WB, sigma, alpha16, alpha8; randn check; largest moves)")
    for nm, d in O["arms"].items():
        c = d["calibration"]
        pr("   %-24s WA %.3f WB %.3f sigma %.3f a16 %.3f a8 %.3f | randn %.3f vs %.3f | nrd_a %s nrd_b %s" % (
            nm, c["wa_inf_w"], c["wb_inf_w"], c["sigma_w"], c["alpha_fp16"], c["alpha_int8"], c["randn_flip_check_w"],
            c["randn_flip_target_w"], d["e70_nrd_tiles"]["nrd_a"], d["e70_nrd_tiles"]["nrd_b"]))
        if "largest_moves_w" in d:
            pr("      largest moves: %s" % ", ".join("%s %+.2f" % kv for kv in d["largest_moves_w"][:6]))
    pr("\n6. zero products unsigned: R3 %s" % json.dumps(r3))
    for k, v in r9.items():
        pr("   R9 %-22s gate %.2f | bus frozen %.2f (sign %.2f, q %.3f) -> bus A1 %.2f" % (k, v["gate_arm_w"], v["bus_arm_frozen_w"], v["bus_arm_frozen_sign_term_w"], v["bus_arm_frozen_q"], v["bus_arm_zero_products_unsigned_w"]))
    pr("\n7. gamma arms: in-sample rms on E64's own c %s MHz; max |d| vs gamma 3: g0 %s, g2 %s MHz; E64-T1 out of sample %s" % (
        O["gamma_arms"]["in_sample_rms_on_e64_own_c_mhz"], gam["0"]["max_abs_delta_mhz"], gam["2"]["max_abs_delta_mhz"],
        json.dumps(O["gamma_arms"]["e64_t1_out_of_sample"])))
    pr("\n8. R5 post-data (alpha from E79's lists)")
    for lst, x in r5.items():
        pr("   %-10s %-46s alpha sums %s  significand %s  top bit %s  (frozen %.3f)  frozen-model rms %s W  rho e79 %s model %s  msb rank e79 %d/%d model %d  dearer %s%s" % (
            lst, x["footing"][:46], x["alpha_ratio_of_sums_all"], x["alpha_ratio_of_sums_significand"], x["alpha_at_top_significand_bit"],
            x["frozen_alpha"], x["frozen_model_rms_w"], x["significand_spearman_e79"], x["significand_spearman_model"],
            x["msb_or_sign"]["e79_rank_of_n"], x["msb_or_sign"]["n"], x["msb_or_sign"]["model_rank_of_n"],
            x["narrow_dearer_than_fp32_same_index"], "" if x["model_counts_flips"] else "  [the model's own stream counts no flips here]"))
    U_ = O["score_u_post_data"]
    pr("\n9. U post-data: fp16 model %.3f vs E79 %.3f +- %.3f; int8 model %.3f vs E79 %.3f +- %.3f; fp32/int8 %s" % (
        U_["fp16"]["model_u_w"], U_["fp16"]["e79_const_minus_zeros_w"], U_["fp16"]["e79_ci95_w"], U_["int8"]["model_u_w"],
        U_["int8"]["e79_const_minus_zeros_w"], U_["int8"]["e79_ci95_w"], U_["ratio_fp32_over_int8"]))
    N_ = O["numbers"]
    pr("\n10. numbers: %s" % json.dumps({k: N_[k] for k in ("op_rate_gop_s", "card_transfer", "term_maxima", "fp32_spread", "sign_bit_rank_e65")})[:2500])
    pr("    gate union at sparse50: %s" % json.dumps(N_["gate_union"]["kinds_json_sparse50"]))
    pr("\n11. R1/R2 out-of-sample sets: %s" % O["scoring_sets_a1"]["n"])
    pr("\n%s sha256 %s" % (a.out, sha(os.path.join(HERE, a.out))))
    return 0


if __name__ == "__main__":
    sys.exit(main())
