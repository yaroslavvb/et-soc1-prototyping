#!/usr/bin/env python3
"""E135: write the frozen predictions, predictions-e135.json and predictions-e135.txt, before the first measured call.

    python3 make_predictions_e135.py            # from tools/gpu/e135/, in the lab repo

Horace He's numbers come from Q132(g) section d's table (the gist's two recorded runs, read from the comment images)
and from horace-chart.txt (the post's chart, read from its pixels); the ET-SoC-1's from E80's and E83's committed
results.json (`cells.<format>/<kind>.burst_rate`, `sus_rate`). Standard library only."""
import json
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
DATA = os.path.join(REPO, "docs", "reports", "data")


def chart():
    path = os.path.join(DATA, "2026-11-01-q132-governor-desk", "horace-chart.txt")
    last = [ln for ln in open(path).read().splitlines() if ln.startswith("{")][-1]
    return json.loads(last), os.path.relpath(path, REPO)


def gist_runs():
    """Q132(g) section d's table, rows 'gist comment, 28 Apr 2024' and '... 21 Jun 2024'."""
    path = os.path.join(DATA, "2026-11-01-q132-governor-desk", "README.md")
    cols = ["randn", "twos", "sparse_neg", "onebit", "rand", "zeros"]
    out = {}
    for ln in open(path).read().splitlines():
        m = re.match(r"\| gist comment, (\d+ \w+ 2024)[^|]*\|(.*)\|\s*\*\*([0-9.]+)\*\*\s*\|$", ln)
        if m:
            vals = [float(x) for x in m.group(2).split("|")]
            out[m.group(1)] = dict(zip(cols, vals))
            out[m.group(1)]["zeros_over_randn_printed"] = float(m.group(3))
    assert len(out) == 2, out
    return out, os.path.relpath(path, REPO) + " (section d, the first table)"


def etsoc1():
    """zeros over random, the kernel's rate, aifoundry2 under its own governor, the resident loop."""
    rows = {}
    src = {}
    for exp, d in (("E80", "2026-10-31-e80-kinds-speed"), ("E83", "2026-10-31-e83-kinds-speed-rest")):
        p = os.path.join(DATA, d, "results.json")
        rows[exp] = json.load(open(p))["cells"]
        src[exp] = os.path.relpath(p, REPO)
    def get(exp, k, q):
        c = rows[exp].get(k)
        return None if c is None else c.get(q)
    out = {}
    for fmt, z, r in (("fp32", "fp32/zeros", "fp32/randn"), ("fp16", "fp16/zeros", "fp16/randn"),
                      ("int8", "int8/zeros", "int8/full")):
        pairs = []
        for ez in ("E80", "E83"):
            for er in ("E80", "E83"):
                zb, rb = get(ez, z, "burst_rate"), get(er, r, "burst_rate")
                zs, rs = get(ez, z, "sus_rate"), get(er, r, "sus_rate")
                if None not in (zb, rb, zs, rs):
                    pairs.append({"zeros_from": ez, "random_from": er, "burst_gap": round(zb / rb, 4),
                                  "sus_gap": round(zs / rs, 4)})
        lim = {e: {"random_burst_limit": get(e, r, "burst_limit"), "random_sus_limit": get(e, r, "sus_limit"),
                   "random_burst_mhz": get(e, r, "burst_mhz"), "random_sus_mhz": get(e, r, "sus_mhz"),
                   "random_burst_w": get(e, r, "burst_w"), "random_sus_w": get(e, r, "sus_w")} for e in ("E80", "E83")}
        out[fmt] = {"pairs": pairs, "random_cells": lim,
                    "burst_gap_range": [min(p["burst_gap"] for p in pairs), max(p["burst_gap"] for p in pairs)],
                    "sus_gap_range": [min(p["sus_gap"] for p in pairs), max(p["sus_gap"] for p in pairs)]}
    return out, src


