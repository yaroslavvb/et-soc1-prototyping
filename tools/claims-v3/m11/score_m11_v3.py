#!/usr/bin/env python3
"""E181's kit round (M11's session 2, Fri 6 Nov 2026): M11's scorer v3 for heat over minutes (tools/claims-v3/m11/REGISTRATION.md section 13
step 1, as amended by A1-A8), desk only (the Intel). score_m11.py (lab 03582d2f) and score_m11_v2.py (lab ebdbb35c) stay as committed: v3
imports v2 unchanged (v2 imports v1 unchanged), and every reading and decision v2 makes is v3's. What v3 adds, from M11's amendments after
v2 (A6 95c75047, A7 65a93fbb, A8 80b92990):

  P   the blind precedence counts A6, A7 and A8 beside the registration and A1-A5 (v2's precedence(), with three more commits);
  G   each session's start_gate mark read whole (A6-2 with A8-4): R0's room and its 53.9 C line, F0, the residue, A8's frozen 0.414 C, the
      residue less it and its 0.50 C line, and `passed`. v3 re-computes the gate from the mark's own numbers and REFUSES (exit 1) when a
      mark's `passed` disagrees with them, or when an A6-form mark carries lines other than A6-2's and A8-4's. A mark written before A6 (E176's
      kit: line 53.0 C, no F0) is read as that kit's own G0 and named so. An excluded session carries its mark's own reason;
  F   FL5(c), the footing law's first blind check, as A7-1 and the footing law's dated note 1 (N1) fix it (A6-5), on every session that
      passed its start gate, from its rests after its holds (R1-R5; rule F: from 20 s after each rest's start to its end, minion clock 600 MHz,
      a clean 34-code record): PRIMARY, per whole firmware degree (temp_c.minshire[0]) inside FL1's aifoundry3 band, 52-66 C, the degrees
      with at least 100 samples, a straight line through the per-degree mean board W weighted by the samples, against the same line through
      FL1's quadratic at the same degrees and weights: PASS if the slopes differ by at most 0.02 W/C, FAIL outside, NOT SCORED with fewer
      than 300 samples (or 2 degrees) in the band. BESIDE, on the 34 codes: the same samples in E97's 0.5 C bins of the 34-sensor mean (at
      least 20 samples each; a bin's point its mean T and mean W), the same weighted line, against E97's law by the same estimator at the
      same bins and weights. And beside, the primary on the degrees 52-58 alone (the range of N1's dry run, item 5). Every FL5(c) reading is
      reported, never a gate of any verdict.

It checks SHA256SUMS-a6, -a7, -a8 and the footing law's SHA256SUMS (bare names, beside the files) before it reads anything; v2 and v1 check
theirs on import.

    /usr/bin/python3 -B tools/claims-v3/m11/score_m11_v3.py score --a3 <pass dir> [--a3 <pass dir>] --lines <out.jsonl> [--json <out>] [--md <out>]
    /usr/bin/python3 -B tools/claims-v3/m11/score_m11_v3.py --self-test --workdir <a new scratch dir> [--json <out>]
Python 3.9 with numpy 1.26 (the Intel's /usr/bin/python3; numpy in the user site, so never -I).
SPDX-License-Identifier: Apache-2.0
"""
import sys

sys.dont_write_bytecode = True
import gzip  # noqa: E402
import hashlib  # noqa: E402
import json  # noqa: E402
import math  # noqa: E402
import os  # noqa: E402
import random  # noqa: E402
import shutil  # noqa: E402
import time  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
TREE = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
FOOT = os.path.join(TREE, "tools", "claims-v3", "footing-law")
V3_LISTS = ("SHA256SUMS-a6", "SHA256SUMS-a7", "SHA256SUMS-a8")
NEW_COMMITS = {"A6": "95c75047", "A7": "65a93fbb", "A8": "80b92990"}
ROOM_MAX_C, RESIDUE_PRED_C, RESIDUE_LINE_C, FLOOR_MAX_C = 53.9, 0.414, 0.50, 53.9     # A6-1, A6-2, A8-4 (run_e181.py carries the same)
EPS_C = 1e-9                                                                          # "at or under" through floating point, as run_e181.py
FL5C_BAND = (52, 66)                 # FL1's aifoundry3 band (footing_law.CARDS)
FL5C_DRY = (52, 58)                  # N1's dry run on E97's rests (footing_law_note1.py item 5)
FL5C_DEG_MIN, FL5C_BIN_MIN, FL5C_MIN_SAMPLES, FL5C_LINE = 100, 20, 300, 0.02
RULE_F_S = 20.0
RESTS_AFTER_HOLDS = ("R1", "R2", "R3", "R4", "R5")
G_TS, H_TS, CAL5 = 57400, 249400, 4096                                               # E97's code_to_c


