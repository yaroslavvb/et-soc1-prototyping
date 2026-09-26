#!/usr/bin/env python3
"""The temperature fields the host received on 20 September, as change points, for the spatial temperature brief.

    python3 tools/ettelem/host_temp_fields.py                 print the two consts the brief embeds
    python3 tools/ettelem/host_temp_fields.py --check PAGE    exit 1 unless PAGE embeds exactly these consts

Reads the three ettelem logs of 20 September in docs/reports/data/2026-09-20-power-aifoundry2/ (thermal-, horace- and
horace2-telemetry.jsonl: 3,681 samples; the Horace logs were committed thinned to 2 Hz) and prints

  const HOST_TEMP = {...};  per session: its start (the lab's local time, UTC-7), length, sampling rate and one row
                            [t_s, mean, low, high, sp_max, sp_min] at the first sample, at every sample where any
                            field changes, and at the last sample. mean, low and high are what the host's temperature
                            query returns for the 34 minion shires (temp_c.minshire: the current mean and the
                            peak-hold extremes); sp_max and sp_min are the service processor's own maximum and minimum
                            of that mean since its stats were reset (sp.minion_c[2], [1]). Also per session: how many
                            samples had pmic_sys (temp_c.pmic) equal to the mean, the largest difference otherwise,
                            and how many had the stats packet's system temperature (sp.system_c) all zero.
  const SHIRE_MV = {...};   per-shire-voltage-idle.json (the idle voltage map of the same evening), for the grid toggle.

HOST_TEMP.cards checks the same fields on both cards, over every committed ettelem log that has them
(docs/reports/data/**/*telemetry*.jsonl[.gz], 20-24 Sep): per card, the number of logs and samples, the distinct
[SP minimum, low] and end-of-log [SP maximum, high] pairs, every rise of the high with the mean and the SP maximum
at that sample and the seconds since the SP maximum last rose and until it next rose (null if not in the log), and
every new record of the SP maximum with the high at that sample, the seconds until the high next rose before the
following record (null if it did not) and the seconds left in the log. Only data directories dated 20-24 September
count (HISTORY_LAST_DAY): the block is the check as published on 25 September, and later data has its own block.

HOST_TEMP.v3 (added 26 September 2026) is the version-3 check of the same fields on three cards: V3-TEL's X3 reset
windows (docs/reports/data/2026-09-25-claims-v3/raw/<card>/tel/p<N>/dbg/x3-w<k>.jsonl.gz, kept passes only, whose
block.json says ok; windows 1-3 hold a 7 s random-data burst, window 4 is idle; tools/claims-v3/tel/README.md), with
the definitions of the X3 reducer that item TEL-R uses: a window's reset worked when, in its first second, low >=
mean - 2 and high <= mean + 3; at each rise of the high, high - mean at that sample; at the window's last sample,
high - SP maximum and low - SP minimum. Also low - SP minimum at every sample whose SP minimum is valid (not 65535,
the value right after a reset), and each kept pass's idle map of the minion rail (dbg/x2-idle.bin, parsed by
parse_sptrace_voltage.parse; only complete captures, those in which all 34 shires printed in one pass, count), and
the number of "Temp [C]" lines in every DEBUG capture (dbg/*.bin). Counts are [value, count] pairs.
HOST_TEMP.sessions also gets one of those windows per card for the chart (the first window of each card's first kept
pass, from its first sample with valid SP statistics), marked with its card; the brief's prose about 20 September
reads only the three sessions without a card.
"""
import argparse
import collections
import datetime
import glob
import gzip
import io
import json
import os
import re
import sys

ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
DATA = os.path.join(ROOT, "docs", "reports", "data", "2026-09-20-power-aifoundry2")
SESSIONS = [("thermal", "Load step (E5)"), ("horace", "Horace, uncontrolled (E7)"), ("horace2", "Horace, 80 °C starts (E8)")]
LOCAL = datetime.timezone(datetime.timedelta(hours=-7))
HISTORY_LAST_DAY = "2026-09-24"
V3 = os.path.join(ROOT, "docs", "reports", "data", "2026-09-25-claims-v3", "raw")
V3_CARDS = ("aifoundry2", "aifoundry3", "aifoundry1-c1")
SP_UNSET = 65535   # the SP's minimum right after a reset of its statistics


def fields(r):
    m, sp = r["temp_c"]["minshire"], r["sp"]["minion_c"]
    return [m[0], m[1], m[2], sp[2], sp[1]]


def read_log(path):
    op = gzip.open if path.endswith(".gz") else open
    return [json.loads(l) for l in op(path, "rt") if l.startswith("{")]


