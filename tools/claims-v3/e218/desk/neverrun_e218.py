#!/usr/bin/env python3
"""E218 (Q230) desk: which of E218's points never ran on aifoundry3 card 0 - THE DECLARED SCAN, LITERALLY (DECLARED-v32.md sections 9.1 and 10:
E218's points are decided at its registration by section 9's rule on the landed MM1-v3.2 and a fresh never-run scan). Reads files, writes only
its report.

    /usr/bin/python3 -I -B tools/claims-v3/e218/desk/neverrun_e218.py scan --lab <the lab at GitHub main> --lanes <W/out> --out <dir>
        E215's scanner's scan (tools/claims-v3/e215/desk/neverrun_e215.py at its pin, with E213's neverrun_e213.py at its pin through it: the
        token rule, the roots, the folder classes, the reader and the mask reading) over the lab's committed data folders (docs/reports/data),
        E212's and E208's committed schedules and arms, and EVERY round lane folder under W/out whose name starts card-, data-, a1, a2 or a3
        (E216's and E217's included: this is the literal scan the fit lane could not run), gzip read through; E218's own folders SUBTRACTED
        (a data folder whose name holds '-e218-'; W/out/card-e218*); plus MM1-v3.2's measured points (its data loader data_v32.py as landed:
        every point MM1-v3.2 read, E214 and E215 among them). Beside it, REPORTED and never deciding: the fit lane's stand-in (every shape token
        E217's committed registration names counted for every card at every mask; E216's registered points counted on aifoundry2 card 0).
        Writes <dir>/scan-e218-reg.json.
    /usr/bin/python3 -I -B tools/claims-v3/e218/desk/neverrun_e218.py report --scan <scan-e218-reg.json> --points <points-e218.csv> --out <dir>
        each point's verdict by its family's reading (e218_v32.py's Never class, imported at its pin): F the shape token never ran on ANY card;
        G and Gt the token never ran on aifoundry3 card 0 (no hit counted for it by E213's classes - a folder naming aifoundry3 or a3, or naming
        no card - and no MM1-v3.2 point of the token there); Y the configuration (shape, mask) never ran on aifoundry3 card 0 (no MM1-v3.2
        point holds it there and no scanned file counted for the card holding the shape token names the mask). Under the literal scan (the
        registered verdict) and under the literal scan plus the stand-in (REPORTED). Writes <dir>/neverrun-e218.json and .txt.
Standard library and numpy (through e218_v32.py's module import; nothing numerical runs here). Single-threaded.
Not read: the model session's uncommitted folders on its boxes (the orchestrator's rule of 23:18:35 PST Mon 16 Nov 2026); aifoundry1's and
aifoundry3's own disks; desk folders (registrations, models, kits, verifiers: E213's rule); a scratch clone inside a lane folder (a .git entry).
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
E218_V32 = ("tools/matmul/mm1/v3.2/e218_v32.py", "75ce6e161ecf7115c0e6c41b42a2c8bf7d9a4a8342a1f40526eed290db9ef1c8")
DATA_V32 = ("tools/matmul/mm1/v3.2/data_v32.py", "72574b86a1dc0546eeee3348503f84b7ec56556cd7c451c99d2d6206ec205fa6")
LANDED_POINTS = ("tools/matmul/mm1/v3.2/out/e218/points-e218.csv", "1771826ee5a05327a2516b51345f9f0ef198c029b072e3d587e3d490cac54936")
A3 = "aifoundry3 card 0"


def now():
    return datetime.datetime.now().astimezone().strftime("%Y-%m-%d %H:%M:%S %Z")


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def pinned(lab, rel, want):
    p = os.path.join(lab, rel)
    got = sha(p)
    if got != want:
        print(f"neverrun_e218: REFUSED, {rel} is {got}, pinned {want}")
        sys.exit(4)
    return p


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def subtracted(rel):
    """E218's own folders (none exists before its card day): a data folder whose name holds '-e218-', the card lane W/out/card-e218*"""
    return ("-e218-" in rel) or rel.startswith("W/out/card-e218")


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
    # REPORTED beside: the fit lane's stand-in (e218_v32.py's scan, its third change), never deciding a verdict here
    s_hits, s_masks, s_src = {}, {}, {}
    e217 = os.path.join(lab, "tools", "claims-v3", "e217", "proposal", "src")
    if os.path.isdir(e217):
        files = []
        for dp, dn, fns in os.walk(e217):
            dn.sort()
            for fn in sorted(fns):
                if fn.endswith(".json"):
                    q = os.path.join(dp, fn)
                    rel = os.path.relpath(q, lab)
                    for t in set(N.RX.findall(N.read_text(q))):
                        s_hits.setdefault(t, {}).setdefault(N.NONE, []).append(rel)
                        s_masks.setdefault(t, {}).setdefault(N.NONE, set()).add("any")
                    files.append(rel)
        s_src["E217"] = {"files": len(files), "counted_as": "every card ('no card named') at every mask ('any')"}
    e216 = os.path.join(lab, "tools", "claims-v3", "e216", "points-e216.csv")
    if os.path.exists(e216):
        rows = list(csv.DictReader(open(e216)))
        for r in rows:
            arm = r.get("arm") or r.get("arm_token")
            mk = r.get("mask") or r.get("shire_mask") or "0xffffffff"
            for t in set(N.RX.findall(f"{arm} {mk}")):
                s_hits.setdefault(t, {}).setdefault("aifoundry2 card 0", []).append("tools/claims-v3/e216/points-e216.csv")
                s_masks.setdefault(t, {}).setdefault("aifoundry2 card 0", set()).add("0x%x" % int(mk, 16))
        s_src["E216"] = {"rows": len(rows), "sha256": sha(e216), "counted_as": "aifoundry2 card 0 at the registered masks"}
    sys.path.insert(0, os.path.join(lab, "tools", "matmul", "mm1", "v3.2"))
    import data_v32 as DV  # noqa: E402
    meas_tok, meas_cfg = {}, {}
    for q in DV.time_points() + DV.energy_points():
        meas_tok.setdefault(q["arm"], set()).add((q["kernel"], q["card"]))
        meas_cfg.setdefault(q["arm"], {}).setdefault(q["card"], set()).add("0x%x" % int(q["mask"], 16))
    head = os.popen(f"git -C '{lab}' rev-parse HEAD 2>/dev/null").read().strip()
    rec = {"what": ("E218's never-run scan at its registration, LITERALLY as DECLARED-v32.md section 9.1 names it: E215's scanner's scan (E213's "
                    "token rule, roots, folder classes and reader, imported at their pins) over the lab at GitHub main and every round card and "
                    "data lane folder (E216's and E217's read), E218's own folders subtracted, plus MM1-v3.2's measured points; the fit lane's "
                    "stand-in beside it, REPORTED"),
           "lab_head": head, "neverrun_e215_sha256": E215_SCAN[1], "neverrun_e213_sha256": NR.E213_SCAN[1], "data_v32_sha256": DATA_V32[1],
           "started": t0, "ended": now(), "files_read": nfiles, "files_read_by_root": by_root,
           "roots": [os.path.relpath(r, lab) for r in roots], "lane_roots": ["W/out/" + os.path.basename(r) for r in lane_roots],
           "subtracted_rule": "a path holding '-e218-', or under W/out/card-e218*", "over_400MB_not_read": [
               os.path.relpath(q, lanes) if q.startswith(lanes) else os.path.relpath(q, lab) for q in big],
           "unreadable": unreadable, "git_dirs_not_read": git_dirs,
           "tokens": {t: {c: {"n": len(v), "files": sorted(set(v))[:6]} for c, v in sorted(cs.items())} for t, cs in sorted(hits.items())},
           "masks_by_card": {t: {c: sorted(v) for c, v in sorted(cs.items())} for t, cs in sorted(masks.items())},
           "mm1_v32_measured_tokens": {t: sorted(f"{k} on {c}" for k, c in v) for t, v in sorted(meas_tok.items())},
           "mm1_v32_measured_masks": {t: {c: sorted(v) for c, v in sorted(cs.items())} for t, cs in sorted(meas_cfg.items())},
           "standin_REPORTED": {"sources": s_src,
                                "tokens": {t: {c: {"n": len(v), "files": sorted(set(v))[:3]} for c, v in sorted(cs.items())} for t, cs in sorted(s_hits.items())},
                                "masks_by_card": {t: {c: sorted(v) for c, v in sorted(cs.items())} for t, cs in sorted(s_masks.items())}}}
    os.makedirs(out, exist_ok=True)
    pth = os.path.join(out, "scan-e218-reg.json")
    json.dump(rec, open(pth, "w"), indent=1, sort_keys=True)
    print(f"scan: {nfiles} files read, {len(hits)} distinct tokens, {len(big)} over 400 MB, {unreadable} unreadable, {git_dirs} git dirs not "
          f"read; lab {head[:12]}; {t0} - {rec['ended']}; scan-e218-reg.json {sha(pth)}")
    return pth


