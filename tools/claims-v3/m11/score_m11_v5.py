#!/usr/bin/env python3
"""E185's kit (Q155, Sat 7 Nov 2026): M11's scorer v5 for heat over minutes (REGISTRATION.md section 13 step 1, as amended by A1-A10), with
E185's rules (tools/claims-v3/e185/E185.md section 6, 98fe28b7). Desk only (the Intel). score_m11.py, v2, v3 and v4 stay as committed: v5 imports
v4 unchanged (v4 imports v3, v3 imports v2, v2 imports v1), and every reading v4 makes is printed by v5 unchanged. What v5 adds:

  A10  M11's registered reading from E185 on is A9's arm, the chain over the smoke pass and the measured pass together (A10, 5e708747). v5
       reads every session that passed its start gate on that reading, staged in A4-8's form (its lines file's stages 7-9: the pair lines
       through H_E and Z, then L1 and S, then L2), and runs the registered decision code (score_m11_v2.decide_card_kind, unchanged) on
       those points: the primary readings, under "A10". A session whose arm A9-1 refuses (no smoke telemetry, too few samples, a gap
       outside (0, 600] s) or that names no smoke pass is read on the measured pass alone and named (A10-3). v4's registered
       (measured-pass-only) readings are printed beside under "measured_pass_alone_reported (A10)", and v4's own A9 block is kept.
  E185 the rules of E185.md section 6, on the pass named by --e185 (it must also be one of the --a3 passes, with its --smoke): each of its
       holds read with tools/claims-v3/e185/arms_e185.py's readers on A10's reading, the three arms with the frozen two-pass gains of
       arms-e185-train.json (G_B, G_Rl); per hold e_F, e_B, e_Rl, the cool-down misses over [b + 120, b + 360) s and the rail share; then
       E185-RF, E185-BF, E185-RB and E185-BEST (tau = 0.0884 / sqrt(n)), each SCORED only with at least 4 scored holds, a fp32.randn and an
       int8.neg_ones hold among them; E185-C per arm over the big holds with a complete cool-down window (n_c >= 3). A hold whose rail
       readings miss its anchor or plateau window (under 5 readable rail rows a second) is not scored for Rl, and the three-arm rules read
       on the holds all three arms score. Reported beside: each arm's mean miss per kind, H_E2's |e| / R, the one-pass arms' misses, and the
       precedence of A10 and E185's registration over the pass's first launch record (blind only if both precede it).

It checks SHA256SUMS-a10, SHA256SUMS-score-m11-v4 and tools/claims-v3/e185/SHA256SUMS-e185-registration (repo paths) before it imports
anything; v4, v3, v2 and v1 check theirs on import.

    /usr/bin/python3 -B tools/claims-v3/m11/score_m11_v5.py score --a3 <pass> [--smoke <smoke pass>] [--host <logs dir>] [--a3 ...]
        [--e185 <E185's pass dir>] --lines <out.jsonl> [--json <out>] [--md <out>]
    /usr/bin/python3 -B tools/claims-v3/m11/score_m11_v5.py --self-test --workdir <a new scratch dir> [--json <out>]
Python 3.9 with numpy 1.26 (the Intel's /usr/bin/python3; numpy in the user site, so never -I). SPDX-License-Identifier: Apache-2.0
"""
import sys

sys.dont_write_bytecode = True
import hashlib  # noqa: E402
import json  # noqa: E402
import math  # noqa: E402
import os  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
TREE = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
E185D = os.path.join(TREE, "tools", "claims-v3", "e185")
V5_LISTS = (os.path.join(HERE, "SHA256SUMS-a10"), os.path.join(HERE, "SHA256SUMS-score-m11-v4"), os.path.join(E185D, "SHA256SUMS-e185-registration"))
A10_COMMIT, E185_COMMIT = "5e708747", "98fe28b7"
SIGMA_C = 0.0884
COOL_MIN_N = 3
MIN_RAIL_HZ = 5.0
A10_LABEL = "registered (A10): the chain over the smoke and the measured pass (A9's arm), M11's reading from E185 on"
ALONE_LABEL = "reported (A10): the measured pass alone, the reading of E181 and before"
KIND = {"fp32.randn": "H", "int8.full": "L", "int8.neg_ones": "S", "fp32.zeros": "Z"}


