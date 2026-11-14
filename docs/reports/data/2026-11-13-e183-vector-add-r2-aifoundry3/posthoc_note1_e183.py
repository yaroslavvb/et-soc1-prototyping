#!/usr/bin/env python3
"""E183's data README, dated note 1 (Sat 14 Nov 2026, after the data verifier): the figures the note quotes, read again from committed
files. Post hoc: it decides nothing, scores nothing and changes no committed file. Standard library only; it imports no lab module, and of
october-forecast-model it reads only the version ids in the freeze lines of note M1 and note M2 and of note M1's reader's two outputs.

It reads this directory's six train blocks (raw/e183/p18310-p18315: runs.jsonl.gz, telemetry.jsonl.gz, train.jsonl.gz, code.sha256),
reduced-e183.json, scored-e183.json and SHA256SUMS, and as text README.md, README.md.dated-note-M1.md, arm-m1-e183.txt and
arm-m1-e183.json; and from the repository, as text only: tools/claims-v3/e183/E183.md, E183.md.dated-note-M2.md, score_e183.py,
reduce_e183_v2.py, run_e183.py and session_e183_v3.sh, tools/claims-v3/e182/e182_stats.py, tools/claims-v3/lib.sh,
workloads/enercat/analyze_catalogue.py and E82's data README (the lines the note cites, and the sha256 of four kit files).

    python3 -B docs/reports/data/2026-11-13-e183-vector-add-r2-aifoundry3/posthoc_note1_e183.py [--out <dir>]

Section 0 finds each line the note cites by a short anchor and prints only the anchor's file, line and label, never the line's text.
Section 1 reads each block's four anchor bursts by the catalogue's burst formula (analyze_catalogue.bursts_of, E180's, re-written here
line for line), first over every sample, the registered reduction, which must equal reduced-e183.json's readings, and then with E82 A2's
dip samples dropped over the block's series (the trains' rule, e182_stats.dips_kept); each busy window's dip count; T3's opening random
burst's dips sample by sample, with the card's own readings beside; and the 12 readings' mean, sd and interval both ways, with E180's RA5
board reading against each (the interval uses the committed reading's own t multiplier, its hw over its se, at the same 12 readings).
Section 2 counts, in each block, the samples the trains' dip rule drops and where they fall: inside a train launch's reading window
[t_start + 170 ms, t_end], in a train launch's first 170 ms, in an anchor burst's busy window, or elsewhere.
Section 3 lists the october-forecast-model versions in note M1's freeze lines and its reader's outputs, and in note M2's, and checks
note M2's M2-4 line on when its scoring runs. Section 4 gives the trains' half-widths as scored-e183.json gives them, against the README's
printed figures. Section 5 gives the build logs' committed paths. Section 6 gives each train's carry-over reading: the SFFS and FSSF
means of L3 - L2, their difference, the kit's figure (the difference over twice the train's estimate) against scored-e183.json and the
README, and the difference over the estimate alone. Section 7 gives the card-lock and timeout lines of the code each block pinned, with
each file's sha256 against every block's code.sha256.

It writes posthoc-note1-e183.json and posthoc-note1-e183.txt beside itself (or in --out), with paths relative to this directory or the
repository's top, floats rounded and no run time, so a re-run from the same tree writes them byte for byte. --data and --top name the
directory and the repository when the script runs from elsewhere. Exit 0 when it ran (its checks' results are in the outputs), 2 on a
usage error.
SPDX-License-Identifier: Apache-2.0
"""
import argparse
import gzip
import hashlib
import json
import math
import os
import re
import statistics as st
import sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
BLOCKS = [18310, 18311, 18312, 18313, 18314, 18315]
LAG_MS, DIP_W = 170, 4.0                 # tools/claims-v3/e182/e182_stats.py lines 19-20 (anchored in section 0)
A_LEAK_80, T_L = 23.257, 36.0            # workloads/enercat/analyze_catalogue.py line 28 (anchored in section 0)
MINUS = "−"
KIT = "tools/claims-v3/e183"
# The lines the note cites: (file relative to the data directory "D:" or the repository's top, label, line, an anchor on that line).
ANCHORS = [
    ("D:README.md", "the trains' half-widths as printed", 61, "Measured: T3 0.0107, T1 0.0117, T4 0.0138,"),
    ("D:README.md", "T2's printed half-width", 62, "T2 0.0150 and T5 0.0059 W."),
    ("D:README.md", "the anchors' item", 96, "- **The anchors**, fadd.ps random"),
    ("D:README.md", "the anchors against RA5", 97, "AGREES (RA5's mean inside)"),
    ("D:README.md", "the anchors by block", 98, "T3 6.373 / 8.930"),
    ("D:README.md", "the carry-over's divisor as printed", 103, "over twice the train's estimate): T3 +0.089"),
    ("D:README.md", "the carry-over figures, continued", 104, "T4 " + MINUS + "0.454, T6 +0.071, T2 +0.011, T5 " + MINUS + "0.037"),
    ("D:README.md", "october-forecast-model's arms, grouped with note M2", 108, "with its dated note 1, and note M2; reported, never a rule"),
    ("D:README.md", "read through the day-2 check v2's gate", 109, "through the day-2 check v2's gate"),
    ("D:README.md", "the build logs' folder as printed", 161, "`e183-build-logs/2026-11-13/`"),
    (KIT + "/E183.md", "section 5.3: the carry-over reading", 236, "its carry-over reading (the mean of L3 - L2 in SFFS quads"),
    (KIT + "/E183.md", "section 5.3: its divisor", 237, "in FSSF, over the train's estimate: a first-order carry-over c"),
    (KIT + "/E183.md", "section 11: the first-order carry-over", 371, "attenuates every contrast by (1 - c)"),
    (KIT + "/E183.md.dated-note-M2.md", "M2-4: when its scoring runs", 124, "after E183's data commit, in a later records round"),
    (KIT + "/score_e183.py", "the kit's carry-over figure", 151, '/ (2 * iv["mean"])'),
    (KIT + "/reduce_e183_v2.py", "the trains' samples: the dip rule", 65, "k = S.dips_kept(sm)"),
    (KIT + "/reduce_e183_v2.py", "the anchors: every sample, the catalogue's formula", 130, "res = ac.bursts_of(tel, runs)"),
    ("tools/claims-v3/e182/e182_stats.py", "the 170 ms lag", 19, "LAG_MS = 170"),
    ("tools/claims-v3/e182/e182_stats.py", "the dip threshold", 20, "DIP_W = 4.0"),
    ("tools/claims-v3/e182/e182_stats.py", "the dip rule", 110, "if v[i] < min(v[i - 2], v[i + 2]) - DIP_W:"),
    ("workloads/enercat/analyze_catalogue.py", "the leak law's constants", 28, "A_LEAK_80, T_L = 23.257, 36.0"),
    ("workloads/enercat/analyze_catalogue.py", "the busy window", 59, "busy = (t >= lo + 0.5) & (t <= hi)"),
    ("workloads/enercat/analyze_catalogue.py", "the idle window before", 62, "before = (t >= max(prev_hi + 2.3, lo - 3.5)) & (t <= lo - 0.3)"),
    ("workloads/enercat/analyze_catalogue.py", "the idle window after", 63, "after = (t >= hi + 2.3) & (t <= min(next_lo - 0.3, hi + 5.5))"),
    ("workloads/enercat/analyze_catalogue.py", "the leak correction", 74, "over = over_raw - leak_slope(0.5 * (Tb + Ti)) * (Tb - Ti)"),
    ("docs/reports/data/2026-10-31-e82-kinds-aifoundry1/README.md", "E82 A2's dip definition", 304, "(the A2 definition:"),
    ("tools/claims-v3/lib.sh", "hold10: timeout 10", 100, 'hold10() { timeout 10 "$@" < /dev/null; }'),
    ("tools/claims-v3/lib.sh", "block_begin", 179, "block_begin() {"),
    ("tools/claims-v3/lib.sh", "block_begin: the card's lock file", 183, "local lk=/run/lock/etsoc-shire${V3_DEVICE:-0}.lock"),
    ("tools/claims-v3/lib.sh", "block_begin: only when the lock file exists, not on a dry pass", 184,
     'if [ -e "$lk" ] && [ -z "${V3_DRY:-}" ]; then'),
    ("tools/claims-v3/lib.sh", "block_begin: flock -n, else exit 3", 185, 'flock -n 9 || { log "card lock $lk is held by another process'),
    ("tools/claims-v3/lib.sh", "block_begin: code.sha256 written at the block's start", 189,
     'sha256sum tools/claims-v3/lib.sh tools/claims-v3/"$EXP"/* > "$OUT/code.sha256"'),
    (KIT + "/run_e183.py", "the anchor bursts: timeout 10", 290, 'cmd = ["timeout", "10", host_bin] + E.burst_args(kind)'),
    (KIT + "/run_e183.py", "the train processes: timeout 10", 312, 'cmd = ["timeout", "10", host_bin] + E.train_args(t, ori)'),
    (KIT + "/session_e183_v3.sh", "the config reads: card lock and timeout 10", 57, "flock -n /run/lock/etsoc-shire0.lock timeout 10 bash"),
]
CODE = ["tools/claims-v3/lib.sh", KIT + "/block_e183_v3.sh", KIT + "/run_e183.py", KIT + "/session_e183_v3.sh"]


