#!/usr/bin/env python3
"""E211 (Q204) desk: THE NEVER-RUN RECORD - that rgm211 (its arms gemmLn and gemmLnc) never ran on any card, and where each of E211's rgm136
twins ran before. The search is E206's own scanner (tools/claims-v3/e206/desk/neverrun_e206.py, imported unchanged, its sha256 pinned): every
GEMM host record or host command line of every file under the roots given (gzip read through; scratch clones holding a .git skipped; a simulator
record listed apart). Standard library only.

    python3 -I -B tools/claims-v3/e211/desk/neverrun_e211.py report [--strip PREFIX=LABEL ...] found.json [found.json ...]
        writes desk/neverrun-e211.json and desk/neverrun-e211.txt from the scanner's outputs (each made by neverrun_e206.py scan LABEL DEFAULT TOP...);
        each --strip writes paths under PREFIX as LABEL (the round's lane folders as OUT/), and the account's home is written HOME/

WHAT IS JUDGED: (a) THE SECOND KERNEL: every configuration whose arm starts gemmLn (gemmLn<MB>x<NB>x<KB> or gemmLnc<MB>x<NB>x<KB>) found
anywhere, with its paths; a SPARSITY record on a card would be a run; a command line or argv list in a plan or a registration is not a run and
is named as such by its path; (b) THE TWINS: for each of E211's 12 gemmL configurations (arm, format, random, 1,024 minions, the full chip), the
cards and paths of every record found. The scanner's outputs are the evidence; this report names them.
SPDX-License-Identifier: Apache-2.0
"""
import hashlib
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", "..", "..", ".."))
SCANNER_REL = "tools/claims-v3/e206/desk/neverrun_e206.py"
SCANNER_SHA = "95b290c0b643954ab5b4608d8af8dff440cb24e600d968d2dd53c3deb335c226"
PTS = json.load(open(os.path.join(HERE, "..", "points-e211.json")))
NOT_RUNS = ("/reg-e211/", "/mm-kernel2/", "/critic-kernel2/", "/kit-e211/", "/verify-e211/", "/fix-e211/", "points-e211", "plan.json", "plan.md",
            "e211-draft-runs")


STRIPS = []      # (prefix, label) pairs from --strip PREFIX=LABEL, then the account's home as HOME/: no login or home path is written


def pub(path):
    """a path as the public record writes it"""
    for prefix, label in STRIPS + [(os.path.expanduser("~") + "/", "HOME/")]:
        if path.startswith(prefix):
            return label + path[len(prefix):]
    return path


def roots_summary(roots):
    """the roots by their parent folder and count (folder names are not listed: a work folder's names are no public record)"""
    out = {}
    for r in roots:
        parent = os.path.dirname(pub(os.path.expanduser(r)).rstrip("/"))
        out[parent] = out.get(parent, 0) + 1
    return {k: f"{v} folder(s)" for k, v in sorted(out.items())}


def report(paths):
    if hashlib.sha256(open(os.path.join(REPO, SCANNER_REL), "rb").read()).hexdigest() != SCANNER_SHA:
        sys.exit(f"neverrun_e211: {SCANNER_REL} is not the pinned {SCANNER_SHA}")
    scans = [json.load(open(p)) for p in paths]
    second, twins = {}, {}
    tw_keys = {f"{p['arm']}|{p['format']}|random|1024|0xffffffff": p["id"] for p in PTS["points"] + PTS["smoke"] if p["arm_family"] == "gemmL"}
    for s in scans:
        for key, rec in s["found"].items():
            arm = key.split("|")[0]
            if arm.startswith("gemmLn"):
                e = second.setdefault(key, {"cards": {}, "sim": 0, "how": {}, "paths": [], "scans": []})
                for c, n in rec["cards"].items():
                    e["cards"][c] = e["cards"].get(c, 0) + n
                e["sim"] += rec["sim"]
                for h, n in rec["how"].items():
                    e["how"][h] = e["how"].get(h, 0) + n
                e["paths"] += [pub(x) for x in rec["paths"]]
                e["scans"].append(s["label"])
            if key in tw_keys:
                e = twins.setdefault(tw_keys[key], {"key": key, "cards": {}, "sim": 0, "paths": [], "scans": []})
                for c, n in rec["cards"].items():
                    e["cards"][c] = e["cards"].get(c, 0) + n
                e["sim"] += rec["sim"]
                e["paths"] += [pub(x) for x in rec["paths"]]
                e["scans"].append(s["label"])
    judged = {}
    for key, e in second.items():
        runs = [p for p in e["paths"] if not any(x in p for x in NOT_RUNS)]
        judged[key] = {"records": e, "card_run_evidence": runs,
                       "judgement": "NOT A RUN: every path is a plan, a registration or this lane's own desk work" if not runs else "LOOK: a path outside the plans"}
    never = all(not j["card_run_evidence"] for j in judged.values())
    out = {"what": "E211's never-run record: rgm211's arms (gemmLn, gemmLnc) and the twins' history, by E206's scanner (unchanged)",
           "scanner": {SCANNER_REL: SCANNER_SHA},
           "scans": [{"label": s["label"], "box": s["box"], "roots": roots_summary(s["roots"]), "files_read": s["files_read"],
                      "over_400MB": [pub(x) for x in s["files_over_400MB_skipped"]], "unreadable": s["n_unreadable"], "seconds": s["seconds"]} for s in scans],
           "second_kernel": {"configurations_found": len(second), "judged": judged, "rgm211_never_ran_on_any_card": never},
           "twins": {pid: twins.get(pid, {"cards": {}, "paths": [], "note": "no record found in the roots scanned"}) for pid in sorted(set(tw_keys.values()))}}
    json.dump(out, open(os.path.join(HERE, "neverrun-e211.json"), "w"), indent=1, sort_keys=True)
    open(os.path.join(HERE, "neverrun-e211.json"), "a").write("\n")
    L = ["E211 never-run record (desk; E206's scanner unchanged)"]
    for s in out["scans"]:
        L.append(f"  scan {s['label']} on {s['box']}: {s['files_read']} files, roots {s['roots']}, over 400 MB {len(s['over_400MB'])}, unreadable {s['unreadable']}")
    L.append(f"THE SECOND KERNEL: {len(second)} gemmLn/gemmLnc configurations named anywhere; rgm211 never ran on any card: {never}")
    for key, j in sorted(judged.items()):
        L.append(f"  {key}: {j['judgement']}; paths {j['records']['paths'][:3]}")
    L.append("THE TWINS (where each gemmL configuration ran before E211):")
    for pid, e in out["twins"].items():
        L.append(f"  {pid} {e.get('key', '')}: cards {e.get('cards')}; sim {e.get('sim', 0)}; paths {e.get('paths', [])[:3]}")
    open(os.path.join(HERE, "neverrun-e211.txt"), "w").write("\n".join(L) + "\n")
    print("\n".join(L))


if __name__ == "__main__":
    args = sys.argv[1:]
    if args[:1] == ["report"]:
        args = args[1:]
        while args[:1] == ["--strip"] and len(args) > 1:
            pre, _, lab = args[1].partition("=")
            STRIPS.append((pre, lab))
            args = args[2:]
        if args:
            report(args)
            sys.exit(0)
    sys.exit(__doc__)