def union(S):
    """the literal scan plus the stand-in (REPORTED)"""
    U = json.loads(json.dumps(S))
    st = S["standin_REPORTED"]
    for t, cs in st["tokens"].items():
        for c, v in cs.items():
            d = U["tokens"].setdefault(t, {}).setdefault(c, {"n": 0, "files": []})
            d["n"] += v["n"]
            d["files"] = (d["files"] + v["files"])[:6]
    for t, cs in st["masks_by_card"].items():
        for c, v in cs.items():
            U["masks_by_card"].setdefault(t, {}).setdefault(c, [])
            U["masks_by_card"][t][c] = sorted(set(U["masks_by_card"][t][c]) | set(v))
    return U


def verdicts(NV, rows):
    out = []
    for r in rows:
        fam = r["family"]
        if fam == "F":
            ok, ev = NV.token_any(r["arm"])
            rule = "F: the shape token never ran on any card"
        elif fam in ("G", "Gt"):
            ok, ev = NV.token_a3(r["arm"])
            rule = "G/Gt: the token never ran on aifoundry3 card 0 (E213's classes)"
        elif fam == "Y":
            ok, ev = NV.config_a3(r["arm"], r["mask"])
            rule = "Y: the configuration (shape, mask) never ran on aifoundry3 card 0"
        else:
            raise SystemExit(f"neverrun_e218: no reading for {r['id']} ({fam})")
        out.append({"id": r["id"], "family": fam, "token": r["arm"], "mask": r["mask"], "never_run": bool(ok), "rule": rule, "evidence": ev})
    return out


