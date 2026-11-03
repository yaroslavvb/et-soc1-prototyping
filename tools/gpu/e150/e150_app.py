"""E150 - E149's frozen toggle model on a second, cheaper GPU type (L4 or A10G), under its own cap.

The registration is E150.md beside this file. This harness is E149's (tools/gpu/e149/e149_app.py) with only these
changes: the GPU type (a declared smoke on both an L4 and an A10G picks one by E150.md's rule), the sizes (passed in the
plan, chosen by E149's amendment A1 rule for that GPU's cap), a subset of E149's stage-1 kinds (phase L: the core
ladders), E149's 21 stage-2 kinds (phase H), both phases measured in one container per board, and shorter heat holds.
Everything here only reads the GPU (NVML getters and `nvidia-smi -q`); nothing is set on it.

    MODAL_PROFILE=yaroslavvb modal run e150_app.py --mode dry
    MODAL_PROFILE=yaroslavvb modal run e150_app.py --mode smoke --run-id <id>        # both GPU types, one each
    MODAL_PROFILE=yaroslavvb modal run --detach e150_app.py --mode main --gpu <L4|A10G> --sizes <json> --run-id <id>
    MODAL_PROFILE=yaroslavvb modal volume get e150-second-gpu /<id> <local dir>

No token, key or workspace secret is read or written here; Modal's client reads its own token from ~/.modal.toml.
"""
import gzip
import hashlib
import json
import math
import os
import subprocess
import sys
import time
import traceback

import modal

APP_NAME = "e150-second-gpu"
VOL_NAME = "e150-second-gpu"
GPU_TYPES = ("L4", "A10G")
PINS = {"python": "3.11", "torch": "2.5.1", "nvidia-ml-py": "12.560.30", "numpy": "2.1.3"}
# `modal billing rates`, read Mon 2 Nov 2026 21:46 PST on the Intel (workspace yaroslavvb)
RATE = {"gpu_h": {"L4": 0.80, "A10G": 1.10}, "cpu_core_h": 0.0473, "mem_gib_h": 0.008}
CPU_CORES = 2.0
MEM_MIB = 8192
SIZE = {"bf16": 2048, "fp16": 1024, "int8": 1024}   # replaced in the container by the plan's "sizes" (E150.md)
SMOKE_SIZES = (512, 1024, 1536, 2048)
TIMEOUT_S = {"S": 600, "M": 3300}
BUDGET_S = {"S": 480.0, "M": 3000.0}
WIN = {"cell_s": 5.0, "ref_s": 3.0, "cell_settle_s": 1.5, "ref_settle_s": 1.0, "group_ms": 20.0, "depth": 4,
       "sampler_period_s": 0.1}
HOLD = {"pre_s": 10.0, "hold_s": 30.0}
HEAT = {"idle_s": 30.0, "ref_hold_s": 120.0, "zeros_hold_s": 60.0}
LAGS = [1, 2, 4, 8, 16, 32]
ACC_PAIRS = 4096
ACC_BLOCK = 16

image = modal.Image.debian_slim(python_version=PINS["python"]).pip_install(
    f"torch=={PINS['torch']}", f"nvidia-ml-py=={PINS['nvidia-ml-py']}", f"numpy=={PINS['numpy']}")
app = modal.App(APP_NAME, image=image)
vol = modal.Volume.from_name(VOL_NAME, create_if_missing=True)

# ---------------------------------------------------------------------------------------------------------------
# The kinds (E149.md, "Stage 1" and "Stage 2"). A kind is (format, name, A spec, B spec). A is stored (M, K) and B
# (N, K), both K-contiguous, and the GEMM is A @ B.t(), as Horace He's mm_weird.py builds it. A spec's "seed" label,
# when given, is shared with every other spec carrying it (so a ladder's rungs, or sorted against shuffled, use the
# very same source values); the side (A or B) is always part of the seed.
BF1, BF15, BFM7 = 0x3F80, 0x3FC0, 0x3FFF          # bf16 1.0, 1.5, 1.9921875
FP1, FP15 = 0x3C00, 0x3E00                        # fp16 1.0, 1.5
BF_MANT, BF_EXP5 = (0, 7), (7, 5)                 # (lowest bit, width): bf16 mantissa, the exponent's low 5 bits
FP_MANT, FP_EXP3 = (0, 10), (10, 3)               # fp16 mantissa, the exponent's low 3 bits
I8_FLIP = (1, 7)                                  # int8 bits 1-7 (bit 0 stays 1 on the base 1, so no value is 0)


def S(**kw):
    return kw


def both(spec):
    return spec, dict(spec)


