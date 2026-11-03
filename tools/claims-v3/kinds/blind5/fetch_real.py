#!/usr/bin/env python3
"""Q138(b) blind pool 5: fetch the few pythia-70m layer-0 tensors the real tiles need and run layer 0's forward pass
on a public-domain text, writing small float32 cuts to real/ and their provenance to real/provenance.json.

    python3 fetch_real.py            # needs network (huggingface.co); numpy only; about 6 MB fetched

Only the safetensors header and the bytes of the tensors used are fetched, by HTTP range requests at a pinned
commit; the token-embedding rows are fetched one row each. make_blind5.py reads only real/, never the network.

The forward pass is GPT-NeoX's layer 0 as pythia-70m configures it (hidden 512, 8 heads of 64, rotary on the first
16 dims of each head with base 10000, LayerNorm eps 1e-5, exact-erf GELU, parallel residual: the MLP reads
post_attention_layernorm(x) of the layer's own input x, so layer 0's MLP needs no attention output). It is computed
in float32 from the model's fp16 weights (each exactly representable in float32).
"""
import hashlib
import json
import math
import os
import struct
import sys
import urllib.request

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "real")
REPO = "EleutherAI/pythia-70m"
REV = "a39f36b100fe8a5377810d56c3f4789b9c53ac42"     # the commit blind pool 4 pinned
URL = f"https://huggingface.co/{REPO}/resolve/{REV}/model.safetensors"
TOK_URL = f"https://huggingface.co/{REPO}/resolve/{REV}/tokenizer.json"
# Charles Dickens, A Tale of Two Cities (1859), its opening; public domain.
TEXT = ("It was the best of times, it was the worst of times, it was the age of wisdom, it was the age of "
        "foolishness, it was the epoch of belief, it was the epoch of incredulity, it was the season of Light, "
        "it was the season of Darkness, it was the spring of hope, it was the winter of despair")
T = 32                       # tokens kept: positions 0..31
HID, HEADS, HS, ROT, FF = 512, 8, 64, 16, 2048
UA = {"User-Agent": "q138b-pool5/1.0"}
FETCHED = []


def get(url, lo=None, hi=None):
    h = dict(UA)
    if lo is not None:
        h["Range"] = f"bytes={lo}-{hi}"
    req = urllib.request.Request(url, headers=h)
    with urllib.request.urlopen(req, timeout=60) as r:
        b = r.read()
    if lo is not None:
        assert len(b) == hi - lo + 1, (url, lo, hi, len(b))
    return b


def header():
    n = struct.unpack("<Q", get(URL, 0, 7))[0]
    hdr = json.loads(get(URL, 8, 8 + n - 1))
    return hdr, 8 + n


def tensor(hdr, base, name, rows=None):
    """The whole tensor (or the listed rows of a 2-D one) as float32. fp16 only."""
    t = hdr[name]
    assert t["dtype"] == "F16", (name, t["dtype"])
    lo, hi = t["data_offsets"]
    shape = t["shape"]
    if rows is None:
        b = get(URL, base + lo, base + hi - 1)
        FETCHED.append({"tensor": name, "data_offsets": [lo, hi], "bytes": hi - lo,
                        "sha256": hashlib.sha256(b).hexdigest()})
        return np.frombuffer(b, dtype="<f2").reshape(shape).astype(np.float32)
    rb = shape[1] * 2
    out = []
    for r in rows:
        b = get(URL, base + lo + r * rb, base + lo + (r + 1) * rb - 1)
        FETCHED.append({"tensor": name, "row": int(r), "bytes": rb, "sha256": hashlib.sha256(b).hexdigest()})
        out.append(np.frombuffer(b, dtype="<f2").astype(np.float32))
    return np.stack(out)


def tokens():
    tj = json.loads(get(TOK_URL))
    vocab = tj["model"]["vocab"]
    pieces, out, first = [], [], True
    import re
    for m in re.finditer(r"[A-Za-z]+|[,]", TEXT):
        w = m.group(0)
        sp = (m.start() > 0 and TEXT[m.start() - 1] == " ")
        s = ("Ġ" + w) if sp else w
        while s:                                         # greedy longest match over the vocabulary (not BPE merges)
            for n in range(len(s), 0, -1):
                if s[:n] in vocab:
                    break
            else:
                raise SystemExit(f"no vocab piece for {s!r}")
            pieces.append(s[:n])
            out.append(int(vocab[s[:n]]))
            s = s[n:]
        if len(out) >= T:
            break
    out, pieces = out[:T], pieces[:T]
    assert len(out) == T, (len(out), pieces)
    return out, pieces, hashlib.sha256(get(TOK_URL)).hexdigest()


