#!/usr/bin/env python3
"""E215, dated note 2 (post hoc; the fix lane fix-e215d, Q224, Thu 19 Nov 2026): E215's never-run scan with four skips, for later kits.

E215's registered scanner (tools/claims-v3/e215/desk/neverrun_e215.py, pinned 9e68b001...) and, through it, E213's
(tools/claims-v3/e213/desk/neverrun_e213.py, d603ff8b...) run UNCHANGED but for their file reader, which this module wraps. On E215's card days
the registered scan read three of E217's registration-desk files, copied into the round's data lane for E217, as if they held runs (E215.md's
dated note 2 has the account). The wrapped reader gives NO TEXT (the file is read as holding nothing) for:
  SKIP-DESK     a copy of a registration, kit or desk tree: a path holding a 'reg-tree/' segment, or a 'tools/claims-v3/' segment anywhere but
                directly under the lab's own top folder (a data lane's copy of a registration; a kit's stand-in doubles). The registered scanners say
                desk folders are not read; their lane roots let these copies in.
  SKIP-NRDESK   a never-run desk file of any experiment, wherever it sits (scan-eNNN.json, neverrun-eNNN[-x].json/.txt,
                judge-eNNN[-x].json/.txt, configs-eNNN.json, labels-eNNN.json, and this module's own skips-eNNN-x.json): an index of where
                configurations were looked for, never a run.
  SKIP-RECORD   a copy of the cards' committed power record (card-record-eNNN.txt, E217's form): its run strings copy committed runs, which the
                scan reads where they were committed.
and, in a JSON file that is read, it drops every object whose "status" says the configuration did not run (SKIP-PLANNED: a status beginning
'PLANNED', or holding 'not run' or 'NOT RUN') before the text is matched; the rest of the file is read as before.
Every file skipped or thinned is listed, with its rule and what its text held before and after (shapes, masks, GEMM run strings), in
<out>/skips-e215-note2.json. Nothing else of the scan changes: roots, classes, subtraction, MM1-v3.1's points, the report's rules.
The module re-exports the registered scanner's names, e213_module() returning the wrapped reader's module, so a card tool that loads 'the
scanner' by path (neverrun_card_e215.py's form) can load this file instead; such a tool calls set_roots(lab, lanes) before its rescan.
    /usr/bin/python3 -I -B neverrun_skips_note2.py scan --lab <lab> --lanes <lanes folder> --out <dir>
    /usr/bin/python3 -I -B neverrun_skips_note2.py report --scan <dir>/scan-e215.json --points <candidates JSON> --out <dir>
    /usr/bin/python3 -I -B neverrun_skips_note2.py selftest <empty dir>      (stand-in lab and lanes; checks each rule and a kept run)
Standard library only (the registered scan imports MM1-v3.1's data loader, numpy through it, for MM1-v3.1's measured points).
SPDX-License-Identifier: Apache-2.0
"""
import hashlib
import importlib.util
import json
import os
import re
import shutil
import subprocess
import sys
import types

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", "..", ".."))
SCANNER = (os.path.join(REPO, "tools", "claims-v3", "e215", "desk", "neverrun_e215.py"),
           "9e68b0012dd782cd1fcb91806a8213f550294822337de204344bd22b73a89789")
NRDESK = re.compile(r"^(scan|neverrun|judge|configs|labels|skips)-e\d{2,3}(-[A-Za-z0-9]+)?\.(json|txt)(\.gz)?$")
RECORD = re.compile(r"^card-record-e\d{2,3}\.txt(\.gz)?$")
CLAIMS = "/tools/claims-v3/"


def _sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def _load(name, path, pin):
    got = _sha(path)
    if got != pin:
        sys.exit(f"neverrun_skips_note2: REFUSED, {path} is {got}, pinned {pin}")
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


