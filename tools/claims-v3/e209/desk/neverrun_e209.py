#!/usr/bin/env python3
"""E209 (Q202) desk: which of E209's points never ran ON THIS CARD (aifoundry2 card 0) - a search of every folder of ours on aifoundry2 for the
names of E209's 29 shapes (the token gemmL<MB>x<NB>x<KB> not followed by a digit: MM1-v2's own scan pattern, e209_v2.py), each hit classed by
where it sits. Standard library only; reads only; gzip read through.

    python3 -I -B tools/claims-v3/e209/desk/neverrun_e209.py scan --lab <the lab at GitHub main> --out-root <the round's lane folders>
                --work <the lab account's work folder> --json <found.json>
    python3 -I -B tools/claims-v3/e209/desk/neverrun_e209.py report <found.json> [--e207-points <points-e207.json>]
                writes desk/neverrun-e209.json and prints desk/neverrun-e209.txt

THE CLASSES (by path):
  COUNTED (a run on aifoundry2 card 0): the lab's data folders (docs/reports/data/<dir>) not named for another card (a folder naming none counts
    as this card's: conservative), MM1-v2's vendored copies of E208's aifoundry2 sessions, the round's card and data lanes of this card
    (a2-*, card-a2*, card-e190, card-e194, card-e200, card-e208*, data-e208* paths naming a2c0) and any other card lane whose box is not known
    (card-* not listed under OTHER CARD: conservative), and the lab account's work folders (a path naming another card excepted).
  OTHER CARD (REPORTED): data folders and card lanes of aifoundry3 or aifoundry1 (named so, or listed: E189, E191, E192, E193, E195-E199, E202,
    E206, E207 lanes).
  DESK ONLY (dismissed, listed): every other path - registrations, models, kits, desk tests and their stand-in doubles (verify-e207's finding
    on E207's step 6n: a desk lane's double is not a run).
  SUBTRACTED: E209's own folders (tools/claims-v3/e209 and every lane named for e209).
  NOT READ: directories holding a .git entry (scratch clones: the lab is read at its source), and the model session's folders under the work
    folder (ee-*: the orchestrator's rule of 23:18:35 PST Mon 16 Nov 2026; its released sessions are in the lab's committed data, read there).
A POINT NEVER RAN ON THIS CARD when no COUNTED hit names its shape (any format, data kind or mask): the stronger claim, MM1-v2's.
SPDX-License-Identifier: Apache-2.0
"""
import gzip
import json
import os
import re
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", "..", "..", ".."))
MAX_BYTES = 400 * 2 ** 20
OTHER_LANES = re.compile(r"^(a3-|a1c0-|a1c1-|a1-|card-a3|card-a1|card-e189$|card-e191|card-e192$|card-e193$|card-e195$|card-e196$|card-e197$|"
                         r"card-e198|card-e199$|card-e202$|card-e206|card-e207|card-e210|card-e211)")
A2_LANES = re.compile(r"^(a2-|card-a2|card-e190$|card-e194$|card-e200$|card-e208)")
OWN = re.compile(r"e209")


def shapes():
    pts = json.load(open(os.path.join(HERE, "..", "points-e209.json")))
    return sorted({p["arm"] for p in pts["points"]}), pts


def classify(label, rel):
    """(class, card) for a hit's path relative to its root"""
    p = rel.replace("\\", "/")
    if label == "lab":
        if p.startswith("tools/claims-v3/e209/"):
            return "SUBTRACTED", None
        if p.startswith("docs/reports/data/"):
            d = p.split("/")[3] if len(p.split("/")) > 3 else ""
            if "aifoundry3" in d or re.search(r"(^|-)a3-", d):
                return "OTHER CARD", "aifoundry3 card 0"
            if "aifoundry1" in d or "a1c0" in d or "a1c1" in d:
                return "OTHER CARD", "aifoundry1"
            return "COUNTED", "aifoundry2 card 0 (a data folder naming no other card)"
        if p.startswith("tools/matmul/mm1/v2/inputs/e208/a2c0-"):
            return "COUNTED", "aifoundry2 card 0 (MM1-v2's vendored copy of E208's data)"
        return "DESK ONLY", None
    if label == "out":
        lane = p.split("/")[0]
        if OWN.search(lane):
            return "SUBTRACTED", None
        if lane.startswith("data-e208"):
            return ("COUNTED", "aifoundry2 card 0 (E208's data lane)") if "a2c0" in p else ("OTHER CARD", "aifoundry1 (E208's data lane)")
        if A2_LANES.match(lane):
            return "COUNTED", "aifoundry2 card 0 (a card lane of this card)"
        if OTHER_LANES.match(lane):
            # another card's lane: only its run folders are runs (rb-*, raw, session); its scans, logs and work files are desk files
            parts = p.split("/")
            if len(parts) > 1 and (parts[1].startswith("rb-") or "raw" in p or "/session" in p):
                return "OTHER CARD", "aifoundry3 or aifoundry1 (a card lane of another card: its run folders)"
            return "DESK ONLY", None
        if lane.startswith("card-"):
            return "COUNTED", "a card lane whose box is not listed (conservative)"
        return "DESK ONLY", None
    if label == "work":
        if "aifoundry3" in p or "aifoundry1" in p or "a1c1" in p or "a1c0" in p:
            return "OTHER CARD", "named for another card"
        return "COUNTED", "the lab account's work folder on aifoundry2 (conservative)"
    return "DESK ONLY", None


