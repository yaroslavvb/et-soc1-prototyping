#!/usr/bin/env python3
"""E184's dated amendment A2 (E184.md.dated-note-A2.md): the amended statistics and their power, and the registered ones on the cases
E184's verifier raised (desk only; before any E184 datum).

    /usr/bin/python3 -B tools/claims-v3/e184/power_e184_a2.py > tools/claims-v3/e184/power-e184-a2.json
    /usr/bin/python3 -B tools/claims-v3/e184/power_e184_a2.py --text > tools/claims-v3/e184/power-e184-a2.txt

It reads, beside it: inputs-e184.json, plan-e184.json and forecast-e184.json (the registration's, unchanged: the step per minion, the
meter's code, the carry positions, the two noise models' quad sd), power_e184.py's delta_ratio (its source text, run alone, as
score_e184.py runs it) and a2-check-e184.json (the contamination model of A2-5, read from E180's committed bursts). Pure Python, seeded,
the same bytes under /usr/bin/python3 3.9 and python3 3.13.

  C   A2-1: scan_fit_a2 (the scorer's statistic, from quads) and its fast twin from level sums (checked equal on 25 draws); the critical
      value t*_A2 (95th percentile of T with no step, 4,000 draws); the power for a one-code and a half-code step at the three carry
      positions; the false alarm under the registration's own dither model (one code's transition displaced by a code, dithered by the
      board's 2.12-code spread: the mean reading moves by at most 0.187 code around the carry), both signs, at the three positions; and a
      uniform offset at every level but the reference. The registered statistic (e184_common.scan_fit, through its fast twin) on the same
      cases, beside it.
  R   A2-2: the registered R (through the origin, delta method) and the null-corrected R (each slope through the null level's mean, delta
      method with the null mean's variance in both slopes and their covariance: delta_ratio_nc), for E184-L and E184-P, under a protocol
      offset at every level (the null's too), an offset at the switched levels only, and small steps read at 0.8 and 0.9; the part's own
      null level read by E184-N's rule in the same draws; A2-2's governing verdict (the registered R, or the null-corrected R when that
      null reads OFFSET) and its disagreement count; and dR/do, how far a protocol offset moves the registered R.
  O   A2-5: the registered rules' power when 0.19% of block refreshes are uncaught partial dips (a2-check-e184.json), without A2-5's rule;
      with it the dips are set aside and the base model's powers stand.
  K   kit note 1 section 1: the smoke gate's chance of a NO-GO on the 16-shire n = 19 quad, the registered band against kit note 1's.
SPDX-License-Identifier: Apache-2.0
"""
import ast
import json
import math
import os
import random
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import e184_common as c  # noqa: E402

TEXT = "--text" in sys.argv
INP = json.load(open(os.path.join(HERE, "inputs-e184.json")))
PLAN = json.load(open(os.path.join(HERE, "plan-e184.json")))
FC = json.load(open(os.path.join(HERE, "forecast-e184.json")))
CHK = json.load(open(os.path.join(HERE, "a2-check-e184.json")))
DS = PLAN["design"]
S_W = INP["e180_anchor"]["board_mw_per_minion"] / 1000.0
LSB = INP["pmic_meter"]["mw_per_code_at_12v"] / 1000.0
CARRY = INP["pmic_meter"]["carry_1024_board_w_at_11p7_12p0_12p3_v"]
SIG_LSB = INP["e180_noise"]["refresh_sd_w_median"]["zeros"] / LSB
QSD = {m: FC["models"][m]["quad_sd_w"] for m in ("base", "pess")}
TH = FC["thresholds"]
REG_T = FC["power"]["C"]["base"]["t_crit_family_5pct"]


def r6(x):
    return None if x is None or x != x else float("%.6g" % x)


def registered(name):
    src = open(os.path.join(HERE, "power_e184.py")).read()
    fn = [n for n in ast.parse(src).body if isinstance(n, ast.FunctionDef) and n.name == name][0]
    ns = {"math": math, "c": c}
    exec(compile(ast.Module(body=[fn], type_ignores=[]), "power_e184.py:" + name, "exec"), ns)
    return ns[name]


delta_ratio = registered("delta_ratio")


