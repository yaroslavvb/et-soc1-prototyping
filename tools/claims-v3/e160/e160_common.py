#!/usr/bin/env python3
"""E160 (Q139): what E160's predictions writer, protocol writer, runner, queue, reducer and self-test share. Standard library only (the runner
must work on aifoundry2's python without numpy). It is E143's e143_common.py with pool 6's names, plus the C check's pins.

  * the frozen inputs and their sha256: Q139(x)'s M8/M7/M6 predictions for aifoundry2, blind pool 6's manifest (blind6.json) and its MANIFEST, M8's
    freeze (m8.json), all committed in d98d2e34 / 122da8b6 before E160's registration;
  * Q139(k)'s C check as committed after its verification (4946a992): the runner wrapper sparsity_ccheck.sh, the host patch and its build script, and
    the C-logging host built from them on aifoundry2 at 06:18 PST on Tue 3 Nov 2026 (build/ccheck/b/host/sparsity_host, before this registration);
  * E80's kernel and sampler (E143's pins): the device code is byte-identical to E143's power passes;
  * the pool's tiles as run values (`file:` a tile of tools/claims-v3/kinds/blind6/tiles/<type>/) and their labels (`b6-<type>.<name>`);
  * the tile check against blind6.json (2,048 B; sha256 of the whole, of A = the first 1,024 B and of B = the last 1,024 B);
  * the scoring helpers the rules use: the seeded bootstrap of an rms drawn from reference errors, and the binomial coverage line (E143's, unchanged).

SPDX-License-Identifier: Apache-2.0
"""
import hashlib
import json
import math
import os
import random

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, "..", "..", ".."))
POOL_REL = "tools/claims-v3/kinds/blind6"
PRED_REL = f"{POOL_REL}/predictions-blind6-aifoundry2.json"
MAN_REL = f"{POOL_REL}/blind6.json"
MANIFEST_REL = f"{POOL_REL}/MANIFEST"
M8_REL = "docs/reports/data/2026-11-03-q139m-model/m8.json"
FROZEN = {  # Q139(x)'s commit d98d2e34 (README-predictions.md, Files); M8's 122da8b6
    PRED_REL: "6b9a5e6ee5f3c4761855d8cedc486c546fecc2d855d0e706919c2a21302e3125",
    MAN_REL: "4c4cee7b96cd128e525601793030ec386bc773dd88d9ef34b7a3fde9a2d4cb03",
    MANIFEST_REL: "a0e91556dee34d393a791e86fd25987b733500da49a1813ece91bdb838c7c5c0",
    M8_REL: "8c23aba2307fd18c15a3a8fc40c8d937ca0df0cf0373a7bc2e9e0c3847d46abd",
}
CCHECK_REL = "tools/claims-v3/ccheck"
CCHECK_FROZEN = {  # Q139(k) after its verification, 4946a992 (README "The exact use for E153, E157 and E160", step 6)
    f"{CCHECK_REL}/sparsity_ccheck.sh": "d00158d454596a8325ff3a7ffa3dff6e80a2e1798516b022009450f63443b9b7",
    f"{CCHECK_REL}/patch_host_ccheck.py": "05a8c867f9c408c59437c30333d02f9252ee54d3d5bd2743e49a5b99a358c3ee",
    f"{CCHECK_REL}/build_host_ccheck.sh": "35537915689bfa02c351b895db8ebd79d066e5a80bd432b38a273ac11d39502f",
}
WRAPPER_REL = f"{CCHECK_REL}/sparsity_ccheck.sh"
CC_HOST_REL = "build/ccheck/b/host/sparsity_host"
# the C-logging host, built by build_host_ccheck.sh on aifoundry2 at 06:18:30 PST, Tue 3 Nov 2026, from workloads/sparsity/host/main.cpp 0f53a7d5...
# patched to 5bd029ca... (tools/claims-v3/e160/logs/build-ccheck-aifoundry2.txt); it links /opt/et/lib/libetrt.so as E80's host does
CC_HOST_SHA256 = "eae32a152b8f0861bd2922c500eac217c931c9b464d3274a6bcf346cc986bfd2"
KERNEL_REL = "build/sparsity_t2/kernel/sparsity.elf"
ETTELEM_REL = "build/ettelem-hpl/ettelem"
E80_SHA256 = {  # E143's pins (run_e143.py E80_SHA256): the kernel and the sampler E143's power passes ran
    KERNEL_REL: "990807f483cd57aa413083c52e647079b86022768562d5810080852f7fd6ea24",
    ETTELEM_REL: "77a46171c915d3a92898af9ffe04d92b86b65f4d36bc29d58f5c086f8accfeb5",
}
GOVERNED_BELOW_MHZ = 795.0       # Q139(x) (README-predictions.md): governed = M8 predicts the burst below 795 MHz
LABEL_PREFIX = "b6-"
BOOT_DRAWS = 20000
BOOT_SEED = 160
MODELS = ("M8", "M7", "M6")


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


def boot_rms_range(errors, n, draws=BOOT_DRAWS, seed=BOOT_SEED):
    """(the 2.5% point, the 97.5% point) of the rms of n errors drawn with replacement from `errors` (E115's, E140's and E143's rule form), seeded."""
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


def binom_cdf(k, n, p):
    return sum(math.comb(n, i) * p ** i * (1 - p) ** (n - i) for i in range(0, k + 1))


def coverage_line(n, p=0.95, q=0.025):
    """the smallest k with P(X <= k) >= q for X ~ Binomial(n, p): E140-P3's line (21 of 25 at n = 25)"""
    for k in range(0, n + 1):
        if binom_cdf(k, n, p) >= q:
            return k
    return n


if __name__ == "__main__":
    import sys
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
