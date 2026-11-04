#!/usr/bin/env python3
"""E156, corrections after verification: POST HOC, labelled. Written Tue 3 Nov 2026 (week 45), after the verifier's report of about
16:18 PST, at the desk: no card, no device command, nothing re-run on a box. It moves no registered verdict, no frozen number and no
prediction. Standard library only; committed inputs only (this data dir, E139's data dir, E156's registration).

    python3 docs/reports/data/2026-11-03-e156-memory-images-card1/posthoc/corrections_e156.py \
        --json docs/reports/data/2026-11-03-e156-memory-images-card1/posthoc/corrections.json \
        > docs/reports/data/2026-11-03-e156-memory-images-card1/posthoc/corrections.txt

C1  every committed verdict JSON's `dirs` field: repo-relative, and no Mac home path anywhere in this data dir
C2  the ties, card 1 minus aifoundry3, with Welch intervals and two-sided p over each card's headline passes (one session per card)
C3  the width readings beyond the registered primary: every reading's d on E32 and E192 at every arm on card 1; reading C (the 64- plus
    128-bit toggles) on E192 on aifoundry3's E139 passes; and what reading C would mean for a random line
C4  the critic's rule read literally: each pair against E132's frozen +0.185 W per image (predictions-e156.json > E132_frozen_W)
C7  the record: the registration's projected passes against the queue's, and the session log's et-who lines
O1  where the board meter's in-window dips fall, against a uniform placement (why the dips-kept arm moves)
"""
import argparse
import glob
import json
import math
import os

D = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
REPO = os.path.abspath(os.path.join(D, "..", "..", "..", ".."))
E139D = os.path.abspath(os.path.join(D, "..", "2026-11-02-e139-memory-split-more-passes"))
PRED = os.path.join(REPO, "tools", "claims-v3", "e156", "predictions-e156.json")
REG = os.path.join(REPO, "tools", "claims-v3", "e156", "README.md")
T975 = {1: 12.706, 2: 4.303, 3: 3.182, 4: 2.776, 5: 2.571, 6: 2.447, 7: 2.365, 8: 2.306, 9: 2.262, 10: 2.228}   # posthoc_e156.py's
HOME = "/" + "Users" + "/"          # spelled in two parts so a repo-wide scan for Mac home paths does not match this file
TWINS = ("el_64", "c3_64", "c3_128", "e2_64", "el_32")   # the encoded-quiet twin (y) of each pair (x, y): E56, E448, E192, E7, E32
RUNS_A_PASS = 18                                        # anchor_pi first and last + the 16 memory items (predictions-e156.json > plan)


def load(p):
    with open(p) as fh:
        return json.load(fh)


def rel(p):
    return os.path.relpath(p, REPO)


# ---- Student t, standard library only (regularized incomplete beta by Lentz's continued fraction) ----
def _betacf(a, b, x):
    tiny, eps = 1e-300, 1e-15
    qab, qap, qam = a + b, a + 1.0, a - 1.0
    c, d = 1.0, 1.0 - qab * x / qap
    d = 1.0 / (d if abs(d) > tiny else tiny)
    h = d
    for m in range(1, 400):
        m2 = 2 * m
        aa = m * (b - m) * x / ((qam + m2) * (a + m2))
        d = 1.0 + aa * d
        d = 1.0 / (d if abs(d) > tiny else tiny)
        c = 1.0 + aa / c
        c = c if abs(c) > tiny else tiny
        h *= d * c
        aa = -(a + m) * (qab + m) * x / ((a + m2) * (qap + m2))
        d = 1.0 + aa * d
        d = 1.0 / (d if abs(d) > tiny else tiny)
        c = 1.0 + aa / c
        c = c if abs(c) > tiny else tiny
        dl = d * c
        h *= dl
        if abs(dl - 1.0) < eps:
            break
    return h


def _betai(a, b, x):
    if x <= 0.0:
        return 0.0
    if x >= 1.0:
        return 1.0
    bt = math.exp(math.lgamma(a + b) - math.lgamma(a) - math.lgamma(b) + a * math.log(x) + b * math.log(1.0 - x))
    if x < (a + 1.0) / (a + b + 2.0):
        return bt * _betacf(a, b, x) / a
    return 1.0 - bt * _betacf(b, a, 1.0 - x) / b


def p_two_sided(t, df):
    return _betai(df / 2.0, 0.5, df / (df + t * t))


