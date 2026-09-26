#!/usr/bin/env python3
"""Turn run_hotline.sh sweeps into the numbers the brief quotes.

    D=docs/reports/data; DATA=$D/2026-09-22-hotline-aifoundry2; DATA3=$D/2026-09-22-hotline-aifoundry3
    analyze_hotline.py $DATA/sweep.jsonl $DATA3/sweep.jsonl --power $DATA/power.json --context $DATA/context.json \
        --barrier $D/2026-09-18-nocbench-aifoundry2/barrier-chip1.jsonl --out $DATA/hotline.json

Nothing is fitted except the one-per-shire round trip against mesh hops. Every other number is a count of
completed operations in a common, barrier-aligned window, or a ratio of two such counts. The host shire is the
one that homes the contended line; "alone" is the same shire doing the same local work with no other shire
launched.

The 'context' block: the remote atomic's round trip (the window over the ops of the one-requester row), the
bank's service time (the median cycles per op of the placement rows with a single home) and the window are
computed from the sweeps; the chip-wide barrier is read from --barrier (NOCBENCH cycles_per_iter_max, one
minion per shire); the errata text and the window table (whose 5, 40 and 100 ms runs are in no raw data file)
are hand-kept in --context. 'layout' and 'empty' are marty1885's shire map from workloads/nocbench/analyze.py,
and 'share_fit' fits each card's one-per-shire round trip (window / ops) against Manhattan hops from shire 0.

--v3 RAW (added 26 September 2026 for the three-card check): read the hot-line passes of the version-3 claims check
instead of, or as well as, sweep files. RAW is docs/reports/data/2026-09-25-claims-v3/raw; every
RAW/<card>/lat/p*/hl/sweep.jsonl whose block.json says "ok" and whose marks.jsonl ends the hl unit is read (the
V3-LAT reducer kept every one of these passes on aifoundry2, aifoundry3 and aifoundry1-c1: results/lat.json,
LAT-H). Each configuration of a card is reduced to one row, the mean over that card's passes field by field (the
per-shire ops and shares shire by shire), which is what the reducer's "magnitudes on pass means" use; the host's
counts also keep their range over the passes (host_ops_lo, host_ops_hi) and every row says n_passes. The plan's
extras are used as follows: 'req' rows (edge N = 19, 21, 22, 23) join the requester sweep; 'alone' rows (the host
shire's N minions alone) give requesters and pollers frac_of_alone_n, the host against its own N-minion rate alone
(LAT-H P2, P5, P6); 'win' rows with the 10 ms rows give 'windows' (the host's count at 5, 10, 40 and 100 ms for
each home, measured, which replaces the hand-kept window table of --context); 'warm' rows with the standard
5-load warm-up rows give 'warmup' (the warm-up is read from configs.txt, since the NOCBENCH line does not print
it); 'poll' rows give 'pollers' (31 remote minions, one per shire). Cards are listed in the chart kit's registry
order (aifoundry2, aifoundry3, aifoundry1-c1), so the first card, which sets 'context' and 'shares_home0', is
aifoundry2 as before.

    D=docs/reports/data; DATA=$D/2026-09-22-hotline-aifoundry2
    analyze_hotline.py --v3 $D/2026-09-25-claims-v3/raw --power $DATA/power.json --context $DATA/context.json \
        --barrier $D/2026-09-18-nocbench-aifoundry2/barrier-chip1.jsonl --out $DATA/hotline.json
"""
import argparse
import collections
import glob
import importlib.util
import json
import os
import re

import numpy as np