NR = _load("neverrun_e215", *SCANNER)
_N = NR.e213_module()                       # E213's module at its own pin (it exits 4 if not)
ROOTS = {"lab": None, "lanes": None}
SKIPS = []
_KIT = {k: getattr(NR, k) for k in dir(NR) if not k.startswith("__")}
globals().update({k: v for k, v in _KIT.items() if k not in globals()})     # the registered names; scan, report, main, e213_module below


def set_roots(lab, lanes):
    ROOTS["lab"], ROOTS["lanes"] = os.path.abspath(lab), os.path.abspath(lanes)


def _rel(p):
    lab, lanes = ROOTS["lab"], ROOTS["lanes"]
    if lab and p.startswith(lab + os.sep):
        return os.path.relpath(p, lab)
    if lanes and p.startswith(lanes + os.sep):
        return "W/out/" + os.path.relpath(p, lanes)
    return p


def desk_copy(p):
    """SKIP-DESK: a 'reg-tree/' segment, or a 'tools/claims-v3/' segment not directly under the lab's own top folder"""
    if "/reg-tree/" in p:
        return True
    i = p.find(CLAIMS)
    while i >= 0:
        prefix = p[:i]
        own = (prefix == ROOTS["lab"]) if ROOTS["lab"] else os.path.exists(os.path.join(prefix, ".git"))
        if not own:
            return True
        i = p.find(CLAIMS, i + 1)
    return False


def skip_rule(p):
    b = os.path.basename(p)
    if desk_copy(p):
        return "SKIP-DESK"
    if NRDESK.match(b):
        return "SKIP-NRDESK"
    if RECORD.match(b):
        return "SKIP-RECORD"
    return None


def _not_run(s):
    return isinstance(s, str) and (s.startswith("PLANNED") or "not run" in s or "NOT RUN" in s)


def drop_planned(o):
    """(the object without any dict whose 'status' says it did not run, the number dropped)"""
    if isinstance(o, dict):
        if _not_run(o.get("status")):
            return None, 1
        out, n = {}, 0
        for k, v in o.items():
            w, m = drop_planned(v)
            n += m
            if w is not None or v is None:
                out[k] = w
        return out, n
    if isinstance(o, list):
        out, n = [], 0
        for v in o:
            w, m = drop_planned(v)
            n += m
            if w is not None or v is None:
                out.append(w)
        return out, n
    return o, 0


def _held(txt):
    return {"shapes": sorted(set(_N.RX.findall(txt))), "masks": sorted({"0x%x" % int(m, 16) for m in NR.MRX.findall(txt)}),
            "gemm_run_strings": sorted({":".join(t) for t in NR.VRX.findall(txt)}) if ":" in txt else []}


def read_text(p):
    """E213's reader with the four skips (module docstring)"""
    txt = _N_READ(p)
    rule = skip_rule(p)
    if rule:
        if _N.RX.search(txt) or (":" in txt and NR.VRX.search(txt)):
            SKIPS.append({"file": _rel(p), "rule": rule, "before": _held(txt), "after": _held("")})
        return ""
    if (p.endswith(".json") or p.endswith(".json.gz")) and ("PLANNED" in txt or "not run" in txt or "NOT RUN" in txt):
        try:
            obj = json.loads(txt)
        except ValueError:
            return txt
        thin, n = drop_planned(obj)
        if n:
            new = json.dumps(thin, sort_keys=True)
            SKIPS.append({"file": _rel(p), "rule": "SKIP-PLANNED", "objects_dropped": n, "before": _held(txt), "after": _held(new)})
            return new
    return txt


_N_READ = _N.read_text
PN = types.ModuleType("neverrun_e213_skips_note2")
PN.__dict__.update({k: v for k, v in _N.__dict__.items() if not k.startswith("__")})
PN.read_text = read_text


def e213_module():
    return PN


NR.e213_module = e213_module                # the registered scan() and the card tool's rescan() reach E213's module through this name


