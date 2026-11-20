#!/usr/bin/env python3
"""E220 (Q233) desk: which configurations never ran on E220's two cards - aifoundry1 card 1 (arm A) and aifoundry2 card 0 (arm B) - by E218's
never-run scan run literally (tools/claims-v3/e218/desk/neverrun_e218.py's scan at E220's registration), with E220's own folders subtracted.
Reads files, writes only its report. No forecast is read or made here.

    /usr/bin/python3 -I -B tools/claims-v3/e220/desk/neverrun_e220.py scan --lab <the lab at GitHub main> --lanes <W/out> --out <dir>
        E215's scanner's scan (tools/claims-v3/e215/desk/neverrun_e215.py at its pin, with E213's neverrun_e213.py at its pin through it: the
        token rule, the roots, the folder classes, the reader and the mask reading) over the lab's committed data folders (docs/reports/data:
        every committed matmul data folder through E219 and E218's), E212's and E208's committed schedules and arms, and EVERY round lane
        folder under W/out whose name starts card-, data-, a1, a2 or a3 (E218's form, literally), gzip read through; E220's own folders
        SUBTRACTED (a data folder whose name holds '-e220-'; W/out/card-e220*); plus MM1-v3.2's measured points (its data loader data_v32.py as
        landed: every point MM1-v3.2 read, E214 and E215 among them). Writes <dir>/scan-e220-reg.json.
    /usr/bin/python3 -I -B tools/claims-v3/e220/desk/neverrun_e220.py report --scan <scan-e220-reg.json> --points <points-e220.csv> --out <dir>
        each registered point's verdict on its own arm's card by its family's reading (the Never class below), written to
        <dir>/neverrun-e220.json and .txt.

THE READINGS (class Never; E218's e218_v32.Never with the card a parameter; E213's folder classes through counted_for):
  token_card(token, card)   the shape token (E213's: gemmL<MB>x<NB>x<KB>, gemmLnc<..>, gemmLn<..>, matched whole) never ran on that card: no
                            hit COUNTED for the card (a folder naming the card; for aifoundry1's cards also a folder naming aifoundry1 but no
                            card; a folder naming no card counts for every card) and no MM1-v3.2 measured point of the token on the card;
  config_card(token, mask, card)  the configuration (shape, mask) never ran on that card: no MM1-v3.2 measured point holds it there and no
                            scanned file counted for the card holding the shape token names the mask (E218's Y reading, literally);
  token_any(token)          never ran on any card (E218's F reading; REPORTED here).
Standard library only; nothing numerical runs. Single-threaded.
Not read: the model session's uncommitted folders on its boxes (the orchestrator's rule of 23:18:35 PST Mon 16 Nov 2026); aifoundry1's and
aifoundry3's own disks; desk folders (registrations, models, kits, verifiers: E213's rule; this lane's own folder reg-e220 is not a card or data
lane); a scratch clone inside a lane folder (a .git entry).
SPDX-License-Identifier: Apache-2.0
"""
import argparse
import csv
import datetime
import hashlib
import importlib.util
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", "..", "..", ".."))
E215_SCAN = ("tools/claims-v3/e215/desk/neverrun_e215.py", "9e68b0012dd782cd1fcb91806a8213f550294822337de204344bd22b73a89789")
DATA_V32 = ("tools/matmul/mm1/v3.2/data_v32.py", "72574b86a1dc0546eeee3348503f84b7ec56556cd7c451c99d2d6206ec205fa6")
C1 = "aifoundry1 card 1"
A2 = "aifoundry2 card 0"
A3 = "aifoundry3 card 0"
ARM_CARD = {"A": C1, "B": A2}


def now():
    return datetime.datetime.now().astimezone().strftime("%Y-%m-%d %H:%M:%S %Z")


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def pinned(lab, rel, want):
    p = os.path.join(lab, rel)
    got = sha(p)
    if got != want:
        print(f"neverrun_e220: REFUSED, {rel} is {got}, pinned {want}")
        sys.exit(4)
    return p


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def subtracted(rel):
    """E220's own folders (none exists before its card day): a data folder whose name holds '-e220-', the card lanes W/out/card-e220*"""
    return ("-e220-" in rel) or rel.startswith("W/out/card-e220")