def _sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def _check_v5_lists():
    counts, bad = {}, []
    for p in V5_LISTS:
        name = os.path.relpath(p, TREE)
        if not os.path.exists(p):
            bad.append(f"{name}: missing")
            continue
        n = 0
        for line in open(p):
            parts = line.split()
            if len(parts) != 2:
                continue
            n += 1
            q = os.path.join(TREE, parts[1])
            if not os.path.exists(q) or _sha(q) != parts[0]:
                bad.append(f"{name}: {parts[1]} differs")
        counts[name] = n
    return counts, bad


_V5_COUNTS, _V5_BAD = _check_v5_lists()
if _V5_BAD:
    raise SystemExit("M11 scorer v5 REFUSED: a registered file differs:\n  " + "\n  ".join(_V5_BAD))

sys.path.insert(0, HERE)
import score_m11_v4 as V4  # noqa: E402  (dc35a540, unchanged)
sys.path.insert(0, E185D)
import arms_e185 as ARMS  # noqa: E402  (98fe28b7, unchanged: E185's registered readers)

V3, V2, V1, A9P = V4.V3, V4.V2, V4.V1, V4.A9P
np = V1.np
r4 = V1.r4
_TRAIN = json.load(open(os.path.join(E185D, "arms-e185-train.json")))
GAINS = {"G_B": _TRAIN["two_pass"]["gains"]["G_B"], "G_Rl": _TRAIN["two_pass"]["gains"]["G_Rl"]}         # E185.md section 2, frozen
GAINS_ONE = {"G_B": _TRAIN["gains"]["G_B"], "G_Rl": _TRAIN["gains"]["G_Rl"]}                           # the one-pass fits, reported beside


# ------------------------------------------------------------------------------------------------ A10: the primary reading, staged
def a10_contexts(sessions_in, out):
    """{sid: context}: the arm's session where A9-1 reads it, the measured pass alone otherwise (named); excluded sessions left out"""
    ctx, how = {}, {}
    actx, why = V4.arm_contexts(sessions_in, out)
    for i, s in enumerate(sessions_in):
        sid = f"S{i + 1}:{os.path.basename(os.path.normpath(s['a3']))}"
        if "excluded" in out["sessions"][sid]:
            how[sid] = "excluded: the session did not pass its start gate"
            continue
        if sid in actx:
            ctx[sid] = actx[sid]
            how[sid] = "the chain over the smoke and the measured pass (A9-1)"
        else:
            ctx[sid] = V2._context(s["a3"])
            how[sid] = f"the measured pass alone (A10-3: {why.get(sid)})"
    return ctx, how


def a10_read(ctx, staging):
    """the staged reading on A10's sessions, stages 7-9 (A4-8's form), as v4's arm_read reads the arm's"""
    log, rows = [], {sid: {} for sid in ctx}
    order = {sid: V2._order_from_records(c) for sid, c in ctx.items()}
    st = {}
    for sid, c in ctx.items():
        for nm in ("H_E", "Z"):
            rows[sid][nm] = V2._read(c, nm, sid, log)
        st[sid] = V2._a2_line(rows[sid], order[sid])
    V4._append(staging, {"stage": 7, "what": "A10's reading: A2's line per session through H_E and Z, written before any later hold's e is read",
                         "t": V2._now(), "sessions": st})
    log.append("stage 7 written: A10's A2 lines")
    st = {}
    for sid, c in ctx.items():
        for nm in ("L1", "S"):
            rows[sid][nm] = V2._read(c, nm, sid, log)
        st[sid] = V2._a4_line(rows[sid], order[sid])
    V4._append(staging, {"stage": 8, "what": "A10's reading: A4's line per session through L1 and S, written before any L2's e is read",
                         "t": V2._now(), "sessions": st})
    log.append("stage 8 written: A10's A4 lines")
    for sid, c in ctx.items():
        rows[sid]["L2"] = V2._read(c, "L2", sid, log)
    V4._append(staging, {"stage": 9, "what": "A10's reading: L2 read; every reading follows in the scorer's JSON", "t": V2._now(),
                         "L2": {sid: {"scored": r["L2"].get("scored"), "P_C": r["L2"].get("P_C"), "e_C": r["L2"].get("e_C")} for sid, r in rows.items()}})
    log.append("stage 9 written: A10's L2 read")
    return rows, log


