#!/usr/bin/env python3
# /// script
# requires-python = ">=3.9"
# dependencies = ["numpy"]
# ///
"""Q142(p): pool 8's one frozen predictor, M10 (primary) with M9 beside, as registered in
tools/claims-v3/m10/POOL8-REGISTRATION.md (lab 3e97f583, committed before this file existed). Nothing is fitted or tuned here:
every number comes from M10's m10.json and m10-s7.json, M9's m9.json, M9's aifoundry2 part (m9_a2.json) and E170's card term.

  python3 -B predict_pool8.py predict <pool_dir> <card> --counts <counts.json> [--counts <more.json> ...] [--roles <roles.json>]
                                        [--no-reuse] [--out <dir>]
        card: aifoundry3 | aifoundry1c1 (600 MHz pinned) | aifoundry2 | aifoundry1c0 (their own governors, 6 s bursts)
        Writes <out>/predictions-pool8-<card>.json and .md (out defaults to pool_dir). Exits 3, writing nothing, if any float
        tile's counts do not reach its convergence-rule N (registration section 2) or the random anchors' roles cannot be read
        (section 3).
  python3 -B predict_pool8.py plan <pool_dir> --counts <counts.json> [...] [--no-reuse]
        per float tile: the N reached, e(N), and the launch points (n0) the next step of the convergence rule needs.
  python3 -B predict_pool8.py scale <predictions-pool8-aifoundry3|aifoundry1c1.json> <reduction.json> [--out <scale.json>]
        the session's float scale from its scale anchors' items ONLY (registration section 3); nothing else is read.
  python3 -B predict_pool8.py primary <predictions.json> <reduction.json> <scale.json> [--out <file.json>]
        M10's primary per tile at each tile's measured rate (rate.mean) times the scale, with the a-priori arm (s = 1), the
        pass-1 arm, the three-point arm, M9 at the same rate and at the nominal rate, and the 4.5 s heat.
  python3 -B predict_pool8.py burst <predictions-pool8-aifoundry2|aifoundry1c0.json> --anchors <reads.json>
                                      --die-starts <die-starts.json> [--out <file.json>]
        the governed bursts recomputed with the session's zeros-anchor reads ({format: [{burst_w, burst_mhz, die_start}]}) and
        each tile's counted bursts' die starts ({tile: [C, ...]}), for M10 carried and M9, as E165 and E170 did.
  python3 -B predict_pool8.py heat-minutes <chain rise C> [...]      the chain's rise x 1.0 (primary) and x 1.032 (the arm)
  python3 -B predict_pool8.py intervals <predictions-pool8-aifoundry3|aifoundry1c1.json>   the bootstrap lines at the pool's n
  python3 -B predict_pool8.py selftest [--out <file>]                 T1-T8 of the registration's section 1

Standard library and numpy 1.26 (the Intel's system python 3.9). SPDX-License-Identifier: Apache-2.0
"""
import os

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS", "NUMEXPR_NUM_THREADS"):
    os.environ.setdefault(_v, "2")
import argparse  # noqa: E402
import builtins  # noqa: E402
import copy  # noqa: E402
import glob  # noqa: E402
import gzip  # noqa: E402
import hashlib  # noqa: E402
import io  # noqa: E402
import json  # noqa: E402
import math  # noqa: E402
import random  # noqa: E402
import shutil  # noqa: E402
import statistics  # noqa: E402
import sys  # noqa: E402
import tempfile  # noqa: E402

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
DD = os.path.join(ROOT, "docs", "reports", "data")
M10D = os.path.join(DD, "2026-11-04-q142m-m10")
M9D = os.path.join(DD, "2026-11-04-q140m-m9")
M7D = os.path.join(DD, "2026-11-02-q138m-model")
REGD = os.path.join(ROOT, "tools", "claims-v3", "m10")
KD = os.path.join(ROOT, "tools", "claims-v3", "kinds")
B6, B7 = os.path.join(KD, "blind6"), os.path.join(KD, "blind7")
S7D = os.path.join(DD, "2026-11-04-q141t-s7-recount")
REG_MD = os.path.join(REGD, "POOL8-REGISTRATION.md")
REG_JSON = os.path.join(REGD, "pool8-registration.json")
REG_SUMS = os.path.join(REGD, "POOL8-SHA256SUMS")
OWN_SUMS = os.path.join(HERE, "SHA256SUMS")
REGISTRATION_COMMIT = "3e97f583"
CARDS = {"aifoundry3": "a3", "aifoundry1c1": "c1", "aifoundry2": "a2", "aifoundry1c0": "c0"}
HEAT_CARD = {"a3": "aifoundry3", "c1": "aifoundry1-c1"}
ZERO_HALF = hashlib.sha256(bytes(1024)).hexdigest()
FLOATS = ("fp32", "fp16")
E78_ANCHORS = ("fp32.randn", "fp16.randn", "int8.full")
REF_SESSIONS = {"blind6": {"a3": "E153", "c1": "E157"}, "blind7": {"a3": "E163", "c1": "E164"}}
load = lambda p: json.load(open(p))  # noqa: E731
fsha = lambda p: hashlib.sha256(open(p, "rb").read()).hexdigest()  # noqa: E731
fam_of = lambda t: "int8" if t == "int8" else "float"  # noqa: E731
G = {}


class Refused(Exception):
    pass


def stop(msg):
    raise SystemExit("POOL8 STOPPED: " + msg)


def rel(p):
    a = os.path.abspath(p)
    return os.path.relpath(a, ROOT) if a.startswith(ROOT + os.sep) else os.path.basename(a)


# ------------------------------------------------------------------ inputs, checked before any frozen code is imported
def read_sums(path, base=ROOT):
    out = {}
    for line in open(path):
        if line.strip():
            h, p = line.split(None, 1)
            out[os.path.normpath(os.path.join(base, p.strip().lstrip("*")))] = h
    return out


def check_inputs():
    bad = [rel(p) for p, h in read_sums(REG_SUMS).items() if not os.path.isfile(p) or fsha(p) != h]
    m10s = read_sums(os.path.join(M10D, "SHA256SUMS"), M10D)
    m10a = read_sums(os.path.join(M10D, "SHA256SUMS-a2"), M10D)
    for nm, lst in (("m10.json", m10s), ("m10-s7.json", m10a)):
        p = os.path.join(M10D, nm)
        if fsha(p) != lst.get(p):
            bad.append(f"{nm} against M10's list")
    if bad:
        stop("inputs differ from POOL8-SHA256SUMS or M10's lists: " + ", ".join(bad))
    return len(read_sums(REG_SUMS))


def frozen():
    """the frozen modules, imported after check_inputs(): predict_m10_s7 (and predict_m10), fit_m10's chain, predict_blind5's zeros S"""
    if G:
        return G
    for p in (M10D, M7D):
        if p not in sys.path:
            sys.path.insert(0, p)
    import predict_m10_s7 as P7  # noqa: E402
    import predict_m10 as P10  # noqa: E402
    import fit_m10 as FM  # noqa: E402  (its chain, counts and fitter; nothing is fitted unless the self-test's T3 re-derives a fold)
    import predict_blind5 as P5  # noqa: E402  (zeros_S, unchanged)
    G.update(P7=P7, P10=P10, FM=FM, P5=P5, RR=FM.RR, RK=FM.RK, M9=FM.M9, M7=FM.M7, F=FM.F)
    G["m10"], G["s7"] = P7.load_m10(), P7.load_s7()
    G["m9"] = load(os.path.join(M9D, "m9.json"))
    G["m7heat"] = load(os.path.join(M7D, "m7.json"))["heat"]
    G["reg"] = load(REG_JSON)
    G["zeros"], G["zr"] = FM.M7.zeros_counts(), FM.M9.zeros_rows()
    G["zeros_S"] = {"a3": P5.zeros_S("aifoundry3"), "c1": P5.zeros_S("aifoundry1")}
    G["prices_e"] = FM.RR.prices()
    return G


def heat_factors():
    """the factors on Q138(t)'s chain: the primary from m10-s7.json (never predict_m10.chain_gain), the arm from m10.json"""
    g = frozen()
    prim = g["P7"].chain_gain_primary(g["s7"])
    arm = g["P7"].chain_gain_arm(g["m10"], g["s7"])
    if prim != 1.0 or g["s7"]["entered_primary"].get("d") is not None:
        stop(f"the heat-over-minutes primary factor is {prim}, not 1.0 (registration section 1)")
    return prim, arm


def minutes_rise(P_chain_c):
    """a hold's predicted plateau rise from Q138(t)'s chain rise P (arm A, given the watts): (primary, arm)"""
    prim, arm = heat_factors()
    return prim * P_chain_c, arm * P_chain_c


