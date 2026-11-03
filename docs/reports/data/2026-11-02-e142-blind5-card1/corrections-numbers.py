#!/usr/bin/env python3
"""E142 (desk, after verification, Mon 2 Nov 2026): print the numbers the README's corrections C1-C5 quote, from committed files only,
so each can be traced to a file and a key. Nothing here is a verdict and nothing is refitted: it reads this directory's scored.json and
telemetry-max.json, the registration's predictions-e142.json, E140's scored.json and scored-nodips.json, Q138(m)'s m7.json,
docs/findings/14-card-behaviour.md, two binaries records, and tools/ettelem/ettelem.cpp at each revision since 20 Sep (through git).
Standard library and git only.

    python3 docs/reports/data/2026-11-02-e142-blind5-card1/corrections-numbers.py > docs/reports/data/2026-11-02-e142-blind5-card1/corrections-numbers.txt
SPDX-License-Identifier: Apache-2.0"""
import hashlib
import json
import math
import os
import re
import statistics
import subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
F = ("fp32", "fp16", "int8")
MODELS = ("M7", "M6", "M5")


def load(*parts):
    with open(os.path.join(REPO, *parts)) as fh:
        return json.load(fh)


S = load("docs", "reports", "data", "2026-11-02-e142-blind5-card1", "scored.json")
P = S["primary"]
PRED = load("tools", "claims-v3", "e142", "predictions-e142.json")
TM = load("docs", "reports", "data", "2026-11-02-e142-blind5-card1", "telemetry-max.json")
E140 = {"primary (dips kept)": load("docs", "reports", "data", "2026-11-02-e140-blind4", "scored.json"),
        "dips removed": load("docs", "reports", "data", "2026-11-02-e140-blind4", "scored-nodips.json")}
M7 = load("docs", "reports", "data", "2026-11-02-q138m-model", "m7.json")


def rms(xs):
    return math.sqrt(statistics.mean([x * x for x in xs]))


def halfwidth(row):
    return (row["hi95"] - row["lo95"]) / 2


print("== C1: M7 against M6 (and M5) on the same 30 non-anchor tiles (scored.json > primary.reported, primary.power_rows)")
for m in MODELS:
    r = P["reported"][m]
    a = r["power_all_nonanchor"]
    c = r["coverage_power"]
    print(f"  {m}: power rms {a['rms']:.3f} W, bias {a['bias']:+.4f} W, inside its 95% band {c['inside']} of {c['n']}, outside {c['outside']}")
print("  mean 95% half-width per format, W (power_rows lo95/hi95; equal to predictions-e142.json tiles.*.<model>.D_95):")
hw = {}
for m in MODELS:
    rows = {k: v for k, v in P["power_rows"][m].items() if not v["pool_anchor"]}
    hw[m] = {}
    for fmt in F:
        a = statistics.mean([halfwidth(v) for v in rows.values() if v["type"] == fmt])
        b = statistics.mean([(t[m]["D_95"][1] - t[m]["D_95"][0]) / 2 for t in PRED["tiles"].values()
                             if t["type"] == fmt and not t["pool_anchor"]])
        assert abs(a - b) < 1e-9, (m, fmt, a, b)
        hw[m][fmt] = a
    hw[m]["all"] = statistics.mean([halfwidth(v) for v in rows.values()])
    worst = max(rows, key=lambda k: abs(rows[k]["error"]) / halfwidth(rows[k]))
    print(f"    {m}: fp32 {hw[m]['fp32']:.3f}  fp16 {hw[m]['fp16']:.3f}  int8 {hw[m]['int8']:.3f}  all 30 {hw[m]['all']:.3f};"
          f"  largest |error| / half-width {abs(rows[worst]['error']) / halfwidth(rows[worst]):.3f} ({worst})")
print("  M7's half-width over M6's: " + ", ".join(f"{k} {hw['M7'][k] / hw['M6'][k]:.2f}x (M6 {100 * (1 - hw['M6'][k] / hw['M7'][k]):.0f}% narrower)"
                                             for k in ("fp32", "fp16", "int8", "all")))
print("  heat, priority-1 tiles (the H1-H3 sets) and coverage over 30 (primary.reported.<model>.heat, coverage_heat):")
for m in ("M7", "M6"):
    h = P["reported"][m]["heat"]
    c = P["reported"][m]["coverage_heat"]
    print(f"    {m}: rms " + " / ".join(f"{h[k]['rms']:.3f}" for k in F) + " C, bias " + " / ".join(f"{h[k]['bias']:+.3f}" for k in F)
          + f" C; inside {c['inside']} of {c['n']}, outside {c['outside']}")
print("  E140 (pool 4, aifoundry3 card 0), M6, as committed (scored.json and scored-nodips.json > primary.power):")
for name, s in E140.items():
    p = s["primary"]
    p3 = p["power"]["rules"]["E140-P3"]
    errs = [v["error"] for v in p["power"]["rows"].values()]
    inside = sum(1 for v in p["power"]["rows"].values() if v["inside"])
    print(f"    {name}: passes {p['passes']}, set aside {[x['pass'] for x in p['set_aside']]}, leakage {p['leak']['mode']} "
          f"({p['leak']['k_w_per_c']:.4f} W/C), P3 {p3['verdict']}, inside {inside} of {len(errs)}, mean(measured - M6) {statistics.mean(errs):+.3f} W")
print(f"  E142's primary: passes {P['passes']}, set aside {P['set_aside']}, leakage {P['leak']['mode']} ({P['leak']['k_w_per_c']} W/C), "
      f"reducer {P['reducer']}")

