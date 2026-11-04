#!/usr/bin/env python3
"""E165 (Q141(g)): what E165's predictions writer, protocol writer, runner, queue, scorer and self-test share. Standard library only (the runner
must work on aifoundry2's python without numpy). It is E160's e160_common.py with pool 7's names, M9's aifoundry2 part as the primary model, and
the same check-of-C pins.

  * the frozen inputs and their sha256: Q140(x)'s predictions for aifoundry2 (predictions-blind7-aifoundry2.json, whose M9.a2_q140l block is M9's
    aifoundry2 part), blind pool 7's manifest (blind7.json) and MANIFEST, the 82 W list (admission-aifoundry2-82w.json), M9's and M8's D per tile
    (a2-inputs-aifoundry2.json): lab 75802201, notes 3c9bb2ba; M9's aifoundry2 part, m9_a2.json and its frozen predictor predict_m9_a2.py (Q140(l),
    5b98bd5c; registration 245caffe; corrections 5c98c0c5);
  * Q139(k)'s check of C as committed after its verification (4946a992): the wrapper, the host patch and its build script, and the C-logging host
    built from them on aifoundry2 on Tue 3 Nov 2026 (E160's pin): E160 ran it, and E165 runs the same binary or refuses;
  * E80's kernel and sampler (E143's and E160's pins);
  * the pool's tiles as run values (`file:` a tile of tools/claims-v3/kinds/blind7/tiles/<type>/) and their labels (`b7-<type>.<name>`);
  * the tile check against blind7.json (2,048 B; sha256 of the whole, of A and of B);
  * the scoring helpers: the seeded bootstrap of an rms drawn from reference errors, the binomial coverage line (E160's, unchanged), and the
    paired bootstrap of an rms difference over tiles (E160's reported form, with E165's draws and seed for the registered "resolved" test);
  * the primary model's call: predict_m9_a2.burst, imported from its committed directory after its sha256 and m9_a2.json's are checked.

SPDX-License-Identifier: Apache-2.0
"""
import hashlib
import json
import math
import os
import random
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, "..", "..", ".."))
POOL_REL = "tools/claims-v3/kinds/blind7"
PRED_REL = f"{POOL_REL}/predictions-blind7-aifoundry2.json"
MAN_REL = f"{POOL_REL}/blind7.json"
MANIFEST_REL = f"{POOL_REL}/MANIFEST"
ADM_REL = f"{POOL_REL}/admission-aifoundry2-82w.json"
A2IN_REL = f"{POOL_REL}/a2-inputs-aifoundry2.json"
Q140L_REL = "docs/reports/data/2026-11-04-q140l-a2-session-terms"
M9A2_REL = f"{Q140L_REL}/m9_a2.json"
PM9A2_REL = f"{Q140L_REL}/predict_m9_a2.py"
FROZEN = {  # pool 7 and its predictions: lab 75802201 (README-predictions.md, Files); M9's aifoundry2 part: 5b98bd5c (unchanged by 5c98c0c5)
    PRED_REL: "e2c467c4a60d6409fb9139e8b109ad5f5e758cc1747367984e164ce397c57c01",
    MAN_REL: "24070633ede0b73b67b8f159db989f1007d43343a7a8d943ac2e2d14f16b9552",
    MANIFEST_REL: "92d2357232c5284b65650c8e1769b231d5f330f399c7bc6f80eedcb17d51557a",
    ADM_REL: "c330806ae93b86ac83e835f50b66398688a002071c817cf77e0d4e0a11caa384",
    A2IN_REL: "ff4f4eaa49dfdcc5aeb59c86ad8225889d737f5d41eb02908e0dc8c1545c3933",
    M9A2_REL: "cc6fbccc4b63fa80575e91abb02c6296a24ac97984fd52a232dbea04a6c6fec8",
    PM9A2_REL: "420b887ea57cfdfec7da6a1f4f3f2017a92da9c9cf86d71cefe8c17ec1fcf284",
}
CCHECK_REL = "tools/claims-v3/ccheck"
CCHECK_FROZEN = {  # Q139(k) after its verification, 4946a992 (E160's pins, unchanged)
    f"{CCHECK_REL}/sparsity_ccheck.sh": "d00158d454596a8325ff3a7ffa3dff6e80a2e1798516b022009450f63443b9b7",
    f"{CCHECK_REL}/patch_host_ccheck.py": "05a8c867f9c408c59437c30333d02f9252ee54d3d5bd2743e49a5b99a358c3ee",
    f"{CCHECK_REL}/build_host_ccheck.sh": "35537915689bfa02c351b895db8ebd79d066e5a80bd432b38a273ac11d39502f",
}
WRAPPER_REL = f"{CCHECK_REL}/sparsity_ccheck.sh"
CC_HOST_REL = "build/ccheck/b/host/sparsity_host"
# the C-logging host E160 ran (built by build_host_ccheck.sh on aifoundry2 at 06:18:30 PST, Tue 3 Nov 2026; tools/claims-v3/e160/logs/
# build-ccheck-aifoundry2.txt). E165 runs the same bytes or refuses: a rebuild gives another sha256 and needs a dated amendment first.
CC_HOST_SHA256 = "eae32a152b8f0861bd2922c500eac217c931c9b464d3274a6bcf346cc986bfd2"
KERNEL_REL = "build/sparsity_t2/kernel/sparsity.elf"
ETTELEM_REL = "build/ettelem-hpl/ettelem"
E80_SHA256 = {  # E143's and E160's pins: the kernel and the sampler of their power passes
    KERNEL_REL: "990807f483cd57aa413083c52e647079b86022768562d5810080852f7fd6ea24",
    ETTELEM_REL: "77a46171c915d3a92898af9ffe04d92b86b65f4d36bc29d58f5c086f8accfeb5",
}
GOVERNED_BELOW_MHZ = 795.0       # the frozen file's split (M9.a2_q140l.group: governed = M9's part predicts the burst below 795 MHz)
LABEL_PREFIX = "b7-"
ZEROS_ANCHORS = ("fp32.anchor7_zeros", "fp16.anchor7_zeros", "int8.anchor7_zeros")   # pool 7's zeros anchors (one tile under three types)
BOOT_DRAWS = 20000
BOOT_SEED = 165
PAIRED_DRAWS = 20000
PAIRED_SEED = 1651
MODELS = ("M9", "M8", "M7", "M6")


