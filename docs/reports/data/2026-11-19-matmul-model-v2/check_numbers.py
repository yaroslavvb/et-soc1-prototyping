#!/usr/bin/env python3
"""The matmul model report, second version: the check. Every number of numbers.json is re-read from its committed source by this
script's own code, and every one must be printed in README.md where numbers.json says. Desk.

    /usr/bin/python3 -I -B check_numbers.py --repo <the lab's top> --numbers numbers.json --readme README.md [--out check-numbers.txt]

For each entry of numbers.json (written by make_figures.py) it:
  1. checks every pinned input's blob: the commit and path exist and the sha256 is the one numbers.json records;
  2. re-derives the value from the entry's source, independently of make_figures.py:
       json    the committed JSON value at the key path (times the scale, where one is given), formatted as printed;
       text    the committed literal must be in the committed file (markdown emphasis and code marks aside, whitespace collapsed), and
               the printed token one of the literal's numbers (commas aside) or the literal's own words;
       desk    the named function, recomputed here from the committed inputs (E213's errors, the gemmLnc ratios, the simulator ratios,
               the tensor-floor ratios, the mask spread, session sums, sums of JSON values, ranges over other cells);
       git     the commit's own committer time, Pacific;
       absent  the path does not exist at the commit;
  3. checks the README: the entry's phrase is in README.md (the same normalisation) and its printed token is in the phrase, entries that
     share a phrase found in their order;
  4. checks every 8-hex commit id the README cites in code marks: it is a commit of the repository, or a registered sealed-forecast prefix.
Then it lists every number of README.md that no phrase covers (dates, times, identifiers, section numbers), for a reader to judge.
It prints one line a check (PASS or FAIL, the key, the printed token, the value found, the source) and exits 1 on any FAIL.
Reads only; standard library only; git is called read-only.
SPDX-License-Identifier: Apache-2.0
"""
import argparse
import csv
import hashlib
import io
import json
import math
import os
import re
import statistics
import subprocess
import sys


def git_show(repo, commit, path):
    r = subprocess.run(["git", "-C", repo, "show", f"{commit}:{path}"], capture_output=True)
    return r.stdout if r.returncode == 0 else None


def clean(s):
    s = re.sub(r"(?m)^>[ ]?", "", s)
    return re.sub(r"\s+", " ", s.replace("**", "").replace("`", "")).strip()


def token_in(tok, s):
    if re.fullmatch(r"[0-9a-f]{8}", tok) and re.search(r"[a-f]", tok):
        return re.search(r"(?<![0-9A-Za-z])" + re.escape(tok) + r"(?![0-9A-Za-z])", s)
    if re.fullmatch(r"[-+0-9.,:/e x of]+", tok) and re.search(r"[0-9]", tok):
        m = re.search(r"(?<![0-9.])" + re.escape(tok) + r"(?![0-9])", s)
        if m or "," not in tok:
            return m
        return re.search(r"(?<![0-9.])" + re.escape(tok.replace(",", "")) + r"(?![0-9])", s.replace(",", ""))
    i = s.find(tok)
    return None if i < 0 else _Span(i, i + len(tok))


class _Span:
    def __init__(self, a, b):
        self.a, self.b = a, b

    def start(self):
        return self.a

    def end(self):
        return self.b


class Src:
    def __init__(self, repo, inputs):
        self.repo = repo
        self.inputs = inputs
        self.cache = {}

    def raw(self, commit, path):
        k = (commit, path)
        if k not in self.cache:
            self.cache[k] = git_show(self.repo, commit, path)
        return self.cache[k]

    def pin(self, name):
        i = self.inputs[name]
        return self.raw(i["commit"], i["path"])

    def pjson(self, name):
        return json.loads(self.pin(name))

    def pcsv(self, name):
        rows = csv.DictReader(io.StringIO(self.pin(name).decode("utf-8")))
        return {r["id"]: r for r in rows}