# ---- A2-1: E184-C with an intercept, the reference level set aside ---------------------------------------------------------------------------
def solve3(a, y):
    """a 3x3 symmetric system by Gauss-Jordan; returns (x, inverse) or (None, None) if singular."""
    m = [list(a[i]) + [1.0 if i == j else 0.0 for j in range(3)] for i in range(3)]
    for i in range(3):
        p = max(range(i, 3), key=lambda r: abs(m[r][i]))
        if abs(m[p][i]) < 1e-12:
            return None, None
        m[i], m[p] = m[p], m[i]
        piv = m[i][i]
        m[i] = [v / piv for v in m[i]]
        for r in range(3):
            if r != i:
                f = m[r][i]
                m[r] = [v - f * w for v, w in zip(m[r], m[i])]
    inv = [row[3:] for row in m]
    x = [math.fsum(inv[i][j] * y[j] for j in range(3)) for i in range(3)]
    return x, inv


def scan_fit_a2(quads, n_ref):
    """A2-1's step search (the scorer's statistic). quads: [{'n': level, 'y': reading(level) - reading(n_ref)}]. The reference level's
    quads (A and B the same image) are set aside: they carry no step, and a reference reading's own error is the same in every other
    quad's contrast, which the intercept takes. For each break k between two consecutive remaining levels, OLS of
    y = c + b (n - n_ref) + d [n > k]; T_k = d / se(d), the residual variance on N - 3 degrees of freedom. Returns the table, the best
    break, max |T| and the reference level's quads as a null reading (their mean and 95% t interval)."""
    ref_q = [q["y"] for q in quads if q["n"] == n_ref]
    qs = [q for q in quads if q["n"] != n_ref]
    ns = sorted(set(q["n"] for q in qs))
    breaks = [(ns[i] + ns[i + 1]) / 2.0 for i in range(len(ns) - 1)]
    y = [q["y"] for q in qs]
    x1 = [q["n"] - n_ref for q in qs]
    N = len(y)
    syy = math.fsum(v * v for v in y)
    rows, best = [], None
    for k in breaks:
        x3 = [1.0 if q["n"] > k else 0.0 for q in qs]
        a = [[float(N), math.fsum(x1), math.fsum(x3)],
             [math.fsum(x1), math.fsum(v * v for v in x1), math.fsum(u * v for u, v in zip(x1, x3))],
             [math.fsum(x3), math.fsum(u * v for u, v in zip(x1, x3)), math.fsum(x3)]]
        xy = [math.fsum(y), math.fsum(u * v for u, v in zip(x1, y)), math.fsum(u * v for u, v in zip(x3, y))]
        beta, inv = solve3(a, xy)
        if beta is None:
            continue
        rss = max(0.0, syy - math.fsum(bb * v for bb, v in zip(beta, xy)))
        s2 = rss / max(1, N - 3)
        se_d = math.sqrt(s2 * inv[2][2]) if s2 * inv[2][2] > 0 else float("nan")
        t = beta[2] / se_d if se_d == se_d and se_d > 0 else float("nan")
        row = {"break_n": k, "c_w": beta[0], "b_w_per_minion": beta[1], "d_w": beta[2], "se_d_w": se_d, "t": t}
        rows.append(row)
        if t == t and (best is None or abs(t) > abs(best["t"])):
            best = row
    nul = None
    if len(ref_q) >= 2:
        m, lo, hi = c.mean_ci(ref_q)
        nul = {"quads": len(ref_q), "mean_w": m, "ci95": [lo, hi]}
    return {"rows": rows, "best": best, "max_abs_t": abs(best["t"]) if best else float("nan"), "reference_null": nul}


