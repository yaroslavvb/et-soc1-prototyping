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
following record (null if it did not) and the seconds left in the log.
"""
import argparse
import datetime
import glob
import gzip
import json
import os
import re
import sys

ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
DATA = os.path.join(ROOT, "docs", "reports", "data", "2026-09-20-power-aifoundry2")
SESSIONS = [("thermal", "Load step (E5)"), ("horace", "Horace, uncontrolled (E7)"), ("horace2", "Horace, 80 °C starts (E8)")]
LOCAL = datetime.timezone(datetime.timedelta(hours=-7))


def fields(r):
    m, sp = r["temp_c"]["minshire"], r["sp"]["minion_c"]
    return [m[0], m[1], m[2], sp[2], sp[1]]


def session(name, label):
    tel = [json.loads(l) for l in open(os.path.join(DATA, name + "-telemetry.jsonl")) if l.startswith("{")]
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
    return {"id": name, "label": label, "start": start, "seconds": round((tel[-1]["t_ms"] - t0) / 1000, 1),
            "hz": round(1000 / dt), "n": len(tel), "pmic_eq_mean": pmic_diff.count(0), "pmic_diff_max": max(pmic_diff),
            "system_c_zero": sum(1 for r in tel if r["sp"]["system_c"] == [0, 0, 0]), "rows": rows}


def cards():
    out = {}
    base = os.path.join(ROOT, "docs", "reports", "data")
    for path in sorted(glob.glob(os.path.join(base, "**", "*telemetry*.jsonl*"), recursive=True)):
        rel = os.path.relpath(path, base)
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


def consts():
    ht = {"fields": ["t_s", "mean", "low", "high", "sp_max", "sp_min"],
          "source": "docs/reports/data/2026-09-20-power-aifoundry2/{thermal,horace,horace2}-telemetry.jsonl; "
                    "tools/ettelem/host_temp_fields.py",
          "sessions": [session(n, l) for n, l in SESSIONS], "cards": cards()}
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
