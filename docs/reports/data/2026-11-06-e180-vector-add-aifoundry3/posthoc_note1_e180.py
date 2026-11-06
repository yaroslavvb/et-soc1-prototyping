#!/usr/bin/env python3
"""E180's data README, dated note 1 (Fri 6 Nov 2026, after the card day's data verifier): every figure the note cites, read from this
directory's committed files (the data commit's 91: the 89 that SHA256SUMS lists, README.md and SHA256SUMS) and, as text or data only,
from six committed files of the kit that the note quotes (tools/claims-v3/e180/E180.md, E180.md.dated-note-A1.md, power_e180.py,
score_e180.py, score_e180_v2.py and forecast-e180.json). Standard library only: it imports no lab module, changes no file it reads, and
writes two files beside itself (or into --out), byte for byte the same on every run with the same interpreter (the Intel's
/usr/bin/python3, 3.9):

    /usr/bin/python3 -B posthoc_note1_e180.py        # writes posthoc-note1-e180.txt and posthoc-note1-e180.json

  section 1  E180-I re-made from the committed reduction by the registered statistic, the order in which the scorer reads its verdicts,
             and every arm's forecast against the interval (the verifier's fault 1);
  section 2  the die's rise over a burst: the scorer's median of the kinds' mean rises, the 282 bursts' own median and mean, and the
             live die reading's range over the session's samples (fault 2);
  section 3  every figure of the README's bullets after its reported table (lines 84-96), and its other figures printed to three
             decimals or fewer from a committed figure, each against that figure at the printed precision (fault 3).

Nothing here is a rule or a verdict: every figure re-reads a committed one.
SPDX-License-Identifier: Apache-2.0
"""
import argparse
import ast
import gzip
import hashlib
import json
import math
import os
import re
import statistics
import sys
from decimal import Decimal, ROUND_HALF_EVEN, ROUND_HALF_UP

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
ap = argparse.ArgumentParser()
ap.add_argument("--data", default=HERE, help="the data directory (default: this script's own)")
ap.add_argument("--out", default=None, help="where the two outputs go (default: the data directory)")
a = ap.parse_args()
DATA = os.path.abspath(a.data)
OUT = os.path.abspath(a.out) if a.out else DATA
KIT = os.path.normpath(os.path.join(DATA, "..", "..", "..", "..", "tools", "claims-v3", "e180"))
KIT_REL = "tools/claims-v3/e180"
OUT_TXT = os.path.join(OUT, "posthoc-note1-e180.txt")
OUT_JSON = os.path.join(OUT, "posthoc-note1-e180.json")
MINUS = "−"
lines = []
out = {"_note": "E180's data README, dated note 1: figures re-read from the committed data (posthoc_note1_e180.py); post hoc, no verdict"}


def say(s=""):
    lines.append(s)


def sha(path):
    return hashlib.sha256(open(path, "rb").read()).hexdigest()


def sg(x, d=4):
    """a signed figure with the README's minus sign (U+2212)"""
    return f"{x:+.{d}f}".replace("-", MINUS)


def kit_text(name):
    return open(os.path.join(KIT, name), encoding="utf-8").read()


def line_of(text, pattern, start=0):
    """1-based number of the first line at or after start (0-based) that matches the regular expression"""
    for i, ln in enumerate(text.split("\n")[start:], start + 1):
        if re.search(pattern, ln):
            return i
    return None


# ---- inputs ----
SUMS = os.path.join(DATA, "SHA256SUMS")
listed = {}
for ln in open(SUMS, encoding="utf-8"):
    if ln.strip():
        h, name = ln.rstrip("\n").split("  ", 1)
        listed[name] = h
bad_sums = sorted(n for n, h in listed.items() if sha(os.path.join(DATA, n)) != h)
readme = open(os.path.join(DATA, "README.md"), encoding="utf-8").read()
RL = readme.split("\n")
sc = json.load(open(os.path.join(DATA, "scored-e180.json"), encoding="utf-8"))
red = json.load(open(os.path.join(DATA, "reduced-e180-v3.json"), encoding="utf-8"))
fc = json.load(open(os.path.join(KIT, "forecast-e180.json"), encoding="utf-8"))
texts = {n: kit_text(n) for n in ("E180.md", "E180.md.dated-note-A1.md", "power_e180.py", "score_e180.py", "score_e180_v2.py")}
say("E180's data README, dated note 1: the figures it cites, re-read from the committed data (posthoc_note1_e180.py)")
say("")
say("== inputs")
say(f"the data commit's files: {len(listed) + 2} (SHA256SUMS lists {len(listed)}; README.md and SHA256SUMS beside); SHA256SUMS re-hashed "
    f"here: {len(listed) - len(bad_sums)} of {len(listed)} OK" + (f"; FAILED: {', '.join(bad_sums)}" if bad_sums else ""))
for n in ("scored-e180.json", "reduced-e180-v3.json"):
    say(f"{n} sha256 {listed.get(n, '(not listed)')} (its SHA256SUMS line)")
for n in sorted(texts) + ["forecast-e180.json"]:
    say(f"read as {'data' if n.endswith('.json') else 'text'}: {KIT_REL}/{n} sha256 {sha(os.path.join(KIT, n))}")
out["inputs"] = {"listed": len(listed), "listed_ok": len(listed) - len(bad_sums), "failed": bad_sums,
                 "kit_sha256": {n: sha(os.path.join(KIT, n)) for n in sorted(texts) + ["forecast-e180.json"]}}

