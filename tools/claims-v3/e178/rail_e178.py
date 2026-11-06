#!/usr/bin/env python3
"""E178 (Q146(g); dated note A3, E178.md.dated-note-A3.md): the REPORTED minion-rail arm, and its reader. Every one-number contrast the
scorer reads is read again, by the scorer's own statistic, on the minion rail's Drail and on the remainder off that rail, D - Drail,
beside the board's D. It is never a verdict: no rule, threshold, verdict or registered power figure of E178 reads it, and the scorer, the
reducer, the collector and every box file stay as committed. Standard library only (the self-test's last case runs the kit's collector,
which needs numpy: the Intel's /usr/bin/python3).

  freeze    python3 -B tools/claims-v3/e178/rail_e178.py freeze [--check]
            writes rail-e178.json and rail-e178.txt, the arm's frozen forecasts; --check rebuilds both in memory: CHECK PASS or FAIL
  read      python3 -B tools/claims-v3/e178/rail_e178.py read --runs-csv <primary runs.csv> --reduction <primary e178.json>
                [--scored <scored.json>] [--card aifoundry3] [--json <out>] [--md <out>]
  selftest  python3 -B tools/claims-v3/e178/rail_e178.py selftest [--txt <out>] [--json <out>] [--no-collect]

THE CONTRASTS (score_e178.py's, in its order): the couple rules E178-H-int8, -fp32, -fp16 and E178-U (COUPLE_RULES); E178-S-int8
(S_RULE) with 127 - neg_ones beside it (S_BESIDE, A1-1); A2-2's 85 - 127; then every pair of forecast-e178.json's `pairs` and its
`extremes`, as score_e178.reported lists them. 52 in all.

THE STATISTIC, the scorer's, unchanged and imported: a couple rule's per-pass x_p is score_e178.couple_xs (the mean over the pass's
segments in which both runs were kept of the in-segment difference, read from the primary's runs.csv); every other contrast's is
score_e178.pair_xs (the difference of the two kinds' per-pass values in the primary's e178.json per_pass); the interval is
score_e178.interval, m +- t(0.975, n - 1) sd / sqrt(n), over the kept passes that give a value; fewer than 2: NOT READ. The three
columns are the same call on three values of each run (couples) or each (pass, kind) (the rest):
  board   D, as the scorer reads it (this column is the scorer's own reading recomputed; the verdicts stay the scorer's);
  rail    Drail, the minion rail's switching over its type's zeros line (reduce_e78.py: rail80 less the interpolated zeros rail80);
  off     D - Drail, everything off the minion rail: the SRAM and NoC rails' part and everything off the three metered rails.
E178-C applies as the scorer applies it, when scored.json is given: a contrast with a kind E178-C left out is not read.

THE FORECAST, frozen in rail-e178.json by a mechanical rule with no measured error: for a contrast (a, b) of type t, the registered
board forecast (forecast-e178.json, aifoundry3's frozen P and F of a less b) times r_t on the rail and times (1 - r_t) off it, where r_t
is the median, over every item of E171's committed reduction (docs/reports/data/2026-11-05-e171-blind8-aifoundry3/e171.json, `items`)
of type t whose D mean over passes is above 2 W, of Drail.mean / D.mean: fp32 0.8096 (26 items), fp16 0.8080 (18), int8 0.8379 (19).
The forecast is not rescaled by the session's s or rates. aifoundry3 only: card 1 has no kit, and its arm would need its own note.

THE READINGS, never a verdict: the interval "reads above 0" (its lower end above 0), "reads below 0" or "spans 0"; each frozen forecast
(P and F) "inside", "above" or "below" the interval. The scorer's words (POSITIVE, PASS, FAIL HIGH, ...) are its verdicts' alone.

EXIT (read): 0 written; 2 usage (a card other than aifoundry3); 6 the runs.csv and the reduction are not one session's (a per-pass mean
differs by more than 1e-9 W, or the kept passes differ); 7 scored.json was given and the board column does not reproduce it; 9 a pinned
input differs, or rail-e178.json is not reproduced from them.
SPDX-License-Identifier: Apache-2.0
"""
import argparse
import csv
import hashlib
import json
import math
import os
import random
import shutil
import statistics
import subprocess
import sys
import tempfile

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
TOP = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

E171 = "docs/reports/data/2026-11-05-e171-blind8-aifoundry3"
# every committed file the arm's forecast and statistic rest on, pinned (each also in SHA256SUMS-e178-registration or -kit)
PINNED = {
    "tools/claims-v3/e178/forecast-e178.json": "7cb8fda874e521e2fd452377ec22981f44fca791811b3bd4d6eb7e87ae0ebf49",
    E171 + "/e171.json": "da1be39fa1992a60ccbce1e6743c03c38fee5b1ea3a045e1e2f49fa6289b7f8f",
    "tools/claims-v3/e178/score_e178.py": "4c2b14eb4a51986f90e980b4dae181dd3362d7918ef2d3190a29a0c26408b8c5",
    "tools/claims-v3/e178/power_e178.py": "2d979182daf334568f8654a7b2eba571ee6bf1e313a4e1f64e8d5b9b58aa7b72",
    "tools/claims-v3/e178/e178_common.py": "62cbf9fdc8cc37f32fedc7b4bd205fc9d5eb930b95639ce44713fad92db17b63",
}
# what the self-test reads besides them (committed; post hoc reads, never a forecast)
SELFTEST_READS = [E171 + "/runs.csv", "docs/reports/data/2026-11-03-q139u-footing/reduced/e78-footing.json",
                  "docs/reports/data/2026-11-03-q139u-footing/reduced/e82-footing.json",
                  "docs/reports/data/2026-11-05-q145a-anatomy-top-lines/anatomy.json", "tools/claims-v3/e178/selftest_collect_e178.py",
                  "tools/claims-v3/e178/collect_e178_v2.sh", "tools/claims-v3/e178/desktest_ccheck_standin_e178.py"]
FROZEN_JSON = os.path.join(HERE, "rail-e178.json")
FROZEN_TXT = os.path.join(HERE, "rail-e178.txt")
CARD, CD = "aifoundry3", "a3"
TYPES = ("fp32", "fp16", "int8")
D_MIN_W = 2.0
TOL_W = 1e-9
A2_2 = ("beside: 85 - 127", "int8.e178_v85", "int8.e178_v127")
COLS = ("board", "rail", "off")
RULE_TEXT = ("for a contrast (a, b) of type t: the registered board forecast (forecast-e178.json, aifoundry3's frozen P and F of a less "
             "b) times r_t on the minion rail and times (1 - r_t) off it; r_t = the median, over every item of E171's committed reduction "
             "(e171.json items) of type t whose D mean over passes is above 2 W, of Drail.mean / D.mean; not rescaled by the session's s "
             "or rates; aifoundry3 only")
NEVER = "reported beside the board verdicts, never a verdict (E178.md.dated-note-A3.md)"
_M = {}


class Refuse(Exception):
    def __init__(self, code, msg):
        super().__init__(msg)
        self.code = code


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def rel(p):
    p = os.path.abspath(p)
    return os.path.relpath(p, TOP) if p.startswith(TOP + os.sep) else os.path.basename(p)


