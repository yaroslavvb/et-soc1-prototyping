#!/usr/bin/env python3
"""E165 (Q141(g)): the session runner. It is E160's run_e160.py with pool 7's names (E143's run_e143.py with Q139(k)'s C log): E119's run_e119.py,
imported and run unchanged (E105's run_e105.py with its admission rule, E101 session 2's run_e101s.py, E80's run_kspeed.py, E64's run_hpl.py; E111's
idle-login rule; the residency query E119 sends, which this ettelem build refuses at its argument check before it opens the device), after the same
preflight:

  BLIND POOL 7'S TILES. A run's value may be `file:` a tile of tools/claims-v3/kinds/blind7/tiles/<its type>/ (Q140(x)'s commit 75802201). Before the
  session every such value is checked: the frozen inputs (Q140(x)'s predictions for aifoundry2, the manifest blind7.json and its MANIFEST, the 82 W
  list, M9's aifoundry2 part and its predictor) hash as committed, the value names a tile of the manifest of the run's own type, the run's label is
  `b7-<the tile's name>`, the tile is not one of the six left out by name, and the file is 2,048 B with the manifest's sha256 of the whole, of A and of
  B. Any mismatch refuses the session (exit 2) before the card lock is taken. Every other value (E80's kinds tiles, checked against kinds.json; `zeros`
  for the rest reading) goes through the imported checks.

  THE C LOG (Q139(k)), as E160: the heater is the wrapper tools/claims-v3/ccheck/sparsity_ccheck.sh, which runs the C-logging host
  build/ccheck/b/host/sparsity_host (the binary E160 ran, sha256 pinned in e165_common.py) with every argument run_hpl.py gives it, the runner's own
  --kernel among them (E80's build/sparsity_t2/kernel/sparsity.elf), and appends --c-log <session>/c-log.jsonl --c-poison. This runner sets
  CCHECK_LOG, CCHECK_KERNEL and CCHECK_HOST for the session.

  PREFLIGHT (Q136's rule, "take more care for writing commands"): before anything opens the card, the wrapper and Q139(k)'s two build files hash as
  committed (4946a992), the C-logging host has the pinned sha256 and carries --c-log, --c-poison, --stop-file, --kernel and --budget, and the kernel and
  the sampler are E80's. E165.md classifies every device-management command they send; a different binary could send something else, so a mismatch
  refuses the session (exit 2). run_hpl.py's own preflight is kept, except its two checks that assume the heater is a compiled host beside its kernel
  (replaced by binaries_why below, as in E160). Under --dry no device is touched and the binary checks are skipped (the tile and frozen-input checks
  are not).

Everything that touches the card -- the card lock held for the session, the other-user checks before every launch process, `timeout 10` on every
launch and config read, the sampler WITHOUT --reset-ms, the trace ring and `ettelem config` after every run, the safety stops (protocol.json safety:
abs_stop_c 76 C on one sample, board_cap_w 85 W on cap_consecutive 3), the end of the session unless the TDP and the threshold read back 65, and the
admission rule (82 W at the estimate; the 82 W lock) -- is the imported code. Nothing is set on the card. A protocol whose safety block lacks those
three keys, or whose board stop is above 85 W, is refused here (exit 2).

    python3 run_e165.py --protocol protocol.json --out <RUNDIR> [--dry] [--only BLOCK ...] [--max-card-min N] [--list]
"""
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "e119"))
import e165_common as C  # noqa: E402
import run_e119 as R119  # noqa: E402

H = R119.H
K = R119.RE.RS.K
WANT_TOOLS = {"heater": C.WRAPPER_REL, "kernel": C.KERNEL_REL, "ettelem": C.ETTELEM_REL}
SAFETY_KEYS = ("abs_stop_c", "board_cap_w", "cap_consecutive")
MAX_BOARD_STOP_W = 85.0      # section 22 of the brief: every registered board stop at most 85 W
HOST_FLAGS = (b"--c-log", b"--c-poison", b"--stop-file", b"--kernel", b"--budget")
WRAPPER_MSGS = ("heater and kernel come from different builds", "heater has no --stop-file", "heater has no --kernel", "heater has no --budget")
LEFT_OUT = None

_prev_check = H.Run.check
_prev_verify = K.verify_tiles
_prev_preflight = H.Session.preflight


