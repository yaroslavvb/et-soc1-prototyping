#!/usr/bin/env python3
"""E222, dated note 1, section 1 (round Q236, lane fix-e222, Fri 20 Nov 2026, written before any E222 datum): the registration's never-run
report in the wording the orchestrator's answer 1 requires, and a positive control by E218's run records. No scan is re-run here and no point,
forecast, rule or label changes: this reads the registered report (tools/claims-v3/e222/desk/neverrun-e222.json, at its pin in
SHA256SUMS-e222-registration) and prints each point's verdict again, family R's four as RAN (exempt by family name: same-card repeats,
REPORTED only) and the 66 others as never ran; then it reads E218's committed data file on aifoundry3 card 0 (data-e218.json at the frozen
scorer's own pin, score_e222.E218_DATA) and shows each R point's configuration (shape token, format, minions, shire mask) among E218's kept
runs there at 600 MHz: the exemption lifted, all four must read RAN. Standard library only.

    /usr/bin/python3 -I -B tools/claims-v3/e222-notes/neverrun_note1_e222.py report <out dir>
        writes <out dir>/neverrun-e222-note1.json and .txt; exit 0 when the corrected count is 66 of 66 and the control 4 of 4; 15 when the
        control fails (the scan could not have seen this card's sessions: the orchestrator's answer 1); 4 a file not at its pin.
SPDX-License-Identifier: Apache-2.0
"""
import hashlib
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", "..", ".."))
E = "tools/claims-v3/e222"
REG_LIST = (E + "/SHA256SUMS-e222-registration", "de67150bee12bde15c50d0f1067d042a0cd0ca3a9a8ad74af577145d077acef7", 30)
E218_DIR = "docs/reports/data/2026-11-20-e218-blind-matmul-aifoundry3"
E218_DATA = (E218_DIR + "/data-e218.json", "31597c6025a732d3e541b2e8923ddd1b0a7b666fd7879987b74bd7132d982d8c")   # score_e222.E218_DATA
CARD = "aifoundry3 card 0"
R_WORDS = "RAN (exempt by family name: same-card repeats, REPORTED only)"


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def now():
    return time.strftime("%Y-%m-%d %H:%M:%S %Z")


def pins():
    rel, pin, n = REG_LIST
    p = os.path.join(REPO, rel)
    if not os.path.exists(p) or sha(p) != pin:
        print(f"neverrun_note1_e222: REFUSED, {rel} is not at its pin {pin[:12]}")
        sys.exit(4)
    lines = {}
    for ln in open(p):
        if ln.strip() and not ln.startswith("#"):
            h, f = ln.split(None, 1)
            lines[f.strip()] = h
    bad = [f for f, h in lines.items() if not os.path.exists(os.path.join(REPO, f)) or sha(os.path.join(REPO, f)) != h]
    if bad or len(lines) != n:
        print(f"neverrun_note1_e222: REFUSED, {rel}: {len(lines) - len(bad)} of {n} OK; not OK: {bad[:5]}")
        sys.exit(4)
    if sha(os.path.join(REPO, E218_DATA[0])) != E218_DATA[1]:
        print(f"neverrun_note1_e222: REFUSED, {E218_DATA[0]} is not at its pin {E218_DATA[1][:12]}")
        sys.exit(4)
    return lines


def control(points):
    """the exemption lifted: each R point's configuration among E218's kept runs on this card (data-e218.json, arm A)"""
    d = json.load(open(os.path.join(REPO, E218_DATA[0])))
    readme = open(os.path.join(REPO, E218_DIR, "README.md")).readline()
    card_named = CARD in readme
    pts = d["arms"]["A"]["points"]
    out = {}
    for p in points:
        if p["family"] != "R":
            continue
        e = p["e218_id"]
        runs = (pts.get(e) or {}).get("runs") or []
        match = []
        for r in runs:
            rec = r.get("record") or {}
            det = r.get("detail") or {}
            same = (rec.get("arm") == p["arm"] and rec.get("type") == p["format"] and int(rec.get("minions", -1)) == int(p["minions"])
                    and int(str(rec.get("shire_mask", "-1")), 16) == int(str(p["shire_mask"]), 16))
            ran = r.get("cycles_gemm") is not None and r.get("t_gemm_s") is not None and 590 <= float(det.get("mhz") or r.get("mhz_min") or 0) <= 610
            if same and ran:
                match.append({"n": r.get("n"), "block": r.get("block"), "mhz": det.get("mhz"), "n_gemm": det.get("n_gemm"), "checks": r.get("checks")})
        out[p["id"]] = {"e218_id": e, "token": p["arm"], "mask": p["shire_mask"], "format": p["format"], "minions": p["minions"],
                        "kept_runs_on_card": len(match), "runs": match, "verdict": "RAN" if (match and card_named) else "never ran"}
    return out, card_named


