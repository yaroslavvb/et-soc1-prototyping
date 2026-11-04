#!/usr/bin/env python3
"""E164 (Q141(b)'s fix pass, Wed 4 Nov 2026, before any E164 data or claim): the desk checks behind amendment E164-A1
(E164.md.dated-note.md) and the kit's dated note (README.md.dated-note.md). Desk only: no device, no ssh, no network. It reads the lab
tree and writes only under the scratch directory it is given, never in the lab tree.

    python3 -B tools/claims-v3/e164/selftest_notes_e164.py --scratch <dir> [--freeze] > tools/claims-v3/e164/logs/selftest-notes.txt

  1. the launch (Q141(b) verifier's fault 1): box/launch_e164.sh and box/launch_e164_a1.sh fed through an emulation of ssh's command
     line (ssh joins its command words with single spaces; the box's shell splits them again) into a sandbox laid out like ~/nekko,
     with shims for sudo/et-holders, ps, setsid and GNU date; a stub session runs the real queue_e164.sh on a stub block;
  2. K7W's planned precision (fault 2): the registered statistic at E157's spreads, the registered planning simulation re-run, per tile,
     and what a true change of 0.1-0.3 W does to K7D and K7W;
  3. the other-user rule as coded (fault 3): block_e164.sh's others_present and lib.sh's, run on the same fixtures;
  4. the logs' scrub (fault 4): scrub_etwho_e164.py on fixtures, and on E157's committed logs (which it must leave unchanged);
  5. every gate of E164 against E163's, the rules only one registers, and E164-RANK1 (fault 5);
  6. the interpreters (fault 6): with --freeze, the freeze re-run in a mirror under /usr/bin/python3 and under python3;
  7. the stops' hottest-tile sentence; 8. the card-minutes; 9. every hash list and the kit's committed files; 10. the device-command
     audit of the new files.
Standard library only. SPDX-License-Identifier: Apache-2.0
"""
import argparse
import ast
import glob
import hashlib
import importlib.util
import json
import math
import os
import random
import re
import shutil
import statistics
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
E = "tools/claims-v3/e164"
OWNER = "selftest-owner"      # the session's login in every fixture
OTHER = "fixture-user"        # another account in every fixture (not a login on any box)
RES = []


def say(*a):
    print(*a)


def check(name, ok, detail=""):
    RES.append((name, ok))
    say(f"  [{'PASS' if ok else 'FAIL'}] {name}" + (f" - {detail}" if detail else ""))


def sha(p):
    return hashlib.sha256(open(p, "rb").read()).hexdigest()


def load(rel):
    spec = importlib.util.spec_from_file_location(os.path.basename(rel)[:-3], os.path.join(ROOT, rel))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def write(p, txt, mode=0o644):
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "w") as f:
        f.write(txt)
    os.chmod(p, mode)