def pinned_check(top=TOP):
    bad = []
    for r, want in PINNED.items():
        p = os.path.join(top, r)
        have = sha(p) if os.path.exists(p) else "missing"
        if have != want:
            bad.append(f"{r}: sha256 {have[:12]} is not the pinned {want[:12]}")
    if bad:
        raise Refuse(9, "a pinned input differs: " + "; ".join(bad))


def S():
    """score_e178.py, imported unchanged (nothing runs at import): its statistic and its contrast lists"""
    if "S" not in _M:
        import score_e178 as s  # noqa: E402
        _M["S"] = s
    return _M["S"]


# ------------------------------------------------------------------------------------------------- the frozen forecast
def ratios(e171, pool8_tiles_only=False):
    by = {}
    for name in sorted(e171["items"]):
        it = e171["items"][name]
        d, r = (it.get("D") or {}).get("mean"), (it.get("Drail") or {}).get("mean")
        if d is None or r is None or not d > D_MIN_W:
            continue
        if pool8_tiles_only and (it.get("anchor") or name == "anchor_pi"):
            continue
        by.setdefault(it["type"], []).append((name, r / d))
    out = {}
    for t in TYPES:
        v = sorted(x for _, x in by[t])
        out[t] = {"median": statistics.median(v), "n": len(v), "min": v[0], "max": v[-1], "items": [n for n, _ in by[t]]}
    return out


def contrast_list(fc):
    s = S()
    L = [{"name": r, "group": "rule", "form": "couple", "a": a, "b": b} for r, (a, b) in s.COUPLE_RULES.items()]
    L.append({"name": "E178-S-int8", "group": "rule", "form": "pass", "a": s.S_RULE[0], "b": s.S_RULE[1]})
    L.append({"name": "beside: 127 - neg_ones", "group": "reported (A1-1)", "form": "pass", "a": s.S_BESIDE[0], "b": s.S_BESIDE[1]})
    L.append({"name": A2_2[0], "group": "reported (A2-2)", "form": "pass", "a": A2_2[1], "b": A2_2[2]})
    for grp, lst in list(fc["pairs"].items()) + [("extremes", [v for t in TYPES for v in fc["extremes"][t].values()])]:
        for i, p in enumerate(lst):
            L.append({"name": f"{grp} {i}: {p['a']} - {p['b']}", "group": f"reported: {grp}", "index": i, "form": "pass", "a": p["a"],
                      "b": p["b"]})
    return L


def build_frozen(top=TOP):
    fc = json.load(open(os.path.join(top, "tools/claims-v3/e178/forecast-e178.json")))
    e171 = json.load(open(os.path.join(top, E171, "e171.json")))
    r, rv = ratios(e171), ratios(e171, pool8_tiles_only=True)
    cs, eff = [], 0.0
    for c in contrast_list(fc):
        ka, kb = fc["kinds"][c["a"]], fc["kinds"][c["b"]]
        if ka["type"] != kb["type"]:
            raise Refuse(9, f"{c['name']}: its two kinds differ in type")
        t = ka["type"]
        dP, dF = ka["P_w"][CD] - kb["P_w"][CD], ka["F_w"][CD] - kb["F_w"][CD]
        q = r[t]["median"]
        e = dict(c, type=t, board={"P_w": dP, "F_w": dF}, rail={"P_w": dP * q, "F_w": dF * q}, off={"P_w": dP * (1 - q), "F_w": dF * (1 - q)})
        eff = max(eff, abs(dP * (rv[t]["median"] - q)), abs(dF * (rv[t]["median"] - q)))
        cs.append(e)
    o = {"_what": "E178 (dated note A3): the reported minion-rail arm's frozen forecasts, written by rail_e178.py freeze before any E178 "
                  "datum; " + NEVER,
         "rule": RULE_TEXT, "card": CARD, "d_min_w": D_MIN_W,
         "inputs_sha256": {k: PINNED[k] for k in ("tools/claims-v3/e178/forecast-e178.json", E171 + "/e171.json")},
         "ratio": r,
         "ratio_variant_pool8_tiles_only": {"what": "the same rule over pool 8's own tiles alone (E78's three random anchors and the tie "
                                                    "left out): reported, not used", "ratio": rv,
                                            "largest_change_of_any_frozen_forecast_w": eff},
         "contrasts": cs}
    js = json.dumps(o, indent=1, sort_keys=True) + "\n"
    T = ["E178, dated note A3: the reported minion-rail arm's frozen forecasts (rail_e178.py freeze; aifoundry3; W). " + NEVER + ".",
         "Rule: " + RULE_TEXT + ".",
         "r_t: " + "; ".join(f"{t} {r[t]['median']:.4f} ({r[t]['n']} items, {r[t]['min']:.4f}-{r[t]['max']:.4f})" for t in TYPES)
         + ". Pool 8's tiles alone (reported, not used): " + "; ".join(f"{t} {rv[t]['median']:.4f} ({rv[t]['n']})" for t in TYPES)
         + f"; no frozen forecast moves by more than {eff:.6f} W.", "",
         f"{'contrast':66s} {'type':5s} {'board P':>9s} {'board F':>9s} {'rail P':>9s} {'rail F':>9s} {'off P':>9s} {'off F':>9s}"]
    for e in cs:
        T.append(f"{e['name'][:66]:66s} {e['type']:5s} {e['board']['P_w']:+9.4f} {e['board']['F_w']:+9.4f} {e['rail']['P_w']:+9.4f} "
                 f"{e['rail']['F_w']:+9.4f} {e['off']['P_w']:+9.4f} {e['off']['F_w']:+9.4f}")
    return js, "\n".join(T) + "\n", o


def frozen_ok(js_path=FROZEN_JSON, txt_path=FROZEN_TXT, top=TOP):
    js, txt, o = build_frozen(top)
    ok = os.path.exists(js_path) and open(js_path).read() == js and os.path.exists(txt_path) and open(txt_path).read() == txt
    return ok, o


# ------------------------------------------------------------------------------------------------- the session's files
def num(x, cast=float):
    try:
        return cast(x) if x not in (None, "", "None") else None
    except ValueError:
        return None


def load_runs(csv_path):
    rows = []
    with open(csv_path, newline="") as f:
        for r in csv.DictReader(f):
            d, dr = num(r.get("D")), num(r.get("Drail"))
            rows.append({"pass": num(r.get("pass"), int), "item": r.get("item"), "segment": num(r.get("segment"), int),
                         "pos": num(r.get("pos"), int), "D": d, "Drail": dr})
    return rows


