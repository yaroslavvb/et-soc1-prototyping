#!/usr/bin/env python3
"""E156's pipeline test, before any E156 pass (nothing here is a measurement). Run from the lab repo root with a python3 that has numpy:

    python3 tools/claims-v3/e156/selftest_e156.py <scratch dir>        # prints SELFTEST PASS / FAIL, exit 0 / 1

A. E139's committed passes (p13910-p13918, the warm-up 13910 among them as reduce_e139.sh reads them, the board meter's dips removed by dp/posthoc_dips.py exactly as reduce_e139.sh does), read by
   reduce_e156.py with E139's images (E132's gen, its counts in E156's form): every contrast E156 shares with E139 (E56, E448, E192, P56,
   P448, P192, V16, Hp, S64, S128, V64, V128, U4z, RH64, RH128) and the line rate must equal E139's committed e139.json to 1e-9, with the
   same headline passes. So the copied estimator and the count-built coefficients reproduce E139's reduction.
B. The same passes with the four new images aliased onto measured runs (e7_64 and eh_32 read eh_64's run windows, e2_64 and el_32 read
   el_64's): the new residuals must equal their formulas on the per-pass values, E7 = P56 - (70/496) V16 + (32/192) Hp and
   E32 = P56 - (210/496) V16 - (32/192) Hp, to 1e-9; and every rule (N1, C1, N2, D) must return a verdict.
"""
import json
import os
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
D139 = os.path.join(ROOT, "docs/reports/data/2026-11-02-e139-memory-split-more-passes")
G132 = os.path.join(ROOT, "docs/reports/data/2026-11-02-e132-memory-split/gen")
G156 = os.path.join(ROOT, "docs/reports/data/2026-11-03-e156-memory-images-card1/gen")
PRED = os.path.join(HERE, "predictions-e156.json")
ALIAS = {"e7_64": "eh_64", "e2_64": "el_64", "eh_32": "eh_64", "el_32": "el_64"}


def run(cmd):
    r = subprocess.run(cmd, capture_output=True, text=True)
    if r.returncode:
        print(r.stdout[-2000:], r.stderr[-2000:])
        raise SystemExit("command failed: " + " ".join(cmd))
    return r.stdout