# 1. the launch ---------------------------------------------------------------------------------------------------------------
def sec_launch(scr):
    say("\n== 1. The launch: the deadline through ssh's command line (fault 1)")
    gdate = shutil.which("gdate") or ""
    tmo = shutil.which("timeout") or shutil.which("gtimeout") or ""
    if not gdate or not tmo:
        check("GNU date and timeout on this machine", False, "missing: section not run")
        return
    L = os.path.join(scr, "launch")
    shutil.rmtree(L, ignore_errors=True)
    home, shim = os.path.join(L, "home"), os.path.join(L, "shim")
    tree = os.path.join(home, "nekko")
    q_src = os.path.join(ROOT, E, "queue_e164.sh")
    write(os.path.join(tree, E, "queue_e164.sh"), open(q_src).read(), 0o755)
    write(os.path.join(tree, E, "check_e164.py"), 'print("HARNESS OK: selftest stub")\n')
    write(os.path.join(tree, E, "session_e164.sh"),
          '#!/usr/bin/env bash\ncd "$(dirname "${BASH_SOURCE[0]}")/../../.."\nmkdir -p build/e164\n'
          'echo "stub session: E164_DEADLINE=[${E164_DEADLINE:-unset}] E164_DROP_P2=[${E164_DROP_P2:-unset}]" >> build/e164/session.log\n'
          'E164_BLOCK=$PWD/stub_block.sh E164_FIRST_S=3 E164_GAP_S=0 bash tools/claims-v3/e164/queue_e164.sh > build/e164/queue.out 2>&1 < /dev/null\n'
          'echo "stub session: queue: $(tail -1 build/e164/queue.out)" >> build/e164/session.log\necho "session end" >> build/e164/session.log\n',
          0o755)
    write(os.path.join(tree, "stub_block.sh"), '#!/usr/bin/env bash\necho "stub block $1"; sleep 0.2; exit 0\n', 0o755)
    write(os.path.join(shim, "date"), f'#!/bin/sh\nexec {gdate} "$@"\n', 0o755)
    write(os.path.join(shim, "setsid"), '#!/bin/sh\nexec "$@"\n', 0o755)
    write(os.path.join(shim, "ps"), '#!/bin/sh\ncat "$E164_T_PS"\n', 0o755)
    write(os.path.join(shim, "et-who"), '#!/bin/sh\ncat "$E164_T_HOLDERS"\n', 0o755)
    write(os.path.join(shim, "sudo"), '#!/bin/sh\n[ "$1" = "-n" ] && shift\ncase "$1" in */et-holders)\n'
          '  [ "$(cat "$E164_T_SUDO_RC")" = 0 ] || { echo "sudo: a password is required" >&2; exit 1; }\n'
          '  cat "$E164_T_HOLDERS"; exit 0 ;;\nesac\necho "selftest sudo shim: refused" >&2; exit 1\n', 0o755)
    if tmo.endswith("gtimeout"):
        write(os.path.join(shim, "timeout"), f'#!/bin/sh\nexec {tmo} "$@"\n', 0o755)
    check("the sandbox's queue_e164.sh is the committed one", sha(os.path.join(tree, E, "queue_e164.sh")) == sha(q_src))
    me = str(os.getuid())
    none = "No process holds an ET-SoC-1 device node or card lock.\n"
    fx = {"none": (none, ""),
          "card1_other": (f"/dev/et1_ops   {OTHER:<14} 23456      01:02 ./x\n", ""),
          "card0_other": (f"/dev/et0_ops   {OTHER:<14} 23456      01:02 ./x\n", "1001 23456 sparsity_host\n"),
          "card0_ours": (f"/dev/et0_mgmt  {OWNER:<14} 23457      00:09 ./y\n", ""),
          "ours_proc": (none, f"{me} 23458 sparsity_host\n")}
    def dl(off, fmt="+%F %H:%M:%S %Z"):    # a deadline string `off` seconds from now, in Pacific time as the round writes it
        r = subprocess.run([gdate, "-d", f"@{int(time.time()) + off}", fmt], capture_output=True, text=True,
                           env={**os.environ, "TZ": "America/Los_Angeles"})
        return r.stdout.strip()
    new = os.path.join(ROOT, E, "box", "launch_e164_a1.sh")
    old = os.path.join(ROOT, E, "box", "launch_e164.sh")
    # name, script, ssh command words (as written after the host, {D} = the deadline), deadline offset s, fixture, sudo rc, expect
    cases = [
        ("A: the committed launch_e164.sh, its own usage line", old, ["bash -s", "--", "{D}"], 3600, "none", 0, "fault"),
        ("B: launch_e164_a1.sh, the old usage line", new, ["bash -s", "--", "{D}"], 3600, "none", 0, "launch"),
        ("C: launch_e164_a1.sh, the new usage line", new, ["bash -s -- '{D}'"], 3600, "none", 0, "launch"),
        ("D: the new line with E164_DROP_P2=1", new, ["E164_DROP_P2=1 bash -s -- '{D}'"], 3600, "none", 0, "launch-p2"),
        ("E: a deadline already past", new, ["bash -s -- '{D}'"], -60, "none", 0, 4),
        ("F: a deadline 1,200 s away (one pass at most)", new, ["bash -s -- '{D}'"], 1200, "none", 0, 4),
        ("G: a deadline 2,000 s away (two passes)", new, ["bash -s -- '{D}'"], 2000, "none", 0, "launch-two"),
        ("H: not a date", new, ["bash -s -- 'soon-ish PST'"], None, "none", 0, 2),
        ("I: no deadline", new, ["bash -s"], None, "none", 0, 2),
        ("J: card 1 held by another user", new, ["bash -s -- '{D}'"], 3600, "card1_other", 0, 3),
        ("K: card 0 used by another user", new, ["bash -s -- '{D}'"], 3600, "card0_other", 0, "launch-card0"),
        ("L: ours on card 0", new, ["bash -s -- '{D}'"], 3600, "card0_ours", 0, 3),
        ("M: our device process running", new, ["bash -s -- '{D}'"], 3600, "ours_proc", 0, 3),
        ("N: et-holders unreadable", new, ["bash -s -- '{D}'"], 3600, "none", 1, 3)]
    for name, script, words0, off, f, src, expect in cases:
        D = dl(off) if off is not None else ""
        day = D.split()[0] if D else "-"
        words = [w.replace("{D}", D) for w in words0]

        def norm(s):
            if D:
                s = s.replace(D, "<deadline>").replace(day, "<date>")
            s = re.sub(r"\b\d{2}:\d{2}:\d{2}\b", "<time>", s)
            s = re.sub(r"T0\+\d+ s", "T0+<n> s", s)
            s = re.sub(r"is -?\d+ s away", "is <n> s away", s)
            return re.sub(r"\b\d{10}\b", "<epoch>", s)
        shutil.rmtree(os.path.join(tree, "build"), ignore_errors=True)
        hold, ps = fx[f]
        write(os.path.join(L, "holders.txt"), hold)
        write(os.path.join(L, "ps.txt"), ps)
        write(os.path.join(L, "sudo_rc"), f"{src}\n")
        env = {"HOME": home, "PATH": shim + os.pathsep + os.environ.get("PATH", ""), "USER": OWNER, "LOGNAME": OWNER,
               "TZ": "America/Los_Angeles", "E164_T_HOLDERS": os.path.join(L, "holders.txt"), "E164_T_PS": os.path.join(L, "ps.txt"),
               "E164_T_SUDO_RC": os.path.join(L, "sudo_rc"), "LANG": "C"}
        joined = " ".join(words)            # ssh sends its command words joined by single spaces; the box's shell splits them again
        # and the script arrives through a pipe, as over ssh's channel (bash -s then reads it byte by byte; a seekable file would let
        # the detached session's fork move bash's read offset)
        r = subprocess.run(["bash", "-c", joined], input=open(script).read(), env=env, capture_output=True, text=True, timeout=180)
        slog = os.path.join(tree, "build", "e164", "session.log")
        for _ in range(60):
            if os.path.exists(slog) and "session end" in open(slog).read():
                break
            if not os.path.exists(os.path.join(tree, "build", "e164", "T0")):
                break
            time.sleep(0.5)
        launched = os.path.exists(os.path.join(tree, "build", "e164", "T0"))
        s = open(slog).read() if os.path.exists(slog) else ""
        m = re.search(r"E164_DEADLINE=\[([^\]]*)\] E164_DROP_P2=\[([^\]]*)\]", s)
        seen, p2 = (m.group(1), m.group(2)) if m else ("", "")
        qm = re.search(r"queue: (.*)", s)
        q = norm(qm.group(1)) if qm else ""
        out = norm(r.stdout + r.stderr)
        refusal = next((ln for ln in out.splitlines() if ln.startswith(("REFUSED", "not a date", "usage"))), "")
        say(f"  {name}: ssh command [{norm(joined)}] -> rc {r.returncode}; {'launched' if launched else 'nothing launched'}"
            + (f"; the session saw E164_DEADLINE [{norm(seen)}], E164_DROP_P2 [{p2}]; queue: {q}" if launched else f"; {refusal}"))
        if expect == "fault":
            check("A reproduces fault 1: the session gets only the date and the queue runs no pass",
                  launched and seen == day and "0 passes" in q)
        elif str(expect).startswith("launch"):
            ok = launched and r.returncode == 0 and seen == D and "5 passes" in q
            ok = ok and p2 == ("1" if expect == "launch-p2" else "unset")
            ok = ok and ("expected by the queue's rule: " + ("2" if expect == "launch-two" else "4") + " of the 4 planned") in out
            if expect == "launch" and name.startswith("C"):
                pr = next((ln for ln in out.splitlines() if ln.startswith("passes expected")), "")
                say(f"    {pr}")
                hl = next((ln for ln in out.splitlines() if ln.startswith("holders at launch")), "")
                say(f"    {hl}")
            if expect == "launch-card0":
                rec = open(os.path.join(tree, "build", "e164", "holders-at-launch.txt")).read()
                ok = ok and "card 0 ours 0, another user 1" in rec and "other users' device processes 1" in rec and OTHER not in rec
                ok = ok and "does not block E164" in out
            check(f"{name[:1]} launches with the whole deadline", ok)
        else:
            check(f"{name[:1]} refused with exit {expect} before anything is launched", r.returncode == expect and not launched)
    shutil.rmtree(L, ignore_errors=True)


