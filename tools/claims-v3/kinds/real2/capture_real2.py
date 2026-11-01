#!/usr/bin/env python3
"""Q132(r), stage 1 of 3: run public models on public-domain inputs and save the operand matrices of real matmuls.

    python3 capture_real2.py --dl <dir> --out <dir> --repo <lab repo root> [--only gpt2,resnet18,...]

<dir> holds the files dl_models.py and dl_images.py fetched, each checked by sha256 against manifest-models.json and
manifest-images.json (the sha256s are repeated in real2.json). CPU only. Nothing here touches a card.

What a "product" is: a matrix A (rows x k) and a matrix B (k x columns) whose product is a real step of the network,
checked here by recomputing that step's output from A @ B and comparing it with what the network computed:
  - a conv layer: A = the layer's input unfolded into patches (F.unfold's own order, channel then height then width),
    B = the layer's weight flattened the same way (a conv IS this matmul, the im2col form);
  - a fully connected or feed-forward layer: A = its input, B = its weight (in, out);
  - GPT-2 attention: A = queries, B = keys transposed, as Q130(n).
Each product is saved as out/products/<name>.npz with A and B in float32 (or the arithmetic it was computed in).
"""
import argparse
import hashlib
import json
import os
import platform
import random
import sys
import time

import numpy as np

ap = argparse.ArgumentParser()
ap.add_argument("--dl", required=True)
ap.add_argument("--out", required=True)
ap.add_argument("--repo", required=True)
ap.add_argument("--only", default="")
ap.add_argument("--threads", type=int, default=8)
ARGS = ap.parse_args()

sys.path.insert(0, os.path.join(ARGS.repo, "tools/claims-v3/kinds/real"))
import make_real as MR  # noqa: E402

ONLY = set(x for x in ARGS.only.split(",") if x)
PD = os.path.join(ARGS.out, "products")
os.makedirs(PD, exist_ok=True)
CAPF = os.path.join(ARGS.out, "capture.json")
CAP = json.load(open(CAPF)) if os.path.exists(CAPF) else {"products": {}, "checks": {}}
MODELS = json.load(open(os.path.join(ARGS.dl, "manifest-models.json")))
IMAGES = json.load(open(os.path.join(ARGS.dl, "images", "manifest-images.json")))
TEXT = MR.TEXT
IMAGE_ORDER_SEED = "Q132(r)/images"


def want(x):
    return not ONLY or x in ONLY


def log(*a):
    print(time.strftime("%H:%M:%S"), *a, flush=True)


def verify_models():
    for slug, rec in MODELS.items():
        files = rec.get("files") or {rec["file"]: {"sha256": rec["sha256"]}}
        for fn, r in files.items():
            if MR.sha_file(os.path.join(ARGS.dl, slug, fn)) != r["sha256"]:
                sys.exit(f"refused: {slug}/{fn} differs from its manifest")


def save(name, A, B, what, source, a_is, b_is, extra=None, dtype=np.float32):
    A = np.asarray(A, dtype=dtype)
    B = np.asarray(B, dtype=dtype)
    p = os.path.join(PD, name + ".npz")
    np.savez(p, A=A, B=B)
    st = {}
    for side, X in (("A", A), ("B", B)):
        X_ = X.astype(np.float64)
        bits = X.view(np.uint32 if dtype == np.float32 else np.uint16)
        low = np.mean((bits & np.uint32(0xFFFF)) == 0) if dtype == np.float32 else np.mean((bits & np.uint16(0x7)) == 0)
        st[side] = {"shape": list(X.shape), "bytes_sha256": hashlib.sha256(X.tobytes()).hexdigest(), "low_mantissa_bits_zero_frac": round(float(low), 6),
                    "low_mantissa_bits": "the low 16 bits of the fp32 word" if dtype == np.float32 else "the low 3 bits of the fp16 word",
                    "plus_zero_frac": round(float(np.mean(bits == 0)), 6),
                    "neg_zero_frac": round(float(np.mean(bits == (0x80000000 if dtype == np.float32 else 0x8000))), 6),
                    "negative_frac": round(float(np.mean(X_ < 0)), 6), "mean": round(float(X_.mean()), 5),
                    "sd": round(float(X_.std()), 5), "max_abs": round(float(np.abs(X_).max()), 5),
                    "p99_abs": round(float(np.quantile(np.abs(X_), 0.99)), 5)}
    CAP["products"][name] = {"what": what, "source": source, "A_is": a_is, "B_is": b_is, "dtype": str(np.dtype(dtype)),
                             "stats": st, **(extra or {})}
    json.dump(CAP, open(CAPF, "w"), indent=1)
    log(name, "A", A.shape, "B", B.shape, "A +0", st["A"]["plus_zero_frac"], "A -0", st["A"]["neg_zero_frac"],
        "A neg", st["A"]["negative_frac"], "B +0", st["B"]["plus_zero_frac"])


# ------------------------------------------------------------------ GPT-2: fp32 (as Q130(n)), fp16, bf16, numpy only
GPT2_LAYERS = (0, 3, 6, 9, 11)


