#!/usr/bin/env python3
# /// script
# requires-python = ">=3.9"
# dependencies = ["numpy"]
# ///
"""Q130(n): real tensors from a public model, cut as kinds tiles, with FROZEN predictions for E86, E87 and E91.

    python3 tools/claims-v3/kinds/real/make_real.py --hf-dir <dir> [--out tools/claims-v3/kinds/real]

<dir> holds three files of Hugging Face `openai-community/gpt2` at revision 607a30d783dfa663caf39e06633721c8d4cfcd7e
(MIT licence), each refused unless its sha256 is the one frozen below:

    model.safetensors   https://huggingface.co/openai-community/gpt2/resolve/<revision>/model.safetensors
    vocab.json, merges.txt   (the same URL form; GPT-2's byte-level BPE)

The model file is never committed: it is 548 MB and anyone can fetch it by the URL and check it by its sha256.

WHAT IT DOES
  1. Parses safetensors with numpy alone (an 8-byte little-endian header length, a JSON header, raw buffers).
  2. Tokenises a fixed public-domain text (the opening of Jane Austen's "Pride and Prejudice", 1813) with GPT-2's
     byte-level BPE, written here for ASCII text, and runs GPT-2 small forward in float32 numpy on its first 128
     tokens: wte + wpe, then per block ln_1, causal attention (12 heads of 64), residual, ln_2, c_fc, GELU (GPT-2's
     tanh form), c_proj, residual; all 12 blocks, ln_f and the tied unembedding, only to check the forward pass
     (the mean next-token loss must be that of a working language model).
  3. Takes three real matrix products:
       l0_mlp_up    layer 0's MLP up-projection:   A = ln_2's output (128 x 768),  B = h.0.mlp.c_fc.weight (768 x 3072)
       l6_mlp_down  layer 6's MLP down-projection: A = the GELU output (128 x 3072), B = h.6.mlp.c_proj.weight (3072 x 768)
       l6_attn_qk   layer 6's attention scores:    A = queries (128 x 768, 12 heads), B = keys transposed (768 x 128)
     and converts each operand to the three types: fp32 as the model computes it; fp16 by IEEE round-to-nearest-even
     of the fp32 values; int8 by symmetric quantisation as a deployment does it (weights per output channel,
     activations per tensor, scale = max|x| / 127, round half to even, clip to +-127; the scales are recorded).
  4. Cuts each product as A = 16 rows by K and B = K by 16 columns, K = 16 / 32 / 64 for fp32 / fp16 / int8, in the
     type's exact layout and stream order, with make_kinds.py's own encode() and tile_stats() (imported, unchanged),
     so a real tile is byte-for-byte the same kind of object as the 51 synthetic kinds. Windows are aligned blocks
     (16 rows, K, 16 columns), as a blocked GEMM feeds them; the K block of A and of B is the same k range.
  5. Chooses each window representatively: 20 aligned windows drawn at random (seeded), each window's statistics
     (gated fraction, zero-word fraction per side, stream-order Hamming per field per side, bus bits per op) compared
     with the 20-window median and with the whole matrix's (zero fractions, per-bit one-probability); the window
     nearest the median (sum over statistics of |x - median| / MAD) is taken, and all 20 are recorded.
  6. Freezes predictions per real tile:
       (a) D: switching W over the type's own zeros at 600 MHz on aifoundry3, from a predictor fitted on E78's 51
           measured kinds ONLY (e78.json items.*.D, the committed tiles). Per type, non-negative least squares on a
           pre-declared list of feature sets computed from each tile's issue stream and gate; the set with the
           lowest leave-one-kind-out rms on E78 is used. 95% interval: point +- t(0.975, n - p) x LOO rms.
       (b) burst and sustained MHz on aifoundry2 from E83's registered relation (dither at an effective cap, W* and
           sigma fitted on E80's 18 kinds; tools/claims-v3/kspeed/e83/predictions.json), applied to (a) through the
           conversion E83 used: c = c_E64(type, zeros) + D / (0.5218 / 0.517)^2.
       (E91) (a) divided by E82's per-type card scale (aifoundry3 / aifoundry1 card 1), labelled.
"""
import argparse
import hashlib
import itertools
import json
import os
import re
import struct
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
KINDS_DIR = os.path.dirname(HERE)
ROOT = os.path.normpath(os.path.join(HERE, "..", "..", "..", ".."))
sys.path.insert(0, KINDS_DIR)
import make_kinds as MK  # noqa: E402

# ------------------------------------------------------------------ provenance, frozen
MODEL = {
    "name": "GPT-2 small (124M parameters, 12 blocks, d_model 768, 12 heads of 64, d_ff 3072)",
    "hf_repo": "openai-community/gpt2",
    "revision": "607a30d783dfa663caf39e06633721c8d4cfcd7e",
    "revision_last_modified": "2024-02-19T10:57:45Z",
    "licence": "MIT (the model card's licence field)",
    "file": "model.safetensors",
    "url": "https://huggingface.co/openai-community/gpt2/resolve/607a30d783dfa663caf39e06633721c8d4cfcd7e/model.safetensors",
    "bytes": 548105171,
    "sha256": "248dfc3911869ec493c76e65bf2fcf7f615828b0254c12b473182f0f81d3a707",
    "sha256_note": "equals the Hub's own LFS oid for this file at this revision (api/models/openai-community/gpt2/tree/<revision>)",
}
TOKENIZER = {
    "vocab.json": {"sha256": "196139668be63f3b5d6574427317ae82f612a97c5d1cdaf36ed2256dbf636783",
                   "git_blob": "1f1d9aaca301414e7f6c9396df506798ff4eb9a6"},
    "merges.txt": {"sha256": "1ce1664773c50f3e0cc8842619a93edc4624525b728b188a9e0be33b7726adc5",
                   "git_blob": "226b0752cac7789c48f0cb3ec53eda48b7be36cc"},
    "url_form": "https://huggingface.co/openai-community/gpt2/resolve/607a30d783dfa663caf39e06633721c8d4cfcd7e/<file>",
}
TEXT_SOURCE = ("Jane Austen, Pride and Prejudice (1813), chapter 1, opening paragraphs: public domain. ASCII "
               "straight quotes; the exact characters are the `text` field, checked by its sha256.")
