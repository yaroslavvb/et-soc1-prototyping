#!/usr/bin/env python3
"""ccheck: the host-side reference of C for sparsity_host's TensorFMA launches, and the check of a launch's C against it.
Q139(k), Tue 3 Nov 2026 (the Q138 critic's rank 14). Standard library only; no device access of any kind.

    ccheck.py check <c-log.jsonl>... [--out verdicts.json] [--jobs 6] [--cache DIR]   # the patched host's --c-log
    ccheck.py e104 <readback.jsonl> [--out verdicts.json] [--jobs 6] [--cache DIR]    # E104's raw read-back lines
    ccheck.py ref <fp32|fp16|int8> <tile.bin> <n> [<n> ...]                            # C for each n, hex, host order
    ccheck.py domain <tile.bin | dir>... [--n 1600000] [--jobs 6] [--out rows.json]     # operand/result classes, every
                                                                                         # op up to n; first-read notes

The reference. C after n TensorFMA ops on one tile is computed by rtl-sim/fma_toggle_v2/accum.c, unchanged and pinned
by sha256 (ENGINE_SHA below), built here with the host's cc: the order and the zero gate are the RTL's (for k, for row
i, for column j; a word pair whose raw A or B word is zero is skipped; op 0's first k is a multiply, not gated, as the
kernel's MUL bit on its first op); fp32 is FMADD rounded to nearest even, denormal operands read as zero and denormal
results flushed; fp16 is the RTL's fixed-point window (each aligned product truncated, a negated term that lost bits
one unit low); int8 is signed x signed in 32-bit wraparound, closed form n x sum (mod 2^32). E104 read 110 launches' C
back on aifoundry1 card 1 (44 designed file tiles, n = 2 .. 541,999, fp32 and fp16) and every word of all 1,024 minions
equals this arithmetic; int8's rule is the RTL's (vpu_tensorfma.v:918-919 sign from u_a/u_b, which the kernel never
sets; tima_adder.v keeps sum[31:0]), and the host's own checkC read int8's signed product sum and byte pairing back on 90
small-integer launches of 25 Sep 2026 (all three cards, n = 20,000, one minion, values in [-3, 3]; docs/reports/data/
2026-09-25-claims-v3/raw/*/lat/p*/sp/fma-int8-elem.jsonl, result "both"), whose expected C this reference equals (V9).
Not read on silicon: int8's 32-bit wrap, full-range int8 operands, float tiles spread wider than E104's (`domain`).
The tile layout is the host's (workloads/sparsity/sparsity_args.h): 2,048 bytes, A
(16 lines of 64 B, row i = line i) then B (line p holds column j's E consecutive k-elements at bytes (j*E+e)*size);
accum.c reads 32-bit words, so fp16's word pairs low halves with low halves and int8's byte e with byte e. C is 256
little-endian 32-bit words, C[i][j] at word i*16+j, minion m's tile at byte m*1024 of the out buffer, as checkC reads
it (workloads/sparsity/host/main.cpp) and as the kernel stores it (kernel/sparsity.c run_fma: row i in f[2i], f[2i+1]).

The verdict of one launch (registered in README.md before any card use of this tool):
  PASS      every participating minion holds the same C, and it equals the reference bit for bit (int8: mod 2^32).
  ROUNDING  floats only: every minion holds the same C, it is not the reference, but every word lies inside the
            rigorous rounding envelope of the exact sum (exact rational n x S, operands read as the unit reads them,
            each step's rounding bounded: fp32 2^-24 of the step's result, fp16 2^-21 of the step's largest term, plus
            2^-126 a step for flushing). The envelope is loose at launch lengths (about +-26% of |C| for fp32 at
            n = 550,000, wider for fp16), so ROUNDING says "the right size and sign", not "right": it is reported, and
            the registered rule counts only PASS as checked-exact.
  FAIL      anything else: minions disagree, a word outside the envelope, an int8 word off, no result read.
Diagnostics name what a failing C does equal (the reference at n-1 or n+1, the run's other n, the poison word, zeros,
another tile's C in the same log, A and B swapped), the words and ulps off, and the first mismatch.
Amendment A1 (Tue 3 Nov 2026, before any card use; README.md):
  UNMODELLED  the C record says the launch ran with the tensor mask on (use_mask 1, from --row-mask) or with B streamed
            through TenB (b_stream 1, from --b-stream). The reference models neither: not checked. The diagnostics
            still say whether its C equals the unmasked, L1 reference (equals_unmasked_reference).
  A record cut short (its writer killed mid-write), a C record with no tiles record before it, or tiles whose bytes do
  not match their fnv: that launch is FAIL (no result), and every other launch in the log is judged. A C record from
  the patch of 60b91395, which did not log the mask and the stream, is judged as above and marked flags_logged false.
"""
import argparse
import concurrent.futures as cf
import hashlib
import json
import os
import re
import shutil
import struct
import subprocess
import sys
import tempfile
import threading
from fractions import Fraction

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
ENGINE_SRC = os.path.join(ROOT, "rtl-sim", "fma_toggle_v2", "accum.c")
ENGINE_SHA = "dc47efbc32e3c45bc935fc1fc1452c81f899423affb2ff94fcb393cf15ef10cf"
POISON_WORD = 0x7FBADBAD     # what the patched host's --c-poison writes before each launch (patch_host_ccheck.py)
TYPES = ("fp32", "fp16", "int8")
MINIONS = 1024
U32 = 2.0 ** -24
REC = '{"ccheck":1,'         # every record of the C log starts with these bytes (patch_host_ccheck.py, sparsity_ccheck.sh)
# What silicon has read, for `domain`'s first-read notes. E104's 44 tiles (1 Nov 2026): the widest exponent spread (max
# minus min biased exponent over a tile's nonzero normal operands, A and B together) and the most distinct nonzero
# operand magnitudes in one tile; validate_ccheck.py V8 recomputes both from E104's committed tiles. int8: the host's
# own --values small tiles, read back by checkC on 25 Sep 2026, hold values in [-3, 3] and never wrap (n = 20,000).
E104_SPREAD = {"fp32": 61, "fp16": 25}
E104_DISTINCT = {"fp32": 481, "fp16": 662}
SMALL_INT8 = 3