def gpt2_inputs():
    d = os.path.join(ARGS.dl, "gpt2")
    vocab = json.load(open(os.path.join(d, "vocab.json"), encoding="utf-8"))
    merges = [ln for ln in open(os.path.join(d, "merges.txt"), encoding="utf-8").read().split("\n")[1:] if ln]
    ids = MR.bpe_encode(TEXT, vocab, merges)[:MR.T_TOKENS]
    names = ["wte.weight", "wpe.weight", "ln_f.weight", "ln_f.bias"]
    for L in range(MR.N_LAYER):
        for s in ("ln_1.weight", "ln_1.bias", "attn.c_attn.weight", "attn.c_attn.bias", "attn.c_proj.weight",
                  "attn.c_proj.bias", "ln_2.weight", "ln_2.bias", "mlp.c_fc.weight", "mlp.c_fc.bias",
                  "mlp.c_proj.weight", "mlp.c_proj.bias"):
            names.append(f"h.{L}.{s}")
    W, _ = MR.read_safetensors(os.path.join(d, "model.safetensors"), names)
    return ids, W


def nll_check(hf, wte, ids):
    T = len(ids)
    logits = hf.astype(np.float64) @ wte.astype(np.float64).T
    lse = np.log(np.exp(logits - logits.max(-1, keepdims=True)).sum(-1)) + logits.max(-1)
    nll = lse[:-1] - logits[np.arange(T - 1), ids[1:]]
    return {"mean_next_token_nll_nats": round(float(nll.mean()), 4), "perplexity": round(float(np.exp(nll.mean())), 2),
            "top1_next_token_accuracy": round(float(np.mean(np.argmax(logits[:-1], axis=-1) == np.asarray(ids[1:]))), 4),
            "positions_scored": T - 1}


def forward32(W, ids):
    """make_real.forward's arithmetic, keeping more layers; L0 and L6 are compared with make_real.forward byte for byte."""
    T = len(ids)
    h = W["wte.weight"][ids] + W["wpe.weight"][:T]
    keep = {}
    mask = np.triu(np.ones((T, T), dtype=bool), k=1)
    for L in range(MR.N_LAYER):
        p = f"h.{L}."
        x = MR.layer_norm(h, W[p + "ln_1.weight"], W[p + "ln_1.bias"])
        qkv = x @ W[p + "attn.c_attn.weight"] + W[p + "attn.c_attn.bias"]
        q, k, v = qkv[:, :768], qkv[:, 768:1536], qkv[:, 1536:]
        qh = q.reshape(T, 12, 64).transpose(1, 0, 2)
        kh = k.reshape(T, 12, 64).transpose(1, 0, 2)
        vh = v.reshape(T, 12, 64).transpose(1, 0, 2)
        att = (qh @ kh.transpose(0, 2, 1)) / np.float32(np.sqrt(64))
        att = np.where(mask[None], np.float32(-1e10), att)
        att = att - att.max(-1, keepdims=True)
        att = np.exp(att)
        att = att / att.sum(-1, keepdims=True)
        y = (att @ vh).transpose(1, 0, 2).reshape(T, 768)
        h = h + (y @ W[p + "attn.c_proj.weight"] + W[p + "attn.c_proj.bias"])
        x2 = MR.layer_norm(h, W[p + "ln_2.weight"], W[p + "ln_2.bias"])
        u = x2 @ W[p + "mlp.c_fc.weight"] + W[p + "mlp.c_fc.bias"]
        g = MR.gelu_new(u)
        h = h + (g @ W[p + "mlp.c_proj.weight"] + W[p + "mlp.c_proj.bias"])
        if L in GPT2_LAYERS:
            keep[f"l{L}_ln2"], keep[f"l{L}_gelu"], keep[f"l{L}_q"], keep[f"l{L}_k"] = x2, g, q, k
    hf = MR.layer_norm(h, W["ln_f.weight"], W["ln_f.bias"])
    return keep, nll_check(hf, W["wte.weight"], ids)


def c16(x):
    return np.float16(x)


def ln16(x, w, b):
    mu = x.mean(-1, keepdims=True)                  # numpy's float16 mean: a float32 accumulator, rounded to float16
    d = x - mu
    # the variance is a dot product, so its accumulator is float32 too. Squaring in fp16 first overflows: GPT-2's
    # residual stream reaches |h| > 256, d*d is inf, and one inf wipes the whole token (the first run did that: NLL 4.44).
    var = (d.astype(np.float32) ** 2).mean(-1, keepdims=True).astype(np.float16)
    return (d / np.sqrt(var + c16(1e-5))) * w + b


