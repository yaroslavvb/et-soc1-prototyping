#!/usr/bin/env python3
"""E184's reduction, v4 (dated amendment A4; kit note 3, KIT.md.dated-note-3.md section 1): reduce_e184_v3.py (v3, which stays as
committed) with A4's session gate, which tests the config reads' KEYS, not their truthiness. v2's reduction runs unchanged, as in v3.
Desk only; it never opens a card.

    python3 -B tools/claims-v3/e184/reduce_e184_v4.py <raw dir> --arm S [--t0 <epoch>] > reduced-e184s-v4.json
    python3 -B tools/claims-v3/e184/reduce_e184_v4.py <raw dir> --arm B [--t0 <epoch>] > reduced-e184b-v4.json
    the layout of reduce_e184_v2.py and v3: <raw dir>/<card>/e184{,-smoke,-stoptest}/p184NN/ and <raw dir>/<card>/logs/ (the box's
    build/e184/, with runbook step 7's reads, config-<arm>-step7-<epoch>.json).

What changes from v3, and nothing else (A4, which corrects A3-3 items 1 and 5 for partial and empty reads):
  1. The three keys are tdp_w, temp_threshold_c and minion_mhz. A key is PRESENT when the read holds it with a value that is not null.
     A read that is a JSON object (not a dry read) with all three present is COMPLETE; one lacking any of them, or holding null for any,
     an empty {} among them, is a FAILED read: what the stock reader prints when a GET fails (tools/ettelem/ettelem.cpp, config(): null
     for a failed TDP or threshold GET, no minion_mhz when the clock GET fails).
  2. A session read is MISSING when its attempt was recorded (its .time file) and its file is absent, empty, holds no JSON object, or holds
     a FAILED read. A MISSING read is replaced as A3-3 says (the newest step-7 read in the 90 minutes before T0 for a start, the oldest in
     the 30 minutes after the end read's attempt for an end), and named in session.departures; with no attempt recorded it is never
     replaced. v3 took any JSON object as the session's own read.
  3. A step-7 file is a read only when it is COMPLETE (v3: any JSON object not a dry read). A failed or empty step-7 file is passed over,
     and the window's next read is taken.
  4. A COMPLETE read, the session's own or its replacement, is checked as registered ON ITS OWN, whatever the other edge holds (v3 checked
     the edges only when both reads were non-empty): aifoundry3 tdp_w 0, temp_threshold_c 65, minion_mhz 600; card 1 minion_mhz 600, and
     once both edges hold a read, tdp_w and temp_threshold_c equal at both. A value matches a registered number only when it is a JSON
     number (true and false are not numbers, though Python reads false == 0). A COMPLETE read not as registered is MOVED: the arm is NOT
     SCORED whatever step 7 reads.
  5. session.config_status names each edge's reading (complete, failed, absent, empty or no JSON object, dry), and session.step7_reads
     marks each step-7 file complete or not.
Everything else is v3's: the T0, the log's "smoke gate passed", the smoke checked again at the desk, a dry read in a real session's file
(never replaced), the windows and their edges, session.reported_step7_after_end (complete reads only, never gated). reduce_s and reduce_b
are v2's, called unchanged.
SPDX-License-Identifier: Apache-2.0
"""
import argparse
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
import reduce_e184_v3 as r3  # noqa: E402

chk = r2.chk
CARDS, SMOKES = r2.CARDS, r2.SMOKES
BEFORE_S, AFTER_S = r3.BEFORE_S, r3.AFTER_S       # A3-3's windows, unchanged
attempt_epoch, iso = r3.attempt_epoch, r3.iso
KEYS = ("tdp_w", "temp_threshold_c", "minion_mhz")
REG_S = {"tdp_w": 0, "temp_threshold_c": 65, "minion_mhz": 600}    # aifoundry3, as registered (E184.md; A3-3 item 4)
REG_B_MHZ = 600                                                     # card 1: 600 MHz, and the same TDP and threshold at both ends


def is_num(v):
    return isinstance(v, (int, float)) and not isinstance(v, bool)


def eq_num(v, want):
    return is_num(v) and v == want


def classify(d):
    """(status, read): status is 'complete', 'failed', 'dry' or 'no JSON object'; read is the object when it is one"""
    if not isinstance(d, dict):
        return "no JSON object", None
    if d.get("dry"):
        return "dry", d
    absent = [k for k in KEYS if d.get(k) is None]
    if absent:
        return "failed (no value for %s)" % ", ".join(absent), d
    return "complete", d


def load(p):
    """(status, object or None) of a config read's file"""
    if not p or not os.path.exists(p):
        return "absent", None
    try:
        raw = open(p).read()
    except OSError:
        return "absent", None
    if not raw.strip():
        return "empty", None
    try:
        d = json.loads(raw)
    except ValueError:
        return "no JSON object", None
    return classify(d)


def step7_reads(logs, arm):
    out = []
    for p in glob.glob(os.path.join(logs, "config-%s-step7-*.json" % arm)):
        mt = re.match(r"config-%s-step7-(\d+)\.json$" % arm, os.path.basename(p))
        if not mt:
            continue
        st, d = load(p)
        out.append({"file": os.path.basename(p), "epoch": int(mt.group(1)), "utc": iso(int(mt.group(1))), "status": st,
                    "config": d if st == "complete" else None})
    return sorted(out, key=lambda x: (x["epoch"], x["file"]))