# ------------------------------------------------------------------ the rate (registration section 4)
def stated_rates():
    g = frozen()
    rt = load(os.path.join(M10D, "a2-checks-m10.json"))["rate"]["by_session_format"]
    reg = g["reg"]["rate"]
    out = {}
    for cd, ses in reg["delta_sessions"].items():
        out[cd] = {}
        for t in ("fp32", "fp16", "int8"):
            d = -statistics.mean(rt[f"{s} {t}"]["mean_pct"] for s in ses)
            if abs(d - reg["delta_pct"][cd][t]) > 1e-9:
                stop(f"the stated offset {cd} {t} reads {d}, the registration {reg['delta_pct'][cd][t]}")
            out[cd][t] = {"delta_pct": d, "nominal_per_s": g["F"].RATE[t], "stated_per_s": g["F"].RATE[t] * (1.0 - d / 100.0)}
    return out


# ------------------------------------------------------------------ the pool
def manifest(pool):
    p = os.path.join(pool, "blind8.json")
    if os.path.exists(p):
        return p, load(p)
    c = []
    for q in sorted(glob.glob(os.path.join(pool, "*.json"))):
        try:
            j = load(q)
        except (ValueError, OSError):
            continue
        if isinstance(j, dict) and isinstance(j.get("tiles"), list) and all(isinstance(x, dict) and "file" in x for x in j["tiles"]):
            c.append((q, j))
    if len(c) != 1:
        stop(f"no single manifest with a 'tiles' list in {pool}: {[rel(q) for q, _ in c]}")
    return c[0]


def tile_bytes(pool, meta):
    p = os.path.join(pool, meta["file"])
    b = open(p, "rb").read()
    h = hashlib.sha256(b).hexdigest()
    want = (meta.get("sha256") or {}).get("whole") if isinstance(meta.get("sha256"), dict) else meta.get("sha256")
    if want and h != want:
        stop(f"{meta['name']}: sha256 {h} differs from its manifest's {want}")
    return p, b, h


def earlier_tiles():
    """(sha256, type) of every pool-6 and pool-7 tile -> [(pool, name, type)], for the re-run sets and the reuse of committed points.
    The type is part of the key: the bench and the card read the same bytes differently in each format (pool 7's three zeros
    anchors share one file's bytes), so a tile is the same tile only in the same format (dated note A1-1)."""
    out = {}
    for pool, d in (("blind6", B6), ("blind7", B7)):
        for m in load(os.path.join(d, f"{pool}.json"))["tiles"]:
            out.setdefault((m["sha256"]["whole"], m["type"]), []).append((pool, m["name"], m["type"]))
    return out


def m10_anchor_names():
    return list(frozen()["m10"]["families"]["float"]["session_scale"]["anchors"])


def roles(man, pool, roles_file=None):
    """registration section 3: zeros / scale / check for every manifest anchor"""
    given = load(roles_file) if roles_file else {}
    out, why = {}, []
    for m in man["tiles"]:
        if not m.get("anchor"):
            continue
        name = m["name"]
        _, b, _ = tile_bytes(pool, m)
        if len(b) == 2048 and hashlib.sha256(b[:1024]).hexdigest() == ZERO_HALF and hashlib.sha256(b[1024:]).hexdigest() == ZERO_HALF:
            r, src = "zeros", "bytes"
        elif str(m.get("anchor_role", "")).lower() in ("check", "scale"):
            r, src = str(m["anchor_role"]).lower(), "anchor_role"
        elif str(m.get("role", "")).lower() in ("check", "scale"):
            r, src = str(m["role"]).lower(), "role"
        elif m.get("check") is True:
            r, src = "check", "check"
        elif "check" in name.lower():
            r, src = "check", "name"
        else:
            r, src = "scale", "default"
        if name in given:
            if src in ("anchor_role", "role", "check", "bytes") and given[name] != r:
                why.append(f"{name}: the roles file says {given[name]}, the manifest {r} ({src})")
            elif src in ("name", "default"):
                r, src = given[name], "roles file"
        out[name] = {"role": r, "source": src, "type": m["type"]}
    for t in FLOATS:
        rnd = [n for n, v in out.items() if v["type"] == t and v["role"] != "zeros"]
        chk = [n for n in rnd if out[n]["role"] == "check"]
        if len(rnd) >= 3 and not chk:
            why.append(f"{t}: {len(rnd)} random anchors and none reads as a check anchor; pass --roles from the design file")
    unknown = sorted(set(given) - set(out))
    if unknown:
        why.append(f"the roles file names tiles that are not anchors: {unknown}")
    if why:
        raise Refused("anchor roles: " + "; ".join(why))
    return out


# ------------------------------------------------------------------ counts and term b (registration section 2)
def committed_point_files():
    cal = ([os.path.join(M9D, "bench-check", "counts-cal.json"), os.path.join(M9D, "recount-rule", "counts-pilot27.json")]
           + sorted(p for p in glob.glob(os.path.join(S7D, "step81", "counts-cal81-*.json")) if not p.endswith("-run.json"))
           + sorted(glob.glob(os.path.join(S7D, "step243", "counts-cal243-*-p[12].json"))))
    m10b = [p for p in sorted(glob.glob(os.path.join(M10D, "bench", "counts-m10-*.json"))) if not p.endswith("-run.json")]
    pools = {"blind6": [os.path.join(B6, "counts-blind6.json")] + m10b,
             "blind7": [os.path.join(B7, "counts-blind7.json"), os.path.join(S7D, "counts-s7-27.json")] + m10b}
    calman = {(m["sha256"], m["type"]): m["name"] for m in load(os.path.join(M9D, "bench-check", "cal-tiles.json"))["tiles"]}
    return pools, cal, calman


_ROWS = {}


def rows_of(path):
    if path not in _ROWS:
        _ROWS[path] = load(path)["rows"] if os.path.exists(path) else {}
    return _ROWS[path]


def counts_points(paths, key):
    """fit_m10.counts_points, line for line, with a read cache (each counts file is parsed once per run)"""
    pts = {}
    for p in paths:
        r = rows_of(p).get(key)
        if r is None:
            continue
        for q in r["points"]:
            if q.get("check_mismatch"):
                stop(f"{key} n0={q['n0']} check_mismatch in {rel(p)}")
            old = pts.get(q["n0"])
            if old is not None and json.dumps(old, sort_keys=True) != json.dumps(q, sort_keys=True):
                stop(f"{key} n0={q['n0']} counted twice with different records")
            pts[q["n0"]] = q
    return pts


def merge_points(pts, more, name):
    for n0, q in more.items():
        if n0 in pts and json.dumps(pts[n0].get("vpu", {}).get("nets_map"), sort_keys=True) != json.dumps(q.get("vpu", {}).get("nets_map"), sort_keys=True):
            stop(f"{name} n0={n0}: counted twice with different counts")
        pts.setdefault(n0, q)


def tile_points(name, t, sha, counts_files, reuse, earlier):
    """every point of a tile: the given counts files (rows by name), plus, by bytes, the committed points of a pool-6/7 or
    calibration tile with the same sha256 (fit_m10.recount's files)"""
    pts, src = {}, []
    for key in (name, name.split(".", 1)[-1]):
        got = counts_points(counts_files, key)
        if got:
            merge_points(pts, got, name)
            src.append("given counts")
            break
    if reuse:
        pools, cal, calman = committed_point_files()
        for pool, nm, _ in earlier.get((sha, t), []):
            merge_points(pts, counts_points(pools[pool], nm), name)
            src.append(f"{pool}:{nm}")
        if (sha, t) in calman:
            merge_points(pts, counts_points(cal, calman[(sha, t)]), name)
            src.append(f"calibration:{calman[(sha, t)]}")
    return pts, src


def three_point_row(name, t, pts, counts_files):
    """the bench's three-point row, as predict_blind7.py reads it: the given counts file's row when it holds the bench's three
    launch points (for fp32 and fp16 RECOUNT-RULE.md's three standard points; int8 runs 318 cycles an op, so its three points sit
    elsewhere and the row is taken as the bench wrote it), else, for a float tile, one built from the three standard points"""
    g = frozen()
    std = g["RR"].points(3)
    for f in counts_files:
        rows = rows_of(f)
        r = rows.get(name) or rows.get(name.split(".", 1)[-1])
        if r is None or "mean" not in r or len(r.get("points", [])) != 3:
            continue
        if t == "int8" or sorted(q["n0"] for q in r["points"]) == sorted(std):
            return r
    if t == "int8" or not all(p in pts for p in std):
        return None
    return {"type": t, "kind": name.split(".", 1)[-1], "points": [pts[p] for p in std], "mean": g["RK"].mean_rows([pts[p] for p in std])}


