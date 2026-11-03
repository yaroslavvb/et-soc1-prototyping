#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
"""E144, corrections after verification (Tue 3 Nov 2026): print every number the README's corrections C1-C6 quote, read from
committed files only: this directory, the registration tools/claims-v3/e144/, tools/claims-v3/lib.sh, E128's guard,
tools/ettelem/ettelem.cpp (at HEAD and, through git, at de262730, the source aifoundry3's binary was built from), Q136(w)'s
tools/claims-v3/dmcmd_table.json, Q138(t)'s directory, E97's e97.json and E89's ident/probe2.out. With --et-platform <clone> it also
prints the PVT functions' line numbers in et-platform 836a4ab (BL2 0.22.0), through git. Desk only: it reads, and writes nothing but
stdout.

    python3 docs/reports/data/2026-11-02-e144-heat-minutes/corrections-numbers.py [--et-platform <et-platform clone>] \
        > docs/reports/data/2026-11-02-e144-heat-minutes/corrections-numbers.txt
"""
import datetime
import gzip
import json
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
DD = os.path.join(ROOT, "docs", "reports", "data")
REG = os.path.join(ROOT, "tools", "claims-v3", "e144")
Q138T = os.path.join(DD, "2026-11-02-q138t-heat-model")
E97 = os.path.join(DD, "2026-11-01-e97-heat-low-power-steady")
E89 = os.path.join(DD, "2026-10-31-e89-heat-low-power")
PASS = os.path.join(HERE, "aifoundry3", "e144", "p14420")
SMOKE = os.path.join(HERE, "aifoundry3", "e144-smoke", "p14401")
PST = datetime.timezone(datetime.timedelta(hours=-8), "PST")


def load(p):
    with open(p) as f:
        return json.load(f)


def rel(p):
    return os.path.relpath(p, ROOT)


def lines(p):
    with open(p, errors="replace") as f:
        return f.read().split("\n")


def show(p, nums):
    """print the given 1-based line numbers of a file, as 'path:line: text'"""
    ls = lines(p)
    for n in nums:
        print(f"  {rel(p)}:{n}: {ls[n - 1].strip()[:160]}")


def git(*args):
    return subprocess.run(["git", "-C", ROOT, *args], capture_output=True, text=True, check=True).stdout


def pst(ms):
    return datetime.datetime.fromtimestamp(ms / 1000.0, PST).strftime("%H:%M:%S")


def rows(path):
    op = gzip.open if path.endswith(".gz") else open
    with op(path, "rt", errors="replace") as f:
        for line in f:
            line = line.strip()
            if line.startswith("{"):
                try:
                    yield json.loads(line)
                except ValueError:
                    pass


def c_function(src, name):
    """the text of a C/C++ function definition starting at 'name(' up to its matching closing brace"""
    i = src.find(name + "(")
    if i < 0:
        return None
    j = src.find("{", i)
    depth = 0
    for k in range(j, len(src)):
        depth += {"{": 1, "}": -1}.get(src[k], 0)
        if depth == 0:
            return src[i:k + 1]
    return None


et_platform = None
if "--et-platform" in sys.argv:
    et_platform = sys.argv[sys.argv.index("--et-platform") + 1]

print("E144 corrections after verification: the numbers C1-C6 quote, from committed files")
print()

# ---------------------------------------------------------------- C1
print("[C1] lib.sh's die_c: the `ettelem sample` calls the first device-command list left out")
show(os.path.join(ROOT, "tools", "claims-v3", "lib.sh"), [103, 188, 196])
show(os.path.join(REG, "block_e144.sh"), [15, 16])
show(os.path.join(ROOT, "tools", "claims-v3", "e128", "ettelem_guard.sh"), [19, 31])
print("  sends per sample, tools/ettelem/ettelem.cpp at HEAD:")
show(os.path.join(ROOT, "tools", "ettelem", "ettelem.cpp"), [149, 165, 166, 167, 172])
head_src = open(os.path.join(ROOT, "tools", "ettelem", "ettelem.cpp")).read()
de_src = git("show", "de262730:tools/ettelem/ettelem.cpp")
print("  sample() at de262730 (the source of aifoundry3's binary) identical to HEAD's:",
      c_function(head_src, "int sample") == c_function(de_src, "int sample"))
for line in lines(os.path.join(HERE, "logs", "sha256-setup.txt")):
    if line.endswith("build/ettelem/ettelem"):
        print("  the box's ettelem binary (logs/sha256-setup.txt):", line.split()[0][:16] + "...")
