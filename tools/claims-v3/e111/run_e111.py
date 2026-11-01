#!/usr/bin/env python3
"""E111 (Q133): one session of a warm probe (W1, W2), the idle read after (END) or the smoke. It IS E98's runner: E80's
../kspeed/run_kspeed.py (E64's tools/claims-v3/hpl/run_hpl.py plus `file:` tiles checked against kinds.json), imported and
run unchanged, exactly as ../kspeed/e98/run_e98.py runs it. Nothing is added to what touches the card.

Before the session it writes <RUNDIR>/e111.json: this wrapper's sha256, the protocol's, the predictions', run_kspeed.py's,
and the zone the box's clock is in (every time in E111 is epoch ms; the zone is for the reader).

Amendment A1 (before the claim and the first launch): run_hpl.py's other-user check asks `who`; that one call is answered by
idle_logins_e111.py, which leaves out a user whose every session has been idle for at least 120 minutes. Nothing else changes.

Everything that touches the card -- the card lock held for the session, the other-user checks before every launch process,
`timeout 10` on every launch and config read, the sampler WITHOUT --reset-ms, the trace ring, residencies and `ettelem
config` after every run, the safety stops (85 C; 97 W on three samples), and the end of the session unless the TDP and the
threshold read back 65 -- is run_hpl.py's own code. Nothing is set on the card.

    python3 run_e111.py --protocol protocol-w1.json --out <RUNDIR> [--dry] [--max-card-min N] [--list]
"""
import hashlib
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "kspeed"))
import run_kspeed as K  # noqa: E402
sys.path.insert(0, HERE)
import idle_logins_e111 as IL  # noqa: E402

H = K.H
# The toy card's switching watts for these tiles, under --dry only (E98's DRY_C, with fp32 randn for the fp32 hold).
DRY_C = {"fp32/zeros": 1.6, "fp16/zeros": 1.4, "int8/zeros": 2.1, "int8/neg_ones": 2.7, "int8/sparse50": 8.1, "fp16/ones": 9.7,
         "int8/full": 9.1, "fp32/randn": 25.2}


def sha256(path):
    return hashlib.sha256(open(path, "rb").read()).hexdigest()


def main():
    if "--dry" not in sys.argv:
        IL.patch(H, as_bytes=True)      # amendment A1: a login idle >= 120 min does not block; everything else as run_hpl.py
    if "--dry" in sys.argv:
        for k, c in DRY_C.items():
            t, v = k.split("/")
            H.DryCard.DYN600[f"file:tools/claims-v3/kinds/tiles/{t}/{v}.bin"] = c
    if "--out" in sys.argv and "--list" not in sys.argv:
        rd = os.path.abspath(sys.argv[sys.argv.index("--out") + 1])
        if not os.path.exists(os.path.join(rd, "session.json")):
            os.makedirs(rd, exist_ok=True)
            pr = sys.argv[sys.argv.index("--protocol") + 1]
            json.dump({"experiment": "E111", "wrapper": "tools/claims-v3/e111/run_e111.py", "wrapper_sha256": sha256(__file__),
                       "protocol": os.path.basename(pr), "protocol_sha256": sha256(pr),
                       "predictions_sha256": sha256(os.path.join(HERE, "predictions-e111.json")),
                       "run_kspeed_sha256": sha256(K.__file__), "run_hpl_sha256": sha256(H.__file__),
                       "idle_logins_sha256": sha256(IL.__file__), "amendment": "A1",
                       "t_ms": int(time.time() * 1000), "zone": time.strftime("%Z"), "argv": sys.argv},
                      open(os.path.join(rd, "e111.json"), "w"), indent=1)
    return K.main()


if __name__ == "__main__":
    sys.exit(main())
