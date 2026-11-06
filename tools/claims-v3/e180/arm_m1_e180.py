#!/usr/bin/env python3
"""E180 (Q149; dated note M2, E180.md.dated-note-M2.md section 1): the reader of dated note M1's REPORTED arm, october-forecast-model's
fadd.ps one-number readings on aifoundry3, read after E180's data the way M1 sections 5 and 6 and M2 section 1 state it. Never a verdict:
it changes no rule, statistic, threshold or verdict of E180.

It reads one session's two desk files, as collect_e180_v3.sh writes them and E180's data commit keeps them:
  reduced-e180-v3.json   reduce_e180_v3.py's reduction: each kept pass's D(kind) (the kept bursts' over-idle power) and, where the
                         reducer kept it, R(kind), the net minion rail on footing A (A1 section 4.1)
  scored-e180.json       score_e180_v3.py's record: E180-H, the reported kinds and A1's RA2 on R
and M1's frozen values from m1-october-forecast-model-e180.json, pinned below at its sha256 (SHA256SUMS-e180-m1's entry). Four readings,
each a mean over the kept passes with power_e180.py's 95% interval (E180.md section 5's form; its functions imported unchanged, pinned
below), the arm's value placed in E180.md section 5's SIZE words: PASS inside; FAIL HIGH if the value is above the interval (the model
prices more than the card reads); FAIL LOW if below.
  H      the board, E180-H's statistic: D(5s) - D(4s) in each kept pass, against M1's 5s - 4s, +0.0041665 W. Recomputed from the
         reduction and refused unless it equals the scorer's E180-H record.
  RA2    the net minion rail, the same statistic on R (A1's RA2), against the same +0.0041665 W: M1 section 5 reads the arm against the
         board and the rail "as it stands", with no board or rail factor. Recomputed and checked against the scorer's record the same way.
  4s     D(fadd.ps/f_4) - D(fadd.ps/zeros) in each kept pass, the scorer's footing for every kind (reported.kinds, D_above_zeros_mean),
         against M1's 4s, +0.0298070 W. Never D(4s) alone: a kind's D is its whole over-idle power.
  5s     D(fadd.ps/f_5) - D(fadd.ps/zeros), against M1's 5s, +0.0339735 W.
Beside H: E180-H's SIGN against 0; 0 W placed in the same SIZE words as the arm (the arm and no difference read differently only when an
end of the interval falls between them, M1 section 6); the session's half-width as a multiple of the arm; and the 00:00:55 frozen
sentence's bracket (M2 section 2): its per-lane-op 4s 8.1 and 5s 9.3 fJ at their rounding give 5s - 4s 8.8 to 10.4 fJ per instruction,
+0.0040 to +0.0048 W at M1's rate; the words at its two ends are printed, and a difference between them is named.
Fewer than 2 kept passes: NOT READ (exit 0).

  check   python3 -B tools/claims-v3/e180/arm_m1_e180.py check
          the pinned inputs at their sha256 and M1's values as M2 states them: CHECK PASS, or exit 9
  read    python3 -B tools/claims-v3/e180/arm_m1_e180.py read --session <dir> [--reduced <file>] [--scored <file>] [--write <dir>]
          <dir> holds reduced-e180-v3.json and scored-e180.json (either can be named on its own); prints the readings; with --write,
          writes arm-m1-e180.json and arm-m1-e180.md into that directory, never over an existing file

EXIT (read): 0 read, or NOT READ; 2 usage (a file missing or unreadable, a card other than aifoundry3); 3 the two files are not one
session's (the kept passes differ, a kept pass lacks a kind, or a recomputed statistic differs from the scorer's record); 4 an output file
already exists (nothing written); 9 a pinned input differs. It needs no module outside Python itself, opens no device and reaches no box.
SPDX-License-Identifier: Apache-2.0
"""
import argparse
import hashlib
import json
import math
import os
import sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)