# 2. K7W's planned precision ---------------------------------------------------------------------------------------------------
def sec_k7(scr):
    say("\n== 2. K7W's planned precision, at E157's per-pass spreads, four E164 passes (fault 2)")
    reg = json.load(open(os.path.join(ROOT, E, "predictions-e164.json")))
    pk = load("tools/claims-v3/ccheck/pick6.py")
    mp = load(f"{E}/make_predictions_e164.py")
    k7, anc = reg["k7"]["tiles"], reg["k7"]["scale_anchors_E157"]
    fams = reg["scheme"]["repeat"]["scale_anchors"]
    assert fams == mp.K7_SCALE_ANCHORS
    n_new = 4

    def se_i(a):
        x = anc[a]
        return math.hypot(x["se"] / x["mean"], (x["sd"] / math.sqrt(n_new)) / x["mean"])
    sse = {}
    for f, an in fams.items():
        if len(an) == 4:   # the middle two of four ratios: any pair can be the middle two
            v = [math.sqrt(se_i(a) ** 2 + se_i(b) ** 2) / 2 for i, a in enumerate(an) for b in an[i + 1:]]
            sse[f] = (min(v), max(v))
        else:
            v = math.sqrt(sum(se_i(a) ** 2 for a in an)) / len(an)
            sse[f] = (v, v)
    say(f"  the scale's standard error (relative): floats {sse['floats'][0]:.4f}-{sse['floats'][1]:.4f}, int8 {sse['int8'][0]:.4f}")
    det = {}
    for t, v in k7.items():
        f = "int8" if v["type"] == "int8" else "floats"
        o = v["E157"]
        vo, vn = o["se"] ** 2, (o["sd"] / math.sqrt(n_new)) ** 2
        nu = (vo + vn) ** 2 / (vo ** 2 / (o["n"] - 1) + vn ** 2 / (n_new - 1))
        tq = pk.t975(nu)
        det[t] = [tq * math.sqrt(vo + vn + (o["mean"] * s) ** 2) for s in sse[f]]
    # the registered planning simulation (make_predictions_e164.k7_planned), re-run with its seed and draws, per tile
    sims = {}

    def simulate(shift_tile=None, shift=0.0, draws=4000, seed=16407):
        rng = random.Random(seed)
        fam = {t: ("int8" if t.startswith("int8.") else "floats") for t in k7}
        a_k7 = {t: {"mean": v["E157"]["mean"], "sd": v["E157"]["sd"]} for t, v in k7.items()}
        a_an = {a: {"mean": v["mean"], "sd": v["sd"]} for a, v in anc.items()}
        res = {"passd": 0, "passw": 0, "w_in": {t: 0 for t in k7}, "d_in": {t: 0 for t in k7}, "hw": {t: [] for t in k7}}
        for _ in range(draws):
            def sess(src, n, sh):
                out = {}
                for t, v in list(src.items()):
                    mu = v["mean"] + (sh if (sh and t == shift_tile) else 0.0)
                    xs = [mu + rng.gauss(0.0, v["sd"]) for _ in range(n)]
                    out[t] = (sum(xs) / n, statistics.stdev(xs) / math.sqrt(n))
                return out
            both = dict(a_k7)
            both.update(a_an)
            old, new = sess(both, 3, 0.0), sess(both, n_new, shift)
            scale, ss = {}, {}
            for f, an in fams.items():
                rat = sorted((old[a][0] / new[a][0], a) for a in an)
                mid = rat[1:3] if len(rat) == 4 else rat
                scale[f] = sum(r for r, _ in mid) / len(mid)
                ss[f] = math.sqrt(sum((r * math.hypot(old[a][1] / old[a][0], new[a][1] / new[a][0])) ** 2 for r, a in mid)) / len(mid)
            nd = nw = 0
            for t in (k7 if shift_tile is None else [shift_tile]):   # a shifted run reads only the shifted tile
                s = scale[fam[t]]
                d = s * new[t][0] - old[t][0]
                vo, vn = old[t][1] ** 2, (s * new[t][1]) ** 2
                nu = (vo + vn) ** 2 / (vo ** 2 / (3 - 1) + vn ** 2 / (n_new - 1))
                hw = pk.t975(nu) * math.sqrt(vo + vn + (new[t][0] * ss[fam[t]]) ** 2)
                res["hw"][t].append(hw)
                if abs(d) <= 0.05:
                    nd += 1
                    res["d_in"][t] += 1
                if abs(d) <= hw:
                    nw += 1
                    res["w_in"][t] += 1
            res["passd"] += nd >= 7
            res["passw"] += nw == len(k7)
        res["draws"] = draws
        return res
    base = simulate()
    comm = reg["precision_before_data"]["E164-K7"]
    same = (base["passd"] / 4000 == comm["P_K7D_pass"] and base["passw"] / 4000 == comm["P_K7W_pass"]
            and all(base["d_in"][t] / 4000 == comm["P_within_0p05_by_tile"][t] for t in k7))
    check("the re-run reproduces the registered planning numbers exactly (P(K7D) 0.172, P(K7W) 0.902, each tile's P(|delta| <= 0.05 W))",
          same, f"P(K7D) {base['passd'] / 4000:.3f}, P(K7W) {base['passw'] / 4000:.3f}")
    say("  per tile, nothing changed between the sessions (4,000 simulated session pairs, seed 16407, as registered):")
    say("  | K7 tile | D, W | K7W half-width at E157's spreads, W | simulated half-width, median (5-95%), W | P(inside K7W) | P(|delta| <= 0.05 W) |")
    for t in k7:
        hw = sorted(base["hw"][t])
        q = lambda p: hw[int(p * (len(hw) - 1))]
        lo, hi = det[t]
        say(f"  | {t} | {k7[t]['E157']['mean']:.2f} | {lo:.3f}" + (f"-{hi:.3f}" if hi - lo > 5e-4 else "") +
            f" | {q(0.5):.3f} ({q(0.05):.3f}-{q(0.95):.3f}) | {base['w_in'][t] / 4000:.3f} | {base['d_in'][t] / 4000:.3f} |")
    ints = [t for t in k7 if t.startswith("int8.")]
    flt = [t for t in k7 if not t.startswith("int8.")]
    i_lo, i_hi = min(det[t][0] for t in ints), max(det[t][1] for t in ints)
    f_lo, f_hi = min(det[t][0] for t in flt), max(det[t][1] for t in flt)
    say(f"  so K7W's half-width is {i_lo:.3f}-{i_hi:.3f} W on the four int8 tiles and {f_lo:.3f}-{f_hi:.3f} W on the floats; "
        f"E164.md's column (E157's se and passes only) gave {min(k7[t]['repeat_band_W_E157'] for t in ints):.3f}-"
        f"{max(k7[t]['repeat_band_W_E157'] for t in ints):.3f} W on int8")
    check("K7W's planned int8 half-width is wider than card 1's 0.1-0.2 W day-to-day floor", i_lo > 0.2, f"{i_lo:.3f}-{i_hi:.3f} W")
    tt = "int8.powerlaw_df4_pc"
    o = k7[tt]["E157"]
    by_n = {}
    for n in (4, 8, 16):
        sei = lambda a: math.hypot(anc[a]["se"] / anc[a]["mean"], (anc[a]["sd"] / math.sqrt(n)) / anc[a]["mean"])
        ss = math.sqrt(sum(sei(a) ** 2 for a in fams["int8"])) / len(fams["int8"])
        vo, vn = o["se"] ** 2, (o["sd"] / math.sqrt(n)) ** 2
        nu = (vo + vn) ** 2 / (vo ** 2 / (o["n"] - 1) + vn ** 2 / (n - 1))
        by_n[n] = pk.t975(nu) * math.sqrt(vo + vn + (o["mean"] * ss) ** 2)
    say(f"  {tt}'s K7W half-width at E157's spreads with 4 / 8 / 16 E164 passes: " + " / ".join(f"{by_n[n]:.3f}" for n in (4, 8, 16)) + " W")
    check("more E164 passes do not narrow K7W's int8 width (E157's three passes set it)", max(by_n.values()) - min(by_n.values()) < 0.03)
    say("  a true day-to-day change on one tile, E164 higher by delta, everything else unchanged (2,000 session pairs each, seed 16408):")
    say("  | K7 tile | delta 0.10 W: P(flagged by K7W) / P(outside 0.05 W) | delta 0.20 W | delta 0.30 W |")
    power = {}
    for t in k7:
        row = []
        for dlt in (0.1, 0.2, 0.3):
            r = simulate(t, dlt, draws=2000, seed=16408)
            pw = 1 - r["w_in"][t] / 2000
            pd = 1 - r["d_in"][t] / 2000
            power[(t, dlt)] = pw
            row.append(f"{pw:.2f} / {pd:.2f}")
        say(f"  | {t} | " + " | ".join(row) + " |")
    worst = max(power[(t, 0.2)] for t in ints)
    check("on int8, K7W flags a true 0.2 W change less than half the time", worst < 0.5, f"at most {worst:.2f}")


