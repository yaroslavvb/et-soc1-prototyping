#!/usr/bin/env python3
"""E224's never-run search REPEATED right before each arm's first card command, and its judgement (Q237, lane kit-e224, Fri 20 Nov 2026, before
any E224 datum), for BOTH ARMS (arm A's step 6n, rb/s06n_neverrun_e224a.sh; arm B's, rb/s06n_neverrun_e224b.sh). E224.md section 4: "The card
lanes repeat the scan right before their first card command (step 6n, note 1's reading): a point found run then is labelled 'ran before' and
leaves every rule, said." E224's registered scanner (desk/neverrun_e224.py) already reads by SESSION RECORDS ONLY (E220's dated note 1,
tools/claims-v3/e220-notes/E220.md.dated-note-1.md, registered as E224's reading); it NEVER OPENS a folder or file whose name holds 'e220',
'e222' or 'e224' (E220 AND E222 BLINDNESS at the registration). E220's two card days ran this afternoon ON E224's TWO CARDS and are committed
(arm A fd074f9e, arm B 257496b7), so a scan that never opens them cannot see them. This tool therefore runs TWO scans and judges both:

    /usr/bin/python3 -I -B tools/claims-v3/e224/desk/neverrun_card_e224.py run DIR --arm A|B --lab LAB --lanes OUT
        1. THE REGISTERED SCAN, unchanged at its registered sha256 (SHA256SUMS-e224-registration), as a subprocess, its outputs in DIR/registered:
           desk/neverrun_e224.py scan --lab LAB --lanes OUT --out DIR/registered; then its report --scan DIR/registered/scan-e224-reg.json
           --points LAB/tools/claims-v3/e224/points-e224.csv --out DIR/registered (neverrun-e224.json and .txt there, never in desk/);
        2. THE KIT'S WIDER SCAN (the brief's "with E220's own sessions counted once committed"): the SAME scanner module, loaded at the same pin in
           a subprocess of this tool (its hidden mode 'wider'), with ONE change made in memory - its never-opened rule narrowed to E224's own names
           (a name holding 'e224': the card lanes card-e224a and card-e224b, E224's data folders and lanes stay unread) - so that E220's and E222's
           committed data folders and lane folders ARE read (E220 AND E222 BLINDNESS ended with reg-e224's freeze line, posted 15:45:40 PST Fri 20
           Nov 2026); its record says so (kit_wider_scan); its report the same report function; outputs in DIR/wider;
        3. THE JUDGEMENT for the arm: a registered point of the arm whose verdict reads NOT never run in EITHER report (session records on the
           arm's card, family L on both cards, a gemmLnc point on both its tokens: E224.md 4's reading) is labelled 'ran before' and leaves every
           rule (the frozen scorer's --labels form, {"ran_before_points": {"<arm>": [...]}}, always written, its list empty when nothing ran);
           the literal reading of both scans REPORTED beside, never a label. DIR/judge-e224-<arm>.json and .txt, DIR/labels-e224-<arm>.json;
           its last line "NEVER-RUN-E224 arm <arm>: <n> of <N> registered points never ran on <card> by session records ...; ran before,
           labelled: <none / ids>; the literal reading (REPORTED, not a label): ..."
    /usr/bin/python3 -I -B tools/claims-v3/e224/desk/neverrun_card_e224.py check-labels FILE --arm A|B
        every label names a registered point of that arm (LABELS-OK / LABELS-REFUSED, exit 0 / 10)

REPORTED, never a gate: the card lane writes a dated note before the data commit when any point is labelled, and passes the labels file to the
scorer at step 13. NOT SEARCHED, as registered: the boxes' own disks and the model session's uncommitted folders (E224.md 4 and 8). Exit 0 with
its line; 14 a scan or report failed (run it again); 10 a usage error. RB_DESKTEST=1 lets E224_NR_SCANNER name a stand-in scanner (the runbooks'
desk tests only: it is called for both scans, with E224_NR_WIDER=1 in the wider one). Standard library only here (the scanner reads MM1-v3.2's
measured points through its data loader, numpy through it: the card lane runs this inside the round's slot, single-threaded).
SPDX-License-Identifier: Apache-2.0
"""
import hashlib
import importlib.util
import json
import os
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
E = os.path.normpath(os.path.join(HERE, ".."))
REPO = os.path.normpath(os.path.join(E, "..", "..", ".."))
SCANNER = (os.path.join(HERE, "neverrun_e224.py"), "e5fbc13aba28d1469392d4d1805877d86b450332f572dd39bbe626b775b2d06c")
POINTS_JSON = os.path.join(E, "points-e224.json")
POINTS_CSV = "tools/claims-v3/e224/points-e224.csv"
CARD = {"A": "aifoundry1 card 1", "B": "aifoundry2 card 0"}
NOTE1 = "tools/claims-v3/e220-notes/E220.md.dated-note-1.md"
WIDER_RULE = ("the kit's wider scan (desk/neverrun_card_e224.py, step 6n): the registered scanner's never-opened rule narrowed in memory to a name "
              "holding 'e224' (E224's own folders: the card lanes card-e224a and card-e224b, E224's data folders), so E220's and E222's committed "
              "data folders and lane folders are read; every other line of the scanner unchanged at its registered sha256")


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def now():
    return time.strftime("%Y-%m-%d %H:%M:%S %Z")