def sha256(b):
    return hashlib.sha256(b).hexdigest()


def fnv64(b):
    h = 1469598103934665603
    for x in b:
        h ^= x
        h = (h * 1099511628211) & 0xFFFFFFFFFFFFFFFF
    return "%016x" % h


def words(b):
    return list(struct.unpack("<%dI" % (len(b) // 4), b))


# ------------------------------------------------------------------------------------------------ the engine

def default_cache():
    return os.environ.get("CCHECK_CACHE") or os.path.expanduser("~/.cache/ccheck-" + ENGINE_SHA[:8])


_ENGINE_LOCK = threading.Lock()


def engine(cache):
    """Build accum.c (sha256-pinned) once into the cache dir; return the binary's path. Thread-safe."""
    with _ENGINE_LOCK:
        src = open(ENGINE_SRC, "rb").read()
        if sha256(src) != ENGINE_SHA:
            raise SystemExit(f"ccheck: {ENGINE_SRC} is not the accum.c E104 validated (sha256 {sha256(src)})")
        os.makedirs(cache, exist_ok=True)
        exe = os.path.join(cache, "accum-" + ENGINE_SHA[:12])
        if not os.path.exists(exe):
            cc = os.environ.get("CC", "cc")
            fd, tmp = tempfile.mkstemp(prefix="accum-build-", dir=cache)
            os.close(fd)
            subprocess.run([cc, "-O2", "-o", tmp, ENGINE_SRC, "-lm"], check=True)
            os.chmod(tmp, 0o755)
            os.replace(tmp, exe)
        return exe


def ref_many(typ, tile, ns, cache):
    """{n: C bytes (1,024)} for every n, from one engine run per tile (accum.c continues from the previous n)."""
    assert typ in TYPES and len(tile) == 2048
    key = typ + "-" + sha256(tile)[:20]
    out, todo = {}, []
    for n in sorted(set(int(x) for x in ns)):
        if n < 1:
            raise ValueError("n must be >= 1")
        p = os.path.join(cache, key + "-%d.bin" % n)
        if os.path.exists(p):
            out[n] = open(p, "rb").read()
        else:
            todo.append(n)
    if todo:
        exe = engine(cache)
        with tempfile.TemporaryDirectory(dir=cache) as d:
            tp = os.path.join(d, "tile.bin")
            open(tp, "wb").write(tile)
            cmd = ["nice", "-n", "10", exe, typ, tp] + [str(n) for n in todo]
            subprocess.run(cmd, cwd=d, check=True, stdout=subprocess.DEVNULL)
            for n in todo:
                b = open(os.path.join(d, "accum_%d.bin" % n), "rb").read()
                assert len(b) == 1024
                os.replace(os.path.join(d, "accum_%d.bin" % n), os.path.join(cache, key + "-%d.bin" % n))
                out[n] = b
    return out


# ------------------------------------------------------------------------------------------------ exact sums

def f32(w):
    """IEEE binary32 word -> Fraction (finite only), denormals read as zero (the unit's DAZ)."""
    e = (w >> 23) & 0xFF
    if e == 0xFF:
        return None
    if e == 0:
        return Fraction(0)
    m = (w & 0x7FFFFF) | 0x800000
    v = Fraction(m) * (Fraction(2) ** (e - 150))
    return -v if w >> 31 else v


def f16(h):
    e = (h >> 10) & 0x1F
    if e == 0x1F:
        return None
    if e == 0:
        return Fraction(0)      # fp16_model.mant16: an exponent of 0 reads as zero
    v = Fraction((h & 0x3FF) | 0x400) * (Fraction(2) ** (e - 25))
    return -v if h >> 15 else v


def exact_terms(typ, tile):
    """Per (i, j): (S, P, steps): S = exact sum of one op's products (as the unit reads its operands), P = the sum of their
    magnitudes, steps = the word pairs a op actually updates C on (the raw-word gate), for the rounding envelope."""
    w = words(tile)
    A = [w[i * 16:(i + 1) * 16] for i in range(16)]
    B = [w[256 + k * 16:256 + (k + 1) * 16] for k in range(16)]
    res = {}
    for i in range(16):
        for j in range(16):
            S, P, steps, bad = Fraction(0), Fraction(0), 0, False
            for k in range(16):
                a, b = A[i][k], B[k][j]
                if typ == "int8":
                    for e in range(4):
                        x = ((a >> (8 * e)) & 0xFF) - (((a >> (8 * e)) & 0x80) << 1)
                        y = ((b >> (8 * e)) & 0xFF) - (((b >> (8 * e)) & 0x80) << 1)
                        S += x * y
                    continue
                if k > 0 and (a == 0 or b == 0):
                    continue                     # gated: C unchanged (op 0's k = 0 multiply is not, but adds 0 then)
                if typ == "fp32":
                    x, y = f32(a), f32(b)
                    if x is None or y is None:
                        bad = True
                        continue
                    p = x * y
                    S += p
                    P += abs(p)
                else:
                    xl, xh, yl, yh = f16(a & 0xFFFF), f16(a >> 16), f16(b & 0xFFFF), f16(b >> 16)
                    if None in (xl, xh, yl, yh):
                        bad = True
                        continue
                    pl, ph = xl * yl, xh * yh
                    S += pl + ph
                    P += abs(pl) + abs(ph)
                steps += 1
            res[(i, j)] = (S, P, steps, bad)
    return res


def envelope(typ, n, S, P, steps):
    """Rigorous bound on |C_unit - n S| after n ops. Each step adds its rounding error, at most u times the step's
    largest magnitude, which is at most |exact partial sum| + |error so far| + |this step's terms|. With the exact
    partial sums bounded by m|S| + P at op m: err <= u (1+u)^N (K|S| n(n-1)/2 + 2 n K P) + N 2^-126, N = n K."""
    u = U32 if typ == "fp32" else 2.0 ** -21
    K = max(steps, 1)
    N = n * K
    Sa, Pf = abs(float(S)), float(P)
    grow = (1 + u) ** N if N * u < 700 else float("inf")
    return u * grow * (K * Sa * n * (n - 1) / 2 + 2 * n * K * Pf) + N * 2.0 ** -126


def word_value(typ, w):
    if typ == "fp32" or typ == "fp16":
        e = (w >> 23) & 0xFF
        if e == 0xFF:
            return None
        return float(f32(w)) if e else (-0.0 if w >> 31 else 0.0)
    return w - (1 << 32) if w & 0x80000000 else w


def ulp_key(w):
    return -(w & 0x7FFFFFFF) if w >> 31 else w


# ------------------------------------------------------------------------------------------------ one launch

def judge(typ, tile, n, groups, participants, refs, others=None, flags=None):
    """groups: [{"count", "first_minion", "minions", "hex"}]; refs: {n: bytes} holding at least n (and n-1, n+1 when
    computed); flags: the C record's {"use_mask", "row_mask", "b_stream"}, or None for a record that does not log them
    (the patch of 60b91395). Returns the verdict dict."""
    v = {"type": typ, "n": n, "participants": participants, "groups": len(groups),
         "counts": sorted((g["count"] for g in groups), reverse=True)}
    ref = refs[n]
    total = sum(g["count"] for g in groups)
    if not groups or total != participants:
        v.update(verdict="FAIL", why=f"read {total} minions of {participants}")
        return v
    unmodelled = []
    if flags is None:
        v["flags_logged"] = False
    else:
        v["flags"] = flags
        if int(flags.get("use_mask", 0)):
            unmodelled.append("the tensor mask is on (row_mask %s)" % flags.get("row_mask"))
        if int(flags.get("b_stream", 0)):
            unmodelled.append("B streams through TenB")
    rw = words(ref)
    out = []
    unanimous = len(groups) == 1
    poison = struct.pack("<I", POISON_WORD) * 256
    for g in groups:
        b = bytes.fromhex(g["hex"])
        gw = words(b)
        diff = [x for x in range(256) if gw[x] != rw[x]]
        d = {"count": g["count"], "first_minion": g.get("first_minion"), "words_off": len(diff)}
        if diff:
            x = diff[0]
            d["first"] = {"i": x // 16, "j": x % 16, "got": "%08x" % gw[x], "want": "%08x" % rw[x]}
            if typ == "int8":
                d["max_abs_off"] = max(abs(((gw[x] - rw[x] + (1 << 31)) % (1 << 32)) - (1 << 31)) for x in diff)
            else:
                d["max_ulp"] = max(abs(ulp_key(gw[x]) - ulp_key(rw[x])) for x in diff)
                d["zero_sign_only"] = all({gw[x], rw[x]} == {0, 0x80000000} for x in diff)
            eq = [f"ref(n={m})" for m, rb in sorted(refs.items()) if m != n and rb == b]
            if b == poison:
                eq.append("poison (no C stored)")
            if b == bytes(1024):
                eq.append("zeros")
            for name, ob in (others or {}).items():
                if ob == b:
                    eq.append(name)
            if eq:
                d["equals"] = eq
        out.append(d)
    v["by_group"] = out
    exact = unanimous and out[0]["words_off"] == 0
    if unmodelled:                       # amendment A1: neither the mask nor the stream is modelled
        v.update(verdict="UNMODELLED", why="; ".join(unmodelled) + ": the reference models neither, so not checked",
                 equals_unmasked_reference=exact)
        return v
    if exact:
        v["verdict"] = "PASS"
        return v
    if not unanimous:
        v.update(verdict="FAIL", why="minions disagree: %d distinct C among %d" % (len(groups), participants))
        return v
    if typ == "int8":
        v.update(verdict="FAIL", why="int8 C is not the exact sum mod 2^32")
        return v
    # floats, unanimous, not bit-exact: inside the rounding envelope of the exact sum?
    terms = exact_terms(typ, tile)
    gw = words(bytes.fromhex(groups[0]["hex"]))
    worst, outside, undecided = 0.0, 0, 0
    for i in range(16):
        for j in range(16):
            S, P, steps, bad = terms[(i, j)]
            got = word_value(typ, gw[i * 16 + j])
            if bad:
                undecided += 1           # a NaN/Inf operand: no exact sum to bound against
                continue
            try:
                bound = envelope(typ, n, S, P, steps)
                true = float(n * S)
            except OverflowError:
                undecided += 1
                continue
            near_edge = bound == float("inf") or abs(true) + bound >= 3.4e38
            if near_edge:
                undecided += 1           # the envelope reaches overflow: an Inf or a clamp cannot be ruled out
                continue
            if got is None:
                outside += 1             # Inf/NaN where the envelope stays finite
                continue
            off = abs(got - true)
            if off > bound:
                outside += 1
            if bound > 0:
                worst = max(worst, off / bound)
    v["envelope"] = {"words_outside": outside, "undecided": undecided, "worst_off_over_bound": round(worst, 6)}
    if outside == 0 and undecided == 0:
        v.update(verdict="ROUNDING", why="unanimous, not bit-exact, inside the rounding envelope of the exact sum")
    else:
        v.update(verdict="FAIL", why=f"{outside} word(s) outside the rounding envelope, {undecided} undecided")
    return v


# ------------------------------------------------------------------------------------------------ inputs

def tile_path_from_values(values, roots):
    p = values[5:] if values.startswith("file:") else values
    if os.path.exists(p):
        return p
    k = p.find("tools/claims-v3/")
    if k >= 0:
        for r in roots:
            q = os.path.join(r, p[k:])
            if os.path.exists(q):
                return q
    return None


def _records(line):
    """One line of a C log -> [(record or None, text)]. A record cut short (its writer killed mid-write) ends with no
    newline, so the next process's first record can share its line: such a line is split where each record starts,
    and a piece that does not parse comes back as None."""
    try:
        return [(json.loads(line), line)]
    except ValueError:
        pass
    cuts = [m.start() for m in re.finditer(re.escape(REC), line)]
    if not cuts or cuts[0] != 0:
        cuts = [0] + cuts
    out = []
    for a, b in zip(cuts, cuts[1:] + [len(line)]):
        piece = line[a:b]
        try:
            out.append((json.loads(piece), piece))
        except ValueError:
            out.append((None, piece))
    return out


def _field(text, key, pat):
    m = re.search('"%s":%s' % (key, pat), text)
    return m.group(1) if m else None


FLAG_KEYS = ("use_mask", "row_mask", "b_stream")
HOST_KEYS = ("host", "host_sha256", "kernel", "kernel_sha256", "kernel_from")


def load_clog(paths):
    """The C log's lines (the patched host's --c-log, the wrapper's host records) -> launches
    [(typ, tile bytes or None, n, groups, participants, meta)]. A launch whose C record was cut short, whose tiles
    record is missing or was cut short, or whose tiles' bytes do not match their fnv comes back with tile None and
    meta["broken"] saying why: check_launches judges it FAIL (no result) and judges every other launch (amendment A1)."""
    tiles, launches = {}, []
    for path in paths:
        host = None
        for ln, line in enumerate(open(path, errors="replace"), 1):
            line = line.strip()
            if not line:
                continue
            for r, text in _records(line):
                base = {"log": os.path.basename(path), "line": ln}
                if host:
                    base.update(host)
                if r is None:                      # a record cut short
                    kind = _field(text, "kind", r'"(\w+)"')
                    if kind == "host":
                        continue
                    if kind == "tiles":
                        fnv = _field(text, "fnv", r'"([0-9a-f]{16})"')
                        if fnv:
                            tiles[fnv] = (None, "its tiles record was cut short")
                        continue
                    it = _field(text, "iters", r"(\d+)")
                    lno = _field(text, "launch", r"(-?\d+)")
                    base.update(broken="its C record was cut short (the run stopped mid-write)",
                                launch=int(lno) if lno is not None else None)
                    launches.append((_field(text, "type", r'"(\w+)"') or "?", None, int(it) if it else None, [], 0, base))
                    continue
                if r.get("ccheck") != 1:
                    continue
                kind = r.get("kind")
                if kind == "host":
                    host = {k: r.get(k) for k in HOST_KEYS}
                    continue
                if kind == "tiles":
                    try:
                        t = bytes.fromhex(r["a"]) + bytes.fromhex(r["b"])
                    except (KeyError, ValueError):
                        t = b""
                    if len(t) != 2048 or fnv64(t) != r.get("fnv"):
                        tiles[r.get("fnv")] = (None, "its tiles record's bytes do not match their fnv")
                    else:
                        tiles[r["fnv"]] = (t, r.get("values"))
                    continue
                if kind != "c":
                    continue
                meta = dict(base, launch=r.get("launch"), ok=r.get("ok"), poison=r.get("poison"),
                            t_start_ms=r.get("t_start_ms"), t_end_ms=r.get("t_end_ms"))
                flags = {k: r[k] for k in FLAG_KEYS if k in r} or None
                entry = tiles.get(r.get("fnv"))
                groups = r.get("groups") if r.get("ok") else []
                if entry is None or entry[0] is None:
                    meta["broken"] = "no tiles record before this C record" if entry is None else entry[1]
                    launches.append((r.get("type", "?"), None, int(r.get("iters", 0)), [], int(r.get("participants", 0)), meta))
                    continue
                if any(len(g.get("hex", "")) != 2048 for g in groups or []):
                    meta["broken"] = "a group's C is not 1,024 bytes"
                    launches.append((r["type"], None, int(r["iters"]), [], int(r["participants"]), meta))
                    continue
                t, values = entry
                meta["values"] = values
                meta["flags"] = flags
                launches.append((r["type"], t, int(r["iters"]), groups or [], int(r["participants"]), meta))
    return launches


def load_e104(path, roots):
    launches = []
    for ln, line in enumerate(open(path), 1):
        r = json.loads(line)
        sp = r["sparsity"]
        tp = tile_path_from_values(sp["values"], roots)
        if tp is None:
            raise SystemExit(f"{path}:{ln}: cannot find the tile {sp['values']}")
        typ = r["tile"].split(".")[0]
        t = open(tp, "rb").read()
        if int(sp["iters"]) != int(r["n"]):
            raise SystemExit(f"{path}:{ln}: the launch's iters {sp['iters']} is not n {r['n']}")
        groups = []
        for gsha, g in sorted(r["groups"].items()):
            if sha256(bytes.fromhex(g["hex"])) != gsha:
                raise SystemExit(f"{path}:{ln}: a group's hex does not match its sha256")
            groups.append({"count": g["minions"], "first_minion": g["first_minion"], "hex": g["hex"]})
        meta = {"log": os.path.basename(path), "line": ln, "tile": r["tile"], "values": sp["values"], "ok": sp["ok"]}
        launches.append((typ, t, int(r["n"]), groups, int(sp["minions"]), meta))
    return launches


def check_launches(launches, cache, jobs, neighbours=True):
    """Every launch judged; refs computed once per (type, tile) for every n needed (n, and n-1, n+1 for diagnostics)."""
    need = {}
    for typ, t, n, *_ in launches:
        if t is None:                   # a broken record: judged FAIL below, no reference needed
            continue
        s = need.setdefault((typ, t), set())
        s.add(n)
        if neighbours:
            s.update(m for m in (n - 1, n + 1) if m >= 1)
    refs = {}
    engine(cache)                       # built once, before the workers start
    with cf.ThreadPoolExecutor(max_workers=max(1, jobs)) as ex:
        futs = {ex.submit(ref_many, typ, t, sorted(ns), cache): (typ, t) for (typ, t), ns in need.items()}
        for f in cf.as_completed(futs):
            refs[futs[f]] = f.result()
    # other tiles' C at the same n, for "equals another tile's C" diagnostics (cheap: only refs already computed)
    out = []
    for typ, t, n, groups, parts, meta in launches:
        if t is None:
            v = {"type": typ, "n": n, "participants": parts, "groups": 0, "counts": [], "verdict": "FAIL",
                 "why": "no result: " + meta["broken"]}
            v.update(meta)
            out.append(v)
            continue
        others = {}
        for (typ2, t2), r2 in refs.items():
            if t2 != t and typ2 == typ and n in r2:
                others[f"another tile's C ({sha256(t2)[:12]})"] = r2[n]
        swapped = t[1024:] + t[:1024]
        if (typ, swapped) in refs and n in refs[(typ, swapped)]:
            others["A and B swapped"] = refs[(typ, swapped)][n]
        v = judge(typ, t, n, groups, parts, refs[(typ, t)], others,
                  flags=meta.get("flags") if "flags" in meta else None)
        v["tile_sha256"] = sha256(t)
        v.update(meta)
        out.append(v)
    return out


VERDICTS = ("PASS", "ROUNDING", "UNMODELLED", "FAIL")


def summarize(verdicts):
    s = {"launches": len(verdicts)}
    for k in VERDICTS:
        s[k] = sum(v["verdict"] == k for v in verdicts)
    s["by_type"] = {t: {k: sum(v["verdict"] == k and v["type"] == t for v in verdicts) for k in VERDICTS}
                    for t in TYPES if any(v["type"] == t for v in verdicts)}
    s["broken_records"] = sum("broken" in v for v in verdicts)
    s["flags_unlogged"] = sum(v.get("flags_logged") is False for v in verdicts)
    bins = sorted({(v.get("host_sha256"), v.get("kernel_sha256")) for v in verdicts if v.get("host_sha256")})
    if bins:
        s["binaries"] = [{"host_sha256": h, "kernel_sha256": k} for h, k in bins]
    s["all_pass"] = s["PASS"] == s["launches"] and s["launches"] > 0
    return s


# ------------------------------------------------------------------------------------------------ domain

def operand_stats(typ, tile):
    """(distinct nonzero normal operand magnitudes, exponent spread, lowest biased exponent of A's and of B's nonzero
    normal operands) for a float tile; for int8 (distinct nonzero values, 0, (largest |A|, largest |B|))."""
    w = words(tile)
    mags, exps, lo = set(), [], [None, None]
    for side, ws in ((0, w[:256]), (1, w[256:])):
        for x in ws:
            if typ == "int8":
                for e in range(4):
                    b = (x >> (8 * e)) & 0xFF
                    v = b - 256 if b > 127 else b
                    if v:
                        mags.add(abs(v))
                        lo[side] = max(lo[side] or 0, abs(v))
                continue
            hs = [x] if typ == "fp32" else [x & 0xFFFF, x >> 16]
            for h in hs:
                m, e = (h & 0x7FFFFFFF, (h >> 23) & 0xFF) if typ == "fp32" else (h & 0x7FFF, (h >> 10) & 0x1F)
                emax = 0xFF if typ == "fp32" else 0x1F
                if m and 0 < e < emax:
                    mags.add(m)
                    exps.append(e)
                    lo[side] = e if lo[side] is None else min(lo[side], e)
    spread = (max(exps) - min(exps)) if exps else 0
    return len(mags), spread, tuple(lo)


def partial_bound(typ, tile, n):
    """A rigorous bound on |C| at every op up to n, every word (floats): an exact partial sum after m ops, mid-op
    included, is at most m|S| + P, and the computed one is within envelope(n) of it (envelope is monotone in n)."""
    worst = 0.0
    for (i, j), (S, P, steps, bad) in exact_terms(typ, tile).items():
        if bad:
            continue
        try:
            b = n * abs(float(S)) + float(P) + envelope(typ, n, S, P, steps)
        except OverflowError:
            b = float("inf")
        worst = max(worst, b)
    return worst


def domain(typ, tile, n, cache):
    """Is this tile's arithmetic, at every op up to n, inside the operand and result classes silicon reads have covered
    (finite normal or zero operands; no Inf, no overflow and no fp16 clamp at ANY op up to n, by a rigorous bound on
    every partial sum; for fp32 no sum in the range the unit flushes to zero)? "inside" is that test. The first-read
    notes say what of the tile's values no silicon read has covered, though its classes are inside: float tiles spread
    wider, or with more distinct magnitudes, than any of E104's 44 tiles; int8 operands beyond the [-3, 3] the host read
    back on 25 Sep 2026, or a 32-bit wrap. A launch on such a tile is that range's first silicon read, so a FAIL there
    can be the model's. Also lists the final n's C: Inf/NaN words, and words at the largest finite."""
    w = words(tile)
    why, first = [], []
    distinct, spread, lo = operand_stats(typ, tile)
    if typ == "int8":
        big = max(x or 0 for x in lo)
        if big > SMALL_INT8:
            first.append(f"operands up to |{big}| (the host's small-integer read-backs of 25 Sep held [-3, 3])")
        terms = exact_terms("int8", tile)
        wraps = sum(abs(n * int(terms[(i, j)][0])) >= (1 << 31) for i in range(16) for j in range(16))
        if wraps:
            first.append(f"{wraps} of 256 words wrap by n={n} (the 32-bit wrap, never read on silicon)")
    else:
        if spread > E104_SPREAD[typ]:
            first.append(f"exponent spread {spread}, wider than any tile E104 read ({E104_SPREAD[typ]})")
        if distinct > E104_DISTINCT[typ]:
            first.append(f"{distinct} distinct operand magnitudes, more than any tile E104 read ({E104_DISTINCT[typ]})")
        bound = partial_bound(typ, tile, n)
        if bound >= 2.0 ** 127:
            why.append(f"a partial sum may reach 2^127 by n={n} (bound {bound:.3g}): an overflow (fp32: Inf, which stays) "
                       "or fp16's clamp at the largest finite cannot be ruled out: never read on silicon")
        if typ == "fp32" and lo[0] is not None and lo[1] is not None and lo[0] + lo[1] - 300 < -126:
            # every product and every computed sum is a multiple of 2^(min E_A + min E_B - 300); at or above 2^-126 a
            # nonzero sum is never denormal, so the flush never fires (proof in README.md, "The domain check")
            why.append("a sum may fall below 2^-126, where the unit flushes it to zero (products' grain 2^%d): never "
                       "read on silicon" % (lo[0] + lo[1] - 300))
    for side, ws in (("A", w[:256]), ("B", w[256:])):
        nan = den = negz = 0
        for x in ws:
            if typ == "fp32":
                e = (x >> 23) & 0xFF
                nan += e == 0xFF
                den += e == 0 and (x & 0x7FFFFF) != 0
                negz += x == 0x80000000
            elif typ == "fp16":
                for h in (x & 0xFFFF, x >> 16):
                    e = (h >> 10) & 0x1F
                    nan += e == 0x1F
                    den += e == 0 and (h & 0x3FF) != 0
                    negz += h == 0x8000
        if nan:
            why.append(f"{side}: {nan} NaN/Inf encodings")
        if den:
            why.append(f"{side}: {den} denormal operands (read as zero: the RTL's rule, never read back on silicon)")
        if negz:
            why.append(f"{side}: {negz} -0 operands (E104's z_ tiles read back -0 at k >= 1: inside)")
    c = ref_many(typ, tile, [n], cache)[n]
    cw = words(c)
    if typ != "int8":
        inf = sum(((x >> 23) & 0xFF) == 0xFF for x in cw)
        clamp = sum((x & 0x7FFFFFFF) == 0x7F7FFFFF for x in cw)
        if inf:
            why.append(f"C at n={n}: {inf} words Inf/NaN (overflow: never read back on silicon)")
        if clamp:
            why.append(f"C at n={n}: {clamp} words at the largest finite (fp16's clamp, or fp32 at the edge: unread)")
    d = {"type": typ, "n": n, "sha256": sha256(tile),
         "inside": not [x for x in why if "inside" not in x], "notes": why, "first_read": first,
         "distinct": distinct, "spread": spread}
    if typ != "int8":
        d["partial_bound"] = float("%.4g" % partial_bound(typ, tile, n))
    return d


# ------------------------------------------------------------------------------------------------ main

def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    for name in ("check", "e104"):
        p = sub.add_parser(name)
        p.add_argument("logs", nargs="+")
        p.add_argument("--out")
        p.add_argument("--jobs", type=int, default=6)
        p.add_argument("--cache", default=default_cache())
        p.add_argument("--root", action="append", default=[], help="repo roots to find tiles under (e104)")
        p.add_argument("--no-neighbours", action="store_true", help="skip the n-1 / n+1 diagnostics (faster)")
    p = sub.add_parser("ref")
    p.add_argument("type", choices=TYPES)
    p.add_argument("tile")
    p.add_argument("n", nargs="+", type=int)
    p.add_argument("--cache", default=default_cache())
    p = sub.add_parser("domain")
    p.add_argument("paths", nargs="+")
    p.add_argument("--n", type=int, default=1600000)
    p.add_argument("--jobs", type=int, default=6)
    p.add_argument("--cache", default=default_cache())
    p.add_argument("--out", help="write every tile's row (notes, first-read notes, spread, bound) as JSON")
    a = ap.parse_args()

    if a.cmd == "ref":
        t = open(a.tile, "rb").read()
        r = ref_many(a.type, t, a.n, a.cache)
        for n in a.n:
            print(n, r[n].hex())
        return 0
    if a.cmd == "domain":
        files = []
        for p in a.paths:
            if os.path.isdir(p):
                for dp, _, fs in os.walk(p):
                    files += [os.path.join(dp, f) for f in sorted(fs) if f.endswith(".bin")]
            else:
                files.append(p)
        rows = []
        with cf.ThreadPoolExecutor(max_workers=max(1, a.jobs)) as ex:
            futs = {}
            for f in sorted(files):
                b = os.path.basename(f)
                typ = next((t for t in TYPES if b.startswith(t) or ("/" + t + "/") in f), None)
                t = open(f, "rb").read()
                if typ is None or len(t) != 2048:
                    rows.append({"file": f, "inside": False, "notes": ["not a 2,048-byte tile of a known type"]})
                    continue
                futs[ex.submit(domain, typ, t, a.n, a.cache)] = f
            for fu in cf.as_completed(futs):
                d = fu.result()
                d["file"] = os.path.relpath(futs[fu], ROOT) if futs[fu].startswith(ROOT) else futs[fu]
                rows.append(d)
        rows.sort(key=lambda r: r["file"])
        for r in rows:
            fr = r.get("first_read") or []
            print(("inside " if r["inside"] else "OUTSIDE"), r["file"], "; ".join(r["notes"]),
                  ("| first silicon read: " + "; ".join(fr)) if fr else "")
        s = {"tiles": len(rows), "inside": sum(r["inside"] for r in rows),
             "first_silicon_read": sum(bool(r.get("first_read")) for r in rows)}
        print(json.dumps(s))
        if a.out:
            json.dump({"summary": s, "n": a.n, "tiles": rows}, open(a.out, "w"), indent=1)
        return 0 if all(r["inside"] for r in rows) else 1

    roots = a.root + [ROOT]
    launches = load_clog(a.logs) if a.cmd == "check" else [x for p in a.logs for x in load_e104(p, roots)]
    verdicts = check_launches(launches, a.cache, a.jobs, neighbours=not a.no_neighbours)
    s = summarize(verdicts)
    for v in verdicts:
        tag = v.get("tile") or (v.get("values") or "")[-48:]
        line = f"{v['verdict']:8s} {v['type']} n={v['n']} {tag} launch={v.get('launch', '-')} groups={v['groups']}"
        if v["verdict"] != "PASS":
            line += " | " + v.get("why", "") + " | " + json.dumps(v.get("by_group"))[:400]
        print(line)
    print(json.dumps(s))
    if a.out:
        json.dump({"summary": s, "launches": verdicts, "engine": {"src": os.path.relpath(ENGINE_SRC, ROOT),
                                                                  "sha256": ENGINE_SHA}}, open(a.out, "w"), indent=1)
    return 0 if s["all_pass"] else 1


if __name__ == "__main__":
    sys.exit(main())
