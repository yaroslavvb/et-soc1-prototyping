#!/usr/bin/env python3
"""E184's reduction, v3 (dated amendment A3, A3-3; kit note 2, KIT.md.dated-note-2.md section 2): reduce_e184_v2.py (v2, which stays as
committed and whose reduction this file runs unchanged) with A3-3's session gate. Desk only; it never opens a card.

    python3 -B tools/claims-v3/e184/reduce_e184_v3.py <raw dir> --arm S [--t0 <epoch>] > reduced-e184s-v3.json
    python3 -B tools/claims-v3/e184/reduce_e184_v3.py <raw dir> --arm B [--t0 <epoch>] > reduced-e184b-v3.json
    the layout of reduce_e184_v2.py: <raw dir>/<card>/e184{,-smoke,-stoptest}/p184NN/ and <raw dir>/<card>/logs/ (the box's build/e184/,
    which now also holds runbook step 7's reads, config-<arm>-step7-<epoch>.json, written there by rb/s09_reads_e184_v2.sh).

What changes from v2, and nothing else: the session gate's config reads (A3-3).
  1. A session read is MISSING when its attempt was recorded (config-<arm>-t<T0>-<edge>.json.time, which the session writes after every
     attempt, `date -Iseconds` on the box) and its file is absent, empty or holds no JSON object. A read that is a JSON object is the
     session's own: v2's checks, unchanged (a moved read leaves the arm NOT SCORED whatever step 7 reads). A dry read in a real session's
     file is never replaced. A missing read with no attempt recorded is never replaced.
  2. A missing START read is replaced by the NEWEST step-7 read of the arm taken in the 90 minutes before T0; a missing END read by the
     OLDEST taken in the 30 minutes after the end read's attempt (the step-7 read's time is the epoch in its name, the box's clock, as T0
     and the .time files). A step-7 file that holds no JSON object is not a read.
  3. The replacement is checked as the session's own read would be (aifoundry3 TDP 0 W, 65 C, 600 MHz; card 1 600 MHz and the same TDP and
     threshold at both ends) and named in session.departures; session.config_from says where each edge's read came from.
  4. Every step-7 read found is listed (session.step7_reads), and one taken after the end read's attempt is reported beside a present end
     read (session.reported_step7_after_end), never gated.
Everything else of the session gate is v2's: the T0 (--t0, else the newest real log), "smoke gate passed" in that log, the smoke checked again
at the desk, and the registered reads. reduce_s and reduce_b are v2's, called unchanged.
SPDX-License-Identifier: Apache-2.0
"""
import argparse
import datetime
import glob
import io
import json
import os
import re
import sys
from contextlib import redirect_stdout

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import reduce_e184_v2 as r2  # noqa: E402

chk = r2.chk
CARDS, SMOKES = r2.CARDS, r2.SMOKES
BEFORE_S = 5400          # A3-3: the start read's window, the 90 minutes before T0
AFTER_S = 1800           # A3-3: the end read's window, the 30 minutes after the end read's attempt


def attempt_epoch(path):
    """the session's record of a read's attempt (<read>.time: `date -Iseconds` on the box), as epoch seconds; None if absent or unread"""
    try:
        s = open(path).read().strip()
    except OSError:
        return None
    try:
        return int(datetime.datetime.fromisoformat(s).timestamp())
    except ValueError:
        return None


