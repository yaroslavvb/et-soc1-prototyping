#!/usr/bin/env python3
"""E192's data README, dated note 1 (Sat 14 Nov 2026, after the data verifier): the figures the note quotes, read again from committed
files. Post hoc: it decides nothing, scores nothing and changes no committed file.

    python3 -I -B docs/reports/data/2026-11-14-e192-intbits-aifoundry3/posthoc_note1_e192.py [--out DIR] [--data DIR --top DIR]

It reads only the files of this directory's data commit: the 27 files SHA256SUMS lists, README.md and SHA256SUMS (never a file added
after them, so the note's own files do not change its outputs); and from the repository: the registration's list
tools/claims-v3/e192/SHA256SUMS-e192-registration and the kit's list SHA256SUMS-e192-kit, each read entry by entry, with E192.md,
KIT.md, session_e192.sh, collect_e192.py, rb/s11_a3_session_e192.sh, logs/dmcmd-audit-e192.txt, check_e192.py and the proposal's
host/main.cpp and intbits_args.h read as text (each pinned by one of the two lists); and E189's
data directory's SHA256SUMS with the file it pins at session/session.log (E189's committed session end).

Section 0: the anchors: SHA256SUMS read entry by entry; the sha256 of README.md and SHA256SUMS; the two lists read entry by entry;
E189's session log against its data directory's SHA256SUMS.
Section 1: the rest. E189's session end; step 7's config read as README.md gives it; the session's first card command (the probe) and
its end; the die at the session's first sample; the lines of E192.md, KIT.md and README.md the note cites.
Section 2: the launch output. The box's manifest (box-manifest.txt) against this directory's files: which of its 26 files are here at
the box's sha256 (the telemetry through its gzip), and which one is here only as the bytes of another file; the kit's lines that say why.
Section 3: the sizes behind registered checks 2 and 3, from run/runs.jsonl: L1 data misses and instruction-cache misses a launch and an
iteration, per arm. The checks' verdicts are the kit's checker's (check_e192.py, run after the data commit); nothing here re-decides them.

It writes posthoc-note1-e192.json and posthoc-note1-e192.txt beside itself (or in --out), with paths relative to this directory or the
repository's top, times in PST (UTC-8, fixed), floats rounded to 9 significant digits and no run time, so a re-run from the same tree
under the same interpreter writes both byte for byte. --data and --top name this directory and the repository's top when the script
runs from a copy. Standard library only. /usr/bin/python3 3.12.3 wrote the committed outputs.
SPDX-License-Identifier: Apache-2.0
"""
import datetime
import gzip
import hashlib
import json
import os
import re
import statistics
import sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
PST = datetime.timezone(datetime.timedelta(hours=-8), "PST")
E192 = "tools/claims-v3/e192"
REG = E192 + "/SHA256SUMS-e192-registration"
KITL = E192 + "/SHA256SUMS-e192-kit"
E189 = "docs/reports/data/2026-11-14-e189-blind-day-aifoundry3"
REST_S = 40 * 60
MEASURED = range(1, 9)      # E192.md: 9 passes, pass 0 the warm-up; passes 1-8 measured


def arg(name, default):
    a = sys.argv[1:]
    return a[a.index(name) + 1] if name in a else default


DATA = os.path.abspath(arg("--data", HERE))
TOP = os.path.abspath(arg("--top", os.path.join(DATA, "..", "..", "..", "..")))
OUT = os.path.abspath(arg("--out", DATA))


def g(x):
    return float("%.9g" % x)


def sha_bytes(b):
    return hashlib.sha256(b).hexdigest()


def sha(path):
    with open(path, "rb") as f:
        return sha_bytes(f.read())


def sums(path):
    out = []
    for ln in open(path, encoding="utf-8"):
        ln = ln.rstrip("\n")
        if ln.strip():
            h, p = ln.split("  ", 1)
            out.append((h, p))
    return out


def check_list(listpath, base):
    ent = sums(listpath)
    bad = [p for h, p in ent if not os.path.isfile(os.path.join(base, p)) or sha(os.path.join(base, p)) != h]
    return len(ent) - len(bad), len(ent), bad


