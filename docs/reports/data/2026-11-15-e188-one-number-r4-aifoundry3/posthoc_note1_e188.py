#!/usr/bin/env python3
"""E188's data README, dated note 1 (Sun 15 Nov 2026, after the data verifier): the figures the note quotes, read again from committed
files. Post hoc readings only: it decides nothing, scores nothing and changes no committed file.

    python3 -I -B docs/reports/data/2026-11-15-e188-one-number-r4-aifoundry3/posthoc_note1_e188.py [--out DIR] [--data DIR --top DIR]

It reads only committed files: the files of this directory's data commit (the 350 that SHA256SUMS lists, README.md and SHA256SUMS;
never a file added after them, so the note's own files do not change its outputs), and as text, from the repository, the lines the
note cites in tools/claims-v3/kinds/run_e78.py and reduce_e78.py, tools/claims-v3/e188/score_e188.py, pairing_e188.py and
forecast_e188.py, tools/claims-v3/ccheck/ccheck.py and patch_host_ccheck.py, and tools/claims-v3/e186/KIT.md.dated-note-2.md.

Section 0: SHA256SUMS read entry by entry; the sha256 of README.md, SHA256SUMS and each cited file.
Section 1: the README lines the note cites.
Section 2: the 24 config reads (each block's config_start.json and config_end.json, and the session's two): each field's values.
Section 3: the run marks whose recorded quiet is the runner's starting value, not a measured gap; each train's closing anchor runner
  (a1): the train's last process end, the runner's start as run_e78.py's starting value implies it, a1's first run and first launch,
  the measured gaps, and the two gates of E78's reduction that read prev_end_ms, under the recorded and the measured previous end.
Section 4: E188-C's coverage: the check of C's verdicts split by what names each launch (the kit scorer's set, the smoke, the
  burn-ins, none), and each group's verdicts.
Section 5: the C-logging host's hash: every tiles record of the ten C logs hashed under the host's offset basis and the standard one;
  every C record's hash against the tiles records of its own log.
Section 6: the window under two readings of G (his words; the booking), with each gate the go lines name.
Section 7: margins at the session's s (post hoc, from scored-e188.json), and the range of s over which every word and sub-word that
  takes s keeps its value, by E188.md 4.2's scaling (forecast_e188.lines_at: M10's line takes s and the train's rate ratio; M12's line
  is that plus its increment; M12's se fixed). Only s moves; every train's rate ratio stays as measured. At the session's s the
  arithmetic must give the kit's words (checked).

It writes posthoc-note1-e188.json and posthoc-note1-e188.txt beside itself (or in --out), with paths relative to this directory or the
repository's top, times in PST (UTC-8), floats rounded to 9 significant digits and no run time, so a re-run from the same tree under the
same interpreter writes both byte for byte. --data and --top name this directory and the repository's top when the script runs from a
copy. Standard library only. /usr/bin/python3 3.12.3 wrote the committed outputs.
SPDX-License-Identifier: Apache-2.0
"""
import datetime as dt
import glob
import gzip
import hashlib
import json
import math
import os
import re
import sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
TRAINS = {18810: "B05", 18811: "PAIR", 18812: "B19", 18813: "AALL", 18814: "B10", 18815: "B22", 18816: "B04"}
ORDER = ["B05", "PAIR", "B19", "AALL", "B10", "B22", "B04"]
ONE_BIT_B = ["B04", "B05", "B10", "B19", "B22"]
BASIS_HOST = 1469598103934665603      # the C-logging host's offset basis (patch_host_ccheck.py, ccheck.py, pairing_e188.py)
BASIS_STD = 14695981039346656037      # FNV-1a 64's standard offset basis
PRIME = 1099511628211
PST = dt.timezone(dt.timedelta(hours=-8))
CITED = ["tools/claims-v3/kinds/run_e78.py", "tools/claims-v3/kinds/reduce_e78.py", "tools/claims-v3/e188/score_e188.py",
         "tools/claims-v3/e188/pairing_e188.py", "tools/claims-v3/e188/forecast_e188.py", "tools/claims-v3/ccheck/ccheck.py",
         "tools/claims-v3/ccheck/patch_host_ccheck.py", "tools/claims-v3/e186/KIT.md.dated-note-2.md"]


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


def pst(ms, frac=True):
    t = dt.datetime.fromtimestamp(ms / 1000.0, tz=PST)
    return t.strftime("%H:%M:%S.%f")[:-3] if frac else t.strftime("%H:%M:%S")


def jl(path):
    op = gzip.open if path.endswith(".gz") else open
    out = []
    with op(path, "rt") as f:
        for line in f:
            line = line.strip()
            if line.startswith("{"):
                out.append(json.loads(line))
    return out


def lines_with(path, needle):
    return [i for i, ln in enumerate(open(path, encoding="utf-8"), 1) if needle in ln]


def D(*p):
    return os.path.join(DATA, *p)


res, txt = {}, ["E188's data README, dated note 1: post hoc readings from committed files (posthoc_note1_e188.py)", ""]

# ---------------------------------------------------------------- 0. the inputs
ok = n = 0
listed = []
for ln in open(D("SHA256SUMS"), encoding="utf-8"):
    if "  " not in ln:
        continue
    h, p = ln.rstrip("\n").split("  ", 1)
    n += 1
    listed.append(p)
    ok += os.path.isfile(D(p)) and sha(D(p)) == h