def report(outdir):
    lines = pins()
    t0 = now()
    nr = json.load(open(os.path.join(REPO, E, "desk", "neverrun-e222.json")))
    P = json.load(open(os.path.join(REPO, E, "points-e222.json")))
    fam = {p["id"]: p["family"] for p in P["points"]}
    rows, never, ranR = [], 0, []
    for q in nr["points"]:
        pid = q["id"]
        if fam.get(pid) == "R" or q.get("reading") == "exempt":
            verdict = R_WORDS
            ranR.append(pid)
        elif q.get("never_run") is True:
            verdict = "never ran"
            never += 1
        else:
            verdict = "RAN (a session record on the card): labelled 'ran before', in no rule"
        rows.append({"id": pid, "family": q["family"], "token": q["token"], "mask": q["mask"], "reading": q["reading"], "verdict": verdict,
                     "literal_reading_REPORTED": "never ran" if q.get("literal_never_run_REPORTED") else "named in a file counted for the card"})
    nonr = [r for r in rows if r["family"] != "R"]
    ctl, card_named = control(P["points"])
    ctl_ok = sum(1 for v in ctl.values() if v["verdict"] == "RAN")
    lit = sum(1 for r in rows if r["literal_reading_REPORTED"] == "never ran")
    head = (f"NEVER-RUN-E222 (dated note 1's wording of the registered report): {never} of {len(nonr)} registered non-R points never ran on {CARD} by "
            f"session records; ran before, labelled: none; family R: " + ", ".join(f"{x} RAN" for x in ranR) + f" {R_WORDS[4:]}; "
            f"the positive control by E218's run records (the exemption lifted; {E218_DATA[0].split('/')[-1]} at its pin {E218_DATA[1][:12]}): "
            f"{ctl_ok} of {len(ctl)} RAN; the literal reading (REPORTED, not a label): {lit} of {len(rows)} never ran")
    rec = {"what": "E222's registered never-run report (desk/neverrun-e222.json, unchanged) in the wording of the orchestrator's answer 1, with "
                   "family R printed RAN (exempt) and a positive control by E218's run records; no re-scan; no point, forecast, rule or label changes",
           "interpreter": f"{sys.executable} {sys.version.split()[0]}", "reads": {"desk/neverrun-e222.json": lines[E + "/desk/neverrun-e222.json"],
           "points-e222.json": lines[E + "/points-e222.json"], E218_DATA[0]: E218_DATA[1]},
           "registered_scan": {"scan_sha256": nr["scan_sha256"], "files_read": nr["files_read"], "window": nr["scan_window"], "lab_head": nr["lab_head"]},
           "n_non_R": len(nonr), "n_non_R_never_ran": never, "family_R": {x: R_WORDS for x in ranR}, "labelled_ran_before": [],
           "positive_control_e218_run_records": {"card_named_in_E218_README_line_1": card_named, "points": ctl, "ran": ctl_ok, "of": len(ctl)},
           "literal_reading_REPORTED_never_ran": lit, "points": rows, "summary": head}
    os.makedirs(outdir, exist_ok=True)
    jp = os.path.join(outdir, "neverrun-e222-note1.json")
    json.dump(rec, open(jp, "w"), indent=1, sort_keys=True)
    open(jp, "a").write("\n")
    tl = [f"E222 never-run report, dated note 1's wording, made {t0} (the registered report desk/neverrun-e222.json read unchanged: scan "
          f"{nr['scan_sha256'][:16]}, {nr['files_read']} files, {nr['scan_window'][0]} - {nr['scan_window'][1]}, lab {nr['lab_head'][:12]}; the "
          f".json beside holds no time, so two runs compare byte for byte)", head]
    for r in rows:
        tl.append(f"{r['id']:7s} {r['family']:4s} {r['token']:18s} {r['mask']:10s} {r['reading']:11s} {r['verdict']}   (literal, REPORTED: {r['literal_reading_REPORTED']})")
    tl.append(f"POSITIVE CONTROL (E218's run records on {CARD}; README line 1 names the card: {card_named}):")
    for pid, v in ctl.items():
        tl.append(f"  {pid} = E218's {v['e218_id']}: {v['token']} {v['format']} {v['minions']} minions mask {v['mask']}: {v['verdict']} "
                  f"({v['kept_runs_on_card']} kept runs at 590-610 MHz: " + ", ".join(f"run {x['n']} {x['block']} {x['mhz']} MHz, {x['n_gemm']} GEMMs, checks {x['checks']}"
                                                                                       for x in v["runs"]) + ")")
    open(os.path.join(outdir, "neverrun-e222-note1.txt"), "w").write("\n".join(tl) + "\n")
    print(head)
    if ctl_ok != len(ctl) or len(ctl) != 4:
        print("POSITIVE CONTROL FAILED")
        return 15
    return 0 if (never == len(nonr) == 66) else 1


if __name__ == "__main__":
    if len(sys.argv) >= 3 and sys.argv[1] == "report":
        sys.exit(report(sys.argv[2]))
    print(__doc__)
    sys.exit(2)
