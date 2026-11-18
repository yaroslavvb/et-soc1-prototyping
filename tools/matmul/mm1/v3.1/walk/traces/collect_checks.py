#!/usr/bin/env python3
"""v31-trace (Q217): collect every fetched run's check (check.json), traced numbers (traced_numbers.json), host records and run facts into
traces/check_summary.json and a markdown table traces/check_summary.md. Desk; standard library; /usr/bin/python3 3.12.3."""
import gzip
import hashlib
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))


def main():
    plan = json.load(open(os.path.join(HERE, "plan.json")))
    rows = []
    for r in plan["runs"]:
        d = os.path.join(HERE, "runs", r["name"])
        if not os.path.exists(os.path.join(d, "check.json")):
            rows.append({"name": r["name"], "ran": False})
            continue
        c = json.load(open(os.path.join(d, "check.json")))
        tn = json.load(open(os.path.join(d, "traced_numbers.json"))) if os.path.exists(os.path.join(d, "traced_numbers.json")) else {}
        s = json.load(gzip.open(os.path.join(d, "summary.json.gz"), "rt"))
        m = s["meta"]
        ph = c["per_hart"]
        w = [x for x in ph.values() if x["expect"] == "the walk's events"]
        h1 = [x for x in ph.values() if x["expect"].startswith("enter")]
        off = [x for x in ph.values() if x["expect"].startswith("never")]
        rows.append({
            "name": r["name"], "ran": True, "kernel": r["kernel"], "arm": r["arm"], "mask": r["mask"], "verdict": c["verdict"],
            "start_pst": __import__("time").strftime("%H:%M:%S", __import__("time").localtime(m["start_epoch"])),
            "end_pst": __import__("time").strftime("%H:%M:%S", __import__("time").localtime(m["end_epoch"])),
            "host_rc": m["host_rc"], "host_wall_s": m["host_wall_s"], "log_lines": s["log_lines"], "log_GB": round(s["log_bytes"] / 1e9, 2),
            "peak_rss_MB": round(m["peak_rss_kb_sum_of_sim_tree"] / 1024.0), "summary_sha256": hashlib.sha256(open(os.path.join(d, "summary.json.gz"), "rb").read()).hexdigest(),
            "working_traced": len(w), "working_exact": sum(1 for x in w if x["equal"]), "events_per_working_hart": sorted({x["n_trace"] for x in w}),
            "diff_positions": c["diff_positions_total"], "side_field_problems": c["side_field_problems"], "lines_ok": c["lines_ok"],
            "lines_read": sum(x["lines_read"] for x in w), "lines_written": sum(x["lines_written"] for x in w),
            "pa_minus_va": sorted({k for x in w for k in x["pa_minus_va"]}),
            "hart1_traced": len(h1), "hart1_ok": sum(1 for x in h1 if x["ok"]), "hart1_u_instr": sorted({x.get("u_instructions") for x in h1}),
            "off_mask_harts": len(off), "off_mask_ok": sum(1 for x in off if x["ok"]),
            "shires_complete_equal": {k: (v["coverage_complete"], v["steps_unequal"]) for k, v in c["shires"].items()},
            "chip_sharing": c["chip_sharing"], "interleaving": c["sysemu_interleaving"], "host": c["host_records"],
            "stray": c.get("stray_unselected_harts"), "leaderA": c.get("leaderA_all"), "leaderB": c.get("leaderB_all"),
            "bases": c["bases"], "traced_numbers": tn,
            "elf_sha256": m.get("elf_sha256"), "host_sha256": m.get("host_sha256"), "stderr_lines": m.get("stderr_lines")})
    json.dump({"runs": rows, "python": sys.version.split()[0]}, open(os.path.join(HERE, "check_summary.json"), "w"), indent=1)
    L = ["| run | kernel | mask | aifoundry3 (PST) | host rc, wall | log streamed | traced working harts exact | events a hart | hart 1s | off-mask | lines read / written | shire streams, chip sharing equal (steps) | sim steps an op | verdict |",
         "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for x in rows:
        if not x["ran"]:
            L.append("| %s | - | - | NOT RUN | | | | | | | | | | |" % x["name"])
            continue
        sh = all(v[0] and v[1] == 0 for v in x["shires_complete_equal"].values())
        L.append("| %s | %s | %s | %s-%s | %d, %.0f s | %s lines, %.1f GB | %d of %d | %s | %d of %d (U %s) | %d of %d | %s / %s | %s; %s of %s | %.2f | %s |" % (
            x["name"], x["kernel"], x["mask"], x["start_pst"], x["end_pst"], x["host_rc"], x["host_wall_s"], format(x["log_lines"], ","),
            x["log_GB"], x["working_exact"], x["working_traced"], x["events_per_working_hart"], x["hart1_ok"], x["hart1_traced"],
            x["hart1_u_instr"], x["off_mask_ok"], x["off_mask_harts"], format(x["lines_read"], ","), format(x["lines_written"], ","),
            "yes" if sh else "NO", x["chip_sharing"].get("op_steps", 0) - x["chip_sharing"].get("steps_unequal", 0) if x["chip_sharing"].get("checked") else "-",
            x["chip_sharing"].get("op_steps", "-"), x["host"]["cycles_per_op_sim_steps"], x["verdict"]))
    open(os.path.join(HERE, "check_summary.md"), "w").write("\n".join(L) + "\n")
    print("\n".join(L))
    return 0


if __name__ == "__main__":
    sys.exit(main())