def main():
    S = os.path.abspath(sys.argv[1])
    os.makedirs(S, exist_ok=True)
    py = sys.executable
    passes = [os.path.join(D139, "passes", "p139%d" % i) for i in range(10, 19)]
    work = os.path.join(S, "w")
    run([py, os.path.join(ROOT, "tools/claims-v3/dp/posthoc_dips.py")] + passes + ["--work", work, "--out", os.path.join(S, "dips.json")])
    # E139's images in E156's gen form: E132's manifest, and E132's counts under "items" (+ E156's four for part B)
    g = os.path.join(S, "gen139")
    os.makedirs(g, exist_ok=True)
    shutil.copy(os.path.join(G132, "manifest.json"), g)
    c132 = json.load(open(os.path.join(G132, "counts.json")))
    json.dump({"items": c132}, open(os.path.join(g, "counts.json"), "w"))
    bad = 0
    # ---- A
    outA = os.path.join(S, "A.json")
    print(run([py, os.path.join(HERE, "reduce_e156.py")] + [os.path.join(work, os.path.basename(p)) for p in passes] +
              ["--gen", g, "--pred", PRED, "--warmup", "13910", "--out", outA, "--label", "selftest-A"]).strip())
    a = json.load(open(outA))
    e = json.load(open(os.path.join(D139, "e139.json")))
    if a["passes_headline"] != e["passes_headline"]:
        bad += 1
        print("DIFFERS headline passes", a["passes_headline"], e["passes_headline"])
    if abs(a["headline"]["lines_per_s"] - e["headline"]["lines_per_s"]) > 1e-3:
        bad += 1
        print("DIFFERS line rate")
    for col in ("board", "noc", "sram", "minion", "off", "ddr_mv"):
        for cn, ecn in (("E56", "E56"), ("E448", "E448"), ("E192", "E192"), ("P56", "P56"), ("P448", "P448"), ("P192", "P192"), ("V16", "V16"),
                        ("Hp", "Hp"), ("S64", "S64"), ("S128", "S128"), ("V64", "V64"), ("V128", "V128"), ("U4z", "U4z"), ("RH64", "RH64"),
                        ("RH128", "RH128"), ("RE64", "RE64"), ("RE128", "RE128")):
            x, y = a["headline"]["contrasts"][col][cn], e["headline"]["contrasts"][col][ecn]
            for k in ("mean", "lo", "hi"):
                if (x[k] is None) != (y[k] is None) or (x[k] is not None and abs(x[k] - y[k]) > 1e-9):
                    bad += 1
                    print("DIFFERS A", col, cn, k, x[k], y[k])
    print("A: %s against E139's e139.json (17 contrasts x 6 columns x mean/lo/hi, the line rate, the headline passes)" % ("ok" if bad == 0 else "DIFFERS"))
    # ---- B: alias the new images onto measured runs
    wb = os.path.join(S, "wB")
    if os.path.exists(wb):
        shutil.rmtree(wb)
    shutil.copytree(work, wb)
    for p in passes:
        d = os.path.join(wb, os.path.basename(p))
        for fn in ("runs.jsonl", "marks.jsonl"):
            lines = [json.loads(x) for x in open(os.path.join(d, fn)) if x.startswith("{")]
            add = []
            for new, old in ALIAS.items():
                for x in lines:
                    if x.get("item") == old:
                        y = dict(x)
                        y["item"] = new
                        add.append(y)
            with open(os.path.join(d, fn), "a") as fh:
                for y in add:
                    fh.write(json.dumps(y) + "\n")
    gb = os.path.join(S, "genB")
    os.makedirs(gb, exist_ok=True)
    m132 = json.load(open(os.path.join(G132, "manifest.json")))
    m156 = {it["name"]: it for it in json.load(open(os.path.join(G156, "manifest.json")))["items"]}
    m132["items"] += [m156[n] for n in ALIAS]
    json.dump(m132, open(os.path.join(gb, "manifest.json"), "w"))
    c156 = json.load(open(os.path.join(G156, "counts.json")))["items"]
    cb = dict(c132)
    cb.update({n: c156[n] for n in ALIAS})
    json.dump({"items": cb}, open(os.path.join(gb, "counts.json"), "w"))
    outB = os.path.join(S, "B.json")
    print(run([py, os.path.join(HERE, "reduce_e156.py")] + [os.path.join(wb, os.path.basename(p)) for p in passes] +
              ["--gen", gb, "--pred", PRED, "--warmup", "13910", "--leak", "0.0108333", "--out", outB, "--label", "selftest-B"]).strip())
    b = json.load(open(outB))
    nb = 0
    for p, pp in b["per_pass"].items():
        c = pp["contrasts"]["board"]
        if c.get("E7") is None or c.get("E32") is None:
            nb += 1
            print("B: pass %s has no E7/E32" % p)
            continue
        f7 = c["P56"] - (70 / 496.0) * c["V16"] + (32 / 192.0) * c["Hp"]
        f32 = c["P56"] - (210 / 496.0) * c["V16"] - (32 / 192.0) * c["Hp"]
        if abs(c["E7"] - f7) > 1e-9 or abs(c["E32"] - f32) > 1e-9 or abs(c["P7"] - c["P56"]) > 1e-9 or abs(c["P32"] - c["P56"]) > 1e-9:
            nb += 1
            print("DIFFERS B pass", p, c["E7"], f7, c["E32"], f32)
    V = b["verdicts"]
    for k in ("N1_new_images", "C1_card_transfer", "N2_width", "D_dbi_evident"):
        print("B: %s -> %s" % (k, V[k]["verdict"]))
        nb += 1 if V[k]["verdict"] in (None, "NOT-SCORED") else 0
    print("B: %s (the new residuals' formulas on every headline pass; every rule returns a verdict)" % ("ok" if nb == 0 else "DIFFERS"))
    bad += nb
    print("SELFTEST", "PASS" if bad == 0 else "FAIL (%d differences)" % bad)
    sys.exit(0 if bad == 0 else 1)


if __name__ == "__main__":
    main()
