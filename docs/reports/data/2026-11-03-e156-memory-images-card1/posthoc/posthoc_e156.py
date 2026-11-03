#!/usr/bin/env python3
"""E156 POST HOC, labelled (written after the registered reduction was read; it moves no registered verdict). Standard library only.

    python3 docs/reports/data/2026-11-03-e156-memory-images-card1/posthoc/posthoc_e156.py > posthoc/posthoc.txt

1. The error of predicting each pair's encoded residual before (no encoded term: 0) and after (E139's frozen price, reading A), from e156.json.
2. One price per encoded 64-bit toggle on this card, fitted per pass on E56, E448 and E7 together, with a t interval over the headline passes;
   and E139's and E156's passes side by side.
3. The session's peaks from the raw telemetry (board W, the hottest minion-shire field, the minion-shire mean, the largest sample gap) and
   since_reset_ms in every sample.
"""
import gzip
import glob
import json
import math
import os

D = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
E139 = os.path.join(D, "..", "2026-11-02-e139-memory-split-more-passes", "e139.json")
T975 = {1: 12.706, 2: 4.303, 3: 3.182, 4: 2.776, 5: 2.571, 6: 2.447, 7: 2.365, 8: 2.306, 9: 2.262, 10: 2.228}


def ci(v):
    n = len(v)
    m = sum(v) / n
    s = math.sqrt(sum((x - m) ** 2 for x in v) / (n - 1))
    h = T975[n - 1] * s / math.sqrt(n)
    return m, m - h, m + h, n


d = json.load(open(os.path.join(D, "e156.json")))
pred = json.load(open(os.path.join(D, "..", "..", "..", "..", "tools", "claims-v3", "e156", "predictions-e156.json")))
V = d["verdicts"]
lr = d["headline"]["lines_per_s"]
B = d["headline"]["contrasts"]["board"]
print("1. before (no encoded term) and after (reading A, 0.4630 pJ x count x %.6g lines/s), W" % lr)
rows = {}
for pn in ("E56", "E448", "E192", "E7", "E32"):
    m = B[pn]["mean"]
    pa = pred["prices"]["A"]["pJ"] * 1e-12 * pred["pairs"][pn]["counts"]["e64"] * lr
    rows[pn] = (m, -m, m - pa)
    print("   %-5s measured %+.3f [%+.3f, %+.3f]  error before %+.3f  after %+.3f  (prediction %+.4f)" % (pn, m, B[pn]["lo"], B[pn]["hi"], -m, m - pa, pa))
rms = lambda xs: math.sqrt(sum(x * x for x in xs) / len(xs))
for name, sel in (("the two new pairs (E7, E32)", ("E7", "E32")), ("the four scored (E56, E448, E7, E32)", ("E56", "E448", "E7", "E32")),
                  ("all five (E192 too)", ("E56", "E448", "E192", "E7", "E32"))):
    print("   rms over %s: before %.4f W, after %.4f W" % (name, rms([rows[p][1] for p in sel]), rms([rows[p][2] for p in sel])))
for rd in ("B", "C", "E", "F"):
    errs = []
    for pn in ("E56", "E448", "E192", "E7", "E32"):
        p = pred["prices"][rd]["pJ"] * 1e-12 * pred["pairs"][pn]["counts"][pred["prices"][rd]["count"]] * lr
        errs.append(B[pn]["mean"] - p)
    print("   reading %s instead (frozen at E139's price): errors E56..E32 %s, rms over all five %.4f W" % (rd, " ".join("%+.3f" % e for e in errs), rms(errs)))

print("\n2. one price per encoded 64-bit toggle, fitted per pass on E56 + E448 + E7 (1,064 toggles a line in all), pJ")
out = {}
for tag, js in (("E156 (card 1)", d), ("E139 (aifoundry3), E56 + E448 only", json.load(open(E139)))):
    vals = []
    for p in js["passes_headline"]:
        pp = js["per_pass"][str(p)]
        c = pp["contrasts"]["board"]
        names = [x for x in ("E56", "E448", "E7") if c.get(x) is not None]
        cnt = {"E56": 392, "E448": 392, "E7": 280}
        vals.append(sum(c[x] for x in names) / (sum(cnt[x] for x in names) * pp["lines_per_s"]) * 1e12)
    m, lo, hi, n = ci(vals)
    out[tag] = (m, lo, hi, n)
    print("   %-36s %.4f [%.4f, %.4f] pJ, n = %d passes" % (tag, m, lo, hi, n))
r = out["E156 (card 1)"][0] / out["E139 (aifoundry3), E56 + E448 only"][0]
print("   card 1 over aifoundry3: %.3f" % r)

print("\n3. the session's peaks (raw telemetry, every pass, the smoke and the stop test)")
bw, hs, mean_c, gap, nres, ns = 0.0, 0.0, 0.0, 0.0, 0, 0
for f in sorted(glob.glob(os.path.join(D, "passes", "p156*", "telemetry.jsonl.gz"))):
    prev = None
    for line in gzip.open(f, "rt"):
        if not line.startswith("{"):
            continue
        s = json.loads(line)
        ns += 1
        bw = max(bw, s["board_w"])
        hs = max(hs, max(s["temp_c"]["minshire"]))
        mean_c = max(mean_c, s["temp_c"]["minshire"][0])
        if s.get("since_reset_ms", -1) != -1:
            nres += 1
        if prev is not None:
            gap = max(gap, s["t_ms"] - prev)
        prev = s["t_ms"]
print("   %d samples; board max %.2f W (stop 66); hottest minion-shire field max %.0f C (stop 72); minion-shire mean max %.0f C (runitems cap 70); "
      "largest gap between samples %.0f ms; samples with since_reset_ms other than -1: %d" % (ns, bw, hs, mean_c, gap, nres))
