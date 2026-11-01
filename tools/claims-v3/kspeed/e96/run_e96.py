#!/usr/bin/env python3
"""E96 (Q132): the session runner. It IS E80's runner, ../run_kspeed.py (E64's tools/claims-v3/hpl/run_hpl.py plus
`file:` tiles checked against kinds.json), imported and run unchanged, with the two additions E87's run_e87.py made and
nothing else:

  1. a `file:` value may also name a real tile: one of Q132(r)'s, tools/claims-v3/kinds/real2/tiles/<type>/<name>.bin
     (commit 6ae4c3d5), or one of Q130(n)'s, tools/claims-v3/kinds/real/tiles/<type>/<name>.bin, for the int8 arm. Before
     the session every such tile is checked: it sits in its own type's folder, it is 2,048 bytes, and its sha256 is the one
     frozen in that folder's predictions file and its tiles file (predictions-real2.json and real2.json, predictions-real.json
     and real.json; each of the four refused unless its own sha256 is the one below). Every other tile goes through
     run_kspeed.py's own verify_tiles against kinds.json, unchanged. The run check is run_kspeed.py's, with the real-tile
     folders allowed beside kinds/tiles/; every other check is run_hpl.py's, unchanged.
  2. under --dry the toy card draws each tile's PREDICTED switching term (this folder's predictions.json c_dry_w), so a dry
     session exercises the gates, the safety paths and reduce_e96.py with plausible numbers. No device is touched under --dry.

Before the session it writes <RUNDIR>/e96.json: this wrapper's sha256 and its inputs', beside run_kspeed.py's own kspeed.json
(every tile's sha256) and run_hpl.py's session.json. Everything that touches the card -- the card lock held for the session,
the other-user checks before every launch process, `timeout 10` on every launch and config read, the sampler WITHOUT
--reset-ms, the trace ring, residencies and `ettelem config` after every run, the safety stops (85 C; 97 W on three samples),
and the end of the session unless the TDP and the threshold read back 65 -- is run_hpl.py's own code. Nothing is set on the card.

    python3 run_e96.py --protocol protocol.json --out <RUNDIR> [--dry] [--only BLOCK ...] [--max-card-min N] [--list]
"""
import hashlib
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, ".."))
import run_kspeed as K  # noqa: E402

H = K.H
REAL2 = "tools/claims-v3/kinds/real2"
REAL1 = "tools/claims-v3/kinds/real"
FOLDERS = {f"{REAL2}/tiles": (REAL2, f"{REAL2}/predictions-real2.json", f"{REAL2}/real2.json"),
           f"{REAL1}/tiles": (REAL1, f"{REAL1}/predictions-real.json", f"{REAL1}/real.json")}
FROZEN_SHA = {f"{REAL2}/predictions-real2.json": "0957e0c295990ac95cded56430697fb0683c9cf451d90f6943c8ff8d6a0b021a",
              f"{REAL2}/real2.json": "6e259fd2e9edaa3d4fdeb663461ec39389ec8c24436c114719536a51d26c8715",
              f"{REAL1}/predictions-real.json": "bab33beee0bcefa3d1aae5bd9af72e2d1c1da0f76bb0947aa2f7a39c6b024941",
              f"{REAL1}/real.json": "eb36f4cd0d88d928d2c0c92165f4a48e23727221d5ac047bff3de3c8e0ad83c0"}
_kspeed_check = K._check            # run_kspeed's run check (run_hpl's, with kinds/tiles/ allowed)
_kspeed_verify = K.verify_tiles     # run_kspeed's tile check against kinds.json


def sha256(path):
    return hashlib.sha256(open(path, "rb").read()).hexdigest()


def folder_of(values):
    for d in FOLDERS:
        if str(values).startswith("file:" + d + "/"):
            return d
    return None


