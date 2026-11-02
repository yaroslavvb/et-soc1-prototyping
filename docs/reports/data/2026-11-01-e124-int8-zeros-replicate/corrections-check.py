#!/usr/bin/env python3
"""E124, corrections after verification (Sun 1 Nov 2026): print, from committed files only, every number that the
README's "Corrections after verification" section and E124.md's dated note quote and that no earlier file prints.

    python3 docs/reports/data/2026-11-01-e124-int8-zeros-replicate/corrections-check.py > corrections-check.txt

Post hoc; it decides nothing and changes no file. Standard library only; it runs from any directory. Intervals are 95%
t-intervals over passes (t at n - 1 degrees of freedom), as the scorer's. Section C3 also asks git for the freeze
commit's time and contents; without git it says so and prints the rest.
"""
import json
import math
import os
import re
import statistics
import subprocess
import time

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
DATA = os.path.join(REPO, "docs", "reports", "data")
REL = os.path.relpath(HERE, REPO)
T95 = {1: 12.706204736174698, 2: 4.302652729749464, 3: 3.182446305284263, 4: 2.7764451051977934}
PST = -8 * 3600  # Sun 1 Nov 2026 after 02:00: PST


def load(*parts):
    with open(os.path.join(*parts)) as f:
        return json.load(f)


def text(*parts):
    with open(os.path.join(*parts)) as f:
        return f.read()


def ci(xs):
    n = len(xs)
    m = statistics.mean(xs)
    return m, T95[n - 1] * statistics.stdev(xs) / math.sqrt(n)


def hms(epoch):
    return time.strftime("%H:%M:%S", time.gmtime(epoch + PST))


def pm(m, h, nd=3):
    return f"{m:+.{nd}f} ± {h:.{nd}f}"


def overlap(a, b):
    return (a["mean"] - a["ci95"]) <= (b["mean"] + b["ci95"]) and (b["mean"] - b["ci95"]) <= (a["mean"] + a["ci95"])


print("E124 corrections-check (post hoc, deciding nothing). Paths are relative to the repository's top level.")
print()

# ---------------------------------------------------------------------------------------------------------------
print("C1  S over idle across sessions on aifoundry1 card 1 (levels over idle carry a session offset; differences cancel it)")
sessions = [
    ("E124 primary (dips removed, 0.2414)", os.path.join(REL, "e124.json")),
    ("E124 dips-kept arm (2 passes)", os.path.join(REL, "e124-dipskept.json")),
    ("E82 (dips kept, auto 0.2414)", "docs/reports/data/2026-10-31-e82-kinds-aifoundry1/e82.json"),
    ("E93 (dips removed, 0.2414)", "docs/reports/data/2026-11-01-e93-zero-gate-silicon/e93.json"),
]
red = {name: load(REPO, path) for name, path in sessions}
items = ["fp32.zeros", "fp16.zeros", "int8.zeros", "anchor_pi"]
for name, path in sessions:
    d = red[name]
    print(f"  {name}: {path}")
    print(f"      passes {d['passes']}; idle {d['idle_level']['mean']:.3f} W; leak {d['leak']['k_w_per_c']:.4f} W/C ({d['leak']['mode']})")
    print("      S: " + "; ".join(f"{k} {pm(d['items'][k]['S']['mean'], d['items'][k]['S']['ci95'])}" for k in items))
    print(f"      D(anchor_pi) {pm(d['items']['anchor_pi']['D']['mean'], d['items']['anchor_pi']['D']['ci95'])};"
          f" G = S(int8.zeros) - S(fp32.zeros) {d['items']['int8.zeros']['S']['mean'] - d['items']['fp32.zeros']['S']['mean']:+.3f}")
e124 = red[sessions[0][0]]
diffs = []
for ref in (sessions[2][0], sessions[3][0]):
    r = red[ref]
    row = []
    for k in items:
        dd = e124["items"][k]["S"]["mean"] - r["items"][k]["S"]["mean"]
        diffs.append(dd)
        row.append(f"{k} {dd:+.3f} (95% intervals overlap: {overlap(e124['items'][k]['S'], r['items'][k]['S'])})")
    print(f"  E124 primary minus {ref.split(' ')[0]}: " + "; ".join(row))