def _sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def _check_lists():
    counts, bad = {}, []
    for name in V3_LISTS:
        p = os.path.join(HERE, name)
        n = 0
        for line in (open(p) if os.path.exists(p) else []):
            parts = line.split()
            if len(parts) != 2:
                continue
            n += 1
            # A8's list names repo paths (as A5's); A6's and A7's name paths beside the list (shasum -c run in this directory)
            q = os.path.join(TREE, parts[1]) if parts[1].startswith(("tools/", "docs/")) else os.path.normpath(os.path.join(HERE, parts[1]))
            if not os.path.exists(q) or _sha(q) != parts[0]:
                bad.append(f"{name}: {parts[1]} differs")
        if not os.path.exists(p):
            bad.append(f"{name}: missing")
        counts[name] = n
    for name in ("SHA256SUMS", "SHA256SUMS-note1"):                                  # the footing law's lists: bare names, beside the files
        p = os.path.join(FOOT, name)
        n = 0
        for line in (open(p) if os.path.exists(p) else []):
            parts = line.split()
            if len(parts) != 2:
                continue
            n += 1
            q = os.path.join(FOOT, parts[1])
            if not os.path.exists(q) or _sha(q) != parts[0]:
                bad.append(f"footing-law/{name}: {parts[1]} differs")
        if not os.path.exists(p):
            bad.append(f"footing-law/{name}: missing")
        counts["footing-law/" + name] = n
    return counts, bad


_V3_COUNTS, _V3_BAD = _check_lists()
if _V3_BAD:
    raise SystemExit("M11 scorer v3 REFUSED: a registered file differs:\n  " + "\n  ".join(_V3_BAD))

sys.path.insert(0, HERE)
import score_m11_v2 as V2  # noqa: E402  (ebdbb35c, unchanged: it checks its lists and imports score_m11.py unchanged)

V1 = V2.V1
np = V2.np
r4 = V2.r4
REG_COMMITS = dict(V2.REG_COMMITS, **NEW_COMMITS)
_FL = json.load(open(os.path.join(FOOT, "footing-law.json")))
FL1_A3 = [float(x) for x in _FL["laws"]["aifoundry3"]["quad_w"]]
E97_LAW = (0.006175439291277969, -0.3665903970069978, 25.998917638611008)        # heat_q138t.py line 167; footing_law.E97


def code_to_c(n):
    return (G_TS + H_TS * n / CAL5 - H_TS / 2) / 1000.0


# ------------------------------------------------------------------------------------------------ P: the precedence, with A6-A8
def precedence(first_launch_ms):
    out = {}
    for k, c in REG_COMMITS.items():
        rc, t = V1.git("log", "-1", "--format=%ct", c)
        rca, _ = V1.git("merge-base", "--is-ancestor", c, "HEAD")
        ok = rc == 0 and rca == 0 and first_launch_ms is not None and int(t) * 1000 < first_launch_ms
        out[k] = {"commit": c, "commit_epoch_s": int(t) if rc == 0 and t else None, "ancestor_of_HEAD": rca == 0, "precedes_first_launch": ok}
    out["blind"] = all(v["precedes_first_launch"] for v in out.values() if isinstance(v, dict))
    return out