def forward16(W32, ids):
    """GPT-2 small computed in fp16: every stored value is IEEE binary16 and every operation rounds to it. Dot products
    (numpy's float16 matmul, which has no BLAS) keep a float32 accumulator and round the result to fp16: exactly what
    the chip's TensorFMA16A32 does (fp16 operands, fp32 accumulator). Numpy's float16 functions compute exp and tanh in
    float32 and round. The causal mask is -inf (fp16 cannot hold -1e10)."""
    W = {k: v.astype(np.float16) for k, v in W32.items()}
    T = len(ids)
    h = W["wte.weight"][ids] + W["wpe.weight"][:T]
    keep = {}
    mask = np.triu(np.ones((T, T), dtype=bool), k=1)
    c = c16(np.sqrt(2.0 / np.pi))
    for L in range(MR.N_LAYER):
        p = f"h.{L}."
        x = ln16(h, W[p + "ln_1.weight"], W[p + "ln_1.bias"])
        qkv = np.matmul(x, W[p + "attn.c_attn.weight"]) + W[p + "attn.c_attn.bias"]
        q, k, v = qkv[:, :768], qkv[:, 768:1536], qkv[:, 1536:]
        qh = q.reshape(T, 12, 64).transpose(1, 0, 2)
        kh = k.reshape(T, 12, 64).transpose(1, 0, 2)
        vh = v.reshape(T, 12, 64).transpose(1, 0, 2)
        att = np.matmul(qh, kh.transpose(0, 2, 1)) / c16(8.0)
        att = np.where(mask[None], c16(-np.inf), att)
        att = att - att.max(-1, keepdims=True)
        att = np.exp(att)
        s = att.astype(np.float32).sum(-1, keepdims=True).astype(np.float16)
        att = att / s
        y = np.matmul(att, vh).transpose(1, 0, 2).reshape(T, 768)
        h = h + (np.matmul(y, W[p + "attn.c_proj.weight"]) + W[p + "attn.c_proj.bias"])
        x2 = ln16(h, W[p + "ln_2.weight"], W[p + "ln_2.bias"])
        u = np.matmul(x2, W[p + "mlp.c_fc.weight"]) + W[p + "mlp.c_fc.bias"]
        g = c16(0.5) * u * (c16(1.0) + np.tanh(c * (u + c16(0.044715) * u * u * u)))
        h = h + (np.matmul(g, W[p + "mlp.c_proj.weight"]) + W[p + "mlp.c_proj.bias"])
        if L in GPT2_LAYERS:
            keep[f"l{L}_ln2"], keep[f"l{L}_gelu"], keep[f"l{L}_q"], keep[f"l{L}_k"] = x2, g, q, k
        log("fp16 layer", L, "done; h sd", round(float(h.astype(np.float32).std()), 4), "nan", int(np.isnan(h).sum()))
    hf = ln16(h, W["ln_f.weight"], W["ln_f.bias"])
    return keep, nll_check(hf, W["wte.weight"], ids), W


def rb(x):
    """Round float32 to bfloat16 (8-bit significand), nearest even, kept in float32 bytes (low 16 bits zero)."""
    x = np.asarray(x, dtype=np.float32)
    u = x.view(np.uint32)
    low = u & np.uint32(0xFFFF)
    hi = u & np.uint32(0xFFFF0000)
    up = (low > 0x8000) | ((low == 0x8000) & (((hi >> np.uint32(16)) & np.uint32(1)) == 1))
    return (hi + (up.astype(np.uint32) << np.uint32(16))).astype(np.uint32).view(np.float32)


def forward_bf16(W32, ids):
    """GPT-2 small computed in bfloat16, as AVX-512 BF16 or a GPU's bf16 does: operands on the bf16 grid, dot products
    with a float32 accumulator, every stored result rounded to bf16 (rb). Held in float32 bytes."""
    W = {k: rb(v) for k, v in W32.items()}
    T = len(ids)
    h = rb(W["wte.weight"][ids] + W["wpe.weight"][:T])
    keep = {}
    mask = np.triu(np.ones((T, T), dtype=bool), k=1)

    def ln(x, w, b):
        mu = rb(x.mean(-1, keepdims=True))
        d = rb(x - mu)
        var = rb((d * d).mean(-1, keepdims=True))
        return rb(rb(d / rb(np.sqrt(rb(var + np.float32(1e-5))))) * w + b)

    c = rb(np.float32(np.sqrt(2.0 / np.pi)))
    for L in range(MR.N_LAYER):
        p = f"h.{L}."
        x = ln(h, W[p + "ln_1.weight"], W[p + "ln_1.bias"])
        qkv = rb(rb(x @ W[p + "attn.c_attn.weight"]) + W[p + "attn.c_attn.bias"])
        q, k, v = qkv[:, :768], qkv[:, 768:1536], qkv[:, 1536:]
        qh = q.reshape(T, 12, 64).transpose(1, 0, 2)
        kh = k.reshape(T, 12, 64).transpose(1, 0, 2)
        vh = v.reshape(T, 12, 64).transpose(1, 0, 2)
        att = rb(rb(qh @ kh.transpose(0, 2, 1)) / np.float32(8.0))
        att = np.where(mask[None], np.float32(-np.inf), att)
        att = rb(att - att.max(-1, keepdims=True))
        att = rb(np.exp(att))
        att = rb(att / rb(att.sum(-1, keepdims=True)))
        y = rb(att @ vh).transpose(1, 0, 2).reshape(T, 768)
        h = rb(h + rb(rb(y @ W[p + "attn.c_proj.weight"]) + W[p + "attn.c_proj.bias"]))
        x2 = ln(h, W[p + "ln_2.weight"], W[p + "ln_2.bias"])
        u = rb(rb(x2 @ W[p + "mlp.c_fc.weight"]) + W[p + "mlp.c_fc.bias"])
        g = rb(rb(np.float32(0.5) * u) * rb(np.float32(1.0) + rb(np.tanh(rb(c * rb(u + rb(np.float32(0.044715) * rb(rb(u * u) * u))))))))
        h = rb(h + rb(rb(g @ W[p + "mlp.c_proj.weight"]) + W[p + "mlp.c_proj.bias"]))
        if L in GPT2_LAYERS:
            keep[f"l{L}_ln2"], keep[f"l{L}_gelu"], keep[f"l{L}_q"], keep[f"l{L}_k"] = x2, g, q, k
    hf = ln(h, W["ln_f.weight"], W["ln_f.bias"])
    return keep, nll_check(hf, W["wte.weight"], ids), W