TEXT = (
    "It is a truth universally acknowledged, that a single man in possession of a good fortune, must be in "
    "want of a wife.\n\n"
    "However little known the feelings or views of such a man may be on his first entering a neighbourhood, "
    "this truth is so well fixed in the minds of the surrounding families, that he is considered the rightful "
    "property of some one or other of their daughters.\n\n"
    "\"My dear Mr. Bennet,\" said his lady to him one day, \"have you heard that Netherfield Park is let at "
    "last?\"\n\n"
    "Mr. Bennet replied that he had not.\n\n"
    "\"But it is,\" returned she; \"for Mrs. Long has just been here, and she told me all about it.\"\n\n"
    "Mr. Bennet made no answer.\n\n"
    "\"Do you not want to know who has taken it?\" cried his wife impatiently.\n\n"
    "\"You want to tell me, and I have no objection to hearing it.\"\n\n"
    "This was invitation enough.\n"
)
T_TOKENS = 128
SEED = 20261031
N_WINDOWS = 20
N_LAYER, D_MODEL, N_HEAD, D_HEAD, D_FF = 12, 768, 12, 64, 3072

# Committed inputs the predictions rest on, each refused unless its sha256 is this one.
E78J = "docs/reports/data/2026-10-31-e78-kinds-energy-matrix/e78.json"
KINDSJ = "tools/claims-v3/kinds/kinds.json"
E83P = "tools/claims-v3/kspeed/e83/predictions.json"
Q130C = "docs/reports/data/2026-10-31-q130-kinds-model/predictions.json"
E64F = "docs/reports/data/2026-10-23-e64-horace-power-limit/figures.json"
E82S = "docs/reports/data/2026-10-31-e82-kinds-aifoundry1/scored.json"
FROZEN_SHA = {
    E78J: "b7463b6c2c159eb70bd59418f729c4c9144f6eec778126ef660fe781cc724da5",
    KINDSJ: "9586568f23a97757e34b3cdacdffe5bee0122d236e28a9f76f06e8598b7b1337",
    E83P: "97f58c89344dc867b66e28c4ea9e969c4c610865700ea91221fed9c8f4f78cec",
    Q130C: "c5a66cb6d5f07a35d783d7db4be0f94a69482cf123defd2eccfda04fb6320a2c",
    E64F: "d430bfabd8f142d8fbb29b6f3f4ede71ff909d491b4de06526826d415828f9cb",
    E82S: "498d5c70f01778248c7800d7d1d7e07b033db35f29b897d40f5a21787bef0b53",
}
TYPES = ("fp32", "fp16", "int8")
MATS = {
    "l0_mlp_up": "layer 0 MLP up-projection: A = ln_2 output (tokens x 768), B = h.0.mlp.c_fc.weight (768 x 3072)",
    "l6_mlp_down": "layer 6 MLP down-projection: A = GELU output (tokens x 3072), B = h.6.mlp.c_proj.weight "
                   "(3072 x 768)",
    "l6_attn_qk": "layer 6 attention scores: A = queries (tokens x 768, 12 heads of 64), B = keys transposed "
                  "(768 x tokens); a window's K block lies inside one head because 64 is a multiple of every K",
}
# Two-sided 95% t quantiles, df 1..30.
T975 = [12.706, 4.303, 3.182, 2.776, 2.571, 2.447, 2.365, 2.306, 2.262, 2.228, 2.201, 2.179, 2.160, 2.145, 2.131,
        2.120, 2.110, 2.101, 2.093, 2.086, 2.080, 2.074, 2.069, 2.064, 2.060, 2.056, 2.052, 2.048, 2.045, 2.042]


def sha_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for blk in iter(lambda: f.read(1 << 20), b""):
            h.update(blk)
    return h.hexdigest()


def sha_bytes(b):
    return hashlib.sha256(b).hexdigest()


# ------------------------------------------------------------------ safetensors, numpy only
def read_safetensors(path, names):
    with open(path, "rb") as f:
        n = struct.unpack("<Q", f.read(8))[0]
        header = json.loads(f.read(n))
        base = 8 + n
        out = {}
        for name in names:
            ent = header[name]
            if ent["dtype"] != "F32":
                raise SystemExit(f"refused: {name} has dtype {ent['dtype']}, expected F32")
            s, e = ent["data_offsets"]
            f.seek(base + s)
            buf = f.read(e - s)
            out[name] = np.frombuffer(buf, dtype="<f4").reshape(ent["shape"]).copy()
    meta = {"header_bytes": n, "tensors": len([k for k in header if k != "__metadata__"])}
    return out, meta


# ------------------------------------------------------------------ GPT-2 byte-level BPE (ASCII text)
def bytes_to_unicode():
    bs = list(range(ord("!"), ord("~") + 1)) + list(range(ord("\xa1"), ord("\xac") + 1)) + \
        list(range(ord("\xae"), ord("\xff") + 1))
    cs = bs[:]
    n = 0
    for b in range(256):
        if b not in bs:
            bs.append(b)
            cs.append(256 + n)
            n += 1
    return dict(zip(bs, [chr(c) for c in cs]))


# GPT-2's pattern with \p{L} and \p{N} written as their ASCII members: identical on ASCII input, which is asserted.
PAT = re.compile(r"""'s|'t|'re|'ve|'m|'ll|'d| ?[A-Za-z]+| ?[0-9]+| ?[^\sA-Za-z0-9]+|\s+(?!\S)|\s+""")


