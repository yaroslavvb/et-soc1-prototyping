#!/usr/bin/env python3
"""E113: the numbers the README's "Corrections after verification" cite, recomputed from committed files.

    python3 docs/reports/data/2026-11-01-e113-a-side-saturation/corrections-check.py \
        > docs/reports/data/2026-11-01-e113-a-side-saturation/corrections-check.txt

Sections C1-C10 follow the corrections in README § Corrections after verification; F checks that no data file and no
frozen file changed since the data commit 64e69cc3 (needs git; skipped without it). Every number here is post hoc,
read off the registered reduction (scored.json, runs.csv, the registered scorer's own functions) and E70's, Q132(b)'s
and E102's committed files. None is a registered verdict. Standard library only.
SPDX-License-Identifier: Apache-2.0
"""
import gzip
import json
import math
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO_DIR = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
sys.path.insert(0, os.path.join(REPO_DIR, "tools", "claims-v3", "e113"))
import score_e113 as S  # noqa: E402  (the registered scorer: its gates, per-pass values and fits)

REL = os.path.relpath(HERE, REPO_DIR)
DATA_COMMIT = "64e69cc3"
s = json.load(open(os.path.join(HERE, "scored.json")))
pred = json.load(open(os.path.join(HERE, "predictions-e113.json")))
ph = json.load(open(os.path.join(HERE, "posthoc.json")))
e70 = json.load(open(os.path.join(REPO_DIR, "docs/reports/data/2026-10-27-e70-saturation-ladder/scored.json")))
runs = S.load_runs(os.path.join(HERE, "runs.csv"))
per, kept = S.gate(runs)
val = S.pass_values(runs, kept)
it = s["items"]
D2 = s["D2_A"]
C = pred["constants"]
rung = {r["item"]: r for r in pred["rungs"]}
FIT = D2["fit_set"]
TOP = "alq_h23"
ALL16 = FIT + [TOP]


def f3(x):
    return "None" if x is None else f"{x:.3f}"


def paired(a, b):
    """dW(a) - dW(b) paired per kept pass (both read against the same zero, so the zero cancels)."""
    return S.mean_se([S.dw(val, p, a) - S.dw(val, p, b) for p in kept
                      if S.dw(val, p, a) is not None and S.dw(val, p, b) is not None])


print("E113 corrections-check (post hoc; the registered reduction: kept passes", kept, ")")
assert kept == s["passes_kept"], (kept, s["passes_kept"])

# ------------------------------------------------------------------------------------------------ C1
print("\nC1. The top rung out of sample under each law, and the A/B ratio rung by rung")
top = it[TOP]
b, bse = rung[TOP]["B_same_mask_E70_W"], rung[TOP]["B_same_mask_E70_se_W"]
c, cse = D2["c_refit"], D2["c_per_pass_mean_se"][1]
c0 = C["mirror_c"]
print(f"  {TOP} measured {top['dW']:.3f} +- {top['se']:.3f} W (scored.json items.{TOP}); E70's lq_h23 (the same mask on B) "
      f"{b:.3f} +- {bse:.3f} W")
pm = c * b
r = top["dW"] - pm
sig_a = r / top["se"]
sig_all = r / math.sqrt(top["se"] ** 2 + (c * bse) ** 2 + (b * cse) ** 2)
sig_b = r / math.sqrt(top["se"] ** 2 + (c * bse) ** 2)
print(f"  mirror, c refitted {c:.4f} +- {cse:.4f} (per pass): predicts {pm:.3f} W, residual {r:+.3f} W = {sig_a:+.1f} SE on the A "
      f"rung alone, {sig_b:+.1f} SE with E70's B-rung SE, {sig_all:+.1f} SE with E70's B-rung SE and c's SE "
      f"(scored.json D2_A.out_of_sample_alq_h23.res_M_refit {D2['out_of_sample_alq_h23']['res_M_refit']:+.4f})")
