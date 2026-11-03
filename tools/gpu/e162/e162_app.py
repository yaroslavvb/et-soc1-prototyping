"""E162 - which operand pairing a GPU pays for: row-against-K kinds on Modal A100-40GB and L40S boards, under the cap.

The registration is E162.md beside this file. This is E149's harness (tools/gpu/e149/e149_app.py) with only these
changes; its NVML sampler, its window, its builders for E149's kinds and its feature code are E149's, unchanged:
- new kind builders (`sq2`: two-value square waves along K or along the rows, with a shared phase, a phase per row or
  column, or one per block of rows; `rowconst`, `colconst`, `dup`, `tile`, `rollM`, `walk`, `walk2`, `sinpos`,
  `checkv`, `stripe`) and E162.md's kinds lists. E149's kinds keep E149's names, specs and seed labels, so on an A100
  they are E149's bytes (checked by sha256 against E149's committed feature records);
- the features add row-direction flips at row-lags 1, 2, 4, 8, 16, 32 (`rlag<r>`; E149's `row` is kept and equals
  `rlag1`) and row-direction gate transitions (`gtrR<r>`);
- two GPU types (A100-40GB, L40S), each format's size taken from the plan, and a guard: a container whose NVML name is
  not the expected type, or whose hashed UUID is on the plan's refuse list (a board the fit has seen), writes DONE with
  the refusal and measures nothing;
- steps that rebuild E149's stage-1 and stage-2 kinds (E149's seeds) and E162's held-out kinds after every window, with
  the NVML sampler stopped, only to compute their features.
Reads only: NVML getters and `nvidia-smi -q`; nothing is set on the GPU.

    MODAL_PROFILE=yaroslavvb modal run e162_app.py --mode dry
    MODAL_PROFILE=yaroslavvb modal run e162_app.py --mode smokeL --run-id <id>
    MODAL_PROFILE=yaroslavvb modal run --detach e162_app.py --mode a1 --run-id <id> [--units A,B]
    MODAL_PROFILE=yaroslavvb modal run --detach e162_app.py --mode l1 --run-id <id> --l40s-size <n> [--units LA,LB]
    MODAL_PROFILE=yaroslavvb modal run --detach e162_app.py --mode a2 --run-id <id> --refuse <h1,h2,...> --units A,B
    MODAL_PROFILE=yaroslavvb modal run --detach e162_app.py --mode l2 --run-id <id> --l40s-size <n> --refuse <...>
    MODAL_PROFILE=yaroslavvb modal volume get e162-gpu-row-k /<id> <local dir>

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

APP_NAME = "e162-gpu-row-k"
VOL_NAME = "e162-gpu-row-k"
PINS = {"python": "3.11", "torch": "2.5.1", "nvidia-ml-py": "12.560.30", "numpy": "2.1.3"}
# `modal billing rates`, read Tue 3 Nov 2026 04:05:39 PST on the Intel (workspace yaroslavvb)
RATE = {"A100": 2.10, "L40S": 1.95, "cpu_core_h": 0.0473, "mem_gib_h": 0.008}
GPU_OF = {"A100": "A100-40GB", "L40S": "L40S"}
NAME_OF = {"A100": "A100", "L40S": "L40S"}         # a substring the NVML name must contain (the guard)
CPU_CORES = 2.0
MEM_MIB = 8192
SIZE_A100 = {"bf16": 2048, "fp16": 1024, "int8": 1024}   # E149's sizes (its A1)
SMOKE_SIZES = (1024, 1536, 2048, 3072, 4096)
# function timeouts and each unit's own step budget (s); the timeouts are the spend's hard ceiling (E162.md, Budget)
TIMEOUT_S = {"LS": 600, "A1": 1680, "L1": 1440, "A2": 720, "L2": 600}
BUDGET_S = {"LS": 480.0, "A1": 1560.0, "L1": 1320.0, "A2": 600.0, "L2": 480.0}
WIN = {"cell_s": 5.0, "ref_s": 3.0, "cell_settle_s": 1.5, "ref_settle_s": 1.0, "group_ms": 20.0, "depth": 4,
       "sampler_period_s": 0.1}
LAGS = [1, 2, 4, 8, 16, 32]
RLAGS = [1, 2, 4, 8, 16, 32]
ACC_PAIRS = 4096
ACC_BLOCK = 16

image = modal.Image.debian_slim(python_version=PINS["python"]).pip_install(
    f"torch=={PINS['torch']}", f"nvidia-ml-py=={PINS['nvidia-ml-py']}", f"numpy=={PINS['numpy']}")
app = modal.App(APP_NAME, image=image)
vol = modal.Volume.from_name(VOL_NAME, create_if_missing=True)

# ---------------------------------------------------------------------------------------------------------------
# E149's kinds, verbatim (e149_app.py `_stage1`, `_stage2`): their names, specs and seed labels ("e149/...").
BF1, BF15, BFM7 = 0x3F80, 0x3FC0, 0x3FFF          # bf16 1.0, 1.5, 1.9921875
FP1, FP15 = 0x3C00, 0x3E00                        # fp16 1.0, 1.5
FPM10 = 0x3FFF                                    # fp16 1.9990234375 (all ten mantissa bits set)
BF_MANT, BF_EXP5 = (0, 7), (7, 5)
FP_MANT, FP_EXP3 = (0, 10), (10, 3)
I8_FLIP = (1, 7)
SQV = {"bf16": (BF1, BFM7), "fp16": (FP1, FPM10), "int8": (1, 127)}   # E162's two-value waves: 7, 10, 6 bits apart


def S(**kw):
    return kw


def both(spec):
    return spec, dict(spec)


def _e149_stage1():
    k = []
    rn = S(g="randn")
    src = S(g="randn", seed="zl-src")
    k.append(("bf16", "randn", *both(rn)))
    for f in (25, 50, 75, 90):
        k.append(("bf16", f"zs{f}", *both(S(g="zmask", src=src, frac=f / 100, block=1))))
    for f in (25, 50, 75, 90):
        k.append(("bf16", f"zb{f}", *both(S(g="zmask", src=src, frac=f / 100, block=64))))
    k.append(("bf16", "zeros", *both(S(g="zeros"))))
    k.append(("bf16", "zsA50", S(g="zmask", src=src, frac=0.5, block=1), dict(src)))
    k.append(("bf16", "zsB50", dict(src), S(g="zmask", src=src, frac=0.5, block=1)))
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
    c15 = S(g="const", bits=BF15)
    k.append(("bf16", "sfix", *both(c15)))
    k.append(("bf16", "sfixAneg", S(g="const", bits=BF15 | 0x8000), dict(c15)))
    k.append(("bf16", "srand", *both(S(g="bitp", base=BF15, pos=15, p=0.5))))
    k.append(("bf16", "srandA", S(g="bitp", base=BF15, pos=15, p=0.5), dict(c15)))
    k.append(("bf16", "srandB", dict(c15), S(g="bitp", base=BF15, pos=15, p=0.5)))
    k.append(("bf16", "smagfix", *both(S(g="absval", src=S(g="randn", seed="mag-src")))))
    k.append(("bf16", "smagrand", *both(S(g="randsign", src=S(g="absval", src=S(g="randn", seed="mag-src"))))))
    osrc = S(g="randn", seed="order-src")
    k.append(("bf16", "dsortK", *both(S(g="sortK", src=osrc))))
    k.append(("bf16", "dshufK", *both(S(g="shufK", src=S(g="sortK", src=osrc)))))
    k.append(("bf16", "dabsK", *both(S(g="randsign", src=S(g="sortK", src=S(g="absval", src=osrc))))))
    k.append(("bf16", "dsortM", *both(S(g="sortM", src=osrc))))
    k.append(("bf16", "drollK", *both(S(g="rollK", src=S(g="sortK", src=osrc)))))
    for b in (1, 2, 4, 8, 16, 64):
        k.append(("bf16", f"sq{b}", *both(S(g="square", v0=BF1, v1=BFM7, block=b))))
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


def _e149_stage2():
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


E149_S1 = _e149_stage1()
E149_S2 = _e149_stage2()


def kid(k):
    return f"{k[0]}.{k[1]}"


E149_BY = {kid(k): k for k in E149_S1}
E149_S2_BY = {kid(k): k for k in E149_S2}


# ---------------------------------------------------------------------------------------------------------------
# E162's kinds (E162.md, "The kinds"). The prefix of a kind's seed labels is "e162" for these and "e149" for E149's.
def _sq(fmt, along, b, ph):
    v0, v1 = SQV[fmt]
    return S(g="sq2", along=along, block=b, ph=ph, v0=v0, v1=v1)


def _new_stage1():
    k = []
    c1 = {"bf16": S(g="const", bits=BF1), "fp16": S(g="const", bits=FP1), "int8": S(g="const", bits=1)}
    for b in (1, 2, 4, 8, 16, 32, 64):          # along K, one phase for every row: no row-direction flips
        k.append(("bf16", f"kS{b}", *both(_sq("bf16", "K", b, "shared"))))
    for b in (1, 2, 4, 8, 16, 32, 64):          # along the rows, one phase for every column: no K-direction flips
        k.append(("bf16", f"rS{b}", *both(_sq("bf16", "R", b, "shared"))))
    k.append(("bf16", "rC16", *both(_sq("bf16", "R", 16, "col"))))   # along the rows, a phase per column
    k.append(("bf16", "rollM", *both(S(g="rollM", src=S(g="randn", seed="rollM-src")))))
    k.append(("bf16", "rowc", *both(S(g="rowconst"))))
    k.append(("bf16", "colc", *both(S(g="colconst"))))
    k.append(("bf16", "rowcA_colcB", S(g="rowconst"), S(g="colconst")))
    k.append(("bf16", "colcA_rowcB", S(g="colconst"), S(g="rowconst")))
    k.append(("bf16", "kS1A", _sq("bf16", "K", 1, "shared"), dict(c1["bf16"])))
    k.append(("bf16", "kS1B", dict(c1["bf16"]), _sq("bf16", "K", 1, "shared")))
    k.append(("bf16", "rS1A", _sq("bf16", "R", 1, "shared"), dict(c1["bf16"])))
    k.append(("bf16", "rS1B", dict(c1["bf16"]), _sq("bf16", "R", 1, "shared")))
    for fmt in ("fp16", "int8"):
        for b in (1, 16):
            k.append((fmt, f"kS{b}", *both(_sq(fmt, "K", b, "shared"))))
            k.append((fmt, f"rS{b}", *both(_sq(fmt, "R", b, "shared"))))
        k.append((fmt, "rowc", *both(S(g="rowconst"))))
        k.append((fmt, "colc", *both(S(g="colconst"))))
    return k


def _held():
    """The held-out kinds: registered with stage 1, measured only in stage 2 on new boards, after the freeze."""
    k = []
    k.append(("bf16", "t16x16", *both(S(g="tile", bm=16, bk=16))))
    k.append(("bf16", "t4x32", *both(S(g="tile", bm=4, bk=32))))
    k.append(("bf16", "t32x4", *both(S(g="tile", bm=32, bk=4))))
    k.append(("bf16", "kB8_4", *both(_sq("bf16", "K", 4, "rb8"))))
    k.append(("bf16", "checkv", *both(S(g="checkv", v0=BF1, v1=BFM7))))
    k.append(("bf16", "stripeK0", *both(S(g="stripe", along="K"))))
    k.append(("bf16", "stripeR0", *both(S(g="stripe", along="R"))))
    k.append(("bf16", "walkK", *both(S(g="walk", along="K"))))
    k.append(("bf16", "walkR", *both(S(g="walk", along="R"))))
    k.append(("bf16", "walk2", *both(S(g="walk2"))))
    k.append(("bf16", "sinpos", *both(S(g="sinpos"))))
    k.append(("bf16", "rdup8", *both(S(g="dup", along="R", n=8))))
    k.append(("bf16", "cdup8", *both(S(g="dup", along="K", n=8))))
    k.append(("bf16", "rollM_A", S(g="rollM", src=S(g="randn", seed="rollMA-src")), S(g="randn")))
    for fmt in ("fp16", "int8"):
        k.append((fmt, "t16x16", *both(S(g="tile", bm=16, bk=16))))
        k.append((fmt, "walkK", *both(S(g="walk", along="K"))))
        k.append((fmt, "rdup8", *both(S(g="dup", along="R", n=8))))
        k.append((fmt, "cdup8", *both(S(g="dup", along="K", n=8))))
    return k


NEW1 = _new_stage1()
HELD = _held()
ZEROS = [E149_BY["bf16.zeros"], E149_BY["fp16.zeros"], E149_BY["int8.zeros"]]
BRIDGE = [E149_BY[x] for x in ("bf16.randn", "bf16.sq1", "bf16.sq16", "bf16.sq64", "bf16.dsortK", "bf16.dshufK",
                               "bf16.dsortM", "bf16.drollK", "bf16.mk3", "fp16.randn", "fp16.mk5", "int8.rand",
                               "int8.k3")]
L40S_CORE = [E149_BY["bf16." + x] for x in (
    "randn", "zeros", "zs50", "zs75", "zb50", "zb75", "base1", "mk1", "mk3", "mk7", "ek1", "ek3", "ek5", "sp25", "sp50",
    "mb0", "mb6", "mk3A", "mk3B", "sfix", "srand", "dsortK", "dshufK", "dsortM", "drollK", "sq1", "sq16", "sq64")]
ANCHOR_RANDN = [E149_BY["bf16.randn"], E149_BY["fp16.randn"], E149_BY["int8.rand"]]
SETS = {
    "A1": BRIDGE + ZEROS + NEW1,                                            # A100 stage 1 (52 kinds)
    "A2": [k for k in HELD] + ZEROS + ANCHOR_RANDN,                         # A100 stage 2 (28 kinds)
    "L1": L40S_CORE + [k for k in NEW1 if k[0] == "bf16"],                  # L40S stage 1, bf16 only (52 kinds)
    "L2": [k for k in HELD if k[0] == "bf16"] + [E149_BY["bf16.zeros"], E149_BY["bf16.randn"]],   # L40S stage 2
    "HA": HELD,                                                             # held-out features, A100
    "HL": [k for k in HELD if k[0] == "bf16"],                              # held-out features, L40S
    "E149": E149_S1 + [k for k in E149_S2 if kid(k) not in E149_BY],        # E149's 113 kinds, features only
}
SMOKE_KINDS = ([("bf16", f"randn@{n}", S(g="randn"), S(g="randn")) for n in SMOKE_SIZES] +
               [("bf16", f"zeros@{n}", S(g="zeros"), S(g="zeros")) for n in SMOKE_SIZES])
PLUMB = NEW1 + HELD                                                       # the smoke builds these at 512 (plumbing)
ANCHORS = {"A": ["bf16.zeros", "fp16.zeros", "int8.zeros"], "L": ["bf16.zeros"]}
REF = ("bf16", "REF", S(g="randn"), S(g="randn"))


def prefix_of(k):
    return "e149" if (kid(k) in E149_BY or kid(k) in E149_S2_BY) and k[1] != "REF" else "e162"


def _seed(label):
    return int(hashlib.sha256(label.encode()).hexdigest()[:12], 16)


# ---------------------------------------------------------------------------------------------------------------
# Building operands on the GPU (E149's builders unchanged, E162's added). Every random draw uses its own
# torch.Generator seeded from a label, so the same kind gives the same bytes on every board of one GPU type.
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


def _two(torch, fmt, spec):
    """The two values of a two-value kind, as 0-dim tensors of the format."""
    if fmt == "int8":
        return (torch.tensor(spec["v0"], dtype=torch.int8, device="cuda"),
                torch.tensor(spec["v1"], dtype=torch.int8, device="cuda"))
    dt = {"bf16": torch.bfloat16, "fp16": torch.float16}[fmt]
    return (_to16(torch, torch.tensor(spec["v0"], device="cuda")).view(dt),
            _to16(torch, torch.tensor(spec["v1"], device="cuda")).view(dt))


def _rand_like_fmt(torch, fmt, shape, g):
    """One random draw per element in the format's 'random' kind: randn (floats) or -128..127 (int8)."""
    if fmt == "int8":
        return torch.randint(-128, 128, shape, generator=g, dtype=torch.int8, device="cuda")
    dt = {"bf16": torch.bfloat16, "fp16": torch.float16}[fmt]
    return torch.randn(shape, generator=g, dtype=dt, device="cuda")


