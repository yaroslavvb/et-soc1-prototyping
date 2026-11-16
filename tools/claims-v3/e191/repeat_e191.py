#!/usr/bin/env python3
"""E191's repeat reading (E191.md's dated amendment A2 and the kit's dated note 3, Q190, Sun 15 Nov 2026, PST; written after E189's data
commit fa9098c4 and after E191's second session's data commit 7156ac15, before any datum of a third session): the third session's
frozen-scorer output set beside the second session's, whose rules are E191's registered verdicts. REPORTED: nothing here is a verdict, and
nothing here changes one.

    /usr/bin/python3 -I -B tools/claims-v3/e191/repeat_e191.py S2_SCORES S3_SCORES [--out FILE]
    /usr/bin/python3 -I -B tools/claims-v3/e191/repeat_e191.py --selftest S2_SCORES

S2_SCORES and S3_SCORES are score_e191.py's own outputs (its --out JSON, unchanged), the first on the second session's committed directory
(docs/reports/data/2026-11-15-e191-blind-day-aifoundry1-c1-s2/), the second on the third session's (...-c1-s3/); step 13 v3 writes both and
then runs this. For each configuration it reports, per session: the passes scored; S1's error (e_j_over), S1T's (e_j_total), S2's ratio (the
mean t_k over the frozen point) with whether the mean t_k is inside the frozen band, and S2T's error (e_j_total_forecast), each as the frozen
scorer computed it; each error's spread over the session's passes (the sample standard deviation of the per-pass errors); the measured means
(J over idle, J with the card at rest, t_k and T0 a launch); and whether the configuration meets each rule. Then the differences, the third
session minus the second: each error in percentage points, each measured mean as a ratio, and S1's and S1T's differences over the two
sessions' combined standard error, sqrt(sd2^2/n2 + sd3^2/n3) of the per-pass errors (a desk statistic, REPORTED, deciding nothing). A
configuration with NO DATA in either session has no difference. The rules: the second session's words (E191's registered verdicts, which
stand) beside the third session's words as the frozen scorer reads that directory (REPORTED: never a verdict of E191, never in place of one).
The registered arms v2.1 and v2c are carried the same way (REPORTED in both sessions). Standard library only; reads two files and writes one.
Exit 0 when read (whatever the words), 2 when an input is not the frozen scorer's form. SPDX-License-Identifier: Apache-2.0
"""
import copy
import hashlib
import json
import math
import os
import sys

ORDER = ["copy-zeros", "copy-random", "sha256", "sort-sorted", "sort-shuffled", "sparse-parity"]
RULES = ["E191-S1", "E191-S1T", "E191-S2", "E191-S2T"]
LABEL = ("REPORTED (E191.md's dated amendment A2): the third session's frozen-scorer output beside the second session's; E191's registered "
         "verdicts are the second session's and stand; nothing here is a verdict or replaces one")


class Refused(Exception):
    pass


def sd(xs):
    if len(xs) < 2:
        return None
    m = sum(xs) / len(xs)
    return math.sqrt(sum((x - m) ** 2 for x in xs) / (len(xs) - 1))


def mean(xs):
    return sum(xs) / len(xs) if xs else None


def check_form(r, which):
    if not isinstance(r, dict):
        raise Refused(f"{which}: not a JSON object")
    for k in ("configs", "rules", "verdict_of_the_day"):
        if k not in r:
            raise Refused(f"{which}: no '{k}' (not score_e191.py's day output)")
    miss = [k for k in ORDER if k not in r["configs"]]
    if miss:
        raise Refused(f"{which}: configurations missing: {', '.join(miss)}")
    miss = [k for k in RULES if k not in r["rules"] or k not in r["verdict_of_the_day"]]
    if miss:
        raise Refused(f"{which}: rules missing: {', '.join(miss)}")
    for k in ORDER:
        c = r["configs"][k]
        if c.get("verdict") == "NO DATA":
            continue
        need = ("passes", "per_pass", "e_j_over", "e_j_total", "e_j_total_forecast", "t_k_mean", "t_point", "t_inside_band",
                "measured_j_over_mean", "measured_j_total_mean", "forecast_j_total_at_forecast", "ok_S1", "ok_S1T", "ok_S2", "ok_S2T")
        miss = [f for f in need if f not in c]
        if miss:
            raise Refused(f"{which}: {k} lacks {', '.join(miss)}")


