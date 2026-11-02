#!/usr/bin/env python3
"""E126, corrections after verification (Mon 2 Nov 2026): print, from committed files, every number that the README's
"Corrections after verification" section quotes and that no earlier file prints.

    python3 docs/reports/data/2026-11-02-e126-gemm-arms/corrections-check.py [--et-platform <clone>] > corrections-check.txt

Post hoc; it decides nothing and changes no file. Standard library only; it runs from any directory. C6's source
comparison also asks git, in a clone of the public et-platform repository (default: external/et-platform in this
repository's top directory, where the lab keeps one); without a clone or git it says so and prints the rest.
"""
import glob
import gzip
import json
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
E119 = os.path.join(REPO, "docs", "reports", "data", "2026-11-01-e119-gemm-speed")
RES = json.load(open(os.path.join(HERE, "results.json")))
R119 = json.load(open(os.path.join(E119, "results.json")))
PH = json.load(open(os.path.join(HERE, "posthoc.json")))
ARMS = ("c8s", "c16r4", "c16r8", "c16r2")
TYPES = ("fp32", "fp16", "int8")


def rel(p):
    return os.path.relpath(p, REPO)


def tel_lines(session_dir):
    """every sampler line of a session, in time order, with its run's name"""
    rows = []
    for p in glob.glob(os.path.join(session_dir, "tel", "*.jsonl.gz")):
        with gzip.open(p, "rt") as f:
            for x in f:
                if x.startswith("{"):
                    j = json.loads(x)
                    j["_run"] = os.path.basename(p)[: -len(".jsonl.gz")]
                    rows.append(j)
    rows.sort(key=lambda j: j["t_ms"])
    return rows


def c1():
    print("C1  The replicate's faster random clocks: the room by proxy, and the heat history (posthoc.json, results.json)")
    room = PH["room"]
    i19, i26 = room["E119"]["card_idle_10min_before"], room["E126"]["card_idle_10min_before"]
    print(f"  card idle, 10 min before each session (medians): E119 {i19['die_median_c']} C / {i19['board_median_w']} W; "
          f"E126 {i26['die_median_c']} C / {i26['board_median_w']} W; difference {i26['die_median_c'] - i19['die_median_c']:+d} C, "
          f"{i26['board_median_w'] - i19['board_median_w']:+.2f} W. No inlet thermometer was read: these are proxies for the room.")
    print("  idle die to held die, C per W = (sus_die - idle die) / (sus_w - idle W), fp32 random sustained (results.json cells):")
    slope = {}
    for nm, res, idle in (("E119", R119, i19), ("E126", RES, i26)):
        for a in ARMS:
            c = res["cells"][f"{a}-fp32-randn"]
            slope[(nm, a)] = (c["sus_die"] - idle["die_median_c"]) / (c["sus_w"] - idle["board_median_w"])
        print(f"    {nm}: " + ", ".join(f"{a} {slope[(nm, a)]:.3f}" for a in ARMS))
    s19 = [slope[("E119", a)] for a in ARMS]
    d = i19["die_median_c"] - i26["die_median_c"]
    print(f"  {d} C at E119's {min(s19):.3f}-{max(s19):.3f} C/W is {d / max(s19):.1f}-{d / min(s19):.1f} W more at the same trip (the room proxy's share)")
    hh = PH["heat_history_dated_note_2026_11_02"]
    for nm in ("E119", "E126"):
        print(f"  {nm}: block B began after {hh[nm]['runs_before_block_B']} runs, {hh[nm]['block_B_start_min']} min into the session")
    print("  per arm, E126 - E119: start die (the reducer's die_start; the gate's reading), t65 (s to the first die mean >= 65 C), "
          "sustained W and MHz; and where each session's 40 s window began against t65:")
    for a in ARMS:
        x, v19, v26 = hh["E126_minus_E119"][a], hh["E119"]["random_sustained"][a], hh["E126"]["random_sustained"][a]
        print(f"    {a:6s} start {x['die_start_c']:+.0f} C ({x['gate_die_c']:+.0f} C gate); t65 {x['t65_s']:+.1f} s; {x['sus_w']:+.2f} W, "
              f"{x['sus_mhz']:+.1f} MHz; window {v19['window_start_minus_t65_s']:+.1f} s (E119) and {v26['window_start_minus_t65_s']:+.1f} s "
              f"(E126) after t65; limit {v19['limit']} -> {v26['limit']}, die {v19['sus_die_c']} -> {v26['sus_die_c']} C")
    ex = [hh["E126_minus_E119"][a]["sus_w"] for a in ARMS if a != "c8s"]
    print(f"  the three c16 arms: +{min(ex):.2f} to +{max(ex):.2f} W; c8s +{hh['E126_minus_E119']['c8s']['sus_w']:.2f} W")
    s26 = [slope[("E126", a)] for a in ARMS if a != "c8s"]
    print(f"  E126's three c16 arms' C per W: {min(s26):.3f}-{max(s26):.3f}; c8s {slope[('E126', 'c8s')]:.3f}")
    print()


