#!/usr/bin/env python3
"""E120, corrections after verification (Sun 1 Nov 2026): print, from committed files only, every number that the
README's "Corrections after verification" section quotes and that no earlier file prints.

    python3 docs/reports/data/2026-11-01-e120-rail-redesign/corrections-check.py > corrections-check.txt

Post hoc; it decides nothing and changes no file. Standard library only; it runs from any directory. Section CV3 also
asks git for the GO commit's time; without git it says so and prints the rest.
"""
import datetime
import json
import os
import re
import statistics
import subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
REL = os.path.relpath(HERE, REPO)
DATA = os.path.join(REPO, "docs", "reports", "data")
UNMETERED = os.path.join(DATA, "2026-09-23-energy-manual", "unmetered_fit.json")
E119_README = os.path.join(DATA, "2026-11-01-e119-gemm-speed", "README.md")
E77_README = os.path.join(DATA, "2026-11-01-e77-rail-one-temperature", "README.md")
GO_COMMIT = "c5a221cb"
STEP_W = 21.0  # the rail step B is quoted at


def load(path):
    with open(path) as f:
        return json.load(f)


def text(path):
    with open(path, encoding="utf-8") as f:
        return f.read()


def rel(path):
    return os.path.relpath(path, REPO)


def ls_slope(xs, ys):
    mx, my = statistics.mean(xs), statistics.mean(ys)
    return sum((x - mx) * (y - my) for x, y in zip(xs, ys)) / sum((x - mx) ** 2 for x in xs)


r = load(os.path.join(HERE, "results.json"))
B = r["B"]
COEF, ROW, M0, VA = B["coef_minion"], B["row_pJ"], B["m0_A_w"], B["V_A"]


def pj(w):
    """B's own conversion: pJ = W x 0.875 / (coef x 21)."""
    return w * ROW / (COEF * STEP_W)


def total_current_w(r_ohm):
    """B's total-current form at arm A's measured idle rail m0 and voltage V_A."""
    return r_ohm * (((M0 + STEP_W) / VA) ** 2 - (M0 / VA) ** 2)


print(f"E120 corrections after verification (Sun 1 Nov 2026): numbers from committed files, data {REL}")
print()

# ---------------------------------------------------------------------------------------------------------------- CV1
print("CV1 The bound against the row: the off-rail that grows with the minion rail, as this design measured it")
u = load(UNMETERED)["aifoundry2"]
print(f"  the row's coefficient ({rel(UNMETERED)} aifoundry2): minion {u['coef']['minion']:.5f} W/W "
      f"(s.e. {u['se']['minion']:.4f}), n {u['n']}, fitted on each configuration's mean unmetered watts over idle "
      f"(uncorrected deltas; tools/ettelem/fit_unmetered.py)")
print(f"  results.json B: coef {COEF:.5f} x {STEP_W:.0f} W = {COEF * STEP_W:.3f} W = {pj(COEF * STEP_W):.3f} pJ (the row); "
      f"m0_A {M0:.4f} W, V_A {VA} V")
print(f"  registered upper edge: R {B['at_ci_high']['R_mohm']:.4f} mOhm -> {B['at_ci_high']['total_current_w']:.3f} W = "
      f"{B['at_ci_high']['total_current_pJ']:.4f} pJ; at the mean R {B['at_mean']['R_mohm']:.4f} mOhm -> "
      f"{B['at_mean']['total_current_w']:.3f} W = {B['at_mean']['total_current_pJ']:.4f} pJ; verdict {B['B_verdict']}")