def t975(df):
    lo, hi = 0.0, 200.0
    for _ in range(200):
        mid = 0.5 * (lo + hi)
        if p_two_sided(mid, df) > 0.05:
            lo = mid
        else:
            hi = mid
    return 0.5 * (lo + hi)


def mean_sd(v):
    n = len(v)
    m = sum(v) / n
    s = math.sqrt(sum((x - m) ** 2 for x in v) / (n - 1))
    return m, s, n


def ci1(v):
    m, s, n = mean_sd(v)
    h = T975[n - 1] * s / math.sqrt(n)
    return {"mean": m, "lo": m - h, "hi": m + h, "n": n}


def welch(a, b):
    m1, s1, n1 = mean_sd(a)
    m2, s2, n2 = mean_sd(b)
    v1, v2 = s1 * s1 / n1, s2 * s2 / n2
    se = math.sqrt(v1 + v2)
    df = (v1 + v2) ** 2 / (v1 * v1 / (n1 - 1) + v2 * v2 / (n2 - 1))
    t = (m1 - m2) / se
    q = t975(df)
    return {"card1": m1, "aifoundry3": m2, "diff": m1 - m2, "lo": m1 - m2 - q * se, "hi": m1 - m2 + q * se, "t": t, "df": df,
            "p": p_two_sided(abs(t), df), "ratio": m1 / m2 if m2 else None, "n": [n1, n2]}


