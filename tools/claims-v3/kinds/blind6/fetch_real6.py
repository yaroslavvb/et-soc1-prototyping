#!/usr/bin/env python3
"""Q139(b) blind pool 6: fetch layer 0 of two public W8A8 checkpoints and run it on a public-domain text, writing small
float32 cuts to real/ and their provenance to real/provenance.json.

    python3 fetch_real6.py            # needs network (huggingface.co); numpy only; about 19 MB fetched

The two checkpoints store int8 weights with one scale per output channel and quantise activations per token at run
time ("int-quantized", compressed-tensors; config.json's quantization_config: weights int8 symmetric, strategy
channel; input_activations int8 symmetric, dynamic, strategy token). So their linear layers ARE W8A8 matmuls, and the
int8 tiles cut here are the operands such a kernel multiplies: the checkpoint's own int8 weight rows, and the
activations quantised per token the way the scheme says (scale = the token's max abs over its whole row / 127).

- RedHatAI/SmolLM-135M-Instruct-quantized.w8a8 (Llama: hidden 576, 9 heads of 64, 3 KV heads, RMSNorm eps 1e-5,
  rotary base 1e4 over the whole head, SiLU-gated MLP of 1536);
- RedHatAI/Qwen2.5-0.5B-quantized.w8a8 (Qwen2: hidden 896, 14 heads of 64, 2 KV heads, q/k/v biases, RMSNorm eps 1e-6,
  rotary base 1e6, SiLU-gated MLP of 4864).

Only the safetensors header, the layer-0 tensors and the embedding rows of the text's tokens are fetched (HTTP range
requests at pinned commits). Layer 0 runs in float32: RMSNorm, the W8A8 q/k/v projections (int8 x int8 summed exactly,
then times the token's and the channel's scales, plus Qwen's bias), rotary, causal softmax attention with grouped KV
heads, the W8A8 o_proj and the residual, RMSNorm, the W8A8 gate and up projections, SiLU(gate) * up. make_blind6.py
reads only real/, never the network. Downloaded bytes are parsed as JSON (the header) and raw little-endian arrays only.
"""
import hashlib
import json
import math
import os
import re
import struct
import sys
import urllib.request

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "real")
UA = {"User-Agent": "q139b-pool6/1.0"}
# Jane Austen, Pride and Prejudice (1813), its opening; public domain.
TEXT = ("It is a truth universally acknowledged, that a single man in possession of a good fortune, must be in want "
        "of a wife. However little known the feelings or views of such a man may be on his first entering a "
        "neighbourhood, this truth is so well fixed in the minds of the surrounding families")
T = 32
MODELS = {
    "smol": {"repo": "RedHatAI/SmolLM-135M-Instruct-quantized.w8a8", "rev": "203f247e5fdd358199df1cecd839a5b8fe5c9473",
             "hid": 576, "heads": 9, "kv": 3, "hs": 64, "ff": 1536, "eps": 1e-5, "theta": 1e4, "bias": False},
    "qwen": {"repo": "RedHatAI/Qwen2.5-0.5B-quantized.w8a8", "rev": "0d1951533baeec89dd257df86d4d10c3bd5429f5",
             "hid": 896, "heads": 14, "kv": 2, "hs": 64, "ff": 4864, "eps": 1e-6, "theta": 1e6, "bias": True},
}


def get(url, lo=None, hi=None):
    h = dict(UA)
    if lo is not None:
        h["Range"] = f"bytes={lo}-{hi}"
    with urllib.request.urlopen(urllib.request.Request(url, headers=h), timeout=120) as r:
        b = r.read()
    if lo is not None:
        assert len(b) == hi - lo + 1, (url, lo, hi, len(b))
    return b