# ------------------------------------------------------------------------------------------------ G: the start gate, read whole
def gate_reading(m):
    """the start_gate mark's own numbers, the gate they give, and whether `passed` agrees (A6-2 with A8-4; or the pre-A6 G0)"""
    if not m:
        return {"form": "none", "passed": None, "recomputed": False, "agrees": False, "why": "no start_gate mark"}
    if "residue_pred_c" not in m:                                                      # E176's kit: G0 as registered then
        room, line = m.get("room_c"), m.get("max_c")
        rec = room is not None and line is not None and room <= line + EPS_C
        return {"form": "pre-A6 G0 (that kit's own line)", "room_c": room, "max_c": line, "passed": m.get("passed"), "recomputed": rec,
                "agrees": bool(m.get("passed")) == rec, "why": m.get("why")}
    room, f0 = m.get("room_c"), m.get("floor_c")
    lines_ok = (m.get("max_c") == ROOM_MAX_C and m.get("residue_pred_c") == RESIDUE_PRED_C and m.get("residue_line_c") == RESIDUE_LINE_C)
    resid = (room - f0) if (room is not None and f0 is not None) else None
    excess = (resid - RESIDUE_PRED_C) if resid is not None else None
    rec = room is not None and room <= ROOM_MAX_C + EPS_C and excess is not None and excess <= RESIDUE_LINE_C + EPS_C
    return {"form": "A6-2 with A8-4", "room_c": room, "max_c": m.get("max_c"), "floor_c": f0, "residue_c": resid,
            "residue_pred_c": m.get("residue_pred_c"), "residue_excess_c": excess, "residue_line_c": m.get("residue_line_c"),
            "lines_as_registered": lines_ok, "passed": m.get("passed"), "recomputed": rec,
            "agrees": lines_ok and bool(m.get("passed")) == rec and (resid is None or abs((m.get("residue_c") or 0.0) - resid) < 1e-9),
            "why": m.get("why")}


# ------------------------------------------------------------------------------------------------ F: FL5(c), both coordinates
def fl5c_samples(pass_dir, rest_names=RESTS_AFTER_HOLDS):
    """rule F's samples of the pass's rests after its holds: (rest names used, firmware degrees, 34-sensor means, board W)"""
    marks = [json.loads(x) for x in open(os.path.join(pass_dir, "marks.jsonl")) if x.strip().startswith("{")]
    rests = [m for m in marks if m.get("kind") == "rest" and m.get("name") in rest_names]
    fw, m34, W = [], [], []
    p = os.path.join(pass_dir, "telemetry.jsonl.gz")
    op = gzip.open if os.path.exists(p) else open
    p = p if os.path.exists(p) else os.path.join(pass_dir, "telemetry.jsonl")
    with op(p, "rt") as f:
        for line in f:
            line = line.strip()
            if not (line.startswith("{") and line.endswith("}")):
                continue
            try:
                s = json.loads(line)
            except ValueError:
                continue
            t = s.get("t_ms")
            if t is None or (s.get("mhz") or {}).get("minion") != 600:
                continue
            if not any(r["t_start_ms"] + RULE_F_S * 1000 <= t < r["t_end_ms"] for r in rests):
                continue
            pv = s.get("pvt") or {}
            cs = pv.get("c") or []
            if pv.get("st") != 0 or pv.get("f") or len(cs) != 34:
                continue
            fw.append(float(s["temp_c"]["minshire"][0]))
            m34.append(sum(code_to_c(c) for c in cs) / 34.0)
            W.append(float(s["board_w"]))
    return [r.get("name") for r in rests], fw, m34, W


def _wline(Ts, Ws, ns):
    n = [float(x) for x in ns]
    sn = sum(n)
    mx = sum(a * b for a, b in zip(n, Ts)) / sn
    my = sum(a * b for a, b in zip(n, Ws)) / sn
    sxx = sum(a * (t - mx) ** 2 for a, t in zip(n, Ts))
    return (sum(a * (t - mx) * (w - my) for a, t, w in zip(n, Ts, Ws)) / sxx if sxx > 0 else float("nan")), mx


def _quad(q, T):
    return q[0] * T * T + q[1] * T + q[2]


