#!/usr/bin/env python3
"""E178 (Q146(g); dated note A4, E178.md.dated-note-A4.md): the REPORTED minion-rail arm's reader, v2. It reads what dated note A3's
reader reads, by the same statistic, against the same frozen forecasts, and is never a verdict. A3's reader (rail_e178.py) stays as
committed: this file imports it unchanged (pinned below at its sha256) and uses its frozen forecasts, its contrast list, its session
checks and its statistic as they are. Four things differ, each fixing a fault of A3's verifier (railv-e178), before any E178 datum:

  A4-1  the self-test's T7 runs the kit's collector, which removes build/e178-out and build/e178-dropped-arms whole (so does A3's T7):
        here T7 looks first, and if either holds anything but the desk test's own output it does not run, removes nothing, and the
        self-test ends NOT COMPLETE (exit 4);
  A4-2  given scored.json of a session with fewer than 2 kept passes (the scorer's own NOT SCORED, with no reported pairs), the session
        reads NOT READ and the reader exits 0, where A3's refused (7) with a false reason; scored.json whose kept passes are not the
        reduction's, or that reads NOT SCORED beside 2 or more kept passes, or holds no reported pairs, still refuses 7, saying which;
  A4-3  a contrast holding a (pass, kind) one of whose kept runs has no Drail is flagged in both forms (rail_reads_the_board_runs
        false; the pairs named in runs_without_Drail), and in pass form its remainder is read, as A3-1 says, on the runs that have one:
        the mean over them of D - Drail (A3's reader took the board's mean over every kept run less the rail's mean over those);
  A4-4  the md table's board cell names the frozen P and, beside it, the scored dP that the scorer's SIZE was judged against; both
        outputs count the distinct readings: 52 contrasts, 48 distinct readings of 44 kind pairs.

On a session where every kept run has a Drail and 2 or more passes are kept, every figure this reader writes equals A3's reader's
(self-test V0, on synthetic sessions and on the kit's collector's output). Standard library only for check and read; the self-test's
scorer cases and T7 (the kit's collector) need the Intel's /usr/bin/python3, with numpy.

  check     python3 -B tools/claims-v3/e178/rail_e178_v2.py check
            A3's five pinned inputs, A3's reader at its sha256, rail-e178.json and .txt rebuilt byte for byte: CHECK PASS or exit 9
  read      python3 -B tools/claims-v3/e178/rail_e178_v2.py read --runs-csv <primary runs.csv> --reduction <primary e178.json>
                [--scored <scored.json>] [--card aifoundry3] [--json <out>] [--md <out>]
  selftest  /usr/bin/python3 -B tools/claims-v3/e178/rail_e178_v2.py selftest [--txt <out>] [--json <out>] [--no-collect]

EXIT (read): 0 written; 2 usage (a card other than aifoundry3); 6 the runs.csv and the reduction are not one session's (A3's check,
unchanged); 7 scored.json is not this session's (its kept passes, its NOT SCORED beside 2 or more kept passes, no reported pairs, or the
board column not reproduced); 9 a pinned input differs (A3's five, or A3's reader), or rail-e178.json is not reproduced from them.
EXIT (selftest): 0 every check passed; 1 a check failed; 4 every other check passed, but T7 did not run (its guard; nothing removed).
SPDX-License-Identifier: Apache-2.0
"""
import argparse
import csv
import json
import os
import shutil
import subprocess
import sys
import tempfile

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
TOP = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
if HERE not in sys.path:
    sys.path.insert(0, HERE)
import rail_e178 as V1  # noqa: E402  (dated note A3's reader, unchanged; nothing runs at import)

Refuse = V1.Refuse
CARD, COLS, TOL_W, TYPES = V1.CARD, V1.COLS, V1.TOL_W, V1.TYPES
V1_REL = "tools/claims-v3/e178/rail_e178.py"
V1_SHA256 = "c1d9e9aeeac4bf97a2b20c3aaa94d614cb26929057acc28f567ab728ace32122"
E172 = "docs/reports/data/2026-11-05-e172-blind8-card1"
# what the self-test reads besides A3's pinned inputs and A3's own self-test reads (committed; post hoc reads, never a forecast)
SELFTEST_READS_V2 = [V1.E171 + "/runs.csv", E172 + "/runs.csv", E172 + "/e172.json", "tools/claims-v3/e178/logs/selftest-rail-e178.json",
                     "tools/claims-v3/e178/score_e178.py", "tools/claims-v3/e178/selftest_collect_e178.py",
                     "tools/claims-v3/e178/collect_e178_v2.sh", "tools/claims-v3/e178/desktest_ccheck_standin_e178.py"]
NEVER = "reported beside the board verdicts, never a verdict (E178.md.dated-note-A3.md; read by dated note A4's reader v2)"
WORK_REL = os.path.join("build", "e178-desktest-work-a4")


def pinned_check(top=TOP):
    V1.pinned_check(top)
    p = os.path.join(top, V1_REL)
    have = V1.sha(p) if os.path.exists(p) else "missing"
    if have != V1_SHA256:
        raise Refuse(9, f"{V1_REL} (dated note A3's reader, imported by this one): sha256 {have[:12]} is not the pinned {V1_SHA256[:12]}")


def distinct(L):
    """A4-4: the contrast list's distinct readings (kind pair and form) and distinct kind pairs"""
    reads, pairs = {}, {}
    for c in L:
        reads.setdefault((c["a"], c["b"], c["form"]), []).append(c["name"])
        pairs.setdefault((c["a"], c["b"]), []).append(c["name"])
    both = [v for (a, b), v in pairs.items() if len({x["form"] for x in L if (x["a"], x["b"]) == (a, b)}) > 1]
    return {"contrasts": len(L), "distinct_readings": len(reads), "distinct_kind_pairs": len(pairs),
            "readings_repeated": [v for v in reads.values() if len(v) > 1], "pairs_read_in_both_forms": both}


# ------------------------------------------------------------------------------------------------- the session
def views(rows, res, no_rail):
    """A3's three columns (rail_e178.views, unchanged), with A3-1's words kept in pass form (A4-3): for a (pass, kind) one of whose kept
    runs has no Drail, the remainder is the mean, over the kept runs of it that have one, of D - Drail"""
    rv, pv = V1.views(rows, res)
    fixed = {}
    for key in sorted(no_rail):
        p, kind = key[1:].split(" ", 1)
        e = (pv["off"]["per_pass"].get(p) or {}).get(kind)
        if e is None:
            continue
        v = [r["D"] - r["Drail"] for r in rows if r["pass"] == int(p) and r["item"] == kind and r["D"] is not None and r["Drail"] is not None]
        e["D"] = sum(v) / len(v) if v else None
        fixed[key] = e["D"]
    return rv, pv, fixed