# ------------------------------------------------------------------------------------------------ the desk functions, recomputed
def num(x):
    if x is None or x == "":
        return None
    return float(x)


def e213_err_list(S, arm, model, q, conv, no_lnc):
    """this check's own reading of E213 (score_e213.py's definitions): the errors of one arm, model and quantity"""
    scores = S.pjson("e213%s_scores" % arm)["arms"][arm]
    pts = scores["measured"]
    own = S.pcsv("e213%s_%s" % (arm, model))
    v3 = S.pcsv("e213%s_v3" % arm)
    points = sorted(p for p, v in pts.items() if v["role"] == "point")
    errs = []

    def keep(p):
        return not (no_lnc and pts[p]["loop"] == "rgm136 gemmLnc")
    if q in ("wall", "mean", "t"):
        col = {"wall": "cycles_per_op_wall", "mean": "cycles_per_op_mean", "t": "seconds_per_gemm"}[q]
        mk = {"wall": "cw", "mean": "cm", "t": "t"}[q]
        by_case = {}
        for p in points:
            by_case.setdefault(pts[p]["case"], []).append(p)
        for case in sorted(by_case):
            ps = by_case[case]
            if not keep(ps[0]):
                continue
            m = sum(pts[p][mk] for p in ps) / len(ps)
            row = own.get(ps[0])
            f = num(row.get(col)) if row else None
            if not f:
                continue
            errs.append(f / m - 1 if conv == "fm" else m / f - 1)
        return errs
    for p in points:
        v = pts[p]
        r3 = v3.get(p)
        if v["W"] is None or r3 is None or num(r3.get("W_over_idle")) is None:
            continue
        watts = num(r3["W_over_idle"]) < 3.0 or v["W"] < 3.0
        r = own.get(p)
        if not r or num(r.get("W_over_idle")) is None or num(r.get("A_W")) is None or num(r.get("B_W_us")) is None:
            continue
        if not keep(p):
            continue
        w_given = num(r["A_W"]) + num(r["B_W_us"]) / (v["cw"] / 600.0)
        j_given = w_given * v["t"]
        if q == "Jg" and not watts:
            errs.append(j_given / v["J"] - 1 if conv == "fm" else v["J"] / j_given - 1)
        elif q == "Jf" and not watts:
            jf = num(r["J_over_idle_per_gemm"])
            errs.append(jf / v["J"] - 1 if conv == "fm" else v["J"] / jf - 1)
        elif q == "Jr":
            jr = v["prest"] * v["t"] + j_given
            errs.append(jr / v["Jrest"] - 1 if conv == "fm" else v["Jrest"] / jr - 1)
        elif q == "Wwatts" and watts:
            errs.append(w_given - v["W"])
    return errs


def d_e213(S, a):
    arms = ["A", "B"] if a["arm"] == "P" else [a["arm"]]
    errs = []
    for arm in arms:
        errs += e213_err_list(S, arm, a["model"], a["q"], a.get("conv", "fm"), a.get("no_lnc", False))
    sc = 1.0 if a["q"] == "Wwatts" else 100.0
    if a["stat"] == "n":
        return len(errs)
    if a["stat"] == "rms":
        return sc * math.sqrt(sum(e * e for e in errs) / len(errs))
    if a["stat"] == "bias":
        return sc * sum(errs) / len(errs)
    raise ValueError(a["stat"])


def e1_ratio(S, p):
    for arm in ("A", "B"):
        cells = S.pjson("e213%s_scores" % arm)["arms"][arm]["cells"]["E1"]
        for c in cells:
            if c["point"] == p:
                return c["measured"] / c["v3"]
    raise KeyError(p)


def d_ratio(S, a):
    v = [e1_ratio(S, p) for p in a["points"]]
    st = a["stat"]
    if st == "min":
        return min(v)
    if st == "max":
        return max(v)
    if st == "one":
        return v[0]
    if st == "mf_pct":
        return 100 * (v[0] - 1)
    if st == "fm_pct":
        return 100 * (1 / v[0] - 1)
    raise ValueError(st)