def diff16(X16, X32):
    """How far an fp16-computed activation lies from rounding the fp32 one."""
    R = X32.astype(np.float16)
    ul = np.spacing(np.abs(R).astype(np.float16)).astype(np.float64)
    d = np.abs(X16.astype(np.float64) - R.astype(np.float64))
    ulps = d / ul
    u16, r16 = X16.view(np.uint16), R.view(np.uint16)
    x32 = X32.astype(np.float64)
    pop = np.vectorize(lambda v: bin(int(v)).count("1"))(np.bitwise_xor(u16, r16).ravel()[:2000000])
    out = {"identical_bits_frac": round(float(np.mean(u16 == r16)), 5),
           "median_ulps": round(float(np.median(ulps)), 2), "p90_ulps": round(float(np.quantile(ulps, 0.9)), 2),
           "p99_ulps": round(float(np.quantile(ulps, 0.99)), 2),
           "mean_bits_differing_per_element": round(float(pop.mean()), 3),
           "sign_differs_frac": round(float(np.mean((u16 >> 15) != (r16 >> 15))), 5),
           "rel_rms_fp16computed_vs_fp32": round(float(np.sqrt(np.mean((X16.astype(np.float64) - x32) ** 2) / np.mean(x32 ** 2))), 6),
           "rel_rms_rounded_vs_fp32": round(float(np.sqrt(np.mean((R.astype(np.float64) - x32) ** 2) / np.mean(x32 ** 2))), 6),
           "neg_zero_frac_computed": round(float(np.mean(u16 == 0x8000)), 5), "neg_zero_frac_rounded": round(float(np.mean(r16 == 0x8000)), 5),
           "plus_zero_frac_computed": round(float(np.mean(u16 == 0)), 5), "plus_zero_frac_rounded": round(float(np.mean(r16 == 0)), 5),
           "subnormal_frac_computed": round(float(np.mean(((u16 & 0x7C00) == 0) & ((u16 & 0x3FF) != 0))), 5),
           "subnormal_frac_rounded": round(float(np.mean(((r16 & 0x7C00) == 0) & ((r16 & 0x3FF) != 0))), 5)}
    return out


def run_gpt2():
    ids, W = gpt2_inputs()
    t0 = time.time()
    keep, chk = forward32(W, ids)
    log("gpt2 fp32 forward", chk, round(time.time() - t0, 1), "s")
    k2, chk2 = MR.forward(W, ids)
    same = all(np.array_equal(keep[a].view(np.uint32), k2[b].view(np.uint32))
               for a, b in (("l0_ln2", "l0_ln2"), ("l6_gelu", "l6_gelu"), ("l6_q", "l6_q"), ("l6_k", "l6_k")))
    CAP["checks"]["gpt2_fp32"] = {**chk, "same_as_make_real_forward": bool(same), "tokens": len(ids), "token_ids_sha256": hashlib.sha256(np.asarray(ids, dtype=np.int64).tobytes()).hexdigest()}
    src = f"{MODELS['gpt2']['hf_repo']}@{MODELS['gpt2']['revision']}, text: Pride and Prejudice (real.json text), tokens 0-127"
    for L in GPT2_LAYERS:
        save(f"gpt2_l{L}_mlp_up", keep[f"l{L}_ln2"], W[f"h.{L}.mlp.c_fc.weight"],
             f"GPT-2 small layer {L} MLP up-projection: A = ln_2 output (128 x 768), B = h.{L}.mlp.c_fc.weight (768 x 3072)", src, "activation", "weight")
        save(f"gpt2_l{L}_mlp_down", keep[f"l{L}_gelu"], W[f"h.{L}.mlp.c_proj.weight"],
             f"GPT-2 small layer {L} MLP down-projection: A = GELU output (128 x 3072), B = h.{L}.mlp.c_proj.weight (3072 x 768)", src, "activation", "weight")
        save(f"gpt2_l{L}_attn_qk", keep[f"l{L}_q"], keep[f"l{L}_k"].T.copy(),
             f"GPT-2 small layer {L} attention scores: A = queries (128 x 768, 12 heads of 64), B = keys transposed (768 x 128)", src, "activation", "activation")
    t0 = time.time()
    k16, chk16, W16 = forward16(W, ids)
    log("gpt2 fp16 forward", chk16, round(time.time() - t0, 1), "s")
    comp = {}
    for a, b in (("l0_ln2", "l0_mlp_up"), ("l6_gelu", "l6_mlp_down"), ("l6_q", "l6_attn_qk"), ("l6_k", "l6_attn_qk.B"), ("l3_gelu", "l3_mlp_down"), ("l9_gelu", "l9_mlp_down")):
        comp[a] = diff16(k16[a], keep[a])
        log("fp16 computed vs rounded", a, comp[a])
    CAP["checks"]["gpt2_fp16_forward"] = {**chk16, "vs_rounding_fp32": comp, "arithmetic": forward16.__doc__.strip()}
    src16 = src + "; computed in fp16 (see checks.gpt2_fp16_forward.arithmetic)"
    for L in (0, 6):
        save(f"gpt2_l{L}_mlp_up_fp16fwd", k16[f"l{L}_ln2"], W16[f"h.{L}.mlp.c_fc.weight"], f"as gpt2_l{L}_mlp_up, A from a forward pass computed in fp16", src16, "activation", "weight", dtype=np.float16)
        save(f"gpt2_l{L}_mlp_down_fp16fwd", k16[f"l{L}_gelu"], W16[f"h.{L}.mlp.c_proj.weight"], f"as gpt2_l{L}_mlp_down, A from a forward pass computed in fp16", src16, "activation", "weight", dtype=np.float16)
        save(f"gpt2_l{L}_attn_qk_fp16fwd", k16[f"l{L}_q"], k16[f"l{L}_k"].T.copy(), f"as gpt2_l{L}_attn_qk, q and k from a forward pass computed in fp16", src16, "activation", "activation", dtype=np.float16)
    t0 = time.time()
    kb, chkb, Wb = forward_bf16(W, ids)
    log("gpt2 bf16 forward", chkb, round(time.time() - t0, 1), "s")
    CAP["checks"]["gpt2_bf16_forward"] = {**chkb, "arithmetic": forward_bf16.__doc__.strip()}
    srcb = src + "; computed in bfloat16, held in fp32 bytes (see checks.gpt2_bf16_forward.arithmetic)"
    save("gpt2_l6_mlp_down_bf16fwd", kb["l6_gelu"], Wb["h.6.mlp.c_proj.weight"], "as gpt2_l6_mlp_down, A and B on the bf16 grid, A from a forward pass computed in bf16", srcb, "activation", "weight")
    save("gpt2_l6_attn_qk_bf16fwd", kb["l6_q"], kb["l6_k"].T.copy(), "as gpt2_l6_attn_qk, q and k from a forward pass computed in bf16", srcb, "activation", "activation")
    json.dump(CAP, open(CAPF, "w"), indent=1)


