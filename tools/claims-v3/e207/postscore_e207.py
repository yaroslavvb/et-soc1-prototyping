#!/usr/bin/env python3
"""E207 (Q199): the after-score tool, registered by E207.md amendment A1 (lane fix-e207, Tue 17 Nov 2026, before any E207 datum) to answer
verify-e207's findings 3 and 6 and the reading of finding 9. It reads the FROZEN scorer's output (score_e207.py's JSON on the committed
data-e207.json; the scorer is unchanged) and never re-scores a run: it re-tallies the scorer's own per-case and per-point verdicts and its own d
values with the scorer's own functions (rule_verdict, h2h_verdict, sign_test_p, imported from score_e207.py unchanged), under the scorer's own
pins (load_frozen: exit 4 if MM1-v1's frozen files, rules-e207.json or points-e207.json changed). Standard library only.

    python3 -I -B tools/claims-v3/e207/postscore_e207.py SCORED.json [--data-dir DIR] [--labels LABELS.json] [--out OUT.json]
    python3 -I -B tools/claims-v3/e207/postscore_e207.py --selftest OUT.json            (prints its words; exit 0 = PASS)

1. THE 'RAN BEFORE' LABELS (A1 item 3; finding 3). The labels are read from --labels, else from DIR/ranbefore-e207-labels.json (the card lane's
   final labels, written with its dated note when it dates a TO DATE place from the session's own start record), else from
   DIR/ranbefore-e207-card.json's "labels_proposed" (step 6n's own, copied into the data directory by the collection), else none. A labelled POINT
   leaves E1, E2, E3, E4, S6, H3 and H4, and its CASE leaves T1, T2, T3, H1 and H2; a labelled CASE (one that ran before in another data kind while
   its points never ran) leaves T1, T2, T3, H1 and H2 only. R0 stays as the scorer read it, on every run of the day (a labelled run's checks of C
   still count). Every rule is re-tallied by the registered arithmetic: 90% of the scored, TOO FEW under 10, NO DATA with none; the exact
   two-sided sign test at alpha 0.05 on the untied, TOO FEW under 10 untied. THE REGISTERED VERDICT IS THIS RE-TALLY ("registered_verdicts"); with
   no label it equals the scorer's own verdict and counts, rule by rule (the self-test checks it on all 16 stand-in days). Both outputs, the
   scorer's and this, are committed beside the data. A label naming an unknown point or case is refused (exit 2).
2. THE FAMILY-LEVEL CHECK beside H1-H4 (A1 item 6; finding 6; REPORTED, never a verdict). The sign tests treat the cases as independent, but E207's
   points fall into 8 families (its 47 time cases into 7: the kinds points share their cases with random points). Per family, the median d over
   its cases or points that remain (the watts points left out, as the scorer's bootstrap leaves them out); a family favours MM1-v1 if that median
   is above the rule's tie, the other model if below minus the tie, else it is tied; the exact two-sided sign test over the untied families
   (TOO FEW under 5 untied: at 0.05 it can decide only with 6 of 6, 7 of 7 or 8 of 8 families one way); and a cluster bootstrap over families
   (10,000 resamples, seeded "E207|family|<rule>"): the percentile 95% interval of the mean d over the cases or points of the drawn families.
3. THE CHECKS OF C READ (A1 item 9; finding 9; REPORTED): from DIR/data-e207.json, every run (the points', the ties') whose reducer detail carries
   checks_missing above 0 (a host process that printed no check of C), which R0 cannot see; the README and verify-e207d read this count (0 expected).
SPDX-License-Identifier: Apache-2.0
"""
import argparse
import copy
import hashlib
import json
import os
import random
import statistics
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import score_e207 as S  # noqa: E402  (the frozen scorer, unchanged: its functions and pins only)

TIME = ("T1", "T2", "T3")
ENERGY = ("E1", "E2", "E3", "E4", "S6")
OTHER = {"H1": "F1", "H2": "F1", "H3": "F2", "H4": "F2"}


