#!/usr/bin/env python3
"""E132, corrections after verification (Mon 2 Nov 2026): the numbers the README's C1-C5 quote, from committed files only.

Post hoc, deciding nothing; standard library only; run from the lab repo's root:

    python3 docs/reports/data/2026-11-02-e132-memory-split/corrections_e132.py > docs/reports/data/2026-11-02-e132-memory-split/corrections_e132.txt

C1  which committed tools/ettelem/ettelem.cpp the box's binary matches (its usage line and the box tree's source hash are in
    logs/ettelem-binary-check.txt), and whether `config`, `sample` and the reset differ between that source and the reviewed one.
C2  the two DDR fields in the telemetry: die_mv.ddr (GET_ASIC_VOLTAGE's PVT memory-shire reading, the rail the reducer reads)
    against reg_mv.ddr (GET_MODULE_VOLTAGE's PMIC DDR voltage register).
C3  the session's peak board power and die readings, what was running at each peak, and whether the SP's since-reset maximum,
    the PVT latches, the statistics-reset field or the clock ever changed.
C4  what R_all is made of: the rungs, the hart stream's share, D_all.
C5  the encoded residuals and the hart stream in every arm (the registered footing and the three others).
"""
import glob
import gzip
import hashlib
import json
import os
import re
import subprocess

HERE = os.path.relpath(os.path.dirname(os.path.abspath(__file__)))
SRC = "tools/ettelem/ettelem.cpp"
BOX_SOURCE_SHA = None  # read from logs/ettelem-binary-check.txt below


def git_show(rev, path):
    return subprocess.run(["git", "show", f"{rev}:{path}"], capture_output=True, check=True).stdout.decode()


def body(text, head):
    """The text of the function whose definition starts with `head`, up to its closing brace at column 0."""
    i = text.find(head)
    if i < 0:
        return None
    j = text.find("\n}\n", i)
    return text[i:j + 3]


def c1():
    print("== C1: the ettelem source the box's binary matches")
    box = open(os.path.join(HERE, "logs", "ettelem-binary-check.txt")).read()
    m = re.search(r"([0-9a-f]{64})\s+tools/ettelem/ettelem\.cpp", box)
    box_src = m.group(1) if m else None
    usage = re.search(r"usage: ettelem[^\n]*", box)
    print("box tree's tools/ettelem/ettelem.cpp sha256:", box_src)
    print("binary's usage line:", usage.group(0) if usage else None)
    revs = subprocess.run(["git", "log", "--format=%h %ad", "--date=format-local:%Y-%m-%d %H:%M", "--", SRC],
                          capture_output=True, check=True).stdout.decode().split("\n")
    texts = {}
    for line in revs:
        if not line.strip():
            continue
        h, when = line.split(" ", 1)
        t = git_show(h, SRC)
        texts[h] = t
        sha = hashlib.sha256(t.encode()).hexdigest()
        u = re.search(r'"(usage: ettelem[^"]*)"((?:\s*"[^"]*")*)', t)
        us = (u.group(1) + "".join(re.findall(r'"([^"]*)"', u.group(2)))).replace("\\n", "").strip() if u else "?"
        print("  %s %s  sha256 %s…%s\n      usage: %s%s" % (
            h, when, sha[:16], "  <- the box tree's source" if sha == box_src else "", us,
            "  <- the binary's usage line" if usage and us == usage.group(0).strip() else ""))
    reviewed = hashlib.sha256(open(SRC, "rb").read()).hexdigest()
    print("reviewed source (the table's build/ettelem/ entry) = HEAD's %s, sha256 %s…" % (SRC, reviewed[:16]))
    box_rev = [h for h, t in texts.items() if hashlib.sha256(t.encode()).hexdigest() == box_src]
    head_rev = [h for h, t in texts.items() if hashlib.sha256(t.encode()).hexdigest() == reviewed]
    if box_rev and head_rev:
        a, b = texts[box_rev[0]], texts[head_rev[0]]
        for name, head in (("config()", "int config(Dm& d)"), ("sample()", "int sample(Dm& d"),
                           ("resetStats()", "  bool resetStats()"), ("get()", "  template <class T> bool get(")):
            ba, bb = body(a, head), body(b, head)
            if name in ("resetStats()", "get()"):
                ba = a[a.find(head):a.find("\n  }\n", a.find(head)) + 5] if head in a else None
                bb = b[b.find(head):b.find("\n  }\n", b.find(head)) + 5] if head in b else None
            print("  %-13s %s at %s and %s: %s" % (name, "byte-identical" if ba is not None and ba == bb else "DIFFERS",
                                                   box_rev[0], head_rev[0], "%d bytes" % len(ba or "")))
        sends_a = sorted(set(re.findall(r"DM_CMD_[A-Z_]+", a)))
        sends_b = sorted(set(re.findall(r"DM_CMD_[A-Z_]+", b)))
        print("  DM_CMD names in %s: %s" % (box_rev[0], ", ".join(sends_a)))
        print("  DM_CMD names in %s: %s" % (head_rev[0], ", ".join(sends_b)))
        print("  subcommands only in %s: %s" % (head_rev[0], "temp [--if-free]" if '"temp"' in b and '"temp"' not in a else "none"))