def run_gpt2_half():
    """torch's own .half() on CPU, a sensitivity beside the numpy fp16 pass: its accumulators are fp16 where torch's are."""
    import torch
    from transformers import GPT2LMHeadModel
    ids, W = gpt2_inputs()
    d = os.path.join(ARGS.dl, "gpt2")
    out = {}
    try:
        m = GPT2LMHeadModel.from_pretrained(d, local_files_only=True, attn_implementation="eager").half().eval()
        grabbed = {}
        def pre(name):
            def hook(mod, inp):
                grabbed[name] = inp[0].detach().cpu().numpy().copy()
            return hook
        m.transformer.h[6].mlp.c_proj.register_forward_pre_hook(pre("l6_gelu"))
        m.transformer.h[0].mlp.c_fc.register_forward_pre_hook(pre("l0_ln2"))
        with torch.no_grad():
            r = m(torch.tensor([ids]), labels=torch.tensor([ids]))
        out["loss_nats"] = round(float(r.loss.float()), 4)
        keep32, _ = MR.forward(W, ids)
        k16 = np.load(os.path.join(PD, "gpt2_l6_mlp_down_fp16fwd.npz"))["A"]
        out["half_l6_gelu_vs_rounding_fp32"] = diff16(grabbed["l6_gelu"][0], keep32["l6_gelu"])
        out["half_l6_gelu_vs_numpy_fp16"] = {"identical_bits_frac": round(float(np.mean(grabbed["l6_gelu"][0].view(np.uint16) == k16.view(np.uint16))), 5)}
        out["half_l0_ln2_vs_rounding_fp32"] = diff16(grabbed["l0_ln2"][0], keep32["l0_ln2"])
        np.savez(os.path.join(PD, "x_gpt2_half_l6_gelu.npz"), A=grabbed["l6_gelu"][0])
        out["ok"] = True
    except Exception as e:  # recorded, not fatal: the numpy pass is the primary one
        out["ok"] = False
        out["error"] = repr(e)[:400]
    log("gpt2 .half()", out)
    CAP["checks"]["gpt2_torch_half"] = out
    json.dump(CAP, open(CAPF, "w"), indent=1)


# ------------------------------------------------------------------ images
def image_list():
    ids = sorted(IMAGES["images"].keys())
    random.Random(IMAGE_ORDER_SEED).shuffle(ids)
    return ids


def imagenet_batch(ids):
    import torch
    from PIL import Image
    from torchvision import transforms as T
    tf = T.Compose([T.Resize(256), T.CenterCrop(224), T.ToTensor(),
                    T.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])])
    return torch.stack([tf(Image.open(os.path.join(ARGS.dl, "images", i + ".jpg")).convert("RGB")) for i in ids])


def vit_batch(ids):
    import torch
    from PIL import Image
    from torchvision import transforms as T
    tf = T.Compose([T.Resize((224, 224)), T.ToTensor(), T.Normalize(mean=[0.5, 0.5, 0.5], std=[0.5, 0.5, 0.5])])
    return torch.stack([tf(Image.open(os.path.join(ARGS.dl, "images", i + ".jpg")).convert("RGB")) for i in ids])


