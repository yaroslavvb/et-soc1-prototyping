#!/usr/bin/env python3
"""E144b (Q138): one step's session of the queue (SMOKE, STOPTEST-DIE, STOPTEST-BOARD, G1, END, G2, END2). It IS E133's runner,
tools/claims-v3/e133/run_e133.py, with E144b's names: E111's chain (E80's ../kspeed/run_kspeed.py over E64's ../hpl/run_hpl.py, `file:`
tiles checked against kinds.json), imported and run unchanged, with E111's idle-login rule (../e111/idle_logins_e111.py: the owner's
ruling of 1 November 2026), E133's one change, which removes a command and adds none, and two refusals added before any device access:

  NO RESIDENCY READ (E133's). run_hpl.py reads `ettelem residency 2 3 4 5 6` after every run (hpl/run_hpl.py:622). On this card's
  BL2 0.22.0 raw states 4-6 are no state: each read logs two ERROR lines and SP_RUNTIME_ERROR events (Q136(w), result 5). Here that one
  command is NOT SENT: the wrapped run_out returns at once with rc null and no output, starts no process and opens no device, and appends
  one line to <RUNDIR>/e144b-not-sent.jsonl. No reducer reads residencies.

  THE AUDITED CHAIN (E133's amendment A1). Before the runner is imported and before any device access, the three files it runs are
  hashed; any other copy refuses with exit 2 (the queue halts). No command is sent.

  THE BINARIES (E143's preflight, added here). Before anything opens the card, the three device programs must be byte-identical to E80's
  (heater build/sparsity_t2/host/sparsity_host, kernel build/sparsity_t2/kernel/sparsity.elf, sampler build/ettelem-hpl/ettelem; the
  binaries E133 and E143 ran). E144b.md classifies every device-management command they send; a different binary could send something
  else, so a mismatch refuses the session (exit 2). Under --dry no device is touched and the binary check is skipped.

  THE STOPS (added here). A protocol whose safety block lacks abs_stop_c, board_cap_w or cap_consecutive, or sets abs_stop_c above 72 C,
  board_cap_w above 93 W or cap_consecutive above 3 (Q138(t)'s frozen aifoundry2 stops), is refused (exit 2). The stop tests lower one.

Everything that touches the card -- the card lock held for the session, the other-user checks before every launch process, `timeout 10`
on every launch and config read, the sampler WITHOUT --reset-ms, the trace ring and `ettelem config` after every run, the safety watcher
(it reads every live sampler line: the die mean or the hottest sensor >= abs_stop_c on one line, or board_w > board_cap_w on
cap_consecutive lines, touches the stop-file and ends the session with exit 4), and the end of the session unless the TDP and the
threshold read back 65 -- is run_hpl.py's own code. Nothing is set on the card.

Before the session it writes <RUNDIR>/e144b.json: this wrapper's sha256, the protocol's, run_kspeed.py's, run_hpl.py's and
idle_logins_e111.py's, the binaries', and the zone the box's clock is in (every time in E144b is epoch ms).

    python3 run_e144b.py --protocol protocol-g1.json --out <RUNDIR> [--dry] [--max-card-min N] [--list]
"""
import hashlib
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, "..", "..", ".."))

AUDITED = {os.path.join("hpl", "run_hpl.py"): "68493295504fba5d4e9056b4f7e7387179d555e4157bbae32075b4197f3df227",
           os.path.join("kspeed", "run_kspeed.py"): "d3d844c7912d873fb1fe80c92dd72124d2714e493bcf4f73a961cfa26d894c0c",
           os.path.join("e111", "idle_logins_e111.py"): "91094be5f9af14c0897a817b7d95777fdaaa6ab12b49304883ccb3d066574ef4"}
E80_SHA256 = {  # E80's binaries (docs/reports/data/2026-10-31-e80-kinds-speed/s1/session.json), the ones E133 and E143 ran on this card
    "build/sparsity_t2/host/sparsity_host": "7adadf4f1ce331cc028c317561933d6d3209da0f0326b0ce9a124b39b15ac0d2",
    "build/sparsity_t2/kernel/sparsity.elf": "990807f483cd57aa413083c52e647079b86022768562d5810080852f7fd6ea24",
    "build/ettelem-hpl/ettelem": "77a46171c915d3a92898af9ffe04d92b86b65f4d36bc29d58f5c086f8accfeb5",
}
WANT_TOOLS = {"heater": "build/sparsity_t2/host/sparsity_host", "kernel": "build/sparsity_t2/kernel/sparsity.elf",
              "ettelem": "build/ettelem-hpl/ettelem"}