passes = list(sc["kept_passes"])
P = red["passes"]

# ---- section 1: E180-I ----
say("")
say("== section 1: E180-I, the integer path, re-made by the registered statistic (fault 1)")
pw = texts["power_e180.py"]
T975 = ast.literal_eval(re.search(r"^T975 = (\{.*\})$", pw, re.M).group(1))
I_MARGIN = float(re.search(r"^I_MARGIN = ([0-9.]+)$", pw, re.M).group(1))
row = line_of(texts["E180.md"], r"^\| \*\*E180-I\*\* \(the integer path\)")
row_text = texts["E180.md"].split("\n")[row - 1]
thr = re.search(r"NULL if the interval lies inside \+-0\.30 W", row_text) is not None
s1 = texts["score_e180.py"]
blk = line_of(s1, r"# E180-I: the integer path")
l_null_test = line_of(s1, r"if -pw\.I_MARGIN <= lo and hi <= pw\.I_MARGIN:", blk)
l_pos = line_of(s1, r"elif lo > 0:", blk)
l_neg = line_of(s1, r"elif hi < 0:", blk)
I = sc["rules"]["E180-I"]
pi8 = list(I["kinds"])
xs = [statistics.mean(P[p]["D"][k] for k in pi8) - P[p]["D"]["fadd.pi/zeros"] for p in passes]
n = len(xs)
m = sum(xs) / n
sd = statistics.stdev(xs)
h = T975[n - 1] * sd / math.sqrt(n)
lo, hi = m - h, m + h
dx = max(abs(u - v) for u, v in zip(xs, I["x"]))
same = abs(m - I["mean"]) < 1e-12 and abs(lo - I["lo"]) < 1e-12 and abs(hi - I["hi"]) < 1e-12 and dx < 1e-12
inside_margin = -I_MARGIN <= lo and hi <= I_MARGIN
if inside_margin:
    v_reg = "NULL"
elif lo > 0:
    v_reg = "POSITIVE"
elif hi < 0:
    v_reg = "NEGATIVE"
else:
    v_reg = "NOT RESOLVED"
sign_alone = "above 0" if lo > 0 else "below 0" if hi < 0 else "spans 0"
where = {}
for arm in ("P", "C", "E", "F", "A"):
    f = I["forecast"][arm]
    where[arm] = {"forecast": f, "where": "below" if f < lo else "above" if f > hi else "inside"}
say(f"E180.md section 5, the E180-I row (line {row}): threshold 'NULL if the interval lies inside +-0.30 W' {'found' if thr else 'NOT FOUND'}; "
    f"power_e180.I_MARGIN {I_MARGIN}; t(0.975, {n - 1}) = power_e180.T975[{n - 1}] = {T975[n - 1]}")
say(f"score_e180.py's E180-I block (line {blk}): the margin test at line {l_null_test} comes first, then 'lo > 0' (POSITIVE) at line {l_pos} "
    f"and 'hi < 0' (NEGATIVE) at line {l_neg}: an interval inside the margin reads NULL whatever its sign")
say(f"the 8 kinds: {', '.join(pi8)}; less fadd.pi/zeros; kept passes {', '.join(passes)}")
say("per pass, mean D(8 kinds) - D(fadd.pi zeros), W: " + ", ".join(f"{p} {sg(x)}" for p, x in zip(passes, xs)) +
    f"; above 0 in {sum(1 for x in xs if x > 0)} of {n}")
say(f"re-made: {sg(m)} [{sg(lo)}, {sg(hi)}] W (sd {sd:.4f}, half-width {h:.4f}); equals scored-e180.json rules.E180-I to 1e-12: {same}")
say(f"inside the +-{I_MARGIN:.2f} W margin: {inside_margin}, so the registered verdict is {v_reg} (scored: {I['verdict']}); by the sign test "
    f"alone the interval lies {sign_alone}")
say("the arms' forecasts (scored-e180.json, the mean of the 8 kinds' frozen W) against the interval: " +
    "; ".join(f"{arm} {sg(v['forecast'])} {v['where']}" for arm, v in where.items()))
flat = [i + 1 for i, ln in enumerate(RL) if re.search(r"\bflat\b", ln)]
cites = {}
for phr in ("the integer add is flat (E180-I NULL)", "the integer add reads flat inside its", "the integer add's held write-back is flat",
            "within ±0.30 W (E180-I NULL)", "+0.1022 W [+0.0385, +0.1659]"):
    cites[phr] = [i + 1 for i, ln in enumerate(RL) if phr in ln]
say(f"README lines holding the word 'flat': {flat}; " + "; ".join(f"{k!r} at {v}" for k, v in cites.items()))
out["section_1"] = {"rule_row_line": row, "threshold_found": thr, "I_MARGIN": I_MARGIN, "t": T975[n - 1], "n": n,
                    "score_lines": {"block": blk, "margin_test": l_null_test, "positive": l_pos, "negative": l_neg},
                    "kinds": pi8, "x": dict(zip(passes, xs)), "above_zero_passes": sum(1 for x in xs if x > 0),
                    "mean": m, "sd": sd, "half_width": h, "lo": lo, "hi": hi, "equals_scored": same,
                    "inside_margin": inside_margin, "verdict": v_reg, "scored_verdict": I["verdict"], "sign_alone": sign_alone,
                    "arms": where, "readme_flat_lines": flat, "readme_cites": cites}