def recount_tile(name, t, pts):
    """RECOUNT-RULE.md sections 1-4 exactly as fit_m10.recount applies them: from N = 9, x3 while e(N) > 0.10 W, to 243"""
    g = frozen()
    RR, pr = g["RR"], g["prices_e"]
    bound, steps = g["reg"]["term_b"]["bound_w"], g["reg"]["term_b"]["steps"]
    rec = {"by_N": {}}
    N = None
    for n in steps:
        pn = RR.points(n)
        if not all(p in pts for p in pn):
            break
        e = RR.err([RR.point_w(pts[p], t, pr) for p in pn])
        rec["by_N"][str(n)] = {"e_w": e["e_w"], "mean_w": e["mean_w"], "met": e["e_w"] <= bound}
        N = n
        if e["e_w"] <= bound:
            break
    rec["N"] = N
    rec["met"] = bool(N and rec["by_N"][str(N)]["met"])
    rec["complete"] = bool(N and (rec["met"] or N == steps[-1]))
    if not rec["complete"]:
        nxt = steps[0] if N is None else 3 * N
        rec["needs_points"] = [p for p in RR.points(nxt) if p not in pts]
        rec["next_N"] = nxt
        return rec, None
    std = RR.points(3)
    if all(p in pts for p in std):
        rec["three_point_minus_N_w"] = sum(RR.point_w(pts[p], t, pr) for p in std) / 3 - rec["by_N"][str(N)]["mean_w"]
    crowN = {"type": t, "kind": name.split(".", 1)[-1], "points": [pts[p] for p in std], "mean": g["RK"].mean_rows([pts[p] for p in RR.points(N)])}
    return rec, crowN


# ------------------------------------------------------------------ the models
def dot(f, terms, coef):
    return sum(float(f[q]) * c for q, c in zip(terms, coef))


def m10_coeffs(f, t, card):
    """per unit rate (J per op), s = 1: M10's pass-2 and pass-1 coefficients with the card term, and f'Cf for the band"""
    g = frozen()
    fm = g["m10"]["families"][fam_of(t)]
    c = fm["card1_scale"] if card == "c1" else 1.0
    x = [float(f[q]) for q in fm["terms"]]
    C = fm["cov_J2"]
    fCf = sum(x[i] * C[i][j] * x[j] for i in range(len(x)) for j in range(len(x)))
    k = g["P10"].d600(f, t, 1.0, card, g["m10"], 1.0)
    return {"k_J_per_op": k, "k1_J_per_op": c * dot(f, fm["terms"], fm["pass1_coef_J"]), "fCf_J2": fCf, "card_term": c,
            "band_k": fm["band_k"], "pool_rms_w": fm["interval_pool_by_format_card"][f"{t}|{'c1' if card == 'c1' else 'a3'}"]["rms_w"]}


def m9_coeffs(f9, t, card):
    g = frozen()
    mod = g["m9"]["families"][fam_of(t)]
    s = mod["card1_scale_by_format"][t] if card == "c1" else 1.0
    x = [float(f9[q]) for q in mod["terms"]]
    C = mod["cov_J2"]
    fCf = sum(x[i] * C[i][j] * x[j] for i in range(len(x)) for j in range(len(x)))
    return {"k_J_per_op": s * dot(f9, mod["terms"], mod["coef_J"]), "fCf_J2": fCf, "card_term": s, "band_k": mod["band_k"],
            "pool_rms_w": mod["interval_pool_by_format_card"][f"{t}|{'c1' if card == 'c1' else 'a3'}"]["rms_w"]}


def band_hw(co, rate):
    return co["band_k"] * math.sqrt(co["pool_rms_w"] ** 2 + co["card_term"] ** 2 * rate * rate * co["fCf_J2"])


def heat_m10(D, t, card, T_run=4.5):
    g = frozen()
    S = D + g["zeros_S"][card][t]["mean"]
    dT = g["P10"].rise_4p5s(S, T_run, card, g["m10"])
    hh = float(g["m7heat"]["band_k"]) * g["reg"]["bands"]["heat_4p5s"]["rms_c"][card][t]
    return {"S_w": S, "dT_win_c": dT, "dT_win_95": [dT - hh, dT + hh]}


def heat_m9(D, t, card):
    g = frozen()
    H7 = g["m7heat"]
    S = D + g["zeros_S"][card][t]["mean"]
    gg = H7["coef"].get(f"S|{HEAT_CARD[card]}")
    hh = H7["band_k"] * H7["interval_pool_by_format_card_c"][f"{t}|{HEAT_CARD[card]}"]["rms_c"]
    return {"S_w": S, "dT_win_c": gg * S, "dT_win_95": [gg * S - hh, gg * S + hh]}


def a2_part():
    sys.path.insert(0, os.path.join(ROOT, "tools", "claims-v3", "e165"))
    import e165_common as C165  # noqa: E402  (E165's shared module, unchanged; m9a2() checks the part's sha256 before importing it)
    return C165.m9a2()


def card0_relation():
    sys.path.insert(0, os.path.join(ROOT, "tools", "claims-v3", "e170"))
    import e170_common as C170  # noqa: E402  (E170's card term, unchanged)
    return C170


def handoff(d, hw):
    """the carried D in predict_blind7.py's handoff form (rounded to 1e-4 W), and the half-width it implies"""
    lo, hi = round(d - hw, 4), round(d + hw, 4)
    return round(d, 4), [lo, hi], 0.5 * (hi - lo)


# ------------------------------------------------------------------ predict
def predict(pool, cardname, counts_files, roles_file=None, reuse=True, out_dir=None, write=True):
    check_inputs()
    g = frozen()
    heat_factors()
    cd = CARDS[cardname]
    mpath, man = manifest(pool)
    earlier = earlier_tiles()
    rl = roles(man, pool, roles_file)
    rates = stated_rates()
    refused, tiles = {}, {}
    for meta in sorted(man["tiles"], key=lambda m: m["name"]):
        name, t = meta["name"], meta["type"]
        path, b, sha = tile_bytes(pool, meta)
        pts, src = tile_points(name, t, sha, counts_files, reuse, earlier)
        crow3 = three_point_row(name, t, pts, counts_files)
        if crow3 is None:
            refused[name] = {"why": "no bench count at the bench's three launch points",
                             "needs_points": g["RR"].points(3) if t in FLOATS else "run_kinds.py's default three points"}
            continue
        if any(q.get("check_mismatch") for q in crow3["points"]) or crow3["mean"].get("check_mismatch"):
            stop(f"{name}: check_mismatch in its three-point counts")
        f3 = g["FM"].chain_feats(crow3, path, t, g["zeros"], g["zr"])
        rec = {"type": t, "priority": meta.get("priority"), "case": meta.get("case"), "real": meta.get("real"), "sha256": sha,
               "anchor_role": rl.get(name, {}).get("role"), "rerun_of": [f"{p}:{n}" for p, n, _ in earlier.get((sha, t), [])] or None,
               "points_from": src}
        if t in FLOATS:
            rc, crowN = recount_tile(name, t, pts)
            rec["recount"] = rc
            if crowN is None:
                refused[name] = {"why": f"the convergence rule needs N = {rc['next_N']}", "needs_points": rc["needs_points"],
                                 "N_reached": rc["N"], "e_w": rc["by_N"].get(str(rc["N"]), {}).get("e_w") if rc["N"] else None}
                continue
            fN = g["FM"].chain_feats(crowN, path, t, g["zeros"], g["zr"])
        else:
            fN = f3
        rec["features"], rec["features_3pt"] = fN, f3
        if cd in ("a3", "c1"):
            co = m10_coeffs(fN, t, cd)
            co3 = m10_coeffs(f3, t, cd)
            c9 = m9_coeffs(f3, t, cd)
            rs, rn = rates[cd][t]["stated_per_s"], rates[cd][t]["nominal_per_s"]
            D = rs * co["k_J_per_op"]
            hw = band_hw(co, rs)
            m10 = dict(co, k3_J_per_op=co3["k_J_per_op"], fCf3_J2=co3["fCf_J2"], rate_stated_per_s=rs,
                       D_stated_w=D, D_stated_95=[D - hw, D + hw], D3_stated_w=rs * co3["k_J_per_op"],
                       D_pass1_stated_w=rs * co["k1_J_per_op"], heat_stated=heat_m10(D, t, cd))
            D9n, D9s = rn * c9["k_J_per_op"], rs * c9["k_J_per_op"]
            hw9 = band_hw(c9, rn)
            m9 = dict(c9, D_nominal_w=D9n, D_nominal_95=[D9n - hw9, D9n + hw9], D_stated_w=D9s, heat_nominal=heat_m9(D9n, t, cd))
            rec["M10"], rec["M9"] = m10, m9
            if rec["rerun_of"]:
                rec["lg_reference"] = lg_reference(earlier[(sha, t)], cd)
        else:
            A2 = a2_part()
            rn = g["F"].RATE[t]
            co = m10_coeffs(fN, t, "a3")
            c9 = m9_coeffs(f3, t, "a3")
            d10, b10, hw10 = handoff(rn * co["k_J_per_op"], band_hw(co, rn))
            d9, b9, hw9 = handoff(rn * c9["k_J_per_op"], band_hw(c9, rn))
            m10 = {"D600_a3_footing_w": d10, "D600_a3_95": b10, "rate_nominal_per_s": rn, "k_J_per_op": co["k_J_per_op"],
                   "a2_fallback": A2.burst(d10, t, anchors=None, die_starts=None, D_band_hw=hw10)}
            m9 = {"D600_a3_footing_w": d9, "D600_a3_95": b9, "a2_fallback": A2.burst(d9, t, anchors=None, die_starts=None, D_band_hw=hw9)}
            if cd == "c0":
                C170 = card0_relation()
                for blk in (m10, m9):
                    blk["card0_fallback"] = {"burst_mhz": blk["a2_fallback"]["burst_mhz"], "kappa": C170.KAPPA0,
                                             "burst_D_w": round(C170.KAPPA0 * blk["a2_fallback"]["burst_D_w"], 3),
                                             "board": "the session's zeros level for the format at the tile's die starts + burst_D_w (burst mode)"}
            rec["M10"], rec["M9"] = m10, m9
            rec["admission_82w_out"] = bool(max(m10["a2_fallback"]["peak_board_hi95_w"], m9["a2_fallback"]["peak_board_hi95_w"]) > 82.0) if cd == "a2" else None
        tiles[name] = rec
    if refused:
        raise Refused(json.dumps({"refused_tiles": refused}, indent=1, sort_keys=True))
    sets = make_sets(tiles, rl)
    out = {"_note": f"Q142(p) predict_pool8.py: pool 8's frozen predictions on {cardname}, M10 primary with M9 beside; nothing refitted "
                    f"(tools/claims-v3/m10/POOL8-REGISTRATION.md, {REGISTRATION_COMMIT})",
           "card": cardname, "registration_commit": REGISTRATION_COMMIT, "registration_sha256": fsha(REG_MD),
           "predictor_sha256": fsha(os.path.abspath(__file__)), "m10_json_sha256": fsha(os.path.join(M10D, "m10.json")),
           "m10_s7_json_sha256": fsha(os.path.join(M10D, "m10-s7.json")), "m9_json_sha256": fsha(os.path.join(M9D, "m9.json")),
           "manifest": rel(mpath), "manifest_sha256": fsha(mpath), "counts": {rel(p): fsha(p) for p in counts_files},
           "reuse_committed_points": reuse, "roles_file": rel(roles_file) if roles_file else None, "roles": rl,
           "heat_minutes_factors": dict(zip(("primary", "arm"), heat_factors())),
           "rates": rates[cd] if cd in ("a3", "c1") else {"carried_D600_at": "the nominal rate", **{t: g["F"].RATE[t] for t in ("fp32", "fp16", "int8")}},
           "rate_rule": g["reg"]["rate"],
           "sets": sets, "tiles": tiles}
    if cd in ("a3", "c1"):
        out["zeros_S_w"] = g["zeros_S"][cd]
        out["m10_anchors"] = m10_anchor_feats(cd)
    if write:
        od = out_dir or pool
        os.makedirs(od, exist_ok=True)
        js = os.path.join(od, f"predictions-pool8-{cardname}.json")
        json.dump(out, open(js, "w"), indent=1, sort_keys=True)
        open(os.path.join(od, f"predictions-pool8-{cardname}.md"), "w").write(summary_md(out))
    return out