class FastScan:
    """scan_fit_a2 (a2=True) and e184_common.scan_fit (a2=False) from level sums: the same OLS, written for the simulation only."""

    def __init__(self, levels, counts, n_ref, a2):
        self.a2, self.ref = a2, n_ref
        self.lv = [n for n in levels if not (a2 and n == n_ref)]
        self.m = {n: counts[n] for n in self.lv}
        ns = self.lv
        self.breaks = [(ns[i] + ns[i + 1]) / 2.0 for i in range(len(ns) - 1)]
        self.N = sum(self.m.values())
        self.pre = []
        for k in self.breaks:
            if a2:
                s0 = float(self.N)
                s1 = math.fsum(self.m[n] * (n - n_ref) for n in ns)
                s3 = math.fsum(self.m[n] for n in ns if n > k)
                s11 = math.fsum(self.m[n] * (n - n_ref) ** 2 for n in ns)
                s13 = math.fsum(self.m[n] * (n - n_ref) for n in ns if n > k)
                a = [[s0, s1, s3], [s1, s11, s13], [s3, s13, s3]]
                _, inv = solve3(a, [0.0, 0.0, 0.0])
                self.pre.append((k, inv))
            else:
                x2 = {n: (1.0 if n > k else 0.0) - (1.0 if n_ref > k else 0.0) for n in ns}
                s11 = math.fsum(self.m[n] * (n - n_ref) ** 2 for n in ns)
                s22 = math.fsum(self.m[n] * x2[n] ** 2 for n in ns)
                s12 = math.fsum(self.m[n] * (n - n_ref) * x2[n] for n in ns)
                self.pre.append((k, (s11, s22, s12, x2)))

    def max_t(self, ys):
        """ys: {level: [quad contrasts]} -> (max |T|, its break, its d)"""
        Y = {n: math.fsum(ys[n]) for n in self.lv}
        syy = math.fsum(v * v for n in self.lv for v in ys[n])
        ty = math.fsum(Y.values())
        t1y = math.fsum((n - self.ref) * Y[n] for n in self.lv)
        best = (0.0, None, None)
        for k, pre in self.pre:
            if self.a2:
                inv = pre
                t3y = math.fsum(Y[n] for n in self.lv if n > k)
                xy = [ty, t1y, t3y]
                beta = [math.fsum(inv[i][j] * xy[j] for j in range(3)) for i in range(3)]
                rss = max(0.0, syy - math.fsum(bb * v for bb, v in zip(beta, xy)))
                se = math.sqrt(rss / (self.N - 3) * inv[2][2])
                d = beta[2]
            else:
                s11, s22, s12, x2 = pre
                s2y = math.fsum(x2[n] * Y[n] for n in self.lv)
                det = s11 * s22 - s12 * s12
                b = (s22 * t1y - s12 * s2y) / det
                d = (s11 * s2y - s12 * t1y) / det
                rss = max(0.0, syy - b * t1y - d * s2y)
                se = math.sqrt(rss / (self.N - 2) * s11 / det)
            t = abs(d / se) if se > 0 else 0.0
            if t > best[0]:
                best = (t, k, d)
        return best


CQ = DS["C"]
C_LEVELS, C_REF = CQ["levels"], CQ["ref"]
C_PER = CQ["quads_per_level_per_sweep"] * len(CQ["sweeps"])
C_BASE = CQ["scan_start_w"]
C_COUNTS = {n: C_PER for n in C_LEVELS}
FAST_A2 = FastScan(C_LEVELS, C_COUNTS, C_REF, True)
FAST_REG = FastScan(C_LEVELS, C_COUNTS, C_REF, False)


def phi(x):
    return 0.5 * (1.0 + math.erf(x / math.sqrt(2.0)))


def bump(p_w, pc_w, sign):
    """the registration's dither model: one transition at the carry displaced by one code, dithered by SIG_LSB codes (sd): the mean
    reading at true level p_w moves by -sign * LSB * P(the dithered value falls in the displaced code)."""
    s = SIG_LSB * LSB
    return -sign * LSB * (phi((pc_w + LSB - p_w) / s) - phi((pc_w - p_w) / s))


def scan_draw(r, model, mu_fn, contam=None):
    sq = QSD[model]
    ys = {}
    for n in C_LEVELS:
        mu = mu_fn(n)
        ys[n] = [mu + r.gauss(0.0, sq) + (contam(r) if contam else 0.0) for _ in range(C_PER)]
    return ys


def mu_step(n_at, d):
    return lambda n: S_W * (n - C_REF) + d * ((1.0 if n > n_at else 0.0) - (1.0 if C_REF > n_at else 0.0))


def mu_bump(pc_w, sign):
    pa = C_BASE + S_W * C_REF
    return lambda n: S_W * (n - C_REF) + bump(C_BASE + S_W * n, pc_w, sign) - bump(pa, pc_w, sign)


def mu_offset(o):
    return lambda n: S_W * (n - C_REF) + (o if n != C_REF else 0.0)


def band_n():
    lo_w, hi_w = CARRY[0] - S_W * 12, CARRY[2] + S_W * 12        # the band widened by one scan level
    return (lo_w - C_BASE) / S_W, (hi_w - C_BASE) / S_W


