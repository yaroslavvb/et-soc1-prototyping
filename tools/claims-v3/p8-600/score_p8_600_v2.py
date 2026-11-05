#!/usr/bin/env python3
# /// script
# requires-python = ">=3.9"
# dependencies = ["numpy"]
# ///
"""Q142(k6) fix pass: score_p8_600_v2.py, beside the committed P8 scorer at 600 MHz (score_p8_600.py, lab a518aa11, sha256 cd5b6024...,
which stays as committed and does all the scoring here). It adds what the kit's verifier (verify-desk-q142k6-kits, Thu 5 Nov 2026) found
missing, as dated note 1 beside each registration registers it (tools/claims-v3/e171/E171.md.dated-note-1.md and
tools/claims-v3/e172/E172.md.dated-note-1.md, lab 2502ba81, committed before this file and before any data):

  ka-pooled  python3 -B score_p8_600_v2.py ka-pooled <E171 scored.json> <E172 scored.json>
                 [--scale-c <E171 scale-c.json> <E172 scale-c.json>] [--json <out>]
      N1: P8-KA pooled, for the registered pair only. It refuses (exit 6, nothing written) unless (1) the first file is run E171 on
      aifoundry3 and the second run E172 on aifoundry1c1; (2) each names its card's frozen predictions file, with the freeze's sha256;
      (3) each was scored by the committed scorer, whose file still has its committed sha256; (4) each passed the C gate (c_sessions.ok);
      (5) the two are different files with different contents; (6) each file's rows are its own card's: every row's a-priori D equals its
      rate x that card's frozen per-op coefficient within 1e-9 W, and both check anchors have a row. Then the committed ka_pooled over the
      two files, unchanged. With --scale-c (each the scale-c.json written for that scored.json), the c_clean_scale arm's pooled reading is
      reported beside, never the verdict.
  scale-c    python3 -B score_p8_600_v2.py scale-c --run E171|E172 --scored <scored.json> --reduction <primary reduction> --raw <raw copy>
                 --ccheck <ccheck --out json> [--json scale-c.json] [--md scale-c.md] [--work <dir>]
      N2: each scale anchor's C status, from the same check of C and by P8-KC's rule (E163's c_status, as the committed scorer copies it),
      with E78's footing items reported beside; then, if an anchor that entered s is not all PASS, the arm c_clean_scale: the frozen
      predict_pool8.scale on a copy of the primary reduction without those anchors' items (written under --work, default <the scored
      file's directory>/scale-c), with every rule scored on it by the committed score_reduction, the same C status and scored sets;
      reported beside, never the verdict. It first checks that the scored file is this run's, on this reduction and these predictions,
      by the committed scorer, C-gated, with the P8-KC block this check of C gives and the scale the frozen scale gives (exit 6 if not).

Exit codes: 0 written; 6 an identity check failed; 9 a predictions or intervals file is not the freeze's (the committed load_pred), or the
committed scorer is not its committed file; 5 the scale read an anchor it must not (the committed check_scale); 1 the predictor's own stop
when one of its hash lists differs ("POOL8 STOPPED" / "POOL8-A2 STOPPED", raised as SystemExit); 2 a usage error. Nothing is written on
any refusal. Python 3.9 with numpy (the predictor's chain needs it): the Intel's /usr/bin/python3. SPDX-License-Identifier: Apache-2.0
"""
import argparse
import copy
import json
import os
import statistics
import sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
TOP = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
if HERE not in sys.path:
    sys.path.insert(0, HERE)
import score_p8_600 as SC  # noqa: E402  (the committed scorer, a518aa11, unchanged; importing it runs nothing)

EXIT_ID = 6
PAIR = (("E171", "aifoundry3"), ("E172", "aifoundry1c1"))   # the registered order: ka-pooled <E171 scored.json> <E172 scored.json>
# E78's items in every pass, other than pool 8's tiles: tools/claims-v3/kinds/e78_common.py ANCHORS and TIE (the self-test checks the list)
E78_ITEMS = ("fp32.zeros", "fp32.randn", "fp16.zeros", "fp16.randn", "int8.zeros", "int8.full", "anchor_pi")
TOL_W = 1e-9
sha = SC.sha
SCORER_REL = "tools/claims-v3/p8-600/score_p8_600.py"