def read_contrast(c, fz, rv, pv, res, passes, excluded, no_rail):
    out = V1.read_contrast(c, fz, rv, pv, res, passes, excluded)
    if "left_out" in out:
        return out
    hit = sorted({f"p{p} {k}" for p in passes for k in (c["a"], c["b"])} & set(no_rail))
    out["runs_without_Drail"] = hit
    if hit:
        out["rail_reads_the_board_runs"] = False
    return out


def scorer_state(sj, passes):
    """A4-2: what scored.json's primary says the scorer read; refuses (7) where it cannot be this session's"""
    pr = sj.get("primary") or {}
    kp = pr.get("kept_passes")
    if kp is not None and [int(x) for x in kp] != list(passes):
        raise Refuse(7, f"scored.json's primary kept passes {[int(x) for x in kp]}, the reduction's {list(passes)}: the files are not one "
                        f"session's")
    if "reported" in pr:
        return {"given": True, "scored": True}
    if pr.get("NOT SCORED") and len(passes) < 2:
        return {"given": True, "scored": False, "why": f"the scorer's own NOT SCORED: {pr['NOT SCORED']}"}
    if pr.get("NOT SCORED"):
        raise Refuse(7, f"scored.json's primary reads NOT SCORED ({pr['NOT SCORED']}) beside the reduction's {len(passes)} kept passes: the "
                        f"files are not one session's")
    raise Refuse(7, "scored.json's primary holds no reported pairs and does not read NOT SCORED: it is not the scorer's output for this "
                    "session")


def scorer_board(sj, c):
    """A3's (rail_e178.scorer_board), with the scored dP and dF the scorer's SIZE was judged against (A4-4)"""
    sb = V1.scorer_board(sj, c)
    if sb is None or "mismatch" in sb:
        return sb
    pr = sj.get("primary") or {}
    if c["group"] == "rule" or c["name"] == "beside: 127 - neg_ones":
        src = (pr.get("rules") or {}).get(c["name"]) or {}
    else:
        lst = ((pr.get("reported") or {}).get("pairs") or {}).get(c["group"][len("reported: "):]) or []
        src = lst[c["index"]] if c.get("index") is not None and c["index"] < len(lst) else {}
    return dict(sb, dP_w=src.get("dP_w"), dF_w=src.get("dF_w"))


def cross_check(sj, c, mine, sc):
    """A3's cross-check of the board column against the scorer (rail_e178.cross_check, unchanged) where the scorer scored; where it did
    not (fewer than 2 kept passes, A4-2), nothing is compared, the rules' NOT SCORED is carried, and no column may read a value"""
    if sc["scored"]:
        d, _ = V1.cross_check(sj, c, mine)
        return d, scorer_board(sj, c)
    if c["group"] == "rule" or c["name"] == "beside: 127 - neg_ones":
        sb = V1.scorer_board(sj, c)
        if sb.get("verdict") is None:
            sb = {"scorer": sc["why"]}
    else:
        sb = {"scorer": sc["why"]} if c["group"].startswith("reported: ") else None
    bad = [f"{c['name']}: the {col} column reads a value where the scorer did not score" for col in COLS if "mean_w" in (mine.get(col) or {})]
    return bad, sb


def read_session(card, csv_path, red_path, scored_path=None, frozen_paths=(V1.FROZEN_JSON, V1.FROZEN_TXT)):
    if card != CARD:
        raise Refuse(2, f"the arm is frozen for {CARD} only, not {card}: card 1 has no E178 kit, and its arm needs its own dated note")
    pinned_check()
    ok, fz = V1.frozen_ok(*frozen_paths)
    if not ok:
        raise Refuse(9, "rail-e178.json or rail-e178.txt is not reproduced from the pinned inputs: refusing")
    rows, res = V1.load_runs(csv_path), json.load(open(red_path))
    cons = V1.consistency(rows, res)
    if not cons["ok"]:
        raise Refuse(6, "runs.csv and the reduction are not one session's: " + json.dumps({k: cons[k] for k in (
            "kept_passes_reduction", "kept_passes_runs_csv", "max_abs_diff_w", "missing")})[:600])
    passes = cons["kept_passes_reduction"]
    sj = json.load(open(scored_path)) if scored_path else None
    sc = scorer_state(sj, passes) if sj is not None else {"given": False}
    excluded = set(((sj or {}).get("primary") or {}).get("rules", {}).get("E178-C", {}).get("c_excluded") or []) if sj else set()
    no_rail = cons["pass_kinds_with_a_run_without_Drail"]
    rv, pv, fixed = views(rows, res, no_rail)
    L = V1.contrast_list(json.load(open(os.path.join(HERE, "forecast-e178.json"))))
    out = {"_note": "E178 (dated note A3): the reported minion-rail arm, read by rail_e178_v2.py (dated note A4); " + NEVER, "run": "E178",
           "card": card, "reader": "rail_e178_v2.py (dated note A4)", "reader_sha256": V1.sha(os.path.abspath(__file__)),
           "reader_a3": {"file": V1_REL, "sha256": V1_SHA256},
           "inputs": {"runs_csv": V1.rel(csv_path), "runs_csv_sha256": V1.sha(csv_path), "reduction": V1.rel(red_path),
                      "reduction_sha256": V1.sha(red_path), "scored": V1.rel(scored_path) if scored_path else None,
                      "scored_sha256": V1.sha(scored_path) if scored_path else None},
           "frozen": {"rail_e178_json_sha256": V1.sha(frozen_paths[0]), "ratio": {t: fz["ratio"][t]["median"] for t in TYPES}},
           "kept_passes": passes, "consistency": cons,
           "e178_c": ({"applied": True, "c_excluded": sorted(excluded), "reported_pairs": "a pair holding a kind E178-C left out is not read; "
                       "the scorer still computes it and marks it c_kept false"} if sj else
                      {"applied": False, "why": "no scored.json given: every kind is read"}),
           "scorer": sc, "distinct": distinct(L),
           "pass_form_remainder_on_runs_with_a_Drail": fixed, "contrasts": []}
    if len(passes) < 2:
        out["NOT READ"] = f"{len(passes)} kept passes, fewer than 2" + (f" ({sc['why']})" if sc.get("scored") is False else "")
    diffs = []
    for c, f in zip(L, fz["contrasts"]):
        if (c["a"], c["b"], c["name"]) != (f["a"], f["b"], f["name"]):
            raise Refuse(9, f"the contrast list and rail-e178.json differ at {c['name']}")
        e = read_contrast(c, f, rv, pv, res, passes, excluded, no_rail)
        if sj is not None:
            d, sb = cross_check(sj, c, e, sc)
            diffs += d
            if sb is not None:
                e["scorer_board"] = sb
        out["contrasts"].append(e)
    cm = {e["name"]: e for e in out["contrasts"]}
    a22 = []
    if all(n in cm and "board" in cm[n] for n in ("E178-S-int8", "beside: 127 - neg_ones", V1.A2_2[0])):
        for col in COLS:
            x, y, z = (cm[n][col]["per_pass"] for n in ("E178-S-int8", "beside: 127 - neg_ones", V1.A2_2[0]))
            a22 += [abs(x[p] - y[p] - z[p]) for p in z if p in x and p in y]
    out["a2_2_identity_max_abs_w"] = max(a22, default=None)
    out["flagged"] = [e["name"] for e in out["contrasts"] if e.get("runs_without_Drail")]
    if sj is not None:
        out["cross_check_with_scored_json"] = {"ok": not diffs, "differences": diffs[:40], "n_differences": len(diffs),
                                               "scorer_scored": sc["scored"]}
        if diffs:
            raise Refuse(7, "the board column does not reproduce scored.json (the files are not one session's): " + "; ".join(diffs[:6]))
    return out


