#!/usr/bin/env python3
"""E111 (Q133): corrections after verification. Recomputes, from committed files only, every number the corrected README cites that
no earlier committed file printed, and lists what changed. Desk only: it opens no device, writes no file and decides nothing (each
number here is a restatement of a registered one or post hoc).

    python3 docs/reports/data/2026-11-01-e111-heat-steady/corrections-check.py > docs/reports/data/2026-11-01-e111-heat-steady/corrections-check.txt

A. random fp32 on the two cards: both ran at 600 MHz (E97's README; E111's results.json A.H-F32)
B. the holds minute by minute on in-kernel samples (the scorer's own selection and fine-W mask), and c over every 5-min window
C. from rest: how much of H-I8's rise had arrived at 76 s; the 76 s line's slope against the plateau coefficient
D. E111-A3: the point estimates' ratio and the registered range
E. E111-A1 as registered (the fine W at 0.442 W/C) beside the die's own slope; H-I8's idle-reset dips, the whole hold against the plateau
F. E111.md: the edits above its Amendments section after the freeze (a8e2c969..f888c802)
G. every file committed at f888c802 under this directory and tools/claims-v3/e111, against the working tree
"""
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
REL = os.path.relpath(HERE, REPO)
TOOLS = "tools/claims-v3/e111"
sys.path.insert(0, os.path.join(REPO, TOOLS))
import reduce_e111 as S  # noqa: E402  the scorer (work_samples, fine_mask, win_stats; E = reduce_e98, imported unchanged)

FREEZE, DATA_COMMIT, LAST = "a8e2c969", "ea74a2ef", "f888c802"
RES = json.load(open(os.path.join(HERE, "results.json")))
PRED = json.load(open(os.path.join(REPO, TOOLS, "predictions-e111.json")))
A, PA = RES["A"], PRED["partA"]
HOLDS = json.loads(json.dumps(PA["holds"]))
HOLDS.update(json.load(open(os.path.join(REPO, TOOLS, "amendment-2.json")))["partA_holds_override"])  # A2: H-I8 from W1B


def r4(x):
    return None if x is None else round(x, 4)


def load(h):
    sp = HOLDS[h]
    r, procs, ws = S.work_samples(os.path.join(HERE, sp["step"]), sp["run"])
    mask, dips = S.fine_mask(ws, procs, sp["clock_mhz"])
    t0 = min(p["t_start_ms"] for p in procs)
    t1 = max(p["t_end_ms"] for p in procs)
    idle_die = (A["idles"][sp["idle_before"]]["die"] + A["idles"][sp["idle_after"]]["die"]) / 2.0
    idle_w = (A["idles"][sp["idle_before"]]["w"] + A["idles"][sp["idle_after"]]["w"]) / 2.0
    return {"sp": sp, "procs": procs, "ws": ws, "mask": mask, "dips": dips, "t0": t0, "t1": t1, "idle_die": idle_die, "idle_w": idle_w}


def stats(H, a_ms, b_ms):
    return S.win_stats(H["ws"], H["mask"], a_ms, b_ms, H["sp"]["clock_mhz"], PA["fine_min_share"])


def sect_a():
    print("A. RANDOM FP32 ON THE TWO CARDS: both ran at 600 MHz")
    p97 = "docs/reports/data/2026-11-01-e97-heat-low-power-steady/README.md"
    lines = open(os.path.join(REPO, p97), encoding="utf-8").read().splitlines()
    print(f"   {p97}:")
    for s in ("600 MHz in every sample", "TDP 0 and threshold 65 °C at every read", "reaches the lab's stop in 221 s",
              "the board 63.1 W in total (40 W over idle)", "the die still climbing 4.1 °C a minute", "settle at about 0.9 °C per board W"):
        hit = [i + 1 for i, ln in enumerate(lines) if s in ln]
        print(f"     {s!r}: {'line ' + str(hit[0]) if hit else 'NOT FOUND'}")
    p, a2 = A["H-F32"]["plateau"], A["H-F32"]["A2"]
    print(f"   E111 H-F32 (results.json A.H-F32.plateau): clock mean {p['mhz']} MHz, share at 600 MHz {p['share_clock']}, die {p['die']} C, "
          f"board {p['w']} W")
    print(f"   over its idle (A.H-F32.A2): {a2['dW_w']} W, rise {a2['rise_c']} C, c {a2['c']} C per board W; c x W over idle = "
          f"{a2['c'] * a2['dW_w']:.2f} C")
    print("   at one clock the cards differ in watts over idle (32.4 here; about 40 at aifoundry3's stop) and in C per board W (0.67; about 0.9)")