def layernorm(x, w, b, eps=1e-5):
    x = x.astype(np.float32)
    mu = x.mean(-1, keepdims=True)
    var = ((x - mu) ** 2).mean(-1, keepdims=True)
    return ((x - mu) / np.sqrt(var + np.float32(eps)) * w + b).astype(np.float32)


def gelu(x):
    erf = np.vectorize(math.erf)
    return (0.5 * x * (1.0 + erf(x / math.sqrt(2.0)))).astype(np.float32)


def rotary(x, pos):
    """GPT-NeoX rotary on the first ROT dims of each head: x (T, HEADS, HS)."""
    inv = 1.0 / (10000.0 ** (np.arange(0, ROT, 2, dtype=np.float64) / ROT))
    fr = np.outer(pos.astype(np.float64), inv)                 # (T, ROT/2)
    emb = np.concatenate([fr, fr], axis=-1)                    # (T, ROT)
    cos, sin = np.cos(emb)[:, None, :].astype(np.float32), np.sin(emb)[:, None, :].astype(np.float32)
    xr, xp = x[..., :ROT], x[..., ROT:]
    half = ROT // 2
    rot_half = np.concatenate([-xr[..., half:], xr[..., :half]], axis=-1)
    return np.concatenate([xr * cos + rot_half * sin, xp], axis=-1).astype(np.float32)