def fmt(e, col):
    x = e.get(col) or {}
    if "mean_w" not in x:
        return x.get("reading", "")
    s = f"{x['mean_w']:+.4f} [{x['lo95_w']:+.4f}, {x['hi95_w']:+.4f}]"
    if col != "board":
        return s + (f"; forecast {e['forecast_w'][col]['P_w']:+.4f} (P) {x['forecast_P_is']}, {e['forecast_w'][col]['F_w']:+.4f} (F) "
                    f"{x['forecast_F_is']}; {x['interval_reads']}")
    dp = (e.get("scorer_board") or {}).get("dP_w")
    return s + f" (frozen P {e['forecast_w']['board']['P_w']:+.4f}" + (f"; scored dP {float(dp):+.4f}" if dp is not None else "") + ")"


def markdown(o):
    d = o["distinct"]
    L = [f"# E178 on {o['card']}: the reported minion-rail arm (dated note A3, read by rail_e178_v2.py of dated note A4), never a verdict", "",
         f"runs.csv {o['inputs']['runs_csv_sha256'][:12]}, e178.json {o['inputs']['reduction_sha256'][:12]}, scored.json "
         f"{(o['inputs']['scored_sha256'] or 'not given')[:12]}; kept passes {o['kept_passes']}; kept runs {o['consistency']['kept_runs']}, "
         f"of them without a Drail {o['consistency']['kept_runs_without_Drail']}; E178-C "
         + (f"applied (left out: {o['e178_c']['c_excluded']})" if o["e178_c"]["applied"] else "not applied (no scored.json)") + "."
         + (f" NOT READ: {o['NOT READ']}." if o.get("NOT READ") else ""), "",
         "The frozen forecasts (rail-e178.json, dated note A3): the registered board forecast times E171's median Drail/D for the format, "
         + ", ".join(f"{t} {v:.4f}" for t, v in o["frozen"]["ratio"].items()) + ", on the minion rail; times one less it off the rail. "
         "Each interval is the scorer's statistic, m +- t(0.975, n - 1) sd / sqrt(n) over the kept passes. The board column is the "
         "scorer's own reading, and its verdicts are the scorer's (results.md); its frozen P is forecast-e178.json's, and its scored dP "
         "(P x s x rate / E171's rate, scored.json's) is the one the scorer's SIZE was judged against.", "",
         f"{d['contrasts']} contrasts: {d['distinct_readings']} distinct readings of {d['distinct_kind_pairs']} kind pairs (repeated "
         f"readings: {'; '.join(' = '.join(v) for v in d['readings_repeated'])}; read in both forms: "
         f"{'; '.join(' and '.join(v) for v in d['pairs_read_in_both_forms'])}).", "",
         "| contrast | the scorer's verdict | board D, W | minion rail Drail, W | off the minion rail, D - Drail, W | n | every kept run has a "
         "Drail |", "|---|---|---|---|---|---|---|"]
    for e in o["contrasts"]:
        sb = e.get("scorer_board") or {}
        if "verdict" in sb:
            v = str(sb.get("verdict")) + (f" / SIZE {sb.get('size')}" if sb.get("size") else "")
        elif "sign" in sb:
            v = f"sign {sb.get('sign')}, P inside {sb.get('P_inside')}"
        else:
            v = sb.get("scorer", "")
        if "left_out" in e:
            L.append(f"| {e['name']} | {v} | {e['left_out']} | | | | |")
            continue
        fl = "yes" if not e.get("runs_without_Drail") else "no: " + ", ".join(e["runs_without_Drail"])
        L.append(f"| {e['name']} | {v} | {fmt(e, 'board')} | {fmt(e, 'rail')} | {fmt(e, 'off')} | {e['board']['n']} | {fl} |")
    L += ["", "Reported beside the board verdicts, never a verdict. A2-2's identity (85 - 127 = S-int8 less 127 - neg_ones, per pass): "
              f"{o.get('a2_2_identity_max_abs_w')} W at most. A contrast with 'no' in the last column holds a kept run without a Drail: its "
              "rail and its remainder are read on the runs that have one, its board on every kept run (rail_reads_the_board_runs false)."]
    if o["e178_c"]["applied"]:
        L.append("E178-C: a contrast holding a kind it left out is not read here; the scorer still computes such reported pairs and marks "
                 "them c_kept false.")
    return "\n".join(L) + "\n"


# ------------------------------------------------------------------------------------------------- the self-test
LINES, RES = [], {}


def check(name, ok, detail):
    RES[name] = {"pass": bool(ok), "detail": detail}
    LINES.append(f"{name}: {'PASS' if ok else 'FAIL'} - {detail}")


