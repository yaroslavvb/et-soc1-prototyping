#!/usr/bin/env python3
"""E178's data README, dated note 1 (Fri 6 Nov 2026, after the card day's data verifier): every figure the note cites, read from this
directory's committed files (the data commit's 347: the 345 that SHA256SUMS lists, README.md and SHA256SUMS) and, as text only, from
three committed files of the kit that the note quotes (tools/claims-v3/e178/E178.md, power_e178.py and score_e178.py). Standard library
only: it imports no lab module, changes no file it reads, and writes two files beside itself, byte for byte the same on every run with
the same interpreter (the Intel's /usr/bin/python3, 3.9; the draws below use random.Random with fixed seeds):

    /usr/bin/python3 -B posthoc_note1_e178.py        # writes posthoc-note1-e178.txt and posthoc-note1-e178.json

  section 1  the equal-flip groups of E178-E and the reported pairs inside them (the verifier's fault 1 (a));
  section 2  the couple rules pass by pass and couple by couple: his pair's per-pass values and its interval re-made by the registered
             statistic, and a post hoc reading of the couples' own scatter, which decides nothing (fault 1 (b));
  section 3  the directory's files by class, what a reader that skips every file that does not decode as UTF-8 reads of them, and two
             of the public-text scan's patterns counted over every file, the tiles byte by byte (fault 1 (c)).

Nothing here is a rule or a verdict: sections 1 and 3 re-read committed figures, and section 2's last block is post hoc.
SPDX-License-Identifier: Apache-2.0
"""
import ast
import gzip
import hashlib
import json
import math
import os
import random
import re
import statistics
import sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
KIT = os.path.normpath(os.path.join(HERE, "..", "..", "..", "..", "tools", "claims-v3", "e178"))
OUT_TXT = os.path.join(HERE, "posthoc-note1-e178.txt")
OUT_JSON = os.path.join(HERE, "posthoc-note1-e178.json")
MINUS = "−"
DRAWS = 40000
SEED = 17890  # the draws of section 2's post hoc block: random.Random(SEED + the rule's index in COUPLE_RULES)
COUPLE_RULES = ["E178-H-int8", "E178-H-fp32", "E178-H-fp16", "E178-U"]
lines = []
out = {"_note": "E178's data README, dated note 1: figures re-read from the committed data (posthoc_note1_e178.py); post hoc, no verdict"}


def say(s=""):
    lines.append(s)


def sha(path):
    return hashlib.sha256(open(path, "rb").read()).hexdigest()


def f4(x):
    """four decimals with the README's sign characters (+ and the minus sign U+2212)"""
    s = f"{x:+.4f}"
    return s.replace("-", MINUS)


def rel(p):
    return os.path.relpath(p, HERE)


# ---- inputs ----
SUMS = os.path.join(HERE, "SHA256SUMS")
listed = {}
for ln in open(SUMS, encoding="utf-8"):
    if ln.strip():
        h, name = ln.rstrip("\n").split("  ", 1)
        listed[name] = h
committed = sorted(set(listed) | {"README.md", "SHA256SUMS"})
bad_sums = sorted(n for n, h in listed.items() if sha(os.path.join(HERE, n)) != h)
readme = open(os.path.join(HERE, "README.md"), encoding="utf-8").read()
readme_lines = readme.split("\n")
kit_text = {n: open(os.path.join(KIT, n), encoding="utf-8").read() for n in ("E178.md", "power_e178.py", "score_e178.py")}
S = json.load(open(os.path.join(HERE, "scored.json"), encoding="utf-8"))
P = S["primary"]
out["inputs"] = {"committed_files": len(committed), "sha256sums_listed": len(listed), "sha256sums_bad": bad_sums,
                 "scored_json_sha256": listed["scored.json"], "readme_sha256": sha(os.path.join(HERE, "README.md")),
                 "kit_text_sha256": {n: hashlib.sha256(t.encode("utf-8")).hexdigest() for n, t in sorted(kit_text.items())}}
say("E178's data README, dated note 1: the figures it cites, re-read from the committed data (posthoc_note1_e178.py)")
say("")
say("== inputs")
say(f"the data commit's files: {len(committed)} (SHA256SUMS lists {len(listed)}; README.md and SHA256SUMS beside); "
    f"SHA256SUMS re-hashed here: {len(listed) - len(bad_sums)} of {len(listed)} OK")
say(f"scored.json sha256 {listed['scored.json']} (its SHA256SUMS line)")
for n, t in sorted(kit_text.items()):
    say(f"read as text: tools/claims-v3/e178/{n} sha256 {hashlib.sha256(t.encode('utf-8')).hexdigest()}")