def pick(reads, edge, t0, tm):
    ok = [x for x in reads if x["config"] is not None]
    if edge == "start":
        c = [x for x in ok if t0 - BEFORE_S <= x["epoch"] <= t0]
        return c[-1] if c else None
    c = [x for x in ok if tm <= x["epoch"] <= tm + AFTER_S]
    return c[0] if c else None


def check_edge(arm, x):
    """the registered values one complete read must hold on its own: [] or the keys not as registered"""
    if arm == "S":
        return [k for k in KEYS if not eq_num(x.get(k), REG_S[k])]
    bad = [] if eq_num(x.get("minion_mhz"), REG_B_MHZ) else ["minion_mhz"]
    return bad + [k for k in ("tdp_w", "temp_threshold_c") if not is_num(x.get(k))]


def session_gate(raw, arm, t0):
    card = CARDS[arm]
    logs = os.path.join(raw, card, "logs")
    g = {"logs_dir": os.path.relpath(logs, raw), "t0": t0, "reasons": [], "departures": [], "gate": "reduce_e184_v4.py (A3-3 with A4)"}
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
    cfg, frm, tms, sts = {}, {}, {}, {}
    for edge in ("start", "end"):
        p = os.path.join(logs, "config-%s-t%s-%s.json" % (arm, t0, edge)) if t0 else None
        tm = attempt_epoch(p + ".time") if p else None
        tms[edge] = tm
        st, d = load(p)
        sts[edge] = st
        if st == "dry":
            g["reasons"].append("the %s config read for T0 %s is a dry read in a real session's file (never replaced)" % (edge, t0))
            cfg[edge], frm[edge] = None, "a dry read"
        elif st == "complete":
            cfg[edge], frm[edge] = d, "the session's own read"
        elif tm is None:
            g["reasons"].append("no complete %s config read for T0 %s (%s), and no record of its attempt (no .time file): not replaced "
                                "(A3-3, A4)" % (edge, t0, st))
            cfg[edge], frm[edge] = None, None
        else:
            sub = pick(reads, edge, t0, tm)
            if sub is None:
                g["reasons"].append("no complete %s config read for T0 %s (its attempt at %s: %s), and no complete step-7 read in A3-3's "
                                    "window (%s): not replaced" % (edge, t0, iso(tm), st, "the 90 minutes before T0" if edge == "start"
                                                                   else "the 30 minutes after that attempt"))
                cfg[edge], frm[edge] = None, None
            else:
                cfg[edge], frm[edge] = sub["config"], "step 7's read %s (A3-3, A4)" % sub["file"]
                g["departures"].append("the %s config read for T0 %s is missing (its attempt at %s: %s); replaced by step 7's read %s, "
                                       "taken at %s (dated amendments A3, A3-3, and A4)" % (edge, t0, iso(tm), st, sub["file"], sub["utc"]))
    g["config"] = cfg
    g["config_from"] = frm
    g["config_status"] = sts
    g["config_attempt_utc"] = {e: iso(tms[e]) for e in tms}
    if tms.get("end") is not None and frm.get("end") == "the session's own read":
        after = [x for x in reads if x["config"] is not None and tms["end"] <= x["epoch"] <= tms["end"] + AFTER_S]
        g["reported_step7_after_end"] = after[0] if after else None
    for edge in ("start", "end"):          # A4: each edge on its own, whatever the other holds
        x = cfg.get(edge)
        if x is None:
            continue
        bad = check_edge(arm, x)
        if bad:
            want = "TDP 0 W / 65 C / 600 MHz" if arm == "S" else "600 MHz with a TDP and a threshold"
            g["reasons"].append("the %s config read (%s) is not as registered (%s: %s): moved, NOT SCORED whatever step 7 reads (A3-3, "
                                "A4): %s" % (edge, frm[edge], want, ", ".join(bad), json.dumps(x, sort_keys=True)[:200]))
    if arm == "B" and cfg.get("start") is not None and cfg.get("end") is not None:
        a, b = cfg["start"], cfg["end"]
        for k in ("tdp_w", "temp_threshold_c"):
            if not (is_num(a.get(k)) and is_num(b.get(k)) and a.get(k) == b.get(k)):
                g["reasons"].append("%s is not the same number at both ends (%s, %s)" % (k, json.dumps(a.get(k)), json.dumps(b.get(k))))
    g["gate_ok"] = not g["reasons"]
    return g


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("raw")
    ap.add_argument("--arm", choices=["S", "B"], required=True)
    ap.add_argument("--t0", type=int, default=None)
    a = ap.parse_args()
    res = r2.reduce_s(a.raw) if a.arm == "S" else r2.reduce_b(a.raw)
    res["reducer"] = "reduce_e184_v4.py (v2's reduction, unchanged; A3-3's session gate with A4: keys, not truthiness)"
    res["session"] = session_gate(a.raw, a.arm, a.t0)
    print(json.dumps(res, indent=1, sort_keys=True))


if __name__ == "__main__":
    main()
