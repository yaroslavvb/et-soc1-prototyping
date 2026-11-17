#!/usr/bin/env python3
"""E206 (Q198) desk: which of E206's points never ran - a search of every data directory of ours for GEMM records of the lab's host. No card.
Standard library only; the scan mode imports nothing of the lab, so it can run on any box from stdin.

    python3 -I -B neverrun_e206.py scan LABEL DEFAULT TOP [TOP ...] > found.json    (on another box: the same, the script read from stdin)
    python3 -I -B tools/claims-v3/e206/desk/neverrun_e206.py report found.json [found.json ...]
                                                                                     writes desk/neverrun-e206.json and prints desk/neverrun-e206.txt

WHAT COUNTS AS A RUN: any line of any file under a top folder (gzip read through) that is a host record or a host command of a GEMM arm:
  (a) a SPARSITY record ("arm": "gemm...", "type", "values", "minions", "shire_mask"), or
  (b) a command line or argv list with --type, --values <gemm arm>:<kind>:... and --shires (minions = 32 x the mask's shires).
The data kind is read from --values: randn -> random; sparse50 -> sparse50; tiles of zeros.bin -> zeros; tiles under real2/ or real/ -> real.
A record from the simulator (a "ghz" under 0.05, or a line or path naming sys_emu, sysemu, sim-check, sim-runs or simulator) is listed apart and
never counts as a card run. The card is read from
the path (aifoundry1-c1 or a1c1 -> aifoundry1 card 1; aifoundry1-c0 or a1c0 -> aifoundry1 card 0; aifoundry2 or a2- -> aifoundry2; aifoundry3 or a3-
-> aifoundry3); a path naming no card takes the scan's DEFAULT ("unknown" for the lab's data and our lanes' folders, the box itself for a box's own
run folders); "unknown" counts as "a card, not known which": it makes a point not never-run on any card; the counts by card (aifoundry3, card 1)
read only records whose path or box names the card, and a point whose only card records name none is listed apart. Directories holding a .git entry (scratch clones of the lab) are skipped: the lab's committed data are scanned at their
source. A point NEVER RAN on a card if no card run matches its arm, format, data kind, minions and shire mask.
SPDX-License-Identifier: Apache-2.0
"""
import gzip
import json
import os
import re
import socket
import sys
import time

RE_ARM = re.compile(r'"arm"\s*:\s*"(gemm[A-Za-z0-9]+)"')
RE_TYPE = re.compile(r'"type"\s*:\s*"(fp32|fp16|int8)"')
RE_VAL = re.compile(r'"values"\s*:\s*"([^"]*)"')
RE_MIN = re.compile(r'"minions"\s*:\s*(\d+)')
RE_MASK = re.compile(r'"shire_mask"\s*:\s*"(0x[0-9a-fA-F]+)"')
RE_GHZ = re.compile(r'"ghz"\s*:\s*([0-9.eE+-]+)')
RE_CTYPE = re.compile(r'--type"?\s*,?\s*"?(fp32|fp16|int8)\b')
RE_CVAL = re.compile(r'--values"?\s*,?\s*"?(gemm[A-Za-z0-9]+:[^"\s,]*)')
RE_CSH = re.compile(r'--shires"?\s*,?\s*"?(0x[0-9a-fA-F]+)')
MAX_BYTES = 400 * 2 ** 20
SIM_MARKS = ("sys_emu", "sysemu", "sim-check", "sim-runs", "simulator")


def kind_of(values):
    parts = values.split(":", 2)
    gen = parts[1] if len(parts) > 1 else "default"
    rest = parts[2] if len(parts) > 2 else ""
    if gen == "randn":
        return "random"
    if gen == "sparse50":
        return "sparse50"
    if gen == "tiles":
        if "zeros.bin" in rest:
            return "zeros"
        if "real2/" in rest or "/real/" in rest:
            return "real"
        return "tiles:other"
    return gen


def card_of(path, default):
    p = path.lower()
    if "aifoundry1-c1" in p or "a1c1" in p:
        return "aifoundry1 card 1"
    if "aifoundry1-c0" in p or "a1c0" in p:
        return "aifoundry1 card 0"
    if "aifoundry2" in p or "/a2-" in p:
        return "aifoundry2 card 0"
    if "aifoundry3" in p or "/a3-" in p:
        return "aifoundry3 card 0"
    if default in ("aifoundry2", "aifoundry3"):
        return f"{default} card 0"
    return "a card, not known which"


