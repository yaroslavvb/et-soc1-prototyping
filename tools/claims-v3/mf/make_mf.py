#!/usr/bin/env python3
"""V3-MF (E75, the memory-path flip ladder): the operand images, the per-level commands, and the designed counts.

    python3 tools/claims-v3/mf/make_mf.py <out-dir>           # srcs/, manifest.json
    python3 tools/claims-v3/mf/make_mf.py <out-dir> --check    # re-derive every count from the bytes on disk

The question (Q128 section 5 item 5): there is **no flip ladder on a memory path**. A DRAM tensor load costs
94-134 pJ per byte against a multiply-add's 5.783 pJ, and the catalogue's only handle on the data is the
zeros-vs-random pair (4.1): L1 0.39 -> 0.54, own scratchpad 2.12 -> 4.43, DRAM 94.6 -> 132.6 pJ/B. That pair
moves TWO things at once — the number of ones carried and the number of bits that change between consecutive
transfers — and it gives one chord, not a slope. This builds the ladder, and splits the two.

## The construction

Every item is a 256 B image, repeated by the host to fill whatever the kernel reads, so the bytes on the wire are
exactly designed. Two element sizes, because two kernels read it two ways:

  * `ld_l1`   (EC_LD_L1, hand-written): eight `flw.ps` from src+0, +32, ... +224, i.e. the eight **32 B blocks**
    of the image in order, out of the L1. Element = 32 B = 256 bits, n = 8, consecutive pairs are (block i,
    block i+1).
  * `flw_pat` (EC_FLW_PAT): 32 B vector loads `--stride 64` apart over `--region` bytes of this hart's slice,
    which the host fills with the image repeated. A stride of 64 fetches **one 64 B line per load** and uses half
    of it, so the thing that travels is the line: element = 64 B = 512 bits, n = 4, consecutive pairs are (line
    i, line i+1). `--slice-bytes` sizes the working set, and so picks the level.

For n elements in a cycle (n even) with exactly k bits changing between neighbours and the same number of ones W
in every element, the image is built from two values alternating:

    T = a set of k bit positions ("the toggling group"), S = W - k/2 positions outside it ("the static ones")
    E_even = S + the first k/2 positions of T          E_odd = S + the last k/2 positions of T

so popcount(E_j ^ E_{j+1}) = k for every j (every bit of T differs), popcount(E_j) = W for both parities, and the
cycle closes because n is even. Two arms come out of the same construction, orthogonal by design:

    k-arm  (mf_<lvl>_k<k>):  k varies, W held at half the element
    w-arm  (mf_<lvl>_w<W>):  W varies, k held at half the element

The k-arm prices a **flipped bit** on that path; the w-arm prices a **carried one** (a DDR bus with data-bus
inversion, or any path with asymmetric drive, pays for ones, not for changes). The zeros-vs-random chord cannot
tell them apart; these two arms can. Anchors: `--operands zeros` and `--operands random` at every level, the
catalogue's own two points, so the ladder is read in the frame 4.1 already published.

Levels, `--harts 1` so 1,024 harts run, 32 per shire — the sizes are 4.2's own, which is what makes the result
comparable to the published per-byte figures:

| item | pattern | per hart | per shire / in all | 4.2's figure (random) |
|---|---|---|---|---|
| `mf_l1_*`   | `ld_l1`   | the 256 B image | — | 0.54 pJ/B |
| `mf_l2_*`   | `flw_pat` | 8 KB    | 256 KB per shire, half the L2 | 3.11 pJ/B |
| `mf_l3_*`   | `flw_pat` | 24 KB   | 768 KB per shire, 24 MB in all | 14.7 pJ/B |
| `mf_dram_*` | `flw_pat` | 128 KB  | 128 MB in all, 4x the 32 MB L3 | 114.6 pJ/B |

The scratchpad is **not** a rung: the host cannot seed a scratchpad (`--scp` makes the kernel read
`EC_SCP_ADDR(...)`, which no host fill reaches), so a scratchpad ladder needs a kernel mode that copies the
image in first. That is registered as out of scope here, with the reason, rather than run on uncontrolled bytes.
"""
import argparse
import json
import os

IMG = 256 * 8                 # bits in the 256 B image
LEVELS = {
    #  name     pattern    element bits  n   slice bytes   extra args
    "l1":   {"pattern": "ld_l1",   "elem": 256, "n": 8, "slice": None,      "unit": "L1 hit, flw.ps 32 B"},
    "l2":   {"pattern": "flw_pat", "elem": 512, "n": 4, "slice": 8192,     "unit": "L2, 256 KB per shire"},
    "l3":   {"pattern": "flw_pat", "elem": 512, "n": 4, "slice": 24576,    "unit": "L3, 24 MB in all"},
    "dram": {"pattern": "flw_pat", "elem": 512, "n": 4, "slice": 131072,   "unit": "DRAM, 128 MB in all"},
}
# The registered rungs. k is bits changing between consecutive elements; w is ones per element.
RUNGS = {
    "l1":   {"k": [0, 64, 128, 192, 256], "w": [64, 192]},
    "l2":   {"k": [0, 256, 512],          "w": []},
    "l3":   {"k": [0, 256, 512],          "w": []},
    "dram": {"k": [0, 128, 256, 384, 512], "w": [128, 384]},
}
WINDOW = 240000000            # the ec campaign's launch window: 0.4 s at 600 MHz