def c_section():
    out = {"t_crit_registered": REG_T}
    # the fast twins equal the scorer's functions
    r = random.Random(18421)
    worst = 0.0
    for _ in range(25):
        ys = scan_draw(r, "base", mu_step(148.0, LSB * r.random()))
        qs = [{"n": n, "y": y} for n in C_LEVELS for y in ys[n]]
        worst = max(worst, abs(scan_fit_a2(qs, C_REF)["max_abs_t"] - FAST_A2.max_t(ys)[0]),
                    abs(c.scan_fit(qs, C_REF)["max_abs_t"] - FAST_REG.max_t(ys)[0]))
    out["fast_twins_max_abs_diff_t"] = worst
    r = random.Random(18422)
    null_t = sorted(FAST_A2.max_t(scan_draw(r, "base", mu_offset(0.0)))[0] for _ in range(4000))
    tcrit = null_t[int(math.ceil(0.95 * (len(null_t) - 1)))]
    out["t_crit_a2"] = r6(tcrit)
    out["t_crit_a2_draws"] = 4000
    r = random.Random(18423)
    null_reg = sorted(FAST_REG.max_t(scan_draw(r, "base", mu_offset(0.0)))[0] for _ in range(4000))
    out["t_crit_registered_recomputed_4000"] = r6(null_reg[int(math.ceil(0.95 * (len(null_reg) - 1)))])
    lo_n, hi_n = band_n()
    reps = 1000
    for model in ("base", "pess"):
        pw = {}
        for lbl, pc in (("carry at 11.7 V", CARRY[0]), ("carry at 12.0 V", CARRY[1]), ("carry at 12.3 V", CARRY[2])):
            n_at = (pc - C_BASE) / S_W
            for dname, dd in (("1 LSB", LSB), ("half an LSB", LSB / 2)):
                r = random.Random(18424 + int(n_at) + (0 if dd == LSB else 1))
                hit = near = inband = 0
                for _ in range(reps):
                    t, k, _d = FAST_A2.max_t(scan_draw(r, model, mu_step(n_at, dd)))
                    if t > tcrit:
                        hit += 1
                        near += 1 if abs(k - n_at) <= 18 else 0
                        inband += 1 if lo_n <= k <= hi_n else 0
                pw["%s, a step of %s" % (lbl, dname)] = {"n_at": r6(n_at), "seen": round(hit / reps, 3),
                                                         "seen_and_located_within_18_minions": round(near / reps, 3),
                                                         "seen_inside_the_band_widened_one_level": round(inband / reps, 3)}
        fa = {}
        for lbl, pc in (("carry at 11.7 V", CARRY[0]), ("carry at 12.0 V", CARRY[1]), ("carry at 12.3 V", CARRY[2])):
            for sign in (1.0, -1.0):
                r = random.Random(18430 + int(pc * 10) + (0 if sign > 0 else 1))
                ha = hr = 0
                for _ in range(reps):
                    ys = scan_draw(r, model, mu_bump(pc, sign))
                    ha += 1 if FAST_A2.max_t(ys)[0] > tcrit else 0
                    hr += 1 if FAST_REG.max_t(ys)[0] > REG_T else 0
                fa["%s, sign %+d" % (lbl, sign)] = {"a2_seen": round(ha / reps, 3), "registered_seen": round(hr / reps, 3)}
        for o in (0.005, 0.010):
            r = random.Random(18440 + int(o * 1000))
            ha = hr = 0
            for _ in range(reps):
                ys = scan_draw(r, model, mu_offset(o))
                ha += 1 if FAST_A2.max_t(ys)[0] > tcrit else 0
                hr += 1 if FAST_REG.max_t(ys)[0] > REG_T else 0
            fa["a uniform %g mW at every level but the reference" % (o * 1000)] = {"a2_seen": round(ha / reps, 3),
                                                                                  "registered_seen": round(hr / reps, 3)}
        r = random.Random(18450)
        ha = sum(1 for _ in range(reps) if FAST_A2.max_t(scan_draw(r, model, mu_offset(0.0)))[0] > tcrit)
        fa["no feature (the nominal false alarm)"] = {"a2_seen": round(ha / reps, 3)}
        out[model] = {"power": pw, "false_alarm": fa}
    out["max_dither_bump_w"] = r6(max(abs(bump(C_BASE + x / 1000.0, CARRY[1], 1.0)) for x in range(0, 2400)))
    out["band_widened_n"] = [r6(lo_n), r6(hi_n)]
    out["draws_per_case"] = reps
    return out