def read_labels(FZ, labels_path=None, data_dir=None):
    """(source, points, cases): --labels, else DIR/ranbefore-e207-labels.json, else DIR/ranbefore-e207-card.json's proposal, else none"""
    src = None
    if labels_path:
        src = labels_path
    elif data_dir and os.path.exists(os.path.join(data_dir, "ranbefore-e207-labels.json")):
        src = os.path.join(data_dir, "ranbefore-e207-labels.json")
    elif data_dir and os.path.exists(os.path.join(data_dir, "ranbefore-e207-card.json")):
        src = os.path.join(data_dir, "ranbefore-e207-card.json")
    if src is None:
        return "none (no labels file: no point or case ran before)", [], []
    d = json.load(open(src))
    lab = d.get("labels_proposed", d)
    pts, cases = sorted(set(lab.get("points", []))), sorted(set(lab.get("cases", [])))
    bad = [p for p in pts if p not in FZ["byid"]] + [c for c in cases if c not in FZ["cases"]]
    if bad:
        raise SystemExit(f"postscore_e207: REFUSED, the labels name unknown points or cases: {bad}")
    where = os.path.basename(src) + (" (step 6n's proposal)" if "labels_proposed" in d else "")
    return where, pts, cases


def retally(sc, FZ, lab_points, lab_cases):
    """the scorer's own cells and d values with the labelled points and cases left out, by the scorer's own arithmetic"""
    R = FZ["rules"]
    share, min_sc = R["verdict"]["share"], R["verdict"]["min_scored"]
    HH = R["head_to_head"]
    out_cases = set(lab_cases) | {FZ["byid"][p]["case"] for p in lab_points}
    out_pts = set(lab_points)
    res = {"rules": {}, "head_to_head": {}, "excluded": {"time_cases": sorted(out_cases), "points": sorted(out_pts)}}
    res["rules"]["R0"] = {"verdict": sc["rules"]["R0"]["verdict"], "note": "read on every run of the day, as the scorer read it"}
    for rl in TIME:
        cells = {k: v for k, v in sc["rules"][rl]["cells"].items() if k not in out_cases}
        res["rules"][rl] = S.rule_verdict(cells, share, min_sc)
    for rl in ENERGY:
        cells = {k: v for k, v in sc["rules"][rl]["cells"].items() if k not in out_pts}
        res["rules"][rl] = S.rule_verdict(cells, share, min_sc)
    for h in ("H1", "H2", "H3", "H4"):
        tie_ln = HH["ties"]["cycles_ln"] if h in ("H1", "H2") else HH["ties"]["j_ln"]
        drop = out_cases if h in ("H1", "H2") else out_pts
        rows = [{"id": k, "watts": (h in ("H3", "H4") and bool(sc["points"].get(k, {}).get("scored_in_watts"))), "d": d}
                for k, d in sc["head_to_head"][h]["d"].items() if k not in drop]
        r = S.h2h_verdict(rows, tie_ln, HH["ties"]["watts_w"], OTHER[h], HH["alpha"], HH["min_untied"])
        res["head_to_head"][h] = {k: r[k] for k in ("verdict", "mm1_closer", "other_closer", "ties", "untied", "p_two_sided")}
    res["verdicts"] = {**{rl: res["rules"][rl]["verdict"] for rl in ("R0",) + TIME + ENERGY},
                       **{h: res["head_to_head"][h]["verdict"] for h in ("H1", "H2", "H3", "H4")}}
    return res