def lg_reference(entries, cd):
    """the re-run tile's own earlier session on this card (registration section 7, P8-LG)"""
    g = frozen()
    out = []
    for pool, nm, _ in entries:
        exp = REF_SESSIONS[pool][cd]
        it = (g["FM"].footing_items(exp) or {}).get(nm)
        if it and isinstance(it.get("D"), dict):
            out.append({"session": exp, "tile": nm, "D_w": it["D"]["mean"], "se_w": it["D"].get("se"), "n": it["D"].get("n")})
    return out


def make_sets(tiles, rl):
    n1 = sorted(n for n, r in tiles.items() if not r["anchor_role"] and not r["rerun_of"] and r["priority"] in (1, None))
    return {"N1": n1, "F1": [n for n in n1 if tiles[n]["type"] in FLOATS], "I1": [n for n in n1 if tiles[n]["type"] == "int8"],
            "by_format": {t: [n for n in n1 if tiles[n]["type"] == t] for t in ("fp32", "fp16", "int8")},
            "RR": sorted(n for n, r in tiles.items() if r["rerun_of"] and not r["anchor_role"] and r["type"] in FLOATS),
            "RR_int8": sorted(n for n, r in tiles.items() if r["rerun_of"] and not r["anchor_role"] and r["type"] == "int8"),
            "KA": sorted(n for n, v in rl.items() if v["role"] == "check" and v["type"] in FLOATS),
            "scale_anchors_pool8": sorted(n for n, v in rl.items() if v["role"] == "scale" and v["type"] in FLOATS),
            "zeros_anchors": sorted(n for n, v in rl.items() if v["role"] == "zeros"),
            "other_priorities": sorted(n for n, r in tiles.items() if not r["anchor_role"] and not r["rerun_of"] and r["priority"] not in (1, None))}


def m10_anchor_feats(cd):
    """the features M10 read for the anchors its own list names (fit_m10.assemble_anchors' map), with their pass-1 coefficients"""
    g = frozen()
    FM = g["FM"]
    feat = {}
    for r in load(os.path.join(M9D, "rows-m9.json")):
        if r["exp"] == "E78" and r["key"] in E78_ANCHORS:
            feat[r["key"]] = r["f"]
    man6 = {m["name"]: m for m in load(os.path.join(B6, "blind6.json"))["tiles"]}
    c6 = load(os.path.join(B6, "counts-blind6.json"))["rows"]
    p6 = load(os.path.join(B6, "predictions-blind6-aifoundry3.json"))["tiles"]
    for n in ("fp32.anchor6_randn", "fp16.anchor6_randn", "int8.anchor6_full"):
        f9 = FM.chain_feats(c6[n], os.path.join(B6, man6[n]["file"]), man6[n]["type"], g["zeros"], g["zr"])
        if max(abs(float(f9[q]) - float(v)) for q, v in p6[n]["features"].items()) > 1e-9:
            stop(f"pool 6's {n}: the chain does not reproduce Q139(x)'s frozen features")
        feat[n] = f9
    f7 = load(os.path.join(B7, "predictions-blind7-aifoundry3.json"))["tiles"]
    for n in ("fp32.anchor7_randn_a", "fp32.anchor7_randn_b", "fp16.anchor7_randn_a", "fp16.anchor7_randn_b",
              "int8.anchor7_full_a", "int8.anchor7_full_b"):
        feat[n] = f7[n]["features"]
    out = {}
    for n, f in feat.items():
        t = n.split(".")[0]
        co = m10_coeffs(f, t, cd)
        out[n] = {"type": t, "features": f, "k_J_per_op": co["k_J_per_op"], "k1_J_per_op": co["k1_J_per_op"],
                  "in_m10_float_list": n in m10_anchor_names()}
    return out


def summary_md(out):
    cd = CARDS[out["card"]]
    L = [f"# Pool 8's frozen predictions on {out['card']} (Q142(p) predict_pool8.py: M10 primary, M9 beside; nothing refitted)", "",
         f"Registration {out['registration_commit']}; m10.json `{out['m10_json_sha256'][:12]}`, m10-s7.json `{out['m10_s7_json_sha256'][:12]}`, "
         f"m9.json `{out['m9_json_sha256'][:12]}`; manifest `{out['manifest']}` `{out['manifest_sha256'][:12]}`; heat over minutes: the chain x "
         f"{out['heat_minutes_factors']['primary']} (primary), x {out['heat_minutes_factors']['arm']} (arm).", ""]
    if cd in ("a3", "c1"):
        L += ["D: W over the type's own zeros at 600 MHz, Q139(u)'s footing, at the stated rate and s = 1 (the a-priori arm; the primary is s x the "
              "measured rate x the per-op coefficient, computed after the session's anchors). Bands 95%.", "",
              "| tile | role | prio | N | e(N) W | M10 D | 95% | M10 3pt | M9 D (nominal) | M10 dT C |", "|---|---|---|---:|---:|---:|---|---:|---:|---:|"]
        for n, r in out["tiles"].items():
            m, m9, rc = r["M10"], r["M9"], r.get("recount") or {}
            e = rc.get("by_N", {}).get(str(rc.get("N")), {}).get("e_w")
            L.append(f"| `{n}` | {r['anchor_role'] or ('re-run' if r['rerun_of'] else '')} | {r['priority']} | {rc.get('N', 3)} | "
                     f"{'' if e is None else f'{e:.3f}'} | {m['D_stated_w']:.3f} | [{m['D_stated_95'][0]:.2f}, {m['D_stated_95'][1]:.2f}] | "
                     f"{m['D3_stated_w']:.3f} | {m9['D_nominal_w']:.3f} | {m['heat_stated']['dT_win_c']:.2f} |")
    else:
        L += ["Bursts under the card's own governor at the part's fallback and T_ref (recomputed per tile from the session's reads by `burst`).", "",
              "| tile | prio | M10 D600 | M10 MHz | M10 board W | M10 peak hi95 | M9 D600 | M9 MHz | M9 board W | M9 peak hi95 | out at 82 W |",
              "|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---|"]
        for n, r in out["tiles"].items():
            a, b = r["M10"]["a2_fallback"], r["M9"]["a2_fallback"]
            L.append(f"| `{n}` | {r['priority']} | {r['M10']['D600_a3_footing_w']:.3f} | {a['burst_mhz']:.1f} | {a['burst_board_w']:.2f} | "
                     f"{a['peak_board_hi95_w']:.2f} | {r['M9']['D600_a3_footing_w']:.3f} | {b['burst_mhz']:.1f} | {b['burst_board_w']:.2f} | "
                     f"{b['peak_board_hi95_w']:.2f} | {'YES' if r.get('admission_82w_out') else ''} |")
    L += ["", "Sets: " + "; ".join(f"{k} {len(v) if isinstance(v, list) else sum(len(x) for x in v.values())}" for k, v in out["sets"].items())]
    return "\n".join(L) + "\n"