def fit(res, key):
    f = (res["per_arm"].get(key) or {}).get("fit") or {}
    return f.get("C"), f.get("C_ci"), f.get("M"), f.get("M_ci")


def c2():
    print("C2  What sharing C took away: c16s (this session) against the cold walk c16 (E119's session), fit T = C/f + M (results.json per_arm)")
    for t in TYPES:
        C1, C1ci, M1, M1ci = fit(RES, f"c16s.{t}")
        C0, C0ci, M0, M0ci = fit(R119, f"c16.{t}")
        dC, dM = C0 - C1, M0 - M1
        for mhz in (600, 800):
            cyc = dC / mhz
            tot = cyc + dM
            print(f"  {t} at {mhz} MHz: c16 C {C0} +- {C0ci}, M {M0} +- {M0ci}; c16s C {C1} +- {C1ci}, M {M1} +- {M1ci}; "
                  f"{dC:.2f} cycles = {cyc:.4f} us, wait {dM:.4f} us, saved {tot:.4f} us: cycles {cyc / tot:.1%}, wait {dM / tot:.1%}")
    for k, nm in (("T600", 600), ("T800", 800)):
        a, b = R119["per_arm"]["c16.fp32"][k], RES["per_arm"]["c16s.fp32"][k]
        print(f"  check, fp32 launch means at {nm} MHz: c16 {a:.4f} - c16s {b:.4f} = {a - b:.4f} us")
    for t in TYPES:
        C, _, M, _ = fit(RES, f"c16s.{t}")
        C0, _, M0, _ = fit(R119, f"c16.{t}")
        print(f"  {t} share of T at 800 MHz that is wait: c16s {M / (C / 800 + M):.1%}, c16 {M0 / (C0 / 800 + M0):.1%}")
    print()


def c3():
    print("C3  c4s's split against c8s's (results.json per_arm; intervals: 95% regression over launches within one session)")
    for t in TYPES:
        a = fit(RES, f"c4s.{t}")
        for nm, res in (("E126", RES), ("E119", R119)):
            b = fit(res, f"c8s.{t}")
            if b[0] is None:
                print(f"  {t}: c8s in {nm}: not run")
                continue
            sep_c = (a[0] - a[1]) > (b[0] + b[1]) or (b[0] - b[1]) > (a[0] + a[1])
            sep_m = (a[2] - a[3]) > (b[2] + b[3]) or (b[2] - b[3]) > (a[2] + a[3])
            xa, xb = RES["per_arm"][f"c4s.{t}"]["X"], res["per_arm"][f"c8s.{t}"]["X"]
            print(f"  {t}: c4s C {a[0]} +- {a[1]}, M {a[2]} +- {a[3]}; c8s ({nm}) C {b[0]} +- {b[1]}, M {b[2]} +- {b[3]}: "
                  f"C {a[0] / b[0] - 1:+.1%} (intervals {'apart' if sep_c else 'overlap'}), M {a[2] / b[2] - 1:+.1%} "
                  f"(intervals {'apart' if sep_m else 'overlap'}); X {xa:.4f} - {xb:.4f} = {xa - xb:+.4f}")
    print()


def c4():
    print("C4  What reached the card besides management commands (the workload's host program; posthoc.json commands_sent)")
    src = os.path.join(REPO, "tools", "claims-v3", "e107", "rgm107", "host", "main.cpp")
    for i, ln in enumerate(open(src), 1):
        if re.search(r"rt_->(loadCode|memcpyHostToDevice|memcpyDeviceToHost|kernelLaunch)\(", ln):
            print(f"  {rel(src)}:{i}: {ln.strip()[:110]}")
    c = PH["commands_sent"]
    print(f"  management commands: {c['sampler_lines']} sampler lines, {c['config_reads_session'] + c['config_reads_queue']} config reads, "
          f"{c['dm_commands']['PMIC voltage-register reads (9 per GET_MODULE_VOLTAGE, 2 per GET_ASIC_VOLTAGE)']} PMIC voltage-register reads, "
          f"WRITE commands {c['dm_commands']['WRITE commands']}")
    print()