def family_check(sc, FZ, lab_points, lab_cases, B=10000):
    """REPORTED: the sign test over family medians of d, and a cluster bootstrap over families of the mean d"""
    HH = FZ["rules"]["head_to_head"]
    out_cases = set(lab_cases) | {FZ["byid"][p]["case"] for p in lab_points}
    out_pts = set(lab_points)
    res = {}
    for h in ("H1", "H2", "H3", "H4"):
        tie = HH["ties"]["cycles_ln"] if h in ("H1", "H2") else HH["ties"]["j_ln"]
        fam = {}
        for k, d in sc["head_to_head"][h]["d"].items():
            if d is None:
                continue
            if h in ("H1", "H2"):
                if k in out_cases:
                    continue
                f = FZ["byid"][FZ["cases"][k][0]]["family"]
            else:
                if k in out_pts or sc["points"].get(k, {}).get("scored_in_watts"):
                    continue
                f = FZ["byid"][k]["family"]
            fam.setdefault(f, []).append(d)
        per = {}
        w = l = t = 0
        for f in sorted(fam):
            m = statistics.median(fam[f])
            side = "MM1-v1" if m > tie else (OTHER[h] if m < -tie else "TIE")
            w += side == "MM1-v1"
            l += side == OTHER[h]
            t += side == "TIE"
            per[f] = {"n": len(fam[f]), "median_d": m, "favours": side}
        n = w + l
        p = S.sign_test_p(w, l)
        if not per:
            v = "NO DATA"
        elif n < 5:
            v = "TOO FEW"
        elif p <= 0.05 and w > l:
            v = "MM1-v1 BETTER"
        elif p <= 0.05 and l > w:
            v = f"{OTHER[h]} BETTER"
        else:
            v = "NOT DECIDED"
        boot = None
        fs = sorted(fam)
        if len(fs) >= 2:
            rng = random.Random(f"E207|family|{h}")
            means = []
            for _ in range(B):
                vals = [x for _k in range(len(fs)) for x in fam[fs[rng.randrange(len(fs))]]]
                means.append(sum(vals) / len(vals))
            means.sort()
            lo, hi = int(0.025 * B), int(0.975 * B) - 1
            allv = [x for f in fs for x in fam[f]]
            boot = {"families": len(fs), "mean_d": sum(allv) / len(allv), "mean_d_95": [means[lo], means[hi]], "resamples": B}
        res[h] = {"verdict_REPORTED": v, "families_mm1_closer": w, "families_other_closer": l, "families_tied": t, "p_two_sided": p,
                  "per_family": per, "cluster_bootstrap": boot, "tie": tie,
                  "label": "REPORTED beside the registered head-to-head verdict (E207.md A1 item 6); never a verdict"}
    return res


def checks_read(data_dir):
    p = os.path.join(data_dir, "data-e207.json") if data_dir else None
    if not p or not os.path.exists(p):
        return {"read": False, "why": "no data-e207.json given"}
    A = (json.load(open(p)).get("arms") or {}).get("A") or {}
    miss, n = [], 0
    for pid, pt in sorted((A.get("points") or {}).items()):
        for r in pt.get("runs") or []:
            n += 1
            if ((r.get("detail") or {}).get("checks_missing") or 0) > 0:
                miss.append(f"{pid}.run{r.get('n')}")
    for r in (A.get("ties") or {}).get("runs") or []:
        n += 1
        if ((r.get("detail") or {}).get("checks_missing") or 0) > 0:
            miss.append(f"tie.run{r.get('n')}")
    return {"read": True, "runs": n, "runs_with_checks_missing": len(miss), "where": miss[:60],
            "label": "REPORTED (E207.md A1 item 9): R0 cannot see a run that printed no check of C; 0 expected"}


def run(scored_path, FZ, data_dir=None, labels_path=None):
    sc = json.load(open(scored_path))
    src, lp, lc = read_labels(FZ, labels_path, data_dir)
    rt = retally(sc, FZ, lp, lc)
    scorer_v = {**{rl: sc["rules"][rl]["verdict"] for rl in ("R0",) + TIME + ENERGY},
                **{h: sc["head_to_head"][h]["verdict"] for h in ("H1", "H2", "H3", "H4")}}
    out = {"experiment": "E207", "what": "the after-score tool (E207.md A1 items 3, 6, 9): the scorer's own cells re-tallied with the 'ran "
                                          "before' labels left out (THE REGISTERED VERDICT), the family-level check and the checks read (REPORTED)",
           "scored_file": os.path.basename(scored_path), "scored_file_sha256": hashlib.sha256(open(scored_path, "rb").read()).hexdigest(),
           "labels": {"source": src, "points": lp, "cases": lc}, "registered_verdicts": rt["verdicts"], "scorer_verdicts": scorer_v,
           "same_as_scorer": rt["verdicts"] == scorer_v, "retally": rt, "family_check_REPORTED": family_check(sc, FZ, lp, lc),
           "checks_read_REPORTED": checks_read(data_dir), "python": sys.version.split()[0]}
    return out


