#!/usr/bin/env python3
"""E83: the README's tables and the blog's kinds-table cells, formatted from results.json (reduce_e83.py's output),
E83's frozen predictions.json and E80's results.json (for the all-51-kinds speed column). Formatting only: every
number is read from those files; the one derived column, board pJ per operation, is the sustained board W over the
sustained kernel rate and is labelled as derived.

    python3 tables.py results.json ../../../../tools/claims-v3/kspeed/e83/predictions.json \
        ../2026-10-31-e80-kinds-speed/results.json [--cells cells.json] > tables.md

Corrected after verification (Sat 31 Oct 2026; README "Corrections after verification", C3 and C7): in cells.json
`interval` holds only an uncertainty, either the runs themselves or, for a sustained cell of one run, one run's
1-sigma from the replicate pairs (one_run_sigma below, the same arithmetic as corrections-check.py C3). The limits get
no interval; their per-pass lines and labels moved to `conditions`. tables.md is unchanged by that correction.
"""
import argparse
import json

UNIT = {"fp32": "TFLOPS", "fp16": "TFLOPS", "int8": "TOPS"}
SRC = "docs/reports/data/2026-10-31-e83-kinds-speed-rest/results.json"
SRC80 = "docs/reports/data/2026-10-31-e80-kinds-speed/results.json"


def f1(x, d=1):
    return "–" if x is None else (f"{x:.{d}f}" if isinstance(x, (int, float)) else str(x))


def one_run_sigma(cell_sets):
    """One sustained run's 1-sigma: sqrt(2) x the rms half-spread of the replicate pairs (a pair's half-spread is
    each run's deviation from the pair mean, sigma / sqrt(2)). Clock: at or near a clamp if the pair's mean is
    <= 615 or >= 790 MHz, else on the slope. Board W and die C: pooled over every pair, sqrt(sum d^2 / 2n)."""
    sl, cl, dw, dd = [], [], [], []
    for cells in cell_sets:
        for c in cells.values():
            r = c.get("sus_mhz_runs") or []
            if len(r) != 2:
                continue
            m, h = (r[0] + r[1]) / 2, abs(r[0] - r[1]) / 2
            (cl if (m <= 615 or m >= 790) else sl).append(h)
            dw.append(abs(c["sus_w_runs"][0] - c["sus_w_runs"][1]))
            dd.append(abs(c["sus_die_runs"][0] - c["sus_die_runs"][1]))

    def rq(xs):
        return (sum(x * x for x in xs) / len(xs)) ** 0.5
    return {"slope": 2 ** 0.5 * rq(sl), "clamp": 2 ** 0.5 * rq(cl), "n_slope": len(sl), "n_clamp": len(cl),
            "w": (sum(x * x for x in dw) / (2 * len(dw))) ** 0.5, "die": (sum(x * x for x in dd) / (2 * len(dd))) ** 0.5,
            "n": len(dw)}