def sect_b(HS):
    print("\nB. THE HOLDS MINUTE BY MINUTE (in-kernel samples, the scorer's selection; die = the 34-sensor whole-degree mean)")
    out = {}
    for h, H in HS.items():
        n = int((H["t1"] - H["t0"]) // 60000)
        rows = []
        print(f"   {h} ({H['sp']['step']}, {H['sp']['kind']} at {H['sp']['clock_mhz']} MHz; idle mean die {H['idle_die']:.3f} C, "
              f"W {H['idle_w']:.4f}; {(H['t1'] - H['t0']) / 60000:.2f} min, {len(H['procs'])} processes):")
        for m in range(n):
            st = stats(H, H["t0"] + m * 60000, H["t0"] + (m + 1) * 60000)
            if not st:
                continue
            rows.append((m, st))
            fine = "  None " if st["fine_w"] is None else f"{st['fine_w']:7.3f}"
            print(f"     min {m:2d}-{m + 1:<2d}  die {st['die']:6.2f}  W {st['w']:6.2f}  fine W {fine}  share at clock {st['share_clock']:.3f}  "
                  f"n {st['n']}")
        out[h] = dict(rows)
        if h == "H-I8":
            spans = ((5, 9), (10, 16), (11, 15), (19, 25))
        else:
            spans = ((8, 24), (25, 25), (26, 26))
        for a, b in spans:
            v = [out[h][m]["die"] for m in range(a, b + 1) if m in out[h]]
            print(f"     die over minutes {a}-{b} (bins {a}-{a + 1} .. {b}-{b + 1}): {min(v):.2f} .. {max(v):.2f}, mean {sum(v) / len(v):.2f}")
        if h == "H-I8":
            lvl = sum(out[h][m]["die"] for m in range(5, 10)) / 5
            low = min(out[h][m]["die"] for m in range(10, 17))
            back = sum(out[h][m]["die"] for m in range(19, 26)) / 7
            print(f"     the dip: level at minutes 5-9 {lvl:.2f}, lowest bin in 10-16 {low:.2f} ({lvl - low:.2f} C down), "
                  f"minutes 19-25 {back:.2f} ({back - low:.2f} C back)")
        else:
            lvl = sum(out[h][m]["die"] for m in range(8, 25)) / 17
            print(f"     the step: minutes 8-24 mean {lvl:.2f}; minute 25 {out[h][25]['die'] - lvl:+.2f} C, minute 26 {out[h][26]['die'] - lvl:+.2f} C")
        cs = []
        for s in range(5, n - 4):
            st = stats(H, H["t0"] + s * 60000, H["t0"] + (s + 5) * 60000)
            c = (st["die"] - H["idle_die"]) / (st["w"] - H["idle_w"])
            cs.append((s, c))
        plat = stats(H, H["t1"] - PA["plateau_s"] * 1000, H["t1"] + 1)
        cp = (plat["die"] - H["idle_die"]) / (plat["w"] - H["idle_w"])
        print(f"     c in every 5-min window from minute 5 (start minute: c): " + ", ".join(f"{s}: {c:.3f}" for s, c in cs))
        print(f"     c over those windows {min(c for _, c in cs):.3f} .. {max(c for _, c in cs):.3f}; the registered plateau (last 300 s) "
              f"{cp:.4f}, results.json A.{h}.A2.c {A[h]['A2']['c']}")
    return out


def sect_c(HS):
    print("\nC. FROM REST: H-I8's rise at 76 s (the length of E98's sustained runs), and the 76 s line's slope against c")
    H = HS["H-I8"]
    rise = A["H-I8"]["A2"]["rise_c"]
    for a, b in ((75, 77), (74, 78), (71, 81)):
        st = stats(H, H["t0"] + a * 1000, H["t0"] + b * 1000)
        print(f"   die over {a}-{b} s from the first process: {st['die']:.2f} C (n {st['n']}); over the idle {st['die'] - H['idle_die']:.2f} C = "
              f"{100 * (st['die'] - H['idle_die']) / rise:.1f}% of the plateau's {rise} C rise")
    k = PRED["partB"]["e98_constants"]["k_line_c_per_w"]
    for h in ("H-I8", "H-F32"):
        print(f"   the 76 s line's slope {k} (predictions-e111.json partB.e98_constants.k_line_c_per_w) / c({h}) {A[h]['A2']['c']} = "
              f"{k / A[h]['A2']['c']:.3f}: a ratio of slopes, not an arrival share")


def sect_d():
    print("\nD. E111-A3: the point estimates and the registered range")
    ci, cf = A["H-I8"]["A2"]["c"], A["H-F32"]["A2"]["c"]
    a3 = A["A3"]
    print(f"   c(H-F32) / c(H-I8) = {cf} / {ci} = {cf / ci:.5f}: the point estimates differ by {100 * abs(1 - cf / ci):.2f}%")
    print(f"   registered range (results.json A.A3, from the two ranges' extremes; a range, not an interval): [{a3['lo']}, {a3['hi']}], "
          f"band {a3['band']}, {a3['verdict']}")
    for h in ("H-I8", "H-F32"):
        x = A[h]["A2"]
        print(f"   c({h}) {x['c']}, range [{x['c_lo']}, {x['c_hi']}] over {{idle before, after, mean}} x {{plateau, previous}} (E111.md, Part A)")


def sect_e(HS):
    print("\nE. E111-A1 AS REGISTERED, and the dips' scope")
    k, bar = PA["k_fine_w_per_c"], PA["steady_bar_c_per_min"]
    for h in ("H-I8", "H-F32"):
        x = A[h]["A1"]
        print(f"   {h}: read on {x['read_on']!r}: fine W {x['fine_slope_w_per_min']:+.5f} W/min / {k} W/C = {x['fine_slope_c_per_min']:+.4f} C/min "
              f"(se {x['fine_slope_se']}) against |slope| <= {bar}: {x['verdict']}; beside, the die's own slope {x['die_slope_c_per_min']:+.4f} "
              f"(se {x['die_slope_se']})")
    H = HS["H-I8"]
    pa, pb = H["t1"] - PA["plateau_s"] * 1000, H["t1"]
    ramp = S.DIP_RAMP_S * 1000
    inplat = [d for d in H["dips"] if d["t1"] + ramp >= pa and d["t0"] <= pb]
    clock = H["sp"]["clock_mhz"]
    share_all = sum(1 for x in H["ws"] if x["mhz"] == clock) / len(H["ws"])
    print(f"   H-I8 idle-reset dips (the scorer's find_dips): {len(H['dips'])} over the whole hold (results.json A.H-I8.dips "
          f"{A['H-I8']['dips']}), {len(inplat)} touching the plateau's last 300 s")
    print(f"   H-I8 share of in-kernel samples at {clock} MHz: {share_all:.4f} over the whole hold, {A['H-I8']['plateau']['share_clock']} in the "
          f"plateau (results.json A.H-I8.plateau.share_clock)")


def git(*a):
    return subprocess.run(["git", "-C", REPO] + list(a), capture_output=True, text=True, check=True,
                          env=dict(os.environ, TZ="America/Los_Angeles")).stdout


def sect_f():
    print(f"\nF. E111.md: edits above its '## Amendments' after the freeze ({FREEZE}..{LAST})")
    path = TOOLS + "/E111.md"
    for ln in git("log", "--reverse", "--format=%h %ad", "--date=format:%H:%M:%S", f"{FREEZE}..{LAST}", "--", path).split("\n"):
        if not ln.strip():
            continue
        c, t = ln.split()
        new, old = git("show", f"{c}:{path}").splitlines(), git("show", f"{c}^:{path}").splitlines()
        am_new = next(i for i, x in enumerate(new) if x.startswith("## Amendments")) + 1
        am_old = next(i for i, x in enumerate(old) if x.startswith("## Amendments")) + 1
        above, below = [], 0
        for h in git("diff", "-U0", f"{c}^", c, "--", path).splitlines():
            if not h.startswith("@@"):
                continue
            o, n = h.split()[1][1:], h.split()[2][1:]
            os_, ol = (int(o.split(",")[0]), int(o.split(",")[1]) if "," in o else 1)
            ns_, nl = (int(n.split(",")[0]), int(n.split(",")[1]) if "," in n else 1)
            for i in range(os_, os_ + ol):
                (above.append(("-", i, old[i - 1])) if i < am_old else None)
                below += 0 if i < am_old else 1
            for i in range(ns_, ns_ + nl):
                (above.append(("+", i, new[i - 1])) if i < am_new else None)
                below += 0 if i < am_new else 1
        print(f"   {c} ({t} PST): {len(above)} line(s) above Amendments, {below} at or below it")
        for s, i, x in above:
            print(f"     {s} line {i}: {x[:150]}{' ...' if len(x) > 150 else ''}")


def sect_g():
    print(f"\nG. FILES: what is committed at {LAST} under {REL}/ and {TOOLS}/, against the working tree")
    at_last = git("ls-tree", "-r", "--name-only", LAST, "--", REL, TOOLS).split()
    st = [x.split("\t") for x in git("diff", "--name-status", LAST, "--", REL, TOOLS).splitlines() if x.strip()]
    changed = [p for s, p in st if s == "M"]
    added = sorted(set([p for s, p in st if s == "A"] + git("ls-files", "--others", "--exclude-standard", "--", REL, TOOLS).split()))
    gone = [p for s, p in st if s == "D"]
    for d in (REL, TOOLS):
        n = [p for p in at_last if p.startswith(d + "/")]
        c = [p for p in changed if p.startswith(d + "/")]
        print(f"   {d}/: {len(n) - len(c)} of {len(n)} files unchanged since {LAST}; changed: {', '.join(os.path.relpath(p, d) for p in c) or 'none'}")
    print(f"   added since {LAST}: {', '.join(added) or 'none'}; removed: {', '.join(gone) or 'none'}")
    print(f"   manifest.sha256 records the files as committed in {DATA_COMMIT}; its README.md line is that version's")


def main():
    HS = {h: load(h) for h in ("H-I8", "H-F32")}
    for h, H in HS.items():
        ok = (H["t0"], H["t1"], len(H["dips"])) == (A[h]["t_start_ms"], A[h]["t_end_ms"], A[h]["dips"])
        print(f"check {h}: the scorer's span and dips reproduce results.json: {ok}")
    sect_a()
    sect_b(HS)
    sect_c(HS)
    sect_d()
    sect_e(HS)
    sect_f()
    sect_g()


if __name__ == "__main__":
    main()
