#!/usr/bin/env python3
"""E143 (Q138): the session runner. It is E146's run_e146.py with E143's names and E80's binaries: E119's run_e119.py, imported and run unchanged (E105's
run_e105.py with its admission rule, E101 session 2's run_e101s.py, E80's run_kspeed.py, E64's run_hpl.py; E111's idle-login rule; the residency query
E119 sends, which this ettelem build refuses at its argument check before it opens the device), after the same preflight, with ONE ADDITION:

  BLIND POOL 5's TILES. A run's value may be `file:` a tile of tools/claims-v3/kinds/blind5/tiles/<its type>/ (Q138(x)'s commit dac39d97). Before the
  session every such value is checked: the three frozen inputs (Q138(x)'s predictions for aifoundry2, the manifest blind5.json, M7's m7.json) hash as
  committed, the value names a tile of the manifest of the run's own type, the run's label is `b5-<the tile's name>`, and the file is 2,048 B with the
  manifest's sha256 of the whole, of A (the first 1,024 B) and of B (the last 1,024 B). Any mismatch refuses the session (exit 2) before the card
  lock is taken. Every other value (E80's kinds tiles, checked against kinds.json; `zeros` for the rest reading) goes through the imported checks.

  PREFLIGHT (Q136's rule, "take more care for writing commands", kept in Q138): before anything opens the card, the three device programs must be
  byte-identical to E80's (its s1/session.json: heater build/sparsity_t2/host/sparsity_host, kernel build/sparsity_t2/kernel/sparsity.elf, sampler
  build/ettelem-hpl/ettelem; the same three E83 and E96 ran). E143.md classifies every device-management command they send; a different binary could
  send something else, so a mismatch refuses the session (exit 2). Under --dry no device is touched and the binary check is skipped (the tile and
  frozen-input checks are not).

Everything that touches the card -- the card lock held for the session, the other-user checks before every launch process, `timeout 10` on every launch
and config read, the sampler WITHOUT --reset-ms, the trace ring and `ettelem config` after every run, the safety stops (protocol.json safety, under the
keys run_hpl.py's watcher reads: abs_stop_c 80 C on one sample, board_cap_w 93 W on cap_consecutive 3), the end of the session unless the TDP and the
threshold read back 65, and the admission rule (86 W at the estimate; the 93 W lock) -- is the imported code. Nothing is set on the card. A protocol
whose safety block lacks those three keys is refused here (exit 2).

    python3 run_e143.py --protocol protocol.json --out <RUNDIR> [--dry] [--only BLOCK ...] [--max-card-min N] [--list]
"""
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "e119"))
import e143_common as C  # noqa: E402
import run_e119 as R119  # noqa: E402

H = R119.H
K = R119.RE.RS.K
E80_SHA256 = {  # E80's binaries (docs/reports/data/2026-10-31-e80-kinds-speed/s1/session.json sha256), unchanged on aifoundry2 since 21 Sep 2026 / 23 Oct 2026
    "build/sparsity_t2/host/sparsity_host": "7adadf4f1ce331cc028c317561933d6d3209da0f0326b0ce9a124b39b15ac0d2",
    "build/sparsity_t2/kernel/sparsity.elf": "990807f483cd57aa413083c52e647079b86022768562d5810080852f7fd6ea24",
    "build/ettelem-hpl/ettelem": "77a46171c915d3a92898af9ffe04d92b86b65f4d36bc29d58f5c086f8accfeb5",
}
WANT_TOOLS = {"heater": "build/sparsity_t2/host/sparsity_host", "kernel": "build/sparsity_t2/kernel/sparsity.elf", "ettelem": "build/ettelem-hpl/ettelem"}
SAFETY_KEYS = ("abs_stop_c", "board_cap_w", "cap_consecutive")

_prev_check = H.Run.check            # run_e101s.py's (run_kspeed.py's, run_hpl.py's)
_prev_verify = K.verify_tiles        # run_e101s.py's (run_kspeed.py's for kinds tiles)


def _check(self):
    """the imported check, with blind pool 5's tiles allowed when they are of the run's own type and carry their b5- label."""
    if not C.is_pool_value(self.values):
        return _prev_check(self)
    bad = []
    rel = str(self.values)[5:]
    if not rel.startswith(f"{C.POOL_REL}/tiles/{self.type}/"):
        bad.append(f"{self.name}: a pool tile must be a tile of its run's type ({rel})")
    if "/" in self.label or not self.label.startswith(C.LABEL_PREFIX):
        bad.append(f"{self.name}: a pool tile needs the label b5-<name> (got {self.label})")
    saved = self.values
    self.values = "zeros"           # every other check of run_hpl's, unchanged
    try:
        bad += K._base_check(self)
    finally:
        self.values = saved
    return bad


