#!/usr/bin/env python3
"""E191's second-session data README, dated note 1 (Sun 15 Nov 2026, after the data verifier): the figures the note quotes, read
again from committed files. Post hoc and reported readings only: it decides nothing, scores nothing and changes no committed file.

    python3 -I -B docs/reports/data/2026-11-15-e191-blind-day-aifoundry1-c1-s2/posthoc_note1_e191.py [--out DIR] [--data DIR --top DIR]

It reads only committed files: the files of this directory's data commit (the 257 that SHA256SUMS lists, README.md, SHA256SUMS and
FILES.txt; never a file added after them, so the note's own files do not change its outputs); and from the repository: E191's
registration list tools/claims-v3/e191/SHA256SUMS-e191-registration with the files it pins, E189's registration list
tools/claims-v3/e189/SHA256SUMS-e189-registration with forecast-e189.json (section 6's reading), and as text E191.md,
collect_e191.py and run_e191_v2.py (the lines the note cites).

Section 0: SHA256SUMS read entry by entry; the sha256 of README.md, SHA256SUMS and FILES.txt; both registration lists read entry by entry.
Section 1: the scrub. The box's session/MANIFEST.sha256 against this directory's bytes; the files outside it; every file's count of
"~", of the login placeholder and of a home-directory path (the text inside every .gz included); session/runner.rc's bytes; the
README's and the collector's lines.
Section 2: S1T's margin on the starting die (post hoc). Only after E191's registration list reads every entry OK (and
tools/ledger/ledger_v2.py and the ledger v2's frozen-v2.json match forecast_e191.py's own pins) does it load the frozen scorer,
score_e191.py, as registered, and use its own pass reader (read_pass), its forecast module's given() and its verdict count
(count_rule): each pass's given-seconds J with the card at rest at its measured t_k and t_w and its T0 moved by one uniform delta,
against the measured J with the card at rest as committed. delta = 0 is the registered reading (it must equal the frozen scorer's
e_j_total, from its own score_day() run here); every other delta is post hoc. Then one more post hoc reading on a law the
registration does not use: card 1's footing law carried below its band's floor.
Section 3: the readings E191.md 8.4 registers as reported, by desk arithmetic from the frozen scorer's measured means (its own
score_day() run here): section 6's reading (E189's frozen J over idle beside card 1's measured J over idle and E191's own), section
3's literals (card 1's two rows in place of aifoundry3's, scaled on the frozen terms) and the frozen bands' coverage.
Section 4: the README lines the note cites for the commit message's scan and the window file.

It writes posthoc-note1-e191.json and posthoc-note1-e191.txt beside itself (or in --out), with paths relative to this directory or the
repository's top, times in PST, floats rounded to 9 significant digits and no run time, so a re-run from the same tree under the same
interpreter writes both byte for byte. --data and --top name this directory and the repository's top when the script runs from a copy.
Standard library only. /usr/bin/python3 3.12.3 wrote the committed outputs.
SPDX-License-Identifier: Apache-2.0
"""
import copy
import gzip
import hashlib
import importlib.util
import json
import math
import os
import re
import sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
CONFIGS = ["copy-zeros", "copy-random", "sha256", "sort-sorted", "sort-shuffled", "sparse-parity"]
REG = "tools/claims-v3/e191/SHA256SUMS-e191-registration"
REG189 = "tools/claims-v3/e189/SHA256SUMS-e189-registration"
HOMEP = b"/ho" + b"me/"    # a home-directory path; written split in two, so that a public-text scan of this file does not read it as one
LOGINP = b"<log" + b"in>"  # the collector's placeholder for the box login
CARD = "aifoundry1-c1"
# E191.md section 3's two literals, as registered (its lines 88-89): the frozen value (aifoundry3's) and card 1's row (energy manual 04)
LIT = {"write-back": {"term": "bytes: DRAM write-back", "frozen_pj": 325.8, "card1_pj": 368.9, "configs": ["copy-random"],
                      "e191_md": "the copy's write-back path, random bytes"},
       "l2": {"term": "bytes: L2", "frozen_pj": 2.83, "card1_pj": 3.86, "configs": ["sha256", "sort-sorted", "sort-shuffled"],
              "e191_md": "the L2, for SHA-256 and the sort"}}


