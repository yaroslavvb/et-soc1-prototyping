#!/usr/bin/env python3
"""E167 (Q141(h)): one step's session of the queue (SMOKE, STOPTEST-DIE, STOPTEST-BOARD, G1Q, END, G2Q, END2), registered in E167.md
(7ba987b3). It IS E161's runner, tools/claims-v3/e161/run_e161.py (E144b's chain: E80's ../kspeed/run_kspeed.py over E64's
../hpl/run_hpl.py, E111's idle-login rule, E133's residency read never sent, the audited chain's sha256; E160's pool-6 tile check and
Q139(k)'s C log on every launch), with E167's names and one addition (E167.md G1, departure D1):

  G1Q's START GATE. A protocol that carries "e167_gate" (protocol-g1q.json) has its HOLD block's run preceded by a check of the REST's
  anchor, read exactly as reduce_e161.rest_reading reads it (the mean of minshire[0] and board_w over the REST file's last 120 s of
  sampler lines that carry board_w and temp_c): if it reads above 49.0 C, or from fewer than 600 lines, no work process starts and the
  session ends with exit 6 ("gate:..."), its end.json saying why. (The REST block's own start waits up to 240 s for a die of 49 C or less:
  protocol-g1q.json.) Under --dry only, E167_DRY_GATE_C=<C> raises the gate's line so a desk dry pass can exercise the HOLD path on the
  toy card (whose die reads about 51 C).

E161's, kept unchanged in content:

  BLIND POOL 6's TILES (E160's). A run's value may be `file:` a tile of tools/claims-v3/kinds/blind6/tiles/<its type>/ (Q139(x)'s commit
  d98d2e34). Before the session every such value is checked by e160_common.py (imported, sha256-pinned): the frozen inputs (Q139(x)'s
  predictions for aifoundry2, blind6.json, its MANIFEST, M8's m8.json, Q139(k)'s three run-time files) hash as committed, the value names a
  tile of the manifest of the run's own type, the run's label is `b6-<the tile's name>`, and the file is 2,048 B with the manifest's
  sha256 of the whole, of A and of B. Any mismatch refuses the session (exit 2) before the card lock is taken.

  THE C LOG (Q139(k), E160's use on this card): the heater is the wrapper tools/claims-v3/ccheck/sparsity_ccheck.sh running the C-logging
  host build/ccheck/b/host/sparsity_host (sha256 eae32a15...) with E80's kernel build/sparsity_t2/kernel/sparsity.elf as the runner's own
  --kernel, appending --c-log <session>/c-log.jsonl --c-poison (one 1 MiB write before and one 1 MiB read after each launch, outside its
  window; runtime DMA, no device-management command).

  NO RESIDENCY READ (run_hpl.py:622's `ettelem residency 2 3 4 5 6` is answered unsent: no process, no device; one line in
  <RUNDIR>/e167-not-sent.jsonl); THE AUDITED CHAIN (run_hpl.py, run_kspeed.py, idle_logins_e111.py and e160_common.py hashed before import;
  any other copy refuses with exit 2); THE BINARIES (real runs only: the wrapper and Q139(k)'s two build files, the C-logging host
  eae32a15..., E80's kernel 990807f4... and sampler 77a46171...; the host must carry --c-log, --c-poison, --stop-file, --kernel and
  --budget); THE STOPS (a protocol whose safety block lacks abs_stop_c, board_cap_w or cap_consecutive, or sets abs_stop_c above 72 C,
  board_cap_w above 80 W or cap_consecutive above 3, is refused with exit 2; the stop tests lower one).

Everything that touches the card -- the card lock held for the session, the other-user checks before every launch process, `timeout 10`
on every launch and config read, the sampler WITHOUT --reset-ms, the trace ring and `ettelem config` after every run, the safety watcher
(it reads every live sampler line: the die mean or the hottest sensor >= abs_stop_c on one line, or board_w > board_cap_w on
cap_consecutive lines, touches the stop-file and ends the session with exit 4), and the end of the session unless the TDP and the
threshold read back 65 -- is run_hpl.py's own code. Nothing is set on the card.

Before the session it writes <RUNDIR>/e167.json: this wrapper's sha256, the protocol's, the chain's, the binaries', the C log's
environment, and the zone the box's clock is in (every time in E167 is epoch ms).

    python3 run_e167.py --protocol protocol-g1q.json --out <RUNDIR> [--dry] [--max-card-min N] [--list]
Exit codes: run_hpl.py's (0 done, 1 error, 2 refused, 3 the card is not ours, 4 a safety stop, 5 a signal), and 6, G1Q's start gate.
"""
import glob
import gzip
import hashlib
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, "..", "..", ".."))

