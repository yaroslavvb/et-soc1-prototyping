#!/usr/bin/env python3
"""E183's dated note M1 (E183.md.dated-note-M1.md, section M1-4): the reader of october-forecast-model's two REPORTED arms, v3 and v4, on
E183's committed reduction. Written before any E183 datum. Python's standard modules only; opens no device, no box and no network.

    /usr/bin/python3 -B tools/claims-v3/e183/arm_m1_read_e183.py --reduced <reduced-e183.json> --out <prefix> [--scored <scored-e183.json>]
        [--m1 <m1-october-forecast-model-e183.json>]                                   # run from the lab repository's top

It writes <prefix>.json and <prefix>.txt and prints the text.

THE MEASURED SIDE is E183's own: each train's estimate and 95% interval from the reduction's processes by e183_stats.train_estimate (the
registration's statistics, imported unchanged, as score_e183.py takes them); b, c, E183-X's T6 - (6 b - c) and E183-J's T3 - T1 and
T4 - T2 by e183_stats; E183-MECH's word by e183_stats.mech_of on E183-B's and E183-C's NULL words (band +-0.004 W a bit). With --scored
(the scorer's file of the same reduction) every train, b, c and the MECH word must equal the scorer's, or the reader refuses (exit 3).
THE MODEL'S SIDE is the committed json's, refused unless its sha256 is the one pinned below (exit 2): for each arm (v3, v4) each train's
central and band on aifoundry3, the model's b, c, x and j's by the same formulas over the same trains the measured side used, and the
model's word (v3 RESULT, v4 BOTH).
THE WORDS, never a verdict and never an E183 rule: the model's central lies inside, above or below the measured 95% interval; its sign is
the estimate's or the other (no sign to compare when either is 0); the estimate lies inside, above or below the model's band; the
model's word is E183-MECH's word or a different one. A train E183 reads NOT SCORED (or that did not run) is not read, and neither is a
quantity made from it. Card 1's figures and the kinds' levels are not read (E183 runs on aifoundry3 and reads no level).
SPDX-License-Identifier: Apache-2.0
"""
import argparse
import hashlib
import json
import os
import sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import e183_common as E  # noqa: E402  (unchanged: the plan)
import e183_stats as S   # noqa: E402  (unchanged: it refuses e182_stats.py off its registered sha256)

M1_JSON = os.path.join(HERE, "m1-october-forecast-model-e183.json")
M1_JSON_SHA256 = "fe81bf2d0c2857b8bf88420c3942514852164b6e3332c2e4aba408153a94aea3"
TRAINS = ("T1", "T2", "T3", "T4", "T5", "T6")
ARMS = ("v3", "v4")
EPS = 1e-12