def r6(x):
    return None if x is None else round(float(x), 6)


def gzjson(p):
    return [json.loads(x) for x in gzip.open(p, "rt", encoding="utf-8") if x.startswith("{")]


def leak_slope(T):
    return A_LEAK_80 / T_L * math.exp((T - 80.0) / T_L)


def bursts(t, w, T, runs):
    """analyze_catalogue.bursts_of's over_idle_w, line for line: t in s (file order), w board W, T minshire[0] C."""
    groups = {}
    for r in runs:
        groups.setdefault((r["cfg"], r["pass"]), []).append(r)
    bl = sorted(((k, rs, min(r["t_start_ms"] for r in rs) / 1000.0, max(r["t_end_ms"] for r in rs) / 1000.0)
                 for k, rs in groups.items()), key=lambda b: b[2])
    out = {}
    for i, (k, rs, lo, hi) in enumerate(bl):
        prev_hi = bl[i - 1][3] if i else t[0]
        next_lo = bl[i + 1][2] if i + 1 < len(bl) else t[-1]
        busy = [j for j in range(len(t)) if lo + 0.5 <= t[j] <= hi]
        before = [j for j in range(len(t)) if max(prev_hi + 2.3, lo - 3.5) <= t[j] <= lo - 0.3]
        after = [j for j in range(len(t)) if hi + 2.3 <= t[j] <= min(next_lo - 0.3, hi + 5.5)]
        rail_idle = [j for j in range(len(t)) if max(prev_hi + 3.0, lo - 3.5) <= t[j] <= lo - 0.3]
        if len(busy) < 5 or len(before) < 4 or len(rail_idle) < 3:
            continue
        idle_b = st.fmean([w[j] for j in before])
        idle = idle_b if len(after) < 4 else 0.5 * (idle_b + st.fmean([w[j] for j in after]))
        Tb = st.fmean([T[j] for j in busy])
        Ti = st.fmean([T[j] for j in before] + ([T[j] for j in after] if len(after) >= 4 else []))
        over = st.fmean([w[j] for j in busy]) - idle - leak_slope(0.5 * (Tb + Ti)) * (Tb - Ti)
        out[k[0]] = {"over": over, "lo": lo, "hi": hi, "n_busy": len(busy)}
    return out


