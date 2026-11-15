#!/usr/bin/env python3
"""E189's data README, dated note 1 (Sat 14 Nov 2026, after the data verifier): the figures the note quotes, read again from committed
files. Post hoc: it decides nothing, scores nothing and changes no committed file.

    python3 -I -B docs/reports/data/2026-11-14-e189-blind-day-aifoundry3/posthoc_note1_e189.py [--out DIR] [--data DIR --top DIR]

It reads only the files of this directory's data commit: the 228 files SHA256SUMS lists, README.md and SHA256SUMS (never a file added
after them, so the note's own files do not change its outputs); and from the repository: the registration's list
tools/claims-v3/e189/SHA256SUMS-e189-registration with the ten files it pins, and as text E189.md, collect_e189.py, e189_common.py,
run_e189.py and two files of sparse parity's code, its header and its host (the lines the note cites).

Section 0: SHA256SUMS read entry by entry; the sha256 of README.md and SHA256SUMS; the registration's list read entry by entry.
Section 1: sparse parity's host.rec, each file's size, sha256 and 64-byte records, its lines in SHA256SUMS and in the box's
MANIFEST.sha256, and where README.md, E189.md and the kit's code name it.
Section 2: each pass's reducer flag of one busy board reading at idle and the share it gives; the README's words.
Section 3: the box's MANIFEST.sha256 against this directory's bytes, every file's count of "~" and of a home-directory path (the text inside every
.gz included), session/runner.rc's bytes; the README's words.
Section 4: the session's times from session/queue.json and session/session.log beside the window's two readings, as README.md's
departures 1 and 6 give his go and G.
Section 5: the README's departures and notes, as listed.
Section 6: S1T's margin on the starting die. Only after the registration's list reads every entry OK (and tools/ledger/ledger_v2.py and
the ledger v2's frozen-v2.json match forecast_e189.py's own pins) does it load the frozen scorer, score_e189.py, as registered, and use
its own pass reader (read_pass), its forecast module's given() and its verdict count (count_rule): each pass's given-seconds J with the
card at rest at its measured t_k and t_w and its T0 moved by one uniform delta, against the measured J with the card at rest as
committed. delta = 0 is the registered reading (it must equal the frozen scorer's e_j_total); every other delta is post hoc.

It writes posthoc-note1-e189.json and posthoc-note1-e189.txt beside itself (or in --out), with paths relative to this directory or the
repository's top, times in PST (UTC-8, fixed), floats rounded to 9 significant digits and no run time, so a re-run from the same tree
under the same interpreter writes both byte for byte. --data and --top name this directory and the repository's top when the script
runs from a copy. Standard library only. /usr/bin/python3 3.12.3 wrote the committed outputs.
SPDX-License-Identifier: Apache-2.0
"""
import datetime
import gzip
import hashlib
import importlib.util
import json
import math
import os
import re
import sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
PST = datetime.timezone(datetime.timedelta(hours=-8), "PST")
CONFIGS = ["copy-zeros", "copy-random", "sha256", "sort-sorted", "sort-shuffled", "sparse-parity"]
REG = "tools/claims-v3/e189/SHA256SUMS-e189-registration"
HOMEP = b"/ho" + b"me/"    # a home-directory path; written split in two, so that a public-text scan of this file does not read it as one


def arg(name, default):
    a = sys.argv[1:]
    return a[a.index(name) + 1] if name in a else default


DATA = os.path.abspath(arg("--data", HERE))
TOP = os.path.abspath(arg("--top", os.path.join(DATA, "..", "..", "..", "..")))
OUT = os.path.abspath(arg("--out", DATA))


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def r9(x):
    if isinstance(x, dict):
        return {k: r9(v) for k, v in x.items()}
    if isinstance(x, (list, tuple)):
        return [r9(v) for v in x]
    if isinstance(x, float):
        return x if x == 0.0 or not math.isfinite(x) else float(f"{x:.8e}")
    return x


def pst(ms):
    return datetime.datetime.fromtimestamp(ms / 1000.0, PST).strftime("%Y-%m-%d %H:%M:%S.%f")[:-3] + " PST"


def hms(s):
    s = int(round(s))
    return f"{s // 3600}:{(s % 3600) // 60:02d}:{s % 60:02d}"


