#!/usr/bin/env python3
"""E211's never-run search REPEATED right before the card day's first card command (Q204, lane kit-e211, Tue 17 Nov 2026, before any E211
datum; E211.md section 4: "The card lane re-checks the never-run list right before its first card command (E207's twins will have run by
then: E211 books no card before E207's data commit)"). Runbook step 6n (rb/s06n_neverrun_e211.sh) calls it at the desk. Standard library only;
it runs E206's scanner UNCHANGED (tools/claims-v3/e206/desk/neverrun_e206.py, sha256 95b290c0..., the scanner E211.md section 4 names) and
judges its outputs as the registration's record does (desk/neverrun_e211.py: rgm211's arms gemmLn and gemmLnc, and where each gemmL twin ran),
reading the scanner's own split of every record into a card record or a simulator record.

    /usr/bin/python3 -I -B tools/claims-v3/e211/desk/neverrun_card_e211.py desk DIR       the desk's three scans -> DIR/found-*.json
    /usr/bin/python3 -I -B tools/claims-v3/e211/desk/neverrun_card_e211.py report DIR [--a3-not-searched WHY]
                                      the judgement -> DIR/neverrun-e211-card.json and .txt; its last line "NEVER-RUN-E211 ..."

THE ROOTS (the registration's, and aifoundry3's box tree): at the desk (aifoundry2) the lab clone at its HEAD (every top-level entry but .git;
under tools/claims-v3 every entry but e211 and sealed-e211, E211's own committed folders, which hold its plans, its desk tests' logs and its
simulator check's record, never a run before E211), the round's lane folders OUT (named by E211_ROUND_OUT; every top-level folder but E211's own
lanes, <role>-e211[<suffix>], and E211's two design lanes mm-kernel2 and critic-kernel2, whose files are plans and desk builds that never ran:
the registration named them not runs) and HOME/claude/work (every folder but the model session's ee-*: the round's rule since 23:18 PST Mon 16
Nov 2026, no lab lane reads their uncommitted session folders; their released sessions are committed in the lab and read there); on aifoundry3
(rb/s06n's remote read, the same scanner sent on stdin, at nice 19 and idle IO, nothing written there) every folder of HOME/aifoundry/build but
E211's own (e211, e211rgm), every folder of HOME/claude/work but ee-*, and HOME/claude/et-soc1-prototyping/build where it exists, written by
s06n to DIR/found-aifoundry3.json. The scanner's rules are unchanged: what counts as a record or a command, the card read from the path, a
record from the simulator (a "ghz" under 0.05, or a line or path naming sys_emu, sysemu, sim-check, sim-runs or simulator) listed apart and
never a card run (the kit's own simulator check on aifoundry3, HOME/claude/work/q204-kit-e211, is such: its records carry "ghz" 0).
THE JUDGEMENT (REPORTED, never a gate): (a) THE SECOND KERNEL: every gemmLn or gemmLnc configuration found with a card record outside the folders
left out: "rgm211 on a card before E211: none" or the keys and paths (a dated note before the data commit, and the orchestrator told: blindness
for those points is gone); simulator records and command lines are named apart; (b) THE TWINS: for each of E211's gemmL configurations
(points-e211.json: the twelve twins and the smoke's s01), the cards and the paths of every record found (E206 arm A's four twins and, once E207
has run, E207's three are expected there, labelled as the registration says). RB_DESKTEST=1 lets E211_NR_LAB, E211_NR_OUT and E211_NR_HOMEW name
stand-in roots (the runbook's desk test only). SPDX-License-Identifier: Apache-2.0
"""
import hashlib
import json
import os
import re
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
E = os.path.normpath(os.path.join(HERE, ".."))
REPO = os.path.normpath(os.path.join(E, "..", "..", ".."))
SCANNER = os.path.join(REPO, "tools/claims-v3/e206/desk/neverrun_e206.py")
SCANNER_PIN = "95b290c0b643954ab5b4608d8af8dff440cb24e600d968d2dd53c3deb335c226"
PTS = os.path.join(E, "points-e211.json")
OWN_LANE = re.compile(r"^[a-z0-9]+-e211(?![0-9])[a-z0-9-]*$")   # E211's own lanes' folders by the round's naming: <role>-e211[<suffix>]
DESIGN_LANES = ("mm-kernel2", "critic-kernel2")                  # E211's design lanes (plans and desk builds; never a run: E211.md 4)
LAB_OWN = ("tools/claims-v3/e211", "tools/claims-v3/sealed-e211")


