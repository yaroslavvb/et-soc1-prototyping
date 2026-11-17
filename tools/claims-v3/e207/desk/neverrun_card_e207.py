#!/usr/bin/env python3
"""E207's never-run search REPEATED right before the card day's first card command (Q199; lane kit-e207, Mon 16 Nov 2026; fixed by lane
fix-e207, Tue 17 Nov 2026, before any E207 datum: E207.md amendment A1 items 1 to 4 and 9, answering verify-e207's findings 1 to 4 and note 13).
Runbook step 6n (rb/s06n_neverrun_e207.sh) calls it at the desk. Standard library only. It runs E206's scanner UNCHANGED (tools/claims-v3/e206/
desk/neverrun_e206.py, sha256 95b290c0...: its scan() over every folder, and its own line rule scan_line() where a folder holding a record of an
E207 point is walked again to find every such record) and the registration's matching UNCHANGED (desk/neverrun_e207.py, run from a copy beside a
copy of points-e207.json in the step's own folder, both checked against SHA256SUMS-e207-registration first, since that script writes its report
beside itself and the committed report must never be overwritten).

    /usr/bin/python3 -I -B tools/claims-v3/e207/desk/neverrun_card_e207.py desk DIR          the desk's scans -> DIR/found-desk-*.json
    /usr/bin/python3 -I -B tools/claims-v3/e207/desk/neverrun_card_e207.py report DIR [--a3 RAW --a3-excluded EXCL] [--a3-not-searched WHY]
                                                                                           the counted records, the registered matching, the dating,
                                                                                           the words

WHAT IS READ, AND HOW EACH PLACE COUNTS (E207.md A1 item 1, stated before any datum):
  COUNTED (a record there is a card run): the lab's data directories (docs/reports/data/<dir>, each scanned on its own); in the round's lane
    folders OUT (E207_ROUND_OUT), the card and data lanes' folders: card-*, data-*, and the earlier rounds' card lanes (a1c0-, a1c1-, a2-, a3-
    followed by <exp>-<what> or q<round>, and q<round>-rb*); HOME/claude/work, every top-level entry but the model session's experiment folders;
    aifoundry3's run folders (rb/s06n's remote read, E207's own build/e207 subtracted).
  DISMISSED, AND LISTED WITH THEIR PATHS (a desk test's double, a kit's log, a plan: never a card run): every other folder of OUT (the desk lanes of
    every experiment: reg-, kit-, verify-, fix-, land-, ready-, scores-, reduce-, mm-, and the rest) and OUT's top-level files; the lab outside its
    data directories (code, kits' logs, a simulator check). verify-e207's finding 1: another experiment's desk test (E209's, E211's) prints records
    of E207's points by the thousand.
  SUBTRACTED (E207's own: never a run "before" E207): OUT folders named <role>-e207[<suffix>]; tools/claims-v3/e207 in the lab (note 13); build/e207
    on aifoundry3.
  NOT READ: HOME/claude/work/ee-*/ (the model session's experiment folders: the orchestrator's rule of 23:18:35 PST Mon 16 Nov 2026 bars every lab
    lane from its uncommitted session folders, finding 4; its released sessions are committed in the lab and read there), except E208's planned
    arms, ee-1116-mmsweep/src/arms.json, read as the registration read them; aifoundry1's own folders (as registered).
WHEN A COUNTED RECORD RAN (E207.md A1 item 2, findings 2 and 3): "ran before" means a card record of the point, or of its case in any data kind,
dated BEFORE MM1-v1's freeze, 21:14:57 PST Mon 16 Nov 2026 (epoch 1794892497; commit 25d2e74e). Every counted record of an E207 point or case is
found again, path by path, and dated from: (1) a session's start epoch in its path (build/eNNN/T<T0>-..., sessions/<T0>-...): before or after the
freeze by that T0; else (2), in the lab, the commit that added its data directory (at or before the freeze: before) or the directory's own date
(before 16 Nov 2026: before; 17 Nov 2026 or later: after); else (3) the file's last write at or before the freeze (before). Nothing else proves a
date: such a record is TO DATE (the card lane reads its session's own start record for the dated note; one it cannot read counts as before). A
point (or case) is RAN BEFORE if any record of it is before, TO DATE if none is before and one is to date, AFTER THE FREEZE if every record is
after: REPORTED, never a label (MM1-v1, F1 and F2 were all frozen before it), the point stays in every rule. E208's planned arms at the
registered bytes (b55f5e13..., planned in the proposal posted 18:25:03 PST Mon 16 Nov 2026) count as before; at other bytes, as to date.
THE OUTPUT: DIR/reg/desk/neverrun-e207.json (the registration's form, on the counted records), DIR/neverrun-e207-card.txt (the words),
DIR/ranbefore-e207.json (every place, its class, the dated paths, and the labels proposed: the RAN BEFORE and TO DATE points, and the cases that
ran before or are to date while their points never ran), and the last line
  "NEVER-RUN <n> of 53 points, <m> of 47 cases[; RAN BEFORE: <ids>][; CASE RAN BEFORE: <cases>][; TO DATE: <ids or cases>][; AFTER THE FREEZE
   (REPORTED, kept): <ids>][; DESK-ONLY (dismissed): <ids>][; aifoundry3 NOT SEARCHED]".
REPORTED: it changes no gate. If the dating itself fails, every counted point that is not never-run is labelled RAN BEFORE and the words say so.
Every path written is in the public form (LAB, OUT, HOME; never a home folder). RB_DESKTEST=1 lets E207_NR_LAB, E207_NR_OUT, E207_NR_HOMEW and
E207_NR_ARMS name stand-in roots (the runbook's desk test only). SPDX-License-Identifier: Apache-2.0
"""
import copy
import gzip
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
E = os.path.normpath(os.path.join(HERE, ".."))
REPO = os.path.normpath(os.path.join(E, "..", "..", ".."))
SCANNER = os.path.join(REPO, "tools/claims-v3/e206/desk/neverrun_e206.py")
SCANNER_PIN = "95b290c0b643954ab5b4608d8af8dff440cb24e600d968d2dd53c3deb335c226"
REG_LIST = os.path.join(E, "SHA256SUMS-e207-registration")
ROOTS = {"lab": REPO, "out": None, "homew": os.path.expanduser("~/claude/work"),
         "arms": os.path.expanduser("~/claude/work/ee-1116-mmsweep/src/arms.json")}