for name, d in (("smoke 14401", SMOKE), ("pass 14420", PASS)):
    b = load(os.path.join(d, "block.json"))
    print(f"  {name} block.json: block {pst(b['t0_ms'])}-{pst(b['t1_ms'])} PST, die_c_start {b['die_c_start']}, "
          f"die_c_end {b['die_c_end']} (non-null: the sample ran)")
audit = lines(os.path.join(REG, "dmcmd-audit.txt"))
die_c_lines = [(i + 1, t) for i, t in enumerate(audit) if t.startswith("tools/claims-v3/lib.sh:103:")]
print(f"  tools/claims-v3/e144/dmcmd-audit.txt lines {die_c_lines[0][0]}-{die_c_lines[-1][0]}: lib.sh:103's sends, "
      f"{len(die_c_lines)}: " + "; ".join(re.sub(r".*ettelem sample: (\S+) \[(.*?)\].*", r"\1 [\2]", t) for _, t in die_c_lines))
print("  ", audit[0])
table = load(os.path.join(ROOT, "tools", "claims-v3", "dmcmd_table.json"))["commands"]
mv = table["GET_MODULE_VOLTAGE"]
print(f"  dmcmd_table.json GET_MODULE_VOLTAGE: id {mv['id']}, class {mv['class']}, pmic {mv['pmic']}, "
      f"pmic_reads {mv['pmic_reads']}; handler {mv['handler']}")
av = table["GET_ASIC_VOLTAGE"]
print(f"  dmcmd_table.json GET_ASIC_VOLTAGE: id {av['id']}, class {av['class']}, pmic {av['pmic']}, pmic_reads {av.get('pmic_reads')}")
# the kinds sent: the three send sites that ran (the sampler, die_c through the guard, config through the guard)
ran = ("tools/claims-v3/e89/pvt_sample.py:", "tools/claims-v3/lib.sh:103:", "tools/claims-v3/e128/ettelem_guard.sh:18:",
       "tools/claims-v3/e128/ettelem_guard.sh:31:")
kinds = {}
for t in audit:
    if t.startswith(ran):
        m = re.search(r": (GET_[A-Z_]+) \[(READ|WRITE), pmic (\w+)\]", t)
        if m:
            kinds[m.group(1)] = (m.group(2), m.group(3))
print(f"  kinds sent (the sites that ran: the sampler, die_c's sample and config through the guard): {len(kinds)}")
for k in sorted(kinds):
    print(f"    {k}: {kinds[k][0]}, pmic {kinds[k][1]}")
print("  of them with PMIC reads:", sorted(k for k, v in kinds.items() if v[1] == "read"))
print()

# ---------------------------------------------------------------- C2
print("[C2] Q138(t)'s corrections C1 and C2, which withdrew the registration's two 'before' framings")
q = lines(os.path.join(Q138T, "README.md"))
for i, t in enumerate(q):
    if t.startswith("- **C1 (major)") or t.startswith("- **C2 (major)") or "No model made that rule" in t \
            or "is withdrawn" in t or t.startswith("| **aifoundry3: the die through"):
        print(f"  {rel(os.path.join(Q138T, 'README.md'))}:{i + 1}: {t.strip()[:230]}")
for i, t in enumerate(q):
    if t.startswith("intercept. Training data"):
        print(f"  {rel(os.path.join(Q138T, 'README.md'))}:{i + 1}: {t.strip()[:160]}")
print()

# ---------------------------------------------------------------- C3
print("[C3] one blind session: the errors as scored (no interval on (a) or (b)), the rest dies, E97's within-session moves")
sc = load(os.path.join(HERE, "scored.json"))
for h in sc["holds"]:
    a, b = h["a"], h["b"]
    print(f"  {h['hold']} ({h['item']}): share {h['share_recorded']:.4f}, period {h['launch_period_s']:.2f} s, rest die {h['rest_die_C']:.3f} C; "
          f"(a) rms {a['rms_C']:.3f}, plateau {a['plateau_err_C']:+.3f}, at 60/120/300/600 s "
          + "/".join(f"{a['err_at_s'][k]:+.3f}" for k in ("60", "120", "300", "600"))
          + f"; (b) plateau {b['plateau_err_C']:+.3f}, worst checkpoint {b['max_abs_checkpoint_err_C']:.3f}; "
          f"interval keys in (a): {[k for k in a if 'interval' in k or k.startswith('ci')]}, in (b): {[k for k in b if 'interval' in k or k.startswith('ci')]}")