def _check(self):
    """run_kspeed's check, with a tile of a real-tile folder of the run's own type allowed as well."""
    d = folder_of(self.values)
    if d is None:
        return _kspeed_check(self)
    bad = []
    rel = self.values[5:]
    if not (rel.startswith(f"{d}/{self.type}/") and rel.endswith(".bin") and ".." not in rel):
        bad.append(f"{self.name}: a real-tile value must be a tile of {d}/{self.type}/ (got {rel})")
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
    """run_kspeed's verify_tiles for kinds tiles, plus the real tiles checked against their folders' frozen files."""
    out, kinds_sha, kinds_rev = _kspeed_verify(root, [r for r in runs if folder_of(r.values) is None])
    reals = [r for r in runs if folder_of(r.values) is not None]
    if not reals:
        return out, kinds_sha, kinds_rev
    for rel, want in FROZEN_SHA.items():
        got = sha256(os.path.join(root, rel))
        if got != want:
            raise SystemExit(f"refused: {rel} sha256 {got} (frozen {want})")
    for r in reals:
        if r.values in out:
            continue
        d = folder_of(r.values)
        base, pred_rel, json_rel = FOLDERS[d]
        PR = json.load(open(os.path.join(root, pred_rel)))["tiles"]
        RJ = json.load(open(os.path.join(root, json_rel)))["tiles"]
        rel = r.values[5:]
        t, name = rel.split("/")[-2], rel.split("/")[-1][:-4]
        rec = PR.get(f"{t}/{name}")
        rj = (RJ.get(t) or {}).get(name)
        if rec is None or rj is None or rec["tile"] != rel or f"{base}/{rj['file']}" != rel:
            raise SystemExit(f"refused: {rel} is not a tile of {pred_rel} and {json_rel}")
        if t != r.type:
            raise SystemExit(f"refused: {rel} is a {t} tile, run {r.name} is {r.type}")
        p = os.path.join(root, rel)
        size = os.path.getsize(p) if os.path.exists(p) else -1
        got = sha256(p) if size >= 0 else None
        if size != 2048 or got != rec["tile_sha256"] or got != rj["sha256"]:
            raise SystemExit(f"refused: {rel} size {size} sha256 {got} ({pred_rel}: {rec['tile_sha256']})")
        out[r.values] = {"type": t, "kind": name, "file": rel, "bytes": size, "sha256": got, "sha256_a": rj.get("sha256_a"),
                         "sha256_b": rj.get("sha256_b"), "tier": ("real2 (Q132(r))" if base == REAL2 else "real (Q130(n))")}
    return out, kinds_sha, kinds_rev


H.Run.check = _check
K.verify_tiles = verify_tiles


def main():
    pred_path = os.path.join(HERE, "predictions.json")
    pred = json.load(open(pred_path))
    if "--dry" in sys.argv:
        for e in list(pred["tiles"].values()) + list(pred["arm"]["tiles"].values()) + list(pred["anchors"].values()):
            H.DryCard.DYN600["file:" + e["tile"]] = e["c_dry_w"]
    if "--out" in sys.argv and "--list" not in sys.argv:
        rd = os.path.abspath(sys.argv[sys.argv.index("--out") + 1])
        if not os.path.exists(os.path.join(rd, "session.json")):
            os.makedirs(rd, exist_ok=True)
            root = os.path.join(HERE, "..", "..", "..", "..")
            pr = sys.argv[sys.argv.index("--protocol") + 1]
            json.dump({"experiment": "E96", "wrapper": os.path.relpath(os.path.abspath(__file__), root),
                       "wrapper_sha256": sha256(__file__), "predictions_sha256": sha256(pred_path),
                       "protocol_sha256": sha256(pr), "run_kspeed_sha256": sha256(K.__file__),
                       "frozen_inputs_sha256": {k: sha256(os.path.join(root, k)) for k in FROZEN_SHA},
                       "t_ms": int(time.time() * 1000), "zone": time.strftime("%Z"), "argv": sys.argv},
                      open(os.path.join(rd, "e96.json"), "w"), indent=1)
    return K.main()


if __name__ == "__main__":
    sys.exit(main())