def sha256_file(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def sha256_bytes(b):
    return hashlib.sha256(b).hexdigest()


def check_frozen(root=ROOT, ccheck=True):
    """[] if the frozen inputs (and, with ccheck, Q139(k)'s three run-time files) are byte-identical to their commits, else what differs."""
    bad = []
    items = dict(FROZEN)
    if ccheck:
        items.update(CCHECK_FROZEN)
    for rel, want in items.items():
        p = os.path.join(root, rel)
        got = sha256_file(p) if os.path.isfile(p) else None
        if got != want:
            bad.append(f"{rel}: sha256 {got}, frozen {want}")
    return bad


def manifest(root=ROOT):
    return {t["name"]: t for t in json.load(open(os.path.join(root, MAN_REL)))["tiles"]}


def tile_value(t):
    """the run value of a manifest tile: file:<the tile's path from the tree's root>"""
    return f"file:{POOL_REL}/{t['file']}"


def label_of(name):
    return LABEL_PREFIX + name


def name_of(label):
    return label[len(LABEL_PREFIX):] if label.startswith(LABEL_PREFIX) else None


def is_pool_value(values):
    v = str(values)
    return v.startswith(f"file:{POOL_REL}/tiles/") and v.endswith(".bin") and ".." not in v


def check_tile(root, t):
    """None if the tile file is the manifest's (2,048 B; whole, A and B sha256), else why not."""
    p = os.path.join(root, POOL_REL, t["file"])
    if not os.path.isfile(p):
        return f"{t['name']}: {p} missing"
    b = open(p, "rb").read()
    if len(b) != 2048:
        return f"{t['name']}: {len(b)} bytes, not 2048"
    s = t["sha256"]
    got = {"whole": sha256_bytes(b), "a": sha256_bytes(b[:1024]), "b": sha256_bytes(b[1024:])}
    for k in ("whole", "a", "b"):
        if got[k] != s[k]:
            return f"{t['name']}: sha256 {k} {got[k]}, manifest {s[k]}"
    return None


def rms(xs):
    xs = [x for x in xs if x is not None]
    return math.sqrt(sum(x * x for x in xs) / len(xs)) if xs else None


def mean(xs):
    xs = [x for x in xs if x is not None]
    return sum(xs) / len(xs) if xs else None


def boot_rms_range(errors, n, draws=BOOT_DRAWS, seed=BOOT_SEED):
    """(the 2.5% point, the 97.5% point) of the rms of n errors drawn with replacement from `errors` (E160's form), seeded."""
    errors = [float(e) for e in errors if e is not None]
    if not errors or n < 1:
        return None, None
    rng = random.Random(seed * 1000003 + n * 101 + len(errors))
    vals = []
    for _ in range(draws):
        s = 0.0
        for _ in range(n):
            e = errors[rng.randrange(len(errors))]
            s += e * e
        vals.append(math.sqrt(s / n))
    vals.sort()
    return vals[int(0.025 * (draws - 1))], vals[int(0.975 * (draws - 1))]


def paired_rms_diff(a, b, draws=PAIRED_DRAWS, seed=PAIRED_SEED):
    """the point and the 95% percentile interval of rms(a) - rms(b) over tiles drawn with replacement, a and b paired by tile (E160's paired_boot
    with E165's draws and seed); None with fewer than 2 tiles"""
    if len(a) < 2 or len(a) != len(b):
        return None
    rng = random.Random(seed + 7919 * len(a))
    vals = []
    n = len(a)
    for _ in range(draws):
        idx = [rng.randrange(n) for _ in range(n)]
        vals.append(rms([a[i] for i in idx]) - rms([b[i] for i in idx]))
    vals.sort()
    return {"point": rms(a) - rms(b), "ci95": [vals[int(0.025 * (draws - 1))], vals[int(0.975 * (draws - 1))]]}


def binom_cdf(k, n, p):
    return sum(math.comb(n, i) * p ** i * (1 - p) ** (n - i) for i in range(0, k + 1))


def coverage_line(n, p=0.95, q=0.025):
    """the smallest k with P(X <= k) >= q for X ~ Binomial(n, p): E140-P3's line (21 of 25 at n = 25), E160's"""
    for k in range(0, n + 1):
        if binom_cdf(k, n, p) >= q:
            return k
    return n


_A2 = None


def m9a2(root=ROOT):
    """predict_m9_a2 (Q140(l)'s frozen predictor), imported from its committed directory after its sha256 and m9_a2.json's are checked"""
    global _A2
    if _A2 is None:
        for rel in (M9A2_REL, PM9A2_REL):
            got = sha256_file(os.path.join(root, rel))
            if got != FROZEN[rel]:
                raise SystemExit(f"refused: {rel}: sha256 {got}, frozen {FROZEN[rel]}")
        sys.path.insert(0, os.path.join(root, Q140L_REL))
        import predict_m9_a2 as A2  # noqa: E402
        if A2.M9_SHA256 != FROZEN[M9A2_REL]:
            raise SystemExit(f"refused: predict_m9_a2 loaded m9_a2.json {A2.M9_SHA256}")
        _A2 = A2
    return _A2


def primary(D, t, anchors, die_starts, D_band_hw):
    """THE PRIMARY (E165.md): M9's aifoundry2 part recomputed mechanically through the frozen burst(), the session's zeros-anchor reads and the
    tile's own bursts' die starts as its inputs; None for either input gives the frozen fallback (anchors) or T_ref (die starts)"""
    return m9a2().burst(D, t, anchors=anchors, die_starts=die_starts, D_band_hw=D_band_hw)


if __name__ == "__main__":
    bad = check_frozen()
    M = manifest()
    for t in M.values():
        why = check_tile(ROOT, t)
        if why:
            bad.append(why)
    print(f"{len(M)} tiles; frozen inputs, Q139(k)'s files and tiles: {'OK' if not bad else 'BAD'}")
    for b in bad:
        print("  ", b)
    print("coverage line at n = 25:", coverage_line(25), "(E140-P3: 21)")
    sys.exit(1 if bad else 0)