rl = lines(os.path.join(PASS, "run.log"))
print("  " + rel(os.path.join(PASS, "run.log")) + ":5: " + rl[4].strip())
for i, t in enumerate(q):
    if t.startswith("- **The plateau moved 0.3"):
        print(f"  {rel(os.path.join(Q138T, 'README.md'))}:{i + 1}: {t.strip()[:200]}")
print()

# ---------------------------------------------------------------- C4
print("[C4] item 8's like for like: E97's H3 (fp32 randn, duty-cycled) against E144's H_H")
e97 = load(os.path.join(E97, "e97.json"))["holds"]["holds"]["H3"]
st = e97["steady"]
hh = [h for h in sc["holds"] if h["hold"] == "H_H"][0]
c = hh["c_per_board_W"]
print(f"  E97 H3: R_ol {st['R_ol']:.4f} [{st['R_ol_lo']:.3f}, {st['R_ol_hi']:.3f}] C per board W, compute share {st['compute_share']:.4f}, "
      f"die {st['T_mean']:.2f} C, rise {st['dT']:.2f} C, idle before {e97['idle']['before']['T']:.3f} C ({e97['idle']['before']['rest']})")
print(f"  E144 H_H: {c['per_board_W']:.4f} [{c['interval'][0]:.3f}, {c['interval'][1]:.3f}] C per board W, share {hh['share_recorded']:.4f}, "
      f"rest die {hh['rest_die_C']:.3f} C, plateau die {hh['rest_die_C'] + hh['b']['measured']['plateau_rise_C']:.2f} C")
print(f"  ratio E144 H_H / E97 H3: {c['per_board_W'] / st['R_ol']:.4f} ({100 * (c['per_board_W'] / st['R_ol'] - 1):+.2f}%; "
      f"against E97's table value 0.877: {100 * (c['per_board_W'] / 0.877 - 1):+.2f}%); "
      f"rest dies differ by {hh['rest_die_C'] - e97['idle']['before']['T']:+.2f} C")
print()

# ---------------------------------------------------------------- C5
print("[C5] command 74 group 0: raw codes on group 0, and the latches across 31 Oct - 2 Nov")
pr = [r for r in rows(os.path.join(HERE, "logs", "probe.out")) if "pvt" in r]
codes = [x for r in pr for x in (r.get("pvt") or {}).get("c", [])]
print(f"  logs/probe.out: {len(pr)} ticks, status {[ (r.get('pvt') or {}).get('st') for r in pr]}, codes {min(codes)}-{max(codes)} "
      f"at a firmware minshire reading of {pr[0]['temp_c']['minshire'][0]} C")
ref = None
for r in rows(os.path.join(E89, "ident", "probe2.out")):
    p = r.get("pvt") or {}
    if "hi" in p:
        ref = p["hi"]
        print(f"  E89 ident/probe2.out: one hi/lo tick at {datetime.datetime.fromtimestamp(r['t_ms'] / 1000.0, datetime.timezone(datetime.timedelta(hours=-7), 'PDT')).strftime('%a %d %b %H:%M:%S PDT')}, "
              f"{len(ref)} high latches, max {max(ref)} codes")
        break
for name, d in (("smoke 14401", SMOKE), ("pass 14420", PASS)):
    n = same = lo_up = hi_up = 0
    prev = None
    nlines = 0
    for r in rows(os.path.join(d, "telemetry.jsonl.gz")):
        nlines += 1
        p = r.get("pvt") or {}
        if "hi" not in p or "lo" not in p:
            continue
        n += 1
        same += p["hi"] == ref
        if prev:
            hi_up += sum(b > a for a, b in zip(prev[0], p["hi"]))
            lo_up += sum(b > a for a, b in zip(prev[1], p["lo"]))
        prev = (p["hi"], p["lo"])
    print(f"  {name}: {nlines} samples, {n} with hi/lo, high latches equal to E89's in {n}: {same == n} ({same}), "
          f"latch rises between ticks: high {hi_up}, low {lo_up}")
for i, t in enumerate(lines(os.path.join(E97, "README.md"))):
    if "150,295" in t and "high latch" in t:
        print(f"  {rel(os.path.join(E97, 'README.md'))}:{i + 1}: ...{t[t.find('All 150,295'):t.find('as in E89') + 9]}")
for i, t in enumerate(lines(os.path.join(E89, "README.md"))):
    if "22,976 samples)" in t:
        print(f"  {rel(os.path.join(E89, 'README.md'))}:{i + 1}: ...{t[t.find('command 74 answered'):t.find('samples)') + 8]}")
