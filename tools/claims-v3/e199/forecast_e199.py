#!/usr/bin/env python3
"""E199 (Q190, lane reg-e199): the forecast frozen for aifoundry1 card 1 before any card-1 X01 datum.

E199's forecast IS E192's measured, reduced prices on aifoundry3 card 0. Every price below is copied exactly (Python's json round
trip, no rounding, no arithmetic) from E192's committed outputs, `intbits-e192.json` and `checks-e192.json` (E192's data, dated
note 2, commit 117312b1), which this script reads only at their committed sha256. **E199 is NOT blind to E192's data: E192's data
is the forecast.**

It also freezes the scale allowance of THE TRANSPORT RULES' second rule (E199.md section 6.4) from its two named sources, each read
at its committed sha256:
  (1) the blind day's three scalar-integer programs, measured on both cards this week with the same hosts, arguments and counts:
      J over idle a launch (`energy.json` > `board.j_per_solve`, the mean of each configuration's four passes) for SHA-256, sort
      sorted and sort shuffled, E191's second session on aifoundry1 card 1 (7156ac15) over E189 on aifoundry3 card 0 (fa9098c4);
  (2) the energy catalogue's per-card means (the three-card check, 25-26 Sep 2026; `combined/<row>/per_card`) for the rows of
      E192's own ops: add, xor, and and nop on random and on zero operands with both harts, and add on random operands with one
      hart: card 1 (`aifoundry1-c1`) over `aifoundry3`.
The allowance is [min, max] of these twelve ratios and 1, each ratio rounded to 6 significant digits.

    /usr/bin/python3 -I -B tools/claims-v3/e199/forecast_e199.py           # from the top of the tree: writes forecast-e199.json, .txt
    /usr/bin/python3 -I -B tools/claims-v3/e199/forecast_e199.py --check   # FORECAST CHECK PASS: both files re-made byte for byte

Re-made before any datum, Mon 16 Nov 2026 (Q191, lane fix-e199; verify-e199 findings F1 and F3): RULES' T2_words give T2's final
form (s* the allowed scale under which the most decided prices hold, as E199.md 6.4 and score_e199.py score it; the first file gave
T2's first form, s* the clipped s_hat), and a price is decided at n >= 4 measured passes (RULES n_min, which score_e199.py reads; 2 in
the first form). No price, source, pin or allowance changed; the file's sha256, freeze line 1 of E199.md, is new.

Standard library only. SPDX-License-Identifier: Apache-2.0
"""
import hashlib
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
TOP = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
E192D = "docs/reports/data/2026-11-14-e192-intbits-aifoundry3"
E189D = "docs/reports/data/2026-11-14-e189-blind-day-aifoundry3"
E191D = "docs/reports/data/2026-11-15-e191-blind-day-aifoundry1-c1-s2"
CAT = "docs/reports/data/2026-09-23-energy-manual/catalogue.json"
PROGS = ("sha256", "sort-sorted", "sort-shuffled")
CAT_ROWS = ("add/random/h2", "add/zeros/h2", "xor/random/h2", "xor/zeros/h2", "and/random/h2", "and/zeros/h2",
            "nop/random/h2", "nop/zeros/h2", "add/random/h1")

PINS = {
    E192D + "/intbits-e192.json": "0a675627f60ebad0002052c7f70c5042744a415a423a889b90c3b71f80a386c5",
    E192D + "/checks-e192.json": "bfe123cf5044c927e42e8674233d7b4683baf25e20702cb668c19f642ace1dfe",
    E192D + "/SHA256SUMS-note2": "27d627e0f7f435babcbf23209311554d59126bddb9bece7daac9303ea97b8814",
    E189D + "/scores-e189.json": "ac8770ba7a1cdf995370c94c5736fda25156e833f9da3b93381f393ee624363c",
    CAT: "1186a9764838330369bc87f90f9ed4aed03d9d1373fd3185a8f107cf2eb1a7ae",
}
# the twelve per-pass energy.json files of source (1), each at its sha256 in its data directory's SHA256SUMS (checked below)
ENERGY_SUMS = {E189D: E189D + "/SHA256SUMS", E191D: E191D + "/SHA256SUMS"}