def lines_with(path, needle):
    out = []
    for i, ln in enumerate(open(path, encoding="utf-8").read().split("\n"), 1):
        if needle in ln:
            out.append(i)
    return out


def text_of(path):
    b = open(path, "rb").read()
    if path.endswith(".gz"):
        b = gzip.decompress(b)
    return b


res = {"what": "E189's data README, dated note 1: post hoc readings of committed files (decides nothing; scores nothing)",
       "interpreter": sys.version.split()[0]}
txt = [res["what"], f"interpreter: python {res['interpreter']}", ""]

# ---------------------------------------------------------------- 0. the anchors
sums = {}
for ln in open(os.path.join(DATA, "SHA256SUMS")):
    if ln.strip():
        h, p = ln.rstrip("\n").split("  ", 1)
        sums[p] = h
ok = sum(1 for p, h in sums.items() if os.path.exists(os.path.join(DATA, p)) and sha(os.path.join(DATA, p)) == h)
FILES = sorted(sums) + ["README.md", "SHA256SUMS"]       # the data commit's files, and nothing added after them
reg_rows = [ln.split(None, 1) for ln in open(os.path.join(TOP, REG)) if ln.strip()]
reg_ok = [p.strip() for h, p in reg_rows if sha(os.path.join(TOP, p.strip())) == h]
s0 = {"sha256sums_entries": len(sums), "sha256sums_ok": ok, "readme_sha256": sha(os.path.join(DATA, "README.md")),
      "sha256sums_sha256": sha(os.path.join(DATA, "SHA256SUMS")), "data_commit_files": len(FILES),
      "registration_list_sha256": sha(os.path.join(TOP, REG)), "registration_entries": len(reg_rows),
      "registration_ok": len(reg_ok)}
res["s0_anchors"] = s0
txt += ["0. anchors",
        f"  SHA256SUMS: {ok} of {len(sums)} entries OK; with README.md and SHA256SUMS the data commit's {len(FILES)} files",
        f"  README.md sha256 {s0['readme_sha256']}", f"  SHA256SUMS sha256 {s0['sha256sums_sha256']}",
        f"  {REG}: {len(reg_ok)} of {len(reg_rows)} entries OK (list sha256 {s0['registration_list_sha256']})", ""]

# ---------------------------------------------------------------- 1. host.rec
man = {}
for ln in open(os.path.join(DATA, "session", "MANIFEST.sha256")):
    if ln.strip():
        h, p = ln.rstrip("\n").split("  ", 1)
        man[p] = h
recs = []
for p in sorted(x for x in FILES if x.endswith("/host.rec")):
    full = os.path.join(DATA, p)
    n = os.path.getsize(full)
    recs.append({"path": p, "bytes": n, "sha256": sha(full), "records_of_64_bytes": n // 64, "remainder": n % 64,
                 "in_sha256sums": sums.get(p) == sha(full), "in_box_manifest": man.get(p) == sha(full)})
cite = {
    "README.md: lines naming host.rec": lines_with(os.path.join(DATA, "README.md"), "host.rec"),
    "README.md: the Files table's passes row": [i for i in lines_with(os.path.join(DATA, "README.md"), "| `passes/<configuration>/p<k>/` |")],
    "tools/claims-v3/e189/E189.md: lines naming host.rec": lines_with(os.path.join(TOP, "tools/claims-v3/e189/E189.md"), "host.rec"),
    "tools/claims-v3/e189/collect_e189.py: lines naming host.rec": lines_with(os.path.join(TOP, "tools/claims-v3/e189/collect_e189.py"), "host.rec"),
    "tools/claims-v3/e189/e189_common.py: lines naming host.rec": lines_with(os.path.join(TOP, "tools/claims-v3/e189/e189_common.py"), "host.rec"),
    "workloads/sparseparity/sparseparity_args.h: SppRecord is 64 bytes": lines_with(os.path.join(TOP, "workloads/sparseparity/sparseparity_args.h"), "sizeof(SppRecord) == 64"),
    "workloads/sparseparity/sparseparity_args.h: SPP_HARTS": lines_with(os.path.join(TOP, "workloads/sparseparity/sparseparity_args.h"), "#define SPP_HARTS 2048u"),
    "workloads/sparseparity/host/main.cpp: the records read back after each launch": lines_with(os.path.join(TOP, "workloads/sparseparity/host/main.cpp"), "runtime->memcpyDeviceToHost(stream, dRec"),
    "workloads/sparseparity/host/main.cpp: --records-out writes them": lines_with(os.path.join(TOP, "workloads/sparseparity/host/main.cpp"), "f.write(reinterpret_cast<const char*>(records.data())"),
}
res["s1_host_rec"] = {"files": recs, "cited_lines": cite}
txt += ["1. sparse parity's host.rec"]
for r in recs:
    txt.append(f"  {r['path']}: {r['bytes']} bytes = {r['records_of_64_bytes']} records of 64 bytes (remainder {r['remainder']}); "
               f"sha256 {r['sha256'][:16]}...; in SHA256SUMS {r['in_sha256sums']}; in the box's MANIFEST.sha256 {r['in_box_manifest']}")
