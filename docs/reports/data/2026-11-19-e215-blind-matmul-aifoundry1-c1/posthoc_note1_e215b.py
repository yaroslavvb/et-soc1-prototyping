#!/usr/bin/env python3
"""E215 arm B data, dated note 1 (post hoc): what the arm A line of this directory's never-run report reads.

Written by the fix lane fix-e215d (Q224), Thu 19 Nov 2026 PST, after the data verifier verify-e215d (its finding 3). Standard library only.
It reads committed files only, each checked first, and writes nothing but its JSON (--json PATH):
  - this directory's step-6n report and judgement (neverrun-e215-card.json, judge-e215-card.json, labels-e215.json; SHA256SUMS);
  - the same three files of arm A's directory, ../2026-11-19-e215-blind-matmul-aifoundry3 (its SHA256SUMS);
  - E215's never-run candidates (tools/claims-v3/e215/desk/candidates-e215.json; SHA256SUMS-e215-registration, and both reports'
    candidates_sha256);
  - E217's registration tree (tools/claims-v3/e217/; SHA256SUMS-e217-registration);
  - the registered scanners' own patterns, reader and tile names: tools/claims-v3/e215/desk/neverrun_e215.py and, through it,
    tools/claims-v3/e213/desk/neverrun_e213.py, each loaded at its pinned sha256 (their module level is standard library only; no scan is run).
For each of arm A's 62 rows (60 scored points, 2 references) it prints the row's verdict in arm A's own step 6n (scan 12:05:06-12:05:17 PST) and
in arm B's (scan 13:41:38-13:41:49 PST), the change in the number of counted files holding the row's shape between the two scans, and the files
of E217's registration tree that meet the row's reading (literal: the shape; family L: the shape and its mask; family S: a GEMM run record
naming one of the kind's tile files). Run from this directory:
    /usr/bin/python3 -I -B posthoc_note1_e215b.py [--json <path>]
SPDX-License-Identifier: Apache-2.0
"""
import hashlib
import importlib.util
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", "..", "..", ".."))
DIR_B = HERE
DIR_A = os.path.join(REPO, "docs", "reports", "data", "2026-11-19-e215-blind-matmul-aifoundry3")
E215 = os.path.join(REPO, "tools", "claims-v3", "e215")
E217 = os.path.join(REPO, "tools", "claims-v3", "e217")
SCANNER = (os.path.join(E215, "desk", "neverrun_e215.py"), "9e68b0012dd782cd1fcb91806a8213f550294822337de204344bd22b73a89789")
STEP6N = ("neverrun-e215-card.json", "judge-e215-card.json", "labels-e215.json")
FAILS = []


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def sums(sums_path, base, names):
    """check names (relative to base, as the sums file writes them) against a sha256sum-form list; returns 'n of n OK'"""
    want = {}
    for ln in open(sums_path, encoding="utf-8"):
        if len(ln) > 66 and ln[64:66] == "  ":
            want[ln[66:].rstrip("\n")] = ln[:64]
    ok = 0
    for n in names:
        if want.get(n) == sha(os.path.join(base, n)):
            ok += 1
        else:
            FAILS.append(f"{os.path.relpath(os.path.join(base, n), REPO)}: not as {os.path.relpath(sums_path, REPO)} lists it")
    return f"{ok} of {len(names)} OK"


def load(name, path, pin):
    if sha(path) != pin:
        sys.exit(f"REFUSED: {os.path.relpath(path, REPO)} is not at its pin {pin[:12]}")
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def live(row):
    return sum(row["token_hits_on_card"].values()) + sum(row["token_hits_other_cards"].values())