def rel(p):
    a = os.path.abspath(p)
    return os.path.relpath(a, TOP) if a.startswith(TOP + os.sep) else os.path.basename(a)


def scrub(o):
    """paths inside the tree kept repo-relative (the data directory is public, and the runbook's desk-path gate reads it)"""
    return json.loads(json.dumps(o, default=str).replace(TOP + os.sep, "").replace(TOP, "<repo>"))


def committed_scorer_sha():
    """the committed scorer's sha256 from its own list (p8-600/SHA256SUMS, a518aa11); the file the import loaded must still have it"""
    want = None
    for line in open(os.path.join(HERE, "SHA256SUMS")):
        parts = line.split(None, 1)
        if len(parts) == 2 and parts[1].strip().lstrip("*") == SCORER_REL:
            want = parts[0]
    have = sha(os.path.abspath(SC.__file__))
    if not want or have != want:
        raise SC.Refuse(SC.EXIT_FROZEN, f"{SCORER_REL}: sha256 {have[:12]} is not its committed {str(want)[:12]} (p8-600/SHA256SUMS)")
    return want


def card_rows(o, pred):
    """N1 (6): every scored row's a-priori D is its rate x this card's frozen per-op coefficient; both check anchors have a row"""
    rows = (o.get("primary") or {}).get("rows") or {}
    bad, n = [], 0
    for t, r in sorted(rows.items()):
        if t not in pred["tiles"]:
            bad.append(f"{t}: not a tile of this card's predictions")
            continue
        if r.get("rate_per_s") is None or r.get("M10_a_priori_w") is None:
            continue
        want = float(r["rate_per_s"]) * float(pred["tiles"][t]["M10"]["k_J_per_op"])
        n += 1
        if abs(want - float(r["M10_a_priori_w"])) > TOL_W:
            bad.append(f"{t}: a-priori D {float(r['M10_a_priori_w']):.6f} W where this card's coefficient gives {want:.6f} W")
    miss = [t for t in pred["sets"]["KA"] if t not in rows]
    bad += [f"{t}: no row" for t in miss]
    return n, bad


def load_json(path, what):
    if not os.path.isfile(path):
        raise SC.Refuse(EXIT_ID, f"{path}: no such file ({what})")
    try:
        return json.load(open(path))
    except Exception as e:  # noqa: BLE001
        raise SC.Refuse(EXIT_ID, f"{rel(path)}: not a JSON {what} ({type(e).__name__})")


# ------------------------------------------------------------------------------------------------- N1: the pooled read
def pair_check(paths):
    """N1: the registered pair, or a refusal (exit 6) naming every check that failed"""
    if len(paths) != 2:
        raise SC.Refuse(EXIT_ID, "ka-pooled takes two files: <E171 scored.json> <E172 scored.json>")
    scorer = committed_scorer_sha()
    fz = SC.freeze_sums()
    bad, objs, info = [], [], []
    for q, (run, card) in zip(paths, PAIR):
        o = load_json(q, "scored.json")
        objs.append(o)
        tag = f"{rel(q)} (the {run} argument)"
        rec = {"argument": run, "file": rel(q), "sha256": sha(q), "run": o.get("run"), "card": o.get("card")}
        if o.get("run") != run or o.get("card") != card:
            bad.append(f"{tag}: run {o.get('run')} on {o.get('card')}, not {run} on {card} (the registered order: <E171 scored.json> "
                       f"<E172 scored.json>)")
        relp = f"tools/claims-v3/kinds/blind8/predictions-pool8-{card}.json"
        if o.get("predictions") != relp:
            bad.append(f"{tag}: predictions {o.get('predictions')}, not {relp}")
        if o.get("predictions_sha256") != fz.get(relp):
            bad.append(f"{tag}: predictions_sha256 {str(o.get('predictions_sha256'))[:12]} is not the freeze's {str(fz.get(relp))[:12]}")
        if o.get("scorer_sha256") != scorer:
            bad.append(f"{tag}: scorer_sha256 {str(o.get('scorer_sha256'))[:12]} is not the committed scorer's {scorer[:12]}")
        if not (o.get("c_sessions") or {}).get("ok"):
            bad.append(f"{tag}: not scored through the C gate (no c_sessions.ok)")
        if not isinstance(o.get("primary"), dict) or "scale" not in o["primary"]:
            bad.append(f"{tag}: no primary block")
        else:
            _, pred = SC.load_pred(card)          # exit 9 if the frozen file is not the freeze's
            n, rb = card_rows(o, pred)
            rec["rows_checked"] = n
            if n == 0 or rb:
                bad.append(f"{tag}: its rows are not {card}'s ({n} checked; " + "; ".join(rb[:3]) + ")")
        info.append(rec)
    if os.path.realpath(paths[0]) == os.path.realpath(paths[1]):
        bad.append("the two arguments are the same file")
    elif info[0]["sha256"] == info[1]["sha256"]:
        bad.append("the two files have the same contents")
    if bad:
        raise SC.Refuse(EXIT_ID, "ka-pooled reads only E171's and E172's own scored sessions (dated note 1, N1): " + "; ".join(bad))
    return objs, info