cited = {c: sha(os.path.join(TOP, c)) for c in CITED}
res["s0_inputs"] = {"sha256sums_ok": ok, "sha256sums_entries": n, "readme_sha256": sha(D("README.md")),
                    "sha256sums_sha256": sha(D("SHA256SUMS")), "cited_sha256": cited}
txt += ["0. Inputs",
        f"  SHA256SUMS: {ok} of {n} entries OK; README.md {res['s0_inputs']['readme_sha256']}; SHA256SUMS {res['s0_inputs']['sha256sums_sha256']}"]
txt += [f"  {c}: {h}" for c, h in cited.items()]
txt.append("")

# ---------------------------------------------------------------- 1. the README lines cited
RM = D("README.md")
s1 = {"go_words_15_05_27": lines_with(RM, "15:05:27 PST"), "booking_15_10_41": lines_with(RM, "15:10:41 PST"),
      "launched_15_15_19": lines_with(RM, "The session launched at 15:15:19"),
      "step11_16_40_45": lines_with(RM, "step 11 started at 16:40:45"),
      "c_8744": lines_with(RM, "8,744 of 8,744 launches PASS"),
      "config_same_at_close": lines_with(RM, "the same at the close"),
      "anchors_at_band": lines_with(RM, "launched at the band (58 C after 59 C)"),
      "never_sent_fw_query": lines_with(RM, "the firmware-revisions query"),
      "scan_pubscan_message": lines_with(RM, "0 hits in the commit message"),
      "scan_tiers_message": lines_with(RM, "in the commit message, none")}
res["s1_readme_lines"] = s1
txt += ["1. README.md's lines cited (line numbers in its committed bytes)"]
txt += [f"  {k}: {v}" for k, v in s1.items()]
txt.append("")

# ---------------------------------------------------------------- 2. the config reads
cfg_files = []
for blk in sorted(glob.glob(D("aifoundry3", "*", "p*"))):
    for f in ("config_start.json", "config_end.json"):
        cfg_files.append(os.path.relpath(os.path.join(blk, f), DATA))
cfg_files += ["logs/config-session-start.json", "logs/config-session-end.json"]
fields = {}
reads = {}
for f in cfg_files:
    c = json.load(open(D(f)))
    reads[f] = c
    for k, v in c.items():
        fields.setdefault(k, {}).setdefault(str(v), []).append(f)
summary = {k: {v: len(fs) for v, fs in sorted(vals.items())} for k, vals in sorted(fields.items())}
odd = {k: {v: fs for v, fs in vals.items() if len(fs) < len(cfg_files)} for k, vals in fields.items() if len(vals) > 1}
blk_close = {}
for f, c in reads.items():
    if f.endswith("config_end.json") and f.startswith("aifoundry3/"):
        b = json.load(open(D(os.path.dirname(f), "block.json")))
        blk_close[f] = {"block_t1_pst": pst(b["t1_ms"], False), "minion_mv": c.get("minion_mv")}
s2 = {"reads": len(cfg_files), "fields": summary, "fields_with_more_than_one_value": odd,
      "session_start": reads["logs/config-session-start.json"], "session_end": reads["logs/config-session-end.json"],
      "session_times": [open(D("logs/config-session-start.json.time")).read().strip(),
                        open(D("logs/config-session-end.json.time")).read().strip()],
      "block_closing_reads": blk_close}
res["s2_config_reads"] = s2
txt += [f"2. The config reads: {len(cfg_files)} files (each block's config_start.json and config_end.json, and the session's two)"]
txt += [f"  {k}: {json.dumps(v, sort_keys=True)}" for k, v in summary.items()]
txt += [f"  a field with more than one value: {k} {json.dumps(v, sort_keys=True)}" for k, v in sorted(odd.items())]
txt += [f"  the session's reads at {s2['session_times'][0]} and {s2['session_times'][1]}: minion_mv "
        f"{s2['session_start']['minion_mv']} and {s2['session_end']['minion_mv']}"]
txt += [f"  {f}: {v['minion_mv']} mV (block.json closes at {v['block_t1_pst']} PST)" for f, v in sorted(blk_close.items())]
txt.append("")

# ---------------------------------------------------------------- 3. the recorded quiet, and each train's closing anchor runner
RUNNER = os.path.join(TOP, "tools/claims-v3/kinds/run_e78.py")
REDUCER = os.path.join(TOP, "tools/claims-v3/kinds/reduce_e78.py")
code3 = {"run_e78_starting_value": lines_with(RUNNER, "last_end = [time.time() - 3600.0]"),
         "run_e78_quiet": lines_with(RUNNER, "quiet = time.time() - last_end[0]"),
         "reduce_e78_prev_end": lines_with(REDUCER, 'pe = m.get("prev_end_ms", prev_end)'),
         "reduce_e78_idle_after_prev": lines_with(REDUCER, '"idle_after_prev_ms": None if pe is None else (t0 - 1200) - pe'),
         "reduce_e78_quiet_gate": lines_with(REDUCER, 'r["quiet_s"] < q - 0.05'),
         "reduce_e78_idle_gate": lines_with(REDUCER, 'r["idle_after_prev_ms"] >= GATES["idle_after_prev_ms"]'),
         "reduce_e78_gate_800": lines_with(REDUCER, '"idle_after_prev_ms": 800')}