def main(argv):
    out_json = argv[argv.index("--json") + 1] if "--json" in argv else None
    lines = ["E215 arm B data, dated note 1 (post hoc): the arm A line of this directory's never-run report, read against arm A's own "
             "step 6n and E217's registration tree. Desk arithmetic on committed records (posthoc_note1_e215b.py, standard library only)."]
    # 1. the inputs, each checked first
    chk = {"arm B step 6n files (this directory's SHA256SUMS)": sums(os.path.join(DIR_B, "SHA256SUMS"), DIR_B, STEP6N + ("neverrun-e215-card.txt",)),
           "arm A step 6n files (arm A's SHA256SUMS)": sums(os.path.join(DIR_A, "SHA256SUMS"), DIR_A, STEP6N + ("neverrun-e215-card.txt",))}
    cand = os.path.join(E215, "desk", "candidates-e215.json")
    chk["E215's candidates (SHA256SUMS-e215-registration)"] = sums(os.path.join(E215, "SHA256SUMS-e215-registration"), REPO,
                                                                   [os.path.relpath(cand, REPO)])
    e217_files = []
    for dp, dn, fns in os.walk(E217):
        dn.sort()
        for fn in sorted(fns):
            p = os.path.join(dp, fn)
            if fn != "SHA256SUMS-e217-registration":
                e217_files.append(os.path.relpath(p, REPO))
    chk["E217's registration tree (SHA256SUMS-e217-registration)"] = sums(os.path.join(E217, "SHA256SUMS-e217-registration"), REPO, e217_files)
    NR = load("neverrun_e215", SCANNER[0], SCANNER[1])
    N = NR.e213_module()                           # E213's scanner at its own pin (it refuses, exit 4, if not)
    chk["the registered scanners"] = f"neverrun_e215.py {SCANNER[1][:12]}, neverrun_e213.py {NR.E213_SCAN[1][:12]} (pins OK)"
    RA = json.load(open(os.path.join(DIR_A, "neverrun-e215-card.json")))
    RB = json.load(open(os.path.join(DIR_B, "neverrun-e215-card.json")))
    JA = json.load(open(os.path.join(DIR_A, "judge-e215-card.json")))
    JB = json.load(open(os.path.join(DIR_B, "judge-e215-card.json")))
    LA = json.load(open(os.path.join(DIR_A, "labels-e215.json")))
    LB = json.load(open(os.path.join(DIR_B, "labels-e215.json")))
    cs = sha(cand)
    chk["both reports read the same candidates"] = "yes" if RA["candidates_sha256"] == RB["candidates_sha256"] == cs else "NO"
    if chk["both reports read the same candidates"] != "yes":
        FAILS.append("the two reports' candidates differ from the registered file")
    lines.append("")
    lines.append("1. Inputs, each checked first:")
    lines += [f"   {k}: {v}" for k, v in chk.items()]
    # 2. the two scans' head lines, as committed
    lines.append("")
    lines.append("2. The two step-6n reports (the registered scanner's report always prints both arms; the card tool judges only its own arm):")
    for tag, R, J, L in (("arm A's day (arm A's directory)", RA, JA, LA), ("arm B's day (this directory)", RB, JB, LB)):
        lines.append(f"   {tag}: scan {R['scan_sha256'][:12]} over {R['files_read']} files, {R['scan_window'][0]} - {R['scan_window'][1]}")
        for arm in ("A", "B"):
            a = R["arms"][arm]
            lines.append(f"     report row, arm {arm}: {a['n_never_run']} of {a['n_points']} scored points never ran; {len(a['dropped'])} read otherwise")
        lines.append(f"     judgement of arm {J['arm']} only ({J['started']} - {J['ended']}): {J['n_never_run']} of {J['n_points']} never ran; "
                     f"labelled 'ran before': {sorted(L[J['arm']]['ran_before_points']) or 'none'}; REPORTED and kept: {len(J['ran_after_REPORTED'])}")
    # 3. E217's registration tree read by the registered scanner's own reader and patterns
    names, _aliases = NR.tile_names(REPO)
    base_kind = {}
    for k, v in names.items():
        for n in v:
            base_kind.setdefault(n, set()).add(k)
    tree = {}
    for rel in e217_files:
        p = os.path.join(REPO, rel)
        if rel.endswith(N.SKIP_EXT) or os.path.islink(p):
            continue
        txt = N.read_text(p)
        shapes = set(N.RX.findall(txt))
        masks = {"0x%x" % int(m, 16) for m in NR.MRX.findall(txt)} if shapes else set()
        kinds = set()
        if ":" in txt:
            for _arm, gen, files in NR.VRX.findall(txt):
                for f in files.split(","):
                    kinds |= base_kind.get(os.path.basename(f.strip()), set())
                if gen == "e37":
                    kinds.add("fp32.e37")
        tree[rel] = (shapes, masks, kinds)
    idx = json.load(open(os.path.join(E217, "desk", "configs-e217.json")))
    recs = idx["records"]
    e217_scan = json.load(open(os.path.join(E217, "desk", "scan-e217.json")))["tokens"]
    record_txt = N.read_text(os.path.join(E217, "desk", "card-record-e217.txt"))
    ra = {x["id"]: x for x in RA["arms"]["A"]["points"]}
    rows, flipped, explained, delta_ok = [], [], [], 0
    lines.append("")
    lines.append(f"3. Arm A's rows (62): the verdict at each scan, the change in counted files holding the shape, and E217's files that meet the "
                 f"row's reading ({len(tree)} of E217's {len(e217_files)} registered files read; {len(e217_files) - len(tree)} skipped by the "
                 f"scanner's own extensions):")
    lines.append("   id   fam shape            mask / kind               12:05   13:41   files with shape 12:05 -> 13:41 (change) | "
                 "E217 files holding the shape | E217 files meeting the reading; configs-e217.json rows of that configuration")
    for x in RB["arms"]["A"]["points"]:
        a = ra[x["id"]]
        shp = x["token"]
        holding = sorted(f for f, (s, m, k) in tree.items() if shp in s)
        if x["family"] == "L":
            meets = sorted(f for f in holding if x["mask"] in tree[f][1])
            cfg = [r["status"] for r in recs if r.get("token") == shp and r.get("mask", "").lower() == x["mask"]]
            what = x["mask"]
        elif x["family"] == "S":
            meets = sorted(f for f, (s, m, k) in tree.items() if x["kind_key"] in k)
            cfg = sorted({":".join(t) for t in NR.VRX.findall(record_txt)
                          if any(x["kind_key"] in base_kind.get(os.path.basename(f.strip()), set()) for f in t[2].split(","))})
            what = x["kind_key"]
        else:
            meets = holding
            cfg = [r["status"] for r in recs if r.get("token") == shp and r.get("exp") == "E215" and r.get("arm_id") == x["id"]]
            what = ""
        d = live(x) - live(a)
        if d == len(holding):
            delta_ok += 1
        flip = a["never_run"] and not x["never_run"]
        if flip:
            flipped.append(x["id"])
            if meets:
                explained.append(x["id"])
        rec = {"id": x["id"], "family": x["family"], "role": x["role"], "shape": shp, "mask_or_kind": what,
               "never_run_at_arm_A_step6n": a["never_run"], "never_run_at_arm_B_step6n": x["never_run"],
               "counted_files_holding_shape": [live(a), live(x)], "change": d, "E217_files_holding_shape": holding,
               "E217_files_meeting_reading": meets,
               ("card_record_e217_run_strings_of_this_kind" if x["family"] == "S" else "configs_e217_rows_of_this_configuration"): sorted(set(cfg)),
               "scan_e217_classes_for_this_shape": sorted(e217_scan.get(shp, {})),
               "arm_B_scan_S_records_outside_MM1_v31_data_any_card": x.get("kind_gemm_runs_outside_mm1_v31_data_any_card")}
        rows.append(rec)
        short = [os.path.basename(f) for f in meets]
        lines.append(f"   {x['id']:4s} {x['family']:3s} {shp:16s} {what:25s} {'never' if a['never_run'] else 'ran':7s} {'never' if x['never_run'] else 'ran':7s} "
                     f"{live(a)} -> {live(x)} ({d:+d}) | {len(holding)} | {', '.join(short) or 'none'}"
                     + (f"; {', '.join(sorted(set(cfg)))}" if cfg else ""))
    # 4. the summary
    fam = {}
    for r in rows:
        if r["role"] != "point":
            continue
        k = "L" if r["family"] == "L" else "S" if r["family"] == "S" else "P, C, R"
        f = fam.setdefault(k, {"rows": 0, "read_otherwise_at_13:41": 0, "met_by_E217_files": 0})
        f["rows"] += 1
        if not r["never_run_at_arm_B_step6n"]:
            f["read_otherwise_at_13:41"] += 1
            if r["E217_files_meeting_reading"]:
                f["met_by_E217_files"] += 1
    s_never = [r["id"] + " " + r["mask_or_kind"] for r in rows if r["family"] == "S" and r["never_run_at_arm_B_step6n"]]
    s_never_met = [r["id"] for r in rows if r["family"] == "S" and r["never_run_at_arm_B_step6n"] and r["E217_files_meeting_reading"]]
    pcr = [r for r in rows if r["role"] == "point" and r["family"] in ("P", "C", "R")]
    pcr_sub = sum(1 for r in pcr if r["scan_e217_classes_for_this_shape"] == ["SUBTRACTED"])
    s_strings = sorted({s for r in rows if r["family"] == "S" for s in r.get("card_record_e217_run_strings_of_this_kind", [])})
    planned_a = sum(1 for r in recs if r.get("exp") == "E215" and r.get("session") == "arm A")
    planned_a_status = sorted({r["status"] for r in recs if r.get("exp") == "E215" and r.get("session") == "arm A"})
    summary = {
        "arm_A_rows": len(rows), "points_never_run_at_arm_A_step6n": sum(1 for r in rows if r["role"] == "point" and r["never_run_at_arm_A_step6n"]),
        "points_never_run_at_arm_B_step6n": sum(1 for r in rows if r["role"] == "point" and r["never_run_at_arm_B_step6n"]),
        "points_read_otherwise_at_arm_B_step6n_only": len(flipped), "of_them_met_by_E217_registration_files": len(explained),
        "by_family": fam, "rows_whose_change_equals_E217_files_holding_the_shape": delta_ok,
        "S_points_still_never_run": s_never, "S_points_still_never_run_with_an_E217_record": s_never_met,
        "configs_e217_rows_of_E215_arm_A": planned_a, "their_status": planned_a_status,
        "PCR_shapes_scan_e217_holds_only_in_its_SUBTRACTED_class": f"{pcr_sub} of {len(pcr)}",
        "card_record_e217_run_strings_of_the_S_kinds": s_strings,
        "inputs": chk, "checks_failed": FAILS}
    lines.append("")
    lines.append("4. Summary:")
    lines.append(f"   arm A's own step 6n: {summary['points_never_run_at_arm_A_step6n']} of 60 scored points never ran (its judgement and labels: "
                 f"labelled none)")
    lines.append(f"   arm B's step 6n, its arm A row: {summary['points_never_run_at_arm_B_step6n']} of 60; read otherwise there only: "
                 f"{len(flipped)}; of them met by a file of E217's registration tree: {len(explained)}")
    for k in ("L", "P, C, R", "S"):
        f = fam.get(k, {})
        lines.append(f"     family {k}: {f.get('rows', 0)} rows, {f.get('read_otherwise_at_13:41', 0)} read otherwise at 13:41, "
                     f"{f.get('met_by_E217_files', 0)} of them met by E217 files")
    lines.append(f"   rows whose change in counted files equals the E217 files holding the shape: {delta_ok} of {len(rows)}")
    lines.append(f"   S points still never run at 13:41: {', '.join(s_never)}; any E217 run record of their kinds: {s_never_met or 'none'}")
    lines.append(f"   configs-e217.json rows of E215 arm A: {planned_a}, status {planned_a_status}")
    lines.append(f"   scan-e217.json: the P, C and R shapes it holds only in its own SUBTRACTED class (files of E215's folders, set apart by E217's "
                 f"scan): {pcr_sub} of {len(pcr)}")
    lines.append(f"   card-record-e217.txt: its GEMM run strings of the S kinds: {', '.join(s_strings) or 'none'}")
    lines.append(f"   checks failed: {FAILS or 'none'}")
    print("\n".join(lines))
    if out_json:
        json.dump({"what": "E215 arm B data, dated note 1 (post hoc): the arm A line of the never-run report (posthoc_note1_e215b.py)",
                   "summary": summary, "rows": rows}, open(out_json, "w"), indent=1, sort_keys=True)
        open(out_json, "a").write("\n")
    return 0 if not FAILS and len(explained) == len(flipped) and delta_ok == len(rows) else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
