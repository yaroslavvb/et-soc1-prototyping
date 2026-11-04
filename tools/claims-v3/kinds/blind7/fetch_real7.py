#!/usr/bin/env python3
"""Q140(b) blind pool 7: run the first layers of three public W8A8 checkpoints on a public-domain text and write small
float32 cuts to real/, with their provenance (model, licence, revision, layer, cut, outlier statistics) in
real/provenance.json.

    python3 fetch_real7.py                 # needs network (huggingface.co); numpy only; writes real/
    python3 fetch_real7.py --explore       # prints, per model and layer, where the activations' outliers are
    python3 fetch_real7.py --cache DIR     # keep fetched byte ranges in DIR (raw bytes only), re-use them later

The three checkpoints store int8 weights with one scale per output channel and quantise activations per token at run
time ("int-quantized", compressed-tensors; config.json's quantization_config: weights int8 symmetric, strategy
channel; input_activations int8 symmetric, dynamic, strategy token). So their linear layers ARE W8A8 matmuls, and the
int8 tiles cut here are the operands such a kernel multiplies: the checkpoint's own int8 weight rows, and the
activations quantised per token the way the scheme says (scale = the token's max abs over its whole row / 127).

- RedHatAI/Qwen2.5-0.5B-quantized.w8a8 (Qwen2: hidden 896, 14 heads of 64, 2 KV heads, q/k/v biases, RMSNorm eps
  1e-6, rotary base 1e6, SiLU-gated MLP of 4864; Apache-2.0), blind pool 6's second model, here past layer 0;
- RedHatAI/SmolLM-135M-Instruct-quantized.w8a8 (Llama: hidden 576, 9 heads, 3 KV heads, eps 1e-5, base 1e4, MLP 1536;
  Apache-2.0), blind pool 6's first model, here past layer 0;
- RedHatAI/SmolLM-360M-Instruct-quantized.w8a8 (Llama: hidden 960, 15 heads, 5 KV heads, eps 1e-5, base 1e4, MLP
  2560; Apache-2.0), a model no pool has used.

Text: the opening of Lewis Carroll, Alice's Adventures in Wonderland (1865), public domain, tokenised by each model's
own byte-level BPE (its tokenizer.json: the pre-tokenizer's split, GPT-2's byte-to-unicode map, the merges by rank;
no special token added). Pool 6 used greedy longest match; this file applies the merges. Only the safetensors header,
the tensors of the layers run and the embedding rows of the text's tokens are fetched, by HTTP range requests at
pinned commits. Downloaded bytes are parsed as JSON (the header, tokenizer.json) and raw little-endian arrays only.
make_blind7.py reads only real/, never the network.
"""
import argparse
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
UA = {"User-Agent": "q140b-pool7/1.0"}
CACHE = None
# Lewis Carroll, Alice's Adventures in Wonderland (1865), the opening of chapter 1; public domain. ASCII only.
TEXT = ("Alice was beginning to get very tired of sitting by her sister on the bank, and of having nothing to do: once "
        "or twice she had peeped into the book her sister was reading, but it had no pictures or conversations in it")
T = 32
MODELS = {
    "qwen": {"repo": "RedHatAI/Qwen2.5-0.5B-quantized.w8a8", "rev": "0d1951533baeec89dd257df86d4d10c3bd5429f5",
             "license": "apache-2.0", "base": "Qwen/Qwen2.5-0.5B", "split": "qwen2",
             "hid": 896, "heads": 14, "kv": 2, "hs": 64, "ff": 4864, "eps": 1e-6, "theta": 1e6, "bias": True, "layers": 4},
    "smol": {"repo": "RedHatAI/SmolLM-135M-Instruct-quantized.w8a8", "rev": "203f247e5fdd358199df1cecd839a5b8fe5c9473",
             "license": "apache-2.0", "base": "HuggingFaceTB/SmolLM-135M-Instruct", "split": "gpt2",
             "hid": 576, "heads": 9, "kv": 3, "hs": 64, "ff": 1536, "eps": 1e-5, "theta": 1e4, "bias": False, "layers": 4},
    "s360": {"repo": "RedHatAI/SmolLM-360M-Instruct-quantized.w8a8", "rev": "4477e7ff83e89ab2310ebfb589af52b356dec848",
             "license": "apache-2.0", "base": "HuggingFaceTB/SmolLM-360M-Instruct", "split": "gpt2",
             "hid": 960, "heads": 15, "kv": 5, "hs": 64, "ff": 2560, "eps": 1e-5, "theta": 1e4, "bias": False, "layers": 4},
}