def bpe_encode(text, vocab, merges):
    assert all(ord(ch) < 128 for ch in text), "the tokenizer here is exact for ASCII text only"
    ranks = {tuple(m.split()): i for i, m in enumerate(merges)}
    b2u = bytes_to_unicode()
    ids = []
    for piece in PAT.findall(text):
        word = tuple(b2u[b] for b in piece.encode("utf-8"))
        while len(word) > 1:
            pairs = {(word[i], word[i + 1]) for i in range(len(word) - 1)}
            best = min(pairs, key=lambda p: ranks.get(p, float("inf")))
            if best not in ranks:
                break
            new, i = [], 0
            while i < len(word):
                if i < len(word) - 1 and (word[i], word[i + 1]) == best:
                    new.append(word[i] + word[i + 1])
                    i += 2
                else:
                    new.append(word[i])
                    i += 1
            word = tuple(new)
        ids.extend(vocab[w] for w in word)
    return ids


# ------------------------------------------------------------------ GPT-2 small forward, float32 numpy
def layer_norm(x, w, b, eps=1e-5):
    mu = x.mean(-1, keepdims=True)
    var = ((x - mu) ** 2).mean(-1, keepdims=True)
    return ((x - mu) / np.sqrt(var + np.float32(eps))) * w + b


def gelu_new(x):
    c = np.float32(np.sqrt(2.0 / np.pi))
    return np.float32(0.5) * x * (np.float32(1.0) + np.tanh(c * (x + np.float32(0.044715) * x * x * x)))


def forward(W, ids):
    T = len(ids)
    h = W["wte.weight"][ids] + W["wpe.weight"][:T]
    keep = {}
    mask = np.triu(np.ones((T, T), dtype=bool), k=1)
    for L in range(N_LAYER):
        p = f"h.{L}."
        x = layer_norm(h, W[p + "ln_1.weight"], W[p + "ln_1.bias"])
        qkv = x @ W[p + "attn.c_attn.weight"] + W[p + "attn.c_attn.bias"]
        q, k, v = qkv[:, :D_MODEL], qkv[:, D_MODEL:2 * D_MODEL], qkv[:, 2 * D_MODEL:]
        qh = q.reshape(T, N_HEAD, D_HEAD).transpose(1, 0, 2)
        kh = k.reshape(T, N_HEAD, D_HEAD).transpose(1, 0, 2)
        vh = v.reshape(T, N_HEAD, D_HEAD).transpose(1, 0, 2)
        att = (qh @ kh.transpose(0, 2, 1)) / np.float32(np.sqrt(D_HEAD))
        att = np.where(mask[None], np.float32(-1e10), att)
        att = att - att.max(-1, keepdims=True)
        att = np.exp(att)
        att = att / att.sum(-1, keepdims=True)
        y = (att @ vh).transpose(1, 0, 2).reshape(T, D_MODEL)
        h = h + (y @ W[p + "attn.c_proj.weight"] + W[p + "attn.c_proj.bias"])
        x2 = layer_norm(h, W[p + "ln_2.weight"], W[p + "ln_2.bias"])
        u = x2 @ W[p + "mlp.c_fc.weight"] + W[p + "mlp.c_fc.bias"]
        g = gelu_new(u)
        h = h + (g @ W[p + "mlp.c_proj.weight"] + W[p + "mlp.c_proj.bias"])
        if L == 0:
            keep["l0_ln2"] = x2
        if L == 6:
            keep["l6_gelu"] = g
            keep["l6_q"] = q
            keep["l6_k"] = k
    hf = layer_norm(h, W["ln_f.weight"], W["ln_f.bias"])
    logits = hf.astype(np.float64) @ W["wte.weight"].astype(np.float64).T
    lse = np.log(np.exp(logits - logits.max(-1, keepdims=True)).sum(-1)) + logits.max(-1)
    nll = lse[:-1] - logits[np.arange(T - 1), ids[1:]]
    top1 = float(np.mean(np.argmax(logits[:-1], axis=-1) == np.asarray(ids[1:])))
    check = {"mean_next_token_nll_nats": round(float(nll.mean()), 4),
             "perplexity": round(float(np.exp(nll.mean())), 2), "top1_next_token_accuracy": round(top1, 4),
             "positions_scored": T - 1}
    return keep, check


# ------------------------------------------------------------------ the three types
def quant_per_tensor(x):
    s = float(np.max(np.abs(x))) / 127.0
    return np.clip(np.rint(x.astype(np.float64) / s), -127, 127).astype(np.int8), s


def quant_per_out_channel(w):
    """w is (in, out) as GPT-2's Conv1D stores it (y = x @ w): one scale per output column."""
    s = np.max(np.abs(w.astype(np.float64)), axis=0) / 127.0
    return np.clip(np.rint(w.astype(np.float64) / s[None, :]), -127, 127).astype(np.int8), s


def to_type(x, t):
    if t == "fp32":
        return x.astype(np.float32)
    if t == "fp16":
        return x.astype(np.float16)          # IEEE round to nearest even, numpy's conversion
    raise ValueError(t)