def side(c):
    """One session's reading of one configuration (the frozen scorer's numbers, plus the spreads over its passes)."""
    if c.get("verdict") == "NO DATA":
        return {"reading": "NO DATA", "passes": c.get("passes", 0)}
    pp = c["per_pass"]
    f_tot = c["forecast_j_total_at_forecast"]
    return {
        "reading": "scored", "passes": c["passes"],
        "e_j_over": c["e_j_over"], "e_j_over_pass_sd": sd([p["err_j_over"] for p in pp]),
        "e_j_total": c["e_j_total"], "e_j_total_pass_sd": sd([p["err_j_total"] for p in pp]),
        "t_ratio": c["t_k_mean"] / c["t_point"], "t_inside_band": c["t_inside_band"],
        "e_j_total_forecast": c["e_j_total_forecast"], "e_j_total_forecast_pass_sd": sd([f_tot / p["measured_j_total"] - 1.0 for p in pp]),
        "measured_j_over_mean": c["measured_j_over_mean"], "measured_j_total_mean": c["measured_j_total_mean"],
        "t_k_mean": c["t_k_mean"], "T0_mean": mean([p["T0"] for p in pp]),
        "meets": {"E191-S1": c["ok_S1"], "E191-S1T": c["ok_S1T"], "E191-S2": c["ok_S2"], "E191-S2T": c["ok_S2T"]},
    }


def z(d, a, b, sa, sb):
    """d over sqrt(sa^2/na + sb^2/nb): None when a spread is unknown or both are zero."""
    if sa is None or sb is None:
        return None
    se = math.sqrt(sa * sa / a + sb * sb / b)
    return d / se if se > 0 else None


def compare(s2, s3, names=("S2_SCORES", "S3_SCORES"), shas=(None, None)):
    check_form(s2, names[0])
    check_form(s3, names[1])
    out = {"what": "E191's repeat reading (repeat_e191.py)", "label": LABEL,
           "inputs": {"second_session": {"file": names[0], "sha256": shas[0]}, "third_session": {"file": names[1], "sha256": shas[1]}},
           "registered_verdicts": {"label": "E191's registered verdicts: the second session's (E191.md 8.3 by the frozen scorer); they stand",
                                   "words": {k: s2["verdict_of_the_day"][k] for k in RULES}},
           "repeat_words": {"label": "REPORTED: the frozen scorer's words on the third session's directory; never a verdict of E191",
                            "words": {k: s3["verdict_of_the_day"][k] for k in RULES}},
           "configs": {}, "rules": {}, "arms": {}}
    ncmp = nod = 0
    for k in ORDER:
        a, b = side(s2["configs"][k]), side(s3["configs"][k])
        row = {"second_session": a, "third_session": b}
        if a["reading"] == "NO DATA" or b["reading"] == "NO DATA":
            row["difference"] = "NO DATA (no difference: a configuration with NO DATA in either session)"
            nod += 1
        else:
            ncmp += 1
            d1, d1t, d2t = b["e_j_over"] - a["e_j_over"], b["e_j_total"] - a["e_j_total"], b["e_j_total_forecast"] - a["e_j_total_forecast"]
            row["difference"] = {
                "label": "REPORTED: the third session minus the second",
                "e_j_over_points": 100.0 * d1, "e_j_total_points": 100.0 * d1t, "e_j_total_forecast_points": 100.0 * d2t,
                "t_ratio_points": 100.0 * (b["t_ratio"] - a["t_ratio"]),
                "measured_j_over_ratio": b["measured_j_over_mean"] / a["measured_j_over_mean"] - 1.0,
                "measured_j_total_ratio": b["measured_j_total_mean"] / a["measured_j_total_mean"] - 1.0,
                "t_k_ratio": b["t_k_mean"] / a["t_k_mean"] - 1.0, "T0_mean_c": b["T0_mean"] - a["T0_mean"],
                "e_j_over_over_combined_se": z(d1, a["passes"], b["passes"], a["e_j_over_pass_sd"], b["e_j_over_pass_sd"]),
                "e_j_total_over_combined_se": z(d1t, a["passes"], b["passes"], a["e_j_total_pass_sd"], b["e_j_total_pass_sd"]),
                "meets_same": {r: a["meets"][r] == b["meets"][r] for r in RULES},
            }
        out["configs"][k] = row
    for r in RULES:
        x, y = s2["rules"][r], s3["rules"][r]
        e = {"second_session": {"registered_verdict": x["verdict"], "scored": x["scored"], "within": x["within"], "outside": x["outside"]},
             "third_session": {"word": y["verdict"], "scored": y["scored"], "within": y["within"], "outside": y["outside"],
                               "label": "REPORTED, never a verdict"}}
        if r == "E191-S1":
            e["second_session"]["rms_e_j_over"] = x.get("rms_e_j_over")
            e["third_session"]["rms_e_j_over"] = y.get("rms_e_j_over")
        out["rules"][r] = e
    for arm in ("v2.1", "v2c"):
        if arm in s2.get("arms", {}) and arm in s3.get("arms", {}):
            out["arms"][arm] = {"label": "a registered arm, REPORTED in both sessions (the day's verdict is the primary's)",
                                "second_session": {r: s2["arms"][arm]["rules"][r]["verdict"] for r in RULES},
                                "third_session": {r: s3["arms"][arm]["rules"][r]["verdict"] for r in RULES},
                                "sparse_parity_e_j_over": {
                                    "second_session": (s2["arms"][arm]["configs"].get("sparse-parity") or {}).get("e_j_over"),
                                    "third_session": (s3["arms"][arm]["configs"].get("sparse-parity") or {}).get("e_j_over")}}
    out["counts"] = {"compared": ncmp, "no_data": nod}
    return out