def check_conv(A, B, conv, x_in, name):
    """The matmul equals the conv: recompute the layer's output from A @ B for the first image."""
    import torch
    with torch.no_grad():
        out = conv(x_in[:1])
    n = out.shape[-2] * out.shape[-1]
    y = torch.tensor(A[:n]) @ torch.tensor(B)
    if conv.bias is not None:
        y = y + conv.bias.detach()
    y = y.T.reshape(out.shape[1], out.shape[2], out.shape[3])
    e = float((y - out[0]).abs().max() / out.abs().max())
    if e > 2e-4:
        sys.exit(f"refused: {name}: the unfolded matmul differs from the conv by {e}")
    return round(e, 7)


def run_resnet():
    import torch
    import torch.nn.functional as F
    from torchvision import models
    m = models.resnet18()
    m.load_state_dict(torch.load(os.path.join(ARGS.dl, "resnet18", MODELS["resnet18"]["file"]), map_location="cpu", weights_only=True))
    m.eval()
    ids = image_list()
    x = imagenet_batch(ids)
    cats = models.ResNet18_Weights.IMAGENET1K_V1.meta["categories"]
    with torch.no_grad():
        top = m(x).argmax(1).tolist()
    CAP["checks"]["resnet18_top1"] = {i: cats[t] for i, t in zip(ids, top)}
    log("resnet18 top-1", list(CAP["checks"]["resnet18_top1"].items())[:32])
    names = {"layer1_0_conv2": m.layer1[0].conv2, "layer1_1_conv1": m.layer1[1].conv1, "layer2_0_conv1": m.layer2[0].conv1, "layer2_1_conv2": m.layer2[1].conv2,
             "layer3_0_conv1": m.layer3[0].conv1, "layer3_1_conv1": m.layer3[1].conv1, "layer4_0_conv1": m.layer4[0].conv1, "layer4_1_conv2": m.layer4[1].conv2}
    grab = {}
    hs = []
    for n, c in names.items():
        hs.append(c.register_forward_pre_hook(lambda mod, inp, n=n: grab.__setitem__(n, inp[0].detach().clone())))
    nimg = 8
    with torch.no_grad():
        m(x[:nimg])
    for h in hs:
        h.remove()
    src = f"torchvision resnet18 IMAGENET1K_V1 ({MODELS['resnet18']['file']}), images: the first {nimg} of the shuffled NASA list: {ids[:nimg]}"
    for n, c in names.items():
        X = grab[n]
        U = F.unfold(X, kernel_size=c.kernel_size, dilation=c.dilation, padding=c.padding, stride=c.stride)
        A = U.permute(0, 2, 1).reshape(-1, U.shape[1]).numpy()
        B = c.weight.detach().flatten(1).T.numpy()
        e = check_conv(A, B, c, X, n)
        save(f"resnet18_{n}", A, B, f"ResNet-18 {n.replace('_', '.')}: A = the layer's input (post-ReLU) unfolded into {c.kernel_size[0]}x{c.kernel_size[1]} patches, rows = (image, patch in scan order), k = (channel, height, width) in F.unfold's order; B = the conv weight flattened the same way (k x out channels)", src, "activation", "weight", {"matmul_vs_conv_max_rel_err": e, "patches_per_image": int(U.shape[2]), "images": nimg})


def run_vgg():
    import torch
    from torchvision import models
    m = models.vgg16()
    m.load_state_dict(torch.load(os.path.join(ARGS.dl, "vgg16", MODELS["vgg16"]["file"]), map_location="cpu", weights_only=True))
    m.eval()
    ids = image_list()
    x = imagenet_batch(ids)
    grab = {}
    h1 = m.classifier[3].register_forward_pre_hook(lambda mod, inp: grab.__setitem__("fc2", inp[0].detach().clone()))
    h2 = m.classifier[6].register_forward_pre_hook(lambda mod, inp: grab.__setitem__("fc3", inp[0].detach().clone()))
    with torch.no_grad():
        y = m(x)
    h1.remove(); h2.remove()
    cats = models.VGG16_Weights.IMAGENET1K_V1.meta["categories"]
    CAP["checks"]["vgg16_top1"] = {i: cats[t] for i, t in zip(ids, y.argmax(1).tolist())}
    log("vgg16 top-1", list(CAP["checks"]["vgg16_top1"].items())[:32])
    src = f"torchvision vgg16 IMAGENET1K_V1 ({MODELS['vgg16']['file']}), images: 32 NASA images in the shuffled order (real2.json images.order)"
    for nm, cl, idx in (("fc2", m.classifier[3], 3), ("fc3", m.classifier[6], 6)):
        A = grab[nm].numpy()
        B = cl.weight.detach().T.numpy()
        with torch.no_grad():
            chk = cl(grab[nm])
        y2 = torch.tensor(A) @ torch.tensor(B) + cl.bias.detach()
        e = float((y2 - chk).abs().max() / chk.abs().max())
        if e > 2e-4:
            sys.exit(f"refused: vgg {nm} matmul differs {e}")
        save(f"vgg16_{nm}", A, B, f"VGG-16 classifier[{idx}]: A = its input, the previous fully connected layer's ReLU output (32 images x 4096), B = classifier[{idx}].weight transposed (4096 x {B.shape[1]})", src, "activation", "weight", {"matmul_vs_layer_max_rel_err": round(e, 7), "images": 32})