# 3. the other-user rule ------------------------------------------------------------------------------------------------------
def extract_fn(txt, start_pat, end_line):
    lines = txt.split("\n")
    i = next(k for k, ln in enumerate(lines) if re.match(start_pat, ln))
    j = next(k for k in range(i + 1, len(lines)) if lines[k] == end_line)
    return "\n".join(lines[i:j + 1]), i + 1, j + 1


def sec_others(scr):
    say("\n== 3. Who blocks E164 on aifoundry1, as the code reads it (fault 3)")
    L = os.path.join(scr, "others")
    shutil.rmtree(L, ignore_errors=True)
    shim = os.path.join(L, "shim")
    stub = os.path.join(L, "et-holders")
    lib = open(os.path.join(ROOT, "tools/claims-v3/lib.sh")).read()
    blk = open(os.path.join(ROOT, E, "block_e164.sh")).read()
    f_e164, a, b = extract_fn(blk, r"^  others_present\(\) \{$", "  }")
    f_lib, c, d = extract_fn(lib, r"^others_present\(\) \{$", "}")
    say(f"  block_e164.sh lines {a}-{b} (E164's override, used whenever V3_DEVICE is set: lib.sh refuses aifoundry1 without it); "
        f"lib.sh lines {c}-{d} (A3)")
    comm = "\n".join(ln for ln in lib.split("\n") if ln.startswith(("DEV_COMM=", "OTHER_COMM=")))
    write(stub, '#!/bin/sh\ncat "$E164_T_HOLDERS"\n', 0o755)
    write(os.path.join(shim, "sudo"), '#!/bin/sh\n[ "$1" = "-n" ] && shift\ncase "$1" in */et-holders)\n'
          '  [ "$(cat "$E164_T_SUDO_RC")" = 0 ] || exit 1\n  exec "$1" ;;\nesac\nexit 1\n', 0o755)
    write(os.path.join(shim, "ps"), '#!/bin/sh\ncat "$E164_T_PS"\n', 0o755)
    write(os.path.join(shim, "who"), '#!/bin/sh\nexit 0\n', 0o755)
    for name, fn in (("e164", f_e164), ("lib", f_lib)):
        write(os.path.join(L, f"{name}.sh"), "#!/usr/bin/env bash\nset -u\nlog() { echo \"LOG $*\"; }\n" + comm + "\n" +
              fn.replace("/usr/local/sbin/et-holders", stub) + "\n"
              "if others_present > /dev/null 2>&1; then echo BLOCKS; else echo 'does not block'; fi\n", 0o755)
    me = str(os.getuid())
    none = "No process holds an ET-SoC-1 device node or card lock.\n"
    fx = [("nobody holds anything", none, "", 0, (False, False)),
          ("another user holds card 0's node", f"/dev/et0_ops   {OTHER:<14} 23456      01:02 ./x\n", "", 0, (False, True)),
          ("another user holds card 0's lock", f"lock:etsoc-shire0.lock {OTHER:<14} 23456 01:02 bash x\n", "", 0, (False, True)),
          ("another user holds card 1's node", f"/dev/et1_mgmt  {OTHER:<14} 23456      01:02 ./x\n", "", 0, (True, True)),
          ("another user holds card 1's lock", f"lock:etsoc-shire1.lock {OTHER:<14} 23456 01:02 bash x\n", "", 0, (True, True)),
          ("another user's device process, no node held", none, "1001 23456 sparsity_host\n", 0, (False, True)),
          ("a CI job running (Runner.Worker, root)", none, "0 23457 Runner.Worker\n", 0, (False, True)),
          ("et-holders unreadable", none, "", 1, (True, False)),
          ("our own holder on card 1 (others_present ignores ours)", f"/dev/et1_ops   {OWNER:<14} 23458      00:01 ./y\n",
           f"{me} 23458 sparsity_host\n", 0, (False, False))]
    say("  | fixture | E164's code (block_e164.sh) | lib.sh's A3 rule |")
    for name, hold, ps, src, (want_e, want_l) in fx:
        write(os.path.join(L, "holders.txt"), hold)
        write(os.path.join(L, "ps.txt"), ps)
        write(os.path.join(L, "sudo_rc"), f"{src}\n")
        env = {"PATH": shim + os.pathsep + os.environ.get("PATH", ""), "USER": OWNER, "V3_DEVICE": "1", "LANG": "C",
               "E164_T_HOLDERS": os.path.join(L, "holders.txt"), "E164_T_PS": os.path.join(L, "ps.txt"),
               "E164_T_SUDO_RC": os.path.join(L, "sudo_rc")}
        got = []
        for nm in ("e164", "lib"):
            r = subprocess.run(["bash", os.path.join(L, f"{nm}.sh")], env=env, capture_output=True, text=True, timeout=30)
            got.append(r.stdout.strip() == "BLOCKS")
        say(f"  | {name} | {'blocks' if got[0] else 'does not block'} | {'blocks' if got[1] else 'does not block'} |")
        check(f"as expected: {name}", tuple(got) == (want_e, want_l))
    shutil.rmtree(L, ignore_errors=True)