def f(x, nd=4, pct=False):
    if x is None:
        return "n/a"
    if isinstance(x, bool):
        return "yes" if x else "no"
    return f"{100.0 * x:+.{nd - 2}f}%" if pct else f"{x:+.{nd}f}"


def text(o):
    L = ["E191 repeat reading: " + o["label"],
         f"inputs: second session {o['inputs']['second_session']['file']} sha256 {o['inputs']['second_session']['sha256']}; "
         f"third session {o['inputs']['third_session']['file']} sha256 {o['inputs']['third_session']['sha256']}",
         "configuration | passes 2nd/3rd | S1 error 2nd, 3rd, difference (points), over the combined SE | S1T error 2nd, 3rd, difference, "
         "over the combined SE | S2 ratio (mean t_k / point) 2nd, 3rd | S2T error 2nd, 3rd, difference | J over idle, J at rest, t_k: 3rd/2nd - 1 "
         "| T0 mean 2nd, 3rd (C)"]
    for k in ORDER:
        row = o["configs"][k]
        a, b = row["second_session"], row["third_session"]
        if isinstance(row["difference"], str):
            L.append(f"{k} | {a['passes']}/{b['passes']} | {a['reading']} / {b['reading']}: {row['difference']}")
            continue
        d = row["difference"]
        L.append(f"{k} | {a['passes']}/{b['passes']} | {f(a['e_j_over'], pct=True)}, {f(b['e_j_over'], pct=True)}, {d['e_j_over_points']:+.2f}, "
                 f"{f(d['e_j_over_over_combined_se'], 2)} | {f(a['e_j_total'], pct=True)}, {f(b['e_j_total'], pct=True)}, "
                 f"{d['e_j_total_points']:+.2f}, {f(d['e_j_total_over_combined_se'], 2)} | {a['t_ratio']:.4f}, {b['t_ratio']:.4f} | "
                 f"{f(a['e_j_total_forecast'], pct=True)}, {f(b['e_j_total_forecast'], pct=True)}, {d['e_j_total_forecast_points']:+.2f} | "
                 f"{f(d['measured_j_over_ratio'], pct=True)}, {f(d['measured_j_total_ratio'], pct=True)}, {f(d['t_k_ratio'], pct=True)} | "
                 f"{a['T0_mean']:.2f}, {b['T0_mean']:.2f}")
    for r in RULES:
        e = o["rules"][r]
        x, y = e["second_session"], e["third_session"]
        rx = f", rms {x['rms_e_j_over']:.4f}" if x.get("rms_e_j_over") is not None else ""
        ry = f", rms {y['rms_e_j_over']:.4f}" if y.get("rms_e_j_over") is not None else ""
        L.append(f"{r}: the registered verdict (the second session's, it stands) {x['registered_verdict']} ({x['within']} of {x['scored']} "
                 f"within{rx}); the third session's word, REPORTED {y['word']} ({y['within']} of {y['scored']} within{ry})")
    for arm, e in o["arms"].items():
        L.append(f"arm {arm} (REPORTED in both): second session " + ", ".join(f"{r} {e['second_session'][r]}" for r in RULES) +
                 "; third session " + ", ".join(f"{r} {e['third_session'][r]}" for r in RULES))
    L.append(f"REPEAT-E191 REPORTED: {o['counts']['compared']} configurations compared, {o['counts']['no_data']} with NO DATA in a session; "
             f"the registered verdicts stand: " + ", ".join(f"{r} {o['registered_verdicts']['words'][r]}" for r in RULES))
    return "\n".join(L)