# ------------------------------------------------------------------ plan
def plan(pool, counts_files, reuse=True):
    check_inputs()
    g = frozen()
    _, man = manifest(pool)
    earlier = earlier_tiles()
    out = {}
    for meta in sorted(man["tiles"], key=lambda m: m["name"]):
        name, t = meta["name"], meta["type"]
        path, b, sha = tile_bytes(pool, meta)
        pts, src = tile_points(name, t, sha, counts_files, reuse, earlier)
        std = g["RR"].points(3)
        if t not in FLOATS:
            ok = three_point_row(name, t, pts, counts_files) is not None
            out[name] = {"type": t, "complete": ok, "needs": None if ok else "the bench's three-point row (run_kinds.py's default points)"}
            continue
        rc, crowN = recount_tile(name, t, pts)
        e = rc["by_N"].get(str(rc["N"]), {}).get("e_w") if rc["N"] else None
        out[name] = {"type": t, "N": rc["N"], "e_w": e, "complete": rc["complete"],
                     "needs_points": sorted(set(rc.get("needs_points", [])) | {p for p in std if p not in pts}), "points_from": src}
    return out


# ------------------------------------------------------------------ scale and primary (registration section 3)
def scale(pred, reduction):
    """the session's float scale from its scale anchors' items only: predict_m10.session_scale's statistic, unchanged, with the
    anchor list set to M10's own float anchors and pool 8's scale anchors"""
    check_inputs()
    g = frozen()
    cd = CARDS[pred["card"]]
    if cd not in ("a3", "c1"):
        stop("scale is for a 600 MHz session")
    items = load(reduction)["items"]
    names = list(dict.fromkeys(m10_anchor_names() + list(pred["sets"]["scale_anchors_pool8"])))
    anchors, used, missing = [], [], []
    nominal = []
    for n in names:
        it = items.get(n)
        if not it or not isinstance(it.get("D"), dict) or it["D"].get("mean") is None:
            missing.append(n)
            continue
        t = n.split(".")[0] if n in pred["m10_anchors"] else pred["tiles"][n]["type"]
        f = pred["m10_anchors"][n]["features"] if n in pred["m10_anchors"] else pred["tiles"][n]["features"]
        if isinstance(it.get("rate"), dict) and it["rate"].get("mean"):
            rate = float(it["rate"]["mean"])
        else:   # fit_m10.assemble_anchors' own fallback, mirrored: the nominal rate when the item holds none
            rate = g["F"].RATE[t]
            nominal.append(n)
        anchors.append({"name": n, "type": t, "f": f, "D": float(it["D"]["mean"]), "rate": rate})
        used.append(n)
    m10 = copy.deepcopy(g["m10"])
    m10["families"]["float"]["session_scale"]["anchors"] = used
    s = g["P10"].session_scale(anchors, "float", cd, m10)
    ratios = {}
    c = m10["families"]["float"]["card1_scale"] if cd == "c1" else 1.0
    for a in anchors:
        dh = c * a["rate"] * dot(a["f"], m10["families"]["float"]["terms"], m10["families"]["float"]["pass1_coef_J"])
        ratios[a["name"]] = a["D"] / dh
    return {"_note": "Q142(p) predict_pool8.py scale: the session's float scale from its scale anchors' items only", "card": pred["card"],
            "reduction": rel(reduction), "reduction_sha256": fsha(reduction), "predictions_card": pred["card"], "s_float": s,
            "anchors_used": used, "anchors_missing": missing, "anchors_at_nominal_rate": nominal, "ratios": ratios,
            "rule": "median of D / (rate x card term x pass-1 prices x features); 1 if none"}


def primary(pred, reduction, sc):
    check_inputs()
    cd = CARDS[pred["card"]]
    items = load(reduction)["items"]
    if sc["reduction_sha256"] != fsha(reduction):
        stop("the scale was read from another reduction")
    s = float(sc["s_float"])
    out = {"_note": "Q142(p) predict_pool8.py primary: M10's primary at each tile's measured rate x the session's float scale",
           "card": pred["card"], "s_float": s, "reduction_sha256": sc["reduction_sha256"], "tiles": {}}
    for n, r in pred["tiles"].items():
        t, m, m9 = r["type"], r["M10"], r["M9"]
        it = items.get(n) or {}
        rate = (it.get("rate") or {}).get("mean")
        src = "measured"
        if rate is None:
            rate, src = m["rate_stated_per_s"], "stated (no measured rate)"
        ss = s if t in FLOATS else 1.0
        D = ss * rate * m["k_J_per_op"]
        hw = band_hw(m, rate)
        D0 = rate * m["k_J_per_op"]
        D9 = rate * m9["k_J_per_op"]
        out["tiles"][n] = {"type": t, "rate_per_s": rate, "rate_source": src, "M10_primary_w": D, "M10_primary_95": [D - hw, D + hw],
                           "M10_a_priori_w": D0, "M10_pass1_w": rate * m["k1_J_per_op"], "M10_3pt_w": ss * rate * m["k3_J_per_op"],
                           "M9_w": D9, "M9_95": [D9 - band_hw(m9, rate), D9 + band_hw(m9, rate)], "M9_nominal_w": m9["D_nominal_w"],
                           "M10_heat": heat_m10(D, t, cd), "M9_heat": heat_m9(D9, t, cd)}
    return out


def burst(pred, anchors, die_starts):
    check_inputs()
    cd = CARDS[pred["card"]]
    A2 = a2_part()
    g = frozen()
    out = {"_note": "Q142(p) predict_pool8.py burst: the governed bursts recomputed with the session's reads", "card": pred["card"], "tiles": {}}
    C170 = card0_relation() if cd == "c0" else None
    for n, r in pred["tiles"].items():
        t = r["type"]
        ds = die_starts.get(n)
        rec = {}
        for lab in ("M10", "M9"):
            blk = r[lab]
            lo, hi = blk["D600_a3_95"]
            hw = 0.5 * (hi - lo)
            if cd == "a2":
                rec[lab] = A2.burst(blk["D600_a3_footing_w"], t, anchors=anchors, die_starts=ds, D_band_hw=hw)
            else:
                b = C170.pred_card0(blk["D600_a3_footing_w"], t, anchors, ds, D_band_hw=hw)
                if b is not None and lab == "M10":
                    b["burst_die_rise_c_M9_law"] = b["burst_die_rise_c"]
                    b["burst_die_rise_c"] = round(g["P10"].rise_card0_burst(b["burst_board_w"], g["m10"]), 3)
                    b["rise_law"] = f"M10 c2: {g['m10']['card0_burst_heat_k_c_per_w']} C/W over 21.5 W"
                rec[lab] = b
        out["tiles"][n] = rec
    return out


# ------------------------------------------------------------------ intervals (registration section 8)
def seed_of(rule):
    return frozen()["reg"]["scoring"]["seed_base"] + sum(ord(c) for c in rule)


def boot_range(ref, n, rule, stat="rms", draws=None):
    draws = draws or frozen()["reg"]["scoring"]["bootstrap_draws"]
    rng = random.Random(seed_of(rule))
    vals = []
    for _ in range(draws):
        x = [ref[rng.randrange(len(ref))] for _ in range(n)]
        vals.append(math.sqrt(sum(v * v for v in x) / n) if stat == "rms" else sum(x) / n)
    vals.sort()
    return [vals[int(0.025 * draws)], vals[int(0.975 * draws) - 1]]


def ref_errors(cd):
    rows = load(os.path.join(M10D, "rows-m10.json"))
    out = {}
    for t in ("fp32", "fp16", "int8"):
        v = "B" if t == "int8" else "B+a+b"
        out[t] = [r["err_w"][v] for r in rows if r["type"] == t and r["card"] == cd and r["err_w"].get(v) is not None]
    return out


def intervals(pred):
    cd = CARDS[pred["card"]]
    ref = ref_errors(cd)
    S = pred["sets"]["by_format"]
    out = {}
    for rule, t in (("P8-P1", "fp32"), ("P8-P2", "fp16"), ("P8-P3", "int8")):
        if S[t]:
            out[rule] = {"n": len(S[t]), "ref_n": len(ref[t]), "rms_95": boot_range(ref[t], len(S[t]), rule)}
    return out


