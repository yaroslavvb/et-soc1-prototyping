#!/usr/bin/env python3
# /// script
# requires-python = ">=3.9,<3.13"
# dependencies = ["numpy==1.26.4"]
# ///
"""Q132(r), stage 2 of 3: cut the captured products into 2,048-byte kinds tiles, with make_kinds.py's own encode() and
tile_stats() (imported, unchanged), so a real2 tile is the same kind of object as E78's 51 kinds and Q130(n)'s nine.
Nothing here touches a card.

    python3 make_real2.py --cap <capture_real2.py's --out> --out tools/claims-v3/kinds/real2

Windows, as Q130(n): aligned blocks (16 rows, K, 16 columns; K = 16 / 32 / 64 for fp32 / fp16 / int8), the same k range
in A and B. Each new window is the one of 20 seeded aligned windows nearest the 20-window median of (gated fraction,
zero-word fraction per side, stream-order Hamming per field per side, bus bits per op), by sum |x - median| / MAD. A
tile compared with another (a calibration, a forward pass) takes that tile's window instead, as its spec says.
The three ReLU products cut in several formats (NESTED) share one window: the same 16 rows and 16 columns, and nested k
blocks (fp32's 16 k are the first of fp16's 32, which are the first of int8's 64), chosen by the same rule with the
distances summed over the three formats, so that "the same numbers in another format" means what it says.

Types: fp32 as computed. fp16 IEEE round-to-nearest-even of the fp32 values, unless the product was computed in fp16
(*_fp16fwd). int8, zero point 0 unless named, weights per output channel, round half to even, clip +-127, activations:
    default   per tensor, scale = max|x| / 127            (Q130(n)'s calibration)
    per_token per row (token or patch), scale = its max|x| / 127   (amend_real.py's "per-token max-abs")
    p9999     per tensor, scale = the 99.99th percentile of |x| / 127, larger values clip
    p999      per tensor, scale = the 99.9th percentile of |x| / 127, larger values clip
    asym      the TFLite int8 convention for activations: s = (hi - lo) / 255 with lo <= 0 <= hi over the whole tensor,
              zero point z = round(-128 - lo / s), code = clip(round(x / s) + z, -128, 127). B is the same per-channel
              symmetric int8 as `default`, so a pair differs in A alone. The kernel's format is signed, and it multiplies
              the raw codes: what the card computes is the true integer product plus z * sum(B over k) per output column,
              which a deployed kernel subtracts afterwards. A ReLU zero becomes -128 (0x80), so this calibration shows
              the zero gate nothing.
"""
import argparse
import hashlib
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
ap = argparse.ArgumentParser()
ap.add_argument("--cap", required=True)
ap.add_argument("--dl", required=True, help="the directory holding manifest-models.json and images/manifest-images.json")
ap.add_argument("--out", default=HERE)
ap.add_argument("--repo", default=os.path.normpath(os.path.join(HERE, "..", "..", "..", "..")))
ARGS = ap.parse_args()
sys.path.insert(0, os.path.join(ARGS.repo, "tools/claims-v3/kinds/real"))
import make_real as MR  # noqa: E402

MK = MR.MK
SEED = 20261101
N_WINDOWS = 20
TYPES = MR.TYPES

# ------------------------------------------------------------------ the tile list, frozen here
# group: Z exact zeros (ReLU); N no exact zeros; T bf16-grid weights; M negative zeros; F fp16 forward pass; B bf16 forward
# pass; C an int8 calibration. tier 1 is the run's list; tier 2 runs if the lane's budget allows.
def S(name, typ, group, tier, product=None, quant="default", window_of=None, window_real=None, why=""):
    return {"name": name, "type": typ, "group": group, "tier": tier, "product": product or name, "quant": quant,
            "window_of": window_of, "window_real": window_real, "why": why}


