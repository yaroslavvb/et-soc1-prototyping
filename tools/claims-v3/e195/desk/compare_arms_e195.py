#!/usr/bin/env python3
"""E195's arm table, cell by cell (a desk check of code; no device, no simulator).

    python3 -I -B compare_arms_e195.py <request.md> <host --list --json> <gen dir> <reduce_x09.py> [<dumps dir>]

Sets request.md's section 2 table (31 arms: access, image, the designed counts per line and the control) beside:
  1. the built host's own arm table (`x09mem_host --list --json`: name, mode, image rule, period), in the same order;
  2. the designed counts the proposal's generator `make_x09.py --host --check` computed FROM THE HOST'S OWN BYTES
     (`<gen dir>/counts.json`), every numeric cell: w, hi, t_enc + tx_enc (and the raw toggles in parentheses), p64 + x64,
     half + x256, k_chan; a cell with a decimal point is read to its last digit (+-0.05), every other cell exactly;
  3. the manifest the generator wrote (`<gen dir>/manifest.json`): 32 items, `anchor_pi` first, every x9_ item's host
     arguments, its tag and its designed counts;
  4. the reducer's controls (`reduce_x09.py`'s CONTRASTS): every arm with a control has the contrast arm - control;
  5. with <dumps dir> (the host's `--dump-image` of every arm), the image column read literally as bytes: each line of the
     host's bytes against the bytes request.md's words name, written out here independently of the host and the generator;
  6. the registered price formulas of request.md sections 2 and 4 against the counts (224 pins, 320 ones, 512 toggles,
     Q's -192 / +256 toggle prices, K's -128 pins, the 0.125 / 1.0 ratio, the floor's terms, the paths' and the channel's
     terms) and section 2's rate arithmetic (0.600e9 lines a second either way at 600 MHz).
Prints every comparison that fails, a count per part, and "ARMS CHECK PASS" or "ARMS CHECK FAIL". Reads files only.
"""
import importlib.util
import json
import os
import re
import sys

req_path, list_path, gen_dir, red_path = sys.argv[1:5]
dumps = sys.argv[5] if len(sys.argv) > 5 else None
bad = []
tally = {}


def ok(part, cond, msg):
    tally.setdefault(part, [0, 0])
    tally[part][0 if cond else 1] += 1
    if not cond:
        bad.append(f"{part}: {msg}")


# ---- request.md section 2's table ----
txt = open(req_path, encoding="utf-8").read()
sec = txt[txt.index("## 2. Arms"):txt.index("## 3. ")]
rows = []
for line in sec.splitlines():
    if line.startswith("| `"):
        c = [x.strip() for x in line.strip().strip("|").split("|")]
        rows.append({"arm": c[0].strip("`"), "access": c[1], "image": c[2], "w": c[3], "hi": c[4], "t": c[5],
                     "p64": c[6], "half": c[7], "k": c[8], "control": c[9]})
host = json.load(open(list_path))
counts = json.load(open(os.path.join(gen_dir, "counts.json")))
man = json.load(open(os.path.join(gen_dir, "manifest.json")))
print(f"request.md rows: {len(rows)}; host arms: {len(host)}; counts: {len(counts)}; manifest items: {len(man['items'])}")

# The request's words, read as the host's terms (this lane's reading, written out; checked below against the host).
ACCESS = {"read, flat": ("rd", 0), "write, flat": ("wr", 0), "read, paced": ("rd", 1024), "write, paced": ("wr", 8192),
          "paced read loop, one L1 line": ("rdl1", 1024),
          "paced write loop into the own scratchpad": ("wrscp", 8192),
          "the paced write loop, its store replaced": ("wrnst", 8192)}
IMAGE = {"zeros": "z", "byte 0 = 0x01, the rest zeros": "first:01", "every byte 0x03": "b:03",
         "every byte 0x0F": "b:0f", "every byte 0x7F": "b:7f", "every byte 0xFF": "b:ff",
         "bytes 00 FF 00 FF ... (lanes constant)": "alt:00:ff:1", "beats 0x0F, 0xF0 (bytes 0F 0F F0 F0 ...)": "alt:0f:f0:2",
         "random, every line distinct": "rnd", "beats 0x0000, 0xFFFF (bytes 00 00 FF FF ...)": "alt:00:ff:2",
         "beats 0x0F, 0xF0": "alt:0f:f0:2", "8-byte pieces 0x0F, 0xF0": "alt:0f:f0:8", "halves 0x0F, 0xF0": "alt:0f:f0:32",
         "0x0F lines (even minions), 0xF0 lines (odd)": "par:0f:f0", "random, each minion its own 512 B": "rnd",
         "random": "rnd", "(no memory traffic)": "z", "(no DRAM traffic)": "z", "(nothing stored)": "z"}