def _stage1():
    k = []
    rn = S(g="randn")
    # (a) the zero ladder, bf16, on one shared randn source
    src = S(g="randn", seed="zl-src")
    k.append(("bf16", "randn", *both(rn)))
    for f in (25, 50, 75, 90):
        k.append(("bf16", f"zs{f}", *both(S(g="zmask", src=src, frac=f / 100, block=1))))
    for f in (25, 50, 75, 90):
        k.append(("bf16", f"zb{f}", *both(S(g="zmask", src=src, frac=f / 100, block=64))))
    k.append(("bf16", "zeros", *both(S(g="zeros"))))
    k.append(("bf16", "zsA50", S(g="zmask", src=src, frac=0.5, block=1), dict(src)))
    k.append(("bf16", "zsB50", dict(src), S(g="zmask", src=src, frac=0.5, block=1)))
    # (b) Hamming ladders from the fixed base 1.0
    k.append(("bf16", "base1", *both(S(g="const", bits=BF1))))
    for kk in (1, 2, 3, 5, 7):
        k.append(("bf16", f"mk{kk}", *both(S(g="kflip", base=BF1, lo=BF_MANT[0], w=BF_MANT[1], k=kk))))
    for kk in (1, 2, 3, 5):
        k.append(("bf16", f"ek{kk}", *both(S(g="kflip", base=BF1, lo=BF_EXP5[0], w=BF_EXP5[1], k=kk))))
    for p in (10, 25, 50):
        k.append(("bf16", f"sp{p}", *both(S(g="bitp", base=BF1, pos=15, p=p / 100))))
    for pos in (0, 3, 6):
        k.append(("bf16", f"mb{pos}", *both(S(g="bitp", base=BF1, pos=pos, p=0.5))))
    for pos in (0, 4):
        k.append(("bf16", f"eb{pos}", *both(S(g="bitp", base=BF1, pos=BF_EXP5[0] + pos, p=0.5))))
    c1 = S(g="const", bits=BF1)
    k.append(("bf16", "mk3A", S(g="kflip", base=BF1, lo=BF_MANT[0], w=BF_MANT[1], k=3), dict(c1)))
    k.append(("bf16", "mk3B", dict(c1), S(g="kflip", base=BF1, lo=BF_MANT[0], w=BF_MANT[1], k=3)))
    k.append(("bf16", "ek2A", S(g="kflip", base=BF1, lo=BF_EXP5[0], w=BF_EXP5[1], k=2), dict(c1)))
    k.append(("bf16", "ek2B", dict(c1), S(g="kflip", base=BF1, lo=BF_EXP5[0], w=BF_EXP5[1], k=2)))
    # (c) signs: constant magnitude 1.5, random against fixed; and randn's magnitudes with fixed against random signs
    c15 = S(g="const", bits=BF15)
    k.append(("bf16", "sfix", *both(c15)))
    k.append(("bf16", "sfixAneg", S(g="const", bits=BF15 | 0x8000), dict(c15)))
    k.append(("bf16", "srand", *both(S(g="bitp", base=BF15, pos=15, p=0.5))))
    k.append(("bf16", "srandA", S(g="bitp", base=BF15, pos=15, p=0.5), dict(c15)))
    k.append(("bf16", "srandB", dict(c15), S(g="bitp", base=BF15, pos=15, p=0.5)))
    k.append(("bf16", "smagfix", *both(S(g="absval", src=S(g="randn", seed="mag-src")))))
    k.append(("bf16", "smagrand", *both(S(g="randsign", src=S(g="absval", src=S(g="randn", seed="mag-src"))))))
    # (d) order: the same values sorted along K against shuffled; along M; rolled; square waves along K
    osrc = S(g="randn", seed="order-src")
    k.append(("bf16", "dsortK", *both(S(g="sortK", src=osrc))))
    k.append(("bf16", "dshufK", *both(S(g="shufK", src=S(g="sortK", src=osrc)))))
    k.append(("bf16", "dabsK", *both(S(g="randsign", src=S(g="sortK", src=S(g="absval", src=osrc))))))
    k.append(("bf16", "dsortM", *both(S(g="sortM", src=osrc))))
    k.append(("bf16", "drollK", *both(S(g="rollK", src=S(g="sortK", src=osrc)))))
    for b in (1, 2, 4, 8, 16, 64):
        k.append(("bf16", f"sq{b}", *both(S(g="square", v0=BF1, v1=BFM7, block=b))))
    # fp16
    k.append(("fp16", "randn", *both(rn)))
    k.append(("fp16", "zeros", *both(S(g="zeros"))))
    fsrc = S(g="randn", seed="zl16-src")
    k.append(("fp16", "zs50", *both(S(g="zmask", src=fsrc, frac=0.5, block=1))))
    k.append(("fp16", "zs75", *both(S(g="zmask", src=fsrc, frac=0.75, block=1))))
    k.append(("fp16", "zb50", *both(S(g="zmask", src=fsrc, frac=0.5, block=64))))
    k.append(("fp16", "base1", *both(S(g="const", bits=FP1))))
    for kk in (1, 3, 5, 7, 10):
        k.append(("fp16", f"mk{kk}", *both(S(g="kflip", base=FP1, lo=FP_MANT[0], w=FP_MANT[1], k=kk))))
    for kk in (1, 2, 3):
        k.append(("fp16", f"ek{kk}", *both(S(g="kflip", base=FP1, lo=FP_EXP3[0], w=FP_EXP3[1], k=kk))))
    for p in (25, 50):
        k.append(("fp16", f"sp{p}", *both(S(g="bitp", base=FP1, pos=15, p=p / 100))))
    k.append(("fp16", "sp50A", S(g="bitp", base=FP1, pos=15, p=0.5), S(g="const", bits=FP1)))
    for pos in (0, 5, 9):
        k.append(("fp16", f"mb{pos}", *both(S(g="bitp", base=FP1, pos=pos, p=0.5))))
    k.append(("fp16", "mk5A", S(g="kflip", base=FP1, lo=FP_MANT[0], w=FP_MANT[1], k=5), S(g="const", bits=FP1)))
    # (e) int8 (torch._int_mm)
    r8 = S(g="randint8")
    k.append(("int8", "rand", *both(r8)))
    k.append(("int8", "zeros", *both(S(g="zeros"))))
    isrc = S(g="randint8", seed="zl8-src")
    for f in (25, 50, 75, 90):
        k.append(("int8", f"zs{f}", *both(S(g="zmask", src=isrc, frac=f / 100, block=1))))
    k.append(("int8", "zb50", *both(S(g="zmask", src=isrc, frac=0.5, block=64))))
    k.append(("int8", "base1", *both(S(g="const", bits=1))))
    for kk in (1, 2, 3, 5, 7):
        k.append(("int8", f"k{kk}", *both(S(g="kflip", base=1, lo=I8_FLIP[0], w=I8_FLIP[1], k=kk))))
    k.append(("int8", "low", *both(S(g="groupp", base=1, bits=[1, 2, 3], p=0.5))))
    k.append(("int8", "high", *both(S(g="groupp", base=1, bits=[4, 5, 6], p=0.5))))
    k.append(("int8", "sign", *both(S(g="groupp", base=1, bits=[7], p=0.5))))
    k.append(("int8", "signA", S(g="groupp", base=1, bits=[7], p=0.5), S(g="const", bits=1)))
    k.append(("int8", "randA", dict(r8), S(g="const", bits=1)))
    k.append(("int8", "randB", S(g="const", bits=1), dict(r8)))
    return k


def _stage2():
    """The held-out kinds: registered with stage 1, measured only in stage 2, after the model's freeze."""
    k = []
    for fmt in ("bf16",):
        k.append((fmt, "zeros", *both(S(g="zeros"))))
        k.append((fmt, "randn", *both(S(g="randn"))))
        k.append((fmt, "rand", *both(S(g="rand"))))
        k.append((fmt, "sparse75", *both(S(g="sparse75"))))
        k.append((fmt, "ternary", *both(S(g="ternary"))))
        k.append((fmt, "onebit", *both(S(g="onebit"))))
        k.append((fmt, "pi", *both(S(g="constf", v=3.1415926535897932384626))))
        k.append((fmt, "twos", *both(S(g="constf", v=2.0))))
        k.append((fmt, "checker", *both(S(g="checker"))))
        k.append((fmt, "gelu_w", S(g="gelu"), S(g="llmw")))
        k.append((fmt, "powerlaw", *both(S(g="powerlaw"))))
        k.append((fmt, "lowrank", *both(S(g="lowrank"))))
        k.append((fmt, "sortrand", *both(S(g="sortK", src=S(g="rand")))))
        k.append((fmt, "sparse_neg", *both(S(g="sparse_neg"))))
    k.append(("fp16", "zeros", *both(S(g="zeros"))))
    k.append(("fp16", "rand", *both(S(g="rand"))))
    k.append(("fp16", "gelu_w", S(g="gelu"), S(g="llmw")))
    k.append(("int8", "zeros", *both(S(g="zeros"))))
    k.append(("int8", "q_gelu_w", S(g="qgelu"), S(g="qllmw")))
    k.append(("int8", "ternary", *both(S(g="ternary"))))
    k.append(("int8", "twos", *both(S(g="const", bits=2))))
    return k


def kid(k):
    return f"{k[0]}.{k[1]}"