def a10(sessions_in, out, staging):
    ctx, how = a10_contexts(sessions_in, out)
    res = {"label": A10_LABEL, "rule": "M11's amendment A10 (A10-1 to A10-3), 5e708747", "how_each_session_is_read": how}
    if not ctx:
        res["reads"] = "NOT SCORED: no session passed its start gate"
        return res
    rows, log = a10_read(ctx, staging)
    res["reading_order"] = log
    sess = {sid: V2._session_dict(c, {nm: rows[sid][nm] for nm in V1.NAMES_A3}) for sid, c in ctx.items()}
    res["sessions"] = {sid: {"holds": s["holds"], "order": s["order"]} for sid, s in sess.items()}
    try:
        res["readings"] = V2.decide_card_kind(sess, "aifoundry3")
        res["reads"] = "SCORED"
    except SystemExit as e:
        res["reads"] = f"NOT SCORED: the registered decision code refused ({str(e)[:300]})"
    return res


# ------------------------------------------------------------------------------------------------ E185's rules (E185.md section 6)
def _rms(v):
    return math.sqrt(sum(x * x for x in v) / len(v)) if v else None


def rule_pair(ex, ey, tau):
    d = _rms(ex) - _rms(ey)
    return {"verdict": "BETTER" if d <= -tau else "WORSE" if d >= tau else "NOT RESOLVED", "D_C": r4(d), "rms_x_C": r4(_rms(ex)), "rms_y_C": r4(_rms(ey))}


def rule_best(es, tau):
    r = {k: _rms(v) for k, v in es.items()}
    best = min(r, key=r.get)
    ties = sorted(k for k in r if k != best and r[k] - r[best] < tau)
    return {"verdict": best if not ties else "NOT SEPARATED (" + ", ".join(sorted([best] + ties)) + ")", "rms_C": {k: r4(v) for k, v in r.items()}}


def rule_cool(ds):
    n = len(ds)
    if n < COOL_MIN_N:
        return {"verdict": "NOT SCORED", "why": f"{n} big holds with a complete cool-down window (at least {COOL_MIN_N})", "n": n}
    m = sum(ds) / n
    sd = math.sqrt(sum((x - m) ** 2 for x in ds) / (n - 1))
    half = V1.DPG.f_ppf(0.95, 1, n - 1) ** 0.5 * sd / math.sqrt(n)
    lo, hi = m - half, m + half
    if (hi < 0 or lo > 0) and abs(m) >= 0.05:
        v = "THE SHAPE MISSES (cooler than the chain)" if m < 0 else "THE SHAPE MISSES (warmer than the chain)"
    elif lo >= -0.10 and hi <= 0.10:
        v = "THE SHAPE HOLDS"
    else:
        v = "NOT RESOLVED"
    return {"verdict": v, "n": n, "mean_d_C": r4(m), "ci95_C": [r4(lo), r4(hi)]}


def rail_coverage(paths, wins):
    """per hold: the readable rail rows a second over its anchor and plateau windows (E185.md section 6's rail clause)"""
    t, q = ARMS.rail_rows(paths)
    ok = np.isfinite(q)
    out = {}
    for nm, w in wins.items():
        a, b = w["anchor_end"], w["b"]
        na = int(np.sum(ok & (t >= a - 120.0) & (t < a)))
        npl = int(np.sum(ok & (t >= b - 300.0) & (t < b)))
        out[nm] = {"anchor_rows": na, "plateau_rows": npl, "ok": na >= MIN_RAIL_HZ * 120.0 and npl >= MIN_RAIL_HZ * 300.0}
    return out