# 4. the logs' scrub ----------------------------------------------------------------------------------------------------------
def sec_scrub(scr):
    say("\n== 4. The logs' scrub before the data commit (fault 4)")
    L = os.path.join(scr, "scrub")
    shutil.rmtree(L, ignore_errors=True)
    sc = os.path.join(ROOT, E, "scrub_etwho_e164.py")
    d1 = os.path.join(L, "fixture")
    owner_lines = [f"/dev/et1_mgmt  {OWNER:<14} 34567      00:05 bash tools/claims-v3/e164/block_e164.sh 16410",
                   f"lock:etsoc-shire1.lock {OWNER:<14} 34568 00:05 bash tools/claims-v3/e164/block_e164.sh 16410"]
    none = "No process holds an ET-SoC-1 device node or card lock."
    log = "\n".join([
        "2026-11-04 12:00:00 PST session start (selftest fixture)",
        f"/dev/et0_ops   {OTHER:<14} 23456   01:02:03 ./bench --card 0 --out /home/{OTHER}/work/run1",
        owner_lines[0], owner_lines[1],
        f"2026-11-04T12:00:01 [aifoundry1-c1] e164 p16410 begins (die 54 C) -> /home/{OWNER}/nekko/build/claims-v3/aifoundry1-c1/e164/p16410",
        f"2026-11-04T12:00:02 [aifoundry1-c1] others present: procs=[] holders=[{OTHER}:45678 ]",
        f"2026-11-04T12:00:03 [aifoundry1-c1] others present: users=[holders:{OTHER}:45678 ] procs=[1001:56789:sparsity_host ]",
        "2026-11-04T12:00:04 [aifoundry1-c1] others present: et-holders unreadable: sudo: a password is required",
        none, f"a note that names {OTHER} in passing", ""])
    write(os.path.join(d1, "session.log"), log)
    write(os.path.join(d1, "queue.out"), "12:00:05 e164: done, 4 passes, at T0+3456 s\n")
    r = subprocess.run([sys.executable, "-B", sc, d1], capture_output=True, text=True)
    say(f"  fixture (owner from the logs' /home/<login>/nekko/ path): rc {r.returncode}; {r.stdout.strip()}")
    after = open(os.path.join(d1, "session.log")).read()
    check("no trace of the other account is left in any file", OTHER not in after and OTHER not in open(os.path.join(d1, "queue.out")).read()
          and OTHER not in open(os.path.join(d1, "et-who-summary.txt")).read())
    check("the owner's holder lines and the 'No process holds' line are kept byte for byte",
          all(ln in after.split("\n") for ln in owner_lines + [none]))
    check("another user's uid in procs=[] is masked", "1001:" not in after and "<another-uid>:56789:sparsity_host" in after)
    check("the queue log, which names nobody, is unchanged", open(os.path.join(d1, "queue.out")).read().startswith("12:00:05 e164: done"))
    summ = open(os.path.join(d1, "et-who-summary.txt")).read().strip().split("\n")[1:]
    say("  et-who-summary.txt: " + " | ".join(summ))
    check("the summary counts card 0's other user and card 1's two of ours, no names",
          summ == ["session.log:2: held: card 0 another user 1, card 1 ours 2", "session.log:9: no holder on either card"])
    rc = subprocess.run([sys.executable, "-B", sc, "--check", d1], capture_output=True, text=True)
    check("--check reads OK after the scrub", rc.returncode == 0, rc.stdout.strip().split("\n")[-1])
    d2 = os.path.join(L, "unscrubbed")
    write(os.path.join(d2, "session.log"), log)
    rc = subprocess.run([sys.executable, "-B", sc, "--check", d2, "--owner", OWNER], capture_output=True, text=True)
    check("--check refuses the unscrubbed fixture (exit 1)", rc.returncode == 1, rc.stdout.strip().split("\n")[-1])
    d3 = os.path.join(L, "twoowners")
    write(os.path.join(d3, "session.log"), f"-> /home/{OWNER}/nekko/build\n-> /home/{OTHER}/nekko/build\n")
    rc = subprocess.run([sys.executable, "-B", sc, d3], capture_output=True, text=True)
    check("two logins in the session's own paths and no --owner: refused (exit 2), nothing rewritten",
          rc.returncode == 2 and not os.path.exists(os.path.join(d3, "et-who-summary.txt")))
    src = os.path.join(ROOT, "docs/reports/data/2026-11-03-e157-blind6-card1/logs")
    d4 = os.path.join(L, "e157")
    shutil.copytree(src, d4)
    r = subprocess.run([sys.executable, "-B", sc, d4], capture_output=True, text=True)
    same = all(sha(os.path.join(d4, n)) == sha(os.path.join(src, n)) for n in os.listdir(src))
    summ = open(os.path.join(d4, "et-who-summary.txt")).read().strip().split("\n")[1:]
    check("E157's committed logs (the parent session's; nobody else on the box) come through byte-identical", r.returncode == 0 and same,
          f"{len(os.listdir(src))} files; {r.stdout.strip()}")
    say("  E157's et-who readings: " + " | ".join(summ))
    shutil.rmtree(L, ignore_errors=True)