# ---- section 2: the die rise ----
say("")
say("== section 2: the die's rise over a burst (fault 2)")
a1 = texts["E180.md.dated-note-A1.md"]
l_a1 = line_of(a1, r"^- \*\*Reported per kind:\*\* the mean rise")
l_med = line_of(texts["score_e180_v2.py"], r"med = st\.median\(v\[\"mean\"\] for v in rise\.values\(\)\)")
kinds = sorted(P[passes[0]]["rise"])
per_kind = {k: statistics.mean(P[p]["rise"][k] for p in passes) for k in kinds}
med_kinds = statistics.median(per_kind.values())
off = sorted(k for k, v in per_kind.items() if abs(v - med_kinds) > 0.5)
bursts = [e["rise"] for p in passes for k in kinds for e in P[p]["runs_v2"][k]]
kp = [P[p]["rise"][k] for p in passes for k in kinds]
q = statistics.quantiles(bursts, n=4)
rise_sc = sc["reported_v2"]["rise"]
same_med = abs(med_kinds - rise_sc["median_c"]) < 1e-12 and off == sorted(rise_sc["off_median"])
say(f"A1 section 4.3 (E180.md.dated-note-A1.md line {l_a1}): reported per kind, the mean rise (Tb - Ti) over passes, and a kind more than "
    f"0.5 C from the median named; score_e180_v2.py line {l_med} takes the median over the kinds' means")
say(f"the kinds' mean rises ({len(per_kind)} kinds, each the mean over {len(passes)} passes): median {med_kinds:.4f} C, mean "
    f"{statistics.mean(per_kind.values()):.4f} C; more than 0.5 C off the median: {', '.join(off) or 'none'} "
    f"({', '.join(f'{per_kind[k]:.3f} C' for k in off)}); equals scored-e180.json reported_v2.rise: {same_med}")
say(f"the bursts ({len(bursts)}: every kept burst of the {len(passes)} passes, reduced-e180-v3.json passes.*.runs_v2): median "
    f"{statistics.median(bursts):.4f} C, mean {statistics.mean(bursts):.4f} C, quartiles {q[0]:.4f} / {q[2]:.4f} C, least {min(bursts):.4f}, "
    f"most {max(bursts):.4f} C; bursts at exactly 0: {sum(1 for b in bursts if b == 0)}")
say(f"the (kind, pass) means ({len(kp)}): median {statistics.median(kp):.4f} C, mean {statistics.mean(kp):.4f} C")
say(f"README lines: 'median 0.870' at {[i + 1 for i, ln in enumerate(RL) if 'median 0.870' in ln]}; "
    f"\"a burst's mean rise was 0.87\" at {[i + 1 for i, ln in enumerate(RL) if 'mean rise was 0.87' in ln]}")
# the live die reading: temp_c.minshire[0] over every sample of the session's telemetry
groups = {}
for sub in ("e180-stoptest", "e180-smoke", "e180"):
    base = os.path.join(DATA, "raw", sub)
    for pdir in sorted(os.listdir(base)):
        f = os.path.join(base, pdir, "telemetry.jsonl.gz")
        if not os.path.exists(f):
            continue
        vals, board, bad = [], [], 0
        with gzip.open(f, "rt", encoding="utf-8", errors="replace") as g:
            for ln in g:
                if not ln.startswith("{"):
                    continue
                try:
                    s = json.loads(ln)
                except ValueError:
                    bad += 1
                    continue
                ms = (s.get("temp_c") or {}).get("minshire")
                if ms:
                    vals.append(ms[0])
                if s.get("board_w") is not None:
                    board.append(s["board_w"])
        groups[f"{sub}/{pdir}"] = {"samples": len(vals), "min_c": min(vals), "max_c": max(vals), "board_max_w": max(board), "bad": bad}
allv = [g for g in groups.values()]
pas = [v for k, v in groups.items() if k.startswith("e180/")]
die = {"samples": sum(g["samples"] for g in allv), "min_c": min(g["min_c"] for g in allv), "max_c": max(g["max_c"] for g in allv),
       "passes_min_c": min(g["min_c"] for g in pas), "passes_max_c": max(g["max_c"] for g in pas),
       "board_max_w": max(g["board_max_w"] for g in allv), "bad_lines": sum(g["bad"] for g in allv)}
say(f"the live die reading, temp_c.minshire[0], over the session's {die['samples']} samples ({len(groups)} telemetry files): "
    f"{die['min_c']:g}-{die['max_c']:g} C (the six passes alone {die['passes_min_c']:g}-{die['passes_max_c']:g} C); board at most "
    f"{die['board_max_w']:.2f} W; unreadable lines {die['bad_lines']}")
say("  " + "; ".join(f"{k} {v['min_c']:g}-{v['max_c']:g} C" for k, v in groups.items()))
out["section_2"] = {"a1_line": l_a1, "score_v2_median_line": l_med, "kinds_mean_rise": per_kind, "kinds_median_c": med_kinds,
                    "kinds_mean_c": statistics.mean(per_kind.values()), "off_median": off, "equals_scored": same_med,
                    "bursts": {"n": len(bursts), "median_c": statistics.median(bursts), "mean_c": statistics.mean(bursts),
                               "q1_c": q[0], "q3_c": q[2], "min_c": min(bursts), "max_c": max(bursts),
                               "at_zero": sum(1 for b in bursts if b == 0)},
                    "kind_pass_means": {"n": len(kp), "median_c": statistics.median(kp), "mean_c": statistics.mean(kp)},
                    "live_die": die, "live_die_by_file": groups}