# ---- part 1: names, order, access, image rule ----
ok("1 host table", len(rows) == 31 and len(host) == 31, f"{len(rows)} request rows, {len(host)} host arms (31 each)")
for i, r in enumerate(rows):
    h = host[i] if i < len(host) else {}
    ok("1 host table", h.get("name") == r["arm"], f"row {i + 1}: request {r['arm']}, host {h.get('name')}")
    acc = ACCESS.get(r["access"])
    ok("1 host table", acc is not None and (h.get("mode"), h.get("period")) == acc,
       f"{r['arm']}: access '{r['access']}' -> {acc}, host ({h.get('mode')}, {h.get('period')})")
    img = IMAGE.get(r["image"])
    ok("1 host table", img is not None and h.get("image") == img,
       f"{r['arm']}: image '{r['image']}' -> {img}, host {h.get('image')}")

# ---- part 2: the numeric cells against the counts from the host's bytes ----
NUM = re.compile(r"^([0-9.]+)(?:\s*\+\s*([0-9.]+))?\s*(?:\((.*)\))?$")


def parse(cell):
    if cell == "-":
        return None
    m = NUM.match(cell)
    if not m:
        raise SystemExit(f"cannot read cell '{cell}'")
    main = [m.group(1)] + ([m.group(2)] if m.group(2) else [])
    par = m.group(3)
    raw = None
    if par is not None:
        if par.strip() == "the same":
            raw = list(main)
        else:
            pm = re.match(r"^([0-9.]+)(?:\s*\+\s*([0-9.]+))?", par.strip())
            raw = [pm.group(1)] + ([pm.group(2)] if pm.group(2) else [])
    return main, raw


def near(want, got):
    """A cell is read to its last printed digit: +-0.05 with one decimal, +-0.5 for a whole number. A designed image's
    counts are whole numbers (checked in part 2b), so for them a whole-number cell must be equal; the random arms'
    whole-number cells (x64 '32') are means of drawn lines."""
    dec = len(want.split(".")[1]) if "." in want else 0
    return abs(float(want) - got) <= 0.5 * 10 ** (-dec) + 1e-9


def same(want, got):
    """want: the cell's numbers (one, or 'a + b'); got: the counts (one, or [inside, across])."""
    if len(want) == 1 and len(got) == 2:      # a single number in a pair column: the sum, and "0" means both parts 0
        return near(want[0], got[0] + got[1]) and (float(want[0]) != 0 or (got[0] == 0 and got[1] == 0))
    return len(want) == len(got) and all(near(a, b) for a, b in zip(want, got))


def cmp_cells(arm, col, cell, got_main, got_raw=None):
    p = parse(cell)
    if p is None:
        return
    main, raw = p
    ok("2 counts", same(main, got_main), f"{arm} {col}: request {cell}, host bytes {got_main}")
    if raw is not None:
        ok("2 counts", got_raw is not None and same(raw, got_raw), f"{arm} {col} (raw): request {cell}, host bytes {got_raw}")


for r in rows:
    c = counts.get(r["arm"], {}).get("counts", {})
    if r["w"] == "-":
        z = all(v == 0 for k, v in c.items() if k not in ("no_dram", "sha256_bytes"))
        ok("2 counts", z and c.get("no_dram") == 1, f"{r['arm']}: '-' row, counts {c}")
        continue
    cmp_cells(r["arm"], "w", r["w"], [c["w"]])
    cmp_cells(r["arm"], "hi", r["hi"], [c["hi"]], [c["w"]])     # raw hi (inversion off) = the ones
    cmp_cells(r["arm"], "t_enc + tx_enc", r["t"], [c["t_enc"], c["tx_enc"]], [c["t_raw"], c["tx_raw"]])
    cmp_cells(r["arm"], "p64 + x64", r["p64"], [c["p64"], c["x64"]])
    cmp_cells(r["arm"], "half + x256", r["half"], [c["half"], c["x256"]])
    cmp_cells(r["arm"], "k_chan", r["k"], [c["k_chan"]])
    if not r["image"].startswith("random"):    # part 2b: a designed image's counts are whole numbers
        keys = ("w", "hi", "dmi", "t_enc", "t_raw", "tx_enc", "tx_raw", "p64", "x64", "half", "x256", "k_chan")
        ok("2b whole counts", all(float(c[k]).is_integer() for k in keys),
           f"{r['arm']}: a designed count is not whole: {[(k, c[k]) for k in keys if not float(c[k]).is_integer()]}")

# ---- part 3: the manifest ----
items = man["items"]
ok("3 manifest", len(items) == 32 and items[0]["name"] == "anchor_pi" and items[0]["kind"] == "fma",
   f"{len(items)} items, first {items[0].get('name')}")
