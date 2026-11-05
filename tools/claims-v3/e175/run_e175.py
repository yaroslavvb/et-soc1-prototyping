#!/usr/bin/env python3
"""E175 (Q143(g)): the session runner. It is E173's run_e173.py (lab 5a2a9ba0) with E175's pool and names (tools/claims-v3/e175/E175.md, lab
c50ff493): E165's run_e165.py with E175's names, and one addition, the watcher fix. E119's run_e119.py,
imported and run unchanged (E105's run_e105.py with its admission rule, E101 session 2's run_e101s.py, E80's run_kspeed.py, E64's run_hpl.py;
E111's idle-login rule; the residency query E119 sends, which this ettelem build refuses at its argument check before it opens the device), after
the same preflight:

  THE WATCHER FIX (run_hpl.py's dated amendment, tools/claims-v3/hpl/run_hpl.py.dated-note.md, "Which future runs use it"): before any Session is
  built, watcher_q142s.install(H) replaces run_hpl's Watcher with the one without the follow() race (E165's D2). install() refuses a run_hpl.py
  with other bytes; then this runner refuses the session (exit 2). Its record goes in the session's e175.json.

  E175'S TILES. A run's value may be `file:` a tile of tools/claims-v3/e175/pool/tiles/<its type>/ (E175's predictions commit). Before the session
  every such value is checked: the frozen inputs (frozen-sha256-e175.json) hash as registered, the value names a tile of e175.json of the run's
  own type, the run's label is `e5-<the tile's name>`, the tile is not left out by name (E175 leaves none: the selection replaced every candidate
  over 82 W), and the file is 2,048 B with the manifest's sha256 of the whole, of A and of B. Any mismatch refuses the session (exit 2) before the
  card lock is taken. Every other value (E80's kinds tiles, checked against kinds.json; `zeros` for the rest reading) goes through the imported
  checks.

  THE C LOG (Q139(k)), as E165: the heater is the wrapper tools/claims-v3/ccheck/sparsity_ccheck.sh, which runs the C-logging host
  build/ccheck/b/host/sparsity_host (the binary E160 built and E165 ran, sha256 pinned in e165_common.py) and appends --c-log
  <session>/c-log.jsonl --c-poison. This runner sets CCHECK_LOG, CCHECK_KERNEL and CCHECK_HOST for the session.

  PREFLIGHT, as E165's (Q136's rule): the wrapper and Q139(k)'s two build files hash as committed, the C-logging host has the pinned sha256 and
  carries its flags, and the kernel and the sampler are E80's; a mismatch refuses the session (exit 2). Under --dry no device is touched and the
  binary checks are skipped (the tile, frozen-input and watcher checks are not).

Everything that touches the card -- the card lock held for the session, the other-user checks before every launch process, `timeout 10` on every
launch and config read, the sampler WITHOUT --reset-ms, the trace ring and `ettelem config` after every run, the safety stops (abs_stop_c 76 C on
one sample, board_cap_w 85 W on cap_consecutive 3), the end of the session unless the TDP and the threshold read back 65, and the admission rule
(82 W at the estimate; the 82 W lock) -- is the imported code. Nothing is set on the card.

    python3 run_e175.py --protocol protocol.json --out <RUNDIR> [--dry] [--only BLOCK ...] [--max-card-min N] [--list]
SPDX-License-Identifier: Apache-2.0
"""
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
TOP = os.path.normpath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "e119"))
sys.path.insert(0, os.path.join(HERE, "..", "hpl"))
import e175_common as C  # noqa: E402
import run_e119 as R119  # noqa: E402
import watcher_q142s as W  # noqa: E402

H = R119.H
K = R119.RE.RS.K
WANT_TOOLS = {"heater": C.WRAPPER_REL, "kernel": C.KERNEL_REL, "ettelem": C.ETTELEM_REL}
SAFETY_KEYS = ("abs_stop_c", "board_cap_w", "cap_consecutive")
MAX_BOARD_STOP_W = 85.0
HOST_FLAGS = (b"--c-log", b"--c-poison", b"--stop-file", b"--kernel", b"--budget")
WRAPPER_MSGS = ("heater and kernel come from different builds", "heater has no --stop-file", "heater has no --kernel", "heater has no --budget")
try:
    WATCHER = W.install(H)
    WATCHER_WHY = None