# ------------------------------------------------------------------ self-test (registration section 1, T1-T8)
def selftest():
    opened = set()
    _open, _gz = builtins.open, gzip.open

    def note(p):
        try:
            a = os.path.abspath(os.fspath(p))
            if a.startswith(ROOT + os.sep) and os.path.isfile(a):
                opened.add(os.path.relpath(a, ROOT))
        except TypeError:
            pass

    def topen(p, *a, **k):
        note(p)
        return _open(p, *a, **k)

    def tgz(p, *a, **k):
        note(p)
        return _gz(p, *a, **k)
    builtins.open, io.open, gzip.open = topen, topen, tgz
    res = {}
    try:
        n_in = check_inputs()
        g = frozen()
        FM, P10 = g["FM"], g["P10"]
        res["inputs"] = {"POOL8-SHA256SUMS": n_in, "ok": True}
        # T1: the primary factor
        prim, arm = heat_factors()
        hd = load(os.path.join(M10D, "heldout-m10.json"))["heat_d_chain_gain"]["holds"]
        big = [h for h in hd if h["fitted"] and h["R_C"] >= 10.0]
        w1 = max(abs((h["R_C"] - minutes_rise(h["P_C"])[0]) - h["e_C"]) for h in big)
        w2 = max(abs((h["R_C"] - minutes_rise(h["P_C"])[1]) - (h["e_C"] - 0.03199 * h["P_C"])) for h in big)
        hb = load(os.path.join(M10D, "heldout-m10.json"))["heat_c1"]["base_refit_loko"]
        hreg = g["reg"]["bands"]["heat_4p5s"]["rms_c"]
        hbad = [f"{cd}|{t}" for cd in ("a3", "c1") for t in ("fp32", "fp16", "int8")
                if abs(hreg[cd][t] - hb[f"{t}|{HEAT_CARD[cd]}"]["rms_c"]) > 1e-12]
        res["T1"] = {"primary_factor": prim, "arm_factor": arm, "large_rises": len(big), "max_primary_vs_armA_c": w1, "max_arm_vs_formula_c": w2,
                     "heat_4p5s_band_rms_as_heldout": not hbad, "heat_band_mismatch": hbad,
                     "pass": prim == 1.0 and abs(arm - 1.03199) < 1e-12 and g["s7"]["entered_primary"].get("d") is None and len(big) == 9
                     and w1 < 1e-12 and w2 < 1e-9 and not hbad}
        # T2: pool 7's 104 rows in sample
        rows, _ = FM.assemble()
        anchors, _ = FM.assemble_anchors(rows, g["zeros"], g["zr"])
        rc = FM.recount(os.path.join(M10D, "bench"), g["zeros"], g["zr"])
        earlier = earlier_tiles()
        ref = {(r["exp"], r["key"]): r for r in load(os.path.join(M10D, "rows-m10.json"))}
        man7 = {m["name"]: m for m in load(os.path.join(B7, "blind7.json"))["tiles"]}
        c7 = os.path.join(B7, "counts-blind7.json")
        worst2, n2, wN = 0.0, 0, 0.0
        my_rc = {}
        for r in rows:
            if r["exp"] not in ("E163", "E164"):
                continue
            m = man7[r["key"]]
            path = os.path.join(B7, m["file"])
            t = r["type"]
            pts, _ = tile_points(r["key"], t, m["sha256"]["whole"], [c7], True, earlier)
            crow3 = three_point_row(r["key"], t, pts, [c7])
            f = FM.chain_feats(crow3, path, t, g["zeros"], g["zr"])
            if r["S_class"]:
                rec, crowN = recount_tile(r["key"], t, pts)
                my_rc[r["key"]] = rec
                f = FM.chain_feats(crowN, path, t, g["zeros"], g["zr"])
                wN = max(wN, max(abs(float(f[q]) - float(rc[r["key"]]["fN"][q])) for q in g["m10"]["families"]["float"]["terms"]))
            fam = fam_of(t)
            used = [a["name"] for a in anchors.get(r["sess"], []) if fam_of(a["type"]) == "float"]
            s = scale_from_list(anchors.get(r["sess"], []), used, r["card"]) if fam == "float" else 1.0
            co = m10_coeffs(f, t, r["card"])
            d = s * r["rate"] * co["k_J_per_op"]
            worst2 = max(worst2, abs(d - ref[(r["exp"], r["key"])]["M10_insample_pred_w"]))
            n2 += 1
        hm = load(os.path.join(M10D, "heldout-m10.json"))["S_recount"]
        wrc = max(abs(my_rc[k]["by_N"][str(my_rc[k]["N"])]["e_w"] - hm[k]["by_N"][str(hm[k]["N"])]["e_w"]) for k in my_rc if k in hm)
        nmatch = sum(1 for k in my_rc if k in hm and my_rc[k]["N"] == hm[k]["N"])
        res["T2"] = {"rows": n2, "max_abs_diff_w": worst2, "S_tiles": len(my_rc), "S_tiles_same_N_as_M10": nmatch, "max_e_N_diff_w": wrc,
                     "max_S_feature_diff": wN, "pass": n2 == 104 and worst2 <= 1e-9 and nmatch == len(my_rc) and wrc < 1e-12 and wN < 1e-9}
        # T3: pool 7's held-out predictions, the fold re-derived by fit_m10.Fit10 and fed to the predictor's formula
        res["T3"] = t3_heldout(rows, anchors, rc)
        # T4: refusal
        res["T4"] = t4_refusal(earlier)
        # T5: aifoundry2 through Q140(l)'s part
        res["T5"] = t5_a2()
        # T6: card 0
        res["T6"] = t6_card0()
        # T7: M9 at 600 MHz
        res["T7"] = t7_m9()
        # T9 (not registered; an added end-to-end check): predict, scale, primary and burst on a pool of committed tiles
        res["T9"] = t9_end_to_end()
        # the rate
        rt = stated_rates()
        res["rate"] = {cd: {t: round(v["delta_pct"], 6) for t, v in x.items()} for cd, x in rt.items()}
    finally:
        builtins.open, io.open, gzip.open = _open, _open, _gz
    mods = set()
    for m in list(sys.modules.values()):
        f = getattr(m, "__file__", None)
        if f and os.path.abspath(f).startswith(ROOT + os.sep):
            mods.add(os.path.relpath(os.path.abspath(f), ROOT))
    seen = sorted((opened | mods) - {os.path.relpath(OWN_SUMS, ROOT)})
    listed = {os.path.relpath(p, ROOT) for p in read_sums(REG_SUMS)}
    own = {os.path.relpath(p, ROOT): h for p, h in read_sums(OWN_SUMS, ROOT).items()} if os.path.exists(OWN_SUMS) else {}
    unlisted = [p for p in seen if p not in listed and p not in own]
    badown = [p for p, h in own.items() if not os.path.isfile(os.path.join(ROOT, p)) or fsha(os.path.join(ROOT, p)) != h]
    res["T8"] = {"files_opened_or_imported": len(seen), "unlisted": unlisted, "own_list_entries": len(own), "own_list_bad": badown,
                 "pass": not unlisted and not badown and bool(own)}
    res["PASS"] = all(v.get("pass") for k, v in res.items() if k.startswith("T"))
    return res


def scale_from_list(anchor_dicts, names, card):
    g = frozen()
    m10 = copy.deepcopy(g["m10"])
    m10["families"]["float"]["session_scale"]["anchors"] = list(names)
    return g["P10"].session_scale(anchor_dicts, "float", card, m10)


def t3_heldout(rows, anchors, rc):
    g = frozen()
    FM, P10 = g["FM"], g["P10"]
    ref = {(r["exp"], r["key"]): r for r in load(os.path.join(M10D, "rows-m10.json"))}
    out = {"rows": 0, "kinds": 0, "max_abs_vs_committed_w": 0.0, "max_abs_vs_fitter_w": 0.0}
    for fam in ("float", "int8"):
        fr = [r for r in rows if fam_of(r["type"]) == fam]
        terms = g["m10"]["families"][fam]["terms"]
        anc = {s: [x for x in v if fam_of(x["type"]) == fam] for s, v in anchors.items()}
        over = {i: rc[r["key"]]["fN"] for i, r in enumerate(fr) if r["S_class"]} if fam == "float" else None
        var = "B+a+b" if fam == "float" else "B"
        ft = FM.Fit10(fr, terms, anc, fam == "float", over)
        kinds = sorted({r["kind"] for r in fr if r["exp"] in ("E163", "E164")})
        for kd in kinds:
            k = ft.kinds.index(kd)
            fit = ft.fit(k)
            bJ = fit["b"] / ft.sc
            fake = copy.deepcopy(g["m10"])
            fake["families"][fam]["coef_J"] = [float(v) for v in bJ]
            fake["families"][fam]["card1_scale"] = float(fit["c"])
            m = ft.kid == k
            pf = ft.pred(m, fit)
            for j, i in enumerate([int(x) for x in m.nonzero()[0]]):
                r = fr[i]
                f = over[i] if (over and i in over) else r["f"]
                s = float(fit["s"][ft.sid[i]]) if fam == "float" else 1.0
                d = P10.d600(f, r["type"], r["rate"], r["card"], fake, s)
                rr = ref[(r["exp"], r["key"])]
                out["max_abs_vs_committed_w"] = max(out["max_abs_vs_committed_w"], abs(d - (rr["D"] - rr["err_w"][var])))
                out["max_abs_vs_fitter_w"] = max(out["max_abs_vs_fitter_w"], abs(d - float(pf[j])))
                out["rows"] += 1
            out["kinds"] += 1
    out["pass"] = out["rows"] == 104 and out["kinds"] == 52 and out["max_abs_vs_committed_w"] <= 5e-7 and out["max_abs_vs_fitter_w"] <= 1e-9
    return out