pm0 = c0 * b
r0 = top["dW"] - pm0
print(f"  mirror, c frozen {c0:.4f}: predicts {pm0:.3f} W, residual {r0:+.3f} W = {r0 / top['se']:+.1f} SE on the A rung alone, "
      f"{r0 / math.sqrt(top['se'] ** 2 + (c0 * bse) ** 2):+.1f} SE with E70's B-rung SE. The frozen c was fitted on E70's alq "
      f"rungs at k = {C['mirror_c_fitted_on_k']} (predictions-e113.json constants), so k = 23 was in its fit: for the frozen "
      f"mirror the top rung is a replicate of a fitted rung, not out of sample")
wa = D2["WA_refit_W"]
psa = S.cov(top["S_A_W"], wa)
print(f"  curve in S_A, W refitted {wa:.3f} W: predicts {psa:.3f} W, residual {top['dW'] - psa:+.3f} W "
      f"({(top['dW'] - psa) / top['se']:.1f} SE); the rung sits {top['dW'] - wa:.3f} W ({(top['dW'] - wa) / top['se']:.1f} SE) "
      f"above W")
print("  per rung, E113's A step over E70's B step of the same mask (SE from both rungs' SEs):")
ratio = {}
for n in ALL16:
    y, se = it[n]["dW"], it[n]["se"]
    bb, bbse = rung[n]["B_same_mask_E70_W"], rung[n]["B_same_mask_E70_se_W"]
    q = y / bb
    qse = q * math.sqrt((se / y) ** 2 + (bbse / bb) ** 2)
    ratio[n] = q
    print(f"    {n:8s} k {rung[n]['k']:2d} {rung[n]['layout']:6s} A {y:6.3f} / B {bb:6.3f} ({rung[n]['B_same_mask_item']}) "
          f"= {q:.3f} +- {qse:.3f}")
lo_small = [n for n in ALL16 if rung[n]["layout"] == "low" and rung[n]["k"] <= 6]
rest = [n for n in ALL16 if n not in lo_small and n != TOP]
print(f"  low layout, k <= 6: {', '.join(f'{ratio[n]:.2f}' for n in lo_small)} (k = "
      f"{', '.join(str(rung[n]['k']) for n in lo_small)}); range {min(ratio[n] for n in lo_small):.2f}-"
      f"{max(ratio[n] for n in lo_small):.2f}")
print(f"  low layout k = 8-16 and every spread mask: range {min(ratio[n] for n in rest):.2f}-{max(ratio[n] for n in rest):.2f} "
      f"({len(rest)} rungs); the top rung {ratio[TOP]:.3f}")
for a, bn in (("alq_h8", "lq_h8"), ("als_h8", "ls_h8")):
    q = S.mean_se([S.dw(val, p, a) / S.dw(val, p, bn) for p in kept])
    print(f"  with E113's own B rung at k = 8: {a} / {bn} = {q[0]:.3f} +- {q[1]:.3f} (per pass; = rho(8) / 2)")

# ------------------------------------------------------------------------------------------------ C2
print("\nC2. Curves in A's own summed prices S_A over the 15 fit rungs, and the pairs where a larger S_A costs less")
pts = [(it[n]["S_A_W"], it[n]["dW"], n) for n in FIT]


def rms_of(f):
    return math.sqrt(sum((f(x) - y) ** 2 for x, y, _ in pts) / len(pts))


w1, r1 = S.fit_w([(x, y) for x, y, _ in pts])
print(f"  registered, one parameter, W (1 - e^(-S/W)): W {w1:.3f} W, rms {r1:.3f} W (scored.json D2_A.R_SA_refit_W "
      f"{D2['R_SA_refit_W']:.3f}); P2's bands: ACCEPTED <= 0.40, REJECTED > 0.60, INCONCLUSIVE between")