def session(name, label, tel=None, extra=None):
    if tel is None:
        tel = read_log(os.path.join(DATA, name + "-telemetry.jsonl"))
    t0 = tel[0]["t_ms"]
    rows, prev = [], None
    for k, r in enumerate(tel):
        v = fields(r)
        if v != prev or k == len(tel) - 1:
            rows.append([round((r["t_ms"] - t0) / 1000, 1)] + v)
            prev = v
    dt = sorted(b["t_ms"] - a["t_ms"] for a, b in zip(tel, tel[1:]))[len(tel) // 2]
    start = datetime.datetime.fromtimestamp(t0 / 1000, LOCAL).strftime("%H:%M")
    pmic_diff = [abs(r["temp_c"]["pmic"] - r["temp_c"]["minshire"][0]) for r in tel]
    out = {"id": name, "label": label, "start": start, "seconds": round((tel[-1]["t_ms"] - t0) / 1000, 1),
           "hz": round(1000 / dt), "n": len(tel), "pmic_eq_mean": pmic_diff.count(0), "pmic_diff_max": max(pmic_diff),
           "system_c_zero": sum(1 for r in tel if r["sp"]["system_c"] == [0, 0, 0]), "rows": rows}
    out.update(extra or {})
    return out


def cards():
    out = {}
    base = os.path.join(ROOT, "docs", "reports", "data")
    for path in sorted(glob.glob(os.path.join(base, "**", "*telemetry*.jsonl*"), recursive=True)):
        rel = os.path.relpath(path, base)
        if rel[:10] > HISTORY_LAST_DAY:
            continue
        op = gzip.open if path.endswith(".gz") else open
        rows = []
        for line in op(path, "rt"):
            if not line.startswith("{"):
                continue
            r = json.loads(line)
            try:
                m, sp = r["temp_c"]["minshire"], r["sp"]["minion_c"]
            except (KeyError, TypeError):
                continue
            rows.append((r["t_ms"], m[0], m[1], m[2], sp[1], sp[2]))  # t, mean, low, high, sp_min, sp_max
        if not rows:
            continue
        c = out.setdefault(re.search(r"aifoundry\d", rel).group(0), {"logs": 0, "samples": 0, "dates": [], "low_pairs": set(),
                                                                      "end_pairs": set(), "rises": [], "records": []})
        c["logs"] += 1; c["samples"] += len(rows); c["dates"].append(rel[:10])
        c["low_pairs"].update((r[4], r[2]) for r in rows)
        c["end_pairs"].add((rows[-1][5], rows[-1][3]))
        t0, rec = rows[0][0], [rows[i][0] for i in range(1, len(rows)) if rows[i][5] > rows[i - 1][5]]
        hi_up = [rows[i][0] for i in range(1, len(rows)) if rows[i][3] > rows[i - 1][3]]
        for i in range(1, len(rows)):  # each new record of the mean, and whether the high rose before the next one
            if rows[i][5] > rows[i - 1][5]:
                t = rows[i][0]
                nxt = min([x for x in rec if x > t], default=None)
                up = [x for x in hi_up if x >= t and (nxt is None or x < nxt)]
                c["records"].append({"log": rel.split("/")[0], "t_s": round((t - t0) / 1000, 1), "sp_max": rows[i][5],
                                     "high": rows[i][3], "high_rose_after_s": round((up[0] - t) / 1000, 1) if up else None,
                                     "log_left_s": round((rows[-1][0] - t) / 1000, 1)})
        for i in range(1, len(rows)):
            if rows[i][3] > rows[i - 1][3]:
                t = rows[i][0]
                before = [t - x for x in rec if x <= t]
                after = [x - t for x in rec if x > t]
                c["rises"].append({"log": rel.split("/")[0], "t_s": round((t - t0) / 1000, 1), "high": rows[i][3],
                                   "mean": rows[i][1], "sp_max": rows[i][5],
                                   "since_record_s": round(min(before) / 1000, 1) if before else None,
                                   "until_record_s": round(min(after) / 1000, 1) if after else None})
    for c in out.values():
        c["dates"] = [min(c["dates"]), max(c["dates"])]
        c["low_pairs"] = sorted(map(list, c["low_pairs"]))
        c["end_pairs"] = sorted(map(list, c["end_pairs"]))
    return out


def v3_passes(card):
    """A card's kept V3-TEL pass directories (block.json status ok), in pass order."""
    ps = glob.glob(os.path.join(V3, card, "tel", "p*"))
    ps = [p for p in ps if re.fullmatch(r"p\d+", os.path.basename(p))
          and json.load(open(os.path.join(p, "block.json"))).get("status") == "ok"]
    return sorted(ps, key=lambda p: int(os.path.basename(p)[1:]))


def v3():
    """HOST_TEMP.v3: the version-3 check's X3 windows and DEBUG captures, per card (see the module docstring)."""
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import parse_sptrace_voltage as psv
    pairs = lambda c: sorted(map(list, c.items()))
    out = {"source": "docs/reports/data/2026-09-25-claims-v3/raw/<card>/tel/p<N>/dbg/ (V3-TEL); "
                     "tools/ettelem/host_temp_fields.py", "cards": {}}
    for card in V3_CARDS:
        P = v3_passes(card)
        if not P:
            continue
        win = collections.Counter(); reset_ok = collections.Counter(); samples = 0
        rises = collections.Counter(); end_hi = {"load": collections.Counter(), "idle": collections.Counter()}
        end_lo = collections.Counter(); lo_all = collections.Counter(); clock = collections.Counter(); temp_lines = captures = 0
        maps = {"complete": 0, "captures": 0, "now": [], "low": [], "high": []}
        for p in P:
            for k in (1, 2, 3, 4):
                path = os.path.join(p, "dbg", "x3-w%d.jsonl.gz" % k)
                if not os.path.exists(path):
                    continue
                kind = "idle" if k == 4 else "load"
                tel = read_log(path)
                R = [(r["t_ms"] / 1000,) + tuple(r["temp_c"]["minshire"][:3]) + (r["sp"]["minion_c"][1], r["sp"]["minion_c"][2])
                     for r in tel]                       # t, mean, low, high, sp_min, sp_max
                clock.update(r["sp"]["minion_mhz"][0] for r in tel)
                win[kind] += 1; samples += len(R)
                reset_ok[kind] += all(x[2] >= x[1] - 2 and x[3] <= x[1] + 3 for x in R if x[0] - R[0][0] <= 1.0)
                if kind == "load":
                    rises.update(R[i][3] - R[i][1] for i in range(1, len(R)) if R[i][3] > R[i - 1][3])
                end_hi[kind][R[-1][3] - R[-1][5]] += 1
                end_lo[R[-1][2] - R[-1][4]] += 1
                lo_all.update(x[2] - x[4] for x in R if x[4] != SP_UNSET)
            for f in sorted(glob.glob(os.path.join(p, "dbg", "*.bin"))):
                captures += 1; temp_lines += open(f, "rb").read().count(b"Temp [C]")
            idle = os.path.join(p, "dbg", "x2-idle.bin")
            if os.path.exists(idle):
                maps["captures"] += 1
                w = io.StringIO(); m = psv.parse(open(idle, "rb").read(), warn=w)
                if not w.getvalue() and len(m) == psv.NSHIRES:
                    maps["complete"] += 1
                    for key, j in (("now", 0), ("low", 1), ("high", 2)):
                        maps[key] += [v["mnn"][j] for v in m.values()]
        mp = {"captures": maps["captures"], "complete": maps["complete"]}
        if maps["complete"]:
            mp.update({"now": [min(maps["now"]), max(maps["now"])], "low_high": [min(maps["low"]), max(maps["high"])]})
        out["cards"][card] = {"passes": len(P), "windows": dict(win), "reset_ok": dict(reset_ok), "samples": samples,
                              "minion_mhz": pairs(clock),
                              "rise_minus_mean": pairs(rises), "end_high_minus_spmax": {k: pairs(v) for k, v in end_hi.items()},
                              "end_low_minus_spmin": pairs(end_lo), "low_minus_spmin_samples": pairs(lo_all),
                              "debug_captures": captures, "temp_lines": temp_lines, "idle_minion_map": mp}
    return out


def v3_sessions():
    """One X3 window per card for the chart: window 1 of the card's first kept pass, from its first sample with valid
    SP statistics."""
    out = []
    for card in V3_CARDS:
        P = v3_passes(card)
        path = os.path.join(P[0], "dbg", "x3-w1.jsonl.gz") if P else None
        if not path or not os.path.exists(path):
            continue
        tel = read_log(path)
        tel = tel[next(i for i, r in enumerate(tel) if r["sp"]["minion_c"][1] != SP_UNSET):]
        day = datetime.datetime.fromtimestamp(tel[0]["t_ms"] / 1000, LOCAL).strftime("%Y-%m-%d")
        out.append(session("v3-" + card, card + ", reset window", tel,
                           {"card": card, "day": day, "window": os.path.relpath(path, os.path.join(ROOT, "docs", "reports", "data"))}))
    return out


def consts():
    ht = {"fields": ["t_s", "mean", "low", "high", "sp_max", "sp_min"],
          "source": "docs/reports/data/2026-09-20-power-aifoundry2/{thermal,horace,horace2}-telemetry.jsonl; "
                    "tools/ettelem/host_temp_fields.py",
          "sessions": [session(n, l) for n, l in SESSIONS] + v3_sessions(), "cards": cards(), "v3": v3()}
    mv = json.load(open(os.path.join(DATA, "per-shire-voltage-idle.json")))
    dump = lambda o: json.dumps(o, separators=(",", ":"), ensure_ascii=False)
    return ["const HOST_TEMP = %s;" % dump(ht), "const SHIRE_MV = %s;" % dump(mv)]


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--check", metavar="PAGE", help="the page that embeds the consts")
    a = ap.parse_args()
    lines = consts()
    if a.check:
        page = open(a.check, encoding="utf-8").read().splitlines()
        stale = [l.split(" = ")[0] for l in lines if l not in page]
        if stale:
            print("%s: stale or missing: %s" % (a.check, ", ".join(stale)))
            sys.exit(1)
        print("%s: up to date" % a.check)
        return
    print("\n".join(lines))


if __name__ == "__main__":
    main()