def read_arms(sid, pdir, smoke, two_pass, gains):
    """every hold of the pass on one reading: R, P and e for the three arms, the cool-down misses, the rail share, scored flags"""
    marks = [json.loads(x) for x in open(os.path.join(pdir, "marks.jsonl")) if x.strip()]
    names = [m["name"] for m in marks if m.get("kind") == "hold_start"]
    S, why = ARMS.load(sid, pdir, smoke, names, two_pass=two_pass)
    if S is None:
        return None, why
    rows = ARMS.read_holds(S)
    paths = ([os.path.join(smoke, "telemetry.jsonl.gz")] if two_pass else []) + [os.path.join(pdir, "telemetry.jsonl.gz")]
    cov = rail_coverage(paths, S["wins"])
    out = {}
    for nm, h in rows.items():
        w = S["wins"][nm]
        P_B, P_Rl = gains["G_B"] * h["P_F_C"], gains["G_Rl"] * h["P_Rl1_C"]
        d = {"item": h["item"], "kind": KIND.get(h["item"]), "scored": bool(w.get("scored")), "rail_ok": cov[nm]["ok"],
             "rail_rows": cov[nm], "R_C": h["R_C"], "P_F_C": h["P_F_C"], "P_B_C": P_B, "P_Rl_C": P_Rl,
             "e_F_C": h["R_C"] - h["P_F_C"], "e_B_C": h["R_C"] - P_B, "e_Rl_C": h["R_C"] - P_Rl, "rail_share": h["rail_share"]}
        if h.get("cool_window_s"):
            d["cool"] = {"e_F_C": h["cool_R_C"] - h["cool_P_F_C"], "e_B_C": h["cool_R_C"] - gains["G_B"] * h["cool_P_F_C"],
                         "e_Rl_C": h["cool_R_C"] - gains["G_Rl"] * h["cool_P_Rl1_C"]}
        else:
            d["cool"] = None
            d["cool_why"] = h.get("cool_why")
        out[nm] = d
    return out, None


def rules(holds):
    use = {nm: h for nm, h in holds.items() if h["scored"] and h["rail_ok"]}
    n = len(use)
    kinds = {h["kind"] for h in use.values()}
    res = {"n_scored_by_all_three": n, "holds_read": sorted(use), "not_read": {nm: ("not scored" if not h["scored"] else "the rail rows miss a window")
                                                                               for nm, h in holds.items() if nm not in use}}
    if n < 4 or "H" not in kinds or "S" not in kinds:
        why = f"{n} holds scored by all three arms" + ("" if n >= 4 else " (at least 4)") + \
              ("" if "H" in kinds else "; no fp32.randn hold") + ("" if "S" in kinds else "; no int8.neg_ones hold")
        for k in ("E185-RF", "E185-BF", "E185-RB", "E185-BEST"):
            res[k] = {"verdict": "NOT SCORED", "why": why}
    else:
        tau = SIGMA_C / math.sqrt(n)
        e = {a: [use[nm][f"e_{a}_C"] for nm in sorted(use)] for a in ("F", "B", "Rl")}
        res["tau_C"] = r4(tau)
        res["E185-RF"] = rule_pair(e["Rl"], e["F"], tau)
        res["E185-BF"] = rule_pair(e["B"], e["F"], tau)
        res["E185-RB"] = rule_pair(e["Rl"], e["B"], tau)
        res["E185-BEST"] = rule_best(e, tau)
        res["per_kind_mean_miss_C"] = {k: {a: r4(sum(use[nm][f"e_{a}_C"] for nm in use if use[nm]["kind"] == k) /
                                               max(1, sum(1 for nm in use if use[nm]["kind"] == k))) for a in ("F", "B", "Rl")}
                                       for k in sorted(kinds)}
    big = {nm: h for nm, h in holds.items() if h["scored"] and h["kind"] in ("H", "L") and h["cool"]}
    res["E185-C"] = {a: rule_cool([h["cool"][f"e_{a}_C"] - h[f"e_{a}_C"] for h in big.values()]) for a in ("F", "B", "Rl")}
    res["E185-C"]["holds"] = sorted(big)
    return res


