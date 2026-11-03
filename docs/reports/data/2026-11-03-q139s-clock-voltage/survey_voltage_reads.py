#!/usr/bin/env python3
"""Q139(s): every committed read-only voltage read, gathered. Standard library only. Desk; no device command.

    python3 survey_voltage_reads.py <lab repo root> --out voltage-reads.json [--jobs 6]

Walks docs/reports/data/ for telemetry (*.jsonl, *.jsonl.gz) and, in every record that carries the minion clock
(`mhz.minion`, DM_CMD_GET_ASIC_FREQUENCIES) and at least one minion voltage, keeps:
  * die_mv.minion  -- DM_CMD_GET_ASIC_VOLTAGE: the on-die PVT voltage monitors (ettelem.cpp sample(), "on-die voltage
                      monitors (PVT), mV");
  * reg_mv.minion  -- DM_CMD_GET_MODULE_VOLTAGE: the regulator set point as the PMIC reports it (250 + 5 x code mV),
                      a read-only PMIC voltage-register read (allowed: the owner's rule of 2 Nov 2026);
  * sp.minion_mv   -- DM_CMD_GET_SP_STATS: the service processor's statistic [avg, min, max] (at et-platform 836a4ab
                      the PVT reading, E118 README D1), and sp.minion_w[0], the minion rail's power as the PMIC reports it;
  * board_w, temp_c.minshire[0] (the die reading).
and the static config reads (`ettelem config` lines: minion_mhz with minion_mv, GET_ASIC_VOLTAGE) in config*.txt/json.

Each record is binned by (card, data dir, session, clock, steady, reg mV, die mV, sp mV, minion-rail W to 0.5 W):
steady = the record's clock equals the previous record's in the same file, within 1 s. The card comes from the
path (aifoundry1-c0 / -c1 / -card0 / aifoundry2 / aifoundry3), else the nearest session.json's host and card, else
the data dir's name, else a fixed list (CARD_BY_DIR, from docs/findings/03-experiments.md). Files it cannot place are
listed, never guessed.
"""
import argparse
import gzip
import json
import os
import re
import sys
from collections import defaultdict
from multiprocessing import Pool

RX_A1 = re.compile(r"aifoundry1[-_]?c(?:ard)?([01])\b|aifoundry1[-_]card([01])")
RX_A = re.compile(r"aifoundry([23])")
# data dirs whose paths name no card (03-experiments.md's host column); aifoundry1 dirs need the card
CARD_BY_DIR = {
    "2026-10-23-e64-horace-power-limit": "aifoundry2",
    "2026-10-27-e69-governor-knob": "aifoundry2",
    "2026-10-31-e80-kinds-speed": "aifoundry2",
    "2026-10-31-e83-kinds-speed-rest": "aifoundry2",
    "2026-10-31-e84-speed-aifoundry1-card0": "aifoundry1c0",
    "2026-11-01-e114-card0-replicates": "aifoundry1c0",
    # aifoundry3 lanes whose paths and session files name no host (CONTEXT section 4: Q129's E74-E76 on aifoundry3;
    # the memory-path lanes E81, E99, E110, E132, E139 on aifoundry3, their READMEs' first lines)
    "2026-10-28-e74-register-file-cells": "aifoundry3",
    "2026-10-28-e75-memory-flip-ladder": "aifoundry3",
    "2026-10-28-e76-trapped-instructions": "aifoundry3",
    "2026-10-31-e81-dram-pattern": "aifoundry3",
    "2026-11-01-e99-dram-mechanism": "aifoundry3",
    "2026-11-01-e110-memory-width": "aifoundry3",
    "2026-11-02-e132-memory-split": "aifoundry3",
    "2026-11-02-e139-memory-split-more-passes": "aifoundry3",
}


def card_from_text(s):
    m = RX_A1.search(s)
    if m:
        return "aifoundry1c" + (m.group(1) or m.group(2))
    m = RX_A.search(s)
    if m:
        return "aifoundry" + m.group(1)
    return None


def card_from_session(path, root):
    d = os.path.dirname(path)
    while len(d) > len(root):
        p = os.path.join(d, "session.json")
        if os.path.exists(p):
            try:
                s = json.load(open(p))
            except Exception:
                return None
            host = s.get("host") or (s.get("protocol") or {}).get("card")
            if not host:
                return None
            if host == "aifoundry1":
                dev = s.get("device", (s.get("protocol") or {}).get("device"))
                card = (s.get("protocol") or {}).get("card", "")
                c = card_from_text(str(card))
                if c and c.startswith("aifoundry1c"):
                    return c
                if dev is not None:
                    return f"aifoundry1c{int(dev)}"
                return None
            return card_from_text(host)
        d = os.path.dirname(d)
    return None


def data_rel(path, root):
    return os.path.relpath(path, os.path.join(root, "docs", "reports", "data"))


def resolve_card(path, root):
    rel = data_rel(path, root)
    top = rel.split(os.sep)[0]
    c = card_from_text(rel)
    if c and c != "aifoundry1":
        return c, "path"
    c = card_from_session(path, root)
    if c:
        return c, "session.json"
    if top in CARD_BY_DIR:
        return CARD_BY_DIR[top], "CARD_BY_DIR"
    return None, None


def opener(p):
    return gzip.open(p, "rt", errors="replace") if p.endswith(".gz") else open(p, errors="replace")