for r, it in zip(rows, items[1:]):
    want = "x9_" + r["arm"].replace(".", "_")
    ok("3 manifest", it["name"] == want, f"item {it['name']} for {r['arm']}")
    ok("3 manifest", it["args"] == ["--item", r["arm"], "--seconds", "%ITEM_S%", "--stop-file", "build/x09-STOP"],
       f"{it['name']} args {it['args']}")
    ok("3 manifest", it.get("tag") == "X09MEM {" and it.get("tool") == "main" and it.get("kind") == "cmd",
       f"{it['name']} tag/tool/kind {it.get('tag')}/{it.get('tool')}/{it.get('kind')}")
    cc = {k: v for k, v in counts[r["arm"]]["counts"].items() if k != "sha256_bytes"}
    ok("3 manifest", it.get("designed") == cc, f"{it['name']} designed counts differ from counts.json")
ok("3 manifest", man.get("ms") is True and man.get("seed") == 1, f"manifest ms {man.get('ms')} seed {man.get('seed')}")

# ---- part 4: the controls against the reducer's contrasts ----
spec = importlib.util.spec_from_file_location("reduce_x09", red_path)
red = importlib.util.module_from_spec(spec)
spec.loader.exec_module(red)
pairs = {tuple(sorted(v[0].items())) for v in red.CONTRASTS.values()}
for r in rows:
    if r["control"] == "-":
        continue
    for ctl in re.findall(r"`([^`]+)`", r["control"]):
        a, b = "x9_" + r["arm"].replace(".", "_"), "x9_" + ctl.replace(".", "_")
        ok("4 controls", tuple(sorted({a: 1, b: -1}.items())) in pairs, f"{r['arm']} - {ctl}: no such contrast")