def subset_equal(a, b, skip=("_note", "reader_sha256"), path=""):
    """every key of A3's output (a) is in v2's (b) with the same value, but the keys named in skip; returns the first difference"""
    if isinstance(a, dict):
        if not isinstance(b, dict):
            return path or "/"
        for k, v in a.items():
            if path == "" and k in skip:
                continue
            if k not in b:
                return f"{path}/{k} missing"
            r = subset_equal(v, b[k], skip, f"{path}/{k}")
            if r:
                return r
        return None
    if isinstance(a, list):
        if not isinstance(b, list) or len(a) != len(b):
            return f"{path} length"
        for i, (x, y) in enumerate(zip(a, b)):
            r = subset_equal(x, y, skip, f"{path}[{i}]")
            if r:
                return r
        return None
    return None if a == b else f"{path}: {a!r} against {b!r}"


def t7_guard(top=TOP):
    """A4-1: what T7, and the kit's collector it runs, would remove that is not the desk test's own: build/e178-out holding anything but
    the desk test's output directory, or build/e178-dropped-arms holding anything. An empty list: T7 may run"""
    import selftest_collect_e178 as V1T  # noqa: E402  (its constants, unchanged; nothing runs at import)
    own = os.path.basename(V1T.OUT_REL)
    found = []
    for d, keep in ((os.path.join("build", "e178-out"), own), (os.path.join("build", "e178-dropped-arms"), None)):
        p = os.path.join(top, d)
        if os.path.isdir(p) and not os.path.islink(p):
            found += [os.path.join(d, x) for x in sorted(os.listdir(p)) if x != keep]
        elif os.path.lexists(p):
            found.append(d)
    return found


def real_scored(tmp, name, csv_path, red_path, excluded=(), s_float=1.0, mutate=None):
    """the REAL scorer's score_reduction on a session (its scale given, so no predictor is read), wrapped as score_session wraps it"""
    s = V1.S()
    import e178_common as E  # noqa: E402
    ok = [t for t in E.E178_NAMES if t not in excluded]
    prim = s.score_reduction(CARD, red_path, csv_path, ok, scale={"s_float": s_float, "anchors_used": [], "note": "self-test: scale given"})
    kc = {"verdict": "FAIL" if excluded else "PASS", "c_excluded": sorted(excluded)}
    prim["rules"] = dict({"E178-C": kc}, **prim.get("rules", {}))
    prim["verdicts"] = dict({"E178-C": kc["verdict"]}, **prim.get("verdicts", {}))
    sj = {"primary": prim, "verdicts": prim["verdicts"]}
    if mutate:
        mutate(sj)
    p = os.path.join(tmp, f"{name}-scored.json")
    open(p, "w").write(json.dumps(sj, indent=1, sort_keys=True, default=str) + "\n")
    return p, sj


def refused(fn, *a):
    try:
        fn(*a)
        return 0, ""
    except Refuse as e:
        return e.code, str(e)