def run_t5():
    import torch
    from transformers import T5ForConditionalGeneration, T5TokenizerFast
    d = os.path.join(ARGS.dl, "t5-small")
    tok = T5TokenizerFast.from_pretrained(d, local_files_only=True)
    m = T5ForConditionalGeneration.from_pretrained(d, local_files_only=True, attn_implementation="eager").eval()
    with torch.no_grad():
        g = m.generate(**tok("translate English to German: The house is wonderful.", return_tensors="pt"), max_new_tokens=16)
    CAP["checks"]["t5_translation"] = tok.decode(g[0], skip_special_tokens=True)
    log("t5 translation:", CAP["checks"]["t5_translation"])
    enc = tok("summarize: " + TEXT, return_tensors="pt", truncation=True, max_length=128)
    n_tok = int(enc["input_ids"].shape[1])
    layers = (0, 2, 5)
    grab = {}
    hs = []
    for L in layers:
        ff = m.encoder.block[L].layer[1].DenseReluDense
        hs.append(ff.wo.register_forward_pre_hook(lambda mod, inp, L=L: grab.__setitem__(f"down{L}", inp[0].detach().clone())))
        hs.append(ff.wi.register_forward_pre_hook(lambda mod, inp, L=L: grab.__setitem__(f"up{L}", inp[0].detach().clone())))
    with torch.no_grad():
        m.encoder(**enc)
    for h in hs:
        h.remove()
    src = f"{MODELS['t5-small']['hf_repo']}@{MODELS['t5-small']['revision']}, text: 'summarize: ' + Pride and Prejudice, {n_tok} tokens"
    CAP["checks"]["t5_tokens"] = n_tok
    for L in layers:
        ff = m.encoder.block[L].layer[1].DenseReluDense
        A = grab[f"down{L}"][0].numpy()
        B = ff.wo.weight.detach().T.numpy()
        save(f"t5small_l{L}_ff_down", A, B, f"t5-small encoder block {L} feed-forward down-projection: A = the ReLU output (tokens x 2048), B = wo.weight transposed (2048 x 512)", src, "activation", "weight")
        A = grab[f"up{L}"][0].numpy()
        B = ff.wi.weight.detach().T.numpy()
        save(f"t5small_l{L}_ff_up", A, B, f"t5-small encoder block {L} feed-forward up-projection: A = its LayerNorm output (tokens x 512), B = wi.weight transposed (512 x 2048)", src, "activation", "weight")


def run_distilbert():
    import torch
    from transformers import DistilBertForMaskedLM, DistilBertTokenizerFast
    d = os.path.join(ARGS.dl, "distilbert")
    tok = DistilBertTokenizerFast.from_pretrained(d, local_files_only=True)
    m = DistilBertForMaskedLM.from_pretrained(d, local_files_only=True, attn_implementation="eager").eval()
    e = tok("The capital of France is [MASK].", return_tensors="pt")
    with torch.no_grad():
        lg = m(**e).logits
    pos = (e["input_ids"][0] == tok.mask_token_id).nonzero()[0, 0]
    CAP["checks"]["distilbert_fill_mask"] = [tok.decode(i) for i in lg[0, pos].topk(5).indices]
    log("distilbert fill-mask:", CAP["checks"]["distilbert_fill_mask"])
    enc = tok(TEXT, return_tensors="pt", truncation=True, max_length=128)
    n_tok = int(enc["input_ids"].shape[1])
    layers = (1, 3, 5)
    grab = {}
    hs = []
    for L in layers:
        ffn = m.distilbert.transformer.layer[L].ffn
        hs.append(ffn.lin2.register_forward_pre_hook(lambda mod, inp, L=L: grab.__setitem__(f"down{L}", inp[0].detach().clone())))
        hs.append(ffn.lin1.register_forward_pre_hook(lambda mod, inp, L=L: grab.__setitem__(f"up{L}", inp[0].detach().clone())))
    with torch.no_grad():
        m(**enc)
    for h in hs:
        h.remove()
    src = f"{MODELS['distilbert']['hf_repo']}@{MODELS['distilbert']['revision']}, text: Pride and Prejudice, {n_tok} tokens"
    CAP["checks"]["distilbert_tokens"] = n_tok
    for L in layers:
        ffn = m.distilbert.transformer.layer[L].ffn
        save(f"distilbert_l{L}_ff_down", grab[f"down{L}"][0].numpy(), ffn.lin2.weight.detach().T.numpy(), f"DistilBERT layer {L} feed-forward down-projection: A = the GELU output (tokens x 3072), B = lin2.weight transposed (3072 x 768)", src, "activation", "weight")
        save(f"distilbert_l{L}_ff_up", grab[f"up{L}"][0].numpy(), ffn.lin1.weight.detach().T.numpy(), f"DistilBERT layer {L} feed-forward up-projection: A = the attention block's output after LayerNorm (tokens x 768), B = lin1.weight transposed (768 x 3072)", src, "activation", "weight")