def c_clean_pooled(objs, info, paths):
    """N2 beside: the pooled KA test over each session's c_clean_scale arm (its primary where the arm is the primary); never the verdict"""
    if len(paths) != 2:
        raise SC.Refuse(EXIT_ID, "--scale-c takes two files: <E171 scale-c.json> <E172 scale-c.json>")
    rows, s1, used = [], [], []
    for q, o, rec, (run, card) in zip(paths, objs, info, PAIR):
        c = load_json(q, "scale-c.json")
        if c.get("run") != run or c.get("card") != card or c.get("scored_sha256") != rec["sha256"]:
            raise SC.Refuse(EXIT_ID, f"{rel(q)}: not the scale-c.json written for {rec['file']} (run {c.get('run')} on {c.get('card')}, "
                                     f"scored_sha256 {str(c.get('scored_sha256'))[:12]}, want {run} on {card}, {rec['sha256'][:12]})")
        arm = c.get("arm")
        if arm:
            ka, s, src = arm.get("P8-KA") or {}, float(arm["s_float"]), "the arm c_clean_scale"
        else:
            ka, s = o["primary"].get("rules", {}).get("P8-KA", {}), float(o["primary"]["scale"]["s_float"])
            src = "the primary (every anchor in s is C all PASS)"
        s1.append(s == 1.0)
        for t, r in sorted((ka.get("tiles") or {}).items()):
            rows.append(dict(r, tile=t, run=run))
        used.append({"run": run, "from": src, "s_float": s, "scale_c": rel(q), "scale_c_sha256": sha(q)})
    mins = SC.P().frozen()["reg"]["scoring"]["minimum_tiles"]["KA_pooled"]
    if any(s1):
        res = {"verdict": "NOT SCORED", "why": "a session's arm took s = 1", "n": len(rows)}
    elif len(rows) < mins:
        res = {"verdict": "NOT SCORED", "why": f"{len(rows)} check anchors, fewer than {mins}", "n": len(rows)}
    else:
        res = dict(SC.ka_test(rows), rows=rows)
    res["sessions"] = used
    res["note"] = "reported beside, never the verdict (dated note 1, N2)"
    return res


def ka_pooled_v2(paths, scale_c=None):
    objs, info = pair_check(paths)
    out = dict(SC.ka_pooled(list(paths)))           # the committed reading, unchanged
    out["identity"] = {"pair": info, "scorer_sha256": committed_scorer_sha(), "v2_sha256": sha(os.path.abspath(__file__)),
                       "checks": ["run and card in the registered order", "the freeze's predictions file and sha256", "the committed scorer",
                                  "C-gated", "two different files", "each card's own rows"]}
    if scale_c:
        out["beside"] = {"c_clean_scale": c_clean_pooled(objs, info, scale_c)}
    return out