def scan(lab, out_root, work, jpath):
    toks, _ = shapes()
    pat = re.compile(rb"gemmL(" + b"|".join(t[5:].encode() for t in toks) + rb")(?![0-9])")
    roots = [("lab", lab), ("out", out_root)]
    not_read = []
    if work and os.path.isdir(work):
        for d in sorted(os.listdir(work)):
            full = os.path.join(work, d)
            if d.startswith("ee-"):
                not_read.append(f"<work>/{d}")
                continue
            roots.append(("work", full))
    hits, nfiles, big, unread, git_skipped, big_paths = [], {}, 0, 0, [], []
    t0 = time.strftime("%Y-%m-%d %H:%M:%S %Z")
    for label, top in roots:
        base = work if label == "work" else top
        for dp, dns, fns in os.walk(top):
            if ".git" in dns or ".git" in fns:
                if dp != top or label != "lab":
                    git_skipped.append(f"<{label}>/{os.path.relpath(dp, base)}")
                    dns[:] = []
                    continue
                dns[:] = [d for d in dns if d != ".git"]
            dns.sort()
            for fn in sorted(fns):
                fp = os.path.join(dp, fn)
                try:
                    if os.path.islink(fp) or not os.path.isfile(fp):
                        continue
                    if os.path.getsize(fp) > MAX_BYTES:
                        big += 1
                        big_paths.append(f"<{label}>/{os.path.relpath(fp, base)}" if label != "work" else f"<work>/{os.path.relpath(fp, work).split(os.sep)[0]}/...")
                        continue
                    data = open(fp, "rb").read()
                    if fn.endswith(".gz"):
                        try:
                            data = gzip.decompress(data)
                        except (OSError, EOFError):
                            pass
                except OSError:
                    unread += 1
                    continue
                nfiles[label] = nfiles.get(label, 0) + 1
                found = {m.group(0).decode() for m in pat.finditer(data)}
                if found:
                    rel = os.path.relpath(fp, base)
                    if label == "work":
                        rel = os.path.relpath(fp, work)
                    cls, card = classify(label, rel)
                    hits.append({"root": label, "path": rel, "shapes": sorted(found), "class": cls, "card": card})
    res = {"what": "every hit of E209's 29 shape names in the folders of ours on aifoundry2, classed (neverrun_e209.py's docstring)",
           "started": t0, "ended": time.strftime("%Y-%m-%d %H:%M:%S %Z"), "pattern": pat.pattern.decode(),
           "roots": {"lab": "<lab> = the lab at GitHub main (a scratch clone)", "out": "<out> = the round's lane folders", "work": "<work>/* = the lab account's work folders"},
           "files_read": nfiles, "over_400MB": big, "over_400MB_paths": big_paths, "unreadable": unread, "not_read_model_session_folders": not_read,
           "not_read_git_dirs": len(git_skipped), "hits": hits}
    json.dump(res, open(jpath, "w"), indent=1, sort_keys=True)
    print(f"files {nfiles}, hits {len(hits)}, over 400 MB {big}, unreadable {unread}, git dirs skipped {len(git_skipped)}, not read {not_read}")


