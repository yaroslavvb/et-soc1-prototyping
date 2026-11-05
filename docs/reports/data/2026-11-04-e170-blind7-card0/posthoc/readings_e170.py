#!/usr/bin/env python3
"""E170, post hoc readings at the desk (Wed 4 Nov 2026, after the registered score; never a verdict, nothing rescored).

1. The SP trace ring (E170.md § The stops: dumped after every run with `ettelem sptrace`, a read, "and read at the desk for
   Pmic_Controller_Handle_Pmic_Error_Event lines"), decoded with the lab's tools/claims-v3/hpl/sptrace_full.py as E84's post hoc
   PMIC reading uses it: per session, the new ring entries across its dumps (start.bin, each run's, end.bin), the PMIC over-power
   alarm lines ("power = <P> mW, alarm set point = <S> mW"), entries naming the PMIC, power-status records in throttle state 3
   (POWER_SAFE), and the clock points the ring set. The ring keeps only its last entries, so each dump covers the end of its run.
2. Card 0's 6 s burst die rise per board W over the frozen burst heat law's 21.5 W knee, against the law's 0.1400 C/W
   (m9_a2.json > burst_heat), from results.json (the registered scorer's per-tile cells).

    python3 -B docs/reports/data/2026-11-04-e170-blind7-card0/posthoc/readings_e170.py > .../posthoc/readings_e170.txt
Standard library only. SPDX-License-Identifier: Apache-2.0
"""
import collections
import json
import os
import re
import statistics as st
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
DD = os.path.dirname(HERE)
TOP = os.path.abspath(os.path.join(DD, "..", "..", "..", ".."))
sys.dont_write_bytecode = True
sys.path.insert(0, os.path.join(TOP, "tools", "claims-v3", "hpl"))
import sptrace_full as spf  # noqa: E402

ALARM = re.compile(r"power = (\d+) mW, alarm set point = (\d+) mW")
print("1. The SP trace ring, per session (aifoundry1-c0/<session>/sp/)")
for sess in ("stoptest-die", "stoptest-board", "smoke", "s1"):
    d = os.path.join(DD, "aifoundry1-c0", sess, "sp")
    if not os.path.isdir(d):
        continue
    runs = sorted(f for f in os.listdir(d) if f.endswith(".bin") and f not in ("start.bin", "end.bin"))
    order = (["start.bin"] if os.path.exists(os.path.join(d, "start.bin")) else []) + runs + \
            (["end.bin"] if os.path.exists(os.path.join(d, "end.bin")) else [])
    prev, n_new, alarms, safes, ops, kinds, pmic = [], 0, [], 0, collections.Counter(), collections.Counter(), 0
    for f in order:
        cur = spf.scan(open(os.path.join(d, f), "rb").read()) or []
        new = spf.since(prev, cur) if prev else cur
        prev = cur
        n_new += len(new)
        for e in new:
            kinds[e["kind"]] += 1
            t = e.get("text") or ""
            if "Pmic" in t or "PMIC" in t:
                pmic += 1
            m = ALARM.search(t) if e["kind"] == "other" else None
            if m:
                alarms.append((f, int(m.group(1)), int(m.group(2))))
            if e["kind"] == "pstat" and e.get("throttle_state") == 3:
                safes += 1
            if e["kind"] == "new_op":
                ops[e.get("mhz")] += 1
    print(f"  {sess}: dumps {len(order)}; new ring entries {n_new} by kind {dict(kinds)}; PMIC over-power alarm lines {len(alarms)}"
          f"{' ' + str(alarms[:5]) if alarms else ''}; entries naming the PMIC {pmic}; POWER_SAFE (throttle state 3) records {safes}; "
          f"clock points set {dict(sorted(ops.items(), key=lambda kv: str(kv[0])))}")