def sha(p):
    with open(p, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def ts():
    return time.strftime("%Y-%m-%d %H:%M:%S %Z")


def scanner():
    if sha(SCANNER) != SCANNER_PIN:
        raise SystemExit(f"NEVERRUN-REFUSED: E206's scanner is not at its pin {SCANNER_PIN[:12]}")
    sys.path.insert(0, os.path.dirname(SCANNER))
    import neverrun_e206 as NR  # noqa: E402 -- E206's scanner, unchanged (its scan mode imports nothing of the lab)
    return NR


def roots():
    r = {"lab": REPO, "out": os.environ.get("E211_ROUND_OUT") or None, "homew": os.path.expanduser("~/claude/work")}
    if os.environ.get("RB_DESKTEST") == "1":
        for k, v in (("lab", "E211_NR_LAB"), ("out", "E211_NR_OUT"), ("homew", "E211_NR_HOMEW")):
            if os.environ.get(v):
                r[k] = os.environ[v]
    return r


def lab_tops(lab):
    """The lab's top-level entries but .git, with tools/ and tools/claims-v3/ opened one level so E211's own folders stay out."""
    tops, left = [], []
    for d in sorted(os.listdir(lab)):
        if d == ".git":
            continue
        p = os.path.join(lab, d)
        if d != "tools" or not os.path.isdir(p):
            tops.append(p)
            continue
        for t in sorted(os.listdir(p)):
            q = os.path.join(p, t)
            if t != "claims-v3" or not os.path.isdir(q):
                tops.append(q)
                continue
            for c in sorted(os.listdir(q)):
                rel = f"tools/claims-v3/{c}"
                if rel in LAB_OWN:
                    left.append(rel)
                else:
                    tops.append(os.path.join(q, c))
    return tops, left


def desk(d):
    NR = scanner()
    r = roots()
    if not r["out"] or not os.path.isdir(r["out"]):
        print("NEVERRUN-REFUSED: E211_ROUND_OUT does not name the round's lane folders")
        return 10
    os.makedirs(d, exist_ok=True)
    left = {}
    lt, left["LAB"] = lab_tops(r["lab"])
    outs = sorted(os.listdir(r["out"]))
    left["OUT"] = [x for x in outs if OWN_LANE.match(x) or x in DESIGN_LANES]
    ot = [os.path.join(r["out"], x) for x in outs if x not in left["OUT"]]
    hw = sorted(os.listdir(r["homew"])) if os.path.isdir(r["homew"]) else []
    left["HOME/claude/work"] = [x for x in hw if x.startswith("ee-")]
    ht = [os.path.join(r["homew"], x) for x in hw if not x.startswith("ee-")]
    for label, tops in (("lab-head", lt), ("round-lanes", ot), ("aifoundry2-work", ht)):
        t0 = time.time()
        res = NR.scan(label, "unknown", tops)
        with open(os.path.join(d, f"found-{label}.json"), "w") as f:
            json.dump(res, f, indent=0, default=str)
        print(f"{ts()} scan {label}: {len(tops)} roots, {res['files_read']} files, {len(res['found'])} configurations, "
              f"{round(time.time() - t0, 1)} s", flush=True)
    with open(os.path.join(d, "left-out.json"), "w") as f:
        json.dump(left, f, indent=1)
    print(f"SCANNED-DESK {ts()}: left out (E211's own and its design lanes, the model session's folders): "
          f"{ {k: len(v) for k, v in left.items()} }")
    return 0


def pub(path, r):
    """A path as the public record writes it: the lab as LAB/, the round's lanes as OUT/, the account's home as HOME/."""
    for pre, lab in ((r["lab"], "LAB"), (r["out"] or "\0", "OUT"), (os.path.expanduser("~"), "HOME")):
        if pre and path.startswith(pre.rstrip("/") + "/"):
            return lab + "/" + path[len(pre.rstrip("/")) + 1:]
    return re.sub(r"^/home/[^/]+/", "HOME/", path)


def report(d, a3_not=None):
    r = roots()
    pts = json.load(open(PTS))
    files = sorted(f for f in os.listdir(d) if f.startswith("found-") and f.endswith(".json"))
    scans = [json.load(open(os.path.join(d, f))) for f in files]
    a3 = any(s.get("label", "").startswith("aifoundry3") for s in scans)
    twin_keys = {f"{p['arm']}|{p['format']}|random|{p['minions']}|{p['shire_mask']}": p["id"]
                 for p in pts["points"] + pts["smoke"] if p["arm_family"] == "gemmL"}
    second, twins = {}, {}
    for s in scans:
        for key, rec in s["found"].items():
            arm = key.split("|")[0]
            hit = None
            if arm.startswith("gemmLn"):
                hit = second.setdefault(key, {"cards": {}, "sim": 0, "how": {}, "paths": [], "scans": []})
            elif key in twin_keys:
                hit = twins.setdefault(twin_keys[key], {"key": key, "cards": {}, "sim": 0, "how": {}, "paths": [], "scans": []})
            if hit is None:
                continue
            for c, n in rec["cards"].items():
                hit["cards"][c] = hit["cards"].get(c, 0) + n
            hit["sim"] += rec["sim"]
            for h, n in rec["how"].items():
                hit["how"][h] = hit["how"].get(h, 0) + n
            hit["paths"] += [pub(x, r) for x in rec["paths"]]
            hit["scans"].append(s["label"])
    on_card = {k: v for k, v in second.items() if v["cards"]}
    out = {"what": "E211's never-run search repeated before the first card command (desk/neverrun_card_e211.py; E206's scanner unchanged)",
           "scanner": {"tools/claims-v3/e206/desk/neverrun_e206.py": SCANNER_PIN}, "when": ts(),
           "scans": [{"label": s["label"], "box": s["box"], "files_read": s["files_read"], "n_unreadable": s["n_unreadable"],
                      "over_400MB": len(s["files_over_400MB_skipped"]), "seconds": s["seconds"], "roots": len(s["roots"])} for s in scans],
           "left_out": json.load(open(os.path.join(d, "left-out.json"))) if os.path.exists(os.path.join(d, "left-out.json")) else {},
           "aifoundry3": "searched" if a3 else f"NOT SEARCHED ({a3_not or 'no aifoundry3 scan in the folder'})",
           "second_kernel": {"configurations_found": len(second), "with_a_card_record": sorted(on_card), "records": second},
           "twins": {pid: twins.get(pid, {"cards": {}, "paths": [], "note": "no record found in the roots scanned"}) for pid in sorted(set(twin_keys.values()))}}
    with open(os.path.join(d, "neverrun-e211-card.json"), "w") as f:
        json.dump(out, f, indent=1, sort_keys=True)
        f.write("\n")
    L = [f"E211 never-run search, repeated before the first card command ({out['when']}; E206's scanner unchanged)"]
    for s in out["scans"]:
        L.append(f"  scan {s['label']} on {s['box']}: {s['roots']} roots, {s['files_read']} files, unreadable {s['n_unreadable']}, over 400 MB {s['over_400MB']}")
    L.append(f"  left out: {out['left_out']}; aifoundry3 {out['aifoundry3']}")
    L.append(f"THE SECOND KERNEL: {len(second)} gemmLn/gemmLnc configuration(s) found; with a card record: {len(on_card)}")
    for k, v in sorted(second.items()):
        L.append(f"  {k}: cards {v['cards']}; simulator {v['sim']}; how {v['how']}; paths {v['paths'][:3]}")
    L.append("THE TWINS (where each gemmL configuration ran before E211's session):")
    ran_before = []
    for pid, v in out["twins"].items():
        L.append(f"  {pid} {v.get('key', '')}: cards {v.get('cards')}; simulator {v.get('sim', 0)}; paths {v.get('paths', [])[:3]}")
        if v.get("cards"):
            ran_before.append(pid)
    line = (f"NEVER-RUN-E211 rgm211 on a card before E211: {'none' if not on_card else ', '.join(sorted(on_card))}; gemmLn/gemmLnc "
            f"configurations found {len(second)} (simulator records {sum(v['sim'] for v in second.values())}); twins with a card record: "
            f"{len(ran_before)} of {len(out['twins'])}; aifoundry3 {'searched' if a3 else 'NOT SEARCHED'}")
    L.append(line)
    with open(os.path.join(d, "neverrun-e211-card.txt"), "w") as f:
        f.write("\n".join(L) + "\n")
    print("\n".join(L))
    return 0


def main(argv):
    if len(argv) >= 2 and argv[0] == "desk":
        return desk(argv[1])
    if len(argv) >= 2 and argv[0] == "report":
        a3n = argv[argv.index("--a3-not-searched") + 1] if "--a3-not-searched" in argv else None
        return report(argv[1], a3n)
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