def fit_two(g):
    """y = W g(S; K): W by least squares at each K on a log grid, then a golden refinement of K."""
    def at(k):
        gs = [g(x, k) for x, _, _ in pts]
        sgg = sum(v * v for v in gs)
        w = sum(v * y for v, (_, y, _) in zip(gs, pts)) / sgg
        return math.sqrt(sum((w * v - y) ** 2 for v, (_, y, _) in zip(gs, pts)) / len(pts)), w
    best = None
    lo, hi, n = 0.05, 2000.0, 20000
    for i in range(n + 1):
        k = lo * (hi / lo) ** (i / n)
        e, w = at(k)
        if best is None or e < best[0]:
            best = (e, w, k)
    a, bnd = best[2] / 1.01, best[2] * 1.01
    gr = (math.sqrt(5) - 1) / 2
    for _ in range(80):
        x1, x2 = bnd - gr * (bnd - a), a + gr * (bnd - a)
        if at(x1)[0] < at(x2)[0]:
            bnd = x2
        else:
            a = x1
    k = 0.5 * (a + bnd)
    e, w = at(k)
    return e, w, k


e2, w2, k2 = fit_two(lambda x, k: 1 - math.exp(-x / k))
e3, w3, k3 = fit_two(lambda x, k: x / (x + k))
print(f"  two parameters, W (1 - e^(-S/K)): W {w2:.2f} W, K {k2:.2f} W, rms {e2:.3f} W")
print(f"  two parameters, W S / (S + K): W {w3:.2f} W, K {k3:.2f} W, rms {e3:.3f} W")


def pava(y):
    blocks = [[v, 1] for v in y]
    i = 0
    while i < len(blocks) - 1:
        if blocks[i][0] / blocks[i][1] > blocks[i + 1][0] / blocks[i + 1][1]:
            blocks[i][0] += blocks[i + 1][0]
            blocks[i][1] += blocks[i + 1][1]
            del blocks[i + 1]
            i = max(i - 1, 0)
        else:
            i += 1
    out = []
    for t, cnt in blocks:
        out += [t / cnt] * cnt
    return out, len(blocks)


srt = sorted(pts)
fit_iso, nblk = pava([y for _, y, _ in srt])
r_iso = math.sqrt(sum((y - f) ** 2 for (_, y, _), f in zip(srt, fit_iso)) / len(srt))
print(f"  any non-decreasing function of S_A (isotonic least squares): rms {r_iso:.3f} W, using {nblk} free levels for 15 rungs")
inv = []
for i in ALL16:
    for j in ALL16:
        if it[i]["S_A_W"] < it[j]["S_A_W"] and it[i]["dW"] > it[j]["dW"]:
            m, se, nn = paired(i, j)
            inv.append((m / se, i, j, m, se))
inv.sort(reverse=True)
big = [t for t in inv if t[0] >= 3]
print(f"  pairs with the smaller S_A but the larger step: {len(inv)}; at >= 3 SE (paired per pass): {len(big)}")
for sg, i, j, m, se in big:
    print(f"    {i:8s} (S_A {it[i]['S_A_W']:6.3f}, dW {it[i]['dW']:.3f}) - {j:8s} (S_A {it[j]['S_A_W']:6.3f}, dW {it[j]['dW']:.3f})"
          f" = {m:+.3f} +- {se:.3f} W ({sg:.1f} SE)")
m, se, nn = paired("als_h4", "alq_h8")
print(f"  the clearest: als_h4 (S_A {it['als_h4']['S_A_W']:.2f} W) {it['als_h4']['dW']:.3f} +- {it['als_h4']['se']:.3f} W against "
      f"alq_h8 (S_A {it['alq_h8']['S_A_W']:.2f} W) {it['alq_h8']['dW']:.3f} +- {it['alq_h8']['se']:.3f} W: {m:+.3f} +- {se:.3f} W "
      f"paired ({m / se:.1f} SE)")
print(f"  any non-decreasing f(S_A) has f(3.92) <= f(5.78), so it misses one of those two rungs by at least {m / 2:.3f} W "
      f"({m / 2 / max(it['als_h4']['se'], it['alq_h8']['se']):.0f} SE of either rung)")

# ------------------------------------------------------------------------------------------------ C3
print("\nC3. What P3's spread rungs can and cannot separate")
p3 = s["rules"]["P3"]
print(f"  the 7 spread rungs, both laws frozen on E70's low layout: mirror {p3['measured']:.3f} W, curve in S_A "
      f"{p3['R_SA_frozen_spread_W']:.3f} W (scored.json rules.P3): the curve reads them as well")
