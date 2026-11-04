#!/usr/bin/env python3
"""E170 (Q141(w)): the session runner on aifoundry1 card 0. It composes runners already run on the lab's cards, each imported unchanged, in this order:

  1. E84's card-0 runner, tools/claims-v3/kspeed/e84/run_e84.py (31 Oct; E114 ran it again on 1 Nov), over E80's run_kspeed.py and E64's run_hpl.py:
     ET_DEVICES=0 for every child, card 0's lock /run/lock/etsoc-shire0.lock held for the session, the other-user test on BOTH cards through
     et-holders before the session and before every launch process, the configuration test after every run against the session's start read;
  2. E119's run_e119.py (over E105's run_e105.py and E101 session 2's run_e101s.py): E105's admission rule around E84's run_one (imported after E84,
     so it wraps E84's), E119's cap (a run starts only if its planned time fits), E111's idle-login rule, and the residency query rewritten to
     states 1-3, which E170's guard then refuses before the reader starts.

and adds, each marked E170:

  E170-1  THE TOOLS. The heater is Q139(k)'s wrapper tools/claims-v3/ccheck/sparsity_ccheck.sh running the C-logging host E157 built on aifoundry1
          (build/ccheck/b/host/sparsity_host, pinned) with E78's kernel there (build/sparsity/kernel/sparsity.elf, pinned); the sampler and every
          query go through tools/claims-v3/e170/ettelem_guard_e170.sh in front of E84's build/ettelem-e84/ettelem (pinned). A protocol naming other
          tools, or any binary with other bytes, is refused (exit 2) before card 0's lock is taken. E84's preflight is kept, except its checks that
          assume the heater is aifoundry1's compiled build/sparsity host beside its kernel, which the pinned-bytes check replaces (as E165 did for
          run_hpl's).
  E170-2  BLIND POOL 7. A run's value may be `file:` a tile of tools/claims-v3/kinds/blind7/tiles/<its type>/: before the session every such value
          is checked against the manifest (the tile's type, its b7- label, 2,048 B and the sha256 of the whole, of A and of B) and refused if it is
          one of the 19 tiles predictions-e170.json leaves out by name (exit 2).
  E170-3  THE STOPS. The protocol's safety block must name the watcher's keys and be at least as strict as E170's (abs_stop_c <= 72, board_cap_w
          <= 65.9, cap_consecutive 1); a looser block is refused (exit 2). The admission line must be at most 60 W and the lock at most 62 W.
  E170-4  THE ALARM. After every run, any sampler line of it under 590 MHz (the PMIC over-power alarm's 300 MHz safe state, E84) ends the session
          at once (exit 4, reason safety:e170_alarm), as a safety stop does.
  E170-5  NO DRAIN. E84's queue drain (the stock dev_mngt_service, which opens both cards' management nodes) is refused: it is not in E170's list.

Nothing is set on the card. Device commands: E170.md, "Device commands sent".

    ET_DEVICES=0 V3_DEVICE=0 python3 run_e170.py --protocol <protocol.json> --out <RUNDIR> [--dry] [--only BLOCK ...] [--max-card-min N] [--list]
SPDX-License-Identifier: Apache-2.0
"""
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, "..", "..", ".."))
for var in ("V3_DEVICE", "ET_DEVICES"):
    if os.environ.get(var, "0") != "0":
        print(f"refused: {var}={os.environ[var]}; E170 runs on card 0 only", file=sys.stderr)
        sys.exit(2)
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "..", "kspeed", "e84"))
sys.path.insert(0, os.path.join(HERE, "..", "e119"))
import e170_common as C  # noqa: E402
import run_e84 as R84  # noqa: E402  (1: card 0's replacements; sets ET_DEVICES=0 and V3_DEVICE=0)
import run_e119 as R119  # noqa: E402  (2: E105's admission now wraps E84's run_one)

H = R84.H
K = R84.K
assert R119.H is H and R119.RE.RS.K is K, "run_e84 and run_e119 must share run_hpl and run_kspeed"
WANT_TOOLS = {"heater": C.WRAPPER_REL, "kernel": C.KERNEL_REL, "ettelem": C.GUARD_REL}
SAFETY_KEYS = ("abs_stop_c", "board_cap_w", "cap_consecutive")
E84_HEATER_MSGS = ("the heater must be aifoundry1's build/sparsity", "heater and kernel come from different builds", "heater has no ", "ettelem ")
PRED = None

_prev_check = H.Run.check
_prev_verify = K.verify_tiles
_prev_preflight = H.Session.preflight     # E84's
_prev_run_one = H.Session.run_one         # E119's (E105's admission around E84's run_one)


def pred():
    global PRED
    if PRED is None:
        PRED = json.load(open(os.path.join(HERE, "predictions-e170.json")))
    return PRED