print("\n== C2: the error against the load, M7, priority-1 tiles (the P1-P3 sets; primary.power_rows.M7)")
for fmt in F:
    rows = [v for v in P["power_rows"]["M7"].values() if v["type"] == fmt and v["priority"] == 1 and not v["pool_anchor"]]
    d = [v["measured"] for v in rows]
    e = rms([v["error"] for v in rows])
    rel = rms([v["error"] / v["measured"] for v in rows])
    print(f"  {fmt}: {len(rows)} tiles, measured D {min(d):.2f}-{max(d):.2f} W (mean {statistics.mean(d):.2f}), rms {e:.3f} W = "
          f"{100 * e / statistics.mean(d):.1f}% of the mean D ({100 * e / max(d):.1f}-{100 * e / min(d):.1f}% of the largest and smallest); "
          f"per-tile relative rms {100 * rel:.1f}%")
print("  M7's card-1 scale (m7.json > families.*.card1_scale_by_format): "
      + ", ".join(f"{fam} {k} {v:.4f}" for fam, d in M7["families"].items() if isinstance(d, dict)
                  for k, v in d.get("card1_scale_by_format", {}).items()))

print("\n== C3: the field named pmic (telemetry-max.json per block; docs/findings/14-card-behaviour.md)")
for b, v in TM["blocks"].items():
    print(f"  {b}: pmic_c_max {v['pmic_c_max']}, shire_mean_c_max {v['shire_mean_c_max']}, equal {v['pmic_c_max'] == v['shire_mean_c_max']}, "
          f"hottest_shire_c_max {v['hottest_shire_c_max']}, board_w_max {v['board_w_max']}")
with open(os.path.join(REPO, "docs", "findings", "14-card-behaviour.md")) as fh:
    lines = fh.read().splitlines()
for i, line in enumerate(lines, 1):
    if line.startswith("| `temp_c.pmic` |"):
        print(f"  14-card-behaviour.md:{i}: {line[:150]}...")
    if "card 1 never read above" in line:
        print(f"  14-card-behaviour.md:{i}: ...{line.strip()[:140]}")

print("\n== C4: the ettelem binary that ran against its reviewed source")


def git(*args):
    return subprocess.run(["git", "-C", REPO] + list(args), check=True, capture_output=True, text=True).stdout


with open(os.path.join(HERE, "logs", "binaries.sha256")) as fh:
    for line in fh:
        if line.rstrip().endswith("build/ettelem/ettelem"):
            print(f"  E142 logs/binaries.sha256: {line.split()[0]}  build/ettelem/ettelem")
b28 = load("docs", "reports", "data", "2026-09-28-heat-placement", "raw", "aifoundry1-c1", "hp", "p5501", "binaries.json")
print(f"  28 Sep, aifoundry1 card 1 (2026-09-28-heat-placement/raw/aifoundry1-c1/hp/p5501/binaries.json > ettelem): {b28['ettelem']['sha256']}")
src = git("show", "HEAD:tools/ettelem/ettelem.cpp")
print(f"  tools/ettelem/ettelem.cpp at HEAD: sha256 {hashlib.sha256(src.encode()).hexdigest()}; last changed in "
      + git("log", "-1", "--format=%h %ad", "--date=format:%Y-%m-%d", "--", "tools/ettelem/ettelem.cpp").strip())


def body(text, signature):
    i = text.find(signature)
    if i < 0:
        return None
    j = text.index("{", i)
    depth = 0
    for k in range(j, len(text)):
        depth += {"{": 1, "}": -1}.get(text[k], 0)
        if depth == 0:
            return text[j:k + 1]
    return None


def nocomment(text):
    return "\n".join(line.split("//")[0] for line in text.splitlines())


print("  per revision of tools/ettelem/ettelem.cpp (DM commands requested in sample() and config(); the reset's guard; the default resetMs;"
      " the subcommands main() dispatches):")
for rev in git("log", "--format=%h %ad", "--date=format:%Y-%m-%d", "--reverse", "--", "tools/ettelem/ettelem.cpp").splitlines():
    h, day = rev.split()
    t = git("show", f"{h}:tools/ettelem/ettelem.cpp")
    smp, cfg = body(t, "int sample("), body(t, "int config(")
    smp_c = sorted(set(re.findall(r"DM_CMD_[A-Z_]+", nocomment(smp or ""))))
    cfg_c = sorted(set(re.findall(r"DM_CMD_[A-Z_]+", nocomment(cfg or ""))))
    sl = (smp or "").splitlines()
    calls = [i for i, line in enumerate(sl) if "d.resetStats()" in line]
    guarded = [i for i in calls if any("resetMs > 0" in sl[j] for j in range(max(0, i - 2), i + 1))]
    default0 = bool(re.search(r"resetMs\s*=\s*0", t))
    subs = sorted(set(re.findall(r'cmd == "([a-z]+)"', t)))
    print(f"    {h} {day}: since_reset_ms emitted {'since_reset_ms' in t}; sample {smp_c}; config {cfg_c}; "
          f"statistics-reset calls in sample {len(calls)}, guarded by 'resetMs > 0' {len(guarded)}; resetMs = 0 default {default0}; "
          f"subcommands {subs}")

print("\n== C5: the tiles where M7's terms differ from M6's and M5's (primary.power_rows; error = measured - model, W)")
for tile in ("fp32.wideexp48_bgate_alt", "fp16.wideexp_bgate_alt", "int8.b_line_flipflop_nogate"):
    print(f"  {tile}: " + "; ".join(f"{m} {P['power_rows'][m][tile]['error']:+.3f} (inside {P['power_rows'][m][tile]['inside']}, "
                                    f"half-width {halfwidth(P['power_rows'][m][tile]):.3f})" for m in MODELS))