SPEC = [
    S("resnet18_l2c1", "fp32", "Z", 1, "resnet18_layer2_0_conv1", why="a ReLU CNN's conv layer at the low end of the live-share range"),
    S("resnet18_l3c1", "fp32", "Z", 1, "resnet18_layer3_0_conv1", why="a ReLU CNN's conv layer: all three formats"),
    S("resnet18_l3c1", "fp16", "Z", 1, "resnet18_layer3_0_conv1"),
    S("resnet18_l3c1", "int8", "Z", 1, "resnet18_layer3_0_conv1"),
    S("vgg16_fc2", "fp32", "Z", 1, why="fully connected, mostly exact zeros, independent along k: all three formats"),
    S("vgg16_fc2", "fp16", "Z", 1),
    S("vgg16_fc2", "int8", "Z", 1),
    S("t5small_l0_down", "fp32", "Z", 1, "t5small_l0_ff_down", why="a ReLU transformer's feed-forward; 92% exact zeros; its weights sit on the bf16 grid"),
    S("t5small_l0_down", "fp16", "Z", 1, "t5small_l0_ff_down"),
    S("t5small_l0_down", "int8", "Z", 2, "t5small_l0_ff_down", why="tier 2: at this share the int8 tile draws under 1 W"),
    S("gpt2_l3_mlp_down", "fp32", "N", 1, why="another GPT-2 layer, GELU output"),
    S("gpt2_l9_attn_qk", "fp32", "N", 1, why="another GPT-2 layer, attention: the kind of tile that sat lowest in E86"),
    S("gpt2_l9_attn_qk", "fp16", "N", 1),
    S("bert_l6_up", "fp32", "N", 1, "bert_l6_ff_up", why="another model, LayerNorm output x up-projection"),
    S("bert_l6_up", "fp16", "N", 1, "bert_l6_ff_up"),
    S("vit_l5_down", "fp32", "N", 1, "vit_l5_ff_down", why="a vision transformer, GELU output x down-projection, on images"),
    S("vit_l5_down", "fp16", "N", 1, "vit_l5_ff_down"),
    S("t5small_l0_up", "fp32", "T", 1, "t5small_l0_ff_up", why="no zeros, A full mantissa, B on the bf16 grid: a real tile whose B bits barely move"),
    S("vit_l11_down", "fp32", "M", 1, "vit_l11_ff_down", why="55% of A's elements are -0.0 (0x80000000): numerically zero, and the gate's test is word == 0"),
    S("vit_l11_down", "int8", "M", 2, "vit_l11_ff_down", window_of=None, why="tier 2: the same layer in int8, where -0.0 becomes a zero byte"),
    S("gpt2_l6_mlp_down_fp16fwd", "fp16", "F", 1, window_real="l6_mlp_down", why="E86's fp16 window, A from an fp16 forward pass; pairs with fp16.real_l6_mlp_down"),
    S("gpt2_l6_attn_qk_fp16fwd", "fp16", "F", 2, window_real="l6_attn_qk", why="tier 2: E86's fp16 window, q and k from an fp16 forward pass; pairs with fp16.real_l6_attn_qk"),
    S("gpt2_l6_mlp_down_bf16fwd", "fp32", "B", 2, why="tier 2: a bf16 forward pass held in fp32 bytes, beside E78's synthetic bf16trunc"),
    S("gpt2_l6_down_per_token", "int8", "C", 1, "gpt2_l6_mlp_down", "per_token", window_real="l6_mlp_down", why="E86's int8 window, per-token calibration; pairs with int8.real_l6_mlp_down"),
    S("gpt2_l6_down_p9999", "int8", "C", 1, "gpt2_l6_mlp_down", "p9999", window_real="l6_mlp_down", why="E86's int8 window, 99.99th percentile clip"),
    S("gpt2_l6_down_p999", "int8", "C", 1, "gpt2_l6_mlp_down", "p999", window_real="l6_mlp_down", why="E86's int8 window, 99.9th percentile clip"),
    S("gpt2_l11_down_maxabs", "int8", "C", 1, "gpt2_l11_mlp_down", "default", why="a GELU layer with one huge activation: max-abs crushes it to zeros"),
    S("gpt2_l11_down_p999", "int8", "C", 1, "gpt2_l11_mlp_down", "p999", window_of=("gpt2_l11_down_maxabs", "int8"), why="the same window, 99.9th percentile clip"),
    S("gpt2_l11_down_asym", "int8", "C", 2, "gpt2_l11_mlp_down", "asym", window_of=("gpt2_l11_down_maxabs", "int8"), why="tier 2: the same window, asymmetric activations"),
    S("vgg16_fc2_asym", "int8", "C", 1, "vgg16_fc2", "asym", window_of=("vgg16_fc2", "int8"), why="the same window as vgg16_fc2 int8, asymmetric activations: zeros become -128 and the gate has nothing"),
]
E86_RERUN = [("fp16", "l6_mlp_down"), ("int8", "l6_mlp_down")]
NESTED = {"resnet18_l3c1": "resnet18_layer3_0_conv1", "vgg16_fc2": "vgg16_fc2", "t5small_l0_down": "t5small_l0_ff_down"}
RELU_PRODUCTS = ["resnet18_layer1_0_conv2", "resnet18_layer1_1_conv1", "resnet18_layer2_0_conv1", "resnet18_layer2_1_conv2",
                 "resnet18_layer3_0_conv1", "resnet18_layer3_1_conv1", "resnet18_layer4_0_conv1", "resnet18_layer4_1_conv2",
                 "vgg16_fc2", "vgg16_fc3", "t5small_l0_ff_down", "t5small_l2_ff_down", "t5small_l5_ff_down"]