def _check(self):
    """the imported check, with blind pool 7's tiles allowed when they are of the run's own type and carry their b7- label (E170-2)"""
    if not C.is_pool_value(self.values):
        return _prev_check(self)
    bad = []
    rel = str(self.values)[5:]
    if not rel.startswith(f"{C.POOL_REL}/tiles/{self.type}/"):
        bad.append(f"{self.name}: a pool tile must be a tile of its run's type ({rel})")
    if "/" in self.label or not self.label.startswith(C.LABEL_PREFIX):
        bad.append(f"{self.name}: a pool tile needs the label b7-<name> (got {self.label})")
    saved = self.values
    self.values = "zeros"
    try:
        bad += K._base_check(self)
    finally:
        self.values = saved
    return bad


def verify_tiles(root, runs):
    """the imported verify_tiles for every other value, plus every pool tile against the manifest and E170's left-out list (E170-2)"""
    pool = [r for r in runs if C.is_pool_value(r.values)]
    out, kinds_sha, kinds_rev = _prev_verify(root, [r for r in runs if not C.is_pool_value(r.values)])
    if not pool:
        return out, kinds_sha, kinds_rev
    bad = C.check_frozen(root)
    by_value = {C.tile_value(t): t for t in C.manifest(root).values()}
    lo = set(pred()["left_out"])
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
            bad.append(f"{r.name}: {t['name']} is left out by name (its card-0 estimate exceeds {C.ADMIT_LINE_W:g} W)")
        why = C.check_tile(root, t)
        if why:
            bad.append(why)
        out[str(r.values)] = {"type": t["type"], "kind": t["name"], "file": f"{C.POOL_REL}/{t['file']}", "bytes": 2048, "sha256": t["sha256"]["whole"],
                              "sha256_a": t["sha256"]["a"], "sha256_b": t["sha256"]["b"], "pool": "blind7", "priority": t.get("priority")}
    if bad:
        raise SystemExit("refused: " + "; ".join(bad))
    return out, kinds_sha, kinds_rev


def binaries_why(root):
    """[] if the wrapper and Q139(k)'s files, the C-logging host, the kernel and E84's ettelem are the pinned bytes, the host carries its flags and the
    guard and wrapper are executable; else what is wrong (E170-1)"""
    bad = []
    for rel, want in list(C.CCHECK_FROZEN.items()) + list(C.BOX_BINARIES.items()):
        p = os.path.join(root, rel)
        got = C.sha256_file(p) if os.path.isfile(p) else None
        if got != want:
            bad.append(f"{rel}: sha256 {got}, registered {want}")
    p = os.path.join(root, C.CC_HOST_REL)
    if os.path.isfile(p):
        blob = open(p, "rb").read()
        for flag in (b"--c-log", b"--c-poison", b"--stop-file", b"--kernel", b"--budget", b"file:"):
            if flag not in blob:
                bad.append(f"{C.CC_HOST_REL} has no {flag.decode()}")
    p = os.path.join(root, C.ETTELEM_REL)
    if os.path.isfile(p):
        blob = open(p, "rb").read()
        for word in (b"uptime", b"sptrace", b"config", b"sample"):
            if word not in blob:
                bad.append(f"{C.ETTELEM_REL} has no {word.decode()}")
    for rel in (C.WRAPPER_REL, C.GUARD_REL):
        if not os.access(os.path.join(root, rel), os.X_OK):
            bad.append(f"{rel} is not executable")
    return bad


def _preflight(self):
    """E84's preflight, its compiled-heater and ettelem-blob checks replaced by binaries_why() (E170-1)"""
    try:
        _prev_preflight(self)
        rest = []
    except H.Refuse as e:
        rest = [m for m in str(e).split("; ") if m and not any(m.startswith(x) for x in E84_HEATER_MSGS)]
    if not self.dry:
        rest += binaries_why(self.root)
    if rest:
        raise H.Refuse("; ".join(rest))


def _drain(self):
    """E170-5: no drain; the stock CLI opens both cards' management nodes"""
    self.mark("e170_drain_refused", "dev_mngt_service is not in E170's classified command list")


def _run_one(self, r, k, n):
    """E119's run_one (the cap, then E105's admission around E84's run_one), then the alarm check on the run's own sampler lines (E170-4)"""
    rec = _prev_run_one(self, r, k, n)
    if rec is None or self.dry:
        return rec
    low = []
    try:
        for ln in open(os.path.join(self.rundir, rec["tel"]), "rb"):
            if ln.startswith(b"{"):
                t = H.parse_tel(ln)
                if t is not None and t[4] is not None and t[4] < C.MIN_MHZ_ALARM:
                    low.append((t[0], t[4]))
    except OSError:
        pass
    if low:
        why = f"e170_alarm {len(low)} sampler lines under {C.MIN_MHZ_ALARM:g} MHz in {r.name} (first {low[0][1]:g} MHz at {low[0][0]})"
        self.mark("e170_alarm", why)
        self.touch(self.stop_file)
        raise H.EndSession(f"safety:{why}", H.EXIT_SAFETY)
    return rec


