#!/usr/bin/env python3
"""E88 corrections after verification: the desk check (Sat 31 Oct 2026, written after the verifier's report).

Prints every number the README's "Corrections after verification" quotes, from committed files only: this
directory's frozen reductions (e88*.json, scored.json), the raw launch records, and tools/claims-v3/rpath/'s
e88.json (stream model, fit) and predictions-e88.json. Standard library only. Everything here is post hoc: it
changes no registered number and no verdict.

    python3 docs/reports/data/2026-10-31-e88-result-path/corrections-check.py > .../corrections-check.txt
"""
import glob
import hashlib
import json
import math
import os
import statistics

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
TOOLS = os.path.join(REPO, "tools", "claims-v3", "rpath")
T95 = {1: 12.706, 2: 4.303, 3: 3.182, 4: 2.776, 5: 2.571}
SPLITS = {"fp32": ("fp32.c_abs", "fp32.r_abs", "fp32.r_walk", "fp32.randn"),
          "fp16": ("fp16.c_cancel", "fp16.r_cancel", "fp16.r_walk", "fp16.randn"),
          "int8": ("int8.c_cancel", "int8.r_cancel", "int8.r_walk", "int8.full")}


def load(*p):
    with open(os.path.join(*p)) as f:
        return json.load(f)


def sha(p):
    with open(p, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def st(v):
    v = [float(x) for x in v]
    m = statistics.fmean(v)
    h = statistics.stdev(v) / math.sqrt(len(v)) * T95[len(v) - 1]
    return m, h


def f(s, nd=3):
    return f"{s[0]:.{nd}f} +- {s[1]:.{nd}f}"


def parts(pp, ty, key="D"):
    """Per pass: (i), (iii), (ii), the total r_walk, and the random anchor, for one format."""
    c, frz, walk, anc = SPLITS[ty]
    P = list(pp)
    i_ = [pp[p][c][key] for p in P]
    iii = [pp[p][frz][key] - pp[p][c][key] for p in P]
    ii = [pp[p][walk][key] - pp[p][frz][key] for p in P]
    tot = [pp[p][walk][key] for p in P]
    an = [pp[p][anc][key] for p in P]
    return i_, iii, ii, tot, an


e = load(HERE, "e88.json")
sc = load(HERE, "scored.json")
mdl = load(TOOLS, "e88.json")
reg = load(TOOLS, "predictions-e88.json")
pp = e["per_pass"]
print("E88 corrections after verification: the desk check (Sat 31 Oct 2026). Post hoc throughout; no registered")
print("number changes and no verdict moves. The frozen outputs' sha256 (compare with the data commit f1c7412e):")
for nm in ("scored.json", "results.md", "e88.json", "e88-keepdips.json", "e88-leak0.545.json", "e88-leak0.3803.json",
           "e88-leak0.json"):
    print(f"   {sha(os.path.join(HERE, nm))}  {nm}")
print(f"Passes kept: {e['passes']}; t(0.975, {len(pp) - 1}) = {T95[len(pp) - 1]}")

print("\nC1 (major). WHAT 'RANDOM' MEANS IN THE SPLIT")
for nm in ("fp32.r_walk", "fp16.r_walk", "int8.r_walk"):
    print(f"   {nm}: {mdl['items'][nm]['rule']}  [tools/claims-v3/rpath/e88.json items.{nm}.rule]")
for ty in SPLITS:
    i_, iii, ii, tot, an = parts(pp, ty)
    anc = SPLITS[ty][3]
    sh = [st([x / a for x, a in zip(v, an)]) for v in (i_, iii, ii, [a - t for a, t in zip(an, tot)])]
    print(f"   {ty}: r_walk / {anc} = {f(st([t / a for t, a in zip(tot, an)]))}; as shares of {anc} (per pass): "
          f"(i) {f(sh[0])}, (iii) {f(sh[1])}, (ii) {f(sh[2])}, {anc} - r_walk {f(sh[3])}")
x32 = sc["primary"]["contrasts"]["X32"]
print(f"   X32 ({x32['what']}): {x32['D']['mean']:.3f} +- {x32['D']['ci95']:.3f} W [scored.json primary.contrasts.X32.D]")

print("\nC2. R32bus IS NOT A PURE BUS SWING: r_het's OWN k = 0 OPERAND TOGGLES")
print(f"   r_het: {mdl['items']['fp32.r_het']['rule']}")
m = mdl["model"]
het, ab = m["fp32.r_het"], m["fp32.r_abs"]
fit = mdl["fit"]["fp32"]
F, a_, c_, b_ = fit["coef"]
d = {"live": het["live_frac"] - ab["live_frac"], "bus": het["bus_bits_per_op"] - ab["bus_bits_per_op"],
     "prod": het["prod"] - ab["prod"], "res": het["res_bits_per_op"] - ab["res_bits_per_op"]}
print(f"   r_het - r_abs per op (stream model): live {d['live']:+.4f}, operand-bus bits {d['bus']:+.1f}, product bits "
      f"{d['prod']:+.1f}, result bits {d['res']:+.1f}  [tools/claims-v3/rpath/e88.json model.fp32.r_het, model.fp32.r_abs]")
wb, wp, wr = a_ * d["bus"], c_ * d["prod"], b_ * d["res"]
cov = fit["cov"]
v = [0.0, d["bus"], d["prod"], 0.0]
res_se = math.sqrt(sum(v[i] * v[j] * cov[i][j] for i in range(4) for j in range(4)))
resid = wb + wp
print(f"   priced at the frozen fp32 fit: bus {wb:.3f} W + product {wp:.3f} W + result {wr:.3f} W = {wb + wp + wr:.3f} W "
      f"(the registered prediction 4.753); the operand residue {resid:.3f} +- {res_se:.3f} W (1 SE of the fit)")
m32 = [c for c in reg["contrasts"] if c["name"] == "M32"][0]["predicted"]["mu"]
m32m = sc["primary"]["contrasts"]["M32"]["D"]["mean"]
k = m32m / m32
print(f"   M32 measured / predicted = {m32m:.3f} / {m32:.3f} = {k:.3f}; the residue scaled by it {resid * k:.3f} W")
P = list(pp)
den = [pp[p]["fp32.r_walk"]["D"] - pp[p]["fp32.r_abs"]["D"] for p in P]
num = [pp[p]["fp32.r_het"]["D"] - pp[p]["fp32.r_abs"]["D"] for p in P]
print(f"   H5 per-pass share, raw (registered): {f(st([n / q for n, q in zip(num, den)]))}")
print(f"   with {resid:.3f} W taken off each pass: {f(st([(n - resid) / q for n, q in zip(num, den)]))}; "
      f"with {resid * k:.3f} W: {f(st([(n - resid * k) / q for n, q in zip(num, den)]))}")
print(f"   R32bus: raw {f(st(num))} W; less {resid:.3f} W {f(st([n - resid for n in num]))} W; "
      f"less {resid * k:.3f} W {f(st([n - resid * k for n in num]))} W")

print("\nC3. THE MODEL'S 17 OF 19: BAND WIDTHS AND WHERE IT MISSES INSIDE THEM")
hw = []
for c in reg["contrasts"]:
    pr, ms = c["predicted"], sc["primary"]["contrasts"][c["name"]]["D"]["mean"]
    hw.append((pr["tol"], c["name"]))
    rel = f"{(ms - pr['mu']) / pr['mu'] * 100:+.0f}%" if abs(pr["mu"]) >= 1 else "-"
    print(f"   {c['name']:7s} predicted {pr['mu']:6.3f} [{pr['lo']:.3f}, {pr['hi']:.3f}] (+-{pr['tol']:.2f})  "
          f"measured {ms:6.3f}  {ms - pr['mu']:+.2f} W  {rel}")
print(f"   band half-widths: {min(hw)[0]:.2f} ({min(hw)[1]}) to {max(hw)[0]:.2f} ({max(hw)[1]})  "
      f"[tools/claims-v3/rpath/predictions-e88.json contrasts.*.predicted.tol]")

print("\nC4. D IS BOARD POWER; THE SAME SPLIT ON THE RAIL (Drail)")
print("   tools/claims-v3/kinds/reduce_e78.py: P = mean board_w over [t0+1 s, t0+3 s), p80 = P - k (T_window - T_launch),")
print("   D = p80 - the type's zeros p80; Drail = rail80 - the type's zeros rail80 (the same window and correction)")
for ty in SPLITS:
    i_, iii, ii, tot, _ = parts(pp, ty, "Drail")
    shs = [st([x / t for x, t in zip(vv, tot)]) for vv in (i_, iii, ii)]
    print(f"   {ty} on the rail: (i) {f(st(i_), 2)}, (iii) {f(st(iii), 2)}, (ii) {f(st(ii), 2)} of {f(st(tot), 2)} W; "
          f"shares {f(shs[0])} / {f(shs[1])} / {f(shs[2])}")

print("\nC5. THE REGISTERED LEAKAGE-SLOPE ARMS ON THE WATTS AND THE SHARES")
arms = [("auto (primary)", "e88.json"), ("0.545", "e88-leak0.545.json"), ("0.3803", "e88-leak0.3803.json"),
        ("0", "e88-leak0.json")]
vals = {}
for nm, fn in arms:
    q = load(HERE, fn)
    print(f"   arm {nm:15s} slope {q['leak']['k_w_per_c']:.4f} W/C, passes {q['passes']}")
    for ty in SPLITS:
        i_, iii, ii, tot, _ = parts(q["per_pass"], ty)
        mm = [statistics.fmean(x) for x in (i_, iii, ii, tot)]
        sh = [statistics.fmean([x / t for x, t in zip(vv, tot)]) for vv in (i_, iii, ii)]
        vals.setdefault(ty, []).append((nm, mm, sh))
        print(f"      {ty}: (i) {mm[0]:.3f}  (iii) {mm[1]:.3f}  (ii) {mm[2]:.3f}  total {mm[3]:.3f} W;  shares "
              f"{sh[0]:.3f} / {sh[1]:.3f} / {sh[2]:.3f}")
print("   range across the four, as (arm low, arm high) minus the primary:")
for ty, rows in vals.items():
    prim = rows[0]
    out = []
    for j, lab in enumerate(("(i)", "(iii)", "(ii)", "total")):
        xs = [r[1][j] for r in rows]
        out.append(f"{lab} {min(xs):.2f}-{max(xs):.2f} ({min(xs) - prim[1][j]:+.2f}/{max(xs) - prim[1][j]:+.2f})")
    shmove = max(abs(r[2][j] - prim[2][j]) for r in rows for j in range(3)) * 100
    print(f"      {ty}: " + "; ".join(out) + f"; largest share move {shmove:.1f} points")

print("\nC6. THE DIPS-KEPT ARM HAS THREE PASSES, BELOW THE REGISTERED MINIMUM OF FOUR")
kd = load(HERE, "e88-keepdips.json")
print(f"   e88-keepdips.json passes {kd['passes']}, set aside {[x['pass'] for x in kd['passes_set_aside']]}; "
      f"predictions-e88.json primary.min_passes = {reg['primary']['min_passes']}")
print(f"   scored.json arms.dips-kept.tally {sc['arms']['dips-kept']['tally']} (score_e88.py has no min_passes check); "
      f"the verdicts it moves: {', '.join(r for r, a in sc['verdicts_moving_between_arms'].items() if 'dips-kept' in a)}")

print("\nC7. S AGAINST D: WHERE ONE'S POINT FALLS OUTSIDE THE OTHER'S INTERVAL")
for nm, c in sc["primary"]["contrasts"].items():
    D, S = c["D"], c["S"]
    s_in_d, d_in_s = D["lo"] <= S["mean"] <= D["hi"], S["lo"] <= D["mean"] <= S["hi"]
    overlap = not (S["hi"] < D["lo"] or S["lo"] > D["hi"])
    if not (s_in_d and d_in_s):
        print(f"   {nm}: D {D['mean']:.3f} [{D['lo']:.3f}, {D['hi']:.3f}], S {S['mean']:.3f} [{S['lo']:.3f}, {S['hi']:.3f}]: "
              f"S inside D's interval {s_in_d}, D inside S's {d_in_s}, intervals overlap {overlap}")
print(f"   intervals overlap in all {len(sc['primary']['contrasts'])} contrasts: "
      f"{all(not (c['S']['hi'] < c['D']['lo'] or c['S']['lo'] > c['D']['hi']) for c in sc['primary']['contrasts'].values())}")

print("\nC8. THE CARD'S RESULT WAS NEVER READ BACK")
cnt = {}
for fn in sorted(glob.glob(os.path.join(HERE, "aifoundry1-c1", "rpath", "*", "runs.jsonl"))):
    with open(fn) as fh:
        for line in fh:
            i0 = line.find('"result"')
            if i0 < 0:
                continue
            val = line[i0:].split('"')[3]
            cnt[val] = cnt.get(val, 0) + 1
print(f"   launch records' \"result\" over every pass and the smoke (runs.jsonl): {cnt}")
src = os.path.join(REPO, "workloads", "sparsity", "host", "main.cpp")
with open(src) as fh:
    for n, line in enumerate(fh, 1):
        if 'rawValues ? "unchecked"' in line:
            print(f"   workloads/sparsity/host/main.cpp:{n}: {line.strip()}")
ok = [nm for nm, ch in mdl["checks"].items() if isinstance(ch, dict) and ch.get("ok")]
print(f"   desk emulation instead (make_e88.py --check): {len(ok)} of {len(mdl['checks'])} checks ok "
      f"[tools/claims-v3/rpath/e88.json checks]")

print("\nC9. THE NUMBERS BEHIND THE BLOG POINTS' WORDING")
it = e["items"]
print(f"   fp32.ones D {it['fp32.ones']['D']['mean']:.3f} +- {it['fp32.ones']['D']['ci95']:.3f} W, fp32.randn D "
      f"{it['fp32.randn']['D']['mean']:.3f} +- {it['fp32.randn']['D']['ci95']:.3f} W, ratio "
      f"{it['fp32.ones']['D']['mean'] / it['fp32.randn']['D']['mean']:.3f}  [e88.json items.fp32.ones.D, items.fp32.randn.D]")
for nm in ("M32s", "R32s", "A16"):
    c = sc["primary"]["contrasts"][nm]
    print(f"   {nm} ({c['what']}): {c['D']['mean']:.3f} +- {c['D']['ci95']:.3f} W, predicted {c['predicted']['mu']:.2f}")
print(f"   s_abs: {mdl['items']['fp32.s_abs']['rule']}")

print("\nC10. THE ~12 W SENTENCE: S (OVER THE IDLE BRACKET) OF EVERY ITEM")
for nm, x in sorted(it.items(), key=lambda kv: kv[1]["S"]["mean"]):
    print(f"   {nm:16s} S {x['S']['mean']:6.2f} W   {'below' if x['S']['mean'] < 12 else 'above'} 12 W")
with open(os.path.join(TOOLS, "E88.md")) as fh:
    hdr = fh.read().splitlines()[2]
print(f"   tools/claims-v3/rpath/E88.md line 3: {hdr[:70]}")
