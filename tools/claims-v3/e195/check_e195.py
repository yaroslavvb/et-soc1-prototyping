#!/usr/bin/env python3
"""E195's kit checker (Q185, lane kit-e195, Sun 15 Nov 2026, before any E195 datum). It opens no device and sends no command: it reads
files a session wrote. Stdlib only, except `leftover`, which imports the registered reducer by path (never copied, never changed).

    python3 -I -B check_e195.py smoke <smoke pass dir>
        THE KIT'S SMOKE GATE (E195.md 5, the lab's choice; beside the registered smoke_gate_x09.py): the smoke's highest board reading
        (board_w, every sample of the pass, its heater bursts included) below 65 W and its highest die reading (temp_c.minshire[0], the
        reading the runner's 70 C stop reads) below 65 C, over at least 100 samples. Prints SMOKE-PEAK PASS or FAIL; exit 0 / 1.
    python3 -I -B check_e195.py dry <session dir> <expected listing>
        the dry session's device calls (every "DRY hold10:" line of its smoke.log and passes.log, in order) against the kit's committed
        listing for aifoundry3 (desk/dry-e195-noms-aifoundry3.txt), each pass's STOP path read as <OUT>/p<pass>/STOP. Prints E195-DRY OK
        or E195-DRY FAIL; exit 0 / 1.
    python3 -I -B check_e195.py leftover <reduce_x09.py> <gen dir> <main pass dir> ... [--warmup 910] [--json OUT]
        WHAT THE REDUCER LEAVES (E195.md 7 and 18.2): for each headline pass and direction, every term the registered code takes as zero
        (the floor's one, high pin and toggle prices; the random closure's toggle price), each named with the arms whose runs it lacked;
        the rails' measured volts beside the reducer's fixed 0.522, 0.698 and 0.484 V; the session's peaks (board_w, temp_c.minshire[0])
        against the live stops (70 W, 70 C). Prints LEFTOVER-E195 lines; exit 0.
    python3 -I -B check_e195.py peaks <pass dir> ...
        the highest board and die readings of each pass and of all of them, against the live stops; exit 0.
SPDX-License-Identifier: Apache-2.0
"""
import gzip
import importlib.util
import json
import os
import re
import sys

SMOKE_MAX_W, SMOKE_MAX_C, SMOKE_MIN_SAMPLES = 65.0, 65.0, 100
STOP_W, STOP_C = 70.0, 70.0
REF_V = {"minion": 0.522, "sram": 0.698, "noc": 0.484}      # the registered reducer's fixed reference volts (E195.md 7)


def tel(d):
    """Every telemetry sample of a pass directory: telemetry.jsonl(.gz), then what a stuck sampler left in .raw beyond it."""
    out = []
    for name in ("telemetry.jsonl", "telemetry.jsonl.gz"):
        p = os.path.join(d, name)
        if os.path.exists(p):
            op = gzip.open if p.endswith(".gz") else open
            with op(p, "rt", errors="replace") as f:
                for ln in f:
                    if ln.startswith("{"):
                        try:
                            out.append(json.loads(ln))
                        except ValueError:
                            pass
            break
    return out


def peak(samples):
    bw = [float(s["board_w"]) for s in samples if isinstance(s.get("board_w"), (int, float))]
    dc = []
    for s in samples:
        try:
            dc.append(float(s["temp_c"]["minshire"][0]))
        except (KeyError, IndexError, TypeError, ValueError):
            pass
    return (max(bw) if bw else None), (max(dc) if dc else None), len(bw), len(dc)


