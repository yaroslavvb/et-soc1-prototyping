#!/usr/bin/env python3
"""E216 (Q227) desk: which shape tokens ever ran on aifoundry2 card 0 - E213's never-run scan (tools/claims-v3/e213/desk/neverrun_e213.py,
imported unchanged at its pin: its token rule, roots, folder classes and reader) re-run at this registration over every committed data folder of
the lab (docs/reports/data), E212's and E208's committed schedules, and the round's card and data lane folders under W/out, plus MM1-v3's and
MM1-v3.1's measured points (their data loaders). Standard library (numpy through the data loaders); reads files, writes only its report.

    python3 -I -B tools/claims-v3/e216/desk/neverrun_e216.py scan --lab <the lab at GitHub main> --lanes <W/out> --out <dir>
        writes <dir>/scan-e216.json

E216'S DEPARTURES FROM E213'S SCAN (stated before it ran):
  - nothing is SUBTRACTED (E216 has no folder of its own yet; E213's own folders are read like any other);
  - NO E215 DATUM IS OPENED: a lane folder whose name holds 'e215' (card-e215a, card-e215b, and every later E215 lane) is left out of the lane
    view before the scan starts, so not one of its files is opened (Q227's rule: no lane of the round opens an E215 data file before E216's
    registration is pushed); the lab is read at this registration's scratch clone, whose HEAD holds no E215 data folder (the scan records it);
  - MM1-v3.1's measured points (data_v31.time_points and energy_points) are read beside MM1-v3's.
THE RULE (point_rule_e216.py applies it): a token NEVER RAN on aifoundry2 card 0 when it has no hit COUNTED for that card (E213's classes: a
folder naming aifoundry2 or a2c0, or naming no card) and no MM1-v3 or MM1-v3.1 measured point of the token on that card. The token is
E213's (gemmL<MB>x<NB>x<KB>, gemmLn.., gemmLnc.., matched whole): a shape-level reading, the strictest - a shape that ran on the card in any
format, data kind or mask is not new.
SPDX-License-Identifier: Apache-2.0
"""
import argparse
import datetime
import hashlib
import importlib.util
import json
import os
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", "..", "..", ".."))
E213_SCAN = ("tools/claims-v3/e213/desk/neverrun_e213.py", "d603ff8b4fac97a8adbafe0bf4ea0e99e555576c7601c93484362c0cd3500546")
A2 = "aifoundry2 card 0"
LANE_PREFIXES = ("card-", "data-", "a1", "a2", "a3")


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def e213_module(lab):
    p = os.path.join(lab, E213_SCAN[0])
    if sha(p) != E213_SCAN[1]:
        print("neverrun_e216: REFUSED, E213's scanner is not at its pin")
        sys.exit(4)
    spec = importlib.util.spec_from_file_location("neverrun_e213", p)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    m.subtracted = lambda rel: False
    return m


def scan(lab, lanes, out):
    t0 = datetime.datetime.now().astimezone().strftime("%Y-%m-%d %H:%M:%S %Z")
    E = e213_module(lab)
    os.makedirs(out, exist_ok=True)
    view = os.path.join(out, "lane-view")
    if os.path.isdir(view):
        shutil.rmtree(view)
    os.makedirs(view)
    kept, left_out = [], []
    for d in sorted(os.listdir(lanes)):
        if not d.startswith(LANE_PREFIXES):
            continue
        if "e215" in d.lower() or "e216" in d.lower():
            left_out.append(d)
            continue
        os.symlink(os.path.join(lanes, d), os.path.join(view, d))
        kept.append(d)
    data_dirs = sorted(os.listdir(os.path.join(lab, "docs", "reports", "data")))
    e215_data = [d for d in data_dirs if "e215" in d.lower()]
    if e215_data:
        print("neverrun_e216: REFUSED, the lab holds an E215 data folder:", e215_data)
        sys.exit(5)
    E.scan(lab, view, out)
    rec = json.load(open(os.path.join(out, "scan-e213.json")))
    os.remove(os.path.join(out, "scan-e213.json"))
    shutil.rmtree(view)
    v31 = os.path.join(lab, "tools", "matmul", "mm1", "v3.1")
    sys.path.insert(0, v31)
    import data_v31 as DV  # noqa: E402
    m31 = {}
    for p in DV.time_points():
        m31.setdefault(p["arm"], set()).add((p.get("kernel"), p["card"], "time"))
    for e in DV.energy_points():
        m31.setdefault(e["arm"], set()).add((e.get("kernel"), e["card"], "energy"))
    rec.update({"what": "E216's never-run scan (E213's scanner at its pin; nothing subtracted; no E215 lane opened)", "e213_scanner": E213_SCAN,
                "lanes_read": kept, "lanes_left_out_never_opened": left_out, "lab_head_has_e215_data_folder": False,
                "mm1_v31_measured_points": {t: sorted(f"{k} on {c} ({w})" for k, c, w in v) for t, v in sorted(m31.items())},
                "data_v31_sha256": sha(os.path.join(v31, "data_v31.py")), "started_e216": t0,
                "ended_e216": datetime.datetime.now().astimezone().strftime("%Y-%m-%d %H:%M:%S %Z"),
                "interpreter": "/usr/bin/python3 " + sys.version.split()[0]})
    json.dump(rec, open(os.path.join(out, "scan-e216.json"), "w"), indent=1, sort_keys=True)
    print(f"scan-e216: {rec['files_read']} files, {len(rec['tokens'])} tokens; lanes read {len(kept)}, left out {left_out}")


def ran_on_a2(S, token):
    """the scan's evidence that a token ran on aifoundry2 card 0 (empty list = never ran there)"""
    ev = []
    for c, v in (S["tokens"].get(token) or {}).items():
        if c in (A2, "no card named"):
            ev.append(f"{v['n']} file(s) counted for {c}: {v['files'][:2]}")
    for x in S["mm1_v3_measured_points"].get(token, []):
        if x.endswith("on " + A2):
            ev.append("MM1-v3 measured point " + x)
    for x in S["mm1_v31_measured_points"].get(token, []):
        if (" on " + A2 + " (") in x:
            ev.append("MM1-v3.1 measured point " + x)
    return ev


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    a1 = sub.add_parser("scan")
    a1.add_argument("--lab", required=True)
    a1.add_argument("--lanes", required=True)
    a1.add_argument("--out", required=True)
    a = ap.parse_args()
    if a.cmd == "scan":
        scan(os.path.abspath(a.lab), os.path.abspath(a.lanes), os.path.abspath(a.out))


if __name__ == "__main__":
    main()