# the inputs, each committed and in a committed hash list (file in this directory -> sha256)
PINNED = {
    "m1-october-forecast-model-e180.json": "83745199c43b2270536bdb1d2d795d8257fe868faa3cb8e649ccc91f6e766d59",  # SHA256SUMS-e180-m1
    "power_e180.py": "7db37ef73167bcb5a9496fd2b675d570595bba46c62df0ec36cef5603953c4e1",  # SHA256SUMS-e180-registration
}
# M1's values as M2 states them (sections 1-4), checked against M1's JSON by `check` and before every read
M1_EXPECT_W = {"4s": 0.02980698673, "5s": 0.0339734562, "5s_minus_4s": 0.004166469466}
M1_EXPECT_RATE = 458357477000.0
CARD = "aifoundry3"
K4, K5, KZ = "fadd.ps/f_4", "fadd.ps/f_5", "fadd.ps/zeros"
REDUCED, SCORED = "reduced-e180-v3.json", "scored-e180.json"
OUT_JSON, OUT_MD = "arm-m1-e180.json", "arm-m1-e180.md"
TOL_W = 1e-9
NEVER = ("REPORTED (october-forecast-model, E180's dated notes M1 and M2): read beside E180's verdicts, never one of them; it changes no "
         "rule, statistic, threshold or verdict")
A1_POWER = ("A1 section 2: with no difference E180-H reads POSITIVE 0.02 at 6 passes at every noise level; its half-width is 0.103-0.198 W "
            "at 6 passes (0.121-0.232 W at 5), 25-48x the arm (29-56x at 5)")


class Refuse(Exception):
    def __init__(self, code, why):
        Exception.__init__(self, why)
        self.code, self.why = code, why


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(1 << 16), b""):
            h.update(b)
    return h.hexdigest()


def check_pinned():
    """the pinned inputs at their sha256, and M1's values as M2 states them; returns M1's JSON"""
    for name, want in PINNED.items():
        p = os.path.join(HERE, name)
        if not os.path.exists(p):
            raise Refuse(9, f"pinned input missing: {name}")
        got = sha256(p)
        if got != want:
            raise Refuse(9, f"pinned input differs: {name} sha256 {got[:16]}... (pinned {want[:16]}...)")
    m1 = json.load(open(os.path.join(HERE, "m1-october-forecast-model-e180.json")))
    arm = m1["arm"]
    for k, v in M1_EXPECT_W.items():
        if abs(arm["model_W_above_zeros"][k] - v) > 1e-15:
            raise Refuse(9, f"M1's {k} reads {arm['model_W_above_zeros'][k]!r}, not M2's {v!r}")
    if arm["rate_instructions_per_s"] != M1_EXPECT_RATE:
        raise Refuse(9, f"M1's rate reads {arm['rate_instructions_per_s']!r}, not {M1_EXPECT_RATE!r}")
    return m1


def bracket(m1):
    """the 00:00:55 frozen sentence's 5s - 4s per instruction (8 lanes), from its per-lane-op figures at their rounding (0.1 fJ)"""
    f = m1["frozen_forecast_fadd"]["per_lane_op_fJ"]
    half = 0.05
    lo = round(8 * ((f["5s"] - half) - (f["4s"] + half)), 10)
    mid = round(8 * (f["5s"] - f["4s"]), 10)
    hi = round(8 * ((f["5s"] + half) - (f["4s"] - half)), 10)
    rate = m1["arm"]["rate_instructions_per_s"]
    return {"fJ": [lo, hi], "point_fJ": mid, "W": [lo * 1e-15 * rate, hi * 1e-15 * rate], "point_W": mid * 1e-15 * rate}


def fragility(m1):
    a = m1["arm"]
    b = a["lines_that_differ_fJ"]["bubble transitions between operations"]["5s_minus_4s"]
    l = a["lines_that_differ_fJ"]["leakage within the logic"]["5s_minus_4s"]
    net = a["model_above_zeros_fJ"]["5s_minus_4s"]
    rate = a["rate_instructions_per_s"]
    return {"bubble_fJ": b, "leakage_fJ": l, "net_fJ": net, "bubble_over_net": b / net,
            "bubble_W": b * 1e-15 * rate, "leakage_W": l * 1e-15 * rate,
            "ten_pct_bubble_moves_net": 0.1 * b / net, "ten_pct_leakage_moves_net": 0.1 * abs(l) / net,
            "line": ("the arm is a near-cancellation: the bubble term, %.0fx the net (%+.2f fJ against %+.2f fJ), is labelled 'assumed' in "
                     "the model's ledger ('modelled' in its per-instruction table), and the model gives no band; 10%% on the bubble term "
                     "moves the arm by %.0f%%, 10%% on the leakage term by %.0f%%" % (b / net, b, net, 100 * 0.1 * b / net,
                                                                                    100 * 0.1 * abs(l) / net))}


def load(path, what):
    if not path or not os.path.exists(path):
        raise Refuse(2, f"{what} not found ({os.path.basename(path) if path else 'not given'})")
    try:
        return json.load(open(path))
    except (OSError, ValueError) as e:
        raise Refuse(2, f"{what} unreadable ({os.path.basename(path)}: {type(e).__name__})")