def pj(c):
    sw, sr = c.get("sus_w"), c.get("sus_rate")
    return sw / sr if (sw and sr) else None          # W / (Tops/s) = pJ per op


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("results")
    ap.add_argument("pred")
    ap.add_argument("e80")
    ap.add_argument("--cells")
    a = ap.parse_args()
    R = json.load(open(a.results))
    P = json.load(open(a.pred))
    E80 = json.load(open(a.e80))
    C = R["cells"]
    print("### The registered rules\n")
    print("| rule | verdict | numbers |")
    print("|---|---|---|")
    for k, v in R["rules"].items():
        nums = {x: y for x, y in v.items() if x not in ("rows", "verdict")}
        print(f"| {k} | **{v['verdict']}** | `{json.dumps(nums)}` |")

    print("\n### Each kind, measured (the 33, then E80's five anchors as re-run here)\n")
    print("| format | kind | burst MHz (2 passes) | burst rate | p800 W | burst die °C | burst limit | sustained MHz "
          "| sustained rate (kernel / wall) | sustained board W | sustained die °C | sustained limit | c W | board pJ/op |")
    print("|---|---|---|---|---|---|---|---|---|---|---|---|---|---|")
    order = [k for k, c in C.items() if c["role"] == "e83"] + [k for k, c in C.items() if c["role"] == "anchor"]
    for key in order:
        c = C[key]
        t, k = key.split("/")
        u = UNIT[t]
        bruns = "/".join(f1(x) for x in c.get("burst_mhz_runs", []))
        die_b = ", ".join(f"{x}→{y}" for x, y in zip(c.get("burst_die_start", []), c.get("burst_die_max", [])))
        sruns = "/".join(f1(x) for x in c.get("sus_mhz_runs", []))
        name = k + (" (anchor)" if c["role"] == "anchor" else "")
        print(f"| {t} | {name} | {f1(c.get('burst_mhz'))} ({bruns}) | {f1(c.get('burst_rate'), 2)} {u} "
              f"| {f1(c.get('burst_p800_w'))} | {die_b} | {c.get('burst_limit')} | {f1(c.get('sus_mhz'))}"
              + (f" ({sruns})" if len(c.get('sus_mhz_runs', [])) > 1 else "")
              + f" | {f1(c.get('sus_rate'), 2)} / {f1(c.get('sus_rate_wall'), 2)} {u} | {f1(c.get('sus_w'), 1)} "
              f"| {f1(c.get('sus_die'), 1)} | {c.get('sus_limit')} | {f1(c.get('c_w'), 2)} | {f1(pj(c), 2)} |")

    print("\n### Predicted against measured (the 33)\n")
    print("| format | kind | burst meas | (a) | (b) 4–12 s | gov arm | sustained meas | (a) | (b) | T1 + E80 line | (a-adj) "
          "| limit meas / (a) | c meas (W) | c pred [95%] | relation on c meas: burst / sustained |")
    print("|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|")
    for key, c in C.items():
        if c["role"] != "e83":
            continue
        t, k = key.split("/")
        pa, pb = c["pred_a"], c["pred_b"]
        print(f"| {t} | {k} | {f1(c.get('burst_mhz'))} | {f1(pa['burst_mhz'])} | {f1(pb['burst_mhz_4_12s'], 0)} "
              f"| {f1(c.get('arm_gov_burst_mhz'))} | {f1(c.get('sus_mhz'))} | {f1(pa['sus_mhz'])} "
              f"| {f1(pb['sus_mhz_40_80s'], 0)} | {f1(c.get('arm_t1_e80line_sus_mhz'))} | {f1(c.get('arm_a_adj_sus_mhz'))} "
              f"| {c.get('sus_limit')} / {pa['sus_limit']} | {f1(c.get('c_w'), 2)} "
              f"| {f1(c['c_pred_w'], 2)} [{c['c_ci95_w'][0]:.2f}, {c['c_ci95_w'][1]:.2f}] "
              f"| {f1(c.get('rel_on_measured_c_burst_mhz'))} / {f1(c.get('rel_on_measured_c_sus_mhz'))} |")

    print("\n### Each kind's switching term as a share of random data's (derived)\n")
    print("Derived, not measured on its own: (c_kind − c_zeros) / (c_random − c_zeros), with this session's own zeros "
          "and random cells of the same format (fp32 zeros and randn, fp16 zeros and randn, int8 zeros and full), all "
          "from `results.json` `cells.*.c_w`. 0 = as cheap as zeros, 1 = as costly as random data.\n")
    print("| format | kind | c W | share of random's switching over zeros |")
    print("|---|---|---|---|")
    ref = {"fp32": ("fp32/zeros", "fp32/randn"), "fp16": ("fp16/zeros", "fp16/randn"), "int8": ("int8/zeros", "int8/full")}
    for key in order:
        t, k = key.split("/")
        z, r = (C.get(ref[t][0], {}).get("c_w"), C.get(ref[t][1], {}).get("c_w"))
        cw = C[key].get("c_w")
        sh = (cw - z) / (r - z) if None not in (cw, z, r) and r != z else None
        print(f"| {t} | {k} | {f1(cw, 2)} | {f1(sh, 3)} |")

    print("\n### All 51 kinds: the speed column (E80's 18 at 12:22–13:02 PDT, E83's 33 later the same afternoon)\n")
    print("| format | kind | session | burst MHz | burst rate | sustained MHz | sustained rate | sustained board W "
          "| sustained die °C | sustained limit |")
    print("|---|---|---|---|---|---|---|---|---|---|")
    allk = []
    for t in ("fp32", "fp16", "int8"):
        for key, c in E80["cells"].items():
            if key.startswith(t + "/"):
                allk.append((key, "E80", c))
        for key, c in C.items():
            if key.startswith(t + "/") and c["role"] == "e83":
                allk.append((key, "E83", c))
    for key, s, c in allk:
        t, k = key.split("/")
        u = UNIT[t]
        extra = ""
        if s == "E80" and key in C:
            extra = f" (E83 re-run: {f1(C[key].get('burst_mhz'))} / {f1(C[key].get('sus_mhz'))})"
        print(f"| {t} | {k} | {s}{extra} | {f1(c.get('burst_mhz'))} | {f1(c.get('burst_rate'), 2)} {u} "
              f"| {f1(c.get('sus_mhz'))} | {f1(c.get('sus_rate'), 2)} {u} | {f1(c.get('sus_w'), 1)} "
              f"| {f1(c.get('sus_die'), 1)} | {c.get('sus_limit')} |")
    print(f"\n{len(allk)} kinds.")

    sig = one_run_sigma([E80["cells"], C])
    bf = {int(f): w for f, w in P["constants"]["B_registered_w"].items()}
    gate = {rep: [m["gate"]["reading"][0] for m in R["runs"] if m["block"] == "BURST" and m["rep"] == rep]
            for rep in (1, 2)}
    dgate = sum(gate[2]) / len(gate[2]) - sum(gate[1]) / len(gate[1])
    rf = [C[x]["burst_mhz_runs"] for x in C if C[x].get("burst_limit") == "power" and not C[x].get("idle_resets_burst")]
    dpass = sum(b - a for a, b in rf) / len(rf)
    cells = []
    for key in order:
        c = C[key]
        t, k = key.split("/")
        u = UNIT[t]
        tile = P["kinds"][key]["tile"].split("/")[-1]
        base = {"format": t, "kind": k, "source": SRC}
        role = "" if c["role"] == "e83" else "; an E80 anchor re-run in E83's session"
        cond = ("aifoundry2 card 0 under its own governor (65 W static TDP, 65 C threshold, read back 65/65 after "
                "every run, never set); E64's kernel, 1,024 minions; Q130(s) rev 2 tile (%s); %s" + role)
        bruns = "/".join(f1(x) for x in c.get("burst_mhz_runs", []))
        if c.get("burst_mhz") is not None:
            ds = ", ".join(str(x) for x in c.get("burst_die_start", []))
            po = (f"; the passes ran in two rounds (all pass-1 bursts, then all pass-2), pass 2 from a die {dgate:.1f} C "
                  "warmer on average" + (f"; on a power-limited kind like this one the pass spread includes a "
                                         f"pass-order effect of {dpass:+.1f} MHz on average (pass 2 minus pass 1 over "
                                         f"the {len(rf)} power-limited kinds without an idle reset; "
                                         "corrections-check.txt C6)" if c.get("burst_limit") == "power" else ""))
            cells.append(dict(base, quantity="burst_MHz", value=f1(c["burst_mhz"]), interval=f"two passes: {bruns}",
                              unit="MHz, mean sampled clock 1.5-6.5 s of a 6 s run",
                              conditions=cond % (tile, f"cool die, launched at a reading <= 55 C ({ds})" + po),
                              source=SRC + f" cells['{key}'].burst_mhz"))
            cells.append(dict(base, quantity=u, value=f1(c.get("burst_rate"), 2),
                              interval="two passes: " + "/".join(f1(x, 2) for x in c.get("burst_rate_runs", [])),
                              unit=f"{u}, kernel-counted, launches starting >= 1.5 s", conditions=cond % (tile, "burst"),
                              source=SRC + f" cells['{key}'].burst_rate"))
            cells.append(dict(base, quantity="board_W_at_800MHz", value=f1(c.get("burst_p800_w"), 1),
                              interval="two passes: " + "/".join(f1(x, 1) for x in c.get("burst_p800_w_runs", [])),
                              unit="W, whole board, median at 800 MHz in the first 1 s after reaching 800",
                              conditions=cond % (tile, "burst, cool die"), source=SRC + f" cells['{key}'].burst_p800_w"))
            cells.append(dict(base, quantity="burst_limit", value=c.get("burst_limit"), interval=None,
                              unit="which governor test stepped the clock first (power / thermal / none)",
                              conditions=cond % (tile, "burst; first throttle-down line per pass: " + ", ".join(
                                  str(x) for x in c.get("burst_first_down", []))),
                              source=SRC + f" cells['{key}'].burst_first_down"))
            if c.get("c_w") is not None:
                cells.append(dict(base, quantity="switching_term_c_W", value=f1(c["c_w"], 2),
                                  interval="two passes: " + "/".join(f1(x, 2) for x in c.get("c_w_runs", [])),
                                  unit=("W, the switching term c of P_f = B_f + c s_f: board switching at 600 MHz and "
                                        "517 mV, referred to a 58 C die, over E64's fitted baseline B_f ("
                                        + " / ".join(f"{bf[f]:.2f}" for f in sorted(bf)) + " W at "
                                        + " / ".join(str(f) for f in sorted(bf)) + " MHz), not over idle; the type's "
                                        "zeros read 1.7-2.4 W on it, and at 700 / 800 MHz the same data switch 1.41 / "
                                        "1.91 times as much (E64's method; corrections-check.txt C2)"),
                                  conditions=cond % (tile, "burst powers at 600/700/800 MHz"),
                                  source=SRC + f" cells['{key}'].c_w"))
        if c.get("sus_mhz") is not None:
            n = len(c.get("sus_mhz_runs", []))
            sruns = "/".join(f1(x) for x in c.get("sus_mhz_runs", []))
            slope = c.get("sus_limit") == "thermal" and c["sus_mhz"] > 615
            s1 = sig["slope"] if slope else sig["clamp"]
            where = (f"on the slope (sqrt(2) x the rms half-spread of the {sig['n_slope']} knife-edge replicate pairs)"
                     if slope else f"at or near a clamp (sqrt(2) x the rms half-spread of {sig['n_clamp']} replicate "
                                   "pairs)")
            iv = f"{n} runs: {sruns}" if n > 1 else f"+-{s1:.1f} MHz, 1 sigma for one run {where}; corrections-check.txt C3"
            cs = cond % (tile, "sustained: nine back-to-back 8 s processes from a die <= 57 C, last 40 s of ~76 s")
            cells.append(dict(base, quantity="sustained_MHz", value=f1(c["sus_mhz"]), interval=iv,
                              unit="MHz, mean sampled clock over the in-kernel readings of the last 40 s", conditions=cs,
                              source=SRC + f" cells['{key}'].sus_mhz"))
            sr = c.get("sus_rate")
            cells.append(dict(base, quantity=u, value=f1(sr, 2),
                              interval=(("runs: " + "/".join(f1(x, 2) for x in c.get("sus_rate_runs", []))) if n > 1
                                        else f"+-{sr * s1 / c['sus_mhz']:.2f} {u}, 1 sigma for one run (the clock's, "
                                             "scaled)"),
                              unit=(f"{u}, kernel-counted over the last 40 s (over the wall clock, the gaps between the "
                                    f"nine processes included: {f1(c.get('sus_rate_wall'), 2)})"), conditions=cs,
                              source=SRC + f" cells['{key}'].sus_rate"))
            cells.append(dict(base, quantity="board_W", value=f1(c.get("sus_w"), 1),
                              interval=(("runs: " + "/".join(f1(x, 2) for x in c.get("sus_w_runs", []))) if n > 1
                                        else f"+-{sig['w']:.1f} W, 1 sigma for one run (pooled over {sig['n']} "
                                             "replicate pairs; corrections-check.txt C3)"),
                              unit="W, whole board, mean over the in-kernel readings of the last 40 s", conditions=cs,
                              source=SRC + f" cells['{key}'].sus_w"))
            cells.append(dict(base, quantity="die_C", value=f1(c.get("sus_die"), 1),
                              interval=(("runs: " + "/".join(f1(x, 1) for x in c.get("sus_die_runs", []))) if n > 1
                                        else f"+-{sig['die']:.1f} C, 1 sigma for one run (pooled over {sig['n']} "
                                             "replicate pairs; corrections-check.txt C3)"),
                              unit="C, mean of the minion-shire die reading over the in-kernel readings of the last 40 s",
                              conditions=cs, source=SRC + f" cells['{key}'].sus_die"))
            cells.append(dict(base, quantity="limit", value=c.get("sus_limit"), interval=None,
                              unit="the test that holds the sustained clock (none / thermal / power)",
                              conditions=cs + "; registered label per run: " + "/".join(c.get("sus_limit_runs", []))
                              + "; E64 R4 labels over the last 40 s: " + json.dumps(c.get("sus_last")),
                              source=SRC + f" cells['{key}'].sus_limit_runs"))
    if a.cells:
        json.dump(cells, open(a.cells, "w"), indent=1)
    return 0


if __name__ == "__main__":
    main()
