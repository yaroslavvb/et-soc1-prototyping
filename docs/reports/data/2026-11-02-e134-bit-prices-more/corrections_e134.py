#!/usr/bin/env python3
"""E134, corrections after verification (Mon 2 Nov 2026): the evidence for C1-C6 of README.md's § Corrections after
verification. POST HOC, labelled, no verdict: nothing here is a registered arm, and no registered file is changed.

Committed files only. Desk compute: run it at a desk machine from anywhere in the lab repository, with a Python that has
numpy (the registered reducer's own requirement), and keep its output beside it:

    python3 docs/reports/data/2026-11-02-e134-bit-prices-more/corrections_e134.py \\
        > docs/reports/data/2026-11-02-e134-bit-prices-more/corrections_e134.txt

[A] C1, the dip line. The registered reduction (reduce_e134.py, reduce_e78.py unchanged) and scorer (score_e134.py), run
    unchanged over the committed raw blocks, except E82 A2's dip line DIP_W, set in memory: 4.0 W is the registered line
    and must reproduce scored.json's primary exactly (the control); 3.0 and 2.0 W are the post-hoc lines. Outputs go to
    build/e134-corrections/ (not committed).
[B] C1, the meter dips of 2-4 W inside the runs' windows ([t0 + 1 s, t0 + 3 s), reduce_e78.py's), and the train gate's
    deviations of the A blocks' zero reads at the 4 W and 2 W lines.
[C] C2, the fp32 positions run in both layouts (all-in j and balanced p items), E102 and E134, and what is still open.
[D] C5, the radix-4 Booth digits each low A bit changes on W79 and W67, and the measured word difference against the
    frozen bench's at every bit.
[E] C6, the ettelem binary's source: its sha256 in logs/binaries.sha256, de262730's and the reviewed source's sha256,
    and the four functions that send device-management commands, compared byte for byte.
[F] C4 and C5, the lines quoted: R2 at every arm (score.log) and E102's B-side ratio rows (its results.md).
SPDX-License-Identifier: Apache-2.0
"""
import csv
import glob
import gzip
import hashlib
import json
import os
import re
import subprocess
import sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
TOP = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
DREL = "docs/reports/data/2026-11-02-e134-bit-prices-more"
E = "tools/claims-v3/e134"
OUT = "build/e134-corrections"
LINES = ("4.0", "3.0", "2.0")


def rel(p):
    return os.path.relpath(p, TOP)


def reduce_at(dip, out, dirs):
    """One reduction at dip line `dip`: reduce_e134.main() with its module's DIP_W set in memory (no file changed)."""
    sys.path.insert(0, os.path.join(TOP, E))
    import reduce_e134  # noqa: E402
    reduce_e134.DIP_W = float(dip)
    sys.argv = ["reduce_e134.py"] + dirs + ["--drop-dips", "--no-refit", "--out", f"{out}/e134.json",
                                            "--csv", f"{out}/runs.csv", "--txt", f"{out}/reduce.txt"]
    reduce_e134.main()


def flat(x, pre=""):
    out = {}
    if isinstance(x, dict):
        for k, v in x.items():
            out.update(flat(v, f"{pre}/{k}"))
    elif isinstance(x, list):
        for i, v in enumerate(x):
            out.update(flat(v, f"{pre}/{i}"))
    else:
        out[pre] = x
    return out


def iv(c):
    return f"{c['mean']:+.3f} [{c['lo']:+.3f}, {c['hi']:+.3f}] (n = {c.get('n')})"


def steps(runs_csv, red_json, gate=True):
    sys.path.insert(0, os.path.join(TOP, E))
    import score_e134 as s  # noqa: E402
    tiles = json.load(open(os.path.join(TOP, E, "e134", "e134-tiles.json")))["tiles"]
    reg = json.load(open(os.path.join(TOP, E, "predictions-e134.json")))
    return s.Book(s.load_runs(runs_csv), tiles, value="p_raw", gate=gate, gate_w=reg["plan"]["train_gate_w"],
                  red=json.load(open(red_json)))