def place(pw, lo, hi, f):
    return pw.size(lo, hi, f)


def read(red, sc, m1, pw):
    """the four readings; raises Refuse(3) when the two files are not one session's"""
    if sc.get("card") != CARD:
        raise Refuse(2, f"the scored session's card is {sc.get('card')!r}: M1's arm is aifoundry3's (card 1's table is not converted)")
    passes = sorted(red.get("passes", {}))
    kept = sc.get("kept_passes")
    if kept != passes:
        raise Refuse(3, f"the scorer's kept passes {kept} are not the reduction's {passes}")
    n = len(passes)
    arm = m1["arm"]["model_W_above_zeros"]
    out = {"what": "E180's dated note M1's arm, read by arm_m1_e180.py (E180.md.dated-note-M2.md section 1)", "never": NEVER,
           "card": CARD, "kept_passes": passes, "n": n,
           "arm_W": {"5s_minus_4s": arm["5s_minus_4s"], "4s_above_zeros": arm["4s"], "5s_above_zeros": arm["5s"]},
           "fragility": fragility(m1)["line"], "a1_power": A1_POWER}
    H = sc.get("rules", {}).get("E180-H", {})
    if n < 2:
        if H.get("verdict") != "NOT SCORED":
            raise Refuse(3, f"{n} kept pass(es) but the scorer's E180-H reads {H.get('verdict')!r}")
        out["status"] = "NOT READ"
        out["why"] = f"{n} kept pass(es); 2 needed (E180.md section 5: every rule NOT SCORED)"
        return out
    for p in passes:
        D = red["passes"][p].get("D", {})
        miss = [k for k in (K4, K5, KZ) if not isinstance(D.get(k), (int, float))]
        if miss:
            raise Refuse(3, f"kept pass {p} has no D for {', '.join(miss)}")
    if "lo" not in H:
        raise Refuse(3, f"{n} kept passes but the scorer's E180-H holds no interval ({H.get('verdict')!r})")

    def series(key, a, b):
        xs = []
        for p in passes:
            rec = red["passes"][p].get(key) or {}
            x, y = rec.get(a), rec.get(b)
            if isinstance(x, (int, float)) and isinstance(y, (int, float)):
                xs.append(x - y)
        return xs

    def reading(xs, f):
        m, lo, hi = pw.interval(xs)
        return {"n": len(xs), "x": xs, "mean": m, "lo": lo, "hi": hi, "half_width": (hi - lo) / 2, "arm_W": f,
                "words": place(pw, lo, hi, f)}

    def same(a, b):
        return abs(a - b) <= TOL_W

    r = {}
    xs = series("D", K5, K4)
    h = reading(xs, arm["5s_minus_4s"])
    if not (same(h["mean"], H["mean"]) and same(h["lo"], H["lo"]) and same(h["hi"], H["hi"])):
        raise Refuse(3, "E180-H recomputed from the reduction (mean %+.6f, %+.6f to %+.6f) differs from the scorer's record (mean %+.6f, "
                        "%+.6f to %+.6f)" % (h["mean"], h["lo"], h["hi"], H["mean"], H["lo"], H["hi"]))
    h["statistic"] = "D(fadd.ps/f_5) - D(fadd.ps/f_4) in each kept pass (E180-H's, on the board)"
    h["zero"] = pw.sign(h["lo"], h["hi"])
    h["zero_words"] = place(pw, h["lo"], h["hi"], 0.0)
    h["scorer_verdict"] = H.get("verdict")
    h["half_width_over_arm"] = h["half_width"] / arm["5s_minus_4s"]
    br = bracket(m1)
    ends = [place(pw, h["lo"], h["hi"], w) for w in br["W"]]
    br["words_at_ends"] = ends
    br["same_words_across"] = ends[0] == ends[1] == h["words"]
    h["bracket_00_00_55"] = br
    h["arm_and_no_difference"] = "read alike" if h["zero_words"] == h["words"] else "read differently"
    r["H_board"] = h
    rep = sc.get("reported", {}).get("kinds", {})
    for tag, k, f in (("4s_above_zeros", K4, arm["4s"]), ("5s_above_zeros", K5, arm["5s"])):
        x = reading(series("D", k, KZ), f)
        want = rep.get(k, {}).get("D_above_zeros_mean")
        if not isinstance(want, (int, float)) or not same(x["mean"], want):
            raise Refuse(3, f"D({k}) - D(fadd.ps/zeros) recomputed ({x['mean']:+.6f}) differs from the scorer's D_above_zeros_mean ({want!r})")
        x["statistic"] = f"D({k}) - D(fadd.ps/zeros) in each kept pass (the scorer's footing for every kind)"
        x["d_kind_alone_mean"] = sum(red["passes"][p]["D"][k] for p in passes) / n
        r[tag] = x
    ra2 = sc.get("reported_v2", {}).get("RA2_his_pair", {}).get("R")
    xr = series("R", K5, K4)
    if ra2 is None:
        r["RA2_rail"] = {"status": "not read", "why": "the scorer's record holds no RA2 on R"}
    elif "mean" not in ra2:
        if len(xr) >= 2:
            raise Refuse(3, f"the reduction holds R in {len(xr)} kept passes but the scorer's RA2 on R reads {ra2.get('verdict_free')!r}")
        r["RA2_rail"] = {"status": "not read", "why": f"{len(xr)} kept pass(es) with a rail reading; 2 needed"}
    else:
        x = reading(xr, arm["5s_minus_4s"])
        if not (same(x["mean"], ra2["mean"]) and same(x["lo"], ra2["lo"]) and same(x["hi"], ra2["hi"])):
            raise Refuse(3, "RA2 on R recomputed from the reduction differs from the scorer's record")
        x["statistic"] = "R(fadd.ps/f_5) - R(fadd.ps/f_4) in each kept pass with a rail reading (A1's RA2, the net minion rail)"
        x["zero"] = pw.sign(x["lo"], x["hi"])
        r["RA2_rail"] = x
    out["status"] = "READ"
    out["readings"] = r
    return out