# ------------------------------------------------------------------------------------------------- N2: the scale anchors' C status
def kc_of(cstat, want):
    """the committed score_session's P8-KC block, from the same c_status (lines 465-470 of score_p8_600.py, mirrored)"""
    unmeasured = sorted(t for t in want if not (cstat.get(t) or {}).get("passes_without_log") and (cstat.get(t) or {}).get("launches", 0) == 0)
    cfail = sorted(t for t in want if t not in unmeasured and not (cstat.get(t) or {}).get("all_pass"))
    ok = [t for t in want if t not in cfail]
    kc = {"verdict": "FAIL" if cfail else ("PASS" if any((cstat.get(t) or {}).get("launches") for t in want) else "NOT SCORED"),
          "c_excluded": cfail, "not_measured": unmeasured,
          "launches": sum((cstat.get(t) or {}).get("launches", 0) for t in want), "PASS": sum((cstat.get(t) or {}).get("PASS", 0) for t in want)}
    return kc, ok


def status_rec(s):
    s = s or {}
    return {"launches": s.get("launches", 0), "PASS": s.get("PASS", 0), "missing": s.get("missing", 0), "other": s.get("other", {}),
            "passes_without_log": s.get("passes_without_log", []), "all_pass": bool(s.get("all_pass"))}