big = []
for mf in sorted(glob.glob(D("aifoundry3", "*", "p*", "marks.jsonl")) + glob.glob(D("aifoundry3", "*", "p*", "a?", "marks.jsonl"))):
    for m in jl(mf):
        if m.get("kind") == "run" and (m.get("quiet_s") or 0) >= 1000:
            big.append({"file": os.path.relpath(mf, DATA), "item": m["item"], "pos": m.get("pos"), "quiet_s": m["quiet_s"],
                        "heats": m.get("heats"), "start_c": m.get("start_c"), "start_hot_c": m.get("start_hot_c"),
                        "run_start_pst": pst(m["t_start_ms"]), "prev_end_pst": pst(m["prev_end_ms"]),
                        "runner_start_implied_pst": pst(m["prev_end_ms"] + 3600000)})
anchors_csv = {}
hdr = None
for ln in open(D("runs-anchors.csv"), encoding="utf-8"):
    row = ln.rstrip("\n").split(",")
    if hdr is None:
        hdr = row
        continue
    rr = dict(zip(hdr, row))
    anchors_csv[int(rr["t0_ms"])] = rr
QUIET_REQ, GATE_IDLE_MS = 2.0, 800
a1rows = {}
for b, t in sorted(TRAINS.items()):
    bd = D("aifoundry3", "e188", f"p{b}")
    tr = [m for m in jl(os.path.join(bd, "marks.jsonl")) if m.get("kind") == "train"]
    last_end = max(m["t_end_ms"] for m in tr)
    am = jl(os.path.join(bd, "a1", "marks.jsonl"))
    first = sorted([m for m in am if m.get("kind") == "run"], key=lambda m: m["t_start_ms"])[0]
    heaters_before = sum(1 for m in am if m.get("kind") == "heater" and m["t_end_ms"] <= first["t_start_ms"])
    runs = [r for r in jl(os.path.join(bd, "a1", "runs.jsonl")) if r.get("pos") == first["pos"] and r.get("item") == first["item"]]
    t0 = min(r["t_start_ms"] for r in runs)
    q_cfg = json.load(open(os.path.join(bd, "a1", "configs.json")))["args"]["quiet_s"]
    pe_rec, pe_meas = first["prev_end_ms"], last_end
    row = anchors_csv.get(t0, {})
    a1rows[t] = {
        "block": b, "train_last_process_end_pst": pst(last_end), "runner_start_implied_pst": pst(pe_rec + 3600000),
        "runner_start_minus_train_end_s": (pe_rec + 3600000 - last_end) / 1000.0,
        "a1_first_run": first["item"], "a1_first_run_start_pst": pst(first["t_start_ms"]), "a1_first_launch_pst": pst(t0),
        "heats": first.get("heats"), "heaters_in_a1_before_it": heaters_before, "start_c": first.get("start_c"),
        "start_hot_c": first.get("start_hot_c"), "quiet_s_recorded": first["quiet_s"], "prev_end_recorded_pst": pst(pe_rec),
        "gap_train_end_to_run_start_s": (first["t_start_ms"] - last_end) / 1000.0,
        "gap_train_end_to_first_launch_s": (t0 - last_end) / 1000.0,
        "quiet_required_s": q_cfg,
        "quiet_gate_recorded_pass": not (first["quiet_s"] < q_cfg - 0.05),
        "quiet_gate_measured_pass": not ((first["t_start_ms"] - last_end) / 1000.0 < q_cfg - 0.05),
        "idle_after_prev_ms_recorded": (t0 - 1200) - pe_rec, "idle_after_prev_ms_measured": (t0 - 1200) - pe_meas,
        "idle_gate_recorded_pass": (t0 - 1200) - pe_rec >= GATE_IDLE_MS,
        "idle_gate_measured_pass": (t0 - 1200) - pe_meas >= GATE_IDLE_MS,
        "runs_anchors_csv": {k: row.get(k) for k in ("pass", "item", "quiet_s", "prev_end_ms", "idle_after_prev_ms", "idle_ok",
                                                      "fail", "fail_reasons", "D")} if row else None}
g1 = [v["gap_train_end_to_run_start_s"] for v in a1rows.values()]
g2 = [v["gap_train_end_to_first_launch_s"] for v in a1rows.values()]
qr = [v["quiet_s_recorded"] for v in a1rows.values()]
rs = [v["runner_start_minus_train_end_s"] for v in a1rows.values()]
s3 = {"code_lines": code3, "runs_with_quiet_at_least_1000_s": big, "a1_by_train": a1rows,
      "ranges": {"quiet_s_recorded": [min(qr), max(qr)], "gap_to_run_start_s": [min(g1), max(g1)],
                 "gap_to_first_launch_s": [min(g2), max(g2)], "runner_start_minus_train_end_s": [min(rs), max(rs)]},
      "gates_all_pass_both_ways": all(v["quiet_gate_recorded_pass"] and v["quiet_gate_measured_pass"] and v["idle_gate_recorded_pass"]
                                      and v["idle_gate_measured_pass"] for v in a1rows.values())}