# ---- section 3: the README's rounded figures ----
say("")
say("== section 3: the README's rounded figures, each against its committed value at the printed precision (fault 3)")
K = sc["reported"]["kinds"]
R = sc["rules"]
L = R["E180-L"]
Dz = {k: v["D_above_zeros_mean"] for k, v in K.items()}
FP = {k: v["forecast"] for k, v in K.items()}
rate = fc["rates"]["aifoundry3"]["fadd.ps"]
dN = fc["pairs"]["his_pair_fadd.ps_5_minus_4"]["dN"]
fj = {"mean": L["mean"] / rate * 1e15, "lo": L["lo"] / rate * 1e15, "hi": L["hi"] / rate * 1e15, "P": L["forecast"]["P"] / rate * 1e15}


def rates(mode):
    return [v["rate"] / 1e11 for k, v in K.items() if k.split("/")[0] == mode]


ps_r, pi_r, psa_r, pia_r = rates("fadd.ps"), rates("fadd.pi"), rates("fadd.ps.acc"), rates("fadd.pi.acc")
r4 = [Dz[k] for k in R["E180-I"]["kinds"]]
H, A, O, X = R["E180-H"], R["E180-A"], R["E180-O"], R["E180-X"]
RA3 = sc["reported_v2"]["RA3_ladder_slope"]["R"]
RA5 = sc["reported_v2"]["RA5_anchors"]["fadd.ps/random - zeros, D"]
# (line, fragment as printed, the printed figure inside it, what it is, its committed value)
LIST = [
    (84, "median 0.870", "0.870", "the die rise: the kinds' mean rises' median (section 2)", med_kinds),
    (85, "4.5871-4.5930", "4.5871", "fadd.ps rate, least (10^11 a second)", min(ps_r)),
    (85, "4.5871-4.5930", "4.5930", "fadd.ps rate, most", max(ps_r)),
    (86, "(0.13% apart)", "0.13", "fadd.ps rates apart (%)", (max(ps_r) / min(ps_r) - 1) * 100),
    (86, "fadd.pi 4.563-4.568", "4.563", "fadd.pi rate, least", min(pi_r)),
    (86, "fadd.pi 4.563-4.568", "4.568", "fadd.pi rate, most", max(pi_r)),
    (86, "fadd.ps.acc 4.509-4.515", "4.509", "fadd.ps.acc rate, least", min(psa_r)),
    (86, "fadd.ps.acc 4.509-4.515", "4.515", "fadd.ps.acc rate, most", max(psa_r)),
    (86, "fadd.pi.acc 4.586", "4.586", "fadd.pi.acc rate, least", min(pia_r)),
    (86, "fadd.pi.acc 4.586", "4.586", "fadd.pi.acc rate, most", max(pia_r)),
    (89, "R3max (thirty result 1-bits) +0.326", "+0.326", "fadd.ps r3_max D", Dz["fadd.ps/r3_max"]),
    (89, "(P +4.947)", "+4.947", "fadd.ps r3_max P", FP["fadd.ps/r3_max"]["P"]),
    (89, "4: +0.189 /", "+0.189", "fadd.ps r3_k24 D", Dz["fadd.ps/r3_k24"]),
    (89, "/ +0.254 /", "+0.254", "fadd.ps r3_k20 D", Dz["fadd.ps/r3_k20"]),
    (89, "/ +0.209 /", "+0.209", "fadd.ps r3_k16 D", Dz["fadd.ps/r3_k16"]),
    (89, "/ +0.206 /", "+0.206", "fadd.ps r3_k12 D", Dz["fadd.ps/r3_k12"]),
    (89, "/ +0.158 /", "+0.158", "fadd.ps r3_k8 D", Dz["fadd.ps/r3_k8"]),
    (89, "/ +0.125;", "+0.125", "fadd.ps r3_k4 D", Dz["fadd.ps/r3_k4"]),
    (90, "0.5s +0.096", "+0.096", "fadd.ps 0.5s D", Dz["fadd.ps/f_0p5"]),
    (90, "0.5s +0.096 (P +1.154)", "+1.154", "fadd.ps 0.5s P", FP["fadd.ps/f_0p5"]["P"]),
    (90, "1.5s +0.102", "+0.102", "fadd.ps 1.5s D", Dz["fadd.ps/f_1p5"]),
    (90, "1.5s +0.102 (P +0.330)", "+0.330", "fadd.ps 1.5s P", FP["fadd.ps/f_1p5"]["P"]),
    (90, "const +0.068", "+0.068", "fadd.ps const D", Dz["fadd.ps/const"]),
    (90, "const +0.068 (P +0.165)", "+0.165", "fadd.ps const P", FP["fadd.ps/const"]["P"]),
    (90, "2s −0.024", "−0.024", "fadd.ps 2s D", Dz["fadd.ps/f_2"]),
    (90, "3s +0.094", "+0.094", "fadd.ps 3s D", Dz["fadd.ps/f_3"]),
    (90, "4s +0.022", "+0.022", "fadd.ps 4s D", Dz["fadd.ps/f_4"]),
    (90, "5s +0.049", "+0.049", "fadd.ps 5s D", Dz["fadd.ps/f_5"]),
    (90, "6s +0.064", "+0.064", "fadd.ps 6s D", Dz["fadd.ps/f_6"]),
    (90, "7s +0.060", "+0.060", "fadd.ps 7s D", Dz["fadd.ps/f_7"]),
    (91, "8s +0.084", "+0.084", "fadd.ps 8s D", Dz["fadd.ps/f_8"]),
    (91, "8s +0.084 (P +0.495)", "+0.495", "fadd.ps 8s P", FP["fadd.ps/f_8"]["P"]),
    (91, "−1 −0.001", "−0.001", "fadd.ps -1 D", Dz["fadd.ps/f_m1"]),
    (91, "−4 +0.060", "+0.060", "fadd.ps -4 D", Dz["fadd.ps/f_m4"]),
    (91, "−5 +0.059", "+0.059", "fadd.ps -5 D", Dz["fadd.ps/f_m5"]),
    (91, "fadd.ps random +8.455", "+8.455", "fadd.ps random D", Dz["fadd.ps/random"]),
    (91, "fadd.ps random +8.455 (P +8.726)", "+8.726", "fadd.ps random P", FP["fadd.ps/random"]["P"]),
    (91, "fadd.pi: random +3.171", "+3.171", "fadd.pi random D", Dz["fadd.pi/random"]),
    (91, "(P +9.639,", "+9.639", "fadd.pi random P", FP["fadd.pi/random"]["P"]),
    (91, "F +3.186)", "+3.186", "fadd.pi random F", FP["fadd.pi/random"]["F"]),
    (92, "eight R4 kinds −0.102 to", "−0.102", "fadd.pi R4 kinds' D, least", min(r4)),
    (92, "to +0.373.", "+0.373", "fadd.pi R4 kinds' D, most", max(r4)),
    (92, "fadd.ps.acc: 4s +0.382", "+0.382", "fadd.ps.acc 4s D", Dz["fadd.ps.acc/f_4"]),
    (92, "5s +0.696", "+0.696", "fadd.ps.acc 5s D", Dz["fadd.ps.acc/f_5"]),
    (92, "const +0.383", "+0.383", "fadd.ps.acc const D", Dz["fadd.ps.acc/const"]),
    (92, "(P +3.293,", "+3.293", "fadd.ps.acc 4s P", FP["fadd.ps.acc/f_4"]["P"]),
    (92, ", +3.281,", "+3.281", "fadd.ps.acc 5s P", FP["fadd.ps.acc/f_5"]["P"]),
    (92, ", +3.293).", "+3.293", "fadd.ps.acc const P", FP["fadd.ps.acc/const"]["P"]),
    (92, "int 1 / 4 / 5: +0.239 /", "+0.239", "fadd.pi.acc int 1 D", Dz["fadd.pi.acc/i_1"]),
    (93, "+0.269 /", "+0.269", "fadd.pi.acc int 4 D", Dz["fadd.pi.acc/i_4"]),
    (93, "/ +0.348 (P", "+0.348", "fadd.pi.acc int 5 D", Dz["fadd.pi.acc/i_5"]),
    (93, "(P +1.199 /", "+1.199", "fadd.pi.acc int 1 P", FP["fadd.pi.acc/i_1"]["P"]),
    (93, "/ +1.199 /", "+1.199", "fadd.pi.acc int 4 P", FP["fadd.pi.acc/i_4"]["P"]),
    (93, "/ +1.816)", "+1.816", "fadd.pi.acc int 5 P", FP["fadd.pi.acc/i_5"]["P"]),
    (94, "0.5s − 1.5s −0.006", "−0.006", "pair 0.5s - 1.5s D", Dz["fadd.ps/f_0p5"] - Dz["fadd.ps/f_1p5"]),
    (94, "(P +0.825)", "+0.825", "pair 0.5s - 1.5s P", FP["fadd.ps/f_0p5"]["P"] - FP["fadd.ps/f_1p5"]["P"]),
    (94, "const − 2s +0.091", "+0.091", "pair const - 2s D", Dz["fadd.ps/const"] - Dz["fadd.ps/f_2"]),
    (94, "(P −0.165)", "−0.165", "pair const - 2s P", FP["fadd.ps/const"]["P"] - FP["fadd.ps/f_2"]["P"]),
    (95, "(each above its zeros) −0.018", "−0.018", "pair fadd.ps 5s - fadd.pi 5s D", Dz["fadd.ps/f_5"] - Dz["fadd.pi/f_5"]),
    (95, "(P +0.495;", "+0.495", "pair fadd.ps 5s - fadd.pi 5s P", FP["fadd.ps/f_5"]["P"] - FP["fadd.pi/f_5"]["P"]),
    (95, "fadd.ps.acc 5s − 4s +0.314", "+0.314", "pair fadd.ps.acc 5s - 4s D", Dz["fadd.ps.acc/f_5"] - Dz["fadd.ps.acc/f_4"]),
    (95, "(P −0.012,", "−0.012", "pair fadd.ps.acc 5s - 4s P", FP["fadd.ps.acc/f_5"]["P"] - FP["fadd.ps.acc/f_4"]["P"]),
    (95, "F +0.132);", "+0.132", "pair fadd.ps.acc 5s - 4s F", FP["fadd.ps.acc/f_5"]["F"] - FP["fadd.ps.acc/f_4"]["F"]),
    (96, "fadd.pi.acc 5 − 4 +0.080", "+0.080", "pair fadd.pi.acc 5 - 4 D", Dz["fadd.pi.acc/i_5"] - Dz["fadd.pi.acc/i_4"]),
]
ELSE = [
    (1, "+0.027 W [-0.050, +0.104]", "+0.027", "E180-H mean", H["mean"]),
    (1, "+0.027 W [-0.050, +0.104]", "-0.050", "E180-H low end", H["lo"]),
    (1, "+0.027 W [-0.050, +0.104]", "+0.104", "E180-H high end", H["hi"]),
    (1, "the registered +0.165 W", "+0.165", "E180-H P", H["forecast"]["P"]),
    (1, "about 0.0097 W a bit (E180-L [+0.0027, +0.0167])", "0.0097", "E180-L mean", L["mean"]),
    (1, "(E180-L [+0.0027, +0.0167])", "+0.0027", "E180-L low end", L["lo"]),
    (1, "(E180-L [+0.0027, +0.0167])", "+0.0167", "E180-L high end", L["hi"]),
    (1, "about 1/17 of P's price", "17", "P's ladder slope over the measured slope", L["forecast"]["P"] / L["mean"]),
    (1, "rho +0.800", "+0.800", "E180-R rho", R["E180-R"]["rho"]),
    (1, "E180-A POSITIVE, +0.36 W", "+0.36", "E180-A mean", A["mean"]),
    (1, "about 0.12 of its forecast", "0.12", "E180-A mean over its P", A["mean"] / A["forecast"]["P"]),
    (55, "about 0.0097 W per 1-bit of v + v", "0.0097", "E180-L mean", L["mean"]),
    (55, "one seventeenth of P's 0.1649 W", "0.1649", "E180-L P", L["forecast"]["P"]),
    (56, "(A's 0.0192,", "0.0192", "E180-L A", L["forecast"]["A"]),
    (57, "0.01 W, and this session", "0.01", "his pair at the measured price (one result bit)", L["mean"]),
    (57, "about ±0.08 W", "0.08", "E180-H half-width", (H["hi"] - H["lo"]) / 2),
    (57, "the registered +0.165", "+0.165", "E180-H P", H["forecast"]["P"]),
    (58, "(±0.012 W a bit)", "0.012", "E180-O half-width", (O["hi"] - O["lo"]) / 2),
    (59, "by +0.36 W on 4s", "+0.36", "E180-A mean", A["mean"]),
    (59, "about 0.12 of P's", "0.12", "E180-A mean over its P", A["mean"] / A["forecast"]["P"]),
    (59, "P's +2.96 W", "+2.96", "E180-A P", A["forecast"]["P"]),
    (62, "rate 4.5836", "4.5836", "the registered fadd.ps rate (10^11 a second)", rate / 1e11),
    (62, "**about 21 fJ", "21", "E180-L mean over the rate (fJ)", fj["mean"]),
    (63, "([6, 36] fJ;", "6", "E180-L low end over the rate (fJ)", fj["lo"]),
    (63, "([6, 36] fJ;", "36", "E180-L high end over the rate (fJ)", fj["hi"]),
    (63, "about 2.6 fJ a lane", "2.6", "per lane, of eight (fJ)", fj["mean"] / 8),
    (63, "against P's 360 fJ", "360", "P's slope over the rate (fJ)", fj["P"]),
    (63, "the bench's 24.995 named", "24.995", "named flips per result bit (forecast-e180.json pairs)", dN),
    (64, "**about 0.85 fJ per named flip**", "0.85", "per named flip (fJ)", fj["mean"] / dN),
    (64, "([0.24, 1.45] fJ)", "0.24", "per named flip, low end", fj["lo"] / dN),
    (64, "([0.24, 1.45] fJ)", "1.45", "per named flip, high end", fj["hi"] / dN),
    (64, "against P's 14.395 fJ", "14.395", "P per named flip", fj["P"] / dN),
    (218, "at about 0.0097 W a bit", "0.0097", "E180-L mean", L["mean"]),
    (218, "1/17 of P's 0.1649", "17", "P's ladder slope over the measured slope", L["forecast"]["P"] / L["mean"]),
    (218, "1/17 of P's 0.1649", "0.1649", "E180-L P", L["forecast"]["P"]),
    (219, "0.0192). Every arm", "0.0192", "E180-L A", L["forecast"]["A"]),
    (220, "reproduces to 3%", "3", "the random row below the catalogue's (%)", (1 - RA5["mean"] / RA5["forecast"]["catalogue"]) * 100),
    (220, "(+8.45 W against +8.70)", "+8.45", "RA5 fadd.ps random - zeros, D", RA5["mean"]),
    (220, "(+8.45 W against +8.70)", "+8.70", "RA5 the catalogue's random - zeros", RA5["forecast"]["catalogue"]),
    (222, "(about 0.01 W against", "0.01", "his pair at the measured price (one result bit)", L["mean"]),
    (222, "against ±0.08 W)", "0.08", "E180-H half-width", (H["hi"] - H["lo"]) / 2),
    (223, "read to ±0.007 W a bit", "0.007", "E180-L half-width", (L["hi"] - L["lo"]) / 2),
    (223, "(yes, about 21 fJ a bit an", "21", "E180-L mean over the rate (fJ)", fj["mean"]),
    (224, "(+0.0093 W a bit [+0.0060,", "+0.0093", "RA3 on the rail, mean", RA3["mean"]),
    (224, "(+0.0093 W a bit [+0.0060,", "+0.0060", "RA3 on the rail, low end", RA3["lo"]),
    (225, "+0.0125], reported)", "+0.0125", "RA3 on the rail, high end", RA3["hi"]),
    (226, "(E180-O NULL, ±0.012 W a bit)", "0.012", "E180-O half-width", (O["hi"] - O["lo"]) / 2),
    (227, "within ±0.30 W (E180-I NULL)", "0.30", "E180-I margin", R["E180-I"]["margin"]),
    (227, "though at 0.12 of", "0.12", "E180-A mean over its P", A["mean"] / A["forecast"]["P"]),
    (228, "P's +0.165 W for his", "+0.165", "E180-H P", H["forecast"]["P"]),
    (229, "the float add's +0.5 W over the integer add", "+0.5", "E180-X P", X["forecast"]["P"]),
    (229, "P's +2.96 W for the running", "+2.96", "E180-A P", A["forecast"]["P"]),
    (231, "near 0.0097 W per result bit", "0.0097", "E180-L mean", L["mean"]),
    (231, "(95% 0.0027-0.0167;", "0.0027", "E180-L low end", L["lo"]),
    (231, "(95% 0.0027-0.0167;", "0.0167", "E180-L high end", L["hi"]),
    (232, "0.85 fJ a named flip", "0.85", "per named flip (fJ)", fj["mean"] / dN),
    (233, "at 50-57 °C", "50", "the live die reading, least (section 2)", die["min_c"]),
    (233, "at 50-57 °C", "57", "the live die reading, most (section 2)", die["max_c"]),
    (233, "mean rise was 0.87 °C", "0.87", "the bursts' mean rise, as the word 'mean' says (section 2)", statistics.mean(bursts)),
    (233, "mean rise was 0.87 °C", "0.87", "the kinds' mean rises' median (section 2)", med_kinds),
]