print(f"  E124's S runs {-max(diffs):.3f} to {-min(diffs):.3f} W below E82's and E93's over these four items")
alls, alld = [], []
for ref in (sessions[2][0], sessions[3][0]):
    r = red[ref]
    shared = [k for k in e124["items"] if k in r["items"]]
    for k in shared:
        ds = e124["items"][k]["S"]["mean"] - r["items"][k]["S"]["mean"]
        dd = e124["items"][k]["D"]["mean"] - r["items"][k]["D"]["mean"]
        alls.append(ds)
        alld.append(dd)
        print(f"      E124 minus {ref.split(' ')[0]}, {k}: S {ds:+.3f}, D {dd:+.3f}")
print(f"  over all {len(alls)} shared cells: S {min(alls):+.3f} to {max(alls):+.3f} W (every one below: {max(alls) < 0});"
      f" D {min(alld):+.3f} to {max(alld):+.3f} W")
for ref in (sessions[2][0], sessions[3][0]):
    r = red[ref]
    print(f"  D(anchor_pi), E124 minus {ref.split(' ')[0]}: {e124['items']['anchor_pi']['D']['mean'] - r['items']['anchor_pi']['D']['mean']:+.3f} W"
          f" (the tie R10 reads on D: scored.json › rules.R10_tie)")
auto = load(REPO, REL, "e124-auto.json")
e109 = load(REPO, "docs/reports/data/2026-11-01-e109-int8-zeros/e109-3pass.json")
ph = load(REPO, "docs/reports/data/2026-11-01-e109-int8-zeros/posthoc.json")["three_passes_gate_lifted"]
ex = load(REPO, REL, "extras.json")
print(f"  S(m0.fp32.zeros): E124 primary {pm(e124['items']['m0.fp32.zeros']['S']['mean'], e124['items']['m0.fp32.zeros']['S']['ci95'])};"
      f" leakage-auto arm ({auto['leak']['k_w_per_c']:.3f} W/C, e124-auto.json) {pm(auto['items']['m0.fp32.zeros']['S']['mean'], auto['items']['m0.fp32.zeros']['S']['ci95'])};"
      f" E109 three passes (leak {e109['leak']['k_w_per_c']:.3f}, e109-3pass.json) {pm(e109['items']['m0.fp32.zeros']['S']['mean'], e109['items']['m0.fp32.zeros']['S']['ci95'])}")
print(f"  S(m0.int8.zeros): E124 primary {pm(e124['items']['m0.int8.zeros']['S']['mean'], e124['items']['m0.int8.zeros']['S']['ci95'])};"
      f" leakage-auto arm {pm(auto['items']['m0.int8.zeros']['S']['mean'], auto['items']['m0.int8.zeros']['S']['ci95'])};"
      f" E109 three passes {pm(e109['items']['m0.int8.zeros']['S']['mean'], e109['items']['m0.int8.zeros']['S']['ci95'])}")
for k in ("fp32.zeros", "int8.zeros"):
    a, b = e124["items"][k]["S"], e109["items"][k]["S"]
    print(f"  S({k}): E124 {pm(a['mean'], a['ci95'])}; E109 three passes {pm(b['mean'], b['ci95'])}; overlap {overlap(a, b)}"
          f" (not among extras.json › beside_e109's twenty)")
b = ex["beside_e109"]
print(f"  read ceilings (from S(m0) levels): fp32 E124 {pm(b['read_ceiling_fp32_pj']['e124']['mean'], b['read_ceiling_fp32_pj']['e124']['half'], 2)} pJ,"
      f" E109 {pm(b['read_ceiling_fp32_pj']['e109']['mean'], b['read_ceiling_fp32_pj']['e109']['half'], 2)} pJ;"
      f" int8 E124 {pm(b['read_ceiling_int8_pj']['e124']['mean'], b['read_ceiling_int8_pj']['e124']['half'], 2)} pJ,"
      f" E109 {pm(b['read_ceiling_int8_pj']['e109']['mean'], b['read_ceiling_int8_pj']['e109']['half'], 2)} pJ")