def consistency(rows, res):
    """runs.csv against the reduction: the kept passes, and every per-pass mean of D and Drail (reduce_e78.py's per_pass)"""
    passes = [int(p) for p in res.get("passes", [])]
    csv_passes = sorted({r["pass"] for r in rows if r["D"] is not None})
    mx = {"D": 0.0, "Drail": 0.0}
    n_cmp, missing, no_rail = 0, [], []
    for p in passes:
        pp = res.get("per_pass", {}).get(str(p), {})
        for item, e in pp.items():
            rr = [r for r in rows if r["pass"] == p and r["item"] == item]
            for k in ("D", "Drail"):
                v = [r[k] for r in rr if r[k] is not None]
                if e.get(k) is None and not v:
                    continue
                if e.get(k) is None or not v:
                    missing.append(f"p{p} {item} {k}")
                    continue
                mx[k] = max(mx[k], abs(sum(v) / len(v) - float(e[k])))
            n_cmp += 1
            if any(r["D"] is not None and r["Drail"] is None for r in rr):
                no_rail.append(f"p{p} {item}")
    ok = csv_passes == passes and not missing and mx["D"] <= TOL_W and mx["Drail"] <= TOL_W
    return {"ok": ok, "kept_passes_reduction": passes, "kept_passes_runs_csv": csv_passes, "max_abs_diff_w": mx, "compared": n_cmp,
            "missing": missing, "kept_runs": sum(1 for r in rows if r["D"] is not None),
            "kept_runs_without_Drail": sum(1 for r in rows if r["D"] is not None and r["Drail"] is None),
            "pass_kinds_with_a_run_without_Drail": no_rail}


def views(rows, res):
    """the three columns as the scorer's functions read them: rows (couples) and a per_pass (the rest), with D set to the column"""
    def val(c, d, dr):
        if c == "board":
            return d
        if d is None or dr is None:
            return None
        return dr if c == "rail" else d - dr
    rv = {c: [dict(r, D=val(c, r["D"], r["Drail"])) for r in rows] for c in COLS}
    pv = {}
    for c in COLS:
        pp = {}
        for p, ents in res.get("per_pass", {}).items():
            pp[p] = {k: {"D": val(c, e.get("D"), e.get("Drail"))} for k, e in ents.items()}
        pv[c] = {"per_pass": pp}
    return rv, pv


def where(lo, hi, f):
    return "inside" if lo <= f <= hi else ("above" if f > hi else "below")


def read_contrast(c, fz, rv, pv, res, passes, excluded):
    s = S()
    out = {k: c[k] for k in ("name", "group", "form", "a", "b")}
    out["type"] = fz["type"]
    out["forecast_w"] = {col: fz[col] for col in COLS}
    left = [k for k in (c["a"], c["b"]) if k in excluded]
    if left:
        out["left_out"] = f"E178-C left out {left}"
        return out
    for col in COLS:
        xs = s.couple_xs(rv[col], passes, c["a"], c["b"]) if c["form"] == "couple" else s.pair_xs(pv[col], passes, c["a"], c["b"])
        v = [xs[p]["x"] for p in sorted(xs)]
        e = {"per_pass": {str(p): xs[p]["x"] for p in sorted(xs)}, "n": len(v)}
        if c["form"] == "couple":
            e["couples"] = {str(p): xs[p]["couples"] for p in sorted(xs)}
        if len(v) < 2:
            e["reading"] = f"NOT READ: {len(v)} kept passes give a value, fewer than 2"
        else:
            m, lo, hi, hw = s.interval(v)
            e.update(mean_w=m, lo95_w=lo, hi95_w=hi, halfwidth_w=hw,
                     interval_reads="reads above 0" if lo > 0 else ("reads below 0" if hi < 0 else "spans 0"))
            if col != "board":
                e.update(forecast_P_is=where(lo, hi, fz[col]["P_w"]), forecast_F_is=where(lo, hi, fz[col]["F_w"]))
        out[col] = e
    # the identity, per kept pass: board = rail + off (exact but for rounding when every run of both kinds has a Drail)
    b, r_, o = out["board"]["per_pass"], out["rail"]["per_pass"], out["off"]["per_pass"]
    same = sorted(b) == sorted(r_) == sorted(o)
    out["identity_max_abs_w"] = max((abs(b[p] - r_[p] - o[p]) for p in b if p in r_ and p in o), default=0.0)
    out["rail_reads_the_board_runs"] = same and out["identity_max_abs_w"] <= TOL_W
    return out


def scorer_board(sj, c):
    """the scorer's own board reading of this contrast in scored.json, or None where it reads none"""
    pr = sj.get("primary") or {}
    if c["group"] == "rule" or c["name"] == "beside: 127 - neg_ones":
        r = (pr.get("rules") or {}).get(c["name"]) or {}
        return {"verdict": r.get("verdict"), "size": r.get("size"), "size_F": r.get("size_F"), "mean_w": r.get("mean_w"),
                "lo95_w": r.get("lo95_w"), "hi95_w": r.get("hi95_w"), "n": r.get("n"),
                "per_pass": {str(p): v.get("x") for p, v in (r.get("per_pass") or {}).items()}}
    if c["group"].startswith("reported: "):
        lst = ((pr.get("reported") or {}).get("pairs") or {}).get(c["group"][len("reported: "):]) or []
        r = lst[c["index"]] if c.get("index") is not None and c["index"] < len(lst) else {}
        if (r.get("a"), r.get("b")) != (c["a"], c["b"]):
            return {"mismatch": f"scored.json lists {r.get('a')} - {r.get('b')} here"}
        return {"sign": r.get("sign"), "P_inside": r.get("P_inside"), "F_inside": r.get("F_inside"), "mean_w": r.get("mean_w"),
                "lo95_w": r.get("lo95_w"), "hi95_w": r.get("hi95_w"), "n": r.get("n")}
    return None


def cross_check(sj, c, mine):
    """the board column against the scorer's reading of the same contrast; returns a list of differences"""
    sb = scorer_board(sj, c)
    if sb is None:
        return [], None
    if "mismatch" in sb:
        return [f"{c['name']}: {sb['mismatch']}"], sb
    if "left_out" in mine:
        return [], sb
    bad = []
    b = mine["board"]
    for k in ("mean_w", "lo95_w", "hi95_w"):
        x, y = b.get(k), sb.get(k)
        if (x is None) != (y is None) or (x is not None and abs(float(x) - float(y)) > TOL_W):
            bad.append(f"{c['name']}: board {k} {x} against scored.json's {y}")
    if sb.get("n") is not None and sb["n"] != b["n"]:
        bad.append(f"{c['name']}: board n {b['n']} against scored.json's {sb['n']}")
    for p, x in (sb.get("per_pass") or {}).items():
        y = b["per_pass"].get(str(p))
        if y is None or abs(float(x) - y) > TOL_W:
            bad.append(f"{c['name']}: p{p} board x {y} against scored.json's {x}")
    return bad, sb