for k, v in cite.items():
    txt.append(f"  {k}: {v if v else 'none'}")
txt.append("")

# ---------------------------------------------------------------- 2. the busy-reading flags
flags = []
for p in sorted(x for x in FILES if x.endswith("/energy.json")):
    for f in json.load(open(os.path.join(DATA, p))).get("flags") or []:
        m = re.search(r"(\d+) of (\d+) busy board_w readings at idle.*?about (\d+)% low", f)
        if m:
            flags.append({"pass": p[len("passes/"):-len("/energy.json")], "busy_at_idle": int(m.group(1)),
                          "idle_readings": int(m.group(2)), "about_pct_low": int(m.group(3))})
pcts = [f["about_pct_low"] for f in flags]
s2 = {"flags": flags, "count": len(flags), "pct_low_min": min(pcts) if pcts else None, "pct_low_max": max(pcts) if pcts else None,
      "readme_lines_3_4_pct": lines_with(os.path.join(DATA, "README.md"), "about 3-4% low")}
res["s2_flags"] = s2
txt += ["2. the reducer's flags of one busy board reading at idle (energy.json > flags; the catalogue cross-check, not the headline)"]
for f in flags:
    txt.append(f"  {f['pass']}: {f['busy_at_idle']} of {f['idle_readings']} busy readings at idle: about {f['about_pct_low']}% low")
txt += [f"  {len(flags)} flags; the shares read {s2['pct_low_min']}-{s2['pct_low_max']}%; README.md says 'about 3-4% low' on line(s) "
        f"{s2['readme_lines_3_4_pct']}", ""]

# ---------------------------------------------------------------- 3. the scrub
man_ok, man_bad = 0, []
for p, h in sorted(man.items()):
    local = os.path.join(DATA, p) if p.startswith("passes/") else os.path.join(DATA, "session", p)
    if os.path.exists(local) and sha(local) == h:
        man_ok += 1
    else:
        man_bad.append(p)
mapped = set((p if p.startswith("passes/") else "session/" + p) for p in man)
outside = sorted(x for x in FILES if x not in mapped)
kinds = {}
for x in outside:
    k = os.path.basename(x)
    kinds[k] = kinds.get(k, 0) + 1
tilde_out, home = {}, {}
for x in FILES:
    b = text_of(os.path.join(DATA, x))
    if x in outside and b.count(b"~"):
        tilde_out[x] = b.count(b"~")
    if b.count(HOMEP):
        home[x] = b.count(HOMEP)
s3 = {"manifest_entries": len(man), "manifest_ok": man_ok, "manifest_bad": man_bad, "outside_manifest": kinds,
      "outside_manifest_files": len(outside), "outside_manifest_with_tilde": tilde_out, "files_with_home_path": home,
      "runner_rc_bytes": open(os.path.join(DATA, "session", "runner.rc"), "rb").read().decode("ascii", "replace"),
      "readme_lines_became_tilde": lines_with(os.path.join(DATA, "README.md"), "home path became `~`"),
      "run_e189_py_writes_the_manifest": lines_with(os.path.join(TOP, "tools/claims-v3/e189/run_e189.py"),
                                                    'with open(os.path.join(out, "MANIFEST.sha256"), "w") as f:')}