def report(paths, e207_points=None):
    toks, pts = shapes()
    found = [json.load(open(p)) for p in paths]
    by = {t: {"COUNTED": [], "OTHER CARD": [], "DESK ONLY": [], "SUBTRACTED": []} for t in toks}
    for f in found:
        for h in f["hits"]:
            # a work-folder path is named by its first folder only in the report (the found file keeps it whole)
            path = h["path"] if h["root"] != "work" else h["path"].split("/")[0] + "/..."
            cls, card = classify(h["root"], h["path"])     # classed here, by this file's rules, whatever the scan wrote
            for t in h["shapes"]:
                by[t][cls].append(f"<{h['root']}>/{path}" + (f" ({card})" if card else ""))
    e207 = {}
    if e207_points:
        E = json.load(open(e207_points))
        for q in E.get("points", []):
            key = (q.get("arm"), q.get("fmt") or q.get("format"), q.get("kind"), int(str(q.get("mask") or q.get("shire_mask") or "0xffffffff"), 16))
            e207[key] = q.get("id")
    rows, never = [], 0
    for p in pts["points"]:
        t = p["arm"]
        nr = len(by[t]["COUNTED"]) == 0
        never += nr
        key = (t, p["fmt"], p["kind"], p["mask_int"])
        rows.append({"id": p["id"], "shape": t, "fmt": p["fmt"], "kind": p["kind"], "mask": p["mask_host"], "never_ran_on_this_card": nr,
                     "shape_on_another_card": sorted({x.split(" (")[0].split("/")[4] if x.startswith("<lab>/docs/reports/data/") else x.split("/")[1]
                                                      for x in by[t]["OTHER CARD"]}),
                     "same_point_planned_in_e207": e207.get(key)})
    out = {"experiment": "E209", "what": "E209's points never run on aifoundry2 card 0 (desk; neverrun_e209.py)", "scans": [{k: f[k] for k in f if k != "hits"} for f in found],
           "shapes_detail": {t: {"counted": by[t]["COUNTED"], "other_card": by[t]["OTHER CARD"][:20], "n_other_card": len(by[t]["OTHER CARD"]),
                          "n_desk_only": len(by[t]["DESK ONLY"]), "desk_only_sample": by[t]["DESK ONLY"][:8], "n_subtracted": len(by[t]["SUBTRACTED"])}
                      for t in toks},
           "points": rows, "never_ran_on_this_card": never, "of": len(rows),
           "shapes_never_on_this_card": sum(1 for t in toks if not by[t]["COUNTED"]), "n_shapes": len(toks),
           "e207_overlap_REPORTED": [r["id"] for r in rows if r["same_point_planned_in_e207"]]}
    json.dump(out, open(os.path.join(HERE, "neverrun-e209.json"), "w"), indent=1, sort_keys=True)
    L = [f"E209 never-run on aifoundry2 card 0: {never} of {len(rows)} points never ran on this card; {out['shapes_never_on_this_card']} of {len(toks)} "
         f"shapes have no counted hit (any format, data kind or mask)"]
    for f in found:
        L.append(f"  scan {f['started']} - {f['ended']}: files read {f['files_read']}; hits {len(f['hits'])}; over 400 MB {f['over_400MB']}; unreadable "
                 f"{f['unreadable']}; git dirs not read {f['not_read_git_dirs']}; model session folders not read {f['not_read_model_session_folders']}")
    for t in toks:
        d = out["shapes_detail"][t]
        L.append(f"  {t}: counted {len(d['counted'])}" + (f" {d['counted'][:3]}" if d["counted"] else "") + f"; other card {d['n_other_card']}; "
                 f"desk only {d['n_desk_only']}; subtracted {d['n_subtracted']}")
    L.append("  points also planned in E207 (aifoundry3; REPORTED, not a run on this card): " + (", ".join(f"{r['id']}={r['same_point_planned_in_e207']}"
                                                                                                 for r in rows if r["same_point_planned_in_e207"]) or "none"))
    L.append("  points whose shape ran on another card (REPORTED): " + (", ".join(f"{r['id']} {r['shape_on_another_card']}" for r in rows
                                                                                  if r["shape_on_another_card"]) or "none"))
    txt = "\n".join(L) + "\n"
    open(os.path.join(HERE, "neverrun-e209.txt"), "w").write(txt)
    sys.stdout.write(txt)


def main():
    a = sys.argv[1:]
    if a and a[0] == "scan":
        kv = dict(zip(a[1::2], a[2::2]))
        scan(kv["--lab"], kv["--out-root"], kv.get("--work"), kv["--json"])
    elif a and a[0] == "report":
        e207 = None
        files = []
        it = iter(a[1:])
        for x in it:
            if x == "--e207-points":
                e207 = next(it)
            else:
                files.append(x)
        report(files, e207)
    else:
        sys.exit(__doc__)


if __name__ == "__main__":
    main()