def scan(lab, lanes, out):
    set_roots(lab, lanes)
    del SKIPS[:]
    NR.scan(ROOTS["lab"], ROOTS["lanes"], out)
    by = {}
    for s in SKIPS:
        by[s["rule"]] = by.get(s["rule"], 0) + 1
    rec = {"what": "the files E215's never-run scan read as holding nothing (SKIP-DESK, SKIP-NRDESK, SKIP-RECORD) or thinned (SKIP-PLANNED), "
                   "by neverrun_skips_note2.py over the registered scanner", "scanner": SCANNER[1], "wrapper": _sha(os.path.abspath(__file__)),
           "files_by_rule": dict(sorted(by.items())), "files": sorted(SKIPS, key=lambda s: s["file"])}
    json.dump(rec, open(os.path.join(out, "skips-e215-note2.json"), "w"), indent=1, sort_keys=True)
    print(f"skips: {len(SKIPS)} files holding a shape or a GEMM run string skipped or thinned; by rule {rec['files_by_rule']}")


def report(scan_path, points_path, out):
    NR.report(scan_path, points_path, out)


def _write(p, txt):
    os.makedirs(os.path.dirname(p), exist_ok=True)
    open(p, "w").write(txt)


def selftest(d):
    """a stand-in lab and lanes tree: each rule skips its file, a run record in a data folder and in a card lane's run folder is kept, a JSON
    index keeps its RAN rows and loses its PLANNED rows; the registered scanner, unwrapped, reads every one (the control)"""
    if os.path.exists(d) and os.listdir(d):
        print(f"selftest: {d} is not empty")
        return 2
    lab, lanes = os.path.join(d, "lab"), os.path.join(d, "lanes")
    for k, fs in NR.S_TILES.items():               # tile_names() hashes the S kinds' registered tiles: copy them in
        for f in fs:
            os.makedirs(os.path.dirname(os.path.join(lab, f)), exist_ok=True)
            shutil.copyfile(os.path.join(REPO, f), os.path.join(lab, f))
    os.makedirs(os.path.join(lab, ".git"))
    run = '{"arm": "gemmL7x7x7", "mask": "0x7", "values": "gemmL7x7x7:tiles:src/tiles/fp32/pow2.bin"}\n'
    _write(os.path.join(lab, "docs/reports/data/2026-01-01-e990-stand-in-aifoundry3/session/runs/001/run.json"), run)
    _write(os.path.join(lab, "tools/claims-v3/e212/proposal/src/sched/a1c1-S9.json"), '{"arms": ["gemmL6x6x1"]}\n')
    _write(os.path.join(lanes, "card-e991/rb/session/runs/001/run.json"), '{"arm": "gemmL5x5x5", "mask": "0x5"}\n')
    _write(os.path.join(lanes, "data-e992/work/reg-tree/tools/claims-v3/e992/desk/configs-e992.json"),
           '{"records": [{"token": "gemmL9x9x9", "mask": "0x9", "status": "PLANNED (stand-in)"}]}\n')
    _write(os.path.join(lanes, "data-e992/work/standin/tools/claims-v3/e992/points-e992.json"), '{"points": ["gemmL9x9x8"]}\n')
    _write(os.path.join(lanes, "data-e993/work/index.json"),
           json.dumps({"rows": [{"token": "gemmL8x8x8", "mask": "0x8", "status": "PLANNED (stand-in, registered; not run at this index)"},
                                {"token": "gemmL4x4x4", "mask": "0x4", "status": "RAN (committed)"},
                                {"token": "gemmL4x4x5", "status": "a2c0-S3 NOT RUN"}]}) + "\n")
    _write(os.path.join(lanes, "data-e994/work/desk/card-record-e994.txt"), "E212 S2 007-1x1x1 gemmL3x3x3:tiles:src/tiles/fp32/lanes2.bin\n")
    _write(os.path.join(lanes, "card-e995/rb/neverrun-A/scan-e995.json"), '{"tokens": {"gemmL2x2x9": {}}}\n')
    _write(os.path.join(lanes, "card-e995/rb/neverrun-A/judge-e995-A.txt"), "gemmL2x2x8 RAN BEFORE\n")
    want_kept = {"gemmL7x7x7", "gemmL6x6x1", "gemmL5x5x5", "gemmL4x4x4"}
    want_gone = {"gemmL9x9x9": "SKIP-DESK", "gemmL9x9x8": "SKIP-DESK", "gemmL8x8x8": "SKIP-PLANNED", "gemmL4x4x5": "SKIP-PLANNED",
                 "gemmL3x3x3": "SKIP-RECORD", "gemmL2x2x9": "SKIP-NRDESK", "gemmL2x2x8": "SKIP-NRDESK"}
    res = {}
    for tag, cmd in (("registered", [sys.executable, "-I", "-B", SCANNER[0], "scan"]),
                     ("wrapped", [sys.executable, "-I", "-B", os.path.abspath(__file__), "scan"])):
        o = os.path.join(d, "out-" + tag)
        r = subprocess.run(cmd + ["--lab", lab, "--lanes", lanes, "--out", o], capture_output=True, text=True)
        if r.returncode != 0:
            print(f"selftest: the {tag} scan failed rc {r.returncode}: {r.stderr[-400:]}")
            return 1
        S = json.load(open(os.path.join(o, "scan-e215.json")))
        res[tag] = {"shapes": sorted(S["tokens"]), "s_kinds": sorted(S["s_kind_gemm_runs_by_card"]),
                    "skips": json.load(open(os.path.join(o, "skips-e215-note2.json")))["files_by_rule"] if tag == "wrapped" else None}
    reg, wr = set(res["registered"]["shapes"]), set(res["wrapped"]["shapes"])
    sk = json.load(open(os.path.join(d, "out-wrapped", "skips-e215-note2.json")))["files"]
    gone_by = {}
    for s in sk:
        for t in set(s["before"]["shapes"]) - set(s["after"]["shapes"]):
            gone_by[t] = s["rule"]
    checks = [("the control (registered, unwrapped) reads every stand-in shape", want_kept | set(want_gone) <= reg),
              ("the wrapped scan keeps the run records (data folder, committed schedule, card lane, a RAN row)", want_kept <= wr),
              ("the wrapped scan reads none of the desk, planned, record and never-run-desk shapes", not (set(want_gone) & wr)),
              ("each one is gone by its own rule", all(gone_by.get(t) == r for t, r in want_gone.items())),
              ("the S-kind run string in the data folder is kept (pow2)", "fp32.pattern:pow2" in res["wrapped"]["s_kinds"]),
              ("the copied power record's S-kind run string is gone (lanes2)", "fp32.pattern:lanes2" in res["registered"]["s_kinds"]
               and "fp32.pattern:lanes2" not in res["wrapped"]["s_kinds"])]
    for what, ok in checks:
        print(f"selftest: {'PASS' if ok else 'FAIL'} {what}")
    print(f"selftest: registered shapes {sorted(reg)}; wrapped shapes {sorted(wr)}; skipped by rule {res['wrapped']['skips']}")
    good = all(ok for _, ok in checks)
    print(f"SELFTEST {'PASS' if good else 'FAIL'} ({sum(ok for _, ok in checks)} of {len(checks)})")
    return 0 if good else 1


def main(argv):
    if argv[:1] == ["scan"] and len(argv) == 7 and argv[1] == "--lab" and argv[3] == "--lanes" and argv[5] == "--out":
        scan(argv[2], argv[4], argv[6])
        return 0
    if argv[:1] == ["report"] and len(argv) == 7 and argv[1] == "--scan" and argv[3] == "--points" and argv[5] == "--out":
        report(argv[2], argv[4], argv[6])
        return 0
    if argv[:1] == ["selftest"] and len(argv) == 2:
        return selftest(os.path.abspath(argv[1]))
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