E = R["E180-E"]["groups"]
V2 = sc["reported_v2"]
RA1, RA2, RA4 = V2["RA1_const_minus_zeros"], V2["RA2_his_pair"], V2["RA4_A_on_rail"]
RA3x, RA5x = V2["RA3_ladder_slope"], V2["RA5_anchors"]
ARMS = ("P", "C", "E", "F", "A")


def ivl(name, d):
    return [(f"{name} mean", d["mean"]), (f"{name} low end", d["lo"]), (f"{name} high end", d["hi"])]


def arms(name, f):
    return [(f"{name} {arm}", f[arm]) for arm in ARMS]


def passes_of(name, xs_):
    return [(f"{name} pass {i + 1}", x) for i, x in enumerate(xs_)]


# the two tables, cell by cell: (line, cell index, the figures the cell prints in order; None = a number that is a label, not a figure)
TABLES = [
    (42, 2, ivl("E180-H", H) + passes_of("E180-H", H["x"])), (42, 3, arms("E180-H forecast", H["forecast"])),
    (43, 2, ivl("E180-L", L)), (43, 3, arms("E180-L forecast", L["forecast"])),
    (44, 2, ivl("E180-O", O)), (44, 3, [("E180-O margin", O["margin"])]),
    (45, 2, [("E180-R rho", R["E180-R"]["rho"])]), (45, 3, [("E180-R line", R["E180-R"]["line"])]),
    (46, 2, [None, ("E180-E popcount 2 spread", E["2"]["spread"]), ("E180-E popcount 3 spread", E["3"]["spread"])]),
    (46, 3, [("E180-E popcount 2 95% point", E["2"]["p95"]), ("E180-E popcount 3 95% point", E["3"]["p95"])]),
    (47, 2, ivl("E180-I", R["E180-I"])),
    (47, 3, [("E180-I margin", R["E180-I"]["margin"]), ("E180-I forecast F", R["E180-I"]["forecast"]["F"]),
             ("E180-I forecast A", R["E180-I"]["forecast"]["A"])]),
    (48, 2, ivl("E180-X", X)), (48, 3, arms("E180-X forecast", X["forecast"])),
    (49, 2, ivl("E180-A", A) + passes_of("E180-A", A["x"])), (49, 3, arms("E180-A forecast", A["forecast"])),
    (49, 4, [("P's offset band, low end", A["offset_band_P_W"][0]), ("P's offset band, high end", A["offset_band_P_W"][1])]),
    (73, 2, ivl("RA1 D", RA1["D"])), (73, 3, [("RA1 D forecast P", RA1["D"]["forecast"]["P"]), ("RA1 D forecast C", RA1["D"]["forecast"]["C"])]),
    (74, 2, ivl("RA1 R", RA1["R"])), (74, 3, [("RA1 R forecast P", RA1["R"]["forecast"]["P"])]),
    (75, 2, ivl("RA1 D_FL1", RA1["D_FL1"]) + ivl("RA1 D_E60", RA1["D_E60"])),
    (75, 3, [("RA1 D_FL1 forecast P", RA1["D_FL1"]["forecast"]["P"]), ("RA1 D_E60 forecast P", RA1["D_E60"]["forecast"]["P"])]),
    (76, 2, ivl("RA2 R", RA2["R"])),
    (76, 3, [("RA2 R forecast P", RA2["R"]["forecast"]["P"]), ("RA2 R forecast F", RA2["R"]["forecast"]["F"]),
             ("RA2 R forecast A", RA2["R"]["forecast"]["A"])]),
    (77, 2, ivl("RA2 D_FL1", RA2["D_FL1"]) + ivl("RA2 D_E60", RA2["D_E60"])),
    (77, 3, [("RA2 D_FL1 forecast P", RA2["D_FL1"]["forecast"]["P"]), ("RA2 D_E60 forecast P", RA2["D_E60"]["forecast"]["P"])]),
    (78, 2, ivl("RA3 R", RA3x["R"])), (78, 3, [("RA3 R forecast P", RA3x["R"]["forecast"]["P"])]),
    (79, 2, ivl("RA3 D_FL1", RA3x["D_FL1"]) + ivl("RA3 D_E60", RA3x["D_E60"])),
    (80, 2, ivl("RA4 R", RA4)), (80, 3, [("RA4 forecast P", RA4["forecast"]["P"])]),
    (81, 2, ivl("RA5 const - zeros D", RA5x["fadd.ps/const - zeros, D"]) + ivl("RA5 random - zeros D", RA5x["fadd.ps/random - zeros, D"])),
    (81, 3, [("RA5 the catalogue's const - zeros D", RA5x["fadd.ps/const - zeros, D"]["forecast"]["catalogue"]),
             ("RA5 the catalogue's random - zeros D", RA5x["fadd.ps/random - zeros, D"]["forecast"]["catalogue"])]),
    (82, 2, ivl("RA5 const - zeros R", RA5x["fadd.ps/const - zeros, R"]) + ivl("RA5 random - zeros R", RA5x["fadd.ps/random - zeros, R"])),
    (82, 3, [("RA5 the catalogue's const - zeros R", RA5x["fadd.ps/const - zeros, R"]["forecast"]["catalogue"]),
             ("RA5 the catalogue's random - zeros R", RA5x["fadd.ps/random - zeros, R"]["forecast"]["catalogue"])]),
]
NUM = re.compile(r"[+\-−]?\d+\.\d+")
TAB, tab_shape = [], []
for ln, ci, want in TABLES:
    cells = [c.strip() for c in RL[ln - 1].strip().strip("|").split("|")]
    got = NUM.findall(cells[ci]) if ci < len(cells) else []
    if len(got) != len(want):
        tab_shape.append((ln, ci, len(got), len(want)))
    for printed, w in zip(got, want):
        if w is not None:
            TAB.append((ln, printed, printed, w[0], w[1]))


