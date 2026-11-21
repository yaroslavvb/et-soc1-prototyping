#!/usr/bin/env python3
"""E222 (Q236) desk: which configurations never ran on E222's one card, aifoundry3 card 0, by E220's never-run scan form AS ITS DATED NOTE 1
AMENDS IT (tools/claims-v3/e220-notes/E220.md.dated-note-1.md: a point counts as RUN on a card only by A SESSION RECORD ON THAT CARD; desk
copies in folders naming no card never count), the literal reading REPORTED beside. Reads files, writes only its report. No forecast is read
or made here; nothing numerical runs but MM1-v3.2's data loader (its measured points), numpy through it.

    /usr/bin/python3 -I -B tools/claims-v3/e222/desk/neverrun_e222.py scan --lab <the lab at GitHub main> --lanes <W/out> --out <dir>
        E220's scan (tools/claims-v3/e220/desk/neverrun_e220.py's scan, its form: E215's scanner at its pin and E213's module at its pin
        through it - the token rule, the roots, the folder classes, the reader and the mask reading) over the lab's committed data folders
        (docs/reports/data: every committed matmul data folder through E221's committed sessions, E218's on this card among them), E212's and
        E208's committed schedules and arms, and EVERY round lane folder under W/out whose name starts card-, data-, a1, a2 or a3, gzip read
        through; plus MM1-v3.2's measured points (data_v32.py as landed). Writes <dir>/scan-e222-reg.json.
    /usr/bin/python3 -I -B tools/claims-v3/e222/desk/neverrun_e222.py report --scan <scan-e222-reg.json> --points <points-e222.csv> --out <dir>
        each registered point's verdict on aifoundry3 card 0 by its family's reading (class Never), written to <dir>/neverrun-e222.json, .txt.

WHAT IS NEVER OPENED (before any read; E220 BLINDNESS, Q236's brief): a docs/reports/data folder whose name holds 'e220'; a round lane folder
whose name holds 'e220' (E220's card-day lanes card-e220a, card-e220b and any data lane of E220); E222's own folders ('-e222-', W/out/card-e222*;
none exists). E220's card days run on aifoundry1 card 1 and aifoundry2 card 0 only (its registration 6901854c), so no session record on
aifoundry3 card 0 can sit in them: leaving them unread cannot hide a run on this card.
WHAT EACH FILE IS (per file, recorded per token and folder class): its folder class (E213's folder_card / lane_card / exp_cards, with two
additions on the conservative side for THIS card: the round's arm-A card lanes card-e213a and card-e215a ran on aifoundry3 card 0 (E213 arm A,
E215 arm A), which E213's experiment map classes as card 1 by its first data folder name: both are classed aifoundry3 card 0 here); and whether
it is A SESSION RECORD (dated note 1, neverrun_card_e220.note1: a file of a committed data folder, docs/reports/data/..., or a session's own
file in a lane folder, the note's SESSION_FILE pattern, never under a /dry/ folder).
THE READINGS (class Never): on aifoundry3 card 0, by SESSION RECORDS ONLY (dated note 1's reading, the registered reading of E222):
  token(token)        the shape token (E213's: gemmL<MB>x<NB>x<KB>, gemmLnc<..>, gemmLn<..>, matched whole) never ran on the card: no session
                      record in a folder classed aifoundry3 card 0 names it and no MM1-v3.2 measured point holds it on the card;
  config(token, mask) the configuration never ran: no MM1-v3.2 measured point holds (token, mask) on the card and no session record classed
                      aifoundry3 card 0 naming the token names the mask;
  mask(mask)          the mask never ran on the card at any shape: no MM1-v3.2 measured point on the card has it and no session record classed
                      aifoundry3 card 0 names it (any 0x hex the reader finds counts: the conservative side);
  literal_token / literal_config (REPORTED, never a verdict): E220's registered literal reading (any file counted for the card by E213's
                      classes, a folder naming no card counting for every card).
Standard library only here (data_v32 brings numpy). Single-threaded (the caller sets the thread variables).
Not read: the model session's uncommitted folders on its boxes (the orchestrator's rule of 23:18:35 PST Mon 16 Nov 2026); the boxes' own disks;
desk folders (registrations, models, kits, verifiers: E213's rule); a scratch clone inside a lane folder (a .git entry).
SPDX-License-Identifier: Apache-2.0
"""
import argparse
import csv
import datetime
import hashlib
import importlib.util
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", "..", "..", ".."))
E215_SCAN = ("tools/claims-v3/e215/desk/neverrun_e215.py", "9e68b0012dd782cd1fcb91806a8213f550294822337de204344bd22b73a89789")
DATA_V32 = ("tools/matmul/mm1/v3.2/data_v32.py", "72574b86a1dc0546eeee3348503f84b7ec56556cd7c451c99d2d6206ec205fa6")
NOTE1 = ("tools/claims-v3/e220-notes/E220.md.dated-note-1.md", "4b87fb4fe4f549fe2005581fc121d49a043b6effe59c112cf6ffe57c008ba897")
A3 = "aifoundry3 card 0"
# dated note 1's session-file pattern (tools/claims-v3/e220/desk/neverrun_card_e220.py, SESSION_FILE), literally
SESSION_FILE = re.compile(r"/(session|sessions|runs|smoke)/|(^|/)(proc[-0-9]*\.(out|err)|run\.json|smoke\.json|queue\.json|session\.log)$")
ARM_A_LANES_A3 = ("W/out/card-e213a/", "W/out/card-e215a/")