def sim_list(S, which):
    out = []
    if which in ("all", "E206-E207"):
        for x in S.pjson("v1_numbers")["timing"]["sim_ratio"]["values"]:
            out.append(x["ratio"] if isinstance(x, dict) else x)
    exps = (["e213"] if which in ("all", "E213") else []) + (["e215"] if which in ("all", "E215") and "e215A_scores" in S.inputs else [])
    for e in exps:
        for arm in ("A", "B"):
            if "%s%s_scores" % (e, arm) not in S.inputs:
                continue
            sc = S.pjson("%s%s_scores" % (e, arm))["arms"][arm]
            for p in sorted(sc["readings_REPORTED"]["timing_simulation"]):
                r = sc["readings_REPORTED"]["timing_simulation"][p]
                if r.get("cycles_gemm_over_sim_steps") is not None and sc["measured"][p]["role"] == "point":
                    out.append(r["cycles_gemm_over_sim_steps"])
    return out


def d_sim(S, a):
    v = sim_list(S, a["which"])
    return {"n": len(v), "min": min(v), "max": max(v), "median": statistics.median(v)}[a["stat"]]


def d_floor(S, a):
    v = []
    for arm in ("A", "B"):
        sc = S.pjson("e213%s_scores" % arm)["arms"][arm]
        for p, r in sc["readings_REPORTED"]["timing_simulation"].items():
            if r.get("counter_mean_over_floor") is not None and sc["measured"][p]["role"] == "point":
                v.append(r["counter_mean_over_floor"])
    return min(v) if a["stat"] == "min" else max(v)


def d_masks(S, a):
    return 100 * max(m["spread"] for m in S.pjson("e213A_scores")["arms"]["A"]["readings_REPORTED"]["masks"])


def d_sum_runs(S, a):
    t = 0
    for name in a["pins"]:
        first = S.pin(name).decode("utf-8").splitlines()[0]
        m = re.search(r"RAN FULL \((\d+) of \d+ runs\)", first)
        t += int(m.group(1))
    return t


def d_sum_cm(S, a):
    t = 0.0
    for name in a["pins"]:
        m = re.search(r"\*\*([0-9.]+) card-minutes\*\*", S.pin(name).decode("utf-8"))
        t += float(m.group(1))
    return t


def follow(x, ptr):
    for k in ptr:
        x = x[k]
    return x


def d_sum_json(S, a):
    d = S.pjson(a["pin"])
    return sum(follow(d, p) for p in a["pointers"])


def d_cells(S, a):
    out = []
    for c in a["cells"]:
        if c["kind"] == "json":
            out.append(follow(S.pjson(c["pin"]), c["pointer"]))
        else:
            out.append(DESK[c.get("fn", "e213")](S, c["args"]))
    return out


E215_GROUPS = {"registered": {"P", "C", "R"}, "posthoc": {"L", "S"}}


