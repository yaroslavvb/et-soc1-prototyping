#!/usr/bin/env python3
# /// script
# requires-python = ">=3.9"
# dependencies = ["numpy"]
# ///
"""E94 (Q132): the tiles of E94 - fresh draws of eight kinds of number, to measure what a KIND costs rather than what
one fixed tile costs (item 11 of the kinds page's section 11; E90's correction C2; E78's C5). Written with make_kinds.py's
own draw_elements, encode and tile_stats (imported, not copied), so every tile is in the host's `file:` layout and its
stats are counted exactly as kinds.json counts E78's.

    python3 tools/claims-v3/kinds/make_e94.py            # writes e94/tiles/<type>/<name>.bin and e94/e94.json
    python3 tools/claims-v3/kinds/make_e94.py --check    # rebuild in memory and compare with what is on disk

The draws: <type>.<kind>_e94d<r>, each drawn by make_kinds.draw_elements with the seed
int.from_bytes(sha256("E94/<type>/<kind>/draw<r>")[:8], "little"), recorded in e94.json. No draw is rejected or chosen.
The bridge: <type>.<kind>_e90d<r>, E90's nine fresh draws (e90/e90.json, measured on aifoundry3) byte for byte, so that the
same draw is read on both cards. E78's committed tile of each rule runs beside them (an E78 anchor already does for the
three random rules). make_e94.py first re-derives each committed tile from make_kinds.rng_for + draw_elements and refuses
if it differs from kinds.json: the rule drawn here is the rule that made the committed tile.
"""
import argparse
import hashlib
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import make_kinds as mk  # noqa: E402

OUT = os.path.join(HERE, "e94")
KINDS_JSON = os.path.join(HERE, "kinds.json")
E90_JSON = os.path.join(HERE, "e90", "e90.json")

# (type, kind, fresh draws, E90's draws run as the bridge)
RULES = (
    ("fp32", "sparse50", 6, 3),
    ("fp16", "nn_like", 6, 3),
    ("fp16", "uniform01", 6, 3),
    ("fp32", "nn_like", 6, 0),
    ("int8", "sparse50", 6, 0),
    ("fp32", "randn", 4, 0),
    ("fp16", "randn", 4, 0),
    ("int8", "full", 4, 0),
)


def seed_of(tag):
    return int.from_bytes(hashlib.sha256(tag.encode()).digest()[:8], "little")


def tile_entry(name, t, kind, group, rule, raw, extra, base):
    st = mk.tile_stats(raw, t)
    rep = base.get("replicates") or {}
    ent = {"type": t, "kind": kind, "group": group, "rule": rule, "file": f"tiles/{t}/{kind}.bin", "bytes": 2048,
           "sha256": hashlib.sha256(raw).hexdigest(), "sha256_a": hashlib.sha256(raw[:1024]).hexdigest(),
           "sha256_b": hashlib.sha256(raw[1024:]).hexdigest(),
           "stats": {"gated_lane_frac": st["gated_lane_frac"], "bus_bits_per_op": st["bus_bits_per_op"]},
           "provisional": t == "int8"}
    ent.update(extra)
    ent["committed_tile"] = {"name": f"{t}.{extra['rule_of'].split('.', 1)[1]}", "sha256": base["sha256"],
                             "gated_lane_frac": base["stats"]["gated_lane_frac"],
                             "bus_bits_per_op": base["stats"]["bus_bits_per_op"]}
    ent["rule_band"] = {q: {kk: rep[q][kk] for kk in ("mean", "sd", "p2.5", "p97.5")} for q in rep
                        if isinstance(rep.get(q), dict)}
    for q in ("gated_lane_frac", "bus_bits_per_op"):
        b = ent["rule_band"].get(q)
        if b:
            ent.setdefault("inside_rule_band", {})[q] = bool(b["p2.5"] <= ent["stats"][q] <= b["p97.5"])
    return ent


