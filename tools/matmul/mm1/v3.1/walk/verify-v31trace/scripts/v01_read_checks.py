#!/usr/bin/env python3
"""verify-v31trace (Q217) v01: read v31-trace's check.json files (read only) and print what each says about the logged harts,
the off-mask harts, the stray harts and the minimum log set of criterion (a). /usr/bin/python3 3.12.3, standard library."""
import glob
import json
import os
import sys

RUNS = "<W>/out/v31-trace/traces/runs"
out = {}
for d in sorted(glob.glob(os.path.join(RUNS, "t*"))):
    c = json.load(open(os.path.join(d, "check.json")))
    name = os.path.basename(d)
    ph = c["per_hart"]
    sel = c["summary_meta"]["log_sel"]
    mask = int(c["mask"], 16)
    act = [s for s in range(32) if (mask >> s) & 1]
    # selection per shire
    selp = {}
    for x in sel:
        s, m = x.split(",")
        selp[int(s)] = bin(int(m, 16)).count("1")
    offmask = {h: r for h, r in ph.items() if r["shire"] not in act}
    hart1 = [r for r in ph.values() if r["shire"] in act and r["thread"] == 1]
    work = [r for r in ph.values() if r.get("expect") == "the walk's events"]
    full_active = all(selp.get(s, 0) == 64 for s in act)
    full_inactive = [s for s, n in selp.items() if s not in act and n == 64]
    rec = {
        "verdict": c["verdict"], "mask": c["mask"], "active_shires": act, "harts_selected_per_shire": selp,
        "selected_harts": c["selected_harts"], "selected_missing_from_log": c["selected_harts_missing_from_log"],
        "per_hart_entries": len(ph), "working_traced": len(work), "exact": c["exact_harts"],
        "hart1_logged": len(hart1), "hart1_ok": sum(1 for r in hart1 if r["ok"]),
        "hart1_U_instr": sorted({r.get("u_instructions") for r in hart1}),
        "offmask_entries": {h: {"ok": r["ok"], "instr": r["instr_by_mode"], "outside_tensor": r["outside_tensor"]} for h, r in offmask.items()},
        "stray": c["stray_unselected_harts"],
        "minimum_log_set_(i)_every_hart_of_every_enabled_shire": full_active,
        "minimum_log_set_(ii)_inactive_shires_with_all_64": full_inactive,
        "bases": c["bases"], "base_agreement": c["base_agreement"], "base_candidates": c["base_candidates"],
        "leaderA_all": c["leaderA_all"], "leaderB_all": c["leaderB_all"], "side_field_problems": c["side_field_problems"],
        "chip": c["chip_sharing"], "interleave": c["sysemu_interleaving"], "host": c["host_records"],
        "warn": c["warn"], "unparsed_tensor": c["unparsed_tensor"],
    }
    out[name] = rec
json.dump(out, sys.stdout, indent=1, default=str)
print()