def selftest(a):
    import e178_common as E  # noqa: E402
    # T1 the pinned inputs, A3's reader, the frozen files
    code, why = refused(pinned_check)
    f_ok, fz = V1.frozen_ok()
    check("T1 A3's five pinned inputs, A3's reader at its sha256, rail-e178.json and .txt rebuilt from them", code == 0 and f_ok
          and len(fz["contrasts"]) == 52,
          f"pinned: {'match' if code == 0 else why}; A3's reader {V1_SHA256[:12]}; rail-e178.json and .txt byte for byte: {f_ok}; "
          f"{len(fz['contrasts'])} contrasts; ratios " + ", ".join(f"{t} {fz['ratio'][t]['median']:.6f}" for t in TYPES))
    # T2 A3's committed post hoc readings, re-made through this reader's path
    committed = json.load(open(os.path.join(HERE, "logs", "selftest-rail-e178.json")))
    e171 = json.load(open(os.path.join(TOP, V1.E171, "e171.json")))
    rows171 = V1.load_runs(os.path.join(TOP, V1.E171, "runs.csv"))
    cons171 = V1.consistency(rows171, e171)
    rv, pv, fx = views(rows171, e171, cons171["pass_kinds_with_a_run_without_Drail"])
    t4, n4 = {}, 0
    for a_, b_, form in (("fp32.randn", "fp32.zeros", "couple"), ("fp16.randn", "fp16.zeros", "couple"), ("int8.full", "int8.zeros", "couple"),
                         ("fp32.anchor8_randn_a_989b8a", "fp32.anchor8_randn_b_833ac3", "pass"),
                         ("fp16.anchor8_randn_a_8c7827", "fp16.anchor8_randn_b_3a0fef", "pass"),
                         ("int8.anchor8_full_a_4aac84", "int8.anchor8_full_b_935710", "pass")):
        c = {"name": f"{a_} - {b_}", "group": "selftest", "form": form, "a": a_, "b": b_}
        e = read_contrast(c, {"type": a_.split(".")[0], **{col: {"P_w": 0.0, "F_w": 0.0} for col in COLS}}, rv, pv, e171, e171["passes"],
                          set(), cons171["pass_kinds_with_a_run_without_Drail"])
        t4[c["name"]] = dict({col: e[col]["halfwidth_w"] for col in COLS}, mean={col: e[col]["mean_w"] for col in COLS})
        n4 += int(e["rail_reads_the_board_runs"] and not e["runs_without_Drail"])
    an = json.load(open(os.path.join(TOP, "docs/reports/data/2026-11-05-q145a-anatomy-top-lines/anatomy.json")))
    red = {s_: json.load(open(os.path.join(TOP, f"docs/reports/data/2026-11-03-q139u-footing/reduced/{s_.lower()}-footing.json")))
           for s_ in ("E78", "E82")}
    i8 = {}
    for tp in an["tensor_pairs"]:
        if tp["a"] != "int8.neg_ones":
            continue
        rs = red[tp["session"]]
        _, pv5, _ = views([], rs, [])
        c = {"name": f"{tp['session']} {tp['a']} - {tp['b']}", "group": "selftest", "form": "pass", "a": tp["a"], "b": tp["b"]}
        e = read_contrast(c, {"type": "", **{col: {"P_w": 0.0, "F_w": 0.0} for col in COLS}}, {}, pv5, rs, [int(p) for p in rs["passes"]],
                          set(), [])
        i8[tp["session"]] = {col: [e[col]["mean_w"], e[col]["halfwidth_w"]] for col in COLS}
    same4 = t4 == committed["T4_halfwidths_e171_post_hoc"]
    same5 = i8 == committed["T5_int8_minus1_against_1"]
    check("T2 A3's committed post hoc readings re-made through this reader (logs/selftest-rail-e178.json T4 and T5)", same4 and same5
          and n4 == 6 and cons171["ok"] and cons171["kept_runs_without_Drail"] == 0 and not fx,
          f"E171's six contrasts (three couples, three same-format pairs): every mean and half-width equal to A3's committed figures: "
          f"{same4}; int8 -1 against 1 on E78 and E82 (the anatomy's pairs): equal: {same5} (E78 rail {i8['E78']['rail'][0]:+.4f} +- "
          f"{i8['E78']['rail'][1]:.4f} W, board {i8['E78']['board'][0]:+.4f} +- {i8['E78']['board'][1]:.4f} W); E171's {cons171['kept_runs']} "
          f"kept runs all with a Drail; none of the six flagged")
    # T3 the committed sessions through read: E171's (no E178 kind: every contrast NOT READ) and E172's consistency (a set-aside pass)
    o171 = read_session(CARD, os.path.join(TOP, V1.E171, "runs.csv"), os.path.join(TOP, V1.E171, "e171.json"))
    o171v1 = V1.read_session(CARD, os.path.join(TOP, V1.E171, "runs.csv"), os.path.join(TOP, V1.E171, "e171.json"))
    nr = sum(1 for e in o171["contrasts"] if all(e[col].get("reading", "").startswith("NOT READ") for col in COLS))
    e172 = json.load(open(os.path.join(TOP, E172, "e172.json")))
    c172 = V1.consistency(V1.load_runs(os.path.join(TOP, E172, "runs.csv")), e172)
    d171 = subset_equal(o171v1, o171)
    check("T3 E171's and E172's committed sessions", nr == 52 and d171 is None and c172["ok"] and c172["kept_passes_reduction"] == [17210, 17211, 17212]
          and [x["pass"] for x in e172.get("passes_set_aside", [])] == [17213],
          f"E171 read: 52 contrasts, {nr} NOT READ (E171 holds no E178 kind), every figure A3's reader writes equal here: {d171 is None}; "
          f"E172 (pass 17213 set aside, its rows without a D): runs.csv against e172.json over {c172['compared']} entries, D to "
          f"{c172['max_abs_diff_w']['D']:.1e} W, Drail to {c172['max_abs_diff_w']['Drail']:.1e} W, kept passes {c172['kept_passes_reduction']}")
    # W2 the distinct readings
    L = V1.contrast_list(json.load(open(os.path.join(HERE, "forecast-e178.json"))))
    dd = distinct(L)
    check("W2 the contrast list's distinct readings (A4-4)", (dd["contrasts"], dd["distinct_readings"], dd["distinct_kind_pairs"]) == (52, 48, 44)
          and len(dd["readings_repeated"]) == 4 and len(dd["pairs_read_in_both_forms"]) == 4,
          f"{dd['contrasts']} contrasts, {dd['distinct_readings']} distinct readings of {dd['distinct_kind_pairs']} kind pairs; repeated: "
          + "; ".join(" = ".join(v) for v in dd["readings_repeated"]) + "; read in both forms: "
          + "; ".join(" and ".join(v) for v in dd["pairs_read_in_both_forms"]))
    fcj = json.load(open(os.path.join(HERE, "forecast-e178.json")))
    q = {t: fz["ratio"][t]["median"] for t in TYPES}
    Pk = {k: v["P_w"][V1.CD] for k, v in fcj["kinds"].items()}

    def p_truth(n):
        t = n.split(".")[0] if "." in n else "fp32"
        b = Pk.get(n, 0.0)
        return b * q[t], b * (1 - q[t])

    def flat_rail(n):
        t = n.split(".")[0] if "." in n else "fp32"
        b = Pk.get(n, 0.0)
        return (1.70 * q[t], b - 1.70 * q[t]) if t == "int8" else (b * q[t], b * (1 - q[t]))

    tmp = tempfile.mkdtemp(prefix="rail-e178-v2-selftest-")
    try:
        # V0 v2 = A3's reader where every kept run has a Drail: S1's session with the scorer's readings, and the real scorer's
        c1, r1 = V1.synth(tmp, "s1", p_truth, 17831)
        sc1 = V1.synth_scored(tmp, "s1", c1, r1)
        o1, o1v1 = read_session(CARD, c1, r1, sc1), V1.read_session(CARD, c1, r1, sc1)
        sc1r, _ = real_scored(tmp, "s1r", c1, r1)
        o1r, o1rv1 = read_session(CARD, c1, r1, sc1r), V1.read_session(CARD, c1, r1, sc1r)
        dv0, dv0r = subset_equal(o1v1, o1), subset_equal(o1rv1, o1r)
        hh = {e["name"]: e for e in o1["contrasts"]}["E178-H-int8"]
        check("V0 every figure A3's reader writes, equal here, where every kept run has a Drail", dv0 is None and dv0r is None
              and o1["cross_check_with_scored_json"]["ok"] and o1r["cross_check_with_scored_json"]["n_differences"] == 0 and not o1["flagged"]
              and sum(1 for e in o1r["contrasts"] if "mean_w" in (e.get("rail") or {})) == 52,
              f"S1's session (the forecast true; the scorer's readings by its functions): {'equal' if dv0 is None else dv0}; the same session "
              f"scored by the REAL score_e178.score_reduction: {'equal' if dv0r is None else dv0r}, 0 differences against it, 52 of 52 read on "
              f"the rail; H-int8 rail {hh['rail']['mean_w']:+.4f} [{hh['rail']['lo95_w']:+.4f}, {hh['rail']['hi95_w']:+.4f}] W "
              f"{hh['rail']['interval_reads']}; flagged 0")
        # F2 fewer than 2 kept passes with the scorer's own scored.json (A4-2)
        c2, r2 = V1.synth(tmp, "f2", p_truth, 17891, passes=(17810,))
        sc2, sj2 = real_scored(tmp, "f2", c2, r2)
        x1, w1 = refused(V1.read_session, CARD, c2, r2, sc2)
        o2 = read_session(CARD, c2, r2, sc2)
        nr2 = sum(1 for e in o2["contrasts"] if all(e[col].get("reading", "").startswith("NOT READ") for col in COLS))
        rules_ns = sum(1 for e in o2["contrasts"] if (e.get("scorer_board") or {}).get("verdict") == "NOT SCORED")
        oj, om = os.path.join(tmp, "f2-out.json"), os.path.join(tmp, "f2-out.md")
        cli = subprocess.run([sys.executable, "-B", os.path.abspath(__file__), "read", "--runs-csv", c2, "--reduction", r2, "--scored", sc2,
                              "--json", oj, "--md", om], cwd=TOP, capture_output=True, text=True, timeout=300)
        check("F2a one kept pass, with the REAL scorer's scored.json (fault 2)", x1 == 7 and "reported" not in sj2["primary"]
              and "NOT SCORED" in sj2["primary"] and nr2 == 52 and o2.get("NOT READ", "").startswith("1 kept passes, fewer than 2 (the scorer's own")
              and o2["cross_check_with_scored_json"]["ok"] and rules_ns == 5 and cli.returncode == 0 and os.path.exists(om),
              f"A3's reader refuses {x1} ('{w1[:90]}...'); this reader: '{o2.get('NOT READ')}', {nr2} of 52 NOT READ in all three columns, the "
              f"rules' scorer verdict NOT SCORED carried on {rules_ns}, cross-check ok; the CLI with --scored exits {cli.returncode} and writes "
              f"the md: {os.path.exists(om)}")
        # a two-pass session with one pass set aside, its rows kept in runs.csv without a D or a Drail, as E172's set-aside pass is
        cs, rs = V1.synth(tmp, "f2s", p_truth, 17894, passes=(17810, 17811))
        red_s = json.load(open(rs))
        red_s["passes"] = [17810]
        red_s["per_pass"].pop("17811")
        red_s["passes_set_aside"] = [{"pass": 17811, "why": "self-test: set aside"}]
        json.dump(red_s, open(rs, "w"))
        rows_s = list(csv.DictReader(open(cs, newline="")))
        for r_ in rows_s:
            if r_["pass"] == "17811":
                r_["D"], r_["Drail"] = "", ""
        with open(cs, "w", newline="") as f:
            w = csv.DictWriter(f, fieldnames=list(rows_s[0].keys()))
            w.writeheader()
            w.writerows(rows_s)
        scs, sjs = real_scored(tmp, "f2s", cs, rs)
        xs1, _ = refused(V1.read_session, CARD, cs, rs, scs)
        os_ = read_session(CARD, cs, rs, scs)
        check("F2c a two-pass session with one pass set aside, with the REAL scorer's scored.json (fault 2, the verifier's case)",
              xs1 == 7 and sjs["primary"].get("set_aside") == [{"pass": 17811, "why": "self-test: set aside"}]
              and os_.get("NOT READ", "").startswith("1 kept passes, fewer than 2") and os_["kept_passes"] == [17810]
              and os_["consistency"]["ok"] and os_["cross_check_with_scored_json"]["ok"],
              f"A3's reader refuses {xs1}; this reader: kept passes {os_['kept_passes']} (17811 set aside, its "
              f"{sum(1 for r_ in rows_s if r_['pass'] == '17811')} rows without a D), '{os_.get('NOT READ')}', exit 0")
        c3, r3 = V1.synth(tmp, "f2b", p_truth, 17892, passes=(17810, 17811))
        sc3, _ = real_scored(tmp, "f2b", c3, r3)
        o3 = read_session(CARD, c3, r3, sc3)
        c4, r4 = V1.synth(tmp, "f2c", p_truth, 17893)
        x4, w4 = refused(read_session, CARD, c4, r4, sc2)

        def drop_kept(sj):
            sj["primary"].pop("kept_passes", None)

        sc5, _ = real_scored(tmp, "f2e", c2, r2, mutate=drop_kept)
        x5, w5 = refused(read_session, CARD, c4, r4, sc5)
        sc6, _ = real_scored(tmp, "f2f", c4, r4, mutate=lambda sj: (sj["primary"].pop("reported"), sj["primary"].pop("kept_passes")))
        x6, w6 = refused(read_session, CARD, c4, r4, sc6)
        check("F2b two kept passes read against the scorer; a scored.json that is not this session's still refuses 7, saying which",
              o3["cross_check_with_scored_json"]["n_differences"] == 0 and x4 == 7 and "kept passes [17810]" in w4 and x5 == 7
              and "NOT SCORED" in w5 and "beside the reduction's 4 kept passes" in w5 and x6 == 7 and "no reported pairs" in w6,
              f"two passes, the real scorer: {o3['cross_check_with_scored_json']['n_differences']} differences; the one-pass scored.json beside "
              f"a four-pass session: exit {x4} ('{w4[:100]}'); the same without its kept_passes: exit {x5} ('{w5[:110]}'); a four-pass "
              f"scored.json with no reported pairs: exit {x6}")
        # F3 a kept run without a Drail, read in both forms (A4-3)
        drop = (17811, "int8.e178_v5", 1)
        c7, r7 = V1.synth(tmp, "f3", p_truth, 17833, drop_rail=drop)
        o7, o7v1 = read_session(CARD, c7, r7), V1.read_session(CARD, c7, r7)
        holds = sorted(e["name"] for e in o7["contrasts"] if "int8.e178_v5" in (e["a"], e["b"]))
        flagged = sorted(o7["flagged"])
        v1_unflagged = sorted(e["name"] for e in o7v1["contrasts"] if "int8.e178_v5" in (e["a"], e["b"]) and e["rail_reads_the_board_runs"])
        rows7 = V1.load_runs(c7)

        def rem(kind):
            v = [r["D"] - r["Drail"] for r in rows7 if r["pass"] == 17811 and r["item"] == kind and r["Drail"] is not None]
            return sum(v) / len(v)

        worst, pform = 0.0, 0
        for e in o7["contrasts"]:
            if e["name"] in holds and e["form"] == "pass":
                pform += 1
                worst = max(worst, abs(e["off"]["per_pass"]["17811"] - (rem(e["a"]) - rem(e["b"]))))
        same_rest = all(subset_equal(x, y) is None for x, y in zip(o7v1["contrasts"], o7["contrasts"]) if x["name"] not in holds)
        check("F3 one kept run without a Drail is flagged in both forms; the pass-form remainder on the runs that have one (fault 3)",
              o7["consistency"]["pass_kinds_with_a_run_without_Drail"] == ["p17811 int8.e178_v5"] and flagged == holds and len(holds) == 4
              and pform == 3 and worst < 1e-12 and same_rest and v1_unflagged == [n for n in holds if not n.startswith("E178-H")]
              and all(e["runs_without_Drail"] == ["p17811 int8.e178_v5"] for e in o7["contrasts"] if e["name"] in holds),
              f"named: {o7['consistency']['pass_kinds_with_a_run_without_Drail']}; flagged here: {flagged} (A3's reader left unflagged "
              f"{v1_unflagged}); the {pform} pass-form remainders in p17811 equal the mean over the runs with a Drail of D - Drail, a less "
              f"b, to {worst:.1e} W; every other contrast equal to A3's reader's: {same_rest}")
        # W1 the board cell's frozen P and scored dP (A4-4), at s = 1.05
        sc8, sj8 = real_scored(tmp, "n6", c4, r4, s_float=1.05)
        o8 = read_session(CARD, c4, r4, sc8)
        h8 = {e["name"]: e for e in o8["contrasts"]}["E178-H-fp32"]
        md8 = markdown(o8)
        cell = fmt(h8, "board")
        want = f"(frozen P {h8['forecast_w']['board']['P_w']:+.4f}; scored dP {sj8['primary']['rules']['E178-H-fp32']['dP_w']:+.4f})"
        check("W1 the md's board cell names the frozen P and the scored dP (A4-4)", want in cell and cell in md8
              and h8["scorer_board"]["dP_w"] == sj8["primary"]["rules"]["E178-H-fp32"]["dP_w"]
              and abs(h8["scorer_board"]["dP_w"] - h8["forecast_w"]["board"]["P_w"]) > 1e-4,
              f"H-fp32 at s = 1.05, the real scorer: '{want}' (A3's reader printed only '(P {h8['forecast_w']['board']['P_w']:+.4f})')")
        # A3's synthetic cases, through this reader
        c9, r9 = V1.synth(tmp, "s2", flat_rail, 17832)
        h9 = {e["name"]: e for e in read_session(CARD, c9, r9)["contrasts"]}["E178-H-int8"]
        sc10 = V1.synth_scored(tmp, "s5", c1, r1, excluded=("int8.e178_v85",))
        o10 = read_session(CARD, c1, r1, sc10)
        lo = sorted(e["name"] for e in o10["contrasts"] if "left_out" in e)
        bad = json.load(open(r1))
        bad["per_pass"]["17812"]["int8.e178_v4"]["D"] += 0.01
        r11 = os.path.join(tmp, "s6-e178.json")
        json.dump(bad, open(r11, "w"))
        x11, _ = refused(read_session, CARD, c1, r11)
        sjb = json.load(open(sc1))
        sjb["primary"]["rules"]["E178-H-int8"]["per_pass"]["17811"]["x"] += 0.001
        sc12 = os.path.join(tmp, "s7-scored.json")
        json.dump(sjb, open(sc12, "w"))
        x12, _ = refused(read_session, CARD, c1, r1, sc12)
        x13, _ = refused(read_session, "aifoundry1c1", c1, r1)
        fj, ft = os.path.join(tmp, "rail-e178.json"), os.path.join(tmp, "rail-e178.txt")
        shutil.copyfile(V1.FROZEN_JSON, fj)
        shutil.copyfile(V1.FROZEN_TXT, ft)
        txt = open(fj).read()
        k = txt.index('"median": 0.8') + len('"median": 0.8')
        open(fj, "w").write(txt[:k] + ("1" if txt[k] != "1" else "2") + txt[k + 1:])
        x14, _ = refused(read_session, CARD, c1, r1, None, (fj, ft))
        ttop = os.path.join(tmp, "top")
        for r_ in list(V1.PINNED) + [V1_REL]:
            os.makedirs(os.path.dirname(os.path.join(ttop, r_)), exist_ok=True)
            shutil.copyfile(os.path.join(TOP, r_), os.path.join(ttop, r_))
        x15a, _ = refused(pinned_check, ttop)
        with open(os.path.join(ttop, V1_REL), "a") as f:
            f.write("\n# one line added\n")
        x15, w15 = refused(pinned_check, ttop)
        check("S A3's synthetic cases through this reader, and A3's reader changed", abs(h9["rail"]["mean_w"]) < 0.01
              and h9["off"]["interval_reads"] == "reads above 0" and h9["rail"]["forecast_P_is"] == "above"
              and lo == sorted(["E178-S-int8", V1.A2_2[0], "extremes 4: int8.e178_v85 - int8.ones"]) and o10["cross_check_with_scored_json"]["ok"]
              and (x11, x12, x13, x14, x15a, x15) == (6, 7, 2, 9, 0, 9) and "rail_e178.py" in w15,
              f"S2 the rail flat: H-int8 rail {h9['rail']['mean_w']:+.4f} W {h9['rail']['interval_reads']}, forecast {h9['rail']['forecast_P_is']}; "
              f"S5 E178-C leaves int8.e178_v85 out: {lo}; S6 a reduction not the runs.csv's: exit {x11}; S7 a scored.json not reproduced: exit "
              f"{x12}; S8 card 1: exit {x13}; S9 a changed rail-e178.json: exit {x14}; a copy of the pinned files: exit {x15a}, then with A3's "
              f"reader changed by one line: exit {x15}")
        # F1 the guard (A4-1), on stand-in trees
        g = {}
        for case, mk in (("a session's output", [("build/e178-out/2026-11-06-e178-one-number-aifoundry3", "scored.json")]),
                         ("a dropped arm", [("build/e178-dropped-arms/session_own", "e178-session_own.json")]),
                         ("the desk test's own output alone", [("build/e178-out/desktest-e178-one-number-aifoundry3", "scored.json")]),
                         ("nothing", [])):
            gt = os.path.join(tmp, "guard-" + case.replace(" ", "-").replace("'", ""))
            for d, f in mk:
                os.makedirs(os.path.join(gt, d), exist_ok=True)
                open(os.path.join(gt, d, f), "w").write("sentinel\n")
            os.makedirs(gt, exist_ok=True)
            found = t7_guard(gt)
            kept = all(os.path.exists(os.path.join(gt, d, f)) for d, f in mk)
            g[case] = {"found": found, "kept": kept}
        check("F1 T7's guard: it runs only where nothing but the desk test's own output would be removed (fault 1)",
              g["a session's output"]["found"] == ["build/e178-out/2026-11-06-e178-one-number-aifoundry3"]
              and g["a dropped arm"]["found"] == ["build/e178-dropped-arms/session_own"]
              and g["the desk test's own output alone"]["found"] == [] and g["nothing"]["found"] == [] and all(v["kept"] for v in g.values()),
              "; ".join(f"{k}: {'refuses, naming ' + ', '.join(v['found']) if v['found'] else 'runs'}" for k, v in g.items())
              + "; every stand-in file kept")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    t7_state = "not asked (--no-collect)"
    if not a.no_collect:
        t7_state = t7(E)
    ok = all(v["pass"] for v in RES.values() if isinstance(v, dict) and "pass" in v)
    n = sum(1 for v in RES.values() if isinstance(v, dict) and "pass" in v)
    npass = sum(1 for v in RES.values() if isinstance(v, dict) and v.get("pass"))
    if ok and t7_state.startswith("refused"):
        LINES.append(f"SELFTEST-RAIL-E178-V2 NOT COMPLETE: {npass} of {n} checks PASS; T7 {t7_state}")
        rc = 4
    else:
        LINES.append(f"SELFTEST-RAIL-E178-V2 {'PASS' if ok else 'FAIL'}: {npass} of {n} checks" + ("" if not a.no_collect else f" (T7 {t7_state})"))
        rc = 0 if ok else 1
    RES["distinct"] = dd
    txt = "\n".join(LINES) + "\n"
    print(txt, end="")
    if a.txt:
        open(a.txt, "w").write(txt)
    if a.json:
        open(a.json, "w").write(json.dumps(RES, indent=1, sort_keys=True) + "\n")
    return rc


