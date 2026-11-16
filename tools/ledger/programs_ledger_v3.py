#!/usr/bin/env python3
"""Plain programs for ledger v3, built from the counter's committed counts: the blind day's five, and any new configuration.

    /usr/bin/python3 -I -B tools/ledger/programs_ledger_v3.py [--out FILE]      # the blind day's five programs

THE COUNTS are exactly the ones ledger v2 priced: workloads/ledger/ledger_estimate.py's own estimate() (pinned, never
edited) over Q166's committed simulator runs (docs/reports/data/2026-11-12-q166-progs/runs, 64 participants of shire
0, two runs a configuration, scaled by arithmetic), with E189's dated change (the sort at 1,800 sorts a launch: its CARD
entries given reps 1800 before estimate() runs, as tools/claims-v3/e189/forecast_e189.py did). Two of estimate()'s own
calls are watched, not changed: by_class_total(total) gives a program's whole counts, and price_counts() the counts v2
priced (a copy's without its moves). A program is then described for ledger_v3.program(): counts a participant, the
lines past the L1 a unit from tools/counter/l1_model.py (the sort through tools/counter/ledger_interp.py's trace,
SHA-256 and the copy from the disassembly's access order), its working set a hart, a copy's bytes and data, and v2's
own byte description (the rules-off path).

A NEW CONFIGURATION (for example E201's): programs_from_estimate() with its own CARD and CASES entries and runs folder,
in estimate()'s own forms; the lines come from the same L1 model at its own sizes.

Desk only: no device, no simulator. Standard library only. SPDX-License-Identifier: Apache-2.0
"""
import argparse
import importlib.util
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.normpath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(REPO, "tools", "counter"))
import ledger_v3 as V3  # noqa: E402

PROGS = "docs/reports/data/2026-11-12-q166-progs"
SORT_REPS = 1800                    # E189's dated change (E189.md section 4.3)
P = 2048
GiB = 1 << 30
# rule 7's launches a burst: E189's K, which E194 kept (tools/claims-v3/e194/forecast_e194.py K_E189)
K_E189 = {"copy-zeros": 8, "copy-random": 8, "sha256": 9, "sort-sorted": 8, "sort-shuffled": 7, "sparse-parity": 9}
SHA_FRAME_B, SHA_K_B, SHA_ST_B = 352, 256, 32      # sha256_compress's frame, K256, the caller's state (the disassembly)


def _estimate_module(repo=REPO):
    V3.mods(repo)                     # checks ledger_estimate.py's pin
    spec = importlib.util.spec_from_file_location("ledger_estimate_v3prog", os.path.join(repo, "workloads/ledger/ledger_estimate.py"))
    le = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(le)
    return le


def run_estimate(card_cfgs=None, cases=None, runs=None, dis=None, repo=REPO):
    """estimate() over the runs, with CARD (and CASES) entries replaced where given; returns {key: (record, whole
    counts, priced counts)} in CARD's order."""
    le = _estimate_module(repo)
    if card_cfgs is None:
        for k in ("sort-sorted", "sort-shuffled"):
            le.CARD[k]["reps"] = SORT_REPS
            le.CARD[k]["args"] = le.CARD[k]["args"].replace("--reps 1500", f"--reps {SORT_REPS}")
    else:
        le.CARD.clear()
        le.CARD.update(card_cfgs)
        le.CASES.clear()
        le.CASES.update(cases)
    whole, priced = [], []
    o_pc, o_bc = le.price_counts, le.by_class_total

    def w_pc(cat, counts, data="random", inplace_hi=True):
        priced.append(dict(counts))
        return o_pc(cat, counts, data, inplace_hi)

    def w_bc(total):
        whole.append(dict(total))
        return o_bc(total)
    le.price_counts, le.by_class_total = w_pc, w_bc
    import argparse as _ap
    ea = _ap.Namespace(runs=runs or os.path.join(repo, PROGS, "runs"), repo=repo,
                       dis=dis or os.path.join(repo, PROGS, "kernel", "ledger.dis.gz"), t0=55.0, spp_dry=None,
                       spp_slices=None, spp_sites=None, spp_dis=None, out=None)
    res = le.estimate(ea)
    le.price_counts, le.by_class_total = o_pc, o_bc
    keys = list(le.CARD)
    if len(whole) != len(keys) or len(priced) != len(keys):
        raise SystemExit(f"programs_ledger_v3: estimate() made {len(whole)} / {len(priced)} calls for {len(keys)} programs")
    return {k: (res["programs"][k], whole[i], priced[i]) for i, k in enumerate(keys)}, le


