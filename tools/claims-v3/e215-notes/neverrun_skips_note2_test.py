#!/usr/bin/env python3
"""E215, dated note 2 (post hoc; fix-e215d, Q224, Thu 19 Nov 2026): the accounting of the scanner fix's test on real inputs. Standard library only.

It reads two scans made back to back over the same folders - T0 by E215's registered scanner unchanged, T1 by neverrun_skips_note2.py - with the
fix's list of the files it skipped or thinned (skips-e215-note2.json), and both scans' reports over E215's registered candidates, and checks:
  1. every change from T0 to T1 is one the fix made: for each shape and card class, T0's count of files holding the shape less T1's equals the
     number of skipped or thinned files of that class whose text held the shape before and not after; T1's masks beside each shape are T0's
     less only masks named in such files; for each S kind and class, T0's count of files with a GEMM run string naming the kind less T1's equals
     the skipped files that held one;
  2. no skipped file is a run record (a run.json, a host's proc output, telemetry, a session log or queue);
  3. the verdicts per point that change from T0 to T1, per arm.
The classes of the skipped files are made by the registered scanners' own rules (E213's lane_card and folder_card, E215's subtracted).
    /usr/bin/python3 -I -B neverrun_skips_note2_test.py <T0 dir> <T1 dir> --lab <lab> [--json <path>]
SPDX-License-Identifier: Apache-2.0
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import neverrun_skips_note2 as F  # noqa: E402  (loads the registered scanners at their pins)

NR, N = F.NR, F._N
RUN_NAMES = ("run.json", "telemetry.jsonl.gz", "session.log", "queue.json", "runner.out")


def klass(rel, expmap):
    return "SUBTRACTED" if NR.subtracted(rel) else (N.lane_card(rel) or N.folder_card(rel, expmap) or N.NONE)


def main(argv):
    t0, t1 = argv[0], argv[1]
    lab = argv[argv.index("--lab") + 1]
    out_json = argv[argv.index("--json") + 1] if "--json" in argv else None
    S0 = json.load(open(os.path.join(t0, "scan-e215.json")))
    S1 = json.load(open(os.path.join(t1, "scan-e215.json")))
    K = json.load(open(os.path.join(t1, "skips-e215-note2.json")))
    R0 = json.load(open(os.path.join(t0, "neverrun-e215.json")))
    R1 = json.load(open(os.path.join(t1, "neverrun-e215.json")))
    expmap = N.exp_cards(lab)
    names, _ = NR.tile_names(lab)
    base_kind = {}
    for k, v in names.items():
        for n in v:
            base_kind.setdefault(n, set()).add(k)

    def kinds(strings):
        ks = set()
        for s in strings:
            arm, gen, files = s.split(":", 2)
            for f in files.split(","):
                ks |= base_kind.get(os.path.basename(f.strip()), set())
            if gen == "e37":
                ks.add("fp32.e37")
        return ks

    files = K["files"]
    for f in files:
        f["class"] = klass(f["file"], expmap)
    lines = [f"neverrun_skips_note2_test.py: T0 (the registered scan) {S0['started']} - {S0['ended']}, {S0['files_read']} files; "
             f"T1 (the wrapped scan) {S1['started']} - {S1['ended']}, {S1['files_read']} files; the fix skipped or thinned {len(files)} files "
             f"holding a shape or a GEMM run string, by rule {K['files_by_rule']}"]
    # 1. shapes by class
    bad, n_cells, n_changed = [], 0, 0
    shapes = sorted(set(S0["tokens"]) | set(S1["tokens"]))
    for t in shapes:
        c0, c1 = S0["tokens"].get(t, {}), S1["tokens"].get(t, {})
        for c in sorted(set(c0) | set(c1)):
            n_cells += 1
            a, b = c0.get(c, {}).get("n", 0), c1.get(c, {}).get("n", 0)
            k = sum(1 for f in files if f["class"] == c and t in f["before"]["shapes"] and t not in f["after"]["shapes"])
            if a != b:
                n_changed += 1
            if a - b != k:
                bad.append(f"shape {t} class {c}: T0 {a} T1 {b}, skipped files holding it {k}")
            m0 = set(S0["masks_by_card"].get(t, {}).get(c, []))
            m1 = set(S1["masks_by_card"].get(t, {}).get(c, []))
            named = set()
            for f in files:
                if f["class"] == c and t in f["before"]["shapes"]:
                    named |= set(f["before"]["masks"])
            if not m1 <= m0 or not (m0 - m1) <= named:
                bad.append(f"masks of {t} class {c}: lost {sorted(m0 - m1)[:6]} not all named in skipped files, or T1 has new ones")
    # S kinds by class
    s_cells = 0
    for kk in sorted(set(S0["s_kind_gemm_runs_by_card"]) | set(S1["s_kind_gemm_runs_by_card"])):
        c0, c1 = S0["s_kind_gemm_runs_by_card"].get(kk, {}), S1["s_kind_gemm_runs_by_card"].get(kk, {})
        for c in sorted(set(c0) | set(c1)):
            s_cells += 1
            a, b = c0.get(c, {}).get("n_files", 0), c1.get(c, {}).get("n_files", 0)
            k = sum(1 for f in files if f["class"] == c and kk in kinds(f["before"]["gemm_run_strings"])
                    and kk not in kinds(f["after"]["gemm_run_strings"]))
            if a - b != k:
                bad.append(f"S kind {kk} class {c}: T0 {a} files T1 {b}, skipped files naming it {k}")
    lines.append(f"1. accounting: {n_cells} (shape, class) cells, {n_changed} changed from T0 to T1, every change equal to the skipped files' "
                 f"count and masks: {'yes' if not [x for x in bad if not x.startswith('S kind')] else 'NO'}; {s_cells} (S kind, class) cells, "
                 f"every change equal to the skipped files' GEMM run strings: {'yes' if not [x for x in bad if x.startswith('S kind')] else 'NO'}")
    lines += [f"   NOT EQUAL: {x}" for x in bad[:40]]
    # 2. what was skipped
    runs = [f["file"] for f in files if os.path.basename(f["file"]).split(".gz")[0] in RUN_NAMES or os.path.basename(f["file"]).startswith("proc-")]
    by_place = {}
    for f in files:
        top = "docs/reports/data" if f["file"].startswith("docs/reports/data/") else ("W/out/" + f["file"].split("/")[2]
                                                                                       if f["file"].startswith("W/out/") else "other")
        by_place.setdefault((f["rule"], top), []).append(f["file"])
    lines.append(f"2. skipped files that are run records (run.json, proc-*, telemetry, session.log, queue.json, runner.out): {len(runs)}"
                 + (f" {runs[:8]}" if runs else ""))
    lines.append("   skipped or thinned files by rule and folder (files; their classes):")
    for (rule, top), fs in sorted(by_place.items()):
        cl = sorted({f["class"] for f in files if f["file"] in fs})
        lines.append(f"     {rule:12s} {top}: {len(fs)} ({', '.join(cl)})")
    committed = sorted(f["file"] for f in files if f["file"].startswith("docs/reports/data/"))
    lines.append(f"   of them in the lab's committed data folders: {len(committed)}")
    lines += [f"     {x}" for x in committed]
    # 3. the verdicts
    changed = {}
    for arm in ("A", "B"):
        a0 = {x["id"]: x for x in R0["arms"][arm]["points"]}
        a1 = {x["id"]: x for x in R1["arms"][arm]["points"]}
        ch = [i for i in a0 if a0[i]["never_run"] != a1[i]["never_run"]]
        changed[arm] = ch
        lines.append(f"3. arm {arm}: T0 {R0['arms'][arm]['n_never_run']} of {R0['arms'][arm]['n_points']} never ran, T1 "
                     f"{R1['arms'][arm]['n_never_run']} of {R1['arms'][arm]['n_points']}; rows changed {len(ch)}"
                     f" (T0 not never run -> T1 never run: {sum(1 for i in ch if a1[i]['never_run'])}); references T0 "
                     f"{[i for i in a0 if a0[i]['role'] != 'point' and not a0[i]['never_run']]}, T1 "
                     f"{[i for i in a1 if a1[i]['role'] != 'point' and not a1[i]['never_run']]}")
    ok = not bad and not runs
    lines.append(f"TEST {'PASS' if ok else 'FAIL'}: every T0-to-T1 change is a skipped file's; no run record skipped")
    print("\n".join(lines))
    if out_json:
        json.dump({"what": "the scanner fix's test on real inputs (neverrun_skips_note2_test.py)", "t0": {k: S0[k] for k in ("started", "ended", "files_read")},
                   "t1": {k: S1[k] for k in ("started", "ended", "files_read")}, "files_by_rule": K["files_by_rule"],
                   "cells": n_cells, "cells_changed": n_changed, "s_cells": s_cells, "not_equal": bad, "run_records_skipped": runs,
                   "skipped_by_rule_and_folder": {f"{r} {t}": len(fs) for (r, t), fs in sorted(by_place.items())},
                   "skipped_in_committed_data_folders": committed,
                   "verdicts": {arm: {"t0_never_run": R0["arms"][arm]["n_never_run"], "t1_never_run": R1["arms"][arm]["n_never_run"],
                                      "n_points": R0["arms"][arm]["n_points"], "rows_changed": changed[arm]} for arm in ("A", "B")},
                   "pass": ok}, open(out_json, "w"), indent=1, sort_keys=True)
        open(out_json, "a").write("\n")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