def t7(E):
    """the kit's own collector on its relabelled real session (selftest_collect_e178.py's rule; a plumbing test, never quoted), then the
    card day's command line; only after the guard (A4-1) finds nothing that is not the desk test's own"""
    found = t7_guard(TOP)
    if found:
        LINES.append(f"T7: NOT RUN - its guard found what the kit's collector would remove: {', '.join(found)}; nothing was removed (run "
                     f"with --no-collect, or move those away after the data commit)")
        return "refused by its guard: " + ", ".join(found)
    import selftest_collect_e178 as V1T  # noqa: E402  (its relabel and its constants, unchanged; nothing runs at import)
    raw, out = os.path.join(TOP, V1T.RAW_REL), os.path.join(TOP, V1T.OUT_REL)
    work = os.path.join(TOP, WORK_REL)
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
        o, ov1, why = None, None, ""
        if okc:
            try:
                args = (CARD, os.path.join(out, "runs.csv"), os.path.join(out, "e178.json"), os.path.join(out, "scored.json"))
                o, ov1 = read_session(*args), V1.read_session(*args)
            except Refuse as e:
                why = f"refused, exit {e.code}: {e}"[:300]
        if o is None:
            check("T7 the kit's collector (collect_e178_v2.sh) on its relabelled real session, then the card day's command line", False,
                  f"collector exit {r.returncode}, results.md written {'results.md written' in log}; {why}")
            return "ran"
        cc = o["cross_check_with_scored_json"]
        nread = sum(1 for e in o["contrasts"] if "mean_w" in (e.get("rail") or {}))
        ident = max(e["identity_max_abs_w"] for e in o["contrasts"] if "board" in e)
        dv1 = subset_equal(ov1, o)
        oj, om = os.path.join(work, "rail-arm-e178.json"), os.path.join(work, "rail-arm-e178.md")
        cli = subprocess.run([sys.executable, "-B", os.path.abspath(__file__), "read", "--runs-csv", os.path.join(V1T.OUT_REL, "runs.csv"),
                              "--reduction", os.path.join(V1T.OUT_REL, "e178.json"), "--scored", os.path.join(V1T.OUT_REL, "scored.json"),
                              "--json", oj, "--md", om], cwd=TOP, capture_output=True, text=True, timeout=300)
        same = os.path.exists(oj) and json.load(open(oj)) == json.loads(json.dumps(o, sort_keys=True))
        mdrows = sum(1 for ln in open(om) if ln.startswith("| ") and not ln.startswith("| contrast")) if os.path.exists(om) else 0
        leak = [x for x in (TOP, os.path.expanduser("~")) if x and os.path.exists(oj) and (x in open(oj).read() or x in open(om).read())]
        kp = (json.load(open(os.path.join(out, "scored.json"))).get("primary") or {}).get("kept_passes")
        check("T7 the kit's collector (collect_e178_v2.sh) on its relabelled real session, then the card day's command line",
              cc["ok"] and cc["scorer_scored"] and o["kept_passes"] == [17810, 17811, 17812, 17813] and kp == o["kept_passes"]
              and o["consistency"]["ok"] and o["consistency"]["kept_runs_without_Drail"] == 0 and o["e178_c"]["applied"] and ident < 1e-12
              and nread >= 40 and dv1 is None and not o["flagged"] and cli.returncode == 0 and same and mdrows == 52 and not leak,
              f"guard: nothing found; collector exit 0, arms dropped 0; scored.json's kept passes {kp} = the reduction's; kept runs "
              f"{o['consistency']['kept_runs']} (every one with a Drail); E178-C applied (left out {o['e178_c']['c_excluded']}); the board "
              f"column reproduces scored.json ({cc['n_differences']} differences); {nread} of 52 contrasts read on the rail; board = rail + off "
              f"to {ident:.1e} W; every figure A3's reader writes on these files equal here: {dv1 is None}; the command line of A4-5 "
              f"(repo-relative paths): exit {cli.returncode}, its json equal to the call's {same}, its md {mdrows} contrast rows, no desk "
              f"path in either {not leak} (E171's tiles under E178's labels: no figure of it is quoted)")
        return "ran"
    finally:
        for d in gone:
            shutil.rmtree(d, ignore_errors=True)