# ---- A2-2: which R governs ------------------------------------------------------------------------------------------------------------------
def delta_ratio_nc(levels, small, large, null_n=0):
    """A2-2's null-corrected R: each slope through the null level's mean c, b = sum n (y - c) / sum n^2 over the quads of its levels; the
    95% interval by the delta method from the pooled within-level variance s2 of the part's quads (every level, the null's too, as
    delta_ratio), with c's variance s2 / N0 carried into both slopes and their covariance. Returns (R, lo, hi, b_small, b_large, c)."""
    nul = levels[null_n]
    cc = c.fmean(nul)
    ss = [(n, y) for n in small for y in levels[n]]
    ll = [(n, y) for n in large for y in levels[n]]
    s2n_s, s2n_l = math.fsum(n * n for n, _ in ss), math.fsum(n * n for n, _ in ll)
    sn_s, sn_l = math.fsum(n for n, _ in ss), math.fsum(n for n, _ in ll)
    bs = math.fsum(n * (y - cc) for n, y in ss) / s2n_s
    bl = math.fsum(n * (y - cc) for n, y in ll) / s2n_l
    dev, dof = [], 0
    for n, ys in levels.items():
        m = c.fmean(ys)
        dev.extend((y - m) ** 2 for y in ys)
        dof += len(ys) - 1
    s2 = math.fsum(dev) / dof
    vc = s2 / len(nul)
    gs, gl = sn_s / s2n_s, sn_l / s2n_l
    vs = s2 / s2n_s + gs * gs * vc
    vl = s2 / s2n_l + gl * gl * vc
    cv = gs * gl * vc
    R = bs / bl
    rel = math.sqrt(max(0.0, vs / bs ** 2 + vl / bl ** 2 - 2 * cv / (bs * bl)))
    return R, R * (1 - 1.96 * rel), R * (1 + 1.96 * rel), bs, bl, cc


def disagree(v_reg, v_nc):
    """A2-2: the two readings disagree when one is LINEAR and the other LOW or HIGH, or one LOW and the other HIGH (NOT RESOLVED
    contradicts nothing)."""
    pair = {v_reg, v_nc}
    return ("LINEAR" in pair and (pair & {"LOW", "HIGH"})) or pair == {"LOW", "HIGH"}


def counts_of(part):
    out = {}
    for p in PLAN["arm_S"]["passes"]:
        for it in p["items"]:
            if it["part"] == part:
                out[it["n"]] = out.get(it["n"], 0) + 1
    return out


def governing(v_reg, v_nc, v_null):
    """A2-2: the registered R governs; when the part's own null level reads OFFSET (E184-N's rule), the null-corrected R governs."""
    return v_nc if v_null == "OFFSET" else v_reg


def offset_slope(counts, small, large):
    """dR/do at a linear meter: a protocol offset o in every quad moves the registered R by (g_small - g_large) / s per watt, with
    g = sum n / sum n^2 over a slope's quads and s the step per minion"""
    gs = math.fsum(n * counts[n] for n in small) / math.fsum(n * n * counts[n] for n in small)
    gl = math.fsum(n * counts[n] for n in large) / math.fsum(n * n * counts[n] for n in large)
    return (gs - gl) / S_W


