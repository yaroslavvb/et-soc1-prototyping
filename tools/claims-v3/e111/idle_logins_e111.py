#!/usr/bin/env python3
"""E111 amendment A1 (Sun 1 Nov 2026, before the claim and the first launch): on aifoundry2, a user who is only logged in, and
whose every session has been idle for at least 120 minutes, does not block. E60's departure D1 for aifoundry3 and aifoundry1 (a
user who is only logged in does not block), with an idle guard that aifoundry3's form does not have.

What still blocks, unchanged, in every check before every launch process: any other user with a session idle under 120 minutes
(so any new login, and anyone who comes back to a terminal), any other user's device process (run_hpl's and run_hlc's OTHER_COMM),
a stale device process of ours, the et_soc1 module's use count over the session's baseline, and the card lock held by anyone.

How: the runners ask `who` and end the session if it lists another user. This module wraps the runner module's own `run_out` so
that a call of exactly ["who"] answers with `who`'s lines for the blocking users only, decided from `who -u`'s idle column; every
other command goes through untouched. Each decision is appended to $E111_IDLE_LOG (if set) as counts only, never a login.

    python3 idle_logins_e111.py        # print the decision for the box as it stands (counts only)
"""
import json
import os
import re
import subprocess
import time

MIN_IDLE_MIN = 120
_HHMM = re.compile(r"^\d{1,2}:\d\d$")


def _me():
    try:
        import pwd
        return pwd.getpwuid(os.getuid()).pw_name
    except Exception:  # noqa: BLE001
        return os.environ.get("USER") or os.environ.get("LOGNAME") or ""


def sessions():
    """[(user, idle minutes or None if unreadable, the raw `who` line)] for every session `who -u` lists."""
    try:
        r = subprocess.run(["who", "-u"], capture_output=True, timeout=10, stdin=subprocess.DEVNULL)
        lines = r.stdout.decode(errors="replace").splitlines()
    except (OSError, subprocess.SubprocessError):
        return None
    out = []
    for ln in lines:
        f = ln.split()
        if not f:
            continue
        idle = None
        # NAME LINE <login time: 2 or 3 tokens ending in HH:MM> IDLE PID [COMMENT]
        for i in range(2, len(f) - 1):
            if _HHMM.match(f[i]):
                tok = f[i + 1]
                if tok == ".":
                    idle = 0
                elif tok == "old":
                    idle = 24 * 60
                elif _HHMM.match(tok):
                    h, m = tok.split(":")
                    idle = int(h) * 60 + int(m)
                break
        out.append((f[0], idle, ln))
    return out


def decide():
    """(blocking users, record): a user blocks unless every one of their sessions reads idle >= MIN_IDLE_MIN. Fails closed: an
    unreadable `who -u`, or a session whose idle cannot be read, blocks."""
    me = _me()
    ss = sessions()
    if ss is None:
        return ["<who -u unreadable>"], {"unreadable": True}
    users = {}
    for u, idle, _ in ss:
        if u == me:
            continue
        users.setdefault(u, []).append(idle)
    blocking = sorted(u for u, idles in users.items() if any(i is None or i < MIN_IDLE_MIN for i in idles))
    ignored = [u for u in users if u not in blocking]
    rec = {"t_ms": int(time.time() * 1000), "other_users": len(users), "other_sessions": sum(len(v) for v in users.values()),
           "blocking_users": len(blocking), "ignored_idle_users": len(ignored),
           "ignored_min_idle_min": min((min(users[u]) for u in ignored), default=None), "rule_min_idle_min": MIN_IDLE_MIN}
    p = os.environ.get("E111_IDLE_LOG")
    if p:
        try:
            with open(p, "a") as fh:
                fh.write(json.dumps(rec) + "\n")
        except OSError:
            pass
    return blocking, rec


def who_text():
    """`who`-shaped text holding one line per blocking user (the runners read only the first field)."""
    blocking, _ = decide()
    return "".join(f"{u} pts/? (blocking)\n" for u in blocking)


def patch(module, as_bytes):
    """Wrap module.run_out so that ["who"] answers through decide(); everything else is the original call."""
    orig = module.run_out
    if getattr(orig, "_e111", False):
        return

    def run_out(cmd, *a, **kw):
        if list(cmd) == ["who"]:
            t = who_text()
            return 0, (t.encode() if as_bytes else t), (b"" if as_bytes else "")
        return orig(cmd, *a, **kw)

    run_out._e111 = True
    module.run_out = run_out


def others_count():
    """For the queue: how many other users block (a count)."""
    return len(decide()[0])


if __name__ == "__main__":
    b, rec = decide()
    print(json.dumps(rec))
    print("blocking users:", len(b))