STAGE1 = _stage1()
STAGE2 = _stage2()
# E150.md "Phase L": E149's core ladders (zeros, the mantissa/exponent/sign ladders, single positions, one-sided rungs,
# signs, order and square waves), every one an E149 stage-1 kind with E149's spec and seed labels.
L_NAMES = {
    "bf16": ["randn", "zs25", "zs50", "zs75", "zs90", "zb50", "zb75", "zeros", "base1", "mk1", "mk3", "mk5", "mk7",
             "ek1", "ek3", "ek5", "sp10", "sp25", "sp50", "mb0", "mb6", "eb0", "eb4", "mk3A", "mk3B", "sfix",
             "sfixAneg", "srand", "dsortK", "dshufK", "dsortM", "drollK", "sq1", "sq4", "sq16", "sq64"],
    "fp16": ["randn", "zeros", "zs50", "zs75", "zb50", "base1", "mk1", "mk3", "mk5", "mk7", "mk10", "ek1", "ek3",
             "sp50", "sp50A", "mb0", "mb9", "mk5A"],
    "int8": ["rand", "zeros", "zs25", "zs50", "zs75", "zs90", "zb50", "base1", "k1", "k3", "k5", "k7", "low", "high",
             "sign", "signA", "randA", "randB"]}
_by = {kid(k): k for k in STAGE1}
PHASE_L = [_by[f"{f}.{n}"] for f, ns in L_NAMES.items() for n in ns]
PHASE_H = [k for k in STAGE2 if kid(k) != "bf16.randn"]       # E149's held-out kinds (17 blind) and the zeros anchors
REF = ("bf16", "REF", S(g="randn"), S(g="randn"))
ANCHOR_EXTRA = {"L": [("bf16", "zeros"), ("fp16", "zeros"), ("int8", "zeros")],
                "H": [("bf16", "zeros"), ("fp16", "zeros"), ("int8", "zeros")]}
RAND_SPEC = {"bf16": S(g="randn"), "fp16": S(g="randn"), "int8": S(g="randint8")}
STAGE_S = ([(f, f"rand@{n}", dict(RAND_SPEC[f]), dict(RAND_SPEC[f])) for n in SMOKE_SIZES for f in RAND_SPEC] +
           [(f, f"zeros@{n}", S(g="zeros"), S(g="zeros")) for n in SMOKE_SIZES for f in RAND_SPEC])


def _seed(label):
    return int(hashlib.sha256(label.encode()).hexdigest()[:12], 16)


# ---------------------------------------------------------------------------------------------------------------
# Building operands on the GPU from a spec. Every random draw uses its own torch.Generator seeded from a label, so the
# same kind gives the same bytes in every container (checked by sha256 in stage 2).
def _to16(torch, v32):
    v32 = v32 & 0xFFFF
    return torch.where(v32 >= 0x8000, v32 - 0x10000, v32).to(torch.int16)


def _to8(torch, v32):
    v32 = v32 & 0xFF
    return torch.where(v32 >= 0x80, v32 - 0x100, v32).to(torch.int8)


def _kmask(torch, shape, lo, w, k, g):
    if k == 0:
        return torch.zeros(shape, dtype=torch.int32, device="cuda")
    if k == w:
        return torch.full(shape, ((1 << w) - 1) << lo, dtype=torch.int32, device="cuda")
    n = shape[0] * shape[1]
    r = torch.rand((n, w), generator=g, device="cuda")
    idx = torch.topk(r, k, dim=1, largest=False).indices
    wts = torch.tensor([1 << (lo + i) for i in range(w)], dtype=torch.int32, device="cuda")
    return wts[idx].sum(dim=1, dtype=torch.int32).view(shape)