def e185(sessions_in, out, e185_dir):
    s = [x for x in sessions_in if os.path.normpath(x["a3"]) == os.path.normpath(e185_dir)]
    res = {"label": "E185.md section 6 (98fe28b7): the three arms on A10's reading, the frozen two-pass gains", "gains_frozen": GAINS}
    if not s:
        res["reads"] = "NOT SCORED: --e185 names no --a3 pass"
        return res
    s = s[0]
    sid = [k for k, v in out["sessions"].items() if v.get("pass_dir") == os.path.basename(os.path.normpath(e185_dir))][-1]
    so = out["sessions"][sid]
    if "excluded" in so:
        res["reads"] = "NOT SCORED: the pass did not pass its start gate"
        return res
    two = bool(s.get("smoke"))
    holds, why = (read_arms("E185", s["a3"], s["smoke"], True, GAINS) if two else (None, "no smoke pass named"))
    res["reading"] = "the chain over the smoke and the measured pass (A10)"
    if holds is None:
        res["reading"] = f"the measured pass alone (A10-3: {why})"
        holds, _ = read_arms("E185", s["a3"], None, False, GAINS)
    res["session"] = sid
    res["holds"] = {nm: {k: (r4(v) if isinstance(v, float) else v) for k, v in h.items() if k != "cool"} |
                    {"cool": None if not h["cool"] else {k: r4(v) for k, v in h["cool"].items()}} for nm, h in holds.items()}
    res["rules"] = rules(holds)
    he2 = holds.get("H_E2")
    res["H_E2_abs_e_over_R"] = r4(abs(he2["e_F_C"]) / he2["R_C"]) if he2 and he2["scored"] and he2["R_C"] else None
    one, _ = read_arms("E185", s["a3"], None, False, GAINS_ONE)
    res["one_pass_reported"] = {"label": ALONE_LABEL + "; the one-pass gains", "gains": GAINS_ONE,
                                "rules": rules(one) if one else None}
    first = so.get("first_launch_ms")
    prec = {}
    for k, c in (("A10", A10_COMMIT), ("E185", E185_COMMIT)):
        rc, t = V1.git("log", "-1", "--format=%ct", c)
        rca, _ = V1.git("merge-base", "--is-ancestor", c, "HEAD")
        prec[k] = {"commit": c, "ancestor_of_HEAD": rca == 0,
                   "precedes_first_launch": rc == 0 and rca == 0 and first is not None and int(t) * 1000 < first}
    res["precedence"] = prec
    res["blind"] = all(v["precedes_first_launch"] for v in prec.values()) and bool(so.get("precedence", {}).get("blind"))
    res["reads"] = "SCORED"
    return res


# ------------------------------------------------------------------------------------------------ the score
def score(sessions_in, lines_path, e185_dir=None):
    out = V4.score(sessions_in, lines_path)                      # v4 writes and renames its lines file (stages 1-6)
    out["scorer"] = "tools/claims-v3/m11/score_m11_v5.py"
    out["imports_unchanged"] = ["tools/claims-v3/m11/score_m11_v4.py"] + out.get("imports_unchanged", []) + ["tools/claims-v3/e185/arms_e185.py"]
    out["lists_checked"] = dict(out.get("lists_checked", {}), **_V5_COUNTS)
    staging = lines_path + ".v5.staging"
    V4._remove(staging)
    try:
        with open(lines_path) as f, open(staging, "w") as g:
            g.write(f.read())
        out["A10"] = a10(sessions_in, out, staging)
        out["measured_pass_alone_reported (A10)"] = {"label": ALONE_LABEL, "aifoundry3": out.get("aifoundry3")}
        if e185_dir:
            out["E185"] = e185(sessions_in, out, e185_dir)
    except BaseException:
        V4._remove(staging)
        raise
    os.replace(staging, lines_path)
    out["lines_staged_as"] = "v4's stages 1-6, then A10's 7-9, renamed to the lines file only after the whole score succeeded"
    return out


