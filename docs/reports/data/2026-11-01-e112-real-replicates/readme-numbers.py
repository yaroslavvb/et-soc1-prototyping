#!/usr/bin/env python3
"""E112: every derived number the README quotes that results.md does not print, from the committed files of this data
directory and the earlier experiments' committed reductions (standard library only).

    python3 docs/reports/data/2026-11-01-e112-real-replicates/readme-numbers.py > .../readme-numbers.txt

Sections: A1 (a)'s ratios to random over three baselines (D over the type's zeros, S over idle, p80 the whole board), paired
per pass, and their three-tile means beside E91's three kept passes and E86's four; A2 the pass times; B1 (b)'s per-tile
ratio agreement with E95 on the registered two kept passes and in the post-hoc three-pass view; B2 (b)'s card scale; B3 the
gate that set pass 11252 aside at every arm; T the card time.
"""
import json
import math
import os
import statistics

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
T95 = {1: 12.706, 2: 4.303, 3: 3.182, 4: 2.776, 5: 2.571}
REF = {"fp32": "fp32.randn", "fp16": "fp16.randn", "int8": "int8.full"}
MAT = ("l0_mlp_up", "l6_mlp_down", "l6_attn_qk")


def load(*p):
    return json.load(open(os.path.join(*p)))


def mc(v):
    v = [x for x in v if x is not None]
    m = statistics.fmean(v)
    if len(v) < 2:
        return m, None, len(v)
    return m, T95[len(v) - 1] * statistics.stdev(v) / math.sqrt(len(v)), len(v)


def pp(res, p, n, k):
    e = res["per_pass"].get(str(p), {}).get(n)
    return None if e is None else e.get(k)


def ratio_series(res, n, k):
    ty = n.split(".")[0]
    out = []
    for p in res["passes"]:
        a, b = pp(res, p, n, k), pp(res, p, REF[ty], k)
        out.append(a / b if a is not None and b else None)
    return out


def fmt(m):
    return f"{m[0]:.4f} ± {m[1]:.4f} (n {m[2]})" if m[1] is not None else f"{m[0]:.4f} (n {m[2]})"