def load(p):
    b = open(p, "rb").read()
    return json.loads(b), hashlib.sha256(b).hexdigest()


def walk_keys(o):
    if isinstance(o, dict):
        for k, v in o.items():
            yield k
            yield from walk_keys(v)
    elif isinstance(o, list):
        for v in o:
            yield from walk_keys(v)


def selftest(p2):
    s2, h2 = load(p2)
    res = []

    def ok(name, cond, why=""):
        res.append((name, bool(cond), why))

    # RS1: the second session beside itself: every difference zero, the words the same, nothing a verdict of the third
    o = compare(s2, copy.deepcopy(s2), ("s2.json", "s2.json"), (h2, h2))
    diffs = [v for k in ORDER for kk, v in o["configs"][k]["difference"].items() if isinstance(v, float)] \
        if all(isinstance(o["configs"][k]["difference"], dict) for k in ORDER) else [1.0]
    ok("RS1", o["counts"] == {"compared": 6, "no_data": 0} and all(v == 0.0 for v in diffs)
       and o["registered_verdicts"]["words"] == s2["verdict_of_the_day"] and o["repeat_words"]["words"] == s2["verdict_of_the_day"]
       and all(all(o["configs"][k]["difference"]["meets_same"].values()) for k in ORDER),
       f"the second session beside itself: {len(diffs)} differences, all zero; 6 compared")
    # RS2: a synthetic third session (each figure moved by a known amount): the differences read exactly those amounts
    s3 = copy.deepcopy(s2)
    inj = {}
    for i, k in enumerate(ORDER):
        c = s3["configs"][k]
        inj[k] = (0.01 * (i + 1), -0.005, 0.02, 1.02, 1.01)
        c["e_j_over"] += inj[k][0]
        c["e_j_total"] += inj[k][1]
        c["e_j_total_forecast"] += inj[k][2]
        c["measured_j_over_mean"] *= inj[k][3]
        c["t_k_mean"] *= inj[k][4]
    s3["verdict_of_the_day"]["E191-S1T"] = "FAIL"
    s3["rules"]["E191-S1T"]["verdict"] = "FAIL"
    o = compare(s2, s3, ("s2.json", "s3-synthetic.json"), (h2, None))
    good = True
    for k in ORDER:
        d = o["configs"][k]["difference"]
        good &= abs(d["e_j_over_points"] - 100 * inj[k][0]) < 1e-9 and abs(d["e_j_total_points"] - 100 * inj[k][1]) < 1e-9
        good &= abs(d["e_j_total_forecast_points"] - 100 * inj[k][2]) < 1e-9 and abs(d["measured_j_over_ratio"] - (inj[k][3] - 1)) < 1e-12
        good &= abs(d["t_k_ratio"] - (inj[k][4] - 1)) < 1e-12 and abs(d["measured_j_total_ratio"]) < 1e-15
    ok("RS2", good and o["registered_verdicts"]["words"]["E191-S1T"] == s2["verdict_of_the_day"]["E191-S1T"]
       and o["repeat_words"]["words"]["E191-S1T"] == "FAIL" and o["rules"]["E191-S1T"]["third_session"]["word"] == "FAIL",
       "known moves read back exactly; the registered S1T stays the second session's while the third's word reads FAIL")
    # RS3: NO DATA in the third session for one configuration: no difference there, the other five compared
    s3 = copy.deepcopy(s2)
    s3["configs"]["sparse-parity"] = {"config": "sparse-parity", "verdict": "NO DATA", "passes": 1,
                                      "note": "fewer than 2 good passes: no data, never a failed prediction"}
    o = compare(s2, s3, ("s2.json", "s3-nodata.json"), (h2, None))
    ok("RS3", o["counts"] == {"compared": 5, "no_data": 1} and isinstance(o["configs"]["sparse-parity"]["difference"], str)
       and o["configs"]["sparse-parity"]["third_session"]["reading"] == "NO DATA", "sparse parity NO DATA: no difference; five compared")
    # RS4, RS5: inputs not of the frozen scorer's form are refused
    s3 = copy.deepcopy(s2)
    del s3["configs"]["sha256"]
    try:
        compare(s2, s3)
        ok("RS4", False, "a third session missing a configuration was read")
    except Refused as e:
        ok("RS4", "configurations missing: sha256" in str(e), f"refused: {e}")
    s3 = copy.deepcopy(s2)
    del s3["rules"]["E191-S2T"]
    try:
        compare(s2, s3)
        ok("RS5", False, "a third session missing a rule was read")
    except Refused as e:
        ok("RS5", "rules missing: E191-S2T" in str(e), f"refused: {e}")
    # RS6: on the third session's side no key is a verdict: its rule words are 'word', its configurations' 'reading'
    o = compare(s2, copy.deepcopy(s2), ("s2.json", "s2.json"), (h2, h2))
    third = [o["configs"][k]["third_session"] for k in ORDER] + [o["rules"][r]["third_session"] for r in RULES]
    ok("RS6", not any("verdict" in kk for t in third for kk in walk_keys(t)) and "registered_verdict" in o["rules"]["E191-S1"]["second_session"],
       "no 'verdict' key on the third session's side; the second session's rules carry 'registered_verdict'")
    # RS7: the text names REPORTED and the registered verdicts on its last line
    t = text(o)
    ok("RS7", t.splitlines()[-1].startswith("REPEAT-E191 REPORTED: 6 configurations compared") and "the registered verdicts stand" in t
       and all(f"{r} {s2['verdict_of_the_day'][r]}" in t.splitlines()[-1] for r in RULES), "the text's last line")
    # RS8: the spreads are the per-pass errors' sample sd (S1's equals the frozen scorer's own e_j_over_pass_sd)
    good = all(abs(side(s2["configs"][k])["e_j_over_pass_sd"] - s2["configs"][k]["e_j_over_pass_sd"]) < 1e-15 for k in ORDER)
    ok("RS8", good, "S1's spread equals the frozen scorer's e_j_over_pass_sd for every configuration")
    for name, good, why in res:
        print(f"{'PASS' if good else 'FAIL'} {name}: {why}")
    n = sum(1 for _, g, _ in res if g)
    print(f"REPEAT-E191 SELFTEST {n} of {len(res)} {'PASS' if n == len(res) else 'FAIL'} (the second session's scores sha256 {h2})")
    return 0 if n == len(res) else 1


def main(argv):
    if len(argv) == 2 and argv[0] == "--selftest":
        return selftest(argv[1])
    outp = None
    if "--out" in argv:
        i = argv.index("--out")
        outp = argv[i + 1]
        argv = argv[:i] + argv[i + 2:]
    if len(argv) != 2:
        print(__doc__)
        return 2
    try:
        s2, h2 = load(argv[0])
        s3, h3 = load(argv[1])
        o = compare(s2, s3, (os.path.basename(argv[0]), os.path.basename(argv[1])), (h2, h3))
    except (OSError, ValueError, Refused) as e:
        print(f"REPEAT-E191 REFUSED: {e}")
        return 2
    if outp:
        open(outp, "w").write(json.dumps(o, indent=1, sort_keys=True) + "\n")
    print(text(o))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