def scale_c(run, scored_path, red_path, raw, ccheck, work=None, draws=None):
    card = SC.RUN_CARD[run]
    a2 = SC.A2()
    lists = a2.check_lists()
    p = SC.P()
    n_in = p.check_inputs()
    pred_path, pred = SC.load_pred(card)            # 9 if not the freeze's
    scorer = committed_scorer_sha()
    o = load_json(scored_path, "scored.json")
    bad = []
    if o.get("run") != run or o.get("card") != card:
        bad.append(f"run {o.get('run')} on {o.get('card')}, not {run} on {card}")
    if o.get("predictions_sha256") != sha(pred_path):
        bad.append("predictions_sha256 is not this card's frozen predictions'")
    if o.get("scorer_sha256") != scorer:
        bad.append("scorer_sha256 is not the committed scorer's")
    if not (o.get("c_sessions") or {}).get("ok"):
        bad.append("not scored through the C gate (no c_sessions.ok)")
    prim = o.get("primary") or {}
    if not os.path.isfile(red_path):
        bad.append(f"{red_path}: no such reduction")
    elif prim.get("reduction_sha256") != sha(red_path):
        bad.append("the reduction given is not the one the scored file was scored on (reduction_sha256)")
    if bad:
        raise SC.Refuse(EXIT_ID, f"{rel(scored_path)} is not {run}'s scored session on these inputs (dated note 1, N2): " + "; ".join(bad))
    res = json.load(open(red_path))
    passes_dir = os.path.join(raw, SC.CS().RUNS[run]["dir"])
    ccf = ccheck if os.path.exists(ccheck) else ccheck + ".gz"
    if not os.path.exists(ccf):
        raise SC.Refuse(EXIT_ID, f"{ccheck}: no check of C")
    want = list(pred["tiles"])
    cstat = SC.c_status(want, res, [ccf], passes_dir)
    kc, ok = kc_of(cstat, want)
    kc_file = (prim.get("rules") or {}).get("P8-KC") or {}
    if any(kc.get(k) != kc_file.get(k) for k in ("verdict", "c_excluded", "not_measured", "launches", "PASS")):
        raise SC.Refuse(EXIT_ID, f"the check of C given ({rel(ccf)}) does not give the scored file's P8-KC block: it is not the check this "
                                 f"session was scored with (recomputed {kc['verdict']}, {kc['launches']} launches; the file's "
                                 f"{kc_file.get('verdict')}, {kc_file.get('launches')})")
    sc0 = p.scale(pred, red_path)
    if list(sc0["anchors_used"]) != list(prim["scale"]["anchors_used"]) or float(sc0["s_float"]) != float(prim["scale"]["s_float"]):
        raise SC.Refuse(EXIT_ID, f"the frozen scale on this reduction ({sc0['s_float']}, {sc0['anchors_used']}) is not the scored file's "
                                 f"({prim['scale']['s_float']}, {prim['scale']['anchors_used']})")
    names_s = list(dict.fromkeys(p.m10_anchor_names() + list(pred["sets"]["scale_anchors_pool8"])))
    cx = SC.c_status(list(dict.fromkeys(names_s + list(E78_ITEMS))), res, [ccf], passes_dir)
    used = list(sc0["anchors_used"])
    anchors = {}
    for n in names_s:
        r = status_rec(cx.get(n))
        r.update(source="pool 8's scale anchor" if n in pred["sets"]["scale_anchors_pool8"] else "M10's own list",
                 in_s=n in used, ratio=sc0["ratios"].get(n))
        anchors[n] = r
    footing = {n: status_rec(cx.get(n)) for n in E78_ITEMS if n not in names_s}
    unclean = [n for n in used if not anchors[n]["all_pass"]]
    foot_bad = [n for n, r in footing.items() if not r["all_pass"]]
    out = {"_note": f"Q142(k6) score_p8_600_v2.py scale-c: {run} on {card}, each scale anchor's C status and the c_clean_scale arm "
                    "(dated note 1, N2; reported beside, never the verdict)",
           "run": run, "card": card, "v2_sha256": sha(os.path.abspath(__file__)), "scorer_sha256": scorer,
           "predictor_lists": lists, "pool8_inputs_checked": n_in,
           "scored": rel(scored_path), "scored_sha256": sha(scored_path), "reduction": rel(red_path), "reduction_sha256": sha(red_path),
           "ccheck": rel(ccf), "ccheck_sha256": sha(ccf), "predictions": rel(pred_path), "predictions_sha256": sha(pred_path),
           "rule": "E163's c_status (the committed scorer's copy): every launch record of the item in a kept pass's runs.jsonl has a C record "
                   "with the same t_start_ms and t_end_ms judged PASS",
           "primary": {"s_float": sc0["s_float"], "anchors_used": used, "anchors_missing": sc0["anchors_missing"],
                       "verdicts": o.get("verdicts")},
           "scale_anchors": anchors, "footing_items": footing,
           "in_s_not_all_pass": unclean, "footing_not_all_pass": foot_bad}
    if not unclean:
        out["arm"] = None
        out["arm_note"] = "every anchor that entered s is C all PASS: the arm c_clean_scale is the primary (not recomputed)"
    else:
        work = work or os.path.join(os.path.dirname(os.path.abspath(scored_path)), "scale-c")
        os.makedirs(work, exist_ok=True)
        fr = copy.deepcopy(res)
        for n in unclean:
            fr["items"].pop(n, None)
        fpath = os.path.join(work, f"{run.lower()}-c-clean-scale.json")
        with open(fpath, "w") as fh:
            fh.write(json.dumps(fr, indent=1, sort_keys=True) + "\n")
        try:
            a = SC.score_reduction(pred_path, pred, card, fpath, cstat, ok, draws)    # the committed function, unchanged
        except BaseException:
            os.remove(fpath)                     # nothing is left behind by a refusal or a stop
            raise
        a["rules"] = dict({"P8-KC": kc}, **a.get("rules", {}))
        a["verdicts"] = dict({"P8-KC": kc["verdict"]}, **a.get("verdicts", {}))
        V0 = o.get("verdicts") or {}
        diff = {r: {"primary": V0.get(r), "arm": a["verdicts"].get(r)} for r in SC.RULES if V0.get(r) != a["verdicts"].get(r)}
        out["arm"] = {"name": "c_clean_scale", "removed_from_s": unclean, "reduction": rel(fpath), "reduction_sha256": sha(fpath),
                      "s_float": a["scale"]["s_float"], "anchors_used": a["scale"]["anchors_used"], "verdicts": a["verdicts"],
                      "rules": {r: {k: v.get(k) for k in ("verdict", "rms", "mean", "line", "n", "inside", "d_rms", "lo95", "hi95")}
                                for r, v in a.get("rules", {}).items()},
                      "P8-KA": a["rules"].get("P8-KA"), "differs_from_primary": diff}
        out["arm_note"] = (f"{len(unclean)} anchor(s) in s not C all PASS ({', '.join(unclean)}): s without them "
                           f"{a['scale']['s_float']:.6f} against the primary's {sc0['s_float']:.6f}; {len(diff)} rule(s) read differently")
    return scrub(out)