GELU_PRODUCTS = ["gpt2_l0_mlp_down", "gpt2_l3_mlp_down", "gpt2_l6_mlp_down", "gpt2_l9_mlp_down", "gpt2_l11_mlp_down",
                 "bert_l2_ff_down", "bert_l6_ff_down", "bert_l11_ff_down", "distilbert_l1_ff_down", "distilbert_l3_ff_down",
                 "distilbert_l5_ff_down", "vit_l2_ff_down", "vit_l5_ff_down", "vit_l11_ff_down"]


def q_sym(x, s):
    return np.clip(np.rint(x.astype(np.float64) / s), -127, 127).astype(np.int8)


def int8_activation(x, quant, tok_axis=0):
    """x is an activation matrix; tok_axis is the axis of its tokens or patches. Returns the int8 codes and a record."""
    a = np.abs(x.astype(np.float64))
    if quant == "default":
        s = float(a.max()) / 127.0
        return q_sym(x, s), {"scheme": "per tensor, symmetric, scale = max|x| / 127, round half to even, clip +-127", "scale": s, "zero_point": 0}
    if quant == "per_token":
        s = a.max(axis=1 - tok_axis, keepdims=True) / 127.0
        return q_sym(x, s), {"scheme": "per token (row), symmetric, scale = that row's max|x| / 127", "scale_summary": {"min": float(s.min()), "median": float(np.median(s)), "max": float(s.max())}, "zero_point": 0}
    if quant in ("p9999", "p999"):
        p = {"p9999": 0.9999, "p999": 0.999}[quant]
        s = float(np.quantile(a, p)) / 127.0
        return q_sym(x, s), {"scheme": f"per tensor, symmetric, scale = the {100 * p:.2f}th percentile of |x| / 127, larger values clip to +-127", "scale": s, "zero_point": 0,
                             "clipped_frac": round(float(np.mean(a / s > 127.5)), 6)}
    if quant == "asym":
        lo, hi = min(float(x.min()), 0.0), max(float(x.max()), 0.0)
        s = (hi - lo) / 255.0
        z = int(np.clip(np.rint(-128 - lo / s), -128, 127))
        q = np.clip(np.rint(x.astype(np.float64) / s) + z, -128, 127).astype(np.int8)
        return q, {"scheme": "TFLite int8 activations: per tensor, asymmetric, s = (hi - lo) / 255 with lo <= 0 <= hi, z = round(-128 - lo / s), code = clip(round(x / s) + z, -128, 127)",
                   "scale": s, "zero_point": z, "lo": lo, "hi": hi,
                   "what_the_card_computes": "sum(code * B) = sum(x / s * B) + z * sum(B): the true integer product plus a per-column constant a deployed kernel subtracts afterwards"}
    raise ValueError(quant)