tel = load(os.path.join(HERE, "e144.json"))["pass"].get("telemetry", {})
print("  e144.json pass.telemetry:", {k: v for k, v in tel.items() if not isinstance(v, (dict, list))})
if et_platform:
    pc = subprocess.run(["git", "-C", et_platform, "show",
                         "836a4ab:device-bootloaders/src/ServiceProcessorBL2/driver/pvt_controller.c"],
                        capture_output=True, text=True, check=True).stdout.split("\n")

    def span(sig):
        s = next(i for i, t in enumerate(pc) if t.startswith(sig))
        e = next(i for i in range(s, len(pc)) if pc[i].startswith("}"))
        return s + 1, e + 1
    for sig in ("static int pvt_get_ts_data(", "int pvt_get_min_shire_ts_sample(", "int pvt_get_ioshire_ts_sample(", "int pvt_hilo_reset("):
        print(f"  et-platform 836a4ab driver/pvt_controller.c: {sig.split('(')[0].split()[-1]} at lines {'-'.join(map(str, span(sig)))}")
else:
    print("  (run with --et-platform <clone> for the PVT functions' line numbers at et-platform 836a4ab)")
print()

# ---------------------------------------------------------------- C6
print("[C6] times and text")
for sha in ("13799873", "8d396e2c", "ca979517", "5718a11e"):
    print("  commit", git("show", "-s", "--format=%h %ad %s", "--date=format:%a %d %b %H:%M:%S", sha).strip()[:120])
print("  " + rel(os.path.join(PASS, "run.log")) + ":1: " + rl[0].strip())
sl = lines(os.path.join(HERE, "logs", "smoke.log"))
print("  logs/smoke.log: " + " | ".join(t.strip().split(" -> ")[0] for t in sl[:5] if "R0 ends" in t or "begins" in t))
ql = lines(os.path.join(HERE, "logs", "queue.log"))
print("  logs/queue.log:1: " + ql[0].strip())
pe = load(os.path.join(Q138T, "predictions-e144.json"))["aifoundry3"]
print(f"  predictions-e144.json: full design {pe['session_minutes']} card-minutes, subset {pe['subset']['session_minutes']}")
for i, t in enumerate(q):
    if "if the gates leave under 80 card-minutes" in t:
        print(f"  {rel(os.path.join(Q138T, 'README.md'))}:{i + 1}: {t.strip()[:120]}")
claim = datetime.datetime(2026, 11, 2, 22, 36, 26, tzinfo=PST)
gate = datetime.datetime(2026, 11, 2, 23, 50, 0, tzinfo=PST)
print(f"  from the claim (22:36:26) to the 23:50 end gate: {(gate - claim).total_seconds() / 60:.1f} min")
for h in pe["subset"]["holds"]:
    if h["hold"] == "H_L":
        print(f"  N1's figures, predictions-e144.json aifoundry3.subset: H_L plateau_per_board_W {h['plateau_per_board_W']}, carried_in_C {h['carried_in_C']}")
    if h["hold"] == "H_H":
        hh_pb = h["plateau_per_board_W"]
print(f"  N1's linearity: {hh_pb} / {[h for h in pe['subset']['holds'] if h['hold'] == 'H_L'][0]['plateau_per_board_W']} = "
      f"{hh_pb / [h for h in pe['subset']['holds'] if h['hold'] == 'H_L'][0]['plateau_per_board_W']:.4f}")
rg = git("show", "8d396e2c:tools/claims-v3/e144/README.md").split("\n")   # the registration with N1, before the dated notes of 3 Nov
for i, t in enumerate(rg):
    if "until ~23:50 PST" in t or t.startswith("*Written Mon 2 Nov 2026") or "under 60 card-minutes" in t \
            or t.startswith("**Note N1, a reading"):
        print(f"  tools/claims-v3/e144/README.md at 8d396e2c, line {i + 1}: {t.strip()[:150]}")
pin = [t for t in lines(os.path.join(PASS, "code.sha256")) if t.endswith("tools/claims-v3/e144/README.md")][0].split()[0]
reg_at = git("show", "13799873:tools/claims-v3/e144/README.md")
import hashlib
print(f"  pass 14420 code.sha256 pins tools/claims-v3/e144/README.md at {pin[:16]}...; the registration commit's text hashes "
      f"{hashlib.sha256(reg_at.encode()).hexdigest()[:16]}... (equal: {hashlib.sha256(reg_at.encode()).hexdigest() == pin})")
others = [t for f in (os.path.join(PASS, "run.log"), os.path.join(HERE, "logs", "smoke.log"), os.path.join(HERE, "logs", "queue.log"))
          for t in lines(f) if "others present" in t or "another user" in t]
print(f"  'others present' / 'another user' lines in run.log, smoke.log, queue.log: {len(others)}")
