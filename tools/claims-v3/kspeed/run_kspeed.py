#!/usr/bin/env python3
"""E80 (Q130): the session runner. It IS E64's runner, tools/claims-v3/hpl/run_hpl.py, imported and run unchanged,
with two additions and nothing else:

  1. a run's --values may be `file:<tile>`, a tile of tools/claims-v3/kinds/tiles/<type>/ (Q130(s) revision 2,
     commit 7d9c0d9e). Before the session every tile the protocol names is checked against kinds.json: the path
     sits in its own type's tile folder, the file is 2,048 bytes, and its sha256 is kinds.json's. A run with a file
     value must carry an explicit label (the label names its telemetry file). The check is recorded in
     <RUNDIR>/kspeed.json beside run_hpl.py's own session.json.
  2. under --dry the toy card draws each file kind's PREDICTED switching watts (predictions.json c_pred_w), so a dry
     session exercises the gates, the safety paths and reduce_kspeed.py with plausible numbers. No device is touched.

Everything that touches the card -- the non-blocking card lock held for the session, the other-user checks before
every launch process, `timeout 10` on every device process, the sampler WITHOUT --reset-ms, the service processor's
trace ring, residencies and `ettelem config` read after every run with the sampler stopped, the safety stops
(85 C, 97 W on three samples), and the end of the session unless the TDP and the threshold read back 65 -- is
run_hpl.py's own code. Nothing is set on the card.

    python3 run_kspeed.py --protocol protocol.json --out <RUNDIR> [--dry] [--only BLOCK ...]
                          [--max-card-min N] [--list] [--root <tree>]
"""
import argparse
import hashlib
import json
import os
import signal
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "hpl"))
import run_hpl as H  # noqa: E402

TILE_DIR = "tools/claims-v3/kinds/tiles"
KINDS_JSON = "tools/claims-v3/kinds/kinds.json"
_base_check = H.Run.check


def _check(self):
    """run_hpl's Run.check, with `file:` values allowed when they name a tile of the run's own type."""
    if not str(self.values).startswith("file:"):
        return _base_check(self)
    bad = []
    rel = self.values[5:]
    if not (rel.startswith(f"{TILE_DIR}/{self.type}/") and rel.endswith(".bin") and ".." not in rel):
        bad.append(f"{self.name}: a file value must be a tile of {TILE_DIR}/{self.type}/ (got {rel})")
    if "/" in self.label or self.label.startswith(self.type + "-file:"):
        bad.append(f"{self.name}: a file value needs an explicit label without '/'")
    saved = self.values
    self.values = "zeros"           # every other check of run_hpl's, unchanged
    try:
        bad += _base_check(self)
    finally:
        self.values = saved
    return bad


H.Run.check = _check


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        h.update(f.read())
    return h.hexdigest()


def verify_tiles(root, runs):
    """{value: record} for every file value, or raise SystemExit(2) on the first mismatch."""
    K = json.load(open(os.path.join(root, KINDS_JSON)))
    by_file = {}
    for t, ks in K["kinds"].items():
        for k, rec in ks.items():
            by_file[f"tools/claims-v3/kinds/{rec['file']}"] = (t, k, rec)
    out = {}
    for r in runs:
        if not str(r.values).startswith("file:") or r.values in out:
            continue
        rel = r.values[5:]
        if rel not in by_file:
            raise SystemExit(f"refused: {rel} is not a tile in kinds.json")
        t, k, rec = by_file[rel]
        if t != r.type:
            raise SystemExit(f"refused: {rel} is a {t} tile, run {r.name} is {r.type}")
        p = os.path.join(root, rel)
        size = os.path.getsize(p) if os.path.exists(p) else -1
        got = sha256(p) if size >= 0 else None
        if size != 2048 or got != rec["sha256"]:
            raise SystemExit(f"refused: {rel} size {size} sha256 {got} (kinds.json {rec['sha256']})")
        out[r.values] = {"type": t, "kind": k, "file": rel, "bytes": size, "sha256": got,
                         "sha256_a": rec.get("sha256_a"), "sha256_b": rec.get("sha256_b"), "tier": rec.get("tier")}
    return out, sha256(os.path.join(root, KINDS_JSON)), K.get("revision")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--protocol", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--dry", action="store_true")
    ap.add_argument("--only", nargs="*")
    ap.add_argument("--max-card-min", type=float)
    ap.add_argument("--list", action="store_true")
    ap.add_argument("--root", default=os.path.join(HERE, "..", "..", ".."))
    a = ap.parse_args()
    a.root = os.path.abspath(a.root)
    proto, runs, bad = H.load_protocol(a.protocol, a.only)
    if bad:
        print("protocol refused:\n  " + "\n  ".join(bad), file=sys.stderr)
        return H.EXIT_REFUSE
    _, all_runs, _ = H.load_protocol(a.protocol, [b["name"] for b in proto["blocks"]])
    tiles, kinds_sha, kinds_rev = verify_tiles(a.root, all_runs)
    if a.list:
        tot = 0
        for r in runs:
            tot += r.plan_s()
            print(f"{r.name:40s} {r.type} {tiles.get(r.values, {}).get('kind', r.values):10s} {r.minions:5d} "
                  f"{r.processes}x{r.seconds:g}s start {r.start}")
        print(f"{len(runs)} runs, about {tot / 60:.0f} min plus gates; {len(tiles)} tiles verified against "
              f"kinds.json ({kinds_sha[:12]})")
        return H.EXIT_OK
    if a.dry:
        pred = json.load(open(os.path.join(HERE, "predictions.json")))
        for v, rec in tiles.items():
            e = pred["kinds"].get(f"{rec['type']}/{rec['kind']}")
            if e:
                H.DryCard.DYN600[v] = e["c_pred_w"]
    s = H.Session(a, proto, runs)
    rd = os.path.abspath(a.out)
    me = {"wrapper": os.path.relpath(os.path.abspath(__file__), a.root), "wrapper_sha256": sha256(__file__),
          "run_hpl_sha256": sha256(H.__file__), "protocol_sha256": sha256(a.protocol),
          "kinds_json_sha256": kinds_sha, "kinds_revision": kinds_rev, "tiles": tiles,
          "runs_planned": [r.name for r in runs]}
    rc, out, _ = H.run_out(["git", "status", "--porcelain", "--", "tools/claims-v3/kspeed",
                            "tools/claims-v3/kinds", "tools/claims-v3/hpl"], cwd=a.root)
    me["git_dirty"] = out.decode().strip()
    rc, out, _ = H.run_out(["git", "rev-parse", "HEAD"], cwd=a.root)
    me["git_head"] = out.decode().strip()
    if not os.path.exists(os.path.join(rd, "session.json")):
        json.dump(me, open(os.path.join(rd, "kspeed.json"), "w"), indent=1)

    def on_signal(signum, frame):
        s.touch(s.stop_file)
        raise H.EndSession(f"signal:{signum}", H.EXIT_SIGNAL)

    signal.signal(signal.SIGTERM, on_signal)
    signal.signal(signal.SIGINT, on_signal)
    try:
        return s.run()
    except H.Refuse as e:
        print(f"refused: {e}", file=sys.stderr)
        return H.EXIT_REFUSE


if __name__ == "__main__":
    sys.exit(main())