class ST:
    """A remote safetensors file read by ranges."""
    def __init__(self, url):
        self.url = url
        n = struct.unpack("<Q", get(url, 0, 7))[0]
        self.hdr = json.loads(get(url, 8, 8 + n - 1))
        self.base = 8 + n
        self.fetched = []

    def _conv(self, b, dtype, shape):
        if dtype == "BF16":
            u = np.frombuffer(b, dtype="<u2").astype(np.uint32) << np.uint32(16)
            return u.view(np.float32).reshape(shape).copy()
        if dtype == "I8":
            return np.frombuffer(b, dtype=np.int8).reshape(shape).astype(np.int64)
        if dtype == "F16":
            return np.frombuffer(b, dtype="<f2").reshape(shape).astype(np.float32)
        if dtype == "F32":
            return np.frombuffer(b, dtype="<f4").reshape(shape).copy()
        raise SystemExit(f"dtype {dtype}")

    def tensor(self, name):
        t = self.hdr[name]
        lo, hi = t["data_offsets"]
        b = get(self.url, self.base + lo, self.base + hi - 1)
        self.fetched.append({"tensor": name, "dtype": t["dtype"], "shape": t["shape"], "data_offsets": [lo, hi],
                             "bytes": hi - lo, "sha256": hashlib.sha256(b).hexdigest()})
        return self._conv(b, t["dtype"], t["shape"])

    def rows(self, name, rows):
        t = self.hdr[name]
        lo, hi = t["data_offsets"]
        esz = {"BF16": 2, "F16": 2, "F32": 4, "I8": 1}[t["dtype"]]
        rb = t["shape"][1] * esz
        out = []
        for r in rows:
            b = get(self.url, self.base + lo + r * rb, self.base + lo + (r + 1) * rb - 1)
            self.fetched.append({"tensor": name, "row": int(r), "bytes": rb, "sha256": hashlib.sha256(b).hexdigest()})
            out.append(self._conv(b, t["dtype"], [t["shape"][1]]))
        return np.stack(out)


def tokens(tok_url):
    raw = get(tok_url)
    vocab = json.loads(raw)["model"]["vocab"]
    pieces, out = [], []
    for m in re.finditer(r"[A-Za-z]+|[,.]", TEXT):
        w = m.group(0)
        sp = (m.start() > 0 and TEXT[m.start() - 1] == " ")
        s = ("Ġ" + w) if sp else w
        while s:                                       # greedy longest match over the vocabulary (not the BPE merges)
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
    assert len(out) >= T, (len(out), pieces)
    return out[:T], pieces[:T], hashlib.sha256(raw).hexdigest()


def rmsnorm(x, w, eps):
    x = x.astype(np.float32)
    r = np.sqrt((x.astype(np.float64) ** 2).mean(-1, keepdims=True) + eps).astype(np.float32)
    return (x / r * w).astype(np.float32)


def q_tok(x):
    """Dynamic per-token symmetric int8 (scale = max abs over the token's row / 127; round half to even)."""
    s = (np.abs(x).max(-1, keepdims=True) / 127.0).astype(np.float64)
    return np.clip(np.round(x / s), -127, 127).astype(np.int64), s[:, 0]


def w8a8(x, Wq, ws, bias=None):
    xq, xs = q_tok(x)
    acc = xq @ Wq.T                                     # exact int64 sums (int32 range on the card)
    y = acc.astype(np.float64) * xs[:, None] * ws.reshape(1, -1).astype(np.float64)
    if bias is not None:
        y = y + bias.reshape(1, -1)
    return y.astype(np.float32)


def rotary(x, pos, theta):
    """Llama/Qwen2 rotate_half over the whole head: x (T, H, 64)."""
    hs = x.shape[-1]
    inv = 1.0 / (theta ** (np.arange(0, hs, 2, dtype=np.float64) / hs))
    fr = np.outer(pos.astype(np.float64), inv)
    emb = np.concatenate([fr, fr], axis=-1)
    cos, sin = np.cos(emb)[:, None, :].astype(np.float32), np.sin(emb)[:, None, :].astype(np.float32)
    half = hs // 2
    rot = np.concatenate([-x[..., half:], x[..., :half]], axis=-1)
    return (x * cos + rot * sin).astype(np.float32)


def silu(x):
    return (x / (1.0 + np.exp(-x.astype(np.float64)))).astype(np.float32)


