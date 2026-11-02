#!/usr/bin/env python3
# /// script
# requires-python = ">=3.9"
# dependencies = ["numpy"]
# ///
"""E123 (Q134): the tiles of E123 - fresh draws of the eleven dagger rows of the kinds table that no card re-drew (E94
measured four of the fifteen), and E94's six fresh draws of fp32 "ReLU x small weights" byte for byte (E94 left that row
UNRESOLVED as registered; reading the same bytes on aifoundry3 is a second bridge between the cards). Written with
make_kinds.py's own draw_elements, encode and tile_stats (imported from tools/claims-v3/kinds/, not copied), so every tile
is in the host's `file:` layout and its stats are counted exactly as kinds.json counts E78's. A port of make_e94.py.

    python3 tools/claims-v3/e123/make_e123.py            # writes tools/claims-v3/e123/tiles/<type>/<name>.bin and e123.json
    python3 tools/claims-v3/e123/make_e123.py --check    # rebuild in memory and compare with what is on disk

The draws: <type>.<kind>_e123d<r>, each drawn by make_kinds.draw_elements with the seed
int.from_bytes(sha256("E123/<type>/<kind>/draw<r>")[:8], "little"), recorded in e123.json. No draw is rejected or chosen.
The bridge: fp32.nn_like_e94d<r>, E94's six fresh draws (tools/claims-v3/kinds/e94/e94.json, measured on aifoundry1 card 1)
byte for byte. make_e123.py first re-derives each committed tile from make_kinds.rng_for + draw_elements and refuses if it
differs from kinds.json: the rule drawn here is the rule that made the committed tile.
"""
import argparse
import hashlib
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
KDIR = os.path.abspath(os.path.join(HERE, "..", "kinds"))
sys.path.insert(0, KDIR)
import make_kinds as mk  # noqa: E402

KINDS_JSON = os.path.join(KDIR, "kinds.json")
E94_JSON = os.path.join(KDIR, "e94", "e94.json")

# (type, kind, fresh draws, E94's draws run as the bridge, class)
#   G  = float kinds gating 25-75% of lanes (E94: between-draw SD 0.5-0.7 W)
#   LF = the other float dagger rows (predicted 0.32 W or less)
#   LI = the int8 dagger rows E94 did not run (predicted 0.26 W or less)
RULES = (
    ("fp32", "nn_like", 2, 6, "G"),
    ("fp16", "sparse50", 5, 0, "G"),
    ("fp16", "wsparse50", 5, 0, "G"),
    ("fp32", "smallint", 3, 0, "LF"),
    ("fp32", "sparse90", 3, 0, "LF"),
    ("fp16", "sparse90", 3, 0, "LF"),
    ("fp16", "wsparse90", 3, 0, "LF"),
    ("fp16", "smallint", 2, 0, "LF"),
    ("int8", "wsparse50", 3, 0, "LI"),
    ("int8", "sparse90", 3, 0, "LI"),
    ("int8", "wsparse90", 2, 0, "LI"),
    ("int8", "ternary", 2, 0, "LI"),
)


def seed_of(tag):
    return int.from_bytes(hashlib.sha256(tag.encode()).digest()[:8], "little")


def draw_raw(t, kind, rng):
    """One fresh tile of a rule; word-granular rules as make_kinds.replicate_draws builds them (E94's draw_raw)."""
    if kind.startswith("wsparse"):
        base = "full" if t == "int8" else "randn"
        a, b = mk.draw_elements(t, base, rng)
        aw, bw = mk.words_of(mk.encode(a, b, t))
        return mk.from_words(*mk.word_sparsify(aw, bw, int(kind[len("wsparse"):]) / 100.0, rng))
    a, b = mk.draw_elements(t, kind, rng)
    return mk.encode(a, b, t)


def committed_raw(t, kind):
    """E78's committed tile re-derived as make_kinds.build makes it (a word-granular kind masks the committed base tile)."""
    if kind.startswith("wsparse"):
        base = "full" if t == "int8" else "randn"
        a, b = mk.draw_elements(t, base, mk.rng_for(t, base))
        aw, bw = mk.words_of(mk.encode(a, b, t))
        return mk.from_words(*mk.word_sparsify(aw, bw, int(kind[len("wsparse"):]) / 100.0, mk.rng_for(t, kind)))
    a, b = mk.draw_elements(t, kind, mk.rng_for(t, kind))
    return mk.encode(a, b, t)