except RuntimeError as e:          # the session is refused in main(), before anything opens a device
    WATCHER, WATCHER_WHY = None, str(e)
_P = None

_prev_check = H.Run.check
_prev_verify = K.verify_tiles
_prev_preflight = H.Session.preflight


def pred():
    global _P
    if _P is None:
        with open(os.path.join(HERE, "predictions-e175.json")) as f:
            _P = json.load(f)
    return _P


def left_out():
    return set(pred()["left_out"])


def _check(self):
    """the imported check, with E175's tiles allowed when they are of the run's own type and carry their e5- label"""
    if not C.is_pool_value(self.values):
        return _prev_check(self)
    bad = []
    rel = str(self.values)[5:]
    if not rel.startswith(f"{C.POOL_REL}/tiles/{self.type}/"):
        bad.append(f"{self.name}: a pool tile must be a tile of its run's type ({rel})")
    if "/" in self.label or not self.label.startswith(C.LABEL_PREFIX):
        bad.append(f"{self.name}: a pool tile needs the label e5-<name> (got {self.label})")
    saved = self.values
    self.values = "zeros"
    try:
        bad += K._base_check(self)
    finally:
        self.values = saved
    return bad


def verify_tiles(top, runs):
    """the imported verify_tiles for every other value, plus every pool tile against the manifest and the left-out list"""
    pool = [r for r in runs if C.is_pool_value(r.values)]
    out, kinds_sha, kinds_rev = _prev_verify(top, [r for r in runs if not C.is_pool_value(r.values)])
    if not pool:
        return out, kinds_sha, kinds_rev
    bad = C.check_frozen(top)
    by_value = {C.tile_value(t): t for t in C.manifest(top).values()}
    lo = left_out()
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
            bad.append(f"{r.name}: {t['name']} is left out by name")
        why = C.check_tile(top, t)
        if why:
            bad.append(why)
        out[str(r.values)] = {"type": t["type"], "kind": t["name"], "file": f"{C.POOL_REL}/{t['file']}", "bytes": 2048, "sha256": t["sha256"]["whole"],
                              "sha256_a": t["sha256"]["a"], "sha256_b": t["sha256"]["b"], "pool": "e175", "priority": t.get("priority")}
    if bad:
        raise SystemExit("refused: " + "; ".join(bad))
    return out, kinds_sha, kinds_rev


def binaries_why(top):
    bad = []
    for rel, want in list(C.CCHECK_FROZEN.items()) + [(C.CC_HOST_REL, C.CC_HOST_SHA256)] + list(C.E80_SHA256.items()):
        p = os.path.join(top, rel)
        got = C.sha256_file(p) if os.path.isfile(p) else None
        if got != want:
            bad.append(f"{rel}: sha256 {got}, registered {want}")
    p = os.path.join(top, C.CC_HOST_REL)
    if os.path.isfile(p):
        with open(p, "rb") as f:
            blob = f.read()
        for flag in HOST_FLAGS:
            if flag not in blob:
                bad.append(f"{C.CC_HOST_REL} has no {flag.decode()}")
    if not os.access(os.path.join(top, C.WRAPPER_REL), os.X_OK):
        bad.append(f"{C.WRAPPER_REL} is not executable")
    return bad


def _preflight(self):
    """run_hpl.py's preflight, its two compiled-heater checks replaced by binaries_why() (as E165 and E160)"""
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