def band(gH, LH, P0, L, n):
    """The overshoot model: random's dynamic power P - P0 scales as f**n; zeros runs at the full clock under the cap.
    At Horace's limit LH random runs at f_max / gH, so at a limit L its clock ratio is (1/gH)*((L-P0)/(LH-P0))**(1/n)."""
    r = (1.0 / gH) * ((L - P0) / (LH - P0)) ** (1.0 / n)
    return max(1.0, 1.0 / r)


def main():
    ch, ch_src = chart()
    gr, gr_src = gist_runs()
    et, et_src = etsoc1()
    g28 = gr["28 Apr 2024"]
    gH = g28["zeros"] / g28["randn"]
    P = {
        "experiment": "E135",
        "frozen": "Mon 2 Nov 2026 (week 45), before the first measured call; written by make_predictions_e135.py",
        "answers": "the kinds page's section 11 item 2, 'A GPU measured the same way' "
                   "(https://spacesheep.dev/@yaroslavvb/horace-kinds-of-numbers#11-what-is-still-open)",
        "horace": {
            "post_text": {"zeros": 295.0, "randn": 257.0, "ratio": round(295.0 / 257.0, 4),
                          "source": "docs/reports/data/2026-10-31-q130-literature/README.md section 1 (the post's text; no size or format stated for the pair)"},
            "gist_runs": gr, "gist_source": gr_src,
            "gist_setting": "mm_weird.py: torch.bfloat16, M = N = K = 8192, B = f(N, K).t(), triton do_bench, median of 10 shuffled trials",
            "chart": ch, "chart_source": ch_src,
            "chart_ratio": round(ch["Zeros"] / ch["Randn"], 4),
            "limit_w": 330.0, "idle_w": 88.0,
            "limit_source": "the post's footnote 1 ('a power limit of 330W') and its idle 'only pulling 88W', "
                            "docs/reports/data/2026-10-31-q130-literature/README.md section 1",
        },
        "etsoc1": {
            "gaps": et, "sources": et_src,
            "mechanism": "aifoundry2's governor: in a burst on a cool die the power test (a ~1.3 s average of board power "
                         "against 65 W) steps the clock in 100 MHz points, so a kind's burst clock is set by how far its "
                         "power at 800 MHz overshoots 65 W; in sustained work the 65 C thermal test acts instead "
                         "(the kinds page, section 3; E64 results.md 'The cool-die ladder'; E80, E83)",
            "burst_gap_fp32_e64": [1.127, 1.150],
            "burst_gap_fp32_e64_source": "docs/findings/05-claims.md, the burst-gap row; the kinds page section 1",
        },
        "model_band": {
            "form": "g(L, n) = max(1, gH * ((LH - P0) / (L - P0)) ** (1 / n)), n in {1, 2, 3}",
            "gH": round(gH, 4), "LH": 330.0, "P0": 88.0,
            "assumptions": ["Horace's zeros ran under his 330 W cap at the full clock",
                            "random data's power above P0 = his 88 W idle scales as clock**n, n between 1 and 3",
                            "our unit's random bf16 draws what his did at the same clock"],
            "examples": {f"{L:g} W": {f"n={n}": round(band(gH, 330.0, 88.0, L, n), 4) for n in (1, 2, 3)}
                         for L in (250.0, 300.0, 330.0, 400.0)},
        },
        "thresholds": {
            "capped_share": 0.5, "uncapped_share": 0.1, "thermal_share_max": 0.05,
            "power_at_cap_lo": 0.95, "power_at_cap_hi": 1.03, "clock_below": 0.99, "clock_at_max": 0.99,
            "speed_follows_clock_spread": 1.03, "iff_gap_min": 1.02, "iff_no_gap": 0.02,
            "burst_sus_lo": -0.01, "burst_sus_hi": 0.05, "chart_rho_min": 0.7, "chart_spread_min": 1.02,
            "protocol_vs_cells": 0.03, "lowcap_clock_same": 0.01, "gist_at_330": [1.17, 1.26],
        },
        "windows_s": {"early": [0.0, 0.5], "burst": [0.0, 3.0], "sus": [3.0, 63.0], "late": [48.0, 63.0]},
        "predictions": {
            "P1": "Horace's protocol (mm_weird.py's six kinds, bf16, 8192^3) on his A100 at 330 W: zeros 292.30 / randn "
                  "239.41 = 1.221 (28 Apr) and 291.63 / 240.43 = 1.213 (21 Jun); the chart's nine kinds 236.47 (randn) "
                  "to 287.69 (zeros), 1.217; the post's text 295 / 257 = 1.148. Ours at our own cap: P6.",
            "P2": "The ET-SoC-1 mechanism, bf16 sustained at the default cap: random's SM clock below zeros' "
                  "(<= 0.99x), SW power cap active in >= 50% of random's samples, every thermal reason <= 5%, "
                  "random's power within 0.95-1.03 of the enforced limit.",
            "P3": "Speed follows the clock: per format and window, TFLOPS per MHz agrees across kinds within 3%.",
            "P4": "The cap's dichotomy: a kind below 95% of the limit holds >= 99% of the max SM clock with the SW "
                  "power cap <= 10%; a kind with the SW power cap >= 50% sits at >= 95% of the limit.",
            "P5": "A lower cap (if nvidia-smi -pl works): random bf16 sits on the new cap with the SW power cap "
                  ">= 50%, the zeros/random gap widens, and a kind that stays under the new cap keeps its clock (1%).",
            "P6": "The gap at our cap from Horace's at his, through the overshoot: the bf16 sustained zeros/randn gap "
                  "inside g(L, n=1..3) (model_band); at 330 W, the gist's 1.17-1.26.",
            "P7": "No slow governor: the bf16 sustained gap minus the burst gap in -0.01 to +0.05.",
            "P8": "Thermal reasons inactive (<= 5% of samples) in every cell's sustained window.",
            "P9": "The gap appears where and only where the cap acts: random capped (>= 50%) and zeros not (<= 10%) "
                  "gives a gap >= 1.02; neither capped gives |gap - 1| <= 0.02.",
            "P10": "The nine bf16 kinds rank as the post's chart does: Spearman rho >= 0.7 (n/a if the spread < 2%).",
            "P11": "Horace's protocol reads the same gap as the sustained cells: |gist6 zeros/randn - bf16 sustained "
                   "zeros/randn| <= 0.03 per unit.",
        },
    }
    with open(os.path.join(HERE, "predictions-e135.json"), "w") as f:
        json.dump(P, f, indent=1)
    lines = ["E135 frozen predictions (predictions-e135.json)", ""]
    lines.append(f"Horace, gist 28 Apr: zeros {g28['zeros']} / randn {g28['randn']} = {gH:.4f}; "
                 f"21 Jun: {gr['21 Jun 2024']['zeros']} / {gr['21 Jun 2024']['randn']} = "
                 f"{gr['21 Jun 2024']['zeros'] / gr['21 Jun 2024']['randn']:.4f}; chart {P['horace']['chart_ratio']}; "
                 f"text {P['horace']['post_text']['ratio']}")
    lines.append("chart: " + ", ".join(f"{k} {v}" for k, v in ch.items()))
    for fmt, v in et.items():
        lines.append(f"ET-SoC-1 {fmt}: burst gap {v['burst_gap_range']}, sustained {v['sus_gap_range']} "
                     f"(random's limits: {[(e, x['random_burst_limit'], x['random_sus_limit']) for e, x in v['random_cells'].items()]})")
    lines.append("model band g(L, n), n = 1 / 2 / 3:")
    for L, d in P["model_band"]["examples"].items():
        lines.append(f"  {L}: " + " / ".join(f"{d[k]:.3f}" for k in ("n=1", "n=2", "n=3")))
    lines.append("")
    for k, v in P["predictions"].items():
        lines.append(f"{k}: {v}")
    with open(os.path.join(HERE, "predictions-e135.txt"), "w") as f:
        f.write("\n".join(lines) + "\n")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