def scan_line(line):
    if "gemm" not in line:
        return None
    m = RE_ARM.search(line)
    if m:
        t, v, mi, mk = RE_TYPE.search(line), RE_VAL.search(line), RE_MIN.search(line), RE_MASK.search(line)
        if not t:
            return None
        values = v.group(1) if v else m.group(1)
        mask = mk.group(1).lower() if mk else "0xffffffff"
        minions = int(mi.group(1)) if mi else 32 * bin(int(mask, 16)).count("1")
        g = RE_GHZ.search(line)
        sim = any(x in line for x in SIM_MARKS) or (g is not None and float(g.group(1)) < 0.05)
        return (m.group(1), t.group(1), kind_of(values), minions, mask, sim, "record")
    t, v = RE_CTYPE.search(line), RE_CVAL.search(line)
    if t and v:
        sh = RE_CSH.search(line)
        mask = sh.group(1).lower() if sh else "0xffffffff"
        values = v.group(1)
        sim = any(x in line for x in SIM_MARKS)
        return (values.split(":", 1)[0], t.group(1), kind_of(values), 32 * bin(int(mask, 16)).count("1"), mask, sim, "command")
    return None


def scan(label, default, tops):
    box = socket.gethostname().split(".")[0]
    found, nfiles, big, bad = {}, 0, [], []
    t0 = time.time()
    for top in tops:
        top = os.path.expanduser(top)
        for dp, dns, fns in os.walk(top):
            if dp != top and ".git" in dns + fns:
                dns[:] = []
                continue
            dns[:] = [d for d in dns if d != ".git"]
            for fn in fns:
                path = os.path.join(dp, fn)
                try:
                    if os.path.islink(path) or not os.path.isfile(path):
                        continue
                    sz = os.path.getsize(path)
                    if sz > MAX_BYTES:
                        big.append(path)
                        continue
                    if fn.endswith(".gz"):
                        with gzip.open(path, "rb") as fh:
                            data = fh.read(MAX_BYTES)
                    else:
                        with open(path, "rb") as fh:
                            data = fh.read()
                except Exception as e:  # noqa: BLE001
                    bad.append(f"{path}: {e!r}"[:300])
                    continue
                nfiles += 1
                if b"gemm" not in data:
                    continue
                for line in data.decode("utf-8", "replace").splitlines():
                    r = scan_line(line)
                    if r is None:
                        continue
                    arm, t, kind, minions, mask, sim, how = r
                    sim = sim or any(x in path for x in SIM_MARKS)
                    key = f"{arm}|{t}|{kind}|{minions}|{mask}"
                    rec = found.setdefault(key, {"cards": {}, "sim": 0, "how": {}, "paths": []})
                    if sim:
                        rec["sim"] += 1
                    else:
                        c = card_of(path, default)
                        rec["cards"][c] = rec["cards"].get(c, 0) + 1
                    rec["how"][how] = rec["how"].get(how, 0) + 1
                    if len(rec["paths"]) < 3 and path not in rec["paths"]:
                        rec["paths"].append(path)
    return {"label": label, "box": box, "default_card": default, "roots": tops, "files_read": nfiles, "files_over_400MB_skipped": big, "unreadable": bad[:50],
            "n_unreadable": len(bad), "seconds": round(time.time() - t0, 1), "found": found}


def pub(path):
    """a path as a public file may show it, with no home folder (a login) in it: a lane's clone of the lab as LAB, the round's lane folders (the
    folder named out that holds them) as OUT, the account's home folder as HOME"""
    path = re.sub(r"^.*/work/clone(?=/|$)", "LAB", path)
    path = re.sub(r"^.*?/out(?=/|$)", "OUT", path)
    return path.replace(os.path.expanduser("~"), "HOME")