AUDITED = {os.path.join("hpl", "run_hpl.py"): "68493295504fba5d4e9056b4f7e7387179d555e4157bbae32075b4197f3df227",
           os.path.join("kspeed", "run_kspeed.py"): "d3d844c7912d873fb1fe80c92dd72124d2714e493bcf4f73a961cfa26d894c0c",
           os.path.join("e111", "idle_logins_e111.py"): "91094be5f9af14c0897a817b7d95777fdaaa6ab12b49304883ccb3d066574ef4",
           os.path.join("e160", "e160_common.py"): "24ecb6f87eb8e253f1c63e7ccb284e379de8cf4477e356b37792ce0def162d43"}
WANT_TOOLS = {"heater": "tools/claims-v3/ccheck/sparsity_ccheck.sh", "kernel": "build/sparsity_t2/kernel/sparsity.elf",
              "ettelem": "build/ettelem-hpl/ettelem"}
STOP_MAX = {"abs_stop_c": 72.0, "board_cap_w": 80.0, "cap_consecutive": 3}
HOST_FLAGS = (b"--c-log", b"--c-poison", b"--stop-file", b"--kernel", b"--budget")
# run_hpl.py preflight's checks that assume a compiled heater beside its kernel: replaced for the wrapper by binaries_why() (E160's list)
WRAPPER_MSGS = ("heater and kernel come from different builds", "heater has no --stop-file", "heater has no --kernel", "heater has no --budget")


def sha256(path):
    return hashlib.sha256(open(path, "rb").read()).hexdigest()


def chain_differs():
    bad = []
    for rel, want in AUDITED.items():
        p = os.path.realpath(os.path.join(HERE, "..", rel))
        try:
            got = sha256(p)
        except OSError as e:
            got = f"unreadable: {e}"
        if got != want:
            bad.append(f"{rel}: {got[:16]} (audited {want[:16]})")
    return bad


def protocol_refusals(argv):
    """the tools and the stops (always), before any import of the chain's session code touches anything."""
    if "--protocol" not in argv:
        return []
    pr = argv[argv.index("--protocol") + 1]
    try:
        proto = json.load(open(pr))
    except (OSError, ValueError) as e:
        return [f"protocol unreadable: {e}"]
    bad = []
    sf = proto.get("safety") or {}
    for k, top in STOP_MAX.items():
        if k not in sf:
            bad.append(f"safety.{k} missing")
        elif float(sf[k]) > top:
            bad.append(f"safety.{k} {sf[k]} above the registered {top:g}")
    if (proto.get("tools") or {}) != WANT_TOOLS:
        bad.append(f"tools {proto.get('tools')} are not E167's (E161's) {WANT_TOOLS}")
    return bad


_bad = chain_differs()
if _bad:
    print("E167 REFUSED: the chain is not the audited one: " + "; ".join(_bad), flush=True)
    sys.exit(2)
_bad = protocol_refusals(sys.argv)
if _bad:
    print("E167 REFUSED (before any device access): " + "; ".join(_bad), flush=True)
    sys.exit(2)

sys.path.insert(0, os.path.join(HERE, "..", "kspeed"))
import run_kspeed as K  # noqa: E402
sys.path.insert(0, os.path.join(HERE, "..", "e111"))
import idle_logins_e111 as IL  # noqa: E402
sys.path.insert(0, os.path.join(HERE, "..", "e160"))
import e160_common as EC  # noqa: E402

