#!/usr/bin/env python3
"""E126 (Q136): the session runner. It IS E119's run_e119.py, imported and run unchanged (E105's run_e105.py with its admission rule, E101 session 2's
run_e101s.py, E80's run_kspeed.py, E64's run_hpl.py; E111's idle-login rule; the residency query E119 sends, which this ettelem build refuses at its
argument check before it opens the device), with one addition and nothing else:

  PREFLIGHT (Q136's rule, "take more care for writing commands"): before anything opens the card, the three device programs must be byte-identical to
  the ones E119 ran on this card (E119's s1/session.json sha256): the heater build/e119/host/sparsity_host, its kernel build/e119/kernel/sparsity.elf
  and the sampler build/ettelem-hpl/ettelem. E126.md classifies every device-management command these programs send from the firmware source and from
  ettelem-dv2's source, which built that ettelem; a different binary could send something else, so a mismatch refuses the session (exit 2) before the
  card lock is taken. Under --dry no device is touched and the check is skipped.

Everything that touches the card -- the card lock held for the session, the other-user checks before every launch process, `timeout 10` on every launch
and config read, the sampler WITHOUT --reset-ms, the trace ring and `ettelem config` after every run, the safety stops (protocol.json: 80 C on one
sample; 93 W on three), the end of the session unless the TDP and the threshold read back 65, and the admission rule (88 W at the estimate; the 93 W
lock) -- is the imported code. Nothing is set on the card.

    python3 run_e126.py --protocol protocol.json --out <RUNDIR> [--dry] [--only BLOCK ...] [--max-card-min N] [--list]
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

E119_SHA256 = {  # docs/reports/data/2026-11-01-e119-gemm-speed/aifoundry2/s1/session.json "sha256"
    "build/e119/host/sparsity_host": "4c6253fbbfcf9c9f43354b3900d79221454f1f3163ae60d44e6b6842851a06ef",
    "build/e119/kernel/sparsity.elf": "27cb001959871fa8c5ef9bf8570cd61add15fb0b8b817ce12a71ed3a7841e318",
    "build/ettelem-hpl/ettelem": "77a46171c915d3a92898af9ffe04d92b86b65f4d36bc29d58f5c086f8accfeb5",
}


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def preflight(proto, root):
    """None if the protocol's three tools are E119's binaries, else why not (a plain function: selftest_e126.py runs it)."""
    tools = proto.get("tools", {})
    want = {"heater": "build/e119/host/sparsity_host", "kernel": "build/e119/kernel/sparsity.elf", "ettelem": "build/ettelem-hpl/ettelem"}
    bad = []
    for k, rel in want.items():
        if tools.get(k) != rel:
            bad.append(f"protocol tools.{k} is {tools.get(k)!r}, not {rel!r}")
            continue
        p = os.path.join(root, rel)
        got = sha256(p) if os.path.isfile(p) else None
        if got != E119_SHA256[rel]:
            bad.append(f"{rel}: sha256 {got}, E119's {E119_SHA256[rel]}")
    return "; ".join(bad) if bad else None


def main():
    pr = sys.argv[sys.argv.index("--protocol") + 1]
    proto = json.load(open(pr))
    dry = "--dry" in sys.argv
    root = ROOT
    if "--root" in sys.argv:
        root = os.path.abspath(sys.argv[sys.argv.index("--root") + 1])
    got = {}
    if not dry and "--list" not in sys.argv:
        why = preflight(proto, root)
        if why is not None:
            print(f"refused: {why}", file=sys.stderr)
            return 2
        got = {rel: E119_SHA256[rel] for rel in E119_SHA256}
    if "--out" in sys.argv and "--list" not in sys.argv:
        rd = os.path.abspath(sys.argv[sys.argv.index("--out") + 1])
        os.makedirs(rd, exist_ok=True)
        if not os.path.exists(os.path.join(rd, "e126.json")):
            json.dump({"experiment": "E126", "request": "Q136", "wrapper": "tools/claims-v3/e126/run_e126.py", "wrapper_sha256": sha256(__file__),
                       "run_e119_sha256": sha256(R119.__file__), "protocol": os.path.basename(pr), "protocol_sha256": sha256(pr),
                       "predictions_sha256": sha256(os.path.join(HERE, "predictions-e126.json")), "binaries_checked": got, "dry": dry,
                       "t_ms": int(time.time() * 1000), "zone": time.strftime("%Z"), "argv": sys.argv}, open(os.path.join(rd, "e126.json"), "w"), indent=1)
    return R119.main()


if __name__ == "__main__":
    sys.exit(main())