lowfit = [n for n in FIT if n.startswith("alq_")]
r_wa_low = math.sqrt(sum((it[n]["dW"] - S.cov(it[n]["S_A_W"], C["WA_W"])) ** 2 for n in lowfit) / len(lowfit))
r_m_low = math.sqrt(sum((it[n]["dW"] - c0 * rung[n]["B_same_mask_E70_W"]) ** 2 for n in lowfit) / len(lowfit))
print(f"  the 8 low rungs in the fit (the layout both frozen constants were fitted on, E70's): curve {r_wa_low:.3f} W, mirror "
      f"{r_m_low:.3f} W; alq_h8: curve {S.cov(it['alq_h8']['S_A_W'], C['WA_W']) - it['alq_h8']['dW']:+.3f} W over, mirror "
      f"{c0 * rung['alq_h8']['B_same_mask_E70_W'] - it['alq_h8']['dW']:+.3f} W over")
print(f"  both layouts, each law refitted (P4): curve {D2['R_SA_refit_W']:.3f} W, mirror {D2['R_M_refit_W']:.3f} W, "
      f"ratio {D2['R_SA_refit_W'] / D2['R_M_refit_W']:.2f}")

# ------------------------------------------------------------------------------------------------ C4
print("\nC4. rho, per designed bit A over B, in both sessions")
for row in e70["D4"]:
    if row["h"] in (8, 12, 16, 23):
        print(f"  E70 (low layout, 27 Oct): rho({row['h']}) = {row['rho_per_bit']:.3f} +- {row['se']:.3f} "
              f"(E70 scored.json D4 h={row['h']})")
for lay in ("low", "spread"):
    q = s["rho8"][lay]
    print(f"  E113 ({lay}): rho(8) = {q['rho']:.3f} +- {q['se']:.3f}, per pass {[round(x, 3) for x in q['per_pass']]}")
lq8 = [S.dw(val, p, "lq_h8") for p in kept]
al8 = [S.dw(val, p, "alq_h8") for p in kept]
e70lq = {x["item"]: x for x in e70["lq"]}["lq_h8"]
e70al = {x["item"]: x for x in e70["alq"]}["alq_h8"]
print(f"  E113 lq_h8 per pass {[round(x, 3) for x in lq8]} W, mean {it['lq_h8']['dW']:.3f} +- {it['lq_h8']['se']:.3f}; "
      f"E70 lq_h8 {e70lq['dW']:.3f} +- {e70lq['se']:.3f}")
print(f"  E113 alq_h8 per pass {[round(x, 3) for x in al8]} W, mean {it['alq_h8']['dW']:.3f} +- {it['alq_h8']['se']:.3f}; "
      f"E70 alq_h8 {e70al['dW']:.3f} +- {e70al['se']:.3f}")
print(f"  E113's alq_h8 over E70's lq_h8: 2 x {it['alq_h8']['dW']:.3f} / {e70lq['dW']:.3f} = "
      f"{2 * it['alq_h8']['dW'] / e70lq['dW']:.3f}; so the two sessions' low-layout rho(8) differ mostly through the B rung")
allr = [r_["rho_per_bit"] for r_ in e70["D4"] if r_["h"] in (8, 12, 16)] + [s["rho8"]["low"]["rho"], s["rho8"]["spread"]["rho"]]
print(f"  range at k = 8-16 over both sessions: {min(allr):.3f}-{max(allr):.3f}")

# ------------------------------------------------------------------------------------------------ C5
print("\nC5. What the stock sampler and ettelem config ask of the PMIC (reads only)")
src = open(os.path.join(REPO_DIR, "tools/ettelem/ettelem.cpp")).read().split("\n")
fn = None
for i, line in enumerate(src, 1):
    mm = re.match(r"^\s*(?:[\w:<>*&]+\s+)+(\w+)\([^;]*\)\s*(?:const\s*)?\{\s*$", line)
    if mm:
        fn = mm.group(1)
    for cmd in ("DM_CMD_GET_ASIC_VOLTAGE", "DM_CMD_GET_MODULE_VOLTAGE", "DM_CMD_SET_STATS_RUN_CONTROL"):
        if cmd in line:
            print(f"  tools/ettelem/ettelem.cpp:{i} in {fn}(): {cmd}")