H = K.H
for _m, _rel in ((H, os.path.join("hpl", "run_hpl.py")), (K, os.path.join("kspeed", "run_kspeed.py")),
                 (IL, os.path.join("e111", "idle_logins_e111.py")), (EC, os.path.join("e160", "e160_common.py"))):
    if os.path.realpath(_m.__file__) != os.path.realpath(os.path.join(HERE, "..", _rel)):
        print(f"E167 REFUSED: {_rel} was imported from {_m.__file__}", flush=True)
        sys.exit(2)

# The toy card's switching watts for these tiles, under --dry only: E144b's (run_e133.py's) for E80's tiles, and M8's D600 at aifoundry3's
# footing for the two pool-6 hold tiles (predictions-blind6-aifoundry2.json), so a dry session exercises the gates with plausible numbers.
DRY_C = {"file:tools/claims-v3/kinds/tiles/fp32/zeros.bin": 1.6, "file:tools/claims-v3/kinds/tiles/int8/neg_ones.bin": 2.7,
         "file:tools/claims-v3/kinds/tiles/fp16/ones.bin": 9.7,
         "file:tools/claims-v3/kinds/blind6/tiles/int8/int8.b_line_zero_ff.bin": 3.4 + 2.1,
         "file:tools/claims-v3/kinds/blind6/tiles/fp32/fp32.real_smol_softmax_v_causal.bin": 13.7 + 1.6}
NOT_SENT_WORDS = ("residency",)
_rundir = [None]

_prev_check = H.Run.check            # run_kspeed.py's (over run_hpl.py's)
_prev_verify = K.verify_tiles        # run_kspeed.py's, for E80's kinds tiles
_prev_preflight = H.Session.preflight


def _check(self):
    """E160's: the imported check, with blind pool 6's tiles allowed when they are of the run's own type and carry their b6- label."""
    if not EC.is_pool_value(self.values):
        return _prev_check(self)
    bad = []
    rel = str(self.values)[5:]
    if not rel.startswith(f"{EC.POOL_REL}/tiles/{self.type}/"):
        bad.append(f"{self.name}: a pool tile must be a tile of its run's type ({rel})")
    if "/" in self.label or not self.label.startswith(EC.LABEL_PREFIX):
        bad.append(f"{self.name}: a pool tile needs the label b6-<name> (got {self.label})")
    saved = self.values
    self.values = "zeros"           # every other check of run_hpl's, unchanged
    try:
        bad += K._base_check(self)
    finally:
        self.values = saved
    return bad


def verify_tiles(root, runs):
    """E160's: the imported verify_tiles for every other value, plus every pool tile against the manifest."""
    pool = [r for r in runs if EC.is_pool_value(r.values)]
    out, kinds_sha, kinds_rev = _prev_verify(root, [r for r in runs if not EC.is_pool_value(r.values)])
    if not pool:
        return out, kinds_sha, kinds_rev
    bad = EC.check_frozen(root)
    by_value = {EC.tile_value(t): t for t in EC.manifest(root).values()}
    for r in pool:
        t = by_value.get(str(r.values))
        if t is None:
            bad.append(f"{r.values}: not a tile of {EC.MAN_REL}")
            continue
        if t["type"] != r.type:
            bad.append(f"{r.values}: a {t['type']} tile, run {r.name} is {r.type}")
        if r.label != EC.label_of(t["name"]):
            bad.append(f"{r.name}: label {r.label}, the tile's is {EC.label_of(t['name'])}")
        why = EC.check_tile(root, t)
        if why:
            bad.append(why)
        out[str(r.values)] = {"type": t["type"], "kind": t["name"], "file": f"{EC.POOL_REL}/{t['file']}", "bytes": 2048,
                              "sha256": t["sha256"]["whole"], "sha256_a": t["sha256"]["a"], "sha256_b": t["sha256"]["b"],
                              "pool": "blind6", "priority": t.get("priority")}
    if bad:
        raise SystemExit("refused: " + "; ".join(bad))
    return out, kinds_sha, kinds_rev