slopes = {}
for foot in ("drift_split", "uncorrected", "board_only"):
    rm = r["footings"][foot]["rung_means"]
    print(f"  footing {foot}{' (central)' if foot == 'drift_split' else ''}:")
    for arm in "AB":
        by_rung = {}
        for key, v in rm.items():
            if key[0] == arm:
                by_rung.setdefault(key.split("-")[1], []).append(v)
        rungs = sorted(by_rung, key=lambda g: statistics.mean(x["minion"] for x in by_rung[g]))
        cells = []
        for g in rungs:
            vs = by_rung[g]
            cells.append(f"{g} minion {statistics.mean(x['minion'] for x in vs):.2f} W, off-rail "
                         f"{statistics.mean(x['offrail'] for x in vs):.3f} W ({min(x['offrail'] for x in vs):.2f} to "
                         f"{max(x['offrail'] for x in vs):.2f} per pass)")
        lo, hi = rungs[0], rungs[-1]
        mlo = statistics.mean(x["minion"] for x in by_rung[lo]); olo = statistics.mean(x["offrail"] for x in by_rung[lo])
        mhi = statistics.mean(x["minion"] for x in by_rung[hi]); ohi = statistics.mean(x["offrail"] for x in by_rung[hi])
        end_slope = (ohi - olo) / (mhi - mlo)
        per_pass = []
        for p in range(1, 6):
            pts = [(v["minion"], v["offrail"]) for key, v in rm.items() if key.startswith(f"{arm}{p}-")]
            per_pass.append(ls_slope([a for a, _ in pts], [b for _, b in pts]))
        slopes[(foot, arm)] = end_slope
        print(f"    arm {arm}: " + "; ".join(cells))
        print(f"    arm {arm}: slope top rung over bottom rung {end_slope:.4f} W per minion W -> x {STEP_W:.0f} W = "
              f"{end_slope * STEP_W:.2f} W = {pj(end_slope * STEP_W):.3f} pJ; per-pass least-squares slope mean "
              f"{statistics.mean(per_pass):.4f} ({min(per_pass):.4f} to {max(per_pass):.4f})")
c = slopes[("drift_split", "A")], slopes[("drift_split", "B")]
print(f"  central footing: {c[0]:.3f} to {c[1]:.3f} W per minion W = {pj(c[0] * STEP_W):.2f} to {pj(c[1] * STEP_W):.2f} pJ, "
      f"{c[0] / COEF:.0%} to {c[1] / COEF:.0%} of the row's {COEF:.3f}; uncorrected footing "
      f"{slopes[('uncorrected', 'A')]:.3f} / {slopes[('uncorrected', 'B')]:.3f} W per minion W")
print(f"  the conduction point estimate ({B['at_mean']['total_current_pJ']:.3f} pJ) over the central in-step off-rail: "
      f"{B['at_mean']['total_current_pJ'] / pj(c[1] * STEP_W):.0%} to {B['at_mean']['total_current_pJ'] / pj(c[0] * STEP_W):.0%}")
print("  if ALL of arm A's top-rung off-rail (central footing) were conduction (total-current form, each launch's own "
      "m0, V0 and window V):")
rm = r["footings"]["drift_split"]["rung_means"]
all_r = []
for p in range(1, 6):
    top = max((v for key, v in rm.items() if key.startswith(f"A{p}-")), key=lambda v: v["minion"])
    reg = ((top["m0"] + top["minion"]) / top["V"]) ** 2 - (top["m0"] / top["V0"]) ** 2
    rr = top["offrail"] / reg
    all_r.append(rr)
    print(f"    pass {p}: off-rail {top['offrail']:.3f} W at minion {top['minion']:.2f} W, regressor {reg:.0f} A^2 -> "
          f"R {rr * 1e3:.3f} mOhm -> at B's {STEP_W:.0f} W step {total_current_w(rr):.2f} W = {pj(total_current_w(rr)):.3f} pJ")
print(f"    range R {min(all_r) * 1e3:.2f} to {max(all_r) * 1e3:.2f} mOhm = {pj(total_current_w(min(all_r))):.2f} to "
      f"{pj(total_current_w(max(all_r))):.2f} pJ, against the registered upper edge "
      f"{B['at_ci_high']['R_mohm']:.2f} mOhm = {B['at_ci_high']['total_current_pJ']:.2f} pJ")
fit = r["footings"]["drift_split"]["fit"]
am = [fit["per_pass"][k]["a_m"] for k in sorted(fit["per_pass"])]
cb = [fit["per_pass"][k]["c_B_w"] for k in sorted(fit["per_pass"])]
rp = [fit["per_pass"][k]["R_eff_ohm"] * 1e3 for k in sorted(fit["per_pass"])]
print(f"  the registered offset fit per pass: R " + " / ".join(f"{x:.3f}" for x in rp) + " mOhm; a_m "
      + " / ".join(f"{x:+.3f}" for x in am) + f" (mean {statistics.mean(am):+.3f}); c_B " + " / ".join(f"{x:.2f}" for x in cb) + " W")
print()

# ---------------------------------------------------------------------------------------------------------------- CV2
print("CV2 E119's residency read")
e119 = text(E119_README)
for needle in ("**No residency was read.**", "All 68 residency queries returned rc 2", "takes raw states 2-6 only"):
    print(f"  {rel(E119_README)} contains {needle!r}: {needle in e119}")