def run_bert():
    import torch
    from transformers import BertForMaskedLM, BertTokenizerFast
    d = os.path.join(ARGS.dl, "bert")
    tok = BertTokenizerFast.from_pretrained(d, local_files_only=True)
    m = BertForMaskedLM.from_pretrained(d, local_files_only=True, attn_implementation="eager").eval()
    e = tok("The capital of France is [MASK].", return_tensors="pt")
    with torch.no_grad():
        lg = m(**e).logits
    pos = (e["input_ids"][0] == tok.mask_token_id).nonzero()[0, 0]
    CAP["checks"]["bert_fill_mask"] = [tok.decode(i) for i in lg[0, pos].topk(5).indices]
    log("bert fill-mask:", CAP["checks"]["bert_fill_mask"])
    enc = tok(TEXT, return_tensors="pt", truncation=True, max_length=128)
    n_tok = int(enc["input_ids"].shape[1])
    layers = (2, 6, 11)
    grab = {}
    hs = []
    for L in layers:
        ly = m.bert.encoder.layer[L]
        hs.append(ly.output.dense.register_forward_pre_hook(lambda mod, inp, L=L: grab.__setitem__(f"down{L}", inp[0].detach().clone())))
        hs.append(ly.intermediate.dense.register_forward_pre_hook(lambda mod, inp, L=L: grab.__setitem__(f"up{L}", inp[0].detach().clone())))
    with torch.no_grad():
        m(**enc)
    for h in hs:
        h.remove()
    src = f"{MODELS['bert']['hf_repo']}@{MODELS['bert']['revision']}, text: Pride and Prejudice, {n_tok} tokens"
    CAP["checks"]["bert_tokens"] = n_tok
    for L in layers:
        ly = m.bert.encoder.layer[L]
        save(f"bert_l{L}_ff_down", grab[f"down{L}"][0].numpy(), ly.output.dense.weight.detach().T.numpy(), f"BERT layer {L} output.dense: A = the GELU output (tokens x 3072), B = output.dense.weight transposed (3072 x 768)", src, "activation", "weight")
        save(f"bert_l{L}_ff_up", grab[f"up{L}"][0].numpy(), ly.intermediate.dense.weight.detach().T.numpy(), f"BERT layer {L} intermediate.dense: A = the attention block's LayerNorm output (tokens x 768), B = intermediate.dense.weight transposed (768 x 3072)", src, "activation", "weight")


def run_vit():
    import torch
    from transformers import ViTForImageClassification
    d = os.path.join(ARGS.dl, "vit-b16")
    m = ViTForImageClassification.from_pretrained(d, local_files_only=True, attn_implementation="eager").eval()
    ids = image_list()
    x = vit_batch(ids)
    with torch.no_grad():
        top = m(x).logits.argmax(1).tolist()
    CAP["checks"]["vit_top1"] = {i: m.config.id2label[t] for i, t in zip(ids, top)}
    log("vit top-1", list(CAP["checks"]["vit_top1"].items())[:32])
    layers = (2, 5, 11)
    grab = {}
    hs = []
    for L in layers:
        ly = m.vit.encoder.layer[L]
        hs.append(ly.output.dense.register_forward_pre_hook(lambda mod, inp, L=L: grab.__setitem__(f"down{L}", inp[0].detach().clone())))
        hs.append(ly.intermediate.dense.register_forward_pre_hook(lambda mod, inp, L=L: grab.__setitem__(f"up{L}", inp[0].detach().clone())))
    nimg = 8
    with torch.no_grad():
        m(x[:nimg])
    for h in hs:
        h.remove()
    src = f"{MODELS['vit-b16']['hf_repo']}@{MODELS['vit-b16']['revision']}, images: the first {nimg} of the shuffled NASA list: {ids[:nimg]}"
    for L in layers:
        ly = m.vit.encoder.layer[L]
        A = grab[f"down{L}"].reshape(-1, 3072).numpy()
        save(f"vit_l{L}_ff_down", A, ly.output.dense.weight.detach().T.numpy(), f"ViT-B/16 layer {L} output.dense: A = the GELU output (images x 197 tokens x 3072, rows = (image, token)), B = output.dense.weight transposed (3072 x 768)", src, "activation", "weight", {"images": nimg, "tokens_per_image": 197})
        A = grab[f"up{L}"].reshape(-1, 768).numpy()
        save(f"vit_l{L}_ff_up", A, ly.intermediate.dense.weight.detach().T.numpy(), f"ViT-B/16 layer {L} intermediate.dense: A = the attention block's output after LayerNorm (rows = (image, token), 768), B = intermediate.dense.weight transposed (768 x 3072)", src, "activation", "weight", {"images": nimg, "tokens_per_image": 197})


def main():
    verify_models()
    CAP["build"] = {"python": platform.python_version(), "machine": platform.machine(), "numpy": np.__version__}
    CAP["images_order"] = image_list()
    if want("gpt2"):
        run_gpt2()
    import torch
    import torchvision
    import transformers
    torch.set_num_threads(ARGS.threads)
    CAP["build"].update({"torch": torch.__version__, "torchvision": torchvision.__version__, "transformers": transformers.__version__})
    for name, fn in (("resnet18", run_resnet), ("vgg16", run_vgg), ("t5", run_t5), ("distilbert", run_distilbert), ("bert", run_bert), ("vit", run_vit), ("gpt2half", run_gpt2_half)):
        if want(name):
            log("start", name)
            fn()
            json.dump(CAP, open(CAPF, "w"), indent=1)
    log("DONE capture")


if __name__ == "__main__":
    main()