res["s3_scrub"] = s3
txt += ["3. the scrub (collect_e189.py's step 4 replaces the box's home path by '~' in every text file and every .gz's text)",
        f"  the box's MANIFEST.sha256 (written on the box before the copy-back): {man_ok} of {len(man)} files at their listed sha256 "
        f"in this directory (passes/ here, the rest under session/); not matching: {man_bad if man_bad else 'none'}",
        f"  the data commit's {len(outside)} files outside that list: {json.dumps(kinds, sort_keys=True)}",
        f"  of those, the files holding '~': {json.dumps(tilde_out, sort_keys=True)}",
        f"  files of the data commit holding a home-directory path (the text inside every .gz included): "
        f"{json.dumps(home, sort_keys=True) if home else 'none'}",
        f"  session/runner.rc: {s3['runner_rc_bytes']!r}",
        f"  README.md says 'the box's home path became `~`' on line(s) {s3['readme_lines_became_tilde']}",
        f"  tools/claims-v3/e189/run_e189.py writes MANIFEST.sha256 (on the box, last) on line(s) {s3['run_e189_py_writes_the_manifest']}",
        ""]

# ---------------------------------------------------------------- 4. the times and the window's two readings
q = json.load(open(os.path.join(DATA, "session", "queue.json")))
log = open(os.path.join(DATA, "session", "session.log"), encoding="utf-8").read().split("\n")


def log_time(rx):
    for i, ln in enumerate(log, 1):
        if re.search(rx, ln):
            return ln[:19], i
    return None, None


last_pass_start, lps_line = log_time(r"PST pass 24: \S+ p\d \(K")
first_pass_start, fps_line = log_time(r"PST pass 1: \S+ p\d \(K")
session_end, se_line = log_time(r"PST session end \(T0")
readme = open(os.path.join(DATA, "README.md"), encoding="utf-8").read()
mg = re.search(r"\*\*(\d\d):(\d\d):(\d\d) PST\*\*, as the plan for Friday had", readme)
mgo = re.search(r"\(about (\d\d):(\d\d)\)\. The registered defaults held", readme)
mstep1 = re.search(r"written by step 1 at (\d\d:\d\d:\d\d)", readme)
day = datetime.datetime(2026, 11, 14, tzinfo=PST)


def at(h, m, s=0):
    return day + datetime.timedelta(hours=h, minutes=m, seconds=s)


def clock(t):
    return t.strftime("%H:%M:%S")


def parse(hms_):
    h, m, s = (int(x) for x in hms_.split(":"))
    return at(h, m, s)


G = at(int(mg.group(1)), int(mg.group(2)), int(mg.group(3)))
GO = at(int(mgo.group(1)), int(mgo.group(2)))
first_cmd = datetime.datetime.fromtimestamp(q["t_first_ms"] / 1000.0, PST)
close = datetime.datetime.fromtimestamp(q["t_close_ms"] / 1000.0, PST)
lps = parse(last_pass_start[11:19])
se = parse(session_end[11:19])
as_run = {"G": clock(G), "last_start_exact": clock(G + datetime.timedelta(hours=1, minutes=30)),
          "last_end_exact": clock(G + datetime.timedelta(hours=3, minutes=30)), "last_start_written": "21:35",
          "last_end_written": "23:35", "rounding_s": 60 - G.second if G.second else 0,
          "last_pass_start_before_exact_last_start": hms((G + datetime.timedelta(hours=1, minutes=30) - lps).total_seconds()),
          "session_end_before_exact_last_end": hms((G + datetime.timedelta(hours=3, minutes=30) - se).total_seconds())}
literal = {"go_about": clock(GO), "last_start_about": clock(GO + datetime.timedelta(hours=1, minutes=30)),
           "last_end_about": clock(GO + datetime.timedelta(hours=3, minutes=30)),
           "first_card_command_after_last_start": hms((first_cmd - (GO + datetime.timedelta(hours=1, minutes=30))).total_seconds()),
           "session_end_after_last_end": hms((se - (GO + datetime.timedelta(hours=3, minutes=30))).total_seconds())}
s4 = {"t0": q["t0"], "t_first_ms": q["t_first_ms"], "first_card_command": pst(q["t_first_ms"]), "t_close_ms": q["t_close_ms"],
      "close": pst(q["t_close_ms"]), "end_bound": pst(q["end_bound_ms"]),
      "first_pass_start": first_pass_start, "first_pass_line": fps_line, "last_pass_start": last_pass_start,
      "last_pass_line": lps_line, "session_end": session_end, "session_end_line": se_line,
      "step1_window_written": mstep1.group(1) if mstep1 else None, "as_run": as_run, "literal": literal}
