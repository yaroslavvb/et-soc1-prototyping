#!/usr/bin/env python3
"""E80: the README's tables and the blog's kinds-table cells, formatted from results.json (reduce_kspeed.py's output)
and predictions.json. Formatting only: every number is read from those two files; the one derived column, board pJ
per operation, is the sustained board W over the sustained kernel rate and is labelled as derived.

    python3 tables.py results.json ../../../../tools/claims-v3/kspeed/predictions.json [--cells cells.json] > tables.md
"""
import argparse
import json
import statistics as st

UNIT = {"fp32": "TFLOPS", "fp16": "TFLOPS", "int8": "TOPS"}


def f1(x, d=1):
    return "–" if x is None else (f"{x:.{d}f}" if isinstance(x, (int, float)) else str(x))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("results")
    ap.add_argument("pred")
    ap.add_argument("--cells")
    a = ap.parse_args()
    R = json.load(open(a.results))
    P = json.load(open(a.pred))
    C = R["cells"]
    src = "docs/reports/data/2026-10-31-e80-kinds-speed/results.json"
    print("### The registered rules\n")
    print("| rule | verdict | numbers |")
    print("|---|---|---|")
    for k, v in R["rules"].items():
        nums = {x: y for x, y in v.items() if x not in ("rows", "verdict")}
        print(f"| {k} | **{v['verdict']}** | `{json.dumps(nums)}` |")
    print("\n### Each kind, measured\n")
    print("| format | kind | burst MHz (2 passes) | burst rate | p800 W | burst die °C | burst limit | sustained MHz "
          "| sustained rate (kernel / wall) | sustained board W | sustained die °C | sustained limit | board pJ/op |")
    print("|---|---|---|---|---|---|---|---|---|---|---|---|---|")
    cells = []
    for key, c in C.items():
        t, k = key.split("/")
        u = UNIT[t]
        bmhz = c.get("burst_mhz")
        bruns = "/".join(f1(x) for x in c.get("burst_mhz_runs", []))
        ds = c.get("burst_die_start", [])
        dm = c.get("burst_die_max", [])
        die_b = ", ".join(f"{a_}→{b_}" for a_, b_ in zip(ds, dm))
        srate = c.get("sus_rate")
        sw = c.get("sus_w")
        pj = (sw / (srate * 1e12) * 1e12) if (sw and srate) else None
        sruns = "/".join(f1(x) for x in c.get("sus_mhz_runs", []))
        print(f"| {t} | {k} | {f1(bmhz)} ({bruns}) | {f1(c.get('burst_rate'), 2)} {u} | {f1(c.get('burst_p800_w'))} "
              f"| {die_b} | {c.get('burst_limit')} | {f1(c.get('sus_mhz'))}"
              + (f" ({sruns})" if len(c.get('sus_mhz_runs', [])) > 1 else "")
              + f" | {f1(srate, 2)} / {f1(c.get('sus_rate_wall'), 2)} {u} | {f1(sw, 1)} | {f1(c.get('sus_die'), 1)} "
              f"| {c.get('sus_limit')} | {f1(pj, 2)} |")
        base = {"format": t, "kind": k, "source": src}
        cond = ("aifoundry2 card 0 under its own governor (65 W static TDP, 65 C threshold, read back 65/65 after "
                "every run, never set); E64's kernel, 1,024 minions; Q130(s) rev 2 tile (%s); %s")
        if bmhz is not None:
            iv = c.get("burst_mhz_runs", [])
            cells.append(dict(base, quantity="burst_MHz", value=f1(bmhz),
                              interval=f"two passes: {bruns}", unit="MHz, mean sampled clock 1.5-6.5 s of a 6 s run",
                              conditions=cond % (P["kinds"][key]["tile"].split("/")[-1],
                                                 "cool die, launched at a reading <= 55 C (%s)" % ", ".join(
                                                     str(x) for x in ds)),
                              source=src + f" cells['{key}'].burst_mhz"))
            cells.append(dict(base, quantity=u, value=f1(c.get("burst_rate"), 2),
                              interval="two passes: " + "/".join(f1(x, 2) for x in c.get("burst_rate_runs", [])),
                              unit=f"{u}, kernel-counted, launches starting >= 1.5 s",
                              conditions=cond % (P["kinds"][key]["tile"].split("/")[-1], "burst"),
                              source=src + f" cells['{key}'].burst_rate"))
            cells.append(dict(base, quantity="board_W_at_800MHz", value=f1(c.get("burst_p800_w"), 1),
                              interval="two passes: " + "/".join(f1(x, 1) for x in c.get("burst_p800_w_runs", [])),
                              unit="W, whole board, median at 800 MHz in the first 1 s after reaching 800",
                              conditions=cond % (P["kinds"][key]["tile"].split("/")[-1], "burst, cool die"),
                              source=src + f" cells['{key}'].burst_p800_w"))
            cells.append(dict(base, quantity="burst_limit", value=c.get("burst_limit"),
                              interval="first throttle-down line per pass: " + ", ".join(
                                  str(x) for x in c.get("burst_first_down", [])),
                              unit="which governor test stepped the clock first (power / thermal / none)",
                              conditions=cond % (P["kinds"][key]["tile"].split("/")[-1], "burst"),
                              source=src + f" cells['{key}'].burst_first_down"))
        if c.get("sus_mhz") is not None:
            n = len(c.get("sus_mhz_runs", []))
            iv = f"{n} runs: {sruns}" if n > 1 else "one run (single pass; E64's SUS reproducibility applies)"
            cs = cond % (P["kinds"][key]["tile"].split("/")[-1],
                         "sustained: nine back-to-back 8 s processes from a die <= 57 C, last 40 s of ~76 s")
            cells.append(dict(base, quantity="sustained_MHz", value=f1(c["sus_mhz"]), interval=iv,
                              unit="MHz, mean sampled clock over the last 40 s", conditions=cs,
                              source=src + f" cells['{key}'].sus_mhz"))
            cells.append(dict(base, quantity=u, value=f1(srate, 2),
                              interval=("runs: " + "/".join(f1(x, 2) for x in c.get("sus_rate_runs", [])))
                              + f"; wall-clock (gaps included) {f1(c.get('sus_rate_wall'), 2)}",
                              unit=f"{u}, kernel-counted over the last 40 s", conditions=cs,
                              source=src + f" cells['{key}'].sus_rate"))
            cells.append(dict(base, quantity="board_W", value=f1(sw, 1),
                              interval="runs: " + "/".join(f1(x, 2) for x in c.get("sus_w_runs", [])),
                              unit="W, whole board, mean over the last 40 s", conditions=cs,
                              source=src + f" cells['{key}'].sus_w"))
            cells.append(dict(base, quantity="die_C", value=f1(c.get("sus_die"), 1),
                              interval="runs: " + "/".join(f1(x, 1) for x in c.get("sus_die_runs", [])),
                              unit="C, mean of the minion-shire die reading over the last 40 s", conditions=cs,
                              source=src + f" cells['{key}'].sus_die"))
            cells.append(dict(base, quantity="limit", value=c.get("sus_limit"),
                              interval="E64 R4 labels over the last 40 s: " + json.dumps(c.get("sus_last")),
                              unit="the test that holds the sustained clock (none / thermal / power)", conditions=cs,
                              source=src + f" cells['{key}'].sus_limit_runs"))
    print("\n### Predicted against measured\n")
    print("| format | kind | burst meas | burst pred (registered) | T1 | Q130(c) 4–12 s | sustained meas | T1 γ3 pred "
          "| Q130(c) | limit meas / pred | c meas (W) | c pred [95%] |")
    print("|---|---|---|---|---|---|---|---|---|---|---|---|")
    for key, c in C.items():
        t, k = key.split("/")
        p = P["kinds"][key]
        print(f"| {t} | {k} | {f1(c.get('burst_mhz'))} | {f1(c.get('pred_burst_reg'))} | {f1(c.get('pred_burst_t1'))} "
              f"| {f1(c.get('pred_burst_q130c'), 0)} | {f1(c.get('sus_mhz'))} | {f1(c.get('pred_sus_t1'))} "
              f"| {f1(c.get('pred_sus_q130c'), 0)} | {c.get('sus_limit')} / {c.get('pred_limit')} "
              f"| {f1(c.get('c_w'), 2)} | {f1(p['c_pred_w'], 2)} [{p['c_ci95_w'][0]:.2f}, {p['c_ci95_w'][1]:.2f}] |")
    if a.cells:
        json.dump(cells, open(a.cells, "w"), indent=1)
    return 0


if __name__ == "__main__":
    main()
