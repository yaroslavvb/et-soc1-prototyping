#!/usr/bin/env python3
"""E184's shared definitions: the design (shire order, minion order, operand images, quads), the readers and the statistics.

Every E184 script imports this file: the forecast and power script (power_e184.py), the image maker (make_images_e184.py), the runner,
the reducer and the scorer. It is part of the registration (tools/claims-v3/e184/E184.md) and is never edited after it; a change is a
dated amendment with a new file.

Pure Python 3.9+ (no numpy), deterministic: every sum is math.fsum, every random draw comes from random.Random with a seed written
here, so the outputs are the same under /usr/bin/python3 3.9 and python3 3.13 (kit v5's lesson: the readers' interpreter pinned, and
nothing depends on it).
SPDX-License-Identifier: Apache-2.0
"""
import math
import random
import struct

# ---------------------------------------------------------------------------------------------------------------------------------
# the design
# ---------------------------------------------------------------------------------------------------------------------------------
EC_MAX_HARTS = 2048            # workloads/enercat/enercat_args.h: 32 shires x 32 minions x 2 harts
IMAGE_BYTES = EC_MAX_HARTS * 256   # one 256 B operand block per hart (kernel/enercat.c: src = sources + hart * 256)
SEED_SLOTS = 18401             # the minion-slot permutation inside a shire
SEED_WORDS = 18402             # the random operand words, one stream per hart
SEED_BOOT = 18404              # the scorer's bootstrap
SEED_B = 18405                 # the card-1 arm's shuffles

# workloads/enercat/host/main.cpp's MESH (shire -> (x, y)), copied as data
MESH = {0: (0, 0), 24: (1, 0), 9: (2, 0), 25: (3, 0), 2: (4, 0), 11: (5, 0),
        8: (0, 1), 16: (1, 1), 1: (2, 1), 17: (3, 1), 10: (4, 1), 19: (5, 1),
        3: (0, 2), 4: (1, 2), 13: (2, 2), 14: (3, 2), 18: (4, 2), 27: (5, 2),
        12: (1, 3), 21: (2, 3), 22: (3, 3), 26: (4, 3),
        20: (1, 4), 29: (2, 4), 30: (3, 4), 15: (4, 4), 23: (5, 4),
        28: (1, 5), 5: (2, 5), 6: (3, 5), 7: (4, 5), 31: (5, 5)}


def shire_order():
    """The 32 compute shires in farthest-point order over the mesh (Manhattan distance), from shire 0: each next shire is the one
    farthest from those already chosen; ties go to the one with the fewest chosen shires within two hops, then to the lower id.
    A prefix of length M is the M-shire mask, so every mask spreads its shires over the die."""
    def dist(s, t):
        return abs(MESH[s][0] - MESH[t][0]) + abs(MESH[s][1] - MESH[t][1])
    order = [0]
    left = sorted(s for s in MESH if s != 0)
    while left:
        best = max(left, key=lambda s: (min(dist(s, t) for t in order), -sum(1 for t in order if dist(s, t) <= 2), -s))
        order.append(best)
        left.remove(best)
    return order


def mask_of(m):
    """The shire mask (an int) of the first m shires of shire_order()."""
    if not 1 <= m <= 32:
        raise ValueError("a mask has 1-32 shires")
    v = 0
    for s in shire_order()[:m]:
        v |= 1 << s
    return v


def slot_order():
    """The order in which a shire's 32 minions are switched (one fixed permutation for every shire)."""
    r = random.Random(SEED_SLOTS)
    return r.sample(range(32), 32)