def passes():
    return sorted(glob.glob(os.path.join(HERE, "passes", "p13*")))


def spans_of(d):
    out = []
    for line in open(os.path.join(d, "marks.jsonl")):
        try:
            r = json.loads(line)
        except ValueError:
            continue
        if "t_start_ms" in r and "t_end_ms" in r:
            k = r.get("kind")
            lab = "heater" if k == "heater" else "burn-in" if k == "burnin" else (
                "anchor_pi" if r.get("item") == "anchor_pi" else "dp_zeros" if r.get("item") == "dp_zeros" else "DRAM item")
            out.append((r["t_start_ms"], r["t_end_ms"], lab))
    return sorted(out)


def c2_c3():
    print("\n== C2 and C3: every telemetry sample of the smoke and the seven passes")
    n = 0
    top = {"board": (-1.0, "", ""), "die": (-1, ""), "pmic": (-1, "")}
    by = {}
    sp_max, latch, since, mhz, regddr = set(), set(), set(), set(), set()
    ddr = [10 ** 9, -1]
    pmic_eq = [0, 0]
    for d in passes():
        name = os.path.basename(d)
        sp_ = spans_of(d)
        pm = {}

        def what(t):
            for a, b, lab in sp_:
                if a - 200 <= t <= b + 200:
                    return lab
            return "between runs"

        for line in gzip.open(os.path.join(d, "telemetry.jsonl.gz"), "rt"):
            try:
                s = json.loads(line)
            except ValueError:
                continue
            n += 1
            since.add(s.get("since_reset_ms"))
            sp = s.get("sp") or {}
            if sp:
                sp_max.add(sp.get("board_max_w"))
                mhz.add(tuple(sp.get("minion_mhz", [])))
            tc = s.get("temp_c") or {}
            if tc:
                latch.add((tc["minshire"][1], tc["minshire"][2]))
                if tc["minshire"][0] > top["die"][0]:
                    top["die"] = (tc["minshire"][0], name)
                if tc.get("pmic", -1) > top["pmic"][0]:
                    top["pmic"] = (tc["pmic"], name)
                pmic_eq[0] += 1
                pmic_eq[1] += int(tc.get("pmic") == tc["minshire"][0])
            dm = s.get("die_mv") or {}
            if "ddr" in dm:
                ddr[0], ddr[1] = min(ddr[0], dm["ddr"]), max(ddr[1], dm["ddr"])
            rm = s.get("reg_mv") or {}
            if "ddr" in rm:
                regddr.add(rm["ddr"])
            if "board_w" in s:
                w, lab = s["board_w"], what(s["t_ms"])
                pm[lab] = max(pm.get(lab, -1.0), w)
                by[lab] = max(by.get(lab, -1.0), w)
                if w > top["board"][0]:
                    top["board"] = (w, name, lab)
        print("  %s  board max by what ran: %s" % (name, ", ".join("%s %.2f W" % (k, v) for k, v in sorted(pm.items()))))
    print("samples:", n)
    print("C3 board power, instantaneous (board_w): max %.2f W, pass %s, during a %s" % top["board"])
    print("C3 board max by what ran, all passes: %s" % ", ".join("%s %.2f W" % (k, v) for k, v in sorted(by.items())))
    print("C3 die mean (temp_c.minshire[0], runitems.py's 78 C stop) max %d C (first at %s)" % top["die"])
    print("C3 temp_c.pmic (runitems.py's 88 C stop) max %d C; equal to temp_c.minshire[0] in %d of %d samples"
          % (top["pmic"][0], pmic_eq[1], pmic_eq[0]))
    print("C3 margins: 75 W - %.2f W = %.2f W; 78 C - %d C = %d C; 88 C - %d C = %d C"
          % (top["board"][0], 75 - top["board"][0], top["die"][0], 78 - top["die"][0], top["pmic"][0], 88 - top["pmic"][0]))
    print("C3 sp.board_max_w values seen (the SP's since-reset maximum):", sorted(sp_max))
    print("C3 PVT latches (temp_c.minshire low, high) seen:", sorted(latch))
    print("C3 since_reset_ms values seen:", sorted(since))
    print("C3 minion clock (sp.minion_mhz) triples seen:", sorted(mhz))
    print("C2 die_mv.ddr (GET_ASIC_VOLTAGE, PVT memory-shire monitor; the reducer's DDR die rail): %d to %d mV" % tuple(ddr))
    print("C2 reg_mv.ddr (GET_MODULE_VOLTAGE, the PMIC's DDR voltage register): values seen", sorted(regddr), "mV")