def scan(args):
    path, root = args
    card, how = resolve_card(path, root)
    rel = data_rel(path, root)
    parts = rel.split(os.sep)
    top = parts[0]
    sess = parts[1] if len(parts) > 2 else "."
    bins = defaultdict(lambda: [0, 0.0, 0.0, 0.0, 0.0])
    n = 0
    tmin = tmax = None
    try:
        with opener(path) as fh:
            first = fh.readline()
            skipped = 0
            while first and not first.startswith("{") and skipped < 20:   # e.g. "Opening device 0" (E84, E114)
                first = fh.readline()
                skipped += 1
            if not first or ('"mhz"' not in first and '"minion_mhz"' not in first):
                return None
            if '"die_mv"' not in first and '"reg_mv"' not in first and '"minion_mv"' not in first:
                return None
            prev_f = prev_t = None
            for line in [first] + list(fh):
                if not line.startswith("{"):
                    continue
                try:
                    r = json.loads(line)
                except ValueError:
                    continue
                mhz = r.get("mhz")
                if not isinstance(mhz, dict) or mhz.get("minion") is None:
                    continue
                f = int(mhz["minion"])
                die = (r.get("die_mv") or {}).get("minion")
                reg = (r.get("reg_mv") or {}).get("minion")
                sp = r.get("sp") or {}
                spv = (sp.get("minion_mv") or [None])[0]
                if die is None and reg is None and spv is None:
                    continue
                mw = (sp.get("minion_w") or [None])[0]
                t = r.get("t_ms")
                steady = int(prev_f == f and t is not None and prev_t is not None and 0 <= t - prev_t <= 1000)
                prev_f, prev_t = f, t
                if t is not None:
                    tmin = t if tmin is None else min(tmin, t)
                    tmax = t if tmax is None else max(tmax, t)
                wb = None if mw is None else round(round(float(mw) * 2) / 2, 1)
                key = (f, steady, reg, die, spv, wb)
                b = bins[key]
                b[0] += 1
                b[1] += float(r["board_w"]) if r.get("board_w") is not None else 0.0
                tc = ((r.get("temp_c") or {}).get("minshire") or [None])[0]
                b[2] += float(tc) if tc is not None else 0.0
                b[3] += float(mw) if mw is not None else 0.0
                b[4] += 1 if tc is not None else 0
                n += 1
    except (OSError, EOFError) as e:
        return {"path": rel, "card": card, "how": how, "error": str(e)[:200]}
    if n == 0:
        return None
    return {"path": rel, "card": card, "how": how, "top": top, "sess": sess, "n": n, "t_ms": [tmin, tmax],
            "bins": [list(k) + v for k, v in bins.items()]}


def config_reads(root):
    """ettelem config lines (GET_ASIC_FREQUENCIES + GET_ASIC_VOLTAGE) in committed config*.txt / *.json files."""
    out = []
    for dp, _, fns in os.walk(os.path.join(root, "docs", "reports", "data")):
        for fn in fns:
            if not fn.startswith("config") or not (fn.endswith(".txt") or fn.endswith(".json") or fn.endswith(".jsonl")):
                continue
            p = os.path.join(dp, fn)
            try:
                lines = open(p, errors="replace").read().splitlines()
            except OSError:
                continue
            card, how = resolve_card(p, root)
            for ln in lines:
                ln = ln.strip()
                if not ln.startswith("{") or "minion_mv" not in ln:
                    continue
                try:
                    r = json.loads(ln)
                except ValueError:
                    continue
                if r.get("minion_mhz") is not None and r.get("minion_mv") is not None:
                    out.append({"path": os.path.relpath(p, root), "card": card, "how": how, "mhz": r["minion_mhz"], "mv": r["minion_mv"],
                                "tdp_w": r.get("tdp_w"), "power_state": r.get("power_state_name")})
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("root")
    ap.add_argument("--out", required=True)
    ap.add_argument("--jobs", type=int, default=6)
    a = ap.parse_args()
    root = os.path.abspath(a.root)
    files = []
    for dp, _, fns in os.walk(os.path.join(root, "docs", "reports", "data")):
        for fn in fns:
            if fn.endswith(".jsonl") or fn.endswith(".jsonl.gz"):
                files.append(os.path.join(dp, fn))
    files.sort()
    with Pool(a.jobs) as pool:
        res = [r for r in pool.imap(scan, [(p, root) for p in files], chunksize=8) if r]
    unplaced = sorted({r["path"] for r in res if not r.get("card")})
    out = {"_note": "Q139(s) survey of committed voltage reads; see the docstring of survey_voltage_reads.py",
           "bin_fields": ["mhz", "steady", "reg_mv", "die_mv", "sp_mv", "minion_w_bin", "n", "sum_board_w", "sum_die_c", "sum_minion_w", "n_die_c"],
           "files_scanned": len(files), "files_with_voltage": len(res), "unplaced_files": unplaced,
           "files": res, "config_reads": config_reads(root)}
    json.dump(out, open(a.out, "w"), separators=(",", ":"))
    print(f"scanned {len(files)} files; {len(res)} with voltage reads; {sum(r.get('n', 0) for r in res)} records; "
          f"{len(unplaced)} unplaced; {len(out['config_reads'])} config reads", file=sys.stderr)


if __name__ == "__main__":
    main()