def operands(prod, t, quant):
    d = np.load(os.path.join(ARGS.cap, "products", prod["key"] + ".npz"))
    A, B = d["A"], d["B"]
    rec = prod["rec"]
    q = {}
    if t == "fp32":
        if A.dtype != np.float32:
            raise SystemExit(f"{prod['key']} is {A.dtype}, not fp32")
        return A, B, q
    if t == "fp16":
        if A.dtype == np.float16:
            return A, B, {"A": {"scheme": "computed in fp16"}, "B": {"scheme": "fp16 from the forward pass" if rec["B_is"] == "activation" else "IEEE round to nearest even of the fp32 weight"}}
        q = {"A": {"scheme": "IEEE round to nearest even from the fp32 value (numpy astype)"}, "B": {"scheme": "IEEE round to nearest even from the fp32 value (numpy astype)"}}
        return A.astype(np.float16), B.astype(np.float16), q
    Aq, qa = int8_activation(A, quant)
    q["A"] = qa
    if rec["B_is"] == "weight":
        Bq, sb = MR.quant_per_out_channel(B)
        q["B"] = {"scheme": "per output channel (column of the (in, out) weight), symmetric, scale_j = max_k |W[k, j]| / 127, round half to even, clip +-127",
                  "scale_summary": {"n": int(sb.size), "min": float(sb.min()), "median": float(np.median(sb)), "max": float(sb.max())}}
    else:
        Bq, qb = int8_activation(B, quant, tok_axis=1)
        q["B"] = qb
    return Aq, Bq, q


def zero_stats(raw, t):
    """What the gate sees (word == 0) against what is numerically zero, per side, from the tile's own words."""
    aw, bw = MK.words_of(raw)
    E = MK.TYPES[t][0]
    ew = 32 // E
    out = {}
    for side, w in (("a", aw), ("b", bw)):
        w = np.asarray(w, dtype=np.uint64).reshape(-1)
        el = [(w >> np.uint64(e * ew)) & np.uint64((1 << ew) - 1) for e in range(E)]
        neg0 = np.uint64(1 << (ew - 1))
        if t == "int8":
            num0 = [x == 0 for x in el]
            nz = np.zeros_like(w, dtype=bool)
        else:
            num0 = [(x == 0) | (x == neg0) for x in el]
            nz = np.stack([x == neg0 for x in el]).any(axis=0)
        all_num0 = np.stack(num0).all(axis=0)
        out[side] = {"plus_zero_word_frac": round(float(np.mean(w == 0)), 6),
                     "numeric_zero_word_frac": round(float(np.mean(all_num0)), 6),
                     "plus_zero_elem_frac": round(float(np.mean(np.concatenate([x == 0 for x in el]))), 6),
                     "neg_zero_elem_frac": 0.0 if t == "int8" else round(float(np.mean(np.concatenate([x == neg0 for x in el]))), 6),
                     "words_holding_a_neg_zero_frac": round(float(np.mean(nz)), 6)}
    a_seq, b_seq = MK.issue_streams_fast(aw, bw, t)
    # the gate as built tests word == 0; beside it, what it would close if it tested numeric zero (reported only)
    if t == "int8":
        out["gated_if_gate_took_numeric_zero"] = float(MK.gate_mask(a_seq, b_seq, t).mean())
    else:
        s = np.uint64(0x7FFFFFFF) if t == "fp32" else np.uint64(0x7FFF7FFF)
        out["gated_if_gate_took_numeric_zero"] = round(float(((a_seq[:, None] & s) == 0).__or__((b_seq & s) == 0).mean()), 6)
    return out