def verify_tiles(root, runs):
    """the imported verify_tiles for every other value, plus every pool tile against the manifest (the addition)."""
    pool = [r for r in runs if C.is_pool_value(r.values)]
    out, kinds_sha, kinds_rev = _prev_verify(root, [r for r in runs if not C.is_pool_value(r.values)])
    if not pool:
        return out, kinds_sha, kinds_rev
    bad = C.check_frozen(root)
    by_value = {C.tile_value(t): t for t in C.manifest(root).values()}
    for r in pool:
        t = by_value.get(str(r.values))
        if t is None:
            bad.append(f"{r.values}: not a tile of {C.MAN_REL}")
            continue
        if t["type"] != r.type:
            bad.append(f"{r.values}: a {t['type']} tile, run {r.name} is {r.type}")
        if r.label != C.label_of(t["name"]):
            bad.append(f"{r.name}: label {r.label}, the tile's is {C.label_of(t['name'])}")
        why = C.check_tile(root, t)
        if why:
            bad.append(why)
        out[str(r.values)] = {"type": t["type"], "kind": t["name"], "file": f"{C.POOL_REL}/{t['file']}", "bytes": 2048, "sha256": t["sha256"]["whole"],
                              "sha256_a": t["sha256"]["a"], "sha256_b": t["sha256"]["b"], "pool": "blind5", "priority": t.get("priority")}
    if bad:
        raise SystemExit("refused: " + "; ".join(bad))
    return out, kinds_sha, kinds_rev


H.Run.check = _check
K.verify_tiles = verify_tiles


def preflight(proto, root):
    """None if the protocol's three tools are E80's binaries and its safety block names the watcher's keys, else why not (selftest_e143.py runs it)."""
    tools = proto.get("tools", {})
    sf = proto.get("safety", {})
    bad = [f"protocol safety lacks {k}" for k in SAFETY_KEYS if k not in sf]
    for k, rel in WANT_TOOLS.items():
        if tools.get(k) != rel:
            bad.append(f"protocol tools.{k} is {tools.get(k)!r}, not {rel!r}")
            continue
        p = os.path.join(root, rel)
        got = C.sha256_file(p) if os.path.isfile(p) else None
        if got != E80_SHA256[rel]:
            bad.append(f"{rel}: sha256 {got}, registered {E80_SHA256[rel]}")
    return "; ".join(bad) if bad else None


def main():
    pr = sys.argv[sys.argv.index("--protocol") + 1]
    proto = json.load(open(pr))
    dry = "--dry" in sys.argv
    root = ROOT
    if "--root" in sys.argv:
        root = os.path.abspath(sys.argv[sys.argv.index("--root") + 1])
    got = {}
    miss = [k for k in SAFETY_KEYS if k not in proto.get("safety", {})]
    if miss and "--list" not in sys.argv:          # under --dry too: a stop the watcher cannot read is no stop
        print(f"refused: protocol safety lacks {', '.join(miss)}", file=sys.stderr)
        return 2
    bad = C.check_frozen(root)
    if bad:
        print("refused: " + "; ".join(bad), file=sys.stderr)
        return 2
    if not dry and "--list" not in sys.argv:
        why = preflight(proto, root)
        if why is not None:
            print(f"refused: {why}", file=sys.stderr)
            return 2
        got = dict(E80_SHA256)
    if "--out" in sys.argv and "--list" not in sys.argv:
        rd = os.path.abspath(sys.argv[sys.argv.index("--out") + 1])
        os.makedirs(rd, exist_ok=True)
        if not os.path.exists(os.path.join(rd, "e143.json")):
            json.dump({"experiment": "E143", "request": "Q138", "wrapper": "tools/claims-v3/e143/run_e143.py", "wrapper_sha256": C.sha256_file(__file__),
                       "e143_common_sha256": C.sha256_file(C.__file__), "run_e119_sha256": C.sha256_file(R119.__file__), "protocol": os.path.basename(pr),
                       "protocol_sha256": C.sha256_file(pr), "predictions_sha256": C.sha256_file(os.path.join(HERE, "predictions-e143.json")),
                       "frozen_inputs": dict(C.FROZEN), "binaries_checked": got, "dry": dry, "safety": proto.get("safety"),
                       "t_ms": int(time.time() * 1000), "zone": time.strftime("%Z"), "argv": sys.argv}, open(os.path.join(rd, "e143.json"), "w"), indent=1)
    return R119.main()


if __name__ == "__main__":
    sys.exit(main())