print("2. The 6 s burst die rise per board W over 21.5 W (results.json > score.reported.tiles)")
r = json.load(open(os.path.join(DD, "results.json")))
rows = [(n, t["burst_w"], t["rise_c"], t["primary"]["burst_die_rise_c"]) for n, t in r["score"]["reported"]["tiles"].items()]
num = sum(rise * (w - 21.5) for _, w, rise, _ in rows)
den = sum((w - 21.5) ** 2 for _, w, _, _ in rows)
err = [rise - pr for _, _, rise, pr in rows]
print(f"  tiles {len(rows)}: median rise / (board - 21.5 W) {st.median(rise / (w - 21.5) for _, w, rise, _ in rows if w > 25):.4f} C/W; "
      f"least squares through the knee {num / den:.4f} C/W; the frozen law 0.1400 C/W; measured - predicted rise mean "
      f"{st.mean(err):+.3f} C, rms {(sum(e * e for e in err) / len(err)) ** 0.5:.3f} C")

print("3. Runs whose burst clock (burst_mhz: 1.5 s after the first launch to the end of the work) read under 795 MHz (results.json > run_rows)")
rr = r["run_rows"]
low = [(x["run"], x["burst_mhz"]) for x in rr if x.get("burst_mhz") is not None and x["burst_mhz"] < 795]
print(f"  {len(low)} of {len(rr)} runs: " + "; ".join(f"{n} {m} MHz" for n, m in low))

print("4. Each run's highest board sample against its tile's card-0 admission estimate (predictions-e170.json > tiles.<name>.est_card0_peak_w)")
P = json.load(open(os.path.join(TOP, "tools", "claims-v3", "e170", "predictions-e170.json")))
est = {t["label"]: (n, t["est_card0_peak_w"], t.get("aim")) for n, t in P["tiles"].items()}
over = []
for x in rr:
    n, e, aim = est[x["label"]]
    if x.get("peak_w") is not None and x["peak_w"] > e:
        over.append((x["run"], n, aim, x["peak_w"], e, x["peak_w"] - e))
print(f"  {len(over)} of {len(rr)} runs peaked over their estimate, by {min(o[5] for o in over):+.2f} to {max(o[5] for o in over):+.2f} W; "
      f"their tiles' aims {dict(collections.Counter(o[2] for o in over))}; the highest sample {max(x['peak_w'] for x in rr):.2f} W")
for o in sorted(over, key=lambda o: -o[5])[:5]:
    print(f"    {o[1]}: {o[3]:.2f} W against {o[4]:.2f} ({o[5]:+.2f}), {o[0]}")

print("5. E170-X0's ratio with the zeros level referred to each tile's own die starts (X0's tiles: non-anchor, M9's burst D >= 5 W)")
tl = r["score"]["reported"]["tiles"]
xn = [n for n, x in tl.items() if not P["tiles"][n]["anchor"] and x["primary"]["a2_burst_D_w"] >= 5.0 and x.get("D_w") is not None]
reg = [tl[n]["D_w"] / tl[n]["primary"]["a2_burst_D_w"] for n in xn]
ref = [(tl[n]["burst_w"] - tl[n]["primary"]["zeros_level_w"]) / tl[n]["primary"]["a2_burst_D_w"] for n in xn]
zl = {}
for x in rr:
    nm = est[x["label"]][0]
    if nm.endswith("anchor7_zeros"):
        zl[(nm.split(".")[0], x["pass"])] = x["die_start"]
off = [x["die_start"] - zl[(est[x["label"]][0].split(".")[0], x["pass"])] for x in rr if est[x["label"]][0] in xn]
print(f"  n {len(xn)}: median D_w / M9 burst D {st.median(reg):.4f} (X0 as registered: the tile less its pass's zeros anchor); median "
      f"(board - the card's zeros level at the tile's own die starts) / M9 burst D {st.median(ref):.4f}; kappa0 0.9463")
print(f"  die start of these tiles' runs less their pass's zeros anchor of the format: mean {st.mean(off):+.2f} C over {len(off)} runs "
      f"(x kT 0.3954 W/C = {0.3954 * st.mean(off):+.2f} W)")
