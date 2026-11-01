#!/usr/bin/env python3
"""E87 (Q130): the session runner. It IS E80's runner, ../run_kspeed.py (E64's tools/claims-v3/hpl/run_hpl.py plus
`file:` tiles checked against kinds.json), imported and run unchanged, with two additions and nothing else:

  1. a `file:` value may also name one of Q130(n)'s real GPT-2 tiles, tools/claims-v3/kinds/real/tiles/<type>/
     <name>.bin (commits 7d5b99af and 99620cc2). Before the session every such tile is checked: it sits in its own
     type's real-tile folder, it is 2,048 bytes, and its sha256 is the one frozen in Q130(n)'s predictions-real.json
     (itself refused unless its sha256 is bab33bee...) and in real.json (refused unless eb36f4cd...). Every other tile
     goes through run_kspeed.py's own verify_tiles against kinds.json, unchanged. The run check is run_kspeed.py's,
     with the real-tile folder allowed beside kinds/tiles/; every other check is run_hpl.py's, unchanged.
  2. under --dry the toy card draws each tile's PREDICTED switching term: Q130(n)'s c for a real tile
     (predictions-real.json tiles.*.b_aifoundry2_governor.c_w) and E83's predicted c for an anchor, so a dry session
     exercises the gates, the safety paths and reduce_e87.py with plausible numbers. No device is touched under --dry.

Before the session it writes <RUNDIR>/e87.json: this wrapper's sha256 and its inputs', beside run_kspeed.py's own
kspeed.json (every tile's sha256) and run_hpl.py's session.json. Everything that touches the card -- the card lock
held for the session, the other-user checks before every launch process, `timeout 10` on every launch and config
read, the sampler WITHOUT --reset-ms, the trace ring, residencies and `ettelem config` after every run, the safety
stops (85 C; 97 W on three samples), and the end of the session unless the TDP and the threshold read back 65 -- is
run_hpl.py's own code. Nothing is set on the card.

    python3 run_e87.py --protocol protocol.json --out <RUNDIR> [--dry] [--only BLOCK ...] [--max-card-min N] [--list]
"""
import hashlib
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, ".."))
import run_kspeed as K  # noqa: E402

H = K.H
REAL_DIR = "tools/claims-v3/kinds/real/tiles"
REAL_PRED = "tools/claims-v3/kinds/real/predictions-real.json"
REAL_JSON = "tools/claims-v3/kinds/real/real.json"
FROZEN_SHA = {REAL_PRED: "bab33beee0bcefa3d1aae5bd9af72e2d1c1da0f76bb0947aa2f7a39c6b024941",
              REAL_JSON: "eb36f4cd0d88d928d2c0c92165f4a48e23727221d5ac047bff3de3c8e0ad83c0"}
_kspeed_check = K._check            # run_kspeed's run check (run_hpl's, with kinds/tiles/ allowed)
_kspeed_verify = K.verify_tiles     # run_kspeed's tile check against kinds.json


def sha256(path):
    return hashlib.sha256(open(path, "rb").read()).hexdigest()


def is_real(values):
    return str(values).startswith("file:" + REAL_DIR + "/")


def _check(self):
    """run_kspeed's check, with a tile of the real-tile folder of the run's own type allowed as well."""
    if not is_real(self.values):
        return _kspeed_check(self)
    bad = []
    rel = self.values[5:]
    if not (rel.startswith(f"{REAL_DIR}/{self.type}/") and rel.endswith(".bin") and ".." not in rel):
        bad.append(f"{self.name}: a real-tile value must be a tile of {REAL_DIR}/{self.type}/ (got {rel})")
    if "/" in self.label or self.label.startswith(self.type + "-file:"):
        bad.append(f"{self.name}: a file value needs an explicit label without '/'")
    saved = self.values
    self.values = "zeros"           # every other check of run_hpl's, unchanged
    try:
        bad += K._base_check(self)
    finally:
        self.values = saved
    return bad


def verify_tiles(root, runs):
    """run_kspeed's verify_tiles for kinds tiles, plus Q130(n)'s real tiles checked against its frozen files."""
    out, kinds_sha, kinds_rev = _kspeed_verify(root, [r for r in runs if not is_real(r.values)])
    reals = [r for r in runs if is_real(r.values)]
    if not reals:
        return out, kinds_sha, kinds_rev
    for rel, want in FROZEN_SHA.items():
        got = sha256(os.path.join(root, rel))
        if got != want:
            raise SystemExit(f"refused: {rel} sha256 {got} (frozen {want})")
    PR = json.load(open(os.path.join(root, REAL_PRED)))["tiles"]
    RJ = json.load(open(os.path.join(root, REAL_JSON)))["tiles"]
    for r in reals:
        if r.values in out:
            continue
        rel = r.values[5:]
        t, name = rel.split("/")[-2], rel.split("/")[-1][:-4]
        rec = PR.get(f"{t}/{name}")
        rj = (RJ.get(t) or {}).get(name)
        if rec is None or rj is None or rec["tile"] != rel or f"tools/claims-v3/kinds/real/{rj['file']}" != rel:
            raise SystemExit(f"refused: {rel} is not a tile of Q130(n)'s predictions-real.json and real.json")
        if t != r.type:
            raise SystemExit(f"refused: {rel} is a {t} tile, run {r.name} is {r.type}")
        p = os.path.join(root, rel)
        size = os.path.getsize(p) if os.path.exists(p) else -1
        got = sha256(p) if size >= 0 else None
        if size != 2048 or got != rec["tile_sha256"] or got != rj["sha256"]:
            raise SystemExit(f"refused: {rel} size {size} sha256 {got} (Q130(n) {rec['tile_sha256']})")
        out[r.values] = {"type": t, "kind": name, "file": rel, "bytes": size, "sha256": got,
                         "sha256_a": rj.get("sha256_a"), "sha256_b": rj.get("sha256_b"), "tier": "real (Q130(n))"}
    return out, kinds_sha, kinds_rev


H.Run.check = _check
K.verify_tiles = verify_tiles


def main():
    pred_path = os.path.join(HERE, "predictions.json")
    pred = json.load(open(pred_path))
    if "--dry" in sys.argv:
        for e in list(pred["tiles"].values()) + list(pred["anchors"].values()):
            H.DryCard.DYN600["file:" + e["tile"]] = e["c_dry_w"]
    if "--out" in sys.argv and "--list" not in sys.argv:
        rd = os.path.abspath(sys.argv[sys.argv.index("--out") + 1])
        if not os.path.exists(os.path.join(rd, "session.json")):
            os.makedirs(rd, exist_ok=True)
            root = os.path.join(HERE, "..", "..", "..", "..")
            json.dump({"experiment": "E87", "wrapper": os.path.relpath(os.path.abspath(__file__), root),
                       "wrapper_sha256": sha256(__file__), "predictions_sha256": sha256(pred_path),
                       "run_kspeed_sha256": sha256(K.__file__),
                       "frozen_inputs_sha256": {k: sha256(os.path.join(root, k)) for k in FROZEN_SHA},
                       "argv": sys.argv},
                      open(os.path.join(rd, "e87.json"), "w"), indent=1)
    return K.main()


if __name__ == "__main__":
    sys.exit(main())