def words(o):
    L = [f"E207 after the scorer (E207.md A1): labels {o['labels']['source']}: points {' '.join(o['labels']['points']) or '-'}; cases "
         f"{' '.join(o['labels']['cases']) or '-'}"]
    rt = o["retally"]
    L.append("THE REGISTERED VERDICTS (the scorer's cells, labelled points and cases left out): " +
             ", ".join(f"{k} {v}" for k, v in o["registered_verdicts"].items()) + ("  (the same as the scorer's)" if o["same_as_scorer"] else ""))
    for rl in TIME + ENERGY:
        x = rt["rules"][rl]
        L.append(f"  {rl} {x['verdict']} ({x.get('pass')}/{x.get('scored')})")
    for h, x in rt["head_to_head"].items():
        L.append(f"  {h} {x['verdict']} (MM1-v1 closer {x['mm1_closer']}, other closer {x['other_closer']}, ties {x['ties']}, p {x['p_two_sided']})")
    for h, x in o["family_check_REPORTED"].items():
        b = x["cluster_bootstrap"]
        L.append(f"FAMILY CHECK (REPORTED) {h}: {x['verdict_REPORTED']} (families MM1-v1 {x['families_mm1_closer']}, {OTHER[h]} "
                 f"{x['families_other_closer']}, tied {x['families_tied']}, p {x['p_two_sided']}); mean d "
                 + (f"{b['mean_d']:.4f}, cluster bootstrap 95% [{b['mean_d_95'][0]:.4f}, {b['mean_d_95'][1]:.4f}] over {b['families']} families"
                    if b else "n/a"))
    c = o["checks_read_REPORTED"]
    L.append("CHECKS READ (REPORTED): " + (f"{c['runs_with_checks_missing']} of {c['runs']} runs printed no check of C"
                                          if c.get("read") else c.get("why", "")))
    return "\n".join(L) + "\n"