def c5():
    print("C5  The hottest sensor's running maximum (temp_c.minshire = [mean, low, high]; the high is a running maximum)")
    rows = tel_lines(os.path.join(HERE, "aifoundry2", "smoke")) + tel_lines(os.path.join(HERE, "aifoundry2", "s1"))
    rows.sort(key=lambda j: j["t_ms"])
    hi = [j["temp_c"]["minshire"][2] for j in rows if j.get("temp_c")]
    mean = [j["temp_c"]["minshire"][0] for j in rows if j.get("temp_c")]
    f0 = rows[0]
    print(f"  E126: {len(rows)} sampler lines (smoke and s1). First ({f0['_run']}, before any load): high {f0['temp_c']['minshire'][2]} C, "
          f"mean {f0['temp_c']['minshire'][0]} C; SP running board max {f0['sp']['board_max_w']} W, min {f0['sp']['board_min_w']} W, "
          f"minion temperature max {f0['sp']['minion_c'][2]} C")
    print(f"  E126: the high over every line: min {min(hi)}, max {max(hi)} C; the mean's highest {max(mean)} C")
    print(f"  results.json peaks: {json.dumps(RES['peaks'])}")
    r19 = tel_lines(os.path.join(E119, "aifoundry2", "smoke")) + tel_lines(os.path.join(E119, "aifoundry2", "s1"))
    r19.sort(key=lambda j: j["t_ms"])
    h19 = [(j["temp_c"]["minshire"][2], j) for j in r19 if j.get("temp_c")]
    top = max(h for h, _ in h19)
    first_top = next(j for h, j in h19 if h == top)
    print(f"  E119: the high read {h19[0][0]} C at its first line and {top} C first in {first_top['_run']}; at its last line {h19[-1][0]} C")
    print()