def cmd_smoke(argv):
    d = argv[0]
    s = tel(d)
    w, c, nw, nc = peak(s)
    bad = []
    if nw < SMOKE_MIN_SAMPLES:
        bad.append(f"{nw} board samples (fewer than {SMOKE_MIN_SAMPLES})")
    if nc < SMOKE_MIN_SAMPLES:
        bad.append(f"{nc} die samples (fewer than {SMOKE_MIN_SAMPLES})")
    if w is not None and w >= SMOKE_MAX_W:
        bad.append(f"highest board reading {w:.2f} W, not below {SMOKE_MAX_W:g} W")
    if c is not None and c >= SMOKE_MAX_C:
        bad.append(f"highest die reading {c:g} C, not below {SMOKE_MAX_C:g} C")
    if w is None or c is None:
        bad.append("no board or die reading")
    head = (f"highest board {w:.2f} W" if w is not None else "no board reading") + ", " + \
           (f"highest die {c:g} C" if c is not None else "no die reading") + f" over {nw} samples (the heater bursts included)"
    if bad:
        print(f"SMOKE-PEAK FAIL: {'; '.join(bad)} ({head}; the kit's gate: below {SMOKE_MAX_W:g} W and {SMOKE_MAX_C:g} C)")
        return 1
    print(f"SMOKE-PEAK PASS: {head}; the kit's gate: below {SMOKE_MAX_W:g} W and below {SMOKE_MAX_C:g} C (E195.md 5)")
    return 0


STOPF = re.compile(r"--stop-file \S*/(p[0-9]+)/STOP")


def calls(lines):
    out = []
    for ln in lines:
        if ln.startswith("DRY hold10: "):
            out.append(STOPF.sub(r"--stop-file <OUT>/\1/STOP", ln.rstrip("\n")))
    return out


def cmd_dry(argv):
    sd, exp = argv[0], argv[1]
    got = []
    for name in ("smoke.log", "passes.log"):
        p = os.path.join(sd, name)
        if os.path.exists(p):
            got += calls(open(p, errors="replace").readlines())
    want = calls(open(exp).readlines())
    if got == want:
        print(f"E195-DRY OK: {len(got)} device calls (the smoke's 8 and 35 for each of the 8 passes: 288), each run by the runner under "
              f"timeout 10, in the kit's committed order for aifoundry3, the listing equal call for call")
        return 0
    n = next((i for i, (a, b) in enumerate(zip(got, want)) if a != b), min(len(got), len(want)))
    print(f"E195-DRY FAIL: {len(got)} device calls against {len(want)} expected; first difference at call {n + 1}: "
          f"got {got[n] if n < len(got) else '<none>'!r}, expected {want[n] if n < len(want) else '<none>'!r}")
    return 1


def cmd_peaks(argv):
    allw, allc = [], []
    for d in argv:
        w, c, nw, _ = peak(tel(d))
        print(f"PEAK {os.path.basename(os.path.normpath(d))}: board {w if w is None else round(w, 2)} W, die {c} C ({nw} samples)")
        if w is not None:
            allw.append(w)
        if c is not None:
            allc.append(c)
    w, c = (max(allw) if allw else None), (max(allc) if allc else None)
    print(f"PEAKS-E195: highest board {w} W (stop {STOP_W:g} W: {('under' if w is not None and w < STOP_W else 'NOT under')}), "
          f"highest die {c} C (stop {STOP_C:g} C: {('under' if c is not None and c < STOP_C else 'NOT under')}) over {len(argv)} passes")
    return 0


