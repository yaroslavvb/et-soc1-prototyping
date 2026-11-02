#!/usr/bin/env python3
"""E119 (Q134): the session runner. It IS E105's run_e105.py (E101 session 2's run_e101s.py, E80's run_kspeed.py, E64's run_hpl.py), imported and run
unchanged, admission rule included, with three additions and nothing else:

  1. IDLE LOGINS (the owner's ruling of 1 November 2026, about 15:00 PST): run_hpl.py's other-user check asks `who`; that one call is answered by E111's
     idle_logins_e111.py, unchanged: a user whose every session has been idle for at least 120 minutes and none of whose live processes started under 120
     minutes ago does not block. Everything else still blocks before every launch process: a non-idle terminal, a new process of a logged-in user, any
     other user's device process, the module's use count over the session's baseline, the card lock held by anyone.
  2. NO READ OF RAW THROTTLE STATE 4 (E77's correction F1): run_hpl.py reads `ettelem residency 2 3 4 5 6` after every run; on this card's BL2 0.22.0
     raw 4 is the enum's UNKNOWN sentinel and 5 and 6 are past it, and each read of them logs two ERROR lines and SP_RUNTIME_ERROR events. Here that one
     command reads `residency 1 2 3` (POWER_UP, POWER_DOWN, POWER_SAFE). A RAM read either way; no reducer uses it.
  3. THE CAP CUTS THE TAIL CLEANLY: a run starts only if the time already used plus its planned time (run_hpl.py's own plan_s) fits the session's cap;
     otherwise the session ends there, exit 0, its end queries read. run_hpl.py's own cap check would cut a run in flight instead.

Everything that touches the card -- the card lock held for the session, `timeout 10` on every launch and config read, the sampler WITHOUT --reset-ms,
the trace ring and `ettelem config` after every run, the safety stops (85 C; 97 W on three samples), the end of the session unless the TDP and the
threshold read back 65, and the admission rule (88 W at the estimate; the 93 W lock) -- is the imported code. Nothing is set on the card.

    python3 run_e119.py --protocol protocol.json --out <RUNDIR> [--dry] [--only BLOCK ...] [--max-card-min N] [--list]
"""
import hashlib
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "kspeed", "e105"))
import run_e105 as RE  # noqa: E402
sys.path.insert(0, os.path.join(HERE, "..", "e111"))
import idle_logins_e111 as IL  # noqa: E402

H = RE.H
RESIDENCY_STATES = ["1", "2", "3"]


def sha256(path):
    return hashlib.sha256(open(path, "rb").read()).hexdigest()


def patch_residency(module):
    """Addition 2: the one `ettelem residency ...` command reads states 1, 2, 3; every other command goes through untouched."""
    orig = module.run_out
    if getattr(orig, "_e119", False):
        return

    def run_out(cmd, *a, **kw):
        c = list(cmd)
        if "residency" in c:
            i = c.index("residency")
            c = c[:i + 1] + RESIDENCY_STATES
        return orig(c, *a, **kw)

    run_out._e119 = True
    module.run_out = run_out


def fits(elapsed_s, plan_s, cap_s):
    """Addition 3, as a plain function (selftest_e119.py runs it): may a run of plan_s start after elapsed_s of a cap_s session?"""
    return elapsed_s + plan_s <= cap_s


_prev_run_one = H.Session.run_one       # run_e105.py's: the admission rule around run_hpl.py's run_one


def _run_one(self, r, k, n):
    if self.t0 is not None and not fits(time.time() - self.t0, r.plan_s(), self.max_card_s):
        rec = {"run": r.name, "t_ms": int(time.time() * 1000), "elapsed_s": round(time.time() - self.t0, 1), "plan_s": round(r.plan_s(), 1),
               "cap_s": round(self.max_card_s, 1)}
        self.mark("e119_cap_tail", json.dumps(rec))
        self.say(f"[{k}/{n}] {r.name}: the cap cuts the tail here ({json.dumps(rec)})")
        raise H.EndSession("done:cap_cuts_tail", H.EXIT_OK)
    return _prev_run_one(self, r, k, n)


H.Session.run_one = _run_one


def main():
    pr = sys.argv[sys.argv.index("--protocol") + 1]
    proto = json.load(open(pr))
    dry = "--dry" in sys.argv
    if not dry:
        IL.patch(H, as_bytes=True)          # addition 1
    patch_residency(H)                      # addition 2 (under --dry the toy card answers the queries; nothing is read)
    if "--out" in sys.argv and "--list" not in sys.argv:
        rd = os.path.abspath(sys.argv[sys.argv.index("--out") + 1])
        RE.ADM["adm"] = RE.Admission(proto, rd)
        os.makedirs(rd, exist_ok=True)
        if not os.path.exists(os.path.join(rd, "e119.json")):
            json.dump({"experiment": "E119", "request": "Q134", "wrapper": "tools/claims-v3/e119/run_e119.py", "wrapper_sha256": sha256(__file__),
                       "protocol": os.path.basename(pr), "protocol_sha256": sha256(pr),
                       "predictions_sha256": sha256(os.path.join(HERE, "predictions-e119.json")),
                       "run_e105_sha256": sha256(RE.__file__), "run_e101s_sha256": sha256(RE.RS.__file__), "run_kspeed_sha256": sha256(RE.RS.K.__file__),
                       "run_hpl_sha256": sha256(H.__file__), "idle_logins_sha256": sha256(IL.__file__), "residency_states": RESIDENCY_STATES,
                       "t_ms": int(time.time() * 1000), "zone": time.strftime("%Z"), "argv": sys.argv}, open(os.path.join(rd, "e119.json"), "w"), indent=1)
    return RE.RS.main()


if __name__ == "__main__":
    sys.exit(main())