def md_summary(res):
    L = [V4.md_summary(res).rstrip("\n").replace("score_m11_v4.py", "score_m11_v5.py")]
    a = res.get("A10", {})
    L.append(f"- A10's reading ({a.get('reads')}): " + "; ".join(f"{k}: {v}" for k, v in (a.get("how_each_session_is_read") or {}).items()))
    rd = a.get("readings") or {}
    if rd:
        L.append(f"  - HM-LG {(rd.get('HM_LG') or {}).get('verdict')}; A1-4 {(rd.get('A1_4') or {}).get('outcome')}; HM-E144 "
                 f"{(rd.get('HM_E144') or {}).get('reading')}; HM-CAL {(rd.get('HM_CAL') or {}).get('verdict')}; HM-CAL-I8 {(rd.get('HM_CAL_I8') or {}).get('verdict')}")
    e = res.get("E185")
    if e:
        L.append(f"- E185's rules ({e.get('reads')}; {e.get('reading')}; blind {e.get('blind')}):")
        r = e.get("rules") or {}
        for k in ("E185-RF", "E185-BF", "E185-RB", "E185-BEST"):
            L.append(f"  - {k}: {(r.get(k) or {}).get('verdict')} {json.dumps({x: y for x, y in (r.get(k) or {}).items() if x != 'verdict'})}")
        for arm in ("F", "B", "Rl"):
            L.append(f"  - E185-C on {arm}: {json.dumps((r.get('E185-C') or {}).get(arm))}")
        for nm, h in (e.get("holds") or {}).items():
            L.append(f"  - {nm} {h.get('item')}: R {h.get('R_C')}, e F {h.get('e_F_C')} / B {h.get('e_B_C')} / Rl {h.get('e_Rl_C')}; "
                     f"cool {h.get('cool')}; rail share {h.get('rail_share')}; scored {h.get('scored')}, rail {h.get('rail_ok')}")
    return "\n".join(L) + "\n"


