#!/usr/bin/env python3
"""E180's scorer, v2 (the registration's dated note A1 sections 1, 4, 5 and 7; the kit's dated note 1 section 2).

    python3 tools/claims-v3/e180/score_e180_v2.py --reduced reduced-e180-v2.json --out scored-e180 [--card aifoundry3]
        [--elfcheck <the box's elfcheck-e180.txt>]          writes scored-e180.json and scored-e180.md; prints one line a rule

Every registered rule is v1's (score_e180.py, which stays as committed, imported and run unchanged on the same reduced session: v2's
reduction returns v1's D untouched), with A1's two registered additions:
  A1-7  check_elf_e180.py's line for mode 261 (the box's kernel disassembly, copied back with the session's logs): FAIL makes E180-A NOT
        SCORED ("the sums do not walk as registered"), v1's record kept beside; UNREAD or no file: scored as registered, labelled "walk
        not verified"; PASS: labelled "walk verified by disassembly". A FAIL for 262 marks the fadd.pi.acc kinds' reported readings.
  A1-5  E180-A's SIZE is reported against P's hart-offset band (offset-e180-a1.json: +0.752 to +4.261 W on aifoundry3), and its arm
        reading is not a price test; its SIGN is the registered verdict.
  A1-1  E180-L's SIZE is flagged footing-limited when P's slope sits within 0.002 W a bit of either end of L's interval.
And the reported arms of A1 section 4 (never a verdict; each a mean over the kept passes with power_e180.py's 95% interval, and where each
arm's frozen forecast sits): RA1 fadd.ps const - zeros on the board (as registered), on D_FL1, on D_E60 and on the net minion rail R;
RA2 his pair (E180-H's statistic) on R, D_FL1 and D_E60; RA3 the ladder slope (E180-L's statistic) on R, D_FL1 and D_E60; RA4 E180-A's
statistic on R; RA5 the anchors (const and random above zeros) on the board and R beside the catalogue's 26 Sep rows (the board's from
noise/noise-e180.json's over_idle_w rows, the rail's from footing-e180-a1.json's pJ times the card's fadd.ps rate); the die rise per
kind, a kind more than 0.5 C off the median named. The rail forecasts are the board's times footing-e180-a1.json's share (0.7741 on
aifoundry3); the forecasts on D_FL1 and D_E60 are footing-e180-a1.json's prices on those footings (P scaled by its price ratio).
SPDX-License-Identifier: Apache-2.0
"""
import argparse
import json
import math
import os
import statistics as st
import sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import power_e180 as pw  # noqa: E402
import score_e180 as s1  # noqa: E402  (v1's rules, unchanged)

ARMS = s1.ARMS
FOOTING_LIMIT = 0.002
RISE_FLAG_C = 0.5


def elf_reading(path):
    """{'261': PASS|FAIL|UNREAD, '262': ...} from check_elf_e180.py's lines; UNREAD for a missing file or line"""
    v = {"261": "UNREAD", "262": "UNREAD", "file": bool(path and os.path.exists(path))}
    if v["file"]:
        for ln in open(path, errors="replace"):
            for m in ("261", "262"):
                if f"mode {m}:" in ln and ln.split()[0] in ("PASS", "FAIL", "UNREAD"):
                    v[m] = ln.split()[0]
    return v


def where(lo, hi, f):
    return "inside" if lo <= f <= hi else "above" if f > hi else "below"


def reading(xs, fore):
    if len(xs) < 2:
        return {"n": len(xs), "verdict_free": "fewer than 2 kept passes"}
    m, lo, hi = pw.interval(xs)
    return {"n": len(xs), "x": xs, "mean": m, "lo": lo, "hi": hi, "forecast": fore,
            "where": {a: where(lo, hi, v) for a, v in fore.items()}}