res["s3_recorded_quiet"] = s3
txt += ["3. The recorded quiet: the runner's starting value, and each train's closing anchor runner a1",
        f"  run_e78.py: the starting value on line(s) {code3['run_e78_starting_value']}, the recorded quiet on {code3['run_e78_quiet']}; "
        f"reduce_e78.py: prev_end_ms read on {code3['reduce_e78_prev_end']}, idle_after_prev_ms on {code3['reduce_e78_idle_after_prev']}, "
        f"the quiet gate on {code3['reduce_e78_quiet_gate']}, the idle gate on {code3['reduce_e78_idle_gate']} (800 ms on "
        f"{code3['reduce_e78_gate_800']})",
        f"  run marks with a recorded quiet of 1,000 s or more: {len(big)}"]
txt += [f"    {r['file']} #{r['pos']} {r['item']}: quiet {r['quiet_s']} s, heats {r['heats']}, start {r['start_c']} C (hot {r['start_hot_c']}), "
        f"run start {r['run_start_pst']}, prev_end {r['prev_end_pst']} (+1 h = {r['runner_start_implied_pst']})" for r in big]
for t, v in a1rows.items():
    c = v["runs_anchors_csv"] or {}
    txt.append(f"  {t} (p{v['block']}): the train's last process ended {v['train_last_process_end_pst']}; a1 started about "
               f"{v['runner_start_implied_pst']} (+{v['runner_start_minus_train_end_s']:.3f} s; prev_end + 1 h); its first run "
               f"{v['a1_first_run']} started {v['a1_first_run_start_pst']}, first launch {v['a1_first_launch_pst']}; heats {v['heats']}, "
               f"heaters before it {v['heaters_in_a1_before_it']}, start {v['start_c']} C (hot {v['start_hot_c']}); quiet recorded "
               f"{v['quiet_s_recorded']} s; measured {v['gap_train_end_to_run_start_s']:.3f} s to the run's start, "
               f"{v['gap_train_end_to_first_launch_s']:.3f} s to its first launch; quiet gate (at least {v['quiet_required_s']} - 0.05 s) "
               f"{'pass' if v['quiet_gate_recorded_pass'] else 'FAIL'} recorded / {'pass' if v['quiet_gate_measured_pass'] else 'FAIL'} "
               f"measured; idle_after_prev_ms {v['idle_after_prev_ms_recorded']} recorded / {v['idle_after_prev_ms_measured']} measured "
               f"(gate 800: {'pass' if v['idle_gate_recorded_pass'] else 'FAIL'} / {'pass' if v['idle_gate_measured_pass'] else 'FAIL'}); "
               f"runs-anchors.csv: idle_after_prev_ms {c.get('idle_after_prev_ms')}, idle_ok {c.get('idle_ok')}, fail {c.get('fail')}")
txt += [f"  ranges: recorded quiet {min(qr)}-{max(qr)} s; measured {min(g1):.3f}-{max(g1):.3f} s to the run's start, {min(g2):.3f}-"
        f"{max(g2):.3f} s to the first launch; the runner started {min(rs):.3f}-{max(rs):.3f} s after the train's last process end",
        f"  every gate passes under both the recorded and the measured previous end: {s3['gates_all_pass_both_ways']}", ""]

# ---------------------------------------------------------------- 4. E188-C's coverage
cc = json.load(open(D("ccheck", "ccheck-all.json")))["launches"]
verd = {(v.get("t_start_ms"), v.get("t_end_ms")): v["verdict"] for v in cc}
sc = json.load(open(D("scored-e188.json")))
kept = sc["kept_passes"]
groups = {"scorer: kept kinds passes": [], "scorer: trains (train records)": [], "scorer: trains' anchors (a0, a1)": [],
          "smoke: kinds items": [], "smoke: train processes": []}
for p in kept:
    groups["scorer: kept kinds passes"] += [r for r in jl(D("aifoundry3", "e188", f"p{p}", "runs.jsonl")) if r.get("item")]
for b in sorted(TRAINS):
    groups["scorer: trains (train records)"] += jl(D("aifoundry3", "e188", f"p{b}", "train.jsonl"))
    for sub in ("a0", "a1"):
        groups["scorer: trains' anchors (a0, a1)"] += [r for r in jl(D("aifoundry3", "e188", f"p{b}", sub, "runs.jsonl")) if r.get("item")]
groups["smoke: kinds items"] = [r for r in jl(D("aifoundry3", "e188-smoke", "p18801", "runs.jsonl")) if r.get("item")]
groups["smoke: train processes"] = jl(D("aifoundry3", "e188-smoke", "p18801", "train", "train.jsonl"))
named = set()
cov = {}
for g, rs_ in groups.items():
    keys = [(r.get("t_start_ms"), r.get("t_end_ms")) for r in rs_]
    named.update(keys)
    vs = {}
    for k in keys:
        vs[verd.get(k, "no C verdict")] = vs.get(verd.get(k, "no C verdict"), 0) + 1
    cov[g] = {"records": len(keys), "verdicts": vs}
burn = []
for p in kept:
    burn += [m for m in jl(D("aifoundry3", "e188", f"p{p}", "marks.jsonl")) if m.get("kind") == "burnin"]
inb, vb, other = 0, {}, []
for k, v in verd.items():
    if k in named:
        continue
    if any(m["t_start_ms"] <= k[0] <= m["t_end_ms"] for m in burn):
        inb += 1
        vb[v] = vb.get(v, 0) + 1
    else:
        other.append(k)