def reg_pin(rel):
    for ln in open(os.path.join(E, "SHA256SUMS-e224-registration")):
        if ln.strip() and not ln.startswith("#"):
            h, f = ln.split(None, 1)
            if f.strip() == rel:
                return h
    return None


def arm_points(arm):
    return json.load(open(POINTS_JSON))["points"][arm]


def scanner():
    """(path, words, stand-in?): the registered scanner at its registered sha256, or (RB_DESKTEST=1) a desk-test stand-in"""
    if os.environ.get("RB_DESKTEST") == "1" and os.environ.get("E224_NR_SCANNER"):
        return os.environ["E224_NR_SCANNER"], "a desk-test stand-in", True
    path, pin = SCANNER
    rel = os.path.relpath(path, REPO)
    if reg_pin(rel) != pin or sha(path) != pin:
        raise ValueError(f"{rel} is not at its registered sha256 {pin[:12]}")
    return path, f"{rel} at its registered sha256 {pin[:12]}", False


def wider(lab, lanes, out, points):
    """the hidden mode: the registered scanner loaded at its pin, its never-opened rule narrowed to 'e224' in memory, then its own scan and
    report into OUT; the scan record gains kit_wider_scan (what was changed and what was read that the registered scan never opens)"""
    path, pin = SCANNER
    if sha(path) != pin:
        print(f"wider: {path} is not at its registered sha256")
        return 4
    spec = importlib.util.spec_from_file_location("neverrun_e224_wider", path)
    M = importlib.util.module_from_spec(spec)
    sys.dont_write_bytecode = True
    spec.loader.exec_module(M)
    reg_rule = M.never_opened
    M.never_opened = lambda name: "e224" in name.lower()
    data_root = os.path.join(lab, "docs", "reports", "data")
    opened_now = {"data_folders": sorted(d for d in os.listdir(data_root) if reg_rule(d) and not M.never_opened(d)),
                  "lane_folders": sorted("W/out/" + d for d in os.listdir(lanes) if d.startswith(("card-", "data-", "a1", "a2", "a3"))
                                         and os.path.isdir(os.path.join(lanes, d)) and reg_rule(d) and not M.never_opened(d))}
    sp = M.scan(lab, lanes, out)
    S = json.load(open(sp))
    S["kit_wider_scan"] = {"rule": WIDER_RULE, "registered_scanner_sha256": pin, "read_here_never_by_the_registered_scan": opened_now}
    S["never_opened"]["rule"] = "a folder, lane or file name holding 'e224' (E224's own): the kit's wider scan (kit_wider_scan)"
    json.dump(S, open(sp, "w"), indent=1, sort_keys=True)
    M.report(sp, points, out)
    return 0