def md(rec, names):
    L = ["# E180: dated note M1's arm, read (october-forecast-model; REPORTED, never a verdict)", "",
         f"*{rec['never']}. Read by `arm_m1_e180.py` (E180.md.dated-note-M2.md section 1) from {names}; aifoundry3, "
         f"{rec['n']} kept pass(es) ({', '.join(rec['kept_passes']) or 'none'}).*", ""]
    if rec["status"] != "READ":
        L += [f"**NOT READ:** {rec['why']}.", ""]
        return "\n".join(L) + "\n"
    r = rec["readings"]
    L += ["| reading | statistic per kept pass | mean (W) | 95% interval (W) | the arm (W) | words |", "|---|---|---:|---|---:|---|"]
    rows = (("E180-H, the board", "H_board"), ("RA2, the net minion rail", "RA2_rail"), ("4s above zeros, the board", "4s_above_zeros"),
            ("5s above zeros, the board", "5s_above_zeros"))
    for label, key in rows:
        x = r[key]
        if "mean" not in x:
            L.append(f"| {label} | - | - | - | - | {x['status']}: {x['why']} |")
            continue
        L.append(f"| {label} | {x['statistic']} | {x['mean']:+.4f} | {x['lo']:+.4f} to {x['hi']:+.4f} | {x['arm_W']:+.4f} | "
                 f"**{x['words']}** |")
    h = r["H_board"]
    br = h["bracket_00_00_55"]
    L += ["",
          f"- **Beside E180-H:** against 0 it reads {h['zero']} (E180-H's SIGN; the scorer's E180-H: {h['scorer_verdict']}). Placed "
          f"as the arm is, no difference (0 W) reads {h['zero_words']} and the arm {h['words']}: they {h['arm_and_no_difference']} "
          f"(they read differently only when an end of the interval falls between 0 and the arm). The half-width, "
          f"{h['half_width']:.4f} W, is {h['half_width_over_arm']:.0f}x the arm.",
          f"- **The 00:00:55 frozen sentence's bracket** (5s - 4s {br['fJ'][0]:.1f} to {br['fJ'][1]:.1f} fJ, {br['W'][0]:+.4f} to "
          f"{br['W'][1]:+.4f} W): {br['words_at_ends'][0]} at its low end, {br['words_at_ends'][1]} at its high end; "
          + ("the same words across it as at M1's value." if br["same_words_across"] else
             "**the words differ across it**: an end of E180-H's interval lies inside the bracket, so the reading at M1's frozen value "
             "is not the reading at every point the 00:00:55 sentence allows."),
          f"- **The footing:** each kind is read as D(kind) - D(fadd.ps/zeros). D(4s) alone averages {r['4s_above_zeros']['d_kind_alone_mean']:.4f} W "
          f"over idle and is never compared with the arm.",
          f"- **Beside the arm:** {rec['fragility']}.",
          f"- **The power, as the records quote it:** {rec['a1_power']}.", ""]
    return "\n".join(L) + "\n"