def t4_refusal(earlier):
    g = frozen()
    tmp = tempfile.mkdtemp(prefix="pool8-selftest-")
    try:
        man7 = {m["name"]: m for m in load(os.path.join(B7, "blind7.json"))["tiles"]}
        names = ["fp32.b_onebit_b20_one", "int8.bheld_33"]
        anames = ["fp32.anchor7_zeros", "fp32.anchor7_randn_a", "fp32.anchor7_randn_b", "fp32.uniform_pm1"]
        for n in names + anames:
            m = man7[n]
            os.makedirs(os.path.join(tmp, os.path.dirname(m["file"])), exist_ok=True)
            shutil.copyfile(os.path.join(B7, m["file"]), os.path.join(tmp, m["file"]))
        json.dump({"tiles": [man7[n] for n in names]}, open(os.path.join(tmp, "blind8.json"), "w"))
        c7 = os.path.join(B7, "counts-blind7.json")
        s27 = os.path.join(S7D, "counts-s7-27.json")
        m81 = os.path.join(M10D, "bench", "counts-m10-b20_one-27to81.json")
        cases = {}
        for lab, files in (("three points only", [c7]), ("points to N = 27", [c7, s27]), ("points to N = 81", [c7, s27, m81])):
            try:
                o = predict(tmp, "aifoundry3", files, reuse=False, write=False)
                rc = o["tiles"]["fp32.b_onebit_b20_one"]["recount"]
                cases[lab] = {"refused": False, "N": rc["N"], "e_w": rc["by_N"][str(rc["N"])]["e_w"]}
            except Refused as e:
                cases[lab] = {"refused": True, "why": json.loads(str(e))["refused_tiles"]}
        man = {"tiles": [man7[n] for n in anames[:3]] + [dict(man7["fp32.uniform_pm1"], anchor=True)]}
        try:
            roles(man, tmp)
            cases["three random fp32 anchors, none a check"] = {"refused": False}
        except Refused as e:
            cases["three random fp32 anchors, none a check"] = {"refused": True, "why": str(e)}
        rf = os.path.join(tmp, "roles.json")
        json.dump({"fp32.uniform_pm1": "check"}, open(rf, "w"))
        try:
            rl = roles(man, tmp, rf)
            cases["the same with a roles file"] = {"refused": False, "roles": {n: v["role"] for n, v in rl.items()}}
        except Refused as e:
            cases["the same with a roles file"] = {"refused": True, "why": str(e)}
        wrote = sorted(glob.glob(os.path.join(tmp, "predictions-*")))
        ok = (cases["three points only"]["refused"] and cases["points to N = 27"]["refused"]
              and cases["points to N = 27"]["why"]["fp32.b_onebit_b20_one"]["N_reached"] == 27
              and not cases["points to N = 81"]["refused"] and cases["points to N = 81"]["N"] == 81
              and abs(cases["points to N = 81"]["e_w"] - 0.095) < 0.0005 and cases["three random fp32 anchors, none a check"]["refused"]
              and not cases["the same with a roles file"]["refused"]
              and cases["the same with a roles file"]["roles"] == {"fp32.anchor7_zeros": "zeros", "fp32.anchor7_randn_a": "scale",
                                                                    "fp32.anchor7_randn_b": "scale", "fp32.uniform_pm1": "check"}
              and not wrote)
        for v in cases.values():
            if isinstance(v.get("why"), dict):
                v["why"] = {k: {kk: vv for kk, vv in x.items() if kk != "needs_points"} | {"needs_points_n": len(x.get("needs_points", []))}
                            for k, x in v["why"].items()}
        return {"cases": cases, "files_written": wrote, "pass": bool(ok)}
    finally:
        shutil.rmtree(tmp)


def t5_a2():
    g = frozen()
    A2 = a2_part()
    p2 = load(os.path.join(B7, "predictions-blind7-aifoundry2.json"))["tiles"]
    man7 = load(os.path.join(B7, "blind7.json"))["tiles"]
    counts = load(os.path.join(B7, "counts-blind7.json"))["rows"]
    n, diff, d600 = 0, [], 0.0
    for m in man7:
        name, t = m["name"], m["type"]
        f9 = g["FM"].chain_feats(counts[name], os.path.join(B7, m["file"]), t, g["zeros"], g["zr"])
        c9 = m9_coeffs(f9, t, "a3")
        rn = g["F"].RATE[t]
        d9, b9, hw9 = handoff(rn * c9["k_J_per_op"], band_hw(c9, rn))
        d600 = max(d600, abs(d9 - p2[name]["M9"]["D600_a3_footing_w"]), abs(b9[0] - p2[name]["M9"]["D600_a3_95"][0]))
        mine = A2.burst(d9, t, anchors=None, die_starts=None, D_band_hw=hw9)
        want = p2[name]["M9"]["a2_q140l"]
        for k, v in want.items():
            if mine.get(k) != v:
                diff.append(f"{name}.{k}")
        n += 1
    return {"tiles": n, "max_D600_diff_w": d600, "fields_differing": diff[:10], "n_fields_differing": len(diff),
            "pass": n == 61 and not diff and d600 < 1e-12}


def t6_card0():
    g = frozen()
    C170 = card0_relation()
    e = load(os.path.join(DD, "2026-11-04-e170-blind7-card0", "results.json"))
    p2 = load(os.path.join(B7, "predictions-blind7-aifoundry2.json"))["tiles"]
    anchors = e["score"]["anchors"]
    tiles = e["score"]["reported"]["tiles"]
    diff, n = [], 0
    for name, tr in sorted(tiles.items()):
        blk = p2[name]["M9"]
        lo, hi = blk["D600_a3_95"]
        b = C170.pred_card0(blk["D600_a3_footing_w"], tr["type"], anchors, tr["die_starts"], D_band_hw=0.5 * (hi - lo))
        for k, v in tr["primary"].items():
            if b.get(k) != v:
                diff.append(f"{name}.{k}: {b.get(k)} vs {v}")
        n += 1
    m10 = g["m10"]
    names = sorted(tiles)
    r = [float(tiles[x]["rise_c"]) for x in names]
    x = [float(tiles[q]["burst_w"]) - 21.5 for q in names]
    kall = sum(a * b for a, b in zip(r, x)) / sum(b * b for b in x)
    loto = []
    for i in range(len(names)):
        ki = sum(r[j] * x[j] for j in range(len(names)) if j != i) / sum(x[j] ** 2 for j in range(len(names)) if j != i)
        loto.append(r[i] - ki * x[i])
    rms_l = math.sqrt(sum(v * v for v in loto) / len(loto))
    hc = load(os.path.join(M10D, "heldout-m10.json"))["heat_c2_card0_burst"]
    prim_rise = [g["P10"].rise_card0_burst(float(tiles[q]["burst_w"]), m10) for q in names]
    ok = (n == 39 and not diff and round(kall, 4) == hc["k_all_tiles"] == m10["card0_burst_heat_k_c_per_w"]
          and round(rms_l, 4) == hc["loto"]["rms_c"] and abs(prim_rise[0] - 0.2415 * (float(tiles[names[0]]["burst_w"]) - 21.5)) < 1e-12)
    return {"tiles": n, "primary_fields_differing": diff[:10], "k_all_tiles": kall, "loto_rms_c": rms_l,
            "committed": {"k_all_tiles": hc["k_all_tiles"], "loto_rms_c": hc["loto"]["rms_c"]}, "c0_h1_reference_residuals_c": loto,
            "pass": bool(ok)}


