#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""E141, corrections after verification (Mon 2 Nov 2026): print every number the README's corrections C1-C6 quote, read from committed
files only (this directory, posthoc-after-verification/, the registration tools/claims-v3/e141/, Q138(m)'s loko-m7.json, the training
experiments' own reductions, E140's and E142's scored files, the tiles, docs/findings/14-card-behaviour.md, and tools/ettelem/ettelem.cpp
at two revisions through git). Desk only; it reads, it writes nothing but stdout.

    python3 docs/reports/data/2026-11-02-e141-blind5-aifoundry3/corrections-numbers.py > .../corrections-numbers.txt
"""
import hashlib
import json
import math
import os
import re
import subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
DD = os.path.join(ROOT, "docs", "reports", "data")
REG = os.path.join(ROOT, "tools", "claims-v3", "e141", "predictions-e141.json")
PH = os.path.join(HERE, "posthoc-after-verification")


def load(p):
    with open(p) as f:
        return json.load(f)


def rel(p):
    return os.path.relpath(p, ROOT)


def sha_file(p):
    with open(p, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def rms(xs):
    return math.sqrt(sum(x * x for x in xs) / len(xs))


# M7's aifoundry3 training experiments and the reduction each one's rows came from (fit_m5.py's and m6_rows.py's file lists; fit_m7.py
# adds E140's e140.json).
TRAIN = {"E78": "2026-10-31-e78-kinds-energy-matrix/e78.json", "E86": "2026-10-31-e86-real-tensors-energy/e86.json",
         "E90": "2026-10-31-e90-signs-spread/e90.json", "E92": "2026-11-01-e92-sign-split/e92.json",
         "E95": "2026-11-01-e95-real-tensors-energy/e95.json", "E115": "2026-11-01-e115-blind-pool/e115.json",
         "E121": "2026-11-01-e121-zero-gate-replicate/e121.json", "E122": "2026-11-01-e122-signs-replicate/e122.json",
         "E123": "2026-11-01-e123-tile-spread-rest/e123.json", "E127": "2026-11-02-e127-b-gate/e127.json",
         "E140": "2026-11-02-e140-blind4/e140.json"}

reg = load(REG)
T = reg["tiles"]
COV = reg["sets"]["coverage_tiles"]
P1 = reg["sets"]["priority1_by_format"]
e141 = load(os.path.join(HERE, "e141.json"))
IT = e141["items"]
sc = load(os.path.join(HERE, "scored.json"))

print("E141 corrections after verification: the numbers C1-C6 quote, from committed files")
print("=" * 100)

# ---------------------------------------------------------------- C1
print("\nC1  The footing of M7's aifoundry3 float training rows, and B1/P2 at it")
L = load(os.path.join(DD, "2026-11-02-q138m-model", "loko-m7.json"))
rows = [r for r in L["families"]["float"]["row_errors"] if r["card"] == "a3"]
rows8 = [r for r in L["families"]["int8"]["row_errors"] if r["card"] == "a3"]
print(f"  source: {rel(os.path.join(DD, '2026-11-02-q138m-model', 'loko-m7.json'))} > families.float|int8.row_errors (card a3)")
print(f"  {'exp':5} {'leak.mode':>9} {'k W/C':>8} {'the meter dips (reducer.dips)':44} {'float rows':>10} {'int8 rows':>9}  file")
k, dipsrm = {}, {}
for e, f in TRAIN.items():
    d = load(os.path.join(DD, f))
    k[e] = float(d["leak"]["k_w_per_c"])
    dr = (d.get("reducer") or {}).get("dips")
    dipsrm[e] = bool(dr) and dr.startswith("removed")
    dtxt = dr or "kept (no record; reduce_e78.py removes no dips)"
    nf = sum(1 for r in rows if r["exp"] == e)
    n8 = sum(1 for r in rows8 if r["exp"] == e)
    print(f"  {e:5} {str(d['leak']['mode']):>9} {k[e]:8.4f} {dtxt[:44]:44} {nf:10d} {n8:9d}  docs/reports/data/{f} > leak, reducer.dips")
nf = len(rows)
fixed = sum(1 for r in rows if r["exp"] in ("E121", "E122", "E123"))
at1994 = sum(1 for r in rows if abs(k[r["exp"]] - 0.1994) < 0.0001)
nodips = sum(1 for r in rows if dipsrm[r["exp"]])
print(f"  float rows: {nf}; at a FIXED 0.1994 (E121, E122, E123; leak.mode '0.1994'): {fixed}; at 0.1994 with E78's own fit: {at1994}; "
      f"with the meter's dips removed ({', '.join(e for e in TRAIN if dipsrm[e])}): {nodips}; with them kept: {nf - nodips}")


def wmean(w):
    return sum(w(r) * k[r["exp"]] for r in rows) / sum(w(r) for r in rows)


kr, kd, kd2 = wmean(lambda r: 1.0), wmean(lambda r: max(r["D"], 0.0)), wmean(lambda r: r["D"] ** 2)
print(f"  the training rows' footing (their sessions' slopes averaged): by rows {kr:.5f}; weighted by D {kd:.5f}; weighted by D^2 {kd2:.5f} W/C")
for fmt in ("fp32", "fp16"):
    rs = [r for r in rows if r["type"] == fmt]
    print(f"    {fmt}: {len(rs)} rows, by rows {sum(k[r['exp']] for r in rs) / len(rs):.4f}, by D^2 "
          f"{sum(r['D'] ** 2 * k[r['exp']] for r in rs) / sum(r['D'] ** 2 for r in rs):.4f}")
print(f"  the training sessions' own fits (auto) span {min(k[e] for e in k if e not in ('E121', 'E122', 'E123')):.4f}"
      f"-{max(k[e] for e in k if e not in ('E121', 'E122', 'E123')):.4f} W/C")
print(f"  E141's session fit (the registered primary): {e141['leak']['k_w_per_c']:.4f} W/C over {e141['leak']['n_runs']} runs  (e141.json > leak)")
print("  the post hoc arms use 0.2104 (the verifier's row count, from the slopes rounded to four places), 0.2163 and 0.2217")

b1lo = sc["primary"]["rules"]["E141-B1"]["interval"]["lo95"]
b1hi = sc["primary"]["rules"]["E141-B1"]["interval"]["hi95"]
p2hi = sc["primary"]["rules"]["E141-P2"]["interval"]["hi95"]
arms = [("dips kept, leak 0 (none)", sc["arms"]["leak0"]), ("dips kept, leak 0.1994", sc["arms"]["leak0.1994"])]
for kk in ("0.2104", "0.2163", "0.2217"):
    arms.append((f"dips kept, leak {kk} (post hoc)", load(os.path.join(PH, f"scored-leak{kk}.json"))["primary"]))
arms.append(("dips kept, auto (REGISTERED)", sc["primary"]))
arms.append(("dips kept, leak 0.3803", sc["arms"]["leak0.3803"]))
for kk in ("0.2104", "0.2163", "0.2217"):
    arms.append((f"dips removed, leak {kk} (post hoc)", load(os.path.join(PH, f"scored-nodips-leak{kk}.json"))["primary"]))
arms.append(("dips removed, auto (reported)", sc["arms"]["dips_removed"]))
print(f"  B1 interval [{b1lo:+.3f}, {b1hi:+.3f}] W; P2 upper line {p2hi:.3f} W   (scored.json > primary.rules.E141-B1|P2.interval)")
print("  sources: scored.json > primary and arms.*; posthoc-after-verification/scored-[nodips-]leak<k>.json > primary")
print(f"  {'arm':36} {'k':>7} {'P1':>14} {'P2':>14} {'P3':>14} {'B1 (floats)':>20} {'B2 (int8)':>18} {'C1':>8}")
for name, a in arms:
    if "rules" not in a:
        print(f"  {name:36} {a['leak']['k_w_per_c']:7.4f}  NOT SCORED (passes set aside: {[x['pass'] for x in a.get('set_aside', [])]})")
        continue
    R = a["rules"]

    def v(rule, key):
        x = R[rule]
        if x.get("verdict") == "NOT SCORED":
            return "NOT SCORED"
        return f"{x[key]:+.3f} {x['verdict']}" if key.startswith("bias") else f"{x[key]:.3f} {x['verdict']}"
    c1 = R["E141-C1"]
    c1s = "NOT SCORED" if c1.get("verdict") == "NOT SCORED" else f"{c1['inside']}/{c1['n']}"
    print(f"  {name:36} {a['leak']['k_w_per_c']:7.4f} {v('E141-P1', 'rms'):>14} {v('E141-P2', 'rms'):>14} {v('E141-P3', 'rms'):>14} "
          f"{v('E141-B1', 'bias_meas_minus_pred_w'):>20} {v('E141-B2', 'bias_meas_minus_pred_w'):>18} {c1s:>8}")
bp = sc["primary"]["rules"]["E141-B1"]["bias_meas_minus_pred_w"]
b1994 = sc["arms"]["leak0.1994"]["rules"]["E141-B1"]["bias_meas_minus_pred_w"]
kp = e141["leak"]["k_w_per_c"]
slope = (bp - b1994) / (kp - 0.1994)
print(f"  B1 moves {slope:+.3f} W per W/C between 0.1994 and {kp:.4f}; it reaches its lower line ({b1lo:+.3f}) at k = "
      f"{0.1994 + (b1lo - b1994) / slope:.4f} W/C")
for kk in ("0.2104", "0.2163", "0.2217"):
    b = load(os.path.join(PH, f"scored-leak{kk}.json"))["primary"]["rules"]["E141-B1"]["bias_meas_minus_pred_w"]
    bn = load(os.path.join(PH, f"scored-nodips-leak{kk}.json"))["primary"]["rules"]["E141-B1"]["bias_meas_minus_pred_w"]
    print(f"  at {kk}: B1 {b:+.3f} W with the dips kept, so the slope gap from {kp:.4f} accounts for {b - bp:+.3f} of the registered "
          f"{bp:+.3f} W ({(b - bp) / bp * -100:.0f}%); with the dips removed too {bn:+.3f} W ({(bn - bp) / bp * -100:.0f}% accounted for)")
for tag in ("leak0.2104", "leak0.2163", "leak0.2217", "nodips-leak0.2104", "nodips-leak0.2163", "nodips-leak0.2217"):
    s = load(os.path.join(PH, f"scored-{tag}.json"))["primary"]
    R = s["rules"]
    print(f"  post hoc {tag}, scored alone (posthoc-after-verification/scored-{tag}.json): passes {s['passes']} set aside "
          f"{[x['pass'] for x in s['set_aside']]}; M1 {R['E141-M1']['d_rms_w']:+.3f} [{R['E141-M1']['lo95']:+.3f}, {R['E141-M1']['hi95']:+.3f}] "
          f"{R['E141-M1']['verdict']}; M2 {R['E141-M2']['d_rms_w']:+.3f} [{R['E141-M2']['lo95']:+.3f}, {R['E141-M2']['hi95']:+.3f}] "
          f"{R['E141-M2']['verdict']}; H1-H3 {R['E141-H1']['rms']:.3f}/{R['E141-H2']['rms']:.3f}/{R['E141-H3']['rms']:.3f} C; "
          f"H4 {R['E141-H4']['inside']}/{R['E141-H4']['n']}; all 30: rms {s['reported']['M7']['power_all_nonanchor']['rms']:.3f} "
          f"bias {s['reported']['M7']['power_all_nonanchor']['bias']:+.3f} W")

# E142 on card 1: its training-matched fixed slope against its own fit
e2 = load(os.path.join(DD, "2026-11-02-e142-blind5-card1", "scored.json"))
e2p, e2a = e2["primary"], e2["arms"]["auto"]
print(f"  E142 (card 1, docs/reports/data/2026-11-02-e142-blind5-card1/scored.json): primary leak {e2p['leak']['mode']} "
      f"B1 {e2p['rules']['E142-B1']['bias_meas_minus_pred_w']:+.3f} {e2p['rules']['E142-B1']['verdict']}; arms.auto leak "
      f"{e2a['leak']['k_w_per_c']:.4f} B1 {e2a['rules']['E142-B1']['bias_meas_minus_pred_w']:+.3f} {e2a['rules']['E142-B1']['verdict']}")
# E140 on pool 4 (M6): the mean error over its rows at its session fit and at 0.1994
e0 = load(os.path.join(DD, "2026-11-02-e140-blind4", "scored.json"))
for name, a in (("primary", e0["primary"]), ("leak0.1994", e0["arms"]["leak0.1994"])):
    rr = a["power"]["rows"]
    fl = [r["error"] for t, r in rr.items() if r.get("type") in ("fp32", "fp16") and r.get("priority") == 1 and r.get("error") is not None]
    al = [r["error"] for t, r in rr.items() if r.get("error") is not None]
    print(f"  E140 (pool 4, M6; docs/reports/data/2026-11-02-e140-blind4/scored.json > {name}.power.rows): leak "
          f"{a['leak']['k_w_per_c']:.4f}: mean error over {len(al)} rows {sum(al) / len(al):+.3f} W; priority-1 floats ({len(fl)}) "
          f"{sum(fl) / len(fl):+.3f} W")

# ---------------------------------------------------------------- C2
print("\nC2  36 tiles = 30 new kinds + 6 anchors; three anchors are E78's own zeros tiles")
anchors = [t for t in T if T[t].get("pool_anchor")]
print(f"  anchors ({len(anchors)}): {', '.join(sorted(anchors))}; non-anchor tiles: {len(COV)} (predictions-e141.json > sets.coverage_tiles)")
for fmt in ("fp32", "fp16", "int8"):
    a = os.path.join(ROOT, "tools", "claims-v3", "kinds", "blind5", "tiles", fmt, f"{fmt}.anchor_zeros.bin")
    b = os.path.join(ROOT, "tools", "claims-v3", "kinds", "tiles", fmt, "zeros.bin")
    print(f"  {rel(a)} {sha_file(a)[:16]}  {rel(b)} {sha_file(b)[:16]}  identical: {sha_file(a) == sha_file(b)}")


def dT_err(t):
    return IT[t]["dT_win"]["mean"] - T[t]["M7"]["dT_win_c"]


p1all = [t for f in P1 for t in P1[f]]
print(f"  M7 heat rms (dT_win - M7): priority-1 per format (the rules) "
      f"{' / '.join(f'{rms([dT_err(t) for t in P1[f]]):.3f}' for f in ('fp32', 'fp16', 'int8'))} C; the 24 priority-1 "
      f"{rms([dT_err(t) for t in p1all]):.3f}; the 30 non-anchor {rms([dT_err(t) for t in COV]):.3f}; all 36 "
      f"{rms([dT_err(t) for t in T]):.3f} C")

# ---------------------------------------------------------------- C3
print("\nC3  Band widths: M7's power bands are wider than M6's, with the same errors")


def hw(t, m, q="D_95"):
    lo, hi = T[t][m][q]
    return (hi - lo) / 2


for fmt in ("fp32", "fp16", "int8"):
    ts = [t for t in COV if T[t]["type"] == fmt]
    h = {m: sum(hw(t, m) for t in ts) / len(ts) for m in ("M7", "M6", "M5")}
    hh = {m: sum(hw(t, m, "dT_win_95") for t in ts) / len(ts) for m in ("M7", "M6")}
    print(f"  {fmt} ({len(ts)} non-anchor tiles): mean power half-width M7 {h['M7']:.3f} / M6 {h['M6']:.3f} / M5 {h['M5']:.3f} W "
          f"(M7/M6 {h['M7'] / h['M6']:.2f}); heat half-width M7 {hh['M7']:.3f} / M6 {hh['M6']:.3f} C")
fl = [t for t in COV if T[t]["type"] != "int8"]
hf = {m: sum(hw(t, m) for t in fl) / len(fl) for m in ("M7", "M6")}
hhf = {m: sum(hw(t, m, "dT_win_95") for t in fl) / len(fl) for m in ("M7", "M6")}
print(f"  floats ({len(fl)}): power half-width M7 {hf['M7']:.3f} / M6 {hf['M6']:.3f} W (x{hf['M7'] / hf['M6']:.2f}); heat M7 "
      f"{hhf['M7']:.3f} / M6 {hhf['M6']:.3f} C")
for m in ("M7", "M6", "M5"):
    z = [abs(IT[t]["D"]["mean"] - T[t][m]["D_w"]) / hw(t, m) for t in COV]
    rp = sc["primary"]["reported"][m]["power_all_nonanchor"]
    cv = sc["primary"]["reported"][m]["coverage_power"]
    print(f"  {m}: 30 non-anchor rms {rp['rms']:.3f} bias {rp['bias']:+.3f} W, inside {cv['inside']} of {cv['n']}, largest "
          f"|error|/half-width {max(z):.2f} (scored.json > primary.reported.{m})")

# ---------------------------------------------------------------- C4
print("\nC4  Kinds-table cells (e141.json > items.<tile>.D and .dT_win: mean, 95% half-width, kept passes)")
print(f"  {'tile':34} {'prio':>4} {'D W':>8} {'+-95%':>6} {'n':>2} {'dT_win C':>9} {'+-95%':>6} {'n':>2}")
for t in sorted(T, key=lambda x: (["fp32", "fp16", "int8"].index(T[x]["type"]), not T[x].get("pool_anchor") is False, x)):
    d, h = IT[t]["D"], IT[t]["dT_win"]
    print(f"  {t:34} {T[t]['priority']:>4} {d['mean']:8.3f} {d['ci95']:6.3f} {d['n']:2d} {h['mean']:9.3f} {h['ci95']:6.3f} {h['n']:2d}"
          f"{'  (anchor)' if T[t].get('pool_anchor') else ''}")

# ---------------------------------------------------------------- C5
print("\nC5  The ettelem binary on aifoundry3 predates the source its sends were classified from")
b = open(os.path.join(HERE, "logs", "binaries.sha256")).read()
m = re.search(r"([0-9a-f]{64})\s+build/ettelem/ettelem", b)
print(f"  binary that ran: build/ettelem/ettelem {m.group(1)[:16]}... (logs/binaries.sha256)")
src = {}
for rev in ("de262730", "efa3e8cd"):
    s = subprocess.run(["git", "-C", ROOT, "show", f"{rev}:tools/ettelem/ettelem.cpp"], capture_output=True, text=True, check=True).stdout
    src[rev] = s
    when = subprocess.run(["git", "-C", ROOT, "log", "-1", "--format=%ad", "--date=short", rev], capture_output=True, text=True).stdout.strip()
    print(f"  tools/ettelem/ettelem.cpp at {rev} ({when}): sha256 {hashlib.sha256(s.encode()).hexdigest()[:16]}...")


def body(s, name):
    mm = re.search(r"^[ \t]*[\w:<>\*&\s]+?\b" + name + r"\s*\([^;{)]*\)\s*(?:const\s*)?\{", s, re.M)
    if not mm:
        return None
    i, depth = mm.end() - 1, 0
    for j in range(i, len(s)):
        depth += {"{": 1, "}": -1}.get(s[j], 0)
        if depth == 0:
            return s[mm.start():j + 1]


for fn in ("config", "sample", "get", "resetStats"):
    a, c = body(src["de262730"], fn), body(src["efa3e8cd"], fn)
    print(f"  {fn}(): byte-identical at the two revisions: {a is not None and a == c}")
print(f"  'temp' subcommand (the later source only; E128's guard refuses it): de262730 {body(src['de262730'], 'temp') is not None}, "
      f"efa3e8cd {body(src['efa3e8cd'], 'temp') is not None}")
fd = open(os.path.join(ROOT, "docs", "findings", "14-card-behaviour.md")).read().splitlines()
ln = [i + 1 for i, x in enumerate(fd) if "On aifoundry3 the `ettelem` that runs is not the reviewed build" in x]
print(f"  docs/findings/14-card-behaviour.md records it at line {ln[0] if ln else '?'} (E132 C1, E134 C6)")

# ---------------------------------------------------------------- C6
print("\nC6  E141-M2 (M7 against M5) by arm")
for name, a in [("primary", sc["primary"])] + [(n, sc["arms"][n]) for n in ("dips_removed", "gates_off", "leak0.1994", "leak0")]:
    x = a["rules"]["E141-M2"]
    if x.get("verdict") == "NOT SCORED":
        print(f"  {name}: NOT SCORED")
        continue
    print(f"  {name}: {x['d_rms_w']:+.3f} W [{x['lo95']:+.3f}, {x['hi95']:+.3f}] {x['verdict']}   (scored.json)")
