#!/usr/bin/env python3
"""The matmul model report, second version: every number its README prints and its five figures draw, read or computed from
committed files only, each with its committed source. Desk.

    /usr/bin/python3 -I -B make_figures.py --repo <the lab's top> --out <dir> [--readme README.md]
    /usr/bin/python3 -I -B make_figures.py --list-inputs

Writes into <dir>: numbers.json (every number of the README: its value, the token the README prints, the README phrase that holds it,
its label and its committed source), tables.md (the README's generated tables, to paste), and fig-1-timing.svg, fig-2-scorecard.svg,
fig-3-switch.svg, fig-4-v31.svg, fig-5-gemmlnc.svg. Standard library only; no card, no device, no network; git is called read-only
(`git show <commit>:<path>`). Every input is pinned by its commit and its blob's sha256 (PINS below): a changed blob stops the run with
exit 4, a missing one with exit 3.

Sources (each entry of numbers.json names one):
  json  a value inside a committed JSON file (a key path);
  text  a committed literal of a committed text file (the README token must be one of the literal's numbers);
  desk  a named function of committed files (its inputs pinned), recomputed independently by check_numbers.py.

The desk functions (labels as in the README):
  e213  E213's scored cases and points on the first version's footing (forecast / measured - 1; cycles per case, the mean of its points;
        J over idle given the measured seconds per point at 3 W over idle and above; J with the card at rest given the seconds per point),
        read from the frozen scorer's committed 'measured' blocks and the frozen forecast CSVs, with the scorer's own definitions
        (score_e213.py: a case is the mean of its points; W given t = A + B / (the measured wall cycles an op / 600 MHz); a watts point is
        one whose MM1-v3 frozen W over idle or measured W over idle is under 3 W). The same code on measured / forecast - 1 reproduces
        the committed notes' figures (checked: the 'mf' entries).
  ratio E213's gemmLnc points and their gemmL twins: measured J over idle / MM1-v3's J given the measured seconds (= 1 + the scorer's E1
        error), from the scorer's committed cells.
  sim   the timing simulation against the card: the card's cycles a GEMM (the slowest minion) over the simulator's instruction count a
        minion a GEMM, as the frozen scorers print it, at every blind point that has one: E206's two arms and E207 (the first version's
        committed values) and E213's two arms (its scorer's committed readings).
  sum   sums of committed per-session figures (runs, card-minutes).
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

# ------------------------------------------------------------------------------------------------ the pinned inputs
V1 = "docs/reports/data/2026-11-17-matmul-model/"
D213A = "docs/reports/data/2026-11-18-e213-blind-matmul-aifoundry3/"
D213B = "docs/reports/data/2026-11-18-e213-blind-matmul-aifoundry1-c1/"
V3 = "tools/matmul/mm1/v3/"
V31 = "tools/matmul/mm1/v3.1/"
PINS = {
    # key: (commit, path, sha256 of the blob)
    "v1_numbers": ("600a8fb9", V1 + "numbers.json", None),
    "v1_readme": ("600a8fb9", V1 + "README.md", None),
    "e213A_scores": ("01283623", D213A + "scores-e213-A.json", "6d894c0307e14bbf3c86fc355ea35855950d11a27c2ea67a2f66b56164bb39e7"),
    "e213B_scores": ("b99b5265", D213B + "scores-e213-B.json", "692bfed37711d069c8fb185f2dae2c21490f5d957fac0cc365bdb3bfccdebb52"),
    "e213P_scores": ("f0d58c84", D213B + "scores-e213-pooled.json", None),
    "e213A_v3": ("b1493082", V3 + "out/mm1_v3_e213.csv", "01a2fdaef0b506b218fad1975dacf397a2c728010a595c8b4dadcbf569c07a49"),
    "e213A_v2": ("b1493082", V3 + "out/mm1_v2_e213.csv", "e1b99f682f303eaeaa818bc09a95e6484d8db5811c43991ae9d1b078476a43af"),
    "e213B_v3": ("291c8201", "tools/claims-v3/e213/forecast-e213b-v3.csv", "e529bbb24de26bc68c50279945c31a0da384e1f6c01cddc1f510cd2e1c0c4ed0"),
    "e213B_v2": ("291c8201", "tools/claims-v3/e213/forecast-e213b-v2.csv", "297762ebbbed7186631716b45aca33af73fd6f56ff769509d1d0c68ef0c411f4"),
    "e213A_note2": ("01283623", D213A + "README.md.dated-note-2.md", None),
    "e213A_readme": ("c69a12aa", D213A + "README.md", None),
    "e213B_note2": ("b99b5265", D213B + "README.md.dated-note-2.md", None),
    "e213B_note3": ("f0d58c84", D213B + "README.md.dated-note-3.md", None),
    "e213B_readme": ("b0c727c5", D213B + "README.md", None),
    "e213_reg": ("291c8201", "tools/claims-v3/e213/E213.md", None),
    "e213_a2": ("8b675547", "tools/claims-v3/e213-a2/E213.md.dated-amendment-A2.md", None),
    "e213_a3": ("8b675547", "tools/claims-v3/e213-a3/E213.md.dated-amendment-A3.md", None),
    "e212s3": ("29b741e0", V3 + "blind-e212s3/blind_v3_e212s3.json", None),
    "e212s3_readme": ("29b741e0", V3 + "blind-e212s3/README.md", None),
    "v3_unread_s4": ("b1493082", V3 + "out/unread_v3_e212s4.json", None),
    "v2_unread_e212": ("b1493082", V3 + "out/unread_v2_e212.json", None),
    "v3_readme": ("b1493082", V3 + "README.md", None),
    "unread_sw": ("f658861c", V31 + "unread-e212sw/scores-unread.json", None),
    "unread_sw_readme": ("f658861c", V31 + "unread-e212sw/README.md", None),
    "counts_readme": ("3e8991d0", V31 + "counts/README.md", None),
    "walk_readme": ("5a75e212", V31 + "walk/README.md", None),
    "v31_holdout": ("2c971828", V31 + "out/holdout_v31.json", None),
    "v31_readme": ("2c971828", V31 + "README.md", None),
    "v31_decl": ("7375bc9c", V31 + "DECLARED-v31.md", None),
    "e211_corr": ("ee0356d9", "tools/claims-v3/e211-notes/E211.md.A1-correction-1.md", None),
    "e212_reg": ("c83a29d1", "tools/claims-v3/e212/E212.md", None),
    "e214_reg": ("95eb8069", "tools/claims-v3/e214/E214.md", None),
    "e215_reg": ("4cb2c2ad", "tools/claims-v3/e215/E215.md", None),
    "v0_readme": ("2d1413f5", "tools/matmul/mm1/v0/README.md", None),
    "e213A_txt": ("01283623", D213A + "scores-e213-A.txt", None),
    "e213B_txt": ("b99b5265", D213B + "scores-e213-B.txt", None),
    "e213P_txt": ("f0d58c84", D213B + "scores-e213-pooled.txt", None),
    "seal_e212_1": ("a1602b0d", "tools/claims-v3/sealed-e212/e212-freeze-lines.md", None),
    "seal_e212_2": ("fcbf60c4", "tools/claims-v3/sealed-e212/e212-freeze-lines-2.md", None),
    "seal_e212_3": ("d8dc4897", "tools/claims-v3/sealed-e212/e212-freeze-lines-3.md", None),
    "seal_e213_1": ("8e91dda6", "tools/claims-v3/sealed-e213/e213-freeze-lines.md", None),
    "seal_e213_2": ("d8404ef2", "tools/claims-v3/sealed-e213/e213-freeze-lines-2.md", None),
    "seal_e214": ("b2230d68", "tools/claims-v3/sealed-e214/e214-freeze-lines.md", None),
    "seal_e215": ("18398ed2", "tools/claims-v3/sealed-e215/e215-freeze-lines.md", None),
    "lnc_readme": ("aaeaa495", "tools/matmul/mm1/v3.2-terms/gemmlnc/README.md", None),
    "lnc_note": ("aaeaa495", "tools/matmul/mm1/v3.2-terms/gemmlnc/README.md.dated-note-1.md", None),
    "lay_readme": ("595fcb59", "tools/matmul/mm1/v3.2-terms/layout/README.md", None),
    "lay_note": ("595fcb59", "tools/matmul/mm1/v3.2-terms/layout/README.md.dated-note-1.md", None),
    "v31_reported": ("2c971828", V31 + "out/reported_v31.json", None),
}
E212_SESSIONS = [  # (session, commit of its data folder, folder)
    ("a1c1-S1", "d2ece7e8", "docs/reports/data/2026-11-17-e212-mmsweep2-a1c1-S1/"),
    ("a1c0-S1", "5601b6a7", "docs/reports/data/2026-11-17-e212-mmsweep2-a1c0-S1/"),
    ("a1c1-S4", "7726e127", "docs/reports/data/2026-11-17-e212-mmsweep2-a1c1-S4/"),
    ("a1c0-S2", "a90105da", "docs/reports/data/2026-11-17-e212-mmsweep2-a1c0-S2/"),
    ("a1c1-S2", "7dfba40b", "docs/reports/data/2026-11-17-e212-mmsweep2-a1c1-S2/"),
    ("a2c0-S1", "ebe552fe", "docs/reports/data/2026-11-17-e212-mmsweep2-a2c0-S1/"),
    ("a1c1-S3", "d8de38b0", "docs/reports/data/2026-11-17-e212-mmsweep2-a1c1-S3/"),
    ("a2c0-S2", "58f01105", "docs/reports/data/2026-11-17-e212-mmsweep2-a2c0-S2/"),
    ("a2c0-S4", "724e8f39", "docs/reports/data/2026-11-17-e212-mmsweep2-a2c0-S4/"),
    ("a2c0-S3", "321f992c", "docs/reports/data/2026-11-18-e212-mmsweep2-a2c0-S3/"),
]
E214_SESSIONS = [
    ("a1c0-S1", "3b3e4182", "docs/reports/data/2026-11-18-e214-mmsweep3-a1c0-S1/"),
    ("a1c1-S1", "f7f3257c", "docs/reports/data/2026-11-18-e214-mmsweep3-a1c1-S1/"),
    ("a1c0-S2", "317ce38c", "docs/reports/data/2026-11-18-e214-mmsweep3-a1c0-S2/"),
    ("a1c1-S2", "a457d7fc", "docs/reports/data/2026-11-18-e214-mmsweep3-a1c1-S2/"),
    ("a1c0-S3", "117ca637", "docs/reports/data/2026-11-18-e214-mmsweep3-a1c0-S3/"),
    ("a1c1-S3", "9ac3c338", "docs/reports/data/2026-11-18-e214-mmsweep3-a1c1-S3/"),
    ("a1c1-S4", "0e95201d", "docs/reports/data/2026-11-18-e214-mmsweep3-a1c1-S4/"),
]
D215 = "tools/claims-v3/e215/"
D215A = "docs/reports/data/2026-11-19-e215-blind-matmul-aifoundry3/"
D215B = "docs/reports/data/2026-11-19-e215-blind-matmul-aifoundry1-c1/"
T32 = "tools/matmul/mm1/v3.2-terms/"
E215_COMMITS = {"terms_lnc": "aaeaa495", "terms_lay": "595fcb59", "terms_ctl": "595fcb59", "data_A": "8355db15", "data_B": "4f648f24",
                "scores_A": "7cddc406", "scores_B": "4cd7b864", "scores_P": "7edf3477",
                "scores_P_path": "docs/reports/data/2026-11-19-e215-blind-matmul-aifoundry1-c1/scores-e215-pooled.txt"}  # E215_COMMITS_LINE
if E215_COMMITS:
    PINS.update({
        # the frozen forecasts, each checked against the sha256 its freeze line names (E215.md section 0; Q225's posts #1.29, #1.29.1)
        "e215_points": ("4cb2c2ad", D215 + "points-e215.json", "d2bf8dddefdd0a565b531c55962cefe84ee1ef77618670ccbcd8e875f0646624"),
        "e215_rules": ("4cb2c2ad", D215 + "rules-e215.json", "e6d5c55421d890510a67db3d0de0453a44bfb9e0e12349e252b42c514bf6c5be"),
        "e215A_land": ("2c971828", V31 + "out/e215/mm1_v31_e215.json", "90742cddce9a355ddf53e85eb80a8075bc67613d36e804d12a8d422d342fd4d4"),
        "e215B_v31": ("4cb2c2ad", D215 + "forecast-e215b-v31.csv", "06541b49e7b86b510aa711bbda7da147806ef05c4c2b42be9c94b1447778cf80"),
        "e215B_v3": ("4cb2c2ad", D215 + "forecast-e215b-v3.csv", "12a91f344edc28184fefb6af131cee31e8a78dd47d86cd030f2ad695114a2c62"),
        "e215B_v2": ("4cb2c2ad", D215 + "forecast-e215b-v2.csv", "0f1c6297722de759e68386650a60afef2525f63c93d8a35b425ffbabc15b47a0"),
        "e215A_v2": ("4cb2c2ad", D215 + "forecast-e215a-v2.csv", "c220d569deb5ff5b54687e2ea012b6c291a493e0db9710481c69a7af89cdba1e"),
        "e215_t7": ("4cb2c2ad", D215 + "forecast-e215-t7.csv", "be96d94ac263bfd6c378c8dfb05cc00abf229f734aa7e2241f32a190d8b934bf"),
        "e215_lnc": (E215_COMMITS["terms_lnc"], T32 + "gemmlnc/forecasts-gemmlnc-e215.csv",
                     "00fcaf5dd05e7af5a95ce1b783b68588a416dde91d0434f4f82ba6bdee6f5a7c"),
        "e215_lay": (E215_COMMITS["terms_lay"], T32 + "layout/forecast-e215-v31-layout.csv",
                     "50949ba38ff7f16db601408fc523e81462cc04df3dddb38dd3007106e3a30754"),
        # the committed data's frozen scorer outputs (arm A's; arm B's and the pooled ones only when committed)
        "e215A_scores": (E215_COMMITS["scores_A"], D215A + "scores-e215-A.json", None),
        "e215A_txt": (E215_COMMITS["scores_A"], D215A + "scores-e215-A.txt", None),
    })
    PINS["e215A_readme"] = (E215_COMMITS.get("data_A", "8355db15"), D215A + "README.md", None)
    if E215_COMMITS.get("data_B"):
        PINS["e215B_readme"] = (E215_COMMITS["data_B"], D215B + "README.md", None)
        PINS["e215B_note1"] = ("2b0c8814", D215B + "README.md.dated-note-1.md", None)
    if E215_COMMITS.get("scores_B"):
        PINS["e215B_scores"] = (E215_COMMITS["scores_B"], D215B + "scores-e215-B.json", None)
        PINS["e215B_txt"] = (E215_COMMITS["scores_B"], D215B + "scores-e215-B.txt", None)
    if E215_COMMITS.get("scores_P"):
        PINS["e215P_txt"] = (E215_COMMITS["scores_P"], E215_COMMITS["scores_P_path"], None)
        PINS["e215P_note"] = (E215_COMMITS["scores_P"], D215B + "README.md.dated-note-3.md", None)
    if E215_COMMITS.get("terms_ctl"):  # verify-lay's REPORTED controls, posted #1.29.1.1 before any E215 datum
        PINS["e215_ctl"] = (E215_COMMITS["terms_ctl"], T32 + "layout/controls-e215/v02_e215_controls.csv",
                            "c5bc239479436db63649e3c83e0763a4b1d493af0bc4b4df1ce892e75b04066d")
    # report-v2-fix: the frozen terms' own REPORTED score on E215 (land-score-terms-e215, Q231), its verifier's dated note
    PINS["terms_note"] = ("c9adc716", T32 + "scores-e215/README.md.dated-note-1.md", None)
E214U_COMMITS = {"unread": "21ba4b45", "counts": "37ae4a87"}  # land-e214u (Q225), pushed 11:53-11:54 PST Thu 19 Nov  # E214U_COMMITS_LINE
if E214U_COMMITS:
    PINS.update({
        "e214u_scores": (E214U_COMMITS["unread"], V31 + "unread-e214/scores-unread-e214.json", None),
        "e214u_readme": (E214U_COMMITS["unread"], V31 + "unread-e214/README.md", None),
        "e214u_decl": (E214U_COMMITS["unread"], V31 + "unread-e214/DECLARED-unread-e214.md", None),
        "e214c_readme": (E214U_COMMITS["counts"], V31 + "counts-e214/README.md", None),
    })
for _s, _c, _d in E212_SESSIONS:
    PINS["e212_" + _s] = (_c, _d + "README.md", None)
for _s, _c, _d in E214_SESSIONS:
    PINS["e214_" + _s] = (_c, _d + "README.md", None)
LOW = 3.0  # W over idle: under it a point is scored in watts (E207's footing; score_e213.py's LOW)


class Repo:
    def __init__(self, top):
        self.top = top
        self.cache = {}

    def blob(self, commit, path):
        k = (commit, path)
        if k not in self.cache:
            r = subprocess.run(["git", "-C", self.top, "show", f"{commit}:{path}"], capture_output=True)
            if r.returncode != 0:
                print(f"make_figures: MISSING {commit}:{path}", file=sys.stderr)
                sys.exit(3)
            self.cache[k] = r.stdout
        return self.cache[k]

    def pinned(self, key):
        c, p, want = PINS[key]
        b = self.blob(c, p)
        got = hashlib.sha256(b).hexdigest()
        if want and got != want:
            print(f"make_figures: CHANGED {c}:{p} sha256 {got}, pinned {want}", file=sys.stderr)
            sys.exit(4)
        return b

    def text(self, key):
        return self.pinned(key).decode("utf-8")

    def json(self, key):
        return json.loads(self.pinned(key))

    def csv(self, key):
        return {r["id"]: r for r in csv.DictReader(io.StringIO(self.text(key)))}


def norm(s):
    """the text as a reader sees it: markdown emphasis and code marks removed, whitespace collapsed"""
    s = re.sub(r"(?m)^>[ ]?", "", s)
    return re.sub(r"\s+", " ", s.replace("**", "").replace("`", "")).strip()


def tok_in(tok, s):
    """a printed token inside a text: a number with digit boundaries (commas aside), an 8-hex prefix with word boundaries, else a substring"""
    if re.fullmatch(r"[0-9a-f]{8}", tok) and re.search(r"[a-f]", tok):
        return re.search(r"(?<![0-9A-Za-z])" + re.escape(tok) + r"(?![0-9A-Za-z])", s) is not None
    if re.fullmatch(r"[-+0-9.,:/e x of]+", tok) and re.search(r"[0-9]", tok):
        pat = lambda t: r"(?<![0-9.])" + re.escape(t) + r"(?![0-9])"
        if re.search(pat(tok), s):
            return True
        return "," in tok and re.search(pat(tok.replace(",", "")), s.replace(",", "")) is not None
    return tok in s


# ------------------------------------------------------------------------------------------------ the desk functions
def fnum(x):
    return None if x in ("", None) else float(x)


def fc_rows(rows):
    return {i: {"cw": fnum(r.get("cycles_per_op_wall")), "cm": fnum(r.get("cycles_per_op_mean")), "t": fnum(r.get("seconds_per_gemm")),
                "W": fnum(r.get("W_over_idle")), "A": fnum(r.get("A_W")), "B": fnum(r.get("B_W_us")), "J": fnum(r.get("J_over_idle_per_gemm"))}
            for i, r in rows.items()}


def e213_errors(R, arm):
    """per case and per point: (key, forecast / measured - 1, measured / forecast - 1) for each model and quantity (score_e213.py's
    definitions); Wwatts holds forecast - measured in W at the watts points"""
    S = R.json("e213%s_scores" % arm)["arms"][arm]
    fc = {"v3": fc_rows(R.csv("e213%s_v3" % arm)), "v2": fc_rows(R.csv("e213%s_v2" % arm))}
    M = S["measured"]
    scored = {p: v for p, v in M.items() if v["role"] == "point"}
    cases = {}
    for p, v in scored.items():
        cases.setdefault(v["case"], []).append(p)
    E = {}

    def add(q, mdl, key, fm, mf, loop):
        E.setdefault(q, {}).setdefault(mdl, []).append({"key": key, "fm": fm, "mf": mf, "loop": loop})
    for case, ids in sorted(cases.items()):
        meas = {k: sum(M[i][k] for i in ids) / len(ids) for k in ("cw", "cm", "t")}
        for mdl in ("v3", "v2"):
            f = fc[mdl].get(ids[0])
            for q, k in (("wall", "cw"), ("mean", "cm"), ("t", "t")):
                if f and f.get(k):
                    add(q, mdl, arm + ":" + case, f[k] / meas[k] - 1, meas[k] / f[k] - 1, M[ids[0]]["loop"])
    for p, v in sorted(scored.items()):
        f3 = fc["v3"][p]
        if v["W"] is None or f3["W"] is None:
            continue
        watts = f3["W"] < LOW or v["W"] < LOW
        for mdl in ("v3", "v2"):
            f = fc[mdl].get(p)
            if not f or f["W"] is None or f["A"] is None or f["B"] is None:
                continue
            Wg = f["A"] + f["B"] / (v["cw"] / 600.0)
            Jg = Wg * v["t"]
            if watts:
                add("Wwatts", mdl, arm + ":" + p, Wg - v["W"], Wg - v["W"], v["loop"])
            else:
                add("Jg", mdl, arm + ":" + p, Jg / v["J"] - 1, v["J"] / Jg - 1, v["loop"])
                add("Jf", mdl, arm + ":" + p, f["J"] / v["J"] - 1, v["J"] / f["J"] - 1, v["loop"])
            Jr = v["prest"] * v["t"] + Jg
            add("Jr", mdl, arm + ":" + p, Jr / v["Jrest"] - 1, v["Jrest"] / Jr - 1, v["loop"])
    return E


def agg(rows, conv, scale=100.0):
    v = [r[conv] for r in rows]
    if not v:
        return None
    return {"n": len(v), "rms": scale * math.sqrt(sum(e * e for e in v) / len(v)), "bias": scale * sum(v) / len(v)}


def e213_stat(cache, arm, model, q, conv="fm", no_lnc=False):
    """arm 'A', 'B' or 'P' (both arms)"""
    arms = ["A", "B"] if arm == "P" else [arm]
    rows = []
    for a in arms:
        rows += cache[a].get(q, {}).get(model, [])
    if no_lnc:
        rows = [r for r in rows if r["loop"] != "rgm136 gemmLnc"]
    return agg(rows, conv, 1.0 if q == "Wwatts" else 100.0)


def e213_ratios(R):
    """measured J over idle / MM1-v3's J given the measured seconds, at E213's gemmLnc points and their gemmL twins (E1's cells)"""
    out = {}
    pairs = {"A": [("a075", "a006"), ("a079", "a076"), ("a082", "a030"), ("a086", "a083"), ("a087", "a088")],
             "B": [("k37", "k06"), ("k40", None)]}
    for arm in ("A", "B"):
        S = R.json("e213%s_scores" % arm)["arms"][arm]
        cells = {c["point"]: c for c in S["cells"]["E1"]}
        for lnc, twin in pairs[arm]:
            c = cells[lnc]
            out[lnc] = {"arm": arm, "role": "gemmLnc", "ratio": c["measured"] / c["v3"], "arm_key": S["measured"][lnc]["case"]}
            if twin and twin in cells:
                t = cells[twin]
                out[twin] = {"arm": arm, "role": "gemmL twin of " + lnc, "ratio": t["measured"] / t["v3"], "arm_key": S["measured"][twin]["case"]}
    return out


def sim_values(R):
    """the card's cycles a GEMM over the simulator's instruction count a minion a GEMM, at every blind point that has one"""
    v1 = R.json("v1_numbers")["timing"]["sim_ratio"]["values"]
    vals = {"E206-E207": [x["ratio"] if isinstance(x, dict) else x for x in v1]}
    for arm in ("A", "B"):
        S = R.json("e213%s_scores" % arm)["arms"][arm]
        ts = S["readings_REPORTED"]["timing_simulation"]
        vals["E213" + arm] = [r["cycles_gemm_over_sim_steps"] for p, r in sorted(ts.items())
                              if r.get("cycles_gemm_over_sim_steps") is not None and S["measured"][p]["role"] == "point"]
    if "e215A_scores" in PINS:
        for arm in ARMS215:
            S = R.json("e215%s_scores" % arm)["arms"][arm]
            ts = S["readings_REPORTED"]["timing_simulation"]
            vals["E215" + arm] = [r["cycles_gemm_over_sim_steps"] for p, r in sorted(ts.items())
                                  if r.get("cycles_gemm_over_sim_steps") is not None and S["measured"][p]["role"] == "point"]
    return vals


def sim_all_of(sim):
    return [v for k in ("E206-E207", "E213A", "E213B", "E215A", "E215B") for v in sim.get(k, [])]


def readme_card_minutes(txt):
    m = re.search(r"\*\*([0-9.]+) card-minutes\*\*", txt)
    return float(m.group(1)) if m else None


def readme_runs(txt):
    m = re.search(r"RAN FULL \((\d+) of (\d+) runs\)", txt.splitlines()[0])
    return int(m.group(1)) if m else None


# ------------------------------------------------------------------------------------------------ E215 (desk; score_e215.py's definitions)
G215 = {"registered": ("P", "C", "R"), "posthoc": ("L", "S")}
FAM215 = ("L", "S", "P", "C", "R")  # a family letter as the 'only' filter (report-v2-fix added S, P, C and R to L)
M215 = ("v31", "v3", "v2", "t7", "lnc", "lay", "lg1", "cnt")
N215 = {"v31": "MM1-v3.1", "v3": "MM1-v3", "v2": "MM1-v2", "t7": "v3.1 with T7", "lnc": "v3.1 + gemmLnc term", "lay": "v3.1 + contention",
        "lg1": "v3.1 + G1 (hop mean)", "cnt": "v3.1 + N1+N2 (shire count only)"}


def e215_fc(R):
    """every frozen E215 forecast by arm, point and model: MM1-v3.1's and MM1-v3's arm A columns from MM1-v3.1's land (via points-e215.json's
    source tokens), arm B's and MM1-v2's from the registration's CSVs, 'v3.1 with T7' from its CSV, and the two candidate terms frozen
    before any E215 datum: 'v3.1 + gemmLnc term' (energy only, at its five gemmLnc points; its time is MM1-v3.1's) and 'v3.1 + contention'
    (time only: the wall cycles and seconds), with its REPORTED G1 hop-mean form beside (the wall cycles)"""
    P = R.json("e215_points")
    land = {q["token"]: q for q in R.json("e215A_land")["points"]}

    def pred(r):
        wa = r.get("W_affine") or {}
        return {"cw": r.get("cycles_per_op_wall"), "cm": r.get("cycles_per_op_mean"), "t": r.get("seconds_per_gemm"), "W": r.get("W_over_idle"),
                "A": wa.get("A_W"), "B": wa.get("B_W_us"), "J": r.get("J_over_idle_per_gemm")}

    def row(r):
        g = lambda k: (None if r.get(k) in ("", None, "NOT FORECAST") else float(r[k]))
        return {"cw": g("cycles_per_op_wall"), "cm": g("cycles_per_op_mean"), "t": g("seconds_per_gemm"), "W": g("W_over_idle"),
                "A": g("A_W"), "B": g("B_W_us"), "J": g("J_over_idle_per_gemm")}
    fc = {"A": {}, "B": {}}
    for p in P["arms"]["A"]["points"]:
        q = land[p["source_token"]]
        fc["A"].setdefault(p["id"], {}).update({"v31": pred(q["v31"]), "v3": pred(q["v3"])})
    for key, tag, m in (("e215B_v31", "B", "v31"), ("e215B_v3", "B", "v3"), ("e215B_v2", "B", "v2"), ("e215A_v2", "A", "v2")):
        for i, r in R.csv(key).items():
            fc[tag].setdefault(i, {})[m] = row(r)
    for i, r in R.csv("e215_t7").items():
        fc["A" if r["card"] == "aifoundry3 card 0" else "B"].setdefault(i, {})["t7"] = row(r)
    for i, r in R.csv("e215_lnc").items():
        if r["role"].startswith("point"):
            fc[r["arm"]].setdefault(i, {})["lnc"] = {"cw": None, "cm": None, "t": None, "W": float(r["lnc_W_over_idle"]), "A": float(r["lnc_A_W"]),
                                                     "B": float(r["lnc_B_W_us"]), "J": float(r["lnc_J_over_idle"])}
    for i, r in R.csv("e215_lay").items():
        if r["role"] == "point":
            fc[r["e215_arm"]].setdefault(i, {})["lay"] = {"cw": float(r["v31c_cycles_per_op_wall"]), "cm": None,
                                                          "t": float(r["v31c_seconds_per_gemm"]), "W": None, "A": None, "B": None, "J": None}
            fc[r["e215_arm"]][i]["lg1"] = {"cw": float(r["REPORTED_G1_cycles_per_op_wall"]), "cm": None, "t": None, "W": None, "A": None,
                                           "B": None, "J": None}
    if "e215_ctl" in PINS:
        for i, r in R.csv("e215_ctl").items():
            tag = "A" if i.startswith("a") else ("B" if i.startswith("b") else None)
            if tag and i in fc[tag]:
                fc[tag][i]["cnt"] = {"cw": float(r["REPORTED_N1+N2_cycles_per_op_wall"]), "cm": None, "t": None, "W": None, "A": None,
                                     "B": None, "J": None}
    return fc


def e215_errors(R, fc, tag):
    """per group, quantity and model, the rows (key, forecast / measured - 1, measured / forecast - 1; at a watts point W forecast - W
    measured): cases (the mean of their points) for the wall, the counter's mean and seconds; points for J over idle given the measured
    seconds (Jg), with the seconds forecast (Jf), and J at rest given t (Jr); a watts point is one whose MM1-v3.1 frozen or measured W over
    idle is under 3 W (score_e215.py's rule, read for every model from MM1-v3.1's)"""
    M = R.json("e215%s_scores" % tag)["arms"][tag]["measured"]
    E = {}

    def add(g, q, mdl, key, fm, mf, extra):
        E.setdefault(g, {}).setdefault(q, {}).setdefault(mdl, []).append(dict({"key": key, "fm": fm, "mf": mf}, **extra))
    for g, fams in G215.items():
        sc = {p: v for p, v in M.items() if v["role"] == "point" and v["family"] in fams}
        cases = {}
        for p in sorted(sc):
            if sc[p]["time_scored"]:
                cases.setdefault(sc[p]["case"], []).append(p)
        for case, ids in sorted(cases.items()):
            meas = {k: sum(M[i][k] for i in ids) / len(ids) for k in ("cw", "cm", "t")}
            F = fc[tag][ids[0]]
            for q, k in (("wall", "cw"), ("mean", "cm"), ("t", "t")):
                for mdl in M215:
                    f = (F.get(mdl) or {}).get(k)
                    if f:
                        add(g, q, mdl, tag + ":" + case, f / meas[k] - 1, meas[k] / f - 1, {"family": M[ids[0]]["family"], "loop": M[ids[0]]["loop"]})
        for p, v in sorted(sc.items()):
            F = fc[tag][p]
            f31 = F["v31"]
            if v["W"] is None or f31.get("W") is None:
                continue
            watts = f31["W"] < LOW or v["W"] < LOW
            ex = {"family": v["family"], "loop": v["loop"], "watts": watts}
            for mdl in M215:
                f = F.get(mdl) or {}
                if f.get("W") is None or f.get("A") is None or f.get("B") is None:
                    continue
                Wg = f["A"] + f["B"] / (v["cw"] / 600.0)
                Jg = Wg * v["t"]
                if watts:
                    add(g, "Wwatts", mdl, tag + ":" + p, Wg - v["W"], Wg - v["W"], ex)
                else:
                    add(g, "Jg", mdl, tag + ":" + p, Jg / v["J"] - 1, v["J"] / Jg - 1, ex)
                    add(g, "Jf", mdl, tag + ":" + p, f["J"] / v["J"] - 1, v["J"] / f["J"] - 1, ex)
                Jr = v["prest"] * v["t"] + Jg
                add(g, "Jr", mdl, tag + ":" + p, Jr / v["Jrest"] - 1, v["Jrest"] / Jr - 1, ex)
    return E


def e215_rows(cache, arm, group, model, q, only=None):
    """arm 'A', 'B' or 'P' (both); group 'registered', 'posthoc'; only: None, one family's letter ('L', 'S', 'P', 'C', 'R'), 'lnc' (the
    gemmLnc loop) or 'nolnc' (every other loop)"""
    rows = []
    for a in (["A", "B"] if arm == "P" else [arm]):
        rows += cache[a].get(group, {}).get(q, {}).get(model, [])
    if only in FAM215:
        rows = [r for r in rows if r["family"] == only]
    elif only == "lnc":
        rows = [r for r in rows if r["loop"] == "rgm136 gemmLnc"]
    elif only == "nolnc":
        rows = [r for r in rows if r["loop"] != "rgm136 gemmLnc"]
    return rows


def e215_stat(cache, arm, group, model, q, conv="fm", only=None):
    return agg(e215_rows(cache, arm, group, model, q, only), conv, 1.0 if q == "Wwatts" else 100.0)


def e215_one(cache, arm, group, model, q, conv, key):
    """one case's or point's error (in % of the measured or forecast value; W at a watts point), its key without the arm prefix"""
    for r in cache[arm].get(group, {}).get(q, {}).get(model, []):
        if r["key"] == arm + ":" + key:
            return (1.0 if q == "Wwatts" else 100.0) * r[conv]
    raise KeyError(key)


def e215_miss(cache, rules, arm, group, model, q, rule, only=None):
    """REPORTED: how many cases (points) of a model sit past MM1-v3.1's registered band of that rule (measured / forecast - 1); only: as
    e215_rows (report-v2-fix added it)"""
    n = 0
    for a in (["A", "B"] if arm == "P" else [arm]):
        band = rules["arms"][a]["bands"][rule]["band"]
        n += sum(1 for r in e215_rows(cache, a, group, model, q, only) if abs(r["mf"]) > band)
    return n


def e215_closer(cache, rules, arm, group, model, q, only=None, base_model="v31"):
    """REPORTED: model against MM1-v3.1 (or base_model, added by report-v2-fix) case by case (point by point), E215's d = |ln(measured /
    base)| - |ln(measured / model)| (in W at a watts point) against each arm's registered tie; closer / farther / ties and the exact two-sided
    sign test"""
    out = {"closer": 0, "farther": 0, "ties": 0}
    tk = {"wall": "cycles_ln", "mean": "cycles_ln", "t": "seconds_ln", "Jg": "joules_ln", "Jf": "joules_ln", "Wwatts": "watts_W"}[q]
    for a in (["A", "B"] if arm == "P" else [arm]):
        base = {r["key"]: r for r in e215_rows(cache, a, group, base_model, q, only)}
        tie = rules["arms"][a]["ties"][tk]
        for r in e215_rows(cache, a, group, model, q, only):
            b = base[r["key"]]
            d = (abs(b["fm"]) - abs(r["fm"])) if q == "Wwatts" else (abs(math.log(1 + b["fm"])) - abs(math.log(1 + r["fm"])))
            out["closer" if d > tie else ("farther" if d < -tie else "ties")] += 1
    n, k = out["closer"] + out["farther"], min(out["closer"], out["farther"])
    out["p"] = min(1.0, 2 * sum(math.comb(n, i) for i in range(k + 1)) / 2 ** n) if n else 1.0
    return out


# ------------------------------------------------------------------------------------------------ the registry
class Reg:
    def __init__(self, R):
        self.R = R
        self.items = []
        self.keys = set()
        self.rows = []

    def _add(self, key, value, printed, phrase, source, label):
        if key in self.keys:
            raise SystemExit(f"make_figures: duplicate key {key}")
        self.keys.add(key)
        self.items.append({"key": key, "value": value, "printed": printed, "phrase": phrase, "label": label, "source": source})

    def json(self, key, pin, pointer, fmt, phrase, label="", scale=None):
        d = self.R.json(pin)
        v = d
        for k in pointer:
            v = v[k]
        printed = fmt.format(v * scale if scale else v)
        c, p, _ = PINS[pin]
        src = {"kind": "json", "commit": c, "path": p, "pointer": pointer, "fmt": fmt}
        if scale:
            src["scale"] = scale
        self._add(key, v, printed, phrase, src, label)
        return printed

    def git(self, key, commit, want, phrase, label="the commit's own time (git, Pacific)", fmt="%H:%M:%S"):
        r = subprocess.run(["git", "-C", self.R.top, "log", "-1", "--format=%cd", "--date=format-local:" + fmt, commit],
                           capture_output=True, text=True, env=dict(os.environ, TZ="America/Los_Angeles"))
        got = r.stdout.strip()
        if got != want:
            raise SystemExit(f"make_figures: {commit} committed at {got}, not {want}")
        self._add(key, got, got, phrase, {"kind": "git", "commit": commit, "fmt": fmt, "tz": "America/Los_Angeles"}, label)

    def absent(self, key, commit, path, phrase, label="no such path at the pin"):
        r = subprocess.run(["git", "-C", self.R.top, "ls-tree", "-d", "--name-only", commit, path], capture_output=True, text=True)
        if r.stdout.strip():
            raise SystemExit(f"make_figures: {path} exists at {commit}")
        self._add(key, None, "none", phrase, {"kind": "absent", "commit": commit, "path": path}, label)

    def text(self, key, pin, literal, token, phrase, label=""):
        t = norm(self.R.text(pin))
        lit = norm(literal)
        if lit not in t:
            raise SystemExit(f"make_figures: literal not in {PINS[pin][1]}: {literal!r}")
        if not tok_in(token, lit):
            raise SystemExit(f"make_figures: token {token!r} not in literal {literal!r}")
        c, p, _ = PINS[pin]
        self._add(key, token, token, phrase, {"kind": "text", "commit": c, "path": p, "literal": literal}, label)
        return token

    def desk(self, key, value, fmt, phrase, fn, args, inputs, label=""):
        printed = fmt.format(value)
        self._add(key, value, printed, phrase, {"kind": "desk", "fn": fn, "args": args, "fmt": fmt,
                                                "inputs": [{"commit": PINS[i][0], "path": PINS[i][1]} for i in inputs]}, label)
        return printed


def sgn(x, d=1):
    return ("{:+.%df}" % d).format(x).replace("+-", "-")


# ------------------------------------------------------------------------------------------------ the scorecard
TESTS_V1 = [  # (row label, the first version's test key, its set or None, [(model key, model label, label)])
    ("E206 arm A (aifoundry3 card 0, 600 MHz)", "E206A", None,
     [("v0", "MM1-v0", "blind; REPORTED"), ("F1", "F1", "blind; REPORTED"), ("F2", "F2", "blind; REPORTED")]),
    ("E206 arm B (aifoundry1 card 1, 600 MHz)", "E206B", None,
     [("v1", "MM1-v1", "card-transfer; REPORTED"), ("v0", "MM1-v0", "blind; REPORTED"), ("F1", "F1", "blind; REPORTED"),
      ("F2", "F2", "blind; REPORTED")]),
    ("E207 (aifoundry3 card 0, 600 MHz)", "E207", None,
     [("v2", "MM1-v2", "shape-blind; REPORTED"), ("v1", "MM1-v1", "shape-blind; registered rules"), ("F1", "F1", "shape-blind; registered head-to-head"),
      ("F2", "F2", "shape-blind; registered head-to-head")]),
    ("E209 (aifoundry2 card 0, its governor)", "E209", None,
     [("v2", "MM1-v2", "blind; registered rules"), ("v1", "MM1-v1", "blind; registered head-to-head"), ("F1", "F1@800", "blind; registered head-to-head")]),
    ("E211, rgm211's 12 points (aifoundry3 card 0)", "E211", "rgm211_12",
     [("v2", "MM1-v2", "blind; REPORTED"), ("v1", "MM1-v1", "blind; registered rules"), ("F1", "F1", "blind; registered head-to-head"),
      ("NC", "NC, a null", "blind; registered head-to-head")]),
]
Q_V1 = {"wall": "cyc_wall", "mean": "cyc_mean", "jg3": "jo_g3", "jr": "jr_g"}
Q_E212 = {"wall": "wall", "mean": "counter_mean", "jg3": "W_given_t_ge3W", "jr": "J_at_rest_given_t"}
Q_E213 = {"wall": "wall", "mean": "mean", "jg3": "Jg", "jr": "Jr"}
E213_INPUTS = ["e213A_scores", "e213B_scores", "e213A_v3", "e213A_v2", "e213B_v3", "e213B_v2"]
E215_INPUTS = ["e215_points", "e215_rules", "e215A_land", "e215B_v31", "e215B_v3", "e215B_v2", "e215A_v2", "e215_t7", "e215_lnc", "e215_lay",
               "e215A_scores"] + (["e215B_scores"] if "e215B_scores" in PINS else []) + (["e215_ctl"] if "e215_ctl" in PINS else [])
ARMS215 = [a for a in ("A", "B") if "e215%s_scores" % a in PINS]
PA215 = "P" if ARMS215 == ["A", "B"] else (ARMS215[0] if ARMS215 else None)  # the pooled key, or the one arm
WHERE215 = "both arms" if PA215 == "P" else "arm %s" % PA215


def cell_json(R, pin, base, bias_key="bias_pct"):
    """a stat dict at a JSON path, or None"""
    x = R.json(pin)
    for p in base:
        if not isinstance(x, dict) or p not in x or x[p] is None:
            return None
        x = x[p]
    if not isinstance(x, dict) or "rms_pct" not in x:
        return None
    return {"src": ("json", pin, base), "n": x["n"], "rms": x["rms_pct"], "bias": x[bias_key], "bias_key": bias_key}


def cell_desk(cache, arm, model, q):
    s = e213_stat(cache, arm, model, q)
    if s is None:
        return None
    return {"src": ("desk", {"arm": arm, "model": model, "q": q, "conv": "fm"}), "n": s["n"], "rms": s["rms"], "bias": s["bias"]}


def sc_rows(R, cache, c215=None):
    """every scorecard row: (test, model label, label, {q: cell}); E215's when its cache is given"""
    rows = []
    for test, tk, setk, models in TESTS_V1:
        for mk, ml, lab in models:
            cells = {}
            for q, qq in Q_V1.items():
                base = (["blind", tk, "models", mk, qq] if setk is None else ["blind", tk, "sets", setk, mk, qq])
                cells[q] = cell_json(R, "v1_numbers", base)
            rows.append((test, ml, lab, cells))
    rows.append(("E212, eight sessions (three cards)", "MM1-v2", "unread",
                 {q: cell_json(R, "v2_unread_e212", ["per_case", "all", qq]) for q, qq in Q_E212.items()}))
    for m, ml in (("v3", "MM1-v3"), ("v2", "MM1-v2")):
        rows.append(("E212 a2c0-S4 (aifoundry2 card 0, its governor)", ml, "unread",
                     {q: cell_json(R, "v3_unread_s4", ["per_case", m, qq]) for q, qq in Q_E212.items()}))
    for m, ml in (("v3", "MM1-v3"), ("v2", "MM1-v2")):
        rows.append(("E212 a2c0-S3, re-run (aifoundry2 card 0, its governor)", ml, "blind; REPORTED",
                     {q: cell_json(R, "e212s3", ["per_case", m, qq]) for q, qq in Q_E212.items()}))
    for arm, test in (("A", "E213 arm A (aifoundry3 card 0, 600 MHz)"), ("B", "E213 arm B (aifoundry1 card 1, 600 MHz)"),
                      ("P", "E213, both arms")):
        for m, ml in (("v3", "MM1-v3"), ("v2", "MM1-v2")):
            rows.append((test, ml, "blind; registered rules" if m == "v3" else "blind; registered head-to-head",
                         {q: cell_desk(cache, arm, m, qq) for q, qq in Q_E213.items()}))
    for m, ml in (("V3", "MM1-v3 with the new counts"), ("N", "N, each format's mean kind")):
        rows.append(("E212's plan tiles and E206's and E207's real tiles (three cards)", ml,
                     "unread; registered pass rule" if m == "V3" else "unread; the pass rule's null",
                     {"wall": None, "mean": None, "jr": None,
                      "jg3": cell_json(R, "unread_sw", ["groups", "A", "all", m, "Q1_cases"], "mean_pct")}))
    if "e214u_scores" in PINS:
        for m, ml in (("v31", "MM1-v3.1"), ("v3", "MM1-v3"), ("v2", "MM1-v2")):
            base = ["tables_per_case", m]
            rows.append(("E214, seven sessions, no configuration twins (aifoundry1 cards 0 and 1)", ml, "unread; declared rules",
                         {"wall": cell_json(R, "e214u_scores", base + ["wall", "pooled", "no_twin"]),
                          "mean": cell_json(R, "e214u_scores", base + ["mean", "pooled", "no_twin"]),
                          "jg3": cell_json(R, "e214u_scores", base + ["E1", "pooled", "no_twin", "relative"]),
                          "jr": cell_json(R, "e214u_scores", base + ["E3", "pooled", "no_twin"])}))
        for m, ml in (("model", "MM1-v3.1 with the new counts"), ("N", "N, each format's mean kind")):
            rows.append(("E214's 20 new tile kinds (aifoundry1 cards 0 and 1)", ml,
                         "unread; declared pass rule" if m == "model" else "unread; the pass rule's null",
                         {"wall": None, "mean": None, "jr": None, "jg3": cell_json(R, "e214u_scores", ["part_S", "v31", "Q1", m])}))
    if c215 is not None:
        rows += sc_rows_e215(c215)
    return rows


E215_TESTS = [("A", "registered", "E215 arm A, families P, C, R (aifoundry3 card 0, 600 MHz)", (("v31", "blind; registered rules"),
              ("v3", "blind; registered head-to-head"), ("v2", "blind; REPORTED"))),
              ("A", "posthoc", "E215 arm A, families L, S (aifoundry3 card 0, 600 MHz)", (("v31", "blind, post hoc-selected; apart"),
              ("v3", "blind, post hoc-selected; apart"))),
              ("B", "registered", "E215 arm B, families P, C, R (aifoundry1 card 1, 600 MHz)", (("v31", "blind; registered rules"),
              ("v3", "blind; registered head-to-head"), ("v2", "blind; REPORTED"))),
              ("B", "posthoc", "E215 arm B, families L, S (aifoundry1 card 1, 600 MHz)", (("v31", "blind, post hoc-selected; apart"),
              ("v3", "blind, post hoc-selected; apart"))),
              ("P", "registered", "E215, both arms, families P, C, R", (("v31", "blind; registered rules"), ("v3", "blind; registered head-to-head")))]
Q_E215 = {"wall": "wall", "mean": "mean", "jg3": "Jg", "jr": "Jr"}


def cell_desk215(c215, arm, group, model, q, only=None):
    s = e215_stat(c215, arm, group, model, q, "fm", only)
    if s is None:
        return None
    args = {"arm": arm, "group": group, "model": model, "q": q, "conv": "fm"}
    if only:
        args["only"] = only
    return {"src": ("desk", args, "e215"), "n": s["n"], "rms": s["rms"], "bias": s["bias"]}


def sc_rows_e215(c215):
    rows = []
    for arm, g, test, models in E215_TESTS:
        if (arm == "P" and PA215 != "P") or (arm in ("A", "B") and arm not in ARMS215):
            continue
        for m, lab in models:
            rows.append((test, N215[m], lab, {q: cell_desk215(c215, arm, g, m, qq) for q, qq in Q_E215.items()}))
    return rows


def sc_text(row):
    test, ml, lab, cells = row
    n_t = str(cells["wall"]["n"]) if cells.get("wall") else "-"
    n_e = str(cells["jg3"]["n"]) if cells.get("jg3") else "-"
    parts = []
    for q in ("wall", "mean", "jg3", "jr"):
        c = cells.get(q)
        parts.append("-" if c is None else "{:.1f} ({})".format(c["rms"], sgn(c["bias"])))
    return f"| {test} | {ml} | {lab} | {n_t} / {n_e} | " + " | ".join(parts) + " |"


def desk_src(c):
    """a desk cell's (function, args, inputs): E213's cells carry ('desk', args), E215's ('desk', args, 'e215')"""
    if len(c["src"]) == 3 and c["src"][2] == "e215":
        return "e215", c["src"][1], E215_INPUTS
    return "e213", c["src"][1], E213_INPUTS


def reg_cell(G, key, c, phrase, what):
    kind = c["src"][0]
    if kind == "json":
        _, pin, base = c["src"]
        G.json(key + ".rms", pin, base + ["rms_pct"], "{:.1f}", phrase, what + ", rms %")
        G.json(key + ".bias", pin, base + [c["bias_key"]], "{:+.1f}", phrase, what + ", bias %")
    else:
        fn, args, inputs = desk_src(c)
        G.desk(key + ".rms", c["rms"], "{:.1f}", phrase, fn, dict(args, stat="rms"), inputs, what + ", rms %, desk")
        G.desk(key + ".bias", c["bias"], "{:+.1f}", phrase, fn, dict(args, stat="bias"), inputs, what + ", bias %, desk")


def reg_n(G, key, c, phrase, what):
    if c["src"][0] == "json":
        _, pin, base = c["src"]
        G.json(key, pin, base + ["n"], "{:d}", phrase, what + ", count")
    else:
        fn, args, inputs = desk_src(c)
        G.desk(key, c["n"], "{:d}", phrase, fn, dict(args, stat="n"), inputs, what + ", count, desk")


def reg_scorecard(G, rows):
    out = []
    for row in rows:
        test, ml, lab, cells = row
        phrase = sc_text(row)
        key = "sc." + re.sub(r"[^A-Za-z0-9]+", "_", test + "." + ml).strip("_")
        if cells.get("wall"):
            reg_n(G, key + ".n_time", cells["wall"], phrase, "cases")
        if cells.get("jg3"):
            reg_n(G, key + ".n_energy", cells["jg3"], phrase, "points")
        for q in ("wall", "mean", "jg3", "jr"):
            if cells.get(q):
                reg_cell(G, f"{key}.{q}", cells[q], phrase, q)
        out.append(phrase)
    return out


def newest_and_f1(rows):
    """the newest MM1 frozen before each blind test, and F1 on the first version's five tests (the summary's ranges)"""
    newest = {"E206 arm A (aifoundry3 card 0, 600 MHz)": "MM1-v0", "E206 arm B (aifoundry1 card 1, 600 MHz)": "MM1-v1",
              "E207 (aifoundry3 card 0, 600 MHz)": "MM1-v2", "E209 (aifoundry2 card 0, its governor)": "MM1-v2",
              "E211, rgm211's 12 points (aifoundry3 card 0)": "MM1-v2", "E212 a2c0-S3, re-run (aifoundry2 card 0, its governor)": "MM1-v3",
              "E213 arm A (aifoundry3 card 0, 600 MHz)": "MM1-v3", "E213 arm B (aifoundry1 card 1, 600 MHz)": "MM1-v3",
              "E215 arm A, families P, C, R (aifoundry3 card 0, 600 MHz)": "MM1-v3.1", "E215 arm B, families P, C, R (aifoundry1 card 1, 600 MHz)": "MM1-v3.1"}
    sel_n = [r for r in rows if newest.get(r[0]) == r[1]]
    sel_f = [r for r in rows if r[1] in ("F1", "F1@800") and r[0] in newest]
    return sel_n, sel_f


def range_entry(G, key, sel, q, phrase):
    cs = [(r[0], r[1], r[3][q]) for r in sel if r[3].get(q)]
    vals = [c["rms"] for _, _, c in cs]
    srcs, ins = [], []
    for _, _, c in cs:
        if c["src"][0] == "json":
            srcs.append({"kind": "json", "pin": c["src"][1], "pointer": c["src"][2] + ["rms_pct"]})
        else:
            fn, args, inputs = desk_src(c)
            srcs.append({"kind": "desk", "fn": fn, "args": dict(args, stat="rms")})
            ins += [i for i in inputs if i not in ins]
    pins = sorted({s["pin"] for s in srcs if s["kind"] == "json"}) + ins
    G.desk(key + ".min", min(vals), "{:.1f}", phrase, "range_min", {"cells": srcs}, pins, "the lowest of the cells named, rms %")
    G.desk(key + ".max", max(vals), "{:.1f}", phrase, "range_max", {"cells": srcs}, pins, "the highest of the cells named, rms %")


# ------------------------------------------------------------------------------------------------ E215's tables
V215 = r"(MM1-v3\.1 BETTER|MM1-v3 BETTER|NOT DECIDED|TOO FEW|NO DATA)"


def e215_blocks(txt):
    """the frozen scorer's printed lines (normalised) by block: 'A registered', 'A posthoc', 'B registered', 'B posthoc', 'pooled
    registered', 'pooled posthoc' -> the block's text"""
    out, cur = {}, None
    for ln in txt.splitlines():
        m = re.match(r"ARM ([AB]) (REGISTERED|POSTHOC) ", ln)
        p = re.match(r"POOLED (REGISTERED|POSTHOC):", ln)
        if m:
            cur = m.group(1) + " " + m.group(2).lower()
            out[cur] = norm(ln)
        elif p:
            cur = None
            out["pooled " + p.group(1).lower()] = norm(ln)
        elif cur and ln.startswith("  "):
            out[cur] += "\n" + norm(ln)
        else:
            cur = None
    return out


def build_e215(G, R, c215, rules):
    """E215's verdict table (the frozen scorer's printed words), its two footings, the REPORTED comparisons and the gemmLnc points; every
    cell registered with its source. Returns the generated rows by table."""
    T, D = G.text, G.desk
    tabs = {"verdicts": [], "footings": [], "reported": [], "lnc": []}
    RA = "e215A_readme"
    T("s45.d.hold", "lnc_note", "E215's two arms were held from 09:59:39 PST and released at about 11:55 PST", "09:59:39", "Both arms were held from 09:59:39 PST")
    T("s45.d.n90", "seal_e215", "for all 90 of E215's points on both arms", "90", "session's seal of all 90 points")
    p = "(sealed at 10:24:43 PST) was registered (committed 11:43:33 PST)"
    T("s45.d.seal", RA, "posted on the round's coordination thread at 10:24:43 PST Thu 19 Nov 2026", "10:24:43", p)
    T("s45.d.sreg", RA, "by `18398ed2` (committed 11:43:33 PST)", "11:43:33", p)
    p = ("first card command at 12:05:55 PST (after the card's configuration read at 12:05:24), 119 of 119 runs in 52.76 card-minutes "
         "(planned 49.4), board peak 59.34 W in the gemmLnc smoke, every sample at 600 MHz (31,606 / 31,606), and 60 of 60 scored points "
         "never run on any card")
    T("s45.d.fcc", RA, "session's first card command at 12:05:55", "12:05:55", p)
    T("s45.d.cfg", RA, "step 7's config read at 12:05:24, reported apart", "12:05:24", p)  # report-v2-fix (L8)
    T("s45.d.r0", RA, "RAN FULL (the opening smoke, the stop-path test, 119 of 119 runs and the gemmLnc smoke)", "119", p)
    T("s45.d.r1", RA, "RAN FULL (the opening smoke, the stop-path test, 119 of 119 runs and the gemmLnc smoke)", "119", p)
    T("s45.d.cm", RA, "52.76 (planned 49.4", "52.76", p)
    T("s45.d.pl", RA, "52.76 (planned 49.4", "49.4", p)
    T("s45.d.pk", RA, "the smoke s03 at place 112 (ran, its board peak 59.34 W)", "59.34", p)
    T("s45.d.mhz", RA, "telemetry samples, and those at 600 MHz | 31,606 / 31,606", "600", p)
    T("s45.d.smp", RA, "telemetry samples, and those at 600 MHz | 31,606 / 31,606", "31,606 / 31,606", p)
    T("s45.d.nr0", RA, "60 of 60 scored points never ran on any card", "60", p)
    T("s45.d.nr1", RA, "60 of 60 scored points never ran on any card", "60", p)
    cols = [(a, g, "e215%s_txt" % a) for a in ARMS215 for g in ("registered", "posthoc")]
    blk = {}
    for arm, g, pin in cols:
        b = e215_blocks(R.text(pin))
        blk[(arm, g)] = (b[arm + " " + g], pin)
    pb = e215_blocks(R.text("e215P_txt")) if "e215P_txt" in PINS else None
    tail = " | - | - |" if pb else " |"
    names = [("R0, S6, the checks and the clock", None), ("T1, wall cycles an op, per case", "T1"), ("T2, the counter's mean, per case", "T2"),
             ("T3, seconds a GEMM, per case", "T3"), ("E1, J over idle given the measured seconds", "E1"),
             ("E2, J over idle with the seconds forecast", "E2"), ("E3, J at rest given the seconds", "E3"),
             ("E4, J at rest with the seconds forecast", "E4")]
    for label, rule in names:
        cells, regs = [], []
        for arm, g, pin in cols:
            text, _ = blk[(arm, g)]
            head = text.split("\n")[0]
            if rule is None:
                m0 = re.search(r"R0 (PASS|FAIL|NO DATA); S6 (PASS|FAIL|NO DATA)", head)
                cells.append(f"{m0.group(1)}, {m0.group(2)}")
                regs.append((pin, head[:head.index(m0.group(0)) + len(m0.group(0))], [m0.group(1), m0.group(2)]))
            else:
                m = re.search(re.escape(rule) + r" (PASS|FAIL|TOO FEW|NO DATA)(?: (\d+/\d+))?", head)
                cells.append(m.group(1) + (" " + m.group(2) if m.group(2) else ""))
                regs.append((pin, head[:head.index(m.group(0)) + len(m.group(0))], [cells[-1]]))
        row = f"| {label} | " + " | ".join(cells) + tail
        for i, (pin, lit, toks) in enumerate(regs):
            for j, tk in enumerate(toks):
                T(f"s45.v.{rule or 'R0S6'}.{i}.{j}", pin, lit, tk, row, "the frozen scorer's printed words")
        tabs["verdicts"].append(row)
    hn = [("H1", "wall cycles, head to head"), ("H2", "the counter's mean"), ("H3", "seconds"), ("H4", "J over idle given the seconds"),
          ("H5", "J over idle with the seconds forecast")]
    for h, label in hn:
        cells, regs = [], []
        for arm, g, pin in cols:
            text, _ = blk[(arm, g)]
            m = re.search(g + " " + h + " " + V215 + r"(?: \(v3\.1 (\d+) / v3 (\d+) / ties (\d+);)?", text)
            v = m.group(1)
            if m.group(2) is not None:
                cells.append(f"{v} {m.group(2)}/{m.group(3)}/{m.group(4)}")
                regs.append((pin, m.group(0), [v, m.group(2), m.group(3), m.group(4)]))
            else:
                cells.append(v)
                regs.append((pin, m.group(0), [v]))
        for g in (("registered", "posthoc") if pb else ()):
            line = pb["pooled " + g]
            m = re.search("HP" + h[1] + " " + V215 + r"(?: \((\d+)/(\d+)/(\d+), p)?", line)
            lit = line[:line.index(m.group(0)) + len(m.group(0))]
            if m.group(2) is not None:
                cells.append(f"{m.group(1)} {m.group(2)}/{m.group(3)}/{m.group(4)}")
                regs.append(("e215P_txt", lit, [m.group(1), m.group(2), m.group(3), m.group(4)]))
            else:
                cells.append(m.group(1))
                regs.append(("e215P_txt", lit, [m.group(1)]))
        row = f"| {label} | " + " | ".join(cells) + " |"
        for i, (pin, lit, toks) in enumerate(regs):
            for j, tk in enumerate(toks):
                T(f"s45.v.{h}.{i}.{j}", pin, lit, tk, row, "the frozen scorer's printed words")
        tabs["verdicts"].append(row)
    # the two footings, both arms, the registered group
    for label, q in (("wall cycles an op, per case", "wall"), ("the counter's mean, per case", "mean"),
                     ("J over idle given the seconds, 3 W and above", "Jg"), ("J with the card at rest given the seconds", "Jr")):
        vals = []
        for conv in ("mf", "fm"):
            for m in ("v31", "v3"):
                s = e215_stat(c215, PA215, "registered", m, q, conv)
                vals.append((conv, m, s))
        row = f"| {label} | " + " | ".join(f"{s['rms']:.2f}% ({sgn(s['bias'], 2)}; n {s['n']})" for _, _, s in vals) + " |"
        for conv, m, s in vals:
            for st, fmt in (("rms", "{:.2f}"), ("bias", "{:+.2f}"), ("n", "{:d}")):
                D(f"s45.f.{q}.{conv}.{m}.{st}", s[st] if st != "n" else s["n"], fmt, row, "e215",
                  {"arm": PA215, "group": "registered", "model": m, "q": q, "conv": conv, "stat": st}, E215_INPUTS,
                  "E215 %s, registered, desk (%s)" % (WHERE215, "measured / forecast - 1" if conv == "mf" else "forecast / measured - 1"))
        tabs["footings"].append(row)
    if "e215P_note" in PINS:
        p = ("they equal the scores lane's own pooled figures: MM1-v3.1 7.01% and MM1-v3 6.78% in wall cycles, 11.50% and 11.57% in J over idle "
             "given t")
        l31 = "| MM1-v3.1 | 7.01% (50) | 6.44% | 7.00% | 11.50% (50) | 11.49% | 4.55% (50) | 6.28% | - |"
        l3 = "| MM1-v3 | 6.78% (50) | 6.06% | 6.77% | 11.57% (50) | 11.55% | 4.57% (50) | 6.23% | - |"
        T("s45.fn.0", "e215P_note", l31, "7.01", p)
        T("s45.fn.1", "e215P_note", l3, "6.78", p)
        T("s45.fn.2", "e215P_note", l31, "11.50", p)
        T("s45.fn.3", "e215P_note", l3, "11.57", p)
    # REPORTED beside: 'v3.1 with T7', the two candidate terms, MM1-v2, at the cases or points each changes
    nl = len(e215_rows(c215, PA215, "registered", "lnc", "Jg", "lnc"))
    rep = [("v3.1 with T7", "t7", PA215, "registered", "wall", None, "every registered case"),
           ("v3.1 with T7", "t7", PA215, "posthoc", "wall", "L", "family L, " + WHERE215),
           ("v3.1 + contention", "lay", PA215, "posthoc", "wall", "L", "family L, " + WHERE215),
           ("v3.1 + G1, frozen beside it", "lg1", PA215, "posthoc", "wall", "L", "family L, " + WHERE215),
           ("v3.1 + N1+N2, its verifier's shire-count control", "cnt", PA215, "posthoc", "wall", "L", "family L, " + WHERE215),
           ("v3.1 + gemmLnc term", "lnc", PA215, "registered", "Jg", "lnc", "the %s gemmLnc points, %s" % ({4: "four", 5: "five"}.get(nl, str(nl)), WHERE215)),
           ("MM1-v2", "v2", PA215, "registered", "wall", None, "every registered case"),
           # report-v2-fix (finding M2): the two frozen MM1s at family L, beside the forms added to MM1-v3.1
           ("MM1-v3", "v3", PA215, "posthoc", "wall", "L", "family L, " + WHERE215),
           ("MM1-v2", "v2", PA215, "posthoc", "wall", "L", "family L, " + WHERE215)]
    for label, m, arm, g, q, only, where in rep:
        s = e215_stat(c215, arm, g, m, q, "fm", only)
        if s is None:
            continue
        b = e215_stat(c215, arm, g, "v31", q, "fm", only)
        cl = e215_closer(c215, rules, arm, g, m, q, only)
        qn = {"wall": "wall cycles", "Jg": "J over idle given t"}[q]
        row = (f"| {label} | {where}, {qn} ({s['n']}) | {s['rms']:.2f}% ({sgn(s['bias'], 2)}) | {b['rms']:.2f}% ({sgn(b['bias'], 2)}) | "
               f"{cl['closer']} / {cl['farther']} / {cl['ties']} (p {cl['p']:.2g}) |")
        args = {"arm": arm, "group": g, "q": q, "conv": "fm"}
        if only:
            args["only"] = only
        k = f"s45.r.{m}.{g}.{q}"
        D(k + ".n", s["n"], "{:d}", row, "e215", dict(args, model=m, stat="n"), E215_INPUTS, "cases or points, desk")
        D(k + ".rms", s["rms"], "{:.2f}", row, "e215", dict(args, model=m, stat="rms"), E215_INPUTS, "REPORTED, rms %, desk")
        D(k + ".bias", s["bias"], "{:+.2f}", row, "e215", dict(args, model=m, stat="bias"), E215_INPUTS, "REPORTED, bias %, desk")
        D(k + ".b.rms", b["rms"], "{:.2f}", row, "e215", dict(args, model="v31", stat="rms"), E215_INPUTS, "MM1-v3.1 at the same, rms %, desk")
        D(k + ".b.bias", b["bias"], "{:+.2f}", row, "e215", dict(args, model="v31", stat="bias"), E215_INPUTS, "MM1-v3.1 at the same, bias %, desk")
        for st in ("closer", "farther", "ties"):
            D(f"{k}.{st}", cl[st], "{:d}", row, "e215c", dict(args, model=m, stat=st), E215_INPUTS, "against MM1-v3.1, desk")
        D(k + ".p", cl["p"], "{:.2g}", row, "e215c", dict(args, model=m, stat="p"), E215_INPUTS, "the exact two-sided sign test, REPORTED, desk")
        tabs["reported"].append(row)
    # the gemmLnc points one by one: measured J over idle / the forecast given the measured seconds
    M = {a: R.json("e215%s_scores" % a)["arms"][a]["measured"] for a in ARMS215}
    for p in sorted(r["key"].split(":")[1] for a in ARMS215 for r in c215[a].get("registered", {}).get("Jg", {}).get("lnc", [])):
        a = p[0].upper()
        v = M[a][p]
        r31 = [r for r in c215[a]["registered"]["Jg"]["v31"] if r["key"] == a + ":" + p][0]
        rl = [r for r in c215[a]["registered"]["Jg"]["lnc"] if r["key"] == a + ":" + p][0]
        shape = v["case"].split("|")[1]
        row = f"| {p} | {shape} {v['format']} | {1 + r31['mf']:.2f} | {1 + rl['mf']:.2f} |"
        D(f"s45.lnc.{p}.v31", 1 + r31["mf"], "{:.2f}", row, "e215pt", {"point": p, "group": "registered", "model": "v31"}, E215_INPUTS,
          "measured / MM1-v3.1's J over idle given t, desk")
        D(f"s45.lnc.{p}.lnc", 1 + rl["mf"], "{:.2f}", row, "e215pt", {"point": p, "group": "registered", "model": "lnc"}, E215_INPUTS,
          "measured / the term's J over idle given t, desk")
        tabs["lnc"].append(row)
        tabs.setdefault("lnc_fig", []).append({"point": p, "label": shape.replace("gemmLnc", ""), "v31": 1 + r31["mf"], "lnc": 1 + rl["mf"]})
    if "B" in ARMS215:
        RB, tB, reg = "e215B_readme", "e215B_txt", "e215_reg"
        p = "its first booking (12:00:51 PST) stopped at its kit's rest rule before any card command"
        T("s45.b.b1", RB, "`book.sh take aifoundry1 card-e215b` BOOKED at 12:00:51 PST", "12:00:51", p)
        p = "one firmware read on the card's present boot, EQUAL at 13:41:24 PST"
        T("s45.b.fw", RB, "at **2026-11-19 13:41:24 PST**, rc 0, verdict EQUAL", "13:41:24", p)
        p = ("first card command at 13:42:22 PST, 71 of 71 runs in 28.55 card-minutes (planned 28.0), board peak 66 W, every sample at 600 MHz "
             "(17,106 / 17,106)")
        T("s45.b.fcc", RB, "The session's first card command at 13:42:22", "13:42:22", p)
        lit = "RAN FULL (the opening smoke, the stop-path test, 71 of 71 runs and the gemmLnc smoke)"
        T("s45.b.r0", RB, lit, "71", p)
        T("s45.b.r1", RB, lit, "71", p)
        T("s45.b.cm", RB, "28.55 (planned 28.0", "28.55", p)
        T("s45.b.pl", RB, "28.55 (planned 28.0", "28.0", p)
        T("s45.b.pk", RB, "66 W at 14:09:57", "66", p)
        T("s45.b.mhz", RB, "telemetry samples, and those at 600 MHz | 17,106 / 17,106", "600", p)
        T("s45.b.smp", RB, "telemetry samples, and those at 600 MHz | 17,106 / 17,106", "17,106 / 17,106", p)
        p = "Its never-run scan named 26 of its 30 points as run on card 1 after the freeze line"
        a0, a1 = "ran after it (REPORTED, kept): ", "\". Step 7"
        tb = norm(R.text(RB))
        seg = tb[tb.index(a0) + len(a0):tb.index(a1, tb.index(a0))]
        D("s45.b.nr1", len(re.findall(r"\bb0[0-9][0-9]\b", seg)), "{:d}", p, "count_in_text", {"pin": "e215B_readme", "between": [a0, a1],
          "pattern": r"\bb0[0-9][0-9]\b"}, ["e215B_readme"], "points the scan listed as run after the freeze line, desk count")
        T("s45.b.nr0", RB, "4 of 30 scored points never ran on aifoundry1 card 1", "30", p)
        p = "registered at 13:14:57 PST and not yet run, plans the same configurations: all 44 of its hits are in a lab lane's copy of E217's registration"
        T("s45.b.e217t", "e215B_note1", "its registration was committed as `78b690b5` at 13:14:57 PST", "13:14:57", p)
        T("s45.b.e217", RB, '{"data-e217": 44}', "44", p)
        # arm B's verdicts
        p = "MM1-v3.1 failed its time bands there too (15 of 18 cases within 10%) and E4 (16 of 18), and passed E1 to E3 (17 of 18)"
        lit = "ARM B REGISTERED (P, C, R): R0 PASS; S6 PASS; T1 FAIL 15/18"
        T("s45.vb.t0", tB, lit, "15", p)
        T("s45.vb.t1", tB, lit, "18", p)
        T("s45.vb.t2", reg, "| T1 | cycles an op, the wall, per case | 10% |", "10", p)
        T("s45.vb.e4a", tB, "E4 FAIL 16/18", "16", p)
        T("s45.vb.e4b", tB, "E4 FAIL 16/18", "18", p)
        T("s45.vb.e1a", tB, "E1 PASS 17/18", "17", p)
        T("s45.vb.e1b", tB, "E1 PASS 17/18", "18", p)
        p = "its one gemmLnc point, b013, drew 1.52 times its forecast"
        D("s45.vb.l", 1 + e215_one(c215, "B", "registered", "v31", "Jg", "mf", "b013") / 100.0, "{:.2f}", p, "e215pt",
          {"point": "b013", "group": "registered", "model": "v31"}, E215_INPUTS, "measured / MM1-v3.1's J over idle given t, desk")
        p = "on both cards the card ran gemmL2x1x7 (fp32 and int8) 12.7% to 14.9% slower than forecast"
        D("s45.vb.r0", e215_one(c215, "B", "registered", "v31", "wall", "mf", "rgm136 gemmL|gemmL2x1x7|fp32|0xffffffff"), "{:.1f}", p, "e215one",
          {"arm": "B", "group": "registered", "model": "v31", "q": "wall", "conv": "mf", "key": "rgm136 gemmL|gemmL2x1x7|fp32|0xffffffff"},
          E215_INPUTS, "one E215 case, %, desk (measured / forecast - 1)")
        D("s45.vb.r1", e215_one(c215, "A", "registered", "v31", "wall", "mf", "rgm136 gemmL|gemmL2x1x7|int8|0xffffffff"), "{:.1f}", p, "e215one",
          {"arm": "A", "group": "registered", "model": "v31", "q": "wall", "conv": "mf", "key": "rgm136 gemmL|gemmL2x1x7|int8|0xffffffff"},
          E215_INPUTS, "one E215 case, %, desk (measured / forecast - 1)")
        p = "(MM1-v3.1 closer at 5 cases, MM1-v3 at 7, with 6 ties)"
        lit = "registered H1 NOT DECIDED (v3.1 5 / v3 7 / ties 6"
        for i, tok in enumerate(("5", "7", "6")):
            T("s45.vb.h%d" % i, tB, lit, tok, p)
        p = "its post hoc time rules are TOO FEW by construction (2 of 8 cases within the band)"
        T("s45.vb.p0", tB, "ARM B POSTHOC (L, S): R0 PASS; S6 PASS; T1 TOO FEW 2/8", "2", p)
        T("s45.vb.p1", tB, "ARM B POSTHOC (L, S): R0 PASS; S6 PASS; T1 TOO FEW 2/8", "8", p)
        base = ["arms", "B", "readings_REPORTED"]
        p = "its four 28-shire masks of gemmL1x15x4 spread by 0.47% and all ran 10.8% to 11.2% faster than MM1-v3.1 forecast, past the band"
        G.json("s45.rdb.l28", "e215B_scores", base + ["layout_sets", 0, "spread"], "{:.2f}", p, "measured spread, REPORTED", scale=100.0)
        for k, ck in (("0", "rgm136 gemmL|gemmL1x15x4|fp32|0xffff0fff"), ("1", "rgm136 gemmL|gemmL1x15x4|fp32|0xfff0ffff")):
            D("s45.rdb.f28" + k, -e215_one(c215, "B", "posthoc", "v31", "wall", "mf", ck), "{:.1f}", p, "e215one_neg",
              {"arm": "B", "group": "posthoc", "model": "v31", "q": "wall", "conv": "mf", "key": ck}, E215_INPUTS, "how far under MM1-v3.1's forecast, %, desk")
        # report-v2-fix (finding M7): arm B's switch-route reading beside arm A's
        p = ("the switch route missed most at int8 real:blind4 (0.886 measured against 0.971) and fp32 blind3 (0.882 against 0.948), where "
             "MM1-v3.1's J over idle given t read +9.1% and +5.6%")
        swB = R.json("e215B_scores")["arms"]["B"]["readings_REPORTED"]["switch_route"]
        kinds = [c["kind"] for c in swB]
        for k, pt in (("0", "b030"), ("1", "b027")):
            i = kinds.index(pt)
            G.json("s45.rdb.sw%sm" % k, "e215B_scores", base + ["switch_route", i, "measured_W_ratio"], "{:.3f}", p, "measured ratio, REPORTED")
            G.json("s45.rdb.sw%sf" % k, "e215B_scores", base + ["switch_route", i, "models_W_ratio", "MM1-v3.1"], "{:.3f}", p,
                   "MM1-v3.1's ratio, REPORTED")
        for k, pt in (("0", "b030"), ("1", "b027")):
            D("s45.rdb.sw%se" % k, e215_one(c215, "B", "posthoc", "v31", "Jg", "fm", pt), "{:+.1f}", p, "e215one",
              {"arm": "B", "group": "posthoc", "model": "v31", "q": "Jg", "conv": "fm", "key": pt}, E215_INPUTS,
              "one E215 point, %, desk (forecast / measured - 1)")
        p = "the ties read 4.5% under the reference"
        D("s45.rdb.off", -100 * R.json("e215B_scores")["arms"]["B"]["day_offset_REPORTED"]["offset_W"], "{:.1f}", p, "e215off",
          {"arm": "B"}, ["e215B_scores"], "minus the day offset, %, REPORTED")
    if "e215P_txt" in PINS:
        tP = "e215P_txt"
        line_r = [l for l in R.text(tP).splitlines() if l.startswith("POOLED REGISTERED")][0]
        line_p = [l for l in R.text(tP).splitlines() if l.startswith("POOLED POSTHOC")][0]
        p = "(MM1-v3.1 closer at 13 cases, MM1-v3 at 19, with 18 ties)"
        lit = line_r[:line_r.index("HP1 ")] + "HP1 NOT DECIDED (13/19/18"
        for i, tok in enumerate(("13", "19", "18")):
            T("s45.vP.h%d" % i, tP, lit, tok, p)
        p = "MM1-v3 is BETTER on HP1 to HP3 (closer at 17 cases against 3)"
        lit = line_p[:line_p.index("HP1 ")] + "HP1 MM1-v3 BETTER (3/17/8"
        m = re.search(r"HP1 MM1-v3 BETTER \((\d+)/(\d+)/(\d+)", line_p)
        T("s45.vP.p1", tP, lit, m.group(2), p)
        T("s45.vP.p2", tP, lit, m.group(1), p)
    if "A" in ARMS215:
        tA, reg = "e215A_txt", "e215_reg"

        def ONE(key, group, q, ck, fmt, phrase, model="v31", conv="mf"):
            v = e215_one(c215, "A", group, model, q, conv, ck)
            D(key, v, fmt, phrase, "e215one", {"arm": "A", "group": group, "model": model, "q": q, "conv": conv, "key": ck}, E215_INPUTS,
              "one E215 case or point, %%, desk (%s)" % ("measured / forecast - 1" if conv == "mf" else "forecast / measured - 1"))
        # the summary (both arms)
        tB = "e215B_txt"
        p = "(27 of 32 and 15 of 18 cases within 10%, against 90% needed)"
        T("os.e215.t0", tA, "ARM A REGISTERED (P, C, R): R0 PASS; S6 PASS; T1 FAIL 27/32", "27", p)
        T("os.e215.t1", tA, "ARM A REGISTERED (P, C, R): R0 PASS; S6 PASS; T1 FAIL 27/32", "32", p)
        T("os.e215.t4", tB, "ARM B REGISTERED (P, C, R): R0 PASS; S6 PASS; T1 FAIL 15/18", "15", p)
        T("os.e215.t5", tB, "ARM B REGISTERED (P, C, R): R0 PASS; S6 PASS; T1 FAIL 15/18", "18", p)
        T("os.e215.t2", reg, "| T1 | cycles an op, the wall, per case | 10% |", "10", p)
        T("os.e215.t3", reg, "PASS if at least 90% of its scored cases or points pass", "90", p)
        p = "(aifoundry3 card 0, 119 of 119 runs; aifoundry1 card 1, 71 of 71 runs after a second booking)"
        lit = "RAN FULL (the opening smoke, the stop-path test, 119 of 119 runs and the gemmLnc smoke)"
        T("os.e215.r0", "e215A_readme", lit, "119", p)
        T("os.e215.r1", "e215A_readme", lit, "119", p)
        lit = "RAN FULL (the opening smoke, the stop-path test, 71 of 71 runs and the gemmLnc smoke)"
        T("os.e215.r2", "e215B_readme", lit, "71", p)
        T("os.e215.r3", "e215B_readme", lit, "71", p)
        p = "the gemmLnc term cut that loop's energy miss from 24.53% to 9.18% rms at its five points"
        for k, m in (("v31", "v31"), ("lnc", "lnc")):
            st = e215_stat(c215, PA215, "registered", m, "Jg", "fm", "lnc")
            D("os.e215.l." + k, st["rms"], "{:.2f}", p, "e215", {"arm": PA215, "group": "registered", "model": m, "q": "Jg", "conv": "fm",
              "only": "lnc", "stat": "rms"}, E215_INPUTS, "REPORTED, rms %, desk")
        p = "(10 of E215's layouts ran 10.1% to 16.6% faster than MM1-v3.1 forecast)"
        D("os.e215.lay.n", e215_miss(c215, rules, PA215, "posthoc", "v31", "wall", "T1"), "{:d}", p, "e215miss",
          {"arm": PA215, "group": "posthoc", "model": "v31", "q": "wall", "rule": "T1"}, E215_INPUTS + ["e215_rules"],
          "cases past MM1-v3.1's registered T1 band, desk")
        for k, ck in (("0", "rgm136 gemmL|gemmL1x9x6|fp32|0x2002202"), ("1", "rgm136 gemmL|gemmL2x4x4|fp32|0xee0e00")):
            D("os.e215.lay" + k, -e215_one(c215, "A", "posthoc", "v31", "wall", "mf", ck), "{:.1f}", p, "e215one_neg",
              {"arm": "A", "group": "posthoc", "model": "v31", "q": "wall", "conv": "mf", "key": ck}, E215_INPUTS, "how far under MM1-v3.1's forecast, %, desk")
        p = "(T1 and T3, 27 of 32 cases within 10%, against 90% needed)"
        T("s45.va.t1.0", tA, "ARM A REGISTERED (P, C, R): R0 PASS; S6 PASS; T1 FAIL 27/32", "27", p)
        T("s45.va.t1.1", tA, "ARM A REGISTERED (P, C, R): R0 PASS; S6 PASS; T1 FAIL 27/32", "32", p)
        T("s45.va.t1.2", reg, "| T1 | cycles an op, the wall, per case | 10% |", "10", p)
        T("s45.va.t1.3", reg, "PASS if at least 90% of its scored cases or points pass", "90", p)
        p = ("two gemmLnc cases ran 14.8% and 15.5% under its forecast, and three cases 11.0% to 14.9% over it: two of family R's "
             "retention points (gemmL2x1x7 in fp32 and int8) and one of family C's one-block points (gemmL8x15x1 in int8)")
        D("s45.va.m0", -e215_one(c215, "A", "registered", "v31", "wall", "mf", "rgm136 gemmLnc|gemmLnc1x12x4|fp32|0xffffffff"), "{:.1f}", p,
          "e215one_neg", {"arm": "A", "group": "registered", "model": "v31", "q": "wall", "conv": "mf",
                          "key": "rgm136 gemmLnc|gemmLnc1x12x4|fp32|0xffffffff"}, E215_INPUTS, "how far under MM1-v3.1's forecast, %, desk")
        D("s45.va.m1", -e215_one(c215, "A", "registered", "v31", "wall", "mf", "rgm136 gemmLnc|gemmLnc1x15x3|fp32|0xffffffff"), "{:.1f}", p,
          "e215one_neg", {"arm": "A", "group": "registered", "model": "v31", "q": "wall", "conv": "mf",
                          "key": "rgm136 gemmLnc|gemmLnc1x15x3|fp32|0xffffffff"}, E215_INPUTS, "how far under MM1-v3.1's forecast, %, desk")
        ONE("s45.va.m2", "registered", "wall", "rgm136 gemmL|gemmL8x15x1|int8|0xffffffff", "{:.1f}", p)
        ONE("s45.va.m3", "registered", "wall", "rgm136 gemmL|gemmL2x1x7|int8|0xffffffff", "{:.1f}", p)
        p = "the counter's mean passed (T2, 30 of 32 within 13%)"
        T("s45.va.t2.0", tA, "ARM A REGISTERED (P, C, R): R0 PASS; S6 PASS; T1 FAIL 27/32; T2 PASS 30/32", "30", p)
        T("s45.va.t2.1", tA, "ARM A REGISTERED (P, C, R): R0 PASS; S6 PASS; T1 FAIL 27/32; T2 PASS 30/32", "32", p)
        T("s45.va.t2.2", reg, "| T2 | cycles an op, the counter's mean, per case | 13% |", "13", p)
        p = "E1 to E3 failed at its four gemmLnc points alone (28 of 32; E2 by a hair, a026 at 13.02% over its forecast against a 13% band)"
        T("s45.va.e1", tA, "E1 FAIL 28/32", "28", p)
        T("s45.va.e1b", tA, "E1 FAIL 28/32", "32", p)
        T("s45.va.e2n", reg, "| **E2** | J over idle with the seconds forecast, per point (watts under 3 W) | **13%** |", "2", p)
        ONE("s45.va.e2v", "registered", "Jf", "a026", "{:.2f}", p)
        T("s45.va.e2b", reg, "| **E2** | J over idle with the seconds forecast, per point (watts under 3 W) | **13%** |", "13", p)
        p = ("they drew 1.14 to 1.39 times its J over idle given the measured seconds (figure 5), and without them its J over idle given t read "
             "3.75% (forecast / measured - 1; 3.54% on the scorer's footing; post hoc)")
        D("s45.va.l0", 1 + e215_one(c215, "A", "registered", "v31", "Jg", "mf", "a026") / 100.0, "{:.2f}", p, "e215pt",
          {"point": "a026", "group": "registered", "model": "v31"}, E215_INPUTS, "measured / MM1-v3.1's J over idle given t, desk")
        D("s45.va.l1", 1 + e215_one(c215, "A", "registered", "v31", "Jg", "mf", "a031") / 100.0, "{:.2f}", p, "e215pt",
          {"point": "a031", "group": "registered", "model": "v31"}, E215_INPUTS, "measured / MM1-v3.1's J over idle given t, desk")
        sn = e215_stat(c215, "A", "registered", "v31", "Jg", "fm", "nolnc")
        D("s45.va.nolnc", sn["rms"], "{:.2f}", p, "e215", {"arm": "A", "group": "registered", "model": "v31", "q": "Jg", "conv": "fm",
          "only": "nolnc", "stat": "rms"}, E215_INPUTS, "post hoc, without the gemmLnc points, rms %, desk")
        # report-v2-fix (finding L3): the same on the scorer's footing
        snm = e215_stat(c215, "A", "registered", "v31", "Jg", "mf", "nolnc")
        D("s45.va.nolnc.mf", snm["rms"], "{:.2f}", p, "e215", {"arm": "A", "group": "registered", "model": "v31", "q": "Jg", "conv": "mf",
          "only": "nolnc", "stat": "rms"}, E215_INPUTS, "post hoc, without the gemmLnc points, rms %, desk (measured / forecast - 1)")
        # report-v2-fix (finding M1): E4's own misses, from the frozen scorer's cells
        p = ("E4 (J at rest with the seconds forecast) failed at 28 of 32 too, but at a031 and a032 and at family R's two gemmL2x1x7 retention "
             "points, a043 and a044 (+9.62% and +12.91% against a 9% band); a024 and a026 passed it")
        T("s45.va.e4.0", tA, "E4 FAIL 28/32", "28", p)
        T("s45.va.e4.1", tA, "E4 FAIL 28/32", "32", p)
        cellsA = R.json("e215A_scores")["arms"]["A"]["cells"]["registered"]["E4"]
        for k, pt in (("2", "a043"), ("3", "a044")):
            i = [c["point"] for c in cellsA].index(pt)
            G.json("s45.va.e4." + k, "e215A_scores", ["arms", "A", "cells", "registered", "E4", i, "err"], "{:+.2f}", p,
                   "the frozen scorer's E4 error at %s, measured / forecast - 1, %%" % pt, scale=100.0)
        T("s45.va.e4.4", reg, "| **E4** | J with the card at rest with the seconds forecast, per point | **9%** |", "9", p)
        if "B" in ARMS215:
            p = "E4's two misses are b013 and b022 (gemmL2x1x7 in int8, +12.78% against a 10% band)"
            cellsB = R.json("e215B_scores")["arms"]["B"]["cells"]["registered"]["E4"]
            i = [c["point"] for c in cellsB].index("b022")
            G.json("s45.vb.e4.0", "e215B_scores", ["arms", "B", "cells", "registered", "E4", i, "err"], "{:+.2f}", p,
                   "the frozen scorer's E4 error at b022, measured / forecast - 1, %", scale=100.0)
            T("s45.vb.e4.1", reg, "| **E4** | J with the card at rest with the seconds forecast, per point | **10%** | 4.47% | 4.63%", "10", p)
        p = "(MM1-v3.1 closer at 8 cases, MM1-v3 at 12, with 12 ties)"
        lit = "registered H1 NOT DECIDED (v3.1 8 / v3 12 / ties 12"
        for i, tok in enumerate(("8", "12", "12")):
            T("s45.va.h%d" % i, tA, lit, tok, p)
        p = "failed its time bands (16 of 20) and E4"
        T("s45.vp.t1.0", tA, "ARM A POSTHOC (L, S): R0 PASS; S6 PASS; T1 FAIL 16/20", "16", p)
        T("s45.vp.t1.1", tA, "ARM A POSTHOC (L, S): R0 PASS; S6 PASS; T1 FAIL 16/20", "20", p)
        p = "(closer at 12 cases against 2)"
        T("s45.vp.h0", tA, "posthoc H1 MM1-v3 BETTER (v3.1 2 / v3 12", "12", p)
        T("s45.vp.h1", tA, "posthoc H1 MM1-v3 BETTER (v3.1 2 / v3 12", "2", p)
        p = "its four time misses are sparse masks the card ran 10.1% to 16.6% faster than MM1-v3.1 forecast"
        D("s45.vp.m0", -e215_one(c215, "A", "posthoc", "v31", "wall", "mf", "rgm136 gemmL|gemmL1x9x6|fp32|0x2002202"), "{:.1f}", p,
          "e215one_neg", {"arm": "A", "group": "posthoc", "model": "v31", "q": "wall", "conv": "mf", "key": "rgm136 gemmL|gemmL1x9x6|fp32|0x2002202"},
          E215_INPUTS, "how far under MM1-v3.1's forecast, %, desk")
        D("s45.vp.m1", -e215_one(c215, "A", "posthoc", "v31", "wall", "mf", "rgm136 gemmL|gemmL2x4x4|fp32|0xee0e00"), "{:.1f}", p,
          "e215one_neg", {"arm": "A", "group": "posthoc", "model": "v31", "q": "wall", "conv": "mf", "key": "rgm136 gemmL|gemmL2x4x4|fp32|0xee0e00"},
          E215_INPUTS, "how far under MM1-v3.1's forecast, %, desk")
        # section 7 (both arms)
        p = "(the card drew 1.14 to 1.52 times its J over idle given the seconds)"
        for k, pt in (("0", "a026"), ("1", "b013")):
            D("s7a.l" + k, 1 + e215_one(c215, pt[0].upper(), "registered", "v31", "Jg", "mf", pt) / 100.0, "{:.2f}", p, "e215pt",
              {"point": pt, "group": "registered", "model": "v31"}, E215_INPUTS, "measured / MM1-v3.1's J over idle given t, desk")
        p = "overshot at arm A's four (0.88 to 0.95 times its forecast) while reading 1.01 at arm B's one"
        for k, pt in (("0", "a032"), ("1", "a024"), ("2", "b013")):
            D("s7a.t" + k, 1 + e215_one(c215, pt[0].upper(), "registered", "lnc", "Jg", "mf", pt) / 100.0, "{:.2f}", p, "e215pt",
              {"point": pt, "group": "registered", "model": "lnc"}, E215_INPUTS, "measured / the term's J over idle given t, desk")
        p = "at NB 12 and 15 the card ran gemmLnc 14.8% and 15.5% faster than MM1-v3.1 forecast"
        T("s7a.nb0", "lnc_note", "so a024 (NB 15) and a026 (NB 12) extrapolate", "12", p)
        T("s7a.nb1", "lnc_note", "so a024 (NB 15) and a026 (NB 12) extrapolate", "15", p)
        for k, ck in (("0", "rgm136 gemmLnc|gemmLnc1x12x4|fp32|0xffffffff"), ("1", "rgm136 gemmLnc|gemmLnc1x15x3|fp32|0xffffffff")):
            D("s7a.tm" + k, -e215_one(c215, "A", "registered", "v31", "wall", "mf", ck), "{:.1f}", p, "e215one_neg",
              {"arm": "A", "group": "registered", "model": "v31", "q": "wall", "conv": "mf", "key": ck}, E215_INPUTS, "how far under MM1-v3.1's forecast, %, desk")
        p = "slow by 8.52% on average (this report's footing), 10 of them past its band (the card 10.1% to 16.6% faster)"
        sl = e215_stat(c215, PA215, "posthoc", "v31", "wall", "fm", "L")
        D("s7a.lb", sl["bias"], "{:.2f}", p, "e215", {"arm": PA215, "group": "posthoc", "model": "v31", "q": "wall", "conv": "fm", "only": "L",
          "stat": "bias"}, E215_INPUTS, "the mean of forecast / measured - 1 at family L, %, desk")
        D("s7a.ln", e215_miss(c215, rules, PA215, "posthoc", "v31", "wall", "T1"), "{:d}", p, "e215miss",
          {"arm": PA215, "group": "posthoc", "model": "v31", "q": "wall", "rule": "T1"}, E215_INPUTS + ["e215_rules"],
          "cases past MM1-v3.1's registered T1 band, desk")
        for k, ck in (("0", "rgm136 gemmL|gemmL1x9x6|fp32|0x2002202"), ("1", "rgm136 gemmL|gemmL2x4x4|fp32|0xee0e00")):
            D("s7a.lm" + k, -e215_one(c215, "A", "posthoc", "v31", "wall", "mf", ck), "{:.1f}", p, "e215one_neg",
              {"arm": "A", "group": "posthoc", "model": "v31", "q": "wall", "conv": "mf", "key": ck}, E215_INPUTS, "how far under MM1-v3.1's forecast, %, desk")
        # report-v2-fix (finding M4): the retention miss as its own item, and the one-K-block item with its own two points only
        p = ("gemmL2x1x7 (a 39 MB GEMM, just past the retention's first edge at 37.4 MB) ran 12.7% to 14.9% slower than MM1-v3.1 forecast in "
             "fp32 and int8 on both cards (the scorer's measured / forecast - 1): 4 of the 8 cases past E215's registered T1 band")
        ia = [q["id"] for q in R.json("e215_points")["arms"]["A"]["points"]].index("a043")
        G.json("s7a.rt.mb", "e215_points", ["arms", "A", "points", ia, "bytes_MB", "all"], "{:.0f}", p, "the registration's footprint, MB")
        T("s7a.rt.x1", "v3_readme", "the first edge at x1 = 37.4 MB", "37.4", p)
        for k, arm, ck in (("r0", "B", "rgm136 gemmL|gemmL2x1x7|fp32|0xffffffff"), ("r1", "A", "rgm136 gemmL|gemmL2x1x7|int8|0xffffffff")):
            D("s7a.rt." + k, e215_one(c215, arm, "registered", "v31", "wall", "mf", ck), "{:.1f}", p, "e215one",
              {"arm": arm, "group": "registered", "model": "v31", "q": "wall", "conv": "mf", "key": ck}, E215_INPUTS,
              "one E215 case, %, desk (measured / forecast - 1)")
        for k, only in (("nR", "R"), ("n", None)):
            args = {"arm": PA215, "group": "registered", "model": "v31", "q": "wall", "rule": "T1"}
            if only:
                args["only"] = only
            D("s7a.rt." + k, e215_miss(c215, rules, PA215, "registered", "v31", "wall", "T1", only), "{:d}", p, "e215miss", args,
              E215_INPUTS + ["e215_rules"], "cases past MM1-v3.1's registered T1 band%s, desk" % (" in family " + only if only else ""))
        p = ("On E215, one of family C's one-block points on each card ran 11.0% and 10.9% slower than MM1-v3.1 forecast (gemmL8x15x1 in int8 "
             "on aifoundry3, gemmL16x14x1 in fp32 on card 1), 2 of the 8 cases past the registered T1 band")
        ONE("s7a.k1", "registered", "wall", "rgm136 gemmL|gemmL8x15x1|int8|0xffffffff", "{:.1f}", p)
        D("s7a.k0", e215_one(c215, "B", "registered", "v31", "wall", "mf", "rgm136 gemmL|gemmL16x14x1|fp32|0xffffffff"), "{:.1f}", p, "e215one",
          {"arm": "B", "group": "registered", "model": "v31", "q": "wall", "conv": "mf", "key": "rgm136 gemmL|gemmL16x14x1|fp32|0xffffffff"},
          E215_INPUTS, "one E215 case, %, desk (measured / forecast - 1)")
        for k, only in (("nC", "C"), ("n", None)):
            args = {"arm": PA215, "group": "registered", "model": "v31", "q": "wall", "rule": "T1"}
            if only:
                args["only"] = only
            D("s7a.k." + k, e215_miss(c215, rules, PA215, "registered", "v31", "wall", "T1", only), "{:d}", p, "e215miss", args,
              E215_INPUTS + ["e215_rules"], "cases past MM1-v3.1's registered T1 band%s, desk" % (" in family " + only if only else ""))
        # REPORTED beside, arm A
        p = "the card drew 0.88 to 0.95 times its forecast at all four"
        D("s45.ra.l0", 1 + e215_one(c215, "A", "registered", "lnc", "Jg", "mf", "a032") / 100.0, "{:.2f}", p, "e215pt",
          {"point": "a032", "group": "registered", "model": "lnc"}, E215_INPUTS, "measured / the term's J over idle given t, desk")
        D("s45.ra.l1", 1 + e215_one(c215, "A", "registered", "lnc", "Jg", "mf", "a024") / 100.0, "{:.2f}", p, "e215pt",
          {"point": "a024", "group": "registered", "model": "lnc"}, E215_INPUTS, "measured / the term's J over idle given t, desk")
        T("s45.ra.an", "lnc_note", "F3 may read high on arm A (by about 3 W at a031 and a032)", "3", "had said it might read high there by about 3 W")
        # report-v2-fix (finding M5): when that reading was written and when it was committed
        p = ("That reading was written at 09:59-10:25 PST, before any E215 datum, but it was committed with the term (aaeaa495, 13:14:37 PST) "
             "after arm A's data commit (8355db15, 13:00:32 PST), in a section its note heads \"REPORTED, post hoc; not a freeze\"")
        T("s45.ra.anw", "lnc_note", "**verify-lnc: HOLDS WITH FIXES** (09:59-10:25 PST; desk;", "09:59-10:25", p, "its verifier's own time")
        G.git("s45.ra.anc", "aaeaa495", "13:14:37", p)
        G.git("s45.ra.dat", "8355db15", "13:00:32", p)
        T("s45.ra.anl", "lnc_note", "## For E215's scores (REPORTED, post hoc; not a freeze)", "REPORTED, post hoc; not a freeze", p,
          "the note's own heading, quoted")
        # report-v2-fix (finding M2): the count-only control came closest only among the forms added to MM1-v3.1
        p = ("Of the forms added to MM1-v3.1, the verifier's count-only control N1+N2 came closest (closer than MM1-v3.1 at 18 cases, farther "
             "at 4)")
        aL = {"arm": PA215, "group": "posthoc", "q": "wall", "conv": "fm", "only": "L"}
        cl = e215_closer(c215, rules, PA215, "posthoc", "cnt", "wall", "L")
        for st in ("closer", "farther"):
            D("s45.ra.cnt." + st, cl[st], "{:d}", p, "e215c", dict(aL, model="cnt", stat=st), E215_INPUTS, "against MM1-v3.1, desk")
        p = ("But MM1-v3, which has no layout term, read those layouts at 9.65% and was closer than N1+N2 at 17 cases, farther at 6, with 5 "
             "ties (p 0.035)")
        s3L = e215_stat(c215, PA215, "posthoc", "v3", "wall", "fm", "L")
        D("s45.ra.v3L", s3L["rms"], "{:.2f}", p, "e215", dict(aL, model="v3", stat="rms"), E215_INPUTS, "REPORTED, rms %, desk")
        cl = e215_closer(c215, rules, PA215, "posthoc", "v3", "wall", "L", base_model="cnt")
        for st in ("closer", "farther", "ties"):
            D("s45.ra.v3cnt." + st, cl[st], "{:d}", p, "e215c", dict(aL, model="v3", base="cnt", stat=st), E215_INPUTS,
              "MM1-v3 against N1+N2, desk")
        D("s45.ra.v3cnt.p", cl["p"], "{:.2g}", p, "e215c", dict(aL, model="v3", base="cnt", stat="p"), E215_INPUTS,
          "the exact two-sided sign test, REPORTED, desk")
        p = ("the terms' own REPORTED score (c9adc716) finds the same against G1+N1 (MM1-v3 closer at 18 cases, G1+N1 at 6, with 4 ties, p "
             "0.023) and reads \"no frozen layout form beats MM1-v3 on these points\"")
        lit = "| G1+N1 | **MM1-v3 CLOSER 6/18/4 (p 0.023)** |"
        for i, tok in enumerate(("18", "6", "4", "0.023")):
            T("s45.ra.g1n1.%d" % i, "terms_note", lit, tok, p, "the terms' REPORTED score's dated note (post hoc)")
        T("s45.ra.g1n1.q", "terms_note", "but no frozen layout form beats MM1-v3 on these points", "no frozen layout form beats MM1-v3 on these points",
          p, "the note's words, quoted")
        if "B" in ARMS215:
            D("s45.ra.b013", 1 + e215_one(c215, "B", "registered", "lnc", "Jg", "mf", "b013") / 100.0, "{:.2f}", "on arm B's one point it read 1.01",
              "e215pt", {"point": "b013", "group": "registered", "model": "lnc"}, E215_INPUTS, "measured / the term's J over idle given t, desk")
        T("s45.ra.nb1", "lnc_note", "at NB 1 it is the highest (a031 25.90, a032 25.75", "1", "most at NB 1 (a031, a032)")
        T("s45.ra.l28", "lay_readme", "At the 28 subset rows the factor runs 0.9942-1.0139", "28", "At family L's 28 layouts MM1-v3.1 and every form beside it")
        if "e215P_note" in PINS:
            p = "MM1-v2 read those layouts best: 6.81% on this report's footing, 6.98% on the scorer's (the pooled note)"
            s2L = e215_stat(c215, PA215, "posthoc", "v2", "wall", "fm", "L")
            D("s45.ra.v2L.fm", s2L["rms"], "{:.2f}", p, "e215", {"arm": PA215, "group": "posthoc", "model": "v2", "q": "wall", "conv": "fm",
              "only": "L", "stat": "rms"}, E215_INPUTS, "REPORTED, rms %, desk")  # report-v2-fix (M2)
            T("s45.ra.v2L", "e215P_note", "| MM1-v2 | 6.98% (28) | 7.47% | 6.97% | 6.04% (23) | 6.77% | 1.42% (28) | 6.88% | 0.24 W (5) |", "6.98", p)
        # the readings (the frozen scorer's REPORTED readings, arm A)
        base = ["arms", "A", "readings_REPORTED"]
        G.json("s45.rd.n28", "e215A_scores", base + ["layout_sets", 1, "shape_format_kind_shires", 3], "{:d}", "at gemmL1x9x6's eight 28-shire masks",
               "the shire count of the set, REPORTED")
        p = "the card's eight times there spread by 0.64%, its two 24-shire masks by 0.31%"
        G.json("s45.rd.l28", "e215A_scores", base + ["layout_sets", 1, "spread"], "{:.2f}", p, "measured spread, REPORTED", scale=100.0)
        G.json("s45.rd.l24", "e215A_scores", base + ["layout_sets", 0, "spread"], "{:.2f}", p, "measured spread, REPORTED", scale=100.0)
        p = "yet all eight 28-shire masks ran 9.2% to 9.8% faster than MM1-v3.1's one forecast"
        for k, ck in (("0", "rgm136 gemmL|gemmL1x9x6|fp32|0xfffff0ff"), ("1", "rgm136 gemmL|gemmL1x9x6|fp32|0xfff0ffff")):
            D("s45.rd.f28" + k, -e215_one(c215, "A", "posthoc", "v31", "wall", "mf", ck), "{:.1f}", p, "e215one_neg",
              {"arm": "A", "group": "posthoc", "model": "v31", "q": "wall", "conv": "mf", "key": ck}, E215_INPUTS, "how far under MM1-v3.1's forecast, %, desk")
        p = "gemmLnc ran at 0.933 and 0.926 of gemmLn's wall cycles, where MM1-v3.1 forecast 1.024"
        G.json("s45.rd.c0", "e215A_scores", base + ["census_path", 0, "measured_cw"], "{:.3f}", p, "measured ratio, REPORTED")
        G.json("s45.rd.c1", "e215A_scores", base + ["census_path", 1, "measured_cw"], "{:.3f}", p, "measured ratio, REPORTED")
        G.json("s45.rd.c2", "e215A_scores", base + ["census_path", 0, "models_cw", "MM1-v3.1"], "{:.3f}", p, "MM1-v3.1's ratio, REPORTED")
        p = "it missed most at int8 data of plus and minus one (0.816 measured against 0.991)"
        G.json("s45.rd.s0", "e215A_scores", base + ["switch_route", 4, "measured_W_ratio"], "{:.3f}", p, "measured ratio, REPORTED")
        G.json("s45.rd.s1", "e215A_scores", base + ["switch_route", 4, "models_W_ratio", "MM1-v3.1"], "{:.3f}", p, "MM1-v3.1's ratio, REPORTED")
        sw = R.json("e215A_scores")["arms"]["A"]["readings_REPORTED"]["switch_route"]
        dmax = max(abs(c["measured_W_ratio"] - c["models_W_ratio"]["MM1-v3.1"]) for i, c in enumerate(sw) if i != 4)
        D("s45.rd.s2", dmax, "{:.3f}", "at the other seven kinds the two agree to within 0.029", "e215sw", {"skip": 4}, ["e215A_scores"],
          "the largest |measured - MM1-v3.1| kind-over-random ratio but the skipped kind, desk")
        p = "the ties read 1.9% under the committed reference in W over idle"
        D("s45.rd.off", -100 * R.json("e215A_scores")["arms"]["A"]["day_offset_REPORTED"]["offset_W"], "{:.1f}", p, "e215off",
          {"arm": "A"}, ["e215A_scores"], "minus the day offset, %, REPORTED")
        # report-v2-fix (finding M6): T7 blind on E215's layouts, in section 6.3
        p = "blind on E215's 28 layouts it read 13.93% against MM1-v3.1's 10.72%"
        for k, m, st, fmt in (("n", "t7", "n", "{:d}"), ("t7", "t7", "rms", "{:.2f}"), ("v31", "v31", "rms", "{:.2f}")):
            s = e215_stat(c215, PA215, "posthoc", m, "wall", "fm", "L")
            D("s63.t7L." + k, s[st], fmt, p, "e215", {"arm": PA215, "group": "posthoc", "model": m, "q": "wall", "conv": "fm", "only": "L",
              "stat": st}, E215_INPUTS, "blind, post hoc-selected, desk")
        # report-v2-fix (finding M7): section 5, E215's family S (blind, post hoc-selected): the paragraph and its table
        aS = {"arm": PA215, "group": "posthoc", "model": "v31", "q": "Jg", "conv": "fm", "only": "S"}
        sS = e215_stat(c215, PA215, "posthoc", "v31", "Jg", "fm", "S")
        p = "read 8.45% rms (+2.53) over the 12 (forecast / measured - 1; figure 3)"
        D("s5S.rms", sS["rms"], "{:.2f}", p, "e215", dict(aS, stat="rms"), E215_INPUTS, "blind, post hoc-selected, rms %, desk")
        D("s5S.bias", sS["bias"], "{:+.2f}", p, "e215", dict(aS, stat="bias"), E215_INPUTS, "blind, post hoc-selected, bias %, desk")
        D("s5S.n", sS["n"], "{:d}", p, "e215", dict(aS, stat="n"), E215_INPUTS, "points, desk")
        p = ("It missed most at int8 data of plus and minus one (a057): +23.6%, where the measured kind-over-random W ratio was 0.816 "
             "against MM1-v3.1's 0.991")
        D("s5S.a057", e215_one(c215, "A", "posthoc", "v31", "Jg", "fm", "a057"), "{:+.1f}", p, "e215one",
          {"arm": "A", "group": "posthoc", "model": "v31", "q": "Jg", "conv": "fm", "key": "a057"}, E215_INPUTS,
          "one E215 point, %, desk (forecast / measured - 1)")
        swA = R.json("e215A_scores")["arms"]["A"]["readings_REPORTED"]["switch_route"]
        i = [c["kind"] for c in swA].index("a057")
        G.json("s5S.a057m", "e215A_scores", base + ["switch_route", i, "measured_W_ratio"], "{:.3f}", p, "measured ratio, REPORTED")
        G.json("s5S.a057f", "e215A_scores", base + ["switch_route", i, "models_W_ratio", "MM1-v3.1"], "{:.3f}", p, "MM1-v3.1's ratio, REPORTED")
        Mf = {a: R.json("e215%s_scores" % a)["arms"][a]["measured"] for a in ARMS215}
        byfmt = {}
        for a in ARMS215:
            for r in e215_rows(c215, a, "posthoc", "v31", "Jg", "S"):
                pt = r["key"].split(":")[1]
                byfmt.setdefault(Mf[a][pt]["format"], []).append((100.0 * r["fm"], a, pt))
        p = "The eight fp32 kinds read -6.7% to +5.6%; the four int8 kinds all read high, +5.7% to +23.6%"
        for fmt_name in ("fp32", "int8"):
            for k, (v, a, pt) in (("lo", min(byfmt[fmt_name])), ("hi", max(byfmt[fmt_name]))):
                D("s5S.%s.%s" % (fmt_name, k), v, "{:+.1f}", p, "e215one",
                  {"arm": a, "group": "posthoc", "model": "v31", "q": "Jg", "conv": "fm", "key": pt}, E215_INPUTS,
                  "the %s end of the %s kinds: one E215 point, %%, desk (forecast / measured - 1)" % ({"lo": "low", "hi": "high"}[k], fmt_name))
        tabs["switch_S"] = []
        tabs["switch_S_fig"] = []
        for a in ARMS215:
            sw = R.json("e215%s_scores" % a)["arms"][a]["readings_REPORTED"]["switch_route"]
            errs = {r["key"].split(":")[1]: 100.0 * r["fm"] for r in e215_rows(c215, a, "posthoc", "v31", "Jg", "S")}
            bs = ["arms", a, "readings_REPORTED", "switch_route"]
            for i, c in enumerate(sw):
                pt = c["kind"]
                kind = c["what"].split(" / random")[0]
                fmt_name = Mf[a][pt]["format"]
                row = (f"| {pt} | {a}, {fmt_name} | {kind} | {c['measured_W_ratio']:.3f} | {c['models_W_ratio']['MM1-v3.1']:.3f} | "
                       f"{sgn(errs[pt])}% |")
                G.json(f"s5S.t.{pt}.m", "e215%s_scores" % a, bs + [i, "measured_W_ratio"], "{:.3f}", row, "measured ratio, REPORTED")
                G.json(f"s5S.t.{pt}.f", "e215%s_scores" % a, bs + [i, "models_W_ratio", "MM1-v3.1"], "{:.3f}", row, "MM1-v3.1's ratio, REPORTED")
                D(f"s5S.t.{pt}.e", errs[pt], "{:+.1f}", row, "e215one",
                  {"arm": a, "group": "posthoc", "model": "v31", "q": "Jg", "conv": "fm", "key": pt}, E215_INPUTS,
                  "one E215 point, %, desk (forecast / measured - 1)")
                tabs["switch_S"].append(row)
                tabs["switch_S_fig"].append({"point": pt, "format": fmt_name, "kind": kind, "measured": c["measured_W_ratio"],
                                             "v31": c["models_W_ratio"]["MM1-v3.1"], "err": errs[pt]})
    return tabs


# ------------------------------------------------------------------------------------------------ every README number
QUOTE = ("I want you to focus on the matte mold most of all, so I want to have a model which predicts matte mold energy and number of transistor "
         "switches and clock cycles. From based on what I know about the size of a matrix and which operations are contained. See check how well "
         "the timing simulation for the matte mold matches reality and the energy.")


def build(G, R, cache, c215=None, rules215=None):
    T, Jn, D = G.text, G.json, G.desk
    rows = sc_rows(R, cache, c215)
    sim = sim_values(R)
    sim_all = sim_all_of(sim)
    floors = []
    for arm in ("A", "B"):
        S = R.json("e213%s_scores" % arm)["arms"][arm]
        floors += [r["counter_mean_over_floor"] for p, r in sorted(S["readings_REPORTED"]["timing_simulation"].items())
                   if r.get("counter_mean_over_floor") is not None and S["measured"][p]["role"] == "point"]
    rat = e213_ratios(R)
    lnc = [rat[p]["ratio"] for p in ("a075", "a079", "a082", "a086", "a087", "k37", "k40")]
    twins = [rat[p]["ratio"] for p in ("a006", "a076", "a030", "a083", "k06")]
    masks_spread = max(m["spread"] for m in R.json("e213A_scores")["arms"]["A"]["readings_REPORTED"]["masks"])
    e212_runs = sum(readme_runs(R.text("e212_" + s)) for s, _, _ in E212_SESSIONS)
    e212_cm = sum(readme_card_minutes(R.text("e212_" + s)) for s, _, _ in E212_SESSIONS)
    e214_runs = sum(readme_runs(R.text("e214_" + s)) for s, _, _ in E214_SESSIONS)
    e214_cm = sum(readme_card_minutes(R.text("e214_" + s)) for s, _, _ in E214_SESSIONS)
    sumin12 = ["e212_" + s for s, _, _ in E212_SESSIONS]
    sumin14 = ["e214_" + s for s, _, _ in E214_SESSIONS]
    st = {"min": "%.1f" % min(sim_all), "max": "%.1f" % max(sim_all), "median": "%.1f" % statistics.median(sim_all)}
    sel_n, sel_f = newest_and_f1(rows)

    def SIM(key, value, fmt, phrase, stat, which):
        D(key, value, fmt, phrase, "sim", {"stat": stat, "which": which}, ["v1_numbers", "e213A_scores", "e213B_scores"],
          "card cycles a GEMM over the simulator's instructions a minion a GEMM, desk")

    def E13(key, arm, model, q, stat, phrase, conv="fm", no_lnc=False, fmt="{:.2f}"):
        s = e213_stat(cache, arm, model, q, conv, no_lnc)
        D(key, s[stat], fmt, phrase, "e213", {"arm": arm, "model": model, "q": q, "conv": conv, "no_lnc": no_lnc, "stat": stat}, E213_INPUTS,
          "E213, %s, %s, desk (%s)" % (model, q, "forecast / measured - 1" if conv == "fm" else "measured / forecast - 1"))

    def RAT(key, which, stat, fmt, phrase):
        vals = [rat[p]["ratio"] for p in which]
        v = {"min": min(vals), "max": max(vals)}[stat] if stat in ("min", "max") else rat[which[0]]["ratio"]
        D(key, v, fmt, phrase, "ratio", {"points": which, "stat": stat}, ["e213A_scores", "e213B_scores"],
          "measured J over idle / MM1-v3's J given the measured seconds, desk")

    V31T = ["time", "v3.1", "LOEO", "all", "no_twin", "rms_pct"]

    def V31(key, model, fam, setk, q, phrase, fmt="{:.2f}"):
        base = ["time" if q is None else "energy", model, fam, setk, "no_twin"] + ([] if q is None else [q]) + ["rms_pct"]
        Jn(key, "v31_holdout", base, fmt, phrase, "held out, no configuration twins, rms %")

    # ---------------- On one screen
    E13("os.e213P.v3.wall", "P", "v3", "wall", "rms", "it kept the wall cycles to 4.1% rms", fmt="{:.1f}")
    RAT("os.lnc.max", ["a075", "a079", "a082", "a086", "a087", "k37", "k40"], "max", "{:.1f}", "under-priced one loop's energy by up to 1.8 times")
    T("os.walk.352", "walk_readme", "352 of 352 traced working minions", "352", "masked walk at 352 of 352 working minions at each of two masks")
    T("os.walk.352b", "walk_readme", "352 of 352 traced working minions", "352", "masked walk at 352 of 352 working minions at each of two masks")
    p = "over %d blind points the card took %s to %s cycles for each simulated instruction" % (len(sim_all), st["min"], st["max"])
    SIM("os.sim.n", len(sim_all), "{:d}", p, "n", "all")
    SIM("os.sim.min", min(sim_all), "{:.1f}", p, "min", "all")
    SIM("os.sim.max", max(sim_all), "{:.1f}", p, "max", "all")
    range_entry(G, "os.newest.wall", sel_n, "wall", "the newest MM1 read 2.7 to 9.0% rms in wall cycles")
    range_entry(G, "os.newest.jg3", sel_n, "jg3", "and 3.2 to 11.9% in joules over idle given the measured seconds")
    p = "against 14.5 to 19.7% and 18.4 to 31.0% for F1"
    range_entry(G, "os.f1.wall", sel_f, "wall", p)
    range_entry(G, "os.f1.jg3", sel_f, "jg3", p)
    # report-v2-fix (finding M3): E215's post hoc-selected points beside the registered range, and the low end's repeated configurations
    sel_ph = [r for r in rows if r[1] == "MM1-v3.1" and r[0] in ("E215 arm A, families L, S (aifoundry3 card 0, 600 MHz)",
                                                                "E215 arm B, families L, S (aifoundry1 card 1, 600 MHz)")]
    if sel_ph:
        range_entry(G, "os.posthoc.wall", sel_ph, "wall",
                    "On E215's post hoc-selected points (families L and S), MM1-v3.1 read 10.2 and 11.8% in wall cycles")
    p = "the low end, 2.7%, is E212's S3, where 29 of its 46 cases repeat a configuration MM1-v3 was fitted on (4.21% on its 17 new ones)"
    tws = ["twins", "wall cycles (time configuration)"]
    Jn("os.s3.low", "e212s3", ["per_case", "v3", "wall", "rms_pct"], "{:.1f}", p, "blind, REPORTED, rms %")
    Jn("os.s3.tw", "e212s3", tws + ["twin", "v3", "n"], "{:d}", p, "cases")
    Jn("os.s3.n", "e212s3", ["n_cases"], "{:d}", p, "cases")
    Jn("os.s3.nt", "e212s3", tws + ["no_twin", "v3", "rms_pct"], "{:.2f}", p, "rms %")
    Jn("os.s3.ntn", "e212s3", tws + ["no_twin", "v3", "n"], "{:d}", p, "cases")
    if c215 is not None:
        # report-v2-fix (finding M7): E215's family S in the summary; (finding M4): the retention and one-K-block misses in the summary
        p = ("blind on E215's 12 newly counted kinds (post hoc-selected), MM1-v3.1's J over idle given the seconds read 8.45%, but +23.6% at "
             "int8 data of plus and minus one")
        sS = e215_stat(c215, PA215, "posthoc", "v31", "Jg", "fm", "S")
        aS = {"arm": PA215, "group": "posthoc", "model": "v31", "q": "Jg", "conv": "fm", "only": "S"}
        D("os.sw.S.n", sS["n"], "{:d}", p, "e215", dict(aS, stat="n"), E215_INPUTS, "family S points, desk")
        D("os.sw.S.rms", sS["rms"], "{:.2f}", p, "e215", dict(aS, stat="rms"), E215_INPUTS, "blind, post hoc-selected, rms %, desk")
        D("os.sw.S.a057", e215_one(c215, "A", "posthoc", "v31", "Jg", "fm", "a057"), "{:+.1f}", p, "e215one",
          {"arm": "A", "group": "posthoc", "model": "v31", "q": "Jg", "conv": "fm", "key": "a057"}, E215_INPUTS,
          "one E215 point, %, desk (forecast / measured - 1)")
        p = ("the time just past the L3's first retention edge (gemmL2x1x7 ran 12.7% to 14.9% slower than MM1-v3.1 forecast on both cards: 4 of "
             "the 8 cases past E215's registered T1 band) and at one K block (11.0% and 10.9% slower)")
        for k, arm, ck in (("r0", "B", "rgm136 gemmL|gemmL2x1x7|fp32|0xffffffff"), ("r1", "A", "rgm136 gemmL|gemmL2x1x7|int8|0xffffffff")):
            D("os.sw7." + k, e215_one(c215, arm, "registered", "v31", "wall", "mf", ck), "{:.1f}", p, "e215one",
              {"arm": arm, "group": "registered", "model": "v31", "q": "wall", "conv": "mf", "key": ck}, E215_INPUTS,
              "one E215 case, %, desk (measured / forecast - 1)")
        for k, only in (("nR", "R"), ("n", None)):
            args = {"arm": PA215, "group": "registered", "model": "v31", "q": "wall", "rule": "T1"}
            if only:
                args["only"] = only
            D("os.sw7." + k, e215_miss(c215, rules215, PA215, "registered", "v31", "wall", "T1", only), "{:d}", p, "e215miss", args,
              E215_INPUTS + ["e215_rules"], "cases past MM1-v3.1's registered T1 band%s, desk" % (" in family " + only if only else ""))
        for k, arm, ck in (("k0", "A", "rgm136 gemmL|gemmL8x15x1|int8|0xffffffff"), ("k1", "B", "rgm136 gemmL|gemmL16x14x1|fp32|0xffffffff")):
            D("os.sw7." + k, e215_one(c215, arm, "registered", "v31", "wall", "mf", ck), "{:.1f}", p, "e215one",
              {"arm": arm, "group": "registered", "model": "v31", "q": "wall", "conv": "mf", "key": ck}, E215_INPUTS,
              "one E215 case, %, desk (measured / forecast - 1)")
    p = "(wall cycles closer at 86 cases, farther at 13)"
    T("os.hp1.v3", "e213P_txt", "HP1 MM1-v3 BETTER (86/13/16", "86", p)
    T("os.hp1.v2", "e213P_txt", "HP1 MM1-v3 BETTER (86/13/16", "13", p)
    Jn("os.e210", "v1_numbers", ["switch", "routes", "R1", "rms_over_D_pct"], "{:.1f}", "energy followed MM1's counted switches to 1.9% of the data-dependent power", "blind, REPORTED, % of D")
    p = "its switch route with 179 new bench counts read 6.8% against 25.0% for a null"
    T("os.counts", "counts_readme", "179 bench points in the tables", "179", p)
    Jn("os.sw.v3", "unread_sw", ["groups", "A", "all", "V3", "Q1_cases", "rms_pct"], "{:.1f}", p, "unread, rms %")
    Jn("os.sw.n", "unread_sw", ["groups", "A", "all", "N", "Q1_cases", "rms_pct"], "{:.1f}", p, "unread, rms %")
    p = "(closer at 35 cases, farther at 5)"
    T("os.sw.c35", "unread_sw_readme", "MM1-v3 is closer on 35 cases and N on 5", "35", p)
    T("os.sw.c5", "unread_sw_readme", "MM1-v3 is closer on 35 cases and N on 5", "5", p)
    p = "(4.72% against 4.72% in wall cycles held out)"
    V31("os.v31.loeo", "v3.1", "LOEO", "all", None, p)
    V31("os.v3r.loeo", "v3 refitted", "LOEO", "all", None, p)
    D("os.e214.runs", e214_runs, "{:d}", "(622 runs on aifoundry1's two cards, committed and verified)", "sum_runs", {"pins": sumin14}, sumin14, "runs, desk sum")
    if "e214u_scores" in PINS:
        p = "and on E214's 20 new kinds 7.76% against 28.05%"
        T("os.e214.k20", "e214u_readme", "group S: E214's 20 new tile kinds, 33 arms, 54 runs", "20", p)
        Jn("os.e214.q1m", "e214u_scores", ["part_S", "v31", "Q1", "model", "rms_pct"], "{:.2f}", p, "unread, rms %")
        Jn("os.e214.q1n", "e214u_scores", ["part_S", "v31", "Q1", "N", "rms_pct"], "{:.2f}", p, "unread, rms %")
        p = "MM1-v3.1 read 6.66% in wall cycles and MM1-v2 8.06%"
        Jn("os.e214.v31", "e214u_scores", ["tables_per_case", "v31", "wall", "pooled", "no_twin", "rms_pct"], "{:.2f}", p, "unread, rms %")
        Jn("os.e214.v2", "e214u_scores", ["tables_per_case", "v2", "wall", "pooled", "no_twin", "rms_pct"], "{:.2f}", p, "unread, rms %")
    p = "to about 0.4% in cycles and 1.2% in joules over idle"
    Jn("os.rep.cyc", "v1_numbers", ["repeat", "E208", "cyc_op_mean", "rms_pct"], "{:.1f}", p, "measured, post hoc, rms %")
    Jn("os.rep.j", "v1_numbers", ["repeat", "E208", "J_op", "rms_pct"], "{:.1f}", p, "measured, post hoc, rms %")
    p = "(1.15 to 1.80 times the forecast at all seven E213 points"
    RAT("os.lnc.min2", ["a075", "a079", "a082", "a086", "a087", "k37", "k40"], "min", "{:.2f}", p)
    RAT("os.lnc.max2", ["a075", "a079", "a082", "a086", "a087", "k37", "k40"], "max", "{:.2f}", p)

    # ---------------- the header
    G.git("hdr.pin", "7edf3477", "15:51:20", "up to GitHub main 7edf3477 (E215's pooled scores, committed at 15:51:20 PST)")
    G.git("hdr.fix", "c9adc716", "16:14:47", "the corrections also cite c9adc716, the frozen terms' own REPORTED score on E215 (committed at 16:14:47 PST)")

    # ---------------- 1
    T("s1.time", "v0_readme", "at or before 09:48:24 PST", "09:48:24", "(Mon 16 Nov 2026, at or before 09:48:24 PST;")
    T("s1.quote", "v0_readme", QUOTE, QUOTE, QUOTE, "the owner's words, verbatim")

    T("s0.shire", "v1_readme", "A *shire* is a group of 32 minions with its own L2 cache", "32", "A *shire* is a group of 32 minions with its own L2 cache")
    # ---------------- 2
    p = ("The ET-SoC-1 has 1,088 minions in 34 shires (32 compute shires, a master and a spare); the lab's kernels use 1,024 of them, in 32 "
         "shires of 32")
    for i, tok in enumerate(("1,088", "34", "32", "1,024", "32", "32")):
        T("s2.chip.%d" % i, "v1_readme", p, tok, p, "as the first version states it (checked there against docs/et-soc1-notes.md and 05-claims.md)")
    T("s2.l3", "v1_readme", "the chip shares a 32 MB L3", "32", "the chip shares a 32 MB L3")
    T("s2.600", "v1_readme", "The lab's cards run at a fixed 600 MHz", "600", "The lab's cards run at a fixed 600 MHz (aifoundry3 card 0 and aifoundry1 card 1)")
    p = "computes M = 1,024·MB, N = 512·NB, K = 512·KB·w (w = 1, 2, 4 for fp32, fp16, int8)"
    for i, tok in enumerate(("1,024", "512", "512")):
        T("s2.grid.%d" % i, "v1_readme", p, tok, p)
    T("s2.192", "v1_readme", "A tile op of one shire asks for 192 cache lines", "192", "A tile op of one shire asks for 192 cache lines")
    p = "kept up to a first edge at 37.4 MB, then half of them on a plateau that ends at 72.3 MB"
    T("s2.x1", "v3_readme", "the first edge at x1 = 37.4 MB", "37.4", p)
    T("s2.x2", "v3_readme", "that ends at x2 = 72.3 MB", "72.3", p)
    T("s2.d8", "v3_readme", "d8 = +4.8%", "+4.8", "an int8 factor on the L3-served stream (+4.8%)")
    T("s2.r2", "v3_readme", "r2 = 0.64", "0.64", "a shire-cache share (0.64)")
    T("s2.kappa", "v3_readme", "so 1.58e16 fin edges a joule", "1.58e16", "(1.58e16 fin edges a joule)")
    T("s2.finedge", "v1_readme", "one transistor gate, one fin, charged or discharged by a net transition",
      "one transistor gate, one fin, charged or discharged by a net transition", "one transistor gate, one fin, charged or discharged by a net transition", "the unit's definition, quoted")
    T("s2.mask32", "v1_readme", "the shire mask: which of the 32 shires run", "32", "| the shire mask: which of the 32 shires run |")
    for key, c, want in (("s2.d.v0", "2d1413f5", "Mon 16 Nov"), ("s2.d.v1", "25d2e74e", "Mon 16 Nov"), ("s2.d.v2", "3ca4b717", "Tue 17 Nov"), ("s2.d.v3", "b1493082", "Tue 17 Nov"),
                         ("s2.d.v31", "2c971828", "Wed 18 Nov")):
        G.git(key, c, want, "| %s (%s) |" % (c, want), "the commit's own date (git, Pacific)", fmt="%a %d %b")
    p = "| 769 GEMM time points and 682 energy points from 11 earlier experiments |"
    for i, tok in enumerate(("769", "682", "11")):
        T("s2.v0fit.%d" % i, "v1_readme", "fitted on 769 GEMM time points and 682 energy points from 11 earlier experiments", tok, p)
    T("s2.v0ho", "v1_readme", "MM1-v0's 5.54%", "5.54", "| 5.54% on its own pool (not comparable) |")
    p = "| 888 time and 791 energy points (with E206 arm A) |"
    T("s2.v1fit.0", "v1_readme", "(888 time and 791 energy", "888", p)
    T("s2.v1fit.1", "v1_readme", "(888 time and 791 energy", "791", p)
    p = "| 4.70% against 5.91% |"
    T("s2.v1ho.0", "v1_readme", "cycles 4.70% for MM1-v1 against 5.91% for MM1-v0's form refitted", "4.70", p)
    T("s2.v1ho.1", "v1_readme", "cycles 4.70% for MM1-v1 against 5.91% for MM1-v0's form refitted", "5.91", p)
    p = "| 1,072 time and 964 energy points (with E208) |"
    T("s2.v2fit.0", "v1_readme", "(1,072 time and 964 energy points)", "1,072", p)
    T("s2.v2fit.1", "v1_readme", "(1,072 time and 964 energy points)", "964", p)
    p = "| 5.41% against 5.70% |"
    T("s2.v2ho.0", "v1_readme", "5.41% for MM1-v2 against 5.70% for MM1-v1's form refitted", "5.41", p)
    T("s2.v2ho.1", "v1_readme", "5.41% for MM1-v2 against 5.70% for MM1-v1's form refitted", "5.70", p)
    p = "| 1,737 time and 1,603 energy points (with E207, E209, E211 and eight E212 sessions) |"
    T("s2.v3fit.0", "v3_readme", "1,737 time points", "1,737", p)
    T("s2.v3fit.1", "v3_readme", "1,603 points v3 prices", "1,603", p)
    p = "| 4.53% against 5.20%; without configuration twins 5.04% against 5.55% |"
    T("s2.v3ho.0", "v3_readme", "LOEO 4.53% v3 against 5.20% v2form", "4.53", p)
    T("s2.v3ho.1", "v3_readme", "LOEO 4.53% v3 against 5.20% v2form", "5.20", p)
    T("s2.v3ho.2", "v3_readme", "without configuration twins, LOEO reads 5.04% against 5.55%", "5.04", p)
    T("s2.v3ho.3", "v3_readme", "without configuration twins, LOEO reads 5.04% against 5.55%", "5.55", p)
    p = "| 1,906 time and 1,832 energy points (with E213 and E212's re-run S3) |"
    T("s2.v31fit.0", "v31_readme", "1906 time points and 1832 energy points", "1,906", p)
    T("s2.v31fit.1", "v31_readme", "1906 time points and 1832 energy points", "1,832", p)
    p = "| without twins 4.72% against 4.72% (section 6) |"
    V31("s2.v31ho.0", "v3.1", "LOEO", "all", None, p)
    V31("s2.v31ho.1", "v3 refitted", "LOEO", "all", None, p)
    T("s2.v3e.0", "v3_readme", "LOEO 4.85% against 6.14%", "4.85", "read 4.85% in W over idle against 6.14% for MM1-v2's form")
    T("s2.v3e.1", "v3_readme", "LOEO 4.85% against 6.14%", "6.14", "read 4.85% in W over idle against 6.14% for MM1-v2's form")
    T("s2.v3e.2", "v3_readme", "LOCO 7.66% against 11.59%", "7.66", "with a card held out 7.66% against 11.59%")
    T("s2.v3e.3", "v3_readme", "LOCO 7.66% against 11.59%", "11.59", "with a card held out 7.66% against 11.59%")
    T("s2.v3e.4", "v3_readme", "anywhere from 6.8% to 43.5%", "6.8", "anything from 6.8% to 43.5%")
    T("s2.v3e.5", "v3_readme", "anywhere from 6.8% to 43.5%", "43.5", "anything from 6.8% to 43.5%")

    # ---------------- 3
    p = "rgm136's gemmL loop runs 46 instructions an op, not 36; rgm211's gemmL walk 40, its gemmLn 31, and gemmLnc 39"
    T("s3.ins46", "e211_corr", "the gemmL loops run 46 and 40 instructions an op, not 36 and 35", "46", p)
    T("s3.ins36", "e211_corr", "the gemmL loops run 46 and 40 instructions an op, not 36 and 35", "36", p)
    T("s3.ins40", "e211_corr", "the gemmL loops run 46 and 40 instructions an op, not 36 and 35", "40", p)
    T("s3.ins31", "e211_corr", "A1's 31 for gemmLn is right", "31", p)
    T("s3.ins39", "e211_corr", "run_gemm_large, non-cooperative | 39 |", "39", p)
    T("s3.harts", "e211_corr", "every one of the 64 harts retired exactly as many instructions as its cycles_span, the simulator's steps",
      "every one of the 64 harts retired exactly as many instructions as its cycles_span, the simulator's steps",
      "\"every one of the 64 harts retired exactly as many instructions as its cycles_span, the simulator's steps\"", "the finding, quoted")
    p = "(46.625 an op, 24.25 a C-tile row and 92 a launch;"
    for i, tok in enumerate(("46.625", "24.25", "92")):
        T("s3.law.%d" % i, "v1_readme", "46.625 steps an op + 24.25 a C-tile row, with + 92 a launch", tok, p)
    T("s3.law11", "v1_readme", "a law fitted to 11 simulator runs", "11", "come from a law fitted to 11 simulator runs of rgm136's gemmL")
    n15 = len(sim.get("E215A", [])) + len(sim.get("E215B", []))
    p = ("Over %d blind points (E206's two arms and E207, %d; E213's two arms, %d%s) the card took %s to %s cycles a GEMM (the slowest "
         "minion) for each simulated instruction a minion, median %s"
         % (len(sim_all), len(sim["E206-E207"]), len(sim["E213A"]) + len(sim["E213B"]), ("; E215's %s, %d" % ("two arms" if len(ARMS215) == 2 else "arm " + ARMS215[0], n15)) if n15 else "",
            st["min"], st["max"], st["median"]))
    SIM("s3.sim.n", len(sim_all), "{:d}", p, "n", "all")
    SIM("s3.sim.n1", len(sim["E206-E207"]), "{:d}", p, "n", "E206-E207")
    SIM("s3.sim.n2", len(sim["E213A"]) + len(sim["E213B"]), "{:d}", p, "n", "E213")
    if n15:
        SIM("s3.sim.nE215", n15, "{:d}", p, "n", "E215")
    SIM("s3.sim.min", min(sim_all), "{:.1f}", p, "min", "all")
    SIM("s3.sim.max", max(sim_all), "{:.1f}", p, "max", "all")
    SIM("s3.sim.med", statistics.median(sim_all), "{:.1f}", p, "median", "all")
    p = ("at each mask, 352 of 352 traced working minions issued exactly the frozen sequence of tensor operations (704 of 704 over both), and "
         "900 traced off-mask minions issued none")
    T("s3.walk.0", "walk_readme", "352 of 352 traced working minions", "352", p)
    T("s3.walk.1", "walk_readme", "352 of 352 traced working minions", "352", p)
    T("s3.walk.2", "walk_readme", "(704 of 704 over both masks)", "704", p)
    T("s3.walk.3", "walk_readme", "(704 of 704 over both masks)", "704", p)
    T("s3.walk.4", "walk_readme", "900 traced off-mask minions", "900", p)
    T("s3.walk.runs", "walk_readme", "the 10 runs'", "10", "5a75e212; 10 simulator runs)")
    p = "ordered only 3 of 8 to 3 of 11 of E212's measured layout pairs by time"
    T("s3.order.0", "walk_readme", "| fewer fresh lines a shire-op, strict LRU at 32 MB | 3 of 8 |", "3 of 8", p)
    T("s3.order.1", "walk_readme", "| fewer fresh lines a shire-op, MM1-v3's frozen retention | 3 of 11 |", "3 of 11", p)
    p = "18 of 18 registered readings within 2 cycles over 12 micro-loop configurations"
    T("s3.rtl.0", "v1_readme", "18 of 18 registered readings within 2 cycles", "18", p)
    T("s3.rtl.1", "v1_readme", "18 of 18 registered readings within 2 cycles", "18", p)
    T("s3.rtl.2", "v1_readme", "18 of 18 registered readings within 2 cycles", "2", p)
    T("s3.rtl.3", "v1_readme", "12 micro-loop configurations", "12", p)
    p = "the counter's mean ran 1.33 to 5.33 times the tensor unit's floor"
    D("s3.floor.min", min(floors), "{:.2f}", p, "floor", {"stat": "min"}, ["e213A_scores", "e213B_scores"], "the counter's mean over the tensor floor, desk")
    D("s3.floor.max", max(floors), "{:.2f}", p, "floor", {"stat": "max"}, ["e213A_scores", "e213B_scores"], "the counter's mean over the tensor floor, desk")

    # ---------------- 4: the scorecard
    T("s4.3W", "v1_readme", "at the points of 3 W over idle and above", "3", "measured seconds per point at 3 W over idle and above")
    sc = reg_scorecard(G, rows)
    rep = ("| the card's repeat floor | the same schedule five hours apart (E208, aifoundry2 card 0) | measured, post hoc | 71 / 60 | 0.38 | 0.41 | "
           "1.16 | - |")
    Jn("s4.rep.n0", "v1_numbers", ["repeat", "E208", "cyc_op_max", "n"], "{:d}", rep)
    Jn("s4.rep.n1", "v1_numbers", ["repeat", "E208", "J_op", "n"], "{:d}", rep)
    Jn("s4.rep.wall", "v1_numbers", ["repeat", "E208", "cyc_op_max", "rms_pct"], "{:.2f}", rep, "measured, post hoc")
    Jn("s4.rep.mean", "v1_numbers", ["repeat", "E208", "cyc_op_mean", "rms_pct"], "{:.2f}", rep, "measured, post hoc")
    Jn("s4.rep.j", "v1_numbers", ["repeat", "E208", "J_op", "rms_pct"], "{:.2f}", rep, "measured, post hoc")
    Jn("s4.note.42", "unread_sw", ["pass_rule_against_N", "Q1", "n_cases"], "{:d}", "on their pass rules' cases (42 and 33)")
    if "e214u_scores" in PINS:
        Jn("s4.note.33", "e214u_scores", ["part_S", "v31", "Q1", "cases"], "{:d}", "on their pass rules' cases (42 and 33)")
    T("s41.ctrl", "v1_readme", "ran 3-6% fast on the card", "3-6", "its controls 3-6% fast")

    # ---------------- 4.2
    T("s42.post", "e212_reg", "at 05:22:43 PST", "05:22:43", "registered by its post at 05:22:43 PST Tue 17 Nov")
    T("s42.c1", "e212_reg", "aifoundry1 card 1 at 600 MHz", "600", "(aifoundry1 card 1 at 600 MHz, aifoundry1 card 0 at low power, aifoundry2 card 0 under its governor)")
    T("s42.arms", "e212_reg", "over 221 arms and an anchor in ten sessions", "221", "rgm136 unchanged over 221 arms and an anchor in ten sessions")
    T("s42.plan.0", "e212_reg", "Totals over the ten schedules: 764 runs; 508.2 planned card-minutes.", "764", "764 runs and 508.2 planned card-minutes")
    T("s42.plan.1", "e212_reg", "Totals over the ten schedules: 764 runs; 508.2 planned card-minutes.", "508.2", "764 runs and 508.2 planned card-minutes")
    p = "All ten sessions ran full and are committed: 764 runs in 342.94 card-minutes"
    D("s42.runs", e212_runs, "{:d}", p, "sum_runs", {"pins": sumin12}, sumin12, "runs, desk sum of the ten data READMEs")
    D("s42.cm", e212_cm, "{:.2f}", p, "sum_cm", {"pins": sumin12}, sumin12, "card-minutes, desk sum of the ten data READMEs")
    T("s42.crash", "e212_a2c0-S3", "was cut when aifoundry2 went down at about 15:45 PST that day", "15:45", "went down at about 15:45 PST Tue, before any of its runs")
    q = "\"Run E212's aifoundry2 S3 again, given that we know what caused the crash.\""
    T("s42.quote", "e212_a2c0-S3", q, q, q, "the owner's word as the separate session relayed it, verbatim")
    p = "55 of 55 runs in 23.02 card-minutes"
    T("s42.s3runs", "e212_a2c0-S3", "RAN FULL (55 of 55 runs)", "55", p)
    T("s42.s3runs2", "e212_a2c0-S3", "RAN FULL (55 of 55 runs)", "55", p)
    T("s42.s3cm", "e212_a2c0-S3", "23.02 card-minutes", "23.02", p)
    p = "read 6.65% in wall cycles and 7.76% in W over idle"
    Jn("s42.v2u.wall", "v2_unread_e212", ["per_case", "all", "wall", "rms_pct"], "{:.2f}", p, "unread, rms %")
    Jn("s42.v2u.w", "v2_unread_e212", ["per_case", "all", "W_given_t_ge3W", "rms_pct"], "{:.2f}", p, "unread, rms %")
    p = "read 4.75% against MM1-v2's 5.80%"
    Jn("s42.s4.v3", "v3_unread_s4", ["per_case", "v3", "wall", "rms_pct"], "{:.2f}", p, "unread, rms %")
    Jn("s42.s4.v2", "v3_unread_s4", ["per_case", "v2", "wall", "rms_pct"], "{:.2f}", p, "unread, rms %")
    p = "and 5.40% against 6.86% on the 18 of its 56 cases whose configuration was new"
    T("s42.s4new.0", "v3_readme", "on the other 18, wall cycles read 5.40% against 6.86%", "5.40", p)
    T("s42.s4new.1", "v3_readme", "on the other 18, wall cycles read 5.40% against 6.86%", "6.86", p)
    T("s42.s4new.2", "v3_readme", "on the other 18, wall cycles read 5.40% against 6.86%", "18", p)
    Jn("s42.s4new.3", "v3_unread_s4", ["n_cases"], "{:d}", p, "cases")
    T("s42.push", "e212s3_readme", "pushed at 20:52:51 PST", "20:52:51", "pushed at 20:52:51 PST Tue 17 Nov")
    T("s42.decl", "e212s3_readme", "hashed into the lane's log at 14:10:50 PST", "14:10:50", "the scoring was declared at 14:10:50 PST Wed")
    T("s42.fcc", "e212s3_readme", "the re-run's first card command came at 16:00:08 PST", "16:00:08", "before the re-run's first card command at 16:00:08")
    p = "MM1-v3 read 2.70% in wall cycles against MM1-v2's 4.33%"
    Jn("s42.s3.v3w", "e212s3", ["per_case", "v3", "wall", "rms_pct"], "{:.2f}", p, "blind, REPORTED, rms %")
    Jn("s42.s3.v2w", "e212s3", ["per_case", "v2", "wall", "rms_pct"], "{:.2f}", p, "blind, REPORTED, rms %")
    p = "and 3.55% in W over idle given the seconds against 5.65%"
    Jn("s42.s3.v3e", "e212s3", ["per_case", "v3", "W_given_t_ge3W", "rms_pct"], "{:.2f}", p, "blind, REPORTED, rms %")
    Jn("s42.s3.v2e", "e212s3", ["per_case", "v2", "W_given_t_ge3W", "rms_pct"], "{:.2f}", p, "blind, REPORTED, rms %")
    p = "closer on 26 cases in cycles, farther on 4, with 16 ties"
    for i, k in enumerate(("v3_closer", "v2_closer", "ties")):
        Jn("s42.s3.h2h.%d" % i, "e212s3", ["head_to_head_per_case_v3_vs_v2", "e_wall", k], "{:d}", p, "cases")
    p = "29 of its 46 cases repeat a configuration in MM1-v3's fit data, where it read 1.07%; on the 17 new ones it read 4.21% against MM1-v2's 6.58%"
    tw = ["twins", "wall cycles (time configuration)"]
    Jn("s42.s3.tw.0", "e212s3", tw + ["twin", "v3", "n"], "{:d}", p, "cases")
    Jn("s42.s3.tw.1", "e212s3", ["n_cases"], "{:d}", p, "cases")
    Jn("s42.s3.tw.2", "e212s3", tw + ["twin", "v3", "rms_pct"], "{:.2f}", p, "rms %")
    Jn("s42.s3.tw.3", "e212s3", tw + ["no_twin", "v3", "n"], "{:d}", p, "cases")
    Jn("s42.s3.tw.4", "e212s3", tw + ["no_twin", "v3", "rms_pct"], "{:.2f}", p, "rms %")
    Jn("s42.s3.tw.5", "e212s3", tw + ["no_twin", "v2", "rms_pct"], "{:.2f}", p, "rms %")
    Jn("s42.s3.v2form", "e212s3", tw + ["no_twin", "v2form", "rms_pct"], "{:.2f}",
       "and v2form, MM1-v2's form refitted on MM1-v3's data and shown beside, 4.08%", "REPORTED beside, rms %")  # report-v2-fix (L5)
    p = "+9.68%, +9.40% and +9.13%"
    for i, tok in enumerate(("+9.68", "+9.40", "+9.13")):
        T("s42.s3.miss.%d" % i, "e212s3_readme", "0x33333333 at +9.68%, 0x1111 at +9.40% and 0x11111111 at +9.13%", tok, p)

    # ---------------- 4.3
    p = "MM1-v3's own 90 frozen points on aifoundry3 card 0 at its pinned 600 MHz (87 never run on any card, 3 references)"
    T("s43.a.90", "e213_reg", "Arm A: 90 points, 87 scored and 3 references, 84 time cases", "90", p)
    T("s43.a.87", "e213_reg", "87 of 87 scored points never ran on any card", "87", p)
    T("s43.a.3", "e213_reg", "Arm A: 90 points, 87 scored and 3 references, 84 time cases", "3", p)
    p = "41 points chosen by the registration on aifoundry1 card 1 at 600 MHz (40 never run there, 1 reference)"
    T("s43.b.41", "e213_reg", "41 points, 40 scored and 1 reference", "41", p)
    T("s43.b.40", "e213_reg", "40 of 40 scored points never ran on card 1", "40", p)
    T("s43.b.1", "e213_reg", "41 points, 40 scored and 1 reference", "1", p)
    p = ("(arm A: 11% in wall cycles, 13% in the counter's mean, 11% in seconds; 11%, 12%, 4% and 10% in the four joule rules; 0.60 W at the "
         "points under 3 W)")
    for i, r in enumerate(("T1", "T2", "T3", "E1", "E2", "E3", "E4")):
        Jn("s43.band.%s" % r, "e213A_scores", ["arms", "A", "bands", r], "{:.0f}", p, "registered band, %", scale=100.0)
    Jn("s43.band.w", "e213A_scores", ["arms", "A", "band_w"], "{:.2f}", p, "registered band, W")
    T("s43.90", "e213A_note2", "PASS if at least 90% of its scored cases or points pass", "90", "and a rule passes at 90%")
    T("s43.power", "e213B_note3", "on arm B alone it is weak, 0.24-0.50", "0.24-0.50", "arm B alone has a power of only 0.24-0.50")
    p = "first card command 06:37:09 PST, 105 of 105 runs in 42.83 card-minutes, board peak 64.22 W"
    T("s43.a.fcc", "e213A_readme", "The session's first card command at 06:37:09", "06:37:09", p)
    T("s43.a.runs", "e213A_readme", "105 of 105 runs", "105", p)
    T("s43.a.runs2", "e213A_readme", "105 of 105 runs", "105", p)
    T("s43.a.cm", "e213A_readme", "| 42.83 (planned 46.3", "42.83", p)
    T("s43.a.peak", "e213A_readme", "64.22 W at 07:12:07", "64.22", p)
    T("s43.b.stop1", "e213_a2", "(06:39:56 PST, no card command)", "06:39:56", "Its first try stopped at its kit's identity gate at 06:39:56 PST")
    q = ("at 15:07:01 PST, \"Firmware revisions query was a false positive. It should have never been forbidden. Reading operations and firmware "
         "are always allowed.\" and at 15:09:49 PST, \"Yeah, fix the corresponding guards. I don't want to modify firmware, but commands which read "
         "firmware should be fine.\"")
    T("s43.a2.day", "e213_a2", "His words, verbatim, Sun 15 Nov 2026", "15", "under the owner's rulings of Sun 15 Nov, verbatim")
    T("s43.a2.t1", "e213_a2", q, "15:07:01", "verbatim: at 15:07:01 PST, \"Firmware")
    T("s43.a2.t2", "e213_a2", q, "15:09:49", "allowed.\" and at 15:09:49 PST, \"Yeah")
    T("s43.a2.quote", "e213_a2", q, q, q, "the owner's rulings, verbatim")
    T("s43.b.fw", "e213B_readme", "at 2026-11-18 15:13:25 PST", "15:13:25", "The read, at 15:13:25 PST, was EQUAL to the lab's earlier record in all seven fields")
    T("s43.a3.ratio", "e213_a3", "drew 1.26-1.72x MM1-v3's frozen W over idle", "1.26-1.72", "gemmLnc drawing 1.26-1.72 times MM1-v3's W over idle")
    q = "In the registered order a trip there costs most of the session"
    T("s43.a3.quote", "e213_a3", q, q, q, "the amendment's words")
    p = "The session (15:15:28-15:45:12 PST): 79 of 85 runs in 29.74 card-minutes"
    T("s43.b.sess", "e213B_readme", "session 15:15:28-15:45:12 PST", "15:15:28-15:45:12", p)
    T("s43.b.79", "e213B_readme", "(79 of 85 runs", "79", p)
    T("s43.b.85", "e213B_readme", "(79 of 85 runs", "85", p)
    T("s43.b.cm", "e213B_readme", "| 29.74 (planned 32.5", "29.74", p)
    T("s43.b.079", "e213B_readme", "During run 079 (k37, gemmLnc3x1x3 fp32 random", "079", "in run 079 (k37, gemmLnc3x1x3 fp32)")
    p = ("the stop left only runs 080-085 unstarted, where in the registered order the same stop, at k37's run 40, would have started nothing "
         "further: k38 and k39 (runs 41-42), the middle tie and all of pass 2 (runs 43-85) unrun")
    T("s43.a3.lost", "e213B_readme", "runs 080-085 (k38 and k39 in pass 1; k39, k38, k37 and k40 in pass 2)", "080-085", p)
    T("s43.a3.run40", "e213_a3", "a stop at k37 (run 40) starts nothing further", "40", p)
    T("s43.a3.r4142", "e213_a3", "so k38 and k39 (runs 41-42), the middle tie and **all of pass 2** (runs 43-85)", "41-42", p)  # report-v2-fix (L8)
    T("s43.a3.pass2", "e213_a3", "all of pass 2 (runs 43-85)", "43-85", p)
    q = "STOP: board 72.24 W above 72 W on 3 samples in a row: nothing further started"
    T("s43.b.stopq", "e213B_readme", q, q, q, "the session log's words")
    # the verdicts table
    p = "| T1-T3, cycles and seconds per case | PASS 81/84, 82/84, 81/84 | PASS 31/31 each | - |"
    for i, tok in enumerate(("81/84", "82/84", "81/84")):
        T("s43.v.t.%d" % i, "e213A_txt", "T1 PASS 81/84; T2 PASS 82/84; T3 PASS 81/84", tok, p)
    T("s43.v.tb", "e213B_txt", "T1 PASS 31/31; T2 PASS 31/31; T3 PASS 31/31", "31/31", p)
    p = "| E1-E3, joules per point | PASS 82/87, 82/87, 81/87 | PASS 36/38 each | - |"
    for i, tok in enumerate(("82/87", "82/87", "81/87")):
        T("s43.v.e.%d" % i, "e213A_txt", "E1 PASS 82/87; E2 PASS 82/87; E3 PASS 81/87", tok, p)
    T("s43.v.eb", "e213B_txt", "E1 PASS 36/38; E2 PASS 36/38; E3 PASS 36/38", "36/38", p)
    p = "| E4, J at rest with the seconds forecast | FAIL 78/87 (79 needed) | PASS 36/38 | - |"
    T("s43.v.e4a", "e213A_txt", "E4 FAIL 78/87", "78/87", p)
    T("s43.v.e4n", "e213A_note2", "passes 78 of 87 points, and its 90% rule needs 79", "79", p)
    T("s43.v.e4b", "e213B_txt", "E4 PASS 36/38", "36/38", p)
    hrows = [("wall cycles, head to head", "H1", "HP1"), ("counter's mean", "H2", "HP2"), ("seconds", "H3", "HP3"),
             ("J over idle given the seconds", "H4", "HP4"), ("J over idle with the seconds forecast", "H5", "HP5")]
    txtA = norm(R.text("e213A_txt"))
    txtB = norm(R.text("e213B_txt"))
    txtP = norm(R.text("e213P_txt"))
    for name, h, hp in hrows:
        ma = re.search(re.escape(h) + r" (MM1-v3 BETTER|NOT DECIDED|MM1-v2 BETTER) \(v3 (\d+) / v2 (\d+) / ties (\d+)", txtA)
        mb = re.search(re.escape(h) + r" (MM1-v3 BETTER|NOT DECIDED|MM1-v2 BETTER) \(v3 (\d+) / v2 (\d+) / ties (\d+)", txtB)
        mp = re.search(re.escape(hp) + r" (MM1-v3 BETTER) \((\d+/\d+/\d+)", txtP)
        row = (f"| {name} | {ma.group(1)} {ma.group(2)}/{ma.group(3)}/{ma.group(4)} | {mb.group(1)} {mb.group(2)}/{mb.group(3)}/{mb.group(4)} | "
               f"{mp.group(1)} {mp.group(2)} |")
        for k, m, pin in (("a", ma, "e213A_txt"), ("b", mb, "e213B_txt")):
            lit = m.group(0)
            for i in (2, 3, 4):
                T(f"s43.v.{h}.{k}.{i}", pin, lit, m.group(i), row)
        T(f"s43.v.{hp}", "e213P_txt", mp.group(0), mp.group(2), row)
        G.rows.append(row)
    # the two footings
    foot = [("wall cycles an op, per case", "wall", "| wall cycles an op, per case | 4.27% (+1.19%; n 115) | 8.90% (+4.23%; n 115) |", False),
            ("the counter's mean, per case", "mean", "| counter's mean, per case | 5.68% (+1.17%; n 115) | 9.10% (+4.16%; n 115) |", False),
            ("J over idle given the seconds, 3 W and above", "Jg", "| J over idle given the seconds (3 W and above) | 15.36% (+1.77%; n 103) | 16.36% (+4.24%; n 102) |", False),
            ("the same without the seven gemmLnc points (post hoc)", "Jg", "| post hoc: J over idle given the seconds without the gemmLnc points | 3.91% (-1.99%; n 96) | 7.34% (+0.69%; n 95) |", True),
            ("J with the card at rest given the seconds", "Jr", "| J with the card at rest given the seconds | 5.86% (+0.97%; n 125) | 6.16% (+1.75%; n 124) |", False)]
    for name, q, lit, nolnc in foot:
        toks = re.findall(r"(\d+\.\d+)% \(", lit)
        s3 = e213_stat(cache, "P", "v3", q, "fm", nolnc)
        s2 = e213_stat(cache, "P", "v2", q, "fm", nolnc)
        row = f"| {name} | {toks[0]}% | {toks[1]}% | {s3['rms']:.2f}% | {s2['rms']:.2f}% |"
        T(f"s43.f.{q}.{int(nolnc)}.notes_v3", "e213B_note3", lit, toks[0], row)
        T(f"s43.f.{q}.{int(nolnc)}.notes_v2", "e213B_note3", lit, toks[1], row)
        E13(f"s43.f.{q}.{int(nolnc)}.d3", "P", "v3", q, "rms", row, no_lnc=nolnc)
        E13(f"s43.f.{q}.{int(nolnc)}.d2", "P", "v2", q, "rms", row, no_lnc=nolnc)
        G.rows.append(row)
    # the mf check: this report's code on measured / forecast - 1 reproduces the notes (a desk entry the check recomputes)
    for q, lit, nolnc in (("wall", "| wall cycles an op, per case | 4.27% (+1.19%; n 115) | 8.90% (+4.23%; n 115) |", False),
                          ("Jg", "| J over idle given the seconds (3 W and above) | 15.36% (+1.77%; n 103) | 16.36% (+4.24%; n 102) |", False),
                          ("Jg", "| post hoc: J over idle given the seconds without the gemmLnc points | 3.91% (-1.99%; n 96) | 7.34% (+0.69%; n 95) |", True)):
        toks = re.findall(r"(\d+\.\d+)% \(", lit)
        row = [r for r in G.rows if r.startswith("| " + {"wall": "wall cycles an op", "Jg": ("the same without" if nolnc else "J over idle given the seconds, 3 W")}[q])][0]
        E13(f"s43.mf.{q}.{int(nolnc)}.v3", "P", "v3", q, "rms", row, conv="mf", no_lnc=nolnc)
        E13(f"s43.mf.{q}.{int(nolnc)}.v2", "P", "v2", q, "rms", row, conv="mf", no_lnc=nolnc)
    p = "a point measured at 1.68 times its forecast reads +68% one way and -40% the other"
    r087 = rat["a087"]["ratio"]
    D("s43.a087.r", r087, "{:.2f}", p, "ratio", {"points": ["a087"], "stat": "one"}, ["e213A_scores"], "measured / forecast, desk")
    D("s43.a087.mf", 100 * (r087 - 1), "{:+.0f}", p, "ratio", {"points": ["a087"], "stat": "mf_pct"}, ["e213A_scores"], "measured / forecast - 1, %, desk")
    D("s43.a087.fm", 100 * (1 / r087 - 1), "{:+.0f}", p, "ratio", {"points": ["a087"], "stat": "fm_pct"}, ["e213A_scores"], "forecast / measured - 1, %, desk")
    p = "but they drew 1.15 to 1.80 times the J over idle MM1-v3 forecast given the seconds"
    RAT("s43.lnc.min", ["a075", "a079", "a082", "a086", "a087", "k37", "k40"], "min", "{:.2f}", p)
    RAT("s43.lnc.max", ["a075", "a079", "a082", "a086", "a087", "k37", "k40"], "max", "{:.2f}", p)
    p = "slower than forecast by 11.6% to 29.5% (the scorer's measured / forecast - 1); masks of one shire count ran up to 13.2% apart"
    T("s43.tm.0", "e213A_note2", "every one slower than forecast (+11.6% to +29.5%)", "11.6", p)
    T("s43.tm.1", "e213A_note2", "every one slower than forecast (+11.6% to +29.5%)", "29.5", p)
    D("s43.masks", 100 * masks_spread, "{:.1f}", p, "masks", {"stat": "max"}, ["e213A_scores"], "the measured spread of wall cycles among masks of one shire count, %, desk")
    p = "E4 failed by one point: 78 of 87 against 79 needed, its nearest misses 0.15 and 0.83 points past the band"
    for i, tok in enumerate(("78", "87", "79")):
        T("s43.e4.%d" % i, "e213A_note2", "passes 78 of 87 points, and its 90% rule needs 79", tok, p)
    T("s43.e4.n0", "e213A_note2", "a053 (0.15 points past the band) and a054 (0.83 points past the band)", "0.15", p)
    T("s43.e4.n1", "e213A_note2", "a053 (0.15 points past the band) and a054 (0.83 points past the band)", "0.83", p)
    p = "seals of E213 (76f0b2f4 and d622ce16) are registered (8e91dda6; d8404ef2 with its correction f3de54a2)"
    T("s43.seal.0", "seal_e213_1", "76f0b2f4", "76f0b2f4", p)
    T("s43.seal.1", "seal_e213_2", "d622ce16", "d622ce16", p)

    # ---------------- 4.4
    T("s44.post", "e214_reg", "posted the proposal at 09:29:50 PST", "09:29:50", "registered by its post at 09:29:50 PST Wed 18 Nov")
    p = ("rgm136 unchanged over 360 arms and an anchor in seven sessions on aifoundry1's two cards (card 1 at 600 MHz, card 0 at low power under "
         "52 W)")
    lit = "over 360 arms and an anchor in seven sessions on aifoundry1's two cards (card 1 at 600 MHz, card 0 at low power under 52 W)"
    for i, tok in enumerate(("360", "600", "52")):
        T("s44.arms.%d" % i, "e214_reg", lit, tok, p)
    p = "its forecast sealed (27bf4e19, and a second seal 804e269b, registered in b2230d68)"
    T("s44.seal.0", "e214_reg", "27bf4e19", "27bf4e19", p)
    T("s44.seal.1", "seal_e214", "804e269b", "804e269b", p)
    q = "\"Focus on the matmul above everything else, and use all the cards without restriction.\""
    T("s44.quote", "e214_reg", "Focus on the matmul above everything else, and use all the cards without restriction.", q.strip('"'), q, "the owner's words as the post relays them, verbatim")
    p = "All seven sessions ran full: 622 runs in 258.28 card-minutes"
    D("s44.runs", e214_runs, "{:d}", p, "sum_runs", {"pins": sumin14}, sumin14, "runs, desk sum of the seven data READMEs")
    D("s44.cm", e214_cm, "{:.2f}", p, "sum_cm", {"pins": sumin14}, sumin14, "card-minutes, desk sum of the seven data READMEs")
    if "e214u_readme" in PINS:
        U, UR = R.json("e214u_scores"), "e214u_readme"
        p = "forecast all 593 of E214's runs"
        T("s44u.runs", "e214u_decl", "**593 runs** ({'anchor': 38, 'arm': 555}) in E214's seven sessions", "593", p)
        p = "(10:42:28, 10:46:14 and 10:49:30 PST Thu 19 Nov)"
        T("s44u.t1", UR, "| 1. DECLARED (before any E214 measurement) | 10:42:28 written", "10:42:28", p)
        T("s44u.t2", UR, "| 2. FORECAST (the frozen predictors, unchanged) | 10:44-10:46:14 written", "10:46:14", p)
        T("s44u.t3", UR, "| the scorer frozen (after a stand-in code test) | 10:49:30 |", "10:49:30", p)
        # report-v2-fix (finding L1): each model's own no-twin set, as the scores have them
        p = ("On the cases whose configuration none of a model's own training points shares (MM1-v3.1's 425 cases, MM1-v3's 429 and MM1-v2's "
             "462 in wall cycles; 425, 426 and 372 in J over idle), MM1-v3.1 read 6.66% in wall cycles and 5.48% in J over idle given the "
             "measured seconds, MM1-v3 6.52% and 5.55%, MM1-v2 8.06% and 7.91%")
        Jn("s44u.n", "e214u_scores", ["tables_per_case", "v31", "wall", "pooled", "no_twin", "n"], "{:d}", p, "cases, no twin")
        Jn("s44u.v3.nw", "e214u_scores", ["tables_per_case", "v3", "wall", "pooled", "no_twin", "n"], "{:d}", p, "cases, no twin")
        Jn("s44u.v2.nw", "e214u_scores", ["tables_per_case", "v2", "wall", "pooled", "no_twin", "n"], "{:d}", p, "cases, no twin")
        for m in ("v31", "v3", "v2"):
            Jn(f"s44u.{m}.ne", "e214u_scores", ["tables_per_case", m, "E1", "pooled", "no_twin", "relative", "n"], "{:d}", p, "points, no twin")
        for m in ("v31", "v3", "v2"):
            Jn(f"s44u.{m}.wall", "e214u_scores", ["tables_per_case", m, "wall", "pooled", "no_twin", "rms_pct"], "{:.2f}", p, "unread, rms %")
            Jn(f"s44u.{m}.e1", "e214u_scores", ["tables_per_case", m, "E1", "pooled", "no_twin", "relative", "rms_pct"], "{:.2f}", p, "unread, rms %")
        p = ("fail T1 and T3 (wall cycles and seconds) on both cards, 195 of 224 and 175 of 201 cases within their 10% and 11% bands against "
             "90% needed, and E4 on card 0")
        T("s44u.f1", UR, "| T1 | 10% | **FAIL** 195/224 (87.1%) | 11% | **FAIL** 175/201 (87.1%) |", "195", p)
        T("s44u.f2", UR, "| T1 | 10% | **FAIL** 195/224 (87.1%) | 11% | **FAIL** 175/201 (87.1%) |", "224", p)
        T("s44u.f3", UR, "| T1 | 10% | **FAIL** 195/224 (87.1%) | 11% | **FAIL** 175/201 (87.1%) |", "175", p)
        T("s44u.f4", UR, "| T1 | 10% | **FAIL** 195/224 (87.1%) | 11% | **FAIL** 175/201 (87.1%) |", "201", p)
        T("s44u.f5", UR, "| T1 | 10% | **FAIL** 195/224 (87.1%) | 11% | **FAIL** 175/201 (87.1%) |", "10", p)
        T("s44u.f6", UR, "| T1 | 10% | **FAIL** 195/224 (87.1%) | 11% | **FAIL** 175/201 (87.1%) |", "11", p)
        T("s44u.f7", UR, "a rule passes when at least 90% of its cases pass", "90", p)
        T("s44u.f8", UR, "| E4 | 10% | **PASS** 243/265 (91.7%) | 10% | **FAIL** 179/209 (85.6%) |", "4", p)
        Jn("s44u.h.n", "e214u_scores", ["head_to_head", "MM1-v3.1 vs MM1-v3", "H1", "pooled", "n"], "{:d}",
           "Head to head, over all 518 cases, twins included", "cases, twins included")  # report-v2-fix (L1)
        p = "(wall cycles closer at 61 cases, farther at 71, with 386 ties)"
        Jn("s44u.h.c", "e214u_scores", ["head_to_head", "MM1-v3.1 vs MM1-v3", "H1", "pooled", "closer_A"], "{:d}", p, "cases")
        Jn("s44u.h.f", "e214u_scores", ["head_to_head", "MM1-v3.1 vs MM1-v3", "H1", "pooled", "closer_B"], "{:d}", p, "cases")
        Jn("s44u.h.t", "e214u_scores", ["head_to_head", "MM1-v3.1 vs MM1-v3", "H1", "pooled", "ties"], "{:d}", p, "cases")
        p = "7.76% against 28.05% for the null at the new kinds' 33 cases (closer at 29, farther at 3, p = 2.6e-06)"
        Jn("s44u.q1.m", "e214u_scores", ["part_S", "v31", "Q1", "model", "rms_pct"], "{:.2f}", p, "unread, rms %")
        Jn("s44u.q1.n", "e214u_scores", ["part_S", "v31", "Q1", "N", "rms_pct"], "{:.2f}", p, "unread, rms %")
        Jn("s44u.q1.k", "e214u_scores", ["part_S", "v31", "Q1", "cases"], "{:d}", p, "cases")
        Jn("s44u.q1.c", "e214u_scores", ["part_S", "v31", "Q1", "closer_model"], "{:d}", p, "cases")
        Jn("s44u.q1.f", "e214u_scores", ["part_S", "v31", "Q1", "closer_N"], "{:d}", p, "cases")
        T("s44u.q1.p", UR, "MM1-v3.1 closer in 29, N in 3, 1 tie; p = 2.6e-06", "2.6e-06", p)
        p = "45 of the 55 cases outside T1's band are over-forecasts, mostly at mid-depth shapes (KB 2-16, NB above 4) on both cards"
        T("s44u.m.0", UR, "45 of the 55 misses are over-forecasts", "45", p)
        T("s44u.m.1", UR, "45 of the 55 misses are over-forecasts", "55", p)
        T("s44u.m.2", UR, "mostly mid-depth shapes (KB 2-16, NB above 4) on both cards", "2-16", p)
        T("s44u.m.3", UR, "mostly mid-depth shapes (KB 2-16, NB above 4) on both cards", "4", p)
        p = "with switch counts made for E214's 20 new tile kinds"
        T("s44u.k20", UR, "group S: E214's 20 new tile kinds, 33 arms, 54 runs", "20", p)

    # ---------------- 4.5
    G.git("s45.reg", "4cb2c2ad", "06:32:24", "registered 4cb2c2ad at 06:32:24 PST Thu 19 Nov")
    T("s45.60", "e215_reg", "MM1-v3.1's own 60-point list", "60", "arm A's 60 points on aifoundry3 card 0")
    T("s45.land", "e215_reg", "committed 23:09:13 PST Wed 18 Nov 2026", "23:09:13", "(2c971828, Wed 23:09:13 PST)")
    p = ("32 by MM1-v3.1's declared point rule (families P, C and R), and 20 of family L (layouts) and 8 of family S (data patterns) chosen "
         "beside them post hoc")
    T("s45.32", "e215_reg", "registered (P, C, R) 32 points and 32 time cases", "32", p)
    T("s45.L", "e215_reg", "L 20, P 12, C 10, R 10, S 8", "20", p)
    T("s45.S", "e215_reg", "L 20, P 12, C 10, R 10, S 8", "8", p)
    p = "arm B's 30 points on aifoundry1 card 1 (8 of family L and 4 of family S post hoc)"
    T("s45.b30", "e215_reg", "30 points chosen here by the same rule", "30", p)
    T("s45.bL", "e215_reg", "(L 8, S 4; section 3)", "8", p)
    T("s45.bS", "e215_reg", "(L 8, S 4; section 3)", "4", p)
    T("s45.famR", "e215_reg", "**R** the two-edge retention at 36-140 MB", "36-140", "R the two-edge retention at 36-140 MB",
      "the registration's family R")  # report-v2-fix (L7: the families defined)
    p = "(arm A: 10% in wall cycles, 13% in J over idle given the seconds)"
    T("s45.t1", "e215_reg", "| T1 | cycles an op, the wall, per case | 10% |", "10", p)
    T("s45.e1", "e215_reg", "| E1 | J over idle given the measured seconds, per point (watts under 3 W) | 13% |", "13", p)
    T("s45.90", "e215_reg", "PASS if at least 90% of its scored cases or points pass", "90", "PASS at 90%, per arm and group")
    q = "\"A NOT DECIDED is the expected reading whichever model is better.\""
    T("s45.quote", "e215_reg", "A NOT DECIDED is the expected reading whichever model is better.", q.strip('"'), q, "the registration's words")

    # ---------------- 4.6, 4.7
    p = "repeated to 0.41% rms in the counter's mean, 0.38% in wall cycles and 1.16% in joules over idle"
    Jn("s46.mean", "v1_numbers", ["repeat", "E208", "cyc_op_mean", "rms_pct"], "{:.2f}", p, "measured, post hoc")
    Jn("s46.wall", "v1_numbers", ["repeat", "E208", "cyc_op_max", "rms_pct"], "{:.2f}", p, "measured, post hoc")
    Jn("s46.j", "v1_numbers", ["repeat", "E208", "J_op", "rms_pct"], "{:.2f}", p, "measured, post hoc")
    T("s46.85", "v1_readme", "The same 85-run schedule", "85", "The same 85-run schedule, run twice five hours apart")
    seals_v1 = [("| E206 arm B | bc750c73, 9db8898a | cb25db36, c931b3d8 |", ["bc750c73", "9db8898a"]), ("| E207 | 26a17d64 | 221a233f |", ["26a17d64"]),
                ("| E208 | 087fa8fd | d005dc53 |", ["087fa8fd"]), ("| E210 | 81a84eb6 | 75ecdd29 |", ["81a84eb6"]),
                ("| E211 | 7e5a361e | 51d74428 |", ["7e5a361e"])]
    for lit, toks in seals_v1:
        for tk in toks:
            T("s47.v1.%s" % tk, "v1_readme", lit, tk, lit, "as the first version lists it")
    T("s47.e209", "v1_readme", "2adc7fd3", "2adc7fd3", "| E209 | 2adc7fd3 (posted after its session, before its data commit: REPORTED) | d6d62660 |", "as the first version lists it")
    p = ("| E212 | 4d77f137 (the post); 8f2df483 (five sessions); 6842eca5 and 0dca417d (the re-run S3) | c83a29d1; a1602b0d; fcbf60c4, "
         "d8dc4897 |")
    T("s47.e212.0", "e212_reg", "4d77f137", "4d77f137", p)
    T("s47.e212.1", "seal_e212_1", "8f2df483", "8f2df483", p)
    T("s47.e212.2", "seal_e212_2", "6842eca5", "6842eca5", p)
    T("s47.e212.3", "seal_e212_3", "0dca417d", "0dca417d", p)
    p = "| E213 | 76f0b2f4 (both arms); d622ce16 (arm B; for arm A posted during its session, REPORTED) | 8e91dda6; d8404ef2, f3de54a2 |"
    T("s47.e213.0", "seal_e213_1", "76f0b2f4", "76f0b2f4", p)
    T("s47.e213.1", "seal_e213_2", "d622ce16", "d622ce16", p)
    p = "| E214 | 27bf4e19 (the post); 804e269b | 95eb8069; b2230d68 |"
    T("s47.e214.0", "e214_reg", "27bf4e19", "27bf4e19", p)
    T("s47.e214.1", "seal_e214", "804e269b", "804e269b", p)
    T("s47.e215", "seal_e215", "24cba7f5", "24cba7f5", "| E215 | 24cba7f5 (all 90 points, both arms, before either arm's first card command) | 18398ed2 |")

    # ---------------- 5
    p = ("read 1.87% of D (the data-dependent power, random minus zeros; REPORTED), against 16.19% for the bit-flip price with one scale, "
         "19.71% for the nearest measured kind and 47.48% for the raw bit flips")
    for r in ("R1", "R3L", "R4", "R3"):
        Jn("s5.e210.%s" % r, "v1_numbers", ["switch", "routes", r, "rms_over_D_pct"], "{:.2f}", p, "blind, REPORTED, % of D")
    Jn("s5.e210.R2", "v1_numbers", ["switch", "routes", "R2", "rms_over_D_pct"], "{:.2f}", "(21.22% on 5 cases)", "blind, REPORTED, % of D")
    Jn("s5.e210.R2n", "v1_numbers", ["switch", "routes", "R2", "n"], "{:d}", "(21.22% on 5 cases)", "cases")
    T("s5.179", "counts_readme", "179 bench points in the tables", "179", "179 bench points of the lab's RTL bench")
    p = "(13 fp32 kinds at a GEMM's accumulator states, 7 fp16 and 6 int8 kinds at the launch points)"
    lit = "13 fp32 kinds at a GEMM's accumulator states (S1 for KB 1 and S2 for KB >= 2, as E210), 7 fp16 and 6 int8 kinds at the harness's launch points"
    for i, tok in enumerate(("13", "7", "6")):
        T("s5.kinds.%d" % i, "counts_readme", lit, tok, p)
    p = "(Q1, 42 cases: E212's plan tiles in 29 cases, E206's and E207's real tiles in 13)"
    Jn("s5.q1.n", "unread_sw", ["pass_rule_against_N", "Q1", "n_cases"], "{:d}", p, "cases")
    Jn("s5.q1.e212", "unread_sw", ["groups", "A", "source=E212", "V3", "Q1_cases", "n"], "{:d}", p, "cases")
    D("s5.q1.e206", sum(R.json("unread_sw")["groups"]["A"]["source=" + s]["V3"]["Q1_cases"]["n"] for s in ("E206A", "E206B", "E207")), "{:d}", p,
      "sum_json", {"pin": "unread_sw", "pointers": [["groups", "A", "source=" + s, "V3", "Q1_cases", "n"] for s in ("E206A", "E206B", "E207")]},
      ["unread_sw"], "cases, desk sum")
    p = "MM1-v3 6.83% rms against 24.97% for the null N"
    T("s5.q1.v3", "unread_sw_readme", "MM1-v3 with the new counts reads 6.83% rms (+2.61), against N's 24.97% (-16.04)", "6.83", p)
    T("s5.q1.N", "unread_sw_readme", "MM1-v3 with the new counts reads 6.83% rms (+2.61), against N's 24.97% (-16.04)", "24.97", p)
    p = "closer on 35 cases and N on 5, with 2 ties (exact sign test p = 1.4e-06)"
    lit = "MM1-v3 is closer on 35 cases and N on 5, with 2 ties (exact sign test p = 1.4e-06)"
    for i, tok in enumerate(("35", "5", "2", "1.4e-06")):
        T("s5.q1.s.%d" % i, "unread_sw_readme", lit, tok, p)
    Jn("s5.q2.n", "unread_sw", ["pass_rule_against_N", "Q2", "n_cases"], "{:d}", "(Q2, E210's metric, 29 cases)", "cases")
    p = "5.70% of D against N's 21.64%, closer on 23 of 29 (p = 0.0023)"
    T("s5.q2.v3", "unread_sw_readme", "5.70% of D rms (+1.93), against N's 21.64% (-12.38)", "5.70", p)
    T("s5.q2.N", "unread_sw_readme", "5.70% of D rms (+1.93), against N's 21.64% (-12.38)", "21.64", p)
    for i, tok in enumerate(("23", "29", "0.0023")):
        T("s5.q2.s.%d" % i, "unread_sw_readme", "MM1-v3 is closer on 23 of 29 (p = 0.0023)", tok, p)
    p = "fp32 3.80% (gate-level counts), fp16 8.20% (counts estimated from fp32's ratio), int8 10.57%"
    for f, tok in (("fp32", "3.80"), ("fp16", "8.20"), ("int8", "10.57")):
        Jn("s5.fmt.%s" % f, "unread_sw", ["groups", "A", "fmt=" + f, "V3", "Q1_cases", "rms_pct"], "{:.2f}", p, "unread, rms %")
    p = "the cleanest part, E212 a2c0-S2's 8 runs, read by none of MM1-v3's design or fitting steps, reads 1.34% in Q1"
    T("s5.clean.0", "unread_sw_readme", "The cleanest part is E212 a2c0-S2's 8 runs", "8", p)
    Jn("s5.clean.1", "unread_sw", ["groups", "A", "card=aifoundry2 card 0", "V3", "Q1_cases", "rms_pct"], "{:.2f}", p, "unread, rms %")
    p = "on aifoundry3's 10 points it applies to, MM1-v1 read 5.98% and MM1-v3 7.82%"
    T("s5.v1.0", "unread_sw_readme", "which applies on aifoundry3's 10 E206/E207 points", "10", p)
    T("s5.v1.1", "unread_sw_readme", "MM1-v1 reads 5.98% and MM1-v3 7.82%", "5.98", p)
    T("s5.v1.2", "unread_sw_readme", "MM1-v1 reads 5.98% and MM1-v3 7.82%", "7.82", p)

    # ---------------- 6
    T("s62.179", "counts_readme", "179 bench points in the tables", "179", "the 179 bench counts (section 5)")
    p = "1,906 time points and 1,832 energy points through E213's two arms"
    T("s6.data.0", "v31_readme", "1906 time points and 1832 energy points", "1,906", p)
    T("s6.data.1", "v31_readme", "1906 time points and 1832 energy points", "1,832", p)
    p = "| E213's family C and BK: T5r closer at 10 cases, tC at 10 (p 1.0000) |"
    lit = "tC closer 10, T5r closer 10, exact sign test p 1.0000"
    for i, tok in enumerate(("10", "10", "1.0000")):
        T("s6.i8.%d" % i, "v31_readme", lit, tok, p)
    p = "NOT DECIDED, then T5r by its pooled LOEO (4.29% against 4.44%)"
    T("s6.i8b.0", "v31_readme", "pooled LOEO wall rms: T5r 4.29%, tC 4.44%", "4.29", p)
    T("s6.i8b.1", "v31_readme", "pooled LOEO wall rms: T5r 4.29%, tC 4.44%", "4.44", p)
    # report-v2-fix (findings L4 and M6): item 3's scores labelled unidentified; item 4's LOLO read with the unidentified fold named
    p = ("| LOEO wall over the touched points: G0 6.58% against 9.19-24.40%, those three scores unidentified (the training cost is flat in the "
         "E213 fold) |")
    T("s6.i3.0", "v31_readme", "G0 6.58%, Gplace 24.40%", "6.58", p)
    T("s6.i3.1", "v31_readme", "Gcoop 9.19%", "9.19", p)
    T("s6.i3.2", "v31_readme", "G0 6.58%, Gplace 24.40%", "24.40", p)
    T("s6.i3.u", "v31_readme", "Item 3's scores of Gplace, Goperand and Gcoop are unidentified", "unidentified", p, "the README's label, quoted")
    p = ("| T7: LOLO 14.40%, pooled LOEO 6.20%; n/32: 89.78% and 4.29%, its LOLO set by the compact fold, where eta is not identified (118.2%; "
         "6.17% with eta at its neutral 0) |")
    lit = "T7 14.40% / 6.20%, demand 92.50% / 4.39%, n32 89.78% / 4.29%"
    for i, tok in enumerate(("14.40", "6.20", "89.78", "4.29")):
        T("s6.i4.%d" % i, "v31_readme", lit, tok, p)
    by = ["item4_LOLO_by_class_each_form"]
    e0 = ["item4_LOLO_compact_eta_not_identified_post_hoc", "n32", "compact_rms_eta_0_post_hoc", "rms_pct"]
    Jn("s6.i4.c", "v31_reported", by + ["n32", "compact"], "{:.1f}", p, "LOLO, compact class, n/32, eta as fitted (not identified), %")
    Jn("s6.i4.e0", "v31_reported", e0, "{:.2f}", p, "the same with eta at its neutral 0, post hoc, REPORTED, %")
    p = ("| n/32: T7 failed its pooled LOEO condition, and class by class T7 was worse (compact 12.96% against 6.17% at eta 0, other 18.66% "
         "against 6.47%, spread 14.32% against 6.55%) |")
    Jn("s6.i4.d0", "v31_reported", by + ["T7", "compact"], "{:.2f}", p, "LOLO by class, T7, %")
    Jn("s6.i4.d1", "v31_reported", e0, "{:.2f}", p, "n/32's compact class with eta at its neutral 0, post hoc, REPORTED, %")
    Jn("s6.i4.d2", "v31_reported", by + ["T7", "other"], "{:.2f}", p, "LOLO by class, T7, %")
    Jn("s6.i4.d3", "v31_reported", by + ["n32", "other"], "{:.2f}", p, "LOLO by class, n/32, %")
    Jn("s6.i4.d4", "v31_reported", by + ["T7", "spread"], "{:.2f}", p, "LOLO by class, T7, %")
    Jn("s6.i4.d5", "v31_reported", by + ["n32", "spread"], "{:.2f}", p, "LOLO by class, n/32, %")
    p = "Its pooled layout-held-out error (14.40% against n/32's 89.78%)"
    T("s63.lolo.0", "v31_readme", lit, "14.40", p)
    T("s63.lolo.1", "v31_readme", lit, "89.78", p)
    T("s6.i1", "v31_readme", "E1t 5.48%", "5.48", "| LOEO W given t: E1t 5.48% |")
    T("s6.i1b", "v31_readme", "E1b's all-data b2, d2 at their bound 0: True", "0", "| E1t (the L2 line energy at its bound 0) |")
    v31rows = [("LOEO, wall cycles", "LOEO", "all", None), ("LOCO, wall cycles", "LOCO", "all", None),
               ("rgm211 left out, wall cycles", "LEAVE rgm211", "all", None), ("the E212 fold, wall cycles", "LOEO", "exp E212", None),
               ("the E213 fold, wall cycles", "LOEO", "exp E213", None), ("LOEO, W over idle given t (3 W and above)", "LOEO", "all", "W given t (>= 3 W)"),
               ("LOCO by the anchor route, W over idle given t", "LOCO (anchor route)", "all", "W given t (>= 3 W)"),
               ("LOCO by the fallback route, W over idle given t", "LOCO (fallback route)", "all", "W given t (>= 3 W)")]
    H = R.json("v31_holdout")
    v31_fig = []
    for name, fam, setk, q in v31rows:
        a = H["time" if q is None else "energy"]["v3.1"][fam][setk]["no_twin"]
        b = H["time" if q is None else "energy"]["v3 refitted"][fam][setk]["no_twin"]
        if q is not None:
            a, b = a[q], b[q]
        row = f"| {name} | {a['rms_pct']:.2f}% (n {a['n']}) | {b['rms_pct']:.2f}% |"
        k = "s63." + re.sub(r"[^A-Za-z0-9]+", "_", name).strip("_")
        V31(k + ".v31", "v3.1", fam, setk, q, row)
        Jn(k + ".n", "v31_holdout", ["time" if q is None else "energy", "v3.1", fam, setk, "no_twin"] + ([] if q is None else [q]) + ["n"], "{:d}", row, "points")
        V31(k + ".v3r", "v3 refitted", fam, setk, q, row)
        G.rows.append(row)
        v31_fig.append((name, a["rms_pct"], b["rms_pct"]))
    p = "(4.723% against 4.723%: equal, not lower)"
    T("s63.acc.0", "v31_readme", "LOEO wall (no twin) v3.1 4.723% against v3 refitted 4.723%", "4.723", p)
    T("s63.acc.1", "v31_readme", "LOEO wall (no twin) v3.1 4.723% against v3 refitted 4.723%", "4.723", p)
    p = "(a held-out card's W over idle by the declared anchor route, 10.92% against 8.85%)"
    V31("s63.acc.2", "v3.1", "LOCO (anchor route)", "all", "W given t (>= 3 W)", p)
    V31("s63.acc.3", "v3 refitted", "LOCO (anchor route)", "all", "W given t (>= 3 W)", p)

    # ---------------- 6.5 the two candidate terms
    p = "their sha256 were posted at 09:32:02 and 09:32:47 PST Thu 19 Nov"
    T("s65.post1", "lnc_note", "as post **#1.29** on the owner's coordination thread at **09:32:02 PST**", "09:32:02", p)
    T("s65.post2", "lay_note", "as post **#1.29.1** on the owner's coordination thread at **09:32:47 PST**", "09:32:47", p)
    p = ("each shire issues 1,024 line reads an op step where gemmL issues 192: 832 duplicate reads a shire-op, 26 a minion-op, with the "
         "same distinct lines")
    lit = "(1,024 lines) where gemmL issues 4 and 8 (192 lines). That is **832 duplicate line reads a shire-op** (26 a minion-op)"
    for i, tok in enumerate(("1,024", "192", "832", "26")):
        T("s65.lnc.d%d" % i, "lnc_readme", lit, tok, p)
    p = "the excess sits on the SRAM rail at every point (+2.2 to +8.3 W) and on the NoC rail at the beyond-L2 shapes with NB of 3 or less (+1.9 to +4.5 W)"
    T("s65.lnc.r0", "lnc_readme", "(+2.2 to +8.3 W; 3.6-7.0 nJ a minion-op)", "+2.2", p)
    T("s65.lnc.r1", "lnc_readme", "(+2.2 to +8.3 W; 3.6-7.0 nJ a minion-op)", "+8.3", p)
    T("s65.lnc.r2", "lnc_readme", "with NB ≤ 3 that are served beyond the L2 (+1.9 to +4.5 W", "3", p)
    T("s65.lnc.r3", "lnc_readme", "with NB ≤ 3 that are served beyond the L2 (+1.9 to +4.5 W", "+1.9", p)
    T("s65.lnc.r4", "lnc_readme", "with NB ≤ 3 that are served beyond the L2 (+1.9 to +4.5 W", "+4.5", p)
    p = ("two constants, 254.4 pJ for each duplicate L2 read and 552.1 pJ for each duplicate of a beyond-L2 line on the A panel's first C "
         "block; on the 9 committed gemmLnc points it read 7.99% in W over idle in sample against MM1-v3.1's 32.56%, and held out one point "
         "at a time 9.81%")
    lit = "It adds **254.4 pJ for each duplicate L2 read**, plus **552.1 pJ for each duplicate of a beyond-L2 line on the A panel's first C block**"
    T("s65.lnc.c1", "lnc_readme", lit, "254.4", p)
    T("s65.lnc.c2", "lnc_readme", lit, "552.1", p)
    T("s65.lnc.n9", "lnc_readme", "These are 9 points, one a configuration (12 runs)", "9", p)
    T("s65.lnc.in", "lnc_readme", "In sample: W over idle rms **7.99%**, against MM1-v3.1's **32.56%**", "7.99", p)
    T("s65.lnc.v31", "lnc_readme", "In sample: W over idle rms **7.99%**, against MM1-v3.1's **32.56%**", "32.56", p)
    T("s65.lnc.lopo", "lnc_readme", "Held out: leave one point out 9.81%", "9.81", p)
    p = ("E215's two points at NB 12 and 15 extrapolate from NB of 6 or less, and that the constants include self-heating (3-13% of each "
         "excess)")
    lit = "no fit point has NB above 6, so a024 (NB 15) and a026 (NB 12) extrapolate the 1/NB form from NB of 6 or less"
    T("s65.lnc.nb0", "lnc_note", lit, "12", p)
    T("s65.lnc.nb1", "lnc_note", lit, "15", p)
    T("s65.lnc.nb2", "lnc_note", lit, "6", p)
    T("s65.lnc.sh", "lnc_note", "which prices at 0.24-1.29 W: 3-13% of each excess", "3-13", p)
    p = ("a = -0.0832, where Phi_fresh is the masked walk's fresh DRAM lines a step over its line requests, less the full chip's: exactly zero at "
         "the full mask, and 0.9942 to 1.0139 at E215's 28 subset points")
    T("s65.lay.a", "lay_readme", "| **F1** | a_fresh -0.0832 |", "-0.0832", p)
    T("s65.lay.f0", "lay_readme", "At the 28 subset rows the factor runs 0.9942-1.0139", "0.9942", p)
    T("s65.lay.f1", "lay_readme", "At the 28 subset rows the factor runs 0.9942-1.0139", "1.0139", p)
    T("s65.lay.f2", "lay_readme", "At the 28 subset rows the factor runs 0.9942-1.0139", "28", p)
    p = "from 6.3195% to 6.2480% and the pooled one from 4.7228% to 4.7101%"
    lit = "(v3.1 / F1: LOEO with no twins 4.7228 / 4.7101; LOLO (b) 6.3195 / 6.2480"
    for i, tok in enumerate(("6.3195", "6.2480", "4.7228", "4.7101")):
        T("s65.lay.h%d" % i, "lay_note", lit, tok, p)
    p = "(every mask loads them evenly, max/mean 1.000)"
    T("s65.lay.mm", "lay_note", "fresh lines per memory shire have max/mean **1.000** at every step of every mask", "1.000", p)
    p = ("permuting its feature within a shire count and shape does as well in 92.4% of draws, a count-only control (N1+N2) would have won, "
         "and the gain is within noise (an interval of -0.171 to +0.032 points)")
    T("s65.lay.p", "lay_note", "the placebo's LOLO (b) is at or below F1's in 92.4% of draws", "92.4", p)
    T("s65.lay.n", "lay_note", "N1+N2 = -0.0935 (1 - n/32) + 0.1177 (1 - n/32)^2, which uses no placement information, passes all three keep conditions", "N1+N2", p)
    T("s65.lay.ci0", "lay_note", "95% interval [-0.171, +0.032]", "-0.171", p)
    T("s65.lay.ci1", "lay_note", "95% interval [-0.171, +0.032]", "+0.032", p)

    # ---------------- 7
    p = ("the card drew 1.15 to 1.80 times the J over idle MM1-v3 forecast given the measured seconds, while their cooperative gemmL twins "
         "read 0.97 to 1.04")
    RAT("s7.lnc.min", ["a075", "a079", "a082", "a086", "a087", "k37", "k40"], "min", "{:.2f}", p)
    RAT("s7.lnc.max", ["a075", "a079", "a082", "a086", "a087", "k37", "k40"], "max", "{:.2f}", p)
    RAT("s7.tw.min", ["a006", "a076", "a030", "a083", "k06"], "min", "{:.2f}", p)
    RAT("s7.tw.max", ["a006", "a076", "a030", "a083", "k06"], "max", "{:.2f}", p)
    p = "Without those seven points MM1-v3's J over idle reads 4.08% on both arms, against 9.92% with them"
    E13("s7.nolnc", "P", "v3", "Jg", "rms", p, no_lnc=True)
    E13("s7.withlnc", "P", "v3", "Jg", "rms", p)
    D("s7.masks", 100 * masks_spread, "{:.1f}", "At an equal shire count the layout moves the time by up to 13.2% (E213, family M)", "masks",
      {"stat": "max"}, ["e213A_scores"], "the measured spread of wall cycles among masks of one shire count, %, desk")
    p = ("MM1-v3.1's energy reads 10.92% by the declared anchor route against MM1-v3 refitted's 8.85%, and 9.64% against 9.11% by the "
         "fallback")
    V31("s7.loco.0", "v3.1", "LOCO (anchor route)", "all", "W given t (>= 3 W)", p)
    V31("s7.loco.1", "v3 refitted", "LOCO (anchor route)", "all", "W given t (>= 3 W)", p)
    V31("s7.loco.2", "v3.1", "LOCO (fallback route)", "all", "W given t (>= 3 W)", p)
    V31("s7.loco.3", "v3 refitted", "LOCO (fallback route)", "all", "W given t (>= 3 W)", p)
    for i, tok in enumerate(("10", "10")):
        T("s7.split.%d" % i, "v31_readme", "tC closer 10, T5r closer 10, exact sign test p 1.0000", tok, "T5r and tC split E213's family C 10 to 10")
    p = "better (3.5% against 5.1%, REPORTED)"
    Jn("s7.e146.tc", "v31_reported", ["item8_E146_store_rungs_both_forms", "tC", "E146 store rungs (never trained)", "rms_pct"], "{:.1f}", p, "REPORTED")
    Jn("s7.e146.t5", "v31_reported", ["item8_E146_store_rungs_both_forms", "T5r", "E146 store rungs (never trained)", "rms_pct"], "{:.1f}", p, "REPORTED")
    p = "MM1-v3's card-1 zeros held out read 5.32% against 8.50% for MM1-v2's form"
    T("s7.z.0", "v3_readme", "card 1's all-zero data 5.32% (+0.10) against 8.50% (+2.97)", "5.32", p)
    T("s7.z.1", "v3_readme", "card 1's all-zero data 5.32% (+0.10) against 8.50% (+2.97)", "8.50", p)
    # report-v2-fix (finding M7): "priced to 6.8% unread" tempered by E215's family S
    p = ("(now counted: priced to 6.8% unread, and blind on E215's 12 new kinds to 8.45%, though int8 data of plus and minus one read +23.6%)"
         if c215 is not None else "(now counted, and priced to 6.8% unread)")
    Jn("s7.tiles", "unread_sw", ["groups", "A", "all", "V3", "Q1_cases", "rms_pct"], "{:.1f}", p, "unread, rms %")
    if c215 is not None:
        sS = e215_stat(c215, PA215, "posthoc", "v31", "Jg", "fm", "S")
        aS = {"arm": PA215, "group": "posthoc", "model": "v31", "q": "Jg", "conv": "fm", "only": "S"}
        D("s7.tiles.S.n", sS["n"], "{:d}", p, "e215", dict(aS, stat="n"), E215_INPUTS, "family S points, desk")
        D("s7.tiles.S.rms", sS["rms"], "{:.2f}", p, "e215", dict(aS, stat="rms"), E215_INPUTS, "blind, post hoc-selected, rms %, desk")
        D("s7.tiles.S.a057", e215_one(c215, "A", "posthoc", "v31", "Jg", "fm", "a057"), "{:+.1f}", p, "e215one",
          {"arm": "A", "group": "posthoc", "model": "v31", "q": "Jg", "conv": "fm", "key": "a057"}, E215_INPUTS,
          "one E215 point, %, desk (forecast / measured - 1)")
    p = "(with rgm211 held out MM1-v3 reads 7.78% against 9.31%)"
    T("s7.r211.0", "v3_readme", "leave rgm211 out 7.78% against 9.31%", "7.78", p)
    T("s7.r211.1", "v3_readme", "leave rgm211 out 7.78% against 9.31%", "9.31", p)
    p = "rgm136's gemmL loop runs 46 instructions an op, not 36 (E211's dated correction 1)"
    T("chg.46", "e211_corr", "the gemmL loops run 46 and 40 instructions an op, not 36 and 35", "46", p)
    T("chg.36", "e211_corr", "the gemmL loops run 46 and 40 instructions an op, not 36 and 35", "36", p)
    # report-v2-fix: the numbers its changelog entry restates, from the same sources as the body's; and eta's neutral 0 in section 6.3
    p = "the scorecard's 2.7-9.0% is on each test's registered points, with E215's post hoc-selected 10.2% and 11.8%"
    range_entry(G, "chg.fix.reg", sel_n, "wall", p)
    if sel_ph:
        range_entry(G, "chg.fix.ph", sel_ph, "wall", p)
    if c215 is not None:
        sn = e215_stat(c215, "A", "registered", "v31", "Jg", "fm", "nolnc")
        D("chg.fix.375", sn["rms"], "{:.2f}", "3.75%'s footing", "e215", {"arm": "A", "group": "registered", "model": "v31", "q": "Jg",
          "conv": "fm", "only": "nolnc", "stat": "rms"}, E215_INPUTS, "post hoc, without the gemmLnc points, rms %, desk")
    Jn("chg.fix.v2form", "e212s3", ["twins", "wall cycles (time configuration)", "no_twin", "v2form", "rms_pct"], "{:.2f}",
       "v2form's 4.08% on S3's new configurations", "REPORTED beside, rms %")
    T("chg.fix.4142", "e213_a3", "so k38 and k39 (runs 41-42), the middle tie and **all of pass 2** (runs 43-85)", "41-42",
      "A3's counterfactual counts runs 41-42")
    T("s63.eta0", "v31_readme", "re-read with that fold's constants and eta at its neutral 0 (REPORTED, post hoc)", "0",
      "with that fold read at eta's neutral 0, T7 was worse than n/32 on every layout class")

    # ---------------- E215
    t215 = build_e215(G, R, c215, rules215) if c215 is not None else None

    # ---------------- the generated tables and the figures
    tables = ["<!-- the scorecard's rows (make_figures.py) -->"] + sc + [rep, "", "<!-- E213's two footings -->"]
    tables += [r for r in G.rows if r.startswith("| wall cycles an op") or r.startswith("| the counter's mean") or r.startswith("| J over idle given the seconds, 3 W")
               or r.startswith("| the same without") or r.startswith("| J with the card at rest given")]
    tables += ["", "<!-- E213's verdicts, head to head -->"] + [r for r in G.rows if r.startswith("| wall cycles, head") or r.startswith("| counter's mean |")
                                                                  or r.startswith("| seconds |") or r.startswith("| J over idle given the seconds |")
                                                                  or r.startswith("| J over idle with the seconds forecast |")]
    tables += ["", "<!-- MM1-v3.1 held out -->"] + [r for r in G.rows if any(r.startswith("| " + n[0] + " |") for n in v31rows)]
    if t215:
        for k, title in (("verdicts", "E215's verdicts"), ("footings", "E215's two footings"), ("reported", "E215 REPORTED beside"),
                         ("lnc", "E215's gemmLnc points"), ("switch_S", "E215's family S (section 5)")):
            tables += ["", f"<!-- {title} -->"] + t215[k]
    figs = {}
    figs["fig-1-timing.svg"] = fig_timing(sim, st)
    fig_rows = []
    pick = [("E206 arm A", "E206 arm A (aifoundry3 card 0, 600 MHz)", "MM1-v0", [("F1", "sq"), ("F2", "tri")]),
            ("E206 arm B", "E206 arm B (aifoundry1 card 1, 600 MHz)", "MM1-v1", [("MM1-v0", "hol"), ("F1", "sq"), ("F2", "tri")]),
            ("E207", "E207 (aifoundry3 card 0, 600 MHz)", "MM1-v2", [("MM1-v1", "hol"), ("F1", "sq"), ("F2", "tri")]),
            ("E209", "E209 (aifoundry2 card 0, its governor)", "MM1-v2", [("MM1-v1", "hol"), ("F1@800", "sq")]),
            ("E211 rgm211", "E211, rgm211's 12 points (aifoundry3 card 0)", "MM1-v2", [("MM1-v1", "hol"), ("F1", "sq")]),
            ("E212 S3", "E212 a2c0-S3, re-run (aifoundry2 card 0, its governor)", "MM1-v3", [("MM1-v2", "hol")]),
            ("E213 arm A", "E213 arm A (aifoundry3 card 0, 600 MHz)", "MM1-v3", [("MM1-v2", "hol")]),
            ("E213 arm B", "E213 arm B (aifoundry1 card 1, 600 MHz)", "MM1-v3", [("MM1-v2", "hol")])]
    # report-v2-fix (findings M3 and L6): figure 2 draws the blind tests only (the two unread rows are in the table alone), and E215's
    # post hoc-selected families L and S beside its registered ones, marked open
    if c215 is not None:
        pick += [x for x in [("E215 arm A", "E215 arm A, families P, C, R (aifoundry3 card 0, 600 MHz)", "MM1-v3.1", [("MM1-v3", "hol")]),
                             ("E215 arm B", "E215 arm B, families P, C, R (aifoundry1 card 1, 600 MHz)", "MM1-v3.1", [("MM1-v3", "hol")]),
                             ("E215 A L,S (post hoc)", "E215 arm A, families L, S (aifoundry3 card 0, 600 MHz)", "MM1-v3.1", [("MM1-v3", "hol")]),
                             ("E215 B L,S (post hoc)", "E215 arm B, families L, S (aifoundry1 card 1, 600 MHz)", "MM1-v3.1", [("MM1-v3", "hol")])]
                 if x[1].split(",")[0][-1] in ARMS215]
    byk = {(r[0], r[1]): r[3] for r in rows}
    for short, test, newest, comps in pick:
        nv = {q: (byk[(test, newest)][q]["rms"] if byk[(test, newest)].get(q) else None) for q in ("wall", "jg3")}
        cs = []
        for cl, shape in comps:
            c = byk[(test, cl)]
            cs.append((cl, {q: (c[q]["rms"] if c.get(q) else None) for q in ("wall", "jg3")}, shape))
        fig_rows.append((short, newest, nv, cs, "post hoc" in short))
    lo_w = min(c["rms"] for r in sel_n for c in [r[3]["wall"]])
    hi_w = max(c["rms"] for r in sel_n for c in [r[3]["wall"]])
    ph = [r[3]["wall"]["rms"] for r in sel_ph] if sel_ph else []
    head2 = "Frozen before each blind test, the newest MM1 read %.1f-%.1f%% in wall cycles on the registered points" % (lo_w, hi_w)
    if ph:
        head2 += ", %.1f-%.1f%% on E215's post hoc ones (open)" % (min(ph), max(ph))
    figs["fig-2-scorecard.svg"] = fig_scorecard(fig_rows, head2)
    sw = R.json("v1_numbers")["switch"]["routes"]
    U = R.json("unread_sw")["pass_rule_against_N"]["Q2"]
    bars = [("E210, blind (13 test cases)", "switch route (R1)", sw["R1"]["rms_over_D_pct"], True),
            ("E210, blind (13 test cases)", "bit flips, scaled (R3L)", sw["R3L"]["rms_over_D_pct"], False),
            ("E210, blind (13 test cases)", "nearest kind (R4)", sw["R4"]["rms_over_D_pct"], False),
            ("E210, blind (13 test cases)", "MM1-v1 kind term (R2, 5)", sw["R2"]["rms_over_D_pct"], False),
            ("E210, blind (13 test cases)", "bit flips, raw (R3)", sw["R3"]["rms_over_D_pct"], False),
            ("Unread tiles (29 cases)", "MM1-v3 + new counts", U["V3"]["rms_pct"], True),
            ("Unread tiles (29 cases)", "null N", U["N"]["rms_pct"], False)]
    head3 = ("Energy followed the counted switches: %.1f%% of D blind and %.1f%% unread, against 16-47%% and %.0f%%"
             % (sw["R1"]["rms_over_D_pct"], U["V3"]["rms_pct"], U["N"]["rms_pct"]))
    sS_fig = t215.get("switch_S_fig") if t215 else None
    if sS_fig:  # report-v2-fix (finding M7)
        head3 += "; on E215's %d new kinds, int8 data of plus and minus one missed" % len(sS_fig)
    figs["fig-3-switch.svg"] = fig_switch(bars, head3, sS_fig)
    figs["fig-4-v31.svg"] = fig_v31(v31_fig, "MM1-v3.1 equalled MM1-v3 refitted in time and lost on a held-out card's energy")
    f5 = None
    if t215:
        f5 = [(r["point"], r["label"], r["v31"], r["lnc"]) for r in t215["lnc_fig"]]
        head5 = ("gemmLnc drew %.2f-%.2fx MM1-v3's forecast on E213 and %.2f-%.2fx MM1-v3.1's on E215; the frozen term read %.2f-%.2fx"
                 % (min(lnc), max(lnc), min(r[2] for r in f5), max(r[2] for r in f5), min(r[3] for r in f5), max(r[3] for r in f5)))
    else:
        head5 = "The non-cooperative loop drew %.2f-%.2fx the energy MM1-v3 forecast; its twins %.2f-%.2fx" % (min(lnc), max(lnc), min(twins), max(twins))
    figs["fig-5-gemmlnc.svg"] = fig_gemmlnc(rat, head5, f5)
    return {"figures": figs, "tables": "\n".join(tables) + "\n"}


# ------------------------------------------------------------------------------------------------ SVG helpers
STYLE = """<style>
  .bg{fill:#ffffff} .ink{fill:#1d1d1b} .ink2{fill:#52514e} .muted{fill:#6f6e69}
  .grid{stroke:#e1e0d9;stroke-width:1} .base{stroke:#c3c2b7;stroke-width:1}
  .acc{fill:#2a78d6} .accs{stroke:#2a78d6;stroke-width:2} .gry{fill:#898781} .gry2{fill:#52514e} .hol{fill:#ffffff;stroke:#2a78d6;stroke-width:2}
  .holg{fill:#ffffff;stroke:#898781;stroke-width:2} .band{fill:#2a78d6;fill-opacity:0.10} .bandg{fill:#898781;fill-opacity:0.12}
  text{font-family:system-ui,-apple-system,"Segoe UI",sans-serif}
  .t1{font-size:16px;font-weight:600} .t2{font-size:13px} .t3{font-size:12.5px} .tn{font-size:12px;font-variant-numeric:tabular-nums}
  @media (prefers-color-scheme: dark){
    .bg{fill:#1a1a19} .ink{fill:#f0efec} .ink2{fill:#c3c2b7} .muted{fill:#a9a8a0}
    .grid{stroke:#2c2c2a} .base{stroke:#383835}
    .acc{fill:#3987e5} .accs{stroke:#3987e5} .gry{fill:#898781} .gry2{fill:#c3c2b7} .hol{fill:#1a1a19;stroke:#3987e5}
    .holg{fill:#1a1a19;stroke:#898781} .band{fill:#3987e5} .bandg{fill:#898781}
  }
</style>"""


def esc(s):
    return str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;")


def wrap(s, width):
    out, line = [], ""
    for w in s.split():
        if len(line) + len(w) + (1 if line else 0) > width:
            out.append(line)
            line = w
        else:
            line = (line + " " + w) if line else w
    if line:
        out.append(line)
    return out


class SVG:
    def __init__(self, w, title, desc):
        self.w = w
        self.title = title
        self.desc = desc
        self.body = []
        self.y = 0

    def t(self, x, y, s, cls="t2 ink", anchor="start", tip=None):
        inner = esc(s) + (f"<title>{esc(tip)}</title>" if tip else "")
        self.body.append(f'<text x="{x:.1f}" y="{y:.1f}" class="{cls}" text-anchor="{anchor}">{inner}</text>')

    def raw(self, s):
        self.body.append(s)

    def head(self, sub):
        y = 26
        for ln in wrap(self.title, 46):
            self.t(16, y, ln, "t1 ink")
            y += 20
        y += 1
        for ln in wrap(sub, 60):
            self.t(16, y, ln, "t3 ink2")
            y += 16
        self.y = y + 6
        return self.y

    def done(self, h):
        h = int(math.ceil(h))
        top = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{self.w}" height="{h}" viewBox="0 0 {self.w} {h}" role="img" '
               f'aria-labelledby="t d" style="max-width:100%;height:auto">\n<title id="t">{esc(self.title)}</title>\n'
               f'<desc id="d">{esc(self.desc)}</desc>\n{STYLE}\n<rect class="bg" x="0" y="0" width="{self.w}" height="{h}"/>\n')
        return top + "\n".join(self.body) + "\n</svg>\n"