def layer0(key):
    m = MODELS[key]
    url = f"https://huggingface.co/{m['repo']}/resolve/{m['rev']}/model.safetensors"
    st = ST(url)
    ids, pieces, tok_sha = tokens(f"https://huggingface.co/{m['repo']}/resolve/{m['rev']}/tokenizer.json")
    uniq = sorted(set(ids))
    E = st.rows("model.embed_tokens.weight", uniq)
    emb = np.stack([E[uniq.index(t)] for t in ids]).astype(np.float32)
    L = "model.layers.0."
    g = lambda n: st.tensor(L + n)
    ln1, ln2 = g("input_layernorm.weight"), g("post_attention_layernorm.weight")
    W = {p: (g(f"{p}.weight"), g(f"{p}.weight_scale")) for p in
         ["self_attn.q_proj", "self_attn.k_proj", "self_attn.v_proj", "self_attn.o_proj",
          "mlp.gate_proj", "mlp.up_proj", "mlp.down_proj"]}
    bias = {p: (g(f"self_attn.{p}.bias") if m["bias"] else None) for p in ["q_proj", "k_proj", "v_proj"]}
    H, KV, HS = m["heads"], m["kv"], m["hs"]
    x1 = rmsnorm(emb, ln1, m["eps"])
    q = w8a8(x1, *W["self_attn.q_proj"], bias["q_proj"]).reshape(T, H, HS)
    k = w8a8(x1, *W["self_attn.k_proj"], bias["k_proj"]).reshape(T, KV, HS)
    v = w8a8(x1, *W["self_attn.v_proj"], bias["v_proj"]).reshape(T, KV, HS)
    pos = np.arange(T)
    qr, kr = rotary(q, pos, m["theta"]), rotary(k, pos, m["theta"])
    grp = H // KV
    mask = np.triu(np.ones((T, T), bool), 1)
    P = np.empty((H, T, T), np.float32)
    att = np.empty((T, H, HS), np.float32)
    for h in range(H):
        s = (qr[:, h, :] @ kr[:, h // grp, :].T / np.float32(math.sqrt(HS))).astype(np.float32)
        s = np.where(mask, -np.inf, s)
        p = np.exp(s - s.max(-1, keepdims=True))
        p = (p / p.sum(-1, keepdims=True)).astype(np.float32)
        P[h] = p
        att[:, h, :] = p @ v[:, h // grp, :]
    o = w8a8(att.reshape(T, H * HS), *W["self_attn.o_proj"])
    hres = (emb + o).astype(np.float32)
    x2 = rmsnorm(hres, ln2, m["eps"])
    gate = w8a8(x2, *W["mlp.gate_proj"])
    up = w8a8(x2, *W["mlp.up_proj"])
    act = (silu(gate) * up).astype(np.float32)
    return {"m": m, "st": st, "ids": ids, "pieces": pieces, "tok_sha": tok_sha, "x1": x1, "x2": x2, "q": qr, "k": kr,
            "v": v, "P": P, "act": act, "W": W, "grp": grp}


def main():
    os.makedirs(OUT, exist_ok=True)
    S, Q = layer0("smol"), layer0("qwen")
    R = slice(16, 32)
    hS, hQ = 1, 3                                                   # the heads used (KV heads hS//3 = 0, hQ//7 = 0)
    kS, kQ = hS // S["grp"], hQ // Q["grp"]

    def wint(M, name, rows, cols):                                  # int8 weight rows (output channels) x input cols, transposed
        return M["W"][name][0][rows, cols].T.astype(np.float32)

    def wscale(M, name, rows):
        return M["W"][name][1].reshape(-1)[rows].astype(np.float32)

    def deq(M, name, rows, cols):                                   # int8 x per-channel scale, exact in float32
        return (M["W"][name][0][rows, cols].astype(np.float32) * wscale(M, name, rows)[:, None]).T.astype(np.float32)

    c16, c64, r16 = slice(0, 16), slice(0, 64), slice(0, 16)
    cuts = {
        # ---- int8 (W8A8): A = float activations (quantised per token by make_blind6 with the row maxima below),
        #      B = the checkpoint's int8 weights (exact integers)
        "smol_ln1_t16_d0_16x64": (S["x1"][R, c64], "SmolLM-135M layer 0: input_layernorm(embed) of tokens 16-31, dims 0-63"),
        "smol_wq8_r0_c0_64x16T": (wint(S, "self_attn.q_proj", r16, c64), "SmolLM-135M layer 0: q_proj int8 weight rows 0-15 (head 0, dims 0-15) x input dims 0-63, transposed"),
        "smol_act_t16_u0_16x64": (S["act"][R, c64], "SmolLM-135M layer 0: SiLU(gate) * up, tokens 16-31, hidden units 0-63 (the down projection's input)"),
        "smol_wdn8_r0_c0_64x16T": (wint(S, "mlp.down_proj", r16, c64), "SmolLM-135M layer 0: down_proj int8 weight rows 0-15 x hidden units 0-63, transposed"),
        "qwen_ln1_t16_d0_16x64": (Q["x1"][R, c64], "Qwen2.5-0.5B layer 0: input_layernorm(embed) of tokens 16-31, dims 0-63"),
        "qwen_wv8_r0_c0_64x16T": (wint(Q, "self_attn.v_proj", r16, c64), "Qwen2.5-0.5B layer 0: v_proj int8 weight rows 0-15 (KV head 0, dims 0-15) x input dims 0-63, transposed"),
        "qwen_ln2_t16_d64_16x64": (Q["x2"][R, slice(64, 128)], "Qwen2.5-0.5B layer 0: post_attention_layernorm of tokens 16-31 (after attention and the residual), dims 64-127"),
        "qwen_wg8_r0_c64_64x16T": (wint(Q, "mlp.gate_proj", r16, slice(64, 128)), "Qwen2.5-0.5B layer 0: gate_proj int8 weight rows 0-15 x input dims 64-127, transposed"),
        "qwen_act_t16_u0_16x64": (Q["act"][R, c64], "Qwen2.5-0.5B layer 0: SiLU(gate) * up, tokens 16-31, hidden units 0-63"),
        "qwen_wdn8_r0_c0_64x16T": (wint(Q, "mlp.down_proj", r16, c64), "Qwen2.5-0.5B layer 0: down_proj int8 weight rows 0-15 x hidden units 0-63, transposed"),
        # ---- fp16 attention matmuls and a dequantised projection (rounded to fp16 by make_blind6)
        "smol_q_h1_t16_d0_16x32": (S["q"][R, hS, 0:32], "SmolLM-135M layer 0, head 1: rotary queries, tokens 16-31, head dims 0-31"),
        "smol_k_kv0_t0_d0_32x16": (S["k"][0:16, kS, 0:32].T, "SmolLM-135M layer 0, KV head 0: rotary keys of tokens 0-15, head dims 0-31, transposed (K^T)"),
        "smol_p_h1_t16_k0_16x32": (S["P"][hS][R, 0:32], "SmolLM-135M layer 0, head 1: causal softmax, query tokens 16-31 x key tokens 0-31"),
        "smol_v_kv0_k0_d0_32x16": (S["v"][0:32, kS, 0:16], "SmolLM-135M layer 0, KV head 0: values of key tokens 0-31, head dims 0-15"),
        "qwen_q_h3_t16_d0_16x32": (Q["q"][R, hQ, 0:32], "Qwen2.5-0.5B layer 0, head 3: rotary queries (with q_proj's bias), tokens 16-31, head dims 0-31"),
        "qwen_k_kv0_t0_d0_32x16": (Q["k"][0:16, kQ, 0:32].T, "Qwen2.5-0.5B layer 0, KV head 0: rotary keys (with k_proj's bias) of tokens 0-15, head dims 0-31, transposed"),
        "qwen_ln1_t16_d0_16x32": (Q["x1"][R, 0:32], "Qwen2.5-0.5B layer 0: input_layernorm(embed) of tokens 16-31, dims 0-31"),
        "qwen_wvdq_r0_c0_32x16T": (deq(Q, "self_attn.v_proj", r16, slice(0, 32)), "Qwen2.5-0.5B layer 0: v_proj weight dequantised (int8 x its channel's scale) rows 0-15 x input dims 0-31, transposed"),
        # ---- fp32
        "smol_p_h1_t0_k0_16x16": (S["P"][hS][0:16, 0:16], "SmolLM-135M layer 0, head 1: causal softmax, query tokens 0-15 x key tokens 0-15 (the diagonal block: exact zeros above the diagonal)"),
        "smol_v_kv0_k0_d0_16x16": (S["v"][0:16, kS, 0:16], "SmolLM-135M layer 0, KV head 0: values of key tokens 0-15, head dims 0-15"),
        "qwen_ln1_t16_d0_16x16": (Q["x1"][R, c16], "Qwen2.5-0.5B layer 0: input_layernorm(embed) of tokens 16-31, dims 0-15"),
        "qwen_wqdq_r0_c0_16x16T": (deq(Q, "self_attn.q_proj", r16, c16), "Qwen2.5-0.5B layer 0: q_proj weight dequantised (int8 x its channel's bf16 scale, exact in fp32) rows 0-15 x input dims 0-15, transposed"),
        "qwen_p_h3_t16_k0_16x16": (Q["P"][hQ][R, 0:16], "Qwen2.5-0.5B layer 0, head 3: softmax, query tokens 16-31 x key tokens 0-15 (every key precedes the query: no masked zeros)"),
        "qwen_v_kv0_k0_d0_16x16": (Q["v"][0:16, kQ, 0:16], "Qwen2.5-0.5B layer 0, KV head 0: values of key tokens 0-15, head dims 0-15"),
    }
    scales = {
        "smol_ln1_t16_d0_16x64": {"per_row_max_abs": [float(v) for v in np.abs(S["x1"][R]).max(-1)], "over": "all 576 dims of each token"},
        "smol_act_t16_u0_16x64": {"per_row_max_abs": [float(v) for v in np.abs(S["act"][R]).max(-1)], "over": "all 1536 hidden units of each token"},
        "qwen_ln1_t16_d0_16x64": {"per_row_max_abs": [float(v) for v in np.abs(Q["x1"][R]).max(-1)], "over": "all 896 dims of each token"},
        "qwen_ln2_t16_d64_16x64": {"per_row_max_abs": [float(v) for v in np.abs(Q["x2"][R]).max(-1)], "over": "all 896 dims of each token"},
        "qwen_act_t16_u0_16x64": {"per_row_max_abs": [float(v) for v in np.abs(Q["act"][R]).max(-1)], "over": "all 4864 hidden units of each token"},
    }
    prov = {"text": TEXT, "text_source": "Jane Austen, Pride and Prejudice (1813), opening; public domain",
            "tokens_kept": T, "tokenizer_note": "greedy longest match over each model's tokenizer.json vocabulary ('Ġ' = a leading space), not the BPE merges",
            "models": {}, "cuts": {}, "scales": scales,
            "quantisation": "activations: q = clip(round_half_even(x / s), -127, 127), s = the token's max abs over its whole row / 127 "
                            "(the checkpoints' dynamic per-token symmetric int8); weights: the checkpoints' own int8 values",
            "forward": "layer 0 in float32: RMSNorm -> W8A8 q/k/v (int8 x int8 exact, x token scale x channel scale, + bias for Qwen) "
                       "-> rotary (rotate_half over 64 dims) -> scores q.k/8 with grouped KV heads -> causal softmax -> P V -> W8A8 o_proj "
                       "-> residual -> RMSNorm -> W8A8 gate, up -> SiLU(gate) * up"}
    for key, M in (("smol", S), ("qwen", Q)):
        m = M["m"]
        prov["models"][key] = {"repo": m["repo"], "revision": m["rev"], "file": "model.safetensors", "license_note": "see the model card",
                               "config": {k: m[k] for k in ("hid", "heads", "kv", "hs", "ff", "eps", "theta", "bias")},
                               "tokenizer_sha256": M["tok_sha"], "tokens": M["ids"], "pieces": M["pieces"],
                               "fetched": M["st"].fetched, "fetched_bytes": int(sum(f["bytes"] for f in M["st"].fetched)),
                               "checks": {"softmax_row_sums_max_err": float(np.abs(M["P"].sum(-1) - 1).max()),
                                          "head_used": hS if key == "smol" else hQ}}
    for name, (arr, what) in cuts.items():
        a = np.ascontiguousarray(arr, dtype=np.float32)
        assert np.isfinite(a).all(), name
        fn = os.path.join(OUT, f"{name}.npy")
        np.save(fn, a)
        prov["cuts"][name] = {"what": what, "shape": list(a.shape), "sha256": hashlib.sha256(open(fn, "rb").read()).hexdigest(),
                              "min": float(a.min()), "max": float(a.max()), "exact_zeros": int((a == 0).sum())}
    with open(os.path.join(OUT, "provenance.json"), "w") as f:
        json.dump(prov, f, indent=1)
        f.write("\n")
    for key in prov["models"]:
        mm = prov["models"][key]
        print(key, mm["repo"], mm["revision"][:12], "fetched", mm["fetched_bytes"], "bytes in", len(mm["fetched"]), "requests")
        print("  pieces", mm["pieces"])
    for n, c in prov["cuts"].items():
        print(f"{n:28s} {c['shape']} min {c['min']:.4g} max {c['max']:.4g} zeros {c['exact_zeros']}")


if __name__ == "__main__":
    sys.exit(main())