def choose_window(Aq, Bq, t, tag, P, rows_t):
    K = MK.TYPES[t][3]
    nr, nk, nj = Aq.shape[0] // 16, Aq.shape[1] // K, Bq.shape[1] // 16
    n_w = min(N_WINDOWS, nr * nk * nj)
    rng = np.random.default_rng(int.from_bytes(hashlib.sha256(f"{SEED}/real2/{tag}/{t}".encode()).digest()[:8], "little"))
    seen, cands = set(), []
    while len(cands) < n_w:
        w = (int(rng.integers(nr)) * 16, int(rng.integers(nk)) * K, int(rng.integers(nj)) * 16)
        if w in seen:
            continue
        seen.add(w)
        Aw, Bw = MR.cut(Aq, Bq, w[0], w[1], w[2], K)
        raw = MK.encode(Aw, Bw, t)
        st = MK.tile_stats(raw, t)
        fe = MR.features(raw, t)
        cands.append({"rows": [w[0], w[0] + 16], "k": [w[1], w[1] + K], "cols": [w[2], w[2] + 16],
                      "vector": MR.window_vector(st, t), "D_pred_w": MR.predict_D(P, t, fe, rows_t)["point_w"]})
    V = np.array([c["vector"] for c in cands], dtype=np.float64)
    med = np.median(V, axis=0)
    mad = np.median(np.abs(V - med), axis=0)
    dist = np.sum(np.abs(V - med) / np.where(mad > 0, mad, 1.0), axis=1)
    for c, dd in zip(cands, dist):
        c["distance_to_median"] = round(float(dd), 4)
        c["vector"] = [round(float(x), 6) for x in c["vector"]]
    ci = int(np.argmin(dist))
    return cands[ci], ci, cands, med, mad


def rows_are(rec, rows_w, CAP):
    """What the window's 16 rows are, in words: the source text's tokens, or which image and which patches or tokens."""
    r0, r1 = rows_w
    order = CAP.get("images_order") or []
    per = rec.get("patches_per_image") or rec.get("tokens_per_image")
    if per:
        i0, i1 = r0 // per, (r1 - 1) // per
        unit = "patches in scan order" if rec.get("patches_per_image") else "tokens"
        imgs = order[i0:i1 + 1]
        return f"image {i0} ({imgs[0]}), {unit} {r0 % per}-{(r1 - 1) % per}" if i0 == i1 else f"images {i0}-{i1} ({', '.join(imgs)}), rows cross the image boundary"
    if rec.get("images"):
        return "images, one row each: " + ", ".join(order[r0:r1])
    return f"tokens {r0}-{r1 - 1} of the source text"


def choose_nested(name, product, CAP, P, rows):
    """One window for all three formats: the same rows and columns, nested k blocks, nearest the 20-window median with the
    per-format distances summed. The int8 block (64 k) is the aligned unit."""
    prod = {"key": product, "rec": CAP["products"][product]}
    ops = {t: operands(prod, t, "default")[:2] for t in TYPES}
    Aq8, Bq8 = ops["int8"]
    nr, nk, nj = Aq8.shape[0] // 16, Aq8.shape[1] // 64, Bq8.shape[1] // 16
    n_w = min(N_WINDOWS, nr * nk * nj)
    rng = np.random.default_rng(int.from_bytes(hashlib.sha256(f"{SEED}/real2/nested/{name}".encode()).digest()[:8], "little"))
    seen, cands = set(), []
    while len(cands) < n_w:
        w = (int(rng.integers(nr)) * 16, int(rng.integers(nk)) * 64, int(rng.integers(nj)) * 16)
        if w in seen:
            continue
        seen.add(w)
        c = {"rows": [w[0], w[0] + 16], "cols": [w[2], w[2] + 16], "k0": w[1], "fmt": {}}
        for t in TYPES:
            K = MK.TYPES[t][3]
            Aq, Bq = ops[t]
            raw = MK.encode(*MR.cut(Aq, Bq, w[0], w[1], w[2], K), t)
            st = MK.tile_stats(raw, t)
            c["fmt"][t] = {"vector": MR.window_vector(st, t), "D_pred_w": MR.predict_D(P, t, MR.features(raw, t), rows[t])["point_w"],
                           "gated": st["gated_lane_frac"], "bus": st["bus_bits_per_op"]}
        cands.append(c)
    dist = np.zeros(len(cands))
    wc = {}
    for t in TYPES:
        V = np.array([c["fmt"][t]["vector"] for c in cands], dtype=np.float64)
        med = np.median(V, axis=0)
        mad = np.median(np.abs(V - med), axis=0)
        dist += np.sum(np.abs(V - med) / np.where(mad > 0, mad, 1.0), axis=1)
        wc[t] = {"statistics": MR.window_names(t), "median": [round(float(x), 6) for x in med], "mad": [round(float(x), 6) for x in mad],
                 "D_pred_band_w": [min(c["fmt"][t]["D_pred_w"] for c in cands), round(float(np.median([c["fmt"][t]["D_pred_w"] for c in cands])), 3), max(c["fmt"][t]["D_pred_w"] for c in cands)],
                 "gated_band": [min(c["fmt"][t]["gated"] for c in cands), round(float(np.median([c["fmt"][t]["gated"] for c in cands])), 6), max(c["fmt"][t]["gated"] for c in cands)]}
    ci = int(np.argmin(dist))
    ch = cands[ci]
    table = [{"rows": c["rows"], "k0": c["k0"], "cols": c["cols"], "gated": {t: c["fmt"][t]["gated"] for t in TYPES}, "D_pred_w": {t: c["fmt"][t]["D_pred_w"] for t in TYPES},
              "bus_bits_per_op": {t: c["fmt"][t]["bus"] for t in TYPES}, "distance_to_median": round(float(d), 4)} for c, d in zip(cands, dist)]
    return ch, ci, table, wc