def check(items):
    rows, missing = [], []
    for ln, frag, printed, what, v in items:
        txt = RL[ln - 1] if 0 < ln <= len(RL) else ""
        if frag not in txt or printed not in frag:
            missing.append((ln, frag))
        p = printed.replace(MINUS, "-").replace("+", "")
        dp = len(p.split(".")[1]) if "." in p else 0
        qd = Decimal(1).scaleb(-dp)
        pv = Decimal(p)
        exact = Decimal(v)
        right = exact.quantize(qd, rounding=ROUND_HALF_EVEN)
        twice = Decimal(f"{v:.{dp + 1}f}").quantize(qd, rounding=ROUND_HALF_UP)
        ok = pv == right
        rows.append({"line": ln, "what": what, "printed": printed, "value": v, "right": str(right),
                     "agrees": ok, "double_rounding": (not ok) and pv == twice})
    return rows, missing


r_list, m_list = check(LIST)
r_tab, m_tab = check(TAB)
r_else, m_else = check(ELSE)


def report(name, rows, missing, every=True):
    bad = [r for r in rows if not r["agrees"]]
    say(f"{name}: {len(rows)} figures; agree {len(rows) - len(bad)}; disagree {len(bad)}, of which double roundings "
        f"{sum(1 for r in bad if r['double_rounding'])}; fragments not found on their line: {len(missing)}" +
        (" " + str(missing) if missing else ""))
    for r in bad:
        dp = len(r["right"].split(".")[1]) if "." in r["right"] else 0
        say(f"  DISAGREES line {r['line']}: {r['what']}: printed {r['printed']}, committed {r['value']:+.6f}, at the printed precision "
            f"{sg(float(r['right']), dp)}" + (f"; the printed figure is the committed one rounded to {dp + 1} decimals ({sg(r['value'], dp + 1)}) "
                                              "and rounded again" if r["double_rounding"] else ""))
    if every:
        say("  every figure (line: what, printed, committed, at the printed precision, agrees):")
        for r in rows:
            say(f"    {r['line']}: {r['what']}, {r['printed']}, {r['value']:+.6f}, {r['right']}, {'yes' if r['agrees'] else 'NO'}")


