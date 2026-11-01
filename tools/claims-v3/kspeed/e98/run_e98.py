#!/usr/bin/env python3
"""E98 (Q132): one probe's session runner. It IS E80's runner, ../run_kspeed.py (E64's tools/claims-v3/hpl/run_hpl.py
plus `file:` tiles checked against kinds.json), imported and run unchanged. The REST block is a run with zero launch
processes, which run_hpl.py's run_one handles as it stands: sampler on, the gate's first reading, no launch, tail_s of
idle samples, sampler off, the management queries. Nothing is added to what touches the card.

Before the session it writes <RUNDIR>/e98.json: this wrapper's sha256, the protocol's, the predictions', and the zone
the box's clock is in (02:00 PDT goes back tonight; every time in E98 is epoch ms, the zone is for the reader).

Everything that touches the card -- the card lock held for the session, the other-user checks before every launch
process, `timeout 10` on every launch and config read, the sampler WITHOUT --reset-ms, the trace ring, residencies and
`ettelem config` after every run, the safety stops (85 C; 97 W on three samples), and the end of the session unless the
TDP and the threshold read back 65 -- is run_hpl.py's own code. Nothing is set on the card.

    python3 run_e98.py --protocol protocol.json --out <RUNDIR> [--dry] [--only BLOCK ...] [--max-card-min N] [--list]
"""
import hashlib
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, ".."))
import run_kspeed as K  # noqa: E402

H = K.H
# The toy card's switching watts for the tiles of this design, under --dry only (E80's predicted c; fp32 zeros has none there).
DRY_C = {"fp32/zeros": 1.6, "fp16/zeros": 1.4, "int8/zeros": 2.1, "int8/neg_ones": 2.7, "int8/sparse50": 8.1, "fp16/ones": 9.7,
         "int8/full": 9.1, "fp32/randn": 25.2}


def sha256(path):
    return hashlib.sha256(open(path, "rb").read()).hexdigest()


def main():
    if "--dry" in sys.argv:
        for k, c in DRY_C.items():
            t, v = k.split("/")
            H.DryCard.DYN600[f"file:tools/claims-v3/kinds/tiles/{t}/{v}.bin"] = c
    if "--out" in sys.argv and "--list" not in sys.argv:
        rd = os.path.abspath(sys.argv[sys.argv.index("--out") + 1])
        if not os.path.exists(os.path.join(rd, "session.json")):
            os.makedirs(rd, exist_ok=True)
            pr = sys.argv[sys.argv.index("--protocol") + 1]
            json.dump({"experiment": "E98", "wrapper": "tools/claims-v3/kspeed/e98/run_e98.py", "wrapper_sha256": sha256(__file__),
                       "protocol_sha256": sha256(pr), "predictions_sha256": sha256(os.path.join(HERE, "predictions.json")),
                       "run_kspeed_sha256": sha256(K.__file__), "t_ms": int(time.time() * 1000), "zone": time.strftime("%Z"),
                       "argv": sys.argv}, open(os.path.join(rd, "e98.json"), "w"), indent=1)
    return K.main()


if __name__ == "__main__":
    sys.exit(main())