def readme_where(phrase):
    return [i + 1 for i, ln in enumerate(readme_lines) if phrase in ln]


# ---- section 1: the equal-flip groups ----
say("")
say("== section 1: E178-E's equal-flip groups, and the reported equal-flip pairs inside them (fault 1 (a))")
row = [i + 1 for i, ln in enumerate(kit_text["E178.md"].split("\n")) if ln.startswith("| **E178-E-int8**")]
lim = re.search(r"\(weak by design: [^)]*\)", kit_text["E178.md"].split("\n")[row[0] - 1]).group(0) if row else None
say(f"E178.md section 5, the E178-E row (line {row[0] if row else '?'}): its power cell ends {lim!r}")
pairs = P["reported"]["pairs"]["equal_flips_different_values"]
sec1 = {"e178_md_row_line": row[0] if row else None, "e178_md_limit": lim, "groups": {}, "pairs_total": len(pairs)}
inside_total = 0
for fmt in ("int8", "fp32", "fp16"):
    r = P["rules"]["E178-E-" + fmt]
    D = r["D_w"]
    lo_k = min(D, key=D.get)
    hi_k = max(D, key=D.get)
    spread = D[hi_k] - D[lo_k]
    inside = [x for x in pairs if x["a"] in r["members"] and x["b"] in r["members"]]
    inside_total += len(inside)
    res = [x for x in inside if x["sign"] != "NOT RESOLVED"]
    g = {"verdict": r["verdict"], "reading": r["reading"], "spread_w": r["spread_w"], "line_w": r["line_w"],
         "spread_equals_max_minus_min": abs(spread - r["spread_w"]) < 1e-12, "lowest": [lo_k, D[lo_k]], "highest": [hi_k, D[hi_k]],
         "members": {k: D[k] for k in r["members"]}, "pairs_inside": len(inside),
         "resolved_inside": [{"a": x["a"], "b": x["b"], "n": x["n"], "mean_w": x["mean_w"], "lo95_w": x["lo95_w"], "hi95_w": x["hi95_w"],
                              "dP_w": x["dP_w"], "P_inside": x["P_inside"], "sign": x["sign"]} for x in res]}
    sec1["groups"][fmt] = g
    say(f"E178-E-{fmt}: {r['verdict']} ({r['reading']}): spread {r['spread_w']:.4f} W (max - min, {hi_k} {D[hi_k]:.4f} W less "
        f"{lo_k} {D[lo_k]:.4f} W) against its 95% line {r['line_w']:.4f} W; members " +
        ", ".join(f"{k} {D[k]:.4f}" for k in r["members"]))
    say(f"  reported equal-flip pairs inside the group: {len(inside)}; resolved (sign not NOT RESOLVED): {len(res)}")
    for x in res:
        say(f"    {x['a']} - {x['b']}: {f4(x['mean_w'])} [{f4(x['lo95_w'])}, {f4(x['hi95_w'])}] W, n {x['n']}, {x['sign']}; "
            f"dP {f4(x['dP_w'])} W, P inside: {x['P_inside']}")
resolved_all = [x for x in pairs if x["sign"] != "NOT RESOLVED"]
sec1["pairs_inside_groups"] = inside_total
sec1["resolved_all"] = len(resolved_all)
say(f"all {len(pairs)} reported equal-flip pairs: {inside_total} inside E178-E's three groups; {len(resolved_all)} resolved, every one "
    f"inside a group")
sec1["readme_lines"] = {p: readme_where(p) for p in ("read alike", "equal-flip kinds read equal in all three formats",
                                                     "the equal-flip groups in all three formats")}
chk = {}
for fmt, g in sec1["groups"].items():
    chk[f"E178-E-{fmt} spread {g['spread_w']:.4f} printed"] = f"spread {g['spread_w']:.4f}" in readme
    for x in g["resolved_inside"]:
        txt = f"{f4(x['mean_w'])} [{f4(x['lo95_w'])}, {f4(x['hi95_w'])}]"
        chk[f"{x['a']} - {x['b']} {txt} printed"] = txt in readme
sec1["readme_checks"] = chk
say("README lines: " + "; ".join(f"{p!r} at {v}" for p, v in sec1["readme_lines"].items()))
say("README transcription checks: " + "; ".join(f"{k}: {v}" for k, v in chk.items()))
out["section_1"] = sec1

