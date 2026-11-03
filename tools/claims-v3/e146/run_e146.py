#!/usr/bin/env python3
"""E146 (Q138): the session runner. It is E136's run_e136.py with E146's names: E119's run_e119.py, imported and run unchanged (E105's run_e105.py with its
admission rule, E101 session 2's run_e101s.py, E80's run_kspeed.py, E64's run_hpl.py; E111's idle-login rule; the residency query E119 sends, which this
ettelem build refuses at its argument check before it opens the device), after the same preflight and nothing else:

  PREFLIGHT (Q136's rule, "take more care for writing commands", kept in Q138): before anything opens the card, the three device programs must be
  byte-identical to the ones E136.md registered and E146.md registers again: the heater build/e136/host/sparsity_host and its kernel
  build/e136/kernel/sparsity.elf (rgm136, built on aifoundry2 at 15:37 PST on 2 Nov 2026; E146's shapes are its arguments, gemmL<MB>x<NB>x<KB>, so no
  new binary) and the sampler build/ettelem-hpl/ettelem (E119's, E126's and E136's). E146.md classifies every device-management command these programs
  send; a different binary could send something else, so a mismatch refuses the session (exit 2) before the card lock is taken. Under --dry no device
  is touched and the check is skipped.

Everything that touches the card -- the card lock held for the session, the other-user checks before every launch process, `timeout 10` on every launch
and config read, the sampler WITHOUT --reset-ms, the trace ring and `ettelem config` after every run, the safety stops (protocol.json safety, under the
keys run_hpl.py's watcher reads: abs_stop_c 80 C on one sample, board_cap_w 93 W on cap_consecutive 3), the end of the session unless the TDP and the
threshold read back 65, and the admission rule (88 W at the estimate; the 93 W lock) -- is the imported code. Nothing is set on the card. A protocol
whose safety block lacks those three keys is refused here (exit 2): E136's named its stops under keys the watcher does not read.

    python3 run_e146.py --protocol protocol.json --out <RUNDIR> [--dry] [--only BLOCK ...] [--max-card-min N] [--list]
"""
import hashlib
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(HERE, "..", "e119"))
import run_e119 as R119  # noqa: E402

E136_SHA256 = {  # E136's registered binaries (tools/claims-v3/e136/logs/build.txt; run_e136.py), unchanged; the sampler is E119's, E126's and E136's
    "build/e136/host/sparsity_host": "76475508f8e88983edfe16bcc8757dd23094877a31c78c302f6003993ee5fe74",
    "build/e136/kernel/sparsity.elf": "aace138caf8071cc7679134211045a89fb09b65cc9a170bfe33409fd36b4fda0",
    "build/ettelem-hpl/ettelem": "77a46171c915d3a92898af9ffe04d92b86b65f4d36bc29d58f5c086f8accfeb5",
}


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def preflight(proto, root):
    """None if the protocol's three tools are E136's registered binaries and its safety block names the watcher's keys, else why not (selftest_e146.py runs it)."""
    tools = proto.get("tools", {})
    sf = proto.get("safety", {})
    bad = [f"protocol safety lacks {k}" for k in ("abs_stop_c", "board_cap_w", "cap_consecutive") if k not in sf]
    want = {"heater": "build/e136/host/sparsity_host", "kernel": "build/e136/kernel/sparsity.elf", "ettelem": "build/ettelem-hpl/ettelem"}
    for k, rel in want.items():
        if tools.get(k) != rel:
            bad.append(f"protocol tools.{k} is {tools.get(k)!r}, not {rel!r}")
            continue
        p = os.path.join(root, rel)
        got = sha256(p) if os.path.isfile(p) else None
        if got != E136_SHA256[rel]:
            bad.append(f"{rel}: sha256 {got}, registered {E136_SHA256[rel]}")
    return "; ".join(bad) if bad else None


def main():
    pr = sys.argv[sys.argv.index("--protocol") + 1]
    proto = json.load(open(pr))
    dry = "--dry" in sys.argv
    root = ROOT
    if "--root" in sys.argv:
        root = os.path.abspath(sys.argv[sys.argv.index("--root") + 1])
    got = {}
    miss = [k for k in ("abs_stop_c", "board_cap_w", "cap_consecutive") if k not in proto.get("safety", {})]
    if miss and "--list" not in sys.argv:          # under --dry too: a stop the watcher cannot read is no stop
        print(f"refused: protocol safety lacks {', '.join(miss)}", file=sys.stderr)
        return 2
    if not dry and "--list" not in sys.argv:
        why = preflight(proto, root)
        if why is not None:
            print(f"refused: {why}", file=sys.stderr)
            return 2
        got = {rel: E136_SHA256[rel] for rel in E136_SHA256}
    if "--out" in sys.argv and "--list" not in sys.argv:
        rd = os.path.abspath(sys.argv[sys.argv.index("--out") + 1])
        os.makedirs(rd, exist_ok=True)
        if not os.path.exists(os.path.join(rd, "e146.json")):
            json.dump({"experiment": "E146", "request": "Q138", "wrapper": "tools/claims-v3/e146/run_e146.py", "wrapper_sha256": sha256(__file__),
                       "run_e119_sha256": sha256(R119.__file__), "protocol": os.path.basename(pr), "protocol_sha256": sha256(pr),
                       "predictions_sha256": sha256(os.path.join(HERE, "predictions-e146.json")), "binaries_checked": got, "dry": dry, "safety": proto.get("safety"),
                       "t_ms": int(time.time() * 1000), "zone": time.strftime("%Z"), "argv": sys.argv}, open(os.path.join(rd, "e146.json"), "w"), indent=1)
    return R119.main()


if __name__ == "__main__":
    sys.exit(main())