def e215_forecasts(S, arm):
    """this check's own reading of E215's frozen forecasts at one arm: {point: {model: {cw, cm, t, W, A, B, J}}}"""
    out = {}

    def put(pid, model, cw, cm, t, W, A, B, J):
        out.setdefault(pid, {})[model] = {"cw": cw, "cm": cm, "t": t, "W": W, "A": A, "B": B, "J": J}

    def csvrows(name):
        return list(csv.DictReader(io.StringIO(S.pin(name).decode("utf-8"))))
    if arm == "A":
        tokens = {p["id"]: p["source_token"] for p in S.pjson("e215_points")["arms"]["A"]["points"]}
        land = {}
        for q in S.pjson("e215A_land")["points"]:
            land[q["token"]] = q
        for pid, tok in tokens.items():
            for model in ("v31", "v3"):
                r = land[tok][model]
                wa = r.get("W_affine") or {}
                put(pid, model, r.get("cycles_per_op_wall"), r.get("cycles_per_op_mean"), r.get("seconds_per_gemm"), r.get("W_over_idle"),
                    wa.get("A_W"), wa.get("B_W_us"), r.get("J_over_idle_per_gemm"))
    names = {"A": [("e215A_v2", "v2")], "B": [("e215B_v31", "v31"), ("e215B_v3", "v3"), ("e215B_v2", "v2")]}[arm]
    card = {"A": "aifoundry3 card 0", "B": "aifoundry1 card 1"}[arm]
    for name, model in names + [("e215_t7", "t7")]:
        for r in csvrows(name):
            if name == "e215_t7" and r["card"] != card:
                continue
            put(r["id"], model, num(r["cycles_per_op_wall"]), num(r["cycles_per_op_mean"]), num(r["seconds_per_gemm"]),
                None if r["W_over_idle"] in ("", "NOT FORECAST") else num(r["W_over_idle"]),
                None if r["A_W"] in ("", "NOT FORECAST") else num(r["A_W"]), None if r["B_W_us"] in ("", "NOT FORECAST") else num(r["B_W_us"]),
                None if r["J_over_idle_per_gemm"] in ("", "NOT FORECAST") else num(r["J_over_idle_per_gemm"]))
    for r in csvrows("e215_lnc"):
        if r["arm"] == arm and r["role"].startswith("point"):
            put(r["id"], "lnc", None, None, None, num(r["lnc_W_over_idle"]), num(r["lnc_A_W"]), num(r["lnc_B_W_us"]), num(r["lnc_J_over_idle"]))
    for r in csvrows("e215_lay"):
        if r["e215_arm"] == arm and r["role"] == "point":
            put(r["id"], "lay", num(r["v31c_cycles_per_op_wall"]), None, num(r["v31c_seconds_per_gemm"]), None, None, None, None)
            put(r["id"], "lg1", num(r["REPORTED_G1_cycles_per_op_wall"]), None, None, None, None, None, None)
    if "e215_ctl" in S.inputs:
        for r in csvrows("e215_ctl"):
            if r["id"][0] == arm.lower() and r["id"] in out:
                put(r["id"], "cnt", num(r["REPORTED_N1+N2_cycles_per_op_wall"]), None, None, None, None, None, None)
    return out


def e215_err_list(S, arm, group, model, q, conv, only):
    """this check's own errors of one arm, group, model and quantity (score_e215.py's definitions; a watts point by MM1-v3.1's W or the
    measured W under 3 W); entries (key, error) so that the comparison against MM1-v3.1 can pair them"""
    meas = S.pjson("e215%s_scores" % arm)["arms"][arm]["measured"]
    F = e215_forecasts(S, arm)
    fams = E215_GROUPS[group]
    pts = sorted(p for p, v in meas.items() if v["role"] == "point" and v["family"] in fams)
    if only in ("L", "S", "P", "C", "R"):  # one family (report-v2-fix added S, P, C and R to L)
        pts = [p for p in pts if meas[p]["family"] == only]
    elif only == "lnc":
        pts = [p for p in pts if meas[p]["loop"] == "rgm136 gemmLnc"]
    elif only == "nolnc":
        pts = [p for p in pts if meas[p]["loop"] != "rgm136 gemmLnc"]
    out = []
    if q in ("wall", "mean", "t"):
        k = {"wall": "cw", "mean": "cm", "t": "t"}[q]
        by = {}
        for p in pts:
            if meas[p]["time_scored"]:
                by.setdefault(meas[p]["case"], []).append(p)
        for case in sorted(by):
            ps = by[case]
            m = sum(meas[p][k] for p in ps) / len(ps)
            f = (F.get(ps[0], {}).get(model) or {}).get(k)
            if f:
                out.append((case, f / m - 1 if conv == "fm" else m / f - 1))
        return out
    for p in pts:
        v = meas[p]
        f31 = F[p]["v31"]
        f = F[p].get(model) or {}
        if v["W"] is None or f31["W"] is None or f.get("W") is None or f.get("A") is None or f.get("B") is None:
            continue
        watts = f31["W"] < 3.0 or v["W"] < 3.0
        w_given = f["A"] + f["B"] / (v["cw"] / 600.0)
        j_given = w_given * v["t"]
        if q == "Wwatts" and watts:
            out.append((p, w_given - v["W"]))
        elif q == "Jg" and not watts:
            out.append((p, j_given / v["J"] - 1 if conv == "fm" else v["J"] / j_given - 1))
        elif q == "Jf" and not watts:
            out.append((p, f["J"] / v["J"] - 1 if conv == "fm" else v["J"] / f["J"] - 1))
        elif q == "Jr":
            jr = v["prest"] * v["t"] + j_given
            out.append((p, jr / v["Jrest"] - 1 if conv == "fm" else v["Jrest"] / jr - 1))
    return out