# ---- section 2: the couple rules, pass by pass ----
say("")
say("== section 2: the couple rules pass by pass (fault 1 (b)); the last block is post hoc and decides nothing")
T975 = ast.literal_eval(re.search(r"^T975 = (\{[^}]*\})", kit_text["power_e178.py"], re.M).group(1))
EXT = ast.literal_eval(re.search(r"for k, v in (\{[0-9:., ]*\})\.items\(\)", kit_text["score_e178.py"]).group(1))
TT = dict(T975)
TT.update({k: v for k, v in EXT.items() if k not in TT})
say(f"t(0.975, df) as registered: power_e178.T975 {T975}, with score_e178's {EXT} beside")


def ratio_draws(ks, seed):
    """the fraction of draws, couples independent N(0, 1), whose ratio (sd of the pass means over the pooled within-pass sd times
    sqrt(mean 1/k)) is at or below the observed one; ks = the number of couples in each pass"""
    rng = random.Random(seed)
    vals = []
    for _ in range(DRAWS):
        means, ss, df = [], 0.0, 0
        for k in ks:
            d = [rng.gauss(0.0, 1.0) for _ in range(k)]
            m = sum(d) / k
            means.append(m)
            ss += sum((a - m) ** 2 for a in d)
            df += k - 1
        vals.append(statistics.stdev(means) / (math.sqrt(ss / df) * math.sqrt(sum(1 / k for k in ks) / len(ks))))
    return vals


sec2 = {}
for idx, name in enumerate(COUPLE_RULES):
    r = P["rules"][name]
    pp = r["per_pass"]
    passes = sorted(pp)
    xs = [pp[p]["x"] for p in passes]
    ks = [len(pp[p]["segment_diffs"]) for p in passes]
    n = len(xs)
    m = statistics.mean(xs)
    hw = TT[n - 1] * statistics.stdev(xs) / math.sqrt(n)
    lo, hi = m - hw, m + hw
    same = max(abs(m - r["mean_w"]), abs(lo - r["lo95_w"]), abs(hi - r["hi95_w"])) < 1e-12
    ss, dfw = 0.0, 0
    neg = []
    for p in passes:
        d = pp[p]["segment_diffs"]
        mp = sum(d) / len(d)
        ss += sum((a - mp) ** 2 for a in d)
        dfw += len(d) - 1
        neg.append(sum(1 for a in d if a < 0))
    sd_c = math.sqrt(ss / dfw)
    sd_pass = statistics.stdev(xs)
    expected = sd_c * math.sqrt(sum(1 / k for k in ks) / n)
    ratio = sd_pass / expected
    hw_c = TT[dfw] * sd_c * math.sqrt(sum(1 / k for k in ks)) / n
    draws = ratio_draws(ks, SEED + idx)
    frac = sum(1 for v in draws if v <= ratio) / DRAWS
    e = {"a": r["a"], "b": r["b"], "verdict": r["verdict"], "n": n, "couples_per_pass": dict(zip(passes, ks)),
         "per_pass_x_w": dict(zip(passes, xs)), "segment_diffs_w": {p: pp[p]["segment_diffs"] for p in passes},
         "negative_couples_per_pass": dict(zip(passes, neg)), "negative_couples": sum(neg), "couples": sum(ks),
         "mean_w": m, "lo95_w": lo, "hi95_w": hi, "t": TT[n - 1], "equals_scored_json": same,
         "posthoc": {"couple_sd_pooled_within_w": sd_c, "couple_df": dfw, "pass_mean_sd_w": sd_pass,
                     "pass_mean_sd_expected_from_couples_w": expected, "ratio": ratio,
                     "draws": DRAWS, "seed": SEED + idx, "fraction_of_draws_at_or_below_ratio": frac,
                     "couple_error_reading": {"t": TT[dfw], "halfwidth_w": hw_c, "lo95_w": m - hw_c, "hi95_w": m + hw_c}}}
    sec2[name] = e
    say(f"{name} ({r['a']} - {r['b']}): {r['verdict']}; per pass " +
        ", ".join(f"{p} {f4(x)} ({k} couples, {q} below 0)" for p, x, k, q in zip(passes, xs, ks, neg)))
    say(f"  the registered interval re-made: {f4(m)} [{f4(lo)}, {f4(hi)}] W, n {n}, t {TT[n - 1]}; equals scored.json to 1e-12: "
        f"{same}")
    say("  couples: " + "; ".join(f"{p} " + ", ".join(f4(a) for a in pp[p]["segment_diffs"]) for p in passes))
    say(f"  post hoc: the couples' sd pooled within passes {sd_c:.4f} W ({dfw} df); the pass means' sd {sd_pass:.4f} W against "
        f"{expected:.4f} W expected from the couples' scatter; ratio {ratio:.3f}; draws at or below it {frac:.4f} "
        f"({DRAWS} draws, seed {SEED + idx})")
    say(f"  post hoc, not registered: the mean of the pass means with the couples' scatter as its error, {f4(m)} "
        f"{chr(177)} {hw_c:.4f} W (t({dfw}) {TT[dfw]}) = [{f4(m - hw_c)}, {f4(m + hw_c)}]")