def now():
    return datetime.datetime.now().astimezone().strftime("%Y-%m-%d %H:%M:%S %Z")


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def pinned(lab, rel, want):
    p = os.path.join(lab, rel)
    got = sha(p)
    if got != want:
        print(f"neverrun_e222: REFUSED, {rel} is {got}, pinned {want}")
        sys.exit(4)
    return p


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def never_opened(name):
    """E220 BLINDNESS and E222's own: a folder or lane name holding 'e220' or 'e222' is never walked, never read"""
    n = name.lower()
    return ("e220" in n) or ("e222" in n)


def is_session_record(rel):
    """dated note 1: a file of a committed data folder, or a session's own file in a lane folder (never a dry pass)"""
    return rel.startswith("docs/reports/data/") or (bool(SESSION_FILE.search(rel)) and "/dry/" not in rel)


def counted_for(card, c):
    """E213's classes (E220's neverrun_e220.counted_for): a folder naming the card, or naming no card (the LITERAL reading, REPORTED)"""
    return c == card or c == "no card named"


def scan(lab, lanes, out):
    NR = load("neverrun_e215_pinned", pinned(lab, *E215_SCAN))
    N = NR.e213_module()  # E213's module at its pin (exit 4 otherwise)
    pinned(lab, *DATA_V32)
    pinned(lab, *NOTE1)
    t0 = now()
    expmap = N.exp_cards(lab)
    data_root = os.path.join(lab, "docs", "reports", "data")
    roots = [data_root, os.path.join(lab, "tools", "claims-v3", "e212", "proposal", "src", "sched"),
             os.path.join(lab, "tools", "claims-v3", "e208", "proposal", "src")]
    lane_names = sorted(d for d in os.listdir(lanes) if d.startswith(("card-", "data-", "a1", "a2", "a3")) and os.path.isdir(os.path.join(lanes, d)))
    lane_roots = [os.path.join(lanes, d) for d in lane_names if not never_opened(d)]
    lanes_not_opened = [d for d in lane_names if never_opened(d)]
    data_not_opened = sorted(d for d in os.listdir(data_root) if never_opened(d))
    hits, masks, smasks, smask_class = {}, {}, {}, {}
    nfiles, big, unreadable, git_dirs, nsession = 0, [], 0, 0, 0
    by_root = {}
    for top in roots + lane_roots:
        for dp, dn, fns in os.walk(top):
            if ".git" in dn or ".git" in fns:
                dn[:] = []
                git_dirs += 1
                continue
            if top == data_root and dp == data_root:
                dn[:] = [d for d in dn if not never_opened(d)]      # E220's data folders (none at the scan's HEAD) never walked
            dn.sort()
            for fn in sorted(fns):
                p = os.path.join(dp, fn)
                if fn.endswith(N.SKIP_EXT) or os.path.islink(p):
                    continue
                try:
                    if os.path.getsize(p) > N.MAX_BYTES:
                        big.append(p)
                        continue
                    txt = N.read_text(p)
                except (OSError, EOFError):
                    unreadable += 1
                    continue
                nfiles += 1
                rel = os.path.relpath(p, lab) if p.startswith(lab + os.sep) else "W/out/" + os.path.relpath(p, lanes)
                rk = os.path.relpath(top, lab) if top.startswith(lab + os.sep) else "W/out/" + os.path.basename(top)
                by_root[rk] = by_root.get(rk, 0) + 1
                if rel.startswith(ARM_A_LANES_A3):
                    c = A3
                else:
                    c = N.lane_card(rel) or N.folder_card(rel, expmap) or N.NONE
                sess = is_session_record(rel)
                found = set(N.RX.findall(txt))
                fm = sorted({"0x%x" % int(m, 16) for m in NR.MRX.findall(txt)})
                if sess:
                    nsession += 1
                    smask_class.setdefault(c, set()).update(fm)
                if not found:
                    continue
                for t in found:
                    h = hits.setdefault(t, {}).setdefault(c, {"files": [], "session_files": [], "n": 0, "n_session": 0})
                    h["n"] += 1
                    if len(h["files"]) < 8:
                        h["files"].append(rel)
                    if sess:
                        h["n_session"] += 1
                        if len(h["session_files"]) < 8:
                            h["session_files"].append(rel)
                        smasks.setdefault(t, {}).setdefault(c, set()).update(fm)
                    masks.setdefault(t, {}).setdefault(c, set()).update(fm)
    sys.path.insert(0, os.path.join(lab, "tools", "matmul", "mm1", "v3.2"))
    import data_v32 as DV  # noqa: E402
    meas_tok, meas_cfg, meas_mask = {}, {}, {}
    for q in DV.time_points() + DV.energy_points():
        mk = "0x%x" % int(q["mask"], 16)
        meas_tok.setdefault(q["arm"], set()).add((q["kernel"], q["card"]))
        meas_cfg.setdefault(q["arm"], {}).setdefault(q["card"], set()).add(mk)
        meas_mask.setdefault(q["card"], set()).add(mk)
    head = os.popen(f"git -C '{lab}' rev-parse HEAD 2>/dev/null").read().strip()
    rec = {"what": ("E222's never-run scan at its registration, in E220's scanner form as its dated note 1 amends it (session records only, on "
                    "aifoundry3 card 0), the literal reading kept beside: E215's scanner's token rule, roots, folder classes and reader (E213's at "
                    "their pins) over the lab at GitHub main and every round card and data lane folder, E220's and E222's folders never opened, plus "
                    "MM1-v3.2's measured points"),
           "lab_head": head, "neverrun_e215_sha256": E215_SCAN[1], "neverrun_e213_sha256": NR.E213_SCAN[1], "data_v32_sha256": DATA_V32[1],
           "note1_sha256": NOTE1[1], "session_file_pattern": SESSION_FILE.pattern, "arm_A_lanes_classed_aifoundry3": list(ARM_A_LANES_A3),
           "started": t0, "ended": now(), "files_read": nfiles, "session_record_files_read": nsession, "files_read_by_root": by_root,
           "roots": [os.path.relpath(r, lab) for r in roots], "lane_roots": ["W/out/" + os.path.basename(r) for r in lane_roots],
           "never_opened": {"rule": "a folder or lane name holding 'e220' (E220 BLINDNESS) or 'e222' (E222's own), never walked or read",
                            "lane_folders": ["W/out/" + d for d in lanes_not_opened], "data_folders": data_not_opened},
           "expmap": expmap, "over_400MB_not_read": [os.path.relpath(q, lanes) if q.startswith(lanes) else os.path.relpath(q, lab) for q in big],
           "unreadable": unreadable, "git_dirs_not_read": git_dirs,
           "tokens": {t: {c: v for c, v in sorted(cs.items())} for t, cs in sorted(hits.items())},
           "masks_by_card": {t: {c: sorted(v) for c, v in sorted(cs.items())} for t, cs in sorted(masks.items())},
           "session_masks_by_card": {t: {c: sorted(v) for c, v in sorted(cs.items())} for t, cs in sorted(smasks.items())},
           "session_masks_by_class_any_token": {c: sorted(v) for c, v in sorted(smask_class.items())},
           "mm1_v32_measured_tokens": {t: sorted(f"{k} on {c}" for k, c in v) for t, v in sorted(meas_tok.items())},
           "mm1_v32_measured_masks": {t: {c: sorted(v) for c, v in sorted(cs.items())} for t, cs in sorted(meas_cfg.items())},
           "mm1_v32_measured_masks_by_card": {c: sorted(v) for c, v in sorted(meas_mask.items())}}
    os.makedirs(out, exist_ok=True)
    pth = os.path.join(out, "scan-e222-reg.json")
    json.dump(rec, open(pth, "w"), indent=1, sort_keys=True)
    print(f"scan: {nfiles} files read ({nsession} session records), {len(hits)} distinct tokens, {len(big)} over 400 MB, {unreadable} unreadable, "
          f"{git_dirs} git dirs not read; never opened: {len(lanes_not_opened)} lane folders, {len(data_not_opened)} data folders; lab {head[:12]}; "
          f"{t0} - {rec['ended']}; scan-e222-reg.json {sha(pth)}")
    return pth