# ------------------------------------------------------------------------------------------------- main
def main(argv):
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("check")
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
        if a.cmd == "check":
            pinned_check()
            ok, fz = V1.frozen_ok()
            if not ok:
                raise Refuse(9, "rail-e178.json or rail-e178.txt is not reproduced from the pinned inputs")
            print(f"CHECK PASS (A3's five pinned inputs; A3's reader at {V1_SHA256[:12]}; rail-e178.json and rail-e178.txt reproduced, "
                  f"{len(fz['contrasts'])} contrasts)")
            return 0
        if a.cmd == "read":
            o = read_session(a.card, os.path.abspath(a.runs_csv), os.path.abspath(a.reduction), os.path.abspath(a.scored) if a.scored else None)
            if a.json:
                open(a.json, "w").write(json.dumps(o, indent=1, sort_keys=True) + "\n")
            if a.md:
                open(a.md, "w").write(markdown(o))
            h = {e["name"]: e for e in o["contrasts"]}.get("E178-H-int8", {})
            d = o["distinct"]
            print(f"RAIL-E178-V2 READ: {d['contrasts']} contrasts ({d['distinct_readings']} distinct readings); flagged {len(o['flagged'])};",
                  f"NOT READ: {o['NOT READ']}" if o.get("NOT READ") else
                  ("H-int8 rail " + (fmt(h, "rail") if "rail" in h else str(h.get("left_out")))))
            return 0
        return selftest(a)
    except Refuse as e:
        print(f"REFUSED (exit {e.code}): {e}")
        return e.code


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