def fl5c_read(fw, m34, W, band=FL5C_BAND):
    """FL5(c) as N1 fixes it: the primary on whole firmware degrees against FL1, and the 34-code reading beside against E97's law"""
    lo, hi = band
    per = {}
    for t, w in zip(fw, W):
        ti = int(round(t))
        if lo <= ti <= hi:
            a = per.setdefault(ti, [0.0, 0])
            a[0] += w
            a[1] += 1
    used = sorted(t for t, v in per.items() if v[1] >= FL5C_DEG_MIN)
    n_used = sum(per[t][1] for t in used)
    out = {"band_c": [lo, hi], "degrees": used, "samples_by_degree": [per[t][1] for t in used], "samples": n_used,
           "line_w_per_c": FL5C_LINE, "min_samples": FL5C_MIN_SAMPLES}
    if len(used) < 2 or n_used < FL5C_MIN_SAMPLES:
        out.update(verdict="NOT SCORED", why=f"{n_used} samples in {len(used)} degree(s) of the band with at least {FL5C_DEG_MIN} each")
        return out
    Ws = [per[t][0] / per[t][1] for t in used]
    ns = [per[t][1] for t in used]
    k_obs, Tw = _wline(used, Ws, ns)
    k_law, _ = _wline(used, [_quad(FL1_A3, t) for t in used], ns)
    d = k_obs - k_law
    out.update(slope_rests_w_per_c=k_obs, slope_FL1_same_estimator=k_law, diff_w_per_c=d, weighted_mean_T_fw=Tw,
               verdict="PASS" if abs(d) <= FL5C_LINE else "FAIL")
    sel = set(used)
    xs = [m for t, m in zip(fw, m34) if int(round(t)) in sel]
    ys = [w for t, w in zip(fw, W) if int(round(t)) in sel]
    bins = {}
    for x, y in zip(xs, ys):
        k = math.floor(x / 0.5)
        a = bins.setdefault(k, [0.0, 0.0, 0])
        a[0] += x
        a[1] += y
        a[2] += 1
    pts = sorted((v[0] / v[2], v[1] / v[2], v[2]) for v in bins.values() if v[2] >= FL5C_BIN_MIN)
    if len(pts) >= 2:
        k34, T34 = _wline([p[0] for p in pts], [p[1] for p in pts], [p[2] for p in pts])
        k97, _ = _wline([p[0] for p in pts], [_quad(E97_LAW, p[0]) for p in pts], [p[2] for p in pts])
        out["beside_34_codes"] = {"bins": len(pts), "samples": sum(p[2] for p in pts), "slope_rests_w_per_c": k34,
                                  "slope_E97_same_estimator": k97, "diff_w_per_c": k34 - k97, "weighted_mean_T_34": T34,
                                  "reads": "PASS" if abs(k34 - k97) <= FL5C_LINE else "FAIL", "note": "reported beside, never a gate"}
    else:
        out["beside_34_codes"] = {"bins": len(pts), "reads": "NOT SCORED"}
    return out


def fl5c(pass_dir):
    names, fw, m34, W = fl5c_samples(pass_dir)
    o = {"rests": names, "rule": "F: from 20 s after each rest's start to its end, 600 MHz, a clean 34-code record",
         "primary": fl5c_read(fw, m34, W, FL5C_BAND), "dry_run_degrees_52_58": fl5c_read(fw, m34, W, FL5C_DRY),
         "note": "FL5(c) (A6-5, A7-1, the footing law's N1): reported, never a gate of any verdict"}
    return o


# ------------------------------------------------------------------------------------------------ the score
def score(a3_dirs, lines_path):
    out = V2.score(a3_dirs, lines_path)
    out["scorer"] = "tools/claims-v3/m11/score_m11_v3.py"
    out["imports_unchanged"] = ["tools/claims-v3/m11/score_m11_v2.py", "tools/claims-v3/m11/score_m11.py"]
    out["lists_checked"] = dict(out.get("lists_checked", {}), **_V3_COUNTS)
    out["registration_commits"] = REG_COMMITS
    problems = []
    for sid, s in out["sessions"].items():
        s["precedence"] = precedence(s["first_launch_ms"])
        g = gate_reading(s["start_gate"])
        s["start_gate_reading"] = g
        if not g["agrees"] and g["form"] != "none":
            problems.append(f"{sid}: the start_gate mark's passed={g['passed']} disagrees with its own numbers ({g})")
        if "excluded" in s:
            s["excluded"] = f"the start gate did not pass ({g['form']}): {g.get('why')}"
        else:
            s["FL5c"] = fl5c(os.path.join(a3_dirs[int(sid.split(':')[0][1:]) - 1]))
    if problems:
        raise SystemExit("M11 scorer v3 REFUSED: " + "; ".join(problems))
    use = {sid: s for sid, s in out["sessions"].items() if "excluded" not in s}
    out["blind"] = all(s["precedence"]["blind"] for s in use.values()) if use else None
    out["label"] = ("blind: every registration and amendment commit (A1-A8) precedes every session's first launch record" if out["blind"]
                    else "post hoc: a registration or amendment commit does not precede a session's first launch record")
    return out