class Never:
    """the readings on aifoundry3 card 0: session records only (dated note 1, registered) and the literal reading (REPORTED)"""

    def __init__(self, S, card=A3):
        self.S = S
        self.card = card

    def token(self, token):
        h = (self.S["tokens"].get(token) or {}).get(self.card) or {}
        meas = [m for m in self.S["mm1_v32_measured_tokens"].get(token, []) if m.endswith(self.card)]
        n_s = int(h.get("n_session") or 0)
        return (n_s == 0 and not meas), {"session_records_on_card": n_s, "session_files": h.get("session_files", [])[:4],
                                         "measured_on_card": meas[:4]}

    def config(self, token, mask):
        m = "0x%x" % int(mask, 16)
        sm = ((self.S["session_masks_by_card"].get(token) or {}).get(self.card)) or []
        mm = ((self.S["mm1_v32_measured_masks"].get(token) or {}).get(self.card)) or []
        ran = (m in sm) or ("any" in sm) or (m in mm)
        h = (self.S["tokens"].get(token) or {}).get(self.card) or {}
        return (not ran), {"mask_named_in_session_records_naming_token": m in sm, "mask_in_mm1_v32_points_on_card": m in mm,
                           "session_files": h.get("session_files", [])[:4] if ran else []}

    def mask(self, mask):
        m = "0x%x" % int(mask, 16)
        a = m in (self.S["session_masks_by_class_any_token"].get(self.card) or [])
        b = m in (self.S["mm1_v32_measured_masks_by_card"].get(self.card) or [])
        return (not a and not b), {"mask_named_in_any_session_record_on_card": a, "mask_in_mm1_v32_points_on_card": b}

    def literal_token(self, token):
        T = {c: v["n"] for c, v in (self.S["tokens"].get(token) or {}).items() if counted_for(self.card, c)}
        meas = [m for m in self.S["mm1_v32_measured_tokens"].get(token, []) if m.endswith(self.card)]
        return (not T and not meas), {"hits_counted_for_card": T}

    def literal_config(self, token, mask):
        m = "0x%x" % int(mask, 16)
        Mb = self.S["masks_by_card"].get(token, {})
        named = sorted(c for c, ms in Mb.items() if counted_for(self.card, c) and (m in ms or "any" in ms))
        mm = ((self.S["mm1_v32_measured_masks"].get(token) or {}).get(self.card)) or []
        return (not named and m not in mm), {"mask_named_in_files_counted_for_card": named}

    def verdict(self, reading, token, mask):
        if reading == "exempt":
            return True, {"exempt": "family R: same-card repeats, exempt from the never-run rule by family name"}
        if reading == "config":
            return self.config(token, mask)
        if reading == "token+masks":
            ok1, e1 = self.token(token)
            ok2, e2 = self.mask(mask)
            return (ok1 and ok2), {"token": e1, "mask": e2}
        return self.token(token)

    def literal(self, reading, token, mask):
        if reading == "config":
            return self.literal_config(token, mask)
        return self.literal_token(token)