r = ex["reported"]
print(f"  int8's extra reads at fp32's ceiling: E124 {pm(r['extra_reads_at_fp32_ceiling_w']['mean'], r['extra_reads_at_fp32_ceiling_w']['half'])} W"
      f" against N {pm(ex['added_rules']['Y1']['N']['mean'], ex['added_rules']['Y1']['N']['half'])};"
      f" E109 (posthoc.json) {pm(ph['extra_reads_at_fp32_ceiling_w']['mean'], ph['extra_reads_at_fp32_ceiling_w']['half'])} W"
      f" against N {pm(ph['S_m0_gap']['mean'], ph['S_m0_gap']['half'])}")
print()

# ---------------------------------------------------------------------------------------------------------------
print("C2  A1's arithmetic (logs/anchor-t0.txt, logs/claim-save-time.txt, logs/release-save-time.txt, logs/queue.out)")
t0 = int(text(HERE, "logs", "anchor-t0.txt").split()[0])
claim = int(text(HERE, "logs", "claim-save-time.txt").split()[0])
release = int(text(HERE, "logs", "release-save-time.txt").split()[0])
q = text(HERE, "logs", "queue.out")
budget, reserve = 1800, 150
print(f"  claim saved {hms(claim)} PST ({claim}); relaunch anchor T0 {hms(t0)} PST ({t0}): the failed launch cost {t0 - claim} s"
      f" = {(t0 - claim) // 60} min {(t0 - claim) % 60} s")
print(f"  limit for a pass's projected end: A1 (T0) {hms(t0 + budget - reserve)} PST; the frozen claim anchor {hms(claim + budget - reserve)} PST")
for m in re.finditer(r"^(\d\d:\d\d:\d\d) (p\d+) starts at T0\+(\d+) s \(projected (\d+) s\)", q, re.M):
    start = t0 + int(m.group(3))
    end = start + int(m.group(4))
    margin = claim + budget - reserve - end
    verdict = "would start" if margin >= 0 else f"would be REFUSED by {-margin} s"
    print(f"  {m.group(2)} starts {hms(start)}, projected end {hms(end)}: under the claim anchor it {verdict}")
for m in re.finditer(r"^(\d\d:\d\d:\d\d) (p\d+) rc=(\d+) \((\d+) s\)", q, re.M):
    print(f"  {m.group(2)} ended {m.group(1)} PST after {m.group(4)} s (rc {m.group(3)})")
cs = text(HERE, "logs", "config-session-start.json.time").strip()
ce = text(HERE, "logs", "config-session-end.json.time").strip()
print(f"  session config reads {cs} and {ce}")
print(f"  release saved {hms(release)} PST ({release}); claim to release {release - claim} s = {(release - claim) / 60:.2f} min"
      f" ({'inside' if release - claim <= budget else 'OUTSIDE'} the frozen 30 card-minutes from the claim to the release)")
print()

# ---------------------------------------------------------------------------------------------------------------
print("C3  the desk finding's time (tools/claims-v3/e124/selftest.txt D; the freeze commit)")
st = text(REPO, "tools", "claims-v3", "e124", "selftest.txt")
for line in st.splitlines():
    if line.startswith("PASS D") or line.strip().startswith("D's verdicts"):
        print("  " + line.strip()[:400])
try:
    out = subprocess.run(["git", "-C", REPO, "show", "-s", "--format=%h %ad", "--date=format:%Y-%m-%d %H:%M:%S %z", "47995958"],
                         capture_output=True, text=True, check=True).stdout.strip()
    frozen = subprocess.run(["git", "-C", REPO, "show", "47995958:tools/claims-v3/e124/selftest.txt"],
                            capture_output=True, text=True, check=True).stdout
    print(f"  freeze commit {out}; selftest.txt there has PASS D: {'PASS D pipeline on E109' in frozen}")
    e124md = subprocess.run(["git", "-C", REPO, "show", "5ca4f13e:tools/claims-v3/e124/E124.md"],
                            capture_output=True, text=True, check=True).stdout
    import hashlib
    print(f"  E124.md at 5ca4f13e (A1): sha256 {hashlib.sha256(e124md.encode()).hexdigest()}"
          f" (each pass's code.sha256 and {REL}/code.sha256 record this one)")