def d_e215(S, a):
    arms = ["A", "B"] if a["arm"] == "P" else [a["arm"]]
    errs = []
    for arm in arms:
        errs += [e for _, e in e215_err_list(S, arm, a["group"], a["model"], a["q"], a.get("conv", "fm"), a.get("only"))]
    sc = 1.0 if a["q"] == "Wwatts" else 100.0
    if a["stat"] == "n":
        return len(errs)
    if a["stat"] == "rms":
        return sc * math.sqrt(sum(e * e for e in errs) / len(errs))
    if a["stat"] == "bias":
        return sc * sum(errs) / len(errs)
    raise ValueError(a["stat"])


def d_e215c(S, a):
    """closer / farther / ties of a model against MM1-v3.1 (or the model named by 'base', report-v2-fix) with each arm's registered tie,
    and the exact two-sided sign test"""
    tiekey = {"wall": "cycles_ln", "mean": "cycles_ln", "t": "seconds_ln", "Jg": "joules_ln", "Jf": "joules_ln", "Wwatts": "watts_W"}[a["q"]]
    rules = S.pjson("e215_rules")
    c = f = t = 0
    for arm in (["A", "B"] if a["arm"] == "P" else [a["arm"]]):
        tie = rules["arms"][arm]["ties"][tiekey]
        base = dict(e215_err_list(S, arm, a["group"], a.get("base", "v31"), a["q"], "fm", a.get("only")))
        for key, e in e215_err_list(S, arm, a["group"], a["model"], a["q"], "fm", a.get("only")):
            if a["q"] == "Wwatts":
                d = abs(base[key]) - abs(e)
            else:
                d = abs(math.log(1 + base[key])) - abs(math.log(1 + e))
            if d > tie:
                c += 1
            elif d < -tie:
                f += 1
            else:
                t += 1
    if a["stat"] == "p":
        n, k = c + f, min(c, f)
        return min(1.0, 2 * sum(math.comb(n, i) for i in range(k + 1)) / 2 ** n) if n else 1.0
    return {"closer": c, "farther": f, "ties": t}[a["stat"]]


def d_e215one(S, a):
    """one E215 case's or point's error, % (W at a watts point)"""
    for key, e in e215_err_list(S, a["arm"], a["group"], a["model"], a["q"], a.get("conv", "fm"), None):
        if key == a["key"]:
            return (1.0 if a["q"] == "Wwatts" else 100.0) * e
    raise KeyError(a["key"])


def d_e215sw(S, a):
    sw = S.pjson("e215A_scores")["arms"]["A"]["readings_REPORTED"]["switch_route"]
    return max(abs(c["measured_W_ratio"] - c["models_W_ratio"]["MM1-v3.1"]) for i, c in enumerate(sw) if i != a["skip"])


def d_e215off(S, a):
    return -100 * S.pjson("e215%s_scores" % a["arm"])["arms"][a["arm"]]["day_offset_REPORTED"]["offset_W"]