def two_values(elem, n, k, w):
    """(E_even, E_odd) as ints of `elem` bits: k bits change between neighbours, w ones in each."""
    if k % 2 or k > elem:
        raise ValueError(f"k={k} must be even and <= {elem}")
    s = w - k // 2
    if s < 0 or s > elem - k:
        raise ValueError(f"w={w} is not reachable at k={k} (static ones {s} outside [0, {elem - k}])")
    t_lo = sum(1 << i for i in range(0, k // 2))                 # first half of the toggling group
    t_hi = sum(1 << i for i in range(k // 2, k))                 # second half
    static = sum(1 << i for i in range(k, k + s))                # the static ones, outside T
    return static | t_lo, static | t_hi


def image(elem, n, a, b):
    """n elements of `elem` bits, alternating a, b, a, b, ... -> 256 bytes, little-endian."""
    out = bytearray()
    for j in range(n):
        v = a if j % 2 == 0 else b
        out += v.to_bytes(elem // 8, "little")
    if len(out) != 256:
        raise ValueError(f"{n} x {elem} bits is {len(out)} bytes, not 256")
    return bytes(out)


def elements(blob, elem, n):
    return [int.from_bytes(blob[j * elem // 8:(j + 1) * elem // 8], "little") for j in range(n)]


def measure(blob, elem, n):
    e = elements(blob, elem, n)
    k = [bin(e[j] ^ e[(j + 1) % n]).count("1") for j in range(n)]
    w = [bin(x).count("1") for x in e]
    return k, w


def args_for(lvl, name, item_s="%ITEM_S%"):
    L = LEVELS[lvl]
    a = ["--pattern", L["pattern"], "--harts", "1", "--seconds", item_s, "--window", str(WINDOW)]
    if name is None:
        a += ["--operands", "zeros"]
    elif name == "random":
        a += ["--operands", "random"]
    else:
        a += ["--operands", "file:%GEN%/srcs/" + name + ".bin"]
    if L["slice"] is None:
        a += ["--slice-bytes", "4096"]          # ld_l1 reads no slice; keep the allocation small
    else:
        a += ["--stride", "64", "--slice-bytes", str(L["slice"]), "--region", str(L["slice"])]
    return a


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("out")
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args()
    os.makedirs(f"{a.out}/srcs", exist_ok=True)
    items = [{"name": "anchor_pi", "kind": "fma", "family": "anchor", "values": "pi"}]
    for lvl, L in LEVELS.items():
        elem, n = L["elem"], L["n"]
        for k in RUNGS[lvl]["k"]:
            name = f"mf_{lvl}_k{k}"
            x, y = two_values(elem, n, k, elem // 2)
            open(f"{a.out}/srcs/{name}.bin", "wb").write(image(elem, n, x, y))
            items.append({"name": name, "kind": "cmd", "tool": "main", "family": f"mf_{lvl}_k", "level": lvl,
                          "src": "%GEN%/srcs/" + name + ".bin", "src_bytes": 256, "k": k, "w": elem // 2,
                          "elem_bits": elem, "n_elem": n, "unit": L["unit"], "tag": "ENERCAT {",
                          "args": args_for(lvl, name),
                          "designed": f"{k} bits change per {elem // 8} B transfer, {elem // 2} ones in each"})
        for w in RUNGS[lvl]["w"]:
            name = f"mf_{lvl}_w{w}"
            k = elem // 2
            x, y = two_values(elem, n, k, w)
            open(f"{a.out}/srcs/{name}.bin", "wb").write(image(elem, n, x, y))
            items.append({"name": name, "kind": "cmd", "tool": "main", "family": f"mf_{lvl}_w", "level": lvl,
                          "src": "%GEN%/srcs/" + name + ".bin", "src_bytes": 256, "k": k, "w": w,
                          "elem_bits": elem, "n_elem": n, "unit": L["unit"], "tag": "ENERCAT {",
                          "args": args_for(lvl, name),
                          "designed": f"{k} bits change per {elem // 8} B transfer, {w} ones in each"})
        for anch, nm in (("zeros", None), ("random", "random")):
            items.append({"name": f"mf_{lvl}_{anch}", "kind": "cmd", "tool": "main", "family": f"mf_{lvl}_anchor",
                          "level": lvl, "k": 0 if anch == "zeros" else 191, "w": 0 if anch == "zeros" else 145,
                          "elem_bits": elem, "n_elem": n, "unit": L["unit"], "tag": "ENERCAT {",
                          "args": args_for(lvl, nm),
                          "designed": "the catalogue's own anchor: " + anch
                                      + (" (zeros: no ones, no changes)" if anch == "zeros" else
                                         " (floats in [0.5,2): 11.944 changes and 18.167 ones per 32-bit word,"
                                         " so 191.1 changes and 290.7 ones per 512-bit line)")})
    json.dump({"exp": "E75", "levels": {k: {kk: vv for kk, vv in v.items()} for k, v in LEVELS.items()},
               "rungs": RUNGS, "window": WINDOW, "items": items},
              open(f"{a.out}/manifest.json", "w"), indent=1)
    print(f"{len(items)} items -> {a.out}")

    if a.check:
        bad = 0
        for it in json.load(open(f"{a.out}/manifest.json"))["items"]:
            if it["kind"] != "cmd" or not it.get("src"):
                continue
            blob = open(f"{a.out}/srcs/{it['name']}.bin", "rb").read()
            k, w = measure(blob, it["elem_bits"], it["n_elem"])
            ok = len(blob) == 256 and set(k) == {it["k"]} and set(w) == {it["w"]}
            print(f"{'ok ' if ok else 'BAD'} {it['name']:16s} {it['level']:4s} elem={it['elem_bits']:3d}b "
                  f"n={it['n_elem']} k={sorted(set(k))} w={sorted(set(w))}")
            bad += 0 if ok else 1
        print(f"check: {bad} bad")
        if bad:
            raise SystemExit(1)


if __name__ == "__main__":
    main()