def get(url, lo=None, hi=None):
    key = None
    if CACHE:
        key = os.path.join(CACHE, hashlib.sha256(f"{url}|{lo}|{hi}".encode()).hexdigest())
        if os.path.exists(key):
            with open(key, "rb") as f:
                return f.read()
    h = dict(UA)
    if lo is not None:
        h["Range"] = f"bytes={lo}-{hi}"
    with urllib.request.urlopen(urllib.request.Request(url, headers=h), timeout=180) as r:
        b = r.read()
    if lo is not None:
        assert len(b) == hi - lo + 1, (url, lo, hi, len(b))
    if key:
        with open(key + ".tmp", "wb") as f:
            f.write(b)
        os.replace(key + ".tmp", key)
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


# ---------------------------------------------------------------- byte-level BPE (GPT-2's scheme), ASCII text only
def bytes_to_unicode():
    bs = list(range(ord("!"), ord("~") + 1)) + list(range(ord("\xa1"), ord("\xac") + 1)) + list(range(ord("\xae"), ord("\xff") + 1))
    cs = bs[:]
    n = 0
    for b in range(256):
        if b not in bs:
            bs.append(b)
            cs.append(256 + n)
            n += 1
    return dict(zip(bs, [chr(c) for c in cs]))


# The two pre-tokenizer splits, with \p{L} -> [A-Za-z] and \p{N} -> [0-9]: exact on ASCII text, which TEXT is.
SPLIT = {
    # Qwen2's Split regex (tokenizer.json pre_tokenizer.pretokenizers[0].pattern.Regex)
    "qwen2": r"(?i:'s|'t|'re|'ve|'m|'ll|'d)|[^\r\nA-Za-z0-9]?[A-Za-z]+|[0-9]| ?[^\sA-Za-z0-9]+[\r\n]*|\s*[\r\n]+|\s+(?!\S)|\s+",
    # SmolLM: Digits(individual) then ByteLevel(use_regex): GPT-2's pattern (digits split one by one first)
    "gpt2": r"'s|'t|'re|'ve|'m|'ll|'d| ?[A-Za-z]+| ?[0-9]| ?[^\sA-Za-z0-9]+|\s+(?!\S)|\s+",
}


def bpe_tokens(tok_json, split):
    assert all(ord(c) < 128 for c in TEXT)
    vocab = tok_json["model"]["vocab"]
    merges = tok_json["model"]["merges"]
    rank = {}
    for r, m in enumerate(merges):
        a, b = (m.split(" ", 1) if isinstance(m, str) else m)
        rank[(a, b)] = r
    b2u = bytes_to_unicode()
    ids, pieces = [], []
    for pre in re.findall(SPLIT[split], TEXT):
        word = [b2u[b] for b in pre.encode("utf-8")]
        while len(word) > 1:
            best = min(((rank.get((word[i], word[i + 1]), None), i) for i in range(len(word) - 1)),
                       key=lambda x: (x[0] is None, x[0] if x[0] is not None else 0, x[1]))
            if best[0] is None:
                break
            r = best[0]
            out, i = [], 0
            while i < len(word):                      # merge every occurrence of the best pair, left to right
                if i < len(word) - 1 and rank.get((word[i], word[i + 1])) == r:
                    out.append(word[i] + word[i + 1])
                    i += 2
                else:
                    out.append(word[i])
                    i += 1
            word = out
        for w in word:
            pieces.append(w)
            ids.append(int(vocab[w]))
        if len(ids) >= T:
            break
    assert len(ids) >= T, (len(ids), pieces)
    return ids[:T], pieces[:T]


# ---------------------------------------------------------------- the forward pass (float32, W8A8 linears)
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


LINEARS = ["self_attn.q_proj", "self_attn.k_proj", "self_attn.v_proj", "self_attn.o_proj",
           "mlp.gate_proj", "mlp.up_proj", "mlp.down_proj"]