def left_out(root=ROOT):
    """the six tiles left out by name (admission-aifoundry2-82w.json, frozen in 75802201)"""
    global LEFT_OUT
    if LEFT_OUT is None:
        LEFT_OUT = set(json.load(open(os.path.join(root, C.ADM_REL)))["left_out"])
    return LEFT_OUT


def _check(self):
    """the imported check, with blind pool 7's tiles allowed when they are of the run's own type and carry their b7- label."""
    if not C.is_pool_value(self.values):
        return _prev_check(self)
    bad = []
    rel = str(self.values)[5:]
    if not rel.startswith(f"{C.POOL_REL}/tiles/{self.type}/"):
        bad.append(f"{self.name}: a pool tile must be a tile of its run's type ({rel})")
    if "/" in self.label or not self.label.startswith(C.LABEL_PREFIX):
        bad.append(f"{self.name}: a pool tile needs the label b7-<name> (got {self.label})")
    saved = self.values
    self.values = "zeros"           # every other check of run_hpl's, unchanged
    try:
        bad += K._base_check(self)
    finally:
        self.values = saved
    return bad


def verify_tiles(root, runs):
    """the imported verify_tiles for every other value, plus every pool tile against the manifest and the 82 W list (the addition)."""
    pool = [r for r in runs if C.is_pool_value(r.values)]
    out, kinds_sha, kinds_rev = _prev_verify(root, [r for r in runs if not C.is_pool_value(r.values)])
    if not pool:
        return out, kinds_sha, kinds_rev
    bad = C.check_frozen(root)
    by_value = {C.tile_value(t): t for t in C.manifest(root).values()}
    lo = left_out(root)
    for r in pool:
        t = by_value.get(str(r.values))
        if t is None:
            bad.append(f"{r.values}: not a tile of {C.MAN_REL}")
            continue
        if t["type"] != r.type:
            bad.append(f"{r.values}: a {t['type']} tile, run {r.name} is {r.type}")
        if r.label != C.label_of(t["name"]):
            bad.append(f"{r.name}: label {r.label}, the tile's is {C.label_of(t['name'])}")
        if t["name"] in lo:
            bad.append(f"{r.name}: {t['name']} is left out by name (its 95% upper peak exceeds 82 W)")
        why = C.check_tile(root, t)
        if why:
            bad.append(why)
        out[str(r.values)] = {"type": t["type"], "kind": t["name"], "file": f"{C.POOL_REL}/{t['file']}", "bytes": 2048, "sha256": t["sha256"]["whole"],
                              "sha256_a": t["sha256"]["a"], "sha256_b": t["sha256"]["b"], "pool": "blind7", "priority": t.get("priority")}
    if bad:
        raise SystemExit("refused: " + "; ".join(bad))
    return out, kinds_sha, kinds_rev


def binaries_why(root):
    """[] if the wrapper, the C-logging host, E80's kernel and the sampler are the pinned bytes and the host carries the flags, else what is wrong."""
    bad = []
    for rel, want in list(C.CCHECK_FROZEN.items()) + [(C.CC_HOST_REL, C.CC_HOST_SHA256)] + list(C.E80_SHA256.items()):
        p = os.path.join(root, rel)
        got = C.sha256_file(p) if os.path.isfile(p) else None
        if got != want:
            bad.append(f"{rel}: sha256 {got}, registered {want}")
    p = os.path.join(root, C.CC_HOST_REL)
    if os.path.isfile(p):
        blob = open(p, "rb").read()
        for flag in HOST_FLAGS:
            if flag not in blob:
                bad.append(f"{C.CC_HOST_REL} has no {flag.decode()}")
    if not os.access(os.path.join(root, C.WRAPPER_REL), os.X_OK):
        bad.append(f"{C.WRAPPER_REL} is not executable")
    return bad


def _preflight(self):
    """run_hpl.py's preflight, its two compiled-heater checks replaced by binaries_why() (as E160)."""
    try:
        _prev_preflight(self)
        rest = []
    except H.Refuse as e:
        rest = [m for m in str(e).split("; ") if m and m not in WRAPPER_MSGS]
    if not self.dry:
        rest += binaries_why(self.root)
    if rest:
        raise H.Refuse("; ".join(rest))


H.Run.check = _check
K.verify_tiles = verify_tiles
H.Session.preflight = _preflight