ARMS_PIN = "b55f5e13a138167f28c53b0db991e5ee9772ac0b70b9bd71876b5925359cb0b7"
OWN_LANE = re.compile(r"^[a-z0-9]+-e207(?![0-9])[a-z0-9]*$")   # E207's own lanes' folders by the round's naming: <role>-e207[<suffix>]
DATA_LANE = re.compile(r"^(card|data)-|^(a1c0|a1c1|a2|a3)-(e[0-9]+-|q[0-9]+$)|^q[0-9]+[a-z0-9]*-rb")   # card and data lanes, of every round
BARRED_HOMEW = re.compile(r"^ee-")                              # the model session's experiment folders (never read but E208's arms)
FREEZE_EPOCH = 1794892497                                       # 21:14:57 PST Mon 16 Nov 2026: MM1-v1's freeze (25d2e74e), E207.md section 0
FREEZE_TEXT = "21:14:57 PST Mon 16 Nov 2026 (MM1-v1's freeze, 25d2e74e)"
T0_RE = re.compile(r"(?:^|/)T?(1[7-9][0-9]{8})(?=[-/])")         # a session's start epoch at the head of a path segment
DATADIR_RE = re.compile(r"^docs/reports/data/([0-9]{4}-[0-9]{2}-[0-9]{2})-[^/]+")


