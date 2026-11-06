#!/usr/bin/env python3
"""E175's data README, dated note 1 (Thu 5 Nov 2026, after the data): the figures and counts the note quotes, read only from committed files.
Post hoc: no rule, line, prediction or verdict is computed anew. It imports no scorer and no predictor (the standard library only) and
writes nothing; its output is posthoc-note1-e175.txt beside it.

    python3 -B -I docs/reports/data/2026-11-05-e175-governed-aifoundry2/posthoc_note1_e175.py \
        > docs/reports/data/2026-11-05-e175-governed-aifoundry2/posthoc-note1-e175.txt

It reads this directory's results.json, logs/queue.out and aifoundry2/s1/runs.jsonl, and every file of the directory as committed in
9f13d7c3 (the note's own three files are left out of the census); M9's aifoundry2 part's frozen m9_a2.json (its burst heat law); and E69's
err_events.txt (the host's boot epoch).
  1. the host's boot, from this directory's two uptime reads, beside E69's boot epoch;
  2. the files: text and binary as the lane's public-text scan told them apart, the .gz files, and what E111's login scrub reads;
  3. E175-A2-H1's chain: each scored tile's predicted rise against the burst heat law applied to that tile's PREDICTED board W;
  4. E175-A2-G, post hoc: as scored, without fp32.e5c10, and without only that tile's dipped pass 3; the four strata;
  5. the bursts that ran while two read-only wait pollers overlapped on aifoundry2 (16:49:23-16:52:06 PST).
SPDX-License-Identifier: Apache-2.0
"""
import datetime as dt
import gzip
import hashlib
import json
import math
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
TOP = os.path.normpath(os.path.join(HERE, "..", "..", "..", ".."))
M9A2 = "docs/reports/data/2026-11-04-q140l-a2-session-terms/m9_a2.json"
E69 = "docs/reports/data/2026-10-27-e69-governor-knob/err_events.txt"
NOTE_FILES = {"README.md.dated-note-1.md", "posthoc_note1_e175.py", "posthoc-note1-e175.txt"}
PST, PDT = dt.timezone(dt.timedelta(hours=-8), "PST"), dt.timezone(dt.timedelta(hours=-7), "PDT")
DIPPED = ("fp32.e5c10_ar_i_t10_adc630", 3)