def dip_flags(w):
    """E82 A2, as e182_stats.dips_kept applies it over a block's series in time order: drop i when w[i] < min(w[i-2], w[i+2]) - 4 W."""
    f = [False] * len(w)
    for i in range(2, len(w) - 2):
        if w[i] < min(w[i - 2], w[i + 2]) - DIP_W:
            f[i] = True
    return f


def place(lo, hi, x):
    return "inside" if lo <= x <= hi else ("above" if x > hi else "below")


def overlap(lo, hi, lo2, hi2):
    return "DIFFERS LOW" if hi < lo2 else ("DIFFERS HIGH" if lo > hi2 else "AGREES")


def main():
    ap = argparse.ArgumentParser(add_help=True)
    ap.add_argument("--data", default=HERE)
    ap.add_argument("--top", default=None)
    ap.add_argument("--out", default=None)
    try:
        a = ap.parse_args()
    except SystemExit:
        return 2
    D = os.path.abspath(a.data)
    TOP = os.path.abspath(a.top) if a.top else os.path.abspath(os.path.join(D, "..", "..", "..", ".."))
    OUT = os.path.abspath(a.out) if a.out else D

    def path(f):
        return os.path.join(D, f[2:]) if f.startswith("D:") else os.path.join(TOP, f)

    def lines(f):
        return open(path(f), encoding="utf-8").read().split("\n")

    J = {"what": "E183's data README, dated note 1: post hoc figures, deciding nothing (posthoc_note1_e183.py)"}
    X = []
    P = X.append

    # ---- section 0: the cited lines
    s0, nok = [], 0
    for f, label, n, anchor in ANCHORS:
        L = lines(f)
        ok = 0 < n <= len(L) and anchor in L[n - 1]
        nok += ok
        s0.append({"file": f.replace("D:", ""), "line": n, "label": label, "anchor_found": ok})
    J["s0_cited_lines"] = {"anchors": s0, "found": nok, "of": len(ANCHORS)}
    P("# posthoc_note1_e183.py: E183's data README, dated note 1 (post hoc, deciding nothing)")
    P("")
    P(f"## 0. The cited lines: {nok} of {len(ANCHORS)} anchors found on their lines")
    for e in s0:
        P(f"  {'OK ' if e['anchor_found'] else 'MISSING'} {e['file']}:{e['line']}  {e['label']}")

    red = json.load(open(os.path.join(D, "reduced-e183.json")))
    sc = json.load(open(os.path.join(D, "scored-e183.json")))
    train_of = {b: red["blocks"][str(b)]["train"] for b in BLOCKS}

    # ---- sections 1 and 2: the anchors and the dips
    s1, s2, maxdiff, t3dips = [], [], 0.0, []
    for b in BLOCKS:
        bd = os.path.join(D, "raw", "e183", "p%d" % b)
        tel = gzjson(os.path.join(bd, "telemetry.jsonl.gz"))
        runs = [json.loads(x) for x in gzip.open(os.path.join(bd, "runs.jsonl.gz"), "rt", encoding="utf-8") if x.strip()]
        recs = gzjson(os.path.join(bd, "train.jsonl.gz"))
        t = [s["t_ms"] / 1000.0 for s in tel]
        w = [float(s["board_w"]) for s in tel]
        T = [s["temp_c"]["minshire"][0] for s in tel]
        in_order = all(tel[i]["t_ms"] < tel[i + 1]["t_ms"] for i in range(len(tel) - 1))
        dip = dip_flags(w)
        keep = [not x for x in dip]
        allb = bursts(t, w, T, runs)
        kb = bursts([x for x, k in zip(t, keep) if k], [x for x, k in zip(w, keep) if k], [x for x, k in zip(T, keep) if k], runs)
        blk = red["blocks"][str(b)]
        row = {"block": b, "train": train_of[b]}
        for side in ("open", "close"):
            z, rr = "e183/fadd.ps/zeros/h2@b%d-%s" % (b, side), "e183/fadd.ps/random/h2@b%d-%s" % (b, side)
            v_all = allb[rr]["over"] - allb[z]["over"]
            v_keep = kb[rr]["over"] - kb[z]["over"]
            v_red = blk["random_minus_zeros_%s_w" % side]
            maxdiff = max(maxdiff, abs(v_all - v_red))
            nd = {}
            for nm, cfg in (("random", rr), ("zeros", z)):
                lo, hi = allb[cfg]["lo"], allb[cfg]["hi"]
                nd[nm] = sum(1 for j in range(len(t)) if dip[j] and lo + 0.5 <= t[j] <= hi)
            row[side] = {"every_sample": r6(v_all), "reduced_e183_json": r6(v_red), "dips_dropped": r6(v_keep),
                         "dips_in_busy_window": nd}
            if b == 18310 and side == "open":
                rs = sorted([r for r in runs if r["cfg"] == rr], key=lambda r: r["t_start_ms"])
                lo, hi = allb[rr]["lo"], allb[rr]["hi"]
                for j in range(len(t)):
                    if dip[j] and lo + 0.5 <= t[j] <= hi:
                        li = [k + 1 for k, r in enumerate(rs) if r["t_start_ms"] <= tel[j]["t_ms"] <= r["t_end_ms"]]
                        k1 = li[0] if li else None
                        t3dips.append({
                            "s_after_burst_start": round(t[j] - lo, 3),
                            "ms_into_its_launch": (tel[j]["t_ms"] - rs[k1 - 1]["t_start_ms"]) if k1 else None,
                            "launch_of_8": k1, "board_w": w[j], "board_w_2_before": w[j - 2], "board_w_2_after": w[j + 2],
                            "clock_mhz": tel[j]["mhz"]["minion"], "minion_die_mv": tel[j]["die_mv"]["minion"],
                            "sp_board_avg_w_2_before_here_2_after": [tel[j - 2]["sp"]["board_avg_w"], tel[j]["sp"]["board_avg_w"],
                                                                      tel[j + 2]["sp"]["board_avg_w"]],
                            "sp_minion_rail_avg_w_2_before_here_2_after": [tel[j - 2]["sp"]["minion_w"][0], tel[j]["sp"]["minion_w"][0],
                                                                            tel[j + 2]["sp"]["minion_w"][0]],
                            "its_launch_rate_per_s": rs[k1 - 1]["ops_per_s"] if k1 else None})
                burst_rates = [r["ops_per_s"] for r in rs]
                held = {(rr, rs[d["launch_of_8"] - 1]["t_start_ms"]) for d in t3dips if d["launch_of_8"]}
                others = [x["ops_per_s"] for x in runs if (x["cfg"], x["t_start_ms"]) not in held]
                block_rates = [min(others), max(others), len(others)]
        s1.append(row)
        # section 2: where the block's dips fall
        where = {"train_reading_window": 0, "train_launch_first_170_ms": 0, "anchor_busy_window": 0, "elsewhere": 0}
        spans = [(min(r["t_start_ms"] for r in runs if r["cfg"] == c), max(r["t_end_ms"] for r in runs if r["cfg"] == c))
                 for c in sorted(set(r["cfg"] for r in runs))]
        for j in range(len(tel)):
            if not dip[j]:
                continue
            x = tel[j]["t_ms"]
            if any(r["t_start_ms"] + LAG_MS <= x <= r["t_end_ms"] for r in recs):
                where["train_reading_window"] += 1
            elif any(r["t_start_ms"] <= x < r["t_start_ms"] + LAG_MS for r in recs):
                where["train_launch_first_170_ms"] += 1
            elif any(lo + 500 <= x <= hi for lo, hi in spans):
                where["anchor_busy_window"] += 1
            else:
                where["elsewhere"] += 1
        s2.append({"block": b, "train": train_of[b], "samples": len(tel), "samples_in_time_order": in_order, "dips": sum(dip),
                   "dips_reduced_e183_json": blk.get("dips_dropped"), "where": where, "train_launch_records": len(recs)})

    a_all = [row[s]["every_sample"] for row in s1 for s in ("open", "close")]
    a_keep = [row[s]["dips_dropped"] for row in s1 for s in ("open", "close")]
    an = sc["reported"]["anchors_random_minus_zeros"]
    tm = an["hw"] / an["se"]
    ra5 = an["E180_RA5_board"]

    def summ(v):
        m, sd = st.fmean(v), st.stdev(v)
        se = sd / math.sqrt(len(v))
        lo, hi = m - tm * se, m + tm * se
        return {"n": len(v), "mean": r6(m), "sd": r6(sd), "min": r6(min(v)), "lo": r6(lo), "hi": r6(hi),
                "RA5_mean_against_it": place(lo, hi, ra5["mean"]), "intervals_overlap": overlap(lo, hi, ra5["lo"], ra5["hi"])}
    S_all, S_keep = summ(a_all), summ(a_keep)
    J["s1_anchors"] = {
        "formula": "workloads/enercat/analyze_catalogue.py bursts_of: over_idle_w, re-written here; random minus zeros at each block's open and close",
        "every_sample_equals_reduced_e183_json_within_1e-9": maxdiff < 1e-9,
        "blocks": s1,
        "twelve_readings": {"every_sample": S_all, "dips_dropped": S_keep, "t_multiplier_from_the_committed_reading": round(tm, 6),
                            "committed_reading": {"mean": r6(an["mean"]), "lo": r6(an["lo"]), "hi": r6(an["hi"]),
                                                  "RA5_mean_against_this": an["E180_RA5_mean_against_this"],
                                                  "intervals_overlap": an["intervals_overlap"]},
                            "E180_RA5_board": {k: r6(v) for k, v in ra5.items()}},
        "T3_open_random_dips": t3dips,
        "T3_open_random_launch_rates_per_s": burst_rates,
        "block_18310_other_anchor_launches_rate_min_max_count": block_rates}
    P("")
    P("## 1. The anchors: fadd.ps random - fadd.ps zeros, each block's open and close (W)")
    P(f"  the formula re-written here equals reduced-e183.json's readings within 1e-9: {maxdiff < 1e-9}")
    P("  block train side : every sample (registered) | dips dropped (E82 A2) | dip samples in the busy windows: random, zeros")
    for row in s1:
        for side in ("open", "close"):
            e = row[side]
            P(f"  {row['block']} {row['train']} {side:5s}: {e['every_sample']:7.3f} | {e['dips_dropped']:7.3f} | "
              f"{e['dips_in_busy_window']['random']}, {e['dips_in_busy_window']['zeros']}")
    for nm, S in (("every sample (registered)", S_all), ("dips dropped (post hoc)", S_keep)):
        P(f"  12 readings, {nm}: mean {S['mean']:.3f}, sd {S['sd']:.3f}, min {S['min']:.3f}, 95% [{S['lo']:.3f}, {S['hi']:.3f}] "
          f"(t multiplier {tm:.6f}, the committed reading's hw/se); E180's RA5 mean {ra5['mean']:.3f} {S['RA5_mean_against_it']} it; "
          f"intervals overlap: {S['intervals_overlap']}")
    P(f"  the committed reading (scored-e183.json): mean {an['mean']:.3f} [{an['lo']:.3f}, {an['hi']:.3f}], RA5 mean "
      f"{an['E180_RA5_mean_against_this']}, overlap {an['intervals_overlap']}; RA5 [{ra5['lo']:.3f}, {ra5['hi']:.3f}]")
    P("  T3's opening random burst: each dip sample (E82 A2's rule) with the card's own readings")
    for d in t3dips:
        P(f"    +{d['s_after_burst_start']:.3f} s after the burst's start, {d['ms_into_its_launch']} ms into its launch {d['launch_of_8']} of 8: "
          f"board {d['board_w']:.2f} W (2 samples before {d['board_w_2_before']:.2f}, 2 after {d['board_w_2_after']:.2f}); clock "
          f"{d['clock_mhz']} MHz; minion die {d['minion_die_mv']} mV; service processor's board average "
          f"{' / '.join('%.2f' % x for x in d['sp_board_avg_w_2_before_here_2_after'])} W and minion rail average "
          f"{' / '.join('%.3f' % x for x in d['sp_minion_rail_avg_w_2_before_here_2_after'])} W (2 before / here / 2 after); its "
          f"launch's rate {d['its_launch_rate_per_s']:.4e}/s")
    P(f"    the burst's eight launch rates: {' '.join('%.4e' % x for x in burst_rates)}; block 18310's other {block_rates[2]} anchor "
      f"launches: {block_rates[0]:.4e}-{block_rates[1]:.4e}/s")

    J["s2_train_dips"] = s2
    P("")
    P("## 2. The trains: the samples the dip rule drops in each block, and where they fall")
    for e in s2:
        wh = e["where"]
        P(f"  {e['block']} {e['train']}: {e['samples']} samples (in time order: {e['samples_in_time_order']}), {e['dips']} dropped "
          f"(reduced-e183.json: {e['dips_reduced_e183_json']}); inside a launch's reading window {wh['train_reading_window']}, "
          f"in a launch's first 170 ms {wh['train_launch_first_170_ms']}, in an anchor's busy window {wh['anchor_busy_window']}, "
          f"elsewhere {wh['elsewhere']}")
    tot = {k: sum(e["where"][k] for e in s2) for k in s2[0]["where"]}
    P(f"  all six: {sum(e['dips'] for e in s2)} dropped; inside a reading window {tot['train_reading_window']}")
    J["s2_totals"] = tot

    # ---- section 3: README line 108
    rx = re.compile(r"october-forecast-model (v[0-9]+), frozen")
    m1v = sorted(set(rx.findall(open(os.path.join(D, "README.md.dated-note-M1.md"), encoding="utf-8").read())))
    m1o = sorted(set(rx.findall(open(os.path.join(D, "arm-m1-e183.txt"), encoding="utf-8").read()) +
                     rx.findall(open(os.path.join(D, "arm-m1-e183.json"), encoding="utf-8").read())))
    m2v = sorted(set(rx.findall(open(path(KIT + "/E183.md.dated-note-M2.md"), encoding="utf-8").read())))
    named = {}
    for dirpath, _, fs in os.walk(D):
        for f in sorted(fs):
            if f.endswith(".gz") or f.startswith("posthoc") or f == "README.md.dated-note-1.md" or f == "SHA256SUMS-note1":
                continue
            p = os.path.join(dirpath, f)
            try:
                s = open(p, encoding="utf-8").read()
            except UnicodeDecodeError:
                continue
            for v in m2v:
                if ("october-forecast-model " + v) in s:
                    named.setdefault(os.path.relpath(p, D), []).append(v)
    m24 = lines(KIT + "/E183.md.dated-note-M2.md")[123]
    J["s3_line_108"] = {"note_M1_freeze_line_versions": m1v, "note_M1_reader_output_versions": m1o, "note_M2_versions": m2v,
                        "files_here_naming_a_note_M2_version": named,
                        "M2_4_says_a_later_records_round": "in a later records round" in m24}
    P("")
    P("## 3. README line 108: which versions were read through the gate")
    P(f"  note M1's freeze lines name {', '.join(m1v)}; its reader's two outputs name {', '.join(m1o)}")
    P(f"  note M2 registers {', '.join(m2v)}; files in this directory (before this note) that name one of them: {len(named)}")
    P(f"  note M2's M2-4 (line 124) places their scoring in a later records round: {'in a later records round' in m24}")

    # ---- section 4: the half-widths
    R = lines("D:README.md")
    printed = dict(re.findall(r"(T[1-6]) (0\.[0-9]{4})", (R[60] + " " + R[61]).split("Measured:")[1].split(" W.")[0]))
    s4 = {}
    for k in ("T3", "T1", "T4", "T6", "T2", "T5"):
        iv = sc["trains"][k]
        hw = iv["hi"] - iv["mean"]
        s4[k] = {"hw": r6(hw), "hw_4dp": "%.4f" % hw, "readme": printed.get(k), "same": printed.get(k) == "%.4f" % hw}
    J["s4_half_widths"] = s4
    P("")
    P("## 4. The trains' half-widths (W): scored-e183.json against README lines 61-62")
    for k, e in s4.items():
        P(f"  {k}: {e['hw']:.6f} -> {e['hw_4dp']}; README {e['readme']}: {'same' if e['same'] else 'DIFFERS'}")

    # ---- section 5: the build logs' committed paths
    paths = [ln.split("  ", 1)[1] for ln in open(os.path.join(D, "SHA256SUMS"), encoding="utf-8").read().splitlines() if "  " in ln]
    bl = [p for p in paths if "build" in p]
    J["s5_build_logs"] = {"sha256sums_entries": len(paths), "build_entries": bl,
                          "an_entry_under_e183_build_logs_2026_11_13": any("e183-build-logs/2026-11-13/" in p for p in paths)}
    P("")
    P(f"## 5. The build records' committed paths (SHA256SUMS, {len(paths)} entries)")
    for p in bl:
        P(f"  {p}")
    P(f"  an entry under e183-build-logs/2026-11-13/: {any('e183-build-logs/2026-11-13/' in p for p in paths)}")

    # ---- section 6: the carry-over
    pr = dict((k, v.replace(MINUS, "-")) for k, v in re.findall(r"(T[1-6]) ([+" + MINUS + r"]0\.[0-9]{3})", R[102] + " " + R[103]))
    s6 = {}
    for b in BLOCKS:
        k = train_of[b]
        cs = {o: [c for p in red["blocks"][str(b)]["process_info"] if p["orientation"] == o for c in p["carry_L3_minus_L2"]]
              for o in ("SFFS", "FSSF")}
        est = sc["trains"][k]["mean"]
        diff = st.mean(cs["SFFS"]) - st.mean(cs["FSSF"])
        kit = diff / (2 * est)
        com = sc["reported"]["trains"][k]["carry_over"]
        s6[k] = {"SFFS_mean_L3_minus_L2": r6(st.mean(cs["SFFS"])), "n_SFFS": len(cs["SFFS"]),
                 "FSSF_mean_L3_minus_L2": r6(st.mean(cs["FSSF"])), "n_FSSF": len(cs["FSSF"]), "difference": r6(diff),
                 "estimate": r6(est), "over_twice_the_estimate": r6(kit), "scored_e183_json": r6(com),
                 "kit_equals_scored_within_1e-12": abs(kit - com) < 1e-12, "readme": pr.get(k),
                 "readme_same_at_3dp": pr.get(k) == "%+.3f" % kit, "over_the_estimate_alone": r6(diff / est)}
    J["s6_carry_over"] = s6
    P("")
    P("## 6. The carry-over reading: SFFS mean(L3 - L2) less FSSF's, and its divisor")
    for k, e in s6.items():
        P(f"  {k}: SFFS {e['SFFS_mean_L3_minus_L2']:+.5f} (n {e['n_SFFS']}), FSSF {e['FSSF_mean_L3_minus_L2']:+.5f} (n {e['n_FSSF']}), "
          f"difference {e['difference']:+.5f}, estimate {e['estimate']:+.5f}; over twice the estimate {e['over_twice_the_estimate']:+.3f} "
          f"(scored-e183.json {e['scored_e183_json']:+.3f}, equal: {e['kit_equals_scored_within_1e-12']}; README {e['readme']}: "
          f"{'same' if e['readme_same_at_3dp'] else 'DIFFERS'}); over the estimate alone {e['over_the_estimate_alone']:+.3f}")

    # ---- section 7: the card lock and timeout 10 in the pinned code
    sha = {f: hashlib.sha256(open(path(f), "rb").read()).hexdigest() for f in CODE}
    pins = {}
    for b in BLOCKS:
        cs = {}
        for ln in open(os.path.join(D, "raw", "e183", "p%d" % b, "code.sha256"), encoding="utf-8"):
            if "  " in ln:
                h, f = ln.rstrip("\n").split("  ", 1)
                cs[f] = h
        pins[str(b)] = {f: (cs.get(f) == sha[f]) for f in CODE}
    J["s7_lock_and_timeout"] = {"files_sha256": sha, "each_block_pins_the_same": pins,
                                "lines": [e for e in s0 if e["file"] in CODE]}
    P("")
    P("## 7. The card lock and timeout 10 in the code each block pinned (a desk read of code; the session's files print neither)")
    for f in CODE:
        P(f"  {f}: sha256 {sha[f][:16]}..., pinned at these bytes in {sum(1 for b in BLOCKS if pins[str(b)][f])} of 6 blocks' code.sha256")
    for e in J["s7_lock_and_timeout"]["lines"]:
        P(f"  {'OK ' if e['anchor_found'] else 'MISSING'} {e['file']}:{e['line']}  {e['label']}")
    P("")
    P("SPDX-License-Identifier: Apache-2.0")

    os.makedirs(OUT, exist_ok=True)
    with open(os.path.join(OUT, "posthoc-note1-e183.json"), "w", encoding="utf-8") as fh:
        json.dump(J, fh, indent=1, sort_keys=False, ensure_ascii=True)
        fh.write("\n")
    with open(os.path.join(OUT, "posthoc-note1-e183.txt"), "w", encoding="utf-8") as fh:
        fh.write("\n".join(X) + "\n")
    print("\n".join(X))
    return 0


if __name__ == "__main__":
    sys.exit(main())