def nocbench():
    """workloads/nocbench/analyze.py: marty1885's shire map (MARTY, EMPTY), hops() and load() of NOCBENCH lines."""
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "analyze.py")
    spec = importlib.util.spec_from_file_location("nocbench_analyze", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def load(paths):
    rows = []
    for p in paths:
        for line in open(p):
            if line.strip():
                rows.append(json.loads(line))
    return rows


def host_shire(r):
    spec = r["home"].split(":")[-1]
    return None if spec == "own" else int(spec)


# the chart kit's card registry order (docs/reports/sources/chartkit.js, CK.cards); other cards follow, sorted
CARD_ORDER = ["aifoundry2", "aifoundry3", "aifoundry1-c1", "aifoundry1-c0"]


def card_order(cards):
    return [c for c in CARD_ORDER if c in cards] + sorted(c for c in cards if c not in CARD_ORDER)


def load_v3(root):
    """The hot-line passes of the claims-v3 LAT blocks under root: <root>/<card>/lat/p*/hl/sweep.jsonl of every block
    whose block.json says ok and whose hl unit ended; each line gets 'warmup' from its configuration's arguments."""
    rows = []
    for d in sorted(glob.glob(os.path.join(root, "*", "lat", "p*", "hl"))):
        blk = os.path.dirname(d)
        txt = open(os.path.join(blk, "block.json")).read()
        m = re.search(r'"status"\s*:\s*"(\w+)"', txt)       # block.json can be invalid JSON ('"die_c_end":,')
        if not m or m.group(1) != "ok":
            continue
        marks = [json.loads(l) for l in open(os.path.join(blk, "marks.jsonl")) if l.strip()]
        if not any(k.get("ev") == "end" and k.get("unit") == "hl" for k in marks):
            continue
        args = {}
        for line in open(os.path.join(d, "configs.txt")):
            if line.strip():
                cid, _, arg = line.rstrip("\n").split("|", 2)
                w = re.findall(r"--warmup (\d+)", arg)
                args[int(cid)] = int(w[-1]) if w else 5        # block.sh passes --warmup 5 before each configuration's own
        for r in load([os.path.join(d, "sweep.jsonl")]):
            r["warmup"] = args.get(r.get("cfg"), 5)
            r["src"] = os.path.relpath(d)
            rows.append(r)
    return rows


def pass_mean(rs):
    """One row from a configuration's passes on one card: every number the mean over the passes (per-shire ops and
    shares shire by shire); the host's count also as its range over the passes; n_passes."""
    if len(rs) == 1 and "pass" not in rs[0]:
        return rs[0]
    out = {}
    for k, v in rs[0].items():
        if k == "shire":
            continue
        if isinstance(v, bool) or not isinstance(v, (int, float)) or k in ("cfg", "pass", "warmup", "per_shire",
                                                                            "shires", "window_cycles", "pace"):
            out[k] = v
        else:
            out[k] = float(np.mean([r[k] for r in rs]))
    out["ok"] = all(r.get("ok", True) for r in rs)
    out["passes"] = sorted(r.get("pass") for r in rs)
    out["n_passes"] = len(rs)
    per = collections.defaultdict(list)
    for r in rs:
        for s_ in r["shire"]:
            per[s_["s"]].append(s_)
    out["shire"] = [{"s": s, "minions": v[0]["minions"],
                     **{k: float(np.mean([x[k] for x in v])) for k in ("ops", "share", "first", "last", "cycles_mean")
                        if k in v[0]}} for s, v in sorted(per.items())]
    h = host_shire(rs[0])
    if h is not None:
        ho = [next((s_["ops"] for s_ in r["shire"] if s_["s"] == h), 0) for r in rs]
        out["host_ops_lo"], out["host_ops_hi"] = min(ho), max(ho)
    return out


def collapse(rows):
    """Rows of one configuration and card (same host and cfg) -> their pass mean; rows without cfg stand alone.
    E-HL1's 'req' rows (the edge, N = 19, 21, 22, 23) are requester rows."""
    groups, order = collections.defaultdict(list), []
    for i, r in enumerate(rows):
        if r.get("group") == "req":
            r = dict(r, group="requesters")
        k = (r["host"], r["cfg"]) if "cfg" in r else (r["host"], "row", i)
        if k not in groups:
            order.append(k)
        groups[k].append(r)
    return [pass_mean(groups[k]) for k in order]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("sweeps", nargs="*")
    ap.add_argument("--v3", metavar="RAW", help="claims-v3 raw directory: every card's LAT hot-line passes (see above)")
    ap.add_argument("--power")
    ap.add_argument("--context", help="hand-kept context.json (errata, window_independence, note) to merge")
    ap.add_argument("--barrier", help="nocbench barrier-chip1.jsonl: the chip-wide barrier, one minion per shire")
    ap.add_argument("--out", required=True)
    a = ap.parse_args()
    raw = load(a.sweeps) + (load_v3(a.v3) if a.v3 else [])
    if not raw:
        ap.error("no sweep rows: give sweep files, --v3, or both")
    rows = collapse(raw)
    rows.sort(key=lambda r: (r.get("cfg") is None, r.get("cfg") or 0))   # configuration order (stable for rows without cfg)
    by_card = collections.defaultdict(list)
    for r in rows:
        by_card[r["host"]].append(r)
    out = {"cards": card_order(by_card), "fairness": [], "placement": [], "local": [], "requesters": [],
           "shires": [], "pace": []}
    if a.v3:
        out["source"] = {"v3": os.path.relpath(a.v3), "sweeps": [os.path.relpath(p) for p in a.sweeps],
                         "passes": {c: sorted({(r["src"], r["pass"]) for r in raw if r["host"] == c}) for c in out["cards"]},
                         "reduction": "each configuration of a card: the mean over its passes, field by field"}

    def shires(r):
        return {s["s"]: s for s in r["shire"]}

    for card in out["cards"]:
        rs = by_card[card]
        # The baseline is the same shire doing the same local work with nothing else launched, per minion,
        # because the pressure sweeps vary how many minions the host shire itself contributes.
        alone = {}
        for r in rs:
            if r["group"] == "local" and r["shires"] == 1:
                h0 = shires(r)[host_shire(r)]
                alone[r["home"]] = h0["ops"] / h0["minions"]
        for r in rs:
            g, sh = r["group"], shires(r)
            h = host_shire(r)
            base = {"card": card, "home": r["home"], "per_shire": r["per_shire"], "shires": r["shires"],
                    "total_ops": r["total_ops"], "cycles_per_op": r["cycles_per_op"], "pace": r.get("pace", 0)}
            if "n_passes" in r:
                base |= {k: r[k] for k in ("n_passes", "host_ops_lo", "host_ops_hi") if k in r}
            if g == "fairness":
                sl = [s["share"] for s in r["shire"]]
                out["fairness"].append(base | {"host_share": sh[h]["share"] if h in sh else None,
                                               "min_share": min(sl), "max_share": max(sl),
                                               "sd_share": float(np.std(sl))})
            elif g == "placement":
                sl = [s["share"] for s in r["shire"]]
                out["placement"].append(base | {"host_share": sh[h]["share"] if h in sh else None,
                                                "min_share": min(sl), "max_share": max(sl)})
            elif g in ("local", "requesters", "shires", "pace"):
                got = sh[h]["ops"] if h in sh else 0
                hm = sh[h]["minions"] if h in sh else 0
                b = alone.get(r["home"], 0)
                rem = [s["ops"] for k, s in sh.items() if k != h]
                out[g if g != "local" else "local"].append(
                    base | {"host_ops": got, "host_minions": hm, "host_alone_ops_per_minion": b,
                            "frac_of_alone": (got / hm) / b if (b and hm) else None,
                            "remote_minions": sum(s["minions"] for k, s in sh.items() if k != h),
                            "remote_ops_per_shire": float(np.mean(rem)) if rem else 0.0,
                            "remote_min": min(rem) if rem else 0, "remote_max": max(rem) if rem else 0})
    # E-HL1's extras (claims-v3 only): the host against its own N-minion rate alone, the windows, the warm-up and the
    # pollers. A host count is the pass mean, with its range over the passes.
    def host_of(r):
        return next((s_ for s_ in r["shire"] if s_["s"] == host_shire(r)), None)

    alone_n = {(r["host"], host_of(r)["minions"]): host_of(r)["ops"] for r in rows if r["group"] == "alone"}
    if alone_n:
        for r in out["requesters"]:
            b = alone_n.get((r["card"], r["host_minions"]))
            r["host_alone_n_ops"] = b
            r["frac_of_alone_n"] = r["host_ops"] / b if b else None
    rng = lambda r: {k: r[k] for k in ("n_passes", "host_ops_lo", "host_ops_hi") if k in r}
    wrows = [r for r in rows if r["group"] == "win" or (r["group"] == "local" and r["shires"] > 1 and "cfg" in r)]
    if any(r["group"] == "win" for r in wrows):
        out["windows"] = [{"card": r["host"], "home": r["home"], "window_cycles": r["window_cycles"],
                           "host_ops": host_of(r)["ops"], "remote_ops": r["total_ops"] - host_of(r)["ops"], **rng(r)}
                          for r in sorted(wrows, key=lambda q: (out["cards"].index(q["host"]), q["home"], q["window_cycles"]))]
    wm = [r for r in rows if (r["group"] == "warm" or (r["group"] == "local" and r["shires"] > 1 and "cfg" in r))
          and r["home"] == "scplocal:0"]
    if any(r["group"] == "warm" for r in wm):
        out["warmup"] = [{"card": r["host"], "warmup": r["warmup"], "host_ops": host_of(r)["ops"],
                          "host_minions": host_of(r)["minions"], **rng(r)}
                         for r in sorted(wm, key=lambda q: (out["cards"].index(q["host"]), q["warmup"]))]
    pl = [r for r in rows if r["group"] == "poll"]
    if pl:
        out["pollers"] = []
        for r in pl:
            h = host_of(r)
            rem = [s_ for s_ in r["shire"] if s_["s"] != host_shire(r)]
            b = alone_n.get((r["host"], h["minions"]))
            out["pollers"].append({"card": r["host"], "home": r["home"], "host_minions": h["minions"], "host_ops": h["ops"],
                                   "host_alone_n_ops": b, "frac_of_alone_n": h["ops"] / b if b else None,
                                   "remote_minions": sum(s_["minions"] for s_ in rem), "remote_shires": len(rem),
                                   "remote_ops": sum(s_["ops"] for s_ in rem),
                                   "remote_cycles_per_atomic": r["window_cycles"] / sum(s_["ops"] for s_ in rem), **rng(r)})

    # the two per-shire share curves the brief plots, from the first card in the sweep
    first = out["cards"][0]
    out["shares_home0"] = []
    for r in rows:
        if r["host"] == first and r["group"] == "fairness" and r["home"] == "0":
            kind = "full" if r["per_shire"] == 32 else "one"
            out["shares_home0"] += [{"s": s_["s"], "share": s_["share"], "kind": kind} for s_ in r["shire"]]
    if a.power:
        out["power"] = json.load(open(a.power))

    nb = nocbench()
    ctx = {}
    if a.barrier:
        b = nb.load(a.barrier)[0]
        ctx["barrier_cycles_chip"] = int(round(b["cycles_per_iter_max"]))
    # the round trip of one remote atomic: the one-requester row of the first card, window over its ops
    r1 = next(r for r in rows if r["host"] == first and r["group"] == "requesters"
              and sum(s_["minions"] for s_ in r["shire"] if s_["s"] != host_shire(r)) == 1)
    rem1 = [s_["ops"] for s_ in r1["shire"] if s_["s"] != host_shire(r1)]
    ctx["remote_atomic_latency_cycles"] = round(r1["window_cycles"] / float(np.mean(rem1)), 1)
    # the shire that one requester ran in: the round trip above is from there, with the bank idle
    ctx["remote_atomic_latency_shire"] = next(s_["s"] for s_ in r1["shire"] if s_["s"] != host_shire(r1) and s_["minions"])
    single = [r["cycles_per_op"] for r in rows if r["group"] == "placement" and not r["home"].endswith("own")]
    ctx["bank_service_cycles"] = float(np.median(single))
    if a.context:
        c = json.load(open(a.context))
        # the hand-kept window table only when no measured windows ('win' rows) are at hand
        ctx.update({k: c[k] for k in ("window_independence", "errata") if k in c and not (k == "window_independence" and "windows" in out)})
    wins = sorted({r["window_cycles"] for r in rows if r["group"] != "win"})
    ctx["window_cycles"] = wins[0] if len(wins) == 1 else wins
    if a.barrier:
        ctx["barrier_source"] = (f"{os.path.relpath(a.barrier)}: NOCBENCH cycles_per_iter_max {b['cycles_per_iter_max']}, "
                                 f"{b['participants']} participants ({b['per_shire']} per shire)")
    if a.context:
        ctx["note"] = json.load(open(a.context)).get("note")
        if "windows" in out:
            ctx["note"] = "hand-kept: errata quoted from the errata document (the window table is measured: 'windows')"
    # the round trip of one remote atomic on every card (the context's is the first card's)
    ctx["remote_atomic_latency_by_card"] = {}
    for card in out["cards"]:
        q = next((r for r in rows if r["host"] == card and r["group"] == "requesters"
                  and sum(s_["minions"] for s_ in r["shire"] if s_["s"] != host_shire(r)) == 1), None)
        if q:
            rq = [s_["ops"] for s_ in q["shire"] if s_["s"] != host_shire(q)]
            ctx["remote_atomic_latency_by_card"][card] = round(q["window_cycles"] / float(np.mean(rq)), 1)
    out["context"] = ctx

    # the mesh the charts draw, and the per-shire shares with one request each on every card
    out["layout"] = {str(k): list(v) for k, v in nb.MARTY.items()}
    out["empty"] = [list(e) for e in nb.EMPTY]
    out["shares_home0_by_card"] = {}
    out["share_fit"] = {}
    for card in out["cards"]:
        sh0 = []
        for r in rows:
            if r["host"] == card and r["group"] == "fairness" and r["home"] == "0":
                kind = "full" if r["per_shire"] == 32 else "one"
                sh0 += [{"s": s_["s"], "share": s_["share"], "kind": kind, "hops": nb.hops(s_["s"], 0)} for s_ in r["shire"]]
                if r["per_shire"] == 1:
                    h = np.array([nb.hops(s_["s"], 0) for s_ in r["shire"]], float)
                    rt = r["window_cycles"] / np.array([s_["ops"] for s_ in r["shire"]], float)
                    shares = np.array([s_["share"] for s_ in r["shire"]])
                    A = np.vstack([np.ones_like(h), h]).T
                    coef, *_ = np.linalg.lstsq(A, rt, rcond=None)
                    hm = float(1 / np.mean(1 / rt))
                    out["share_fit"][card] = {
                        "round_trip_cycles_0_hops": round(float(coef[0]), 2), "cycles_per_hop": round(float(coef[1]), 3),
                        "harmonic_mean_cycles": round(hm, 1),
                        "max_share_error": round(float(np.abs(hm / (A @ coef) - shares).max()), 4),
                        "r_share_hops": round(float(np.corrcoef(h, shares)[0, 1]), 3), "n": int(len(h)),
                        "model": "share = harmonic_mean_cycles / (round_trip_cycles_0_hops + cycles_per_hop * hops); "
                                 "round trip = window / ops, one minion per shire, home 0, hops = Manhattan distance on the shire map"}
        out["shares_home0_by_card"][card] = sh0
    json.dump(out, open(a.out, "w"), indent=1)

    print("FAIRNESS: does the shire that homes the line get its share of the atomic?")
    for r in out["fairness"]:
        print(f"  {r['card']:11s} home {r['home']:7s} {r['per_shire']:2d}/shire  host share "
              f"{r['host_share']:.4f}  spread {r['min_share']:.3f}-{r['max_share']:.3f}  sd {r['sd_share']:.4f}")
    print("\nPLACEMENT: throughput of one contended line against 32 separate lines")
    for r in out["placement"]:
        print(f"  {r['card']:11s} home {r['home']:8s} {r['total_ops']:10.0f} ops  {r['cycles_per_op']:6.2f} cycles/op")
    print("\nLOCAL: the host shire's own memory path while its shire cache is hammered")
    for r in out["local"]:
        if r["shires"] == 1:
            print(f"  {r['card']:11s} {r['home']:12s} alone: {r['host_ops']:9.0f} local ops "
                  f"({r['host_alone_ops_per_minion']:.0f} per minion)")
        else:
            print(f"  {r['card']:11s} {r['home']:12s} with {r['remote_minions']:4d} remote minions: "
                  f"{r['host_ops']:6.0f} = {100 * r['frac_of_alone']:.3f}% of alone")
    print("\nREQUESTERS: one other shire, N of its minions hammering")
    for r in out["requesters"]:
        print(f"  {r['card']:11s} {r['remote_minions']:3d} remote minions  remote "
              f"{6e6 / max(r['remote_ops_per_shire'], 1):6.1f} cycles/op  host {100 * r['frac_of_alone']:7.2f}% of alone")
    c = out["context"]
    print(f"\nCONTEXT: remote atomic {c['remote_atomic_latency_cycles']} cycles, bank {c['bank_service_cycles']} cycles per op, "
          f"window {c['window_cycles']} cycles" + (f", chip barrier {c['barrier_cycles_chip']} cycles" if "barrier_cycles_chip" in c else ""))
    for card, f in out["share_fit"].items():
        print(f"  {card}: one per shire, round trip {f['round_trip_cycles_0_hops']} + {f['cycles_per_hop']} cycles per hop; "
              f"shares within {f['max_share_error']} of {f['harmonic_mean_cycles']}/(round trip), r = {f['r_share_hops']}")
    for r in out["requesters"]:
        if r.get("frac_of_alone_n") is not None:
            print(f"  {r['card']:13s} N = {r['remote_minions']:3d}: host {100 * r['frac_of_alone_n']:7.3f}% of its {r['host_minions']}-minion rate alone")
    for r in out.get("pollers", []):
        print(f"POLLERS {r['card']:13s} {r['remote_minions']} remote minions in {r['remote_shires']} shires: remote "
              f"{r['remote_cycles_per_atomic']:.2f} cycles/atomic, host ({r['host_minions']} minion) at {100 * r['frac_of_alone_n']:.2f}% of alone")
    for r in out.get("windows", []):
        print(f"WINDOW {r['card']:13s} {r['home']:12s} {r['window_cycles']:9d} cycles: host {r['host_ops']:6.1f} "
              f"({r.get('host_ops_lo')}-{r.get('host_ops_hi')}), remote {r['remote_ops']:10.0f}")
    for r in out.get("warmup", []):
        print(f"WARMUP {r['card']:13s} warm-up {r['warmup']:2d}: host {r['host_ops']:6.1f} ({r.get('host_ops_lo')}-{r.get('host_ops_hi')})")
    print("\nPACE: cycles a remote waits between atomics")
    for r in out["pace"]:
        print(f"  {r['card']:11s} pace {r['pace']:6d}  host {100 * r['frac_of_alone']:7.3f}% of alone"
              f"  remotes {r['remote_ops_per_shire']:8.0f}/shire")


if __name__ == "__main__":
    main()