def selected_minions(m, n):
    """The n minions switched to random operands on an m-shire mask: round robin over the mask's shires in shire_order(),
    and inside a shire in slot_order(). Nested: level n's minions are the first n of level n + 1's. Returns [(shire, minion)]."""
    if n > 32 * m:
        raise ValueError("more minions than the mask has")
    so, sl = shire_order()[:m], slot_order()
    return [(so[k % m], sl[k // m]) for k in range(n)]


def hart_words(h):
    """The 64 operand words of hart h when it is switched: floats uniform in [0.5, 2) (the catalogue's `random` range, host
    main.cpp sources()), one random.Random stream per hart, so a hart's words are the same at every level."""
    r = random.Random(SEED_WORDS * 4096 + h)
    out = []
    for _ in range(64):
        f = 0.5 + 1.5 * r.random()
        w = struct.unpack("<I", struct.pack("<f", f))[0]
        if w >= 0x40000000:          # float32 rounding reached 2.0: the largest float32 below 2.0 instead
            w = 0x3FFFFFFF
        out.append(w)
    return out


def image_bytes(m, n):
    """The 524,288 B operand image (EC_MAX_HARTS x 256 B, hart-major, little-endian words) of level n on the m-shire mask:
    both harts of each selected minion hold hart_words(h); every other word is zero."""
    words = [0] * (EC_MAX_HARTS * 64)
    for s, mi in selected_minions(m, n):
        for t in (0, 1):
            h = s * 64 + mi * 2 + t
            words[h * 64:(h + 1) * 64] = hart_words(h)
    return struct.pack("<%dI" % len(words), *words)


def image_name(m, n):
    return "m%02d_n%03d.bin" % (m, n)


# The quad: one host process, under timeout 10. S (the A image, 2 launches) settles the card after the process opens; then four
# blocks of 4 launches (1.6 s each at the 0.4 s window): A B B A or B A A B, alternating from quad to quad.
LAUNCH_S = 0.4
WINDOW_CYCLES = 240000000      # 0.4 s at 600 MHz, the catalogue's window
SETTLE_LAUNCHES = 2
BLOCK_LAUNCHES = 4
ORIENT = {"ABBA": ("A", "B", "B", "A"), "BAAB": ("B", "A", "A", "B")}
DISCARD_S = 0.35               # each block's first 0.35 s is not read (one SP pass of 155-166 ms, the sampler's 0.1 s, margin)
MIN_REFRESHES = 4              # a block with fewer kept refreshes sets its quad aside


def schedule_lines(orient, img_a, img_b):
    """The host's --schedule file for one quad: '<label> <launches> <image path>' per segment."""
    lines = ["S %d %s" % (SETTLE_LAUNCHES, img_a)]
    for role in ORIENT[orient]:
        lines.append("%s %d %s" % (role, BLOCK_LAUNCHES, img_a if role == "A" else img_b))
    return lines


# ---------------------------------------------------------------------------------------------------------------------------------
# the readers
# ---------------------------------------------------------------------------------------------------------------------------------
def fmean(xs):
    xs = list(xs)
    return math.fsum(xs) / len(xs) if xs else float("nan")


def fsd(xs):
    xs = list(xs)
    if len(xs) < 2:
        return float("nan")
    m = fmean(xs)
    return math.sqrt(math.fsum((x - m) ** 2 for x in xs) / (len(xs) - 1))


def refreshes(samples):
    """Distinct SP refreshes: drop a sample whose board reading and three rail averages equal the previous sample's (the sampler
    reads at 10 Hz, the SP refreshes every 155-166 ms on aifoundry3)."""
    out, prev = [], None
    for d in samples:
        try:
            key = (d["board_w"], d["sp"]["minion_w"][0], d["sp"]["sram_w"][0], d["sp"]["noc_w"][0])
        except (KeyError, IndexError, TypeError):
            continue
        if key != prev:
            out.append(d)
        prev = key
    return out


def dip_keep(xs):
    """E82 amendment A2's dip rule, as E178 and Q150 read it: refresh i is a launch-gap dip if x[i] < min(x[i-2], x[i+2]) - 4.0 W.
    Returns the kept indexes."""
    keep = []
    for i, x in enumerate(xs):
        if 2 <= i < len(xs) - 2 and x < min(xs[i - 2], xs[i + 2]) - 4.0:
            continue
        keep.append(i)
    return keep


def read_process(samples, launches, field="board"):
    """One quad's blocks from its launches (the host's ENERCAT lines: seg, label, t_start_ms, t_end_ms) and the process's telemetry.
    field 'board' reads board_w, 'rail' the minion rail's PMIC average (sp.minion_w[0]).
    Returns {'blocks': [(label, value, n_refreshes, t0_ms, t1_ms)], 'reason': None or why the quad is set aside}."""
    segs = {}
    for ln in launches:
        s = segs.setdefault(ln["seg"], {"label": ln["label"], "t0": ln["t_start_ms"], "t1": ln["t_end_ms"], "n": 0, "ok": True})
        s["t0"] = min(s["t0"], ln["t_start_ms"])
        s["t1"] = max(s["t1"], ln["t_end_ms"])
        s["n"] += 1
        s["ok"] = s["ok"] and bool(ln.get("ok", True))
    order = sorted(segs)
    if [segs[k]["label"] for k in order][:1] != ["S"] or len(order) != 5:
        return {"blocks": [], "reason": "segments %s, not S + four blocks" % [segs[k]["label"] for k in order]}
    if any(not segs[k]["ok"] for k in order):
        return {"blocks": [], "reason": "a launch did not end ok"}
    if any(segs[k]["n"] != (SETTLE_LAUNCHES if segs[k]["label"] == "S" else BLOCK_LAUNCHES) for k in order):
        return {"blocks": [], "reason": "a segment ran %s launches" % [segs[k]["n"] for k in order]}
    t_lo = segs[order[0]]["t0"] - 1000
    t_hi = segs[order[-1]]["t1"] + 1000
    ref = refreshes([d for d in samples if t_lo <= d.get("t_ms", -1) <= t_hi])
    xs = [d["board_w"] for d in ref]
    kept = set(dip_keep(xs))
    out = []
    for k in order[1:]:
        g = segs[k]
        lo, hi = g["t0"] + DISCARD_S * 1000.0, g["t1"]
        vals = []
        for i, d in enumerate(ref):
            if i in kept and lo <= d["t_ms"] <= hi:
                vals.append(d["board_w"] if field == "board" else d["sp"]["minion_w"][0])
        if len(vals) < MIN_REFRESHES:
            return {"blocks": [], "reason": "block %s has %d kept refreshes (< %d)" % (g["label"], len(vals), MIN_REFRESHES)}
        out.append((g["label"], fmean(vals), len(vals), g["t0"], g["t1"]))
    labels = tuple(b[0] for b in out)
    if labels not in ORIENT.values():
        return {"blocks": [], "reason": "block order %s" % (labels,)}
    return {"blocks": out, "reason": None}


def quad_contrast(blocks):
    """(B1 + B2 - A1 - A2) / 2 over a quad's four blocks, and the A blocks' mean (the base or reference level)."""
    a = [b[1] for b in blocks if b[0] == "A"]
    b = [b[1] for b in blocks if b[0] == "B"]
    if len(a) != 2 or len(b) != 2:
        raise ValueError("a quad has two A and two B blocks")
    return (math.fsum(b) - math.fsum(a)) / 2.0, math.fsum(a) / 2.0


# ---------------------------------------------------------------------------------------------------------------------------------
# the statistics (the ladder, the operating point, the scan)
# ---------------------------------------------------------------------------------------------------------------------------------
T975 = {1: 12.706, 2: 4.303, 3: 3.182, 4: 2.776, 5: 2.571, 6: 2.447, 7: 2.365, 8: 2.306, 9: 2.262, 10: 2.228, 11: 2.201, 12: 2.179,
        13: 2.160, 14: 2.145, 15: 2.131, 16: 2.120, 17: 2.110, 18: 2.101, 19: 2.093, 20: 2.086, 22: 2.074, 24: 2.064, 26: 2.056,
        28: 2.048, 30: 2.042, 35: 2.030, 40: 2.021, 50: 2.009, 60: 2.000, 80: 1.990, 100: 1.984, 120: 1.980}


def t975(df):
    """The two-sided 95% point of Student's t (table, the next lower tabulated df; 1.96 beyond 120)."""
    if df < 1:
        return float("nan")
    if df > 120:
        return 1.960
    k = max(d for d in T975 if d <= df)
    return T975[k]


def by_level(quads):
    """quads: [{'n': int, 'y': contrast}] -> {n: [y, ...]} in the quads' order."""
    out = {}
    for q in quads:
        out.setdefault(q["n"], []).append(q["y"])
    return out


def slope_through(levels, ns, c):
    """b = sum n (y - c) / sum n^2 over every quad at the levels ns (OLS through the null-corrected origin, quad weights)."""
    num = math.fsum(n * (y - c) for n in ns for y in levels.get(n, []))
    den = math.fsum(n * n for n in ns for _ in levels.get(n, []))
    return num / den if den > 0 else float("nan")


def ratio_reading(levels, small, large, null_n=0):
    """R = b(small) / b(large), each slope through the null level's mean (n = null_n). Returns (R, b_small, b_large, c)."""
    c = fmean(levels[null_n])
    bs, bl = slope_through(levels, small, c), slope_through(levels, large, c)
    return bs / bl, bs, bl, c


def bootstrap_ratio(levels, small, large, reps=2000, seed=SEED_BOOT, null_n=0):
    """The percentile bootstrap of R: quads resampled with replacement within each level (the null level included), 2,000 draws.
    Returns (lo, hi) of the 95% interval and the draws' sd."""
    r = random.Random(seed)
    keys = sorted(levels)
    draws = []
    for _ in range(reps):
        res = {}
        for k in keys:
            ys = levels[k]
            res[k] = [ys[r.randrange(len(ys))] for _ in ys]
        try:
            draws.append(ratio_reading(res, small, large, null_n)[0])
        except ZeroDivisionError:
            continue
    draws.sort()
    lo = draws[int(math.floor(0.025 * (len(draws) - 1)))]
    hi = draws[int(math.ceil(0.975 * (len(draws) - 1)))]
    return lo, hi, fsd(draws)


def three_way(lo, hi, delta, target=1.0):
    """LINEAR if [lo, hi] lies inside target +- delta; LOW if hi < target; HIGH if lo > target; else NOT RESOLVED."""
    if target - delta <= lo and hi <= target + delta:
        return "LINEAR"
    if hi < target:
        return "LOW"
    if lo > target:
        return "HIGH"
    return "NOT RESOLVED"


def mean_ci(ys):
    """Mean and its 95% t interval."""
    m, n = fmean(ys), len(ys)
    if n < 2:
        return m, float("nan"), float("nan")
    h = t975(n - 1) * fsd(ys) / math.sqrt(n)
    return m, m - h, m + h


def null_reading(ys, delta):
    """E184-N: NULL if the 95% interval lies inside +-delta; OFFSET if it excludes 0; else NOT RESOLVED."""
    m, lo, hi = mean_ci(ys)
    if -delta <= lo and hi <= delta:
        v = "NULL"
    elif lo > 0 or hi < 0:
        v = "OFFSET"
    else:
        v = "NOT RESOLVED"
    return v, m, lo, hi


def jump_reading(levels, z_crit):
    """E184-J: the full-ladder OLS y = c + b n over every quad; each level's mean residual over its se (the level's residual sd
    over k**0.5, k its quads). A JUMP is SEEN if any |r_n| / se_n exceeds z_crit (Bonferroni over the levels, two-sided 5%).
    Returns (verdict, rows)."""
    pts = [(n, y) for n in sorted(levels) for y in levels[n]]
    mn, my = fmean(p[0] for p in pts), fmean(p[1] for p in pts)
    sxx = math.fsum((p[0] - mn) ** 2 for p in pts)
    b = math.fsum((p[0] - mn) * (p[1] - my) for p in pts) / sxx
    c = my - b * mn
    rows, worst = [], 0.0
    for n in sorted(levels):
        rs = [y - c - b * n for y in levels[n]]
        se = fsd(rs) / math.sqrt(len(rs)) if len(rs) > 1 else float("nan")
        z = fmean(rs) / se if se and se == se else float("nan")
        rows.append({"n": n, "resid_w": fmean(rs), "se_w": se, "z": z})
        if z == z:
            worst = max(worst, abs(z))
    return ("SEEN" if worst > z_crit else "NONE SEEN"), {"b_w_per_minion": b, "c_w": c, "max_abs_z": worst, "levels": rows}


def scan_fit(quads, n_ref, breaks=None):
    """E184-C's step search. quads: [{'n': level, 'y': reading(level) - reading(n_ref)}]. For each candidate break k between two
    consecutive scan levels, OLS of y = b (n - n_ref) + d ([n > k] - [n_ref > k]) over every quad; T_k = d / se(d). Returns the
    table and max |T|."""
    ns = sorted(set(q["n"] for q in quads))
    if breaks is None:
        breaks = [(ns[i] + ns[i + 1]) / 2.0 for i in range(len(ns) - 1)]
    rows, best = [], None
    for k in breaks:
        x1 = [q["n"] - n_ref for q in quads]
        x2 = [(1.0 if q["n"] > k else 0.0) - (1.0 if n_ref > k else 0.0) for q in quads]
        y = [q["y"] for q in quads]
        s11, s22, s12 = math.fsum(a * a for a in x1), math.fsum(a * a for a in x2), math.fsum(a * c for a, c in zip(x1, x2))
        s1y, s2y = math.fsum(a * c for a, c in zip(x1, y)), math.fsum(a * c for a, c in zip(x2, y))
        det = s11 * s22 - s12 * s12
        if det <= 0:
            continue
        b = (s22 * s1y - s12 * s2y) / det
        d = (s11 * s2y - s12 * s1y) / det
        res = [yy - b * a - d * c for yy, a, c in zip(y, x1, x2)]
        s2 = math.fsum(r * r for r in res) / max(1, len(y) - 2)
        se_d = math.sqrt(s2 * s11 / det)
        t = d / se_d if se_d > 0 else float("nan")
        row = {"break_n": k, "b_w_per_minion": b, "d_w": d, "se_d_w": se_d, "t": t}
        rows.append(row)
        if t == t and (best is None or abs(t) > abs(best["t"])):
            best = row
    return {"rows": rows, "best": best, "max_abs_t": abs(best["t"]) if best else float("nan")}


# ---------------------------------------------------------------------------------------------------------------------------------
# card 1's SRAM arm: the reset windows (the version-3 TEL block's reader, Q150's form)
# ---------------------------------------------------------------------------------------------------------------------------------
def reset_window_ratios(samples, rail="sram_w", min_since_ms=700, board_step_w=0.5, min_avg_w=0.3):
    """Steady samples inside 1 s reset windows, each giving (min / average, max / average) of the rail's PMIC statistics
    [avg, min, max]: Q150's rule, line for line (docs/reports/data/2026-11-06-q150-meter-checks/reset_minmax_bylevel.py, 707cd2c5):
    since_reset_ms >= 700; the board within 0.5 W (strictly) of the PMIC's board average and of the previous sample's board reading
    (the previous sample is every parsed sample's, kept or not); the rail's average above 0.3 W and its maximum under 65 W.
    Returns a list of (min/avg, max/avg, avg, board_w)."""
    out, prev = [], None
    for d in samples:
        s = d.get("sp")
        sr = d.get("since_reset_ms", -1)
        b = d.get("board_w")
        ok = bool(s and sr is not None and sr >= min_since_ms and b is not None and prev is not None
                  and abs(b - s["board_avg_w"]) < board_step_w and abs(b - prev) < board_step_w)
        prev = b
        if not ok:
            continue
        a, mn, mx = s[rail]
        if a > min_avg_w and mx < 65:
            out.append((mn / a, mx / a, a, b))
    return out


def median(xs):
    xs = sorted(xs)
    n = len(xs)
    if not n:
        return float("nan")
    return xs[n // 2] if n % 2 else (xs[n // 2 - 1] + xs[n // 2]) / 2.0


def bootstrap_median(xs, reps=2000, seed=SEED_BOOT):
    r = random.Random(seed)
    xs = list(xs)
    draws = sorted(median([xs[r.randrange(len(xs))] for _ in xs]) for _ in range(reps))
    return draws[int(math.floor(0.025 * (reps - 1)))], draws[int(math.ceil(0.975 * (reps - 1)))]