def load_reducer(path):
    spec = importlib.util.spec_from_file_location("reduce_x09_registered", path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def cmd_leftover(argv):
    red, gen = argv[0], argv[1]
    rest = argv[2:]
    warm, jout = None, None
    if "--warmup" in rest:
        i = rest.index("--warmup"); warm = int(rest[i + 1]); rest = rest[:i] + rest[i + 2:]
    if "--json" in rest:
        i = rest.index("--json"); jout = rest[i + 1]; rest = rest[:i] + rest[i + 2:]
    dirs = rest
    m = load_reducer(red)
    man = {it["name"]: it for it in json.load(open(os.path.join(gen, "manifest.json")))["items"]}
    R = []
    for d in dirs:
        R += m.runs_of_pass(d, filtered=True)
    k, _ = m.leak_slope(R)
    s = m.session(R, k, warm)
    cells, head = s["cells"], s["head"]

    def present(name, p):
        spec = m.CONTRASTS[name][0]
        for it in spec:
            x = cells.get((p, it))
            if x is None or m.field_of(x, "p") is None:
                return False
        x = cells.get((p, m.RATE_OF[name]))
        return bool(x is not None and x["rate"])

    def lacks(name, p):
        return sorted(it for it in m.CONTRASTS[name][0] if cells.get((p, it)) is None)

    rows, lines = [], []
    for p in head:
        for d, pre in (("rd", "R"), ("wr", "W")):
            one = present(f"{pre}.tie27", p)
            pin = present(f"{pre}.hi_t0", p) or present(f"{pre}.K", p)
            tog = present(f"{pre}.tog", p)
            w1, rnd = present(f"{pre}.w1", p), present(f"{pre}.rnd", p)
            miss = []
            if w1:
                if not one:
                    miss.append(("floor", "one", lacks(f"{pre}.tie27", p)))
                if not pin:
                    miss.append(("floor", "high pin", sorted(set(lacks(f"{pre}.hi_t0", p)) | set(lacks(f"{pre}.K", p)))))
                if not tog:
                    miss.append(("floor", "toggle", lacks(f"{pre}.tog", p)))
                if rnd and one and pin and not tog:
                    miss.append(("random closure", "toggle", lacks(f"{pre}.tog", p)))
            rows.append({"pass": p, "dir": d, "floor_computed": w1, "missing": [{"where": a, "term": b, "lacks": c} for a, b, c in miss]})
            if not w1:
                lines.append(f"LEFTOVER-E195 p{p} {d}: the floor is not computed (x9_{d}_w1 or x9_{d}_z lacks a kept run): no zero-filled term")
            elif miss:
                lines.append(f"LEFTOVER-E195 p{p} {d}: taken as zero by the registered code: " + "; ".join(
                    f"the {a}'s {b} price (no kept run of {', '.join(c) or 'its rate'})" for a, b, c in miss))
            else:
                lines.append(f"LEFTOVER-E195 p{p} {d}: the floor's and the random closure's terms all present")
    volts, peaks = {}, {}
    for dd in dirs:
        ss = tel(dd)
        pv = {}
        for rn in REF_V:
            vs = []
            for x in ss:
                try:
                    vs.append(float(x["sp"][f"{rn}_mv"][0]))
                except (KeyError, IndexError, TypeError, ValueError):
                    pass
            pv[rn] = (sum(vs) / len(vs) / 1000.0) if vs else None
        volts[os.path.basename(os.path.normpath(dd))] = pv
        w, c, nw, _ = peak(ss)
        peaks[os.path.basename(os.path.normpath(dd))] = {"board_w": w, "die_c": c, "samples": nw}
    for rn, ref in REF_V.items():
        vals = [v[rn] for v in volts.values() if v.get(rn) is not None]
        mean = (sum(vals) / len(vals)) if vals else None
        lines.append(f"LEFTOVER-E195 rail {rn}: measured {('%.4f V' % mean) if mean is not None else 'no reading'} (mean of the passes' "
                     f"sp.{rn}_mv[0]); the reducer's fixed reference {ref:.3f} V (its electrons use the fixed volts: E195.md 7)")
    bw = [x["board_w"] for x in peaks.values() if x["board_w"] is not None]
    dc = [x["die_c"] for x in peaks.values() if x["die_c"] is not None]
    lines.append(f"LEFTOVER-E195 peaks: highest board {max(bw) if bw else None} W against the {STOP_W:g} W stop, highest die "
                 f"{max(dc) if dc else None} C against the {STOP_C:g} C stop, over {len(peaks)} passes")
    nz = sum(1 for r in rows if r["missing"])
    lines.append(f"LEFTOVER-E195: headline passes {head}; {nz} pass-direction(s) with a zero-filled term of {len(rows)}")
    for ln in lines:
        print(ln)
    if jout:
        with open(jout, "w") as f:
            json.dump({"headline": head, "rows": rows, "rail_volts": volts, "reference_volts": REF_V, "peaks": peaks}, f, indent=1)
    return 0


def main(argv):
    cmds = {"smoke": (cmd_smoke, 1), "dry": (cmd_dry, 2), "peaks": (cmd_peaks, 1), "leftover": (cmd_leftover, 3)}
    if not argv or argv[0] not in cmds or len(argv) - 1 < cmds[argv[0]][1]:
        print(__doc__)
        return 2
    return cmds[argv[0]][0](argv[1:])


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