def section_a(dirs):
    print("[A] C1 - the dip line, post hoc (the registered reducer and scorer; only DIP_W moved, in memory)")
    com = json.load(open(os.path.join(TOP, DREL, "scored.json")))["primary"]
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
    for dip in LINES:
        o = f"{OUT}/dip{dip}"
        os.makedirs(os.path.join(TOP, o), exist_ok=True)
        r1 = subprocess.run([sys.executable, os.path.abspath(__file__), "--reduce-at", dip, o] + dirs, cwd=TOP, env=env,
                            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL).returncode
        r2 = subprocess.run([sys.executable, f"{E}/score_e134.py", "--primary", f"{o}/runs.csv,{o}/e134.json",
                             "--md", f"{o}/results.md", "--json", f"{o}/scored.json"], cwd=TOP, env=env,
                            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL).returncode
        s = json.load(open(os.path.join(TOP, o, "scored.json")))["primary"]
        red = json.load(open(os.path.join(TOP, o, "e134.json")))
        dd = {k: v["samples_removed"] for k, v in red["reducer"]["dip_samples_removed"].items()}
        tag = "  (the registered line: the control)" if dip == "4.0" else "  (post hoc)"
        print(f"\n  DIP_W = {dip} W{tag}; reduce rc {r1}, score rc {r2}")
        per = ", ".join(f"{k} {v}" for k, v in sorted(dd.items()))
        print(f"    meter-dip samples removed: {sum(dd.values())} ({per})")
        print(f"    blocks kept: A {s['blocks']['A']}, B {s['blocks']['B']}; set aside: "
              f"{[(x['pass'], x['why']) for x in s['set_aside']] or 'none'}")
        print("    verdicts: " + ", ".join(f"{k} {v.get('verdict')}" for k, v in s["rules"].items()))
        c = s["statistics"]["contrasts_W"]
        r2d = s["rules"]["E134-R2"]["detail"]
        print(f"    E134-R2, W67 - W79 at bit 6, all-in: {r2d['mean']:+.3f} [{r2d['lo']:+.3f}, {r2d['hi']:+.3f}] W "
              f"(n = {r2d['n']}); per block {', '.join(f'{b} {v:.3f}' for b, v in r2d['per_block'].items())}; "
              f"the WORD line 0.262 W")
        three = [r2d["per_block"][b] for b in ("13411", "13412", "13413") if b in r2d["per_block"]]
        if len(three) == 3:
            m = sum(three) / 3
            se = (sum((v - m) ** 2 for v in three) / 2) ** 0.5 / 3 ** 0.5
            print(f"    E134-R2 over the three blocks the registered primary kept (13411-13413) only: {m:+.3f} "
                  f"[{m - 4.303 * se:+.3f}, {m + 4.303 * se:+.3f}] W (t(2) = 4.303)")
        print(f"    balanced twin, A_word_bal_6: {iv(c['A_word_bal_6'])} W")
        for k in ("0", "6"):
            x = s["rules"]["E134-R1"]["detail"][k]
            print(f"    E134-R1, W79 bit {k} all-in / balanced: {x['ratio']:.2f} [{x['lo']:.2f}, {x['hi']:.2f}]")
        x = s["rules"]["E134-R3"]["detail"]
        print(f"    E134-R3, W67 bit 6 all-in / balanced: {x['ratio']:.2f} [{x['lo']:.2f}, {x['hi']:.2f}]")
        for k in ("aj_6", "a67j_6"):
            w, f = s["prices"][k]["W"], s["prices"][k]["fJ"]
            print(f"    {k}: {w['mean']:.3f} [{w['lo']:.3f}, {w['hi']:.3f}] W, {f['mean']:.0f} [{f['lo']:.0f}, {f['hi']:.0f}] fJ a flip")
        b = steps(os.path.join(TOP, o, "runs.csv"), os.path.join(TOP, o, "e134.json"), gate=False)
        for it in ("fp32.aj_6", "fp32.a67j_6", "fp32.ap_6", "fp32.a67p_6"):
            st = b.steps.get(it, {}).get("W", {})
            print(f"    step per block, train gate off ({it}, W): " + ", ".join(f"{p} {v:.3f}" for p, v in sorted(st.items())))
        fs, fc = flat(s), flat(com)
        bk = [k for k in fc if "/prices/b" in k or "/contrasts_W/B_" in k or "B_allin_over_bal" in k]
        print(f"    B numbers (prices b*, contrasts B_*, ratios B_*) equal to the committed primary: "
              f"{sum(fs.get(k) == fc.get(k) for k in bk)} of {len(bk)}")
        if dip == "4.0":
            same = sum(fs.get(k) == fc.get(k) for k in fc)
            rc = open(os.path.join(TOP, o, "runs.csv"), "rb").read() == open(os.path.join(TOP, DREL, "runs.csv"), "rb").read()
            print(f"    CONTROL: scored.json primary leaves equal to the committed: {same} of {len(fc)}; "
                  f"runs.csv byte-identical to the committed: {rc}")