def t9_end_to_end():
    """a pool of pool 7's eight single-high-bit tiles and two int8 tiles, predicted for both 600 MHz cards and card 0; the scale and
    the primary read from E163's and E164's committed reductions must give M10's in-sample predictions (rows-m10.json), and the
    card-0 burst mode on E170's committed reads must give E170's committed primary for M9"""
    g = frozen()
    tmp = tempfile.mkdtemp(prefix="pool8-e2e-")
    try:
        man7 = {m["name"]: m for m in load(os.path.join(B7, "blind7.json"))["tiles"]}
        names = ["fp32.b_onebit_b20_one", "fp32.b_onebit_b20_full", "fp32.b_onebit_b20_pi", "fp32.b_onebit_b20_seventh",
                 "fp32.b_onebit_b22_third", "fp16.b_onebit_b9_one", "fp16.b_onebit_b8_pi", "fp32.b_onebit_b20_third_a1p5",
                 "int8.bheld_33", "int8.b_line_0f_f0"]
        for n in names:
            os.makedirs(os.path.join(tmp, os.path.dirname(man7[n]["file"])), exist_ok=True)
            shutil.copyfile(os.path.join(B7, man7[n]["file"]), os.path.join(tmp, man7[n]["file"]))
        json.dump({"tiles": [man7[n] for n in names]}, open(os.path.join(tmp, "blind8.json"), "w"))
        c7 = [os.path.join(B7, "counts-blind7.json")]
        ins = {(r["exp"], r["key"]): r["M10_insample_pred_w"] for r in load(os.path.join(M10D, "rows-m10.json"))}
        sc_train = g["m10"]["families"]["float"]["session_scales_training"]
        out, ok = {}, True
        for card, exp, red in (("aifoundry3", "E163", g["FM"].FOOTING["E163"]), ("aifoundry1c1", "E164", g["FM"].FOOTING["E164"])):
            pred = predict(tmp, card, c7, reuse=True, out_dir=tmp)
            pj = load(os.path.join(tmp, f"predictions-pool8-{card}.json"))
            sc = scale(pj, red)
            pr = primary(pj, red, sc)
            worst = max(abs(pr["tiles"][n]["M10_primary_w"] - ins[(exp, n)]) for n in names)
            sess = f"{exp}|{CARDS[card]}"
            out[card] = {"s_float": sc["s_float"], "m10_json_s": sc_train.get(sess), "anchors_used": sc["anchors_used"],
                         "max_abs_vs_insample_w": worst, "tiles": len(pr["tiles"]), "same_json_on_reload": pred["tiles"].keys() == pj["tiles"].keys()}
            ok = ok and worst <= 1e-9 and abs(sc["s_float"] - sc_train[sess]) <= 5e-6 and len(pr["tiles"]) == len(names)
        e = load(os.path.join(DD, "2026-11-04-e170-blind7-card0", "results.json"))
        tiles = e["score"]["reported"]["tiles"]
        predict(tmp, "aifoundry1c0", c7, reuse=True, out_dir=tmp)
        pj = load(os.path.join(tmp, "predictions-pool8-aifoundry1c0.json"))
        ds = {n: tiles[n]["die_starts"] for n in names if n in tiles}
        bu = burst(pj, e["score"]["anchors"], ds)
        diff, n0 = [], 0
        for n in ds:
            for k, v in tiles[n]["primary"].items():
                if bu["tiles"][n]["M9"].get(k) != v:
                    diff.append(f"{n}.{k}")
            want = round(g["m10"]["card0_burst_heat_k_c_per_w"] * (bu["tiles"][n]["M10"]["burst_board_w"] - 21.5), 3)
            if bu["tiles"][n]["M10"]["burst_die_rise_c"] != want:
                diff.append(f"{n}.M10 rise")
            n0 += 1
        out["aifoundry1c0"] = {"tiles_in_E170": n0, "fields_differing": diff}
        ok = ok and n0 >= 6 and not diff
        # the same bytes in three formats (pool 7's zeros anchors): reuse by bytes keeps each format's own points (dated note A1-1)
        earlier = earlier_tiles()
        zsha = man7["fp16.anchor7_zeros"]["sha256"]["whole"]
        same = len({man7[f"{t}.anchor7_zeros"]["sha256"]["whole"] for t in ("fp32", "fp16", "int8")}) == 1
        zr16 = rows_of(os.path.join(B7, "counts-blind7.json"))["fp16.anchor7_zeros"]
        pts, _ = tile_points("fp16.anchor7_zeros", "fp16", zsha, [], True, earlier)
        zok = same and sorted(pts) == sorted(q["n0"] for q in zr16["points"]) and all(pts[q["n0"]] == q for q in zr16["points"])
        out["zeros_anchors_one_file_three_formats"] = {"same_bytes": same, "fp16_points_are_fp16s": zok}
        ok = ok and zok
        out["pass"] = bool(ok)
        return out
    finally:
        shutil.rmtree(tmp)


def t7_m9():
    g = frozen()
    man7 = load(os.path.join(B7, "blind7.json"))["tiles"]
    counts = load(os.path.join(B7, "counts-blind7.json"))["rows"]
    out = {}
    ok = True
    for card, cd in (("aifoundry3", "a3"), ("aifoundry1c1", "c1")):
        p = load(os.path.join(B7, f"predictions-blind7-{card}.json"))["tiles"]
        worst, n, dworst = 0.0, 0, 0.0
        for m in man7:
            name, t = m["name"], m["type"]
            f9 = g["FM"].chain_feats(counts[name], os.path.join(B7, m["file"]), t, g["zeros"], g["zr"])
            c9 = m9_coeffs(f9, t, cd)
            D = g["F"].RATE[t] * c9["k_J_per_op"]
            worst = max(worst, abs(round(D, 4) - p[name]["M9"]["D_w"]))
            hw = band_hw(c9, g["F"].RATE[t])
            worst = max(worst, abs(round(D - hw, 4) - p[name]["M9"]["D_95"][0]), abs(round(D + hw, 4) - p[name]["M9"]["D_95"][1]))
            h = heat_m9(D, t, cd)
            dworst = max(dworst, abs(round(h["dT_win_c"], 3) - p[name]["M9"]["dT_win_c"]))
            n += 1
        out[card] = {"tiles": n, "max_abs_after_rounding_w": worst, "max_heat_after_rounding_c": dworst}
        ok = ok and n == 61 and worst == 0.0 and dworst == 0.0
    out["pass"] = bool(ok)
    return out


# ------------------------------------------------------------------ main
def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("predict")
    p.add_argument("pool")
    p.add_argument("card", choices=sorted(CARDS))
    p.add_argument("--counts", action="append", required=True)
    p.add_argument("--roles")
    p.add_argument("--no-reuse", action="store_true")
    p.add_argument("--out")
    q = sub.add_parser("plan")
    q.add_argument("pool")
    q.add_argument("--counts", action="append", default=[])
    q.add_argument("--no-reuse", action="store_true")
    s = sub.add_parser("scale")
    s.add_argument("predictions")
    s.add_argument("reduction")
    s.add_argument("--out")
    r = sub.add_parser("primary")
    r.add_argument("predictions")
    r.add_argument("reduction")
    r.add_argument("scale")
    r.add_argument("--out")
    b = sub.add_parser("burst")
    b.add_argument("predictions")
    b.add_argument("--anchors", required=True)
    b.add_argument("--die-starts", required=True)
    b.add_argument("--out")
    h = sub.add_parser("heat-minutes")
    h.add_argument("rise", nargs="+", type=float)
    i = sub.add_parser("intervals")
    i.add_argument("predictions")
    t = sub.add_parser("selftest")
    t.add_argument("--out")
    a = ap.parse_args()
    if a.cmd == "predict":
        try:
            o = predict(os.path.abspath(a.pool), a.card, [os.path.abspath(c) for c in a.counts], a.roles, not a.no_reuse, a.out)
        except Refused as e:
            print("REFUSED (registration sections 2-3); nothing written:\n" + str(e))
            return 3
        print(summary_md(o))
        return 0
    if a.cmd == "plan":
        print(json.dumps(plan(os.path.abspath(a.pool), [os.path.abspath(c) for c in a.counts], not a.no_reuse), indent=1, sort_keys=True))
        return 0
    if a.cmd in ("scale", "primary", "burst"):
        pred = load(a.predictions)
        if a.cmd == "scale":
            o = scale(pred, a.reduction)
        elif a.cmd == "primary":
            o = primary(pred, a.reduction, load(a.scale))
        else:
            o = burst(pred, load(a.anchors), load(a.die_starts))
        s_ = json.dumps(o, indent=1, sort_keys=True)
        if a.out:
            open(a.out, "w").write(s_ + "\n")
        print(s_)
        return 0
    if a.cmd == "heat-minutes":
        check_inputs()
        print(json.dumps({"rises_c": a.rise, "primary_c": [minutes_rise(x)[0] for x in a.rise], "arm_c": [minutes_rise(x)[1] for x in a.rise],
                          "factors": dict(zip(("primary", "arm"), heat_factors()))}))
        return 0
    if a.cmd == "intervals":
        check_inputs()
        print(json.dumps(intervals(load(a.predictions)), indent=1, sort_keys=True))
        return 0
    res = selftest()
    s_ = json.dumps(res, indent=1, sort_keys=True, default=str)
    if a.out:
        open(a.out, "w").write(s_ + "\n")
    print(json.dumps({k: (v.get("pass") if isinstance(v, dict) and "pass" in v else v) for k, v in res.items()}, sort_keys=True))
    return 0 if res["PASS"] else 1


if __name__ == "__main__":
    sys.exit(main())