fl = [sec2[k]["posthoc"]["ratio"] for k in COUPLE_RULES[1:]]
say(f"the three float couple rules' ratios: {min(fl):.3f} to {max(fl):.3f}; his pair's {sec2['E178-H-int8']['posthoc']['ratio']:.3f}")
pf = [x for x in P["reported"]["pairs"]["his_4_5"] if x["a"] == "int8.e178_v5"][0]
arms = {k: {"kept_passes": v.get("kept_passes"), "E178-H-int8": (v.get("verdicts") or {}).get("E178-H-int8")}
        for k, v in sorted(S["arms"].items())}
w = P["rules"]["E178-W-int8"]
wk = {k: w[k] for k in sorted(w) if isinstance(w[k], (int, float, str)) and not isinstance(w[k], bool)}
RAIL = json.load(open(os.path.join(HERE, "rail-arm-e178.json"), encoding="utf-8"))
rc = [c for c in RAIL["contrasts"] if c["name"] == "E178-H-int8"][0]["rail"]
sec2["beside_his_pair"] = {"pass_form": {"mean_w": pf["mean_w"], "lo95_w": pf["lo95_w"], "hi95_w": pf["hi95_w"], "n": pf["n"],
                                         "sign": pf["sign"]}, "arms": arms, "E178-W-int8": wk,
                           "rail_column": {k: rc[k] for k in ("mean_w", "lo95_w", "hi95_w", "n", "interval_reads")}}
say(f"beside his pair: the reported pass form {f4(pf['mean_w'])} [{f4(pf['lo95_w'])}, {f4(pf['hi95_w'])}] W, n {pf['n']}, {pf['sign']}; "
    f"the rail arm's minion-rail column (rail-arm-e178.json) {f4(rc['mean_w'])} [{f4(rc['lo95_w'])}, {f4(rc['hi95_w'])}] W, "
    f"{rc['interval_reads']}")
say("  the seven reduction arms' E178-H-int8: " + "; ".join(f"{k} {v['E178-H-int8']} ({len(v['kept_passes'] or [])} passes)"
                                                         for k, v in arms.items()))
say("  E178-W-int8: " + ", ".join(f"{k} {v}" for k, v in wk.items()))
sec2["_registered_couple_sd_w"] = 0.125
sec2["readme_lines"] = {p: readme_where(p) for p in ("resolved in", "all four passes", "the int8 couple's per-pass sd")}
say("README lines: " + "; ".join(f"{p!r} at {v}" for p, v in sec2["readme_lines"].items()))
out["section_2"] = sec2

# ---- section 3: the files by class ----
say("")
say("== section 3: the directory's files by class, and what a UTF-8 reader reads of them (fault 1 (c))")
cls = {"text": [], "gz": [], "tile": []}
for f in committed:
    cls["gz" if f.endswith(".gz") else ("tile" if f.endswith(".bin") else "text")].append(f)
text_not_utf8 = []
for f in cls["text"]:
    try:
        open(os.path.join(HERE, f), "rb").read().decode("utf-8")
    except UnicodeDecodeError:
        text_not_utf8.append(f)
tile_utf8, tile_not = [], []
by_fmt = {}
printable = {}
for f in cls["tile"]:
    b = open(os.path.join(HERE, f), "rb").read()
    fmt = os.path.basename(f).split(".")[0]
    try:
        b.decode("utf-8")
        tile_utf8.append(f)
        by_fmt.setdefault(fmt, [0, 0])[0] += 1
    except UnicodeDecodeError:
        tile_not.append(f)
        by_fmt.setdefault(fmt, [0, 0])[1] += 1
    runs = re.findall(rb"[ -~]{8,}", b)
    if runs:
        printable[f] = sorted({chr(c) for r_ in runs for c in r_})


def utf8_reader(files):
    """what a reader that opens every non-.gz file as UTF-8 text and skips any that fails reads (the files as counted), and the .gz"""
    n = g = 0
    for f in files:
        if f.endswith(".gz"):
            g += 1
            continue
        try:
            open(os.path.join(HERE, f), "rb").read().decode("utf-8")
            n += 1
        except UnicodeDecodeError:
            pass
    return n, g