def r_section():
    out = {}
    reps = 2000
    for part, small, large, delta in (("L", DS["L"]["small"], DS["L"]["large"], TH["delta_L"]),
                                      ("P", DS["P"]["small"], DS["P"]["large"], TH["delta_P"])):
        counts = counts_of(part)
        res = {"dR_per_w_of_offset": r6(offset_slope(counts, small, large)), "null_quads": counts[0]}
        for model in ("base", "pess"):
            sq = QSD[model]
            cases = {}
            for name, gain, off, where in (("linear, no offset", 1.0, 0.0, "all"), ("a protocol offset of +5 mW (every level)", 1.0, 0.005, "all"),
                                           ("a protocol offset of +10 mW (every level)", 1.0, 0.010, "all"),
                                           ("a protocol offset of -5 mW (every level)", 1.0, -0.005, "all"),
                                           ("a protocol offset of +20 mW (every level)", 1.0, 0.020, "all"),
                                           ("+5 mW at the switched levels only", 1.0, 0.005, "switched"),
                                           ("small steps read 0.8", 0.8, 0.0, "all"), ("small steps read 0.9", 0.9, 0.0, "all")):
                r = random.Random(18460 + len(cases) + (0 if model == "base" else 50) + (0 if part == "L" else 100))
                tally = {"reg": {}, "nc": {}, "gov": {}, "disagree": 0, "N": {}}
                for _ in range(reps):
                    lv = {}
                    for n, k in counts.items():
                        mu = S_W * n * (gain if n in small else 1.0) + (off if (where == "all" or n != 0) else 0.0)
                        lv[n] = [mu + r.gauss(0.0, sq) for _ in range(k)]
                    _, lo, hi, _, _, _ = delta_ratio(lv, small, large)
                    v1 = c.three_way(lo, hi, delta)
                    _, lo2, hi2, _, _, _ = delta_ratio_nc(lv, small, large)
                    v2 = c.three_way(lo2, hi2, delta)
                    vn = c.null_reading(lv[0], TH["delta_N_w"])[0]
                    vg = governing(v1, v2, vn)
                    for key, val in (("reg", v1), ("nc", v2), ("gov", vg), ("N", vn)):
                        tally[key][val] = tally[key].get(val, 0) + 1
                    tally["disagree"] += 1 if disagree(v1, v2) else 0
                cases[name] = {"registered_R": {k: round(v / reps, 3) for k, v in sorted(tally["reg"].items())},
                               "null_corrected_R": {k: round(v / reps, 3) for k, v in sorted(tally["nc"].items())},
                               "governing_A2_2": {k: round(v / reps, 3) for k, v in sorted(tally["gov"].items())},
                               "disagree": round(tally["disagree"] / reps, 3),
                               "own_null_by_E184-N_rule": {k: round(v / reps, 3) for k, v in sorted(tally["N"].items())}}
            res[model] = cases
        out["E184-" + part] = res
    out["draws_per_case"] = reps
    return out


# ---- A2-5: uncaught partial dips -------------------------------------------------------------------------------------------------------------
E = CHK["e180_fadd_bursts"]
DIP_RATE = E["rate_set_aside_per_block_refresh"]
DIP_DEPTHS = E["depths_w"]
REFRESHES_PER_BLOCK = FC["models"]["base"]["refreshes_per_block"]
P_QUAD = 1.0 - (1.0 - DIP_RATE) ** (4 * REFRESHES_PER_BLOCK)


def contam(r):
    """a quad's contrast moved by one uncaught dip in one of its four blocks: +depth / (2 x refreshes) if in an A block, - if in a B"""
    if r.random() >= P_QUAD:
        return 0.0
    dd = DIP_DEPTHS[r.randrange(len(DIP_DEPTHS))] / (2.0 * REFRESHES_PER_BLOCK)
    return dd if r.random() < 0.5 else -dd


def o_section(tcrit_a2):
    out = {"dip_rate_per_block_refresh": DIP_RATE, "depths_w": DIP_DEPTHS, "refreshes_per_block": REFRESHES_PER_BLOCK,
           "quads_with_a_dip": r6(P_QUAD), "source": "a2-check-e184.json > e180_fadd_bursts (E180's 162 fadd.ps bursts)"}
    reps = 2000
    for model in ("base",):
        sq = QSD[model]
        res = {}
        for tag, use in (("without A2-5 (the registered reader)", True), ("with A2-5 (dips set aside: the base model)", False)):
            r = random.Random(18480 + (0 if use else 1))
            n_null = {"NULL": 0, "OFFSET": 0, "NOT RESOLVED": 0}
            lt = {}
            jt = 0
            pt = {}
            ex = 0
            counts_L, counts_P = counts_of("L"), counts_of("P")
            for _ in range(reps):
                lv = {n: [S_W * n + r.gauss(0.0, sq) + (contam(r) if use else 0.0) for _ in range(k)] for n, k in counts_L.items()}
                n_null[c.null_reading(lv[0], TH["delta_N_w"])[0]] += 1
                _, lo, hi, _, _, _ = delta_ratio(lv, DS["L"]["small"], DS["L"]["large"])
                v = c.three_way(lo, hi, TH["delta_L"])
                lt[v] = lt.get(v, 0) + 1
                jt += 1 if c.jump_reading(lv, TH["z_jump"])[0] == "SEEN" else 0
                pv = {n: [S_W * n + r.gauss(0.0, sq) + (contam(r) if use else 0.0) for _ in range(k)] for n, k in counts_P.items()}
                _, lo, hi, _, _, _ = delta_ratio(pv, DS["P"]["small"], DS["P"]["large"])
                v = c.three_way(lo, hi, TH["delta_P"])
                pt[v] = pt.get(v, 0) + 1
                ex += 1 if lo > TH["exclude_P_lower_end"] else 0
            r2 = random.Random(18482 + (0 if use else 1))
            cs = sum(1 for _ in range(1000) if FAST_A2.max_t(scan_draw(r2, model, mu_offset(0.0), contam if use else None))[0] > tcrit_a2)
            res[tag] = {"E184-N": {k: round(v / reps, 3) for k, v in sorted(n_null.items())},
                        "E184-L if linear": {k: round(v / reps, 3) for k, v in sorted(lt.items())},
                        "E184-J false alarm": round(jt / reps, 3),
                        "E184-P if linear": {k: round(v / reps, 3) for k, v in sorted(pt.items())},
                        "E184-P EXCLUDED if linear": round(ex / reps, 3), "E184-C (A2) false alarm": round(cs / 1000, 3)}
        out[model] = res
    out["draws_per_case"] = reps
    return out