def board(res, name):
    return [res["per_pass"][str(p)]["contrasts"]["board"][name] for p in res["passes_headline"]]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", default=None)
    a = ap.parse_args()
    out = {"label": "POST HOC (corrections after verification, Tue 3 Nov 2026); no registered verdict, frozen number or prediction moves"}
    e156 = load(os.path.join(D, "e156.json"))
    e139 = load(os.path.join(E139D, "e139.json"))
    pred = load(PRED)

    # C1
    print("C1. the `dirs` field of each verdict JSON, and Mac home paths in this data dir")
    c1 = {}
    for f in sorted(glob.glob(os.path.join(D, "*.json"))):
        j = load(f)
        if "dirs" in j:
            c1[os.path.basename(f)] = {"n": len(j["dirs"]), "first": j["dirs"][0], "last": j["dirs"][-1]}
            print("   %-22s %2d dirs, %s .. %s" % (os.path.basename(f), len(j["dirs"]), j["dirs"][0], j["dirs"][-1]))
    hits = 0
    for base, _dirs, files in os.walk(D):
        for fn in files:
            if fn.endswith((".json", ".md", ".txt", ".csv", ".py", ".log", ".out", ".jsonl", ".sha256", ".time")):
                try:
                    with open(os.path.join(base, fn), errors="replace") as fh:
                        hits += fh.read().count(HOME)
                except OSError:
                    pass
    print("   text files in this data dir holding a Mac home path: %d occurrences" % hits)
    out["C1"] = {"dirs": c1, "home_path_occurrences": hits}

    # C2
    print("\nC2. the ties, card 1 (E156, %d headline passes) minus aifoundry3 (E139, %d), board W; Welch 95%% interval, two-sided p" % (
        len(e156["passes_headline"]), len(e139["passes_headline"])))
    c2 = {}
    ties = e156["verdicts"]["ties_vs_E139"]
    for t in ("S64", "S128", "V16", "V64", "V128", "U4z", "Hp", "RH64", "RH128"):
        x, y = board(e156, t), board(e139, t)
        w = welch(x, y)
        assert abs(w["card1"] - ties[t]["mean_W"]) < 1e-9 and abs(w["aifoundry3"] - ties[t]["E139_W"]) < 1e-9, t
        c2[t] = w
        print("   %-6s card 1 %+.3f  aifoundry3 %+.3f  difference %+.3f [%+.3f, %+.3f]  ratio %.3f  t %.2f  df %.1f  p %.3f  %s" % (
            t, w["card1"], w["aifoundry3"], w["diff"], w["lo"], w["hi"], w["ratio"], w["t"], w["df"], w["p"],
            "resolved" if w["lo"] > 0 or w["hi"] < 0 else "NOT resolved (the interval holds 0)"))
    out["C2"] = c2

    # C3
    print("\nC3. the width readings beyond the registered primary (d_X = pair - k_X x the mean of E56 and E448; consistent if its 95% interval holds 0)")
    c3 = {"card1": {}, "aifoundry3_E139": {}}
    arms = (("primary (dips removed, leak auto)", "e156.json"), ("leak 0.2936", "e156-leak0.2936.json"),
            ("leak 0.3803", "e156-leak0.3803.json"), ("leak 0.3134", "e156-leak0.3134.json"), ("dips kept", "e156-unfiltered.json"))
    for arm, f in arms:
        n2 = load(os.path.join(D, f))["verdicts"]["N2_width"]
        row = {"verdict": n2["verdict"], "consistent_on_both": n2["consistent_readings"]}
        print("   card 1, %-34s N2 %-18s" % (arm, n2["verdict"]))
        for pair in ("E32", "E192"):
            for X in ("A", "B", "C", "E", "F"):
                r = n2["pairs"][pair][X]
                row["%s_%s" % (pair, X)] = {"k": r["k"], "d": r["d_W"]["mean"], "lo": r["d_W"]["lo"], "hi": r["d_W"]["hi"],
                                            "consistent": r["consistent"]}
            print("      %-5s " % pair + "  ".join("%s %+.3f [%+.3f, %+.3f]%s" % (
                X, row["%s_%s" % (pair, X)]["d"], row["%s_%s" % (pair, X)]["lo"], row["%s_%s" % (pair, X)]["hi"],
                "" if row["%s_%s" % (pair, X)]["consistent"] else " x") for X in ("A", "B", "C", "E", "F")))
        c3["card1"][arm] = row
    kA = e156["verdicts"]["N2_width"]["pairs"]["E192"]["A"]["k"]
    kC = e156["verdicts"]["N2_width"]["pairs"]["E192"]["C"]["k"]
    kF = e156["verdicts"]["N2_width"]["pairs"]["E192"]["F"]["k"]
    print("   aifoundry3, E139's headline passes (no E32 there: only E192 tests C), k_A %.4f, k_C %.4f, k_F %.4f" % (kA, kC, kF))
    for arm, f in (("primary (dips removed, leak auto)", "e139.json"), ("leak 0.2936", "e139-leak0.2936.json"),
                   ("leak 0.3803", "e139-leak0.3803.json"), ("dips kept", "e139-unfiltered.json")):
        r = load(os.path.join(E139D, f))
        e56, e448, e192 = board(r, "E56"), board(r, "E448"), board(r, "E192")
        row = {}
        for X, k in (("A", kA), ("C", kC), ("F", kF)):
            c = ci1([z - k * (u + v) / 2.0 for u, v, z in zip(e56, e448, e192)])
            c["consistent"] = c["lo"] <= 0.0 <= c["hi"]
            row[X] = c
        c3["aifoundry3_E139"][arm] = row
        print("      %-34s E192 " % arm + "  ".join("%s %+.3f [%+.3f, %+.3f]%s" % (
            X, row[X]["mean"], row[X]["lo"], row[X]["hi"], "" if row[X]["consistent"] else " x") for X in ("A", "C", "F")))
    # a random line: each byte sent through read DBI as 9 pins (8 DQ + DMI; inverted when it has more than four ones, dm_enc.ENC)
    pop = [bin(i).count("1") for i in range(512)]
    enc = [b if pop[b] <= 4 else ((~b & 0xFF) | 0x100) for b in range(256)]
    pe = sum(pop[enc[x] ^ enc[y]] for x in range(256) for y in range(256)) / 65536.0
    edges = {"e32": 15 * 4, "e64": 7 * 8, "e128": 3 * 16}           # byte edges between consecutive W-bit pieces of a 64 B line
    cnt = {k: v * pe for k, v in edges.items()}
    lps = e156["headline"]["lines_per_s"]
    pA, pC = pred["prices"]["A"]["pJ"], pred["prices"]["C"]["pJ"]
    tA = pA * 1e-12 * cnt["e64"] * lps
    tC = pC * 1e-12 * (cnt["e64"] + cnt["e128"]) * lps
    c3["random_line"] = {"pins_differing_per_byte_edge": pe, "byte_edges": edges, "counts": cnt, "lines_per_s": lps,
                         "term_A_W": tA, "term_C_W": tC, "C_minus_A_W": tC - tA, "C_over_A": tC / tA}
    print("   a random 64 B line: %.4f of a byte's 9 encoded pins differ across a byte edge; e32 %.1f, e64 %.1f, e128 %.1f a line"
          % (pe, cnt["e32"], cnt["e64"], cnt["e128"]))
    print("   at this session's %.5g lines/s: reading A's term %.4f W; reading C's (price %.4f pJ on e64 + e128) %.4f W: +%.4f W, x%.3f"
          % (lps, tA, pC, tC, tC - tA, tC / tA))
    out["C3"] = c3

    # C4
    lit = pred["E132_frozen_W"]
    print("\nC4. the critic's rule read literally: each pair against E132's frozen %+.3f W per image (predictions-e156.json > E132_frozen_W), line 0.05 W" % lit)
    c4 = {}
    for pair, src in (("E7", "N1_new_images"), ("E32", "N1_new_images"), ("E56", "C1_card_transfer"), ("E448", "C1_card_transfer")):
        r = e156["verdicts"][src]["pairs"][pair]
        err = r["mean_W"] - lit
        c4[pair] = {"measured_W": r["mean_W"], "error_vs_literal_W": err, "literal_verdict": "PASS" if abs(err) <= 0.05 else "FAIL",
                    "registered_prediction_W": r["predicted_W"], "registered_error_W": r["error_W"], "registered_verdict": r["verdict"]}
        print("   %-5s measured %+.3f  literal error %+.3f (%s)   registered price x count %+.3f, error %+.3f (%s)" % (
            pair, r["mean_W"], err, c4[pair]["literal_verdict"], r["predicted_W"], r["error_W"], r["verdict"]))
    out["C4"] = c4

    # C7
    print("\nC7. the record")
    reg = open(REG).read().splitlines()
    proj = [ln.strip() for ln in reg if "Expected: about" in ln]
    log = open(os.path.join(D, "logs", "session.log")).read().splitlines()
    done = [ln for ln in log if "e156: done" in ln]
    print("   the registration (tools/claims-v3/e156/README.md): %s" % (proj[0] if proj else "?"))
    print("   the session log: %s" % (done[0] if done else "?"))
    print("   e156.json: warm-up pass %s, %d headline passes (%s-%s), %d set aside" % (
        e156["warmup_pass"], len(e156["passes_headline"]), e156["passes_headline"][0], e156["passes_headline"][-1], len(e156["passes_set_aside"])))
    who = []
    for i, ln in enumerate(log):
        if "No process holds" in ln:
            stamp = log[i - 1][:23] if i else ""
            who.append({"line": i + 1, "after": stamp, "text": ln.strip()})
            print("   logs/session.log line %d, after the line stamped %s: %s" % (i + 1, stamp, ln.strip()))
    out["C7"] = {"projection": proj[0] if proj else None, "queue": done[0] if done else None,
                 "headline_passes": len(e156["passes_headline"]), "et_who": who}

    # O1
    dj = load(os.path.join(D, "dips.json"))
    tw = other = 0
    on_runs = {}
    for p in e156["passes_headline"]:
        for dip in dj["passes"]["p%d" % p]["list"]:
            r = dip.get("run")
            if r and r.get("in_power_window"):
                on_runs[r["item"]] = on_runs.get(r["item"], 0) + 1
                if r["item"] in TWINS:
                    tw += 1
                else:
                    other += 1
    n = tw + other
    q = len(TWINS) / float(RUNS_A_PASS)
    tail = sum(math.comb(n, k) * q ** k * (1 - q) ** (n - k) for k in range(tw, n + 1))
    print("\nO1. in-window dips over the %d headline passes: %d, %d of them on the encoded-quiet twins (%s), which are %d of the %d runs a pass;"
          " P(at least %d of %d | uniform) = %.4f (one-sided binomial)" % (len(e156["passes_headline"]), n, tw, ", ".join(TWINS), len(TWINS),
                                                                             RUNS_A_PASS, tw, n, tail))
    print("   by item: " + ", ".join("%s %d" % (k, v) for k, v in sorted(on_runs.items(), key=lambda kv: (-kv[1], kv[0]))))
    out["O1"] = {"in_window_dips": n, "on_twins": tw, "twin_share_of_runs": q, "p_at_least": tail, "by_item": on_runs}

    if a.json:
        with open(a.json, "w") as fh:
            json.dump(out, fh, indent=1, sort_keys=True)
            fh.write("\n")


if __name__ == "__main__":
    main()