def main():
    os.makedirs(OUT, exist_ok=True)
    hdr, base = header()
    ids, pieces, tok_sha = tokens()
    uniq = sorted(set(ids))
    E = tensor(hdr, base, "gpt_neox.embed_in.weight", rows=uniq)
    emb = np.stack([E[uniq.index(t)] for t in ids])            # (T, 512)
    L = "gpt_neox.layers.0."
    ln1w, ln1b = tensor(hdr, base, L + "input_layernorm.weight"), tensor(hdr, base, L + "input_layernorm.bias")
    ln2w = tensor(hdr, base, L + "post_attention_layernorm.weight")
    ln2b = tensor(hdr, base, L + "post_attention_layernorm.bias")
    Wqkv, bqkv = tensor(hdr, base, L + "attention.query_key_value.weight"), tensor(hdr, base, L + "attention.query_key_value.bias")
    Wup, bup = tensor(hdr, base, L + "mlp.dense_h_to_4h.weight"), tensor(hdr, base, L + "mlp.dense_h_to_4h.bias")
    Wdn = tensor(hdr, base, L + "mlp.dense_4h_to_h.weight")

    x1 = layernorm(emb, ln1w, ln1b)                            # (T, 512) the attention's input
    qkv = (x1 @ Wqkv.T + bqkv).astype(np.float32).reshape(T, HEADS, 3 * HS)
    pos = np.arange(T)
    q = rotary(qkv[..., :HS], pos)
    k = rotary(qkv[..., HS:2 * HS], pos)
    v = qkv[..., 2 * HS:]
    x2 = layernorm(emb, ln2w, ln2b)                            # (T, 512) the MLP's input (parallel residual)
    hpre = (x2 @ Wup.T + bup).astype(np.float32)               # (T, 2048)
    hg = gelu(hpre)                                            # (T, 2048) post-GELU

    H = 2                                                      # the attention head used for Q, K, P, V
    s = (q[:, H, :] @ k[:, H, :].T / np.float32(math.sqrt(HS))).astype(np.float32)   # (T, T) scores
    mask = np.triu(np.ones((T, T), bool), 1)
    s_m = np.where(mask, -np.inf, s)
    p = np.exp(s_m - s_m.max(-1, keepdims=True))
    p = (p / p.sum(-1, keepdims=True)).astype(np.float32)      # causal softmax, exact zeros above the diagonal

    R = slice(16, 32)                                          # the query / token rows of every A cut
    cuts = {
        # fp32
        "ln1_t16_d0_16x16": (x1[R, 0:16], "input_layernorm(embed) of tokens 16-31, dims 0-15"),
        "wq_h3_r192_c0_16x16T": (Wqkv[3 * 192:3 * 192 + 16, 0:16].T, "query_key_value.weight rows 576-591 (head 3's query dims 0-15), input dims 0-15, transposed"),
        "gelu_t16_u1024_16x16": (hg[R, 1024:1040], "post-GELU of dense_h_to_4h, tokens 16-31, hidden units 1024-1039"),
        "wdn_r0_c1024_16x16T": (Wdn[0:16, 1024:1040].T, "dense_4h_to_h.weight rows 0-15 (outputs), hidden units 1024-1039, transposed"),
        # fp16
        "q_h2_t16_d0_16x32": (q[R, H, 0:32], "rotary queries of head 2, tokens 16-31, head dims 0-31"),
        "k_h2_t0_d0_32x16": (k[0:16, H, 0:32].T, "rotary keys of head 2, tokens 0-15, head dims 0-31, transposed (K^T)"),
        "p_h2_t16_k0_16x32": (p[R, 0:32], "causal softmax of head 2, query tokens 16-31, key tokens 0-31"),
        "v_h2_k0_d0_32x16": (v[0:32, H, 0:16], "values of head 2, key tokens 0-31, head dims 0-15"),
        "ln2_t16_d32_16x32": (x2[R, 32:64], "post_attention_layernorm(embed) of tokens 16-31, dims 32-63"),
        "wup_r512_c32_32x16T": (Wup[512:528, 32:64].T, "dense_h_to_4h.weight rows 512-527 (hidden units), input dims 32-63, transposed"),
        # int8 sources (float32; make_blind5 quantises with the scales below)
        "ln2_t16_d64_16x64": (x2[R, 64:128], "post_attention_layernorm(embed) of tokens 16-31, dims 64-127"),
        "wup_r768_c64_64x16T": (Wup[768:784, 64:128].T, "dense_h_to_4h.weight rows 768-783, input dims 64-127, transposed"),
        "gelu_t16_u1536_16x64": (hg[R, 1536:1600], "post-GELU, tokens 16-31, hidden units 1536-1599"),
        "wdn_r128_c1536_64x16T": (Wdn[128:144, 1536:1600].T, "dense_4h_to_h.weight rows 128-143, hidden units 1536-1599, transposed"),
    }
    scales = {
        # per-token (dynamic) activation scale: max abs over the token's WHOLE row; per-output-channel weight scale:
        # max abs over the channel's WHOLE input row. Both / 127 in make_blind5.
        "ln2_t16_d64_16x64": {"per_row_max_abs": [float(v) for v in np.abs(x2[R]).max(-1)], "over": "all 512 dims of each token"},
        "gelu_t16_u1536_16x64": {"per_row_max_abs": [float(v) for v in np.abs(hg[R]).max(-1)], "over": "all 2048 hidden units of each token"},
        "wup_r768_c64_64x16T": {"per_col_max_abs": [float(v) for v in np.abs(Wup[768:784]).max(-1)], "over": "all 512 inputs of each output channel"},
        "wdn_r128_c1536_64x16T": {"per_col_max_abs": [float(v) for v in np.abs(Wdn[128:144]).max(-1)], "over": "all 2048 inputs of each output channel"},
    }
    prov = {"model": REPO, "revision": REV, "file": "model.safetensors", "dtype": "F16",
            "tokenizer": {"file": "tokenizer.json", "sha256": tok_sha},
            "text": TEXT, "text_source": "Charles Dickens, A Tale of Two Cities (1859), opening sentence; public domain",
            "tokens": ids, "pieces": pieces,
            "forward": "layer 0 of GPT-NeoX as pythia-70m configures it, in float32 from the fp16 weights: "
                       "input_layernorm -> query_key_value (+bias) -> rotary on dims 0-15 of each head (base 10000) -> "
                       "scores q.k/8 -> causal softmax; post_attention_layernorm -> dense_h_to_4h (+bias) -> exact GELU",
            "head": H, "fetched": FETCHED, "cuts": {}, "scales": scales,
            "checks": {"softmax_row_sums_max_err": float(np.abs(p.sum(-1) - 1).max()),
                       "ln1_row_mean_abs_max": float(np.abs((x1 - ln1b).mean(-1)).max())}}
    for name, (arr, what) in cuts.items():
        a = np.ascontiguousarray(arr, dtype=np.float32)
        fn = os.path.join(OUT, f"{name}.npy")
        np.save(fn, a)
        prov["cuts"][name] = {"what": what, "shape": list(a.shape), "sha256": hashlib.sha256(open(fn, "rb").read()).hexdigest(),
                              "min": float(a.min()), "max": float(a.max()), "exact_zeros": int((a == 0).sum())}
    with open(os.path.join(OUT, "provenance.json"), "w") as f:
        json.dump(prov, f, indent=1)
        f.write("\n")
    print("tokens", ids)
    print("pieces", pieces)
    print("fetched", sum(x["bytes"] for x in FETCHED), "bytes in", len(FETCHED), "requests")
    for n, c in prov["cuts"].items():
        print(f"{n:28s} {c['shape']} min {c['min']:.4g} max {c['max']:.4g} zeros {c['exact_zeros']}")
    print(prov["checks"])


if __name__ == "__main__":
    sys.exit(main())