e77 = text(E77_README)
needle = "raw 3 read 0 at all 11 reads"
print(f"  {rel(E77_README)} (its F1) contains {needle!r}: {needle in e77}")
gates = load(os.path.join(HERE, "raw", "gates.json"))
print(f"  E120 raw/gates.json residency: {gates['residency']!r}")
qrc = {}
with open(os.path.join(HERE, "raw", "queries.jsonl")) as f:
    for line in f:
        q = json.loads(line)
        qrc.setdefault((q.get("residency_rc"), json.dumps(q.get("residency"))), []).append(q["tag"])
for (rc, res), tags in qrc.items():
    print(f"  E120 raw/queries.jsonl: {len(tags)} queries with residency_rc {rc} and residency {res} ({', '.join(tags)})")
print()

# ---------------------------------------------------------------------------------------------------------------- CV3
print("CV3 Amendment A1's time")
try:
    out = subprocess.run(["git", "-C", REPO, "show", "-s", "--format=%h %ci", GO_COMMIT], capture_output=True,
                         text=True, timeout=20)
    print(f"  git: the GO commit holding A1: {out.stdout.strip() or 'not found: ' + out.stderr.strip()}")
except (OSError, subprocess.SubprocessError) as e:
    print(f"  git unavailable ({type(e).__name__}); the GO commit is {GO_COMMIT}")
with open(os.path.join(HERE, "raw", "gov.jsonl")) as f:
    sets = [json.loads(line) for line in f]
first_set = next(e for e in sets if e.get("event") == "set")
print(f"  raw/gov.jsonl first set: TDP {first_set['asked']['tdp_w']} W sent at {first_set['sent'][0]['t_iso']} "
      f"(rc {first_set['sent'][0]['rc']}), read back at {first_set['readback_iso']}")
with open(os.path.join(HERE, "raw", "queries.jsonl")) as f:
    first_pass = next(q for q in map(json.loads, f) if q["tag"] != "start")
print(f"  raw/queries.jsonl first end-of-pass query: {first_pass['tag']} at {first_pass['t_iso']}")
print()

# ---------------------------------------------------------------------------------------------------------------- CV4
print("CV4 The post hoc upper edge against the registered one")
for line in text(os.path.join(HERE, "posthoc.txt")).splitlines():
    m = re.search(r"upper edge ([\d.]+) W = ([\d.]+) pJ", line)
    if m:
        print(f"  {line.split(':')[0][:60]:60s} upper edge {m.group(1)} W = {m.group(2)} pJ")
print()

# ---------------------------------------------------------------------------------------------------------------- CV5
print("CV5 The kernel-event window")
kl = text(os.path.join(HERE, "raw", "logs", "kernlog-after.txt")).splitlines()
cap = datetime.datetime.strptime(kl[0].replace(" PST", ""), "%Y-%m-%d %H:%M:%S")
up = float(kl[1].split()[0])
evs = []
for line in kl:
    m = re.match(r"\[\s*(\d+\.\d+)\]\s.*Error Event Detected", line)
    if m:
        evs.append(cap - datetime.timedelta(seconds=up - float(m.group(1))))
end = load(os.path.join(HERE, "raw", "end.json"))["t_end_iso"]
end_t = datetime.datetime.strptime(end[:19], "%Y-%m-%dT%H:%M:%S")
w0 = cap.replace(hour=20, minute=48, second=55)
inwin = [t for t in evs if w0 <= t <= cap]
print(f"  raw/logs/kernlog-after.txt read at {kl[0]} (uptime {up:.2f} s); the session ended {end} "
      f"(raw/end.json), {(cap - end_t).total_seconds():.0f} s before the read")
last = max(evs)
print(f"  ET 'Error Event Detected' lines in the buffer: {len(evs)}; from {w0:%H:%M:%S} to {cap:%H:%M:%S} PST: {len(inwin)}; "
      f"the last at {last:%Y-%m-%d %H:%M:%S}.{last.microsecond // 100000} PST, plus up to 1 s (the read's header "
      f"clock is to the second)")
print(f"  raw/kernel-events.txt header: {text(os.path.join(HERE, 'raw', 'kernel-events.txt')).splitlines()[0]}")
print()

# ---------------------------------------------------------------------------------------------------------------- CV6
print("CV6 The change record")
cr = text(os.path.join(HERE, "CHANGE-RECORD.md"))
print(f"  CHANGE-RECORD.md placeholders left ('⟨RUN'): {cr.count(chr(0x27E8) + 'RUN')}")
for field in ("Card asset, serial, board revision, form factor, DRAM capacity",
              "PMIC bootloader, protocol and watchdog assumptions",
              "Exact qualified reset source"):
    print(f"  CHANGE-RECORD.md addresses the template field {field!r}: {field in cr}")