def one_scan(scan, d, lab, lanes, wide, env):
    """(rc, scan record, report record) of one scan into d (the registered one as the scanner's own subprocesses; the wider one through this
    file's hidden mode, or the stand-in with E224_NR_WIDER=1)"""
    os.makedirs(d, exist_ok=True)
    pts = os.path.join(lab, POINTS_CSV)
    stand = os.environ.get("RB_DESKTEST") == "1" and os.environ.get("E224_NR_SCANNER")
    if wide and not stand:
        r = subprocess.run([sys.executable, "-I", "-B", os.path.abspath(__file__), "wider", "--lab", lab, "--lanes", lanes, "--out", d, "--points", pts],
                           capture_output=True, text=True, env=env)
        open(os.path.join(d, "wider.out"), "w").write(r.stdout + r.stderr)
        rcs = (r.returncode,)
    else:
        e = dict(env, E224_NR_WIDER="1") if wide else env
        r1 = subprocess.run([sys.executable, "-I", "-B", scan, "scan", "--lab", lab, "--lanes", lanes, "--out", d], capture_output=True, text=True, env=e)
        open(os.path.join(d, "scan.out"), "w").write(r1.stdout + r1.stderr)
        r2 = subprocess.run([sys.executable, "-I", "-B", scan, "report", "--scan", os.path.join(d, "scan-e224-reg.json"), "--points", pts, "--out", d],
                            capture_output=True, text=True, env=e)
        open(os.path.join(d, "report.out"), "w").write(r2.stdout + r2.stderr)
        rcs = (r1.returncode, r2.returncode)
    sp, rp = os.path.join(d, "scan-e224-reg.json"), os.path.join(d, "neverrun-e224.json")
    if any(rc != 0 for rc in rcs) or not os.path.exists(sp) or not os.path.exists(rp):
        return max(rcs) or 14, None, None
    return 0, json.load(open(sp)), json.load(open(rp))


def run(d, arm, lab, lanes):
    os.makedirs(d, exist_ok=True)
    try:
        scan, swhy, _ = scanner()
    except ValueError as e:
        print(f"NEVER-RUN-E224 arm {arm}: REFUSED ({e})")
        return 14
    t0 = now()
    env = dict(os.environ, OMP_NUM_THREADS="1", OPENBLAS_NUM_THREADS="1", MKL_NUM_THREADS="1", NUMEXPR_NUM_THREADS="1")
    res = {}
    for name, wide in (("registered", False), ("wider", True)):
        rc, S, R = one_scan(scan, os.path.join(d, name), lab, lanes, wide, env)
        if rc != 0 or S is None:
            print(f"NEVER-RUN-E224 arm {arm}: the {name} scan or its report failed (rc {rc}; {d}/{name}/)")
            return 14
        res[name] = (S, R)
    mine = [q["id"] for q in arm_points(arm)]
    verdict = {}
    for name, (S, R) in res.items():
        v = {x["id"]: x for x in R["points"] if x["arm"] == arm and x["id"] in mine}
        if set(v) != set(mine):
            print(f"NEVER-RUN-E224 arm {arm}: the {name} report does not read every registered point of the arm ({len(v)} of {len(mine)})")
            return 14
        verdict[name] = v
    lab1 = sorted(pid for pid in mine if not all(verdict[n][pid]["never_run"] for n in verdict))
    lit = {n: sorted(pid for pid in mine if not verdict[n][pid]["literal_never_run_REPORTED"]) for n in verdict}
    labels = {"ran_before_points": {arm: lab1}}
    json.dump(labels, open(os.path.join(d, f"labels-e224-{arm}.json"), "w"), indent=1, sort_keys=True)
    Sr, Sw = res["registered"][0], res["wider"][0]
    rec = {"what": f"E224 arm {arm}'s step 6n: the registration's scan and report repeated unchanged, the kit's wider scan, and the judgement "
                   f"(desk/neverrun_card_e224.py)",
           "arm": arm, "card": CARD[arm], "started": t0, "ended": now(), "scanner": swhy, "lab_head": Sr.get("lab_head"),
           "reading": (f"E224.md 4 (dated note 1, {NOTE1}, registered as E224's reading): a point counts as run on its arm's card only by a session "
                       f"record on that card (family L on both cards); desk copies in folders naming no card never count"),
           "scans": {n: {"files_read": res[n][0].get("files_read"), "session_record_files_read": res[n][0].get("session_record_files_read"),
                         "scan_sha256": sha(os.path.join(d, n, "scan-e224-reg.json")), "report_sha256": sha(os.path.join(d, n, "neverrun-e224.json")),
                         "never_opened": res[n][0].get("never_opened"), "n_never_run_of_arm": sum(1 for p in mine if verdict[n][p]["never_run"]),
                         "ran_of_arm": sorted(p for p in mine if not verdict[n][p]["never_run"])} for n in res},
           "kit_wider_scan": Sw.get("kit_wider_scan"), "n_points": len(mine), "n_never_run": len(mine) - len(lab1), "ran_before_labelled": lab1,
           "evidence": {pid: {n: verdict[n][pid].get("evidence") for n in verdict} for pid in lab1},
           "literal_reading_REPORTED": {"what": "E220's registered literal reading, REPORTED beside by E224's scanner: any file counted for the card, a "
                                                "folder naming no card counting for every card; never a label",
                                        "ran_before": lit},
           "rule": "E224.md 4: a registered point either scan finds run on its arm's card - by a session record on that card - is labelled 'ran "
                   "before' and leaves every rule, whatever the date (REPORTED, never a gate)"}
    json.dump(rec, open(os.path.join(d, f"judge-e224-{arm}.json"), "w"), indent=1, sort_keys=True)
    # both scans' reports together in DIR (the collection's step 12 copies DIR/neverrun-e224.json and .txt into the data directory)
    json.dump({"what": "E224's never-run reports at step 6n: the registered scan's (registered) and the kit's wider scan's (wider), each "
                       "desk/neverrun_e224.py's report form", "registered": res["registered"][1], "wider": res["wider"][1]},
              open(os.path.join(d, "neverrun-e224.json"), "w"), indent=1, sort_keys=True)
    open(os.path.join(d, "neverrun-e224.txt"), "w").write(
        "== the registered scan's report (desk/neverrun_e224.py at its registered sha256; E220's, E222's and E224's folders never opened)\n"
        + open(os.path.join(d, "registered", "neverrun-e224.txt")).read()
        + "== the kit's wider scan's report (the same scanner, its never-opened rule narrowed to E224's own names)\n"
        + open(os.path.join(d, "wider", "neverrun-e224.txt")).read())
    line = (f"NEVER-RUN-E224 arm {arm}: {len(mine) - len(lab1)} of {len(mine)} registered points never ran on {CARD[arm]} by session records "
            f"(E224.md 4, dated note 1's reading), in the registered scan and the kit's wider scan (E220's and E222's folders read) both (scans "
            f"{rec['scans']['registered']['scan_sha256'][:12]} / {rec['scans']['wider']['scan_sha256'][:12]}, {Sr.get('files_read')} / "
            f"{Sw.get('files_read')} files, lab {str(Sr.get('lab_head'))[:12]}); ran before, labelled: {', '.join(lab1) if lab1 else 'none'}; "
            f"the literal reading (REPORTED, not a label): {len(mine) - len(lit['registered'])} / {len(mine) - len(lit['wider'])} of {len(mine)} "
            f"never ran")
    open(os.path.join(d, f"judge-e224-{arm}.txt"), "w").write(json.dumps(rec, indent=1, sort_keys=True)[:6000] + "\n" + line + "\n")
    print(line)
    return 0