def sha256(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def where(m, iv):
    return "inside" if iv["lo"] <= m <= iv["hi"] else ("above" if m > iv["hi"] else "below")


def sign_word(m, est):
    if est is None or m == 0 or est == 0:
        return "no sign to compare"
    return "the estimate's sign" if (m > 0) == (est > 0) else "the other sign"


def in_band(est, band):
    lo, hi = band
    return "inside the model's band" if lo <= est <= hi else ("above the model's band" if est > hi else "below the model's band")


def measured(red, plan):
    by_train = {b["train"]: b for b in red["blocks"].values()}
    T = {}
    for t in plan["trains"]:
        b = by_train.get(t["train"])
        if b is None:
            T[t["train"]] = {"mean": None, "se": None, "df": None, "lo": None, "hi": None, "why": "not run or set aside"}
            continue
        T[t["train"]] = S.train_estimate([(o, q) for o, q in b["processes"]])
    b, hb = S.price_b(T)
    c, hc = S.price_c(T)
    x, used = S.x_resid(T)
    jr, jo = S.j_diff(T, "T1", "T3"), S.j_diff(T, "T2", "T4")
    vb, vc = S.null_of(b, S.NULL_BAND_W), S.null_of(c, S.NULL_BAND_W)
    return {"T": T, "b": b, "hb": hb, "c": c, "hc": hc, "x": x, "x_used": used, "j_T3_minus_T1": jr, "j_T4_minus_T2": jo,
            "B_word": vb, "C_word": vc, "mech": S.mech_of(vb, vc)}


def same(a, b):
    return (a is None and b is None) or (a is not None and b is not None and abs(a - b) <= EPS * max(1.0, abs(a), abs(b)))


def cross_check(M, sc):
    bad = []
    for t in TRAINS:
        m, s = M["T"].get(t, {}), sc["trains"].get(t, {})
        for k in ("mean", "lo", "hi"):
            if not same(m.get(k), s.get(k)):
                bad.append(f"{t} {k}: {m.get(k)} against the scorer's {s.get(k)}")
    for q, rule, key in (("b", "E183-B", "b"), ("c", "E183-C", "c")):
        for k in ("mean", "lo", "hi"):
            if not same(M[q].get(k), sc["rules"][rule][key].get(k)):
                bad.append(f"{q} {k}: {M[q].get(k)} against the scorer's {sc['rules'][rule][key].get(k)}")
    if M["mech"] != sc["rules"]["E183-MECH"]["verdict"]:
        bad.append(f"E183-MECH {M['mech']} against the scorer's {sc['rules']['E183-MECH']['verdict']}")
    return bad


def model_combo(mt, terms):
    return sum(a * mt[t] for a, t in terms)


def read(M, m1):
    out = {"_what": "october-forecast-model's two REPORTED arms (v3, v4) read on E183's reduction by E183.md.dated-note-M1.md section M1-4; "
                    "never a verdict, never an E183 rule", "freeze_lines": m1["freeze_lines"],
           "column": "model: W above the fadd.ps zeros at E183's registered rate (aifoundry3 board); E183: W at the board, D(first) - D(second)",
           "measured": {}, "arms": {}}
    T = M["T"]
    for t in TRAINS:
        iv = T.get(t, {})
        out["measured"][t] = ({"mean": iv["mean"], "lo": iv["lo"], "hi": iv["hi"], "units": iv.get("units")} if S.scored(iv)
                              else {"read": "NOT SCORED", "why": iv.get("why")})
    for q in ("b", "c", "x", "j_T3_minus_T1", "j_T4_minus_T2"):
        iv = M[q]
        out["measured"][q] = {"mean": iv["mean"], "lo": iv["lo"], "hi": iv["hi"]} if S.scored(iv) else {"read": "NOT SCORED"}
    out["measured"]["b_from"], out["measured"]["c_from"] = M["hb"], M["hc"]
    out["measured"]["E183-MECH"] = {"word": M["mech"], "B": M["B_word"], "C": M["C_word"]}
    lines = ["october-forecast-model's reported arms for E183 (E183.md.dated-note-M1.md, M1-4): v3 and v4 against E183's measured trains",
             "  " + m1["freeze_lines"]["v3"], "  " + m1["freeze_lines"]["v4"],
             "  the model: W above the fadd.ps zeros at E183's rate (aifoundry3 board); E183: W at the board; REPORTED, never a rule"]
    for v in ARMS:
        mt = {t: m1["trains"][t][v]["aifoundry3"]["central_W"] for t in TRAINS}
        mb = {t: m1["trains"][t][v]["aifoundry3"]["band_W"] for t in TRAINS}
        A = {"trains": {}, "prices": {}, "word": {}}
        lines.append(f"ARM {v} (october-forecast-model {v}):")
        for t in TRAINS:
            iv = T.get(t, {})
            if not S.scored(iv):
                A["trains"][t] = {"model_W": mt[t], "read": "not read: E183 reads this train NOT SCORED", "why": iv.get("why")}
                lines.append(f"  {t}: model {mt[t]:+.5f} W; not read (the train is NOT SCORED: {iv.get('why')})")
                continue
            w, s, bd = where(mt[t], iv), sign_word(mt[t], iv["mean"]), in_band(iv["mean"], mb[t])
            A["trains"][t] = {"model_W": mt[t], "model_band_W": mb[t], "estimate_W": iv["mean"], "lo": iv["lo"], "hi": iv["hi"],
                              "units": iv.get("units"), "model_reads": w, "sign": s, "estimate_against_band": bd,
                              "model_minus_estimate_W": mt[t] - iv["mean"]}
            lines.append(f"  {t}: model {mt[t]:+.5f} W against {iv['mean']:+.5f} [{iv['lo']:+.5f}, {iv['hi']:+.5f}] W ({iv.get('units')} units): "
                         f"{w}, {s}; the estimate {bd} [{mb[t][0]:+.5f}, {mb[t][1]:+.5f}]")
        # the prices and checks, by E183.md section 5.1's formulas over the trains the measured side used
        forms = {"b": [(1.0 / (7 * len(M["hb"])), t) for t in M["hb"]] if M["hb"] else None,
                 "c": [(1.0 / (7 * len(M["hc"])), t) for t in M["hc"]] if M["hc"] else None}
        if M["x_used"]:
            hb, hc = M["hb"], M["hc"]
            forms["x"] = [(1.0, "T6")] + [(-6.0 / (7 * len(hb)), t) for t in hb] + [(1.0 / (7 * len(hc)), t) for t in hc]
        else:
            forms["x"] = None
        forms["j_T3_minus_T1"] = [(1.0, "T3"), (-1.0, "T1")]
        forms["j_T4_minus_T2"] = [(1.0, "T4"), (-1.0, "T2")]
        names = {"b": "b, W a result 1-bit (E183-B)", "c": "c, W an operand 1-bit (E183-C)", "x": "T6 - (6 b - c), W (E183-X)",
                 "j_T3_minus_T1": "T3 - T1, W (E183-J)", "j_T4_minus_T2": "T4 - T2, W (E183-J)"}
        for q in ("b", "c", "x", "j_T3_minus_T1", "j_T4_minus_T2"):
            iv = M[q]
            if forms[q] is None or not S.scored(iv):
                A["prices"][q] = {"read": "not read: E183 reads it NOT SCORED"}
                lines.append(f"  {names[q]}: not read (NOT SCORED)")
                continue
            mv = model_combo(mt, forms[q])
            w, s = where(mv, iv), sign_word(mv, iv["mean"])
            A["prices"][q] = {"model": mv, "from": [t for _, t in forms[q]], "estimate": iv["mean"], "lo": iv["lo"], "hi": iv["hi"],
                              "model_reads": w, "sign": s}
            lines.append(f"  {names[q]}: model {mv:+.6f} against {iv['mean']:+.6f} [{iv['lo']:+.6f}, {iv['hi']:+.6f}]: {w}, {s}")
        mw = m1["words"][v]
        if M["mech"] in ("NOT SCORED",):
            A["word"] = {"model": mw, "E183-MECH": M["mech"], "read": "not read: E183-MECH reads NOT SCORED"}
            lines.append(f"  the word: the model's {mw}; E183-MECH NOT SCORED: not read")
        else:
            rel = "the same word" if mw == M["mech"] else "a different word"
            A["word"] = {"model": mw, "E183-MECH": M["mech"], "reads": rel}
            lines.append(f"  the word: the model's {mw} beside E183-MECH's {M['mech']} (B {M['B_word']}, C {M['C_word']}): {rel}")
        out["arms"][v] = A
    lines.append("Not read: card 1's figures (E183 runs on aifoundry3 card 0) and the kinds' levels (E183 reads no level).")
    lines.append("Labels: REPORTED, never a rule; the model's figures are modelled and frozen before any E183 datum; E183's are blind "
                 "measurements.")
    out["not_read"] = ["card 1's figures", "the kinds' levels above zeros"]
    return out, lines


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--reduced", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--scored")
    ap.add_argument("--m1", default=M1_JSON)
    a = ap.parse_args()
    got = sha256(a.m1)
    if got != M1_JSON_SHA256:
        print(f"REFUSED: {os.path.basename(a.m1)} sha256 {got[:16]} is not the committed note's {M1_JSON_SHA256[:16]}")
        sys.exit(2)
    m1 = json.load(open(a.m1))
    M = measured(json.load(open(a.reduced)), E.plan())
    if a.scored:
        bad = cross_check(M, json.load(open(a.scored)))
        if bad:
            print("REFUSED: the reduction and the scorer's file disagree:\n  " + "\n  ".join(bad[:12]))
            sys.exit(3)
    out, lines = read(M, m1)
    out["inputs"] = {"reduced": os.path.basename(a.reduced), "scored": os.path.basename(a.scored) if a.scored else None,
                     "m1_json_sha256": got, "scored_cross_check": "equal" if a.scored else "not given"}
    json.dump(out, open(a.out + ".json", "w"), indent=1, sort_keys=True)
    open(a.out + ".txt", "w").write("\n".join(lines) + "\n")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