def sha(p):
    with open(p, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def pub(path):
    """a path as a public file may show it (E206's form): a lane's clone of the lab as LAB, the round's lane folders as OUT, the home folder as HOME"""
    path = re.sub(r"^.*/work/clone(?=/|$)", "LAB", str(path))
    path = re.sub(r"^.*?/out(?=/|$)", "OUT", path)
    path = path.replace(os.path.expanduser("~"), "HOME")
    path = re.sub(r"^/home/[^/]+", "HOME", path)
    return path.replace("~", "HOME")


def pt(t):
    return subprocess.run(["date", "-d", f"@{int(t)}", "+%Y-%m-%d %H:%M:%S %Z"], capture_output=True, text=True,
                          env={"TZ": "America/Los_Angeles"}).stdout.strip() if t is not None else "unknown"


def ts():
    return subprocess.run(["date", "+%Y-%m-%d %H:%M:%S %Z"], capture_output=True, text=True, env={"TZ": "America/Los_Angeles"}).stdout.strip()


def roots():
    """The roots: the lab clone this file sits in, the round's lane folders (E207_ROUND_OUT, which the card lane sets to the round's OUT;
    required), HOME/claude/work and E208's planned arms there."""
    r = dict(ROOTS)
    r["out"] = os.environ.get("E207_ROUND_OUT") or None
    if os.environ.get("RB_DESKTEST") == "1":
        for k, v in (("lab", "E207_NR_LAB"), ("out", "E207_NR_OUT"), ("homew", "E207_NR_HOMEW"), ("arms", "E207_NR_ARMS")):
            if os.environ.get(v):
                r[k] = os.environ[v]
    return r


def scanner():
    if sha(SCANNER) != SCANNER_PIN:
        raise SystemExit(f"NEVERRUN-REFUSED: E206's scanner is not at its pin {SCANNER_PIN[:12]}")
    sys.path.insert(0, os.path.dirname(SCANNER))
    import neverrun_e206 as NR  # noqa: E402 -- E206's scanner, unchanged (its scan mode imports nothing of the lab)
    return NR


def empty(label):
    return {"label": label, "box": "", "default_card": "unknown", "roots": [], "files_read": 0, "files_over_400MB_skipped": [], "unreadable": [],
            "n_unreadable": 0, "seconds": 0.0, "found": {}}


def merge(label, scans):
    """several scans' counts summed, key by key and card by card (the scanner's own form)"""
    out = empty(label)
    for s in scans:
        out["box"] = out["box"] or s.get("box", "")
        out["roots"] += s.get("roots", [])
        out["files_read"] += s.get("files_read", 0)
        out["files_over_400MB_skipped"] += s.get("files_over_400MB_skipped", [])
        out["n_unreadable"] += s.get("n_unreadable", 0)
        out["seconds"] = round(out["seconds"] + s.get("seconds", 0.0), 1)
        for key, rec in s.get("found", {}).items():
            r = out["found"].setdefault(key, {"cards": {}, "sim": 0, "how": {}, "paths": []})
            for c, n in rec.get("cards", {}).items():
                r["cards"][c] = r["cards"].get(c, 0) + n
            r["sim"] += rec.get("sim", 0)
            for h, n in rec.get("how", {}).items():
                r["how"][h] = r["how"].get(h, 0) + n
            for p in rec.get("paths", []):
                if len(r["paths"]) < 3 and p not in r["paths"]:
                    r["paths"].append(p)
    return out


def subtract(raw, excl):
    """raw minus excl, key by key and card by card (the scanner's own counts); keys left with no card and no simulator record are dropped."""
    out = copy.deepcopy(raw)
    for key, rec in excl.get("found", {}).items():
        if key not in out["found"]:
            continue
        r = out["found"][key]
        for c, n in rec.get("cards", {}).items():
            r["cards"][c] = r["cards"].get(c, 0) - n
            if r["cards"][c] <= 0:
                del r["cards"][c]
        r["sim"] = max(0, r.get("sim", 0) - rec.get("sim", 0))
        if not r["cards"] and not r["sim"]:
            del out["found"][key]
    out["files_read"] = raw["files_read"] - excl.get("files_read", 0)
    return out


def scan_files(NR, label, files):
    """E206's scanner's own loop and line rule (scan_line) over a list of FILES (HOME/claude/work's top-level files: its scan() walks folders only)"""
    found, n, big, bad = {}, 0, [], []
    t0 = time.time()
    for path in files:
        try:
            if os.path.islink(path) or not os.path.isfile(path):
                continue
            if os.path.getsize(path) > NR.MAX_BYTES:
                big.append(path)
                continue
            if path.endswith(".gz"):
                with gzip.open(path, "rb") as fh:
                    data = fh.read(NR.MAX_BYTES)
            else:
                with open(path, "rb") as fh:
                    data = fh.read()
        except Exception as e:  # noqa: BLE001
            bad.append(f"{path}: {e!r}"[:300])
            continue
        n += 1
        if b"gemm" not in data:
            continue
        for line in data.decode("utf-8", "replace").splitlines():
            r = NR.scan_line(line)
            if r is None:
                continue
            arm, t, kind, minions, mask, sim, how = r
            sim = sim or any(x in path for x in NR.SIM_MARKS)
            key = f"{arm}|{t}|{kind}|{minions}|{mask}"
            rec = found.setdefault(key, {"cards": {}, "sim": 0, "how": {}, "paths": []})
            if sim:
                rec["sim"] += 1
            else:
                c = NR.card_of(path, "unknown")
                rec["cards"][c] = rec["cards"].get(c, 0) + 1
            rec["how"][how] = rec["how"].get(how, 0) + 1
            if len(rec["paths"]) < 3 and path not in rec["paths"]:
                rec["paths"].append(path)
    return {"label": label, "box": "", "default_card": "unknown", "roots": list(files), "files_read": n, "files_over_400MB_skipped": big,
            "unreadable": bad[:50], "n_unreadable": len(bad), "seconds": round(time.time() - t0, 1), "found": found}


def desk(d):
    NR = scanner()
    r = roots()
    if not r["out"] or not os.path.isdir(r["out"]):
        print("NEVERRUN-REFUSED: E207_ROUND_OUT does not name the round's lane folders (the card lane sets it to the round's OUT)")
        return 2
    os.makedirs(d, exist_ok=True)
    t0 = time.time()
    raw = {"scans": {}}
    places = []     # every place scanned on its own: {"place", "where", "class", "root", "scan"} (scans with no record kept as counts only)
    labtops = [os.path.join(r["lab"], x) for x in sorted(os.listdir(r["lab"])) if x != ".git"]
    raw["scans"]["lab-main-all"] = NR.scan("lab-main-all", "unknown", labtops)
    dd = os.path.join(r["lab"], "docs", "reports", "data")
    counts = {"lab-data": [0, 0], "out-own": [0, 0], "out-data": [0, 0], "out-desk": [0, 0], "homew": [0, 0]}

    def add(where, cls, root, s, name):
        counts_key = {"lab": "lab-data", "out": f"out-{cls}", "homew": "homew"}[where] if where != "lab-own" else None
        if counts_key:
            counts[counts_key][0] += 1
            counts[counts_key][1] += s["files_read"]
        if s["found"] or where == "lab-own":
            places.append({"place": name, "where": where, "class": cls, "root": root, "scan": s})

    def walkable(p):   # the scanner's own rule: a folder holding a .git entry (a clone) is never read, so it is not scanned on its own either
        return os.path.isdir(p) and not os.path.islink(p) and not os.path.lexists(os.path.join(p, ".git"))
    for x in (sorted(os.listdir(dd)) if os.path.isdir(dd) else []):
        p = os.path.join(dd, x)
        if walkable(p):
            add("lab", "data", p, NR.scan(f"lab-data {x}", "unknown", [p]), f"docs/reports/data/{x}")
    own_lab = os.path.join(r["lab"], "tools", "claims-v3", "e207")
    add("lab-own", "own", own_lab, NR.scan("lab-e207-own", "unknown", [own_lab]) if os.path.isdir(own_lab) else empty("lab-e207-own"),
        "tools/claims-v3/e207")
    raw["scans"]["round-lanes"] = NR.scan("round-lanes", "unknown", [r["out"]])
    for x in sorted(os.listdir(r["out"])):
        p = os.path.join(r["out"], x)
        if not walkable(p):
            continue
        cls = "own" if OWN_LANE.match(x) else ("data" if DATA_LANE.match(x) else "desk")
        add("out", cls, p, NR.scan(f"round-lanes {x}", "unknown", [p]), x)
    barred, hfiles = [], []
    if os.path.isdir(r["homew"]):
        for x in sorted(os.listdir(r["homew"])):
            p = os.path.join(r["homew"], x)
            if BARRED_HOMEW.match(x):
                barred.append(x)
            elif walkable(p):
                add("homew", "data", p, NR.scan(f"aifoundry2-work {x}", "unknown", [p]), x)
            elif os.path.isfile(p) and not os.path.islink(p):
                hfiles.append(p)
        add("homew", "data", None, scan_files(NR, "aifoundry2-work top-level files", hfiles), "(its top-level files)")
    meta = {"started": time.strftime("%Y-%m-%d %H:%M:%S %Z", time.localtime(t0)), "seconds": round(time.time() - t0, 1),
            "scanner_sha256": SCANNER_PIN, "counts": counts, "homew_not_read": barred, "homew_top_files": len(hfiles),
            "excluded_lanes": [pl["place"] for pl in places if pl["where"] == "out" and pl["class"] == "own"],
            "out_classes": {"data": DATA_LANE.pattern, "own": OWN_LANE.pattern, "desk": "every other folder"}}
    json.dump({"scans": raw["scans"], **meta}, open(os.path.join(d, "found-desk-raw.json"), "w"), indent=0, default=str)
    json.dump({"places": places}, open(os.path.join(d, "found-desk-places.json"), "w"), indent=0, default=str)
    for k, s in raw["scans"].items():
        print(f"scan {k}: {s['files_read']} files, {len(s['found'])} GEMM configurations, over 400 MB {len(s['files_over_400MB_skipped'])}, "
              f"unreadable {s['n_unreadable']}, {s['seconds']} s")
    for k, (nf, nr) in counts.items():
        print(f"  {k}: {nf} folders scanned on their own, {nr} files")
    print(f"places holding a record of the lab's host (each scanned on its own): {len(places)}; E207's own lanes (subtracted): {meta['excluded_lanes']}")
    print(f"HOME/claude/work: the model session's experiment folders NOT READ (the 23:18:35 rule): {barred}")
    print(f"SCANNED-DESK {ts()} ({meta['seconds']} s)")
    return 0


# ------------------------------------------------------------------ matching, finding again, dating
def kind_scan(kind):
    return {"random": "random", "e37": "e37"}.get(kind, "tiles:other")


def want_keys(pts):
    """E207's points and cases as the registration's matching reads them (the mask as a number)"""
    wp, wc = {}, {}
    for p in pts:
        m = int(p["shire_mask"], 16)
        wp.setdefault((p["arm"], p["format"], kind_scan(p["kind"]), p["minions"], m), []).append(p["id"])
        wc.setdefault((p["arm"], p["format"], m), set()).add(p["case"])
    return wp, wc


def key_tuple(key):
    arm, t, kd, mi, mk = key.split("|")
    return (arm, t, kd, int(mi), int(mk, 16))


def hits_of(scan, wp, wc):
    """the E207 points and cases a scan holds card records of (simulator records never count)"""
    hp, hc = set(), set()
    for key, rec in scan.get("found", {}).items():
        if not rec.get("cards"):
            continue
        k = key_tuple(key)
        if k in wp:
            hp.update(wp[k])
        if (k[0], k[1], k[4]) in wc:
            hc.update(wc[(k[0], k[1], k[4])])
    return hp, hc


def walk_paths(NR, top, wp, wc):
    """every file under top holding a card record of an E207 point or case, by E206's scanner's own walk and line rule"""
    hits = {}
    for dp, dns, fns in os.walk(top):
        if dp != top and ".git" in dns + fns:
            dns[:] = []
            continue
        dns[:] = [x for x in dns if x != ".git"]
        for fn in fns:
            path = os.path.join(dp, fn)
            try:
                if os.path.islink(path) or not os.path.isfile(path) or os.path.getsize(path) > NR.MAX_BYTES:
                    continue
                if fn.endswith(".gz"):
                    with gzip.open(path, "rb") as fh:
                        data = fh.read(NR.MAX_BYTES)
                else:
                    with open(path, "rb") as fh:
                        data = fh.read()
            except Exception:  # noqa: BLE001
                continue
            if b"gemm" not in data:
                continue
            for line in data.decode("utf-8", "replace").splitlines():
                rr = NR.scan_line(line)
                if rr is None:
                    continue
                arm, t, kind, minions, mask, sim, how = rr
                if sim or any(x in path for x in NR.SIM_MARKS):
                    continue
                m = int(mask, 16)
                k = (arm, t, kind, minions, m)
                h = hits.setdefault(path, {"points": set(), "cases": set()})
                if k in wp:
                    h["points"].update(wp[k])
                if (arm, t, m) in wc:
                    h["cases"].update(wc[(arm, t, m)])
                if not h["points"] and not h["cases"]:
                    del hits[path]
    return hits


_COMMIT = {}


def dir_commit_time(lab, rel_dir):
    """the earliest commit that added a file under rel_dir in the lab clone (None if it is not a git work tree or never committed)"""
    if rel_dir in _COMMIT:
        return _COMMIT[rel_dir]
    t = None
    try:
        p = subprocess.run(["git", "-C", lab, "log", "--diff-filter=A", "--format=%ct", "--", rel_dir], capture_output=True, text=True, timeout=120)
        v = [int(x) for x in p.stdout.split() if x.isdigit()] if p.returncode == 0 else []
        t = min(v) if v else None
    except Exception:  # noqa: BLE001
        t = None
    _COMMIT[rel_dir] = t
    return t


def date_path(path, rel, where, lab):
    """(class, why) for one record's file: 'before', 'after' or 'to date' (E207.md A1 item 2)"""
    m = None
    for mm in T0_RE.finditer(rel):
        m = mm
    if m:
        t0 = int(m.group(1))
        return ("after" if t0 > FREEZE_EPOCH else "before"), f"its session's start in its path, T0 {t0} = {pt(t0)}"
    if where == "lab":
        md = DATADIR_RE.match(rel)
        if md:
            rd = "/".join(rel.split("/")[:4])
            ct = dir_commit_time(lab, rd)
            if ct is not None and ct <= FREEZE_EPOCH:
                return "before", f"its data directory was first committed {pt(ct)}"
            if md.group(1) < "2026-11-16":
                return "before", f"its data directory is dated {md.group(1)}"
            if md.group(1) >= "2026-11-17":
                return "after", f"its data directory is dated {md.group(1)} (its session's day)"
            return "to date", f"its data directory is dated {md.group(1)}, first committed {pt(ct) if ct else 'never (not in the history read)'}"
        return "to date", "a lab file outside a data directory"
    if where in ("out", "homew"):
        try:
            mt = os.path.getmtime(path)
        except OSError:
            mt = None
        if mt is not None and mt <= FREEZE_EPOCH:
            return "before", f"the file was last written {pt(mt)}"
        return "to date", f"the file was last written {pt(mt)}; no session start in its path"
    return "to date", "no session start in its path (aifoundry3's scan carries no file times)"


def worst(classes):
    if "before" in classes:
        return "RAN BEFORE"
    if "to date" in classes:
        return "TO DATE"
    if "after" in classes:
        return "AFTER THE FREEZE"
    return None


def classify(NR, r, pts, places, a3scan, arms_path, arms_sha):
    """every counted place holding an E207 point or case, found again path by path and dated; the dismissed places listed"""
    wp, wc = want_keys(pts)
    byid = {p["id"]: p for p in pts}
    out = {"freeze": {"epoch": FREEZE_EPOCH, "text": FREEZE_TEXT}, "counted": [], "dismissed": [], "points": {}, "cases": {}}
    pcls = {p["id"]: [] for p in pts}
    ccls = {p["case"]: [] for p in pts}
    for pl in places:
        if pl["class"] == "own":
            continue
        hp, hc = hits_of(pl["scan"], wp, wc)
        if not hp and not hc:
            continue
        counted = pl["class"] == "data"
        rec = {"place": pub(pl["root"]) if pl["root"] else pl["place"], "where": pl["where"], "class": pl["class"], "points": sorted(hp),
               "cases": sorted(hc)}
        if not counted:
            rec["paths"] = sorted({pub(x) for k, v in pl["scan"]["found"].items() if v.get("cards") for x in v.get("paths", [])
                                   if key_tuple(k) in wp or (key_tuple(k)[0], key_tuple(k)[1], key_tuple(k)[4]) in wc})[:12]
            out["dismissed"].append(rec)
            continue
        files = []
        if pl["root"] and os.path.isdir(pl["root"]):
            hits = walk_paths(NR, pl["root"], wp, wc)
            base = r["lab"] if pl["where"] == "lab" else pl["root"]
        else:
            hits = {}
            base = None
            for k, v in pl["scan"]["found"].items():
                if not v.get("cards"):
                    continue
                kt = key_tuple(k)
                for x in v.get("paths", []):
                    h = hits.setdefault(x, {"points": set(), "cases": set()})
                    h["points"].update(wp.get(kt, []))
                    h["cases"].update(wc.get((kt[0], kt[1], kt[4]), set()))
        for path, h in sorted(hits.items()):
            rel = os.path.relpath(path, base) if base else path
            c, why = date_path(path, rel, pl["where"], r["lab"])
            files.append({"path": pub(path), "class": c, "why": why, "points": sorted(h["points"]), "cases": sorted(h["cases"])})
            for i in h["points"]:
                pcls[i].append(c)
            for cs in h["cases"]:
                ccls[cs].append(c)
        rec["files"] = files[:60]
        rec["n_files"] = len(files)
        out["counted"].append(rec)
    if a3scan is not None:
        hp, hc = hits_of(a3scan, wp, wc)
        if hp or hc:
            files = []
            for k, v in a3scan["found"].items():
                if not v.get("cards"):
                    continue
                kt = key_tuple(k)
                pp, cc = wp.get(kt, []), wc.get((kt[0], kt[1], kt[4]), set())
                if not pp and not cc:
                    continue
                for x in v.get("paths", []):
                    c, why = date_path(x, x, "aifoundry3", r["lab"])
                    files.append({"path": pub(x), "class": c, "why": why, "points": sorted(pp), "cases": sorted(cc)})
                    for i in pp:
                        pcls[i].append(c)
                    for cs in cc:
                        ccls[cs].append(c)
            out["counted"].append({"place": "aifoundry3's run folders", "where": "aifoundry3", "class": "data", "points": sorted(hp),
                                   "cases": sorted(hc), "files": files, "n_files": len(files),
                                   "note": "the scanner keeps at most 3 paths a configuration; those are dated"})
    planned = set()
    if arms_path and os.path.exists(arms_path):
        for x in json.load(open(arms_path)).get("arms", []):
            kd = {"rnd": "random"}.get(x["kind"], x["kind"])
            planned.add((f"gemmL{x['mb']}x{x['nb']}x{x['kb']}", x["type"], kd, int(x["shires"], 16)))
    pc = "before" if arms_sha == ARMS_PIN else "to date"
    pwhy = ("E208's planned arms at the registered bytes (planned before the freeze)" if pc == "before"
            else "E208's planned arms changed since the registration")
    for p in pts:
        m = int(p["shire_mask"], 16)
        if (p["arm"], p["format"], p["kind"], m) in planned:
            pcls[p["id"]].append(pc)
            out.setdefault("planned", []).append({"id": p["id"], "class": pc, "why": pwhy})
        if any(x[0] == p["arm"] and x[1] == p["format"] and x[3] == m for x in planned):
            ccls[p["case"]].append(pc)
    for i, v in pcls.items():
        out["points"][i] = {"class": worst(v) or "NEVER-RUN", "records_dated": len(v), "case": byid[i]["case"]}
    for cs, v in ccls.items():
        out["cases"][cs] = {"class": worst(v) or "NEVER-RUN", "records_dated": len(v), "points": sorted(x["id"] for x in pts if x["case"] == cs)}
    lab_pts = sorted(i for i, v in out["points"].items() if v["class"] in ("RAN BEFORE", "TO DATE"))
    lab_cases = sorted(cs for cs, v in out["cases"].items() if v["class"] in ("RAN BEFORE", "TO DATE")
                       and not any(out["points"][i]["class"] in ("RAN BEFORE", "TO DATE") for i in v["points"]))
    out["labels_proposed"] = {"points": lab_pts, "cases": lab_cases,
                              "what": "E207.md A1 item 3: a labelled point leaves every rule (and its case the time rules); a labelled case leaves "
                                      "T1, T2, T3, H1 and H2 only. TO DATE ones are labelled unless the card lane's dated note shows, from the "
                                      "session's own start record, that the run came after the freeze (then it writes ranbefore-e207-labels.json)."}
    return out


def report(d, a3=None, a3x=None, a3_not=None):
    r = roots()
    raw = json.load(open(os.path.join(d, "found-desk-raw.json")))
    places = json.load(open(os.path.join(d, "found-desk-places.json")))["places"]
    pts = json.load(open(os.path.join(E, "points-e207.json")))["points"]
    net = {"what": "the counted records only (neverrun_card_e207.py, E207.md A1 item 1): the lab's data directories, the card and data lanes' "
                   "folders, HOME/claude/work but the model session's folders, aifoundry3's run folders but build/e207", "scans": {}}
    net["scans"]["lab-data"] = merge("lab-data", [pl["scan"] for pl in places if pl["where"] == "lab"])
    net["scans"]["round-lanes-data"] = merge("round-lanes-data", [pl["scan"] for pl in places if pl["where"] == "out" and pl["class"] == "data"])
    net["scans"]["aifoundry2-work"] = merge("aifoundry2-work", [pl["scan"] for pl in places if pl["where"] == "homew"])
    for k, n, root in (("lab-data", "lab-data", os.path.join(r["lab"], "docs", "reports", "data")),
                       ("round-lanes-data", "out-data", os.path.join(r["out"] or "OUT", "(card and data lanes)")),
                       ("aifoundry2-work", "homew", os.path.join(r["homew"], "(all but ee-*)"))):
        net["scans"][k]["files_read"] = raw["counts"][n][1]
        net["scans"][k]["roots"] = [root]
        net["scans"][k]["box"] = raw["scans"]["lab-main-all"].get("box", "")
    # the dismissed remainders, by the scanner's own counts: the lab outside its data directories (E207's own folder subtracted too) and OUT's
    # top-level files (OUT less every folder scanned on its own)
    lab_other = subtract(subtract(raw["scans"]["lab-main-all"], merge("lab-data", [pl["scan"] for pl in places if pl["where"] == "lab"])),
                         merge("lab-own", [pl["scan"] for pl in places if pl["where"] == "lab-own"]))
    for v in lab_other["found"].values():
        v["paths"] = [x for x in v.get("paths", []) if "/docs/reports/data/" not in x and "/tools/claims-v3/e207/" not in x]
    out_top = subtract(raw["scans"]["round-lanes"], merge("out", [pl["scan"] for pl in places if pl["where"] == "out"]))
    for v in out_top["found"].values():
        v["paths"] = [x for x in v.get("paths", []) if r["out"] and os.path.dirname(x) == r["out"].rstrip("/")]
    extra = [{"place": "the lab outside its data directories", "where": "lab-other", "class": "desk", "root": None, "scan": lab_other},
             {"place": "OUT's top-level files", "where": "out-top", "class": "desk", "root": None, "scan": out_top}]
    a3_line = "aifoundry3's run folders: NOT SEARCHED (" + (a3_not or "no scan given") + ")"
    a3scan = None
    if a3:
        ra = json.load(open(a3))
        xa = json.load(open(a3x)) if a3x and os.path.exists(a3x) and os.path.getsize(a3x) > 2 else {"found": {}, "files_read": 0}
        a3scan = subtract(ra, xa)
        net["scans"]["aifoundry3-ours"] = a3scan
        a3_line = (f"aifoundry3's run folders: {ra['files_read']} files read, {xa.get('files_read', 0)} of them in E207's own build/e207 "
                   f"(subtracted)")
    fn = os.path.join(d, "found-net.json")
    json.dump(net, open(fn, "w"), indent=0, default=str)
    # the registration's matching, unchanged, from a copy beside a copy of points-e207.json (both at the registration's sha256)
    want = {}
    for ln in open(REG_LIST):
        if ln.strip():
            h, p = ln.split(None, 1)
            want[p.strip()] = h
    rd = os.path.join(d, "reg")
    os.makedirs(os.path.join(rd, "desk"), exist_ok=True)
    for rel, dst in (("tools/claims-v3/e207/desk/neverrun_e207.py", os.path.join(rd, "desk", "neverrun_e207.py")),
                     ("tools/claims-v3/e207/points-e207.json", os.path.join(rd, "points-e207.json"))):
        shutil.copyfile(os.path.join(REPO, rel), dst)
        if sha(dst) != want.get(rel):
            print(f"NEVERRUN-REFUSED: {rel} is not at the registration's sha256")
            return 3
    arms = r["arms"]
    ah = sha(arms) if os.path.exists(arms) else None
    if ah is None:
        print(f"NEVERRUN-REFUSED: E208's planned arms are not at {arms}")
        return 3
    p = subprocess.run([sys.executable, "-I", "-B", os.path.join(rd, "desk", "neverrun_e207.py"), fn, "--e208-arms", arms,
                        "--when", f"the card lane's repeat, {ts()}"], capture_output=True, text=True)
    txt = p.stdout
    if p.returncode != 0 or not os.path.exists(os.path.join(rd, "desk", "neverrun-e207.json")):
        open(os.path.join(d, "neverrun-e207-card.txt"), "w").write(txt + (p.stderr or ""))
        print(f"NEVERRUN-FAILED: the registration's matching rc {p.returncode}: {(p.stderr or '')[-300:]}")
        return 14
    rep = json.load(open(os.path.join(rd, "desk", "neverrun-e207.json")))
    c = rep["counts"]
    ran = [x["id"] for x in rep["rows"] if not x["never_run_point"]]
    ran_cases = sorted({x["case"] for x in rep["rows"] if not x["never_run_case_any_kind"]})
    # the places, found again and dated (A1 items 1-3); any failure here labels every counted hit, conservatively
    NR = scanner()
    try:
        cl = classify(NR, r, pts, places + extra, a3scan, arms, ah)
        mine = sorted(i for i, v in cl["points"].items() if v["class"] != "NEVER-RUN")
        mine_c = sorted(cs for cs, v in cl["cases"].items() if v["class"] != "NEVER-RUN")
        if mine != sorted(ran) or mine_c != ran_cases:
            raise ValueError(f"the dating found {mine} / {len(mine_c)} cases where the registered matching found {sorted(ran)} / {len(ran_cases)}")
        cl["status"] = "dated"
    except Exception as e:  # noqa: BLE001
        why = re.sub(r"/home/[^/\s'\"]+", "HOME", pub(str(e)))[:300]
        cl = {"status": f"DATING FAILED ({type(e).__name__}: {why}): every counted point found run is labelled RAN BEFORE",
              "freeze": {"epoch": FREEZE_EPOCH, "text": FREEZE_TEXT}, "counted": [], "dismissed": [],
              "points": {x["id"]: {"class": ("RAN BEFORE" if not x["never_run_point"] else "NEVER-RUN"), "case": x["case"]} for x in rep["rows"]},
              "cases": {}, "labels_proposed": {"points": sorted(ran), "cases": ran_cases, "what": "the conservative fallback"}}
        for x in rep["rows"]:
            cl["cases"].setdefault(x["case"], {"class": "NEVER-RUN" if x["never_run_case_any_kind"] else "RAN BEFORE", "points": []})
            cl["cases"][x["case"]]["points"].append(x["id"])
        cl["labels_proposed"]["cases"] = sorted(cs for cs, v in cl["cases"].items() if v["class"] == "RAN BEFORE"
                                                and not any(cl["points"][i]["class"] == "RAN BEFORE" for i in v["points"]))
    desk_only = sorted({i for rec in cl["dismissed"] for i in rec["points"]} - set(ran))
    cl.update({"when": ts(), "desk_scans_started": raw.get("started"), "a3": a3_line, "e208_arms_sha256": ah,
               "e208_arms_registered": ah == ARMS_PIN, "homew_not_read": raw.get("homew_not_read", []), "desk_only_points": desk_only,
               "not_searched": "aifoundry1's own folders (as registered); HOME/claude/work/ee-*/ (the orchestrator's rule of 23:18:35 PST Mon 16 Nov "
                               "2026; E208's planned arms read)", "registered_counts": c})
    json.dump(cl, open(os.path.join(d, "ranbefore-e207.json"), "w"), indent=1, sort_keys=True)
    P = cl["points"]
    before = sorted(i for i, v in P.items() if v["class"] == "RAN BEFORE")
    todate = sorted(i for i, v in P.items() if v["class"] == "TO DATE")
    after = sorted(i for i, v in P.items() if v["class"] == "AFTER THE FREEZE")
    cbefore = [cs for cs in cl["labels_proposed"]["cases"] if cl["cases"][cs]["class"] == "RAN BEFORE"]
    ctodate = [cs for cs in cl["labels_proposed"]["cases"] if cl["cases"][cs]["class"] == "TO DATE"]
    lines = [txt.rstrip("\n"), "",
             f"step 6n's reading (E207.md A1): 'ran before' = a card record dated before {FREEZE_TEXT}; {cl['status']}",
             f"desk scans: {raw.get('started')} ({raw.get('seconds')} s); E207's own folders subtracted: {raw.get('excluded_lanes')}, "
             f"tools/claims-v3/e207; {a3_line}",
             f"HOME/claude/work: NOT READ {raw.get('homew_not_read', [])} (the model session's folders, the orchestrator's rule of 23:18:35 PST "
             f"Mon 16 Nov 2026); E208's planned arms read: sha256 {ah} "
             f"({'the registered file' if ah == ARMS_PIN else 'CHANGED since the registration: read as it is now; its matches are TO DATE'})"]
    for rec in cl["counted"]:
        lines.append(f"  COUNTED {rec['where']} {rec['place']}: points {' '.join(rec['points']) or '-'}; cases {len(rec['cases'])}; "
                     f"{rec.get('n_files', 0)} file(s)")
        for f in rec.get("files", [])[:8]:
            lines.append(f"    {f['class'].upper()}: {f['path']} ({f['why']}; points {' '.join(f['points']) or '-'})")
    for rec in cl["dismissed"]:
        kind = {"out": "a desk lane's folder", "lab-other": "not a data directory", "out-top": "not a lane's folder"}.get(rec["where"], rec["where"])
        lines.append(f"  DISMISSED ({kind}, never a card run) {rec['place']}: points "
                     f"{' '.join(rec['points']) or '-'}; cases {len(rec['cases'])}; e.g. {', '.join(rec.get('paths', [])[:3])}")
    for x in cl.get("planned", []):
        lines.append(f"  PLANNED {x['id']}: {x['class'].upper()} ({x['why']})")
    if before or todate or cbefore or ctodate:
        lines.append(f"  LABELS PROPOSED (the card lane's dated note before the data commit; E207.md A1 item 3): points "
                     f"{' '.join(cl['labels_proposed']['points']) or '-'}; cases (the time rules only) {' '.join(cl['labels_proposed']['cases']) or '-'}")
    word = (f"NEVER-RUN {c['never_run_points']} of {c['points']} points, {c['never_run_cases']} of {c['cases']} cases"
            + (f"; RAN BEFORE: {' '.join(before)}" if before else "")
            + (f"; CASE RAN BEFORE: {' '.join(cbefore)}" if cbefore else "")
            + (f"; TO DATE: {' '.join(todate + ctodate)}" if (todate or ctodate) else "")
            + (f"; AFTER THE FREEZE (REPORTED, kept): {' '.join(after)}" if after else "")
            + (f"; DESK-ONLY (dismissed): {' '.join(desk_only)}" if desk_only else "")
            + ("" if a3 else "; aifoundry3 NOT SEARCHED"))
    lines.append(word)
    body = "\n".join(lines) + "\n"
    open(os.path.join(d, "neverrun-e207-card.txt"), "w").write(body + (p.stderr or ""))
    print(body.rstrip("\n"))
    return 0


def main(argv):
    if argv[:1] == ["desk"] and len(argv) == 2:
        return desk(argv[1])
    if argv[:1] == ["report"] and len(argv) >= 2:
        a3 = argv[argv.index("--a3") + 1] if "--a3" in argv else None
        a3x = argv[argv.index("--a3-excluded") + 1] if "--a3-excluded" in argv else None
        a3n = argv[argv.index("--a3-not-searched") + 1] if "--a3-not-searched" in argv else None
        return report(argv[1], a3, a3x, a3n)
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