def tile_entry(t, kind, group, rule, raw, extra, base):
    st = mk.tile_stats(raw, t)
    rep = base.get("replicates") or {}
    ent = {"type": t, "kind": kind, "group": group, "rule": rule, "file": f"tiles/{t}/{kind}.bin", "bytes": 2048,
           "sha256": hashlib.sha256(raw).hexdigest(), "sha256_a": hashlib.sha256(raw[:1024]).hexdigest(),
           "sha256_b": hashlib.sha256(raw[1024:]).hexdigest(),
           "stats": {"gated_lane_frac": st["gated_lane_frac"], "bus_bits_per_op": st["bus_bits_per_op"]},
           "provisional": t == "int8"}
    ent.update(extra)
    ent["committed_tile"] = {"name": extra["rule_of"], "sha256": base["sha256"],
                             "gated_lane_frac": base["stats"]["gated_lane_frac"],
                             "bus_bits_per_op": base["stats"]["bus_bits_per_op"]}
    ent["rule_band"] = {q: {kk: rep[q][kk] for kk in ("n", "mean", "sd", "p2.5", "p97.5")} for q in rep
                        if isinstance(rep.get(q), dict)}
    for q in ("gated_lane_frac", "bus_bits_per_op"):
        b = ent["rule_band"].get(q)
        if b:
            ent.setdefault("inside_rule_band", {})[q] = bool(b["p2.5"] <= ent["stats"][q] <= b["p97.5"])
    return ent


def entries(k, e94):
    out = {}
    for t, kind, n_new, n_bridge, cls in RULES:
        base = k["kinds"][t][kind]
        raw0 = committed_raw(t, kind)
        if hashlib.sha256(raw0).hexdigest() != base["sha256"]:
            raise SystemExit(f"{t}.{kind}: make_kinds no longer reproduces the committed tile")
        for r in range(1, n_new + 1):
            tag = f"E123/{t}/{kind}/draw{r}"
            rng = np.random.default_rng(seed_of(tag))
            raw = draw_raw(t, kind, rng)
            out[f"{t}.{kind}_e123d{r}"] = (raw, tile_entry(
                t, f"{kind}_e123d{r}", "draw", f"a fresh draw of E78's rule `{kind}` ({t}) with a new seed", raw,
                {"seed_tag": tag, "seed": seed_of(tag), "rule_of": f"{t}.{kind}", "draw": r, "class": cls}, base))
        for r in range(1, n_bridge + 1):
            ev = e94["tiles"][f"{t}.{kind}_e94d{r}"]
            raw = open(os.path.join(KDIR, "e94", ev["file"]), "rb").read()
            if hashlib.sha256(raw).hexdigest() != ev["sha256"]:
                raise SystemExit(f"E94's {t}.{kind}_e94d{r} differs from e94.json")
            out[f"{t}.{kind}_e94d{r}"] = (raw, tile_entry(
                t, f"{kind}_e94d{r}", "bridge",
                f"E94's fresh draw d{r} of `{kind}` ({t}), byte for byte, measured on aifoundry1 card 1", raw,
                {"seed_tag": ev["seed_tag"], "seed": ev["seed"], "rule_of": f"{t}.{kind}", "draw": r, "class": cls,
                 "e94_name": f"{t}.{kind}_e94d{r}"}, base))
    return out


def build(check=False):
    k = json.load(open(KINDS_JSON))
    e94 = json.load(open(E94_JSON))
    spec = {"experiment": "E123", "date": "2026-11-01",
            "generator": "tools/claims-v3/e123/make_e123.py (make_kinds.py's draw_elements, encode and tile_stats, imported)",
            "kinds_json_sha256": hashlib.sha256(open(KINDS_JSON, "rb").read()).hexdigest(),
            "make_kinds_sha256": hashlib.sha256(open(os.path.join(KDIR, "make_kinds.py"), "rb").read()).hexdigest(),
            "e94_json_sha256": hashlib.sha256(open(E94_JSON, "rb").read()).hexdigest(),
            "seed_rule": "seed = int.from_bytes(sha256(seed_tag)[:8], 'little'); rng = numpy default_rng(seed)",
            "rules": {f"{t}.{kind}": {"fresh": n, "bridge": b, "class": c} for t, kind, n, b, c in RULES},
            "tiles": {}}
    problems = []
    for name, (raw, ent) in entries(k, e94).items():
        assert len(raw) == 2048, name
        p = os.path.join(HERE, ent["file"])
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
        old = json.load(open(os.path.join(HERE, "e123.json")))
        if old.get("tiles") != json.loads(json.dumps(spec["tiles"])):
            problems.append("e123.json tiles differ from the rebuild")
        print(json.dumps({"tiles": len(spec["tiles"]), "problems": problems}))
        sys.exit(1 if problems else 0)
    json.dump(spec, open(os.path.join(HERE, "e123.json"), "w"), indent=1)
    for n, e in spec["tiles"].items():
        s = e["stats"]
        print(f"{n:28s} {e['group']:7s} gated {s['gated_lane_frac']:.4f} bus {s['bus_bits_per_op']:6d} "
              f"inside band {e.get('inside_rule_band')}")


if __name__ == "__main__":
    main()
