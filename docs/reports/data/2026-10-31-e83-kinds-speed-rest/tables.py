#!/usr/bin/env python3
"""E83: the README's tables and the blog's kinds-table cells, formatted from results.json (reduce_e83.py's output),
E83's frozen predictions.json and E80's results.json (for the all-51-kinds speed column). Formatting only: every
number is read from those files; the one derived column, board pJ per operation, is the sustained board W over the
sustained kernel rate and is labelled as derived.

    python3 tables.py results.json ../../../../tools/claims-v3/kspeed/e83/predictions.json \
        ../2026-10-31-e80-kinds-speed/results.json [--cells cells.json] > tables.md
"""
import argparse
import json

UNIT = {"fp32": "TFLOPS", "fp16": "TFLOPS", "int8": "TOPS"}
SRC = "docs/reports/data/2026-10-31-e83-kinds-speed-rest/results.json"
SRC80 = "docs/reports/data/2026-10-31-e80-kinds-speed/results.json"


def f1(x, d=1):
    return "–" if x is None else (f"{x:.{d}f}" if isinstance(x, (int, float)) else str(x))


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
            cells.append(dict(base, quantity="burst_MHz", value=f1(c["burst_mhz"]), interval=f"two passes: {bruns}",
                              unit="MHz, mean sampled clock 1.5-6.5 s of a 6 s run",
                              conditions=cond % (tile, f"cool die, launched at a reading <= 55 C ({ds})"),
                              source=SRC + f" cells['{key}'].burst_mhz"))
            cells.append(dict(base, quantity=u, value=f1(c.get("burst_rate"), 2),
                              interval="two passes: " + "/".join(f1(x, 2) for x in c.get("burst_rate_runs", [])),
                              unit=f"{u}, kernel-counted, launches starting >= 1.5 s", conditions=cond % (tile, "burst"),
                              source=SRC + f" cells['{key}'].burst_rate"))
            cells.append(dict(base, quantity="board_W_at_800MHz", value=f1(c.get("burst_p800_w"), 1),
                              interval="two passes: " + "/".join(f1(x, 1) for x in c.get("burst_p800_w_runs", [])),
                              unit="W, whole board, median at 800 MHz in the first 1 s after reaching 800",
                              conditions=cond % (tile, "burst, cool die"), source=SRC + f" cells['{key}'].burst_p800_w"))
            cells.append(dict(base, quantity="burst_limit", value=c.get("burst_limit"),
                              interval="first throttle-down line per pass: " + ", ".join(
                                  str(x) for x in c.get("burst_first_down", [])),
                              unit="which governor test stepped the clock first (power / thermal / none)",
                              conditions=cond % (tile, "burst"), source=SRC + f" cells['{key}'].burst_first_down"))
            if c.get("c_w") is not None:
                cells.append(dict(base, quantity="switching_term_c_W", value=f1(c["c_w"], 2),
                                  interval="two passes: " + "/".join(f1(x, 2) for x in c.get("c_w_runs", [])),
                                  unit=("W, the switching term c of P_f = B_f + c s_f at 600 MHz / 517 mV, referred to "
                                        "a 58 C die (E64's method; includes the type's zero-data level)"),
                                  conditions=cond % (tile, "burst powers at 600/700/800 MHz"),
                                  source=SRC + f" cells['{key}'].c_w"))
        if c.get("sus_mhz") is not None:
            n = len(c.get("sus_mhz_runs", []))
            sruns = "/".join(f1(x) for x in c.get("sus_mhz_runs", []))
            iv = f"{n} runs: {sruns}" if n > 1 else "one run (see the data README for the replicate spread)"
            cs = cond % (tile, "sustained: nine back-to-back 8 s processes from a die <= 57 C, last 40 s of ~76 s")
            cells.append(dict(base, quantity="sustained_MHz", value=f1(c["sus_mhz"]), interval=iv,
                              unit="MHz, mean sampled clock over the last 40 s", conditions=cs,
                              source=SRC + f" cells['{key}'].sus_mhz"))
            cells.append(dict(base, quantity=u, value=f1(c.get("sus_rate"), 2),
                              interval=("runs: " + "/".join(f1(x, 2) for x in c.get("sus_rate_runs", [])))
                              + f"; wall-clock (gaps included) {f1(c.get('sus_rate_wall'), 2)}",
                              unit=f"{u}, kernel-counted over the last 40 s", conditions=cs,
                              source=SRC + f" cells['{key}'].sus_rate"))
            cells.append(dict(base, quantity="board_W", value=f1(c.get("sus_w"), 1),
                              interval="runs: " + "/".join(f1(x, 2) for x in c.get("sus_w_runs", [])),
                              unit="W, whole board, mean over the last 40 s", conditions=cs,
                              source=SRC + f" cells['{key}'].sus_w"))
            cells.append(dict(base, quantity="die_C", value=f1(c.get("sus_die"), 1),
                              interval="runs: " + "/".join(f1(x, 1) for x in c.get("sus_die_runs", [])),
                              unit="C, mean of the minion-shire die reading over the last 40 s", conditions=cs,
                              source=SRC + f" cells['{key}'].sus_die"))
            cells.append(dict(base, quantity="limit", value=c.get("sus_limit"),
                              interval="E64 R4 labels over the last 40 s: " + json.dumps(c.get("sus_last")),
                              unit="the test that holds the sustained clock (none / thermal / power)", conditions=cs,
                              source=SRC + f" cells['{key}'].sus_limit_runs"))
    if a.cells:
        json.dump(cells, open(a.cells, "w"), indent=1)
    return 0


if __name__ == "__main__":
    main()