def score(red, fc, card, foot, offset, elf, noise):
    out = s1.score(red, fc, card)                     # every registered rule, v1's code on v1's D
    K = fc["kinds"]
    W = {n: K[n]["W"][card] for n in K}
    passes = sorted(red["passes"])
    share = foot["F5_rail"]["share_minion_A_of_board"][card]
    pr = foot["F2_prices_by_footing"]
    pP = fc["prices"][f"P@{card}"]["pN_fJ"]
    scale = {"D": 1.0, "R": share}
    if card == "aifoundry3":
        scale.update({"D_FL1": pr["FL1"]["P_pN_fJ"] / pP, "D_E60": pr["E60_inrun"]["P_pN_fJ"] / pP})
    v2 = {"rail_share": share, "elfcheck": elf, "notes": []}

    def val(p, key, nm):
        return red["passes"][p]["D"][nm] if key == "D" else red["passes"][p].get(key, {}).get(nm)

    def series(key, f):
        xs = []
        for p in passes:
            try:
                x = f(lambda nm: val(p, key, nm))
            except TypeError:
                continue
            if x is not None:
                xs.append(x)
        return xs

    def fore(key, g):
        s = scale[key]
        return {a: s * g(a) for a in (ARMS if key in ("D", "R") else ("P",))}

    keys = [k for k in ("D", "D_FL1", "D_E60", "R") if k in scale]
    cz = lambda a: W["fadd.ps/const"][a] - W["fadd.ps/zeros"][a]
    hp = lambda a: W["fadd.ps/f_5"][a] - W["fadd.ps/f_4"][a]
    aa = lambda a: (W["fadd.ps.acc/f_4"][a] - W["fadd.ps.acc/zeros"][a]) - (W["fadd.ps/f_4"][a] - W["fadd.ps/zeros"][a])
    v2["RA1_const_minus_zeros"] = {k: reading(series(k, lambda g: g("fadd.ps/const") - g("fadd.ps/zeros")), fore(k, cz)) for k in keys}
    v2["RA2_his_pair"] = {k: reading(series(k, lambda g: g("fadd.ps/f_5") - g("fadd.ps/f_4")), fore(k, hp)) for k in keys if k != "D"}
    ladder = fc["ladder"]["kinds"]
    xres = [K[nm]["result_popcount"] for nm in ladder]
    fs = {a: pw.ols(xres, [W[nm][a] for nm in ladder]) for a in ARMS}
    v2["RA3_ladder_slope"] = {k: reading(series(k, lambda g: pw.ols(xres, [g(nm) - g("fadd.ps/zeros") for nm in ladder])),
                                         {a: scale[k] * fs[a] for a in (ARMS if k == "R" else ("P",))}) for k in keys if k != "D"}
    v2["RA4_A_on_rail"] = reading(series("R", lambda g: (g("fadd.ps.acc/f_4") - g("fadd.ps.acc/zeros")) -
                                         (g("fadd.ps/f_4") - g("fadd.ps/zeros"))), fore("R", aa))
    # RA5: the anchors beside the catalogue's 26 Sep rows: the board's in W from the registration's noise rows (over_idle_w per pass);
    # the rail's (footing A) in pJ from footing-e180-a1.json, times the card's registered fadd.ps rate
    v2["RA5_anchors"] = {}
    rows = noise["cards"][card]["rows"]
    rate = W["fadd.ps/f_4"]["rate"]
    f5 = foot["F5_rail"]
    for nm, ck in (("fadd.ps/const", "const"), ("fadd.ps/random", "random")):
        board = st.mean(rows[f"fadd.ps/{ck}/h2"]["over_idle_w"]) - st.mean(rows["fadd.ps/zeros/h2"]["over_idle_w"])
        rail_pj = (f5["const_minus_zeros_pj_committed"]["minion_A"]["per_card"][card] if ck == "const"
                   else f5["random_minus_zeros_pj"][card]["minion_A"])
        v2["RA5_anchors"][f"{nm} - zeros, D"] = reading(series("D", lambda g: g(nm) - g("fadd.ps/zeros")), {"catalogue": board})
        v2["RA5_anchors"][f"{nm} - zeros, R"] = reading(series("R", lambda g: g(nm) - g("fadd.ps/zeros")),
                                                        {"catalogue": rail_pj * 1e-12 * rate})
    # the die rise per kind
    rise = {}
    for nm in K:
        xs = [red["passes"][p].get("rise", {}).get(nm) for p in passes]
        xs = [x for x in xs if x is not None]
        if xs:
            rise[nm] = {"mean": st.mean(xs), "min": min(xs), "max": max(xs)}
    if rise:
        med = st.median(v["mean"] for v in rise.values())
        v2["rise"] = {"per_kind": rise, "median_c": med,
                      "off_median": sorted(nm for nm, v in rise.items() if abs(v["mean"] - med) > RISE_FLAG_C)}
    r = out["rules"]
    # A1-1: the footing-limited flag on E180-L's SIZE
    L = r.get("E180-L", {})
    if "lo" in L:
        fP = L["forecast"]["P"]
        lim = min(abs(fP - L["lo"]), abs(fP - L["hi"])) <= FOOTING_LIMIT
        L["footing_limited"] = lim
        if lim:
            v2["notes"].append(f"E180-L: P's slope {fP:.5f} sits within {FOOTING_LIMIT} W a bit of its interval's edge: footing-limited (A1-1)")
    # A1-5: E180-A against P's offset band; its arm reading is not a price test
    A = r.get("E180-A", {})
    band = offset["P_range_W"]
    if "lo" in A:
        A["offset_band_P_W"] = band
        A["inside_offset_band"] = A["hi"] >= band[0] and A["lo"] <= band[1]
        A["size_reading"] = ("not separated from the harts' start offset" if A["inside_offset_band"] and A["size"]["P"] != "PASS"
                             else "as registered" if A["size"]["P"] == "PASS" else "outside P's offset band")
        A["arm_reading"] = "not a price test (A1 section 5)"
    # A1-7: the disassembly's reading
    lab = {"PASS": "walk verified by disassembly", "UNREAD": "walk not verified", "FAIL": "the sums do not walk as registered"}
    if elf["261"] == "FAIL" and "verdict" in A:
        r["E180-A"] = {"verdict": "NOT SCORED", "why": "A1-7: check_elf_e180.py read FAIL for mode 261: the sums do not walk as registered",
                       "v1": A}
    elif "verdict" in A:
        A["walk"] = lab[elf["261"]]
    v2["walk_labels"] = {"fadd.ps.acc": lab[elf["261"]], "fadd.pi.acc": lab[elf["262"]]}
    out["reported_v2"] = v2
    return out