STOP_MAX = {"abs_stop_c": 72.0, "board_cap_w": 93.0, "cap_consecutive": 3}


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
    """the binaries (real runs only) and the stops (always), before any import of the chain's session code touches anything."""
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
        bad.append(f"tools {proto.get('tools')} are not E80's {WANT_TOOLS}")
    if "--dry" not in argv and "--list" not in argv:
        for rel, want in E80_SHA256.items():
            try:
                got = sha256(os.path.join(ROOT, rel))
            except OSError as e:
                got = f"unreadable: {e}"
            if got != want:
                bad.append(f"{rel}: {got[:16]} (E80's {want[:16]})")
    return bad


_bad = chain_differs()
if _bad:
    print("E144b REFUSED: the chain is not the audited one: " + "; ".join(_bad), flush=True)
    sys.exit(2)
_bad = protocol_refusals(sys.argv)
if _bad:
    print("E144b REFUSED (before any device access): " + "; ".join(_bad), flush=True)
    sys.exit(2)

sys.path.insert(0, os.path.join(HERE, "..", "kspeed"))
import run_kspeed as K  # noqa: E402
sys.path.insert(0, os.path.join(HERE, "..", "e111"))
import idle_logins_e111 as IL  # noqa: E402

H = K.H
for _m, _rel in ((H, os.path.join("hpl", "run_hpl.py")), (K, os.path.join("kspeed", "run_kspeed.py")),
                 (IL, os.path.join("e111", "idle_logins_e111.py"))):
    if os.path.realpath(_m.__file__) != os.path.realpath(os.path.join(HERE, "..", _rel)):
        print(f"E144b REFUSED: {_rel} was imported from {_m.__file__}", flush=True)
        sys.exit(2)
# The toy card's switching watts for these tiles, under --dry only (run_e133.py's DRY_C, unchanged).
DRY_C = {"fp32/zeros": 1.6, "fp16/zeros": 1.4, "int8/zeros": 2.1, "int8/neg_ones": 2.7, "int8/sparse50": 8.1, "fp16/ones": 9.7,
         "int8/full": 9.1, "fp32/randn": 25.2}
NOT_SENT_WORDS = ("residency",)
_rundir = [None]


def is_not_sent(cmd):
    """True for the one command E144b never sends: any `ettelem residency ...` (a word of the argv, not a substring)."""
    return any(str(w) in NOT_SENT_WORDS for w in cmd)


def patch_no_residency(module):
    """Wrap module.run_out so that a residency command is answered at once, unsent; every other command is the original call."""
    orig = module.run_out
    if getattr(orig, "_e144b", False):
        return

    def run_out(cmd, *a, **kw):
        if is_not_sent(cmd):
            if _rundir[0]:
                try:
                    with open(os.path.join(_rundir[0], "e144b-not-sent.jsonl"), "a") as f:
                        f.write(json.dumps({"t_ms": int(time.time() * 1000), "argv": [os.path.basename(str(cmd[2])) if len(cmd) > 2 else ""]
                                            + [str(w) for w in cmd[3:]], "why": "E144b (E133's rule): no residency read (raw 4-6 log SP errors)"}) + "\n")
                except OSError:
                    pass
            return None, b"", b"E144b: not sent"
        return orig(cmd, *a, **kw)

    run_out._e144b = True
    module.run_out = run_out


def main():
    if "--dry" not in sys.argv:
        IL.patch(H, as_bytes=True)      # E111's A1/A3: a login idle >= 120 min (no process newer than 120 min) does not block
    patch_no_residency(H)               # E133's: the residency read is never sent (dry runs send nothing anyway)
    if "--dry" in sys.argv:
        for k, c in DRY_C.items():
            t, v = k.split("/")
            H.DryCard.DYN600[f"file:tools/claims-v3/kinds/tiles/{t}/{v}.bin"] = c
    if "--out" in sys.argv and "--list" not in sys.argv:
        rd = os.path.abspath(sys.argv[sys.argv.index("--out") + 1])
        _rundir[0] = rd
        if not os.path.exists(os.path.join(rd, "session.json")):
            os.makedirs(rd, exist_ok=True)
            pr = sys.argv[sys.argv.index("--protocol") + 1]
            bins = {}
            for rel in E80_SHA256:
                try:
                    bins[rel] = sha256(os.path.join(ROOT, rel))
                except OSError:
                    bins[rel] = None
            json.dump({"experiment": "E144b", "request": "Q138", "wrapper": "tools/claims-v3/e144b/run_e144b.py", "wrapper_sha256": sha256(__file__),
                       "protocol": os.path.basename(pr), "protocol_sha256": sha256(pr),
                       "run_kspeed_sha256": sha256(K.__file__), "run_hpl_sha256": sha256(H.__file__),
                       "idle_logins_sha256": sha256(IL.__file__), "binaries_sha256": bins, "not_sent": list(NOT_SENT_WORDS),
                       "t_ms": int(time.time() * 1000), "zone": time.strftime("%Z"), "argv": sys.argv},
                      open(os.path.join(rd, "e144b.json"), "w"), indent=1)
    return K.main()


if __name__ == "__main__":
    sys.exit(main())
