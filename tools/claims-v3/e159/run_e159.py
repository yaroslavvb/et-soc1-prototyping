#!/usr/bin/env python3
"""E159 (Q139): the session runner. It is E158's run_e158.py with E159's names: E119's run_e119.py, imported and run unchanged (E105's run_e105.py with its
admission rule, E101 session 2's run_e101s.py, E80's run_kspeed.py, E64's run_hpl.py; E111's idle-login rule; the residency query E119 sends, which this
ettelem build refuses at its argument check before it opens the device), after E146's preflight, unchanged, and E158's two refusals, unchanged:

  PREFLIGHT (E146's, imported): before anything opens the card, the three device programs must be byte-identical to E136's registered build (the heater
  build/e136/host/sparsity_host and its kernel build/e136/kernel/sparsity.elf, rgm136, built on aifoundry2 at 15:37 PST on 2 Nov 2026; E159's three
  shapes are its arguments, gemmL<MB>x<NB>x<KB>; the sampler build/ettelem-hpl/ettelem). E159.md classifies every device-management command they send;
  a different binary could send something else, so a mismatch refuses the session (exit 2) before the card lock is taken. Under --dry it is skipped.
  THE STOPS (Q139's rule for aifoundry2, Tue 3 Nov 2026: "every registered board stop is at most 85 W on live samples"): a protocol whose safety block
  lacks abs_stop_c, board_cap_w or cap_consecutive, whose board_cap_w is above 85 W, or whose admission limit limit_p800_w is above 82 W ("no tile,
  shape or hold whose predicted peak board power exceeds 82 W runs as designed") is refused (exit 2), under --dry too.

Everything that touches the card -- the card lock held for the session, the other-user checks before every launch process, `timeout 10` on every launch
and config read, the sampler WITHOUT --reset-ms, the trace ring and `ettelem config` after every run, the safety stops under the keys run_hpl.py's
watcher reads, the end of the session unless the TDP and the threshold read back 65, and the admission rule -- is the imported code. Nothing is set on
the card.

The design and the predictions are Q139(q)'s, frozen at 91def7c4 (docs/reports/data/2026-11-03-q139q-gemm-g3/predictions-e159.json); the protocol is
written from them by make_protocol_e159.py. The runner records the protocol's sha256 and that file's registered sha256 in e159.json.

    python3 run_e159.py --protocol protocol.json --out <RUNDIR> [--dry] [--only BLOCK ...] [--max-card-min N] [--list]
"""
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, "..", "..", ".."))
sys.path.insert(0, os.path.join(HERE, "..", "e146"))
import run_e146 as R146  # noqa: E402  (E146's runner: its preflight, E136's registered sha256, and run_e119 as R146.R119)

MAX_BOARD_STOP_W = 85.0
MAX_LIMIT_W = 82.0
PREDICTIONS = "docs/reports/data/2026-11-03-q139q-gemm-g3/predictions-e159.json"
PREDICTIONS_SHA256 = "497497cb1d2b1eb669a6c551895981ac4e997327fdd428017d3becb633b81255"   # frozen-sha256.json at 91def7c4


def stops_ok(proto):
    """None if the protocol's stops and admission limit are inside the brief's, else why not (selftest_e159.py runs it)"""
    sf = proto.get("safety", {})
    bad = [f"protocol safety lacks {k}" for k in ("abs_stop_c", "board_cap_w", "cap_consecutive") if k not in sf]
    if "board_cap_w" in sf and float(sf["board_cap_w"]) > MAX_BOARD_STOP_W:
        bad.append(f"board_cap_w {sf['board_cap_w']} W is above {MAX_BOARD_STOP_W:g} W")
    lim = proto.get("limit_p800_w")
    if lim is None or float(lim) > MAX_LIMIT_W:
        bad.append(f"limit_p800_w {lim} is missing or above {MAX_LIMIT_W:g} W")
    return "; ".join(bad) if bad else None


def main():
    pr = sys.argv[sys.argv.index("--protocol") + 1]
    proto = json.load(open(pr))
    dry = "--dry" in sys.argv
    root = ROOT
    if "--root" in sys.argv:
        root = os.path.abspath(sys.argv[sys.argv.index("--root") + 1])
    if "--list" not in sys.argv:
        why = stops_ok(proto)
        if why is not None:
            print(f"refused: {why}", file=sys.stderr)
            return 2
    got = {}
    if not dry and "--list" not in sys.argv:
        why = R146.preflight(proto, root)
        if why is not None:
            print(f"refused: {why}", file=sys.stderr)
            return 2
        got = dict(R146.E136_SHA256)
    if "--out" in sys.argv and "--list" not in sys.argv:
        rd = os.path.abspath(sys.argv[sys.argv.index("--out") + 1])
        os.makedirs(rd, exist_ok=True)
        if not os.path.exists(os.path.join(rd, "e159.json")):
            pp = os.path.join(root, PREDICTIONS)
            json.dump({"experiment": "E159", "request": "Q139", "wrapper": "tools/claims-v3/e159/run_e159.py", "wrapper_sha256": R146.sha256(__file__),
                       "run_e146_sha256": R146.sha256(R146.__file__), "run_e119_sha256": R146.sha256(R146.R119.__file__), "protocol": os.path.basename(pr),
                       "protocol_sha256": R146.sha256(pr), "predictions": PREDICTIONS, "predictions_sha256_registered": PREDICTIONS_SHA256,
                       "predictions_sha256_here": R146.sha256(pp) if os.path.isfile(pp) else None, "binaries_checked": got, "dry": dry,
                       "safety": proto.get("safety"), "limit_p800_w": proto.get("limit_p800_w"), "peak_lock_w": proto.get("peak_lock_w"),
                       "t_ms": int(time.time() * 1000), "zone": time.strftime("%Z"), "argv": sys.argv}, open(os.path.join(rd, "e159.json"), "w"), indent=1)
    return R146.R119.main()


if __name__ == "__main__":
    sys.exit(main())