H.Run.check = _check
K.verify_tiles = verify_tiles
H.Session.preflight = _preflight
H.Session.drain = _drain
H.Session.run_one = _run_one


def protocol_why(proto):
    """None, or why the protocol may not run (E170-1, E170-3): its tools, its stops, its admission, no left-out tile"""
    bad = []
    tools = proto.get("tools", {})
    for k, rel in WANT_TOOLS.items():
        if tools.get(k) != rel:
            bad.append(f"protocol tools.{k} is {tools.get(k)!r}, not {rel!r}")
    sf = proto.get("safety", {})
    bad += [f"protocol safety lacks {k}" for k in SAFETY_KEYS if k not in sf]
    if not bad:
        if float(sf["abs_stop_c"]) > C.SAFETY["abs_stop_c"]:
            bad.append(f"die stop {sf['abs_stop_c']} C is looser than {C.SAFETY['abs_stop_c']} C")
        if float(sf["board_cap_w"]) > C.SAFETY["board_cap_w"]:
            bad.append(f"board stop {sf['board_cap_w']} W is looser than {C.SAFETY['board_cap_w']} W")
        if int(sf["cap_consecutive"]) != C.SAFETY["cap_consecutive"]:
            bad.append(f"board stop on {sf['cap_consecutive']} samples, not {C.SAFETY['cap_consecutive']}")
    if float(proto.get("limit_p800_w", 999)) > C.ADMIT_LINE_W or float(proto.get("peak_lock_w", 999)) > C.PEAK_LOCK_W:
        bad.append(f"admission {proto.get('limit_p800_w')} W / lock {proto.get('peak_lock_w')} W looser than {C.ADMIT_LINE_W:g} / {C.PEAK_LOCK_W:g} W")
    lo = set(pred()["left_out"])
    for bl in proto.get("blocks", []):
        for r in bl.get("runs", []):
            nm = C.name_of(str(r.get("label", "")))
            if nm in lo:
                bad.append(f"protocol runs {nm}, left out by name")
            if nm is not None and nm not in pred()["tiles"]:
                bad.append(f"protocol runs {nm}, not an admitted tile")
    return "; ".join(bad) if bad else None


def main():
    pr = sys.argv[sys.argv.index("--protocol") + 1]
    proto = json.load(open(pr))
    dry = "--dry" in sys.argv
    root = ROOT
    if "--root" in sys.argv:
        root = os.path.abspath(sys.argv[sys.argv.index("--root") + 1])
    why = protocol_why(proto)
    if why and "--list" not in sys.argv:
        print(f"refused: {why}", file=sys.stderr)
        return 2
    bad = C.check_frozen(root)
    if bad:
        print("refused: " + "; ".join(bad), file=sys.stderr)
        return 2
    got = {}
    if not dry and "--list" not in sys.argv:
        b = binaries_why(root)
        if b:
            print("refused: " + "; ".join(b), file=sys.stderr)
            return 2
        got = {rel: C.sha256_file(os.path.join(root, rel)) for rel in [C.WRAPPER_REL, C.GUARD_REL] + list(C.BOX_BINARIES)}
    if "--out" in sys.argv and "--list" not in sys.argv:
        rd = os.path.abspath(sys.argv[sys.argv.index("--out") + 1])
        os.makedirs(rd, exist_ok=True)
        os.environ["CCHECK_LOG"] = os.path.join(rd, "c-log.jsonl")
        os.environ["CCHECK_KERNEL"] = os.path.join(root, C.KERNEL_REL)
        os.environ["CCHECK_HOST"] = os.path.join(root, C.CC_HOST_REL)
        if not os.path.exists(os.path.join(rd, "e170.json")):
            json.dump({"experiment": "E170", "request": "Q141(w)", "card": C.CARD, "et_devices": os.environ.get("ET_DEVICES"),
                       "wrapper": "tools/claims-v3/e170/run_e170.py", "wrapper_sha256": C.sha256_file(__file__),
                       "e170_common_sha256": C.sha256_file(C.__file__), "run_e84_sha256": C.sha256_file(R84.__file__),
                       "run_e119_sha256": C.sha256_file(R119.__file__), "run_hpl_sha256": C.sha256_file(H.__file__),
                       "protocol": os.path.basename(pr), "protocol_sha256": C.sha256_file(pr),
                       "predictions_sha256": C.sha256_file(os.path.join(HERE, "predictions-e170.json")),
                       "binaries_checked": got, "dry": dry, "safety": proto.get("safety"), "kappa0": C.KAPPA0,
                       "ccheck_env": {k: os.environ[k] for k in ("CCHECK_LOG", "CCHECK_KERNEL", "CCHECK_HOST")},
                       "t_ms": int(time.time() * 1000), "zone": time.strftime("%Z"), "argv": sys.argv}, open(os.path.join(rd, "e170.json"), "w"), indent=1)
    return R119.main()


if __name__ == "__main__":
    sys.exit(main())