def report(scan_path, points_path, out):
    S = json.load(open(scan_path))
    NV = Never(S)
    rows = list(csv.DictReader(open(points_path)))
    res = []
    for r in rows:
        reading = r["neverrun_reading"]
        ok, ev = NV.verdict(reading, r["token"], r["shire_mask"])
        lok, lev = NV.literal("config" if reading == "config" else "token", r["token"], r["shire_mask"])
        res.append({"id": r["id"], "family": r["family"], "token": r["token"], "mask": r["shire_mask"], "card": A3, "reading": reading,
                    "never_run": bool(ok), "evidence": ev, "literal_never_run_REPORTED": bool(lok), "literal_evidence_REPORTED": lev})
    rec = {"what": "E222's never-run verdicts per registered point on aifoundry3 card 0 (desk/neverrun_e222.py report): session records only "
                   "(E220's dated note 1), the literal reading REPORTED beside",
           "scan_sha256": sha(scan_path), "points_sha256": sha(points_path), "scan_window": [S["started"], S["ended"]], "lab_head": S["lab_head"],
           "files_read": S["files_read"], "n_points": len(res), "n_never_run": sum(1 for v in res if v["never_run"]),
           "ran": [v["id"] for v in res if not v["never_run"]],
           "literal_REPORTED": {"n_never_run": sum(1 for v in res if v["literal_never_run_REPORTED"]),
                                "ran": [v["id"] for v in res if not v["literal_never_run_REPORTED"]]}, "points": res}
    os.makedirs(out, exist_ok=True)
    json.dump(rec, open(os.path.join(out, "neverrun-e222.json"), "w"), indent=1, sort_keys=True)
    lines = [f"E222 never-run report; scan {rec['scan_sha256'][:16]} ({S['files_read']} files, {S['started']} - {S['ended']}, lab {S['lab_head'][:12]})",
             f"points {os.path.basename(points_path)} sha256 {rec['points_sha256'][:16]}: {rec['n_never_run']} of {len(res)} never ran on {A3} by "
             f"session records (family R exempt by name); ran: {rec['ran']}; the literal reading (REPORTED): {rec['literal_REPORTED']['n_never_run']} "
             f"of {len(res)} never ran"]
    for v in res:
        lines.append(f"{v['id']:7s} {v['family']:4s} {v['token']:18s} {v['mask']:10s} {v['reading']:11s} never_run={v['never_run']} "
                     f"literal={v['literal_never_run_REPORTED']}")
    open(os.path.join(out, "neverrun-e222.txt"), "w").write("\n".join(lines) + "\n")
    print("\n".join(lines[:2]))


def main():
    ap = argparse.ArgumentParser()
    sp = ap.add_subparsers(dest="cmd", required=True)
    a1 = sp.add_parser("scan")
    a1.add_argument("--lab", required=True)
    a1.add_argument("--lanes", required=True)
    a1.add_argument("--out", required=True)
    a2 = sp.add_parser("report")
    a2.add_argument("--scan", required=True)
    a2.add_argument("--points", required=True)
    a2.add_argument("--out", required=True)
    a = ap.parse_args()
    if a.cmd == "scan":
        scan(os.path.abspath(a.lab), os.path.abspath(a.lanes), a.out)
    else:
        report(a.scan, os.path.abspath(a.points), a.out)


if __name__ == "__main__":
    main()