def md_summary(res):
    L = [V2.md_summary(res).rstrip("\n").replace("score_m11_v2.py", "score_m11_v3.py")]
    for sid, s in res.get("sessions", {}).items():
        g = s.get("start_gate_reading", {})
        L.append(f"- {sid} start gate ({g.get('form')}): passed {g.get('passed')}; room {r4(g.get('room_c'))} C, F0 {r4(g.get('floor_c'))} C, "
                 f"residue {r4(g.get('residue_c'))} C, less {g.get('residue_pred_c')} = {r4(g.get('residue_excess_c'))} C"
                 + (f"; excluded: {s['excluded']}" if "excluded" in s else ""))
        f = s.get("FL5c")
        if f:
            p, b = f["primary"], f["primary"].get("beside_34_codes", {})
            L.append(f"- {sid} FL5(c), reported: {p['verdict']} (rests {r4(p.get('slope_rests_w_per_c'))} against FL1 "
                     f"{r4(p.get('slope_FL1_same_estimator'))} W/C, diff {r4(p.get('diff_w_per_c'))}, {p['samples']} samples at degrees "
                     f"{p['degrees'][:1] + p['degrees'][-1:] if p['degrees'] else []}); beside on the 34 codes: {b.get('reads')} (diff "
                     f"{r4(b.get('diff_w_per_c'))}); degrees 52-58: {f['dry_run_degrees_52_58']['verdict']} "
                     f"(diff {r4(f['dry_run_degrees_52_58'].get('diff_w_per_c'))})")
    return "\n".join(L) + "\n"


# ------------------------------------------------------------------------------------------------ self-test
def _rewrite_gate(pdir, room=None, floor=None, passed_override=None, pre_a6=False):
    """replace the pass's start_gate mark by an A6-form one (or a pre-A6 one) from the room mark's own reading"""
    mp = os.path.join(pdir, "marks.jsonl")
    ms = [json.loads(x) for x in open(mp) if x.strip()]
    out = []
    for m in ms:
        if m.get("kind") == "start_gate":
            continue
        out.append(m)
        if m.get("kind") == "room":
            r = m["mean34_c"] if room is None else room
            if pre_a6:
                out.append({"kind": "start_gate", "t_ms": m["t_ms"], "room_c": r, "max_c": 53.0, "passed": r <= 53.0,
                            "why": "self-test: a pre-A6 G0 mark"})
                continue
            resid = r - floor
            exc = resid - RESIDUE_PRED_C
            ok = r <= ROOM_MAX_C + EPS_C and exc <= RESIDUE_LINE_C + EPS_C
            out.append({"kind": "start_gate", "t_ms": m["t_ms"], "room_c": r, "max_c": ROOM_MAX_C, "floor_c": floor, "floor_from": "self-test",
                        "residue_c": resid, "residue_pred_c": RESIDUE_PRED_C, "residue_excess_c": exc, "residue_line_c": RESIDUE_LINE_C,
                        "room_ok": r <= ROOM_MAX_C, "residue_ok": exc <= RESIDUE_LINE_C,
                        "passed": ok if passed_override is None else passed_override,
                        "why": (f"room {r:.3f} C > {ROOM_MAX_C} C" if r > ROOM_MAX_C else
                                (f"R0's room - F0 - {RESIDUE_PRED_C} = {exc:+.3f} C > {RESIDUE_LINE_C} C (A8-4)" if exc > RESIDUE_LINE_C
                                 else "self-test: the design runs")),
                        "rule": "A6-2 with A8-4"})
    with open(mp, "w") as f:
        for m in out:
            f.write(json.dumps(m) + "\n")


