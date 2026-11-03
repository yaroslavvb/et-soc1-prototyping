#!/usr/bin/env python3
"""E143 (Q138): what E143's predictions writer, protocol writer, runner, reducer and self-test share. Standard library only (the runner
must work on aifoundry2's python without numpy).

  * the frozen inputs and their sha256 (Q138(x)'s predictions for aifoundry2, blind pool 5's manifest, M7's freeze);
  * the pool's 36 tiles as run values (`file:` a tile of tools/claims-v3/kinds/blind5/tiles/<type>/) and their labels (`b5-<type>.<name>`);
  * the tile check against blind5.json (2,048 B; sha256 of the whole, of A = the first 1,024 B and of B = the last 1,024 B);
  * the scoring helpers the rules use: the seeded bootstrap of an rms drawn from reference errors, and the binomial coverage line.

SPDX-License-Identifier: Apache-2.0
"""
import hashlib
import json
import math
import os
import random

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, "..", "..", ".."))
POOL_REL = "tools/claims-v3/kinds/blind5"
PRED_REL = f"{POOL_REL}/predictions-blind5-aifoundry2.json"
MAN_REL = f"{POOL_REL}/blind5.json"
M7_REL = "docs/reports/data/2026-11-02-q138m-model/m7.json"
FROZEN = {  # Q138(x)'s commit dac39d97 (README-predictions.md, Files); M7's 3a210f2b
    PRED_REL: "596ec0754fb2abd95ac85604b497338fd3a7c8759078470a023a1b0c0726632b",
    MAN_REL: "946f8493f158ae293fa6b4b81b122130bf740c8eb8d8c7777c8fd2248f88f13d",
    M7_REL: "bfeea822b87e0a1f8c315809192faf0a437b72bcadd1459c027cd857c8b3d8b2",
}
GOVERNED_BELOW_MHZ = 795.0       # Q138(x) and M7's verifier: governed = M7 predicts the burst below 795 MHz
LABEL_PREFIX = "b5-"
BOOT_DRAWS = 20000
BOOT_SEED = 143


def sha256_file(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def sha256_bytes(b):
    return hashlib.sha256(b).hexdigest()


def check_frozen(root=ROOT):
    """[] if the three frozen inputs are byte-identical to Q138(x)'s and M7's commits, else what differs."""
    bad = []
    for rel, want in FROZEN.items():
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
    """(the 2.5% point, the 97.5% point) of the rms of n errors drawn with replacement from `errors` (E115's and E140's rule form), seeded."""
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
    print(f"{len(M)} tiles; frozen inputs and tiles: {'OK' if not bad else 'BAD'}")
    for b in bad:
        print("  ", b)
    print("coverage line at n = 25:", coverage_line(25), "(E140-P3: 21)")
    sys.exit(1 if bad else 0)