def section_b():
    print("\n[B] C1 - the meter dips of 2-4 W inside run windows (committed telemetry, dips kept), and the train gate")
    tiles = json.load(open(os.path.join(TOP, E, "e134", "e134-tiles.json")))["tiles"]
    runs = list(csv.DictReader(open(os.path.join(TOP, DREL, "runs.csv"))))
    scored = [r for r in runs if r["fail"] in ("0", "False") and r["item"] in tiles and r["segment"] != "-1"]
    hits_all = hits_scored = 0
    for p in sorted({r["pass"] for r in runs}):
        tel = [json.loads(ln) for ln in gzip.open(os.path.join(TOP, DREL, f"aifoundry3/kinds/p{p}/telemetry.jsonl.gz"), "rt")]
        t, B = [x["t_ms"] for x in tel], [x["board_w"] for x in tel]
        dips = [(t[i], min(B[i - 2], B[i + 2]) - B[i], B[i]) for i in range(2, len(B) - 2)
                if None not in (B[i], B[i - 2], B[i + 2]) and B[i] < min(B[i - 2], B[i + 2]) - 2.0]
        for r in runs:
            if r["pass"] != p or r["fail"] not in ("0", "False"):
                continue
            t0 = float(r["t0_ms"])
            inw = [(round((ti - t0) / 1000, 2), round(d, 2), round(bw, 2)) for ti, d, bw in dips if t0 + 1000 <= ti < t0 + 3000]
            if [x for x in inw if x[1] <= 4.0]:
                hits_all += 1
                sc = r in scored
                hits_scored += sc
                print(f"  {p} pos {r['pos']} {r['item']}{'' if sc else ' (a settling run, not scored)'}: dips in the window "
                      f"(s after t0, depth below min(i-2, i+2) in W, board W): {inw}; p_raw {float(r['p_raw']):.3f} W")
    print(f"  runs (not failed): {len(runs)}, of which scored (a tile item, not a settling run): {len(scored)}; "
          f"with a 2-4 W dip in the window: {hits_all} runs, {hits_scored} of them scored")
    for dip in ("4.0", "2.0"):
        rows = list(csv.DictReader(open(os.path.join(TOP, OUT, f"dip{dip}", "runs.csv"))))
        print(f"  the train gate at the {dip} W line: A-block zero reads more than 0.15 W off the line through their "
              f"neighbours (the gate is 0.25 W)")
        n = 0
        for p in ("13410", "13411", "13412", "13413"):
            zs = {}
            for r in rows:
                if r["pass"] == p and r["fail"] in ("0", "False") and r["item"] in tiles and r["segment"] != "-1" \
                        and tiles[r["item"]]["zero"] is None:
                    zs.setdefault(r["item"], []).append(r)
            for z, rd in sorted(zs.items()):
                rd.sort(key=lambda r: float(r["t0_ms"]))
                for a, b, c in zip(rd, rd[1:], rd[2:]):
                    pa, pb, pc = float(a["p_raw"]), float(b["p_raw"]), float(c["p_raw"])
                    ta, tb, tc = float(a["t0_ms"]), float(b["t0_ms"]), float(c["t0_ms"])
                    dev = pb - (pa + (pc - pa) * (tb - ta) / max(tc - ta, 1.0))
                    if abs(dev) > 0.15:
                        n += 1
                        print(f"    {p} {z} pos {b['pos']}: {dev:+.3f} W off its line (p_raw {pb:.3f} W)")
        if not n:
            print("    none")


def positions(path, fams):
    names = json.load(open(path))["tiles"]
    pos = {f: set() for f in fams}
    for n in names:
        m = re.match(r"fp32\.([a-z0-9]+?)_(\d+)$", n)
        if m and m.group(1) in pos:
            pos[m.group(1)].add(int(m.group(2)))
    return pos


def ranges(xs):
    xs, out = sorted(xs), []
    for x in xs:
        if out and x == out[-1][1] + 1:
            out[-1][1] = x
        else:
            out.append([x, x])
    return ", ".join(f"{a}" if a == b else f"{a}-{b}" for a, b in out) or "none"