def pst(epoch_s):
    return datetime.datetime.fromtimestamp(epoch_s, PST).strftime("%Y-%m-%d %H:%M:%S")


def epoch(s):
    return datetime.datetime.strptime(s, "%Y-%m-%d %H:%M:%S").replace(tzinfo=PST).timestamp()


def mmss(s):
    s = int(round(s))
    return "%d min %02d s" % (s // 60, s % 60)


def lines_matching(path, pattern, flags=0):
    rx = re.compile(pattern, flags)
    return [i for i, ln in enumerate(open(path, encoding="utf-8", errors="replace"), 1) if rx.search(ln)]


def one(path, pattern, what):
    ls = lines_matching(path, pattern)
    if len(ls) != 1:
        raise SystemExit("posthoc_note1_e192: expected one line for %s in %s, found %s" % (what, path, ls))
    return ls[0]


def first_after(path, anchor, pattern):
    ra, rp = re.compile(anchor), re.compile(pattern)
    seen = False
    for i, ln in enumerate(open(path, encoding="utf-8", errors="replace"), 1):
        seen = seen or bool(ra.search(ln))
        if seen and rp.search(ln):
            return i
    raise SystemExit("posthoc_note1_e192: no line for %s after %s in %s" % (pattern, anchor, path))


def line_text(path, n):
    with open(path, encoding="utf-8", errors="replace") as f:
        for i, ln in enumerate(f, 1):
            if i == n:
                return ln.rstrip("\n")
    return None


txt = ["E192's data README, dated note 1: post hoc readings of committed files (decides nothing; scores nothing)",
       "interpreter: python %d.%d.%d" % sys.version_info[:3]]
res = {"note": "E192 data README dated note 1 (Sat 14 Nov 2026): post hoc, decides nothing, scores nothing",
       "interpreter": "python %d.%d.%d" % sys.version_info[:3]}

# ---------------------------------------------------------------- 0. anchors
ent = sums(os.path.join(DATA, "SHA256SUMS"))
okd = [p for h, p in ent if sha(os.path.join(DATA, p)) == h]
reg = check_list(os.path.join(TOP, REG), TOP)
kit = check_list(os.path.join(TOP, KITL), TOP)
e189_sums = dict((p, h) for h, p in sums(os.path.join(TOP, E189, "SHA256SUMS")))
e189_log = os.path.join(TOP, E189, "session", "session.log")
e189_ok = e189_sums.get("session/session.log") == sha(e189_log)
pinned = {p for _, p in sums(os.path.join(TOP, REG))} | {p for _, p in sums(os.path.join(TOP, KITL))}
read_as_text = [E192 + "/E192.md", E192 + "/KIT.md", E192 + "/session_e192.sh", E192 + "/collect_e192.py",
                E192 + "/rb/s11_a3_session_e192.sh", E192 + "/logs/dmcmd-audit-e192.txt", E192 + "/check_e192.py",
                E192 + "/proposal/src/host/main.cpp", E192 + "/proposal/src/intbits_args.h"]
res["anchors"] = {"SHA256SUMS_ok": len(okd), "SHA256SUMS_entries": len(ent),
                  "README.md_sha256": sha(os.path.join(DATA, "README.md")),
                  "SHA256SUMS_sha256": sha(os.path.join(DATA, "SHA256SUMS")),
                  "registration_list": {"ok": reg[0], "entries": reg[1], "bad": reg[2], "sha256": sha(os.path.join(TOP, REG))},
                  "kit_list": {"ok": kit[0], "entries": kit[1], "bad": kit[2], "sha256": sha(os.path.join(TOP, KITL))},
                  "files_read_as_text_pinned": {p: (p in pinned) for p in read_as_text},
                  "e189_session_log_at_its_SHA256SUMS": e189_ok}
txt += ["", "0. anchors",
        "  SHA256SUMS: %d of %d entries OK; with README.md and SHA256SUMS the data commit's %d files" % (len(okd), len(ent), len(ent) + 2),
        "  README.md sha256 %s" % res["anchors"]["README.md_sha256"],
        "  SHA256SUMS sha256 %s" % res["anchors"]["SHA256SUMS_sha256"],
        "  %s: %d of %d entries OK (list sha256 %s)" % (REG, reg[0], reg[1], res["anchors"]["registration_list"]["sha256"]),
        "  %s: %d of %d entries OK (list sha256 %s)" % (KITL, kit[0], kit[1], res["anchors"]["kit_list"]["sha256"]),
        "  read as text, each pinned by one of the two lists: " + ", ".join("%s %s" % (os.path.basename(p), "yes" if pinned and p in pinned else "NO") for p in read_as_text),
        "  %s/session/session.log at its directory's SHA256SUMS: %s" % (E189, "yes" if e189_ok else "NO")]

# ---------------------------------------------------------------- 1. the rest
E192MD = os.path.join(TOP, E192, "E192.md")
KITMD = os.path.join(TOP, E192, "KIT.md")
README = os.path.join(DATA, "README.md")
SLOG = os.path.join(DATA, "session", "session.log")

n_end189 = one(e189_log, r"^\d{4}-\d\d-\d\d \d\d:\d\d:\d\d PST session end \(T0 \d+\)", "E189's session end")
m = re.match(r"^(\S+ \S+) PST session end \(T0 (\d+)\)", line_text(e189_log, n_end189))
e189_end, e189_t0 = m.group(1), int(m.group(2))
t_end189 = epoch(e189_end)

n_cfg = one(README, r"k6's config read before the session \(\d\d:\d\d:\d\d PST\)", "step 7's config read in README.md")
cfg_hms = re.search(r"k6's config read before the session \((\d\d:\d\d:\d\d) PST\)", line_text(README, n_cfg)).group(1)
n_cfg2 = one(README, r"step 7's reads \(et-who clean at \d\d:\d\d:\d\d\)", "step 7's reads in README.md")
cfg2_hms = re.search(r"step 7's reads \(et-who clean at (\d\d:\d\d:\d\d)\)", line_text(README, n_cfg2)).group(1)
day = e189_end.split()[0]
t_cfg = epoch(day + " " + cfg_hms)

AUDIT = os.path.join(TOP, E192, "logs", "dmcmd-audit-e192.txt")
cfg_lines = lines_matching(AUDIT, r": ettelem config: ")
cfg_cmds = []
for n in cfg_lines:
    mm = re.search(r": ettelem config: (\S+) \[(\w+)", line_text(AUDIT, n))
    if (mm.group(1), mm.group(2)) not in cfg_cmds:
        cfg_cmds.append((mm.group(1), mm.group(2)))
t0 = int(open(os.path.join(DATA, "session", "first-card-command.txt")).read().strip())
n_fcc = one(SLOG, r"the first card command at \d\d:\d\d:\d\d PST; the cap at \d\d:\d\d:\d\d PST \(\d+ s\)", "the first card command")
m = re.search(r"the first card command at (\d\d:\d\d:\d\d) PST; the cap at (\d\d:\d\d:\d\d) PST \((\d+) s\)", line_text(SLOG, n_fcc))
fcc_hms, cap_hms, cap_s = m.group(1), m.group(2), int(m.group(3))
n_end = one(SLOG, r"^\S+ \S+ PST session end \(T0 \d+\)", "E192's session end")
e192_end = re.match(r"^(\S+ \S+) PST", line_text(SLOG, n_end)).group(1)
n_ct = one(SLOG, r"card time \d+ s from the first card command \(cap \d+ s\)", "the card time")
card_s = int(re.search(r"card time (\d+) s from the first card command", line_text(SLOG, n_ct)).group(1))
t_end192 = epoch(e192_end)

with gzip.open(os.path.join(DATA, "run", "telemetry.jsonl.gz"), "rt") as f:
    first = json.loads(f.readline())
    die_min = first["temp_c"]["minshire"][0]
    for ln in f:
        d = json.loads(ln)["temp_c"]["minshire"][0]
        die_min = min(die_min, d)
first_die = first["temp_c"]["minshire"][0]
first_t = first["t_ms"] / 1000.0

rest = {
    "e189_session_end": e189_end + " PST", "e189_T0": e189_t0,
    "e189_session_end_line": "%s/session/session.log line %d" % (E189, n_end189),
    "rest_opens": pst(t_end189 + REST_S) + " PST",
    "step7_config_read_readme": cfg_hms + " PST", "step7_readme_lines": [n_cfg, n_cfg2], "step7_et_who_clean_readme": cfg2_hms + " PST",
    "step7_after_e189_end_s": int(round(t_cfg - t_end189)),
    "step7_config_commands_by_the_kit_audit": ["%s %s" % c_ for c_ in cfg_cmds], "step7_audit_lines": cfg_lines,
    "first_card_command_T0": t0, "first_card_command": pst(t0) + " PST",
    "first_card_command_session_log": {"line": n_fcc, "time": fcc_hms, "cap_at": cap_hms, "cap_s": cap_s},
    "first_card_command_after_e189_end_s": int(round(t0 - t_end189)),
    "first_card_command_after_step7_s": int(round(t0 - t_cfg)),
    "rest_met_by_s_as_run": int(round(t0 - t_end189 - REST_S)),
    "rest_short_by_s_if_step7_counted": int(round(REST_S - (t_cfg - t_end189))),
    "e192_session_end": e192_end + " PST", "e192_session_end_line": n_end,
    "card_time_s_session_log": card_s, "card_time_s_check": int(round(t_end192 - t0)),
    "span_step7_to_session_end_s_no_registered_quantity": int(round(t_end192 - t_cfg)),
    "die_first_sample_c": first_die, "die_first_sample_at": pst(first_t) + "." + ("%03d" % (first["t_ms"] % 1000)) + " PST",
    "die_lowest_c": die_min,
    "next_rest_opens": pst(t_end192 + REST_S) + " PST",
}
cite = {
    "E192.md": {
        "a departure is a dated amendment": one(E192MD, r"A departure is a dated", "status"),
        "reads only: the session's chain": one(E192MD, r"every device command the session's chain sends", "section 3"),
        "check 2: L1 data misses 0": one(E192MD, r"L1 data misses 0\.", "check 2"),
        "check 3: I-cache misses per iteration equal": one(E192MD, r"Instruction-cache misses per iteration equal across arms", "check 3"),
        "the cap from the session's first card command": one(E192MD, r"The cap is 65 card-minutes from the session's first card", "cap"),
        "the rest: E192's first card command": one(E192MD, r"E192's first card command at least 40 minutes after the end", "rest"),
        "the rest: the next session after E192's end": one(E192MD, r"the next session of ours there at least 40 minutes after E192's end", "rest 2"),
        "section 11: a gate before the sampler": one(E192MD, r"a gate before the sampler \(a holder, the lock, the rest, the window, the go\)", "s11"),
        "section 12: with the rest between": one(E192MD, r"with the rest between", "s12"),
        "section 17: the rest rule read on the box": one(E192MD, r"the 40-minute rest rule read on the box", "s17"),
    },
    "KIT.md": {
        "the first card command, the per-sensor probe": one(KITMD, r"the first card command, the per-sensor probe", "kit fcc"),
        "the session's card time and its cap count from it": one(KITMD, r"the session's card time and its cap count from it", "kit fcc 2"),
        "the audit covers k6's step 7 config read": one(KITMD, r"\(k6's step 7 config read\)", "kit audit"),
        "step 7: the reads": one(KITMD, r"^\| 7 \| the reads \|", "kit step 7"),
        "step 9: the session, the rest rule": one(KITMD, r"^\| 9 \| the session \|", "kit step 9"),
        "the rest rule: no E192 session starts within 40 minutes": one(KITMD, r"no E192 session starts within 40 minutes", "kit rest"),
        "the cap: from the first card command (the probe": one(KITMD, r"from the first card command \(the probe", "kit cap"),
        "section 7: the rest before E192's first card command": one(KITMD, r"The 40-minute rest before E192's first card command", "kit s7"),
    },
    "README.md": {
        "the config read before the session": n_cfg,
        "the rest row": one(README, r"^\| the rest \|", "rest row"),
        "step 7's reads": n_cfg2,
        "the rest line read at step 9": one(README, r"rest: 40 minutes since E189's session end", "rest line"),
        "COPY EXACT": one(README, r"\*\*COPY EXACT\*\*", "copy exact"),
        "26 files at the box's sha256": one(README, r"26 files at the box's sha256", "26 files"),
        "step 7's read the only other management command": one(README, r"Step 7's config read before the session", "only other"),
    },
}
res["rest"] = rest
res["lines"] = cite
txt += ["", "1. the rest, and step 7's config read",
        "  E189's session end: %s PST (%s)" % (e189_end, rest["e189_session_end_line"]),
        "  the rest opens (+40 min): %s" % rest["rest_opens"],
        "  step 7's config read, as README.md gives it: %s PST (line %d; line %d: et-who clean at %s)" % (cfg_hms, n_cfg, n_cfg2, cfg2_hms),
        "    %d s (%s) after E189's session end" % (rest["step7_after_e189_end_s"], mmss(rest["step7_after_e189_end_s"])),
        "    its commands by the kit's audit (%s, lines %s): %d, %s" % (os.path.relpath(AUDIT, TOP), ", ".join(str(n) for n in cfg_lines),
                                                                  len(cfg_cmds), "; ".join("%s %s" % c_ for c_ in cfg_cmds)),
        "  the session's first card command (the probe): T0 %d = %s (session/first-card-command.txt; session/session.log line %d: %s PST, the cap at %s PST, %d s)" % (
            t0, rest["first_card_command"], n_fcc, fcc_hms, cap_hms, cap_s),
        "    %d s (%s) after E189's session end; %d s (%s) after step 7's read" % (
            rest["first_card_command_after_e189_end_s"], mmss(rest["first_card_command_after_e189_end_s"]),
            rest["first_card_command_after_step7_s"], mmss(rest["first_card_command_after_step7_s"])),
        "  as run (the rest to the session's first card command): met, %d s past the 40 minutes" % rest["rest_met_by_s_as_run"],
        "  if step 7's read counted as E192's first card command: %d s (%s) short of the 40 minutes" % (
            rest["rest_short_by_s_if_step7_counted"], mmss(rest["rest_short_by_s_if_step7_counted"])),
        "  E192's session end: %s PST (session/session.log line %d); card time %d s by line %d (%d s by the clock), cap %d s" % (
            e192_end, n_end, card_s, n_ct, rest["card_time_s_check"], cap_s),
        "  from step 7's read to the session's end: %d s (no registered rule counts this span)" % rest["span_step7_to_session_end_s_no_registered_quantity"],
        "  the die at the session's first sample (%s): %s C; the session's lowest: %s C" % (rest["die_first_sample_at"], first_die, die_min),
        "  the next session of ours on the card rests until %s" % rest["next_rest_opens"]]
for doc, d in cite.items():
    path = {"E192.md": E192MD, "KIT.md": KITMD, "README.md": README}[doc]
    rel = os.path.relpath(path, TOP) if doc != "README.md" else "README.md"
    txt.append("  %s:" % rel)
    for k, n in d.items():
        txt.append("    line %d: %s" % (n, k))

# ---------------------------------------------------------------- 2. the launch output
box, box_line = [], {}
for i, ln in enumerate(open(os.path.join(DATA, "box-manifest.txt"), encoding="utf-8"), 1):
    p = ln.split()
    if len(p) == 3 and p[0] == "SUM":
        box.append((p[1], p[2]))
        box_line[p[2]] = i
sd = "build/e192/T%d/" % t0
br = "build/claims-v3/aifoundry3/e192/"
here_sha = {p: h for h, p in ent}
kept, notkept = [], []
for h, p in box:
    if p.startswith(sd + "run/"):
        dp = "run/" + p[len(sd + "run/"):]
    elif p.startswith(sd):
        dp = "session/" + p[len(sd):]
    elif p.startswith(br):
        dp = "build/" + p[len(br):]
    else:
        dp = None
    if dp is None:
        same = sorted(q for q, hq in here_sha.items() if hq == h)
        same_box = sorted("%s (line %d)" % (q, box_line[q]) for hq, q in box if hq == h and q != p)
        notkept.append({"box_path": p, "box_manifest_line": box_line[p], "sha256": h, "same_bytes_as": same,
                        "same_sha256_in_box_manifest": same_box})
        continue
    if dp == "run/telemetry.jsonl":
        with gzip.open(os.path.join(DATA, "run", "telemetry.jsonl.gz"), "rb") as f:
            ok = sha_bytes(f.read()) == h
        dp = "run/telemetry.jsonl.gz (uncompressed)"
    else:
        ok = os.path.isfile(os.path.join(DATA, dp)) and sha(os.path.join(DATA, dp)) == h
    kept.append({"box_path": p, "here": dp, "same_sha256": ok})
slog_b = open(SLOG, "rb").read()
res["launch_output"] = {"box_files": len(box), "kept_as_files_at_the_box_sha256": sum(1 for k in kept if k["same_sha256"]),
                        "kept_but_different": [k for k in kept if not k["same_sha256"]], "not_kept_as_a_file": notkept,
                        "session_log_bytes": len(slog_b), "session_log_lines": slog_b.count(b"\n"),
                        "lines": {
                            "session_e192.sh say() tees each line to the log and stdout": one(os.path.join(TOP, E192, "session_e192.sh"), r'^say\(\) \{.*\| tee -a "\$LOG"', "say"),
                            "rb/s11_a3_session_e192.sh: stdout and stderr to build/e192/launch-T<T0>.out": lines_matching(os.path.join(TOP, E192, "rb", "s11_a3_session_e192.sh"), r'> "build/e192/launch-T\$T0\.out" 2>&1'),
                            "collect_e192.py assemble: the session directory": first_after(os.path.join(TOP, E192, "collect_e192.py"), r'^def assemble\(', r'sd = os\.path\.join\(raw, "build/e192/T%s" % t0\)'),
                            "collect_e192.py assemble: the build record": first_after(os.path.join(TOP, E192, "collect_e192.py"), r'^def assemble\(', r'br = os\.path\.join\(raw, "build/claims-v3/aifoundry3/e192"\)'),
                            "collect_e192.py assemble: box-manifest.txt": lines_matching(os.path.join(TOP, E192, "collect_e192.py"), r'"box-manifest\.txt"\), os\.path\.join\(out, "box-manifest\.txt"\)'),
                        }}
txt += ["", "2. the launch output",
        "  box-manifest.txt: %d box files; %d here as files at the box's sha256 (the telemetry through its gzip); %d here but different" % (
            len(box), res["launch_output"]["kept_as_files_at_the_box_sha256"], len(res["launch_output"]["kept_but_different"]))]
for k in notkept:
    txt.append("  not a file here: %s (box-manifest.txt line %d), sha256 %s; the same sha256 in the box's manifest: %s; here: %s (%d bytes, %d lines)" % (
        k["box_path"], k["box_manifest_line"], k["sha256"], ", ".join(k["same_sha256_in_box_manifest"]) or "none",
        ", ".join(k["same_bytes_as"]) or "none", len(slog_b), slog_b.count(b"\n")))
for k, v in res["launch_output"]["lines"].items():
    txt.append("    %s: line %s" % (k, v))

# ---------------------------------------------------------------- 3. the sizes behind checks 2 and 3
SRC = os.path.join(TOP, E192, "proposal", "src")
runs = [json.loads(ln) for ln in open(os.path.join(DATA, "run", "runs.jsonl"), encoding="utf-8") if ln.strip()]
raw = [r for r in runs if r.get("pass", -1) >= 0]
smoke = [r for r in runs if r.get("pass", -1) < 0]
groups = {}
for r in raw:
    groups.setdefault((r["pass"], r["seq"]), []).append(r)
meas = [r for r in raw if r["pass"] in MEASURED and r.get("role") != "burnin"]
NB = 128    # neighbourhoods: 32 shires x 4; the host counts each neighbourhood's counters once (main.cpp)


def arm_means(pop, key):
    b = {}
    for r in pop:
        b.setdefault(r["arm"], []).append(r[key])
    return {a: statistics.mean(v) for a, v in b.items()}


l1 = [r["l1d_miss"] for r in raw]
l1_all = arm_means(raw, "l1d_miss")
l1_meas = arm_means(meas, "l1d_miss")
it = [r["iters"] for r in raw]
ic_meas = arm_means(meas, "icache_miss")
xor_arms = sorted(a for a, v in ic_meas.items() if v < 4600)
oth = {a: v for a, v in ic_meas.items() if a not in xor_arms}
ic_oth = [r["icache_miss"] for r in meas if r["arm"] not in xor_arms]
ic_xor = [r["icache_miss"] for r in meas if r["arm"] in xor_arms]
per = {}
for (p, s), rs in sorted(groups.items()):
    if p not in MEASURED or rs[0].get("role") == "burnin":
        continue
    per.setdefault(rs[0]["arm"], []).append(sum(r["icache_miss"] for r in rs) / sum(r["iters"] for r in rs))
per_mean = {a: statistics.mean(v) for a, v in per.items()}
lo_a = min(per_mean, key=lambda a: (per_mean[a], a))
hi_a = max(per_mean, key=lambda a: (per_mean[a], a))
res["check_sizes"] = {
    "launches_passes_0_8": len(raw), "smoke_launches": len(smoke), "runs_passes_0_8": len(groups),
    "measured_launches_no_burnin": len(meas),
    "l1d": {"launches_reading_0": sum(1 for x in l1 if x == 0),
            "runs_whose_launches_all_read_0": sum(1 for rs in groups.values() if all(r["l1d_miss"] == 0 for r in rs)),
            "a_launch_min": min(l1), "a_launch_max": max(l1), "a_launch_mean": g(statistics.mean(l1)),
            "arm_means_passes_0_8": [g(min(l1_all.values())), g(max(l1_all.values()))],
            "arm_means_measured_passes": [g(min(l1_meas.values())), g(max(l1_meas.values()))],
            "a_neighbourhood_a_launch_mean": g(statistics.mean(l1) / NB),
            "per_iteration": g(sum(l1) / sum(it))},
    "iterations_a_launch_summed_over_harts": [min(it), max(it)],
    "icache_measured": {"arm_means_30": [g(min(oth.values())), g(max(oth.values()))], "arms_other": len(oth),
                        "low_arms": {a: g(ic_meas[a]) for a in xor_arms},
                        "a_launch_other_arms": [min(ic_oth), max(ic_oth)],
                        "a_launch_other_arms_below_4600": sum(1 for x in ic_oth if x < 4600), "a_launch_other_arms_n": len(ic_oth),
                        "a_launch_low_arms": [min(ic_xor), max(ic_xor)],
                        "a_neighbourhood_a_launch_mean": g(statistics.mean([r["icache_miss"] for r in meas]) / NB),
                        "per_iteration": g(sum(r["icache_miss"] for r in meas) / sum(r["iters"] for r in meas))},
    "check3_quantity": {"min": g(per_mean[lo_a]), "min_arm": lo_a, "max": g(per_mean[hi_a]), "max_arm": hi_a,
                        "spread": g(per_mean[hi_a] - per_mean[lo_a]),
                        "spread_over_min": g((per_mean[hi_a] - per_mean[lo_a]) / per_mean[lo_a])},
    "lines": {
        "main.cpp: the counters are neighbourhood sums, each neighbourhood counted once": one(os.path.join(SRC, "host", "main.cpp"), r"The minion counters are neighbourhood sums", "nb sums"),
        "main.cpp: iters summed over the participants": one(os.path.join(SRC, "host", "main.cpp"), r"^\s+iters \+= r\.iters;", "iters sum"),
        "intbits_args.h: icm before and after the loop": one(os.path.join(SRC, "intbits_args.h"), r"uint64_t icm0, icm1;", "icm"),
        "intbits_args.h: l1m before and after the loop": one(os.path.join(SRC, "intbits_args.h"), r"uint64_t l1m0, l1m1;", "l1m"),
        "check_e192.py: check 3, no threshold registered": one(os.path.join(TOP, E192, "check_e192.py"), r"no threshold is registered, so$", "c3 a"),
        "check_e192.py: check 3, EQUAL means identical": one(os.path.join(TOP, E192, "check_e192.py"), r"^\s+EQUAL means identical, and anything else", "c3 b"),
    },
    "windows_cycles": sorted({r["window"] for r in runs}),
}
c = res["check_sizes"]
txt += ["", "3. the sizes behind registered checks 2 and 3 (post hoc; the verdicts are the kit's checker's)",
        "  run/runs.jsonl: %d launches in passes 0-8 (%d runs), and the smoke's %d; measured passes 1-8 without the burn-ins: %d launches" % (
            len(raw), len(groups), len(smoke), len(meas)),
        "  L1 data misses (check 2: 0 on every run): launches reading 0: %d of %d; runs whose launches all read 0: %d of %d" % (
            c["l1d"]["launches_reading_0"], len(raw), c["l1d"]["runs_whose_launches_all_read_0"], len(groups)),
        "    a launch: %d to %d (mean %s; %s a neighbourhood of %d); the %d arms' means: %s to %s (passes 0-8), %s to %s (measured passes)" % (
            c["l1d"]["a_launch_min"], c["l1d"]["a_launch_max"], c["l1d"]["a_launch_mean"], c["l1d"]["a_neighbourhood_a_launch_mean"], NB,
            len(l1_all), c["l1d"]["arm_means_passes_0_8"][0], c["l1d"]["arm_means_passes_0_8"][1],
            c["l1d"]["arm_means_measured_passes"][0], c["l1d"]["arm_means_measured_passes"][1]),
        "    per iteration (summed misses over summed iterations, passes 0-8): %s" % c["l1d"]["per_iteration"],
        "  iterations a launch, summed over the 1,024 participants: %d to %d; the window of every launch (cycles): %s" % (
            min(it), max(it), ", ".join(str(w) for w in sorted({r["window"] for r in runs}))),
        "  instruction-cache misses (check 3: per iteration equal across arms), measured passes without the burn-ins:",
        "    the arms' means a launch: %s to %s in %d arms; %s" % (
            c["icache_measured"]["arm_means_30"][0], c["icache_measured"]["arm_means_30"][1], len(oth),
            ", ".join("%s %s" % (a, v) for a, v in c["icache_measured"]["low_arms"].items())),
        "    single launches: %d to %d in those %d arms (%d of %d below 4,600); %d to %d in %s" % (
            min(ic_oth), max(ic_oth), len(oth), c["icache_measured"]["a_launch_other_arms_below_4600"], len(ic_oth),
            min(ic_xor), max(ic_xor), " and ".join(xor_arms)),
        "    %s a neighbourhood a launch; per iteration, all those launches: %s" % (
            c["icache_measured"]["a_neighbourhood_a_launch_mean"], c["icache_measured"]["per_iteration"]),
        "    check 3's quantity (each arm's mean over its runs of misses / iterations): %s (%s) to %s (%s); spread %s, %s of the lowest" % (
            c["check3_quantity"]["min"], lo_a, c["check3_quantity"]["max"], hi_a, c["check3_quantity"]["spread"],
            c["check3_quantity"]["spread_over_min"])]
for k, v in c["lines"].items():
    txt.append("    %s: line %d" % (k, v))

os.makedirs(OUT, exist_ok=True)
with open(os.path.join(OUT, "posthoc-note1-e192.json"), "w", encoding="utf-8") as f:
    json.dump(res, f, indent=1, sort_keys=True)
    f.write("\n")
with open(os.path.join(OUT, "posthoc-note1-e192.txt"), "w", encoding="utf-8") as f:
    f.write("\n".join(txt) + "\n")
print("\n".join(txt))