def d_count_in_text(S, a):
    """how many times a pattern occurs in a pinned text between two markers (the text cleaned as the README check cleans it)"""
    tx = clean(S.pin(a["pin"]).decode("utf-8"))
    i = tx.index(a["between"][0]) + len(a["between"][0])
    return len(re.findall(a["pattern"], tx[i:tx.index(a["between"][1], i)]))


def d_e215miss(S, a):
    rules = S.pjson("e215_rules")
    n = 0
    for arm in (["A", "B"] if a["arm"] == "P" else [a["arm"]]):
        band = rules["arms"][arm]["bands"][a["rule"]]["band"]
        n += sum(1 for _, e in e215_err_list(S, arm, a["group"], a["model"], a["q"], "mf", a.get("only")) if abs(e) > band)
    return n


def d_e215pt(S, a):
    """one E215 point's measured / forecast (J over idle given the measured seconds) for a model"""
    arm = a["point"][0].upper()
    for key, e in e215_err_list(S, arm, a["group"], a["model"], "Jg", "mf", None):
        if key == a["point"]:
            return 1 + e
    raise KeyError(a["point"])


DESK = {"e213": d_e213, "ratio": d_ratio, "sim": d_sim, "floor": d_floor, "masks": d_masks, "sum_runs": d_sum_runs, "sum_cm": d_sum_cm,
        "sum_json": d_sum_json, "range_min": lambda S, a: min(d_cells(S, a)), "range_max": lambda S, a: max(d_cells(S, a)),
        "e215": d_e215, "e215c": d_e215c, "e215pt": d_e215pt, "e215one": d_e215one, "e215one_neg": lambda S, a: -d_e215one(S, a),
        "e215sw": d_e215sw, "e215off": d_e215off, "count_in_text": d_count_in_text, "e215miss": d_e215miss}