def build(key, r, whole, priced, card, f_mhz=600.0, lines=None, launches_a_burst=None):
    """One estimate() record as a ledger_v3 program on `card`."""
    cfg = r["config"]
    Pp = cfg["participants"]
    prog = cfg["prog"]
    counts = {m: n / Pp for m, n in sorted(whole.items())}
    if prog == "copy":
        part = cfg["bytes"] // Pp
        nbytes = cfg["bytes"] * cfg["passes"]
        L = lines if lines is not None else lines_for(prog, part=part)
        lines_a_launch = {k: L[k] * cfg["passes"] for k in ("fills", "read_fills", "write_fills", "dirty_evictions")}
        moves_counted = {m: whole.get(m, 0) - priced.get(m, 0) for m in V3.MOVES}
        return V3.program(key, "copy", card, counts, Pp, units=cfg["passes"], unit=f"pass over {part} B a hart",
                          f_mhz=f_mhz, lines=dict(lines_a_launch, per_unit=L), working_set_b_per_hart=2 * part,
                          copy={"bytes": nbytes, "data": cfg.get("data", "random"), "part_bytes_per_hart": part,
                                "passes": cfg["passes"], "moves_counted": moves_counted},
                          v2_bytes={"note": "a copy: v2's DRAM terms (no L2 term)"},
                          launches_a_burst=launches_a_burst)
    bt = [v for k, v in r["terms"].items() if k.startswith("bytes past the L1")][0]
    if prog == "sha256":
        units = cfg["repeat"] * (cfg["block"] // 64) + 1            # the compressions and the padding block
        L = lines if lines is not None else lines_for("sha256")
        lines_a_launch = {k: L[k] * units for k in ("fills", "read_fills", "write_fills", "dirty_evictions")}
        v2b = {"bytes_point": bt["lines_point"] * 64, "bytes_high": bt["lines_high"] * 64, "lines_high": bt["lines_high"]}
        ws = cfg["block"] + SHA_FRAME_B + SHA_K_B + SHA_ST_B
        return V3.program(key, "scalar", card, counts, Pp, units=units, unit="64 B block (one compression)",
                          f_mhz=f_mhz, lines=dict(lines_a_launch, per_unit=L), working_set_b_per_hart=ws, v2_bytes=v2b,
                          launches_a_burst=launches_a_burst)
    n = cfg["keys"]
    units = cfg["reps"]
    L = lines if lines is not None else lines_for("sort", keys=n, order=cfg["order"])
    lines_a_launch = {k: L[k] * units for k in ("fills", "read_fills", "write_fills", "dirty_evictions")}
    v2b = {"bytes_point": bt["bytes_point"], "bytes_high": bt["bytes_point"] * 1.5, "lines_high": bt["bytes_point"] / 64.0}
    return V3.program(key, "scalar", card, counts, Pp, units=units, unit=f"sort of {n} keys", f_mhz=f_mhz,
                      lines=dict(lines_a_launch, per_unit=L), working_set_b_per_hart=3 * 4 * n, v2_bytes=v2b,
                      launches_a_burst=launches_a_burst)


_LINES = {}


def lines_for(prog, keys=None, order=None, part=None):
    """Lines past the L1 a unit from tools/counter/l1_model.py (cached)."""
    import l1_model as L1  # noqa: E402
    key = (prog, keys, order, part)
    if key not in _LINES:
        if prog == "sort":
            r = L1.sort_lines(keys, order)
        elif prog == "sha256":
            r = L1.sha256_lines()
        else:
            r = L1.copy_lines(part)
        _LINES[key] = {k: r[k] for k in ("fills", "read_fills", "write_fills", "dirty_evictions", "fills_range",
                                          "dirty_evictions_range")}
    return _LINES[key]


_EST = {}


def blind_day_programs(card, f_mhz=600.0, repo=REPO):
    """The blind day's five plain programs (E189's configurations) on `card` at f_mhz (estimate() run once a process)."""
    if repo not in _EST:
        _EST[repo] = run_estimate(repo=repo)[0]
    est = _EST[repo]
    return {k: build(k, r, w, p, card, f_mhz=f_mhz, launches_a_burst=K_E189.get(k)) for k, (r, w, p) in est.items()}


def programs_from_estimate(card_cfgs, cases, runs, card, dis=None, f_mhz=600.0, lines=None, launches=None, repo=REPO):
    """New configurations in estimate()'s own forms (CARD entries and CASES pairs over a runs folder): ledger_v3
    programs on `card`. lines: {key: lines a unit} to use instead of the L1 model's; launches: {key: K}."""
    est, _ = run_estimate(card_cfgs=card_cfgs, cases=cases, runs=runs, dis=dis, repo=repo)
    lines = lines or {}
    launches = launches or {}
    return {k: build(k, r, w, p, card, f_mhz=f_mhz, lines=lines.get(k), launches_a_burst=launches.get(k))
            for k, (r, w, p) in est.items()}


def main(argv):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--card", default="aifoundry3")
    ap.add_argument("--out")
    a = ap.parse_args(argv)
    progs = blind_day_programs(a.card)
    for k, p in progs.items():
        N = sum(p["counts"].values())
        B = p["counts"].get("@taken", 0) + p["counts"].get("@jump", 0)
        print(f"{k:14s} N {N:.6g} a participant, B {B:.6g} ({100 * B / N:.2f}%), units {p['units']}, "
              f"fills a launch {p['lines'].get('fills', 0):.6g}, working set {p['working_set_b_per_hart']} B a hart")
    if a.out:
        json.dump(progs, open(a.out, "w"), indent=1, sort_keys=True)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