def main():
    for p, want in MR.FROZEN_SHA.items():
        if MR.sha_file(os.path.join(ARGS.repo, p)) != want:
            sys.exit(f"refused: {p} differs from its frozen sha256")
    real = json.load(open(os.path.join(ARGS.repo, "tools/claims-v3/kinds/real/real.json")))
    PR = json.load(open(os.path.join(ARGS.repo, "tools/claims-v3/kinds/real/predictions-real.json")))
    E78 = json.load(open(os.path.join(ARGS.repo, MR.E78J)))
    P, rows = MR.fit_predictor(E78, ARGS.repo)
    for t in TYPES:                                            # the frozen beta decides; the refit must agree to 1e-4
        fz = PR["predictor"]["per_type"][t]
        if P[t]["selected"] != fz["selected"] or np.max(np.abs(np.array(P[t]["beta"]) - np.array(fz["beta"]))) > 1e-4:
            sys.exit(f"refused: the predictor for {t} does not reproduce the frozen one")
        P[t]["beta"] = fz["beta"]
    CAP = json.load(open(os.path.join(ARGS.cap, "capture.json")))
    td = os.path.join(ARGS.out, "tiles")
    tiles, chosen = {}, {}
    nested = {n: choose_nested(n, pr, CAP, P, rows) for n, pr in NESTED.items()}
    for sp in SPEC:
        t, name = sp["type"], sp["name"]
        prod = {"key": sp["product"], "rec": CAP["products"][sp["product"]]}
        Aq, Bq, quant = operands(prod, t, sp["quant"])
        K = MK.TYPES[t][3]
        wc = None
        if sp["name"] in nested and sp["window_of"] is None:
            ch, ci, table, wcn = nested[sp["name"]]
            rows_w, k_w, cols_w = ch["rows"], [ch["k0"], ch["k0"] + K], ch["cols"]
            rule = "one window for all three formats: the same rows and columns, nested k blocks (fp32's 16 k are the first of fp16's 32, the first of int8's 64), nearest the 20-window median with the distances summed over the formats"
            wc = {**wcn[t], "index": ci, "nested_candidates": table}
        elif sp["window_real"]:
            w = real["tiles"][t][sp["window_real"]]["window"]
            rows_w, k_w, cols_w = w["rows"], w["k"], w["cols"]
            rule = f"Q130(n)'s committed window for {t}/{sp['window_real']} (E86 ran it), so the pair differs only in what is named"
        elif sp["window_of"]:
            w = chosen[sp["window_of"]]
            rows_w, k_w, cols_w = w["rows"], w["k"], w["cols"]
            rule = f"the window of {sp['window_of'][1]}/{sp['window_of'][0]}, so the pair differs only in the calibration"
        else:
            ch, ci, cands, med, mad = choose_window(Aq, Bq, t, name, P, rows[t])
            rows_w, k_w, cols_w = ch["rows"], ch["k"], ch["cols"]
            rule = f"the one of {len(cands)} seeded aligned windows nearest their median (sum of |x - median| / MAD over window_choice.statistics)"
            wc = {"statistics": MR.window_names(t), "median": [round(float(x), 6) for x in med], "mad": [round(float(x), 6) for x in mad],
                  "index": ci, "D_pred_band_w": [min(c["D_pred_w"] for c in cands), round(float(np.median([c["D_pred_w"] for c in cands])), 3), max(c["D_pred_w"] for c in cands)],
                  "gated_band": [min(c["vector"][0] for c in cands), round(float(np.median([c["vector"][0] for c in cands])), 6), max(c["vector"][0] for c in cands)],
                  "candidates": [{"rows": c["rows"], "k": c["k"], "cols": c["cols"], "gated": c["vector"][0], "bus_bits_per_op": int(c["vector"][-1]), "D_pred_w": c["D_pred_w"], "distance_to_median": c["distance_to_median"]} for c in cands]}
        chosen[(name, t)] = {"rows": rows_w, "k": k_w, "cols": cols_w}
        Aw, Bw = Aq[rows_w[0]:rows_w[1], k_w[0]:k_w[1]], Bq[k_w[0]:k_w[1], cols_w[0]:cols_w[1]]
        if Aw.shape != (16, K) or Bw.shape != (K, 16):
            sys.exit(f"refused: {t}/{name} window shape {Aw.shape} {Bw.shape}")
        raw = MK.encode(Aw, Bw, t)
        if t != "int8" and not (np.all(np.isfinite(np.asarray(Aw, dtype=np.float64))) and np.all(np.isfinite(np.asarray(Bw, dtype=np.float64)))):
            sys.exit(f"refused: {t}/{name} holds an inf or a NaN")
        dtype, size = MK.TYPES[t][2], MK.TYPES[t][1]
        da, db = MK.decode(raw, t)
        if not (np.array_equal(da.view(f"<u{size}"), np.asarray(Aw).astype(dtype).view(f"<u{size}")) and
                np.array_equal(db.view(f"<u{size}"), np.asarray(Bw).astype(dtype).view(f"<u{size}"))):
            sys.exit(f"refused: {t}/{name} does not decode back to its intended elements")
        os.makedirs(os.path.join(td, t), exist_ok=True)
        with open(os.path.join(td, t, name + ".bin"), "wb") as fh:
            fh.write(raw)
        st = MK.tile_stats(raw, t)
        fe = MR.features(raw, t)
        whole = {"A": MR.whole_stats(Aq, t, "a"), "B": MR.whole_stats(Bq, t, "b")}
        tiles.setdefault(t, {})[name] = {
            "file": f"tiles/{t}/{name}.bin", "bytes": len(raw), "sha256": MR.sha_bytes(raw), "sha256_a": MR.sha_bytes(raw[:1024]), "sha256_b": MR.sha_bytes(raw[1024:]),
            "group": sp["group"], "tier": sp["tier"], "why": sp["why"], "product": sp["product"], "matrix": sp["product"], "calibration": sp["quant"] if t == "int8" else None,
            "what": prod["rec"]["what"], "source": prod["rec"]["source"], "A_is": prod["rec"]["A_is"], "B_is": prod["rec"]["B_is"],
            "window": {"rows": rows_w, "k": k_w, "cols": cols_w, "rule": rule, "rows_are": rows_are(prod["rec"], rows_w, CAP)}, "quantisation": quant, "stats": st, "zero": zero_stats(raw, t),
            "whole_matrix": {"A": {k: whole["A"][k] for k in ("zero_word_frac", "zero_elem_frac", "mean", "sd", "max_abs")}, "B": {k: whole["B"][k] for k in ("zero_word_frac", "zero_elem_frac", "mean", "sd", "max_abs")}},
            "window_choice": wc, "features": fe}
        if sp["window_real"] and sp["quant"] == "default" and t == "int8":
            pass
        print(f"{t} {name:28s} g {st['gated_lane_frac']:.3f} Az {st['a']['zero_word_frac']:.3f} Ae {st['a']['zero_elem_frac']:.3f} bus {st['bus_bits_per_op']:6d} D {MR.predict_D(P, t, fe, rows[t])['point_w']:6.2f} win {rows_w} {k_w} {cols_w}", flush=True)

    # checks: the committed int8 l6_mlp_down tile must come back byte for byte from this capture
    Aq, Bq, _ = operands({"key": "gpt2_l6_mlp_down", "rec": CAP["products"]["gpt2_l6_mlp_down"]}, "int8", "default")
    w = real["tiles"]["int8"]["l6_mlp_down"]["window"]
    r0 = MK.encode(Aq[w["rows"][0]:w["rows"][1], w["k"][0]:w["k"][1]], Bq[w["k"][0]:w["k"][1], w["cols"][0]:w["cols"][1]], "int8")
    reproduces = MR.sha_bytes(r0) == real["tiles"]["int8"]["l6_mlp_down"]["sha256"]
    print("committed int8 l6_mlp_down reproduced from this capture:", reproduces)
    if not reproduces:
        sys.exit("refused: the committed int8 tile does not reproduce")

    # the desk table: every captured ReLU and GELU product, zero words and gate per format over the whole matrix
    desk = {}
    for name in RELU_PRODUCTS + GELU_PRODUCTS:
        rec = CAP["products"][name]
        row = {"A_plus_zero_frac": rec["stats"]["A"]["plus_zero_frac"], "A_neg_zero_frac": rec["stats"]["A"]["neg_zero_frac"], "A_max_abs": rec["stats"]["A"]["max_abs"], "A_p99_abs": rec["stats"]["A"]["p99_abs"], "formats": {}}
        for t in TYPES:
            Aq, Bq, _ = operands({"key": name, "rec": rec}, t, "default")
            wa, wb = MR.whole_stats(Aq, t, "a"), MR.whole_stats(Bq, t, "b")
            row["formats"][t] = {"A_zero_word_frac": wa["zero_word_frac"], "A_zero_elem_frac": wa["zero_elem_frac"], "B_zero_word_frac": wb["zero_word_frac"]}
        Aq, Bq, _ = operands({"key": name, "rec": rec}, "int8", "p999")
        row["formats"]["int8_p999"] = {"A_zero_word_frac": MR.whole_stats(Aq, "int8", "a")["zero_word_frac"], "A_zero_elem_frac": MR.whole_stats(Aq, "int8", "a")["zero_elem_frac"]}
        desk[name] = row

    models = json.load(open(os.path.join(ARGS.dl, "manifest-models.json")))
    images = json.load(open(os.path.join(ARGS.dl, "images", "manifest-images.json")))
    spec = {
        "experiment": "Q132(r)", "date": "2026-11-01", "generator": "tools/claims-v3/kinds/real2/make_real2.py",
        "what": "real tensors from public models on public-domain inputs, cut as 2,048-byte kinds tiles (A then B, 1,024 bytes each), for E95 and E96",
        "models": models, "images": {"licence": images.get("licence"), "order": CAP.get("images_order"), "files": images.get("images")},
        "text": {"source": MR.TEXT_SOURCE, "sha256": MR.sha_bytes(MR.TEXT.encode("ascii")), "see": "tools/claims-v3/kinds/real/real.json text"},
        "capture_checks": CAP["checks"], "build": CAP.get("build"),
        "conventions": {"layout_and_stream": "make_kinds.py encode() / tile_stats(), imported unchanged (kinds.json facts)", "K": {t: MK.TYPES[t][3] for t in TYPES},
                        "tier": "tier 1 is the run's list (25 new tiles + 2 E86 tiles = 27); tier 2 runs if the lane's budget allows"},
        "e86_tiles_rerun_with_them": [{"type": t, "matrix": m, "item": f"{t}.real_{m}", "file": f"tools/claims-v3/kinds/real/{real['tiles'][t][m]['file']}", "sha256": real["tiles"][t][m]["sha256"]} for t, m in E86_RERUN],
        "committed_int8_l6_mlp_down_reproduced_from_this_capture": reproduces,
        "desk_gate_by_format": desk,
        "tiles": tiles,
    }
    with open(os.path.join(ARGS.out, "real2.json"), "w") as fh:
        json.dump(spec, fh, indent=1)
        fh.write("\n")
    print("real2.json sha256", MR.sha_file(os.path.join(ARGS.out, "real2.json")))
    return 0


if __name__ == "__main__":
    sys.exit(main())