def self_test(workdir):
    if os.path.exists(workdir):
        raise SystemExit(f"--workdir {workdir} exists: name a new one")
    os.makedirs(workdir)
    T = {"lists_checked": dict(_V3_COUNTS), "cases": {}}
    probs = []

    def case(name, ok, got):
        T["cases"][name] = {"pass": bool(ok), "got": got}
        if not ok:
            probs.append(f"{name}: {got}")

    # (1) the gate's constants are run_e181.py's (the kit and the scorer read one rule)
    import ast  # noqa: E402  (run_e181.py's constants read from its source: nothing of the box runner is imported or run)
    kc = {}
    for node in ast.parse(open(os.path.join(TREE, "tools", "claims-v3", "e181", "run_e181.py")).read()).body:
        if isinstance(node, ast.Assign):
            for tg in node.targets:
                names = [tg] if isinstance(tg, ast.Name) else (list(tg.elts) if isinstance(tg, ast.Tuple) else [])
                vals = [node.value] if isinstance(tg, ast.Name) else (list(node.value.elts) if isinstance(node.value, ast.Tuple) else [])
                for n_, v_ in zip(names, vals):
                    if isinstance(n_, ast.Name) and n_.id in ("ROOM_MAX_C", "FLOOR_MAX_C", "RESIDUE_PRED_C", "RESIDUE_LINE_C", "WARM_HI", "EPS_C", "REGISTRATION"):
                        kc[n_.id] = ast.literal_eval(v_)
    case("G1 the gate's constants equal run_e181.py's", (kc.get("ROOM_MAX_C"), kc.get("FLOOR_MAX_C"), kc.get("RESIDUE_PRED_C"),
                                                          kc.get("RESIDUE_LINE_C"), kc.get("WARM_HI"), kc.get("EPS_C"))
         == (ROOM_MAX_C, FLOOR_MAX_C, RESIDUE_PRED_C, RESIDUE_LINE_C, 53.9, EPS_C) and (kc.get("REGISTRATION") or {}).get("a8") == NEW_COMMITS["A8"], kc)
    a8 = json.load(open(os.path.join(HERE, "residue-a8.json")))["E181"]["predicted_residue_C"]
    case("G2 A8-4's frozen 0.414 C is residue-a8.json's prediction to 3 decimals", round(a8, 3) == RESIDUE_PRED_C, a8)
    # (2) gate_reading on synthetic marks
    g_pass = gate_reading({"room_c": 51.6, "floor_c": 51.0, "residue_c": 0.6, "max_c": 53.9, "residue_pred_c": 0.414, "residue_line_c": 0.5, "passed": True})
    g_room = gate_reading({"room_c": 54.0, "floor_c": 53.8, "residue_c": 0.2, "max_c": 53.9, "residue_pred_c": 0.414, "residue_line_c": 0.5, "passed": False})
    g_res = gate_reading({"room_c": 52.0, "floor_c": 51.0, "residue_c": 1.0, "max_c": 53.9, "residue_pred_c": 0.414, "residue_line_c": 0.5, "passed": False})
    g_lie = gate_reading({"room_c": 52.0, "floor_c": 51.0, "residue_c": 1.0, "max_c": 53.9, "residue_pred_c": 0.414, "residue_line_c": 0.5, "passed": True})
    g_loose = gate_reading({"room_c": 51.6, "floor_c": 51.0, "residue_c": 0.6, "max_c": 54.5, "residue_pred_c": 0.414, "residue_line_c": 0.5, "passed": True})
    g_edge = gate_reading({"room_c": 51.914, "floor_c": 51.0, "residue_c": 0.914, "max_c": 53.9, "residue_pred_c": 0.414, "residue_line_c": 0.5, "passed": True})
    case("G3 gate_reading: pass / room / residue / a lying mark / a looser line / the line's edge",
         g_pass["agrees"] and g_pass["recomputed"] and g_room["agrees"] and not g_room["recomputed"] and g_res["agrees"]
         and not g_res["recomputed"] and not g_lie["agrees"] and not g_loose["agrees"] and g_edge["recomputed"] and g_edge["agrees"],
         {"pass": g_pass["recomputed"], "room": g_room["recomputed"], "residue": g_res["recomputed"], "lie_agrees": g_lie["agrees"],
          "loose_agrees": g_loose["agrees"], "edge_recomputed": g_edge["recomputed"], "edge_excess": g_edge["residue_excess_c"]})
    # (3) FL5(c) on synthetic rests with known slopes
    rng = random.Random("M11-v3-selftest|FL5c")

    def synth(dk, n_per=400, degs=range(53, 63), off=0.85):
        fw, m34, W = [], [], []
        for t in degs:
            for _ in range(n_per):
                x = t + rng.uniform(-0.5, 0.5)
                fw.append(float(t))
                m34.append(x + off)
                W.append(_quad(FL1_A3, x) + dk * (x - 58.0) + rng.gauss(0, 0.05))
        return fw, m34, W
    r0 = fl5c_read(*synth(0.0))
    r5 = fl5c_read(*synth(0.05))
    rs = fl5c_read(*synth(0.0, n_per=25))
    case("F1 FL5(c): FL1's own law reads PASS; a slope 0.05 W/C above it FAIL; 250 samples NOT SCORED",
         r0["verdict"] == "PASS" and abs(r0["diff_w_per_c"]) < 0.01 and r5["verdict"] == "FAIL" and abs(r5["diff_w_per_c"] - 0.05) < 0.01
         and rs["verdict"] == "NOT SCORED",
         {"law": [r0["verdict"], r4(r0["diff_w_per_c"])], "plus_0.05": [r5["verdict"], r4(r5["diff_w_per_c"])], "few": rs["verdict"],
          "beside_law": r0["beside_34_codes"]["reads"]})
    # (4) FL5(c)'s estimator reproduces N1's committed dry run on E97's rests (footing-law-note1.json item 5)
    e97 = os.path.join(TREE, "docs/reports/data/2026-11-01-e97-heat-low-power-steady/aifoundry3/e97/p9720")
    names, fw, m34, W = fl5c_samples(e97, rest_names=("R0", "R1", "R2"))
    dr = fl5c_read(fw, m34, W, FL5C_DRY)
    com = json.load(open(os.path.join(FOOT, "footing-law-note1.json")))["5_FL5c_dry_run_on_E97_rests"]
    case("F2 the dry run on E97's rests, degrees 52-58, equals the footing law's N1 item 5",
         dr["degrees"] == com["degrees"] and dr["samples_by_degree"] == com["samples"]
         and abs(dr["slope_rests_w_per_c"] - com["slope_rests"]) < 1e-9 and abs(dr["slope_FL1_same_estimator"] - com["slope_FL1_same_estimator"]) < 1e-9,
         {"v3": [dr["degrees"], r4(dr["slope_rests_w_per_c"]), r4(dr["slope_FL1_same_estimator"]), r4(dr["diff_w_per_c"])],
          "committed": [com["degrees"], r4(com["slope_rests"]), r4(com["slope_FL1_same_estimator"]), r4(com["diff"])]})
    # (5) whole sessions on E154's committed pass, its holds renamed to M11's (v2's REN): passing, refused at the room, refused at the residue
    e154 = V1.P166.E154P
    room154 = [json.loads(x) for x in open(os.path.join(e154, "marks.jsonl")) if '"room"' in x]
    room154 = [m for m in room154 if m.get("kind") == "room"][0]["mean34_c"]
    f0 = 50.98740804036458                                         # E154's F0 (residue-a8.json > sessions > E154 > F0_C)
    runs = {}
    for nm, kw in (("S-PASS", {"floor": f0}), ("S-ROOM", {"floor": f0, "room": 54.0}), ("S-RES", {"floor": room154 - 0.414 - 0.6}),
                   ("S-PRE-A6", {"pre_a6": True})):
        d = os.path.join(workdir, nm, "p18120")
        os.makedirs(os.path.dirname(d))
        V2._renamed_e154(d)
        _rewrite_gate(d, **kw)
        lines = os.path.join(workdir, nm, "lines.jsonl")
        try:
            res = score([d], lines)
            runs[nm] = res
        except SystemExit as e:
            runs[nm] = {"refused": str(e)}
    p = runs["S-PASS"]
    sp = list(p["sessions"].values())[0]
    case("S1 a passing session: scored, its gate read whole, FL5(c) on its rests (both coordinates)",
         "excluded" not in sp and sp["start_gate_reading"]["form"] == "A6-2 with A8-4" and sp["start_gate_reading"]["agrees"]
         and sum(1 for h in sp["holds"].values() if h.get("scored")) == 5 and "FL5c" in sp
         and sp["FL5c"]["primary"]["verdict"] in ("PASS", "FAIL", "NOT SCORED") and "HM_LG" in p["aifoundry3"],
         {"holds_scored": sum(1 for h in sp["holds"].values() if h.get("scored")), "gate": sp["start_gate_reading"]["recomputed"],
          "residue_excess_c": r4(sp["start_gate_reading"]["residue_excess_c"]), "FL5c": sp["FL5c"]["primary"]["verdict"],
          "FL5c_diff": r4(sp["FL5c"]["primary"].get("diff_w_per_c")), "FL5c_34": sp["FL5c"]["primary"]["beside_34_codes"].get("reads"),
          "HM_LG": p["aifoundry3"]["HM_LG"]["verdict"], "label": p["label"][:9]})
    for nm, want in (("S-ROOM", "room 54.000 C"), ("S-RES", "A8-4")):
        q = runs[nm]
        s = list(q["sessions"].values())[0]
        case(f"S2 {nm}: refused at the start gate, NOT SCORED, the mark's reason carried",
             "excluded" in s and q["aifoundry3"].get("verdict", "").startswith("NOT SCORED") and "FL5c" not in s
             and not s["start_gate_reading"]["recomputed"] and s["start_gate_reading"]["agrees"],
             {"excluded": s.get("excluded"), "verdict": q["aifoundry3"].get("verdict"), "why_has": want in str(s.get("excluded"))})
        if want not in str(s.get("excluded")):
            probs.append(f"{nm}: the mark's reason ({want}) is not carried: {s.get('excluded')}")
    q = runs["S-PRE-A6"]
    s = list(q["sessions"].values())[0]
    case("S3 a pre-A6 mark (E176's kit form) read as that kit's own G0", s["start_gate_reading"]["form"].startswith("pre-A6")
         and s["start_gate_reading"]["agrees"], s["start_gate_reading"])
    # (6) a mark whose passed disagrees with its numbers: refused
    d = os.path.join(workdir, "S-LIE", "p18120")
    os.makedirs(os.path.dirname(d))
    V2._renamed_e154(d)
    _rewrite_gate(d, floor=room154 - 0.414 - 0.6, passed_override=True)
    try:
        score([d], os.path.join(workdir, "S-LIE", "lines.jsonl"))
        lie = "not refused"
    except SystemExit as e:
        lie = str(e)[:160]
    case("S4 a start_gate mark whose passed disagrees with its numbers: REFUSED", lie.startswith("M11 scorer v3 REFUSED"), lie)
    # (7) E176's committed pass beside a passing session: excluded with its own G0's reason; the passing one still decides
    e176 = os.path.join(TREE, "docs/reports/data/2026-11-05-e176-m11-holds-aifoundry3/aifoundry3/e176/p17620")
    res2 = score([e176, os.path.join(workdir, "S-PASS", "p18120")], os.path.join(workdir, "lines-two.jsonl"))
    s1, s2 = list(res2["sessions"].values())
    case("S5 E176's committed pass beside it: excluded (pre-A6 G0, 53.582 C > 53.0 C); the passing session scored",
         "excluded" in s1 and "excluded" not in s2 and s1["start_gate_reading"]["form"].startswith("pre-A6") and "HM_LG" in res2["aifoundry3"],
         {"E176": s1.get("excluded"), "second": "scored" if "excluded" not in s2 else s2.get("excluded")})
    # (8) the precedence with A6-A8: a launch now reads blind; one second before A8's commit, not
    rc, t8 = V1.git("log", "-1", "--format=%ct", NEW_COMMITS["A8"])
    pn = precedence(int(time.time() * 1000))
    pb = precedence((int(t8) - 1) * 1000) if rc == 0 and t8 else {"blind": None}
    case("P1 the precedence counts A6-A8: now blind, one second before A8 post hoc", pn["blind"] is True and pb["blind"] is False,
         {"now": pn["blind"], "before_A8": pb["blind"], "commits": list(REG_COMMITS)})
    T["problems"] = probs
    T["pass"] = not probs
    return T