def counted_for(card, c):
    """E213's classes (neverrun_e213.counted_for, e218_v32.counted_for): a folder naming that card, or naming no card; for aifoundry1's two
    cards also a folder naming aifoundry1 but no card"""
    if c == card or c == "no card named":
        return True
    if card in ("aifoundry1 card 1", "aifoundry1 card 0") and c == "aifoundry1 (card not named)":
        return True
    return False


def scan(lab, lanes, out):
    NR = load("neverrun_e215_pinned", pinned(lab, *E215_SCAN))
    N = NR.e213_module()  # E213's module at its pin (exit 4 otherwise)
    pinned(lab, *DATA_V32)
    t0 = now()
    expmap = N.exp_cards(lab)
    roots = [os.path.join(lab, "docs", "reports", "data"), os.path.join(lab, "tools", "claims-v3", "e212", "proposal", "src", "sched"),
             os.path.join(lab, "tools", "claims-v3", "e208", "proposal", "src")]
    lane_roots = sorted(os.path.join(lanes, d) for d in os.listdir(lanes)
                        if d.startswith(("card-", "data-", "a1", "a2", "a3")) and os.path.isdir(os.path.join(lanes, d)))
    hits, masks = {}, {}
    nfiles, big, unreadable, git_dirs = 0, [], 0, 0
    by_root = {}
    for top in roots + lane_roots:
        for dp, dn, fns in os.walk(top):
            if ".git" in dn or ".git" in fns:
                dn[:] = []
                git_dirs += 1
                continue
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
                c = "SUBTRACTED" if subtracted(rel) else (N.lane_card(rel) or N.folder_card(rel, expmap) or N.NONE)
                found = set(N.RX.findall(txt))
                if not found:
                    continue
                fm = sorted({"0x%x" % int(m, 16) for m in NR.MRX.findall(txt)})
                for t in found:
                    hits.setdefault(t, {}).setdefault(c, []).append(rel)
                    masks.setdefault(t, {}).setdefault(c, set()).update(fm)
    sys.path.insert(0, os.path.join(lab, "tools", "matmul", "mm1", "v3.2"))
    import data_v32 as DV  # noqa: E402
    meas_tok, meas_cfg = {}, {}
    for q in DV.time_points() + DV.energy_points():
        meas_tok.setdefault(q["arm"], set()).add((q["kernel"], q["card"]))
        meas_cfg.setdefault(q["arm"], {}).setdefault(q["card"], set()).add("0x%x" % int(q["mask"], 16))
    head = os.popen(f"git -C '{lab}' rev-parse HEAD 2>/dev/null").read().strip()
    rec = {"what": ("E220's never-run scan at its registration, LITERALLY in E218's scanner form (tools/claims-v3/e218/desk/neverrun_e218.py's scan): "
                    "E215's scanner's scan (E213's token rule, roots, folder classes and reader, imported at their pins) over the lab at GitHub main "
                    "and every round card and data lane folder, E220's own folders subtracted, plus MM1-v3.2's measured points"),
           "lab_head": head, "neverrun_e215_sha256": E215_SCAN[1], "neverrun_e213_sha256": NR.E213_SCAN[1], "data_v32_sha256": DATA_V32[1],
           "started": t0, "ended": now(), "files_read": nfiles, "files_read_by_root": by_root,
           "roots": [os.path.relpath(r, lab) for r in roots], "lane_roots": ["W/out/" + os.path.basename(r) for r in lane_roots],
           "expmap": expmap,
           "subtracted_rule": "a path holding '-e220-', or under W/out/card-e220*", "over_400MB_not_read": [
               os.path.relpath(q, lanes) if q.startswith(lanes) else os.path.relpath(q, lab) for q in big],
           "unreadable": unreadable, "git_dirs_not_read": git_dirs,
           "tokens": {t: {c: {"n": len(v), "files": sorted(set(v))[:8]} for c, v in sorted(cs.items())} for t, cs in sorted(hits.items())},
           "masks_by_card": {t: {c: sorted(v) for c, v in sorted(cs.items())} for t, cs in sorted(masks.items())},
           "mm1_v32_measured_tokens": {t: sorted(f"{k} on {c}" for k, c in v) for t, v in sorted(meas_tok.items())},
           "mm1_v32_measured_masks": {t: {c: sorted(v) for c, v in sorted(cs.items())} for t, cs in sorted(meas_cfg.items())}}
    os.makedirs(out, exist_ok=True)
    pth = os.path.join(out, "scan-e220-reg.json")
    json.dump(rec, open(pth, "w"), indent=1, sort_keys=True)
    print(f"scan: {nfiles} files read, {len(hits)} distinct tokens, {len(big)} over 400 MB, {unreadable} unreadable, {git_dirs} git dirs not "
          f"read; lab {head[:12]}; {t0} - {rec['ended']}; scan-e220-reg.json {sha(pth)}")
    return pth