# ------------------------------------------------------------------------------------------------ self-test (E181's committed data)
def self_test(workdir):
    if os.path.exists(workdir):
        raise SystemExit(f"--workdir {workdir} exists: name a new one")
    os.makedirs(workdir)
    T = {"lists_checked": dict(_V5_COUNTS), "cases": {}}
    probs = []

    def case(name, ok, got):
        T["cases"][name] = {"pass": bool(ok), "got": got}
        if not ok:
            probs.append(f"{name}: {got}")

    D = os.path.join(TREE, "docs", "reports", "data")
    e176 = os.path.join(D, "2026-11-05-e176-m11-holds-aifoundry3", "aifoundry3", "e176", "p17620")
    e181 = os.path.join(D, "2026-11-06-e181-m11-session2-aifoundry3", "aifoundry3", "e181", "p18120")
    sm181 = os.path.join(D, "2026-11-06-e181-m11-session2-aifoundry3", "aifoundry3", "e181-smoke", "p18101")
    logs181 = os.path.join(D, "2026-11-06-e181-m11-session2-aifoundry3", "logs")
    com = json.load(open(os.path.join(D, "2026-11-06-e181-m11-session2-aifoundry3", "scored-m11.json")))
    sess = [{"a3": e176, "smoke": None, "host": None}, {"a3": e181, "smoke": sm181, "host": logs181}]
    res = score(sess, os.path.join(workdir, "lines-e181.jsonl"), e185_dir=e181)
    canon = lambda x: json.loads(json.dumps(x, sort_keys=True, default=str))  # noqa: E731
    # V1: v4's registered readings unchanged (E181's committed score)
    case("V1 v4's registered readings on E176 + E181 equal E181's committed score (the aifoundry3 block and each session's holds)",
         canon(res["aifoundry3"]) == canon(com["aifoundry3"]) and
         all(canon(res["sessions"][k]["holds"]) == canon(com["sessions"][k]["holds"]) for k in com["sessions"] if "holds" in com["sessions"][k]),
         {"aifoundry3_same": canon(res["aifoundry3"]) == canon(com["aifoundry3"])})
    # V2: A10's primary equals the committed A9 arm's readings (every session's arm read, so the mixed path is the arm)
    arm = com["arm_A9"]["all_readings_on_the_arm"]
    case("V2 A10's primary readings on E181 equal the committed A9 arm's readings, decision by decision (A10-3: E181 read on the arm)",
         res["A10"]["reads"] == "SCORED" and canon(res["A10"]["readings"]) == canon(arm),
         {"reads": res["A10"]["reads"], "how": res["A10"]["how_each_session_is_read"],
          "HM_CAL": (res["A10"].get("readings") or {}).get("HM_CAL", {}).get("verdict"), "committed_HM_CAL": arm.get("HM_CAL", {}).get("verdict")})
    # V3: the lines file holds stages 1-9 in order, no staging file left
    st = [json.loads(x).get("stage") for x in open(os.path.join(workdir, "lines-e181.jsonl")) if x.strip()]
    case("V3 the lines file holds v4's stages 1-6 then A10's 7-9, and no staging file is left",
         st == [1, 2, 3, 4, 5, 6, 7, 8, 9] and not any(x.endswith(".staging") for x in os.listdir(workdir)), {"stages": st})
    # V4: E185's readers on E181's five holds reproduce the registration's two-pass held-out misses
    e1 = json.load(open(os.path.join(E185D, "arms-e185-e181.json")))["two_pass"]["held_out"]["misses"]["E181"]
    hh = res["E185"]["holds"]
    dmax = max(abs(hh[nm][f"e_{a}_C"] - e1[nm][f"e_{a}_C"]) for nm in e1 for a in ("F", "B", "Rl"))
    case("V4 E185's arms on E181's five holds (A10's reading, frozen gains) give arms-e185-e181.json's two-pass held-out misses within 1e-4 C",
         dmax <= 1.0e-4, {"max_diff_C": dmax})
    rr = res["E185"]["rules"]
    case("V5 E185's rules read on E181 (a stand-in session: H_E and S present, n 5): rms F / B / Rl as the registration's held-out "
         "0.2963 / 0.2312 / 0.1978 C", rr["n_scored_by_all_three"] == 5 and rr["E185-BEST"]["rms_C"] == {"F": 0.2963, "B": 0.2312, "Rl": 0.1978},
         {"BEST": rr["E185-BEST"], "RF": rr["E185-RF"]["verdict"], "RB": rr["E185-RB"]["verdict"], "BF": rr["E185-BF"]["verdict"],
          "C_F": rr["E185-C"]["F"]})
    case("V6 E181's E185 reading is labelled post hoc for A10 and E185's registration (both commits after E181's first launch)",
         res["E185"]["blind"] is False and not res["E185"]["precedence"]["A10"]["precedes_first_launch"], res["E185"]["precedence"])
    # V7: the rules on synthetic holds with known answers
    def syn(spec):
        out = {}
        for i, (nm, item, P_F, ratio_rl, truth, cool) in enumerate(spec):
            P_B, P_Rl = GAINS["G_B"] * P_F, ratio_rl * P_F
            R = {"F": P_F, "B": P_B, "Rl": P_Rl}[truth] + (0.01 if i % 2 else -0.01)
            h = {"item": item, "kind": KIND[item], "scored": True, "rail_ok": True, "R_C": R, "P_F_C": P_F, "P_B_C": P_B, "P_Rl_C": P_Rl,
                 "e_F_C": R - P_F, "e_B_C": R - P_B, "e_Rl_C": R - P_Rl, "rail_share": None, "cool": None}
            if cool is not None:
                h["cool"] = {f"e_{a}_C": h[f"e_{a}_C"] + cool + (0.002 * i) for a in ("F", "B", "Rl")}
            out[nm] = h
        return out
    base = [("H_E", "fp32.randn", 14.4, 1.0011, None, -0.10), ("L1", "int8.full", 10.2, 1.040, None, -0.10),
            ("L2", "int8.full", 10.3, 1.040, None, -0.10), ("H_E2", "fp32.randn", 14.0, 1.0011, None, -0.10),
            ("S", "int8.neg_ones", 3.9, 1.074, None, None), ("S2", "int8.neg_ones", 2.0, 1.074, None, None)]
    for truth in ("F", "B", "Rl"):
        r = rules(syn([(a, b, c, d, truth, f) for a, b, c, d, _, f in base]))
        want = {"F": ("WORSE", "WORSE"), "B": ("BETTER", None), "Rl": (None, "BETTER")}[truth]
        ok = r["E185-BEST"]["verdict"] == truth and (want[0] is None or r["E185-BF"]["verdict"] == want[0]) and \
            (want[1] is None or r["E185-RF"]["verdict"] == want[1])
        case(f"V7 synthetic holds whose R is arm {truth}'s P (+/-0.01 C): E185-BEST reads {truth}", ok,
             {"BEST": r["E185-BEST"], "RF": r["E185-RF"]["verdict"], "BF": r["E185-BF"]["verdict"], "RB": r["E185-RB"]["verdict"]})
    r = rules(syn([(a, b, c, d, "F", f) for a, b, c, d, _, f in base]))
    case("V8 a cool-down 0.10 C under the plateau on four big holds: E185-C reads THE SHAPE MISSES (cooler) on F",
         r["E185-C"]["F"]["verdict"] == "THE SHAPE MISSES (cooler than the chain)", r["E185-C"]["F"])
    r = rules(syn([(a, b, c, d, "F", (0.0 if f is not None else None)) for a, b, c, d, _, f in base]))
    case("V9 a cool-down equal to the plateau's miss: E185-C reads THE SHAPE HOLDS on F", r["E185-C"]["F"]["verdict"] == "THE SHAPE HOLDS",
         r["E185-C"]["F"])
    r = rules(syn([x for x in [(a, b, c, d, "F", f) for a, b, c, d, _, f in base] if x[1] != "int8.neg_ones"]))
    case("V10 no int8.neg_ones hold scored: every arm rule NOT SCORED", r["E185-BEST"]["verdict"] == "NOT SCORED", r["E185-BEST"])
    sy = syn([(a, b, c, d, "F", f) for a, b, c, d, _, f in base])
    sy["S"]["rail_ok"] = sy["S2"]["rail_ok"] = False
    r = rules(sy)
    case("V11 rail rows missing on both int8.neg_ones holds: those holds leave the three-arm rules, which then read NOT SCORED",
         r["E185-BEST"]["verdict"] == "NOT SCORED" and sorted(r["not_read"]) == ["S", "S2"], {"not_read": r["not_read"], "BEST": r["E185-BEST"]})
    # V12: A10-3: a session with no smoke named is read on the measured pass alone, named
    res2 = score([{"a3": e176, "smoke": None, "host": None}, {"a3": e181, "smoke": None, "host": None}], os.path.join(workdir, "lines-alone.jsonl"))
    how = res2["A10"]["how_each_session_is_read"]
    alone = canon((res2["A10"].get("readings") or {}).get("HM_LG")) == canon(com["aifoundry3"].get("HM_LG"))
    case("V12 no smoke named: A10-3 reads E181 on the measured pass alone, named, and its HM-LG is the registered one",
         "the measured pass alone" in how.get("S2:p18120", "") and alone, {"how": how, "HM_LG_same_as_registered": alone})
    T["pass"] = not probs
    T["problems"] = probs
    T["label"] = "checks of the code on E181's committed data and on synthetic holds, never a reading of a session"
    return T