RULES = {
    "z": 2.0,
    "z_words": "the lab's 95% interval, mean +- 2 SE (E192.md section 6: 'a contrast whose 95% interval (mean +- 2 SE) contains zero')",
    "share_pct": 85,
    "share_words": "a family PASSES when at least K = ceil(0.85 N) of its N registered prices hold; it FAILS when at least F = N - K + 1 "
                   "miss; NO DATA when none is decided; otherwise NOT DECIDED",
    "se_ratio_max": 3.0,
    "n_min": 4,
    "decided_words": "a price is decided when card 1 has a value with n >= 4 measured passes and an SE no larger than 3 x aifoundry3's "
                     "SE for the same price; otherwise NOT DECIDED (its reason recorded); a session cut short before its fourth "
                     "measured pass decides no price (NO DATA)",
    "T1_words": "|m1 - m3| <= 2 sqrt(se1^2 + se3^2): card 1's value within the two values' combined 95% interval",
    "T2_words": "|m1 - s* m3| <= 2 sqrt(se1^2 + (s* se3)^2), s* = the family's one card-to-card scale: the scale in the allowance "
                "[s_lo, s_hi] (which holds 1) under which the most of the family's decided prices hold, found exactly (ties go to the "
                "value nearest the clipped s_hat, then nearest 1), so T2 never holds fewer prices than T1. THE SCALE: the weighted "
                "least-squares s_hat = sum(w m1 m3) / sum(w m3^2), w = 1 / (se1^2 + se3^2), over the family's decided prices, its SE "
                "1 / sqrt(sum(w m3^2)), times sqrt(chi2 / (D - 1)) when that is above 1; the scale holds when s_hat +- 2 SE meets the "
                "allowance (E199.md section 6.4)",
}
FAMILIES = (
    ("A", "board", "arms", "contrast_pJ_board", ["E199-T1", "E199-T2"],
     "per-arm contrast against its control in the same pass, pJ per instruction, board (the 12 V input), temperature-corrected "
     "(E192.md section 6's primary): THE HEADLINE FAMILY"),
    ("B", "board", "ladders", "board", ["E199-T1L", "E199-T2L"],
     "the 24 ladder quantities, fJ per bit or per position (pJ where named), board, temperature-corrected"),
    ("C", "rail", "arms", "contrast_pJ_rail", ["E199-T1R", "E199-T2R"],
     "per-arm contrast, pJ per instruction, the core (minion) rail, temperature-corrected, after E151's rail filter (section 6.5)"),
    ("D", "rail", "ladders", "rail", ["E199-T1RL", "E199-T2RL"],
     "the 24 ladder quantities, the core rail, temperature-corrected, after E151's rail filter (section 6.5)"),
)
REPORTED = (
    ("R1", "board", "pJ_board_over_idle", "per-arm energy over idle, pJ per instruction, board (E192.md 14: one shared bias; the idle "
                                          "footing is each card's own): REPORTED, scored by both rules, no verdict"),
    ("R2", "rail", "pJ_rail_over_idle", "per-arm energy over idle, pJ per instruction, core rail: REPORTED, scored by both rules, no "
                                        "verdict"),
)


def sha(path):
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def sig6(x):
    return float("%.6g" % x)


def check_pins():
    bad = []
    for rel, want in sorted(PINS.items()):
        p = os.path.join(TOP, rel)
        got = sha(p) if os.path.exists(p) else "missing"
        if got != want:
            bad.append("%s: %s, not %s" % (rel, got, want))
    note2 = open(os.path.join(TOP, E192D, "SHA256SUMS-note2")).read().split("\n")
    for name in ("intbits-e192.json", "checks-e192.json"):
        if not any(l.split() == [PINS[E192D + "/" + name], name] for l in note2 if l.strip()):
            bad.append("%s is not pinned by E192's SHA256SUMS-note2 at %s" % (name, PINS[E192D + "/" + name]))
    return bad


def energy_files():
    """The twelve energy.json files of source (1), each checked against its data directory's own SHA256SUMS."""
    out, bad = {}, []
    for d, sums in ENERGY_SUMS.items():
        lines = {}
        for l in open(os.path.join(TOP, sums)):
            parts = l.split()
            if len(parts) == 2:
                lines[parts[1].lstrip("*")] = parts[0]
        for prog in PROGS:
            for k in (1, 2, 3, 4):
                rel = "passes/%s/p%d/energy.json" % (prog, k)
                want = lines.get(rel) or lines.get("./" + rel)
                p = os.path.join(TOP, d, rel)
                got = sha(p) if os.path.exists(p) else "missing"
                if want is None or got != want:
                    bad.append("%s/%s: %s against its SHA256SUMS line %s" % (d, rel, got, want))
                out[(d, prog, k)] = (p, got)
    return out, bad