def read_session(card, csv_path, red_path, scored_path=None, frozen_paths=(FROZEN_JSON, FROZEN_TXT)):
    if card != CARD:
        raise Refuse(2, f"the arm is frozen for {CARD} only, not {card}: card 1 has no E178 kit, and its arm needs its own dated note")
    pinned_check()
    ok, fz = frozen_ok(*frozen_paths)
    if not ok:
        raise Refuse(9, "rail-e178.json or rail-e178.txt is not reproduced from the pinned inputs: refusing")
    rows, res = load_runs(csv_path), json.load(open(red_path))
    cons = consistency(rows, res)
    if not cons["ok"]:
        raise Refuse(6, "runs.csv and the reduction are not one session's: " + json.dumps({k: cons[k] for k in (
            "kept_passes_reduction", "kept_passes_runs_csv", "max_abs_diff_w", "missing")})[:600])
    sj = json.load(open(scored_path)) if scored_path else None
    excluded = set(((sj or {}).get("primary") or {}).get("rules", {}).get("E178-C", {}).get("c_excluded") or []) if sj else set()
    passes = cons["kept_passes_reduction"]
    rv, pv = views(rows, res)
    out = {"_note": "E178 (dated note A3): the reported minion-rail arm, read by rail_e178.py; " + NEVER, "run": "E178", "card": card,
           "reader_sha256": sha(os.path.abspath(__file__)),
           "inputs": {"runs_csv": rel(csv_path), "runs_csv_sha256": sha(csv_path), "reduction": rel(red_path), "reduction_sha256": sha(red_path),
                      "scored": rel(scored_path) if scored_path else None, "scored_sha256": sha(scored_path) if scored_path else None},
           "frozen": {"rail_e178_json_sha256": sha(frozen_paths[0]), "ratio": {t: fz["ratio"][t]["median"] for t in TYPES}},
           "kept_passes": passes, "consistency": cons,
           "e178_c": ({"applied": True, "c_excluded": sorted(excluded)} if sj else
                      {"applied": False, "why": "no scored.json given: every kind is read"}),
           "contrasts": []}
    if len(passes) < 2:
        out["NOT READ"] = f"{len(passes)} kept passes, fewer than 2"
    diffs = []
    for c, f in zip(contrast_list(json.load(open(os.path.join(HERE, "forecast-e178.json")))), fz["contrasts"]):
        if (c["a"], c["b"], c["name"]) != (f["a"], f["b"], f["name"]):
            raise Refuse(9, f"the contrast list and rail-e178.json differ at {c['name']}")
        e = read_contrast(c, f, rv, pv, res, passes, excluded)
        if sj is not None:
            d, sb = cross_check(sj, c, e)
            diffs += d
            if sb is not None:
                e["scorer_board"] = sb
        out["contrasts"].append(e)
    # A2-2's identity: 85 - 127 = S-int8 less 127 - neg_ones, per kept pass (neg_ones cancels)
    cm = {e["name"]: e for e in out["contrasts"]}
    a22 = []
    if all(n in cm and "board" in cm[n] for n in ("E178-S-int8", "beside: 127 - neg_ones", A2_2[0])):
        for col in COLS:
            x, y, z = (cm[n][col]["per_pass"] for n in ("E178-S-int8", "beside: 127 - neg_ones", A2_2[0]))
            a22 += [abs(x[p] - y[p] - z[p]) for p in z if p in x and p in y]
    out["a2_2_identity_max_abs_w"] = max(a22, default=None)
    if sj is not None:
        out["cross_check_with_scored_json"] = {"ok": not diffs, "differences": diffs[:40], "n_differences": len(diffs)}
        if diffs:
            raise Refuse(7, "the board column does not reproduce scored.json (the files are not one session's): " + "; ".join(diffs[:6]))
    return out


def fmt(e, col):
    x = e.get(col) or {}
    if "mean_w" not in x:
        return x.get("reading", "")
    s = f"{x['mean_w']:+.4f} [{x['lo95_w']:+.4f}, {x['hi95_w']:+.4f}]"
    if col != "board":
        s += (f"; forecast {e['forecast_w'][col]['P_w']:+.4f} (P) {x['forecast_P_is']}, {e['forecast_w'][col]['F_w']:+.4f} (F) "
              f"{x['forecast_F_is']}; {x['interval_reads']}")
    else:
        s += f" (P {e['forecast_w']['board']['P_w']:+.4f})"
    return s


def markdown(o):
    L = [f"# E178 on {o['card']}: the reported minion-rail arm (dated note A3, rail_e178.py), never a verdict", "",
         f"runs.csv {o['inputs']['runs_csv_sha256'][:12]}, e178.json {o['inputs']['reduction_sha256'][:12]}, scored.json "
         f"{(o['inputs']['scored_sha256'] or 'not given')[:12]}; kept passes {o['kept_passes']}; kept runs {o['consistency']['kept_runs']}, "
         f"of them without a Drail {o['consistency']['kept_runs_without_Drail']}; E178-C "
         + (f"applied (left out: {o['e178_c']['c_excluded']})" if o["e178_c"]["applied"] else "not applied (no scored.json)") + ".",
         "", "The frozen forecasts (rail-e178.json): the registered board forecast times E171's median Drail/D for the format, "
         + ", ".join(f"{t} {v:.4f}" for t, v in o["frozen"]["ratio"].items()) + ", on the minion rail; times one less it off the rail. "
         "Each interval is the scorer's statistic, m +- t(0.975, n - 1) sd / sqrt(n) over the kept passes. The board column is the "
         "scorer's own reading; its verdicts are the scorer's (results.md).", "",
         "| contrast | the scorer's verdict | board D, W | minion rail Drail, W | off the minion rail, D - Drail, W | n |", "|---|---|---|---|---|---|"]
    for e in o["contrasts"]:
        sb = e.get("scorer_board") or {}
        v = (f"{sb.get('verdict')} / SIZE {sb.get('size')}" if "verdict" in sb else
             (f"sign {sb.get('sign')}, P inside {sb.get('P_inside')}" if "sign" in sb else ""))
        if "left_out" in e:
            L.append(f"| {e['name']} | {v} | {e['left_out']} | | | |")
            continue
        L.append(f"| {e['name']} | {v} | {fmt(e, 'board')} | {fmt(e, 'rail')} | {fmt(e, 'off')} | {e['board']['n']} |")
    L += ["", f"Reported beside the board verdicts, never a verdict. A2-2's identity (85 - 127 = S-int8 less 127 - neg_ones, per pass): "
              f"{o.get('a2_2_identity_max_abs_w')} W at most."]
    return "\n".join(L) + "\n"


# ------------------------------------------------------------------------------------------------- the self-test
LINES, RES = [], {}


def check(name, ok, detail):
    RES[name] = {"pass": bool(ok), "detail": detail}
    LINES.append(f"{name}: {'PASS' if ok else 'FAIL'} - {detail}")


def indep_interval(v):
    n = len(v)
    m = sum(v) / n
    sd = math.sqrt(sum((x - m) ** 2 for x in v) / (n - 1))
    t = {1: 12.706, 2: 4.303, 3: 3.182, 4: 2.776, 5: 2.571, 6: 2.447}[n - 1]
    return m, m - t * sd / math.sqrt(n), m + t * sd / math.sqrt(n)


