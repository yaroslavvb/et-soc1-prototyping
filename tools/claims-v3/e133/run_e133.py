#!/usr/bin/env python3
"""E133 (Q136): one session of the queue (SMOKE, W2, END, W1B, END2, W3). It IS E111's runner, run_e111.py's chain: E80's
../kspeed/run_kspeed.py (E64's ../hpl/run_hpl.py plus `file:` tiles checked against kinds.json), imported and run unchanged,
with E111's idle-login rule (../e111/idle_logins_e111.py: the owner's ruling of 1 November 2026), and ONE change, which removes
a command and adds none:

  NO RESIDENCY READ. run_hpl.py reads `ettelem residency 2 3 4 5 6` after every run (hpl/run_hpl.py:622). On this card's BL2
  0.22.0 raw states 4-6 are no state: each read logs two ERROR lines and SP_RUNTIME_ERROR events (Q136(w), result 5), and the
  owner's rules of 2 November 2026 allow no such read. Here that one command is NOT SENT: the wrapped run_out returns at once
  with rc null and no output, starts no process and opens no device, and appends one line to <RUNDIR>/e133-not-sent.jsonl.
  No reducer reads residencies (E111's, E98's and E133's do not).

Everything that touches the card -- the card lock held for the session, the other-user checks before every launch process,
`timeout 10` on every launch and config read, the sampler WITHOUT --reset-ms, the trace ring and `ettelem config` after every
run, the safety stops (E133's protocols: 80 C on the die mean or the hottest sensor, 93 W on three samples), and the end of the
session unless the TDP and the threshold read back 65 -- is run_hpl.py's own code. Nothing is set on the card.

Before the session it writes <RUNDIR>/e133.json: this wrapper's sha256, the protocol's, the predictions', run_kspeed.py's,
run_hpl.py's and idle_logins_e111.py's, and the zone the box's clock is in (every time in E133 is epoch ms).

    python3 run_e133.py --protocol protocol-w2.json --out <RUNDIR> [--dry] [--max-card-min N] [--list]
"""
import hashlib
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))

# Amendment A1 (Mon 2 Nov 2026, before any E133 data): the chain must be the audited one. Before the runner is imported and before
# any device access, the three files it runs are hashed; any other copy refuses with exit 2 (the queue halts). No command is sent.
AUDITED = {os.path.join("hpl", "run_hpl.py"): "68493295504fba5d4e9056b4f7e7387179d555e4157bbae32075b4197f3df227",
           os.path.join("kspeed", "run_kspeed.py"): "d3d844c7912d873fb1fe80c92dd72124d2714e493bcf4f73a961cfa26d894c0c",
           os.path.join("e111", "idle_logins_e111.py"): "91094be5f9af14c0897a817b7d95777fdaaa6ab12b49304883ccb3d066574ef4"}


def chain_differs():
    bad = []
    for rel, want in AUDITED.items():
        p = os.path.realpath(os.path.join(HERE, "..", rel))
        try:
            got = hashlib.sha256(open(p, "rb").read()).hexdigest()
        except OSError as e:
            got = f"unreadable: {e}"
        if got != want:
            bad.append(f"{rel}: {got[:16]} (audited {want[:16]})")
    return bad


_bad = chain_differs()
if _bad:
    print("E133 REFUSED (amendment A1): the chain is not the audited one: " + "; ".join(_bad), flush=True)
    sys.exit(2)

sys.path.insert(0, os.path.join(HERE, "..", "kspeed"))
import run_kspeed as K  # noqa: E402
sys.path.insert(0, os.path.join(HERE, "..", "e111"))
import idle_logins_e111 as IL  # noqa: E402

H = K.H
for _m, _rel in ((H, os.path.join("hpl", "run_hpl.py")), (K, os.path.join("kspeed", "run_kspeed.py")),
                 (IL, os.path.join("e111", "idle_logins_e111.py"))):
    if os.path.realpath(_m.__file__) != os.path.realpath(os.path.join(HERE, "..", _rel)):   # A1: the imported module is the hashed file
        print(f"E133 REFUSED (amendment A1): {_rel} was imported from {_m.__file__}", flush=True)
        sys.exit(2)
# The toy card's switching watts for these tiles, under --dry only (run_e111.py's DRY_C, unchanged).
DRY_C = {"fp32/zeros": 1.6, "fp16/zeros": 1.4, "int8/zeros": 2.1, "int8/neg_ones": 2.7, "int8/sparse50": 8.1, "fp16/ones": 9.7,
         "int8/full": 9.1, "fp32/randn": 25.2}
NOT_SENT_WORDS = ("residency",)
_rundir = [None]


def sha256(path):
    return hashlib.sha256(open(path, "rb").read()).hexdigest()


def is_not_sent(cmd):
    """True for the one command E133 never sends: any `ettelem residency ...` (a word of the argv, not a substring)."""
    return any(str(w) in NOT_SENT_WORDS for w in cmd)


def patch_no_residency(module):
    """Wrap module.run_out so that a residency command is answered at once, unsent; every other command is the original call."""
    orig = module.run_out
    if getattr(orig, "_e133", False):
        return

    def run_out(cmd, *a, **kw):
        if is_not_sent(cmd):
            if _rundir[0]:
                try:
                    with open(os.path.join(_rundir[0], "e133-not-sent.jsonl"), "a") as f:
                        f.write(json.dumps({"t_ms": int(time.time() * 1000), "argv": [os.path.basename(str(cmd[2])) if len(cmd) > 2 else ""]
                                            + [str(w) for w in cmd[3:]], "why": "E133: no residency read (raw 4-6 log SP errors)"}) + "\n")
                except OSError:
                    pass
            return None, b"", b"E133: not sent"
        return orig(cmd, *a, **kw)

    run_out._e133 = True
    module.run_out = run_out


def main():
    if "--dry" not in sys.argv:
        IL.patch(H, as_bytes=True)      # E111's A1/A3: a login idle >= 120 min (no process newer than 120 min) does not block
    patch_no_residency(H)               # E133: the residency read is never sent (applies to real runs; dry runs send nothing anyway)
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
            json.dump({"experiment": "E133", "request": "Q136", "wrapper": "tools/claims-v3/e133/run_e133.py", "wrapper_sha256": sha256(__file__),
                       "protocol": os.path.basename(pr), "protocol_sha256": sha256(pr),
                       "predictions_sha256": sha256(os.path.join(HERE, "predictions-e133.json")),
                       "run_kspeed_sha256": sha256(K.__file__), "run_hpl_sha256": sha256(H.__file__),
                       "idle_logins_sha256": sha256(IL.__file__), "not_sent": list(NOT_SENT_WORDS),
                       "t_ms": int(time.time() * 1000), "zone": time.strftime("%Z"), "argv": sys.argv},
                      open(os.path.join(rd, "e133.json"), "w"), indent=1)
    return K.main()


if __name__ == "__main__":
    sys.exit(main())
