#!/usr/bin/env python3
"""Build ref_committed.json: the committed per-card values that V3-LAT's registered predictions compare against.

    python3 tools/claims-v3/lat/make_ref.py            (reads docs/reports/data/, writes ref_committed.json here)

Run once before the first card block; reduce.py reads the JSON (never the committed files), so the reference is
fixed and hashed with the block code (block_begin writes code.sha256 over this directory). Sources:
  hot line   docs/reports/data/2026-09-22-hotline-aifoundry{2,3}/sweep.jsonl   (LAT-H P1: "the committed per-card
             value" of every unstopped host fraction; which configurations are stopped)
  relay      docs/reports/data/2026-09-22-onchip-aifoundry{2,3}/sweep.jsonl    (LAT-R (v): "every size, intensity
             and stages ratio within +-5% of the committed per-card value")
  divergence docs/reports/data/2026-09-18-sparsity-aifoundry3/diverge/          (LAT-S5: "lane efficiencies identical
             to 18 Sep (same seed); throughput within +-3%"; one card only, the draw is the same on both)
"""
import json
import os

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", ".."))
D = os.path.join(ROOT, "docs", "reports", "data")
CARDS = ("aifoundry2", "aifoundry3")


def jl(p):
    return [json.loads(l) for l in open(p) if l.strip()]


def hot_key(r):
    return f'{r["group"]}|{r["home"]}|{r["shire_mask"]}|{r["per_shire"]}|{r["pace"]}'


def host_of(home):
    s = home.split(":")[-1]
    return None if s == "own" else int(s)


def hotline(card):
    rows = jl(f"{D}/2026-09-22-hotline-{card}/sweep.jsonl")
    alone = {}
    for r in rows:
        if r["group"] == "local" and r["shires"] == 1:
            h = host_of(r["home"])
            s = {x["s"]: x for x in r["shire"]}[h]
            alone[r["home"]] = s["ops"] / s["minions"]
    out = {}
    for r in rows:
        h = host_of(r["home"])
        sh = {x["s"]: x for x in r["shire"]}
        rec = {"host_ops": sh[h]["ops"] if h is not None and h in sh else None}
        if h is not None and h in sh and r["home"] in alone:
            rec["frac"] = sh[h]["ops"] / sh[h]["minions"] / alone[r["home"]]
        out[hot_key(r)] = rec
    return out


def relay(card):
    rows = jl(f"{D}/2026-09-22-onchip-{card}/sweep.jsonl")
    keyof = {"size": "stage_bytes", "intensity": "work", "stages": "stages"}
    by = {}
    for r in rows:
        if r.get("test") == "relay" and r["group"] in keyof:
            by.setdefault(f'{r["group"]}|{r[keyof[r["group"]]]}', {})[r["medium"]] = r["gb_s"]
    return {k: {"scp_over_dram": m["scp"] / m["dram"], "hop_over_dram": m["hop"] / m["dram"]}
            for k, m in by.items() if len(m) == 3}


def diverge():
    out = {}
    for a in ("0", "3", "2", "1.5", "1.2"):
        for v in ("static", "refill", "scalar"):
            p = f"{D}/2026-09-18-sparsity-aifoundry3/diverge/diverge-{v}-a{a}.jsonl"
            r = [json.loads(l.split(" ", 1)[1]) for l in open(p) if l.startswith("SPARSITY ")][0]
            out[f"{v}|{float(a):g}"] = {"lane_efficiency": r["lane_efficiency"],
                                        "tfma_600": 8 * r["useful_lane_iters"] / r["cycles_mean"] * 600 / 1e6}
    return out


def main():
    ref = {"sources": {"hotline": "docs/reports/data/2026-09-22-hotline-<card>/sweep.jsonl",
                       "relay": "docs/reports/data/2026-09-22-onchip-<card>/sweep.jsonl",
                       "diverge": "docs/reports/data/2026-09-18-sparsity-aifoundry3/diverge/"},
           "hotline": {c: hotline(c) for c in CARDS},
           "relay": {c: relay(c) for c in CARDS},
           "diverge_18sep": diverge()}
    out = os.path.join(os.path.dirname(os.path.abspath(__file__)), "ref_committed.json")
    json.dump(ref, open(out, "w"), indent=1, sort_keys=True)
    print(f"wrote {out}: {sum(len(v) for v in ref['hotline'].values())} hot-line, "
          f"{sum(len(v) for v in ref['relay'].values())} relay, {len(ref['diverge_18sep'])} divergence references")


if __name__ == "__main__":
    main()