except Exception as err:  # git absent or not a clone
    print(f"  git not available here ({type(err).__name__}); the freeze is 47995958, 19:18:17 PST")
print("  The self-test's run times (19:15:46 PST, its output read at 19:16:04; the re-run that wrote selftest.txt 19:16:20-19:16:24)"
      " are from the lane's session record, which is not committed.")
print()

# ---------------------------------------------------------------------------------------------------------------
print("C4  dips removed per pass, the dips-kept arm, the per-pass outlier (e124.json, e124-dipskept.json, scored.json)")
dips = e124["reducer"]["dip_samples_removed"]
print("  dip samples removed: " + ", ".join(f"{k} {v['samples_removed']}" for k, v in sorted(dips.items())))
dk = load(REPO, REL, "e124-dipskept.json")
print(f"  dips-kept arm keeps {dk['passes']}; sets aside " + "; ".join(f"{s['pass']} ({', '.join(s['why'])})" for s in dk["passes_set_aside"]))
sc = load(REPO, REL, "scored.json")
for k in ("G_op", "G_rest"):
    pp = sc["gap"][k]["per_pass"]
    print(f"  {k} per pass {sc['passes']}: " + ", ".join(f"{x:+.3f}" for x in pp))
print()

# ---------------------------------------------------------------------------------------------------------------
print("C5  item 15's live step over pi: reported (R9), no verdict (e124.json › per_pass, scored.json, extras.json)")
passes = [str(p) for p in e124["passes"]]
step = [e124["per_pass"][p]["fp32.a_nz_b_randn"]["D"] - e124["per_pass"][p]["anchor_pi"]["D"] for p in passes]
m, h = ci(step)
print("  D(fp32.a_nz_b_randn) - D(anchor_pi) per pass: " + ", ".join(f"{x:+.3f}" for x in step) + f"; paired {pm(m, h)} W")
tm = sc["item15"]["T_minus"]
lc = ex["reported"]["live_over_constant_w"]
print(f"  T- {pm(tm['mean'], tm['half'])} W; inside the live lanes (extras.json › reported.live_over_constant_w) {pm(lc['mean'], lc['half'])} W")
r9 = sc["rules"]["R9_live_split"]
print(f"  scored.json › rules.R9_live_split keys {sorted(r9)}; a verdict key: {'verdict' in r9}")
for line in text(REPO, "tools", "claims-v3", "e109", "E109.md").splitlines():
    if line.startswith("| **R9**"):
        print("  E109.md: " + line.strip())
for line in text(REPO, "tools", "claims-v3", "e124", "E124.md").splitlines():
    if line.startswith("Reported with no verdict"):
        print("  E124.md: " + line.strip()[:260])
print()

# ---------------------------------------------------------------------------------------------------------------
print("C6  wording (scored.json › rules.R6_cycles, extras.json › added_rules.Y2, tools/claims-v3/e124/reduce_e124.py)")
r6 = sc["rules"]["R6_cycles"]
shapes = sorted({k.split(".")[0] + "." + k.split(".")[1] for k in r6})
print(f"  R6 entries {len(r6)}: {sorted(r6)}")
print(f"  distinct arm x format shapes {len(shapes)}: {shapes} (the two item-15 tiles run m0.fp32's shape, "
      f"{r6['m0.fp32.a_zeros_b_randn']['predicted']:.0f} and {r6['m0.fp32.a_nz_b_randn']['predicted']:.0f} cycles predicted)")
y2 = ex["added_rules"]["Y2"]["e_op_pj"]
print(f"  Y2 95% upper bounds: fp32 {y2['fp32']['hi']:.1f} pJ, int8 {y2['int8']['hi']:.1f} pJ (line {ex['added_rules']['Y2']['line_pj']:.1f} pJ)")
src = text(REPO, "tools", "claims-v3", "e124", "reduce_e124.py")
mm = re.search(r"^DIP_W = ([0-9.]+)", src, re.M)
print(f"  reduce_e124.py DIP_W = {mm.group(1) if mm else '?'}: sample i dropped when board_w[i] < min(board_w[i-2], board_w[i+2]) - DIP_W")