def synth(tmp, name, truth, seed, passes=(17810, 17811, 17812, 17813), drop_rail=None, sd_rail=0.002, sd_off=0.004):
    """a synthetic E178 session in the registered order: each run's Drail = the kind's rail truth + noise, D = Drail + its off truth +
    noise; writes runs.csv and a reduction json (reduce_e78.py's per_pass: the mean of the kept runs) and returns their paths"""
    import e178_common as E  # noqa: E402
    rng = random.Random(seed)
    rows = []
    for p in passes:
        for j, (n, s) in enumerate(E.order_by_rule(CARD, p)):
            rt, ot = truth(n)
            dr = rt + rng.gauss(0, sd_rail)
            d = dr + ot + rng.gauss(0, sd_off)
            rows.append({"pass": p, "segment": s, "pos": j, "item": n, "D": d, "Drail": dr, "fail": 0})
    if drop_rail:
        for r in rows:
            if (r["pass"], r["item"], r["segment"]) == drop_rail:
                r["Drail"] = None
                break
    per = {}
    for r in rows:
        e = per.setdefault(str(r["pass"]), {}).setdefault(r["item"], {"_D": [], "_R": []})
        e["_D"].append(r["D"])
        if r["Drail"] is not None:
            e["_R"].append(r["Drail"])
    for p in per:
        for k, e in per[p].items():
            per[p][k] = {"D": sum(e["_D"]) / len(e["_D"]), "Drail": (sum(e["_R"]) / len(e["_R"])) if e["_R"] else None}
    res = {"passes": list(passes), "per_pass": per, "items": {}}
    cp, rp = os.path.join(tmp, f"{name}-runs.csv"), os.path.join(tmp, f"{name}-e178.json")
    with open(cp, "w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["D", "Drail", "fail", "item", "pass", "pos", "segment"])
        w.writeheader()
        for r in rows:
            w.writerow({k: ("" if r[k] is None else r[k]) for k in w.fieldnames})
    json.dump(res, open(rp, "w"))
    return cp, rp


def synth_scored(tmp, name, csv_path, red_path, excluded=()):
    """a scored.json with the scorer's own board readings of the synthetic session (its functions, unchanged; s = 1)"""
    s = S()
    import e178_common as E  # noqa: E402
    fc = json.load(open(os.path.join(HERE, "forecast-e178.json")))
    res = json.load(open(red_path))
    passes = [int(p) for p in res["passes"]]
    rows = s.load_rows(csv_path)
    sf = s.scored_forecasts(fc, CARD, 1.0, res)
    ok = set(E.E178_NAMES) - set(excluded)
    R = {"E178-C": {"verdict": "FAIL" if excluded else "PASS", "c_excluded": sorted(excluded)}}
    for rule, (a, b) in s.COUPLE_RULES.items():
        R[rule] = s.diff_rule(s.couple_xs(rows, passes, a, b), sf[a]["P_w"] - sf[b]["P_w"], sf[a]["F_w"] - sf[b]["F_w"]) if (
            a in ok and b in ok) else {"verdict": "NOT SCORED"}
    for rule, (a, b) in (("E178-S-int8", s.S_RULE), ("beside: 127 - neg_ones", s.S_BESIDE)):
        R[rule] = s.diff_rule(s.pair_xs(res, passes, a, b), sf[a]["P_w"] - sf[b]["P_w"], sf[a]["F_w"] - sf[b]["F_w"]) if (
            a in ok and b in ok) else {"verdict": "NOT SCORED"}
    meas, _ = s.measured(res, list(E.E178_NAMES), passes)
    rep = s.reported(fc, sf, meas, rows, passes, res, ok)
    sj = {"primary": {"rules": R, "reported": rep}, "verdicts": {k: v.get("verdict") for k, v in R.items()}}
    pth = os.path.join(tmp, f"{name}-scored.json")
    open(pth, "w").write(json.dumps(sj, indent=1, sort_keys=True, default=str) + "\n")
    return pth


def selftest(a):
    s = S()
    import e178_common as E  # noqa: E402
    # T1 the pinned inputs and the frozen files
    try:
        pinned_check()
        p_ok, p_why = True, ""
    except Refuse as e:
        p_ok, p_why = False, f" ({e})"
    f_ok, fz = frozen_ok()
    check("T1 the pinned inputs, and rail-e178.json and .txt rebuilt from them", p_ok and f_ok,
          f"{len(PINNED)} pinned sha256 match: {p_ok}{p_why}; rail-e178.json and rail-e178.txt byte for byte: {f_ok}; "
          f"{len(fz['contrasts'])} contrasts")
    # T2 the ratios, re-derived from e171.json and again from E171's runs.csv
    e171 = json.load(open(os.path.join(TOP, E171, "e171.json")))
    rows171 = load_runs(os.path.join(TOP, E171, "runs.csv"))
    r = ratios(e171)
    alt = {}
    for name, it in e171["items"].items():
        pm = {}
        for k in ("D", "Drail"):
            per = []
            for p in e171["passes"]:
                v = [x[k] for x in rows171 if x["pass"] == p and x["item"] == name and x[k] is not None]
                if v:
                    per.append(sum(v) / len(v))
            pm[k] = sum(per) / len(per) if per else None
        if pm["D"] is not None and pm["Drail"] is not None and pm["D"] > D_MIN_W:
            alt.setdefault(it["type"], []).append(pm["Drail"] / pm["D"])
    alt_med = {t: statistics.median(alt[t]) for t in TYPES}
    rr = {t: round(r[t]["median"], 3) for t in TYPES}
    check("T2 the ratios r_t, re-derived", rr == {"fp32": 0.810, "fp16": 0.808, "int8": 0.838}
          and [r[t]["n"] for t in TYPES] == [26, 18, 19] and max(abs(alt_med[t] - r[t]["median"]) for t in TYPES) < 1e-12,
          "e171.json, items with D > 2 W: " + "; ".join(f"{t} {r[t]['median']:.6f} (n {r[t]['n']})" for t in TYPES)
          + f"; from E171's runs.csv the same to {max(abs(alt_med[t] - r[t]['median']) for t in TYPES):.1e}; pool 8's tiles alone: "
          + "; ".join(f"{t} {v['median']:.6f} (n {v['n']})" for t, v in fz["ratio_variant_pool8_tiles_only"]["ratio"].items())
          + f" (largest change of any frozen forecast {fz['ratio_variant_pool8_tiles_only']['largest_change_of_any_frozen_forecast_w']:.6f} W)")
    h = next(c for c in fz["contrasts"] if c["name"] == "E178-H-int8")
    check("T3 the example: int8 5s against 4s", round(h["board"]["P_w"], 3) == 0.186 and round(h["rail"]["P_w"], 3) == 0.156,
          f"board {h['board']['P_w']:+.4f} W, rail {h['rail']['P_w']:+.4f} W, off {h['off']['P_w']:+.4f} W (P); F {h['board']['F_w']:+.4f} / "
          f"{h['rail']['F_w']:+.4f} / {h['off']['F_w']:+.4f} W")
    # T4 E171's committed session through the reader's path (post hoc reads of E171; E171's own items, never E178's)
    cons = consistency(rows171, e171)
    rv, pv = views(rows171, e171)
    t4, worst, hw = [], 0.0, {}
    for a_, b_, form in (("fp32.randn", "fp32.zeros", "couple"), ("fp16.randn", "fp16.zeros", "couple"), ("int8.full", "int8.zeros", "couple"),
                         ("fp32.anchor8_randn_a_989b8a", "fp32.anchor8_randn_b_833ac3", "pass"),
                         ("fp16.anchor8_randn_a_8c7827", "fp16.anchor8_randn_b_3a0fef", "pass"),
                         ("int8.anchor8_full_a_4aac84", "int8.anchor8_full_b_935710", "pass")):
        c = {"name": f"{a_} - {b_}", "group": "selftest", "form": form, "a": a_, "b": b_}
        fzc = {"type": a_.split(".")[0], **{col: {"P_w": 0.0, "F_w": 0.0} for col in COLS}}
        e = read_contrast(c, fzc, rv, pv, e171, e171["passes"], set())
        ref = (s.couple_xs(s.load_rows(os.path.join(TOP, E171, "runs.csv")), e171["passes"], a_, b_) if form == "couple"
               else s.pair_xs(e171, e171["passes"], a_, b_))
        same = {str(p): v["x"] for p, v in ref.items()} == e["board"]["per_pass"]
        ind = [indep_interval(list(e[col]["per_pass"].values())) for col in COLS]
        d_ind = max(abs(ind[i][j] - (e[col]["mean_w"], e[col]["lo95_w"], e[col]["hi95_w"])[j]) for i, col in enumerate(COLS) for j in range(3))
        worst = max(worst, d_ind)
        cpl = sorted(set((e["board"].get("couples") or {}).values()))
        t4.append(same and e["rail_reads_the_board_runs"] and d_ind < 1e-12 and (form == "pass" or cpl == [3]))
        hw[c["name"]] = {col: e[col]["halfwidth_w"] for col in COLS}
        hw[c["name"]]["mean"] = {col: e[col]["mean_w"] for col in COLS}
    RES["T4_halfwidths_e171_post_hoc"] = hw
    check("T4 E171's committed session (runs.csv and e171.json) through the reader", cons["ok"] and cons["kept_runs_without_Drail"] == 0
          and all(t4),
          f"runs.csv's per-pass means against e171.json: D to {cons['max_abs_diff_w']['D']:.1e} W, Drail to {cons['max_abs_diff_w']['Drail']:.1e} "
          f"W over {cons['compared']} (pass, item) entries; kept runs {cons['kept_runs']}, without a Drail {cons['kept_runs_without_Drail']}; "
          f"three couples (each anchor against its zeros, 3 complete couples a pass) and three same-format pool-8 anchor pairs: the board "
          f"column equals score_e178.couple_xs / pair_xs called directly, board = rail + off in every pass, and an independent mean, sd and "
          f"t give the three intervals to {worst:.1e} W: {sum(t4)} of {len(t4)}")
    # T5 the anatomy's earlier measurement: its int8 -1 against 1 and the other one-number pairs, from Q139(u)'s footing reductions
    an = json.load(open(os.path.join(TOP, "docs/reports/data/2026-11-05-q145a-anatomy-top-lines/anatomy.json")))
    red = {"E78": json.load(open(os.path.join(TOP, "docs/reports/data/2026-11-03-q139u-footing/reduced/e78-footing.json"))),
           "E82": json.load(open(os.path.join(TOP, "docs/reports/data/2026-11-03-q139u-footing/reduced/e82-footing.json")))}
    t5, mxd, i8 = [], 0.0, {}
    for tp in an["tensor_pairs"]:
        rs = red[tp["session"]]
        _, pv5 = views([], rs)
        c = {"name": f"{tp['session']} {tp['a']} - {tp['b']}", "group": "selftest", "form": "pass", "a": tp["a"], "b": tp["b"]}
        e = read_contrast(c, {"type": "", **{col: {"P_w": 0.0, "F_w": 0.0} for col in COLS}}, {}, pv5, rs, [int(p) for p in rs["passes"]], set())
        for col, key in (("board", "D"), ("rail", "Drail")):
            for k1, k2 in (("mean_w", "mean"), ("halfwidth_w", "ci95")):
                mxd = max(mxd, abs(e[col][k1] - tp[key][k2]))
        t5.append(e["board"]["n"] == tp["D"]["n"] == tp["Drail"]["n"])
        if tp["a"] == "int8.neg_ones":
            i8[tp["session"]] = {col: (e[col]["mean_w"], e[col]["halfwidth_w"]) for col in COLS}
    RES["T5_int8_minus1_against_1"] = i8
    check("T5 the anatomy's committed pairs (anatomy.json tensor_pairs; E78 and E82 at Q139(u)'s footing), re-read", all(t5) and mxd < 1e-9
          and len(t5) == 12,
          f"{len(t5)} pairs, every mean and 95% half-width of D and Drail to {mxd:.1e} W; int8 -1 against 1: "
          + "; ".join(f"{k} board {v['board'][0]:+.4f} +- {v['board'][1]:.4f}, rail {v['rail'][0]:+.4f} +- {v['rail'][1]:.4f}, off "
                      f"{v['off'][0]:+.4f} +- {v['off'][1]:.4f} W" for k, v in i8.items()))
    # T6 synthetic sessions in E178's registered order
    fcj = json.load(open(os.path.join(HERE, "forecast-e178.json")))
    q = {t: fz["ratio"][t]["median"] for t in TYPES}
    Pk = {k: v["P_w"][CD] for k, v in fcj["kinds"].items()}

    def p_truth(n):
        t = n.split(".")[0] if "." in n else "fp32"
        b = Pk.get(n, 0.0)
        return b * q[t], b * (1 - q[t])

    def flat_rail(n):
        t = n.split(".")[0] if "." in n else "fp32"
        b = Pk.get(n, 0.0)
        return (1.70 * q[t], b - 1.70 * q[t]) if t == "int8" else (b * q[t], b * (1 - q[t]))

    tmp = tempfile.mkdtemp(prefix="rail-e178-selftest-")
    try:
        c1, r1 = synth(tmp, "s1", p_truth, 17831)
        sc1 = synth_scored(tmp, "s1", c1, r1)
        o = read_session(CARD, c1, r1, sc1)
        cm = {e["name"]: e for e in o["contrasts"]}
        hh = cm["E178-H-int8"]
        ins = [e for e in o["contrasts"] if "rail" in e and "forecast_P_is" in e["rail"]]
        inside = sum(1 for e in ins if e["rail"]["forecast_P_is"] == "inside")
        ident = max(e["identity_max_abs_w"] for e in o["contrasts"])
        check("S1 the forecast true on both lines", o["cross_check_with_scored_json"]["ok"] and hh["rail"]["interval_reads"] == "reads above 0"
              and abs(hh["rail"]["mean_w"] - hh["forecast_w"]["rail"]["P_w"]) <= 2 * hh["rail"]["halfwidth_w"] and ident < 1e-12
              and inside >= 0.85 * len(ins) and len(o["contrasts"]) == 52 and o["a2_2_identity_max_abs_w"] < 1e-12,
              f"52 contrasts read; the board column reproduces the scorer's own readings (rules and reported pairs): "
              f"{o['cross_check_with_scored_json']['ok']}; H-int8 rail {hh['rail']['mean_w']:+.4f} [{hh['rail']['lo95_w']:+.4f}, "
              f"{hh['rail']['hi95_w']:+.4f}] W {hh['rail']['interval_reads']}, its forecast {hh['forecast_w']['rail']['P_w']:+.4f} "
              f"{hh['rail']['forecast_P_is']}; rail forecasts inside {inside} of {len(ins)}; board = rail + off to {ident:.1e} W; A2-2's "
              f"identity to {o['a2_2_identity_max_abs_w']:.1e} W")
        c2, r2 = synth(tmp, "s2", flat_rail, 17832)
        o2 = read_session(CARD, c2, r2)
        h2 = {e["name"]: e for e in o2["contrasts"]}["E178-H-int8"]
        check("S2 int8's difference all off the minion rail (the rail flat)", abs(h2["rail"]["mean_w"]) < 0.01
              and h2["off"]["interval_reads"] == "reads above 0" and h2["rail"]["forecast_P_is"] == "above" and not o2["e178_c"]["applied"],
              f"H-int8 rail {h2['rail']['mean_w']:+.4f} [{h2['rail']['lo95_w']:+.4f}, {h2['rail']['hi95_w']:+.4f}] {h2['rail']['interval_reads']} "
              f"(forecast {h2['rail']['forecast_P_is']}); off {h2['off']['mean_w']:+.4f} {h2['off']['interval_reads']}; E178-C not applied "
              f"without scored.json")
        c3, r3 = synth(tmp, "s3", p_truth, 17833, drop_rail=(17811, "int8.e178_v5", 1))
        o3 = read_session(CARD, c3, r3)
        h3 = {e["name"]: e for e in o3["contrasts"]}["E178-H-int8"]
        check("S3 one kept run without a Drail", o3["consistency"]["kept_runs_without_Drail"] == 1
              and o3["consistency"]["pass_kinds_with_a_run_without_Drail"] == ["p17811 int8.e178_v5"] and not h3["rail_reads_the_board_runs"]
              and "mean_w" in h3["rail"],
              f"named: {o3['consistency']['pass_kinds_with_a_run_without_Drail']}; H-int8 read on the runs that have one, and flagged "
              f"(rail_reads_the_board_runs {h3['rail_reads_the_board_runs']}, board - rail - off up to {h3['identity_max_abs_w']:.4f} W in that pass)")
        c4, r4 = synth(tmp, "s4", p_truth, 17834, passes=(17810,))
        o4 = read_session(CARD, c4, r4)
        nr = sum(1 for e in o4["contrasts"] if all(e[col].get("reading", "").startswith("NOT READ") for col in COLS))
        check("S4 one kept pass", nr == 52 and "NOT READ" in o4, f"{nr} of 52 contrasts NOT READ; '{o4.get('NOT READ')}'")
        sc5 = synth_scored(tmp, "s5", c1, r1, excluded=("int8.e178_v85",))
        o5 = read_session(CARD, c1, r1, sc5)
        lo = sorted(e["name"] for e in o5["contrasts"] if "left_out" in e)
        check("S5 E178-C leaves int8.e178_v85 out", lo == sorted(["E178-S-int8", A2_2[0], "extremes 4: int8.e178_v85 - int8.ones"])
              and o5["cross_check_with_scored_json"]["ok"], f"left out: {lo}")
        bad = json.load(open(r1))
        bad["per_pass"]["17812"]["int8.e178_v4"]["D"] += 0.01
        r6 = os.path.join(tmp, "s6-e178.json")
        json.dump(bad, open(r6, "w"))
        try:
            read_session(CARD, c1, r6)
            x6 = 0
        except Refuse as e:
            x6 = e.code
        check("S6 a reduction that is not the runs.csv's session", x6 == 6, f"exit {x6}")
        sjb = json.load(open(sc1))
        sjb["primary"]["rules"]["E178-H-int8"]["per_pass"]["17811"]["x"] += 0.001
        sc7 = os.path.join(tmp, "s7-scored.json")
        json.dump(sjb, open(sc7, "w"))
        try:
            read_session(CARD, c1, r1, sc7)
            x7 = 0
        except Refuse as e:
            x7 = e.code
        check("S7 a scored.json the board column does not reproduce", x7 == 7, f"exit {x7}")
        try:
            read_session("aifoundry1c1", c1, r1)
            x8 = 0
        except Refuse as e:
            x8 = e.code
        check("S8 card 1", x8 == 2, f"exit {x8}: the arm is frozen for aifoundry3 only")
        fj, ft = os.path.join(tmp, "rail-e178.json"), os.path.join(tmp, "rail-e178.txt")
        shutil.copyfile(FROZEN_JSON, fj)
        shutil.copyfile(FROZEN_TXT, ft)
        txt = open(fj).read()
        k = txt.index('"median": 0.8') + len('"median": 0.8')
        open(fj, "w").write(txt[:k] + ("1" if txt[k] != "1" else "2") + txt[k + 1:])
        try:
            read_session(CARD, c1, r1, None, (fj, ft))
            x9 = 0
        except Refuse as e:
            x9 = e.code
        check("S9 a changed rail-e178.json", x9 == 9, f"exit {x9}: one digit of a ratio changed in a copy")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    # T7 the kit's own collector on its relabelled real session (selftest_collect_e178.py's rule; a plumbing test, never quoted)
    if not a.no_collect:
        t7(E)
    ok = all(v["pass"] for v in RES.values() if isinstance(v, dict) and "pass" in v)
    n = sum(1 for v in RES.values() if isinstance(v, dict) and "pass" in v)
    LINES.append(f"SELFTEST-RAIL-E178 {'PASS' if ok else 'FAIL'}: {sum(1 for v in RES.values() if isinstance(v, dict) and v.get('pass'))} of "
                 f"{n} checks")
    txt = "\n".join(LINES) + "\n"
    print(txt, end="")
    if a.txt:
        open(a.txt, "w").write(txt)
    if a.json:
        open(a.json, "w").write(json.dumps(RES, indent=1, sort_keys=True) + "\n")
    return 0 if ok else 1


def t7(E):
    import selftest_collect_e178 as V1T  # noqa: E402  (its relabel and its constants, unchanged; nothing runs at import)
    raw, out = os.path.join(TOP, V1T.RAW_REL), os.path.join(TOP, V1T.OUT_REL)
    work = os.path.join(TOP, "build", "e178-desktest-work-a3")
    gone = (raw, os.path.join(TOP, "build", "e178-out"), work, os.path.join(TOP, "build", "e178-dropped-arms"))
    for d in gone:
        shutil.rmtree(d, ignore_errors=True)
    items = {it["name"]: it for it in E.load_items()}
    try:
        for po, pn in V1T.PASSMAP.items():
            V1T.relabel_pass(os.path.join(V1T.SRC, "aifoundry3", "e171", f"p{po}"), os.path.join(raw, "e178", f"p{pn}"), po, pn, items)
        shutil.copytree(os.path.join(V1T.SRC, "aifoundry3", "e171-smoke", "p17101"), os.path.join(raw, "e178-smoke", "p17801"))
        shutil.copytree(os.path.join(V1T.SRC, "aifoundry3", "e171-stoptest", "p17102"), os.path.join(raw, "e178-stoptest", "p17802"))
        os.makedirs(os.path.join(raw, "logs"))
        open(os.path.join(raw, "logs", "README.txt"), "w").write("desk test: no session logs\n")
        ren = {f"c-log-p{po}.jsonl": f"c-log-p{pn}.jsonl" for po, pn in V1T.PASSMAP.items()}
        ren["c-log-p17101.jsonl"] = "c-log-p17801.jsonl"
        v = json.load(open(os.path.join(V1T.SRC, "ccheck", "ccheck-all.json")))
        for x in v["launches"]:
            x["log"] = ren.get(x["log"], x["log"])
        os.makedirs(work)
        vf = os.path.join(work, "verdicts-relabelled.json")
        json.dump(v, open(vf, "w"))
        env = dict(os.environ, E178_DESKTEST="1", E178_CCHECK_STANDIN=os.path.join(HERE, "desktest_ccheck_standin_e178.py"),
                   E178_DESKTEST_VERDICTS=vf, E178_DATE="desktest", PY="/usr/bin/python3")
        env.pop("E178_DESKTEST_FAIL_REDUCE", None)
        env.pop("E178_DESKTEST_BREAK_JSON", None)
        r = subprocess.run(["nice", "-n", "10", "bash", os.path.join(HERE, "collect_e178_v2.sh"), V1T.RAW_REL], cwd=TOP, env=env,
                           capture_output=True, text=True, timeout=1500)
        log = (r.stdout + r.stderr).replace(TOP + os.sep, "").replace(TOP, "<repo>")
        okc = r.returncode == 0 and "results.md written" in log and "arms dropped: 0" in log
        o, why = None, ""
        if okc:
            try:
                o = read_session(CARD, os.path.join(out, "runs.csv"), os.path.join(out, "e178.json"), os.path.join(out, "scored.json"))
            except Refuse as e:
                why = f"refused, exit {e.code}: {e}"[:300]
        if o is None:
            check("T7 the kit's collector (collect_e178_v2.sh) on its relabelled real session, then the reader", False,
                  f"collector exit {r.returncode}, results.md written {'results.md written' in log}; {why}")
            return
        cc = o["cross_check_with_scored_json"]
        nread = sum(1 for e in o["contrasts"] if "mean_w" in (e.get("rail") or {}))
        ident = max(e["identity_max_abs_w"] for e in o["contrasts"] if "board" in e)
        # the card day's command line itself, as A3-4 gives it, into the work directory
        oj, om = os.path.join(work, "rail-arm-e178.json"), os.path.join(work, "rail-arm-e178.md")
        cli = subprocess.run([sys.executable, "-B", os.path.abspath(__file__), "read", "--runs-csv", os.path.join(V1T.OUT_REL, "runs.csv"),
                              "--reduction", os.path.join(V1T.OUT_REL, "e178.json"), "--scored", os.path.join(V1T.OUT_REL, "scored.json"),
                              "--json", oj, "--md", om], cwd=TOP, capture_output=True, text=True, timeout=300)
        same = os.path.exists(oj) and json.load(open(oj)) == json.loads(json.dumps(o, sort_keys=True))
        mdrows = sum(1 for ln in open(om) if ln.startswith("| ") and not ln.startswith("| contrast")) if os.path.exists(om) else 0
        leak = [x for x in (TOP, os.path.expanduser("~")) if x and os.path.exists(oj) and (x in open(oj).read() or x in open(om).read())]
        check("T7 the kit's collector (collect_e178_v2.sh) on its relabelled real session, then the reader",
              cc["ok"] and o["kept_passes"] == [17810, 17811, 17812, 17813] and o["consistency"]["ok"]
              and o["consistency"]["kept_runs_without_Drail"] == 0 and o["e178_c"]["applied"] and ident < 1e-12 and nread >= 40
              and cli.returncode == 0 and same and mdrows == 52 and not leak,
              f"collector exit 0, arms dropped 0; read with its runs.csv, e178.json and scored.json: kept passes {o['kept_passes']}, kept runs "
              f"{o['consistency']['kept_runs']} (every one with a Drail), runs.csv's per-pass means against e178.json to "
              f"{max(o['consistency']['max_abs_diff_w'].values()):.1e} W; E178-C applied (left out {o['e178_c']['c_excluded']}); the board "
              f"column reproduces scored.json's rules and reported pairs ({cc['n_differences']} differences); {nread} of 52 contrasts read on "
              f"the rail; board = rail + off to {ident:.1e} W; the command line of A3-4 (repo-relative paths): exit {cli.returncode}, its json "
              f"equal to the call's {same}, its md {mdrows} contrast rows, no desk path in either {not leak} (E171's tiles under E178's "
              f"labels: no figure of it is quoted)")
    finally:
        for d in gone:
            shutil.rmtree(d, ignore_errors=True)


# ------------------------------------------------------------------------------------------------- main
def main(argv):
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    f = sub.add_parser("freeze")
    f.add_argument("--check", action="store_true")
    r = sub.add_parser("read")
    r.add_argument("--runs-csv", required=True)
    r.add_argument("--reduction", required=True)
    r.add_argument("--scored")
    r.add_argument("--card", default=CARD)
    r.add_argument("--json")
    r.add_argument("--md")
    t = sub.add_parser("selftest")
    t.add_argument("--txt")
    t.add_argument("--json")
    t.add_argument("--no-collect", action="store_true")
    a = ap.parse_args(argv)
    try:
        if a.cmd == "freeze":
            pinned_check()
            js, txt, o = build_frozen()
            if a.check:
                ok = os.path.exists(FROZEN_JSON) and open(FROZEN_JSON).read() == js and os.path.exists(FROZEN_TXT) and open(FROZEN_TXT).read() == txt
                print("CHECK", "PASS" if ok else "FAIL", f"(rail-e178.json and rail-e178.txt, {len(o['contrasts'])} contrasts)")
                return 0 if ok else 1
            open(FROZEN_JSON, "w").write(js)
            open(FROZEN_TXT, "w").write(txt)
            print(txt, end="")
            return 0
        if a.cmd == "read":
            o = read_session(a.card, os.path.abspath(a.runs_csv), os.path.abspath(a.reduction), os.path.abspath(a.scored) if a.scored else None)
            if a.json:
                open(a.json, "w").write(json.dumps(o, indent=1, sort_keys=True) + "\n")
            if a.md:
                open(a.md, "w").write(markdown(o))
            h = {e["name"]: e for e in o["contrasts"]}.get("E178-H-int8", {})
            print("RAIL-E178 READ:", len(o["contrasts"]), "contrasts;", "H-int8 rail", fmt(h, "rail") if "rail" in h else h.get("left_out"))
            return 0
        return selftest(a)
    except Refuse as e:
        print(f"REFUSED (exit {e.code}): {e}")
        return e.code


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