def c6(clone):
    print("C6  Which host build ran, and what the session shows")
    man = open(os.path.join(HERE, "aifoundry2", "s1", "manifest.txt")).read().splitlines()
    for ln in man:
        if ln.startswith(("sha256", "et_soc1")):
            print(f"  manifest.txt: {re.sub(' +', ' ', ln)}")
    print(f"  libDM.so in the manifest: {'yes' if any('libDM' in ln for ln in man) else 'no'}")
    tally, dates = {}, {}
    for p in glob.glob(os.path.join(REPO, "docs", "reports", "data", "**", "*manifest.txt"), recursive=True):
        lines = open(p, errors="replace").read().splitlines()
        host = next((ln.split() for ln in lines if ln.startswith("host")), None)
        if not host or len(host) < 3 or host[1] != "aifoundry2":
            continue
        for ln in lines:
            if ln.startswith(("sha256", "et_soc1")):
                k = re.sub(" +", " ", ln)
                tally[k] = tally.get(k, 0) + 1
                dates.setdefault(k, []).append(host[2][:10])
    n = len({d for v in dates.values() for d in v})
    for k, v in sorted(tally.items(), key=lambda kv: -kv[1]):
        print(f"  aifoundry2 manifests in the repository: {v} x '{k}', {min(dates[k])} to {max(dates[k])}")
    print(f"  ({n} distinct dates)")
    facts = os.path.join(REPO, "docs", "reports", "data", "2026-09-25-aifoundry1", "facts.md")
    for ln in open(facts):
        if ln.startswith(("| `libDM.so`", "| `/opt/et` runtime", "| `/usr/src/et-platform` HEAD", "| `dev_mngt_service`")):
            print(f"  {rel(facts)}: {ln.strip()[:150]}")
    if clone and os.path.isdir(os.path.join(clone, ".git")):
        def git(*a):
            return subprocess.run(["git", "-C", clone] + list(a), capture_output=True, text=True)
        anc = git("merge-base", "--is-ancestor", "353f20e", "836a4ab").returncode == 0
        print(f"  et-platform ({os.path.relpath(clone, REPO) if clone.startswith(REPO) else 'a clone'}): 353f20e "
              f"({git('log', '-1', '--format=%ci', '353f20e').stdout.strip()}) is {'an' if anc else 'NOT an'} ancestor of 836a4ab "
              f"({git('log', '-1', '--format=%ci', '836a4ab').stdout.strip()})")
        paths = ["devicelayer", "devicemanagement", "device-management-application", "et-driver", "common-sw", "device-api"]
        st = git("diff", "--stat", "353f20e", "836a4ab", "--", *paths).stdout.strip()
        print(f"  git diff --stat 353f20e 836a4ab -- {' '.join(paths)}: {st or '(no change)'}")
        st = git("diff", "--stat", "353f20e", "836a4ab", "--", "esperanto-tools-libs/src").stdout.strip().splitlines()
        print("  git diff --stat 353f20e 836a4ab -- esperanto-tools-libs/src: " + " | ".join(s.strip() for s in st))
        print(f"  its commits: {git('log', '--format=%h %s', '353f20e..836a4ab', '--', 'esperanto-tools-libs/src').stdout.strip()}")
        for rev in ("353f20e", "836a4ab"):
            vs = []
            for f in ("esperanto-tools-libs", "devicelayer", "devicemanagement", "device-management-application"):
                m = re.search(r"project\((\w+) VERSION ([\d.]+)", git("show", f"{rev}:{f}/CMakeLists.txt").stdout)
                vs.append(f"{m.group(1)} {m.group(2)}" if m else f"{f} ?")
            print(f"  {rev}: " + ", ".join(vs))
    else:
        print("  et-platform: no clone given (--et-platform <clone>), so the source comparison is not printed")
    rows = tel_lines(os.path.join(HERE, "aifoundry2", "smoke")) + tel_lines(os.path.join(HERE, "aifoundry2", "s1"))
    rows.sort(key=lambda j: j["t_ms"])
    sp = [j["sp"] for j in rows if j.get("sp")]
    mx = [s["board_max_w"] for s in sp]
    mn = [s["board_min_w"] for s in sp]
    tm = [s["minion_c"][2] for s in sp]
    falls = sum(1 for a, b in zip(mx, mx[1:]) if b < a) + sum(1 for a, b in zip(mn, mn[1:]) if b > a) + sum(1 for a, b in zip(tm, tm[1:]) if b < a)
    print(f"  SP running statistics over {len(sp)} lines: board max {min(mx)}-{max(mx)} W, board min {min(mn)}-{max(mn)} W, minion temperature "
          f"max {min(tm)}-{max(tm)} C; falls in a maximum or rises in a minimum: {falls}")
    print(f"  since_reset_ms values: {sorted({j.get('since_reset_ms') for j in rows})}")
    cfg = []
    for sd in ("smoke", "s1"):
        d = os.path.join(HERE, "aifoundry2", sd)
        for p in ("runs.jsonl", "queries.jsonl"):
            for x in open(os.path.join(d, p)):
                if x.strip():
                    j = json.loads(x)
                    q = j.get("queries", j) if p == "runs.jsonl" else j
                    if q and "config_rc" in q:
                        cfg.append(q.get("config") or {})
    for p in glob.glob(os.path.join(HERE, "aifoundry2", "snapshot-*.json")):
        s = json.load(open(p))
        if s.get("config_rc") is not None:
            cfg.append(s.get("config") or {})
    print(f"  ettelem config reads: {len(cfg)}; (TDP W, threshold C) read: {sorted({(c.get('tdp_w'), c.get('temp_threshold_c')) for c in cfg})}")
    dumps = glob.glob(os.path.join(HERE, "aifoundry2", "*", "sp", "*.bin"))
    bad = sum(open(p, "rb").read().count(w) for p in dumps for w in (b"ERROR", b"error", b"invalid", b"Invalid"))
    print(f"  SP trace dumps: {len(dumps)}; occurrences of ERROR / error / invalid: {bad}")
    rc = {}
    for sd in ("smoke", "s1"):
        with gzip.open(os.path.join(HERE, "aifoundry2", sd, "launches.jsonl.gz"), "rt") as f:
            for x in f:
                if x.strip():
                    k = str(json.loads(x).get("rc"))
                    rc[k] = rc.get(k, 0) + 1
    print(f"  workload processes by exit code (smoke and s1): {rc}")
    print()


def main():
    clone = None
    if "--et-platform" in sys.argv:
        clone = os.path.abspath(sys.argv[sys.argv.index("--et-platform") + 1])
    elif os.path.isdir(os.path.join(REPO, "external", "et-platform")):
        clone = os.path.join(REPO, "external", "et-platform")
    print("E126 corrections after verification, Mon 2 Nov 2026: the numbers the corrections quote, from committed files. Post hoc; it decides nothing.")
    print()
    c1()
    c2()
    c3()
    c4()
    c5()
    c6(clone)


if __name__ == "__main__":
    main()