def whole_stats(M, t, side):
    """Statistics of a whole operand matrix in type t: words = E consecutive k (along a row of A, a column of B)."""
    E, size, dtype, K = MK.TYPES[t]
    X = np.asarray(M)
    if side == "b":
        X = X.T                                                  # rows = output columns, k along the row
    R, Kd = X.shape
    Kd2 = (Kd // E) * E
    X = np.ascontiguousarray(X[:, :Kd2])
    ew = 32 // E
    if t == "int8":
        u = X.astype(np.int8).view(np.uint8).astype(np.uint64)
    elif t == "fp16":
        u = X.astype(np.float16).view(np.uint16).astype(np.uint64)
    else:
        u = X.astype(np.float32).view(np.uint32).astype(np.uint64)
    words_zero = np.all(u.reshape(R, Kd2 // E, E) == 0, axis=-1)
    vals = X.astype(np.float64)
    return {"elements": int(u.size), "zero_word_frac": round(float(words_zero.mean()), 6),
            "zero_elem_frac": round(float(np.mean(u == 0)), 6),
            "p1_elem": [round(float(np.mean((u >> np.uint64(b)) & np.uint64(1))), 6) for b in range(ew)],
            "mean": round(float(vals.mean()), 6), "sd": round(float(vals.std()), 6),
            "max_abs": round(float(np.max(np.abs(vals))), 6)}


# ------------------------------------------------------------------ predictor features (stream and gate)
def elem_width(words, t, mode):
    """Per word, the width of each of its E elements. floats: 'sig' = significant mantissa bits (the field's width
    minus its trailing zeros, 0 for a zero field), 'pop' = mantissa popcount; int8: 'sig' = bit length of |x|,
    'pop' = popcount of |x|."""
    w = np.asarray(words, dtype=np.uint64)
    E = MK.TYPES[t][0]
    ew = 32 // E
    out = []
    for e in range(E):
        x = ((w >> np.uint64(e * ew)) & np.uint64((1 << ew) - 1)).astype(np.int64)
        if t == "int8":
            m = np.abs(np.where(x >= 128, x - 256, x))
            if mode == "pop":
                out.append(MK.popcount32(m.astype(np.uint32)))
            else:
                out.append(np.where(m > 0, np.floor(np.log2(np.maximum(m, 1))).astype(np.int64) + 1, 0))
            continue
        mbits = 23 if t == "fp32" else 10
        m = x & ((1 << mbits) - 1)
        if mode == "pop":
            out.append(MK.popcount32(m.astype(np.uint32)))
        else:
            low = m & (-m)
            tz = np.where(m > 0, np.round(np.log2(np.maximum(low, 1))).astype(np.int64), 0)
            out.append(np.where(m > 0, mbits - tz, 0))
    return np.stack(out, axis=-1)


def features(raw, t):
    """What the predictor reads from a tile: u = the ungated share of column-slot-cycles (make_kinds' gate);
    A, B = operand-bus bit flips that land on ungated slots (A: the broadcast word's flips times the ungated slots of
    the micro-op it lands on; B: each slot's own flips when that slot is ungated), in units of 1e4 bits an op;
    N_* = ungated slot-cycles whose operand pair changed, in 1e3; Vs_* = the same slot-cycles weighted by the summed
    element widths of both operands (1e4), Vp_* = weighted by the product of (1 + width) (1e5)."""
    aw, bw = MK.words_of(raw)
    a_seq, b_seq = MK.issue_streams_fast(aw, bw, t)
    gm = MK.gate_mask(a_seq, b_seq, t)
    on = ~gm
    on_slot = np.concatenate([on, on], axis=1) if t == "int8" else on
    on_next = np.roll(on_slot, -1, axis=0).astype(np.float64)
    n_on_next = on_next.sum(axis=1)
    da = (a_seq ^ np.roll(a_seq, -1)).astype(np.uint32)
    db = (b_seq ^ np.roll(b_seq, -1, axis=0)).astype(np.uint32)
    f = {"u": float(on_slot.mean()),
         "A": float((MK.popcount32(da) * n_on_next).sum()) / 1e4,
         "B": float((MK.popcount32(db) * on_next).sum()) / 1e4}
    a_next, b_next = np.roll(a_seq, -1), np.roll(b_seq, -1, axis=0)
    act = ((a_seq != a_next)[:, None] | (b_seq != b_next)).astype(np.float64) * on_next
    for mode in ("sig", "pop"):
        wa = elem_width(a_next, t, mode).astype(np.float64)
        wb = elem_width(b_next, t, mode).astype(np.float64)
        f["N_" + mode] = float(act.sum()) / 1e3
        f["Vs_" + mode] = float(((wa[:, None, :] + wb).sum(axis=-1) * act).sum()) / 1e4
        f["Vp_" + mode] = float((((1 + wa[:, None, :]) * (1 + wb)).sum(axis=-1) * act).sum()) / 1e5
    return {k: round(v, 6) for k, v in f.items()}


CANDIDATES = {
    "u,A,B": ["u", "A", "B"],
    "u,A,B,Vs_sig": ["u", "A", "B", "Vs_sig"],
    "u,A,B,Vp_sig": ["u", "A", "B", "Vp_sig"],
    "u,A,B,Vs_pop": ["u", "A", "B", "Vs_pop"],
    "u,A,B,Vp_pop": ["u", "A", "B", "Vp_pop"],
    "u,Vs_sig": ["u", "Vs_sig"],
    "u,Vp_sig": ["u", "Vp_sig"],
    "u,Vs_pop": ["u", "Vs_pop"],
    "u,Vp_pop": ["u", "Vp_pop"],
    "u,N_sig,A,B,Vs_sig": ["u", "N_sig", "A", "B", "Vs_sig"],
    "u,N_pop,A,B,Vp_pop": ["u", "N_pop", "A", "B", "Vp_pop"],
}


def nnls(X, y):
    """Exact non-negative least squares by enumerating supports (at most 5 columns): every power term >= 0."""
    p = X.shape[1]
    best = (np.inf, None)
    for r in range(1, p + 1):
        for S in itertools.combinations(range(p), r):
            b = np.linalg.lstsq(X[:, S], y, rcond=None)[0]
            if np.all(b >= 0):
                sse = float(np.sum((X[:, S] @ b - y) ** 2))
                if sse < best[0] - 1e-12:
                    full = np.zeros(p)
                    full[list(S)] = b
                    best = (sse, full)
    return best[1]


def fit_predictor(E78, root):
    """Per type: the candidate with the lowest leave-one-kind-out rms on E78's kinds of that type (ties: fewer
    terms), NNLS on all of them. Uses E78's 51 kinds and their committed tiles only."""
    rows = {t: [] for t in TYPES}
    for key, it in E78["items"].items():
        if "." not in key:
            continue
        t, k = key.split(".", 1)
        raw = open(os.path.join(root, "tools/claims-v3/kinds/tiles", t, k + ".bin"), "rb").read()
        rows[t].append({"kind": k, "D": it["D"]["mean"], "D_ci95": it["D"]["ci95"], "f": features(raw, t)})
    out = {}
    for t in TYPES:
        R = rows[t]
        y = np.array([r["D"] for r in R])
        table = {}
        for name, cols in CANDIDATES.items():
            X = np.array([[r["f"][c] for c in cols] for r in R])
            b = nnls(X, y)
            res = X @ b - y
            loo = []
            for i in range(len(y)):
                m = np.ones(len(y), bool)
                m[i] = False
                loo.append(float(X[i] @ nnls(X[m], y[m]) - y[i]))
            loo = np.array(loo)
            table[name] = {"cols": cols, "beta": [round(float(v), 6) for v in b],
                           "terms_nonzero": int(np.sum(b > 0)),
                           "rms_in_w": round(float(np.sqrt(np.mean(res ** 2))), 4),
                           "rms_loo_w": round(float(np.sqrt(np.mean(loo ** 2))), 4),
                           "max_abs_loo_w": round(float(np.max(np.abs(loo))), 4),
                           "loo_residual_w": {R[i]["kind"]: round(float(loo[i]), 3) for i in range(len(y))}}
        sel = min(table, key=lambda n: (table[n]["rms_loo_w"], table[n]["terms_nonzero"]))
        s = table[sel]
        n, p = len(y), s["terms_nonzero"]
        tq = T975[n - p - 1]
        cols = s["cols"]
        X = np.array([[r["f"][c] for c in cols] for r in R])
        out[t] = {"n_kinds": n, "selected": sel, "cols": cols, "beta": s["beta"], "terms_nonzero": p,
                  "rms_in_w": s["rms_in_w"], "rms_loo_w": s["rms_loo_w"], "max_abs_loo_w": s["max_abs_loo_w"],
                  "t975": tq, "pi95_halfwidth_w": round(tq * s["rms_loo_w"], 4),
                  "feature_range_e78": {c: [round(float(X[:, j].min()), 6), round(float(X[:, j].max()), 6)]
                                        for j, c in enumerate(cols)},
                  "feature_mean_sd_e78": {c: [float(X[:, j].mean()), float(X[:, j].std()) or 1.0]
                                          for j, c in enumerate(cols)},
                  "e78_points": [{"kind": r["kind"], "D_w": round(r["D"], 4), "fit_w": round(float(X[i] @ np.array(s["beta"])), 4)}
                                 for i, r in enumerate(R)],
                  "candidates": table}
    return out, rows


def predict_D(P, t, f, rows_t):
    s = P[t]
    x = np.array([f[c] for c in s["cols"]])
    pt = float(x @ np.array(s["beta"]))
    hw = s["pi95_halfwidth_w"]
    used = [c for c, b in zip(s["cols"], s["beta"]) if b > 0]          # the terms the prediction rests on
    outside = [c for c in used if not (s["feature_range_e78"][c][0] - 1e-9 <= f[c]
                                       <= s["feature_range_e78"][c][1] + 1e-9)]
    # nearest E78 kind in the used features, z-scored over E78's kinds of the type (a labelled arm)
    ms = s["feature_mean_sd_e78"]
    z = np.array([(f[c] - ms[c][0]) / ms[c][1] for c in used])
    best = min(rows_t, key=lambda r: float(np.sum((np.array([(r["f"][c] - ms[c][0]) / ms[c][1]
                                                              for c in used]) - z) ** 2)))
    return {"point_w": round(max(pt, 0.0), 3), "pi95_w": [round(max(pt - hw, 0.0), 3), round(pt + hw, 3)],
            "model": s["selected"], "features_outside_e78_range": outside,
            "nearest_e78_kind": best["kind"], "nearest_e78_kind_D_w": round(best["D"], 3)}


# ------------------------------------------------------------------ windows
def window_vector(st, t):
    v = [st["gated_lane_frac"], st["a"]["zero_word_frac"], st["b"]["zero_word_frac"]]
    for side in ("a", "b"):
        for fld in MK.FIELDS[t]:
            v.append(st[side]["hamming"][fld])
    v.append(st["bus_bits_per_op"])
    return v


def window_names(t):
    names = ["gated_lane_frac", "a.zero_word_frac", "b.zero_word_frac"]
    for side in ("a", "b"):
        names += [f"{side}.hamming.{fld}" for fld in MK.FIELDS[t]]
    return names + ["bus_bits_per_op"]


def cut(Aq, Bq, r0, k0, j0, K):
    return Aq[r0:r0 + 16, k0:k0 + K], Bq[k0:k0 + K, j0:j0 + 16]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--hf-dir", required=True, help="a directory holding model.safetensors, vocab.json, merges.txt")
    ap.add_argument("--out", default=HERE)
    a = ap.parse_args()

    # ---- inputs, refused unless their sha256 is frozen
    shas = {}
    for p, want in FROZEN_SHA.items():
        got = sha_file(os.path.join(ROOT, p))
        if got != want:
            sys.exit(f"refused: {p} sha256 {got} is not the frozen {want}")
        shas[p] = got
    mpath = os.path.join(a.hf_dir, "model.safetensors")
    if sha_file(mpath) != MODEL["sha256"]:
        sys.exit("refused: model.safetensors sha256 differs from the frozen one")
    for fn, rec in TOKENIZER.items():
        if fn.endswith((".json", ".txt")) and sha_file(os.path.join(a.hf_dir, fn)) != rec["sha256"]:
            sys.exit(f"refused: {fn} sha256 differs from the frozen one")

    # ---- tokens and the forward pass
    vocab = json.load(open(os.path.join(a.hf_dir, "vocab.json"), encoding="utf-8"))
    merges = [ln for ln in open(os.path.join(a.hf_dir, "merges.txt"), encoding="utf-8").read().split("\n")[1:] if ln]
    ids_all = bpe_encode(TEXT, vocab, merges)
    if len(ids_all) < T_TOKENS:
        sys.exit(f"refused: the text gives {len(ids_all)} tokens, need {T_TOKENS}")
    ids = ids_all[:T_TOKENS]
    names = ["wte.weight", "wpe.weight", "ln_f.weight", "ln_f.bias"]
    for L in range(N_LAYER):
        for s in ("ln_1.weight", "ln_1.bias", "attn.c_attn.weight", "attn.c_attn.bias", "attn.c_proj.weight",
                  "attn.c_proj.bias", "ln_2.weight", "ln_2.bias", "mlp.c_fc.weight", "mlp.c_fc.bias",
                  "mlp.c_proj.weight", "mlp.c_proj.bias"):
            names.append(f"h.{L}.{s}")
    W, smeta = read_safetensors(mpath, names)
    keep, fcheck = forward(W, ids)
    if not (fcheck["mean_next_token_nll_nats"] < 5.0):
        sys.exit(f"refused: the forward pass does not look like a working GPT-2 ({fcheck})")

    full = {
        "l0_mlp_up": (keep["l0_ln2"], W["h.0.mlp.c_fc.weight"], "activation", "weight"),
        "l6_mlp_down": (keep["l6_gelu"], W["h.6.mlp.c_proj.weight"], "activation", "weight"),
        "l6_attn_qk": (keep["l6_q"], keep["l6_k"].T.copy(), "activation", "activation"),
    }

    # ---- the predictor (E78 only), the relation (E83), the card scale (E82)
    E78 = json.load(open(os.path.join(ROOT, E78J)))
    P, e78rows = fit_predictor(E78, ROOT)
    sys.path.insert(0, os.path.join(ROOT, "tools", "claims-v3", "kspeed", "e83"))
    import predict_e83 as P83  # noqa: E402
    E83 = json.load(open(os.path.join(ROOT, E83P)))
    F64 = json.load(open(os.path.join(ROOT, E64F)))
    Q = json.load(open(os.path.join(ROOT, Q130C)))["predictions"]
    rel = P83.Rel({int(k): v for k, v in F64["fit"]["B"].items()})
    Wb, sb = E83["relation"]["burst"]["W_star_w"], E83["relation"]["burst"]["sigma_w"]
    Ws, ss = E83["relation"]["sustained"]["W_star_w"], E83["relation"]["sustained"]["sigma_w"]
    c0 = {t: Q[f"{t}/zeros"]["c_w_a2_600mhz"] for t in TYPES}
    xfer = P83.XFER
    scale82 = json.load(open(os.path.join(ROOT, E82S)))["cross_card"]["primary"]["x3"]["per_type_median"]

    def clocks(t, D):
        c = c0[t] + D / xfer
        b, b8 = rel.f(c, Wb, sb)
        s, s8 = rel.f(c, Ws, ss)
        return c, b, b8, s, s8

    # ---- tiles
    td = os.path.join(a.out, "tiles")
    tiles, preds, mats_out = {}, {}, {}
    for name, (Af, Bf, akind, bkind) in full.items():
        mats_out[name] = {"what": MATS[name], "A_shape": list(Af.shape), "B_shape": list(Bf.shape),
                          "A_is": akind, "B_is": bkind,
                          "fp32_A": whole_stats(Af, "fp32", "a"), "fp32_B": whole_stats(Bf, "fp32", "b")}
        for t in TYPES:
            E, size, dtype, K = MK.TYPES[t]
            quant = {}
            if t == "int8":
                Aq, sa = quant_per_tensor(Af)
                if bkind == "weight":
                    Bq, sbv = quant_per_out_channel(Bf)
                    quant = {"A": {"scheme": "per tensor, symmetric, scale = max|A| / 127 over the whole "
                                             f"{Af.shape[0]} x {Af.shape[1]} activation, round half to even, "
                                             "clip +-127", "scale": sa},
                             "B": {"scheme": "per output channel (column of the (in, out) weight), symmetric, "
                                             "scale_j = max_k |W[k, j]| / 127 over the whole column, round half to "
                                             "even, clip +-127",
                                   "scale_summary": {"n": int(sbv.size), "min": float(sbv.min()),
                                                     "median": float(np.median(sbv)), "max": float(sbv.max())}}}
                else:
                    Bq, sbs = quant_per_tensor(Bf)
                    quant = {"A": {"scheme": "per tensor (all 12 heads' queries), symmetric, scale = max|q| / 127",
                                   "scale": sa},
                             "B": {"scheme": "per tensor (all 12 heads' keys), symmetric, scale = max|k| / 127",
                                   "scale": sbs}}
            else:
                Aq, Bq = to_type(Af, t), to_type(Bf, t)
                if t == "fp16":
                    quant = {"A": {"scheme": "IEEE round to nearest even from the fp32 value (numpy astype)"},
                             "B": {"scheme": "IEEE round to nearest even from the fp32 value (numpy astype)"}}
            whole = {"A": whole_stats(Aq, t, "a"), "B": whole_stats(Bq, t, "b")}
            # aligned windows: rows by 16, k by K, columns by 16
            nr, nk, nj = Aq.shape[0] // 16, Aq.shape[1] // K, Bq.shape[1] // 16
            rng = np.random.default_rng(int.from_bytes(
                hashlib.sha256(f"{SEED}/real/{name}/{t}".encode()).digest()[:8], "little"))
            seen, cands = set(), []
            while len(cands) < N_WINDOWS:
                w = (int(rng.integers(nr)) * 16, int(rng.integers(nk)) * K, int(rng.integers(nj)) * 16)
                if w in seen:
                    continue
                seen.add(w)
                Aw, Bw = cut(Aq, Bq, w[0], w[1], w[2], K)
                raw = MK.encode(Aw, Bw, t)
                st = MK.tile_stats(raw, t)
                fe = features(raw, t)
                pd = predict_D(P, t, fe, e78rows[t])
                ws = {"A": whole_stats(Aw, t, "a"), "B": whole_stats(Bw, t, "b")}
                cands.append({"rows": [w[0], w[0] + 16], "k": [w[1], w[1] + K], "cols": [w[2], w[2] + 16],
                              "vector": window_vector(st, t), "D_pred_w": pd["point_w"],
                              "p1_elem_mad_vs_whole": {
                                  s_: round(float(np.mean(np.abs(np.array(ws[s_]["p1_elem"]) -
                                                                 np.array(whole[s_]["p1_elem"])))), 6)
                                  for s_ in ("A", "B")}})
            V = np.array([c["vector"] for c in cands], dtype=np.float64)
            med = np.median(V, axis=0)
            mad = np.median(np.abs(V - med), axis=0)
            scale = np.where(mad > 0, mad, 1.0)
            dist = np.sum(np.abs(V - med) / scale, axis=1)
            for c, dd in zip(cands, dist):
                c["distance_to_median"] = round(float(dd), 4)
                c["vector"] = [round(float(x), 6) for x in c["vector"]]
            ci = int(np.argmin(dist))
            ch = cands[ci]
            Aw, Bw = cut(Aq, Bq, ch["rows"][0], ch["k"][0], ch["cols"][0], K)
            raw = MK.encode(Aw, Bw, t)
            # the independent decoder must give back exactly the intended elements (make_kinds --check's test)
            da_, db_ = MK.decode(raw, t)
            want_a = np.asarray(Aw).astype(dtype)
            want_b = np.asarray(Bw).astype(dtype)
            if not (np.array_equal(da_.view(f"<u{size}"), want_a.view(f"<u{size}")) and
                    np.array_equal(db_.view(f"<u{size}"), want_b.view(f"<u{size}"))):
                sys.exit(f"refused: {t}/{name} does not decode back to its intended elements")
            os.makedirs(os.path.join(td, t), exist_ok=True)
            with open(os.path.join(td, t, f"{name}.bin"), "wb") as fh:
                fh.write(raw)
            st = MK.tile_stats(raw, t)
            fe = features(raw, t)
            pd = predict_D(P, t, fe, e78rows[t])
            c, b, b8, s, s8 = clocks(t, pd["point_w"])
            c_lo, b_hi, _, s_hi, _ = clocks(t, pd["pi95_w"][0])
            c_hi, b_lo, _, s_lo, _ = clocks(t, pd["pi95_w"][1])
            Dband = sorted(cc["D_pred_w"] for cc in cands)
            rec = {
                "file": f"tiles/{t}/{name}.bin", "bytes": len(raw), "sha256": sha_bytes(raw),
                "sha256_a": sha_bytes(raw[:1024]), "sha256_b": sha_bytes(raw[1024:]),
                "matrix": name, "what": MATS[name],
                "window": {"rows": ch["rows"], "k": ch["k"], "cols": ch["cols"], "index_among_20": ci,
                           "rule": "the one of 20 seeded aligned windows nearest the 20-window median (sum of "
                                   "|x - median| / MAD over window_choice.statistics)"},
                "quantisation": quant,
                "stats": st,
                "whole_matrix": whole,
                "window_vs_whole": {
                    "zero_word_frac_A": [st["a"]["zero_word_frac"], whole["A"]["zero_word_frac"]],
                    "zero_word_frac_B": [st["b"]["zero_word_frac"], whole["B"]["zero_word_frac"]],
                    "p1_elem_mean_abs_dev": ch["p1_elem_mad_vs_whole"]},
                "window_choice": {"statistics": window_names(t), "median_of_20": [round(float(x), 6) for x in med],
                                  "mad_of_20": [round(float(x), 6) for x in mad], "candidates": cands},
                "features": fe,
            }
            tiles.setdefault(t, {})[name] = rec
            preds[f"{t}/{name}"] = {
                "tile": f"tools/claims-v3/kinds/real/tiles/{t}/{name}.bin", "tile_sha256": rec["sha256"],
                "gated_lane_frac": st["gated_lane_frac"], "bus_bits_per_op": st["bus_bits_per_op"],
                "a_aifoundry3_600mhz": {
                    "D_w": pd["point_w"], "D_pi95_w": pd["pi95_w"], "model": pd["model"],
                    "features_outside_e78_range": pd["features_outside_e78_range"],
                    "nearest_e78_kind": pd["nearest_e78_kind"], "nearest_e78_kind_D_w": pd["nearest_e78_kind_D_w"],
                    "D_band_over_20_windows_w": {"min": Dband[0], "median": round(float(np.median(Dband)), 3),
                                                 "max": Dband[-1]}},
                "e91_aifoundry1_card1_600mhz": {
                    "D_w": round(pd["point_w"] / scale82[t], 3),
                    "D_pi95_w": [round(pd["pi95_w"][0] / scale82[t], 3), round(pd["pi95_w"][1] / scale82[t], 3)],
                    "card_scale_e82": round(scale82[t], 4)},
                "b_aifoundry2_governor": {
                    "c_w": round(c, 3), "c_pi95_w": [round(c_lo, 3), round(c_hi, 3)],
                    "burst_mhz": round(b, 1), "burst_mhz_pi95": [round(b_lo, 1), round(b_hi, 1)],
                    "burst_share800": round(b8, 3), "burst_limit": "none" if b8 >= P83.NONE_SHARE else "power",
                    "burst_rate": round(P83.SH.rate_t(t, b), 3),
                    "sus_mhz": round(s, 1), "sus_mhz_pi95": [round(s_lo, 1), round(s_hi, 1)],
                    "sus_share800": round(s8, 3), "sus_limit": "none" if s8 >= P83.NONE_SHARE else "thermal",
                    "sus_rate": round(P83.SH.rate_t(t, s), 3),
                    "rate_unit": "TOPS" if t == "int8" else "TFLOPS"},
            }

    predictor_pub = {t: {k: v for k, v in P[t].items() if k != "feature_mean_sd_e78"} for t in TYPES}
    predictions = {
        "experiment": "Q130(n)", "date": "2026-10-31",
        "what": ("FROZEN predictions for the real GPT-2 tiles, made before any card ran them: (a) D, the switching W "
                 "over the type's own zeros at 600 MHz on aifoundry3 (E86), from a predictor fitted on E78's 51 "
                 "kinds only; (E91) the same divided by E82's per-type card scale, for aifoundry1 card 1; (b) the "
                 "burst and sustained clock on aifoundry2 under its own governor (E87), from E83's registered "
                 "relation applied to (a)"),
        "inputs_sha256": shas,
        "model_sha256": MODEL["sha256"],
        "predictor": {
            "form": ("per type, D = sum_i beta_i x_i with every beta_i >= 0 (exact NNLS), no intercept, so zeros "
                     "predict 0; x from make_real.features() on the tile's issue stream and gate"),
            "selection": ("per type, the candidate with the lowest leave-one-kind-out rms over E78's kinds of that "
                          "type (ties: fewer non-zero terms); the candidate list is CANDIDATES in make_real.py"),
            "interval": "point +- t(0.975, n - p) x LOO rms, p = non-zero terms; floored at 0",
            "fitted_on": "E78's 51 kinds only: e78.json items.<type>.<kind>.D.mean and the committed tiles",
            "per_type": predictor_pub},
        "relation_e83": {"source": E83P, "burst": {"W_star_w": Wb, "sigma_w": sb},
                         "sustained": {"W_star_w": Ws, "sigma_w": ss},
                         "conversion": "c = c_E64(type, zeros) + D / (0.5218 / 0.517)^2, as E83 used",
                         "c_zeros_w": c0, "xfer": xfer, "none_share_800": P83.NONE_SHARE,
                         "interval": "the clock at the two ends of (a)'s 95% interval"},
        "card_scale_e82": {"source": E82S + " cross_card.primary.x3.per_type_median",
                           "aifoundry3_over_card1": {t: round(scale82[t], 6) for t in TYPES}},
        "tiles": preds,
    }
    pjson = json.dumps(predictions, indent=1) + "\n"
    with open(os.path.join(a.out, "predictions-real.json"), "w") as fh:
        fh.write(pjson)
    spec = {
        "experiment": "Q130(n)", "date": "2026-10-31", "generator": "tools/claims-v3/kinds/real/make_real.py",
        "what": "real GPT-2 small tensors cut as 2,048-byte kinds tiles (A then B, 1,024 bytes each)",
        "model": MODEL, "tokenizer": TOKENIZER, "safetensors": smeta,
        "text": {"source": TEXT_SOURCE, "text": TEXT, "sha256": sha_bytes(TEXT.encode("ascii")),
                 "tokens_in_text": len(ids_all), "tokens_used": T_TOKENS, "token_ids": ids},
        "forward_check": fcheck,
        "conventions": {
            "layout_and_stream": "make_kinds.py encode() / tile_stats(), imported unchanged (kinds.json facts)",
            "K": {t: MK.TYPES[t][3] for t in TYPES},
            "fp16": "IEEE round to nearest even of the fp32 activations and weights (an fp16 model would compute "
                    "its activations in fp16; rounding the fp32 ones is the approximation)",
            "int8": "symmetric, zero point 0: weights per output channel, activations per tensor (max-abs over "
                    "this text's 128 tokens), round half to even, clip +-127",
            "attention": "raw q and k (the 1/sqrt(64) scale is applied after the product)",
            "rows": "tokens 0..127 of the text; windows are aligned 16-row blocks, so a window may include token 0",
        },
        "frozen_inputs_sha256": shas,
        "matrices": mats_out,
        "tiles": tiles,
        "predictions_file": "predictions-real.json",
        "predictions_sha256": sha_bytes(pjson.encode()),
        "predictions": predictions,
    }
    with open(os.path.join(a.out, "real.json"), "w") as fh:
        json.dump(spec, fh, indent=1)
        fh.write("\n")

    print(f"forward check: {fcheck}")
    for t in TYPES:
        s = P[t]
        print(f"predictor {t}: {s['selected']} beta {s['beta']} rms_in {s['rms_in_w']} LOO {s['rms_loo_w']} "
              f"(max {s['max_abs_loo_w']}) pi95 +-{s['pi95_halfwidth_w']} W")
    for key, p in preds.items():
        A_, B_ = p["a_aifoundry3_600mhz"], p["b_aifoundry2_governor"]
        print(f"{key:20s} gated {p['gated_lane_frac']:.3f} bus {p['bus_bits_per_op']:6d}  D {A_['D_w']:6.2f} "
              f"[{A_['D_pi95_w'][0]:.2f}, {A_['D_pi95_w'][1]:.2f}] near {A_['nearest_e78_kind']} "
              f"({A_['nearest_e78_kind_D_w']}) out {A_['features_outside_e78_range']}  burst {B_['burst_mhz']:.1f} "
              f"[{B_['burst_mhz_pi95'][0]:.0f}-{B_['burst_mhz_pi95'][1]:.0f}] sus {B_['sus_mhz']:.1f} "
              f"[{B_['sus_mhz_pi95'][0]:.0f}-{B_['sus_mhz_pi95'][1]:.0f}] {B_['sus_limit']}")
    print(f"predictions-real.json sha256 {sha_bytes(pjson.encode())}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