def binaries_why(root):
    """E160's: [] if the wrapper, the C-logging host, E80's kernel and the sampler are the pinned bytes and the host carries the flags."""
    bad = []
    for rel, want in list(EC.CCHECK_FROZEN.items()) + [(EC.CC_HOST_REL, EC.CC_HOST_SHA256)] + list(EC.E80_SHA256.items()):
        p = os.path.join(root, rel)
        got = EC.sha256_file(p) if os.path.isfile(p) else None
        if got != want:
            bad.append(f"{rel}: sha256 {got}, registered {want}")
    p = os.path.join(root, EC.CC_HOST_REL)
    if os.path.isfile(p):
        blob = open(p, "rb").read()
        for flag in HOST_FLAGS:
            if flag not in blob:
                bad.append(f"{EC.CC_HOST_REL} has no {flag.decode()}")
    if not os.access(os.path.join(root, EC.WRAPPER_REL), os.X_OK):
        bad.append(f"{EC.WRAPPER_REL} is not executable")
    return bad


def _preflight(self):
    """E160's: run_hpl.py's preflight, its compiled-heater checks replaced by binaries_why()."""
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

# ---------------------------------------------------------------------------------------------- E167: G1Q's start gate (E167.md G1)
EXIT_GATE = 6
_prev_run_one = H.Session.run_one


def rest_anchor(rundir, window_s=120.0):
    """reduce_e161.rest_reading's reading in plain Python (no numpy on the box's path): the mean of minshire[0] and board_w over the REST
    files' last window_s s of sampler lines carrying board_w and temp_c (heat_q138t._rows' filter), sorted by time; (T, P, lines)"""
    rows = []
    for p in sorted(glob.glob(os.path.join(rundir, "tel", "REST-*.jsonl*"))):
        op = gzip.open if p.endswith(".gz") else open
        with op(p, "rt") as f:
            for line in f:
                if not line.startswith("{"):
                    continue
                try:
                    r = json.loads(line)
                except ValueError:
                    continue
                if "board_w" in r and "temp_c" in r:
                    rows.append((r["t_ms"] / 1000.0, float(r["temp_c"]["minshire"][0]), float(r["board_w"])))
    if not rows:
        return None, None, 0
    rows.sort(key=lambda x: x[0])
    t_last = rows[-1][0]
    sel = [x for x in rows if x[0] - t_last >= -window_s]
    return sum(x[1] for x in sel) / len(sel), sum(x[2] for x in sel) / len(sel), len(sel)


def _run_one(self, r, k, n):
    """E167: before the gated block's run (G1Q's HOLD), its REST anchor must read at or under the gate's line"""
    g = self.proto.get("e167_gate")
    if g and r.block == g["block"]:
        line = float(g["rest_anchor_max_c"])
        dry_line = os.environ.get("E167_DRY_GATE_C")
        if dry_line:
            if not self.dry:
                raise H.EndSession("error:E167_DRY_GATE_C is for --dry only", H.EXIT_REFUSE)
            line = float(dry_line)
        T, Pw, nl = rest_anchor(self.rundir, float(g["window_s"]))
        ok = T is not None and nl >= int(g["min_lines"]) and T <= line
        self.mark("e167_gate", json.dumps({"rest_anchor_C": T, "rest_board_W": Pw, "lines": nl, "line_C": line, "passed": ok,
                                           "dry_line": bool(dry_line)}))
        self.say(f"    E167 G1Q start gate: REST anchor {T if T is None else round(T, 3)} C from {nl} lines, line {line:g} C: "
                 f"{'passed' if ok else 'NOT passed'}")
        if not ok:
            raise H.EndSession(f"gate:G1Q's REST anchor {T if T is None else round(T, 3)} C from {nl} lines (at most {line:g} C, at least "
                               f"{g['min_lines']} lines): no work process", EXIT_GATE)
    return _prev_run_one(self, r, k, n)


H.Session.run_one = _run_one


def is_not_sent(cmd):
    """True for the one command E167 never sends: any `ettelem residency ...` (a word of the argv, not a substring)."""
    return any(str(w) in NOT_SENT_WORDS for w in cmd)


