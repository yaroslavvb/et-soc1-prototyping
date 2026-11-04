#!/usr/bin/env python3
"""E169 (Q141(s)): the session runner. It is E158's run_e158.py with E169's names: E119's run_e119.py, imported and run unchanged (E105's run_e105.py with
its admission rule, E101 session 2's run_e101s.py, E80's run_kspeed.py, E64's run_hpl.py; E111's idle-login rule; the residency query E119 sends, which
this ettelem build refuses at its argument check before it opens the device), after E146's preflight, unchanged, and E158's two refusals with one more:

  PREFLIGHT (E146's, imported): before anything opens the card, the three device programs must be byte-identical to E136's registered build (the heater
  build/e136/host/sparsity_host and its kernel build/e136/kernel/sparsity.elf, rgm136, built on aifoundry2 at 15:37 PST on 2 Nov 2026; E169's shapes
  are its arguments, gemmL<MB>x<NB>x<KB>; the sampler build/ettelem-hpl/ettelem). The kit's README classifies every device-management command they send;
  a different binary could send something else, so a mismatch refuses the session (exit 2) before the card lock is taken. Under --dry it is skipped.
  THE STOPS (E158's refusals, and this round's die bound for aifoundry2, REGISTRATION-A2.md D7): a protocol whose safety block lacks abs_stop_c,
  board_cap_w or cap_consecutive, whose board_cap_w is above 85 W, whose abs_stop_c is above 76 C, or whose admission limit limit_p800_w is above 82 W
  is refused (exit 2), under --dry too. The stop-path tests lower one stop each (30 W, 30 C), which these bounds allow.

Everything that touches the card -- the card lock held for the session, the other-user checks before every launch process, `timeout 10` on every launch
and config read, the sampler WITHOUT --reset-ms, the trace ring and `ettelem config` after every run, the safety stops under the keys run_hpl.py's
watcher reads, the end of the session unless the TDP and the threshold read back 65, and the admission rule -- is the imported code. Nothing is set on
the card.

The design and the step rule are REGISTRATION-A2.md's (217c94a2), over Q140(q)'s frozen predictions (e39d06da); the protocol is written from them by
make_protocol_e169.py. The runner records the protocol's sha256 and the frozen files' registered and present sha256 in e169.json.

    python3 run_e169.py --protocol protocol.json --out <RUNDIR> [--dry] [--only BLOCK ...] [--max-card-min N] [--list]
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
MAX_DIE_STOP_C = 76.0
MAX_LIMIT_W = 82.0
FROZEN = {"docs/reports/data/2026-11-04-q140q-gemm-g4-stride/predictions-e169.json": "38ee500fa1e66107ef5c544688263b1e988fb5a675bdee05f9876df1432cf19f",
          "tools/claims-v3/e169/step-rule-e169.json": "e76aa66b3911b681dc3b4056153efc6043f3f1b44a508700f378c159aef0e86f",
          "tools/claims-v3/e169/kit-e169.json": "28ef79aa7eb30c4e435ea564464057d5971dba0f9d5da6d52d90ffd8dccf98f0"}


def stops_ok(proto):
    """None if the protocol's stops and admission limit are inside the bounds, else why not (selftest_kit_e169.py runs it)"""
    sf = proto.get("safety", {})
    bad = [f"protocol safety lacks {k}" for k in ("abs_stop_c", "board_cap_w", "cap_consecutive") if k not in sf]
    if "board_cap_w" in sf and float(sf["board_cap_w"]) > MAX_BOARD_STOP_W:
        bad.append(f"board_cap_w {sf['board_cap_w']} W is above {MAX_BOARD_STOP_W:g} W")
    if "abs_stop_c" in sf and float(sf["abs_stop_c"]) > MAX_DIE_STOP_C:
        bad.append(f"abs_stop_c {sf['abs_stop_c']} C is above {MAX_DIE_STOP_C:g} C")
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
        if not os.path.exists(os.path.join(rd, "e169.json")):
            here = {rel: (R146.sha256(os.path.join(root, rel)) if os.path.isfile(os.path.join(root, rel)) else None) for rel in FROZEN}
            json.dump({"experiment": "E169", "request": "Q141(s)", "wrapper": "tools/claims-v3/e169/run_e169.py", "wrapper_sha256": R146.sha256(__file__),
                       "run_e146_sha256": R146.sha256(R146.__file__), "run_e119_sha256": R146.sha256(R146.R119.__file__), "protocol": os.path.basename(pr),
                       "protocol_sha256": R146.sha256(pr), "frozen_sha256_registered": FROZEN, "frozen_sha256_here": here,
                       "frozen_match": all(here[k] == v for k, v in FROZEN.items()), "binaries_checked": got, "dry": dry,
                       "safety": proto.get("safety"), "limit_p800_w": proto.get("limit_p800_w"), "peak_lock_w": proto.get("peak_lock_w"),
                       "t_ms": int(time.time() * 1000), "zone": time.strftime("%Z"), "argv": sys.argv}, open(os.path.join(rd, "e169.json"), "w"), indent=1)
    return R146.R119.main()


if __name__ == "__main__":
    sys.exit(main())