# ------------------------------------------------------------------------------------------------ the check
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", default=".")
    ap.add_argument("--numbers", required=True)
    ap.add_argument("--readme", required=True)
    ap.add_argument("--out", default=None)
    a = ap.parse_args()
    N = json.load(open(a.numbers))
    inputs = N["meta"]["inputs"]
    S = Src(a.repo, inputs)
    lines = []
    fails = 0

    def out(ok, what, tok, found, src):
        nonlocal fails
        if not ok:
            fails += 1
        lines.append(f"{'PASS' if ok else 'FAIL'} | {what} | {tok} | {found} | {src}")

    # 1. the pinned inputs
    for name, i in sorted(inputs.items()):
        b = S.raw(i["commit"], i["path"])
        got = hashlib.sha256(b).hexdigest() if b is not None else None
        out(got == i["sha256"], "input " + name, i["commit"], (got or "MISSING")[:16], i["path"])
    # 2. every value from its source
    for e in N["numbers"]:
        s = e["source"]
        k, tok = e["key"], e["printed"]
        try:
            if s["kind"] == "json":
                v = follow(json.loads(S.raw(s["commit"], s["path"])), s["pointer"])
                shown = s["fmt"].format(v * s["scale"] if s.get("scale") else v)
                out(shown == tok, k, tok, shown, f"{s['path']} @ {s['commit']} {'/'.join(map(str, s['pointer']))}")
            elif s["kind"] == "text":
                t = clean(S.raw(s["commit"], s["path"]).decode("utf-8"))
                lit = clean(s["literal"])
                ok = lit in t and token_in(tok, lit) is not None
                out(ok, k, tok if len(tok) < 60 else tok[:57] + "...", "literal found" if lit in t else "LITERAL NOT FOUND",
                    f"{s['path']} @ {s['commit']}")
            elif s["kind"] == "desk":
                v = DESK[s["fn"]](S, s["args"])
                shown = s["fmt"].format(v)
                same = (abs(v - e["value"]) <= 1e-9 * max(1.0, abs(v))) if isinstance(v, float) else (v == e["value"])
                out(shown == tok and same, k, tok, f"{shown} ({s['fn']})", ", ".join(f"{x['path']} @ {x['commit']}" for x in s["inputs"])[:200])
            elif s["kind"] == "git":
                r = subprocess.run(["git", "-C", a.repo, "log", "-1", "--format=%cd", "--date=format-local:" + s["fmt"], s["commit"]],
                                   capture_output=True, text=True, env=dict(os.environ, TZ=s["tz"]))
                out(r.stdout.strip() == tok, k, tok, r.stdout.strip(), f"git {s['commit']}")
            elif s["kind"] == "absent":
                r = subprocess.run(["git", "-C", a.repo, "ls-tree", "--name-only", s["commit"], s["path"]], capture_output=True, text=True)
                out(r.returncode == 0 and not r.stdout.strip(), k, tok, "absent" if not r.stdout.strip() else "PRESENT", f"{s['path']} @ {s['commit']}")
            else:
                out(False, k, tok, "unknown kind " + s["kind"], "")
        except Exception as ex:  # a broken source is a FAIL, never a skip
            out(False, k, tok, f"ERROR {type(ex).__name__}: {ex}", s.get("path", s.get("fn", "")))
    # 3. the README
    readme = open(a.readme, encoding="utf-8").read()
    R = clean(readme)
    spans = []
    groups = []
    for e in N["numbers"]:
        if groups and groups[-1][0] == e["phrase"]:
            groups[-1][1].append(e)
        else:
            groups.append((e["phrase"], [e]))
    for phrase, es in groups:
        ph = clean(phrase)
        at = R.find(ph)
        if at < 0:
            for e in es:
                out(False, "README " + e["key"], e["printed"][:40], "PHRASE NOT IN README", ph[:120])
            continue
        spans.append((at, at + len(ph)))
        cur = 0
        for e in es:
            m = token_in(e["printed"], ph[cur:])
            if m is None:
                out(False, "README " + e["key"], e["printed"][:40], "TOKEN NOT IN PHRASE (in order)", ph[:120])
            else:
                cur += m.end()
                out(True, "README " + e["key"], e["printed"][:40], "in phrase", ph[:80])
    # 4. commit ids in code marks
    seals = {e["printed"] for e in N["numbers"] if re.fullmatch(r"[0-9a-f]{8}", e["printed"] or "")}
    for cid in sorted(set(re.findall(r"`([0-9a-f]{8})`", readme))):
        r = subprocess.run(["git", "-C", a.repo, "cat-file", "-e", cid + "^{commit}"], capture_output=True)
        if r.returncode == 0:
            out(True, "commit " + cid, cid, "a commit", "git cat-file")
        else:
            out(cid in seals, "commit " + cid, cid, "a registered seal prefix" if cid in seals else "NOT A COMMIT", "git cat-file")
    # 5. the numbers no phrase covers
    covered = [False] * len(R)
    for x, y in spans:
        for i in range(x, y):
            covered[i] = True
    unc = []
    for m in re.finditer(r"(?<![A-Za-z0-9_.\-/])[+-]?\d+(?:[.,:]\d+)*%?(?![A-Za-z0-9_])", R):
        if not covered[m.start()]:
            unc.append(f"  {m.group(0)}  ...{R[max(0, m.start() - 40):m.end() + 20]}...")
    n_pass = sum(1 for ln in lines if ln.startswith("PASS"))
    head = [f"check_numbers: {len(lines)} checks, {n_pass} PASS, {fails} FAIL ({len(N['numbers'])} numbers in numbers.json)"]
    tail = [f"numbers of README.md that no phrase covers ({len(unc)}; dates, times, identifiers, rule and section numbers):"] + unc
    text = "\n".join(head + lines + [""] + tail) + "\n"
    if a.out:
        with open(a.out, "w") as f:
            f.write(text)
    print(head[0])
    for ln in lines:
        if ln.startswith("FAIL"):
            print(ln)
    return 1 if fails else 0


if __name__ == "__main__":
    sys.exit(main())