def main():
    args = sys.argv[1:]
    jp = args[args.index("--json") + 1] if "--json" in args else None
    mp = args[args.index("--md") + 1] if "--md" in args else None
    if "--self-test" in args:
        if "--workdir" not in args:
            raise SystemExit("M11 scorer v3: --self-test needs --workdir <a new scratch dir>")
        T = self_test(args[args.index("--workdir") + 1])
        print("M11 scorer v3 self-test: lists " + ", ".join(f"{k} {v}" for k, v in T["lists_checked"].items()))
        for k, x in T["cases"].items():
            print(f"  {k:100s} {'PASS' if x['pass'] else 'FAIL'}  {json.dumps(x['got'], default=str)[:300]}")
        print("SELF-TEST " + ("PASS" if T["pass"] else "FAIL: " + "; ".join(T["problems"])))
        if jp:
            json.dump(T, open(jp, "w"), indent=1, sort_keys=True, default=str)
        sys.exit(0 if T["pass"] else 1)
    if not args or args[0] != "score":
        raise SystemExit(__doc__)
    if any(x == "--a2" for x in args):
        raise SystemExit("M11 scorer v3: no aifoundry2 reader here (E177 is not built); refused")
    a3 = [args[i + 1] for i, x in enumerate(args) if x == "--a3"]
    if not a3:
        raise SystemExit("M11 scorer v3: name at least one aifoundry3 pass with --a3")
    if "--lines" not in args:
        raise SystemExit("M11 scorer v3: name the lines file with --lines (A4-8: the lines are written before the later holds are read)")
    res = score(a3, args[args.index("--lines") + 1])
    if jp:
        json.dump(res, open(jp, "w"), indent=1, sort_keys=True, default=str)
    if mp:
        open(mp, "w").write(md_summary(res))
    print(md_summary(res))


if __name__ == "__main__":
    main()