def section_c():
    print("\n[C] C2 - fp32 positions run in both layouts (all-in j and balanced p), and what is still open")
    e102 = positions(os.path.join(TOP, "tools/claims-v3/kinds/e102/e102.json"), ("aj", "ap", "bj", "bp"))
    e134 = positions(os.path.join(TOP, E, "e134", "e134-tiles.json"), ("aj", "ap", "a67j", "a67p", "bj", "bp"))
    for f, v in sorted(e102.items()):
        print(f"  E102 (card 1) {f}: {ranges(v)}")
    for f, v in sorted(e134.items()):
        print(f"  E134 (aifoundry3) {f}: {ranges(v)}")
    allp = set(range(32))
    b = (e102["bj"] & e102["bp"]) | (e134["bj"] & e134["bp"])
    a79 = (e102["aj"] & e102["ap"]) | (e134["aj"] & e134["ap"])
    a67 = e134["a67j"] & e134["a67p"]
    print(f"  B, both layouts: {ranges(b)}; open: {ranges(allp - b)}")
    print(f"  A on W79 (E102's and E134's word), both layouts: {ranges(a79)}; open: {ranges(allp - a79)}")
    print(f"  A on W67, both layouts: {ranges(a67)}; open: {ranges(allp - a67)}")
    print(f"  measured in both layouts for the first time by E134: B {ranges((e134['bj'] & e134['bp']) - (e102['bj'] & e102['bp']))}")


def digits(w):
    sig = (w & 0x7FFFFF) | 0x800000
    b = lambda i: (sig >> i) & 1 if i >= 0 else 0  # noqa: E731
    return [-2 * b(2 * k + 1) + b(2 * k) + b(2 * k - 1) for k in range(13)]


def section_d():
    print("\n[D] C5 - the radix-4 Booth digits each low A bit changes (b-1 = 0, digits d0-d12 of the 24-bit significand)")
    words = {"W79": 0x3FBD207C, "W67": 0x3FBBC9E4}
    com = json.load(open(os.path.join(TOP, DREL, "scored.json")))["primary"]["statistics"]["contrasts_W"]
    pred = json.load(open(os.path.join(TOP, E, "predictions-e134.json")))["contrasts_pred_W"]
    side = lambda d: "neg" if d < 0 else "zero-or-pos"  # noqa: E731
    for j in range(8):
        parts = []
        for nm, w in words.items():
            d0, d1 = digits(w), digits(w ^ (1 << j))
            ch = [(k, d0[k], d1[k]) for k in range(13) if d0[k] != d1[k]]
            cross = any(side(a) != side(c) for _, a, c in ch)
            parts.append(f"{nm} " + "; ".join(f"d{k} {a:+d} -> {c:+d}" for k, a, c in ch) +
                         f" ({'crosses' if cross else 'keeps its side'})")
        c = com[f"A_word_allin_{j}"]
        bench = pred[f"A_word_allin_{j}"]["bench"]
        res = c["lo"] > 0 or c["hi"] < 0
        same = res and (c["mean"] > 0) == (bench > 0)
        print(f"  bit {j}: {' | '.join(parts)}")
        print(f"      W67 - W79 all-in {iv(c)} W, bench {bench:+.3f}: "
              + (f"resolves, {'with' if same else 'against'} the bench's sign, measured / bench {c['mean'] / bench:.2f}"
                 if res else "does not resolve"))


def fn_body(src, pat):
    lines = src.split("\n")
    for i, ln in enumerate(lines):
        if re.search(pat, ln):
            depth, out, started = 0, [], False
            for l2 in lines[i:]:
                out.append(l2)
                depth += l2.count("{") - l2.count("}")
                started = started or "{" in l2
                if started and depth <= 0:
                    return "\n".join(out)
    return None


