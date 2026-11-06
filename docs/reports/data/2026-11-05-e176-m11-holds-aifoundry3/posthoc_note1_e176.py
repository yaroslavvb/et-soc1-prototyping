#!/usr/bin/env python3
"""E176's data README, dated note 1: R0's start and end values, read again from this directory's committed files. Post hoc.

    python3 -I posthoc_note1_e176.py [this directory]

Reads only aifoundry3/e176/p17620/telemetry.jsonl.gz and marks.jsonl (the measured pass: R0 and the start gate) and
aifoundry3/e176-smoke/p17601/telemetry.jsonl.gz (the smoke's first sample, the idle floor). The 34-sensor mean is E97's
conversion of the raw codes as tools/claims-v3/e176/smoke_gate_e176.py has it (code_to_c), over samples with status 0,
no fault and 34 codes, as that gate filters them. Times are PST (UTC-8 on 5 November 2026). Imports no scorer and
changes nothing: no number, rule or verdict of E176 rests on it.
"""
import gzip
import json
import os
import sys

G_TS, H_TS, CAL5 = 57400, 249400, 4096
PST_S = -8 * 3600


def code_to_c(n):
    return (G_TS + H_TS * n / CAL5 - H_TS / 2) / 1000.0


def mean34(rec):
    pv = rec.get("pvt") or {}
    cs = pv.get("c") or []
    if pv.get("st") == 0 and not pv.get("f") and len(cs) == 34:
        return sum(code_to_c(x) for x in cs) / 34.0
    return None


def clock(ms):
    t = ms / 1000.0 + PST_S
    s = int(t // 1) % 86400
    return "%02d:%02d:%02d.%03d" % (s // 3600, s % 3600 // 60, s % 60, int(round((t % 1) * 1000)) % 1000)


def load(path):
    op = gzip.open if path.endswith(".gz") else open
    out = []
    with op(path, "rt") as f:
        for line in f:
            line = line.strip()
            if line.startswith("{"):
                out.append(json.loads(line))
    return out


def main():
    d = sys.argv[1] if len(sys.argv) > 1 else os.path.dirname(os.path.abspath(__file__))
    p = os.path.join(d, "aifoundry3", "e176", "p17620")
    tel = load(os.path.join(p, "telemetry.jsonl.gz"))
    marks = load(os.path.join(p, "marks.jsonl"))
    smoke = load(os.path.join(d, "aifoundry3", "e176-smoke", "p17601", "telemetry.jsonl.gz"))
    rest = [m for m in marks if m.get("kind") == "rest" and m.get("name") == "R0"][0]
    room = [m for m in marks if m.get("kind") == "room"][0]
    t0, t1 = rest["t_start_ms"], rest["t_end_ms"]
    rows = [(r["t_ms"], mean34(r)) for r in tel if mean34(r) is not None]
    print("1. the measured pass 17620: %d telemetry lines, %d usable" % (len(tel), len(rows)))
    print("   R0's rest mark: start %s, end %s, %.3f s" % (clock(t0), clock(t1), (t1 - t0) / 1000.0))
    first = rows[0]
    before = [r for r in rows if r[0] < t0]
    print("   the pass's first sample: %s, mean34 %.3f C, %.3f s before R0's start; %d samples precede R0"
          % (clock(first[0]), first[1], (t0 - first[0]) / 1000.0, len(before)))
    pk = max(rows, key=lambda r: r[1])
    print("   the pass's highest mean34: %.3f C at %s" % (pk[1], clock(pk[0])))
    inr0 = [r for r in rows if t0 <= r[0] <= t1]
    a = [v for t, v in rows if t0 <= t < t0 + 1000]
    b = [v for t, v in rows if t1 - 1000 < t <= t1]
    print("2. R0 (%d samples)" % len(inr0))
    print("   its first sample: %s (+%.3f s), mean34 %.3f C; its first second's mean %.3f C (n %d)"
          % (clock(inr0[0][0]), (inr0[0][0] - t0) / 1000.0, inr0[0][1], sum(a) / len(a), len(a)))
    t299 = t0 + 299000
    n299 = min(inr0, key=lambda r: abs(r[0] - t299))
    print("   its sample nearest +299 s: %s, mean34 %.3f C" % (clock(n299[0]), n299[1]))
    print("   its last sample: %s (+%.3f s), mean34 %.3f C; its last second's mean %.3f C (n %d)"
          % (clock(inr0[-1][0]), (inr0[-1][0] - t0) / 1000.0, inr0[-1][1], sum(b) / len(b), len(b)))
    w = [v for t, v in rows if t1 - 120000 <= t <= t1]
    g0 = sum(w) / len(w)
    print("3. G0's room, R0's last 120 s: n %d, mean %.4f C; the rest mark's idle_c %.4f C; the room mark's mean34_c %.4f C"
          % (len(w), g0, rest["idle_c"], room["mean34_c"]))
    s = [(t, v) for t, v in rows if t1 - 240000 <= t <= t1]
    mt = sum(t for t, _ in s) / len(s)
    mv = sum(v for _, v in s) / len(s)
    slope = sum((t - mt) * (v - mv) for t, v in s) / sum((t - mt) ** 2 for t, _ in s)
    print("   the slope over R0's last 240 s: n %d, %.3f C per 10 min (least squares)" % (len(s), slope * 600000.0))
    sm = [(r["t_ms"], mean34(r), r.get("board_w")) for r in smoke if mean34(r) is not None]
    print("4. the smoke 17601's first sample (the idle floor): %s, mean34 %.3f C, board %.2f W" % (clock(sm[0][0]), sm[0][1], sm[0][2]))
    print("   G0's room above that floor: %.3f C" % (g0 - sm[0][1]))


if __name__ == "__main__":
    print("E176, dated note 1: post hoc reads of committed files (posthoc_note1_e176.py)")
    main()
