#!/usr/bin/env python3
"""E101, session 2 (Q132): the session runner. It IS E80's runner, ../run_kspeed.py (E64's tools/claims-v3/hpl/run_hpl.py plus `file:` tiles), imported and run unchanged, with two additions and nothing else:

  1. a run's value may be an arm of tools/claims-v3/rgm's host, `<arm>:<gen>:<files>` (tools/claims-v3/kinds/e101_common.py writes them), or `file:` a tile of rgm/tiles or kinds/real2/tiles. Before the session every file a
     value names is checked against e101_common's registered sha256 (kinds.json, real2.json, the e37 tiles). Every other check of a run is run_hpl.py's, unchanged.
  2. under --dry the toy card draws each cell's switching term c from protocol.json's `dry_c_w`, so a dry session exercises the gates, the safety paths and reduce_e101s.py with plausible numbers. No device is touched under --dry.

Everything that touches the card -- the card lock held for the session, the other-user checks before every launch process, `timeout 10` on every launch and config read, the sampler WITHOUT --reset-ms, the trace ring, residencies and `ettelem config`
after every run, the safety stops (85 C; 97 W on three samples), and the end of the session unless the TDP and the threshold read back 65 -- is run_hpl.py's own code. Nothing is set on the card.

    python3 run_e101s.py --protocol protocol.json --out <RUNDIR> [--dry] [--only BLOCK ...] [--max-card-min N] [--list]
"""
import hashlib
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, "..", "..", "..", ".."))
sys.path.insert(0, os.path.join(HERE, ".."))
sys.path.insert(0, os.path.join(HERE, "..", "..", "kinds"))
import run_kspeed as K  # noqa: E402
import e101_common as e101  # noqa: E402

H = K.H
_kspeed_check = K._check
_kspeed_verify = K.verify_tiles
ARM_PREFIX = ("tenb:", "mm", "gemm")


def sha256(path):
    return hashlib.sha256(open(path, "rb").read()).hexdigest()


def is_new(values):
    v = str(values)
    return v.startswith(ARM_PREFIX) or v.startswith(f"file:{e101.RGM}/") or v.startswith(f"file:{e101.REAL2_REL}/")


def _check(self):
    """run_kspeed's check, with E101's values allowed as well."""
    if not is_new(self.values):
        return _kspeed_check(self)
    bad = []
    if "/" in self.label or self.label.startswith(self.type + "-file:"):
        bad.append(f"{self.name}: a new value needs an explicit label without '/'")
    saved = self.values
    self.values = "zeros"           # every other check of run_hpl's, unchanged
    try:
        bad += K._base_check(self)
    finally:
        self.values = saved
    return bad


def verify_tiles(root, runs):
    """run_kspeed's verify_tiles for kinds tiles run resident, plus every file an E101 value names, against the registered sha256."""
    out, kinds_sha, kinds_rev = _kspeed_verify(root, [r for r in runs if not is_new(r.values)])
    new = {str(r.values): r for r in runs if is_new(r.values)}
    if not new:
        return out, kinds_sha, kinds_rev
    bad = e101.check_files(root)
    items = {it["name"]: it for it in e101.load_items()}
    reg = {}
    for it in items.values():
        if it.get("tile") and it.get("sha256"):
            reg[it["tile"]] = it["sha256"]
    real = e101._real2()["tiles"]
    for ty, names in e101.REAL_SET.items():
        for n in names:
            reg[f"{e101.REAL2_REL}/{real[ty][n]['file']}"] = real[ty][n]["sha256"]
    for v, r in new.items():
        files = v[5:].split(",") if v.startswith("file:") else v.split(":", 2)[2].split(",")
        rec = {"type": r.type, "kind": r.label, "values": v, "files": {}}
        for rel in files:
            if rel not in reg:
                bad.append(f"{v}: {rel} is not a registered tile")
                continue
            p = os.path.join(root, rel)
            got = sha256(p) if os.path.exists(p) else None
            rec["files"][rel] = got
            if got != reg[rel]:
                bad.append(f"{rel}: sha256 {got}, registered {reg[rel]}")
        out[v] = rec
    if bad:
        raise SystemExit("refused: " + "; ".join(bad))
    return out, kinds_sha, kinds_rev


H.Run.check = _check
K.verify_tiles = verify_tiles


def main():
    pr = sys.argv[sys.argv.index("--protocol") + 1]
    proto = json.load(open(pr))
    if "--dry" in sys.argv:
        for v, c in proto.get("dry_c_w", {}).items():
            H.DryCard.DYN600[v] = c
    if "--out" in sys.argv and "--list" not in sys.argv:
        rd = os.path.abspath(sys.argv[sys.argv.index("--out") + 1])
        if not os.path.exists(os.path.join(rd, "session.json")):
            os.makedirs(rd, exist_ok=True)
            json.dump({"experiment": "E101", "session": 2, "wrapper": os.path.relpath(os.path.abspath(__file__), ROOT), "wrapper_sha256": sha256(__file__),
                       "protocol_sha256": sha256(pr), "run_kspeed_sha256": sha256(K.__file__), "e101_common_sha256": sha256(e101.__file__),
                       "t_ms": int(time.time() * 1000), "zone": time.strftime("%Z"), "argv": sys.argv},
                      open(os.path.join(rd, "e101s.json"), "w"), indent=1)
    return K.main()


if __name__ == "__main__":
    sys.exit(main())