def protocol_why(proto, top):
    """None if the protocol's tools are the wrapper, E80's kernel and sampler, its safety block names the watcher's keys with a board stop at most
    85 W and a die stop at most 76 C, its admission is at most 82 W, and no run is a tile left out by name; else why not"""
    tools = proto.get("tools", {})
    sf = proto.get("safety", {})
    bad = [f"protocol safety lacks {k}" for k in SAFETY_KEYS if k not in sf]
    if "board_cap_w" in sf and float(sf["board_cap_w"]) > MAX_BOARD_STOP_W:
        bad.append(f"protocol board stop {sf['board_cap_w']} W is above {MAX_BOARD_STOP_W:g} W")
    if "abs_stop_c" in sf and float(sf["abs_stop_c"]) > C.STOPS["abs_stop_c"]:
        bad.append(f"protocol die stop {sf['abs_stop_c']} C is above {C.STOPS['abs_stop_c']} C")
    if float(proto.get("limit_p800_w", 999)) > C.LIMIT_W or float(proto.get("peak_lock_w", 999)) > C.PEAK_LOCK_W:
        bad.append(f"admission {proto.get('limit_p800_w')} W / lock {proto.get('peak_lock_w')} W looser than {C.LIMIT_W:g} / {C.PEAK_LOCK_W:g} W")
    for k, rel in WANT_TOOLS.items():
        if tools.get(k) != rel:
            bad.append(f"protocol tools.{k} is {tools.get(k)!r}, not {rel!r}")
    lo = left_out()
    for bl in proto.get("blocks", []):
        for r in bl.get("runs", []):
            n = C.name_of(str(r.get("label", "")))
            if n in lo:
                bad.append(f"protocol runs {n}, left out by name")
    return "; ".join(bad) if bad else None


def main():
    pr = sys.argv[sys.argv.index("--protocol") + 1]
    with open(pr) as f:
        proto = json.load(f)
    dry = "--dry" in sys.argv
    top = TOP
    if "--root" in sys.argv:
        top = os.path.abspath(sys.argv[sys.argv.index("--root") + 1])
    listing = "--list" in sys.argv
    if WATCHER_WHY is not None and not listing:
        print(f"refused: the watcher fix did not install: {WATCHER_WHY}", file=sys.stderr)
        return 2
    why = protocol_why(proto, top)
    if why and not listing:
        print(f"refused: {why}", file=sys.stderr)
        return 2
    bad = C.check_frozen(top)
    if bad:
        print("refused: " + "; ".join(bad), file=sys.stderr)
        return 2
    got = {}
    if not dry and not listing:
        b = binaries_why(top)
        if b:
            print("refused: " + "; ".join(b), file=sys.stderr)
            return 2
        got = {rel: C.sha256_file(os.path.join(top, rel)) for rel in [C.WRAPPER_REL, C.CC_HOST_REL] + list(C.E80_SHA256)}
    if "--out" in sys.argv and not listing:
        rd = os.path.abspath(sys.argv[sys.argv.index("--out") + 1])
        os.makedirs(rd, exist_ok=True)
        os.environ["CCHECK_LOG"] = os.path.join(rd, "c-log.jsonl")
        os.environ["CCHECK_KERNEL"] = os.path.join(top, C.KERNEL_REL)
        os.environ["CCHECK_HOST"] = os.path.join(top, C.CC_HOST_REL)
        if not os.path.exists(os.path.join(rd, "e175.json")):
            with open(os.path.join(rd, "e175.json"), "w") as f:
                json.dump({"experiment": "E175", "request": "Q143(g)", "wrapper": "tools/claims-v3/e175/run_e175.py", "wrapper_sha256": C.sha256_file(__file__),
                           "e175_common_sha256": C.sha256_file(C.__file__), "run_e119_sha256": C.sha256_file(R119.__file__),
                           "run_hpl_sha256": C.sha256_file(H.__file__), "watcher": WATCHER, "protocol": os.path.basename(pr),
                           "protocol_sha256": C.sha256_file(pr), "predictions_sha256": C.sha256_file(os.path.join(HERE, "predictions-e175.json")),
                           "frozen_list_sha256": C.sha256_file(C.FROZEN_FILE), "binaries_checked": got, "dry": dry, "safety": proto.get("safety"),
                           "ccheck_env": {k: os.environ[k] for k in ("CCHECK_LOG", "CCHECK_KERNEL", "CCHECK_HOST")},
                           "t_ms": int(time.time() * 1000), "zone": time.strftime("%Z"), "argv": sys.argv}, f, indent=1)
    return R119.main()


if __name__ == "__main__":
    sys.exit(main())