nlines, resets, n_die, n_reg = 0, set(), 0, 0
passes = sorted(os.listdir(os.path.join(HERE, "aifoundry3", "e113"))) + ["../smoke-p1130"]
for pdir in passes:
    path = os.path.normpath(os.path.join(HERE, "aifoundry3", "e113", pdir, "telemetry.jsonl.gz"))
    with gzip.open(path, "rt") as fh:
        for line in fh:
            if not line.startswith("{"):
                continue
            d = json.loads(line)
            nlines += 1
            resets.add(d.get("since_reset_ms"))
            n_die += "die_mv" in d     # printed only when GET_ASIC_VOLTAGE answered (ettelem.cpp sample())
            n_reg += "reg_mv" in d     # printed only when GET_MODULE_VOLTAGE answered
print(f"  saved 10 Hz sampler readings, 7 passes and the smoke (telemetry.jsonl.gz): {nlines}; with die_mv (GET_ASIC_VOLTAGE) "
      f"{n_die}, with reg_mv (GET_MODULE_VOLTAGE) {n_reg}; since_reset_ms values seen: "
      f"{sorted(x for x in resets if x is not None)} (-1: no statistics reset)")
cfg = [line for line in open(os.path.join(HERE, "logs", "session.log")) if " config config-session-" in line]
print(f"  ettelem config reads in logs/session.log: {len(cfg)}")
lib = open(os.path.join(REPO_DIR, "tools/claims-v3/lib.sh")).read().split("\n")
fn = None
for i, line in enumerate(lib, 1):
    mm = re.match(r"^\s*(\w+)\(\)\s*\{", line)
    if mm:
        fn = mm.group(1)
    if line.startswith("die_c()") or "=$(die_c" in line:
        where = "the definition" if line.startswith("die_c()") else f"in {fn}()"
        print(f"  tools/claims-v3/lib.sh:{i} ({where}): {line.strip()[:100]}")
print("  (heat_to() returns at once on aifoundry3, where lib.sh:31 leaves GOV_FREE empty; block_begin and block_end call die_c once "
      "each per pass)")

# ------------------------------------------------------------------------------------------------ C6
print("\nC6. The op rate's unit")
rates = [per[p]["mean_rate"] for p in sorted(per)]
print(f"  reduce_hl.py's rate is iters x minions per second over the run window ('fma: minion-ops/s'); pass means "
      f"{min(rates) / 1e9:.4f}-{max(rates) / 1e9:.4f} G minion-ops/s over the card's 1,024 minions = "
      f"{min(rates) / 1024 / 1e6:.3f}-{max(rates) / 1024 / 1e6:.3f} M ops/s per minion (600 MHz / 546 cycles = "
      f"{600e6 / 546 / 1e6:.3f} M)")

# ------------------------------------------------------------------------------------------------ C7
print("\nC7. What the two sides share: the dumped tiles of pass 1133 (A tile then B tile, 256 fp32 words each)")


def words(path):
    raw = open(path, "rb").read()
    w = [int.from_bytes(raw[i:i + 4], "little") for i in range(0, len(raw), 4)]
    return w[:256], w[256:512]


for name in ("alq_h8", "lq_h8", "als_h8", "ls_h8"):
    A, B = words(os.path.join(HERE, "aifoundry3", "e113", "p1133", "tiles", f"{name}.b1133.bin"))
    da, db = sorted(set(A)), sorted(set(B))
    xa = sorted({x ^ y for x in da for y in da if x < y})
    print(f"  {name:7s}: {len(da)} distinct A word(s) {['%08x' % x for x in da][:2]}, {len(db)} distinct B word(s)"
          + (f"; A words differ by {['%06x' % x for x in xa]}" if xa else "")
          + (f"; B = {['%08x' % x for x in db]}" if len(db) == 1 else ""))
    if len(db) > 1:
        rows = [B[i * 16:(i + 1) * 16] for i in range(16)]
        lane_x = sorted({rw[l] ^ rw[8 + l] for rw in rows for l in range(8)})
        bases = sorted({rw[l] for rw in rows for l in range(8)})
        print(f"           B rows: {len(bases)} per-lane base words, each lane l against lane 8+l differs by "
              f"{['%06x' % x for x in lane_x]}")