def families_from(ib):
    """The registered families and the reported sets, from any output of E192's reducer (E199.md section 6.1): each price's path into
    the file, and E192's mean, SE, n and reading copied as they are."""
    fams = {}
    for fid, meter, where, field, rules, words in FAMILIES:
        prices = []
        if where == "arms":
            for arm in sorted(ib["arms"]):
                rec = ib["arms"][arm]
                if "control" not in rec:
                    continue
                v = rec[field]
                prices.append({"key": arm, "path": ["arms", arm, field], "control": rec["control"],
                               "mean": v["mean"], "se": v["se"], "n": v["n"], "reading": v["reading"]})
        else:
            for k, v in ib["ladders"][field].items():
                prices.append({"key": k, "path": ["ladders", field, k], "mean": v["mean"], "se": v["se"], "n": v["n"],
                               "reading": v["reading"]})
        n = len(prices)
        kk = (RULES["share_pct"] * n + 99) // 100
        fams[fid] = {"meter": meter, "what": words, "rules": rules, "N": n, "K": kk, "F": n - kk + 1, "prices": prices}
    rep = {}
    for rid, meter, field, words in REPORTED:
        prices = []
        for arm in sorted(ib["arms"]):
            v = ib["arms"][arm][field]
            prices.append({"key": arm, "path": ["arms", arm, field], "mean": v["mean"], "se": v["se"], "n": v["n"],
                           "reading": v["reading"]})
        rep[rid] = {"meter": meter, "what": words, "N": len(prices), "prices": prices}
    return fams, rep


def build():
    bad = check_pins()
    efiles, b2 = energy_files()
    bad += b2
    if bad:
        raise SystemExit("REFUSED: " + "; ".join(bad))
    ib = json.load(open(os.path.join(TOP, E192D, "intbits-e192.json")))
    ck = json.load(open(os.path.join(TOP, E192D, "checks-e192.json")))
    fams, rep = families_from(ib)

    # the allowance, source (1)
    ratios = []
    sc = json.load(open(os.path.join(TOP, E189D, "scores-e189.json")))
    for prog in PROGS:
        m = {}
        for d in (E189D, E191D):
            vals = [json.load(open(efiles[(d, prog, k)][0]))["board"]["j_per_solve"] for k in (1, 2, 3, 4)]
            m[d] = sum(vals) / len(vals)
        e189_scorer = sc["configs"][prog]["measured_j_over_mean"]
        if abs(e189_scorer - m[E189D]) > 1e-9 * abs(m[E189D]):
            raise SystemExit("REFUSED: E189's %s mean %r differs from its scorer's %r" % (prog, m[E189D], e189_scorer))
        ratios.append({"source": "(1) the blind day: E191's second session (card 1) over E189 (aifoundry3), J over idle a launch, "
                                 "mean of 4 passes each",
                       "row": prog, "card1": sig6(m[E191D]), "aifoundry3": sig6(m[E189D]),
                       "ratio": sig6(m[E191D] / m[E189D])})
    cat = json.load(open(os.path.join(TOP, CAT)))
    for row in CAT_ROWS:
        pc = cat["combined"][row]["per_card"]
        c1, a3 = pc["aifoundry1-c1"]["mean"], pc["aifoundry3"]["mean"]
        ratios.append({"source": "(2) the energy catalogue's per-card means (the three-card check, 25-26 Sep 2026), pJ an op",
                       "row": row, "card1": sig6(c1), "aifoundry3": sig6(a3), "ratio": sig6(c1 / a3)})
    s_lo = min([1.0] + [r["ratio"] for r in ratios])
    s_hi = max([1.0] + [r["ratio"] for r in ratios])
    out = {
        "experiment": "E199",
        "what": "E199's forecast for aifoundry1 card 1 at 600 MHz as found, frozen before any card-1 X01 datum: E192's measured, "
                "reduced prices on aifoundry3 card 0, copied exactly from its committed outputs (no rounding, no arithmetic)",
        "label": "REGISTERED (the forecast is E192's MEASURED prices; E199 is NOT blind to E192's data: E192's data is the forecast)",
        "measured_on": "aifoundry3 card 0, E192, Sat 14 Nov 2026, session 21:07:37-22:07:08 PST (T0 1794719257), 9 passes, pass 0 the "
                       "warm-up, 8 measured passes (1-8), the registered reducer reduce_intbits.py at 715fddaa..., unchanged",
        "forecast_for": "aifoundry1 card 1, 600 MHz as found, ET_DEVICES=1, X01's 32 arms and anchor as E192 registered them",
        "sources": {rel: {"sha256": want} for rel, want in sorted(PINS.items())},
        "source_commits": {"E192 registration": "a282aad6", "E192 kit": "a6fe5c20", "E192 data": "a6e17e83",
                           "E192 data note 1": "4e964246", "E192 data note 2 (intbits-e192.json, checks-e192.json)": "117312b1",
                           "E189 data": "fa9098c4", "E191 second session's data": "7156ac15"},
        "energy_files": [{"path": os.path.relpath(p, TOP), "sha256": s} for (_, _, _), (p, s) in sorted(efiles.items())],
        "rules": RULES,
        "families": fams,
        "reported": rep,
        "allowance": {"s_lo": s_lo, "s_hi": s_hi, "ratios": ratios,
                      "how": "[min, max] of the twelve named ratios and 1; each ratio card 1 over aifoundry3, 6 significant digits"},
        "beta_W_per_C_e192": ib["beta_W_per_C"],
        "e192_used_passes": ck["used_passes"],
        "e192_checks": {k: v["verdict"] for k, v in ck["checks"].items()},
        "e192_runs": len(ib["runs"]),
        "interpreter": "/usr/bin/python3 3.12.3 on aifoundry2 wrote this file (standard library only)",
    }
    return out