def build(torch, spec, fmt, shape, label):
    """One operand (rows, K) in format fmt. label = '<default seed label>'; a spec's own 'seed' overrides it."""
    side = label.rsplit("/", 1)[-1]
    lab = (f"e149/{fmt}/{spec['seed']}/{side}" if "seed" in spec else label)
    g = torch.Generator(device="cuda")
    g.manual_seed(_seed(lab))
    g2 = torch.Generator(device="cuda")
    g2.manual_seed(_seed(label + "/x"))
    t = spec["g"]
    dev = "cuda"
    R, K = shape
    if fmt == "int8":
        if t == "zeros":
            return torch.zeros(shape, dtype=torch.int8, device=dev)
        if t == "randint8":
            return torch.randint(-128, 128, shape, generator=g, dtype=torch.int8, device=dev)
        if t == "const":
            return _to8(torch, torch.full(shape, spec["bits"], dtype=torch.int32, device=dev))
        if t == "kflip":
            m = _kmask(torch, shape, spec["lo"], spec["w"], spec["k"], g2)
            return _to8(torch, spec["base"] ^ m)
        if t == "groupp":
            m = torch.zeros(shape, dtype=torch.int32, device=dev)
            for b in spec["bits"]:
                m |= (torch.rand(shape, generator=g2, device=dev) < spec["p"]).to(torch.int32) << b
            return _to8(torch, spec["base"] ^ m)
        if t == "zmask":
            X = build(torch, spec["src"], fmt, shape, label)
            return _zmask(torch, X, spec, g2)
        if t == "ternary":
            return torch.randint(-1, 2, shape, generator=g, dtype=torch.int8, device=dev)
        if t == "qgelu":
            x = torch.nn.functional.gelu(torch.randn(shape, generator=g, device=dev))
            s = x.abs().max() / 127.0
            return torch.clamp(torch.round(x / s), -127, 127).to(torch.int8)
        if t == "qllmw":
            w = _tdist(torch, shape, g) * 0.02
            s = w.abs().amax(dim=1, keepdim=True) / 127.0
            return torch.clamp(torch.round(w / s), -127, 127).to(torch.int8)
        raise ValueError(f"int8 {t}")
    dt = {"bf16": torch.bfloat16, "fp16": torch.float16}[fmt]
    if t == "zeros":
        return torch.zeros(shape, dtype=dt, device=dev)
    if t == "randn":
        return torch.randn(shape, generator=g, dtype=dt, device=dev)
    if t == "rand":
        return torch.rand(shape, generator=g, dtype=dt, device=dev)
    if t == "const":
        return _to16(torch, torch.full(shape, spec["bits"], dtype=torch.int32, device=dev)).view(dt)
    if t == "constf":
        return torch.full(shape, spec["v"], dtype=dt, device=dev)
    if t == "kflip":
        m = _kmask(torch, shape, spec["lo"], spec["w"], spec["k"], g2)
        return _to16(torch, spec["base"] ^ m).view(dt)
    if t == "bitp":
        m = (torch.rand(shape, generator=g2, device=dev) < spec["p"]).to(torch.int32) << spec["pos"]
        return _to16(torch, spec["base"] ^ m).view(dt)
    if t == "zmask":
        X = build(torch, spec["src"], fmt, shape, label)
        return _zmask(torch, X, spec, g2)
    if t == "absval":
        return build(torch, spec["src"], fmt, shape, label).abs()
    if t == "randsign":
        X = build(torch, spec["src"], fmt, shape, label)
        neg = torch.rand(shape, generator=g2, device=dev) < 0.5
        return torch.where(neg, -X, X)
    if t == "sortK":
        X = build(torch, spec["src"], fmt, shape, label)
        return torch.sort(X.float(), dim=1).values.to(dt)
    if t == "sortM":
        X = build(torch, spec["src"], fmt, shape, label)
        return torch.sort(X.float(), dim=0).values.to(dt)
    if t == "shufK":
        X = build(torch, spec["src"], fmt, shape, label)
        idx = torch.argsort(torch.rand(shape, generator=g2, device=dev), dim=1)
        return torch.gather(X, 1, idx)
    if t == "rollK":
        X = build(torch, spec["src"], fmt, shape, label)
        off = torch.randint(0, K, (R, 1), generator=g2, device=dev)
        idx = (torch.arange(K, device=dev).view(1, -1) + off) % K
        return torch.gather(X, 1, idx)
    if t == "square":
        b = spec["block"]
        ph = torch.randint(0, 2 * b, (R, 1), generator=g2, device=dev)
        hi = ((torch.arange(K, device=dev).view(1, -1) + ph) // b) % 2 == 1
        v0 = _to16(torch, torch.tensor(spec["v0"], device=dev)).view(dt)
        v1 = _to16(torch, torch.tensor(spec["v1"], device=dev)).view(dt)
        return torch.where(hi, v1, v0)
    if t == "sparse75":                      # Horace He's post: a random 75% masked (mask drawn in fp32)
        x = torch.randn(shape, generator=g, dtype=dt, device=dev)
        keep = torch.rand(shape, generator=g2, device=dev) >= 0.75
        return torch.where(keep, x, torch.zeros((), dtype=dt, device=dev))
    if t == "sparse_neg":                    # his mm_weird.py: the negative half zeroed
        x = torch.randn(shape, generator=g, dtype=dt, device=dev)
        return torch.where(x < 0, torch.zeros((), dtype=dt, device=dev), x)
    if t == "ternary":
        return torch.randint(-1, 2, shape, generator=g, device=dev).to(dt)
    if t == "onebit":                        # his code: (randn.view(int16) & 0b1000) converted, so 0.0 or 8.0
        x = torch.randn(shape, generator=g, dtype=dt, device=dev)
        return (x.view(torch.int16) & 0b1000).to(dt)
    if t == "checker":                       # randn with every element where (i - j) is odd set to 0
        x = torch.randn(shape, generator=g, dtype=dt, device=dev)
        par = (torch.arange(R, device=dev).view(-1, 1) - torch.arange(K, device=dev).view(1, -1)) % 2 == 0
        return torch.where(par, x, torch.zeros((), dtype=dt, device=dev))
    if t == "gelu":                          # post-GELU activations of unit-normal pre-activations
        return torch.nn.functional.gelu(torch.randn(shape, generator=g, device=dev)).to(dt)
    if t == "llmw":                          # LLM-like weights: Student-t (5 dof) x 0.02
        return (_tdist(torch, shape, g) * 0.02).to(dt)
    if t == "powerlaw":                      # Pareto magnitudes (alpha 1.5, shifted to start at 0), random signs
        u = torch.rand(shape, generator=g, device=dev).clamp_min(1e-12)
        mag = (u.pow(-1.0 / 1.5) - 1.0).clamp_max(1.0e4)
        neg = torch.rand(shape, generator=g2, device=dev) < 0.5
        return torch.where(neg, -mag, mag).to(dt)
    if t == "lowrank":                       # rank 16, unit-variance entries
        U = torch.randn((R, 16), generator=g, device=dev)
        V = torch.randn((16, K), generator=g2, device=dev)
        return (U @ V / 4.0).to(dt)
    raise ValueError(f"{fmt} {t}")


def _tdist(torch, shape, g, dof=5):
    z = torch.randn(shape, generator=g, device="cuda")
    c = torch.zeros(shape, device="cuda")
    for _ in range(dof):
        c += torch.randn(shape, generator=g, device="cuda") ** 2
    return z / torch.sqrt(c / dof)


def _zmask(torch, X, spec, g2):
    f, b = spec["frac"], spec["block"]
    R, K = X.shape
    if b == 1:
        z = torch.rand(X.shape, generator=g2, device="cuda") < f
    else:
        z = (torch.rand((R, K // b), generator=g2, device="cuda") < f).repeat_interleave(b, dim=1)
    return torch.where(z, torch.zeros((), dtype=X.dtype, device="cuda"), X)


def size_of(k):
    """A kind's M = N = K: SIZE[fmt], or the '@n' suffix of its name (the size smoke S2 only)."""
    return int(k[1].split('@')[1]) if '@' in k[1] else SIZE[k[0]]


def make_pair(torch, k, n=None):
    fmt, name, sa, sb = k
    n = size_of(k) if n is None else n
    A = build(torch, sa, fmt, (n, n), f"e149/{fmt}/{name}/A")
    Bs = build(torch, sb, fmt, (n, n), f"e149/{fmt}/{name}/B")
    return A.contiguous(), Bs.contiguous()


def sha(torch, X):
    return hashlib.sha256(X.contiguous().view(torch.uint8).cpu().numpy().tobytes()).hexdigest()


# ---------------------------------------------------------------------------------------------------------------
# Features from the operand bits (E149.md, "The model"). X is (rows, K) as stored. Every flip is counted between two
# operands of one row: K-lag s (s = 1 is "consecutive along K", the ET-SoC-1 model's form) or the next row at the
# same k (the row direction: M for A, N for B).
def _bits(torch, X, fmt):
    if fmt == "int8":
        return X.view(torch.uint8).to(torch.int32), 8
    return X.view(torch.int16).to(torch.int32) & 0xFFFF, 16


def side_feats(torch, X, fmt):
    I, W = _bits(torch, X, fmt)
    out = {"ones": [], "row": []}
    for s in LAGS:
        out[f"lag{s}"] = []
    for p in range(W):
        b = ((I >> p) & 1).to(torch.uint8)
        out["ones"].append(float(b.float().mean()))
        for s in LAGS:
            out[f"lag{s}"].append(float((b[:, s:] ^ b[:, :-s]).float().mean()))
        out["row"].append(float((b[1:, :] ^ b[:-1, :]).float().mean()))
        del b
    nz = (X != 0)
    sb = ((I >> (W - 1)) & 1).to(torch.uint8)
    vec = {"nz_k": nz.float().mean(dim=0), "sg_k": sb.float().mean(dim=0)}
    for s in LAGS:
        vec[f"nzc{s}_k"] = (nz[:, s:] & nz[:, :-s]).float().mean(dim=0)
        vec[f"sf{s}_k"] = (sb[:, s:] ^ sb[:, :-s]).float().mean(dim=0)
    Y = X.float()
    out["stats"] = {"frac_zero": float((Y == 0).float().mean()), "mean": float(Y.mean()), "std": float(Y.std()),
                    "min": float(Y.min()), "max": float(Y.max()), "frac_neg": float((Y < 0).float().mean()),
                    "finite": bool(torch.isfinite(Y).all())}
    return out, vec


def cross_feats(torch, va, vb):
    out = {"nzprod": float((va["nz_k"] * vb["nz_k"]).mean()),
           "negprod": float((va["sg_k"] * (1 - vb["sg_k"]) + (1 - va["sg_k"]) * vb["sg_k"]).mean())}
    for s in LAGS:
        fa, fb = va[f"sf{s}_k"], vb[f"sf{s}_k"]
        out[f"psgn{s}"] = float((fa * (1 - fb) + (1 - fa) * fb).mean())
        za, zb = va["nz_k"], vb["nz_k"]
        both_now = za[:-s] * zb[:-s]
        both_next = za[s:] * zb[s:]
        stay = va[f"nzc{s}_k"] * vb[f"nzc{s}_k"]
        out[f"gtr{s}"] = float((both_now + both_next - 2 * stay).mean())
    return out


def acc_feats(torch, A, Bs, fmt, seed_label):
    """Flips of the fp32 (int32 for int8) running sum between consecutive 16-k blocks, for ACC_PAIRS sampled (i, j)."""
    g = torch.Generator(device="cuda")
    g.manual_seed(_seed(seed_label))
    n, K = A.shape
    ii = torch.randint(0, n, (ACC_PAIRS,), generator=g, device="cuda")
    jj = torch.randint(0, Bs.shape[0], (ACC_PAIRS,), generator=g, device="cuda")
    if fmt == "int8":
        prod = A[ii].to(torch.int32) * Bs[jj].to(torch.int32)
        blk = prod.view(ACC_PAIRS, K // ACC_BLOCK, ACC_BLOCK).sum(dim=2, dtype=torch.int32)
        run = torch.cumsum(blk, dim=1, dtype=torch.int32)
        bits = run
    else:
        prod = A[ii].float() * Bs[jj].float()
        blk = prod.view(ACC_PAIRS, K // ACC_BLOCK, ACC_BLOCK).sum(dim=2)
        run = torch.cumsum(blk, dim=1)
        bits = run.view(torch.int32)
    x = bits[:, 1:] ^ bits[:, :-1]
    per = []
    for p in range(32):
        per.append(float(((x >> p) & 1).float().mean()) / ACC_BLOCK)
    return {"acc_pos": per, "acc": sum(per), "acc_finite": bool(torch.isfinite(run.float()).all())}


def kind_feats(torch, k, A, Bs):
    fmt = k[0]
    fa, va = side_feats(torch, A, fmt)
    fb, vb = side_feats(torch, Bs, fmt)
    cr = cross_feats(torch, va, vb)
    ac = acc_feats(torch, A, Bs, fmt, f"e149/acc/{kid(k)}")
    return {"kind": kid(k), "fmt": fmt, "A": fa, "B": fb, "cross": cr, "acc": ac,
            "spec": {"A": k[2], "B": k[3]}, "sha_A": sha(torch, A), "sha_B": sha(torch, Bs)}


# ---------------------------------------------------------------------------------------------------------------
# The NVML sampler: its own process. Getters only (E135's, unchanged).
SAMPLER_SRC = r'''
import json, os, sys, time
import pynvml as N

out_path, stop_path, period = sys.argv[1], sys.argv[2], float(sys.argv[3])
N.nvmlInit()
h = N.nvmlDeviceGetHandleByIndex(0)

def _reasons():
    f = getattr(N, "nvmlDeviceGetCurrentClocksEventReasons", None) or N.nvmlDeviceGetCurrentClocksThrottleReasons
    return f(h)

CALLS = [
    ("sm", lambda: N.nvmlDeviceGetClockInfo(h, N.NVML_CLOCK_SM)),
    ("mem", lambda: N.nvmlDeviceGetClockInfo(h, N.NVML_CLOCK_MEM)),
    ("p_mw", lambda: N.nvmlDeviceGetPowerUsage(h)),
    ("e_mj", lambda: N.nvmlDeviceGetTotalEnergyConsumption(h)),
    ("temp", lambda: N.nvmlDeviceGetTemperature(h, N.NVML_TEMPERATURE_GPU)),
    ("rsn", _reasons),
    ("plim_mw", lambda: N.nvmlDeviceGetEnforcedPowerLimit(h)),
    ("pstate", lambda: N.nvmlDeviceGetPerformanceState(h)),
    ("util", lambda: (lambda u: [u.gpu, u.memory])(N.nvmlDeviceGetUtilizationRates(h))),
]
FIELDS = [("p_inst_mw", 186), ("t_mem", 82)]

def _fv(v):
    u = v.value
    get = {0: lambda: u.dVal, 1: lambda: u.uiVal, 2: lambda: u.ulVal, 3: lambda: u.ullVal, 4: lambda: u.sllVal}
    return get.get(v.valueType, lambda: None)()

dead, errs = {}, {}
f = open(out_path, "a", buffering=1)
f.write(json.dumps({"status": "start", "t": time.time(), "period": period}) + "\n")
nxt = time.time()
n = 0
while not os.path.exists(stop_path):
    ta = time.time()
    rec = {"t": round(ta, 4)}
    for k, fn in CALLS:
        if k in dead:
            continue
        try:
            rec[k] = fn()
        except N.NVMLError as e:
            if e.value == N.NVML_ERROR_NOT_SUPPORTED:
                dead[k] = str(e)
            else:
                errs[k] = errs.get(k, 0) + 1
            rec[k] = None
        except Exception:
            errs[k] = errs.get(k, 0) + 1
            rec[k] = None
    if "fields" not in dead:
        try:
            vals = N.nvmlDeviceGetFieldValues(h, [fid for _, fid in FIELDS])
            for (k, _), v in zip(FIELDS, vals):
                rec[k] = _fv(v) if v.nvmlReturn == 0 else None
        except Exception as e:
            dead["fields"] = repr(e)
    rec["tb"] = round(time.time(), 4)
    f.write(json.dumps(rec) + "\n")
    n += 1
    if n == 1 or n % 3000 == 0:
        f.write(json.dumps({"status": "health", "n": n, "dead": dead, "errs": errs, "t": time.time()}) + "\n")
    nxt += period
    d = nxt - time.time()
    if d > 0:
        time.sleep(d)
    else:
        nxt = time.time()
f.write(json.dumps({"status": "end", "n": n, "dead": dead, "errs": errs, "t": time.time()}) + "\n")
f.close()
'''


def _s(x):
    return x.decode() if isinstance(x, bytes) else str(x)


def _wjson_gz(path, obj):
    with gzip.open(path, "wt", encoding="utf-8") as f:
        json.dump(obj, f, separators=(",", ":"))


def _wjson(path, obj):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, indent=1)


def _scrub(text):
    out = []
    for line in text.splitlines():
        key = line.split(":", 1)[0]
        if any(w in key for w in ("UUID", "Serial Number", "GPU PDI", "Board ID", "Bus Id", "Bus")):
            out.append(key + ": [scrubbed]")
        else:
            out.append(line)
    return "\n".join(out)


# ---------------------------------------------------------------------------------------------------------------
# The plans. A pass = REF, then (cell, REF) for every kind in the pass's order; each format's zeros also runs at the
# start, middle and end of a pass (the anchors). Unit A runs the passes forward then reversed, unit B the reverse.
def pass_order(kinds, stage, unit, p, fmts=("bf16", "fp16", "int8")):
    ids = [kid(k) for k in kinds if k[0] in fmts]
    anchors = [f"{f}.{n}" for f, n in ANCHOR_EXTRA[stage] if f in fmts]
    import random as _r
    rnd = _r.Random(_seed(f"e150/order/{stage}"))
    body = list(ids)
    rnd.shuffle(body)
    mid = len(body) // 2
    seq = anchors + body[:mid] + anchors + body[mid:] + anchors
    fwd = (unit == "A") == (p % 2 == 1)
    return seq if fwd else list(reversed(seq))


def plan(stage, unit, sizes=None):
    """stage "S": the declared smoke (one container per GPU type); stage "M": the measured run (one per board)."""
    if stage == "S":
        seq = [kid(k) for k in sorted(STAGE_S, key=lambda k: (size_of(k), k[1].startswith("zeros"), k[0]))]
        return {"stage": "S", "unit": unit, "sizes": {"bf16": 512, "fp16": 512, "int8": 512},
                "steps": [{"op": "static"}, {"op": "gen", "set": "S"}, {"op": "idle", "s": 10.0},
                          {"op": "hold", "kind": "bf16.rand@1024", "s": 45.0, "label": "warm"},
                          {"op": "pass", "p": 1, "seq": seq}, {"op": "idle", "s": 5.0}]}
    if stage == "M":
        steps = [{"op": "static"}, {"op": "gen", "set": "M"}, {"op": "idle", "s": HEAT["idle_s"]},
                 {"op": "hold", "kind": "bf16.REF", "s": HEAT["ref_hold_s"], "label": "heat_ref"},
                 {"op": "hold", "kind": "bf16.zeros", "s": HEAT["zeros_hold_s"], "label": "heat_zeros"}]
        fm = tuple(f for f in ("bf16", "fp16", "int8") if f in (sizes or SIZE))   # a dropped format runs nothing
        for p in (1, 2):
            steps.append({"op": "pass", "p": p, "seq": pass_order(PHASE_L, "L", unit, p, fm)})
        for p in (3, 4):
            steps.append({"op": "pass", "p": p, "seq": pass_order(PHASE_H, "H", unit, p, fm)})
        hold_ids = [kid(k) for k in STAGE2 if k[1] != "zeros" and k[0] in fm]
        if unit == "B":
            hold_ids = list(reversed(hold_ids))
        steps.append({"op": "holds", "seq": hold_ids, "pre_s": HOLD["pre_s"], "hold_s": HOLD["hold_s"]})
        steps.append({"op": "idle", "s": 20.0})
        return {"stage": "M", "unit": unit, "sizes": dict(sizes or SIZE), "steps": steps}
    raise ValueError(stage)


def step_seconds(st):
    op = st["op"]
    if op == "static":
        return 40.0
    if op == "gen":
        return {"S": 20.0, "M": 60.0}[st["set"]]
    if op == "idle":
        return st["s"] + 2.0
    if op == "hold":
        return st["s"] + 1.0
    if op == "pass":
        return WIN["ref_s"] + len(st["seq"]) * (WIN["cell_s"] + WIN["ref_s"] + 0.25)
    if op == "holds":
        return len(st["seq"]) * (st["pre_s"] + st["hold_s"] + 0.5)
    if op == "feat2":
        return 60.0
    return 60.0


def dollars(seconds, gpu):
    per_h = RATE["gpu_h"][gpu] + CPU_CORES * RATE["cpu_core_h"] + MEM_MIB / 1024 * RATE["mem_gib_h"]
    return seconds / 3600.0 * per_h, per_h


# ---------------------------------------------------------------------------------------------------------------
class Unit:
    def __init__(self, run_id, pl, budget_s):
        import pynvml
        self.N = pynvml
        self.N.nvmlInit()
        self.h = self.N.nvmlDeviceGetHandleByIndex(0)
        self.run_id, self.plan, self.unit, self.stage = run_id, pl, pl["unit"], pl["stage"]
        self.budget_s = budget_s
        self.root = f"/vol/{run_id}/{self.unit}"
        self.t_fn = time.time()
        self.step_i = 0
        self.chunk = 0
        self.samp_off = 0
        self.samp_path = "/tmp/e150_samples.jsonl"
        self.stop_path = "/tmp/e150_sampler.stop"
        self.ops = {}
        self.torch = None
        self.skipped = []

    def elapsed(self):
        return time.time() - self.t_fn

    def flush_samples(self):
        try:
            with open(self.samp_path, "rb") as f:
                f.seek(self.samp_off)
                data = f.read()
        except FileNotFoundError:
            return
        cut = data.rfind(b"\n") + 1
        if cut <= 0:
            return
        with gzip.open(f"{self.root}/samples/{self.chunk:03d}.jsonl.gz", "wb") as g:
            g.write(data[:cut])
        self.chunk += 1
        self.samp_off += cut

    def mm_for(self, kname):
        torch = self.torch
        A, Bt, C, fmt = self.ops[kname]
        if fmt == "int8":
            return lambda: torch._int_mm(A, Bt, out=C)
        return lambda: torch.mm(A, Bt, out=C)

    def window(self, kname, secs):
        """Back-to-back calls of one kind for secs, a CUDA event after every group; host times bracket it."""
        torch = self.torch
        fn = self.mm_for(kname)
        grp = self.ops[kname + "#grp"]
        evs = []
        pend = []
        torch.cuda.synchronize()
        e0 = torch.cuda.Event(enable_timing=True)
        t_a = time.time()
        e0.record()
        n = 0
        while True:
            for _ in range(grp):
                fn()
            n += grp
            e = torch.cuda.Event(enable_timing=True)
            e.record()
            evs.append(e)
            pend.append(e)
            if len(pend) > WIN["depth"]:
                pend.pop(0).synchronize()
                if time.time() - t_a >= secs:
                    break
        torch.cuda.synchronize()
        t_b = time.time()
        gpu_ms = e0.elapsed_time(evs[-1])
        return {"kind": kname, "t_a": t_a, "t_b": t_b, "calls": n, "group": grp, "gpu_ms": round(gpu_ms, 3),
                "n": self.ops[kname + "#n"]}

    def run_step(self, st):
        need = step_seconds(st)
        if st["op"] not in ("static", "gen", "feat2") and self.elapsed() + need > self.budget_s:
            self.skipped.append({"step": st.get("label") or st["op"], "elapsed_s": self.elapsed()})
            print(f"[{self.unit}] SKIP (budget) {st.get('label') or st['op']}", flush=True)
            return
        i = self.step_i
        self.step_i += 1
        label = st.get("label") or (f"pass{st['p']}" if st["op"] == "pass" else st["op"])
        t_a = time.time()
        try:
            rec = getattr(self, "step_" + st["op"])(st)
        except Exception:
            rec = {"error": traceback.format_exc()}
        rec.update({"i": i, "op": st["op"], "label": label, "unit": self.unit, "stage": self.stage,
                    "t_step_a": t_a, "t_step_b": time.time(),
                    "step": {k: v for k, v in st.items() if k != "seq"}, "seq": st.get("seq")})
        _wjson_gz(f"{self.root}/steps/{i:03d}_{label}.json.gz", rec)
        self.flush_samples()
        vol.commit()
        print(f"[{self.unit}] {i:03d} {label:<16} {time.time() - t_a:7.1f} s {rec.get('brief', '')}"
              f"{'  ERROR' if rec.get('error') else ''}", flush=True)
        if rec.get("error"):
            print(rec["error"][-2000:], flush=True)

    def step_static(self, st):
        N, h, info = self.N, self.h, {}

        def g(name, fn):
            try:
                info[name] = fn()
            except Exception as e:
                info[name] = f"ERR {type(e).__name__}: {e}"
        g("name", lambda: _s(N.nvmlDeviceGetName(h)))
        g("driver", lambda: _s(N.nvmlSystemGetDriverVersion()))
        g("vbios", lambda: _s(N.nvmlDeviceGetVbiosVersion(h)))
        g("uuid_sha12", lambda: hashlib.sha256(_s(N.nvmlDeviceGetUUID(h)).encode()).hexdigest()[:12])
        g("power_default_mw", lambda: N.nvmlDeviceGetPowerManagementDefaultLimit(h))
        g("power_enforced_mw", lambda: N.nvmlDeviceGetEnforcedPowerLimit(h))
        for nm, c in (("sm", N.NVML_CLOCK_SM), ("mem", N.NVML_CLOCK_MEM)):
            g(f"max_clock_{nm}", lambda c=c: N.nvmlDeviceGetMaxClockInfo(h, c))
            g(f"app_clock_{nm}", lambda c=c: N.nvmlDeviceGetApplicationsClock(h, c))
        for nm, c in (("slowdown", N.NVML_TEMPERATURE_THRESHOLD_SLOWDOWN),
                      ("gpu_max", N.NVML_TEMPERATURE_THRESHOLD_GPU_MAX)):
            g(f"temp_threshold_{nm}", lambda c=c: N.nvmlDeviceGetTemperatureThreshold(h, c))
        g("mem_total_mib", lambda: N.nvmlDeviceGetMemoryInfo(h).total // 2 ** 20)
        try:
            r = subprocess.run(["nvidia-smi", "-q", "-d", "POWER,CLOCK,PERFORMANCE,TEMPERATURE"], capture_output=True,
                               text=True, timeout=60)
            info["nvidia-smi -q -d POWER,CLOCK,PERFORMANCE,TEMPERATURE"] = _scrub(r.stdout)
        except Exception as e:
            info["nvidia-smi"] = f"ERR {e!r}"
        torch = self.torch
        info["torch"] = str(torch.__version__)
        info["torch_cuda"] = str(torch.version.cuda)
        info["device_name_torch"] = str(torch.cuda.get_device_name(0))
        import importlib.metadata as md
        info["pip"] = {}
        for pkg in ("torch", "nvidia-cublas-cu12", "nvidia-ml-py", "numpy", "modal"):
            try:
                info["pip"][pkg] = md.version(pkg)
            except Exception as e:
                info["pip"][pkg] = f"ERR {e!r}"
        return {"static": info, "brief": f"{info.get('name')} {info.get('uuid_sha12')} enforced "
                                         f"{info.get('power_enforced_mw')} mW"}

    def _prepare(self, kinds, with_feats):
        torch = self.torch
        feats = {}
        for k in kinds:
            name = kid(k)
            A, Bs = make_pair(torch, k)
            if with_feats:
                feats[name] = kind_feats(torch, k, A, Bs)
            else:
                feats[name] = {"sha_A": sha(torch, A), "sha_B": sha(torch, Bs)}
            fmt = k[0]
            Bt = Bs.t()
            nn = A.shape[0]
            C = torch.empty((nn, nn), dtype=torch.int32 if fmt == "int8" else A.dtype, device="cuda")
            self.ops[name + "#n"] = nn
            self.ops[name] = (A, Bt, C, fmt)
            fn = self.mm_for(name)
            for _ in range(3):
                fn()
            torch.cuda.synchronize()
            e1 = torch.cuda.Event(enable_timing=True)
            e2 = torch.cuda.Event(enable_timing=True)
            e1.record()
            for _ in range(5):
                fn()
            e2.record()
            torch.cuda.synchronize()
            est = e1.elapsed_time(e2) / 5.0
            self.ops[name + "#grp"] = max(1, int(round(WIN["group_ms"] / est)))
            Cf = C.float()
            feats[name]["check"] = {"est_ms": est, "C_absmax": float(Cf.abs().max()),
                                    "C_finite": bool(torch.isfinite(Cf).all())}
            del Cf
        return feats

    def step_gen(self, st):
        fm = set(self.plan["sizes"])
        sets = {"S": STAGE_S, "M": [k for k in PHASE_L + PHASE_H if k[0] in fm]}
        kinds = list(sets[st["set"]]) + [REF]
        feats = self._prepare(kinds, with_feats=(st["set"] == "M"))
        _wjson_gz(f"{self.root}/features-{st['set']}.json.gz", feats)
        return {"n_kinds": len(kinds), "brief": f"{len(kinds)} kinds built"}

    def plan_ids(self):
        ids = set()
        for s in self.plan["steps"]:
            for x in (s.get("seq") or []):
                ids.add(x)
            if s.get("kind"):
                ids.add(s["kind"])
        return ids

    def step_idle(self, st):
        t_a = time.time()
        time.sleep(st["s"])
        return {"t_a": t_a, "t_b": time.time(), "brief": f"idle {st['s']:g} s"}

    def step_hold(self, st):
        w = self.window(st["kind"], st["s"])
        return {"windows": [w], "brief": f"{st['kind']} {w['calls']} calls"}

    def step_pass(self, st):
        ws = [dict(self.window("bf16.REF", WIN["ref_s"]), role="ref")]
        for kname in st["seq"]:
            if self.elapsed() + WIN["cell_s"] + WIN["ref_s"] + 5.0 > self.budget_s:
                self.skipped.append({"pass": st["p"], "from": kname, "elapsed_s": self.elapsed()})
                break
            ws.append(dict(self.window(kname, WIN["cell_s"]), role="cell"))
            ws.append(dict(self.window("bf16.REF", WIN["ref_s"]), role="ref"))
        return {"windows": ws, "brief": f"{sum(1 for w in ws if w['role'] == 'cell')} cells"}

    def step_holds(self, st):
        ws = []
        for kname in st["seq"]:
            if self.elapsed() + st["pre_s"] + st["hold_s"] + 5.0 > self.budget_s:
                self.skipped.append({"holds_from": kname, "elapsed_s": self.elapsed()})
                break
            ws.append(dict(self.window("bf16.zeros", st["pre_s"]), role="pre", for_kind=kname))
            ws.append(dict(self.window(kname, st["hold_s"]), role="hold"))
        return {"windows": ws, "brief": f"{sum(1 for w in ws if w['role'] == 'hold')} holds"}

    def step_feat2(self, st):
        """After every measurement: stop the sampler, free stage 1's operands, build stage 2's kinds and compute
        their features only (no window runs on them here)."""
        open(self.stop_path, "w").close()
        time.sleep(1.0)
        self.flush_samples()
        self.ops = {}
        self.torch.cuda.empty_cache()
        torch = self.torch
        feats = {}
        for k in STAGE2:
            A, Bs = make_pair(torch, k)
            feats[kid(k)] = kind_feats(torch, k, A, Bs)
            del A, Bs
        _wjson_gz(f"{self.root}/features-2.json.gz", feats)
        return {"n_kinds": len(feats), "brief": f"stage-2 features for {len(feats)} kinds (no power read)"}


def _run(run_id, plan_json, budget_s):
    pl = json.loads(plan_json)
    SIZE.update({k: int(v) for k, v in pl["sizes"].items()})
    unit = pl["unit"]
    root = f"/vol/{run_id}/{unit}"
    vol.reload()
    if os.path.exists(root + "/STARTED"):
        return json.dumps({"unit": unit, "status": "refused: STARTED exists, so this is a restart of the input"})
    os.makedirs(root + "/steps", exist_ok=True)
    os.makedirs(root + "/samples", exist_ok=True)
    _wjson(root + "/STARTED", {"t": time.time(), "unit": unit, "run_id": run_id})
    _wjson(root + "/plan.json", pl)
    vol.commit()
    u = Unit(run_id, pl, budget_s)
    with open("/tmp/e150_sampler.py", "w") as f:
        f.write(SAMPLER_SRC)
    sp = subprocess.Popen([sys.executable, "/tmp/e150_sampler.py", u.samp_path, u.stop_path,
                           str(WIN["sampler_period_s"])])
    summary = {"unit": unit, "run_id": run_id, "t_fn": u.t_fn, "sizes": dict(SIZE)}
    try:
        time.sleep(1.0)
        import torch
        u.torch = torch
        torch.backends.cuda.matmul.allow_tf32 = False
        torch.zeros(1, device="cuda")
        torch.cuda.synchronize()
        for st in pl["steps"]:
            u.run_step(st)
    except Exception:
        summary["error"] = traceback.format_exc()
    finally:
        open(u.stop_path, "w").close()
        try:
            sp.wait(timeout=15)
        except Exception:
            sp.kill()
        u.flush_samples()
        summary["skipped"] = u.skipped
        summary["t_end"] = time.time()
        summary["elapsed_s"] = summary["t_end"] - u.t_fn
        _wjson(root + "/DONE", summary)
        vol.commit()
    return json.dumps(summary)


@app.function(gpu="L4", timeout=TIMEOUT_S["S"], cpu=CPU_CORES, memory=MEM_MIB, volumes={"/vol": vol})
def run_smoke_L4(run_id: str, plan_json: str, budget_s: float) -> str:
    return _run(run_id, plan_json, budget_s)


@app.function(gpu="A10G", timeout=TIMEOUT_S["S"], cpu=CPU_CORES, memory=MEM_MIB, volumes={"/vol": vol})
def run_smoke_A10G(run_id: str, plan_json: str, budget_s: float) -> str:
    return _run(run_id, plan_json, budget_s)


@app.function(gpu="L4", timeout=TIMEOUT_S["M"], cpu=CPU_CORES, memory=MEM_MIB, volumes={"/vol": vol})
def run_main_L4(run_id: str, plan_json: str, budget_s: float) -> str:
    return _run(run_id, plan_json, budget_s)


@app.function(gpu="A10G", timeout=TIMEOUT_S["M"], cpu=CPU_CORES, memory=MEM_MIB, volumes={"/vol": vol})
def run_main_A10G(run_id: str, plan_json: str, budget_s: float) -> str:
    return _run(run_id, plan_json, budget_s)


SMOKE_FN = {"L4": run_smoke_L4, "A10G": run_smoke_A10G}
MAIN_FN = {"L4": run_main_L4, "A10G": run_main_A10G}


def _collect(calls):
    for u, c in calls.items():
        print(f"unit {u}: call {c.object_id}", flush=True)
    for u, c in calls.items():
        try:
            res = c.get()
        except Exception as e:
            res = json.dumps({"unit": u, "error": repr(e)})
        print(f"unit {u}: {res[:1500]}", flush=True)


@app.local_entrypoint()
def main(mode: str = "dry", run_id: str = "", gpu: str = "", sizes: str = ""):
    if mode == "dry":
        tot_s = 0.0
        for g in GPU_TYPES:
            pl = plan("S", f"S-{g}")
            secs = sum(step_seconds(s) for s in pl["steps"]) + 90.0
            d, per_h = dollars(secs, g)
            cap, _ = dollars(TIMEOUT_S["S"], g)
            tot_s += d
            print(f"smoke on {g}: {len(pl['steps'])} steps, planned {secs / 60:.1f} min (${d:.2f}), timeout "
                  f"{TIMEOUT_S['S'] / 60:.0f} min (at most ${cap:.2f}), rate ${per_h:.4f}/h")
        for g in GPU_TYPES:
            tot = 0.0
            for u in ("A", "B"):
                pl = plan("M", u)
                secs = sum(step_seconds(s) for s in pl["steps"]) + 90.0
                d, per_h = dollars(secs, g)
                cap, _ = dollars(TIMEOUT_S["M"], g)
                tot += d
                print(f"main on {g} unit {u}: {len(pl['steps'])} steps, planned {secs / 60:.1f} min (${d:.2f}), "
                      f"budget {BUDGET_S['M'] / 60:.0f} min, timeout {TIMEOUT_S['M'] / 60:.0f} min (at most ${cap:.2f})")
            print(f"  projected on {g}: smokes ${tot_s:.2f} + main ${tot:.2f} = ${tot_s + tot:.2f}")
        pl = plan("M", "A")
        for s in pl["steps"]:
            extra = f" {len(s['seq'])} windows" if s.get("seq") else ""
            print("   ", s["op"], s.get("label", ""), s.get("kind", ""), extra)
        print(f"phase L: {len(PHASE_L)} kinds; phase H: {len(PHASE_H)} kinds; smoke: {len(STAGE_S)} windows a GPU")
        return
    assert run_id, "--run-id is required"
    if mode == "smoke":
        calls = {f"S-{g}": SMOKE_FN[g].spawn(run_id, json.dumps(plan("S", f"S-{g}")), BUDGET_S["S"])
                 for g in GPU_TYPES}
        _collect(calls)
        return
    if mode == "main":
        assert gpu in MAIN_FN, gpu
        sz = json.loads(sizes)
        assert set(sz) <= {"bf16", "fp16", "int8"}, sz
        calls = {u: MAIN_FN[gpu].spawn(run_id, json.dumps(plan("M", u, sz)), BUDGET_S["M"]) for u in ("A", "B")}
        _collect(calls)
        return
    raise SystemExit(f"unknown mode {mode}")