def patch_no_residency(module):
    """E144b's: wrap module.run_out so that a residency command is answered at once, unsent; every other command is the original call."""
    orig = module.run_out
    if getattr(orig, "_e167", False):
        return

    def run_out(cmd, *a, **kw):
        if is_not_sent(cmd):
            if _rundir[0]:
                try:
                    with open(os.path.join(_rundir[0], "e167-not-sent.jsonl"), "a") as f:
                        f.write(json.dumps({"t_ms": int(time.time() * 1000), "argv": [os.path.basename(str(cmd[2])) if len(cmd) > 2 else ""]
                                            + [str(w) for w in cmd[3:]], "why": "E167 (E133's rule): no residency read (raw 4-6 log SP errors)"}) + "\n")
                except OSError:
                    pass
            return None, b"", b"E167: not sent"
        return orig(cmd, *a, **kw)

    run_out._e167 = True
    module.run_out = run_out


def main():
    dry = "--dry" in sys.argv
    if os.environ.get("E167_DRY_GATE_C") and not dry:
        print("E167 REFUSED: E167_DRY_GATE_C is for --dry only", flush=True)
        return 2
    if not dry:
        IL.patch(H, as_bytes=True)      # E111's A1/A3: a login idle >= 120 min (no process newer than 120 min) does not block
    patch_no_residency(H)               # E133's: the residency read is never sent (dry runs send nothing anyway)
    if dry:
        for v, c in DRY_C.items():
            H.DryCard.DYN600[v] = c
    if "--list" not in sys.argv:
        bad = EC.check_frozen(ROOT)
        if bad:
            print("E167 REFUSED: " + "; ".join(bad), flush=True)
            return 2
        if not dry:
            why = binaries_why(ROOT)
            if why:
                print("E167 REFUSED (before any device access): " + "; ".join(why), flush=True)
                return 2
    if "--out" in sys.argv and "--list" not in sys.argv:
        rd = os.path.abspath(sys.argv[sys.argv.index("--out") + 1])
        _rundir[0] = rd
        os.makedirs(rd, exist_ok=True)
        os.environ["CCHECK_LOG"] = os.path.join(rd, "c-log.jsonl")
        os.environ["CCHECK_KERNEL"] = os.path.join(ROOT, EC.KERNEL_REL)
        os.environ["CCHECK_HOST"] = os.path.join(ROOT, EC.CC_HOST_REL)
        if not os.path.exists(os.path.join(rd, "session.json")) and not os.path.exists(os.path.join(rd, "e167.json")):
            pr = sys.argv[sys.argv.index("--protocol") + 1]
            bins = {}
            for rel in [EC.WRAPPER_REL, EC.CC_HOST_REL] + list(EC.E80_SHA256):
                try:
                    bins[rel] = sha256(os.path.join(ROOT, rel))
                except OSError:
                    bins[rel] = None
            json.dump({"experiment": "E167", "request": "Q141(h)", "wrapper": "tools/claims-v3/e167/run_e167.py", "wrapper_sha256": sha256(__file__),
                       "protocol": os.path.basename(pr), "protocol_sha256": sha256(pr), "e167_gate": json.load(open(pr)).get("e167_gate"),
                       "run_kspeed_sha256": sha256(K.__file__), "run_hpl_sha256": sha256(H.__file__),
                       "idle_logins_sha256": sha256(IL.__file__), "e160_common_sha256": sha256(EC.__file__), "binaries_sha256": bins,
                       "frozen_inputs": {**EC.FROZEN, **EC.CCHECK_FROZEN}, "not_sent": list(NOT_SENT_WORDS), "dry": dry,
                       "ccheck_env": {k: os.environ[k] for k in ("CCHECK_LOG", "CCHECK_KERNEL", "CCHECK_HOST")},
                       "t_ms": int(time.time() * 1000), "zone": time.strftime("%Z"), "argv": sys.argv},
                      open(os.path.join(rd, "e167.json"), "w"), indent=1)
    return K.main()


if __name__ == "__main__":
    sys.exit(main())