def md(s):
    L = [s1.md(s).rstrip("\n"), "", "## Reported beside, never a verdict (E180.md.dated-note-A1.md)", ""]
    v = s["reported_v2"]
    L.append(f"- The accumulating sums: fadd.ps.acc {v['walk_labels']['fadd.ps.acc']}; fadd.pi.acc {v['walk_labels']['fadd.pi.acc']} "
             f"(A1-7; check_elf_e180.py {'read' if v['elfcheck']['file'] else 'not found'}).")
    A = s["rules"].get("E180-A", {})
    if "offset_band_P_W" in A:
        L.append(f"- E180-A against P's hart-offset band {A['offset_band_P_W'][0]:+.3f} to {A['offset_band_P_W'][1]:+.3f} W: SIZE "
                 f"{A['size_reading']}; its arm reading is not a price test (A1 section 5).")
    if s["rules"].get("E180-L", {}).get("footing_limited") is not None:
        L.append(f"- E180-L footing-limited (A1-1): {s['rules']['E180-L']['footing_limited']}.")
    def line(name, rec):
        if "mean" not in rec:
            return f"- {name}: {rec.get('verdict_free', 'no reading')}"
        w = "; ".join(f"{a} {f:+.4f} {rec['where'][a]}" for a, f in rec["forecast"].items())
        return f"- {name}: {rec['mean']:+.4f} (95% {rec['lo']:+.4f} to {rec['hi']:+.4f}){'; forecasts: ' + w if w else ''}"
    for k, rec in v["RA1_const_minus_zeros"].items():
        L.append(line(f"RA1 fadd.ps const - zeros on {k} (W)", rec))
    for k, rec in v["RA2_his_pair"].items():
        L.append(line(f"RA2 his pair on {k} (W)", rec))
    for k, rec in v["RA3_ladder_slope"].items():
        L.append(line(f"RA3 the ladder slope on {k} (W a bit)", rec))
    L.append(line("RA4 E180-A's statistic on R (W)", v["RA4_A_on_rail"]))
    for k, rec in v["RA5_anchors"].items():
        L.append(line(f"RA5 {k} (W)", rec))
    if "rise" in v:
        L.append(f"- The die rise per kind: median {v['rise']['median_c']:.3f} C; more than {RISE_FLAG_C} C off it: "
                 f"{', '.join(v['rise']['off_median']) or 'none'}.")
    for n in v["notes"]:
        L.append(f"- {n}")
    return "\n".join(L) + "\n"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--reduced", required=True)
    ap.add_argument("--out", required=True, help="prefix: writes <out>.json and <out>.md")
    ap.add_argument("--card", default="aifoundry3")
    ap.add_argument("--forecast", default=os.path.join(HERE, "forecast-e180.json"))
    ap.add_argument("--footing", default=os.path.join(HERE, "footing-e180-a1.json"))
    ap.add_argument("--offset", default=os.path.join(HERE, "offset-e180-a1.json"))
    ap.add_argument("--noise", default=os.path.join(HERE, "noise", "noise-e180.json"))
    ap.add_argument("--elfcheck", default=None)
    a = ap.parse_args()
    s = score(s1.load(a.reduced), s1.load(a.forecast), a.card, s1.load(a.footing), s1.load(a.offset), elf_reading(a.elfcheck),
              s1.load(a.noise))
    json.dump(s, open(a.out + ".json", "w"), indent=1, sort_keys=True)
    open(a.out + ".md", "w").write(md(s))
    for k, r in s["rules"].items():
        print(f"{k}: {r['verdict']}")


if __name__ == "__main__":
    main()
