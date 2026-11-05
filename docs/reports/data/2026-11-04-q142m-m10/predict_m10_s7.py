#!/usr/bin/env python3
"""Q142(m), dated amendment A2: M10's predictor with REGISTRATION.md section 7 applied. predict_m10.py and m10.json stay as
committed; this file reads them and m10-s7.json (written by section7_m10.py). Every function is predict_m10's, except the factor
on Q138(t)'s chain: M10's primary uses the factor in m10-s7.json (1, the chain unscaled, when section 7 keeps term d out), and
m10.json's 1 + gamma (predict_m10.chain_gain) is a reported arm only.

    python3 -B predict_m10_s7.py selftest [<m10-s7.json>]   # the hashes, the two factors, and predict_m10's own self-test
                                                            # (power, unchanged); the default m10-s7.json is this directory's

As a module: everything predict_m10 offers, plus
  load_s7(path=None)                 m10-s7.json
  chain_gain_primary(s7)             the factor on Q138(t)'s chain for M10's primary prediction
  chain_gain_arm(m10, s7)            the reported arm's factor (m10.json's 1 + gamma), or None when there is no arm
SPDX-License-Identifier: Apache-2.0
"""
import hashlib
import json
import os
import sys

sys.dont_write_bytecode = True
HERE = os.path.dirname(os.path.abspath(__file__))
if HERE not in sys.path:
    sys.path.insert(0, HERE)
import predict_m10 as P  # noqa: E402  (unchanged)
from predict_m10 import d600, load_m10, rise_4p5s, rise_card0_burst, session_scale  # noqa: E402,F401


def load_s7(path=None):
    return json.load(open(path or os.path.join(HERE, "m10-s7.json")))


def chain_gain_primary(s7):
    return float(s7["heat_chain_factor_primary"])


def chain_gain_arm(m10, s7):
    return P.chain_gain(m10) if s7.get("heat_chain_gain_reported_arm") else None


def selftest(s7_path=None):
    m10, s7 = load_m10(), load_s7(s7_path)
    sha = hashlib.sha256(open(os.path.join(HERE, "m10.json"), "rb").read()).hexdigest()
    listed = {ln.split(None, 1)[1].strip(): ln.split(None, 1)[0] for ln in open(os.path.join(HERE, "SHA256SUMS")) if ln.strip()}
    checks = {"m10_json_as_committed": sha == listed.get("m10.json"), "m10_s7_names_this_m10_json": sha == s7["m10_json_sha256"],
              "primary_factor": chain_gain_primary(s7), "arm_factor": chain_gain_arm(m10, s7),
              "primary_is_the_chain_unscaled": chain_gain_primary(s7) == 1.0 and not s7["entered_primary"].get("d"),
              "arm_is_m10_json_gain": chain_gain_arm(m10, s7) == P.chain_gain(m10)}
    print(json.dumps({"checks": checks}), flush=True)
    rc = P.selftest()
    ok = rc == 0 and all(v for k, v in checks.items() if k not in ("primary_factor", "arm_factor"))
    print(json.dumps({"selftest_s7": "PASS" if ok else "FAIL"}))
    return 0 if ok else 1


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "selftest":
        sys.exit(selftest(sys.argv[2] if len(sys.argv) > 2 else None))
    print(__doc__)