def report(scan_path, points_path, out):
    lab = REPO
    E = load("e218_v32_pinned", pinned(lab, *E218_V32))
    S = json.load(open(scan_path))
    rows = list(csv.DictReader(open(points_path)))
    lit = verdicts(E.Never(S), rows)
    uni = verdicts(E.Never(union(S)), rows)
    res = {"what": "E218's never-run verdicts per point (desk/neverrun_e218.py report): the literal scan decides; the stand-in union is REPORTED",
           "scan_sha256": sha(scan_path), "points_sha256": sha(points_path), "points_path": os.path.relpath(points_path, lab),
           "landed_points_sha256_pinned": LANDED_POINTS[1], "points_are_the_landed_file": sha(points_path) == LANDED_POINTS[1],
           "scan_window": [S["started"], S["ended"]], "lab_head": S["lab_head"], "files_read": S["files_read"],
           "literal": {"n_points": len(lit), "n_never_run": sum(1 for v in lit if v["never_run"]),
                       "ran": [v["id"] for v in lit if not v["never_run"]], "points": lit},
           "standin_union_REPORTED": {"n_never_run": sum(1 for v in uni if v["never_run"]), "ran": [v["id"] for v in uni if not v["never_run"]],
                                      "points": uni}}
    os.makedirs(out, exist_ok=True)
    json.dump(res, open(os.path.join(out, "neverrun-e218.json"), "w"), indent=1, sort_keys=True)
    lines = [f"E218 never-run report; scan {res['scan_sha256'][:16]} ({S['files_read']} files, {S['started']} - {S['ended']}, lab {S['lab_head'][:12]})",
             f"points {os.path.relpath(points_path, lab)} sha256 {res['points_sha256'][:16]} (the landed file: {res['points_are_the_landed_file']})",
             f"LITERAL (registered): {res['literal']['n_never_run']} of {len(lit)} never ran on aifoundry3 card 0 by their family's reading; "
             f"ran: {res['literal']['ran']}",
             f"literal + the fit lane's stand-in (REPORTED): {res['standin_union_REPORTED']['n_never_run']} of {len(uni)}; ran: "
             f"{res['standin_union_REPORTED']['ran']}"]
    for v, u in zip(lit, uni):
        lines.append(f"{v['id']:5s} {v['family']:2s} {v['token']:16s} {v['mask']:10s} never_run={v['never_run']} (with stand-in {u['never_run']}) "
                     f"{json.dumps(v['evidence'], sort_keys=True)[:220]}")
    open(os.path.join(out, "neverrun-e218.txt"), "w").write("\n".join(lines) + "\n")
    print("\n".join(lines[:4]))


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