# 5. the gates against E163's, and E164-RANK1 ----------------------------------------------------------------------------------
def rule_ids(md, pre):
    ids = []
    for ln in open(os.path.join(ROOT, md)).read().split("\n"):
        m = re.match(r"^\| (?:\*\*)?(" + pre + r"-[A-Za-z0-9′']+|RK4)(?:\*\*)?", ln)
        if m and m.group(1) not in ids:
            ids.append(m.group(1))
    return ids


def sec_gates(scr):
    say("\n== 5. Every gate of E164 against E163's, and the rules only one registers (fault 5)")
    a = json.load(open(os.path.join(ROOT, "tools/claims-v3/e163/predictions-e163.json")))
    b = json.load(open(os.path.join(ROOT, E, "predictions-e164.json")))
    ma, mb = dict(a["spec"]["mins"]), dict(b["plan"]["min_tiles"])
    ma["unaimed"] = a["spec"]["u_rule"]["min_tiles"]
    rows = [("P1", "fp32", "priority-1 fp32 (17)"), ("P2", "fp16", "priority-1 fp16 (9)"), ("P3", "int8", "priority-1 int8 (22)"),
            ("B1", "floats", "priority-1 floats (26)"), ("B2", "int8", "priority-1 int8 (22)"), ("H1", "fp32", "priority-1 fp32 (17)"),
            ("H2", "fp16", "priority-1 fp16 (9)"), ("H3", "int8", "priority-1 int8 (22)"), ("U1", "unaimed", "the 12 U tiles"),
            ("R1", "real", "the 10 priority-1 real tiles"), ("R2", "real", "the 10 priority-1 real tiles")]
    say("  | rule | set | E163 needs at least | E164 needs at least | differs |")
    nd = 0
    for r, k, s in rows:
        diff = ma[k] != mb[k]
        nd += diff
        say(f"  | {r} | {s} | {ma[k]} | {mb[k]} | {'yes' if diff else 'no'} |")
    say("  | C1, H4 | the 48 | 10 (NOT SCORED under) | 10 | no |")
    say("  | M1, M2 | the 48 | 10 | 10 | no |")
    check("the machine gates match the words of both registrations",
          ma == {"fp32": 9, "fp16": 5, "int8": 11, "floats": 13, "real": 7, "unaimed": 8}
          and mb == {"fp32": 6, "fp16": 4, "int8": 6, "floats": 8, "real": 8, "unaimed": 10})
    check("11 of the 11 gated rule slots differ (P1-P3, B1-B2, H1-H3, U1, R1, R2)", nd == 11, f"{nd} differ")
    sc164 = open(os.path.join(ROOT, E, "score_e164.py")).read()
    sc163 = open(os.path.join(ROOT, "tools/claims-v3/e163/score_e163.py")).read()
    check("R2 is gated with R1 by the real-tile minimum in both scorers",
          'rules[f"{pre}-R1"] = rules[f"{pre}-R2"]' in sc164 and 'rules[rr["R1"]] = rules[rr["R2"]]' in sc163)
    i3 = rule_ids("tools/claims-v3/e163/E163.md", "E163")
    i4 = rule_ids(f"{E}/E164.md", "E164")
    s3 = {x.split("-", 1)[-1] for x in i3}
    s4 = {x.split("-", 1)[-1] for x in i4}
    say(f"  E163's rules: {', '.join(i3)}")
    say(f"  E164's rules: {', '.join(i4)}")
    say(f"  only E163: {', '.join(sorted(s3 - s4))}; only E164: {', '.join(sorted(s4 - s3))} (KC and PC are the same C rule, named apart)")
    say(f"  other differences: bootstrap seed 16300 vs 16400 (both 20,000 draws, paired 5,000); heat references 0.1813 / 0.1589 / 0.2046 C "
        f"(aifoundry3) vs 0.3519 / 0.3547 / 0.1408 C (card 1); E163 plans 3 kinds passes, E164 4; both score from 2 kept passes")
    e163md = open(os.path.join(ROOT, "tools/claims-v3/e163/E163.md")).read()
    check("E163.md says E164 registers the other half of RANK1, and E164.md registers no RANK1",
          "E164 registers the other half" in e163md and "RANK1" not in open(os.path.join(ROOT, E, "E164.md")).read())
    r1 = load(f"{E}/rank1_e164.py")
    base = {"E164-M1": "BETTER", "E164-U1": "PASS", "E164-B1": "PASS", "E164-B2": "PASS", "E164-C1": "PASS"}
    cases = [(base, "PASS"), ({**base, "E164-M1": "NOT RESOLVED"}, "FAIL"), ({**base, "E164-B1": "FAIL HIGH"}, "FAIL"),
             ({**base, "E164-U1": "NOT SCORED"}, "NOT SCORED"), ({**base, "E164-M1": "WORSE", "E164-C1": "NOT SCORED"}, "NOT SCORED"),
             ({}, "NOT SCORED")]
    ok = all(r1.rank1(v)["verdict"] == want for v, want in cases)
    check("rank1_e164.py reads E163-RANK1's precedence (PASS / NOT SCORED / FAIL) on six verdict sets", ok)
    spec = a["spec"]["rank1"]["needs"]
    check("E164-RANK1 needs exactly what E163-RANK1 needs, rule for rule",
          {k.replace("E163-", ""): v for k, v in spec.items()} == {k.replace("E164-", ""): v for k, v in r1.NEEDS.items()})