def sha256(p):
    with open(p, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def rms(v):
    return math.sqrt(sum(x * x for x in v) / len(v))


def mean(v):
    return sum(v) / len(v)


def g_line(e):
    """E175-A2-G's line as registered (p8gov.fixed_G): rms <= 4.0 MHz AND |mean| <= 2.0 MHz; here only as a post hoc comparison"""
    return "within both lines" if rms(e) <= 4.0 and abs(mean(e)) <= 2.0 else "outside a line"


def at(ms, tz):
    return dt.datetime.fromtimestamp(ms / 1000.0, tz)


R = json.load(open(os.path.join(HERE, "results.json")))
SC = R["score"]
T = SC["reported"]["tiles"]
print("E175, dated note 1: post hoc reads of committed files (posthoc_note1_e175.py)")
print(f"results.json sha256 {sha256(os.path.join(HERE, 'results.json'))}")

# 1. the boot ---------------------------------------------------------------------------------------------------------------------------
print("\n1. THE HOST'S BOOT")
UP = re.compile(r'"t_ms": (\d+), "zone": "(\w+)", "sensors_rc": \d+, "uptime": "(\d\d:\d\d:\d\d) up (\d+) days?,\s+(\d+):(\d\d),')
lo_all, hi_all = None, None
for ln in open(os.path.join(HERE, "logs", "queue.out")):
    m = UP.search(ln)
    if not m:
        continue
    t = int(m.group(1)) / 1000.0
    days, hh, mm = int(m.group(4)), int(m.group(5)), int(m.group(6))
    el_min = days * 86400 + hh * 3600 + mm * 60
    lo, hi = t - (el_min + 60), t - el_min          # uptime prints whole minutes: the boot lies in (lo, hi]
    lo_all = lo if lo_all is None else max(lo_all, lo)
    hi_all = hi if hi_all is None else min(hi_all, hi)
    print(f"  queue.out: at {at(t * 1000, PST):%Y-%m-%d %H:%M:%S} {m.group(2)} the box read 'up {days} days, {hh}:{mm:02d}': the boot lies in "
          f"({at(lo * 1000, PDT):%H:%M:%S}, {at(hi * 1000, PDT):%H:%M:%S}] PDT on {at(hi * 1000, PDT):%Y-%m-%d}")
print(f"  both reads: the boot lies in ({at(lo_all * 1000, PDT):%Y-%m-%d %H:%M:%S}, {at(hi_all * 1000, PDT):%H:%M:%S}] PDT "
      f"= ({at(lo_all * 1000, PST):%H:%M:%S}, {at(hi_all * 1000, PST):%H:%M:%S}] PST")
e69 = open(os.path.join(TOP, E69)).read()
m = re.search(r"boot epoch, (\d{4}-\d\d-\d\dT[\d:.]+[+-]\d\d:\d\d)", e69)
b = dt.datetime.fromisoformat(m.group(1))
bt = b.timestamp()
print(f"  {E69}: the host's boot epoch {m.group(1)} = {b.astimezone(PDT):%Y-%m-%d %H:%M:%S} PDT = {b.astimezone(PST):%H:%M:%S} PST "
      f"= {b.astimezone(dt.timezone.utc):%H:%M:%S} UTC; inside both reads: {lo_all < bt <= hi_all}")
as_pst = dt.datetime(2026, 10, 26, 15, 13, 3, tzinfo=PST).timestamp()
print(f"  read as PST, '2026-10-26 15:13:03' would be {at(as_pst * 1000, PDT):%H:%M:%S} PDT: inside both reads: {lo_all < as_pst <= hi_all}")

# 2. the files ---------------------------------------------------------------------------------------------------------------------------
print("\n2. THE FILES (this directory as committed in 9f13d7c3; the note's own three files left out)")
TEXT_SUF = (".json", ".jsonl", ".txt", ".md", ".log", ".out")     # the lane's scan: a NUL in the first 4096 bytes and none of these = binary
SCRUB_SUF = (".json", ".jsonl", ".log", ".out", ".txt")          # E111's scrub_logins_e111.py: these suffixes, every level, <= 200 MB
files = []
for dp, _, fs in os.walk(HERE):
    for f in sorted(fs):
        if dp == HERE and f in NOTE_FILES:
            continue
        files.append(os.path.join(dp, f))
text, binary, gz, scrub, other = [], [], [], [], {}
for p in files:
    raw = gzip.open(p, "rb").read() if p.endswith(".gz") else open(p, "rb").read()
    if p.endswith(".gz"):
        gz.append(p)
    if b"\0" in raw[:4096] and not p.endswith(TEXT_SUF):
        binary.append(p)
    else:
        text.append(p)
    if p.endswith(SCRUB_SUF) and os.path.getsize(p) <= 200 * 1024 * 1024:
        scrub.append(p)
    else:
        k = ".gz" if p.endswith(".gz") else os.path.splitext(p)[1] or "(none)"
        other[k] = other.get(k, 0) + 1
rel = lambda p: os.path.relpath(p, HERE)  # noqa: E731
bdirs = {}
for p in binary:
    bdirs[os.path.dirname(rel(p))] = bdirs.get(os.path.dirname(rel(p)), 0) + 1
print(f"  files {len(files)} (the note's own three files are not counted)")
print(f"  as the lane's public-text scan told them apart: text {len(text)} (of them .gz, read through: {len(gz)}), binary {len(binary)}")
print(f"  the binary files, by folder: {dict(sorted(bdirs.items()))}; all named *.bin: {all(p.endswith('.bin') for p in binary)}")
print(f"  E111's login scrub reads (every level; .json .jsonl .log .out .txt): {len(scrub)} files; it does not read: {dict(sorted(other.items()))}")
nosuf = [(rel(p), os.path.getsize(p)) for p in files if not os.path.splitext(p)[1]]
print(f"  the files with no suffix (name, bytes): {nosuf}")
print(f"  logs/scrub.txt (the collection's scrub): {open(os.path.join(HERE, 'logs', 'scrub.txt')).read().strip()}")

# 3. H1's chain ---------------------------------------------------------------------------------------------------------------------------
print("\n3. E175-A2-H1: THE PREDICTED RISE IS THE BURST HEAT LAW ON THE PREDICTED BOARD W")
H = json.load(open(os.path.join(TOP, M9A2)))["burst_heat"]
k, p0 = H["k_used_c_per_w"], H["P_idle_w"]
print(f"  {M9A2} (sha256 {sha256(os.path.join(TOP, M9A2))[:16]}...) > burst_heat: k_used_c_per_w {k:.5f}, P_idle_w {p0}")
scored = SC["governed"] + SC["pinned"]
for lab in ("M10", "M9"):
    d = [abs(T[n][lab]["burst_die_rise_c"] - round(k * (T[n][lab]["burst_board_w"] - p0), 3)) for n in scored]
    print(f"  {lab}: {len(d)} scored tiles, max |frozen rise - k x (predicted board W - P_idle)| = {max(d):.4f} C")
n0 = "fp16.e5c02_ar_k_t10_5a2fd3"
print(f"  e.g. {n0}: {k:.5f} x ({T[n0]['M10']['burst_board_w']} - {p0}) = {k * (T[n0]['M10']['burst_board_w'] - p0):.3f} C; "
      f"frozen {T[n0]['M10']['burst_die_rise_c']} C; measured {T[n0]['rise_c']} C; the measured board W ({T[n0]['burst_w']}) enters nothing")
e = [T[n]["rise_c"] - T[n]["M10"]["burst_die_rise_c"] for n in scored]
h1 = SC["rules"]["E175-A2-H1"]
print(f"  H1 re-read: rms {rms(e):.4f} C, mean {mean(e):+.4f} C over {len(e)} (results.json > score.rules.E175-A2-H1: {h1.get('rms', h1.get('stat'))}, "
      f"{h1.get('verdict')})")

# 4. G post hoc ---------------------------------------------------------------------------------------------------------------------------
print("\n4. E175-A2-G, POST HOC (never a verdict: G FAILS as registered, and no pass is set aside)")
gov = SC["governed"]


def errs(names, lab):
    return [T[n]["burst_mhz"] - T[n][lab]["burst_mhz"] for n in names]


g = SC["rules"]["E175-A2-G"]
for lab in ("M10", "M9"):
    e = errs(gov, lab)
    who = "M10 carried (the primary)" if lab == "M10" else "M9's part (beside)"
    print(f"  {who}: as scored, n {len(e)}: rms {rms(e):.3f} MHz, mean {mean(e):+.3f} MHz ({g_line(e)})")
print(f"  results.json > score.rules.E175-A2-G: rms {g['rms']}, mean {g['mean']}, {g['verdict']}")
name, dp = DIPPED
c = R["cells"][f"e5-{name}"]
print(f"  {name}: passes {c['passes']}: burst MHz {c['burst_mhz_runs']}, board W {c['burst_w_runs']}, kernel MHz {c['kernel_mhz_runs']}, "
      f"die starts {c['die_start_runs']} C; the cell {c['burst_mhz']} MHz; M10 carried {T[name]['M10']['burst_mhz']} MHz, "
      f"M9's part {T[name]['M9']['burst_mhz']} MHz")
keep = [i for i, p in enumerate(c["passes"]) if p != dp]
m3 = round(mean([c["burst_mhz_runs"][i] for i in keep]), 2)     # the reduction's form: the mean over the passes, to 0.01 MHz
print(f"  without pass {dp}: the tile's mean over passes {[c['passes'][i] for i in keep]} = {m3} MHz; its die starts "
      f"{[c['die_start_runs'][i] for i in keep]} C are the four's value, and the frozen predictor averages its prediction over the tile's die "
      f"starts (predict_m9_a2.py's _cell), so the prediction is the scored one")
for lab in ("M10", "M9"):
    rest = [n for n in gov if n != name]
    e15 = errs(rest, lab)
    e16 = e15 + [m3 - T[name][lab]["burst_mhz"]]
    print(f"  {lab}: without the tile (n {len(e15)}): rms {rms(e15):.3f}, mean {mean(e15):+.3f} MHz ({g_line(e15)}); without only its pass {dp} "
          f"(n {len(e16)}, the tile at {m3 - T[name][lab]['burst_mhz']:+.2f} MHz): rms {rms(e16):.3f}, mean {mean(e16):+.3f} MHz ({g_line(e16)})")
for s in (1, 2, 3, 4):
    names = [n for n in gov if T[n]["stratum"] == s]
    e = errs(names, "M10")
    bs = SC["reported"]["by_set"][f"stratum_{s}"]
    print(f"  stratum S{s} (n {len(e)}): M10 rms {rms(e):.3f}, mean {mean(e):+.3f} MHz (by_set: {bs['M10_mhz_rms']} / {bs['M10_mhz_mean']})")

# 5. the overlap -------------------------------------------------------------------------------------------------------------------------
print("\n5. THE BURSTS DURING THE TWO WAIT POLLERS' OVERLAP (16:49:23-16:52:06 PST)")
w0 = dt.datetime(2026, 11, 5, 16, 49, 23, tzinfo=PST).timestamp() * 1000
w1 = dt.datetime(2026, 11, 5, 16, 52, 6, tzinfo=PST).timestamp() * 1000
inw = []
for ln in open(os.path.join(HERE, "aifoundry2", "s1", "runs.jsonl")):
    r = json.loads(ln)
    if r.get("t_first_ms") is not None and r["t_first_ms"] <= w1 and r["t_last_ms"] >= w0:
        inw.append(r)
for r in inw:
    print(f"  {r['run']}: {at(r['t_first_ms'], PST):%H:%M:%S}-{at(r['t_last_ms'], PST):%H:%M:%S} PST")
print(f"  {len(inw)} of s1's bursts ran inside the window, in part or whole")