cov["burn-ins (C launches inside a burnin mark)"] = {"records": inb, "verdicts": vb, "burnin_marks": len(burn)}
scorer_n = sum(cov[g]["records"] for g in groups if g.startswith("scorer"))
smoke_n = sum(cov[g]["records"] for g in groups if g.startswith("smoke"))
c_status_n = sum(v["launches"] for v in sc["c_status"]["trains"].values())   # its train blocks: train records and their anchors
allv = {}
for v in verd.values():
    allv[v] = allv.get(v, 0) + 1
s4 = {"check_of_c_launches": len(cc), "distinct_time_keys": len(verd), "check_of_c_verdicts": allv, "groups": cov,
      "scorer_set": scorer_n, "scorer_c_status_train_block_launches": c_status_n, "smoke": smoke_n, "burn_ins": inb,
      "named_by_none": len(other),
      "score_e188_c_status_lines": lines_with(os.path.join(TOP, "tools/claims-v3/e188/score_e188.py"), "def c_status(raw, ccheck_files, kept_passes):"),
      "rule_e188_c": sc["rules"]["E188-C"]}
res["s4_c_coverage"] = s4
txt += [f"4. E188-C's coverage: the check of C judged {len(cc)} launches ({json.dumps(allv, sort_keys=True)}; {len(verd)} distinct start-end keys)"]
txt += [f"  {g}: {v['records']} records, {json.dumps(v['verdicts'], sort_keys=True)}" for g, v in cov.items()]
txt += [f"  the kit scorer's set (score_e188.py c_status, line(s) {s4['score_e188_c_status_lines']}): {scorer_n} launches "
        f"(scored-e188.json's c_status counts {c_status_n} in the seven train blocks: the train records and their anchors; the kinds "
        f"passes' {cov['scorer: kept kinds passes']['records']} are its kept passes' item records); the smoke {smoke_n}; the burn-ins "
        f"{inb}; named by none {len(other)}; "
        f"in all {scorer_n + smoke_n + inb + len(other)}",
        f"  E188-C as scored: {sc['rules']['E188-C']['verdict']}", ""]

# ---------------------------------------------------------------- 5. the C-logging host's hash
def fnv(b, basis):
    h = basis
    for x in b:
        h ^= x
        h = (h * PRIME) & 0xFFFFFFFFFFFFFFFF
    return "%016x" % h