# 6. the interpreters ---------------------------------------------------------------------------------------------------------
def sec_interp(scr, freeze):
    say("\n== 6. The interpreters of the freeze (fault 6)")
    py39 = "/usr/bin/python3"
    v = lambda py: subprocess.run([py, "-c", "import sys; print(sys.version.split()[0])"], capture_output=True, text=True).stdout.strip()
    npv = subprocess.run([py39, "-c", "import numpy; print(numpy.__version__)"], capture_output=True, text=True).stdout.strip()
    say(f"  {py39}: Python {v(py39)}, numpy {npv or 'absent'}; python3 on the PATH: Python {v('python3')}")
    if not freeze:
        say("  the re-run in a mirror: not run (pass --freeze)")
        return
    M = os.path.join(scr, "mirror")
    shutil.rmtree(M, ignore_errors=True)
    os.makedirs(os.path.join(M, "tools", "claims-v3"))
    shutil.copytree(os.path.join(ROOT, E), os.path.join(M, E), ignore=shutil.ignore_patterns("__pycache__"))
    for d in glob.glob(os.path.join(ROOT, "tools", "claims-v3", "*")):
        if os.path.basename(d) != "e164":
            os.symlink(d, os.path.join(M, "tools", "claims-v3", os.path.basename(d)))
    for d in glob.glob(os.path.join(ROOT, "*")):
        if os.path.basename(d) != "tools":
            os.symlink(d, os.path.join(M, os.path.basename(d)))
    for d in glob.glob(os.path.join(ROOT, "tools", "*")):
        if os.path.basename(d) != "claims-v3":
            os.symlink(d, os.path.join(M, "tools", os.path.basename(d)))

    def run(py, script):
        t = time.time()
        r = subprocess.run(["nice", "-n", "10", py, "-B", f"{E}/{script}"], cwd=M, capture_output=True, text=True, timeout=1800)
        return r.returncode, time.time() - t

    def cmp(name):
        a, b = os.path.join(ROOT, E, name), os.path.join(M, E, name)
        if sha(a) == sha(b):
            return "byte-identical", []
        la, lb = open(a).read().split("\n"), open(b).read().split("\n")
        return "differs", [i + 1 for i, (x, y) in enumerate(zip(la, lb)) if x != y]
    rc, s = run(py39, "ref_errors_e164.py")
    st, _ = cmp("ref-errors-m9.json")
    check(f"ref_errors_e164.py under {py39} {v(py39)} rewrites ref-errors-m9.json byte for byte", rc == 0 and st == "byte-identical",
          f"rc {rc}, {s:.0f} s")
    rc, s = run(py39, "make_predictions_e164.py")
    st1, _ = cmp("predictions-e164.json")
    st2, _ = cmp("planned-intervals.txt")
    check(f"make_predictions_e164.py under {py39} {v(py39)}: predictions-e164.json and planned-intervals.txt byte for byte",
          rc == 0 and st1 == st2 == "byte-identical", f"rc {rc}, {s:.0f} s")
    rc, s = run("python3", "make_predictions_e164.py")
    st1, lines = cmp("predictions-e164.json")
    st2, _ = cmp("planned-intervals.txt")
    reg = json.load(open(os.path.join(ROOT, E, "predictions-e164.json")))
    alt = json.load(open(os.path.join(M, E, "predictions-e164.json")))
    paths = []

    def walk(x, y, p):
        if isinstance(x, dict):
            for k in x:
                walk(x[k], y.get(k), p + [k])
        elif isinstance(x, list):
            for i, (u, w) in enumerate(zip(x, y)):
                walk(u, w, p + [str(i)])
        elif x != y:
            paths.append((".".join(p), x, y))
    walk(reg, alt, [])
    say(f"  python3 {v('python3')}: rc {rc}, {s:.0f} s; predictions-e164.json {st1} at lines {lines}; planned-intervals.txt {st2}")
    for p, x, y in paths:
        say(f"    {p}: committed {x!r}, python3 {v('python3')} {y!r} (difference {abs(x - y):.1e})")
    check("under python3 3.10+ only two reported sd fields differ, each in its last digit, and no verdict reads them",
          rc == 0 and st2 == "byte-identical" and len(paths) == 2 and all(p.endswith(".sd") and abs(x - y) < 1e-15 for p, x, y in paths))
    shutil.rmtree(M, ignore_errors=True)