def section_e():
    print("\n[E] C6 - the ettelem binary's source")
    for ln in open(os.path.join(TOP, DREL, "logs", "binaries.sha256")):
        if "ettelem" in ln:
            print(f"  logs/binaries.sha256 (read on aifoundry3 at the session's setup): {ln.split()[0][:16]}... {ln.split()[1]}")
    src = {}
    for rev in ("de262730", "efa3e8cd"):
        txt = subprocess.run(["git", "-C", TOP, "show", f"{rev}:tools/ettelem/ettelem.cpp"], capture_output=True,
                             text=True).stdout
        src[rev] = txt
        when = subprocess.run(["git", "-C", TOP, "log", "-1", "--format=%ad", "--date=iso", rev], capture_output=True,
                              text=True).stdout.strip()
        print(f"  tools/ettelem/ettelem.cpp at {rev} ({when}): sha256 {hashlib.sha256(txt.encode()).hexdigest()[:16]}...")
    pats = {"config()": r"^int config\(Dm& d\) \{", "sample()": r"^int sample\(Dm& d,",
            "Dm::get()": r"template <class T> bool get\(", "Dm::resetStats()": r"bool resetStats\(\) \{"}
    for nm, pat in pats.items():
        a, b = fn_body(src["de262730"], pat), fn_body(src["efa3e8cd"], pat)
        cmds = sorted(set(re.findall(r"DM_CMD_[A-Z_]+", a or "")))
        print(f"  {nm}: de262730 against the reviewed efa3e8cd: {'byte-identical' if a and a == b else 'DIFFERS'}; names {cmds}")
    layer = re.compile(r"createPcieDeviceLayer\([^)]*\)[^;]*;[^\n]*")
    for rev in ("de262730", "efa3e8cd"):
        found = layer.findall(src[rev])
        print(f"  {rev}: the device layer Dm opens: {found}")
    print("  E127's record of the build: tools/claims-v3/e127/README.md, the paragraph naming de262730")
    m = re.search(r"loglevel[^\n]*\((DM_CMD_[A-Z_]+)\)", src["de262730"])
    print(f"  de262730's loglevel subcommand sends {m.group(1) if m else '?'} (a WRITE); the calls of loglevel or sptrace "
          f"in E134's scripts and lib.sh:")
    callers = sorted(glob.glob(os.path.join(TOP, E, "*.sh")) + glob.glob(os.path.join(TOP, E, "*.py"))) + \
        [os.path.join(TOP, "tools/claims-v3/lib.sh")]
    n = 0
    for f in callers:
        for i, ln in enumerate(open(f), 1):
            if re.search(r"\b(loglevel|sptrace)\b", ln):
                n += 1
                print(f"    {rel(f)}:{i}: {ln.strip()}")
    print(f"    {n} lines in {len(callers)} files")
    vals, nsamp = {}, 0
    for f in sorted(glob.glob(os.path.join(TOP, DREL, "aifoundry3/kinds/*/telemetry.jsonl.gz"))):
        for ln in gzip.open(f, "rt"):
            v = json.loads(ln).get("since_reset_ms")
            vals[v] = vals.get(v, 0) + 1
            nsamp += 1
    print(f"  since_reset_ms over every committed telemetry sample (the nine blocks and the smoke): {nsamp} samples, "
          f"values {vals}")


def section_f():
    print("\n[F] the lines quoted")
    for ln in open(os.path.join(TOP, DREL, "score.log")):
        if ln.startswith("E134-R2"):
            print(f"  score.log: {ln.strip()}")
    for ln in open(os.path.join(TOP, "docs/reports/data/2026-11-01-e102-balanced-bit-prices/results.md")):
        if ln.startswith("| fp32 B |"):
            print(f"  E102 results.md: {ln.strip()}")


def main():
    if len(sys.argv) > 1 and sys.argv[1] == "--reduce-at":
        return reduce_at(sys.argv[2], sys.argv[3], sys.argv[4:])
    os.chdir(TOP)
    dirs = [rel(d) for d in sorted(glob.glob(os.path.join(TOP, DREL, "aifoundry3/kinds/p134[1-2][0-9]")))
            if '"status":"ok"' in open(os.path.join(d, "block.json")).read()]
    print(f"E134 corrections after verification: post hoc, labelled, no verdict. Blocks: {', '.join(os.path.basename(d) for d in dirs)}")
    print("Registered files read unchanged: " + ("yes" if subprocess.run(
        ["git", "-C", TOP, "diff", "--quiet", "af56740a", "HEAD", "--", E + "/predictions-e134.json", E + "/reduce_e134.py",
         E + "/score_e134.py", E + "/e134_common.py", E + "/e134", "tools/claims-v3/kinds"]).returncode == 0 else "NO")
          + " (git diff af56740a HEAD on the scorer, the reducer, the items and the tiles)\n")
    section_a(dirs)
    section_b()
    section_c()
    section_d()
    section_e()
    section_f()


if __name__ == "__main__":
    main()