# ---- part 5: the image column as bytes (the host's dumps) ----
if dumps:
    def lines_of(arm):
        b = open(os.path.join(dumps, arm + ".bin"), "rb").read()
        return [b[i:i + 64] for i in range(0, len(b), 64)]

    def rep(pat):
        return (bytes(pat) * (64 // len(pat) + 1))[:64]

    WORDS = {"zeros": rep([0]), "byte 0 = 0x01, the rest zeros": bytes([1]) + bytes(63),
             "every byte 0x03": rep([3]), "every byte 0x0F": rep([0x0F]), "every byte 0x7F": rep([0x7F]),
             "every byte 0xFF": rep([0xFF]), "bytes 00 FF 00 FF ... (lanes constant)": rep([0, 0xFF]),
             "beats 0x0F, 0xF0 (bytes 0F 0F F0 F0 ...)": rep([0x0F, 0x0F, 0xF0, 0xF0]),
             "beats 0x0F, 0xF0": rep([0x0F, 0x0F, 0xF0, 0xF0]),
             "beats 0x0000, 0xFFFF (bytes 00 00 FF FF ...)": rep([0, 0, 0xFF, 0xFF]),
             "8-byte pieces 0x0F, 0xF0": rep([0x0F] * 8 + [0xF0] * 8), "halves 0x0F, 0xF0": rep([0x0F] * 32 + [0xF0] * 32),
             "(no memory traffic)": rep([0]), "(no DRAM traffic)": rep([0]), "(nothing stored)": rep([0])}
    for r in rows:
        L = lines_of(r["arm"])
        writes = r["access"].startswith("write") or "write loop" in r["access"]
        n_expect = 1024 * 8 if writes else 3 * 2048
        ok("5 bytes", len(L) == n_expect, f"{r['arm']}: {len(L)} lines in the dump, {n_expect} expected")
        w = r["image"]
        if w in WORDS:
            ok("5 bytes", all(x == WORDS[w] for x in L), f"{r['arm']}: a line differs from '{w}'")
        elif w == "0x0F lines (even minions), 0xF0 lines (odd)":
            good = all(L[m * 8 + j] == rep([0xF0 if m % 2 else 0x0F]) for m in range(1024) for j in range(8))
            ok("5 bytes", good, f"{r['arm']}: minion parity rule broken")
        elif w.startswith("random"):
            ok("5 bytes", len(set(L)) == len(L), f"{r['arm']}: {len(L) - len(set(L))} repeated lines")
            if writes:
                imgs = [b"".join(L[m * 8:(m + 1) * 8]) for m in range(1024)]
                ok("5 bytes", len(set(imgs)) == 1024, f"{r['arm']}: minions' 512 B images not all distinct")
        else:
            ok("5 bytes", False, f"{r['arm']}: no byte reading for '{w}'")
    # paced arms move the flat arms' bytes
    for a, b in (("rdh.z", "rd.z"), ("rdh.u4", "rd.u4"), ("rdh.rnd", "rd.rnd"), ("wrh.z", "wr.z"), ("wrh.u4", "wr.u4"),
                 ("wrh.rnd", "wr.rnd")):
        ok("5 bytes", lines_of(a) == lines_of(b), f"{a} and {b} move different bytes")

# ---- part 6: the registered formulas against the counts; the rate arithmetic ----
C = {a: counts[a]["counts"] for a in counts}
for d in ("rd", "wr"):
    g = lambda s, k: C[f"{d}.{s}"][k]
    T = lambda s: g(s, "t_enc") + g(s, "tx_enc")
    ok("6 formulas", g("u4", "w") == g("l08", "w") and g("u4", "hi") - g("l08", "hi") == 224 and T("u4") == T("l08") == 0,
       f"{d}: u4 - l08 is not 224 high pins at equal ones with no toggle")
    ok("6 formulas", g("u7", "hi") == g("u2", "hi") and g("u7", "w") - g("u2", "w") == 320, f"{d}: u7 - u2 is not 320 ones")
    ok("6 formulas", T("a44") - T("u4") == 512 and g("a44", "t_enc") - g("u4", "t_enc") == 496 and
       g("a44", "w") == g("u4", "w") and g("a44", "hi") == g("u4", "hi"), f"{d}: a44 - u4 is not 512 toggles (496 inside)")
    Kh = (g("u8", "hi") - g("u7", "hi")) - (g("u4", "hi") - g("u2", "hi")) / 2
    Kw = (g("u8", "w") - g("u7", "w")) - (g("u4", "w") - g("u2", "w")) / 2   # = K's pins if inversion is off (hi = w)
    ok("6 formulas", Kh == -128 and Kw == 0, f"{d}: K is {Kh} pins at {Kw} ones (want -128 pins at 0 ones; 0 if off)")
    ok("6 formulas", (g("w1", "w"), g("w1", "hi"), T("w1")) == (1, 1, 2), f"{d}: w1 is not one one, one pin, two toggles")
Q = lambda k1, k2: (C["wr.a08"][k1] + C["wr.a08"][k2] - C["wr.l08"][k1] - C["wr.l08"][k2]) - \
    (C["wr.a44"][k1] + C["wr.a44"][k2] - C["wr.u4"][k1] - C["wr.u4"][k2]) / 2
ok("6 formulas", Q("t_enc", "tx_enc") == -192 and Q("t_raw", "tx_raw") == 256, "Q is not -192 (live) / +256 (off) toggles")
ok("6 formulas", C["wr.l08"]["w"] == C["wr.a08"]["w"] and C["wr.l08"]["hi"] == C["wr.a08"]["hi"],
   "l08 and a08 differ in ones or high pins")
tog = lambda a, kind: C[a]["t_" + kind] + C[a]["tx_" + kind]
r_live = (tog("wr.a08", "enc") - tog("wr.l08", "enc")) / (tog("wr.a44", "enc") - tog("wr.u4", "enc"))
r_off = (tog("wr.a08", "raw") - tog("wr.l08", "raw")) / (tog("wr.a44", "raw") - tog("wr.u4", "raw"))
ok("6 formulas", r_live == 0.125 and r_off == 1.0, f"(a08 - l08)/(a44 - u4) {r_live} live, {r_off} off")
p, h, c, u = C["wr.p64"], C["wr.h256"], C["wr.c44"], C["wr.u4"]
ok("6 formulas", p["t_enc"] + p["tx_enc"] == 128 and p["p64"] == 448 and p["w"] == u["w"] and p["hi"] == u["hi"],
   "p64 - u4 is not 448 path bits and 128 toggles at equal ones and pins")
ok("6 formulas", h["t_enc"] + h["tx_enc"] == 32 and h["p64"] == 64 and h["half"] == 256 and h["w"] == u["w"] and
   h["hi"] == u["hi"], "h256 - u4 is not 256 half bits, 64 path bits and 32 toggles")
ok("6 formulas", c["t_enc"] + c["tx_enc"] == 8 and c["k_chan"] == 256 and c["p64"] == 0 and c["half"] == 0,
   "c44 - u4 is not 256 channel bits and 8 toggles with no in-line path bits")
lines_rd = 1024 * 600e6 / 1024
lines_wr = 1024 * 8 * 600e6 / 8192
ok("6 formulas", lines_rd == 600e6 and lines_wr == 600e6, f"paced line rates {lines_rd:.4g}, {lines_wr:.4g}")
ok("6 formulas", 1024 * 128 * 1024 == 128 * 2 ** 20 and 1024 * 256 * 1024 == 256 * 2 ** 20, "slice totals")

for k in sorted(tally):
    print(f"part {k}: {tally[k][0]} hold, {tally[k][1]} fail")
for b in bad:
    print("  FAIL " + b)
print("ARMS CHECK " + ("PASS" if not bad else "FAIL"))
sys.exit(1 if bad else 0)