before = [f for f in committed if f not in ("README.md", "SHA256SUMS")]
r_before = utf8_reader(before)
r_all = utf8_reader(committed)
HOME_RX = re.compile("/" + "home" + "/" + r"([A-Za-z0-9_.-]+)")
KEY_RX = re.compile(r"\b" + "ro" + "ot" + r"\b(?![\s-]+(?:caus|port|complex))", re.I)
owner = None
for f in committed:
    if f.endswith("configs.json"):
        m = re.search(r'"[a-z]+": "' + "/" + "home" + "/" + r'([A-Za-z0-9_.-]+)/aifoundry"', open(os.path.join(HERE, f), encoding="utf-8").read())
        if m:
            owner = m.group(1)
            break
counts = {}
for c, files in cls.items():
    h_own = h_other = k = 0
    for f in files:
        b = open(os.path.join(HERE, f), "rb").read()
        s = gzip.decompress(b).decode("utf-8", "replace") if c == "gz" else (b.decode("latin-1") if c == "tile" else b.decode("utf-8"))
        for mm in HOME_RX.finditer(s):
            if mm.group(1) == owner:
                h_own += 1
            else:
                h_other += 1
        k += len(KEY_RX.findall(s))
    counts[c] = {"home_path_owner": h_own, "home_path_other": h_other, "tree_key_word": k}
sec3 = {"files": len(committed), "text": len(cls["text"]), "gz": len(cls["gz"]), "tiles": len(cls["tile"]),
        "text_not_utf8": text_not_utf8, "tiles_utf8": len(tile_utf8), "tiles_not_utf8": len(tile_not),
        "tiles_by_format_utf8_not": {k: by_fmt[k] for k in sorted(by_fmt)},
        "utf8_reader_without_readme_and_sums": {"files_read": r_before[0], "gz": r_before[1]},
        "utf8_reader_all": {"files_read": r_all[0], "gz": r_all[1]},
        "tiles_with_8_printable_bytes_in_a_row": {f: v for f, v in sorted(printable.items())},
        "owner_from_configs_tree_key": owner is not None, "pattern_counts_every_file": counts,
        "readme_lines": {p: readme_where(p) for p in ("262 text files", "scanned on their own")}}
say(f"files: {len(committed)} = {len(cls['text'])} text (README.md and SHA256SUMS among them; {len(text_not_utf8)} not UTF-8) + "
    f"{len(cls['gz'])} .gz + {len(cls['tile'])} tiles (.bin)")
say(f"tiles whose bytes decode as UTF-8: {len(tile_utf8)}; that do not: {len(tile_not)}; by format (decode, not): " +
    ", ".join(f"{k} {v[0]}/{v[1]}" for k, v in sorted(by_fmt.items())))
say(f"a UTF-8 reader that skips what fails, over every file but README.md and SHA256SUMS: {r_before[0]} files read and {r_before[1]} "
    f".gz ({len(cls['text']) - 2} text + {r_before[0] - (len(cls['text']) - 2)} tiles); over all {len(committed)}: {r_all[0]} and {r_all[1]}")
say(f"tiles with 8 or more printable bytes in a row: {len(printable)}: " +
    "; ".join(f"{f} {''.join(v)!r}" for f, v in sorted(printable.items())))
say("two of the public-text scan's patterns over every file (text as UTF-8, the .gz decompressed, the tiles byte by byte): " +
    "; ".join(f"{c}: the owner's own box home path {v['home_path_owner']}, another account's {v['home_path_other']}, the configs' "
              f"tree-key word {v['tree_key_word']}" for c, v in counts.items()))
say(f"  in all: the owner's own box home path {sum(v['home_path_owner'] for v in counts.values())}, another account's "
    f"{sum(v['home_path_other'] for v in counts.values())}, the configs' tree-key word {sum(v['tree_key_word'] for v in counts.values())} "
    f"(the account read from the configs' tree key, never printed: {'found' if owner else 'NOT FOUND'})")
say("README lines: " + "; ".join(f"{p!r} at {v}" for p, v in sec3["readme_lines"].items()))
out["section_3"] = sec3

say("")
say("== the README lines the note's sections 4 and 5 cite (the post's next clause; the score and step 22's later gates)")
cite = {p: readme_where(p) for p in ("until ~13:49 PST", "after its C-session gate", "## Who checked it")}
say("README lines: " + "; ".join(f"{p!r} at {v}" for p, v in cite.items()))
out["readme_lines_sections_4_5"] = cite

say("")
say("nothing here is a rule or a verdict; every rule, verdict and figure of README.md stands but the sentences the note corrects")
open(OUT_TXT, "w", encoding="utf-8").write("\n".join(lines) + "\n")
open(OUT_JSON, "w", encoding="utf-8").write(json.dumps(out, indent=1, sort_keys=True, ensure_ascii=False) + "\n")
print("\n".join(lines))