def summary_line(c):
    n = len(c["primary"]["anchors_used"])
    if not c["arm"]:
        s = f"SCALE-C {c['run']}: {n} anchors in s, every one C all PASS: the arm c_clean_scale is the primary"
    else:
        s = (f"SCALE-C {c['run']}: {len(c['in_s_not_all_pass'])} of {n} anchors in s not C all PASS ({', '.join(c['in_s_not_all_pass'])}): "
             f"the arm c_clean_scale reads s {c['arm']['s_float']:.5f} against {c['primary']['s_float']:.5f}, "
             f"{len(c['arm']['differs_from_primary'])} rule(s) differ (reported beside)")
    if c["footing_not_all_pass"]:
        s += f"; footing items not C all PASS: {', '.join(c['footing_not_all_pass'])}"
    return s


def markdown(c):
    L = [f"# {c['run']} on {c['card']}: the scale anchors' C status (score_p8_600_v2.py scale-c; dated note 1, N2)", "",
         f"Reported beside, never the verdict. The registered verdicts are the committed scorer's `{c['scored']}` "
         f"({c['scored_sha256'][:12]}); the check of C `{c['ccheck']}` ({c['ccheck_sha256'][:12]}); the primary's s = "
         f"{c['primary']['s_float']:.5f} from {len(c['primary']['anchors_used'])} anchors.", "",
         "| anchor | from | in s | ratio | launches | PASS | C all PASS |", "|---|---|---|---:|---:|---:|---|"]
    for n, r in c["scale_anchors"].items():
        ratio = f"{r['ratio']:.5f}" if isinstance(r.get("ratio"), (int, float)) else ""
        L.append(f"| `{n}` | {r['source']} | {'yes' if r['in_s'] else 'no'} | {ratio} | {r['launches']} | {r['PASS']} | "
                 f"{'yes' if r['all_pass'] else 'NO'} |")
    L += ["", "E78's other items, on which the reduction's footing rests (reported only):", "",
          "| item | launches | PASS | C all PASS |", "|---|---:|---:|---|"]
    for n, r in c["footing_items"].items():
        L.append(f"| `{n}` | {r['launches']} | {r['PASS']} | {'yes' if r['all_pass'] else 'NO'} |")
    L += ["", summary_line(c), ""]
    if c["arm"]:
        L += ["| rule | primary | c_clean_scale |", "|---|---|---|"]
        for r in SC.RULES:
            L.append(f"| {r} | {(c['primary']['verdicts'] or {}).get(r)} | {c['arm']['verdicts'].get(r)} |")
    return "\n".join(L) + "\n"


def main(argv):
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    k = sub.add_parser("ka-pooled")
    k.add_argument("scored", nargs=2)
    k.add_argument("--scale-c", nargs=2)
    k.add_argument("--json")
    s = sub.add_parser("scale-c")
    s.add_argument("--run", required=True, choices=sorted(SC.RUN_CARD))
    s.add_argument("--scored", required=True)
    s.add_argument("--reduction", required=True)
    s.add_argument("--raw", required=True)
    s.add_argument("--ccheck", required=True)
    s.add_argument("--json")
    s.add_argument("--md")
    s.add_argument("--work")
    a = ap.parse_args(argv)
    try:
        if a.cmd == "ka-pooled":
            o = ka_pooled_v2([os.path.abspath(x) for x in a.scored], [os.path.abspath(x) for x in a.scale_c] if a.scale_c else None)
            if a.json:
                open(a.json, "w").write(json.dumps(scrub(o), indent=1, sort_keys=True, default=str) + "\n")
            print(json.dumps({k_: o[k_] for k_ in ("verdict", "n") if k_ in o}))
            if "beside" in o:
                b = o["beside"]["c_clean_scale"]
                print(json.dumps({"beside_c_clean_scale": {k_: b[k_] for k_ in ("verdict", "n") if k_ in b}}))
            return 0
        c = scale_c(a.run, os.path.abspath(a.scored), os.path.abspath(a.reduction), os.path.abspath(a.raw), os.path.abspath(a.ccheck),
                    os.path.abspath(a.work) if a.work else None)
    except SC.Refuse as e:
        print(f"REFUSED (exit {e.code}): {e}")
        return e.code
    if a.json:
        open(a.json, "w").write(json.dumps(c, indent=1, sort_keys=True, default=str) + "\n")
    if a.md:
        open(a.md, "w").write(markdown(c))
    print(summary_line(c))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