def forward(key, n_layers):
    m = MODELS[key]
    url = f"https://huggingface.co/{m['repo']}/resolve/{m['rev']}/model.safetensors"
    st = ST(url)
    traw = get(f"https://huggingface.co/{m['repo']}/resolve/{m['rev']}/tokenizer.json")
    ids, pieces = bpe_tokens(json.loads(traw), m["split"])
    uniq = sorted(set(ids))
    E = st.rows("model.embed_tokens.weight", uniq)
    h = np.stack([E[uniq.index(t)] for t in ids]).astype(np.float32)
    H, KV, HS = m["heads"], m["kv"], m["hs"]
    grp = H // KV
    pos = np.arange(T)
    mask = np.triu(np.ones((T, T), bool), 1)
    layers = []
    for li in range(n_layers):
        L = f"model.layers.{li}."
        g = lambda n: st.tensor(L + n)                                   # noqa: E731
        ln1, ln2 = g("input_layernorm.weight"), g("post_attention_layernorm.weight")
        W = {p: (g(f"{p}.weight"), g(f"{p}.weight_scale")) for p in LINEARS}
        bias = {p: (g(f"self_attn.{p}.bias") if m["bias"] else None) for p in ["q_proj", "k_proj", "v_proj"]}
        h_in = h
        x1 = rmsnorm(h, ln1, m["eps"])
        q = w8a8(x1, *W["self_attn.q_proj"], bias["q_proj"]).reshape(T, H, HS)
        k = w8a8(x1, *W["self_attn.k_proj"], bias["k_proj"]).reshape(T, KV, HS)
        v = w8a8(x1, *W["self_attn.v_proj"], bias["v_proj"]).reshape(T, KV, HS)
        qr, kr = rotary(q, pos, m["theta"]), rotary(k, pos, m["theta"])
        P = np.empty((H, T, T), np.float32)
        att = np.empty((T, H, HS), np.float32)
        for hh in range(H):
            s = (qr[:, hh, :] @ kr[:, hh // grp, :].T / np.float32(math.sqrt(HS))).astype(np.float32)
            s = np.where(mask, -np.inf, s)
            p = np.exp(s - s.max(-1, keepdims=True))
            p = (p / p.sum(-1, keepdims=True)).astype(np.float32)
            P[hh] = p
            att[:, hh, :] = p @ v[:, hh // grp, :]
        attf = att.reshape(T, H * HS)
        o = w8a8(attf, *W["self_attn.o_proj"])
        hmid = (h + o).astype(np.float32)
        x2 = rmsnorm(hmid, ln2, m["eps"])
        gate = w8a8(x2, *W["mlp.gate_proj"])
        up = w8a8(x2, *W["mlp.up_proj"])
        act = (silu(gate) * up).astype(np.float32)
        dn = w8a8(act, *W["mlp.down_proj"])
        h = (hmid + dn).astype(np.float32)
        layers.append({"h_in": h_in, "x1": x1, "q": qr, "k": kr, "v": v, "P": P, "att": attf, "hmid": hmid, "x2": x2,
                       "act": act, "h_out": h, "W": W, "ln1": ln1, "ln2": ln2})
    return {"m": m, "st": st, "ids": ids, "pieces": pieces, "tok_sha": hashlib.sha256(traw).hexdigest(),
            "layers": layers, "grp": grp}


def outlier_stats(x):
    """Per token: max |x| over the row against the row's median |x|, the dims of the top values, and the share of the
    row's per-token int8 codes that are -1, 0 or +1 (what an outlier does to the other bytes)."""
    a = np.abs(x.astype(np.float64))
    mx = a.max(-1)
    med = np.median(a, -1)
    q, _ = q_tok(x)
    small = (np.abs(q) <= 1).mean(-1)
    return {"max_over_median": [round(float(v), 2) for v in mx / np.maximum(med, 1e-30)],
            "argmax": [int(v) for v in a.argmax(-1)], "max_abs": [round(float(v), 4) for v in mx],
            "int8_small_share": [round(float(v), 4) for v in small]}


def explore(n):
    for key in MODELS:
        M = forward(key, n)
        print("==", key, MODELS[key]["repo"], "pieces", M["pieces"])
        for li, Ly in enumerate(M["layers"]):
            for nm in ("x1", "att", "x2", "act", "h_out"):
                s = outlier_stats(Ly[nm])
                r = np.array(s["max_over_median"])
                top = np.argsort(-r)[:4]
                dims = {}
                for t in range(T):
                    dims[s["argmax"][t]] = dims.get(s["argmax"][t], 0) + 1
                common = sorted(dims.items(), key=lambda kv: -kv[1])[:4]
                print(f"  L{li} {nm:5s} ratio med {np.median(r):8.1f} max {r.max():9.1f} (tokens {list(top)}) "
                      f"maxabs {max(s['max_abs']):9.3f} argmax dims {common} int8-small med {np.median(s['int8_small_share']):.3f} "
                      f"max {max(s['int8_small_share']):.3f}")
            sink = Ly["P"][:, 8:, 0].mean()
            print(f"  L{li} P: mean attention on token 0 from queries 8-31 over heads {sink:.3f}; per head "
                  f"{[round(float(v), 2) for v in Ly['P'][:, 8:, 0].mean(-1)]}")
        print("  fetched", sum(f["bytes"] for f in M["st"].fetched), "bytes")


def block64(u, width=64):
    """The aligned block of `width` consecutive indices that holds index u."""
    s = (int(u) // width) * width
    return slice(s, s + width)


def write_cuts():
    """Run layers 0-3 of the three checkpoints and cut 24 arrays (12 tiles), each by a rule stated here (outlier dims and units are
    chosen by argmax on the data, never by hand). An --explore 4 pass located the outliers first (README, Real tiles)."""
    os.makedirs(OUT, exist_ok=True)
    Q, S, X = forward("qwen", 4), forward("smol", 4), forward("s360", 4)
    R = slice(16, 32)
    R0 = slice(0, 16)

    def wint(M, li, name, rows, cols):            # int8 weight rows (output channels) x input cols, transposed
        return M["layers"][li]["W"][name][0][rows, cols].T.astype(np.float32)

    def wsc(M, li, name, rows):
        return M["layers"][li]["W"][name][1].reshape(-1)[rows].astype(np.float32)

    def deq(M, li, name, rows, cols):             # int8 x per-channel bf16 scale, exact in float32
        return (M["layers"][li]["W"][name][0][rows, cols].astype(np.float32) * wsc(M, li, name, rows)[:, None]).T.astype(np.float32)

    Lq3, Ls2, Ls3, Lx1, Lx2, Lx3 = Q["layers"][3], S["layers"][2], S["layers"][3], X["layers"][1], X["layers"][2], X["layers"][3]
    # the outliers, by argmax on the data
    u_q3 = int(np.abs(Lq3["act"][0]).argmax())                       # Qwen L3 down_proj input: token 0's massive unit
    d_q3 = int(np.bincount(np.abs(Lq3["x1"]).argmax(-1)).argmax())  # Qwen L3 q/k/v input: the commonest argmax dim
    d_s2 = int(np.bincount(np.abs(Ls2["x2"]).argmax(-1)).argmax())  # SmolLM-135M L2 gate/up input: its outlier dim
    d_s3 = int(np.bincount(np.abs(Ls3["x1"]).argmax(-1)).argmax())  # SmolLM-135M L3 q/k/v input
    d_x3 = int(np.bincount(np.abs(Lx3["x1"]).argmax(-1)).argmax())  # SmolLM-360M L3 q/k/v input
    d_x3b = int(np.bincount(np.abs(Lx3["x2"]).argmax(-1)).argmax()) # SmolLM-360M L3 gate/up input
    sink = Lq3["P"][:, 16:32, 0].mean(-1)
    h_q3 = int(sink.argmax())                                        # Qwen L3: the head that sinks most on token 0
    kv_q3 = h_q3 // Q["grp"]
    h_q3lo = int(sink.argmin())                                      # Qwen L3: the head that sinks least (fp16's tile:
    kv_q3lo = h_q3lo // Q["grp"]                                     # the sink head's tiny weights are fp16 subnormals)
    h_x3 = 1                                                         # SmolLM-360M L3 head 1 (KV head 0), as pool 6 took head 1
    kv_x3 = h_x3 // X["grp"]
    h_x1 = 2                                                         # SmolLM-360M L1 head 2 (KV head 0)
    kv_x1 = h_x1 // X["grp"]
    c16, c32, c64, r16 = slice(0, 16), slice(0, 32), slice(0, 64), slice(0, 16)
    bq3, bs2, bx3 = block64(u_q3), block64(d_s2), block64(d_x3)
    bq3x = block64(d_q3)
    b16s3 = block64(d_s3, 16)
    b32x3 = block64(d_x3b, 32)
    cuts = {
        # ---- int8 (W8A8): A = float activations, quantised per token by make_blind7 with the row maxima below;
        #      B = the checkpoint's own int8 weights (exact integers)
        "s360_l3_x1_t16_d%d_16x64" % bx3.start: (Lx3["x1"][R, bx3], f"SmolLM-360M layer 3: input_layernorm output, tokens 16-31, dims {bx3.start}-{bx3.stop - 1} (holds the outlier dim {d_x3}, the argmax of every token)"),
        "s360_l3_wq8_r0_c%d_64x16T" % bx3.start: (wint(X, 3, "self_attn.q_proj", r16, bx3), f"SmolLM-360M layer 3: q_proj int8 weight rows 0-15 x input dims {bx3.start}-{bx3.stop - 1}, transposed"),
        "qwen_l3_act_t0_u%d_16x64" % bq3.start: (Lq3["act"][R0, bq3], f"Qwen2.5-0.5B layer 3: SiLU(gate) * up (down_proj's input), tokens 0-15, hidden units {bq3.start}-{bq3.stop - 1} (holds token 0's massive unit {u_q3})"),
        "qwen_l3_wdn8_r0_u%d_64x16T" % bq3.start: (wint(Q, 3, "mlp.down_proj", r16, bq3), f"Qwen2.5-0.5B layer 3: down_proj int8 weight rows 0-15 x hidden units {bq3.start}-{bq3.stop - 1}, transposed"),
        "smol_l2_x2_t16_d%d_16x64" % bs2.start: (Ls2["x2"][R, bs2], f"SmolLM-135M layer 2: post_attention_layernorm output, tokens 16-31, dims {bs2.start}-{bs2.stop - 1} (holds the outlier dim {d_s2})"),
        "smol_l2_wup8_r0_c%d_64x16T" % bs2.start: (wint(S, 2, "mlp.up_proj", r16, bs2), f"SmolLM-135M layer 2: up_proj int8 weight rows 0-15 x input dims {bs2.start}-{bs2.stop - 1}, transposed"),
        "qwen_l3_x1_t0_d%d_16x64" % bq3x.start: (Lq3["x1"][R0, bq3x], f"Qwen2.5-0.5B layer 3: input_layernorm output, tokens 0-15 (token 0 the attention sink), dims {bq3x.start}-{bq3x.stop - 1} (holds the outlier dim {d_q3})"),
        "qwen_l3_wk8_r0_c%d_64x16T" % bq3x.start: (wint(Q, 3, "self_attn.k_proj", r16, bq3x), f"Qwen2.5-0.5B layer 3: k_proj int8 weight rows 0-15 (KV head 0, dims 0-15) x input dims {bq3x.start}-{bq3x.stop - 1}, transposed"),
        "s360_l2_att_t16_d0_16x64": (Lx2["att"][R, c64], "SmolLM-360M layer 2: attention output (o_proj's input), tokens 16-31, dims 0-63 (head 0's output)"),
        "s360_l2_wo8_r0_c0_64x16T": (wint(X, 2, "self_attn.o_proj", r16, c64), "SmolLM-360M layer 2: o_proj int8 weight rows 0-15 x input dims 0-63, transposed"),
        "smol_l3_act_t16_u0_16x64": (Ls3["act"][R, c64], "SmolLM-135M layer 3: SiLU(gate) * up, tokens 16-31, hidden units 0-63"),
        "smol_l3_wdn8_r0_u0_64x16T": (wint(S, 3, "mlp.down_proj", r16, c64), "SmolLM-135M layer 3: down_proj int8 weight rows 0-15 x hidden units 0-63, transposed"),
        # ---- fp16 (rounded to fp16 by make_blind7)
        "qwen_l3_p_h%d_t16_k0_16x32" % h_q3lo: (Lq3["P"][h_q3lo][R, c32], f"Qwen2.5-0.5B layer 3, head {h_q3lo} (the head that puts least weight on token 0, the attention sink, in a layer whose other heads sink): causal softmax, query tokens 16-31 x key tokens 0-31"),
        "qwen_l3_v_kv%d_k0_d0_32x16" % kv_q3lo: (Lq3["v"][c32, kv_q3lo, c16], f"Qwen2.5-0.5B layer 3, KV head {kv_q3lo}: values of key tokens 0-31, head dims 0-15"),
        "s360_l3_q_h%d_t16_d0_16x32" % h_x3: (Lx3["q"][R, h_x3, c32], f"SmolLM-360M layer 3, head {h_x3}: rotary queries, tokens 16-31, head dims 0-31"),
        "s360_l3_k_kv%d_t0_d0_32x16" % kv_x3: (Lx3["k"][r16, kv_x3, c32].T, f"SmolLM-360M layer 3, KV head {kv_x3}: rotary keys of tokens 0-15, head dims 0-31, transposed (K^T)"),
        "s360_l3_x2_t16_d%d_16x32" % b32x3.start: (Lx3["x2"][R, b32x3], f"SmolLM-360M layer 3: post_attention_layernorm output, tokens 16-31, dims {b32x3.start}-{b32x3.stop - 1} (holds its outlier dim {d_x3b})"),
        "s360_l3_wgdq_r0_c%d_32x16T" % b32x3.start: (deq(X, 3, "mlp.gate_proj", r16, b32x3), f"SmolLM-360M layer 3: gate_proj weight dequantised (int8 x its channel's scale) rows 0-15 x input dims {b32x3.start}-{b32x3.stop - 1}, transposed"),
        # ---- fp32
        "qwen_l3_p_h%d_t16_k0_16x16" % h_q3: (Lq3["P"][h_q3][R, c16], f"Qwen2.5-0.5B layer 3, head {h_q3}: softmax, query tokens 16-31 x key tokens 0-15 (key 0 the sink; every key precedes the query: no masked zeros)"),
        "qwen_l3_v_kv%d_k0_d16_16x16" % kv_q3: (Lq3["v"][c16, kv_q3, slice(16, 32)], f"Qwen2.5-0.5B layer 3, KV head {kv_q3}: values of key tokens 0-15, head dims 16-31"),
        "smol_l3_x1_t16_d%d_16x16" % b16s3.start: (Ls3["x1"][R, b16s3], f"SmolLM-135M layer 3: input_layernorm output, tokens 16-31, dims {b16s3.start}-{b16s3.stop - 1} (holds the outlier dim {d_s3})"),
        "smol_l3_wqdq_r0_c%d_16x16T" % b16s3.start: (deq(S, 3, "self_attn.q_proj", r16, b16s3), f"SmolLM-135M layer 3: q_proj weight dequantised (int8 x its channel's bf16 scale, exact in fp32) rows 0-15 x input dims {b16s3.start}-{b16s3.stop - 1}, transposed"),
        "s360_l1_q_h%d_t16_d0_16x16" % h_x1: (Lx1["q"][R, h_x1, c16], f"SmolLM-360M layer 1, head {h_x1}: rotary queries, tokens 16-31, head dims 0-15"),
        "s360_l1_k_kv%d_t0_d0_16x16" % kv_x1: (Lx1["k"][r16, kv_x1, c16].T, f"SmolLM-360M layer 1, KV head {kv_x1}: rotary keys of tokens 0-15, head dims 0-15, transposed (K^T)"),
    }
    acts8 = {"s360_l3_x1_t16_d%d_16x64" % bx3.start: (Lx3["x1"][R], "all 960 dims of each token"),
             "qwen_l3_act_t0_u%d_16x64" % bq3.start: (Lq3["act"][R0], "all 4864 hidden units of each token"),
             "smol_l2_x2_t16_d%d_16x64" % bs2.start: (Ls2["x2"][R], "all 576 dims of each token"),
             "qwen_l3_x1_t0_d%d_16x64" % bq3x.start: (Lq3["x1"][R0], "all 896 dims of each token"),
             "s360_l2_att_t16_d0_16x64": (Lx2["att"][R], "all 960 dims of each token"),
             "smol_l3_act_t16_u0_16x64": (Ls3["act"][R], "all 1536 hidden units of each token")}
    scales = {}
    for n, (full, over) in acts8.items():
        st = outlier_stats(full)
        scales[n] = {"per_row_max_abs": [float(v) for v in np.abs(full).max(-1)], "over": over,
                     "row_max_over_median": st["max_over_median"], "row_argmax": st["argmax"],
                     "row_int8_small_share": st["int8_small_share"]}
    picks = {"qwen_l3_down_massive_unit": u_q3, "qwen_l3_x1_outlier_dim": d_q3, "smol_l2_x2_outlier_dim": d_s2,
             "smol_l3_x1_outlier_dim": d_s3, "s360_l3_x1_outlier_dim": d_x3, "s360_l3_x2_outlier_dim": d_x3b,
             "qwen_l3_sink_head": h_q3, "qwen_l3_least_sink_head": h_q3lo,
             "qwen_l3_sink_weight_per_head": [round(float(v), 4) for v in sink],
             "rule": "an outlier dim is the commonest per-token argmax of |x| over the layer's 32 tokens; Qwen's massive unit "
                     "is token 0's argmax of |SiLU(gate) * up|; the sink head is the head with the largest mean softmax "
                     "weight on key 0 over queries 16-31 (fp32's tile), the least-sink head the smallest (fp16's tile); each cut "
                     "takes the aligned block (64, 32 or 16 wide) holding the outlier"}
    prov = {"text": TEXT, "text_source": "Lewis Carroll, Alice's Adventures in Wonderland (1865), chapter 1's opening; public domain",
            "tokens_kept": T, "tokenizer_note": "each model's own byte-level BPE from its tokenizer.json (pre-tokenizer split "
                                                "with \\p{L} -> [A-Za-z] and \\p{N} -> [0-9], exact on this ASCII text; GPT-2's "
                                                "byte-to-unicode map; merges applied by rank); no special token added",
            "models": {}, "cuts": {}, "scales": scales, "picks": picks,
            "quantisation": "activations: q = clip(round_half_even(x / s), -127, 127), s = the token's max abs over its whole row / 127 "
                            "(the checkpoints' dynamic per-token symmetric int8); weights: the checkpoints' own int8 values",
            "forward": "layers 0-3 in float32: RMSNorm -> W8A8 q/k/v (int8 x int8 exact, x token scale x channel scale, + bias for Qwen) "
                       "-> rotary (rotate_half over 64 dims) -> scores q.k/8 with grouped KV heads -> causal softmax -> P V -> W8A8 o_proj "
                       "-> residual -> RMSNorm -> W8A8 gate, up -> SiLU(gate) * up -> W8A8 down_proj -> residual"}
    for key, M in (("qwen", Q), ("smol", S), ("s360", X)):
        m = M["m"]
        prov["models"][key] = {"repo": m["repo"], "revision": m["rev"], "file": "model.safetensors", "license": m["license"],
                               "license_source": "the model's Hugging Face card (cardData.license), read 4 Nov 2026",
                               "base_model": m["base"], "layers_run": len(M["layers"]),
                               "config": {k: m[k] for k in ("hid", "heads", "kv", "hs", "ff", "eps", "theta", "bias")},
                               "tokenizer_sha256": M["tok_sha"], "tokens": M["ids"], "pieces": M["pieces"],
                               "fetched": M["st"].fetched, "fetched_bytes": int(sum(f["bytes"] for f in M["st"].fetched)),
                               "checks": {"softmax_row_sums_max_err": float(max(np.abs(Ly["P"].sum(-1) - 1).max() for Ly in M["layers"]))}}
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
        print(key, mm["repo"], mm["revision"][:12], mm["license"], "fetched", mm["fetched_bytes"], "bytes in", len(mm["fetched"]), "requests")
    print(json.dumps({k: v for k, v in picks.items() if k != "rule"}))
    for n, c in prov["cuts"].items():
        print(f"{n:34s} {c['shape']} min {c['min']:.4g} max {c['max']:.4g} zeros {c['exact_zeros']}")
    for n, s in scales.items():
        print(f"{n:34s} row max/median {min(s['row_max_over_median']):.1f}..{max(s['row_max_over_median']):.1f}  int8 small share "
              f"{min(s['row_int8_small_share']):.3f}..{max(s['row_int8_small_share']):.3f}")


def main():
    global CACHE
    ap = argparse.ArgumentParser()
    ap.add_argument("--explore", type=int, default=0, help="run this many layers per model and print outlier stats")
    ap.add_argument("--cache", default=None)
    args = ap.parse_args()
    if args.cache:
        CACHE = os.path.abspath(args.cache)
        os.makedirs(CACHE, exist_ok=True)
    if args.explore:
        explore(args.explore)
        return 0
    write_cuts()
    return 0


if __name__ == "__main__":
    sys.exit(main())