# 7.-10. ----------------------------------------------------------------------------------------------------------------------
def sec_rest(scr):
    say("\n== 7. The stops' hottest-tile sentence (E164.md, Stops)")
    p7 = json.load(open(os.path.join(ROOT, "tools/claims-v3/kinds/blind7/predictions-blind7-aifoundry1c1.json")))["tiles"]
    p6 = json.load(open(os.path.join(ROOT, "tools/claims-v3/kinds/blind6/predictions-blind6-aifoundry1c1.json")))["tiles"]
    h7 = max(p7, key=lambda t: p7[t]["M9"]["S_w"])
    h6 = max(p6, key=lambda t: p6[t]["M8"]["S_w"])
    h6n = max((t for t in p6 if "anchor" not in t), key=lambda t: p6[t]["M8"]["S_w"])
    say(f"  pool 7's hottest M9 S on card 1: {h7} {p7[h7]['M9']['S_w']:.2f} W; pool 6's hottest M8 S: {h6} {p6[h6]['M8']['S_w']:.3f} W "
        f"(run in E157 and again in E164); pool 6's hottest non-anchor tile: {h6n} {p6[h6n]['M8']['S_w']:.3f} W")
    check("pool 6's anchor fp32.anchor6_randn, which E164 runs, is predicted hotter than pool 7's hottest tile",
          h6 == "fp32.anchor6_randn" and p6[h6]["M8"]["S_w"] > p7[h7]["M9"]["S_w"])
    say("\n== 8. The card-minutes, from E157's measured session on this card")
    q = open(os.path.join(ROOT, "docs/reports/data/2026-11-03-e157-blind6-card1/logs/queue.out")).read()
    first = int(re.search(r"p15710 starts at T0\+(\d+) s", q).group(1))
    durs = [int(x) for x in re.findall(r"p1571\d rc=0 \((\d+) s\)", q)]
    sc = [d * 98 / 78 for d in durs]
    end = first + sum(sc) + 4 * 10
    say(f"  E157: first pass at T0+{first} s, passes {durs} s for 78 launches; scaled to 98: {[round(x) for x in sc]} s; four passes, three "
        f"10 s gaps and the queue's sleep after the last: the session ends about T0+{end:.0f} s = {end / 60:.1f} card-minutes "
        f"({(first + 4 * min(sc) + 40) / 60:.1f}-{(first + 4 * max(sc) + 40) / 60:.1f} at the shortest and longest pass)")
    s4 = first + sc[0] + 10 + sc[1] + 10 + sc[2] + 10
    check("the fourth pass starts inside the 3,840 s limit and a fifth does not fit; the session ends inside the 65-minute cap",
          s4 + max(sc) <= 3840 and s4 + sc[3] + 10 + max(sc) > 3840 and end <= 3900)
    say("\n== 9. Every hash list, and the kit's committed files")
    b7 = os.path.join(ROOT, "tools/claims-v3/kinds/blind7")
    ok7 = sum(1 for ln in open(os.path.join(b7, "SHA256SUMS")) if ln.strip() and sha(os.path.join(b7, ln.split(None, 1)[1].strip().lstrip("*"))) == ln.split()[0])
    check("blind7/SHA256SUMS", ok7 == 91, f"{ok7} OK")
    g4 = os.path.join(ROOT, "docs/reports/data/2026-11-04-q140q-gemm-g4-stride")
    fj = json.load(open(os.path.join(g4, "frozen-sha256-e168.json")))
    okj = sum(1 for p, h in fj.items() if sha(os.path.normpath(os.path.join(g4, p))) == h)
    check("frozen-sha256-e168.json", okj == len(fj) == 9, f"{okj} of {len(fj)}")
    ft = [ln.split() for ln in open(os.path.join(g4, "frozen-sha256-e168-scorer.txt")) if ln.strip()]
    okt = sum(1 for h, p in ft if sha(os.path.normpath(os.path.join(g4, p))) == h)
    check("frozen-sha256-e168-scorer.txt", okt == len(ft) == 18, f"{okt} of {len(ft)}")
    src = open(os.path.join(ROOT, "docs/reports/data/2026-11-04-q140e-heat-replicates/predict_q140e.py")).read()
    fr = next(ast.literal_eval(n.value) for n in ast.parse(src).body
              if isinstance(n, ast.Assign) and any(isinstance(t, ast.Name) and t.id == "FROZEN" for t in n.targets))
    okf = sum(1 for p, h in fr.items() if sha(os.path.join(ROOT, p)) == h)
    check("predict_q140e's FROZEN input hashes", okf == len(fr) == 26, f"{okf} of {len(fr)}")
    r = subprocess.run([sys.executable, "-B", os.path.join(ROOT, E, "check_e164.py"), "--desk"], capture_output=True, text=True)
    check("check_e164.py --desk (harness-e164.json)", r.returncode == 0, r.stdout.strip())
    tracked = subprocess.run(["git", "-C", ROOT, "ls-tree", "-r", "--name-only", "ce10e301", "--", E], capture_output=True, text=True).stdout.split()
    changed = subprocess.run(["git", "-C", ROOT, "diff", "--name-only", "ce10e301", "--", *tracked], capture_output=True, text=True).stdout.split()
    check("every file of the kit's three commits is unchanged in the tree (only new files are added)", len(tracked) == 58 and not changed,
          f"{len(tracked)} files, {len(changed)} changed")
    data = subprocess.run(["git", "-C", ROOT, "log", "--all", "--name-only", "--format=", "--", "docs/reports/data/"], capture_output=True,
                          text=True).stdout.split()
    e164d = sorted({p for p in data if re.search(r"docs/reports/data/[^/]*e164", p)})
    check("no E164 data exists in the repository's history", not e164d, f"{len(e164d)} paths")
    say("\n== 10. The device-command audit of the new files")
    new = [f"{E}/box/launch_e164_a1.sh", f"{E}/collect_e164_a1.sh", f"{E}/scrub_etwho_e164.py", f"{E}/rank1_e164.py",
           f"{E}/selftest_notes_e164.py"]
    r = subprocess.run([sys.executable, "-B", os.path.join(ROOT, "tools/claims-v3/dmcmd_audit.py"), *new], cwd=ROOT, capture_output=True, text=True)
    verdict = next((ln for ln in (r.stdout + "\n" + r.stderr).split("\n") if ln.startswith("dmcmd_audit:")), "no verdict line")
    check("dmcmd_audit.py on the five new files reads GO with no send site", r.returncode == 0 and "GO (0 send site" in verdict, verdict)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--scratch", required=True)
    ap.add_argument("--freeze", action="store_true")
    a = ap.parse_args()
    scr = os.path.abspath(a.scratch)
    if scr == ROOT or scr.startswith(ROOT + os.sep):
        sys.exit("the scratch directory must be outside the lab tree")
    os.makedirs(scr, exist_ok=True)
    say("E164 fix-pass self-test (selftest_notes_e164.py): the desk checks behind E164.md.dated-note.md (E164-A1) and README.md.dated-note.md;"
        " no device, no ssh; scratch paths are not printed")
    sec_launch(scr)
    sec_k7(scr)
    sec_others(scr)
    sec_scrub(scr)
    sec_gates(scr)
    sec_interp(scr, a.freeze)
    sec_rest(scr)
    bad = [n for n, ok in RES if not ok]
    say(f"\nRESULT: {len(RES) - len(bad)} PASS, {len(bad)} FAIL" + (": " + "; ".join(bad) if bad else ""))
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