def arg(name, default):
    a = sys.argv[1:]
    return a[a.index(name) + 1] if name in a else default


DATA = os.path.abspath(arg("--data", HERE))
TOP = os.path.abspath(arg("--top", os.path.join(DATA, "..", "..", "..", "..")))
OUT = os.path.abspath(arg("--out", DATA))


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def r9(x):
    if isinstance(x, dict):
        return {k: r9(v) for k, v in x.items()}
    if isinstance(x, (list, tuple)):
        return [r9(v) for v in x]
    if isinstance(x, float):
        return x if x == 0.0 or not math.isfinite(x) else float(f"{x:.8e}")
    return x


def lines_with(path, needle):
    return [i for i, ln in enumerate(open(path, encoding="utf-8").read().split("\n"), 1) if needle in ln]


def text_of(path):
    b = open(path, "rb").read()
    return gzip.decompress(b) if path.endswith(".gz") else b


def read_list(path):
    rows = {}
    for ln in open(path):
        if ln.strip():
            h, p = ln.rstrip("\n").split(None, 1)
            rows[p.strip()] = h
    return rows


res = {"what": "E191's second-session data README, dated note 1: post hoc and reported readings of committed files "
               "(decides nothing; scores nothing)", "interpreter": sys.version.split()[0]}
txt = [res["what"], f"interpreter: python {res['interpreter']}", ""]

# ---------------------------------------------------------------- 0. the anchors
sums = read_list(os.path.join(DATA, "SHA256SUMS"))
ok = sum(1 for p, h in sums.items() if os.path.exists(os.path.join(DATA, p)) and sha(os.path.join(DATA, p)) == h)
FILES = sorted(sums) + ["FILES.txt", "README.md", "SHA256SUMS"]    # the data commit's files, and nothing added after them
reg = read_list(os.path.join(TOP, REG))
reg_ok = [p for p, h in reg.items() if sha(os.path.join(TOP, p)) == h]
reg189 = read_list(os.path.join(TOP, REG189))
reg189_ok = [p for p, h in reg189.items() if sha(os.path.join(TOP, p)) == h]
s0 = {"sha256sums_entries": len(sums), "sha256sums_ok": ok, "data_commit_files": len(FILES),
      "readme_sha256": sha(os.path.join(DATA, "README.md")), "sha256sums_sha256": sha(os.path.join(DATA, "SHA256SUMS")),
      "files_txt_sha256": sha(os.path.join(DATA, "FILES.txt")),
      "registration_list_sha256": sha(os.path.join(TOP, REG)), "registration_entries": len(reg), "registration_ok": len(reg_ok),
      "e189_registration_list_sha256": sha(os.path.join(TOP, REG189)), "e189_registration_entries": len(reg189),
      "e189_registration_ok": len(reg189_ok)}
res["s0_anchors"] = s0
txt += ["0. anchors",
        f"  SHA256SUMS: {ok} of {len(sums)} entries OK; with FILES.txt, README.md and SHA256SUMS the data commit's {len(FILES)} files",
        f"  README.md sha256 {s0['readme_sha256']}", f"  SHA256SUMS sha256 {s0['sha256sums_sha256']}",
        f"  FILES.txt sha256 {s0['files_txt_sha256']}",
        f"  {REG}: {len(reg_ok)} of {len(reg)} entries OK (list sha256 {s0['registration_list_sha256']})",
        f"  {REG189}: {len(reg189_ok)} of {len(reg189)} entries OK (list sha256 {s0['e189_registration_list_sha256']})", ""]

# ---------------------------------------------------------------- 1. the scrub
man = read_list(os.path.join(DATA, "session", "MANIFEST.sha256"))
man_ok, man_bad = 0, []
for p, h in sorted(man.items()):
    local = os.path.join(DATA, p) if p.startswith("passes/") else os.path.join(DATA, "session", p)
    if os.path.exists(local) and sha(local) == h:
        man_ok += 1
    else:
        man_bad.append(p)
