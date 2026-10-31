#!/usr/bin/env python3
"""E83 (Q130): the session runner. It IS E80's runner, ../run_kspeed.py (E64's tools/claims-v3/hpl/run_hpl.py plus
`file:` tiles checked against kinds.json), imported and run unchanged, with one addition and nothing else:

  under --dry the toy card draws each E83 kind's PREDICTED switching term (this folder's predictions.json,
  `c_pred_w`), so a dry session exercises the gates, the safety paths and reduce_e83.py with plausible numbers.
  (run_kspeed.py's own dry table covers only E80's 18 kinds.) No device is touched under --dry.

Before the session it writes <RUNDIR>/e83.json: this wrapper's sha256 and predictions.json's, beside run_kspeed.py's
own kspeed.json (every tile's sha256, checked against kinds.json) and run_hpl.py's session.json. Everything that
touches the card -- the card lock held for the session, the other-user checks before every launch process,
`timeout 10` on every device process, the sampler WITHOUT --reset-ms, the trace ring, residencies and `ettelem
config` after every run, the safety stops (85 C; 97 W on three samples), and the end of the session unless the TDP
and the threshold read back 65 -- is run_hpl.py's own code. Nothing is set on the card.

    python3 run_e83.py --protocol protocol.json --out <RUNDIR> [--dry] [--only BLOCK ...] [--max-card-min N] [--list]
"""
import hashlib
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, ".."))
import run_kspeed as K  # noqa: E402


def sha256(path):
    return hashlib.sha256(open(path, "rb").read()).hexdigest()


def main():
    pred_path = os.path.join(HERE, "predictions.json")
    pred = json.load(open(pred_path))
    if "--dry" in sys.argv:
        for e in pred["kinds"].values():
            K.H.DryCard.DYN600["file:" + e["tile"]] = e["c_pred_w"]
    if "--out" in sys.argv and "--list" not in sys.argv:
        rd = os.path.abspath(sys.argv[sys.argv.index("--out") + 1])
        if not os.path.exists(os.path.join(rd, "session.json")):
            os.makedirs(rd, exist_ok=True)
            json.dump({"experiment": "E83", "wrapper": os.path.relpath(os.path.abspath(__file__),
                                                                     os.path.join(HERE, "..", "..", "..", "..")),
                       "wrapper_sha256": sha256(__file__), "predictions_sha256": sha256(pred_path),
                       "run_kspeed_sha256": sha256(K.__file__), "argv": sys.argv},
                      open(os.path.join(rd, "e83.json"), "w"), indent=1)
    return K.main()


if __name__ == "__main__":
    sys.exit(main())