def check_labels(f, arm):
    try:
        L = json.load(open(f))
        ids = L["ran_before_points"][arm]
        ok = isinstance(ids, list) and all(isinstance(x, str) for x in ids) and set(L["ran_before_points"]) == {arm}
    except (OSError, ValueError, KeyError, TypeError):
        ok, ids = False, None
    mine = {q["id"] for q in arm_points(arm)}
    if not ok or any(x not in mine for x in ids):
        print(f"LABELS-REFUSED: {f} is not arm {arm}'s labels of its registered points")
        return 10
    print(f"LABELS-OK: {len(ids)} label(s) of arm {arm}'s registered points ({', '.join(ids) if ids else 'none'})")
    return 0


def main(a):
    if len(a) >= 2 and a[0] == "check-labels" and len(a) == 4 and a[2] == "--arm" and a[3] in CARD:
        return check_labels(a[1], a[3])
    if len(a) == 8 and a[0] == "run" and a[2] == "--arm" and a[3] in CARD and a[4] == "--lab" and a[6] == "--lanes":
        return run(os.path.abspath(a[1]), a[3], os.path.abspath(a[5]), os.path.abspath(a[7]))
    if len(a) == 9 and a[0] == "wider" and a[1] == "--lab" and a[3] == "--lanes" and a[5] == "--out" and a[7] == "--points":
        return wider(a[2], a[4], a[6], a[8])
    print(__doc__.split("REPORTED, never a gate")[0])
    return 10


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