def report(paths):
    here = os.path.dirname(os.path.abspath(__file__))
    pts = json.load(open(os.path.join(here, "..", "points-e206.json")))["points"]
    scans = [json.load(open(p)) for p in paths]
    card_runs, sim_runs = {}, {}
    for s in scans:
        for key, rec in s["found"].items():
            for c, n in rec["cards"].items():
                card_runs.setdefault(key, {}).setdefault(c, 0)
                card_runs[key][c] += n
            if rec["sim"]:
                sim_runs[key] = sim_runs.get(key, 0) + rec["sim"]
    rows, cnt = [], {"never_any_card": 0, "never_aifoundry3": 0, "never_card1": 0, "never_any_card_as_shape": 0, "arm_B_points": 0,
                     "never_card1_on_arm_B": 0, "only_unnamed_card_records": 0}
    for p in pts:
        key = f"{p['arm']}|{p['format']}|{p['kind']}|{p['minions']}|{p['shire_mask']}"
        cards = card_runs.get(key, {})
        shape_cards = {}
        for k, v in card_runs.items():
            a, t, kd, mi, mk = k.split("|")
            if a == p["arm"] and t == p["format"] and int(mi) == p["minions"] and mk == p["shire_mask"]:
                for c, n in v.items():
                    shape_cards[c] = shape_cards.get(c, 0) + n
        named = set(cards) - {"a card, not known which"}
        r = {"id": p["id"], "name": p["name"], "key": key, "cards": sorted(cards), "records": sum(cards.values()),
             "never_any_card": not cards, "never_aifoundry3": "aifoundry3 card 0" not in named, "never_card1": "aifoundry1 card 1" not in named,
             "only_unnamed_card_records": bool(cards) and not named,
             "shape_any_kind_cards": sorted(shape_cards), "simulator_records": sim_runs.get(key, 0), "on_arm_B": p["on_arm"]["B"]}
        rows.append(r)
        cnt["never_any_card"] += r["never_any_card"]
        cnt["never_aifoundry3"] += r["never_aifoundry3"]
        cnt["never_card1"] += r["never_card1"]
        cnt["never_any_card_as_shape"] += not shape_cards
        cnt["arm_B_points"] += p["on_arm"]["B"]
        cnt["never_card1_on_arm_B"] += p["on_arm"]["B"] and r["never_card1"]
        cnt["only_unnamed_card_records"] += r["only_unnamed_card_records"]
    out = {"what": "E206's points against every GEMM record found in our data directories (a desk search; see neverrun_e206.py)",
           "scans": [{"label": s["label"], "box": s["box"], "default_card": s["default_card"], "roots": [pub(x) for x in s["roots"]],
                      "files_read": s["files_read"], "files_over_400MB_skipped": [pub(x) for x in s["files_over_400MB_skipped"]],
                      "n_unreadable": s["n_unreadable"], "seconds": s["seconds"]} for s in scans],
           "paths": "LAB = a clone of the lab at GitHub main; OUT = the round's lane folders on aifoundry2; HOME = the lab account's home folder on the box named",
           "counts": cnt, "points": rows,
           "keys_found_on_cards": len(card_runs), "keys_found_in_the_simulator_only": len([k for k in sim_runs if k not in card_runs])}
    json.dump(out, open(os.path.join(here, "neverrun-e206.json"), "w"), indent=1, sort_keys=True)
    print("E206 never-run search (desk): every GEMM record of the lab's host in our data directories")
    for s in out["scans"]:
        print(f"  scan {s['label']} on {s['box']} (default card {s['default_card']}): {s['files_read']} files read under {', '.join(s['roots'])}; over 400 MB skipped "
              f"{len(s['files_over_400MB_skipped'])}; unreadable {s['n_unreadable']}")
    print(f"  distinct GEMM keys (arm, format, kind, minions, mask) seen on a card: {out['keys_found_on_cards']}; in the simulator only: "
          f"{out['keys_found_in_the_simulator_only']}")
    print(f"  E206 points never run on any card: {cnt['never_any_card']} of {len(pts)} (as a shape in any data kind: {cnt['never_any_card_as_shape']}); "
          f"never on aifoundry3: {cnt['never_aifoundry3']}; never on aifoundry1 card 1: {cnt['never_card1']} "
          f"({cnt['never_card1_on_arm_B']} of arm B's {cnt['arm_B_points']}); points whose only card records name no card: "
          f"{cnt['only_unnamed_card_records']}")
    for r in rows:
        if not r["never_any_card"]:
            print(f"  ran before: {r['id']} {r['name']}: {', '.join(r['cards'])} ({r['records']} records)")
    print("  never run on any card: " + " ".join(r["id"] for r in rows if r["never_any_card"]))


def main():
    if len(sys.argv) >= 4 and sys.argv[1] == "scan":
        json.dump(scan(sys.argv[2], sys.argv[3], sys.argv[4:]), sys.stdout, indent=1, sort_keys=True)
        sys.stdout.write("\n")
    elif len(sys.argv) >= 3 and sys.argv[1] == "report":
        report(sys.argv[2:])
    else:
        print(__doc__)
        sys.exit(2)


if __name__ == "__main__":
    main()