mapped = set((p if p.startswith("passes/") else "session/" + p) for p in man)
outside = sorted(x for x in FILES if x not in mapped)
kinds = {}
for x in outside:
    k = os.path.basename(x)
    kinds[k] = kinds.get(k, 0) + 1
tilde_out, login_any, home = {}, {}, {}
gz = 0
for x in FILES:
    gz += x.endswith(".gz")
    b = text_of(os.path.join(DATA, x))
    if x in outside and b.count(b"~"):
        tilde_out[x] = b.count(b"~")
    if b.count(LOGINP):
        login_any[x] = b.count(LOGINP)
    if b.count(HOMEP):
        home[x] = b.count(HOMEP)
COL = os.path.join(TOP, "tools/claims-v3/e191/collect_e191.py")
s1 = {"manifest_entries": len(man), "manifest_ok": man_ok, "manifest_bad": man_bad, "outside_manifest": kinds,
      "outside_manifest_files": len(outside), "outside_manifest_with_tilde": tilde_out, "files_with_login_placeholder": login_any,
      "files_with_home_path": home, "gz_files_read_as_text": gz,
      "runner_rc_bytes": open(os.path.join(DATA, "session", "runner.rc"), "rb").read().decode("ascii", "replace"),
      "readme_lines_scrub_ran": lines_with(os.path.join(DATA, "README.md"), "The collector's scrub ran (the box's home path became"),
      "collect_e191_py_replaces_home": lines_with(COL, 'new = data.replace(box_home.encode(), b"~")'),
      "collect_e191_py_replaces_login": lines_with(COL, 'new = login_re(login).sub(b"<login>", new)'),
      "collect_e191_py_prints_collected": lines_with(COL, 'print(f"COLLECTED {rel}'),
      "run_e191_v2_py_writes_the_manifest": lines_with(os.path.join(TOP, "tools/claims-v3/e191/run_e191_v2.py"),
                                                       'with open(os.path.join(out, "MANIFEST.sha256"), "w") as f:')}
res["s1_scrub"] = s1
txt += ["1. the scrub (collect_e191.py's step 4 puts '~' for the box's home path and a placeholder for the box login, in every text file "
        "and every .gz's text)",
        f"  the box's MANIFEST.sha256 (written on the box, last, before the copy-back): {man_ok} of {len(man)} files at their listed "
        f"sha256 in this directory (passes/ here, the rest under session/); not matching: {man_bad if man_bad else 'none'}",
        f"  the data commit's {len(outside)} files outside that list: {json.dumps(kinds, sort_keys=True)}",
        f"  of those, the files holding '~': {json.dumps(tilde_out, sort_keys=True) if tilde_out else 'none'}",
        f"  files of the data commit holding the login placeholder: {json.dumps(login_any, sort_keys=True) if login_any else 'none'}",
        f"  files of the data commit holding a home-directory path (the text inside all {gz} .gz files included): "
        f"{json.dumps(home, sort_keys=True) if home else 'none'}",
        f"  session/runner.rc: {s1['runner_rc_bytes']!r}",
        f"  README.md says the scrub ran and the box's home path became '~' on line(s) {s1['readme_lines_scrub_ran']}",
        f"  tools/claims-v3/e191/collect_e191.py: the home path replaced on line(s) {s1['collect_e191_py_replaces_home']}, the login on "
        f"line(s) {s1['collect_e191_py_replaces_login']}, its COLLECTED line printed on line(s) {s1['collect_e191_py_prints_collected']}",
        f"  tools/claims-v3/e191/run_e191_v2.py writes MANIFEST.sha256 (on the box, last) on line(s) "
        f"{s1['run_e191_v2_py_writes_the_manifest']}", ""]

# ---------------------------------------------------------------- 2. S1T's margin on the starting die (post hoc)
s2 = {"refused": None}
pins_needed = ["tools/ledger/ledger_v2.py", "docs/reports/data/2026-11-12-q166-ledger-v2/frozen-v2.json"]
if len(reg_ok) != len(reg):
    s2["refused"] = "E191's registration list does not read every entry OK"
else:
    spec = importlib.util.spec_from_file_location("forecast_e191_pins", os.path.join(TOP, "tools/claims-v3/e191/forecast_e191.py"))
    FP = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(FP)
    bad = [p for p in pins_needed if sha(os.path.join(TOP, p)) != FP.PINS[p]]
    if bad:
        s2["refused"] = "pinned inputs differ: " + ", ".join(bad)