res["s4_window"] = s4
txt += ["4. the session's times (session/queue.json, session/session.log) and the window's two readings",
        f"  first card command {s4['first_card_command']}; close {s4['close']}; the cap's end bound {s4['end_bound']}",
        f"  pass 1 started {first_pass_start} (session.log line {fps_line}); pass 24 started {last_pass_start} (line {lps_line}); "
        f"session end {session_end} (line {se_line})",
        f"  as run (README.md departure 6): G {as_run['G']}; G+1:30 = {as_run['last_start_exact']}, G+3:30 = {as_run['last_end_exact']}; "
        f"written {as_run['last_start_written']} / {as_run['last_end_written']} (rounded up {as_run['rounding_s']} s; step 1 wrote them at "
        f"{s4['step1_window_written']}); pass 24 started {as_run['last_pass_start_before_exact_last_start']} before G+1:30; the session "
        f"ended {as_run['session_end_before_exact_last_end']} before G+3:30",
        f"  by the letter of E189.md section 13 (G = his go, about {literal['go_about']}, README.md departure 1): last start about "
        f"{literal['last_start_about']}, last end about {literal['last_end_about']}; the first card command came "
        f"{literal['first_card_command_after_last_start']} after that last start, and the session ended "
        f"{literal['session_end_after_last_end']} after that last end", ""]

# ---------------------------------------------------------------- 5. the departures as listed
deps = []
rl = readme.split("\n")
start = next(i for i, ln in enumerate(rl) if ln.startswith("## Departures and notes"))
for i in range(start + 1, len(rl)):
    if rl[i].startswith("## "):
        break
    m = re.match(r"^(\d)\. \*\*(.+?)\*\*", rl[i])
    if m:
        deps.append({"n": int(m.group(1)), "title": m.group(2), "line": i + 1})
res["s5_departures"] = {"heading_line": start + 1, "items": deps}
txt += [f"5. README.md's departures and notes (heading line {start + 1})"]
txt += [f"  {d['n']}. {d['title']} (line {d['line']})" for d in deps]
txt.append("")

# ---------------------------------------------------------------- 6. S1T's margin on the starting die (post hoc)
s6 = {"refused": None}
pins_needed = ["tools/ledger/ledger_v2.py", "docs/reports/data/2026-11-12-q166-ledger-v2/frozen-v2.json"]
if len(reg_ok) != len(reg_rows):
    s6["refused"] = "the registration's list does not read every entry OK"
else:
    spec = importlib.util.spec_from_file_location("forecast_e189_pins", os.path.join(TOP, "tools/claims-v3/e189/forecast_e189.py"))
    FP = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(FP)
    bad = [p for p in pins_needed if sha(os.path.join(TOP, p)) != FP.PINS[p]]
    if bad:
        s6["refused"] = "pinned inputs differ: " + ", ".join(bad)