hl = {}
for f in sorted(glob.glob(D("ccheck", "c-log-p*.jsonl.gz"))):
    recs = jl(f)
    tiles = [r for r in recs if r.get("kind") == "tiles"]
    cs = [r for r in recs if r.get("kind") == "c"]
    host = std = 0
    fn = set()
    for r in tiles:
        b = bytes.fromhex(r["a"]) + bytes.fromhex(r["b"])
        host += fnv(b, BASIS_HOST) == r["fnv"]
        std += fnv(b, BASIS_STD) == r["fnv"]
        fn.add(r["fnv"])
    hl[os.path.basename(f)] = {"tiles_records": len(tiles), "bytes_each": sorted({len(r["a"]) // 2 + len(r["b"]) // 2 for r in tiles}),
                               "equal_host_basis": host, "equal_standard_basis": std, "c_records": len(cs),
                               "c_records_whose_fnv_is_a_tiles_record_of_its_log": sum(1 for r in cs if r.get("fnv") in fn)}
tot = {k: sum(v[k] for v in hl.values()) for k in ("tiles_records", "equal_host_basis", "equal_standard_basis", "c_records",
                                                    "c_records_whose_fnv_is_a_tiles_record_of_its_log")}
trn = {k: sum(v[k] for f, v in hl.items() if int(f[7:12]) in TRAINS) for k in ("tiles_records", "equal_host_basis", "equal_standard_basis")}
s5 = {"basis_host": str(BASIS_HOST), "basis_standard": str(BASIS_STD), "prime": PRIME, "by_log": hl, "total": tot, "train_logs": trn,
      "code_lines": {"patch_host_ccheck_ccFnv": lines_with(os.path.join(TOP, "tools/claims-v3/ccheck/patch_host_ccheck.py"), "uint64_t h = 1469598103934665603ull;"),
                     "ccheck_fnv64": lines_with(os.path.join(TOP, "tools/claims-v3/ccheck/ccheck.py"), "h = 1469598103934665603"),
                     "pairing_e188_fnv64": lines_with(os.path.join(TOP, "tools/claims-v3/e188/pairing_e188.py"), "h = 1469598103934665603"),
                     "pairing_e188_named_fnv1a64": lines_with(os.path.join(TOP, "tools/claims-v3/e188/pairing_e188.py"), "FNV-1a 64"),
                     "e186_kit_note2_basis": lines_with(os.path.join(TOP, "tools/claims-v3/e186/KIT.md.dated-note-2.md"),
                                                    "not FNV-1a's standard 14695981039346656037")}}
res["s5_hash"] = s5
txt += ["5. The C-logging host's hash (FNV-1a's form: each byte xored in, then a multiply by 1099511628211, mod 2^64)",
        f"  offset basis as used {BASIS_HOST} (patch_host_ccheck.py line(s) {s5['code_lines']['patch_host_ccheck_ccFnv']}, ccheck.py "
        f"{s5['code_lines']['ccheck_fnv64']}, pairing_e188.py {s5['code_lines']['pairing_e188_fnv64']}; named 'FNV-1a 64' on pairing_e188.py "
        f"line(s) {s5['code_lines']['pairing_e188_named_fnv1a64']}; E186's kit note 2 names the basis on line(s) {s5['code_lines']['e186_kit_note2_basis']}); "
        f"the standard basis {BASIS_STD}"]
txt += [f"  {f}: {v['tiles_records']} tiles records ({v['bytes_each']} bytes each, A then B): {v['equal_host_basis']} equal under the host's "
        f"basis, {v['equal_standard_basis']} under the standard; C records {v['c_records']}, {v['c_records_whose_fnv_is_a_tiles_record_of_its_log']} "
        f"with the hash of a tiles record of their log" for f, v in hl.items()]
txt += [f"  in all: {tot['tiles_records']} tiles records, {tot['equal_host_basis']} under the host's basis, {tot['equal_standard_basis']} under "
        f"the standard; the seven train logs {trn['tiles_records']}, {trn['equal_host_basis']}, {trn['equal_standard_basis']}; C records "
        f"{tot['c_records']}, {tot['c_records_whose_fnv_is_a_tiles_record_of_its_log']} paired to a tiles record of their log", ""]

# ---------------------------------------------------------------- 6. the window under two readings of G
def at(hms):
    h, m, s = (int(x) for x in hms.split(":"))
    return dt.datetime(2026, 11, 15, h, m, s, tzinfo=PST)


def ceil_min(t):
    return t if t.second == 0 else (t.replace(second=0) + dt.timedelta(minutes=1))


rd = open(RM, encoding="utf-8").read()
steps = {"5": re.search(r"5 the sync \((\d\d:\d\d:\d\d)", rd).group(1),
         "6": re.search(r"6 the build, attempt 1 \(\d\d:\d\d:\d\d-(\d\d:\d\d:\d\d)", rd).group(1),
         "8": re.search(r"8 the dry pass \(\d\d:\d\d:\d\d-(\d\d:\d\d:\d\d)", rd).group(1),
         "9": re.search(r"9 the launch, FULL yes \((\d\d:\d\d:\d\d)", rd).group(1),
         "11": re.search(r"step 11 started at (\d\d:\d\d:\d\d)", rd).group(1)}
q = open(D("logs", "queue.out"), encoding="utf-8").read()
starts = re.findall(r"^(\d\d:\d\d:\d\d) p(\d+) \((\w+)\) starts at T0\+(\d+) s \(projected (\d+) s\)", q, re.M)
last_q = starts[-1]
dl = re.search(r"deadline (\d{4}-\d\d-\d\d \d\d:\d\d:\d\d)", q).group(1)
sess_start = open(D("logs", "config-session-start.json.time")).read().strip()[11:19]
sess_end = open(D("logs", "config-session-end.json.time")).read().strip()[11:19]
first_runner = re.search(r"^(\d\d:\d\d:\d\d) \[aifoundry3\] E78 pass", open(D("logs", "session.log"), encoding="utf-8").read(), re.M).group(1)
win = {}
for name, g in (("G = his words, 15:05:27", "15:05:27"), ("G = the booking, 15:10:41 (as run)", "15:10:41")):
    G = at(g)
    ls_, le_ = ceil_min(G + dt.timedelta(hours=1, minutes=30)), ceil_min(G + dt.timedelta(hours=3, minutes=30))
    q_end = at(last_q[0]) + dt.timedelta(seconds=int(last_q[4]))
    chk = {"steps 5, 6, 8, 9 at or before the last start": all(at(steps[k]) <= ls_ for k in ("5", "6", "8", "9")),
           "the session's start (T0) at or before the last start": at(sess_start) <= ls_,
           "step 9: launch + 100 min within the last end": at(steps["9"]) + dt.timedelta(minutes=100) <= le_,
           "the queue's last item: start + projected within the last end": q_end <= le_,
           "the session's end within the last end": at(sess_end) <= le_,
           "step 11: start + 10 min within the last end": at(steps["11"]) + dt.timedelta(minutes=10) <= le_}
    win[name] = {"G": g, "last_start": ls_.strftime("%H:%M"), "last_end": le_.strftime("%H:%M"), "checks": chk,
                 "all_hold": all(chk.values()), "queue_last_item_projected_end": q_end.strftime("%H:%M:%S")}
s6 = {"times": {"steps": steps, "session_start": sess_start, "first_runner_line": first_runner, "queue_last_start": last_q[0],
                "queue_last_item": f"p{last_q[1]} ({last_q[2]})", "queue_last_projected_s": int(last_q[4]), "queue_deadline_as_run": dl,
                "session_end": sess_end}, "readings": win}
res["s6_window"] = s6
txt += ["6. The window under two readings of G (form (a): last start G+1:30, last end G+3:30, each rounded up to the whole minute)",
        f"  times: steps 5 {steps['5']}, 6 ended {steps['6']}, 8 ended {steps['8']}, 9 {steps['9']}, 11 {steps['11']} (README); T0 "
        f"{sess_start}; the first runner line {first_runner} (session.log); the queue's last start {last_q[0]} (p{last_q[1]}, projected "
        f"{last_q[4]} s), its deadline as run {dl} (queue.out); the session's end {sess_end}"]
for k, v in win.items():
    txt.append(f"  {k}: last start {v['last_start']}, last end {v['last_end']}; every gate holds: {v['all_hold']} "
               f"(the queue's last item projected to end {v['queue_last_item_projected_end']})")
    txt += [f"    {c}: {'yes' if b else 'NO'}" for c, b in v["checks"].items()]
txt.append("")

# ---------------------------------------------------------------- 7. margins at the session's s, and the range of s
R = sc["rules"]
s_used = sc["scale"]["s_used"]
T = {}
for t in ORDER:
    e, L = R[f"E188-{t}"]["estimate"], R[f"E188-{t}"]["lines_w"]
    T[t] = {"mean": e["mean"], "hw": e["hw"], "se": e["se"], "a": L["M10"] / s_used, "inc": L["M12"] - L["M10"], "se12": L["M12_se"]}
GB, GA = R["E188-GB1"], R["E188-GA23"]
BP, MM = R["E188-BPOS"], R["E188-M"]


def size(d, w):
    return "PASS" if abs(d) <= w else ("FAIL LOW" if d > 0 else "FAIL HIGH")


def repeat(lo, hi, ref):
    return "AGREES" if lo <= ref[1] and hi >= ref[0] else ("DIFFERS HIGH" if lo > ref[1] else "DIFFERS LOW")


def sign(lo, hi):
    return "POSITIVE" if lo > 0 else ("NEGATIVE" if hi < 0 else "NOT RESOLVED")


def which(a, b):
    return {(True, True): "BOTH", (True, False): "M12", (False, True): "M10", (False, False): "NEITHER"}[(a == "PASS", b == "PASS")]


def words(s):
    w = {}
    for t, v in T.items():
        l10 = v["a"] * s
        l12 = l10 + v["inc"]
        s12 = size(v["mean"] - l12, math.sqrt(v["hw"] ** 2 + (1.96 * v["se12"]) ** 2))
        s10 = size(v["mean"] - l10, v["hw"])
        w[f"E188-{t}"] = which(s12, s10)
        w[f"E188-{t} SIZE M12"], w[f"E188-{t} SIZE M10"] = s12, s10
    y = [T[t]["mean"] - T[t]["a"] * s for t in GB["trains"]]
    g = sum(y) / len(y)
    hw = GB["gamma_B"]["hw"]
    w["E188-GB1"] = sign(g - hw, g + hw)
    w["E188-GB1 SIZE M12"] = size(g - GB["M12_gamma_B_w"], math.sqrt(hw ** 2 + (1.96 * GB["M12_gamma_B_se_w"]) ** 2))
    w["E188-GB1 REPEAT"] = repeat(g - hw, g + hw, GB["E186_GB"])
    w["E188-GB1 SIZE M10 (beside)"] = size(g, hw)
    ga = (T["AALL"]["mean"] - T["AALL"]["a"] * s) / 23.0
    hwa = GA["gamma_A"]["hw"]
    w["E188-GA23"] = sign(ga - hwa, ga + hwa)
    w["E188-GA23 SIZE M12"] = size(ga - GA["M12_gamma_A_w"], math.sqrt(hwa ** 2 + (1.96 * GA["M12_gamma_A_se_w"]) ** 2))
    w["E188-GA23 REPEAT"] = repeat(ga - hwa, ga + hwa, GA["E186_GA"])
    w["E188-GA23 SIZE M10 (beside)"] = size(ga, hwa)
    ys = {t: T[t]["mean"] - T[t]["a"] * s for t in ONE_BIT_B}
    wt = {t: 1.0 / T[t]["se"] ** 2 for t in ONE_BIT_B}
    yw = sum(wt[t] * ys[t] for t in ONE_BIT_B) / sum(wt.values())
    qb = sum(wt[t] * (ys[t] - yw) ** 2 for t in ONE_BIT_B)
    w["E188-BPOS"] = "FLAT" if qb <= BP["flat_q"]["chi2_95"] else "VARIES"
    q12 = sum((T[t]["mean"] - T[t]["a"] * s - T[t]["inc"]) ** 2 / (T[t]["se"] ** 2 + T[t]["se12"] ** 2) for t in ORDER)
    q10 = sum((T[t]["mean"] - T[t]["a"] * s) ** 2 / T[t]["se"] ** 2 for t in ORDER)
    c12, c10 = q12 <= MM["M12"]["chi2_95"], q10 <= MM["M10"]["chi2_95"]
    w["E188-M"] = {(True, True): "BOTH", (True, False): "M12", (False, True): "M10", (False, False): "NEITHER"}[(c12, c10)]
    return w, {"GB1": g, "GA23": ga, "BPOS_Q": qb, "M12_Q": q12, "M10_Q": q10}


w0, v0 = words(s_used)
kit = {}
for t in ORDER:
    kit[f"E188-{t}"] = R[f"E188-{t}"]["which"]
    kit[f"E188-{t} SIZE M12"], kit[f"E188-{t} SIZE M10"] = R[f"E188-{t}"]["size_M12"], R[f"E188-{t}"]["size_M10"]
kit.update({"E188-GB1": GB["verdict"], "E188-GB1 SIZE M12": GB["size_M12"], "E188-GB1 REPEAT": GB["repeat_E186_GB"],
            "E188-GB1 SIZE M10 (beside)": GB["size_M10_beside"], "E188-GA23": GA["verdict"], "E188-GA23 SIZE M12": GA["size_M12"],
            "E188-GA23 REPEAT": GA["repeat_E186_GA"], "E188-GA23 SIZE M10 (beside)": GA["size_M10_beside"],
            "E188-BPOS": BP["flat_q"]["word"], "E188-M": MM["verdict"]})
same = {k: w0[k] == kit[k] for k in kit}
dq = {"GB1": abs(v0["GB1"] - GB["gamma_B"]["mean"]), "GA23": abs(v0["GA23"] - GA["gamma_A"]["mean"]),
      "BPOS_Q": abs(v0["BPOS_Q"] - BP["flat_q"]["Q"]), "M12_Q": abs(v0["M12_Q"] - MM["M12"]["Q"]), "M10_Q": abs(v0["M10_Q"] - MM["M10"]["Q"])}
marg = {}
for t, v in T.items():
    l10 = v["a"] * s_used
    l12 = l10 + v["inc"]
    w12 = math.sqrt(v["hw"] ** 2 + (1.96 * v["se12"]) ** 2)
    marg[f"E188-{t} SIZE M12"] = w12 - abs(v["mean"] - l12)
    marg[f"E188-{t} SIZE M10"] = v["hw"] - abs(v["mean"] - l10)
g, hw = GB["gamma_B"]["mean"], GB["gamma_B"]["hw"]
marg["E188-GB1 SIZE M12"] = math.sqrt(hw ** 2 + (1.96 * GB["M12_gamma_B_se_w"]) ** 2) - abs(g - GB["M12_gamma_B_w"])
marg["E188-GB1 REPEAT (overlap; negative = the gap)"] = min(g + hw, GB["E186_GB"][1]) - max(g - hw, GB["E186_GB"][0])
ga, hwa = GA["gamma_A"]["mean"], GA["gamma_A"]["hw"]
marg["E188-GA23 SIZE M12"] = math.sqrt(hwa ** 2 + (1.96 * GA["M12_gamma_A_se_w"]) ** 2) - abs(ga - GA["M12_gamma_A_w"])
marg["E188-GA23 REPEAT (overlap; negative = the gap)"] = min(ga + hwa, GA["E186_GA"][1]) - max(ga - hwa, GA["E186_GA"][0])
marg["E188-BPOS (point - Q)"] = BP["flat_q"]["chi2_95"] - BP["flat_q"]["Q"]
marg["E188-M M12 (point - Q)"] = MM["M12"]["chi2_95"] - MM["M12"]["Q"]
marg["E188-M M10 (point - Q)"] = MM["M10"]["chi2_95"] - MM["M10"]["Q"]
STEP = 1e-5


def edge(direction):
    k = 0
    while True:
        k += 1
        s = s_used + direction * k * STEP
        if s <= 0.5 or s >= 2.0:
            return s, []
        w, _ = words(s)
        ch = sorted(x for x in w if w[x] != w0[x])
        if ch:
            return s, [f"{x}: {w0[x]} -> {w[x]}" for x in ch]


lo_s, lo_ch = edge(-1)
hi_s, hi_ch = edge(+1)
at1, _ = words(1.0)
s7 = {"s_used": s_used, "kit_words_reproduced": all(same.values()), "not_reproduced": sorted(k for k, v in same.items() if not v),
      "largest_figure_difference": dq, "margins_at_s_used": marg,
      "s_range_every_word_holds": [lo_s + STEP, hi_s - STEP], "first_change_below": {"s": lo_s, "changes": lo_ch},
      "first_change_above": {"s": hi_s, "changes": hi_ch}, "words_changed_at_s_1": sorted(f"{x}: {w0[x]} -> {at1[x]}" for x in at1 if at1[x] != w0[x]),
      "scan_step": STEP, "lines_at_lines": lines_with(os.path.join(TOP, "tools/claims-v3/e188/forecast_e188.py"), "def lines_at(row, s, rate_ratio):")}
res["s7_margins_and_s"] = s7
txt += ["7. Margins at the session's s, and the range of s over which every word that takes s holds (post hoc; deciding nothing)",
        f"  s = {s_used!r}; at it this arithmetic gives the kit's words: {s7['kit_words_reproduced']} ({len(same)} words and sub-words; "
        f"largest figure difference {max(dq.values()):.3e}); forecast_e188.lines_at on line(s) {s7['lines_at_lines']}"]
txt += [f"  {k}: {v:+.5f}" for k, v in marg.items()]
txt += [f"  every word and sub-word holds for s in [{s7['s_range_every_word_holds'][0]:.5f}, {s7['s_range_every_word_holds'][1]:.5f}] "
        f"(step {STEP:g}; every train's rate ratio as measured)",
        f"  first change below: at s {lo_s:.5f}: {'; '.join(lo_ch) if lo_ch else 'none within the scan'}",
        f"  first change above: at s {hi_s:.5f}: {'; '.join(hi_ch) if hi_ch else 'none within the scan'}",
        f"  at s = 1 (rate ratios as measured), words that change: {s7['words_changed_at_s_1'] if s7['words_changed_at_s_1'] else 'none'}", ""]

os.makedirs(OUT, exist_ok=True)
with open(os.path.join(OUT, "posthoc-note1-e188.json"), "w") as f:
    json.dump(r9(res), f, indent=1, sort_keys=True)
    f.write("\n")
with open(os.path.join(OUT, "posthoc-note1-e188.txt"), "w") as f:
    f.write("\n".join(txt) + "SPDX-License-Identifier: Apache-2.0\n")
print("\n".join(txt))