def build_e162(torch, spec, fmt, shape, label, g, g2):
    """E162's builders (E162.md, "The kinds"). shape = (rows, K)."""
    t = spec["g"]
    dev = "cuda"
    R, K = shape
    if t == "sq2":
        b = spec["block"]
        ph = spec["ph"]
        if spec["along"] == "K":
            if ph == "shared":
                p = torch.randint(0, 2 * b, (1, 1), generator=g2, device=dev)
            elif ph == "row":
                p = torch.randint(0, 2 * b, (R, 1), generator=g2, device=dev)
            elif ph.startswith("rb"):
                n = int(ph[2:])
                p = torch.randint(0, 2 * b, (R // n, 1), generator=g2, device=dev).repeat_interleave(n, dim=0)
            else:
                raise ValueError(ph)
            hi = ((torch.arange(K, device=dev).view(1, -1) + p) // b) % 2 == 1
        else:
            if ph == "shared":
                p = torch.randint(0, 2 * b, (1, 1), generator=g2, device=dev)
            elif ph == "col":
                p = torch.randint(0, 2 * b, (1, K), generator=g2, device=dev)
            else:
                raise ValueError(ph)
            hi = ((torch.arange(R, device=dev).view(-1, 1) + p) // b) % 2 == 1
        hi = hi.expand(R, K)                  # a shared phase gives one row (or column) of the pattern
        v0, v1 = _two(torch, fmt, spec)
        return torch.where(hi, v1, v0).contiguous()
    if t == "checkv":
        v0, v1 = _two(torch, fmt, spec)
        hi = (torch.arange(R, device=dev).view(-1, 1) - torch.arange(K, device=dev).view(1, -1)) % 2 != 0
        return torch.where(hi, v1, v0)
    if t == "rowconst":
        return _rand_like_fmt(torch, fmt, (R, 1), g).expand(R, K).contiguous()
    if t == "colconst":
        return _rand_like_fmt(torch, fmt, (1, K), g).expand(R, K).contiguous()
    if t == "dup":
        n = spec["n"]
        if spec["along"] == "R":
            return _rand_like_fmt(torch, fmt, (R // n, K), g).repeat_interleave(n, dim=0)
        return _rand_like_fmt(torch, fmt, (R, K // n), g).repeat_interleave(n, dim=1)
    if t == "tile":
        bm, bk = spec["bm"], spec["bk"]
        return _rand_like_fmt(torch, fmt, (R // bm, K // bk), g).repeat_interleave(bm, dim=0).repeat_interleave(
            bk, dim=1)
    if t == "rollM":                          # each column sorted along the rows, then rolled by its own offset
        X = build(torch, spec["src"], fmt, shape, label)
        Xs = torch.sort(X.float(), dim=0).values
        off = torch.randint(0, R, (1, K), generator=g2, device=dev)
        idx = (torch.arange(R, device=dev).view(-1, 1) + off) % R
        out = torch.gather(Xs, 0, idx)
        return out.to(X.dtype)
    if t == "stripe":                         # randn (or -128..127) with every odd column (K) or row zeroed
        X = _rand_like_fmt(torch, fmt, shape, g)
        if spec["along"] == "K":
            X[:, 1::2] = 0
        else:
            X[1::2, :] = 0
        return X
    if t == "walk":                           # a random walk along K (each row its own) or along the rows
        if spec["along"] == "K":
            w = torch.cumsum(torch.randn(shape, generator=g, device=dev) * 0.05, dim=1) + \
                torch.randn((R, 1), generator=g2, device=dev)
        else:
            w = torch.cumsum(torch.randn(shape, generator=g, device=dev) * 0.05, dim=0) + \
                torch.randn((1, K), generator=g2, device=dev)
        if fmt == "int8":                     # bounded and smooth: 100 sin(w)
            return torch.round(100.0 * torch.sin(w)).to(torch.int8)
        return w.to({"bf16": torch.bfloat16, "fp16": torch.float16}[fmt])
    if t == "walk2":                          # u_i + v_k: random walks along both directions
        u = torch.cumsum(torch.randn((R, 1), generator=g, device=dev) * 0.05, dim=0)
        v = torch.cumsum(torch.randn((1, K), generator=g2, device=dev) * 0.05, dim=1)
        w = u + v
        if fmt == "int8":
            return torch.round(100.0 * torch.sin(w)).to(torch.int8)
        return w.to({"bf16": torch.bfloat16, "fp16": torch.float16}[fmt])
    if t == "sinpos":                         # the transformer positional table: rows are positions, K dimensions
        pos = torch.arange(R, device=dev, dtype=torch.float32).view(-1, 1)
        i2 = (torch.arange(K, device=dev) // 2).to(torch.float32).view(1, -1)
        ang = pos * torch.pow(10000.0, -2.0 * i2 / K)
        even = (torch.arange(K, device=dev) % 2 == 0).view(1, -1)
        w = torch.where(even, torch.sin(ang), torch.cos(ang))
        if fmt == "int8":
            return torch.round(127.0 * w).to(torch.int8)
        return w.to({"bf16": torch.bfloat16, "fp16": torch.float16}[fmt])
    raise ValueError(f"{fmt} {t}")


E162_GENS = {"sq2", "checkv", "rowconst", "colconst", "dup", "tile", "rollM", "stripe", "walk", "walk2", "sinpos"}


def build(torch, spec, fmt, shape, label):
    """One operand (rows, K) in format fmt (E149's `build`, with E162's builders added). label =
    '<prefix>/<fmt>/<name>/<side>'; a spec's own 'seed' overrides it as E149's does."""
    side = label.rsplit("/", 1)[-1]
    pre = label.split("/", 1)[0]
    lab = (f"{pre}/{fmt}/{spec['seed']}/{side}" if "seed" in spec else label)
    g = torch.Generator(device="cuda")
    g.manual_seed(_seed(lab))
    g2 = torch.Generator(device="cuda")
    g2.manual_seed(_seed(label + "/x"))
    t = spec["g"]
    dev = "cuda"
    R, K = shape
    if t in E162_GENS:
        return build_e162(torch, spec, fmt, shape, label, g, g2)
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
    if t == "sparse75":
        x = torch.randn(shape, generator=g, dtype=dt, device=dev)
        keep = torch.rand(shape, generator=g2, device=dev) >= 0.75
        return torch.where(keep, x, torch.zeros((), dtype=dt, device=dev))
    if t == "sparse_neg":
        x = torch.randn(shape, generator=g, dtype=dt, device=dev)
        return torch.where(x < 0, torch.zeros((), dtype=dt, device=dev), x)
    if t == "ternary":
        return torch.randint(-1, 2, shape, generator=g, device=dev).to(dt)
    if t == "onebit":
        x = torch.randn(shape, generator=g, dtype=dt, device=dev)
        return (x.view(torch.int16) & 0b1000).to(dt)
    if t == "checker":
        x = torch.randn(shape, generator=g, dtype=dt, device=dev)
        par = (torch.arange(R, device=dev).view(-1, 1) - torch.arange(K, device=dev).view(1, -1)) % 2 == 0
        return torch.where(par, x, torch.zeros((), dtype=dt, device=dev))
    if t == "gelu":
        return torch.nn.functional.gelu(torch.randn(shape, generator=g, device=dev)).to(dt)
    if t == "llmw":
        return (_tdist(torch, shape, g) * 0.02).to(dt)
    if t == "powerlaw":
        u = torch.rand(shape, generator=g, device=dev).clamp_min(1e-12)
        mag = (u.pow(-1.0 / 1.5) - 1.0).clamp_max(1.0e4)
        neg = torch.rand(shape, generator=g2, device=dev) < 0.5
        return torch.where(neg, -mag, mag).to(dt)
    if t == "lowrank":
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


def size_of(k, sizes):
    """A kind's M = N = K: the plan's size for its format, or the '@n' suffix of its name (the L40S smoke)."""
    return int(k[1].split('@')[1]) if '@' in k[1] else int(sizes[k[0]])


def make_pair(torch, k, n):
    fmt, name, sa, sb = k
    pre = prefix_of(k)
    A = build(torch, sa, fmt, (n, n), f"{pre}/{fmt}/{name}/A")
    Bs = build(torch, sb, fmt, (n, n), f"{pre}/{fmt}/{name}/B")
    return A.contiguous(), Bs.contiguous()


def sha(torch, X):
    return hashlib.sha256(X.contiguous().view(torch.uint8).cpu().numpy().tobytes()).hexdigest()


# ---------------------------------------------------------------------------------------------------------------
# Features from the operand bits: E149's (`side_feats`, `cross_feats`, `acc_feats`), plus the row-direction flips at
# row-lags RLAGS (`rlag<r>`; `row` = `rlag1`, E149's key) and the row-direction gate transitions (`gtrR<r>`).
def _bits(torch, X, fmt):
    if fmt == "int8":
        return X.view(torch.uint8).to(torch.int32), 8
    return X.view(torch.int16).to(torch.int32) & 0xFFFF, 16


def side_feats(torch, X, fmt):
    I, W = _bits(torch, X, fmt)
    out = {"ones": [], "row": []}
    for s in LAGS:
        out[f"lag{s}"] = []
    for r in RLAGS:
        out[f"rlag{r}"] = []
    for p in range(W):
        b = ((I >> p) & 1).to(torch.uint8)
        out["ones"].append(float(b.float().mean()))
        for s in LAGS:
            out[f"lag{s}"].append(float((b[:, s:] ^ b[:, :-s]).float().mean()))
        out["row"].append(float((b[1:, :] ^ b[:-1, :]).float().mean()))
        for r in RLAGS:
            out[f"rlag{r}"].append(float((b[r:, :] ^ b[:-r, :]).float().mean()))
        del b
    nz = (X != 0)
    sb = ((I >> (W - 1)) & 1).to(torch.uint8)
    vec = {"nz_k": nz.float().mean(dim=0), "sg_k": sb.float().mean(dim=0)}
    for s in LAGS:
        vec[f"nzc{s}_k"] = (nz[:, s:] & nz[:, :-s]).float().mean(dim=0)
        vec[f"sf{s}_k"] = (sb[:, s:] ^ sb[:, :-s]).float().mean(dim=0)
    for r in RLAGS:
        vec[f"nzR{r}_k"] = (nz[r:, :] ^ nz[:-r, :]).float().mean(dim=0)
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
    for r in RLAGS:     # E162: a row step of A at one k (B fixed) or of B (A fixed) changes the gate state
        out[f"gtrR{r}"] = float((va[f"nzR{r}_k"] * vb["nz_k"]).mean() + (vb[f"nzR{r}_k"] * va["nz_k"]).mean())
    return out


def acc_feats(torch, A, Bs, fmt, seed_label):
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
    ac = acc_feats(torch, A, Bs, fmt, f"{prefix_of(k)}/acc/{kid(k)}")
    return {"kind": kid(k), "fmt": fmt, "A": fa, "B": fb, "cross": cr, "acc": ac,
            "spec": {"A": k[2], "B": k[3]}, "sha_A": sha(torch, A), "sha_B": sha(torch, Bs), "n": int(A.shape[0])}


# ---------------------------------------------------------------------------------------------------------------
# The NVML sampler: its own process. Getters only (E135's and E149's, unchanged).
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
# The plans (E162.md, "How a window is read"). A pass = REF, then (cell, REF) for every kind in the pass's order; each
# format's zeros also run at the start, middle and end of a pass. Unit 1 of a pair runs the passes forward then
# reversed, unit 2 the reverse; a replacement unit keeps the order of the unit it replaces.
def pass_order(kinds, stage, fwd, anchors):
    ids = [kid(k) for k in kinds]
    import random as _r
    rnd = _r.Random(_seed(f"e162/order/{stage}"))
    body = list(ids)
    rnd.shuffle(body)
    mid = len(body) // 2
    seq = anchors + body[:mid] + anchors + body[mid:] + anchors
    return seq if fwd else list(reversed(seq))


def plan(stage, unit, first=True, l40s_size=None, refuse=()):
    """stage: LS (L40S smoke), A1, L1 (stage 1), A2, L2 (stage 2). first: this unit runs pass 1 forward."""
    gpu = "A100" if stage.startswith("A") else "L40S"
    if gpu == "A100":
        sizes = dict(SIZE_A100)
    else:
        n = int(l40s_size) if l40s_size else 1024
        sizes = {"bf16": n, "fp16": n, "int8": n}
    base = {"stage": stage, "unit": unit, "gpu": gpu, "sizes": sizes, "expect_name": NAME_OF[gpu],
            "refuse_uuid": list(refuse), "first_fwd": bool(first)}
    if stage == "LS":
        seq = [kid(k) for k in SMOKE_KINDS]
        steps = [{"op": "static"}, {"op": "gen", "set": "LS"}, {"op": "plumb"}, {"op": "idle", "s": 10.0},
                 {"op": "hold", "kind": "bf16.REF", "s": 45.0, "label": "warm_ref"},
                 {"op": "pass", "p": 1, "seq": seq}, {"op": "idle", "s": 5.0}]
        return dict(base, steps=steps)
    anchors = ANCHORS["A" if gpu == "A100" else "L"]
    if stage in ("A1", "L1"):
        steps = [{"op": "static"}, {"op": "gen", "set": stage}, {"op": "idle", "s": 30.0}]
        for p in (1, 2):
            fwd = (p == 1) == first
            steps.append({"op": "pass", "p": p, "seq": pass_order(SETS[stage], stage, fwd, anchors)})
        steps += [{"op": "idle", "s": 20.0}, {"op": "feat", "set": "HA" if gpu == "A100" else "HL", "stop": True}]
        if gpu == "A100":
            steps.append({"op": "feat", "set": "E149", "stop": True})
        return dict(base, steps=steps)
    if stage in ("A2", "L2"):
        steps = [{"op": "static"}, {"op": "gen", "set": stage}, {"op": "idle", "s": 20.0},
                 {"op": "pass", "p": 1, "seq": pass_order(SETS[stage], stage, first, anchors)},
                 {"op": "idle", "s": 10.0}]
        return dict(base, steps=steps)
    raise ValueError(stage)


def step_seconds(st):
    op = st["op"]
    if op == "static":
        return 40.0
    if op == "gen":
        return {"LS": 15.0, "A1": 100.0, "L1": 90.0, "A2": 50.0, "L2": 30.0}[st["set"]]
    if op == "plumb":
        return 60.0
    if op == "idle":
        return st["s"] + 2.0
    if op == "hold":
        return st["s"] + 1.0
    if op == "pass":
        return WIN["ref_s"] + len(st["seq"]) * (WIN["cell_s"] + WIN["ref_s"] + 0.25)
    if op == "feat":
        return {"HA": 30.0, "HL": 20.0, "E149": 100.0}[st["set"]]
    return 60.0


def dollars(seconds, gpu):
    per_h = RATE[gpu] + CPU_CORES * RATE["cpu_core_h"] + MEM_MIB / 1024 * RATE["mem_gib_h"]
    return seconds / 3600.0 * per_h, per_h


# ---------------------------------------------------------------------------------------------------------------
class Unit:
    def __init__(self, run_id, pl, budget_s):
        import pynvml
        self.N = pynvml
        self.N.nvmlInit()
        self.h = self.N.nvmlDeviceGetHandleByIndex(0)
        self.run_id, self.plan, self.unit, self.stage = run_id, pl, pl["unit"], pl["stage"]
        self.sizes = pl["sizes"]
        self.budget_s = budget_s
        self.vdir = f"/vol/{run_id}/{self.unit}"
        self.t_fn = time.time()
        self.step_i = 0
        self.chunk = 0
        self.samp_off = 0
        self.samp_path = "/tmp/e162_samples.jsonl"
        self.stop_path = "/tmp/e162_sampler.stop"
        self.ops = {}
        self.torch = None
        self.skipped = []
        self.refused = None

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
        with gzip.open(f"{self.vdir}/samples/{self.chunk:03d}.jsonl.gz", "wb") as g:
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
        if st["op"] not in ("static", "gen", "feat", "plumb") and self.elapsed() + need > self.budget_s:
            self.skipped.append({"step": st.get("label") or st["op"], "elapsed_s": self.elapsed()})
            print(f"[{self.unit}] SKIP (budget) {st.get('label') or st['op']}", flush=True)
            return
        if st["op"] in ("feat", "plumb") and self.elapsed() + need > self.budget_s + 60.0:
            self.skipped.append({"step": st.get("set") or st["op"], "elapsed_s": self.elapsed()})
            print(f"[{self.unit}] SKIP (budget) {st['op']} {st.get('set', '')}", flush=True)
            return
        i = self.step_i
        self.step_i += 1
        label = st.get("label") or (f"pass{st['p']}" if st["op"] == "pass" else
                                    (f"feat_{st['set']}" if st["op"] == "feat" else st["op"]))
        t_a = time.time()
        try:
            rec = getattr(self, "step_" + st["op"])(st)
        except Exception:
            rec = {"error": traceback.format_exc()}
        rec.update({"i": i, "op": st["op"], "label": label, "unit": self.unit, "stage": self.stage,
                    "t_step_a": t_a, "t_step_b": time.time(),
                    "step": {k: v for k, v in st.items() if k != "seq"}, "seq": st.get("seq")})
        _wjson_gz(f"{self.vdir}/steps/{i:03d}_{label}.json.gz", rec)
        self.flush_samples()
        vol.commit()
        print(f"[{self.unit}] {i:03d} {label:<16} {time.time() - t_a:7.1f} s {rec.get('brief', '')}"
              f"{'  ERROR' if rec.get('error') else ''}", flush=True)
        if rec.get("error"):
            print(rec["error"][-2000:], flush=True)
        return rec

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
        g("sm_count_torch", lambda: self.torch.cuda.get_device_properties(0).multi_processor_count)
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
        for pkg in ("torch", "nvidia-cublas-cu12", "nvidia-ml-py", "numpy"):
            try:
                info["pip"][pkg] = md.version(pkg)
            except Exception as e:
                info["pip"][pkg] = f"ERR {e!r}"
        # the guard (E162.md, "The boards"): the expected GPU type, and never a board the fit has seen
        name = str(info.get("name"))
        if self.plan["expect_name"] not in name:
            self.refused = f"refused: NVML name {name!r} is not the expected type {self.plan['expect_name']!r}"
        elif info.get("uuid_sha12") in set(self.plan.get("refuse_uuid") or []):
            self.refused = f"refused: board {info.get('uuid_sha12')} is on the refuse list (a board the fit has seen)"
        info["refused"] = self.refused
        return {"static": info, "brief": f"{name} {info.get('uuid_sha12')} enforced "
                                         f"{info.get('power_enforced_mw')} mW{'  ' + self.refused if self.refused else ''}"}

    def _prepare(self, kinds, with_feats):
        torch = self.torch
        feats = {}
        for k in kinds:
            name = kid(k)
            nn = size_of(k, self.sizes)
            A, Bs = make_pair(torch, k, nn)
            if with_feats:
                feats[name] = kind_feats(torch, k, A, Bs)
            else:
                feats[name] = {"sha_A": sha(torch, A), "sha_B": sha(torch, Bs), "n": nn}
            fmt = k[0]
            Bt = Bs.t()
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
        s = st["set"]
        kinds = (list(SMOKE_KINDS) if s == "LS" else list(SETS[s])) + [REF]
        feats = self._prepare(kinds, with_feats=(s in ("A1", "L1")))
        _wjson_gz(f"{self.vdir}/features-{s}.json.gz", feats)
        return {"n_kinds": len(kinds), "brief": f"{len(kinds)} kinds built"}

    def step_plumb(self, st):
        """The smoke's plumbing: every E162 kind of every format built at 512 with its features and one GEMM (no
        window, no power read for them)."""
        torch = self.torch
        out = {}
        for k in PLUMB:
            A, Bs = make_pair(torch, k, 512)
            fe = kind_feats(torch, k, A, Bs)
            if k[0] == "int8":
                C = torch._int_mm(A, Bs.t())
            else:
                C = torch.mm(A, Bs.t())
            fe["check"] = {"C_absmax": float(C.float().abs().max()), "C_finite": bool(torch.isfinite(C.float()).all())}
            out[kid(k)] = fe
            del A, Bs, C
        _wjson_gz(f"{self.vdir}/features-plumb.json.gz", out)
        return {"n_kinds": len(out), "brief": f"plumbing: {len(out)} kinds at 512"}

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

    def step_feat(self, st):
        """After every measurement: stop the sampler, free the measured operands, build a set's kinds and compute
        their features only (no window runs on them here)."""
        if st.get("stop") and not os.path.exists(self.stop_path):
            open(self.stop_path, "w").close()
            time.sleep(1.0)
            self.flush_samples()
        self.ops = {}
        self.torch.cuda.empty_cache()
        torch = self.torch
        s = st["set"]
        sizes = SIZE_A100 if s == "E149" else self.sizes
        feats = {}
        for k in SETS[s]:
            A, Bs = make_pair(torch, k, size_of(k, sizes))
            feats[kid(k)] = kind_feats(torch, k, A, Bs)
            del A, Bs
        _wjson_gz(f"{self.vdir}/features-{s}.json.gz", feats)
        return {"n_kinds": len(feats), "brief": f"features for {len(feats)} kinds of set {s} (no power read)"}


def _run(run_id, plan_json, budget_s):
    pl = json.loads(plan_json)
    unit = pl["unit"]
    vdir = f"/vol/{run_id}/{unit}"
    vol.reload()
    if os.path.exists(vdir + "/STARTED"):
        return json.dumps({"unit": unit, "status": "refused: STARTED exists, so this is a restart of the input"})
    os.makedirs(vdir + "/steps", exist_ok=True)
    os.makedirs(vdir + "/samples", exist_ok=True)
    _wjson(vdir + "/STARTED", {"t": time.time(), "unit": unit, "run_id": run_id})
    _wjson(vdir + "/plan.json", pl)
    vol.commit()
    u = Unit(run_id, pl, budget_s)
    with open("/tmp/e162_sampler.py", "w") as f:
        f.write(SAMPLER_SRC)
    sp = subprocess.Popen([sys.executable, "/tmp/e162_sampler.py", u.samp_path, u.stop_path,
                           str(WIN["sampler_period_s"])])
    summary = {"unit": unit, "run_id": run_id, "t_fn": u.t_fn}
    try:
        time.sleep(1.0)
        import torch
        u.torch = torch
        torch.backends.cuda.matmul.allow_tf32 = False
        torch.zeros(1, device="cuda")
        torch.cuda.synchronize()
        for st in pl["steps"]:
            u.run_step(st)
            if u.refused:
                summary["refused"] = u.refused
                break
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
        _wjson(vdir + "/DONE", summary)
        vol.commit()
    return json.dumps(summary)


FN_KW = dict(cpu=CPU_CORES, memory=MEM_MIB, volumes={"/vol": vol})


@app.function(gpu=GPU_OF["L40S"], timeout=TIMEOUT_S["LS"], **FN_KW)
def l40s_smoke(run_id: str, plan_json: str, budget_s: float) -> str:
    return _run(run_id, plan_json, budget_s)


@app.function(gpu=GPU_OF["A100"], timeout=TIMEOUT_S["A1"], **FN_KW)
def a100_s1(run_id: str, plan_json: str, budget_s: float) -> str:
    return _run(run_id, plan_json, budget_s)


@app.function(gpu=GPU_OF["L40S"], timeout=TIMEOUT_S["L1"], **FN_KW)
def l40s_s1(run_id: str, plan_json: str, budget_s: float) -> str:
    return _run(run_id, plan_json, budget_s)


@app.function(gpu=GPU_OF["A100"], timeout=TIMEOUT_S["A2"], **FN_KW)
def a100_s2(run_id: str, plan_json: str, budget_s: float) -> str:
    return _run(run_id, plan_json, budget_s)


@app.function(gpu=GPU_OF["L40S"], timeout=TIMEOUT_S["L2"], **FN_KW)
def l40s_s2(run_id: str, plan_json: str, budget_s: float) -> str:
    return _run(run_id, plan_json, budget_s)


FNS = {"LS": l40s_smoke, "A1": a100_s1, "L1": l40s_s1, "A2": a100_s2, "L2": l40s_s2}
DEFAULT_UNITS = {"LS": ["LS"], "A1": ["A", "B"], "L1": ["LA", "LB"], "A2": ["A", "B"], "L2": ["LA", "LB"]}


def dry_report():
    tot, cap_tot = 0.0, 0.0
    for st_ in ("LS", "A1", "L1", "A2", "L2"):
        gpu = "A100" if st_.startswith("A") else "L40S"
        for i, u in enumerate(DEFAULT_UNITS[st_]):
            pl = plan(st_, u, first=(i == 0), l40s_size=2048)
            secs = sum(step_seconds(s) for s in pl["steps"]) + 45.0
            d, per_h = dollars(secs, gpu)
            cap, _ = dollars(TIMEOUT_S[st_], gpu)
            tot += d
            cap_tot += cap
            print(f"{st_} unit {u} ({gpu}, ${per_h:.4f}/h): {len(pl['steps'])} steps, planned {secs / 60:.1f} min "
                  f"(${d:.2f}), budget {BUDGET_S[st_] / 60:.0f} min, timeout {TIMEOUT_S[st_] / 60:.0f} min "
                  f"(at most ${cap:.2f})")
            for s in pl["steps"]:
                extra = f" {len(s['seq'])} windows" if s.get("seq") else ""
                print("   ", s["op"], s.get("set", ""), s.get("label", ""), s.get("kind", ""), extra)
    print({k: len(v) for k, v in SETS.items()}, "smoke", len(SMOKE_KINDS), "plumb", len(PLUMB))
    print(f"projected total ${tot:.2f}; the timeouts' ceiling ${cap_tot:.2f}")


@app.local_entrypoint()
def main(mode: str = "dry", run_id: str = "", units: str = "", l40s_size: int = 0, refuse: str = "",
         order: str = ""):
    """order: 'first' or 'second' per unit, comma-separated (default: the first unit runs pass 1 forward)."""
    if mode == "dry":
        dry_report()
        return
    assert run_id, "--run-id is required"
    st_ = {"smokeL": "LS", "a1": "A1", "l1": "L1", "a2": "A2", "l2": "L2"}[mode]
    if st_ in ("L1", "L2"):
        assert l40s_size > 0, "--l40s-size is required (amendment A1's choice)"
    us = units.split(",") if units else DEFAULT_UNITS[st_]
    ords = order.split(",") if order else ["first" if i == 0 else "second" for i in range(len(us))]
    ref = [x for x in refuse.split(",") if x]
    fn = FNS[st_]
    calls = {}
    for u, o in zip(us, ords):
        pl = plan(st_, u, first=(o == "first"), l40s_size=l40s_size or None, refuse=ref)
        calls[u] = fn.spawn(run_id, json.dumps(pl), BUDGET_S[st_])
        print(f"unit {u} ({o}): call {calls[u].object_id}", flush=True)
    for u, c in calls.items():
        try:
            res = c.get()
        except Exception as e:
            res = json.dumps({"unit": u, "error": repr(e)})
        print(f"unit {u}: {res[:1500]}", flush=True)