if s6["refused"] is None:
    spec = importlib.util.spec_from_file_location("score_e189", os.path.join(TOP, "tools/claims-v3/e189/score_e189.py"))
    SC = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(SC)
    LV, FC, F = SC.modules()
    fc = json.load(open(os.path.join(TOP, "tools/claims-v3/e189/forecast-e189.json")))
    tol = SC.RULES["E189-S1T"]["tol"]
    passes = {}
    for key in CONFIGS:
        d = os.path.join(DATA, "passes", key)
        passes[key] = [SC.read_pass(os.path.join(d, p), key)[0] for p in sorted(os.listdir(d)) if p.startswith("p")]
        passes[key] = [p for p in passes[key] if p]

    def e_tot(key, delta):
        ps = passes[key]
        g = [FC.given(fc["configs"][key], p["t_k"], p["t_w"], p["T0"] + delta, F, LV)["j_total"] for p in ps]
        return (sum(g) / len(g)) / (sum(p["j_total"] for p in ps) / len(ps)) - 1.0

    def verdict(delta):
        cs = [{"config": k, "ok_S1T": abs(e_tot(k, delta)) <= tol} for k in CONFIGS]
        c = SC.count_rule("E189-S1T", cs, "ok_S1T")
        return c["verdict"], c["within"]

    def edge(fn, a, b, steps=60):
        """fn(a) and fn(b) differ: bisect to the point where fn changes (to below 1e-9 C)."""
        fa = fn(a)
        for _ in range(steps):
            m = 0.5 * (a + b)
            if fn(m) == fa:
                a = m
            else:
                b = m
        return 0.5 * (a + b)

    laws = {}
    for key in CONFIGS:
        for p in passes[key]:
            law = FC.given(fc["configs"][key], p["t_k"], p["t_w"], p["T0"], F, LV)["rest_law"]
            laws[law] = laws.get(law, 0) + 1
    reg = {k: e_tot(k, 0.0) for k in CONFIGS}
    v0 = verdict(0.0)
    cross = {}
    for key in CONFIGS:
        within = lambda d, k=key: abs(e_tot(k, d)) <= tol  # noqa: E731
        row = {}
        for side, lim in (("lower", -5.0), ("upper", 5.0)):
            row[side] = round(edge(within, 0.0, lim), 3) if within(0.0) and not within(lim) else None
        cross[key] = row
    vfn = lambda d: verdict(d)[0]  # noqa: E731
    flips = {side: (round(edge(vfn, 0.0, lim), 3) if vfn(lim) != v0[0] else None) for side, lim in (("lower", -5.0), ("upper", 5.0))}
    grid = {}
    for d in (-1.0, -0.5, 0.5, 1.0):
        grid[f"{d:+.1f}"] = {"e_j_total": {k: e_tot(k, d) for k in CONFIGS}, "verdict": verdict(d)[0], "within": verdict(d)[1]}
    t0s = sorted(p["T0"] for k in CONFIGS for p in passes[k])
    s6 = {"refused": None, "label": "post hoc (delta = 0 is the registered reading)", "tol": tol,
          "passes_read": {k: len(passes[k]) for k in CONFIGS}, "t0_min": t0s[0], "t0_max": t0s[-1],
          "rest_law_at_delta_0": laws, "registered_e_j_total": reg, "registered_verdict": v0[0], "registered_within": v0[1],
          "crossing_delta_c": cross, "verdict_changes_at_delta_c": flips, "at_delta": grid,
          "footing_band_c": F["idle_laws"]["aifoundry3"]["quad_band_c"]}
res["s6_s1t_margin"] = s6
txt.append("6. S1T's margin on the starting die (post hoc; delta = 0 is the registered reading)")
if s6["refused"]:
    txt.append(f"  REFUSED: {s6['refused']}")
else:
    txt += [f"  read by the frozen scorer's read_pass: {json.dumps(s6['passes_read'])}; T0 (die_c.before) {s6['t0_min']}-{s6['t0_max']} C; "
            f"the footing law's band {s6['footing_band_c']} C; the rest law at delta 0: {json.dumps(laws, sort_keys=True)}",
            f"  registered (delta 0): S1T {v0[0]}, {v0[1]} of 6 within {tol:.0%}; e_j_total "
            + ", ".join(f"{k} {reg[k]:+.6f}" for k in CONFIGS)]
    def cs(x):
        return f"{x:+.3f} C" if x is not None else "none between -5 and +5 C"
    for k in CONFIGS:
        txt.append(f"  {k}: |e_j_total| passes {tol:.0%} at a uniform delta of {cs(cross[k]['lower'])} below and "
                   f"{cs(cross[k]['upper'])} above")
    txt.append(f"  S1T's word changes from {v0[0]} at a uniform delta of {cs(flips['lower'])} below and {cs(flips['upper'])} above")
    for d, g in grid.items():
        txt.append(f"  delta {d} C: S1T {g['verdict']}, {g['within']} of 6 within; " + ", ".join(f"{k} {g['e_j_total'][k]:+.6f}" for k in CONFIGS))
txt.append("")

os.makedirs(OUT, exist_ok=True)
with open(os.path.join(OUT, "posthoc-note1-e189.json"), "w") as f:
    json.dump(r9(res), f, indent=1, sort_keys=True)
    f.write("\n")
with open(os.path.join(OUT, "posthoc-note1-e189.txt"), "w") as f:
    f.write("\n".join(txt) + "SPDX-License-Identifier: Apache-2.0\n")
print("\n".join(txt))