def main():
    A = load(HERE, "a-e91-rerun", "e91.json")
    E91 = load(ROOT, "docs/reports/data/2026-10-31-e91-real-tensors-aifoundry1/e91.json")
    E86 = load(ROOT, "docs/reports/data/2026-10-31-e86-real-tensors-energy/e86.json")
    print("== A1: (a)'s ratios to random, paired per pass (D over the type's zeros, S over idle, p80 the whole board)")
    for k in ("D", "S", "p80"):
        print(f"-- {k}")
        for ty in ("fp32", "fp16", "int8"):
            for m in MAT:
                n = f"{ty}.real_{m}"
                print(f"  {n:24s} E112a {fmt(mc(ratio_series(A, n, k)))}")
    print("-- three-tile means (per pass the mean over the three tiles, then over passes)")
    for k in ("D", "S", "p80"):
        for ty in ("fp32", "fp16", "int8"):
            row = []
            for lab, res in (("E112a", A), ("E91 (3 kept)", E91), ("E86 aifoundry3", E86)):
                per = []
                for p in res["passes"]:
                    rs = []
                    for m in MAT:
                        n = f"{ty}.real_{m}"
                        a, b = pp(res, p, n, k), pp(res, p, REF[ty], k)
                        rs.append(a / b if a is not None and b else None)
                    per.append(statistics.fmean(rs) if None not in rs else None)
                row.append(f"{lab} {fmt(mc(per))}")
            print(f"  {k:3s} {ty}: " + "; ".join(row))
    print("-- three-tile means of D / random at each leakage arm of (a) (the arms' own reductions)")
    for arm in ("leak0.1994", "leak0.545", "leak0.3803", "leak0"):
        R = load(HERE, "a-e91-rerun", f"e91-{arm}.json")
        row = []
        for ty in ("fp32", "fp16", "int8"):
            per = []
            for p in R["passes"]:
                rs = []
                for m in MAT:
                    a, b = pp(R, p, f"{ty}.real_{m}", "D"), pp(R, p, REF[ty], "D")
                    rs.append(a / b if a is not None and b else None)
                per.append(statistics.fmean(rs) if None not in rs else None)
            row.append(f"{ty} {fmt(mc(per))}")
        print(f"  {arm}: " + "; ".join(row))
    print("-- idle level (W): E112a", round(A["idle_level"]["mean"], 3), "| E91", round(E91["idle_level"]["mean"], 3),
          "| E86", round(E86["idle_level"]["mean"], 3))
    print("-- leakage slope auto (W/C): E112a", round(A["leak"]["k_w_per_c"], 4), "| E91", round(E91["leak"]["k_w_per_c"], 4),
          "| E86", round(E86["leak"]["k_w_per_c"], 4))

    print("\n== A2: pass times (s), from logs/e112-queue.log")
    for line in open(os.path.join(HERE, "logs", "e112-queue.log")):
        if " rc=" in line or "skipping" in line or "starts at" in line:
            print("  " + line.rstrip())

    print("\n== B1: (b)'s per-tile ratio to random (D over zeros, per pass D/D(random), mean over passes) against E95 on aifoundry3")
    reg = load(ROOT, "tools/claims-v3/e112/predictions-e112.json")
    elig = reg["b"]["cross_card"]["X4"]["eligible"]
    for lab, f in (("registered reduction, two kept passes (11250, 11251)", ("b-e95-card1", "scored.json")),
                   ("POST HOC, three passes, the zeros-line limit raised to 0.26 W", ("b-e95-card1", "posthoc-gate026", "scored-posthoc-gate026.json"))):
        s = load(HERE, *f)
        rows = s["cross_card"]["primary"]["rows"]
        print(f"-- {lab}")
        for ty in ("fp32", "fp16", "int8"):
            d = [(abs(v["r_card1"]["mean"] - v["r_aifoundry3"]["mean"]), v["r_card1"]["mean"] - v["r_aifoundry3"]["mean"], n)
                 for n, v in rows.items() if n.startswith(ty + ".") and "r_card1" in v and v["r_card1"]["mean"] is not None]
            d.sort()
            print(f"  {ty}: {len(d)} tiles; max |r(card 1) - r(aifoundry3)| {d[-1][0]:.4f} ({d[-1][2]}); median |diff| "
                  f"{statistics.median([x[0] for x in d]):.4f}; mean diff {statistics.fmean([x[1] for x in d]):+.4f}")
        rat = sorted(rows[n]["D_aifoundry3"]["mean"] / rows[n]["D_card1"]["mean"] for n in elig)
        print(f"  B2 card scale: median D(aifoundry3, E95 dips removed) / D(card 1) over the {len(rat)} X4-eligible tiles "
              f"{statistics.median(rat):.4f} (IQR {rat[len(rat) // 4]:.4f}-{rat[(3 * len(rat)) // 4]:.4f})")

    print("\n== B3: the pass gates of (b) at every reduction")
    for f in ("e112b.json", "e112b-dipskept.json", "e112b-leak0.1994.json", "e112b-leak0.545.json", "e112b-leak0.3803.json",
              "e112b-leak0.json", os.path.join("posthoc-gate026", "e112b-posthoc-gate026.json")):
        r = load(HERE, "b-e95-card1", f)
        print(f"  {f}: kept {r['passes']}, leak {r['leak']['k_w_per_c']:.4f}, set aside {json.dumps(r['passes_set_aside'])}")
    print("  (a), for comparison:")
    for f in ("e91.json", "e91-dipskept.json", "e91-leak0.1994.json", "e91-leak0.545.json", "e91-leak0.3803.json", "e91-leak0.json"):
        r = load(HERE, "a-e91-rerun", f)
        print(f"  {f}: kept {r['passes']}, leak {r['leak']['k_w_per_c']:.4f}, set aside {json.dumps(r['passes_set_aside'])}")

    print("\n== B4: the budget rule's arithmetic at the spare's decision (claim + 2,980 s)")
    print("  a:11214 projected 334 s: end claim + 3,314 s, limit claim + 3,480 s, margin", 3480 - 3314, "s")
    print("  had b:11253 stood in its place, projected 502 s: end claim + 3,482 s, past the limit by", 2980 + 502 - 3480, "s")
    print("\n== T: card time, claim post to release edit (logs/push-and-claim-times.txt)")
    print("  claim 12:53:53.736 PST (Discord's timestamp); release saved about 13:49:2x PST (the save returned 13:49:24):",
          f"{(13 * 3600 + 49 * 60 + 24 - (12 * 3600 + 53 * 60 + 53.736)) / 60:.1f} card-minutes of 60")


if __name__ == "__main__":
    main()