def text(f):
    L = ["E199's forecast for aifoundry1 card 1 (REGISTERED; NOT blind to E192: it IS E192's measured prices on aifoundry3 card 0,",
         "copied exactly from intbits-e192.json at 0a675627...). mean +- SE over E192's 8 measured passes; reading as E192's reducer",
         "wrote it.", ""]
    for fid in ("A", "B", "C", "D"):
        fam = f["families"][fid]
        L.append("family %s (%s; rules %s; N %d, PASS at K >= %d holding, FAIL at F >= %d missing): %s" % (
            fid, fam["meter"], ", ".join(fam["rules"]), fam["N"], fam["K"], fam["F"], fam["what"]))
        for p in fam["prices"]:
            L.append("  %-34s %12.6f +- %-10.6f n %d  %s%s" % (p["key"], p["mean"], p["se"], p["n"], p["reading"],
                                                               ("  (vs %s)" % p["control"]) if "control" in p else ""))
        L.append("")
    for rid in ("R1", "R2"):
        fam = f["reported"][rid]
        L.append("reported %s (%s; N %d): %s" % (rid, fam["meter"], fam["N"], fam["what"]))
        for p in fam["prices"]:
            L.append("  %-34s %12.6f +- %-10.6f n %d  %s" % (p["key"], p["mean"], p["se"], p["n"], p["reading"]))
        L.append("")
    a = f["allowance"]
    L.append("the scale allowance of rule T2: s in [%g, %g] (%s)" % (a["s_lo"], a["s_hi"], a["how"]))
    for r in a["ratios"]:
        L.append("  %-16s card 1 %-9g aifoundry3 %-9g ratio %-8g  %s" % (r["row"], r["card1"], r["aifoundry3"], r["ratio"], r["source"]))
    L.append("")
    L.append("rules: z %g (%s); share %d%%; SE ratio cap %g; decided at n >= %d measured passes" % (
        f["rules"]["z"], f["rules"]["z_words"], f["rules"]["share_pct"], f["rules"]["se_ratio_max"], f["rules"]["n_min"]))
    L.append("E192's section 7 checks on aifoundry3 (REPORTED beside card 1's, never a transport verdict): " +
             "; ".join("%s %s" % (k, v) for k, v in f["e192_checks"].items()))
    L.append("FORECAST-E199 MADE")
    return "\n".join(L) + "\n"


def dumps(f):
    return json.dumps(f, indent=1, sort_keys=False) + "\n"


def main():
    f = build()
    js, tx = dumps(f), text(f)
    pj, pt = os.path.join(HERE, "forecast-e199.json"), os.path.join(HERE, "forecast-e199.txt")
    if "--check" in sys.argv[1:]:
        ok = (os.path.exists(pj) and open(pj).read() == js) and (os.path.exists(pt) and open(pt).read() == tx)
        # every forecast price equals E192's committed value, field for field
        ib = json.load(open(os.path.join(TOP, E192D, "intbits-e192.json")))
        n = same = 0
        for grp in (f["families"], f["reported"]):
            for fam in grp.values():
                for p in fam["prices"]:
                    src = ib
                    for k in p["path"]:
                        src = src[k]
                    for fld in ("mean", "se", "n", "reading"):
                        n += 1
                        same += int(src[fld] == p[fld] and type(src[fld]) is type(p[fld]))
        print("forecast-e199.json and .txt re-made byte for byte: %s; fields equal to intbits-e192.json: %d of %d; interpreter %s" % (
            ok, same, n, sys.version.split()[0]))
        print("FORECAST CHECK " + ("PASS" if ok and same == n else "FAIL"))
        sys.exit(0 if ok and same == n else 1)
    with open(pj, "w") as fh:
        fh.write(js)
    with open(pt, "w") as fh:
        fh.write(tx)
    print("wrote %s and %s; allowance [%g, %g]" % (os.path.relpath(pj, TOP), os.path.relpath(pt, TOP), f["allowance"]["s_lo"],
                                                    f["allowance"]["s_hi"]))


if __name__ == "__main__":
    main()