# ------------------------------------------------------------------------------------------------ C8
print("\nC8. The et-who reads in the committed logs")
for lg in ("setup.log", "session.log"):
    stamp = None
    for line in open(os.path.join(HERE, "logs", lg)):
        mm = re.match(r"^(?:== )?(\d{4}-\d\d-\d\d[ T]\d\d:\d\d:\d\d)", line)
        if mm:
            stamp = mm.group(1)
        if "No process holds" in line or "holds an ET-SoC-1" in line:
            print(f"  logs/{lg}: after the line stamped {stamp}: {line.strip()}")
first = [line for line in open(os.path.join(HERE, "logs", "smoke.log")) if "#0 " in line][0]
print(f"  logs/smoke.log, the first launch: {first.strip()[:80]}")

# ------------------------------------------------------------------------------------------------ C9
print("\nC9. The bench against the card, and E102's composites on A")
for k, v in ph["bench_vs_card"].items():
    print(f"  k = {k:>2}: bench A/B net toggles {v['bench_A_over_B_nets']:.3f}, card A/B watts {v['card_A_over_B_W']:.3f} "
          f"(E113's alq over E70's lq, five days apart), bench over card {v['bench_over_card']:.3f} (posthoc.json bench_vs_card)")
own = it["alq_h8"]["dW"] / it["lq_h8"]["dW"]
bn8 = ph["bench_vs_card"]["8"]["bench_A_over_B_nets"]
print(f"  k =  8 in one session (E113's own lq_h8): card A/B {own:.3f}, bench over card {bn8 / own:.3f}")
e102 = os.path.join(REPO_DIR, "docs/reports/data/2026-11-01-e102-balanced-bit-prices/README.md")
for i, line in enumerate(open(e102), 1):
    cells = [x.strip().replace("*", "") for x in line.strip().strip("|").split("|")]
    if len(cells) == 12 and cells[0] in ("0", "6", "11", "16", "20", "22") and cells[1] == "mant":
        print(f"  E102 README:{i} bit {cells[0]}: A all-in over balanced, board {cells[9]}; rail {cells[10]}; bench {cells[11]}")

# ------------------------------------------------------------------------------------------------ C10
print("\nC10. Small facts the wording now uses")
d1 = {d["k"]: d for d in s["D1_A"]}
print(f"  D1_A: k = 3 {d1[3]['dW_spread_minus_low']:+.3f} +- {d1[3]['se']:.3f}, k = 4 {d1[4]['dW_spread_minus_low']:+.3f} +- "
      f"{d1[4]['se']:.3f} W (the dip); E70's B side: {[round(d['B_side_D1_E70_W'], 3) for d in s['D1_A']]} at k = "
      f"{[d['k'] for d in s['D1_A']]} (no dip)")

# ------------------------------------------------------------------------------------------------ F
print(f"\nF. Data and frozen files against the data commit {DATA_COMMIT}")
try:
    paths = [REL, "tools/claims-v3/e113"]
    ls = subprocess.run(["git", "-C", REPO_DIR, "ls-tree", "-r", DATA_COMMIT, "--"] + paths, capture_output=True, text=True,
                        check=True).stdout.split("\n")
    blobs = {}
    for line in ls:
        if line:
            meta, p = line.split("\t", 1)
            blobs[p] = meta.split()[2]
    now = subprocess.run(["git", "-C", REPO_DIR, "hash-object", "--stdin-paths"], input="\n".join(blobs) + "\n",
                         capture_output=True, text=True, check=True).stdout.split()
    changed = [p for p, h in zip(blobs, now) if blobs[p] != h]
    print(f"  {len(blobs)} files at {DATA_COMMIT} under {REL} and tools/claims-v3/e113; unchanged {len(blobs) - len(changed)}; "
          f"changed: {changed}")
except (OSError, subprocess.CalledProcessError) as exc:
    print(f"  skipped (no git here: {exc})")