class Never:
    """E218's e218_v32.Never with the card a parameter"""

    def __init__(self, S):
        self.S = S

    def token_any(self, token):
        T = {c: v["n"] for c, v in self.S["tokens"].get(token, {}).items() if c != "SUBTRACTED"}
        meas = self.S["mm1_v32_measured_tokens"].get(token, [])
        return (not T and not meas), {"hits": T, "measured": meas}

    def token_card(self, token, card):
        T = {c: v["n"] for c, v in self.S["tokens"].get(token, {}).items() if c != "SUBTRACTED" and counted_for(card, c)}
        F = {c: v["files"][:3] for c, v in self.S["tokens"].get(token, {}).items() if c != "SUBTRACTED" and counted_for(card, c)}
        meas = [m for m in self.S["mm1_v32_measured_tokens"].get(token, []) if m.endswith(card)]
        return (not T and not meas), {"hits_counted_for_card": T, "files": F, "measured_on_card": meas}

    def config_card(self, token, mask, card):
        m = "0x%x" % int(mask, 16)
        Mb = self.S["masks_by_card"].get(token, {})
        named = sorted(c for c, ms in Mb.items() if c != "SUBTRACTED" and counted_for(card, c) and (m in ms or "any" in ms))
        Mm = self.S["mm1_v32_measured_masks"].get(token, {})
        mpt = sorted(c for c, ms in Mm.items() if c == card and m in ms)
        F = {c: self.S["tokens"].get(token, {}).get(c, {}).get("files", [])[:3] for c in named}
        return (not named and not mpt), {"mask_named_in_files_counted_for_card": named, "files": F, "mask_in_mm1_v32_points_on_card": mpt}

    def verdict(self, family_reading, token, mask, card):
        if family_reading == "config":
            return self.config_card(token, mask, card)
        return self.token_card(token, card)


def report(scan_path, points_path, out):
    S = json.load(open(scan_path))
    NV = Never(S)
    rows = list(csv.DictReader(open(points_path)))
    res = []
    for r in rows:
        card = ARM_CARD[r["arm"]]
        reading = r["neverrun_reading"]
        ok, ev = NV.verdict(reading, r["token"], r["mask"], card)
        res.append({"arm": r["arm"], "id": r["id"], "family": r["family"], "token": r["token"], "mask": r["mask"], "card": card,
                    "reading": reading, "never_run": bool(ok), "evidence": ev})
    rec = {"what": "E220's never-run verdicts per registered point on its own arm's card (desk/neverrun_e220.py report)",
           "scan_sha256": sha(scan_path), "points_sha256": sha(points_path), "scan_window": [S["started"], S["ended"]], "lab_head": S["lab_head"],
           "files_read": S["files_read"], "n_points": len(res), "n_never_run": sum(1 for v in res if v["never_run"]),
           "ran": [v["arm"] + ":" + v["id"] for v in res if not v["never_run"]], "points": res}
    os.makedirs(out, exist_ok=True)
    json.dump(rec, open(os.path.join(out, "neverrun-e220.json"), "w"), indent=1, sort_keys=True)
    lines = [f"E220 never-run report; scan {rec['scan_sha256'][:16]} ({S['files_read']} files, {S['started']} - {S['ended']}, lab {S['lab_head'][:12]})",
             f"points {os.path.basename(points_path)} sha256 {rec['points_sha256'][:16]}: {rec['n_never_run']} of {len(res)} never ran on their arm's card; "
             f"ran: {rec['ran']}"]
    for v in res:
        lines.append(f"{v['arm']} {v['id']:6s} {v['family']:4s} {v['token']:18s} {v['mask']:10s} {v['reading']:6s} never_run={v['never_run']}")
    open(os.path.join(out, "neverrun-e220.txt"), "w").write("\n".join(lines) + "\n")
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