def iv(c):
    return "%+.3f [%+.3f, %+.3f]" % (c["mean"], c["lo"], c["hi"])


def c4_c5():
    J = json.load(open(os.path.join(HERE, "e132.json")))
    B = J["headline"]["contrasts"]["board"]
    print("\n== C4: what R_all is made of (e132.json headline.contrasts.board, the registered primary arm)")
    for k in ("R_all", "D_all", "H"):
        print("  %-6s %s  (%s)" % (k, iv(B[k]), B[k]["what"]))
    rungs = ["R_%d" % b for b in range(8)] + ["R_hi"]
    print("  rungs: " + ", ".join("%s %+.3f" % (k, B[k]["mean"]) for k in rungs))
    tot = sum(B[k]["mean"] for k in rungs)
    three = sum(B[k]["mean"] for k in ("R_3", "R_4", "R_hi"))
    print("  R_0 + ... + R_7 + R_hi = %+.4f (R_all %+.4f)" % (tot, B["R_all"]["mean"]))
    print("  the three named paths R_3 + R_4 + R_hi = %+.3f W; the other six rungs = %+.3f W" % (three, tot - three))
    cnt = json.load(open(os.path.join(HERE, "gen", "counts.json")))
    k = {n: cnt[n]["k_stream"] for n in ("dm_u4", "ab_7", "ab_x70", "ab_rnd")}
    share = (k["ab_rnd"] - k["dm_u4"]) / (k["ab_x70"] - k["ab_7"])
    print("  k_stream (gen/counts.json): %s; the hart stream's share of D_all = %.2f/%.0f x H = %.4f x %.4f = %.4f W"
          % (k, k["ab_rnd"] - k["dm_u4"], k["ab_x70"] - k["ab_7"], share, B["H"]["mean"], share * B["H"]["mean"]))
    print("  R_all + that share = %+.4f W = D_all %+.4f" % (B["R_all"]["mean"] + share * B["H"]["mean"], B["D_all"]["mean"]))
    print("  R_3 + R_4 + R_hi + H = %+.3f W (close to R_all by coincidence: H is not in R_all, and the other six rungs are)"
          % (three + B["H"]["mean"]))
    print("\n== C5: the encoded residuals and the hart stream in every arm (headline.contrasts.board)")
    for f, lab in (("e132.json", "registered primary: dips removed, auto 0.0228 W/C"),
                   ("e132-leak0.2936.json", "0.2936 W/C, dips removed"), ("e132-leak0.3803.json", "0.3803 W/C, dips removed"),
                   ("e132-unfiltered.json", "unfiltered, its own auto")):
        A = json.load(open(os.path.join(HERE, f)))["headline"]["contrasts"]["board"]
        cells = []
        for n in ("E448", "E56", "E192", "H", "D_all", "R_all"):
            c = A[n]
            cells.append("%s %s%s" % (n, iv(c), "" if c["lo"] > 0 else " (crosses 0)"))
        print("  %-22s %s\n      %s" % (f, lab, "; ".join(cells)))


if __name__ == "__main__":
    c1()
    c2_c3()
    c4_c5()