def lines(rec):
    if rec["status"] != "READ":
        return [f"M1 ARM: NOT READ ({rec['why']})"]
    out = []
    for key in ("H_board", "RA2_rail", "4s_above_zeros", "5s_above_zeros"):
        x = rec["readings"][key]
        if "mean" not in x:
            out.append(f"M1 ARM {key}: {x['status']} ({x['why']})")
        else:
            out.append(f"M1 ARM {key}: mean {x['mean']:+.4f} W (95% {x['lo']:+.4f} to {x['hi']:+.4f}) against {x['arm_W']:+.4f} W: {x['words']}")
    h = rec["readings"]["H_board"]
    out.append(f"M1 ARM H_board beside: against 0 {h['zero']}; no difference (0 W) {h['zero_words']}, the arm {h['words']}: "
               f"{h['arm_and_no_difference']}; bracket ends "
               f"{h['bracket_00_00_55']['words_at_ends'][0]} / {h['bracket_00_00_55']['words_at_ends'][1]}"
               f"{'' if h['bracket_00_00_55']['same_words_across'] else ' (the words differ across the bracket)'}")
    out.append("M1 ARM: " + NEVER)
    return out


def main():
    ap = argparse.ArgumentParser(description="E180's dated note M1's REPORTED arm, read (dated note M2)")
    sub = ap.add_subparsers(dest="cmd")
    sub.add_parser("check")
    rp = sub.add_parser("read")
    rp.add_argument("--session", default=None, help="a directory holding reduced-e180-v3.json and scored-e180.json")
    rp.add_argument("--reduced", default=None)
    rp.add_argument("--scored", default=None)
    rp.add_argument("--write", default=None, help="a directory to write arm-m1-e180.json and arm-m1-e180.md into")
    a = ap.parse_args()
    try:
        m1 = check_pinned()
        if a.cmd == "check":
            br = bracket(m1)
            print("CHECK PASS: %s; M1's arm %+.7f / %+.7f / %+.7f W (5s - 4s / 4s / 5s above zeros); the 00:00:55 bracket %.1f to %.1f fJ, "
                  "%+.7f to %+.7f W" % (", ".join(f"{k} {v[:12]}..." for k, v in PINNED.items()), M1_EXPECT_W["5s_minus_4s"],
                                        M1_EXPECT_W["4s"], M1_EXPECT_W["5s"], br["fJ"][0], br["fJ"][1], br["W"][0], br["W"][1]))
            return 0
        if a.cmd != "read":
            ap.print_usage()
            return 2
        red_p = a.reduced or (os.path.join(a.session, REDUCED) if a.session else None)
        sc_p = a.scored or (os.path.join(a.session, SCORED) if a.session else None)
        red, sc = load(red_p, "the reduction"), load(sc_p, "the scorer's record")
        if a.write:
            targets = [os.path.join(a.write, n) for n in (OUT_JSON, OUT_MD)]
            have = [os.path.basename(t) for t in targets if os.path.exists(t)]
            if have:
                raise Refuse(4, f"{', '.join(have)} already in the output directory: nothing written")
            if not os.path.isdir(a.write):
                raise Refuse(2, "the output directory does not exist")
        import power_e180 as pw  # noqa: E402  (pinned above; nothing runs at import)
        rec = read(red, sc, m1, pw)
        rec["inputs"] = {"reduced": {"name": os.path.basename(red_p), "sha256": sha256(red_p)},
                         "scored": {"name": os.path.basename(sc_p), "sha256": sha256(sc_p)},
                         "m1": {"name": "tools/claims-v3/e180/m1-october-forecast-model-e180.json",
                                "sha256": PINNED["m1-october-forecast-model-e180.json"]}}
        for ln in lines(rec):
            print(ln)
        if a.write:
            names = f"`{os.path.basename(red_p)}` and `{os.path.basename(sc_p)}`"
            with open(os.path.join(a.write, OUT_JSON), "x") as f:
                json.dump(rec, f, indent=1, sort_keys=True)
                f.write("\n")
            with open(os.path.join(a.write, OUT_MD), "x") as f:
                f.write(md(rec, names))
            print(f"M1 ARM: wrote {OUT_JSON} and {OUT_MD}")
        return 0
    except Refuse as e:
        print(f"M1 ARM REFUSED (exit {e.code}): {e.why}")
        return e.code


if __name__ == "__main__":
    sys.exit(main())