# ---- kit note 1 section 1: the smoke's 16-shire quad -------------------------------------------------------------------------------------------
def k_section():
    y19 = S_W * 19
    out = {"expected_w_if_linear": r6(y19), "bands": {"registered": [0.05, 0.30], "kit note 1": [-0.15, 0.30]}}
    for model in ("base", "pess"):
        sq = QSD[model]
        rows = {}
        for g in (1.0, 0.8, 0.5, 0.2865, 0.0):
            mu = g * y19
            p_reg = phi((0.05 - mu) / sq) + 1.0 - phi((0.30 - mu) / sq)
            p_new = phi((-0.15 - mu) / sq) + 1.0 - phi((0.30 - mu) / sq)
            rows["small steps read %g" % g] = {"no_go_registered_band": r6(p_reg), "no_go_kit_note_1_band": r6(p_new)}
        out[model] = rows
    return out


res = {"what": "E184 dated amendment A2's statistics and powers (power_e184_a2.py)", "inputs": ["inputs-e184.json", "plan-e184.json",
       "forecast-e184.json", "power_e184.py (delta_ratio's text)", "a2-check-e184.json"]}
res["C"] = c_section()
res["R"] = r_section()
res["O"] = o_section(res["C"]["t_crit_a2"])
res["K"] = k_section()
if TEXT:
    C = res["C"]
    L = ["E184 dated amendment A2: statistics and powers (power_e184_a2.py)"]
    L.append("A2-1 E184-C: t*_A2 %.3f (%d draws, scale-free); registered t* %.3f (recomputed on 4,000 draws %.3f); fast twins differ by at "
             "most %.2e in T; dither bump at most %.4f W; band widened by one level: n %s" %
             (C["t_crit_a2"], C["t_crit_a2_draws"], C["t_crit_registered"], C["t_crit_registered_recomputed_4000"],
              C["fast_twins_max_abs_diff_t"], C["max_dither_bump_w"], C["band_widened_n"]))
    for model in ("base", "pess"):
        L.append("  %s power (A2): %s" % (model, json.dumps(C[model]["power"], sort_keys=True)))
        L.append("  %s false alarm (A2 against the registered statistic): %s" % (model, json.dumps(C[model]["false_alarm"], sort_keys=True)))
    for rule in ("E184-L", "E184-P"):
        L.append("A2-2 %s: dR/do %s per W of offset; its own null level has %d quads" % (rule, res["R"][rule]["dR_per_w_of_offset"],
                                                                                           res["R"][rule]["null_quads"]))
        for model in ("base", "pess"):
            L.append("A2-2 %s %s: %s" % (rule, model, json.dumps(res["R"][rule][model], sort_keys=True)))
    L.append("A2-5 contamination: %s" % json.dumps({k: v for k, v in res["O"].items() if k != "base"}, sort_keys=True))
    L.append("A2-5 base: %s" % json.dumps(res["O"]["base"], sort_keys=True))
    L.append("kit note 1 section 1, the smoke's 16-shire quad: %s" % json.dumps(res["K"], sort_keys=True))
    print("\n".join(L))
else:
    print(json.dumps(res, indent=1, sort_keys=True))