report("lines 84-96, the bullets after the reported table", r_list, m_list)
report("the two tables (the rules, lines 42-49; the reported arms, lines 73-82), every figure of their measured and forecast cells and "
       "the E180-A band" + (f"; cells whose count of figures differs from the list: {tab_shape}" if tab_shape else
                            "; every cell's count of figures matches the list"), r_tab, m_tab, every=False)
say("  (each of these figures is in posthoc-note1-e180.json section_3.tables)")
report("elsewhere (lines 1, 55-64 and 218-233: the figures printed to three decimals or fewer from a committed figure)", r_else, m_else)
out["section_3"] = {"lines_84_96": r_list, "lines_84_96_missing": m_list, "tables": r_tab, "tables_missing": m_tab,
                    "tables_cell_count_mismatch": tab_shape, "elsewhere": r_else, "elsewhere_missing": m_else,
                    "rate": rate, "dN": dN, "fJ": fj}

say("")
say("nothing here is a rule or a verdict; every rule, verdict and figure of README.md stands but the words and figures the note corrects")
os.makedirs(OUT, exist_ok=True)
open(OUT_TXT, "w", encoding="utf-8").write("\n".join(lines) + "\n")
open(OUT_JSON, "w", encoding="utf-8").write(json.dumps(out, indent=1, sort_keys=True, ensure_ascii=False) + "\n")
print("\n".join(lines))