SC = LV = FC = F = fc = score = None
if s2["refused"] is None:
    spec = importlib.util.spec_from_file_location("score_e191", os.path.join(TOP, "tools/claims-v3/e191/score_e191.py"))
    SC = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(SC)
    LV, FC, F = SC.modules()
    fc = json.load(open(os.path.join(TOP, "tools/claims-v3/e191/forecast-e191.json")))
    score = SC.score_day(DATA, LV, FC, F, fc)        # the frozen scorer's own reading of this directory, as registered
    tol = SC.RULES["E191-S1T"]["tol"]
    passes = {}
    for key in CONFIGS:
        d = os.path.join(DATA, "passes", key)
        passes[key] = [SC.read_pass(os.path.join(d, p), key)[0] for p in sorted(os.listdir(d)) if p.startswith("p")]
        passes[key] = [p for p in passes[key] if p]

    def e_tot(key, delta, FF=None):
        FF = F if FF is None else FF
        ps = passes[key]
        g = [FC.given(fc["configs"][key], p["t_k"], p["t_w"], p["T0"] + delta, FF, LV)["j_total"] for p in ps]
        return (sum(g) / len(g)) / (sum(p["j_total"] for p in ps) / len(ps)) - 1.0

    def verdict(delta, FF=None):
        cs = [{"config": k, "ok_S1T": abs(e_tot(k, delta, FF)) <= tol} for k in CONFIGS]
        c = SC.count_rule("E191-S1T", cs, "ok_S1T")
        return c["verdict"], c["within"]

    def bisect(fn, a, b, steps=60):
        """fn(a) != fn(b): the point where fn changes, to below 1e-9 C."""
        fa = fn(a)
        for _ in range(steps):
            m = 0.5 * (a + b)
            if fn(m) == fa:
                a = m
            else:
                b = m
        return 0.5 * (a + b)

    def changes(fn, lo=-5.0, hi=5.0, n=1000):
        """Every change of fn on a grid of n steps over [lo, hi], each refined by bisection: (delta, value before, value after),
        reading from 0 outward on each side."""
        out = []
        for side, end in (("lower", lo), ("upper", hi)):
            prev_d, prev_v = 0.0, fn(0.0)
            for i in range(1, n // 2 + 1):
                d = end * i / (n // 2)
                v = fn(d)
                if v != prev_v:
                    out.append({"side": side, "delta_c": round(bisect(fn, prev_d, d), 3), "from": prev_v, "to": v})
                prev_d, prev_v = d, v
        return out

    laws = {}
    for key in CONFIGS:
        for p in passes[key]:
            law = FC.given(fc["configs"][key], p["t_k"], p["t_w"], p["T0"], F, LV)["rest_law"]
            laws[law] = laws.get(law, 0) + 1
    reg_e = {k: e_tot(k, 0.0) for k in CONFIGS}
    same_as_scorer = max(abs(reg_e[k] - score["configs"][k]["e_j_total"]) for k in CONFIGS)
    v0 = verdict(0.0)
    cross = {k: changes(lambda d, k=k: abs(e_tot(k, d)) <= tol) for k in CONFIGS}
    flips = changes(lambda d: verdict(d)[0])
    counts = changes(lambda d: verdict(d)[1])
    grid = {}
    for d in (-1.0, -0.9, -0.7, -0.5, 0.2, 0.5, 1.0):
        v = verdict(d)
        grid[f"{d:+.1f}"] = {"e_j_total": {k: e_tot(k, d) for k in CONFIGS}, "verdict": v[0], "within": v[1]}
    t0s = sorted(p["T0"] for k in CONFIGS for p in passes[k])
    band = list(F["idle_laws"][CARD]["quad_band_c"])
    # post hoc, a law the registration does not use: card 1's footing law carried below its band's floor (to 40 C)
    G = copy.deepcopy(F)
    G["idle_laws"][CARD]["quad_band_c"] = [40.0, band[1]]
    alt_e = {k: e_tot(k, 0.0, G) for k in CONFIGS}
    alt_v = verdict(0.0, G)
    alt_law = {}
    for key in CONFIGS:
        for p in passes[key]:
            law = FC.given(fc["configs"][key], p["t_k"], p["t_w"], p["T0"], G, LV)["rest_law"]
            alt_law[law] = alt_law.get(law, 0) + 1
    s2 = {"refused": None, "label": "post hoc (delta = 0 is the registered reading)", "tol": tol,
          "passes_read": {k: len(passes[k]) for k in CONFIGS}, "t0_min": t0s[0], "t0_max": t0s[-1],
          "footing_band_c": band, "rest_law_at_delta_0": laws, "registered_e_j_total": reg_e,
          "registered_vs_frozen_scorer_max_abs_diff": same_as_scorer, "registered_verdict": v0[0], "registered_within": v0[1],
          "frozen_scorer_s1t": {"verdict": score["rules"]["E191-S1T"]["verdict"], "within": score["rules"]["E191-S1T"]["within"]},
          "within_changes_by_config": cross, "verdict_changes": flips, "within_count_changes": counts, "at_delta": grid,
          "law_carried_below_floor": {"label": "post hoc, a law the registration does not use (card 1's footing law carried "
                                               "from its floor down to 40 C); never a reading of the day",
                                      "quad_band_c": G["idle_laws"][CARD]["quad_band_c"], "rest_law": alt_law,
                                      "e_j_total": alt_e, "verdict": alt_v[0], "within": alt_v[1]}}
res["s2_s1t_margin"] = s2
txt.append("2. S1T's margin on the starting die (post hoc; delta = 0 is the registered reading)")
if s2["refused"]:
    txt.append(f"  REFUSED: {s2['refused']}")
else:
    txt += [f"  read by the frozen scorer's read_pass: {json.dumps(s2['passes_read'])}; T0 (die_c.before) {s2['t0_min']}-{s2['t0_max']} C; "
            f"card 1's footing law's band {band} C; the rest law at delta 0: {json.dumps(laws, sort_keys=True)}",
            f"  registered (delta 0): S1T {v0[0]}, {v0[1]} of 6 within {tol:.0%} (the frozen scorer's own run: "
            f"{s2['frozen_scorer_s1t']['verdict']}, {s2['frozen_scorer_s1t']['within']} of 6; e_j_total equal to it within "
            f"{same_as_scorer:.1e}); e_j_total " + ", ".join(f"{k} {reg_e[k]:+.6f}" for k in CONFIGS)]
    for k in CONFIGS:
        ch = "; ".join(f"{c['side']} side at {c['delta_c']:+.3f} C ({'inside' if c['from'] else 'outside'} to "
                       f"{'inside' if c['to'] else 'outside'})" for c in cross[k]) or "no change between -5 and +5 C"
        txt.append(f"  {k}: within {tol:.0%} at delta 0: {abs(reg_e[k]) <= tol}; changes: {ch}")
    txt.append("  S1T's word changes: " + ("; ".join(f"{c['side']} side at {c['delta_c']:+.3f} C ({c['from']} to {c['to']})"
                                                     for c in flips) or "none between -5 and +5 C"))
    txt.append("  the count within changes: " + "; ".join(f"{c['side']} side at {c['delta_c']:+.3f} C ({c['from']} to {c['to']})"
                                                          for c in counts))
    for d, g in grid.items():
        txt.append(f"  delta {d} C: S1T {g['verdict']}, {g['within']} of 6 within; "
                   + ", ".join(f"{k} {g['e_j_total'][k]:+.6f}" for k in CONFIGS))
    lc = s2["law_carried_below_floor"]
    txt.append(f"  post hoc, a law the registration does not use (the footing law carried down to 40 C; rest law "
               f"{json.dumps(alt_law, sort_keys=True)}): S1T {lc['verdict']}, {lc['within']} of 6 within; "
               + ", ".join(f"{k} {alt_e[k]:+.6f}" for k in CONFIGS))
txt.append("")

# ---------------------------------------------------------------- 3. E191.md 8.4's reported readings (desk arithmetic)
s3 = {"refused": s2["refused"]}
if score is not None:
    md = os.path.join(TOP, "tools/claims-v3/e191/E191.md")
    e189 = json.load(open(os.path.join(TOP, "tools/claims-v3/e189/forecast-e189.json")))
    rows6 = {}
    for k in CONFIGS:
        c = score["configs"][k]
        m, own = c["measured_j_over_mean"], c["given_j_over_mean"]
        a3 = e189["configs"][k]["j_over_idle"]
        pt = fc["configs"][k]["j_over_idle"]
        e_a3, e_own = a3 / m - 1.0, own / m - 1.0
        rows6[k] = {"measured_j_over_mean": m, "e191_given_mean": own, "e191_frozen_point": pt, "e189_frozen_j_over_idle": a3,
                    "e_e189_prices": e_a3, "e_e191_own": e_own, "e_e191_frozen_point": pt / m - 1.0,
                    "nearer": "E189's (aifoundry3's prices)" if abs(e_a3) < abs(e_own) else "E191's own (card 1's prices)",
                    "abs_gap": abs(abs(e_a3) - abs(e_own))}
    rows3 = {}
    lit_lines = {}
    for name, L in LIT.items():
        lit_lines[name] = [i for i in lines_with(md, f"{L['frozen_pj']} pJ/B") if i in lines_with(md, f"{L['card1_pj']} pJ/B")]
        for k in L["configs"]:
            c = score["configs"][k]
            t = fc["configs"][k]["terms"][L["term"]]["j"]
            delta = t * (L["card1_pj"] / L["frozen_pj"] - 1.0)
            m, own = c["measured_j_over_mean"], c["given_j_over_mean"]
            rows3[k] = {"literal": name, "frozen_term_j": t, "bytes_implied": t / (L["frozen_pj"] * 1e-12), "delta_j": delta,
                        "delta_share_of_frozen_point": delta / fc["configs"][k]["j_over_idle"],
                        "e_registered": own / m - 1.0, "e_with_card1_row": (own + delta) / m - 1.0}
    cover = {}
    for k in CONFIGS:
        c = score["configs"][k]
        r = fc["configs"][k]
        cover[k] = {"measured_j_over_mean": c["measured_j_over_mean"], "j_over_idle_band": r["j_over_idle_band"],
                    "j_over_inside": c["j_over_inside_frozen_band"], "measured_j_total_mean": c["measured_j_total_mean"],
                    "j_total_band": r["j_total_band"], "j_total_inside": c["j_total_inside_frozen_band"],
                    "t_k_mean": c["t_k_mean"], "t_band": c["t_band"], "t_inside": c["t_inside_band"]}
    s3 = {"refused": None, "label": "REPORTED (E191.md 8.4): desk arithmetic from the frozen scorer's measured means; decides nothing",
          "section6_reading": rows6, "section6_line": lines_with(md, "One more reading, REPORTED and never scored"),
          "section3_literals": rows3, "section3_lines": lit_lines, "band_coverage": cover,
          "band_coverage_counts": {"j_over_inside": sum(cover[k]["j_over_inside"] for k in CONFIGS),
                                   "j_total_inside": sum(cover[k]["j_total_inside"] for k in CONFIGS),
                                   "t_inside": sum(cover[k]["t_inside"] for k in CONFIGS)}}
res["s3_reported_8_4"] = s3
txt.append("3. E191.md 8.4's reported readings (REPORTED: desk arithmetic from the frozen scorer's measured means; deciding nothing)")
if s3["refused"]:
    txt.append(f"  REFUSED: {s3['refused']}")
else:
    txt.append(f"  section 6's reading (E191.md line(s) {s3['section6_line']}): E189's frozen J over idle (aifoundry3's prices) beside card 1's "
               "measured J over idle and E191's own given J over idle")
    for k, r in rows6.items():
        txt.append(f"  {k}: measured {r['measured_j_over_mean']:.5f} J; E189's {r['e189_frozen_j_over_idle']:.5f} ({r['e_e189_prices']:+.4%}); "
                   f"E191's given {r['e191_given_mean']:.5f} ({r['e_e191_own']:+.4%}; its frozen point {r['e191_frozen_point']:.5f}, "
                   f"{r['e_e191_frozen_point']:+.4%}); nearer: {r['nearer']} by {r['abs_gap']:.4%}")
    txt.append(f"  section 3's literals (E191.md line(s) {lit_lines}): the frozen term scaled by card 1's row over the frozen literal")
    for k, r in rows3.items():
        txt.append(f"  {k} ({r['literal']}): frozen term {r['frozen_term_j']:.6f} J ({r['bytes_implied']:.6e} B implied); +{r['delta_j']:.6f} J "
                   f"({r['delta_share_of_frozen_point']:+.3%} of the frozen J over idle); error {r['e_registered']:+.4%} as registered, "
                   f"{r['e_with_card1_row']:+.4%} with card 1's row")
    txt.append(f"  the frozen bands' coverage: J over idle inside for {s3['band_coverage_counts']['j_over_inside']} of 6, J with the card at "
               f"rest for {s3['band_coverage_counts']['j_total_inside']} of 6, the mean t_k for {s3['band_coverage_counts']['t_inside']} of 6")
    for k, c in cover.items():
        txt.append(f"  {k}: J over idle {c['measured_j_over_mean']:.5f} in {c['j_over_idle_band']}: {c['j_over_inside']}; J at rest "
                   f"{c['measured_j_total_mean']:.5f} in {c['j_total_band']}: {c['j_total_inside']}; mean t_k {c['t_k_mean']:.6f} s in "
                   f"{c['t_band']}: {c['t_inside']}")
txt.append("")

# ---------------------------------------------------------------- 4. the README lines cited, and the reducer's grid step (arithmetic)
RED = os.path.join(TOP, "workloads/sparseparity/tools/energy_reduce.py")
t0 = float(json.load(open(os.path.join(DATA, "session", "queue.json")))["t0"])
step = (t0 + 0.005) - t0
s4 = {"readme_commit_message_scan": lines_with(os.path.join(DATA, "README.md"), "message read 0 lines and 0 sanitizer hits"),
      "readme_window_file": lines_with(os.path.join(DATA, "README.md"), "is the moment step 1 wrote it, not his go"),
      "reducer_integrate_def": lines_with(RED, "def integrate(t, y, a, b, step=0.005):"),
      "reducer_integrate_grid": lines_with(RED, "g = np.arange(a, b, step)"),
      "reducer_integrate_sum": lines_with(RED, "return float(np.interp(g, t, y).sum() * step)"),
      "t0_s": t0, "float_spacing_at_t0_s": math.ulp(t0), "rounded_step_at_t0_s": step, "rounded_step_rel": step / 0.005 - 1.0,
      "one_spacing_lower_rel": (step - math.ulp(t0)) / 0.005 - 1.0}
res["s4_readme_lines_and_grid"] = s4
txt += ["4. README.md's lines cited, and the reducer's grid step (arithmetic)",
        f"  the commit message's scan ('... message read 0 lines and 0 sanitizer hits'): line(s) {s4['readme_commit_message_scan']}",
        f"  the window file's RB_GO_EPOCH ('... is the moment step 1 wrote it, not his go'): line(s) {s4['readme_window_file']}",
        f"  workloads/sparseparity/tools/energy_reduce.py: integrate() on line(s) {s4['reducer_integrate_def']}, its grid by numpy's arange "
        f"on line(s) {s4['reducer_integrate_grid']}, its sum times the nominal step on line(s) {s4['reducer_integrate_sum']}",
        f"  at the session's T0 {t0:.0f} s the float spacing is {s4['float_spacing_at_t0_s']:.6e} s; fl(T0 + 0.005) - T0 = "
        f"{step!r} s ({s4['rounded_step_rel']:+.3e} relative to 5 ms; one spacing lower: {s4['one_spacing_lower_rel']:+.3e})", ""]

os.makedirs(OUT, exist_ok=True)
with open(os.path.join(OUT, "posthoc-note1-e191.json"), "w") as f:
    json.dump(r9(res), f, indent=1, sort_keys=True)
    f.write("\n")
with open(os.path.join(OUT, "posthoc-note1-e191.txt"), "w") as f:
    f.write("\n".join(txt) + "SPDX-License-Identifier: Apache-2.0\n")
print("\n".join(txt))