def logx(v, lo, hi, x0, x1):
    v = max(lo, min(hi, v))
    return x0 + (math.log10(v) - math.log10(lo)) / (math.log10(hi) - math.log10(lo)) * (x1 - x0)


# ------------------------------------------------------------------------------------------------ the figures
def fig_timing(vals, st):
    allv = sim_all_of(vals)
    groups = [("E206, E207", vals["E206-E207"], "acc"), ("E213", vals["E213A"] + vals["E213B"], "gry")]
    if "E215A" in vals:
        groups.append(("E215" + ("" if "E215B" in vals else " arm A"), vals["E215A"] + vals.get("E215B", []), "gry2"))
    names = ", ".join(g[0] for g in groups[:-1]) + " and " + groups[-1][0]
    title = "A GEMM took %s to %s card cycles for each instruction the simulator counts" % (st["min"], st["max"])
    desc = ("Stacked histogram of the card's cycles a GEMM (the slowest minion) over the simulator's instruction count a minion a GEMM, at %d "
            "blind points of rgm136's gemmL loop (%s; median %s). The simulator has no clock: its step is one instruction."
            % (len(allv), names, st["median"]))
    s = SVG(400, title, desc)
    y0 = s.head("Card cycles per simulated instruction, %d blind points of rgm136's gemmL (%s); median %s. The instruction counts "
                "come from a law fitted to 11 simulator runs." % (len(allv), names, st["median"]))
    edges = [7.5 + 2.5 * i for i in range(13)]
    counts = []
    for _, vs, _ in groups:
        c = [0] * 12
        for v in vs:
            c[min(11, max(0, int((v - 7.5) // 2.5)))] += 1
        counts.append(c)
    top = int(math.ceil(max(sum(c[i] for c in counts) for i in range(12)) * 1.12 / 10.0) * 10)
    lx = 16
    for (name, vs, cls) in groups:
        s.raw(f'<rect class="{cls}" x="{lx}" y="{y0}" width="12" height="12" rx="2"/>')
        s.t(lx + 17, y0 + 10.5, "%s (%d)" % (name, len(vs)), "t3 ink")
        lx += 128
    y0 += 34
    x0, x1 = 46, 384
    ph = 190
    yb = y0 + ph
    bw = (x1 - x0) / 12.0
    step = 20 if top <= 120 else 40
    for g in range(0, top + 1, step):
        yy = yb - g / top * ph
        s.raw(f'<line class="grid" x1="{x0}" x2="{x1}" y1="{yy:.1f}" y2="{yy:.1f}"/>')
        s.t(x0 - 6, yy + 4, str(g), "tn muted", "end")
    for i in range(12):
        xa = x0 + i * bw + 1
        tip = "%.1fx to %.1fx: " % (edges[i], edges[i + 1]) + ", ".join("%d of %s" % (c[i], g[0]) for c, g in zip(counts, groups))
        ytop = yb
        for c, (_, _, cls) in zip(counts, groups):
            if c[i]:
                h = c[i] / top * ph
                ytop -= h
                s.raw(f'<rect class="{cls}" x="{xa:.1f}" y="{ytop:.1f}" width="{bw - 2:.1f}" height="{h:.1f}"><title>{esc(tip)}</title></rect>')
                ytop -= 2
    s.raw(f'<line class="base" x1="{x0}" x2="{x1}" y1="{yb}" y2="{yb}"/>')
    for i in range(0, 13, 2):
        xx = x0 + i * bw
        s.t(xx, yb + 16, "%gx" % edges[i], "tn muted", "middle")
    s.t((x0 + x1) / 2, yb + 34, "card cycles a GEMM / simulated instructions a minion a GEMM", "t3 ink2", "middle")
    s.t(x0 - 6, y0 - 14, "points", "tn muted", "end")
    return s.done(yb + 48)


def fig_scorecard(rows_fig, head):
    """rows_fig: list of (test label, newest MM1 label, {q: value}, [(comparator label, {q: value}, shape)], post hoc?); a post hoc row's
    newest-MM1 dot is drawn open (report-v2-fix: E215's post hoc-selected families L and S, apart from the registered points)"""
    title = head
    desc = ("Two panels, log scale 1% to 100%: the rms error of the newest MM1 frozen before each blind test (filled circle; open for E215's "
            "post hoc-selected families L and S) against the lab's earlier routes and the previous MM1 (grey), in wall cycles an op and in J "
            "over idle given the measured seconds (3 W and above). The shaded band is the card's own session repeat. The unread tests are in "
            "the README's table only.")
    s = SVG(400, title, desc)
    y = s.head("rms of forecast / measured - 1, log scale. Filled: the newest MM1 frozen before the test, on its registered points; open: "
               "E215's post hoc-selected points. Grey: the previous MM1 (open circle), F1 (square), F2 (triangle). Shaded: the card's own "
               "session repeat (0.38% and 1.16%).")
    pans = [("wall cycles an op", "wall", 110, 243, 0.383), ("J over idle, given t", "jg3", 262, 390, 1.163)]
    lo, hi = 0.3, 100.0
    for name, q, xa, xb, rep in pans:
        s.t((xa + xb) / 2, y + 10, name, "t3 ink", "middle")
    y += 22
    ytop = y
    rh = 30
    for i, (test, newest, nv, comps, posthoc) in enumerate(rows_fig):
        yy = y + i * rh + rh / 2
        for ln_i, ln in enumerate(wrap(test, 15)[:2]):
            s.t(16, yy - 3 + ln_i * 13 - (6 if len(wrap(test, 15)) > 1 else 0) + 4, ln, "t3 ink")
        for name, q, xa, xb, rep in pans:
            s.raw(f'<line class="grid" x1="{xa}" x2="{xb}" y1="{yy:.1f}" y2="{yy:.1f}"/>')
            for cl, cv, shape in comps:
                v = cv.get(q)
                if v is None:
                    continue
                cx = logx(v, lo, hi, xa, xb)
                tip = f"{test}: {cl} {v:.1f}%"
                if shape == "sq":
                    s.raw(f'<rect class="gry" x="{cx - 4.5:.1f}" y="{yy - 4.5:.1f}" width="9" height="9" rx="1.5"><title>{esc(tip)}</title></rect>')
                elif shape == "tri":
                    s.raw(f'<path class="gry2" d="M {cx:.1f} {yy - 6:.1f} L {cx + 5.5:.1f} {yy + 4.5:.1f} L {cx - 5.5:.1f} {yy + 4.5:.1f} Z"><title>{esc(tip)}</title></path>')
                elif shape == "dia":
                    s.raw(f'<path class="gry2" d="M {cx:.1f} {yy - 6:.1f} L {cx + 6:.1f} {yy:.1f} L {cx:.1f} {yy + 6:.1f} L {cx - 6:.1f} {yy:.1f} Z"><title>{esc(tip)}</title></path>')
                else:
                    s.raw(f'<circle class="holg" cx="{cx:.1f}" cy="{yy:.1f}" r="4.5"><title>{esc(tip)}</title></circle>')
            v = nv.get(q)
            if v is not None:
                cx = logx(v, lo, hi, xa, xb)
                tip = f"{test}: {newest} {v:.1f}%" + (" (post hoc-selected points)" if posthoc else "")
                s.raw(f'<circle class="{"hol" if posthoc else "acc"}" cx="{cx:.1f}" cy="{yy:.1f}" r="5.5"><title>{esc(tip)}</title></circle>')
                s.t(cx, yy - 8, f"{v:.1f}", "tn ink", "middle")
    yb = y + len(rows_fig) * rh
    for name, q, xa, xb, rep in pans:
        bx = logx(rep, lo, hi, xa, xb)
        s.raw(f'<rect class="band" x="{xa}" y="{ytop}" width="{bx - xa:.1f}" height="{yb - ytop:.1f}"><title>the card repeats to {rep:.2f}%</title></rect>')
        for g in (1, 3, 10, 30, 100):
            gx = logx(g, lo, hi, xa, xb)
            s.raw(f'<line class="base" x1="{gx:.1f}" x2="{gx:.1f}" y1="{yb}" y2="{yb + 4}"/>')
            if g in (1, 10) or (g == 100 and q == "jg3"):
                s.t(gx, yb + 16, f"{g}%", "tn muted", "end" if g == 100 else "middle")
        s.raw(f'<line class="base" x1="{xa}" x2="{xb}" y1="{yb}" y2="{yb}"/>')
    return s.done(yb + 30)


def fig_switch(bars, head, pts=None):
    """bars: list of (group, label, value % of D, accent?); pts (report-v2-fix): E215's family S kinds, each {point, format, kind,
    measured, v31, err}, drawn as a scatter of the measured kind-over-random W ratio against MM1-v3.1's"""
    desc = ("Horizontal bars: each route's rms error in the data-dependent power as a share of D (random minus zeros), on E210's 13 blind "
            "test cases and on the unread test's 29 cases. The switch route is the accent bar."
            + (" Below, a scatter of E215's family S kinds (blind, post hoc-selected): each kind's W over idle over its random partner's, "
               "measured against MM1-v3.1's forecast, fp32 as circles and int8 as squares; the diagonal is an exact forecast, and the one "
               "kind far from it is int8 data of plus and minus one." if pts else ""))
    s = SVG(400, head, desc)
    y = s.head("rms error of the data-dependent power, % of D (random minus zeros). E210: blind, nine patterns at two shapes; unread: new "
               "switch counts for E212's plan tiles and the real tiles.")
    x0, x1 = 170, 360
    vmax = 50.0
    grp = None
    for g, lab, v, acc in bars:
        if g != grp:
            y += 8
            s.t(16, y + 10, g, "t3 ink2")
            y += 18
            grp = g
        w = v / vmax * (x1 - x0)
        s.t(16, y + 13, lab, "t3 ink")
        s.raw(f'<rect class="{"acc" if acc else "gry"}" x="{x0}" y="{y + 2}" width="{w:.1f}" height="14" rx="2"><title>{esc(f"{g}: {lab} {v:.2f}% of D")}</title></rect>')
        s.t(x0 + w + 5, y + 13.5, f"{v:.1f}%", "tn ink")
        y += 22
    s.raw(f'<line class="base" x1="{x0}" x2="{x0}" y1="{y - 22 * len(bars) - 40}" y2="{y}"/>')
    if not pts:
        return s.done(y + 14)
    # report-v2-fix (finding M7): E215's family S, blind and post hoc-selected: each kind's W over idle over its random partner's, measured
    # against MM1-v3.1's forecast ratio; on the diagonal the forecast is exact. fp32 circles, int8 squares; the one miss in the accent.
    y += 20
    for ln in wrap("E215 family S, blind (post hoc-selected), %d kinds: each kind's W over idle over its random partner's, measured "
                   "(up) against MM1-v3.1's forecast (across)" % len(pts), 60):
        s.t(16, y, ln, "t3 ink2")
        y += 16
    y += 4
    s.raw(f'<circle class="gry" cx="22" cy="{y - 4:.1f}" r="4.5"/>')
    s.t(31, y, "fp32", "t3 ink")
    s.raw(f'<rect class="gry2" x="68" y="{y - 8.5:.1f}" width="9" height="9" rx="1.5"/>')
    s.t(82, y, "int8", "t3 ink")
    s.t(120, y, "on the line: exactly as forecast", "t3 muted")
    y += 34
    lo, hi = 0.4, 1.05
    px0, px1, ph = 70, 370, 230
    py0, py1 = y + ph, y

    def X(v):
        return px0 + (v - lo) / (hi - lo) * (px1 - px0)

    def Y(v):
        return py0 - (v - lo) / (hi - lo) * (py0 - py1)
    for g in (0.5, 0.6, 0.7, 0.8, 0.9, 1.0):
        s.raw(f'<line class="grid" x1="{px0}" x2="{px1}" y1="{Y(g):.1f}" y2="{Y(g):.1f}"/>')
        s.raw(f'<line class="grid" x1="{X(g):.1f}" x2="{X(g):.1f}" y1="{py1}" y2="{py0}"/>')
        s.t(px0 - 6, Y(g) + 4, f"{g:.1f}", "tn muted", "end")
        s.t(X(g), py0 + 15, f"{g:.1f}", "tn muted", "middle")
    s.raw(f'<line class="base" x1="{px0}" x2="{px1}" y1="{py0}" y2="{py0}"/>')
    s.raw(f'<line class="base" x1="{px0}" x2="{px0}" y1="{py1}" y2="{py0}"/>')
    s.raw(f'<line class="accs" x1="{X(lo):.1f}" y1="{Y(lo):.1f}" x2="{X(hi):.1f}" y2="{Y(hi):.1f}" stroke-opacity="0.35"/>')
    worst = max(pts, key=lambda q: abs(q["err"]))
    for q in sorted(pts, key=lambda q: q is worst):
        cx, cy = X(q["v31"]), Y(q["measured"])
        tip = (f"{q['point']} ({q['format']}, {q['kind']}): measured {q['measured']:.3f}, MM1-v3.1 {q['v31']:.3f}; J over idle given t "
               f"{sgn(q['err'])}%")
        cls = "acc" if q is worst else ("gry2" if q["format"] == "int8" else "gry")
        if q["format"] == "int8":
            s.raw(f'<rect class="bg" x="{cx - 6.5:.1f}" y="{cy - 6.5:.1f}" width="13" height="13" rx="2.5"/>')
            s.raw(f'<rect class="{cls}" x="{cx - 4.5:.1f}" y="{cy - 4.5:.1f}" width="9" height="9" rx="1.5"><title>{esc(tip)}</title></rect>')
        else:
            s.raw(f'<circle class="bg" cx="{cx:.1f}" cy="{cy:.1f}" r="6.5"/>')
            s.raw(f'<circle class="{cls}" cx="{cx:.1f}" cy="{cy:.1f}" r="4.5"><title>{esc(tip)}</title></circle>')
    cy = Y(worst["measured"])
    name = "int8 ±1" if worst["kind"] == "pattern:i8_pm1" else worst["kind"]
    s.t(px1, cy + 20, f"{worst['point']}, {name}", "t3 ink", "end")
    s.t(px1, cy + 34, f"J over idle {sgn(worst['err'])}%", "t3 ink", "end")
    s.t((px0 + px1) / 2, py0 + 32, "MM1-v3.1's forecast ratio", "t3 ink2", "middle")
    s.t(16, py1 - 6, "measured ratio", "t3 ink2")
    return s.done(py0 + 44)


def fig_v31(pairs, head):
    """pairs: list of (label, v3.1 value, v3 refitted value)"""
    desc = ("Paired horizontal bars: MM1-v3.1 (accent) and MM1-v3 refitted on the same points and folds (grey), held-out rms error, "
            "without configuration twins where marked.")
    s = SVG(400, head, desc)
    y = s.head("held-out rms, the same points and folds. Accent: MM1-v3.1. Grey: MM1-v3's form refitted on v3.1's data. Time folds "
               "without configuration twins.")
    s.raw(f'<rect class="acc" x="16" y="{y}" width="12" height="12" rx="2"/>')
    s.t(33, y + 10.5, "MM1-v3.1", "t3 ink")
    s.raw(f'<rect class="gry" x="120" y="{y}" width="12" height="12" rx="2"/>')
    s.t(137, y + 10.5, "MM1-v3 refitted", "t3 ink")
    y += 26
    x0, x1 = 172, 352
    vmax = 12.0
    for lab, a, b in pairs:
        lines = wrap(lab, 24)
        for k, ln in enumerate(lines[:2]):
            s.t(16, y + 12 + 13 * k, ln, "t3 ink")
        for k, (v, cls, nm) in enumerate(((a, "acc", "MM1-v3.1"), (b, "gry", "MM1-v3 refitted"))):
            w = v / vmax * (x1 - x0)
            yy = y + 2 + k * 13
            s.raw(f'<rect class="{cls}" x="{x0}" y="{yy}" width="{w:.1f}" height="11" rx="2"><title>{esc(f"{lab}: {nm} {v:.2f}%")}</title></rect>')
            s.t(x0 + w + 5, yy + 10, f"{v:.2f}%", "tn ink")
        y += 36
    s.raw(f'<line class="base" x1="{x0}" x2="{x0}" y1="{y - 36 * len(pairs)}" y2="{y}"/>')
    return s.done(y + 10)


def fig_gemmlnc(rat, head, e215=None):
    """rat: E213's gemmLnc points and twins (measured / MM1-v3 given t); e215: [(point, label, measured / MM1-v3.1, measured / the term)]"""
    desc = ("Dot plot: measured J over idle over the forecast given the measured seconds, at E213's seven points of rgm136's non-cooperative "
            "loop gemmLnc (accent; MM1-v3) and their cooperative gemmL twins (grey)" +
            (", and at E215's five gemmLnc points (accent: MM1-v3.1; open: MM1-v3.1 with the gemmLnc term frozen before E215's data)"
             if e215 else "") + ". 1 is a perfect forecast.")
    s = SVG(400, head, desc)
    y = s.head("measured J over idle / the forecast given the measured seconds (blind). E213: MM1-v3 at gemmLnc (accent) and its gemmL "
               "twin (grey)." + (" E215: MM1-v3.1 (accent) and MM1-v3.1 + the gemmLnc term (open)." if e215 else ""))
    x0, x1 = 150, 380
    lo, hi = 0.8, 1.9

    def X(v):
        return x0 + (v - lo) / (hi - lo) * (x1 - x0)
    order = ["a075", "a079", "a082", "a086", "a087", "k37", "k40"]
    twins = {"a075": "a006", "a079": "a076", "a082": "a030", "a086": "a083", "a087": "a088", "k37": "k06"}
    ytop = y
    if e215:
        s.t(16, y + 12, "E213, MM1-v3", "t3 ink2")
        y += 22
    for p in order:
        r = rat[p]
        shape = r["arm_key"].split("|")[1]
        fmt = r["arm_key"].split("|")[2]
        s.t(16, y + 12, f"{p} {shape} {fmt}", "t3 ink")
        s.raw(f'<line class="grid" x1="{x0}" x2="{x1}" y1="{y + 8}" y2="{y + 8}"/>')
        t = twins.get(p)
        if t and t in rat:
            tx = X(rat[t]["ratio"])
            s.raw(f'<circle class="gry" cx="{tx:.1f}" cy="{y + 8}" r="4.5"><title>{esc(f"{t}, the gemmL twin of {p}: {rat[t]['ratio']:.3f}")}</title></circle>')
        cx = X(r["ratio"])
        s.raw(f'<circle class="acc" cx="{cx:.1f}" cy="{y + 8}" r="5.5"><title>{esc(f"{p} gemmLnc: {r['ratio']:.3f}")}</title></circle>')
        s.t(cx + 9, y + 12, f"{r['ratio']:.2f}", "tn ink")
        y += 26
    if e215:
        y += 6
        s.t(16, y + 12, "E215 (gemmLnc, fp32), MM1-v3.1 and + term", "t3 ink2")
        y += 22
        for p, lab, a, b in e215:
            s.t(16, y + 12, f"{p} {lab}", "t3 ink")
            s.raw(f'<line class="grid" x1="{x0}" x2="{x1}" y1="{y + 8}" y2="{y + 8}"/>')
            bx = X(b)
            s.raw(f'<circle class="hol" cx="{bx:.1f}" cy="{y + 8}" r="5"><title>{esc(f"{p}, MM1-v3.1 + the gemmLnc term: {b:.3f}")}</title></circle>')
            cx = X(a)
            s.raw(f'<circle class="acc" cx="{cx:.1f}" cy="{y + 8}" r="5.5"><title>{esc(f"{p}, MM1-v3.1: {a:.3f}")}</title></circle>')
            s.t(max(cx, bx) + 9, y + 12, f"{a:.2f} / {b:.2f}", "tn ink")
            y += 26
    one = X(1.0)
    s.raw(f'<line class="base" x1="{one:.1f}" x2="{one:.1f}" y1="{ytop - 4}" y2="{y}"/>')
    for g in (0.8, 1.0, 1.2, 1.4, 1.6, 1.8):
        s.t(X(g), y + 14, f"{g:.1f}", "tn muted", "middle")
    s.t((x0 + x1) / 2, y + 30, "measured / forecast", "t3 ink2", "middle")
    return s.done(y + 40)


# ------------------------------------------------------------------------------------------------ main
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", default=".")
    ap.add_argument("--out", default=None)
    ap.add_argument("--list-inputs", action="store_true")
    a = ap.parse_args()
    if a.list_inputs:
        for k, (c, p, h) in sorted(PINS.items()):
            print(k, c, p, h or "")
        return 0
    R = Repo(a.repo)
    for k in PINS:
        R.pinned(k)
    G = Reg(R)
    cache = {arm: e213_errors(R, arm) for arm in ("A", "B")}
    c215 = rules215 = None
    if "e215A_scores" in PINS:
        fc215 = e215_fc(R)
        c215 = {arm: (e215_errors(R, fc215, arm) if arm in ARMS215 else {}) for arm in ("A", "B")}
        rules215 = R.json("e215_rules")
    out = build(G, R, cache, c215, rules215)
    if a.out:
        os.makedirs(a.out, exist_ok=True)
        meta = {"what": "every number of README.md: its value, the token printed, the README phrase, its label and its committed source",
                "interpreter": sys.version.split()[0], "inputs": {k: {"commit": c, "path": p, "sha256": hashlib.sha256(R.blob(c, p)).hexdigest()}
                                                                  for k, (c, p, h) in sorted(PINS.items())}}
        with open(os.path.join(a.out, "numbers.json"), "w") as f:
            json.dump({"meta": meta, "numbers": G.items}, f, indent=1, sort_keys=True)
            f.write("\n")
        for name, svg in out["figures"].items():
            with open(os.path.join(a.out, name), "w") as f:
                f.write(svg)
        with open(os.path.join(a.out, "tables.md"), "w") as f:
            f.write(out["tables"])
    print(f"make_figures: {len(G.items)} numbers, {len(out['figures'])} figures")
    return 0


if __name__ == "__main__":
    sys.exit(main())