# ------------------------------------------------------------------ the self-test
def selftest(outp):
    FZ = S.load_frozen()
    res = {"what": "postscore_e207.py's self-test (desk check of code): (1) with no label the re-tally equals the frozen scorer's verdicts and "
                   "counts on all 16 stand-in days; (2) labels on day A leave out exactly the stated cells (counts stated apart from retally()); "
                   "(3) a case label flips T1 from FAIL to PASS on a stated day; (4) the family check on days A, B and J; (5) the labels files' "
                   "precedence and the refusal of an unknown label; (6) the checks read", "checks": {}, "python": sys.version.split()[0]}
    ok_all = True

    def chk(name, got, want):
        nonlocal ok_all
        ok = got == want
        ok_all &= ok
        res["checks"][name] = {"ok": ok, "got": got, "want": want}
    # (1) no label: the scorer's own verdicts and counts, day by day
    for day in S.STANDINS:
        sc = json.loads(json.dumps(S.score(S.standin_data(FZ, day), FZ), default=str))
        rt = retally(sc, FZ, [], [])
        diff = {}
        for rl in TIME + ENERGY:
            a, b = rt["rules"][rl], sc["rules"][rl]
            if (a["verdict"], a.get("scored"), a.get("pass")) != (b["verdict"], b.get("scored"), b.get("pass")):
                diff[rl] = [(a["verdict"], a.get("scored"), a.get("pass")), (b["verdict"], b.get("scored"), b.get("pass"))]
        for h in ("H1", "H2", "H3", "H4"):
            ks = ("verdict", "mm1_closer", "other_closer", "ties", "untied", "p_two_sided")
            if any(rt["head_to_head"][h][k] != sc["head_to_head"][h][k] for k in ks):
                diff[h] = [[rt["head_to_head"][h][k] for k in ks], [sc["head_to_head"][h][k] for k in ks]]
        if rt["verdicts"]["R0"] != sc["rules"]["R0"]["verdict"]:
            diff["R0"] = [rt["verdicts"]["R0"], sc["rules"]["R0"]["verdict"]]
        chk(f"1.{day} no label = the scorer", diff, {})
    # (2) labels on day A: b01 (a point: its case gemmL1x3x2|fp32|0xffffffff leaves the time rules with it) and b05's case (time only)
    scA = json.loads(json.dumps(S.score(S.standin_data(FZ, "A"), FZ), default=str))
    lp, lc = ["b01"], ["gemmL2x3x2|int8|0xffffffff"]
    rt = retally(scA, FZ, lp, lc)
    want = {"T1": [45, 45, "PASS"], "T2": [45, 45, "PASS"], "T3": [45, 45, "PASS"], "E1": [52, 52, "PASS"], "E2": [52, 52, "PASS"],
            "E3": [52, 52, "PASS"], "E4": [52, 52, "PASS"], "S6": [52, 52, "PASS"]}
    chk("2.A labels: rule counts (stated: 47 cases less 2, 53 points less 1, all PASS)",
        {rl: [rt["rules"][rl]["scored"], rt["rules"][rl]["pass"], rt["rules"][rl]["verdict"]] for rl in want}, want)
    h_want = {"H1": [45, 0, 0], "H2": [45, 0, 0], "H4": [48, 0, 0]}   # day A: MM1-v1 exact; F1/F2 apart by more than the ties at every case
    chk("2.A labels: H1, H2, H4 counts (stated: 47 - 2 cases; F2's 49 priced points - b01)",
        {h: [rt["head_to_head"][h]["mm1_closer"], rt["head_to_head"][h]["other_closer"], rt["head_to_head"][h]["ties"]] for h in h_want}, h_want)
    chk("2.A labels: R0 kept as read", rt["verdicts"]["R0"], scA["rules"]["R0"]["verdict"])
    # (3) a case label that flips T1: day A with the wall cycles of 5 cases at 1.2 x MM1-v1 (T1 42 of 47 = 0.894: FAIL); label one of the 5
    dA = S.standin_data(FZ, "A")
    five = sorted(FZ["cases"])[:5]
    for c in five:
        for pid in FZ["cases"][c]:
            for r in dA["arms"]["A"]["points"][pid]["runs"]:
                r["cycles_gemm"] = r["cycles_gemm"] * 1.2
    sc3 = json.loads(json.dumps(S.score(dA, FZ), default=str))
    rt3 = retally(sc3, FZ, [], [five[0]])
    chk("3. the scorer's T1 on the 1.2x day (stated 42 of 47 FAIL)", [sc3["rules"]["T1"]["pass"], sc3["rules"]["T1"]["scored"], sc3["rules"]["T1"]["verdict"]],
        [42, 47, "FAIL"])
    chk("3. the re-tally's T1 with one of the 5 labelled (stated 42 of 46 PASS); T2 and T3 PASS at 46",
        [rt3["rules"]["T1"]["pass"], rt3["rules"]["T1"]["scored"], rt3["rules"]["T1"]["verdict"], rt3["rules"]["T2"]["verdict"],
         rt3["rules"]["T3"]["scored"]], [42, 46, "PASS", "PASS", 46])
    # (4) the family check (REPORTED): day A every family MM1-v1; day B (F1's cycles) every time family F1; day J mixed
    fA = family_check(scA, FZ, [], [], B=2000)
    chk("4.A H1 families (stated 7 of 7 MM1-v1, p 2/2^7, MM1-v1 BETTER)",
        [fA["H1"]["families_mm1_closer"], fA["H1"]["families_other_closer"], fA["H1"]["p_two_sided"], fA["H1"]["verdict_REPORTED"]],
        [7, 0, 2 / 2 ** 7, "MM1-v1 BETTER"])
    chk("4.A H4 families (stated 8 of 8 MM1-v1)", [fA["H4"]["families_mm1_closer"], fA["H4"]["verdict_REPORTED"]], [8, "MM1-v1 BETTER"])
    scB = json.loads(json.dumps(S.score(S.standin_data(FZ, "B"), FZ), default=str))
    fB = family_check(scB, FZ, [], [], B=2000)
    chk("4.B H1 families (stated 7 of 7 F1, F1 BETTER)", [fB["H1"]["families_other_closer"], fB["H1"]["verdict_REPORTED"]], [7, "F1 BETTER"])
    scJ = json.loads(json.dumps(S.score(S.standin_data(FZ, "J"), FZ), default=str))
    fJ = family_check(scJ, FZ, [], [], B=2000)
    chk("4.J H1 families not unanimous (NOT DECIDED or TOO FEW)", fJ["H1"]["verdict_REPORTED"] in ("NOT DECIDED", "TOO FEW"), True)
    chk("4.A H1 bootstrap interval over the cases' mean d lies above 0", fA["H1"]["cluster_bootstrap"]["mean_d_95"][0] > 0, True)
    # (5) the labels files: the final file wins over step 6n's proposal; the proposal alone; none; an unknown label refused
    import tempfile
    with tempfile.TemporaryDirectory() as td:
        json.dump({"labels_proposed": {"points": ["b10"], "cases": []}}, open(os.path.join(td, "ranbefore-e207-card.json"), "w"))
        s1 = read_labels(FZ, None, td)
        json.dump({"points": [], "cases": []}, open(os.path.join(td, "ranbefore-e207-labels.json"), "w"))
        s2 = read_labels(FZ, None, td)
        s0 = read_labels(FZ, None, os.path.join(td, "nothing"))
        json.dump({"points": ["b99"], "cases": []}, open(os.path.join(td, "bad.json"), "w"))
        try:
            read_labels(FZ, os.path.join(td, "bad.json"))
            refused = False
        except SystemExit:
            refused = True
        chk("5. the proposal alone -> b10", s1[1], ["b10"])
        chk("5. the final file wins -> none", s2[1], [])
        chk("5. no file -> none", (s0[1], s0[2]), ([], []))
        chk("5. an unknown label refused", refused, True)
        # (6) the checks read: a stand-in data-e207.json with one point run missing its check
        d6 = S.standin_data(FZ, "A")
        for pid, pt in d6["arms"]["A"]["points"].items():
            for r in pt["runs"]:
                r["detail"] = {"checks_missing": 1 if (pid == "b07" and r["block"] == "pass2") else 0}
        json.dump(d6, open(os.path.join(td, "data-e207.json"), "w"))
        cr = checks_read(td)
        chk("6. the checks read: 1 run of 106 point runs and 3 tie runs", [cr["runs_with_checks_missing"], cr["runs"]], [1, 109])
    res["verdict"] = "PASS" if ok_all else "FAIL"
    json.dump(res, open(outp, "w"), indent=1, default=str)
    lines = [f"selftest-postscore: {res['verdict']} ({sum(1 for c in res['checks'].values() if c['ok'])} of {len(res['checks'])} checks as stated)"]
    for k, c in res["checks"].items():
        lines.append(f"  {'ok ' if c['ok'] else 'BAD'} {k}" + ("" if c["ok"] else f": got {c['got']}, want {c['want']}"))
    return res["verdict"] == "PASS", "\n".join(lines) + "\n"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("scored", nargs="?")
    ap.add_argument("--data-dir")
    ap.add_argument("--labels")
    ap.add_argument("--out")
    ap.add_argument("--selftest")
    a = ap.parse_args()
    if a.selftest:
        ok, txt = selftest(a.selftest)
        sys.stdout.write(txt)
        sys.exit(0 if ok else 1)
    if not a.scored:
        ap.error("SCORED.json, or --selftest OUT.json")
    FZ = S.load_frozen()
    o = run(a.scored, FZ, a.data_dir, a.labels)
    if a.out:
        json.dump(o, open(a.out, "w"), indent=1, default=str)
    sys.stdout.write(words(o))


if __name__ == "__main__":
    main()