def preflight(proto, root):
    """None if the protocol's tools are the wrapper, E80's kernel and sampler, every pinned binary hashes as registered, its safety block names the
    watcher's keys with a board stop at most 85 W, and no run is a tile left out by name; else why not (selftest_e165.py runs it)."""
    tools = proto.get("tools", {})
    sf = proto.get("safety", {})
    bad = [f"protocol safety lacks {k}" for k in SAFETY_KEYS if k not in sf]
    if "board_cap_w" in sf and float(sf["board_cap_w"]) > MAX_BOARD_STOP_W:
        bad.append(f"protocol board stop {sf['board_cap_w']} W is above {MAX_BOARD_STOP_W:g} W")
    for k, rel in WANT_TOOLS.items():
        if tools.get(k) != rel:
            bad.append(f"protocol tools.{k} is {tools.get(k)!r}, not {rel!r}")
    lo = left_out(ROOT)
    for bl in proto.get("blocks", []):
        for r in bl.get("runs", []):
            n = C.name_of(str(r.get("label", "")))
            if n in lo:
                bad.append(f"protocol runs {n}, left out by name")
    bad += binaries_why(root)
    return "; ".join(bad) if bad else None


def main():
    pr = sys.argv[sys.argv.index("--protocol") + 1]
    proto = json.load(open(pr))
    dry = "--dry" in sys.argv
    root = ROOT
    if "--root" in sys.argv:
        root = os.path.abspath(sys.argv[sys.argv.index("--root") + 1])
    got = {}
    sf = proto.get("safety", {})
    miss = [k for k in SAFETY_KEYS if k not in sf]
    if miss and "--list" not in sys.argv:          # under --dry too: a stop the watcher cannot read is no stop
        print(f"refused: protocol safety lacks {', '.join(miss)}", file=sys.stderr)
        return 2
    if float(sf.get("board_cap_w", 0)) > MAX_BOARD_STOP_W and "--list" not in sys.argv:
        print(f"refused: protocol board stop {sf.get('board_cap_w')} W is above {MAX_BOARD_STOP_W:g} W", file=sys.stderr)
        return 2
    bad = C.check_frozen(root)
    if bad:
        print("refused: " + "; ".join(bad), file=sys.stderr)
        return 2
    lo = left_out(root)
    lab = [C.name_of(str(r.get("label", ""))) for bl in proto.get("blocks", []) for r in bl.get("runs", [])]
    if any(n in lo for n in lab) and "--list" not in sys.argv:
        print(f"refused: the protocol runs a tile left out by name ({sorted(set(n for n in lab if n in lo))})", file=sys.stderr)
        return 2
    if not dry and "--list" not in sys.argv:
        why = preflight(proto, root)
        if why is not None:
            print(f"refused: {why}", file=sys.stderr)
            return 2
        got = {rel: C.sha256_file(os.path.join(root, rel)) for rel in [C.WRAPPER_REL, C.CC_HOST_REL] + list(C.E80_SHA256)}
    if "--out" in sys.argv and "--list" not in sys.argv:
        rd = os.path.abspath(sys.argv[sys.argv.index("--out") + 1])
        os.makedirs(rd, exist_ok=True)
        os.environ["CCHECK_LOG"] = os.path.join(rd, "c-log.jsonl")
        os.environ["CCHECK_KERNEL"] = os.path.join(root, C.KERNEL_REL)
        os.environ["CCHECK_HOST"] = os.path.join(root, C.CC_HOST_REL)
        if not os.path.exists(os.path.join(rd, "e165.json")):
            json.dump({"experiment": "E165", "request": "Q141(g)", "wrapper": "tools/claims-v3/e165/run_e165.py", "wrapper_sha256": C.sha256_file(__file__),
                       "e165_common_sha256": C.sha256_file(C.__file__), "run_e119_sha256": C.sha256_file(R119.__file__), "protocol": os.path.basename(pr),
                       "protocol_sha256": C.sha256_file(pr), "predictions_sha256": C.sha256_file(os.path.join(HERE, "predictions-e165.json")),
                       "frozen_inputs": {**C.FROZEN, **C.CCHECK_FROZEN}, "binaries_checked": got, "dry": dry, "safety": proto.get("safety"),
                       "ccheck_env": {k: os.environ[k] for k in ("CCHECK_LOG", "CCHECK_KERNEL", "CCHECK_HOST")},
                       "t_ms": int(time.time() * 1000), "zone": time.strftime("%Z"), "argv": sys.argv}, open(os.path.join(rd, "e165.json"), "w"), indent=1)
    return R119.main()


if __name__ == "__main__":
    sys.exit(main())