def iso(ep):
    return datetime.datetime.fromtimestamp(ep, datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ") if ep is not None else None


def step7_reads(logs, arm):
    out = []
    for p in glob.glob(os.path.join(logs, "config-%s-step7-*.json" % arm)):
        mt = re.match(r"config-%s-step7-(\d+)\.json$" % arm, os.path.basename(p))
        if not mt:
            continue
        try:
            d = json.load(open(p))
        except (OSError, ValueError):
            d = None
        out.append({"file": os.path.basename(p), "epoch": int(mt.group(1)), "utc": iso(int(mt.group(1))),
                    "config": d if isinstance(d, dict) and not d.get("dry") else None})
    return sorted(out, key=lambda x: (x["epoch"], x["file"]))


def pick(reads, edge, t0, tm):
    ok = [x for x in reads if x["config"] is not None]
    if edge == "start":
        c = [x for x in ok if t0 - BEFORE_S <= x["epoch"] <= t0]
        return c[-1] if c else None
    c = [x for x in ok if tm <= x["epoch"] <= tm + AFTER_S]
    return c[0] if c else None


def session_gate(raw, arm, t0):
    card = CARDS[arm]
    logs = os.path.join(raw, card, "logs")
    g = {"logs_dir": os.path.relpath(logs, raw), "t0": t0, "reasons": [], "departures": [], "gate": "reduce_e184_v3.py (A3-3)"}
    cands = []
    for p in glob.glob(os.path.join(logs, "session-%s-t*.log" % arm)):
        mt = re.match(r"session-%s-t(\d+)\.log$" % arm, os.path.basename(p))
        if mt:
            cands.append(int(mt.group(1)))
    if t0 is None:
        t0 = max(cands) if cands else None
        g["t0"] = t0
        g["t0_from"] = "the newest real session log" if t0 else None
    else:
        g["t0_from"] = "--t0"
    g["session_logs_found"] = sorted(cands)
    log = os.path.join(logs, "session-%s-t%s.log" % (arm, t0)) if t0 else None
    if not log or not os.path.exists(log):
        g["reasons"].append("no session log for T0 %s in %s" % (t0, g["logs_dir"]))
        txt = ""
    else:
        txt = open(log, errors="replace").read()
    g["log_smoke_gate_passed"] = "smoke gate passed" in txt
    g["log_session_end"] = ("session end (T0 %s)" % t0) in txt
    if txt and not g["log_smoke_gate_passed"]:
        g["reasons"].append("the session log has no 'smoke gate passed' line")
    sp = os.path.join(raw, card, "e184-smoke", SMOKES[arm])
    if os.path.isdir(sp):
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = chk.smoke(sp)
        g["desk_smoke"] = buf.getvalue().strip()
        if rc != 0:
            g["reasons"].append("the smoke, checked again at the desk: " + g["desk_smoke"][:300])
    else:
        g["desk_smoke"] = None
        g["reasons"].append("no smoke pass in the raw copy")
    reads = step7_reads(logs, arm)
    g["step7_reads"] = reads
    cfg, frm, tms = {}, {}, {}
    for edge in ("start", "end"):
        p = os.path.join(logs, "config-%s-t%s-%s.json" % (arm, t0, edge)) if t0 else None
        tm = attempt_epoch(p + ".time") if p else None
        tms[edge] = tm
        try:
            d = json.load(open(p)) if p else None
        except (OSError, ValueError):
            d = None
        if isinstance(d, dict) and d.get("dry"):
            g["reasons"].append("the %s config read for T0 %s is a dry read in a real session's file (never replaced)" % (edge, t0))
            cfg[edge], frm[edge] = None, "a dry read"
        elif isinstance(d, dict):
            cfg[edge], frm[edge] = d, "the session's own read"
        elif tm is None:
            g["reasons"].append("no %s config read for T0 %s, and no record of its attempt (no .time file): not replaced (A3-3)" % (edge, t0))
            cfg[edge], frm[edge] = None, None
        else:
            sub = pick(reads, edge, t0, tm)
            if sub is None:
                g["reasons"].append("no %s config read for T0 %s (its attempt at %s returned nothing), and no step-7 read in A3-3's window "
                                    "(%s): not replaced" % (edge, t0, iso(tm), "the 90 minutes before T0" if edge == "start" else
                                                            "the 30 minutes after that attempt"))
                cfg[edge], frm[edge] = None, None
            else:
                cfg[edge], frm[edge] = sub["config"], "step 7's read %s (A3-3)" % sub["file"]
                g["departures"].append("the %s config read for T0 %s is missing (its attempt at %s returned nothing); replaced by step 7's "
                                       "read %s, taken at %s (dated amendment A3, A3-3)" % (edge, t0, iso(tm), sub["file"], sub["utc"]))
    g["config"] = cfg
    g["config_from"] = frm
    g["config_attempt_utc"] = {e: iso(tms[e]) for e in tms}
    if tms.get("end") is not None and frm.get("end") == "the session's own read":
        after = [x for x in reads if x["config"] is not None and tms["end"] <= x["epoch"] <= tms["end"] + AFTER_S]
        g["reported_step7_after_end"] = after[0] if after else None
    a, b = cfg.get("start") or {}, cfg.get("end") or {}
    if a and b:
        if arm == "S":
            for edge, x in (("start", a), ("end", b)):
                if not (x.get("tdp_w") == 0 and x.get("temp_threshold_c") == 65 and x.get("minion_mhz") == 600):
                    g["reasons"].append("the %s config read (%s) is not TDP 0 W / 65 C / 600 MHz: %s" % (
                        edge, frm[edge], json.dumps(x, sort_keys=True)[:200]))
        else:
            for edge, x in (("start", a), ("end", b)):
                if x.get("minion_mhz") != 600:
                    g["reasons"].append("the %s config read (%s) is not 600 MHz" % (edge, frm[edge]))
            for k in ("tdp_w", "temp_threshold_c"):
                if a.get(k) != b.get(k):
                    g["reasons"].append("%s changed between the start and end reads (%s, %s)" % (k, a.get(k), b.get(k)))
    g["gate_ok"] = not g["reasons"]
    return g


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("raw")
    ap.add_argument("--arm", choices=["S", "B"], required=True)
    ap.add_argument("--t0", type=int, default=None)
    a = ap.parse_args()
    res = r2.reduce_s(a.raw) if a.arm == "S" else r2.reduce_b(a.raw)
    res["reducer"] = "reduce_e184_v3.py (v2's reduction, unchanged; A3-3's session gate)"
    res["session"] = session_gate(a.raw, a.arm, a.t0)
    print(json.dumps(res, indent=1, sort_keys=True))


if __name__ == "__main__":
    main()
