#!/usr/bin/env python3
"""The blind days' measured passes, read from their committed data directories, for ledger v3's freeze and readings.

    /usr/bin/python3 -I -B tools/ledger/measured_ledger_v3.py [--out FILE]

Per pass (every pass of every configuration; none of these days set a pass aside): the slowest minion's kernel cycles
(host-raw.json hart0_cycles.max for the ledger host, host.json kernel.cycles_max for sparse parity) and t_k = those
cycles / the day's registered clock (600 MHz; E194 800 MHz, its scorer's rule), the wall seconds a launch t_w =
1 / energy.json solves_per_s, the launches, the starting die (energy.json die_c.before), J over idle a launch
(board.j_per_solve) and J with the card at rest a launch (board.j_per_solve_total). MEASURED; the means are desk
arithmetic. Standard library only. SPDX-License-Identifier: Apache-2.0
"""
import argparse
import json
import os
import statistics as st
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
DATA = "docs/reports/data"
DAYS = {
    "E189": {"dir": "2026-11-14-e189-blind-day-aifoundry3", "card": "aifoundry3", "f_hz": 600e6, "data_commit": "fa9098c4",
             "label": "blind (the registered day); its frozen scores stand"},
    "E191s2": {"dir": "2026-11-15-e191-blind-day-aifoundry1-c1-s2", "card": "aifoundry1-c1", "f_hz": 600e6,
               "data_commit": "7156ac15", "label": "blind (the registered second session); its frozen scores stand"},
    "E191s3": {"dir": "2026-11-16-e191-blind-day-aifoundry1-c1-s3", "card": "aifoundry1-c1", "f_hz": 600e6,
               "data_commit": "a28e4f3e", "label": "REPORTED repeat (E191 amendment A2), never a verdict"},
    "E194": {"dir": "2026-11-16-e194-blind-day-aifoundry2", "card": "aifoundry2", "f_hz": 800e6, "data_commit": "72514ce5",
             "label": "blind under the frozen v2 (registered after E189's data); its frozen scores stand"},
}
CONFIGS = ("copy-zeros", "copy-random", "sha256", "sort-sorted", "sort-shuffled", "sparse-parity")
KEYS = ("t_k", "t_w", "T0", "j_over", "j_total", "cycles_max", "launches")


def read_day(day, repo=REPO):
    info = DAYS[day]
    base = os.path.join(repo, DATA, info["dir"], "passes")
    out = {}
    for cfg in CONFIGS:
        d = os.path.join(base, cfg)
        passes = []
        for p in sorted(os.listdir(d), key=lambda x: int(x.lstrip("p"))):
            pd = os.path.join(d, p)
            e = json.load(open(os.path.join(pd, "energy.json")))
            if cfg == "sparse-parity":
                cyc = json.load(open(os.path.join(pd, "host.json")))["kernel"]["cycles_max"]
            else:
                cyc = json.load(open(os.path.join(pd, "host-raw.json")))["hart0_cycles"]["max"]
            passes.append({"pass": p, "cycles_max": cyc, "t_k": cyc / info["f_hz"], "t_w": 1.0 / e["solves_per_s"],
                           "launches": e["solves"], "T0": e["die_c"]["before"], "j_over": e["board"]["j_per_solve"],
                           "j_total": e["board"]["j_per_solve_total"], "ok": e.get("ok")})
        mean = {k: st.mean(x[k] for x in passes) for k in KEYS}
        mean["j_over_sd_rel"] = st.stdev(x["j_over"] for x in passes) / mean["j_over"] if len(passes) > 1 else None
        out[cfg] = {"passes": passes, "n": len(passes), "mean": mean}
    return out


def read_all(repo=REPO):
    return {d: {"info": DAYS[d], "configs": read_day(d, repo)} for d in DAYS}


def main(argv):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--out")
    a = ap.parse_args(argv)
    res = read_all()
    for d, v in res.items():
        for cfg, c in v["configs"].items():
            m = c["mean"]
            print(f"{d:7s} {cfg:14s} n {c['n']}  t_k {m['t_k']:.5f}  t_w {m['t_w']:.5f}  T0 {m['T0']:.2f}  "
                  f"J/idle {m['j_over']:.4f}  J total {m['j_total']:.4f}  launches {m['launches']:.2f}")
    if a.out:
        json.dump(res, open(a.out, "w"), indent=1, sort_keys=True)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