def _parse(args):
    sessions = V4._parse(args)
    e = args[args.index("--e185") + 1] if "--e185" in args else None
    return sessions, e


def main():
    args = sys.argv[1:]
    jp = args[args.index("--json") + 1] if "--json" in args else None
    mp = args[args.index("--md") + 1] if "--md" in args else None
    if "--self-test" in args:
        if "--workdir" not in args:
            raise SystemExit("M11 scorer v5: --self-test needs --workdir <a new scratch dir>")
        T = self_test(args[args.index("--workdir") + 1])
        print("M11 scorer v5 self-test: lists " + ", ".join(f"{k} {v}" for k, v in T["lists_checked"].items()))
        for k, x in T["cases"].items():
            print(f"  {k:130s} {'PASS' if x['pass'] else 'FAIL'}  {json.dumps(x['got'], default=str)[:300]}")
        print(f"SELF-TEST {'PASS' if T['pass'] else 'FAIL: ' + '; '.join(T['problems'])} ({sum(1 for x in T['cases'].values() if x['pass'])} of {len(T['cases'])})")
        if jp:
            json.dump(T, open(jp, "w"), indent=1, sort_keys=True, default=str)
        sys.exit(0 if T["pass"] else 1)
    if not args or args[0] != "score":
        raise SystemExit(__doc__)
    sessions, e = _parse(args)
    if not sessions:
        raise SystemExit("M11 scorer v5: name at least one aifoundry3 pass with --a3")
    if "--lines" not in args:
        raise SystemExit("M11 scorer v5: name the lines file with --lines")
    res = score(sessions, args[args.index("--lines") + 1], e)
    if jp:
        json.dump(res, open(jp, "w"), indent=1, sort_keys=True, default=str)
    if mp:
        open(mp, "w").write(md_summary(res))
    print(md_summary(res))


if __name__ == "__main__":
    main()