def entries(k, e90):
    out = {}
    for t, kind, n_new, n_bridge in RULES:
        base = k["kinds"][t][kind]
        rng0 = mk.rng_for(t, kind)
        a0, b0 = mk.draw_elements(t, kind, rng0)
        raw0 = mk.encode(a0, b0, t)
        if hashlib.sha256(raw0).hexdigest() != base["sha256"]:
            raise SystemExit(f"{t}.{kind}: make_kinds no longer reproduces the committed tile")
        for r in range(1, n_new + 1):
            tag = f"E94/{t}/{kind}/draw{r}"
            rng = np.random.default_rng(seed_of(tag))
            a_el, b_el = mk.draw_elements(t, kind, rng)
            name = f"{t}.{kind}_e94d{r}"
            raw = mk.encode(a_el, b_el, t)
            out[name] = (raw, tile_entry(name, t, f"{kind}_e94d{r}", "draw",
                                         f"a fresh draw of E78's rule `{kind}` ({t}) with a new seed", raw,
                                         {"seed_tag": tag, "seed": seed_of(tag), "rule_of": f"{t}.{kind}", "draw": r},
                                         base))
        for r in range(1, n_bridge + 1):
            ev = e90["tiles"][f"{t}.{kind}_d{r}"]
            raw = open(os.path.join(HERE, "e90", ev["file"]), "rb").read()
            if hashlib.sha256(raw).hexdigest() != ev["sha256"]:
                raise SystemExit(f"E90's {t}.{kind}_d{r} differs from e90.json")
            name = f"{t}.{kind}_e90d{r}"
            out[name] = (raw, tile_entry(name, t, f"{kind}_e90d{r}", "bridge",
                                         f"E90's fresh draw d{r} of `{kind}` ({t}), byte for byte, measured on aifoundry3",
                                         raw, {"seed_tag": ev["seed_tag"], "seed": ev["seed"], "rule_of": f"{t}.{kind}",
                                               "draw": r, "e90_name": f"{t}.{kind}_d{r}"}, base))
    return out


def build(check=False):
    k = json.load(open(KINDS_JSON))
    e90 = json.load(open(E90_JSON))
    spec = {"experiment": "E94", "date": "2026-11-01",
            "generator": "tools/claims-v3/kinds/make_e94.py (make_kinds.py's draw_elements, encode and tile_stats, imported)",
            "kinds_json_sha256": hashlib.sha256(open(KINDS_JSON, "rb").read()).hexdigest(),
            "make_kinds_sha256": hashlib.sha256(open(os.path.join(HERE, "make_kinds.py"), "rb").read()).hexdigest(),
            "e90_json_sha256": hashlib.sha256(open(E90_JSON, "rb").read()).hexdigest(),
            "seed_rule": "seed = int.from_bytes(sha256(seed_tag)[:8], 'little'); rng = numpy default_rng(seed)",
            "rules": {f"{t}.{kind}": {"fresh": n, "bridge": b} for t, kind, n, b in RULES},
            "tiles": {}}
    problems = []
    for name, (raw, ent) in entries(k, e90).items():
        assert len(raw) == 2048, name
        p = os.path.join(OUT, ent["file"])
        if check:
            have = open(p, "rb").read() if os.path.exists(p) else b""
            if have != raw:
                problems.append(f"{name}: on-disk tile differs from the rebuild")
        else:
            os.makedirs(os.path.dirname(p), exist_ok=True)
            open(p, "wb").write(raw)
        spec["tiles"][name] = ent
    return spec, problems


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args()
    spec, problems = build(check=a.check)
    if a.check:
        old = json.load(open(os.path.join(OUT, "e94.json")))
        if old.get("tiles") != json.loads(json.dumps(spec["tiles"])):
            problems.append("e94.json tiles differ from the rebuild")
        print(json.dumps({"tiles": len(spec["tiles"]), "problems": problems}))
        sys.exit(1 if problems else 0)
    json.dump(spec, open(os.path.join(OUT, "e94.json"), "w"), indent=1)
    for n, e in spec["tiles"].items():
        s = e["stats"]
        print(f"{n:28s} {e['group']:7s} gated {s['gated_lane_frac']:.4f} bus {s['bus_bits_per_op']:6d} "
              f"inside band {e.get('inside_rule_band')}")


if __name__ == "__main__":
    main()
